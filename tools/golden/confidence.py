#!/usr/bin/env python3
"""The engine's confidence that a situation is a decision (R-492): how steady its reading is.

Every situation the engine reads rests on draft numbers (how close players must stand to be in one fight, how long a
player must be there to count, how long numbers must hold). A classic decision is read the same way wherever those
numbers sit; a weak one appears or vanishes when one of them moves a little. So each game is read again with every
number of the reading, one at a time, a quarter lower and higher and at half and double (common.py GVG_TRY; nothing in
the engine is changed), and each play is looked for in every one of those readings:

  same     a play of the same kind, team, side, call, sizes and numbers starts within SAME_S of it
  other    the kind of play is still read there for that team, but as something else (other numbers, another call)
  gone     nothing of that kind is read there

The confidence of a situation is told in three bands, fitted on 2026-11-17 to his grades of the five games graded his new way (HC v Team, Men v Crew,
옷옷옷옷 v RACK, Men v RACK, Men v hold: 228 graded situations; R-492, R-497, R-515). Two things can happen to a situation when a number moves: the engine
stops reading it at all (every play of it is gone), or it still reads it with other details (other players counted, another call). What his grades showed:
a situation that never disappears and whose details hold at a quarter is Classic two times in three (84 of 126); one that disappears at a quarter's move
is almost never Classic (3 of 27) and holds the largest share of Weak and No decision (10 of 27).

  high     still read at every move, and its details hold at a quarter either way
  medium   still read at a quarter either way, but its details move there, or it disappears at half or double
  low      a quarter's move of one number makes it disappear

His grades by band on those five games (Classic, Visible, Weak, No decision): high 84, 35, 2, 5; medium 23, 34, 8, 10; low 3, 14, 4, 6. Taking high as
Classic, medium as Visible and low as Weak or No decision, the band is his grade on 128 of 228 (56%), and far off (high on a Weak or No decision, low on a
Classic) on 10; the bands before (high: nothing moves at all; low: two numbers move anything at a quarter) were his grade on 123 and far off on 16. Tried on
the same grades and not kept, because each game banded from the other four did no better: the length of the situation, and a table by kind of play. What
steadiness cannot do is tell Visible from Weak or No decision (his four reasons for those, R-509, are about what is at stake: too brief, too small, no real
fight, an unclear edge), and nothing has been fitted for that yet (never guessed). Fit again when more games are graded: `confidence.py reband <file>`
writes the bands again from the stored readings without running the engine.

A situation the engine itself tells as context (`clear` false, R-488) has no band: it is "none".

Usage:  python3 tools/golden/confidence.py run <out.json> <report id> [<report id> ...] [--jobs 2]
        python3 tools/golden/confidence.py show <out.json> [<report id>]
        python3 tools/golden/confidence.py reband <out.json>
A reading tool: it is in no cache key. `review.py export --confidence <out.json>` puts the bands on the page."""
import collections, concurrent.futures, json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ENGINE = os.path.join(REPO, "tools", "replay_analysis")
QUARTER, FAR = (0.75, 1.25), (0.5, 2.0)
SAME_S = 6            # a play starting within this many seconds of the one looked for is the same play (as in review.py compare)
cl = lambda t: f"{int(t) // 60}:{int(t) % 60:02d}"

