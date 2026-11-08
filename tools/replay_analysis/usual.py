"""The usual play: for every decision point (decisions.py), what teams usually do in similar situations and how each
choice turned out, measured in win chance (causal map: decisions are caused by the situation; a choice that does better
than the usual play is a candidate "more optimal play").

- Outcome: the change in the deciding team's win chance over the decision's window, from a win model fitted WITHOUT that
  match (it never saw the result), so no guessed weights are involved. Components (deaths, NPCs, flag lead) are shown
  alongside so the number can be read.
- Choice: the decision's choice (ran, held, already running, pushed, reset, ...), refined by what the players actually
  did in the first 5 s (e.g. "held, fell back" against "held, fought"), not over the window, which the fight shapes.
- Usual play in a situation: the most common choice among the 15 most similar decisions of the same kind in OTHER
  matches (similar = flag lead, stand, boost clock, numbers, DP, NPCs, Lord damage, minute, strength gap, scaled).
- Choice effect: each choice's win-chance change against the most common choice, adjusted for the situation (a linear
  fit on the same variables, readable as one number per choice), with a 90% interval from resampling whole matches.
  With few matches most intervals include 0: "not enough data yet" is the honest reading.
- Pre-trend check (a placebo test): the same comparison on the change in win chance over the PRE_S seconds BEFORE the
  decision. A choice can't cause what happened before it, so a clear pre-trend difference means teams making that
  choice were already sliding (or rising): its effect is partly who chooses it, not what it does, and is marked so.
- Fight state (fightstate.py: enemy minus own expected deaths in the next 10 s) is part of every situation, so a choice
  is compared with teams that were winning or losing their fight about as much.

Usage:  python3 usual.py [--src DIR]     reads the analysis files (analyze.py --all --out DIR, default /tmp/ga), writes
                                         data/model/usual_play.json and prints the table per decision kind"""
import collections, statistics, glob, json, math, os, random, sys, warnings
import numpy as np
warnings.filterwarnings("ignore")
import model as M
from common import REPO

OUT = os.path.join(REPO, "data", "model", "usual_play.json")
K, BOOT, MIN_N = 15, 200, 25
SIT = ["flag_lead", "stand", "boost_in", "alive", "main", "dp", "npcs", "lord_damage", "minute", "strength_gap", "fight_state"]
PRE_S = 30                   # seconds before a decision for the pre-trend check
# variables only some decision kinds have (Denning): can the winners reach the enemy pit before its res; is the team
# losing its fight when the enemy's boost is near
# Snare matchup (Denning, after Bounty's and Nick's commentary: running the flag or splitting into a lot of snare is
# likely poor play; the data decides): own and enemy snare power of the live players and own speed power (movepower.py)
SNARE = ["own_snare_power", "enemy_snare_power", "own_speed_power"]
SIT_EXTRA = {"after_wipe": ["pit_margin_s"], "boost_clock": ["deaths_30s_diff", "main_diff_now", "health_diff"] + SNARE,
             "enemy_pickup": SNARE, "split_or_stay": SNARE, "runner_choice": SNARE,
             "split_in_base": ["split_size", "defender_snare_power", "attacker_self_defence", "main_diff_now", "health_diff",
                               # Denning (batch 10): collapse depends on what the split can get NPC-wise, its DP, and killability
                               "split_dp", "split_npc_dps", "def_npc_value", "split_healers"]}
# kinds whose choice effects are also split by the snare matchup (enemy snare power minus own speed power, in thirds)
SNARE_SPLIT = {"boost_clock", "enemy_pickup", "split_or_stay", "runner_choice"}
# per-player flags a choice's effect is also split by (Denning, B23), besides own spike build
SPLIT_BY = {"split_in_base": ["defender_snare"]}
# kinds whose choice effects are also split by the fight state (fightstate.py; Denning D4: falling back is likely a
# mistake unless losing the fight). Bands come from the data: the decisions of a kind split into thirds by fight state
# (lowest third = most behind in the fight, top third = most ahead), so every band has cases (Denning, batch 2).
FIGHT_SPLIT = {"boost_clock", "power_play", "enemy_pickup"}
# build axes (readable, from the skill data): what kind of build each team is; similar situations include similar builds
AXES = ["spike", "shutdown", "knockdowns", "defence", "sustain"]
# the map (Denning, 2026-11-07: the best play differs by guild hall): its measured geometry (features.py: flag run Y,
# pit-to-stand distance, distance between bases) is part of every situation's similarity, so the usual play compares
# decisions on similar maps, and enters the adjustment with the build axes; each choice's effect is also split by map
# name once a map has INTERACT_MIN cases of both the choice and the usual one. Geometry pools similar maps, so a map
# played rarely still borrows from maps shaped like it.
MAP_COLS = ["map_flag_run", "map_pit_to_stand", "map_bases_apart"]
BUILD_ADJUST_FROM = 150      # decisions of a kind before build axes enter the adjustment (they're fixed per match)
INTERACT_MIN = 10            # cases per cell before a choice's effect is split by build


