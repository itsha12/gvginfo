"""Decision points: the recurring moments where a team chooses, recorded as situation -> choice -> outcome, so that
"what is the optimal play here" can be answered by comparing what happened after different choices in similar
situations across many matches (and, after the bulk pull, by the win-probability model instead of the provisional
edge).

Kinds (each record: kind, team (the team choosing), t, state, choice, actions (what every player did in the next 20 s:
carrying, to the spawn, fell back, advanced, fought, held, died), first_actions (the same over the first 5 s: the
choice the usual play groups by), outcome, edge_change):
- enemy_pickup: the enemy picks up a new flag. Choices: already running, ran (picked up within 25 s), held.
- split_in_base: an enemy split enters the base. Choices: who answered and how fast (on time 15 s, late, missed).
- power_play: a numbers advantage at main for 10 s+, away from home (a numbers advantage in the own base or pit is a
  defence, not a power play; and the two mains must trade damage). Choices: pushed (ground or pressure), held.
- boost_clock: the enemy's boost is 30 s away. Choices: running (a carrier out), not running.
- after_wipe: the team just won a wipe. Choices: pushed the pit, took the flag, reset.
- late_game: 24:00 reached. Choice: Lord commitment (players at the enemy Lord) against defence; outcome = result.
- split_or_stay (Denning, after Bounty's and Nick's commentary): every 30 s from 1:00, for a team not already
  splitting with 6+ alive: did it start a split in the next 30 s (split) or not (stayed)? Weighed by the usual play
  against the snare matchup, so "should we split here" gets an answer, not just "will they split".
- runner_choice (Denning, 2026-11-08: capping on a warrior, a midline, a dervish or a monk is a strategic decision):
  every fresh run (a pickup within 1,500 of the team's flag spawn). Choice = who carries (common.runner_class); window
  90 s. The usual play compares carriers in similar situations (and by snare matchup).
Every record's extra carries the snare matchup at that moment (movepower.py): own and enemy snare power of the live
players and own speed power (Denning: starting the flag game or a split against a lot of snare is likely poor play;
the data decides).

The state is the scoreboard key that makes situations comparable: flag position and lead, stand and boost clock,
numbers, DP, pit NPCs, Lord damage, build archetypes, phase. Outcomes are scoreboard swings over a fixed window.

Usage:  python3 decisions.py <report id>
In code: decision_points(st, sb, episodes) -> list of dicts (analyze.py)."""
from buildfeat import player_flags
from common import split_context
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


ACT_W = 20           # seconds after a decision point over which each player's action is read
MOVE = 800           # units of movement toward a pit that count as falling back or advancing
# the choice itself (Denning, after batch 9): what the team did in its first seconds, because what happened over the
# next 20 s is partly the fight's result (held, advanced read +5.5 and held, fell back -4.1, both clear, at 133 matches).
# The usual play groups choices by this; the 20 s actions stay as context (library, discovery). Movement threshold
# scaled to the shorter window.
FIRST_W = 5
FIRST_MOVE = MOVE * FIRST_W / ACT_W


def response(sb, tm, t, w=ACT_W, move=MOVE):
    """What each player of team tm actually did in the w seconds after t: died, carrying, to the spawn, fell back
    (toward its own pit), advanced (toward the enemy pit), fought (dealt or took damage while staying), or held.
    Returns per role, the counts, and a short key for grouping in the library (e.g. "advanced 3, fell back 2, ...")."""
    st, m = sb.st, sb.m
    own, foe = st.geo.pit.get(tm), st.geo.pit.get(3 - tm)
    t1 = min(t + w, st.end - 1)
    per = {}
    for a in st.players[tm]:
        if not st.alive(a, t): continue
        p0, p1 = st.pos(a, t)[0], st.pos(a, t1)[0]
        if any(t < x <= t1 for x in st.death_times.get(a, [])): act = "died"
        elif any(c["a"] == a and c["s"] <= t1 and c["e"] >= t for c in st.carries): act = "carrying"
        elif p1 and d(p1, st.geo.spawn[tm]) < 1200 and d(p0, st.geo.spawn[tm]) >= 1200: act = "to the spawn"
        elif p0 and p1 and d(p1, own) < d(p0, own) - move: act = "fell back"
        elif p0 and p1 and d(p1, foe) < d(p0, foe) - move: act = "advanced"
        elif any(sb.fighting(a, x, 2) for x in range(int(t), int(t1) + 1, 2)): act = "fought"
        else: act = "held"
        per[m.roles[a]] = act
    c = collections.Counter(per.values())
    return {"by_role": per, "counts": dict(c), "key": ", ".join(f"{k} {v}" for k, v in sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))}


