"""knowledge/model.md: the generated structural reference (Denning, November 2026 review, E1).

One table per fitted model, rebuilt by every Train batch run (learning.finish) and by `python3 modelpage.py`: the
question, the row unit, rows and events, the inputs grouped by causal-map link with each input's kind (context, state,
decision, execution) and status, the held-out score against the baseline, the inputs pruned for the data's sake, the
measures kept beside the node as the enemy's response, and the inputs that mark the situation. Plus the win model,
the decision kinds, and the map's waiting list. This page is what a reader uses to understand the structure; if a node
can't be explained in GvG terms from it, it isn't explainable yet (the readability test). Report layer: no cache key."""
import collections, datetime, json, os, sys
from common import REPO

NODE_DIR = os.path.join(REPO, "data", "model", "nodes")
OUT = os.path.join(REPO, "knowledge", "model.md")
TIER_NAMES = {"decision": "Tier 2: decision nodes", "execution": "Tier 3: execution nodes", "win": "Tier 4: the win model"}


def _load(p):
    try: return json.load(open(p))
    except (OSError, ValueError): return None


def _learned():
    import learnednodes as LN
    out = {}
    for node in LN.SPEC:
        s = _load(os.path.join(NODE_DIR, f"L_{node}.json"))
        if s: out[node] = s
    return out


def _nodes_py():
    import nodes as N
    out = {}
    for node in N.FITTED:
        s = _load(os.path.join(NODE_DIR, f"{node}.json"))
        if s: out[node] = s
    return out


ROW_UNIT = {"run_outcome": "a run at 5, 15 and 30 s in", "flag_swing": "a 20 s moment", "run_defence": "an enemy run at 5, 15 and 30 s in",
            "capture_speed": "an enemy capture", "power_play": "a power-play window", "fight_outcome": "a fight", "split_chance": "a 15 s moment",
            "split_answer": "a split entering the base", "split_effect": "a split entering the base", "collapse": "a split",
            "pit_npc_loss": "a 3 s moment with enemies in the pit (defending side)",
            "deaths": "a live player every 3 s", "kill_conversion": "a burst (3+ attackers, 250+ in 2 s)", "flag_answer": "an answer to an enemy capture",
            "lord_damage": "a 3 s moment with enemies in the pit"}
NODES_PY_QUESTION = {"deaths": "Does this player die in the next 10 s?", "kill_conversion": "Does this burst kill within 8 s?",
                     "flag_answer": "How many seconds slower than possible was the answer to the enemy's capture?",
                     "lord_damage": "How much Lord damage lands in the next 10 s?"}


def _score(s, learned):
    v = s["validation"]
    if learned:
        return f"{v['metric']} {v['glass box']} against {v['simple baseline']} ({v['verdict']})"
    g, b = v["glass box"], v["simple baseline"]
    if "auc" in g: return f"AUC {g['auc']} against {b['auc']} for {' and '.join(v.get('baseline uses') or [])} alone ({v['verdict']})"
    return f"typical error {g.get('mae_s')} s against {b.get('mae_s')} s ({v['verdict']})"


