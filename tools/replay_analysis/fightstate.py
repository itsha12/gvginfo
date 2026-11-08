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

FOLDS = 6


def _dir(ids=None):
    """Predictions depend on the training set: one folder per set of trained matches and death-model code (cache.py)."""
    import cache, model as M
    ids = ids if ids is not None else [m for b in M.batches() for m in b["matches"]]
    return os.path.join(cache.ROOT, "fightstate", cache.fit_key("node"), cache.ids_key(ids))


def version(rid):
    """A short key for the fight-state predictions a match table reads (changes when they change)."""
    import hashlib
    p = os.path.join(_dir(), rid + ".json")
    return hashlib.sha1(open(p, "rb").read()).hexdigest()[:10] if os.path.exists(p) else "none"


def _predict(e, rows, feats):
    import pandas as pd
    X = pd.DataFrame([{k: r.get(k) for k in feats} for r in rows]).astype(float)
    return e.predict_proba(X)[:, 1]


def _save(rid, rows, p):
    out = {}
    for r, q in zip(rows, p):
        out.setdefault(str(r["t"]), {}).setdefault(r["team"], 0.0)
        out[str(r["t"])][r["team"]] += float(q)
    json.dump({t: {k: round(v, 3) for k, v in d.items()} for t, d in out.items()}, open(os.path.join(_dir(), rid + ".json"), "w"))


def _fit_job(job):
    """One death model for the predictions (top level so it can run in another process, parallel.py)."""
    import nodes as N
    X, y, w, n = job
    return N._ebm(n).fit(X, y, sample_weight=w)


def build(ids, extra=()):
    """Out-of-match predictions for ids (by groups) and for extra (from a model on all ids). Only the groups with a
    match still to predict are fitted (the learning report calls this again with the newest replays as extra, after
    cache.py warm has built the trained ones), and the fits run side by side (parallel.py). Same models, same
    predictions."""
    import nodes as N, parallel
    ids = list(ids)
    os.makedirs(_dir(), exist_ok=True)
    have = lambda r: os.path.exists(os.path.join(_dir(), r + ".json"))
    groups = [g for g in (ids[i::FOLDS] for i in range(FOLDS)) if g and not all(have(r) for r in g)]
    extra = [r for r in extra if not have(r)]
    if not groups and not extra: return      # already built for this training set and engine
    jobs, cols = [], []           # each fit's own variables (they depend on how many matches it is trained on)
    for g in groups:
        df, X, y, gg, w = N._frame("deaths", [x for x in ids if x not in g])
        jobs.append((X, y, w, gg.nunique())); cols.append(list(X.columns))
    if extra:
        df, X, y, gg, w = N._frame("deaths", ids)
        jobs.append((X, y, w, gg.nunique())); cols.append(list(X.columns))
    models = parallel.run(_fit_job, jobs)
    for g, e, c in zip(groups, models, cols):
        for rid in g: rows = N.node_rows("deaths_all", rid); _save(rid, rows, _predict(e, rows, c))
    if extra:
        for rid in extra: rows = N.node_rows("deaths_all", rid); _save(rid, rows, _predict(models[-1], rows, cols[-1]))


def build_group(ids, k):
    """One group's predictions only (the speed-up: each group on its own machine). Same fit as build()."""
    import nodes as N
    ids = list(ids); os.makedirs(_dir(), exist_ok=True)
    g = ids[k::FOLDS]
    if not g or all(os.path.exists(os.path.join(_dir(), r + ".json")) for r in g): return g
    df, X, y, gg, w = N._frame("deaths", [x for x in ids if x not in g])
    e = _fit_job((X, y, w, gg.nunique())); c = list(X.columns)
    for rid in g: rows = N.node_rows("deaths_all", rid); _save(rid, rows, _predict(e, rows, c))
    return g


def build_extra(ids, extra):
    """The stored replays outside the training set, from a model on every trained match (the speed-up's last job)."""
    import nodes as N
    ids = list(ids); os.makedirs(_dir(), exist_ok=True)
    extra = [r for r in extra if not os.path.exists(os.path.join(_dir(), r + ".json"))]
    if not extra: return
    df, X, y, gg, w = N._frame("deaths", ids)
    e = _fit_job((X, y, w, gg.nunique())); c = list(X.columns)
    for rid in extra: rows = N.node_rows("deaths_all", rid); _save(rid, rows, _predict(e, rows, c))


_C = {}
def expected(rid, t):
    if rid not in _C:
        p = os.path.join(_dir(), rid + ".json")
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
        allr = __import__("common").replay_ids()
        build(ids, [x for x in allr if x not in ids])
        print("fight state built for", len(allr), "matches")
    elif a:
        rid = a[0]
        for t in range(0, 1800, 30):
            e = expected(rid, t)
            if e: print(f"{t // 60}:{t % 60:02d}", e)
