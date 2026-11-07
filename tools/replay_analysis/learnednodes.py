"""The learned causal map, step 2b (Denning 2026-11-07): node models built from the event layer, each using only the
causal-map links into it, so every link's strength is measured on matches the model never saw.

Each node: one row per event (a run, a fight, a split, a power play) or per sampled moment, a label after it, and
features measured at or before it, grouped by the causal-map link they stand for (from node -> the node's map target).
Glass box (Explainable Boosting Machine, main effects only, so every curve reads on its own), held out by match.

A link's strength = how much worse the node predicts unseen matches without that link's features (refit without them,
same folds): log loss for yes/no nodes, mean absolute error (s) for number nodes. Status: supported when the gain is
more than twice its spread across folds, rejected when dropping it helps by more than twice its spread, otherwise not
clear yet. Written into data/model/causal_map.json (field "measured", status changed only from hypothesis) and logged in
data/model/link_log.json. A link that a node needs and the map lacked is added as a hypothesis, logged, with its source.

Nodes (map target):
  run_outcome      (R.3)  a flag run is captured; read at the same point of every run (5, 15, 30 s in): control and
                          damage on the runner so far, not over the whole run (a run that gets far gets Crippled)
  flag_swing       (R.3)  change in flag lead over the next 60 s (s), every 20 s
  capture_speed    (R.3)  seconds an enemy capture took, from the defending side; defence read 10 s into the run
  power_play       (K.4)  a power play of any size kills
  fight_outcome    (R.2)  a fight is won; play measured before its first death (wrong casts over the fight, as rates)
  split_chance     (A.allocation)  a team starts a split in the next 30 s (for "failed to split")
  split_answer     (P.11) seconds until the first defender reaches a split in the base (60 = never)
  split_effect     (R.5)  a split in the base kills a pit NPC
  collapse         (R.1)  a split member dies during the split
Usage:  python3 learnednodes.py fit [node ...]     fit, measure links, write data/model/nodes/L_<node>.json, print
        python3 learnednodes.py write              fit all, write link strengths into the causal map and the log
In code: fit_all(ids) -> {node: summary}; whatif(node, row, changes) -> (before, after)."""
import collections, datetime, hashlib, json, math, os, statistics, sys, warnings
import numpy as np
warnings.filterwarnings("ignore")
from common import REPO
import model as M

NODE_DIR = os.path.join(REPO, "data", "model", "nodes")
MAP = os.path.join(REPO, "data", "model", "causal_map.json")
LINK_LOG = os.path.join(REPO, "data", "model", "link_log.json")
from lnrows import CHECKPOINTS, CLIP, NEVER
REGRESSION = {"flag_swing", "capture_speed", "split_answer"}

