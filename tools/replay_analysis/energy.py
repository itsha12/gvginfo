"""Energy (R-664 to R-689): one reading, `Match.energy()`.

The replays hold no energy. gvg.report models it: for every player the least and the most energy he can have, every
two seconds, and his maximum as it changes with the weapon set he holds and with his death penalty or morale boost.
That estimate is kept in the file beside each replay (extras.py) and is what is read here. It is an estimate with
bounds, and every reading from it carries both (`lo`, `hi`); `mid` is their middle. A match gvg.report has no energy
for (before 27 August 2026, and 18 counted matches of 2 to 5 September) reads blank: `ok` is False and every figure
is None (R-672).

Whose energy (R-665, R-670, R-675): the backline monks' first; the midline's, which for energy is the Ritualist, the
Mesmer, the Elementalist, the Necromancer and the smite monk; nobody else's (`kind` is None for the frontline, the
Ranger and the Paragon, and nothing here answers for them).

The scale (R-667, R-668, R-686): energy is read as what the player would have if he took up his double high set now.
A monk can always change sets, so a monk at 10 on a 40/40 set has 30 more to call on, at the price of regeneration.
So `scaled = shown + what the change of set would add`, never less than what is shown. For a Monk, a Mesmer, a
Ritualist and a Necromancer, whose casting sets hold 42 alike, the double high set holds 72 and the change adds 72
less the maximum of the set held. Death penalty and morale move a maximum by their share of the BASE 20 energy only,
never of what armour and weapons add: +2 at a full boost, -3 a death, -12 at 60%, on every set alike (the game's
rule, and what gvg.report's maximum does: a monk's shield set reads 25, 27 on a full boost, 22 after one death). So
`top = 72 + 20 x morale / 100`, and what a change of set adds does not move with morale. (Until 2026-11-24 the top
was 72 x (1 + morale / 100): a monk on a boost read 5 too high and one at 15% death penalty 6 too low, at 60% as
having no set to change to: 43% of all readings, and always against the team with deaths behind it.)
An Elementalist's maximum also holds his Energy Storage and falls with Overcast, so it does not say which set he
holds; the replay does (the weapon set of each sample, gvg.report's labels). What the change would add is read from
the set held, `SET_HOLDS`: 72 less 42 on a wand and focus, 40 on a staff, 62 in single high, 72 in double high, 30
on anything else (a shield set, a flag in hand). Energy Storage and Overcast are in what is shown already and are
the same on every set. (Until 2026-11-24 his top was the highest maximum he held in the match, which counted his
Overcast as energy to call on and gave him a double high set only where he had shown one.)

Out of energy, for the excuse (R-681, R-682): a monk under 20, a midline player under 15, on that scale. `out` is
"yes" where even the most he can have is under the line, "maybe" where only the least is, else "no". These two lines
are his set points for the excuse only: where energy is an input to a decision no line is set, and what followed is
read across the range of energy at that decision (R-669).

    E = Match.from_branch("<report id>").energy()
    E.ok                      False where gvg.report has no energy for the match
    E.kind(a)                 "monk", "midline" or None
    E.at(a, t)                {lo, hi, mid, shown: (lo, hi), cap, top, set, out} at second t on the scale; None where unread or he is dead
                              (`set` False where an Elementalist's set is not known and 30 is taken)
    E.group(ids, t)           the read players among ids, alive: {n, mean, low, mean_lo, mean_hi, out, maybe}; `low` is the lowest
                              player's middle (R-683: the average, the lowest monk and how many, the data to say which tells)
    E.monks(ids), E.midline(ids)    the backline monks and the midline among ids

    E.account(a, t0, t1)      where his energy went over a stretch: had, spent on casts, taken by the enemy, came back (the excuse, below)
    denial(m)                 every time an enemy skill took energy from a player (R-685)
    excuse(M, plays)          the record kept beside the plays: at each death the monks of that fight, who was out and where the minute's energy
                              went; at each failure to kill, the midline of the team that had the job (R-666, the second aspect)

    python3 energy.py <report id>     each read player's energy through one match
    python3 energy.py <report id> excuse [m:ss]     the excuse of every death and failure to kill in a match (from the second given), as sentences
    python3 energy.py cover           coverage, and the checks of the record over every counted match (does it read as a player knows)
"""
import bisect, collections

TOP = 72                        # a double high set (R-667): 40 on a staff, 42 on a 40/40 set, 62 in single high, 72 in double high
OUT_MONK = 20                   # a monk under this is out, for the excuse (R-681: "Anything less than 20e in my mind would likely be not the monk's fault")
OUT_MIDLINE = 15                # a midline player under this is out (R-682), on the same scale (R-686)
MIDLINE = ("Ritualist", "Mesmer", "Elementalist", "Necromancer")      # R-670; the smite monk is told below
BASE = 20                       # the base energy, the only part of a maximum death penalty and morale move (the game's rule; gvg.report's maximum follows it)
SET_HOLDS = (("Double High", 72), ("Single High", 62), ("Wand", 42), ("Staff", 40))      # what a caster's set holds at no Energy Storage, by gvg.report's label of it (R-667); any other set 30
SET_ELSE = 30                   # a shield set (25 to 35 by its weapon), a martial weapon, a flag in hand


