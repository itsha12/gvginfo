"""Variables the commentary and comms point to (Denning: the new variables are the most important thing they give),
each measured in every stored replay and tested against the outcome the speaker said it drives. A variable that holds
up moves into the model it belongs to (win model candidate in features.CANDIDATES, or a node model's variables);
one that doesn't is kept here with its result so it isn't proposed again without new evidence.

Each entry: the claim that suggested it (paraphrased, with source and match tag), how it is measured, the outcome,
and the result: rates by group with a 90% interval from resampling whole matches, and a verdict (supported,
contradicted, unclear). Comparisons are made within strata (local numbers, build) so a variable isn't credited
with what numbers or builds already explain.

Variables (more can be added to VARS):
  solo_monk        a group whose only healer is one monk is easier to kill ("solo monk, go on the monk")
  no_healer_group  a group of 2+ with no healer loses players more often ("keep a prot plus a monk on one side and
                   the rit plus a monk on the other at all times")
  spread           a tight group takes more deaths against area damage ("spread out", vs invoke and Ele spikes)
  strip_on_spike   an enchantment removed from the target as a spike lands makes it kill ("double Shatter kills")
  armor_on_spike   Cracked Armor (Shell Shock) on the target when a spike lands makes it kill ("Shell Shock between two
                   and one")
  hexed_spikers    spikers carrying hexes land fewer kills ("Migraine not covered", "why are we not killing")
  low_morale       a player with a big death penalty is easier to kill ("their warrior has 30 DP, we could fight him")
  merge            pushing the enemy pit with the whole team kills more NPCs for fewer deaths ("whoever called to merge,
                   we ended way earlier")
  turtle           a team sitting in its own base gives up the game to Lord damage unless it breaks out ("they're
                   turtling, we have to make a play"); also a win-model candidate (features.CANDIDATES turtle_diff)
  interrupted_spikers  the spiking team interrupted just before the spike lands fewer kills ("Complicate my Deep Wound")
  area_damage_spacing  area damage taken against allies within 322 (the right test for "spread out")
  spike_caster_sets, spike_target_shield  weapon sets on spikes (40/40 against shields)
  footmen          footmen lost and the result
  portal           Isle of Solitude: portal jumps (fake collapse, then port in) and what follows them
Not measurable from the replay data (said in the comms, kept as open items): gate or lock control, terrain and line of
sight (stairs, walls, choke points), energy, call timing ("4, 3, 2, 1").

Usage:  python3 comms_vars.py [names...]      measure (all by default), write data/benchmarks/comms_variables.json
In code: measure(names) -> {name: result}."""
import collections, json, math, os, random, statistics, subprocess, sys
from common import REPO, CAST_R

OUT = os.path.join(REPO, "data", "benchmarks", "comms_variables.json")
SOURCE = {
    "solo_monk": "OG comms [ohno v One], [ohno v NwAy]: calls of 'solo monk' as the moment to commit (go on the monk)",
    "no_healer_group": "OG comms [ohno v One]: keep a prot and a monk on one side and the Rit and a monk on the other at all times",
    "spread": "OG comms [ohno v Fun], [OG v cope J]: 'spread out' against invoke and Ele spikes",
    "strip_on_spike": "OG comms [ohno v Crew]: 'double Shatter kills'",
    "armor_on_spike": "OG comms [OG v cope J]: land Shell Shock between 'two' and 'one' of the countdown",
    "hexed_spikers": "OG comms [OG v cope J], [OG v hdm]: Migraine not covered on a spiker, 'why are we not killing'",
    "low_morale": "OG comms [ohno v One]: their warrior has 30 DP, we could just fight him",
    "merge": "OG comms [ohno v Crew]: whoever called to merge, we ended way earlier",
    "turtle": "OG comms [ohno v One], [ohno v Crew]: they are turtling, so we have to make a play; if they get a kill it may break the turtle",
    "portal": "OG comms [ohno v One], [ohno v Fun]: fake a collapse, then port back in; every rotation does Lord damage",
}


