"""Execution of a play, read the same way for both teams (REDESIGN 2.12; R-299, R-572, R-621).

How a play was carried out over the whole play (R-710), for the team that makes the play ("own") and for the players it meets
("their"), each side by the same measures, so that the enemy's execution is scored as ours is (R-299) and is never
offered as a fix. A record kept beside the plays (`flag_cost[rid].execution`, one entry a play id): it tells no play
and changes none.

The window is the whole play, from its start to its end (R-710; before it, the first 20 s); nothing under EXEC_MIN_S. A
team held in its base is read on the first HOLD_FIRST_S of the hold as well (`first`, R-621). Each kill attempt is to
be read to its own outcome (stage X2), so execution stays read before the result (R-299). Who is read: the players the play names (`who`, a split
or its defence), else the team's main team at the second the play is told; against them, every enemy player in the
same fight as one of them in the window (`Moments.linked`, the one reading of who is in which fight, R-464). A play
whose players meet nobody has `n[1]` 0 and its measures say only what it did on its own (a run, a stand-off).

Measures (MEASURES: key, the direction a higher value should go for the team doing it, what it is in a player's words).
Amounts by players are a living player a 10 s; counts are the group's a 10 s; shares are 0 to 1, blank where there is
nothing to take a share of (a blank that means "no damage dealt", not a fault, R-460).

Sources: the replay's damage, heal and interrupt events; degen, which the replay records as no damage, from gvg.report
(`degen.py`, R-638, R-649: in the damage on their players, the shares and the damage on their NPCs, and shown apart);
`pressure.py` (kiting, baits, knockdowns, disables, cast prevention); the event layer (`eventlayer.py`: strips and wasted strips, time spent Blind, hexes kept up, hex
removal); the usual damage of each role (`eventlayer.usual_dps`, the role's measured middle).
The team's own care, read with `forensics.py` on the play's window (the measurements of a death, asked of a play):
casts into a ready interrupt (`Forensics.casting`), attacks made while Blind, and damage taken off a shield set while
not casting (`Forensics.sets_damage`).
Energy taken from their players (R-685, R-692: whom a Mesmer drains, their monks or their midline, is execution and no
decision): `energy.denial`, the points taken by Energy Surge, Energy Burn, Mind Wrack, Power Leak, Shame, Guilt and
Malaise, and the share of them taken from their backline monks.
Carried from the old engine's execution nodes (stage X1, REDESIGN.md "Execution"): spike spread and spikes on healers
(the event layer's spikes), casts while Dazed (`Forensics.casting`), Blind on their frontline and defensive Blind, the
right strip and the worth stripped, the right hex removed (the event layer, valued against what was in range,
`eventlayer.valued`), time their players spent Crippled (control on a runner), and the share of our speed and escape
skills off recharge as the play starts (a split's escapes at a collapse).
Not read here yet (stage X2): what a prot did (R-636); how well a monk spends his energy (R-704); the spike package (R-708).

The faults (stage X4; R-713 to R-715): `deaths` keeps every death of a player with the checked chances his team missed (`flag_cost[rid].deaths`), each
play's record names the deaths that fell inside it for its own players and for the enemy it met (`deaths`), and `say_death` and `say_faults` say them.

Usage:  python3 execution.py <report id> [m:ss]            the execution record of a match's plays (from the second given)
        python3 execution.py attempts <report id> [m:ss]   every kill attempt in sentences
        python3 execution.py deaths <report id> [m:ss]     every death with the checked chances his team missed"""
import bisect, collections, sys
from common import SPIKE_BURST, backline_monk

EXEC_MIN_S = 6              # a play shorter than this has no execution read
HOLD_FIRST_S = 20           # a team held in its base is also read on the first seconds of the hold, against what it then loses (R-621), kept as "first"
# The stretch a play's execution is read on is the whole play, from its start to its end (R-710: "Read it over the whole play"), not its first 20 s.
# Each kill attempt is read to its own outcome in the attempt record (REDESIGN.md "Execution", stage X2), which keeps execution read before the result (R-299).
EXEC_STEP = 2               # who meets whom is read every other second, as the fights are

MEASURES = (
    ("dmg", +1, "damage on their players, hits and degen, a living player a 10 s"),
    ("dmg_v_usual", +1, "the hits in that damage against the usual of the players alive (1.0 is the usual; the usual is of hits)"),
    ("healer_share", 0, "share of that damage on their backline monks (offence or defence: no direction, R-304)"),
    ("focus", 0, "share of that damage on the one player hit most"),
    ("spikes", +1, f"bursts of {SPIKE_BURST[0]} or more on one player inside {SPIKE_BURST[1]:.0f} s, a 10 s"),
    ("interrupts", +1, "interrupts landed, a 10 s"),
    ("interrupts_on_healers", +1, "interrupts landed on their backline monks, a 10 s"),
    ("knockdowns", +1, "knockdowns landed, a 10 s"),
    ("knockdowns_on_casting", +1, "knockdowns landed on a player who was casting, a 10 s"),
    ("disable", +1, "skill-seconds disabled on them (Complicate, Power Lock, Power Block, Blackout), a 10 s"),
    ("castprev", +1, "casts of theirs punished by Shame, Guilt or Diversion, a 10 s"),
    ("degen", +1, "degen landed on their players, health a living player a 10 s (gvg.report's, in the damage above too)"),
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
    ("drain", +1, "energy taken from their players (Energy Surge, Energy Burn, Mind Wrack, Power Leak, Shame, Guilt, Malaise), points a 10 s"),
    ("drain_on_monks", 0, "share of that energy taken from their backline monks (offence or defence: no direction, R-692)"),
    # carried from the old engine's execution nodes (REDESIGN.md "Execution", stage X1; learnednodes.EXPECTED, R-290), so nothing it measured is lost
    ("spike_spread", -1, "how far apart the big hits of a spike landed, seconds, the middle spike (off-timed spikes, R-701)"),
    ("spikes_on_healers", 0, "share of the spikes on their healers (offence or defence: read against the play's job, R-709)"),
    ("dazed_casts", -1, "casts started while Dazed, a 10 s"),
    ("blind_front_secs", +1, "seconds their frontline spent Blind, a 10 s"),
    ("blind_def_secs", +1, "seconds Blind on players who had just hit our healers (defensive Blind), a 10 s"),
    ("strip_right", +1, "share of the strips that took the most valuable enchantment in range"),
    ("strip_value", +1, "worth of the enchantments stripped (their measured output a second), a 10 s"),
    ("hex_right", +1, "share of the hex removals that took the most costly hex in range off our players"),
    ("cripple_secs", +1, "seconds their players spent Crippled, a 10 s (on a flag runner, the control the old run node read)"),
    ("escapes_ready", +1, "share of the speed and escape skills on our bars off recharge as the play starts"),
    # gvg.report's interrupt attempts (R-639; checked against the replays, R-707: 2,006 of 2,011 of its hits are interrupts the replays record)
    ("intr_tried", +1, "targeted interrupts thrown at them, landed or missed, a 10 s (gvg.report's attempts)"),
    ("intr_missed_share", -1, "share of those that missed"),
    ("intr_slow_share", -1, "share of those that missed because the cast finished first (thrown late)"),
    # converting an advantage, the res and giving ground (R-712, R-557), and environment areas (R-314)
    ("spike_kill_share", +1, "share of our spikes on them that killed (the conversion of an advantage into kills)"),
    ("res_tried", 0, "resurrection casts started on our dead, a 10 s"),
    ("res_first_s", -1, "seconds from the start of the play to our first res cast, where a player of ours lay dead at its start"),
    ("res_stopped_share", -1, "share of our res casts interrupted or cancelled"),
    ("ground_back", 0, "how far our group fell back towards our own pit over the first 20 s, game units (negative: it advanced)"),
    ("water_share", +1, "share of our time in the flag stand area spent in its healing water (halls with water labelled: Druid's Isle, R-314)"),
    # target choice against the play's objective (R-702, R-709): blank where the job is neither to kill nor to hold
    ("disrupt_right", +1, "share of our knockdowns and interrupts on the right players for the job (to kill: their backline monks; to hold: their damage dealers)"),
    ("dmg_on_front", -1, "share of our damage on their frontline when the job is to kill (warriors take less and stop only offence, R-702)"),
)


