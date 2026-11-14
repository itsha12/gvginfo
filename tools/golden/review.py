#!/usr/bin/env python3
"""The review key (R-450): every row Denning has marked, kept as a test the reading must go on passing.

  python3 tools/golden/review.py score <plays file> [--key <path>]   score a run (from `moments.py all <file> --dev`)
  python3 tools/golden/review.py rows [--key <path>]                 the rows and their marks
  python3 tools/golden/review.py game <report id> <plays file>       one whole game, every situation the engine reads, as a
                                                                     table for him to mark while he watches it (R-454)
  python3 tools/golden/review.py numbers [--steps 0.5,0.75,1.25,2] [--names FIGHT_LINK,JOIN_S]
                                                                     the numbers test (R-470): each draft number of the fight reading
                                                                     at those shares of its value, against every marked row (about a
                                                                     minute a value, one at a time: a run already uses every core)
  python3 tools/golden/review.py compare <report id> <rows.json> <marks.json> <plays he marked> name=<plays> ...
                                                                     one marked game, several engines against his verdicts on
                                                                     it (the before-and-after test)
  python3 tools/golden/review.py export <plays file> <out.json> --part N [--set w1] [--label "round 3"] [--drop <id>,<id>]
                                                                     the games of that part of a whole-game set (dev_set.json) as
                                                                     the rows of the site's Model > Game review page, where he
                                                                     marks the reading of each situation and each side's call
                                                                     (R-455; written to main's data/model/game_reviews.json; his
                                                                     marks are saved by the page to game_review_marks.json)

The key (`data/model/review_key.json`, on main; a copy rides on the branch) holds, for each row he was shown: the match,
the window, what the engine said then (`shown`), his mark and his words (`said`), and `checks`: Claude's reading of his
mark as things the plays must hold or must not hold, which he corrects. A check names plays by `play`, `side`, `team` and
a window in seconds of match time (`at` = the play overlaps it, `start` = the play begins inside it, `end` = it ends inside it), and `want` gives the
fields they must carry (`who~` = these roles among who, `who#` = how many, `scenario~` = these words in the scenario; a
list of values = any of them). `has` passes when one play fits, `none` when no play fits. A check marked `open` is a
fault known and not yet fixed: it is reported apart and does not fail the row. Engine faults go here as checks, never
into RULINGS.md (R-452). An accuracy figure by kind of play comes from the rows of a whole-game review (R-454), where
every call of a game is marked, not from rows picked to cover rare plays."""
import collections, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
KEY = os.path.join(REPO, "data", "model", "review_key.json")
cl = lambda t: f"{int(t) // 60}:{int(t) % 60:02d}"


def fits(p, sel, want):
    for k in ("play", "side", "team"):
        if k in sel and p.get(k) != sel[k]: return False
    if "at" in sel and not (p["t1"] >= sel["at"][0] and p["t0"] <= sel["at"][1]): return False
    if "start" in sel and not (sel["start"][0] <= p["t0"] <= sel["start"][1]): return False
    if "end" in sel and not (sel["end"][0] <= p["t1"] <= sel["end"][1]): return False
    for k, v in (want or {}).items():
        if k == "who~":
            if not all(any(w in r for r in p.get("who", [])) or w in p.get("scenario", "") for w in v): return False
        elif k == "who#":
            if len(p.get("who", [])) != v: return False
        elif k == "scenario~":
            if not all(w in p.get("scenario", "") for w in ([v] if isinstance(v, str) else v)): return False
        elif isinstance(v, list):
            if p.get(k) not in v: return False
        elif p.get(k) != v: return False
    return True


def check(plays, c):
    kind = "has" if "has" in c else "none"
    sel = c[kind]
    hit = [p for p in plays if fits(p, sel, c.get("want") if kind == "has" else sel.get("want"))]
    return bool(hit) if kind == "has" else not hit


