"""Judgement and the edge ledger.

Judgement: each rule turns a principle from knowledge/tactics.md into a check on episodes and returns findings:
  {"rule", "principle" (tactics section), "team", "t", "verdict", "evidence", "question"}
verdict is one of: good, on time, late, missed, wrong role, risky, mistake, great enemy play, note. Thresholds are first guesses, to be calibrated
against Denning's verdicts (data/review_labels.json) and, after the bulk pull, against benchmarks.

Edge ledger: every change in an edge (a death and its death penalty, a boost, a pit NPC, Lord damage) with the episode
that caused it, so each episode's cost or gain is counted and the match's biggest swings stand out.

Usage:  python3 rules.py <report id> [findings] [ledger]"""
import collections, sys
from replaylib import Match
from state import GameState, d
import episodes as E
import fights as F

T = dict(split_on_time=15, split_late=60, collapse_within=30, help_within=15, pp_min=20, pp_pressure=1.3,
         isolated=2000, monk_far=5000, near_boost=90)
FRONT = {"Hammer", "Hammer A", "Hammer B", "AoB Derv", "Warrior", "Dervish", "Assassin"}


def _ahead(st, tag, t):
    """Clearly ahead on the visible edges: more pit NPCs alive and better morale (boosts minus death penalty)."""
    s = st.at(t); other = next(x for x in st.m.tag.values() if x != tag)
    npcs = lambda x: sum(int(c) for c in s[x]["pit_npcs"].replace("K", " ").replace("A", " ").replace("B", " ").split())
    mor = lambda x: sum(s[x]["morale"].values())
    return npcs(tag) - npcs(other) >= 2 and mor(tag) - mor(other) >= 30


