"""Lineup strength: how strong the eight players who actually played were, not only their guild (substitutes and new
rosters change a team; Denning).

From every stored match result (data/matches/*.json: character names, teams, result, event), in time order:
- characters are grouped into people with Denning's Players-page assignments (data/aliases.json); others stay as
  characters;
- each person has an Elo-style rating, moved after every match by how the result compared with what both lineups'
  average ratings expected (opponent-adjusted, so beating strong teams counts more than a raw win rate);
- MAT results count MAT_WEIGHT times as much as other results (Denning: MAT is the better test). MAT_WEIGHT and the
  step size K are not chosen by hand: the pair that best predicts LATER results (log loss on matches after the first
  WARMUP) is used, from the grid below, and the whole grid is saved so the choice can be checked;
- a match's lineup gap uses only ratings from before it, so its own result never leaks in;
- also kept for comparison: each person's shrunk win rate (MAT weighted the same way), averaged per lineup.

Output: data/model/lineup.json (chosen K and MAT weight, the grid, prediction quality, ratings per person).
Usage:  python3 lineup.py                 fit and write
In code: lineup_gaps() -> {match id: gap in rating points from the first team's side}; gap_for(names_a, names_b, at)."""
import collections, glob, json, math, os, sys
from common import REPO

OUT = os.path.join(REPO, "data", "model", "lineup.json")
WARMUP = 300
K_GRID = (8, 16, 32, 48, 64, 96, 128)
MAT_GRID = (1, 1.5, 2, 3, 4, 6, 8)
SCALES = (0.5, 0.75, 1, 1.5, 2, 3, 4, 6, 8, 12)
SCALE = 400 / math.log(10)
PRIOR_GAMES = 10            # shrinkage for the win-rate comparison (a definition, not a value: shown with the grid)


def people_map():
    try: p = json.load(open(os.path.join(REPO, "data", "aliases.json")))["people"]
    except (OSError, ValueError, KeyError): return {}
    return {c: person for person, chars in p.items() for c in chars}


def load():
    pm, rows = people_map(), []
    for f in sorted(glob.glob(os.path.join(REPO, "data", "matches", "2*.json"))):
        for r in json.load(open(f)):
            t = r.get("teams") or []
            if len(t) != 2 or r.get("winner") not in (1, 2): continue
            side = {t[0]["id"]: 0, t[1]["id"]: 1}
            names = ([], [])
            for p in r.get("players", []):
                if p.get("team") in side and p.get("n"): names[side[p["team"]]].append(pm.get(p["n"], p["n"]))
            if not names[0] or not names[1]: continue
            rows.append({"id": r["id"], "at": r.get("at") or 0, "mat": r.get("occ") == "MAT", "a": names[0], "b": names[1],
                         "a_won": r["winner"] == t[0]["id"]})
    return sorted(rows, key=lambda r: r["at"])


def run(rows, K, mat_w, until_at=None):
    """One pass in time order. Returns ({match id: pre-match gap (points, first team's side)}, ratings, record)."""
    R = collections.defaultdict(float)
    rec = collections.defaultdict(lambda: [0.0, 0.0])          # weighted wins, weighted games
    gaps, wr = {}, {}
    for r in rows:
        if until_at is not None and r["at"] >= until_at: break
        ra = sum(R[p] for p in r["a"]) / len(r["a"]); rb = sum(R[p] for p in r["b"]) / len(r["b"])
        gaps[r["id"]] = ra - rb
        wr_a = sum((rec[p][0] + PRIOR_GAMES / 2) / (rec[p][1] + PRIOR_GAMES) for p in r["a"]) / len(r["a"])
        wr_b = sum((rec[p][0] + PRIOR_GAMES / 2) / (rec[p][1] + PRIOR_GAMES) for p in r["b"]) / len(r["b"])
        wr[r["id"]] = wr_a - wr_b
        e = 1 / (1 + 10 ** (-(ra - rb) / 400)); y = 1.0 if r["a_won"] else 0.0
        w = mat_w if r["mat"] else 1.0
        for p in r["a"]: R[p] += K * w * (y - e)
        for p in r["b"]: R[p] -= K * w * (y - e)
        for p in r["a"]: rec[p][0] += w * y; rec[p][1] += w
        for p in r["b"]: rec[p][0] += w * (1 - y); rec[p][1] += w
    return gaps, R, rec, wr


