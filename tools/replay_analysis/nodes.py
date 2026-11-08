"""Node models along the causal map (data/model/causal_map.json): each explains one result from what happened before it,
so the engine can say WHY, not only who is winning. Glass box (Explainable Boosting Machine), readable, tested on
matches it never saw. Time order is enforced: every feature is measured at or before the moment, the label after it.

Nodes so far:
- deaths: one row per alive player every SAMPLE s; label = the player dies within HORIZON s. Features: the player's
  state (health, health ceiling, damage taken, attackers, knockdowns, Daze, Deep Wound, cripple, interrupts, prots and
  blocks up, conditions it took on itself), its support (healers in range, healers dead, allies and enemies near, local
  numbers, distance from its group and pit), the situation (res timer, flag lead, minute, strength gap) and the
  matchup (enemy threats against own answers). Rows with no damage taken in 10 s are kept at 1 in NEG_KEEP and weighted.
- lord_kill: while enemies are in a team's pit (every SAMPLE s), label = its Lord dies within LORD_HORIZON s; the pit
  features plus the Lord's rebuilt health, whether it is exposed and its net damage taken in the last 60 s (lord.py).
  28 of the first 30 matches ended with a Lord kill: this node is how the end of a match is explained.
- kill_conversion: one row per burst (3+ attackers, 250+ damage in 2 s on one target); label = the target dies within
  8 s. Features: the target's defence (prots and blocks up, healers in range, health, ceiling, knocked down, Dazed),
  the attackers' shutdown (Blind, interrupts and knockdowns on them in the last 5 s), the burst itself, the matchup.

Usage:  python3 nodes.py fit [deaths|kill_conversion]   fit on the trained batches, write data/model/nodes/<node>.json and
                                                        .md, print validation and what it leans on
        python3 nodes.py explain <report id> <m:ss> <team role>   why that player's death risk was what it was
In code: node_rows(node, rid), fit_node(node, ids) -> (summary, model)."""
import bisect, collections, json, math, os, random, statistics, sys, warnings
import numpy as np
warnings.filterwarnings("ignore")
from common import REPO, CAST_R, PROT_SKILLS, BLOCKS, RES_EVERY, IN_AREA
import model as M
from buildfeat import matchup

NODE_DIR = os.path.join(REPO, "data", "model", "nodes")
SAMPLE, HORIZON, NEG_KEEP = 3, 10, 4
LORD_HORIZON = 30        # lord_kill: the Lord dies within this many seconds
MATCHUP_KEYS = ["enemy_knockdowns_v_own_aura_of_stability", "enemy_interrupts", "enemy_energy_denial", "enemy_snares",
                "enemy_blind", "enemy_strips", "own_condition_removal", "own_prots"]


class Timeline:
    """Per-player event lists by second, built once per match, so features are quick to read at any second."""
    def __init__(self, st, sb):
        m = st.m
        self.st, self.sb, self.m = st, sb, m
        self.dmg_in = collections.defaultdict(list)       # victim -> [(t, dmg, attacker)]
        self.dmg_out = collections.defaultdict(list)
        for r in m.o["ev"]:
            if r[1] == "dm" and (r[5] or 0) > 0 and r[3] in m.PL and r[2] in m.PL and m.team(r[2]) != m.team(r[3]):
                self.dmg_in[r[3]].append((r[0] / 10, r[5], r[2])); self.dmg_out[r[2]].append((r[0] / 10, r[5], r[3]))
        self.kd = collections.defaultdict(list); self.ir = collections.defaultdict(list)
        for k in m.o.get("knockdowns", []): self.kd[k[2]].append(k[0] / 10)
        for i in m.o.get("interrupts", []): self.ir[i[3]].append(i[0] / 10)
        self.cond = collections.defaultdict(list)          # target -> [(start, end, name, source team)]
        self.ench = collections.defaultdict(list)          # target -> [(start, end, skill name)]
        self.hex = collections.defaultdict(list)           # target -> [(start, end, skill name)]
        for e in m.o.get("effects", []):
            if e[0] is None: continue
            s0, s1 = e[0] / 10, (e[1] or 10 ** 9) / 10
            if e[2] == "c" and e[7]: self.cond[e[5]].append((s0, s1, e[7], m.team(e[4]) if isinstance(e[4], int) else None))
            elif e[2] == "e": self.ench[e[5]].append((s0, s1, m.sk(e[3])))
            elif e[2] == "h": self.hex[e[5]].append((s0, s1, m.sk(e[3])))
        self.healers = {tm: [a for a in st.players[tm] if _healer(m, a)] for tm in st.teams}
        self.deaths = {a: sorted(st.death_times.get(a, [])) for a in m.PL}

    def window(self, L, t, w): return [x for x in L if t - w < x[0] <= t]

    def group_of(self, a, t):
        """The player's group (players within fight range of each other) at second t, cached per team and second."""
        tm = self.m.team(a); k = (tm, int(t))
        if not hasattr(self, "_groups"): self._groups = {}
        if k not in self._groups: self._groups[k] = self.m.groups(tm, int(t) * 10)
        return next((g for g in self._groups[k] if a in g), [a])

    def has_cond(self, a, t, names, own_source=None):
        tm = self.m.team(a)
        return any(s0 <= t <= s1 and n in names and (own_source is None or (src == tm) == own_source) for s0, s1, n, src in self.cond.get(a, []))

    def hexes_on(self, a, t):
        return sum(1 for s0, s1, _ in self.hex.get(a, []) if s0 <= t <= s1)

    def ench_up(self, a, t, names):
        return any(s0 <= t <= s1 and n in names for s0, s1, n in self.ench.get(a, []))

    def dies_within(self, a, t, h):
        L = self.deaths[a]; i = bisect.bisect_right(L, t)
        return i < len(L) and L[i] <= t + h


def _physical(m, a):
    """A physical attacker (Blind stops its attacks): frontline, Ranger or Paragon (as eventlayer.py's Blind records)."""
    from common import line
    try: fl = line(m, a) == "frontline"
    except Exception: fl = m.A[a].get("p") in ("Warrior", "Assassin", "Dervish")
    return fl or m.A[a].get("p") in ("Ranger", "Paragon")


