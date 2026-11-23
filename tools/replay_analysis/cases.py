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
     read too and dropped, R-544; it is read in the timing ladder only, R-545). The reads, the windows and the
     position are on one clock, their runner's set-off (R-546). Where our own runner was already out when theirs
     set off, the decision is another one and has its own scenarios: our flag just in with theirs still on its way,
     run again or not, read 15 and 30 s after our cap (R-546). At each read their run is still under way and we had sent nobody by the read
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

5. The timing ladder (R-545; `cases.py ladder`): the check of the readings themselves, run at a checkpoint before
   anything is read from the advice. Do the run, stay and timing readings go with flag advantage, in the engine's
   tally and in the replay's own caps and boosts; are the clocks one; is the stand read right. A report, never a
   verdict; the 45 s read is kept here only.

Usage:  python3 cases.py test <plays file from `moments.py all`> [--json <out.json>]     the whole report
        python3 cases.py case <plays file> <report id> <m:ss>                          one decision, its calls and cases
        python3 cases.py cards <plays file> [f1 | <report id>] [--site <main>/data/model/flag_cards.json]     every flag decision of the graded games, or of one match, as sentences
        python3 cases.py ladder <plays file> [--json <out.json>]                         the timing ladder: a check of the flag readings (no prices, no advice)
        python3 cases.py main-fight <plays file> [--json <out.json>]                     the split family's other half: the main fight while a split is out
        python3 cases.py splits <plays file> [--json <out.json>]                         the split family, stage 1: the answer to a split, its readings checked and what followed each answer
        python3 cases.py pushes <plays file> [--json <out.json>]                         pushing the flagger, stage 1: its readings checked and what followed each push
        python3 cases.py held <plays file> [--json <out.json>]                           a team held in its base, stage 1: its readings checked and what followed each hold
        python3 cases.py res <plays file> [--json <out.json>]                            the base res, stage 1: a team in the enemy's base when their dead come back
        python3 cases.py opening <plays file> [--json <out.json>]                        the opening, stage 1: the first flag and where the players went
A reading tool over the plays file: it writes no prepared data and is in no cache key (cache.REPORT_LAYER)."""
import collections, json, math, os, re, sys
import numpy as np
from common import REPO

MIN_PLAYS, MIN_MATCHES = 30, 15                  # R-538: the floor under any verdict
LEVEL_MIN, RIDGE = 60, 10.0                      # setting the nearest cases level: the cases of a call a slope is fitted from at least, and how hard it is held towards none (Claude's draft)
K_TRY = (30, 45, 60, 90, 120)
Z = 1.645                                        # a 90% range
DRAWS = 300
PRICE = ("strength gap (per 100 points of rating)", "a flag of lead", "death penalty (per 15%, one death's worth)", "morale boost (+10% on all eight)", "a pit NPC", "Lord health (per 10%)")
SCALE = (100.0, 1.0, 15.0, 80.0, 1.0, 0.1)       # the unit each price is quoted in
VARS = ("flag lead", "seconds to the boost", "own players at the main fight", "their players at the main fight", "own morale", "their morale", "strength gap", "the hall's flag run, s",
        "own chance of winning at that second")       # the last one is the whole position as the prices read it (2026-11-19: teams that sent nobody were already winning, and the eight before it did not hold that level)
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
        x = [st["flag_lead"], st["boost_in"], st["main"][0], st["main"][1], af["90"]["morale"][0][0], af["90"]["morale"][1][0], gap, m["run_s"], 100 * p0]
        # what the 60 s before the decision did to the chance of winning, in win points: the test of a call against what came before it (None in the first minute)
        bf, pre = p.get("before"), None
        if bf and bf["after"]["lead"][0] is not None and "npcs_lost" in bf["state"]: pre = 100 * (p0 - chance(beta, position(bf["state"], bf["after"], gap, False)))
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
                    "from_cap": bool((p.get("clock") or {}).get("from_cap")), "flag_up": p.get("our_flag_up"), "pre": pre, "track": p.get("track"), "lead": {H: af[H]["lead_change"] for H in HS}, "quiet": {H: af[H]["deaths"] == [0, 0] and af[H]["npcs"] == [0, 0] for H in HS},
                    "hard": {H: {"deaths": af[H]["deaths"], "npcs": af[H]["npcs"], "lead_change": af[H]["lead_change"], "boosts": af[H]["boosts"]} for H in HS}})
    return out, skipped


def _delay(c):
    """Seconds from the decision's clock to our runner setting off, None when we sent nobody. The clock (`anchor` on
    the play) is their runner's set-off; where our runner was already out when theirs set off it is our cap."""
    k = c["clock"]
    return None if k["our_off"] is None else k["our_off"] - k["anchor"]


def answering(C):
    """The cases of their run and our answer that can be read at a fixed second."""
    return [c for c in C if c["kind"] == "flag" and not c["in_hand"] and c["clock"] and c["stand"] in ("own", "enemy")]


def read_cases(C):
    """Our answer to their run as it stands 15 and 30 s after their runner set off (R-542, R-543). At each read their
    run is still under way, and we had sent nobody by the read before; the call is whether a runner of ours has set
    off by now (the second player of a double run told apart), or none yet. Reads, windows and position are on one
    clock (R-546). Where our own runner was already out when theirs set off, the decision is another one, read from
    our cap with their flag still on its way: run again, or not (R-546); its cases are scenarios of their own."""
    out = []
    for c in answering(C):
        k, delay = c["clock"], _delay(c)
        for n, R in enumerate(READS):
            if k["their_end"] <= k["anchor"] + R: break                             # their run is over: nothing left to answer
            if n and delay is not None and delay <= READS[n - 1]: break             # we had already sent a runner by the read before
            sent = delay is not None and delay <= R
            if c["from_cap"]: name = f"Our flag just in, their {c['their']} still on its way; {R} s after our cap" + (f", nobody sent by {READS[n - 1]} s" if n else "")
            else: name = f"Their {c['their']}; {'we hold the stand' if c['stand'] == 'own' else 'they hold the stand'}; {R} s after their runner set off" + (f", nobody sent by {READS[n - 1]} s" if n else "")
            out.append(dict(c, read=R, scenario=name, call=(DOUBLE if k["our_double"] else SENT) if sent else NONE))
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
        self.y = dict(self.v, pre=np.array([np.nan if c.get("pre") is None else c["pre"] for c in C], float), p0=np.array([100 * c["p0"] for c in C]))
        self._b = {}

    def slope(self, call, fold, key):
        """How the outcome `key` runs with the matching variables among the cases of one call, from the other groups
        of matches: a straight fit, held towards no slope (ridge), used to set a call's nearest cases level with
        the case they are read for. None where the call has too few cases to carry it (under LEVEL_MIN): no levelling."""
        k = (call, int(fold), key)
        if k not in self._b:
            ok = (self.call == call) & (self.fold != fold) & ~np.isnan(self.y[key])
            if ok.sum() < LEVEL_MIN: self._b[k] = None
            else:
                Zc, yc = self.Z[ok], self.y[key][ok]
                A = Zc - Zc.mean(axis=0)
                self._b[k] = np.linalg.solve(A.T @ A + RIDGE * np.eye(A.shape[1]), A.T @ (yc - yc.mean()))
        return self._b[k]

    def level(self, i, j, call, key):
        """The outcome `key` among the cases j of `call`, set level with case i: each neighbour's outcome less what
        its own distance from case i on the matching variables is worth (nearest cases are never the same spot, and
        the rarer call's nearest are further off). The mean, its spread with the plays of one match as one draw,
        the plays and the matches. Without enough cases to fit the slope it is the plain mean."""
        j = j[~np.isnan(self.y[key][j])]
        if len(j) == 0: return None
        b = self.slope(call, self.fold[i], key)
        v = self.y[key][j] - ((self.Z[j] - self.Z[i]) @ b if b is not None else 0.0)
        mu = float(v.mean()); res = collections.defaultdict(float)
        for r, e in zip(self.rid[j], v - mu): res[r] += e
        G = len(res)
        return mu, math.sqrt(sum(e * e for e in res.values()) * (G / (G - 1) if G > 1 else 1)) / len(v), len(v), G

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
            mu, se, n, G = self.level(i, j, a, H); W[a] = {"worth": mu, "se": se, "plays": n, "matches": G, "near": j, "plain": float(self.v[H][j].mean())}
            # like cases have to stand round the case: where its own chance of winning lies outside nine in ten of a call's nearest cases, they are all to one side
            # of it and the levelling would be reading beyond them (옷옷옷옷 v RACK 6:15, a team at 92% in its own pit): no verdict from such a spot
            lo_, hi_ = np.percentile(self.y["p0"][j], [5, 95]); W[a]["beside"] = bool(lo_ <= self.y["p0"][i] <= hi_)
        out = {"calls": W, "advice": None, "clear": False, "verdict": "too few cases", "margin": None, "range": None}
        if len(W) < 2: return out
        order = sorted(W, key=lambda a: -W[a]["worth"])
        best, nxt = order[0], order[1]
        d, se = W[best]["worth"] - W[nxt]["worth"], math.hypot(W[best]["se"], W[nxt]["se"])
        out.update(advice=best, clear=d - Z * se > 0, margin=d, range=[d - Z * se, d + Z * se])
        if not (W[best]["beside"] and W[nxt]["beside"]):
            out.update(clear=False, verdict="an unusual spot: no like cases round it", unusual=True); return out
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
                         "v": c["v"][H], "end": 100 * (c["won"] - c["p0"]), "pre": c.get("pre")})
    out = {"tally": dict(tally), "rows": len(rows), "matched": sum(r["matched"] for r in rows), "advice": dict(collections.Counter(r["advice"] for r in rows))}
    if out["matched"] < MIN_PLAYS or len(rows) - out["matched"] < MIN_PLAYS: out["verdict"] = "too few to call"; return out
    rnd = random.Random(7); by = collections.defaultdict(list)
    for r in rows: by[r["rid"]].append(r)
    ids = sorted(by)
    for col in ("v", "end", "pre"):                                              # "pre": the same test on the 60 s before the decision, which no answer can change (SPEC 5, rule 4)
        use = [r for r in rows if r[col] is not None]
        if col == "pre" and (sum(r["matched"] for r in use) < MIN_PLAYS or len(use) - sum(r["matched"] for r in use) < MIN_PLAYS): continue
        byc = collections.defaultdict(list)
        for r in use: byc[r["rid"]].append(r)
        idc = sorted(byc)
        e = _effect(use, col); draws = []
        for _ in range(DRAWS):
            R = [r for k in (rnd.choice(idc) for _ in idc) for r in byc[k]]
            if 0 < sum(r["matched"] for r in R) < len(R): draws.append(_effect(R, col))
        draws.sort()
        lo, hi = draws[int(0.05 * len(draws))], draws[int(0.95 * len(draws)) - 1]
        raw = [float(np.mean([r[col] for r in use if r["matched"] == b])) for b in (True, False)]
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
    R = [dict(c, call=SENT if (_delay(c) is not None and _delay(c) <= 30) else NONE) for c in answering(C) if not c["from_cap"] and c["clock"]["their_end"] > c["clock"]["their_off"] + 30]
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
        if "single run" not in name or "; 15 s after their runner set off" not in name: continue
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
        if "single run" not in name or "; 15 s after their runner set off" not in name: continue
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
    rows = [dict(c, _m=M[c["rid"]]) for c in answering(C) if not c["from_cap"] and c["our_runner"] and _delay(c) is not None and c["clock"]["our_off"] <= c["clock"]["their_end"]]
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


# ---- do the similar cases of each answer start level, and were they level before (2026-11-19)
def level_check(s, a=NONE, b=(SENT, DOUBLE)):
    """Were the teams that gave two answers on the same road before they gave them? The difference between the
    answers (a less b), over the cases of one scenario, in three things: the chance of winning at the decision
    second (plain: what the matching has to take out); what the 60 s before the decision had done to that chance,
    plain and set against the same position (a straight fit on the matching variables); and the 180 s after, set
    against the same position. The 60 s before is the test (SPEC 5, rule 4): it is matched on nowhere and no answer
    can change it, so a difference there says the answer marks the situation and what follows it is no advice.
    Ranges from drawing whole matches again."""
    import random
    idx = [i for i in range(len(s.C)) if s.call[i] == a or s.call[i] in b]
    isa = np.array([float(s.call[i] == a) for i in idx])
    if isa.sum() < MIN_PLAYS or (1 - isa).sum() < MIN_PLAYS: return {}
    rid = s.rid[idx]; by = collections.defaultdict(list)
    for n_, r in enumerate(rid): by[r].append(n_)
    ids, out = sorted(by), {}
    def est(y, adjust, rows):
        ok = rows[~np.isnan(y[rows])]
        if isa[ok].sum() < 5 or (1 - isa[ok]).sum() < 5: return None
        if not adjust: return float(y[ok][isa[ok] == 1].mean() - y[ok][isa[ok] == 0].mean())
        A = np.column_stack([np.ones(len(ok)), isa[ok], s.Z[idx][ok]])
        return float(np.linalg.lstsq(A, y[ok], rcond=None)[0][1])
    for label, key, adjust in (("chance of winning at the start, plain", "p0", False), ("the 60 s before, plain", "pre", False), ("the 60 s before, same position", "pre", True),
                               ("180 s on, plain", "180", False), ("180 s on, same position", "180", True)):
        if key not in s.y: continue
        y = s.y[key][idx]; allr = np.arange(len(idx)); e = est(y, adjust, allr)
        if e is None: continue
        rnd, dr = random.Random(7), []
        for _ in range(DRAWS):
            rows = np.array([n_ for k in (rnd.choice(ids) for _ in ids) for n_ in by[k]])
            d = est(y, adjust, rows)
            if d is not None: dr.append(d)
        dr.sort()
        out[label] = (e, dr[int(0.05 * len(dr))], dr[int(0.95 * len(dr)) - 1], int(isa.sum()), int(len(isa) - isa.sum()))
    return out


PATHS = ("a runner within 15 s", "a runner 15 to 90 s on", "no runner for 90 s")
def _path(c):
    d = _delay(c)
    return PATHS[2] if d is None or d > 90 else PATHS[0] if d <= 15 else PATHS[1]


def _fell_row(pr, label, v, out, indent="     "):
    if not v: return
    h = [c["hard"]["180"] for c in v]; m = lambda f: float(np.mean([f(x) for x in h if f(x) is not None]))
    pre = [c["pre"] for c in v if c.get("pre") is not None]
    row = {"cases": len(v), "win chance at the start": 100 * float(np.mean([c["p0"] for c in v])), "the 60 s before": float(np.mean(pre)) if pre else None, "their flag in": 100 * float(np.mean([c["their_flag"] == "captured" for c in v])),
           "flags": m(lambda x: x["lead_change"]), "net kills": m(lambda x: x["deaths"][1] - x["deaths"][0]), "own boosts": m(lambda x: x["boosts"][0]), "their boosts": m(lambda x: x["boosts"][1]),
           "net pit NPCs": m(lambda x: x["npcs"][1] - x["npcs"][0]), "win points": float(np.mean([c["v"]["180"] for c in v]))}
    out[label] = row
    pr(f"{indent}{label:38} {len(v):5}  {row['win chance at the start']:8.0f}%  {('' if row['the 60 s before'] is None else format(row['the 60 s before'], '+.1f')):>10}  {row['their flag in']:12.0f}%  {row['flags']:+6.2f}  {row['net kills']:+9.2f}  "
       f"{row['own boosts']:9.2f}  {row['their boosts']:11.2f}  {row['win points']:+10.1f}" + ("   (under the floor)" if len(v) < MIN_PLAYS else ""))


FELL_HEAD = f"{'':38} {'cases':>5}  {'started at':>9}  {'60 s before':>10}  {'their flag in':>13}  {'flags':>6}  {'net kills':>9}  {'own boost':>9}  {'their boost':>11}  {'win points':>10}"
def as_it_fell(C, pr):
    """What followed each answer, as it fell, 180 s on (his reading of 2026-11-19, the form he found clear): by how
    soon our runner set off, and for no runner by whether their flag got in. Beside each: the chance of winning the
    team started from and what the 60 s before had done to it, so that a row which only shows who was already
    winning is seen as that. A description: it compares nothing with a like spot, and is no advice."""
    out = {}
    groups = (("Their single run; we hold the stand", lambda c: not c["from_cap"] and c["their"] == "single run" and c["stand"] == "own"),
              ("Their single run; they hold the stand", lambda c: not c["from_cap"] and c["their"] == "single run" and c["stand"] == "enemy"),
              ("Our flag just in, their single run still on its way: run again, or not (from our cap)", lambda c: c["from_cap"] and c["their"] == "single run"))
    live = [c for c in answering(C) if c["clock"]["their_end"] > c["clock"]["anchor"] + READS[0]]
    pr(f"\n8. As it fell, 180 s on: what followed each answer (their run still under way {READS[0]} s in; a description, set against no like spot)")
    pr("   started at = own chance of winning at the decision second; 60 s before = what the minute before had done to it, in win points; flags = change in flag lead;")
    pr("   net kills = their deaths less ours; boosts = morale boosts landed; win points = change in the chance of winning.")
    for name, f in groups:
        R = [c for c in live if f(c)]
        pr(f"\n   {name} ({len(R)})"); pr("     " + FELL_HEAD)
        o = out[name] = {}
        for k in PATHS: _fell_row(pr, k, [c for c in R if _path(c) == k], o)
        none = [c for c in R if _path(c) == PATHS[2]]
        _fell_row(pr, "  no runner, their flag got in", [c for c in none if c["their_flag"] == "captured"], o)
        _fell_row(pr, "  no runner, their flag did not", [c for c in none if c["their_flag"] != "captured"], o)
    return out


