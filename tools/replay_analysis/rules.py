"""Judgement and the edge ledger.

Judgement: each rule turns a principle from knowledge/tactics.md into a check on episodes and returns findings:
  {"rule", "principle" (tactics line ids, e.g. "S18" or "F6 F7"), "team", "t", "verdict", "evidence", "question"}
verdict is one of: good, on time, late, missed, wrong role, risky, mistake, great enemy play, note. Thresholds are first guesses, to be calibrated
against Denning's verdicts (data/review_labels.json) and, after the bulk pull, against benchmarks.

Edge ledger: every change in an edge (a death and its death penalty, a boost, a pit NPC, Lord damage) with the episode
that caused it (a death's own cause and its fight), so each episode's cost or gain is counted and the match's biggest
swings stand out.

Usage:  python3 rules.py <report id> [findings] [ledger]"""
import collections, sys
from replaylib import Match
from state import GameState, d
from scoreboard import Scoreboard
import episodes as E
import fights as F

T = dict(split_on_time=15, split_late=60, collapse_within=30, help_within=15, pp_min=20, pp_pressure=1.3,
         isolated=2000, monk_far=5000, near_boost=90)
FRONT = {"Hammer", "Hammer A", "Hammer B", "AoB Derv", "Warrior", "Dervish", "Assassin"}


# death cause -> verdict and tactics ids (Denning's rulings in data/review_labels.json)
DEATH_VERDICTS = [
    ("coordinated enemy pressure", "great enemy play", "M1"),
    ("spike", "note", "X3"),
    ("backline down", "note", "K11"),
    ("outnumbered away from pit while up on flags", "mistake", "F6 F7 D8"),
    ("fight during a forced flag run", "note", "F5 F11"),
    ("positioning", "mistake", "M12 O3"),
    ("lack of support", "mistake", "M14"),
    ("out-pressured despite support", "note", "M1 X7"),
    ("out-damaged despite prots", "note", "X3 X7"),
    ("unclear", "note", "M1"),
]


def _ahead(st, tag, t):
    """Clearly ahead on the visible edges: more pit NPCs alive and better morale (boosts minus death penalty)."""
    s = st.at(t); other = next(x for x in st.m.tag.values() if x != tag)
    npcs = lambda x: sum(int(c) for c in s[x]["pit_npcs"].replace("K", " ").replace("A", " ").replace("B", " ").split())
    mor = lambda x: sum(s[x]["morale"].values())
    return npcs(tag) - npcs(other) >= 2 and mor(tag) - mor(other) >= 30


def _parked_or_threatened(st, r):
    """A drop that isn't a fumble: the flag parked at the own spawn (held back on purpose), a drop before the match
    clock starts, or a drop with enemies already within 1,500 (dropping to fight)."""
    m = st.m
    tm = next(k for k, v in m.tag.items() if v == r["team"])
    a = next((x for x in st.players[tm] if m.roles[x] == r["runner"]), None)
    if a is None or r["end"] <= 5: return True
    p = st.pos(a, r["end"])[0]
    if d(p, st.geo.spawn[tm]) < 2500: return True
    return any(st.alive(e, r["end"]) and d(st.pos(e, r["end"])[0], p) < 1500 for e in st.players[3 - tm])