def findings(st, ep=None):
    m = st.m
    ep = ep or {"splits": E.splits(st), "flag_runs": E.flag_runs(st), "stand": E.stand_ledger(st),
                "deaths": F.deaths(st), "windows": F.windows(st)}
    out = []
    add = lambda **k: out.append(k)

    # ---- splits (tactics: 3. Splits)
    for s in ep["splits"]:
        if s["kind"] == "full team collapse":
            foe = next(t for t in m.tag.values() if t != s["team"])
            add(rule="full team collapse", principle="3. Splits (Denning: full team collapse)", team=foe, t=s["start"], verdict="note",
                evidence=f"{foe} turned {len(s['defenders'])} players on {s['team']} {'+'.join(s['members'])}; kills {s['deaths']}")
            continue
        if s["kind"] != "split" or s["entered_base"] is None: continue
        foe = next(t for t in m.tag.values() if t != s["team"])
        ref = s["entered_base"]
        first = s["defenders"][0] if s["defenders"] else None
        lat = (first["first"] - ref) if first else None
        v = "missed" if lat is None or lat > T["split_late"] else ("late" if lat > T["split_on_time"] else "on time")
        lost = [k for k in s["npc_kills"] if not k["defenders_present"]]
        add(rule="split answered", principle="3. Splits: defending", team=foe, t=ref, verdict=v,
            evidence=f"{s['team']} {'+'.join(s['members'])} entered the base at {m.f(ref*10)}; first answer "
                     + (f"{first['role']} after {lat} s ({first['came']})" if first else "none")
                     + (f"; NPCs lost with nobody there: {', '.join(k['npc'] for k in lost)}" if lost else ""),
            question="Was the answer late, and who should have gone?" if v != "on time" else None)
        if s["members"] == ["Ranger"]:
            roles = [x["role"] for x in s["defenders"]]
            t0 = first["first"] if first else None
            mesa = any(x["role"] == "Mes/A" for x in s["defenders"])
            coll = [x for x in s["defenders"] if x["role"] in FRONT and t0 is not None and x["first"] - t0 <= T["collapse_within"]]
            only8 = roles and set(roles) <= {"8 Monk"}
            pit_dead = st.at(ref)[foe]["pit_npcs"] == "K0 A0 B0"
            # Denning: answering with the 8 monk keeps all damage at main; a risk that may pay off with kills (data
            # needed). Once the pit is dead, the 8 monk staying in base is right: the Mes/A can't hold a ranger alone.
            v2 = ("good" if mesa and coll else "note" if only8 and pit_dead
                  else "risky" if only8 else ("wrong role" if roles else "missed"))
            add(rule="lone ranger: Mes/A plus frontline collapse", principle="3. Splits: Denning on lone ranger splits",
                team=foe, t=ref, verdict=v2,
                evidence=f"answered by {', '.join(roles) or 'nobody'}; frontline collapse within {T['collapse_within']} s: "
                         + (", ".join(x['role'] for x in coll) or "none"))
        # the split's own value: what it drew and what it took
        drawn = sum(1 for x in s["defenders"] if x["came"] != "already in base")
        took = len(s["npc_kills"])
        if s["end"] - s["start"] >= 45:
            v3 = "good" if took >= 2 or drawn > len(s["members"]) else ("note" if took or drawn else "mistake")
            add(rule="split value", principle="3. Splits: a split is judged by what it forces and what it takes",
                team=s["team"], t=s["start"], verdict=v3,
                evidence=f"{'+'.join(s['members'])} for {s['end']-s['start']} s: took {took} NPCs, drew {drawn} defenders from elsewhere; "
                         f"main numbers meanwhile {s['main_numbers']}; splitter deaths {s['deaths']}")

    # ---- flag (tactics: 5. The flag game)
    for r in ep["flag_runs"]:
        if r["runner"] == "8 Monk":
            add(rule="running on the 8 monk", principle="5. Running costs (Denning)", team=r["team"], t=r["start"], verdict="note",
                evidence=f"8 monk carried {r['secs']} s -> {r['outcome']}", question="Were 2 enemy damage dead, or was it desperate?")
        if r["pushers"] and r["first_push"] is not None:
            helped = [h for h in r["helpers"] if h["latency"] <= T["help_within"]]
            # Denning: one damage pushing is likely fine, depending on the pusher and the runner; 2+ pushers need help
            dmg_pushers = [k for k, v in r["pushers"].items() if v["actions"].get("damage", 0) or v["actions"].get("knockdown", 0)]
            if len(dmg_pushers) >= 2 and (r["outcome"] in ("dropped", "died") or r["min_hp"] is not None and r["min_hp"] < 40):
                add(rule="pushed flagger supported", principle="5. Pushing the flagger (Denning)", team=r["team"], t=r["first_push"],
                    verdict="good" if helped else "late",
                    evidence=f"{r['runner']} pushed by {', '.join(r['pushers'])} from {m.f(r['first_push']*10)}; "
                             f"help within {T['help_within']} s: {', '.join(h['role'] for h in helped) or 'none'}; outcome {r['outcome']}, min HP {r['min_hp']}%")
        if r["outcome"] == "dropped" and not r["pushers"] and (r["min_hp"] or 0) >= 70 and not r["double"]:
            add(rule="flag dropped without reason", principle="5. Boosts (Bounty)", team=r["team"], t=r["end"], verdict="note",
                evidence=f"{r['runner']} dropped at {m.f(r['end']*10)} unpushed at {r['min_hp']}%+ HP", question="Intended (to a better runner) or a mistake?")
    for h in ep["stand"]:
        if h["short_of_boost"] and h["to"] < st.end - 1:
            # Denning: losing the stand that close to a boost is normal; it points at the capping team being down on
            # flags (an on-time flag, or a team up on flags, caps earlier)
            capper = next(t for t in m.tag.values() if t != h["team"])
            add(rule="capped just before a boost", principle="5. Boosts (Denning)", team=capper, t=h["to"], verdict="late",
                evidence=f"{h['team']} held {h['held']} s; {capper} capped {h['short_of_boost']} s before a boost, so was down on flags",
                question=None)

    # ---- numbers windows (tactics: 5. The power play)
    for w in ep["windows"]:
        if w["secs"] < T["pp_min"]: continue
        conv = bool(w["kills"]) or w["pressure_vs_avg"] >= T["pp_pressure"] and (w["pushed_toward_enemy_pit"] or 0) > 500
        # Denning: a team that is already winning doesn't need to force it; holding is fine
        ahead = _ahead(st, w["team"], w["start"])
        add(rule="power play converted", principle="5. The power play (Denning, Bounty); 4. a winning team needn't risk",
            team=w["team"], t=w["start"],
            verdict="good" if w["kills"] or w.get("npcs_taken") else ("note" if conv or ahead else "missed"),
            evidence=f"{w['numbers']} for {w['secs']} s (enemy short: {w['enemy_short_because']}); pressure x{w['pressure_vs_avg']}, "
                     f"kills {w['kills']}, NPCs taken {w.get('npcs_taken')}, losses {w['losses']}, ground {w['pushed_toward_enemy_pit']}",
            question=None if w["kills"] or w.get("npcs_taken") or ahead else "Push harder, or was holding right?")

    # ---- deaths (tactics: 6, 8, 9, 11)
    for x in ep["deaths"]:
        why = []
        if x["isolated"]: why.append("isolated from the main group")
        far = {k: v for k, v in x["monk_distance"].items() if v > T["monk_far"]}
        # Denning: the 8 monk staying in base once its pit is dead (defending the Lord) is right, not a monk out of place
        if "8 Monk" in far and st.at(x["t"])[x["team"]]["pit_npcs"] == "K0 A0 B0": far.pop("8 Monk")
        if far: why.append(f"monks far away: {far}")
        if not x["monk_casts_on_victim"] and not x["victim"].endswith("Monk"): why.append("no prot or heal on the victim")
        if len(x["knockdowns"]) >= 2: why.append(f"{len(x['knockdowns'])} knockdowns")
        if x["interrupts_on_monks"]: why.append(f"{len(x['interrupts_on_monks'])} interrupts on its monks")
        if x["peel_hits"] == 0: why.append("no peel")
        if x["after_time"]: why.append("after time")
        cost = x["then"]
        a = x.get("assessment", {})
        great = a.get("cause", "").startswith("coordinated")
        why = [f"cause: {a.get('cause')}"] + why + [f"acceptable mistakes: {'; '.join(a['mistakes'])}"] * bool(a.get("mistakes")) \
              + list(a.get("notes", []))
        add(rule="death", principle="6. Kills and timing; 8 to 11 micro", team=x["team"], t=x["t"],
            verdict="great enemy play" if great else ("mistake" if (x["isolated"] or far) else "note"),
            evidence=f"{x['victim']} at {x['zone']} ({x['numbers'][0]}v{x['numbers'][1]}), burst {x['burst_max_2s']}/2 s by {list(x['damage_by'])[:3]}; "
                     + "; ".join(why) + f"; then {cost}")
    return sorted(out, key=lambda f: f["t"])


