"""Step 3 of the learned causal map: discovery (Denning: discovery of unknown variables and interactions matters most).
Candidate variables are tested against every learned node on matches the node never saw; what holds up twice is held
for Denning's approval as a new link, never added to the model automatically.

The candidates (Denning, November 2026 review, M6): the variable catalogue (catalogue.py, prefix "p."): what each team
did in the 10 s and 30 s before the moment, generated mechanically from the replay schema (damage by target class,
healing, casts by target class, cancels, attacks, interrupts, conditions, knockdown and moving seconds, deaths; own,
enemy, own by line, and own minus enemy). They are decision and execution variables by construction, so a discovery
can become advice. State and build variables (the old pool: the win model's table, prefix "s.", and the build
features, prefix "b.") are no longer offered: they are adjustment in every node already, never a fix.

The test, in two stages (both held out by match, the node's own 6 folds):
  1. Screen: the node's current model is fitted on the training folds; a one-variable glass-box curve is then fitted on
     top of its readings (starting from them) and scored on the held-out fold. Gain = held-out loss without minus with
     (positive = the variable predicts what the node misses). Cheap, so every variable gets it.
  2. Confirm: the best SCREEN_KEEP variables per node that gained on the screen are refitted properly (the node's
     variables plus the new one, the same fits as a link test) against the node without it, on the same folds.
     A pass = confirmed gain more than twice its spread and positive in at least 5 of 6 folds.
The two-run rule (Denning): a candidate is offered only after it passes in two discovery runs (on different training
sets); a first pass is recorded in data/model/discovery_history.json as "passed once". Many variables are tested, so
chance winners are expected; the page says how many would pass by chance.

Usage:  python3 discover.py node <node>      one node (a GitHub job), writes data/model/discovery/<node>.json
        python3 discover.py join             joins the nodes' files: data/model/discovery.json, knowledge/discovery.md
        python3 discover.py all              every node here (slow), then join"""
import collections, glob, json, math, os, statistics, sys, warnings
import numpy as np
warnings.filterwarnings("ignore")
from common import REPO

OUT_DIR = os.path.join(REPO, "data", "model", "discovery")
SCREEN_KEEP = 6
MIN_PRESENT = 0.3        # a variable must be measured on at least this share of a node's rows
SKIP = {"won", "match", "team", "t"}


def _ids():
    import model as M
    return [m for b in M.batches() for m in b["matches"]]


HISTORY = os.path.join(REPO, "data", "model", "discovery_history.json")


def panel(rid):
    """{(team, t): {variable: value}} every 5 s: the variable catalogue (play variables only, M6)."""
    import catalogue
    return catalogue.panel(rid)


def _panel_job(rid):
    try: return rid, {f"{k[0]}|{k[1]}": v for k, v in panel(rid).items()}
    except Exception as ex: return rid, {"error": str(ex)}


def frame(node, ids):
    """The node's rows with every candidate variable joined at the row's moment."""
    import pandas as pd, parallel, eventlayer as EL, learnednodes as LN
    V = EL.load_values() or {}
    df, X, y, g = LN.frame(node, ids, V)
    pans = dict(parallel.run(_panel_job, sorted(set(df["match"]))))
    cand = []
    for _, r in df.iterrows():
        P = pans.get(r["match"]) or {}
        t = int(r["t"]); t5 = t - t % 5
        v = None
        for k in (t5, t5 - 5, t5 - 10):
            v = P.get(f"{r['team']}|{k}")
            if v: break
        cand.append(v or {})
    C = pd.DataFrame(cand, index=df.index)
    own = set(X.columns)
    keep = [c for c in C.columns if c.split(".", 1)[1] not in own and C[c].notna().mean() >= MIN_PRESENT and C[c].nunique() > 1]
    return df, X, y, g, C[keep].astype(float)


def _loss(reg, yte, p):
    if reg: return float(np.mean(np.abs(yte - p)))
    p = np.clip(p, .002, .998); return float(np.mean(-(yte * np.log(p) + (1 - yte) * np.log(1 - p))))


