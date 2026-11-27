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

The sum (the catalogue's stage 4; R-734): every kill attempt carries its `ledger`, each part of "a death is a sum" a measured amount (health at the start,
what landed by kind, what was healed, health at the end, what the parts leave over; what was stopped before it landed from gvg.report's recap), and every
missed chance what it would have stopped or added. `pressure` keeps the pressure attempts beside the spikes (R-741, R-749: a player kept in danger for a
while; it reads every death with no spike, in place of the heaviest 2 s). Each play's record names the attempts made inside it, so question 3 is read
attempt by attempt (R-732, `say_q3`), with the enemy's credit apart (R-733). `even_rows` keeps the even 8v8's execution-only rows (R-731).

Usage:  python3 execution.py <report id> [m:ss]            the execution record of a match's plays (from the second given)
        python3 execution.py attempts <report id> [m:ss]   every kill attempt in sentences
        python3 execution.py pressure <report id> [m:ss]   every pressure attempt in sentences
        python3 execution.py even <report id> [m:ss]       the even 8v8s' rows: both teams read as trying to kill (question 3)
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
    ("into_ready", -1, "casts of a skill worth interrupting by a backline monk, started with an enemy interrupt ready and in range, and interrupted, a 10 s (R-743)"),
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
        self.hl = collections.defaultdict(list)                # player -> [(second, healer, amount)] healing that landed on him
        for r in m.o["ev"]:
            if r[0] is not None and r[1] == "hl" and r[3] in pl and len(r) > 5 and isinstance(r[5], (int, float)) and r[5] > 0: self.hl[r[3]].append((r[0] / 10, r[2], r[5]))
        for a in self.hl: self.hl[a].sort(key=lambda x: x[0])
        self.recaps = [r for r in (m.extras().o.get("recaps") or []) if r.get("who") in pl and r.get("t") is not None]      # gvg.report's recaps of deaths and survived spikes (R-636)
        self._per = None

    def per_use(self, a, sid):
        """What a cast of skill sid gave player a on average this match, by gvg.report's summary (R-734: the amount beside a missed chance, measured, not
        priced): {"casts", "healing", "stopped", "damage"} a cast, or None where he never cast it. A monk's healing and prevention from the file beside
        the replay as `casting.py` reads it (Divine Favor in, overhealing out); a skill's damage from the match summary (`data/matches`: checked against the
        replays' own hits, R-707, on 14 matches: a player's total is the replay's, median ratio 1.00, and the skills hold a median 55% of it, the rest
        plain attacks). Aegis, Protective Spirit and Aura of Stability stop nothing in gvg.report's figures (R-704 c): `unmeasured`, never a nought."""
        if self._per is None:
            import casting, eventlayer as EL
            self._per = {}
            for h, row in casting.record(self.m, self.rid)["monks"].items():
                for nm, n, _e, healed, _o, prevented, _b in row["skills"]:
                    if n: self._per[(int(h), nm)] = {"casts": n, "healing": round(healed / n), "stopped": round(prevented / n), **({"unmeasured": True} if nm in casting.APART else {})}
            by_name = {p.get("n"): p for p in EL._match_players(self.rid)}
            for a_ in self.m.PL:
                for k, v in ((by_name.get(self.m.A[a_].get("n")) or {}).get("sk") or {}).items():
                    if v and v[0] and v[1]: self._per.setdefault((a_, self.F.sname(int(k))), {"casts": v[0]})["damage"] = round(v[1] / v[0])
        return self._per.get((a, self.F.sname(sid) if isinstance(sid, int) else sid))

    def caught(self):
        """The match's casts into a ready interrupt as R-743 counts them (`caught`), read once."""
        if getattr(self, "_caught", None) is None: self._caught = caught(self)
        return self._caught

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
            "into_ready": g10(sum(1 for c in self.caught() if c["id"] in X and t0 <= c["t"] < t1)),       # R-743: only an interrupted cast of a listed skill by a backline monk (`caught`)
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
from forensics import CHANCE_S, PRESSED, REACT_S, DEEP_WOUND_SHARE, DEEP_WOUND_MAX, DANGER_HP, _act   # a monk's chance to prot or heal, when he is busy (R-711) and the time to react (R-716): one reading, in forensics.py
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


_TAGS = {}


def tags():
    """The skill tags (`data/model/skill_tags.json`: what each skill in use does to the sum of a death, reviewed by Denning, R-753 to R-765), by the skill's
    name without " (PvP)". A missing file stops the reading (R-460). A skill not in it is untagged: never read as doing nothing (R-767)."""
    if not _TAGS:
        import json, os
        here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        for v in json.load(open(os.path.join(here, "data", "model", "skill_tags.json"), encoding="utf-8"))["skills"].values(): _TAGS[v["name"]] = v
    return _TAGS


def is_strip(sd):
    """Can this skill take an enchantment off a foe? The skill data lists what a skill removes without saying from whom, so a Dervish skill that spends one
    of its user's own enchantments (Wearying Strike, Pious Assault, Signet of Pious Restraint) read as a strip; the reviewed tags say which removals are
    strips, and a tagged skill is read from them. An untagged skill is read from the skill data as before."""
    if "Enchantment" not in (sd.get("removes") or []): return False
    t = tags().get((sd.get("name") or "").replace(" (PvP)", ""))
    return t is None or "enchantments" in t["removes"]


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
                if c[4] == "interrupted": missed.append({"kind": "interrupt", "side": "defence", "taken": True, "skill": F.sname(c[1]), "caster": c[0], "at": at, "chance": False})
                elif tried: missed.append({"kind": "interrupt", "side": "defence", "skill": F.sname(c[1]), "caster": c[0], "by": [F.name(r[1]) + " " + F.sname(r[5]) for r in tried][:3],
                                           "tried": [r[4] for r in tried], "at": at, "chance": True})        # thrown and missed: a chance not taken all the same, with gvg.report's read of why
                elif ready and c[4] == "finished": missed.append({"kind": "interrupt", "side": "defence", "skill": F.sname(c[1]), "caster": c[0], "by": ready[:3], "at": at, "chance": True})
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
            # the sum (R-734): each part a measured amount, from the spike's first hit to its outcome; and beside each missed chance what it would have stopped or added
            led = ledger(E, tgt, t, end, bool(died and end < t + ATT_AFTER_S), first)
            for x in missed:
                _amounts(E, x)
                if x["kind"] == "strip" and led.get("stopped") is not None:
                    up = {k.replace(" PvP", "") for k in prots_up}
                    x["amount"] = sum(b[2] for b in led["stopped"]["by"] if b[1] and b[1].replace(" PvP", "") in up)
            out.append({"t": round(first, 1), "tm": tm, "team": m.tag[tm], "target": m.roles[tgt], "id": tgt, "kind": "spike", "state": target_state, "target_class": "healer" if tgt in E.healer else "other",
                        "dmg": round(dmg), "killed": bool(died and end < t + ATT_AFTER_S), "s": round(end - first, 1), "attackers": [m.roles[a] for a in att],
                        "spread": ld["spread_s"], "in_1s": ld["in_1s"],
                        "strip": {"n": len(strips), "lead": round(min(r["t"] for r in strips) - first, 1) if strips else None, "prot_off": any(r.get("prot") for r in strips),
                                  "at": sorted([round(r["t"] - first, 1), bool(r.get("prot"))] for r in strips)},
                        "pressure": {"interrupts": len(pr_i), "knockdowns": len(pr_k), "dazed": len(pr_d),
                                     "lead": round(min(pr_i + pr_k) - first, 1) if pr_i or pr_k else None,
                                     "interrupts_at": sorted(round(x - first, 1) for x in pr_i), "knockdowns_at": sorted(round(x - first, 1) for x in pr_k)},
                        "prots_up": prots_up, "prots_cast": [[F.sname(c[1]), round(c[2] - first, 1), c[4]] for c in prot_cast],
                        "heals_cast": [[F.sname(c[1]), round(c[2] - first, 1), c[4]] for c in heal_cast],
                        "missed": missed, "ledger": led})
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
    if r.get("ledger"): L.append(say_ledger(r["ledger"]))
    ch = [x for x in r["missed"] if x.get("chance")]
    for x in ch:
        who = x["by"] if isinstance(x["by"], str) else "; ".join(x["by"])
        if x["kind"] == "interrupt" and x.get("tried"):
            L.append(f"Missed by the defence: {x['skill']} went off; an interrupt was thrown at it and missed ({who}; gvg.report's read: {', '.join(str(r) for r in x['tried'])}).")
        elif x["kind"] == "interrupt": L.append(f"Missed by the defence: {x['skill']} went off with an interrupt ready ({who}){say_amounts(x)}.")
        elif x["kind"] in ("prot", "heal"): L.append(f"Missed by the defence: {who} had {', '.join(x['skills'])} ready, not cast on him{say_amounts(x)}.")
        elif x["kind"] == "strip": L.append(f"Missed by the attack: prot(s) up ({', '.join(x['prots'])}) and a strip ready ({who}), none came{say_amounts(x)}.")
        elif x["kind"] == "pressure": L.append(f"Missed by the attack: an interrupt ready on his monks ({who}), none landed.")
    for x in r["missed"]:
        if x.get("busy_on"): L.append(f"Not a chance: {x['by']} was busy on {x['busy_on']} (R-711).")
        elif x.get("out_of_energy"): L.append(f"Not a chance: {x['by']} was out of energy (R-681).")
        elif x.get("spiked"): L.append(f"Not a chance: {x['by']} was himself under a spike (R-747).")
    return " ".join(L)


# ------------------------------------------------------------------ the ledger (the catalogue's stage 4; R-734: "a death is a sum")
RECAP_NEAR_S = (1, 4)       # gvg.report's recap of a survived spike is this attempt's where its second lies from this long before our first big hit to this long after
                            # our reading of it ends (on the development set its second is a median 2.7 s after our first big hit, 0.5 to 5 s for all but three of 131)


def _recap(E, tgt, t0, t1, died, first=None):
    """gvg.report's recap of this attempt, or None: of his death (within 2 s of it, as the death account reads it), or of the survived spike nearest our first
    big hit. Its figures are its own estimates, shown beside ours (R-717), checked against the replays (R-707: ENGINE_NOTES section 44)."""
    if died: R = [r for r in E.recaps if r["who"] == tgt and r.get("kind") == "death" and abs(r["t"] / 10 - t1) <= 2]
    else: R = [r for r in E.recaps if r["who"] == tgt and r.get("kind") == "save" and (first if first is not None else t0) - RECAP_NEAR_S[0] <= r["t"] / 10 <= t1 + RECAP_NEAR_S[1]]
    return min(R, key=lambda r: abs(r["t"] / 10 - (t1 if died else first if first is not None else t0)), default=None)


def ledger(E, tgt, t0, t1, died, first=None):
    """The sum of a kill attempt on tgt, each part a measured amount (R-734; docs/EXECUTION.md "The logical core"):

        health at the start + healing  against  what landed (hits by their players, hits by their NPCs, degen, Deep Wound)  ->  health at the end

    read between two of his samples, the last at or before t0 and the first at or after t1 (his death, where he died), so that the two ends are health the
    replay itself recorded. `unread` is what the parts leave over (start + healed + deep_wound_back - landed - end): regen, life stolen or given, a weapon
    set changed, the second between two samples; it is kept and shown, never spread over the parts (R-460). What never landed is not in the replays: damage
    stopped by prots and attacks blocked are gvg.report's, from its recap of the death or the survived spike where it has one (`stopped`; None where it has
    none: not known, never nought). `off_shield`: of the hits, what landed while he held a set with no shield and was not casting, and what a shield would
    have stopped of it (`Forensics.sets_damage`; None where he carries no shield set). Health is in points (`Forensics.health`)."""
    F, m = E.F, E.m
    ts = F._track(tgt)[0]
    i0 = F.sample(tgt, t0)
    s0 = ts[i0] if i0 is not None else t0
    i1 = None if died else F.sample(tgt, t1, after=True)
    s1 = t1 if died or i1 is None else ts[i1]
    start, mx = F.health(tgt, s0), F.max_health(tgt, s0)
    end = 0.0 if died else (F.health(tgt, s1) if i1 is not None else None)
    tk, rows = F.taken(tgt, s0, s1)
    ev = [(u, 0, n) for u, n, k, _src in rows if k != "degen"]                 # (second, 0 damage or 1 healing, amount): what lands before what heals inside one tenth
    dg = m.degen().cut(tgt, s0, s1)                                            # every source: the enemy's, nobody's, the hall's
    degen = sum(r[1] for r in dg)
    ev += [(float(r[0]), 0, r[1]) for r in dg]
    F.deep_wound_at(tgt, s0)
    dw = 0.0
    dw_back = 0.0
    for a_, b_ in F._dw.get(tgt, ()):                                          # Deep Wound as it lands takes its cut of his health with his maximum, and gives it back as it ends
        v = F.max_health(tgt, a_ - .6)
        cut = min(DEEP_WOUND_MAX, DEEP_WOUND_SHARE * v) if v else float(DEEP_WOUND_MAX)
        if s0 < a_ <= s1: dw += cut; ev.append((a_, 0, cut))
        if s0 < b_ <= s1 and not (died and b_ >= s1 - .2): dw_back += cut; ev.append((b_ + .05, 2, cut))
    ev += [(u, 1, n) for u, _h, n in E.hl.get(tgt, ()) if s0 < u <= s1]
    ev.sort()
    # Healing is recorded as cast, whether or not he had the health missing to take it: what landed is read by walking the parts in order from his health at
    # the start, a heal filling him no further than his maximum at that second; the rest of it is overhealing, kept apart
    h, healed, over, by_monk = start, 0.0, 0.0, 0.0
    raw = sum(n for _, k, n in ev if k == 1)
    if start is not None:
        for u, k, n in ev:
            if not k: h = max(0.0, h - n); continue
            cap = F.max_health(tgt, u) or mx
            got = max(0.0, min(n, cap - h))
            h += got
            if k == 1: healed += got; over += n - got
    landed = tk["hit"] + tk["npc"] + degen + dw
    out = {"from": round(s0, 1), "to": round(s1, 1), "max": None if mx is None else round(mx), "start": None if start is None else round(start),
           "hits": round(tk["hit"]), "npc": round(tk["npc"]), "degen": round(degen), "deep_wound": round(dw), "landed": round(landed),
           "healed": round(healed) if start is not None else None, "overhealed": round(over) if start is not None else None, "heals_cast": round(raw),
           "deep_wound_back": round(dw_back), "end": None if end is None else round(end)}
    out["unread"] = None if start is None or end is None else round(end - h)   # his health at the end less what the parts give: more is healing or regen unseen, less is damage unseen
    rc = _recap(E, tgt, t0, t1, died, first)
    if rc is None: out["stopped"] = None
    else:
        pv = [[F.name(p[0]) if p[0] in m.PL else None, F.sname(p[1]) if p[1] is not None else None, round(p[4] or 0), p[3] or 0] for p in rc.get("prev") or []]
        out["stopped"] = {"amount": round(sum(p[2] for p in pv)), "blocked": sum(p[3] for p in pv), "by": pv, "recap_t": round(rc["t"] / 10, 1),
                          "their_damage": round((rc.get("totals") or {}).get("damage_taken_estimate") or 0), "their_healing": round((rc.get("totals") or {}).get("healing_received_estimate") or 0)}
    sd = F.sets_damage(m.team(tgt), s0, s1, who=[tgt])["players"].get(F.name(tgt))
    out["off_shield"] = {"landed": sd["off_shield_not_casting"], "shield_would_stop": sd["shield_would_stop"]} if sd and sd["has_shield_set"] else None
    return out


def say_ledger(g, who="He"):
    """The sum in a sentence: what he had, what landed by kind, what was stopped and healed, what he was left with."""
    if not g or g.get("start") is None: return "His health is not in the replay here, so the sum cannot be set out."
    if not g["landed"] and g.get("end") == 0 and g.get("stopped") is None:      # R-460: said, never a blank
        return (f"The sum cannot be set out: {who.lower()} had {g['start']} health of {g['max']} and nothing landed on him in the replay's record, and gvg.report has no recap of the death "
                "(not seen by the observer, life stolen, his own sacrifice): the record does not say what killed him.")
    parts = [f"{g['hits']} in hits"] + [f"{g[k]} {w}" for k, w in (("npc", "from their NPCs"), ("degen", "in degen"), ("deep_wound", "from Deep Wound")) if g[k]]
    st = g.get("stopped")
    L = [f"The sum: {who} had {g['start']} health of {g['max']}; {g['landed']} landed ({', '.join(parts)}); "
         + ("what was stopped before it landed is not in gvg.report's record of this attempt; " if st is None else
            f"{st['amount']} stopped before it landed" + (" (" + ", ".join(f"{b[1] or 'unnamed'} {b[2]}" for b in st["by"][:4] if b[2]) + ")" if any(b[2] for b in st["by"]) else "")
            + (f", {st['blocked']} attack{'s' if st['blocked'] != 1 else ''} blocked" if st["blocked"] else "") + " by gvg.report's estimate; ")
         + f"{g['healed']} healed" + (f" ({g['overhealed']} more cast on him was overhealing)" if g.get("overhealed") else "")
         + (f", {g['deep_wound_back']} back as Deep Wound came off" if g.get("deep_wound_back") else "")
         + (f"; he ended at {g['end']}" if g.get("end") is not None else "; his health at the end is not in the replay")
         + (f" ({abs(g['unread'])} {'more' if g['unread'] > 0 else 'less'} than the parts give)." if g.get("unread") not in (None, 0) else ".")]
    o = g.get("off_shield")
    if o and o["shield_would_stop"]: L.append(f"{o['landed']} of the hits landed while he held a set with no shield and was not casting: a shield would have stopped about {o['shield_would_stop']}.")
    return " ".join(L)


def _amounts(E, row):
    """R-734: beside a missed chance, what it would have stopped or added, measured and not ranked: what a cast of that skill gave that player on average this
    match (`Exec.per_use`). On a prot or a heal, each ready skill's healing and prevention a cast; on an interrupt, the damage a cast of the skill that went
    off did for its caster. Added to the row as `amounts`; a skill gvg.report cannot measure (R-704 c) or he never cast this match is None, never nought."""
    if row["kind"] in ("prot", "heal") and row.get("id") is not None:
        out = {}
        for nm in row.get("skills") or ():
            u = E.per_use(row["id"], nm)
            out[nm] = None if u is None or u.get("unmeasured") or "healing" not in u else {"healed": u["healing"], "stopped": u["stopped"], "casts": u["casts"]}
        row["amounts"] = out
    elif row["kind"] == "interrupt" and row.get("caster") is not None:
        u = E.per_use(row["caster"], row["skill"])
        row["amount"] = None if u is None or "damage" not in u else {"damage": u["damage"], "casts": u["casts"]}
    return row


def say_amounts(x):
    """The amount beside a missed chance, in words (R-734)."""
    nm = lambda s_: s_.replace(" PvP", "")
    if x["kind"] in ("prot", "heal"):
        A = x.get("amounts") or {}
        P = []
        for k in x.get("skills") or ():
            v = A.get(k)
            if v is None: P.append(f"{nm(k)}: not measured by gvg.report")
            else: P.append(f"{nm(k)} about " + " and ".join(p_ for p_ in ((f"{v['stopped']} stopped" if v["stopped"] else ""), (f"{v['healed']} healed" if v["healed"] or not v["stopped"] else "")) if p_) + " a cast")
        return ("; what a cast gave him on average this match: " + ", ".join(P)) if P else ""
    if x["kind"] == "interrupt":
        v = x.get("amount")
        return f" (about {v['damage']} damage a cast for its caster this match)" if v else ""
    if x["kind"] == "strip":
        v = x.get("amount")
        return f"; the prots on him stopped {v} in this attempt by gvg.report's estimate" if v is not None else ""
    return ""


# ------------------------------------------------------------------ the pressure attempt (the catalogue's stage 4; R-741, R-749)
def pressure(E, atts):
    """Every pressure attempt of both teams, beside the spikes (`attempts`): a player kept in danger by the enemy for a while (`Forensics.danger`: his health at
    or under DANGER_HP for DANGER_KEPT_S or longer with DANGER_FIRE landing on him, hits and degen; the cut-offs set from the data, R-741), read to its own
    outcome (R-710): his death, his health back above the line, or the enemy leaving him alone. The record is shaped as a spike's so the same readings serve:
    the sum (`ledger`), the prots and heals cast on him with their seconds from its start, the chances his monks missed (`Forensics.chances`: a prot or a
    heal ready as the danger began, in reach, never cast on him before the outcome; the clock starts when the replay first finds him at or under the line,
    as it starts at the first big hit of a spike, R-748), and who landed what. `spikes`: the seconds of that team's spikes on him inside it (a spike that
    took him under the line, or one that tried to finish him: both records stand, the spike read as a spike). `after_spike`: it began inside a spike's
    own reading, so it is that attempt going on and is no second attempt in any count. A record: no play reads it."""
    from forensics import is_prot, is_heal, DANGER_FIRE
    F, m = E.F, E.m
    F.casts()
    out = []
    for tgt in m.PL:
        tm_d = m.team(tgt); tm = 3 - tm_d
        if tm_d not in (1, 2): continue
        theirs = F.players(tm_d)
        monks = [h for h in theirs if h in E.monk]
        for ep in F.danger(tgt):
            t0, t1 = ep["t0"], ep["t1"]
            if t0 >= E.M.over or (ep["died"] and t1 >= E.M.over): continue          # the losing team recorded dying all at once as the match ends is no attempt (Moments.over)
            tk, rows = F.taken(tgt, t0 - DANGER_FIRE[1], t1)
            by = collections.Counter()
            for _, n, _k, src in rows:
                if isinstance(src, int) and src in m.PL: by[src] += n
            sp = [r for r in atts if r["tm"] == tm and r.get("id") == tgt and r["t"] - ATT_BEFORE_S <= t1 and t0 <= r["t"] + r["s"]]
            on_tgt = [c for h in theirs for c in F._by_agent.get(h, ()) if c[5] == tgt and t0 - ATT_BEFORE_S <= c[2] <= t1]
            prots_up = [F.sname(e[3]) for e in m.o.get("effects") or [] if e[2] == "e" and e[5] == tgt and e[0] is not None and e[0] <= t0 * 10
                        and (e[1] is None or e[1] >= t0 * 10) and is_prot(F.sdata(e[3]))]
            missed = [_amounts(E, x) for x in F.chances(tgt, t0, t1, {"prot": is_prot, "heal": is_heal}, monks=monks)]
            out.append({"t": round(t0, 1), "told": round(ep["told"], 1), "tm": tm, "team": m.tag[tm], "target": m.roles[tgt], "id": tgt, "kind": "pressure",
                        "target_class": "healer" if tgt in E.healer else "other", "killed": bool(ep["died"]), "how": ep["how"], "s": round(t1 - t0, 1),
                        "attackers": [m.roles[a] for a, _ in by.most_common()], "dmg": round(sum(tk.values())),
                        "spikes": [r["t"] for r in sp], "after_spike": next((r["t"] for r in sp if r["t"] <= ep["told"] <= r["t"] + r["s"]), None),
                        "prots_up": prots_up, "prots_cast": [[F.sname(c[1]), round(c[2] - t0, 1), c[4]] for c in on_tgt if is_prot(F.sdata(c[1]))],
                        "heals_cast": [[F.sname(c[1]), round(c[2] - t0, 1), c[4]] for c in on_tgt if is_heal(F.sdata(c[1]))],
                        "missed": missed, "ledger": ledger(E, tgt, t0, t1, ep["died"])})
    return sorted(out, key=lambda r: r["t"])


def say_pressure(r):
    """A pressure attempt in sentences (R-329): what it was, the sum, the chances his monks missed with the amount beside each (R-734), nothing ranked."""
    from forensics import DANGER_HP, DANGER_KEPT_S
    clk = lambda t: f"{int(t // 60)}:{int(t % 60):02d}"
    nm = lambda s_: s_.replace(" PvP", "")
    how = {"died": "he died", "escaped": f"his health came back above {DANGER_HP}", "left alone": "they left him alone", "the match ended": "the match ended"}[r["how"]]
    L = [f"{clk(r['t'])} {r['team']} keep the {r['target']} in danger (at or under {DANGER_HP} health for {DANGER_KEPT_S} s or longer, with damage landing on him) for {r['s']} s: {how}"
         + (f" ({', '.join(r['attackers'][:5])})." if r["attackers"] else " (degen and NPCs only).")]
    if r.get("after_spike") is not None: L.append(f"It follows their spike on him at {clk(r['after_spike'])}: one attempt going on, not a second.")
    elif r["spikes"]: L.append("Their spike" + ("s" if len(r["spikes"]) > 1 else "") + " on him inside it: " + ", ".join(clk(t) for t in r["spikes"]) + ".")
    L.append(say_ledger(r["ledger"]))
    if r["prots_up"]: L.append(f"Prots on him as it began: {', '.join(nm(k) for k in r['prots_up'])}.")
    if r["prots_cast"] or r["heals_cast"]:
        L.append("Cast on him: " + "; ".join(f"{nm(n)} {abs(d)} s {'before' if d < 0 else 'after'} it began ({o})" for n, d, o in (r["prots_cast"] + r["heals_cast"])[:8]) + ".")
    for x in r["missed"]:
        if x.get("chance"): L.append(f"Missed by the defence: {x['by']} had {', '.join(nm(k) for k in x['skills'])} ready, not cast on him before the outcome" + say_amounts(x) + ".")
        elif x.get("busy_on"): L.append(f"Not a chance: {x['by']} was busy on {x['busy_on']} (R-711).")
        elif x.get("out_of_energy"): L.append(f"Not a chance: {x['by']} was out of energy (R-681).")
        elif x.get("spiked"): L.append(f"Not a chance: {x['by']} was himself under a spike (R-747).")
    return " ".join(L)


# ------------------------------------------------------------------ the even 8v8's row (the catalogue's stage 4; R-731)
EVEN_GAP_S = 4              # one reading missed (the fights are read every other second) does not end an even 8v8


def even_rows(E, plays, ATT=None, PRS=None, D=None, FL=None, CT=None):
    """R-731: an even 8v8 with no flag, split or numbers difference has no play and no job, and both teams are read as trying to kill. One execution-only
    row for each such stretch of a fight (never a decision: R-557; kept beside the plays as `flag_cost[rid].even`, no play reads it): every one of the sixteen
    players alive and in one fight (`Moments.fights`), not a stand-off (`Moments.standoff_at`: main teams standing off are not a fight, R-405), for JOIN_S or
    longer (the time after which a player counts in a fight, R-350), one missed reading allowed. "No other job": the seconds inside a play of either team
    are that play's and are left to it (a fight is told once), so a row is the part of the stretch no play covers, where that part is itself JOIN_S or
    longer; `under` names the plays that took the rest. Each row: both teams' measures over it with the objective to kill (`Exec.side`, as on a play), and
    the kill attempts, deaths, failed spikes and casts caught of each team inside it, as places in the match's lists."""
    from common import JOIN_S
    M, m = E.M, E.m
    step = EXEC_STEP
    P1, P2 = set(M.st.players[1]), set(M.st.players[2])
    if len(P1) != 8 or len(P2) != 8: return []
    ok = []
    for t in range(0, int(min(M.T, M.over)) + 1, step):
        g = next((g for g in M.fights(t) if g["n"][1] == 8 and g["n"][2] == 8), None)
        if g is not None and M.standoff_at(P1 | P2, t) is None: ok.append(t)
    runs, cur = [], None
    for t in ok:
        if cur is not None and t - cur[1] <= EVEN_GAP_S: cur[1] = t
        else:
            if cur is not None: runs.append(cur)
            cur = [t, t]
    if cur is not None: runs.append(cur)
    covered = sorted((int(p["t0"]), int(p["t1"]), p["play"]) for p in plays)
    out = []
    for a, b in runs:
        b += step
        if b - a < JOIN_S: continue
        free, u, under = [], a, set()
        for c0, c1, kind in covered:
            if c1 <= a or c0 >= b: continue
            under.add(kind)
            if c0 > u: free.append((u, min(c0, b)))
            u = max(u, c1)
        if u < b: free.append((u, b))
        for t0, t1 in free:
            if t1 - t0 < JOIN_S: continue
            rid = m.o["meta"]["id"]
            row = {"id": f"{rid[:8]}-even_8v8-{t0}", "rid": rid, "play": "even 8v8", "t0": t0, "t1": t1, "s": t1 - t0, "fight": [a, b], "under": sorted(under),
                   "objective": "offence", "teams": [m.tag[1], m.tag[2]], "sides": {}}
            for tm, X, Y in ((1, P1, P2), (2, P2, P1)):
                sd = {"measures": E.side(X, Y, t0, t1, "offence")}
                if ATT is not None: sd["attempts"] = [i for i, r in enumerate(ATT) if r["tm"] == tm and t0 <= r["t"] <= t1]
                if PRS is not None: sd["pressure"] = [i for i, r in enumerate(PRS) if r["tm"] == tm and t0 <= r["t"] <= t1]
                if D is not None: sd["deaths"] = [i for i, d in enumerate(D) if d["tm"] == tm and t0 <= d["t"] <= t1]
                if FL is not None: sd["fails"] = [i for i, d in enumerate(FL) if d["tm"] == tm and t0 <= d["t"] <= t1]
                if CT is not None: sd["caught"] = [i for i, c in enumerate(CT) if c["tm"] == tm and t0 <= c["t"] <= t1]
                row["sides"][m.tag[tm]] = sd
            out.append(row)
    return out


# ------------------------------------------------------------------ casting into a ready interrupt (the catalogue's stage 1; R-743)
def caught(E):
    """Every cast into a ready interrupt that is a fault by R-743: the cast was interrupted, the skill is one worth interrupting (either side of the approved
    list, `worth`), the caster is a backline monk (told by his bar, R-698: "generally only for the backline"), and the interrupt that stopped it was ready
    when the cast began: off recharge, in range, its thrower free to act, and able to stop that kind of skill (the reading of an interrupt chance on a spike
    skill: `can_stop`, `intr_range`, `Forensics.ready`). The interrupter and his skill are the replay's own interrupt record for that cast. A cast stopped
    by something he could not see ready as he began (a knockdown, Shame already on him, an interrupt that came off recharge during the cast, a skill that is
    no interrupt thrown on demand) is not this fault. Tied to no kill attempt, so it is listed on the play's row by kind (R-745). A record: no play reads it."""
    F, m = E.F, E.m
    F.casts()
    listed = worth("offensive") | worth("defensive") | worth("flag")
    is_intr = lambda sd: intr_kind(sd) is not None
    irs = collections.defaultdict(list)                    # caster -> [(second, interrupter, interrupt skill)]
    for i in m.o.get("interrupts") or []:
        if i[0] is not None: irs[i[3]].append((i[0] / 10, i[1], i[2]))
    out = []
    for a in sorted(E.monk):
        foes = {f: _role_skills(F, f, is_intr) for f in F.enemies(a)}
        for c in F._by_agent.get(a, ()):
            if c[4] != "interrupted" or c[1] is None or c[3] is None: continue
            sd_c = F.sdata(c[1])
            if (sd_c.get("name") or "").replace(" (PvP)", "") not in listed: continue
            t = c[2]
            row = next(((by, sk) for u, by, sk in irs.get(a, ()) if abs(u - c[3]) <= .3 and by in foes), None)
            if row is None: continue
            by, sk = row
            ready = [sid for sid, sd in foes[by] if (sk is None or sid == sk) and can_stop(sd, sd_c) and (F.dist(by, a, t) or 1e9) <= intr_range(F, by, sd, t) and _ready(F, by, sid, sd, t)]
            if not ready: continue
            tm = m.team(a)
            out.append({"t": round(t, 1), "id": a, "tm": tm, "team": m.tag[tm], "who": m.roles[a], "skill": F.sname(c[1]),
                        "on": m.roles[c[5]] if c[5] in m.PL and c[5] != a else None, "by": [F.name(by), F.sname(ready[0])]})
    return sorted(out, key=lambda r: r["t"])


def say_caught(c):
    clk = lambda t: f"{int(t // 60)}:{int(t % 60):02d}"
    nm = lambda s_: s_.replace(" PvP", "")
    return (f"{clk(c['t'])} {c['team']}'s {c['who']} cast {nm(c['skill'])}" + (f" on {c['on']}" if c.get("on") else "") + f" into a ready interrupt and was interrupted: {c['by'][0]} had "
            + f"{nm(c['by'][1])} ready and in range when the cast began (R-743).")


# ------------------------------------------------------------------ the faults said on a death and on a play (stage X4; R-713, R-714, R-715)
FAULT_KINDS = ("prot", "heal", "interrupt")      # the kinds of missed chance stage X3 passed on unseen matches (`cases.py attempts` section G, which stops with an error
                                                 # when its verdicts and this line differ): a strip missed by the attack reads backwards and pressure on the target's
                                                 # monks shows no difference, so neither is ever told as a fault (R-285). All three are the defence's, so by R-714 a
                                                 # fault is listed only where a player died: on a spike that killed, and in the death accounts.


RULED_KINDS = ("strip",)    # the kinds of missed chance he rules by name (R-744): told as faults whatever the check on unseen matches shows, the check's result said beside
                            # them (`ruled_check`), and brought to him where they read backwards. A strip ready and not used on a protted target is the attack's, so by
                            # R-714 it is listed on a spike that failed (R-729). Pressure on the target's monks is ruled by nobody and fails the check: never told.


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


def deaths(E, atts, prs=None):
    """Every death of a player with the checked chances his team missed (stage X4; kept beside the plays as `flag_cost[rid].deaths`, no play reads it). A fault
    is a missed chance of a kind stage X3 passed (FAULT_KINDS), none priced or ranked (R-713), and all are the defence's, so they are listed where a player
    died (R-714): on the spike that killed him, read from its kill attempt (a prot, a heal, an interrupt on a spike skill), and on a death with no spike
    (under 400 on him inside 3 s) from the pressure attempt that killed him (R-749: `pressure`, in place of the heaviest 2 s on him; a prot, a heal; the
    interrupt chance is defined on a spike's skills). Where he died without having been kept in danger (`kept` False: he fell from above the line and died
    inside a second, or with too little landing on him) the reading starts at the first thing the enemy landed on him after the replay last found him above
    the line (`Forensics.death_start`). Each death carries the sum (`ledger`, R-734) and each fault what it would have stopped or added (`_amounts`).
    A kind a team mate took in time is no fault and is not listed against the player who held back (R-715). The record holds what was there; its words are `say_death`. Beside the faults, what was no chance: a monk busy on a player under pressure (R-711) or out of energy (R-681). The deaths recorded as
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
            d["ledger"] = r.get("ledger")
            for kind in ("prot", "heal"):
                if kind not in FAULT_KINDS: continue
                tk, mi, _ = T[kind]
                if tk(r): taken.append(kind)
                elif mi(r): faults += [{"kind": kind, "by": x["by"], "skills": x["skills"], "at": x["at"], "amounts": x.get("amounts")} for x in r["missed"] if x["kind"] == kind and x.get("chance")]
            if "interrupt" in FAULT_KINDS:
                for x in r["missed"]:
                    if x["kind"] != "interrupt" or x.get("at", 0) > CHANCE_S: continue
                    if x.get("taken"): taken.append("interrupt")
                    elif x.get("chance"): faults.append({"kind": "interrupt", "skill": x["skill"], "by": [who_what(b_) for b_ in x["by"]], "at": x["at"], "amount": x.get("amount"), **({"tried": x["tried"]} if x.get("tried") else {})})
            other = [x for x in r["missed"] if x.get("busy_on") or x.get("out_of_energy") or x.get("spiked")]
        else:
            # R-749: the pressure attempt that ended in this death, in place of the heaviest 2 s on him; where he was not kept in danger, from the first
            # thing landed on him after he was last found above the line (`Forensics.death_start`). One reading of where it starts for both.
            q = next((q for q in (prs or ()) if q["killed"] and q["id"] == a and abs(q["t"] + q["s"] - td) <= 0.3), None)
            bt, kept = (q["t"], True) if q is not None else F.death_start(a, td)
            tk_, rows_ = F.taken(a, bt - .05, td)
            d.update(first=round(bt, 1), kept=bool(kept), dmg=round(sum(tk_.values())), attackers=sorted({m.roles[x[3]] for x in rows_ if x[3] in pl}),
                     ledger=q["ledger"] if q is not None else ledger(E, a, bt, td, True))
            kinds = {k: f for k, f in (("prot", is_prot), ("heal", is_heal)) if k in FAULT_KINDS}
            ch = [_amounts(E, c) for c in F.chances(a, bt, td, kinds)]
            taken = F.taken_in_time(a, bt, kinds)
            faults = [{"kind": c["kind"], "by": c["by"], "skills": c["skills"], "at": c["at"], "amounts": c.get("amounts")} for c in ch if c["chance"] and c["kind"] not in taken]
            other = [c for c in ch if c.get("busy_on") or c.get("out_of_energy") or c.get("spiked")]
        d["faults"] = faults
        d["taken"] = sorted(set(taken))
        d["no_chance"] = [{"kind": x["kind"], "by": x["by"], **({"busy_on": x["busy_on"]} if x.get("busy_on") else {"spiked": True} if x.get("spiked") else {"out_of_energy": True})}
                          for x in other if x["kind"] in FAULT_KINDS]
        out.append(d)
    return sorted(out, key=lambda d: d["t"])


def credit(r):
    """R-733: what the defence did well on an attempt that did not kill, shown apart from the attack's faults and never as one: the prots and heals it cast
    on him that finished inside the seconds a chance is looked for (to CHANCE_S after the start), the spike skills it interrupted, and from the sum what was
    stopped before it landed (gvg.report's estimate, where it has a recap) and what was healed. What was there, no judgement."""
    g = r.get("ledger") or {}
    return {"prots": sorted({n for n, d_, o in r.get("prots_cast") or () if o == "finished" and d_ <= CHANCE_S}),
            "heals": sorted({n for n, d_, o in r.get("heals_cast") or () if o == "finished" and d_ <= CHANCE_S}),
            "interrupted": sorted({x["skill"] for x in r.get("missed") or () if x["kind"] == "interrupt" and x.get("taken")}),
            "stopped": (g.get("stopped") or {}).get("amount"), "healed": g.get("healed")}


def say_credit(c, name):
    nm = lambda s_: s_.replace(" PvP", "")
    P = ([f"prots in time ({', '.join(nm(k) for k in c['prots'])})"] if c["prots"] else []) + ([f"heals in time ({', '.join(nm(k) for k in c['heals'])})"] if c["heals"] else []) \
        + ([f"interrupted {', '.join(nm(k) for k in c['interrupted'])}"] if c["interrupted"] else [])
    amt = ([f"{c['stopped']} stopped before it landed"] if c.get("stopped") else []) + ([f"{c['healed']} healed"] if c.get("healed") else [])
    if not P and not amt: return ""
    return f"{name}'s credit, apart (R-733): " + ("; ".join(P) if P else "nothing cast in time") + (" (" + ", ".join(amt) + ")" if amt else "") + "."


def fails(E, atts):
    """Every spike that did not kill, with the attack's missed chances of the kinds he rules by name (RULED_KINDS; R-729, R-744), listed where the attack
    failed (R-714): a strip ready and in range at the first big hit with a prot on the target, and none came from 3 s before the first big hit to CHANCE_S
    after it (`chance_tests`, the one reading of taken and missed). A strip that took a prot off in those seconds is the strip taken (good play, R-729); one
    that came only later is kept apart as late (done out of time, R-713: not listed as a fault, since the record does not say it was ready at the first
    hit). The record holds what was there; its words are `say_fail`. Kept beside the plays as `flag_cost[rid].fails`; no play reads it."""
    F, m, T = E.F, E.m, chance_tests()
    names = sorted((F.name(a) for a in m.PL), key=len, reverse=True)
    who_what = lambda s_: next(([n, s_[len(n) + 1:]] for n in names if s_.startswith(n + " ")), [s_, ""])
    out = []
    for r in atts:
        if r["killed"]: continue
        tm = r["tm"]
        d = {"t": r["t"], "tm": tm, "team": r["team"], "on": m.tag[3 - tm], "target": r["target"], "id": E.agent.get((m.tag[3 - tm], r["target"])), "dmg": r["dmg"],
             "attackers": r["attackers"], "spread": r["spread"], "prots_up": r["prots_up"], "ledger": r.get("ledger"), "credit": credit(r)}
        faults, taken, late = [], [], []
        for kind in RULED_KINDS:
            tk, mi, lt = T[kind]
            if tk(r): taken.append(kind)
            elif mi(r): faults += [{"kind": kind, "by": [who_what(b_) for b_ in x["by"]], "prots": x.get("prots") or [], "amount": x.get("amount")} for x in r["missed"] if x["kind"] == kind and x.get("chance")]
            elif lt(r): late.append({"kind": kind, "at": min((a_ for a_, _p in r[kind].get("at", [])), default=None), "prot_off": bool(r[kind].get("prot_off"))})
        d.update(faults=faults, taken=taken, late=late)
        out.append(d)
    return out


_CHECK = {}


def ruled_check(kind):
    """What the check on unseen matches says of a ruled kind (R-744: shown beside the fault as evidence): (verdict, difference in points of spikes that killed,
    taken against missed, like with like) from the last `cases.py attempts` kept in data/model/attempts_cases.json, or None where no report is kept."""
    if not _CHECK:
        import json, os
        p = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "model", "attempts_cases.json")
        _CHECK.update((json.load(open(p, encoding="utf-8")).get("x3") or {}) if os.path.exists(p) else {}); _CHECK.setdefault("", None)
    v = _CHECK.get(kind)
    return (v["verdict"], round(v["difference"], 1)) if v else None


RULED_SAY = {"strip": "a strip on a protted target"}
RULED_BY = {"strip": "R-729, R-744"}


def say_fail(d):
    """A spike that did not kill, in sentences: what it was, then the attack's ruled misses with what was there and the check's result beside them (R-744)."""
    clk = lambda t: f"{int(t // 60)}:{int(t % 60):02d}"
    nm = lambda s_: s_.replace(" PvP", "")
    L = [f"{clk(d['t'])} {d['team']}'s spike on {d['on']}'s {d['target']} does not kill ({', '.join(d['attackers']) or 'nobody recorded'}): {d['dmg']} in 3 s, the big hits over {d['spread']} s"
         + (f"; on him at the first big hit: {', '.join(nm(k) for k in d['prots_up'])}." if d["prots_up"] else "; no prot on him at the first big hit.")]
    for kind in RULED_KINDS:
        X = [x for x in d["faults"] if x["kind"] == kind]
        if X:
            ck = ruled_check(kind)
            L.append(f"Missed by {d['team']}, {RULED_SAY[kind]} (a fault by his ruling, {RULED_BY[kind]}): " + "; ".join(f"{w[len(d['team']) + 1:] if w.startswith(d['team'] + ' ') else w} had {nm(v)}" for x in X for w, v in x["by"])
                     + " ready and in range, and none came from 3 s before the first big hit to 1.5 s after it"
                     + "".join(say_amounts({"kind": kind, "amount": x.get("amount")}) for x in X[:1]) + "."
                     + (f" The check on unseen matches: {ck[0]} (the strip taken against missed, {ck[1]:+.1f} points of spikes that killed)." if ck else " The check on unseen matches: not yet run on this reading."))
        elif kind in d["taken"]: L.append(f"Done in time by {d['team']} (good play, R-729): {RULED_SAY[kind]}.")
        for x in d["late"]:
            if x["kind"] != kind or x.get("at") is None: continue
            L.append(f"{d['team']}'s strip came in time ({x['at']:+.1f} s from the first big hit) but took no prot off." if x["at"] <= CHANCE_S
                     else f"Out of time (R-713): {d['team']}'s strip came only {x['at']:+.1f} s from the first big hit.")
    if d.get("ledger"): L.append(say_ledger(d["ledger"]))
    if d.get("credit"):
        c_ = say_credit(d["credit"], d["on"])
        if c_: L.append(c_)
    return " ".join(L)


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
    elif d.get("kept"): L = [f"{clk(d['t'])} {d['team']}'s {d['who']} dies with no spike on him (under 400 inside 3 s), kept in danger by {d['by']} from {clk(d['first'])} (at or under {DANGER_HP} health with damage landing on him, R-749): {d['dmg']} landed on him, hits and degen ({who})."]
    else: L = [f"{clk(d['t'])} {d['team']}'s {d['who']} dies with no spike on him (under 400 inside 3 s) and without being kept in danger first: {d['dmg']} landed on him from {d['by']} ({who}) between {clk(d['first'])}, the first thing landed on him after he was last above {DANGER_HP} health, and his death."]
    if d.get("ledger"): L.append(say_ledger(d["ledger"]))
    for kind in ("prot", "heal"):
        X = [x for x in d["faults"] if x["kind"] == kind]
        if X: L.append(f"Missed by {d['team']}, {FAULT_SAY[kind]}: " + "; ".join(f"{mine(x['by'])} had {', '.join(nm(k) for k in x['skills'])} ready, in reach, his hands free" + say_amounts(x) for x in X) + "; not cast on him in the time he had to see " + ("the hit" if d["spike"] else "it") + " and cast (R-716).")
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
                 + ((lambda A: " What a cast of each did for its caster on average this match (R-734): " + ", ".join(f"{k} about {v}" for k, v in A.items()) + "." if A else "")(
                     collections.OrderedDict((nm(x["skill"]), x["amount"]["damage"]) for x in X if x.get("amount"))))
                 + (" Thrown and missed: " + "; ".join(tried) + "." if tried else ""))
    if not d["faults"]: L.append(f"No checked chance missed by {d['team']}" + (" (a prot, a heal or an interrupt on a spike skill)." if d["spike"] else " (a prot or a heal; with no spike there is no spike skill to interrupt)."))
    if d["taken"]: L.append("Done in time by a team mate, so no fault (R-715): " + ", ".join(FAULT_SAY[k] for k in d["taken"]) + ".")
    for x in d["no_chance"]:
        L.append(f"Not a chance ({FAULT_SAY[x['kind']]}): {mine(x['by'])} was busy on {mine(x['busy_on'])}, who was under pressure (R-711)." if x.get("busy_on")
                 else f"Not a chance ({FAULT_SAY[x['kind']]}): {mine(x['by'])} was himself under a spike (R-747)." if x.get("spiked")
                 else f"Not a chance ({FAULT_SAY[x['kind']]}): {mine(x['by'])} was out of energy (R-681).")
    return L


