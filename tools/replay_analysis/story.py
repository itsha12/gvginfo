"""The story so far (R-341): a match told the way Denning tells it in his golden moment notes.

What it says, in his words:
  State        who is where and what they are doing, at the opening and every minute: each team's main team (the group
               on the flag stand side, R-335), splits, defenders, the runner, players waiting back or dead, the stand.
  Movement     who leaves to go back for the flag (not only who picks it up), who goes to split and which way, who
               goes back to defend, who falls out and by which door.
  The flag     one flag a team (R-339): picked up, handed off, capped or overcapped, dropped where it falls, returned
               by the enemy; double runs with where the next runner came from (R-340, R-343).
  Fights       every fight with its place and numbers once damage is traded; who joins (and how: through mid, through
               the pit, by a door, through the gate), whether an answer is on time (R-348), swaps, who pushes, who
               falls back and whether under pressure (team health and deaths, R-349, R-352).
  Deaths       where, against the base res clock; resurrections by a team-mate; base resurrections; NPCs and footmen
               taken; boosts.
A draft: it does not yet read a threat or a posture, and it judges no play.

Report layer: reads the measurement layers (moments.py, hallmap.py) and writes text; it is in no cache key.

Usage:  python3 story.py <report id> [from m:ss] [to m:ss]
In code: story(Moments(st)) -> [(second, text)], in time order."""
import collections, re, sys
from common import (JOIN_S, OVERCAP_S, RES_EVERY, BOOST_EVERY, ON_TIME_S, LATE_S, PRESSURE_HP, PRESSURE_DEATH_S, PRESSURE_MIN,
                    SPAWN_R, FIGHT_LINK)
from state import d

STEP = 2
LADDER = {"stand": 0, "greater stand": 0, "field": 0, "front footies": 1, "back footies": 1, "front door": 2, "back door": 2, "base": 3, "pit": 4}
GROUND = ("front footies", "back footies", "front door", "back door", "base", "pit")
RES_SKILL = re.compile(r"Resurrect|Rebirth|Restore Life|Flesh of My Flesh|Death Pact|We Shall Return|Renew Life|Unyielding Aura|Light of Dwayna|Vengeance|Lively Was Naomei", re.I)


def clock(t): return f"{int(t) // 60}:{int(t) % 60:02d}"
def _names(M, xs): return ", ".join(M.m.roles[x] for x in xs)
def _s(xs): return "s" if len(xs) == 1 else ""
def _where(M, a, t): return M.place_words(*M.place_at(a, min(max(int(t), 0), M.T)))


def _passed(M, a, t0, t1):
    """The places a player stood in between two seconds, in order."""
    kinds = []
    for u in range(max(int(t0), 0), min(int(t1), M.T) + 1, 2):
        if not M.AL[a][u]: break
        k = M.place_at(a, u)
        if not kinds or kinds[-1] != k: kinds.append(k)
    return kinds


def _route_words(M, a, kinds, t0, t1):
    out, ks = [], [k for k, _ in kinds]
    if "stand" in ks or "greater stand" in ks: out.append("through mid")
    if "pit" in ks: out.append("through the pit")
    for dr in ("front door", "back door"):
        if dr in ks: out.append("by the " + dr)
    if M.hall.gates and any(M.AL[a][u] and min(d(M.P[a][u], g) for g in M.hall.gates) < 500 for u in range(max(int(t0), 0), min(int(t1), M.T) + 1, 2)):
        out.append("through the gate")
    return (" " + " and ".join(out[:2])) if out else ""


def _came(M, a, t_join):
    ks = _passed(M, a, t_join - 90, t_join - 2)
    return _route_words(M, a, ks[:-1] if len(ks) > 1 else [], t_join - 90, t_join)


def _went(M, a, t0):
    ks = _passed(M, a, t0, t0 + 60)
    return _route_words(M, a, ks[1:], t0, t0 + 60)


