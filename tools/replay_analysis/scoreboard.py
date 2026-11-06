"""The scoreboard: every edge that decides a GvG match, per team, at any second, so every layer judges situations the
same way (knowledge/tactics.md, "Reading the scoreboard").

Edges:
- Flag position (Denning): being up on flags means being in the better position to get a boost and to run, not having
  capped last. A team's flag ETA is how many seconds until it could capture: carrying = the carrier's distance to the
  stand; a dropped flag = the nearest teammate's walk to it plus the carry; at the spawn = the best runner's trip to the
  spawn (a dead runner waits for the res) plus the full carry (Y). Position is judged on the next capture exchange:
  the team not holding the stand (C) captures in ETA_C; the holder (H) answers when its own flag arrives, so its
  response is max(ETA_H - ETA_C, 0); C then needs its next flag: Y if a runner is already waiting at its spawn (full
  running), else its carrier's walk back plus Y (2Y). flag_lead = the enemy's response minus the own: positive = up on
  flags by that many seconds, about the length of the power play the exchange gives. A holder with a backup flag near
  the stand answers at once (response 0); a defender that carries its flag partway while holding off a solo pusher
  shortens its Y. Checked against Denning's ruling at [Men v HC C] 9:31 (HC up) and against the real exchange times.
- Flag clock: the holder's next boost, and whether the other team can capture before it.
- Flag duty: players carrying, waiting at the spawn, or walking back after a capture (not in the fight).
- Numbers: players alive, in the main group, and down (with when they return).
- Death penalty: morale per player and team; effective max health; spike threat (the enemy's typical kill burst) and
  how many players it now kills outright (DP stacking against a spike team).
- Pit NPCs alive, Lord damage dealt (the 28:00 tiebreak; players don't see it).
- Build archetype and measured Lord pressure: the summed Lord damage per second of the team's non-healers, from
  data/benchmarks/lord_damage.json (benchmarks.py lord, measured at the Lord across every stored replay), and the
  healing monks it keeps. No guessed weights: a profession without measured data gives None.

Usage:  python3 scoreboard.py <report id> [step]      prints the scoreboard every step seconds (default 30)
In code: sb = Scoreboard(st); sb.at(t) -> dict; sb.edge(tag, t) -> provisional edge value."""
import bisect, collections, math, statistics, sys
from replaylib import Match
from state import GameState, d
from common import RUN_SPEED, CARRY_SPEED, RES_EVERY, BOOST_EVERY, SPIKE_REACT

UP_ON_FLAGS = 10                # seconds of flag lead that count as up on flags
LATE = 24 * 60                  # the late game (know the tiebreak from here)
NPC_VALUE = {"knight": 3, "bodyguard": 3, "archer": 1.5}
_LORD = None
def lord_dps(role, prof):
    """Measured Lord damage per second at the Lord (role first, else profession; None if never measured)."""
    global _LORD
    if _LORD is None:
        import json, os
        from common import REPO
        try: _LORD = json.load(open(os.path.join(REPO, "data", "benchmarks", "lord_damage.json")))
        except (OSError, ValueError): _LORD = {"by_role": {}, "by_profession": {}}
    r = _LORD["by_role"].get(role.rstrip(" 0123456789").replace("Hammer A", "Hammer").replace("Hammer B", "Hammer"))
    if r and not r["thin"]: return r["dps"]
    p = _LORD["by_profession"].get(prof)
    return p["dps"] if p and not p["thin"] else None


