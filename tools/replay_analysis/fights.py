"""Fight-level episodes: deaths (what happened in the 15 s before), monk profiles (casting, reaction, spacing),
numbers windows (who had more players in the main fight, why, and what they did with it) and team posture (offensive
or defensive against the situation).

Usage:  python3 fights.py <report id> [fights] [deaths] [monks] [windows] [posture]
In code: deaths(st, sb), engagements(st, sb, deaths), monks(st), windows(st), posture(st) -> lists of dicts (analyze.py)."""
import bisect, collections, math, statistics, sys
from replaylib import Match
from state import GameState, d
from scoreboard import Scoreboard
from common import (CAST_R, PRE, SPIKE_REACT, SPIKE_BURST, SUPPORT_SHARE, CHAIN_GAP, AFTER_TIME, RES_EVERY, CRITICAL, BLOCKS,
                    GAP_CLOSERS, STRIP_SKILLS, skill_kind, activation)

SPIKE = SPIKE_REACT       # a burst a monk should react to (monk profiles)


def _monks(st, tm):
    """The healing backline: monks in slots 6 to 8 and any other monk without Word of Censure (smiters are damage)."""
    m = st.m
    return [a for a in st.players[tm] if m.A[a].get("p") == "Monk" and (m.A[a].get("slot") in (6, 7, 8)
            or not any(m.sk(b) == "Word of Censure" for b in m.A[a].get("bar", []) if b))]


def _casts(st):
    """Monk-relevant casts: [(t, caster, target, skill id, name, kind, finished?)]."""
    m, out = st.m, []
    starts = [r for r in m.o["ev"] if r[1] == "cs" and r[2] in m.PL]
    for r in starts:
        nm = m.sk(r[4]) if r[4] else ""
        out.append((r[0] / 10, r[2], r[3], r[4], nm, skill_kind(r[4], nm)))
    return out