# node -> (map target, {group (map node the link comes from): {feature: description}}, base features kept in every fit)
SPEC = {
 "run_outcome": ("R.3", {
    "P.10": {"stand_own": "own team holds the stand", "stand_enemy": "the enemy holds the stand",
             "enemy_boost_in": "seconds to the enemy's boost (if it holds)", "flag_lead": "flag lead at the start (s)",
             "runner_line": "runner 0 frontline, 1 midline, 2 backline"},
    "A.allocation": {"escort": "escorts at the start", "own_main": "own main", "enemy_main": "enemy main",
                     "enemy_power_play": "running into an enemy power play"},
    "K.11": {"crippled_so_far": "runner Crippled by this point", "knocked_down_so_far": "runner knocked down by this point",
             "other_control_so_far": "other conditions on the runner by this point", "damage_so_far": "damage on the runner by this point",
             "pushers_so_far": "enemies who pushed the runner by this point"},
    "C.map": {"run_dist": "distance from the team's spawn to the stand"},
    "C.strength": {"strength_gap": "team strength gap"}}, {"checkpoint_s": "seconds into the run"}),
 "flag_swing": ("R.3", {
    "S.scoreboard": {"flag_lead": "flag lead now (s)"},
    "P.10": {"waiting_runner": "a runner waiting", "backup_flag": "a backup flag", "stand_own": "own team holds the stand",
             "stand_enemy": "the enemy holds the stand", "own_boost_in": "seconds to own boost", "enemy_boost_in": "seconds to the enemy's boost"},
    "A.allocation": {"own_alive": "own players alive", "enemy_alive": "enemy players alive", "own_main": "own main", "enemy_main": "enemy main",
                     "own_flag_duty": "own players on flag duty", "enemy_flag_duty": "enemy players on flag duty",
                     "own_in_enemy_base": "own players in the enemy base", "enemy_in_own_base": "enemy players in own base"},
    "R.1": {"own_deaths_30s": "own deaths in the last 30 s", "enemy_deaths_30s": "enemy deaths in the last 30 s"},
    "C.clock": {"minute": "minute", "res_in": "seconds to the next res"},
    "C.map": {"run_dist": "distance from the team's spawn to the stand"},
    "C.strength": {"strength_gap": "team strength gap"}}, {}),
 "capture_speed": ("R.3", {
    "A.allocation": {"defenders_free": "defenders alive and not on flag duty", "escort": "the runner's escorts"},
    "A.mesa_free": {"pushers_10s": "defenders who pushed the runner in the run's first 10 s",
                    "control_10s": "conditions and knockdowns on the runner in the first 10 s", "damage_10s": "damage on the runner in the first 10 s"},
    "C.map": {"run_dist": "distance from the runner's spawn to the stand"},
    "C.strength": {"strength_gap": "defending team's strength gap"}}, {}),
 "power_play": ("K.4", {
    "A.allocation": {"size": "players up", "own_main": "own main", "enemy_main": "enemy main",
                     "short_dead": "share of the enemy's missing player-seconds: dead", "short_running": "running the flag",
                     "short_backside": "on the back side or push side", "short_base": "in a base or pit"},
    "R.3": {"flag_lead": "flag lead (s)"},
    "P.14": {"pushed": "pushed (1) or held (0)"},
    "K.2": {"dps_v_usual": "own damage per second against the usual of the players alive"},
    "K.5": {"enemy_prots_10s": "enemy prot casts per 10 s", "enemy_heal_s": "enemy healing per second"},
    "P.2": {"spikes_10s": "own spikes per 10 s", "spike_spread": "median spread of own spikes (s)"},
    "P.1": {"spikes_on_healers": "share of own spikes on healers"},
    "K.11": {"blinds_on_own_10s": "Blinds on own players per 10 s"},
    "C.strength": {"strength_gap": "team strength gap"}}, {"window_s": "seconds the power play lasted"}),
 "fight_outcome": ("R.2", {
    "A.allocation": {"own_local": "own players in the fight", "enemy_local": "enemy players in the fight"},
    "P.13": {"peel_defensive_diff": "own frontline damage share on attackers of own backline, minus the enemy's"},
    "P.17": {"ready_interrupt_diff": "interrupted after casting into a ready interrupt, per cast, own minus enemy",
             "dazed_casts_diff": "casts while Dazed, per cast, own minus enemy", "blind_attacks_diff": "attacks while Blind per player, own minus enemy"},
    "P.18": {"strip_right_diff": "share of strips on the best target in range, own minus enemy",
             "strip_value_diff": "value of enchantments stripped per 10 s, own minus enemy"},
    "P.19": {"blind_front_diff": "Blinds on the enemy frontline, own minus enemy", "blind_defensive_diff": "defensive Blinds, own minus enemy"},
    "P.2": {"spike_spread_diff": "median spike spread (s), own minus enemy", "spikes_diff": "spikes, own minus enemy"},
    "K.1": {"dps_v_usual_diff": "damage against the usual of the players alive, own minus enemy"},
    "P.5": {"hex_secs_diff": "value-weighted seconds hexes stayed on own players, own minus enemy",
            "hex_right_diff": "share of hex removals that took the most costly hex in range, own minus enemy"},
    "C.strength": {"strength_gap": "team strength gap"}}, {}),
 "split_chance": ("A.allocation", {
    "S.scoreboard": {"flag_lead": "flag lead (s)", "own_alive": "own alive", "enemy_alive": "enemy alive", "own_main": "own main",
                     "enemy_main": "enemy main", "stand_own": "own team holds the stand", "stand_enemy": "the enemy holds the stand"},
    "C.clock": {"minute": "minute", "res_in": "seconds to the next res"},
    "C.builds": {"own_speed": "speed skills on own bars", "own_snares": "snares on own bars", "enemy_snares": "snares on enemy bars"},
    "C.strength": {"strength_gap": "team strength gap"}}, {}),
 "split_answer": ("P.11", {
    "S.scoreboard": {"flag_lead": "defenders' flag lead (s)", "def_alive": "defenders alive", "att_main": "attackers' main"},
    "A.mesa_free": {"def_free": "defenders alive and not on flag duty", "nearest_to_base": "nearest defender to its base at the split's entry"},
    "A.allocation": {"size": "split size"},
    "C.clock": {"minute": "minute"},
    "C.strength": {"strength_gap": "defending team's strength gap"}}, {}),
 "split_effect": ("R.5", {
    "P.11": {"latency": "seconds until the first defender arrived (60 = never)", "defenders": "defenders who came"},
    "A.allocation": {"size": "split size", "main_diff": "own main minus enemy main meanwhile"},
    "K.8": {"split_healers": "healers in the split"},
    "C.strength": {"strength_gap": "splitting team's strength gap"}}, {}),
 "collapse": ("R.1", {
    "P.11": {"latency": "seconds until the first defender arrived (60 = never)"},
    "P.9": {"defenders_10s": "defenders arriving within 10 s of the first"},
    "C.builds": {"def_snares": "snares on the defending team's bars", "split_speed": "speed skills on the splitting team's bars"},
    "A.allocation": {"size": "split size", "main_diff": "own main minus enemy main meanwhile"},
    "C.strength": {"strength_gap": "splitting team's strength gap"}}, {}),
}
# why each link that a node needs and the map may lack is a hypothesis, and who it came from
NEW_LINK_WHY = {
    ("K.11", "R.3"): ("control on the runner (Cripple, knockdowns) stops a run; read at the same point of every run", "Denning"),
    ("C.strength", "R.3"): ("stronger teams play better at everything; kept in every model so play isn't confused with strength", "Claude"),
    ("S.scoreboard", "R.3"): ("a flag lead tends to grow or shrink by how it stands now (boost and run timing)", "Claude"),
    ("R.1", "R.3"): ("deaths lose flag position: the runner, the escort or the main", "Claude"),
    ("C.clock", "R.3"): ("the res clock and the minute change what a run can do", "Claude"),
    ("A.mesa_free", "R.3"): ("defenders free to push a runner slow the enemy's capture", "Denning"),
    ("A.allocation", "K.4"): ("a power play is any numbers advantage at main, an 8v7 while the enemy runs included", "Denning"),
    ("A.allocation", "R.2"): ("numbers in a fight decide much of it", "Denning"),
    ("P.13", "R.2"): ("frontline defensive peel (hitting or snaring enemies on its own backline) protects the healers", "Denning"),
    ("P.17", "R.2"): ("wrong casts lose fights: casting into ready interrupts without cancelling, casting while Dazed, attacking while Blind", "Denning"),
    ("P.18", "R.2"): ("strips on the right target (Elementalist enchantments when defensive, prots off a target under attack)", "Denning"),
    ("P.19", "R.2"): ("Blind on the enemy frontline, above all on players hitting own healers, is defensive play", "Denning"),
    ("P.2", "R.2"): ("off spike timing fails to kill", "Denning"),
    ("K.1", "R.2"): ("damage output against the role's usual", "Denning"),
    ("P.5", "R.2"): ("the right hexes removed, and fast", "Denning"),
    ("C.strength", "R.2"): ("stronger teams play better at everything; kept in every model so play isn't confused with strength", "Claude"),
    ("S.scoreboard", "A.allocation"): ("a team splits from the situation: flag lead, stand, numbers", "Claude"),
    ("C.clock", "A.allocation"): ("the res clock and the minute change when a split pays", "Claude"),
    ("C.builds", "A.allocation"): ("split builds (speed, snares) and the enemy's snares decide whether a split is possible", "Claude"),
    ("C.strength", "A.allocation"): ("stronger teams play better at everything; kept in every model so play isn't confused with strength", "Claude"),
    ("A.mesa_free", "P.11"): ("free defenders near the base answer a split sooner", "Denning"),
    ("A.allocation", "P.11"): ("a bigger split draws more defenders", "Claude"),
    ("P.9", "R.1"): ("collapse timing: defenders arriving together kill a split member", "Denning"),
    ("C.builds", "R.1"): ("a snare on the split defender makes a collapse on a lone attacker much more likely to kill", "Denning"),
    ("A.allocation", "R.1"): ("a split outnumbered at the point of contact dies", "Claude"),
    ("C.strength", "R.1"): ("stronger teams play better at everything; kept in every model so play isn't confused with strength", "Claude"),
    ("C.strength", "R.5"): ("stronger teams play better at everything; kept in every model so play isn't confused with strength", "Claude"),
    ("C.strength", "P.11"): ("stronger teams play better at everything; kept in every model so play isn't confused with strength", "Claude"),
    ("C.clock", "P.11"): ("the res clock and the minute change how a split is answered", "Claude"),
}
NEW_NODES = [
    {"id": "P.17", "layer": "play", "name": "Wrong casts", "description": "casting into a ready interrupt without cancelling, casting while Dazed, attacking while Blind (every role)", "how": "eventlayer.py casts"},
    {"id": "P.18", "layer": "play", "name": "Enchantment strips", "description": "strips on the best target in range, valued from data (an enchantment's recorded output plus the bearer's measured drop after a strip)", "how": "eventlayer.py strips, values()"},
    {"id": "P.19", "layer": "play", "name": "Blind on enemies", "description": "Blind on the enemy frontline, and on players hitting own healers (defensive)", "how": "eventlayer.py blinds"},
]


