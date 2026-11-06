"""Node models along the causal map (data/model/causal_map.json): each explains one result from what happened before it,
so the engine can say WHY, not only who is winning. Glass box (Explainable Boosting Machine), readable, tested on
matches it never saw. Time order is enforced: every feature is measured at or before the moment, the label after it.

Nodes so far:
- deaths: one row per alive player every SAMPLE s; label = the player dies within HORIZON s. Features: the player's
  state (health, health ceiling, damage taken, attackers, knockdowns, Daze, Deep Wound, cripple, interrupts, prots and
  blocks up, conditions it took on itself), its support (healers in range, healers dead, allies and enemies near, local
  numbers, distance from its group and pit), the situation (res timer, flag lead, minute, strength gap) and the
  matchup (enemy threats against own answers). Rows with no damage taken in 10 s are kept at 1 in NEG_KEEP and weighted.
- kill_conversion: one row per burst (3+ attackers, 250+ damage in 2 s on one target); label = the target dies within
  8 s. Features: the target's defence (prots and blocks up, healers in range, health, ceiling, knocked down, Dazed),
  the attackers' shutdown (Blind, interrupts and knockdowns on them in the last 5 s), the burst itself, the matchup.

Usage:  python3 nodes.py fit [deaths|kill_conversion]   fit on the trained batches, write data/model/nodes/<node>.json and
                                                        .md, print validation and what it leans on
        python3 nodes.py explain <report id> <m:ss> <team role>   why that player's death risk was what it was
In code: node_rows(node, rid), fit_node(node, ids) -> (summary, model)."""
import bisect, collections, json, math, os, random, statistics, sys, warnings
import numpy as np
warnings.filterwarnings("ignore")
from common import REPO, CAST_R, PROT_SKILLS, BLOCKS, RES_EVERY
import model as M
from buildfeat import matchup

NODE_DIR = os.path.join(REPO, "data", "model", "nodes")
CACHE = "/tmp/gvg_node_rows"
SAMPLE, HORIZON, NEG_KEEP = 3, 10, 4
MATCHUP_KEYS = ["enemy_knockdowns_v_own_aura_of_stability", "enemy_interrupts", "enemy_energy_denial", "enemy_snares",
                "enemy_blind", "enemy_strips", "own_condition_removal", "own_prots"]


class Timeline:
    """Per-player event lists by second, built once per match, so features are quick to read at any second."""
    def __init__(self, st, sb):
        m = st.m
        self.st, self.sb, self.m = st, sb, m
        self.dmg_in = collections.defaultdict(list)       # victim -> [(t, dmg, attacker)]
        self.dmg_out = collections.defaultdict(list)
        for r in m.o["ev"]:
            if r[1] == "dm" and (r[5] or 0) > 0 and r[3] in m.PL and r[2] in m.PL and m.team(r[2]) != m.team(r[3]):
                self.dmg_in[r[3]].append((r[0] / 10, r[5], r[2])); self.dmg_out[r[2]].append((r[0] / 10, r[5], r[3]))
        self.kd = collections.defaultdict(list); self.ir = collections.defaultdict(list)
        for k in m.o.get("knockdowns", []): self.kd[k[2]].append(k[0] / 10)
        for i in m.o.get("interrupts", []): self.ir[i[3]].append(i[0] / 10)
        self.cond = collections.defaultdict(list)          # target -> [(start, end, name, source team)]
        self.ench = collections.defaultdict(list)          # target -> [(start, end, skill name)]
        for e in m.o.get("effects", []):
            if e[0] is None: continue
            s0, s1 = e[0] / 10, (e[1] or 10 ** 9) / 10
            if e[2] == "c" and e[7]: self.cond[e[5]].append((s0, s1, e[7], m.team(e[4]) if isinstance(e[4], int) else None))
            elif e[2] == "e": self.ench[e[5]].append((s0, s1, m.sk(e[3])))
        self.healers = {tm: [a for a in st.players[tm] if _healer(m, a)] for tm in st.teams}
        self.deaths = {a: sorted(st.death_times.get(a, [])) for a in m.PL}

    def window(self, L, t, w): return [x for x in L if t - w < x[0] <= t]

    def has_cond(self, a, t, names, own_source=None):
        tm = self.m.team(a)
        return any(s0 <= t <= s1 and n in names and (own_source is None or (src == tm) == own_source) for s0, s1, n, src in self.cond.get(a, []))

    def ench_up(self, a, t, names):
        return any(s0 <= t <= s1 and n in names for s0, s1, n in self.ench.get(a, []))

    def dies_within(self, a, t, h):
        L = self.deaths[a]; i = bisect.bisect_right(L, t)
        return i < len(L) and L[i] <= t + h