def score(path, key=KEY):
    K = json.load(open(key)); D = json.load(open(path))
    by = collections.defaultdict(list)
    for p in D["plays"]: by[p["rid"]].append(p)
    res, missing, by_type = collections.Counter(), [], collections.defaultdict(lambda: [0, 0])
    opened = collections.defaultdict(lambda: [0, 0])          # set -> [open checks that now hold, open checks]
    for r in K["rows"]:
        if not r.get("checks"): res["no check (not marked, or nothing to test)"] += 1; continue
        if r["rid"] not in by: missing.append(r["id"]); continue
        firm = [c for c in r["checks"] if not c.get("open")]; opn = [c for c in r["checks"] if c.get("open")]
        bad = [c for c in firm if not check(by[r["rid"]], c)]
        still = [c for c in opn if not check(by[r["rid"]], c)]
        opened[r.get("set")][0] += len(opn) - len(still); opened[r.get("set")][1] += len(opn)
        ok = not bad
        res["pass" if ok else "FAIL"] += 1
        by_type[r["type"]][0] += ok; by_type[r["type"]][1] += 1
        if bad:
            print(f"FAIL {r['id']} ({r['type']}; his mark: {r['mark']}) {r['match']} {cl(r['window'][0])}-{cl(r['window'][1])}")
            for c in bad: print("     ", json.dumps(c, ensure_ascii=False))
        for c in still: print(f"open {r['id']} ({r['type']}): {c.get('why', '')}")
        for c in opn:
            if c not in still: print(f"now passes, was open: {r['id']} ({r['type']}): {c.get('why', '')}")
    print("\nThe review key:", ", ".join(f"{v} {k}" for k, v in sorted(res.items())), (f"; matches not in the run: {missing}" if missing else ""))
    print("Open checks that hold now, of the open checks, by set: " + "; ".join(f"{k}: {a} of {b}" for k, (a, b) in sorted(opened.items(), key=str) if b))
    print("By kind of play (rows passing of rows checked): " + "; ".join(f"{k} {a}/{b}" for k, (a, b) in sorted(by_type.items())))
    return res["FAIL"]


def situations(plays):
    """A game's plays grouped into situations: the two sides of one split phase, of one numbers moment, of one push on
    a flagger or of one Lord push are one situation, read once and judged from each side."""
    G = collections.OrderedDict()
    for p in sorted(plays, key=lambda p: (p["t0"], p["t1"])):
        kind = {"flagger pushed": "push flagger"}.get(p["play"], p["play"])
        k = (kind, p["t0"]) if kind == "numbers" else (kind, p["t0"], p["t1"]) if kind in ("lord", "push flagger") else (kind, p["t0"], p.get("size"), p.get("defenders")) if kind == "split" else (kind, p["t0"], p["team"])
        if kind == "split":                               # the attacker's and the defender's play of a phase can end a few seconds apart
            k = next((q for q in G if q[0] == "split" and q[2:] == k[2:] and abs(q[1] - k[1]) <= 2), k)
        G.setdefault(k, []).append(p)
    return list(G.values())


def game(rid, path, set_id="w"):
    """One game, every situation the engine reads, as a table for Denning to mark while he watches it (R-454)."""
    D = json.load(open(path)); rid = next(r for r in D["matches"] if r.startswith(rid)); m = D["matches"][rid]
    P = [p for p in D["plays"] if p["rid"] == rid]
    print(f"**{' v '.join(m['teams'])}, {m['map']}, {m['date']}** ([replay](https://gvg.report/report/{rid}#map)); {len(situations(P))} situations\n")
    print("| # | Time | What the engine reads | Each side's job & result |\n|---|---|---|---|")
    for i, g in enumerate(situations(P), 1):
        read = _reads(g)
        res = []
        for p in g:
            tests = [("yes: " if v else "no: ") + k for k, v in list(p["tests"].items()) + list(p.get("any_of", {}).items())]
            lab = p.get("call") or p.get("answer") or p.get("ours") or ""
            res.append(f"**{p['team']}**" + (f" ({p['side']})" if p["side"] not in ("own",) and p["play"] in ("split", "lord") else "") + (f" [{lab}]" if lab else "") + f": {p['job']}. **{'Met' if p['met'] else 'Not met'}**" + (" (" + "; ".join(tests) + ")" if tests else "") + ("" if p.get("ruled", True) else " *(job is a draft)*"))
        print(f"| {i} | {cl(g[0]['t0'])}–{cl(max(p['t1'] for p in g))} | {read} | " + "<br>".join(res) + " |")


