"""Learning report: what the win-probability model learned from the latest batch of matches, in words.

Usage:  python3 learning.py            fits on every batch in data/model/batches.json, writes
                                       data/model/reports/batch_NN.md and keeps data/model/history/batch_NN.json
Sections: the honest test (better than team strength alone?); what it leans on and how that changed since the last
batch; each important curve in words, with its uncertainty; discovery (interaction candidates, untested until held-out
matches confirm them; the moments the model got most wrong, which point to missing variables); Denning's rulings seen
through the model (win chance before and after each ruled moment, and its breakdown); questions for Denning.
Claude reads the report, adds its own explanation in the chat, and turns confirmed lessons into tactics lines."""
import collections, json, math, os, sys, warnings
import numpy as np
warnings.filterwarnings("ignore")
import model as M
from features import DESCRIPTIONS
from common import REPO

REPORTS = os.path.join(M.MODEL_DIR, "reports")
HISTORY = os.path.join(M.MODEL_DIR, "history")


def clock(t): return f"{int(t // 60)}:{int(t % 60):02d}"


def curve_words(t):
    """One line: overall direction and a few points, with uncertainty flagged."""
    c = [x for x in t.get("curve", []) if x["from"] is not None]
    if not c: return "no data"
    first, last = c[0]["points"], c[-1]["points"]
    noisy = sum(1 for x in c if abs(x["points"]) < x["plus_minus"]) / len(c)
    trend = "rises" if last - first > 2 else ("falls" if first - last > 2 else "is flat")
    step = max(1, len(c) // 5)
    pts = "; ".join(f"{x['from']}..{x['to']}: {x['points']:+}" for x in c[::step])
    return f"{trend} from {first:+} to {last:+} points ({pts})" + (" (mostly within its uncertainty)" if noisy > 0.5 else "")


def tags(rid):
    t = M.match_table(rid)
    return " v ".join(sorted({r["team"] for r in t}, key=lambda x: [r["team"] for r in t].index(x))) + f" ({rid[:8]})"


_HOLD = {}
def holdout_model(ids, rid):
    """A model fitted on every match except rid, so a match is always explained by a model that never saw it."""
    if rid not in _HOLD: _HOLD[rid] = M.WPModel.fit_on([x for x in ids if x != rid])
    return _HOLD[rid]


def report():
    bs = M.batches(); n = len(bs) - 1
    ids = [m for b in bs for m in b["matches"]]
    new_ids = bs[-1]["matches"]
    model, wp, df, held, X, y = M.fit_and_save(ids, n)
    prev_p = os.path.join(HISTORY, f"batch_{n - 1:02d}.json")
    prev = json.load(open(prev_p)) if n > 0 and os.path.exists(prev_p) else None
    os.makedirs(HISTORY, exist_ok=True); os.makedirs(REPORTS, exist_ok=True)
    json.dump(model, open(os.path.join(HISTORY, f"batch_{n:02d}.json"), "w"), indent=1)

    L = [f"# Learning report, batch {n}", "",
         f"Trained on {model['matches']} matches ({len(new_ids)} new in this batch). Variables in use: "
         f"{len(model['variables_in_use'])}; build variables from {M.STAGES['build_variables']} matches, interactions from "
         f"{M.STAGES['interactions']}.", ""]
    v = model["validation"]
    L += ["## 1. The honest test", "",
          f"**{v['verdict'].capitalize()}.** Held-out accuracy (matches held out whole), log loss in brackets (lower is better):", ""]
    for name in [k for k in v if k != "verdict"]:
        L.append(f"- {name}: " + ", ".join(f"{k} {x['accuracy']:.0%} ({x['log_loss']})" for k, x in v[name].items()))
    if prev:
        pv = prev["validation"]
        L.append(f"- Change since batch {n - 1}: glass box log loss {pv['glass box']['all']['log_loss']} -> "
                 f"{v['glass box']['all']['log_loss']}; strength only {pv['strength only']['all']['log_loss']} -> "
                 f"{v['strength only']['all']['log_loss']}.")
    L.append("")

    L += ["## 2. What it leans on", ""]
    pimp = {t["term"]: t["importance"] for t in prev["terms"]} if prev else {}
    for t in model["terms"][:12]:
        ch = f" (was {pimp[t['term']]})" if t["term"] in pimp else (" (new)" if prev else "")
        L.append(f"- **{t['term']}** {t['importance']}{ch}: {t['description']}")
    L += ["", "## 3. The curves in words", "",
          "Points = win-chance points added to an otherwise even game at each range of the variable.", ""]
    for t in model["terms"][:10]:
        if "curve" in t: L.append(f"- **{t['term']}** {curve_words(t)}")
        else: L.append(f"- **{t['term']}** (interaction): see wp_model.md")
    L.append("")

    # discovery 1: interaction candidates (screen only, coarse bins)
    from interpret.utils import measure_interactions
    use = model["variables_in_use"]
    cand = measure_interactions(X[use], y, init_score=M.strength_score(X), max_interaction_bins=8)[:8]
    L += ["## 4. Discovery", "", "**Interaction candidates** (a screen: pairs whose combination seems to matter beyond each "
          "alone; untested until held-out matches confirm them; switched on in the model from "
          f"{M.STAGES['interactions']} matches):", ""]
    for (i, j), s in cand:
        L.append(f"- {use[i]} with {use[j]} (screen {s:.3f})")
    # discovery 2: candidate variables, retested every batch
    L += ["", "**Candidate variables** (proposed variables, tested on unseen matches; log loss, lower is better):", ""]
    for c in M.test_candidates(ids):
        L.append(f"- {c['candidate']}: {c['without']} without, {c['with']} with: {c['verdict']}. {c['description']}")
    # discovery 3: surprises = held-out moments most wrong, one per match
    yv = y.values; p = np.clip(held, 0.02, 0.98)
    loss = -(yv * np.log(p) + (1 - yv) * np.log(1 - p))
    d = df.assign(p=p, loss=loss)
    worst = d.sort_values("loss", ascending=False).drop_duplicates("match").head(6)
    L += ["", "**Surprises** (moments where the held-out model was most confident about the team that went on to lose; "
          "each points to something the variables don't capture yet):", ""]
    for _, r in worst.iterrows():
        row = next(x for x in M.match_table(r["match"]) if x["t"] == r["t"] and x["team"] == r["team"])
        pw, parts = holdout_model(ids, r["match"]).explain(row)
        L.append(f"- {tags(r['match'])} at {clock(r['t'])}: a model that never saw this match gave {r['team']} {pw}%, and "
                 f"{r['team']} {'won' if r['won'] else 'lost'}. Why it thought so: " + ", ".join(f"{a} {b:+}" for a, b in parts[:5]))
    # rulings
    labels = json.load(open(os.path.join(REPO, "data", "review_labels.json")))["labels"]
    L += ["", "## 5. Denning's rulings seen through the model", "",
          "Win chance from a model that never saw the match, 20 s before and 60 s after each ruled moment. Contributions are "
          "points for an otherwise even game (the curves' scale).", ""]
    seen = set()
    for lb in labels:
        if "t" not in lb or lb["match"] not in ids or (lb["match"], lb["t"]) in seen: continue
        seen.add((lb["match"], lb["t"]))
        tab = M.match_table(lb["match"])
        def at(t, team):
            t = int(t - t % 5)
            return next((x for x in tab if x["t"] == t and x["team"] == team), None)
        for team in sorted({x["team"] for x in tab}):
            b, a = at(lb["t"] - 20, team), at(lb["t"] + 60, team)
            if not b or not a: continue
            hm = holdout_model(ids, lb["match"])
            pb, partsb = hm.explain(b); pa, partsa = hm.explain(a)
            L.append(f"- {tags(lb['match'])} {clock(lb['t'])} ({lb['rule']}), {team}: {pb}% 20 s before -> {pa}% 60 s after "
                     f"({pa - pb:+.1f}). After: " + ", ".join(f"{x} {y_:+}" for x, y_ in partsa[:4]))
    L += ["", "## 6. For Denning", "",
          "- Which curves look wrong to you? A correction (direction, cap, drop, or a pair to always test) is logged with "
          "your reason and tested on held-out matches.",
          "- Do any surprises remind you of something the variables don't capture (a missing variable)?",
          "- Any variable you think matters that isn't listed?", ""]
    path = os.path.join(REPORTS, f"batch_{n:02d}.md")
    open(path, "w").write("\n".join(L) + "\n")
    open(os.path.join(REPORTS, "latest.md"), "w").write("\n".join(L) + "\n")
    note = ("*Generated by tools/replay_analysis/learning.py after each training batch (earlier reports: "
            "data/model/reports/). Don't edit this page.*\n\n")
    open(os.path.join(REPO, "knowledge", "learning-report.md"), "w").write(note + "\n".join(L) + "\n")
    return path


if __name__ == "__main__":
    print(report())
