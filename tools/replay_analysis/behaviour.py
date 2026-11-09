"""Behaviour: decisions found from what teams actually did (Denning, November 2026 review, bundle 2; docs/SPEC.md
section 8). Formerly discovery.py (the variable screen is discover.py).

- Behaviour clusters: at every decision point (decisions.py), and at every recurring state (the split_or_stay grid:
  every 30 s from 1:00 for a team with 6+ alive), each player's action in the next 20 s is recorded (carrying, to the
  spawn, fell back, advanced, fought, held, died). A team's response is the share of its players in each action, by
  line (frontline, midline, backline). Responses are grouped by k-means (k from 2 to 7, the clearest k by silhouette);
  each group is described by its typical response, the named choices it covers, its win-chance change against the
  kind's mean (raw and adjusted for the situation), and example moments. A group spread across several named choices,
  or a named choice split across groups, is a response nobody has named yet: UNNAMED, for Denning to name, merge or
  reject. Written to data/model/behaviour.json and knowledge/behaviour.md after each batch (learning.py).
- Leverage: per decision kind, how much the choice matters: the share of the spread in win-chance change explained by
  the choice beyond the situation, and the range between the best and worst choice. Attention goes where leverage is high.

In code: clusters(recs) -> {kind: {...}}; leverage(recs) -> [...]; write(recs) -> paths
(recs = usual.wp_change(usual.load(DIR))). Report layer: no cache key."""
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
        # the situation adjustment (usual.py's situation columns), so a group's win change is read at the same situation
        from usual import situation, SIT, SIT_EXTRA
        cols = SIT + SIT_EXTRA.get(kind, [])
        try:
            S = np.array([[situation(r, r.get("gap"))[c] for c in cols] for r in L], float); S = (S - S.mean(0)) / (S.std(0) + 1e-9)
            y = np.array([r.get("wp_change") if r.get("wp_change") is not None else np.nan for r in L], float)
            okr = ~np.isnan(y)
            G = np.zeros((len(L), k))
            for i, l in enumerate(km.labels_): G[i, l] = 1.0
            A = np.hstack([S[okr], G[okr][:, 1:]])
            coef, *_ = np.linalg.lstsq(np.hstack([np.ones((okr.sum(), 1)), A]), y[okr], rcond=None)
            adj = [0.0] + [float(x) for x in coef[-(k - 1):]]
            adj = [a - float(np.mean(adj)) for a in adj]
        except Exception: adj = [None] * k
        for g in range(k):
            idx = [i for i, l in enumerate(km.labels_) if l == g]
            named = collections.Counter(refine(L[i]) for i in idx)
            wc = [L[i]["wp_change"] for i in idx if L[i].get("wp_change") is not None]
            top = named.most_common(3)
            ex = sorted(idx, key=lambda i: -abs(L[i].get("wp_change") or 0))[:3]
            groups.append({"n": len(idx), "response": _describe(km.cluster_centers_[g]),
                           "named_choices": dict(top), "win_change_mean": round(float(np.mean(wc)), 1) if wc else None,
                           "win_change_adjusted": round(adj[g], 1) if adj[g] is not None else None,
                           "unnamed": top[0][1] / len(idx) < 0.6,
                           "examples": [{"match": L[i]["match"], "team": L[i]["team"], "t": L[i]["t"], "choice": refine(L[i]),
                                         "wp_change": L[i].get("wp_change")} for i in ex]})
        out[kind] = {"k": k, "silhouette": round(float(s), 2), "clusters": sorted(groups, key=lambda g: -g["n"]),
                     "groups": sorted(groups, key=lambda g: -g["n"])}
    return out


def write(recs):
    """data/model/behaviour.json and knowledge/behaviour.md: the clusters with example moments, UNNAMED first."""
    import json, os
    from common import REPO
    cl = clusters(recs); lev = leverage(recs)
    os.makedirs(os.path.join(REPO, "data", "model"), exist_ok=True)
    json.dump({"about": "Behaviour clusters and leverage (behaviour.py): responses nobody named, for Denning to name or reject.",
               "kinds": cl, "leverage": lev}, open(os.path.join(REPO, "data", "model", "behaviour.json"), "w"), indent=1, default=str)
    def clock(t): return f"{int(t // 60)}:{int(t % 60):02d}"
    L = ["*Generated by tools/replay_analysis/behaviour.py after each batch; don't edit.*", "", "# What teams actually do: behaviour clusters", "",
         "At every decision point and every recurring state (every 30 s), what the eight players did in the next 20 s, grouped "
         "by similarity. A group no single named choice covers is **UNNAMED**: a response the engine sees teams make that nobody "
         "has named. Denning names it (it becomes a choice the usual play compares), merges it, or rejects it. Win change = "
         "win-chance points over the window, raw and adjusted for the situation (against the kind's mean).", ""]
    un = [(kind, g) for kind, x in cl.items() for g in x["clusters"] if g["unnamed"]]
    L += [f"## Unnamed responses to rule on: {len(un)}", ""]
    for kind, g in un:
        L.append(f"- **{kind.replace('_', ' ')}** (n {g['n']}): {g['response']}; named today as {g['named_choices']}; win change raw {g['win_change_mean']}, adjusted {g['win_change_adjusted']}")
        for e in g["examples"]: L.append(f"  - example: {e['team']} at {clock(e['t'])} in {e['match'][:8]} (recorded as {e['choice']}, {e['wp_change']:+} points)")
    L += ["", "## Leverage: where the choice matters most", ""]
    for x in lev:
        L.append(f"- {x['kind'].replace('_', ' ')} ({x['n']}): the choice explains {x['explained_by_choice']:.1%} beyond the situation ({x['explained_by_situation']:.1%}); range {x['range']} points, best {x['best']}, worst {x['worst']}")
    L += ["", "## Every kind", ""]
    for kind, x in cl.items():
        L.append(f"**{kind.replace('_', ' ')}** ({x['k']} groups, separation {x['silhouette']})")
        for g in x["clusters"]:
            L.append(f"- n {g['n']}: {g['response']}; named as {g['named_choices']}; win change {g['win_change_mean']} (adjusted {g['win_change_adjusted']})" + (" UNNAMED" if g["unnamed"] else ""))
        L.append("")
    out = os.path.join(REPO, "knowledge", "behaviour.md")
    open(out, "w").write("\n".join(L) + "\n")
    idx_p = os.path.join(REPO, "knowledge", "index.json")
    try:
        idx = json.load(open(idx_p))
        if not any(i.get("id") == "behaviour" for i in idx):
            pos = next((n for n, i in enumerate(idx) if i.get("id") == "learned-model"), len(idx))
            idx.insert(pos, {"id": "behaviour", "title": "What teams actually do", "file": "behaviour.md", "group": "Finding new variables", "tab": "model"})
            json.dump(idx, open(idx_p, "w"), indent=1, ensure_ascii=False)
    except (OSError, ValueError): pass
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
