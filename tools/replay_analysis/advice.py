"""Does the advice work? The goal test (Denning, November 2026 review, P2; docs/SPEC.md section 1).

For every decision kind: the matches are split into 6 groups; for each group the advice is built from the other five
only (so the test matches are unseen), then read on the test group: did teams whose choice matched the advice do
better than teams whose choice didn't, in win-chance change over the decision's window, adjusted for the situation?

The advice for a decision = among the K most similar decisions in the training groups (usual.py's similarity: the
situation, build axes and map), the choice with the best mean win-chance change, if it has MIN_CASES cases among
them and beats the most common choice there by MARGIN points; otherwise the usual play (the most common choice).
"Matched" = the team chose what the advice says. The effect = the adjusted difference in win-chance change between
matched and unmatched decisions (a regression on the situation plus a matched flag, like usual.py's choice effects),
with a 90% range from resampling whole matches. A kind passes when the range excludes 0 and the effect is positive.

The second reading, "the blind test", is set up here and scored by hand: ten sealed moments (data/model/blind_test.json)
where Denning's call and the model's are both recorded before the outcome is read; the outcome then scores both.

Usage: python3 advice.py            (reads the decision records usual.py builds; prints the table)
In code: advice_test(recs) -> {kind: {...}}; lines(res) -> report lines. Report layer: no cache key."""
import collections, json, os, random, sys
import numpy as np
from common import REPO

K = 15
MIN_CASES = 5
MARGIN = 2.0
FOLDS = 6
BOOT = 200
OUT = os.path.join(REPO, "data", "model", "advice_test.json")


def _prep(recs, kind):
    import usual as U
    L = [r for r in recs if r["kind"] == kind and "wp_change" in r]
    for r in L:
        r["choice2"] = U.refine(r); r["sit"] = U.situation(r, r.get("gap"))
    counts = collections.Counter(r["choice2"] for r in L)
    choices = [c for c, n in counts.most_common() if n >= MIN_CASES]
    L = [r for r in L if r["choice2"] in choices]
    if len(L) < 40 or len(choices) < 2: return None
    build_cols = [f"{side}_{a}" for side in ("own", "enemy") for a in U.AXES]
    nb_cols = U.SIT + U.SIT_EXTRA.get(kind, []) + build_cols + U.MAP_COLS
    adj_cols = U.SIT + U.SIT_EXTRA.get(kind, [])
    XN = np.array([[r["sit"][k] for k in nb_cols] for r in L], float)
    ZN = (XN - XN.mean(0)) / (XN.std(0) + 1e-9)
    XA = np.array([[r["sit"][k] for k in adj_cols] for r in L], float)
    ZA = (XA - XA.mean(0)) / (XA.std(0) + 1e-9)
    y = np.array([r["wp_change"] for r in L], float)
    return L, choices, ZN, ZA, y


def _fold_of(match):
    import cache
    return cache.fold_of(match, FOLDS)


def advise(i, train_idx, L, ZN, y):
    """The advice for decision i from the training decisions: (recommended choice, usual choice, cases behind it)."""
    d = np.sqrt(((ZN[train_idx] - ZN[i]) ** 2).sum(1))
    near = [train_idx[j] for j in np.argsort(d)[:K]]
    by = collections.defaultdict(list)
    for j in near: by[L[j]["choice2"]].append(y[j])
    usual = max(by.items(), key=lambda kv: len(kv[1]))[0]
    best, bval = usual, float(np.mean(by[usual]))
    for c, v in by.items():
        if len(v) >= MIN_CASES and float(np.mean(v)) >= bval + MARGIN: best, bval = c, float(np.mean(v))
    return best, usual, len(by.get(best, []))


def advice_test(recs):
    out = {}
    kinds = sorted({r["kind"] for r in recs})
    for kind in kinds:
        p = _prep(recs, kind)
        if not p: out[kind] = {"note": "not enough decisions yet"}; continue
        L, choices, ZN, ZA, y = p
        fold = np.array([_fold_of(r["match"]) for r in L])
        matched = np.zeros(len(L)); specific = np.zeros(len(L), bool)
        rec_counts = collections.Counter()
        for f in range(FOLDS):
            te = np.where(fold == f)[0]; tr = np.where(fold != f)[0]
            if len(te) == 0 or len(tr) < 20: continue
            for i in te:
                best, usual, n = advise(i, tr, L, ZN, y)
                matched[i] = 1.0 if L[i]["choice2"] == best else 0.0
                specific[i] = best != usual
                rec_counts[best] += 1
        # adjusted difference: win-chance change on the situation plus the matched flag
        def effect(idx):
            A = np.hstack([np.ones((len(idx), 1)), ZA[idx], matched[idx, None]])
            coef, *_ = np.linalg.lstsq(A, y[idx], rcond=None)
            return float(coef[-1])
        allidx = np.arange(len(L))
        est = effect(allidx)
        matches = sorted({r["match"] for r in L}); mi = collections.defaultdict(list)
        for i, r in enumerate(L): mi[r["match"]].append(i)
        rnd = random.Random(7); boots = []
        for _ in range(BOOT):
            idx = np.array([i for mm in (rnd.choice(matches) for _ in matches) for i in mi[mm]])
            try: boots.append(effect(idx))
            except Exception: pass
        lo, hi = (np.percentile(boots, [5, 95]) if boots else (None, None))
        raw_m = float(np.mean(y[matched == 1])) if (matched == 1).any() else None
        raw_u = float(np.mean(y[matched == 0])) if (matched == 0).any() else None
        sp = specific.astype(bool)
        spec_eff = None
        if sp.sum() >= 20 and (matched[sp] == 1).any() and (matched[sp] == 0).any():
            spec_eff = round(float(np.mean(y[sp & (matched == 1)]) - np.mean(y[sp & (matched == 0)])), 1)
        out[kind] = {"n": len(L), "matches": len(matches), "matched_share": round(float(matched.mean()), 2),
                     "effect_matched_vs_not": round(est, 1), "interval": [round(float(lo), 1), round(float(hi), 1)] if lo is not None else None,
                     "clear": bool(lo is not None and lo > 0), "raw_matched": round(raw_m, 1) if raw_m is not None else None,
                     "raw_unmatched": round(raw_u, 1) if raw_u is not None else None,
                     "specific_advice_share": round(float(sp.mean()), 2),
                     "specific_advice_effect_raw": spec_eff,
                     "recommended": dict(rec_counts.most_common(6))}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"about": __doc__.split("\n\n")[1].strip(), "kinds": out}, open(OUT, "w"), indent=1)
    return out