def _screen_job(job):
    from interpret.glassbox import ExplainableBoostingClassifier as EBC, ExplainableBoostingRegressor as EBR
    reg, xtr, ytr, btr, xte, yte, bte = job
    kw = dict(max_bins=16, outer_bags=2, min_samples_leaf=20 if not reg else 8, max_rounds=200, interactions=0, random_state=7)
    m = (EBR if reg else EBC)(**kw)
    ok = ~np.isnan(xtr)
    if ok.sum() < 30: return None
    m.fit(xtr.reshape(-1, 1), ytr, init_score=btr)
    if reg: p = m.predict(xte.reshape(-1, 1), init_score=bte)
    else: p = m.predict_proba(xte.reshape(-1, 1), init_score=bte)[:, 1]
    return _loss(reg, yte, p)


def run_node(node, ids=None):
    import parallel, learnednodes as LN
    from sklearn.model_selection import GroupKFold
    ids = ids or _ids()
    df, X, y, g, C = frame(node, ids)
    reg = node in LN.REGRESSION
    yv = y.values.astype(float)
    folds = list(GroupKFold(n_splits=6).split(X, y, g))
    # the node's current model per fold: its readings on train and test rows (the starting score for the screen)
    jobs = [("full", reg, g.iloc[tr].nunique(), X.iloc[tr], y.iloc[tr].values, None, None, node) for tr, te in folds]
    base_models = parallel.run(LN._job, jobs)
    def score(e, Xp):
        inner = getattr(e, "inner", e)
        if reg: return np.asarray(e.predict(Xp), float)
        p = np.clip(e.predict_proba(Xp)[:, 1], 1e-4, 1 - 1e-4); return np.log(p / (1 - p))
    base_tr = [score(e, X.iloc[tr]) for e, (tr, te) in zip(base_models, folds)]
    base_te = [score(e, X.iloc[te]) for e, (tr, te) in zip(base_models, folds)]
    base_loss = [_loss(reg, yv[te], (b if reg else 1 / (1 + np.exp(-b)))) for b, (tr, te) in zip(base_te, folds)]
    # 1. screen every candidate
    sj, owner = [], []
    for c in C.columns:
        col = C[c].values
        for k, (tr, te) in enumerate(folds):
            sj.append((reg, col[tr], yv[tr], base_tr[k], col[te], yv[te], base_te[k])); owner.append((c, k))
    res = parallel.run(_screen_job, sj)
    by = collections.defaultdict(dict)
    for (c, k), r in zip(owner, res):
        if r is not None: by[c][k] = base_loss[k] - r
    screen = []
    for c, d in by.items():
        if len(d) < 4: continue
        v = list(d.values()); mu = statistics.mean(v); se = statistics.stdev(v) / math.sqrt(len(v))
        screen.append({"variable": c, "gain": round(mu, 5), "plus_minus": round(se, 5), "folds_up": sum(1 for x in v if x > 0),
                       "present": round(float(C[c].notna().mean()), 2)})
    screen.sort(key=lambda x: -(x["gain"] - x["plus_minus"]))
    # 2. confirm the best
    top = [x for x in screen if x["gain"] > 0][:SCREEN_KEEP]
    cj, cown = [], []
    for x in top:
        c = x["variable"]; X2 = X.copy(); X2[c] = C[c]
        for k, (tr, te) in enumerate(folds):
            cj.append(("fold", reg, g.iloc[tr].nunique(), X2.iloc[tr], y.iloc[tr].values, X2.iloc[te], y.iloc[te].values, node)); cown.append((c, k))
    for k, (tr, te) in enumerate(folds):
        cj.append(("fold", reg, g.iloc[tr].nunique(), X.iloc[tr], y.iloc[tr].values, X.iloc[te], y.iloc[te].values, node)); cown.append(("__base__", k))
    cres = parallel.run(LN._job, cj)
    sc = collections.defaultdict(dict)
    for (c, k), r in zip(cown, cres): sc[c][k] = r["score"]
    confirmed = []
    for x in top:
        c = x["variable"]
        d = [sc["__base__"][k] - sc[c][k] for k in range(len(folds))]
        mu = statistics.mean(d); se = statistics.stdev(d) / math.sqrt(len(d)); up = sum(1 for v in d if v > 0)
        status = "discovery (held for Denning)" if mu - 2 * se > 0 and up >= 5 else ("against" if mu + 2 * se < 0 else "not clear yet")
        # which way it leans: the share of the node's result in the variable's lowest and highest thirds
        col = C[c]; q1, q2 = col.quantile([1 / 3, 2 / 3])
        lo, hi = y[col <= q1].mean(), y[col > q2].mean()
        confirmed.append({**x, "confirm_gain": round(mu, 5), "confirm_plus_minus": round(se, 5), "confirm_folds_up": up, "status": status,
                          "result_low_third": round(float(lo), 3), "result_high_third": round(float(hi), 3),
                          "cut_low": round(float(q1), 2), "cut_high": round(float(q2), 2)})
    out = {"node": node, "target": LN.SPEC[node][0], "matches": int(g.nunique()), "rows": int(len(y)),
           "metric": "mean absolute error (s)" if reg else "log loss", "tested": len(screen),
           "screen_passed": sum(1 for x in screen if x["gain"] - 2 * x["plus_minus"] > 0),
           "screen": screen[:25], "confirmed": confirmed}
    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump(out, open(os.path.join(OUT_DIR, f"{node}.json"), "w"), indent=1)
    return out