def _healer(m, a):
    from phases import healer
    return healer(m, a)


def death_features(tl, a, t, mu, gap):
    st, sb, m = tl.st, tl.sb, tl.m
    from state import d
    tm = m.team(a); p, s = st.pos(a, t)
    base = m.A[a].get("hp") or 500
    din3 = tl.window(tl.dmg_in[a], t, 3); din10 = tl.window(tl.dmg_in[a], t, 10)
    heal_live = [b for b in tl.healers[tm] if b != a and st.alive(b, t)]
    in_range = [b for b in heal_live if d(st.pos(b, t)[0], p) <= CAST_R]
    near = lambda team, r: sum(1 for b in st.players[team] if b != a and st.alive(b, t) and d(st.pos(b, t)[0], p) <= r)
    main = st.main_group(tm, t); c = st.centroid(main, t)
    sbt = sb.at(t)[m.tag[tm]]
    return {
        "is_healer": int(a in tl.healers[tm]), "line": {"frontline": 0, "midline": 1, "backline": 2}[__import__("common").line(m, a)],
        "health_pct": s["hp"], "health_ceiling": round(sb.eff_hp(a, t) / base, 2),
        "damage_taken_3s": sum(x[1] for x in din3), "damage_taken_10s": sum(x[1] for x in din10),
        "attackers_5s": len({x[2] for x in tl.window(tl.dmg_in[a], t, 5)}),
        "knocked_down_now": int(s["st"] == "k"), "knockdowns_10s": sum(1 for x in tl.kd[a] if t - 10 < x <= t),
        "interrupted_10s": sum(1 for x in tl.ir[a] if t - 10 < x <= t),
        "dazed": int(tl.has_cond(a, t, {"dazed"})), "crippled": int(tl.has_cond(a, t, {"crippled"})),
        "deep_wound": int(tl.has_cond(a, t, {"deep_wound"})),
        "conditions_self_taken": int(tl.has_cond(a, t, {"deep_wound", "burning", "bleeding", "poison", "crippled", "blind", "weakness", "dazed"}, own_source=True)),
        "prot_up": int(tl.ench_up(a, t, PROT_SKILLS)), "block_up": int(tl.ench_up(a, t, BLOCKS)),
        "healers_in_range": len(in_range), "healers_dead": sum(1 for b in tl.healers[tm] if b != a and not st.alive(b, t)),
        "allies_near": near(tm, 1500), "enemies_near": near(3 - tm, 1500), "local_diff": near(tm, 2000) - near(3 - tm, 2000),
        "dist_from_group": round(d(p, c)) if a not in main and c else 0,
        "dist_own_pit": round(d(p, st.geo.pit.get(tm))), "res_in": sbt and sb.at(t)["res_in"],
        "flag_lead": max(min(sbt["flag_lead"], 150), -150), "minute": round(t / 60, 1), "strength_gap": gap,
        **{k: mu[k] for k in MATCHUP_KEYS},
    }


