"""Context priors from every stored result, not only replays: does a build matchup, a map or a flux favour one side
beyond what strength predicts? 1,700+ results are far more than the replays, so these effects can be measured now
instead of waiting for 60 replays (METHODS.md, "The causal model", context layer).

For every stored match: each team's archetype (scoreboard.archetype on the bars; a grouping label), the map and the
month's flux. Features are antisymmetric (a mirrored match gives the mirrored answer):
- matchup: +1 for (own archetype vs enemy archetype), -1 for the reverse pairing;
- map x archetype: +1 for the own archetype on this map, -1 for the enemy's;
- flux x archetype: the same per active flux.
A logistic fit with the strength gap as a fixed offset (so it only learns what strength doesn't explain), ridge
penalty chosen by time order: trained on earlier matches, tested on the latest third, against strength alone. If no
penalty beats strength alone on the latest third, the prior is switched off (all zero): it has to earn its place.
Replay matches are left out of the fit.

Output: data/model/context.json (the test, each effect in points with its matches, the chosen penalty).
Usage:  python3 context.py
In code: prior(match_id, tag) -> points to add to the strength gap (0 if off or unknown)."""
import collections, glob, json, math, os, subprocess
from common import REPO

OUT = os.path.join(REPO, "data", "model", "context.json")
K = 400 / math.log(10)
PENALTIES = (0.03, 0.1, 0.3, 1, 3)
MIN_CELL = 8                 # matches a feature needs before it can be used


class _Rec:
    """A stored match record shaped like replaylib.Match, enough for scoreboard.archetype."""
    _names = None
    def __init__(self, r):
        if _Rec._names is None: _Rec._names = _skill_names()
        self.A = [{"p": p.get("p"), "bar": p.get("bar") or [], "team": p.get("team")} for p in r.get("players", [])]
        self.PL = list(range(len(self.A)))
        self.roles = {i: a["p"] or "?" for i, a in enumerate(self.A)}
    def team(self, a): return self.A[a]["team"]
    def sk(self, s): return _Rec._names.get(s, str(s))


def _skill_names():
    d = json.load(open(os.path.join(REPO, "data", "skills.json")))
    rows = d["skills"] if isinstance(d, dict) and "skills" in d else d
    rows = list(rows.values()) if isinstance(rows, dict) else rows
    names = {s["id"]: s["name"].replace(" (PvP)", " PvP") for s in rows}
    try:
        tmap = json.load(open(os.path.join(REPO, "data", "template_id_map.json")))["pvp_to_template"]
        for pvp, orig in tmap.items():
            if int(pvp) in names and orig not in names: names[orig] = names[int(pvp)]
    except (OSError, ValueError, KeyError): pass
    return names


def load():
    from scoreboard import archetype
    rows = []
    for f in sorted(glob.glob(os.path.join(REPO, "data", "matches", "2*.json"))):
        for r in json.load(open(f)):
            t = r.get("teams") or []
            if len(t) != 2 or r.get("winner") not in (1, 2): continue
            rec = _Rec(r)
            try: arch = {x["id"]: archetype(rec, x["id"])["kind"] for x in t}
            except Exception: continue
            rows.append({"id": r["id"], "at": r.get("at") or 0, "map": r.get("map"), "flux": r.get("flux") or [],
                         "a": t[0]["tag"] or t[0]["guild"], "b": t[1]["tag"] or t[1]["guild"],
                         "arch_a": arch[t[0]["id"]], "arch_b": arch[t[1]["id"]], "a_won": r["winner"] == t[0]["id"]})
    return sorted(rows, key=lambda r: r["at"])


def feats(r):
    """Antisymmetric features from team a's side."""
    A, B = r["arch_a"], r["arch_b"]
    f = collections.Counter()
    if A != B: f[f"matchup: {A} v {B}"] += 1; f[f"matchup: {B} v {A}"] -= 1
    f[f"map: {A} on {r['map']}"] += 1; f[f"map: {B} on {r['map']}"] -= 1
    for x in r["flux"]: f[f"flux: {A} in {x}"] += 1; f[f"flux: {B} in {x}"] -= 1
    return {k: v for k, v in f.items() if v}


