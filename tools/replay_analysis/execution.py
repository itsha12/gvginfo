"""Execution of a play, read the same way for both teams (REDESIGN 2.12; R-299, R-572, R-621).

How a play was carried out in its first seconds, for the team that makes the play ("own") and for the players it meets
("their"), each side by the same measures, so that the enemy's execution is scored as ours is (R-299) and is never
offered as a fix. A record kept beside the plays (`flag_cost[rid].execution`, one entry a play id): it tells no play
and changes none.

The window is the play's first EXEC_S seconds (or the whole play where it is shorter; nothing under EXEC_MIN_S): a
fixed early stretch, read before the result (SPEC 5, rule 1). Who is read: the players the play names (`who`, a split
or its defence), else the team's main team at the second the play is told; against them, every enemy player in the
same fight as one of them in the window (`Moments.linked`, the one reading of who is in which fight, R-464). A play
whose players meet nobody has `n[1]` 0 and its measures say only what it did on its own (a run, a stand-off).

Measures (MEASURES: key, the direction a higher value should go for the team doing it, what it is in a player's words).
Amounts by players are a living player a 10 s; counts are the group's a 10 s; shares are 0 to 1, blank where there is
nothing to take a share of (a blank that means "no damage dealt", not a fault, R-460).

Sources: the replay's damage, heal and interrupt events; `pressure.py` (kiting, degen, baits, knockdowns, disables,
cast prevention); the event layer (`eventlayer.py`: strips and wasted strips, time spent Blind, hexes kept up, hex
removal); the usual damage of each role (`eventlayer.usual_dps`, the role's measured middle).
The team's own care, read with `forensics.py` on the play's window (the measurements of a death, asked of a play):
casts into a ready interrupt (`Forensics.casting`), attacks made while Blind, and damage taken off a shield set while
not casting (`Forensics.sets_damage`).
Not read here: energy (not in the replays); what a prot did (R-636, at the rebuild).

Usage:  python3 execution.py <report id> [m:ss]     the execution record of a match's plays (from the second given)"""
import bisect, collections, sys
from common import SPIKE_BURST

EXEC_S = 20                 # the stretch of a play its execution is read on: the first 20 s, as the call is read 20 s in (R-556, R-567); Claude's draft
EXEC_MIN_S = 6              # a play shorter than this has no execution read
EXEC_STEP = 2               # who meets whom is read every other second, as the fights are

MEASURES = (
    ("dmg", +1, "damage on their players, a living player a 10 s"),
    ("dmg_v_usual", +1, "that damage against the usual of the players alive (1.0 is the usual)"),
    ("healer_share", 0, "share of that damage on their backline monks (offence or defence: no direction, R-304)"),
    ("focus", 0, "share of that damage on the one player hit most"),
    ("spikes", +1, f"bursts of {SPIKE_BURST[0]} or more on one player inside {SPIKE_BURST[1]:.0f} s, a 10 s"),
    ("interrupts", +1, "interrupts landed, a 10 s"),
    ("interrupts_on_healers", +1, "interrupts landed on their backline monks, a 10 s"),
    ("knockdowns", +1, "knockdowns landed, a 10 s"),
    ("knockdowns_on_casting", +1, "knockdowns landed on a player who was casting, a 10 s"),
    ("disable", +1, "skill-seconds disabled on them (Complicate, Power Lock, Power Block, Blackout), a 10 s"),
    ("castprev", +1, "casts of theirs punished by Shame, Guilt or Diversion, a 10 s"),
    ("degen", +1, "degeneration kept on them, pip-seconds a 10 s"),
    ("kite", +1, "seconds their melee chased without hitting (kiting and pre-kiting), a 10 s"),
    ("baits", +1, "their interrupts thrown at a cancelled cast, a 10 s"),
    ("strips", +1, "useful strips (a prot off a player under attack, or an enchantment off their midline or frontline), a 10 s"),
    ("strips_wasted", -1, "strips that removed nothing, a 10 s"),
    ("blind_secs", +1, "seconds their physical attackers spent Blind, a 10 s"),
    ("hex_secs", +1, "hex-seconds kept on them, a 10 s"),
    ("hex_removed", +1, "hexes removed from our own players, a 10 s"),
    ("npc_dmg", 0, "damage on their NPCs, a living player a 10 s"),
    ("npc_heal", 0, "healing on our own NPCs, a 10 s"),
    ("into_ready", -1, "casts started with an enemy interrupt ready and in range, a 10 s"),
    ("blind_attacks", -1, "attacks made while Blind, a 10 s"),
    ("off_shield", -1, "share of the damage taken that landed on a player off his shield set and not casting (players who carry a shield set)"),
)
KEYS = tuple(k for k, _, _ in MEASURES)
SIGN = {k: s for k, s, _ in MEASURES}
WORDS = {k: w for k, _, w in MEASURES}


