"""The usual play: for every decision point (decisions.py), what teams usually do in similar situations and how each
choice turned out, measured in win chance (causal map: decisions are caused by the situation; a choice that does better
than the usual play is a candidate "more optimal play").

- Outcome: the change in the deciding team's win chance over the decision's window, from a win model fitted WITHOUT that
  match (it never saw the result), so no guessed weights are involved. Components (deaths, NPCs, flag lead) are shown
  alongside so the number can be read.
- Choice: the decision's choice (ran, held, already running, pushed, reset, ...), refined by what the players actually
  did (e.g. "held, fell back" against "held, fought").
- Usual play in a situation: the most common choice among the 15 most similar decisions of the same kind in OTHER
  matches (similar = flag lead, stand, boost clock, numbers, DP, NPCs, Lord damage, minute, strength gap, scaled).
- Choice effect: each choice's win-chance change against the most common choice, adjusted for the situation (a linear
  fit on the same variables, readable as one number per choice), with a 90% interval from resampling whole matches.
  With few matches most intervals include 0: "not enough data yet" is the honest reading.

Usage:  python3 usual.py [--src DIR]     reads the analysis files (analyze.py --all --out DIR, default /tmp/ga), writes
                                         data/model/usual_play.json and prints the table per decision kind"""
import collections, glob, json, math, os, random, sys, warnings
import numpy as np
warnings.filterwarnings("ignore")
import model as M
from common import REPO

OUT = os.path.join(REPO, "data", "model", "usual_play.json")
K, BOOT, MIN_N = 15, 200, 25
SIT = ["flag_lead", "stand", "boost_in", "alive", "main", "dp", "npcs", "lord_damage", "minute", "strength_gap"]


def refine(r):
    """The choice plus what the players did: the most common action among players not carrying."""
    acts = collections.Counter(v for v in r["actions"]["by_role"].values() if v not in ("carrying", "died"))
    top = acts.most_common(1)[0][0] if acts else None
    base = r["choice"].split(":")[0]
    if r["kind"] == "late_game":            # Lord commitment from 24:00, in levels
        n = float(r["choice"].split()[0])
        return "0 to 1 at the enemy Lord" if n < 1.5 else ("2 to 3 at the enemy Lord" if n < 3.5 else "4+ at the enemy Lord")
    return f"{base}, {top}" if r["kind"] in ("enemy_pickup", "boost_clock", "power_play") and top else base


def situation(r, gap):
    k = r["state"]
    num = lambda s: int(s.split("v")[0]) - int(s.split("v")[1])
    return {"flag_lead": k["flag_lead"], "stand": {"own": 1, "enemy": -1}.get(k["stand"], 0), "boost_in": k["boost_in"] or 0,
            "alive": num(k["alive"]), "main": num(k["main"]), "dp": k["dp"], "npcs": k["npcs"], "lord_damage": k["lord_damage"],
            "minute": r["t"] / 60, "strength_gap": gap or 0}


def load(src):
    recs = []
    for f in sorted(glob.glob(os.path.join(src, "*.json"))):
        a = json.load(open(f))
        for r in a.get("decisions", []): recs.append({"match": a["id"], **r})
    return recs


def wp_change(recs):
    """Win-chance change over each decision's window, from a model that never saw that match."""
    ids = [m for b in M.batches() for m in b["matches"]]
    by_match = collections.defaultdict(list)
    for r in recs: by_match[r["match"]].append(r)
    for mid, L in by_match.items():
        if mid not in ids: continue
        wp = M.WPModel.fit_on([x for x in ids if x != mid])
        tab = {(x["team"], x["t"]): x for x in M.match_table(mid)}
        for r in L:
            t0 = r["t"] - r["t"] % 5; t1 = t0 + r["outcome"]["window_s"] - r["outcome"]["window_s"] % 5
            last = max(tt for (tm_, tt) in tab if tm_ == r["team"])
            a, b = tab.get((r["team"], t0)), tab.get((r["team"], min(t1, last))) or tab.get((r["team"], min(t1, last) - 5))
            if a and b:
                r["wp_before"] = wp.explain(a)[0]; r["wp_after"] = wp.explain(b)[0]
                r["wp_change"] = round(r["wp_after"] - r["wp_before"], 1); r["gap"] = a.get("strength_gap")
    return [r for r in recs if "wp_change" in r]


