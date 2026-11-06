"""Discovery tools (METHODS.md "Discovery"): finding what nobody named and where decisions matter most.

- Behaviour clusters: at every decision point (decisions.py) each player's action in the next 20 s is recorded
  (carrying, to the spawn, fell back, advanced, fought, held, died). A team's response is the share of its players in
  each action, split by line (frontline, midline, backline). Responses are grouped by k-means (k from 2 to 7, the k with
  the best silhouette, i.e. the clearest groups); each group is described in words by its typical response, the
  named choices it covers and its average win-chance change. A group spread across several named choices, or a named
  choice split across groups, is a response nobody has named yet: Denning names, merges or rejects it.
- Leverage: per decision kind, how much the choice matters: the share of the spread in win-chance change explained by
  the choice beyond the situation (fitted on the same situation variables as usual.py), and the range between the
  best and worst choice. Attention goes where leverage is high.

In code: clusters(recs) -> {kind: [group, ...]}; leverage(recs) -> [{kind, explained_by_choice, range, n}]
(recs = usual.wp_change(usual.load(DIR))). Used by the learning report."""
import collections
import numpy as np

ACTIONS = ["carrying", "to the spawn", "fell back", "advanced", "fought", "held", "died"]
LINES = ["frontline", "midline", "backline"]
MIN_DECISIONS = 30


def _line_of(role):
    """Line from the engine's role name (replaylib.role_names; common.line decides by build where the match is open)."""
    r = role.lower()
    if "monk" in r or "prot" in r: return "backline"
    if any(k in r for k in ("hammer", "warrior", "derv", "assassin")): return "frontline"
    return "midline"


def response_vector(r):
    by = r["actions"]["by_role"]
    v = collections.Counter()
    for role, act in by.items():
        a = next((x for x in ACTIONS if act.startswith(x)), None)
        if a: v[(_line_of(role), a)] += 1
    n = max(len(by), 1)
    return [v[(ln, a)] / n for ln in LINES for a in ACTIONS]


def _describe(c):
    parts = []
    for i, x in sorted(enumerate(c), key=lambda kv: -kv[1])[:4]:
        if x < 0.06: break
        ln, a = LINES[i // len(ACTIONS)], ACTIONS[i % len(ACTIONS)]
        parts.append(f"{a} ({ln}, {x * 8:.1f} of 8)")
    return ", ".join(parts) or "mixed"


def clusters(recs):
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    from usual import refine
    out = {}
    for kind in sorted({r["kind"] for r in recs}):
        L = [r for r in recs if r["kind"] == kind and r.get("actions", {}).get("by_role")]
        if len(L) < MIN_DECISIONS: continue
        X = np.array([response_vector(r) for r in L])
        best = None
        for k in range(2, min(8, len(L) // 8 + 1)):
            km = KMeans(n_clusters=k, n_init=10, random_state=7).fit(X)
            if len(set(km.labels_)) < 2: continue
            s = silhouette_score(X, km.labels_)
            if best is None or s > best[0]: best = (s, k, km)
        if not best: continue
        s, k, km = best
        groups = []
        for g in range(k):
            idx = [i for i, l in enumerate(km.labels_) if l == g]
            named = collections.Counter(refine(L[i]) for i in idx)
            wc = [L[i]["wp_change"] for i in idx if L[i].get("wp_change") is not None]
            top = named.most_common(3)
            groups.append({"n": len(idx), "response": _describe(km.cluster_centers_[g]),
                           "named_choices": dict(top), "win_change_mean": round(float(np.mean(wc)), 1) if wc else None,
                           "unnamed": top[0][1] / len(idx) < 0.6})
        out[kind] = {"k": k, "silhouette": round(float(s), 2), "groups": sorted(groups, key=lambda g: -g["n"])}
    return out


def leverage(recs):
    from usual import refine, situation, SIT, SIT_EXTRA
    rows = []
    for kind in sorted({r["kind"] for r in recs}):
        L = [r for r in recs if r["kind"] == kind and r.get("wp_change") is not None]
        if len(L) < MIN_DECISIONS: continue
        for r in L: r["_c"] = refine(r); r["_s"] = situation(r, r.get("gap"))
        cols = SIT + SIT_EXTRA.get(kind, [])
        cs = [c for c, n in collections.Counter(r["_c"] for r in L).most_common() if n >= 5]
        L = [r for r in L if r["_c"] in cs]
        if len(cs) < 2 or len(L) < MIN_DECISIONS: continue
        X = np.array([[r["_s"][k] for k in cols] for r in L], float); X = (X - X.mean(0)) / (X.std(0) + 1e-9)
        D = np.array([[1.0 if r["_c"] == c else 0.0 for c in cs[1:]] for r in L])
        y = np.array([r["wp_change"] for r in L], float)
        def r2(A):
            A = np.hstack([np.ones((len(y), 1)), A]); coef, *_ = np.linalg.lstsq(A, y, rcond=None)
            return 1 - float(np.sum((y - A @ coef) ** 2) / np.sum((y - y.mean()) ** 2)), coef
        r_sit, _ = r2(X); r_all, coef = r2(np.hstack([X, D]))
        eff = [0.0] + list(coef[-len(cs) + 1:])
        rows.append({"kind": kind, "n": len(L), "explained_by_situation": round(r_sit, 3),
                     "explained_by_choice": round(r_all - r_sit, 3), "range": round(float(max(eff) - min(eff)), 1),
                     "best": cs[int(np.argmax(eff))], "worst": cs[int(np.argmin(eff))]})
    return sorted(rows, key=lambda x: -x["explained_by_choice"])


if __name__ == "__main__":
    import sys, json, usual as U
    src = sys.argv[1] if len(sys.argv) > 1 else "/tmp/ga"
    recs = U.wp_change(U.load(src))
    print(json.dumps(leverage(recs), indent=1))
    for kind, x in clusters(recs).items():
        print(f"\n== {kind}: {x['k']} groups (silhouette {x['silhouette']})")
        for g in x["groups"]: print(f"  n={g['n']:3} {g['response']} | named {g['named_choices']} | win {g['win_change_mean']}" + (" | UNNAMED" if g["unnamed"] else ""))