# What each number of the reading is, in a player's words: said when a move of it changes a situation. A number not
# listed here is said by its name (and should then be added).
WORDS = {
    "JOIN_S": "how long a player must be in a fight before he counts in it",
    "TURN_S": "how long a team must be making for a split before its collapse is told",
    "TURN_CLOSE": "how fast a player must close on a split to be making for it",
    "JOIN_LOOK_S": "how far ahead the engine looks for a player joining a fight",
    "FIGHT_LINK": "how close players must stand to be in the same fight",
    "FIGHT_HOLD": "how far a player may drift and still be in the fight he was in",
    "FIGHT_HOLD_S": "how long a player at the edge of a fight is kept in it",
    "FIGHT_ACT": "how far away a player hitting or casting into a fight still counts in it",
    "FIGHT_CLOSE": "how close a player must come to have joined a fight",
    "FOUGHT": "how much casting and attacking makes it a fight and not players passing",
    "SPLIT_MIN_S": "how long a player must be on the enemy's ground to be on a split",
    "SPLIT_GAP_S": "how long back on the own side ends a split",
    "SPLIT_FIGHT_GAP_S": "how long two groups may be out of contact and still be one split fight",
    "SPLIT_FIGHT_MIN": "how many players a side open a split fight",
    "GROUND_MOVE": "how far a team must move for it to have taken or given ground",
    "GROUND_S": "how long a team must hold new ground for the move to count",
    "GROUND_BACK": "how far back a team must go for it to have fallen back",
    "GROUND_SPLIT_MOVE": "how far a split must move for it to have taken or given ground",
    "GROUND_MIN": "the smallest move of ground that is told",
    "GROUND_JUMP": "how big a jump in position starts the reading again (a wipe and a base res)",
    "PIT_S": "how long in the pit counts as being in the pit",
    "SIDE_FIGHT_MAX": "how large a fight away from the main fight may be",
    "SIDE_FIGHT_S": "how long a fight away from the main fight must last",
    "UNDEFENDED_S": "how long a split must stand unanswered to be undefended",
    "SWAP_S": "how quickly one defender must replace another for it to be a swap",
    "SWAP_STAY_S": "how long the new defender must stay for it to be a swap",
    "JOIN_MOVE": "how far a player must travel to have joined from elsewhere",
    "JOIN_LEAD": "how far ahead of his team a joining player must be",
    "PUSHFLAG_R": "how close an enemy must be to the flagger to be pushing him",
    "PUSHFLAG_S": "how long an enemy must stay on the flagger for it to be a push",
    "PUSHFLAG_SHORT_S": "how long a push that follows the flagger into his team must last",
    "PUSHFLAG_LATE_S": "how late a hit on the flagger may land and still be the push",
    "PUSHFLAG_GAP_S": "how long a push on the flagger may break and still be one push",
    "PUSHFLAG_MATES": "how many team mates around the flagger make it a fight and not a push on him",
    "PUSHFLAG_AHEAD_S": "how long before his pickup a player is already his team's flagger",
    "ROUTE_ENDS": "how much of a flag run near the spawn and the stand is left out of the route",
    "ROUTE_OFF": "how close to a drawn flag run the carrier must keep",
    "ROUTE_CLEAR": "how much nearer one drawn flag run must be than the other",
    "ROUTE_MIN_S": "how long the carrier must walk a route for it to be read",
    "LEAD_S": "how far ahead the flag lead looks",
    "LEAD_HALF": "where half a flag ahead begins", "LEAD_ONE": "where a full flag ahead begins",
    "LEAD_ONE_HALF": "where a flag and a half ahead begins", "LEAD_TWO": "where two flags ahead begins",
    "STANDOFF_S": "how long two teams must stand off for it to be a stand-off",
    "STANDOFF_HITS": "how little may be traded in a stand-off", "STANDOFF_MIN": "how many players a side make a stand-off",
    "STANDOFF_R": "how close two teams stand in a stand-off",
    "STANDOFF_SPLIT_MIN": "how many players make a stand-off on a split", "STANDOFF_SPLIT_S": "how long a split must stand off",
    "STANDOFF_STILL": "how still a team must be in a stand-off", "STANDOFF_NEAR": "how near the teams are in a stand-off",
    "PICKUP_DELAY_S": "how late a flag must be picked up to be a delayed pickup",
    "HOLD_S": "how long a flag must be kept near the stand to be a held flag",
    "HOLD_BACK_S": "how long a flag is kept back before it is a hold",
    "LEFT_AT_SPAWN_S": "how long a flag may lie at the spawn before it is left there on purpose",
    "BOOST_LATE_S": "how close to the boost a cap must come to be held for it",
    "HELP_IN_S": "how soon help must reach a flagger", "HELP_BACK_S": "how soon the help must be back",
    "LEAVE_RES_S": "how long before the base res a team must leave", "MONK_S": "how long a monk must be in a fight to count there",
    "MONK_MIN": "how many monks are counted in a fight", "LORD_GAP_S": "how long a Lord push may break and still be one push",
    "DOUBLE_NEXT_S": "how soon the second player must go back for it to be a double run",
    "FLAG_TAKEN_OUT_S": "how long a flag picked up at home may wait before it is a run",
}