def backline_monk(m, a):
    """A backline monk, as `jobs.plays` tells one (R-457): a Monk in a monk's slot who does not smite."""
    r = m.roles.get(a) or ""
    return m.A[a].get("p") == "Monk" and not r.startswith("Monk ") and "WoC" not in r


class Energy:
    def __init__(self, m):
        self.m = m
        E = m.extras().energy
        self.ok = bool(E and E.get("players"))
        self._k = {}
        for a in m.PL:
            p = m.A[a].get("p")
            self._k[a] = "monk" if backline_monk(m, a) else "midline" if p in MIDLINE or p == "Monk" else None
        if not self.ok: return
        self.step, self.start = E["step"] / 10, E["start"] / 10
        self._p = {int(a): v for a, v in E["players"].items()}
        self._cap = {a: ([c[0] / 10 for c in v.get("cap") or []], [c[1] for c in v.get("cap") or []]) for a, v in self._p.items()}
        self._mo = collections.defaultdict(lambda: ([], []))      # player -> (seconds, death penalty or morale boost in % of his maximum)
        for e in m.o.get("ev") or []:
            if e[1] == "mo" and e[0] is not None and e[2] in self._k and isinstance(e[5], (int, float)):
                ts, vs = self._mo[e[2]]; ts.append(e[0] / 10); vs.append(e[5])
        self._sets = {int(a): [x.get("label") or "" for x in v] for a, v in (m.o.get("sets") or {}).items()}      # each player's weapon sets, by the index his samples carry (`w`)

    def kind(self, a): return self._k.get(a)
    def monks(self, ids): return [a for a in ids if self._k.get(a) == "monk"]
    def midline(self, ids): return [a for a in ids if self._k.get(a) == "midline"]

    def morale(self, a, t):
        """His death penalty (negative) or morale boost at t, in %."""
        ts, vs = self._mo[a] if a in self._mo else ((), ())
        i = bisect.bisect_right(ts, t) - 1
        return vs[i] if i >= 0 else 0

    def _adds(self, a, t, s, cap):
        """What taking up his double high set would add at t (never less than nothing), and whether his set is known.
        An Elementalist: from the set his sample holds; everybody else: the double high maximum less the maximum held."""
        if self.m.A[a].get("p") == "Elementalist":
            L, w = self._sets.get(a) or [], s.get("w", -1)
            label = L[w] if w is not None and 0 <= w < len(L) else None
            return TOP - next((v for k, v in SET_HOLDS if label and k in label), SET_ELSE), label is not None
        return max(TOP + BASE * self.morale(a, t) / 100 - cap, 0), True

    def at(self, a, t):
        if not self.ok or self._k.get(a) is None or a not in self._p: return None
        s = self.m.snap(a, round(t * 10))
        if not self.m.alive(s): return None
        v = self._p[a]
        i = int((t - self.start) // self.step)                   # the sample at or before t, never the one after it (SPEC 5, rule 1)
        if i < 0 or i >= len(v["lo"]) or v["lo"][i] is None or v["hi"][i] is None: return None
        ts, cs = self._cap[a]
        j = bisect.bisect_right(ts, t) - 1
        cap = cs[max(j, 0)] if cs else None
        if cap is None: return None
        add, known = self._adds(a, t, s, cap)
        lo, hi = v["lo"][i] + add, v["hi"][i] + add
        line = OUT_MONK if self._k[a] == "monk" else OUT_MIDLINE
        return {"lo": round(lo, 1), "hi": round(hi, 1), "mid": round((lo + hi) / 2, 1), "shown": (v["lo"][i], v["hi"][i]), "cap": cap, "top": round(cap + add, 1),
                "set": known, "out": "yes" if hi < line else "maybe" if lo < line else "no"}

    def shown(self, a, t):
        """(least, most) energy gvg.report gives any player on the set he holds at t, read or not; None where it has none."""
        if not self.ok or a not in self._p: return None
        v = self._p[a]
        i = int((t - self.start) // self.step)
        return None if i < 0 or i >= len(v["lo"]) or v["lo"][i] is None or v["hi"][i] is None else (v["lo"][i], v["hi"][i])

    def group(self, ids, t):
        """The read players among ids who are alive at t, together (R-683). None where the match has no energy; n 0 where none of them is read or alive."""
        if not self.ok: return None
        r = [x for x in (self.at(a, t) for a in ids) if x]
        if not r: return {"n": 0, "mean": None, "low": None, "mean_lo": None, "mean_hi": None, "out": 0, "maybe": 0}
        n = len(r)
        return {"n": n, "mean": round(sum(x["mid"] for x in r) / n, 1), "low": min(x["mid"] for x in r), "mean_lo": round(sum(x["lo"] for x in r) / n, 1),
                "mean_hi": round(sum(x["hi"] for x in r) / n, 1), "out": sum(x["out"] == "yes" for x in r), "maybe": sum(x["out"] == "maybe" for x in r)}


# ---- each fight's energy on every play (R-689, piece 2; R-666 the third aspect, R-683): a record kept beside the plays, `flag_cost[rid].energy`.
# It tells no play and changes none. For every play: the second its decision arises (`decision_second`), and at that second and BEFORE_S before it, the
# energy of the backline monks and of the midline in that fight, the team's own and the enemy's, each as `Energy.group` (the average, the lowest player
# and how many: the data to say which tells, R-683). Whose (R-666: "on a split, only split monk energy matters"): on a split play (a split or its
# defence) our side is the players it names (`who`); on every other play our main team at that second, the fight the decision is about (a flag, a boost or
# a push play names its runners or pushers, who are not that fight; a runner away is the reason the fight is 8 v 7); their side is every enemy player in
# the same fight as one of ours in the FIGHT_WIN seconds to the decision (`Moments.linked`, the one reading of who is in which fight, R-464), else, where
# nobody of theirs is in a fight with ours (a run answered from a stand-off), their main team (`their_from` says which). The minute before reads the same
# players, those of them alive then: whether the energy at the decision was already so a minute before (SPEC 5, rule 4). Beside it, `team`: every living
# backline monk of each team, wherever he stands. It is what the answer to their split reads (R-688: by our own monks): on the defending side the
# defenders are the call itself, so their monks alone would read the energy of the answer chosen, not of the team choosing it. The like spots of the base res
# and of the decision to split at all (`res_spots`, `split_ticks`, records beside the plays too) carry the same reading.
BEFORE_S = 60                   # the minute before, as for every other factor of a decision (`jobs.FLAG_BEFORE_S`)
FIGHT_WIN = 4                   # who is in the fight is read over the 4 s to the decision, every other second as execution reads it (Claude's draft: one reading alone misses a player between casts)
FIGHT_STEP = 2
RES_READ_S = 20                 # a base res is a decision this long before the res (`jobs.RES_READ_S`, R-592)


def decision_second(p):
    """The second a play's decision arises: a flag play's one clock (`clock.anchor`, R-546: their runner's set-off, or our cap where we run again);
    a base res 20 s before the res (R-592, `res.early`); every other play its own start."""
    if p["play"] == "flag" and (p.get("clock") or {}).get("anchor") is not None: return int(p["clock"]["anchor"])
    if p["play"] == "base res": return int(p["t0"]) - RES_READ_S
    return int(p["t0"])


def _fight(M, X, foe, u):
    Y = set()
    for v in range(max(u - FIGHT_WIN, 0), u + 1, FIGHT_STEP):
        live = [a for a in X if M.AL[a][v]]
        for b in M.st.players[foe]:
            if b not in Y and M.AL[b][v] and any(M.linked(a, b, v) for a in live): Y.add(b)
    if Y: return sorted(Y), "fight"
    return [b for b in M.main_team(foe, u) if M.AL[b][u]], "main team"


def _read(E, M, tm, X, Y, u, how):
    side = lambda ids, v: {"monks": E.group(E.monks(ids), v), "midline": E.group(E.midline(ids), v)}
    team = lambda k, v: E.group(E.monks(M.st.players[k]), v)
    b = u - BEFORE_S
    return {"u": u, "own": side(X, u), "their": side(Y, u), "their_from": how, "ids": [E.monks(X), E.monks(Y)], "team": [team(tm, u), team(3 - tm, u)],
            "before": None if b < 0 else {"own": side(X, b), "their": side(Y, b), "team": [team(tm, b), team(3 - tm, b)]}}


def record(M, plays, ticks=(), spots=()):
    """{"ok", "plays": {play id: reading}, "split_ticks": {tick id: reading}, "res_spots": [reading, in the order of the spots]} for one match.
    `ok` False and nothing else where gvg.report has no energy for the match (R-672): every reading of it is blank, and the reports count such matches."""
    E = M.m.energy()
    if not E.ok: return {"ok": False}
    m, T = M.m, M.T
    agent = {(m.tag[m.team(a)], m.roles[a]): a for a in m.PL}
    out = {"ok": True, "plays": {}, "split_ticks": {}, "res_spots": []}
    for p in plays:
        tm, u = p["tm"], min(max(decision_second(p), 0), T)
        X = [agent[(m.tag[tm], r)] for r in (p.get("who") or ()) if (m.tag[tm], r) in agent] if p.get("split") is not None else []
        X = [a for a in X if M.AL[a][u]] or [a for a in M.main_team(tm, u) if M.AL[a][u]] or [a for a in M.st.players[tm] if M.AL[a][u]]
        Y, how = _fight(M, X, 3 - tm, u)
        out["plays"][p["id"]] = _read(E, M, tm, X, Y, u, how)
    for k in ticks:
        tm, u = k["tm"], min(int(k["t0"]), T)
        X = [a for a in M.main_team(tm, u) if M.AL[a][u]] or [a for a in M.st.players[tm] if M.AL[a][u]]
        Y, how = _fight(M, X, 3 - tm, u)
        out["split_ticks"][k["id"]] = _read(E, M, tm, X, Y, u, how)
    inb = M.base_zones() if spots else None
    for s in spots:                                       # the players in their base at the spot (as `jobs.res_spots` counts them), and the enemy players they fight
        tm, u = s["tm"], min(int(s["t"]), T)
        X = [a for a in M.st.players[tm] if M.AL[a][u] and M.P[a][u] and M._deep(a, u) in inb]
        Y, how = _fight(M, X, 3 - tm, u)
        out["res_spots"].append(_read(E, M, tm, X, Y, u, how))
    return out


# ---- the excuse (R-689, piece 3; R-666, the second aspect): "if the monks in a fight are all out of energy, there is no micro play regardless of how good
# the monks are to save the target", and "the reason a team may not kill in a fight (although rare) can be the midlines are out of energy". Three readings,
# all here, and one record kept beside the plays (`flag_cost[rid].excuse`: it tells no play and changes none):
#   `denial(m)`            every time an enemy skill took energy from a read player (R-685), with how much and how surely;
#   `Energy.account`       where a player's energy went over a stretch: what he had, what he spent on casts (a cast costs its energy whether it finished, was
#                          interrupted or was cancelled, R-680), what the enemy took, and what came back (the balance: regeneration, energy skills, and the
#                          error of gvg.report's estimate, which is why it is called what came back and not regeneration);
#   `excuse(M, plays)`     at every death, the backline monks in the dead player's fight a second before it: who was out (R-681: under 20), and each one's
#                          account of the minute before; and for every play with the job to kill (numbers up, the strong side, the main fight against
#                          no monk), met or not, the midline of the team in that fight: how long each was out (R-682: under 15), and his account.
# An excuse says what was so, never why a player died: a monk out of energy could not have saved him, and that is all it says. Whom a Mesmer drains, their
# monks or their midline, is execution (R-692): `execution.py` reads it from `denial` (`drain`, `drain_on_monks`).
# Energy denial as read (what is on real bars: Mind Wrack, Energy Surge, Energy Burn, Power Leak, Shame, Guilt, Malaise):
#   Energy Surge, Energy Burn   the energy lost is the damage on the target over 7 or 9 (the skills' own words): exact where the damage is a whole multiple; a
#                               lower bound where a prot cut the damage; nothing where no damage is seen (a target with no energy on the set he holds loses none).
#   Mind Wrack                  1 for every non-hex Mesmer skill its caster finishes on the hexed player while it is on him (the hex's stretch is in the replay).
#   Power Leak                  on a landed interrupt, the skill's energy loss at its caster's Domination Magic (gvg.report's attributes; unread where unknown),
#                               and no more than the most the player can have on the set he holds (gvg.report's upper bound a second before): not sure.
#   Shame, Guilt                where the hex triggered (`pressure.py`), "up to" the skill's figure, bounded the same way: not sure.
#   Malaise                     1 every 3 s it is on the player: not sure (he loses none at 0).
# A figure that is not sure is still the best reading of what was taken and counts in an account; the account says how much of it is not sure.
# Not read: Avatar of Lyssa (1 from nearby foes when a Dervish enchantment is lost), Ether Feast (on three bars in a hundred and forty matches).
ACCOUNT_S = 60                  # "the energy of the minute before", as every other minute before is 60 s
EXCUSE_READ_S = 1               # the monks' energy at a death is read this long before it: the last second they could still have acted for him
DENIAL_DAMAGE = {"Energy Surge": 7, "Energy Burn": 9}      # damage a point of energy lost, on the target
DENIAL_STEAL = ("Shame", "Guilt")
MALAISE_S = 3                   # -1 energy degeneration is a point every 3 s


def _base(n): return (n or "").replace(" (PvP)", "").replace(" PvP", "")


def denial(m):
    """[(second, by, on, skill, energy, sure)] for one match, in time order: energy an enemy skill took from a player. `energy` None where the skill landed and
    its size is not known (Power Leak with no attribute). `sure` False where the figure is a bound and not a count."""
    if getattr(m, "_denial", None) is not None: return m._denial
    from forensics import skilldata
    import movepower
    SK, PL, rid = skilldata(), set(m.PL), m.o["meta"]["id"]
    name = lambda sid: _base(m.sk(sid)) if sid is not None else None
    foe = lambda a, b: a in PL and b in PL and m.team(a) != m.team(b)
    En = m.energy()
    def at_rank(a, skill, what, b, t):
        """The skill's figure at its caster's Domination Magic, and no more than the most b can have on the set he holds a second before."""
        r = (movepower._ranks().get((rid, m.nm(a))) or {}).get("Domination Magic")
        v = next((x["values"] for x in (SK.get(skill) or {}).get("prog") or [] if x.get("name") == what), None)
        if r is None or not v: return None
        e, has = float(v[min(int(r), len(v) - 1)]), En.shown(b, t - 1)
        return e if has is None else min(e, float(has[1]))
    ev = sorted((e for e in m.o["ev"] if e[0] is not None), key=lambda e: e[0])
    dm = collections.defaultdict(list)                      # (by, on) -> [(tenth, amount)] of armour-ignoring damage
    for e in ev:
        if e[1] == "dm" and len(e) > 6 and e[6] == "armor_ignoring" and isinstance(e[5], (int, float)) and e[5] > 0 and foe(e[2], e[3]): dm[(e[2], e[3])].append((e[0], e[5]))
    wrack = collections.defaultdict(list)                   # (caster, target) -> the stretches his Mind Wrack was on that player
    out = []
    for x in m.o.get("effects") or []:
        if x[0] is None or x[2] != "h" or not foe(x[4], x[5]): continue
        nm, s0, s1 = name(x[3]), x[0] / 10, (x[1] / 10 if x[1] is not None else 1e9)
        if nm == "Mind Wrack": wrack[(x[4], x[5])].append((s0, s1))
        elif nm == "Malaise":
            u = s0 + MALAISE_S
            while u <= min(s1, s0 + 60): out.append((u, x[4], x[5], nm, 1.0, False)); u += MALAISE_S
    open_ = {}
    for e in ev:
        c, a = e[1], e[2]
        if c == "cs": open_[a] = (e[4], e[3])
        elif c in ("cx", "ir"): open_.pop(a, None)
        elif c == "cf" and a in open_:
            sid, b = open_.pop(a); nm = name(sid)
            if b is None or not foe(a, b): continue
            t = e[0] / 10
            if nm in DENIAL_DAMAGE:
                per = DENIAL_DAMAGE[nm]
                hits = [n for u, n in dm.get((a, b), ()) if e[0] - 1 <= u <= e[0] + 3 and n <= 10 * per + 1]      # its own damage; Mind Wrack's end can land in the same tenth and is larger
                whole = [n for n in hits if abs(n / per - round(n / per)) < 0.05]
                if whole: out.append((t, a, b, nm, float(round(max(whole) / per)), True))
                elif hits: out.append((t, a, b, nm, round(max(hits) / per, 1), False))
                else: out.append((t, a, b, nm, 0.0, False))
            sd = SK.get(m.sk(sid)) or SK.get(nm) or {}
            if sd.get("prof") == "Mesmer" and "Hex" not in (sd.get("type") or "") and any(s0 <= t <= s1 + 0.2 for s0, s1 in wrack.get((a, b), ())):
                out.append((t, a, b, "Mind Wrack", 1.0, True))
    for i in m.o.get("interrupts") or []:
        if i[0] is not None and name(i[2]) == "Power Leak" and foe(i[1], i[3]): out.append((i[0] / 10, i[1], i[3], "Power Leak", at_rank(i[1], "Power Leak", "Energy loss", i[3], i[0] / 10), False))
    if any(name(b) in DENIAL_STEAL for a in PL for b in (m.A[a].get("bar") or []) if b):
        import pressure
        for s0, s1, by, on, trig, nm in pressure.record(rid)["castprev"]:
            if trig and nm in DENIAL_STEAL and foe(by, on): out.append((s1, by, on, nm, at_rank(by, nm, "Energy stolen", on, s1), False))
    out.sort(key=lambda x: x[0])
    m._denial = out
    return out


def _cost(sd):
    try: return float(sd.get("energy") or 0)
    except (TypeError, ValueError): return 0.0


def _account(self, a, t0, t1):
    """Where a read player's energy went from t0 to t1 (seconds), on the scale: {s, from, to, spent, taken, by: {skill: energy}, unsure, came_back}. It starts
    at the first second from t0 he is read (he may have been dead) and is None where he is not read at t1 or for no 10 s of the stretch.
    `spent` is the listed cost of every cast he started (R-680); a cost cut by a skill shows in what came back. `taken` is every figure of `denial`,
    `unsure` the part of it that is a bound and not a count. `came_back` is the balance, to - from + spent + taken: regeneration, energy skills, and
    the error of the estimate."""
    y = self.at(a, t1)
    u = next((v for v in range(int(t0), int(t1) - 9) if self.at(a, v)), None)
    if y is None or u is None: return None
    x = self.at(a, u)
    if getattr(self, "_cs", None) is None:
        from forensics import skilldata
        SK = skilldata(); self._cs = collections.defaultdict(list)
        for e in self.m.o["ev"]:
            if e[0] is not None and e[1] == "cs" and e[2] in self._k and self._k[e[2]] is not None:
                c = _cost(SK.get(self.m.sk(e[4])) or SK.get(_base(self.m.sk(e[4]))) or {}) if e[4] is not None else 0.0
                if c: self._cs[e[2]].append((e[0] / 10, c))
        self._den = collections.defaultdict(list)
        for d in denial(self.m): self._den[d[2]].append(d)
    spent = sum(c for t, c in self._cs.get(a, ()) if u <= t < t1)
    by, taken, unsure = collections.Counter(), 0.0, 0.0
    for t, src, _, nm, e, ok in self._den.get(a, ()):
        if not (u <= t < t1) or e is None: continue
        by[nm] += e; taken += e
        if not ok: unsure += e
    return {"s": int(t1) - u, "from": x["mid"], "to": y["mid"], "spent": round(spent, 1), "taken": round(taken, 1), "unsure": round(unsure, 1),
            "by": {k: round(v, 1) for k, v in by.items()}, "came_back": round(y["mid"] - x["mid"] + spent + taken, 1)}

Energy.account = _account


def _mates(M, a, u):
    """The living players of a's team in his fight in the FIGHT_WIN seconds to u, himself among them (`Moments.linked`, the one reading of it, R-464)."""
    tm, X = M.m.team(a), {a}
    for v in range(max(u - FIGHT_WIN, 0), u + 1, FIGHT_STEP):
        if not M.AL[a][v]: continue
        for b in M.st.players[tm]:
            if b not in X and M.AL[b][v] and M.linked(a, b, v): X.add(b)
    return sorted(X)


def kill_job(p):
    """A play whose job was to kill: the test is that more of theirs die than of ours (numbers up, the strong side, the main fight while a split is out)."""
    return any(k.startswith("more of theirs die") for k in (p.get("tests") or {}))


def excuse(M, plays):
    """{"ok", "deaths": [...], "kill_jobs": [...]} for one match (see above). `ok` False and nothing else where the match has no energy (R-672).
    `kill_jobs` holds every play with the job to kill, met or not (`met`): the excuse is said of those not met, the others are what they are set beside."""
    E = M.m.energy()
    if not E.ok: return {"ok": False}
    m, T = M.m, M.T
    row = lambda b, u, t0: {"who": m.roles[b], **{k: v for k, v in (E.at(b, u) or {}).items() if k in ("lo", "hi", "mid", "out")}, "account": E.account(b, t0, u)}
    out = {"ok": True, "deaths": [], "kill_jobs": []}
    for tm in M.st.teams:
        for a in M.st.players[tm]:
            for td in M.st.death_times.get(a, ()):
                if td >= M.over: continue                      # the deaths the match ends in are no deaths of the reading (`Moments.over`)
                u = max(int(td) - EXCUSE_READ_S, 0)
                while u > 0 and not M.AL[a][u]: u -= 1
                if int(td) - u > 4: continue                   # not seen alive in the seconds before it: nothing to read
                rows = [r for r in (row(b, u, u - ACCOUNT_S) for b in E.monks(_mates(M, a, u))) if "mid" in r]
                n, o = len(rows), sum(r["out"] == "yes" for r in rows)
                out["deaths"].append({"t": int(td), "u": u, "tm": tm, "team": m.tag[tm], "who": m.roles[a], "kind": E.kind(a), "n": n, "out": o,
                                      "maybe": sum(r["out"] == "maybe" for r in rows), "all_out": bool(n) and o == n, "monks": rows})
    agent = {(m.tag[m.team(a)], m.roles[a]): a for a in m.PL}
    for p in plays:
        if not kill_job(p): continue
        tm, t0, t1 = p["tm"], min(int(p["t0"]), T), min(int(p["t1"]), T)
        X = [agent[(m.tag[tm], r)] for r in (p.get("who") or ()) if (m.tag[tm], r) in agent]
        X = [a for a in X if M.AL[a][t0]] or [a for a in M.main_team(tm, t0) if M.AL[a][t0]]
        rows = []
        for b in E.midline(X):
            R = [x for x in (E.at(b, v) for v in range(t0, t1 + 1, FIGHT_STEP)) if x]
            if not R: continue
            rows.append({"who": m.roles[b], "read_s": FIGHT_STEP * len(R), "out_s": FIGHT_STEP * sum(x["out"] == "yes" for x in R), "maybe_s": FIGHT_STEP * sum(x["out"] == "maybe" for x in R),
                         "low": min(x["mid"] for x in R), "account": E.account(b, max(t1 - ACCOUNT_S, 0), t1)})
        out["kill_jobs"].append({"id": p["id"], "t0": t0, "t1": t1, "tm": tm, "team": m.tag[tm], "play": p["play"], "side": p.get("side"), "met": bool(p.get("met")), "n": len(rows),
                               "out": sum(2 * r["out_s"] >= r["read_s"] for r in rows), "midline": rows})
    out["deaths"].sort(key=lambda d: (d["t"], d["tm"]))
    return out


def _say_account(c):
    if not c: return "the minute before is not read"
    took = ", ".join(f"{k} {v:.0f}" for k, v in sorted(c["by"].items(), key=lambda kv: -kv[1]) if v >= 0.5)
    return (f"over the {c['s']} s before he went from {c['from']:.0f} to {c['to']:.0f}: spent {c['spent']:.0f} on casts, had {c['taken']:.0f} taken"
            + (f" ({took}" + (f"; {c['unsure']:.0f} of it not sure" if c["unsure"] >= 1 else "") + ")" if took else "") + f", and {c['came_back']:.0f} came back")


def say_death(d):
    """A death's excuse as a sentence a player would use: what was so, never why he died."""
    f = lambda t: f"{t // 60}:{t % 60:02d}"
    if not d["n"]: return f"{f(d['t'])} {d['team']} {d['who']} dies with no backline monk of his team in his fight."
    word = {"yes": "out", "maybe": "possibly out", "no": ""}
    who = "; ".join(f"{r['who']} at {r['mid']:.0f}" + (f" ({word[r['out']]})" if word[r["out"]] else "") for r in d["monks"])
    head = ("every monk in his fight was out of energy" if d["all_out"] else f"{d['out']} of the {d['n']} monks in his fight {'was' if d['out'] == 1 else 'were'} out of energy" if d["out"]
            else "no monk in his fight was out of energy")
    tail = " ".join(f"{r['who']}, {_say_account(r['account'])}." for r in d["monks"] if r["out"] != "no")
    return f"{f(d['t'])} {d['team']} {d['who']} dies: {head} ({who})." + (" " + tail if tail else "")


def say_no_kill(r):
    f = lambda t: f"{t // 60}:{t % 60:02d}"
    head = f"{f(r['t0'])} to {f(r['t1'])} {r['team']} does not kill: "
    if not r["n"]: return head + "no midline player of its fight is read."
    outs = [x for x in r["midline"] if x["out_s"]]
    if not outs: return head + f"none of its {r['n']} midline players was out of energy (the lowest at {min(x['low'] for x in r['midline']):.0f})."
    rest = r["n"] - len(outs)
    return (head + "; ".join(f"{x['who']} was out for {x['out_s']} of {x['read_s']} s (lowest {x['low']:.0f}; {_say_account(x['account'])})" for x in outs)
            + (f"; the other {rest} midline {'was' if rest == 1 else 'were'} not out." if rest else "."))


# ---- the checks of the record: does it read as any player knows (a report; nothing is fitted and nothing reads it)
FIRE = 150                      # a team that took this much in hits in 10 s is under fire; one that took nothing is at rest (for the checks only)

def _check(rid):
    from replaylib import Match
    try:
        m = Match.from_branch(rid); E = m.energy()
    except Exception as e: return {"rid": rid, "error": f"{type(e).__name__}: {e}"}
    if not E.ok: return {"rid": rid, "ok": False}
    end = int(max(T["t"][-1] for T in m.TR.values() if T.get("t")) / 10)
    PL = set(m.PL)
    hit = {1: collections.Counter(), 2: collections.Counter()}; died = {1: [], 2: []}
    for e in m.o.get("ev") or []:
        if e[0] is None: continue
        if e[1] == "dm" and e[3] in PL and e[2] in PL and m.team(e[2]) != m.team(e[3]) and len(e) > 5 and isinstance(e[5], (int, float)): hit[m.team(e[3])][int(e[0] / 10)] += e[5]
        elif e[1] == "dt" and e[2] in PL: died[m.team(e[2])].append(e[0] / 10)
    out = {"rid": rid, "ok": True, "rows": [], "time": collections.Counter()}
    for tm in (1, 2):
        ids = [a for a in m.PL if m.team(a) == tm]
        mk, md = E.monks(ids), E.midline(ids)
        for t in range(60, end - 20, 10):
            g = E.group(mk, t)
            for a in mk + md:
                x = E.at(a, t)
                if x: out["time"][(E.kind(a), x["out"])] += 1
            if not g or not g["n"]: continue
            g2 = E.group(mk, t + 10)
            took = sum(hit[tm][u] for u in range(t, t + 10))
            out["rows"].append((g["mean"], g["low"], g["n"], (g2["mean"] - g["mean"]) if g2 and g2["n"] == g["n"] else None, took, int(any(t < d <= t + 20 for d in died[tm]))))
    out["time"] = {f"{k[0]}|{k[1]}": v for k, v in out["time"].items()}
    return out


if __name__ == "__main__":
    import sys, json, subprocess
    a = sys.argv[1:]
    if a and a[0] == "cover":
        import multiprocessing, common
        ids = common.replay_ids()
        with multiprocessing.Pool(int(a[a.index("--jobs") + 1]) if "--jobs" in a else 2) as pool: res = pool.map(_check, ids, chunksize=8)
        bad = [r for r in res if "error" in r]; ok = [r for r in res if r.get("ok")]
        print(f"{len(ids)} counted matches: {len(ok)} with gvg.report's energy, {len(res) - len(ok) - len(bad)} without (blank, R-672), {len(bad)} that could not be read")
        rows = [x for r in ok for x in r["rows"]]
        tm = collections.Counter()
        for r in ok: tm.update(r["time"])
        for k in ("monk", "midline"):
            tot = sum(v for kk, v in tm.items() if kk.startswith(k + "|")) or 1
            print(f"  a {k} player is out (under {OUT_MONK if k == 'monk' else OUT_MIDLINE} on the double high scale): for certain {100 * tm[k + '|yes'] / tot:.1f}% of his time alive, possibly {100 * tm[k + '|maybe'] / tot:.1f}%")
        mean = lambda v: sum(v) / len(v) if v else float("nan")
        print(f"  a team's backline monks, read every 10 s from 1:00 ({len(rows):,} readings): average {mean([x[0] for x in rows]):.1f}, the lowest monk {mean([x[1] for x in rows]):.1f}")
        fire, rest = [x[3] for x in rows if x[3] is not None and x[4] >= FIRE], [x[3] for x in rows if x[3] is not None and x[4] == 0]
        print(f"  E1, energy falls under fire and comes back at rest: over the next 10 s a team's monks change by {mean(fire):+.1f} when it takes {FIRE} or more in hits ({len(fire):,}) and by {mean(rest):+.1f} when it takes none ({len(rest):,}): {'HOLDS' if mean(fire) < 0 < mean(rest) else 'DOES NOT HOLD'}")
        print("  E2, a death on the team in the next 20 s, by its monks' average and by its lowest monk:")
        for name, i in (("average", 0), ("lowest monk", 1)):
            cells = []
            for lo_, hi_ in ((0, 20), (20, 30), (30, 40), (40, 50), (50, 60), (60, 200)):
                v = [x[5] for x in rows if lo_ <= x[i] < hi_]
                cells.append(f"{lo_}-{hi_ if hi_ < 200 else ''}: {100 * mean(v):.0f}% ({len(v):,})" if v else f"{lo_}-{hi_}: none")
            print(f"     {name:12} " + "; ".join(cells))
        for r in bad[:10]: print("  " + r["rid"][:8], r["error"])
        sys.exit(1 if bad else 0)
    elif len(a) >= 2 and a[1] == "excuse":
        from replaylib import Match
        from state import GameState
        from scoreboard import Scoreboard
        import common, jobs, moments
        idx = json.loads(subprocess.check_output(["git", "-C", common.REPO, "show", "origin/replays:index.json"]))["matches"]
        rid = next(r for r in idx if r.startswith(a[0]))
        st = GameState(Match.from_branch(rid))
        M = moments.Moments(st, Scoreboard(st))
        P = jobs.plays(M, M.records())
        for p in P: p.setdefault("id", f"{p['play']}-{p['tm']}-{p['t0']}")
        X = excuse(M, P)
        print(" v ".join(idx[rid]["teams"]), "| the excuse (R-666): what was so at each death and each failure to kill, never why")
        if not X["ok"]: print("  energy is not in gvg.report's record of this match: blank (R-672)"); sys.exit()
        frm = (lambda v: int(v.split(":")[0]) * 60 + int(v.split(":")[1]))(a[2]) if len(a) > 2 else 0
        for t, line in sorted([(d["t"], say_death(d)) for d in X["deaths"]] + [(r["t0"], say_no_kill(r)) for r in X["kill_jobs"] if not r["met"]]):
            if t >= frm: print("  " + line)
    elif a:
        from replaylib import Match
        import common
        idx = json.loads(subprocess.check_output(["git", "-C", common.REPO, "show", "origin/replays:index.json"]))["matches"]
        rid = next(r for r in idx if r.startswith(a[0]))
        m = Match.from_branch(rid); E = m.energy()
        print(" v ".join(idx[rid]["teams"]), "| energy", "read" if E.ok else "not in gvg.report's record: blank (R-672)")
        if E.ok:
            end = int(max(T["t"][-1] for T in m.TR.values() if T.get("t")) / 10)
            for b in sorted(m.PL, key=lambda b: (m.team(b), m.A[b].get("slot") or 0)):
                if E.kind(b) is None: continue
                xs = [x for x in (E.at(b, t) for t in range(60, end, 10)) if x]
                if not xs: continue
                mids = sorted(x["mid"] for x in xs)
                print(f"  {m.role(b):20} {E.kind(b):8} middle {mids[len(mids) // 2]:5.1f}  lowest tenth {mids[len(mids) // 10]:5.1f}  out for certain {100 * sum(x['out'] == 'yes' for x in xs) / len(xs):4.1f}%  possibly {100 * sum(x['out'] == 'maybe' for x in xs) / len(xs):4.1f}%  bounds within 2: {100 * sum(x['hi'] - x['lo'] <= 2 for x in xs) / len(xs):3.0f}%")
    else: print(__doc__)