def _blind_secs_on(tl, a, t0, t1):
    iv = sorted((max(s0, t0), min(s1, t1)) for s0, s1, n, _ in tl.cond.get(a, []) if n == "blind" and s1 > t0 and s0 < t1)
    tot, cs, ce = 0.0, None, None
    for s, e in iv:
        if cs is None: cs, ce = s, e
        elif s > ce: tot += ce - cs; cs, ce = s, e
        else: ce = max(ce, e)
    return tot + (ce - cs if cs is not None else 0)


def _healer(m, a):
    from phases import healer
    return healer(m, a)


def death_features(tl, a, t, mu, gap):
    st, sb, m = tl.st, tl.sb, tl.m
    from state import d
    tm = m.team(a); p, s = st.pos(a, t)
    base = m.A[a].get("hp") or 500
    din3 = tl.window(tl.dmg_in[a], t, 3); din10 = tl.window(tl.dmg_in[a], t, 10)
    heal_live = [b for b in tl.healers[tm] if b != a and st.alive(b, t)]
    in_range = [b for b in heal_live if d(st.pos(b, t)[0], p) <= CAST_R]
    near = lambda team, r: sum(1 for b in st.players[team] if b != a and st.alive(b, t) and d(st.pos(b, t)[0], p) <= r)
    main = st.main_group(tm, t); c = st.centroid(main, t)
    sbt = sb.at(t)[m.tag[tm]]
    return {
        "is_healer": int(a in tl.healers[tm]), "line": {"frontline": 0, "midline": 1, "backline": 2}[__import__("common").line(m, a)],
        "health_pct": s["hp"], "health_ceiling": round(sb.eff_hp(a, t) / base, 2),
        "damage_taken_3s": sum(x[1] for x in din3), "damage_taken_10s": sum(x[1] for x in din10),
        "attackers_5s": len({x[2] for x in tl.window(tl.dmg_in[a], t, 5)}),
        "knocked_down_now": int(s["st"] == "k"), "knockdowns_10s": sum(1 for x in tl.kd[a] if t - 10 < x <= t),
        "interrupted_10s": sum(1 for x in tl.ir[a] if t - 10 < x <= t),
        "dazed": int(tl.has_cond(a, t, {"dazed"})), "crippled": int(tl.has_cond(a, t, {"crippled"})),
        "deep_wound": int(tl.has_cond(a, t, {"deep_wound"})),
        "conditions_self_taken": int(tl.has_cond(a, t, {"deep_wound", "burning", "bleeding", "poison", "crippled", "blind", "weakness", "dazed"}, own_source=True)),
        "prot_up": int(tl.ench_up(a, t, PROT_SKILLS)), "block_up": int(tl.ench_up(a, t, BLOCKS)),
        "hexes_on": tl.hexes_on(a, t), "hexes_on_own_healers": sum(tl.hexes_on(b, t) for b in heal_live),
        "healers_in_range": len(in_range),
        # OG comms (comms_vars.py): a monk alone has no other monk to support it; every group needs a healer; fight the
        # player with a big death penalty; spread out against area damage
        "solo_healer": int(a in tl.healers[tm] and not in_range),
        "group_no_healer": int(len(g := tl.group_of(a, t)) >= 2 and not any(b in tl.healers[tm] for b in g)),
        "own_morale": (sbt.get("morale") or {}).get(m.roles.get(a), 0) or 0 if sbt else 0,
        "allies_in_area": near(tm, IN_AREA),
        "healers_dead": sum(1 for b in tl.healers[tm] if b != a and not st.alive(b, t)),
        "allies_near": near(tm, 1500), "enemies_near": near(3 - tm, 1500), "local_diff": near(tm, 2000) - near(3 - tm, 2000),
        "dist_from_group": round(d(p, c)) if a not in main and c else 0,
        "away_3000": int(a not in main and bool(c) and d(p, c) >= 3000),
        "dist_own_pit": round(d(p, st.geo.pit.get(tm))), "res_in": sbt and sb.at(t)["res_in"],
        "flag_lead": max(min(sbt["flag_lead"], 150), -150), "minute": round(t / 60, 1), "strength_gap": gap,
        **{k: mu[k] for k in MATCHUP_KEYS},
    }


DEATH_DESC = {
    "is_healer": "the player is a healer (1) or not (0)", "line": "0 frontline, 1 midline, 2 backline",
    "health_pct": "current health %", "health_ceiling": "maximum health after death penalty, as a share of normal",
    "damage_taken_3s": "damage taken in the last 3 s", "damage_taken_10s": "damage taken in the last 10 s",
    "attackers_5s": "different enemies who hit the player in the last 5 s", "knocked_down_now": "knocked down now",
    "knockdowns_10s": "knockdowns in the last 10 s", "interrupted_10s": "times interrupted in the last 10 s",
    "dazed": "Dazed now", "crippled": "Crippled now", "deep_wound": "Deep Wound now",
    "conditions_self_taken": "carrying a condition it took on itself from a teammate (Draw Conditions)",
    "prot_up": "a prot (Guardian, Spirit Bond, Life Sheath, Protective Spirit...) on the player now",
    "block_up": "a block enchantment up now", "hexes_on": "hexes on the player now",
    "hexes_on_own_healers": "hexes on its team's live healers now (hex pressure on the backline)",
    "healers_in_range": "own healers alive within cast range (other than the player)",
    "solo_healer": "the player is a healer with no other own healer within cast range (OG comms: a solo monk is vulnerable)",
    "group_no_healer": "the player's group (2+) has no healer (OG comms: keep a healer with every group)",
    "own_morale": "the player's own morale: negative = death penalty, positive = boost (OG comms: fight the player with 30 DP)",
    "allies_in_area": "allies within 322 (the area of most area spells; OG comms: spread out)",
    "healers_dead": "own healers dead", "allies_near": "allies within 1,500", "enemies_near": "enemies within 1,500",
    "local_diff": "allies minus enemies within 2,000", "dist_from_group": "distance from its main group (0 if in it)",
    "away_3000": "3,000+ from its main group (Denning: clearer than 2,500 for a split or a collapse)",
    "dist_own_pit": "distance from its own pit", "res_in": "seconds until the next res", "flag_lead": "own flag lead (s)",
    "minute": "match minute", "strength_gap": "own minus enemy team strength",
    "enemy_knockdowns_v_own_aura_of_stability": "enemy knockdown skills minus own Auras of Stability (matchup)",
    "enemy_interrupts": "enemy interrupt skills", "enemy_energy_denial": "enemy energy-denial skills",
    "enemy_snares": "enemy snare skills", "enemy_blind": "enemy Blind skills", "enemy_strips": "enemy enchantment removal skills",
    "own_condition_removal": "own condition removal skills", "own_prots": "own prot skills",
}