_num = lambda p: (re.search(r"\((\d+ v \d+)", p["scenario"]) or [None, None])[1] if p["play"] == "numbers" else None
sig = lambda p: (p["play"], p["team"], p.get("side"), p.get("call") or p.get("answer") or p.get("ours"), p.get("size"), p.get("defenders"), _num(p))
kind = lambda p: ({"flagger pushed": "push flagger"}.get(p["play"], p["play"]), p["team"])

_SNIP = ("import json, sys, moments\n"
         "out = {}\n"
         "for rid in sys.argv[2:]:\n"
         "    r, rec, ex = moments._one(rid)\n"
         "    out[rid] = {'error': rec['error']} if isinstance(rec, dict) and 'error' in rec else (ex or {}).get('plays', [])\n"
         "json.dump(out, open(sys.argv[1], 'w'), default=list)\n")


def _read(ids, name=None, value=None):
    """The plays of these matches with one number of the reading set to another value (or as it is)."""
    fd, path = tempfile.mkstemp(suffix=".json"); os.close(fd)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    env.pop("GVG_TRY", None)
    if name: env["GVG_TRY"] = f"{name}={value}"
    r = subprocess.run([sys.executable, "-c", _SNIP, path] + list(ids), cwd=ENGINE, env=env, capture_output=True, text=True)
    try: out = json.load(open(path))
    except Exception: out = {rid: {"error": (r.stdout + r.stderr)[-300:]} for rid in ids}
    os.remove(path)
    return out


def tests():
    """Every number of the reading at a quarter either way and at half and double: (name, share, value)."""
    sys.path.insert(0, ENGINE); import common
    out = []
    for n in common.TRY_NAMES:
        base = getattr(common, n)
        for k in QUARTER + FAR:
            v = base * k; v = int(round(v)) if isinstance(base, int) else round(v, 3)
            if v != base and (n, v) not in [(a, c) for a, _, c in out]: out.append((n, k, v))
    return out


def run(out, ids, jobs=2):
    sys.path.insert(0, ENGINE); import common
    ids = [next((r for r in common.replay_index() if r.startswith(i)), i) for i in ids]
    base = _read(ids)
    bad = [r for r in ids if isinstance(base[r], dict)]
    if bad: sys.exit(f"confidence: the engine fails on {bad} as it is: {base[bad[0]]['error']}")
    T = tests(); res = {r: {p["id"]: {"same": [], "other": [], "gone": [], "failed": []} for p in base[r]} for r in ids}
    done = 0
    with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
        for (n, k, v), got in zip(T, ex.map(lambda t: _read(ids, t[0], t[2]), T)):
            done += 1
            if done % 20 == 0: print(f"  {done} of {len(T)} readings", file=sys.stderr, flush=True)
            for r in ids:
                Q = got.get(r)
                for p in base[r]:
                    e = res[r][p["id"]]
                    if not isinstance(Q, list): e["failed"].append([n, k]); continue        # R-460: a reading that fails is counted, never taken as "gone"
                    if any(sig(q) == sig(p) and abs(q["t0"] - p["t0"]) <= SAME_S for q in Q): e["same"].append([n, k])
                    elif any(kind(q) == kind(p) and q["t1"] >= p["t0"] and q["t0"] <= p["t1"] for q in Q): e["other"].append([n, k])
                    else: e["gone"].append([n, k])
    failed = sorted({(n, k) for r in ids for e in res[r].values() for n, k in e["failed"]})
    if failed: print(f"confidence: {len(failed)} readings failed and are left out of every count: {failed}", file=sys.stderr)
    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    json.dump({"about": "How steady each play's reading is when the draft numbers of the reading are moved (tools/golden/confidence.py; R-492). Bands fitted to his grades of five games, 2026-11-17.",
               "engine": commit, "tests": len(T), "failed": [list(f) for f in failed], "plays": {r: {i: dict(e, **band(e)) for i, e in res[r].items()} for r in ids},
               "base": {r: [{k_: p.get(k_) for k_ in ("id", "play", "team", "side", "t0", "t1", "scenario", "clear")} for p in base[r]] for r in ids}}, open(out, "w"), ensure_ascii=False)
    show(out)