def _powers(st):
    """Each player's snare and speed power (movepower.py), once per match."""
    if getattr(st, "_mp", None) is None:
        import movepower
        st._mp = movepower.powers(st.m)
    return st._mp


def _move_ctx(st, tm, t):
    """Snare matchup at t (movepower.py): power of the live players on each side."""
    P = _powers(st)
    live = lambda k, kind: round(sum(P[a][kind] for a in st.players[k] if st.alive(a, t)), 1)
    return {"own_snare_power": live(tm, "snare"), "enemy_snare_power": live(3 - tm, "snare"), "own_speed_power": live(tm, "speed")}


def rec(sb, kind, tm, t, choice, t_end, extra=None, **more):
    tag = sb.m.tag[tm]
    sw = sb.swing(tag, t, t_end)
    extra = {**_move_ctx(sb.st, tm, t), **(extra or {})}
    return {"kind": kind, "team": tag, "t": round(t), "state": key(sb, tm, t), "choice": choice,
            "actions": response(sb, tm, t), "first_actions": response(sb, tm, t, FIRST_W, FIRST_MOVE), "outcome": sw, "edge_change": sw["edge_change"], "extra": extra or {}, **more}


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


COLLAPSE_MAX_AWAY = 180   # seconds; a collapser not back at main by then is counted as away for this long


def _collapse_away(st, sb, tm, coll):
    """How long the collapsers were away from the main group, and what the main fight lost meanwhile (the cost side of
    a collapse; the kill or NPCs saved are the gain). coll = [(agent, first second near the split)]."""
    if not coll: return {}
    m = st.m; spans = []
    for b, first in coll:
        leave = next((t for t in range(int(first), max(int(first) - 60, 0), -1) if b in st.main_group(tm, t)), max(int(first) - 20, 0))
        back = next((t for t in range(int(first) + 5, min(int(first) + COLLAPSE_MAX_AWAY, int(st.end) - 1))
                     if b in st.main_group(tm, t)), None)
        died = any(leave <= x <= (back or first + COLLAPSE_MAX_AWAY) for x in st.death_times.get(b, []))
        spans.append((leave, back if back is not None else min(int(first) + COLLAPSE_MAX_AWAY, int(st.end) - 1), back is None, died))
    t0 = min(x[0] for x in spans); t1 = max(x[1] for x in spans)
    sw = sb.swing(m.tag[tm], t0, t1); other = next(v for k, v in m.tag.items() if k != tm)
    return {"collapse_away_s": t1 - t0, "collapser_seconds": sum(x[1] - x[0] for x in spans),
            "collapser_not_back": int(any(x[2] for x in spans)), "collapser_died": int(any(x[3] for x in spans)),
            "away_deaths_own": sw["deaths"][m.tag[tm]], "away_deaths_enemy": sw["deaths"][other],
            "away_flag_lead_change": sw["flag_lead_change"], "away_caps_own": sw["caps"].get(m.tag[tm], 0),
            "away_caps_enemy": sw["caps"].get(other, 0), "away_npcs_lost": len(sw["npcs_lost"][m.tag[tm]]),
            "away_dp_change": sw["dp_change"][m.tag[tm]]}


