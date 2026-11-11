"""Decision moments for families 1 to 3 (docs/REDESIGN.md step 2, items 2.3 to 2.7): departures, event triggers, the
scenario at the trigger, the call read as an allocation, and forced reads. A draft until the golden moments agree
(R-303); the old decision kinds (decisions.py) keep running beside it.

Departure (R-296): a player leaves the main group, the res shrine or the base. Read from the moment of leaving and
  labelled afterwards by what it became within PURPOSE_S, or earlier on a pickup or on entering the enemy base:
  run (picks up the own flag, or waits at the own flag spawn), split (enters the enemy base, or is still deep on the
  enemy side away from both mains), collapse (goes home while enemy players are in the base), retreat (goes home with
  nobody there), return (back in the main group), other. A player the main group walked away from in his own base has
  not left: his leave is the moment he walks out of the base (or picks up the flag there).
Trigger (one record a moment, per deciding team):
  1 Flag decision     an enemy player leaves to run; the enemy's boost is BOOST_WARN_S away; an own player picks up a
                      fresh flag. Triggers within MERGE_S are one moment.
  2 Answer to a split an enemy group leaves and turns out to be a split (the moment its first player leaves).
  3 Numbers advantage numbers differ where the mains meet, for NUMBERS_MIN_S or more: one record for the side that is
                      up and one for the side that is down (R-301).
Scenario: the version of the decision, from the state at the trigger (a short key; the continuous state rides along
  for finding similar cases).
Call (R-294): where the players stand READ_FROM to READ_TO seconds after the trigger: runners, where the rest are
  (more than AREA_SHARE of the living main group inside a labelled area, Denning 2026-11-10), defenders and their mix.
  Never from damage or deaths. "At the footmen" is read from Denning's Footman labels and the measured reach
  (hallmap.py, R-307), only while a footman is alive and only on halls that have them (R-311).
Forced (2.7): a player of the deciding team died inside the read window; kept apart.

Usage:  python3 moments.py <report id> [family]      the match's moments in order
        python3 moments.py all <out.json> [--jobs N]  every counted match, compact (for counts and golden picks)
        python3 moments.py counts <out.json>          cases by family, scenario and call
In code: Moments(st, sb).records() -> list of dicts."""
import collections, json, math, statistics, sys
from common import (READ_FROM, READ_TO, AREA_SHARE, PURPOSE_S, LEAVE_MIN_S, HOME_WAIT_S, SPAWN_R, GROUP_LEAVE_S, MEET_R,
                    NUMBERS_MIN_S, MERGE_S, BOOST_WARN_S, FLAGGER_R, SPLIT_FAR, BOOST_EVERY, SERIOUS_CARRY_S, FIGHT_LINK)
from state import d

HOME, THEIRS = ("own pit", "own base"), ("enemy pit", "enemy base")
FAMILY = {1: "Flag decision", 2: "Answer to a split", 3: "Numbers advantage"}
TRIGGER_WORDS = {"enemy_run": "an enemy player leaves to run a flag", "boost": f"the enemy's boost is {BOOST_WARN_S} s away",
                 "own_flag": "an own player picks up a fresh flag"}
PLACE_WORDS = {"stand": "at the stand", "footmen": "at the footmen", "own pit": "in the own pit", "own base": "in the own base",
               "enemy pit": "in the enemy pit", "enemy base": "in the enemy base", "backside": "on the backside",
               "push side": "on the push side", "own half": "spread over the own half", "enemy half": "spread over the enemy half",
               "spread": "spread out", "nobody": "nobody"}
REST_CALL = {"stand": "stay at the stand", "footmen": "fall to footmen", "own pit": "retreat to the pit",
             "own base": "fall back into the base"}