DEATH_DESC = {
    "is_healer": "the player is a healer (1) or not (0)", "line": "0 frontline, 1 midline, 2 backline",
    "health_pct": "current health %", "health_ceiling": "maximum health after death penalty, as a share of normal",
    "damage_taken_3s": "damage taken in the last 3 s", "damage_taken_10s": "damage taken in the last 10 s",
    "attackers_5s": "different enemies who hit the player in the last 5 s", "knocked_down_now": "knocked down now",
    "knockdowns_10s": "knockdowns in the last 10 s", "interrupted_10s": "times interrupted in the last 10 s",
    "dazed": "Dazed now", "crippled": "Crippled now", "deep_wound": "Deep Wound now",
    "conditions_self_taken": "carrying a condition it took on itself from a teammate (Draw Conditions)",
    "prot_up": "a prot (Guardian, Spirit Bond, Life Sheath, Protective Spirit...) on the player now",
    "block_up": "a block enchantment up now", "healers_in_range": "own healers alive within cast range",
    "healers_dead": "own healers dead", "allies_near": "allies within 1,500", "enemies_near": "enemies within 1,500",
    "local_diff": "allies minus enemies within 2,000", "dist_from_group": "distance from its main group (0 if in it)",
    "dist_own_pit": "distance from its own pit", "res_in": "seconds until the next res", "flag_lead": "own flag lead (s)",
    "minute": "match minute", "strength_gap": "own minus enemy team strength",
    "enemy_knockdowns_v_own_aura_of_stability": "enemy knockdown skills minus own Auras of Stability (matchup)",
    "enemy_interrupts": "enemy interrupt skills", "enemy_energy_denial": "enemy energy-denial skills",
    "enemy_snares": "enemy snare skills", "enemy_blind": "enemy Blind skills", "enemy_strips": "enemy enchantment removal skills",
    "own_condition_removal": "own condition removal skills", "own_prots": "own prot skills",
}


def _build_rows(node, rid):
    from replaylib import Match
    from state import GameState
    from scoreboard import Scoreboard
    from strength import strength_gap
    st = GameState(Match.from_branch(rid)); sb = Scoreboard(st); m = st.m
    tl = Timeline(st, sb)
    rnd = random.Random(rid)
    gaps = {}
    for tm in st.teams:
        gaps[tm] = strength_gap(m.o["meta"]["id"], m.tag[tm], m.o["meta"].get("started"), m.tag[3 - tm],
                                {x["tag"]: x.get("rating") for x in m.o["meta"]["teams"]})[1]
    mus = {tm: matchup(m, tm) for tm in st.teams}
    rows = []
    if node == "deaths":
        last = st.end - 1 - HORIZON
        ends = {t for a in m.PL for t in st.death_times.get(a, []) if t >= st.end - 1}
        for t in range(5, int(last), SAMPLE):
            for a in m.PL:
                if not st.alive(a, t): continue
                y = int(tl.dies_within(a, t, HORIZON))
                active = bool(tl.window(tl.dmg_in[a], t, 10))
                if not y and not active:
                    if rnd.randrange(NEG_KEEP): continue
                    w = NEG_KEEP
                else: w = 1
                rows.append({"match": rid, "team": m.tag[m.team(a)], "role": m.roles[a], "t": t, "y": y, "w": w,
                             **death_features(tl, a, t, mus[m.team(a)], gaps[m.team(a)])})
    elif node == "kill_conversion":
        for v in m.PL:
            L = tl.dmg_in[v]; last = -99
            for i, (t, _, _) in enumerate(L):
                w = [x for x in L[i:] if x[0] <= t + 2]
                if sum(x[1] for x in w) < 250 or len({x[2] for x in w}) < 3 or t - last < 4 or t > st.end - 10: continue
                last = t; atk = {x[2] for x in w}; vt = m.team(v)
                f = death_features(tl, v, t, mus[vt], gaps[vt])
                blind = sum(1 for b in atk if tl.has_cond(b, t + 1, {"blind"}))
                rup = sum(1 for b in atk for x in tl.ir[b] if t - 5 < x <= t + 2)
                kdat = sum(1 for b in atk for x in tl.kd[b] if t - 5 < x <= t + 2)
                rows.append({"match": rid, "team": m.tag[3 - vt], "role": m.roles[v], "t": round(t), "y": int(tl.dies_within(v, t, 8)), "w": 1,
                             "target_is_healer": f["is_healer"], "target_line": f["line"], "target_health_pct": f["health_pct"],
                             "target_ceiling": f["health_ceiling"], "target_prot_up": f["prot_up"], "target_block_up": f["block_up"],
                             "target_healers_in_range": f["healers_in_range"], "target_knocked_down": f["knocked_down_now"],
                             "target_dazed": f["dazed"], "target_deep_wound": f["deep_wound"], "target_dist_from_group": f["dist_from_group"],
                             "burst_damage": round(sum(x[1] for x in w)), "attackers": len(atk), "attackers_blinded": blind,
                             "attackers_interrupted": rup, "attackers_knocked_down": kdat, "strength_gap": -f["strength_gap"] if f["strength_gap"] is not None else None,
                             "own_interrupts_v_enemy_heals": mus[3 - vt]["own_interrupts_v_enemy_heals"],
                             "enemy_prots": mus[3 - vt]["enemy_prots"], "enemy_blind": mus[3 - vt]["enemy_blind"], "minute": round(t / 60, 1)})
    return rows