def archetype(m, tm):
    """Team build archetype from the bars (a label for grouping matchups, not a judgement), its measured Lord damage per
    second if all its non-healers were at the Lord, and its healing monks."""
    ps = [a for a in m.PL if m.team(a) == tm]
    bar = lambda a: {m.sk(b) for b in m.A[a].get("bar", []) if b}
    prof = lambda a: m.A[a].get("p")
    woc = sum(1 for a in ps if "Word of Censure" in bar(a))
    invoke = sum(1 for a in ps if "Invoke Lightning" in bar(a))
    paragon = sum(1 for a in ps if prof(a) == "Paragon") >= 2 or any("Decapitate" in bar(a) for a in ps)
    healers = sum(1 for a in ps if prof(a) == "Monk" and "Word of Censure" not in bar(a))
    from common import skill_type
    hexers = sum(1 for a in ps if prof(a) in ("Necromancer", "Mesmer") and sum(1 for s in bar(a) if "Hex" in skill_type(s)) >= 4)
    hammers = sum(1 for a in ps if prof(a) == "Warrior" and "Hammer Bash" in bar(a))
    front = sum(1 for a in ps if prof(a) in ("Warrior", "Dervish", "Assassin"))
    kind = ("WoC spike" if woc >= 2 else "invoke spike" if invoke >= 2 else "paragon spike" if paragon
            else "hex way" if hexers >= 2 and healers <= 2 else "double hammer balance" if hammers >= 2
            else "balance" if front >= 1 else "other")
    dps = [lord_dps(m.roles[a], prof(a)) for a in ps if not (prof(a) == "Monk" and "Word of Censure" not in bar(a))]
    power = round(sum(x for x in dps if x is not None), 1) if dps and None not in dps else None
    return {"kind": kind, "spike": kind.endswith("spike"), "healing_monks": healers, "lord_dps_measured": power}