def features(node):
    tgt, groups, base = SPEC[node]
    return list(base) + [f for g in groups.values() for f in g]


def describe(node, f):
    tgt, groups, base = SPEC[node]
    if f in base: return base[f]
    for g in groups.values():
        if f in g: return g[f]
    return ""


# ---------------------------------------------------------------- rows (lnrows.py)
from lnrows import node_rows, _rows_job, _vhash


# ---------------------------------------------------------------- fitting
def _ebm(n_matches, regression, bags=4):
    from interpret.glassbox import ExplainableBoostingClassifier as EBM, ExplainableBoostingRegressor as EBR
    kw = dict(max_bins=16, outer_bags=bags, min_samples_leaf=20 if not regression else 8, max_rounds=400, interactions=0, random_state=7)
    return (EBR if regression else EBM)(**kw)


def _job(job):
    """One fit: a held-out fold's score (and the baseline's), or the final model. Top level for parallel.py."""
    kind, regression, n, Xtr, ytr, Xte, yte = job
    # the held-out link tests use 2 bags (the same for every variant, so the comparison is fair; measured 2026-11-07:
    # half the time); the final readable model uses 4
    e = _ebm(n, regression, 4 if kind == "full" else 2).fit(Xtr, ytr)
    if kind == "full": return e
    if regression:
        p = e.predict(Xte); return {"score": float(np.mean(np.abs(yte - p))), "base": float(np.mean(np.abs(yte - np.median(ytr)))), "n": len(yte)}
    p = np.clip(e.predict_proba(Xte)[:, 1], .002, .998); q = float(np.clip(np.mean(ytr), .002, .998))
    ll = lambda pp: float(np.mean(-(yte * np.log(pp) + (1 - yte) * np.log(1 - pp))))
    return {"score": ll(p), "base": ll(np.full(len(yte), q)), "n": len(yte)}


