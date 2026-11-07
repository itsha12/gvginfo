"""The win-probability model: glass box, trained a few matches at a time, readable and amendable.

Model: an Explainable Boosting Machine (`interpret`). The starting point is team strength alone (the fitted rating gap
from every stored result, 400 points = 10 to 1 odds); the model then learns what the game state adds or subtracts:
win chance = strength + one learned curve per variable + learned two-variable tables (interactions).
Complexity grows with the data (STAGES): build variables (fixed for a whole match, which with few matches only
fingerprint matches) from 60 matches, interactions from 40. Training rows every 15 s (nearby seconds repeat each
other). Few boosting rounds, since the library's internal stopping test can't hold out whole matches. Everything it learns is written to data/model/wp_model.json (curves,
tables, importance, uncertainty) and data/model/wp_model.md (the same in words, for Denning).

Corrections: data/model_corrections.json, a list of {"term", "kind", "reason", ...} that Denning can edit:
  {"term": "knights_own", "kind": "direction", "increasing": true, "reason": "..."}   curve can only rise (or fall)
  {"term": "boost_clock", "kind": "drop", "reason": "..."}                            variable not used
  {"term": "flag_lead & minute", "kind": "interaction", "reason": "..."}              always offer this pair
  {"term": "lord_damage_diff", "kind": "cap", "max_points": 15, "reason": "..."}      effect limited to +-15 points
Every fit reports held-out accuracy with and without the corrections, so a correction is tested, not trusted.

Validation: matches are held out whole (never the same match in training and test). Compared with team strength alone
and with a black-box model (gradient boosting) on the same data, so the cost of readability is measured.

Usage:  python3 model.py fit [--matches FILE]        fit on the matches in data/model/batches.json (or a list file)
        python3 model.py explain <report id> <m:ss>  breakdown of both teams' win chance at that moment, from a model
                                                     fitted without that match (it never saw the result)
In code: WPModel.load_or_fit(); wp.explain(row) -> (win chance, [(term, points), ...])."""
import collections, itertools, json, math, os, subprocess, sys, warnings
import numpy as np
warnings.filterwarnings("ignore")
from common import REPO
from features import VARIABLES, CANDIDATES, DESCRIPTIONS

MODEL_DIR = os.path.join(REPO, "data", "model")
CORR = os.path.join(REPO, "data", "model_corrections.json")
STATIC = {"strength_gap", "lord_dps_own", "lord_dps_enemy", "healing_monks_own", "healing_monks_enemy",
          "spike_build_own", "spike_build_enemy", "map_flag_run", "map_pit_to_stand", "map_bases_apart",
          "flux_minion_apocalypse", "flux_meek_shall_inherit", "flux_jack_of_all_trades", "flux_chain_combo"}       # fixed for a whole match
NAMES = [n for n, _, _ in VARIABLES]
STAGES = {"build_variables": 60, "interactions": 40}   # matches needed before these are switched on
TRAIN_STEP = 15
EVEN_GAP = 200               # "even on strength": under this many rating points apart (about 1.3 to 1 odds)
SETTINGS = dict(max_bins=16, outer_bags=4, min_samples_leaf=20, max_rounds=300, random_state=7)


def strength_score(X):
    """Log odds from the team strength gap alone (Bradley-Terry scale: 400 points = 10 to 1)."""
    return (X["strength_gap"].fillna(0) * math.log(10) / 400).values


def terms_for(n_matches, names=NAMES):
    """The variables the model may use at this many matches (strength is the baseline, not a term)."""
    out = [n for n in names if n != "strength_gap" and (n in NAMES or n in {c for c, _, _ in CANDIDATES})]
    if n_matches < STAGES["build_variables"]: out = [n for n in out if n not in STATIC]
    return out


def sig(x): return 1 / (1 + math.exp(-x))


_TABLES = {}
def match_table(rid):
    """The match table for one replay (shared cache, cache.py: keyed by the engine code and by the fight-state
    predictions it reads, so it is rebuilt only when either changes)."""
    import cache, fightstate
    key = fightstate.version(rid)
    if (rid, key) not in _TABLES:
        def build():
            from replaylib import Match
            from state import GameState
            from scoreboard import Scoreboard
            from features import table
            from strength import strength_gap
            st = GameState(Match.from_branch(rid)); sb = Scoreboard(st)
            return table(st, sb, strength_gap)
        _TABLES[(rid, key)] = cache.prepared("table", rid, build, sub=key)
    return _TABLES[(rid, key)]