def ledger(st, ep=None):
    """Every edge change with its likely cause, plus each team's running totals."""
    m = st.m
    ep = ep or {"splits": E.splits(st), "windows": F.windows(st), "flag_runs": E.flag_runs(st)}
    rows = []
    for a in m.PL:
        for t in st.death_times.get(a, []):
            if t >= st.end - 1: continue
            cause = next((f"numbers window {m.f(w['start']*10)}" for w in ep["windows"] if w["start"] <= t <= w["end"] + 5), None)
            rows.append({"t": round(t), "team": m.tag[m.team(a)], "edge": "death", "what": m.roles[a],
                         "down_s": round(st.next_res(t) - t), "cause": cause or "fight"})
    for h in E.stand_ledger(st):
        for k in range(h["boosts"]):
            rows.append({"t": h["from"] + 120 * (k + 1), "team": h["team"], "edge": "boost", "what": "+morale", "cause": f"stand held from {m.f(h['from']*10)}"})
    for a, t in st.npc_dead.items():
        v = st.geo.npcs.get(a)
        if not v or t >= st.end - 1 or v["kind"] == "guild_lord": continue
        cause = next((f"{s['team']} split {'+'.join(s['members'])}" for s in ep["splits"] if s["start"] <= t <= s["end"] + 2
                      and m.tag[3 - v["team"]] == s["team"]), "push")
        rows.append({"t": round(t), "team": m.tag[v["team"]], "edge": "NPC lost", "what": v["kind"] + ("" if v.get("pit") else " (outside)"), "cause": cause})
    lord = collections.defaultdict(float)
    for r in m.o["ev"]:
        if r[1] == "dm" and isinstance(r[3], int) and r[3] < len(m.A) and m.A[r[3]].get("npc") == "guild_lord" and r[2] in m.PL:
            lord[(int(r[0] // 600), m.tag[m.team(r[2])])] += r[5] or 0
    for (mi, tag), v in sorted(lord.items()):
        rows.append({"t": mi * 60, "team": tag, "edge": "Lord damage dealt", "what": round(v), "cause": "minute total"})
    return sorted(rows, key=lambda r: r["t"])


def show(st, what):
    m = st.m
    if "findings" in what:
        print("== findings")
        for f in findings(st):
            print(f"{m.f(f['t']*10):>5} {f['team']:5} {f['verdict']:10} {f['rule']}: {f['evidence']}")
    if "ledger" in what:
        print("== edge ledger")
        for r in ledger(st):
            print(f"{m.f(r['t']*10):>5} {r['team']:5} {r['edge']:17} {r['what']} ({r['cause']}" + (f", down {r['down_s']} s" if 'down_s' in r else "") + ")")


if __name__ == "__main__":
    st = GameState(Match.from_branch(sys.argv[1]))
    show(st, sys.argv[2:] or ("findings", "ledger"))
