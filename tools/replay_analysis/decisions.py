"""Decision points: the recurring moments where a team chooses, recorded as situation -> choice -> outcome, so that
"what is the optimal play here" can be answered by comparing what happened after different choices in similar
situations across many matches (and, after the bulk pull, by the win-probability model instead of the provisional
edge).

Kinds (each record: kind, team (the team choosing), t, state, choice, outcome, edge_change):
- enemy_pickup: the enemy picks up a new flag. Choices: already running, ran (picked up within 25 s), held.
- split_in_base: an enemy split enters the base. Choices: who answered and how fast (on time 15 s, late, missed).
- power_play: a numbers advantage at main for 10 s+. Choices: pushed (ground or pressure), held.
- boost_clock: the enemy's boost is 30 s away. Choices: running (a carrier out), not running.
- after_wipe: the team just won a wipe. Choices: pushed the pit, took the flag, reset.
- late_game: 24:00 reached. Choice: Lord commitment (players at the enemy Lord) against defence; outcome = result.

The state is the scoreboard key that makes situations comparable: flag position and lead, stand and boost clock,
numbers, DP, pit NPCs, Lord damage, build archetypes, phase. Outcomes are scoreboard swings over a fixed window.

Usage:  python3 decisions.py <report id>
In code: decision_points(st, sb, episodes) -> list of dicts (analyze.py)."""
import collections, sys
from replaylib import Match
from state import GameState, d
from scoreboard import Scoreboard, LATE
from common import RES_EVERY, PIT_R

WINDOW = 90          # seconds of outcome after a decision unless the episode defines its own


def phase(t): return "early" if t < 8 * 60 else ("late" if t >= LATE else "mid")


def key(sb, tm, t):
    """Comparable situation for team tm at second t."""
    s = sb.at(int(t)); m = sb.m
    me, foe = m.tag[tm], m.tag[3 - tm]
    a, b = s[me], s[foe]
    owner = s["stand"]["owner"]
    return {"phase": phase(t), "flag": a["flag"], "flag_lead": a["flag_lead"],
            "stand": "own" if owner == me else ("enemy" if owner == foe else None), "boost_in": s["stand"]["boost_in"],
            "alive": f"{a['alive']}v{b['alive']}", "main": f"{a['main']}v{b['main']}",
            "dp": a["morale_sum"] - b["morale_sum"], "npcs": round(a["npc_value"] - b["npc_value"], 1),
            "lord_damage": a["lord_damage_dealt"] - b["lord_damage_dealt"],
            "builds": f"{sb.arch[tm]['kind']} v {sb.arch[3 - tm]['kind']}"}


def rec(sb, kind, tm, t, choice, t_end, **extra):
    tag = sb.m.tag[tm]
    sw = sb.swing(tag, t, t_end)
    return {"kind": kind, "team": tag, "t": round(t), "state": key(sb, tm, t), "choice": choice,
            "outcome": sw, "edge_change": sw["edge_change"], **extra}


def enemy_pickups(st, sb):
    m, out = st.m, []
    fl = [(t / 10, typ, a) for t, typ, a, *_ in m.o.get("flags", []) if m.team(a)]
    for i, (t, typ, a) in enumerate(fl):
        if typ != "flag_picked_up" or t < 0: continue
        x = m.team(a); y = 3 - x
        # a handoff (own drop just before, close by) is not a new run
        if any(ty == "flag_dropped" and m.team(b) == x and 0 <= t - tt <= 15 for tt, ty, b in fl[max(i - 3, 0):i]): continue
        mine = [c for c in st.carries if m.team(c["a"]) == y]
        if any(c["s"] <= t <= c["e"] for c in mine): choice = "already running"
        elif any(t < c["s"] <= t + 25 for c in mine): choice = "ran"
        else: choice = "held"
        out.append(rec(sb, "enemy_pickup", y, t, choice, t + WINDOW, runner=m.roles[a]))
    return out


def splits_in_base(st, sb, splits):
    m, out = st.m, []
    for s in splits:
        if s["kind"] != "split" or s["entered_base"] is None: continue
        y = next(k for k, v in m.tag.items() if v != s["team"])
        dfn = s["defenders"]
        lat = dfn[0]["latency"] if dfn else None
        speed = "missed" if lat is None or lat > 60 else ("late" if lat > 15 else "on time")
        choice = f"{speed}: " + (", ".join(f"{x['role']} ({x['came']})" for x in dfn[:4]) or "nobody")
        out.append(rec(sb, "split_in_base", y, s["entered_base"], choice, s["end"] + 30,
                       split="+".join(s["members"]), answered_by=[x["role"] for x in dfn]))
    return out