def batches():
    p = os.path.join(MODEL_DIR, "batches.json")
    return json.load(open(p))["batches"] if os.path.exists(p) else []


def corrections():
    try: return json.load(open(CORR))["corrections"]
    except (OSError, ValueError, KeyError): return []


def _frame(ids, step=TRAIN_STEP, extra=()):
    import pandas as pd
    from integrity import usable
    ids = usable(list(ids))
    rows = [r for rid in ids for r in match_table(rid) if r["won"] is not None and r["t"] % step == 0]
    df = pd.DataFrame(rows)
    return df, df[NAMES + list(extra)].astype(float), df["won"].astype(int), df["match"]


def _validate_candidate(args):
    df, X, y, g, corr, n = args
    return validate(df, X[NAMES + ([n] if n else [])], y, g, corr, extra=[n] if n else [])[0]


def test_candidates(ids):
    """Held-out log loss with each candidate variable added, against the model without it."""
    corr = corrections()
    df, X, y, g = _frame(ids, extra=[n for n, _, _ in CANDIDATES])
    import multiprocessing as mp
    jobs = [None] + [n for n, _, _ in CANDIDATES if n in X]
    # each validation is independent: run them side by side, in fresh processes ("spawn"): forked workers deadlock once
    # the parent has used the model library's threads (found 2026-11-06)
    with mp.get_context("spawn").Pool(min(len(jobs), os.cpu_count() or 2)) as p:
        res = dict(zip(jobs, p.map(_validate_candidate, [(df, X, y, g, corr, n) for n in jobs])))
    base = res[None]
    out = []
    for n, dsc, _ in CANDIDATES:
        if n not in res: continue
        v = res[n]
        out.append({"candidate": n, "description": dsc, "without": base["glass box"]["all"]["log_loss"],
                    "with": v["glass box"]["all"]["log_loss"],
                    "verdict": "improves: ready to move into the model" if v["glass box"]["all"]["log_loss"] < base["glass box"]["all"]["log_loss"] - 0.005
                    else "does not improve yet"})
    return out


def _ebm(corr, names, n_matches):
    from interpret.glassbox import ExplainableBoostingClassifier as EBM
    drop = {c["term"] for c in corr if c["kind"] == "drop"}
    use = [n for n in terms_for(n_matches, names) if n not in drop]
    static_pairs = [(a, b) for a, b in itertools.combinations(use, 2) if a in STATIC and b in STATIC]
    forced = [tuple(c["term"].split(" & ")) for c in corr if c["kind"] == "interaction"]
    kw = dict(SETTINGS, interactions=8 if n_matches >= STAGES["interactions"] else 0)
    if static_pairs and kw["interactions"]: kw["exclude"] = static_pairs
    return EBM(feature_names=use, **kw), use, forced


def _apply(ebm, corr):
    """Directions and caps applied to a fitted model (drops and forced interactions act at fit time)."""
    names = list(ebm.term_names_)
    for c in corr:
        if c["term"] not in names: continue
        i = names.index(c["term"])
        if c["kind"] == "direction":
            ebm.monotonize(i, increasing=bool(c.get("increasing", True)))
        elif c["kind"] == "cap":
            lim = math.log((50 + c["max_points"]) / (50 - c["max_points"]))     # points at 50% -> log odds
            ebm.term_scores_[i] = np.clip(ebm.term_scores_[i], -lim, lim)
    return ebm


def _fit(X, y, corr, n_matches):
    ebm, use, forced = _ebm(corr, list(X.columns), n_matches)
    init = strength_score(X)
    ebm.fit(X[use], y, init_score=init)
    chosen = [tuple(use[f] for f in tf) for tf in ebm.term_features_ if len(tf) == 2]
    missing = [p for p in forced if p not in chosen and p[::-1] not in chosen and all(x in use for x in p)]
    if missing:     # Denning asked for these pairs: refit with the chosen pairs plus his
        from interpret.glassbox import ExplainableBoostingClassifier as EBM
        kw = dict(SETTINGS); kw["interactions"] = [tuple(use.index(x) for x in p) for p in chosen + missing]
        ebm = EBM(feature_names=use, **kw).fit(X[use], y, init_score=init)
    return _apply(ebm, corr), use