def fit():
    import numpy as np
    from strength import components, _blend
    rp = set(json.loads(subprocess.check_output(["git", "-C", REPO, "show", "origin/replays:index.json"]))["matches"])
    rows = [r for r in load() if r["id"] not in rp]
    coef = _blend() or {"fitted": 1.0}
    use = rows[300:]
    cols = collections.Counter(k for r in use for k in feats(r))
    names = sorted(k for k, n in cols.items() if n >= MIN_CELL)
    ix = {k: i for i, k in enumerate(names)}
    X = np.zeros((len(use), len(names))); off = np.zeros(len(use)); y = np.zeros(len(use))
    for i, r in enumerate(use):
        for k, v in feats(r).items():
            if k in ix: X[i, ix[k]] = v
        c = components(r["id"], r["a"])
        g = sum(coef.get(k, 0) * (c[k] if c[k] is not None else (c["fitted"] or 0)) for k in ("ladder", "fitted", "lineup") if k in coef)
        off[i] = g / K; y[i] = int(r["a_won"])
    cut = int(len(y) * 2 / 3)
    def ll(p, yy): p = np.clip(p, 0.02, 0.98); return float(-np.mean(yy * np.log(p) + (1 - yy) * np.log(1 - p)))
    sig = lambda z: 1 / (1 + np.exp(-z))
    base = ll(sig(off[cut:]), y[cut:])
    tests = {}
    for C in PENALTIES:
        w = _offset_logit(X[:cut], y[:cut], off[:cut], C)
        tests[C] = ll(sig(off[cut:] + X[cut:] @ w), y[cut:])
    bestC = min(tests, key=tests.get)
    on = tests[bestC] < base - 0.002
    w = _offset_logit(X, y, off, bestC) if on else np.zeros(len(names))
    effects = {k: {"points": round(float(w[ix[k]]) * K), "matches": cols[k]} for k in names if abs(w[ix[k]]) * K >= 5}
    out = {"about": __doc__.split("\n\n")[1].strip(), "matches": len(use), "features": len(names),
           "test": {"strength alone": round(base, 4), **{f"with context, penalty {C}": round(v, 4) for C, v in tests.items()}},
           "switched_on": bool(on), "penalty": bestC,
           "effects": dict(sorted(effects.items(), key=lambda kv: -abs(kv[1]["points"]))),
           "weights": {k: float(w[ix[k]]) for k in names}}
    json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
    return out


def _offset_logit(X, y, off, lam, iters=30):
    """Ridge logistic regression with a fixed offset (log odds from strength), by Newton steps."""
    import numpy as np
    w = np.zeros(X.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-(off + X @ w)))
        g = X.T @ (y - p) - lam * len(y) * 0.01 * w
        H = (X * (p * (1 - p))[:, None]).T @ X + lam * len(y) * 0.01 * np.eye(X.shape[1])
        w = w + np.linalg.solve(H, g)
    return w


_W = {}
def prior(match_id, tag, rec=None):
    """Points the context adds for tag in this match (0 when the prior is off or the match is unknown). rec = a stored
    match record or a replay-shaped dict for matches not stored."""
    if "w" not in _W:
        try:
            o = json.load(open(OUT)); _W["w"] = o["weights"] if o.get("switched_on") else {}
        except (OSError, ValueError, KeyError): _W["w"] = {}
        _W["rows"] = {r["id"]: r for r in load()} if _W["w"] else {}
    if not _W["w"]: return 0
    r = _W["rows"].get(match_id) or rec
    if not r: return 0
    z = sum(_W["w"].get(k, 0) * v for k, v in feats(r).items())
    return round(z * K * (1 if tag == r["a"] else -1))


if __name__ == "__main__":
    o = fit()
    print(o["matches"], "matches,", o["features"], "features; test:", o["test"], "switched on:", o["switched_on"])
    for k, v in list(o["effects"].items())[:15]: print(f"  {v['points']:+5} {k} ({v['matches']} matches)")