def join():
    import learnednodes as LN
    rows = []
    for f in sorted(glob.glob(os.path.join(OUT_DIR, "*.json"))):
        rows.append(json.load(open(f)))
    # R-286 (Denning): own_ and diff_ variables are offered; enemy_ variables are the enemy's concurrent response and are
    # never offered, but the matching enemy_ reading is shown beside an offered candidate as "what the enemy did"
    passed = [dict(c, node=r["node"], target=r["target"]) for r in rows for c in r["confirmed"]
              if c["status"].startswith("discovery") and not c["variable"].startswith("p.enemy_")]
    enemy_side = {(r["node"], c["variable"]): c for r in rows for c in r["confirmed"] if c["variable"].startswith("p.enemy_")}
    def beside(d):
        base = d["variable"].split("_", 1)[1] if d["variable"].startswith(("p.own_", "p.diff_")) else None
        # own_<line>_<thing>: the enemy counterpart is the team-level enemy_<thing>
        e = enemy_side.get((d["node"], f"p.enemy_{base}")) if base else None
        if e is None and base:
            parts = base.split("_", 1)
            if len(parts) == 2: e = enemy_side.get((d["node"], f"p.enemy_{parts[1]}"))
        return f"{e['variable']} {e['confirm_gain']:+.4f} ({e['status']})" if e else "did not pass the screen"
    tested = sum(r["tested"] for r in rows)
    # the two-run rule: a pass is recorded; a candidate is offered once it has passed in two runs
    import datetime
    today = datetime.date.today().isoformat()
    try: hist = json.load(open(HISTORY))
    except (OSError, ValueError): hist = {}
    run_key = f"{today}:{max((r['matches'] for r in rows), default=0)}"
    for d in passed:
        k = f"{d['node']}|{d['variable']}"
        h = hist.setdefault(k, {"passes": []})
        if run_key not in h["passes"]: h["passes"].append(run_key)
    json.dump(hist, open(HISTORY, "w"), indent=1)
    found, once = [], []
    for d in passed:
        n = len(hist[f"{d['node']}|{d['variable']}"]["passes"])
        (found if n >= 2 else once).append(dict(d, passes=n))
    json.dump({"about": "Step 3 discovery (discover.py): the variable catalogue (play variables) against every learned node, held "
                        "out by match. A candidate is offered after passing in two runs; none is in the model until Denning approves.",
               "tested": tested, "nodes": rows, "discoveries": found, "passed_once": once, "held": found,
               "enemy_side": [dict(c, node=n) for (n, v), c in sorted(enemy_side.items())]},
              open(os.path.join(REPO, "data", "model", "discovery.json"), "w"), indent=1)
    L = ["# What discovery found", "",
         "Step 3 of the learned causal map (`discover.py`): the variable catalogue (`catalogue.py`: what each team did in the 10 s "
         "and 30 s before a moment, generated from the replay schema; decision and execution variables only) tested against "
         "every learned node on matches the node never saw. A **pass** predicts what the node misses by more than twice its "
         "spread, in at least 5 of 6 held-out folds. A candidate is **offered** to Denning once it has passed in two runs (the "
         "two-run rule): approve (it becomes a link in the causal map and an input of the node), reject, or wait. Only what "
         "the team itself did (own_, and own minus enemy as diff_) is offered; the enemy's side of the same measure (enemy_) is the "
         "enemy's concurrent response, never advice, and is shown beside a candidate as what the enemy did (Denning, R-286).", "",
         f"Variables tested: {tested} (variable by node); {sum(r['screen_passed'] for r in rows)} passed the screen, where chance alone "
         f"would pass about {round(tested * 0.023)} (2.3% at twice the spread). Treat a candidate as a lead.", ""]
    if found:
        L += ["## Offered (passed in two runs)", "",
              "| Node | Variable | Gain on unseen matches | Folds up | Result, lowest third -> highest third | What the enemy did (enemy_ side) |", "|---|---|---|---|---|---|"]
        for d in sorted(found, key=lambda d: -d["confirm_gain"]):
            L.append(f"| {d['node'].replace('_', ' ')} | {d['variable']} | {d['confirm_gain']:+.4f} (+/- {d['confirm_plus_minus']:.4f}) | "
                     f"{d['confirm_folds_up']} of 6 | {d['result_low_third']} (at or below {d['cut_low']:g}) -> {d['result_high_third']} (above {d['cut_high']:g}) | {beside(d)} |")
    else:
        L.append("Nothing offered yet (no candidate has passed in two runs).")
    if once:
        L += ["", "## Passed once (waits for a second run)", ""]
        for d in sorted(once, key=lambda d: -d["confirm_gain"]):
            L.append(f"- {d['node'].replace('_', ' ')}: {d['variable']} {d['confirm_gain']:+.4f} (+/- {d['confirm_plus_minus']:.4f}), {d['confirm_folds_up']} of 6 folds up; the enemy's side: {beside(d)}")
    es = sorted((c for c in enemy_side.values() if c["status"].startswith("discovery")), key=lambda c: -c["confirm_gain"])
    if es:
        L += ["", "## The enemy's side (passed, never offered: concurrent response)", ""]
        for c in es[:12]:
            L.append(f"- {c['variable']} {c['confirm_gain']:+.4f} (+/- {c['confirm_plus_minus']:.4f})")
    L += ["", "## Per node", ""]
    for r in rows:
        L.append(f"**{r['node'].replace('_', ' ')}** ({r['target']}; {r['matches']} matches, {r['rows']} rows, {r['metric']}): "
                 f"{r['tested']} variables screened, {r['screen_passed']} passed the screen")
        for c in r["confirmed"]:
            L.append(f"- {c['variable']}: screen {c['gain']:+.4f}, confirmed {c['confirm_gain']:+.4f} (+/- {c['confirm_plus_minus']:.4f}, "
                     f"{c['confirm_folds_up']} of 6 folds up): {c['status']}")
        L.append("")
    open(os.path.join(REPO, "knowledge", "discovery.md"), "w").write("\n".join(L) + "\n")
    return found


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["node"]:
        r = run_node(a[1]); print(a[1], r["tested"], "tested,", sum(1 for c in r["confirmed"] if c["status"].startswith("discovery")), "discoveries")
    elif a[:1] == ["join"]:
        for d in join(): print(d["node"], d["variable"], d["confirm_gain"])
    elif a[:1] == ["all"]:
        import learnednodes as LN
        for n in LN.SPEC: run_node(n)
        join()
    else: print(__doc__)