def objective(p):
    """The objective a play's target choice is read against (R-709): "offence" where its job is to kill, "defence" where it is to hold, survive, defend a
    split or be held in base, else None (a flag to get in, NPCs to take, ground: no target is right or wrong by the job alone). Read from the job's words."""
    import re
    j = (p.get("job") or "").strip()
    if p.get("play") == "pinned": return "defence"
    if re.match(r"(Kill|Turn the extra player into a kill|Take NPCs or kills|Concede the boost for kills)", j): return "offence"
    if re.match(r"(Hold|Survive|Delay|No deaths|Lose no player|Reach cover|Keep them busy)", j): return "defence"
    return None
KEYS = tuple(k for k, _, _ in MEASURES)
SIGN = {k: s for k, s, _ in MEASURES}
WORDS = {k: w for k, _, w in MEASURES}


class Exec:
    """One match's events laid out for windows. `side(X, Y, t0, t1)`: what the players X did to the players Y."""

    def __init__(self, M, rid):
        import pressure as PR, eventlayer as EL
        from phases import healer, line
        self.line = line
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
        self.monk = {a for a in m.PL if backline_monk(m, a)}       # the backline monks alone, by their bars (R-698): a healing Ritualist is no monk for energy (R-699)
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
        # Degen is damage too (R-638, R-649): gvg.report's, by the player it credits (degen.py). It counts in the amounts and the shares; a spike is still read
        # from the hits, and so is the damage against the roles' usual until the usual itself takes degen in (eventlayer.py, at the rebuild).
        self.dg, self.dg_npc = [], []
        for tg, v in m.degen().rows.items():
            for u, n, src, _ in v:
                if src not in pl or tg >= len(m.A): continue
                if tg in pl and m.team(tg) != m.team(src): self.dg.append((u, src, tg, n))
                elif m.A[tg].get("npc") and m.A[tg].get("team") not in (None, m.team(src)): self.dg_npc.append((u, src, tg, n))
        for L in (self.dm, self.dm_npc, self.hl_npc, self.dg, self.dg_npc): L.sort(key=lambda x: x[0])
        self._t = {id(L): [x[0] for x in L] for L in (self.dm, self.dm_npc, self.hl_npc, self.dg, self.dg_npc)}
        self.intr = sorted((i[0] / 10, i[1], i[3]) for i in (m.o.get("interrupts") or []) if i[0] is not None and i[1] in pl and i[3] in pl)
        import forensics, energy
        self.F = forensics.Forensics(rid, m)
        self.den = [(t, a, b, e) for t, a, b, _, e, _ in energy.denial(m) if e]      # energy taken by an enemy skill (R-685): (second, by, on, points)
        self.blind = collections.defaultdict(list)             # player -> [(from, to)] Blind on him
        for e in m.o.get("effects") or []:
            if e[2] == "c" and e[7] == "blind" and e[0] is not None and e[5] in pl: self.blind[e[5]].append((e[0] / 10, e[1] / 10 if e[1] is not None else 1e9))
        self.ia = sorted((r[0] / 10, r[2], r[4], r[5], r[6], r[3]) for r in (m.extras().o.get("attempts") or []) if r[0] is not None)   # (second, by, on, hit, read, skill)
        self.crip = collections.defaultdict(list)              # player -> [(from, to)] Crippled
        for e in m.o.get("effects") or []:
            if e[2] == "c" and e[7] == "crippled" and e[0] is not None and e[5] in pl: self.crip[e[5]].append((e[0] / 10, e[1] / 10 if e[1] is not None else 1e9))
        from common import skill_row
        self.speed = {}                                        # player -> [(skill id, recharge)] his speed and escape skills (Increased Movement Speed)
        for a in m.PL:
            L = []
            for sid in m.A[a].get("bar") or []:
                r = skill_row(sid, m.sk(sid)) if sid else None
                if r and "Increased Movement Speed" in (r.get("causes") or []): L.append((sid, float(r.get("recharge") or 0)))
            self.speed[a] = L
        self.cf = collections.defaultdict(list)                # (player, skill) -> the seconds a cast of it finished
        for r in m.o["ev"]:
            if r[0] is not None and r[1] == "cf" and r[2] in pl and len(r) > 4: self.cf[(r[2], r[4])].append(r[0] / 10)
        EL.valued(self.R, self.V)                              # each strip and hex removal against the best it had in range (step 2a)
        self.att = collections.defaultdict(list)               # player -> the seconds he attacked
        for r in m.o["ev"]:
            if r[0] is not None and r[1] == "at" and r[2] in pl: self.att[r[2]].append(r[0] / 10)
        for a in self.att: self.att[a].sort()

    def _cut(self, L, t0, t1):
        T = self._t[id(L)]
        return L[bisect.bisect_left(T, t0):bisect.bisect_left(T, t1)]

    def side(self, X, Y, t0, t1, obj=None):
        """What the players X did to the players Y in [t0, t1): one dict of MEASURES, or None where no player of X is alive in it. obj: the objective of X's
        play (`objective`), for target choice."""
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
        hit_tot = sum(n for v in by_t.values() for _, n in v)
        on = collections.Counter({b: sum(n for _, n in v) for b, v in by_t.items()})      # target -> damage on him, hits and degen
        dg_tot = 0.0
        for t, a, b, n in self._cut(self.dg, t0, t1):
            if a in X and b in Y: on[b] += n; dg_tot += n
        tot = hit_tot + dg_tot
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
        dn = [(b, e) for t, a, b, e in self.den if t0 <= t < t1 and a in X and b in Y]
        dn_tot = sum(e for _, e in dn)
        import statistics
        sp = [r for r in R.get("spikes", ()) if t0 <= r["t"] < t1 and r["team"] == tag and r["target"] in yr]
        cs = [F.casting(a, t0, t1)["measures"] for a in X]
        st_ = [r for r in R.get("strips", ()) if t0 <= r["t"] < t1 and r["team"] == tag and r["by"] in xr]
        st_a = [r for r in st_ if r.get("available")]
        hr = [r for r in R.get("hex_removals", ()) if t0 <= r["t"] < t1 and r["team"] == tag and r["by"] in xr and r.get("available")]
        bl = [b for b in R.get("blinds", ()) if b["team"] == tag and b["target"] in yr]
        esc = [(a, sid, rc) for a in X for sid, rc in self.speed.get(a, ())]
        ready = sum(1 for a, sid, rc in esc if not any(t0 - rc < u <= t0 for u in self.cf.get((a, sid), ())))
        ia = [r for r in self.ia if t0 <= r[0] < t1 and r[1] in X and r[2] in Y]
        ia_miss = [r for r in ia if not r[3]]
        rs = [c for a in X for c in F._by_agent.get(a, ()) if t0 <= c[2] < t1 and c[5] is not None and c[5] in m.PL and c[5] != a
              and m.team(c[5]) == tm and not F.alive(c[5], c[2])]
        dead0 = any(not M.AL[a][min(int(t0), M.T)] for a in M.st.players[tm])
        g0, g1 = [a for a in X if M.AL[a][min(int(t0), M.T)]], [a for a in X if M.AL[a][min(int(t0) + 20, int(t1), M.T)]]
        pit = M.st.geo.pit.get(tm) if hasattr(M.st, "geo") else None
        from state import d as _d
        c0, c1 = (M.st.centroid(g0, int(t0)) if g0 else None), (M.st.centroid(g1, min(int(t0) + 20, int(t1))) if g1 else None)
        wa = self.water_share(X, t0, t1)
        kd_on = [k[2] for k in (m.o.get("knockdowns") or []) if k[0] is not None and t0 * 10 <= k[0] < t1 * 10 and k[1] in X and k[2] in Y]
        dis = kd_on + [b for _, b in intr]
        right = (lambda b: b in self.monk) if obj == "offence" else (lambda b: b not in self.healer) if obj == "defence" else None
        front = {b for b in Y if self.line(m, b) == "frontline"}
        out = {
            "dmg": p10(tot),
            "dmg_v_usual": round(hit_tot / usual, 2) if usual > 0 else None,
            "healer_share": round(sum(n for b, n in on.items() if b in self.healer) / tot, 2) if tot else None,
            "focus": round(max(on.values()) / tot, 2) if tot else None,
            "spikes": g10(spikes),
            "interrupts": g10(len(intr)),
            "interrupts_on_healers": g10(sum(1 for _, b in intr if b in self.healer)),
            "knockdowns": g10(tw["knockdowns"]),
            "knockdowns_on_casting": g10(tw["knockdowns_on_casting"]),
            "disable": g10(tw["disable_skill_secs"]),
            "castprev": g10(tw["castprev_triggered"]),
            "degen": p10(dg_tot),
            "kite": g10(tw["kite_secs"] + tw["prekite_secs"]),
            "baits": g10(tw["baits"]),
            "strips": g10(sum(1 for s in R.get("strips", ()) if t0 <= s["t"] < t1 and s["team"] == tag and s["by"] in xr and s.get("useful"))),
            "strips_wasted": g10(sum(1 for s in R.get("strips_wasted", ()) if t0 <= s["t"] < t1 and s["team"] == tag and s["by"] in xr)),
            "blind_secs": g10(sum(ov(b["t"], b["end"]) for b in R.get("blinds", ()) if b["team"] == tag and b.get("attacker") and b["target"] in yr)),
            "hex_secs": g10(sum(ov(h["t"], h["t"] + (h.get("secs") or 0)) for h in R.get("hexes", ()) if h["team"] == ftag and h["target"] in yr)),
            "hex_removed": g10(sum(1 for h in R.get("hex_removals", ()) if t0 <= h["t"] < t1 and h["team"] == tag and h["by"] in xr and h.get("removed"))),
            "npc_dmg": p10(sum(n for t, a, b, n in self._cut(self.dm_npc, t0, t1) if a in X) + sum(n for t, a, b, n in self._cut(self.dg_npc, t0, t1) if a in X)),
            "npc_heal": g10(sum(n for t, a, b, n in self._cut(self.hl_npc, t0, t1) if a in X)),
            "into_ready": g10(sum(c["into_ready_interrupt"] for c in cs)),
            "blind_attacks": g10(blind_att),
            "off_shield": sd["off_shield_share"] if sd["taken"] > 1 else None,
            "drain": g10(dn_tot),
            "drain_on_monks": round(sum(e for b, e in dn if b in self.monk) / dn_tot, 2) if dn_tot else None,
            "spike_spread": round(statistics.median(r["spread_s"] for r in sp), 2) if sp else None,
            "spikes_on_healers": round(sum(1 for r in sp if r["target_class"] == "healer") / len(sp), 2) if sp else None,
            "dazed_casts": g10(sum(c.get("while_dazed", 0) for c in cs)),
            "blind_front_secs": g10(sum(ov(b["t"], b["end"]) for b in bl if b["target_class"] == "frontline")),
            "blind_def_secs": g10(sum(ov(b["t"], b["end"]) for b in bl if b.get("defensive"))),
            "strip_right": round(sum(1 for r in st_a if r.get("right_target")) / len(st_a), 2) if st_a else None,
            "strip_value": g10(sum(r.get("value") or 0 for r in st_)),
            "hex_right": round(sum(1 for r in hr if r.get("right_hex")) / len(hr), 2) if hr else None,
            "cripple_secs": g10(sum(ov(s0, s1) for b in Y for s0, s1 in self.crip.get(b, ()))),
            "escapes_ready": round(ready / len(esc), 2) if esc else None,
            "spike_kill_share": round(sum(1 for r in sp if r.get("killed")) / len(sp), 2) if sp else None,
            "res_tried": g10(len(rs)),
            "res_first_s": round(min(c[2] for c in rs) - t0, 1) if rs and dead0 else None,
            "res_stopped_share": round(sum(1 for c in rs if c[4] in ("interrupted", "cancelled")) / len(rs), 2) if rs else None,
            "ground_back": round(_d(c1, pit) - _d(c0, pit), 0) * -1 if pit and c0 and c1 else None,
            "water_share": wa,
            "intr_tried": g10(len(ia)),
            "intr_missed_share": round(len(ia_miss) / len(ia), 2) if ia else None,
            "intr_slow_share": round(sum(1 for r in ia_miss if r[4] == "finished") / len(ia), 2) if ia else None,
            "disrupt_right": round(sum(1 for b in dis if right(b)) / len(dis), 2) if right and dis else None,
            "dmg_on_front": round(sum(n for b, n in on.items() if b in front) / tot, 2) if obj == "offence" and tot else None,
        }
        return out

    def water_share(self, X, t0, t1):
        """R-314: of X's player-seconds inside the hall's labelled flag stand area, the share inside a labelled Water area; None where the hall has none."""
        H = self.M.hall
        if H is None or not getattr(H, "labels", None): return None
        water = [l["pts"] for l in H.labels if l.get("kind") == "area" and l.get("type") == "Water"]
        stand = [l["pts"] for l in H.labels if l.get("kind") == "area" and l.get("type") == "Flag stand area"]
        if not water or not stand: return None
        def inside(pt, poly):
            x, y, c = pt[0], pt[1], False
            for i in range(len(poly)):
                (x1, y1), (x2, y2) = poly[i], poly[i - 1]
                if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
            return c
        n = w = 0
        for u in range(int(t0), int(t1), 2):
            for a in X:
                if not self.M.AL[a][min(u, self.M.T)]: continue
                pt = self.M.st.pos(a, u)[0]
                if not pt or not any(inside(pt, s) for s in stand): continue
                n += 1; w += any(inside(pt, s) for s in water)
        return round(w / n, 2) if n else None

    def players(self, p):
        """The players a play's execution is read for, and the enemy players they meet in its window: (X, Y, t0, t1), or None where the play is too short."""
        M, m = self.M, self.m
        tm, t0 = p["tm"], int(p["t0"])
        t1 = min(int(p["t1"]), M.T)                              # the whole play (R-710)
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
        obj = objective(p)
        own = self.side(X, Y, t0, t1, obj)
        if own is None: return None
        out = {"s": t1 - t0, "n": [len(X), len(Y)], "objective": obj, "own": own, "their": self.side(Y, X, t0, t1) if Y else None}
        if p.get("play") == "pinned" and t1 - t0 > HOLD_FIRST_S:          # R-621: the first seconds of a hold read against what the team then loses
            f1 = t0 + HOLD_FIRST_S
            out["first"] = {"s": HOLD_FIRST_S, "own": self.side(X, Y, t0, f1, obj), "their": self.side(Y, X, t0, f1) if Y else None}
        return out