def say_faults(p, x, D, teams, FL=None, CT=None, ATT=None, PRS=None):
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
    def attack(sd, name):                                  # the spikes that did not kill, with the strip missed (R-729, R-744, R-714)
        L = [FL[i] for i in (x.get("fails") or {}).get(sd, ())] if FL is not None else []
        if not L: return ""
        W = [d for d in L if d["faults"] or d["late"]]
        return (f" {name}'s spikes that did not kill: {len(L)}, {sum(1 for d in L if d['faults'])} with a strip missed (a fault by his ruling, R-744)"
                + f", {sum(1 for d in L if d['taken'])} with the strip in time." + (" " + " ".join(say_fail(d) for d in W) if W else ""))
    def play_level(sd, name):                              # faults tied to no kill attempt, always listed on the play's row by kind, with their count (R-745)
        L = [CT[i] for i in (x.get("caught") or {}).get(sd, ())] if CT is not None else []
        return f" {name}, casts into a ready interrupt (R-743): {len(L)}. " + " ".join(say_caught(c) for c in L) if L else ""
    # question 3 (R-732): where the play's job is to kill, every kill attempt it made over the whole play, each with its sum and the enemy's credit apart (R-733)
    q3 = ""
    if asks_q3(p, x) and ATT is not None and PRS is not None and "attempts" in x:
        q3 = " " + say_q3(p["team"], foe, [ATT[i] for i in x["attempts"]["own"]], [PRS[i] for i in x["pressure"]["own"]], p["t0"], p["t0"] + x["s"], FL, brief=True)
    return (side("own", p["team"]) + attack("own", p["team"]) + play_level("own", p["team"]) + q3
            + " Apart, the enemy it met (never a fix, R-299): " + side("their", foe) + attack("their", foe) + play_level("their", foe)
            + (" Context, not a fault: " + "; ".join(ctx) + "." if ctx else ""))


