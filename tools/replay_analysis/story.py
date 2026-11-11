"""The story so far (R-341): a match told the way Denning tells it in his golden moment notes, as a chain of events in
his words: who brought the flag and how (run, hand-off, double run, overcap), every fight on the map with its own
numbers and where it stands (the flag stand, footies, front door, pit), who joined or left a fight, deaths against the
base res clock, NPCs taken, boosts; how a player came to a fight (through mid, through the pit, by a door), whether an
answer was on time (R-348), swaps, who falls back and whether under pressure (team health and deaths, R-349), and who
falls out. A draft: it does not yet read a threat or a posture, and it judges no play.

Report layer: reads the measurement layers (moments.py, hallmap.py) and writes text; it is in no cache key.

Usage:  python3 story.py <report id> [from m:ss] [to m:ss]
In code: story(Moments(st)) -> [(second, text)], in time order."""
import collections, sys
from common import JOIN_S, OVERCAP_S, RES_EVERY, BOOST_EVERY, ON_TIME_S, LATE_S, PRESSURE_HP, PRESSURE_DEATH_S

STEP = 2


def clock(t): return f"{int(t) // 60}:{int(t) % 60:02d}"


def _flag_events(M):
    m, out = M.m, []
    lives = M.flag_lives()
    caps = sorted((L["end"], L["team"]) for L in lives if L["how"] == "captured")
    for L in lives:
        tag, role = m.tag[L["team"]], (lambda a: m.roles[a])
        ser = [c for c in L["carries"] if c[0] in L["serious"]]
        if not ser: continue
        nxt = L.get("next_runner")
        out.append((ser[0][1], f"{tag}'s {role(ser[0][0])} picks up the flag"))
        for a, b in zip(ser, ser[1:]):
            if a[0] == b[0]: continue
            tail = " and goes back for the next flag (double run, each half running)" if nxt == a[0] else ""
            out.append((b[1], f"{tag}'s {role(a[0])} hands the flag to {role(b[0])}{tail}"))
        if L["how"] == "captured":
            over = any(tm != L["team"] and 0 <= L["end"] - t <= OVERCAP_S for t, tm in caps)
            tail = f"; {role(nxt)} is already back for the next flag (double run, each full running)" if L["form"] == "double run, full" else ""
            out.append((L["end"], f"{tag}'s {role(L['capper'])} {'overcaps' if over else 'caps'}{tail}"))
        elif L["how"] == "returned":
            out.append((ser[-1][2] or L["end"], f"{tag}'s flag is dropped by {role(ser[-1][0])} and goes back to the spawn"))
    return out


LADDER = {"stand": 0, "greater stand": 0, "field": 0, "front footies": 1, "back footies": 1, "front door": 2, "back door": 2, "base": 3, "pit": 4}


def _health(M, ids, t):
    """Mean health % of these players over the last 10 s (the living ones)."""
    xs = [s["hp"] for u in range(max(t - 10, 0), t + 1, 2) for a in ids for s in [M.m.snap(a, u * 10)] if s and M.m.alive(s)]
    return round(sum(xs) / len(xs)) if xs else None


def _pressure(M, tm, ids, t):
    """Under pressure is a team's health, energy and deaths; where it stands is the result (R-349). Energy is not in
    the replays, so this reads health and deaths only."""
    h = _health(M, ids, t)
    d = sum(1 for a in M.st.players[tm] for td in M.st.death_times.get(a, []) if t - PRESSURE_DEATH_S <= td <= t)
    words = f"team health {h}%" + (f", {d} death{'s' if d != 1 else ''} in the last {PRESSURE_DEATH_S} s" if d else "")
    return (h is not None and h < PRESSURE_HP) or d > 0, words


def _route(M, a, t_join):
    """How a player came to a fight, in Denning's words: through mid, through the pit, by a door (looked back 90 s or
    to the last time he stood in another fight for JOIN_S)."""
    kinds, t = [], t_join
    for u in range(t_join - 2, max(t_join - 90, 0), -2):
        if not M.AL[a][u]: break
        k = M.hall.place(M.P[a][u])
        if not kinds or kinds[-1] != k: kinds.append(k)
    ks = [k for k, _ in kinds[1:]]            # where he passed before the place he arrived at
    out = []
    if "stand" in ks or "greater stand" in ks: out.append("through mid")
    if "pit" in ks: out.append("through the pit")
    for d in ("front door", "back door"):
        if d in ks: out.append("by the " + d)
    return " " + " and ".join(out[:2]) if out else ""