# ------------------------------------------------------------------ the kill attempt (stage X2; R-701, R-703, R-708, R-710, R-711, R-713)
ATT_BEFORE_S = 3            # a strip, pressure on his monks or a prot this long before the spike's first big hit belongs to the attempt (Claude's draft: the window
                            # in which each part counts as "together" is measured in stage X3 from these records, R-708; this only bounds what is kept)
ATT_AFTER_S = 8             # an attempt is read to the target's death, or this long after its first hit where he lives (the old spike reading's 8 s)
from forensics import CHANCE_S, PRESSED, REACT_S, _act   # a monk's chance to prot or heal, when he is busy (R-711) and the time to react (R-716): one reading, in forensics.py
MISSED_KINDS = (            # each kind of missed chance (R-713), the side that missed it, and its words; stage X3 checks each on unseen matches
    ("prot", "defence", "a prot ready on a monk in reach who was not busy, not cast on the target"),
    ("heal", "defence", "a heal ready on a monk in reach with energy, who was not busy, not cast on the target before the outcome"),
    ("interrupt", "defence", "a spike skill cast with an interrupt of ours ready and in range, and it went off"),
    ("strip", "attack", "a prot on the target with a strip of ours ready and in range, and none came"),
    ("pressure", "attack", "an interrupt of ours ready on one of their monks in reach of the target, and none landed on their monks"),
)


