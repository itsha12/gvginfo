"""The variables the win-probability model may look at (the visible "neurons"), and the match table built from them.

Every variable has a plain-language description; nothing else reaches the model. Rows are one per 5 s per team, from
that team's side ("own" and "enemy"), with whether that team won. Add a variable by adding one line to VARIABLES
(name, description, function of the scoreboard row); Denning can propose them, and discovery suggests them.

Usage:  python3 features.py <report id> [t]      prints the variables for one match (every 60 s, or at second t)
In code: table(st, sb, strength) -> list of rows (dicts); VARIABLES for names and descriptions."""
import sys
from replaylib import Match
from state import GameState, d
from scoreboard import Scoreboard
from common import PIT_R

STEP = 5


def _own(s, sb, tm): return s[sb.m.tag[tm]]
def _foe(s, sb, tm): return s[sb.m.tag[3 - tm]]


def _npc(sb, tm, t, kind):
    st = sb.st
    return sum(1 for a, v in st.geo.npcs.items() if v["team"] == tm and v.get("pit") and v["kind"] == kind and st.npc_dead.get(a, 1e9) > t)


def _splitting(sb, tm, t):
    """Players of tm alive, away from its main group (2,500+), on the enemy half and not carrying a flag: on a split."""
    st = sb.st
    main = st.main_group(tm, t); c = st.centroid(main, t)
    if not c: return 0
    car = set(st.carrier(t))
    n = 0
    for a in st.players[tm]:
        if a in main or a in car or not st.alive(a, t): continue
        p = st.pos(a, t)[0]
        if p and d(p, st.geo.pit[3 - tm]) < d(p, st.geo.pit[tm]) and d(p, c) > 2500: n += 1
    return n


def _in_pit(sb, tm, t, whose):
    """Players of tm alive within PIT_R + 500 of a pit (whose: own or enemy)."""
    st = sb.st
    pit = st.geo.pit.get(tm if whose == "own" else 3 - tm)
    return sum(1 for a in st.players[tm] if st.alive(a, t) and d(st.pos(a, t)[0], pit) < PIT_R + 500)


def _geo(sb):
    if not hasattr(sb, "_geo_shape"):
        g = sb.st.geo
        y = [d(g.spawn[tm], g.stand) for tm in (1, 2) if g.spawn.get(tm)]
        ps = [d(g.pit[tm], g.stand) for tm in (1, 2) if g.pit.get(tm)]
        sb._geo_shape = {"y": round(sum(y) / len(y)) if y else None, "pit_stand": round(sum(ps) / len(ps)) if ps else None,
                         "bases": round(d(g.base.get(1), g.base.get(2))) if g.base.get(1) and g.base.get(2) else None}
    return sb._geo_shape


def _flux(sb, name):
    f = sb.m.o["meta"].get("flux") or {}
    return int(bool(f.get(f"{name}_active")))