def frame(node, ids, V):
    import pandas as pd, parallel
    from integrity import usable
    ids = usable(list(ids))
    rows = [r for L in parallel.run(_rows_job, [(node, rid, V) for rid in ids]) for r in L]
    df = pd.DataFrame(rows)
    feats = features(node)
    for f in feats:
        if f not in df: df[f] = np.nan
    y = df["y"].astype(float if node in REGRESSION else int)
    return df, df[feats].astype(float), y, df["match"]


def fit_all(ids, nodes=None, V=None):
    """Fit every node, its held-out score, and each link's strength (refit without the link's features), all fits
    pooled on every core. Returns {node: summary}; writes data/model/nodes/L_<node>.json."""
    import parallel, eventlayer as EL
    from sklearn.model_selection import GroupKFold
    V = V or EL.load_values() or EL.values(ids)
    nodes = nodes or list(SPEC)
    prep, jobs, owner = {}, [], []
    for node in nodes:
        df, X, y, g = frame(node, ids, V)
        if len(df) < 40 or g.nunique() < 6 or (node not in REGRESSION and y.nunique() < 2): continue
        reg = node in REGRESSION
        folds = list(GroupKFold(n_splits=6).split(X, y, g))
        variants = [("all", list(X.columns))] + [(grp, [c for c in X.columns if c not in fs]) for grp, fs in SPEC[node][1].items()]
        prep[node] = (df, X, y, g, folds, variants)
        for vn, cols in variants:
            for tr, te in folds:
                jobs.append(("fold", reg, g.iloc[tr].nunique(), X.iloc[tr][cols], y.iloc[tr].values, X.iloc[te][cols], y.iloc[te].values)); owner.append((node, vn))
        jobs.append(("full", reg, g.nunique(), X, y.values, None, None)); owner.append((node, "full"))
    res = parallel.run(_job, jobs)
    out = {}
    for node, (df, X, y, g, folds, variants) in prep.items():
        reg = node in REGRESSION
        R_ = collections.defaultdict(list)
        for o, r in zip(owner, res):
            if o[0] == node: R_[o[1]].append(r)
        e = R_["full"][0]
        allf = R_["all"]
        wavg = lambda L, k: sum(x[k] * x["n"] for x in L) / sum(x["n"] for x in L)
        val = {"glass box": round(wavg(allf, "score"), 4), "simple baseline": round(wavg(allf, "base"), 4),
               "metric": "mean absolute error (s)" if reg else "log loss"}
        val["verdict"] = "adds to the simple baseline" if val["glass box"] < val["simple baseline"] - (0.5 if reg else 0.0005) else "no better than the simple baseline yet"
        links = []
        for grp, fs in SPEC[node][1].items():
            d_ = [w["score"] - a_["score"] for w, a_ in zip(R_[grp], allf)]       # positive = the link helps on unseen matches
            mu = statistics.mean(d_); se = statistics.stdev(d_) / math.sqrt(len(d_)) if len(d_) > 1 else float("inf")
            status = "supported" if mu - 2 * se > 0 else "rejected" if mu + 2 * se < 0 else "not clear yet"
            links.append({"from": grp, "to": SPEC[node][0], "features": list(fs), "strength": round(mu, 4 if not reg else 2),
                          "plus_minus": round(se, 4 if not reg else 2), "status": status})
        terms = M.readable(e, list(X.columns), X) if not reg else __import__("nodes").readable_seconds(e, list(X.columns), X)
        for t in terms: t["description"] = describe(node, t["term"])
        rate = None if reg else round(float(y.mean()), 3)
        summary = {"node": node, "target": SPEC[node][0], "matches": int(g.nunique()), "rows": int(len(y)), "rate": rate,
                   "mean": round(float(y.mean()), 1) if reg else None, "validation": val, "links": links, "terms": terms,
                   "note": ("seconds added to (or taken off) the result, against the average" if reg else
                            "points = change in the chance of the result for an otherwise even (50%) case")}
        os.makedirs(NODE_DIR, exist_ok=True)
        json.dump(summary, open(os.path.join(NODE_DIR, f"L_{node}.json"), "w"), indent=1)
        _MODELS[node] = (e, list(X.columns))
        out[node] = summary
    return out