# Interrupts that can be thrown on demand at a cast, by what they can stop (from each skill's own text, read once): "spell" (a spell or chant), "attack" or
# "any". Skills that interrupt only on a condition the thrower does not choose at the moment (a critical hit, Burning, a Deep Wound, a condition on the
# target, a hex or stance already up, an area or spirit) are not a chance to interrupt a given cast and are left out.
CONDITIONAL = {"Clumsiness", "Panic", "Keystone Signet", "Spinal Shivers", "Rust", "Maelstrom", "Thunderclap", "Dwarven Battle Stance", "Choking Gas",
               "Wailing Weapon", "Shivers of Dread", "Teinai's Wind", "Critical Chop", "Agonizing Chop", "Disrupting Throw", "Disrupting Accuracy",
               "Warmonger's Weapon", "Dissonance", "Anthem of Disruption", "Lyssa's Haste", "Wandering Eye", "Disrupting Lunge"}
MELEE_R = 250               # an interrupting melee attack reaches this far (adjacent, with a step)


def intr_kind(sd):
    """What an interrupt skill can stop when thrown at a cast: "spell", "attack", "any", or None where it is not thrown on demand (CONDITIONAL)."""
    import re
    name = (sd.get("name") or "").replace(" (PvP)", "")
    if "Interrupt" not in (sd.get("causes") or []) or name in CONDITIONAL: return None
    d = " ".join(x for x in re.split(r"(?<=\.)\s", sd.get("desc") or "") if "nterrupt" in x or "disrupt" in x)
    if re.search(r"casting a spell|spell-casting|cast spells", d): return "spell"
    if re.search(r"is attacking|attacking foe", d): return "attack"
    return "any"


def can_stop(sd_i, sd_c):
    """Can interrupt skill sd_i stop a cast of sd_c?"""
    k = intr_kind(sd_i)
    if k is None: return False
    ty = sd_c.get("type") or ""
    if k == "spell": return "Spell" in ty or "Chant" in ty
    if k == "attack": return "Attack" in ty
    return True


# How long an interrupt takes to land once thrown (R-750): a spell or signet its cast time; an attack skill half its stated activation, or half its weapon's
# swing where it states none (knowledge/attack-timing.md: the hit lands halfway; knowledge/weapons.md for the swings). So Distracting Shot and Savage Shot a
# quarter second: arrow flight is left out for now (his word).
SWING = {"Hammer": 1.75, "Scythe": 1.5, "Spear": 1.5, "Bow": 2.025}       # every other attack 1.33 (axe, sword, daggers)


def intr_time(sd):
    ty, a = sd.get("type") or "", _act(sd.get("activation"))
    if "Attack" in ty: return (a or next((v for k, v in SWING.items() if k in ty), 1.33)) / 2
    return a


_WORTH = {}


def worth(side):
    """The skills worth interrupting (R-727; `data/model/interrupt_worth.json`, approved by Denning, the words in main's docs/EXECUTION.md): the names on one
    side of the list ("defensive": interrupts that help us live; "offensive": that help us kill; "flag": snares on our runner). A missing file stops the reading (R-460)."""
    if not _WORTH:
        import json, os
        here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        d = json.load(open(os.path.join(here, "data", "model", "interrupt_worth.json"), encoding="utf-8"))
        for k in ("offensive", "flag", "defensive"): _WORTH[k] = frozenset(n for L in d[k].values() for n in L)
    return _WORTH[side]