# ---- what else changes the answer (stage 3), and the sentence for one decision (stage 4)
def _thirds(vals):
    v = sorted(x for x in vals if x is not None)
    return (v[len(v) // 3], v[2 * len(v) // 3]) if v else (0, 0)


def factor_list(s):
    """What a team can see at the second it has to answer, each as two or three plain groups."""
    lo, hi = _thirds([c["more"][6] for c in s.C])
    holder = "our" if "we hold the stand" in s.C[0]["scenario"] or "our cap" in s.C[0]["scenario"] else "their"
    return (
        ("Numbers at the main fight", lambda c: "we are up" if c["x"][2] > c["x"][3] else "we are down" if c["x"][2] < c["x"][3] else "even"),
        ("Their morale", lambda c: "two deaths' worth of penalty or more" if c["x"][5] <= -30 else "little or none"),
        ("Our morale", lambda c: "two deaths' worth of penalty or more" if c["x"][4] <= -30 else "little or none"),
        ("Their runner", lambda c: line_of(c["their_runner"])),
        ("Where our main team stands", lambda c: None if c["more"][1] is None else "on their side of the stand" if c["more"][1] < 0 else "at the stand" if c["more"][1] == 0 else "on our own side"),
        (f"Seconds to {holder} boost", lambda c: None if c["x"][1] is None else "under 60 s" if c["x"][1] < 60 else "60 s or more"),
        ("The flag can beat the boost", lambda c: None if c["beats"] is None else "yes" if c["beats"] else "no"),
        ("The base res", lambda c: None if c["more"][0] is None else "within 40 s" if c["more"][0] < 40 else "later"),
        ("Flag lead before their run", lambda c: "we are behind (half a flag or more)" if c["x"][0] <= -0.35 else "we are ahead (half a flag or more)" if c["x"][0] >= 0.35 else "level"),
        ("Strength", lambda c: "we are the stronger team" if c["x"][6] >= 100 else "we are the weaker team" if c["x"][6] <= -100 else "close"),
        ("Our snares, to slow their flag", lambda c: None if c["more"][6] is None else "the fewest third" if c["more"][6] <= lo else "the most third" if c["more"][6] > hi else "the middle third"),
        ("How long their flag should take", lambda c: None if c["more"][7] is None else "under 45 s" if c["more"][7] < 45 else "45 s or more"))


def factors(S, pr):
    """Stage 3 (2026-11-19): what else changes the answer. For each thing a team can see, in each of its groups: what
    holding off is worth, no runner out at 15 s less a runner out, in win points 180 s on, set against the same
    position (one straight fit on the matching variables for the scenario, with the answer's worth let differ by
    group; ranges from drawing whole matches again). A thing matters where the worth differs between its groups.
    A reading of where to look: many groups are read, so one in ten will look clear by chance, and none of it is
    advice until it holds on unseen matches."""
    import random
    out = {}
    pr("\n9. What else changes the answer: what holding off is worth (no runner out at 15 s, less a runner out), 180 s on, at the same position, by what a team can see")
    pr("   + = holding off is ahead; - = the runner is ahead. MATTERS: the worth differs between the groups beyond a 1 in 100 chance; MAY MATTER: beyond 1 in 20. Read as where to look: about one row in ten is clear by chance.")
    for name, s in S.items():
        if "single run" not in name or not (name.endswith("15 s after their runner set off") or name.endswith("15 s after our cap")): continue
        idx = np.array([i for i in range(len(s.C)) if s.call[i] in (NONE, SENT, DOUBLE)])
        isa = np.array([float(s.call[i] == NONE) for i in idx]); y = s.y["180"][idx]; Zs = s.Z[idx]; rid = s.rid[idx]
        by = collections.defaultdict(list)
        for n_, r in enumerate(rid): by[r].append(n_)
        ids = sorted(by)
        pr(f"\n   {name} ({len(idx)}: {int(isa.sum())} held off, {int(len(isa) - isa.sum())} sent)")
        o = out[name] = {}
        for label, f in factor_list(s):
            lev = [f(s.C[i]) for i in idx]
            names = [k for k, n in collections.Counter(x for x in lev if x is not None).most_common() if n >= MIN_PLAYS]
            names = [k for k in names if sum(1 for x, a in zip(lev, isa) if x == k and a) >= 10 and sum(1 for x, a in zip(lev, isa) if x == k and not a) >= 10]
            if len(names) < 2: continue
            G = np.array([[float(x == k) for k in names] for x in lev]); keep = G.sum(axis=1) > 0
            def est(rows):
                A = np.column_stack([np.ones(len(rows)), Zs[rows], G[rows][:, 1:], G[rows] * isa[rows][:, None]])
                return np.linalg.lstsq(A, y[rows], rcond=None)[0][-len(names):]
            base = np.flatnonzero(keep); e = est(base)
            rnd, dr = random.Random(7), []
            for _ in range(DRAWS):
                rows = np.array([n_ for k in (rnd.choice(ids) for _ in ids) for n_ in by[k] if keep[n_]])
                if len(rows) > Zs.shape[1] + 2 * len(names) + 5: dr.append(est(rows))
            dr = np.array(dr); lo_, hi_ = np.percentile(dr, 5, axis=0), np.percentile(dr, 95, axis=0)
            a_, b_ = int(np.argmax(e)), int(np.argmin(e)); gap = dr[:, a_] - dr[:, b_]
            # the two groups furthest apart are picked after seeing them, which flatters the gap: "matters" asks for the stricter 1 in 100, "may matter" for 1 in 20
            matters = "matters" if float(np.percentile(gap, 1)) > 0 else "may matter" if float(np.percentile(gap, 5)) > 0 else None
            o[label] = {"matters": matters, "gap": [float(e[a_] - e[b_]), float(np.percentile(gap, 5)), float(np.percentile(gap, 95))],
                        "groups": {k: {"held off": int(((G[:, n_] == 1) & (isa == 1)).sum()), "sent": int(((G[:, n_] == 1) & (isa == 0)).sum()), "worth": [float(e[n_]), float(lo_[n_]), float(hi_[n_])]} for n_, k in enumerate(names)}}
            pr(f"     {label}" + (f"   {matters.upper()}: {e[a_] - e[b_]:.1f} win points between its groups ({np.percentile(gap, 5):+.1f} to {np.percentile(gap, 95):+.1f})" if matters else "   (no clear difference between its groups)"))
            for n_, k in enumerate(names):
                g = o[label]["groups"][k]; w = "holding off ahead" if lo_[n_] > 0 else "the runner ahead" if hi_[n_] < 0 else "not clear"
                pr(f"       {k:40} {g['held off']:4} held off, {g['sent']:3} sent: {e[n_]:+5.1f} ({lo_[n_]:+.1f} to {hi_[n_]:+.1f})  {w}")
    return out


PLACE = {0: "at the stand", 1: "at {own}'s footmen", 2: "at {own}'s door", 3: "in {own}'s base", 4: "in {own}'s pit", -1: "at {foe}'s footmen", -2: "at {foe}'s door", -3: "in {foe}'s base", -4: "in {foe}'s pit"}
CALL_WORDS = {NONE: "holding off (no runner out at {R} s)", SENT: "a runner out by {R} s", DOUBLE: "a double run started by {R} s"}
DID_WORDS = {NONE: "held off", SENT: "had a runner out", DOUBLE: "had started a double run"}
VERDICT_WORDS = {"right": "the answer the data favours", "wrong": "against what the data favours", "no clear difference": "no clear difference either way", "an unusual spot: no like cases round it": "an unusual spot, no reading"}
def card(s, i, K, M):
    """One flag decision as sentences a player would use (stage 4; SPEC section 7, the query): the spot, what the
    team did, what followed, and what teams in similar spots got from each answer. The last line is a reading, not
    advice (the held-out test does not yet show a gain spot by spot)."""
    c = s.C[i]; m = M[c["rid"]]; k = c["clock"]; us = c["team"]; them = next(t for t in m["teams"] if t != us); R = c["read"]
    x, mo = c["x"], c["more"]; tr = c["their_runner"]["role"]; at = lambda sec: cl(sec)
    # every number is said with whose it is (his word, 2026-11-19: "I need to know clearly WHO the numbers favour (7v6 in favour of Team, fight at stand)")
    place = lambda st_, own, foe: PLACE.get(int(st_), "elsewhere").format(own=own, foe=foe) if st_ is not None else "place not read"
    up = f"{us} up by {x[2] - x[3]:.0f}" if x[2] > x[3] else f"{them} up by {x[3] - x[2]:.0f}" if x[3] > x[2] else "even"
    flags_ = f"{us} ahead on flags by {x[0]:.1f}" if x[0] >= 0.35 else f"{them} ahead on flags by {-x[0]:.1f}" if x[0] <= -0.35 else "flags level"
    morale_ = lambda v: "no death penalty or boost" if v == 0 else f"{v:+.0f}"
    hold = f"{us} holds the stand" if c["stand"] == "own" else f"{them} holds the stand"
    # a cap that lands in the seconds after is said with it: who holds the stand at that second can be about to change (hold v RACK 10:49: RACK's flag has just
    # gone in and hold caps over it 3 s later)
    soon = [(u - (k["anchor"] - k["their_off"]), us if h == "own" else them) for u, h in ((c.get("track") or {}).get("caps") or [])]
    soon = [f"{who} caps {rel} s later" for rel, who in soon if 0 < rel <= 15]
    if soon: hold += " (" + ", ".join(soon) + ")"
    boost = "" if x[1] is None else f", boost in {x[1]:.0f} s"
    # a runner who waited back at his flag spawn from the gates did not set off: he takes the flag up (his words on Men v RACK 0:51, 2026-11-20: "Warrior was
    # waiting back, he didn't go back at 0:04"); a first flag that goes in over theirs is said so ("Men held the stand and RACK capped over (i.e. RACK didn't cap the first flag)"); and our own next
    # flag already up the field is said with the spot (Men v hold 2:07: "men already has flag in hand at stand")
    wb = k.get("their_waited_back")
    fu = c.get("flag_up")
    up_ = "" if not fu else f" {us}'s next flag is already up: " + (f"carried by its {fu['by']} {'in' if fu['where'].startswith(('the greater', 'the field')) else 'at'} {fu['where']}" if fu["carried"] else f"lying {'in' if fu['where'].startswith(('the greater', 'the field')) else 'at'} {fu['where']} since {at(fu['since'])}") + "."
    if c["from_cap"]:
        way = f"he waited back at his flag spawn from {at(wb)} and took it up at {at(k['their_pick'])}" if wb is not None else f"he set off at {at(k['their_off'])}"
        goes = f"{us}'s first flag goes in, over {them}'s (in since {at(k['cap_over'])})," if k.get("cap_over") is not None else f"{us}'s flag goes in"
        L = [f"{at(k['anchor'])}  {goes} while {them}'s {tr} is still on his way with theirs ({way}). Run again, or not?{up_}"]
    elif wb is not None: L = [f"{at(k['anchor'])}  {them}'s {tr}, who waits back at his flag spawn from {at(wb)}, takes up a flag at {at(k['their_pick'])} ({c['their']}). {hold}{boost}.{up_}"]
    else: L = [f"{at(k['anchor'])}  {them}'s {tr} sets off for a flag ({c['their']}). {hold}{boost}.{up_}"]
    L.append(f"    The spot: main fight {us} {x[2]:.0f} v {them} {x[3]:.0f} ({up}); {us}'s main team {place(mo[1], us, them)}, {them}'s {place(mo[2], them, us)}; morale {us} {morale_(x[4])}, {them} {morale_(x[5])} (the eight summed; a death is -15); "
             f"{flags_}; base res in {mo[0]:.0f} s; {us}'s chance of winning {100 * c['p0']:.0f}%.")
    d = _delay(c); who = (c.get("our_runner") or {}).get("role")
    if d is None or d > 180: did = f"{us} sends nobody in the next three minutes."
    elif d < 0: raise ValueError(f"card {c['id']}: {us}'s runner set off {-d} s before the run he is told to answer (R-460: whoever set off first is sending; jobs.flag_plays)")
    else: did = f"{us} sends {('its ' + who) if who else 'a runner'} {d} s later" + (" (a double run)" if k["our_double"] else "") + "."
    L.append(f"    The answer: {did}")
    h = c["hard"]["180"]; tf = c["their_flag"]
    theirs = f"{them}'s flag in at {at(k['their_end'])}" if tf == "captured" else f"{them}'s flag does not get in ({tf or 'not capped'}, {at(k['their_end'])})"
    ours = "" if d is None or d > 180 else (f"; {us}'s in at {at(k['our_end'])}" if k.get("our_how") == "captured" else f"; {us}'s does not get in")
    lc = h["lead_change"]
    L.append(f"    What followed, 180 s on: {theirs}{ours}; flag lead {'not read' if lc is None else format(lc, '+.2f') + ' for ' + us}; deaths {us} {h['deaths'][0]}, {them} {h['deaths'][1]}; boosts {us} {h['boosts'][0]}, {them} {h['boosts'][1]}; "
             f"{us}'s chance of winning {100 * c['p0']:.0f}% to {100 * c['p0'] + c['v']['180']:.0f}% ({c['v']['180']:+.1f}).")
    r = s.read(i, K, False, "180"); W = r["calls"]
    if len(W) < 2: L.append("    Similar spots: too few to compare the answers.")
    else:
        parts = "; ".join(f"{CALL_WORDS[a].format(R=R)} {w['worth']:+.1f} ({w['plays']} cases)" for a, w in sorted(W.items(), key=lambda kv: -kv[1]["worth"]))
        if r.get("unusual"): L.append(f"    Similar spots: an unusual spot ({us} at {100 * c['p0']:.0f}% to win); the nearest cases all lie to one side of it, so no reading. {us} {DID_WORDS[c['call']]}.")
        else:
            if r["clear"]: verdict = f"the data favours {CALL_WORDS[r['advice']].format(R=R)} by {r['margin']:.1f} win points ({r['range'][0]:+.1f} to {r['range'][1]:+.1f})"
            else: verdict = f"no clear difference ({r['margin']:.1f}, {r['range'][0]:+.1f} to {r['range'][1]:+.1f})"
            mine = "" if "mine" not in r else f" {us} {DID_WORDS[c['call']]}: {VERDICT_WORDS.get(r['verdict'], r['verdict'])}."
            L.append(f"    Similar spots, 180 s on, from the same position: {parts}: {verdict}.{mine}")
    if R != READS[0]: L = [f"    Second look, {R} s in, still nobody sent" + L[-1].strip()[len("Similar spots"):]]
    return "\n".join(L), {"id": c["id"], "lines": [x.strip() for x in L], "rid": c["rid"], "t": k["anchor"], "team": us, "read": R, "call": c["call"], "unusual": bool(r.get("unusual")), "compared": len(W) >= 2, "advice": r["advice"] if r["clear"] else None, "verdict": r["verdict"], "margin": r["margin"], "range": r["range"], "v180": c["v"]["180"]}


def cards(path, which="f1", out_json=None, site=None):
    """The sentence for every answer to a flag run (and every "run again, or not") in a set of whole games of the
    development set (default f1, the games he graded), or in one match by report id. In match order. `site`: also
    written as the rows of Model > Game review > Flag advice (`data/model/flag_cards.json` on main), one card a
    decision with its second look inside it; a card's id is its play's id, so his marks stay on it."""
    D, M, B, P, C, skipped, S = build(path)
    K, _ = choose_k(S)
    dv = json.load(open(os.path.join(REPO, "data", "model", "dev_set.json")))
    rids = [w["rid"] for w in sorted(dv["whole_game"], key=lambda w: w.get("part", 0)) if w.get("set") == which] or [r for r in M if r.startswith(which)]
    if not rids: sys.exit("no such set or match")
    print("Flag decisions as the engine reads them. \"Similar spots\" is a reading, not advice: spot by spot it does not yet hold on unseen matches. Times are match time; the first is the second to go to.")
    res = []
    for rid in rids:
        m = M[rid]; L = m.get("length_s")
        rows = sorted(((s.C[i]["clock"]["anchor"], s.C[i]["read"], s.C[i]["team"], name, i) for name, s in S.items() if " after their runner set off" in name or " after our cap" in name
                       for i in range(len(s.C)) if s.C[i]["rid"] == rid))
        print(f"\n\n=== {' v '.join(m['teams'])}, {m['map']}, {m['date']}" + (f", {L // 60}:{L % 60:02d} long" if L else "") + f": https://gvg.report/report/{rid}#map")
        for _, R_, _, name, i in rows:
            text, rec = card(S[name], i, K, M); print(("\n" if R_ == READS[0] else "") + text); res.append(rec)
        first = [r for r in res if r["rid"] == rid and r["read"] == READS[0]]
        tally = collections.Counter(VERDICT_WORDS.get(r["verdict"], r["verdict"]) for r in first)
        if first: print(f"\n  In this game, at the first look: " + "; ".join(f"{k} {v}" for k, v in tally.most_common()))
    first = [r for r in res if r["read"] == READS[0]]
    tally = collections.Counter(VERDICT_WORDS.get(r["verdict"], r["verdict"]) for r in first)
    print(f"\nAll {len(rids)} games, {len(first)} decisions at the first look: " + "; ".join(f"{k} {v}" for k, v in tally.most_common()))
    if out_json: json.dump(res, open(out_json, "w"), ensure_ascii=False, indent=1, default=float)
    if site:
        import subprocess, datetime
        games = []
        for rid in rids:
            m, by = M[rid], collections.OrderedDict()
            for r in res:
                if r["rid"] != rid: continue
                if r["read"] == READS[0]:
                    head, spot, answer, followed, similar = r["lines"]
                    by[r["id"]] = {"id": r["id"], "t": r["t"], "team": r["team"], "head": head.split("  ", 1)[-1], "spot": spot, "answer": answer, "followed": followed, "similar": similar, "second": None,
                                   "reading": bool(r["compared"] and not r["unusual"]), "verdict": VERDICT_WORDS.get(r["verdict"], r["verdict"])}
                elif r["id"] in by: by[r["id"]]["second"] = r["lines"][0]
            games.append({"rid": rid, "teams": m["teams"], "map": m["map"], "date": m["date"], "length_s": m.get("length_s"), "cards": list(by.values())})
        _keep_marks(games, site)
        eng = subprocess.check_output(["git", "-C", REPO, "rev-parse", "--short", "HEAD"], text=True).strip()
        json.dump({"about": "The engine's sentence for every answer to a flag run, and every \"run again, or not\", in the games of set " + which + " (tools/replay_analysis/cases.py cards, on the engine branch). The first three lines of a card "
                            "are what happened; the similar-spots line is a reading, not advice (R-538). Shown on Model > Game review > Flag advice; his marks are in flag_card_marks.json."
                            " A card keeps the id it was first written with (`play` is its play now), so his marks stay on it; `changed` says what is told differently from the card he marked, and the page then asks for that card again; `gone` lists the cards he marked that are no longer written.",
                   "generated": datetime.date.today().isoformat(), "engine": eng, "set": which, "games": games}, open(site, "w"), ensure_ascii=False, indent=1, default=float)
    return res


def _substance(parts):
    """What a card says, without the figures that move a little with every fit: the head and the answer word for word, the spot and what followed without the
    chance of winning, and which answer the first look favours. `parts` = head, spot, answer, followed, similar."""
    import re
    head, spot, answer, followed, similar = (list(parts) + [""] * 5)[:5]
    spot = re.sub(r"; [^;]*chance of winning \d+%\.?$", "", spot)
    followed = re.sub(r"; [^;]*chance of winning \d+% to \d+% \([-+][\d.]+\)\.?$", "", followed)
    fav = re.search(r"the data favours (a runner out by \d+ s|holding off|.+? over .+?) by [\d.]+ win points", similar)
    look = "the data favours " + fav.group(1) if fav else "no clear difference" if "no clear difference" in similar else "no reading"
    return {"what happened": (head, spot, answer, followed), "the reading": look}


def _keep_marks(games, site, marks_file="flag_card_marks.json"):
    """His marks stay on the cards when the cards are written again (2026-11-20: all 61 were marked, and four changes to the reading rewrote a handful). A card
    takes the id of the card it was before (the same game, team and kind of decision, nearest in time and within 40 s), so the marks file, which is his, is never
    touched from here. A card he marked that now says something else in substance is given `changed`, in words, and the page asks for it again with his earlier
    marks beside it; one whose figures only moved with the fit is not. A marked card that is no longer written is listed under the game's `gone`."""
    prev = json.load(open(site)) if os.path.exists(site) else {"games": []}
    mp = os.path.join(os.path.dirname(site), marks_file)
    marks = json.load(open(mp)).get("games", {}) if os.path.exists(mp) else {}
    kind = lambda c: ("Run again" in c["head"], c.get("side"))
    for g in games:
        old = list(next((x["cards"] for x in prev["games"] if x["rid"] == g["rid"]), [])); mk = (marks.get(g["rid"]) or {}).get("marks", {})
        gone_before = next((x.get("gone", []) for x in prev["games"] if x["rid"] == g["rid"]), [])
        used = set()
        for c in g["cards"]:
            c["play"] = c["id"]
            o = min((o for o in old if o["id"] not in used and o["team"] == c["team"] and kind(o) == kind(c) and abs(o["t"] - c["t"]) <= 40), key=lambda o: abs(o["t"] - c["t"]), default=None)
            if o is None: continue
            used.add(o["id"]); c["id"] = o["id"]
        taken = collections.Counter(c["id"] for c in g["cards"])
        for c in g["cards"]:                                              # a new card whose play id is the kept id of another card
            if taken[c["id"]] > 1 and c["id"] == c["play"] and not any(o["id"] == c["id"] for o in old): c["id"] += "b"
        for c in g["cards"]:
            m = mk.get(c["id"])
            if not m or not m.get("text"): continue
            was, now = _substance(m["text"].split(" | ")), _substance([c["head"], c["spot"], c["answer"], c["followed"], c["similar"]])
            diff = []
            if was["what happened"] != now["what happened"]: diff.append("what happened is told differently")
            if was["the reading"] != now["the reading"]: diff.append(f"the reading at the first look was \"{was['the reading']}\" and is now \"{now['the reading']}\"")
            if diff: c["changed"] = "Since you marked it: " + "; ".join(diff) + "."
        gone = [{"id": o["id"], "t": o["t"], "team": o["team"], "head": o["head"], "answer": o["answer"]} for o in old if o["id"] not in used and o["id"] in mk]
        gone += [x for x in gone_before if x["id"] in mk and not any(y["id"] == x["id"] for y in gone) and not any(c["id"] == x["id"] for c in g["cards"])]
        if gone: g["gone"] = sorted(gone, key=lambda x: x["t"])


# ---- the report
def build(path):
    D, M = load(path)
    B, P = prices(D, M)
    C, skipped = cases(D, M, B)
    by = collections.defaultdict(list)
    for c in [c for c in C if c["scenario"]] + read_cases(C): by[c["scenario"]].append(c)
    order = lambda n: (0 if "boost" in n else 3 if "in hand" in n else 2 if "after our cap" in n else 1, n.split(";")[0], n.split(";")[1] if ";" in n else "", n)
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
        n = len(s.C); cnt = collections.Counter(s.call.tolist()); reads = " after their runner set off" in name or " after our cap" in name
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
        if reads:
            lv = level_check(s); out["level check"] = lv
            g = lv.get("the 60 s before, same position")
            if g:
                mark = "level" if g[1] <= 0 <= g[2] else "NOT LEVEL: the answer marks the situation here, and what follows it is no advice"
                pr(f"     were the two answers on the same road before? none yet less a runner sent: chance of winning at that second {_fmt(lv['chance of winning at the start, plain'])} points; what the 60 s before had done to it")
                pr(f"     {_fmt(lv['the 60 s before, plain'])} plain, {_fmt(g)} set against the same position: {mark}. 180 s on: {_fmt(lv['180 s on, plain'])} plain, {_fmt(lv['180 s on, same position'])} set against the same position")
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
        b4 = t.get("pre")
        pr(f"   {label}: {ta.get('cases', 0)} cases, clear advice in {t['rows']} ({adv}), matched {t['matched']}: {e['effect']:+.1f} ({e['range'][0]:+.1f} to {e['range'][1]:+.1f}) {e['verdict']}; "
           f"in how the match ended {en['effect']:+.1f} ({en['range'][0]:+.1f} to {en['range'][1]:+.1f})"
           + ("" if not b4 else f"; in the 60 s before {b4['effect']:+.1f} ({b4['range'][0]:+.1f} to {b4['range'][1]:+.1f})" + ("" if b4["range"][0] <= 0 <= b4["range"][1] else " NOT LEVEL")))
    boost = {k: s for k, s in S.items() if "boost" in k}
    for H in ("90", "180"):
        line(f"their boost 30 s away, every case, {H} s on", advice_test(boost, K, H))
        line(f"their boost 30 s away, without the flag only held at home, {H} s on", advice_test(boost, K, H, drop_held=True))
    for R in READS:
        Sx = {k: s for k, s in S.items() if f"; {R} s after their runner set off" in k}
        for H in HORIZONS: line(f"their run, our answer read at {R} s, {H} s on", advice_test(Sx, K, H))
    for R in READS:                                                               # the other decision (R-546): our flag just in with theirs still on its way, run again or not
        Sx = {k: s for k, s in S.items() if f"; {R} s after our cap" in k}
        for H in HORIZONS: line(f"our flag just in, theirs still coming: run again, read {R} s after our cap, {H} s on", advice_test(Sx, K, H))
    res["given"] = given(C, pr)
    graded = set()
    dv = os.path.join(REPO, "data", "model", "dev_set.json")
    if os.path.exists(dv): graded = {w["rid"] for w in json.load(open(dv))["whole_game"] if w.get("set") == "f1"}
    pr("\n5. What the advice was: their run and our answer, read 15 s after their runner set off and judged 180 s on (the advice as the held-out test gives it)")
    res["advice_was"] = advice_was(S, M, K, pr, graded)
    pr("\n6. What a team with no runner out at 15 s goes on to do")
    res["held_off"] = held_off(S, D, M, K, pr)
    res["run_in_answer"] = run_in_answer(C, M, pr)
    res["as_it_fell"] = as_it_fell(C, pr)
    res["factors"] = factors(S, pr)
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


# ---- the timing ladder: a check of the flag readings themselves (2026-11-19, his ask; a report, never a verdict)
LADDER_READS = (15, 30, 45)                      # the 45 s read is back for this check only (his word, 2026-11-19); the advice is still read at 15 and 30 s (R-544)
RUNGS = ("ours set off before theirs", "within 15 s of theirs", "15 to 30 s after", "30 to 45 s after", "45 to 90 s after", "later than 90 s, or never")
_rung = lambda d: 5 if d is None or d > 90 else 0 if d < 0 else 1 if d <= 15 else 2 if d <= 30 else 3 if d <= 45 else 4
LEAD_BANDS = ((-9, -1.0, "a flag or more behind"), (-1.0, -0.35, "about half a flag behind"), (-0.35, 0.35, "level"), (0.35, 1.0, "about half a flag ahead"), (1.0, 9, "a flag or more ahead"))


def _held(tr, a, b, side="own"):
    """Seconds of (a, b] from their runner's set-off in which `side` holds the stand, from the caps themselves."""
    own, t, n = tr["stand"][0], 0, 0
    for u, h in sorted(tr["caps"]) + [[10 ** 6, None]]:
        lo, hi = max(t, a), min(u, b)
        if hi > lo and own == side: n += hi - lo
        own, t = h, u
    return n


def _this_flag(c, H=180):
    """Seconds of the H from their runner's set-off in which this flag of theirs holds the stand: from its cap to our
    next cap. 0 when it never got in."""
    if c["their_in"] is None or c["their_in"] >= H: return 0
    nx = min([u for u, h in c["tr"]["caps"] if h == "own" and u > c["their_in"]] or [10 ** 6])
    return min(nx, H) - c["their_in"]


def ladder_cases(D, M):
    """One case a run of theirs that we had to answer (the opening, Shadow of Haste runs and a flag of ours already in
    hand set aside, as in the similar cases), on one clock: their runner's set-off (the second he turned for home,
    R-498). `delay` is our next runner's set-off less theirs, by the same reading of a set-off; None when we never
    ran again. `stand` is the holder of the stand as the engine reads it for the case, at the second of its clock.
    `from_cap`: our own runner was already out when theirs set off, so the decision (run again, or not) is ours only
    from our cap, and its clock is our cap (R-546)."""
    out, skipped = [], collections.Counter()
    for p in D["plays"]:
        if p["play"] != "flag" or "clock" not in p: continue
        if "track" not in p: sys.exit("this plays file has no `track` on its flag plays: run `moments.py all` again with this engine")
        if p.get("soh") or p.get("runner_soh"): skipped["Shadow of Haste run (R-456)"] += 1; continue
        if p.get("opening"): skipped["the opening (R-541)"] += 1; continue
        if p["ours"] == "a flag already in hand": skipped["our flag already in hand"] += 1; continue
        tr, k, st = p["track"], p["clock"], p["state"]
        if st["stand"] not in ("own", "enemy"): skipped["nobody holds the stand"] += 1; continue
        if tr["lead"][0] is None: skipped["flag lead not read (no labelled hall)"] += 1; continue
        delay = None if k["our_off"] is None else k["our_off"] - k["their_off"]
        in_ = lambda how, end: (end - k["their_off"]) if (how == "captured" and end is not None) else None
        af = {H: p["after"][H] for H in HORIZONS if H in p["after"] and not p["after"][H]["ended"]}
        out.append({"id": p["id"], "rid": p["rid"], "team": p["team"], "off": k["their_off"], "delay": delay, "rung": _rung(delay), "call": RUNGS[_rung(delay)], "stand": st["stand"], "stand_off": tr["stand"][0], "their": p["their"],
                    "their_len": k["their_end"] - k["their_off"], "their_in": in_(p["beside"].get("their_flag"), k["their_end"]), "our_in": in_(k.get("our_how"), k.get("our_end")),
                    "eta": k["their_eta_s"], "told": tr["told_after"], "from_cap": bool(k["from_cap"]), "left": tr["left_s"], "tr": tr, "run_s": M[p["rid"]]["run_s"], "said": p["scenario"],
                    "after": {H: v["lead_change"] for H, v in af.items()}})
    return out, skipped


def _lead(c, a, b):
    """The change in flag lead (the engine's tally, R-408) from a to b seconds after their runner's set-off; None when the match is over by then."""
    tr = c["tr"]; i, j = tr["at"].index(a), tr["at"].index(b)
    return None if tr["lead"][i] is None or tr["lead"][j] is None else tr["lead"][j] - tr["lead"][i]


def _slope(rows, fx, fy):
    """The straight-line slope of fy on fx with a 90% range from drawing whole matches again; None under the floor."""
    import random
    R = [(c["rid"], fx(c), fy(c)) for c in rows if fx(c) is not None and fy(c) is not None]
    if len(R) < MIN_PLAYS or len({r for r, _, _ in R}) < MIN_MATCHES: return None
    fit = lambda Q: float(np.polyfit([x for _, x, _ in Q], [y for _, _, y in Q], 1)[0])
    by = collections.defaultdict(list)
    for r in R: by[r[0]].append(r)
    ids, rnd, dr = sorted(by), random.Random(7), []
    for _ in range(DRAWS):
        Q = [r for k in (rnd.choice(ids) for _ in ids) for r in by[k]]
        if len({x for _, x, _ in Q}) > 1: dr.append(fit(Q))
    dr.sort()
    return fit(R), dr[int(0.05 * len(dr))], dr[int(0.95 * len(dr)) - 1], len(R)


def ladder(path, out_json=None):
    """Do the run, stay and timing readings go with flag advantage (his ask, 2026-11-19)? A check of the readings,
    before anything more is built on them: no prices, no similar cases, no advice. Flags are the interim result.
    Two measures of it are kept apart: the engine's own flag tally (R-408), which counts a flag on its way and so
    rises with a runner sent by its own making, and the events the replay records (who capped and when, how long a
    flag holds the stand, the boosts that land), which owe nothing to the tally."""
    D, M = load(path); pr = print
    C, skipped = ladder_cases(D, M)
    res = {"cases": len(C), "skipped": dict(skipped)}
    pr(f"The timing ladder: do the run, stay and timing readings go with flag advantage? {len(C)} runs of theirs that we had to answer, in {len({c['rid'] for c in C})} matches" + "".join(f"; set aside, {k}: {v}" for k, v in skipped.items()))
    pr("Counted from one second, their runner's set-off (the second he turned for home, R-498). A check of the readings: no prices, no advice, no verdict.")
    med = lambda v: float(np.median(v)) if len(v) else float("nan")
    share = lambda v: 100 * float(np.mean(v)) if len(v) else float("nan")
    mean = lambda v: float(np.mean(v)) if len(v) else float("nan")
    word = lambda g: "too few" if not g else "HOLDS" if g[1] > 0 else "AGAINST" if g[2] < 0 else "not clear"

    # A. the clocks, and the stand
    n = len(C); cut = ((0, 5, "under 5 s"), (5, 10, "5 to 9 s"), (10, 20, "10 to 19 s"), (20, 30, "20 to 29 s"), (30, 10 ** 6, "30 s or more"))
    main = [c for c in C if not c["from_cap"]]; cap_ = [c for c in C if c["from_cap"]]; hall_ = [c for c in main if c["told"] >= 5]
    pr("\nA. The clocks. The reads of an answer, the windows and the position a case is matched on are counted from one second (R-546):")
    pr(f"   their runner's set-off in {len(main)} cases; our own cap in {len(cap_)}, where our runner was already out when theirs set off (another decision: run again, or not; B2),")
    pr(f"   a middle {med([c['told'] for c in cap_]):.0f} s after their set-off. The page tells a run by the hall's rule (R-461), later than its runner turned for home by 5 s or more in {len(hall_)} (middle {med([c['told'] for c in hall_]):.0f} s).")
    res["clocks"] = {"from their set-off": len(main), "from our own cap": len(cap_), "told by the hall's rule 5 s or more after the set-off": len(hall_)}
    both = [(c["after"]["90"], _lead(c, 0, 90)) for c in main if c["after"].get("90") is not None and _lead(c, 0, 90) is not None]
    off_ = sum(abs(a - b) >= 0.05 for a, b in both)
    pr(f"   Check, the windows on that clock: the 90 s window of the plays and the raw record from the set-off differ in {off_} of {len(both)} cases" + ("" if not off_ else "   (CHECK: they should be one reading)"))
    # the stand at the clock's second against the stand 3 s on, from the caps themselves
    at_ = lambda c: c["told"] if c["from_cap"] else 0
    now_ = lambda c: "own" if _held(c["tr"], at_(c) + 3, at_(c) + 4) else "enemy"
    ok_ = [c for c in C if at_(c) >= 0 and c["left"] > at_(c) + 5]
    wrong = [c for c in ok_ if c["stand"] == "enemy" and now_(c) == "own"]; wrong2 = [c for c in ok_ if c["stand"] == "own" and now_(c) == "enemy"]
    filed = sum(c["stand"] == "enemy" for c in C)
    pr(f"   Check, the stand: the engine says they hold the stand and 3 s on we hold it in {len(wrong)} of the {filed} cases filed under \"they hold the stand\" ({sum(c['from_cap'] for c in wrong)} at our own cap); the other way round in {len(wrong2)}.")
    soon = [c for c in main if c["stand"] == "own" and any(u <= 15 and h == "theirs" for u, h in c["tr"]["caps"])]
    pr(f"   Open: in {len(soon)} cases filed under \"we hold the stand\" their flag before goes in within 15 s of their runner turning for home (he sets off as it caps).")
    res["clocks"].update({"90 s window differs from the raw record": off_, "filed under they hold the stand": filed, "read as theirs, ours 3 s on": len(wrong), "of them at our own cap": sum(c["from_cap"] for c in wrong),
                          "read as ours, theirs 3 s on": len(wrong2), "we hold the stand, their flag before in within 15 s": len(soon)})

    # B. the ladder
    pr(f"\nB. The ladder: by how long after their runner ours set off ({len(main)} cases; the {len(cap_)} where our runner was already out are in B2).")
    pr("   If the readings are right, each rung down should be worse in flags than the one above it.")
    pr("   tally = change in the engine's flag lead from their set-off (R-408; it counts a flag on its way). From the replay's own events: their flag holds = seconds of the next 180")
    pr("   in which this flag of theirs holds the stand (its cap to our next cap; 0 if it never got in); stand = seconds of the next 180 in which we hold the stand; boost = lands within 300 s.")
    res["ladder"] = {}
    def table(rows, T):
        pr(f"     {'our runner':27} {'cases':>5}  {'their flag in':>13}  {'ours in':>9}  {'tally +60':>9} {'+90':>6} {'+180':>6}  {'their flag holds':>16}  {'stand':>6}  {'their boost':>11}  {'own boost':>9}")
        for i, name in enumerate(RUNGS):
            R = [c for c in rows if c["rung"] == i]
            if not R: continue
            full = [c for c in R if c["left"] >= 180]; long_ = [c for c in R if c["left"] >= 300]
            ld = {H: [x for x in (_lead(c, 0, H) for c in R) if x is not None] for H in (60, 90, 180)}
            row = {"cases": len(R), "their flag in": share([c["their_in"] is not None for c in R]), "their flag in, s": med([c["their_in"] for c in R if c["their_in"] is not None]),
                   "our flag in": share([c["our_in"] is not None for c in R]), "our flag in, s": med([c["our_in"] for c in R if c["our_in"] is not None]),
                   "tally": {H: mean(v) for H, v in ld.items()}, "their flag holds, s": mean([_this_flag(c) for c in full]), "stand_s": mean([_held(c["tr"], 0, 180) for c in full]),
                   "their boost": share([any(h == "theirs" for _, h in c["tr"]["boosts"]) for c in long_]), "own boost": share([any(h == "own" for _, h in c["tr"]["boosts"]) for c in long_])}
            T[name] = row
            pr(f"     {name:27} {len(R):5}  {row['their flag in']:5.0f}% {row['their flag in, s']:4.0f} s  {row['our flag in']:3.0f}% {row['our flag in, s']:3.0f} s  {row['tally'][60]:+9.2f} {row['tally'][90]:+6.2f} {row['tally'][180]:+6.2f}"
               f"  {row['their flag holds, s']:14.0f} s  {row['stand_s']:4.0f} s  {row['their boost']:10.0f}%  {row['own boost']:8.0f}%" + ("   (under the floor)" if len(R) < MIN_PLAYS else ""))
        pr("     each rung against the next one down (+ = the sooner runner is better off, as it should be):")
        T["steps"] = {}
        full = [c for c in rows if c["left"] >= 180]
        for a, b, wa, wb in [((RUNGS[i],), (RUNGS[i + 1],), RUNGS[i], RUNGS[i + 1]) for i in range(1, len(RUNGS) - 1)] + [(RUNGS[1:3], RUNGS[4:], "within 30 s", "later than 45 s, or never")]:
            g1 = _two(rows, lambda c: _lead(c, 0, 90), a, b); g2 = _two(full, _this_flag, b, a)
            T["steps"][f"{wa} against {wb}"] = {"tally 90 s": g1, "their flag holds, s fewer": g2}
            pr(f"       {wa:22} against {wb:26}: tally 90 s on {_fmt(g1, True):24} {word(g1):9}; their flag holds {_fmt(g2):22} s fewer {word(g2)}")
    for stand, words in (("own", "We hold the stand"), ("enemy", "They hold the stand")):
        for label, rows in ((f"{words}: every case", [c for c in main if c["stand"] == stand]), (f"{words}: where their flag got in", [c for c in main if c["stand"] == stand and c["their_in"] is not None])):
            pr(f"\n   {label} ({len(rows)})")
            table(rows, res["ladder"].setdefault(label, {}))
    # B2. our runner already out: the decision is ours from our cap, so its clock is our cap
    pr(f"\n   B2. Our runner already out when theirs set off ({len(cap_)}): from our cap, with their flag still on its way, how soon our next runner set off. Counted from our cap (the windows of the plays).")
    pr(f"     {'our next runner':27} {'cases':>5}  {'their flag in':>13}  {'tally +60':>9} {'+90':>6} {'+180':>6}")
    res["from our cap"] = {}
    for i, name in enumerate(("before our cap", "within 15 s of our cap", "15 to 30 s after", "30 to 45 s after", "45 to 90 s after", "later than 90 s, or never")):
        R = [c for c in cap_ if _rung(None if c["delay"] is None else c["delay"] - c["told"]) == i]
        if not R: continue
        t_ = {H: mean([c["after"][H] for c in R if c["after"].get(H) is not None]) for H in HORIZONS}
        res["from our cap"][name] = {"cases": len(R), "their flag in": share([c["their_in"] is not None for c in R]), "tally": t_}
        pr(f"     {name:27} {len(R):5}  {share([c['their_in'] is not None for c in R]):12.0f}%  {t_['60']:+9.2f} {t_['90']:+6.2f} {t_['180']:+6.2f}" + ("   (under the floor)" if len(R) < MIN_PLAYS else ""))

    # C. the clocks against the caps
    pr("\nC. The clocks against the caps. Where their flag got in and our next flag got in (the answers within 120 s):")
    res["caps"] = {}
    for stand, words in (("own", "we hold the stand"), ("enemy", "they hold the stand")):
        R = [c for c in main if c["stand"] == stand and c["their_in"] is not None and c["our_in"] is not None and c["delay"] is not None and 0 <= c["delay"] <= 120]
        sl = _slope(R, lambda c: c["delay"], lambda c: c["our_in"])
        res["caps"][words] = {"cases": len(R), "our cap from their set-off, s per s of delay": sl}
        pr(f"   {words} ({len(R)}): each second later our runner sets off, our flag goes in {sl[0]:.2f} s later ({sl[1]:.2f} to {sl[2]:.2f}); 1.00 is a set-off that reads right" if sl else f"   {words}: too few")
        for i in range(1, 5):
            Q = [c for c in R if c["rung"] == i]
            if Q: pr(f"     {RUNGS[i]:22} {len(Q):4}: their flag in {med([c['their_in'] for c in Q]):3.0f} s after their set-off, ours {med([c['our_in'] for c in Q]):3.0f} s; ours after theirs by {med([c['our_in'] - c['their_in'] for c in Q]):+4.0f} s (middle); our run took {med([c['our_in'] - c['delay'] for c in Q]):3.0f} s")
    E = [(c["their_in"], c["eta"]) for c in main if c["their_in"] is not None and c["eta"] and c["their"] == "single run" and c["stand"] == "own"]
    if E:
        err = [a - b for a, b in E]
        pr(f"   How long their flag should take, as the engine foretells it at their runner's set-off, against how long it took (single runs that got in, we hold the stand, {len(E)}): foretold {med([b for _, b in E]):.0f} s, took {med([a for a, _ in E]):.0f} s (middle);")
        pr(f"   took less foretold: middle {med(err):+.0f} s; a quarter of them {float(np.percentile(err, 25)):+.0f} s or under, a quarter {float(np.percentile(err, 75)):+.0f} s or over; within 10 s in {share([abs(x) <= 10 for x in err]):.0f}%.")
        res["caps"]["their flag: took less foretold, s"] = [float(np.percentile(err, q)) for q in (25, 50, 75)]; res["caps"]["foretold within 10 s"] = share([abs(x) <= 10 for x in err])

    # D. the grid: the reads against the windows
    pr("\nD. The grid: each read against each window. At a read their run is still under way and we had sent nobody by the read before; a runner sent by now, less none yet (+ = the runner is ahead).")
    pr("   `could be in`: the share of the runners sent whose flag had time to reach the stand inside the window (the hall's full run from the stand). Where it is low the cell is arithmetic, not play.")
    res["grid"] = {}
    def grid(pop, key):
        for stand, words in (("own", "We hold the stand"), ("enemy", "They hold the stand")):
            for anchor in ("their set-off", "the read"):
                pr(f"   {words}; windows counted from {anchor}:")
                for n_, R in enumerate(LADDER_READS):
                    prev = LADDER_READS[n_ - 1] if n_ else None
                    rows = [dict(c, call=SENT if (c["delay"] is not None and c["delay"] <= R) else NONE) for c in pop if c["stand"] == stand and c["their_len"] > R and not (prev is not None and c["delay"] is not None and c["delay"] <= prev)]
                    ns, nn = sum(c["call"] == SENT for c in rows), sum(c["call"] == NONE for c in rows)
                    line = f"     read at {R} s ({ns} sent, {nn} not):"
                    for H in (60, 90, 180):
                        a, b = (0, H) if anchor == "their set-off" else (R, R + H)
                        g = _two(rows, lambda c: _lead(c, a, b), (SENT,), (NONE,)); gs = _two([c for c in rows if c["left"] >= 180], _this_flag, (NONE,), (SENT,)) if anchor == "their set-off" and H == 180 else None
                        can = share([c["delay"] + BACK_AND_RUN * c["run_s"] <= b for c in rows if c["call"] == SENT]) if ns else float("nan")
                        res["grid"][f"{key}{words}; from {anchor}; read {R}; window {H}"] = {"sent": ns, "not": nn, "tally": g, "their flag holds, s fewer": gs, "could be in %": can}
                        line += f"  | {H:>3} s: tally {_fmt(g, True)} {word(g)}, could be in {can:.0f}%" + (f", their flag holds {_fmt(gs)} s fewer" if gs else "")
                    pr(line)
    grid(main, "")

    # E. is the tally flag advantage? The tally at their set-off against who gets the next morale boost
    pr("\nE. Is the tally flag advantage? The engine's flag lead at their runner's set-off (every case), against whose morale boost lands next, inside 300 s:")
    res["tally"] = {}
    L = [c for c in C if c["left"] >= 300]
    for lo, hi, name in LEAD_BANDS:
        R = [c for c in L if lo <= c["tr"]["lead"][0] < hi]
        if not R: continue
        fb = [min(c["tr"]["boosts"])[1] if c["tr"]["boosts"] else None for c in R]
        row = res["tally"][name] = {"cases": len(R), "own next": share([x == "own" for x in fb]), "theirs next": share([x == "theirs" for x in fb]), "none": share([x is None for x in fb])}
        pr(f"     {name:26} {len(R):5}: ours {row['own next']:3.0f}%, theirs {row['theirs next']:3.0f}%, none {row['none']:3.0f}%")
    sl = _slope(L, lambda c: c["tr"]["lead"][0], lambda c: sum(1 if h == "own" else -1 for _, h in c["tr"]["boosts"]))
    if sl: pr(f"     a flag of lead is worth {sl[0]:+.2f} boosts (ours less theirs) in the next 300 s ({sl[1]:+.2f} to {sl[2]:+.2f})" + ("   HOLDS" if sl[1] > 0 else "   AGAINST" if sl[2] < 0 else "   NOT CLEAR"))
    res["tally"]["boosts per flag of lead"] = sl

    # F. moments to look at
    def show(c, why=""):
        m = M[c["rid"]]; t = lambda s_: "none" if s_ is None else cl(c["off"] + s_)
        ld = _lead(c, 0, 90)
        pr(f"     {' v '.join(m['teams'])}, {m['map']}, {m['date']}, {int(m['length_s'] or 0) // 60} min: {c['said']}. Their runner sets off {cl(c['off'])}, ours {t(c['delay'])}; their flag in {t(c['their_in'])}, ours {t(c['our_in'])}; "
           f"tally 90 s on {'not read' if ld is None else format(ld, '+.2f')}; their flag holds the stand {_this_flag(c)} of the next 180 s. {why}https://gvg.report/report/{c['rid']}#map")
    pr("\nF. Moments to look at (go to the second their runner sets off)")
    own = [c for c in main if c["stand"] == "own" and c["their_in"] is not None and c["left"] >= 180 and _lead(c, 0, 90) is not None and c["their"] == "single run" and c["told"] < 5]
    pr("   The ladder as it should read. A runner within 15 s, both flags in:")
    for c in sorted([c for c in own if c["rung"] == 1 and c["our_in"] is not None and c["our_in"] > c["their_in"] and _this_flag(c) <= 15 and c["their_in"] >= 40], key=lambda c: (abs(c["delay"] - 8), c["rid"]))[:2]: show(c)
    pr("   ... and no runner for 90 s or at all, their flag in:")
    for c in sorted([c for c in own if c["rung"] == 5 and _this_flag(c) >= 100], key=lambda c: (abs(c["their_in"] - 55), c["rid"]))[:2]: show(c)
    pr("   To check the set-off itself. A runner read as setting off within 15 s whose flag took longest to get in (is his set-off read too early?):")
    for c in sorted([c for c in own if c["rung"] == 1 and c["our_in"] is not None and c["their_in"] >= 40], key=lambda c: (-(c["our_in"] - c["delay"]), c["rid"]))[:3]: show(c, f"Our run took {c['our_in'] - c['delay']} s. ")
    pr("   The two clocks furthest apart by the hall's rule (the run told long after its runner turned for home):")
    for c in sorted(hall_, key=lambda c: (-c["told"], c["rid"]))[:3]: show(c, f"Told as a run {c['told']} s after he turned for home. ")
    pr("   The other decision (R-546): our runner already out when theirs set off; from our cap, run again or not:")
    for c in sorted([c for c in cap_ if c["their_len"] > c["told"] + 15 and 20 <= c["told"] <= 40 and c["their_in"] is not None], key=lambda c: c["rid"])[:3]: show(c, f"Our flag before went in at {cl(c['off'] + c['told'])}, {c['told']} s after their runner set off. ")
    if out_json: json.dump(res, open(out_json, "w"), ensure_ascii=False, indent=1, default=float)
    return res


# ---- the numbers family (family 3; R-550 to R-552), stage 1: the readings, and a first table as it fell
NUM_SOURCES = ("kills", "runner away", "on the way")       # R-550: the main fight while a split is out is left for the split family
NUM_READ, NUM_LATER = 20, 60                               # the call is read where each main team stands 20 s after the numbers are told, and told again at 60 s (his, R-556; jobs.NUMBERS_TRACK_S)
UP_CALLS = ("stay and kill", "push into their base for NPCs", "push their flagger", "run a flag for a backup", "fall back and reset")
DOWN_CALLS = ("stay and fight", "fall to footmen", "retreat to the pit", "trade with a split")


def _num_call(p, read=NUM_READ):
    """The call of a team up or down on numbers, in his options (R-551), read `read` s in and not from the whole situation: where its main team stands then
    against where it stood (a step on its ladder: own pit 4, own base 3, own door 2, own footmen 1, the stand 0, their footmen -1, their door -2 ... their pit
    -4), and whether a runner of its own has gone. Pushing their flagger and trading with a split are still read from the whole play (Moments' call): few."""
    i = p["track"]["at"].index(read); s0, s1 = p["track"]["steps"][0][0], p["track"]["steps"][i][0]
    if s0 is None or s1 is None: return None
    if p["numbers_side"] == "up":
        if p["call"] == "push their flagger": return UP_CALLS[2]
        if p["track"]["runner_out"][i]: return UP_CALLS[3]
        if s1 <= -2 and s1 < s0: return UP_CALLS[1]
        if s1 > s0: return UP_CALLS[4]
        return UP_CALLS[0]
    if p["call"] == "split": return DOWN_CALLS[3]
    if s1 > s0 and s1 >= 3: return DOWN_CALLS[2]
    if s1 > s0: return DOWN_CALLS[1]
    return DOWN_CALLS[0]


def numbers_cases(D, M, B):
    """One case a clear numbers situation of the kinds in scope, from each side: its early call, its clock, the hard results on the fixed record and their
    price, from prices that never saw its match (as for a flag play)."""
    out, skipped = [], collections.Counter()
    for p in D["plays"]:
        if p["play"] != "numbers": continue
        if p.get("clear") is False: skipped["no clear decision (the numbers never held, or a player counted twice)"] += 1; continue
        if p["source"] not in NUM_SOURCES: skipped[f"from {p['source']}: left for the split family, or the wipe's own job"] += 1; continue
        if p["side"] == "after a wipe": skipped["kills at their base, the wipe's own job"] += 1; continue
        if "state" not in p: raise ValueError(f"numbers play {p['id']} carries no position: run moments.py all again on this engine (R-460)")
        m, st, af = M[p["rid"]], p["state"], p["after"]
        if not m["winner"]: skipped["no winner recorded"] += 1; continue
        gap = m["gap"][p["team"]]
        ends = {H: None if af[H]["ended"] else position(st, af[H], gap, True) for H in HORIZONS}
        if st["flag_lead"] is None or af["90"]["lead"][0] is None or any(ends[H] is None and not af[H]["ended"] for H in ends): skipped["flag lead not read"] += 1; continue
        call = _num_call(p)
        if call is None: skipped[f"no main team alive {NUM_READ} s in"] += 1; continue
        beta, won = B[m["fold"]], float(m["winner"] == p["team"])
        p0 = chance(beta, position(st, af["90"], gap, False))
        stp = p["track"]["steps"][0]; mor = af["90"]["morale"]
        bf, pre = p.get("before"), None
        if bf and bf["after"]["lead"][0] is not None and "npcs_lost" in bf["state"]: pre = 100 * (p0 - chance(beta, position(bf["state"], bf["after"], gap, False)))
        n = [int(x) for x in p["numbers"].split("v")]; k = p["clock"]; told = p["t0"]
        res = [r for r in k["hard_res"] if r[1] == ("own" if p["numbers_side"] == "down" else "theirs")]      # a res on the side that is down
        # what a like spot is matched on (as for a flag play, with what a numbers situation adds): the flag lead, the boost clock, each side's players in the fight
        # and its morale, the strength gap, the base res, the chance of winning, where each main team stands, and each side's dead. `more` is unused here
        x = [st["flag_lead"], st["boost_in"], n[0], n[1], mor[0][0], mor[1][0], gap, k["res_in"], 100 * p0, stp[0], stp[1], k["dead"][0], k["dead"][1]]
        out.append({"id": p["id"], "rid": p["rid"], "team": p["team"], "t": told, "side": p["numbers_side"], "source": p["source"], "call": call, "by": abs(n[0] - n[1]), "numbers": p["numbers"],
                    "x": x, "more": None, "fold": m["fold"], "won": won, "held": False, "kind": "numbers", "later": _num_call(p, NUM_LATER), "their_step": stp[1], "dead": k["dead"], "res_all": k["hard_res"],
                    "scenario": f"{'Up' if p['numbers_side'] == 'up' else 'Down'} on numbers from " + ("kills" if p["source"] == "kills" else "a runner away or players on the way"),
                    "lasted": k["end"] - told, "res_in": k["res_in"], "res_first": res[0][0] if res else None, "p0": p0, "pre": pre, "step": p["track"]["steps"][0][0],
                    "v": {H: 100 * ((won if af[H]["ended"] else chance(beta, ends[H])) - p0) for H in HORIZONS},
                    "hard": {H: {"deaths": af[H]["deaths"], "npcs": af[H]["npcs"], "lead_change": af[H]["lead_change"]} for H in HORIZONS}})
    return out, skipped


def _num_range(C, f, g, n=400):
    """A difference between two groups of cases with its 90% range over whole matches (f picks the first group, g the second; the value is c['_y'])."""
    by = collections.defaultdict(lambda: [[], []])
    for c in C:
        if f(c): by[c["rid"]][0].append(c["_y"])
        elif g(c): by[c["rid"]][1].append(c["_y"])
    rids = sorted(by); rng = np.random.default_rng(7)
    def diff(R):
        a = [y for r in R for y in by[r][0]]; b = [y for r in R for y in by[r][1]]
        return (np.mean(a) - np.mean(b)) if a and b else None
    d0 = diff(rids); bs = [x for x in (diff(list(rng.choice(rids, len(rids)))) for _ in range(n)) if x is not None]
    lo, hi = (np.percentile(bs, 5), np.percentile(bs, 95)) if bs else (None, None)
    return d0, lo, hi, sum(len(by[r][0]) for r in rids), sum(len(by[r][1]) for r in rids)


def numbers(path, out_json=None):
    """Stage 1 of the numbers family: do the readings go with what any player knows (a larger and a longer advantage kills more, the base res ends an advantage
    from kills, a res in the fight ends it at once: R-552), and a first table of what followed each early call, as it fell. A report: it advises nothing."""
    D, M = load(path); B, P = prices(D, M)
    C, skipped = numbers_cases(D, M, B)
    lines, res = [], {"cases": len(C), "skipped": dict(skipped), "counts": {}, "checks": {}, "as_it_fell": {}}
    pr = lambda x="": (lines.append(x), print(x))
    kill = lambda c, H="90": c["hard"][H]["deaths"][1] > c["hard"][H]["deaths"][0]
    pr(f"The numbers advantage (R-550 to R-552), stage 1, on {len(M)} matches: {len(C)} situations read from one side each" + "".join(f"; set aside, {k}: {v}" for k, v in skipped.most_common()))
    pr("\nA. How many, by cause and side (a situation is told once for the team up and once for the team down)")
    for src in NUM_SOURCES:
        for sd in ("up", "down"):
            X = [c for c in C if c["source"] == src and c["side"] == sd]; res["counts"][f"{src}, {sd}"] = [len(X), len({c['rid'] for c in X})]
            pr(f"   from {src:12} team {sd:5} {len(X):5} in {len({c['rid'] for c in X}):3} matches; lasted (middle) {np.median([c['lasted'] for c in X]) if X else 0:3.0f} s")
    K = [c for c in C if c["source"] == "kills" and c["side"] == "up"]
    pr(f"\nB. The readings, on numbers from kills, the team up ({len(K)}). A kill = more of theirs die than of ours in the 90 s after the numbers are told.")
    def check(name, f, g, expect, y, fa, ga, unit="%"):
        for c in K: c["_y"] = y(c)
        d, lo, hi, na, nb = _num_range(K, f, g)
        if d is None: pr(f"   {name}: too few"); return
        sc = 100 if unit == "%" else 1
        word = "HOLDS" if (lo > 0 if expect > 0 else hi < 0) else "AGAINST" if (hi < 0 if expect > 0 else lo > 0) else "not clear"
        pr(f"   {name}: {fa} {sc * np.mean([c['_y'] for c in K if f(c)]):.0f}{unit} ({na}); {ga} {sc * np.mean([c['_y'] for c in K if g(c)]):.0f}{unit} ({nb}); difference {sc * d:+.0f}{unit} ({sc * lo:+.0f} to {sc * hi:+.0f})   {word}")
        res["checks"][name] = {"first": float(np.mean([c['_y'] for c in K if f(c)])), "second": float(np.mean([c['_y'] for c in K if g(c)])), "difference": float(d), "range": [float(lo), float(hi)], "n": [na, nb], "reads": word}
    check("B1 up by two or more kills more often than up by one", lambda c: c["by"] >= 2, lambda c: c["by"] == 1, +1, kill, "up by two or more", "up by one")
    check("B2 the base res far off kills more often than the base res near", lambda c: c["res_in"] >= 60, lambda c: c["res_in"] < 30, +1, kill, "base res 60 s or more away", "under 30 s away")
    check("B3 the base res far off, the numbers last longer", lambda c: c["res_in"] >= 60, lambda c: c["res_in"] < 30, +1, lambda c: c["lasted"], "base res 60 s or more away", "under 30 s away", unit=" s")
    # A res in their fight (R-552: "if a res gets off, a numbers advantage from kills is pretty much over"). It is not set against the cases with no res: a res
    # comes where players are dying, so those fights show more kills, not fewer (2026-11-20: 79% against 63%, a comparison that marks the fight). What is read is
    # what the numbers did after it, by how far up the team was: with a team up by one a res should level the fight at once
    res["ended"] = {}
    for lab, f in (("up by one", lambda c: c["by"] == 1), ("up by two or more", lambda c: c["by"] >= 2)):
        G = [c for c in K if f(c)]; R_ = [c for c in G if c["res_first"] is not None and c["res_first"] <= c["lasted"] + 5]; aft = [c["lasted"] - c["res_first"] for c in R_]
        at_res = [c for c in G if abs(c["lasted"] - c["res_in"]) <= 12]
        o = res["ended"][lab] = {"situations": len(G), "a res in their fight while the numbers stood": len(R_), "then over within 6 s": float(np.mean([x <= 6 for x in aft])) if aft else None,
                                 "then still up 30 s on": float(np.mean([x >= 30 for x in aft])) if aft else None, "seconds more (middle)": float(np.median(aft)) if aft else None, "ended within 12 s of the base res": len(at_res)}
        pr(f"   B4 a res in their fight, team {lab} ({len(G)}): one came while the numbers stood in {len(R_)} ({100 * len(R_) / max(len(G), 1):.0f}%); the numbers were then over within 6 s in {100 * (o['then over within 6 s'] or 0):.0f}% "
           f"and still told 30 s on in {100 * (o['then still up 30 s on'] or 0):.0f}% (a middle {o['seconds more (middle)'] or 0:.0f} s more); ended within 12 s of the base res: {len(at_res)} ({100 * len(at_res) / max(len(G), 1):.0f}%)")
    pr("      Open: a numbers situation is told once through a level spell shorter than 10 s, so a res that levels the fight and a new kill seconds later are one situation today; by R-552 the res ended it.")
    pr(f"\nC. As it fell: what followed each call, read {NUM_READ} s in, 90 and 180 s on (a description set against no like spot; who makes a call follows the spot)")
    pr("   started at = own chance of winning when the numbers are told; 60 s before = what the minute before had done to it, in win points.")
    head = f"     {'':32} {'cases':>5}  {'started at':>10}  {'60 s before':>11}  {'they lose one':>13}  {'we lose one':>11}  {'net kills':>9}  {'net NPCs':>8}  {'flags':>6}  {'win pts 90':>10}  {'win pts 180':>11}"
    for name, f, calls in (("Up on numbers from kills", lambda c: c["side"] == "up" and c["source"] == "kills", UP_CALLS), ("Down on numbers from kills", lambda c: c["side"] == "down" and c["source"] == "kills", DOWN_CALLS),
                           ("Up on numbers, their runner away or their players on the way", lambda c: c["side"] == "up" and c["source"] != "kills", UP_CALLS),
                           ("Down on numbers, our runner away or our players on the way", lambda c: c["side"] == "down" and c["source"] != "kills", DOWN_CALLS)):
        X = [c for c in C if f(c)]; pr(f"\n   {name} ({len(X)})"); pr(head); o = res["as_it_fell"][name] = {}
        for call in calls:
            V = [c for c in X if c["call"] == call]
            if not V: continue
            h = [c["hard"]["90"] for c in V]; pre = [c["pre"] for c in V if c["pre"] is not None]
            row = {"cases": len(V), "matches": len({c["rid"] for c in V}), "started at": 100 * float(np.mean([c["p0"] for c in V])), "the 60 s before": float(np.mean(pre)) if pre else None,
                   "they lose one": 100 * float(np.mean([x["deaths"][1] > 0 for x in h])), "we lose one": 100 * float(np.mean([x["deaths"][0] > 0 for x in h])), "net kills": float(np.mean([x["deaths"][1] - x["deaths"][0] for x in h])),
                   "net NPCs": float(np.mean([x["npcs"][1] - x["npcs"][0] for x in h])), "flags": float(np.mean([x["lead_change"] for x in h if x["lead_change"] is not None])),
                   "win points 90": float(np.mean([c["v"]["90"] for c in V])), "win points 180": float(np.mean([c["v"]["180"] for c in V]))}
            o[call] = row
            pr(f"     {call:32} {len(V):5}  {row['started at']:9.0f}%  {('' if row['the 60 s before'] is None else format(row['the 60 s before'], '+.1f')):>11}  {row['they lose one']:12.0f}%  {row['we lose one']:10.0f}%  {row['net kills']:+9.2f}  "
               f"{row['net NPCs']:+8.2f}  {row['flags']:+6.2f}  {row['win points 90']:+10.1f}  {row['win points 180']:+11.1f}" + ("   (under the floor)" if len(V) < MIN_PLAYS or row["matches"] < MIN_MATCHES else ""))
    S = numbers_scenarios(C); K, _ = choose_k(S); res["K"] = K; res["advice_test"] = {}
    pr(f"\nD. Like spots, and the test on matches the advice never saw (the {K} nearest cases of each call, set level with the case read; the floor of {MIN_PLAYS} plays and {MIN_MATCHES} matches)")
    pr("   matched on: flag lead, seconds to the boost, each side's players in the fight, each side's morale, strength gap, seconds to the base res, chance of winning, where each main team stands, each side's dead")
    pr("   For each scenario: where the advice is clear, teams whose call 20 s in matched it against those whose call did not, in win points; and the same test on the 60 s before, which no call can change.")
    for name, s in S.items():
        o = res["advice_test"][name] = {}
        for H in HORIZONS:
            t = advice_test({name: s}, K, H); o[H] = {k: v for k, v in t.items()}
            adv = ", ".join(f"{a} {n_}" for a, n_ in sorted(t.get("advice", {}).items(), key=lambda q: -q[1]))
            if "v" not in t: pr(f"   {name}, {H} s on: {len(s.C)} cases, clear advice in {t['rows']}: too few to call [{adv}]"); continue
            pre = t.get("pre"); lv = "" if not pre else f"; in the 60 s before {pre['effect']:+.1f} ({pre['range'][0]:+.1f} to {pre['range'][1]:+.1f})" + ("" if pre["verdict"] == "no clear difference" else " NOT LEVEL")
            pr(f"   {name}, {H} s on: {len(s.C)} cases, clear advice in {t['rows']} ({adv}), matched {t['matched']}: {t['v']['effect']:+.1f} ({t['v']['range'][0]:+.1f} to {t['v']['range'][1]:+.1f}) {t['v']['verdict']}; "
               f"in how the match ended {t['end']['effect']:+.1f} ({t['end']['range'][0]:+.1f} to {t['end']['range'][1]:+.1f}){lv}")
    if out_json: json.dump(res, open(out_json, "w"), indent=1, default=float)
    return res


def numbers_scenarios(C):
    """The numbers cases by scenario (the side and the cause), each laid out for finding the nearest."""
    by = collections.defaultdict(list)
    for c in C: by[c["scenario"]].append(c)
    return {k: Scenario(v) for k, v in sorted(by.items()) if len(v) >= MIN_PLAYS}


NUM_DID = {"stay and kill": "stays and fights where the fight is", "push into their base for NPCs": "has pushed into their base", "push their flagger": "pushes their flagger", "run a flag for a backup": "has sent a runner for a flag",
           "fall back and reset": "has fallen back", "stay and fight": "stays and fights", "fall to footmen": "has fallen back toward its footmen", "retreat to the pit": "has retreated into its base or pit", "trade with a split": "sends a split"}
def numbers_cards(path, which="f1", site=None):
    """The sentence for every numbers situation in scope in the games of a set (stage 4), as for the flags: the spot, the call 20 s in (and what the team is doing
    at 60 s), what followed, and what teams in like spots got from each call. A situation he graded Weak or No decision on the Decisions view is left out (the
    engine still reads too many short ones). `site`: written as the rows of Model > Game review > Numbers advice; a card's id is its play's id."""
    D, M = load(path); B, P = prices(D, M); C, _ = numbers_cases(D, M, B); S = numbers_scenarios(C); K, _ = choose_k(S)
    dv = json.load(open(os.path.join(REPO, "data", "model", "dev_set.json")))
    rids = [w["rid"] for w in sorted(dv["whole_game"], key=lambda w: w.get("part", 0)) if w.get("set") == which] or [r for r in M if r.startswith(which)]
    key = json.load(open(os.path.join(REPO, "data", "model", "review_key.json")))["rows"]
    low = {(r["rid"], r["window"][0]) for r in key if r.get("set") == "f1" and r.get("type") == "numbers" and r.get("grade") in ("weak", "none")}
    at = lambda sec: cl(sec); games, left = [], 0
    for rid in rids:
        m, cards_ = M[rid], []
        for name, s in S.items():
            for i, c in enumerate(s.C):
                if c["rid"] != rid: continue
                if any(r == rid and abs(w - c["t"]) <= 6 for r, w in low): left += 1; continue
                us = c["team"]; them = next(t for t in m["teams"] if t != us); x = c["x"]; h = c["hard"]["180"]
                place = lambda st_, own, foe: PLACE.get(int(st_), "elsewhere").format(own=own, foe=foe) if st_ is not None else "place not read"
                n = c["numbers"].split("v"); up = c["side"] == "up"
                why = "from kills" if c["source"] == "kills" else f"with {them if up else us}'s runner away" if c["source"] == "runner away" else f"with {them if up else us}'s players still on their way"
                head = f"{us} is {'up' if up else 'down'} on numbers in the main fight, {us} {n[0]} v {them} {n[1]}, {why}. Base res in {x[7]:.0f} s."
                flags_ = f"{us} ahead on flags by {x[0]:.1f}" if x[0] >= 0.35 else f"{them} ahead on flags by {-x[0]:.1f}" if x[0] <= -0.35 else "flags level"
                mo = lambda v: "no death penalty or boost" if v == 0 else f"{v:+.0f}"
                spot = (f"The spot: {us}'s main team {place(x[9], us, them)}, {them}'s {place(x[10], them, us)}; dead {us} {c['dead'][0]}, {them} {c['dead'][1]}; morale {us} {mo(x[4])}, {them} {mo(x[5])} "
                        f"(the eight summed; a death is -15); {flags_}; {us}'s chance of winning {100 * c['p0']:.0f}%.")
                answer = f"The call: 20 s in, {us} {NUM_DID[c['call']]}" + ("" if c["later"] in (None, c["call"]) else f"; 60 s in, it {NUM_DID[c['later']]}") + "."
                res_ = "; ".join(f"{(us if w == 'own' else them)}'s {role} is resurrected {sec} s in" for sec, w, role in c["res_all"][:3])
                followed = (f"What followed, 180 s on: deaths {us} {h['deaths'][0]}, {them} {h['deaths'][1]}; NPCs lost {us} {h['npcs'][0]}, {them} {h['npcs'][1]}; " + (f"{res_}; " if res_ else "") +
                            f"the numbers lasted {c['lasted']} s; {us}'s chance of winning {100 * c['p0']:.0f}% to {100 * c['p0'] + c['v']['180']:.0f}% ({c['v']['180']:+.1f}).")
                r = s.read(i, K, False, "180"); W = r["calls"]
                if len(W) < 2: similar, reading, verdict = "Similar spots: too few like cases to compare the calls.", False, "too few cases"
                elif r.get("unusual"): similar, reading, verdict = f"Similar spots: an unusual spot ({us} at {100 * c['p0']:.0f}% to win); the nearest cases all lie to one side of it, so no reading.", False, "an unusual spot, no reading"
                else:
                    parts = "; ".join(f"{a} {W[a]['worth']:+.1f} ({W[a]['plays']} cases)" for a in sorted(W, key=lambda a: -W[a]["worth"]))
                    if c["call"] in W and r.get("mine"):
                        d2, lo, hi = r["mine"]; vw = VERDICT_WORDS.get(r["verdict"], r["verdict"])
                        tail = (f"the data favours {c['call']} over {r['against']} by {d2:.1f} win points ({lo:+.1f} to {hi:+.1f})" if r["verdict"] == "right" else
                                f"the data favours {r['against']} over {c['call']} by {-d2:.1f} win points ({-hi:+.1f} to {-lo:+.1f})" if r["verdict"] == "wrong" else f"no clear difference between {c['call']} and {r['against']} ({abs(d2):.1f}, {lo:+.1f} to {hi:+.1f})")
                        similar, reading, verdict = f"Similar spots, 180 s on, from the same position: {parts}: {tail}. {us}'s call: {vw}.", True, vw
                    else: similar, reading, verdict = f"Similar spots, 180 s on, from the same position: {parts}. Too few like cases of {us}'s own call ({c['call']}) to judge it.", False, "too few cases of this call"
                cards_.append({"id": c["id"], "t": c["t"], "team": us, "side": c["side"], "head": head, "spot": spot, "answer": answer, "followed": followed, "similar": similar, "second": None, "reading": reading, "verdict": verdict})
        cards_.sort(key=lambda q: (q["t"], q["team"]))
        games.append({"rid": rid, "teams": m["teams"], "map": m["map"], "date": m["date"], "length_s": m.get("length_s"), "cards": cards_})
        print(f"\n=== {' v '.join(m['teams'])}, {m['map']}, {m['date']}: https://gvg.report/report/{rid}#map")
        for q in cards_: print(f"{at(q['t'])}  {q['head']}\n    {q['spot']}\n    {q['answer']}\n    {q['followed']}\n    {q['similar']}")
    first = [q for g in games for q in g["cards"]]
    print(f"\nAll {len(rids)} games: {len(first)} cards ({left} situations he graded Weak or No decision left out): " + "; ".join(f"{k} {v}" for k, v in collections.Counter(q["verdict"] for q in first).most_common()))
    if site:
        import subprocess, datetime
        _keep_marks(games, site, "numbers_card_marks.json")
        eng = subprocess.check_output(["git", "-C", REPO, "rev-parse", "--short", "HEAD"], text=True).strip()
        json.dump({"about": "The engine's sentence for every numbers advantage at the main fight (from kills, a runner away or players on their way; R-550) in the games of set " + which + " (tools/replay_analysis/cases.py numbers-cards, on the engine branch). "
                            "The first lines of a card are what happened; the similar-spots line is a reading, not advice. Shown on Model > Game review > Numbers advice; his marks are in numbers_card_marks.json. Ids, `changed` and `gone` as in flag_cards.json.",
                   "generated": datetime.date.today().isoformat(), "engine": eng, "set": which, "games": games}, open(site, "w"), ensure_ascii=False, indent=1, default=float)
    return games


# ---- the split family, stage 1 (R-558): the answer to a split
SPLIT_READS = (20, 40)                           # the seconds after a split is told at which the answer to it is read: the first answer, frozen at 20 s, and what it had become at 40 s (R-567, his: "Can we do 20s and 40s?"; 30 and 60 s were Claude's draft)
SPLIT_VARS = ("flag lead", "seconds to the boost", "seconds to the base res", "own morale", "their morale", "strength gap", "own chance of winning at that second", "own main team's place (steps toward own pit)",
              "their main team's place (steps toward their pit)", "own pit NPCs already lost", "own dead", "their dead", "players on the split", "monks on the split", "self-defence skills on the split",
              "the split's snares", "the split's speed", "the split's escapes")      # R-566 and his agreement of 2026-11-21: the list put to him, with each side's dead and what the split can do as properties (R-539). Its damage against NPCs is not measured yet (`Moments._props`)
SPLIT_SIZES = ("one player", "two players", "three players", "four or more")
SPLIT_ANSWERS = ("nobody coming", "a defender on his way", "one defender, a monk", "one defender, not a monk", "one defender", "two monks", "fewer than the split", "mirror", "add one", "two or more extra", "a collapse", "the whole team")


SPLIT_NONE = ("nobody coming", "a defender on his way")
SPLIT_FEWER = SPLIT_NONE + ("one defender", "two monks", "fewer than the split")      # fewer defenders on it than it has players, 20 s in
SPLIT_MATCHED = ("one defender, a monk", "one defender, not a monk", "mirror", "add one", "two or more extra", "a collapse", "the whole team")      # as many as the split or more


def _split_answer(s, read):
    """The answer a split has met `read` s after it is told, in his words (R-558; who defends, 2026-11: against one player a monk or a damage player; against
    three the mirror, two monks or the whole team): from how many of it stand on the enemy's ground at that second, how many defend it and how many of those
    are backline monks, and whether that second lies in a collapse or in the whole team's turn. None when the split is over by then or not yet on their ground."""
    v = s["numbers"][s["at"].index(read)]
    if v is None or v[0] == 0: return None, None
    k, n, mk = v[:3]
    kinds = {kd for a, b, _, _, kd in s["stretches"] if a <= read <= b}
    size = SPLIT_SIZES[min(k, 4) - 1]
    if "whole team" in kinds: return size, "the whole team"
    if n == 0:                                               # nobody on it yet: a defender who is there within 20 s more was on his way; else nobody was coming (R-569). Told by what the
        later = [w for h, w in zip(s["at"], s["numbers"]) if read < h <= read + 20]      # defending team did alone: a split that leaves of itself with nobody come is still "nobody coming"
        return size, "a defender on his way" if any(w and w[1] > 0 for w in later) else "nobody coming"
    if "collapse" in kinds and n > k: return size, "a collapse"
    if k == 1 and n == 1: return size, "one defender, a monk" if mk else "one defender, not a monk"
    if n < k: return size, "two monks" if (n == 2 and mk == 2) else "one defender" if n == 1 else "fewer than the split"
    return size, "mirror" if n == k else "add one" if n == k + 1 else "two or more extra"


def split_cases(D, M, B):
    """One case a split, from the side of the team it is sent against: the answer it had met at each read, the split's own account (NPCs it took, deaths on it
    and among its defenders) and the hard results over the whole map on the fixed record with their price, from prices that never saw its match."""
    by, out, skipped = {}, [], collections.Counter()
    for p in D["plays"]:
        if p["play"] != "split" or p.get("change"): continue
        if "split" not in p: raise ValueError(f"split play {p['id']} carries no split record: run moments.py all again on this engine (R-460)")
        if "at_told" in p and p["side"].startswith("defender"): by.setdefault((p["rid"], p["split"]["id"]), p)
    seen = {(p["rid"], p["split"]["id"]) for p in D["plays"] if p["play"] == "split" and not p.get("change")}
    skipped["no row of the defending team in its first told stretch"] = len(seen) - len(by)
    for (rid, sid), p in sorted(by.items()):
        m, s, st, af = M[rid], p["split"], p["at_told"]["state"], p["at_told"]["after"]
        if p.get("group") == "push team": skipped["a push team and a defence team (R-487), no split"] += 1; continue
        if not m["winner"]: skipped["no winner recorded"] += 1; continue
        gap = m["gap"][p["team"]]
        ends = {H: None if af[H]["ended"] else position(st, af[H], gap, True) for H in HORIZONS}
        if st["flag_lead"] is None or af["90"]["lead"][0] is None or any(ends[H] is None and not af[H]["ended"] for H in ends): skipped["flag lead not read"] += 1; continue
        beta, won = B[m["fold"]], float(m["winner"] == p["team"])
        p0 = chance(beta, position(st, af["90"], gap, False))
        bf, pre = p["at_told"].get("before"), None
        if bf and bf["after"]["lead"][0] is not None and "npcs_lost" in bf["state"]: pre = 100 * (p0 - chance(beta, position(bf["state"], bf["after"], gap, False)))
        within = lambda L, h: sum(1 for x in L if 0 <= x <= h)
        i0 = s["at"].index(SPLIT_READS[0]); nm, pp, mor = s["numbers"][i0], s["props"][i0] or {}, af["90"]["morale"]
        size0, call0 = _split_answer(s, SPLIT_READS[0])
        # what a like spot is matched on (SPLIT_VARS), from the side of the team the split is sent against; a split not on their ground at the first read has no case among the like spots
        x = [st["flag_lead"], st["boost_in"], s["res_in"], mor[0][0], mor[1][0], gap, 100 * p0, s["steps"][1], s["steps"][0], st["npcs_lost"][0][0], s["dead"][1], s["dead"][0],
             nm[0] if nm else None, nm[3] if nm else None, pp.get("self_defence"), pp.get("snare"), pp.get("speed"), pp.get("escapes")]
        out.append({"id": p["id"], "rid": rid, "team": p["team"], "t": s["told"], "sid": sid, "fold": m["fold"], "won": won, "p0": p0, "pre": pre, "x": x, "more": None, "held": False, "kind": "split",
                    "scenario": size0 and f"A split of {size0}", "call": call0, "home": s["home"], "runner_out": s["runner_out"], "own_split": s["own_split"], "pit_alive": s["pit_alive"], "lord": {h: sum(v_ for t_, v_ in s["lord_damage"] if 0 <= t_ <= h) for h in (90, 180)},
                    "by": {h: (lambda v_: None if v_ is None else [v_[0], v_[1]])(s["numbers"][s["at"].index(h)]) for h in s["at"]},
                    "read": {r: _split_answer(s, r) for r in SPLIT_READS}, "first_defender": None if s["first_defender"] is None else s["first_defender"] - s["told"],
                    "reached": None if s["reached"] is None else s["reached"] - s["told"], "lasted": s["end"] - s["told"], "res_in": s["res_in"], "size0": s["size"],
                    "pit": {h: sum(1 for t_, _, pit in s["npcs"] if pit and 0 <= t_ <= h) for h in (90, 180)}, "any_npc": {h: sum(1 for t_, _, _ in s["npcs"] if 0 <= t_ <= h) for h in (90, 180)},
                    "split_dies": {h: within(s["split_deaths"], h) for h in (90, 180)}, "defender_dies": {h: within(s["defender_deaths"], h) for h in (90, 180)},
                    "v": {H: 100 * ((won if af[H]["ended"] else chance(beta, ends[H])) - p0) for H in HORIZONS},
                    "hard": {H: {"deaths": af[H]["deaths"], "npcs": af[H]["npcs"], "lead_change": af[H]["lead_change"]} for H in HORIZONS}})
    return out, skipped


def split_factor_list(s):
    """What the team a split is sent against can see when it has to answer, each as two or three plain groups (R-568, and the rest of what its like spots are matched on)."""
    x = lambda i: (lambda c: c["x"][i])
    return (
        ("The game clock", lambda c: "before 12:00" if c["t"] < 720 else "12:00 on"),
        ("The base res", lambda c: "within 40 s" if c["res_in"] < 40 else "40 to 80 s away" if c["res_in"] < 80 else "80 s or more away"),
        ("Our players already at home", lambda c: "none" if c["home"] == 0 else "one or two" if c["home"] <= 2 else "three or more"),
        ("A flag run of ours under way", lambda c: "yes" if c["runner_out"][1] else "no"),
        ("A split of our own out", lambda c: "yes" if c["own_split"] else "no"),
        ("Our pit NPCs left", lambda c: (lambda n_: "all of them" if c["x"][9] == 0 else "two or more, not all" if n_ >= 2 else "one or none")(sum(c["pit_alive"].values()))),
        ("Our pit archers", lambda c: "one or more left" if c["pit_alive"]["archer"] else "none left"),
        ("Our knights", lambda c: "one or more left" if c["pit_alive"]["knight"] else "none left"),
        ("Our dead", lambda c: "none" if c["x"][10] == 0 else "one or more"),
        ("Their dead", lambda c: "none" if c["x"][11] == 0 else "one or more"),
        ("Where our main team stands", lambda c: None if c["x"][7] is None else "on their side of the stand" if c["x"][7] < 0 else "at the stand" if c["x"][7] == 0 else "on our own side"),
        ("Flag lead", lambda c: "we are behind (half a flag or more)" if c["x"][0] <= -0.35 else "we are ahead (half a flag or more)" if c["x"][0] >= 0.35 else "level"),
        ("Strength", lambda c: "we are the stronger team" if c["x"][5] >= 100 else "we are the weaker team" if c["x"][5] <= -100 else "close"),
        ("A monk on the split", lambda c: None if c["x"][13] is None else "yes" if c["x"][13] > 0 else "no"),
        ("Self-defence on the split", lambda c: None if c["x"][14] is None else "none" if c["x"][14] == 0 else "some"))


def split_factors(S, pr):
    """Stage 3 of the answer to a split (R-568): what else changes the answer. For each thing the defending team can see, in each of its groups: what meeting
    the split with as many defenders as it has players, or more, 20 s in is worth against fewer (nobody, a defender still on his way, one against two, two
    against three), in win points 180 s on, set against the same position (one straight fit on the matching variables for that size of split, with the
    answer's worth let differ by group; ranges from drawing whole matches again). As `factors` for the flag: a reading of where to look. Many groups are
    read, so about one in ten will look clear by chance, and none of it is advice until it holds on unseen matches."""
    import random
    out = {}
    pr("\nF. What else changes the answer: what meeting the split with as many defenders as it has players, or more, is worth against fewer, 20 s in; 180 s on, at the same position, by what the defending team can see")
    pr("   + = matching it is ahead; - = fewer is ahead. MATTERS: the worth differs between the groups beyond a 1 in 100 chance; MAY MATTER: beyond 1 in 20. Read as where to look: about one row in ten is clear by chance.")
    for name, s in S.items():
        idx = np.array([i for i in range(len(s.C)) if s.call[i] in SPLIT_FEWER + SPLIT_MATCHED])
        isa = np.array([float(s.call[i] in SPLIT_MATCHED) for i in idx]); y = s.y["180"][idx]; Zs = s.Z[idx]; rid = s.rid[idx]
        by = collections.defaultdict(list)
        for n_, r in enumerate(rid): by[r].append(n_)
        ids = sorted(by)
        pr(f"\n   {name} ({len(idx)}: {int(isa.sum())} matched it or more, {int(len(isa) - isa.sum())} fewer)")
        o = out[name] = {}
        # the whole size first, with no groups: the plain worth of matching it, at the same position
        def est0(rows):
            A = np.column_stack([np.ones(len(rows)), Zs[rows], isa[rows]]); return float(np.linalg.lstsq(A, y[rows], rcond=None)[0][-1])
        rnd, dr0 = random.Random(7), []
        for _ in range(DRAWS):
            rows = np.array([n_ for k in (rnd.choice(ids) for _ in ids) for n_ in by[k]]); dr0.append(est0(rows))
        e0 = est0(np.arange(len(idx))); l0, h0 = np.percentile(dr0, 5), np.percentile(dr0, 95)
        o["all"] = {"worth": [e0, float(l0), float(h0)], "matched": int(isa.sum()), "fewer": int(len(isa) - isa.sum())}
        pr(f"     every case of this size: {e0:+5.1f} ({l0:+.1f} to {h0:+.1f})  " + ("matching it ahead" if l0 > 0 else "fewer ahead" if h0 < 0 else "not clear"))
        for label, f in split_factor_list(s):
            lev = [f(s.C[i]) for i in idx]
            names = [k for k, n in collections.Counter(x for x in lev if x is not None).most_common() if n >= MIN_PLAYS]
            names = [k for k in names if sum(1 for x, a in zip(lev, isa) if x == k and a) >= 10 and sum(1 for x, a in zip(lev, isa) if x == k and not a) >= 10]
            if len(names) < 2: continue
            G = np.array([[float(x == k) for k in names] for x in lev]); keep = G.sum(axis=1) > 0
            def est(rows):
                A = np.column_stack([np.ones(len(rows)), Zs[rows], G[rows][:, 1:], G[rows] * isa[rows][:, None]])
                return np.linalg.lstsq(A, y[rows], rcond=None)[0][-len(names):]
            base = np.flatnonzero(keep); e = est(base)
            rnd, dr = random.Random(7), []
            for _ in range(DRAWS):
                rows = np.array([n_ for k in (rnd.choice(ids) for _ in ids) for n_ in by[k] if keep[n_]])
                if len(rows) > Zs.shape[1] + 2 * len(names) + 5: dr.append(est(rows))
            dr = np.array(dr); lo_, hi_ = np.percentile(dr, 5, axis=0), np.percentile(dr, 95, axis=0)
            a_, b_ = int(np.argmax(e)), int(np.argmin(e)); gap = dr[:, a_] - dr[:, b_]
            matters = "matters" if float(np.percentile(gap, 1)) > 0 else "may matter" if float(np.percentile(gap, 5)) > 0 else None
            o[label] = {"matters": matters, "gap": [float(e[a_] - e[b_]), float(np.percentile(gap, 5)), float(np.percentile(gap, 95))],
                        "groups": {k: {"matched": int(((G[:, n_] == 1) & (isa == 1)).sum()), "fewer": int(((G[:, n_] == 1) & (isa == 0)).sum()), "worth": [float(e[n_]), float(lo_[n_]), float(hi_[n_])]} for n_, k in enumerate(names)}}
            pr(f"     {label}" + (f"   {matters.upper()}: {e[a_] - e[b_]:.1f} win points between its groups ({np.percentile(gap, 5):+.1f} to {np.percentile(gap, 95):+.1f})" if matters else "   (no clear difference between its groups)"))
            for n_, k in enumerate(names):
                g = o[label]["groups"][k]; w = "matching it ahead" if lo_[n_] > 0 else "fewer ahead" if hi_[n_] < 0 else "not clear"
                pr(f"       {k:40} {g['matched']:4} matched, {g['fewer']:3} fewer: {e[n_]:+5.1f} ({lo_[n_]:+.1f} to {hi_[n_]:+.1f})  {w}")
    return out


def splits(path, out_json=None):
    """The split family (R-558), the answer to a split. Stage 1: do the readings go with what any player knows, and a first table of what followed each
    answer, as it fell (a description: a row of that table is set against no like spot). Stage 2 (section E): each answer set against like spots, and the
    test on matches the advice never saw. A reading is no advice until that test shows a gain for its size of split."""
    D, M = load(path); B, P = prices(D, M)
    C, skipped = split_cases(D, M, B)
    lines, res = [], {"cases": len(C), "skipped": dict(skipped), "timing": {}, "checks": {}, "as_it_fell": {}}
    pr = lambda x="": (lines.append(x), print(x))
    q3 = lambda L: tuple(float(np.percentile(L, q)) for q in (25, 50, 75)) if L else (0, 0, 0)
    pr(f"The answer to a split (R-558), stage 1, on {len(M)} matches: {len(C)} splits in {len({c['rid'] for c in C})} matches, each read from the side of the team it is sent against"
       + "".join(f"; set aside, {k}: {v}" for k, v in skipped.most_common() if v))
    pr("\nA. The clock of a split, from the second it is told (R-562)")
    rd = [c["reached"] for c in C if c["reached"] is not None]; fd = [c["first_defender"] for c in C if c["first_defender"] is not None]
    res["timing"] = {"reaches their base, footmen or a defender (quartiles, s)": q3(rd), "first defender on it (quartiles, s)": q3(fd), "never defended": sum(1 for c in C if c["first_defender"] is None), "lasts (quartiles, s)": q3([c["lasted"] for c in C])}
    pr(f"   it can first do something (their footmen, base or pit, or a defender on it) {q3(rd)[1]:.0f} s after it is told (the middle half {q3(rd)[0]:.0f} to {q3(rd)[2]:.0f} s)")
    pr(f"   the first defender is on it {q3(fd)[1]:.0f} s after it is told (the middle half {q3(fd)[0]:.0f} to {q3(fd)[2]:.0f} s); no defender ever: {res['timing']['never defended']} ({100 * res['timing']['never defended'] / max(len(C), 1):.0f}%)")
    pr(f"   it lasts {q3([c['lasted'] for c in C])[1]:.0f} s (the middle half {q3([c['lasted'] for c in C])[0]:.0f} to {q3([c['lasted'] for c in C])[2]:.0f} s)")
    pr("   by the second after it is told: still on their ground, and of those with a defender on it")
    res["timing"]["by second"] = {}
    for h in sorted(C[0]["by"]) if C else ():
        on_ = [c for c in C if c["by"][h] and c["by"][h][0] > 0]; df = sum(1 for c in on_ if c["by"][h][1] > 0)
        res["timing"]["by second"][h] = {"on their ground": len(on_), "defended": df}
        pr(f"     {h:3} s: {len(on_):5} of {len(C)} on their ground ({100 * len(on_) / max(len(C), 1):.0f}%); a defender on it in {100 * df / max(len(on_), 1):.0f}% of those")
    for r in SPLIT_READS:
        X = [c for c in C if c["read"][r][0]]; n_ = collections.Counter(c["read"][r][0] for c in X)
        res["timing"][f"read at {r} s"] = {"read": len(X), "over or not yet on their ground": len(C) - len(X), "by size": dict(n_)}
        pr(f"   read {r} s in: {len(X)} splits on their ground ({len(C) - len(X)} over by then or not yet there): " + ", ".join(f"{z} {n_[z]}" for z in SPLIT_SIZES))
    R0 = SPLIT_READS[0]; ans = lambda c: c["read"][R0][1]; size = lambda c: c["read"][R0][0]
    X = [c for c in C if size(c)]
    pr(f"\nB. The readings: what any player knows, asked of the answer read {R0} s in ({len(X)} splits). Each is two groups set side by side with a 90% range over whole matches.")
    def check(name, f, g, expect, y, fa, ga, unit=""):
        for c in X: c["_y"] = y(c)
        d, lo, hi, na, nb = _num_range(X, f, g)
        if d is None or min(na, nb) < MIN_PLAYS: pr(f"   {name}: too few ({na} and {nb})"); res["checks"][name] = {"reads": "too few", "n": [na, nb]}; return
        sc = 100 if unit == "%" else 1
        word = "HOLDS" if (lo > 0 if expect > 0 else hi < 0) else "AGAINST" if (hi < 0 if expect > 0 else lo > 0) else "not clear"
        a_, b_ = np.mean([c["_y"] for c in X if f(c)]), np.mean([c["_y"] for c in X if (not f(c)) and g(c)])
        pr(f"   {name}: {fa} {sc * a_:.{0 if unit == '%' else 2}f}{unit} ({na}); {ga} {sc * b_:.{0 if unit == '%' else 2}f}{unit} ({nb}); difference {sc * d:+.{0 if unit == '%' else 2}f}{unit} ({sc * lo:+.{0 if unit == '%' else 2}f} to {sc * hi:+.{0 if unit == '%' else 2}f})   {word}")
        res["checks"][name] = {"first": float(a_), "second": float(b_), "difference": float(d), "range": [float(lo), float(hi)], "n": [na, nb], "reads": word}
    pit = lambda c: c["pit"][180]; none_ = lambda c: ans(c) in SPLIT_NONE; solo = lambda c: size(c) == SPLIT_SIZES[0]
    fewer = lambda c: ans(c) in ("one defender", "two monks", "fewer than the split"); even = lambda c: ans(c) in ("mirror", "one defender, a monk", "one defender, not a monk"); extra = lambda c: ans(c) in ("add one", "two or more extra", "a collapse")
    check("S1 a split nobody defends takes more pit NPCs than a defended one (3 min)", none_, lambda c: not none_(c), +1, pit, "nobody on it", "defended")
    check("S2 undefended, two or more take more pit NPCs than one player (3 min)", lambda c: none_(c) and not solo(c), lambda c: none_(c) and solo(c), +1, pit, "two or more", "one player")
    check("S3 a defender there within 15 s, fewer pit NPCs than one there after 45 s or never (3 min)", lambda c: c["first_defender"] is not None and c["first_defender"] <= 15, lambda c: c["first_defender"] is None or c["first_defender"] >= 45, -1, pit, "within 15 s", "after 45 s or never")
    check("S4 fewer defenders than the split, more pit NPCs than a mirror or more (3 min)", fewer, lambda c: even(c) or extra(c), +1, pit, "fewer than the split", "mirror or more")
    check("S5 the whole team on it, a split player dies more often than against a mirror (90 s)", lambda c: ans(c) == "the whole team", even, +1, lambda c: float(c["split_dies"][90] > 0), "the whole team", "mirror", unit="%")
    check("S6 one or more extra defenders, a split player dies more often than against a mirror (90 s)", extra, even, +1, lambda c: float(c["split_dies"][90] > 0), "extra defenders", "mirror", unit="%")
    check("S7 fewer defenders than the split, a defender dies more often than in a mirror or more (90 s)", fewer, lambda c: even(c) or extra(c), +1, lambda c: float(c["defender_dies"][90] > 0), "fewer than the split", "mirror or more", unit="%")
    # (a lone player defended by a damage player against one defended by a monk is not asked: he dropped that truth, R-534)
    pr(f"\nC. As it fell: what followed each answer, for the team the split is sent against (a description set against no like spot: who answers how follows the spot)")
    pr("   started at = that team's chance of winning when the split is told; 60 s before = what the minute before had done to it, in win points; pit NPCs, split and defender deaths are the split's own;")
    pr("   net kills (theirs minus ours), flags and win points are over the whole map, 90 and 180 s from the telling.")
    head = f"     {'':26} {'cases':>5}  {'started at':>10}  {'60 s before':>11}  {'pit NPCs 90':>11}  {'pit NPCs 180':>12}  {'Lord dmg 180':>12}  {'split loses one':>15}  {'defence loses one':>17}  {'net kills':>9}  {'flags':>6}  {'win pts 90':>10}  {'win pts 180':>11}"
    for r in SPLIT_READS:
        o_r = res["as_it_fell"][f"read {r} s in"] = {}
        for z in SPLIT_SIZES:
            V_ = [c for c in C if c["read"][r][0] == z]
            if not V_: continue
            pr(f"\n   A split of {z}, the answer read {r} s in ({len(V_)})"); pr(head); o = o_r[z] = {}
            for a in SPLIT_ANSWERS:
                V = [c for c in V_ if c["read"][r][1] == a]
                if not V: continue
                h = [c["hard"]["90"] for c in V]; pre = [c["pre"] for c in V if c["pre"] is not None]; fl = [x["lead_change"] for x in h if x["lead_change"] is not None]
                row = o[a] = {"cases": len(V), "matches": len({c["rid"] for c in V}), "started at": 100 * float(np.mean([c["p0"] for c in V])), "the 60 s before": float(np.mean(pre)) if pre else None,
                              "pit NPCs 90": float(np.mean([c["pit"][90] for c in V])), "pit NPCs 180": float(np.mean([c["pit"][180] for c in V])), "Lord damage 180": float(np.mean([c["lord"][180] for c in V])), "split loses one": 100 * float(np.mean([c["split_dies"][90] > 0 for c in V])),
                              "defence loses one": 100 * float(np.mean([c["defender_dies"][90] > 0 for c in V])), "net kills": float(np.mean([x["deaths"][1] - x["deaths"][0] for x in h])), "flags": float(np.mean(fl)) if fl else 0.0,
                              "win points 90": float(np.mean([c["v"]["90"] for c in V])), "win points 180": float(np.mean([c["v"]["180"] for c in V]))}
                pr(f"     {a:26} {len(V):5}  {row['started at']:9.0f}%  {('' if row['the 60 s before'] is None else format(row['the 60 s before'], '+.1f')):>11}  {row['pit NPCs 90']:11.2f}  {row['pit NPCs 180']:12.2f}  {row['Lord damage 180']:12.0f}  {row['split loses one']:14.0f}%  "
                   f"{row['defence loses one']:16.0f}%  {row['net kills']:+9.2f}  {row['flags']:+6.2f}  {row['win points 90']:+10.1f}  {row['win points 180']:+11.1f}" + ("   (under the floor)" if len(V) < MIN_PLAYS or row["matches"] < MIN_MATCHES else ""))
    # how an answer changes between the reads: the first read is not the whole answer
    mv = collections.Counter((c["read"][SPLIT_READS[0]][1], c["read"][SPLIT_READS[1]][1] or "over by then") for c in C if c["read"][SPLIT_READS[0]][0])
    pr(f"\nD. From the answer {SPLIT_READS[0]} s in to the answer {SPLIT_READS[1]} s in (the commonest moves)")
    res["moves"] = [[a, b, n] for (a, b), n in mv.most_common(14)]
    for (a, b), n in mv.most_common(14): pr(f"     {a:26} -> {b:26} {n:5}")
    # ---- like spots (stage 2): each answer set against the nearest cases of the other answers, set level with the case read, and the test on unseen matches
    by_s = collections.defaultdict(list)
    for c in C:
        if c["scenario"]: by_s[c["scenario"]].append(c)
    S = {k: Scenario(v) for k, v in sorted(by_s.items(), key=lambda kv: SPLIT_SIZES.index(kv[0][len("A split of "):])) if len(v) >= MIN_PLAYS}
    K, _ = choose_k(S); res["K"] = K; res["like_spots"] = {}; res["advice_test"] = {}
    pr(f"\nE. Like spots: the answer read {R0} s in, set against the {K} nearest cases of each other answer from other matches, set level with the case read (the floor of {MIN_PLAYS} plays and {MIN_MATCHES} matches an answer)")
    pr("   matched on: " + ", ".join(SPLIT_VARS))
    pr("   E1. Each answer's worth at the same spot, 180 s on, in win points against the commonest answer (the mean over every case of that size, with the 90% range such a comparison has at one spot). A reading, not advice.")
    for name, s_ in S.items():
        ref = s_.calls[0]; rows_ = collections.defaultdict(list); o = res["like_spots"][name] = {"cases": len(s_.C), "against": ref, "answers": {}}
        for i in range(len(s_.C)):
            r = s_.read(i, K, False)
            if ref not in r["calls"]: continue
            for a_, w in r["calls"].items():
                if a_ != ref: rows_[a_].append((w["worth"] - r["calls"][ref]["worth"], math.hypot(w["se"], r["calls"][ref]["se"])))
        pr(f"\n   {name} ({len(s_.C)}); against \"{ref}\" ({int((s_.call == ref).sum())} cases)")
        for a_ in s_.calls[1:]:
            n_a = int((s_.call == a_).sum())
            if a_ not in rows_ or len(rows_[a_]) < MIN_PLAYS: pr(f"     {a_:26} {n_a:4} cases: too few to set beside it"); o["answers"][a_] = {"cases": n_a, "reads": "too few"}; continue
            # the range is the usual one at a single spot (the two sets of nearest cases, the plays of one match as one draw), not narrowed by averaging over spots:
            # the same nearest cases stand behind most spots of a size, so the spots are not separate evidence (a first form drew whole matches again over the
            # spots and gave ranges a tenth as wide)
            mu, se_ = float(np.mean([d_ for d_, _ in rows_[a_]])), float(np.mean([e_ for _, e_ in rows_[a_]]))
            lo, hi = mu - Z * se_, mu + Z * se_
            word = "better" if lo > 0 else "worse" if hi < 0 else "no clear difference"
            o["answers"][a_] = {"cases": n_a, "worth": mu, "range": [float(lo), float(hi)], "reads": word}
            pr(f"     {a_:26} {n_a:4} cases: {mu:+5.1f} ({lo:+.1f} to {hi:+.1f})   {word}")
    pr(f"\n   E2. The test on matches the advice never saw: where the advice is clear, teams whose answer {R0} s in matched it against those whose answer did not, in win points; and the same test on the 60 s before, which no answer can change.")
    for name, s_ in S.items():
        o = res["advice_test"][name] = {}
        for H in HORIZONS:
            t = advice_test({name: s_}, K, H); o[H] = {k: v for k, v in t.items()}
            adv = ", ".join(f"{a_} {n_}" for a_, n_ in sorted(t.get("advice", {}).items(), key=lambda q: -q[1]))
            if "v" not in t: pr(f"   {name}, {H} s on: {len(s_.C)} cases, clear advice in {t['rows']}: too few to call [{adv}]"); continue
            pre = t.get("pre"); lv = "" if not pre else f"; in the 60 s before {pre['effect']:+.1f} ({pre['range'][0]:+.1f} to {pre['range'][1]:+.1f})" + ("" if pre["verdict"] == "no clear difference" else " NOT LEVEL")
            pr(f"   {name}, {H} s on: {len(s_.C)} cases, clear advice in {t['rows']} ({adv}), matched {t['matched']}: {t['v']['effect']:+.1f} ({t['v']['range'][0]:+.1f} to {t['v']['range'][1]:+.1f}) {t['v']['verdict']}; "
               f"in how the match ended {t['end']['effect']:+.1f} ({t['end']['range'][0]:+.1f} to {t['end']['range'][1]:+.1f}){lv}")
    res["factors"] = split_factors(S, pr)
    N = [p for p in D["plays"] if p["play"] == "numbers" and p.get("source") == "split elsewhere"]
    res["main_fight_while_a_split_is_out"] = len(N)
    pr(f"\nG. The other half of the family, not read here: the main fight while a split is out: {len(N)} numbers rows \"from a split elsewhere\" in {len({p['rid'] for p in N})} matches (his calls of R-551, with collapse and send more).")
    if out_json: json.dump(res, open(out_json, "w"), indent=1, default=float)
    return res


# ---- the split family, the other half (R-558): the main fight while a split is out
MAIN_SCEN = ("Up at the main fight, their split in our base", "Down at the main fight, our split out", "Down at the main fight, their split in our base", "Up at the main fight, our split out")
COLLAPSE, PULL_BACK, SEND_MORE, BRING_BACK = "collapse on the split", "pull a defender back to the main fight", "send more on the split", "bring players back from the split"
MAIN_VARS = ("flag lead", "seconds to the boost", "own players at the main fight", "their players at the main fight", "own morale", "their morale", "strength gap", "seconds to the base res", "own chance of winning at that second",
             "own main team's place", "their main team's place", "own dead", "their dead", "players on our split", "their defenders on it", "players on their split", "our defenders on it")


def _main_whose(p):
    """Whose split is out as the numbers at the main fight are told: ours, theirs, both, or none on the enemy's ground in the first 20 s (players away who are
    still on their way, or a split that is not told)."""
    sp = [v for h, v in zip(p["track"]["at"], p["track"]["splits"]) if h <= NUM_READ and v]
    own, th = max((v[0] for v in sp), default=0), max((v[2] for v in sp), default=0)
    return "both" if own and th else "ours" if own else "theirs" if th else "none"


def _main_call(p, read=NUM_READ, lost=(False, False)):
    """The call of a main team while a split is out, read `read` s after the numbers are told (R-556), in his words (R-551, with "collapse" and "send more on
    split", which he named for this half): a change to the split first (a split already there as the numbers are told: more of ours on it, or more of our
    defenders on theirs; fewer of either), else where the main team stands and whether a runner has gone, as for any numbers (`_num_call`)."""
    i = p["track"]["at"].index(read); a, b = p["track"]["splits"][0], p["track"]["splits"][i]
    if a is None or b is None: return None
    whose = _main_whose(p)
    # fewer on a split, or on its defence, is a call only when the player came away alive: a death there is no call (R-571; of 266 rows with fewer on the split
    # 41 were a split player dying, teams at 30% and 2.3 kills down, against 55% and level for the rest). `lost`: a player of our split, and a defender of ours
    # on theirs, died in the window; such a row is read by where the main team stands, as any numbers
    if whose == "theirs" and a[2] > 0:
        if b[3] > a[3]: return COLLAPSE
        if b[3] < a[3] and b[2] > 0 and not lost[1]: return PULL_BACK
    if whose == "ours" and a[0] > 0:
        if b[0] > a[0]: return SEND_MORE
        if b[0] < a[0] and not lost[0]: return BRING_BACK
    return _num_call(p, read)


def main_cases(D, M, B):
    """One case a clear numbers situation at the main fight with a split out, from each side: whose split it is, the call 20 s in, the hard results on the fixed
    record and their price, from prices that never saw its match (as `numbers_cases`)."""
    out, skipped = [], collections.Counter()
    SP = collections.defaultdict(dict)                       # every split of the match, for the deaths on it and among its defenders
    for p in D["plays"]:
        if p["play"] == "split" and not p.get("change") and p.get("split"): SP[p["rid"]][p["split"]["id"]] = p["split"]
    def lost_in(p, read):                                    # (a player of a split of ours died, a defender of ours on a split of theirs died), from 2 s before the numbers are told to 2 s after the read
        own = any(s_["tm"] == p["tm"] and any(-2 <= s_["told"] + x_ - p["t0"] <= read + 2 for x_ in s_["split_deaths"]) for s_ in SP[p["rid"]].values())
        dfd = any(s_["tm"] != p["tm"] and any(-2 <= s_["told"] + x_ - p["t0"] <= read + 2 for x_ in s_["defender_deaths"]) for s_ in SP[p["rid"]].values())
        return own, dfd
    for p in D["plays"]:
        if p["play"] != "numbers" or p.get("source") != "split elsewhere": continue
        if p.get("clear") is False: skipped["no clear decision (the numbers never held, or a player counted twice)"] += 1; continue
        if "state" not in p or "splits" not in p["track"]: raise ValueError(f"numbers play {p['id']} carries no position or no splits: run moments.py all again on this engine (R-460)")
        m, st, af = M[p["rid"]], p["state"], p["after"]
        if not m["winner"]: skipped["no winner recorded"] += 1; continue
        whose = _main_whose(p)
        if whose == "none": skipped["no told split on the enemy's ground in the first 20 s (players on their way, or the whole team's turn)"] += 1; continue
        if whose == "both": skipped["a split of each team out at once (a trade): too few to read apart"] += 1; continue
        gap = m["gap"][p["team"]]
        ends = {H: None if af[H]["ended"] else position(st, af[H], gap, True) for H in HORIZONS}
        if st["flag_lead"] is None or af["90"]["lead"][0] is None or any(ends[H] is None and not af[H]["ended"] for H in ends): skipped["flag lead not read"] += 1; continue
        call = _main_call(p, NUM_READ, lost_in(p, NUM_READ))
        if call is None: skipped[f"no main team alive {NUM_READ} s in, or the match over"] += 1; continue
        beta, won = B[m["fold"]], float(m["winner"] == p["team"])
        p0 = chance(beta, position(st, af["90"], gap, False))
        stp = p["track"]["steps"][0]; mor = af["90"]["morale"]; sp0 = p["track"]["splits"][0]
        bf, pre = p.get("before"), None
        if bf and bf["after"]["lead"][0] is not None and "npcs_lost" in bf["state"]: pre = 100 * (p0 - chance(beta, position(bf["state"], bf["after"], gap, False)))
        n = [int(x) for x in p["numbers"].split("v")]; k = p["clock"]; side = p["numbers_side"]
        scen = MAIN_SCEN[{("up", "theirs"): 0, ("down", "ours"): 1, ("down", "theirs"): 2, ("up", "ours"): 3}[(side, whose)]]
        x = [st["flag_lead"], st["boost_in"], n[0], n[1], mor[0][0], mor[1][0], gap, k["res_in"], 100 * p0, stp[0], stp[1], k["dead"][0], k["dead"][1]] + list(sp0)
        out.append({"id": p["id"], "rid": p["rid"], "team": p["team"], "t": p["t0"], "side": side, "whose": whose, "call": call, "by": abs(n[0] - n[1]), "numbers": p["numbers"], "x": x, "more": None,
                    "fold": m["fold"], "won": won, "held": False, "kind": "main fight", "later": _main_call(p, NUM_LATER, lost_in(p, NUM_LATER)), "scenario": scen, "lasted": k["end"] - p["t0"], "res_in": k["res_in"], "p0": p0, "pre": pre,
                    "arriving": (sp0[2] if whose == "theirs" else sp0[0]) == 0, "split0": sp0, "split20": p["track"]["splits"][p["track"]["at"].index(NUM_READ)],
                    "v": {H: 100 * ((won if af[H]["ended"] else chance(beta, ends[H])) - p0) for H in HORIZONS},
                    "hard": {H: {"deaths": af[H]["deaths"], "npcs": af[H]["npcs"], "lead_change": af[H]["lead_change"], "pit": [sum(1 for z in af[H]["npc_kinds"][q] if z in PIT) for q in (0, 1)]} for H in HORIZONS}})
    return out, skipped


def main_fight(path, out_json=None):
    """The split family's other half (R-558), the main fight while a split is out: the readings (what any player knows), what followed each call, as it fell,
    then like spots and the test on unseen matches. A report: no row of it is advice until the held-out test shows a gain for its scenario."""
    D, M = load(path); B, P = prices(D, M)
    C, skipped = main_cases(D, M, B)
    lines, res = [], {"cases": len(C), "skipped": dict(skipped), "counts": {}, "checks": {}, "as_it_fell": {}}
    pr = lambda x="": (lines.append(x), print(x))
    pr(f"The main fight while a split is out (R-558), on {len(M)} matches: {len(C)} situations read from one side each" + "".join(f"; set aside, {k}: {v}" for k, v in skipped.most_common()))
    pr("\nA. How many (a situation is told once for the team up and once for the team down)")
    for sc in MAIN_SCEN:
        X = [c for c in C if c["scenario"] == sc]; res["counts"][sc] = {"cases": len(X), "matches": len({c["rid"] for c in X}), "the split still on its way as the numbers are told": sum(c["arriving"] for c in X)}
        up1 = sum(1 for c in X if c["by"] == 1)
        pr(f"   {sc:48} {len(X):5} in {len({c['rid'] for c in X}):3} matches; by one player {up1}, by two or more {len(X) - up1}; lasted (middle) {np.median([c['lasted'] for c in X]) if X else 0:3.0f} s; the split still on its way as the numbers are told: {sum(c['arriving'] for c in X)}")
    kill = lambda c, H="90": float(c["hard"][H]["deaths"][1] > c["hard"][H]["deaths"][0])
    pr(f"\nB. The readings: what any player knows ({len(C)} situations). Each is two groups set side by side with a 90% range over whole matches. A kill = more of theirs die than of ours in the 90 s after the numbers are told.")
    def check(name, pop, f, g, expect, y, fa, ga, unit="%"):
        X = [c for c in C if pop(c)]
        for c in X: c["_y"] = y(c)
        d, lo, hi, na, nb = _num_range(X, f, g)
        if d is None or min(na, nb) < MIN_PLAYS: pr(f"   {name}: too few ({na} and {nb})"); res["checks"][name] = {"reads": "too few", "n": [na, nb]}; return
        sc = 100 if unit == "%" else 1; dp = 0 if unit == "%" else 2
        word = "HOLDS" if (lo > 0 if expect > 0 else hi < 0) else "AGAINST" if (hi < 0 if expect > 0 else lo > 0) else "not clear"
        a_, b_ = np.mean([c["_y"] for c in X if f(c)]), np.mean([c["_y"] for c in X if (not f(c)) and g(c)])
        pr(f"   {name}: {fa} {sc * a_:.{dp}f}{unit} ({na}); {ga} {sc * b_:.{dp}f}{unit} ({nb}); difference {sc * d:+.{dp}f}{unit} ({sc * lo:+.{dp}f} to {sc * hi:+.{dp}f})   {word}")
        res["checks"][name] = {"first": float(a_), "second": float(b_), "difference": float(d), "range": [float(lo), float(hi)], "n": [na, nb], "reads": word}
    up, down, theirs, ours = (lambda c: c["side"] == "up"), (lambda c: c["side"] == "down"), (lambda c: c["whose"] == "theirs"), (lambda c: c["whose"] == "ours")
    check("M1 the team up at the main fight kills more often than the team down", lambda c: True, up, down, +1, kill, "up", "down")
    check("M2 up by two or more kills more often than up by one", up, lambda c: c["by"] >= 2, lambda c: c["by"] == 1, +1, kill, "up by two or more", "up by one")
    check("M3 their split in our base and we are up at the main fight: we lose more pit NPCs than when we are down there (3 min)", theirs, up, down, +1, lambda c: c["hard"]["180"]["pit"][0], "up at the main fight", "down at the main fight", unit="")
    check("M4 our split out and we are down at the main fight: we take more pit NPCs than when we are up there (3 min)", ours, down, up, +1, lambda c: c["hard"]["180"]["pit"][1], "down at the main fight", "up at the main fight", unit="")
    check("M5 a collapse on their split: they lose a player more often than when nobody is added (90 s)", lambda c: theirs(c) and not c["arriving"], lambda c: c["call"] == COLLAPSE, lambda c: c["call"] != COLLAPSE, +1,
          lambda c: float(c["hard"]["90"]["deaths"][1] > 0), "a collapse", "nobody added")
    check("M6 more sent on our split: more of their pit NPCs fall than when nobody is added (3 min)", lambda c: ours(c) and not c["arriving"], lambda c: c["call"] == SEND_MORE, lambda c: c["call"] != SEND_MORE, +1,
          lambda c: c["hard"]["180"]["pit"][1], "more sent", "nobody added", unit="")
    # The trade itself: with a split out, the side up at the main fight against the side down there, whoever's split it is. Not a call (how many are sent home, or
    # on the split, is the answer to the split; the numbers at the main fight are what that leaves), so it is told as a reading with the same test on the 60 s
    # before: a side that was already gaining then marks the situation (SPEC 5, rule 4)
    pr("\n   The trade: the side up at the main fight against the side down there, in win points (and the same comparison on the 60 s before, which the numbers cannot have caused)")
    res["trade"] = {}
    for lab, pop in (("their split in our base (up: fewer sent home than they split; down: more)", theirs), ("our split out (up: they sent more home than we split; down: fewer)", ours)):
        X = [c for c in C if pop(c)]; o = res["trade"][lab] = {}
        for key, f_ in (("90 s on", lambda c: c["v"]["90"]), ("180 s on", lambda c: c["v"]["180"]), ("the 60 s before", lambda c: c["pre"])):
            Y = [c for c in X if f_(c) is not None]
            for c in Y: c["_y"] = f_(c)
            d, lo, hi, na, nb = _num_range(Y, up, down); o[key] = {"difference": float(d), "range": [float(lo), float(hi)], "n": [na, nb]}
        pr(f"     {lab}: 90 s on {o['90 s on']['difference']:+.1f} ({o['90 s on']['range'][0]:+.1f} to {o['90 s on']['range'][1]:+.1f}); 180 s on {o['180 s on']['difference']:+.1f} ({o['180 s on']['range'][0]:+.1f} to {o['180 s on']['range'][1]:+.1f}); "
           f"the 60 s before {o['the 60 s before']['difference']:+.1f} ({o['the 60 s before']['range'][0]:+.1f} to {o['the 60 s before']['range'][1]:+.1f})" + ("  NOT LEVEL before: partly who is up" if o["the 60 s before"]["range"][0] > 0 or o["the 60 s before"]["range"][1] < 0 else ""))
    pr(f"\nC. As it fell: what followed each call, read {NUM_READ} s in, 90 and 180 s on (a description set against no like spot: who makes a call follows the spot)")
    pr("   started at = own chance of winning when the numbers are told; 60 s before = what the minute before had done to it, in win points; pit NPCs are over the whole map, 180 s on.")
    head = f"     {'':52} {'cases':>5}  {'started at':>10}  {'60 s before':>11}  {'they lose one':>13}  {'we lose one':>11}  {'net kills':>9}  {'our pit NPCs':>12}  {'their pit NPCs':>14}  {'flags':>6}  {'win pts 90':>10}  {'win pts 180':>11}"
    for sc in MAIN_SCEN:
        X = [c for c in C if c["scenario"] == sc]; pr(f"\n   {sc} ({len(X)})"); pr(head); o = res["as_it_fell"][sc] = {}
        for call, _ in collections.Counter(c["call"] for c in X).most_common():
            V = [c for c in X if c["call"] == call]
            h = [c["hard"]["90"] for c in V]; pre = [c["pre"] for c in V if c["pre"] is not None]; fl = [x["lead_change"] for x in h if x["lead_change"] is not None]
            row = o[call] = {"cases": len(V), "matches": len({c["rid"] for c in V}), "started at": 100 * float(np.mean([c["p0"] for c in V])), "the 60 s before": float(np.mean(pre)) if pre else None,
                             "they lose one": 100 * float(np.mean([x["deaths"][1] > 0 for x in h])), "we lose one": 100 * float(np.mean([x["deaths"][0] > 0 for x in h])), "net kills": float(np.mean([x["deaths"][1] - x["deaths"][0] for x in h])),
                             "our pit NPCs": float(np.mean([c["hard"]["180"]["pit"][0] for c in V])), "their pit NPCs": float(np.mean([c["hard"]["180"]["pit"][1] for c in V])), "flags": float(np.mean(fl)) if fl else 0.0,
                             "win points 90": float(np.mean([c["v"]["90"] for c in V])), "win points 180": float(np.mean([c["v"]["180"] for c in V]))}
            pr(f"     {call:52} {len(V):5}  {row['started at']:9.0f}%  {('' if row['the 60 s before'] is None else format(row['the 60 s before'], '+.1f')):>11}  {row['they lose one']:12.0f}%  {row['we lose one']:10.0f}%  {row['net kills']:+9.2f}  "
               f"{row['our pit NPCs']:12.2f}  {row['their pit NPCs']:14.2f}  {row['flags']:+6.2f}  {row['win points 90']:+10.1f}  {row['win points 180']:+11.1f}" + ("   (under the floor)" if len(V) < MIN_PLAYS or row["matches"] < MIN_MATCHES else ""))
    by_s = collections.defaultdict(list)
    for c in C: by_s[c["scenario"]].append(c)
    S = {k: Scenario(by_s[k]) for k in MAIN_SCEN if len(by_s[k]) >= MIN_PLAYS}
    K, _ = choose_k(S); res["K"] = K; res["like_spots"] = {}; res["advice_test"] = {}
    pr(f"\nD. Like spots: the call {NUM_READ} s in, set against the {K} nearest cases of each other call from other matches, set level with the case read (the floor of {MIN_PLAYS} plays and {MIN_MATCHES} matches a call)")
    pr("   matched on: " + ", ".join(MAIN_VARS))
    pr("   D1. Each call's worth at the same spot, 180 s on, in win points against the commonest call (the mean over every case of the scenario, with the 90% range such a comparison has at one spot). A reading, not advice.")
    for name, s_ in S.items():
        ref = s_.calls[0]; rows_ = collections.defaultdict(list); o = res["like_spots"][name] = {"cases": len(s_.C), "against": ref, "calls": {}}
        for i in range(len(s_.C)):
            r = s_.read(i, K, False)
            if ref not in r["calls"]: continue
            for a_, w in r["calls"].items():
                if a_ != ref: rows_[a_].append((w["worth"] - r["calls"][ref]["worth"], math.hypot(w["se"], r["calls"][ref]["se"])))
        pr(f"\n   {name} ({len(s_.C)}); against \"{ref}\" ({int((s_.call == ref).sum())} cases)")
        for a_ in s_.calls[1:]:
            n_a = int((s_.call == a_).sum())
            if a_ not in rows_ or len(rows_[a_]) < MIN_PLAYS: pr(f"     {a_:52} {n_a:4} cases: too few to set beside it"); o["calls"][a_] = {"cases": n_a, "reads": "too few"}; continue
            mu, se_ = float(np.mean([d_ for d_, _ in rows_[a_]])), float(np.mean([e_ for _, e_ in rows_[a_]]))
            lo, hi = mu - Z * se_, mu + Z * se_
            word = "better" if lo > 0 else "worse" if hi < 0 else "no clear difference"
            o["calls"][a_] = {"cases": n_a, "worth": mu, "range": [float(lo), float(hi)], "reads": word}
            pr(f"     {a_:52} {n_a:4} cases: {mu:+5.1f} ({lo:+.1f} to {hi:+.1f})   {word}")
    pr(f"\n   D2. The test on matches the advice never saw: where the advice is clear, teams whose call {NUM_READ} s in matched it against those whose call did not, in win points; and the same test on the 60 s before, which no call can change.")
    for name, s_ in S.items():
        o = res["advice_test"][name] = {}
        for H in HORIZONS:
            t = advice_test({name: s_}, K, H); o[H] = {k: v for k, v in t.items()}
            adv = ", ".join(f"{a_} {n_}" for a_, n_ in sorted(t.get("advice", {}).items(), key=lambda q: -q[1]))
            if "v" not in t: pr(f"   {name}, {H} s on: {len(s_.C)} cases, clear advice in {t['rows']}: too few to call [{adv}]"); continue
            pre = t.get("pre"); lv = "" if not pre else f"; in the 60 s before {pre['effect']:+.1f} ({pre['range'][0]:+.1f} to {pre['range'][1]:+.1f})" + ("" if pre["verdict"] == "no clear difference" else " NOT LEVEL")
            pr(f"   {name}, {H} s on: {len(s_.C)} cases, clear advice in {t['rows']} ({adv}), matched {t['matched']}: {t['v']['effect']:+.1f} ({t['v']['range'][0]:+.1f} to {t['v']['range'][1]:+.1f}) {t['v']['verdict']}; "
               f"in how the match ended {t['end']['effect']:+.1f} ({t['end']['range'][0]:+.1f} to {t['end']['range'][1]:+.1f}){lv}")
    if out_json: json.dump(res, open(out_json, "w"), indent=1, default=float)
    return res


# ---- the kinds that follow (R-572), stage 1: pushing the flagger, and a team held in its base
def _told(p, M, B):
    """The position a play was told at and what followed on the fixed record, priced without its match (`at_told` on the play, as on a split): the chance of
    winning it started from, what the minute before had done to it, the change 60, 90 and 180 s on, and the hard results. None where the flag lead is not read."""
    if "at_told" not in p: raise ValueError(f"{p['play']} play {p['id']} carries no position: run moments.py all again on this engine (R-460)")
    m, st, af = M[p["rid"]], p["at_told"]["state"], p["at_told"]["after"]
    if not m["winner"]: return None
    gap = m["gap"][p["team"]]
    ends = {H: None if af[H]["ended"] else position(st, af[H], gap, True) for H in HORIZONS}
    if st["flag_lead"] is None or af["90"]["lead"][0] is None or any(ends[H] is None and not af[H]["ended"] for H in ends): return None
    beta, won = B[m["fold"]], float(m["winner"] == p["team"])
    p0 = chance(beta, position(st, af["90"], gap, False))
    bf, pre = p["at_told"].get("before"), None
    if bf and bf["after"]["lead"][0] is not None and "npcs_lost" in bf["state"]: pre = 100 * (p0 - chance(beta, position(bf["state"], bf["after"], gap, False)))
    return {"id": p["id"], "rid": p["rid"], "team": p["team"], "t": p["t0"], "p0": p0, "pre": pre, "state": st,
            "v": {H: 100 * ((won if af[H]["ended"] else chance(beta, ends[H])) - p0) for H in HORIZONS},
            "hard": {H: {"deaths": af[H]["deaths"], "npcs": af[H]["npcs"], "lead_change": af[H]["lead_change"]} for H in HORIZONS}}


def _reading(pr, res, C, name, f, g, expect, y, fa, ga, unit="%"):
    """One reading any player knows, as a difference between two groups of cases with its 90% range over whole matches: HOLDS, AGAINST or not clear."""
    for c in C: c["_y"] = y(c)
    d, lo, hi, na, nb = _num_range(C, f, g)
    if d is None or na < MIN_PLAYS or nb < MIN_PLAYS: pr(f"   {name}: too few ({na} against {nb})"); res["checks"][name] = {"n": [na, nb], "reads": "too few"}; return
    sc = 100 if unit == "%" else 1
    word = "HOLDS" if (lo > 0 if expect > 0 else hi < 0) else "AGAINST" if (hi < 0 if expect > 0 else lo > 0) else "not clear"
    a_, b_ = float(np.mean([c["_y"] for c in C if f(c)])), float(np.mean([c["_y"] for c in C if (not f(c)) and g(c)]))
    fm = (lambda v: f"{sc * v:.0f}{unit}") if unit in ("%", " s") else (lambda v: f"{v:.2f}{unit}")
    dm = (lambda v: f"{sc * v:+.0f}{unit}") if unit in ("%", " s") else (lambda v: f"{v:+.2f}{unit}")
    pr(f"   {name}: {fa} {fm(a_)} ({na}); {ga} {fm(b_)} ({nb}); difference {dm(d)} ({dm(lo)} to {dm(hi)})   {word}")
    res["checks"][name] = {"first": a_, "second": b_, "difference": float(d), "range": [float(lo), float(hi)], "n": [na, nb], "reads": word}


def _fell(pr, out, label, V, extra=(), H="90"):
    """One row of an "as it fell" table: what followed, a description set against no like spot."""
    if not V: return
    h = [c["hard"][H] for c in V]; pre = [c["pre"] for c in V if c["pre"] is not None]
    row = {"cases": len(V), "matches": len({c["rid"] for c in V}), "started at": 100 * float(np.mean([c["p0"] for c in V])), "the 60 s before": float(np.mean(pre)) if pre else None,
           "they lose one": 100 * float(np.mean([x["deaths"][1] > 0 for x in h])), "we lose one": 100 * float(np.mean([x["deaths"][0] > 0 for x in h])),
           "net NPCs": float(np.mean([x["npcs"][1] - x["npcs"][0] for x in h])), "flags": float(np.mean([x["lead_change"] for x in h if x["lead_change"] is not None] or [0])),
           "win points 90": float(np.mean([c["v"]["90"] for c in V])), "win points 180": float(np.mean([c["v"]["180"] for c in V]))}
    for name, fn, _ in extra: row[name] = fn(V)
    out[label] = row
    pr(f"     {label:52} {len(V):5}  {row['started at']:9.0f}%  {('' if row['the 60 s before'] is None else format(row['the 60 s before'], '+.1f')):>11}  " + "  ".join(fmt(row[name]) for name, _, fmt in extra)
       + f"  {row['they lose one']:12.0f}%  {row['we lose one']:10.0f}%  {row['net NPCs']:+8.2f}  {row['flags']:+6.2f}  {row['win points 90']:+10.1f}  {row['win points 180']:+11.1f}"
       + ("   (under the floor)" if len(V) < MIN_PLAYS or row["matches"] < MIN_MATCHES else ""))


def _fell_head(extra=()):
    return (f"     {'':52} {'cases':>5}  {'started at':>10}  {'60 s before':>11}  " + "  ".join(f"{name:>{w}}" for name, w in extra)
            + f"  {'they lose one':>13}  {'we lose one':>11}  {'net NPCs':>8}  {'flags':>6}  {'win pts 90':>10}  {'win pts 180':>11}")


PUSH_WHO = ("one player", "two or more players", "the main team")
PUSH_ON = ("carrying", "going back", "at the stand")


def push_cases(D, M, B):
    """One case a push on a flagger, from the side of the team that pushes: who pushes (R-573), where the flagger was, whether his team sent help, and what
    became of the flag; the hard results over the whole map on the fixed record with their price. Shadow of Haste runs are set aside (R-456)."""
    out, skipped = [], collections.Counter()
    other = {(p["rid"], p["t0"], p["t1"]): p for p in D["plays"] if p["play"] == "flagger pushed"}
    for p in D["plays"]:
        if p["play"] != "push flagger": continue
        if p.get("soh"): skipped["a Shadow of Haste run (R-456)"] += 1; continue
        c = _told(p, M, B)
        if c is None: skipped["no winner recorded, or the flag lead not read"] += 1; continue
        q, b = other.get((p["rid"], p["t0"], p["t1"])), p["beside"]
        on = next((w for w in PUSH_ON if f", {w}" in p["scenario"]), None) or ("at the stand" if "at th" in p["scenario"] else "other")
        c.update(who="the main team" if p["main"] else "one player" if p["pushers"] == 1 else "two or more players", pushers=p["pushers"], on=on, helped=bool(q and q.get("helped")),
                 stopped=bool(p["any_of"].get("their flag is stopped")), flag_in=b["flag"] == "captured", late=b["against_usual"], carrier_died=bool(b["carrier_died"]), lasted=p["t1"] - p["t0"], met=bool(p["met"]))
        out.append(c)
    return out, skipped


def pushes(path, out_json=None):
    """Pushing the flagger (R-371, R-573), stage 1: do the readings go with what any player knows, and what followed each push, as it fell. A report: it
    advises nothing. From the side of the team that pushes; the flagger's team is the same rows read the other way."""
    D, M = load(path); B, P = prices(D, M)
    C, skipped = push_cases(D, M, B)
    lines, res = [], {"cases": len(C), "skipped": dict(skipped), "counts": {}, "checks": {}, "as_it_fell": {}}
    pr = lambda x="": (lines.append(x), print(x))
    pr(f"Pushing the flagger (R-573), stage 1, on {len(M)} matches: {len(C)} pushes in {len({c['rid'] for c in C})} matches, each read from the side of the team that pushes"
       + "".join(f"; set aside, {k}: {v}" for k, v in skipped.most_common() if v))
    pr("\nA. How many, by who pushes and where the flagger was")
    for w in PUSH_WHO:
        X = [c for c in C if c["who"] == w]; res["counts"][w] = {"pushes": len(X), "matches": len({c["rid"] for c in X}), "on": {o: sum(1 for c in X if c["on"] == o) for o in PUSH_ON + ("other",)}}
        pr(f"   {w:20} {len(X):4} in {len({c['rid'] for c in X}):3} matches; the flagger " + ", ".join(f"{o} {sum(1 for c in X if c['on'] == o)}" for o in PUSH_ON + ("other",) if any(c["on"] == o for c in X))
           + f"; lasted (middle) {np.median([c['lasted'] for c in X]) if X else 0:.0f} s; his team sent help in {100 * np.mean([c['helped'] for c in X]) if X else 0:.0f}%")
    K = [c for c in C if c["on"] == "carrying"]
    pr(f"\nB. The readings, on pushes of a flagger carrying his flag ({len(K)}). Stopped = the flag does not get in on that run.")
    rd = lambda *a, **k: _reading(pr, res, K, *a, **k)
    rd("U1 two or more players stop the flag more often than one", lambda c: c["who"] == "two or more players", lambda c: c["who"] == "one player", +1, lambda c: c["stopped"], "two or more", "one player")
    rd("U2 the main team stops the flag more often than players sent for him", lambda c: c["who"] == "the main team", lambda c: c["who"] != "the main team", +1, lambda c: c["stopped"], "the main team", "players")
    rd("U3 a flagger who dies under the push: the flag is stopped more often", lambda c: c["carrier_died"], lambda c: not c["carrier_died"], +1, lambda c: c["stopped"], "he dies", "he lives")
    L = [c for c in K if c["flag_in"] and c["late"] is not None]
    _reading(pr, res, L, "U4 a flag that still gets in is later against two or more than against one", lambda c: c["who"] != "one player", lambda c: c["who"] == "one player", +1, lambda c: c["late"], "two or more, or the main team", "one player", unit=" x the usual run")
    rd("U5 a push that stops the flag leaves the pushers better off in flags 90 s on", lambda c: c["stopped"], lambda c: not c["stopped"], +1, lambda c: c["hard"]["90"]["lead_change"] or 0.0, "stopped", "got in", unit=" flags")
    pr("   Not a reading: help sent. A team sends help to the pushes that need it, so help marks the push (SPEC 5, rule 4); it is shown below as it fell and never as a cause.")
    extra = (("flag stopped", lambda V: 100 * float(np.mean([c["stopped"] for c in V])), lambda v: f"{v:11.0f}%"), ("he dies", lambda V: 100 * float(np.mean([c["carrier_died"] for c in V])), lambda v: f"{v:6.0f}%"),
             ("late (middle)", lambda V: float(np.median([c["late"] for c in V if c["late"] is not None] or [0])), lambda v: f"{v:12.2f}x"))
    head = _fell_head((("flag stopped", 12), ("he dies", 7), ("late (middle)", 13)))
    pr("\nC. As it fell, from the pushers' side, 90 s on (win points also 180 s on): a description set against no like spot; who pushes follows the spot")
    pr("   started at = the pushers' chance of winning when the push is told; 60 s before = what the minute before had done to it; late = arrival against the hall's usual run, flags that got in;")
    pr("   they lose one, we lose one = a death anywhere on the map; flags = change in the pushers' flag lead.")
    for on in PUSH_ON:
        X = [c for c in C if c["on"] == on]
        if not X: continue
        pr(f"\n   The flagger {on} ({len(X)})"); pr(head); o = res["as_it_fell"][on] = {}
        for w in PUSH_WHO:
            _fell(pr, o, w, [c for c in X if c["who"] == w], extra)
            for hl, hv in (("his team sends help", True), ("no help", False)): _fell(pr, o, f"  {w}, {hl}", [c for c in X if c["who"] == w and c["helped"] == hv], extra)
    # D. The solo push (R-588, his suspicion: "a one player push just isn't that effective at stopping a flag ... maybe that player could be better used doing
    # something else to gain flag advantage (e.g. double running or helping get our own flag in quick)"). Read on their runs, from the flag plays: who pushed
    # their flagger while he carried, and whether the team that pushed sent a runner of its own. A team ahead in flags loses lead as their flag gets in whatever
    # it does, so each row is also set level on the lead held when their runner set off (a straight line fitted over all the rows).
    R = their_runs(D)
    pr(f"\nD. Their run, by who pushed their flagger and whether the pushing team ran a flag of its own ({len(R)} runs; the opening and runs answered from our own cap left out)")
    pr("   level = change in our flag lead 90 s on, less what the lead we held when their runner set off gives on its own; in brackets its 90% range over whole matches.")
    res["their_runs"] = o = {}
    for w in ("no push",) + PUSH_WHO:
        for ours in ("no runner of ours", "a runner of ours"):
            X = [r for r in R if r["who"] == w and r["ours"] == ours]
            if len(X) < 15: continue
            bs = _one_range(X, "level")
            o[f"{w}, {ours}"] = {"runs": len(X), "matches": len({r["rid"] for r in X}), "their flag gets in": 100 * float(np.mean([r["their_in"] for r in X])), "flags": float(np.mean([r["lc"] for r in X])),
                                 "level": float(np.mean([r["level"] for r in X])), "range": bs}
            pr(f"   {w:20} {ours:18} {len(X):4} in {len({r['rid'] for r in X}):3} matches; their flag gets in {100 * np.mean([r['their_in'] for r in X]):3.0f}%; flags 90 s on {np.mean([r['lc'] for r in X]):+.2f}; level {np.mean([r['level'] for r in X]):+.2f} ({bs[0]:+.2f} to {bs[1]:+.2f})")
    N = [r for r in R if r["ours"] == "no runner of ours"]
    _reading(pr, res, N, "U6 with no runner of ours sent, one player pushing gets their flag stopped more often than nobody pushing", lambda r: r["who"] == "one player", lambda r: r["who"] == "no push", +1, lambda r: not r["their_in"], "one player", "no push")
    _reading(pr, res, N, "U7 with no runner of ours sent, two or more pushing get their flag stopped more often than one", lambda r: r["who"] == "two or more players", lambda r: r["who"] == "one player", +1, lambda r: not r["their_in"], "two or more", "one player")
    _reading(pr, res, [r for r in R if r["who"] == "one player"], "U8 a team pushing with one player is better off in flags (level) where it also sends a runner of its own", lambda r: r["ours"] == "a runner of ours", lambda r: r["ours"] == "no runner of ours", +1, lambda r: r["level"], "a runner sent", "none sent", unit=" flags")
    _reading(pr, res, N, "U9 with no runner of ours sent, one player pushing leaves us better off in flags (level) than nobody pushing", lambda r: r["who"] == "one player", lambda r: r["who"] == "no push", +1, lambda r: r["level"], "one player", "no push", unit=" flags")
    pr("   Read with care: who pushes and who runs follow the spot. These rows are where to look, never advice.")
    # E. His five questions (R-591, 2026-11-22: "The real question if a team is pushing is: does that actually create a flag advantage? Does it result in more
    # kills? More NPCs? Are you more vulnerable to split? Do you take more deaths on your own team?"). Read on their runs, the 90 s from their runner's set-off,
    # a push against no push; kills and our own deaths are also read in the 60 s before, which no push can change: a gap that was already there marks the spot.
    pr(f"\nE. His five questions, on the same runs: the 90 s from their runner's set-off, by who pushed their flagger")
    pr(f"     {'':22} {'runs':>5}  {'flags (level)':>13}  {'kills':>6}  {'60 s before':>11}  {'own deaths':>10}  {'60 s before':>11}  {'NPCs taken':>10}  {'NPCs lost':>9}  {'they split on us':>16}  {'main fight down, s':>18}")
    res["five"] = o = {}
    mn = lambda X, k: float(np.mean([r[k] for r in X if r[k] is not None] or [0.0]))
    for w in ("no push",) + PUSH_WHO:
        X = [r for r in R if r["who"] == w]
        if len(X) < 15: continue
        o[w] = {"runs": len(X), "matches": len({r["rid"] for r in X}), "flags (level)": mn(X, "level"), "kills": mn(X, "kills"), "kills, 60 s before": mn(X, "kills_before"), "own deaths": mn(X, "deaths"), "own deaths, 60 s before": mn(X, "deaths_before"),
                "NPCs taken": mn(X, "npcs"), "NPCs lost": mn(X, "npcs_lost"), "they split on us": 100 * mn(X, "their_split"), "main fight down, s": mn(X, "down_s")}
        v = o[w]
        pr(f"     {w:22} {len(X):5}  {v['flags (level)']:+13.2f}  {v['kills']:6.2f}  {v['kills, 60 s before']:11.2f}  {v['own deaths']:10.2f}  {v['own deaths, 60 s before']:11.2f}  {v['NPCs taken']:10.2f}  {v['NPCs lost']:9.2f}  {v['they split on us']:15.0f}%  {v['main fight down, s']:18.1f}")
    psh, non = (lambda r: r["who"] in PUSH_WHO[:2]), (lambda r: r["who"] == "no push")
    Q = [r for r in R if r["who"] != PUSH_WHO[2]]                          # players sent for him against nobody; the main team walking onto him is the main fight moving (R-401)
    pr("   Players sent for him (one, or two or more) against nobody pushing; the main team moving onto him is left out of these (it is the main fight moving, R-401):")
    _reading(pr, res, Q, "U10 a push leaves the pushing team better off in flags 90 s on (level)", psh, non, +1, lambda r: r["level"], "a push", "no push", unit=" flags")
    _reading(pr, res, Q, "U11 a push brings more kills in the 90 s", psh, non, +1, lambda r: r["kills"], "a push", "no push", unit=" kills")
    _reading(pr, res, [r for r in Q if r["kills_before"] is not None], "U11b ... and the same teams were already killing more in the 60 s before (if so, the kills mark the spot)", psh, non, +1, lambda r: r["kills_before"], "a push", "no push", unit=" kills")
    _reading(pr, res, Q, "U12 a push brings more NPCs in the 90 s", psh, non, +1, lambda r: r["npcs"], "a push", "no push", unit=" NPCs")
    _reading(pr, res, Q, "U13 a team that pushes is split on more often in the 90 s", psh, non, +1, lambda r: r["their_split"], "a push", "no push")
    _reading(pr, res, Q, "U13b ... and loses more NPCs", psh, non, +1, lambda r: r["npcs_lost"], "a push", "no push", unit=" NPCs")
    _reading(pr, res, Q, "U14 a team that pushes takes more deaths of its own in the 90 s", psh, non, +1, lambda r: r["deaths"], "a push", "no push", unit=" deaths")
    _reading(pr, res, [r for r in Q if r["deaths_before"] is not None], "U14b ... and was already taking more in the 60 s before", psh, non, +1, lambda r: r["deaths_before"], "a push", "no push", unit=" deaths")
    _reading(pr, res, [r for r in Q if r["down_s"] is not None], "U15 a team that pushes has its main fight a player down for longer in the 90 s", psh, non, +1, lambda r: r["down_s"], "a push", "no push", unit=" s")
    pr("   A reading that holds here is where to look, never advice: a team pushes where it can afford to.")
    pr("   No family (R-597, his word on these figures): the one gain, two or more players stopping a flag, is the flag family's already. The readings stay as a report.")
    if out_json: json.dump(res, open(out_json, "w"), indent=1, default=float)
    return res


def _one_range(X, key, n=400):
    """The 90% range of a mean over whole matches."""
    by = collections.defaultdict(list)
    for x in X: by[x["rid"]].append(x[key])
    ids, rng = sorted(by), np.random.default_rng(7)
    bs = [float(np.mean([v for i in rng.choice(len(ids), len(ids)) for v in by[ids[i]]])) for _ in range(n)]
    return [float(np.percentile(bs, 5)), float(np.percentile(bs, 95))]


def their_runs(D):
    """One row a run of theirs told as a flag play (the opening, runs answered from our own cap and Shadow of Haste runs left out), from the side of the team
    it is run against: who of ours pushed their flagger while he carried (R-573), whether we sent a runner of our own, whether their flag got in, and the
    change in our flag lead 90 s on, also set level on the lead we held when their runner set off."""
    push, rows, split = collections.defaultdict(list), [], collections.defaultdict(list)
    for p in D["plays"]:
        if p["play"] == "push flagger" and not p.get("soh") and "carrying" in p["scenario"]: push[(p["rid"], p["tm"])].append(p)
        if p["play"] == "split" and p["side"] == "attacker" and (p.get("split") or {}).get("told") == p["t0"]: split[(p["rid"], p["tm"])].append(p)      # a split, once, at the second it is told
    for f in D["plays"]:
        if f["play"] != "flag" or f.get("soh") or not f.get("clock") or not f.get("after"): continue
        c = f["clock"]
        if c.get("from_cap") or f["scenario"].startswith("The opening") or c.get("their_off") is None: continue
        a, b = c["their_off"], (c.get("their_end") or c["their_off"] + 60)
        ov = [q for q in push[(f["rid"], f["tm"])] if q["t0"] <= b and q["t1"] >= a]
        h = f["after"].get("90") or {}
        if h.get("lead_change") is None or f["state"].get("flag_lead") is None: continue
        bf = (f.get("before") or {}).get("after") or {}
        sp = lambda tm: any(q["t0"] > a and q["t0"] <= a + 90 for q in split[(f["rid"], tm)])
        rows.append({"rid": f["rid"], "team": f["team"], "t": a, "who": "no push" if not ov else PUSH_WHO[2] if any(q["main"] for q in ov) else PUSH_WHO[0] if max(q["pushers"] for q in ov) == 1 else PUSH_WHO[1],
                     "ours": "a runner of ours" if "run" in f["ours"] else "no runner of ours", "form": f["ours"], "lc": h["lead_change"], "lead0": f["state"]["flag_lead"], "their_in": f["beside"].get("their_flag") == "captured",
                     # his five questions (R-591): kills, NPCs, deaths of our own and a split against us in the 90 s from their runner's set-off, and the same kills and deaths in the 60 s before it
                     "kills": h["deaths"][1], "deaths": h["deaths"][0], "npcs": h["npcs"][1], "npcs_lost": h["npcs"][0], "their_split": sp(3 - f["tm"]), "our_split": sp(f["tm"]),
                     "kills_before": bf["deaths"][1] if bf.get("deaths") else None, "deaths_before": bf["deaths"][0] if bf.get("deaths") else None,
                     "down_s": (h.get("numbers") or {}).get("main_down_s"), "up_s": (h.get("numbers") or {}).get("main_up_s")})
    k = np.polyfit([r["lead0"] for r in rows], [r["lc"] for r in rows], 1)
    for r in rows: r["level"] = r["lc"] - (k[0] * r["lead0"] + k[1])
    return rows


HELD_ENDS = ("it breaks out", "held to the base res", "the hold ends otherwise")
HELD_NUMBERS = ("level or up in players", "a player down", "two or more down")


def held_cases(D, M, B):
    """One case a team held in its own base or pit by the enemy's main team (the `pinned` plays), from its own side: how long, how it ended, what it lost
    while held, the players alive on each side and the base res when it began; the hard results over the whole map on the fixed record with their price."""
    out, skipped = [], collections.Counter()
    for p in D["plays"]:
        if p["play"] != "pinned": continue
        c = _told(p, M, B)
        if c is None: skipped["no winner recorded, or the flag lead not read"] += 1; continue
        st, b = c["state"], p["beside"]
        down = st["alive"][1] - st["alive"][0]
        res_in, s_ = st["res_in"], b["pinned_s"]
        c.update(held_s=s_, broke_out=bool(p["broke_out"]), npc_lost=b["pit_npcs_lost"], died=b["deaths"][0], killed=b["deaths"][1], res_in=res_in, down=down, met=bool(p["met"]),
                 numbers=HELD_NUMBERS[0] if down <= 0 else HELD_NUMBERS[1] if down == 1 else HELD_NUMBERS[2],
                 end=HELD_ENDS[0] if p["broke_out"] else HELD_ENDS[1] if res_in is not None and abs(s_ - res_in) <= 12 else HELD_ENDS[2])
        out.append(c)
    return out, skipped


def held(path, out_json=None):
    """A team held in its base (R-506, R-478), stage 1: do the readings go with what any player knows, and what followed, as it fell. A report: it advises
    nothing. From the side of the team held in."""
    D, M = load(path); B, P = prices(D, M)
    C, skipped = held_cases(D, M, B)
    lines, res = [], {"cases": len(C), "skipped": dict(skipped), "counts": {}, "checks": {}, "as_it_fell": {}}
    pr = lambda x="": (lines.append(x), print(x))
    pr(f"A team held in its own base or pit by the enemy's main team, stage 1, on {len(M)} matches: {len(C)} holds in {len({c['rid'] for c in C})} matches, each read from the side of the team held in"
       + "".join(f"; set aside, {k}: {v}" for k, v in skipped.most_common() if v))
    pr("\nA. How many, by how the hold ended and the players alive when it began")
    for e in HELD_ENDS:
        X = [c for c in C if c["end"] == e]; res["counts"][e] = {"holds": len(X), "matches": len({c["rid"] for c in X})}
        pr(f"   {e:26} {len(X):4} in {len({c['rid'] for c in X}):3} matches; held (middle) {np.median([c['held_s'] for c in X]) if X else 0:3.0f} s; " + ", ".join(f"{n} {sum(1 for c in X if c['numbers'] == n)}" for n in HELD_NUMBERS))
    pr(f"\nB. The readings ({len(C)} holds). A pit NPC = a knight, a pit archer or the Bodyguard lost while the team is held.")
    rd = lambda *a, **k: _reading(pr, res, C, *a, **k)
    rd("H1 held 60 s or longer, a pit NPC is lost more often than held under 30 s", lambda c: c["held_s"] >= 60, lambda c: c["held_s"] < 30, +1, lambda c: c["npc_lost"] > 0, "60 s or longer", "under 30 s")
    rd("H2 held a player or more down, a pit NPC is lost more often than level or up", lambda c: c["down"] >= 1, lambda c: c["down"] <= 0, +1, lambda c: c["npc_lost"] > 0, "a player or more down", "level or up")
    rd("H3 held two or more down, a player dies more often than level or up", lambda c: c["down"] >= 2, lambda c: c["down"] <= 0, +1, lambda c: c["died"] > 0, "two or more down", "level or up")
    R_ = [c for c in C if c["res_in"] is not None]
    _reading(pr, res, R_, "H4 the base res near when the hold begins, the hold is shorter than with the res far", lambda c: c["res_in"] <= 30, lambda c: c["res_in"] >= 60, -1, lambda c: c["held_s"], "base res within 30 s", "60 s or more away", unit=" s")
    _reading(pr, res, R_, "H5 the base res near, a pit NPC is lost less often than with the res far", lambda c: c["res_in"] <= 30, lambda c: c["res_in"] >= 60, -1, lambda c: c["npc_lost"] > 0, "base res within 30 s", "60 s or more away")
    pr("   Not a reading: the break-out. Which teams break out follows the spot (a team that can, does), so it marks the hold; it is shown below as it fell. A team that breaks out and")
    pr("   loses a player or a pit NPC on the way has not met its job (R-478).")
    extra = (("held s (mid)", lambda V: float(np.median([c["held_s"] for c in V])), lambda v: f"{v:12.0f}"), ("pit NPC lost", lambda V: 100 * float(np.mean([c["npc_lost"] > 0 for c in V])), lambda v: f"{v:11.0f}%"),
             ("a player dies", lambda V: 100 * float(np.mean([c["died"] > 0 for c in V])), lambda v: f"{v:12.0f}%"), ("job met", lambda V: 100 * float(np.mean([c["met"] for c in V])), lambda v: f"{v:6.0f}%"))
    head = _fell_head((("held s (mid)", 12), ("pit NPC lost", 12), ("a player dies", 13), ("job met", 7)))
    pr("\nC. As it fell, from the side of the team held in, 90 s on (win points also 180 s on): a description set against no like spot; how a hold ends follows the spot")
    pr("   started at = its chance of winning when the hold begins; 60 s before = what the minute before had done to it; pit NPC lost, a player dies = while held;")
    pr("   they lose one, we lose one = a death anywhere on the map in the 90 s; net NPCs = theirs lost less ours.")
    for n in HELD_NUMBERS:
        X = [c for c in C if c["numbers"] == n]
        if not X: continue
        pr(f"\n   Held in, {n} ({len(X)})"); pr(head); o = res["as_it_fell"][n] = {}
        for e in HELD_ENDS: _fell(pr, o, e, [c for c in X if c["end"] == e], extra)
    if out_json: json.dump(res, open(out_json, "w"), indent=1, default=float)
    return res


RES_CALLS = ("stayed through the res", "left before the res")
RES_LOW = 85                                     # the players in their base are low on health between them under this (the report's own band, Claude's draft: no play reads it)
RES_BACK = ("one coming back", "two coming back", "three or more coming back")


def res_cases(D, M, B):
    """One case a team in the enemy's base at their base res, from its own side: whether it stayed through the res or left before it, how many of theirs
    came back, whether it was then outnumbered, and who died of it; the hard results over the whole map on the fixed record with their price."""
    out, skipped = [], collections.Counter()
    for p in D["plays"]:
        if p["play"] != "base res": continue
        if "res" not in p: raise ValueError(f"base res play {p['id']} carries no record: run moments.py all again on this engine (R-460)")
        c = _told(p, M, B)
        if c is None: skipped["no winner recorded, or the flag lead not read"] += 1; continue
        r, b = p["res"], p["beside"]
        n = r["coming_back"]
        c.update(call=p["call"], back=n, back_band=RES_BACK[0] if n <= 1 else RES_BACK[1] if n == 2 else RES_BACK[2], attackers=r.get("attackers"), defenders=r.get("defenders"),
                 outnumbered=r.get("outnumbered"), died=b["deaths_after"] > 0, deaths=b["deaths_after"], met=bool(p["met"]),
                 health=r.get("health"), low=r.get("low"), inside=r.get("inside"), pit_npcs=r.get("pit_npcs"))
        if p["call"] == RES_CALLS[0] and "health" not in r: raise ValueError(f"base res play {p['id']} carries no health: run moments.py all again on this engine (R-460)")
        if "early" not in r: raise ValueError(f"base res play {p['id']} carries no reading before the res: run moments.py all again on this engine (R-460)")
        e = r["early"]; mid = lambda v: None if not v else float(np.median(v))
        if "danger" not in e: raise ValueError(f"base res play {p['id']} carries no reading of the danger spot: run moments.py all again on this engine (R-460)")
        st, mo, m = p["at_told"]["state"], p["at_told"]["after"]["60"]["morale"], M[p["rid"]]
        c.update(early=e, at_res=r.get("at_res"), in_s=r.get("in_s"), deaths_60=r.get("deaths_60"), n=e["n"], e_health=e["health"], shrine=mid(e.get("shrine_walk")), past=e.get("past_shrine"),
                 npc_on=e["npc_on"], npc_dmg=e["npc_dmg"], taken=e["taken"], main=bool(e["n"]) and e["of_main"] * 2 > e["n"], stayed=p["call"] == RES_CALLS[0],
                 marks=e["marks"], nmarks=sum(e["marks"]), danger=bool(e["danger"]), two_60=(r.get("deaths_60") or 0) >= 2, kills=c["hard"]["90"]["deaths"][1], npcs=c["hard"]["90"]["npcs"][1],
                 own_morale=mo[0][0], their_morale=mo[1][0], dm=mo[0][0] - mo[1][0], stand=st["stand"] == "own", their_alive=e["alive"][1], monks=e.get("monks") or 0, late=p["t0"] + RES_READ >= 720,
                 gap=m["gap"][p["team"]], fold=m["fold"], won=float(m["winner"] == p["team"]), chance=100 * c["p0"], more=None, held=False)
        if c["danger"] != (p.get("clear") is not False): raise ValueError(f"base res play {p['id']}: the danger spot and the call disagree: run moments.py all again on this engine (R-460)")
        if c["danger"]:                                                        # his factors (R-613, R-616), read in the engine (`jobs.res_factors`)
            if "factors" not in r: raise ValueError(f"base res play {p['id']} in the danger spot carries no factors: run moments.py all again on this engine (R-460)")
            f_ = r["factors"]; c.update(factors=f_, behind=bool(f_["morale_behind"]), stand=bool(f_["stand"]), late=bool(f_["late"]), against=f_["against"], dm=f_["morale"])
        # the price of a death at this position, as the price of a position reads it (prices that never saw this match): one more death on our side is 15 of
        # death penalty on one player, a kill the same on theirs, a pit NPC one more of theirs lost
        x0 = position(st, p["at_told"]["after"]["90"], c["gap"], False); beta = B[m["fold"]]
        bump = lambda i, d_: 100 * (chance(beta, [v + (d_ if j == i else 0) for j, v in enumerate(x0)]) - c["p0"])
        c.update(price={"one death": bump(2, -15), "two deaths": bump(2, -30), "a kill": bump(2, 15), "a pit NPC": bump(4, 1)})
        c["x"] = [c["chance"], c["gap"], c["their_morale"], c["own_morale"], e["health"] if e["health"] is not None else 90.0, c["their_alive"], float(n), float(bool(c["outnumbered"])), float(c["stand"]), float(c["late"]), float(c["monks"]), float(e["pit_npcs"])]
        out.append(c)
    return out, skipped


RES_READ = 20                                    # a base res play is told this long before the res (`jobs.RES_READ_S`): the danger spot is read then
GREEDY = ("deep (half of them or more past their res shrine)", "NPCs on them (two or more enemy NPCs hitting them in the 20 s before)", "worn (250 damage or more a player in the minute before, R-615)")      # the three factors of the danger spot (R-610), read in the engine (`jobs._res_stand`: `marks`, `danger`)
HIS_RES = (("3b7bfeac", 1440, "yM v hook 24:00", True), ("512d445f", 720, "Crew v One 12:00", True), ("33dab8e5", 360, "Men v BcS 6:00", True), ("19f38ea6", 600, "Book v hook 10:00", True),
           ("39e9d728", 480, "DUM v ohno 8:00", True), ("c19f13e3", 600, "Men v NwAy 10:00", True), ("328de049", 960, "Book v cope 16:00", False), ("5527465c", 360, "hook v Men 6:00", None))      # his words of 2026-11-22 on the stays where two or more died: the six that are the greedy stay, one that is a res onto a split, and hook v Men, left as it is read (R-595, R-607)
DANGER_VARS = ("own chance of winning at that second", "strength gap", "their morale", "our morale", "health of our players in their base", "their players alive", "their dead to come back", "outnumbered in their base once they res",
               "we hold the stand", "the res of 12:00 or later", "our monks in their base", "their pit NPCs alive")
# what a team in the danger spot can know before the res, for "why some die and some do not" (R-610): a number is read in thirds of the danger spot's own stays
DANGER_F = (("its chance of winning at that second", "chance", "%"), ("the strength gap", "gap", ""), ("their morale (summed over the eight; a death is 15 on one player)", "their_morale", ""),
            ("our morale", "own_morale", ""), ("morale, ours less theirs", "dm", ""), ("health of our players in their base", "e_health", "%"))
DANGER_B = (("their players alive", (("seven or eight", lambda c: c["their_alive"] >= 7), ("six or fewer", lambda c: c["their_alive"] <= 6))),
            ("their dead to come back", (("one", lambda c: c["back"] <= 1), ("two", lambda c: c["back"] == 2), ("three or more", lambda c: c["back"] >= 3))),
            ("once they res", (("we are outnumbered in their base", lambda c: bool(c["outnumbered"])), ("we are not", lambda c: not c["outnumbered"]))),
            ("the flag", (("we hold the stand", lambda c: c["stand"]), ("we do not", lambda c: not c["stand"]))),
            ("the clock (the Amulet of Protection, R-603)", (("the res of 10:00 or earlier", lambda c: not c["late"]), ("the res of 12:00 or later", lambda c: c["late"]))),
            ("our monks in their base", (("three", lambda c: c["monks"] >= 3), ("two or fewer", lambda c: c["monks"] <= 2))))


def spot_cases(D, M):
    """The base res spots read 40 s before the res (`jobs.res_spots`, R-601), main teams only: whether the team stood in the danger spot then (R-610) and
    whether it stayed through the res or fell out before it (R-605)."""
    out = []
    for rid, v in D["flag_cost"].items():
        if "res_spots" not in (v or {}): raise ValueError(f"match {rid} carries no base res spots: run moments.py all again on this engine (R-460)")
        for s in v["res_spots"]:
            e = s["stand"]
            if "danger" not in e: raise ValueError(f"match {rid}: a base res spot carries no reading of the danger spot: run moments.py all again on this engine (R-460)")
            if not (e["n"] >= 3 and e["of_main"] * 2 > e["n"]): continue
            left = s["n"] - s["deaths"][0]
            call = "stayed" if s["in_at_res"] and s["in_at_res"] * 2 >= left else "fell out" if not s["in_at_res"] and s["deaths"][0] * 2 < s["n"] else None
            if call: out.append({"rid": rid, "team": s["team"], "res": s["res"], "call": call, "danger": bool(e["danger"]), "left_s": None if s["left_at"] is None else s["res"] - s["left_at"]})
    return out


FACTORS = (("morale", "morale 30 or more under theirs (the eight summed)", "morale not behind", lambda c: c["behind"]),
           ("stand", "the stand not held", "the stand held", lambda c: not c["stand"]),
           ("clock", "the res of 12:00 or later (recorded, not counted: R-616)", "before 12:00", lambda c: c["late"]))      # the first two are the factors of the call (R-616: "morale and stand only"); the clock of R-613 is read beside them and counts for nothing


def his_factors(S, g, pr, mn, rng):
    """E. The call in the danger spot on his factors (R-613, R-616: the morale difference and whether the stand is held count; the 12:00 breakpoint is recorded
    and not counted): each beside the stays without it, then by how many of the two stand against the stay. No verdict (R-617)."""
    g["factors"] = o = {"each": {}, "against": {}, "checks": {}}
    pr(f"\nE. The call in the danger spot on his factors (R-613, R-616): the morale difference and whether the stand is held count against a stay; the 12:00 breakpoint is recorded beside them and not counted ({len(S)} stays).")
    pr("   No verdict is built from them (R-617): whether a stay in the danger spot is a mistake is not known, and falling out cannot be set beside it.")
    pr("   One dies = one of its players in their base, in the 30 s after the res; win pts = the change in its chance of winning 90 s and three minutes on from the reading (90% range over whole matches).")
    pr(f"     {'':52} {'stays':>5}  {'one dies':>16}  {'two or more within 60 s':>23}  {'kills':>5}  {'NPCs':>5}  {'win pts 90 s':>12}  {'win pts 180 s':>22}  {'started at':>10}")
    def row(label, V, into):
        if not V: return
        if len(V) < 8: pr(f"     {label:52} {len(V):5}  too few to read: " + ", ".join(f"{c['deaths_60']} die" for c in V)); into[label] = {"stays": len(V), "deaths_60": [c["deaths_60"] for c in V]}; return
        lo, hi = rng(V, lambda c: c["died"]); wl, wh = rng(V, lambda c: c["v"]["180"]); w = float(np.mean([c["v"]["180"] for c in V])); dies = 100 * mn(V, "died")
        into[label] = {"stays": len(V), "one dies": dies, "range": [100 * lo, 100 * hi], "two or more within 60 s": 100 * mn(V, "two_60"), "kills": mn(V, "kills"), "NPCs": mn(V, "npcs"), "win points 90": float(np.mean([c["v"]["90"] for c in V])), "win points": w, "win range": [wl, wh], "started at": mn(V, "chance")}
        pr(f"     {label:52} {len(V):5}  {f'{dies:3.0f}% ({100 * lo:.0f} to {100 * hi:.0f})':>16}  {100 * mn(V, 'two_60'):22.0f}%  {mn(V, 'kills'):5.2f}  {mn(V, 'npcs'):5.2f}  {np.mean([c['v']['90'] for c in V]):+12.1f}  {f'{w:+.1f} ({wl:+.1f} to {wh:+.1f})':>22}  {mn(V, 'chance'):9.0f}%")
    row("every stay in the danger spot", S, o["each"])
    for _, on, off, f in FACTORS:
        row(on, [c for c in S if f(c)], o["each"]); row("  " + off, [c for c in S if not f(c)], o["each"])
    pr("   By how many of the two (morale behind, the stand not held) stand against the stay:")
    for n_ in (0, 1, 2): row(("neither", "one", "both")[n_], [c for c in S if c["against"] == n_], o["against"])
    row("one or both", [c for c in S if c["against"] >= 1], o["against"])
    rd = lambda *a, **k: _reading(pr, o, S, *a, **k)
    pr("   The readings (his factors as he gave them; each a difference between two groups of the stays):")
    for i, (key, on, off, f) in enumerate(FACTORS):
        rd(f"E{2 * i + 1} with {on} a player dies of the res more often", f, lambda c: True, +1, lambda c: c["died"], on.split(" (")[0], off)
        rd(f"E{2 * i + 2} ... and the stay is worse off three minutes on", f, lambda c: True, -1, lambda c: c["v"]["180"], on.split(" (")[0], off, unit=" points")
    rd("E7 with morale behind or the stand not held a player dies of the res more often than with neither", lambda c: c["against"] >= 1, lambda c: True, +1, lambda c: c["died"], "one or both against", "neither")
    rd("E8 ... and two or more die within 60 s more often", lambda c: c["against"] >= 1, lambda c: True, +1, lambda c: c["two_60"], "one or both against", "neither")
    rd("E9 ... and the stay is worse off three minutes on", lambda c: c["against"] >= 1, lambda c: True, -1, lambda c: c["v"]["180"], "one or both against", "neither", unit=" points")
    rd("E10 with both against it the stay is worse off three minutes on than with one or neither", lambda c: c["against"] >= 2, lambda c: True, -1, lambda c: c["v"]["180"], "both against", "one or neither", unit=" points")


def death_cost(S, g, pr, mn, rng):
    """F. What a death costs a team in the danger spot, in its chance of winning: as it fell (the stays by how many of the players in their base died within
    60 s of the res), and as the price of a position reads one more death at the position the team stood in. With what a kill and a pit NPC are worth at the
    same position, so that the stay can be weighed."""
    g["death_cost"] = o = {"as_it_fell": {}, "price": {}}
    pr(f"\nF. What a death costs in the danger spot ({len(S)} stays), in the chance of winning.")
    pr("   1. As it fell: the stays by how many of the players in their base died within 60 s of the res. The change in the chance of winning is from the reading (20 s before the res) to 90 s and three minutes on;")
    pr("      won = the share of those matches the team went on to win.")
    pr(f"     {'':24} {'stays':>5}  {'started at':>10}  {'win pts 90 s':>12}  {'win pts 180 s':>22}  {'won':>5}  {'kills':>5}  {'NPCs':>5}")
    groups = (("nobody dies", lambda c: (c["deaths_60"] or 0) == 0), ("one dies", lambda c: c["deaths_60"] == 1), ("two or more die", lambda c: (c["deaths_60"] or 0) >= 2))
    for label, f in groups:
        V = [c for c in S if f(c)]
        if not V: continue
        wl, wh = rng(V, lambda c: c["v"]["180"]); w = float(np.mean([c["v"]["180"] for c in V]))
        o["as_it_fell"][label] = {"stays": len(V), "matches": len({c["rid"] for c in V}), "started at": mn(V, "chance"), "win points 90": float(np.mean([c["v"]["90"] for c in V])), "win points": w, "win range": [wl, wh], "won": 100 * mn(V, "won"), "kills": mn(V, "kills"), "NPCs": mn(V, "npcs")}
        pr(f"     {label:24} {len(V):5}  {mn(V, 'chance'):9.0f}%  {np.mean([c['v']['90'] for c in V]):+12.1f}  {f'{w:+.1f} ({wl:+.1f} to {wh:+.1f})':>22}  {100 * mn(V, 'won'):4.0f}%  {mn(V, 'kills'):5.2f}  {mn(V, 'npcs'):5.2f}" + ("   (under the floor)" if len(V) < MIN_PLAYS else ""))
    for name, f, h in (("one death against none", groups[1][1], "180"), ("two or more against none", groups[2][1], "180"), ("one or more against none", lambda c: (c["deaths_60"] or 0) >= 1, "180"), ("one or more against none, 90 s on", lambda c: (c["deaths_60"] or 0) >= 1, "90")):
        for c in S: c["_y"] = c["v"][h]
        d, lo, hi, na, nb = _num_range(S, f, groups[0][1])
        if d is None: continue
        o["as_it_fell"][name] = {"difference": float(d), "range": [float(lo), float(hi)], "n": [na, nb]}
        pr(f"     {name}: {d:+.1f} points ({lo:+.1f} to {hi:+.1f}), {na} stays against {nb}" + ("   (under the floor of 30: a size to look at, no more)" if na < MIN_PLAYS else ""))
    # set level on where the team started: a team far ahead has little left to gain, and the stays that take deaths start lower. Each stay with a death against
    # the stays without one, of other matches, that started within 10 points of it (20 where fewer than five do)
    none = [c for c in S if groups[0][1](c)]
    def level(c, h):
        for w in (10, 20, 100):
            V = [x["v"][h] for x in none if x["rid"] != c["rid"] and abs(x["chance"] - c["chance"]) <= w]
            if len(V) >= 5: return c["v"][h] - float(np.mean(V))
    pr("      Set level on where the team started (each stay with a death against the stays without one that started within 10 points of it, three minutes on):")
    for name, f in (("one death", groups[1][1]), ("two or more", groups[2][1]), ("one or more", lambda c: (c["deaths_60"] or 0) >= 1)):
        V = [dict(c, _l=level(c, "180")) for c in S if f(c)]; V = [c for c in V if c["_l"] is not None]
        if not V: continue
        lo, hi = _one_range(V, "_l")
        o["as_it_fell"][name + ", level"] = {"difference": float(np.mean([c["_l"] for c in V])), "range": [float(lo), float(hi)], "n": len(V), "started at": mn(V, "chance")}
        pr(f"     {name:12} {np.mean([c['_l'] for c in V]):+.1f} points ({lo:+.1f} to {hi:+.1f}), {len(V)} stays that started at {mn(V, 'chance'):.0f}%" + ("   (under the floor of 30: a size to look at, no more)" if len(V) < MIN_PLAYS else ""))
    pr("      These stays differ in more than the deaths (a team that loses two has usually lost the fight in their base as well), so the difference is what went with the deaths, not the deaths alone.")
    pr("   2. As the price of a position reads it: one more death on the team at the position it stood in 20 s before the res, everything else left as it was (the price is fitted on every position of every")
    pr("      match and never saw the stay's own match; a death is 15% of death penalty on one player, and the price takes in what usually goes with a death, the player gone until he is brought back):")
    for k in ("one death", "two deaths", "a kill", "a pit NPC"):
        v = [c["price"][k] for c in S]; lo, hi = (float(x) for x in np.percentile(v, [10, 90]))
        o["price"][k] = {"mean": float(np.mean(v)), "from": lo, "to": hi}
        pr(f"     {k:12} {np.mean(v):+5.1f} points (eight in ten of the stays between {lo:+.1f} and {hi:+.1f})")
    bands = (("its chance of winning under 50%", lambda c: c["chance"] < 50), ("50 to 75%", lambda c: 50 <= c["chance"] < 75), ("75 to 90%", lambda c: 75 <= c["chance"] < 90), ("90% or more", lambda c: c["chance"] >= 90))
    pr("      By where the team stood (a death costs most where the match is still open):")
    o["price"]["by_chance"] = {}
    for label, f in bands:
        V = [c for c in S if f(c)]
        if not V: continue
        o["price"]["by_chance"][label] = {"stays": len(V), **{k: float(np.mean([c["price"][k] for c in V])) for k in ("one death", "two deaths", "a kill", "a pit NPC")}}
        pr(f"     {label:32} {len(V):4} stays: one death {np.mean([c['price']['one death'] for c in V]):+5.1f}, two {np.mean([c['price']['two deaths'] for c in V]):+5.1f}, a kill {np.mean([c['price']['a kill'] for c in V]):+5.1f}, a pit NPC {np.mean([c['price']['a pit NPC'] for c in V]):+5.1f}")
    # the stay weighed at those prices: the kills it took in the 90 s against the players it lost (NPCs are counted beside it: the count takes in footmen, which are not priced)
    took = [c["kills"] * c["price"]["a kill"] for c in S]; lost = [c["hard"]["90"]["deaths"][0] * c["price"]["one death"] for c in S]
    o["weighed"] = {"kills": mn(S, "kills"), "kills worth": float(np.mean(took)), "own deaths": float(np.mean([c["hard"]["90"]["deaths"][0] for c in S])), "deaths cost": float(np.mean(lost)),
                    "npcs": mn(S, "npcs"), "own npcs": float(np.mean([c["hard"]["90"]["npcs"][0] for c in S]))}
    pr(f"   3. The stay weighed at those prices, over the 90 s from the reading and the whole map: the team takes {mn(S, 'kills'):.2f} kills ({np.mean(took):+.1f} points) and loses {o['weighed']['own deaths']:.2f} players ({np.mean(lost):+.1f} points);"
       f" it takes {mn(S, 'npcs'):.2f} NPCs and loses {o['weighed']['own npcs']:.2f} (footmen among them, which are not priced). A sum of prices, not a comparison with falling out, which almost nobody does.")


RES_BEHIND = 30                                  # `jobs.RES_MORALE_BEHIND`, his (R-616): the sentence says the morale difference as a factor from here


def res_sentence(r):
    """The sentence for one base res in the danger zone (R-617, his form: "team X had 70% win chance, but was in danger zone with significant factors against,
    took 2 deaths and lost -20 points"): where the team stood, what of his two factors stood against the stay (R-616), and what followed. It says what
    happened and gives no verdict: whether the stay was a mistake is not known, since almost nobody falls out."""
    foe = next((t for t in r["teams"] if t != r["team"]), "their")
    ag = [w for w, on in zip((f"morale {-r['morale']} under theirs", "the stand not held"), (r["morale"] <= -RES_BEHIND, not r["stand"])) if on]
    n, k, pts = r["deaths_60"] or 0, r["kills_90"], r["win_points_180"]
    lost = "took no deaths" if n == 0 else "took one death" if n == 1 else f"took {n} deaths"      # deaths, as he says it ("took 2 deaths"): a player brought back can die again inside the minute
    moved = f"{'gained' if pts > 0 else 'lost'} {abs(pts):.0f} point{'' if round(abs(pts)) == 1 else 's'} of its chance of winning" if abs(pts) >= 0.5 else "its chance of winning did not move"
    ch = round(r["started_at"]); had = f"had {'an' if ch in (8, 11, 18) or 80 <= ch <= 89 else 'a'} {ch}% chance of winning"
    spot = f"({r['past_shrine']} of {r['n']} past their res shrine, {r['npcs_hitting']} NPCs on them, {r['taken']} damage a player in the minute before)"
    if r["call"] != RES_CALLS[0]:
        return (f"{r['team']} {had} and left {foe}'s base before the base res of {cl(r['res'])}, out of the danger zone {spot}, with {', '.join(ag) if ag else 'nothing'} against a stay; "
                f"it {lost} in the minute after the res, got {k} kill{'' if k == 1 else 's'} in 90 s, and three minutes on {moved}.")
    return (f"{r['team']} {had} and stayed through {foe}'s base res of {cl(r['res'])} in the danger zone {spot}, with {', '.join(ag) if ag else 'nothing'} against the stay; "
            f"it {lost} within 60 s of the res, got {k} kill{'' if k == 1 else 's'} in 90 s, and three minutes on {moved}.")


def danger_calls(X, M, g, pr):
    """Every base res in the danger zone with its call, his two factors (R-616) and its sentence (R-617; R-614: "I would want to see the base res call just for
    every danger zone base res"): kept whole in the report's file; printed, those with a factor against the stay and those where two or more died."""
    rows = []
    for c in sorted(X, key=lambda c: (M[c["rid"]]["date"], c["rid"], c["t"])):
        m, f = M[c["rid"]], c["factors"]
        if f["morale_behind"] != (f["morale"] <= -RES_BEHIND): raise ValueError(f"base res {c['rid']} {c['t']}: the morale factor is read on another number than the sentence's: set RES_BEHIND to jobs.RES_MORALE_BEHIND (R-460)")
        r = {"rid": c["rid"], "date": m["date"], "teams": m["teams"], "map": m["map"], "length_s": m["length_s"], "team": c["team"], "res": f["res"], "call": RES_CALLS[0] if c["stayed"] else RES_CALLS[1], "n": c["n"], "past_shrine": c["past"], "npcs_hitting": c["early"]["npcs_hitting"], "taken": c["taken"],
             "morale": f["morale"], "stand": f["stand"], "late": f["late"], "against": f["against"], "deaths_30": c["deaths"], "deaths_60": c["deaths_60"], "kills_90": c["kills"], "npcs_90": c["npcs"], "started_at": c["chance"], "win_points_180": c["v"]["180"]}
        r["sentence"] = res_sentence(r); rows.append(r)
    g["calls"] = rows
    line = lambda r: f"     {r['date']} {' v '.join(r['teams'])}, {r['map']}, {cl(r['length_s'] or 0)} long: {r['sentence']}   https://gvg.report/report/{r['rid']}#map"
    pr(f"\nI. Every base res in the danger zone as a sentence (R-617): {len(rows)}, kept whole in the report's file (`danger.calls`). What happened and no verdict. Those with a factor against the stay (R-616):")
    for r in rows:
        if r["against"] >= 1: pr(line(r))
    pr("   Those with neither against it where two or more of the players in their base died within 60 s of the res:")
    for r in rows:
        if (r["deaths_60"] or 0) >= 2 and r["against"] == 0: pr(line(r))
    left = [r for r in rows if r["call"] != RES_CALLS[0] and r["against"] == 0]
    if left:
        pr("   Those that left before the res, with neither against a stay:")
        for r in left: pr(line(r))


def danger_report(D, M, C, res, pr):
    """The base res as a decision (R-592, R-609, R-610): only in the danger spot, his three factors read 20 s before the res for the main team. Where it is and
    how often; what the stay cost and brought; why some stays take deaths and some do not, by what the team can know before the res; and when the stay is the
    right call, from like spots among the stays with the test on matches the reading never saw. Nearly every team in the danger spot stays, so a stay is set
    against holding what the team had, not against falling out, which the matches do not hold."""
    G = [c for c in C if c["main"] and c["n"] >= 3]
    X = [c for c in G if c["danger"]]; S = [c for c in X if c["stayed"]]
    res["danger"] = g = {"main team in their base": len(G), "set aside (a res onto a split, or fewer than three)": len(C) - len(G), "spots": len(X), "matches": len({c["rid"] for c in X}), "stayed": len(S), "left": len(X) - len(S),
                         "by_marks": {}, "his_games": [], "why": {}, "checks": {}}
    mn = lambda V, k: float(np.mean([float(c[k]) for c in V if c[k] is not None] or [0.0]))
    def rng(V, f):
        for c in V: c["_b"] = float(f(c))
        return _one_range(V, "_b")
    pr(f"\nD. The danger spot (R-609, R-610): the main team in their base (three or more of it) 20 s before the res with all three of his factors on: " + "; ".join(GREEDY))
    pr(f"   Of {len(G)} times a main team is in their base at the res ({len(C) - len(G)} set aside: a res onto a split, or fewer than three): {len(X)} in the danger spot, in {len({c['rid'] for c in X})} of {len(M)} matches;")
    pr(f"   {len(S)} stayed through the res and {len(X) - len(S)} left before it. Only these are a decision and carry a call (R-609, R-612); every other base res is told as context, with no call.")
    pr("   By how many of the three a main team that stays carries (context):")
    for n_ in (0, 1, 2, 3):
        V = [c for c in G if c["stayed"] and c["nmarks"] == n_]
        if not V: continue
        g["by_marks"][str(n_)] = {"stays": len(V), "one dies": 100 * mn(V, "died"), "two or more within 60 s": 100 * mn(V, "two_60"), "started at": mn(V, "chance")}
        pr(f"     {('none', 'one', 'two', 'all three: the danger spot')[n_]:30} {len(V):4} stays; one of them dies in the 30 s after {100 * mn(V, 'died'):3.0f}%; two or more within 60 s {100 * mn(V, 'two_60'):3.0f}%; started at {mn(V, 'chance'):3.0f}%")
    if not S: return
    lo, hi = rng(S, lambda c: c["died"]); wl, wh = rng(S, lambda c: c["v"]["180"])
    g["stays"] = {"one dies": 100 * mn(S, "died"), "range": [100 * lo, 100 * hi], "two or more within 60 s": 100 * mn(S, "two_60"), "kills": mn(S, "kills"), "NPCs": mn(S, "npcs"), "win points": float(np.mean([c["v"]["180"] for c in S])), "win range": [wl, wh], "started at": mn(S, "chance")}
    pr(f"   The stays in the danger spot: one of the players in their base dies in the 30 s after the res in {100 * mn(S, 'died'):.0f}% ({100 * lo:.0f} to {100 * hi:.0f}), two or more within 60 s in {100 * mn(S, 'two_60'):.0f}%; in the 90 s from")
    pr(f"   the reading they take {mn(S, 'kills'):.2f} kills and {mn(S, 'npcs'):.2f} NPCs; their chance of winning, {mn(S, 'chance'):.0f}% at the reading, is {np.mean([c['v']['180'] for c in S]):+.1f} points three minutes on ({wl:+.1f} to {wh:+.1f}).")
    pr("   His games (the stays where two or more died that he looked at):")
    for rid8, t, name, his in HIS_RES:
        c = next((c for c in C if c["rid"].startswith(rid8) and c["stayed"] and c["t"] + RES_READ == t), None)
        if c is None: pr(f"     {name}: not told as a stay"); g["his_games"].append({"game": name, "found": False}); continue
        e = c["early"]
        g["his_games"].append({"game": name, "his": his, "danger": c["danger"], "main": bool(c["main"] and c["n"] >= 3), "marks": c["marks"], "n": e["n"], "of_main": e["of_main"], "past_shrine": e.get("past_shrine"), "npcs_hitting": e["npcs_hitting"],
                               "npc_dmg": e["npc_dmg"], "taken": e["taken"], "health": e["health"], "deaths": c["deaths"], "deaths_60": c["deaths_60"]})
        pr(f"     {name:20} his: {'the greedy stay' if his else 'left as it is read' if his is None else 'a res onto a split':18} engine: {'IN THE DANGER SPOT' if c['danger'] else 'not in it         '} ({', '.join(m.split(' (')[0] for m, v in zip(GREEDY, c['marks']) if v) or 'no factor'}"
           f"{'' if c['main'] and c['n'] >= 3 else '; not the main team'}); {e['n']} in their base, {e.get('past_shrine')} past the shrine, {e['npcs_hitting']} NPCs hitting them ({e['npc_dmg']} damage), {e['taken']} damage each in the minute, health {e['health']}%; {c['deaths']} die in 30 s, {c['deaths_60']} in 60 s")
    ok = [x for x in g["his_games"] if x.get("found", True) and x["his"] is not None]
    g["agrees"] = sum(1 for x in ok if x["danger"] == x["his"]); g["of"] = len(ok)
    pr(f"   The danger spot takes in {sum(1 for x in ok if x['his'] and x['danger'])} of his {sum(1 for x in ok if x['his'])} greedy stays and none of the stays he set aside.")
    his_factors(S, g, pr, mn, rng)
    death_cost(S, g, pr, mn, rng)
    # ---- G. why some die and some do not
    pr(f"\nG. Why some stays in the danger spot take deaths and some do not ({len(S)} stays), by what the team can know before the res. One dies = one of its players in their base, in the 30 s after the res;")
    pr("   win pts = the change in its chance of winning three minutes on, with the 90% range over whole matches. The three factors of the danger spot are on in every row, so they tell nothing apart here.")
    head = f"     {'':62} {'stays':>5}  {'one dies':>16}  {'two or more within 60 s':>23}  {'kills':>5}  {'NPCs':>5}  {'win pts':>22}  {'started at':>10}"
    pr(head)
    def row(label, V):
        if len(V) < 8: pr(f"     {label:62} {len(V):5}  too few"); g["why"][label] = {"stays": len(V)}; return
        lo, hi = rng(V, lambda c: c["died"]); wl, wh = rng(V, lambda c: c["v"]["180"]); w = float(np.mean([c["v"]["180"] for c in V])); dies = 100 * mn(V, "died")
        g["why"][label] = {"stays": len(V), "one dies": 100 * mn(V, "died"), "range": [100 * lo, 100 * hi], "two or more within 60 s": 100 * mn(V, "two_60"), "kills": mn(V, "kills"), "NPCs": mn(V, "npcs"), "win points": w, "win range": [wl, wh], "started at": mn(V, "chance")}
        pr(f"     {label:62} {len(V):5}  {f'{dies:3.0f}% ({100 * lo:.0f} to {100 * hi:.0f})':>16}  {100 * mn(V, 'two_60'):22.0f}%  {mn(V, 'kills'):5.2f}  {mn(V, 'npcs'):5.2f}  {f'{w:+.1f} ({wl:+.1f} to {wh:+.1f})':>22}  {mn(V, 'chance'):9.0f}%")
    row("every stay in the danger spot", S)
    thirds = {}
    for name, k, unit in DANGER_F:
        V = [c for c in S if c[k] is not None]
        if len(V) < 24: continue
        t1, t2 = (float(x) for x in np.percentile([c[k] for c in V], [100 / 3, 200 / 3])); thirds[k] = (t1, t2)
        row(f"{name}: the lowest third (under {t1:.0f}{unit})", [c for c in V if c[k] < t1]); row(f"  the middle third", [c for c in V if t1 <= c[k] < t2]); row(f"  the highest third ({t2:.0f}{unit} or more)", [c for c in V if c[k] >= t2])
    for name, bands in DANGER_B:
        for lab, f in bands: row(f"{name}: {lab}", [c for c in S if f(c)])
    g["thirds"] = {k: list(v) for k, v in thirds.items()}
    rd = lambda *a, **k: _reading(pr, g, S, *a, **k)
    pr("   The readings, each a difference between two groups of the stays with its 90% range over whole matches:")
    low = lambda k: (lambda c: c[k] is not None and c[k] < thirds[k][0]) if k in thirds else (lambda c: False)
    rd("D1 a team that is not far ahead (its chance of winning in the lowest third) loses a player to the res more often", low("chance"), lambda c: True, +1, lambda c: c["died"], "not far ahead", "the rest")
    rd("D2 ... and loses two or more within 60 s more often", low("chance"), lambda c: True, +1, lambda c: c["two_60"], "not far ahead", "the rest")
    rd("D3 with their morale in the highest third (an enemy that has not died much) two or more die more often", (lambda c: c["their_morale"] >= thirds["their_morale"][1]) if "their_morale" in thirds else (lambda c: False), lambda c: True, +1, lambda c: c["two_60"], "their morale high", "the rest")
    rd("D4 with morale no better than theirs by much (the difference in the lowest third) two or more die more often (R-606)", low("dm"), lambda c: True, +1, lambda c: c["two_60"], "small difference", "the rest")
    rd("D5 a team that will be outnumbered in their base once they res loses a player more often", lambda c: bool(c["outnumbered"]), lambda c: True, +1, lambda c: c["died"], "outnumbered", "not")
    rd("D6 a team low on health (the lowest third) is worse off three minutes on (R-602: \"already likely to die\")", low("e_health"), lambda c: True, -1, lambda c: c["v"]["180"], "low on health", "the rest", unit=" points")
    rd("D7 a team that does not hold the stand is worse off three minutes on", lambda c: not c["stand"], lambda c: True, -1, lambda c: c["v"]["180"], "no stand", "holds the stand", unit=" points")
    rd("D8 from the res of 12:00 on a stay is worse off three minutes on than before it (the Amulet of Protection, R-603)", lambda c: c["late"], lambda c: True, -1, lambda c: c["v"]["180"], "12:00 or later", "earlier", unit=" points")
    # ---- F. when the stay is the right call: like spots among the stays, and the test on unseen matches
    pr(f"\nH. When the stay is the right call: each stay in the danger spot read from the nearest stays of other groups of matches, set level with it. Matched on: " + ", ".join(DANGER_VARS))
    pr("   The reading is what staying was worth at like spots, in the chance of winning three minutes on, against holding what the team had: \"the stay pays\" where its 90% range lies above nothing, \"the stay")
    pr("   costs\" where it lies below, else no clear reading. Falling out cannot be set beside it: in the danger spot almost nobody does.")
    g["reading"] = o = {}
    if len(S) < 2 * MIN_PLAYS: pr(f"   Too few stays ({len(S)}) for like spots."); danger_calls(X, M, g, pr); return
    for c in S: c["call"] = "stayed"
    s_ = Scenario(S); s_.names = list(DANGER_VARS); K_ = MIN_PLAYS; o["K"] = K_
    pred = []
    for i in range(len(S)):
        j = s_.near(i, "stayed", K_, True)
        if len(j) < MIN_PLAYS or len(set(s_.rid[j].tolist())) < MIN_MATCHES: pred.append(None); continue
        mu, se, _, _ = s_.level(i, j, "stayed", "180"); pred.append((mu, mu - Z * se, mu + Z * se))
    R_ = [dict(c, pred=p_[0], read="the stay pays" if p_[1] > 0 else "the stay costs" if p_[2] < 0 else "no clear reading") for c, p_ in zip(S, pred) if p_ is not None]
    o["read"] = dict(collections.Counter(r["read"] for r in R_)); o["stays"] = len(R_)
    pr(f"   Of {len(R_)} stays, from the {K_} nearest: " + ", ".join(f"{k} {v}" for k, v in collections.Counter(r["read"] for r in R_).most_common()))
    pr(f"     {'':28} {'stays':>5}  {'one dies':>8}  {'two or more within 60 s':>23}  {'what the stay then did (win pts)':>32}  {'started at':>10}")
    for k in ("the stay pays", "no clear reading", "the stay costs"):
        V = [r for r in R_ if r["read"] == k]
        if not V: continue
        o[k] = {"stays": len(V), "one dies": 100 * mn(V, "died"), "two or more within 60 s": 100 * mn(V, "two_60"), "win points": float(np.mean([r["v"]["180"] for r in V])), "started at": mn(V, "chance")}
        pr(f"     {k:28} {len(V):5}  {100 * mn(V, 'died'):7.0f}%  {100 * mn(V, 'two_60'):22.0f}%  {np.mean([r['v']['180'] for r in V]):+32.1f}  {mn(V, 'chance'):9.0f}%")
    # the test: does the reading, made without a stay's own group of matches, tell the stays that went badly from those that went well?
    cut = float(np.percentile([r["pred"] for r in R_], 100 / 3)); o["worst_third_under"] = cut
    res_ = {"checks": g["checks"]}
    worst, rest = (lambda r: r["pred"] < cut), (lambda r: True)
    pr(f"   The test on matches the reading never saw: the third of the stays it reads worst (staying worth under {cut:+.1f} points at like spots) against the rest")
    _reading(pr, res_, R_, "T1 the stays read worst are worse off three minutes on", worst, rest, -1, lambda r: r["v"]["180"], "read worst", "the rest", unit=" points")
    _reading(pr, res_, R_, "T2 ... and lose a player to the res more often", worst, rest, +1, lambda r: r["died"], "read worst", "the rest")
    _reading(pr, res_, R_, "T3 ... and lose two or more within 60 s more often", worst, rest, +1, lambda r: r["two_60"], "read worst", "the rest")
    top = sorted(R_, key=lambda r: r["pred"])[:12]
    o["read_worst"] = [{"rid": r["rid"], "team": r["team"], "t": r["t"] + RES_READ, "worth": r["pred"], "deaths": r["deaths"], "deaths_60": r["deaths_60"], "then": r["v"]["180"]} for r in top]
    pr("   The stays read worst, to look at (what staying was worth at like spots; who died; what the stay then did):")
    for r in top:
        m = M[r["rid"]]
        pr(f"     {m['date']} {' v '.join(m['teams'])}, {m['map']}, {cl(m['length_s'] or 0)} long: {r['team']} at the res of {cl(r['t'] + RES_READ)}: read {r['pred']:+.1f}; {r['deaths']} die in 30 s, {r['deaths_60']} in 60 s; then {r['v']['180']:+.1f}   https://gvg.report/report/{r['rid']}#map")
    # ---- the same spot 40 s before the res: who falls out of it
    P = [c for c in spot_cases(D, M) if c["danger"]]
    o["at_40_s"] = {"stayed": sum(1 for c in P if c["call"] == "stayed"), "fell out": sum(1 for c in P if c["call"] == "fell out")}
    pr(f"\n   Falling out of the danger spot (read 40 s before the res, R-601, R-605): {o['at_40_s']['stayed']} stayed through the res and {o['at_40_s']['fell out']} fell out before it: too few to say what falling out is worth there.")
    danger_calls(X, M, g, pr)


def base_res(path, out_json=None):
    """The base res (R-359, R-377), stage 1: a team in the enemy's base when their dead come back. Do the readings go with what any player knows, and what
    followed staying and leaving, as it fell. A report: it advises nothing ("staying costs more deaths than leaving" is not one of his truths, R-534: it is
    shown as it fell and never as a reading)."""
    D, M = load(path); B, P = prices(D, M)
    C, skipped = res_cases(D, M, B)
    lines, res = [], {"cases": len(C), "skipped": dict(skipped), "counts": {}, "checks": {}, "as_it_fell": {}}
    pr = lambda x="": (lines.append(x), print(x))
    pr(f"The base res, stage 1, on {len(M)} matches: {len(C)} times a team is in the enemy's base at their base res, in {len({c['rid'] for c in C})} matches, each read from its own side"
       + "".join(f"; set aside, {k}: {v}" for k, v in skipped.most_common() if v))
    pr("\nA. How many, by what the team did and how many of theirs came back")
    for call in RES_CALLS:
        X = [c for c in C if c["call"] == call]; res["counts"][call] = {"cases": len(X), "matches": len({c["rid"] for c in X})}
        pr(f"   {call:24} {len(X):4} in {len({c['rid'] for c in X}):3} matches; " + ", ".join(f"{b} {sum(1 for c in X if c['back_band'] == b)}" for b in RES_BACK)
           + ("" if call != RES_CALLS[0] else f"; outnumbered after it {sum(1 for c in X if c['outnumbered'])}"))
    S = [c for c in C if c["call"] == RES_CALLS[0]]
    pr(f"\nB. The readings, on teams that stayed through the res ({len(S)}). Dies = a player of those in their base dies in the 30 s after the res.")
    rd = lambda *a, **k: _reading(pr, res, S, *a, **k)
    rd("B1 outnumbered after the res, a player dies more often than not outnumbered", lambda c: bool(c["outnumbered"]), lambda c: not c["outnumbered"], +1, lambda c: c["died"], "outnumbered", "not outnumbered")
    rd("B2 three or more coming back, a player dies more often than with one", lambda c: c["back"] >= 3, lambda c: c["back"] <= 1, +1, lambda c: c["died"], "three or more back", "one back")
    pr("   Not a reading: staying against leaving. Which teams leave follows the spot (a team that is losing the base leaves), and he took it off the known truths (R-534).")
    pr("   Not a reading either: how many come back. Three or more of theirs come back where three or more have just been killed, so it marks a team that is winning the base")
    pr("   (tried as a reading on 2026-11-22: net kills 90 s on ran +2.1 the other way).")
    # His picture of the danger (R-589): "the real danger is just dying to base res ... staying in range in a dangerous position when the enemy team bases so your
    # players are low on energy and health and you have NPCs on you, and the team base reses at pretty much full strength and kills your players". Health is in
    # the replay and energy is not; "in range" is read as right inside (the pit or the base, not at a door).
    H = [c for c in S if c["health"] is not None]
    rd = lambda *a, **k: _reading(pr, res, H, *a, **k)
    rd("B3 a team low on health as the res lands (its players in the base under 85% between them) loses a player more often", lambda c: c["health"] < RES_LOW, lambda c: c["health"] >= RES_LOW, +1, lambda c: c["died"], "low on health", "not low")
    rd("B4 the same team loses two or more more often", lambda c: c["health"] < RES_LOW, lambda c: c["health"] >= RES_LOW, +1, lambda c: c["deaths"] >= 2, "low on health", "not low")
    rd("B5 four or more right inside with four or more coming back, a player dies more often than otherwise", lambda c: c["inside"] >= 4 and c["back"] >= 4, lambda c: not (c["inside"] >= 4 and c["back"] >= 4), +1, lambda c: c["died"], "four inside, four back", "otherwise")
    rd("B6 with three or more pit NPCs alive a player dies more often than with two or fewer", lambda c: c["pit_npcs"] >= 3, lambda c: c["pit_npcs"] < 3, +1, lambda c: c["died"], "three or more NPCs", "two or fewer")
    pr(f"\n   The stays by how the players in the base stand as the res lands ({len(H)}): how often one of them dies in the 30 s after, and two or more")
    res["by_health"] = o = {}
    def hrow(label, X):
        if not X: return
        o[label] = {"cases": len(X), "matches": len({c["rid"] for c in X}), "one dies": 100 * float(np.mean([c["died"] for c in X])), "two or more die": 100 * float(np.mean([c["deaths"] >= 2 for c in X]))}
        pr(f"     {label:62} {len(X):4} in {len({c['rid'] for c in X}):3} matches; one dies {o[label]['one dies']:3.0f}%; two or more {o[label]['two or more die']:3.0f}%" + ("   (under the floor)" if len(X) < MIN_PLAYS else ""))
    hrow("every stay", H)
    for lo, hi in ((0, 70), (70, 85), (85, 95), (95, 101)): hrow(f"health between them {lo} to {min(hi, 100)}%", [c for c in H if lo <= c["health"] < hi])
    hrow("low on health, four or more right inside, four or more coming back", [c for c in H if c["health"] < RES_LOW and c["inside"] >= 4 and c["back"] >= 4])
    hrow("not low, four or more right inside, four or more coming back", [c for c in H if c["health"] >= RES_LOW and c["inside"] >= 4 and c["back"] >= 4])
    worst = sorted((c for c in H if c["deaths"] >= 2), key=lambda c: -c["deaths"])
    res["two_or_more_die"] = [{"rid": c["rid"], "team": c["team"], "t": c["t"] + 20, "deaths": c["deaths"], "health": c["health"], "inside": c["inside"], "back": c["back"], "pit_npcs": c["pit_npcs"]} for c in worst]
    pr(f"\n   The stays where two or more die of it ({len(worst)}), to look at:")
    for c in worst[:14]:
        pr(f"     {M[c['rid']]['date']} {' v '.join(M[c['rid']]['teams'])}, {M[c['rid']]['map']}: {c['team']} at the res of {cl(c['t'] + 20)}, {c['deaths']} die; health {c['health']}%, {c['inside']} right inside of {c['attackers']}, {c['back']} coming back, {c['pit_npcs']} pit NPCs alive   https://gvg.report/report/{c['rid']}#map")
    extra = (("one of them dies", lambda V: 100 * float(np.mean([c["died"] for c in V])), lambda v: f"{v:15.0f}%"), ("job met", lambda V: 100 * float(np.mean([c["met"] for c in V])), lambda v: f"{v:6.0f}%"))
    head = _fell_head((("one of them dies", 16), ("job met", 7)))
    pr("\nC. As it fell, from the side of the team in their base, 90 s on (win points also 180 s on): a description set against no like spot; who stays follows the spot")
    pr("   started at = its chance of winning 20 s before the res (stayed) or when it leaves; one of them dies = of the players in their base, in the 30 s after the res;")
    pr("   they lose one, we lose one = a death anywhere on the map in the 90 s; net NPCs = theirs lost less ours.")
    for b in RES_BACK:
        X = [c for c in C if c["back_band"] == b]
        if not X: continue
        pr(f"\n   {b[0].upper() + b[1:]} ({len(X)})"); pr(head); o = res["as_it_fell"][b] = {}
        _fell(pr, o, "stayed, not outnumbered after it", [c for c in X if c["call"] == RES_CALLS[0] and not c["outnumbered"]], extra)
        _fell(pr, o, "stayed, outnumbered after it", [c for c in X if c["call"] == RES_CALLS[0] and c["outnumbered"]], extra)
        _fell(pr, o, "left before the res", [c for c in X if c["call"] == RES_CALLS[1]], extra)
    danger_report(D, M, C, res, pr)
    if out_json: json.dump(res, open(out_json, "w"), indent=1, default=float)
    return res


OPEN_FLAG = ("brings its first flag up and caps it", "brings it up and holds it at the stand, then caps", "brings it up and does not cap it", "brings no flag and sends a player back for it", "brings no flag")
OPEN_MATCHUP = ("8 v 8", "8 v 7: they leave a player back", "7 v 8: we leave a player back", "7 v 7: each leaves a player back", "a split from the gates, either team", "other")
OPEN_SPLIT_BY = 180                              # a split "at the opening" for the report: told in the first three minutes
OPEN_LINES = ("frontline", "midline", "backline")
_stem = lambda role: re.sub(r"\s+(\d+|[AB])$", "", role)


RESP_MIN, RESP_SHARE = 5, 0.35                    # a guild has a usual split response where one player is sent to five or more splits and to 35% or more of those it answers (Claude's draft)
OPEN_EARLY_BY = 180                              # a player "sent back before a cap" turned for home inside the first three minutes


def usual_responder(D, monks=True):
    """Each guild's usual split response (R-590, his fourth point: "their usual split response character (e.g. a mes/a)"), as he defines it (R-593): "the
    player most often sent from the main team, leaving out the runner. It's usually Mes/A or Necro or Ele (or 8 monk as we know)". Measured, not named by
    build: over every stored match, the player the guild most often sends first to a split (one or two first defenders: a collapse or a team coming home
    names nobody), the players who ran that team's flags in the match left out (whoever ran most of them, and anyone who ran two in five or more). Monks
    count (the 8 Monk is one of his). A guild has one where that player was sent to RESP_MIN or more splits and RESP_SHARE or more of those counted.
    Returns {guild: player} and the counts behind it. `monks=False`: the same with the monks left out, the player other than a monk most often sent: by his
    definition the answer is the 8 Monk for nearly every guild, and his fourth point on the opening ("a flag on their usual split response character (e.g. a
    mes/a)") is about a player who can come up with the flag in hand; shown beside it until he says which he means."""
    runner, first, G = {}, {}, collections.defaultdict(collections.Counter)
    for p in D["plays"]:
        if p["play"] != "opening": continue
        if "runners" not in p.get("open", {}): raise ValueError(f"opening play {p['id']} carries no record of who ran the flags: run moments.py all again on this engine (R-460)")
        runs = collections.Counter()
        for r, n in p["open"]["runners"].items(): runs[_stem(r)] += n
        top = max(runs.values(), default=0)
        runner[(p["rid"], p["tm"])] = {r for r, n in runs.items() if n == top or n >= 0.4 * sum(runs.values())}
    for p in sorted((p for p in D["plays"] if p["play"] == "split" and p["side"] == "defender"), key=lambda p: p["t0"]):
        if not p.get("who") or p.get("call") in ("no answer", "part-run", None): continue
        first.setdefault((p["rid"], p["tm"], (p.get("split") or {}).get("id")), p)
    for p in first.values():
        if len(p["who"]) > 2: continue
        for r in p["who"]:
            if _stem(r) not in runner.get((p["rid"], p["tm"]), ()) and (monks or not ("Monk" in r or "Prot" in r)): G[p["team"]][_stem(r)] += 1
    return {g: c.most_common(1)[0][0] for g, c in G.items() if c.most_common(1)[0][1] >= RESP_MIN and c.most_common(1)[0][1] >= RESP_SHARE * sum(c.values())}, G


OPEN_OUT = (("flags 3:00", "lead180", "{:+10.2f}"), ("flags 5:00", "lead300", "{:+10.2f}"), ("net kills 3:00", "kills180", "{:+14.2f}"), ("net kills 5:00", "kills300", "{:+14.2f}"),
            ("net NPCs 5:00", "npcs300", "{:+13.2f}"), ("boosts 2:00, 4:00", "boosts300", "{:+17.2f}"), ("win pts 5:00", "v300", "{:+12.1f}"), ("win pts 8:00", "v480", "{:+12.1f}"))
OPEN_MAIN = (("flags at 5:00", "lead300", " flags", 1), ("net kills by 5:00", "kills300", " kills", 1), ("NPCs by 5:00", "npcs300", " NPCs", 1), ("the boosts of 2:00 and 4:00", "boosts300", " boosts", 1),
             ("chance of winning at 5:00", "v300", " points", 0), ("chance of winning at 8:00", "v480", " points", 0))      # what a call is judged on (his answer of 2026-11-22: "The main thing is flag advantage and kills; then to smaller extent boost and winning at 5:00 and 8:00"; the NPCs are his "ability to defend splits (so NPCs lost)")
OPEN_VARS = ("strength gap", "the hall's flag run, seconds", "our first flag on a frontliner", "our first flag on a midline player", "their first flag on a frontliner", "their first flag on a midline player")
GATES = ("all eight to the stand", "a split from the gates", "a player back at the flag spawn for the next flag", "other (players kept at home, mostly against a split)")


def opening_cases(D, M, B):
    """One case a team's opening (R-520, R-541, R-590), from its own side: what it showed the other team at the gates (players at the stand, a split, a player
    left back, a flag or none and on whom) and what the other team showed it; who capped first, and whether it sent a player back for its next flag before
    anybody had capped; and what stood 3, 5 and 8 minutes from the gates: flags, kills, NPCs, boosts, and the chance of winning priced without its match.
    Every result but the chance of winning is also kept set level on the strength gap (`_lv`: less what the gap gives on its own, a straight line over every
    opening), since the stronger team picks its opening too."""
    out, skipped, (resp, _), early = [], collections.Counter(), usual_responder(D, monks=False), collections.defaultdict(list)      # the player other than a monk (R-598)
    for p in D["plays"]:
        if p["play"] == "split" and p["side"] == "attacker" and p["t0"] <= OPEN_SPLIT_BY: early[(p["rid"], p["tm"])].append(p["t0"])
    for p in D["plays"]:
        if p["play"] != "opening": continue
        if "meet" not in p.get("open", {}) or "480" not in p["open"].get("later", {}): raise ValueError(f"opening play {p['id']} carries no record of the next flag or of 8:00: run moments.py all again on this engine (R-460)")
        c = _told(p, M, B)
        if c is None: skipped["no winner recorded, or the flag lead not read"] += 1; continue
        m, o, f = M[p["rid"]], p["open"], p["beside"]["flag"]; th, tf, lt = o["their"], o["their_flag"], o["later"]
        st, gap, beta, won = p["at_told"]["state"], m["gap"][p["team"]], B[m["fold"]], float(m["winner"] == p["team"])
        mine, theirs = p["beside"]["first_cap"], o["their_first_cap"]
        flag = (OPEN_FLAG[1] if f["how"] == "captured" and (f.get("held_s") or 0) >= 15 else OPEN_FLAG[0] if f["how"] == "captured" else OPEN_FLAG[2]) if f["brought"] else OPEN_FLAG[3] if f.get("sent_back") else OPEN_FLAG[4]
        mu = (OPEN_MATCHUP[4] if o["split"] or th["split"] else OPEN_MATCHUP[0] if (o["stand"], th["stand"]) == (8, 8) else OPEN_MATCHUP[1] if (o["stand"], th["stand"]) == (8, 7)
              else OPEN_MATCHUP[2] if (o["stand"], th["stand"]) == (7, 8) else OPEN_MATCHUP[3] if (o["stand"], th["stand"]) == (7, 7) else OPEN_MATCHUP[5])
        at = lambda h, fn: None if lt[h]["ended"] else fn(lt[h])
        a180 = p["at_told"]["after"]["180"]
        def priced(h):
            if lt[h]["ended"]: return 100 * (won - c["p0"])
            x = position(st, lt[h], gap, True)
            return None if x is None else 100 * (chance(beta, x) - c["p0"])
        caps = [x for x in (mine, theirs) if x is not None]; cap0 = min(caps) if caps else None
        sent = lambda n: bool(n and not n["left"] and n["off"] > o["meet"] and n["off"] <= OPEN_EARLY_BY and (cap0 is None or n["off"] < cap0))      # turned for home after the teams met and before either had capped
        capped_first = mine is not None and (theirs is None or mine < theirs)
        team_id = (p["rid"], p["tm"])
        mine_resp = resp.get(p["team"]) if resp.get(p["team"]) in {_stem(r) for v in o["roles"].values() for r in v} else None      # the guild's usual split response, where that player is in this line-up
        their_tag = next(t for t in m["teams"] if t != p["team"])
        their_resp = resp.get(their_tag) if resp.get(their_tag) in {_stem(r) for v in o["their_roles"].values() for r in v} else None
        gates = GATES[1] if o["split"] else GATES[0] if o["stand"] == 8 else GATES[2] if o["waits"] and o["stand"] == 7 else GATES[3]
        c.update(their_held=bool(tf["brought"] and (tf.get("held_s") or 0) >= 15), gates=gates)
        c["v"].update({"300": priced("300"), "480": priced("480")})
        c.update(flag=flag, brought=bool(f["brought"]), their_brought=bool(tf["brought"]), matchup=mu, stand=o["stand"], their_stand=th["stand"], line=f.get("line") if f["brought"] else None,
                 their_line=tf.get("line") if tf["brought"] else None, held=bool(f["brought"] and (f.get("held_s") or 0) >= 15), handed=bool(f["brought"] and len(f["by"]) > 1),
                 lost=bool(f["brought"] and f["how"] not in ("captured", "not run")), first_cap=mine, their_first_cap=theirs, both_capped=mine is not None and theirs is not None,
                 capped_first=capped_first, sent_back=sent(o["next"]), their_sent_back=sent(o["their_next"]), meet=o["meet"],
                 lead180=None if a180["ended"] else a180["lead_change"], lead300=at("300", lambda x: x["lead_change"]),
                 kills180=None if a180["ended"] else a180["deaths"][1] - a180["deaths"][0], kills300=at("300", lambda x: x["deaths"][1] - x["deaths"][0]),
                 npcs300=at("300", lambda x: x["npcs"][1] - x["npcs"][0]), npcs_lost300=at("300", lambda x: x["npcs"][0]), boosts300=at("300", lambda x: x["boosts"][0] - x["boosts"][1]),
                 first_boost=None if a180["ended"] else a180["boosts"][0] - a180["boosts"][1],
                 lose300=at("300", lambda x: x["deaths"][0] > 0), kill300=at("300", lambda x: x["deaths"][1] > 0), v300=c["v"]["300"], v480=c["v"]["480"],
                 first_kill=None if not o.get("first_death") or o["first_death"][0] > 300 else o["first_death"][1] == "their",
                 responder=mine_resp, their_responder=their_resp, on_responder=bool(f["brought"] and f["by"] and mine_resp and _stem(f["by"][0]) == mine_resp),
                 their_on_responder=bool(tf["brought"] and tf["by"] and their_resp and _stem(tf["by"][0]) == their_resp),
                 they_split=bool(early[(p["rid"], 3 - p["tm"])]), we_split=bool(early[team_id]), by=f["by"], won=won, gap=gap, fold=m["fold"], run_s=m["run_s"])
        out.append(c)
    for _, k, _ in OPEN_OUT:                                               # each hard result set level on the strength gap
        if k.startswith("v"):
            for c in out: c[k + "_lv"] = c[k]
            continue
        X = [c for c in out if c[k] is not None]
        b = float(np.polyfit([c["gap"] for c in X], [float(c[k]) for c in X], 1)[0]) if len(X) > 30 else 0.0
        for c in out: c[k + "_lv"] = None if c[k] is None else float(c[k]) - b * c["gap"]
    return out, skipped


def _open_cmp(pr, o, X, label, f, g, fa, ga):
    """One call against another, from the side of the team that makes it, on what he judges an opening by: each result set level on the strength gap, the
    difference with its 90% range over whole matches. A reading; `clear` where the range lies to one side of nothing."""
    na, nb = sum(1 for c in X if f(c)), sum(1 for c in X if not f(c) and g(c))
    ra, rb = len({c["rid"] for c in X if f(c)}), len({c["rid"] for c in X if not f(c) and g(c)})
    low = min(na, nb) < MIN_PLAYS or min(ra, rb) < MIN_MATCHES
    pr(f"   {label}: {fa} ({na} in {ra} matches) against {ga} ({nb} in {rb})" + ("   UNDER THE FLOOR of 30 plays and 15 matches a side: as it fell, no reading" if low else ""))
    r = o[label] = {"first": fa, "second": ga, "n": [na, nb], "matches": [ra, rb], "under_the_floor": bool(low), "results": {}}
    if not na or not nb: return r
    for name, k, unit, lv in OPEN_MAIN:
        Y = [c for c in X if c[k + "_lv"] is not None and (f(c) or g(c))]
        for c in Y: c["_y"] = c[k + "_lv"]
        d, lo, hi, a_, b_ = _num_range(Y, f, g)
        if d is None or lo is None: continue
        word = "no reading" if low else "better" if lo > 0 else "worse" if hi < 0 else "no clear difference"
        r["results"][name] = {"difference": float(d), "range": [float(lo), float(hi)], "n": [a_, b_], "reads": word}
        fm = (lambda v: f"{v:+.1f}") if unit == " points" else (lambda v: f"{v:+.2f}")
        pr(f"      {name:30} {fm(d)}{unit} ({fm(lo)} to {fm(hi)})   {word}")
    return r


def _open_scenario(C, call):
    """The cases of one opening spot laid out for like spots (R-538), matched on what a team knows at the gates (OPEN_VARS): there is no minute before an
    opening, so strength, the hall and on whom each first flag came up are what a call can be set level on."""
    V = []
    for c in C:
        k = call(c)
        if k is None or c["v300"] is None or c["v480"] is None: continue
        V.append(dict(c, call=k, more=None, pre=None, x=[c["gap"], c["run_s"], float(c["line"] == "frontline"), float(c["line"] == "midline"), float(c["their_line"] == "frontline"), float(c["their_line"] == "midline")]))
    if len(V) < 2 * MIN_PLAYS: return None
    s = Scenario(V); s.names = list(OPEN_VARS)
    for H in ("300", "480"): s.v[H] = s.y[H] = np.array([c["v"][H] for c in V], float)
    return s


def opening_report(path, out_json=None):
    """The opening (R-520, R-590, R-596), set out on the seven decisions he passed (R-611): who goes where from the gates; whether to bring the first flag up
    and on whom; at the stand, cap or hold; hand the flag to another player; send a player back for the next flag before anyone has capped; split, or answer
    a split, in the first 3:00; and what to do with a flag when they bring none. For each: what teams do, by what they can see of the other team, and what
    followed the call, judged on flags and kills first, then the boosts and the chance of winning at 5:00 and 8:00, with the NPCs, set level on strength.
    Who caps first, and whether anybody caps, is what two teams' choices come to and is never a call (R-608): it is kept only among the readings. Like spots
    and the test on unseen matches where teams divide. A report: nothing in it is advice until that test shows a gain."""
    D, M = load(path); B, P = prices(D, M)
    C, skipped = opening_cases(D, M, B)
    resp, RG = usual_responder(D, monks=False)
    lines, res = [], {"cases": len(C), "skipped": dict(skipped), "decisions": {}, "checks": {}, "as_it_fell": {}, "calls": {}}
    pr = lambda x="": (lines.append(x), print(x))
    mean = lambda V, k: float(np.mean([c[k] for c in V if c[k] is not None] or [0.0]))
    pct = lambda V, f: 100 * float(np.mean([bool(f(c)) for c in V])) if V else 0.0
    pr(f"The opening (R-590, R-596, R-611), on {len(M)} matches: {len(C)} openings in {len({c['rid'] for c in C})} matches, each team's read from its own side"
       + "".join(f"; set aside, {k}: {v}" for k, v in skipped.most_common() if v))
    NS = [c for c in C if c["matchup"] != OPEN_MATCHUP[4]]                 # no split from the gates by either team
    U = [c for c in NS if c["brought"]]                                    # ... and a first flag brought up: the openings in which a team stands at the stand with its flag
    E8 = [c for c in U if c["stand"] == 8]
    N = [c for c in C if c["brought"] and not c["their_brought"]]
    K = [c for c in C if c["their_brought"] and c["their_responder"] and c["matchup"] != OPEN_MATCHUP[4]]
    K2 = [c for c in C if c["brought"] and c["responder"] and c["matchup"] != OPEN_MATCHUP[4]]
    sees = (("8 v 8", OPEN_MATCHUP[0]), ("eight against seven (they have a player back)", OPEN_MATCHUP[1]), ("seven against eight (we have a player back)", OPEN_MATCHUP[2]), ("7 v 7 (each has a player back)", OPEN_MATCHUP[3]))
    dd = res["decisions"]
    pr("\nA. The seven decisions, and what teams do")
    pr("   1. Who goes where from the gates (before a team has seen the other)")
    dd["1 from the gates"] = {g_: sum(1 for c in C if c["gates"] == g_) for g_ in GATES}
    for g_ in GATES: pr(f"      {g_:56} {dd['1 from the gates'][g_]:4}  {pct(C, lambda c: c['gates'] == g_):3.0f}%")
    pr("   2. Whether to bring the first flag up, and on whom (frontline = warriors, dervishes, melee assassins; midline = the rest but monks)")
    dd["2 the first flag"] = {"brings one": pct(C, lambda c: c["brought"]), **{ln: sum(1 for c in C if c["line"] == ln) for ln in OPEN_LINES}, "none": sum(1 for c in C if not c["brought"])}
    pr(f"      brings one {pct(C, lambda c: c['brought']):.0f}%: " + ", ".join(f"on a {ln} player {pct(C, lambda c: c['line'] == ln):.0f}%" for ln in OPEN_LINES) + f"; none {pct(C, lambda c: not c['brought']):.0f}%")
    pr(f"   3. At the stand: cap or hold (a first flag brought up and no split from the gates, {len(U)}; hold = the flag in hand at the stand 15 s or more before it is capped)")
    dd["3 cap or hold"] = o3 = {"all": {"openings": len(U), "holds": pct(U, lambda c: c["held"])}}
    pr(f"      {'all of them':56} {len(U):4}  holds {pct(U, lambda c: c['held']):3.0f}%")
    for lab, mu in sees:
        X = [c for c in U if c["matchup"] == mu]; o3[lab] = {"openings": len(X), "holds": pct(X, lambda c: c["held"])}
        pr(f"      {lab:56} {len(X):4}  holds {pct(X, lambda c: c['held']):3.0f}%")
    for ln in OPEN_LINES:
        X = [c for c in E8 if c["line"] == ln]; o3[f"eight at the stand, flag on a {ln} player"] = {"openings": len(X), "holds": pct(X, lambda c: c["held"])}
        pr(f"      {'eight at the stand, the flag on a ' + ln + ' player':56} {len(X):4}  holds {pct(X, lambda c: c['held']):3.0f}%")
    pr(f"   4. Hand the flag to another player ({len(U)})")
    dd["4 hand it on"] = o4 = {"all": pct(U, lambda c: c["handed"])}
    pr(f"      {'all of them':56} {len(U):4}  hands it on {pct(U, lambda c: c['handed']):3.0f}%")
    for ln in OPEN_LINES:
        X = [c for c in E8 if c["line"] == ln]; o4[f"eight at the stand, flag on a {ln} player"] = pct(X, lambda c: c["handed"])
        pr(f"      {'eight at the stand, the flag on a ' + ln + ' player':56} {len(X):4}  hands it on {pct(X, lambda c: c['handed']):3.0f}%")
    pr(f"   5. Send a player back for the next flag before anyone has capped ({len(NS)}, no split from the gates)")
    dd["5 send a player back"] = o5 = {"all": pct(NS, lambda c: c["sent_back"])}
    pr(f"      {'all of them':56} {len(NS):4}  sends one back {pct(NS, lambda c: c['sent_back']):3.0f}%")
    for lab, mu in sees:
        X = [c for c in NS if c["matchup"] == mu]; o5[lab] = pct(X, lambda c: c["sent_back"])
        pr(f"      {lab:56} {len(X):4}  sends one back {pct(X, lambda c: c['sent_back']):3.0f}%")
    pr(f"   6. Split, or answer a split, in the first 3:00 ({len(C)})")
    dd["6 a split"] = {"splits": pct(C, lambda c: c["we_split"]), "is split on": pct(C, lambda c: c["they_split"])}
    pr(f"      a team splits in the first 3:00 in {pct(C, lambda c: c['we_split']):.0f}% of openings and is split on in {pct(C, lambda c: c['they_split']):.0f}%. The answer to a split is the split family's (`cases.py splits`).")
    kinds = collections.Counter(resp.values()); res["responders"] = kinds.most_common()
    pr(f"      The usual split response (R-593, R-598: the player other than a monk most often sent from the main team, the runner left out), for the {len(resp)} guilds that have one: " + ", ".join(f"{k} {n}" for k, n in kinds.most_common())
       + f". A first flag came up on that player {sum(1 for c in K2 if c['on_responder'])} times in {len(K2)}.")
    pr(f"   7. They bring no flag and we bring one ({len(N)})")
    dd["7 no flag against us"] = {"caps inside 15 s": sum(1 for c in N if c["flag"] == OPEN_FLAG[0]), "holds 15 s or more, then caps": sum(1 for c in N if c["flag"] == OPEN_FLAG[1]), "never caps it": sum(1 for c in N if c["flag"] == OPEN_FLAG[2])}
    pr("      " + ", ".join(f"{k} {v}" for k, v in dd["7 no flag against us"].items()))
    F = [c for c in C if c["brought"] and c["their_brought"] and c["both_capped"] and c["matchup"] != OPEN_MATCHUP[4]]
    pr(f"\nB. The readings: what any player knows of the opening, checked. Who caps first is no call (R-608: \"Nobody capping is no one's decision\"): N1 to N4 say only what follows it ({len(F)} openings where both capped, no split from the gates)")
    rd = lambda X, *a, **k: _reading(pr, res, X, *a, **k)
    sec, fst = (lambda c: not c["capped_first"]), (lambda c: c["capped_first"])
    rd([c for c in F if c["lead180"] is not None], "N1 the team that caps second is better off in flags at 3:00 than the team that caps first (F25)", sec, fst, +1, lambda c: c["lead180"], "caps second", "caps first", unit=" flags")
    rd([c for c in F if c["lead300"] is not None], "N2 the same at 5:00", sec, fst, +1, lambda c: c["lead300"], "caps second", "caps first", unit=" flags")
    rd([c for c in F if c["kills300"] is not None], "N3 the team that caps second is ahead in kills at 5:00", sec, fst, +1, lambda c: c["kills300"], "caps second", "caps first", unit=" kills")
    rd([c for c in F if c["kills300"] is not None], "N3b ... counted as ahead or behind, so that a wipe is one game and not eight kills (ahead +1, level 0, behind -1)", sec, fst, +1, lambda c: float(np.sign(c["kills300"])), "caps second", "caps first", unit=" (share ahead less share behind)")
    rd([c for c in F if c["boosts300"] is not None], "N4 the team that caps second takes more of the boosts of 2:00 and 4:00", sec, fst, +1, lambda c: c["boosts300"], "caps second", "caps first", unit=" boosts")
    rd(C, "N5 a team with all eight at the stand caps second more often against seven than against eight", lambda c: c["matchup"] == OPEN_MATCHUP[1], lambda c: c["matchup"] == OPEN_MATCHUP[0], +1, lambda c: not c["capped_first"], "8 v 7", "8 v 8")
    rd(U, "N5b ... and holds its flag more often", lambda c: c["matchup"] == OPEN_MATCHUP[1], lambda c: c["matchup"] == OPEN_MATCHUP[0], +1, lambda c: c["held"], "8 v 7", "8 v 8")
    V7 = [c for c in C if c["matchup"] in (OPEN_MATCHUP[0], OPEN_MATCHUP[2])]
    rd([c for c in V7 if c["first_boost"] is not None], "N12 a team that leaves a player back against eight takes the boost of 2:00 more often than a team in an 8 v 8 (ours less theirs)", lambda c: c["matchup"] == OPEN_MATCHUP[2], lambda c: True, +1, lambda c: c["first_boost"], "7 v 8", "8 v 8", unit=" boosts")
    rd([c for c in V7 if c["boosts300"] is not None], "N13 the same over the boosts of 2:00 and 4:00", lambda c: c["matchup"] == OPEN_MATCHUP[2], lambda c: True, +1, lambda c: c["boosts300"], "7 v 8", "8 v 8", unit=" boosts")
    rd([c for c in V7 if c["lose300"] is not None], "N14 a team that leaves a player back against eight loses a player in the first five minutes more often than a team in an 8 v 8", lambda c: c["matchup"] == OPEN_MATCHUP[2], lambda c: True, +1, lambda c: c["lose300"], "7 v 8", "8 v 8")
    rd(U, "N6 a first flag on a frontliner with a player left back is capped first more often than other first flags", lambda c: c["line"] == "frontline" and c["stand"] == 7, lambda c: True, +1, lambda c: c["capped_first"], "frontliner, one back", "other first flags")
    rd(E8, "N7 all eight at the stand: a first flag on a midline player is held more often than one on a frontliner", lambda c: c["line"] == "midline", lambda c: c["line"] == "frontline", +1, lambda c: c["held"], "on a midline", "on a frontliner")
    rd(E8, "N8 all eight at the stand: a first flag on a frontliner is handed to another player more often than one on a midline", lambda c: c["line"] == "frontline", lambda c: c["line"] == "midline", +1, lambda c: c["handed"], "on a frontliner", "on a midline")
    rd(U, "N9 a first flag that came up on a frontliner is lost before it is capped more often than one on a midline", lambda c: c["line"] == "frontline", lambda c: c["line"] == "midline", +1, lambda c: c["lost"], "on a frontliner", "on a midline")
    rd(K, "N15 a team splits in the first 3:00 more often where their first flag came up on their usual split response", lambda c: c["their_on_responder"], lambda c: True, +1, lambda c: c["we_split"], "their flag on their split response", "on another player")
    rd(K2, "N16 a team whose first flag came up on its own usual split response hands it to another player more often", lambda c: c["on_responder"], lambda c: True, +1, lambda c: c["handed"], "our flag on our split response", "on another player")
    head = f"     {'':62} {'cases':>5}  {'started at':>10}  {'holds':>6}  " + "  ".join(f"{n:>{len(fm.format(0))}}" for n, _, fm in OPEN_OUT) + f"  {'first kill':>10}  {'wins':>5}"
    def row(o, label, V):
        if not V: return
        r = {"cases": len(V), "matches": len({c["rid"] for c in V}), "started at": 100 * mean(V, "p0"), "holds": 100 * mean(V, "held"), **{n: mean(V, k) for n, k, _ in OPEN_OUT}, "first kill": 100 * mean(V, "first_kill"), "wins": 100 * mean(V, "won")}
        o[label] = r
        pr(f"     {label:62} {len(V):5}  {r['started at']:9.0f}%  {r['holds']:5.0f}%  " + "  ".join(fm.format(r[n]) for n, _, fm in OPEN_OUT) + f"  {r['first kill']:9.0f}%  {r['wins']:4.0f}%"
           + ("   (under the floor)" if len(V) < MIN_PLAYS or r["matches"] < MIN_MATCHES else ""))
    pr("\nC. As it fell, decision by decision: a description set against no like spot; the opening a team picks follows its build and its strength")
    pr("   started at = its chance of winning at the gates; flags = change in its flag lead from the gates; net kills = theirs dead less ours; net NPCs = theirs lost less ours; boosts = ours less")
    pr("   theirs; win pts = the change in its chance of winning by then, priced without its match; first kill = it takes the first kill of the game, where there is one by 5:00.")
    cm = lambda *a: _open_cmp(pr, res["calls"], *a)
    note = ("   A difference is between the teams that make the call and the teams that do not, their own opponents among them, who lose what they gain: it overstates the call's own gain by the",
            "   share of the others who faced it. The ranges are over whole matches and stand. A reading, never advice; under the floor of 30 plays and 15 matches a side it is shown as it fell.")
    pr("\nD. Is it the right call? Each decision from the side of the team that makes it, every result set level on the strength gap (an opening has no minute before it to test a call against).")
    for x in note: pr(x)
    pr("\n   1. From the gates"); pr(head); o = res["as_it_fell"]["1 from the gates"] = {}
    for g_ in GATES: row(o, g_, [c for c in C if c["gates"] == g_])
    for lab, mu in sees: row(o, "  " + lab, [c for c in C if c["matchup"] == mu])
    G3 = [c for c in C if c["gates"] in GATES[:3]]
    cm(G3, "from the gates: a split", lambda c: c["gates"] == GATES[1], lambda c: c["gates"] == GATES[0], "a split from the gates", "all eight to the stand")
    cm(V7, "from the gates: a player back against eight", lambda c: c["matchup"] == OPEN_MATCHUP[2], lambda c: True, "leaves a player back", "brings eight (8 v 8)")
    pr("\n   2. The first flag, and on whom (no split from the gates)"); pr(head); o = res["as_it_fell"]["2 the first flag"] = {}
    for ln in OPEN_LINES: row(o, f"brought up on a {ln} player", [c for c in NS if c["line"] == ln])
    row(o, "no flag brought up", [c for c in NS if not c["brought"]])
    cm(U, "the first flag: on a frontliner", lambda c: c["line"] == "frontline", lambda c: c["line"] == "midline", "on a frontliner", "on a midline player")
    cm(NS, "the first flag: bring none", lambda c: not c["brought"], lambda c: True, "brings no flag", "brings one")
    pr("\n   3. At the stand: cap or hold"); pr(head); o = res["as_it_fell"]["3 cap or hold"] = {}
    row(o, "holds 15 s or more", [c for c in U if c["held"]]); row(o, "caps without holding", [c for c in U if not c["held"]])
    for lab, mu in sees:
        row(o, f"  {lab}: holds", [c for c in U if c["matchup"] == mu and c["held"]]); row(o, f"  {lab}: does not", [c for c in U if c["matchup"] == mu and not c["held"]])
    cm(U, "at the stand: hold", lambda c: c["held"], lambda c: True, "holds 15 s or more", "caps without holding")
    for lab, mu in sees[:3]: cm([c for c in U if c["matchup"] == mu], f"{lab}: hold", lambda c: c["held"], lambda c: True, "holds 15 s or more", "caps without holding")
    cm([c for c in E8 if c["line"] == "midline"], "eight at the stand, the flag on a midline player: hold", lambda c: c["held"], lambda c: True, "holds 15 s or more", "caps without holding")
    cm([c for c in E8 if c["line"] == "frontline"], "eight at the stand, the flag on a frontliner: hold", lambda c: c["held"], lambda c: True, "holds 15 s or more", "caps without holding")
    bh = [c for c in U if c["held"] and c["their_held"]]; res["both_hold"] = {"openings": len(bh), "matches": len({c["rid"] for c in bh})}
    pr(f"   (Both teams hold in {len(bh)} openings of {len({c['rid'] for c in bh})} matches: there the two make the same call and what one gains the other loses.)")
    pr("\n   4. Hand the flag to another player"); pr(head); o = res["as_it_fell"]["4 hand it on"] = {}
    row(o, "hands it on", [c for c in U if c["handed"]]); row(o, "keeps it on the player who brought it", [c for c in U if not c["handed"]])
    cm(U, "hand the flag on", lambda c: c["handed"], lambda c: True, "hands it to another player", "keeps it")
    cm([c for c in E8 if c["line"] == "frontline"], "eight at the stand, the flag on a frontliner: hand it on", lambda c: c["handed"], lambda c: True, "hands it to another player", "keeps it on him")
    pr("\n   5. Send a player back for the next flag before anyone has capped"); pr(head); o = res["as_it_fell"]["5 send a player back"] = {}
    row(o, "sends one back", [c for c in NS if c["sent_back"]]); row(o, "does not", [c for c in NS if not c["sent_back"]])
    cm(NS, "send a player back before a cap", lambda c: c["sent_back"], lambda c: True, "sends a player back", "does not")
    cm([c for c in NS if c["matchup"] == OPEN_MATCHUP[1]], "eight against seven: send a player back too", lambda c: c["sent_back"], lambda c: True, "sends a player back", "does not")
    pr("\n   6. A split in the first 3:00"); pr(head); o = res["as_it_fell"]["6 a split"] = {}
    row(o, "we split in the first 3:00", [c for c in C if c["we_split"]]); row(o, "they split on us", [c for c in C if c["they_split"]]); row(o, "nobody splits", [c for c in C if not c["they_split"] and not c["we_split"]])
    row(o, "their flag on their usual split response", [c for c in K if c["their_on_responder"]]); row(o, "  and we split", [c for c in K if c["their_on_responder"] and c["we_split"]])
    cm(C, "split in the first 3:00", lambda c: c["we_split"], lambda c: True, "splits", "does not")
    cm(K, "their flag on their usual split response: split", lambda c: c["their_on_responder"] and c["we_split"], lambda c: c["their_on_responder"], "splits in the first 3:00", "does not")
    pr("\n   7. They bring no flag and we bring one"); pr(head); o = res["as_it_fell"]["7 no flag against us"] = {}
    row(o, "we cap ours inside 15 s of reaching the stand", [c for c in N if c["flag"] == OPEN_FLAG[0]]); row(o, "we hold ours 15 s or more, then cap", [c for c in N if c["flag"] == OPEN_FLAG[1]]); row(o, "we never cap it", [c for c in N if c["flag"] == OPEN_FLAG[2]])
    cm(N, "they bring no flag: cap ours at once", lambda c: c["flag"] == OPEN_FLAG[0], lambda c: True, "caps inside 15 s", "holds, or never caps")
    # ---- like spots and the test on unseen matches, only where teams divide
    pr("\nE. Like spots and the test on matches the advice never saw, only where teams divide (the floor of 30 plays and 15 matches a call). Matched on: " + ", ".join(OPEN_VARS))
    pr("   The advice for each opening comes from the other groups of matches; teams that matched it are set against those that did not, in the chance of winning at 5:00 and 8:00 and in how the match ended.")
    spots = (("3. at the stand with a flag, no split: hold it 15 s or more, or cap without holding", U, lambda c: "holds" if c["held"] else "does not hold"),
             ("3. eight at the stand with a flag: hold, or cap without holding", E8, lambda c: "holds" if c["held"] else "does not hold"),
             ("4. a first flag brought up, no split: hand it on or keep it", U, lambda c: "hands it on" if c["handed"] else "keeps it"),
             ("1. from the gates: a split, or all eight to the stand", G3, lambda c: "a split" if c["gates"] == GATES[1] else "eight to the stand" if c["gates"] == GATES[0] else None))
    res["like_spots"] = {}
    for name, X, call in spots:
        s_ = _open_scenario(X, call); o = res["like_spots"][name] = {}
        if s_ is None or len(s_.calls) < 2 or min(collections.Counter(s_.call.tolist()).values()) < MIN_PLAYS: pr(f"\n   {name}: too few of one call to set beside the other"); o["reads"] = "too few"; continue
        K_, _ = choose_k({name: s_}); o["K"] = K_; o["calls"] = dict(collections.Counter(s_.call.tolist()))
        pr(f"\n   {name} ({len(s_.C)}: " + ", ".join(f"{k} {n}" for k, n in collections.Counter(s_.call.tolist()).most_common()) + f"); the {K_} nearest cases of each call")
        for H, lab in (("300", "5:00"), ("480", "8:00")):
            ref, rows_ = s_.calls[0], []
            for i in range(len(s_.C)):
                r = s_.read(i, K_, False, H)
                if len(r["calls"]) == 2: a_ = next(a for a in r["calls"] if a != ref); rows_.append((r["calls"][a_]["worth"] - r["calls"][ref]["worth"], math.hypot(r["calls"][a_]["se"], r["calls"][ref]["se"])))
            if len(rows_) < MIN_PLAYS: pr(f"     at {lab}: too few spots with both calls round them"); continue
            mu_, se_ = float(np.mean([d_ for d_, _ in rows_])), float(np.mean([e_ for _, e_ in rows_])); lo, hi = mu_ - Z * se_, mu_ + Z * se_
            other = next(a for a in s_.calls if a != ref)
            o[f"worth {lab}"] = {"call": other, "against": ref, "worth": mu_, "range": [lo, hi], "reads": "better" if lo > 0 else "worse" if hi < 0 else "no clear difference"}
            pr(f"     at {lab}: \"{other}\" against \"{ref}\" at the same spot {mu_:+.1f} points ({lo:+.1f} to {hi:+.1f})   {o[f'worth {lab}']['reads']}")
            t = advice_test({name: s_}, K_, H); o[f"test {lab}"] = t
            adv = ", ".join(f"{a_} {n_}" for a_, n_ in sorted(t.get("advice", {}).items(), key=lambda q: -q[1]))
            if "v" not in t: pr(f"     the test at {lab}: clear advice in {t['rows']} of {len(s_.C)} [{adv}]: too few to call")
            else: pr(f"     the test at {lab}: clear advice in {t['rows']} of {len(s_.C)} ({adv}), matched {t['matched']}: {t['v']['effect']:+.1f} ({t['v']['range'][0]:+.1f} to {t['v']['range'][1]:+.1f}) {t['v']['verdict']}; "
                     f"in how the match ended {t['end']['effect']:+.1f} ({t['end']['range'][0]:+.1f} to {t['end']['range'][1]:+.1f})")
    if out_json: json.dump(res, open(out_json, "w"), indent=1, default=lambda x: float(x) if isinstance(x, (np.floating, np.integer)) else str(x))
    return res


HAND_UP = 0.35                                    # up on flags, for his first point: the tally of R-408 half a flag or more ahead at the pickup (`common.LEAD_HALF`)
HAND_HOLD_S = 15                                 # a held flag: in hand at the stand this long before it is capped (`common.HOLD_S`)
HOLD_GROUPS = ("the stand mesmer", "the Mes/A", "another midline player", "a frontliner", "a monk")


def _hold_group(role, line):
    r = role or ""
    return HOLD_GROUPS[0] if r.startswith("Stand Mes") else HOLD_GROUPS[1] if r.startswith("Mes/A") else HOLD_GROUPS[3] if line == "frontline" else HOLD_GROUPS[4] if line == "backline" else HOLD_GROUPS[2]


def hand_cases(D, M, B):
    """The flag lives and the put-downs of `jobs.flag_hands` (R-620), each priced at the second it is read from, without its match."""
    lives, puts, holds, skipped = [], [], [], collections.Counter()
    for rid, v in D["flag_cost"].items():
        if "flag_hands" not in (v or {}): raise ValueError(f"match {rid} carries no record of its flags' put-downs: run moments.py all again on this engine (R-460)")
        L = sorted(v["flag_hands"]["lives"], key=lambda x: x["t0"])
        for x in L:
            c = _told(dict(x, rid=rid), M, B)
            if c is None: skipped["a flag life: no winner recorded, or the flag lead not read"] += 1; continue
            nxt = next((y for y in L if y["tm"] == x["tm"] and y["t0"] > x["t0"]), None)
            c.update({k: x[k] for k in ("tm", "first_flag", "runner", "runner_line", "carriers", "how", "end", "form", "arrive", "held_s", "holder", "holder_line", "put_downs")})
            ar = x["arrive"]; on = next((k for k in x["carriers"] if ar and k[2] <= ar["t"] + 1 and (k[3] is None or k[3] >= ar["t"])), None)      # the carry in which it first stood at the stand
            c.update(own_stand=c["state"]["stand"] == "own", stood_s=None if not on or on[3] is None else on[3] - ar["t"],
                     handed_at_stand=bool(ar) and any(k[2] > ar["t"] and k[0] != ar["by"] for k in x["carriers"]))
            c.update(lead=c["state"]["flag_lead"], captured=x["how"] == "captured", returned=x["how"] == "returned", cap_s=None if x["how"] != "captured" else x["end"] - x["t0"],
                     next_s=None if nxt is None or x["end"] is None else nxt["t0"] - x["end"], next_runner=None if nxt is None else nxt["runner"])
            lives.append(c)
            if x.get("hold_told"):
                h = _told(dict(x, rid=rid, t0=x["hold_t"], at_told=x["hold_told"], id=x["id"] + "-hold"), M, B)
                if h is None: skipped["a held flag: no winner recorded, or the flag lead not read"] += 1; continue
                h.update(tm=x["tm"], first_flag=x["first_flag"], holder=x["holder"], line=x["holder_line"], group=_hold_group(x["holder"], x["holder_line"]), held_s=x["held_s"], lead=h["state"]["flag_lead"],
                         next_s=c["next_s"], holder_runs_next=c["next_runner"] == x["holder"], npcs_lost=h["hard"]["180"]["npcs"][0])
                holds.append(h)
        for x in v["flag_hands"]["put_downs"]:
            c = _told(dict(x, rid=rid), M, B)
            if c is None: skipped["a put-down: no winner recorded, or the flag lead not read"] += 1; continue
            if "returned_soon" not in x: raise ValueError(f"match {rid}: a put-down carries no reading of when it was returned: run moments.py all again on this engine (R-460)")
            c.update({k: x[k] for k in ("tm", "life", "first_flag", "by", "by_line", "carried_s", "dead", "place", "at_stand", "own_half", "before_stand", "enemy_near", "nearest", "mates_near", "then", "lay_s", "taker", "taker_line", "handed",
                                        "handoff", "first_enemy_s", "return_by_s", "returned_soon", "returned_soon_sure")})
            c.update(returned=x["then"] == "returned", in_range=x["enemy_near"] > 0, lead=c["state"]["flag_lead"])
            puts.append(c)
    return lives, puts, holds, skipped


def handoff(path, out_json=None):
    """The hand-off and the flag returned (R-620 to R-624): the record of every put-down, what a return costs, and his three points as readings on it. A
    report: it advises nothing, and how a flag is carried follows the spot a team is in (a team under pressure hands off where it must)."""
    D, M = load(path); B, P = prices(D, M)
    lives, puts, holds, skipped = hand_cases(D, M, B)
    lines, res = [], {"lives": len(lives), "put_downs": len(puts), "holds": len(holds), "skipped": dict(skipped), "checks": {}, "record": {}, "price": {}, "frontliner": {}, "opening": {}, "holding": {}}
    pr = lambda x="": (lines.append(x), print(x))
    pct = lambda V, f: 100 * float(np.mean([bool(f(c)) for c in V])) if V else 0.0
    mean = lambda V, f: float(np.mean([f(c) for c in V if f(c) is not None] or [0.0]))
    link = lambda c: f"{' v '.join(M[c['rid']]['teams'])}, {M[c['rid']]['map']}, {M[c['rid']]['date']}, {cl(M[c['rid']]['length_s'] or 0)} long, {c['team']} at {cl(c['t'])}: https://gvg.report/report/{c['rid']}#map"
    pr(f"The hand-off and the flag returned (R-620), on {len(M)} matches: {len(lives)} flag lives, {len(puts)} times a flag was put down, {len(holds)} held flags" + "".join(f"; set aside, {k}: {v}" for k, v in skipped.most_common() if v))
    pr("A flag put down goes back only when an enemy player picks it up (R-622). In range = a living enemy player within an aggro bubble of the flag as it is put down (R-623).")
    # ---- A. the record
    live = [c for c in puts if not c["dead"]]
    pr(f"\nA. Every put-down, by what became of the flag. {len(puts) - len(live)} are a carrier who died with it; the rest ({len(live)}) were put down by a living player.")
    pr(f"     {'':44} {'all':>6}  {'out of range':>12}  {'one in range':>12}  {'two or more':>11}")
    for th in ("a team mate took it up", "its carrier took it up again", "returned", "left lying"):
        V = [c for c in live if c["then"] == th]
        res["record"][th] = {"all": len(V), "out of range": sum(1 for c in V if c["enemy_near"] == 0), "one in range": sum(1 for c in V if c["enemy_near"] == 1), "two or more": sum(1 for c in V if c["enemy_near"] >= 2)}
        pr(f"     {th:44} {len(V):6}  {res['record'][th]['out of range']:12}  {res['record'][th]['one in range']:12}  {res['record'][th]['two or more']:11}")
    for lab, f in (("out of range", lambda c: c["enemy_near"] == 0), ("one enemy player in range", lambda c: c["enemy_near"] == 1), ("two or more in range", lambda c: c["enemy_near"] >= 2)):
        V = [c for c in live if f(c)]; res["record"]["returned, " + lab] = {"put-downs": len(V), "returned": pct(V, lambda c: c["returned"])}
        pr(f"     returned, of the flags put down {lab}: {pct(V, lambda c: c['returned']):.0f}% of {len(V)}")
    rd = lambda C_, *a, **k: _reading(pr, res, C_, *a, **k)
    pr("   The readings:")
    rd(live, "X1 a flag put down with an enemy player in range is returned more often than one put down out of range", lambda c: c["in_range"], lambda c: True, +1, lambda c: c["returned"], "in range", "out of range")
    rd(live, "X2 ... and more often with two or more in range than with one", lambda c: c["enemy_near"] >= 2, lambda c: c["enemy_near"] == 1, +1, lambda c: c["returned"], "two or more", "one")
    rd([c for c in live if c["in_range"]], "X3 in range, a flag put down by a frontliner is returned more often than one put down by a midline player", lambda c: c["by_line"] == "frontline", lambda c: c["by_line"] == "midline", +1, lambda c: c["returned"], "a frontliner", "a midline player")
    # ---- B. the hand-off returned, against the flag that lay and was returned later (R-626)
    hand = [c for c in live if c["handoff"]]
    for c in hand: c["fate"] = "returned within 15 s" if c["returned_soon"] else "returned later" if c["returned"] else "a team mate took it up" if c["then"] == "a team mate took it up" else "its carrier took it up again" if c["then"] == "its carrier took it up again" else "left lying"
    soon = [c for c in live if c["returned_soon"]]
    pr(f"\nB. A hand-off returned, against a flag that lay and was returned later (R-626: \"contested v uncontested\"). A hand-off = a living player puts the flag down with a team mate within an aggro bubble of it")
    pr(f"   ({len(hand)} of the {len(live)} put-downs; Claude's draft of the word). Returned within 15 s = returned, with an enemy player standing on the flag within 15 s of the put-down: the second of a return is an")
    pr(f"   estimate until the rebuild (R-481); of {len(soon)} such returns {sum(1 for c in soon if c['returned_soon_sure'])} are certain on the latest second it can have gone back too. On RJT v RACK the estimate has all four known returns right.")
    pr("   1. Every returned flag, by how long it lay before an enemy player first stood on it (flags = the change in the tally of R-408 from the put-down; the boost and the player sent back are in the tally):")
    pr(f"     {'':44} {'returns':>7}  {'started at':>10}  {'flags 60 s':>10}  {'flags 90 s':>10}  {'flags 180 s':>11}  {'win pts 180 s':>13}")
    lay = lambda c: c["first_enemy_s"] if c["first_enemy_s"] is not None else 1e9
    fl_ = lambda V, H: float(np.mean([c["hard"][H]["lead_change"] for c in V if c["hard"][H]["lead_change"] is not None] or [0.0]))
    res["price"]["by_lay"] = {}
    for lab, f in (("a hand-off, returned within 15 s", lambda c: c["handoff"] and c["returned_soon"]), ("no team mate by it, returned within 15 s", lambda c: not c["handoff"] and c["returned_soon"]),
                   ("it lay 15 s to 2 minutes first", lambda c: not c["returned_soon"] and lay(c) < 120), ("it lay 2 minutes or longer first", lambda c: not c["returned_soon"] and lay(c) >= 120)):
        V = [c for c in live if c["returned"] and f(c)]
        if not V: continue
        res["price"]["by_lay"][lab] = {"returns": len(V), "started at": 100 * mean(V, lambda c: c["p0"]), "flags 60": fl_(V, "60"), "flags 90": fl_(V, "90"), "flags 180": fl_(V, "180"), "win points 180": mean(V, lambda c: c["v"]["180"])}
        pr(f"     {lab:44} {len(V):7}  {100 * mean(V, lambda c: c['p0']):9.0f}%  {fl_(V, '60'):+10.2f}  {fl_(V, '90'):+10.2f}  {fl_(V, '180'):+11.2f}  {mean(V, lambda c: c['v']['180']):+13.1f}")
    pr("   2. What a returned hand-off costs in flags: the hand-offs returned within 15 s against the hand-offs a team mate took up, all of them and then only those with an enemy player in range,")
    pr("      where the two stand in the same danger (90% range over whole matches):")
    for lab, V in (("every hand-off", hand), ("hand-offs with an enemy player in range", [c for c in hand if c["in_range"]])):
        o = res["price"][lab] = {"hand-offs": len(V), "returned within 15 s": sum(1 for c in V if c["fate"] == "returned within 15 s"), "a team mate took it up": sum(1 for c in V if c["fate"] == "a team mate took it up")}
        for H in HORIZONS:
            for c in V: c["_y"] = c["hard"][H]["lead_change"] if c["hard"][H]["lead_change"] is not None else 0.0
            d_, lo, hi, na, nb = _num_range(V, lambda c: c["fate"] == "returned within 15 s", lambda c: c["fate"] == "a team mate took it up")
            if d_ is None: continue
            o[f"flags {H}"] = {"difference": float(d_), "range": [float(lo), float(hi)], "n": [na, nb]}
            pr(f"     {lab}, {H} s on: {d_:+.2f} of a flag ({lo:+.2f} to {hi:+.2f}), {na} returned against {nb} taken up" + ("   (under the floor)" if min(na, nb) < MIN_PLAYS else ""))
        for c in V: c["_y"] = c["v"]["180"]
        d_, lo, hi, na, nb = _num_range(V, lambda c: c["fate"] == "returned within 15 s", lambda c: c["fate"] == "a team mate took it up")
        if d_ is not None:
            o["win points 180"] = {"difference": float(d_), "range": [float(lo), float(hi)]}
            pr(f"     ... and in the chance of winning three minutes on: {d_:+.1f} points ({lo:+.1f} to {hi:+.1f}); started at {100 * mean([c for c in V if c['fate'] == 'returned within 15 s'], lambda c: c['p0']):.0f}% against {100 * mean([c for c in V if c['fate'] == 'a team mate took it up'], lambda c: c['p0']):.0f}%")
    pr("   3. His truth (T13, R-629: \"A hand-off with at least one enemy player in aggro bubble gets returned more often in the next 15s than a hand-off that is at least 1.5-2 aggro bubbles away from enemy\"):")
    far = lambda k: (lambda c: c["nearest"] is None or c["nearest"] >= k * 1000)
    rd(hand, "X4 a hand-off with an enemy player within an aggro bubble is returned within 15 s more often than one 1.5 bubbles or more from the enemy", lambda c: c["in_range"], far(1.5), +1, lambda c: c["returned_soon"], "in the bubble", "1.5 bubbles or more")
    rd(hand, "X5 ... and than one 2 bubbles or more from the enemy", lambda c: c["in_range"], far(2.0), +1, lambda c: c["returned_soon"], "in the bubble", "2 bubbles or more")
    res["record"]["hand-offs by what became of them"] = dict(collections.Counter(c["fate"] for c in hand))
    pr("     the hand-offs, by what became of them: " + ", ".join(f"{k} {v}" for k, v in collections.Counter(c["fate"] for c in hand).most_common()))
    # ---- C. his first point
    later = [c for c in lives if not c["first_flag"]]
    Fr = [c for c in later if c["runner_line"] == "frontline"]
    def how_run(c):
        a = c["arrive"]
        if a is None: return "never stood at the stand"
        return "run to the stand on the frontliner" if a["line"] == "frontline" else "handed on before the stand"
    for c in Fr: c["run"] = how_run(c)
    RUNS = ("run to the stand on the frontliner", "handed on before the stand", "never stood at the stand")
    pr(f"\nC. His first point (tactics F52): a flag run on a frontliner, by whether he runs it all the way to the stand or hands it to a midline player before the stand. Flags after the first, {len(Fr)} run by a frontliner")
    pr(f"   of {len(later)}. Up on flags is read as his case of it: we hold the stand at the pickup, so the flag cannot be capped until they cap (they \"can just hold the flag and you are a man down\"). Read from the")
    pr("   pickup; capped in = seconds from the pickup to the cap (middle); on him = seconds the first carrier at the stand stood there with it (middle); handed there = it changed hands after it reached the stand.")
    extra = (("capped", lambda V: pct(V, lambda c: c["captured"]), lambda v: f"{v:5.0f}%"), ("returned", lambda V: pct(V, lambda c: c["returned"]), lambda v: f"{v:7.0f}%"),
             ("capped in", lambda V: float(np.median([c["cap_s"] for c in V if c["cap_s"] is not None] or [0])), lambda v: f"{v:7.0f} s"),
             ("on him", lambda V: float(np.median([c["stood_s"] for c in V if c["stood_s"] is not None] or [0])), lambda v: f"{v:4.0f} s"), ("handed there", lambda V: pct(V, lambda c: c["handed_at_stand"]), lambda v: f"{v:11.0f}%"))
    head = _fell_head((("capped", 6), ("returned", 8), ("capped in", 9), ("on him", 6), ("handed there", 12)))
    for lab, f in (("we hold the stand at the pickup", lambda c: c["own_stand"]), ("we do not hold the stand", lambda c: not c["own_stand"])):
        X = [c for c in Fr if f(c)]; pr(f"\n   {lab} ({len(X)})"); pr(head); o = res["frontliner"][lab] = {}
        for r_ in RUNS: _fell(pr, o, r_, [c for c in X if c["run"] == r_], extra)
    up = [c for c in Fr if c["own_stand"] and c["run"] != RUNS[2]]
    pr("   The readings (we hold the stand, the flags that came to stand in hand at the stand):")
    rd(up, "C1 with the stand ours, a flag run to the stand on the frontliner is returned more often than one handed on before it", lambda c: c["run"] == RUNS[0], lambda c: True, +1, lambda c: c["returned"], "on the frontliner", "handed on")
    rd(up, "C2 ... the team loses a player in the 90 s more often", lambda c: c["run"] == RUNS[0], lambda c: True, +1, lambda c: c["hard"]["90"]["deaths"][0] > 0, "on the frontliner", "handed on")
    rd(up, "C3 ... is worse off in flags 90 s on", lambda c: c["run"] == RUNS[0], lambda c: True, -1, lambda c: c["hard"]["90"]["lead_change"] or 0.0, "on the frontliner", "handed on", unit=" flags")
    rd(up, "C4 ... and in the chance of winning three minutes on", lambda c: c["run"] == RUNS[0], lambda c: True, -1, lambda c: c["v"]["180"], "on the frontliner", "handed on", unit=" points")
    hp = [c for c in live if not c["first_flag"] and c["by_line"] == "frontline" and c["then"] in ("a team mate took it up", "returned") and c["taker_line"] != "frontline"]
    pr(f"   Where a frontliner hands a later flag on (or loses it trying): {len(hp)} put-downs. Before the stand, out of range: returned {pct([c for c in hp if c['before_stand'] and not c['in_range']], lambda c: c['returned']):.0f}% of {sum(1 for c in hp if c['before_stand'] and not c['in_range'])};"
       f" before the stand, in range: {pct([c for c in hp if c['before_stand'] and c['in_range']], lambda c: c['returned']):.0f}% of {sum(1 for c in hp if c['before_stand'] and c['in_range'])};"
       f" at the stand, in range: {pct([c for c in hp if not c['before_stand'] and c['in_range']], lambda c: c['returned']):.0f}% of {sum(1 for c in hp if not c['before_stand'] and c['in_range'])}.")
    res["frontliner"]["hand-offs"] = {"put-downs": len(hp), "before the stand, out of range": [sum(1 for c in hp if c["before_stand"] and not c["in_range"]), pct([c for c in hp if c["before_stand"] and not c["in_range"]], lambda c: c["returned"])],
                                      "before the stand, in range": [sum(1 for c in hp if c["before_stand"] and c["in_range"]), pct([c for c in hp if c["before_stand"] and c["in_range"]], lambda c: c["returned"])],
                                      "at the stand, in range": [sum(1 for c in hp if not c["before_stand"] and c["in_range"]), pct([c for c in hp if not c["before_stand"] and c["in_range"]], lambda c: c["returned"])]}
    # ---- D. his second point
    opens = {(p["rid"], p["tm"]): p for p in D["plays"] if p["play"] == "opening"}
    firsts = [c for c in lives if c["first_flag"] and (c["rid"], c["tm"]) in opens]
    for c in firsts:
        o = opens[(c["rid"], c["tm"])]["open"]; th = o["their"]
        c["eight_v_seven"] = o["stand"] == 8 and th["stand"] == 7 and th["back"] + th["waits"] >= 1 and not o["split"] and not th["split"]
        played = [x for x in c["carriers"] if x[3] is None or x[3] > 0]
        c["kept"] = "kept on the frontliner" if all(x[1] == "frontline" for x in played) else "handed to a midline player or a monk"
        lt = o["later"]["300"]
        c["flags_5"] = None if lt["ended"] else lt["lead"][0]; c["net_kills_5"] = lt["deaths"][1] - lt["deaths"][0]
    Ff = [c for c in firsts if c["runner_line"] == "frontline"]
    pr(f"\nD. His second point (tactics F53): at the opening, a first flag that came up on a frontliner, kept on him or handed to a midline player. {len(Ff)} first flags came up on a frontliner, of {len(firsts)}.")
    pr("   Eight against seven = we have eight at the stand and they seven with their eighth back at home or waiting for the next flag, no split on either side. flags 5:00 = the tally at 5:00;")
    pr("   net kills 5:00 = theirs dead less ours by 5:00.")
    def orow(lab, V, into):
        into[lab] = row = {"openings": len(V), "matches": len({c["rid"] for c in V}), "capped": pct(V, lambda c: c["captured"]), "returned": pct(V, lambda c: c["returned"]), "flags 5:00": mean(V, lambda c: c["flags_5"]), "net kills 5:00": mean(V, lambda c: c["net_kills_5"]),
                           "win points 180": mean(V, lambda c: c["v"]["180"])}
        if not V: pr(f"     {lab:52} {0:5}"); return
        pr(f"     {lab:52} {len(V):5}  capped {row['capped']:3.0f}%  returned {row['returned']:3.0f}%  flags 5:00 {row['flags 5:00']:+5.2f}  net kills 5:00 {row['net kills 5:00']:+5.2f}  win pts 180 s {row['win points 180']:+5.1f}" + ("   (under the floor)" if len(V) < MIN_PLAYS else ""))
    for lab, f in (("eight against seven", lambda c: c["eight_v_seven"]), ("every other opening", lambda c: not c["eight_v_seven"])):
        X = [c for c in Ff if f(c)]; pr(f"   {lab} ({len(X)})"); o = res["opening"][lab] = {}
        for k in ("kept on the frontliner", "handed to a midline player or a monk"): orow(k, [c for c in X if c["kept"] == k], o)
    oh = [c for c in live if c["first_flag"] and c["by_line"] == "frontline" and c["then"] in ("a team mate took it up", "returned")]
    res["opening"]["hand-offs"] = {"out of range": [sum(1 for c in oh if not c["in_range"]), pct([c for c in oh if not c["in_range"]], lambda c: c["returned"])], "in range": [sum(1 for c in oh if c["in_range"]), pct([c for c in oh if c["in_range"]], lambda c: c["returned"])]}
    pr(f"   A frontliner's put-downs of a first flag ({len(oh)}): out of range, returned {res['opening']['hand-offs']['out of range'][1]:.0f}% of {res['opening']['hand-offs']['out of range'][0]}; in range, returned {res['opening']['hand-offs']['in range'][1]:.0f}% of {res['opening']['hand-offs']['in range'][0]}.")
    pr("   The readings (first flags that came up on a frontliner):")
    rd(Ff, "D1 a first flag kept on the frontliner is returned more often than one handed on", lambda c: c["kept"] == "kept on the frontliner", lambda c: True, +1, lambda c: c["returned"], "kept", "handed on")
    rd([c for c in Ff if c["eight_v_seven"]], "D2 eight against seven, a first flag kept on the frontliner leaves the team worse off in flags at 5:00", lambda c: c["kept"] == "kept on the frontliner", lambda c: True, -1, lambda c: c["flags_5"] or 0.0, "kept", "handed on", unit=" flags")
    rd(oh, "D3 a frontliner's first flag put down in range is returned more often than one put down out of range", lambda c: c["in_range"], lambda c: True, +1, lambda c: c["returned"], "in range", "out of range")
    # ---- E. his third point
    pr(f"\nE. His third point (tactics F54): who holds a held flag. {len(holds)} flags stood in hand at the stand 15 s or longer before they were capped, read from the second the hold began; the holder is the")
    pr("   player who capped it, named by build (R-624). next flag = seconds from the cap to the team's next pickup (middle); NPCs lost = the team's own, anywhere, in the three minutes from the hold;")
    pr("   holder runs next = the holder himself takes the next flag.")
    extra = (("held s", lambda V: float(np.median([c["held_s"] for c in V])), lambda v: f"{v:6.0f}"), ("next flag", lambda V: float(np.median([c["next_s"] for c in V if c["next_s"] is not None] or [0])), lambda v: f"{v:7.0f} s"),
             ("NPCs lost", lambda V: mean(V, lambda c: c["npcs_lost"]), lambda v: f"{v:9.2f}"), ("holder runs next", lambda V: pct(V, lambda c: c["holder_runs_next"]), lambda v: f"{v:15.0f}%"))
    pr(_fell_head((("held s", 6), ("next flag", 9), ("NPCs lost", 9), ("holder runs next", 16))))
    o = res["holding"]["by group"] = {}
    for g_ in HOLD_GROUPS: _fell(pr, o, "held on " + g_, [c for c in holds if c["group"] == g_], extra)
    pr("   By the holder's build:")
    o = res["holding"]["by build"] = {}
    for role, n in collections.Counter(_stem(c["holder"] or "?") for c in holds).most_common(12):
        _fell(pr, o, role, [c for c in holds if _stem(c["holder"] or "?") == role], extra)
    pr("   The readings:")
    rd(holds, "E1 a flag held on the Mes/A costs more NPCs in the three minutes from the hold than one held on the stand mesmer", lambda c: c["group"] == HOLD_GROUPS[1], lambda c: c["group"] == HOLD_GROUPS[0], +1, lambda c: c["npcs_lost"], "the Mes/A", "the stand mesmer", unit=" NPCs")
    rd(holds, "E2 a flag held on a frontliner leaves the team worse off three minutes on than one held on a midline player", lambda c: c["group"] == HOLD_GROUPS[3], lambda c: c["group"] in HOLD_GROUPS[:3], -1, lambda c: c["v"]["180"], "a frontliner", "a midline player", unit=" points")
    # ---- moments to look at
    pr("\nF. To look at: flags a frontliner put down in range that were returned (the time is the put-down)")
    look = sorted([c for c in live if c["returned"] and c["in_range"] and c["by_line"] == "frontline"], key=lambda c: (M[c["rid"]]["date"], c["t"]))
    res["look"] = [{"rid": c["rid"], "team": c["team"], "t": c["t"], "by": c["by"], "place": c["place"], "enemy_near": c["enemy_near"], "first_flag": c["first_flag"]} for c in look]
    for c in look[-12:]: pr(f"     {link(c)}   {c['by']} puts it down at {c['place']}, {c['enemy_near']} in range" + (" (the first flag)" if c["first_flag"] else ""))
    if out_json: json.dump(res, open(out_json, "w"), indent=1, default=lambda x: float(x) if isinstance(x, (np.floating, np.integer)) else str(x))
    return res


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "test": report(a[1], a[a.index("--json") + 1] if "--json" in a else None)
    elif len(a) >= 4 and a[0] == "case": case(a[1], a[2], a[3])
    elif len(a) >= 2 and a[0] == "cards": cards(a[1], a[2] if len(a) > 2 and not a[2].startswith("--") else "f1", a[a.index("--json") + 1] if "--json" in a else None, a[a.index("--site") + 1] if "--site" in a else None)
    elif len(a) >= 2 and a[0] == "ladder": ladder(a[1], a[a.index("--json") + 1] if "--json" in a else None)
    elif len(a) >= 2 and a[0] == "numbers": numbers(a[1], a[a.index("--json") + 1] if "--json" in a else None)
    elif len(a) >= 2 and a[0] == "main-fight": main_fight(a[1], a[a.index("--json") + 1] if "--json" in a else None)
    elif len(a) >= 2 and a[0] == "splits": splits(a[1], a[a.index("--json") + 1] if "--json" in a else None)
    elif len(a) >= 2 and a[0] == "pushes": pushes(a[1], a[a.index("--json") + 1] if "--json" in a else None)
    elif len(a) >= 2 and a[0] == "held": held(a[1], a[a.index("--json") + 1] if "--json" in a else None)
    elif len(a) >= 2 and a[0] == "handoff": handoff(a[1], a[a.index("--json") + 1] if "--json" in a else None)
    elif len(a) >= 2 and a[0] == "res": base_res(a[1], a[a.index("--json") + 1] if "--json" in a else None)
    elif len(a) >= 2 and a[0] == "opening": opening_report(a[1], a[a.index("--json") + 1] if "--json" in a else None)
    elif len(a) >= 2 and a[0] == "numbers-cards": numbers_cards(a[1], a[2] if len(a) > 2 and not a[2].startswith("--") else "f1", a[a.index("--site") + 1] if "--site" in a else None)
    else: print(__doc__)
