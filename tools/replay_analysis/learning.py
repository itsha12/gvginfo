"""Learning report: what the win-probability model learned from the latest batch of matches, in words.

Usage:  python3 learning.py            fits on every batch in data/model/batches.json, writes
                                       data/model/reports/batch_NN.md and keeps data/model/history/batch_NN.json
        python3 learning.py part <name> [--out DIR]   one part of the report on its own machine: main, cands, or
                                       nodes:<node,node...> (the Train batch workflow runs them side by side)
        python3 learning.py finish [DIR]   join the saved parts, run values, the TQs and the snapshot, write the report
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


# ---- the report in sections. Each section adds its lines to ctx["parts"][name] and may leave values in ctx for later
# sections. Run serially (report()) or split across machines (the Train batch workflow): part("main"), part("cands"),
# part("nodes:deaths") ... each save their lines to a folder, and finish() runs the last sections on the saved parts
# and writes the report. The text and order are the same either way.
from nodes import FITTED as NODE_LIST        # retired nodes (npc_loss, lord_kill) are not fitted or reported (M1)
ORDER = ["head", "diff", "lean", "cands", "surprises", "rulings", "nodes_head"] + [f"node:{x}" for x in NODE_LIST] + \
        ["learned", "usual", "advice", "values", "tqs", "snapshot", "questions"]
# E5 (Denning, November 2026 review): the TQs and the snapshot run every other chunk unless asked (GVG_TQS=yes|no|auto),
# candidate-variable tests only when there are candidates
TQS = os.environ.get("GVG_TQS", "auto")


def _ctx():
    bs = M.batches(); n = len(bs) - 1
    ids = [m for b in bs for m in b["matches"]]
    prev_p = os.path.join(HISTORY, f"batch_{n - 1:02d}.json")
    prev = json.load(open(prev_p)) if n > 0 and os.path.exists(prev_p) else None
    return {"n": n, "ids": ids, "new_ids": bs[-1]["matches"], "prev": prev, "parts": {}}


def fightstate_extra(ids):
    """Fight-state predictions for every stored replay (trained ones by groups, the rest from a model on all trained
    matches). Run once before any section (the workflow's preparation job does it, so every part shares it)."""
    import fightstate, subprocess
    allr = __import__("common").replay_ids()
    fightstate.build(ids, [x for x in allr if x not in ids])       # before the tables: fight_state reads it


def s_head(c):
    ids, n, prev, new_ids = c["ids"], c["n"], c["prev"], c["new_ids"]
    fightstate_extra(ids)
    if not os.path.exists(M.CAPS): M.cap_test(ids)          # normally built by cache.py warm (the workflow's prepare job)
    model, wp, df, held, X, y = M.fit_and_save(ids, n)
    c.update(model=model, df=df, held=held, X=X, y=y)
    os.makedirs(HISTORY, exist_ok=True); os.makedirs(REPORTS, exist_ok=True)
    json.dump(model, open(os.path.join(HISTORY, f"batch_{n:02d}.json"), "w"), indent=1)

    L = [f"# Learning report, batch {n}", "",
         f"Trained on {model['matches']} matches ({len(new_ids)} new in this batch). Variables in use: "
         f"{len(model['variables_in_use'])}; build variables from {M.STAGES['build_variables']} matches, interactions from "
         f"{M.STAGES['interactions']}.", ""]
    v = model["validation"]; c["v"] = v
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
    for name in [k for k in v if k not in ("verdict", "gain_over_strength", "by_period", "by_strength_band")]:
        L.append(f"- {name}: " + ", ".join(f"{k} {x['accuracy']:.0%} ({x['log_loss']})" for k, x in v[name].items()))
    # by period and by strength band (Denning, November 2026 review): glass box against strength alone, log loss
    for key, lab in (("by_period", "By month played"), ("by_strength_band", "By strength band")):
        if v.get(key):
            L.append(f"- {lab} (glass box against strength alone, log loss; matches): "
                     + "; ".join(f"{k} {x['glass box']['log_loss']} v {x['strength only']['log_loss']} ({x['matches']})" for k, x in v[key].items()))
    if "gain_over_strength" in v:
        gs = v["gain_over_strength"]
        L.append(f"- Gain over strength alone (log loss, resampling whole matches): {gs['log_loss_gain']:+} "
                 f"(90% range {gs['range_90'][0]:+} to {gs['range_90'][1]:+}).")
    if prev:
        pv = prev["validation"]
        L.append(f"- Change since batch {n - 1}: glass box log loss {pv['glass box']['all']['log_loss']} -> "
                 f"{v['glass box']['all']['log_loss']}; strength only {pv['strength only']['all']['log_loss']} -> "
                 f"{v['strength only']['all']['log_loss']}.")
    # Denning's cap tests (the data picks the cap) and the calibration by minute, both built by cache.py warm
    try:
        for term, ch in json.load(open(M.CAPS))["choices"].items():
            L.append(f"- Cap test on {term} (held-out log loss, {ch['matches']} matches): "
                     + ", ".join(f"{k if k == 'none' else k + ' points'} {v}" for k, v in ch["log_loss"].items()) + f"; chosen: {ch['verdict']}.")
        pr = json.load(open(M.CAPS)).get("pairs") or {}
        if pr: L.append(f"- Pair test ({'; '.join(pr['pairs'])}; held-out log loss, {pr['matches']} matches): allowed "
                        f"{pr['log_loss']['allowed']}, blocked {pr['log_loss']['blocked']}; chosen: {pr['verdict']}.")
    except (OSError, ValueError, KeyError): pass
    try:
        cal = json.load(open(M.CALIB))
        L.append(f"- Calibration by minute (held-out predictions on {cal['matches']} matches; pooled cells joined by straight "
                 "lines, blended by minute; every win chance below and in values, usual play and the TQs goes through it). "
                 "Predicted -> how often those teams won -> calibrated:")
        for b in cal["bands"]:
            lo, hi = b["minutes"]
            ends = [x for x in b["cells"] if x["from"] in (0, 2, 35, 50, 90, 98)]
            L.append(f"  - {lo} to {hi if hi else 'end'} min: "
                     + "; ".join(f"{x['predicted']}% -> won {x['won']}% ({x['matches']} matches) -> {x['calibrated']}%" for x in ends))
    except (OSError, ValueError, KeyError): pass
    L.append("")
    _lap("integrity and honest test text")
    c["parts"]["head"] = L


def s_lean(c):
    model, prev, X, y = c["model"], c["prev"], c["X"], c["y"]
    L = ["## 2. What it leans on", ""]
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
    c["parts"]["lean"] = L


def s_cands(c):
    # discovery 2: candidate variables, retested every batch. Split across machines, the base is fitted here on the same
    # folds and rows (model.test_candidates), so the number is the honest test's own
    base = c["v"]["glass box"]["all"]["log_loss"] if "v" in c else None
    from features import CANDIDATES
    if not CANDIDATES:
        c["parts"]["cands"] = ["", "**Candidate variables**: none queued (proposals wait for the next bundled engine change).", ""]
        _lap("candidate variables"); return
    L = ["", "**Candidate variables** (proposed variables, tested on unseen matches; log loss, lower is better):", ""]
    for x in M.test_candidates(c["ids"], base=base):
        L.append(f"- {x['candidate']}: {x['without']} without, {x['with']} with: {x['verdict']}. {x['description']}")
    _lap("candidate variables")
    c["parts"]["cands"] = L


def s_surprises(c):
    ids, df, held, y = c["ids"], c["df"], c["held"], c["y"]
    # discovery 3: surprises = held-out moments most wrong, one per match
    yv = y.values; p = np.clip(held, 0.02, 0.98)
    loss = -(yv * np.log(p) + (1 - yv) * np.log(1 - p))
    d = df.assign(p=p, loss=loss)
    worst = d.sort_values("loss", ascending=False).drop_duplicates("match").head(6)
    L = ["", "**Surprises** (moments where the held-out model was most confident about the team that went on to lose; "
         "each points to something the variables don't capture yet):", ""]
    for _, r in worst.iterrows():
        row = next(x for x in M.match_table(r["match"]) if x["t"] == r["t"] and x["team"] == r["team"])
        pw, parts = holdout_model(ids, r["match"]).explain(row)
        L.append(f"- {tags(r['match'])} at {clock(r['t'])}: a model that never saw this match gave {r['team']} {pw}%, and "
                 f"{r['team']} {'won' if r['won'] else 'lost'}. Why it thought so: " + ", ".join(f"{a} {b:+}" for a, b in parts[:5]))
    _lap("surprises")
    c["parts"]["surprises"] = L


def s_rulings(c):
    ids = c["ids"]
    labels = json.load(open(os.path.join(REPO, "data", "review_labels.json")))["labels"]
    L = ["", "## 5. Denning's rulings seen through the model", "",
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
    c["parts"]["rulings"] = L


def s_nodes(c, which=None):
    """The node models (section 6). which = the nodes to fit here (all by default); each node's lines are kept apart
    so nodes fitted on different machines join in the usual order."""
    import nodes as NODES
    c["parts"]["nodes_head"] = ["", "## 6. Why: the node models", "",
        "Each explains one result from what happened before it (time order enforced), tested on matches it never saw. "
        "AUC = how often a moment that led to the result scores above one that didn't (0.5 = guessing, 1 = perfect).", ""]
    node_fits = NODES.fit_nodes([x for x in NODE_LIST if which is None or x in which], c["ids"])
    for node, (s_, e_, df_, held_) in node_fits.items():
        L = []
        v_ = s_["validation"]
        if node in NODES.REGRESSION:
            what = {"flag_answer": "seconds an answer to an enemy capture was slower than possible",
                    "lord_damage": "Lord damage dealt in the next 10 s while players are in the enemy pit"}[node]
            unit = "s" if node == "flag_answer" else ""
            L.append(f"**{node.replace('_', ' ')}** ({what}; "
                     f"{s_['matches']} matches, {s_['rows']} rows): {v_['verdict']} (typical error {v_['glass box']['mae_s']}{unit} "
                     f"against {v_['simple baseline']['mae_s']}{unit} for the median; explains {v_['glass box']['r2']:.0%} of the spread).")
            if node in getattr(NODES, "TWO_PART", ()): L.append(f"  ({s_['note']}.)")
            for t in [t for t in s_["terms"] if t.get("curve")][:10]:      # two-variable tables (chance part) are in the node file
                cv = [x for x in t["curve"] if x["from"] is not None]
                u = "" if node in getattr(NODES, "TWO_PART", ()) else ((" " + unit) if unit else "")
                if "(amount" in t["term"]: u = "%"
                elif "(chance" in t["term"]: u = " points"
                L.append(f"- **{t['term']}** ({NODES.DESC[node].get(t.get('base_term', t['term']), '')}): " +
                         "; ".join(f"{x['from']}..{x['to']}: {x['points']:+}{u}" for x in cv[::max(1, len(cv) // 5)]))
        else:
            L.append(f"**{node.replace('_', ' ')}** ({s_['matches']} matches, {s_['rows']} moments, {s_['events']} results): "
                     f"{v_['verdict']} (AUC {v_['glass box']['auc']} against {v_['simple baseline']['auc']} for "
                     f"{' and '.join(v_['baseline uses'])} alone).")
            for t in s_["terms"][:10]:
                if "curve" in t: L.append(f"- **{t['term']}** ({t['description']}) {curve_words(t)}")
        L.append("")
        c["parts"][f"node:{node}"] = L
    _lap("node models")


def s_learned(c):
    # step 2 of the learned causal map: event-layer values (2a) and the learned nodes with every link's measured strength
    import eventlayer as EL, learnednodes as LN, causal_map as CM
    ids = c["ids"]
    EL.warm(ids); V_ = EL.values(ids)
    bs_ = M.batches(); last2 = [m for b in bs_[-2:] for m in b["matches"]]
    open(os.path.join(REPO, "data", "model", "reports", "measures.md"), "w").write("\n".join(EL.report(last2)) + "\n")
    _lap("event layer and values")
    ln_fits = LN.fit_all(ids, V=V_)
    L = LN.report_lines(ln_fits)
    LN.write_map(ln_fits)
    LN.render_overview(ln_fits)
    CM.render()
    _lap("learned nodes")
    c["parts"]["learned"] = L


def s_usual(c):
    # the usual play (usual.py): needs the analysis files (analyze.py --all --out /tmp/ga)
    import usual as U, copy
    L = []
    c["tq_recs"] = c["tq_res"] = None
    if os.path.isdir("/tmp/ga"):
        # the decision records are built once (win chance from held-out models) and copied for each use; the TQs reuse the
        # copy the usual play was measured on (it carries each decision's refined choice and its usual play)
        base_recs = U.wp_change(U.load("/tmp/ga"))
        tq_recs = copy.deepcopy(base_recs)
        res = tq_res = U.analyse(tq_recs)
        c["tq_recs"], c["tq_res"] = tq_recs, tq_res
        # data/model/usual_play.json kept current (it held old readings before; the report was the only current copy)
        json.dump({"about": U.__doc__.split("\n\n")[1].strip(), "decisions": len(tq_recs), "kinds": res}, open(U.OUT, "w"), indent=1, default=str)
        # the goal test (advice.py): does matching the advice built from unseen-to-the-match groups do better
        try:
            import advice as ADV
            c["parts"]["advice"] = ADV.lines(ADV.advice_test(copy.deepcopy(base_recs)))
        except Exception as ex:
            c["parts"]["advice"] = ["## Does the advice work? (the goal test)", "", f"Not run: {ex}", ""]
        _lap("advice test")
        L += ["## 7. The usual play", "", "Each choice against the most common one in that kind of decision, in win-chance points over the "
              "decision's window, adjusted for the situation, with a 90% range from resampling whole matches. CLEAR = the "
              "range excludes 0. Win chance comes from a model that never saw the match. The same comparison over the "
              f"{U.PRE_S} s BEFORE the decision is a placebo test: a choice can't cause what came before it, so a clear "
              "difference there means the effect is partly who makes that choice.", ""]
        for kind, x in res.items():
            if "choices" not in x: L.append(f"- **{kind}**: {x.get('note')} ({x.get('n')})"); continue
            L.append(f"**{kind.replace('_', ' ')}** ({x['n']} decisions, {x['matches']} matches; usual: {x['reference']})")
            for ch in x["choices"][1:]:
                L.append(f"- {ch['choice']} (n {ch['n']}): {ch['effect_vs_usual']:+} [{ch['interval'][0]:+}, {ch['interval'][1]:+}]"
                         + (" CLEAR" if ch.get("clear") else "")
                         + (f"; in the {U.PRE_S} s before: {ch['pre_trend_vs_usual']:+} [{ch['pre_interval'][0]:+}, {ch['pre_interval'][1]:+}]"
                            + (" ALREADY DIFFERENT BEFORE: partly who chooses it" if ch.get("selection_warning") else "")
                            if "pre_trend_vs_usual" in ch else ""))
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
            sc = [b for b in x.get("by_build", []) if "snare" in b]
            if sc:
                L.append("  By snare matchup (movepower.py: enemy snare power of the live players minus own speed power; decisions "
                         "split into thirds; raw win-chance change, against the usual choice in the same third):")
                for b in sc:
                    if "raw_difference" in b:
                        L.append(f"  - {b['choice']}, {b['snare']}: {b['raw_difference']:+} (n {b['n']} against {b['n_usual']})")
                    elif b.get("n"):
                        L.append(f"  - {b['choice']}, {b['snare']}: too few yet (n {b['n']} against {b['n_usual']}; "
                                 f"means {b.get('raw_mean')} against {b.get('raw_mean_usual')})")
            mc = [b for b in x.get("by_build", []) if "map" in b and "raw_difference" in b]
            if mc:
                L.append("  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):")
                for b in mc: L.append(f"  - {b['choice']}, {b['map']}: {b['raw_difference']:+} (n {b['n']} against {b['n_usual']})")
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
        import behaviour as DSC
        recs_d = copy.deepcopy(base_recs)
        try: DSC.write(copy.deepcopy(base_recs))          # data/model/behaviour.json, knowledge/behaviour.md
        except Exception as ex: L.append(f"- behaviour page not written: {ex}")
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
            un = sum(1 for x in cl.values() for g in x["clusters"] if g["unnamed"])
            L += [f"**Behaviour clusters: what teams actually did** ({un} UNNAMED responses for Denning to name or reject; the full "
                  "list with example moments is on the page \"What teams actually do\", knowledge/behaviour.md)", ""]
    _lap("usual play")
    c["parts"]["usual"] = L


def s_values_measure(c):
    # measured where the usual play just loaded every match's held-out win chance (reused in memory: about 2 minutes
    # saved against measuring it on another machine); written and priced after the node models (s_values)
    import values as VAL
    c["values_v"] = VAL.measure(c["ids"])
    _lap("values (measure)")


def s_values(c):
    # after the node models: the causes are priced from data/model/nodes/*.json
    import values as VAL
    v = c.get("values_v") or VAL.measure(c["ids"]); VAL.write(v)
    c["parts"]["values"] = ["## 8. What results and causes are worth", ""] + VAL.report_lines(v)
    _lap("values")


def s_tqs(c):
    # the TQs (Denning's four questions, replacing the five random whys): a flag swing, a monk death, a power play without
    # a kill and a pit NPC loss from the new matches, each with the different play measured (tq.py)
    import tq as TQ
    if not _run_tqs(c): L = ["## The TQs", "", f"Not run this chunk (batch {c['n']}; the TQs run every other chunk, or with GVG_TQS=yes).", ""]
    elif c.get("tq_recs") is not None: L = TQ.lines(c["new_ids"], c["ids"], c["tq_recs"], c["tq_res"])
    else: L = ["## The TQs", "", "Not answered: the analysis files are missing (analyze.py --all --out /tmp/ga).", ""]
    _lap("TQs")
    c["parts"]["tqs"] = L


def _run_tqs(c):
    if TQS == "yes": return True
    if TQS == "no": return False
    return c["n"] % 2 == 0


def s_snapshot(c):
    import snapshot as SNAP
    c["parts"]["snapshot"] = (SNAP.snapshot(c["ids"], c["new_ids"], "/tmp/gl") if os.path.isdir("/tmp/gl") and _run_tqs(c)
                              else ["## 9. Detailed learnings snapshot", "", "Not run this chunk (every other chunk, or with GVG_TQS=yes).", ""])
    _lap("snapshot")
    c["parts"]["questions"] = questions_lines()
    _lap("questions")


def s_diff(c):
    """E6 (Denning, November 2026 review): what changed since the last batch, as a diff: link status changes (from
    link_log.json's last two runs), inputs pruned or restored (the map's waiting list), win-model terms that moved most,
    and the honest test's movement. Everything else in the report is the full state; this is what to read first."""
    L = ["## What changed since the last batch", ""]
    n, prev, model = c["n"], c.get("prev"), c.get("model")
    try:
        log = json.load(open(os.path.join(M.MODEL_DIR, "link_log.json")))
        dates = sorted({e["date"] for e in log})
        if len(dates) >= 2:
            last, before = dates[-1], dates[-2]
            cur = {(e["node"], e["from"], e["to"]): e for e in log if e["date"] == last}
            old = {(e["node"], e["from"], e["to"]): e for e in log if e["date"] == before}
            ch = [(k, old[k]["status"], v["status"], v["strength"]) for k, v in cur.items() if k in old and old[k]["status"] != v["status"]]
            new = [k for k in cur if k not in old]; gone = [k for k in old if k not in cur]
            L.append(f"- Learned-node links: {len(ch)} status changes since {before}"
                     + (": " + "; ".join(f"{k[0]} {k[1]} -> {k[2]}: {a} -> {b} ({s:+})" for k, a, b, s in ch) if ch else "") + ".")
            if new: L.append(f"- Links measured for the first time: {', '.join(f'{k[0]} {k[1]} -> {k[2]}' for k in new[:12])}{'...' if len(new) > 12 else ''}.")
            if gone: L.append(f"- Links no longer fitted: {', '.join(f'{k[0]} {k[1]} -> {k[2]}' for k in gone[:12])}.")
    except (OSError, ValueError, KeyError) as ex: L.append(f"- Link changes: not read ({ex}).")
    try:
        cmap = json.load(open(os.path.join(M.MODEL_DIR, "causal_map.json")))
        W = [w for w in cmap.get("waiting", []) if w.get("kind") == "pruned input"]
        if W: L.append(f"- Inputs left out so the nodes fit the data: {len(W)} (" + "; ".join(f"{w['node']} {w['feature']}" for w in W[:10]) + ("..." if len(W) > 10 else "") + ").")
        conc = [l for l in cmap.get("links", []) if l.get("status") == "concurrent"]
        if conc: L.append("- Links held as the enemy's concurrent response (measured, not fitted): " + "; ".join(l["from"] + " -> " + l["to"] for l in conc) + ".")
    except (OSError, ValueError): pass
    if model and prev:
        pimp = {t["term"]: t["importance"] for t in prev["terms"]}
        moved = sorted(((t["term"], t["importance"] - pimp.get(t["term"], 0)) for t in model["terms"]), key=lambda x: -abs(x[1]))[:6]
        L.append("- Win-model terms that moved most (importance): " + ", ".join(f"{t} {d:+.3f}" for t, d in moved) + ".")
        pv, v = prev["validation"], model["validation"]
        L.append(f"- Honest test: glass box {pv['glass box']['all']['log_loss']} -> {v['glass box']['all']['log_loss']}, strength alone "
                 f"{pv['strength only']['all']['log_loss']} -> {v['strength only']['all']['log_loss']} (batch {n - 1} -> {n}).")
    marks = []
    for f in sorted(__import__("glob").glob(os.path.join(M.MODEL_DIR, "nodes", "L_*.json"))):
        try:
            s_ = json.load(open(f))
            for m in s_.get("marks_situation") or []: marks.append(f"{s_['node']} {m}")
        except (OSError, ValueError): pass
    if marks: L.append(f"- Inputs that mark the situation (never a fix): {', '.join(marks)}.")
    L.append("")
    c["parts"]["diff"] = L


def questions_lines():
    """Questions for Denning come from the mechanisms (Denning, November 2026 review): clusters to name, candidates to
    approve, pruned inputs to confirm, links the data wants to reject. No list of Claude's ideas."""
    L = ["## 10. For Denning", ""]
    try:
        cmap = json.load(open(os.path.join(M.MODEL_DIR, "causal_map.json")))
        pend = [l for l in cmap.get("links", []) if l.get("pending_rejection")]
        if pend: L.append("- Links of yours the data says to reject (rule: override yes, or not yet): " + "; ".join(f"{l['from']} -> {l['to']}" for l in pend) + ".")
        W = cmap.get("waiting", [])
        if W: L.append(f"- Waiting list: {len(W)} items (data/model/causal_map.json, waiting); nothing moves in until the next bundled engine change.")
    except (OSError, ValueError): pass
    try:
        d = json.load(open(os.path.join(M.MODEL_DIR, "discovery.json")))
        held = d.get("held") or d.get("discoveries") or []
        if held: L.append(f"- Discovery candidates held for approval: {len(held)} (knowledge/discovery.md; only decision and execution variables that passed twice are offered).")
    except (OSError, ValueError): pass
    try:
        b = json.load(open(os.path.join(M.MODEL_DIR, "behaviour.json")))
        un = [x for k in b.get("kinds", {}).values() for x in k.get("clusters", []) if x.get("unnamed")]
        if un: L.append(f"- Behaviour clusters no named choice covers: {len(un)} to name or reject (knowledge/behaviour.md).")
    except (OSError, ValueError): pass
    if len(L) == 2: L.append("- Nothing to rule on this batch.")
    L.append("")
    return L


def _write(c, part_seconds=None):
    import platform
    L = [x for k in ORDER for x in c["parts"].get(k, [])]
    n = c["n"]
    cpu = next((l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")), None) if os.path.exists("/proc/cpuinfo") else None
    cpu = cpu or platform.machine()
    # the processor is recorded because the model library's fits can differ in the last digits between processor types
    t = {"cores": os.cpu_count(), "cpu": cpu, "seconds": _T["laps"]}
    if part_seconds: t["split"] = part_seconds
    json.dump(t, open(os.path.join(REPORTS, "timings.json"), "w"), indent=1)
    path = os.path.join(REPORTS, f"batch_{n:02d}.md")
    open(path, "w").write("\n".join(L) + "\n")
    open(os.path.join(REPORTS, "latest.md"), "w").write("\n".join(L) + "\n")
    note = ("*Generated by tools/replay_analysis/learning.py after each training batch (earlier reports: "
            "data/model/reports/). Don't edit this page.*\n\n")
    open(os.path.join(REPO, "knowledge", "learning-report.md"), "w").write(note + "\n".join(L) + "\n")
    return path


def report():
    """The whole report on one machine, section by section."""
    _lap("start")
    c = _ctx()
    for fn in (s_head, s_lean, s_cands, s_surprises, s_rulings, s_nodes, s_learned, s_usual, s_values_measure, s_values, s_tqs, s_snapshot, s_diff):
        fn(c)
    try:
        import modelpage; modelpage.render()
    except Exception as ex: print("model page not rendered:", ex)
    return _write(c)


# ---- split across machines (the Train batch workflow): parts in parallel, then finish
PART_SECTIONS = {"main": (s_head, s_lean, s_surprises, s_rulings, s_usual, s_values_measure), "learned": (s_learned,),
                 "cands": (s_cands,)}


def part(name, out):
    """Run one part's sections and save its lines (and, for main, the decision records the TQs reuse) to out/."""
    import pickle, time
    t0 = time.time(); _lap("start")
    c = _ctx()
    if name.startswith("nodes:"): s_nodes(c, name.split(":", 1)[1].split(","))
    else:
        for fn in PART_SECTIONS[name]: fn(c)
    os.makedirs(out, exist_ok=True)
    safe = name.replace(":", "_").replace(",", "+")
    json.dump({"part": name, "lines": c["parts"], "laps": _T["laps"], "seconds": round(time.time() - t0, 1)},
              open(os.path.join(out, f"part_{safe}.json"), "w"))
    if name == "main":
        pickle.dump({"tq_recs": c.get("tq_recs"), "tq_res": c.get("tq_res"), "values_v": c.get("values_v")}, open(os.path.join(out, "main_recs.pkl"), "wb"))


def finish(src):
    """Join the saved parts and run the last sections (values and the TQs read the node models' files; snapshot)."""
    import glob, pickle
    _lap("start")
    c = _ctx(); split = {}
    for f in sorted(glob.glob(os.path.join(src, "part_*.json"))):
        p = json.load(open(f)); c["parts"].update(p["lines"]); split[p["part"]] = {"seconds": p["seconds"], "laps": p["laps"]}
        for k, s in p["laps"].items(): _T["laps"][k] = round(_T["laps"].get(k, 0) + s, 1)
    missing = [k for k in ["head", "lean", "cands", "surprises", "rulings", "learned", "usual"] + [f"node:{x}" for x in NODE_LIST]
               if k not in c["parts"]]
    if missing: raise SystemExit(f"parts missing: {missing}")
    rp = os.path.join(src, "main_recs.pkl")
    if os.path.exists(rp): c.update(pickle.load(open(rp, "rb")))
    for fn in (s_values, s_tqs, s_snapshot, s_diff): fn(c)
    try:
        import modelpage; modelpage.render()
    except Exception as ex: print("model page not rendered:", ex)
    return _write(c, split)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["part"]: part(a[1], a[a.index("--out") + 1] if "--out" in a else "/tmp/parts")
    elif a[:1] == ["finish"]: print(finish(a[1] if len(a) > 1 else "/tmp/parts"))
    else: print(report())