def forensics(st, a, td, pre=PRE, sb=None):
    """Everything about one death that decides whether it was a misplay, a lack of support or a great enemy play:
    context (numbers, flag), backline in range and its state, prots on the victim (landed, stripped, interrupted),
    self-prots, knockdowns (through a block or not, moving into a Coward), interrupts (on critical skills, right after a
    knockdown, fakeable or not), conditions (cripple, Deep Wound, Daze on the monks), how the attackers got there
    (gap closers, the victim standing still), and peel on the attackers."""
    m = st.m; tm = m.team(a); foe = 3 - tm
    t0 = td - pre; T0, T1 = int(t0 * 10), int(td * 10)
    f = lambda t: m.f(int(t))
    R = lambda x: m.roles.get(x) or m.nm(x)
    mon = [b for b in _monks(st, tm) if b != a]
    hits = [r for r in m.o["ev"] if r[1] == "dm" and r[3] == a and T0 <= r[0] <= T1 and (r[5] or 0) > 0]
    attackers = collections.Counter(r[2] for r in hits if r[2] in m.PL)
    main_att = [x for x, _ in attackers.most_common(3)]
    out = {}
    # context
    out["numbers"] = f"{len(st.main_group(tm, int(td - 2)))}v{len(st.main_group(foe, int(td - 2)))}"
    out["carriers"] = [m.role(x) for x in st.carrier(td - 2)]
    # the flag situation for the victim's team (scoreboard: flag position judged on the next capture exchange)
    sb = sb or Scoreboard(st)
    tag, ftag = m.tag[tm], m.tag[foe]
    b5 = sb.at(int(td - 5))
    foe_pick = max((t / 10 for t, typ, x, *_ in m.o.get("flags", []) if typ == "flag_picked_up" and m.team(x) == foe and t / 10 <= td), default=None)
    enemy_running = [m.role(x) for x in st.carrier(td - 2) if m.team(x) == foe]
    out["flag"] = {"enemy_running": enemy_running, "enemy_running_for_s": round(td - foe_pick) if enemy_running and foe_pick else None,
                   "own_flag": b5[tag]["flag"], "own_flag_lead": b5[tag]["flag_lead"], "stand_owner": b5["stand"]["owner"],
                   "boost_in": b5["stand"]["boost_in"],
                   "own_runner_carrying": any(m.team(x) == tm for x in st.carrier(td - 2)),
                   "own_flag_duty": b5[tag]["flag_duty"], "victim_on_flag_duty": any(r == m.roles[a] for r, _ in b5[tag]["flag_duty"]),
                   "victim_zone": st.zone(a, td - 5)}
    out["dp"] = {"victim_morale": st.morale(a, td - 1), "victim_eff_hp": sb.eff_hp(a, td - 1),
                 "team_morale": b5[tag]["morale_sum"], "enemy_morale": b5[ftag]["morale_sum"],
                 "spike_threat": b5[tag]["spike_threat"], "killable_by_one_spike": b5[tag]["killable_by_one_spike"]}
    own, since = st.stand_owner(td)
    out["stand"] = f"{m.tag.get(own)} held {round(td - since)} s" if own else "nobody"
    # backline in cast range each second, and its state (k knocked down, c casting)
    # in_range_share is over the seconds the monk was alive; a monk dead for the whole window is "dead", not out of range
    rng = {}
    win = list(range(int(t0), int(td) + 1))
    for b in mon:
        secs = [t for t in win if st.alive(b, t)]
        inr = [t for t in secs if d(st.pos(b, t)[0], st.pos(a, t)[0]) <= CAST_R]
        states = collections.Counter(st.pos(b, t)[1]["st"] for t in secs if st.pos(b, t)[1])
        att_on = collections.Counter(R(r[2]) for r in m.o["ev"] if r[1] == "dm" and r[3] == b and T0 <= r[0] <= T1 and r[2] in m.PL)
        rng[R(b)] = {"alive_share": round(len(secs) / len(win), 2), "alive_at_death": st.alive(b, td - 1),
                     "in_range_share": round(len(inr) / len(secs), 2) if secs else None,
                     "states": dict(states), "under_attack_by": dict(att_on.most_common(3))}
    out["backline"] = rng
    # prots: enchantments on the victim, how they ended; prot casts started on the victim and what happened to them
    ench = []
    for e in m.o.get("effects", []):
        if e[5] == a and e[2] == "e" and e[0] is not None and e[0] <= T1 and (e[1] or 10 ** 9) >= T0:
            ench.append(f"{m.sk(e[3])} by {R(e[4])} {f(e[0])}-{f(e[1]) if e[1] else '?'} ({e[6]})")
    out["enchantments"] = ench
    irs = [i for i in m.o.get("interrupts", []) if T0 <= i[0] <= T1]
    att = []
    for r in m.o["ev"]:
        if r[1] == "cs" and r[3] == a and r[2] in st.players[tm] and T0 <= r[0] <= T1 and m.sk(r[4]) in CRITICAL:
            cut = next((i for i in irs if i[3] == r[2] and 0 <= i[0] - r[0] <= 30), None)
            att.append(f"{f(r[0])} {R(r[2])} {m.sk(r[4])}" + (f" INTERRUPTED by {R(cut[1])} {m.sk(cut[2])}" if cut else ""))
    out["prot_attempts"] = att
    if m.A[a].get("p") == "Monk":
        out["self_prots"] = [f"{f(r[0])} {m.sk(r[4])}" for r in m.o["ev"] if r[1] == "cs" and r[2] == a and (r[3] in (a, None))
                             and T0 <= r[0] <= T1 and skill_kind(r[4], m.sk(r[4])) == "prot"]
    # knockdowns: through a block? moving into a Coward?
    kds = []
    for k in m.o.get("knockdowns", []):
        if k[2] != a or not (T0 <= k[0] <= T1): continue
        blocked = [m.sk(e[3]) for e in m.o.get("effects", []) if e[5] == a and e[2] == "e" and m.sk(e[3]) in BLOCKS
                   and e[0] is not None and e[0] <= k[0] <= (e[1] or 10 ** 9)]
        mv = st.pos(a, k[0] / 10 - 1)[1]
        kds.append(f"{f(k[0])} {R(k[1])} {m.sk(k[3])}" + (f" through {', '.join(blocked)}" if blocked else ", no block up")
                   + (" (moving into a Coward)" if "Coward" in m.sk(k[3]) and mv and mv["st"] == "m" else ""))
    out["knockdowns"] = kds
    # interrupts on the victim and its backline: critical? right after a knockdown? fakeable (long into the cast)?
    rup = []
    for i in irs:
        if i[3] != a and i[3] not in mon: continue
        after_kd = any(k[2] == i[3] and 0 <= i[0] - k[0] <= 15 for k in m.o.get("knockdowns", []))
        crit = m.sk(i[4]) in CRITICAL
        rup.append(f"{f(i[0])} {R(i[1])} {m.sk(i[2])} on {R(i[3])} casting {m.sk(i[4])}" + (" (critical)" if crit else "")
                   + (f", {i[6]} ms into the cast" if i[6] is not None else "") + (" right after a knockdown" if after_kd else ""))
    out["interrupts"] = rup
    # conditions on the victim and Daze on its backline
    cond = []
    for e in m.o.get("effects", []):
        if e[2] == "c" and e[7] and e[0] is not None and T0 - 50 <= e[0] <= T1 and (e[5] == a or (e[5] in mon and e[7] in ("dazed", "crippled"))):
            cond.append(f"{e[7]} on {R(e[5])} by {R(e[4])} at {f(e[0])}")
    out["conditions"] = cond
    # how the attackers got there: gap closers used on the victim, the victim standing still before contact
    gc = [f"{f(r[0])} {R(r[2])} {m.sk(r[4])}" for r in m.o["ev"] if r[1] == "cs" and r[2] in main_att and m.sk(r[4]) in GAP_CLOSERS
          and T0 - 50 <= r[0] <= T1]
    approach = []
    for x in main_att:
        if m.A[x].get("p") not in ("Warrior", "Dervish", "Assassin"): continue
        ds = [(t, d(st.pos(x, t)[0], st.pos(a, t)[0])) for t in range(int(t0), int(td) + 1)]
        contact = next((t for t, dd in ds if dd < 150), None)
        if contact is not None:
            before = [st.pos(a, t)[1]["st"] for t in range(contact - 4, contact) if st.pos(a, t)[1]]
            approach.append(f"{R(x)} reached melee at {f(contact * 10)}; victim in the 4 s before: {''.join(before)} (m moving, i idle, c casting, k down)")
    out["approach"] = {"gap_closers": gc, "contact": approach}
    # peel: the victim's team hitting, knocking down, hexing or blinding its main attackers
    peel = collections.Counter()
    for r in m.o["ev"]:
        if r[1] == "dm" and r[3] in main_att and r[2] in st.players[tm] and T0 <= r[0] <= T1: peel[R(r[2])] += 1
    out["peel"] = dict(peel)
    out["peel_effects"] = [f"{m.sk(e[3])} on {R(e[5])} by {R(e[4])}" for e in m.o.get("effects", []) if e[5] in main_att and e[2] in ("h", "c")
                           and e[4] in st.players[tm] and e[0] is not None and T0 <= e[0] <= T1]
    return out