def intr_range(F, f, sd, t):
    from common import CAST_R
    ty = sd.get("type") or ""
    if "Bow" in ty: return F.bow_range(f, t)
    if "Attack" in ty and "Spear" not in ty: return MELEE_R
    return CAST_R


def _role_skills(F, a, test):
    return [(sid, F.sdata(sid)) for sid in (F.m.A[a].get("bar") or []) if sid and test(F.sdata(sid))]


def _ready(F, a, sid, sd, t, hands=True): return F.ready(a, sid, sd, t, hands)       # the one reading: forensics.Forensics.ready


def attempts(E):
    """Every spike of both teams (`events._spikes`: 400 or more on one player inside 3 s) as a kill attempt, read to its own outcome (R-710): the package
    (R-708: how its big hits landed, the strip on the target, pressure on the target's monks) and the chances each side missed (R-713). A record: no play reads it."""
    import events as EV
    from common import CAST_R
    F, m = E.F, E.m
    F.casts()
    En = m.energy()
    kill_w, deaths = {}, collections.defaultdict(list)
    for e in F.ev:
        if e[1] == "dt" and e[0] / 10 < E.M.over: deaths[e[2]].append(e[0] / 10)      # the losing team recorded dying all at once as the match ends is no kill (Moments.over)
    from forensics import is_prot, is_heal
    is_strip = lambda sd: "Enchantment" in (sd.get("removes") or [])
    is_intr = lambda sd: intr_kind(sd) is not None
    out = []
    for tm in (1, 2):
        mine, theirs = F.players(tm), F.players(3 - tm)
        for t, tgt, dmg, win, died in EV._spikes(F, tm):
            end = next((d for d in deaths[tgt] if t <= d <= t + ATT_AFTER_S), t + ATT_AFTER_S)
            ld = EV._landing(win)
            first = ([x for x in win if x[3] >= 60] or win)[0][0]
            att = sorted({x[1] for x in win})
            near = lambda a, u: (F.dist(a, tgt, u) or 1e9) <= CAST_R
            # the package (R-708)
            strips = [r for r in E.R.get("strips", ()) if r["team"] == m.tag[tm] and r["target"] == m.roles[tgt] and first - ATT_BEFORE_S <= r["t"] <= end]
            monks = [h for h in theirs if h in E.monk]
            pr_i = [(i[0] / 10) for i in (m.o.get("interrupts") or []) if i[0] is not None and i[3] in monks and i[1] in mine and first - ATT_BEFORE_S <= i[0] / 10 <= end]
            pr_k = [k[0] for h in monks for k in F.kds_on(h, first - ATT_BEFORE_S, end)]
            pr_d = [h for h in monks if F.has(h, "c", "dazed", first)]
            prots_up = [F.sname(e[3]) for e in m.o.get("effects") or [] if e[2] == "e" and e[5] == tgt and e[0] is not None and e[0] <= first * 10
                        and (e[1] is None or e[1] >= first * 10) and is_prot(F.sdata(e[3]))]
            on_tgt = [c for h in theirs for c in F._by_agent.get(h, ()) if c[5] == tgt and first - ATT_BEFORE_S <= c[2] <= end]
            prot_cast = [c for c in on_tgt if is_prot(F.sdata(c[1]))]
            heal_cast = [c for c in on_tgt if is_heal(F.sdata(c[1]))]
            missed = []
            # defence: prots and heals (R-703, R-711), read at the first big hit; the monk's energy from gvg.report (out under 20, R-681: no chance)
            # A chance needs time to act (forensics.Forensics.chances, the one reading for attempts and deaths): "not healed" is never true merely because
            # he died at once; busy on a player under pressure (R-711) and out of energy (R-681) are no chance.
            missed += F.chances(tgt, first, end, {"prot": is_prot, "heal": is_heal}, monks=monks)
            # defence: interrupts on the spike's skills. Only a skill worth interrupting (R-727), by an interrupt that can stop that kind of skill, where the
            # cast took at least the time to react and the interrupt's own time to land (R-742, R-750: how long it took is the replay's own record of the
            # cast, so a half-cast spell, a Mesmer's fast cast and an attack skill's hit halfway through a quickened swing are read as they were), and the
            # interrupter could act once he had seen it (off recharge, hands free, his own aftercast over: R-716, the clock from the cast's start, R-748).
            sp_casts = [c for a in att for c in F._by_agent.get(a, ()) if c[5] == tgt and first - ATT_BEFORE_S <= c[2] <= end and c[1] is not None]
            for c in sp_casts:
                sd_c = F.sdata(c[1])
                if (sd_c.get("name") or "").replace(" (PvP)", "") not in worth("defensive"): continue
                took, u = (c[3] - c[2] if c[3] is not None else None), c[2] + REACT_S
                ready = [f"{F.name(f)} {F.sname(sid)}" for f in theirs for sid, sd in _role_skills(F, f, is_intr)
                         if can_stop(sd, sd_c) and took is not None and took + 1e-6 >= REACT_S + intr_time(sd)
                         and (F.dist(f, c[0], u) or 1e9) <= intr_range(F, f, sd, u) and _ready(F, f, sid, sd, u) and not F.in_aftercast(f, u)]
                tried = [r for r in E.ia if r[2] == c[0] and r[1] in theirs and c[2] - 0.5 <= r[0] <= (c[3] or c[2] + 1)]
                at = round(c[2] - first, 1)          # when the spike skill's cast started, from the first big hit (X3 compares taken and missed over the same seconds)
                if c[4] == "interrupted": missed.append({"kind": "interrupt", "side": "defence", "taken": True, "skill": F.sname(c[1]), "at": at, "chance": False})
                elif tried: missed.append({"kind": "interrupt", "side": "defence", "skill": F.sname(c[1]), "by": [F.name(r[1]) + " " + F.sname(r[5]) for r in tried][:3],
                                           "tried": [r[4] for r in tried], "at": at, "chance": True})        # thrown and missed: a chance not taken all the same, with gvg.report's read of why
                elif ready and c[4] == "finished": missed.append({"kind": "interrupt", "side": "defence", "skill": F.sname(c[1]), "by": ready[:3], "at": at, "chance": True})
            # attack: a strip on a prot, pressure on their monks
            if prots_up and not strips:
                ready = [f"{F.name(a)} {F.sname(sid)}" for a in mine for sid, sd in _role_skills(F, a, is_strip) if near(a, first) and _ready(F, a, sid, sd, first)]
                if ready: missed.append({"kind": "strip", "side": "attack", "by": ready[:3], "prots": prots_up, "chance": True})
            if not pr_i:
                ready = [f"{F.name(a)} {F.sname(sid)} on {F.name(h)}" for a in mine for sid, sd in _role_skills(F, a, lambda x: intr_kind(x) in ("spell", "any")) for h in monks
                         if near(h, first) and (F.dist(a, h, first) or 1e9) <= intr_range(F, a, sd, first) and _ready(F, a, sid, sd, first)]
                if ready: missed.append({"kind": "pressure", "side": "attack", "by": ready[:3], "chance": True})
            # what the old kill conversion node read (knowledge/model.md, "kill conversion"), at the first big hit: state of the target, never a fault
            from state import d as _d
            S_ = E.M.st
            pos = S_.pos(tgt, int(first))[0]
            mg = S_.main_group(3 - tm, int(first)); cen = S_.centroid(mg, int(first)) if mg else None
            hp = (m.snap(tgt, round(first * 10)) or {}).get("hp")
            target_state = {"health_pct": hp, "ceiling": round(1 + S_.morale(tgt, first) / 100, 2),
                            "healers_in_range": sum(1 for h in theirs if h != tgt and h in E.healer and F.alive(h, first) and near(h, first)),
                            "hexes": sum(1 for e in m.o.get("effects") or [] if e[2] == "h" and e[5] == tgt and e[0] is not None and e[0] <= first * 10 and (e[1] is None or e[1] >= first * 10)),
                            "from_group": round(_d(pos, cen)) if pos and cen and tgt not in mg else 0}
            out.append({"t": round(first, 1), "tm": tm, "team": m.tag[tm], "target": m.roles[tgt], "state": target_state, "target_class": "healer" if tgt in E.healer else "other",
                        "dmg": round(dmg), "killed": bool(died and end < t + ATT_AFTER_S), "s": round(end - first, 1), "attackers": [m.roles[a] for a in att],
                        "spread": ld["spread_s"], "in_1s": ld["in_1s"],
                        "strip": {"n": len(strips), "lead": round(min(r["t"] for r in strips) - first, 1) if strips else None, "prot_off": any(r.get("prot") for r in strips),
                                  "at": sorted([round(r["t"] - first, 1), bool(r.get("prot"))] for r in strips)},
                        "pressure": {"interrupts": len(pr_i), "knockdowns": len(pr_k), "dazed": len(pr_d),
                                     "lead": round(min(pr_i + pr_k) - first, 1) if pr_i or pr_k else None,
                                     "interrupts_at": sorted(round(x - first, 1) for x in pr_i), "knockdowns_at": sorted(round(x - first, 1) for x in pr_k)},
                        "prots_up": prots_up, "prots_cast": [[F.sname(c[1]), round(c[2] - first, 1), c[4]] for c in prot_cast],
                        "heals_cast": [[F.sname(c[1]), round(c[2] - first, 1), c[4]] for c in heal_cast],
                        "missed": missed})
    return sorted(out, key=lambda r: r["t"])


