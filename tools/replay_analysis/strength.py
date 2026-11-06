"""Team strength: how strong each guild is, so the model can tell "good teams do X" apart from "X wins".

Two measures, both from every stored match result (data/matches/*.json, far more matches than the replays):
- ladder: each guild's in-game rating at the time of the match, as gvg.report recorded it;
- fitted: a Bradley-Terry rating fitted on results only (each match weighs less the older it is, half-life HALF_LIFE
  days), on the same scale as the ladder (400 points = 10 to 1 odds). Fitted ratings use only matches before the one
  being rated, so a match's own result never leaks into the strength gap the model sees.
The report compares how well each predicts results (log loss, accuracy) so the better one is chosen by data.
- lineup: the eight players who actually played (lineup.py: each person's MAT-weighted record, time ordered).
- elo: gvg.report's guild Elo (tournament-elo.v2: start 1500, K 32, scale 400; after 21 days without a match, -50 every
  7 days down to 1500), rebuilt here match by match from the stored results so each match sees only the Elo from
  before it (gvg.report's own table is today's and would leak later results). The rebuild is checked against
  gvg.report's table (data/gvgreport/elo.json) when it has been synced. Denning: much more accurate than the ladder.
The model's baseline is the blend: a logistic fit of results on the three gaps (no intercept: a mirrored match must
give the mirrored answer), trained on earlier matches and tested on the latest third, so how much each measure counts
is measured. Replay matches are left out of the blend's fit.

Usage:  python3 strength.py            -> data/model/strength.json (ratings per guild with matches behind them) and
                                          the comparison printed
In code: strength_gap(match_id, team_tag, ...) -> (ladder gap, blended gap) for that match, from the team's side;
         components(...) -> the three gaps separately."""
import collections, glob, json, math, os, sys
from common import REPO

HALF_LIFE = 60            # days
OUT = os.path.join(REPO, "data", "model")
K = 400 / math.log(10)    # rating points per unit of log odds


ELO = {"start": 1500, "k": 32, "scale": 400, "inactive_days": 21, "decay_every_days": 7, "decay": 50, "floor": 1500}
ELO_EVENTS = ("AT-A", "AT-B", "AT-C", "MAT")      # tournament matches (gvg.report rates tournaments)