_AOE = {}
def _aoe_skills(m, a):
    """Area-damage skills on a player's bar (Denning P9: knights ball up and eat area damage). Cached by the bar's skill
    names (until 2026-11-07 it was cached by the player's slot alone, so one match's count leaked into the next match a
    process handled, and the rows depended on which matches a worker happened to build first)."""
    bar = tuple(m.sk(b) for b in m.A[a].get("bar", []) if b)
    if bar not in _AOE:
        from buildfeat import _skills, FEATURES
        S = _skills()
        _AOE[bar] = sum(1 for k in bar if S.get(k) and FEATURES["area_damage"](S[k]))
    return _AOE[bar]


def _drops(st, tl, fl, tm, t0, t1):
    """The team's flag drops between t0 and t1, by kind (Denning): a quick hand-off (a teammate picks it up within 5 s),
    forced (the carrier was hit in the 5 s before, or died), or parked (it lay 5 s or more: a team deciding not to run
    yet, most often in its own base); seconds parked, and seconds parked in its own base."""
    from state import d
    m = st.m
    out = {"quick_handoffs": 0, "forced_drops": 0, "parked_s": 0, "parked_in_base_s": 0}
    for i, (t, ty, a) in enumerate(fl):
        if ty != "flag_dropped" or m.team(a) != tm or not (t0 <= t <= t1): continue
        nxt = next(((tt, b) for tt, tyy, b in fl[i + 1:] if tyy == "flag_picked_up" and m.team(b) == tm), None)
        hit = bool(tl.window(tl.dmg_in[a], t, 5)) or any(abs(x - t) <= 2 for x in st.death_times.get(a, []))
        gap = (nxt[0] - t) if nxt else (t1 - t)
        if hit: out["forced_drops"] += 1
        if gap <= 5 and nxt and nxt[1] != a: out["quick_handoffs"] += 1
        elif gap > 5:
            g = min(gap, t1 - t); out["parked_s"] += round(g)
            if st.zone(a, t) in ("own base", "own pit"): out["parked_in_base_s"] += round(g)
    return out