def assess(st, a, td, fx):
    """Denning's way of judging a death: what kind of death it was (cause) and the smaller mistakes around it, graded
    basic, minor or acceptable. Causes, in order: spike; backline down (a monk already dead: the death follows from an
    earlier one); the flag situation (outnumbered away from pit while up on flags; a fight during a forced flag run);
    positioning (out of range of its monks: overextended, caught away from its group, chased down while retreating, or
    out of range); coordinated enemy pressure (2+ monks tied up: a great enemy play); lack of support (a monk free, no
    prots); out-pressured despite support (prots cast, one monk tied up); out-damaged despite prots (backline free)."""
    m = st.m; tm = m.team(a)
    T0, T1 = int((td - PRE) * 10), int(td * 10)
    R = lambda x: m.roles.get(x) or m.nm(x)
    mon = [b for b in _monks(st, tm) if b != a]
    mistakes, notes = [], []
    bl = fx["backline"]
    live = {r: v for r, v in bl.items() if v["alive_at_death"]}
    dead_monks = [r for r, v in bl.items() if not v["alive_at_death"]]
    victim_monk = m.A[a].get("p") == "Monk"
    need = min(1 if victim_monk else 2, len(live))
    in_range = [r for r, v in live.items() if (v["in_range_share"] or 0) >= SUPPORT_SHARE]
    supported = bool(live) and len(in_range) >= need
    # pressure on the backline at the same time: each live monk under attack or knocked down
    pressured = [r for r, v in live.items() if v["under_attack_by"] or v["states"].get("k")]
    stripped = [e for e in fx["enchantments"] if "removed" in e]
    attempts = fx["prot_attempts"]
    hits = sorted((h[0], h[5]) for h in m.o["ev"] if h[1] == "dm" and h[3] == a and T0 <= h[0] <= T1 and (h[5] or 0) > 0)
    w = int(SPIKE_BURST[1] * 10)
    burst = max((sum(v for tt, v in hits if t <= tt <= t + w) for t, _ in hits), default=0)
    hp_before = st.pos(a, td - 3)[1]
    flag = fx.get("flag", {})
    zone = flag.get("victim_zone")
    # how a death out of range happened
    main = st.main_group(tm, int(td - 3)); mc = st.centroid(main, int(td - 3)); p = st.pos(a, td - 3)[0]
    foe_pit = st.geo.pit.get(3 - tm); own_pit = st.geo.pit.get(tm)
    p0 = st.pos(a, td - PRE)[0]
    retreating = p0 and p and own_pit and d(p, own_pit) < d(p0, own_pit) - 300
    if burst >= SPIKE_BURST[0] and hp_before and hp_before["hp"] >= 60: cause = "spike"
    elif dead_monks and not supported:
        died_recently = any(tt for b in mon for tt in st.death_times.get(b, []) if 0 <= td - tt <= CHAIN_GAP)
        cause = f"backline down ({len(dead_monks)} monk{'s' if len(dead_monks) > 1 else ''} dead" + (", in a chain)" if died_recently else ")")
    elif flag.get("enemy_running") and flag.get("own_flag") == "up" and not flag.get("own_runner_carrying") \
            and not flag.get("victim_on_flag_duty") and not supported and zone in ("backside", "stand"):
        # Denning [Men v HC C]: up on flags, the team need not cap at once; the backside group falls back toward pit
        # and only follows if the enemy goes for the runner
        cause = "outnumbered away from pit while up on flags"
        mistakes.append("minor: up on flags with the runner not under threat, the group should have fallen back toward "
                        "pit (and the runner could wait before capping) rather than fight outnumbered")
    elif flag.get("enemy_running") and flag.get("own_flag") != "up" and not supported:
        cause = "fight during a forced flag run (enemy running, team not up on flags)"
    elif not supported:
        if a not in main and mc and p and d(p, mc) > 2000 and zone not in ("own pit", "own base"):
            cause = "positioning: caught away from its group"
        elif mc and p and foe_pit and d(p, foe_pit) < d(mc, foe_pit) - 1000 and zone in ("push side", "enemy base", "enemy pit"):
            cause = "positioning: overextended (ahead of its team on the enemy side)"
        elif retreating: cause = "positioning: chased down while retreating"
        else: cause = "positioning: out of range of its monks"
    elif len(pressured) >= 2: cause = "coordinated enemy pressure (great enemy play)"
    elif not (attempts or stripped): cause = "lack of support (a monk free but no prots)"
    elif pressured: cause = "out-pressured despite support (prots cast, one monk tied up)"
    else: cause = "out-damaged despite prots (backline free)"
    dp = fx.get("dp", {})
    if dp.get("spike_threat") and dp.get("victim_eff_hp") and dp["victim_eff_hp"] <= dp["spike_threat"]:
        notes.append(f"DP stacking: at {dp['victim_morale']}% morale its health ({dp['victim_eff_hp']}) was within one enemy "
                     f"spike ({dp['spike_threat']})")
    # interrupts: quarter-second casts are luck, not a monk error (Denning)
    for i in fx["interrupts"]:
        sk = i.split(" casting ")[1].split(" (")[0].split(",")[0] if " casting " in i else ""
        if sk and activation(sk) <= 0.25: notes.append(f"unlucky interrupt on a ¼ s cast ({sk}): not a monk error")
    # the 8 (or any monk) Dazed by casting right beside a ranger without faking first (Denning: a mistake)
    for i in m.o.get("interrupts", []):
        if (i[3] in mon or (i[3] == a and m.A[a].get("p") == "Monk")) and T0 <= i[0] <= T1 and "Concussion" in m.sk(i[2]):
            close = d(st.pos(i[3], i[0] / 10)[0], st.pos(i[1], i[0] / 10)[0]) < 600
            faked = any(r[1] == "cx" and r[2] == i[3] and i[0] - 60 <= r[0] < i[0] - 3
                        and not any(j[3] == i[3] and abs(j[0] - r[0]) <= 3 for j in m.o.get("interrupts", []))  # a real fake, not an interrupt
                        and not any(k[2] == i[3] and abs(k[0] - r[0]) <= 3 for k in m.o.get("knockdowns", []))
                        for r in m.o["ev"])
            alone = not any(d(st.pos(b, i[0] / 10)[0], st.pos(i[3], i[0] / 10)[0]) <= CAST_R for b in _monks(st, tm) if b != i[3])
            msg = (f"minor: {R(i[3])} cast beside the ranger without cancel-casting first and got Dazed"
                   + (" (alone with no other monk: could be game ending, especially after time)" if alone else ""))
            if close and not faked and activation(m.sk(i[4])) > 0.25 and msg not in mistakes: mistakes.append(msg)
    # no Aura of Stability on a monk being knocked down (Denning), counted only when a holder had it recharged (12 s)
    # and was free to cast (alive, not knocked down) at the knockdown; it never covers its caster
    holders = [b for b in st.players[tm] if any(m.sk(x) == "Aura of Stability" for x in m.A[b].get("bar", []) if x)]
    aos = [r for r in m.o["ev"] if r[1] == "cs" and r[2] in holders and m.sk(r[4]) == "Aura of Stability"]
    up = [e for e in m.o.get("effects", []) if m.sk(e[3]) == "Aura of Stability" and e[0] is not None]
    missed_aos = collections.Counter()
    for k in m.o.get("knockdowns", []):
        b = k[2]
        if b not in mon + [a] or not (T0 - 100 <= k[0] <= T1): continue
        if any(e[5] == b and e[0] <= k[0] <= (e[1] or 10 ** 9) for e in up): continue
        for h in holders:
            if h == b or not st.alive(h, k[0] / 10): continue
            hs = st.pos(h, k[0] / 10)[1]
            last = max((r[0] for r in aos if r[2] == h and r[0] <= k[0]), default=-10 ** 6)
            if k[0] - last >= 120 and hs and hs["st"] != "k": missed_aos[(b, h)] += 1
    for (b, h), n in missed_aos.items():
        mistakes.append(f"acceptable: {R(h)} had Aura of Stability recharged but {R(b)} was knocked down without it ({n}x)")
    # no defensive interrupts on the enemy mesmers who stripped prots or burned energy (Denning)
    foe_mes = [b for b in st.players[3 - tm] if m.A[b].get("p") == "Mesmer"]
    shut = [r for r in m.o["ev"] if r[1] == "cs" and r[2] in foe_mes and r[3] in mon + [a] and T0 - 50 <= r[0] <= T1
            and any(w in m.sk(r[4]) for w in STRIP_SKILLS)]
    own_mes = [b for b in st.players[tm] if m.A[b].get("p") in ("Mesmer", "Ranger")]
    defensive = [i for i in m.o.get("interrupts", []) if i[1] in own_mes and i[3] in foe_mes and T0 - 50 <= i[0] <= T1]
    went = sorted({m.sk(r[4]) for r in shut} | ({"Shatter Enchantment (stripped a prot)"} if stripped else set()))
    if went and not defensive:
        mistakes.append(f"acceptable: no defensive interrupts on the enemy mesmers ({', '.join(went)} went off)")
    # Denning: a mesmer near a monk under attack should always interrupt defensively (hammer attack skills, Burning Arrow)
    own_mes_near = [b for b in st.players[tm] if m.A[b].get("p") == "Mesmer" and st.alive(b, td - 3)
                    and d(st.pos(b, td - 3)[0], st.pos(a, td - 3)[0]) < 1500]
    att_set = {r[2] for r in m.o["ev"] if r[1] == "dm" and r[3] == a and T0 <= r[0] <= T1 and r[2] in m.PL}
    on_att = [i for i in m.o.get("interrupts", []) if i[1] in own_mes_near and i[3] in att_set and T0 <= i[0] <= T1]
    if m.A[a].get("p") == "Monk" and own_mes_near and not on_att:
        mistakes.append(f"minor: {', '.join(R(b) for b in own_mes_near)} near the monk but no defensive interrupts on its attackers")
    # which way the victim moved relative to its own pit while under pressure (kiting toward protection or away)
    p0, p1 = st.pos(a, td - PRE)[0], st.pos(a, td - 1)[0]
    if p0 and p1 and st.geo.pit.get(tm):
        d0, d1 = d(p0, st.geo.pit[tm]), d(p1, st.geo.pit[tm])
        if abs(d1 - d0) > 300:
            notes.append(f"moved {'toward' if d1 < d0 else 'away from'} its own pit ({round(d0)} to {round(d1)})")
    # peel: hitting the attackers or enemy mesmers is defensive (or both); hitting enemy monks while dying is offensive only
    attackers = {r[2] for r in m.o["ev"] if r[1] == "dm" and r[3] == a and T0 <= r[0] <= T1 and r[2] in m.PL}
    tgt = collections.Counter()
    for r in m.o["ev"]:
        if r[1] == "dm" and r[2] in st.players[tm] and r[3] in st.players[3 - tm] and T0 <= r[0] <= T1:
            p = m.A[r[3]].get("p")
            tgt["the victim's attackers (defensive)" if r[3] in attackers and p != "Mesmer"
                else "enemy mesmers (offensive and defensive)" if p == "Mesmer"
                else "enemy monks (offensive only)" if p == "Monk" else "others"] += 1
    if tgt and tgt["enemy monks (offensive only)"] > 0.5 * sum(tgt.values()):
        mistakes.append("minor: team mostly hit enemy monks while the victim died (purely offensive)")
    return {"cause": cause, "mistakes": mistakes, "notes": sorted(set(notes)), "peel_targets": dict(tgt)}


