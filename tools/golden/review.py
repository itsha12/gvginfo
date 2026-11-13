#!/usr/bin/env python3
"""The review key (R-450): every row Denning has marked, kept as a test the reading must go on passing.

  python3 tools/golden/review.py score <plays file> [--key <path>]   score a run (from `moments.py all <file> --dev`)
  python3 tools/golden/review.py rows [--key <path>]                 the rows and their marks
  python3 tools/golden/review.py game <report id> <plays file>       one whole game, every situation the engine reads, as a
                                                                     table for him to mark while he watches it (R-454)

The key (`data/model/review_key.json`, on main; a copy rides on the branch) holds, for each row he was shown: the match,
the window, what the engine said then (`shown`), his mark and his words (`said`), and `checks`: Claude's reading of his
mark as things the plays must hold or must not hold, which he corrects. A check names plays by `play`, `side`, `team` and
a window in seconds of match time (`at` = the play overlaps it, `start` = the play begins inside it), and `want` gives the
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
    for r in K["rows"]:
        if not r.get("checks"): res["no check (not marked, or nothing to test)"] += 1; continue
        if r["rid"] not in by: missing.append(r["id"]); continue
        firm = [c for c in r["checks"] if not c.get("open")]; opn = [c for c in r["checks"] if c.get("open")]
        bad = [c for c in firm if not check(by[r["rid"]], c)]
        still = [c for c in opn if not check(by[r["rid"]], c)]
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
    print("By kind of play (rows passing of rows checked): " + "; ".join(f"{k} {a}/{b}" for k, (a, b) in sorted(by_type.items())))
    return res["FAIL"]


def situations(plays):
    """A game's plays grouped into situations: the two sides of one split phase, of one numbers moment, of one push on
    a flagger or of one Lord push are one situation, read once and judged from each side."""
    G = collections.OrderedDict()
    for p in sorted(plays, key=lambda p: (p["t0"], p["t1"])):
        kind = {"flagger pushed": "push flagger"}.get(p["play"], p["play"])
        k = (kind, p["t0"], p["t1"]) if kind in ("numbers", "lord", "push flagger") else (kind, p["t0"], p.get("size"), p.get("defenders")) if kind == "split" else (kind, p["t0"], p["team"])
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
    first = {"split": ("attacker", "defender", "attacker's main team"), "lord": ("attacker", "defender")}
    for i, g in enumerate(situations(P), 1):
        g.sort(key=lambda p: (first.get(p["play"], ()).index(p["side"]) if p["side"] in first.get(p["play"], ()) else 0, p["play"] != "push flagger"))
        read = g[0]["scenario"] + ("; ".join([""] + [p["scenario"].split(": ", 1)[-1] for p in g[1:] if p["play"] == "split" and p["side"] == "defender" and p.get("call") in ("collapse", "full collapse", "part-run")]))
        if g[0]["play"] == "numbers" and len(g) > 1: read += " | " + g[1]["scenario"].split("; ", 1)[-1]
        if g[0].get("soh"): read += " (Shadow of Haste run: set aside)"
        res = []
        for p in g:
            tests = [("yes: " if v else "no: ") + k for k, v in list(p["tests"].items()) + list(p.get("any_of", {}).items())]
            lab = p.get("call") or p.get("answer") or p.get("ours") or ""
            res.append(f"**{p['team']}**" + (f" ({p['side']})" if p["side"] not in ("own",) and p["play"] in ("split", "lord") else "") + (f" [{lab}]" if lab else "") + f": {p['job']}. **{'Met' if p['met'] else 'Not met'}**" + (" (" + "; ".join(tests) + ")" if tests else "") + ("" if p.get("ruled", True) else " *(job is a draft)*"))
        print(f"| {i} | {cl(g[0]['t0'])}–{cl(max(p['t1'] for p in g))} | {read} | " + "<br>".join(res) + " |")


def rows(key=KEY):
    for r in json.load(open(key))["rows"]:
        print(f"{r['id']:8} {r['mark']:12} {r['type']:34} {r['match']} {cl(r['window'][0])}-{cl(r['window'][1])} | {len(r.get('checks', []))} checks" + (" | " + r["note"] if r.get("note") else ""))


if __name__ == "__main__":
    a = sys.argv[1:]
    key = a[a.index("--key") + 1] if "--key" in a else KEY
    if a and a[0] == "score": sys.exit(1 if score(a[1], key) else 0)
    elif a and a[0] == "rows": rows(key)
    elif a and a[0] == "game": game(a[1], a[2])
    else: print(__doc__)