def build_axes(rid):
    """Build axes per team tag: spike (a spike build), shutdown (interrupts, energy denial, Daze, Blind), knockdowns,
    defence (prots, blocks, Aura of Stability), sustain (heals, condition and hex removal)."""
    from replaylib import Match
    from buildfeat import team_features
    from scoreboard import archetype
    m = Match.from_branch(rid); out = {}
    for tm in (1, 2):
        f = team_features(m, tm); a = archetype(m, tm)
        out[m.tag[tm]] = {"spike": int(a["spike"]), "shutdown": f["interrupts"] + f["energy_denial"] + f["daze"] + f["blind"],
                          "knockdowns": f["knockdowns"], "defence": f["prots"] + f["blocks"] + f["aura_of_stability"],
                          "sustain": f["heals"] + f["condition_removal"] + f["hex_removal"], "kind": a["kind"]}
    return out


def refine(r):
    """The choice plus what the players did in its first seconds (decisions.FIRST_W; Denning: the 20 s that follow are
    partly the fight's result): the most common action among players not carrying."""
    acts = collections.Counter(v for v in (r.get("first_actions") or r["actions"])["by_role"].values() if v not in ("carrying", "died"))
    top = acts.most_common(1)[0][0] if acts else None
    base = r["choice"].split(":")[0]
    if r["kind"] == "split_in_base": return (r.get("extra") or {}).get("response") or base
    if r["kind"] == "late_game":            # Lord commitment from 24:00, in levels
        n = float(r["choice"].split()[0])
        return "0 to 1 at the enemy Lord" if n < 1.5 else ("2 to 3 at the enemy Lord" if n < 3.5 else "4+ at the enemy Lord")
    return f"{base}, {top}" if r["kind"] in ("enemy_pickup", "boost_clock", "power_play") and top else base


def situation(r, gap):
    k = r["state"]
    num = lambda s: int(s.split("v")[0]) - int(s.split("v")[1])
    out = {"flag_lead": k["flag_lead"], "stand": {"own": 1, "enemy": -1}.get(k["stand"], 0), "boost_in": k["boost_in"] or 0,
           "alive": num(k["alive"]), "main": num(k["main"]), "dp": k["dp"], "npcs": k["npcs"], "lord_damage": k["lord_damage"],
           "minute": r["t"] / 60, "strength_gap": gap or 0, "fight_state": r.get("fight_state") or 0}
    for v in SIT_EXTRA.get(r["kind"], []): out[v] = (r.get("extra") or {}).get(v) or 0
    for side in ("own", "enemy"):
        for ax in AXES: out[f"{side}_{ax}"] = r["axes"][side][ax]
    for c in MAP_COLS: out[c] = (r.get("map_geo") or {}).get(c) or 0
    return out


def load(src):
    recs = []
    for f in sorted(glob.glob(os.path.join(src, "*.json"))):
        a = json.load(open(f))
        if not __import__("common").counts(a["id"]): continue        # before common.TRAIN_FROM
        ax = build_axes(a["id"])
        try: row0 = next(iter(M.match_table(a["id"])), {})
        except Exception: row0 = {}
        geo = {c: row0.get(c) for c in MAP_COLS}
        for r in a.get("decisions", []):
            other = next(t for t in ax if t != r["team"])
            recs.append({"match": a["id"], **r, "axes": {"own": ax[r["team"]], "enemy": ax[other]},
                         "map": a["meta"].get("map"), "map_geo": geo})
    return recs


