"""The Guild Lord: its health over the match, whether it is exposed, and what that does to the win condition.

28 of the first 30 replays ended with a Lord kill, so the Lord is the real end point of almost every match. The replay
has no Lord health, so it is rebuilt second by second from the damage and healing recorded on the Lord:
- max health: the Lord's recorded max health (1,680) plus 1% per morale boost its team has had (Denning; up to 1,848);
- Amulet of Protection (knowledge/guild-lord.md): health lost per second is capped, 25 at 0:00 rising 11.6% a minute to
  300 at 12:00; damage over the cap is healed back. Whether gvg.report's recorded damage is before or after the cap is
  measured (benchmarks.py regen tries both); first reading: after (applying the cap again made the rebuilt health at
  death much worse, 629 against 332), so the cap is not applied again;
- regeneration (Denning): 10 health per second always (the wiki's +5 pips), plus out-of-combat regeneration once the
  Lord hasn't been hit for a few seconds, starting at +2 per second and rising to +10. The delay and how fast it rises
  are MEASURED (benchmarks.py regen: the pair that best puts the rebuilt health at 0 when Lords die, without any
  surviving Lord reaching 0); until measured, REGEN_DELAY and RAMP_S below are used;
- healing recorded on the Lord (Bodyguard's Oath of Healing, players) is added as recorded;
- exposed: its Bodyguard and both knights are dead (pit roster from integrity.ROSTER);
- a team whose Lord damage was not observed (integrity.lord_damage_unobserved) gets None, not a number.
Entourage (less damage while the pit NPCs outnumber the attackers) is not modelled: the recorded damage is taken as
applied.

In code: L = LordState(st); L.health(team, t) -> share of max (0..1) or None; L.exposed(team, t); L.max_hp(team, t);
         L.damage_net(team, t, window) -> damage minus healing on the team's Lord in the last window seconds."""
import json, math, os
from common import REPO, BOOST_EVERY

BASE_REGEN = 10            # health per second, always (Denning)
EXTRA_START, EXTRA_MAX = 2, 10    # out-of-combat regeneration: starts at +2, caps at +10 per second (Denning)
REGEN_DELAY, RAMP_S = 5, 2        # seconds unhit before it starts; seconds per +2 step (measured by benchmarks.py regen)
BOOST_HP = 0.01            # +1% Lord max health per boost (Denning), up to MAX_BOOSTS
MAX_BOOSTS = 10
_FIT = None


def measured():
    """(delay, ramp seconds, amulet cap applied) from data/benchmarks/lord_regen.json, else the defaults."""
    global _FIT
    if _FIT is None:
        try:
            o = json.load(open(os.path.join(REPO, "data", "benchmarks", "lord_regen.json")))
            _FIT = (o["delay_s"], o["ramp_s"], o["amulet_cap_applied"])
        except (OSError, ValueError, KeyError): _FIT = (REGEN_DELAY, RAMP_S, False)
    return _FIT


def amulet_cap(t):
    """Most health the Lord can lose in one second at match second t (Amulet of Protection)."""
    return min(300.0, 25.0 * (1.116 ** (t / 60)))


def extra_regen(unhit_s, delay, ramp):
    if unhit_s < delay: return 0.0
    return min(EXTRA_MAX, EXTRA_START + 2 * int((unhit_s - delay) // ramp))


def boosts(st, tm, t):
    """Boosts team tm had by second t: every full BOOST_EVERY seconds holding the stand."""
    n, caps = 0, st.caps + [(1e9, None)]
    for (c, who), (nxt, _) in zip(caps, caps[1:]):
        if who == tm and c < t: n += int((min(nxt, t) - c) // BOOST_EVERY)
    return min(n, MAX_BOOSTS)


def simulate(ev, base, end, delay, ramp, max_hp=None, floor=True, cap=False):
    """Health at every whole second 0..end from [(t, -damage or +heal)]; max_hp(t) defaults to base."""
    dmg = [0.0] * (int(end) + 2); heal = [0.0] * (int(end) + 2)
    for t, v in ev:
        i = min(int(t), int(end) + 1)
        if v < 0: dmg[i] -= v
        else: heal[i] += v
    hp, last_hit, out = float(base), -1e9, []
    for s in range(int(end) + 1):
        mx = max_hp(s) if max_hp else base
        loss = min(dmg[s], amulet_cap(s)) if cap else dmg[s]
        if dmg[s] > 0: last_hit = s
        hp = hp - loss + heal[s] + BASE_REGEN + extra_regen(s - last_hit, delay, ramp)
        hp = min(mx, hp)
        if floor: hp = max(0.0, hp)
        out.append(hp)
    return out


class LordState:
    def __init__(self, st, delay=None, ramp=None, cap=None):
        self.st, m = st, st.m
        d0, r0, c0 = measured()
        self.delay, self.ramp, self.cap = (delay or d0), (ramp or r0), (c0 if cap is None else cap)
        self.lord = {a.get("team"): i for i, a in enumerate(m.A) if a.get("npc") == "guild_lord"}
        rec = {l["team"]: l.get("max_hp") for l in m.o.get("lords", [])}
        self.base_hp = {tm: rec.get(tm) or 1680 for tm in (1, 2)}
        self.unobserved = set(m.o.get("integrity", {}).get("lord_damage_unobserved", []))   # attacking teams
        self.ev = {tm: [] for tm in (1, 2)}         # (t, -damage or +heal) on tm's Lord
        for r in m.o["ev"]:
            if r[1] in ("dm", "hl") and r[3] in self.lord.values() and r[5]:
                tm = m.A[r[3]].get("team")
                if tm in self.ev: self.ev[tm].append((r[0] / 10, -r[5] if r[1] == "dm" else r[5]))
        for tm in self.ev: self.ev[tm].sort()
        self.dead = {tm: next((r[0] / 10 for r in m.o["ev"] if r[1] == "dt" and r[2] == self.lord.get(tm)), None) for tm in (1, 2)}
        self._hp = {tm: simulate(self.ev[tm], self.base_hp[tm], st.end, self.delay, self.ramp, lambda s, tm=tm: self.max_hp(tm, s), cap=self.cap)
                    for tm in (1, 2)}

    def max_hp(self, tm, t):
        return self.base_hp[tm] * (1 + BOOST_HP * boosts(self.st, tm, t))

    def health_abs(self, tm, t):
        if 3 - tm in self.unobserved: return None
        if self.dead[tm] is not None and t >= self.dead[tm]: return 0.0
        S = self._hp[tm]
        return S[min(max(int(t), 0), len(S) - 1)]

    def health(self, tm, t):
        h = self.health_abs(tm, t)
        return None if h is None else round(h / self.max_hp(tm, t), 3)

    def damage_net(self, tm, t, window=60):
        if 3 - tm in self.unobserved: return None
        return round(-sum(v for tt, v in self.ev[tm] if t - window < tt <= t))

    def exposed(self, tm, t):
        """Bodyguard and both knights dead (the Lord can be hit without its guards)."""
        st = self.st
        guards = [a for a, v in st.geo.npcs.items() if v["team"] == tm and v.get("pit") and v["kind"] in ("bodyguard", "knight")]
        return int(bool(guards) and all(st.npc_dead.get(a, 1e9) <= t for a in guards))