_MODELS = {}


def whatif(node, row, changes):
    """The node's reading for one row, and again with some features changed: (before, after) as a chance (%) or
    seconds. The fitted model is the one from the last fit_all in this process."""
    import pandas as pd
    e, cols = _MODELS[node]
    x0 = pd.DataFrame([{c: row.get(c) for c in cols}]).astype(float)
    x1 = x0.copy()
    for k, v in changes.items(): x1[k] = v
    if node in REGRESSION: return round(float(e.predict(x0)[0]), 1), round(float(e.predict(x1)[0]), 1)
    return round(float(e.predict_proba(x0)[0, 1]) * 100, 1), round(float(e.predict_proba(x1)[0, 1]) * 100, 1)


# ---------------------------------------------------------------- the causal map
def write_map(summaries):
    """Each measured link's strength and status into causal_map.json (adding the links and nodes the nodes need),
    every change logged in the map and in link_log.json."""
    c = json.load(open(MAP)); today = datetime.date.today().isoformat()
    have = {n["id"] for n in c["nodes"]}
    for n in NEW_NODES:
        if n["id"] not in have:
            c["nodes"].append(n); c["log"].append({"date": today, "change": f"node {n['id']} {n['name']} added (step 2b: {n['how']})", "by": "Claude, from Denning's list"})
    for nid, frm, why in (("P.17", "C.matchup", "the enemy's interrupts, Daze and Blind against own cancels and removal set how many casts go wrong"),
                          ("P.18", "C.builds", "strips come from the enchantment removal on own bars, and the targets from the enemy's enchantments"),
                          ("P.19", "C.builds", "Blind comes from the Blind skills on own bars")):
        if not any(l["to"] == nid for l in c["links"]):
            c["links"].append({"from": frm, "to": nid, "why": why, "source": "Claude", "confirmed_by_denning": False, "status": "hypothesis", "tactics": []})
            c["log"].append({"date": today, "change": f"link {frm} -> {nid} added as a hypothesis: {why}", "by": "Claude"})
    for n in c["nodes"]:
        if n["id"] == "P.5" and "hex" not in n.get("description", "").lower():
            n["description"] = (n.get("description", "") + "; hex removal: the right hexes removed (valued from data) and how fast").strip("; ")
            n["how"] = (n.get("how", "") + "; eventlayer.py hex_removals").strip("; ")
    log = json.load(open(LINK_LOG)) if os.path.exists(LINK_LOG) else []
    changes = 0
    for node, s in summaries.items():
        for L in s["links"]:
            pair = [l for l in c["links"] if l["from"] == L["from"] and l["to"] == L["to"]]
            if not pair:
                why, src = NEW_LINK_WHY.get((L["from"], L["to"]), ("needed by the node model " + node, "Claude"))
                nl = {"from": L["from"], "to": L["to"], "why": why, "source": src, "confirmed_by_denning": False, "status": "hypothesis", "tactics": []}
                c["links"].append(nl); pair = [nl]
                c["log"].append({"date": today, "change": f"link {L['from']} -> {L['to']} added as a hypothesis (node {node}): {why}", "by": src})
            meas = {"node": node, "strength": L["strength"], "plus_minus": L["plus_minus"], "status": L["status"],
                    "metric": s["validation"]["metric"], "matches": s["matches"], "features": L["features"], "date": today}
            for l in pair:
                old = l.get("measured", {}).get(node, {}).get("status")
                l.setdefault("measured", {})[node] = meas
                if old != L["status"]: changes += 1
            log.append({"date": today, "node": node, "from": L["from"], "to": L["to"], **{k: meas[k] for k in ("strength", "plus_minus", "status", "metric", "matches")}})
    # status from data: a link still a hypothesis, or one whose status the data set, follows its latest measurements
    # (supported if any node supports it, rejected if every node that measured it rejects it, else a hypothesis);
    # statuses set by Denning or by a formula are never changed (the measurement is recorded beside them)
    for l in c["links"]:
        ms = [v["status"] for v in (l.get("measured") or {}).values()]
        if not ms or not (l["status"] == "hypothesis" or l.get("status_by") == "data"): continue
        new = "supported" if "supported" in ms else "rejected" if all(x == "rejected" for x in ms) else "hypothesis"
        if new != l["status"]:
            c["log"].append({"date": today, "change": f"link {l['from']} -> {l['to']}: {l['status']} -> {new} by data ("
                             + ", ".join(f"{k} {v['status']} {v['strength']:+}" for k, v in l["measured"].items()) + ")", "by": "data"})
            l["status"] = new
        if new == "hypothesis": l.pop("status_by", None)
        else: l["status_by"] = "data"
    c["version"] = max(c.get("version", 10), 11)
    json.dump(c, open(MAP, "w"), indent=1, ensure_ascii=False)
    json.dump(log, open(LINK_LOG, "w"), indent=1)
    return changes