KC_DESC = {"target_is_healer": "target is a healer", "target_line": "target 0 frontline, 1 midline, 2 backline",
           "target_health_pct": "target health % when the burst started", "target_ceiling": "target's health ceiling",
           "target_prot_up": "a prot on the target", "target_block_up": "a block on the target",
           "target_healers_in_range": "target's healers in range", "target_knocked_down": "target knocked down",
           "target_dazed": "target Dazed", "target_deep_wound": "target has Deep Wound",
           "target_dist_from_group": "target's distance from its group", "burst_damage": "damage in the 2 s burst",
           "attackers": "attackers in the burst", "attackers_blinded": "attackers Blind during the burst",
           "attackers_interrupted": "interrupts on the attackers (5 s before to 2 s after)",
           "attackers_knocked_down": "knockdowns on the attackers (5 s before to 2 s after)",
           "strength_gap": "attacking minus target team strength", "own_interrupts_v_enemy_heals": "attackers' interrupt skills minus target team's heals",
           "enemy_prots": "target team's prot skills", "enemy_blind": "target team's Blind skills", "minute": "match minute"}
DESC = {"deaths": DEATH_DESC, "kill_conversion": KC_DESC}


def node_rows(node, rid):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, f"{node}_{rid}.json")
    if not os.path.exists(p): json.dump(_build_rows(node, rid), open(p, "w"))
    return json.load(open(p))


MATCH_FIXED = {"deaths": set(MATCHUP_KEYS) | {"strength_gap"},
               "kill_conversion": {"own_interrupts_v_enemy_heals", "enemy_prots", "enemy_blind", "strength_gap"}}
STAGE_FIXED = 60     # matches before variables fixed for a whole match (matchup counts) are used (they fingerprint matches)


def features_for(node, n_matches):
    keep_fixed = {"strength_gap"} if n_matches < STAGE_FIXED else MATCH_FIXED[node]
    return [k for k in DESC[node] if k not in MATCH_FIXED[node] or k in keep_fixed]


def _frame(node, ids):
    import pandas as pd
    df = pd.DataFrame([r for rid in ids for r in node_rows(node, rid)])
    feats = features_for(node, df["match"].nunique())
    return df, df[feats].astype(float), df["y"].astype(int), df["match"], df["w"].astype(float)


def _ebm(n_matches):
    from interpret.glassbox import ExplainableBoostingClassifier as EBM
    return EBM(max_bins=16, outer_bags=4, min_samples_leaf=20, max_rounds=500, interactions=6 if n_matches >= 25 else 0,
               random_state=7)


def _wmetrics(p, y, w):
    p = np.clip(p, 0.002, 0.998)
    ll = float(np.sum(w * -(y * np.log(p) + (1 - y) * np.log(1 - p))) / np.sum(w))
    # ranking quality: how often a row that led to the result scores above one that didn't (AUC)
    from sklearn.metrics import roc_auc_score
    return {"log_loss": round(ll, 4), "auc": round(float(roc_auc_score(y, p, sample_weight=w)), 3), "rate": round(float(np.average(y, weights=w)), 4)}