# name, description, function(scoreboard row s, Scoreboard sb, team tm, second t, extra)
# Matching own and enemy quantities are single differences (own minus enemy): with "own" and "enemy" as separate
# variables they partly cancel and split the data. Build variables are separate (they describe each side's build).
O, E = _own, _foe
VARIABLES = [
    ("minute", "match clock in minutes", lambda s, sb, tm, t, x: t / 60),
    ("strength_gap", "own minus enemy strength (blend of the guild fitted rating and the lineup of players who played, strength.py blend; rating points from results before this match; 400 = 10 to 1 odds); the model's baseline",
     lambda s, sb, tm, t, x: x["strength_gap"]),
    ("flag_lead", "seconds up (+) or down (-) on flags: enemy's response minus own on the next capture exchange",
     lambda s, sb, tm, t, x: max(min(O(s, sb, tm)["flag_lead"], 150), -150)),
    ("stand", "who holds the flag stand: 1 own, 0 nobody, -1 enemy",
     lambda s, sb, tm, t, x: 0 if not s["stand"]["owner"] else (1 if s["stand"]["owner"] == sb.m.tag[tm] else -1)),
    ("boost_clock", "seconds until the stand holder's next boost (+ if own boost is coming, - if the enemy's, 0 nobody)",
     lambda s, sb, tm, t, x: 0 if not s["stand"]["owner"] else (1 if s["stand"]["owner"] == sb.m.tag[tm] else -1) * s["stand"]["boost_in"]),
    ("carrying_diff", "own minus enemy players carrying a flag",
     lambda s, sb, tm, t, x: sum(1 for r, w in O(s, sb, tm)["flag_duty"] if w == "carrying") - sum(1 for r, w in E(s, sb, tm)["flag_duty"] if w == "carrying")),
    ("alive_diff", "own minus enemy players alive", lambda s, sb, tm, t, x: O(s, sb, tm)["alive"] - E(s, sb, tm)["alive"]),
    ("down_diff_s", "enemy minus own seconds until all dead players are back (+ = the enemy has more time down)",
     lambda s, sb, tm, t, x: sum(E(s, sb, tm)["down"].values()) - sum(O(s, sb, tm)["down"].values())),
    ("main_diff", "own minus enemy players in each team's main group", lambda s, sb, tm, t, x: O(s, sb, tm)["main"] - E(s, sb, tm)["main"]),
    ("morale_diff", "own minus enemy morale summed over players (boosts +, death penalty -)",
     lambda s, sb, tm, t, x: O(s, sb, tm)["morale_sum"] - E(s, sb, tm)["morale_sum"]),
    ("morale_total", "both teams' morale summed (how much death penalty is in the game overall)",
     lambda s, sb, tm, t, x: O(s, sb, tm)["morale_sum"] + E(s, sb, tm)["morale_sum"]),
    ("spike_killable_diff", "enemy minus own players within one spike of the other side (DP stacking; 0 unless a spike build is involved)",
     lambda s, sb, tm, t, x: len(E(s, sb, tm)["killable_by_one_spike"]) - len(O(s, sb, tm)["killable_by_one_spike"])),
    ("knights_diff", "own minus enemy pit knights alive", lambda s, sb, tm, t, x: _npc(sb, tm, t, "knight") - _npc(sb, 3 - tm, t, "knight")),
    ("archers_diff", "own minus enemy pit archers alive", lambda s, sb, tm, t, x: _npc(sb, tm, t, "archer") - _npc(sb, 3 - tm, t, "archer")),
    ("bodyguard_diff", "own minus enemy Bodyguard alive", lambda s, sb, tm, t, x: _npc(sb, tm, t, "bodyguard") - _npc(sb, 3 - tm, t, "bodyguard")),
    ("lord_damage_diff", "own minus enemy Lord damage dealt so far (the 28:00 tiebreak; players can't see it); blank when either team's Lord damage wasn't observed",
     lambda s, sb, tm, t, x: (O(s, sb, tm)["lord_damage_dealt"] - E(s, sb, tm)["lord_damage_dealt"])
     if O(s, sb, tm)["lord_damage_observed"] and E(s, sb, tm)["lord_damage_observed"] else None),
    ("lord_health_diff", "own minus enemy Lord health as a share of its max (rebuilt from damage, healing and measured regeneration, lord.py); blank if unobserved",
     lambda s, sb, tm, t, x: (O(s, sb, tm)["lord_health"] - E(s, sb, tm)["lord_health"])
     if O(s, sb, tm)["lord_health"] is not None and E(s, sb, tm)["lord_health"] is not None else None),
    ("lord_exposed_diff", "enemy Lord exposed (its Bodyguard and knights dead) minus own: +1 = only the enemy's is exposed",
     lambda s, sb, tm, t, x: E(s, sb, tm)["lord_exposed"] - O(s, sb, tm)["lord_exposed"]),
    ("pit_pressure_diff", "own players in the enemy pit minus enemy players in the own pit",
     lambda s, sb, tm, t, x: _in_pit(sb, tm, t, "enemy") - _in_pit(sb, 3 - tm, t, "enemy")),
    ("fight_state", "who is winning the fight now: enemy minus own expected deaths in the next 10 s, from a deaths model that never saw the match (fightstate.py)",
     lambda s, sb, tm, t, x: __import__("fightstate").diff(sb.m.o["meta"]["id"], t, sb.m.tag[tm])),
    ("res_in", "seconds until the next base res", lambda s, sb, tm, t, x: s["res_in"]),
    ("lord_dps_own", "own build's measured Lord damage per second if all its non-healers were at the Lord",
     lambda s, sb, tm, t, x: sb.arch[tm]["lord_dps_measured"]),
    ("lord_dps_enemy", "enemy build's measured Lord damage per second", lambda s, sb, tm, t, x: sb.arch[3 - tm]["lord_dps_measured"]),
    ("healing_monks_own", "own healing monks in the build", lambda s, sb, tm, t, x: sb.arch[tm]["healing_monks"]),
    ("healing_monks_enemy", "enemy healing monks in the build", lambda s, sb, tm, t, x: sb.arch[3 - tm]["healing_monks"]),
    ("spike_build_own", "own build is a spike build (1) or not (0)", lambda s, sb, tm, t, x: int(sb.arch[tm]["spike"])),
    ("spike_build_enemy", "enemy build is a spike build", lambda s, sb, tm, t, x: int(sb.arch[3 - tm]["spike"])),
    # map shape (state.MapGeo; fixed for a match, so staged like the build variables)
    ("map_flag_run", "the map's flag run Y: distance from the flag spawn to the stand (average of both sides)",
     lambda s, sb, tm, t, x: _geo(sb)["y"]),
    ("map_pit_to_stand", "the map's distance from a pit to the stand (average of both sides)",
     lambda s, sb, tm, t, x: _geo(sb)["pit_stand"]),
    ("map_bases_apart", "the map's distance between the two bases", lambda s, sb, tm, t, x: _geo(sb)["bases"]),
    # flux (gvg.report records which flux was active; fixed for a match)
    ("flux_minion_apocalypse", "flux Minion Apocalypse active", lambda s, sb, tm, t, x: _flux(sb, "minion_apocalypse")),
    ("flux_meek_shall_inherit", "flux Meek Shall Inherit active", lambda s, sb, tm, t, x: _flux(sb, "meek_shall_inherit")),
    ("flux_jack_of_all_trades", "flux Jack of All Trades active", lambda s, sb, tm, t, x: _flux(sb, "jack_of_all_trades")),
    ("flux_chain_combo", "flux Chain Combo active", lambda s, sb, tm, t, x: _flux(sb, "chain_combo")),
]
# Candidate variables (discovery): computed and retested in every learning report (held-out accuracy with and without
# each), but only moved into VARIABLES once they improve predictions on unseen matches. Each notes who proposed it,
# when, and why.
CANDIDATES = [
    ("split_diff", "own minus enemy players on a split (away from their main group on the enemy half, not carrying). "
     "Proposed batch 1 by Claude: the knights curve runs backwards, maybe standing in for the cost of splitting",
     lambda s, sb, tm, t, x: _splitting(sb, tm, t) - _splitting(sb, 3 - tm, t)),
]
DESCRIPTIONS = {n: dsc for n, dsc, _ in VARIABLES + CANDIDATES}


