"""The Guild Lord: its health over the match, whether it is exposed, and what that does to the win condition.

28 of the first 30 replays ended with a Lord kill, so the Lord is the real end point of almost every match. The replay
has no Lord health, so it is rebuilt from the damage and healing recorded on the Lord:
- max health: the Lord's recorded max health (1,680) plus 1% per morale boost its team has had (Denning; up to 1,848);
- natural regeneration: health comes back once the Lord has taken no damage for REGEN_DELAY s, at a rate MEASURED
  from the Lord deaths (benchmarks.py regen: the rate that best puts the rebuilt health at 0 when Lords die). Nothing
  is guessed beyond the delay, which is the game's out-of-combat rule and can be corrected;
- exposed: its Bodyguard and both knights are dead (pit roster from integrity.ROSTER);
- a team whose Lord damage was not observed (integrity.lord_damage_unobserved) gets None, not a number.

In code: L = LordState(st); L.health(team, t) -> share of max (0..1) or None; L.exposed(team, t); L.max_hp(team, t);
         L.damage_net(team, t, window) -> damage minus healing on the team's Lord in the last window seconds."""
import bisect, json, os
from common import REPO, BOOST_EVERY

REGEN_DELAY = 5            # seconds without damage before natural regeneration starts (game rule; correctable)
BOOST_HP = 0.01            # +1% Lord max health per boost (Denning), up to MAX_BOOSTS
MAX_BOOSTS = 10
_REGEN = None


def regen_rate():
    """Measured Lord regeneration (health per second out of combat), from data/benchmarks/lord_regen.json."""
    global _REGEN
    if _REGEN is None:
        try: _REGEN = json.load(open(os.path.join(REPO, "data", "benchmarks", "lord_regen.json")))["rate"]
        except (OSError, ValueError, KeyError): _REGEN = None
    return _REGEN


def boosts(st, tm, t):
    """Boosts team tm had by second t: every full BOOST_EVERY seconds holding the stand."""
    n, caps = 0, st.caps + [(1e9, None)]
    for (c, who), (nxt, _) in zip(caps, caps[1:]):
        if who == tm and c < t: n += int((min(nxt, t) - c) // BOOST_EVERY)
    return min(n, MAX_BOOSTS)


class LordState:
    def __init__(self, st, rate=None):
        self.st, m = st, st.m
        self.rate = regen_rate() if rate is None else rate
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
        self._series = {tm: self._build(tm) for tm in (1, 2)}

    def max_hp(self, tm, t):
        return self.base_hp[tm] * (1 + BOOST_HP * boosts(self.st, tm, t))

    def _build(self, tm):
        """[(t, health)] after every event, with regeneration between events (None if the rate isn't measured yet)."""
        hp, last_dmg, t0, out = self.base_hp[tm], -1e9, 0.0, []
        for t, v in self.ev[tm] + [(self.st.end + 1, 0)]:
            hp = self._regen(tm, hp, t0, t, last_dmg)
            mx = self.max_hp(tm, t)
            hp = max(0.0, min(mx, hp + v))
            if v < 0: last_dmg = t
            t0 = t; out.append((t, hp, last_dmg))
        return out

    def _regen(self, tm, hp, t0, t1, last_dmg):
        if not self.rate: return hp
        start = max(t0, last_dmg + REGEN_DELAY)
        return min(self.max_hp(tm, t1), hp + self.rate * (t1 - start)) if t1 > start else hp

    def health_abs(self, tm, t):
        if 3 - tm in self.unobserved: return None
        if self.dead[tm] is not None and t >= self.dead[tm]: return 0.0
        S = self._series[tm]
        i = bisect.bisect_right([x[0] for x in S], t) - 1
        if i < 0: return self.max_hp(tm, t)
        t0, hp, last = S[i]
        return self._regen(tm, hp, t0, t, last)

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