# ---- state: who is where and what they are doing
def state_line(M, t):
    st, m, parts = M.st, M.m, []
    owner, since = st.stand_owner(t)
    parts.append("Stand: " + (f"{m.tag[owner]}, boost in {round(BOOST_EVERY - (t - since) % BOOST_EVERY)} s" if owner else "nobody"))
    for tm in st.teams:
        foe, side = 3 - tm, st.side.get(tm)
        live = [a for a in st.players[tm] if M.AL[a][t]]
        dead = [a for a in st.players[tm] if not M.AL[a][t]]
        gs = []
        for a in live:
            hit = [g for g in gs if any(d(M.P[a][t], M.P[b][t]) < FIGHT_LINK for b in g)]
            gs = [g for g in gs if g not in hit] + [[a] + [x for g in hit for x in g]]
        to_stand = M.hall.to(M.hall.stand)
        near = lambda g: min(to_stand.get(M.hall.snap(M.P[a][t]), 1e9) for a in g)
        monks = lambda g: sum(1 for a in g if m.A[a].get("p") == "Monk")
        mt = M.main_team(tm, t)                               # the engine's main team (R-335, R-355), not a second reading
        main = max(gs, key=lambda g: (len(mt & set(g)), len(g), -near(g))) if gs else []
        bits = []
        for g in sorted(gs, key=lambda g: (g is not main, -len(g))):
            z = collections.Counter(M.place_at(a, t) for a in g); kind, sd = max(z, key=lambda k: (z[k], str(k)))
            where = M.place_words(kind, sd)
            car = [a for a in g if M.carrying(a, t)]
            foes = [b for b in st.players[foe] if M.AL[b][t] and any(d(M.P[b][t], M.P[a][t]) < FIGHT_LINK for a in g)]
            vs = f" against {len(foes)}" if foes else ""
            flag = f", {m.roles[car[0]]} holding the flag" if car and len(g) > 1 else ""
            if g is main: bits.append(f"main team {len(g)} at {where}{vs}{flag} ({_names(M, sorted(g))})" if len(g) < len(live) or t < 60 else f"all {len(g)} at {where}{vs}{flag}")
            elif len(g) == 1 and car: bits.append(f"{m.roles[g[0]]} running the flag at {where}")
            elif len(g) == 1 and M.on_leg(g[0], t, ("run",)): bits.append(f"{m.roles[g[0]]} going back for the flag")
            elif len(g) == 1 and d(M.P[g[0]][t], M.spawn[tm]) < SPAWN_R and not foes: bits.append(f"{m.roles[g[0]]} waiting back at the flag spawn")
            elif sd is not None and sd != side and kind in GROUND: bits.append(f"{_names(M, sorted(g))} splitting at {where}{vs}{flag}")
            elif sd == side and kind in GROUND and foes: bits.append(f"{_names(M, sorted(g))} defending at {where}{vs}{flag}")
            else: bits.append(f"{_names(M, sorted(g))} at {where}{vs}{flag}")
        if dead: bits.append(f"{_names(M, dead)} dead (base res in {round(RES_EVERY - t % RES_EVERY)} s)")
        parts.append(f"{m.tag[tm]}: " + "; ".join(bits))
    return f"STATE. " + ". ".join(parts) + "."