def power_plays(st, sb, windows):
    m, out = st.m, []
    for w in windows:
        tm = next(k for k, v in m.tag.items() if v == w["team"])
        pushed = (w["pushed_toward_enemy_pit"] or 0) > 500 or w["pressure_vs_avg"] >= 1.3
        out.append(rec(sb, "power_play", tm, w["start"], "pushed" if pushed else "held", w["end"] + 20,
                       numbers=w["numbers"], enemy_short=w["enemy_short_because"]))
    return out


def boost_clocks(st, sb):
    m, out = st.m, []
    caps = st.caps + [(st.end, None)]
    for (c, h), (c2, _) in zip(caps, caps[1:]):
        k = 1
        while c + 120 * k - 30 < c2:            # the holder still holds 30 s before this boost
            tb = c + 120 * k; t = tb - 30
            if t < st.end - 30:
                ch = 3 - h
                running = any(m.team(x) == ch for x in st.carrier(t))
                out.append(rec(sb, "boost_clock", ch, t, "running" if running else "not running", t + 40,
                               boost_conceded=tb < c2))
            k += 1
    return out


def after_wipes(st, sb, fights):
    m, out = st.m, []
    for f in fights:
        if not f["wipe"]: continue
        w = next(k for k, v in m.tag.items() if v == f["opponent_won_fight"]); l = 3 - w
        t0 = f["end"]
        pit = st.geo.pit.get(l)
        pushed = any(sum(1 for b in st.players[w] if st.alive(b, t) and d(st.pos(b, t)[0], pit) < PIT_R + 500) >= 3
                     for t in range(int(t0), int(t0) + 45, 3))
        took_flag = any(m.team(c["a"]) == w and t0 <= c["s"] <= t0 + 45 for c in st.carries)
        choice = "pushed the pit" if pushed else ("took the flag" if took_flag else "reset")
        back = max(st.next_res(x[0]) for x in f["deaths"] if x[1] == f["team"])
        out.append(rec(sb, "after_wipe", w, t0, choice, back + 15, losses=f["losses"]))
    return out


def late_game(st, sb):
    m = st.m
    if st.end < LATE: return []
    out = []
    win = (m.o["meta"].get("result") or {}).get("winning_team_id")
    for tm in st.teams:
        pit = st.geo.pit.get(3 - tm)
        at = [sum(1 for b in st.players[tm] if st.alive(b, t) and d(st.pos(b, t)[0], pit) < PIT_R + 500)
              for t in range(LATE, st.end, 5)]
        commit = round(sum(at) / max(len(at), 1), 1)
        r = rec(sb, "late_game", tm, LATE, f"{commit} players at the enemy Lord on average", st.end - 1,
                late_push_and_defend=sb.arch[tm]["late_push_and_defend"], lord_power=sb.arch[tm]["lord_power"])
        r["won"] = m.tag.get(win) == m.tag[tm] if win else None
        out.append(r)
    return out


def decision_points(st, sb, ep):
    out = (enemy_pickups(st, sb) + splits_in_base(st, sb, ep["splits"]) + power_plays(st, sb, ep["windows"])
           + boost_clocks(st, sb) + after_wipes(st, sb, ep["fights"]) + late_game(st, sb))
    return sorted(out, key=lambda r: r["t"])


if __name__ == "__main__":
    import episodes as E, fights as F
    st = GameState(Match.from_branch(sys.argv[1])); sb = Scoreboard(st)
    ds = F.deaths(st, sb)
    ep = {"splits": E.splits(st), "windows": F.windows(st), "fights": F.engagements(st, sb, ds)}
    for r in decision_points(st, sb, ep):
        k = r["state"]
        print(f"{st.m.f(r['t'] * 10):>5} {r['team']:5} {r['kind']:13} {r['choice'][:60]:60} | flags {k['flag']} {k['flag_lead']:+} "
              f"stand {k['stand']} main {k['main']} dp {k['dp']:+} npcs {k['npcs']:+} | edge {r['edge_change']:+}")