def learned_table(node, s):
    import learnednodes as LN
    L = []
    q = LN.PLAIN.get(node, node)
    what = f"{s['rows']:,} rows ({ROW_UNIT.get(node, 'event')}), " + (f"average {s['mean']} s" if node in LN.REGRESSION else f"{s['rate']:.0%} positive") + f", {s['matches']} matches"
    L += [f"### {node.replace('_', ' ')}: {q}", "", f"{what}. Held out by match: {_score(s, True)}. "
          f"Inputs {s.get('inputs', sum(len(l['features']) for l in s['links']))}" + (f" of a cap of {s['input_cap']}" if s.get('input_cap') else "") + ".", ""]
    marks = set(s.get("marks_situation") or [])
    kinds = s.get("kinds") or {f: LN.kind_of(node, f) for l in s["links"] for f in l["features"]}
    terms = {t["term"]: t for t in s.get("terms", [])}
    L += ["| Link (cause group) | Kind | Status | Gain | Inputs |", "|---|---|---|---|---|"]
    names = _map_names()
    for l in sorted(s["links"], key=lambda l: -l["strength"]):
        ins = []
        for f in sorted(l["features"], key=lambda f: -(terms.get(f, {}).get("importance") or 0)):
            d = LN.describe(node, f) or f
            ins.append(d + (" [marks the situation]" if f in marks else ""))
        L.append(f"| {names.get(l['from'], l['from'])} ({l['from']}) | {'/'.join(l.get('kinds') or sorted({kinds.get(f, '?') for f in l['features']}))} | {l['status']} | {l['strength']:+} ± {l['plus_minus']} | {'; '.join(ins)} |")
    if s.get("concurrent"):
        L += ["", "Measured beside the node, never a cause (what the enemy did in the window): " + "; ".join(s["concurrent"].values()) + "."]
    if s.get("pruned"):
        L += ["", "Left out so the inputs fit the data: " + "; ".join(f"{LN.describe(node, p['feature']) or p['feature']} ({p['reason']})" for p in s["pruned"]) + "."]
    L.append("")
    return L


def nodes_py_table(node, s):
    import nodes as N
    L = [f"### {node.replace('_', ' ')}: {NODES_PY_QUESTION.get(node, node)}", "",
         f"{s['rows']:,} rows ({ROW_UNIT.get(node, 'row')}), {s.get('events', '?')} events, {s['matches']} matches. Held out by match: {_score(s, False)}.", "",
         "| Input | Kind | Reading |", "|---|---|---|"]
    ctx = set(N.MATCH_FIXED.get(node, set()))
    for t in sorted(s.get("terms", []), key=lambda t: -(t.get("importance") or 0))[:14]:
        if "&" in t["term"]: continue
        kind = "context" if t["term"] in ctx or t["term"] == "strength_gap" else ("state" if any(k in t["term"] for k in ("flag_lead", "minute", "res_", "morale", "health", "alive", "numbers", "local", "distance")) else "execution")
        cv = [c for c in t.get("curve") or [] if c.get("from") is not None]
        rd = f"{cv[0]['points']:+g} at {cv[0]['from']:g}..{cv[0]['to']:g}; {cv[-1]['points']:+g} at {cv[-1]['from']:g}..{cv[-1]['to']:g}" if len(cv) >= 2 else ""
        L.append(f"| {t.get('description') or t['term']} | {kind} | {rd} |")
    L.append("")
    return L


_NAMES = None
def _map_names():
    global _NAMES
    if _NAMES is None:
        c = _load(os.path.join(REPO, "data", "model", "causal_map.json")) or {}
        _NAMES = {n["id"]: n["name"] for n in c.get("nodes", [])}
    return _NAMES


def win_model_lines():
    w = _load(os.path.join(REPO, "data", "model", "wp_model.json"))
    if not w: return ["(no win model yet)", ""]
    v = w["validation"]; so, gb = v.get("strength only", {}).get("all", {}), v.get("glass box", {}).get("all", {})
    L = [f"{w['rows']:,} rows (one per team per 15 s), {w['matches']} matches, {len(w['variables_in_use'])} variables in use. Held out by whole match: "
         f"log loss {gb.get('log_loss')} against {so.get('log_loss')} for strength alone; accuracy {gb.get('accuracy', 0):.0%} against {so.get('accuracy', 0):.0%}.", "",
         "| Variable | Kind | Importance |", "|---|---|---|"]
    import features as F
    desc = getattr(F, "DESCRIPTIONS", {})
    fixed = {"strength_gap", "lord_dps_own", "lord_dps_enemy", "healing_monks_own", "healing_monks_enemy", "spike_build_own", "spike_build_enemy",
             "map_flag_run", "map_pit_to_stand", "map_bases_apart", "period"} | {v for v in w["variables_in_use"] if v.startswith("flux_")}
    for t in sorted(w["terms"], key=lambda t: -(t.get("importance") or 0))[:20]:
        kind = "pairing" if "&" in t["term"] else ("context" if t["term"] in fixed else "state")
        L.append(f"| {desc.get(t['term'], t.get('description') or t['term'])} | {kind} | {t.get('importance', 0):.3f} |")
    L.append("")
    return L