# ---- movement: who goes where
def _run_starts(M):
    """For each fresh pickup at the spawn: when its runner set off for the spawn (he walked more than 1,500 to get
    there), and since when he waited there (10 s or more). {(player, pickup second): (set off, waited since)}."""
    if getattr(M, "_runs", None) is not None: return M._runs
    out = {}
    for L in M.flag_lives():
        c = next((c for c in L["carries"] if c[0] in L["serious"]), None)
        if not c or c[1] < 2: continue
        a, tp, tm = c[0], min(int(c[1]), M.T), L["team"]
        if d(M.P[a][tp], M.spawn[tm]) >= SPAWN_R: continue
        dist = lambda u: M.hall.to(M.spawn[tm]).get(M.hall.snap(M.P[a][u]), 1e9) if M.AL[a][u] else None
        u = tp
        while u >= 2 and dist(u - 2) is not None and dist(u - 2) < SPAWN_R: u -= 2
        waited = u
        while u >= 4 and dist(u - 4) is not None and dist(u) is not None and dist(u - 4) > dist(u) + 40: u -= 2
        out[(a, tp)] = (u if dist(u) is not None and dist(u) - SPAWN_R > 1500 else None, waited if tp - waited >= 10 else None)
    M._runs = out
    return out


def _move_events(M):
    m, out = M.m, []
    for (a, tp), (start, waited) in _run_starts(M).items():      # when a player goes to run, not only when he picks up
        tm = m.team(a)
        if start is not None: out.append((start, f"{m.tag[tm]}'s {m.roles[a]} leaves {_where(M, a, start)} to go back for the flag"))
        if waited is not None: out.append((waited, f"{m.tag[tm]}'s {m.roles[a]} waits back at the flag spawn for the next flag"))
    return out + _attempt_events(M)


NUM = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight"}


def _attempt_events(M):
    """Splits, main team pushes and base res swings, printed from the engine's records (moments.attempts, caught):
    the story says what the record holds and nothing else (R-362)."""
    m, out = M.m, []
    mk = lambda n: "no monk" if not n else ("one monk" if n == 1 else f"{NUM.get(n, n)} monks")
    for x in M.attempts():
        tag, foe, an = x["team"], m.tag[3 - x["tm"]], x["answer"]
        who = ", ".join(q["role"] for q in x["members"])
        way = f" by the {x['way']}" if x["way"] else ""
        if x["kind"] == "split":
            size = NUM.get(x["size"], x["size"]) + (f" (up to {NUM.get(x['max'], x['max'])})" if x["max"] > x["size"] else "")
            head = f"{tag} splits {size}{way}" + (" from the opening" if x["opening"] else "") + f" ({who}; {mk(x['monks'])})"
            if x["carried_flag"]: head += ", taking the flag with it"
            out.append((x["t0"], head))
            if an["defenders"]:
                beh = "already there" if (an["behind_s"] or 0) <= 4 else f"{an['behind_s']} s behind"
                out.append((x["t_in"] + (an["behind_s"] or 0), f"{foe} answers {tag}'s split with {NUM.get(len(an['defenders']), len(an['defenders']))} ({', '.join(an['defenders'])}; {mk(an['monks'])}), {beh}, {an['met']}"
                            + (f"; {', '.join(an['went_back'])} also go{'es' if len(an['went_back']) == 1 else ''} back" if an["went_back"] else "")))
            elif an["went_back"]: out.append((x["t_in"], f"{foe} sends {', '.join(an['went_back'])} back for {tag}'s split; they never meet it"))
            else: out.append((x["t_in"], f"{foe} does not answer {tag}'s split"))
            mn = x["main"]
            res = [f"takes {', '.join(x['npcs'])}" if x["npcs"] else "takes no NPC", f"kills {', '.join(x['kills'])}" if x["kills"] else "no kills",
                   f"loses {', '.join(x['lost'])}" if x["lost"] else "no deaths"]
            end = {"left": "it leaves", "routed": "it is routed", "killed": "it is killed", "main team joined": "its main team joins it", "match ended": "the match ends"}[x["end"]]
            tail = f" ({x['after']})" if x["after"] and x["after"] != "elsewhere" else ""
            main = f"; meanwhile its main team fought a player or more up for {mn['up_s']} s, even {mn['even_s']} s, down {mn['down_s']} s" if mn["contact_s"] else "; its main team was in no fight meanwhile"
            out.append((x["t1"], f"{tag}'s split ends after {clock(x['t1'] - x['t_in'])}: {end}{tail}; {'; '.join(res)}{main}"))
            if x["ahead"] and abs(x["ahead"]["lead_s"]) >= 4:
                ah = x["ahead"]; first = tag if ah["lead_s"] > 0 else foe
                out.append((ah["split_back"], f"{tag}'s split is back with its main team {abs(ah['lead_s'])} s {'ahead of' if ah['lead_s'] > 0 else 'behind'} {foe}'s defenders: {first} has the numbers there for that long"
                            + (f" and kills {ah['kills_for'] if first == tag else ah['kills_against']}" if (ah['kills_for'] if first == tag else ah['kills_against']) else " and gets no kill")))
        else:
            out.append((x["t_in"], f"{tag}'s main team pushes in{way}, {NUM.get(x['size'], x['size'])} against {NUM.get(an['n'], an['n']) if an['n'] else 'nobody'}"))
            res = [f"takes {', '.join(x['npcs'])}" if x["npcs"] else "takes no NPC", f"kills {len(x['kills'])}" if x["kills"] else "no kills", f"loses {len(x['lost'])}" if x["lost"] else "no deaths"]
            if x["end"] != "match ended": out.append((x["t1"], f"{tag}'s push ends after {clock(x['t1'] - x['t_in'])}: {'; '.join(res)}"))
        for f in x["forced_out"]:
            out.append((f["left"], f"{tag} gives ground in {foe}'s base as {foe}'s {f['defender']} arrives"))
    for c in M.caught():
        if not (c["outnumbered"] or c["lead_lost"]): continue
        foe = m.tag[3 - c["tm"]]
        what = "is outnumbered" if c["outnumbered"] else ("loses its numbers lead" if c["lead_lost"] else "keeps its lead")
        after = f"; {c['team']} loses {', '.join(c['lost_after'])} in the next minute" if c["lost_after"] else ""
        out.append((c["t"] - 5, f"{c['team']} is in {foe}'s base at the base res: {c['attackers']} v {c['defenders']} becomes {c['attackers']} v {c['defenders'] + c['coming_back']} ({c['team']} {what}){after}"))
    return out