def deaths(st, sb=None):
    m, out = st.m, []
    sb = sb or Scoreboard(st)
    casts = st.__dict__.setdefault("_casts", _casts(st))
    kd = m.o.get("knockdowns", []); ir = m.o.get("interrupts", [])
    # end-of-match markers: when a Lord dies, every player on that team "dies" in the same second; they aren't deaths
    same = collections.Counter((int(t), m.team(a)) for a in m.PL for t in st.death_times.get(a, []))
    for a in m.PL:
        for td in st.death_times.get(a, []):
            if td >= st.end - 1 or same[(int(td), m.team(a))] >= 5: continue
            tm, foe = m.team(a), 3 - m.team(a)
            t0 = td - PRE
            hits = [r for r in m.o["ev"] if r[1] == "dm" and r[3] == a and t0 * 10 <= r[0] <= td * 10 and (r[5] or 0) > 0]
            src = collections.Counter(); kinds = collections.Counter()
            for r in hits:
                src[m.role(r[2]) if r[2] is not None else "?"] += r[5]; kinds[r[6] or "?"] += r[5]
            # tightest burst
            best = 0
            for r in hits:
                w = sum(h[5] for h in hits if r[0] <= h[0] <= r[0] + 20)
                best = max(best, w)
            first_big = next((r[0] / 10 for r in hits if sum(h[5] for h in hits if r[0] <= h[0] <= r[0] + 20) >= 200), None)
            monks = _monks(st, tm)
            p_end = st.pos(a, td - 1)[0]
            monk_dist = {m.roles[b]: round(d(st.pos(b, td - 1)[0], p_end)) for b in monks if b != a and st.alive(b, td - 1)}
            main = st.main_group(tm, int(t0 + 5))
            mc = st.centroid(main, int(t0 + 5))
            isolated = d(st.pos(a, int(t0 + 5))[0], mc) > 2000 if a not in main else False
            own_casts = [(round(c[0] - (first_big or td), 1), m.roles[c[1]], c[4]) for c in casts
                         if c[2] == a and c[1] in monks and t0 <= c[0] <= td and c[5] in ("prot", "heal")]
            monk_busy = {}
            for b in monks:
                if b == a: continue
                cs = [c for c in casts if c[1] == b and (first_big or td) - 3 <= c[0] <= td and c[2] is not None]
                monk_busy[m.roles[b]] = [f"{c[4]}->{m.roles.get(c[2], m.nm(c[2]))}" for c in cs][:6]
            kds = [(round(r[0] / 10 - td, 1), m.roles.get(r[1])) for r in kd if r[2] == a and t0 * 10 <= r[0] <= td * 10]
            irs_t = [(round(r[0] / 10 - td, 1), m.roles.get(r[1]), m.sk(r[4])) for r in ir if r[3] == a and t0 * 10 <= r[0] <= td * 10]
            irs_m = [(round(r[0] / 10 - td, 1), m.roles.get(r[3]), m.sk(r[4])) for r in ir if r[3] in monks and t0 * 10 <= r[0] <= td * 10]
            attackers = {r[2] for r in hits if r[2] in m.PL}
            peel = sum(1 for r in m.o["ev"] if r[1] == "dm" and r[2] in st.players[tm] and r[3] in attackers and t0 * 10 <= r[0] <= td * 10)
            res = st.next_res(td)
            after_time = (td % RES_EVERY) <= AFTER_TIME
            before_time = (res - td) <= AFTER_TIME
            sets = m.o.get("sets", {}).get(str(a), []); snap = m.snap(a, int(td * 10) - 10)
            death_set = None       # holding its lowest-health weapon set (40+ below its highest) when it died
            if snap and len(sets) > 1 and 0 <= snap.get("w", -1) < len(sets):
                hps = [x.get("hp") or 0 for x in sets]
                death_set = (sets[snap["w"]].get("hp") or 0) == min(hps) and max(hps) - min(hps) >= 40
            out.append({
                "t": round(td), "team": m.tag[tm], "victim": m.roles[a], "zone": st.zone(a, td - 2), "after_time": after_time,
                "before_time": before_time, "death_set": death_set,
                "down_for": round(res - td), "burst_max_2s": round(best), "first_big_hit": round(first_big - td, 1) if first_big else None,
                "damage_by": {k: round(v) for k, v in src.most_common(5)}, "damage_kind": {k: round(v) for k, v in kinds.items()},
                "knockdowns": kds, "interrupts_on_victim": irs_t, "interrupts_on_monks": irs_m,
                "monk_casts_on_victim": own_casts, "monks_busy_with": monk_busy, "monk_distance": monk_dist,
                "isolated": isolated, "peel_hits": peel, "numbers": (len(st.main_group(tm, int(td - 2))), len(st.main_group(foe, int(td - 2)))),
                # what the death cost: everything that changed until the victim was back
                "then": sb.swing(m.tag[tm], td, res),
                "forensics": (fx := forensics(st, a, td, sb=sb)),
                "assessment": assess(st, a, td, fx),
            })
    return sorted(out, key=lambda x: x["t"])