def _build_rows(node, rid):
    from replaylib import Match
    from state import GameState
    from scoreboard import Scoreboard
    from strength import strength_gap
    st = GameState(Match.from_branch(rid)); sb = Scoreboard(st); m = st.m
    tl = Timeline(st, sb)
    rnd = random.Random(rid)
    gaps = {}
    for tm in st.teams:
        gaps[tm] = strength_gap(m.o["meta"]["id"], m.tag[tm], m.o["meta"].get("started"), m.tag[3 - tm],
                                {x["tag"]: x.get("rating") for x in m.o["meta"]["teams"]},
                                {m.tag[k]: [m.nm(a) for a in m.PL if m.team(a) == k] for k in (1, 2)})[1]
    mus = {tm: matchup(m, tm) for tm in st.teams}
    rows = []
    if node == "deaths_all":           # every alive player every 5 s, no sampling: for fightstate.py predictions
        for t in range(5, int(st.end - 1), 5):
            for a in m.PL:
                if st.alive(a, t):
                    rows.append({"match": rid, "team": m.tag[m.team(a)], "role": m.roles[a], "t": t,
                                 **death_features(tl, a, t, mus[m.team(a)], gaps[m.team(a)])})
    elif node == "deaths":
        last = st.end - 1 - HORIZON
        ends = {t for a in m.PL for t in st.death_times.get(a, []) if t >= st.end - 1}
        for t in range(5, int(last), SAMPLE):
            for a in m.PL:
                if not st.alive(a, t): continue
                y = int(tl.dies_within(a, t, HORIZON))
                active = bool(tl.window(tl.dmg_in[a], t, 10))
                if not y and not active:
                    if rnd.randrange(NEG_KEEP): continue
                    w = NEG_KEEP
                else: w = 1
                rows.append({"match": rid, "team": m.tag[m.team(a)], "role": m.roles[a], "t": t, "y": y, "w": w,
                             **death_features(tl, a, t, mus[m.team(a)], gaps[m.team(a)])})
    elif node == "kill_conversion":
        for v in m.PL:
            L = tl.dmg_in[v]; last = -99
            for i, (t, _, _) in enumerate(L):
                w = [x for x in L[i:] if x[0] <= t + 2]
                if sum(x[1] for x in w) < 250 or len({x[2] for x in w}) < 3 or t - last < 4 or t > st.end - 10: continue
                last = t; atk = {x[2] for x in w}; vt = m.team(v)
                f = death_features(tl, v, t, mus[vt], gaps[vt])
                # Blind as time, not a count (Denning): seconds the burst's physical attackers spent Blind from 3 s
                # before the burst to 3 s after it, overlaps on one player counted once (as eventlayer's Blind records)
                blind = round(sum(_blind_secs_on(tl, b, t - 3, t + 3) for b in atk if _physical(m, b)), 1)
                rup = sum(1 for b in atk for x in tl.ir[b] if t - 5 < x <= t + 2)
                kdat = sum(1 for b in atk for x in tl.kd[b] if t - 5 < x <= t + 2)
                rows.append({"match": rid, "team": m.tag[3 - vt], "role": m.roles[v], "t": round(t), "y": int(tl.dies_within(v, t, 8)), "w": 1,
                             "target_is_healer": f["is_healer"], "target_line": f["line"], "target_health_pct": f["health_pct"],
                             "target_ceiling": f["health_ceiling"], "target_prot_up": f["prot_up"], "target_block_up": f["block_up"],
                             "target_healers_in_range": f["healers_in_range"], "target_knocked_down": f["knocked_down_now"],
                             "target_dazed": f["dazed"], "target_deep_wound": f["deep_wound"], "target_dist_from_group": f["dist_from_group"],
                             "target_away_3000": f["away_3000"], "target_hexes": f["hexes_on"],
                             "target_healers_hexed": f["hexes_on_own_healers"],
                             "burst_damage": round(sum(x[1] for x in w)), "attackers": len(atk), "attackers_blinded": blind,
                             "attackers_interrupted": rup, "attackers_knocked_down": kdat, "strength_gap": -f["strength_gap"] if f["strength_gap"] is not None else None,
                             "own_interrupts_v_enemy_heals": mus[3 - vt]["own_interrupts_v_enemy_heals"],
                             "enemy_prots": mus[3 - vt]["enemy_prots"], "enemy_blind": mus[3 - vt]["enemy_blind"], "minute": round(t / 60, 1)})
    elif node == "flag_answer":
        import episodes as E
        from state import d
        from common import line as LINE
        fl = [(x[0] / 10, x[1], x[2]) for x in m.o.get("flags", []) if m.team(x[2])]
        for c in E.flag_cycles(st, sb):
            if "possible_s" not in c or c["own_pickup"] is None: continue
            tm = next(k for k, v in m.tag.items() if v == c["team"]); foe = 3 - tm
            pc, cc = c["enemy_cap"], c["own_cap"]
            starter = next((a for a in st.players[tm] if m.roles[a] == c["runner"]), None)
            if starter is None: continue
            mine = [x for x in st.carries if m.team(x["a"]) == tm and x["s"] <= cc and x["e"] >= pc]
            car_dmg = sum(v for cr in mine for (tt, v, _) in tl.dmg_in[cr["a"]] if cr["s"] <= tt <= cr["e"])
            pushers = len({b for cr in mine for (tt, _, b) in tl.dmg_in[cr["a"]] if cr["s"] <= tt <= cr["e"]})
            fighting = sum(1 for b in st.players[tm] if st.alive(b, pc) and (tl.window(tl.dmg_in[b], pc, 5) or tl.window(tl.dmg_out[b], pc, 5)))
            from features import _splitting
            sbt = sb.at(int(pc))
            rows.append({"match": rid, "team": c["team"], "role": c["runner"], "t": pc, "y": max(min(c["slower_than_possible_s"], 180), -30), "w": 1,
                         "possible_s": c["possible_s"], "runner_line": {"frontline": 0, "midline": 1, "backline": 2}[LINE(m, starter)],
                         "runner_is_mesa": int(c["runner"] == "Mes/A"), "runner_dead_at_enemy_cap": int(not st.alive(starter, pc)),
                         "runner_to_spawn": round(d(st.pos(starter, pc)[0], st.geo.spawn[tm])) if st.alive(starter, pc) else None,
                         "waiting_runner": int(sb.waiting_runner(tm, int(pc)) is not None),
                         "runners_used": len({x["a"] for x in st.carries if m.team(x["a"]) == tm and x["e"] <= pc}),
                         "enemies_in_the_way": sum((c.get("enemies_in_the_way") or {}).values()),
                         "carrier_damage_taken": round(car_dmg), "pushers": pushers,
                         **_drops(st, tl, fl, tm, pc, cc),
                         "own_deaths_during": sum(1 for b in st.players[tm] for tt in st.death_times.get(b, []) if pc < tt <= cc),
                         "enemy_deaths_during": sum(1 for b in st.players[foe] for tt in st.death_times.get(b, []) if pc < tt <= cc),
                         "own_fighting_at_enemy_cap": fighting, "own_splitting": _splitting(sb, tm, int(pc)),
                         "alive_diff": sbt[m.tag[tm]]["alive"] - sbt[m.tag[foe]]["alive"],
                         "morale_diff": sbt[m.tag[tm]]["morale_sum"] - sbt[m.tag[foe]]["morale_sum"],
                         "flag_lead_at_enemy_cap": max(min(sbt[m.tag[tm]]["flag_lead"], 150), -150),
                         "minute": round(pc / 60, 1), "strength_gap": gaps[tm]})
    elif node in ("npc_loss", "lord_damage", "lord_kill"):
        from state import d
        from common import PIT_R
        from scoreboard import lord_dps
        lords = {l["team"]: l["a"] for l in m.o.get("lords", [])}
        npc_hits = collections.defaultdict(list); npc_heals = collections.defaultdict(list); lord_in = collections.defaultdict(list)
        for r in m.o["ev"]:
            if not isinstance(r[3], int) or r[3] >= len(m.A): continue
            x = m.A[r[3]]
            if r[1] == "dm" and x.get("npc") in ("knight", "archer", "bodyguard") and r[2] in m.PL: npc_hits[x.get("team")].append((r[0] / 10, r[5] or 0))
            if r[1] == "hl" and x.get("npc") in ("knight", "archer", "bodyguard", "guild_lord") and r[2] in m.PL: npc_heals[x.get("team")].append((r[0] / 10, r[5] or 0))
            if r[1] == "dm" and x.get("npc") == "guild_lord" and r[2] in m.PL: lord_in[x.get("team")].append((r[0] / 10, r[5] or 0))
        def dps(a): return lord_dps(m.roles[a], m.A[a].get("p")) or 0
        for dt in st.teams:                  # dt = the defending team (whose pit / Lord)
            at = 3 - dt; pit = st.geo.pit.get(dt)
            if pit is None: continue
            if node in ("lord_damage", "lord_kill") and at in sb.lordstate.unobserved: continue    # integrity.py
            pit_npcs = [(a, v) for a, v in st.geo.npcs.items() if v["team"] == dt and v.get("pit") and v["kind"] != "guild_lord"]
            first_in = None
            for t in range(5, int(st.end - 12), SAMPLE):
                inside = [b for b in st.players[at] if st.alive(b, t) and d(st.pos(b, t)[0], pit) < PIT_R + 800]
                if not inside: first_in = None; continue
                first_in = first_in if first_in is not None else t
                defs = [b for b in st.players[dt] if st.alive(b, t) and d(st.pos(b, t)[0], pit) < PIT_R + 800]
                alive_n = [(a, v) for a, v in pit_npcs if st.npc_dead.get(a, 1e9) > t]
                alive_at = sum(1 for b in st.players[at] if st.alive(b, t))
                base = {"attackers": len(inside), "attacker_healers": sum(1 for b in inside if _healer(m, b)),
                        "attackers_share": round(len(inside) / alive_at, 2) if alive_at else 0,
                        "attackers_area_damage": sum(_aoe_skills(m, b) for b in inside),
                        "full_pit_targets": len(alive_pre) if (alive_pre := [x for x in pit_npcs if st.npc_dead.get(x[0], 1e9) > t]) else 0,
                        "attackers_lord_dps": round(sum(dps(b) for b in inside), 1),
                        "defenders": len(defs), "defender_healers": sum(1 for b in defs if _healer(m, b)),
                        "seconds_in_pit": t - first_in,
                        "knights": sum(1 for _, v in alive_n if v["kind"] == "knight"), "archers": sum(1 for _, v in alive_n if v["kind"] == "archer"),
                        "bodyguard": sum(1 for _, v in alive_n if v["kind"] == "bodyguard"),
                        "npc_damage_5s": round(sum(v for tt, v in npc_hits[dt] if t - 5 < tt <= t)),
                        "npc_healing_10s": round(sum(v for tt, v in npc_heals[dt] if t - 10 < tt <= t)),
                        "defenders_elsewhere": sum(1 for b in st.players[dt] if st.alive(b, t) and b not in defs),
                        "res_in": st.next_res(t) - t, "minute": round(t / 60, 1), "strength_gap": gaps[at]}
                if node == "lord_kill":
                    L = sb.lordstate
                    if L.dead[dt] is not None and L.dead[dt] <= t: continue
                    rows.append({"match": rid, "team": m.tag[at], "role": "", "t": t, "w": 1,
                                 "y": int(L.dead[dt] is not None and t < L.dead[dt] <= t + LORD_HORIZON), **base,
                                 "lord_health": L.health(dt, t), "lord_exposed": L.exposed(dt, t),
                                 "lord_damage_taken_60s": L.damage_net(dt, t, 60)})
                    continue
                if node == "npc_loss":
                    if not alive_n: continue
                    y = int(any(t < st.npc_dead.get(a, 1e9) <= t + 15 for a, _ in alive_n))
                    rows.append({"match": rid, "team": m.tag[at], "role": "", "t": t, "y": y, "w": 1, **base})
                else:
                    yv = sum(v for tt, v in lord_in[dt] if t < tt <= t + 10)
                    rows.append({"match": rid, "team": m.tag[at], "role": "", "t": t, "y": round(min(yv, 4000)), "w": 1, **base})
    return rows