def stored():
    return list(json.loads(subprocess.check_output(["git", "-C", REPO, "show", "origin/replays:index.json"]))["matches"])


def _boot(groups, stat, n=600, seed=7):
    """90% interval of stat over resampled whole matches; groups = {match: [records]}."""
    rnd = random.Random(seed); ks = list(groups); vals = []
    for _ in range(n):
        s = [r for k in (rnd.choice(ks) for _ in ks) for r in groups[k]]
        v = stat(s)
        if v is not None: vals.append(v)
    if len(vals) < 20: return None
    vals.sort(); return [round(vals[int(.05 * len(vals))], 3), round(vals[int(.95 * len(vals)) - 1], 3)]


def _rate(rs, key="y"): return round(sum(r[key] for r in rs) / len(rs), 3) if rs else None


def _strat_diff(rs, flag, key="y", strata="s"):
    """Rate difference (flag minus not), averaged over strata with both sides present, weighted by stratum size."""
    by = collections.defaultdict(lambda: ([], []))
    for r in rs: by[r[strata]][0 if r[flag] else 1].append(r[key])
    num = den = 0
    for a, b in by.values():
        if len(a) >= 3 and len(b) >= 3:
            w = len(a) + len(b); num += w * (sum(a) / len(a) - sum(b) / len(b)); den += w
    return round(num / den, 3) if den else None


def _verdict(diff, ci, expect):
    if diff is None or ci is None: return "unclear (too few cases)"
    if ci[0] > 0 or ci[1] < 0:
        ok = (diff > 0) == (expect > 0)
        return "supported" if ok else "contradicted"
    return "unclear (interval crosses zero)"


# ---------------------------------------------------------------- per-match records
def _phase_groups(rid):
    """Each group in each phase with its healers, size, the numbers it faced and whether it lost players."""
    import events as EV
    a = EV.analysis(rid); out = []
    for p in a["phases"]:
        for tag, x in p["teams"].items():
            for g in x.get("groups", []):
                c = g.get("capacities") or {}
                try: own, en = map(int, g["numbers"].split("v"))
                except (ValueError, KeyError): continue
                if en == 0: continue
                out.append({"m": rid, "team": tag, "zone": g["zone"], "size": own, "enemies": en, "healers": c.get("healers", 0),
                            "lost": int((c.get("losses") or 0) > 0), "kills": c.get("kills") or 0, "secs": p["secs"],
                            "job": g.get("job"), "s": f"{max(-2, min(2, own - en))}"})
    return out


def _spike_rows(rid):
    import events as EV
    from forensics import Forensics, skilldata
    F = Forensics(rid); out = []
    for tm in F.tag:
        for t0, tgt, dmg, win, died in EV._spikes(F, tm):
            atk = sorted({x[1] for x in win})
            strip = [c for c in F.casts() if c[0] in F.m.PL and F.m.team(c[0]) == tm and c[5] == tgt and t0 - 2 <= c[2] <= t0 + 1
                     and "Enchantment" in (F.sdata(c[1]).get("removes") or []) and c[4] == "finished"]
            cracked = F.has(tgt, "c", "cracked_armor", t0) or F.has(tgt, "c", "weakness_or_cracked_armor", t0)
            hexed = sum(1 for x in atk if any(e[2] == "h" and e[5] == x and e[0] is not None and e[0] <= t0 * 10 and (e[1] is None or e[1] >= t0 * 10)
                                              for e in F.m.o.get("effects", [])))
            l = EV._landing(win)
            sets = [F.weapon_set(x, t0) for x in atk]
            caster = sum(1 for w in sets if w and w.get("hct") and "Shield" not in w["label"])
            shielded = sum(1 for w in sets if w and "Shield" in w["label"])
            tw = F.weapon_set(tgt, t0)
            irs = sum(1 for x in F.players(tm) for i in F.intr_on(x, t0 - 5, t0 + 1))
            out.append({"m": rid, "y": int(died), "strip": int(bool(strip)), "cracked": int(cracked), "hexed": int(hexed > 0),
                        "spread": l["spread_s"], "s": f"{min(l['attackers'], 5)}", "team": F.tag[tm],
                        "caster_sets": int(caster > shielded), "target_shield": int(bool(tw and "Shield" in tw["label"])), "t": t0,
                        "interrupted": int(irs >= 1)})
    return out