def local_numbers(st, a, t, r=2000):
    """Players of each side alive within r of player a at second t (a included): the numbers where the fight was."""
    p = st.pos(a, t)[0]; tm = st.m.team(a)
    n = lambda x: sum(1 for b in st.players[x] if st.alive(b, t) and d(st.pos(b, t)[0], p) <= r)
    return (n(tm), n(3 - tm)) if p else (None, None)


def engagements(st, sb, ds=None):
    """Fights: deaths of either team no more than CHAIN_GAP s apart form one engagement. For the losing side: the trigger
    (its first death, with the death's own cause), the situation it fought in (from the scoreboard just before), where,
    whether it became a wipe, and what it cost until every player was back (Denning: individual deaths don't win
    games; what matters is what put the team there and what the fight was converted into)."""
    m = st.m
    ds = ds if ds is not None else deaths(st, sb)
    out, cur = [], []
    for x in sorted(ds, key=lambda x: x["t"]):
        if cur and x["t"] - cur[-1]["t"] > CHAIN_GAP: out.append(cur); cur = []
        cur.append(x)
    if cur: out.append(cur)
    res = []
    for g in out:
        losses = collections.Counter(x["team"] for x in g)
        tags = list(m.tag.values())
        first = g[0]
        loser = max(tags, key=lambda t: (losses[t], t == first["team"]))
        winner = next(t for t in tags if t != loser)
        ltm = next(k for k, v in m.tag.items() if v == loser)
        lost = [x for x in g if x["team"] == loser]
        trig = lost[0]
        start = max(g[0]["t"] - PRE, 0); end = g[-1]["t"]
        b = sb.at(start)
        L, W = b[loser], b[winner]
        monk_deaths = sum(1 for x in lost if "Monk" in x["victim"] or "Prot" in x["victim"])
        wipe = len(lost) >= 3 or monk_deaths >= 2
        # where the losing side died, relative to itself
        zones = collections.Counter(x["zone"] for x in lost)
        where = zones.most_common(1)[0][0]
        sit = []
        loc = local_numbers(st, next(a for a in st.players[ltm] if m.roles[a] == trig["victim"]), trig["t"] - 3)
        if loc[0] < loc[1]:
            why = [f"{r} {w}" for r, w in L["flag_duty"]] + [f"{r} down" for r in L["down"]]
            sit.append(f"outnumbered where it fought {loc[0]}v{loc[1]}" + (f" ({', '.join(why[:4])})" if why else ""))
        elif loc[0] > loc[1]:
            sit.append(f"lost while up in numbers where it fought {loc[0]}v{loc[1]}")
        if L["flag_duty"] and L["flag"] == "down": sit.append(f"running while down on flags ({L['flag_lead']:+} s)")
        if L["flag"] == "up" and where in ("backside", "stand") and W["flag_duty"]:
            sit.append(f"fought away from pit while up on flags ({L['flag_lead']:+} s): could fall back")
        if where in ("enemy pit", "enemy base"): sit.append(f"pushed into the enemy pit ({W['pit_npcs']} alive)")
        if where in ("own pit", "own base"): sit.append(f"defending its own pit ({L['pit_npcs']} alive)")
        if trig["after_time"]: sit.append("first death after time")
        if len(L["killable_by_one_spike"]) >= 2: sit.append(f"DP stacked against a spike ({len(L['killable_by_one_spike'])} within one spike)")
        if "Monk" in trig["victim"] or "Prot" in trig["victim"]: sit.append("a monk died first")
        if not sit: sit.append("even fight")
        back = max(st.next_res(x["t"]) for x in lost)
        cons = sb.swing(loser, start, back)
        gained = cons["npcs_lost"][loser] or cons["lord_damage"][winner] >= 500 or cons["boosts"].get(winner) \
                 or cons["caps"].get(winner)
        res.append({"team": loser, "opponent_won_fight": winner, "start": start, "end": end, "wipe": wipe, "local_numbers": loc,
                    "losses": dict(losses), "deaths": [(x["t"], x["team"], x["victim"], x["assessment"]["cause"]) for x in g],
                    "trigger": {"t": trig["t"], "victim": trig["victim"], "cause": trig["assessment"]["cause"],
                                "mistakes": trig["assessment"]["mistakes"]},
                    "where": where, "situation": sit,
                    "before": {loser: sb.summary(loser, start), winner: sb.summary(winner, start),
                               "stand": b["stand"]["owner"], "boost_in": b["stand"]["boost_in"]},
                    "archetypes": {loser: sb.arch[ltm]["kind"], winner: sb.arch[3 - ltm]["kind"]},
                    "consequence": cons, "converted": bool(gained)})
    return res