def asks_q3(p, x):
    """Is question 3 asked of this play (why a team that should have killed did not)? Where its job is to kill (`objective`, R-709), and on every numbers
    advantage from the side that has it, whatever the call it made there (R-732: the window is the whole numbers advantage; R-557: a team up on numbers
    keeps trying to kill)."""
    return x.get("objective") == "offence" or (p.get("play") == "numbers" and p.get("numbers_side") in ("up", "strong side", "after a wipe"))


def say_q3(team, foe, A, P, t0, t1, FL=None, brief=False):
    """Question 3 in sentences (R-732: why a team that should have killed did not, read over the whole numbers advantage, attempt by attempt): every kill
    attempt of `team` in [t0, t1], spikes (A) and pressure attempts (P), then each one that did not kill with its sum (R-734), the attack's ruled misses and
    the enemy's credit apart (R-733). A pressure attempt that only carries a spike on (`after_spike`) is that spike's and is not counted again. FL: the
    match's failed spikes (`fails`), whose sentences carry the strip missed."""
    clk = lambda t: f"{int(t // 60)}:{int(t % 60):02d}"
    P = [q for q in P if q.get("after_spike") is None]
    n, k = len(A) + len(P), sum(1 for r in A + P if r["killed"])
    tg = len({r["id"] for r in A + P})
    if not n: return f"Question 3 (R-732), {clk(t0)} to {clk(t1)}: {team} made no kill attempt: no spike (400 on one player inside 3 s) and nobody of {foe} kept in danger."
    L = [f"Question 3 (R-732), {clk(t0)} to {clk(t1)}: {team} made {n} kill attempt{'s' if n != 1 else ''} on {tg} player{'s' if tg != 1 else ''} ({len(A)} spike{'s' if len(A) != 1 else ''}, "
         f"{len(P)} time{'s' if len(P) != 1 else ''} a player kept in danger), {k} killed."]
    by_t = {(d["t"], d["id"]): d for d in FL or ()}
    for r in sorted(A + P, key=lambda r: r["t"]):
        if brief and r.get("kind") != "pressure" and not r["killed"]:        # said in full beside it already: the time, the target and the sum only
            L.append(f"{clk(r['t'])} spike on the {r['target']}, he lived. " + say_ledger(r.get("ledger")) + " " + say_credit(credit(r), foe))
        elif r["killed"]: L.append(f"{clk(r['t'])} the {r['target']} dies ({'spike' if r.get('kind') != 'pressure' else 'kept in danger'}). " + say_ledger(r.get("ledger")))
        elif r.get("kind") == "pressure": L.append(say_pressure(r) + " " + say_credit(credit(r), foe))
        else: L.append(say_fail(by_t[(r["t"], r["id"])]) if (r["t"], r["id"]) in by_t else say_attempt(r))
    return " ".join(x.strip() for x in L if x)


