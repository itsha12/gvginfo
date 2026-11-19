#!/usr/bin/env python3
"""Similar cases for the flag family (REDESIGN.md stage D, c; R-451, R-531, R-538 to R-544): which answer did better
among teams in a similar spot, and does a team that made the better call do better in matches the engine never saw
(the held-out advice test).

1. The price of a result (R-538, his yardstick). A call is judged by the hard results on a fixed record after it
   (R-294): flags, deaths (as the death penalty they leave), morale boosts, NPCs, Lord damage. A stay can win a kill
   and lose half a flag, so each result is priced by how much it moves the chance of winning the match: one small
   model of a position, fitted on every moment of every counted match, mirrored (a mirrored position gives the
   mirrored answer, no intercept):
       chance of winning = logistic( strength gap, flag lead, death penalty, morale boost, pit NPCs lost, Lord health )
   each as own minus enemy (death penalty and morale boost are priced apart: a boost on a team with no death penalty
   is not a death undone). Footmen are not priced: on their own a footman is worth nothing to who wins, and beside
   the pit NPCs its price runs backwards (SPEC.md section 5, 4c: a reaction, never a price); each run prints the
   check. A call's priced result is the chance at the end of the window less the chance at its start, in win points
   (a match that ends inside the window ends at 100 or 0). The prices are fitted without the match they are used on
   (10 fixed groups of matches, cache.fold_of). A stand-in for the win model, which is rebuilt at stage E: six
   numbers, printed with every run, nothing guessed.

2. Similar cases (2.10). Cases are compared inside one scenario only, and within it by nearness on what he agreed
   (R-538): the flag lead, seconds to the next boost, players at the main fight on each side, each team's morale, the
   strength gap, and the hall as the usual length of its flag run in seconds (halls alike in that pool); and for the
   answer to their run also (R-539, R-540, R-544) the res clock, where each main team stands, who their runner is as
   what he can do, each team's snares, how long their flag should take, and whether the flag can beat the boost. A
   build is a fixed state, never a call, but it bears on which call is right: it comes in as properties, never as a
   label. Each variable in standard units of its scenario, equal weight (measured weights and a short list of six
   were tried and dropped, R-544: they agreed with equal weight in all but three of thirty-six tests). For a case and
   a call, the K nearest cases of other matches that made that call give the call's worth there, with a 90% range
   that treats the plays of one match as one draw. K is chosen by the data. Floor (R-538): a call is read only from
   30 plays or more out of 15 matches or more. Verdict (REDESIGN "Verdict rules"): against the best other call with
   enough cases, never by this match's result: right, wrong, or no clear difference.
   The scenarios:
   - Their boost is 30 s away: run a flag, or send none (read twice: every case, and without the flag only held at
     home, R-534).
   - Our flag already in hand when their runner sets off: what we did with it.
   - Their run and our answer (R-542, R-543): read at fixed seconds after their runner set off, 15 and 30 s (45 s was
     read too and dropped, R-544). At each read their run is still under way and we had sent nobody by the read
     before; the call is whether a runner of ours has set off by now (a single runner, or the second player of a
     double run), or none yet. A team with none yet may send one later or never: what is judged is the decision as it
     stands at that second. It is never read to the end of their run: a "stay" so read takes in every run of theirs
     that came to nothing (their flag fails after 35% of such stays and 9% of runs). What followed is read 60, 90 and
     180 s after the decision arose (120 s was read too and dropped). The opening is out: a different decision (R-541).

3. The held-out advice test (R-274, R-451). For each group of matches the prices and the cases come from the other
   nine. Where the advice is clear (the best call beats the next by more than its range), did the teams whose call
   matched it do better than those whose call did not, in the priced result, set against the same scenario and
   position, with a 90% range from drawing whole matches again.

4. His given (R-542), printed as a check: a team that sends nobody is further behind on flags (T12 in truths.py), and
   with no kill or other gain it should be worse off; read with their flag able to beat our boost and not.

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
MORE = ("seconds to the base res", "own main team's place (steps toward own pit)", "their main team's place (steps toward their pit)", "their runner is a backline monk", "their runner's speed",
        "their team's snares", "own team's snares", "seconds their flag should take to the stand", "the flag can beat the boost")
READS = (15, 30)                                 # the seconds after their runner set off at which our answer is read (R-543; 45 s dropped, R-544)
HORIZONS = ("60", "90", "180")                   # what followed, read at three seconds from the decision (R-543; 120 s dropped, R-544)
BACK_AND_RUN = 1.76                              # a full run from the stand in units of the hall's carry from the spawn: back to the spawn at running speed (205/270 of the carry), then the carry
SENT, DOUBLE, NONE = "a runner sent by now", "a double run started by now", "no runner yet"
PIT = ("knight", "archer", "bodyguard")
FRONT = ("Warrior", "Hammer", "Derv", "Ranger", "Assassin", "Paragon", "Axe", "Sword")      # a runner told by his line: a backline monk, a frontline player (these), else a midline player
line_of = lambda r: None if not r else "a backline monk" if r["monks"] else "a frontline player" if any(w in r["role"] for w in FRONT) else "a midline player"
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
        M[rid] = {"teams": m["teams"], "map": m["map"], "date": m["date"], "length_s": idx[rid].get("length_s"), "winner": idx[rid].get("winner"), "gap": {a: g, b: -g}, "run_s": hall.get(m["map"]), "fold": cache.fold_of(rid)}
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


# ---- the cases
def cases(D, M, B):
    """One case a flag play (Shadow of Haste runs set aside, R-456; the opening apart, R-541) or boost play, with the
    variables it is matched on and its priced result at each second read, from prices that never saw its match. A
    boost play and a flag already in hand carry their scenario and call; their run and our answer gets both from
    read_cases, at fixed seconds."""
    out, skipped = [], collections.Counter()
    for p in D["plays"]:
        if p["play"] not in ("flag", "boost") or "state" not in p: continue
        if p.get("soh") or p.get("runner_soh"): skipped["Shadow of Haste run (R-456)"] += 1; continue
        if p.get("opening"): skipped["the opening: a different decision (R-541)"] += 1; continue
        m, st, af = M[p["rid"]], p["state"], p["after"]
        if not m["winner"]: skipped["no winner recorded"] += 1; continue
        gap = m["gap"][p["team"]]
        HS = [H for H in HORIZONS if H in af]                  # the boost plays carry 90 and 180 s only
        ends = {H: None if af[H]["ended"] else position(st, af[H], gap, True) for H in HS}
        if st["flag_lead"] is None or af["90"]["lead"][0] is None or any(ends[H] is None and not af[H]["ended"] for H in ends): skipped["flag lead not read"] += 1; continue
        held, scen, call, in_hand = False, None, None, False
        if p["play"] == "boost":
            scen, call = "Their boost is 30 s away", {"run": "run a flag", "concede": "send no flag"}[p["call"]]
            held = p["call"] == "run" and not p["beside"]["denied"] and p.get("rest") in HELD_REST
        elif p["ours"] == "a flag already in hand":
            if not p.get("hand"): skipped["a flag in hand and their flag never got in: nothing to answer"] += 1; continue
            scen, call, in_hand = f"Their {p['their']}; our flag already in hand", p["hand"], True
        beta, won = B[m["fold"]], float(m["winner"] == p["team"])
        p0 = chance(beta, position(st, af["90"], gap, False))
        v = {H: 100 * ((won if af[H]["ended"] else chance(beta, ends[H])) - p0) for H in HS}
        x = [st["flag_lead"], st["boost_in"], st["main"][0], st["main"][1], af["90"]["morale"][0][0], af["90"]["morale"][1][0], gap, m["run_s"]]
        more = beats = None
        if "their_runner" in p:                                 # a flag play: what else can be seen at that second
            tr, tms, stp, eta = p["their_runner"], p["teams"], p["steps"], (p.get("clock") or {}).get("their_eta_s")
            # can the flag beat the boost (R-544)? With us holding the stand: their flag should be in before our boost lands, so the stand is under threat. With them
            # holding it: a run of ours from the stand should be in before their boost. Nobody holding it: no boost to beat
            if st["boost_in"] is not None:
                if st["stand"] == "own": beats = None if eta is None else eta < st["boost_in"]
                elif st["stand"] == "enemy": beats = BACK_AND_RUN * m["run_s"] < st["boost_in"]
            more = [st["res_in"], stp[0], stp[1], float(tr["monks"] > 0), tr["speed"], tms["snare"][1], tms["snare"][0], eta, None if beats is None else float(beats)]
        out.append({"id": p["id"], "rid": p["rid"], "fold": m["fold"], "team": p["team"], "t": p["t0"], "kind": p["play"], "scenario": scen, "call": call, "x": x, "more": more, "v": v, "p0": p0,
                    "won": won, "held": held, "said": p["scenario"], "clock": p.get("clock"), "stand": st["stand"], "their": p.get("their"), "in_hand": in_hand, "beats": beats,
                    "their_flag": (p.get("beside") or {}).get("their_flag"), "boosts": {H: af[H]["boosts"] for H in HS},
                    "their_runner": p.get("their_runner"), "our_runner": p.get("our_runner"), "snares": (p.get("teams") or {}).get("snare"), "t1": p["t1"],
                    "our_capped": p["tests"].get("our flag is capped"), "main_deaths": (p.get("beside") or {}).get("deaths_at_the_main_fight"),
                    "lead": {H: af[H]["lead_change"] for H in HS}, "quiet": {H: af[H]["deaths"] == [0, 0] and af[H]["npcs"] == [0, 0] for H in HS},
                    "hard": {H: {"deaths": af[H]["deaths"], "npcs": af[H]["npcs"], "lead_change": af[H]["lead_change"], "boosts": af[H]["boosts"]} for H in HS}})
    return out, skipped


def _delay(c):
    """Seconds from their runner setting off to ours, None when we sent nobody."""
    k = c["clock"]
    return None if k["our_off"] is None else k["our_off"] - k["their_off"]


def answering(C):
    """The cases of their run and our answer that can be read at a fixed second."""
    return [c for c in C if c["kind"] == "flag" and not c["in_hand"] and c["clock"] and c["stand"] in ("own", "enemy")]


def read_cases(C):
    """Our answer to their run as it stands 15 and 30 s after their runner set off (R-542, R-543). At each read their
    run is still under way, and we had sent nobody by the read before; the call is whether a runner of ours has set
    off by now (the second player of a double run told apart), or none yet."""
    out = []
    for c in answering(C):
        k, delay = c["clock"], _delay(c)
        for n, R in enumerate(READS):
            if k["their_end"] <= k["their_off"] + R: break                          # their run is over: nothing left to answer
            if n and delay is not None and delay <= READS[n - 1]: break             # we had already sent a runner by the read before
            stand = "we hold the stand" if c["stand"] == "own" else "they hold the stand"
            sent = delay is not None and delay <= R
            out.append(dict(c, read=R, scenario=f"Their {c['their']}; {stand}; {R} s after their runner set off" + (f", nobody sent by {READS[n - 1]} s" if n else ""),
                            call=(DOUBLE if k["our_double"] else SENT) if sent else NONE))
    return out


class Scenario:
    """The cases of one scenario, laid out for finding the nearest."""
    def __init__(self, C):
        self.C = C
        self.extended = all(c["more"] is not None for c in C)   # the added variables, where every case of the scenario has them (the flag plays)
        X = np.array([[np.nan if v is None else v for v in (c["x"] + c["more"] if self.extended else c["x"])] for c in C], float)
        with np.errstate(all="ignore"):
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                med = np.nanmedian(X, axis=0)
        med = np.where(np.isnan(med), 0.0, med)
        X = np.where(np.isnan(X), med, X)                       # a variable not read for a case: the scenario's middle, so it leans nowhere
        sd = X.std(axis=0); sd[sd == 0] = 1.0
        self.Z = (X - X.mean(axis=0)) / sd
        self.names = list(VARS + MORE) if self.extended else list(VARS)
        self.rid = np.array([c["rid"] for c in C]); self.fold = np.array([c["fold"] for c in C]); self.call = np.array([c["call"] for c in C])
        self.calls = [k for k, _ in collections.Counter(self.call.tolist()).most_common()]
        self.v = {H: np.array([c["v"][H] for c in C]) for H in HORIZONS if all(H in c["v"] for c in C)}

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
    w = max(len(r["z"]) for r in rows)                           # scenarios matched on fewer variables: nothing in the columns they do not have
    A = np.array([[1.0, float(r["matched"]), r["p0"]] + [float(r["scenario"] == s) for s in scen[1:]] + list(r["z"]) + [0.0] * (w - len(r["z"])) for r in rows])
    yv = np.array([r[col] for r in rows])
    return float(np.linalg.lstsq(A, yv, rcond=None)[0][1])


def advice_test(S, K, H="180", drop_held=False):
    """Held out: the advice for every case from the other nine groups of matches, judged on the priced result H
    seconds on. Among cases with clear advice, the teams that matched it against those that did not."""
    import random
    rows, tally = [], collections.Counter()
    for name, s in S.items():
        for i, c in enumerate(s.C):
            if drop_held and c["held"]: continue
            r = s.read(i, K, True, H)
            tally["cases"] += 1
            if r["advice"] is None: tally["too few cases"] += 1; continue
            if not r["clear"]: tally["no clear advice"] += 1; continue
            tally["clear advice"] += 1
            rows.append({"rid": c["rid"], "scenario": name, "matched": c["call"] == r["advice"], "advice": r["advice"], "call": c["call"], "p0": c["p0"], "z": s.Z[i].tolist(),
                         "v": c["v"][H], "end": 100 * (c["won"] - c["p0"])})
    out = {"tally": dict(tally), "rows": len(rows), "matched": sum(r["matched"] for r in rows), "advice": dict(collections.Counter(r["advice"] for r in rows))}
    if out["matched"] < MIN_PLAYS or len(rows) - out["matched"] < MIN_PLAYS: out["verdict"] = "too few to call"; return out
    rnd = random.Random(7); by = collections.defaultdict(list)
    for r in rows: by[r["rid"]].append(r)
    ids = sorted(by)
    for col in ("v", "end"):
        e = _effect(rows, col); draws = []
        for _ in range(DRAWS):
            R = [r for k in (rnd.choice(ids) for _ in ids) for r in by[k]]
            if 0 < sum(r["matched"] for r in R) < len(R): draws.append(_effect(R, col))
        draws.sort()
        lo, hi = draws[int(0.05 * len(draws))], draws[int(0.95 * len(draws)) - 1]
        raw = [float(np.mean([r[col] for r in rows if r["matched"] == b])) for b in (True, False)]
        out[col] = {"effect": e, "range": [lo, hi], "matched_mean": raw[0], "unmatched_mean": raw[1], "verdict": "better" if lo > 0 else "worse" if hi < 0 else "no clear difference"}
    out["matches"] = len(ids)
    return out


def _two(rows, f, a=(SENT, DOUBLE), b=(NONE,)):
    """The mean of f among the calls a less its mean among the calls b, with a 90% range that takes the plays of one
    match as one draw. None under the floor."""
    out = []
    for calls in (a, b):
        R = [(c, f(c)) for c in rows if c["call"] in calls and f(c) is not None]
        if len(R) < MIN_PLAYS or len({c["rid"] for c, _ in R}) < MIN_MATCHES: return None
        v = np.array([x for _, x in R], float); mu = float(v.mean()); res = collections.defaultdict(float)
        for (c, _), e in zip(R, v - mu): res[c["rid"]] += e
        G = len(res); out.append((mu, math.sqrt(sum(e * e for e in res.values()) * G / (G - 1)) / len(v), len(v)))
    d, se = out[0][0] - out[1][0], math.hypot(out[0][1], out[1][1])
    return d, d - Z * se, d + Z * se, out[0][2], out[1][2]


_fmt = lambda g, flags=False: "too few" if not g else (f"{g[0]:+.2f} ({g[1]:+.2f} to {g[2]:+.2f})" if flags else f"{g[0]:+.1f} ({g[1]:+.1f} to {g[2]:+.1f})")


def given(C, pr):
    """His given (R-542), read with their runner 30 s into a run still under way, whatever we had done by 15 s: a
    runner sent by then against none. Its half on flags is T12 in truths.py. Its other half ("if you stay and don't
    kill or get any other advantage, you should be at a disadvantage") is read where nobody and no NPC dies meanwhile,
    and apart by whether the flag can beat the boost: with us holding the stand, a flag of theirs that cannot beat our
    boost threatens nothing, and a team that sends nobody there gets its boost."""
    R = [dict(c, call=SENT if (_delay(c) is not None and _delay(c) <= 30) else NONE) for c in answering(C) if c["clock"]["their_end"] > c["clock"]["their_off"] + 30]
    res = {"cases": len(R)}
    pr(f"\n4. His given (R-542), their runner 30 s into a run still under way ({len(R)} cases): a runner sent by then, less none (+ is the runner ahead)")
    g = _two(R, lambda c: c["lead"]["90"]); res["flags 90 s"] = g
    pr(f"   In flags, 90 s on: {_fmt(g, True)}" + (f" [{g[3]} sent, {g[4]} not]" if g else "") + ("   HOLDS" if g and g[1] > 0 else "   FAILS" if g and g[2] < 0 else "   NOT CLEAR"))
    pr("   In win points, where nobody and no NPC dies in the 90 s (a stay with no kill should be worse off, so + is expected):")
    for stand, words in (("own", "we hold the stand"), ("enemy", "they hold the stand")):
        for label, rows in ((f"{words}, every such case", [c for c in R if c["stand"] == stand]),
                            (f"{words}, {'their flag should be in before our boost' if stand == 'own' else 'a run of ours could be in before their boost'}", [c for c in R if c["stand"] == stand and c["beats"] is True]),
                            (f"{words}, {'their flag cannot be in before our boost' if stand == 'own' else 'a run of ours could not be in before their boost'}", [c for c in R if c["stand"] == stand and c["beats"] is False])):
            q = [c for c in rows if c["quiet"]["90"]]
            g90, g180, fl = _two(q, lambda c: c["v"]["90"]), _two(q, lambda c: c["v"]["180"]), _two(q, lambda c: c["lead"]["90"])
            ob = _two(q, lambda c: c["boosts"]["90"][0])
            word = "   HOLDS" if g90 and g90[1] > 0 else "   AGAINST" if g90 and g90[2] < 0 else "   NOT CLEAR" if g90 else ""
            res[label] = {"cases": len(q), "win points 90 s": g90, "win points 180 s": g180, "flags 90 s": fl, "own boosts 90 s": ob}
            pr(f"     {label}: 90 s on {_fmt(g90)}{word}; 180 s on {_fmt(g180)}; flags 90 s on {_fmt(fl, True)}; own boosts landed in 90 s {_fmt(ob, True)}" + (f" [{g90[3]} sent, {g90[4]} not]" if g90 else f" [{len(q)} cases]"))
        # all else equal in full: nobody and no NPC dies and no boost lands for either side, so that only the flags differ
        q = [c for c in R if c["stand"] == stand and c["quiet"]["90"] and c["boosts"]["90"] == [0, 0]]
        g90, fl = _two(q, lambda c: c["v"]["90"]), _two(q, lambda c: c["lead"]["90"])
        word = "   HOLDS" if g90 and g90[1] > 0 else "   AGAINST" if g90 and g90[2] < 0 else "   NOT CLEAR" if g90 else ""
        res[f"{words}, and no boost lands"] = {"cases": len(q), "win points 90 s": g90, "flags 90 s": fl}
        pr(f"     {words}, and no boost lands for either side either: 90 s on {_fmt(g90)}{word}; flags 90 s on {_fmt(fl, True)}" + (f" [{g90[3]} sent, {g90[4]} not]" if g90 else f" [{len(q)} cases]"))
    return res


# ---- what the advice was, what a team that holds off goes on to do, and the run in answer (2026-11-19, his asks)
def _mean(rows, f):
    """The mean of f over rows with a 90% range that takes the plays of one match as one draw; None under the floor."""
    R = [(c, f(c)) for c in rows if f(c) is not None]
    if len(R) < MIN_PLAYS or len({c["rid"] for c, _ in R}) < MIN_MATCHES: return None
    v = np.array([float(x) for _, x in R]); mu = float(v.mean()); res = collections.defaultdict(float)
    for (c, _), e in zip(R, v - mu): res[c["rid"]] += e
    G = len(res); se = math.sqrt(sum(e * e for e in res.values()) * G / (G - 1)) / len(v)
    return mu, mu - Z * se, mu + Z * se, len(v)


_pct = lambda g: "too few" if not g else f"{100 * g[0]:.0f}% ({100 * g[1]:.0f} to {100 * g[2]:.0f})"
_num = lambda g, d=1: "too few" if not g else f"{g[0]:+.{d}f} ({g[1]:+.{d}f} to {g[2]:+.{d}f})"


def _where(c):
    m = c["_m"]; L = m.get("length_s")
    return f"{' v '.join(m['teams'])}, {m['map']}, {m['date']}" + (f", {L // 60}:{L % 60:02d} long" if L else "")


def advice_was(S, M, K, pr, graded=()):
    """What the advice was (his ask: "I also don't see what the advice actually was"): at the read 15 s after their
    runner set off, judged 180 s on, the advice as the held-out test gives it. For each holder of the stand: the cases
    where it says hold off, where it says send, and where it says nothing clear, each described by what a team could
    see at that second; what the teams did and how they fared; and moments to look at, with the second their runner
    set off."""
    out = {}
    look = (("we are up on numbers at the main fight", lambda c: c["x"][2] > c["x"][3]), ("we are down on numbers there", lambda c: c["x"][2] < c["x"][3]),
            ("we stand on their side of the stand", lambda c: None if c["more"][1] is None else c["more"][1] < 0), ("we stand on our own side of it", lambda c: None if c["more"][1] is None else c["more"][1] > 0),
            ("they stand on their own side of it", lambda c: None if c["more"][2] is None else c["more"][2] > 0),
            ("their runner is a backline monk", lambda c: c["more"][3] > 0), ("the flag can beat the boost", lambda c: c["beats"]),
            ("the base res is under 40 s away", lambda c: c["more"][0] < 40), ("we are the stronger team (by 100 points or more)", lambda c: c["x"][6] >= 100), ("we are the weaker team (by 100 or more)", lambda c: c["x"][6] <= -100))
    nums = (("flag lead, in flags", lambda c: c["x"][0], 2), ("seconds to the boost", lambda c: c["x"][1], 0), ("seconds their flag should take", lambda c: c["more"][7], 0),
            ("own morale (the eight summed)", lambda c: c["x"][4], 0), ("their morale", lambda c: c["x"][5], 0), ("their team's snares", lambda c: c["more"][5], 0))
    for name, s in S.items():
        if "single run" not in name or "; 15 s after" not in name: continue
        R = [s.read(i, K, True, "180") for i in range(len(s.C))]
        G = {"hold off": [], "send a runner": [], "nothing clear": []}
        for c, r in zip(s.C, R):
            key = "nothing clear" if not r["clear"] else "hold off" if r["advice"] == NONE else "send a runner" if r["advice"] in (SENT, DOUBLE) else "nothing clear"
            G[key].append(dict(c, _margin=r["margin"] or 0, _m=M[c["rid"]]))
        pr(f"\n   {name}: the advice says hold off in {len(G['hold off'])}, send a runner in {len(G['send a runner'])}, nothing clear in {len(G['nothing clear'])}")
        o = out[name] = {k: {"cases": len(v)} for k, v in G.items()}
        pr(f"     {'what a team could see at that second':52} {'hold off':>12} {'send':>12} {'nothing clear':>14}")
        for label, f in look:
            sh = {k: (np.mean([bool(f(c)) for c in v if f(c) is not None]) if len([c for c in v if f(c) is not None]) >= MIN_PLAYS else None) for k, v in G.items()}
            for k in G: o[k][label] = sh[k]
            pr(f"     {label:52} " + " ".join(f"{('too few' if sh[k] is None else f'{100 * sh[k]:.0f}%'):>{w}}" for k, w in (("hold off", 12), ("send a runner", 12), ("nothing clear", 14))))
        for label, f, d in nums:
            mu = {k: (np.mean([f(c) for c in v if f(c) is not None]) if len([c for c in v if f(c) is not None]) >= MIN_PLAYS else None) for k, v in G.items()}
            for k in G: o[k][label] = mu[k]
            pr(f"     {label:52} " + " ".join(f"{('too few' if mu[k] is None else f'{mu[k]:+.{d}f}' if d else f'{mu[k]:.0f}'):>{w}}" for k, w in (("hold off", 12), ("send a runner", 12), ("nothing clear", 14))))
        for k, did in (("hold off", NONE), ("send a runner", SENT)):
            v = G[k]
            if not v: continue
            a, b = [c for c in v if c["call"] == did], [c for c in v if c["call"] != did]
            ga, gb = _mean(a, lambda c: c["v"]["180"]), _mean(b, lambda c: c["v"]["180"])
            o[k]["did as advised"] = {"cases": len(a), "win points 180 s": ga}; o[k]["did otherwise"] = {"cases": len(b), "win points 180 s": gb}
            pr(f"     where it says {k}: {len(a)} did, 180 s on {_num(ga)}; {len(b)} did otherwise, {_num(gb)}")
            best = sorted(v, key=lambda c: (c["rid"] not in graded, -c["_margin"]))[:3]
            o[k]["look at"] = [{"rid": c["rid"], "their_runner_sets_off": c["clock"]["their_off"], "said": c["said"], "call": c["call"]} for c in best]
            for c in best:
                pr(f"       look at: {_where(c)}; their runner sets off at {cl(c['clock']['their_off'])} ({c['said']}); {c['team']} at 15 s: {c['call']}; similar spots favour {k} by {c['_margin']:.1f} win points; "
                   f"what followed 180 s on {c['v']['180']:+.1f}: https://gvg.report/report/{c['rid']}#map")
    return out


def held_off(S, D, M, K, pr):
    """What a team with no runner out 15 s after theirs set off goes on to do, and how each path fares (his ask: is
    "hold off" advice, or teams seeing a run that is failing?). The paths: a runner 15 to 30 s after theirs; one
    later while their flag is still out; one only once their run has ended; none in the 90 s. Beside each: how often
    their flag got in, how often we pushed their flagger meanwhile, how often one of theirs died in the first 60 s.
    Then the test of the question: where the advice says hold off, the teams that held off against those that sent,
    apart by whether their flag got in."""
    push = collections.defaultdict(list)
    for p in D["plays"]:
        if p["play"] == "push flagger": push[(p["rid"], p["team"])].append((p["t0"], p["t1"]))
    out = {}
    def path(c):
        k, d = c["clock"], _delay(c)
        if d is None or d > 90 and k["our_off"] >= k["their_end"] + 30: return "no runner in the next 90 s" if (d is None or d > 90) else None
        if d <= 30: return "a runner 15 to 30 s after theirs"
        if k["our_off"] < k["their_end"]: return "a runner later, their flag still out"
        return "a runner once their run had ended"
    pushed = lambda c: any(t0 <= c["clock"]["their_end"] and t1 >= c["clock"]["their_off"] for t0, t1 in push.get((c["rid"], c["team"]), ()))
    for name, s in S.items():
        if "single run" not in name or "; 15 s after" not in name: continue
        rows = [c for c in s.C if c["call"] == NONE]
        pr(f"\n   {name}: {len(rows)} with no runner yet. What they went on to do:")
        o = out[name] = {}
        by = collections.defaultdict(list)
        for c in rows: by[path(c) or "a runner later"].append(c)
        for k in ("a runner 15 to 30 s after theirs", "a runner later, their flag still out", "a runner once their run had ended", "no runner in the next 90 s"):
            v = by.get(k, [])
            if not v: continue
            g = _mean(v, lambda c: c["v"]["180"]); fl = _mean(v, lambda c: c["lead"]["180"])
            o[k] = {"cases": len(v), "their flag got in": float(np.mean([c["their_flag"] == "captured" for c in v])), "pushed their flagger": float(np.mean([pushed(c) for c in v])),
                    "a kill in 60 s": float(np.mean([c["hard"]["60"]["deaths"][1] > 0 for c in v])), "win points 180 s": g, "flags 180 s": fl}
            pr(f"     {k:40} {len(v):4} ({100 * len(v) // len(rows)}%): their flag got in {100 * o[k]['their flag got in']:.0f}%; we pushed their flagger {100 * o[k]['pushed their flagger']:.0f}%; "
               f"one of theirs died within 60 s {100 * o[k]['a kill in 60 s']:.0f}%; 180 s on {_num(g)} win points, flag lead {_num(fl, 2)}")
        R = [s.read(i, K, True, "180") for i in range(len(s.C))]
        adv = [dict(c) for c, r in zip(s.C, R) if r["clear"] and r["advice"] == NONE]
        pr(f"     where the advice says hold off ({len(adv)}), holding off less sending, 180 s on, in win points:")
        for label, sub in (("every such case", adv), ("their flag got in", [c for c in adv if c["their_flag"] == "captured"]), ("their flag did not get in", [c for c in adv if c["their_flag"] != "captured"])):
            g = _two(sub, lambda c: c["v"]["180"], a=(NONE,), b=(SENT, DOUBLE))
            cnt = collections.Counter(c["call"] == NONE for c in sub)
            o[f"hold off advised, {label}"] = {"held off": cnt[True], "sent": cnt[False], "held off less sent": g}
            pr(f"       {label:28} {_fmt(g)}   [{cnt[True]} held off, {cnt[False]} sent]")
        sh = lambda v: float(np.mean([c["their_flag"] == "captured" for c in v])) if v else float("nan")
        pr(f"       their flag got in after {100 * sh([c for c in adv if c['call'] == NONE]):.0f}% of the holds and {100 * sh([c for c in adv if c['call'] != NONE]):.0f}% of the sends there")
    return out


def run_in_answer(C, M, pr):
    """The run in answer, judged on whether it held even (R-540): our flag in, how long it took against a clean run
    for the hall (back to the spawn and the carry), what it cost at the main fight meanwhile, and the priced result.
    By who was sent, and by their team's snares. As it fell, set against nothing else: who a team sends follows from
    its build and its spot, so this says where to look, never who to send."""
    rows = [dict(c, _m=M[c["rid"]]) for c in answering(C) if c["our_runner"] and _delay(c) is not None and c["clock"]["our_off"] <= c["clock"]["their_end"]]
    for c in rows:
        took = c["t1"] - c["clock"]["our_off"]
        c["_late"] = (took / (BACK_AND_RUN * c["_m"]["run_s"])) if c["our_capped"] and took > 0 else None
        c["_net"] = None if not c["main_deaths"] else c["main_deaths"][0] - c["main_deaths"][1]
    pr(f"\n7. The run in answer ({len(rows)} runs set off while their flag was still out), as it fell")
    out = {"runs": len(rows)}
    def table(title, groups):
        pr(f"\n   {title}")
        pr(f"     {'':34} {'runs':>5}  {'our flag got in':>22}  {'time against a clean run':>26}  {'own less their deaths at main':>30}  {'win points 90 s on':>22}  {'180 s on':>22}")
        for label, v in groups:
            g = {"in": _mean(v, lambda c: c["our_capped"]), "late": _mean(v, lambda c: c["_late"]), "net": _mean(v, lambda c: c["_net"]), "v90": _mean(v, lambda c: c["v"]["90"]), "v180": _mean(v, lambda c: c["v"]["180"])}
            out[f"{title}: {label}"] = dict(g, runs=len(v))
            late = "too few" if not g["late"] else f"x{g['late'][0]:.2f} ({g['late'][1]:.2f} to {g['late'][2]:.2f})"
            pr(f"     {label:34} {len(v):5}  {_pct(g['in']):>22}  {late:>26}  {_num(g['net'], 2):>30}  {_num(g['v90']):>22}  {_num(g['v180']):>22}")
    table("every run", [("every run in answer", rows)])
    table("by our runner's line", [(k, [c for c in rows if line_of(c["our_runner"]) == k]) for k in ("a backline monk", "a midline player", "a frontline player")])
    names = [k for k, n in collections.Counter(c["our_runner"]["role"].rstrip(" 0123456789AB").strip() for c in rows).most_common() if n >= MIN_PLAYS]
    table("by our runner", [(k, [c for c in rows if c["our_runner"]["role"].rstrip(" 0123456789AB").strip() == k]) for k in names])
    sp = [c["our_runner"]["speed"] for c in rows]; lo, hi = np.percentile(sp, [33.3, 66.7])
    table("by our runner's speed skills", [("the slowest third", [c for c in rows if c["our_runner"]["speed"] <= lo]), ("the middle third", [c for c in rows if lo < c["our_runner"]["speed"] <= hi]), ("the fastest third", [c for c in rows if c["our_runner"]["speed"] > hi])])
    table("by our runner's self-defence", [("none on his bar", [c for c in rows if not c["our_runner"]["self_defence"]]), ("some on his bar", [c for c in rows if c["our_runner"]["self_defence"]])])
    sn = [c["snares"][1] for c in rows]; lo, hi = np.percentile(sn, [33.3, 66.7])
    table("by their team's snares", [("the fewest third", [c for c in rows if c["snares"][1] <= lo]), ("the middle third", [c for c in rows if lo < c["snares"][1] <= hi]), ("the most third", [c for c in rows if c["snares"][1] > hi])])
    table("by who holds the stand", [("we hold it", [c for c in rows if c["stand"] == "own"]), ("they hold it", [c for c in rows if c["stand"] == "enemy"])])
    return out


# ---- the report
def build(path):
    D, M = load(path)
    B, P = prices(D, M)
    C, skipped = cases(D, M, B)
    by = collections.defaultdict(list)
    for c in [c for c in C if c["scenario"]] + read_cases(C): by[c["scenario"]].append(c)
    order = lambda n: (0 if "boost" in n else 2 if "in hand" in n else 1, n.split(";")[0], n.split(";")[1] if ";" in n else "", n)
    S = {k: Scenario(by[k]) for k in sorted(by, key=order)}
    return D, M, B, P, C, skipped, S


def report(path, out_json=None):
    D, M, B, P, C, skipped, S = build(path)
    pr = print
    pr(f"Similar cases for the flag family (R-451, R-531, R-538 to R-544), on {len(M)} matches: {len(C)} cases" + "".join(f"; set aside, {k}: {v}" for k, v in skipped.items()))
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
    pr(f"\n2. Similar cases. Matched on: {', '.join(VARS)}; and for their run and our answer also: {', '.join(MORE)}.")
    pr("   K (how many nearest cases a call is read from), by how well it foretells a case's own result: " + "; ".join(f"K {k}: miss {math.sqrt(e):.2f} win points ({n:,} cases)" for k, (e, n) in err.items()) + f". Chosen: {K}.")
    res = {"prices": P, "K": K, "k_error": {k: e for k, (e, n) in err.items()}, "scenarios": {}, "skipped": dict(skipped), "notes": D["_notes"]}
    for name, s in S.items():
        n = len(s.C); cnt = collections.Counter(s.call.tolist()); reads = " after their runner set off" in name
        pr(f"\n   {name}: {n} cases in {len(set(s.rid.tolist()))} matches")
        for a in s.calls:
            sel = s.call == a
            hd = [c["hard"]["180"] for c, ok in zip(s.C, sel) if ok]
            mean = lambda f: float(np.mean([f(h) for h in hd]))
            lc = [h["lead_change"] for h in hd if h["lead_change"] is not None]
            pr(f"     {a:34} {cnt[a]:5}   as it fell, 180 s on: {s.v['180'][sel].mean():+5.1f} win points; flag lead {np.mean(lc):+.2f}; deaths {mean(lambda h: h['deaths'][0]):.2f} own, {mean(lambda h: h['deaths'][1]):.2f} theirs; "
               f"NPCs lost {mean(lambda h: h['npcs'][0]):.2f} own, {mean(lambda h: h['npcs'][1]):.2f} theirs" + ("" if cnt[a] >= MIN_PLAYS else "   (under the floor: no verdict)"))
        out = res["scenarios"][name] = {"cases": n, "calls": dict(cnt)}
        if reads:
            out["a runner less none"] = {}
            for H in HORIZONS:
                fl, wp = _two(s.C, lambda c: c["lead"][H]), _two(s.C, lambda c: c["v"][H]); out["a runner less none"][H] = {"flags": fl, "win points": wp}
                pr(f"     a runner sent (single or double) less none yet, {H:>3} s on: flag lead {_fmt(fl, True)}; win points {_fmt(wp)}")
        R = [s.read(i, K, False) for i in range(n)]
        adv = collections.Counter((r["advice"], r["clear"]) for r in R if r["advice"]); ver = collections.Counter(r["verdict"] for r in R)
        out.update(verdicts=dict(ver), clear_advice={a: v for (a, c), v in adv.items() if c})
        if not adv: pr("     no two calls with enough cases: no verdict in this scenario"); continue
        clear = sum(v for (a, c), v in adv.items() if c)
        pr("     in similar spots, 180 s on, the better call is: " + ("; ".join(f"{a} in {v} ({100 * v // n}%)" for (a, c), v in sorted(adv.items(), key=lambda kv: -kv[1]) if c) or "nowhere clear")
           + f"; no clear difference in {n - clear - ver['too few cases']} ({100 * (n - clear - ver['too few cases']) // n}%)" + (f"; too few cases in {ver['too few cases']}" if ver["too few cases"] else ""))
    pr("\n3. The held-out advice test: where the advice is clear, did teams that matched it do better? (advice and prices from the other nine groups of matches;")
    pr("   matched against not matched in win points, set against the same scenario and position, with its 90% range)")
    res["advice_test"] = {}
    def line(label, t):
        res["advice_test"][label] = t; ta = t["tally"]
        adv = "; ".join(f"{k} {v}" for k, v in sorted(t["advice"].items(), key=lambda kv: -kv[1]))
        if "v" not in t: pr(f"   {label}: {ta.get('cases', 0)} cases, clear advice in {t['rows']}: too few to call (matched {t['matched']})" + (f" [{adv}]" if adv else "")); return
        e, en = t["v"], t["end"]
        pr(f"   {label}: {ta.get('cases', 0)} cases, clear advice in {t['rows']} ({adv}), matched {t['matched']}: {e['effect']:+.1f} ({e['range'][0]:+.1f} to {e['range'][1]:+.1f}) {e['verdict']}; "
           f"in how the match ended {en['effect']:+.1f} ({en['range'][0]:+.1f} to {en['range'][1]:+.1f})")
    boost = {k: s for k, s in S.items() if "boost" in k}
    for H in ("90", "180"):
        line(f"their boost 30 s away, every case, {H} s on", advice_test(boost, K, H))
        line(f"their boost 30 s away, without the flag only held at home, {H} s on", advice_test(boost, K, H, drop_held=True))
    for R in READS:
        Sx = {k: s for k, s in S.items() if f"; {R} s after their runner set off" in k}
        for H in HORIZONS: line(f"their run, our answer read at {R} s, {H} s on", advice_test(Sx, K, H))
    res["given"] = given(C, pr)
    graded = set()
    dv = os.path.join(REPO, "data", "model", "dev_set.json")
    if os.path.exists(dv): graded = {w["rid"] for w in json.load(open(dv))["whole_game"] if w.get("set") == "f1"}
    pr("\n5. What the advice was: their run and our answer, read 15 s after their runner set off and judged 180 s on (the advice as the held-out test gives it)")
    res["advice_was"] = advice_was(S, M, K, pr, graded)
    pr("\n6. What a team with no runner out at 15 s goes on to do")
    res["held_off"] = held_off(S, D, M, K, pr)
    res["run_in_answer"] = run_in_answer(C, M, pr)
    held = sum(1 for c in C if c["held"])
    pr(f"\n   The flag only held at home at a boost (a boost run that denies nothing while the rest fall back): {held} of {sum(1 for c in C if c['kind'] == 'boost')} boost cases.")
    if out_json: json.dump(res, open(out_json, "w"), ensure_ascii=False, indent=1, default=float)
    return res


def case(path, rid, at):
    """One decision as its card: the situation, each call's worth among the nearest cases, the verdict, and three of
    the nearest cases of each call with their replay links and the second to look at. Their run and our answer is
    shown at its first read. A verdict is a reading, not advice, until the held-out test shows a gain for its scenario."""
    D, M, B, P, C, skipped, S = build(path)
    K, _ = choose_k(S)
    t = (lambda a: int(a[0]) * 60 + int(a[1]))(at.split(":"))
    hits = [(abs(c["t"] - t), c.get("read", 0), name, i) for name, s in S.items() for i, c in enumerate(s.C) if c["rid"].startswith(rid)]
    if not hits: sys.exit("no flag or boost case in that match")
    _, _, name, i = min(hits)
    s = S[name]; c = s.C[i]; m = M[c["rid"]]; r = s.read(i, K, False)
    print(f"{' v '.join(m['teams'])}, {m['map']}, {m['date']}, {cl(c['t'])}: https://gvg.report/report/{c['rid']}#map")
    print(f"  {c['said']}\n  scenario: {name}; {c['team']}'s call: {c['call']}; chance of winning at that second {100 * c['p0']:.0f}%")
    print("  matched on: " + "; ".join(f"{n} {v:.0f}" if isinstance(v, (int, float)) and abs(v) >= 10 else f"{n} {v}" for n, v in zip(VARS + MORE, c["x"] + (c["more"] or []))))
    print("  what followed: " + ", ".join(f"{c['v'][H]:+.1f} win points at {H} s" for H in HORIZONS if H in c["v"]) + f"; at 180 s deaths {c['hard']['180']['deaths']}, NPCs lost {c['hard']['180']['npcs']}, flag lead {c['hard']['180']['lead_change']}")
    for a, w in sorted(r["calls"].items(), key=lambda kv: -kv[1]["worth"]):
        print(f"  {a:34} worth {w['worth']:+5.1f} win points 180 s on (90% range {w['worth'] - Z * w['se']:+.1f} to {w['worth'] + Z * w['se']:+.1f}), from {w['plays']} plays in {w['matches']} matches")
        for j in w["near"][:3]:
            x = s.C[j]; mm = M[x["rid"]]
            print(f"      {' v '.join(mm['teams'])}, {mm['map']}, {mm['date']}, {cl(x['t'])} ({x['team']}; {x['v']['180']:+.1f}): https://gvg.report/report/{x['rid']}#map")
    print(f"  the better call in similar spots: {r['advice']}" + (f", ahead of the next by {r['margin']:.1f} win points (90% range {r['range'][0]:+.1f} to {r['range'][1]:+.1f})" if r["advice"] else "") + f"; the call made: {r['verdict']}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "test": report(a[1], a[a.index("--json") + 1] if "--json" in a else None)
    elif len(a) >= 4 and a[0] == "case": case(a[1], a[2], a[3])
    else: print(__doc__)
