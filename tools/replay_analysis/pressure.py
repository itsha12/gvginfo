"""Pressure measures Denning asked for after chunk 4 (session 4u), measured from the replays, per player:

  kiting       seconds an enemy melee player (warrior, dervish, assassin only: Denning) spent chasing the player without
               hitting it: the melee's latest attack target (attack started in the last 5 s) is the player, they are
               250 to 1,300 apart (not in contact), the melee is moving and deals the player no damage that second or the
               next. Credit to the player kiting; the melee's wasted seconds are kept too.
  pre-kiting   seconds the player kept its distance from a melee heading for it before contact: the melee has started
               no attack in the last 3 s, moved 200+ toward the player over 2 s (heading within about 37 degrees), the
               gap shrank by less than a third of the melee's travel, and the player was moving.
  degen        degeneration the player put on enemies, in pip-seconds (1 pip = 2 health a second): bleeding 3, poison 4,
               disease 4, burning 7 pips (game values), plus health-degeneration hexes at the caster's rank (skill text).
               Uptime is measured (the replays' condition and hex intervals, removal included); degen caps at 10 pips on
               one target at a time. The replays record degeneration as no damage at all, so without this it was unseen.
  baits        enemy interrupts that landed on nothing because the player cancelled: an enemy finished an interrupt skill
               on the player, no interrupt from it landed within 1 s, and the player stopped a cast (no interrupt on it)
               in the 2 s before. Only baits the data proves; a cancel that scared an interrupter off can't be seen.
  knockdowns   knockdowns the player landed on enemies, and how many hit a target that was casting.
  disables     skill-seconds disabled on enemies by Complicate, Power Lock, Power Block (that attribute's skills on the
               target's bar) and Blackout (all 8 skills). Whether it landed is measured (interrupts; Blackout's cast
               landing on its target); how long the skills stay disabled is not recorded, so it comes from the skill text at
               the caster's rank (the one partly rule-based measure).
  cast prevention  seconds Shame, Guilt and Diversion sat on enemies, and how many were triggered (the hex ended early
               just after the target started a cast: a cast that failed or was punished).

In code: record(rid) -> per-player event lists (cached); team_window(rec, team_agents, foe_agents, t0, t1) -> totals;
player_window(rec, a, t0, t1) -> one player's totals; on_player(rec, a, t, w) -> what was done to a player in the last w s.
Times in seconds."""
import bisect, collections, functools, json, math, re
from common import REPO

MELEE = {"Warrior", "Dervish", "Assassin"}
COND_PIPS = {"bleeding": 3, "poison": 4, "disease": 4, "burning": 7}
DISABLES = {"Complicate", "Power Lock", "Power Block", "Blackout"}
CAST_PREVENTION = {"Shame", "Guilt", "Diversion"}
PIP_HP = 2
DEGEN_CAP = 10


def _base(name):
    return re.sub(r"\s*\(?PvP\)?$", "", name or "").strip()


@functools.lru_cache(maxsize=1)
def _interrupt_skills():
    from buildfeat import _skills
    return {k for k, s in _skills().items() if "interrupt" in (s.get("desc") or "").lower()}


def _rank(m, a, s):
    import movepower
    return movepower._ranks().get((m.o["meta"]["id"], m.nm(a)), {}).get(s.get("attr"), movepower.DEFAULT_RANK)


def _at_rank(desc, pattern, rank):
    mm = re.search(r"(\d+)\.\.(\d+) " + pattern, desc or "")
    if not mm: return None
    lo, hi = int(mm.group(1)), int(mm.group(2))
    return lo + (hi - lo) * min(rank, 15) / 15


def _hex_pips(m, caster, sname):
    from buildfeat import _skills
    s = _skills().get(sname)
    if not s or "Hex" not in (s.get("type") or ""): return 0
    if caster is None or not isinstance(caster, int): rank = 12
    else: rank = _rank(m, caster, s)
    return _at_rank(s.get("desc"), "Health degeneration", rank) or 0


def _disable_secs(m, caster, sname, target, interrupted=None):
    """Skill-seconds disabled on the target (Power Block: that attribute's skills on its bar; Blackout: all 8)."""
    from buildfeat import _skills
    import movepower
    S = _skills(); s = S.get(sname)
    if not s: return 0
    rank = _rank(m, caster, s) if isinstance(caster, int) else movepower.DEFAULT_RANK
    dur = movepower._duration(s, rank, "disable") or 0
    base = _base(sname)
    if base == "Blackout": n = 8
    elif base == "Power Block":
        att = (S.get(m.sk(interrupted)) or {}).get("attr") if interrupted is not None else None
        n = max(1, sum(1 for b in (m.A[target].get("bar") or []) if b and att and (S.get(m.sk(b)) or {}).get("attr") == att))
    else: n = 1
    return round(dur * n, 1)