def table(st, sb, strength=None, step=STEP):
    """One row per step seconds per team: match, team, t, won, then every variable."""
    m = st.m
    win = (m.o["meta"].get("result") or {}).get("winning_team_id")
    rows = []
    for tm in st.teams:
        gap = None
        if strength:
            at = m.o["meta"].get("started")       # ms since 1970
            ratings = {t["tag"]: t.get("rating") for t in m.o["meta"]["teams"]}
            lu = {m.tag[k]: [m.nm(a) for a in m.PL if m.team(a) == k] for k in (1, 2)}
            lad, fit = strength(m.o["meta"]["id"], m.tag[tm], at, m.tag[3 - tm], ratings, lu); gap = fit
        x = {"strength_gap": gap}
        for t in range(0, st.end - 1, step):
            s = sb.at(t)
            r = {"match": m.o["meta"]["id"], "team": m.tag[tm], "t": t, "won": int(win == tm) if win in (1, 2) else None}
            for n, _, fn in VARIABLES + CANDIDATES: r[n] = fn(s, sb, tm, t, x)
            rows.append(r)
    return rows


if __name__ == "__main__":
    from strength import strength_gap
    st = GameState(Match.from_branch(sys.argv[1])); sb = Scoreboard(st)
    rows = table(st, sb, strength_gap, 60 if len(sys.argv) < 3 else 1)
    want = int(sys.argv[2]) if len(sys.argv) > 2 else None
    for r in rows:
        if want is None or r["t"] == want: print({k: (round(v, 1) if isinstance(v, float) else v) for k, v in r.items()})