def wp_change(recs):
    """Win-chance change over each decision's window, from a model that never saw that match."""
    ids = [m for b in M.batches() for m in b["matches"]]
    by_match = collections.defaultdict(list)
    for r in recs: by_match[r["match"]].append(r)
    for mid, L in by_match.items():
        if mid not in ids: continue
        wp = M.WPModel.heldout(ids, mid)
        tab = {(x["team"], x["t"]): x for x in M.match_table(mid)}
        for r in L:
            t0 = r["t"] - r["t"] % 5; t1 = t0 + r["outcome"]["window_s"] - r["outcome"]["window_s"] % 5
            last = max(tt for (tm_, tt) in tab if tm_ == r["team"])
            a, b = tab.get((r["team"], t0)), tab.get((r["team"], min(t1, last))) or tab.get((r["team"], min(t1, last) - 5))
            if a and b:
                r["wp_before"] = wp.explain(a)[0]; r["wp_after"] = wp.explain(b)[0]
                r["wp_change"] = round(r["wp_after"] - r["wp_before"], 1); r["gap"] = a.get("strength_gap")
                p0 = tab.get((r["team"], max(t0 - PRE_S, 0)))
                r["wp_pre"] = round(r["wp_before"] - wp.explain(p0)[0], 1) if p0 and t0 >= PRE_S else None
                import fightstate
                r["fight_state"] = fightstate.diff(mid, t0, r["team"])
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
        build_cols = [f"{side}_{a}" for side in ("own", "enemy") for a in AXES]
        adj_cols = SIT + SIT_EXTRA.get(kind, []) + (build_cols + MAP_COLS if len(L) >= BUILD_ADJUST_FROM else [])
        nb_cols = SIT + SIT_EXTRA.get(kind, []) + build_cols + MAP_COLS     # similarity always includes builds and the map
        X = np.array([[r["sit"][k] for k in adj_cols] for r in L], float)
        XN = np.array([[r["sit"][k] for k in nb_cols] for r in L], float)
        ZN = (XN - XN.mean(0)) / (XN.std(0) + 1e-9)
        mu, sd = X.mean(0), X.std(0) + 1e-9; Z = (X - mu) / sd
        ref = choices[0]
        D = np.array([[1.0 if r["choice2"] == c else 0.0 for c in choices[1:]] for r in L])
        y = np.array([r["wp_change"] for r in L], float)
        matches = sorted({r["match"] for r in L})
        pre = np.array([r["wp_pre"] if r.get("wp_pre") is not None else np.nan for r in L], float)
        def fit(idx, yy=y):
            idx = np.array([i for i in idx if not np.isnan(yy[i])])
            A = np.hstack([np.ones((len(idx), 1)), Z[idx], D[idx]])
            coef, *_ = np.linalg.lstsq(A, yy[idx], rcond=None)
            return coef[-len(choices) + 1:]
        est = fit(np.arange(len(L))); est_pre = fit(np.arange(len(L)), pre)
        rnd = random.Random(7); boots = []; boots_pre = []
        mi = collections.defaultdict(list)
        for i, r in enumerate(L): mi[r["match"]].append(i)
        for _ in range(BOOT):
            idx = [i for mm in (rnd.choice(matches) for _ in matches) for i in mi[mm]]
            try: boots.append(fit(np.array(idx))); boots_pre.append(fit(np.array(idx), pre))
            except Exception: pass
        boots = np.array(boots); boots_pre = np.array(boots_pre)
        rows = [{"choice": ref, "n": counts[ref], "share": round(counts[ref] / len(L), 2), "raw_wp_change": round(float(np.mean([r["wp_change"] for r in L if r["choice2"] == ref])), 1),
                 "effect_vs_usual": 0.0, "interval": [0.0, 0.0]}]
        for j, c in enumerate(choices[1:]):
            lo, hi = (np.percentile(boots[:, j], [5, 95]) if len(boots) else (None, None))
            plo, phi = (np.percentile(boots_pre[:, j], [5, 95]) if len(boots_pre) else (0, 0))
            pre_clear = bool(plo > 0 or phi < 0)
            rows.append({"choice": c, "n": counts[c], "share": round(counts[c] / len(L), 2),
                         "raw_wp_change": round(float(np.mean([r["wp_change"] for r in L if r["choice2"] == c])), 1),
                         "effect_vs_usual": round(float(est[j]), 1), "interval": [round(float(lo), 1), round(float(hi), 1)],
                         "clear": bool(lo > 0 or hi < 0),
                         "pre_trend_vs_usual": round(float(est_pre[j]), 1), "pre_interval": [round(float(plo), 1), round(float(phi), 1)],
                         "selection_warning": pre_clear})
        # usual play per decision: most common choice among the K most similar decisions in other matches
        flagged = []
        eff = {x["choice"]: x["effect_vs_usual"] for x in rows}
        for i, r in enumerate(L):
            dist = np.sqrt(((ZN - ZN[i]) ** 2).sum(1)); order = [j for j in np.argsort(dist) if L[j]["match"] != r["match"]][:K]
            usual = collections.Counter(L[j]["choice2"] for j in order).most_common(1)[0][0]
            r["usual"] = usual
            if r["choice2"] != usual and abs(eff[r["choice2"]] - eff[usual]) >= 3:
                flagged.append({"match": r["match"], "team": r["team"], "t": r["t"], "chose": r["choice2"], "usual": usual,
                                "difference": round(eff[r["choice2"]] - eff[usual], 1), "wp_change": r["wp_change"]})
        # choice effects split by build (own spike build or not), only where each cell has enough cases
        by_build = []
        splits = [("own build", lambda r: r["sit"]["own_spike"], {0: "not spike", 1: "spike"})]
        splits += [(f, (lambda f: lambda r: int(bool((r.get("extra") or {}).get(f))))(f), {0: "no", 1: "yes"})
                   for f in SPLIT_BY.get(kind, [])]
        maps = sorted({r.get("map") for r in L if r.get("map")})
        splits.append(("map", lambda r: r.get("map"), {mp: mp for mp in maps}))
        if kind in FIGHT_SPLIT:
            fs = np.array([r["sit"]["fight_state"] for r in L], float)
            lo3, hi3 = np.percentile(fs, [100 / 3, 200 / 3])
            band = lambda r, lo3=lo3, hi3=hi3: (-1 if r["sit"]["fight_state"] <= lo3 else 1 if r["sit"]["fight_state"] > hi3 else 0)
            splits.append(("fight", band, {-1: f"behind in the fight (lowest third, {lo3:+.2f} or less)",
                                           0: "middle third", 1: f"ahead in the fight (top third, above {hi3:+.2f})"}))
        if kind in SNARE_SPLIT:
            sm = lambda r: r["sit"].get("enemy_snare_power", 0) - r["sit"].get("own_speed_power", 0)
            sv = np.array([sm(r) for r in L], float)
            slo, shi = np.percentile(sv, [100 / 3, 200 / 3])
            sband = lambda r, slo=slo, shi=shi: (-1 if sm(r) <= slo else 1 if sm(r) > shi else 0)
            splits.append(("snare", sband, {-1: f"little enemy snare for own speed (lowest third, {slo:+.0f} or less)",
                                            0: "middle third", 1: f"a lot of enemy snare for own speed (top third, above {shi:+.0f})"}))
        for c in choices[1:]:
            for name, get, labels in splits:
                for sp in labels:
                    a_ = [r["wp_change"] for r in L if r["choice2"] == c and get(r) == sp]
                    b_ = [r["wp_change"] for r in L if r["choice2"] == ref and get(r) == sp]
                    cell = {"choice": c, name: labels[sp], "n": len(a_), "n_usual": len(b_)}
                    if len(a_) >= INTERACT_MIN and len(b_) >= INTERACT_MIN:
                        cell["raw_difference"] = round(float(np.mean(a_) - np.mean(b_)), 1)
                    elif name == "map": continue
                    elif name != "own build":
                        cell["note"] = "too few yet"
                        cell["raw_mean"] = round(float(np.mean(a_)), 1) if a_ else None
                        cell["raw_mean_usual"] = round(float(np.mean(b_)), 1) if b_ else None
                    else: continue
                    by_build.append(cell)
        out[kind] = {"n": len(L), "matches": len(matches), "reference": ref, "choices": rows, "adjusted_for": adj_cols,
                     "by_build": by_build,
                     "unusual_choices": sorted(flagged, key=lambda f: -abs(f["difference"]))[:10]}
    return out