# ---- the flag
def _next_runner(M, L):
    """Where the player who takes the next flag came from (R-340, R-343)."""
    n, tc = L["next_runner"], min(int(L["end"]), M.T)
    rs = next((v for (a, tp), v in sorted(_run_starts(M).items(), key=lambda kv: kv[0][1]) if a == n and tp >= tc - 2), None)
    if rs and rs[0] is not None: return f"went back for it at {clock(rs[0])} from {_where(M, n, rs[0])}"
    if rs and rs[1] is not None: return "was waiting back at the flag spawn"
    return "was already near the flag spawn"


def _flag_events(M):
    m, out = M.m, []
    lives = M.flag_lives()
    caps = sorted((L["end"], L["team"]) for L in lives if L["how"] == "captured")
    for L in lives:
        tag, foe, role = m.tag[L["team"]], m.tag[3 - L["team"]], (lambda a: m.roles[a])
        ser = [c for c in L["carries"] if c[0] in L["serious"]]
        if not ser: continue
        nxt = L.get("next_runner")
        out.append((ser[0][1], f"{tag}'s {role(ser[0][0])} picks up the flag at the spawn"))
        for i, c in enumerate(ser):
            b = ser[i + 1] if i + 1 < len(ser) else None
            if b is not None and b[0] != c[0] and c[2] is not None and b[1] - c[2] <= 20:
                tail = " and goes back for the next flag (double run, each half running)" if nxt == c[0] else ""
                out.append((b[1], f"{tag}'s {role(c[0])} hands the flag to {role(b[0])} at {_where(M, b[0], b[1])}{tail}"))
            elif c[2] is not None and not (L["how"] == "captured" and b is None):
                out.append((c[2], f"{tag}'s {role(c[0])} drops the flag at {_where(M, c[0], c[2])}; it stays there"))
                if b is not None: out.append((b[1], f"{tag}'s {role(b[0])} picks the flag up from the ground"))
        if L["how"] == "captured":
            over = any(tm != L["team"] and 0 <= L["end"] - t <= OVERCAP_S for t, tm in caps)
            tail = ""
            if L["form"] == "double run, full": tail = f"; {role(nxt)} {_next_runner(M, L)} and takes the next flag (double run, each full running)"
            fr = next((x for x in M.flags_record() if x["tm"] == L["team"] and abs(x["end"] - L["end"]) <= 1), None)
            if fr: tail = (" behind their main team (a back cap)" if fr["back_cap"] else "") + f" (runner {fr['runner']} away {fr['away_s']} s" + (", next flag already waiting" if fr["backup_waiting"] else "") + ")" + tail
            out.append((L["end"], f"{tag}'s {role(L['capper'])} {'overcaps' if over else 'caps'}{tail}"))
        elif L["how"] == "returned":
            who = L.get("returned")
            if who: out.append((who[0], f"{foe}'s {role(who[1])} returns {tag}'s flag: it goes back to the spawn"))
            else: out.append((L["end"], f"{tag}'s flag is back at the spawn (the return was not seen)"))
    return out