def _fight_events(M):
    """Fights followed through time. A change in a fight's numbers is told once it has lasted JOIN_S (shorter is
    support, not a player more, R-350), with how each player came, whether an answer was on time (R-348), swaps, and
    whether the team that falls back is under pressure (R-349)."""
    m, T, out, tracks = M.m, M.T, [], []
    need = max(JOIN_S // STEP, 1)
    tag = {1: m.tag[1], 2: m.tag[2]}
    side_tm = {v: k for k, v in M.st.side.items()}
    names = lambda xs: ", ".join(m.roles[x] for x in xs)
    for t in range(0, T + 1, STEP):
        now = [f for f in M.fights(t) if f["n"][1] and f["n"][2]]
        used = set()
        for f in now:
            ids = f["ids"][1] | f["ids"][2]
            best = max(((len(ids & tr["ids"]), i) for i, tr in enumerate(tracks) if i not in used and t - tr["seen"] <= 10), default=(0, None))
            if best[1] is not None and best[0] * 2 >= min(len(ids), len(tracks[best[1]]["ids"])):
                tr = tracks[best[1]]; used.add(best[1])
            else:
                tr = {"stable": None, "pend": None, "count": 0, "first": {}, "last": {}, "joined": {}}; tracks.append(tr); used.add(len(tracks) - 1)
            tr["ids"], tr["seen"] = ids, t
            for a in ids:
                if a not in tr["first"] or t - tr["last"].get(a, -99) > JOIN_S: tr["first"][a] = t
                tr["last"][a] = t
            key = (f["ids"][1], f["ids"][2])
            sig = (f["n"][1], f["n"][2], f["place"], f["kind"], f["side"])
            if tr["pend"] == sig: tr["count"] += 1
            else: tr["pend"], tr["count"], tr["since"], tr["pkey"] = sig, 1, t, key
            if tr["count"] < need or tr["stable"] == sig: continue
            old, okey = tr["stable"], tr.get("skey")
            a_, b_, place, kind, side = sig
            if old is None:
                out.append((tr["since"], f"A fight at {place}: {tag[1]} {a_} v {b_} {tag[2]} ({tag[1]}: {', '.join(f['who'][1])}; {tag[2]}: {', '.join(f['who'][2])})"))
            else:
                bits, came_by = [], {}
                for tm in (1, 2):
                    was, is_ = okey[tm - 1], key[tm - 1]
                    came = sorted(is_ - was, key=lambda x: tr["first"].get(x, t)); went = list(was - is_)
                    dead = [x for x in went if not M.AL[x][min(tr["since"], T)]]      # dead when the numbers changed, not when confirmed
                    left = [x for x in went if x not in dead]
                    came_by[tm] = came
                    if came and left and len(came) == len(left):
                        bits.append(f"{tag[tm]} swaps {names(came)} in for {names(left)}"); left = []
                    elif came:
                        bits.append(f"{tag[tm]}'s {names(came)} join{'s' if len(came) == 1 else ''}{_route(M, came[0], tr['first'].get(came[0], t))}")
                    if left: bits.append(f"{tag[tm]}'s {names(left)} leave{'s' if len(left) == 1 else ''}")
                    if dead: bits.append(f"{tag[tm]}'s {names(dead)} {'is' if len(dead) == 1 else 'are'} dead")
                # an answer: one side's join after the other's (R-348)
                for tm in (1, 2):
                    foe = 3 - tm
                    if not came_by[tm]: continue
                    mine = tr["first"].get(came_by[tm][0], t)
                    theirs = min((tr["first"].get(x, t) for x in came_by[foe]), default=None)
                    if theirs is None and tr["joined"].get(foe) and 0 <= mine - tr["joined"][foe] <= 60: theirs = tr["joined"][foe]
                    if theirs is not None and mine >= theirs and (came_by[foe] and mine > theirs or not came_by[foe]):
                        gap = mine - theirs
                        bits.append(f"{tag[tm]} matches {gap} s behind" + (" (on time)" if gap <= ON_TIME_S else " (late)" if gap >= LATE_S else ""))
                    elif theirs is not None and came_by[foe] and mine == theirs:
                        if tm == 1: bits.append("both arrive together")
                    tr["joined"][tm] = mine
                moved = place != old[2]
                why = ""
                if moved and side in side_tm and LADDER[kind] > (LADDER[old[3]] if old[4] == side else 0):
                    back = side_tm[side]
                    hot, words = _pressure(M, back, key[back - 1], tr["since"])
                    why = f" ({tag[back]} falls back{', under pressure' if hot else ''}: {words})"
                elif moved and old[4] in side_tm and (side != old[4] or LADDER[kind] < LADDER[old[3]]):
                    why = f" ({tag[side_tm[old[4]]]} pushes out)"
                if (a_, b_) != old[:2]:
                    head = f"The fight moves from {old[2]} to {place}{why}: " if moved else f"{place[0].upper() + place[1:]}: "
                    out.append((tr["since"], f"{head}{tag[1]} {old[0]} v {old[1]} {tag[2]} becomes {a_} v {b_}" + (" (" + "; ".join(bits) + ")" if bits else "")))
                elif moved:
                    out.append((tr["since"], f"The {a_} v {b_} fight moves from {old[2]} to {place}{why}"))
            tr["stable"], tr["skey"], tr["start"] = sig, key, tr.get("start", tr["since"])
        for tr in tracks:                         # a fight on one team's ground that the visitors walk away from
            if tr["stable"] is None or tr.get("ended") or t - tr["seen"] <= 12: continue
            tr["ended"] = True
            a_, b_, place, kind, side = tr["stable"]
            if side not in side_tm or LADDER[kind] < 1 or tr["seen"] - tr["start"] < 20: continue
            vis = 3 - side_tm[side]
            alive = [x for x in tr["skey"][vis - 1] if M.AL[x][min(t, T)]]
            gone = [x for x in alive if (lambda k: k[1] != side or LADDER[k[0]] < 1)(M.hall.place(M.P[x][min(t, T)]))]
            if len(alive) * 2 >= len(tr["skey"][vis - 1]) and alive and len(gone) * 2 > len(alive):
                out.append((tr["seen"], f"{tag[vis]}'s {names(alive)} fall{'s' if len(alive) == 1 else ''} out of {place}"))
    return out


def _death_events(M):
    m, st, out = M.m, M.st, []
    for tm in st.teams:
        ds = sorted((td, a) for a in st.players[tm] for td in st.death_times.get(a, []))
        i = 0
        while i < len(ds):
            j = i
            while j + 1 < len(ds) and ds[j + 1][0] - ds[j][0] <= 10: j += 1
            t0 = ds[i][0]; res = RES_EVERY - t0 % RES_EVERY
            who = ", ".join(m.roles[a] for _, a in ds[i:j + 1])
            out.append((t0, f"{m.tag[tm]} loses {who} ({round(res)} s before the base res)"))
            i = j + 1
    for a, td in st.npc_dead.items():
        v = st.geo.npcs.get(a)
        if v and v.get("team") in m.tag and v["kind"] != "guild_lord":
            out.append((td, f"{m.tag[3 - v['team']]} takes {m.tag[v['team']]}'s {v['kind'].replace('_', ' ')}"))
    for tdead in sorted(x for tm, xs in M.foot_dead.items() for x in xs): pass
    caps = st.caps + [(st.end, None)]
    for (c, h), (c2, _) in zip(caps, caps[1:]):
        k = 1
        while h in m.tag and c + BOOST_EVERY * k < c2:
            out.append((c + BOOST_EVERY * k, f"{m.tag[h]} boosts")); k += 1
    return out


def story(M, t0=0, t1=None):
    ev = _flag_events(M) + _fight_events(M) + _death_events(M)
    t1 = M.T if t1 is None else t1
    return sorted(((t, s) for t, s in ev if t0 <= t <= t1), key=lambda x: x[0])


def _secs(x):
    a, b = x.split(":"); return int(a) * 60 + int(b)


if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit()
    from replaylib import Match
    from state import GameState
    import common, moments
    rid = next((r for r in common.replay_ids() if r.startswith(sys.argv[1])), sys.argv[1])
    st = GameState(Match.from_branch(rid))
    M = moments.Moments(st)
    print(st.m.o["meta"]["map"], "|", st.m.tag[1], "v", st.m.tag[2])
    for t, s in story(M, _secs(sys.argv[2]) if len(sys.argv) > 2 else 0, _secs(sys.argv[3]) if len(sys.argv) > 3 else None):
        print(f"{clock(t):>6}  {s}")