def findings(st, ep=None):
    m = st.m
    if ep is None:
        sb = Scoreboard(st); ds = F.deaths(st, sb)
        ep = {"splits": E.splits(st), "flag_runs": E.flag_runs(st), "stand": E.stand_ledger(st), "deaths": ds,
              "windows": F.windows(st), "fights": F.engagements(st, sb, ds)}
    out = []
    add = lambda **k: out.append(k)

    # ---- splits (tactics: 3. Splits)
    for s in ep["splits"]:
        if s["kind"] == "full team collapse":
            foe = next(t for t in m.tag.values() if t != s["team"])
            add(rule="full team collapse", principle="S5", team=foe, t=s["start"], verdict="note",
                evidence=f"{foe} turned {len(s['defenders'])} players on {s['team']} {'+'.join(s['members'])}; kills {s['deaths']}")
            continue
        if s["kind"] != "split" or s["entered_base"] is None: continue
        foe = next(t for t in m.tag.values() if t != s["team"])
        ref = s["entered_base"]
        first = s["defenders"][0] if s["defenders"] else None
        lat = (first["first"] - ref) if first else None
        v = "missed" if lat is None or lat > T["split_late"] else ("late" if lat > T["split_on_time"] else "on time")
        lost = [k for k in s["npc_kills"] if not k["defenders_present"]]
        add(rule="split answered", principle="S18", team=foe, t=ref, verdict=v,
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
            add(rule="lone ranger: Mes/A plus frontline collapse", principle="S19 S20 S21",
                team=foe, t=ref, verdict=v2,
                evidence=f"answered by {', '.join(roles) or 'nobody'}; frontline collapse within {T['collapse_within']} s: "
                         + (", ".join(x['role'] for x in coll) or "none"))
        # the split's own value: what it drew and what it took
        drawn = sum(1 for x in s["defenders"] if x["came"] != "already in base")
        took = len(s["npc_kills"])
        if s["end"] - s["start"] >= 45:
            v3 = "good" if took >= 2 or drawn > len(s["members"]) else ("note" if took or drawn else "mistake")
            add(rule="split value", principle="S10",
                team=s["team"], t=s["start"], verdict=v3,
                evidence=f"{'+'.join(s['members'])} for {s['end']-s['start']} s: took {took} NPCs, drew {drawn} defenders from elsewhere; "
                         f"main numbers meanwhile {s['main_numbers']}; splitter deaths {s['deaths']}")

    # ---- flag (tactics: 5. The flag game)
    for r in ep["flag_runs"]:
        if r["runner"] == "8 Monk":
            add(rule="running on the 8 monk", principle="F19", team=r["team"], t=r["start"], verdict="note",
                evidence=f"8 monk carried {r['secs']} s -> {r['outcome']}", question="Were 2 enemy damage dead, or was it desperate?")
        if r["pushers"] and r["first_push"] is not None:
            helped = [h for h in r["helpers"] if h["latency"] <= T["help_within"]]
            # Denning: one damage pushing is likely fine, depending on the pusher and the runner; 2+ pushers need help
            dmg_pushers = [k for k, v in r["pushers"].items() if v["actions"].get("damage", 0) or v["actions"].get("knockdown", 0)]
            if len(dmg_pushers) >= 2 and (r["outcome"] in ("dropped", "died") or r["min_hp"] is not None and r["min_hp"] < 40):
                add(rule="pushed flagger supported", principle="F20 F21", team=r["team"], t=r["first_push"],
                    verdict="good" if helped else "late",
                    evidence=f"{r['runner']} pushed by {', '.join(r['pushers'])} from {m.f(r['first_push']*10)}; "
                             f"help within {T['help_within']} s: {', '.join(h['role'] for h in helped) or 'none'}; outcome {r['outcome']}, min HP {r['min_hp']}%")
        if r["outcome"] == "dropped" and not r["pushers"] and (r["min_hp"] or 0) >= 70 and not r["double"] \
                and not _parked_or_threatened(st, r):
            add(rule="flag dropped without reason", principle="F27", team=r["team"], t=r["end"], verdict="note",
                evidence=f"{r['runner']} dropped at {m.f(r['end']*10)} unpushed at {r['min_hp']}%+ HP", question="Intended (to a better runner) or a mistake?")
    for h in ep["stand"]:
        if h["short_of_boost"] and h["to"] < st.end - 1:
            # Denning: losing the stand that close to a boost is normal; it points at the capping team being down on
            # flags (an on-time flag, or a team up on flags, caps earlier)
            capper = next(t for t in m.tag.values() if t != h["team"])
            add(rule="capped just before a boost", principle="F26", team=capper, t=h["to"], verdict="late",
                evidence=f"{h['team']} held {h['held']} s; {capper} capped {h['short_of_boost']} s before a boost, so was down on flags",
                question=None)

    # ---- numbers windows (tactics: 5. The power play)
    for w in ep["windows"]:
        if w["secs"] < T["pp_min"]: continue
        conv = bool(w["kills"]) or w["pressure_vs_avg"] >= T["pp_pressure"] and (w["pushed_toward_enemy_pit"] or 0) > 500
        # Denning: a team that is already winning doesn't need to force it; holding is fine
        ahead = _ahead(st, w["team"], w["start"])
        add(rule="power play converted", principle="F23 F24 W8",
            team=w["team"], t=w["start"],
            verdict="good" if w["kills"] or w.get("npcs_taken") else ("note" if conv or ahead else "missed"),
            evidence=f"{w['numbers']} for {w['secs']} s (enemy short: {w['enemy_short_because']}); pressure x{w['pressure_vs_avg']}, "
                     f"kills {w['kills']}, NPCs taken {w.get('npcs_taken')}, losses {w['losses']}, ground {w['pushed_toward_enemy_pit']}",
            question=None if w["kills"] or w.get("npcs_taken") or ahead else "Push harder, or was holding right?")

    # ---- deaths: the verdict follows the death's cause (fights.assess); evidence keeps the details
    for x in ep["deaths"]:
        a = x.get("assessment", {}); cause = a.get("cause", "unclear")
        verdict, pr = next(((v, p) for k, v, p in DEATH_VERDICTS if cause.startswith(k)), ("note", "M1"))
        if verdict == "note" and any(mm.startswith("basic") for mm in a.get("mistakes", [])): verdict = "mistake"
        why = [f"cause: {cause}"]
        if x["after_time"]: why.append("after time")
        if a.get("mistakes"): why.append("mistakes: " + "; ".join(a["mistakes"]))
        why += list(a.get("notes", []))
        c = x["then"]
        add(rule="death", principle=pr, team=x["team"], t=x["t"], verdict=verdict,
            evidence=f"{x['victim']} at {x['zone']} ({x['numbers'][0]}v{x['numbers'][1]}), burst {x['burst_max_2s']}/2 s by "
                     f"{list(x['damage_by'])[:3]}; " + "; ".join(why)
                     + f"; until back ({c['window_s']} s): NPCs lost {c['npcs_lost'][x['team']]}, caps {c['caps']}, edge {c['edge_change']:+}")

    # ---- fights: what put the losing side there and whether the winner converted (W6, W7, K8)
    for g in ep.get("fights", []):
        sit = " ".join(g["situation"]); c = g["consequence"]; loser, winner = g["team"], g["opponent_won_fight"]
        if "fought away from pit while up on flags" in sit:
            add(rule="fight while up on flags", principle="F6 F7 D8", team=loser, t=g["start"], verdict="mistake",
                evidence=f"{loser} lost {g['losses'].get(loser)} on its {g['where']} while up on flags; " + sit)
        if "running while down on flags" in sit and "outnumbered" in sit:
            add(rule="forced run outnumbered", principle="F5 F11 F12", team=loser, t=g["start"], verdict="note",
                evidence=f"{loser} had to run, down on flags, and lost the fight outnumbered: " + sit,
                question="Should an extra damage have gone back with the runner, or should it not have run (F18)?")
        if "pushed into the enemy pit" in sit and not sit.endswith("(K0 A0 B0 alive)") and "K2" in sit:
            add(rule="pushed into an intact pit", principle="P8", team=loser, t=g["start"], verdict="risky", evidence=sit)
        if "first death after time" in sit:
            add(rule="died after time", principle="K1 P2", team=loser, t=g["trigger"]["t"], verdict="mistake",
                evidence=f"{g['trigger']['victim']} died just after the res ({g['trigger']['cause']})")
        if "DP stacked against a spike" in sit:
            add(rule="DP stacking against a spike", principle="K4 D6", team=loser, t=g["start"], verdict="note", evidence=sit)
        if g["wipe"]:
            w_tm = next(k for k, v in m.tag.items() if v == winner)
            ahead = _ahead(st, winner, g["end"])
            add(rule="wipe converted", principle="K8 W8 W9 D5", team=winner, t=g["end"],
                verdict="good" if g["converted"] else ("note" if ahead else "missed"),
                evidence=f"{winner} wiped {loser} ({g['losses'].get(loser)} deaths); until they were back: NPCs taken "
                         f"{c['npcs_lost'][loser]}, Lord damage {c['lord_damage'][winner]}, caps {c['caps']}, boosts {c['boosts']}",
                question=None if g["converted"] or ahead else "What should the wipe have been turned into?")
    return sorted(out, key=lambda f: f["t"])


def ledger(st, ep=None):
    """Every edge change with its likely cause, plus each team's running totals."""
    m = st.m
    if ep is None:
        sb = Scoreboard(st); ds = F.deaths(st, sb)
        ep = {"splits": E.splits(st), "deaths": ds, "fights": F.engagements(st, sb, ds)}
    rows = []
    fight_of = {}
    for g in ep.get("fights", []):
        for t, tag, victim, _ in g["deaths"]: fight_of[(t, tag, victim)] = f"fight {m.f(g['start'] * 10)}" + (" (wipe)" if g["wipe"] else "")
    for x in ep["deaths"]:
        rows.append({"t": x["t"], "team": x["team"], "edge": "death", "what": x["victim"], "down_s": x["down_for"],
                     "cause": x["assessment"]["cause"] + (f", {fight_of[(x['t'], x['team'], x['victim'])]}" if (x['t'], x['team'], x['victim']) in fight_of else "")})
    for h in E.stand_ledger(st):
        for k in range(h["boosts"]):
            rows.append({"t": h["from"] + 120 * (k + 1), "team": h["team"], "edge": "boost", "what": "+morale", "cause": f"stand held from {m.f(h['from']*10)}"})
    for a, t in st.npc_dead.items():
        v = st.geo.npcs.get(a)
        if not v or t >= st.end - 1 or v["kind"] == "guild_lord": continue
        cause = next((f"{s['team']} split {'+'.join(s['members'])}" for s in ep["splits"] if s["start"] <= t <= s["end"] + 2
                      and m.tag[3 - v["team"]] == s["team"]), None)
        cause = cause or next((f"converted from the fight at {m.f(g['start'] * 10)}" + (" (wipe)" if g["wipe"] else "")
                               for g in ep.get("fights", []) if g["team"] == m.tag[v["team"]]
                               and g["start"] <= t <= g["start"] + g["consequence"]["window_s"]), "push")
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