def say_attempt(r):
    """A kill attempt in sentences (R-329): what landed together, and every missed chance of both sides, none ranked (R-713)."""
    clk = lambda t: f"{int(t // 60)}:{int(t % 60):02d}"
    foe = "their" if r["tm"] else ""
    L = [f"{clk(r['t'])} {r['team']} spike on the {r['target']} ({', '.join(r['attackers'])}): {r['dmg']} in 3 s, "
         + ("killed him" if r["killed"] else "he lived") + f" (read over {r['s']} s)."]
    L.append(f"Big hits landed over {r['spread']} s ({100 * r['in_1s']:.0f}% of the damage in the first second).")
    st = r["strip"]
    L.append("No strip on him." if not st["n"] else f"{st['n']} strip(s) on him, the first {abs(st['lead'])} s {'before' if st['lead'] < 0 else 'after'} the first big hit"
             + (", a prot taken off." if st["prot_off"] else "."))
    p_ = r["pressure"]
    L.append("No pressure on his monks." if not (p_["interrupts"] or p_["knockdowns"] or p_["dazed"]) else
             f"Pressure on his monks: {p_['interrupts']} interrupt(s), {p_['knockdowns']} knockdown(s), {p_['dazed']} Dazed at the first hit"
             + (f", the first {abs(p_['lead'])} s {'before' if p_['lead'] < 0 else 'after'} it." if p_["lead"] is not None else "."))
    z = r.get("state") or {}
    if z: L.append(f"He stood at {z['health_pct']}% health, his maximum {100 * z['ceiling']:.0f}% of normal, {z['healers_in_range']} healer(s) of his in range, "
                   f"{z['hexes']} hex(es) on him" + (f", {z['from_group']} from his main group." if z["from_group"] else ", with his main group."))
    if r["prots_up"]: L.append(f"Prots on him at the first hit: {', '.join(r['prots_up'])}.")
    if r["prots_cast"] or r["heals_cast"]:
        L.append("Cast on him: " + "; ".join(f"{n} {abs(d)} s {'before' if d < 0 else 'after'} ({o})" for n, d, o in r["prots_cast"] + r["heals_cast"]) + ".")
    ch = [x for x in r["missed"] if x.get("chance")]
    for x in ch:
        who = x["by"] if isinstance(x["by"], str) else "; ".join(x["by"])
        if x["kind"] == "interrupt" and x.get("tried"):
            L.append(f"Missed by the defence: {x['skill']} went off; an interrupt was thrown at it and missed ({who}; gvg.report's read: {', '.join(str(r) for r in x['tried'])}).")
        elif x["kind"] == "interrupt": L.append(f"Missed by the defence: {x['skill']} went off with an interrupt ready ({who}).")
        elif x["kind"] in ("prot", "heal"): L.append(f"Missed by the defence: {who} had {', '.join(x['skills'])} ready, not cast on him.")
        elif x["kind"] == "strip": L.append(f"Missed by the attack: prot(s) up ({', '.join(x['prots'])}) and a strip ready ({who}), none came.")
        elif x["kind"] == "pressure": L.append(f"Missed by the attack: an interrupt ready on his monks ({who}), none landed.")
    for x in r["missed"]:
        if x.get("busy_on"): L.append(f"Not a chance: {x['by']} was busy on {x['busy_on']} (R-711).")
        elif x.get("out_of_energy"): L.append(f"Not a chance: {x['by']} was out of energy (R-681).")
        elif x.get("spiked"): L.append(f"Not a chance: {x['by']} was himself under a spike (R-747).")
    return " ".join(L)


# ------------------------------------------------------------------ the faults said on a death and on a play (stage X4; R-713, R-714, R-715)
FAULT_KINDS = ("prot", "heal", "interrupt")      # the kinds of missed chance stage X3 passed on unseen matches (`cases.py attempts` section G, which stops with an error
                                                 # when its verdicts and this line differ): a strip missed by the attack reads backwards and pressure on the target's
                                                 # monks shows no difference, so neither is ever told as a fault (R-285). All three are the defence's, so by R-714 a
                                                 # fault is listed only where a player died: on a spike that killed, and in the death accounts.