# ---------------------------------------------------------------- report lines
def report_lines(summaries):
    L = ["", "## 6b. The learned nodes (step 2 of the learned causal map)", "",
         "Each node uses only the causal-map links into it. A link's strength is how much worse the node predicts matches it "
         "never saw without that link's features (refit without them, same folds); supported when the gain is more than twice "
         "its spread across folds, rejected when dropping it helps by more than that, otherwise not clear yet.", ""]
    for node, s in summaries.items():
        v = s["validation"]; reg = node in REGRESSION
        what = (f"{s['rows']} cases, average {s['mean']} s" if reg else f"{s['rows']} cases, result rate {s['rate']:.0%}")
        L.append(f"**{node.replace('_', ' ')}** (map {s['target']}; {s['matches']} matches, {what}): {v['metric']} {v['glass box']} against "
                 f"{v['simple baseline']} for the simple baseline ({v['verdict']}).")
        for l in sorted(s["links"], key=lambda l: -l["strength"]):
            L.append(f"- link {l['from']} -> {l['to']}: gain {l['strength']:+} (+/- {l['plus_minus']}), {l['status']} ({', '.join(l['features'][:4])}{'...' if len(l['features']) > 4 else ''})")
        top = [t for t in s["terms"] if "curve" in t][:3]
        for t in top:
            cv = t["curve"]; lo, hi = cv[0], cv[-1]
            unit = "s" if reg else "points"
            L.append(f"  - leans on **{t['term']}** ({t['description']}): {lo['points']:+} {unit} at {lo['from']} to {lo['to']}, {hi['points']:+} at {hi['from']} to {hi['to']}")
        L.append("")
    return L


if __name__ == "__main__":
    a = sys.argv[1:]
    ids = [m for b in M.batches() for m in b["matches"]]
    if a and a[0] in ("fit", "write"):
        import time; t0 = time.time()
        S = fit_all(ids, a[1:] if a[0] == "fit" and len(a) > 1 else None)
        print("\n".join(report_lines(S)))
        if a[0] == "write": print("link status changes:", write_map(S))
        print(f"{time.time() - t0:.0f} s")
