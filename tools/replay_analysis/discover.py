"""Step 3 of the learned causal map: discovery (Denning: discovery of unknown variables and interactions matters most).
Every measured variable is tested against every learned node on matches the node never saw; what holds up is held
for Denning's approval as a new link, never added to the model automatically.

The variables: everything the engine measures about a team at a moment, joined to each node row at its time (the
same team, the 5 s state at or before the row): the win model's state table (flag lead, numbers, morale, pit NPCs,
Lord damage and health, res timer, fight state, carriers, splits, turtling, footmen, map geometry, flux ...; prefix
"s.") and the build and matchup features (counts from the skill data, threat against answer pairs, and snare, speed
and escape power; prefix "b."). Variables already in the node are skipped.

The test, in two stages (both held out by match, the node's own 6 folds):
  1. Screen: the node's current model is fitted on the training folds; a one-variable glass-box curve is then fitted on
     top of its readings (starting from them) and scored on the held-out fold. Gain = held-out loss without minus with
     (positive = the variable predicts what the node misses). Cheap, so every variable gets it.
  2. Confirm: the best SCREEN_KEEP variables per node that gained on the screen are refitted properly (the node's
     variables plus the new one, the same fits as a link test) against the node without it, on the same folds.
     A discovery = confirmed gain more than twice its spread and positive in at least 5 of 6 folds.
Many variables are tested, so some chance winners are expected: a discovery is a lead for Denning to rule on (approve
as a link, reject, or wait for more matches), and the report says how many would pass by chance.

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


def panel(rid):
    """{(team, t): {variable: value}} every 5 s: the state table plus the team's build features."""
    import model as M
    from replaylib import Match
    from buildfeat import matchup
    import movepower as MP
    m = Match.from_branch(rid)
    P = MP.powers(m)
    build = {}
    for tm in (1, 2):
        b = {f"b.{k}": v for k, v in matchup(m, tm).items()}
        for side, k in (("own", tm), ("enemy", 3 - tm)):
            for kind in ("snare", "speed", "escapes"):
                b[f"b.{side}_{kind}_power"] = round(sum(P[a][kind] for a in m.PL if m.team(a) == k), 1)
        build[m.tag[tm]] = b
    out = {}
    for r in M.match_table(rid):
        v = {f"s.{k}": x for k, x in r.items() if k not in SKIP and isinstance(x, (int, float)) and not isinstance(x, bool)}
        v.update(build.get(r["team"], {}))
        out[(r["team"], int(r["t"]))] = v
    return out


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
    found = [dict(c, node=r["node"], target=r["target"]) for r in rows for c in r["confirmed"] if c["status"].startswith("discovery")]
    tested = sum(r["tested"] for r in rows)
    json.dump({"about": "Step 3 discovery (discover.py): every measured variable against every learned node, held out by match. "
                        "Discoveries are held for Denning's approval; none is in the model until he approves.",
               "tested": tested, "nodes": rows, "discoveries": found}, open(os.path.join(REPO, "data", "model", "discovery.json"), "w"), indent=1)
    L = ["# What discovery found", "",
         "Step 3 of the learned causal map (`discover.py`): every variable the engine measures about a team at a moment (the "
         "state table, prefix s., and the build and matchup features, prefix b.) tested against every learned node on matches "
         "the node never saw. A **discovery** predicts what the node misses by more than twice its spread, in at least 5 of 6 "
         "held-out folds. Each is held for Denning's approval: approve (it becomes a link in the causal map and a variable in the "
         "node), reject, or wait for more matches.", "",
         f"Variables tested: {tested} (variable by node); {sum(r['screen_passed'] for r in rows)} passed the screen, where chance alone "
         f"would pass about {round(tested * 0.023)} (2.3% at twice the spread). Treat a discovery as a lead.", ""]
    if found:
        L += ["| Node | Variable | Gain on unseen matches | Folds up | Result, lowest third -> highest third |", "|---|---|---|---|---|"]
        for d in sorted(found, key=lambda d: -d["confirm_gain"]):
            L.append(f"| {d['node'].replace('_', ' ')} | {d['variable']} | {d['confirm_gain']:+.4f} (+/- {d['confirm_plus_minus']:.4f}) | "
                     f"{d['confirm_folds_up']} of 6 | {d['result_low_third']} (at or below {d['cut_low']:g}) -> {d['result_high_third']} (above {d['cut_high']:g}) |")
    else:
        L.append("No discoveries yet.")
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