def _player_rows(rid):
    """Every 5 s, every alive player in a fight: its own death penalty, its group's spacing, and whether it dies in 10 s;
    plus each team's share of players sitting in its own base (turtle) and what happened in the next 60 s."""
    import events as EV
    from forensics import Forensics
    F = Forensics(rid); a = EV.analysis(rid); m = F.m
    from forensics import skilldata
    from common import IN_AREA
    AOE = {n for n, sd in skilldata().items() if sd.get("aoe")}
    aoe_hits = collections.defaultdict(list)      # victim -> [(t, damage)] from area skills
    for e in F.ev:
        if e[1] == "dm" and e[3] in m.PL and e[2] in m.PL and m.team(e[2]) != m.team(e[3]) and (e[5] or 0) > 0:
            sid = F.hit_skill(e[2], e[0] / 10, e[4])
            if sid is not None and F.sname(sid) in AOE: aoe_hits[e[3]].append((e[0] / 10, e[5]))
    dt = collections.defaultdict(list)
    for e in F.ev:
        if e[1] == "dt" and e[2] in m.PL: dt[e[2]].append(e[0] / 10)
    sb = {r["t"]: r for r in a["scoreboard"]}; st = {r["t"]: r for r in a["state"]}
    aoe = {}
    for tm in F.tag:
        foes = [x for x in m.PL if m.team(x) != tm]
        aoe[tm] = int(sum(1 for x in foes if m.A[x].get("p") == "Elementalist") >= 2)
    pl, tu = [], []
    for t in sorted(sb):
        if t < 20: continue
        for tm, tag in F.tag.items():
            row = sb[t].get(tag) or {}; mor = row.get("morale") or {}
            gs = m.groups(tm, t * 10)
            for g in gs:
                if len(g) < 3: continue
                pos = [(x, m.snap(x, t * 10)) for x in g]
                for x, s in pos:
                    others = [math.dist((s["x"], s["y"]), (o["x"], o["y"])) for y, o in pos if y != x]
                    de = [d for d in (F.dist(x, f, t) for f in F.enemies(x) if F.alive(f, t)) if d is not None]
                    if not de or min(de) > 1500: continue
                    role = m.roles.get(x)
                    hl = x in F.healers
                    others_h = [o for y, o in pos if y != x and y in F.healers]
                    allh = [h for h in F.players(tm) if h in F.healers and h != x and F.alive(h, t)]
                    pl.append({"m": rid, "y": int(any(t < d <= t + 10 for d in dt[x])), "morale": mor.get(role, 0) or 0,
                               "gap": min(others), "aoe": aoe[tm], "s": f"{len(g)}v{sum(1 for d in de if d <= CAST_R)}",
                               "hp": s["hp"], "healer": int(hl),
                               "solo": int(hl and not any((F.dist(x, h, t) or 1e9) <= CAST_R for h in allh)),
                               "in_area": sum(1 for y, o in pos if y != x and math.dist((s["x"], s["y"]), (o["x"], o["y"])) <= IN_AREA),
                               "aoe_dmg": round(sum(v for tt, v in aoe_hits[x] if t < tt <= t + 5))})
            z = (st.get(t, {}).get(tag) or {}).get("zones") or {}
            alive = row.get("alive") or 0
            inbase = sum(1 for r, zz in z.items() if zz in ("own base", "own pit"))
            if alive >= 5: tu.append({"m": rid, "team": tag, "t": t, "share": inbase / alive})
    # turtle windows: 6+ alive in own base for 60 s straight; what each side did in the next 90 s
    win = (a["meta"].get("result") or {}).get("winning_team_id")
    tags = {t["id"]: t["tag"] for t in a["meta"]["teams"]}
    led = a["ledger"]; turtles = []
    for tag in tags.values():
        L = [r for r in tu if r["team"] == tag]; run = 0; last = -999
        for r in L:
            # not a turtle: a team back in base because it just died (resurrected at its shrine)
            fresh = any(d["team"] == tag and r["t"] - 120 <= d["t"] <= r["t"] for d in a["deaths"])
            run = run + 5 if r["share"] >= .75 and not fresh else 0
            if run >= 60 and r["t"] - last > 120:
                last = r["t"]; t1 = r["t"] + 90; foe = [x for x in tags.values() if x != tag][0]
                turtles.append({"m": rid, "team": tag, "t": r["t"], "won": int(tags.get(win) == tag),
                                "npcs_lost": sum(1 for l in led if l["edge"] == "NPC lost" and l["team"] == tag and r["t"] < l["t"] <= t1),
                                "deaths_own": sum(1 for d in a["deaths"] if d["team"] == tag and r["t"] < d["t"] <= t1),
                                "deaths_foe": sum(1 for d in a["deaths"] if d["team"] == foe and r["t"] < d["t"] <= t1)})
    # merges: a phase where a team has 7+ in one group in the enemy pit or base
    merges = [g for g in _phase_groups(rid) if g["zone"] in ("enemy pit", "enemy base") and g["size"] >= 3]
    # portal jumps (Isle of Solitude): a player moving 2,500+ in one recorded second
    jumps = []
    if a["meta"]["map"] == "Isle of Solitude":
        for x in m.PL:
            T = m.TR.get(str(x)) or {}
            for i in range(1, len(T.get("t", []))):
                if any(T["st"][j] == "d" for j in range(max(0, i - 3), i + 1)): continue      # a res, not a port
                if T["t"][i] - T["t"][i - 1] <= 15 and math.dist((T["x"][i], T["y"][i]), (T["x"][i - 1], T["y"][i - 1])) > 2500:
                    jumps.append({"m": rid, "team": tags.get(m.team(x)), "t": T["t"][i] / 10, "who": m.roles.get(x)})
    return pl, turtles, merges, jumps


