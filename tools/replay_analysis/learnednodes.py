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
  capture_speed    (R.3)  seconds an enemy capture took, from the defending side
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
CHECKPOINTS = (5, 15, 30)
REGRESSION = {"flag_swing", "capture_speed", "split_answer"}
CLIP = 150
NEVER = 60

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
    "A.mesa_free": {"nearest_defender": "nearest defender to the runner at mid-run", "pushers": "defenders who pushed the runner",
                    "first_push_s": "seconds into the run of the first push (none = the run's length)"},
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


# ---------------------------------------------------------------- rows
def _ctx(rid):
    """What every node's rows need from one match."""
    import tq, eventlayer as EL
    from replaylib import Match
    from state import GameState, d
    from strength import strength_gap
    from buildfeat import matchup
    a = tq._analysis(rid); R = EL.records(rid)
    st = GameState(Match.from_branch(rid)); m = st.m
    tags = [t["tag"] for t in a["meta"]["teams"]]
    tm_of = {m.tag[k]: k for k in (1, 2)}
    gaps = {}
    for tm in (1, 2):
        gaps[m.tag[tm]] = strength_gap(m.o["meta"]["id"], m.tag[tm], m.o["meta"].get("started"), m.tag[3 - tm],
                                       {x["tag"]: x.get("rating") for x in m.o["meta"]["teams"]},
                                       {m.tag[k]: [m.nm(x) for x in m.PL if m.team(x) == k] for k in (1, 2)})[1]
    mus = {m.tag[tm]: matchup(m, tm) for tm in (1, 2)}
    run_dist = {}
    for tg, tm in tm_of.items():
        try: run_dist[tg] = round(d(st.geo.spawn[tm], st.geo.stand))
        except Exception: run_dist[tg] = None
    return a, R, st, m, tags, tm_of, gaps, mus, run_dist


def _row(rows, t):
    best = None
    for r in rows:
        if r["t"] <= t: best = r
        else: break
    return best or rows[0]


def _short(why):
    tot = sum((why or {}).values()) or 1
    g = lambda ks: round(sum((why or {}).get(k, 0) for k in ks) / tot, 2)
    return {"short_dead": g(["dead"]), "short_running": g(["running flag"]), "short_backside": g(["backside", "push side"]),
            "short_base": g(["own base", "own pit", "enemy base", "enemy pit"])}