def validate(node, df, X, y, g, w):
    from sklearn.model_selection import GroupKFold
    from sklearn.linear_model import LogisticRegression
    base_cols = {"deaths": ["health_pct", "damage_taken_3s"], "kill_conversion": ["burst_damage", "target_health_pct"]}[node]
    preds = {n: np.zeros(len(y)) for n in ("simple baseline", "glass box")}
    for tr, te in GroupKFold(n_splits=min(6, g.nunique())).split(X, y, g):
        b = LogisticRegression(max_iter=1000).fit(X.iloc[tr][base_cols].fillna(0), y.iloc[tr], sample_weight=w.iloc[tr])
        preds["simple baseline"][te] = b.predict_proba(X.iloc[te][base_cols].fillna(0))[:, 1]
        e = _ebm(g.iloc[tr].nunique()).fit(X.iloc[tr], y.iloc[tr], sample_weight=w.iloc[tr])
        preds["glass box"][te] = e.predict_proba(X.iloc[te])[:, 1]
    out = {n: _wmetrics(p, y.values, w.values) for n, p in preds.items()}
    out["baseline uses"] = base_cols
    out["verdict"] = "adds to the simple baseline" if out["glass box"]["log_loss"] < out["simple baseline"]["log_loss"] - 0.0005 else "no better than the simple baseline yet"
    return out, preds["glass box"]


def fit_node(node, ids):
    df, X, y, g, w = _frame(node, ids)
    val, held = validate(node, df, X, y, g, w)
    e = _ebm(g.nunique()).fit(X, y, sample_weight=w)
    terms = M.readable(e, list(X.columns), X)
    for t in terms:
        if "curve" in t: t["description"] = DESC[node].get(t["term"], t["description"])
    summary = {"node": node, "matches": int(g.nunique()), "rows": int(len(y)), "events": int(y.sum()), "validation": val,
               "note": "points = change in the chance of the result for an otherwise even (50%) case; read the direction and size, "
                       "not the absolute level", "terms": terms}
    os.makedirs(NODE_DIR, exist_ok=True)
    json.dump(summary, open(os.path.join(NODE_DIR, f"{node}.json"), "w"), indent=1)
    return summary, e, df, held


def explain_row(e, row, feats):
    import pandas as pd
    x = pd.DataFrame([{k: row.get(k) for k in feats}]).astype(float)
    contrib = e.eval_terms(x)[0]
    total = float(np.ravel(e.intercept_)[0]) + float(contrib.sum())
    parts = sorted([(e.term_names_[i], M._points(c)) for i, c in enumerate(contrib) if abs(M._points(c)) >= 1], key=lambda kv: -abs(kv[1]))
    return round(M.sig(total) * 100, 1), parts


if __name__ == "__main__":
    a = sys.argv[1:]
    ids = [m for b in M.batches() for m in b["matches"]]
    if a and a[0] == "fit":
        for node in (a[1:] or ["deaths", "kill_conversion"]):
            s, e, df, held = fit_node(node, ids)
            print(f"== {node}: {s['matches']} matches, {s['rows']} rows, {s['events']} events")
            print(json.dumps(s["validation"]))
            print([(t["term"], t["importance"]) for t in s["terms"][:12]])
    elif a and a[0] == "explain":
        rid, clock, who = a[1], a[2], " ".join(a[3:])
        t = int(clock.split(":")[0]) * 60 + int(clock.split(":")[1])
        others = [x for x in ids if x != rid]
        df, X, y, g, w = _frame("deaths", others)
        e = _ebm(g.nunique()).fit(X, y, sample_weight=w)
        rows = [r for r in node_rows("deaths", rid) if f"{r['team']} {r['role']}" == who]
        for r in sorted(rows, key=lambda r: abs(r["t"] - t))[:1] + [r for r in rows if t - 12 <= r["t"] <= t and r["t"] != sorted(rows, key=lambda r: abs(r["t"] - t))[0]["t"]]:
            p, parts = explain_row(e, r, list(X.columns))
            print(f"{r['t'] // 60}:{r['t'] % 60:02d} risk {p}% | " + ", ".join(f"{k} {v:+}" for k, v in parts[:8]))