def decision_lines():
    import decisions as D
    kinds = getattr(D, "KINDS", None)
    L = ["| Kind | Moment | Choices | Definition |", "|---|---|---|---|"]
    if kinds:
        for k, d in kinds.items():
            L.append(f"| {k} | {d.get('moment', '')} | {d.get('choices', '')} | {d.get('source', '')} |")
    else:
        L.append("| (decisions.py has no KINDS table yet) | | | |")
    u = _load(os.path.join(REPO, "data", "model", "usual_play.json")) or {}
    ks = u.get("kinds") or {}
    if ks:
        L += ["", "Cases per kind in the usual play (last report): " + ", ".join(f"{k} {v.get('n')}" for k, v in sorted(ks.items())) + "."]
    L.append("")
    return L


def waiting_lines():
    c = _load(os.path.join(REPO, "data", "model", "causal_map.json")) or {}
    W = c.get("waiting") or []
    if not W: return ["(nothing waiting)", ""]
    by = collections.Counter(w.get("kind") for w in W)
    L = [", ".join(f"{k}: {n}" for k, n in by.items()), ""]
    for w in W[:40]:
        L.append(f"- {w.get('kind')}: {w.get('node', '')} {w.get('feature', w.get('name', ''))}: {w.get('why', '')}")
    if len(W) > 40: L.append(f"- ... and {len(W) - 40} more (data/model/causal_map.json, \"waiting\")")
    L.append("")
    return L


def render():
    import learnednodes as LN
    today = datetime.date.today().isoformat()
    LN_ = _learned(); NP = _nodes_py()
    m = max([s["matches"] for s in list(LN_.values()) + list(NP.values())] or [0])
    L = [f"*Generated by tools/replay_analysis/modelpage.py ({today}); don't edit. The design is in docs/SPEC.md, the rulings in "
         "docs/RULINGS.md, the readable curves in \"What the model has learned\" and \"Win-probability model\".*", "",
         "# The model: structure", "",
         f"Trained on {m} matches. Every fitted model answers one question and appears once. Each input has a kind: **context** "
         "(fixed for the match) and **state** (the situation now) are adjustment and never a fix; **decision** (a choice the team "
         "made) and **execution** (how well it was carried out) are the only candidates for \"what should have been done\" and "
         "\"what went wrong\". What the other team did during the same window is measured beside a node, never fitted. An "
         "input that predicts the previous result as well as the next **marks the situation** and is never a fix. Every link's "
         "status comes from refitting without it on matches the model never saw.", "",
         "## Tier 2: decision nodes (the macro answer)", ""]
    L += decision_lines()
    L += ["## Tier 3: execution nodes (the micro answer)", ""]
    order = ["fight_outcome", "power_play", "run_outcome", "run_defence", "capture_speed", "flag_swing", "split_chance",
             "split_answer", "split_effect", "collapse", "pit_npc_loss"]
    for node in order + [n for n in LN_ if n not in order]:
        if node in LN_: L += learned_table(node, LN_[node])
    for node in ["deaths", "kill_conversion", "flag_answer", "lord_damage"]:
        if node in NP: L += nodes_py_table(node, NP[node])
    L += ["## Tier 4: the win model", ""] + win_model_lines()
    L += ["## Waiting list (not in any model)", ""] + waiting_lines()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w").write("\n".join(L) + "\n")
    _index()
    return OUT


def _index():
    p = os.path.join(REPO, "knowledge", "index.json")
    idx = _load(p) or []
    if not any(x.get("id") == "model" for x in idx):
        pos = next((i for i, x in enumerate(idx) if x.get("id") == "learned-model"), len(idx))
        idx.insert(pos, {"id": "model", "title": "The model: structure", "file": "model.md", "group": "GvG"})
        json.dump(idx, open(p, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    print(render())