FIRST = {"split": ("attacker", "defender", "attacker's main team", "defender's main team"), "lord": ("attacker", "defender")}


def _reads(g):
    """What the engine reads in a situation, in one line; sorts its plays (the attacker first, then the defender)."""
    g.sort(key=lambda p: (FIRST.get(p["play"], ()).index(p["side"]) if p["side"] in FIRST.get(p["play"], ()) else 0, p["play"] != "push flagger"))
    read = g[0]["scenario"] + ("; ".join([""] + [p["scenario"].split(": ", 1)[-1] for p in g[1:] if p["play"] == "split" and p["side"] == "defender" and p.get("call") in ("collapse", "full collapse", "part-run")]))
    if g[0]["play"] == "numbers" and len(g) > 1: read += " | " + g[1]["scenario"].split("; ", 1)[-1]
    if g[0].get("soh"): read += " (Shadow of Haste run: set aside)"
    return read


def export(path, out, part, set_id="w1", label=None, drop=()):
    """The games of one part of a whole-game set as the rows of the site's Game review page (R-455): for each situation
    what the engine reads, and under it each side's call with its job, the result and the tests behind the result. He
    marks the reading and every call on its own. Games already in the file from another part are kept."""
    import datetime, subprocess
    D = json.load(open(path))
    whole = json.load(open(os.path.join(REPO, "data", "model", "dev_set.json")))["whole_game"]
    want = [w["rid"] for w in whole if w["set"] == set_id and w.get("part") == part]
    kept_back = {w["rid"] for w in whole if w.get("part") in ("hidden", "spare")}                                    # R-467: never on the page, whatever is asked for
    main_labels, own_labels = os.path.join(os.path.dirname(os.path.abspath(out)), "..", "maps", "labels"), os.path.join(REPO, "data", "maps", "labels")
    if os.path.isdir(main_labels):                                                                                   # his hall labels are saved to main: rows read from older labels would be put to him as the engine's reading
        differ = [f for f in sorted(os.listdir(main_labels)) if f.endswith(".json") and (not os.path.exists(os.path.join(own_labels, f)) or open(os.path.join(main_labels, f), "rb").read() != open(os.path.join(own_labels, f), "rb").read())]
        if differ: sys.exit("export: hall labels on main differ from the branch (" + ", ".join(differ) + "): copy them over, run the development set again, then export")
    old = json.load(open(out)) if os.path.exists(out) else {"games": []}
    games = [g for g in old["games"] if g["rid"] not in want and g["rid"] not in kept_back and not any(g["rid"].startswith(x) for x in drop)]      # drop: games taken off the page
    for rid in want:
        m = D["matches"][rid]; P = [p for p in D["plays"] if p["rid"] == rid]; sits = []
        for i, g in enumerate(situations(P), 1):
            read = _reads(g); calls = []
            for p in g:
                side = p["side"] if p["side"] not in ("own",) and p["play"] in ("split", "lord", "numbers") else ""
                calls.append({"id": p["id"], "team": p["team"], "side": side, "label": p.get("call") or p.get("answer") or p.get("ours") or "", "job": p["job"], "met": bool(p["met"]),
                              "tests": [[bool(v), k] for k, v in list(p["tests"].items()) + list(p.get("any_of", {}).items())], "any": bool(p.get("any_of")) and bool(p["tests"]) is False, "draft": not p.get("ruled", True)})
            sits.append({"n": i, "id": "s:" + g[0]["id"], "kind": {"flagger pushed": "push flagger"}.get(g[0]["play"], g[0]["play"]), "t0": g[0]["t0"], "t1": max(p["t1"] for p in g), "reads": read, "calls": calls})
        games.append({"set": set_id, "part": part, "label": label or f"part {part}", "rid": rid, "teams": m["teams"], "map": m["map"], "date": m["date"], "situations": sits})
    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    json.dump({"about": "The rows of Model > Game review (R-454, R-455): every situation the engine reads in each review game, written by tools/golden/review.py export on the engine branch. His marks are in game_review_marks.json, never here.",
               "generated": datetime.date.today().isoformat(), "engine": commit, "games": games}, open(out, "w"), ensure_ascii=False, indent=1)
    print("; ".join(f"{' v '.join(g['teams'])}: {len(g['situations'])} situations, {sum(len(s['calls']) for s in g['situations'])} calls" for g in games))


