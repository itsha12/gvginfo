#!/usr/bin/env python3
"""Similar cases for the flag family (REDESIGN.md stage D, c; R-451, R-531, R-538): which answer to an enemy flag run
did better among teams in a similar spot, and does a team that made the better call do better in matches the engine
never saw (the held-out advice test).

Three parts, each readable on its own:

1. The price of a result (R-538, his yardstick). A call is judged by the hard results on the fixed 90 and 180 s record
   (R-294): flags, deaths (as the death penalty they leave), morale boosts, NPCs, Lord damage. A stay can win a kill and lose half a flag, so
   each result is priced by how much it moves the chance of winning the match: one small model of a position, fitted
   on every moment of every counted match, mirrored (a mirrored position gives the mirrored answer, no intercept):
       chance of winning = logistic( strength gap, flag lead, death penalty, morale boost, pit NPCs lost, Lord health )
   each as own minus enemy (death penalty and morale boost are priced apart: a boost on a team with no death penalty
   is not a death undone). Footmen are not priced: on their own a footman is worth nothing to who wins, and beside
   the pit NPCs its price runs backwards (SPEC.md section 5, 4c: a reaction, never a price); each run prints the check. A call's priced result is the chance at the end of the window less the chance at its
   start, in win points (a match that ends inside the window ends at 100 or 0). The prices are fitted without the
   match they are used on (10 fixed groups of matches, cache.fold_of). This is a stand-in for the win model, which is
   rebuilt at stage E: six numbers, printed with every run, nothing guessed.

2. Similar cases (2.10). A case is a flag play (their run and our answer; a flag already in hand; their boost 30 s
   away) with the position it was chosen from. Cases are compared inside one scenario only (their single or double
   run, who holds the stand, the opening apart, a flag in hand apart), and within it by nearness on what he agreed
   (R-538): the flag lead, seconds to the next boost, players at the main fight on each side, each team's morale, the
   strength gap, and the hall as the usual length of its flag run in seconds (so halls alike in that pool), each in
   standard units of its scenario, equal weight. For a case and a call, the K nearest cases of other matches that
   made that call give the call's worth there, with a 90% range that treats the plays of one match as one draw. K is
   chosen by the data: the K that best foretells a case's own result from its neighbours.
   Floor (R-538): a call is read only from 30 plays or more out of 15 matches or more; under it, no verdict.
   Verdict on a call (REDESIGN "Verdict rules"): against the best other call with enough cases, never by this
   match's result: right, wrong, or no clear difference when the range includes none.

3. The held-out advice test (R-274, R-451). For each group of matches the prices and the cases come from the other
   nine. Where the advice is clear (the best call beats the next by more than its range), did the teams whose call
   matched it do better than those whose call did not: in the priced result at 180 s, and in how the match ended
   against what the position foretold, each set against the same scenario and position, with a 90% range from drawing
   whole matches again. The boost is read twice: every case, and without the flag only held at home (R-534: cope v
   hold 14:33; a boost "run" that denies nothing while the rest fall back).

Usage:  python3 cases.py test <plays file from `moments.py all`> [--json <out.json>]     the whole report
        python3 cases.py case <plays file> <report id> <m:ss>                          one decision, its calls and cases
A reading tool over the plays file: it writes no prepared data and is in no cache key (cache.REPORT_LAYER)."""
import collections, json, math, os, sys
import numpy as np
from common import REPO

MIN_PLAYS, MIN_MATCHES = 30, 15                  # R-538: the floor under any verdict
K_TRY = (30, 45, 60, 90, 120)
Z = 1.645                                        # a 90% range
DRAWS = 300
PRICE = ("strength gap (per 100 points of rating)", "a flag of lead", "death penalty (per 15%, one death's worth)", "morale boost (+10% on all eight)", "a pit NPC", "Lord health (per 10%)")
SCALE = (100.0, 1.0, 15.0, 80.0, 1.0, 0.1)       # the unit each price is quoted in
VARS = ("flag lead", "seconds to the boost", "own players at the main fight", "their players at the main fight", "own morale", "their morale", "strength gap", "the hall's flag run, s")
PIT = ("knight", "archer", "bodyguard")
HELD_REST = ("fall back into the base", "retreat to the pit", "fall to footmen")
cl = lambda t: f"{int(t) // 60}:{int(t) % 60:02d}"