class Exec:
    """One match's events laid out for windows. `side(X, Y, t0, t1)`: what the players X did to the players Y."""

    def __init__(self, M, rid):
        import pressure as PR, eventlayer as EL
        from phases import healer, line
        self.M, self.m, self.rid = M, M.m, rid
        m = self.m
        self.PR, self.prr = PR, PR.record(rid)
        self.R = EL.records(rid)
        self.V = EL.load_values()
        self.usual = {}
        for a in m.PL:
            cl = "healer" if healer(m, a) else ("frontline" if line(m, a) == "frontline" else "midline")
            self.usual[a] = EL.usual_dps(self.V, m.roles.get(a), cl) or 0.0
        self.healer = {a for a in m.PL if healer(m, a)}
        self.agent = {(m.tag[m.team(a)], m.roles[a]): a for a in m.PL}
        pl = set(m.PL)
        self.dm, self.dm_npc, self.hl_npc = [], [], []
        for r in m.o["ev"]:
            if r[0] is None or r[1] not in ("dm", "hl") or not isinstance(r[2], int) or not isinstance(r[3], int) or max(r[2], r[3]) >= len(m.A): continue
            n = r[5] if len(r) > 5 and isinstance(r[5], (int, float)) else 0
            if n <= 0 or r[2] not in pl: continue
            if r[1] == "dm":
                if r[3] in pl and m.team(r[3]) != m.team(r[2]): self.dm.append((r[0] / 10, r[2], r[3], n))
                elif m.A[r[3]].get("npc") and m.A[r[3]].get("team") not in (None, m.team(r[2])): self.dm_npc.append((r[0] / 10, r[2], r[3], n))
            elif m.A[r[3]].get("npc") and m.A[r[3]].get("team") == m.team(r[2]): self.hl_npc.append((r[0] / 10, r[2], r[3], n))
        for L in (self.dm, self.dm_npc, self.hl_npc): L.sort(key=lambda x: x[0])
        self._t = {id(L): [x[0] for x in L] for L in (self.dm, self.dm_npc, self.hl_npc)}
        self.intr = sorted((i[0] / 10, i[1], i[3]) for i in (m.o.get("interrupts") or []) if i[0] is not None and i[1] in pl and i[3] in pl)
        import forensics
        self.F = forensics.Forensics(rid, m)
        self.blind = collections.defaultdict(list)             # player -> [(from, to)] Blind on him
        for e in m.o.get("effects") or []:
            if e[2] == "c" and e[7] == "blind" and e[0] is not None and e[5] in pl: self.blind[e[5]].append((e[0] / 10, e[1] / 10 if e[1] is not None else 1e9))
        self.att = collections.defaultdict(list)               # player -> the seconds he attacked
        for r in m.o["ev"]:
            if r[0] is not None and r[1] == "at" and r[2] in pl: self.att[r[2]].append(r[0] / 10)
        for a in self.att: self.att[a].sort()

    def _cut(self, L, t0, t1):
        T = self._t[id(L)]
        return L[bisect.bisect_left(T, t0):bisect.bisect_left(T, t1)]

    def side(self, X, Y, t0, t1):
        """What the players X did to the players Y in [t0, t1): one dict of MEASURES, or None where no player of X is alive in it."""
        M, m = self.M, self.m
        X, Y, secs = set(X), set(Y), t1 - t0
        if not X or secs <= 0: return None
        tm = m.team(next(iter(X)))
        ps = sum(1 for u in range(int(t0), int(t1)) for a in X if M.AL[a][min(u, M.T)])
        if not ps: return None
        g10, p10 = (lambda v: round(10.0 * v / secs, 2)), (lambda v: round(10.0 * v / ps, 1))
        by_t = collections.defaultdict(list)
        for t, a, b, n in self._cut(self.dm, t0, t1):
            if a in X and b in Y: by_t[b].append((t, n))
        tot = sum(n for v in by_t.values() for _, n in v)
        usual = sum(self.usual[a] for u in range(int(t0), int(t1)) for a in X if M.AL[a][min(u, M.T)])
        spikes = 0
        for v in by_t.values():
            i = 0
            while i < len(v):
                j, s = i, 0.0
                while j < len(v) and v[j][0] <= v[i][0] + SPIKE_BURST[1]: s += v[j][1]; j += 1
                if s >= SPIKE_BURST[0]: spikes += 1; i = j
                else: i += 1
        intr = [(a, b) for t, a, b in self.intr if t0 <= t < t1 and a in X and b in Y]
        tw = self.PR.team_window(self.prr, X, Y, t0, t1)
        tag, ftag = m.tag[tm], m.tag[3 - tm]
        xr, yr = {m.roles[a] for a in X}, {m.roles[a] for a in Y}
        ov = lambda s0, s1: max(0.0, min(s1, t1) - max(s0, t0))
        R = self.R
        F = self.F
        sd = F.sets_damage(tm, t0, t1, who=sorted(X))["measures"]
        blind_att = sum(1 for a in X for t in self.att[a][bisect.bisect_left(self.att[a], t0):bisect.bisect_left(self.att[a], t1)] if any(s0 <= t <= s1 for s0, s1 in self.blind.get(a, ())))
        out = {
            "dmg": p10(tot),
            "dmg_v_usual": round(tot / usual, 2) if usual > 0 else None,
            "healer_share": round(sum(n for b, v in by_t.items() if b in self.healer for _, n in v) / tot, 2) if tot else None,
            "focus": round(max(sum(n for _, n in v) for v in by_t.values()) / tot, 2) if tot else None,
            "spikes": g10(spikes),
            "interrupts": g10(len(intr)),
            "interrupts_on_healers": g10(sum(1 for _, b in intr if b in self.healer)),
            "knockdowns": g10(tw["knockdowns"]),
            "knockdowns_on_casting": g10(tw["knockdowns_on_casting"]),
            "disable": g10(tw["disable_skill_secs"]),
            "castprev": g10(tw["castprev_triggered"]),
            "degen": g10(tw["degen_pip_secs"]),
            "kite": g10(tw["kite_secs"] + tw["prekite_secs"]),
            "baits": g10(tw["baits"]),
            "strips": g10(sum(1 for s in R.get("strips", ()) if t0 <= s["t"] < t1 and s["team"] == tag and s["by"] in xr and s.get("useful"))),
            "strips_wasted": g10(sum(1 for s in R.get("strips_wasted", ()) if t0 <= s["t"] < t1 and s["team"] == tag and s["by"] in xr)),
            "blind_secs": g10(sum(ov(b["t"], b["end"]) for b in R.get("blinds", ()) if b["team"] == tag and b.get("attacker") and b["target"] in yr)),
            "hex_secs": g10(sum(ov(h["t"], h["t"] + (h.get("secs") or 0)) for h in R.get("hexes", ()) if h["team"] == ftag and h["target"] in yr)),
            "hex_removed": g10(sum(1 for h in R.get("hex_removals", ()) if t0 <= h["t"] < t1 and h["team"] == tag and h["by"] in xr and h.get("removed"))),
            "npc_dmg": p10(sum(n for t, a, b, n in self._cut(self.dm_npc, t0, t1) if a in X)),
            "npc_heal": g10(sum(n for t, a, b, n in self._cut(self.hl_npc, t0, t1) if a in X)),
            "into_ready": g10(sum(F.casting(a, t0, t1)["measures"]["into_ready_interrupt"] for a in X)),
            "blind_attacks": g10(blind_att),
            "off_shield": sd["off_shield_share"] if sd["taken"] > 1 else None,
        }
        return out

    def players(self, p):
        """The players a play's execution is read for, and the enemy players they meet in its window: (X, Y, t0, t1), or None where the play is too short."""
        M, m = self.M, self.m
        tm, t0 = p["tm"], int(p["t0"])
        t1 = min(int(p["t1"]), t0 + EXEC_S, M.T)
        if t1 - t0 < EXEC_MIN_S: return None
        X = [self.agent[(m.tag[tm], r)] for r in (p.get("who") or ()) if (m.tag[tm], r) in self.agent]
        if not X: X = [a for a in M.main_team(tm, t0) if M.AL[a][t0]] or [a for a in M.st.players[tm] if M.AL[a][t0]]
        Y = set()
        for u in range(t0 - t0 % EXEC_STEP, t1 + 1, EXEC_STEP):
            if u > M.T: break
            live = [a for a in X if M.AL[a][u]]
            for b in M.st.players[3 - tm]:
                if b not in Y and M.AL[b][u] and any(M.linked(a, b, u) for a in live): Y.add(b)
        return X, sorted(Y), t0, t1

    def play(self, p):
        w = self.players(p)
        if w is None: return None
        X, Y, t0, t1 = w
        own = self.side(X, Y, t0, t1)
        if own is None: return None
        return {"s": t1 - t0, "n": [len(X), len(Y)], "own": own, "their": self.side(Y, X, t0, t1) if Y else None}