def monks(st, phase=120):
    """Per monk per 2-minute phase: casts by kind, top targets, reaction to bursts on allies, idle time while allies were
    hurt, interrupts and knockdowns received, cancelled casts (fakes), distance to the nearest enemy mesmer or ranger."""
    m, out = st.m, []
    casts = st.__dict__.setdefault("_casts", _casts(st))
    dmg = collections.defaultdict(list)
    for r in m.o["ev"]:
        if r[1] == "dm" and r[3] in m.PL and (r[5] or 0) > 0: dmg[r[3]].append((r[0] / 10, r[5]))
    bursts = []      # (t, ally) where ally took SPIKE[0]+ in SPIKE[1] s
    for a, L in dmg.items():
        last = -99
        for i, (t, _) in enumerate(L):
            tot = sum(x for tt, x in L[i:] if tt <= t + SPIKE[1])
            if tot >= SPIKE[0] and t - last > 5: bursts.append((t, a)); last = t
    stopped = [r for r in m.o["ev"] if r[1] == "cx"]
    irs = m.o.get("interrupts", []); kds = m.o.get("knockdowns", [])
    for tm in st.teams:
        foes_shut = [b for b in st.players[3 - tm] if m.A[b].get("p") in ("Mesmer", "Ranger")]
        for b in _monks(st, tm):
            for p0 in range(0, st.end, phase):
                p1 = min(p0 + phase, st.end)
                alive = sum(1 for t in range(p0, p1) if st.alive(b, t))
                if alive < 10: continue
                mine = [c for c in casts if c[1] == b and p0 <= c[0] < p1]
                kinds = collections.Counter(c[5] for c in mine)
                tg = collections.Counter(m.roles.get(c[2], "self" if c[2] == b else "other") for c in mine if c[2] is not None)
                react = []
                for t, a in bursts:
                    if not (p0 <= t < p1) or m.team(a) != tm or not st.alive(b, t): continue
                    if d(st.pos(b, t)[0], st.pos(a, t)[0]) > CAST_R: continue
                    first = next((c[0] - t for c in mine if c[2] == a and c[5] in ("prot", "heal") and t - 1 <= c[0] <= t + 4), None)
                    react.append(round(first, 1) if first is not None else None)
                idle_hurt = 0
                for t in range(p0, p1):
                    _, s = st.pos(b, t)
                    if not s or not m.alive(s) or s["st"] not in ("i", "m"): continue
                    if any(m.team(a) == tm and abs(tt - t) <= 1 and d(st.pos(a, t)[0], st.pos(b, t)[0]) < CAST_R for tt, a in bursts): idle_hurt += 1
                fakes = sum(1 for r in stopped if r[2] == b and p0 * 10 <= r[0] < p1 * 10
                            and not any(i[3] == b and abs(i[0] - r[0]) <= 3 for i in irs))
                spacing = []
                for t in range(p0, p1, 3):
                    p = st.pos(b, t)[0]
                    if not p or not st.alive(b, t): continue
                    ds = [d(p, st.pos(f, t)[0]) for f in foes_shut if st.alive(f, t)]
                    if ds: spacing.append(min(ds))
                caught = [x for x in react if x is not None]
                out.append({
                    "team": m.tag[tm], "monk": m.roles[b], "phase": f"{p0 // 60}-{p1 // 60} min", "alive_s": alive,
                    "casts_per_min": round(len(mine) / alive * 60, 1), "kinds": dict(kinds), "top_targets": tg.most_common(4),
                    "bursts_in_range": len(react), "answered": len(caught), "median_reaction": round(statistics.median(caught), 1) if caught else None,
                    "idle_while_ally_hurt_s": idle_hurt, "fakes": fakes,
                    "interrupted": sum(1 for i in irs if i[3] == b and p0 * 10 <= i[0] < p1 * 10),
                    "knocked_down": sum(1 for k in kds if k[2] == b and p0 * 10 <= k[0] < p1 * 10),
                    "median_dist_to_enemy_mes_or_ranger": round(statistics.median(spacing)) if spacing else None,
                })
    return out