# ---- the matches and the positions
def load(path):
    import common, strength, cache
    D, idx = json.load(open(path)), common.replay_index()
    usual = json.load(open(os.path.join(REPO, "data", "benchmarks", "flag_arrival.json")))["usual"]
    by = collections.defaultdict(list)
    for k, v in usual.items(): by[k.split("|")[0]].append(v)
    hall = {h: sum(v) / len(v) for h, v in by.items()}
    M, nogap = {}, 0
    for rid, m in D["matches"].items():
        a, b = m["teams"]
        g = strength.strength_gap(rid, a)[1]
        if g is None: g, nogap = 0.0, nogap + 1
        M[rid] = {"teams": m["teams"], "map": m["map"], "date": m["date"], "winner": idx[rid].get("winner"), "gap": {a: g, b: -g}, "run_s": hall.get(m["map"]), "fold": cache.fold_of(rid)}
    known = [v["run_s"] for v in M.values() if v["run_s"]]
    mid = sorted(known)[len(known) // 2]
    nohall = sorted({v["map"] for v in M.values() if not v["run_s"]})
    for v in M.values(): v["run_s"] = v["run_s"] or mid          # a hall with no measured run (said in the report): the middle hall's, so it leans nowhere
    D["_notes"] = {"no strength gap": nogap, "halls with no measured flag run": nohall, "no winner": sum(1 for v in M.values() if not v["winner"])}
    return D, M


def position(st, af, gap, now, footmen=False):
    """A position as the price model reads it, own minus enemy: at the start of the window, or `now` at its end.
    `footmen`: with the footmen lost added on the end (for the check that leaves them unpriced)."""
    i = 1 if now else 0
    lead = af["lead"][i]
    if lead is None: return None
    lost = [list(x) for x in st["npcs_lost"]]
    if now:
        for k in (0, 1):
            lost[k][0] += sum(1 for n in af["npc_kinds"][k] if n in PIT); lost[k][1] += sum(1 for n in af["npc_kinds"][k] if n == "footman")
    lo = af["lord"]
    lord = (lo[0][i] - lo[1][i]) if lo[0][i] is not None and lo[1][i] is not None else 0.0      # a Lord whose damage was not observed: no difference read (a blank that means "not in the replay")
    mp = af["morale_parts"]
    return [gap, lead, mp[0][i][0] - mp[1][i][0], mp[0][i][1] - mp[1][i][1], lost[1][0] - lost[0][0], lord] + ([lost[1][1] - lost[0][1]] if footmen else [])


def price_rows(D, M):
    """Every position the run holds, with whether its team won: each moment and each flag or boost play, at its
    start and, where the match is still going, 90 and 180 s on."""
    X, y, g = [], [], []
    src = [(r["rid"], r["team"], r["state"], r["after"]) for r in D["records"]] + [(p["rid"], p["team"], p["state"], p["after"]) for p in D["plays"] if "state" in p]
    for rid, team, st, af in src:
        m = M[rid]
        if not m["winner"] or "npcs_lost" not in st: continue
        won = float(m["winner"] == team)
        for H, now in (("90", False), ("90", True), ("180", True)):
            if now and af[H]["ended"]: continue
            x = position(st, af[H], m["gap"][team], now, footmen=True)
            if x is not None: X.append(x); y.append(won); g.append(m["fold"])
    X = np.array(X, float)
    return X[:, :-1], np.array(y), np.array(g), X[:, -1]


def fit_prices(X, y, scale=SCALE):
    from sklearn.linear_model import LogisticRegression
    Xs = X / np.array(scale)
    lr = LogisticRegression(fit_intercept=False, C=1e4, max_iter=2000)
    lr.fit(np.vstack([Xs, -Xs]), np.concatenate([y, 1 - y]))              # mirrored: the other team's side of the same position
    return lr.coef_[0]


chance = lambda beta, x: 1.0 / (1.0 + math.exp(-float(np.dot(beta, np.array(x) / np.array(SCALE)))))


def prices(D, M):
    """The prices fitted without each group of matches, the prices on every match (for the report), and how well the
    held-out prices foretell who wins."""
    X, y, g, foot = price_rows(D, M)
    folds = sorted(set(g.tolist()))
    B = {f: fit_prices(X[g != f], y[g != f]) for f in folds}
    full = fit_prices(X, y)
    p = np.array([chance(B[f], x) for x, f in zip(X, g)])
    gap_only = 1 / (1 + np.exp(-(X[:, 0] / SCALE[0]) * np.array([B[f][0] for f in g])))
    ll = lambda q: float(-np.mean(y * np.log(np.clip(q, 1e-6, 1)) + (1 - y) * np.log(np.clip(1 - q, 1e-6, 1))))
    cal = []
    for lo in np.arange(0, 1, 0.1):
        sel = (p >= lo) & (p < lo + 0.1)
        if sel.sum() >= 50: cal.append((round(float(lo), 1), int(sel.sum()), round(float(p[sel].mean()), 3), round(float(y[sel].mean()), 3)))
    spread = np.std(np.array([B[f] for f in folds]), axis=0)
    f_alone = fit_prices(np.column_stack([X[:, 0], foot]), y, (SCALE[0], 1.0))[1]           # the footman check: its price beside the strength gap alone, and beside everything priced
    f_beside = fit_prices(np.column_stack([X, foot]), y, SCALE + (1.0,))[-1]
    return B, {"footman_check": [25 * float(f_alone), 25 * float(f_beside)], "rows": int(len(y)), "beta": full.tolist(), "spread": spread.tolist(), "logloss": round(ll(p), 4), "logloss_strength_only": round(ll(gap_only), 4),
               "accuracy": round(float(np.mean((p > 0.5) == (y > 0.5))), 3), "calibration": cal}


# ---- the cases
def cases(D, M, B):
    """One case a flag play (Shadow of Haste runs set aside, R-456) or boost play, with its scenario, its call, the
    variables it is matched on, and its priced result at 90 and 180 s from prices that never saw its match."""
    out, skipped = [], collections.Counter()
    for p in D["plays"]:
        if p["play"] not in ("flag", "boost") or "state" not in p: continue
        if p.get("soh") or p.get("runner_soh"): skipped["Shadow of Haste run (R-456)"] += 1; continue
        m, st, af = M[p["rid"]], p["state"], p["after"]
        if not m["winner"]: skipped["no winner recorded"] += 1; continue
        gap = m["gap"][p["team"]]
        ends = {H: None if af[H]["ended"] else position(st, af[H], gap, True) for H in ("90", "180")}
        if st["flag_lead"] is None or af["90"]["lead"][0] is None or any(ends[H] is None and not af[H]["ended"] for H in ends): skipped["flag lead not read"] += 1; continue
        held = False
        if p["play"] == "boost":
            scen, call = "Their boost is 30 s away", {"run": "run a flag", "concede": "send no flag"}[p["call"]]
            held = p["call"] == "run" and not p["beside"]["denied"] and p.get("rest") in HELD_REST
        elif p["ours"] == "a flag already in hand":
            if not p.get("hand"): skipped["a flag in hand and their flag never got in: nothing to answer"] += 1; continue
            scen, call = f"Their {p['their']}; our flag already in hand", p["hand"]
        else:
            stand = {"own": "we hold the stand", "enemy": "they hold the stand", "nobody": "nobody holds the stand"}[st["stand"]]
            scen, call = ("The opening (no flag capped yet): their" if p.get("opening") else "Their") + f" {p['their']}; {stand}", {"stay": "stay", "single run": "single run", "double run": "double run"}[p["ours"]]
        beta, won = B[m["fold"]], float(m["winner"] == p["team"])
        p0 = chance(beta, position(st, af["90"], gap, False))
        v = {H: 100 * ((won if af[H]["ended"] else chance(beta, ends[H])) - p0) for H in ("90", "180")}
        x = [st["flag_lead"], st["boost_in"], st["main"][0], st["main"][1], af["90"]["morale"][0][0], af["90"]["morale"][1][0], gap, m["run_s"]]
        out.append({"id": p["id"], "rid": p["rid"], "fold": m["fold"], "team": p["team"], "t": p["t0"], "kind": p["play"], "scenario": scen, "call": call, "x": x, "v": v, "p0": p0, "won": won,
                    "held": held, "said": p["scenario"],
                    "hard": {H: {"deaths": af[H]["deaths"], "npcs": af[H]["npcs"], "lead_change": af[H]["lead_change"], "boosts": af[H]["boosts"]} for H in ("90", "180")}})
    return out, skipped


class Scenario:
    """The cases of one scenario, laid out for finding the nearest."""
    def __init__(self, C):
        self.C = C
        X = np.array([[np.nan if v is None else v for v in c["x"]] for c in C], float)
        med = np.nanmedian(X, axis=0); med = np.where(np.isnan(med), 0.0, med)
        X = np.where(np.isnan(X), med, X)                       # seconds to the boost where nobody holds the stand: the scenario's middle (the stand is part of the scenario)
        sd = X.std(axis=0); sd[sd == 0] = 1.0
        self.Z = (X - X.mean(axis=0)) / sd
        self.rid = np.array([c["rid"] for c in C]); self.fold = np.array([c["fold"] for c in C]); self.call = np.array([c["call"] for c in C])
        self.calls = [k for k, _ in collections.Counter(self.call.tolist()).most_common()]
        self.v = {H: np.array([c["v"][H] for c in C]) for H in ("90", "180")}

    def near(self, i, call, K, heldout):
        """The K nearest cases that made `call`, from other matches (heldout: from other groups of matches)."""
        ok = (self.call == call) & ((self.fold != self.fold[i]) if heldout else (self.rid != self.rid[i]))
        j = np.flatnonzero(ok)
        if len(j) == 0: return j
        d = ((self.Z[j] - self.Z[i]) ** 2).sum(axis=1)
        return j[np.argsort(d, kind="stable")[:K]]

    def worth(self, j, H):
        """The mean priced result of those cases, and its spread with the plays of one match taken as one draw."""
        v = self.v[H][j]; n = len(v); mu = float(v.mean())
        res = collections.defaultdict(float)
        for r, e in zip(self.rid[j], v - mu): res[r] += e
        G = len(res)
        se = math.sqrt(sum(e * e for e in res.values()) * (G / (G - 1) if G > 1 else 1)) / n
        return mu, se, n, G

    def read(self, i, K, heldout, H="180"):
        """Each call's worth at case i, the advice, and the verdict on the call the team made."""
        W = {}
        for a in self.calls:
            j = self.near(i, a, K, heldout)
            if len(j) < MIN_PLAYS or len(set(self.rid[j].tolist())) < MIN_MATCHES: continue
            mu, se, n, G = self.worth(j, H); W[a] = {"worth": mu, "se": se, "plays": n, "matches": G, "near": j}
        out = {"calls": W, "advice": None, "clear": False, "verdict": "too few cases", "margin": None, "range": None}
        if len(W) < 2: return out
        order = sorted(W, key=lambda a: -W[a]["worth"])
        best, nxt = order[0], order[1]
        d, se = W[best]["worth"] - W[nxt]["worth"], math.hypot(W[best]["se"], W[nxt]["se"])
        out.update(advice=best, clear=d - Z * se > 0, margin=d, range=[d - Z * se, d + Z * se])
        c = self.call[i]
        if c in W:
            alt = next(a for a in order if a != c)
            d2, se2 = W[c]["worth"] - W[alt]["worth"], math.hypot(W[c]["se"], W[alt]["se"])
            out.update(verdict="right" if d2 - Z * se2 > 0 else "wrong" if d2 + Z * se2 < 0 else "no clear difference", against=alt, mine=[d2, d2 - Z * se2, d2 + Z * se2])
        else: out["verdict"] = "too few cases of this call"
        return out


def choose_k(S):
    """The K that best foretells a case's own priced result at 180 s from the K nearest cases of the same call in
    other groups of matches: the mean squared miss, over every scenario."""
    err = {}
    for K in K_TRY:
        miss = []
        for s in S.values():
            for i in range(len(s.C)):
                j = s.near(i, s.call[i], K, True)
                if len(j) >= MIN_PLAYS: miss.append((s.v["180"][i] - s.v["180"][j].mean()) ** 2)
        err[K] = (float(np.mean(miss)), len(miss))
    return min(err, key=lambda k: err[k][0]), err


# ---- the held-out advice test
def _effect(rows, col):
    """The difference between matched and unmatched in `col`, set against the same scenario and position: a straight
    fit on a matched flag, the scenario, the chance of winning at the start and the matching variables."""
    scen = sorted({r["scenario"] for r in rows})
    A = np.array([[1.0, float(r["matched"]), r["p0"]] + [float(r["scenario"] == s) for s in scen[1:]] + list(r["z"]) for r in rows])
    yv = np.array([r[col] for r in rows])
    return float(np.linalg.lstsq(A, yv, rcond=None)[0][1])


def advice_test(S, K, drop_held=False, only=None):
    """Held out: the advice for every case from the other nine groups of matches. Among cases with clear advice, the
    teams that matched it against those that did not."""
    import random
    rows, tally = [], collections.Counter()
    for name, s in S.items():
        if only and not only(name): continue
        for i, c in enumerate(s.C):
            if drop_held and c["held"]: continue
            r = s.read(i, K, True)
            tally["cases"] += 1
            if r["advice"] is None: tally["too few cases"] += 1; continue
            if not r["clear"]: tally["no clear advice"] += 1; continue
            tally["clear advice"] += 1
            rows.append({"rid": c["rid"], "scenario": name, "matched": c["call"] == r["advice"], "advice": r["advice"], "call": c["call"], "p0": c["p0"], "z": s.Z[i].tolist(),
                         "v180": c["v"]["180"], "v90": c["v"]["90"], "end": 100 * (c["won"] - c["p0"]), "margin": r["margin"]})
    out = {"tally": dict(tally), "rows": len(rows)}
    n1 = sum(r["matched"] for r in rows)
    if n1 < MIN_PLAYS or len(rows) - n1 < MIN_PLAYS: out["verdict"] = "too few to call"; out["matched"] = n1; return out, rows
    rnd = random.Random(7); by = collections.defaultdict(list)
    for r in rows: by[r["rid"]].append(r)
    ids = sorted(by)
    for col in ("v180", "v90", "end"):
        e = _effect(rows, col); draws = []
        for _ in range(DRAWS):
            R = [r for k in (rnd.choice(ids) for _ in ids) for r in by[k]]
            if 0 < sum(r["matched"] for r in R) < len(R): draws.append(_effect(R, col))
        draws.sort()
        lo, hi = draws[int(0.05 * len(draws))], draws[int(0.95 * len(draws)) - 1]
        raw = [float(np.mean([r[col] for r in rows if r["matched"] == b])) for b in (True, False)]
        out[col] = {"effect": e, "range": [lo, hi], "matched_mean": raw[0], "unmatched_mean": raw[1], "verdict": "better" if lo > 0 else "worse" if hi < 0 else "no clear difference"}
    out["matched"], out["matches"] = n1, len(ids)
    out["advice"] = dict(collections.Counter(r["advice"] for r in rows)); out["calls"] = dict(collections.Counter(r["call"] for r in rows))
    return out, rows


# ---- the report
def build(path):
    D, M = load(path)
    B, P = prices(D, M)
    C, skipped = cases(D, M, B)
    by = collections.defaultdict(list)
    for c in C: by[c["scenario"]].append(c)
    S = {k: Scenario(v) for k, v in sorted(by.items(), key=lambda kv: -len(kv[1]))}
    return D, M, B, P, C, skipped, S


def report(path, out_json=None):
    D, M, B, P, C, skipped, S = build(path)
    pr = print
    pr(f"Similar cases for the flag family (R-451, R-531, R-538), on {len(M)} matches: {len(C)} cases" + "".join(f"; set aside, {k}: {v}" for k, v in skipped.items()))
    for k, v in D["_notes"].items():
        if v: pr(f"  note: {k}: {v}")
    pr("\n1. The price of a result: what each is worth to the chance of winning the match, from an even position")
    pr(f"   ({P['rows']:,} positions; fitted without the match priced; the spread is across the ten groups of matches)")
    for name, b, sp in zip(PRICE, P["beta"], P["spread"]):
        pr(f"   {name:42} {25 * b:+6.1f} win points   (spread {25 * sp:.1f})")
    fa, fb = P["footman_check"]
    pr(f"   A footman is not priced: beside the strength gap alone it is worth {fa:+.1f} win points, and beside the results above {fb:+.1f}" + (" (backwards: a reaction, not a price)" if fb < 0 else " (CHECK: no longer backwards; look again at leaving it out)"))
    pr(f"   Who wins, foretold on matches the prices never saw: {100 * P['accuracy']:.0f}% right; log loss {P['logloss']} against {P['logloss_strength_only']} from the strength gap alone")
    pr("   Foretold chance against what happened: " + "; ".join(f"{100 * a:.0f}% said, {100 * b:.0f}% won ({n:,})" for _, n, a, b in P["calibration"]))
    K, err = choose_k(S)
    pr(f"\n2. Similar cases. Matched on: {', '.join(VARS)}.")
    pr("   K (how many nearest cases a call is read from), by how well it foretells a case's own result: " + "; ".join(f"K {k}: miss {math.sqrt(e):.2f} win points ({n:,} cases)" for k, (e, n) in err.items()) + f". Chosen: {K}.")
    res = {"prices": P, "K": K, "k_error": {k: e for k, (e, n) in err.items()}, "scenarios": {}, "skipped": dict(skipped), "notes": D["_notes"]}
    for name, s in S.items():
        n = len(s.C); cnt = collections.Counter(s.call.tolist())
        pr(f"\n   {name}: {n} cases in {len(set(s.rid.tolist()))} matches")
        for a in s.calls:
            sel = s.call == a
            hd = [c["hard"]["180"] for c, ok in zip(s.C, sel) if ok]
            mean = lambda f: float(np.mean([f(h) for h in hd]))
            lc = [h["lead_change"] for h in hd if h["lead_change"] is not None]
            pr(f"     {a:34} {cnt[a]:5}   as it fell, 180 s on: {s.v['180'][sel].mean():+5.1f} win points; flag lead {np.mean(lc):+.2f}; deaths {mean(lambda h: h['deaths'][0]):.2f} own, {mean(lambda h: h['deaths'][1]):.2f} theirs; "
               f"NPCs lost {mean(lambda h: h['npcs'][0]):.2f} own, {mean(lambda h: h['npcs'][1]):.2f} theirs" + ("" if cnt[a] >= MIN_PLAYS else "   (under the floor: no verdict)"))
        R = [s.read(i, K, False) for i in range(n)]
        adv = collections.Counter((r["advice"], r["clear"]) for r in R if r["advice"]); ver = collections.Counter(r["verdict"] for r in R)
        clear = sum(v for (a, c), v in adv.items() if c)
        usual = s.calls[0]
        res["scenarios"][name] = {"cases": n, "calls": dict(cnt), "verdicts": dict(ver), "clear_advice": {a: v for (a, c), v in adv.items() if c}, "best_not_clear": {a: v for (a, c), v in adv.items() if not c}}
        if not adv: pr("     no two calls with enough cases: no verdict in this scenario"); continue
        pr("     in similar spots the better call is: " + "; ".join(f"{a} in {v} ({100 * v // n}%)" for (a, c), v in sorted(adv.items(), key=lambda kv: -kv[1]) if c) + (f"; no clear difference in {n - clear - ver['too few cases']} ({100 * (n - clear - ver['too few cases']) // n}%)") + (f"; too few cases in {ver['too few cases']}" if ver["too few cases"] else ""))
        mg = [r["margin"] for r in R if r["clear"]]
        if mg: pr(f"     where it is clear, the better call is ahead by {np.median(mg):.1f} win points (middle case; {min(mg):.1f} to {max(mg):.1f}); the usual play here is {usual}, and the advice differs from it in {sum(1 for r in R if r['clear'] and r['advice'] != usual)} cases")
        pr("     the calls teams made: " + "; ".join(f"{k} {v}" for k, v in ver.most_common()))
    pr("\n3. The held-out advice test: where the advice is clear, did teams that matched it do better? (advice and prices from the other nine groups of matches)")
    tests = [("every flag and boost scenario", dict()), ("their run, our answer (not the boost, not the opening)", dict(only=lambda n: n.startswith("Their") and "boost" not in n and "in hand" not in n)),
             ("the opening", dict(only=lambda n: n.startswith("The opening"))),
             ("their boost 30 s away, every case", dict(only=lambda n: "boost" in n)), ("their boost 30 s away, without the flag only held at home", dict(only=lambda n: "boost" in n, drop_held=True))]
    res["advice_test"] = {}
    for label, kw in tests:
        t, rows = advice_test(S, K, **kw); res["advice_test"][label] = t
        ta = t["tally"]
        pr(f"\n   {label}: {ta.get('cases', 0)} cases; clear advice in {ta.get('clear advice', 0)}, no clear advice in {ta.get('no clear advice', 0)}, too few cases in {ta.get('too few cases', 0)}")
        if "v180" not in t: pr(f"     {t.get('verdict', 'too few to call')} (matched {t.get('matched', 0)} of {t['rows']})"); continue
        pr(f"     matched the advice {t['matched']} of {t['rows']} ({100 * t['matched'] // t['rows']}%), in {t['matches']} matches; the advice: " + "; ".join(f"{k} {v}" for k, v in sorted(t["advice"].items(), key=lambda kv: -kv[1])))
        for col, words in (("v180", "priced result 180 s on"), ("v90", "priced result 90 s on"), ("end", "how the match ended against the position")):
            e = t[col]
            pr(f"     {words:42} matched {e['matched_mean']:+5.1f}, not matched {e['unmatched_mean']:+5.1f}; set against the same scenario and position: {e['effect']:+.1f} win points (90% range {e['range'][0]:+.1f} to {e['range'][1]:+.1f}): {e['verdict']}")
    held = sum(1 for c in C if c["held"])
    pr(f"\n   The flag only held at home at a boost (a boost run that denies nothing while the rest fall back): {held} of {sum(1 for c in C if c['kind'] == 'boost')} boost cases.")
    if out_json: json.dump(res, open(out_json, "w"), ensure_ascii=False, indent=1, default=float)
    return res


def case(path, rid, at):
    """One decision as its card: the situation, each call's worth among the nearest cases, the verdict, and three of
    the nearest cases of each call with their replay links and the second to look at."""
    D, M, B, P, C, skipped, S = build(path)
    K, _ = choose_k(S)
    t = (lambda a: int(a[0]) * 60 + int(a[1]))(at.split(":"))
    c = min((c for c in C if c["rid"].startswith(rid)), key=lambda c: abs(c["t"] - t), default=None)
    if c is None: sys.exit("no flag or boost case in that match")
    s = S[c["scenario"]]; i = next(k for k, x in enumerate(s.C) if x["id"] == c["id"])
    m = M[c["rid"]]; r = s.read(i, K, False)
    print(f"{' v '.join(m['teams'])}, {m['map']}, {m['date']}, {cl(c['t'])}: https://gvg.report/report/{c['rid']}#map")
    print(f"  {c['said']}\n  scenario: {c['scenario']}; {c['team']}'s call: {c['call']}; chance of winning at that second {100 * c['p0']:.0f}%")
    print("  matched on: " + "; ".join(f"{n} {v:.0f}" if isinstance(v, (int, float)) and abs(v) >= 10 else f"{n} {v}" for n, v in zip(VARS, c["x"])))
    print(f"  what followed: {c['v']['90']:+.1f} win points at 90 s, {c['v']['180']:+.1f} at 180 s; at 180 s deaths {c['hard']['180']['deaths']}, NPCs lost {c['hard']['180']['npcs']}, flag lead {c['hard']['180']['lead_change']}")
    for a, w in sorted(r["calls"].items(), key=lambda kv: -kv[1]["worth"]):
        print(f"  {a:34} worth {w['worth']:+5.1f} win points (90% range {w['worth'] - Z * w['se']:+.1f} to {w['worth'] + Z * w['se']:+.1f}), from {w['plays']} plays in {w['matches']} matches")
        for j in w["near"][:3]:
            x = s.C[j]; mm = M[x["rid"]]
            print(f"      {' v '.join(mm['teams'])}, {mm['map']}, {mm['date']}, {cl(x['t'])} ({x['team']}; {x['v']['180']:+.1f}): https://gvg.report/report/{x['rid']}#map")
    print(f"  advice: {r['advice']}" + (f", ahead of the next call by {r['margin']:.1f} win points (90% range {r['range'][0]:+.1f} to {r['range'][1]:+.1f})" if r["advice"] else "") + f"; verdict on the call made: {r['verdict']}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "test": report(a[1], a[a.index("--json") + 1] if "--json" in a else None)
    elif len(a) >= 4 and a[0] == "case": case(a[1], a[2], a[3])
    else: print(__doc__)
