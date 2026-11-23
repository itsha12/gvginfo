#!/usr/bin/env python3
"""What is at stake in a situation (R-509, R-572): the second part of the engine's confidence, beside steadiness.

Steadiness (confidence.py) says whether the engine keeps reading a situation when its settings move; it cannot tell a
Visible decision from a Weak one or from no decision at all. His four reasons for those grades (R-509) are about what
is at stake: too brief; impact too small to make a difference; no real fight, nothing at stake; a weak or unclear small
edge. This tool measures those on every graded situation, from the engine's own records, and tests on his grades
whether they tell his Weak and No decision rows from his Classic and Visible ones, each game judged from the others.

Measures of a situation (the largest over its plays, where it has two sides):
  length   seconds from when it is told to when it ends                              ("too brief")
  traded   damage the two sides put on one another in its first 20 s, a living player a 10 s, both sides added
           (the execution record, execution.py)                                       ("no real fight")
  met      enemy players its players met in those seconds                             ("nothing at stake")
  hard     what followed in 90 s: deaths on both sides, NPCs lost, flags of lead moved ("impact too small")
`hard` is a result, so it can describe a graded row but is never part of the band of a new one: the band is read
before the result. It is shown to see whether "impact too small" is something the first 20 s already tell.

Nothing is guessed: a cut is kept only where, chosen on the other games, it tells his grades on the game left out.
A reading tool: it is in no cache key and changes no play.

Usage:  python3 tools/golden/stake.py <plays file from moments.py all> --key <main>/data/model/review_key.json [--json out.json]"""
import collections, json, statistics, sys

GRADES = ("classic", "visible", "weak", "none")
LOWISH = ("weak", "none")
SAME_S = 6
MEASURES = ("length", "traded", "met", "hard")
BEFORE = ("length", "traded", "met")            # what can be read before the result


def situations(D, K):
    """His graded situations of set f1 (the new way of grading, R-491) joined to the plays as read now."""
    by = collections.defaultdict(list)
    for p in D["plays"]: by[p["rid"]].append(p)
    out, lost = [], 0
    for r in K["rows"]:
        if r.get("set") != "f1" or r.get("scheme") != 2 or r.get("grade") not in GRADES or r.get("band") not in ("high", "medium", "low"): continue
        if r["rid"] not in by: lost += 1; continue
        t0, t1 = r["window"]
        kinds = {r["type"]} | ({"flagger pushed"} if r["type"] == "push flagger" else set())
        P = [p for p in by[r["rid"]] if p["play"] in kinds and abs(p["t0"] - t0) <= SAME_S]
        if not P: lost += 1; continue
        X = D["flag_cost"][r["rid"]].get("execution") or {}
        xs = [X[p["id"]] for p in P if p["id"] in X]
        hard = None
        for p in P:
            af = ((p.get("at_told") or p).get("after") or {}).get("90")
            if af and af.get("lead_change") is not None:
                h = sum(af["deaths"]) + sum(af["npcs"]) + abs(af["lead_change"]); hard = h if hard is None else max(hard, h)
        out.append({"id": r["id"], "rid": r["rid"], "match": r["match"], "t0": t0, "kind": r["type"], "grade": r["grade"], "band": r["band"], "reason": r.get("reason") or [],
                    "length": max(t1 - t0, max(p["t1"] - p["t0"] for p in P)),
                    "traded": max((x["own"]["dmg"] + ((x["their"] or {}).get("dmg") or 0) for x in xs), default=None),
                    "met": max((x["n"][1] for x in xs), default=None), "hard": hard})
    return out, lost


def _rate(S): return (sum(1 for s in S if s["grade"] in LOWISH), len(S))


def _best_cut(S, key):
    """The cut on one measure that best tells his Weak and No decision rows (at or under it) from the rest: the largest share of them caught less the share of his
    Classic and Visible rows caught with them."""
    V = sorted({s[key] for s in S if s[key] is not None})
    lo, hi = [s for s in S if s["grade"] in LOWISH and s[key] is not None], [s for s in S if s["grade"] not in LOWISH and s[key] is not None]
    if not lo or not hi: return None
    best = None
    for c in V:
        j = sum(1 for s in lo if s[key] <= c) / len(lo) - sum(1 for s in hi if s[key] <= c) / len(hi)
        if best is None or j > best[0]: best = (j, c)
    return best[1]