class Scoreboard:
    def __init__(self, st):
        self.st, self.m = st, st.m
        m = self.m
        self.tags = {tm: m.tag[tm] for tm in st.teams}
        self.arch = {tm: archetype(m, tm) for tm in st.teams}
        self.runners = {tm: [a for a, _ in collections.Counter(c["a"] for c in st.carries if m.team(c["a"]) == tm).most_common()]
                        for tm in st.teams}
        self._flag_track()
        self._bursts()
        self._lord()
        self._busy()
        self._cache = {}

    # ---- the flag object of each team over time: ("spawn",) ("carried", a) ("dropped", pos)
    def _flag_track(self):
        m, st = self.m, self.st
        self.fl = {tm: [(-10 ** 6, ("spawn",))] for tm in st.teams}
        evs = [(t / 10, typ, a) for t, typ, a, *_ in m.o.get("flags", []) if m.team(a) in st.teams]
        for i, (t, typ, a) in enumerate(evs):
            tm = m.team(a)
            if typ == "flag_picked_up": self.fl[tm].append((t, ("carried", a)))
            elif typ == "flagstand_captured": self.fl[tm].append((t, ("spawn",)))     # a new flag appears at the spawn
            elif typ == "flag_dropped":
                p = st.pos(a, t)[0]
                nxt = next(((tt, b) for tt, ty, b in evs[i + 1:] if ty == "flag_picked_up" and m.team(b) == tm), None)
                # picked up again far from where it fell: it was returned to the spawn (assumed at once)
                far = nxt and p and d(st.pos(nxt[1], nxt[0])[0], p) > 1500
                self.fl[tm].append((t, ("spawn",) if far or not p else ("dropped", p)))
        self.fl_t = {tm: [x[0] for x in self.fl[tm]] for tm in st.teams}

    def _busy(self):
        """Times each player dealt or took damage (a player trading damage is fighting, not waiting to run)."""
        m = self.m
        b = collections.defaultdict(list)
        for r in m.o["ev"]:
            if r[1] == "dm" and (r[5] or 0) > 0:
                if r[2] in m.PL: b[r[2]].append(r[0] / 10)
                if r[3] in m.PL: b[r[3]].append(r[0] / 10)
        self.busy_t = {a: sorted(v) for a, v in b.items()}

    def fighting(self, a, t, w=10):
        L = self.busy_t.get(a, [])
        i = bisect.bisect_right(L, t)
        return i > 0 and t - L[i - 1] <= w

    def waiting_runner(self, tm, t):
        """A runner already at the spawn, out of the main group and not trading damage: the next flag is 1Y away."""
        st = self.st
        main = set(st.main_group(tm, t)); f = self.flag(tm, t)
        for b in self.runners[tm]:
            if b in main or not st.alive(b, t) or (f[0] == "carried" and f[1] == b): continue
            if d(st.pos(b, t)[0], st.geo.spawn[tm]) < 1200 and not self.fighting(b, t): return b
        return None

    def y(self, tm):
        return d(self.st.geo.spawn[tm], self.st.geo.stand) / CARRY_SPEED

    def exchange(self, t):
        """The next capture exchange from second t: who holds (H), who must capture (C), each team's response time
        and the flag lead (positive = up on flags)."""
        st = self.st
        owner, _ = st.stand_owner(t)
        eta = {tm: self.eta(tm, t) for tm in st.teams}
        if owner is None:
            return {tm: {"eta": eta[tm], "response": eta[tm][0], "lead": eta[3 - tm][0] - eta[tm][0]} for tm in st.teams}
        H, C = owner, 3 - owner
        tC = eta[C][0]
        tH = max(eta[H][0], tC)
        resp_H = tH - tC
        back = d(st.geo.stand, st.geo.spawn[C]) / RUN_SPEED
        nxt = (tC + self.y(C)) if self.waiting_runner(C, t) is not None else (tC + back + self.y(C))
        resp_C = max(nxt - tH, 0)
        return {H: {"eta": eta[H], "response": round(resp_H), "lead": round(resp_C - resp_H)},
                C: {"eta": eta[C], "response": round(resp_C), "lead": round(resp_H - resp_C)}}

    def flag(self, tm, t):
        i = bisect.bisect_right(self.fl_t[tm], t) - 1
        return self.fl[tm][max(i, 0)][1]

    def _bursts(self):
        """Enemy kill bursts on each team (3+ attackers, SPIKE_REACT damage in 2 s): the spike threat."""
        m = self.m
        self.burst = {tm: [] for tm in self.st.teams}
        hits = collections.defaultdict(list)
        for r in m.o["ev"]:
            if r[1] == "dm" and r[3] in m.PL and r[2] in m.PL and m.team(r[2]) != m.team(r[3]) and (r[5] or 0) > 0:
                hits[r[3]].append((r[0] / 10, r[2], r[5]))
        for v, L in hits.items():
            last = -99
            for i, (t, _, _) in enumerate(L):
                w = [h for h in L[i:] if h[0] <= t + SPIKE_REACT[1]]
                tot = sum(h[2] for h in w)
                if tot >= SPIKE_REACT[0] and len({h[1] for h in w}) >= 3 and t - last > 4:
                    self.burst[m.team(v)].append((t, tot)); last = t
        for tm in self.burst: self.burst[tm].sort()

    def _lord(self):
        m = self.m
        self.lord_hits = {tm: [] for tm in self.st.teams}     # damage dealt by tm to the enemy Lord
        for r in m.o["ev"]:
            if r[1] == "dm" and isinstance(r[3], int) and r[3] < len(m.A) and m.A[r[3]].get("npc") == "guild_lord" and r[2] in m.PL:
                self.lord_hits[m.team(r[2])].append((r[0] / 10, r[5] or 0))
        self.lord_cum = {}
        for tm, L in self.lord_hits.items():
            L.sort(); acc, ts, vs = 0, [], []
            for t, v in L: acc += v; ts.append(t); vs.append(acc)
            self.lord_cum[tm] = (ts, vs)

    def lord_damage(self, tm, t):
        ts, vs = self.lord_cum[tm]
        i = bisect.bisect_right(ts, t) - 1
        return round(vs[i]) if i >= 0 else 0

    # ---- flag position
    def _reach(self, b, p, t):
        """Seconds for player b to reach point p (a dead player waits for the res at its base)."""
        st = self.st
        if st.alive(b, t): return d(st.pos(b, t)[0], p) / RUN_SPEED
        return st.next_res(t) - t + d(st.geo.base[self.m.team(b)], p) / RUN_SPEED

    def eta(self, tm, t):
        """Seconds until tm could capture, and how (carrying, dropped flag, from the spawn with whom)."""
        st, geo = self.st, self.st.geo
        f = self.flag(tm, t)
        if f[0] == "carried" and st.alive(f[1], t):
            return round(d(st.pos(f[1], t)[0], geo.stand) / CARRY_SPEED), f"carrying ({self.m.roles[f[1]]})"
        cand = self.runners[tm] or self.st.players[tm]
        if f[0] == "dropped":
            best = min(cand, key=lambda b: self._reach(b, f[1], t))
            return round(self._reach(best, f[1], t) + d(f[1], geo.stand) / CARRY_SPEED), f"dropped flag ({self.m.roles[best]})"
        sp = geo.spawn[tm]
        best = min(cand, key=lambda b: self._reach(b, sp, t))
        return round(self._reach(best, sp, t) + d(sp, geo.stand) / CARRY_SPEED), f"from the spawn ({self.m.roles[best]})"

    def flag_duty(self, tm, t):
        """Players on flag duty: carrying, waiting near the spawn, or walking back after capturing (not in the main group)."""
        st, m = self.st, self.m
        main = set(st.main_group(tm, t)); out = []
        last_cap = {a: tt for tt, typ, a, *_ in ((x[0] / 10, x[1], x[2]) for x in m.o.get("flags", [])) if typ == "flagstand_captured" and tt <= t}
        for b in st.players[tm]:
            if b in main or not st.alive(b, t): continue
            f = self.flag(tm, t)
            if f[0] == "carried" and f[1] == b: out.append((m.roles[b], "carrying"))
            elif d(st.pos(b, t)[0], st.geo.spawn[tm]) < 1200 and not self.fighting(b, t): out.append((m.roles[b], "waiting at the spawn"))
            elif b in last_cap and t - last_cap[b] <= 45: out.append((m.roles[b], "walking back"))
        return out

    # ---- death penalty and spikes
    def eff_hp(self, a, t):
        base = self.m.A[a].get("hp") or 500
        return round(base * (100 + self.st.morale(a, t)) / 100)

    def spike_threat(self, tm, t):
        """The enemy's typical kill burst on tm so far (75th percentile, at least 5 bursts; else the whole match)."""
        L = [v for tt, v in self.burst[tm] if tt <= t]
        L = L if len(L) >= 5 else [v for _, v in self.burst[tm]]
        return round(statistics.quantiles(L, n=4)[2]) if len(L) >= 4 else None

    # ---- the whole board
    def at(self, t):
        t = int(t)
        if t in self._cache: return self._cache[t]
        st, m = self.st, self.m
        owner, since = st.stand_owner(t)
        held = t - since if owner else 0
        boost_in = round(BOOST_EVERY - held % BOOST_EVERY) if owner else None
        ex = self.exchange(t)
        eta = {tm: ex[tm]["eta"] for tm in st.teams}
        out = {"t": t, "res_in": round(st.next_res(t) - t), "late": t >= LATE,
               "stand": {"owner": m.tag.get(owner), "held_s": round(held), "boost_in": boost_in}}
        for tm in st.teams:
            foe = 3 - tm
            dead = [a for a in st.players[tm] if not st.alive(a, t)]
            morale = {m.roles[a]: st.morale(a, t) for a in st.players[tm]}
            threat = self.spike_threat(tm, t) if self.arch[foe]["spike"] else None
            f = self.flag(tm, t)
            lead = ex[tm]["lead"]
            out[m.tag[tm]] = {
                "alive": len(st.players[tm]) - len(dead), "main": len(st.main_group(tm, t)),
                "down": {m.roles[a]: round(st.next_res(t) - t) for a in dead},
                "flag_eta": eta[tm][0], "flag_how": eta[tm][1], "flag_response": ex[tm]["response"], "flag_lead": lead,
                "waiting_runner": (lambda b: self.m.roles[b] if b is not None else None)(self.waiting_runner(tm, t)),
                "flag": ("up" if lead >= UP_ON_FLAGS else "down" if lead <= -UP_ON_FLAGS else "even"),
                "backup_flag": owner == tm and f[0] in ("carried", "dropped")
                               and d(st.pos(f[1], t)[0] if f[0] == "carried" else f[1], st.geo.stand) < 2500,
                "can_cap_before_boost": (eta[tm][0] < boost_in) if owner == foe else None,
                "flag_duty": self.flag_duty(tm, t),
                "morale_sum": sum(morale.values()), "morale": {k: v for k, v in morale.items() if v},
                "spike_threat": threat,
                "killable_by_one_spike": [m.roles[a] for a in st.players[tm] if threat and a not in dead and self.eff_hp(a, t) <= threat],
                "pit_npcs": st.pit_npcs(tm, t), "npc_value": self.npc_value(tm, t),
                "lord_damage_dealt": self.lord_damage(tm, t),
            }
        self._cache[t] = out
        return out

    def npc_value(self, tm, t):
        st = self.st
        return sum(NPC_VALUE.get(v["kind"], 0) for a, v in st.geo.npcs.items()
                   if v["team"] == tm and v.get("pit") and st.npc_dead.get(a, 1e9) > t)

    def edge(self, tag, t):
        """Provisional edge value for one team at second t (to be replaced by the win-probability model after the bulk
        pull): own pit NPC value, morale (boosts minus DP), players down (seconds until they return), flag lead and Lord
        damage, each against the enemy's. Weights are first guesses; use differences over a window, not the level."""
        s = self.at(t); other = next(x for x in self.tags.values() if x != tag)
        def v(x):
            b = s[x]
            return (b["npc_value"] + b["morale_sum"] / 10 - sum(b["down"].values()) / 30 + b["lord_damage_dealt"] / 300)
        return round(v(tag) - v(other) + max(min(s[tag]["flag_lead"], 60), -60) / 30, 1)

    def swing(self, tag, t0, t1):
        """What changed for tag (against the enemy) between t0 and t1: deaths, pit NPCs, captures, boosts, Lord damage,
        DP, flag lead and the provisional edge. Used for the consequence of a death, a fight or a decision."""
        st, m = self.st, self.m
        tm = next(k for k, v in self.tags.items() if v == tag); foe = 3 - tm
        t1 = min(t1, st.end - 1)
        deaths = lambda x: sum(1 for a in st.players[x] for tt in st.death_times.get(a, []) if t0 < tt <= t1)
        npcs = lambda x: [st.geo.npcs[a]["kind"] for a, tt in st.npc_dead.items() if a in st.geo.npcs and st.geo.npcs[a]["team"] == x
                          and st.geo.npcs[a]["kind"] != "guild_lord" and t0 < tt <= t1]
        caps = collections.Counter(m.tag[x] for tt, x in st.caps if t0 < tt <= t1)
        boosts = collections.Counter()
        cl = st.caps + [(st.end, None)]
        for (c, x), (c2, _) in zip(cl, cl[1:]):
            k = 1
            while c + BOOST_EVERY * k < c2:
                if t0 < c + BOOST_EVERY * k <= t1: boosts[m.tag[x]] += 1
                k += 1
        a, b = self.at(int(t0)), self.at(int(t1))
        other = self.tags[foe]
        return {"window_s": round(t1 - t0), "deaths": {tag: deaths(tm), other: deaths(foe)},
                "npcs_lost": {tag: npcs(tm), other: npcs(foe)}, "caps": dict(caps), "boosts": dict(boosts),
                "lord_damage": {tag: b[tag]["lord_damage_dealt"] - a[tag]["lord_damage_dealt"],
                                other: b[other]["lord_damage_dealt"] - a[other]["lord_damage_dealt"]},
                "dp_change": {tag: b[tag]["morale_sum"] - a[tag]["morale_sum"], other: b[other]["morale_sum"] - a[other]["morale_sum"]},
                "flag_lead_change": b[tag]["flag_lead"] - a[tag]["flag_lead"],
                "edge_change": round(self.edge(tag, int(t1)) - self.edge(tag, int(t0)), 1)}

    def summary(self, tag, t):
        b = self.at(t)[tag]
        return (f"{b['alive']} up (main {b['main']}), flags {b['flag']} {b['flag_lead']:+} s, DP {b['morale_sum']}, "
                f"NPCs {b['pit_npcs']}, Lord dmg {b['lord_damage_dealt']}")


def show(sb, step=30):
    m = sb.m
    print({m.tag[tm]: sb.arch[tm] for tm in sb.st.teams})
    for t in range(0, sb.st.end + 1, step):
        s = sb.at(t)
        row = [f"{m.f(t * 10):>5}", f"stand {s['stand']['owner'] or '-'}" + (f" boost {s['stand']['boost_in']}s" if s['stand']['owner'] else "")]
        for tm in sb.st.teams:
            tag = m.tag[tm]; b = s[tag]
            row.append(f"{tag}: {b['alive']}up main{b['main']} flags {b['flag']}({b['flag_lead']:+}, eta {b['flag_eta']} {b['flag_how']})"
                       + (" BACKUP" if b["backup_flag"] else "") + f" DP{b['morale_sum']} {b['pit_npcs']} lord {b['lord_damage_dealt']}"
                       + (f" spike-killable {b['killable_by_one_spike']}" if b["killable_by_one_spike"] else ""))
        print(" | ".join(row))


if __name__ == "__main__":
    st = GameState(Match.from_branch(sys.argv[1]))
    show(Scoreboard(st), int(sys.argv[2]) if len(sys.argv) > 2 else 30)