def elo_run(rows, events=ELO_EVENTS):
    """gvg.report's Elo rebuilt in time order: {match id: pre-match gap (a minus b)}, final {guild: elo}."""
    R, last, gaps = {}, {}, {}
    day = 86400000
    def cur(g, at):
        r = R.get(g, ELO["start"])
        if g in last and r > ELO["floor"]:
            idle = (at - last[g]) / day - ELO["inactive_days"]
            if idle > 0: r = max(ELO["floor"], r - ELO["decay"] * (int(idle // ELO["decay_every_days"]) + 1))
        return r
    for r in rows:
        ra, rb = cur(r["a"], r["at"]), cur(r["b"], r["at"])
        gaps[r["id"]] = ra - rb
        if events and r.get("occ") not in events: continue
        e = 1 / (1 + 10 ** (-(ra - rb) / ELO["scale"])); y = 1.0 if r["a_won"] else 0.0
        R[r["a"]] = ra + ELO["k"] * (y - e); R[r["b"]] = rb - ELO["k"] * (y - e)
        last[r["a"]] = last[r["b"]] = r["at"]
    end = max((r["at"] for r in rows), default=0)
    return gaps, {g: round(cur(g, end)) for g in R}


def elo_check(rows):
    """The rebuild against gvg.report's current table (by guild tag): mean absolute difference, and the event set that
    reproduces it best (tournaments only, or every stored match)."""
    try: tab = {x["tag"]: x["elo"] for x in json.load(open(os.path.join(REPO, "data", "gvgreport", "elo.json")))["rows"] if x.get("tag")}
    except (OSError, ValueError, KeyError): return None
    out = {}
    for name, ev in (("tournaments", ELO_EVENTS), ("all stored", None)):
        _, fin = elo_run(rows, ev)
        both = [g for g in tab if g in fin]
        out[name] = {"guilds": len(both), "mean_abs_diff": round(sum(abs(tab[g] - fin[g]) for g in both) / max(len(both), 1), 1)}
    return out


def load():
    rows = []
    for f in sorted(glob.glob(os.path.join(REPO, "data", "matches", "2*.json"))):
        for r in json.load(open(f)):
            t = r.get("teams") or []
            if len(t) != 2 or r.get("winner") not in (1, 2): continue
            rows.append({"id": r["id"], "at": r.get("at") or 0, "date": r.get("date"),
                         "a": t[0]["tag"] or t[0]["guild"], "b": t[1]["tag"] or t[1]["guild"],
                         "ra": t[0].get("rating"), "rb": t[1].get("rating"), "a_won": r["winner"] == t[0]["id"], "occ": r.get("occ")})
    return sorted(rows, key=lambda r: r["at"])


def fit(rows, until_at=None, iters=60):
    """Bradley-Terry by simple gradient steps on time-weighted results before until_at."""
    use = [r for r in rows if until_at is None or r["at"] < until_at]
    if not use: return {}
    last = until_at or max(r["at"] for r in use)
    w = lambda r: 0.5 ** ((last - r["at"]) / 86400000 / HALF_LIFE)
    s = collections.defaultdict(float)
    for _ in range(iters):
        g = collections.defaultdict(float); h = collections.defaultdict(float)
        for r in use:
            p = 1 / (1 + math.exp(-(s[r["a"]] - s[r["b"]])))
            e = (1.0 if r["a_won"] else 0.0) - p
            ww = w(r)
            g[r["a"]] += ww * e; g[r["b"]] -= ww * e
            h[r["a"]] += ww * p * (1 - p); h[r["b"]] += ww * p * (1 - p)
        for k in list(g):
            s[k] += g[k] / (h[k] + 1.0)        # +1: pulls guilds with few matches toward average
    return {k: v * K for k, v in s.items()}


_CACHE = {}
def _fitted_gap(match_id, tag, at=None, opp=None, ratings=None):
    """(ladder gap, fitted gap) from tag's side for one match. A match not among the stored results (e.g. a replay newer
    than the last results update) is rated from every result before its time `at` (ms), against `opp`; the ladder
    gap then comes from `ratings` ({tag: ladder rating} from the replay) if given."""
    if "rows" not in _CACHE:
        _CACHE["rows"] = load(); _CACHE["by_id"] = {r["id"]: r for r in _CACHE["rows"]}
    r = _CACHE["by_id"].get(match_id)
    if not r:
        if at is None or opp is None: return None, None
        if at not in _CACHE: _CACHE[at] = fit(_CACHE["rows"], at)
        f = _CACHE[at]
        lad = (ratings[tag] - ratings[opp]) if ratings and ratings.get(tag) is not None and ratings.get(opp) is not None else None
        if tag not in f or opp not in f: return lad, lad      # an unrated guild: use the ladder gap (same scale), never 0
        return lad, round(f[tag] - f[opp])
    if r["at"] not in _CACHE: _CACHE[r["at"]] = fit(_CACHE["rows"], r["at"])
    f = _CACHE[r["at"]]
    sign = 1 if tag == r["a"] else -1
    lad = (r["ra"] - r["rb"]) * sign if r["ra"] is not None and r["rb"] is not None else None
    if r["a"] not in f or r["b"] not in f: return lad, lad
    return lad, round((f[r["a"]] - f[r["b"]]) * sign)


def _blend():
    if "blend" not in _CACHE:
        try: _CACHE["blend"] = json.load(open(os.path.join(OUT, "strength.json")))["blend"]["coef"]
        except (OSError, ValueError, KeyError): _CACHE["blend"] = None
    return _CACHE["blend"]


def components(match_id, tag, at=None, opp=None, ratings=None, lineups=None):
    """{ladder, fitted, lineup} gaps in rating points from tag's side (None where unknown). lineups = {tag: [names]}
    for a match not among the stored results."""
    import lineup as LU
    lad, fit_g = _fitted_gap(match_id, tag, at, opp, ratings)
    g = LU.lineup_gaps().get(match_id)
    if g is not None:
        r = _CACHE["by_id"].get(match_id)
        lin = g if (r is None or tag == r["a"]) else -g
    elif lineups and opp in lineups and tag in lineups and at:
        lin = LU.gap_for(lineups[tag], lineups[opp], at)
    else: lin = None
    if "elo" not in _CACHE: _CACHE["elo"] = elo_run(_CACHE["rows"])[0]
    e = _CACHE["elo"].get(match_id)
    if e is not None:
        r = _CACHE["by_id"][match_id]; elo = e if tag == r["a"] else -e
    elif at and opp:
        _, fin = elo_run([x for x in _CACHE["rows"] if x["at"] < at])     # a newer match: Elo from every result before it
        elo = fin.get(tag, ELO["start"]) - fin.get(opp, ELO["start"])
    else: elo = None
    return {"ladder": lad, "fitted": fit_g, "lineup": lin, "elo": elo}


def strength_gap(match_id, tag, at=None, opp=None, ratings=None, lineups=None):
    """(ladder gap, blended gap): the blend of ladder, fitted and lineup gaps measured by blend(); before blend() has
    run, the fitted gap."""
    c = components(match_id, tag, at, opp, ratings, lineups)
    coef = _blend()
    if not coef or c["fitted"] is None: return c["ladder"], c["fitted"]
    x = {"ladder": c["ladder"] if c["ladder"] is not None else c["fitted"], "fitted": c["fitted"], "lineup": c["lineup"] or 0,
         "elo": c["elo"] or 0}
    from context import prior          # matchup, map and flux effects beyond strength (0 while switched off)
    return c["ladder"], round(sum(coef.get(k, 0) * x[k] for k in x) + prior(match_id, tag))


def blend(rows, replay_ids=()):
    """How much each measure counts in predicting a result, measured: logistic fits (no intercept) of results on each
    combination of the ladder, fitted, lineup and Elo gaps, trained on the earlier two thirds of the matches after the
    first 300 and tested on the latest third; the combination that predicts the latest third best is refitted on all
    of them. Replay matches are left out."""
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    import lineup as LU
    import itertools
    lg = LU.lineup_gaps(); eg = elo_run(rows)[0]
    use = [r for r in rows[300::2] if r["id"] not in replay_ids and r["id"] in lg]
    X, y = [], []
    for r in use:
        f = fit(rows, r["at"], iters=25)
        fg = f.get(r["a"], 0) - f.get(r["b"], 0)
        lad = (r["ra"] - r["rb"]) if r["ra"] is not None and r["rb"] is not None else fg
        X.append([lad / K, fg / K, lg[r["id"]] / K, eg[r["id"]] / K]); y.append(int(r["a_won"]))
    X, y = np.array(X), np.array(y)
    cut = int(len(y) * 2 / 3)
    names = ["ladder", "fitted", "lineup", "elo"]
    def score(cols):
        m = LogisticRegression(fit_intercept=False, C=1e6).fit(X[:cut][:, cols], y[:cut])
        p = np.clip(m.predict_proba(X[cut:][:, cols])[:, 1], 0.02, 0.98)
        yt = y[cut:]
        return {"log_loss": round(float(-np.mean(yt * np.log(p) + (1 - yt) * np.log(1 - p))), 4),
                "accuracy": round(float(np.mean((p > 0.5) == yt)), 3)}
    combos = {"+".join(names[i] for i in c): list(c) for n in range(1, 5) for c in itertools.combinations(range(4), n)}
    test = {k: score(c) for k, c in combos.items()}
    pick = min(test, key=lambda k: test[k]["log_loss"])            # the measures that predict the latest third best
    full = LogisticRegression(fit_intercept=False, C=1e6).fit(X[:, combos[pick]], y)
    coef = {n: 0.0 for n in names}
    coef.update({names[i]: round(float(v), 3) for i, v in zip(combos[pick], full.coef_[0])})
    return {"about": blend.__doc__.strip(), "chosen": pick, "train_matches": cut, "test_matches": len(y) - cut, "test": test, "coef": coef,
            "note": "coef: rating points of blended gap per point of each gap (1 = taken at face value)"}


def compare(rows):
    """How well each measure predicts results, on matches after the first 300 (fitted ratings use only earlier ones)."""
    out = {}
    test = rows[300::3]                      # every third later match, to keep the fits quick
    for name in ("ladder", "fitted"):
        ll = acc = n = 0
        for r in test:
            if name == "ladder":
                if r["ra"] is None or r["rb"] is None: continue
                gap = r["ra"] - r["rb"]
            else:
                f = fit(rows, r["at"], iters=25); gap = f.get(r["a"], 0) - f.get(r["b"], 0)
            p = 1 / (1 + 10 ** (-gap / 400)); p = min(max(p, 0.02), 0.98)
            y = 1 if r["a_won"] else 0
            ll += -(y * math.log(p) + (1 - y) * math.log(1 - p)); acc += (p > 0.5) == bool(y); n += 1
        out[name] = {"log_loss": round(ll / n, 3), "accuracy": round(acc / n, 3), "matches": n}
    out["coin flip"] = {"log_loss": round(math.log(2), 3), "accuracy": 0.5}
    return out


if __name__ == "__main__":
    rows = load()
    final = fit(rows)
    games = collections.Counter([r["a"] for r in rows] + [r["b"] for r in rows])
    cmp = compare(rows)
    rp = set(json.loads(__import__("subprocess").check_output(["git", "-C", REPO, "show", "origin/replays:index.json"]))["matches"])
    bl = blend(rows, rp)
    bl["elo_rebuild_check"] = elo_check(rows)
    print("blend:", bl["test"], bl["coef"], "elo check:", bl["elo_rebuild_check"])
    os.makedirs(OUT, exist_ok=True)
    json.dump({"about": __doc__.split("\n\n")[1].strip(), "matches": len(rows), "half_life_days": HALF_LIFE,
               "prediction": cmp, "blend": bl,
               "guilds": {g: {"fitted": round(v), "matches": games[g]} for g, v in sorted(final.items(), key=lambda kv: -kv[1])}},
              open(os.path.join(OUT, "strength.json"), "w"), indent=1, ensure_ascii=False)
    print(len(rows), "matches,", len(final), "guilds")
    print("prediction of results:", cmp)
    print("top:", [(g, round(v), games[g]) for g, v in sorted(final.items(), key=lambda kv: -kv[1])[:12]])
