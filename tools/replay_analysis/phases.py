"""Phases, theatres, plans, jobs and capacities: the global view of a match (Denning: fights are global; a group is judged
by its job in its team's plan). Causal map nodes: A.phase, A.plan, A.jobs, A.roles_ratio, A.mesa_free and the
capacities K.1 to K.13 (data/model/causal_map.json).

- Theatre: every place on the map where players are, at one second: all alive players of both teams clustered by
  distance (THEATRE_R), giving local numbers such as "backside 3v4", "push side 5v3", "Mes/A 1v0 carrying".
- Phase: a stretch where both teams' setups (their theatres, rounded) stay the same; it ends when the setup changes
  for MIN_PHASE s, or at a death, a res or a capture.
- Plan (starting labels, Denning `J11`: to be found and amended from data): 8v8 brawl, power play, weak side holding,
  flag game, split pressure, holding in the pit, late Lord push, regrouping.
- Job per group: convert (strong side), hold (weak side), contest (even), cap and return (carrier), split (in the
  enemy base), defend (in its own base against a split), free (no enemy near).
- Capacities per group per phase (measured, nothing learned): damage dealers and healers, pressure (damage per s to
  enemy players), damage uptime (a damage dealer is active in a second it attacks, casts or deals damage, so kiting
  casters count) and lost damage-seconds by cause, healing per s, monk uptime, incoming damage per s,
  sustain margin, bursts and kills (kill conversion), control received, health ceiling. Then the phase's results and
  its trade (scoreboard swing for each team).

Usage:  python3 phases.py <report id> [m:ss-m:ss]     prints phases (all, or those overlapping the range)
In code: phases(st, sb) -> list of dicts (analyze.py)."""
import collections, math, statistics, sys
from replaylib import Match
from state import GameState, d
from scoreboard import Scoreboard, LATE
from common import RES_EVERY, PIT_R, line

THEATRE_R = 2000       # players within this of each other (either team) are in one theatre
MIN_PHASE = 8          # seconds a new setup must last to start a phase
BLIND = {"blind"}; WEAK = {"weakness", "weakness_or_cracked_armor"}; DAZE = {"dazed"}


def healer(m, a):
    """A healing monk (slots 6 to 8, or any monk without Word of Censure) or a healing ritualist in the 8 slot."""
    p = m.A[a].get("p"); bar = {m.sk(b) for b in m.A[a].get("bar", []) if b}
    if p == "Monk": return "Word of Censure" not in bar or m.A[a].get("slot") in (6, 7, 8)
    return p == "Ritualist" and m.A[a].get("slot") == 8


def theatres(st, t):
    """Clusters of alive players of both teams at second t: [{"members": {team: [agents]}, "centre": (x, y)}]."""
    live = [(a, st.pos(a, t)[0]) for tm in st.teams for a in st.players[tm] if st.alive(a, t)]
    live = [(a, p) for a, p in live if p]
    groups = []
    for a, p in live:
        hit = [g for g in groups if any(d(p, q) < THEATRE_R for _, q in g)]
        groups = [g for g in groups if g not in hit] + [[(a, p)] + [x for g in hit for x in g]]
    out = []
    for g in groups:
        mem = {tm: [a for a, _ in g if st.m.team(a) == tm] for tm in st.teams}
        out.append({"members": mem, "centre": (statistics.mean(p[0] for _, p in g), statistics.mean(p[1] for _, p in g))})
    return out


def zone_of(st, tm, p):
    """Zone of a point from team tm's side (own pit, own base, backside, stand, push side, enemy base, enemy pit)."""
    g = st.geo
    if d(p, g.pit.get(tm)) < PIT_R: return "own pit"
    if d(p, g.pit.get(3 - tm)) < PIT_R: return "enemy pit"
    if d(p, g.stand) < 1500: return "stand"
    if d(p, g.base.get(tm)) < 2500: return "own base"
    if d(p, g.base.get(3 - tm)) < 2500: return "enemy base"
    return "backside" if d(p, g.base.get(tm)) < d(p, g.base.get(3 - tm)) else "push side"


