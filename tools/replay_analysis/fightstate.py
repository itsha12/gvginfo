"""Fight state: who is winning the fight right now, as a forward-looking number (Denning D4: staying near the enemy's
boost depends on whether the own team is losing the fight).

Expected deaths per team in the next 10 s = the sum of every live player's death risk from the deaths node
(nodes.py), always from a death model that never saw the match (6 groups of matches; each match is predicted by the
model fitted on the other groups). It is measured every 5 s.

Used as: the win model's variable fight_state (enemy minus own expected deaths), and as a situation control when
choices are compared (usual.py), so "fell back" is compared with teams that were losing their fight about as badly.
A match not among the trained ones is predicted by the model fitted on all of them.

Usage:  python3 fightstate.py build            predictions for every trained match (and the newest replays)
        python3 fightstate.py <report id>      the fight state every 30 s
In code: build(ids); expected(rid, t) -> {tag: expected deaths} or None; diff(rid, t, tag) -> enemy minus own."""
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings("ignore")

CACHE = "/tmp/gvg_fightstate"
FOLDS = 6


def _predict(e, rows, feats):
    import pandas as pd
    X = pd.DataFrame([{k: r.get(k) for k in feats} for r in rows]).astype(float)
    return e.predict_proba(X)[:, 1]


def _save(rid, rows, p):
    out = {}
    for r, q in zip(rows, p):
        out.setdefault(str(r["t"]), {}).setdefault(r["team"], 0.0)
        out[str(r["t"])][r["team"]] += float(q)
    json.dump({t: {k: round(v, 3) for k, v in d.items()} for t, d in out.items()}, open(os.path.join(CACHE, rid + ".json"), "w"))


def build(ids, extra=()):
    """Out-of-match predictions for ids (by groups) and for extra (from a model on all ids). Clears the win model's
    table cache, which reads them."""
    import nodes as N, model as M, shutil
    os.makedirs(CACHE, exist_ok=True)
    ids = list(ids)
    groups = [ids[i::FOLDS] for i in range(FOLDS)]
    for g in groups:
        if not g: continue
        train = [x for x in ids if x not in g]
        df, X, y, gg, w = N._frame("deaths", train)
        e = N._ebm(gg.nunique()).fit(X, y, sample_weight=w)
        for rid in g: rows = N.node_rows("deaths_all", rid); _save(rid, rows, _predict(e, rows, list(X.columns)))
    if extra:
        df, X, y, gg, w = N._frame("deaths", ids)
        e = N._ebm(gg.nunique()).fit(X, y, sample_weight=w)
        for rid in extra: rows = N.node_rows("deaths_all", rid); _save(rid, rows, _predict(e, rows, list(X.columns)))
    shutil.rmtree(M.TABLES, ignore_errors=True)


_C = {}
def expected(rid, t):
    if rid not in _C:
        p = os.path.join(CACHE, rid + ".json")
        _C[rid] = json.load(open(p)) if os.path.exists(p) else None
    d = _C[rid]
    if not d: return None
    return d.get(str(int(t) // 5 * 5)) or d.get(str(int(t) // 5 * 5 - 5))


def diff(rid, t, tag):
    """Enemy minus own expected deaths in the next 10 s (+ = the enemy is losing the fight), or None."""
    e = expected(rid, t)
    if not e: return None
    return round(sum(v for k, v in e.items() if k != tag) - e.get(tag, 0.0), 3)


if __name__ == "__main__":
    a = sys.argv[1:]
    import model as M
    if a and a[0] == "build":
        ids = [m for b in M.batches() for m in b["matches"]]
        import subprocess
        from common import REPO
        allr = list(json.loads(subprocess.check_output(["git", "-C", REPO, "show", "origin/replays:index.json"]))["matches"])
        build(ids, [x for x in allr if x not in ids])
        print("fight state built for", len(allr), "matches")
    elif a:
        rid = a[0]
        for t in range(0, 1800, 30):
            e = expected(rid, t)
            if e: print(f"{t // 60}:{t % 60:02d}", e)