def _footmen_rows(rid):
    """Per team: footmen it had, footmen lost, when the first fell, and whether the team won."""
    import events as EV
    from features import footmen
    from replaylib import Match
    a = EV.analysis(rid); m = Match.from_branch(rid)
    win = (a["meta"].get("result") or {}).get("winning_team_id"); out = []
    for tm, L in footmen(m).items():
        tag = next(t["tag"] for t in a["meta"]["teams"] if t["id"] == tm)
        lost = sorted(x for _, x in L if x is not None)
        out.append({"m": rid, "team": tag, "had": len(L), "lost": len(lost), "first": lost[0] if lost else None, "won": int(win == tm)})
    return out


def _one(rid):
    try:
        pl, tu, mg, jp = _player_rows(rid)
        return {"groups": _phase_groups(rid), "spikes": _spike_rows(rid), "players": pl, "turtles": tu, "merges": mg, "jumps": jp,
                "footmen": _footmen_rows(rid)}
    except Exception as ex:
        return {"error": f"{rid}: {ex}"}


def collect(ids):
    from multiprocessing import Pool
    allr = collections.defaultdict(list)
    with Pool(os.cpu_count() or 2) as p:
        for r in p.imap_unordered(_one, ids):
            if "error" in r: print(r["error"]); continue
            for k, v in r.items(): allr[k] += v
    return allr


def _by_match(rs):
    g = collections.defaultdict(list)
    for r in rs: g[r["m"]].append(r)
    return g