def setup(st, t):
    """Each team's setup at t: sorted (zone, own, enemy) for each theatre it has players in; carriers marked."""
    car = set(st.carrier(t))
    th = theatres(st, t)
    sig = {}
    for tm in st.teams:
        rows = []
        for x in th:
            own, foe = x["members"][tm], x["members"][3 - tm]
            if not own: continue
            z = zone_of(st, tm, x["centre"])
            rows.append((z, len(own), len(foe), any(a in car for a in own)))
        sig[tm] = tuple(sorted(rows))
    return sig, th


def segment(st):
    """Phase boundaries: setup changes lasting MIN_PHASE s, deaths, res times, captures."""
    sigs = [setup(st, t)[0] for t in range(0, st.end)]
    hard = set(int(t) for a in st.m.PL for t in st.death_times.get(a, []))
    hard |= set(range(RES_EVERY, st.end, RES_EVERY)) | {int(t) for t, _ in st.caps}
    cuts, cur = [0], sigs[0]
    t = 1
    while t < st.end:
        if t in hard and t - cuts[-1] >= 3:
            cuts.append(t); cur = sigs[t]
        elif sigs[t] != cur and all(sigs[min(t + k, st.end - 1)] == sigs[t] for k in range(MIN_PHASE)) and t - cuts[-1] >= 3:
            cuts.append(t); cur = sigs[t]
        t += 1
    cuts.append(st.end)
    return list(zip(cuts, cuts[1:]))


def _groups_of(st, t0, t1, tm):
    """A team's groups across a phase: the theatres at the phase's middle second, with the enemy players in each."""
    tmid = (t0 + t1) // 2
    _, th = setup(st, tmid)
    car = set(st.carrier(tmid))
    out = []
    for x in th:
        own, foe = x["members"][tm], x["members"][3 - tm]
        if not own: continue
        out.append({"own": own, "enemy": foe, "zone": zone_of(st, tm, x["centre"]), "carrying": [a for a in own if a in car]})
    return out


def job(st, g, t, n_own, n_foe):
    if g["carrying"] and len(g["own"]) == 1: return "cap and return"
    if not g["enemy"]: return "free"
    if g["zone"] in ("enemy base", "enemy pit") and len(g["own"]) <= 4: return "split"
    if g["zone"] in ("own base", "own pit") and len(g["enemy"]) <= 4 and n_foe >= len(g["enemy"]): return "defend"
    a, b = len(g["own"]), len(g["enemy"])
    return "convert" if a > b else ("hold" if a < b else "contest")


def plan(st, sb, tm, groups, t):
    s = sb.at(t); tag = st.m.tag[tm]
    big = max(groups, key=lambda g: len(g["own"]), default=None)
    labels = []
    if t >= LATE and sum(len(g["own"]) for g in groups if g["zone"] == "enemy pit") >= 3: labels.append("late Lord push")
    if big and len(big["own"]) >= 6 and len(big["enemy"]) >= 6: labels.append("8v8 brawl")
    if any(len(g["own"]) - len(g["enemy"]) >= 2 and g["enemy"] for g in groups): labels.append("power play")
    if any(len(g["own"]) < len(g["enemy"]) for g in groups) and any(len(g["own"]) > len(g["enemy"]) and g["enemy"] for g in groups):
        labels.append("weak side holding")
    if s[tag]["flag_duty"] or any(g["carrying"] for g in groups): labels.append("flag game")
    if any(g["zone"] in ("enemy base", "enemy pit") and g is not big for g in groups): labels.append("split pressure")
    if big and big["zone"] in ("own pit", "own base"): labels.append("holding in the pit")
    if not labels: labels.append("regrouping")
    return labels