def _team_dps(team, tg, t0, t1, V, alive_roles):
    """A team's damage on enemy players per second in [t0, t1] against the sum of the usual of the players alive."""
    import eventlayer as EL
    b = team["bucket_s"]; L = team["dmg5"][tg]
    i0, i1 = int(t0 // b), max(int(t0 // b) + 1, int(math.ceil(t1 / b)))
    dmg = sum(L[i0:i1]); secs = (i1 - i0) * b
    us = sum(EL.usual_dps(V, r, None) or 0 for r in alive_roles)
    return round(dmg / secs / us, 2) if us and secs else None


def _build(node, rid, V):
    import eventlayer as EL
    a, R, st, m, tags, tm_of, gaps, mus, run_dist = _ctx(rid)
    R = EL.valued(json.loads(json.dumps(R)), V)
    sb, sr = a["scoreboard"], a["state"]
    foe = lambda tg: tags[1] if tg == tags[0] else tags[0]
    team = (R.get("team") or [{}])[0]
    roles_alive = lambda tg, t: (_row(sr, t)[tg].get("main_roles") or []) if sr else []
    deaths = a["deaths"]
    rows = []
    def add(tg, t, y, **f):
        rows.append({"match": rid, "team": tg, "t": t, "y": y, **f})
    if node == "run_outcome":
        rec = {(r["team"], r["t"]): r for r in R.get("runs", [])}
        for fr in a["flag_runs"]:
            r = rec.get((fr["team"], fr["start"]))
            if not r: continue
            tg = fr["team"]
            for k in CHECKPOINTS:
                if fr["secs"] <= k: continue
                ct = [c for c in r.get("control_times") or [] if c[0] <= k]
                add(tg, fr["start"] + k, int(fr["outcome"] == "captured"), checkpoint_s=k,
                    stand_own=int(r["stand"] == "own"), stand_enemy=int(r["stand"] == "enemy"), enemy_boost_in=r["enemy_boost_in"],
                    flag_lead=max(min(r["flag_lead"], CLIP), -CLIP), runner_line={"frontline": 0, "midline": 1, "backline": 2}.get(fr.get("line")),
                    escort=r["escort"], own_main=r["main"][0], enemy_main=r["main"][1], enemy_power_play=int(r["enemy_power_play"]),
                    crippled_so_far=int(any(c[1] == "crippled" for c in ct)), knocked_down_so_far=sum(1 for c in ct if c[1] == "knockdown"),
                    other_control_so_far=sum(1 for c in ct if c[1] not in ("crippled", "knockdown")),
                    damage_so_far=sum(x[1] for x in r.get("damage_times") or [] if x[0] <= k),
                    pushers_so_far=sum(1 for x in r.get("pusher_first") or [] if x <= k),
                    run_dist=run_dist.get(tg), strength_gap=gaps[tg])
    elif node == "flag_swing":
        by_t = {r["t"]: r for r in sb}; i = 0
        for r in sb:
            t = r["t"]
            if t < 20 or t % 20 or t + 60 not in by_t: continue
            tg = tags[i % 2]; i += 1; fg = foe(tg); s2 = by_t[t + 60]
            stt = _row(sr, t)
            zones = lambda x, z: sum(1 for v in (stt[x].get("zones") or {}).values() if v == z)
            own_b = r["stand"].get("boost_in") if r["stand"]["owner"] == tg else None
            en_b = r["stand"].get("boost_in") if r["stand"]["owner"] == fg else None
            lead = max(min(r[tg]["flag_lead"], CLIP), -CLIP)
            add(tg, t, max(min(s2[tg]["flag_lead"], CLIP), -CLIP) - lead, flag_lead=lead,
                waiting_runner=int(r[tg].get("waiting_runner") is not None), backup_flag=int(bool(r[tg].get("backup_flag"))),
                stand_own=int(r["stand"]["owner"] == tg), stand_enemy=int(r["stand"]["owner"] == fg), own_boost_in=own_b, enemy_boost_in=en_b,
                own_alive=r[tg]["alive"], enemy_alive=r[fg]["alive"], own_main=r[tg]["main"], enemy_main=r[fg]["main"],
                own_flag_duty=len(r[tg].get("flag_duty") or []), enemy_flag_duty=len(r[fg].get("flag_duty") or []),
                own_in_enemy_base=zones(tg, "enemy base") + zones(tg, "enemy pit"), enemy_in_own_base=zones(fg, "enemy base") + zones(fg, "enemy pit"),
                own_deaths_30s=sum(1 for x in deaths if x["team"] == tg and t - 30 < x["t"] <= t),
                enemy_deaths_30s=sum(1 for x in deaths if x["team"] == fg and t - 30 < x["t"] <= t),
                minute=round(t / 60, 1), res_in=r.get("res_in"), run_dist=run_dist.get(tg), strength_gap=gaps[tg])
    elif node == "capture_speed":
        rec = {(r["team"], r["t"]): r for r in R.get("runs", [])}
        for c in R.get("caps", []):
            r = rec.get((c["team"], c["t"] - c["secs"])) or next((x for x in R.get("runs", []) if x["team"] == c["team"] and abs(x["t"] + x["secs"] - c["t"]) <= 2), None)
            pf = (r or {}).get("pusher_first") or []
            add(c["defender"], c["t"], c["secs"], defenders_free=c["defenders_free"], escort=c["escort"], nearest_defender=c["nearest_defender"],
                pushers=c["pushers"], first_push_s=pf[0] if pf else c["secs"], run_dist=run_dist.get(c["team"]), strength_gap=gaps[c["defender"]])
    elif node == "power_play":
        for p in R.get("power", []):
            tg, fg = p["team"], foe(p["team"]); t0, t1 = p["t"], p["t"] + max(p["window_s"], 5); w = (t1 - t0) / 10
            sp = [x for x in R.get("spikes", []) if x["team"] == tg and t0 <= x["t"] <= t1]
            hb = team.get("heal5", {}).get(fg) or []; b = team.get("bucket_s", 5)
            eh = sum(hb[int(t0 // b):max(int(t0 // b) + 1, int(math.ceil(t1 / b)))]) / max(t1 - t0, 1)
            try: own, en = map(int, p["main"].split("v"))
            except ValueError: continue
            add(tg, t0, int(p["kills"] > 0), window_s=round(t1 - t0), size=p["size"], own_main=own, enemy_main=en, **_short(p["enemy_short_because"]),
                flag_lead=max(min(p["flag_lead"], CLIP), -CLIP), pushed=int(p["choice"] == "pushed"),
                dps_v_usual=_team_dps(team, tg, t0, t1, V, roles_alive(tg, t0)),
                enemy_prots_10s=round(sum(1 for x in team.get("prot_casts", []) if x[1] == fg and t0 <= x[0] <= t1) / w, 2), enemy_heal_s=round(eh, 1),
                spikes_10s=round(len(sp) / w, 2), spike_spread=statistics.median([x["spread_s"] for x in sp]) if sp else None,
                spikes_on_healers=round(sum(1 for x in sp if x["target_class"] == "healer") / len(sp), 2) if sp else None,
                blinds_on_own_10s=round(sum(1 for x in R.get("blinds", []) if x["team"] == fg and t0 <= x["t"] <= t1) / w, 2),
                strength_gap=gaps[tg])
    elif node == "fight_outcome":
        for fi, f in enumerate(a.get("fights") or []):
            # fights.py stores each fight from the side that lost it; alternate the side read so both outcomes appear
            tg = f["team"] if fi % 2 == 0 else foe(f["team"]); fg = foe(tg)
            if f.get("opponent_won_fight") is None: continue
            t0 = f["start"] - 5
            first = min([x[0] for x in f.get("deaths") or []] or [f["end"]])
            t1 = max(first, f["start"] + 5)
            def side(x):
                cs = [c for c in R.get("casts", []) if c["fight"] == fi and c["team"] == x]
                n = sum(c["casts"] for c in cs) or None
                pl = len(cs) or None
                pe = [c["defensive_share"] for c in R.get("peel", []) if c["fight"] == fi and c["team"] == x]
                s_ = [r for r in R.get("strips", []) if r["team"] == x and t0 <= r["t"] <= t1]
                sa = [r for r in s_ if r.get("available")]
                bl = [r for r in R.get("blinds", []) if r["team"] == x and t0 <= r["t"] <= t1]
                sp = [r for r in R.get("spikes", []) if r["team"] == x and t0 <= r["t"] <= t1]
                hx = [r for r in R.get("hexes", []) if r["team"] == x and t0 <= r["t"] <= t1 and r.get("value", 0) > 0]
                hr = [r for r in R.get("hex_removals", []) if r["team"] == x and t0 <= r["t"] <= t1 and r.get("available")]
                hs = (sum(r["value"] * min(r["secs"] if r["secs"] is not None else t1 - r["t"], 30) for r in hx) / sum(r["value"] for r in hx)) if hx else None
                return {"ready": sum(c["interrupted_after_ready"] for c in cs) / n if n else None, "dazed": sum(c["while_dazed"] for c in cs) / n if n else None,
                        "blind_att": sum(c["attacks_while_blind"] for c in cs) / pl if pl else None,
                        "peel": statistics.mean(pe) if pe else None, "strip_right": sum(r["right_target"] for r in sa) / len(sa) if sa else None,
                        "strip_value": sum(r["value"] for r in s_) / max(t1 - t0, 1) * 10,
                        "blind_front": sum(1 for r in bl if r["target_class"] == "frontline"), "blind_def": sum(1 for r in bl if r["defensive"]),
                        "spread": statistics.median([r["spread_s"] for r in sp]) if sp else None, "spikes": len(sp),
                        "dps": _team_dps(team, x, t0, t1, V, roles_alive(x, f["start"])),
                        "hex_secs": hs, "hex_right": sum(r["right_hex"] for r in hr) / len(hr) if hr else None}
            o, e = side(tg), side(fg)
            df = lambda k: (o[k] - e[k]) if o[k] is not None and e[k] is not None else None
            ln = f.get("local_numbers") or [None, None]
            if tg != f["team"]: ln = ln[::-1]
            add(tg, f["start"], int(f.get("opponent_won_fight") == tg), own_local=ln[0], enemy_local=ln[1],
                peel_defensive_diff=df("peel"), ready_interrupt_diff=df("ready"), dazed_casts_diff=df("dazed"), blind_attacks_diff=df("blind_att"),
                strip_right_diff=df("strip_right"), strip_value_diff=df("strip_value"), blind_front_diff=df("blind_front"), blind_defensive_diff=df("blind_def"),
                spike_spread_diff=df("spread"), spikes_diff=df("spikes"), dps_v_usual_diff=df("dps"), hex_secs_diff=df("hex_secs"), hex_right_diff=df("hex_right"),
                strength_gap=gaps[tg])
    elif node == "split_chance":
        spl = collections.defaultdict(list)
        for s_ in a.get("splits", []): spl[s_["team"]].append((s_["start"], s_["end"]))
        for r in sb:
            t = r["t"]
            if t < 30 or t % 15 or t > (sb[-1]["t"] - 30): continue
            for tg in tags:
                if any(s0 <= t <= s1 for s0, s1 in spl[tg]): continue
                fg = foe(tg); mu = mus[tg]
                add(tg, t, int(any(t < s0 <= t + 30 for s0, _ in spl[tg])), flag_lead=max(min(r[tg]["flag_lead"], CLIP), -CLIP),
                    own_alive=r[tg]["alive"], enemy_alive=r[fg]["alive"], own_main=r[tg]["main"], enemy_main=r[fg]["main"],
                    stand_own=int(r["stand"]["owner"] == tg), stand_enemy=int(r["stand"]["owner"] == fg), minute=round(t / 60, 1), res_in=r.get("res_in"),
                    own_speed=mu.get("own_speed"), own_snares=mu.get("own_snares"), enemy_snares=mu.get("enemy_snares"), strength_gap=gaps[tg])
    elif node in ("split_answer", "split_effect", "collapse"):
        from state import d
        rec = {(r["team"], r["t"]): r for r in R.get("splits", [])}
        for s_ in a.get("splits", []):
            r = rec.get((s_["team"], s_["start"]))
            if not r: continue
            tg, fg = s_["team"], foe(s_["team"])
            lat = [x["latency"] for x in s_.get("defenders") or []]
            first = min(lat) if lat else None
            latency = max(min(first, NEVER), -30) if first is not None else NEVER
            if node == "split_answer":
                if s_.get("entered_base") is None: continue
                te = s_["entered_base"]; srow = _row(sb, te); dtm = tm_of[fg]
                near = [d(st.pos(b, te)[0], st.geo.base[dtm]) for b in st.players[dtm] if st.alive(b, te)] if getattr(st.geo, "base", None) else []
                add(fg, te, latency, flag_lead=max(min(srow[fg]["flag_lead"], CLIP), -CLIP), def_alive=srow[fg]["alive"], att_main=srow[tg]["main"],
                    def_free=srow[fg]["alive"] - len(srow[fg].get("flag_duty") or []), nearest_to_base=round(min(near)) if near else None,
                    size=r["size"], minute=round(te / 60, 1), strength_gap=gaps[fg])
            elif node == "split_effect":
                if s_.get("entered_base") is None: continue
                from common import line as LINE
                heal = sum(1 for x in s_["members"] if "Monk" in x or x in ("Prot",))
                add(tg, s_["start"], int(r["pit_kills"] > 0), latency=latency, defenders=r["defenders"], size=r["size"],
                    main_diff=r["main_diff"], split_healers=heal, strength_gap=gaps[tg])
            else:
                add(tg, s_["start"], int(r["split_deaths"] > 0), latency=latency,
                    defenders_10s=sum(1 for x in lat if first is not None and x <= first + 10), def_snares=mus[fg].get("own_snares"),
                    split_speed=mus[tg].get("own_speed"), size=r["size"], main_diff=r["main_diff"], strength_gap=gaps[tg])
    return rows


def _vhash(V): return hashlib.sha1(json.dumps(V, sort_keys=True).encode()).hexdigest()[:10]


def node_rows(node, rid, V):
    import cache
    return cache.prepared("lrows", rid, lambda: _build(node, rid, V), sub=f"{node}-{_vhash(V)}")


def _rows_job(job):
    node, rid, V = job
    return node_rows(node, rid, V)


# ---------------------------------------------------------------- fitting
def _ebm(n_matches, regression):
    from interpret.glassbox import ExplainableBoostingClassifier as EBM, ExplainableBoostingRegressor as EBR
    kw = dict(max_bins=16, outer_bags=4, min_samples_leaf=20 if not regression else 8, max_rounds=400, interactions=0, random_state=7)
    return (EBR if regression else EBM)(**kw)


def _job(job):
    """One fit: a held-out fold's score (and the baseline's), or the final model. Top level for parallel.py."""
    kind, regression, n, Xtr, ytr, Xte, yte = job
    e = _ebm(n, regression).fit(Xtr, ytr)
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
                if l["status"] == "hypothesis" and L["status"] in ("supported", "rejected"):
                    l["status"] = L["status"]
                    c["log"].append({"date": today, "change": f"link {L['from']} -> {L['to']} {L['status']} by the {node} node "
                                     f"(held-out gain {L['strength']} +/- {L['plus_minus']}, {s['matches']} matches)", "by": "data"})
                if old != L["status"]: changes += 1
            log.append({"date": today, "node": node, "from": L["from"], "to": L["to"], **{k: meas[k] for k in ("strength", "plus_minus", "status", "metric", "matches")}})
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