def splits_in_base(st, sb, splits):
    m, out = st.m, []
    for s in splits:
        if s["kind"] != "split" or s["entered_base"] is None: continue
        y = next(k for k, v in m.tag.items() if v != s["team"])
        dfn = s["defenders"]
        lat = dfn[0]["latency"] if dfn else None
        speed = "missed" if lat is None or lat > 60 else ("late" if lat > 15 else "on time")
        choice = f"{speed}: " + (", ".join(f"{x['role']} ({x['came']})" for x in dfn[:4]) or "nobody")
        # Denning (B23): with a snare on the defender a collapse is much more likely to kill; without one, holding 1v1
        # (and part running flags, keeping NPCs up) is the usual aim
        role_to = {m.roles[b]: b for b in st.players[y]}
        # the holder = the first defender not collapsing from main (already in base, or back from the field: a Mes/A
        # usually comes back as the split approaches), else the first to arrive; collapsers counted apart
        holder_d = next((x for x in dfn if x["came"] != "collapse from main"), dfn[0] if dfn else None)
        holder = role_to.get(holder_d["role"]) if holder_d else None
        ff = player_flags(m, holder) if holder is not None else {}
        coll = [role_to[x["role"]] for x in dfn if x["came"] == "collapse from main" and x["role"] in role_to]
        away = _collapse_away(st, sb, y, [(role_to[x["role"]], x["first"]) for x in dfn
                                           if x["came"] == "collapse from main" and x["role"] in role_to])
        atk = {m.roles[a]: a for a in st.players[3 - y]}
        af = [player_flags(m, atk[r]) for r in s["members"] if r in atk]
        collapse = any(x["came"] == "collapse from main" and (x["latency"] or 0) <= 60 for x in dfn)
        response = "missed" if speed == "missed" else ("collapsed" if collapse else "defended without a collapse")
        out.append(rec(sb, "split_in_base", y, s["entered_base"], choice, s["end"] + 30,
                       split="+".join(s["members"]), answered_by=[x["role"] for x in dfn],
                       extra={"response": response, "split_size": len(s["members"]), "defenders": len(dfn),
                              "defender_snare": int(ff.get("snare", 0) > 0), "defender_interrupt": int(ff.get("interrupt", 0) > 0),
                              # how strong the defenders' snares are, not just whether (Denning, after the commentary)
                              "defender_snare_power": round(sum(_powers(st)[role_to[x["role"]]]["snare"] for x in dfn if x["role"] in role_to), 1),
                              "holder": holder_d["role"] if holder_d else None,
                              "holder_in_base": int(bool(holder_d and holder_d["came"] != "collapse from main")),
                              "collapsers": len(coll), "collapser_snare": int(any(player_flags(m, b)["snare"] for b in coll)),
                              "attacker_self_defence": sum(x["self_defence"] + x["self_heal"] for x in af),
                              "split_died": int(bool(s["deaths"])),
                              # Denning (S32): how the main fight is going decides whether the frontline can leave
                              "main_diff_now": len(st.main_group(y, s["entered_base"])) - len(st.main_group(3 - y, s["entered_base"])),
                              "health_diff": _health(st, y, s["entered_base"]) - _health(st, 3 - y, s["entered_base"]),
                              # Denning (batch 10): what the split can get NPC-wise, its death penalty, and whether it can be killed
                              **split_context(st, [atk[r] for r in s["members"] if r in atk], s["entered_base"], sb.npc_value(y, s["entered_base"])),
                              **away}))
    return out


def power_plays(st, sb, windows):
    m, out = st.m, []
    for w in windows:
        # a numbers advantage held at home (own base or pit) is a defence (e.g. a turtle against a push), not a power
        # play: found in batch 6 (One holding 8v3 in its own pit while turtling, ohno v One)
        if w.get("at_home") or not w.get("contact", True): continue      # or no damage traded: not a fight
        tm = next(k for k, v in m.tag.items() if v == w["team"])
        # pushing read up to the first kill (Denning, after batch 9), the whole window when there was none
        mv = w.get("pushed_to_first_kill", w["pushed_toward_enemy_pit"]); pr = w.get("pressure_to_first_kill", w["pressure_vs_avg"])
        pushed = (mv or 0) > 500 or pr >= 1.3
        out.append(rec(sb, "power_play", tm, w["start"], "pushed" if pushed else "held", w["end"] + 20,
                       numbers=w["numbers"], enemy_short=w["enemy_short_because"], first_kill=w.get("first_kill")))
    return out