def chance_tests():
    """Each kind of missed chance as (taken, missed, late), each a test on a kill attempt, all read over the same seconds (from 3 s before the first big hit to
    CHANCE_S after it, the seconds a monk's chance is looked for): a spike that kills ends at the death and one that fails is read for 8 s, so anything counted
    to the end of the attempt piles up on the spikes that failed. Taken by anyone in time is taken (R-715). Late: done, but only after those seconds (out of
    time, R-713). The one reading of taken and missed: stage X3's test (`cases.py`) and the faults listed (`deaths`) both use it."""
    CH = CHANCE_S
    ints = lambda r: [x for x in r["missed"] if x["kind"] == "interrupt" and x.get("at", 0) <= CH]
    out = {}
    for kind, key in (("prot", "prots_cast"), ("heal", "heals_cast")):
        tk = (lambda key: lambda r: any(d <= CH for _, d, _o in r[key]))(key)
        has = (lambda kind: lambda r: any(x["kind"] == kind and x.get("chance") for x in r["missed"]))(kind)
        out[kind] = (tk, (lambda tk, has: lambda r: has(r) and not tk(r))(tk, has), lambda r: False)
    mi = lambda r: any(x.get("chance") for x in ints(r))
    out["interrupt"] = (lambda r: any(x.get("taken") for x in ints(r)) and not mi(r), mi, lambda r: False)
    st = lambda r: bool(r["prots_up"]) and any(prot and a <= CH for a, prot in r["strip"].get("at", []))
    out["strip"] = (st, lambda r: not st(r) and any(x["kind"] == "strip" and x.get("chance") for x in r["missed"]),
                    lambda r: bool(r["prots_up"]) and r["strip"]["n"] > 0 and not st(r))
    pt = lambda r: any(a <= CH for a in r["pressure"].get("interrupts_at", []))
    out["pressure"] = (pt, lambda r: not pt(r) and any(x["kind"] == "pressure" and x.get("chance") for x in r["missed"]),
                       lambda r: r["pressure"]["interrupts"] > 0 and not pt(r))
    return out


def deaths(E, atts):
    """Every death of a player with the checked chances his team missed (stage X4; kept beside the plays as `flag_cost[rid].deaths`, no play reads it). A fault
    is a missed chance of a kind stage X3 passed (FAULT_KINDS), none priced or ranked (R-713), and all are the defence's, so they are listed where a player
    died (R-714): on the spike that killed him, read from its kill attempt (a prot, a heal, an interrupt on a spike skill), and on a death with no spike
    (under 400 on him inside 3 s: pressure on a player already low), read as the death account reads it, from the start of the burst that killed him (a prot,
    a heal; the interrupt chance is defined on a spike's skills). A kind a team mate took in time is no fault and is not listed against the player who held
    back (R-715). The record holds what was there; its words are `say_death`. Beside the faults, what was no chance: a monk busy on a player under pressure (R-711) or out of energy (R-681). The deaths recorded as
    the match ends are none (`Moments.over`)."""
    from forensics import is_prot, is_heal
    F, m, T = E.F, E.m, chance_tests()
    F.casts()
    pl, out = set(m.PL), []
    names = sorted((F.name(a) for a in pl), key=len, reverse=True)
    who_what = lambda s_: next(([n, s_[len(n) + 1:]] for n in names if s_.startswith(n + " ")), [s_, ""])      # "tag role skill" as [player, skill]: the attempt record keeps one string
    for e in F.ev:
        if e[1] != "dt" or e[0] is None or e[2] not in pl: continue
        a, td = e[2], e[0] / 10
        tm = m.team(a)
        if tm not in (1, 2) or td >= E.M.over: continue           # the losing team recorded dying all at once as the match ends is no death to account for (Moments.over)
        r = max((r for r in atts if r["killed"] and r["tm"] == 3 - tm and r["target"] == m.roles[a] and abs(r["t"] + r["s"] - td) <= 0.3), key=lambda r: r["t"], default=None)
        d = {"t": round(td, 1), "id": a, "tm": tm, "team": m.tag[tm], "who": m.roles[a], "by": m.tag[3 - tm], "spike": r is not None}
        faults, taken = [], []
        if r is not None:
            d.update(first=r["t"], dmg=r["dmg"], attackers=r["attackers"], spread=r["spread"])
            for kind in ("prot", "heal"):
                if kind not in FAULT_KINDS: continue
                tk, mi, _ = T[kind]
                if tk(r): taken.append(kind)
                elif mi(r): faults += [{"kind": kind, "by": x["by"], "skills": x["skills"], "at": x["at"]} for x in r["missed"] if x["kind"] == kind and x.get("chance")]
            if "interrupt" in FAULT_KINDS:
                for x in r["missed"]:
                    if x["kind"] != "interrupt" or x.get("at", 0) > CHANCE_S: continue
                    if x.get("taken"): taken.append("interrupt")
                    elif x.get("chance"): faults.append({"kind": "interrupt", "skill": x["skill"], "by": [who_what(b_) for b_ in x["by"]], "at": x["at"], **({"tried": x["tried"]} if x.get("tried") else {})})
            other = [x for x in r["missed"] if x.get("busy_on") or x.get("out_of_energy") or x.get("spiked")]
        else:
            bt = F.killing_burst(a, td)
            d.update(first=round(bt, 1), dmg=round(sum(x[3] for x in F.damage_on(a, bt, td))), attackers=sorted({m.roles[x[1]] for x in F.damage_on(a, bt, td) if x[1] in pl}))
            kinds = {k: f for k, f in (("prot", is_prot), ("heal", is_heal)) if k in FAULT_KINDS}
            ch = F.chances(a, bt, td, kinds)
            taken = F.taken_in_time(a, bt, kinds)
            faults = [{"kind": c["kind"], "by": c["by"], "skills": c["skills"], "at": c["at"]} for c in ch if c["chance"] and c["kind"] not in taken]
            other = [c for c in ch if c.get("busy_on") or c.get("out_of_energy") or c.get("spiked")]
        d["faults"] = faults
        d["taken"] = sorted(set(taken))
        d["no_chance"] = [{"kind": x["kind"], "by": x["by"], **({"busy_on": x["busy_on"]} if x.get("busy_on") else {"spiked": True} if x.get("spiked") else {"out_of_energy": True})}
                          for x in other if x["kind"] in FAULT_KINDS]
        out.append(d)
    return sorted(out, key=lambda d: d["t"])


FAULT_SAY = {"prot": "a prot", "heal": "a heal", "interrupt": "an interrupt on a spike skill"}


def say_death(d): return " ".join(death_lines(d))