# ---- fights
def _health(M, ids, t):
    xs = [s["hp"] for u in range(max(t - 10, 0), t + 1, 2) for a in ids for s in [M.m.snap(a, u * 10)] if s and M.m.alive(s)]
    return round(sum(xs) / len(xs)) if xs else None


def _pressure(M, tm, ids, t):
    """Under pressure is a team's health, energy and deaths; where it stands is the result (R-349). Energy is not in
    the replays, so this reads health and deaths only (R-353)."""
    h = _health(M, ids, t)
    n = sum(1 for a in M.st.players[tm] for td in M.st.death_times.get(a, []) if t - PRESSURE_DEATH_S <= td <= t)
    words = f"team health {h}%" + (f", {n} death{'s' if n != 1 else ''} in the last {PRESSURE_DEATH_S} s" if n else "")
    return (h is not None and h < PRESSURE_HP) or n > 0, words


def _fight_events(M):
    """Fights followed through time: told once damage is traded. Numbers and place are followed apart, each told once
    it has lasted (numbers JOIN_S, R-350; place 8 s), so a death or a res does not hide a move."""
    m, T, out, tracks = M.m, M.T, [], []
    need, need_p = max(JOIN_S // STEP, 1), 4
    tag = {1: m.tag[1], 2: m.tag[2]}
    side_tm = {v: k for k, v in M.st.side.items()}
    canon = lambda p: ("mid", None) if p[1] in ("stand", "greater stand") else (p[1], p[2])
    for t in range(0, T + 1, STEP):
        now = [f for f in M.fights(t) if f["n"][1] and f["n"][2]]
        used = set()
        for f in now:
            ids = f["ids"][1] | f["ids"][2]
            best = max(((len(ids & tr["ids"]), i) for i, tr in enumerate(tracks) if i not in used and t - tr["seen"] <= 10), default=(0, None))
            if best[1] is not None and best[0] * 2 >= min(len(ids), len(tracks[best[1]]["ids"])):
                tr = tracks[best[1]]; used.add(best[1])
            else:
                tr = {"n": None, "p": None, "npend": None, "ncount": 0, "ppend": None, "pcount": 0, "first": {}, "last": {}, "joined": {}, "hit": False}
                tracks.append(tr); used.add(len(tracks) - 1)
            tr["ids"], tr["seen"] = ids, t
            tr["hit"] = tr["hit"] or M.contact(f["ids"][1], f["ids"][2], t - STEP, t)
            for a in ids:
                if a not in tr["first"] or t - tr["last"].get(a, -99) > JOIN_S: tr["first"][a] = t
                tr["last"][a] = t
            key, n, p = (f["ids"][1], f["ids"][2]), (f["n"][1], f["n"][2]), (f["place"], f["kind"], f["side"])
            if tr["npend"] == n: tr["ncount"] += 1
            else: tr["npend"], tr["ncount"], tr["nsince"] = n, 1, t
            if tr["ppend"] is not None and canon(tr["ppend"]) == canon(p): tr["pcount"] += 1
            else: tr["ppend"], tr["pcount"], tr["psince"] = p, 1, t
            if not tr["hit"]: continue                       # no damage traded yet: not a fight
            home = side_tm.get(p[2])
            few = bool(home) and n[home - 1] <= 2 and n[2 - home] > n[home - 1] and p[1] in GROUND
            if tr["n"] is None:
                if tr["ncount"] < need: continue
                head = (f"{tag[home]}'s {_names(M, sorted(key[home - 1]))} defend{_s(key[home - 1])} {n[home - 1]} v {n[2 - home]} at {p[0]}" if few
                        else f"A fight at {p[0]}: {tag[1]} {n[0]} v {n[1]} {tag[2]}")
                out.append((max(tr["nsince"], t - JOIN_S), f"{head} ({tag[1]}: {', '.join(f['who'][1])}; {tag[2]}: {', '.join(f['who'][2])})"))
                tr["n"], tr["key"], tr["p"], tr["start"] = n, key, p, tr["nsince"]
                continue
            if tr["pcount"] >= need_p and canon(p) != canon(tr["p"]):
                old = tr["p"]
                if p[2] in side_tm and LADDER[p[1]] > (LADDER[old[1]] if old[2] == p[2] else 0):
                    back = side_tm[p[2]]; fwd = 3 - back
                    hot, words = _pressure(M, back, key[back - 1], tr["psince"])
                    if len(key[back - 1]) >= PRESSURE_MIN and hot: line = f"{tag[back]} falls back from {old[0]} to {p[0]}, under pressure ({words}); {tag[fwd]} follows"
                    else: line = f"{tag[fwd]} pushes from {old[0]} to {p[0]}"
                elif old[2] in side_tm and (p[2] != old[2] or LADDER[p[1]] < LADDER[old[1]]):
                    line = f"{tag[side_tm[old[2]]]} pushes out from {old[0]} to {p[0]}"
                else: line = f"The fight moves from {old[0]} to {p[0]}"
                out.append((tr["psince"], f"{line} ({tag[1]} {n[0]} v {n[1]} {tag[2]})"))
                tr["p"] = p
            if tr["ncount"] >= need and n != tr["n"]:
                bits, came_by, okey = [], {}, tr["key"]
                for tm in (1, 2):
                    was, is_ = okey[tm - 1], key[tm - 1]
                    came = sorted(is_ - was, key=lambda x: tr["first"].get(x, t)); went = list(was - is_)
                    dead = [x for x in went if not M.AL[x][min(tr["nsince"], T)]]
                    left = [x for x in went if x not in dead]
                    came_by[tm] = came
                    if came and left and len(came) == len(left):
                        bits.append(f"{tag[tm]} swaps {_names(M, came)} in for {_names(M, left)}"); left = []
                    elif came:
                        bits.append(f"{tag[tm]}'s {_names(M, came)} join{_s(came)}{_came(M, came[0], tr['first'].get(came[0], t))}")
                    if left: bits.append(f"{tag[tm]}'s {_names(M, left)} leave{_s(left)}")
                    if dead: bits.append(f"{tag[tm]}'s {_names(M, dead)} {'is' if len(dead) == 1 else 'are'} dead")
                for tm in (1, 2):                    # an answer: one side's join after the other's (R-348)
                    foe = 3 - tm
                    if not came_by[tm]: continue
                    mine = tr["first"].get(came_by[tm][0], t)
                    theirs = min((tr["first"].get(x, t) for x in came_by[foe]), default=None)
                    if theirs is None and tr["joined"].get(foe) is not None and 0 <= mine - tr["joined"][foe] <= 60: theirs = tr["joined"][foe]
                    if theirs is not None and mine > theirs:
                        gap = mine - theirs
                        bits.append(f"{tag[tm]} matches {gap} s behind" + (" (on time)" if gap <= ON_TIME_S else " (late)" if gap >= LATE_S else ""))
                    elif theirs is not None and came_by[foe] and mine == theirs and tm == 1: bits.append("both arrive together")
                    tr["joined"][tm] = mine
                tail = (" (" + "; ".join(bits) + ")") if bits else ""
                if few: out.append((tr["nsince"], f"{tag[home]}'s {_names(M, sorted(key[home - 1]))} now defend{_s(key[home - 1])} {n[home - 1]} v {n[2 - home]} at {p[0]}{tail}"))
                else: out.append((tr["nsince"], f"{p[0][0].upper() + p[0][1:]}: {tag[1]} {tr['n'][0]} v {tr['n'][1]} {tag[2]} becomes {n[0]} v {n[1]}{tail}"))
                tr["n"], tr["key"] = n, key
        for tr in tracks:                         # a fight on one team's ground that the visitors walk away from
            if tr["n"] is None or tr.get("ended") or t - tr["seen"] <= 12: continue
            tr["ended"] = True
            place, kind, side = tr["p"]
            if side not in side_tm or LADDER[kind] < 1 or tr["seen"] - tr["start"] < 20: continue
            vis = 3 - side_tm[side]
            alive = [x for x in tr["key"][vis - 1] if M.AL[x][min(t, T)]]
            gone = [x for x in alive if (lambda k: k[1] != side or LADDER[k[0]] < 1)(M.place_at(x, min(t + 10, T)))]
            if not alive or len(gone) * 2 <= len(alive): continue
            by = collections.defaultdict(list)
            for x in gone:
                ks = [k for k, sd in _passed(M, x, tr["seen"] - 6, tr["seen"] + 30) if sd == side and k in ("front door", "back door")]
                by[ks[-1] if ks else ""].append(x)
            for door, xs in by.items():
                out.append((tr["seen"], f"{tag[vis]}'s {_names(M, xs)} fall{_s(xs)} out of {place}" + (f" by the {door}" if door else "")))
    return out


# ---- deaths, resurrections, NPCs, boosts
def _death_events(M):
    m, st, out = M.m, M.st, []
    res_casts = [(r[0] / 10, r[2], r[3]) for r in m.o["ev"] if r[1] in ("cf", "sa") and r[2] in M.P and RES_SKILL.search(m.sk(r[4]) if r[4] else "")]
    base = collections.defaultdict(list)
    for tm in st.teams:
        ds = sorted((td, a) for a in st.players[tm] for td in st.death_times.get(a, []))
        i = 0
        while i < len(ds):
            j = i
            while j + 1 < len(ds) and ds[j + 1][0] - ds[j][0] <= 10: j += 1
            lines = []                                    # one line per place and base-res outcome; nobody twice in a line
            for td, a in ds[i:j + 1]:
                nxt = (int(td) // RES_EVERY + 1) * RES_EVERY; res = nxt - td
                based = any(M.AL[a][u] for u in range(min(nxt, M.T), min(nxt + 4, M.T) + 1))
                late = res <= 5 and not based and nxt + 4 <= M.T      # seen in the replay, not read off the clock
                key = (_where(M, a, td - 2), late)
                L = next((x for x in lines if x[0] == key and a not in x[2]), None)
                if L is None: lines.append([key, td, [a], res])
                else: L[2].append(a)
            for (where, late), t0, xs, res in lines:
                when = f"just too late for the base res; the next is in {round(RES_EVERY + res)} s" if late else f"{round(res)} s before the base res"
                out.append((t0, f"{m.tag[tm]} loses {', '.join(m.roles[a] for a in xs)} at {where} ({when})"))
            i = j + 1
        for td, a in ds:
            up = next((u for u in range(int(td) + 2, M.T + 1) if M.AL[a][u]), None)
            if up is None: continue
            if min(up % RES_EVERY, RES_EVERY - up % RES_EVERY) <= 4: base[(tm, round(up / RES_EVERY) * RES_EVERY)].append(a)
            else:
                by = next((c for tc, c, tg in res_casts if up - 10 <= tc <= up + 2 and m.team(c) == tm and (tg == a or tg is None)), None)
                out.append((up, f"{m.tag[tm]}'s {m.roles[a]} is resurrected" + (f" by {m.roles[by]}" if by is not None else "") + f" at {_where(M, a, up)} ({round(up - td)} s after dying)"))
    for (tm, tr), xs in base.items():
        out.append((tr, f"Base res: {m.tag[tm]}'s {_names(M, sorted(set(xs)))} come{_s(set(xs))} back"))
    resign = {}                                           # a resignation kills the whole side in one instant: say so, don't list it
    for a, td in st.npc_dead.items():
        v = st.geo.npcs.get(a)
        if v and v.get("team") in m.tag and v["kind"] == "guild_lord":
            up = [b for b in st.players[v["team"]] if M.AL[b][max(0, int(td) - 2)]]
            if len(up) >= 2 and all(any(abs(x - td) <= 1.5 for x in st.death_times.get(b, [])) for b in up): resign[v["team"]] = td
    for tm, td in resign.items():
        out[:] = [(t, x) for t, x in out if not (abs(t - td) <= 1.5 and x.startswith(f"{m.tag[tm]} loses "))]
        out.append((td, f"{m.tag[tm]} resigns: {m.tag[3 - tm]} wins"))
    for a, td in st.npc_dead.items():
        v = st.geo.npcs.get(a)
        if v and v.get("team") in resign and abs(td - resign[v["team"]]) <= 1.5: continue
        if v and v.get("team") in m.tag and v["kind"] == "guild_lord":
            out.append((td, f"{m.tag[3 - v['team']]} kills {m.tag[v['team']]}'s Guild Lord ({round(RES_EVERY - td % RES_EVERY)} s before the base res): {m.tag[3 - v['team']]} wins"))
        elif v and v.get("team") in m.tag:
            out.append((td, f"{m.tag[3 - v['team']]} takes {m.tag[v['team']]}'s {v['kind'].replace('_', ' ')}"))
    for tm, xs in M.foot_dead.items():
        for td in xs:
            if tm in resign and abs(td - resign[tm]) <= 1.5: continue
            if tm in m.tag: out.append((td, f"{m.tag[3 - tm]} takes {m.tag[tm]}'s footman"))
    caps = st.caps + [(st.end, None)]
    for (c, h), (c2, _) in zip(caps, caps[1:]):
        k = 1
        while h in m.tag and c + BOOST_EVERY * k < c2:
            out.append((c + BOOST_EVERY * k, f"{m.tag[h]} boosts")); k += 1
    return out


def story(M, t0=0, t1=None, states=True):
    lord = min((td for a, td in M.st.npc_dead.items() if (M.st.geo.npcs.get(a) or {}).get("kind") == "guild_lord"), default=None)
    t1 = M.T if t1 is None else t1
    if lord is not None: t1 = min(t1, lord)               # the game is over when a Lord dies; the replay runs on a few seconds
    ev = _flag_events(M) + _move_events(M) + _fight_events(M) + _death_events(M)
    if states: ev += [(u, state_line(M, u)) for u in [45] + list(range(120, M.T + 1, 60)) if u <= M.T]
    return sorted(((t, s) for t, s in ev if t0 <= t <= t1), key=lambda x: (x[0], not x[1].startswith("STATE")))


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