def _ll(rows, gap_of, scale=1.0, only=None):
    ll = acc = n = 0
    for r in rows[WARMUP:]:
        if only == "mat" and not r["mat"]: continue
        g = gap_of(r["id"])
        if g is None: continue
        p = min(max(1 / (1 + 10 ** (-g * scale / 400)), 0.02), 0.98); y = 1 if r["a_won"] else 0
        ll += -(y * math.log(p) + (1 - y) * math.log(1 - p)); acc += (p > 0.5) == bool(y); n += 1
    return {"log_loss": round(ll / n, 4), "accuracy": round(acc / n, 3), "matches": n}


def _best_scale(rows, gap_of):
    """Each measure on its best scale (ratings and win rates aren't on the 400-points scale by themselves); also
    scored on later MAT matches alone."""
    b = min(({"scale": s, **_ll(rows, gap_of, s)} for s in SCALES), key=lambda v: v["log_loss"])
    b["on_mat_matches"] = _ll(rows, gap_of, b["scale"], only="mat")
    return b


def fit():
    rows = load()
    grid = {}
    for K in K_GRID:
        for w in MAT_GRID:
            g, *_ = run(rows, K, w)
            grid[f"K{K} MAT x{w}"] = dict(_best_scale(rows, g.get), K=K, mat_weight=w)
    wr_grid = {}
    for w in MAT_GRID:
        wr = run(rows, 16, w)[3]
        wr_grid[f"MAT x{w}"] = dict(_best_scale(rows, lambda i, wr=wr: wr.get(i) * 400), mat_weight=w)
    best_r = min(grid.values(), key=lambda v: v["log_loss"])
    best_w = min(wr_grid.values(), key=lambda v: v["log_loss"])
    # the measure used is whichever predicts later results better: an opponent-adjusted rating or a shrunk win rate
    measure = "rating" if best_r["log_loss"] <= best_w["log_loss"] else "win_rate"
    best = best_r if measure == "rating" else dict(best_w, K=16)
    gaps, R, rec, wr = run(rows, best["K"], best["mat_weight"])
    played = collections.Counter(p for r in rows for p in r["a"] + r["b"])
    out = {"about": __doc__.split("\n\n")[1].strip(), "matches": len(rows), "chosen": {"measure": measure, "K": best["K"], "mat_weight": best["mat_weight"], "scale": best["scale"]},
           "prediction": {"lineup rating": best_r, "lineup win rate": best_w},
           "grid": {"rating": grid, "win_rate": wr_grid},
           "people": {p: {"rating": round(v), "matches": played[p], "win_rate_weighted": round(rec[p][0] / rec[p][1], 3) if rec[p][1] else None}
                      for p, v in sorted(R.items(), key=lambda kv: -kv[1]) if played[p] >= 10}}
    json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
    return out


_C = {}
def chosen():
    if "c" not in _C:
        try: _C["c"] = json.load(open(OUT))["chosen"]
        except (OSError, ValueError, KeyError): _C["c"] = {"K": 16, "mat_weight": 1}
    return _C["c"]


def _to_points(c, g, wr):
    """The chosen measure as a gap in rating points (400 = 10 to 1 odds), on its fitted scale."""
    return g * c["scale"] if c.get("measure", "rating") == "rating" else wr * 400 * c["scale"]


def lineup_gaps():
    if "gaps" not in _C:
        c = chosen(); _C["rows"] = load(); g, _, _, wr = run(_C["rows"], c["K"], c["mat_weight"])
        _C["gaps"] = {i: _to_points(c, g[i], wr[i]) for i in g}
    return _C["gaps"]


def gap_for(names_a, names_b, at):
    """Lineup gap for a match not among the stored results (e.g. a newer replay), from ratings before time at."""
    c = chosen(); pm = people_map()
    rows = _C.get("rows") or load()
    _, R, rec, _ = run(rows, c["K"], c["mat_weight"], until_at=at)
    if not names_a or not names_b: return None
    A = [pm.get(n, n) for n in names_a]; B = [pm.get(n, n) for n in names_b]
    g = sum(R.get(p, 0.0) for p in A) / len(A) - sum(R.get(p, 0.0) for p in B) / len(B)
    wrate = lambda p: (rec[p][0] + PRIOR_GAMES / 2) / (rec[p][1] + PRIOR_GAMES) if p in rec else 0.5
    wr = sum(wrate(p) for p in A) / len(A) - sum(wrate(p) for p in B) / len(B)
    return _to_points(c, g, wr)


if __name__ == "__main__":
    o = fit()
    print(o["matches"], "matches; chosen", o["chosen"])
    print("prediction:", o["prediction"])
    print("top:", list(o["people"].items())[:10])
