"""Learning report: what the win-probability model learned from the latest batch of matches, in words.

Usage:  python3 learning.py            fits on every batch in data/model/batches.json, writes
                                       data/model/reports/batch_NN.md and keeps data/model/history/batch_NN.json
Sections: the honest test (better than team strength alone?); what it leans on and how that changed since the last
batch; each important curve in words, with its uncertainty; discovery (interaction candidates, untested until held-out
matches confirm them; the moments the model got most wrong, which point to missing variables); Denning's rulings seen
through the model (win chance before and after each ruled moment, and its breakdown); the node models; the usual play;
values; the TQs (Denning's four questions with the different play measured, tq.py); the snapshot; questions for Denning.
Each section's time goes to data/model/reports/timings.json. Candidate tests and node models pool their fits on every core.
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


def holdout_model(ids, rid):
    """A model fitted on every match except rid, so a match is always explained by a model that never saw it (fitted
    once per batch and shared with every layer, cache.py)."""
    return M.WPModel.heldout(ids, rid)


_T = {"t": None, "laps": {}}
def _lap(name):
    """Time spent on the section that just finished (shown in the workflow log and data/model/reports/timings.json)."""
    import time
    now = time.time()
    if _T["t"] is not None:
        _T["laps"][name] = round(now - _T["t"], 1); print(f"[time] {name}: {_T['laps'][name]} s", flush=True)
    _T["t"] = now


def report():
    _lap("start")
    bs = M.batches(); n = len(bs) - 1
    ids = [m for b in bs for m in b["matches"]]
    new_ids = bs[-1]["matches"]
    import fightstate, subprocess, integrity
    allr = list(json.loads(subprocess.check_output(["git", "-C", REPO, "show", "origin/replays:index.json"]))["matches"])
    fightstate.build(ids, [x for x in allr if x not in ids])       # before the tables: fight_state reads it
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
    _lap("fit and honest test")
    # data integrity (integrity.py): what was repaired or can't be trusted in the matches trained on
    from replaylib import Match
    from state import GameState
    ig = {rid: GameState(Match.from_branch(rid)).m.o["integrity"] for rid in ids}
    L += ["## 0. Data integrity", "",
          f"- Lengths repaired: {sum(1 for x in ig.values() if x['length']['repaired'])} "
          + "".join(f"({rid[:8]} {x['length']['recorded_s']} s -> {x['length']['used_s']} s) " for rid, x in ig.items() if x["length"]["repaired"]),
          f"- Matches with a team's Lord damage not observed (left blank, not zero): {sum(1 for x in ig.values() if x['lord_damage_unobserved'])}",
          f"- Pit NPCs added from the standard roster (never seen in the replay): {sum(sum(x['roster_added'].values()) for x in ig.values() if x['roster_added'])} "
          f"in {sum(1 for x in ig.values() if x['roster_added'] and sum(x['roster_added'].values()))} matches",
          f"- Left out of training: {sum(1 for x in ig.values() if x['exclude'])}", ""]
    L += ["## 1. The honest test", "",
          f"**{v['verdict'].capitalize()}.** Held-out accuracy (matches held out whole), log loss in brackets (lower is better):", ""]
    for name in [k for k in v if k not in ("verdict", "gain_over_strength")]:
        L.append(f"- {name}: " + ", ".join(f"{k} {x['accuracy']:.0%} ({x['log_loss']})" for k, x in v[name].items()))
    if "gain_over_strength" in v:
        gs = v["gain_over_strength"]
        L.append(f"- Gain over strength alone (log loss, resampling whole matches): {gs['log_loss_gain']:+} "
                 f"(90% range {gs['range_90'][0]:+} to {gs['range_90'][1]:+}).")
    if prev:
        pv = prev["validation"]
        L.append(f"- Change since batch {n - 1}: glass box log loss {pv['glass box']['all']['log_loss']} -> "
                 f"{v['glass box']['all']['log_loss']}; strength only {pv['strength only']['all']['log_loss']} -> "
                 f"{v['strength only']['all']['log_loss']}.")
    L.append("")

    _lap("integrity and honest test text")
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

    _lap("curves")
    # discovery 1: interaction candidates (screen only, coarse bins)
    from interpret.utils import measure_interactions
    use = model["variables_in_use"]
    cand = measure_interactions(X[use], y, init_score=M.strength_score(X), max_interaction_bins=8)[:8]
    L += ["## 4. Discovery", "", "**Interaction candidates** (a screen: pairs whose combination seems to matter beyond each "
          "alone; untested until held-out matches confirm them; switched on in the model from "
          f"{M.STAGES['interactions']} matches):", ""]
    for (i, j), s in cand:
        L.append(f"- {use[i]} with {use[j]} (screen {s:.3f})")
    _lap("interaction screen")
    # discovery 2: candidate variables, retested every batch
    L += ["", "**Candidate variables** (proposed variables, tested on unseen matches; log loss, lower is better):", ""]
    for c in M.test_candidates(ids, base=v["glass box"]["all"]["log_loss"]):
        L.append(f"- {c['candidate']}: {c['without']} without, {c['with']} with: {c['verdict']}. {c['description']}")
    _lap("candidate variables")
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
    _lap("surprises")
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
    _lap("rulings")
    # the node models: why results happen (causal map)
    import nodes as NODES
    L += ["", "## 6. Why: the node models", "",
          "Each explains one result from what happened before it (time order enforced), tested on matches it never saw. "
          "AUC = how often a moment that led to the result scores above one that didn't (0.5 = guessing, 1 = perfect).", ""]
    node_fits = NODES.fit_nodes(["deaths", "kill_conversion", "flag_answer", "npc_loss", "lord_damage", "lord_kill"], ids)
    for node, (s_, e_, df_, held_) in node_fits.items():
        v_ = s_["validation"]
        if node in NODES.REGRESSION:
            what = {"flag_answer": "seconds an answer to an enemy capture was slower than possible",
                    "lord_damage": "Lord damage dealt in the next 10 s while players are in the enemy pit"}[node]
            unit = "s" if node == "flag_answer" else ""
            L.append(f"**{node.replace('_', ' ')}** ({what}; "
                     f"{s_['matches']} matches, {s_['rows']} rows): {v_['verdict']} (typical error {v_['glass box']['mae_s']}{unit} "
                     f"against {v_['simple baseline']['mae_s']}{unit} for the median; explains {v_['glass box']['r2']:.0%} of the spread).")
            for t in s_["terms"][:10]:
                c = [x for x in t["curve"] if x["from"] is not None]
                L.append(f"- **{t['term']}** ({NODES.DESC[node].get(t['term'], '')}): " +
                         "; ".join(f"{x['from']}..{x['to']}: {x['points']:+}{(' ' + unit) if unit else ''}" for x in c[::max(1, len(c) // 5)]))
        else:
            L.append(f"**{node.replace('_', ' ')}** ({s_['matches']} matches, {s_['rows']} moments, {s_['events']} results): "
                     f"{v_['verdict']} (AUC {v_['glass box']['auc']} against {v_['simple baseline']['auc']} for "
                     f"{' and '.join(v_['baseline uses'])} alone).")
            for t in s_["terms"][:10]:
                if "curve" in t: L.append(f"- **{t['term']}** ({t['description']}) {curve_words(t)}")
        L.append("")
    _lap("node models")
    # the usual play (usual.py): needs the analysis files (analyze.py --all --out /tmp/ga)
    import usual as U, copy
    tq_recs = tq_res = None
    if os.path.isdir("/tmp/ga"):
        # the decision records are built once (win chance from held-out models) and copied for each use; the TQs reuse the
        # copy the usual play was measured on (it carries each decision's refined choice and its usual play)
        base_recs = U.wp_change(U.load("/tmp/ga"))
        tq_recs = copy.deepcopy(base_recs)
        res = tq_res = U.analyse(tq_recs)
        L += ["## 7. The usual play", "", "Each choice against the most common one in that kind of decision, in win-chance points over the "
              "decision's window, adjusted for the situation, with a 90% range from resampling whole matches. CLEAR = the "
              "range excludes 0. Win chance comes from a model that never saw the match. The same comparison over the "
              f"{U.PRE_S} s BEFORE the decision is a placebo test: a choice can't cause what came before it, so a clear "
              "difference there means the effect is partly who makes that choice.", ""]
        for kind, x in res.items():
            if "choices" not in x: L.append(f"- **{kind}**: {x.get('note')} ({x.get('n')})"); continue
            L.append(f"**{kind.replace('_', ' ')}** ({x['n']} decisions, {x['matches']} matches; usual: {x['reference']})")
            for c in x["choices"][1:]:
                L.append(f"- {c['choice']} (n {c['n']}): {c['effect_vs_usual']:+} [{c['interval'][0]:+}, {c['interval'][1]:+}]"
                         + (" CLEAR" if c.get("clear") else "")
                         + (f"; in the {U.PRE_S} s before: {c['pre_trend_vs_usual']:+} [{c['pre_interval'][0]:+}, {c['pre_interval'][1]:+}]"
                            + (" ALREADY DIFFERENT BEFORE: partly who chooses it" if c.get("selection_warning") else "")
                            if "pre_trend_vs_usual" in c else ""))
            fc = [b for b in x.get("by_build", []) if "fight" in b]
            if fc:
                L.append("  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into "
                         "thirds; raw win-chance change, against the usual choice in the same third):")
                for b in fc:
                    if "raw_difference" in b:
                        L.append(f"  - {b['choice']}, {b['fight']}: {b['raw_difference']:+} (n {b['n']} against {b['n_usual']})")
                    elif b.get("n"):
                        L.append(f"  - {b['choice']}, {b['fight']}: too few yet (n {b['n']} against {b['n_usual']}; "
                                 f"means {b.get('raw_mean')} against {b.get('raw_mean_usual')})")
            L.append("")
        cc = U.collapse_cost(copy.deepcopy(base_recs))
        if cc:
            L += ["**Collapses on a split: time away and its cost** (`S32`; per collapse, averages; main = what the main "
                  "fight lost while the collapsers were away)", "",
                  "| Group | Cases | Away (median s) | Split killed | Collapser died | Own deaths at main | Enemy deaths at main | Flag lead change | DP change | Win change |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
            for k, x in cc.items():
                L.append(f"| {k} | {x['n']} | {x['away_s_median']:g} | {x['killed_split']} | {x['collapser_died']} | "
                         f"{x['own_deaths_at_main']} | {x['enemy_deaths_at_main']} | {x['flag_lead_change']:+} | "
                         f"{x['dp_change']:+} | {x['win_change']:+} |")
            L.append("")
        # discovery at decision points (discovery.py): where the choice matters most, and responses nobody named
        import discovery as DSC
        recs_d = copy.deepcopy(base_recs)
        lev = DSC.leverage(recs_d)
        if lev:
            L += ["**Leverage: where the choice matters most** (share of the spread in win-chance change explained by the "
                  "choice beyond the situation; range = best minus worst choice, in points)", ""]
            for x in lev:
                L.append(f"- {x['kind'].replace('_', ' ')} ({x['n']}): choice explains {x['explained_by_choice']:.1%} "
                         f"(situation {x['explained_by_situation']:.1%}); range {x['range']} points, best {x['best']}, worst {x['worst']}")
            L.append("")
        cl = DSC.clusters(recs_d)
        if cl:
            L += ["**Behaviour clusters: what teams actually did** (each decision's response grouped by what every player did "
                  "in the next 20 s; UNNAMED = a group no single named choice covers: a response for Denning to name or reject)", ""]
            for kind, x in cl.items():
                L.append(f"*{kind.replace('_', ' ')}* ({x['k']} groups, separation {x['silhouette']}):")
                for g in x["groups"]:
                    L.append(f"- n {g['n']}: {g['response']}; named as {g['named_choices']}; win change {g['win_change_mean']}"
                             + (" UNNAMED" if g["unnamed"] else ""))
            L.append("")
    import values as VAL
    v = VAL.measure(ids); VAL.write(v)
    _lap("usual play")
    L += ["## 8. What results and causes are worth", ""] + VAL.report_lines(v)
    _lap("values")
    # the TQs (Denning's four questions, replacing the five random whys): a flag swing, a monk death, a power play without
    # a kill and a pit NPC loss from the new matches, each with the different play measured (tq.py)
    import tq as TQ
    if tq_recs is not None: L += TQ.lines(new_ids, ids, tq_recs, tq_res)
    else: L += ["## The TQs", "", "Not answered: the analysis files are missing (analyze.py --all --out /tmp/ga).", ""]
    _lap("TQs")
    import snapshot as SNAP
    if os.path.isdir("/tmp/gl"): L += SNAP.snapshot(ids, new_ids, "/tmp/gl")
    _lap("snapshot")
    L += ["## 10. For Denning", "",
          "- Which curves look wrong to you? A correction (direction, cap, drop, or a pair to always test) is logged with "
          "your reason and tested on held-out matches.",
          "- Do any surprises remind you of something the variables don't capture (a missing variable)?",
          "- Any variable you think matters that isn't listed?", ""]
    _lap("questions")
    cpu = next((l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")), None) if os.path.exists("/proc/cpuinfo") else None
    # the processor is recorded because the model library's fits can differ in the last digits between processor types
    json.dump({"cores": os.cpu_count(), "cpu": cpu, "seconds": _T["laps"]}, open(os.path.join(REPORTS, "timings.json"), "w"), indent=1)
    path = os.path.join(REPORTS, f"batch_{n:02d}.md")
    open(path, "w").write("\n".join(L) + "\n")
    open(os.path.join(REPORTS, "latest.md"), "w").write("\n".join(L) + "\n")
    note = ("*Generated by tools/replay_analysis/learning.py after each training batch (earlier reports: "
            "data/model/reports/). Don't edit this page.*\n\n")
    open(os.path.join(REPO, "knowledge", "learning-report.md"), "w").write(note + "\n".join(L) + "\n")
    return path


if __name__ == "__main__":
    print(report())