def windows(st, min_len=10):
    """Stretches where one team had more players in the main fight (both mains within 2,500 of each other)."""
    m, out = st.m, []
    cur = None
    def numbers(t):
        a, b = st.main_group(1, t), st.main_group(2, t)
        ca, cb = st.centroid(a, t), st.centroid(b, t)
        return (len(a), len(b)) if d(ca, cb) < 2500 else None
    for t in range(0, st.end + 1):
        n = numbers(t)
        adv = None if not n or n[0] == n[1] else (1 if n[0] > n[1] else 2)
        if adv and cur and cur["adv"] == adv and t - cur["last"] <= 2:
            cur["last"] = t; cur["n"].append(n)
        else:
            if cur and cur["last"] - cur["start"] >= min_len: out.append(cur)
            cur = {"adv": adv, "start": t, "last": t, "n": [n]} if adv else None
    if cur and cur["last"] - cur["start"] >= min_len: out.append(cur)
    res = []
    for w in out:
        tm, foe, t0, t1 = w["adv"], 3 - w["adv"], w["start"], w["last"]
        # why the other side was short: its players away (carrying, splitting, dead)
        why = collections.Counter()
        for t in range(t0, t1 + 1, 3):
            main = st.main_group(foe, t); car = set(st.carrier(t))
            for b in st.players[foe]:
                if b in main: continue
                why["dead" if not st.alive(b, t) else ("running flag" if b in car else st.zone(b, t))] += 1
        dmg = sum(r[5] or 0 for r in m.o["ev"] if r[1] == "dm" and r[2] in st.players[tm] and r[3] in st.players[foe] and t0 * 10 <= r[0] <= t1 * 10)
        base = sum(r[5] or 0 for r in m.o["ev"] if r[1] == "dm" and r[2] in st.players[tm] and r[3] in st.players[foe]) / st.end
        kills = [(round(tt), m.roles[b]) for b in st.players[foe] for tt in st.death_times.get(b, []) if t0 <= tt <= t1 + 5]
        npcs = [(round(tt), st.geo.npcs[x]["kind"]) for x, tt in st.npc_dead.items() if x in st.geo.npcs
                and st.geo.npcs[x]["team"] == foe and t0 <= tt <= t1 + 10]
        losses = [(round(tt), m.roles[b]) for b in st.players[tm] for tt in st.death_times.get(b, []) if t0 <= tt <= t1 + 5]
        c0 = st.centroid(st.main_group(tm, t0), t0); c1 = st.centroid(st.main_group(tm, t1), t1)
        moved = round(d(c0, st.geo.pit[foe]) - d(c1, st.geo.pit[foe])) if c0 and c1 else None
        res.append({"team": m.tag[tm], "start": t0, "end": t1, "secs": t1 - t0,
                    "numbers": collections.Counter(f"{a}v{b}" if tm == 1 else f"{b}v{a}" for a, b in w["n"]).most_common(2),
                    "enemy_short_because": dict(why.most_common(3)), "pressure_vs_avg": round(dmg / max(t1 - t0, 1) / max(base, 1), 2),
                    "kills": kills, "npcs_taken": npcs, "losses": losses, "pushed_toward_enemy_pit": moved})
    return res


