"""Node models along the causal map (data/model/causal_map.json): each explains one result from what happened before it,
so the engine can say WHY, not only who is winning. Glass box (Explainable Boosting Machine), readable, tested on
matches it never saw. Time order is enforced: every feature is measured at or before the moment, the label after it.

Nodes so far:
- deaths: one row per alive player every SAMPLE s; label = the player dies within HORIZON s. Features: the player's
  state (health, health ceiling, damage taken, attackers, knockdowns, Daze, Deep Wound, cripple, interrupts, prots and
  blocks up, conditions it took on itself), its support (healers in range, healers dead, allies and enemies near, local
  numbers, distance from its group and pit), the situation (res timer, flag lead, minute, strength gap) and the
  matchup (enemy threats against own answers). Rows with no damage taken in 10 s are kept at 1 in NEG_KEEP and weighted.
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
from common import REPO, CAST_R, PROT_SKILLS, BLOCKS, RES_EVERY
import model as M
from buildfeat import matchup

NODE_DIR = os.path.join(REPO, "data", "model", "nodes")
CACHE = "/tmp/gvg_node_rows"
SAMPLE, HORIZON, NEG_KEEP = 3, 10, 4
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
        for e in m.o.get("effects", []):
            if e[0] is None: continue
            s0, s1 = e[0] / 10, (e[1] or 10 ** 9) / 10
            if e[2] == "c" and e[7]: self.cond[e[5]].append((s0, s1, e[7], m.team(e[4]) if isinstance(e[4], int) else None))
            elif e[2] == "e": self.ench[e[5]].append((s0, s1, m.sk(e[3])))
        self.healers = {tm: [a for a in st.players[tm] if _healer(m, a)] for tm in st.teams}
        self.deaths = {a: sorted(st.death_times.get(a, [])) for a in m.PL}

    def window(self, L, t, w): return [x for x in L if t - w < x[0] <= t]

    def has_cond(self, a, t, names, own_source=None):
        tm = self.m.team(a)
        return any(s0 <= t <= s1 and n in names and (own_source is None or (src == tm) == own_source) for s0, s1, n, src in self.cond.get(a, []))

    def ench_up(self, a, t, names):
        return any(s0 <= t <= s1 and n in names for s0, s1, n in self.ench.get(a, []))

    def dies_within(self, a, t, h):
        L = self.deaths[a]; i = bisect.bisect_right(L, t)
        return i < len(L) and L[i] <= t + h


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
        "healers_in_range": len(in_range), "healers_dead": sum(1 for b in tl.healers[tm] if b != a and not st.alive(b, t)),
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
    "block_up": "a block enchantment up now", "healers_in_range": "own healers alive within cast range",
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
    """Area-damage skills on a player's bar (Denning P9: knights ball up and eat area damage)."""
    if a not in _AOE:
        from buildfeat import _skills, FEATURES
        S = _skills()
        _AOE[a] = sum(1 for b in m.A[a].get("bar", []) if b and S.get(m.sk(b)) and FEATURES["area_damage"](S[m.sk(b)]))
    return _AOE[a]


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
                                {x["tag"]: x.get("rating") for x in m.o["meta"]["teams"]})[1]
    mus = {tm: matchup(m, tm) for tm in st.teams}
    rows = []
    if node == "deaths":
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
                blind = sum(1 for b in atk if tl.has_cond(b, t + 1, {"blind"}))
                rup = sum(1 for b in atk for x in tl.ir[b] if t - 5 < x <= t + 2)
                kdat = sum(1 for b in atk for x in tl.kd[b] if t - 5 < x <= t + 2)
                rows.append({"match": rid, "team": m.tag[3 - vt], "role": m.roles[v], "t": round(t), "y": int(tl.dies_within(v, t, 8)), "w": 1,
                             "target_is_healer": f["is_healer"], "target_line": f["line"], "target_health_pct": f["health_pct"],
                             "target_ceiling": f["health_ceiling"], "target_prot_up": f["prot_up"], "target_block_up": f["block_up"],
                             "target_healers_in_range": f["healers_in_range"], "target_knocked_down": f["knocked_down_now"],
                             "target_dazed": f["dazed"], "target_deep_wound": f["deep_wound"], "target_dist_from_group": f["dist_from_group"],
                             "target_away_3000": f["away_3000"],
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
    elif node in ("npc_loss", "lord_damage"):
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
            pit_npcs = [(a, v) for a, v in st.geo.npcs.items() if v["team"] == dt and v.get("pit") and v["kind"] != "guild_lord"]
            first_in = None
            for t in range(5, int(st.end - 12), SAMPLE):
                inside = [b for b in st.players[at] if st.alive(b, t) and d(st.pos(b, t)[0], pit) < PIT_R + 800]
                if not inside: first_in = None; continue
                first_in = first_in if first_in is not None else t
                defs = [b for b in st.players[dt] if st.alive(b, t) and d(st.pos(b, t)[0], pit) < PIT_R + 800]
                alive_n = [(a, v) for a, v in pit_npcs if st.npc_dead.get(a, 1e9) > t]
                base = {"attackers": len(inside), "attacker_healers": sum(1 for b in inside if _healer(m, b)),
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
                if node == "npc_loss":
                    if not alive_n: continue
                    y = int(any(t < st.npc_dead.get(a, 1e9) <= t + 15 for a, _ in alive_n))
                    rows.append({"match": rid, "team": m.tag[at], "role": "", "t": t, "y": y, "w": 1, **base})
                else:
                    yv = sum(v for tt, v in lord_in[dt] if t < tt <= t + 10)
                    rows.append({"match": rid, "team": m.tag[at], "role": "", "t": t, "y": round(min(yv, 4000)), "w": 1, **base})
    return rows


NPC_DESC = {"attackers": "enemy players in the pit", "attacker_healers": "of which healers",
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
           "target_dist_from_group": "target's distance from its group", "target_away_3000": "target 3,000+ from its main group", "burst_damage": "damage in the 2 s burst",
           "attackers": "attackers in the burst", "attackers_blinded": "attackers Blind during the burst",
           "attackers_interrupted": "interrupts on the attackers (5 s before to 2 s after)",
           "attackers_knocked_down": "knockdowns on the attackers (5 s before to 2 s after)",
           "strength_gap": "attacking minus target team strength", "own_interrupts_v_enemy_heals": "attackers' interrupt skills minus target team's heals",
           "enemy_prots": "target team's prot skills", "enemy_blind": "target team's Blind skills", "minute": "match minute"}
DESC = {"deaths": DEATH_DESC, "kill_conversion": KC_DESC, "flag_answer": FA_DESC, "npc_loss": NPC_DESC, "lord_damage": NPC_DESC}
REGRESSION = {"flag_answer", "lord_damage"}      # these nodes predict a number (seconds), not a yes/no


def node_rows(node, rid):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, f"{node}_{rid}.json")
    if not os.path.exists(p): json.dump(_build_rows(node, rid), open(p, "w"))
    return json.load(open(p))


MATCH_FIXED = {"deaths": set(MATCHUP_KEYS) | {"strength_gap"},
               "kill_conversion": {"own_interrupts_v_enemy_heals", "enemy_prots", "enemy_blind", "strength_gap"},
               "flag_answer": {"strength_gap"}, "npc_loss": {"strength_gap"}, "lord_damage": {"strength_gap"}}
STAGE_FIXED = 60     # matches before variables fixed for a whole match (matchup counts) are used (they fingerprint matches)


# variables tested and held back from a node because they made its predictions on unseen matches worse (retested
# whenever the node is refitted with more data; see the learning report)
HELD_BACK = {"npc_loss": {"attackers_area_damage"}}


def features_for(node, n_matches):
    keep_fixed = {"strength_gap"} if n_matches < STAGE_FIXED else MATCH_FIXED[node]
    return [k for k in DESC[node] if (k not in MATCH_FIXED[node] or k in keep_fixed) and k not in HELD_BACK.get(node, set())]


def _frame(node, ids):
    import pandas as pd
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


def validate_regression(node, df, X, y, g, w):
    """Held out by match: mean absolute error against always guessing the training median, and the share of the spread
    explained (R squared)."""
    from sklearn.model_selection import GroupKFold
    pe, pb = np.zeros(len(y)), np.zeros(len(y))
    for tr, te in GroupKFold(n_splits=min(6, g.nunique())).split(X, y, g):
        pb[te] = float(np.median(y.iloc[tr]))
        pe[te] = _ebm(g.iloc[tr].nunique(), True).fit(X.iloc[tr], y.iloc[tr]).predict(X.iloc[te])
    yv = y.values.astype(float)
    r2 = lambda p: round(1 - float(np.sum((yv - p) ** 2) / np.sum((yv - yv.mean()) ** 2)), 3)
    out = {"glass box": {"mae_s": round(float(np.mean(np.abs(yv - pe))), 1), "r2": r2(pe)},
           "simple baseline": {"mae_s": round(float(np.mean(np.abs(yv - pb))), 1), "r2": r2(pb)}, "baseline uses": ["the median"]}
    # judged on both: typical error, and share of the spread explained (a result that is usually 0, like Lord damage,
    # makes the median look good on typical error alone)
    better = out["glass box"]["mae_s"] < out["simple baseline"]["mae_s"] - 0.5 or out["glass box"]["r2"] > out["simple baseline"]["r2"] + 0.05
    out["verdict"] = "adds to the simple baseline" if better else "no better than the simple baseline yet"
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


def validate(node, df, X, y, g, w):
    from sklearn.model_selection import GroupKFold
    from sklearn.linear_model import LogisticRegression
    base_cols = {"deaths": ["health_pct", "damage_taken_3s"], "kill_conversion": ["burst_damage", "target_health_pct"],
                 "npc_loss": ["attackers", "defenders"]}[node]
    preds = {n: np.zeros(len(y)) for n in ("simple baseline", "glass box")}
    for tr, te in GroupKFold(n_splits=min(6, g.nunique())).split(X, y, g):
        b = LogisticRegression(max_iter=1000).fit(X.iloc[tr][base_cols].fillna(0), y.iloc[tr], sample_weight=w.iloc[tr])
        preds["simple baseline"][te] = b.predict_proba(X.iloc[te][base_cols].fillna(0))[:, 1]
        e = _ebm(g.iloc[tr].nunique()).fit(X.iloc[tr], y.iloc[tr], sample_weight=w.iloc[tr])
        preds["glass box"][te] = e.predict_proba(X.iloc[te])[:, 1]
    out = {n: _wmetrics(p, y.values, w.values) for n, p in preds.items()}
    out["baseline uses"] = base_cols
    out["verdict"] = "adds to the simple baseline" if out["glass box"]["log_loss"] < out["simple baseline"]["log_loss"] - 0.0005 else "no better than the simple baseline yet"
    return out, preds["glass box"]


def fit_node(node, ids):
    df, X, y, g, w = _frame(node, ids)
    if node in REGRESSION:
        y = df["y"].astype(float)
        val, held = validate_regression(node, df, X, y, g, w)
        e = _ebm(g.nunique(), True).fit(X, y)
        terms = readable_seconds(e, list(X.columns), X)
    else:
        val, held = validate(node, df, X, y, g, w)
        e = _ebm(g.nunique()).fit(X, y, sample_weight=w)
        terms = M.readable(e, list(X.columns), X)
    for t in terms:
        if "curve" in t: t["description"] = DESC[node].get(t["term"], t["description"])
    summary = {"node": node, "matches": int(g.nunique()), "rows": int(len(y)),
               "events": int(y.sum()) if node not in REGRESSION else None, "validation": val,
               "note": ("seconds added to (or taken off) the answer, compared with the average answer" if node in REGRESSION else
                        "points = change in the chance of the result for an otherwise even (50%) case; read the direction and size, "
                        "not the absolute level"), "terms": terms}
    os.makedirs(NODE_DIR, exist_ok=True)
    json.dump(summary, open(os.path.join(NODE_DIR, f"{node}.json"), "w"), indent=1)
    return summary, e, df, held


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
        for node in (a[1:] or ["deaths", "kill_conversion", "flag_answer", "npc_loss", "lord_damage"]):
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