def death_lines(d):
    """A death in sentences (R-329), one a line: what killed him, then every checked chance his team missed with what was there (the skill ready, the monk in
    reach), none ranked (R-713), then what was no chance (R-711, R-681). Times are match times, as on the replay."""
    clk = lambda t: f"{int(t // 60)}:{int(t % 60):02d}"
    nm = lambda s_: s_.replace(" PvP", "")
    mine = lambda s_: nm(s_[len(d["team"]) + 1:] if s_.startswith(d["team"] + " ") else s_)      # a team mate is said by his role alone
    who = (", ".join(d["attackers"]) or "nobody recorded")
    if d["spike"]: L = [f"{clk(d['t'])} {d['team']}'s {d['who']} dies to a spike by {d['by']} ({who}): {d['dmg']} in 3 s, the first big hit at {clk(d['first'])}, the big hits over {d['spread']} s."]
    else: L = [f"{clk(d['t'])} {d['team']}'s {d['who']} dies with no spike on him (under 400 inside 3 s): {d['dmg']} from {d['by']} ({who}) between {clk(d['first'])}, the start of the heaviest 2 s on him, and his death."]
    for kind in ("prot", "heal"):
        X = [x for x in d["faults"] if x["kind"] == kind]
        if X: L.append(f"Missed by {d['team']}, {FAULT_SAY[kind]}: " + "; ".join(f"{mine(x['by'])} had {', '.join(nm(k) for k in x['skills'])} ready, in reach, his hands free" for x in X) + "; not cast on him in the time he had to see the hit and cast (R-716).")
    X = [x for x in d["faults"] if x["kind"] == "interrupt"]
    if X:                                                  # the spike's skills that went off, then the interrupts that were ready for them, each said once: one interrupt stops one skill
        went, held = collections.Counter(nm(x["skill"]) for x in X), collections.OrderedDict()
        for x in X:
            for who_, what in x["by"]:
                if nm(what) not in held.setdefault(mine(who_), []): held[mine(who_)].append(nm(what))
        tried = [f"{'; '.join(mine(w) + ' with ' + nm(v) for w, v in x['by'])} at {nm(x['skill'])} (gvg.report's read: {', '.join(str(v) for v in x['tried'])})" for x in X if x.get("tried")]
        n_i = sum(len(v) for v in held.values())
        L.append(f"Missed by {d['team']}, {FAULT_SAY['interrupt']}: {len(X)} of the spike's skills went off ({', '.join(k + (f' {v} times' if v > 1 else '') for k, v in went.items())}) with "
                 + f"{n_i} interrupt{'s' if n_i != 1 else ''} ready and in range: " + "; ".join(f"{w} had {', '.join(v)}" for w, v in held.items()) + "."
                 + (" Thrown and missed: " + "; ".join(tried) + "." if tried else ""))
    if not d["faults"]: L.append(f"No checked chance missed by {d['team']}" + (" (a prot, a heal or an interrupt on a spike skill)." if d["spike"] else " (a prot or a heal; with no spike there is no spike skill to interrupt)."))
    if d["taken"]: L.append("Done in time by a team mate, so no fault (R-715): " + ", ".join(FAULT_SAY[k] for k in d["taken"]) + ".")
    for x in d["no_chance"]:
        L.append(f"Not a chance ({FAULT_SAY[x['kind']]}): {mine(x['by'])} was busy on {mine(x['busy_on'])}, who was under pressure (R-711)." if x.get("busy_on")
                 else f"Not a chance ({FAULT_SAY[x['kind']]}): {mine(x['by'])} was himself under a spike (R-747)." if x.get("spiked")
                 else f"Not a chance ({FAULT_SAY[x['kind']]}): {mine(x['by'])} was out of energy (R-681).")
    return L


def say_faults(p, x, D, teams):
    """The faults of a play in sentences (stage X4): the deaths of the team making the play with the checked chances it missed, then the enemy's apart (scored
    the same way, never a fix, R-299), each with its replay time; then the two measures that come close to the outcome itself, said as context and never as a
    fault (`spike_kill_share`, `dmg`). x is the play's execution record, D the match's deaths (`deaths`). None where the play has no record."""
    if x is None or "deaths" not in x: return None
    foe = next((t for t in teams if t != p["team"]), "the enemy")
    def side(sd, name):
        L = [D[i] for i in x["deaths"][sd]]
        if not L: return f"{name}: nobody of its players in this play died, so no fault is listed (R-714)."
        n = sum(len(d["faults"]) for d in L)
        return f"{name}: {len(L)} death{'s' if len(L) != 1 else ''}, {n} missed chance{'s' if n != 1 else ''}. " + " ".join(say_death(d) for d in L)
    ctx = []
    for sd, name in (("own", p["team"]), ("their", foe)):
        v = x.get(sd)
        if not v: continue
        k, dm = v.get("spike_kill_share"), v.get("dmg")
        ctx.append(f"{name} " + ("made no spike" if k is None else f"killed with {100 * k:.0f}% of its spikes") + ("" if dm is None else f" and did {dm:.0f} damage a living player a 10 s"))
    return (side("own", p["team"]) + " Apart, the enemy it met (never a fix, R-299): " + side("their", foe)
            + (" Context, not a fault: " + "; ".join(ctx) + "." if ctx else ""))


def record(M, rid, plays, E=None, D=None):
    """{play id: its execution record} for the plays of one match (kept beside the plays; no play reads it). With the match's deaths (`deaths`), each record
    carries `deaths`: for the play's own players and for the enemy players it met, which deaths fell inside the play (their places in the deaths record), so
    the faults are said on the play (stage X4)."""
    E, out = E or Exec(M, rid), {}
    for p in plays:
        r = E.play(p)
        if r is None: continue
        if D is not None:
            X, Y, t0, t1 = E.players(p)
            r["deaths"] = {"own": [i for i, d in enumerate(D) if d["id"] in X and t0 <= d["t"] <= t1], "their": [i for i, d in enumerate(D) if d["id"] in Y and t0 <= d["t"] <= t1]}
        out[p["id"]] = r
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit()
    from replaylib import Match
    from state import GameState
    if a[0] == "deaths":                                  # python3 execution.py deaths <report id> [m:ss]: every death with the checked chances missed (stage X4)
        import moments
        from scoreboard import Scoreboard
        st = GameState(Match.from_branch(a[1])); M = moments.Moments(st, Scoreboard(st))
        frm = (lambda s: int(s.split(":")[0]) * 60 + int(s.split(":")[1]))(a[2]) if len(a) > 2 else 0
        E_ = Exec(M, a[1])
        for d in deaths(E_, attempts(E_)):
            if d["t"] >= frm: print(say_death(d) + "\n")
        sys.exit()
    if a[0] == "attempts":                                # python3 execution.py attempts <report id> [m:ss]
        import moments
        from scoreboard import Scoreboard
        st = GameState(Match.from_branch(a[1])); M = moments.Moments(st, Scoreboard(st))
        frm = (lambda s: int(s.split(":")[0]) * 60 + int(s.split(":")[1]))(a[2]) if len(a) > 2 else 0
        for r in attempts(Exec(M, a[1])):
            if r["t"] < frm: continue
            print(say_attempt(r))
        sys.exit()
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
        print(f"\n{p['t0'] // 60}:{p['t0'] % 60:02d} {p['play']} ({p['team']}), {r['n'][0]} against {r['n'][1]}, over {r['s']} s: {p['scenario'][:110]}")
        for k in KEYS:
            o, t = r["own"].get(k), (r["their"] or {}).get(k)
            if o or t: print(f"    {k:22} own {'' if o is None else o:>7}   their {'' if t is None else t:>7}   {WORDS[k]}")