NPC_DESC = {"attackers": "enemy players in the pit", "attacker_healers": "of which healers",
            "attackers_share": "share of the attacking team's live players in the pit (OG comms: merge before pushing the pit)",
            "attackers_area_damage": "area-damage skills on the attackers' bars (Denning P9)",
            "full_pit_targets": "pit NPCs alive (targets the defending monks must watch, P9)",
            "attackers_lord_dps": "attackers' measured damage per second against a Lord (benchmarks)",
            "defenders": "own players in the pit", "defender_healers": "of which healers",
            "seconds_in_pit": "seconds the attackers have been in the pit", "knights": "own knights alive",
            "archers": "own pit archers alive", "bodyguard": "own Bodyguard alive",
            "npc_damage_5s": "damage on the pit NPCs in the last 5 s", "npc_healing_10s": "healing on own pit NPCs and Lord in the last 10 s",
            "defenders_elsewhere": "own players alive outside the pit", "res_in": "seconds until the next res",
            "minute": "match minute", "strength_gap": "attacking minus defending team strength"}


FA_DESC = {"possible_s": "fastest possible answer (s) from the flag model at the enemy's capture",
           "runner_line": "runner 0 frontline, 1 midline, 2 backline", "runner_is_mesa": "the runner is the Mes/A",
           "runner_dead_at_enemy_cap": "the runner was dead when the enemy captured",
           "runner_to_spawn": "runner's distance to its flag spawn when the enemy captured",
           "waiting_runner": "a runner was already waiting at the spawn", "runners_used": "players who had carried so far",
           "enemies_in_the_way": "enemy presence along the runner's trip back to the spawn",
           "carrier_damage_taken": "damage the carrier took while carrying", "pushers": "enemies who hit the carrier",
           "quick_handoffs": "quick hand-offs (a teammate picked it up within 5 s)",
           "forced_drops": "drops with the carrier hit in the 5 s before, or dying",
           "parked_s": "seconds the flag lay parked (dropped 5 s or more: not running yet)",
           "parked_in_base_s": "of which in the own base (Denning: deciding not to run)", "own_deaths_during": "own deaths during the answer",
           "enemy_deaths_during": "enemy deaths during the answer", "own_fighting_at_enemy_cap": "own players fighting when the enemy captured",
           "own_splitting": "own players on a split", "alive_diff": "own minus enemy players alive",
           "morale_diff": "own minus enemy morale", "flag_lead_at_enemy_cap": "own flag lead when the enemy captured",
           "minute": "match minute", "strength_gap": "own minus enemy team strength"}


