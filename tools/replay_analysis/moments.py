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
Shape (2.8, R-297): who the call was made with (as properties: monks, heals, prots, self-defence, snare and speed power,
  escapes), which way (the drawn flag run and door, the door a defender came home by, the door or ground of a push or a
  fall back) and when (seconds to the first move; a delay is a decision when something was being gained elsewhere as
  the moment came, R-321, and execution otherwise).
Consequence (2.9, R-294, R-412): what followed over the whole map at 90 s and about 3 min, hard results only, with the
  flag lead then and now set beside the numbers meanwhile (the main team's fight, the other fights, players away for
  the flag).
The records (R-362: the record is the work; story.py only prints them): attempts (splits and main team pushes), caught,
  flags_record (with the flag route, the door, the hold before a cap and its distance from the enemy's boost),
  main_team, lane, moves, split_fights, ground, undefended, on_pit, and the words of R-373 and R-375 to R-378, each its
  own record: flag_pushes (pushing the flagger, R-371), flag_lead (a full flag and half a flag up, R-375), pregame
  (the flag before the gates), standoffs (the disengage, R-405), timing (R-377, R-400, R-407), monk_counts and on_lord (R-378),
  and way_out (a team going out of its base by a door, R-417).

Usage:  python3 moments.py <report id> [family]      the match's moments in order
        python3 moments.py all <out.json> [--jobs N]  every counted match, compact (for counts and golden picks)
        python3 moments.py counts <out.json>          cases by family, scenario and call
        python3 moments.py after <out.json>           what followed each call at 90 s, on average (stage D: the consequence record)
        python3 moments.py runner <out.json>          what running a flag costs in players at the main fight (R-412)
        python3 jobs.py summary <out.json>            the plays and how often each job was met (jobs.py)
In code: Moments(st, sb).records() -> list of dicts."""
import collections, json, math, statistics, sys
from common import (DOUBLE_NEXT_S, FLAG_MOMENT_GREATER, FLAG_MOMENT_STAND, FIGHT_HOLD, FIGHT_HOLD_S, FIGHT_ACT, FIGHT_CLOSE, READ_FROM, READ_TO, CONSEQ_S, ON_TIME_S, LATE_S, PIT_S, AREA_SHARE, PURPOSE_S, LEAVE_MIN_S, HOME_WAIT_S, SPAWN_R, GROUP_LEAVE_S, MEET_R,
                    NUMBERS_MIN_S, MERGE_S, BOOST_WARN_S, FLAGGER_R, SPLIT_FAR, BOOST_EVERY, SERIOUS_CARRY_S, FIGHT_LINK, GROUND_MOVE, GROUND_S, GROUND_BACK, GROUND_JUMP, GROUND_SPLIT_MOVE, SIDE_FIGHT_MAX, SIDE_FIGHT_S, UNDEFENDED_S,
                    RETURN_R, FOOT_ENGAGED_S, SPLIT_STEP, SPLIT_MIN_S, SPLIT_GAP_S, FORCED_OUT_S, AHEAD_LOOK_S, CAUGHT_S, NPC_NEAR,
                    JOIN_S, RES_EVERY, flux_at, JOIN_LOOK_S, JOIN_MOVE, JOIN_LEAD, JOIN_ENGAGE, JOIN_ENGAGE_S, MAIN_BIG, SWAP_S, SWAP_STAY_S, SPLIT_FIGHT_GAP_S, SPLIT_FIGHT_MIN,
                    PUSHFLAG_R, PUSHFLAG_S, PUSHFLAG_SHORT_S, PUSHFLAG_LATE_S, PUSHFLAG_GAP_S, PUSHFLAG_MATES, PUSHFLAG_AHEAD_S, ROUTE_ENDS, ROUTE_OFF, ROUTE_CLEAR, ROUTE_MIN_S, LEAD_S,
                    WAY_OUT_GAP_S, STANDOFF_S, STANDOFF_HITS, STANDOFF_MIN, STANDOFF_R, STANDOFF_SPLIT_MIN, STANDOFF_SPLIT_S, STANDOFF_STILL, STANDOFF_NEAR, LEAD_HALF, LEAD_ONE, LEAD_ONE_HALF, LEAD_TWO, HOLD_BACK_S, LEFT_AT_SPAWN_S, RUN_SPEED, PICKUP_DELAY_S, HOLD_S, BOOST_LATE_S, HELP_IN_S, HELP_BACK_S, LEAVE_RES_S, MONK_S, MONK_MIN, LORD_GAP_S)
from state import d
from hallmap import _seg_dist

HOME, THEIRS = ("own pit", "own base"), ("enemy pit", "enemy base")
LEAD_WORDS = (None, "half a flag", "a flag", "a flag and a half", "two flags")      # the bands of the flag lead (R-408)
FAMILY = {1: "Flag decision", 2: "Answer to a split", 3: "Numbers advantage"}
TRIGGER_WORDS = {"enemy_run": "an enemy player leaves to run a flag", "boost": f"the enemy's boost is {BOOST_WARN_S} s away",
                 "own_flag": "an own player goes to run a fresh flag"}
PLACE_WORDS = {"stand": "at the stand", "footmen": "at the footmen", "own pit": "in the own pit", "own base": "in the own base",
               "enemy pit": "in the enemy pit", "enemy base": "in the enemy base", "backside": "on the backside",
               "push side": "on the push side", "own half": "spread over the own half", "enemy half": "spread over the enemy half",
               "spread": "spread out", "nobody": "nobody"}
REST_CALL = {"stand": "stay at the stand", "footmen": "fall to footmen", "own pit": "retreat to the pit",
             "own base": "fall back into the base"}


class Moments:
    def __init__(self, st, sb=None):
        self.st, self.m, self.hall, self.sb, self.T = st, st.m, st.hall, sb, st.end
        import datetime
        self.day = datetime.datetime.fromtimestamp(st.m.o["meta"]["started"] / 1000, datetime.timezone.utc).strftime("%Y-%m-%d")      # the day it was played (UTC); a match with no start time stops here, loudly (R-460)
        m, R = st.m, range(st.end + 1)
        self.P, self.AL = {}, {}
        for a in m.PL:
            ps, al = [], []
            for t in R:
                p, s = st.pos(a, t); ps.append(p); al.append(bool(p) and m.alive(s))
            self.P[a], self.AL[a] = ps, al
        self.MAIN = {tm: [frozenset(st.main_group(tm, t)) for t in R] for tm in st.teams}
        self._z = {}
        self.spawn = {tm: (self.hall.spawn.get(st.side[tm]) if self.hall and tm in st.side else None) or st.geo.spawn.get(tm) for tm in st.teams}
        self.carry = collections.defaultdict(list)
        for c in st.carries: self.carry[c["a"]].append((c["s"], c["e"]))
        self.flag_ev, self.missed_pickups = self._flag_ev()
        for tp, a, tc in self.missed_pickups: self.carry[a].append((tp, tc))
        self.pick = collections.defaultdict(list)
        for t, typ, a in self.flag_ev:
            if typ == "flag_picked_up": self.pick[a].append(t)
        self.foot_dead = collections.defaultdict(list)       # team -> times its footmen died
        for r in m.o["ev"]:
            if r[1] == "dt" and isinstance(r[2], int) and r[2] < len(m.A) and m.A[r[2]].get("npc") == "footman":
                self.foot_dead[m.A[r[2]].get("team")].append(r[0] / 10)
        self.foot_act = collections.defaultdict(list)        # team -> seconds its footmen dealt or took damage
        foot_hit = collections.defaultdict(list)             # footman -> [(second, the player who hit him)]: which group he stood in is read from where they stood
        self.hits = collections.defaultdict(list)            # second -> [(actor, target)] damage between players
        self.npc_hits = collections.defaultdict(list)        # player -> seconds he damaged an enemy NPC
        self.acts = collections.defaultdict(list)            # second -> [(actor, target)] damage dealt or a skill landed, between players of the two teams
        self.aid = collections.defaultdict(list)             # second -> [(actor, target)] a heal or a skill landed on a team mate
        self._nr, self._ia = {}, {}
        self.lord_hits = collections.defaultdict(list)       # team -> [(second, the enemy player, amount)] damage on its Guild Lord
        self.pit_kind = collections.defaultdict(lambda: collections.defaultdict(set))  # team -> second -> which of them (knight, bodyguard, guild_lord)
        self.pit_act = collections.defaultdict(lambda: collections.defaultdict(set))   # team -> second -> enemy players trading damage with its knight, bodyguard or Guild Lord (R-387)
        for r in m.o["ev"]:
            if r[1] in ("dm", "sa") and r[2] in self.P and r[3] in self.P and m.team(r[2]) != m.team(r[3]): self.acts[int(r[0] / 10)].append((r[2], r[3]))
            if r[1] in ("hl", "sa") and r[2] in self.P and r[3] in self.P and r[2] != r[3] and m.team(r[2]) == m.team(r[3]): self.aid[int(r[0] / 10)].append((r[2], r[3]))
            if r[1] != "dm" or not isinstance(r[2], int) or not isinstance(r[3], int) or max(r[2], r[3]) >= len(m.A): continue
            if m.A[r[3]].get("npc") == "guild_lord" and r[2] in self.P and m.A[r[3]].get("team") not in (None, m.team(r[2])):
                self.lord_hits[m.A[r[3]].get("team")].append((r[0] / 10, r[2], r[5] if len(r) > 5 and isinstance(r[5], (int, float)) else 0))
            for x in (r[2], r[3]):
                if m.A[x].get("npc") == "footman": self.foot_act[m.A[x].get("team")].append(r[0] / 10)
            if m.A[r[3]].get("npc") == "footman" and r[2] in self.P: foot_hit[r[3]].append((r[0] / 10, r[2]))
            if r[2] in self.P and r[3] in self.P and m.team(r[2]) != m.team(r[3]): self.hits[int(r[0] / 10)].append((r[2], r[3]))
            for x, y in ((r[2], r[3]), (r[3], r[2])):
                if m.A[x].get("npc") in ("knight", "bodyguard", "guild_lord") and y in self.P and m.A[x].get("team") not in (None, m.team(y)):
                    self.pit_act[m.A[x].get("team")][int(r[0] / 10)].add(y); self.pit_kind[m.A[x].get("team")][int(r[0] / 10)].add(m.A[x].get("npc"))
            if r[2] in self.P and r[3] not in self.P and m.A[r[3]].get("npc") and m.A[r[3]].get("team") not in (None, m.team(r[2])): self.npc_hits[r[2]].append(r[0] / 10)
        self.foot_gone = collections.defaultdict(lambda: collections.defaultdict(list))      # team -> "front" or "back" -> times a footman of that group died (the replays carry no footman positions)
        if self.hall is not None:
            for r in m.o["ev"]:
                x = r[2]
                if r[1] != "dt" or not isinstance(x, int) or x >= len(m.A) or m.A[x].get("npc") != "footman": continue
                tm_, sd = m.A[x].get("team"), st.side.get(m.A[x].get("team"))
                pts = [self.P[a][min(max(int(u), 0), self.T)] for u, a in foot_hit.get(x, ()) if r[0] / 10 - 15 <= u <= r[0] / 10]
                pts = [q for q in pts if q]
                if sd is None or not pts: continue
                c = (statistics.fmean(q[0] for q in pts), statistics.fmean(q[1] for q in pts))
                near = {k: min(math.dist(c, f) for f in self.hall.footies[sd][k]) for k in ("front", "back") if self.hall.footies[sd][k]}
                if near: self.foot_gone[tm_][min(near, key=near.get)].append(r[0] / 10)
        self._eng = {}
        self._pit = {}
        self._dp, self._ov, self._fp, self._att, self._last, self._mt, self._ln, self._fr = {}, {}, None, None, {}, {}, None, None
        self._fi, self._mv, self._sf, self._gr, self._und = None, None, None, None, None
        self._lost = {}
        self._fpush, self._lead, self._leadl, self._lead_on, self._so, self._hitc, self._mc, self._tim = None, None, None, None, None, None, None, None
        self._wo = None
        self._fc, self._tl_, self._npcd, self._bst, self._lord = {}, None, None, None, None      # fights by second; the map's numbers every 2 s; NPC deaths; boosts landed
        self.side_cut = set()                                # seconds at which a side fight was cut off a bigger one (counted for the thresholds table)
        self.legs = self._departures()
        self.by_player = collections.defaultdict(list)
        for g in self.legs: self.by_player[g["a"]].append(g)

    def _flag_ev(self):
        """The flag events in seconds, players only: [(t, kind, player)], and the pickups the observer missed
        [(pickup, player, capture)]. A capture by a player with no pickup recorded on him (about 1 capture in 40) is
        given one, read from the capture as a missed return is read from the flag being back (R-389): where a team
        mate last dropped the flag, the first second the capper stood on it; failing that at his own flag spawn, the
        last second he stood there since his team's last flag event. No such second: the capture stays as recorded."""
        m, out, missed = self.m, [], []
        op, last, lastp = {}, {}, {}                         # open pickups by player; team -> its last flag event (t, kind, player); team -> who last picked up
        for t, typ, a, *_ in m.o.get("flags", []):
            if a not in self.P or typ not in ("flag_picked_up", "flag_dropped", "flagstand_captured"): continue
            t, tm = t / 10, m.team(a)
            if typ == "flag_picked_up":
                if a in op and lastp.get(tm) == a and all(self.AL[a][u] for u in range(max(int(op[a]), 0), min(int(t), self.T) + 1)): continue      # a second pickup with no drop between, he alive throughout and nobody of his team taking it meanwhile: the same carry (replaylib._carries)
                op[a] = t; lastp[tm] = a
            elif typ == "flag_dropped": op.pop(a, None)
            elif a not in op:
                lt, lk, la = last.get(tm, (0, None, None))
                u1, tp = min(int(t), self.T), None
                if lk == "flag_dropped" and la != a:
                    u0 = min(int(lt), self.T)                 # positions are by the second and a drop falls between two: either side of it,
                    spots = [q for q in (self.P[la][u0], self.P[la][min(u0 + 1, self.T)]) if q]      # or the two meeting just after it
                    tp = next((max(u, lt) for u in range(u0, u1 + 1) if self.P[a][u] and (any(d(self.P[a][u], q) < RETURN_R for q in spots)
                               or (u <= u0 + 3 and self.P[la][u] and d(self.P[a][u], self.P[la][u]) < RETURN_R))), None)
                if tp is None and self.spawn.get(tm):
                    tp = next((u for u in range(u1, int(lt) - 1, -1) if self.P[a][u] and d(self.P[a][u], self.spawn[tm]) < SPAWN_R), None)
                    if tp is not None: tp = max(tp, lt)       # never before the team's last flag event: a flag he dropped at the spawn and took again is picked up after the drop
                if tp is not None and tp <= t:               # at the very second of the capture is still before it: the events keep their order
                    out.append((tp, "flag_picked_up", a)); missed.append((tp, a, t))
            else: op.pop(a, None)
            out.append((t, typ, a)); last[tm] = (t, typ, a)
        return sorted(out, key=lambda x: x[0]), missed

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
    def _near(self, t):
        """The pairs of living players within FIGHT_LINK of one another at second t."""
        if t not in self._nr:
            live = [a for a in self.m.PL if self.AL[a][t]]
            self._nr[t] = {(a, b) for i, a in enumerate(live) for b in live[i + 1:] if d(self.P[a][t], self.P[b][t]) < FIGHT_LINK}
        return self._nr[t]

    def _acting(self, t, aid=True):
        """The pairs of players who hit or cast on one another (and, with aid, who heal or protect one another) within
        FIGHT_HOLD_S of second t."""
        if (t, aid) not in self._ia:
            s = set()
            for u in range(max(t - FIGHT_HOLD_S, 0), min(t + FIGHT_HOLD_S, self.T) + 1):
                for src in ((self.acts, self.aid) if aid else (self.acts,)):
                    for x, y in src.get(u, ()): s.add((x, y) if x < y else (y, x))
            self._ia[(t, aid)] = s
        return self._ia[(t, aid)]

    def linked(self, a, b, t):
        """Are two living players in the same fight at second t (the one reading of it, used by the fights, the numbers
        and a split's defenders alike): within reach; or just out of reach having been within it a few seconds either
        side; or further apart and one hitting or casting on the other. A heal does not link two players: a monk
        healing across from the main fight is not on the split (NwAy v Men 11:50, review key s1-21)."""
        if a > b: a, b = b, a
        if (a, b) in self._near(t): return True
        dist = d(self.P[a][t], self.P[b][t])
        if dist < FIGHT_ACT and (a, b) in self._acting(t, aid=False): return True
        return dist < FIGHT_HOLD and any((a, b) in self._near(u) for u in range(max(t - FIGHT_HOLD_S, 0), min(t + FIGHT_HOLD_S, self.T) + 1, 2))

    def engaged_in(self, a, members, t):
        """Is a player who is within reach of a fight engaged in it at second t: standing FIGHT_CLOSE from someone in it,
        acting in it, or standing where he is (a caster at range). A player walking in has not joined yet, and one
        walking away has left (R-464)."""
        if any(b != a and self.AL[b][t] and d(self.P[a][t], self.P[b][t]) < FIGHT_CLOSE for b in members): return True
        if any((x == a and y in members) or (y == a and x in members) for x, y in self._acting(t)): return True
        u = max(t - SPLIT_STEP, 0)
        return bool(self.AL[a][u] and self.P[a][u]) and d(self.P[a][t], self.P[a][u]) < 150 * SPLIT_STEP      # under about half a run: standing, or shuffling

    def visits(self, times, reach, engaged, deaths=(), min_s=None, to_end=True):
        """When a player counts as one more in a fight, from the seconds he is within reach of it and the seconds he is
        engaged in it (standing FIGHT_CLOSE from someone in it, or acting in it). He counts from when he first engages to
        when he last does (R-464: he has joined when he reaches the fight, and has left when he walks away, not when he
        comes into or goes out of reach), if that is JOIN_S or longer (R-350: less is support), or he dies in it, or the
        match ends with him there (R-459). A gap of FIGHT_HOLD_S or less does not end a visit. Returns one flag a reading."""
        n, keep, i, step = len(times), [False] * len(times), 0, (times[1] - times[0] if len(times) > 1 else SPLIT_STEP)
        min_s = JOIN_S if min_s is None else min_s
        while i < n:
            if not reach[i]: i += 1; continue
            j, gap = i, max(1, FIGHT_HOLD_S // step)
            while True:
                nxt = next((q for q in range(j + 1, min(j + gap + 1, n - 1) + 1) if reach[q]), None)
                if nxt is None: break
                j = nxt
            died = any(times[i] - 2 <= td <= times[j] + 4 for td in deaths)
            es = [q for q in range(i, j + 1) if engaged[q]]
            if es or died:
                a_, b_ = (es[0], es[-1]) if es else (i, j)
                if died: b_ = j
                if (b_ - a_ + 1) * step >= min_s or died or (to_end and j == n - 1):
                    for q in range(a_, b_ + 1): keep[q] = True
            i = j + 1
        return keep

    def fights(self, t):
        """The groups on the map at second t: living players of both teams in the same fight (`linked`), each with its
        numbers by team and where it stands (the place of team 1's players, else team 2's, named by whose ground it
        is). Denning reads a match this way ("3v4 in the back door", "7v7 at the stand")."""
        if t in self._fc: return self._fc[t]
        st, m = self.st, self.m
        live = [a for a in m.PL if self.AL[a][t]]
        gs = []
        for a in live:
            hit = [g for g in gs if any(self.linked(a, b, t) for b in g)]
            gs = [g for g in gs if g not in hit] + [[a] + [x for g in hit for x in g]]
        cut = []
        for g in gs:                                         # a small fight hanging off a bigger one (R-374: the opening ranger 1v1 is not part of the 8v8)
            if len(g) < 6 or len({m.team(a) for a in g}) < 2: cut.append(g); continue
            gset, link = set(g), collections.defaultdict(set)
            for u in range(max(int(t) - SIDE_FIGHT_S, 0), min(int(t) + SIDE_FIGHT_S, self.T) + 1):
                for x, y in self.hits.get(u, ()):
                    if x in gset and y in gset: link[x].add(y); link[y].add(x)
            for a in g:
                for b in g:
                    if a < b and m.team(a) == m.team(b) and d(self.P[a][t], self.P[b][t]) < 1000: link[a].add(b); link[b].add(a)
            comps, seen = [], set()
            for a in g:
                if a in seen: continue
                comp, todo = [], [a]
                while todo:
                    x = todo.pop()
                    if x in seen: continue
                    seen.add(x); comp.append(x); todo += [y for y in link[x] if y not in seen]
                comps.append(comp)
            apart = lambda c: all(d(self.P[a][t], self.P[b][t]) >= 1000 for a in c for b in g if b not in c)      # and nobody else of the fight within an aggro bubble of them
            side = [c for c in comps if len({m.team(a) for a in c}) == 2 and len(c) <= SIDE_FIGHT_MAX and len(c) * 2 < len(g) and apart(c)]
            if side and len(g) - sum(len(c) for c in side) >= 2:
                off = {a for c in side for a in c}; self.side_cut.add(int(t))
                cut.append([a for a in g if a not in off]); cut += side
            else: cut.append(g)
        gs = cut
        out = []
        for g in gs:
            n = {tm: [a for a in g if m.team(a) == tm] for tm in st.teams}
            z = collections.Counter(self.place_at(a, t) for a in g)
            kind, side = max(z, key=lambda k: (z[k], str(k)))
            out.append({"n": {tm: len(n[tm]) for tm in st.teams}, "ids": {tm: frozenset(n[tm]) for tm in st.teams},
                        "who": {tm: sorted(m.roles[a] for a in n[tm]) for tm in st.teams}, "monks": {tm: self._mk(n[tm]) for tm in st.teams},
                        "kind": kind, "side": side, "place": self.place_words(kind, side),
                        "flag": [a for a in g if self.carrying(a, t)]})
        self._fc[t] = sorted(out, key=lambda x: -(x["n"][1] + x["n"][2]))
        return self._fc[t]

    def engaged(self, t):
        """{side: are that side's footmen in a fight now} (R-307: fell to footmen means the footmen are engaged)."""
        if t not in self._eng:
            self._eng[t] = {self.st.side[tm]: self.footmen_alive(tm, t) > 0 and any(t - FOOT_ENGAGED_S <= x <= t for x in self.foot_act.get(tm, ()))
                            for tm in self.st.teams if tm in self.st.side}
        return self._eng[t]

    def place_at(self, a, t):
        """Where a player stands, in Denning's words. The pit is wider than its drawn area (R-387): a player is at his
        own pit when he stands within reach of his knights, bodyguard or Guild Lord, and at the enemy's pit when he, or
        a team mate next to him, is trading damage with one of them. Footies: the enemy's only while those footmen are
        engaged (R-307); his own whenever he stands within reach of his own living footmen (R-391)."""
        k, s = self.hall.place(self.P[a][t], self.engaged(t))
        if k not in ("pit", "stand") and not k.endswith("footies"):      # R-391: at his own footies whenever he stands within reach of his own living footmen, engaged or not
            tm, own, r = self.m.team(a), self.st.side.get(self.m.team(a)), self.hall.reach()
            if own is not None and r:
                for g in ("front", "back"):
                    F = self.hall.footies[own][g]
                    if F and len(F) > sum(1 for x in self.foot_gone[tm][g] if x <= t) and any(math.dist(self.P[a][t], f) <= r for f in F): k, s = g + " footies", own; break
        if s is None or k in ("pit", "stand", "greater stand"): return k, s
        if k == "field" and self.st.side.get(self.m.team(a)) != s: return k, s      # out in the field he is not at the enemy's pit, whatever he hit a moment ago (a team that left by a teleporter)
        key = (a, t)
        if key not in self._pit:
            hall, tm_s = self.hall, next((tm for tm, sd in self.st.side.items() if sd == s), None)
            v = False
            if tm_s is not None:
                if self.m.team(a) == tm_s:
                    r, pts = hall.reach(), hall.npc[s]["Knight"] + hall.npc[s]["Bodyguard"] + [hall.lord[s]]
                    v = bool(r) and min(math.dist(self.P[a][t], q) for q in pts) <= r
                else:
                    act = self.pit_act.get(tm_s)
                    if act:
                        on = set().union(*(act.get(u, ()) for u in range(int(t) - PIT_S, int(t) + 1)))
                        v = a in on or any(self.AL[b][t] and self.P[b][t] and d(self.P[a][t], self.P[b][t]) < 1000 for b in on)
            self._pit[key] = v
        return ("pit", s) if self._pit[key] else (k, s)

    def contact(self, ids1, ids2, t0, t1):
        """Did these two groups trade damage between t0 and t1 (standing near each other is not a fight)."""
        return any((x in ids1 and y in ids2) or (x in ids2 and y in ids1) for u in range(max(int(t0), 0), int(t1) + 1) for x, y in self.hits.get(u, ()))

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
        ev = self.flag_ev
        for tm in st.teams:
            cur, lives = None, []
            for t, typ, a in ev:
                if m.team(a) != tm: continue
                u = min(max(int(t), 0), self.T)
                if typ == "flag_picked_up":
                    fresh = self.P[a][u] is not None and d(self.P[a][u], self.spawn[tm]) < SPAWN_R
                    if fresh and cur is not None and cur["carries"] and cur["carries"][-1][2] is not None:
                        lc = cur["carries"][-1]; lp = self.P[lc[0]][min(int(lc[2]), self.T)]
                        if lp and d(self.P[a][u], lp) < RETURN_R: fresh = False      # the flag lay there: picked up from the ground
                    if fresh and cur is not None and cur["carries"]:        # the flag was returned to the spawn
                        last = cur["carries"][-1]; td = last[2] if last[2] is not None else t
                        pos = self.P[last[0]][min(int(td), self.T)]
                        near = [(d(self.P[b][u], pos), u, b) for u in range(int(td), min(int(t), self.T) + 1) for b in st.players[3 - tm]
                                if pos and self.AL[b][u] and d(self.P[b][u], pos) < RETURN_R]
                        # players run past a flag without returning it, so the last enemy to stand on it before the
                        # next pickup at the spawn is taken as the one who returned it (Denning's mark, BcS v hook 6:22)
                        close = [x for x in near if x[0] < 150] or near
                        who = (lambda x: (x[1], x[2]))(max(close, key=lambda x: x[1])) if close else None
                        cur["end"], cur["how"] = t, "returned"
                        cur["dropped"], cur["returned"] = (td, last[0], pos), who
                        lives.append(cur); cur = None
                    if cur is None: cur = {"team": tm, "start": t, "carries": [], "end": None, "how": None}
                    cur["carries"].append([a, t, None])
                elif cur is not None and cur["carries"] and cur["carries"][-1][0] == a and cur["carries"][-1][2] is None:
                    cur["carries"][-1][2] = t
                    if typ == "flagstand_captured":
                        cur["end"], cur["how"], cur["capper"] = t, "captured", a; lives.append(cur); cur = None
            if cur is not None: lives.append(cur)
            for i, L in enumerate(lives):
                sp = self.hall.spawn.get(self.st.side.get(L["team"])) if self.hall is not None else None
                def gave(i):                                  # he gave it to a team mate out on the map: a hand-off, however briefly the pickup was seen on him
                    cs = L["carries"]
                    if i + 1 >= len(cs) or cs[i + 1][0] == cs[i][0] or sp is None: return False
                    q = self.P[cs[i + 1][0]][min(max(int(cs[i + 1][1]), 0), self.T)]
                    return bool(q) and d(q, sp) > 2 * SPAWN_R
                L["serious"] = [c[0] for i, c in enumerate(L["carries"]) if (c[2] is None or c[2] - c[1] >= SERIOUS_CARRY_S or c[0] == L.get("capper") or gave(i))]
                order = list(dict.fromkeys(L["serious"]))
                L["form"] = None
                if L["how"] != "captured": continue
                nxt = next((x for x in lives[i + 1:] if any(c[2] is None or c[2] - c[1] >= SERIOUS_CARRY_S for c in x["carries"])), None)
                n = next((c[0] for c in nxt["carries"] if c[2] is None or c[2] - c[1] >= SERIOUS_CARRY_S), None) if nxt else None
                tc = min(int(L["end"]), self.T)
                back = False
                soon = nxt is not None and nxt["start"] - L["end"] <= DOUBLE_NEXT_S       # he takes the next flag at once: that is what he was back there for
                if n is not None and soon and n != L["capper"] and self.P[n][tc] is not None and self.hall is not None:
                    w1, w2 = self.hall.walk(self.P[n][tc], self.spawn[tm]), self.hall.walk(self.P[n][tc], self.hall.stand)
                    back = w1 is not None and w2 is not None and w1 < w2
                if back: L["form"] = "double run, half" if n in order else "double run, full"
                else: L["form"] = "hand-off to cap" if len(order) > 1 else "single run"
                L["next_runner"] = n if back else None
            out += lives
        return sorted(out, key=lambda L: L["start"])

    # ---- splits and main team pushes: one record an attempt (R-355, R-357, R-358, R-362 to R-364)
    def _deep(self, a, t):
        """The place a player stands on the enemy's ground (past the stand and the greater stand area, on the enemy's
        side of the hall), or None. A player standing with team mates who are not there is with them, not there."""
        k = (a, t)
        if k not in self._dp:
            v = None
            if self.AL[a][t] and self.P[a][t] and self.hall is not None:
                kind, side = self.place_at(a, t)
                if side is not None and side != self.st.side.get(self.m.team(a)) and kind not in ("stand", "greater stand"): v = kind
            self._dp[k] = v
        return self._dp[k]

    def flag_player(self, tm, t):
        """The player responsible for the team's flag at second t: its latest serious carrier (the first, before any)."""
        if self._fp is None:
            self._fp = collections.defaultdict(list)
            for L in self.flag_lives():
                for c in L["carries"]:
                    if c[0] in L["serious"]: self._fp[L["team"]].append((c[1], c[0]))
            for k in self._fp: self._fp[k].sort()
        xs = self._fp.get(tm) or []
        last = None
        for s, a in xs:
            if s > t: break
            last = a
        return last if last is not None else (xs[0][1] if xs else None)

    def lane(self, a, t):
        """Which way a player last went: "front" (the stand, the greater stand area, a front door or front footies) or
        "back" (a back door or back footies); None from his base until he passes one. The main teams meet on the
        front lane, through the stand; a split goes round the back."""
        if self._ln is None:
            self._ln = {}
            for x in self.m.PL:
                cur, row = None, {}
                for u in range(0, self.T + 1, SPLIT_STEP):
                    if not self.AL[x][u]: cur = None
                    elif self.hall is not None and self.P[x][u]:
                        k = self.place_at(x, u)[0]
                        if k in ("stand", "greater stand", "front door", "front footies"): cur = "front"
                        elif k in ("back door", "back footies"): cur = "back"
                    row[u] = cur
                self._ln[x] = row
        return self._ln[a][t - t % SPLIT_STEP]

    def main_team(self, tm, t):
        """The main team at second t (R-335, R-355): the group on the flag stand side, the one responsible for flags.
        While the team stands together (all but two of its living players in one group) it is that group. When the
        team divides, the main team is the part that has been carrying the flag (carries by its players over the
        team's last three flags and next two), helped by which part stays while the other walks away over the next
        minute (in the first minute of the match, by which part is nearer the stand 30 s on). It then stays that group, following its players, until
        the team is together again; and whenever one part stands on the front lane (the stand and the front doors) while
        the others have gone round the back, that part is the main team (see lane). Monks only break a tie. A split
        stays a split while its main team is dead (R-392): the main team is then its survivors, or nobody, until its
        dead are back or the groups rejoin."""
        if self._mt.get(tm) is None:
            st, hall = self.st, self.hall
            to_stand = hall.to(hall.stand) if hall is not None else {}
            far = lambda ids, u: statistics.fmean(to_stand.get(hall.snap(self.P[a][u]), 1e5) for a in ids)
            monks = lambda ids: sum(1 for a in ids if self.m.A[a].get("p") == "Monk")
            lives = [(L["start"], set(L["serious"])) for L in self.flag_lives() if L["team"] == tm]
            def flags(g, u):
                i = sum(1 for s_, _ in lives if s_ <= u)
                return sum(len(c & set(g)) for _, c in lives[max(i - 3, 0):i + 2])
            out, prev, together = {}, frozenset(), True
            fallen, lost = set(), {}                          # main team players who died as main team and are still dead (R-392)
            for u in range(0, self.T + 1, SPLIT_STEP):
                live = [a for a in st.players[tm] if self.AL[a][u]]
                fallen = {a for a in fallen | set(prev) if not self.AL[a][u]}
                lost[u] = len(fallen)
                gs = []
                for a in live:
                    hit = [g for g in gs if any(d(self.P[a][u], self.P[b][u]) < FIGHT_LINK for b in g)]
                    gs = [g for g in gs if g not in hit] + [[a] + [x for g in hit for x in g]]
                gs.sort(key=len, reverse=True)
                if not gs: out[u] = prev; continue
                if fallen and not (prev & set(gs[0])) and len(gs[0]) < max(len(live) + len(fallen) - 2, 2):
                    # R-392: the others are the bigger part of the living team only because the main team's players died.
                    # They do not become the main team: it stays its survivors, or nobody, until its dead are back or the groups rejoin
                    ov = max(gs, key=lambda g: (len(prev & set(g)), len(g)))
                    if prev & set(ov): prev = frozenset(ov)
                    out[u] = prev if any(self.AL[a][u] for a in prev) else frozenset(); continue
                if len(gs[0]) >= max(len(live) - 2, 2) or len(gs) == 1: prev, together = frozenset(gs[0]), True
                elif together:                                # the team divides here: judged 30 s on, once the parts have formed
                    v = min(u + 30, self.T)
                    later = []
                    for a in [a for a in live if self.AL[a][v]]:
                        hit = [g for g in later if any(d(self.P[a][v], self.P[b][v]) < FIGHT_LINK for b in g)]
                        later = [g for g in later if g not in hit] + [[a] + [x for g in hit for x in g]]
                    cand = [g for g in later if len(g) >= 2] or later or gs
                    if u < 60: key = {id(g): far(g, v) for g in cand}
                    else:                                     # who walks away is read a minute on: a split takes time to get going
                        w = min(u + 60, self.T)
                        key = {id(g): d(self.centre(g, u), self.centre([a for a in g if self.AL[a][w]] or g, w if any(self.AL[a][w] for a in g) else v)) for g in cand}
                    ks = sorted(key.values())
                    stays = lambda g: 2 if len(ks) > 1 and key[id(g)] == ks[0] and ks[1] - ks[0] > 2000 else 0
                    own = {id(g): list(g) for g in cand}      # a lone runner counts for the part he comes back to
                    for a in [a for a in live if self.AL[a][v] and not any(a in g for g in cand)]:
                        for w in range(v, min(v + 60, self.T) + 1, 4):
                            hit = next((g for g in cand if self.AL[a][w] and any(self.AL[b][w] and d(self.P[a][w], self.P[b][w]) < FIGHT_LINK for b in g)), None)
                            if hit is not None: own[id(hit)].append(a); break
                    best = set(max(cand, key=lambda g: (flags(own[id(g)], u) + stays(g), monks(g), len(g))))
                    pick = max(gs, key=lambda g: (len(best & set(g)), len(g)))
                    prev, together = frozenset(pick), False
                else:                                         # divided: the main team is the group its players are in
                    ov = sorted(((len(prev & set(g)), flags(g, u), len(g), g) for g in gs), key=lambda x: (-x[0], -x[1], -x[2]))
                    if ov[0][0] >= 1: prev = frozenset(ov[0][3])
                    else: prev = frozenset()
                if not together:                              # one part on the front lane and the others round the back: that part
                    cand = [g for g in gs if len(g) >= 2]
                    vote = lambda g: sum((self.lane(a, u) == "front") - (self.lane(a, u) == "back") for a in g)
                    fr = [g for g in cand if vote(g) > 0]
                    if len(fr) == 1 and len(cand) > 1 and all(vote(g) < 0 for g in cand if g is not fr[0]): prev = frozenset(fr[0])
                    big = [g for g in cand if len(g) >= MAIN_BIG and all(len(g) >= len(h) + 2 for h in gs if h is not g) and vote(g) >= 0]
                    if big: prev = frozenset(big[0])          # an uneven divide: the part of five or more, two bigger than any other and not round the back, is the main team (R-421: NwAy v SKT 14:50, SKT's five pushing NwAy's front door; R-335 and R-355 keep the even 4 v 4)
                out[u] = prev
            self._mt[tm] = out; self._lost[tm] = lost
        return self._mt[tm][t - t % SPLIT_STEP]

    def main_lost(self, tm, t):
        """How many of the main team's players are dead at second t, having died as main team (R-392)."""
        self.main_team(tm, t)
        return self._lost[tm][t - t % SPLIT_STEP]

    def _over(self, tm, t):
        """(players of tm on a split, players of its main team pushing, the rest alive) at second t. On the enemy's
        ground and not standing with team mates who are not: with the main team it is a main team push (R-364),
        otherwise a split. A player walking in to join a main team that is already over there is doing neither."""
        k = (tm, t)
        if k not in self._ov:
            live = [a for a in self.st.players[tm] if self.AL[a][t]]
            deep = [a for a in live if self._deep(a, t)]
            rest = [a for a in live if a not in deep]
            deep = [a for a in deep if not any(d(self.P[a][t], self.P[b][t]) < FIGHT_LINK for b in rest)]
            main = self.main_team(tm, t)
            mc = self.centre([a for a in main if a in rest], t)   # out in the field counts only well away from the main team
            deep = [a for a in deep if a in main or self._deep(a, t) != "field" or mc is None or d(self.P[a][t], mc) >= MEET_R]
            push = [a for a in deep if a in main]
            if len(live) + self.main_lost(tm, t) - len(deep) < 3 and len(deep) > len(push): push = deep       # nobody left to be a main team (a main team that is dead still counts, R-392: its split stays a split)
            split = [a for a in deep if a not in push]
            if push and split:
                c0, v = self.centre(push, t), min(t + 6, self.T)
                c1 = self.centre([a for a in push if self.AL[a][v]], v) or c0
                split = [a for a in split if not (self.AL[a][v] and d(self.P[a][v], c1) < d(self.P[a][t], c0) - 600)]
            self._ov[k] = (split, push, [a for a in live if a not in deep])
        return self._ov[k]

    def _cluster(self, ids, t):
        gs = []
        for a in ids:
            hit = [g for g in gs if any(d(self.P[a][t], self.P[b][t]) < FIGHT_LINK for b in g)]
            gs = [g for g in gs if g not in hit] + [[a] + [x for g in hit for x in g]]
        return max(gs, key=len) if gs else []

    def attempts(self):
        """Every split attempt and every main team push of the match, one record each (Denning, R-362: the record is
        the work). An attempt runs from the moment its first player leaves his team (0:00 allowed, R-357) until its
        players are back with their team, dead, or back on their own side of the stand for SPLIT_GAP_S (R-363); going
        in and out of the enemy base stays one attempt. Each record: who (roles, monks), the way in, where; the answer
        (who defended, monks, how far behind, met outside the base or in it); what the splitting team's main team had
        meanwhile (numbers where it fought); how it ended; the result (NPCs, kills, deaths); and the linked moves
        (R-358): a defender arriving and the attackers leaving the base, and a split rejoining its main team ahead of
        its defenders; and, for a main team push, whether it walked its fight onto the enemy's flag (onto_flag, R-401:
        an enemy carrier within PUSHFLAG_R of the pushing players for PUSHFLAG_S or longer)."""
        if self._att is not None: return self._att
        st, m, T, out = self.st, self.m, self.T, []
        R = range(0, T + 1, SPLIT_STEP)
        for tm in st.teams:
            if self.hall is None or tm not in st.side: continue
            foe = 3 - tm
            for kind in ("split", "push"):
                iv = []                                       # (start, end, player) spells over there
                for a in st.players[tm]:
                    on = [t for t in R if a in self._over(tm, t)[kind == "push"]]
                    spells, cur = [], None
                    for t in on:
                        gone = cur is not None and any(not self.AL[a][u] for u in range(cur[1], t))
                        if cur is None or t - cur[1] > SPLIT_GAP_S or gone:
                            if cur: spells.append(cur)
                            cur = [t, t, 0]
                        cur[1] = t; cur[2] += SPLIT_STEP
                    if cur: spells.append(cur)
                    iv += [(s, e, a) for s, e, n in spells if n >= SPLIT_MIN_S]
                iv.sort()
                groups = []
                for s, e, a in iv:
                    if groups and s <= groups[-1]["t1"]: groups[-1]["iv"].append((s, e, a)); groups[-1]["t1"] = max(groups[-1]["t1"], e)
                    else: groups.append({"t_in": s, "t1": e, "iv": [(s, e, a)]})
                for g in groups:
                    if kind == "push" and len({a for _, _, a in g["iv"]}) < 3: continue
                    out.append(self._attempt(tm, foe, kind, g))
        for x in out:                                         # left behind: the last one or two of a main team push that was routed or killed are not a split (Denning, 옷옷옷옷 v Men 5:10: "he just got left behind as the rest of his team wiped")
            if x["kind"] == "split" and x["max"] <= 2 and any(y["kind"] == "push" and y["tm"] == x["tm"] and y["end"] in ("routed", "killed") and y["t1"] - 4 <= x["t_in"] <= y["t1"] + SPLIT_GAP_S
                                                               and set(x["ids"]) <= set(y["ids"]) for y in out):
                x["solo"] = "other"; x["left_behind"] = True
        self._att = sorted(out, key=lambda x: (x["t_in"], x["tm"]))
        return self._att

    def _attempt(self, tm, foe, kind, g):
        st, m, T = self.st, self.m, self.T
        cl = lambda x: max(min(int(x), T), 0)
        t_in, t1 = g["t_in"], g["t1"]
        span = {}
        for s, e, a in g["iv"]: span.setdefault(a, []).append((s, e))
        members = sorted(span, key=lambda a: span[a][0][0])
        on = lambda a, t: any(s <= t <= e for s, e in span[a]) and self.AL[a][t]
        R = range(t_in, t1 + 1, SPLIT_STEP)
        # the leaving: back to the last second the first player stood with his team or at home
        def left_at(a):                                   # each member's own leaving, read the same way: who set out together and who came later
            s0 = span[a][0][0]; t_ = s0
            for u in (range(s0, max(s0 - 90, -1), -1) if kind == "split" else ()):
                near = sum(1 for b in st.players[tm] if b != a and b not in span and self.AL[b][u] and self.P[a][u] and d(self.P[a][u], self.P[b][u]) < FIGHT_LINK)
                t_ = u
                if not self.P[a][u] or near >= 3 or (self.at_home(a, u, tm) and not self._deep(a, u)): break
            return t_
        left = {a: left_at(a) for a in members}
        a0, t0 = members[0], left[members[0]]
        ways = collections.Counter(self._deep(a, t) for a in members for t in range(span[a][0][0], min(span[a][0][0] + 40, t1) + 1, SPLIT_STEP) if self._deep(a, t) in ("front door", "back door"))
        places = collections.Counter(self._deep(a, t) for t in R for a in members if on(a, t) and self._deep(a, t))
        sizes = collections.Counter(sum(1 for a in members if on(a, t)) for t in R)
        # the answer
        link, first, arrivals = collections.Counter(), {}, []
        ndef = collections.Counter()
        for t in R:
            ms = [a for a in members if on(a, t)]
            if not ms: continue
            ds = [b for b in st.players[foe] if self.AL[b][t] and any(d(self.P[b][t], self.P[a][t]) < FIGHT_LINK for a in ms)]
            ndef[len(ds)] += 1
            for b in ds:
                if b not in first: first[b] = t
                if link[b] == 0 or t - self._last.get((id(g), b), -99) > SPLIT_GAP_S: arrivals.append((t, b))
                self._last[(id(g), b)] = t; link[b] += SPLIT_STEP
        died_on = {b for a in members for td in st.death_times.get(a, []) if any(s_ - 1 <= td <= e_ + 4 for s_, e_ in span[a])
                   for b in link if self.AL[b][cl(td - 1)] and self.P[a][cl(td - 1)] and d(self.P[b][cl(td - 1)], self.P[a][cl(td - 1)]) < FIGHT_LINK}
        traded = collections.Counter()                    # damage traded with the split: a defender even when he stood off it (a ranger 1v1)
        for t in range(t_in, min(t1 + 10, T) + 1):
            for x_, y_ in self.hits.get(t, ()):
                for mine, his in ((x_, y_), (y_, x_)):
                    if mine in span and his in self.P and m.team(his) == foe and (on(mine, t - t % SPLIT_STEP) or t > t1):
                        traded[his] += 1; first.setdefault(his, t)
        defenders = sorted((b for b in set(link) | set(traded) if link[b] >= JOIN_S or b in died_on or traded[b] >= 3), key=lambda b: first[b])
        # who went home to cover it without reaching it (R-358: an answer is also the players it pulls back)
        homeg = ("pit", "base", "front door", "back door", "front footies", "back footies")
        def home(b, u):
            if not self.AL[b][u]: return False
            k_, sd = self.place_at(b, u)
            return sd == st.side.get(foe) and k_ in homeg
        fm = self.main_team(foe, t_in)
        covered, away = [], []
        if kind == "split":
            for b in st.players[foe]:
                if b in defenders or home(b, max(t0 - 2, 0)): continue
                hs = [t for t in R if home(b, t) and (b not in self.main_team(foe, t) or not self._over(tm, t)[1])]      # his whole main team going home counts too, unless the split's main team pushed it there
                if len(hs) * SPLIT_STEP >= JOIN_S: covered.append((hs[0], b))
                if sum(1 for t in hs if b not in self.main_team(foe, t)) * SPLIT_STEP >= JOIN_S: away.append(b)      # ... and those who left their main team to do it
        covered_t = min((t for t, _ in covered), default=None)
        covered = [b for _, b in sorted(covered)]
        swaps = []                                        # a swap in the answer (R-374): one player covering the split goes and another comes within SWAP_S, on it or standing off it at home
        if kind == "split":
            spells = {}
            for b in set(defenders) | set(covered):
                on_it = [t for t in R if self.AL[b][t] and (any(on(a, t) and d(self.P[b][t], self.P[a][t]) < FIGHT_LINK for a in members) or (home(b, t) and b not in self.main_team(foe, t)))]
                cur = None
                for t in on_it:
                    if cur is not None and t - cur[1] <= SPLIT_GAP_S: cur[1] = t
                    else:
                        cur = [t, t]; spells.setdefault(b, []).append(cur)
            def stood(b, u, v):                           # where he mostly stood over a spell (the middle of his positions)
                ps = [self.P[b][t] for t in range(u, v + 1, SPLIT_STEP) if self.P[b][t]]
                return (statistics.median(p[0] for p in ps), statistics.median(p[1] for p in ps))
            for b1, xs in spells.items():
                for s1, e1 in xs:
                    if e1 - s1 < SWAP_STAY_S or e1 >= t1 - SPLIT_STEP or any(0 < s_ - e1 <= SWAP_STAY_S for s_, _ in xs): continue
                    for b2, ys in spells.items():
                        y = next(((s2, e2) for s2, e2 in ys if b2 != b1 and abs(s2 - e1) <= SWAP_S and s2 > s1 + SWAP_STAY_S and e2 - s2 >= SWAP_STAY_S and e2 > e1 + SWAP_STAY_S
                                  and d(stood(b2, s2, e2), stood(b1, s1, e1)) < FIGHT_LINK), None)      # he comes to stand where the other stood
                        if y and not any(w["in_id"] == b2 and w["t_in"] == y[0] for w in swaps): swaps.append({"t": max(y[0], e1), "in": m.roles[b2], "out": m.roles[b1], "in_id": b2, "out_id": b1, "t_in": y[0], "t_out": e1}); break
            swaps.sort(key=lambda w: w["t"])
        t_met = min((first[b] for b in defenders), default=None)
        met = None
        if t_met is not None:
            ks = collections.Counter(self._deep(a, t_met) for a in members if on(a, t_met) and self._deep(a, t_met))
            met = ("outside the base" if max(ks, key=ks.get) == "field" else "at the " + max(ks, key=ks.get)) if ks else None
        usual = max((n for n in ndef if n), key=lambda n: ndef[n], default=0)
        # the main team meanwhile (a split only): numbers where the rest of the team fought
        diffs, contact = collections.Counter(), 0
        if kind == "split":
            for t in R:
                rest = [a for a in self.main_team(tm, t) if self.AL[a][t] and a not in span]
                en = [b for b in st.players[foe] if self.AL[b][t] and b not in defenders and any(d(self.P[b][t], self.P[a][t]) < FIGHT_LINK for a in rest)]
                if rest and en: diffs["up" if len(rest) > len(en) else "down" if len(rest) < len(en) else "even"] += SPLIT_STEP; contact += 1
        # deaths, kills, NPCs
        def chased(a, td):                                # died on the way out, a defender still on him
            u = cl(td - 1)
            return bool(self.P[a][u]) and any(self.AL[x][u] and d(self.P[a][u], self.P[x][u]) < FIGHT_LINK for x in defenders)
        lost = [(td, a) for a in members for td in st.death_times.get(a, [])
                if any(s - 1 <= td <= e + 4 or (e < td <= e + SPLIT_GAP_S and chased(a, td)) for s, e in span[a])]
        kills = [(td, b) for b in st.players[foe] for td in st.death_times.get(b, [])
                 if t_in <= td <= t1 + 4 and any(on(a, cl(td)) and self.P[b][cl(td - 1)] and d(self.P[a][cl(td)], self.P[b][cl(td - 1)]) < FIGHT_LINK for a in members)]
        npcs = []
        for x, td in st.npc_dead.items():
            v = st.geo.npcs.get(x)
            if not v or v.get("team") != foe or not (t_in <= td <= t1 + 4): continue
            u = cl(td)
            lastp = lambda a: next((self.P[a][x] for x in range(u, max(u - 6, -1), -1) if self.P[a][x] and any(s_ <= x <= e_ + 2 for s_, e_ in span[a])), None)
            if v.get("pos") is None or any(lastp(a) and d(lastp(a), v["pos"]) < NPC_NEAR for a in members): npcs.append((td, v["kind"].replace("_", " ")))
        for td in self.foot_dead.get(foe, ()):
            u = cl(td)
            if t_in <= td <= t1 + 4 and any(on(a, u) and str(self._deep(a, u) or "").endswith("footies") for a in members): npcs.append((td, "footman"))
        # how it ended
        alive_end = [a for a in members if not any(span[a][-1][1] - 2 <= td <= span[a][-1][1] + 5 for td in st.death_times.get(a, []))]
        late = [a for td, a in lost if td >= t1 - 40]
        alive_end = [a for a in alive_end if not any(t1 < td <= t1 + SPLIT_GAP_S for td, x in lost if x == a)]
        u = min(t1 + SPLIT_STEP * 3, T)
        if t1 >= T - 4: end = "match ended"
        elif not alive_end: end = "killed"
        elif kind == "split" and any(a in self._over(tm, u)[1] for a in alive_end): end = "main team joined"
        elif late: end = "routed"
        else: end = "left"
        after = went = None
        if end in ("left", "routed") and alive_end:
            u = min(t1 + SPLIT_GAP_S, T)
            a = alive_end[0]
            with_team = sum(1 for b in st.players[tm] if b not in span and self.AL[b][u] and self.AL[a][u] and d(self.P[a][u], self.P[b][u]) < FIGHT_LINK)
            after = "rejoined the main team" if with_team >= 3 else ("went home" if self.AL[a][u] and self.at_home(a, u, tm) else "elsewhere")
            ws = collections.Counter(self.place_at(b, u) for b in alive_end if self.AL[b][u])      # where it stood SPLIT_GAP_S after leaving: on its own ground it fell back there
            if ws and after != "rejoined the main team":
                (k_, sd_), n_ = ws.most_common(1)[0]
                if sd_ == st.side.get(tm) and k_ != "field" and n_ * 2 >= len(alive_end): went = self.place_words(k_, sd_)
        # linked moves (R-358)
        depth = {"pit": 3, "base": 2, "front footies": 2, "back footies": 2, "front door": 1, "back door": 1, "field": 0}
        lvl = {}
        for t in R:
            xs = sorted(depth.get(self._deep(a, t), 0) for a in members if on(a, t))
            lvl[t] = xs[len(xs) // 2] if xs else None
        ts = [t for t in R if lvl[t] is not None]
        backs = [t for i, t in enumerate(ts) if i and lvl[ts[i - 1]] > lvl[t] and all(lvl[x] <= lvl[t] for x in ts[i:i + 4])]
        forced = []
        came = [(t, b) for b in st.players[foe] for t in R if t >= t_in + 10 and home(b, t) and not any(home(b, t - k) for k in range(SPLIT_STEP, 12, SPLIT_STEP) if t - k >= 0)]
        for to in backs:
            near = sorted([(ta, b) for ta, b in arrivals if b in defenders and -8 <= to - ta <= FORCED_OUT_S] + [(ta, b) for ta, b in came if -8 <= to - ta <= FORCED_OUT_S])
            if near: forced.append({"defender": m.roles[near[0][1]], "arrived": near[0][0], "left": to})
        ahead = None
        back = defenders + away                           # who has to come back from it: a main team that went home together is already together
        if kind == "split" and after == "rejoined the main team" and back:
            tj = next((u for u in range(t1, min(t1 + AHEAD_LOOK_S, T) + 1) if any(self.AL[a][u] and sum(1 for b in st.players[tm] if b not in span and self.AL[b][u] and d(self.P[a][u], self.P[b][u]) < FIGHT_LINK) >= 3 for a in alive_end)), None)
            others = [b for b in st.players[foe] if b not in back]
            td_ = next((u for u in range(max(t1 - 20, 0), min(t1 + AHEAD_LOOK_S + 30, T) + 1) if any(self.AL[b][u] and sum(1 for c in others if self.AL[c][u] and d(self.P[b][u], self.P[c][u]) < FIGHT_LINK) >= 3 for b in back)), None)
            if tj is not None and td_ is not None:
                lead = td_ - tj
                win = (min(tj, td_), max(tj, td_) + 10)
                ahead = {"split_back": tj, "defenders_back": td_, "lead_s": lead,
                         "kills_for": sum(1 for b in st.players[foe] for x in st.death_times.get(b, []) if win[0] <= x <= win[1]),
                         "kills_against": sum(1 for b in st.players[tm] for x in st.death_times.get(b, []) if win[0] <= x <= win[1])}
        mk = lambda ids: sum(1 for a in ids if m.A[a].get("p") == "Monk" and not m.roles[a].startswith("Monk "))   # backline monks, not a smiter
        onto = None                                       # R-401: a main team push that walks its fight onto the enemy's flag, held by a player standing in his team
        if kind == "push":
            secs, first_t = collections.Counter(), {}
            for t in R:
                ms = [a for a in members if on(a, t)]
                for b in st.players[foe]:
                    if self.AL[b][t] and self.carrying(b, t) and any(d(self.P[b][t], self.P[a][t]) < PUSHFLAG_R for a in ms): secs[b] += SPLIT_STEP; first_t.setdefault(b, t)
            if secs and max(secs.values()) >= PUSHFLAG_S:
                b = max(secs, key=secs.get)
                onto = {"role": m.roles[b], "id": b, "t": first_t[b], "s": secs[b], "place": self.place_words(*self.place_at(b, first_t[b]))}
        solo = None                                       # R-381: a lone player is splitting only when he hits NPCs or trades damage with a defender
        if kind == "split" and max(sizes) == 1:
            busy = bool(npcs) or sum(traded.values()) >= 2 or any(t_in <= x <= t1 + 4 for a in members for x in self.npc_hits.get(a, ()))
            solo = "split" if busy else "other"
        n_in = None                                       # the numbers as the push goes in, read as the fight lines read them: the usual numbers over its fight's first JOIN_S (R-350), not the push's usual size against the usual defenders over the whole push (golden game 1, 3:32: 6 v 3)
        if kind == "push":
            seen, f0 = collections.Counter(), None
            for t in range(t_in - t_in % SPLIT_STEP, min(t_in + 3 * JOIN_S, T) + 1, SPLIT_STEP):
                if f0 is not None and t > f0 + JOIN_S: break
                fs = [f for f in self.fights(t) if f["n"][1] and f["n"][2] and len(f["ids"][tm] & set(members)) * 2 >= len([a for a in members if on(a, t)] or [0])]
                if fs:
                    f = max(fs, key=lambda f: len(f["ids"][tm] & set(members)))
                    f0 = t if f0 is None else f0; seen[(f["n"][tm], f["n"][foe])] += 1
            if seen: n_in = max(seen, key=lambda k: (seen[k], k))
        return {"kind": kind, "tm": tm, "solo": solo, "team": m.tag[tm], "t0": t0, "t_in": t_in, "t1": t1, "opening": t_in <= 75, "n_in": n_in,
                "members": [{"role": m.roles[a], "prof": m.A[a].get("p"), "from": span[a][0][0], "to": span[a][-1][1], "left": left[a]} for a in members],
                "ids": members, "size": max(sizes, key=lambda n: (sizes[n], n)), "max": max(sizes), "monks": mk(members),
                "flag_player": self.flag_player(tm, t_in) in members,
                "carried_flag": any(self.carrying(a, t) and on(a, t) for a in members for t in R),
                "way": max(ways, key=ways.get) if ways else None, "where": max(places, key=places.get) if places else None,
                "answer": {"defenders": [m.roles[b] for b in defenders], "ids": defenders, "n": usual, "max": max(ndef) if ndef else 0, "monks": mk(defenders),
                           "behind_s": (t_met - t_in) if t_met is not None else None, "met": met, "arrivals": [(first[b], m.roles[b]) for b in defenders], "went_back": [m.roles[b] for b in covered], "went_back_ids": covered,
                           "went_back_t": covered_t, "swaps": swaps},
                "main": {"contact_s": contact * SPLIT_STEP, "up_s": diffs["up"], "even_s": diffs["even"], "down_s": diffs["down"]},
                "end": end, "after": after, "went": went, "lost": [m.roles[a] for _, a in sorted(lost)], "kills": [m.roles[b] for _, b in sorted(kills)],
                "npcs": [k for _, k in sorted(npcs)], "forced_out": forced, "ahead": ahead, "onto_flag": onto}

    def way_out(self):
        """A team going out of its base by a door (his commentary: "sends six out the back door"), one record each
        time: three or more of a team, half of them or more its main team, pass out of their own base or pit along the
        same drawn door (or past that door's footies) within WAY_OUT_GAP_S of each other and are still out of their
        own ground WAY_OUT_GAP_S later. Each record: when the first of them reached the door, the team, the door, who."""
        if self._wo is not None: return self._wo
        st, m, T, ev = self.st, self.m, self.T, []
        doorof = {"front door": "front door", "back door": "back door", "front footies": "front door", "back footies": "back door"}
        for tm in st.teams:
            own = st.side.get(tm)
            if self.hall is None or own is None: continue
            for a in st.players[tm]:
                inside, door, t_door = True, None, None        # everyone starts in his base
                for u in range(0, T + 1, SPLIT_STEP):
                    if not self.AL[a][u]: inside, door = False, None; continue
                    k, sd = self.place_at(a, u)
                    if sd == own and k in ("pit", "base"): inside, door, t_door = True, None, None
                    elif sd == own and k in doorof:
                        if inside: door, t_door = doorof[k], (u if door is None else t_door)      # the last door he is on before he is out (two doors can leave by one corridor)
                    else:
                        if inside and door is not None and u - t_door <= 60: ev.append((tm, door, u, t_door, a))
                        inside, door = False, None
        ev.sort(key=lambda x: (x[0], x[1], x[2]))
        groups = []
        for tm, door, u, t_door, a in ev:
            g = groups[-1] if groups else None
            if g and g["tm"] == tm and g["door"] == door and u - g["t1"] <= WAY_OUT_GAP_S: g["ids"].append(a); g["t1"] = u; g["t"] = min(g["t"], t_door)
            else: groups.append({"tm": tm, "door": door, "t": t_door, "t1": u, "ids": [a]})
        out = []
        for g in groups:
            v = min(g["t1"] + WAY_OUT_GAP_S, T); own = st.side.get(g["tm"])
            still = [a for a in g["ids"] if self.AL[a][v] and not (self.place_at(a, v)[1] == own and self.place_at(a, v)[0] in ("pit", "base") + tuple(doorof))]
            main = self.main_team(g["tm"], min(g["t1"] + 4 - (g["t1"] + 4) % SPLIT_STEP, T))
            if len(g["ids"]) < 3 or len(still) * 2 < len(g["ids"]) or sum(1 for a in g["ids"] if a in main) * 2 < len(g["ids"]): continue
            out.append(dict(g, team=m.tag[g["tm"]], n=len(g["ids"]), roles=[m.roles[a] for a in g["ids"]]))
        self._wo = sorted(out, key=lambda g: g["t"])
        return self._wo

    # ---- joins, leaves and swaps; the split fight record (R-365, R-374)
    def _fight_index(self):
        """second -> {player: the fight he stands in}, for fights with both teams in them, read every SPLIT_STEP."""
        if self._fi is None:
            self._fi = {}
            for t in range(0, self.T + 1, SPLIT_STEP):
                row = {}
                for f in self.fights(t):
                    if f["n"][1] and f["n"][2]:
                        for a in f["ids"][1] | f["ids"][2]: row[a] = f
                self._fi[t] = row
        return self._fi

    def on_pit(self):
        """Who is on the pit NPCs (R-378, R-387): one record each stretch in which a team trades damage with the
        enemy's knights, bodyguard or Guild Lord, a stretch ending after 30 s without any. Each record: when, the
        attacking team, whose pit, the players on them, and which NPCs."""
        out = []
        for tm_s, act in self.pit_act.items():
            cur = None
            for u in sorted(act):
                if cur is not None and u - cur["t1"] <= 30: cur["t1"] = u; cur["ids"] |= act[u]; cur["npcs"] |= self.pit_kind[tm_s][u]
                else:
                    cur = {"t": u, "t1": u, "tm": 3 - tm_s, "team": self.m.tag[3 - tm_s], "foe": self.m.tag[tm_s], "ids": set(act[u]), "npcs": set(self.pit_kind[tm_s][u])}
                    out.append(cur)
        for r in out: r["roles"] = sorted(self.m.roles[a] for a in r["ids"])
        return sorted(out, key=lambda r: r["t"])

    def undefended(self):
        """When a split is left with nobody defending it (R-374: "hdm's ranger is undefended"). The answer in an
        attempt's record is who met it; this follows it afterwards: each stretch of UNDEFENDED_S or longer, during an
        attempt, with no living enemy within FIGHT_LINK of any of its players on the enemy's ground. One record a
        stretch: when it starts and ends, the splitting team, who is on it, where, and whether it had been defended."""
        if self._und is not None: return self._und
        st, m, S, out = self.st, self.m, SPLIT_STEP, []
        for x in self.attempts():
            if x.get("kind") != "split" or x.get("solo") == "other": continue
            tm = x["tm"]; foe = 3 - tm
            ids = [a for a in st.players[tm] if m.roles[a] in {y["role"] for y in x["members"]}]
            span = {a: next((y["from"], y["to"]) for y in x["members"] if y["role"] == m.roles[a]) for a in ids}
            cur, had = None, False
            for u in range(int(x["t_in"]) - int(x["t_in"]) % S, min(int(x["t1"]), self.T) + 1, S):
                on = [a for a in ids if span[a][0] <= u <= span[a][1] and self.AL[a][u] and self.P[a][u]]
                near = on and any(self.AL[e][u] and self.P[e][u] and d(self.P[e][u], self.P[a][u]) < FIGHT_LINK for e in st.players[foe] for a in on)
                if on and not near:
                    if cur is None: cur = {"t": u, "t1": u, "ids": on, "had": had}
                    cur["t1"] = u
                else:
                    if cur and cur["t1"] - cur["t"] >= UNDEFENDED_S: out.append(cur)
                    cur = None; had = had or bool(near)
            if cur and cur["t1"] - cur["t"] >= UNDEFENDED_S: out.append(cur)
            for r in out:
                if "team" not in r:
                    z = collections.Counter(self.place_at(a, u) for a in r["ids"] for u in range(r["t"], r["t1"] + 1, 6) if self.AL[a][u] and self.P[a][u])
                    r.update(team=x["team"], foe=m.tag[foe], roles=[m.roles[a] for a in r["ids"]], place=self.place_words(*max(z, key=lambda k: (z[k], str(k)))))
        self._und = sorted(out, key=lambda r: r["t"])
        return self._und

    def ground(self):
        """Ground, one record each time a group moves up or back (R-374: "falls back to its footies", "pushes up to
        the front door", "the split is pushed toward its pit"). Read for each main team and for each side of a split
        fight. A group's depth is the walked distance of its middle player from its own Guild Lord, read every 2 s; a
        move is GROUND_MOVE or more of it covered within GROUND_S by the same players, ended once the group comes
        GROUND_BACK the other way. The reading starts again when the depth jumps (a wipe and a base res, or the group
        being different players), so those are never told as moves. Each record: when it started and ended, the team,
        which group (main or split), back or up, where from and to, how far, who, the enemy next to it at the start
        (pressed) and at the end (followed), and whether the two were trading damage as it began."""
        if self._gr is not None: return self._gr
        st, m, hall, T, S = self.st, self.m, self.hall, self.T, SPLIT_STEP
        out = []
        def read(tm, row, group):
            side, foe = st.side.get(tm), 3 - tm
            MOVE = GROUND_MOVE if group == "main" else GROUND_SPLIT_MOVE; BACK = MOVE // 2
            fld = hall.to(hall.lord[side])
            dep = lambda x, u: fld.get(hall.snap(self.P[x][u]))
            row = [(u, (lambda ds: statistics.median(ds) if len(ds) >= 2 else None)(sorted(v for v in (dep(x, u) for x in g) if v is not None)), g) for u, g in row]
            runs, cur = [], []
            for x in row:                                    # unbroken stretches of walking
                if x[1] is None or (cur and abs(x[1] - cur[-1][1]) > GROUND_JUMP):
                    if len(cur) > 2: runs.append(cur)
                    cur = [] if x[1] is None else [x]
                else: cur.append(x)
            if len(cur) > 2: runs.append(cur)
            for run in runs:
                segs, piv, ext, way = [], 0, 0, 0
                for i in range(1, len(run)):
                    dv = run[i][1] - run[ext][1]
                    if way == 0:
                        if abs(run[i][1] - run[piv][1]) >= BACK: way, ext = (1 if run[i][1] > run[piv][1] else -1), i
                    elif dv * way > 0: ext = i
                    elif -dv * way >= BACK:
                        segs.append((piv, ext, way)); piv, ext, way = ext, i, -way
                if way: segs.append((piv, ext, way))
                for i0, i1, way in segs:
                    full = run[i1][1] - run[i0][1]
                    if abs(full) < MOVE: continue
                    a = max(i for i in range(i0, i1 + 1) if abs(run[i][1] - run[i0][1]) <= 0.15 * abs(full))
                    b = min(i for i in range(a, i1 + 1) if abs(run[i][1] - run[i1][1]) <= 0.15 * abs(full))
                    best, fast = None, a                      # the fastest GROUND_MOVE inside it must fit in GROUND_S; the move is told from there
                    for i in range(a, b + 1):
                        j = next((j for j in range(i + 1, b + 1) if abs(run[j][1] - run[i][1]) >= MOVE), None)
                        if j is not None and (best is None or run[j][0] - run[i][0] < best): best, fast = run[j][0] - run[i][0], i
                    if best is None or best > GROUND_S: continue
                    u0, u1, g0, g1 = run[a][0], run[b][0], run[a][2], run[b][2]
                    same = [x for x in g0 if x in g1]         # the same players must have made the move: a group that only gains or loses players has not moved
                    dd = [dep(x, u1) - dep(x, u0) for x in same if dep(x, u0) is not None and dep(x, u1) is not None]
                    if len(dd) < 2 or len(dd) * 2 < len(g0) or statistics.median(dd) * way < MOVE * 0.75: continue
                    def where(g, u):
                        z = collections.Counter(self.place_at(x, u) for x in g)
                        return max(z, key=lambda k: (z[k], str(k)))
                    near = lambda g, u: [e for e in st.players[foe] if self.AL[e][u] and self.P[e][u] and any(d(self.P[e][u], self.P[x][u]) < FIGHT_LINK for x in g)]
                    k0, k1 = where(g0, u0), where(g1, u1)
                    if way < 0:                               # a fall back that comes to rest at the team's own footies is told as falling to them (R-307, R-391),
                        ke = where([x for x in run[i1][2] if x in g0] or run[i1][2], run[i1][0])      # though most of the way was covered before reaching them
                        if ke[0].endswith("footies") and ke[1] == side: k1 = ke
                    out.append({"t": run[fast][0], "t0": u0, "t1": u1, "team": m.tag[tm], "tm": tm, "group": group, "way": "up" if way > 0 else "back", "dist": round(abs(run[b][1] - run[a][1])),
                                "from": self.place_words(*k0), "to": self.place_words(*k1), "from_kind": k0[0], "from_side": k0[1], "to_kind": k1[0], "to_side": k1[1],
                                "ids": sorted(g0), "n": len(g0), "pressed": len(near(g0, u0)), "followed": len(near(g1, u1)),
                                "fighting": self.contact(set(g0), set(st.players[foe]), max(u0 - 10, 0), u0)})
        if hall is not None:
            for tm in st.teams:
                if st.side.get(tm) is None: continue
                read(tm, [(u, [x for x in self.main_team(tm, u) if self.AL[x][u] and self.P[x][u]]) for u in range(0, T + 1, S)], "main")
                for r in self.split_fights():
                    mem = [x for x in r["members"][m.tag[tm]]]
                    read(tm, [(u, [x["id"] for x in mem if any(s_ <= u <= e for s_, e in x["spans"]) and self.AL[x["id"]][u] and self.P[x["id"]][u]])
                              for u in range(int(r["t0"]) - int(r["t0"]) % S, int(r["t1"]) + 1, S)], "split")
        self._gr = sorted(out, key=lambda x: x["t"])
        return self._gr

    def moves(self):
        """Every join, leave and swap at a fight, one record each (R-374): the collapses and rotations Denning calls.
        Read player by player, so a fight that breaks up or merges does not hide it. A player joins when he comes to
        stand in a fight (JOIN_S or longer, R-350) with players he was not with JOIN_LOOK_S earlier, having moved
        JOIN_MOVE or more and JOIN_LEAD times further than they did (otherwise the fight came to him: two groups
        meeting is a fight starting, not a join). A leave is the same read forwards, for a player who stays alive. Each
        record: the second, the team, who, the place, the numbers before and after, whether he came from a res,
        whether he left for the flag and where a leaver went. Swaps are read inside a split fight (split_fights)."""
        if self._mv is not None: return self._mv
        m, T, S = self.m, self.T, SPLIT_STEP
        idx = self._fight_index()
        comp = lambda a, t: ((idx[t][a]["ids"][1] | idx[t][a]["ids"][2]) - {a}) if a in idx[t] else frozenset()
        def travel(ids, u, v):
            ids = [x for x in ids if self.AL[x][u] and self.AL[x][v]]
            return d(self.centre(ids, u), self.centre(ids, v)) if ids else None
        def engaged(f, t):                                   # the two sides of that group trade damage or stand within an aggro bubble (JOIN_ENGAGE)
            i1, i2 = f["ids"][1], f["ids"][2]
            if any(d(self.P[x][t], self.P[y][t]) < JOIN_ENGAGE for x in i1 for y in i2 if self.AL[x][t] and self.AL[y][t]): return True
            return any((x in i1 and y in i2) or (x in i2 and y in i1) for u in range(max(t - JOIN_ENGAGE_S, 0), min(t + JOIN_ENGAGE_S, T) + 1) for x, y in self.acts.get(u, ()))
        ev = []
        for a in m.PL:
            tm, stays, cur = m.team(a), [], None
            for t in range(0, T + 1, S):
                c = comp(a, t)
                if not c: continue
                if cur is not None and t - cur["t1"] <= JOIN_S and len(c & cur["last"]) * 2 >= min(len(c), len(cur["last"])): cur["t1"], cur["last"] = t, c      # out of it for less than JOIN_S is not a leave (R-350)
                else:
                    if cur: stays.append(cur)
                    cur = {"t0": t, "t1": t, "first": c, "last": c}
            if cur: stays.append(cur)
            for s_ in stays:
                t0, t1 = s_["t0"], s_["t1"]
                if t1 - t0 < JOIN_S: continue
                u = max(t0 - JOIN_LOOK_S, 0)
                ua = next((x for x in range(u, t0) if self.AL[a][x]), None)
                if t0 >= 6 and len(s_["first"]) >= 2 and ua is not None:
                    theirs = travel(s_["first"], u, t0)
                    fresh = [x for x in s_["first"] if x not in comp(a, u - u % S)]
                    mine = d(self.P[a][ua], self.P[a][t0])
                    if theirs is not None and len(fresh) * 2 >= len(s_["first"]) and mine >= JOIN_MOVE and mine >= JOIN_LEAD * theirs and engaged(idx[t0][a], t0):
                        f = idx[t0][a]
                        ev.append({"t": t0, "kind": "join", "tm": tm, "ids": [a], "with": s_["first"], "place": f["place"], "n": (f["n"][1], f["n"][2]),
                                   "res": any(t0 - 60 <= td <= t0 for td in self.st.death_times.get(a, [])), "stay_s": t1 - t0})
                v = min(t1 + JOIN_LOOK_S, T)
                if t1 <= T - 6 and len(s_["last"]) >= 2 and all(self.AL[a][x] for x in range(t1, v + 1)):
                    theirs = travel(s_["last"], t1, v)
                    mine = d(self.P[a][t1], self.P[a][v])
                    foes = travel([x for x in s_["last"] if m.team(x) != tm], t1, v)      # he went further than the enemy he faced: if the enemy walked off and he stayed, he did not leave (golden game 1, 7:24)
                    if theirs is not None and len(comp(a, v - v % S) & s_["last"]) * 2 < len(s_["last"]) and mine >= JOIN_MOVE and mine >= JOIN_LEAD * theirs and (foes is None or mine > foes) and engaged(idx[t1][a], t1):
                        f = idx[t1][a]
                        ev.append({"t": t1, "kind": "leave", "tm": tm, "ids": [a], "with": s_["last"], "place": f["place"], "n": (f["n"][1], f["n"][2]),
                                   "flag": any(t1 <= p <= t1 + 60 for p in self.pick.get(a, ())), "stay_s": t1 - t0, "to": self.place_words(*self.place_at(a, v))})
        ev.sort(key=lambda x: (x["kind"], x["tm"], x["t"]))
        merged = []
        for x in ev:                                         # players arriving or leaving together are one move
            y = merged[-1] if merged else None
            if y and y["kind"] == x["kind"] and y["tm"] == x["tm"] and x["t"] - y["t1"] <= 6 and (len(x["with"] & y["with"]) >= 2 or set(x["ids"]) & y["with"] or set(y["ids"]) & x["with"]):
                y["ids"] += x["ids"]; y["each"].append((x["ids"][0], x["t"], x["stay_s"])); y["t1"] = x["t"]; y["with"] = y["with"] | x["with"]
                y["res"] = y.get("res") and x.get("res"); y["flag"] = y.get("flag") and x.get("flag")
                if x["kind"] == "join": y["n"], y["place"] = x["n"], x["place"]
            else: merged.append(dict(x, t1=x["t"], each=[(x["ids"][0], x["t"], x["stay_s"])]))
        for x in merged:
            k = len(x["ids"]); n = x["n"]
            side = (k, 0) if x["tm"] == 1 else (0, k)
            if x["kind"] == "join": x["before"], x["after"] = (max(n[0] - side[0], 0), max(n[1] - side[1], 0)), n
            else: x["before"], x["after"] = n, (max(n[0] - side[0], 0), max(n[1] - side[1], 0))
            x["roles"] = [m.roles[a] for a in x["ids"]]; x["team"] = m.tag[x["tm"]]
        self._mv = sorted(merged, key=lambda x: x["t"])
        return self._mv

    def split_fights(self):
        """The split fights of the match, one record each (R-365): a fight away from both main teams, at least
        SPLIT_FIGHT_MIN a side when it opens, kept as one record for as long as the same two groups stay on each other,
        wherever it drifts and whoever is pushing (out of contact for up to SPLIT_FIGHT_GAP_S is still the same fight).
        Each record: when, who on each side and from when to when, who started it (whose ground it opened on), the
        seconds on each team's ground and between them, the usual numbers and monks a side (R-378), the joins, leaves
        and swaps inside it (moves), who was pulled off it onto the main fight (pulled), NPCs taken and deaths by side, what the main teams had meanwhile, and the split
        attempts it covers (those are told as this one fight, not as separate splits)."""
        if self._sf is not None: return self._sf
        st, m, T, S = self.st, self.m, self.T, SPLIT_STEP
        side_tm = {v: k for k, v in st.side.items()}
        mainers = {}
        def in_main(ids, tm, t):
            if (tm, t) not in mainers: mainers[(tm, t)] = [a for a in self.main_team(tm, t) if self.AL[a][t]]
            mt = mainers[(tm, t)]
            return bool(mt) and sum(1 for a in mt if a in ids) * 2 >= len(mt)
        recs, mainn = [], {}
        for t in range(0, T + 1, S):
            for f in self.fights(t):
                n = f["n"]
                if not (n[1] and n[2]): continue
                ids = f["ids"][1] | f["ids"][2]
                if in_main(ids, 1, t) or in_main(ids, 2, t):
                    mainn[t] = (n[1], n[2]); continue
                best = None
                for r in recs:
                    if t - r["seen"] > SPLIT_FIGHT_GAP_S: continue
                    rc = {tm: {a for a, u in r["last"].items() if m.team(a) == tm and t - u <= 30 and self.AL[a][t]} or {a for a, u in r["last"].items() if m.team(a) == tm and u == r["seen"]} for tm in (1, 2)}
                    o1, o2 = len(f["ids"][1] & rc[1]), len(f["ids"][2] & rc[2])
                    if o1 and o2 and (o1 + o2) * 2 >= min(len(ids), len(rc[1]) + len(rc[2])) and (best is None or o1 + o2 > best[0]): best = (o1 + o2, r)
                if best is None:
                    if min(n[1], n[2]) < SPLIT_FIGHT_MIN: continue
                    r = {"t0": t, "seen": t, "last": {}, "at": collections.defaultdict(list), "track": []}
                    recs.append(r)
                else: r = best[1]
                r["seen"] = t
                for a in ids: r["last"][a] = t; r["at"][a].append(t)
                r["track"].append((t, n[1], n[2], f["place"], f["side"], f["kind"]))
        out, atts = [], self.attempts()
        mk = lambda ids: sum(1 for a in ids if m.A[a].get("p") == "Monk" and not m.roles[a].startswith("Monk "))
        cl = lambda x: max(min(int(x), T), 0)
        for r in recs:
            t0, t1 = r["t0"], r["seen"]
            if len(r["track"]) * S < SPLIT_MIN_S or t1 - t0 < SPLIT_MIN_S: continue
            span = {}
            ticks = [x[0] for x in r["track"]]
            for a, ts in r["at"].items():      # a stay ends when the fight goes on without him for JOIN_S of its own time: a lull in the fight itself is not a leave
                sp, had, miss = [], set(ts), 0
                for t in ticks:
                    if t in had:
                        if sp and miss * S <= JOIN_S: sp[-1][1] = t
                        else: sp.append([t, t])
                        miss = 0
                    else: miss += 1
                sp = [(s_, e) for s_, e in sp if e - s_ >= JOIN_S]
                if sp: span[a] = sp
            mem = {tm: sorted((a for a in span if m.team(a) == tm), key=lambda a: span[a][0][0]) for tm in (1, 2)}
            if not (mem[1] and mem[2]): continue
            first = [x for x in r["track"] if x[0] <= t0 + 10]
            sd = collections.Counter(x[4] for x in first).most_common(1)[0][0]
            started = (3 - side_tm[sd]) if sd in side_tm and collections.Counter(x[5] for x in first).most_common(1)[0][0] not in ("stand", "greater stand") else None
            ground = collections.Counter()
            for x in r["track"]: ground[side_tm.get(x[4]) if x[5] not in ("stand", "greater stand", "field") else 0] += S
            nums = collections.Counter((x[1], x[2]) for x in r["track"])
            on = lambda a, t: any(s_ <= t <= e for s_, e in span.get(a, ()))
            monks = {tm: collections.Counter(mk([a for a in mem[tm] if on(a, x[0])]) for x in r["track"]).most_common(1)[0][0] for tm in (1, 2)}
            everyone = set(mem[1]) | set(mem[2])
            inside = [x for x in self.moves() if t0 - 4 <= x["t"] <= t1 + 4 and len(x["with"] & everyone) * 2 >= len(x["with"])]
            pulled = []
            swaps = []         # a swap (R-374): a new player comes into the fight within SWAP_S of one who had been in it leaving it
            for tm_ in (1, 2):
                ins = [(s_, a) for a in mem[tm_] for i, (s_, e) in enumerate(span[a])
                       if s_ > t0 + JOIN_S and e - s_ >= SWAP_STAY_S and not (i and s_ - span[a][i - 1][1] <= 60)]
                outs = [(e, a, e - s_) for a in mem[tm_] for i, (s_, e) in enumerate(span[a])
                        if e < t1 - JOIN_S and e - s_ >= SWAP_STAY_S and not (i + 1 < len(span[a]) and span[a][i + 1][0] - e <= 60)
                        and not any(e - 2 <= td <= e + 6 for td in st.death_times.get(a, []))]
                gone = set()
                for tj, a in sorted(ins):
                    c = [o for o in outs if o[1] != a and abs(o[0] - tj) <= SWAP_S and (o[0], o[1]) not in gone]
                    if c:
                        o = min(c, key=lambda o: (abs(o[0] - tj), -o[2])); gone.add((o[0], o[1]))
                        swaps.append({"t": max(tj, o[0]), "team": m.tag[tm_], "tm": tm_, "in": m.roles[a], "out": m.roles[o[1]], "in_id": a, "out_id": o[1], "t_in": tj, "t_out": o[0]})
                # pulled off the split onto the main fight (Denning: "pulling the ele off the split"): a player who goes out of it
                # as above and, within JOIN_LOOK_S, stands in his main team's fight and is still in it JOIN_S later. Told from
                # here because a split fight that falls back into the main fight for a moment hides it from moves()
                idx = self._fight_index()
                for e, a, _ in outs:
                    u = next((u for u in range(e + S, min(e + JOIN_LOOK_S, T - JOIN_S) + 1, S) if a in idx[u] and in_main(idx[u][a]["ids"][1] | idx[u][a]["ids"][2], tm_, u)), None)
                    if u is None or not all(self.AL[a][x] for x in range(e, u + JOIN_S + 1)): continue
                    v = u + JOIN_S - JOIN_S % S; f = idx[v].get(a)
                    if f is None or not in_main(f["ids"][1] | f["ids"][2], tm_, v) or len(f["ids"][tm_] & set(mem[tm_])) * 2 > f["n"][tm_]: continue      # not when the split fight itself has become the main fight
                    pulled.append({"t": u, "team": m.tag[tm_], "tm": tm_, "role": m.roles[a], "id": a, "t_out": e, "place": f["place"], "n": (f["n"][1], f["n"][2])})
            deaths = {tm: [m.roles[a] for td, a in sorted((td, a) for a in mem[tm] for td in st.death_times.get(a, []) if any(s_ - 1 <= td <= e + 4 for s_, e in span[a]))] for tm in (1, 2)}
            npcs = {1: [], 2: []}
            for x, td in st.npc_dead.items():
                v = st.geo.npcs.get(x)
                if not v or v.get("team") not in (1, 2) or not (t0 <= td <= t1 + 4): continue
                by = 3 - v["team"]; u = cl(td)
                if v.get("pos") is not None and any(on(a, u - u % S) and self.P[a][u] and d(self.P[a][u], v["pos"]) < NPC_NEAR for a in mem[by]): npcs[by].append((td, v["kind"].replace("_", " ")))
            for tm in (1, 2):
                for td in self.foot_dead.get(3 - tm, ()):
                    u = cl(td)
                    if t0 <= td <= t1 + 4 and any(on(a, u - u % S) and str(self._deep(a, u) or "").endswith("footies") for a in mem[tm]): npcs[tm].append((td, "footman"))
            mm = collections.Counter()
            for x in r["track"]:
                if x[0] in mainn: a_, b_ = mainn[x[0]]; mm["up" if a_ > b_ else "down" if a_ < b_ else "even"] += S
            cov = [i for i, x in enumerate(atts) if x["kind"] == "split" and set(x["ids"]) & set(mem[x["tm"]])
                   and (min(x["t1"], t1) - max(x["t_in"], t0)) * 2 >= (x["t1"] - x["t_in"])]
            p0 = collections.Counter(x[3] for x in first).most_common(1)[0][0]
            start = {}
            for tm in (1, 2):
                a0 = [a for a in mem[tm] if span[a][0][0] <= t0 + 20]
                start[tm] = a0 or [a for a in mem[tm] if span[a][0][0] == min(span[b][0][0] for b in mem[tm])]
            left = min((atts[i]["t0"] for i in cov if atts[i]["tm"] == started), default=t0) if started else t0
            away = lambda tm: all(a not in self.main_team(tm, min(20, T)) for a in start[tm])
            both = t0 <= 75 and away(1) and away(2)
            out.append({"t0": t0, "t1": t1, "t_left": min(left, t0), "opening": t0 <= 75, "both_opening": both, "start": {m.tag[tm]: [m.roles[a] for a in start[tm]] for tm in (1, 2)}, "place": p0, "started": m.tag[started] if started else None, "started_tm": started,
                        "members": {m.tag[tm]: [{"role": m.roles[a], "id": a, "from": span[a][0][0], "to": span[a][-1][1], "spans": span[a]} for a in mem[tm]] for tm in (1, 2)},
                        "ids": {tm: mem[tm] for tm in (1, 2)}, "n": max(nums, key=nums.get), "monks": {m.tag[tm]: monks[tm] for tm in (1, 2)},
                        "ground_s": {m.tag[1]: ground[1], m.tag[2]: ground[2], "between": ground[0]}, "linked_s": len(r["track"]) * S,
                        "moves": [{"t": x["t"], "kind": x["kind"], "team": x["team"], "roles": x["roles"]} for x in inside], "swaps": swaps, "pulled": pulled,
                        "npcs": {m.tag[tm]: [k for _, k in sorted(npcs[tm])] for tm in (1, 2)}, "deaths": {m.tag[tm]: deaths[tm] for tm in (1, 2)},
                        "main": {"up_s": mm["up"], "even_s": mm["even"], "down_s": mm["down"]}, "attempts": cov})
        self._sf = out
        return self._sf

    def caught(self):
        """Caught out (R-359): a team in the enemy's base CAUGHT_S or less before the defenders' base res, outnumbered
        or about to be once the dead come back. One record a base res and attacking team, with what followed."""
        st, m, out = self.st, self.m, []
        inb = ("pit", "base", "front door", "back door", "front footies", "back footies")
        for tm in st.teams:
            foe = 3 - tm
            for B in range(RES_EVERY, self.T + 1, RES_EVERY):
                u = B - 6
                att = [a for a in st.players[tm] if self.AL[a][u] and self._deep(a, u) in inb]
                if not att: continue
                res = [b for b in st.players[foe] if not self.AL[b][B - 6] and any(self.AL[b][x] for x in range(B - 3, min(B + 4, self.T) + 1))]   # the replay clock runs up to 2 s off the res
                home = [b for b in st.players[foe] if self.AL[b][u] and any(d(self.P[b][u], self.P[a][u]) < FIGHT_LINK for a in att)]
                since = next((x for x in range(u, max(B - 90, 0), -SPLIT_STEP) if not any(self.AL[a][x] and self._deep(a, x) in inb for a in att)), None)
                if not res: continue
                dead = sorted({m.roles[a] for a in att for td in st.death_times.get(a, []) if B <= td <= B + 60})
                stay = [a for a in att if self.AL[a][min(B + 6, self.T)] and self._deep(a, min(B + 6, self.T)) in inb]
                if not any(self.AL[a][min(B + 2, self.T)] and self._deep(a, min(B + 2, self.T)) in inb for a in att) and all(self.AL[a][min(B + 2, self.T)] for a in att): continue      # all out, alive, by the res: it left before the res (timing), it was not caught
                out.append({"t": B, "tm": tm, "team": m.tag[tm], "attackers": len(att), "defenders": len(home), "coming_back": len(res),
                            "outnumbered": len(att) < len(home) + len(res), "lead_lost": len(att) > len(home) and len(att) <= len(home) + len(res),
                            "went_in": (since + SPLIT_STEP) if since is not None else None, "stayed": len(stay), "lost_after": dead})
        return sorted(out, key=lambda x: x["t"])

    # ---- the flag record: what each flag cost and how it was used (R-360, R-362)
    def flags_record(self):
        """One record a flag life, on top of flag_lives (form, carriers, how it ended): the runner (role, profession),
        when he set off for it and how long he was away from his team for it (R-360: seconds from leaving the group
        to standing with three team mates again, or to the flag's end); whether the next flag was already waiting at
        the spawn when this one ended; a back cap (capped with nobody of the enemy at the stand while the enemy's main
        team stood on the capper's own ground); whether it travelled with a split; where it was dropped; the enemy's
        boost clock when it was picked up and whether it beat that boost; and whether a carrier died holding it."""
        if self._fr is not None: return self._fr
        st, m, T, out = self.st, self.m, self.T, []
        lives = self.flag_lives()
        cl = lambda x: max(min(int(x), T), 0)
        for i, L in enumerate(lives):
            tm, foe = L["team"], 3 - L["team"]
            ser = [c for c in L["carries"] if c[0] in L["serious"]]
            if not ser: continue
            a, tp = ser[0][0], cl(ser[0][1])
            end = cl(L["end"] if L["end"] is not None else (ser[-1][2] if ser[-1][2] is not None else T))
            with_team = lambda x, u: self.AL[x][u] and sum(1 for b in st.players[tm] if b != x and self.AL[b][u] and d(self.P[x][u], self.P[b][u]) < FIGHT_LINK) >= 3
            left = next((u for u in range(tp, max(tp - 90, -1), -1) if with_team(a, u)), None)
            back = next((u for u in range(tp, min(end + 20, T) + 1) if with_team(a, u)), None)
            away = ((back if back is not None else min(end, T)) - (left if left is not None else tp))
            nxt = next((x for x in lives[i + 1:] if x["team"] == tm and any(c[0] in x["serious"] for c in x["carries"])), None)
            n0 = next((c for c in nxt["carries"] if c[0] in nxt["serious"]), None) if nxt else None
            backup = bool(n0) and L["how"] == "captured" and (n0[1] <= end + 3 or (self.AL[n0[0]][end] and d(self.P[n0[0]][end], self.spawn[tm]) < SPAWN_R))
            back_cap = False
            if L["how"] == "captured":
                c = L["capper"]
                near = [b for b in st.players[foe] if self.AL[b][end] and self.P[c][end] and d(self.P[b][end], self.P[c][end]) < FIGHT_LINK]
                over = [b for b in self.main_team(foe, end) if self.AL[b][end] and self._deep(b, end)]
                back_cap = not near and len(over) >= 3
            split = any(c[0] in self._over(tm, u)[0] for c in ser for u in range(cl(c[1]) - cl(c[1]) % SPLIT_STEP, cl(c[2] if c[2] is not None else end) + 1, SPLIT_STEP))
            died = [m.roles[c[0]] for c in ser if c[2] is not None and any(abs(td - c[2]) <= 2 for td in st.death_times.get(c[0], []))]
            drop = None
            if L["how"] != "captured" and ser[-1][2] is not None and self.hall is not None and self.P[ser[-1][0]][cl(ser[-1][2])]:
                drop = self.place_words(*self.place_at(ser[-1][0], cl(ser[-1][2])))
            owner, since = st.stand_owner(tp)
            clock = round(BOOST_EVERY - (tp - since) % BOOST_EVERY) if owner == foe else None
            # the way it was run (R-373): the drawn flag run followed to the stand and on the walk back for it, and the own door it went out by
            trk = [self.P[c[0]][u] for c in ser for u in range(cl(c[1]), cl(c[2] if c[2] is not None else end) + 1) if self.AL[c[0]][u]]
            if self.hall is not None:                          # ... to his arrival at the stand: what he walks while he holds it there is not the route
                i = next((i for i, p in enumerate(trk) if p and d(p, self.hall.stand) <= ROUTE_ENDS), None)
                if i is not None: trk = trk[:i + 1]
            route = self._flag_route(tm, trk)
            back_route = None                                  # the walk back counts only when it began around the stand
            if left is not None and self.hall is not None and self.AL[a][left] and self.place_at(a, left)[0] in ("stand", "greater stand"):
                back_route = self._flag_route(tm, [self.P[a][u] for u in range(left, tp + 1) if self.AL[a][u]])
            door = None
            if self.hall is not None:
                for c in ser:
                    for u in range(cl(c[1]), cl(c[2] if c[2] is not None else end) + 1, SPLIT_STEP):
                        if not self.AL[c[0]][u]: continue
                        k_, sd_ = self.place_at(c[0], u)
                        if sd_ == st.side.get(tm) and k_ in ("front door", "back door"): door = k_; break
                        if k_ in ("stand", "greater stand"): break
                    if door: break
            # timing (R-377): how long it stood in hand in the flag stand area before the cap, and how close to the enemy's boost the cap landed
            held, cap_boost = 0, None
            if L["how"] == "captured" and self.hall is not None:
                u = end
                while u > tp and any(c[1] <= u <= (c[2] if c[2] is not None else end) and self.AL[c[0]][u] and self.place_at(c[0], u)[0] == "stand" for c in ser): u -= 1      # in the flag stand area itself: the walk across the greater stand area is not a hold
                held = end - u
                o2, s2 = st.stand_owner(max(L["end"] - 1, 0))
                if o2 == foe: cap_boost = round(BOOST_EVERY - (L["end"] - s2) % BOOST_EVERY)
            stayed = None                                      # he handed it off, stayed with it to the cap, then went back for the next himself
            if L["how"] == "captured" and L["start"] >= 0 and L["form"] == "hand-off to cap" and n0 and n0[0] != L["capper"] and n0[0] in [c[0] for c in ser]:
                x = n0[0]; th = max((c[2] for c in ser if c[0] == x and c[2] is not None), default=None)
                cp = self.P[L["capper"]][end]
                if th is not None and end - th >= HELP_IN_S and self.AL[x][end] and cp and d(self.P[x][end], cp) < FIGHT_LINK and n0[1] - end <= HELP_BACK_S:
                    stayed = {"role": m.roles[x], "id": x, "s": round(end - th), "went_back": round(n0[1])}
            out.append({"team": m.tag[tm], "tm": tm, "start": tp, "end": end, "how": L["how"], "form": L["form"],
                        "runner": m.roles[a], "runner_prof": m.A[a].get("p"), "carriers": [m.roles[c[0]] for c in ser], "ids": [c[0] for c in ser],
                        "set_off": left, "away_s": max(away, 0), "backup_waiting": backup, "back_cap": back_cap, "with_split": split,
                        "dropped_at": drop, "died_carrying": died, "enemy_boost_in": clock, "pregame": L["start"] < 0,
                        "capper": m.roles[L["capper"]] if L["how"] == "captured" else None, "runner_id": a, "pickup": ser[0][1],
                        "route": route["name"] if route else None, "back_route": back_route["name"] if back_route else None, "door": door,
                        "held_s": held, "cap_boost_in": cap_boost, "stayed": stayed,
                        "beat_boost": (L["how"] == "captured" and end - tp < clock) if clock is not None else None})
        self._fr = out
        return out

    # ---- reading step 2: the words of R-371, R-373 and R-375 to R-378, each its own record
    def _mk(self, ids):
        """Backline monks among these players (a smiter is not one)."""
        return sum(1 for a in ids if self.m.A[a].get("p") == "Monk" and not self.m.roles[a].startswith("Monk "))

    def _flagger(self, b, tm, t):
        """Is this player his team's flagger at second t: "carrying" its flag, or "going back" for it or "at the spawn"
        within PUSHFLAG_AHEAD_S of picking it up. None otherwise."""
        if not self.AL[b][t] or not self.P[b][t]: return None
        if self.carrying(b, t): return "carrying"
        if any(t < p <= t + PUSHFLAG_AHEAD_S for p in self.pick.get(b, ())):
            if self.spawn.get(tm) and d(self.P[b][t], self.spawn[tm]) < 2 * SPAWN_R: return "at the spawn"
            if self.on_leg(b, t, ("run",)): return "going back"
        return None

    def flag_pushes(self):
        """Pushing the flagger, its own record apart from a split and a push (R-371). One record each stretch in which
        players of one team stand on the other team's flagger (within PUSHFLAG_R of him for PUSHFLAG_S or longer,
        having hit him or landed a skill on him) while he is on his own: carrying the flag, going back for it or at his
        flag spawn about to pick it up, with fewer than PUSHFLAG_MATES team mates around him and fewer than half of his
        main team, and not himself on a split or a push. Each record: when, who pushes (and whether it is their main team), the flagger and what he was
        doing, where, who of his team came to help, and what came of it: he died, he dropped the flag, the flag was
        returned or capped, and how long he waited at his spawn before picking up with an enemy on him (R-377)."""
        if self._fpush is not None: return self._fpush
        st, m, T, S, out = self.st, self.m, self.T, SPLIT_STEP, []
        if self.hall is None: self._fpush = out; return out
        lives = self.flag_lives()
        for tm in st.teams:                                   # tm pushes; the flagger is one of the other team's players
            foe = 3 - tm
            if tm not in st.side or foe not in st.side: continue
            for b in st.players[foe]:
                runs, cur = [], None
                for t in range(0, T + 1, S):
                    state = self._flagger(b, foe, t)
                    on = []
                    if state:
                        mates = sum(1 for x in st.players[foe] if x != b and self.AL[x][t] and d(self.P[x][t], self.P[b][t]) < FIGHT_LINK)
                        sp, pu, _ = self._over(foe, t)
                        rest = sum(1 for x in self.main_team(foe, t) if x != b and self.AL[x][t])      # on his own: with fewer than PUSHFLAG_MATES team mates and fewer than half his main team
                        if mates < PUSHFLAG_MATES and mates * 2 < max(rest, 2) and ((b not in sp and b not in pu) or self._deep(b, t) == "field"):      # out in the field he is on his run, not on a split (a stand that lies on the enemy's half)
                            on = [a for a in st.players[tm] if self.AL[a][t] and d(self.P[a][t], self.P[b][t]) < PUSHFLAG_R]
                    if not on: continue
                    if cur is None or t - cur["t1"] > PUSHFLAG_GAP_S:
                        cur = {"t": t, "t1": t, "secs": collections.Counter(), "state": state, "states": set()}
                        runs.append(cur)
                    cur["t1"] = t; cur["states"].add(state)
                    for a in on: cur["secs"][a] += S
                for r in runs:
                    t0, t1 = r["t"], r["t1"]
                    # R-418: he reaches his team with them still on him (the stretch ends only because he is no longer on his own): a hit or
                    # skill that lands as he arrives counts, and the push needs only PUSHFLAG_SHORT_S on his own
                    v = min(t1 + S, T)
                    reached = self.AL[b][v] and bool(self._flagger(b, foe, v)) and any(self.AL[a][v] and d(self.P[a][v], self.P[b][v]) < PUSHFLAG_R for a in r["secs"])
                    acted = collections.Counter()
                    for u in range(t0 - 1, min(t1 + (PUSHFLAG_LATE_S if reached else 2), T) + 1):
                        for x, y in self.acts.get(u, ()):
                            if y == b and x in r["secs"]: acted[x] += 1
                    ids = sorted((a for a in r["secs"] if acted[a] or r["secs"][a] >= PUSHFLAG_S), key=lambda a: (-acted[a], -r["secs"][a]))
                    main = [a for a in self.main_team(tm, t0) if self.AL[a][t0]]
                    helped = sorted({x for x in st.players[foe] if x != b for u in range(t0, t1 + 1, S)
                                     if self.AL[x][u] and self.AL[b][u] and d(self.P[x][u], self.P[b][u]) < 1000}
                                    - {x for x in st.players[foe] if x != b and self.AL[x][t0] and d(self.P[x][t0], self.P[b][t0]) < FIGHT_LINK})
                    died = any(t0 <= td <= t1 + 4 for td in st.death_times.get(b, []))
                    L = next((x for x in lives if x["team"] == foe and x["start"] <= t1 + PUSHFLAG_AHEAD_S and (x["end"] is None or x["end"] >= t0)
                              and any(c[0] == b for c in x["carries"])), None)
                    handed = lambda c: any(c2[0] != b and 0 <= c2[1] - c[2] <= 20 for c2 in L["carries"])      # a team mate has it within 20 s: a hand-off, not a drop (as the story tells it)
                    dropped = any(c[0] == b and c[2] is not None and t0 <= c[2] <= t1 + 4 and not (L["how"] == "captured" and L.get("capper") == b and abs(L["end"] - c[2]) < 1) and not handed(c)
                                  for c in (L["carries"] if L else ()))
                    if not acted or not ids or (t1 - t0 < PUSHFLAG_S and not died and not dropped and not (reached and t1 - t0 >= PUSHFLAG_SHORT_S)): continue      # a short push still counts when he drops the flag or dies under it, or reaches his team with them on him (R-418)
                    delay, pk = None, None
                    if r["state"] != "carrying" and self.spawn.get(foe):
                        pk = next((p for p in self.pick.get(b, ()) if p > t0), None)
                        if pk is not None and pk <= t1 + PUSHFLAG_AHEAD_S:
                            prev = max((x["end"] for x in lives if x["team"] == foe and x["end"] is not None and x["end"] <= pk), default=0)
                            there = next((u for u in range(t0, min(int(pk), T) + 1) if self.AL[b][u] and d(self.P[b][u], self.spawn[foe]) < SPAWN_R), None)
                            pushed = [u for u in range(t0, min(int(pk), T) + 1, S) if self.AL[b][u] and any(self.AL[a][u] and d(self.P[a][u], self.P[b][u]) < PUSHFLAG_R for a in ids)]
                            if there is not None and pushed: delay = max(round(pk - max(there, prev, pushed[0])), 0)
                    at_spawn = bool(self.spawn.get(foe)) and d(self.P[b][t0], self.spawn[foe]) < 2 * SPAWN_R
                    out.append({"t": t0, "t1": t1, "tm": tm, "team": m.tag[tm], "foe": m.tag[foe], "flagger": b, "role": m.roles[b], "doing": r["state"],
                                "carried": "carrying" in r["states"], "ids": ids, "roles": [m.roles[a] for a in ids],
                                "main": bool(main) and sum(1 for a in ids if a in main) * 2 >= len(main) and len(ids) >= 3,
                                "place": f"{m.tag[foe]}'s flag spawn" if at_spawn else self.place_words(*self.place_at(b, t0)), "at_spawn": at_spawn,
                                "acts": sum(acted.values()), "helped": [m.roles[x] for x in helped], "died": died, "dropped": dropped and not died, "reached_team": bool(reached),
                                "flag": (L["how"] or "open") if L else None, "pickup": pk if delay is not None else None, "delay_s": delay})
        self._fpush = sorted(out, key=lambda x: x["t"])
        return self._fpush

    def _flag_route(self, tm, pts):
        """Which drawn flag run a walk followed, on a hall where Denning has drawn more than one a side: the short way
        or the long way (by walked length). Read away from the spawn and the stand, where the runs lie apart: the walk
        stayed within ROUTE_OFF of the run on average and ROUTE_CLEAR closer to it than to the next. None otherwise."""
        hall, side = self.hall, self.st.side.get(tm)
        if hall is None or side is None or not self.spawn.get(tm): return None
        rs = [r for r in hall.routes if r["type"] == "Flag run" and r["side"] == side]
        if len(rs) < 2: return None
        pts = [p for p in pts if p and d(p, self.spawn[tm]) > ROUTE_ENDS and d(p, hall.stand) > ROUTE_ENDS]
        if len(pts) < ROUTE_MIN_S: return None
        sc = sorted((statistics.fmean(min(_seg_dist(p, u, v) for u, v in zip(r["pts"], r["pts"][1:])) for p in pts), r["walked"], r["id"]) for r in rs)
        if sc[0][0] > ROUTE_OFF or sc[1][0] - sc[0][0] < ROUTE_CLEAR: return None
        ws = sorted(r["walked"] for r in rs)
        return {"name": "short way" if sc[0][1] == ws[0] else "long way" if sc[0][1] == ws[-1] else "middle way", "id": sc[0][2], "walked": sc[0][1], "off": round(sc[0][0])}

    def pregame(self):
        """The pre-game flag (R-374): for each team, who picked its flag up before the gates opened and who has it in
        hand at 0:00 (the replay keeps the flag events from before 0:00). {team: {"picked": [(second, player)],
        "holder": player or None, "dropped": second or None}}."""
        m, out = self.m, {tm: {"picked": [], "holder": None, "dropped": None} for tm in self.st.teams}
        for t, typ, a, *_ in m.o.get("flags", []):
            if t >= 0 or a not in self.P: continue
            r = out[m.team(a)]
            if typ == "flag_picked_up": r["picked"].append((t / 10, a)); r["holder"], r["dropped"] = a, None
            elif typ == "flag_dropped" and r["holder"] == a: r["holder"], r["dropped"] = None, t / 10
        return out

    def _lead_values(self):
        """{team: {second: (stand, flag, runner)}} every SPLIT_STEP: each team's flag tally in three parts (R-408).
        stand = 1 while the team holds the stand. flag = how much of a flag run (stand to spawn and back, walked) its
        next flag has behind it, 0 to 1: carried, by how far its carrier still is from the stand; lying on the
        ground, by the nearest living player's walk to it and on to the stand; at the spawn, by the walk of the
        player going back for it (0 while nobody is). runner = up to half a run more while that flag is still out and
        the player who takes the following one is already on his way back to the spawn or waiting there. A team's
        lead is its tally less the enemy's: a cap turns a flag in hand (1) into the stand (1) and takes the stand
        from the enemy, so a backup that answers an enemy cap leaves the lead where it was. None without a labelled
        hall."""
        if self._lead is not None: return self._lead
        st, hall, T, S = self.st, self.hall, self.T, SPLIT_STEP
        out = {tm: {} for tm in st.teams}
        ok = hall is not None and all(self.spawn.get(tm) for tm in st.teams)
        span = {tm: [] for tm in st.teams}                     # (from, to, carrier or None while it lies on the ground, where it lies, who takes the next flag)
        lives = self.flag_lives()
        for i, L in enumerate(lives):
            ser = [c for c in L["carries"] if c[0] in L["serious"]]
            if not ser: continue
            end = L["end"] if L["end"] is not None else T + 1
            nxt = next((y for y in lives[i + 1:] if y["team"] == L["team"] and y["serious"]), None)
            n = next((c[0] for c in nxt["carries"] if c[0] in nxt["serious"]), None) if nxt else None
            for k, c in enumerate(ser):
                e = c[2] if c[2] is not None else end
                span[L["team"]].append((c[1], e, c[0], None, n))
                after = ser[k + 1][1] if k + 1 < len(ser) else end
                if e < after: span[L["team"]].append((e, after, None, self.P[c[0]][min(max(int(e), 0), T)], n))
        self._lead_on = span
        w = lambda p, q: hall.walk(p, q) if p and q else None
        home = {tm: w(self.spawn[tm], hall.stand) for tm in st.teams} if ok else {}
        back = {tm: w(hall.stand, self.spawn[tm]) for tm in st.teams} if ok else {}
        if not ok or not all(home.values()) or not all(back.values()):
            for tm in st.teams: out[tm] = {t: None for t in range(0, T + 1, S)}
            self._lead = out; return out
        trip = {tm: back[tm] + home[tm] for tm in st.teams}
        def parts(tm, t, owner):
            x = next((x for x in span[tm] if x[0] <= t < x[1]), None)
            runner = 0.0
            if x and x[2] is not None and self.AL[x[2]][t]: go = w(self.P[x[2]][t], hall.stand)
            else:
                lies = x[3] if x else None
                if x and x[2] is not None:                     # its carrier is dead with no drop recorded yet: it lies where he fell
                    lies = next((self.P[x[2]][u] for u in range(t, max(int(x[0]) - 1, -1), -1) if self.AL[x[2]][u] and self.P[x[2]][u]), None)
                if lies:
                    ds = [v for v in (w(self.P[a][t], lies) for a in st.players[tm] if self.AL[a][t]) if v is not None]
                    go = (min(ds) + (w(lies, hall.stand) or 0)) if ds else None
                else:                                          # at the spawn: the player going back for it, if anyone is
                    ds = [v for v in (w(self.P[a][t], self.spawn[tm]) for a in st.players[tm] if self._flagger(a, tm, t) in ("going back", "at the spawn")) if v is not None]
                    go = (min(ds) + home[tm]) if ds else trip[tm]
            if x and x[4] is not None and x[4] != x[2] and self.AL[x[4]][t] and not self.carrying(x[4], t):      # the flag is out and the next runner is already going back
                v = w(self.P[x[4]][t], self.spawn[tm])
                if v is not None and v < 0.8 * back[tm]: runner = round(0.5 * (1 - v / back[tm]), 2)
            if go is None: return None
            return (1 if owner == tm else 0, round(min(max(1 - go / trip[tm], 0), 1), 2), runner)
        for t in range(0, T + 1, S):
            owner, _ = st.stand_owner(t)
            for tm in st.teams: out[tm][t] = parts(tm, t, owner)
        self._lead = out
        return out

    def lead_value(self, tm, t):
        """The team's flag lead at second t: its tally less the enemy's, in flags (R-408). None when it cannot be read."""
        v = self._lead_values(); u = min(max(int(t), 0), self.T) // SPLIT_STEP * SPLIT_STEP
        a, b = v[tm][u], v[3 - tm][u]
        return None if a is None or b is None else round(sum(a) - sum(b), 2)

    def _lead_levels(self):
        """{team: {second: 0 to 4}}: the bands of the lead Denning ruled (R-408). 0 = under LEAD_HALF (level, or
        behind); 1 = about half a flag up; 2 = a flag up (LEAD_ONE); 3 = a flag and a half (LEAD_ONE_HALF); 4 = two
        flags or more (LEAD_TWO)."""
        if self._leadl is None:
            band = lambda v: 0 if v is None or v < LEAD_HALF else 1 if v < LEAD_ONE else 2 if v < LEAD_ONE_HALF else 3 if v < LEAD_TWO else 4
            self._leadl = {tm: {t: band(self.lead_value(tm, t)) for t in range(0, self.T + 1, SPLIT_STEP)} for tm in self.st.teams}
        return self._leadl

    def flag_lead(self):
        """Flag lead (R-408), one record each stretch of LEAD_S or longer in which a team's lead stays in one band:
        about half a flag up, a flag up, a flag and a half, two flags. Each record: when, the team, the band, the
        lead at the middle of the stretch and the three parts of each team's tally then (stand, flag, runner), who
        has the team's next flag and where, and where the enemy's flag is (at the spawn, in hand, on the ground)."""
        lv, vals, S, out = self._lead_levels(), self._lead_values(), SPLIT_STEP, []
        m = self.m
        for tm in self.st.teams:
            cur = None
            for t in range(0, self.T + 1, S):
                v = lv[tm][t]
                if cur is not None and v == cur["lv"]: cur["t1"] = t; continue
                if cur is not None and cur["lv"] >= 1 and cur["t1"] - cur["t"] >= LEAD_S: out.append(cur)
                cur = {"t": t, "t1": t, "lv": v, "tm": tm}
            if cur is not None and cur["lv"] >= 1 and cur["t1"] - cur["t"] >= LEAD_S: out.append(cur)
        for r in out:
            tm = r["tm"]; t = (r["t"] + r["t1"]) // 2 // S * S
            mine = next((x for x in self._lead_on[tm] if x[0] <= t < x[1]), None)
            theirs = next((x for x in self._lead_on[3 - tm] if x[0] <= t < x[1]), None)
            a = mine[2] if mine and mine[2] is not None else None
            r.update(team=m.tag[tm], foe=m.tag[3 - tm], level=LEAD_WORDS[r["lv"]], lead=self.lead_value(tm, t), own=vals[tm][t], enemy=vals[3 - tm][t],
                     holds=bool(vals[tm][t] and vals[tm][t][0]),
                     backup=m.roles[a] if a is not None else None, backup_at=self.place_words(*self.place_at(a, t)) if a is not None and self.AL[a][t] else None,
                     own_flag="in hand" if a is not None else ("on the ground" if mine else "at the spawn"),
                     enemy_flag="at the spawn" if theirs is None else ("in hand" if theirs[2] is not None else "on the ground"))
        return sorted(out, key=lambda r: r["t"])

    def lead_at(self, tm, t):
        """The team's flag lead at second t in words (R-408): None under half a flag, else "half a flag", "a flag",
        "a flag and a half" or "two flags"."""
        return LEAD_WORDS[self._lead_levels()[tm][min(max(int(t), 0), self.T) // SPLIT_STEP * SPLIT_STEP]]

    def _between(self, a, b, t):
        """Hits between two sets of players (a of team 1, b of team 2) over the 10 s up to second t."""
        if self._hitc is None:
            self._hitc = {u: collections.Counter((x, y) if self.m.team(x) == 1 else (y, x) for x, y in xs) for u, xs in self.hits.items()}
        return sum(c for u in range(max(int(t) - 9, 0), int(t) + 1) if u in self._hitc for (x, y), c in self._hitc[u].items() if x in a and y in b)

    def standoff_at(self, ids, t, slack=0):
        """The stand-off these players stand in at second t (half of them or more), or None."""
        ids = set(ids)
        return next((r for r in self.standoffs() if r["t"] - slack <= t <= r["t1"] + slack and len(ids & (set(r["ids"][1]) | set(r["ids"][2]))) * 2 >= len(ids)), None)

    def standoffs(self):
        """The disengage (R-405), framed on Denning's classic example (R-411: OG v hdm on Isle of the Dead, 1:13 to
        2:14: a real 8 v 8 trading 1.3 to 2.5 hits a player in 10 s falls to 0.2 to 0.6, then to nothing for 42 s, the
        two main teams 1,900 to 3,400 apart, hdm at OG's front door and OG inside its base, hdm's 8 away for the flag).
        One record each stretch of STANDOFF_S or longer in which the two main teams, STANDOFF_MIN or more alive in
        each, stand within STANDOFF_R of each other (their middles; they need not be close enough to be one fight)
        and trade no more than STANDOFF_HITS hits for each of their players in any 10 s. Such a stretch is not a
        fight: the story stops calling it one. Each record: when, the numbers, where each main team stands, the
        hits traded in it and the furthest the two stood apart, whether they had been fighting just before, who of
        each team was away from its main team and whether for the flag, and how it ended."""
        if self._so is not None: return self._so
        S, T, m, st, out, cur = SPLIT_STEP, self.T, self.m, self.st, [], None
        def close(end, t):
            nonlocal cur
            if cur is not None:
                cur["end"] = end; cur["t_end"] = t
                if cur["t1"] - cur["t"] >= STANDOFF_S: out.append(cur)
            cur = None
        for t in range(0, T + 1, S):
            a = frozenset(x for x in self.main_team(1, t) if self.AL[x][t] and self.P[x][t]); b = frozenset(x for x in self.main_team(2, t) if self.AL[x][t] and self.P[x][t])
            if min(len(a), len(b)) < STANDOFF_MIN: close("a main team is no longer there", t); continue
            gap = d(self.centre(a, t), self.centre(b, t))
            if gap > STANDOFF_R: close("they part", t); continue
            h = self._between(a, b, t)
            if h > STANDOFF_HITS * (len(a) + len(b)): close("the fight resumes", t); continue
            if cur is None: cur = {"t": t, "t1": t, "first": (a, b), "seen": {1: set(), 2: set()}, "nums": collections.Counter(), "gap": 0, "places": {1: collections.Counter(), 2: collections.Counter()}, "in": collections.Counter(), "steps": 0}
            cur["t1"] = t; cur["nums"][(len(a), len(b))] += 1; cur["gap"] = max(cur["gap"], gap); cur["seen"][1] |= a; cur["seen"][2] |= b; cur["steps"] += 1
            for x in a | b: cur["in"][x] += 1
            for tm, g in ((1, a), (2, b)):
                z = collections.Counter(self.place_at(x, t) for x in g) if self.hall is not None else None
                if z: cur["places"][tm][max(z, key=lambda k: (z[k], str(k)))] += 1
        close("the match ends", T)
        keep = []
        for r in out:
            t0, t1 = r["t"], r["t1"]; a, b = r["first"]
            hits = sum(c for u in range(t0, t1 + 1) if self._hitc and u in self._hitc for (x, y), c in self._hitc[u].items() if x in r["seen"][1] and y in r["seen"][2])
            n = max(r["nums"], key=r["nums"].get)
            away = {tm: [(m.roles[x], "for the flag" if any(self._flagger(x, tm, u) for u in range(t0, t1 + 1, 6)) else "elsewhere")
                         for x in st.players[tm] if r["in"][x] * 2 < r["steps"] and sum(1 for u in range(t0, t1 + 1, 6) if self.AL[x][u]) * 2 >= len(range(t0, t1 + 1, 6))] for tm in (1, 2)}      # alive, and with his main team for under half of it
            place = {tm: self.place_words(*max(r["places"][tm], key=r["places"][tm].get)) if r["places"][tm] else None for tm in (1, 2)}
            keep.append({"t": t0, "t1": t1, "n": n, "ids": {tm: sorted(r["seen"][tm]) for tm in (1, 2)}, "teams": (m.tag[1], m.tag[2]), "places": place,
                         "kind": "main", "who": {tm: [m.roles[x] for x in sorted(r["seen"][tm])] for tm in (1, 2)},
                         "place": place[1] if place[1] == place[2] else f"{place[2]} and {place[1]}", "hits": hits, "rate": round(hits * 10 / max((t1 - t0 + 1) * sum(n), 1), 2),
                         "apart": round(r["gap"]), "fought": self.contact(a, b, t0 - 30, t0 - 1), "away": away, "end": r["end"],
                         "resume": (r["t_end"],) + tuple(len([x for x in self.main_team(tm, r["t_end"]) if self.AL[x][r["t_end"]]]) for tm in (1, 2)) if r["end"] == "the fight resumes" else None})
        keep += self._split_standoffs()
        self._so = sorted(keep, key=lambda r: r["t"])
        return self._so

    def _split_standoffs(self):
        """A stand-off on a split (R-415): two groups, at least one of them not its team's main team, STANDOFF_SPLIT_MIN
        or more in each, standing STANDOFF_NEAR to STANDOFF_R apart (their middles), each staying within
        STANDOFF_STILL of where it stood when the stand-off began, and neither trading more than STANDOFF_HITS hits a
        player in any 10 s with the other nor hitting NPCs, for STANDOFF_SPLIT_S or longer. A split on its way
        somewhere (a collapse through mid takes no damage either) is not one: it is not standing still. Once begun it
        is followed on its own players, so a group that stands with its main team for a moment is still the group.
        Records as standoffs(). Framed on NwAy v SKT (13:20 and 14:50: two groups of three, 2,200 to 3,000 apart,
        still to within 400 to 800, one hit or none, for 26 to 35 s)."""
        S, T, m, st, out, live = SPLIT_STEP, self.T, self.m, self.st, [], []
        npc = collections.defaultdict(collections.Counter)
        for a, xs in self.npc_hits.items():
            for x in xs: npc[int(x)][a] += 1
        def groups(tm, t):
            ids = [x for x in st.players[tm] if self.AL[x][t] and self.P[x][t]]; gs = []
            for a in ids:
                hit = [g for g in gs if any(d(self.P[a][t], self.P[b][t]) < FIGHT_LINK for b in g)]
                gs = [g for g in gs if g not in hit] + [[a] + [x for g in hit for x in g]]
            main = [x for x in self.main_team(tm, t) if self.AL[x][t]]
            return [(frozenset(g), bool(main) and sum(1 for x in g if x in main) * 2 >= len(main)) for g in gs if len(g) >= STANDOFF_SPLIT_MIN]
        def read(A, B, t):                                      # (the two middles, how far apart, quiet) for these players, the living ones
            A = frozenset(x for x in A if self.AL[x][t] and self.P[x][t]); B = frozenset(x for x in B if self.AL[x][t] and self.P[x][t])
            if min(len(A), len(B)) < STANDOFF_SPLIT_MIN: return None
            ca, cb = self.centre(A, t), self.centre(B, t)
            if any(d(self.P[x][t], ca) > FIGHT_LINK for x in A) or any(d(self.P[x][t], cb) > FIGHT_LINK for x in B): return None      # the group has broken up
            quiet = self._between(A, B, t) + sum(npc[u][x] for u in range(max(t - 9, 0), t + 1) if u in npc for x in A | B) <= STANDOFF_HITS * (len(A) + len(B))
            return A, B, ca, cb, d(ca, cb), quiet
        for t in range(0, T + 1, S):
            for r in list(live):                               # a stand-off already begun: followed on its own players
                v = read(r["first"][0], r["first"][1], t)
                end = "a group breaks up" if v is None else "they fight" if not v[5] else "a group moves off" if d(v[2], r["c0"][0]) > STANDOFF_STILL or d(v[3], r["c0"][1]) > STANDOFF_STILL \
                    else "they close or part" if not (STANDOFF_NEAR <= v[4] <= STANDOFF_R) else None
                if end: r["end"] = end; live.remove(r); out.append(r); continue
                r["t1"] = t; r["nums"][(len(v[0]), len(v[1]))] += 1; r["gap"] = max(r["gap"], v[4])
                for tm, g in ((1, v[0]), (2, v[1])):
                    z = collections.Counter(self.place_at(x, t) for x in g)
                    r["places"][tm][max(z, key=lambda k: (z[k], str(k)))] += 1
            busy = set().union(*(r["first"][0] | r["first"][1] for r in live)) if live else set()
            for A, mainA in groups(1, t):
                for B, mainB in groups(2, t):
                    if (mainA and mainB) or (A | B) & busy: continue      # the two main teams are standoffs() itself
                    v = read(A, B, t)
                    if v is None or not v[5] or not (STANDOFF_NEAR <= v[4] <= STANDOFF_R): continue
                    r = {"t": t, "t1": t, "c0": (v[2], v[3]), "first": (A, B), "seen": {1: set(A), 2: set(B)}, "nums": collections.Counter({(len(A), len(B)): 1}), "gap": v[4],
                         "places": {1: collections.Counter(), 2: collections.Counter()}, "end": None}
                    for tm, g in ((1, A), (2, B)):
                        z = collections.Counter(self.place_at(x, t) for x in g)
                        r["places"][tm][max(z, key=lambda k: (z[k], str(k)))] += 1
                    live.append(r); busy |= A | B
        for r in live: r["end"] = "the match ends"; out.append(r)
        keep = []
        for r in out:
            t0, t1 = r["t"], r["t1"]
            if t1 - t0 < STANDOFF_SPLIT_S: continue
            A, B = r["first"]; n = max(r["nums"], key=r["nums"].get)
            hits = sum(c for u in range(t0, t1 + 1) if self._hitc and u in self._hitc for (x, y), c in self._hitc[u].items() if x in r["seen"][1] and y in r["seen"][2])
            place = {tm: self.place_words(*max(r["places"][tm], key=r["places"][tm].get)) for tm in (1, 2)}
            keep.append({"t": t0, "t1": t1, "n": n, "ids": {tm: sorted(r["seen"][tm]) for tm in (1, 2)}, "teams": (m.tag[1], m.tag[2]), "places": place, "kind": "split",
                         "who": {tm: [m.roles[x] for x in sorted(r["first"][tm - 1])] for tm in (1, 2)},
                         "place": place[1] if place[1] == place[2] else f"{place[2]} and {place[1]}", "hits": hits, "rate": round(hits * 10 / max((t1 - t0 + 1) * sum(n), 1), 2),
                         "apart": round(r["gap"]), "fought": self.contact(A, B, t0 - 30, t0 - 1), "away": {1: [], 2: []}, "end": r["end"], "resume": None})
        return keep

    def monk_counts(self):
        """Monk counts in a fight (R-378: "solo monk", "on two monks"), one record each time the number of backline
        monks a team has in its main team's fight changes and stays changed for MONK_S. Each record: when, the team,
        how many monks now and before (in a fight with MONK_MIN or more of the team in it), of how many on the team, where, the numbers in the fight, and what became of
        each monk who is no longer in it (dead, or where he stands) or who came into it."""
        if self._mc is not None: return self._mc
        st, m, T, S, out = self.st, self.m, self.T, SPLIT_STEP, []
        idx = self._fight_index()
        for tm in st.teams:
            total = self._mk(st.players[tm])
            told, pend = None, None                          # told = (count, monks in it); pend = [count, since, monks, fight]
            for t in range(0, T + 1, S):
                main = [a for a in self.main_team(tm, t) if self.AL[a][t]]
                fs = collections.Counter(id(idx[t][a]) for a in main if a in idx[t])
                f = next((idx[t][a] for a in main if a in idx[t] and id(idx[t][a]) == fs.most_common(1)[0][0]), None) if fs else None
                if f is None or fs.most_common(1)[0][1] * 2 < len(main) or f["n"][tm] < MONK_MIN: pend = None; continue
                mk = frozenset(a for a in f["ids"][tm] if self.m.A[a].get("p") == "Monk" and not m.roles[a].startswith("Monk "))
                n = len(mk)
                if pend is None or pend[0] != n: pend = [n, t, mk, f]
                if t - pend[1] < MONK_S or (told is not None and told[0] == n): continue
                was = told
                told = (n, pend[2])
                if was is None and n >= total: continue      # the fight opens on all its monks: nothing to tell
                t0 = pend[1]
                gone = sorted((was[1] if was else frozenset(a for a in st.players[tm] if self.m.A[a].get("p") == "Monk" and not m.roles[a].startswith("Monk "))) - pend[2])
                came = sorted(pend[2] - was[1]) if was else []
                why = [(m.roles[a], "dead" if not self.AL[a][t0] else ("with the flag" if self._flagger(a, tm, t0) else "at " + self.place_words(*self.place_at(a, t0)))) for a in gone]
                out.append({"t": t0, "tm": tm, "team": m.tag[tm], "n": n, "was": was[0] if was else None, "of": total, "place": pend[3]["place"],
                            "fight": (pend[3]["n"][1], pend[3]["n"][2]), "gone": why, "came": [m.roles[a] for a in came]})
        self._mc = sorted(out, key=lambda x: x["t"])
        return self._mc

    def on_lord(self):
        """Who is on the Guild Lord (R-378), one record each stretch in which a team damages the enemy's Guild Lord, a
        stretch ending after LORD_GAP_S without any. Each record: when, the team, whose Lord, the players on him, the
        hits and the damage as recorded, and how many of the Lord's team stood in their pit when it began."""
        out = []
        for tm_l, xs in self.lord_hits.items():
            cur = None
            for t, a, n in sorted(xs):
                if cur is not None and t - cur["t1"] <= LORD_GAP_S: cur["t1"] = t
                else:
                    u = min(max(int(t), 0), self.T)
                    cur = {"t": t, "t1": t, "tm": 3 - tm_l, "team": self.m.tag[3 - tm_l], "foe": self.m.tag[tm_l], "ids": set(), "hits": 0, "dmg": 0,
                           "defenders": sum(1 for b in self.st.players[tm_l] if self.AL[b][u] and self.hall is not None and self.place_at(b, u) == ("pit", self.st.side.get(tm_l)))}
                    out.append(cur)
                cur["ids"].add(a); cur["hits"] += 1; cur["dmg"] += n or 0
        for r in out: r["ids"] = sorted(r["ids"]); r["roles"] = [self.m.roles[a] for a in r["ids"]]; r["dmg"] = round(r["dmg"])
        return sorted(out, key=lambda r: r["t"])

    def timing(self):
        """The timing choices the record keeps (R-377, R-400), one record each:
          delayed pickup     the flagger stood at his spawn PICKUP_DELAY_S or longer with an enemy on him before picking up;
          held to the boost  a flag stood in hand at the stand HOLD_S or longer and was capped BOOST_LATE_S or less
                             before the enemy's boost;
          stayed to help     a player handed the flag off, was still with it HELP_IN_S or more later at the cap, and
                             then went back for the next flag himself;
          left before res    a split or a main team push left the enemy's base LEAVE_RES_S or less before the base res
                             that brought the defenders' dead back;
          held back          (the fifth, R-400, R-407) clear, deliberate play: a flag kept in hand around the stand
                             (the stand or the greater stand area) while the enemy holds the stand, HOLD_BACK_S or
                             longer without capping;
          left at the spawn  (the fifth again) a flag not run yet while the enemy holds the stand (R-409): back at
                             the spawn after a cap or a return and picked up LEFT_AT_SPAWN_S or more later than its
                             next runner needed to walk back for it from where he stood (at RUN_SPEED), nobody on him.
        Each record: the second the choice shows, the team, the kind, who, and the seconds that measure it."""
        if self._tim is not None: return self._tim
        st, m, T, out = self.st, self.m, self.T, []
        for p in self.flag_pushes():
            if p["delay_s"] is not None and p["delay_s"] >= PICKUP_DELAY_S:
                out.append({"t": p["pickup"], "tm": 3 - p["tm"], "team": p["foe"], "kind": "delayed pickup", "who": [p["role"]], "s": p["delay_s"], "by": p["roles"], "foe": p["team"]})
        for fr in self.flags_record():
            tag, foe = fr["team"], m.tag[3 - fr["tm"]]
            if fr["how"] == "captured" and fr["held_s"] >= HOLD_S and fr["cap_boost_in"] is not None and fr["cap_boost_in"] <= BOOST_LATE_S:
                out.append({"t": fr["end"], "tm": fr["tm"], "team": tag, "kind": "held to the boost", "who": [fr["capper"]], "s": fr["held_s"], "boost_in": fr["cap_boost_in"], "foe": foe})
            if fr.get("stayed"):
                out.append({"t": fr["end"], "tm": fr["tm"], "team": tag, "kind": "stayed to help", "who": [fr["stayed"]["role"]], "s": fr["stayed"]["s"], "went_back": fr["stayed"]["went_back"], "foe": foe})
        inb = ("pit", "base", "front door", "back door", "front footies", "back footies")
        for x in self.attempts():
            if x.get("solo") == "other" or x["end"] in ("killed", "match ended"): continue
            tm = x["tm"]; foe = 3 - tm
            for B in range((int(x["t_in"]) // RES_EVERY + 1) * RES_EVERY, min(int(x["t1"]) + LEAVE_RES_S, T) + 1, RES_EVERY):      # every base res the attempt ran up to: it may go back in afterwards
                last = max((u for a in x["ids"] for u in range(max(B - LEAVE_RES_S, int(x["t_in"])), min(B, int(x["t1"])) + 1) if u % SPLIT_STEP == 0 and self.AL[a][u] and self._deep(a, u) in inb), default=None)
                if last is None or last >= B: continue
                res = [b for b in st.players[foe] if not self.AL[b][max(B - 6, 0)] and any(self.AL[b][u] for u in range(B - 3, min(B + 4, T) + 1))]
                alive = [a for a in x["ids"] if self.AL[a][min(B, T)]]
                if not res or len(alive) * 2 < len(x["ids"]) or any(self._deep(a, min(B + 2, T)) in inb for a in alive): continue
                out.append({"t": last, "tm": tm, "team": x["team"], "kind": "left before res", "who": [y["role"] for y in x["members"] if y["from"] <= last <= y["to"] + SPLIT_STEP], "s": B - last, "coming_back": len(res), "what": x["kind"], "foe": m.tag[foe]})      # who was in it then, not everyone the attempt ever had (Denning, NwAy v SKT 23:50: three, not four)
        if self.hall is not None:                            # held back (R-400, R-407): in hand around the stand while the enemy holds it, HOLD_BACK_S without capping
            for L in self.flag_lives():
                tm = L["team"]; end = min(int(L["end"] if L["end"] is not None else T), T)
                ser = [c for c in L["carries"] if c[0] in L["serious"]]
                if not ser: continue
                s0, who = None, None
                def close(u):
                    if s0 is not None and u - s0 >= HOLD_BACK_S:
                        out.append({"t": s0, "tm": tm, "team": m.tag[tm], "kind": "held back", "who": [m.roles[who]], "s": u - s0, "place": self.place_words(*self.place_at(who, s0)),
                                    "capped": L["how"] == "captured" and abs(L["end"] - u) <= 2, "foe": m.tag[3 - tm]})
                for u in range(max(int(ser[0][1]), 0), end + 1):
                    a = next((c[0] for c in ser if c[1] <= u <= (c[2] if c[2] is not None else end)), None)
                    held = a is not None and self.AL[a][u] and self.P[a][u] and st.stand_owner(u)[0] == 3 - tm and self.place_at(a, u)[0] in ("stand", "greater stand")
                    if held and s0 is None: s0, who = u, a
                    elif not held: close(u); s0 = None
                close(end)
        delayed = {round(r["t"]) for r in out if r["kind"] == "delayed pickup"}
        prev_end = {}
        for fr in self.flags_record():                        # left at the spawn (R-400): ready there, and picked up later than the walk back for it needed
            tm, a, p = fr["tm"], fr["runner_id"], fr["pickup"]
            avail = prev_end.get(tm); prev_end[tm] = fr["end"] if fr["how"] in ("captured", "returned") else None
            if avail is None or self.hall is None or p <= avail or round(p) in delayed: continue
            u = min(int(avail), T)
            walk = self.hall.walk(self.P[a][u], self.spawn[tm]) if self.AL[a][u] and self.P[a][u] else None
            idle = round(p - avail - (walk / RUN_SPEED if walk is not None else 0))
            ready = min(int(avail + (walk / RUN_SPEED if walk is not None else 0)), T)
            if walk is not None and idle >= LEFT_AT_SPAWN_S and st.stand_owner(ready)[0] == 3 - tm and st.stand_owner(min(int(p), T))[0] == 3 - tm:      # only while the enemy holds the stand (R-409)
                out.append({"t": avail, "tm": tm, "team": m.tag[tm], "kind": "left at the spawn", "who": [fr["runner"]], "s": idle, "pickup": p, "foe": m.tag[3 - tm]})
        boost = [r["t"] for r in out if r["kind"] == "held to the boost"]      # a hold that ends in a cap just before the boost is told once, as that
        out = [r for r in out if not (r["kind"] == "held back" and r["capped"] and any(abs(r["t"] + r["s"] - b) <= 3 for b in boost))]
        self._tim = sorted(out, key=lambda r: r["t"])
        return self._tim

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

    # ---- 2.4 to 2.7, rebuilt on the records (R-351, R-362: the record is the work; Denning's golden game 1 note: when people go to run, not only when they pick up)
    def run_starts(self):
        """When each fresh flag's runner set off for his spawn, and since when he waited there. One record a fresh
        pickup at the spawn: the runner, his team, the pickup, when he set off (walked more than 1,500 to get there; None
        if he was already near it) and since when he waited there (10 s or more; else None). The story's "leaves ... to
        go back for the flag" and "waits back at the flag spawn" lines print from this record."""
        if getattr(self, "_rs", None) is not None: return self._rs
        out = []
        for L in self.flag_lives():
            tm = L["team"]                                  # the life's first pickup at the spawn, serious or a short carry handed on (golden game 1, 6:51: hook's Monk 4 to the 8 Monk)
            at_sp = [c for c in L["carries"] if d(self.P[c[0]][min(max(int(c[1]), 0), self.T)], self.spawn[tm]) < SPAWN_R or c[1] < 2]      # a flag picked up before the gates counts (golden hold v Apes: the WoC holds it from the start)
            c = next((c for c in at_sp if c[0] in L["serious"]), at_sp[0] if at_sp else None)          # the first serious carrier to pick it up there; a brief pickup (R-339) only if nobody serious did
            if not c or not L["serious"]: continue
            a, tp = c[0], min(max(int(c[1]), 0), self.T)
            dist = lambda u: self.hall.to(self.spawn[tm]).get(self.hall.snap(self.P[a][u]), 1e9) if self.AL[a][u] else None
            u = tp
            while u >= 2 and dist(u - 2) is not None and dist(u - 2) < SPAWN_R: u -= 2
            waited = u
            while u >= 4 and dist(u - 4) is not None and dist(u) is not None and dist(u - 4) > dist(u) + 40: u -= 2
            runner = L["capper"] if L.get("capper") in L["serious"] else L["serious"][-1]     # who ran it in: the capper, else the last serious carrier (a brief pickup handed on is not a runner: golden hdm v One 17:24)
            own, out_t = self.st.side.get(tm), None          # when the flag is under way: the runner first stands off his own base with it (Denning's golden game 1: "hook's 8 Monk leaves the base at 7:05")
            for c2 in [c2 for c2 in L["carries"] if c2[0] == runner]:
                for v in range(max(int(c2[1]), 0), min(int(c2[2] if c2[2] is not None else self.T), self.T) + 1, 2):
                    k_, s_ = self.place_at(c2[0], v)
                    if not (s_ == own and k_ in ("pit", "base")): out_t = v; break           # out of his base and pit: on his way out by a door
                if out_t is not None: break
            pre = c[1] < 2                                   # before the gates nobody set off or waited
            set_off = u if not pre and dist(u) is not None and dist(u) - SPAWN_R > 1500 else None
            # when he goes to run (R-461): setting off from inside the greater stand area, it is when he leaves that area, or the flag stand area itself, by the hall; anywhere else, when he sets off
            moment, rule = set_off, "sets off"
            if set_off is not None and self.place_at(a, set_off)[0] in ("stand", "greater stand"):
                name = self.hall.name
                inside = ("stand", "greater stand") if name in FLAG_MOMENT_GREATER else ("stand",) if name in FLAG_MOMENT_STAND else None
                if inside is None: rule = "sets off (hall not ruled)"
                elif self.place_at(a, set_off)[0] in inside:
                    moment = next((v for v in range(set_off, tp + 1, 2) if self.place_at(a, v)[0] not in inside), tp)
                    rule = "leaves the greater stand area" if len(inside) == 2 else "leaves the stand area"
            out.append({"a": a, "runner": runner, "serious": list(L["serious"]), "carries": [tuple(c2[:3]) for c2 in L["carries"]], "tm": tm, "pickup": tp, "set_off": set_off, "moment": moment, "moment_rule": rule,
                        "waited": waited if not pre and tp - waited >= 10 else None, "under_way": out_t})
        self._rs = out
        return out

    def _went_to_run(self, r): return min(x for x in (r["moment"], r["waited"], r["pickup"]) if x is not None)      # the decision moment of a flag run (R-461); the story's "leaves to go back" line stays at set_off

    def triggers(self):
        """One record a moment (2.4), each read from a record:
          family 1 (the flag)   the enemy's runner sets off for his flag (run_starts: when he goes to run, not only when he
                                picks up), the enemy's boost BOOST_WARN_S away, an own fresh pickup at the spawn;
          family 2 (a split)    an enemy split attempt sets out, or grows by a player (attempts);
          family 3 (numbers)    a numbers difference in the fight a main team stands in, wherever it is (R-351), held
                                NUMBERS_MIN_S or longer; read from both sides (R-301)."""
        st, m, out = self.st, self.m, []
        rs = self.run_starts()
        for tm in st.teams:
            foe, f1 = 3 - tm, []
            for r in rs:
                if r["tm"] == foe:                         # when he goes to run, and again when the flag is under way (golden game 1: hook's flag leaves its base at 7:05, after he went back at 6:05)
                    f1.append((self._went_to_run(r), "enemy_run", r))
                    if r["under_way"] is not None and r["under_way"] - self._went_to_run(r) > MERGE_S: f1.append((r["under_way"], "enemy_run", r))
                elif r["tm"] == tm:
                    f1.append((self._went_to_run(r), "own_flag", r))
                    if r["under_way"] is not None and r["under_way"] - r["pickup"] > MERGE_S: f1.append((r["under_way"], "own_flag", r))     # only a flag held a while before it is taken out     # a flag held, then taken out (golden hold v Apes 1:37: the WoC runs it out of the back door)      # the decision is going to run, not the pickup (golden ohno v xxx: "the decision to run was actually at around 11:42", the pickup at 12:02)
            caps = st.caps + [(st.end, None)]
            for (c, h), (c2, _) in zip(caps, caps[1:]):
                k = 1
                while h == foe and c + BOOST_EVERY * k - BOOST_WARN_S < c2:
                    f1.append((int(c + BOOST_EVERY * k - BOOST_WARN_S), "boost", None)); k += 1
            cur = None
            for t, kind, ref in sorted(f1, key=lambda x: x[0]):
                if cur and t - cur["t"] <= MERGE_S: cur["triggers"].append(kind); cur["refs"].append(ref)
                else:
                    cur = {"family": 1, "tm": tm, "t": t, "triggers": [kind], "refs": [ref]}; out.append(cur)
            for x in self.attempts():
                if x["tm"] != foe or x["kind"] != "split" or x.get("solo") == "other": continue
                out.append({"family": 2, "tm": tm, "t": x["t_in"], "triggers": ["split"], "refs": [x]})      # the moment is the crossing to the enemy's side, not the leave (R-458)
                for q in x["members"]:                      # a player joining the split later is a moment of its own
                    if q["from"] > x["t_in"] + JOIN_S and q["from"] < x["t1"]:
                        out.append({"family": 2, "tm": tm, "t": q["from"], "triggers": ["split grows"], "refs": [x]})
                for t_, kind_ in self._split_shifts(x, tm):     # R-421: a split that changes door, or divides, is a new moment
                    out.append({"family": 2, "tm": tm, "t": t_, "triggers": [kind_], "refs": [x]})
            for r in self.standoffs():                      # two split groups standing off (R-415): a threat the defenders answer (R-421: NwAy v SKT 14:50)
                if r["kind"] == "split": out.append({"family": 2, "tm": tm, "t": r["t"], "triggers": ["split stand-off"], "refs": [r]})
        for e in self._numbers():
            for tm in st.teams:
                out.append({"family": 3, "tm": tm, "t": e["start"], "triggers": ["up" if tm == e["adv"] else "down"], "refs": [e]})
        seen, keep = set(), []
        for x in sorted(out, key=lambda x: (x["t"], x["family"], x["tm"])):
            if x["family"] == 2:                            # one moment for one split at one second
                k = (x["tm"], x["t"], x["refs"][0].get("t0", -1))
                if k in seen: continue
                seen.add(k)
            if 0 < x["t"] < self.T - READ_TO: keep.append(x)
        return keep

    def _split_shifts(self, x, tm):
        """The seconds a split on tm's ground changes door (most of it now at the other door, JOIN_S or longer) or
        divides (players at both doors, JOIN_S or longer, after being at one), each with its kind (R-421)."""
        own, out = self.st.side.get(tm), []
        def door(k, sd):                                 # which part of the map a split player is in: one of the defenders' doors, or out of their base (a player leaving the split through mid, golden Men v hdm 9:36); in their base or pit he is with the split
            if sd == own and k in ("front door", "front footies"): return "front"
            if sd == own and k in ("back door", "back footies"): return "back"
            if sd == own and k in ("base", "pit"): return None
            return "out"
        cur, both, pend = None, False, None
        for t in range(x["t0"] - x["t0"] % SPLIT_STEP, min(x["t1"], self.T) + 1, SPLIT_STEP):
            ds = collections.Counter()
            for a, q in zip(x["ids"], x["members"]):
                if q["from"] <= t <= q["to"] and self.AL[a][t]:
                    k, sd = self.place_at(a, t)
                    if door(k, sd): ds[door(k, sd)] += 1
            if ds and set(ds) == {"out"}: continue                  # all out of their base: the split is between visits, not moving
            now = ("both" if len(ds) >= 2 else next(iter(ds))) if ds else None
            if now is None: continue
            if cur is None: cur = now if now != "both" else None; continue
            if now != cur and (pend is None or pend[1] != now): pend = (t, now)
            elif now == cur: pend = None
            if pend and t - pend[0] >= JOIN_S:
                out.append((pend[0], "split divides" if pend[1] == "both" else "split changes door"))
                cur, pend = pend[1], None
        return out

    def _numbers(self):
        """Numbers differences in the fight a main team stands in (R-351: every fight, not only where the mains meet):
        each a stretch of NUMBERS_MIN_S or more with the same side up, read every 2 s from the fight records."""
        S, eps, cur, F = SPLIT_STEP, [], None, {}
        times = list(range(0, self.T + 1, S))
        for t in times:
            f = None
            for tm in self.st.teams:
                mt = [a for a in self.main_team(tm, t) if self.AL[a][t]]
                if not mt: continue
                fs = [g for g in self.fights(t) if g["n"][1] and g["n"][2] and len(g["ids"][tm] & set(mt)) * 2 >= len(mt)]
                if fs: f = max(fs, key=lambda g: g["n"][1] + g["n"][2]); break
            F[t] = f
        # a player counts in the fight's numbers only if he stays JOIN_S, and then from when he arrived; one who goes sooner was never a player more
        # (R-350, R-459: Crew v hdm 7:22, six seconds of 8 v 7). One missed reading allowed; a death in it counts at once; so does the end of the match.
        counted = {}
        for a in self.m.PL:
            tm_a = self.m.team(a)
            reach = [F[t] is not None and a in F[t]["ids"][tm_a] for t in times]
            counted[a] = self.visits(times, reach, [r and self.engaged_in(a, F[t]["ids"][1] | F[t]["ids"][2], t) for r, t in zip(reach, times)], self.st.death_times.get(a, []))
        for ti, t in enumerate(times):
            f = F[t]
            n = {tm: sum(1 for a in f["ids"][tm] if counted[a][ti]) for tm in self.st.teams} if f is not None else None
            adv = None if n is None or not n[1] or not n[2] or n[1] == n[2] else (1 if n[1] > n[2] else 2)
            if adv and cur and cur["adv"] == adv and t - cur["last"] <= S: cur["last"] = t; cur["ns"].append((n[1], n[2]))
            else:
                if cur and cur["last"] - cur["start"] >= NUMBERS_MIN_S: eps.append(cur)
                cur = {"adv": adv, "start": t, "last": t, "ns": [(n[1], n[2])], "place": (f["kind"], f["side"]), "ids": {tm: frozenset(a for a in f["ids"][tm] if counted[a][ti]) for tm in self.st.teams}} if adv else None      # ids: the players counted in it
        if cur and cur["last"] - cur["start"] >= NUMBERS_MIN_S: eps.append(cur)
        return eps

    # ---- 2.5 scenario
    def _state(self, tm, t):
        """The continuous state that rides along with a scenario (for similar cases, 2.10)."""
        st, foe = self.st, 3 - tm
        owner, since = st.stand_owner(t)
        s = {"stand": "own" if owner == tm else "enemy" if owner == foe else "nobody",
             "boost_in": round(BOOST_EVERY - (t - since) % BOOST_EVERY) if owner else None,
             "alive": [sum(self.AL[a][t] for a in st.players[k]) for k in (tm, foe)],
             "main": [len([a for a in self.main_team(k, t) if self.AL[a][t]]) for k in (tm, foe)],
             "own_flag": any(self.carrying(a, t) for a in st.players[tm]),
             "enemy_flag": any(self.carrying(a, t) for a in st.players[foe]),
             "res_in": round(st.next_res(t) - t), "footmen": self.footmen_alive(tm, t),
             "enemy_boost": self.boost_worth(foe, t), "own_boost": self.boost_worth(tm, t)}
        s["flag_lead"] = self.lead_value(tm, t)          # in flags, the tally of R-408 (None on a hall whose walks cannot be read)
        s["lead_band"] = self.lead_at(tm, t)             # his bands: None under half a flag, "half a flag", "a flag" ...
        return s

    def _ladder(self, tm, kind, side):
        """A place as a step on a team's ladder (R-341's places): own pit 4 ... the stand 0 ... enemy pit -4."""
        own = self.st.side.get(tm)
        k = {"pit": 4, "base": 3, "front door": 2, "back door": 2, "front footies": 1, "back footies": 1}.get(kind, 0)
        return k if side == own else -k

    def scenario(self, x, s):
        fam, tm, t, foe = x["family"], x["tm"], x["t"], 3 - x["tm"]
        stand = {"own": "own team holds the stand", "enemy": "the enemy holds the stand", "nobody": "nobody holds the stand"}[s["stand"]]
        if fam == 1:
            kind = next(k for k in ("enemy_run", "boost", "own_flag") if k in x["triggers"])
            return {"key": f"{kind}|{s['stand']}", "label": f"{TRIGGER_WORDS[kind].capitalize()}; {stand}",
                    "parts": {"trigger": kind, "stand": s["stand"], "lead": s.get("flag_lead")}}
        if fam == 2 and "split stand-off" in x["triggers"]:
            r = x["refs"][0]; n = len(r["who"][foe])
            return {"key": f"{min(n, 4)}|home", "label": f"An enemy group of {n} stands off with {len(r['who'][tm])} of ours ({r['place']})",
                    "parts": {"size": n, "home": len(r["who"][tm]), "split_has_monk": any("Monk" in w for w in r["who"][foe]), "split": r["who"][foe], "way": None, "grows": False}}
        if fam == 2:
            g = x["refs"][0]
            ids = [a for a, q in zip(g["ids"], g["members"]) if q["from"] <= t + SPLIT_STEP]
            n = len(ids) or 1
            home = [a for a in self.st.players[tm] if self.AL[a][t] and self.place_at(a, t)[1] == self.st.side.get(tm) and self.place_at(a, t)[0] in ("pit", "base", "front door", "back door", "front footies", "back footies")]
            size = {1: "a solo split", 2: "a two-player split", 3: "a three-player split"}.get(n, "a split of four or more")
            healer = any(self.m.A[a].get("p") == "Monk" for a in ids)
            hk = "home" if home else "empty"
            grow = "split grows" in x["triggers"]
            head = {"split grows": f"The enemy split grows to {n}", "split changes door": f"The enemy split ({n}) changes door", "split divides": f"The enemy split ({n}) divides between the doors"}.get(x["triggers"][0], f"{size.capitalize()} sets out")
            return {"key": f"{min(n, 4)}|{hk}",
                    "label": head + "; " + ({"home": f"{len(home)} at home", "empty": "nobody is home"}[hk]),
                    "parts": {"size": n, "home": len(home), "split_has_monk": healer, "split": [self.m.roles[a] for a in ids], "way": g.get("way"), "grows": grow}}
        e, side = x["refs"][0], x["triggers"][0]
        short = tm if side == "down" else foe
        why = collections.Counter()
        fight_ids = e["ids"][short]
        for a in self.st.players[short]:
            if a in fight_ids: continue
            if not self.AL[a][t]: why["kills"] += 1
            elif self.carrying(a, t) or any(r["a"] == a and self._went_to_run(r) - 5 <= t <= r["pickup"] + 60 for r in self.run_starts()) or d(self.P[a][t], self.spawn[short]) < SPAWN_R: why["runner away"] += 1
            else: why["split elsewhere"] += 1
        src = "wipe" if len(fight_ids) <= 2 and why["kills"] >= 5 else max(("kills", "runner away", "split elsewhere"), key=lambda k: (why[k], k == "kills", k == "runner away"))
        runs = []                                        # the numbers it starts with (the first held two readings or more), and each change after that (R-446: numbers that change are told)
        for i_, c in enumerate(e["ns"]):
            if runs and runs[-1][0] == c: runs[-1][2] += 1
            else: runs.append([c, e["start"] + i_ * SPLIT_STEP, 1])
        held = [r for r in runs if r[2] >= 2] or runs
        own = lambda c: c if tm == 1 else c[::-1]
        n = own(held[0][0])
        then = "".join(f"; then {own(c)[0]} v {own(c)[1]} from {int(u) // 60}:{int(u) % 60:02d}" for c, u, k_ in held[1:4] if k_ >= 3)
        words = {"kills": "kills", "runner away": "a runner away", "split elsewhere": "players split elsewhere", "wipe": "a wipe"}[src]
        return {"key": f"{side}|{src}", "label": f"{'Up' if side == 'up' else 'Down'} on numbers in the main fight ({n[0]} v {n[1]}, {self.place_words(*e['place'])}{then}), from {words}",
                "parts": {"side": side, "source": src, "numbers": f"{n[0]}v{n[1]}", "short_because": dict(why), "place": self.place_words(*e["place"]), "step": self._ladder(tm, *e["place"])}}

    # ---- 2.6 the call, read from the records in the window after the trigger (never from damage or deaths)
    def _runners(self, tm, t):
        """Own players who go to run in the window: they set off for the spawn, wait there or pick up from t - 10 to
        t + READ_TO, or carry the flag at READ_FROM to READ_TO (a hand-off counts the player who takes it on)."""
        out = set()
        for r in self.run_starts():                      # the serious carriers of each flag carried in the window: a hand-off counts the player who takes it on (golden Book v One 9:16), a brief pickup handed on does not (hdm v One 17:24)
            if r["tm"] != tm: continue
            if t - 10 <= self._went_to_run(r) <= t + READ_TO: out.add(r["runner"])
            out |= {a for a, s0, e0 in r["carries"] if a in r["serious"] and s0 <= t + READ_TO and (e0 is None or e0 >= t - 10) and (s0 >= t - 10 or self.carrying(a, min(t + READ_FROM, self.T)))}
        return out

    def _rest(self, tm, t, runners):
        """Where the rest of the main team went, from the records: a split it sent (attempts), a push in (attempts), a
        push on their flagger (flag_pushes), a move back or up (ground), else where it stood READ_FROM to READ_TO."""
        T, foe = self.T, 3 - tm
        main = [a for a in self.main_team(tm, t) if self.AL[a][t] and a not in runners]
        def of_main(ids): return main and sum(1 for a in ids if a in main) * 2 >= len(main)
        sp = [x for x in self.attempts() if x["tm"] == tm and x["kind"] == "split" and t - 2 <= x["t0"] <= t + READ_TO and x["max"] >= 2 and of_main(x["ids"])]      # a split by others is not where the rest went
        if sp: return f"split by the {sp[0]['way'] or 'door'}", sp[0]
        for w in self.way_out():                         # out by a door, and a split from it within PURPOSE_S, is a split by that door (R-325: a leave's purpose is fixed 60 s on; golden Apes v Book 22:04)
            if w["tm"] != tm or not (t - 2 <= w["t"] <= t + READ_TO): continue
            later = [x for x in self.attempts() if x["tm"] == tm and x["kind"] == "split" and w["t"] <= x["t0"] <= w["t"] + PURPOSE_S and x["max"] >= 2]
            return (f"split by the {w['door']}" if later else f"go out by the {w['door']}"), w
        pu = [x for x in self.attempts() if x["tm"] == tm and x["kind"] == "push" and t - 2 <= x["t_in"] <= t + READ_TO]
        if pu: return "push in", pu[0]
        fp = [x for x in self.flag_pushes() if x["tm"] == tm and x.get("main") and t - 2 <= x["t"] <= t + READ_TO]
        if fp: return "push their flagger", fp[0]
        gr = [x for x in self.ground() if x["tm"] == tm and x["group"] == "main" and t - 2 <= x["t"] <= t + READ_TO and x["to_kind"] not in ("stand", "greater stand", "field")]     # a move about the stand is not falling back or pushing up
        if gr:
            g = gr[0]; own = self.st.side.get(tm)
            if g["way"] == "back":
                if g["from_side"] != own and g["from_kind"] in ("pit", "base", "front door", "back door"): return "fall out", g
                return {"pit": "retreat to the pit", "base": "fall back into the base", "front door": "fall back into the base", "back door": "fall back into the base",
                        "front footies": "fall to footmen", "back footies": "fall to footmen"}.get(g["to_kind"] if g["to_side"] == own else "", "fall back"), g
            if g["to_side"] == foe or (g["to_side"] not in (None, own) and g["to_kind"] in ("front door", "back door", "base", "pit", "front footies", "back footies")):
                return "push up to their " + (g["to_kind"] if g["to_kind"] in ("front door", "back door") else "base"), g
            return "push up", g
        ps = collections.Counter()
        for u in range(min(t + READ_FROM, T), min(t + READ_TO, T) + 1, 2):
            g = [a for a in self.main_team(tm, u) if self.AL[a][u] and a not in runners]
            if g: ps[collections.Counter(self.place_at(a, u) for a in g).most_common(1)[0][0]] += 1
        if not ps: return "nobody", None
        (k, sd), own = ps.most_common(1)[0][0], self.st.side.get(tm)
        g0 = [a for a in self.main_team(tm, t) if self.AL[a][t] and a not in runners]      # where it stood at the moment: a step along the ladder by then is a push up or a fall back, however short (golden Men v hdm 3:50: from the stand to hdm's front door)
        if g0:
            k0, sd0 = collections.Counter(self.place_at(a, t) for a in g0).most_common(1)[0][0]
            l0, l1 = self._ladder(tm, k0, sd0), self._ladder(tm, k, sd)
            if l1 <= -2 and l1 < l0: return "push up to their " + (k if k in ("front door", "back door") else "base"), None
            if l1 >= 2 and l1 > l0: return {"pit": "retreat to the pit", "front footies": "fall to footmen", "back footies": "fall to footmen"}.get(k, "fall back into the base"), None
        if k in ("stand", "greater stand"): return "stay at the stand", None
        if sd == own: return {"pit": "retreat to the pit", "base": "fall back into the base", "front door": "fall back into the base", "back door": "fall back into the base",
                              "front footies": "fall to footmen", "back footies": "fall to footmen"}.get(k, "stay on their side"), None
        if sd is not None: return "stay on the enemy's side", None
        return "stay at the stand", None

    def call(self, x, s):
        fam, tm, t, foe = x["family"], x["tm"], x["t"], 3 - x["tm"]
        role = lambda a: self.m.roles[a]
        if fam == 1:
            runners = self._runners(tm, t)
            rest, rec = self._rest(tm, t, runners)
            n = min(len(runners), 2)
            lab = ("no runner", "one runner", "two runners")[n]
            return {"key": f"{n}|{rest}", "label": f"{lab.capitalize()}; the rest {rest}", "runners": n, "rest": rest,
                    "shape": {"runners": sorted(role(a) for a in runners), "from": rec and {k: rec.get(k) for k in ("t", "t_in", "t0", "way", "to", "from", "door", "to_kind", "to_side") if k in rec}}}
        if fam == 2 and x["triggers"][0] not in ("split", "split grows"):       # a later moment of a split (it grows, changes door, divides) or a stand-off: the defenders are the own players on their own ground near the enemy's split READ_FROM to READ_TO on
            dids = None
            if "split stand-off" in x["triggers"]:
                r = x["refs"][0]; ene, k = set(), len(r["who"][foe])
                n, defs = len(r["who"][tm]), list(r["who"][tm])
            else:
                g = x["refs"][0]; own = self.st.side.get(tm)
                ene = [a for a, q in zip(g["ids"], g["members"]) if q["from"] <= t + READ_TO and q["to"] >= t]
                cnt, who = collections.Counter(), collections.defaultdict(int)
                for u in range(min(t + READ_FROM, self.T), min(t + READ_TO, self.T) + 1, 2):
                    near = [b for b in self.st.players[tm] if self.AL[b][u] and self.place_at(b, u)[1] == own and any(self.AL[e][u] and d(self.P[b][u], self.P[e][u]) < FIGHT_LINK for e in ene)]
                    cnt[len(near)] += 1
                    for b in near: who[b] += 1
                n = max(cnt, key=lambda c: (cnt[c], c)) if cnt else 0
                dids = [b for b, _ in sorted(who.items(), key=lambda kv: -kv[1])[:n]]
                defs = [role(b) for b in dids]
                u0 = min(t + READ_FROM, self.T)                 # the split still on their ground: a player who left it through mid is answered elsewhere (golden Men v hdm 9:36: the Prot mirrors the Air Ele, 3 v 3 at the back door)
                k = max(1, sum(1 for e in ene if self.AL[e][u0] and self.place_at(e, u0)[1] == own and self.place_at(e, u0)[0] != "field"))
            monks = sum(1 for r_ in defs if "Monk" in r_ and "WoC" not in r_)
            alive = sum(self.AL[a][min(t + READ_TO, self.T)] for a in self.st.players[tm])
            if n >= max(6, alive - 1): c = "full collapse"
            elif n == 0: c = "no answer"
            elif n == 2 and monks == 2: c = "two monks"
            elif n == 1 and k > 1: c = "one defender"
            elif n == k: c = "mirror"
            elif n == k + 1: c = "add one"
            elif n < k: c = "defend a player down"
            else: c = f"send {n} against {k}"
            return {"key": c, "label": c.capitalize(), "defenders": n, "split": k, "monks": monks, "shape": {"defenders": defs, "ids": dids}}
        if fam == 2:
            g = x["refs"][0]; an = g["answer"]
            k = max(1, len([q for q in g["members"] if q["from"] <= t + READ_TO]))
            arrived = [(ta, r) for ta, r in an["arrivals"] if ta <= t + READ_TO + 10]
            went_back = len(an.get("went_back") or []) if (an.get("went_back_t") is None or an["went_back_t"] <= t + 60) else 0
            alive = sum(self.AL[a][min(t + READ_TO, self.T)] for a in self.st.players[tm])
            ids = set(an["ids"]); defs = [r for _, r in arrived] if "split grows" in x["triggers"] else an["defenders"]
            n = len(defs) if "split grows" in x["triggers"] else an["n"]
            monks = sum(1 for r in defs if "Monk" in r and "WoC" not in r)
            if went_back >= 5 or n >= max(6, alive - 1): c = "full collapse"
            elif n == 0: c = "no answer"
            elif n == 2 and monks == 2: c = "two monks"
            elif n == 1 and k > 1: c = "one defender"
            elif n == k: c = "mirror"
            elif n == k + 1: c = "add one"
            elif n < k: c = "defend a player down"
            else: c = f"send {n} against {k}"
            return {"key": c, "label": c.capitalize(), "defenders": n, "split": k, "monks": monks,
                    "shape": {"defenders": defs, "behind_s": an["behind_s"], "met": an["met"], "went_back": an.get("went_back")}}
        rest, rec = self._rest(tm, t, set())
        side = x["triggers"][0]
        c = {"fall out": "fall out", "retreat to the pit": "retreat down the ladder", "fall back into the base": "retreat down the ladder", "fall to footmen": "retreat down the ladder",
             "fall back": "retreat down the ladder", "push in": "push in", "push their flagger": "push their flagger"}.get(rest)
        if c is None: c = "push up" if rest.startswith(("push up", "go out")) else ("split" if rest.startswith("split") else "stay")
        return {"key": c, "label": c.capitalize() + ("" if c == rest else f" ({rest})"), "rest": rest,
                "shape": {"from": rec and {k: rec.get(k) for k in ("t", "t_in", "t0", "way", "to", "from", "door", "to_kind", "to_side") if k in rec}}}

    def verbs(self, tm, t):
        """Everything the team did in the call's window (t - 2 to t + READ_TO), as Denning's verbs (REDESIGN "his
        vocabulary"), each read from its record: run (who went to run), split (who, by which door: attempts),
        join (who came to a fight: moves, his "collapse"), push their flagger (flag_pushes), push in (attempts),
        out by a door (way_out), fall back, fall out, push up (ground, the main team)."""
        lo, hi, m, own, out = t - 2, t + READ_TO, self.m, self.st.side.get(tm), []
        for a in self._runners(tm, t): out.append(("run", m.roles[a]))
        for x in self.attempts():
            if x["tm"] != tm: continue
            if x["kind"] == "split" and lo <= x["t0"] <= hi: out.append(("split", x["way"] or "door"))
            if x["kind"] == "split":
                out += [("split", q["role"]) for q in x["members"] if lo <= q["from"] <= hi]
            if x["kind"] == "push" and lo <= x["t_in"] <= hi: out.append(("push in", x["way"] or ""))
        for x in self.moves():
            if x["tm"] == tm and x["kind"] == "join" and lo <= x["t"] <= hi: out += [("join", r) for r in x["roles"]]
        for x in self.flag_pushes():
            if x["tm"] == tm and lo <= x["t"] <= hi: out += [("push their flagger", r) for r in x["roles"]]
        for w in self.way_out():
            if w["tm"] == tm and lo <= w["t"] <= hi: out.append(("out by", w["door"]))
        for g in self.ground():
            if g["tm"] == tm and lo <= g["t"] <= hi:
                if g["way"] == "back": out.append(("fall out" if g["from_side"] not in (None, own) and g["from_kind"] in ("pit", "base", "front door", "back door") else "fall back", g["group"]))
                else: out.append(("push up", g["group"]))
        for x in self.attempts():                         # an answer to the enemy's split: defenders arriving in the window
            if x["tm"] == 3 - tm and x["kind"] == "split":
                out += [("answer", r) for ta, r in x["answer"]["arrivals"] if lo <= ta <= hi]
        return sorted(set(out))

    # ---- stage D (2.8, 2.9): the shape of the call (R-297) and the consequence record (R-294, R-412)
    def _tl(self):
        """The map's numbers every SPLIT_STEP, read once from the fights: for each team, the fight its main team
        stands in (its numbers, own first; who of it is in that fight; its place), the other fights on the map with
        both teams in them (own players less the enemy's, summed: a power play on a split is a number above 0), and
        its players away for the flag (carrying it, going back for it or at the spawn for it, and not in the main
        team's fight)."""
        if self._tl_ is not None: return self._tl_
        st, out = self.st, {}
        for t in range(0, self.T + 1, SPLIT_STEP):
            fs = [g for g in self.fights(t) if g["n"][1] and g["n"][2]]
            row = {}
            for tm in st.teams:
                foe = 3 - tm
                mt = [a for a in self.main_team(tm, t) if self.AL[a][t]]
                mine = [g for g in fs if mt and len(g["ids"][tm] & set(mt)) * 2 >= len(mt)]
                f = max(mine, key=lambda g: g["n"][1] + g["n"][2]) if mine else None
                inf = f["ids"][tm] if f else frozenset(mt)
                row[tm] = {"main": (f["n"][tm], f["n"][foe]) if f else None, "ids": inf, "place": (f["kind"], f["side"]) if f else None,
                           "side": sum(g["n"][tm] - g["n"][foe] for g in fs if g is not f),
                           "side_n": sum(1 for g in fs if g is not f),
                           "flag_away": [a for a in st.players[tm] if a not in inf and self._flagger(a, tm, t)]}
            out[t] = row
        self._tl_ = out
        return out

    def _npc_deaths(self):
        """[(second, the team that lost it, kind)] for every knight, archer, bodyguard, footman and Guild Lord killed."""
        if self._npcd is None:
            m, seen, out = self.m, set(), []
            for r in m.o["ev"]:
                x = r[2]
                if r[1] != "dt" or not isinstance(x, int) or x >= len(m.A) or x in seen: continue
                k = m.A[x].get("npc")
                if k in ("knight", "archer", "bodyguard", "footman", "guild_lord") and m.A[x].get("team") in self.st.teams:
                    seen.add(x); out.append((r[0] / 10, m.A[x].get("team"), k))
            self._npcd = sorted(out)
        return self._npcd

    def _boosts(self):
        """[(second, team)] for every morale boost that landed: every BOOST_EVERY of holding the stand."""
        if self._bst is None:
            out, caps = [], self.st.caps + [(self.st.end + 1, None)]
            for (c, h), (c2, _) in zip(caps, caps[1:]):
                k = 1
                while h in self.st.teams and c + BOOST_EVERY * k < c2: out.append((c + BOOST_EVERY * k, h)); k += 1
            self._bst = out
        return self._bst

    def gained_elsewhere(self, tm, t, main=True):
        """What the team was gaining elsewhere at second t (R-321, the timing rule of R-297): a live numbers
        advantage in its main team's fight (not for a numbers moment, main=False: there the main fight is the moment
        itself, and elsewhere is a fight away from it), NPC damage in progress (its players hit an enemy NPC within
        PIT_S), or its own boost about to land (BOOST_WARN_S). Empty when nothing was."""
        out, row = [], self._tl()[min(max(int(t), 0), self.T) // SPLIT_STEP * SPLIT_STEP][tm]
        if main and row["main"] and row["main"][0] > row["main"][1]: out.append("numbers in the main fight (%d v %d)" % row["main"])
        if not main and row["side"] > 0: out.append("numbers in a fight away from the main one")
        if any(t - PIT_S <= u <= t for a in self.st.players[tm] for u in self.npc_hits.get(a, ())): out.append("NPC damage in progress")
        owner, since = self.st.stand_owner(t)
        if owner == tm and BOOST_EVERY - (t - since) % BOOST_EVERY <= BOOST_WARN_S: out.append("its boost about to land")
        return out

    def _props(self, ids):
        """A group of players as properties, not class names (REDESIGN "Shape": the same call by a Mesmer and a
        Ranger is compared on what the two can do): how many, backline monks, heals and prots on their bars (skills),
        self-defence (skills), snares and speed (power, movepower.py) and escapes. NPC damage is not here yet: it
        has to be measured per bar, not read from a skill list."""
        from buildfeat import FEATURES, PLAYER_FLAGS, _skills
        from movepower import player_power
        S, m = _skills(), self.m
        out = {"n": len(ids), "monks": self._mk(ids), "heals": 0, "prots": 0, "self_defence": 0, "snare": 0.0, "speed": 0.0, "escapes": 0}
        for a in ids:
            for b in m.A[a].get("bar", []):
                s = S.get(m.sk(b)) if b else None
                if not s: continue
                out["heals"] += bool(FEATURES["heals"](s)); out["prots"] += bool(FEATURES["prots"](s)); out["self_defence"] += bool(PLAYER_FLAGS["self_defence"](s))
            p = player_power(m, a)
            out["snare"] += p["snare"]; out["speed"] += p["speed"]; out["escapes"] += p["escapes"]
        out["snare"], out["speed"] = round(out["snare"], 1), round(out["speed"], 1)
        return out

    def _came_by(self, b, tm, t_from, t_to):
        """The way a player came home between two seconds: "home already" (on his own ground at the start), else the
        last of his own doors he stood on before the end ("front door", "back door"), "by a teleporter" when he
        covered more than GROUND_JUMP in one step on the way, else "through the base" (in by neither drawn door)."""
        own, T = self.st.side.get(tm), self.T
        homeg = ("pit", "base", "front door", "back door", "front footies", "back footies")
        u0, u1 = min(max(int(t_from), 0), T), min(max(int(t_to), 0), T)
        if not self.AL[b][u0]: return "from the res shrine"
        k, sd = self.place_at(b, u0)
        if sd == own and k in homeg: return "home already"
        door, tele = None, False
        for u in range(u0 - u0 % SPLIT_STEP, u1 + 1, SPLIT_STEP):
            if not self.AL[b][u]: continue
            k, sd = self.place_at(b, u)
            if sd == own and k in ("front door", "front footies"): door = "front door"
            elif sd == own and k in ("back door", "back footies"): door = "back door"
            v = u - SPLIT_STEP
            if v >= 0 and self.AL[b][v] and d(self.P[b][u], self.P[b][v]) > GROUND_JUMP: tele = True
        return "by a teleporter" if tele and door is None else (door or "through the base")

    def shape(self, x, c):
        """The shape of a call (R-297): who (the players it was made with, as properties), which way (the route:
        the drawn flag run and door for a runner, the door a defender came home by, the door or the ground of a
        push or a fall back) and when (seconds from the moment to the first of them moving). A delay is a decision
        when something was being gained elsewhere as the moment came (R-321) and execution otherwise; nothing else
        is read into it (intent is not in a replay). On time is within ON_TIME_S and late from LATE_S (R-348)."""
        fam, tm, t, m = x["family"], x["tm"], x["t"], self.m
        old = c.get("shape") or {}
        rec, ids, when, way = old.get("from"), [], None, {}
        if fam == 1:
            ids = sorted(self._runners(tm, t))
            gone = [self._went_to_run(r) for r in self.run_starts() if r["tm"] == tm and (r["runner"] in ids or r["a"] in ids) and t - 10 <= self._went_to_run(r) <= t + READ_TO]
            when = min(gone) if gone else None
            fr = next((f for f in self.flags_record() if f["tm"] == tm and set(f["ids"]) & set(ids) and f["end"] >= t - 10 and f["start"] <= t + READ_TO + PURPOSE_S), None)
            if fr: way = {"flag_run": fr["route"], "door": fr["door"], "walk_back": fr["back_route"], "form": fr["form"]}
        elif fam == 2:
            g = x["refs"][0]
            if "answer" in g:
                an = g["answer"]
                first = {b: ta for b, (ta, _) in zip(an["ids"], an["arrivals"])}
                trig = x["triggers"][0]                      # the players the call was read from: the usual number of defenders, first to arrive first; for a split that grows, those there by the window; for a later moment, those near it in the window
                ids = list(an["ids"][:c.get("defenders") or 0]) if trig == "split" else [b for b in an["ids"] if first[b] <= t + READ_TO + 10] if trig == "split grows" else list(old.get("ids") or [])
                came = collections.Counter(self._came_by(b, tm, min(g["t0"], t), first.get(b, t + READ_TO)) for b in ids)
                way = {"came_by": dict(came), "met": an.get("met")}
                if trig == "split": when = (t + an["behind_s"]) if ids and an.get("behind_s") is not None else None      # how far behind the split its first defender was (R-348), from the split reaching their ground
                else: when = min((first[b] for b in ids if b in first and first[b] >= t - 2), default=None)
            else:                                           # a stand-off of split groups: the record keeps roles
                ids = [a for a in self.st.players[tm] if m.roles[a] in (old.get("defenders") or ())]
        else:
            ids = sorted(x["refs"][0]["ids"][tm])
            if rec: when = next((rec[k] for k in ("t_in", "t", "t0") if rec.get(k) is not None), None)
        if rec and fam != 2:                                # where the rest went: the door of a push, a split or a way out, the ground a move came to rest on
            door = rec.get("door") or (rec.get("way") if rec.get("way") in ("front door", "back door") else None)
            if door: way["door"] = way.get("door") or door; way["rest_door"] = door
            if rec.get("to_kind"): way["to"] = self.place_words(rec["to_kind"], rec.get("to_side"))
        delay = None if when is None else int(round(when - t))
        gained = self.gained_elsewhere(tm, t, main=fam != 3)
        tim = {"delay_s": delay, "gained_elsewhere": gained, "kind": None, "words": None}
        if delay is None and fam == 1 and ids: tim["words"] = "already under way"       # the runner had the flag, or was on his way for it, before the moment
        if delay is not None:
            if delay <= ON_TIME_S: tim["words"] = "on time"
            else:
                tim["words"] = (f"late, {delay} s" if delay >= LATE_S else f"after {delay} s")
                tim["kind"] = "decision" if gained else "execution"
        return dict(old, who=[m.roles[a] for a in ids], ids=list(ids), props=self._props(ids), way=way, timing=tim)

    def _main_step(self, tm, t):
        """Where the team's main team stands at second t as a step on its ladder (own pit 4 ... the stand 0 ... the
        enemy's pit -4), and that place in words. None when it has nobody alive."""
        g = [a for a in self.main_team(tm, t) if self.AL[a][t]]
        if not g: return None, None
        k, sd = collections.Counter(self.place_at(a, t) for a in g).most_common(1)[0][0]
        return self._ladder(tm, k, sd), self.place_words(k, sd)

    def consequence(self, tm, t):
        """What followed a moment, over the whole map, at each of CONSEQ_S (90 s and about 3 min, R-294): hard
        results only, each as [own, enemy] from the deciding team's side. Deaths; NPCs lost (by kind); each Guild
        Lord's health then and now (rebuilt, lord.py; None where its damage was not observed); captures and boosts landed; morale (the eight players' morale summed, then and now);
        the flag lead in flags then and now (R-408) and who holds the stand; and, so that what was given up in flags
        can be set beside what was gained for it (R-412), the numbers meanwhile: seconds the main team's fight was a
        player or more up, even and down, the player-seconds it adds up to (8 v 7 for 30 s is 30), the same for
        every other fight on the map (a power play on a split), and the seconds each team had a player away for the
        flag. Then where the main team stood at the end, as a step on its ladder. `ended` when the match ended inside
        the window (with who won). Win points are added beside these when the win model is rebuilt (stage E)."""
        st, T, foe, S = self.st, self.T, 3 - tm, SPLIT_STEP
        tl, both = self._tl(), lambda f: [f(tm), f(foe)]
        won = (st.m.o["meta"].get("result") or {}).get("winning_team_id")
        ms = lambda k, u: sum(st.morale(a, u) for a in st.players[k])
        if self._lord is None:
            from lord import LordState
            self._lord = LordState(st)
        def lh(k, u):
            v = self._lord.health(k, u)
            return None if v is None else round(v, 2)
        out = {}
        for H in CONSEQ_S:
            t1 = min(t + H, T)
            R = range(t - t % S + S, t1 + 1, S)
            npc = lambda k: [kd for u, k2, kd in self._npc_deaths() if k2 == k and t < u <= t1]
            num = {"main_up_s": 0, "main_even_s": 0, "main_down_s": 0, "main_net": 0, "side_up_s": 0, "side_down_s": 0, "side_net": 0}
            away = [0, 0]
            for u in R:
                row = tl[u][tm]
                if row["main"]:
                    dn = row["main"][0] - row["main"][1]
                    num["main_up_s" if dn > 0 else "main_down_s" if dn < 0 else "main_even_s"] += S; num["main_net"] += dn * S
                if row["side_n"]:
                    num["side_net"] += row["side"] * S
                    if row["side"] > 0: num["side_up_s"] += S
                    elif row["side"] < 0: num["side_down_s"] += S
                away[0] += S * bool(row["flag_away"]); away[1] += S * bool(tl[u][foe]["flag_away"])
            owner, _ = st.stand_owner(t1)
            l0, l1 = self.lead_value(tm, t), self.lead_value(tm, t1)
            s0, s1 = self._main_step(tm, t), self._main_step(tm, t1)
            out[str(H)] = {
                "to": t1, "ended": t + H > T, "won": (won == tm) if (t + H > T and won in st.teams) else None,
                "deaths": both(lambda k: sum(1 for a in st.players[k] for td in st.death_times.get(a, []) if t < td <= t1)),
                "npcs": both(lambda k: len(npc(k))), "npc_kinds": both(lambda k: sorted(npc(k))),
                "lord": both(lambda k: [lh(k, t), lh(k, t1)]),
                "caps": both(lambda k: sum(1 for u, h in st.caps if h == k and t < u <= t1)),
                "boosts": both(lambda k: sum(1 for u, h in self._boosts() if h == k and t < u <= t1)),
                "morale": both(lambda k: [ms(k, t), ms(k, t1)]),
                "lead": [l0, l1], "lead_change": None if l0 is None or l1 is None else round(l1 - l0, 2),
                "stand": "own" if owner == tm else "enemy" if owner == foe else "nobody",
                "numbers": num, "flag_away_s": away, "step": [s0[0], s1[0]], "place": s1[1]}
        return out

    def runner_cost(self):
        """What running a flag costs in players at the main fight (R-412: "roughly 0.8 of a player down, to be
        measured"). One row a flag life that was run (not the pre-game flag): its form; the run in seconds, from the
        runner leaving his team for it (R-360) to its end; the seconds of that run in which his main team stood in a
        fight; and the player-seconds of those in which a carrier of this flag, alive, was not in that fight. The
        share missing over all runs is the measured number."""
        tl, out = self._tl(), []
        for f in self.flags_record():
            if f["pregame"]: continue
            tm, s0, e = f["tm"], int(f["set_off"] if f["set_off"] is not None else f["start"]), int(f["end"])
            fight = miss = 0
            by, own = {"stand": [0, 0], "own": [0, 0], "enemy": [0, 0]}, self.st.side.get(tm)      # the same by where the main fight stood: around the stand, on the runner's own ground, on the enemy's
            for u in range(s0 - s0 % SPLIT_STEP, min(e, self.T) + 1, SPLIT_STEP):
                row = tl[u][tm]
                if not row["main"]: continue
                gone = SPLIT_STEP * min(1, sum(1 for a in set(f["ids"]) if self.AL[a][u] and a not in row["ids"]))
                fight += SPLIT_STEP; miss += gone
                k, sd = row["place"]
                w = by["stand" if k in ("stand", "greater stand") else "own" if sd == own else "enemy"]
                w[0] += SPLIT_STEP; w[1] += gone
            out.append({"form": f["form"] or f["how"] or "open", "how": f["how"], "run_s": e - s0, "away_s": f["away_s"], "fight_s": fight, "miss_s": miss, "by": by})
        return out

    def flag_duty(self):
        """Over the whole match, for each team: the seconds its main team stood in a fight, and the player-seconds of
        those in which one of its players was away for the flag (the average players down for the flag, R-412)."""
        tl, out = self._tl(), {}
        for tm in self.st.teams:
            rows = [r[tm] for r in tl.values() if r[tm]["main"]]
            out[tm] = (len(rows) * SPLIT_STEP, sum(len(r["flag_away"]) for r in rows) * SPLIT_STEP)
        return out

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
                who = [m.roles[r["a"]]] if r else None
            elif x["family"] == 2: who = list(ref["who"][3 - tm]) if "split stand-off" in x["triggers"] else [q["role"] for q in ref["members"]]
            c = self.call(x, s)
            c["shape"] = self.shape(x, c)                   # who, which way, when (R-297)
            out.append({"id": f"{m.o['meta']['id'][:8]}-{x['family']}-{tm}-{t}", "rid": m.o["meta"]["id"], "family": x["family"],
                        "t": t, "team": m.tag[tm], "tm": tm, "triggers": x["triggers"], "who": who,
                        "scenario": self.scenario(x, s), "call": c, "verbs": self.verbs(tm, t), "forced": bool(died), "died": died, "state": s,
                        "after": self.consequence(tm, t)})
        return out


def match_records(rid):
    from replaylib import Match
    from state import GameState
    from scoreboard import Scoreboard
    st = GameState(Match.from_branch(rid))
    if not st.hall: return None
    M = Moments(st, Scoreboard(st))
    recs = M.records()
    import jobs                                          # the plays and their jobs; each moment gets its allocation (R-425)
    EXTRA[rid] = {"runs": M.runner_cost(), "duty": [M.flag_duty()[tm] for tm in (1, 2)], "plays": jobs.plays(M, recs), "flags": jobs.bench_rows(M),
                  "flag_moments": dict(collections.Counter(r["moment_rule"] for r in M.run_starts() if r["set_off"] is not None))}
    return recs


EXTRA = {}       # report id -> the runner cost rows of the match last read (R-412), kept beside the records by `all`


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
    try: return rid, match_records(rid), EXTRA.pop(rid, None)
    except Exception as e: return rid, {"error": f"{type(e).__name__}: {e}"}, None


def dev_ids():
    """The development set (R-453): the matches Denning has reviewed, the golden and the line-up games. Run after every
    change (`moments.py all <file> --dev`, under a minute); every match only at a checkpoint."""
    import common, os
    here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    want = json.load(open(os.path.join(here, "data", "model", "dev_set.json")))["matches"]
    have = set(common.replay_ids())
    return [r for r in want if r in have]


def run_all(path, jobs=2, ids=None):
    import multiprocessing, common
    ids, out, bad, extra = (ids if ids is not None else common.replay_ids()), {}, {}, {}
    idx = common.replay_index()
    with multiprocessing.Pool(jobs) as pool:
        for rid, rec, ex in pool.imap_unordered(_one, ids, chunksize=4):
            if isinstance(rec, dict): bad[rid] = rec["error"]
            elif rec is not None: out[rid] = rec; extra[rid] = ex
    json.dump({"matches": {r: {"map": idx[r]["map"], "date": idx[r]["date"][:10], "teams": idx[r]["teams"]} for r in out},
               "records": [x for r in sorted(out) for x in out[r]], "plays": [p for r in sorted(out) for p in (extra[r] or {}).get("plays", [])],
               "flag_cost": {r: {k: v for k, v in (extra[r] or {}).items() if k != "plays"} for r in out}, "errors": bad}, open(path, "w"), default=list)
    print(len(out), "matches,", sum(len(v) for v in out.values()), "moments,", len(bad), "errors", list(bad.items())[:3])
    fm = collections.Counter()
    for r in out:
        for k, v in ((extra[r] or {}).get("flag_moments") or {}).items(): fm[k] += v
    print("flag runs set off for, by how the moment is read (R-461):", dict(fm))
    if blanks([x for r in sorted(out) for x in out[r]], [p for r in sorted(out) for p in (extra[r] or {}).get("plays", [])]): sys.exit(1)


def blanks(records, plays):
    """A reading which fails must fail loudly (R-460). Counts the blanks of every field of the moments' state and of the
    plays; a field blank on every row is a fault, printed as one and returned (the run then ends with an error). A
    blank that only means "not in the replay", or "does not apply here", shows as a share and is no fault."""
    rows = collections.defaultdict(lambda: [0, 0])
    def see(name, v): rows[name][0] += 1; rows[name][1] += v is None
    for x in records:
        for k, v in x["state"].items(): see("state." + k, v)
        for k in ("who", "scenario", "call", "verbs", "after"): see("moment." + k, x.get(k))
    for p in plays:
        for k in ("team", "scenario", "job", "met", "moment"):
            if k in p: see("play." + k, p[k])
        for k, v in (p.get("beside") or {}).items(): see(f"play[{p['play']}].beside." + k, v)
    some = sorted(((b / n, k) for k, (n, b) in rows.items() if b and b < n), reverse=True)
    fault = sorted(k for k, (n, b) in rows.items() if n >= 20 and b == n)
    print("blank in part (share of rows):", ", ".join(f"{k} {s:.0%}" for s, k in some) or "none")
    if fault: print("FAULT, blank on every row:", ", ".join(fault))
    return fault


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


def after(path):
    """What followed each call, on average, at 90 s (the consequence record over every counted match). A description
    for checking that the readings make sense, not a verdict: nothing here is adjusted for the situation, and a call
    made from a losing position looks worse than it was. Forced reads are left out."""
    D = json.load(open(path)); R = [x for x in D["records"] if not x["forced"] and not x["after"]["90"]["ended"]]
    mean = lambda xs: (sum(xs) / len(xs)) if xs else 0.0
    print(len(R), "moments not forced, the match still going 90 s on. Columns, all from the deciding team's side over the 90 s: deaths (own, enemy);")
    print("NPCs lost (own, enemy); change in flag lead (flags); player-seconds up in the main team's fight; the same in other fights;")
    print("seconds with a player away for the flag (own, enemy); steps moved on the ladder (+ is toward the own pit)")
    for fam in (1, 2, 3):
        F = [x for x in R if x["family"] == fam]
        print(f"\nFamily {fam}: {FAMILY[fam]} ({len(F)})")
        for k, n in collections.Counter(x["call"]["key"] for x in F).most_common(12):
            G = [x["after"]["90"] for x in F if x["call"]["key"] == k]
            L = [g["lead_change"] for g in G if g["lead_change"] is not None]
            St = [g["step"][1] - g["step"][0] for g in G if None not in g["step"]]
            print(f"  {n:5} {k[:44]:44} deaths {mean([g['deaths'][0] for g in G]):.2f} {mean([g['deaths'][1] for g in G]):.2f}  NPCs {mean([g['npcs'][0] for g in G]):.2f} {mean([g['npcs'][1] for g in G]):.2f}"
                  f"  lead {mean(L):+.2f}  main {mean([g['numbers']['main_net'] for g in G]):+6.1f}  other {mean([g['numbers']['side_net'] for g in G]):+6.1f}"
                  f"  away {mean([g['flag_away_s'][0] for g in G]):4.1f} {mean([g['flag_away_s'][1] for g in G]):4.1f}  ladder {mean(St):+.2f}")
    T = [x["call"]["shape"]["timing"] for x in R]
    dl = [t for t in T if t["kind"]]
    print(f"\nTiming (R-297, R-321): {sum(1 for t in T if t['delay_s'] is not None)} calls with a first move read; {sum(1 for t in T if t['words'] == 'on time')} on time; "
          f"{len(dl)} delayed, of which {sum(1 for t in dl if t['kind'] == 'decision')} with something being gained elsewhere (a decision) and {sum(1 for t in dl if t['kind'] == 'execution')} with nothing (execution)")
    gl = collections.Counter(g.split(" (")[0] for t in dl for g in t["gained_elsewhere"])
    print("  what was being gained: " + "; ".join(f"{k} {v}" for k, v in gl.most_common()))


def runner(path):
    """The cost of running a flag in players (R-412: "roughly 0.8 of a player down, to be measured"), three ways."""
    D = json.load(open(path)); X = D["flag_cost"]
    runs = [r for v in X.values() if v for r in v["runs"]]
    med = lambda xs: statistics.median(xs) if xs else 0
    cap = [r for r in runs if r["how"] == "captured"]
    print(f"{len(runs)} flags run in {len(X)} matches ({len(cap)} captured)")
    print("1. While a flag is being run (from the runner leaving his team for it to its end), in the seconds his main team stood in a fight:")
    for name, rows in [("every flag", runs), ("captured", cap)] + [(f, [r for r in runs if r["form"] == f]) for f, _ in collections.Counter(r["form"] or "open" for r in runs).most_common(6)]:
        fs, ms = sum(r["fight_s"] for r in rows), sum(r["miss_s"] for r in rows)
        print(f"   {(name or 'open'):22} {len(rows):5} flags; run {med([r['run_s'] for r in rows]):5.0f} s (median); a fight for {100 * fs / max(sum(r['run_s'] for r in rows), 1):3.0f}% of it; a carrier missing from that fight {ms / max(fs, 1):.2f} of the time")
    for k, words in (("stand", "around the stand"), ("own", "on the runner's own ground"), ("enemy", "on the enemy's ground")):
        fs, ms = sum(r["by"][k][0] for r in runs if "by" in r), sum(r["by"][k][1] for r in runs if "by" in r)
        print(f"   with the main fight {words:28} {fs:8} s of fight; a carrier missing {ms / max(fs, 1):.2f} of the time")
    print("2. Seconds away from the fight per flag (R-360) over the run's length, captured flags: "
          f"{sum(r['away_s'] for r in cap) / max(sum(r['run_s'] for r in cap), 1):.2f} (median away {med([r['away_s'] for r in cap]):.0f} s of {med([r['run_s'] for r in cap]):.0f} s)")
    duty = [v["duty"][i] for v in X.values() if v for i in (0, 1) if v["duty"][i][0] >= 120]
    sh = sorted(d_[1] / d_[0] for d_ in duty)
    q = lambda p: sh[int(p * (len(sh) - 1))] if sh else 0
    print(f"3. Over a whole match, players away for the flag while the main team stood in a fight: {sum(d_[1] for d_ in duty) / max(sum(d_[0] for d_ in duty), 1):.2f} of a player on average "
          f"({len(duty)} team-matches; a quarter of them under {q(0.25):.2f}, half under {q(0.5):.2f}, a quarter over {q(0.75):.2f})")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "all": run_all(a[1], int(a[a.index("--jobs") + 1]) if "--jobs" in a else 2, dev_ids() if "--dev" in a else None)
    elif a and a[0] == "counts": counts(a[1])
    elif a and a[0] == "after": after(a[1])
    elif a and a[0] == "runner": runner(a[1])
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
        if len(a) > 1 and a[1] in ("splits", "flags"):         # the records, as kept
            from replaylib import Match
            from state import GameState
            import common
            st_ = GameState(Match.from_branch(next((r for r in common.replay_ids() if r.startswith(a[0])), a[0])))
            M_ = Moments(st_)
            print(json.dumps({"flux": flux_at(st_.m.o["meta"]["started"]), "attempts": M_.attempts(), "caught": M_.caught(), "split_fights": M_.split_fights(), "moves": [{k: v for k, v in x.items() if k not in ("with", "ids", "each")} for x in M_.moves()]} if a[1] == "splits" else M_.flags_record(), indent=1, default=list))
            sys.exit()
        recs = match_records(a[0]) or []
        for x in recs:
            if len(a) > 1 and str(x["family"]) != a[1]: continue
            print(f"{Match.f(x['t'] * 10):>5} F{x['family']} {x['team']:5} {x['scenario']['label']}"
                  + (f" ({', '.join(x['who'])})" if x["who"] else "") + f" -> {x['call']['label']}" + (" [forced: " + ", ".join(x["died"]) + "]" if x["forced"] else ""))
    else: print(__doc__)