def collapse_cost(recs, late=20):
    """Collapses on a split (Denning, S31, S32): how long the collapsers were away from main, what the main fight lost
    meanwhile, what the collapse gained (split member killed), and the change in win chance, by time away and by match
    phase (before and from minute `late`)."""
    L = [r for r in recs if r["kind"] == "split_in_base" and (r.get("extra") or {}).get("collapse_away_s") is not None]
    def row(X):
        if not X: return None
        e = [r["extra"] for r in X]
        return {"n": len(X), "away_s_median": statistics.median(x["collapse_away_s"] for x in e),
                "killed_split": sum(x["split_died"] for x in e), "collapser_died": sum(x["collapser_died"] for x in e),
                "own_deaths_at_main": round(statistics.mean(x["away_deaths_own"] for x in e), 2),
                "enemy_deaths_at_main": round(statistics.mean(x["away_deaths_enemy"] for x in e), 2),
                "flag_lead_change": round(statistics.mean(x["away_flag_lead_change"] for x in e), 1),
                "dp_change": round(statistics.mean(x["away_dp_change"] for x in e), 1),
                "win_change": round(statistics.mean(r["wp_change"] for r in X), 1)}
    groups = {"all": L,
              "away under 30 s": [r for r in L if r["extra"]["collapse_away_s"] < 30],
              "away 30 to 60 s": [r for r in L if 30 <= r["extra"]["collapse_away_s"] < 60],
              "away 60 s or more": [r for r in L if r["extra"]["collapse_away_s"] >= 60],
              f"before {late}:00": [r for r in L if r["t"] < late * 60],
              f"from {late}:00": [r for r in L if r["t"] >= late * 60],
              "split member killed": [r for r in L if r["extra"]["split_died"]],
              "no kill": [r for r in L if not r["extra"]["split_died"]]}
    return {k: row(v) for k, v in groups.items() if v}


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
                  f"[{c['interval'][0]:+.1f}, {c['interval'][1]:+.1f}]" + ("  CLEAR" if c.get("clear") else "")
                  + (f" | before: {c['pre_trend_vs_usual']:+.1f}" + ("  ALREADY DIFFERENT BEFORE" if c.get("selection_warning") else "") if "pre_trend_vs_usual" in c else ""))