def measure(ids=None):
    ids = ids or stored()
    R = collect(ids); res = {}
    # solo monk: groups of 3+ with healers, did they lose a player (within the same numbers)
    G = [dict(g, y=g["lost"], solo=int(g["healers"] == 1)) for g in R["groups"] if g["size"] >= 3 and g["healers"] >= 1]
    d = _strat_diff(G, "solo"); ci = _boot(_by_match(G), lambda s: _strat_diff(s, "solo"))
    res["solo_monk"] = {"measure": "groups of 3+ players facing enemies in a phase: one healer against two or more, same local numbers; outcome = the group lost a player in that phase",
                        "n": len(G), "rate_one_healer": _rate([g for g in G if g["solo"]]), "rate_two_plus": _rate([g for g in G if not g["solo"]]),
                        "difference": d, "interval_90": ci, "verdict": _verdict(d, ci, +1)}
    # a monk alone: the healer's own death, no other own healer within casting range against one or more (Denning: a
    # monk alone is vulnerable because no other monk supports it); the first test above (group losses) measured the
    # wrong outcome
    H = [dict(r) for r in R["players"] if r["healer"]]
    d = _strat_diff(H, "solo"); ci = _boot(_by_match(H), lambda s: _strat_diff(s, "solo"))
    res["solo_monk"]["healer_death"] = {"measure": "healers in a fight every 5 s: no other own healer within casting range against one or more; outcome = the healer died within 10 s; same local numbers",
                                        "n": len(H), "rate_alone": _rate([r for r in H if r["solo"]]), "rate_supported": _rate([r for r in H if not r["solo"]]),
                                        "difference": d, "interval_90": ci, "verdict": _verdict(d, ci, +1)}
    res["solo_monk"]["verdict"] = res["solo_monk"]["healer_death"]["verdict"] + " (healer's own death; the group test was the wrong outcome)"
    # no healer in a group of 2+
    G2 = [dict(g, y=g["lost"], none=int(g["healers"] == 0)) for g in R["groups"] if g["size"] >= 2]
    d = _strat_diff(G2, "none"); ci = _boot(_by_match(G2), lambda s: _strat_diff(s, "none"))
    res["no_healer_group"] = {"measure": "groups of 2+ facing enemies in a phase: no healer against at least one, same local numbers; outcome = lost a player",
                              "n": len(G2), "rate_no_healer": _rate([g for g in G2 if g["none"]]), "rate_with_healer": _rate([g for g in G2 if not g["none"]]),
                              "difference": d, "interval_90": ci, "verdict": _verdict(d, ci, +1)}
    # spread: tight (nearest ally under 150) against spread, players in a fight, by enemy area-damage build
    P = R["players"]
    for k, sub in (("all", P), ("vs_area_damage", [r for r in P if r["aoe"]]), ("vs_other", [r for r in P if not r["aoe"]])):
        S = [dict(r, tight=int(r["gap"] < 150)) for r in sub]
        d = _strat_diff(S, "tight"); ci = _boot(_by_match(S), lambda s: _strat_diff(s, "tight"))
        res.setdefault("spread", {"measure": "players in a fight every 5 s: nearest ally under 150 units (tight) against farther, same local numbers; outcome = died within 10 s; split by whether the enemy has 2+ elementalists (area damage)"})[k] = {
            "n": len(S), "rate_tight": _rate([r for r in S if r["tight"]]), "rate_spread": _rate([r for r in S if not r["tight"]]),
            "difference": d, "interval_90": ci, "verdict": _verdict(d, ci, +1)}
    # area damage against spacing: area-skill damage taken in the next 5 s by allies within 322
    A = [r for r in R["players"] if r["aoe"]]
    def amean(rs): return round(statistics.mean(r["aoe_dmg"] for r in rs), 1) if rs else None
    def adiff(rs):
        by = collections.defaultdict(lambda: ([], []))
        for r in rs: by[r["s"]][0 if r["in_area"] >= 2 else 1].append(r["aoe_dmg"])
        num = den = 0
        for x, y in by.values():
            if len(x) >= 3 and len(y) >= 3: w = len(x) + len(y); num += w * (statistics.mean(x) - statistics.mean(y)); den += w
        return round(num / den, 1) if den else None
    d = adiff(A); ci = _boot(_by_match(A), adiff)
    res["area_damage_spacing"] = {"measure": "players in a fight against a team with 2+ elementalists, every 5 s: area-skill damage taken in the next 5 s with 2+ allies within 322 against 0 or 1; same local numbers",
                                  "n": len(A), "mean_2plus_allies_close": amean([r for r in A if r["in_area"] >= 2]),
                                  "mean_0_or_1": amean([r for r in A if r["in_area"] < 2]),
                                  "by_allies_in_area": {k: amean([r for r in A if min(r["in_area"], 3) == k]) for k in range(4)},
                                  "difference": d, "interval_90": ci, "verdict": _verdict(d, ci, +1), "source": SOURCE.get("spread")}
    # spikes
    SP = R["spikes"]
    for name, flag, desc in (("strip_on_spike", "strip", "an enchantment removal by the spiking team finished on the target from 2 s before the first hit to 1 s after"),
                             ("armor_on_spike", "cracked", "the target had Cracked Armor at the first hit"),
                             ("hexed_spikers", "hexed", "at least one spiker carried a hex at the first hit")):
        d = _strat_diff(SP, flag); ci = _boot(_by_match(SP), lambda s, f=flag: _strat_diff(s, f))
        res[name] = {"measure": f"spikes (400+ in 3 s): {desc}; outcome = the target died within 8 s; compared within the number of spikers",
                     "n": len(SP), "cases": sum(r[flag] for r in SP), "rate_with": _rate([r for r in SP if r[flag]]), "rate_without": _rate([r for r in SP if not r[flag]]),
                     "difference": d, "interval_90": ci, "verdict": _verdict(d, ci, -1 if name == "hexed_spikers" else +1)}
    # weapon sets on spikes: spikers mostly on fast-cast (40/40) caster sets against mostly not; target on a shield set
    for name, flag, desc, exp in (("spike_caster_sets", "caster_sets", "most spikers held a fast-cast caster set with no shield (40/40)", +1),
                                  ("spike_target_shield", "target_shield", "the target held a shield set at the first hit", -1),
                                  ("interrupted_spikers", "interrupted", "the spiking team was interrupted at least once in the 5 s before the first hit", -1)):
        d = _strat_diff(SP, flag); ci = _boot(_by_match(SP), lambda s, f=flag: _strat_diff(s, f))
        res[name] = {"measure": f"spikes (400+ in 3 s): {desc}; outcome = the target died within 8 s; compared within the number of spikers",
                     "n": len(SP), "cases": sum(r[flag] for r in SP), "rate_with": _rate([r for r in SP if r[flag]]),
                     "rate_without": _rate([r for r in SP if not r[flag]]), "difference": d, "interval_90": ci,
                     "verdict": _verdict(d, ci, exp), "source": "OG comms [OG v hdm]: 'they keep Complicating my Deep Wound'" if name == "interrupted_spikers"
                     else "OG comms [OG v cope J]: against mirrors, spike in 40/40 sets to get as many off as we can"}
    # spike rate: spikes per minute of match by the share of a team's spikes thrown on caster sets
    byt = collections.defaultdict(list)
    for r in SP: byt[(r["m"], r["team"])].append(r)
    res["spike_caster_sets"]["teams_mostly_caster_sets_spikes"] = sum(1 for v in byt.values() if sum(x["caster_sets"] for x in v) > len(v) / 2)
    # low morale: death penalty 15+ against none, players in a fight, same local numbers
    L = [dict(r, low=int(r["morale"] <= -15)) for r in P if r["morale"] <= 0]
    d = _strat_diff(L, "low"); ci = _boot(_by_match(L), lambda s: _strat_diff(s, "low"))
    res["low_morale"] = {"measure": "players in a fight every 5 s: death penalty 15% or more against none; outcome = died within 10 s; same local numbers",
                         "n": len(L), "rate_dp15": _rate([r for r in L if r["low"]]), "rate_no_dp": _rate([r for r in L if not r["low"]]),
                         "difference": d, "interval_90": ci, "verdict": _verdict(d, ci, +1)}
    # merge: pit pushes with 7+ against fewer: kills in the phase per 30 s and losses
    M = [dict(g, y=int(g["kills"] > 0), full=int(g["size"] >= 7), s="all") for g in R["merges"]]
    d = _strat_diff(M, "full"); ci = _boot(_by_match(M), lambda s: _strat_diff(s, "full"))
    dl = _strat_diff([dict(r, y=r["lost"]) for r in M], "full")
    res["merge"] = {"measure": "groups in the enemy pit or base: 7+ players against 3 to 6; outcome = killed a player in that phase (and, separately, lost one)",
                    "n": len(M), "kill_rate_full": _rate([r for r in M if r["full"]]), "kill_rate_partial": _rate([r for r in M if not r["full"]]),
                    "difference": d, "interval_90": ci, "loss_rate_difference": dl, "verdict": _verdict(d, ci, +1)}
    # turtles
    T = R["turtles"]
    res["turtle"] = {"measure": "a team with 75%+ of its live players in its own base or pit for 60 s straight (5+ alive), with no deaths in the 2 minutes before (so not just resurrected); what the next 90 s held and who won",
                     "n": len(T), "turtling_team_won": _rate([dict(t, y=t["won"]) for t in T]),
                     "after_90s": {"npcs_lost_by_turtle": round(statistics.mean([t["npcs_lost"] for t in T]), 2) if T else None,
                                   "deaths_turtle": round(statistics.mean([t["deaths_own"] for t in T]), 2) if T else None,
                                   "deaths_other": round(statistics.mean([t["deaths_foe"] for t in T]), 2) if T else None},
                     "cases": [f"{t['m'][:8]} {t['team']} {int(t['t'] // 60)}:{int(t['t'] % 60):02d}" for t in T][:30],
                     "verdict": "descriptive (the win-model candidate turtle_diff tests it on unseen matches)"}
    FM = R["footmen"]
    lost_more = [r for r in FM if r["lost"] > 0]
    res["footmen"] = {"measure": "footmen (base NPCs) per team per match: how many it had, lost, and whether it won",
                      "teams": len(FM), "had_mean": round(statistics.mean(r["had"] for r in FM), 2) if FM else None,
                      "teams_losing_any": len(lost_more), "won_when_losing_any": _rate([dict(r, y=r["won"]) for r in lost_more]),
                      "won_when_losing_none": _rate([dict(r, y=r["won"]) for r in FM if r["lost"] == 0]),
                      "verdict": "descriptive (the win-model candidate footmen_diff and values.py test it)", "source": "OG comms [ohno v NwAy], [ohno v Fun]"}
    J = R["jumps"]
    res["portal"] = {"measure": "Isle of Solitude: a player moving 2,500+ units in one recorded second (a portal jump)",
                     "n": len(J), "by_team": dict(collections.Counter(f"{j['m'][:8]} {j['team']}" for j in J)),
                     "verdict": "descriptive (too few Solitude matches to test)"}
    for k in res: res[k]["source"] = SOURCE.get(k)
    out = {"about": "Variables suggested by commentary and comms, measured in every stored replay (comms_vars.py). "
                    "Intervals: 90% from resampling whole matches. Verdict: supported / contradicted when the interval "
                    "excludes zero, else unclear.", "matches": len(ids), "variables": res}
    json.dump(out, open(OUT, "w"), indent=1)
    return out


if __name__ == "__main__":
    r = measure()
    for k, v in r["variables"].items():
        print(k, json.dumps({kk: vv for kk, vv in v.items() if kk not in ("measure", "source", "cases")})[:400])