def posture(st, step=30):
    """Every 30 s: how far forward each team's main group is (0 = own pit, 1 = enemy pit) and the situation (numbers,
    morale, stand, NPCs), so offensive play in a bad situation stands out."""
    m, out = st.m, []
    for t in range(0, st.end + 1, step):
        s = st.at(t)
        row = {"t": t}
        for tm in st.teams:
            c = st.centroid(st.main_group(tm, t), t)
            a, b = d(c, st.geo.pit[tm]), d(c, st.geo.pit[3 - tm])
            fwd = round(a / (a + b), 2) if c else None
            x = s[m.tag[tm]]
            row[m.tag[tm]] = {"forward": fwd, "alive": x["alive"], "main": x["main"],
                              "morale_sum": sum(x["morale"].values()), "npcs": x["pit_npcs"]}
        row["stand"] = s["stand"]["owner"]
        out.append(row)
    return out


def show(st, what):
    m = st.m; f = lambda t: m.f(int(t * 10))
    if "fights" in what:
        print("== fights (engagements)")
        sb = Scoreboard(st)
        for x in engagements(st, sb):
            c = x["consequence"]
            print(f"{f(x['start'])}-{f(x['end'])} {x['team']} lost {x['losses']}{' WIPE' if x['wipe'] else ''} at {x['where']} | "
                  f"trigger {x['trigger']['victim']} ({x['trigger']['cause']}) | {'; '.join(x['situation'])}")
            print(f"    before: {x['before']}")
            print(f"    cost until back ({c['window_s']} s): NPCs {c['npcs_lost']}, caps {c['caps']}, boosts {c['boosts']}, "
                  f"Lord dmg {c['lord_damage']}, DP {c['dp_change']}, flag lead {c['flag_lead_change']:+}, edge {c['edge_change']:+}"
                  f"{'' if x['converted'] else ' | NOT CONVERTED'}")
    if "deaths" in what:
        print("== deaths")
        for x in deaths(st):
            print(f"{f(x['t'])} {x['team']} {x['victim']} at {x['zone']}{' AFTER TIME' if x['after_time'] else ''} (down {x['down_for']} s)"
                  f" | burst {x['burst_max_2s']} in 2 s | {x['numbers'][0]}v{x['numbers'][1]} | isolated {x['isolated']} | peel hits {x['peel_hits']}")
            print(f"    damage {x['damage_by']} | KDs {x['knockdowns']} | interrupts on victim {x['interrupts_on_victim']}")
            print(f"    own monk casts on victim {x['monk_casts_on_victim']} | interrupts on monks {x['interrupts_on_monks']}")
            print(f"    monks busy with {x['monks_busy_with']} | monk distance {x['monk_distance']} | then {x['then']}")
    if "monks" in what:
        print("== monks (per 2 minutes)")
        for x in monks(st):
            print(f"{x['team']} {x['monk']:7} {x['phase']:9} {x['casts_per_min']:5}/min {x['kinds']} | bursts {x['answered']}/{x['bursts_in_range']}"
                  f" react {x['median_reaction']} s | idle while hurt {x['idle_while_ally_hurt_s']} s | fakes {x['fakes']} | int {x['interrupted']}"
                  f" KD {x['knocked_down']} | to mes/ranger {x['median_dist_to_enemy_mes_or_ranger']}")
    if "windows" in what:
        print("== numbers windows")
        for x in windows(st):
            print(f"{x['team']} up {f(x['start'])}-{f(x['end'])} ({x['secs']} s) {x['numbers']} | enemy short: {x['enemy_short_because']}"
                  f" | pressure x{x['pressure_vs_avg']} | kills {x['kills']} | losses {x['losses']} | pushed {x['pushed_toward_enemy_pit']}")
    if "posture" in what:
        print("== posture (forward: 0 own pit, 1 enemy pit)")
        for x in posture(st):
            print(f"{f(x['t'])} " + " | ".join(f"{k}: fwd {v['forward']} up {v['alive']} main {v['main']} morale {v['morale_sum']} {v['npcs']}"
                                               for k, v in x.items() if isinstance(v, dict)) + f" | stand {x['stand']}")


if __name__ == "__main__":
    st = GameState(Match.from_branch(sys.argv[1]))
    show(st, sys.argv[2:] or ("fights", "deaths", "monks", "windows", "posture"))