def report(path, key, out_json=None):
    D, K = json.load(open(path)), json.load(open(key))
    S, lost = situations(D, K)
    res = {"situations": len(S), "not found in this run": lost, "by_grade": {}, "cuts": {}, "held_out": {}}
    games = sorted({s["rid"] for s in S})
    print(f"What is at stake (R-509): {len(S)} graded situations of {len(games)} games read by this engine ({lost} of his rows are of games or plays not in this run)")
    print("\nA. The middle of each measure by his grade (and the lower and upper quarter)")
    print(f"   {'':12} {'rows':>5}  " + "  ".join(f"{m:>22}" for m in MEASURES))
    for g in GRADES:
        X = [s for s in S if s["grade"] == g]; row = res["by_grade"][g] = {"rows": len(X)}
        cells = []
        for m in MEASURES:
            v = sorted(s[m] for s in X if s[m] is not None)
            if len(v) < 4: cells.append(f"{'':>22}"); continue
            q = statistics.quantiles(v, n=4); row[m] = [round(q[0], 1), round(q[1], 1), round(q[2], 1)]
            cells.append(f"{q[1]:8.1f} ({q[0]:.0f} to {q[2]:.0f})".rjust(22))
        print(f"   {({'none': 'no decision'}.get(g, g)):12} {len(X):5}  " + "  ".join(cells))
    print("\nB. His reasons (R-509) against the measures: the middle of each where he ticked that reason")
    rs = collections.defaultdict(list)
    for s in S:
        for r in s["reason"]: rs[r].append(s)
    for r, X in sorted(rs.items(), key=lambda kv: -len(kv[1])):
        mid = lambda m: (lambda v: f"{statistics.median(v):.1f}" if v else "")([s[m] for s in X if s[m] is not None])
        print(f"   {r[:60]:60} {len(X):3}   " + "  ".join(f"{m} {mid(m)}" for m in MEASURES))
    if not rs: print("   (no reason ticked on a row of these games)")
    print("\nC. One cut a measure, fitted on all games: his Weak and No decision rows at or under it, against his Classic and Visible rows at or under it")
    for m in MEASURES:
        c = _best_cut(S, m)
        if c is None: continue
        lo = [s for s in S if s["grade"] in LOWISH and s[m] is not None]; hi = [s for s in S if s["grade"] not in LOWISH and s[m] is not None]
        a, b = sum(1 for s in lo if s[m] <= c), sum(1 for s in hi if s[m] <= c)
        res["cuts"][m] = {"cut": c, "weak_or_none_under": [a, len(lo)], "classic_or_visible_under": [b, len(hi)]}
        print(f"   {m:8} at or under {c:6.1f}: {a} of {len(lo)} Weak or No decision ({a / len(lo):.0%}); {b} of {len(hi)} Classic or Visible ({b / len(hi):.0%})" + ("   (a result: not for the band)" if m not in BEFORE else ""))
    print("\nD. Each game judged from the others (the cut chosen without it): the rows it calls low stake, by his grade")
    print("   'low stake' = at or under the cut. Read against steadiness alone: the rows the band already calls low.")
    for name, keys in (("length", ("length",)), ("traded", ("traded",)), ("met", ("met",)), ("length or traded", ("length", "traded")), ("length and traded", ("length", "traded"))):
        flagged = []
        for g in games:
            train, test = [s for s in S if s["rid"] != g], [s for s in S if s["rid"] == g]
            cuts = {k: _best_cut(train, k) for k in keys}
            if any(c is None for c in cuts.values()): continue
            hit = (lambda s: all(s[k] is not None and s[k] <= cuts[k] for k in keys)) if " and " in name else (lambda s: any(s[k] is not None and s[k] <= cuts[k] for k in keys))
            flagged += [s for s in test if hit(s)]
        c = collections.Counter(s["grade"] for s in flagged); tot = collections.Counter(s["grade"] for s in S)
        res["held_out"][name] = {g: [c[g], tot[g]] for g in GRADES}
        print(f"   {name:18} " + "  ".join(f"{({'none': 'no decision'}.get(g, g))} {c[g]} of {tot[g]}" for g in GRADES)
              + f"   -> of the rows flagged, {sum(c[g] for g in LOWISH)} of {len(flagged)} are Weak or No decision")
    c = collections.Counter(s["grade"] for s in S if s["band"] == "low"); tot = collections.Counter(s["grade"] for s in S)
    res["held_out"]["band low (steadiness alone)"] = {g: [c[g], tot[g]] for g in GRADES}
    print(f"   {'band low (steady.)':18} " + "  ".join(f"{({'none': 'no decision'}.get(g, g))} {c[g]} of {tot[g]}" for g in GRADES)
          + f"   -> of the rows flagged, {sum(c[g] for g in LOWISH)} of {sum(c.values())} are Weak or No decision")
    print("\nE. By band and length (his grades: Classic, Visible, Weak, No decision)")
    for b in ("high", "medium", "low"):
        for nm, f in (("under 20 s", lambda s: s["length"] < 20), ("20 to 40 s", lambda s: 20 <= s["length"] < 40), ("40 s or longer", lambda s: s["length"] >= 40)):
            X = [s for s in S if s["band"] == b and f(s)]; c = collections.Counter(s["grade"] for s in X)
            print(f"   {b:7} {nm:15} " + ", ".join(str(c[g]) for g in GRADES))
    if out_json: json.dump(res, open(out_json, "w"), indent=1)
    return res


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 3 and "--key" in a: report(a[0], a[a.index("--key") + 1], a[a.index("--json") + 1] if "--json" in a else None)
    else: print(__doc__)