def band_of(es, extra=()):
    """The band of a situation and the reason in a player's words (fitted to his grades of five games, 2026-11-17: the module's own text). `es`: the stored
    readings of its plays (the two sides of a split, of a numbers moment); `extra`: those of the joins, collapses and leaves told in its row (R-514), which
    count as its details and never as the situation itself."""
    es, every = list(es), list(es) + list(extra)
    keys = sorted({(n, k) for e in every for t in ("same", "other", "gone") for n, k in e[t]})
    names = lambda L: list(dict.fromkeys(L))
    gone = lambda steps: names(n for n, k in keys if k in steps and es and all([n, k] in e["gone"] for e in es))
    moved = lambda steps: names(n for n, k in keys if k in steps and any([n, k] in e["other"] or [n, k] in e["gone"] for e in every))
    say = lambda N, n=2: "; ".join(WORDS.get(x, x) for x in N[:n]) + (f"; and {len(N) - n} more of its settings" if len(N) > n else "")
    vq, vf, mq = gone(QUARTER), gone(FAR), moved(QUARTER)
    if vq: return {"band": "low", "why": "The engine stops reading this when one of its settings is moved a quarter: " + say(vq) + ".", "moved_by": vq}
    if vf: return {"band": "medium", "why": "Still read when the engine's settings are moved a quarter either way. At half or double it is no longer read; it hangs on: " + say(vf) + ".", "moved_by": vf}
    if mq: return {"band": "medium", "why": "Read as a situation wherever the engine's settings sit, but who is counted in it or the call changes when one is moved a quarter: " + say(mq) + ".", "moved_by": mq}
    return {"band": "high", "why": "Still read wherever the engine's settings sit, down to half and up to double, and read the same way at a quarter either way.", "moved_by": []}


def band(e):
    """The band of one play on its own."""
    return band_of([e])


def reband(path):
    """Write the bands again from the stored readings (after the bands are fitted again): the engine is not run."""
    D = json.load(open(path))
    for P in D["plays"].values():
        for e in P.values(): e.update(band(e))
    D["about"] = "How steady each play's reading is when the draft numbers of the reading are moved (tools/golden/confidence.py; R-492). Bands fitted to his grades of five games, 2026-11-17."
    json.dump(D, open(path, "w"), ensure_ascii=False)
    show(path)


def show(path, rid=None):
    D = json.load(open(path))
    for r, P in D["plays"].items():
        if rid and not r.startswith(rid): continue
        base = {p["id"]: p for p in D["base"][r]}
        c = collections.Counter(("none" if base[i].get("clear") is False else e["band"], base[i]["play"]) for i, e in P.items())
        print(f"{r[:8]}: {len(P)} plays; " + "; ".join(f"{b} {sum(v for (x, _), v in c.items() if x == b)}" for b in ("high", "medium", "low", "none")))
        for k_ in sorted({k for _, k in c}): print(f"   {k_:15}" + "  ".join(f"{b} {c[(b, k_)]:3}" for b in ("high", "medium", "low", "none")))
        movers = collections.Counter(n for e in P.values() for n in e["moved_by"])
        print("   the numbers that move the most plays: " + ", ".join(f"{n} {v}" for n, v in movers.most_common(10)))
        if rid:
            for i, e in sorted(P.items(), key=lambda kv: base[kv[0]]["t0"]):
                p = base[i]; print(f"   {cl(p['t0']):>5} {p['team']:6} {p['play']:14} {e['band']:6} {p['scenario'][:90]} | {e['why'][:140]}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "run":
        j = int(a[a.index("--jobs") + 1]) if "--jobs" in a else 2
        run(a[1], [x for i, x in enumerate(a[2:]) if x != "--jobs" and a[2:][i - 1] != "--jobs"], j)
    elif a and a[0] == "show": show(a[1], a[2] if len(a) > 2 else None)
    elif a and a[0] == "reband": reband(a[1])
    else: print(__doc__)