def compare(rid, rows_file, marks_file, shown_file, others):
    """One marked game, several engines side by side (the before-and-after test): each engine's calls for the game are
    matched to the calls he was shown (same play, team, side, call, sizes and numbers, starting within 6 s) and take his
    verdict on them; a call he was never shown is counted apart, since nobody has judged it. `shown_file` is the plays
    file of the engine whose rows he marked; `others` are name=plays-file pairs. The test leans toward the engine he
    marked for the calls he called right, and against it for the wrong ones, because only its calls were judged."""
    import re
    R, Mk = json.load(open(rows_file)), json.load(open(marks_file))
    g = next(g for g in R["games"] if g["rid"].startswith(rid)); mk = Mk["games"][g["rid"]]["marks"]
    num = lambda p: (re.search(r"\((\d+ v \d+)", p["scenario"]) or [None, None])[1] if p["play"] == "numbers" else None
    sig = lambda p: (p["play"], p["team"], p.get("side"), p.get("call") or p.get("answer") or p.get("ours"), p.get("size"), p.get("defenders"), num(p))
    load = lambda f: [p for p in json.load(open(f))["plays"] if p["rid"] == g["rid"]]
    shown, verdict = load(shown_file), {}
    for s_ in g["situations"]:
        sm = mk.get(s_["id"], {}).get("mark")
        for c in s_["calls"]:
            cm = mk.get(c["id"], {}).get("mark")
            verdict[c["id"]] = "repeat" if sm == "repeat" else "unmarked" if not sm else "wrong" if "wrong" in (sm, cm) else "partly" if "partly" in (sm, cm) else "right" if cm == "right" else "unmarked"
    right = [i for i, v in verdict.items() if v == "right"]
    print(f"{' v '.join(g['teams'])}: he was shown {len(verdict)} calls: " + ", ".join(f"{v} {k}" for k, v in collections.Counter(verdict.values()).most_common()))
    for name, f in others:
        res, hit = collections.Counter(), set()
        for p in load(f):
            m = [q for q in shown if q["id"] in verdict and sig(q) == sig(p) and abs(q["t0"] - p["t0"]) <= 6]
            if not m: res["never shown to him"] += 1; continue
            q = min(m, key=lambda q: abs(q["t0"] - p["t0"])); hit.add(q["id"])
            res[verdict[q["id"]] if verdict[q["id"]] != "right" or bool(q["met"]) == bool(p["met"]) else "right reading, another result"] += 1
        print(f"  {name}: {sum(res.values())} calls: " + ", ".join(f"{v} {k}" for k, v in res.most_common()) + f"; says {sum(1 for i in right if i in hit)} of his {len(right)} right calls")


NUMBERS = ("FIGHT_LINK", "JOIN_S", "FIGHT_HOLD_S", "FIGHT_ACT", "FIGHT_HOLD", "FIGHT_CLOSE", "FOUGHT", "FLAG_TAKEN_OUT_S", "DOUBLE_NEXT_S")