def capacities(st, sb, members, foes, t0, t1, ev_idx):
    """Measured capacities of one group over [t0, t1) against the enemy players in its theatre."""
    m = st.m
    T0, T1 = t0 * 10, t1 * 10
    secs = max(t1 - t0, 1)
    dmg_dealers = [a for a in members if not healer(m, a)]
    heals = [a for a in members if healer(m, a)]
    out = {"damage_dealers": len(dmg_dealers), "healers": len(heals)}
    ev = [r for r in ev_idx if T0 <= r[0] < T1]
    mem, fo = set(members), set(foes)
    dealt = sum(r[5] or 0 for r in ev if r[1] == "dm" and r[2] in mem and r[3] in m.PL and m.team(r[3]) != m.team(members[0]))
    taken = sum(r[5] or 0 for r in ev if r[1] == "dm" and r[3] in mem and r[2] in m.PL and m.team(r[2]) != m.team(members[0]))
    healed = sum(r[5] or 0 for r in ev if r[1] == "hl" and r[2] in heals and r[3] in m.PL and m.team(r[3]) == m.team(members[0]))
    out.update(pressure=round(dealt / secs), incoming=round(taken / secs), healing=round(healed / secs),
               sustain_margin=round((healed - taken) / secs))
    # damage uptime and lost damage-seconds by cause (priority: dead, knocked down, carrying, Blind, Weakness, moving, idle)
    eff = [e for e in m.o.get("effects", []) if e[2] == "c" and e[0] is not None and e[0] < T1 and (e[1] or 10 ** 9) > T0]
    def cond(a, t, names): return any(e[5] == a and e[7] in names and e[0] <= t * 10 <= (e[1] or 10 ** 9) for e in eff)
    car = {(c["a"], t) for c in st.carries for t in range(int(max(c["s"], t0)), int(min(c["e"], t1)))}
    hit_s = {(r[2], r[0] // 10) for r in ev if r[1] == "dm" and r[2] in mem and (r[5] or 0) > 0}   # dealt damage that second
    lost = collections.Counter(); active = 0
    for a in dmg_dealers:
        for t in range(t0, t1):
            s = st.pos(a, t)[1]
            if not s or s["st"] == "d" or not m.alive(s): lost["dead"] += 1; continue
            if s["st"] == "k": lost["knocked down"] += 1; continue
            if (a, t) in car: lost["carrying"] += 1; continue
            if cond(a, t, BLIND): lost["blind"] += 1; continue
            if s["st"] in ("a", "c") or (a, t) in hit_s:
                if cond(a, t, WEAK): lost["weakness (attacking weakened)"] += 1
                active += 1; continue
            lost["moving" if s["st"] == "m" else "idle"] += 1
    tot = len(dmg_dealers) * secs
    out["damage_uptime"] = round(active / tot, 2) if tot else None
    out["lost_damage_s"] = dict(lost.most_common())
    # monk uptime: seconds not knocked down, Dazed or dead
    up = sum(1 for a in heals for t in range(t0, t1)
             if (lambda s: s and m.alive(s) and s["st"] != "k")(st.pos(a, t)[1]) and not cond(a, t, DAZE))
    out["monk_uptime"] = round(up / (len(heals) * secs), 2) if heals else None
    # control received by the group
    irs = [i for i in m.o.get("interrupts", []) if T0 <= i[0] < T1 and i[3] in mem]
    kds = [k for k in m.o.get("knockdowns", []) if T0 <= k[0] < T1 and k[2] in mem]
    out["control_received"] = {"interrupts": len(irs), "on healers": sum(1 for i in irs if i[3] in heals),
                               "knockdowns": len(kds), "on healers kd": sum(1 for k in kds if k[2] in heals)}
    # bursts by the group (3+ attackers, 250+ in 2 s on one target) and kills
    hits = collections.defaultdict(list)
    for r in ev:
        if r[1] == "dm" and r[2] in mem and r[3] in fo and (r[5] or 0) > 0: hits[r[3]].append((r[0], r[2], r[5]))
    bursts = 0
    for v, L in hits.items():
        last = -999
        for i, (tt, _, _) in enumerate(L):
            w = [h for h in L[i:] if h[0] <= tt + 20]
            if sum(h[2] for h in w) >= 250 and len({h[1] for h in w}) >= 3 and tt - last > 40: bursts += 1; last = tt
    kills = sum(1 for a in foes for tt in st.death_times.get(a, []) if t0 <= tt < t1 + 2)
    losses = sum(1 for a in members for tt in st.death_times.get(a, []) if t0 <= tt < t1 + 2)
    out.update(bursts=bursts, kills=kills, losses=losses,
               kill_conversion=round(kills / bursts, 2) if bursts else None,
               health_ceiling=round(statistics.mean(sb.eff_hp(a, t0) / (m.A[a].get("hp") or 500) for a in members), 2))
    return out


def phases(st, sb=None):
    m = st.m; sb = sb or Scoreboard(st)
    ev_idx = [r for r in m.o["ev"] if r[1] in ("dm", "hl")]
    out = []
    for t0, t1 in segment(st):
        if t1 - t0 < 3: continue
        tmid = (t0 + t1) // 2
        row = {"start": t0, "end": t1, "secs": t1 - t0, "teams": {}}
        for tm in st.teams:
            tag = m.tag[tm]
            gs = _groups_of(st, t0, t1, tm)
            n_own = sum(len(g["own"]) for g in gs); n_foe = len(set(a for g in gs for a in g["enemy"]))
            groups = []
            for g in gs:
                jb = job(st, g, tmid, n_own, n_foe)
                cap = capacities(st, sb, g["own"], g["enemy"], t0, t1, ev_idx)
                held = jb in ("hold", "defend") and cap["losses"] == 0
                groups.append({"zone": g["zone"], "numbers": f"{len(g['own'])}v{len(g['enemy'])}", "job": jb,
                               "members": [m.roles[a] for a in g["own"]], "enemies": [m.roles[a] for a in g["enemy"]],
                               "job_done": (cap["losses"] == 0) if jb in ("hold", "defend", "cap and return") else
                                           (cap["kills"] > 0 if jb in ("convert", "split") else None),
                               "time_held": (t1 - t0) if held else 0, "capacities": cap})
            row["teams"][tag] = {"plan": plan(st, sb, tm, gs, tmid), "groups": sorted(groups, key=lambda g: -len(g["members"])),
                                 "dead": [m.roles[a] for a in st.players[tm] if not st.alive(a, tmid)]}
        sw = sb.swing(m.tag[1], t0, t1)
        row["trade"] = {"deaths": sw["deaths"], "npcs_lost": sw["npcs_lost"], "caps": sw["caps"], "boosts": sw["boosts"],
                        "lord_damage": sw["lord_damage"], "flag_lead_change": {m.tag[1]: sw["flag_lead_change"], m.tag[2]: -sw["flag_lead_change"]},
                        "edge_change": {m.tag[1]: sw["edge_change"], m.tag[2]: -sw["edge_change"]}}
        out.append(row)
    return out


def show(st, rng=None):
    m = st.m; f = lambda t: m.f(int(t * 10))
    for p in phases(st):
        if rng and (p["end"] < rng[0] or p["start"] > rng[1]): continue
        print(f"\n{f(p['start'])}-{f(p['end'])} ({p['secs']} s) | trade: deaths {p['trade']['deaths']}, NPCs {p['trade']['npcs_lost']}, "
              f"caps {p['trade']['caps']}, edge {p['trade']['edge_change']}")
        for tag, x in p["teams"].items():
            print(f"  {tag}: plan {', '.join(x['plan'])}" + (f" | dead {x['dead']}" if x["dead"] else ""))
            for g in x["groups"]:
                c = g["capacities"]
                print(f"    {g['numbers']} {g['zone']:10} job {g['job']:14} done {str(g['job_done']):5} {'+'.join(g['members'])} v {'+'.join(g['enemies']) or '-'}")
                print(f"       dmg {c['damage_dealers']} / heal {c['healers']} | pressure {c['pressure']}/s, incoming {c['incoming']}/s, "
                      f"healing {c['healing']}/s, margin {c['sustain_margin']} | uptime {c['damage_uptime']} lost {c['lost_damage_s']} | "
                      f"monk uptime {c['monk_uptime']} | control {c['control_received']} | bursts {c['bursts']} kills {c['kills']} losses {c['losses']}")


if __name__ == "__main__":
    st = GameState(Match.from_branch(sys.argv[1]))
    rng = None
    if len(sys.argv) > 2:
        a, b = sys.argv[2].split("-"); s2 = lambda x: int(x.split(":")[0]) * 60 + int(x.split(":")[1]); rng = (s2(a), s2(b))
    show(st, rng)