def _nearest_foe(st, m, a, t, r):
    p = st.pos(a, t)[0]
    if not p: return None
    best = None
    for b in m.PL:
        if m.team(b) == m.team(a): continue
        q, s = st.pos(b, t)
        if q and m.alive(s) and math.dist(p, q) <= r and (best is None or math.dist(p, q) < best[1]): best = (b, math.dist(p, q))
    return best[0] if best else None


def build(rid):
    from replaylib import Match
    from state import GameState
    st = GameState(Match.from_branch(rid)); m = st.m
    ev = sorted((e for e in m.o.get("ev") or [] if e[0] is not None), key=lambda e: e[0])
    PL = set(m.PL); team = {a: m.team(a) for a in m.PL}
    foe = lambda a, b: a in PL and b in PL and team[a] != team[b]
    end = int(st.end)
    out = {"kite": collections.defaultdict(list), "prekite": collections.defaultdict(list), "wasted": collections.defaultdict(list),
           "degen": [], "baits": collections.defaultdict(list), "kd": [], "disable": [], "castprev": []}

    # ---- casts: open intervals per player (for knockdowns on casters and baits)
    casts = collections.defaultdict(list); open_ = {}; stops = collections.defaultdict(list); irs = collections.defaultdict(list)
    for e in ev:
        a = e[2]
        if e[1] == "cs": open_[a] = (e[0], e[4])
        elif e[1] in ("cf", "cx", "ir") and a in open_:
            t0, sid = open_.pop(a); casts[a].append((t0 / 10, e[0] / 10, sid, e[1]))
        if e[1] == "cx": stops[a].append(e[0] / 10)
        if e[1] == "ir": irs[a].append(e[0] / 10)
    def casting(a, t):
        return any(s0 <= t <= s1 + 0.1 for s0, s1, _, _ in casts.get(a, ()) if s0 <= t)

    # ---- kiting and pre-kiting (1 s positions)
    attack_on = collections.defaultdict(list)          # melee -> [(t, target)]
    hit = set()                                        # (attacker, target, second)
    for e in ev:
        if e[1] == "at" and foe(e[2], e[3]): attack_on[e[2]].append((e[0] / 10, e[3]))
        elif e[1] == "dm" and (e[5] or 0) > 0 and foe(e[2], e[3]): hit.add((e[2], e[3], int(e[0] // 10)))
    melee = [a for a in m.PL if m.A[a].get("p") in MELEE]
    pos = lambda a, t: st.pos(a, t)
    for M in melee:
        ats = attack_on.get(M, []); ts = [x[0] for x in ats]
        enemies = [b for b in m.PL if team[b] != team[M]]
        prev = {}
        for t in range(1, end):
            pM, sM = pos(M, t)
            if not pM or not m.alive(sM): prev = {}; continue
            i = bisect.bisect_right(ts, t) - 1
            if i >= 0 and t - ats[i][0] <= 5:
                T = ats[i][1]; pT, sT = pos(T, t)
                if pT and m.alive(sT) and sM.get("st") == "m":
                    dd = math.dist(pM, pT)
                    if 250 <= dd <= 1300 and (M, T, t) not in hit and (M, T, t + 1) not in hit:
                        out["kite"][T].append(t); out["wasted"][M].append(t)
            # pre-kiting: not engaged in the last 3 s
            if (i < 0 or t - ats[i][0] > 3) and t >= 2:
                pM2, sM2 = pos(M, t - 2)
                if pM2 and m.alive(sM2):
                    mv = (pM[0] - pM2[0], pM[1] - pM2[1]); travel = math.hypot(*mv)
                    if travel >= 200:
                        best, bc = None, 0.8
                        for P in enemies:
                            pP, sP = pos(P, t); pP2, sP2 = pos(P, t - 2)
                            if not pP or not pP2 or not m.alive(sP): continue
                            d0, d1 = math.dist(pM2, pP2), math.dist(pM, pP)
                            if d1 > 1300 or d1 < 250: continue
                            to = (pP2[0] - pM2[0], pP2[1] - pM2[1]); n = math.hypot(*to)
                            if not n: continue
                            cos = (mv[0] * to[0] + mv[1] * to[1]) / (travel * n)
                            if cos >= bc: best, bc = (P, d0, d1, sP), cos
                        if best:
                            P, d0, d1, sP = best
                            if d0 - d1 < travel / 3 and sP.get("st") == "m": out["prekite"][P].append(t)

    # ---- degen: condition and hex intervals on enemies (pip-seconds kept as intervals)
    for x in m.o.get("effects") or []:
        if x[0] is None: continue
        s0, s1 = x[0] / 10, (x[1] if x[1] is not None else end * 10) / 10
        caster, target = x[4], x[5]
        if target not in PL: continue
        if x[2] == "c" and (x[7] or "") in COND_PIPS:
            out["degen"].append((s0, s1, COND_PIPS[x[7]], caster if caster in PL else None, target))
        elif x[2] == "h":
            nm = m.sk(x[3]); p = _hex_pips(m, caster, nm)
            if p: out["degen"].append((s0, s1, round(p, 1), caster if caster in PL else None, target))
            if _base(nm) in CAST_PREVENTION and caster in PL:
                trig = (s1 - s0) < 5.5 and any(s1 - 1.5 <= c0 <= s1 + 0.2 for c0, _, _, _ in casts.get(target, ()))
                out["castprev"].append((s0, min(s1, s0 + 6.5), caster, target, int(trig), _base(nm)))

    # ---- knockdowns landed
    for k in m.o.get("knockdowns") or []:
        t, src, tgt = k[0] / 10, k[1], k[2]
        if foe(src, tgt): out["kd"].append((t, src, tgt, int(casting(tgt, t))))

    # ---- disables: interrupt skills that disable, and Blackout landing
    for i in m.o.get("interrupts") or []:
        t, src, sk, tgt = i[0] / 10, i[1], m.sk(i[2]), i[3]
        if _base(sk) in DISABLES and foe(src, tgt):
            out["disable"].append((t, src, tgt, _disable_secs(m, src, sk, tgt, i[4]), _base(sk)))
    sa = collections.defaultdict(list)                 # (caster, skill name) -> [(t, target)]
    for e in ev:
        if e[1] == "sa" and e[4] is not None: sa[(e[2], m.sk(e[4]))].append((e[0] / 10, e[3]))
    for a, L in casts.items():
        if a not in PL: continue
        for s0, s1, sid, how in L:
            nm = m.sk(sid)
            if how != "cf" or _base(nm) != "Blackout": continue
            # the replays record no target for Blackout: a touch skill, so the nearest enemy within 250 (touch range)
            tg = next((b for tt, b in sa.get((a, nm), []) if abs(tt - s1) <= 1.0 and foe(a, b)), None) or _nearest_foe(st, m, a, s1, 250)
            if tg is not None: out["disable"].append((s1, a, tg, _disable_secs(m, a, nm, tg), "Blackout"))

    # ---- baits: enemy interrupt finished on a player, nothing landed, the player had just cancelled
    INT = _interrupt_skills()
    landed = collections.defaultdict(list)
    for i in m.o.get("interrupts") or []: landed[(i[1], i[3])].append(i[0] / 10)
    for S, L in casts.items():
        if S not in PL: continue
        for s0, s1, sid, how in L:
            nm = m.sk(sid)
            if how != "cf" or nm not in INT: continue
            # the replays record an interrupt's target only when it lands; a miss has none. So: no interrupt from this
            # caster landed within 1 s, and an enemy within casting range had just cancelled (the nearest cancel in time)
            if any(s1 - 0.5 <= x <= s1 + 1.0 for L_ in (v for (src, _), v in landed.items() if src == S) for x in L_): continue
            pS = st.pos(S, s1)[0]
            best = None
            for T in m.PL:
                if not foe(S, T): continue
                pT = st.pos(T, s1)[0]
                if not pS or not pT or math.dist(pS, pT) > 1250: continue
                for x in stops.get(T, ()):
                    if s1 - 2.0 <= x <= s1 + 0.3 and not any(abs(x - y) <= 0.3 for y in irs.get(T, ())):
                        if best is None or abs(s1 - x) < best[1]: best = (T, abs(s1 - x))
            if best: out["baits"][best[0]].append(round(s1, 1))
    return {k: (dict(v) if isinstance(v, collections.defaultdict) else v) for k, v in out.items()}


def record(rid):
    import cache
    r = cache.prepared("pressure", rid, lambda: build(rid))
    for k in ("kite", "prekite", "wasted", "baits"):
        r[k] = {int(a): v for a, v in r[k].items()}
    return r


def _count(L, t0, t1):
    return sum(1 for x in L if t0 <= x < t1)


def _overlap(s0, s1, t0, t1):
    return max(0.0, min(s1, t1) - max(s0, t0))


def team_window(r, own, foes, t0, t1):
    """What team `own` did to `foes` (and had done to it) in [t0, t1): per-team totals."""
    own, foes = set(own), set(foes)
    degen_by_target = collections.defaultdict(float)
    for s0, s1, pips, c, tg in r["degen"]:
        if tg in foes and c in own:          # degen with no recorded caster is credited to nobody
            degen_by_target[tg] += pips * _overlap(s0, s1, t0, t1)
    span = max(t1 - t0, 1e-9)
    degen = sum(min(v, DEGEN_CAP * span) for v in degen_by_target.values())
    return {"kite_secs": sum(_count(r["kite"].get(a, ()), t0, t1) for a in own),
            "prekite_secs": sum(_count(r["prekite"].get(a, ()), t0, t1) for a in own),
            "melee_wasted_secs": sum(_count(r["wasted"].get(a, ()), t0, t1) for a in own),
            "degen_pip_secs": round(degen, 1),
            "baits": sum(_count(r["baits"].get(a, ()), t0, t1) for a in own),
            "knockdowns": sum(1 for t, s, tg, c in r["kd"] if s in own and t0 <= t < t1),
            "knockdowns_on_casting": sum(c for t, s, tg, c in r["kd"] if s in own and t0 <= t < t1),
            "disable_skill_secs": round(sum(v for t, s, tg, v, _ in r["disable"] if s in own and t0 <= t < t1), 1),
            "castprev_secs": round(sum(_overlap(s0, s1, t0, t1) for s0, s1, c, tg, tr, _ in r["castprev"] if c in own), 1),
            "castprev_triggered": sum(tr for s0, s1, c, tg, tr, _ in r["castprev"] if c in own and t0 <= s1 < t1)}


def player_window(r, a, t0, t1):
    """One player's own totals in [t0, t1) (credit to the player who did it)."""
    return team_window(r, [a], [b for b in _all_players(r) if b != a], t0, t1)


def _all_players(r):
    s = set()
    for _, _, _, c, tg in r["degen"]: s.add(tg); s.add(c)
    for t, src, tg, *_ in r["kd"]: s.add(src); s.add(tg)
    s |= set(r["kite"]) | set(r["prekite"]) | set(r["wasted"]) | set(r["baits"])
    return {x for x in s if isinstance(x, int)}


def on_player(r, a, t, w=10):
    """What was being done to player a in the w seconds up to t: degen pips on it now, its kiting (seconds chased
    without being hit) and pre-kiting, skill-seconds disabled on it, cast prevention on it now."""
    ix = _by_target(r)
    pips = sum(x[2] for x in ix["degen"].get(a, ()) if x[0] <= t < x[1])
    return {"degen_pips_now": round(min(pips, DEGEN_CAP), 1),
            "kited_10s": _count(r["kite"].get(a, ()), t - w, t + 0.001),
            "prekited_10s": _count(r["prekite"].get(a, ()), t - w, t + 0.001),
            "disabled_skill_secs_10s": round(sum(x[3] for x in ix["disable"].get(a, ()) if t - w <= x[0] <= t), 1),
            "castprev_now": int(any(x[0] <= t < x[1] for x in ix["castprev"].get(a, ())))}


def _by_target(r):
    """The record's degen, disables and cast prevention indexed by target (built once per record; not saved)."""
    if "_by" not in r:
        r["_by"] = {"degen": collections.defaultdict(list), "disable": collections.defaultdict(list), "castprev": collections.defaultdict(list)}
        for x in r["degen"]: r["_by"]["degen"][x[4]].append(x)
        for x in r["disable"]: r["_by"]["disable"][x[2]].append(x)
        for x in r["castprev"]: r["_by"]["castprev"][x[3]].append(x)
    return r["_by"]


def players(rid):
    """Per-player totals over the whole match (snapshot tables)."""
    from replaylib import Match
    m = Match.from_branch(rid); r = record(rid)
    end = max([x[0] for x in m.o.get("ev") or [] if x[0] is not None] or [0]) / 10
    out = {}
    for a in m.PL:
        tot = team_window(r, [a], [b for b in m.PL if m.team(b) != m.team(a)], -60, end + 60)
        out[a] = {"team": m.tag[m.team(a)], "role": m.roles.get(a), "prof": m.A[a].get("p"), "minutes": round(end / 60, 2), **tot}
    return out


if __name__ == "__main__":
    import sys
    rid = sys.argv[1]
    if len(rid) < 36:
        import common; rid = next(k for k in common.replay_index() if k.startswith(rid))
    for a, v in players(rid).items(): print(v)