def lines(res):
    L = ["## Does the advice work? (the goal test)", "",
         "For each decision kind, the advice is built from five groups of matches and read on the sixth (unseen): teams whose "
         "choice matched the advice against teams whose didn't, win-chance change over the decision's window adjusted for the "
         "situation, 90% range from resampling whole matches. The advice = the best choice among the 15 most similar decisions "
         f"(at least {MIN_CASES} cases, {MARGIN:g}+ points better than the usual play), else the usual play. \"Specific\" = the "
         "advice differed from the usual play.", ""]
    passed = [k for k, v in res.items() if v.get("clear")]
    L.append(f"**{len(passed)} of {sum(1 for v in res.values() if 'n' in v)} kinds pass** (effect positive, range excludes 0): {', '.join(passed) or 'none yet'}.")
    L.append("")
    for k, v in res.items():
        if "n" not in v: L.append(f"- {k}: {v['note']}"); continue
        iv = f"{v['interval'][0]:+} to {v['interval'][1]:+}" if v.get("interval") else "?"
        L.append(f"- {k} ({v['n']} decisions, {v['matches']} matches): matched the advice {v['matched_share']:.0%} of the time; "
                 f"effect of matching {v['effect_matched_vs_not']:+} points (90% {iv}; {'clear' if v['clear'] else 'not clear'}); "
                 f"raw {v['raw_matched']} matched against {v['raw_unmatched']} not; specific advice in {v['specific_advice_share']:.0%} of cases"
                 + (f", raw effect there {v['specific_advice_effect_raw']:+}" if v.get("specific_advice_effect_raw") is not None else "")
                 + f". Most recommended: {', '.join(f'{c} ({n})' for c, n in v['recommended'].items())}.")
    L.append("")
    return L


# ---- the blind test (scored by hand)
BLIND = os.path.join(REPO, "data", "model", "blind_test.json")


def blind_pick(recs, n=10, seed=11):
    """Ten sealed moments for the blind test: decisions of kinds with specific advice, spread over kinds and matches,
    with the model's call recorded (from the other matches) and the outcome hidden until both calls are in."""
    rnd = random.Random(seed)
    byk = collections.defaultdict(list)
    for r in recs:
        if "wp_change" in r and r["kind"] not in ("late_game",): byk[r["kind"]].append(r)
    picks = []
    kinds = [k for k in byk if len(byk[k]) >= 40]
    while len(picks) < n and kinds:
        k = kinds[len(picks) % len(kinds)]
        p = _prep(recs, k)
        if not p: kinds.remove(k); continue
        L, choices, ZN, ZA, y = p
        i = rnd.randrange(len(L))
        tr = np.array([j for j in range(len(L)) if L[j]["match"] != L[i]["match"]])
        best, usual, nn = advise(i, tr, L, ZN, y)
        r = L[i]
        picks.append({"id": len(picks) + 1, "match": r["match"], "team": r["team"], "t": r["t"], "kind": k,
                      "situation": r["state"], "choices_seen": choices, "model_call": best, "usual_play": usual,
                      "denning_call": None, "actual_choice": "(sealed)", "outcome_wp_change": "(sealed)",
                      "_sealed": {"actual_choice": r["choice2"], "wp_change": r["wp_change"]}})
    json.dump({"about": "The blind test (Denning, November 2026 review): ten moments; Denning writes his call in denning_call "
                        "before anyone reads the sealed fields; then advice.py blind_score reveals and scores both calls by the "
                        "measured outcome of teams that made each choice in that situation.", "picks": picks}, open(BLIND, "w"), indent=1)
    return picks


if __name__ == "__main__":
    import usual as U, pickle
    src = sys.argv[1] if len(sys.argv) > 1 else "/tmp/ga"
    recs = U.wp_change(U.load(src))
    res = advice_test(recs)
    print("\n".join(lines(res)))
    if "--blind" in sys.argv: print(json.dumps(blind_pick(recs), indent=1)[:2000])