def analyse(recs):
    out = {}
    for kind in sorted({r["kind"] for r in recs}):
        L = [r for r in recs if r["kind"] == kind]
        for r in L: r["choice2"] = refine(r); r["sit"] = situation(r, r.get("gap"))
        counts = collections.Counter(r["choice2"] for r in L)
        choices = [c for c, n in counts.most_common() if n >= 5]
        L = [r for r in L if r["choice2"] in choices]
        if len(L) < MIN_N or len(choices) < 2:
            out[kind] = {"n": len(L), "note": "not enough decisions yet"}; continue
        X = np.array([[r["sit"][k] for k in SIT] for r in L], float)
        mu, sd = X.mean(0), X.std(0) + 1e-9; Z = (X - mu) / sd
        ref = choices[0]
        D = np.array([[1.0 if r["choice2"] == c else 0.0 for c in choices[1:]] for r in L])
        y = np.array([r["wp_change"] for r in L], float)
        matches = sorted({r["match"] for r in L})
        def fit(idx):
            A = np.hstack([np.ones((len(idx), 1)), Z[idx], D[idx]])
            coef, *_ = np.linalg.lstsq(A, y[idx], rcond=None)
            return coef[-len(choices) + 1:]
        est = fit(np.arange(len(L)))
        rnd = random.Random(7); boots = []
        mi = collections.defaultdict(list)
        for i, r in enumerate(L): mi[r["match"]].append(i)
        for _ in range(BOOT):
            idx = [i for mm in (rnd.choice(matches) for _ in matches) for i in mi[mm]]
            try: boots.append(fit(np.array(idx)))
            except Exception: pass
        boots = np.array(boots)
        rows = [{"choice": ref, "n": counts[ref], "share": round(counts[ref] / len(L), 2), "raw_wp_change": round(float(np.mean([r["wp_change"] for r in L if r["choice2"] == ref])), 1),
                 "effect_vs_usual": 0.0, "interval": [0.0, 0.0]}]
        for j, c in enumerate(choices[1:]):
            lo, hi = (np.percentile(boots[:, j], [5, 95]) if len(boots) else (None, None))
            rows.append({"choice": c, "n": counts[c], "share": round(counts[c] / len(L), 2),
                         "raw_wp_change": round(float(np.mean([r["wp_change"] for r in L if r["choice2"] == c])), 1),
                         "effect_vs_usual": round(float(est[j]), 1), "interval": [round(float(lo), 1), round(float(hi), 1)],
                         "clear": bool(lo > 0 or hi < 0)})
        # usual play per decision: most common choice among the K most similar decisions in other matches
        flagged = []
        eff = {x["choice"]: x["effect_vs_usual"] for x in rows}
        for i, r in enumerate(L):
            dist = np.sqrt(((Z - Z[i]) ** 2).sum(1)); order = [j for j in np.argsort(dist) if L[j]["match"] != r["match"]][:K]
            usual = collections.Counter(L[j]["choice2"] for j in order).most_common(1)[0][0]
            r["usual"] = usual
            if r["choice2"] != usual and abs(eff[r["choice2"]] - eff[usual]) >= 3:
                flagged.append({"match": r["match"], "team": r["team"], "t": r["t"], "chose": r["choice2"], "usual": usual,
                                "difference": round(eff[r["choice2"]] - eff[usual], 1), "wp_change": r["wp_change"]})
        out[kind] = {"n": len(L), "matches": len(matches), "reference": ref, "choices": rows,
                     "unusual_choices": sorted(flagged, key=lambda f: -abs(f["difference"]))[:10]}
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    src = a[a.index("--src") + 1] if "--src" in a else "/tmp/ga"
    recs = wp_change(load(src))
    res = analyse(recs)
    json.dump({"about": __doc__.split("\n\n")[1].strip(), "decisions": len(recs), "kinds": res}, open(OUT, "w"), indent=1, default=str)
    for kind, x in res.items():
        print(f"\n== {kind}: {x.get('n')} decisions" + (f" in {x['matches']} matches" if "matches" in x else "") + (f" ({x['note']})" if "note" in x else ""))
        for c in x.get("choices", []):
            print(f"  {c['choice']:28} n={c['n']:3} ({c['share']:.0%}) raw {c['raw_wp_change']:+5.1f} | vs usual {c['effect_vs_usual']:+5.1f} "
                  f"[{c['interval'][0]:+.1f}, {c['interval'][1]:+.1f}]" + ("  CLEAR" if c.get("clear") else ""))
