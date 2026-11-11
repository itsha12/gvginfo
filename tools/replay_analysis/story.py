"""The story so far (R-341): a match told the way Denning tells it in his golden moment notes, as a chain of events in
his words: who brought the flag and how (run, hand-off, double run, overcap), every fight on the map with its own
numbers and where it stands (the flag stand, footies, front door, pit), who joined or left a fight, deaths against the
base res clock, NPCs taken, boosts. A first draft: it states what happened; it does not yet say why (matching, pressure,
threat) or judge a play.

Report layer: reads the measurement layers (moments.py, hallmap.py) and writes text; it is in no cache key.

Usage:  python3 story.py <report id> [from m:ss] [to m:ss]
In code: story(Moments(st)) -> [(second, text)], in time order."""
import collections, sys
from common import JOIN_S, OVERCAP_S, RES_EVERY, BOOST_EVERY

STEP = 5


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


def _fight_events(M):
    """Fights followed through time. A change in a fight's numbers is told once it has lasted JOIN_S (shorter is
    support, not a player more); so is a move to another place."""
    m, T, out, tracks = M.m, M.T, [], []
    need = max(JOIN_S // STEP, 1)
    t1, t2 = m.tag[1], m.tag[2]
    for t in range(0, T + 1, STEP):
        now = [f for f in M.fights(t) if f["n"][1] and f["n"][2]]
        used = set()
        for f in now:
            ids = f["ids"][1] | f["ids"][2]
            best = max(((len(ids & tr["ids"]), i) for i, tr in enumerate(tracks) if i not in used and t - tr["seen"] <= 3 * STEP), default=(0, None))
            if best[1] is not None and best[0] * 2 >= min(len(ids), len(tracks[best[1]]["ids"])):
                tr = tracks[best[1]]; used.add(best[1])
            else:
                tr = {"stable": None, "pend": None, "count": 0}; tracks.append(tr); used.add(len(tracks) - 1)
            tr["ids"], tr["seen"] = ids, t
            key = (f["ids"][1], f["ids"][2], f["place"])
            sig = (f["n"][1], f["n"][2], f["place"])
            if tr["pend"] and (tr["pend"][0], tr["pend"][1], tr["pend"][2]) == sig: tr["count"] += 1
            else: tr["pend"], tr["count"], tr["since"], tr["pkey"] = sig, 1, t, key
            if tr["count"] >= need and tr["stable"] != sig:
                old, tr_old = tr["stable"], tr.get("skey")
                a, b, place = sig
                if old is None:
                    out.append((tr["since"], f"A fight at {place}: {t1} {a} v {b} {t2} ({t1}: {', '.join(f['who'][1])}; {t2}: {', '.join(f['who'][2])})"))
                else:
                    bits = []
                    for tm, tag in ((1, t1), (2, t2)):
                        was, is_ = tr_old[tm - 1], key[tm - 1]
                        came = [x for x in is_ - was]; went = [x for x in was - is_]
                        dead = [x for x in went if not M.AL[x][min(t, T)]]
                        left = [x for x in went if x not in dead]
                        if came: bits.append(f"{tag}'s {', '.join(m.roles[x] for x in came)} join{'s' if len(came) == 1 else ''}")
                        if left: bits.append(f"{tag}'s {', '.join(m.roles[x] for x in left)} leave{'s' if len(left) == 1 else ''}")
                        if dead: bits.append(f"{tag}'s {', '.join(m.roles[x] for x in dead)} {'is' if len(dead) == 1 else 'are'} dead")
                    if (a, b) != old[:2]:
                        moved = f"The fight moves from {old[2]} to {place}: " if place != old[2] else f"{place[0].upper() + place[1:]}: "
                        out.append((tr["since"], f"{moved}{t1} {old[0]} v {old[1]} {t2} becomes {a} v {b}" + (" (" + "; ".join(bits) + ")" if bits else "")))
                    elif place != old[2]:
                        out.append((tr["since"], f"The {a} v {b} fight moves from {old[2]} to {place}"))
                tr["stable"], tr["skey"] = sig, key
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