KC_DESC = {"target_is_healer": "target is a healer", "target_line": "target 0 frontline, 1 midline, 2 backline",
           "target_health_pct": "target health % when the burst started", "target_ceiling": "target's health ceiling",
           "target_prot_up": "a prot on the target", "target_block_up": "a block on the target",
           "target_healers_in_range": "target's healers in range", "target_knocked_down": "target knocked down",
           "target_dazed": "target Dazed", "target_deep_wound": "target has Deep Wound",
           "target_dist_from_group": "target's distance from its group", "target_hexes": "hexes on the target",
           "target_healers_hexed": "hexes on the target team's live healers", "target_away_3000": "target 3,000+ from its main group", "burst_damage": "damage in the 2 s burst",
           "attackers": "attackers in the burst", "attackers_blinded": "seconds the burst's physical attackers spent Blind (3 s before to 3 s after)",
           "attackers_interrupted": "interrupts on the attackers (5 s before to 2 s after)",
           "attackers_knocked_down": "knockdowns on the attackers (5 s before to 2 s after)",
           "strength_gap": "attacking minus target team strength", "own_interrupts_v_enemy_heals": "attackers' interrupt skills minus target team's heals",
           "enemy_prots": "target team's prot skills", "enemy_blind": "target team's Blind skills", "minute": "match minute"}
LK_DESC = dict(NPC_DESC, lord_health="the Lord's rebuilt health as a share of its max (lord.py)",
               lord_exposed="its Bodyguard and both knights dead", lord_damage_taken_60s="net damage on the Lord in the last 60 s")
DESC = {"deaths": DEATH_DESC, "kill_conversion": KC_DESC, "flag_answer": FA_DESC, "npc_loss": NPC_DESC, "lord_damage": NPC_DESC,
        "lord_kill": LK_DESC}
REGRESSION = {"flag_answer", "lord_damage"}      # these nodes predict a number (seconds), not a yes/no
# Lord damage is lopsided (most 10 s windows little or none, a few big bursts): fitted in two parts (Denning, after
# batch 9) - the chance of any Lord damage in the window, then how much when there is some (on a log scale) - and read
# two ways: the middle of the predicted spread for typical error, its average for the share of the spread explained.
TWO_PART = {"lord_damage"}


class TwoPart:
    """Chance of any (classifier) x amount when there is some (regressor on log(1 + y)), both glass box (EBM)."""
    def __init__(self, n_matches):
        self.n = n_matches

    def fit(self, X, y, sample_weight=None):
        yv = np.asarray(y, float); pos = yv > 0
        self.rate = float(pos.mean())
        self.clf = _ebm(self.n, False).fit(X, pos.astype(int))
        Xp = X[pos] if hasattr(X, "iloc") else X[pos]
        self.reg = _ebm(self.n, True).fit(Xp, np.log1p(yv[pos]))
        res = np.log1p(yv[pos]) - self.reg.predict(Xp)
        self.sigma = float(np.std(res)) if len(res) > 1 else 0.0
        self.smear = float(np.mean(np.exp(res))) if len(res) else 1.0      # back from the log scale (Duan)
        return self

    def chance(self, X): return self.clf.predict_proba(X)[:, 1]

    def predict(self, X):
        """The middle of the predicted spread (what minimizes the typical error): 0 when damage is less likely than not."""
        from statistics import NormalDist
        p, mu = self.chance(X), self.reg.predict(X)
        out = np.zeros(len(p))
        nd = NormalDist()
        for i, (pi, mi) in enumerate(zip(p, mu)):
            if pi > 0.5: out[i] = max(math.expm1(mi + self.sigma * nd.inv_cdf(min(max(1 - 0.5 / pi, 1e-6), 1 - 1e-6))), 0.0)
        return out

    def predict_mean(self, X):
        return self.chance(X) * np.maximum(np.exp(self.reg.predict(X)) * self.smear - 1, 0)

    def term_importances(self): return self.clf.term_importances()


def _model(node, n_matches):
    return TwoPart(n_matches) if node in TWO_PART else _ebm(n_matches, node in REGRESSION)


_ROWS = {}
def node_rows(node, rid):
    """A node's rows for one match (shared cache, cache.py: keyed by the engine code they are built from)."""
    import cache
    key = (node, rid)
    if key not in _ROWS:
        _ROWS[key] = cache.prepared("rows", rid, lambda: _build_rows(node, rid), sub=node)
    return _ROWS[key]


def heldout_node(node, ids, rid):
    """(model, features) for a node fitted on ids without rid, fitted once per training set (cache.py)."""
    import cache
    def fit(train):
        df, X, y, g, w = _frame(node, train)
        if node in REGRESSION: y = df["y"].astype(float)
        return (_model(node, g.nunique()).fit(X, y, sample_weight=None if node in REGRESSION else w), list(X.columns))
    return cache.heldout("node", rid, list(ids), fit, sub=node)


MATCH_FIXED = {"deaths": set(MATCHUP_KEYS) | {"strength_gap"},
               "kill_conversion": {"own_interrupts_v_enemy_heals", "enemy_prots", "enemy_blind", "strength_gap"},
               "flag_answer": {"strength_gap"}, "npc_loss": {"strength_gap"}, "lord_damage": {"strength_gap"},
               "lord_kill": {"strength_gap"}}
STAGE_FIXED = 60     # matches before variables fixed for a whole match (matchup counts) are used (they fingerprint matches)


# variables tested and held back from a node because they made its predictions on unseen matches worse (retested
# whenever the node is refitted with more data; see the learning report)
HELD_BACK = {"npc_loss": {"attackers_area_damage"}}


def features_for(node, n_matches):
    keep_fixed = {"strength_gap"} if n_matches < STAGE_FIXED else MATCH_FIXED[node]
    return [k for k in DESC[node] if (k not in MATCH_FIXED[node] or k in keep_fixed) and k not in HELD_BACK.get(node, set())]


def _frame(node, ids):
    import pandas as pd
    from integrity import usable
    ids = usable(list(ids))
    df = pd.DataFrame([r for rid in ids for r in node_rows(node, rid)])
    feats = features_for(node, df["match"].nunique())
    return df, df[feats].astype(float), df["y"].astype(int), df["match"], df["w"].astype(float)