def say_even(row, ATT, PRS, FL=None):
    """An even 8v8's row in sentences (R-731): both teams read as trying to kill, each by question 3."""
    clk = lambda t: f"{int(t // 60)}:{int(t % 60):02d}"
    a, b = row["teams"]
    L = [f"{clk(row['t0'])} to {clk(row['t1'])}, an even 8v8 with no other job ({row['s']} s; execution only, no decision, R-731): both teams are read as trying to kill."]
    for team, foe in ((a, b), (b, a)):
        sd = row["sides"][team]
        L.append(say_q3(team, foe, [ATT[i] for i in sd.get("attempts", ())], [PRS[i] for i in sd.get("pressure", ())], row["t0"], row["t1"], FL))
    return "\n".join(L)


def record(M, rid, plays, E=None, D=None, FL=None, CT=None, ATT=None, PRS=None):
    """{play id: its execution record} for the plays of one match (kept beside the plays; no play reads it). With the match's deaths (`deaths`), each record
    carries `deaths`: for the play's own players and for the enemy players it met, which deaths fell inside the play (their places in the deaths record), so
    the faults are said on the play (stage X4). With the kill attempts (`attempts`, `pressure`), each carries `attempts` and `pressure` the same way: the
    attempts its own players made on the enemy it met and those made on them, over the whole play, so that question 3 is read attempt by attempt (R-732)."""
    E, out = E or Exec(M, rid), {}
    for p in plays:
        r = E.play(p)
        if r is None: continue
        if D is not None:
            X, Y, t0, t1 = E.players(p)
            r["deaths"] = {"own": [i for i, d in enumerate(D) if d["id"] in X and t0 <= d["t"] <= t1], "their": [i for i, d in enumerate(D) if d["id"] in Y and t0 <= d["t"] <= t1]}
        if FL is not None or CT is not None:               # the spikes that did not kill and the casts caught inside the play, as places in `fails` and `caught` (stage 1 of the catalogue)
            X, Y, t0, t1 = E.players(p)
            Xs, Ys, tm = set(X), set(Y), p["tm"]
            if FL is not None: r["fails"] = {"own": [i for i, d in enumerate(FL) if d["tm"] == tm and d["id"] in Ys and t0 <= d["t"] <= t1],
                                             "their": [i for i, d in enumerate(FL) if d["tm"] == 3 - tm and d["id"] in Xs and t0 <= d["t"] <= t1]}
            if CT is not None: r["caught"] = {"own": [i for i, c in enumerate(CT) if c["id"] in Xs and t0 <= c["t"] <= t1],
                                              "their": [i for i, c in enumerate(CT) if c["id"] in Ys and t0 <= c["t"] <= t1]}
        for key, L_ in (("attempts", ATT), ("pressure", PRS)):
            if L_ is None: continue
            X, Y, t0, t1 = E.players(p)
            Xs, Ys, tm = set(X), set(Y), p["tm"]
            r[key] = {"own": [i for i, a_ in enumerate(L_) if a_["tm"] == tm and a_["id"] in Ys and t0 <= a_["t"] <= t1],
                      "their": [i for i, a_ in enumerate(L_) if a_["tm"] == 3 - tm and a_["id"] in Xs and t0 <= a_["t"] <= t1]}
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
        A_ = attempts(E_)
        for d in deaths(E_, A_, pressure(E_, A_)):
            if d["t"] >= frm: print(say_death(d) + "\n")
        sys.exit()
    if a[0] in ("fails", "caught"):                       # python3 execution.py fails|caught <report id> [m:ss]: the spikes that did not kill with the strip missed; the casts into a ready interrupt (R-743)
        import moments
        from scoreboard import Scoreboard
        st = GameState(Match.from_branch(a[1])); M = moments.Moments(st, Scoreboard(st))
        frm = (lambda s: int(s.split(":")[0]) * 60 + int(s.split(":")[1]))(a[2]) if len(a) > 2 else 0
        E_ = Exec(M, a[1])
        for d in (fails(E_, attempts(E_)) if a[0] == "fails" else E_.caught()):
            if d["t"] >= frm: print((say_fail(d) if a[0] == "fails" else say_caught(d)) + "\n")
        sys.exit()
    if a[0] in ("pressure", "even"):                     # python3 execution.py pressure|even <report id> [m:ss]: the pressure attempts (R-741, R-749); the even 8v8s' rows (R-731)
        import moments, jobs
        from scoreboard import Scoreboard
        st = GameState(Match.from_branch(a[1])); M = moments.Moments(st, Scoreboard(st))
        frm = (lambda s: int(s.split(":")[0]) * 60 + int(s.split(":")[1]))(a[2]) if len(a) > 2 else 0
        E_ = Exec(M, a[1])
        A_ = attempts(E_); P_ = pressure(E_, A_)
        if a[0] == "pressure":
            for r in P_:
                if r["t"] >= frm: print(say_pressure(r) + "\n")
        else:
            FL_ = fails(E_, A_)
            for row in even_rows(E_, jobs.plays(M, M.records()), A_, P_, deaths(E_, A_, P_), FL_, E_.caught()):
                if row["t1"] >= frm: print(say_even(row, A_, P_, FL_) + "\n")
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