def numbers(steps=(0.5, 0.75, 1.25, 2.0), names=NUMBERS, jobs=1, key=KEY, work="/tmp/numbers"):
    """The numbers test (R-470): each draft number of the fight reading tried at these shares of its value, one at a time,
    over the development set, and scored against every row he has marked. For each value: the marked rows that then
    fail, and the open checks that then hold. It shows where a number sits (a wide stretch where nothing changes, or an
    edge where a small step breaks rows); it is not a way to pick a value (R-465, R-470)."""
    import concurrent.futures, subprocess
    sys.path.insert(0, os.path.join(REPO, "tools", "replay_analysis")); import common
    os.makedirs(work, exist_ok=True); K = json.load(open(key))

    def read(path):
        by = collections.defaultdict(list)
        for p in json.load(open(path))["plays"]: by[p["rid"]].append(p)
        bad, held = [], []
        for r in K["rows"]:
            if not r.get("checks") or r["rid"] not in by: continue
            if any(not check(by[r["rid"]], c) for c in r["checks"] if not c.get("open")): bad.append(r["id"])
            held += [r["id"] for c in r["checks"] if c.get("open") and check(by[r["rid"]], c)]
        return bad, held

    def run(name, v):
        out = os.path.join(work, f"{name}_{v}.json"); env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        if name: env["GVG_TRY"] = f"{name}={v}"
        r = subprocess.run([sys.executable, "moments.py", "all", out, "--dev"], cwd=os.path.join(REPO, "tools", "replay_analysis"), env=env, capture_output=True, text=True)
        if not os.path.exists(out): return name, v, None, (r.stdout + r.stderr)[-300:]
        res = read(out); os.remove(out); return name, v, res, ""

    todo = [("", 0)]
    for n in names:
        base = getattr(common, n)
        for k in steps:
            v = base * k; v = int(round(v)) if isinstance(base, int) else round(v, 3)
            if v != base and (n, v) not in todo: todo.append((n, v))
    got = {}
    with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
        for n, v, res, err in ex.map(lambda t: run(*t), todo):
            got[(n, v)] = res; print(f"  ran {n or 'as it is'} {v if n else ''}" + (f" FAILED: {err}" if res is None else ""), file=sys.stderr, flush=True)
    b0, h0 = got[("", 0)]
    print(f"As it is: {len(b0)} marked rows fail {b0 or ''}; {len(h0)} open checks hold")
    for n in names:
        print(f"{n} = {getattr(common, n)}")
        for (m, v), res in got.items():
            if m != n: continue
            if res is None: print(f"   {v}: the run failed"); continue
            bad, held = res; new_bad = [x for x in bad if x not in b0]; new_held = [x for x in held if x not in h0]; lost = [x for x in h0 if x not in held]
            print(f"   {v}: {len(new_bad)} marked rows fail" + (f" ({', '.join(new_bad)})" if new_bad else "") + (f"; open checks that then hold: {', '.join(new_held)}" if new_held else "") + (f"; open checks that no longer hold: {', '.join(lost)}" if lost else ""))


def rows(key=KEY):
    for r in json.load(open(key))["rows"]:
        print(f"{r['id']:8} {r['mark']:12} {r['type']:34} {r['match']} {cl(r['window'][0])}-{cl(r['window'][1])} | {len(r.get('checks', []))} checks" + (" | " + r["note"] if r.get("note") else ""))


if __name__ == "__main__":
    a = sys.argv[1:]
    key = a[a.index("--key") + 1] if "--key" in a else KEY
    if a and a[0] == "score": sys.exit(1 if score(a[1], key) else 0)
    elif a and a[0] == "rows": rows(key)
    elif a and a[0] == "numbers": numbers(tuple(float(x) for x in a[a.index("--steps") + 1].split(",")) if "--steps" in a else (0.5, 0.75, 1.25, 2.0), tuple(a[a.index("--names") + 1].split(",")) if "--names" in a else NUMBERS, key=key)
    elif a and a[0] == "game": game(a[1], a[2])
    elif a and a[0] == "compare": compare(a[1], a[2], a[3], a[4], [x.split("=", 1) for x in a[5:]])
    elif a and a[0] == "export": export(a[1], a[2], int(a[a.index("--part") + 1]), a[a.index("--set") + 1] if "--set" in a else "w1", a[a.index("--label") + 1] if "--label" in a else None, a[a.index("--drop") + 1].split(",") if "--drop" in a else ())
    else: print(__doc__)