def _health(st, tm, t):
    """Average health % of a team's main group (Denning reads enemy health live from the score share)."""
    hp = [st.m.snap(a, int(t * 10))["hp"] for a in st.main_group(tm, t) if st.m.snap(a, int(t * 10))]
    return round(sum(hp) / len(hp)) if hp else 0


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
                # Denning: falling back is fine when the team is losing its fight; a mistake when it could fight on
                own_d = sum(1 for b in st.players[ch] for x in st.death_times.get(b, []) if t - 30 < x <= t)
                foe_d = sum(1 for b in st.players[h] for x in st.death_times.get(b, []) if t - 30 < x <= t)
                out.append(rec(sb, "boost_clock", ch, t, "running" if running else "not running", t + 40,
                               boost_conceded=tb < c2, extra={"deaths_30s_diff": foe_d - own_d,
                                                              "main_diff_now": len(st.main_group(ch, t)) - len(st.main_group(h, t)),
                                                              "health_diff": _health(st, ch, t) - _health(st, h, t)}))
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
        # Denning: from a wipe at the stand a team can't reach the enemy pit and take NPCs before the res
        alive_w = [b for b in st.players[w] if st.alive(b, t0)]
        c = st.centroid(alive_w, int(t0)) if alive_w else None
        from common import RUN_SPEED
        reach = round(d(c, pit) / RUN_SPEED) if c and pit else None
        res_in = round(st.next_res(t0) - t0)
        out.append(rec(sb, "after_wipe", w, t0, choice, back + 15, losses=f["losses"],
                       extra={"seconds_to_enemy_pit": reach, "enemy_res_in": res_in,
                              "pit_margin_s": (res_in - reach) if reach is not None else None}))
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
                lord_dps_measured=sb.arch[tm]["lord_dps_measured"], healing_monks=sb.arch[tm]["healing_monks"])
        r["won"] = m.tag.get(win) == m.tag[tm] if win else None
        out.append(r)
    return out


def split_or_stay(st, sb, splits, every=30, ahead=30, window=90):
    m, out = st.m, []
    by = collections.defaultdict(list)
    for s_ in splits:
        if s_["kind"] == "split": by[s_["team"]].append((s_["start"], s_["end"]))
    for t in range(60, int(st.end) - window, every):
        for tm in st.teams:
            tag = m.tag[tm]
            if any(s0 <= t <= s1 for s0, s1 in by[tag]): continue          # already splitting
            if sum(1 for a in st.players[tm] if st.alive(a, t)) < 6: continue
            went = any(t < s0 <= t + ahead for s0, _ in by[tag])
            out.append(rec(sb, "split_or_stay", tm, t, "split" if went else "stayed", t + window))
    return out


def runner_choices(st, sb, window=90):
    from common import runner_class
    import movepower
    from common import CARRY_SPEED
    m, out = st.m, []
    for c in st.carries:
        a = c["a"]; tm = m.team(a)
        if tm not in st.teams or c["s"] < 0: continue
        p = st.pos(a, c["s"])[0]
        if not p or d(p, st.geo.spawn[tm]) > 1500 or c["s"] > st.end - window: continue
        from common import is_hold
        if is_hold(st, c): continue          # Denning: a hold is not a capture attempt
        out.append(rec(sb, "runner_choice", tm, c["s"], runner_class(m, a), c["s"] + window,
                       extra={"runner_role": m.roles.get(a), "runner_speed_bonus": movepower.speed_bonus(m, a),
                              "min_capture_s": round(d(st.geo.spawn[tm], st.geo.stand) / movepower.carry_speed(m, a, CARRY_SPEED), 1),
                              "captured": int(c["how"] == "flagstand_captured")}))
    return out


def decision_points(st, sb, ep):
    out = (enemy_pickups(st, sb) + splits_in_base(st, sb, ep["splits"]) + power_plays(st, sb, ep["windows"])
           + boost_clocks(st, sb) + after_wipes(st, sb, ep["fights"]) + late_game(st, sb)
           + split_or_stay(st, sb, ep["splits"]) + runner_choices(st, sb))
    return sorted(out, key=lambda r: r["t"])


if __name__ == "__main__":
    import episodes as E, fights as F
    st = GameState(Match.from_branch(sys.argv[1])); sb = Scoreboard(st)
    ds = F.deaths(st, sb)
    ep = {"splits": E.splits(st), "windows": F.windows(st), "fights": F.engagements(st, sb, ds)}
    for r in decision_points(st, sb, ep):
        k = r["state"]
        print(f"{st.m.f(r['t'] * 10):>5} {r['team']:5} {r['kind']:13} {r['choice'][:40]:40} | {r['actions']['key'][:55]:55} | flags "
              f"{k['flag']} {k['flag_lead']:+} stand {k['stand']} main {k['main']} dp {k['dp']:+} npcs {k['npcs']:+} | edge {r['edge_change']:+}")