def _ebm(n_matches, regression=False):
    from interpret.glassbox import ExplainableBoostingClassifier as EBM, ExplainableBoostingRegressor as EBR
    kw = dict(max_bins=16, outer_bags=4, min_samples_leaf=20 if not regression else 8, max_rounds=500,
              interactions=(6 if n_matches >= 25 else 0) if not regression else 0, random_state=7)
    return (EBR if regression else EBM)(**kw)


def _wmetrics(p, y, w):
    p = np.clip(p, 0.002, 0.998)
    ll = float(np.sum(w * -(y * np.log(p) + (1 - y) * np.log(1 - p))) / np.sum(w))
    # ranking quality: how often a row that led to the result scores above one that didn't (AUC)
    from sklearn.metrics import roc_auc_score
    return {"log_loss": round(ll, 4), "auc": round(float(roc_auc_score(y, p, sample_weight=w)), 3), "rate": round(float(np.average(y, weights=w)), 4)}


def _node_job(job):
    """One fit for a node: a held-out fold (predictions for the matches left out, and the simple baseline's) or the
    final fit on everything (job kind "full"). Top level so it can run in another process (parallel.py)."""
    kind, n_matches, regression, Xtr, ytr, wtr, Xte, base_cols = job[:8]
    node = job[8] if len(job) > 8 else None
    kw = {} if regression else {"sample_weight": wtr}
    e = (TwoPart(n_matches) if node in TWO_PART else _ebm(n_matches, regression)).fit(Xtr, ytr, **kw)
    if kind == "full": return e
    if node in TWO_PART:
        return {"glass": e.predict(Xte), "glass_mean": e.predict_mean(Xte), "base": float(np.median(ytr)), "base_mean": float(np.mean(ytr))}
    if regression: return {"glass": e.predict(Xte), "base": float(np.median(ytr)), "base_mean": float(np.mean(ytr))}
    from sklearn.linear_model import LogisticRegression
    b = LogisticRegression(max_iter=1000).fit(Xtr[base_cols].fillna(0), ytr, sample_weight=wtr)
    return {"glass": e.predict_proba(Xte)[:, 1], "base": b.predict_proba(Xte[base_cols].fillna(0))[:, 1]}


BASE_COLS = {"deaths": ["health_pct", "damage_taken_3s"], "kill_conversion": ["burst_damage", "target_health_pct"],
             "npc_loss": ["attackers", "defenders"], "lord_kill": ["attackers", "defenders"]}


def _jobs(node, X, y, g, w, regression):
    from sklearn.model_selection import GroupKFold
    folds = list(GroupKFold(n_splits=min(6, g.nunique())).split(X, y, g))
    bc = BASE_COLS.get(node, [])
    jobs = [("fold", g.iloc[tr].nunique(), regression, X.iloc[tr], y.iloc[tr], w.iloc[tr], X.iloc[te], bc, node) for tr, te in folds]
    jobs.append(("full", g.nunique(), regression, X, y, w, None, bc, node))
    return folds, jobs


def _folds_and_full(node, X, y, g, w, regression):
    """Every held-out fold and the final fit, side by side (parallel.py); the same fits as one after another."""
    import parallel
    folds, jobs = _jobs(node, X, y, g, w, regression)
    res = parallel.run(_node_job, jobs)
    return folds, res[:-1], res[-1]


def validate_regression(node, df, X, y, g, w, _done=None):
    """Held out by match: mean absolute error against always guessing the training median, and the share of the spread
    explained (R squared)."""
    folds, res, _ = _done or _folds_and_full(node, X, y, g, w, True)
    pe, pb, pem, pbm = (np.zeros(len(y)) for _ in range(4))
    for (tr, te), r in zip(folds, res):
        pb[te] = r["base"]; pe[te] = r["glass"]
        pem[te] = r.get("glass_mean", r["glass"]); pbm[te] = r.get("base_mean", r["base"])
    yv = y.values.astype(float)
    r2 = lambda p: round(1 - float(np.sum((yv - p) ** 2) / np.sum((yv - yv.mean()) ** 2)), 3)
    # typical error from the middle reading against always guessing the median; share of the spread explained from the
    # average reading against always guessing the average (the fair baseline for each measure)
    out = {"glass box": {"mae_s": round(float(np.mean(np.abs(yv - pe))), 1), "r2": r2(pem)},
           "simple baseline": {"mae_s": round(float(np.mean(np.abs(yv - pb))), 1), "r2": r2(pbm)},
           "baseline uses": ["the median (typical error)", "the average (spread explained)"]}
    # Denning (after batch 9): "adds" only if no worse on typical error AND better on the spread explained; either alone
    # misleads on a lopsided result (Lord damage read "adds" at a typical error of 125 against 92 for the median)
    better = out["glass box"]["mae_s"] <= out["simple baseline"]["mae_s"] and out["glass box"]["r2"] > out["simple baseline"]["r2"] + 0.05
    out["verdict"] = "adds to the simple baseline" if better else "no better than the simple baseline yet"
    if node in TWO_PART: out["form"] = "two parts: chance of any, then amount when there is some (log scale)"
    return out, pe


def readable_seconds(e, names, X):
    """Curves of a regression node in seconds (not win-chance points)."""
    imp = e.term_importances(); out = []
    for i, name in enumerate(e.term_names_):
        f = e.term_features_[i]
        if len(f) != 1: continue
        f = f[0]; edges = list(e.bins_[f][0]) if len(e.bins_[f]) else []
        col = X[names[f]].dropna(); lo, hi = (float(col.min()), float(col.max())) if len(col) else (None, None)
        b = [lo] + [float(x) for x in edges] + [hi]
        sc, sd = e.term_scores_[i], e.standard_deviations_[i]
        out.append({"term": name, "description": "", "importance": round(float(imp[i]), 3),
                    "curve": [{"from": round(b[j], 2) if b[j] is not None else None, "to": round(b[j + 1], 2) if b[j + 1] is not None else None,
                               "points": round(float(sc[j + 1]), 1), "plus_minus": round(float(sd[j + 1]), 1)} for j in range(len(b) - 1)]})
    return sorted(out, key=lambda t: -t["importance"])