def _predict(ebm, use, X):
    return 1 / (1 + np.exp(-(ebm.decision_function(X[use]) + strength_score(X))))


def _metrics(p, y):
    p = np.clip(p, 0.02, 0.98)
    return {"log_loss": round(float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))), 3),
            "accuracy": round(float(np.mean((p > 0.5) == (y == 1))), 3),
            "brier": round(float(np.mean((p - y) ** 2)), 3)}


def _validate_fold(job):
    """One held-out fold of the win model's honest test (top level so it can run in another process)."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    Xtr, ytr, Xte, corr, n_tr = job
    out = {}
    m1, use = _fit(Xtr, ytr, corr, n_tr); out["glass box"] = _predict(m1, use, Xte)
    if corr:
        m0, use0 = _fit(Xtr, ytr, [], n_tr); out["glass box without corrections"] = _predict(m0, use0, Xte)
    bb = HistGradientBoostingClassifier(max_iter=200, random_state=7).fit(Xtr.fillna(-999), ytr)
    out["black box"] = bb.predict_proba(Xte.fillna(-999))[:, 1]
    return out


def validate(df, X, y, groups, corr, extra=()):
    """Held-out comparison (matches held out whole): team strength alone, the glass box with and without corrections,
    and a black box given the same variables."""
    from sklearn.model_selection import GroupKFold
    from sklearn.ensemble import HistGradientBoostingClassifier
    import parallel
    k = min(6, groups.nunique())
    preds = {n: np.zeros(len(y)) for n in ("strength only", "glass box", "glass box without corrections", "black box")}
    folds = list(GroupKFold(n_splits=k).split(X, y, groups))
    # every fold's fits are independent: side by side on all cores (parallel.py), same results as one after another
    res = parallel.run(_validate_fold, [(X.iloc[tr], y.iloc[tr], X.iloc[te], corr, groups.iloc[tr].nunique()) for tr, te in folds])
    for (tr, te), r in zip(folds, res):
        preds["strength only"][te] = 1 / (1 + np.exp(-strength_score(X.iloc[te])))
        for n, v in r.items(): preds[n][te] = v
    if not corr: preds.pop("glass box without corrections")
    out = {}
    for n, p in preds.items():
        out[n] = {"all": _metrics(p, y.values)}
        for lo, hi in ((0, 5), (5, 10), (10, 15), (15, 99)):
            sel = (df["minute"] >= lo) & (df["minute"] < hi)
            if sel.sum(): out[n][f"{lo}-{hi if hi < 99 else 'end'} min"] = _metrics(p[sel.values], y.values[sel.values])
    # the matches that matter most for play: those that last (reach 15:00) and those even on strength
    length = df.groupby("match")["t"].transform("max")
    subsets = {"matches lasting 15 min+": (length >= 900).values,
               f"matches even on strength (gap under {EVEN_GAP})": (df["strength_gap"].abs().fillna(0) < EVEN_GAP).values}
    for n, p in preds.items():
        for name, sel in subsets.items():
            if sel.sum(): out[n][name] = dict(_metrics(p[sel], y.values[sel]), matches=int(df["match"][sel].nunique()))
    g, s0 = out["glass box"]["all"], out["strength only"]["all"]
    # how sure: the glass box's log loss gain over strength alone, resampling whole matches (90% range)
    lossg = -(y.values * np.log(np.clip(preds["glass box"], .02, .98)) + (1 - y.values) * np.log(1 - np.clip(preds["glass box"], .02, .98)))
    losss = -(y.values * np.log(np.clip(preds["strength only"], .02, .98)) + (1 - y.values) * np.log(1 - np.clip(preds["strength only"], .02, .98)))
    gain = collections.defaultdict(list)
    for mm, a, b in zip(groups.values, losss, lossg): gain[mm].append(a - b)
    ms = list(gain); rnd = np.random.RandomState(7); boots = []
    for _ in range(500):
        pick = rnd.choice(len(ms), len(ms))
        vals = [v for i in pick for v in gain[ms[i]]]
        boots.append(float(np.mean(vals)))
    lo, hi = np.percentile(boots, [5, 95])
    out["gain_over_strength"] = {"log_loss_gain": round(float(np.mean(losss - lossg)), 3), "range_90": [round(float(lo), 3), round(float(hi), 3)]}
    out["verdict"] = ("beats strength alone" + (" (clear: the range excludes 0)" if lo > 0 else " (not yet clear: the range includes 0)")
                      if g["log_loss"] < s0["log_loss"] - 0.005 else
                      "not yet better than strength alone: treat the curves as noise")
    return out, preds["glass box"]


def _points(score):
    """A contribution in log odds shown as win-chance points for an otherwise even (50%) game."""
    return round((sig(score) - 0.5) * 100, 1)


def readable(ebm, use, X):
    """Every learned curve and table, in plain numbers."""
    terms = []
    imp = ebm.term_importances()
    for i, name in enumerate(ebm.term_names_):
        feats = ebm.term_features_[i]
        sc = ebm.term_scores_[i]; sd = ebm.standard_deviations_[i]
        if len(feats) == 1:
            f = feats[0]; edges = list(ebm.bins_[f][0]) if len(ebm.bins_[f]) else []
            col = X[use[f]].dropna()
            lo, hi = (float(col.min()), float(col.max())) if len(col) else (None, None)
            bounds = [lo] + [float(e) for e in edges] + [hi]
            curve = [{"from": round(bounds[j], 2) if bounds[j] is not None else None,
                      "to": round(bounds[j + 1], 2) if bounds[j + 1] is not None else None,
                      "points": _points(sc[j + 1]), "plus_minus": round(float(sd[j + 1]) * 25, 1)}
                     for j in range(len(bounds) - 1)]
            terms.append({"term": name, "description": DESCRIPTIONS.get(name, ""), "importance": round(float(imp[i]), 3),
                          "missing_points": _points(sc[0]), "curve": curve})
        else:
            a, b = feats
            ea = [float(e) for e in (ebm.bins_[a][-1] if len(ebm.bins_[a]) else [])]
            eb = [float(e) for e in (ebm.bins_[b][-1] if len(ebm.bins_[b]) else [])]
            table = [[_points(sc[r + 1][c + 1]) for c in range(len(eb) + 1)] for r in range(len(ea) + 1)]
            terms.append({"term": name, "description": f"{DESCRIPTIONS.get(use[a], '')} TOGETHER WITH {DESCRIPTIONS.get(use[b], '')}",
                          "importance": round(float(imp[i]), 3), "rows": f"{use[a]} cut at {[round(e, 1) for e in ea]}",
                          "columns": f"{use[b]} cut at {[round(e, 1) for e in eb]}", "table_points": table})
    return sorted(terms, key=lambda t: -t["importance"])


class WPModel:
    def __init__(self, ebm, use):
        self.ebm, self.use = ebm, use

    @classmethod
    def fit_on(cls, ids):
        df, X, y, g = _frame(ids)
        ebm, use = _fit(X, y, corrections(), g.nunique())
        return cls(ebm, use)

    @classmethod
    def heldout(cls, ids, rid):
        """The win model fitted on ids without rid (a model that never saw that match), fitted once per training set
        and reused by every layer (cache.py)."""
        import cache
        return cache.heldout("wp", rid, list(ids), cls.fit_on)

    @classmethod
    def load_or_fit(cls):
        ids = [m for b in batches() for m in b["matches"]]
        return cls.fit_on(ids)

    def explain(self, row):
        """Win chance, and each term's contribution in points for an otherwise even (50%) game: the same scale as the
        curves in wp_model.md, readable even when the chance is near 0 or 100%."""
        import pandas as pd
        x = pd.DataFrame([{n: row.get(n) for n in self.use + ["strength_gap"]}]).astype(float)
        contrib = list(self.ebm.eval_terms(x[self.use])[0])
        strength = float(strength_score(x)[0])
        total = float(np.ravel(self.ebm.intercept_)[0]) + strength + float(sum(contrib))
        parts = [("team strength", _points(strength))] + [(self.ebm.term_names_[i], _points(c)) for i, c in enumerate(contrib)]
        return round(sig(total) * 100, 1), sorted([x for x in parts if abs(x[1]) >= 0.5], key=lambda kv: -abs(kv[1]))


def write_md(model):
    """The model in words: wp_model.md."""
    L = [f"# Win-probability model (batch {model['batch']}, {model['matches']} matches)", "",
         "Every number is win-chance points for an otherwise even game (50%), learned from the matches so far; "
         "\"+-\" is the uncertainty across bags. Few matches = rough curves.", "",
         "## How well it predicts (matches held out whole)", ""]
    L.append(f"**Verdict: {model['validation']['verdict']}.** Team strength alone is the baseline; the curves below are "
             "what the game state adds to it.")
    L.append("")
    if "gain_over_strength" in model["validation"]:
        gs = model["validation"]["gain_over_strength"]
        L.append(f"Gain over strength alone (log loss, resampling whole matches): {gs['log_loss_gain']:+}, 90% range "
                 f"{gs['range_90'][0]:+} to {gs['range_90'][1]:+}.")
        L.append("")
    for n, v in model["validation"].items():
        if n in ("verdict", "gain_over_strength"): continue
        L.append(f"- {n}: accuracy {v['all']['accuracy']:.0%}, log loss {v['all']['log_loss']} "
                 f"({'; '.join(f'{k} {vv['accuracy']:.0%}' for k, vv in v.items() if k != 'all')})")
    L += ["", "## What it learned, most important first", ""]
    for t in model["terms"]:
        L.append(f"### {t['term']} (importance {t['importance']})")
        L.append(t["description"])
        if "curve" in t:
            pts = [c for c in t["curve"] if c["from"] is not None]
            if pts:
                step = max(1, len(pts) // 8)
                L.append("; ".join(f"{c['from']} to {c['to']}: {c['points']:+} (+-{c['plus_minus']})" for c in pts[::step]))
        else:
            L.append(f"Rows: {t['rows']}. Columns: {t['columns']}.")
            for r in t["table_points"]: L.append("    " + "  ".join(f"{v:+6.1f}" for v in r))
        L.append("")
    if model["corrections"]:
        L += ["## Corrections applied", ""] + [f"- {c['term']}: {c['kind']} ({c.get('reason', '')})" for c in model["corrections"]]
    txt = "\n".join(L) + "\n"
    open(os.path.join(MODEL_DIR, "wp_model.md"), "w").write(txt)
    note = ("*Generated by tools/replay_analysis/model.py after each training batch: don't edit this page. To correct the "
            "model, tell Claude or add a correction to data/model_corrections.json (it is logged and tested).*\n\n")
    open(os.path.join(REPO, "knowledge", "wp-model.md"), "w").write(note + txt)


def fit_and_save(ids, batch):
    df, X, y, g = _frame(ids)
    corr = corrections()
    val, held = validate(df, X, y, g, corr)
    ebm, use = _fit(X, y, corr, g.nunique())
    model = {"format": "gvginfo.wp_model.v1", "batch": batch, "matches": int(g.nunique()), "rows": int(len(y)),
             "settings": SETTINGS, "stages": STAGES, "variables_in_use": use, "corrections": corr, "validation": val,
             "intercept_points": _points(float(np.ravel(ebm.intercept_)[0])), "terms": readable(ebm, use, X)}
    os.makedirs(MODEL_DIR, exist_ok=True)
    json.dump(model, open(os.path.join(MODEL_DIR, "wp_model.json"), "w"), indent=1)
    write_md(model)
    return model, WPModel(ebm, use), df, held, X, y


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "explain":
        rid, clock = args[1], args[2]
        t = int(clock.split(":")[0]) * 60 + int(clock.split(":")[1]); t -= t % 5
        wp = WPModel.fit_on([m for b in batches() for m in b["matches"] if m != rid])
        for r in match_table(rid):
            if r["t"] == t:
                p, parts = wp.explain(r)
                print(f"{r['team']}: {p}% |", ", ".join(f"{n} {v:+}" for n, v in parts[:10]))
    else:
        ids = [m for b in batches() for m in b["matches"]]
        model, wp, df, held, X, y = fit_and_save(ids, len(batches()) - 1)
        print(json.dumps(model["validation"], indent=1)[:2000])
        print([(t["term"], t["importance"]) for t in model["terms"][:12]])