def record(M, rid, plays):
    """{play id: its execution record} for the plays of one match (kept beside the plays; no play reads it)."""
    E, out = Exec(M, rid), {}
    for p in plays:
        r = E.play(p)
        if r is not None: out[p["id"]] = r
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit()
    from replaylib import Match
    from state import GameState
    from scoreboard import Scoreboard
    import jobs, moments
    st = GameState(Match.from_branch(a[0]))
    M = moments.Moments(st, Scoreboard(st))
    P = jobs.plays(M, M.records())
    for p in P: p.setdefault("id", f"{p['play']}-{p['tm']}-{p['t0']}")
    frm = (lambda s: int(s.split(":")[0]) * 60 + int(s.split(":")[1]))(a[1]) if len(a) > 1 else 0
    E = Exec(M, a[0])
    for p in sorted(P, key=lambda p: p["t0"]):
        if p["t0"] < frm: continue
        r = E.play(p)
        if r is None: continue
        print(f"\n{p['t0'] // 60}:{p['t0'] % 60:02d} {p['play']} ({p['team']}), {r['n'][0]} against {r['n'][1]}, first {r['s']} s: {p['scenario'][:110]}")
        for k in KEYS:
            o, t = r["own"].get(k), (r["their"] or {}).get(k)
            if o or t: print(f"    {k:22} own {'' if o is None else o:>7}   their {'' if t is None else t:>7}   {WORDS[k]}")