class Moments:
    def __init__(self, st, sb=None):
        self.st, self.m, self.hall, self.sb, self.T = st, st.m, st.hall, sb, st.end
        m, R = st.m, range(st.end + 1)
        self.P, self.AL = {}, {}
        for a in m.PL:
            ps, al = [], []
            for t in R:
                p, s = st.pos(a, t); ps.append(p); al.append(bool(p) and m.alive(s))
            self.P[a], self.AL[a] = ps, al
        self.MAIN = {tm: [frozenset(st.main_group(tm, t)) for t in R] for tm in st.teams}
        self._z = {}
        flags = m.o.get("flags", [])
        self.pick = collections.defaultdict(list)
        for t, typ, a, *_ in flags:
            if typ == "flag_picked_up" and a in self.P: self.pick[a].append(t / 10)
        self.carry = collections.defaultdict(list)
        for c in st.carries: self.carry[c["a"]].append((c["s"], c["e"]))
        self.spawn = {tm: (self.hall.spawn.get(st.side[tm]) if self.hall and tm in st.side else None) or st.geo.spawn.get(tm) for tm in st.teams}
        self.foot_dead = collections.defaultdict(list)       # team -> times its footmen died
        for r in m.o["ev"]:
            if r[1] == "dt" and isinstance(r[2], int) and r[2] < len(m.A) and m.A[r[2]].get("npc") == "footman":
                self.foot_dead[m.A[r[2]].get("team")].append(r[0] / 10)
        self.legs = self._departures()
        self.by_player = collections.defaultdict(list)
        for g in self.legs: self.by_player[g["a"]].append(g)

    # ---- basics
    def zone(self, a, t):
        k = (a, t)
        if k not in self._z: self._z[k] = self.st.zone(a, t)
        return self._z[k]

    def carrying(self, a, t): return any(s <= t <= e for s, e in self.carry.get(a, ()))
    def away(self, a, t, tm): return self.AL[a][t] and a not in self.MAIN[tm][t]
    def at_home(self, a, t, tm):
        return self.zone(a, t) in HOME or d(self.P[a][t], self.spawn[tm]) < SPAWN_R

    def in_base_of(self, tm, t):
        """Enemy players standing in tm's base or pit, not carrying a flag."""
        return [b for b in self.st.players[3 - tm] if self.AL[b][t] and self.zone(b, t) in THEIRS and not self.carrying(b, t)]

    def footmen_alive(self, tm, t):
        if not self.hall or tm not in self.st.side: return 0
        return len(self.hall.footmen[self.st.side[tm]]) - sum(1 for x in self.foot_dead.get(tm, ()) if x <= t)

    def boost_worth(self, tm, t):
        """What the next boost would give team tm (R-333): a boost adds 10 morale to each player up to +10, so a team
        at full morale gains nothing and a team deep in death penalty gains most, in proportion to the health it has
        left. points = morale the boost would add over the eight players; health = the gain in maximum health as a
        share of what they have now, averaged; dp_players = players carrying death penalty."""
        ms = [self.st.morale(a, t) for a in self.st.players[tm]]
        gain = [min(10, 10 - x) for x in ms]
        return {"points": sum(gain), "health": round(sum(g / (100 + x) for g, x in zip(gain, ms)) / max(len(ms), 1), 3),
                "dp_players": sum(1 for x in ms if x < 0)}

    def centre(self, g, t):
        pts = [self.P[a][t] for a in g if self.AL[a][t]]
        return (statistics.fmean(p[0] for p in pts), statistics.fmean(p[1] for p in pts)) if pts else None

    def where(self, g, t, tm):
        """Where a group is: the place more than AREA_SHARE of its living players stand in (smaller places first)."""
        g = [a for a in g if self.AL[a][t]]
        if not g: return "nobody"
        z = collections.Counter(self.zone(a, t) for a in g)
        sh = lambda *k: sum(z[x] for x in k) / len(g)
        if sh("own pit") > AREA_SHARE: return "own pit"
        if sh("stand") > AREA_SHARE: return "stand"
        if self.footmen_alive(tm, t) > 0:
            f = self.hall.at_footmen([self.P[a][t] for a in g], self.st.side[tm])
            if f is not None and f > AREA_SHARE: return "footmen"
        if sh(*HOME) > AREA_SHARE: return "own base"
        if sh("enemy pit") > AREA_SHARE: return "enemy pit"
        if sh(*THEIRS) > AREA_SHARE: return "enemy base"
        if sh("backside") > AREA_SHARE: return "backside"
        if sh("push side") > AREA_SHARE: return "push side"
        if sh("backside", *HOME) > AREA_SHARE: return "own half"
        if sh("push side", *THEIRS) > AREA_SHARE: return "enemy half"
        return "spread"

    # ---- every fight on the map, with its own numbers (a draft of the theatre layer, R-341)
    def fights(self, t):
        """The groups on the map at second t: living players of both teams linked within FIGHT_LINK, each with its
        numbers by team and where it stands (the place of team 1's players, else team 2's, named by whose ground it
        is). Denning reads a match this way ("3v4 in the back door", "7v7 at the stand")."""
        st, m = self.st, self.m
        live = [a for a in m.PL if self.AL[a][t]]
        gs = []
        for a in live:
            hit = [g for g in gs if any(d(self.P[a][t], self.P[b][t]) < FIGHT_LINK for b in g)]
            gs = [g for g in gs if g not in hit] + [[a] + [x for g in hit for x in g]]
        out = []
        for g in gs:
            n = {tm: [a for a in g if m.team(a) == tm] for tm in st.teams}
            z = collections.Counter(self.hall.place(self.P[a][t]) for a in g)
            kind, side = max(z, key=lambda k: (z[k], str(k)))
            out.append({"n": {tm: len(n[tm]) for tm in st.teams}, "ids": {tm: frozenset(n[tm]) for tm in st.teams},
                        "who": {tm: sorted(m.roles[a] for a in n[tm]) for tm in st.teams},
                        "kind": kind, "side": side, "place": self.place_words(kind, side),
                        "flag": [a for a in g if self.carrying(a, t)]})
        return sorted(out, key=lambda x: -(x["n"][1] + x["n"][2]))

    def place_words(self, kind, side):
        tag = {v: self.m.tag[k] for k, v in self.st.side.items()}.get(side)
        if kind == "stand": return "the flag stand"
        if kind == "greater stand": return "the greater stand area"
        if kind == "field": return f"the field on {tag}'s side"
        return f"{tag}'s {kind}"

    # ---- the flag, one life at a time
    def flag_lives(self):
        """A team has one flag (Denning, R-339). Its life runs from the pickup at the own flag spawn to the capture, or
        to its return to the spawn (not recorded: read from the next pickup being at the spawn again). Each life is
        labelled afterwards by what the players went on to do (R-340):
          single run          one player carried it in;
          hand-off to cap     it changed hands and nobody went back for the next flag;
          double run, half    a player who handed it off was back toward the spawn at the capture and took the next flag;
          double run, full    a player who never carried it was back toward the spawn at the capture and took the next.
        A pickup dropped within SERIOUS_CARRY_S without a capture is not a carry (R-339). "Back toward the spawn at the
        capture" = nearer the own spawn than the stand, walked. Not yet read: a hand-off to hold (the receiver keeps
        the flag near the fight, R-340 form 2), and whether the next runner went back for the flag or was already
        home (back from a split, defending, resurrected): today both count as a double run."""
        st, m, out = self.st, self.m, []
        ev = [(t / 10, typ, a) for t, typ, a, *_ in m.o.get("flags", []) if a in self.P and typ in ("flag_picked_up", "flag_dropped", "flagstand_captured")]
        for tm in st.teams:
            cur, lives = None, []
            for t, typ, a in ev:
                if m.team(a) != tm: continue
                u = min(max(int(t), 0), self.T)
                if typ == "flag_picked_up":
                    fresh = self.P[a][u] is not None and d(self.P[a][u], self.spawn[tm]) < SPAWN_R
                    if fresh and cur is not None and cur["carries"]:        # the flag was returned to the spawn
                        cur["end"], cur["how"] = t, "returned"; lives.append(cur); cur = None
                    if cur is None: cur = {"team": tm, "start": t, "carries": [], "end": None, "how": None}
                    cur["carries"].append([a, t, None])
                elif cur is not None and cur["carries"] and cur["carries"][-1][0] == a and cur["carries"][-1][2] is None:
                    cur["carries"][-1][2] = t
                    if typ == "flagstand_captured":
                        cur["end"], cur["how"], cur["capper"] = t, "captured", a; lives.append(cur); cur = None
            if cur is not None: lives.append(cur)
            for i, L in enumerate(lives):
                L["serious"] = [c[0] for c in L["carries"] if (c[2] is None or c[2] - c[1] >= SERIOUS_CARRY_S or c[0] == L.get("capper"))]
                order = list(dict.fromkeys(L["serious"]))
                L["form"] = None
                if L["how"] != "captured": continue
                nxt = next((x for x in lives[i + 1:] if any(c[2] is None or c[2] - c[1] >= SERIOUS_CARRY_S for c in x["carries"])), None)
                n = next((c[0] for c in nxt["carries"] if c[2] is None or c[2] - c[1] >= SERIOUS_CARRY_S), None) if nxt else None
                tc = min(int(L["end"]), self.T)
                back = (n is not None and n != L["capper"] and self.P[n][tc] is not None and self.hall is not None
                        and (self.hall.walk(self.P[n][tc], self.spawn[tm]) or 1e9) < (self.hall.walk(self.P[n][tc], self.hall.stand) or 0))
                if back: L["form"] = "double run, half" if n in order else "double run, full"
                else: L["form"] = "hand-off to cap" if len(order) > 1 else "single run"
                L["next_runner"] = n if back else None
            out += lives
        return sorted(out, key=lambda L: L["start"])

    # ---- 2.3 departures
    def _departures(self):
        out = []
        for tm in self.st.teams:
            for a in self.st.players[tm]:
                t = 0
                while t <= self.T:
                    if not self.away(a, t, tm): t += 1; continue
                    s = t
                    while t <= self.T and self.away(a, t, tm): t += 1
                    out += self._legs(a, tm, s, t - 1)
        seen, keep = set(), []
        for g in sorted(out, key=lambda x: (x["t"], x["a"])):       # one run, one leave: the earlier leg keeps the pickup
            k = (g["a"], g.get("pickup"))
            if g["purpose"] == "run" and g.get("pickup") is not None:
                if k in seen: continue
                seen.add(k)
            keep.append(g)
        return keep

    def _legs(self, a, tm, s, e):
        """The leaves inside one stretch away from the main group (seconds s to e)."""
        starts = []
        was_dead = s > 0 and self.P[a][s - 1] is not None and not self.AL[a][s - 1]
        if not self.at_home(a, s, tm):
            if e - s + 1 >= LEAVE_MIN_S: starts.append((s, "res shrine" if was_dead else "main"))
            streak, came_dead = 0, False
        else:
            streak, came_dead = 1, was_dead
        for t in range(s + 1, e + 1):
            if self.at_home(a, t, tm):
                streak += 1
                continue
            if streak:
                t0 = t - streak                                      # the stay at home ran from t0 to t - 1
                pk = [x for x in self.pick.get(a, ()) if t0 <= x < t and self.carrying(a, t)]
                if streak >= HOME_WAIT_S or pk:
                    starts.append((int(pk[-1]) if pk else t, "res shrine" if came_dead else "base"))
                streak, came_dead = 0, False
        legs = []
        for i, (t0, origin) in enumerate(starts):
            end = (starts[i + 1][0] - 1) if i + 1 < len(starts) else e
            purpose, fixed = self._purpose(a, tm, t0, origin)
            pk = next((x for x in self.pick.get(a, ()) if t0 - 1 <= x <= t0 + PURPOSE_S), None) if purpose == "run" else None
            legs.append({"a": a, "team": tm, "t": t0, "end": end, "origin": origin, "purpose": purpose, "fixed": fixed, "pickup": pk})
        return legs

    def _purpose(self, a, tm, t0, origin):
        """What a leave became, and when that was fixed."""
        if self.carrying(a, t0): return "run", t0
        home_at, coll, wait, t = None, False, 0, t0
        for t in range(t0 + 1, min(t0 + PURPOSE_S, self.T) + 1):
            if not self.AL[a][t]: return "died", t
            if self.carrying(a, t): return "run", t
            z = self.zone(a, t)
            if z in THEIRS and d(self.P[a][t], self.centre(self.MAIN[tm][t], t)) > SPLIT_FAR: return "split", t   # away from the own main
            foes = self.in_base_of(tm, t)
            wait = wait + 1 if (d(self.P[a][t], self.spawn[tm]) < SPAWN_R and not foes) else 0
            if wait >= HOME_WAIT_S: return "run", t
            if z in HOME and origin == "main":
                home_at = home_at or t; coll = coll or bool(foes)
            if a in self.MAIN[tm][t] and t - t0 >= 3 and t < self.T and a in self.MAIN[tm][t + 1]:
                return (("collapse" if coll else "retreat") if home_at else "return"), t
        if home_at: return ("collapse" if coll else "retreat"), home_at
        if self.AL[a][t] and self.zone(a, t) == "push side":
            c1, c2 = self.centre(self.MAIN[tm][t], t), self.centre(self.MAIN[3 - tm][t], t)
            if d(self.P[a][t], c1) > SPLIT_FAR and d(self.P[a][t], c2) > SPLIT_FAR: return "split", t
        return "other", t

    def groups(self, purpose):
        """Leaves of one purpose by one team within GROUP_LEAVE_S of the first: one group."""
        out = []
        for g in self.legs:
            if g["purpose"] != purpose: continue
            cur = next((x for x in reversed(out) if x["team"] == g["team"] and g["t"] - x["t"] <= GROUP_LEAVE_S), None)
            if cur and g["a"] not in cur["members"]: cur["members"].append(g["a"]); cur["legs"].append(g)
            elif not cur: out.append({"team": g["team"], "t": g["t"], "members": [g["a"]], "legs": [g]})
        return out

    def on_leg(self, a, t, purposes):
        return next((g for g in self.by_player.get(a, ()) if g["t"] <= t <= g["end"] and g["purpose"] in purposes), None)

    # ---- 2.4 triggers
    def triggers(self):
        st, out = self.st, []
        for tm in st.teams:
            foe, f1 = 3 - tm, []
            for g in self.legs:
                if g["purpose"] == "run" and g["team"] == foe: f1.append((g["t"], "enemy_run", g))
            caps = st.caps + [(st.end, None)]
            for (c, h), (c2, _) in zip(caps, caps[1:]):
                k = 1
                while h == foe and c + BOOST_EVERY * k - BOOST_WARN_S < c2:
                    f1.append((int(c + BOOST_EVERY * k - BOOST_WARN_S), "boost", None)); k += 1
            for a in st.players[tm]:
                for x in self.pick.get(a, ()):
                    if d(self.P[a][min(int(x), self.T)], self.spawn[tm]) < SPAWN_R: f1.append((int(x), "own_flag", a))
            cur = None
            for t, kind, ref in sorted(f1, key=lambda x: x[0]):
                if cur and t - cur["t"] <= MERGE_S: cur["triggers"].append(kind); cur["refs"].append(ref)
                else:
                    cur = {"family": 1, "tm": tm, "t": t, "triggers": [kind], "refs": [ref]}; out.append(cur)
            for g in self.groups("split"):
                if g["team"] == foe: out.append({"family": 2, "tm": tm, "t": g["t"], "triggers": ["split"], "refs": [g]})
        cur, eps = None, []
        for t in range(self.T + 1):
            a, b = self.MAIN[1][t], self.MAIN[2][t]
            meet = d(self.centre(a, t), self.centre(b, t)) < MEET_R
            adv = None if not meet or len(a) == len(b) else (1 if len(a) > len(b) else 2)
            if adv and cur and cur["adv"] == adv and t - cur["last"] <= 2: cur["last"] = t
            else:
                if cur and cur["last"] - cur["start"] >= NUMBERS_MIN_S: eps.append(cur)
                cur = {"adv": adv, "start": t, "last": t} if adv else None
        if cur and cur["last"] - cur["start"] >= NUMBERS_MIN_S: eps.append(cur)
        for e in eps:
            for tm in st.teams:
                out.append({"family": 3, "tm": tm, "t": e["start"], "triggers": ["up" if tm == e["adv"] else "down"], "refs": [e]})
        return sorted((x for x in out if 0 < x["t"] < self.T - READ_TO), key=lambda x: (x["t"], x["family"], x["tm"]))

    # ---- 2.5 scenario
    def _state(self, tm, t):
        """The continuous state that rides along with a scenario (for similar cases, 2.10)."""
        st, foe = self.st, 3 - tm
        owner, since = st.stand_owner(t)
        s = {"stand": "own" if owner == tm else "enemy" if owner == foe else "nobody",
             "boost_in": round(BOOST_EVERY - (t - since) % BOOST_EVERY) if owner else None,
             "alive": [sum(self.AL[a][t] for a in st.players[k]) for k in (tm, foe)],
             "main": [len(self.MAIN[tm][t]), len(self.MAIN[foe][t])],
             "own_main": self.where(self.MAIN[tm][t], t, tm), "enemy_main": self.where(self.MAIN[foe][t], t, foe),
             "own_flag": any(self.carrying(a, t) for a in st.players[tm]),
             "enemy_flag": any(self.carrying(a, t) for a in st.players[foe]),
             "res_in": round(st.next_res(t) - t), "footmen": self.footmen_alive(tm, t),
             "enemy_boost": self.boost_worth(foe, t), "own_boost": self.boost_worth(tm, t)}
        s["enemy_main"] = {"own pit": "enemy pit", "own base": "enemy base", "enemy pit": "own pit", "enemy base": "own base",
                           "backside": "push side", "push side": "backside", "own half": "enemy half",
                           "enemy half": "own half", "footmen": "enemy footmen"}.get(s["enemy_main"], s["enemy_main"])
        if self.sb:
            b = self.sb.at(t)[self.m.tag[tm]]
            s.update(flag_lead=b["flag_lead"], flag=b["flag"], morale_diff=b["morale_sum"] - self.sb.at(t)[self.m.tag[foe]]["morale_sum"])
        return s

    def scenario(self, x, s):
        fam, tm, t, foe = x["family"], x["tm"], x["t"], 3 - x["tm"]
        stand = {"own": "own team holds the stand", "enemy": "the enemy holds the stand", "nobody": "nobody holds the stand"}[s["stand"]]
        if fam == 1:
            kind = next(k for k in ("enemy_run", "boost", "own_flag") if k in x["triggers"])
            return {"key": f"{kind}|{s['stand']}", "label": f"{TRIGGER_WORDS[kind].capitalize()}; {stand}",
                    "parts": {"trigger": kind, "stand": s["stand"]}}
        if fam == 2:
            g = x["refs"][0]; n = len(g["members"])
            home = [a for a in self.st.players[tm] if self.AL[a][t] and self.zone(a, t) in HOME]
            size = {1: "a solo split", 2: "a two-player split", 3: "a three-player split"}.get(n, "a split of four or more")
            healer = any(self.m.A[a].get("p") == "Monk" for a in g["members"])
            hk = "main" if s["own_main"] in HOME else ("home" if home else "empty")
            return {"key": f"{min(n, 4)}|{hk}",
                    "label": f"{size.capitalize()} leaves; " + {"main": "the main group is already home", "home": "a defender is home", "empty": "nobody is home"}[hk],
                    "parts": {"size": n, "home": len(home), "split_has_monk": healer, "split": [self.m.roles[a] for a in g["members"]]}}
        side = x["triggers"][0]
        short = tm if side == "down" else foe
        why = collections.Counter()
        for a in self.st.players[short]:
            if a in self.MAIN[short][t]: continue
            if not self.AL[a][t]: why["kills"] += 1
            elif self.carrying(a, t) or self.on_leg(a, t, ("run",)) or d(self.P[a][t], self.spawn[short]) < SPAWN_R: why["runner away"] += 1
            else: why["split elsewhere"] += 1
        up_missing = sum(1 for a in self.st.players[3 - short] if a not in self.MAIN[3 - short][t])
        src = "wipe" if len(self.MAIN[short][t]) <= 2 and why["kills"] >= 5 else max(
            ("kills", "runner away", "split elsewhere"), key=lambda k: (why[k], k == "kills", k == "runner away"))
        n = s["main"]
        words = {"kills": "kills", "runner away": "a runner away", "split elsewhere": "players split elsewhere", "wipe": "a wipe"}[src]
        return {"key": f"{side}|{src}", "label": f"{'Up' if side == 'up' else 'Down'} on numbers where the mains meet, from {words}",
                "parts": {"side": side, "source": src, "numbers": f"{n[0]}v{n[1]}", "short_because": dict(why), "other_side_missing": up_missing}}

    # ---- 2.6 the call
    def _samples(self, t): return range(min(t + READ_FROM, self.T), min(t + READ_TO, self.T) + 1, 2)

    def _mode(self, xs):
        c = collections.Counter(xs)
        return max(c, key=lambda k: (c[k], k)) if c else None

    def _runners(self, tm, t):
        """Own players on flag duty in the read window: carrying, or on a leave that became a run."""
        out = set()
        for u in self._samples(t):
            for a in self.st.players[tm]:
                if self.AL[a][u] and (self.carrying(a, u) or (self.away(a, u, tm) and self.on_leg(a, u, ("run",)))): out.add(a)
        return out

    def _on_flagger(self, tm, t, rest_of):
        """Is the main group (less its own runners) on an enemy flag runner for more than half the read window?"""
        foe, hit, n = 3 - tm, 0, 0
        for u in self._samples(t):
            n += 1
            c = self.centre(rest_of(u), u)
            fl = [b for b in self.st.players[foe] if self.AL[b][u] and (self.carrying(b, u) or (self.away(b, u, foe) and self.on_leg(b, u, ("run",))))]
            if c and any(d(self.P[b][u], c) < FLAGGER_R for b in fl): hit += 1
        return n and hit / n > 0.5

    def call(self, x, s):
        fam, tm, t, foe = x["family"], x["tm"], x["t"], 3 - x["tm"]
        role = lambda a: self.m.roles[a]
        runners = self._runners(tm, t)
        rest_of = lambda u: [a for a in self.MAIN[tm][u] if a not in runners or self.carrying(a, u)]
        place = self._mode([self.where([a for a in self.MAIN[tm][u] if a not in runners], u, tm) for u in self._samples(t)])
        meet = sum(d(self.centre(self.MAIN[tm][u], u), self.centre(self.MAIN[foe][u], u)) < MEET_R for u in self._samples(t)) / max(len(self._samples(t)), 1) > 0.5
        shape = {"runners": sorted(role(a) for a in runners)}
        # how far the rest are from the stand, walked (for the "mid" question: fighting around the stand but outside its labelled area)
        cs = [self.centre([a for a in self.MAIN[tm][u] if a not in runners], u) for u in self._samples(t)]
        ds = sorted(self.hall.walk(c, self.hall.stand) or 0 for c in cs if c)
        shape["rest_to_stand"] = ds[len(ds) // 2] if ds else None
        if fam == 1:
            with_team = [a for a in runners if sum(self.carrying(a, u) and a in self.MAIN[tm][u] for u in self._samples(t)) > len(self._samples(t)) / 2]
            u0 = min(t + READ_FROM, self.T)
            if with_team and any(self.zone(a, u0) != "stand" for a in with_team): rest = "push the flag through as a team"
            elif place in ("push side", "enemy base", "enemy pit", "enemy half") and self._on_flagger(tm, t, rest_of): rest = "push their flagger"
            else: rest = REST_CALL.get(place, "other: " + PLACE_WORDS.get(place, place))
            n = min(len(runners), 2)
            lab = ("no runner", "one runner", "two runners")[n]
            return {"key": f"{n}|{rest}", "label": f"{lab.capitalize()}; the rest {rest}" if not rest.startswith("other") else f"{lab.capitalize()}; the rest {PLACE_WORDS.get(place, place)}",
                    "runners": n, "rest": rest, "place": place, "shape": shape}
        if fam == 2:
            g = x["refs"][0]; k = len(g["members"]); u = min(t + READ_TO, self.T)
            defs = [a for a in self.st.players[tm] if self.AL[a][u] and (self.zone(a, u) in HOME or self.on_leg(a, u, ("collapse", "retreat")))]
            alive = sum(self.AL[a][u] for a in self.st.players[tm]); n = len(defs)
            monks = sum(self.m.A[a].get("p") == "Monk" for a in defs)
            if n >= max(6, alive - 1): c = "full collapse"
            elif n == 0: c = "no answer"
            elif n == 2 and monks == 2: c = "two monks"
            elif n == 1: c = "one defender"
            elif n == k: c = "mirror"
            elif n == k + 1: c = "add one"
            else: c = f"other: {n} against {k}"
            sent = [(role(l["a"]), l["t"] - t) for l in self.legs if l["team"] == tm and l["purpose"] in ("collapse", "retreat") and t <= l["t"] <= t + READ_TO]
            late = [(role(l["a"]), l["t"] - t) for l in self.legs if l["team"] == tm and l["purpose"] == "collapse" and t + READ_TO < l["t"] <= t + PURPOSE_S]
            shape.update(defenders=sorted(role(a) for a in defs), sent=sent, sent_later=late)
            return {"key": c, "label": c.capitalize() if not c.startswith("other") else f"{n} defenders against a split of {k}",
                    "defenders": n, "split": k, "monks": monks, "place": place, "shape": shape}
        side = x["triggers"][0]
        own_run = [l for l in self.legs if l["team"] == tm and l["purpose"] == "run" and t <= l["t"] <= t + READ_TO]
        own_split = [l for l in self.legs if l["team"] == tm and l["purpose"] == "split" and t <= l["t"] <= t + READ_TO]
        if side == "up":
            if place in THEIRS: c = "push the pit for NPCs"
            elif place in ("push side", "enemy half") and self._on_flagger(tm, t, rest_of): c = "push their flagger"
            elif own_run and s["stand"] == "own": c = "run again for a backup"
            elif meet: c = "stay and kill"
            elif place in ("push side", "enemy half"): c = "chase DP"
            elif own_run or runners: c = "take the flag and reset"
            else: c = "other: " + PLACE_WORDS.get(place, place)
        else:
            if own_split: c = "trade with a split"
            elif place == "footmen": c = "fall to footmen"
            elif place == "own pit": c = "retreat to the pit"
            elif place == "own base": c = "fall back into the base"
            elif meet: c = "fight on"
            else: c = "other: " + PLACE_WORDS.get(place, place)
        shape.update(split=sorted(role(l["a"]) for l in own_split))
        return {"key": c, "label": c.capitalize() if not c.startswith("other") else f"The main group is {PLACE_WORDS.get(place, place)}",
                "place": place, "meet": bool(meet), "shape": shape}

    # ---- records
    def records(self):
        m, out = self.m, []
        for x in self.triggers():
            tm, t = x["tm"], x["t"]
            s = self._state(tm, t)
            died = [m.roles[a] for a in self.st.players[tm] for td in self.st.death_times.get(a, []) if t < td <= t + READ_TO]
            ref = x["refs"][0]
            who = None
            if x["family"] == 1:
                r = next((r for r in x["refs"] if isinstance(r, dict)), None)
                who = [m.roles[r["a"]]] if r else ([m.roles[r2] for r2 in x["refs"] if isinstance(r2, int)][:1] or None)
            elif x["family"] == 2: who = [m.roles[a] for a in ref["members"]]
            out.append({"id": f"{m.o['meta']['id'][:8]}-{x['family']}-{tm}-{t}", "rid": m.o["meta"]["id"], "family": x["family"],
                        "t": t, "team": m.tag[tm], "tm": tm, "triggers": x["triggers"], "who": who,
                        "origin": ref.get("origin") if x["family"] == 1 and isinstance(ref, dict) else (ref["legs"][0]["origin"] if x["family"] == 2 else None),
                        "scenario": self.scenario(x, s), "call": self.call(x, s), "forced": bool(died), "died": died, "state": s})
        return out


def match_records(rid):
    from replaylib import Match
    from state import GameState
    from scoreboard import Scoreboard
    st = GameState(Match.from_branch(rid))
    if not st.hall: return None
    return Moments(st, Scoreboard(st)).records()


def _flag_forms(rid):
    from replaylib import Match
    from state import GameState
    try:
        st = GameState(Match.from_branch(rid))
        if not st.hall: return rid, None
        M = Moments(st)
        return rid, [(L["form"] or L["how"] or "open", len(set(L["serious"])), sum(1 for c in L["carries"] if c[0] not in L["serious"])) for L in M.flag_lives()]
    except Exception as e: return rid, {"error": f"{type(e).__name__}: {e}"}


def _one(rid):
    try: return rid, match_records(rid)
    except Exception as e: return rid, {"error": f"{type(e).__name__}: {e}"}


def run_all(path, jobs=2):
    import multiprocessing, common
    ids, out, bad = common.replay_ids(), {}, {}
    idx = common.replay_index()
    with multiprocessing.Pool(jobs) as pool:
        for rid, rec in pool.imap_unordered(_one, ids, chunksize=4):
            if isinstance(rec, dict): bad[rid] = rec["error"]
            elif rec is not None: out[rid] = rec
    json.dump({"matches": {r: {"map": idx[r]["map"], "date": idx[r]["date"][:10], "teams": idx[r]["teams"]} for r in out},
               "records": [x for r in sorted(out) for x in out[r]], "errors": bad}, open(path, "w"))
    print(len(out), "matches,", sum(len(v) for v in out.values()), "moments,", len(bad), "errors", list(bad.items())[:3])


def counts(path):
    D = json.load(open(path)); R = D["records"]
    print(len(D["matches"]), "matches;", len(R), "moments;", sum(x["forced"] for x in R), "forced")
    for fam in (1, 2, 3):
        F = [x for x in R if x["family"] == fam]
        print(f"\nFamily {fam}: {FAMILY[fam]} ({len(F)} moments, {round(100 * sum(x['forced'] for x in F) / max(len(F), 1))}% forced)")
        sc = collections.Counter(x["scenario"]["key"] for x in F)
        for k, n in sc.most_common():
            calls = collections.Counter(x["call"]["key"] for x in F if x["scenario"]["key"] == k and not x["forced"])
            lab = next(x["scenario"]["label"] for x in F if x["scenario"]["key"] == k)
            print(f"  {n:5}  {lab}")
            print("         " + "; ".join(f"{c} {v}" for c, v in calls.most_common(7)))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "all": run_all(a[1], int(a[a.index("--jobs") + 1]) if "--jobs" in a else 2)
    elif a and a[0] == "counts": counts(a[1])
    elif a and a[0] == "flags":         # how every flag's life ended, over all counted matches
        import multiprocessing, common
        c, brief, bad = collections.Counter(), 0, 0
        with multiprocessing.Pool(int(a[a.index("--jobs") + 1]) if "--jobs" in a else 2) as pool:
            for rid, rows in pool.imap_unordered(_flag_forms, common.replay_ids(), chunksize=4):
                if not isinstance(rows, list): bad += rows is not None; continue
                for form, n, b in rows: c[form] += 1; brief += b
        tot = sum(c.values())
        for k, v in c.most_common(): print(f"{v:6} {round(100 * v / tot):3}%  {k}")
        print(f"{brief} pickups dropped within {SERIOUS_CARRY_S} s without a capture (not counted as carries); {bad} matches failed")
    elif a:
        from replaylib import Match
        recs = match_records(a[0]) or []
        for x in recs:
            if len(a) > 1 and str(x["family"]) != a[1]: continue
            print(f"{Match.f(x['t'] * 10):>5} F{x['family']} {x['team']:5} {x['scenario']['label']}"
                  + (f" ({', '.join(x['who'])})" if x["who"] else "") + f" -> {x['call']['label']}" + (" [forced: " + ", ".join(x["died"]) + "]" if x["forced"] else ""))
    else: print(__doc__)