def validate(node, df, X, y, g, w, _done=None):
    folds, res, _ = _done or _folds_and_full(node, X, y, g, w, False)
    preds = {n: np.zeros(len(y)) for n in ("simple baseline", "glass box")}
    for (tr, te), r in zip(folds, res):
        preds["simple baseline"][te] = r["base"]; preds["glass box"][te] = r["glass"]
    out = {n: _wmetrics(p, y.values, w.values) for n, p in preds.items()}
    out["baseline uses"] = BASE_COLS[node]
    out["verdict"] = "adds to the simple baseline" if out["glass box"]["log_loss"] < out["simple baseline"]["log_loss"] - 0.0005 else "no better than the simple baseline yet"
    return out, preds["glass box"]


COST_ORDER = ["deaths", "lord_kill", "npc_loss", "kill_conversion", "lord_damage", "flag_answer"]   # slowest first (measured)


def fit_nodes(nodes, ids):
    """Fit and validate several nodes with every fit pooled together (each node's held-out folds and final fit), so all
    cores stay busy instead of one node after another; the slowest node's fits go first. Same fits, same results as
    fit_node for each node. Returns {node: (summary, model, df, held-out predictions)}."""
    import parallel
    prep, jobs, owner = {}, [], []
    for node in sorted(nodes, key=lambda n: COST_ORDER.index(n) if n in COST_ORDER else 99):
        df, X, y, g, w = _frame(node, ids)
        regression = node in REGRESSION
        if regression: y = df["y"].astype(float)
        folds, js = _jobs(node, X, y, g, w, regression)
        prep[node] = (df, X, y, g, w, regression, folds)
        jobs += js; owner += [node] * len(js)
    res = parallel.run(_node_job, jobs)
    out = {}
    for node in nodes:
        df, X, y, g, w, regression, folds = prep[node]
        r = [x for x, o in zip(res, owner) if o == node]
        done = (folds, r[:-1], r[-1])
        if node in TWO_PART:
            val, held = validate_regression(node, df, X, y, g, w, done); e = done[2]
            terms = [dict(t, term=t["term"] + " (chance of any)") for t in M.readable(e.clf, list(X.columns), X)]
            for t in readable_seconds(e.reg, list(X.columns), X):
                for c in t["curve"]:
                    c["points"] = round((math.exp(c["points"]) - 1) * 100, 1); c["plus_minus"] = round((math.exp(c["plus_minus"]) - 1) * 100, 1)
                terms.append(dict(t, term=t["term"] + " (amount when there is some, % more)", base_term=t["term"]))
            for t in terms: t.setdefault("base_term", t["term"].split(" (")[0])
        elif regression:
            val, held = validate_regression(node, df, X, y, g, w, done); e = done[2]
            terms = readable_seconds(e, list(X.columns), X)
        else:
            val, held = validate(node, df, X, y, g, w, done); e = done[2]
            terms = M.readable(e, list(X.columns), X)
        for t in terms:
            if "curve" in t: t["description"] = DESC[node].get(t.get("base_term", t["term"]), t["description"])
        summary = {"node": node, "matches": int(g.nunique()), "rows": int(len(y)),
                   "events": int(y.sum()) if node not in REGRESSION else None, "validation": val,
                   "note": ("'chance of any' curves: points of the chance of any Lord damage in the window; 'amount' curves: % more "
                            "Lord damage when there is some" if node in TWO_PART else
                            "seconds added to (or taken off) the answer, compared with the average answer" if node in REGRESSION else
                            "points = change in the chance of the result for an otherwise even (50%) case; read the direction and size, "
                            "not the absolute level"), "terms": terms}
        os.makedirs(NODE_DIR, exist_ok=True)
        json.dump(summary, open(os.path.join(NODE_DIR, f"{node}.json"), "w"), indent=1)
        out[node] = (summary, e, df, held)
    return out


def fit_node(node, ids):
    return fit_nodes([node], ids)[node]


def explain_row(e, row, feats):
    import pandas as pd
    x = pd.DataFrame([{k: row.get(k) for k in feats}]).astype(float)
    contrib = e.eval_terms(x)[0]
    total = float(np.ravel(e.intercept_)[0]) + float(contrib.sum())
    parts = sorted([(e.term_names_[i], M._points(c)) for i, c in enumerate(contrib) if abs(M._points(c)) >= 1], key=lambda kv: -abs(kv[1]))
    return round(M.sig(total) * 100, 1), parts


if __name__ == "__main__":
    a = sys.argv[1:]
    ids = [m for b in M.batches() for m in b["matches"]]
    if a and a[0] == "fit":
        for node in (a[1:] or ["deaths", "kill_conversion", "flag_answer", "npc_loss", "lord_damage", "lord_kill"]):
            s, e, df, held = fit_node(node, ids)
            print(f"== {node}: {s['matches']} matches, {s['rows']} rows, {s['events']} events")
            print(json.dumps(s["validation"]))
            print([(t["term"], t["importance"]) for t in s["terms"][:12]])
    elif a and a[0] == "explain":
        rid, clock, who = a[1], a[2], " ".join(a[3:])
        t = int(clock.split(":")[0]) * 60 + int(clock.split(":")[1])
        others = [x for x in ids if x != rid]
        df, X, y, g, w = _frame("deaths", others)
        e = _ebm(g.nunique()).fit(X, y, sample_weight=w)
        rows = [r for r in node_rows("deaths", rid) if f"{r['team']} {r['role']}" == who]
        for r in sorted(rows, key=lambda r: abs(r["t"] - t))[:1] + [r for r in rows if t - 12 <= r["t"] <= t and r["t"] != sorted(rows, key=lambda r: abs(r["t"] - t))[0]["t"]]:
            p, parts = explain_row(e, r, list(X.columns))
            print(f"{r['t'] // 60}:{r['t'] % 60:02d} risk {p}% | " + ", ".join(f"{k} {v:+}" for k, v in parts[:8]))
