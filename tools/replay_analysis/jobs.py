"""Plays and their jobs (docs/REDESIGN.md 2.11; R-298; Denning's rulings of 2026-11-13, R-423 to R-437).

A call is an allocation (R-425): at a moment a team has players running a flag, pushing the enemy's flagger, on a
split, defending one, collapsing on one, and the rest standing somewhere. Each part is a PLAY, read from its own record
(moments.py: the record is the work, R-362), and each play has a JOB with a success test read across the whole map.
A job runs on its own clock: to the event that ends it (R-424: a flag job until that flag is capped or returned, a
split job for the life of the split, a numbers job until the numbers are level, a delay job until help arrives or the
next base res), never a fixed 90 s. Whether the job was met is a RESULT. It is not a verdict on the call (that comes
from similar cases) and not a reading of execution (read before the result). What a play cost elsewhere is kept
beside it and is never part of its test (R-427: a test covers only what the players of the play control).

The plays (each a dict: play, side, tm, team, t0, t1, who, scenario, job, tests {words: held}, met, beside, ruled):
  flag            their run (single, or double; a hand-off to cap counts as single) against ours (stay, single run,
                  double run, a flag already in hand), R-426
  push flagger    players on the enemy's flagger: stopped, or 30% later than the hall's usual, R-427; and from the
                  flagger's side, helped or flagged through it (gap 8, R-434)
  split           each split attempt from both sides (R-428): the attacker's job is set by the answer it met; the
                  defender's by what it sent; a collapse (players leave the main fight to kill it, then go back) and a
                  full collapse are their own calls (R-429); a lone defender part-running his flag (R-430); the race
                  back when it ends (gap 6)
  numbers         a numbers difference in the main team's fight from kills, players split elsewhere or a wipe (the one
                  from a runner away is the flag decision's own consequence and is merged into it, R-431)
  boost           the enemy's boost is coming: deny it, or concede it for kills (gap 2)
  pinned          a team held in its own base or pit: hold the NPCs and lose nobody until the base res, or break out
                  (gap 1)
  base res        in the enemy's base as its dead come back: be out, or set for the fight (gap 5)
  lord            a push on the Guild Lord from LORD_PUSH_FROM, both sides (R-435): attackers against the pit NPCs
                  alive, monks with the push, Lord damage or the kill; the result is the match

Usage:  python3 jobs.py <report id>                     the plays of one match
        python3 jobs.py summary <file from moments.py all>   how often each job was met, by play and scenario
        python3 jobs.py bench <file from moments.py all>     rebuild data/benchmarks/flag_arrival.json
In code: plays(M, recs) -> list of plays; allocation(recs, plays) adds each moment's plays to it."""
import collections, json, os, statistics, sys
from common import (FIGHT_ACT, FLAG_TAKEN_OUT_S, REPO, READ_TO, SPLIT_STEP, SPLIT_GAP_S, FIGHT_LINK, JOIN_S, JOIN_LOOK_S, NPC_NEAR, can_kill, SOH_REMOVED, RUN_SPEED, GROUND_JUMP, RES_EVERY, BOOST_EVERY, BOOST_WARN_S, BOOST_LATE_S, LEAD_HALF, LEAD_ONE, CARRY_SPEED, PIT_R,
                    FLAG_GAIN, PART_RUN_GAIN, LATE_FLAG, ANSWER_CAP_S, COLLAPSE_VISIT_S, PINNED_S, LORD_PUSH_FROM, LORD_BASE_R, AFTER_WIPE_MIN_S, NUMBERS_TAIL_S, FLAG_JOB_MAX_S)
from state import d

HOMEG = ("pit", "base", "front door", "back door", "front footies", "back footies")
_BENCH = None


def _usual_arrival(M, tm):
    """The usual seconds from the pickup at the spawn to arriving at the stand for this hall and side: measured
    (data/benchmarks/flag_arrival.json), else the walk at carrying speed."""
    global _BENCH
    if _BENCH is None:
        p = os.path.join(REPO, "data", "benchmarks", "flag_arrival.json")
        _BENCH = json.load(open(p))["usual"] if os.path.exists(p) else {}
    v = _BENCH.get(f"{M.m.o['meta']['map']}|{M.st.side.get(tm)}")
    if v: return v
    w = M.hall.walk(M.spawn[tm], M.hall.stand) if M.hall is not None and M.spawn.get(tm) else None
    return (w / CARRY_SPEED) if w else None


class _K:
    """Counting helpers over one match."""
    def __init__(self, M):
        self.M, self.st, self.T = M, M.st, M.T
        self.deaths = {tm: sorted((td, a) for a in M.st.players[tm] for td in M.st.death_times.get(a, [])) for tm in M.st.teams}
        self.npc = M._npc_deaths()

    def died(self, tm, a, b, ids=None):
        return sum(1 for td, x in self.deaths[tm] if a < td <= b and (ids is None or x in ids))

    def died_main(self, tm, a, b):
        """Deaths of a team at its main fight: every death but those of players who were out on a split when they died
        (R-466: a flag run is held to the deaths at the main fight, not to those of a split that was collapsed on)."""
        sp = [x for x in self.M.attempts() if x["kind"] == "split" and x["tm"] == tm]
        on_split = lambda x_, td: any(x_ in s["ids"] and q["from"] - 2 <= td <= q["to"] + 8 for s in sp for a_, q in zip(s["ids"], s["members"]) if a_ == x_)
        return sum(1 for td, x in self.deaths[tm] if a < td <= b and not on_split(x, td))

    def npcs(self, tm, a, b, pit=False):
        return sum(1 for u, k, kind in self.npc if k == tm and a < u <= b and kind != "guild_lord" and (not pit or kind in ("knight", "archer", "bodyguard")))

    def lead(self, tm, t): return self.M.lead_value(tm, min(max(int(t), 0), self.T))

    def gain(self, tm, a, b):
        x, y = self.lead(tm, a), self.lead(tm, b)
        return None if x is None or y is None else round(y - x, 2)

    def caps(self, tm, a, b): return [u for u, h in self.st.caps if h == tm and a < u <= b]


def _play(M, play, side, tm, t0, t1, who, scenario, job, tests, beside=None, ruled=True, any_of=None, **more):
    """tests: {words: held}, all needed; any_of: {words: held}, one needed."""
    met = all(tests.values()) and (not any_of or any(any_of.values()))
    return dict({"play": play, "side": side, "tm": tm, "team": M.m.tag[tm], "t0": int(t0), "t1": int(min(t1, M.T)), "who": list(who), "scenario": scenario, "job": job,
                 "tests": dict(tests), "any_of": dict(any_of or {}), "met": bool(met), "beside": beside or {}, "ruled": ruled}, **more)


# ---- the flag: their run against ours (R-426)
def _flag_rows(M):
    """The flags that were run, each with when its runner went for it: the second he set off for his spawn
    (run_starts: his walk there, not the last time he stood with his team, which can be a minute earlier), else the
    pickup when he was already there. `soh`: a carrier has Shadow of Haste on his bar (the flag mechanic since
    removed from the game: Denning sets those runs aside as examples)."""
    if getattr(M, "_frows", None) is not None: return M._frows
    out, m = [], M.m
    rs = {(r["tm"], int(r["pickup"])): r for r in M.run_starts()}
    pin = lambda tm, t: any(k == tm and a <= t <= b for k, a, b in pinned(M))
    others = [tuple(x["pts"][0]) for x in (M.hall.labels or []) if x.get("type") == "Flag stand" and x.get("pts") and d(tuple(x["pts"][0]), M.hall.stand) > 500]
    for f in M.flags_record():
        if f["pregame"]: continue
        r = next((rs[k] for k in ((f["tm"], int(f["start"]) + dt) for dt in (0, -1, 1)) if k in rs), None)
        s0, runner = int(f["start"]), f["runner"]
        if r is not None:
            went = r["set_off"] is not None and not pin(f["tm"], r["set_off"]) and not pin(f["tm"], r["pickup"])      # he walked back for it, his team not held in its base (a player falling back into his base with his team did not go to run)
            if went: s0 = min(int(r["moment"]), s0)                       # when he goes to run, by the hall (R-461)
            elif r["under_way"] is not None and r["under_way"] - r["pickup"] > FLAG_TAKEN_OUT_S:
                s0, runner = int(r["under_way"]), m.roles[r["runner"]]    # picked up at home and kept there: the run starts when its runner takes it out
        if r is not None and f["how"] != "captured" and not M.travelled(f["tm"], r["carries"]): continue      # picked up and put down at home: not a run
        e, other = int(f["end"]), False
        if r is not None and f["how"] != "captured" and r["carries"] and r["carries"][-1][2] is not None and r["carries"][-1][2] < e:
            e = int(r["carries"][-1][2])                                  # put down for good: the run ends there, not when the flag goes back to the spawn
            p = M.P[r["carries"][-1][0]][min(e, M.T)]
            other = bool(p) and any(d(p, o) < 400 for o in others)        # at the hall's other flag stand (his answer on TFS v 옷옷옷옷 2:54: the Obelisk flag stand)
        soh = M.day < SOH_REMOVED and any(m.sk(b) == "Shadow of Haste" for a in f["ids"] for b in m.A[a].get("bar", []) if b)      # R-456: only while the mechanic was in the game
        out.append(dict(f, runner=runner, s0=min(s0, e), pick=int(f["start"]), e=e, other_stand=other, double=(f["form"] or "").startswith("double"), soh=soh))
    M._frows = out
    return out


def flag_plays(M, K, pinned_at):
    FR, out, T, role = _flag_rows(M), [], M.T, M.m.roles
    runs = []                                                             # their runs: a flag dropped or returned and taken again at once is one run, the one that got further
    for f in sorted(FR, key=lambda f: (f["tm"], f["s0"])):
        if runs and runs[-1]["tm"] == f["tm"] and f["s0"] - runs[-1]["s0"] <= 10:
            if (f["how"] == "captured", f["e"]) > (runs[-1]["how"] == "captured", runs[-1]["e"]): runs[-1] = f
        else: runs.append(f)
    for f in sorted(runs, key=lambda f: f["s0"]):
        B, A = f["tm"], 3 - f["tm"]
        w0, w1 = f["s0"], min(f["e"], T)
        if w1 - w0 < 10 or pinned_at(A, w0): continue
        mine = [g for g in FR if g["tm"] == A]
        inhand = next((g for g in mine if g["pick"] < w0 - 15 and g["e"] > w0 + 5), None)
        new = next((g for g in mine if w0 - 15 <= g["s0"] <= w1), None)
        if inhand:                                                        # in hand means close to the flag stand (his mark, TFS v 옷옷옷옷 1:40). A flag on its way that goes on to be capped is our run, begun first; one that never gets in (carried off on a split, dropped) is no answer, and the run set off for in the window is
            c = next((a for a in inhand["ids"] if M.carrying(a, w0) and M.AL[a][w0]), None)
            held = c is not None and M.place_at(c, w0)[0] in ("stand", "greater stand")
            if not held: new, inhand = (inhand if inhand["how"] == "captured" or new is None else new), None
        if new is not None and not inhand and new["s0"] < w0 - 2: continue      # we set off first: their run is the answer to ours and is told from their side (his mark, hdm v hook 7:07: "it's hdm's decision, hook starts running first")
        theirs = "double run" if f["double"] else "single run"
        ours = "a flag already in hand" if inhand else "stay" if not new else "double run" if new["double"] else "single run"
        g = inhand or new
        who = [role[a] for a in dict.fromkeys(g["ids"])] if g else []
        scen = f"They {theirs.replace(' run', '')} run ({M.m.tag[B]}'s {f['runner']}{', to the Obelisk flag stand' if f['other_stand'] else ''}); {M.m.tag[A]}: {ours}"
        end = min(max(w1, g["e"] if g else w1), w0 + FLAG_JOB_MAX_S, T)
        dA, dB = (lambda t1: K.died_main(A, w0, t1)), (lambda t1: K.died_main(B, w0, t1))      # deaths at the main fights only (R-466)
        bes = lambda t1: {"flag_lead": [K.lead(A, w0), K.lead(A, t1)], "deaths_at_the_main_fight": [dA(t1), dB(t1)], "deaths_anywhere": [K.died(A, w0, t1), K.died(B, w0, t1)], "their_flag": f["how"], "their_form": f["form"], "our_form": g and g["form"]}
        kw = dict(their=theirs, ours=ours, soh=bool(f["soh"] or (g and g["soh"])))
        if ours == "a flag already in hand":
            t1 = min(w1 + ANSWER_CAP_S, T)
            caps_b = K.caps(B, w0, w1 + 1)
            ans = bool(caps_b) and bool(K.caps(A, caps_b[-1] - 1, caps_b[-1] + ANSWER_CAP_S))
            owner, since = M.st.stand_owner(max(g["e"] - 1, 0))
            pre = g["how"] == "captured" and owner == B and (BOOST_EVERY - (g["e"] - since) % BOOST_EVERY) <= BOOST_LATE_S
            out.append(_play(M, "flag", "own", A, w0, t1, who, scen, "Answer their cap at once, or cap just before their boost", {},
                             any_of={"their flag does not get in": not caps_b, f"our cap follows theirs within {ANSWER_CAP_S} s": ans, "our cap lands just before their boost": bool(pre)}, beside=bes(t1), **kw))
        elif ours == "stay":
            t1 = min(w1 + 10, T) if not f["double"] else w1
            job = "Kill with the two extra players before their flag is in" if f["double"] else "Kill with the extra player while their runner is away"
            out.append(_play(M, "flag", "own", A, w0, t1, [], scen, job + ", or their flag does not get in", {},
                             any_of={"more of theirs die at the main fight than of ours": dB(t1) > dA(t1), "their flag does not get in": f["how"] != "captured"}, beside=bes(t1), **kw))      # R-467: staying costs nothing if their flag fails
        elif (ours == "double run") == f["double"]:                      # single against single, double against double
            lv = K.lead(A, end)
            out.append(_play(M, "flag", "own", A, w0, end, who, scen, "Get the flag in, lose no more players than they do, and end no worse than half a flag behind",
                             {"our flag is capped": new["how"] == "captured", "no more of ours die at the main fight than of theirs": dA(end) <= dB(end),
                              "no worse than half a flag behind at the end": lv is None or lv >= -LEAD_HALF}, beside=bes(end), **kw))
        elif ours == "double run":                                        # they single run, we double
            t1 = min(w1 + ANSWER_CAP_S + 5, T)                            # through their cap, and the answer to it
            gn = K.gain(A, w0, t1)
            out.append(_play(M, "flag", "own", A, w0, t1, who, scen, "Gain flag advantage through their next cap, and lose nobody while two are away",
                             {f"flag lead better by {FLAG_GAIN} or more": gn is not None and gn >= FLAG_GAIN, "nobody of ours dies at the main fight": dA(t1) == 0}, beside=bes(t1), **kw))
        else:                                                             # they double run, we single
            lv = K.lead(A, end)
            s0, s1 = M._main_step(A, w0)[0], M._main_step(A, end)[0]
            out.append(_play(M, "flag", "own", A, w0, end, who, scen, "Kill or take ground with the extra player, and end no worse than a flag behind",
                             {"no worse than a flag behind at the end": lv is None or lv >= -LEAD_ONE},
                             any_of={"more of theirs die at the main fight than of ours": dB(end) > dA(end), "ground taken": s0 is not None and s1 is not None and s1 < s0,
                                     "one of their NPCs dies": K.npcs(B, w0, end) > 0}, beside=bes(end), **kw))
    return out


# ---- pushing the flagger (R-427), and the flagger's side (gap 8)
def push_plays(M, K):
    FR, out, role, done = _flag_rows(M), [], M.m.roles, {}
    splits = [x for x in M.attempts() if x["kind"] == "split"]
    for p in M.flag_pushes():
        tm, foe = p["tm"], 3 - p["tm"]
        # a split player on a defender who carries his flag is a split with a part-run (R-430), not a push on a flagger (his mark, TFS v 옷옷옷옷 6:20)
        if any(x["tm"] == tm and x["t_in"] <= p["t"] <= x["t1"] + 4 and set(p["roles"]) <= {q["role"] for q in x["members"]} for x in splits): continue
        f = next((f for f in FR if f["tm"] == foe and p["flagger"] in f["ids"] and f["s0"] - 60 <= p["t"] <= f["e"] + 2), None)
        key = (foe, f["pick"]) if f else (foe, p["t"])
        if key in done:                                                   # a second push on the same flag: one play, everyone who pushed
            q = done[key]
            for r in p["roles"]:
                if r not in q["who"]: q["who"].append(r)
            continue
        usual = _usual_arrival(M, foe)
        arrive = ((f["e"] - f["held_s"]) - f["pick"] + (p["delay_s"] or 0)) if f and f["how"] == "captured" else None
        if arrive is not None and usual is not None and arrive < 0.5 * usual: continue      # not a run from the spawn (a flag taken over near the stand): nothing to hold against the usual run
        stopped = (f is None and (p["died"] or p["dropped"])) or (f is not None and f["how"] != "captured")
        late = arrive is not None and usual is not None and arrive >= LATE_FLAG * usual
        t1 = f["e"] if f else p["t1"]
        n = len(p["roles"])
        scen = f"{M.m.tag[tm]} pushes {M.m.tag[foe]}'s flagger ({p['role']}, {p['doing']}) with {'its main team' if p['main'] else 'one player' if n == 1 else str(n) + ' players'}"
        bes = {"arrival_s": arrive, "usual_s": usual and round(usual), "against_usual": arrive and usual and round(arrive / usual, 2), "flag": f["how"] if f else p["flag"],
               "carrier_died": bool(p["died"]), "pickup_delay_s": p["delay_s"], "flag_lead": [K.lead(tm, p["t"]), K.lead(tm, t1)], "helped": p["helped"]}
        soh = bool(f and f["soh"])                                        # a Shadow of Haste run cannot be held against the usual run: set aside in the counts
        q = _play(M, "push flagger", "own", tm, p["t"], t1, p["roles"], scen, "Stop their flag, or make it 30% late", {},
                  any_of={"their flag is stopped": bool(stopped), "it arrives 30% or more later than usual": bool(late)}, beside=bes, pushers=n, main=bool(p["main"]), soh=soh)
        done[key] = q; out.append(q)
        helped = bool(p["helped"])                                        # the flagger's side: send help, or flag through it
        on_time = f is not None and f["how"] == "captured" and not late
        tests = {"the flag gets in, less than 30% late": on_time}
        if helped: tests["nobody else of ours dies meanwhile"] = K.died(foe, p["t"], t1, ids=set(M.st.players[foe]) - {p["flagger"]}) == 0
        out.append(_play(M, "flagger pushed", "own", foe, p["t"], t1, [p["role"]] + list(p["helped"]),
                         f"{M.m.tag[foe]}'s flagger ({p['role']}) is pushed by {n}; {M.m.tag[foe]} " + ("sends help (" + ", ".join(p["helped"]) + ")" if helped else "flags through it"),
                         "Get the flag in on time" + (", without losing a player for the help sent" if helped else ""), tests, beside=bes, helped=helped, soh=soh))
    return out


# ---- a split, from both sides, phase by phase (R-428 to R-430; Denning's review of 2026-11-13, R-438 to R-446)
def _runs(vals, times, min_s, keep_last=False):
    """Runs of a constant value over the sampled seconds, runs shorter than min_s merged into the longer neighbour:
    [(value, first second, last second)]."""
    runs = []
    for v, t in zip(vals, times):
        if runs and runs[-1][0] == v: runs[-1][2] = t
        else: runs.append([v, t, t])
    while len(runs) > 1:
        cand = range(len(runs) - 1) if keep_last else range(len(runs))       # keep_last: the last run stands however short (the game ended in it)
        i = min(cand, key=lambda i: runs[i][2] - runs[i][1])
        if runs[i][2] - runs[i][1] + SPLIT_STEP >= min_s: break
        near = lambda q: (sum(abs(x - y) for x, y in zip(runs[q][0], runs[i][0])) if isinstance(runs[i][0], tuple) else 0, -(runs[q][2] - runs[q][1]))     # a short stretch joins the neighbour whose numbers are nearest its own, then the longer one
        j = i - 1 if i == len(runs) - 1 else i + 1 if i == 0 else min((i - 1, i + 1), key=near)
        lo, hi = min(i, j), max(i, j)
        runs[lo:hi + 1] = [[runs[j][0], runs[lo][1], runs[hi][2]]]
        k = 0
        while k + 1 < len(runs):                                           # neighbours that are now the same value are one run
            if runs[k][0] == runs[k + 1][0]: runs[k:k + 2] = [[runs[k][0], runs[k][1], runs[k + 1][2]]]
            else: k += 1
    return [tuple(r) for r in runs]


def split_plays(M, K):
    st, m, T, out, tl, S_ = M.st, M.m, M.T, [], M._tl(), SPLIT_STEP
    role, hall = m.roles, M.hall
    A = [x for x in M.attempts() if x["kind"] == "split" and x.get("solo") != "other"]
    is_monk = lambda a: m.A[a].get("p") == "Monk" and not role[a].startswith("Monk ") and "WoC" not in role[a]      # a backline monk; a smiter (the WoC monks, whatever their slot) is damage (R-457; TFS v 옷옷옷옷 4:06)
    for x in A:
        tm, foe, an = x["tm"], 3 - x["tm"], x["answer"]
        own_d = st.side.get(foe)
        frm = {a: int(q["from"]) for a, q in zip(x["ids"], x["members"])}
        to = {a: int(q["to"]) for a, q in zip(x["ids"], x["members"])}
        deep = lambda a, u: M.AL[a][u] and M._deep(a, u - u % S_) is not None
        # a chase is not a split: players following an enemy split out of their own base, who never reach a door (Denning, NwAy v hook 3:04: the split is hook's, chased out, and its Air Ele dies at 3:48)
        # (it sets off while that split is still out and takes no NPC: hdm v 옷옷옷옷 3:46 is a split of its own, after theirs had gone home, and takes an archer; review key s1-26)
        chased = next((y for y in A if y["tm"] == foe and y["t_in"] <= x["t_in"] <= y["t1"] + 4 and x["where"] == "field" and not x["npcs"]
                       and len(set(x["ids"]) & (set(y["answer"]["ids"]) | set(y["answer"].get("went_back_ids") or []))) * 2 >= len(x["ids"])), None)
        if chased is not None: continue
        # follow its players for as long as they stay on the enemy's ground, past the record's own end (the label can change under them: a split that becomes the only players left, or is renamed a push)
        # ... but not once its main team has come to it: then it is a main team push, and the split is over (his marks on Men v Apes: "not a split" from 3:10 to 7:00 and from 8:28 to 11:16, where the record itself had ended "main team joined")
        mates = [b for b in st.players[tm] if b not in x["ids"]]
        joined = lambda a, u: sum(1 for b in mates if M.AL[b][u] and M.P[a][u] and d(M.P[a][u], M.P[b][u]) < FIGHT_LINK) >= 3      # three or more of the rest of his team are with him
        ext = {}
        for a in x["ids"]:
            u, gap = to[a], 0
            while u + S_ <= T and gap <= SPLIT_GAP_S and not joined(a, u + S_):
                u += S_
                gap = 0 if deep(a, u) else gap + S_
            ext[a] = u - gap
        nxt = min((y["t_in"] for y in A if y["tm"] == tm and y["t_in"] > x["t_in"] and set(y["ids"]) & set(x["ids"])), default=T + 1)
        t0, t9 = int(x["t_in"]) - int(x["t_in"]) % S_, min(max(ext.values()), nxt - S_, T)
        times = list(range(t0, t9 + 1, S_))
        if len(times) < 3: continue
        hop = lambda a, u: any(0 <= v - S_ and v <= T and M.P[a][v] and M.P[a][v - S_] and d(M.P[a][v], M.P[a][v - S_]) > GROUND_JUMP for v in (u, u + S_))      # just through a teleporter
        raw = lambda a, u: frm[a] <= u <= ext[a] and deep(a, u) and not hop(a, u)
        def stays(flags, extra=(), to_end=False):         # a player counts once he has been there JOIN_S (R-350: less is support, or passing by), one missed reading allowed; a death in it counts at once; and, for a defender, being there when the game ends (R-459, Book v One 19:28)
            keep, i = [False] * len(flags), 0
            while i < len(flags):
                if not flags[i]: i += 1; continue
                j = i
                while j + 1 < len(flags) and (flags[j + 1] or (j + 2 < len(flags) and flags[j + 2])): j += 1
                if (j - i + 1) * S_ >= JOIN_S or any(times[i] - 2 <= td <= times[j] + 4 for td in extra) or (to_end and j == len(flags) - 1 and times[j] >= T - S_ - 1):
                    for q in range(i, j + 1): keep[q] = True
                i = j + 1
            return keep
        s_on = {a: stays([raw(a, u) for u in times], st.death_times.get(a, [])) for a in x["ids"]}
        on = lambda a, u: s_on[a][(u - t0) // S_] if t0 <= u <= t9 else False
        Ss = [[a for a in x["ids"] if s_on[a][i]] for i in range(len(times))]
        split_deaths = [td for a in x["ids"] for td in st.death_times.get(a, [])]
        def defends(b):                                   # a defender is on the split: within reach of a split player, or further off with one of them hitting or casting on the other (Moments' reading of who is in a fight, without the hold: a player hovering at the edge of reach is not defending, 옷옷옷옷 v Men 6:50); for 12 s, or at a death (his own, or the split player's: R-464)
            def on(a, u):
                dist = d(M.P[b][u], M.P[a][u])
                return dist < FIGHT_LINK or (dist < FIGHT_ACT and ((a, b) if a < b else (b, a)) in M._acting(u, aid=False))
            reach = [bool(M.AL[b][u]) and any(M.AL[a][u] and on(a, u) for a in s) for u, s in zip(times, Ss)]
            return M.visits(times, reach, reach, list(st.death_times.get(b, [])) + split_deaths, to_end=at_end0)      # a defender kites and heals at range: being on the split is enough
        at_end0 = times[-1] >= T - S_ - 1
        d_on = {b: defends(b) for b in st.players[foe]}
        Ds = [[b for b in st.players[foe] if d_on[b][i]] for i in range(len(times))]
        smooth = lambda xs: [sorted(xs[max(i - 2, 0):i + 3])[len(xs[max(i - 2, 0):i + 3]) // 2] for i in range(len(xs))]
        kn = list(zip(smooth([len(s) for s in Ss]), smooth([len(dn) for dn in Ds])))
        # it counts from when it can do something: at their footies, in their base or pit, or met by a defender (Denning, Book v One 18:54: "when the split actually reaches base/NPCs")
        reach = next((u for u, s, dn in zip(times, Ss, Ds) if dn or any(M.place_at(a, u)[0] in ("pit", "base", "front footies", "back footies") for a in s)), None)
        if reach is None: continue
        # the players chasing it out afterwards: a death on the way out with a defender still on him is the split's (R-363), for as long as the chase lasts
        lastD = set(b for dn in Ds[-6:] for b in dn)
        end_chase = t9
        for u in range(t9 + S_, min(t9 + 60, T) + 1, S_):
            if any(M.AL[a][u] and M.AL[b][u] and d(M.P[a][u], M.P[b][u]) < FIGHT_LINK for a in x["ids"] for b in lastD): end_chase = u
            elif u - end_chase > 6: break
        npc_ev = []                                                        # the NPCs it took, each with when and whether it was a pit NPC: only those its own players stood by (R-442)
        for z, td in st.npc_dead.items():
            v = st.geo.npcs.get(z)
            if not v or v.get("team") != foe or v.get("kind") in ("guild_lord", "footman") or not (t0 <= td <= t9 + 4): continue
            u = min(max(int(td), 0), T)
            near = [a for a in x["ids"] if frm[a] <= u <= ext[a] + 4 and M.P[a][u] and (d(M.P[a][u], v["pos"]) < NPC_NEAR if v.get("pos") else M.place_at(a, u)[0] in ("pit", "base"))]
            if near: npc_ev.append((td, v["kind"], bool(v.get("pit"))))
        for td in M.foot_dead.get(foe, ()):
            u = min(max(int(td), 0), T)
            if t0 <= td <= t9 + 4 and any(frm[a] <= u <= ext[a] + 4 and M.AL[a][u] and str(M._deep(a, u - u % S_) or "").endswith("footies") for a in x["ids"]): npc_ev.append((td, "footman", False))
        def there(a, td):                                 # he died on the split: on their ground just before, or on the way out with a defender still on him (not back at his own main fight: 옷옷옷옷 v Men 15:28)
            u = min(max(int(td) - 1, 0), T)
            return any(on(a, v // S_ * S_) for v in (u, max(u - 2, 0), max(u - 4, 0))) or (t9 < td <= end_chase + 2 and any(M.AL[b][u] and M.P[a][u] and d(M.P[a][u], M.P[b][u]) < FIGHT_LINK for b in lastD))
        dA = sorted((td, a) for a in x["ids"] for td in st.death_times.get(a, []) if frm[a] - 1 <= td <= max(ext[a], end_chase) + 4 and there(a, td))
        dD = sorted((td, b) for b in st.players[foe] for td in st.death_times.get(b, [])
                    if t0 <= td <= t9 + 4 and M.P[b][min(max(int(td) - 1, 0), T)] and any(on(a, min(max(int(td) - 1, 0), T) // S_ * S_) and d(M.P[b][min(max(int(td) - 1, 0), T)], M.P[a][min(max(int(td) - 1, 0), T)]) < FIGHT_LINK for a in x["ids"]))
        at_end = times[-1] >= T - S_ - 1                                   # the game ended with the split still out: its last phase stands however short (R-459)
        phases = [(v, max(a_, reach), b_) for v, a_, b_ in _runs(kn, times, JOIN_S, keep_last=at_end) if v[0] > 0 and b_ >= reach and (b_ - max(a_, reach) + S_ >= JOIN_S or (at_end and b_ == times[-1]))]
        wb = set(an.get("went_back_ids") or [])
        prevD, base = set(), f"{m.tag[tm]}'s split by the {x['way'] or 'door'}"
        for pi, ((k, n), p0, p1) in enumerate(phases):
            last = pi == len(phases) - 1
            idx = [i for i, u in enumerate(times) if p0 <= u <= p1]
            cs, cd = collections.Counter(a for i in idx for a in Ss[i]), collections.Counter(b for i in idx for b in Ds[i])
            Sp, Dp = [a for a, _ in cs.most_common(k)], [b for b, _ in cd.most_common(n)]
            e1 = min(p1 + 4, T)
            # a death that made the numbers of this phase belongs to the phase before it (his mark, hdm v hook 7:52: "they are only 4 v 3 because they killed a defender"): at its first seconds only the deaths of players counted in it are its own
            lostp = [a for td, a in dA if p0 - 1 <= td <= (max(e1, end_chase + 2) if last else e1) and (pi == 0 or td > p0 + 4 or a in Sp)]
            killp = [b for td, b in dD if p0 - 1 <= td <= e1 and (pi == 0 or td > p0 + 4 or b in Dp)]
            npcs = [(kind, pit) for td, kind, pit in npc_ev if p0 - 1 <= td <= e1]
            n_lost, n_kill, n_npc, n_pit = len(lostp), len(killp), len(npcs), sum(1 for _, pit in npcs if pit)
            away_a, away_d = K.died(tm, p0, e1) - sum(1 for td, a in dA if p0 < td <= e1), K.died(foe, p0, e1) - sum(1 for td, b in dD if p0 < td <= e1)
            ga, gd = K.gain(tm, p0, e1), K.gain(foe, p0, e1)
            ms, md = sum(map(is_monk, Sp)), sum(map(is_monk, Dp))          # monks the split brought, monks defending it
            dmg_s, dmg_d = k - ms, n - md
            mid = (p0 + p1) // 2 // S_ * S_
            ma, mdn = set(tl[mid][tm]["ids"]) - set(Sp), set(tl[mid][foe]["ids"]) - set(Dp)
            main = {"own": [len(ma) - sum(map(is_monk, ma)), sum(map(is_monk, ma))], "theirs": [len(mdn) - sum(map(is_monk, mdn)), sum(map(is_monk, mdn))]}      # [damage, monks] of each main team's fight, the split and its defenders left out
            kills = can_kill(dmg_s, md)                                    # damage against the monks defending (R-457: 2+ against one, 4+ against two, 5+ against three; three are not expected to kill two)
            main_can = [can_kill(main["own"][0], main["theirs"][1]), can_kill(main["theirs"][0], main["own"][1])]      # at the main fight, each side's damage against the other's monks
            no_monk = [main["theirs"][1] == 0, main["own"][1] == 0]         # the other side has no backline monk at the main fight
            main_kills = main_can[0] and (not main_can[1] or no_monk[0])    # the job to kill goes to a side that meets its ratio while the other does not (R-457), and always to a side facing no monk (R-462: ohno v Fun 11:10)
            main_killed = main_can[1] and (not main_can[0] or no_monk[1])
            # a collapse (R-429, R-441): players come from their main fight, the defence becomes at least one more than the split, and they go back
            new = [b for b in Dp if b not in prevD]
            def from_main(b):                             # he stood with his main team, away from home, in the 45 s before he arrived
                for u in range(max(p0 - 45, 0) // S_ * S_, max(p0 - JOIN_S, 0) + 1, S_):
                    if M.AL[b][u] and b in M.main_team(foe, u) and len(M.main_team(foe, u)) >= 3 and not (M.place_at(b, u)[1] == own_d and M.place_at(b, u)[0] in HOMEG): return True
                return False
            came = [b for b in new if from_main(b)]
            short = p1 - p0 <= COLLAPSE_VISIT_S
            alive_d = sum(M.AL[b][mid] for b in st.players[foe])
            full = (n >= max(6, alive_d - 1) and k < n) or (len(wb) >= 5 and an.get("went_back_t") is not None and p0 - 10 <= an["went_back_t"] <= p1)
            collapse = bool(came) and n >= k + 1 and short and pi > 0 and not full
            whoA, whoD = [role[a] for a in Sp], [role[b] for b in Dp]
            size = {1: "one player", 2: "two players", 3: "three players"}.get(k, f"{k} players")
            scen_a = f"{base}: {size} ({', '.join(whoA)}) against {n} defending" + (f" ({', '.join(whoD)})" if n else "")
            besA = {"npcs_taken": [kind for kind, _ in npcs], "kills": [role[b] for b in killp], "lost": [role[a] for a in lostp], "flag_lead": [K.lead(tm, p0), K.lead(tm, e1)], "deaths_away_from_the_split": [away_a, away_d],
                    "split": [dmg_s, ms], "defence": [dmg_d, md], "main": main, "main_can_kill": main_can, "reached": reach, "phase": [pi + 1, len(phases)], "chased_until": end_chase if last and end_chase > t9 else None}
            besD = {"pit_npcs_lost": [kind for kind, pit in npcs if pit], "other_npcs_lost": [kind for kind, pit in npcs if not pit], "lost": [role[b] for b in killp], "split_killed": [role[a] for a in lostp],
                    "flag_lead": [K.lead(foe, p0), K.lead(foe, e1)], "deaths_away_from_the_split": [away_d, away_a], "split": [dmg_s, ms], "defence": [dmg_d, md], "main": {"own": main["theirs"], "theirs": main["own"]}, "main_can_kill": main_can[::-1], "phase": [pi + 1, len(phases)]}
            elsewhere = {"more of theirs die away from the split than of ours": away_d > away_a, f"flag lead better by {FLAG_GAIN} or more": ga is not None and ga >= FLAG_GAIN}
            kill_or_npc = {"a defender killed": n_kill > 0, "an NPC taken": n_npc > 0}
            kw = dict(size=k, defenders=n, split_damage=dmg_s, defending_monks=md)
            # the attacker's job, set by the answer it meets (R-428)
            if full or collapse:
                ans = "met by a full collapse" if full else "collapsed on"
                out.append(_play(M, "split", "attacker", tm, p0, e1, whoA, scen_a + ("; the whole team turns on it" if full else f"; {', '.join(role[b] for b in came)} collapse from the main fight"),
                                 "Survive and gain an advantage elsewhere on the map", {"nobody on the split dies": n_lost == 0}, any_of=elsewhere, beside=besA, answer=ans, **kw))
            elif n == 0: out.append(_play(M, "split", "attacker", tm, p0, e1, whoA, scen_a, "Take NPCs", {"an NPC taken": n_npc > 0}, beside=besA, answer="undefended", **kw))
            elif k < n: out.append(_play(M, "split", "attacker", tm, p0, e1, whoA, scen_a, "Survive and gain an advantage elsewhere on the map", {"nobody on the split dies": n_lost == 0}, any_of=elsewhere, beside=besA, answer="a player or more down", **kw))
            elif k == 1 and n == 1 and md == 1: out.append(_play(M, "split", "attacker", tm, p0, e1, whoA, scen_a, "Hold the monk there; the main team's job is to kill", {"the split player survives": n_lost == 0}, beside=besA, answer="1 v 1, defended by a monk", **kw))
            elif kills: out.append(_play(M, "split", "attacker", tm, p0, e1, whoA, scen_a, "Kill or take NPCs" if k > n else "Take NPCs or kills", {}, any_of=kill_or_npc, beside=besA,
                                            answer="1 v 1, the defender not a monk" if k == 1 else "a player or more up" if k > n else "even", **kw))
            else: out.append(_play(M, "split", "attacker", tm, p0, e1, whoA, scen_a + f"; {dmg_s} damage against {md} monks", "Hold the monks there and lose nobody; NPCs are a bonus (a kill is not expected of it)",
                                   {"nobody on the split dies": n_lost == 0}, beside=besA, ruled=False, answer="held by monks", **kw))
            at_main = lambda own, theirs: f"; at the main fight {main[own][0]} damage against {main[theirs][1]} monk{'s' if main[theirs][1] != 1 else ''}, and theirs {main[theirs][0]} against {main[own][1]}"
            if not (full or collapse) and n and main_kills:
                out.append(_play(M, "split", "attacker's main team", tm, p0, e1, [], scen_a + at_main("own", "theirs"),
                                 "Kill at the main fight: " + ("they have no monk there" if no_monk[0] else "its damage can kill against their monks there, and theirs cannot"), {"more of theirs die away from the split than of ours": away_d > away_a}, beside=besA, answer="the main fight can kill", **kw))
            # the defender's side
            scen_d = f"{m.tag[foe]} against {base}: {n} ({', '.join(whoD)}) against {size}" if n else f"{m.tag[foe]} against {base}: nobody against {size}"
            pit_ok = {"no pit NPC lost": n_pit == 0}
            if full:
                out.append(_play(M, "split", "defender", foe, p0, e1, whoD, scen_d + ": full collapse", "Kill the split or drive it out (the flags it costs are beside it)", {},
                                 any_of={"a split player dies": n_lost > 0, "the split is gone within the visit": last and short}, beside=besD, call="full collapse", **kw))
            elif collapse:
                rows = [tl[u][foe]["main"] for u in range(p0, p1 + 1, S_) if tl[u][foe]["main"]]
                out.append(_play(M, "split", "defender", foe, p0, e1, [role[b] for b in came], scen_d + f": collapse by {', '.join(role[b] for b in came)} from the main fight",
                                 "Kill a split player before going back (what it cost at the main fight and in flags is beside it)", {"a split player dies during the collapse": n_lost > 0},
                                 beside=dict(besD, visit_s=p1 - p0, main_net=sum(r[0] - r[1] for r in rows) * S_), call="collapse", **kw))
            elif n == 0:
                out.append(_play(M, "split", "defender", foe, p0, e1, [], scen_d, "Win elsewhere before the split costs more than it gains", {},
                                 any_of={"more of theirs die away from the split than of ours": away_a > away_d, f"flag lead better by {FLAG_GAIN} or more": gd is not None and gd >= FLAG_GAIN}, beside=besD, ruled=False, call="no answer", **kw))
            elif n < k:
                out.append(_play(M, "split", "defender", foe, p0, e1, whoD, scen_d, "Delay: keep the split off the pit NPCs and stay alive", dict(pit_ok, **{"no defender dies": n_kill == 0}), beside=besD, call="one defender" if n == 1 else "a player down", **kw))
            elif n == k:
                out.append(_play(M, "split", "defender", foe, p0, e1, whoD, scen_d, "Hold it even: lose no pit NPC and no more players than the split does", dict(pit_ok, **{"no more defenders die than split players": n_kill <= n_lost}), beside=besD, call="mirror", **kw))
            else:
                out.append(_play(M, "split", "defender", foe, p0, e1, whoD, scen_d, "Kill it or drive it out with the extra player, and lose no pit NPC for it", pit_ok,
                                 any_of={"a split player dies": n_lost > 0, "the split is gone within the visit": last and short}, beside=besD, call="add one", **kw))
            if not (full or collapse) and n and main_killed:               # the same job from the defenders' side (R-457)
                out.append(_play(M, "split", "defender's main team", foe, p0, e1, [], scen_d + at_main("theirs", "own"),
                                 "Kill at the main fight: " + ("they have no monk there" if no_monk[1] else "its damage can kill against their monks there, and theirs cannot"), {"more of theirs die away from the split than of ours": away_a > away_d}, beside=besD, call="the main fight can kill", **kw))
            if k == 1 and n == 1 and not collapse:                         # a lone defender part-running his flag (R-430)
                b = Dp[0]
                carried = sum(S_ for u in range(max(p0 - JOIN_S, 0), p1 + 1, S_) if M.carrying(b, u))      # from when he got there: he counts as the defender only JOIN_S later (review key s1-28)
                if carried >= 6:
                    out.append(_play(M, "split", "defender", foe, p0, e1, [role[b]], scen_d + f": the lone defender carries his flag for {carried} s", "Gain a slight flag advantage while losing no pit NPC and not dying",
                                     dict(pit_ok, **{f"flag lead better by {PART_RUN_GAIN} or more": gd is not None and gd >= PART_RUN_GAIN, "the defender does not die": n_kill == 0}), beside=dict(besD, carried_s=carried), call="part-run", **kw))
            prevD = set(Dp)
    return out


# ---- a numbers difference in the main team's fight (R-431, gaps 4, 5 and 7)
def numbers_plays(M, K, trig, recs, pinned_at):
    out, T, st = [], M.T, M.st
    f1 = collections.defaultdict(list)
    for x in recs:
        if x["family"] == 1: f1[x["tm"]].append(x["t"])
    for g, x in zip(trig, recs):
        if x["family"] != 3: continue
        tm, foe, t, e = x["tm"], 3 - x["tm"], x["t"], g["refs"][0]
        side, src, c = x["scenario"]["parts"]["side"], x["scenario"]["parts"]["source"], x["call"]["key"]
        if src == "runner away" and any(abs(u - t) <= READ_TO for u in f1[tm]):
            x["merged"] = "the flag decision"                             # R-431: the consequence of the flag decision, not a second one
            continue
        if pinned_at(tm, t): continue
        end = min(e["last"] + NUMBERS_TAIL_S, T)
        dA, dB = (lambda b: K.died(tm, t, b)), (lambda b: K.died(foe, t, b))
        scen = x["scenario"]["label"] + f"; {x['team']}: {x['call']['label'].lower()}"
        bes = lambda b: {"deaths": [dA(b), dB(b)], "npcs": [K.npcs(tm, t, b), K.npcs(foe, t, b)], "flag_lead": [K.lead(tm, t), K.lead(tm, b)], "lasted_s": e["last"] - e["start"]}
        back, push = c in ("retreat down the ladder", "fall out"), c in ("push up", "push in", "push their flagger")
        monk = lambda a: M.m.A[a].get("p") == "Monk" and not M.m.roles[a].startswith("Monk ") and "WoC" not in M.m.roles[a]
        dmg_own, monks_their = sum(1 for a in e["ids"][tm] if not monk(a)), sum(1 for a in e["ids"][foe] if monk(a))
        kill_on = can_kill(dmg_own, monks_their)                          # R-457 in the main fight too (his marks, hdm v hook 4:12, 6:52: "2 damage v 2 monks again")
        kw = dict(source=src, numbers_side=side, call=c, numbers=x["scenario"]["parts"]["numbers"])
        if src == "wipe" or (src == "kills" and side == "up" and x["scenario"]["parts"].get("step", 0) <= -2 and x["scenario"]["parts"]["short_because"].get("kills", 0) >= 3):
            if side != "up": continue                                     # gap 4: after a wipe, or kills at their base
            res = min(st.next_res(t) + 5, T)
            c = M.centre([a for a in M.main_team(tm, t - t % SPLIT_STEP) if M.AL[a][t]], t)
            walk = M.hall.walk(c, M.hall.lord[st.side.get(foe)]) if c else None
            need = (walk / RUN_SPEED if walk else 0) + AFTER_WIPE_MIN_S        # the walk to their pit, and time to kill something there (R-445: "they can't really take NPCs from where they were in 12 s")
            if x["state"]["res_in"] < need:
                B = st.next_res(t)
                out.append(_play(M, "numbers", "after a wipe", tm, t, min(B + 30, T), [], scen + f"; their base res is {x['state']['res_in']} s away and their pit about {round(need - AFTER_WIPE_MIN_S)} s",
                                 "Too late for NPCs: be out, or set for the fight, when they res", {"nobody of ours dies in the 30 s after the res": K.died(tm, B, B + 30) == 0},
                                 beside=dict(bes(min(B + 30, T)), res_in=x["state"]["res_in"], pit_walk_s=round(need - AFTER_WIPE_MIN_S)), call2="too late for NPCs", **kw))
            else:
                out.append(_play(M, "numbers", "after a wipe", tm, t, res, [], scen, "Take pit NPCs before their base res", {"one of their pit NPCs dies before the res": K.npcs(foe, t, res, pit=True) > 0},
                                 beside=dict(bes(res), res_in=x["state"]["res_in"], pit_walk_s=round(need - AFTER_WIPE_MIN_S)), call2="time for NPCs", **kw))
        elif src == "split elsewhere" and side == "up" and not kill_on:
            out.append(_play(M, "numbers", "strong side", tm, t, end, [], scen + f"; {dmg_own} damage against {monks_their} monk{'s' if monks_their != 1 else ''}", "Keep them busy and lose nobody (a kill is not expected of it)", {"nobody of ours dies": dA(end) == 0}, beside=bes(end), ruled=False, **kw))
        elif src == "split elsewhere":                                    # gap 7: judge each group by its job
            if side == "up": out.append(_play(M, "numbers", "strong side", tm, t, end, [], scen, "Kill with the numbers while their players are away", {"more of theirs die than of ours": dB(end) > dA(end)}, beside=bes(end), **kw))
            else: out.append(_play(M, "numbers", "weak side", tm, t, end, [], scen, "No deaths, keep them busy, do not chase", {"nobody of ours dies": dA(end) == 0}, beside=bes(end), **kw))
        elif side == "up":
            if back: out.append(_play(M, "numbers", "up", tm, t, end, [], scen, "Reset without giving anything back", {"nobody of ours dies": dA(end) == 0, "no NPC lost": K.npcs(tm, t, end) == 0}, beside=bes(end), ruled=False, **kw))
            elif push or c == "split": out.append(_play(M, "numbers", "up", tm, t, end, [], scen, "Take ground and NPCs with the numbers", {"no more of ours die than of theirs": dA(end) <= dB(end)},
                                                        any_of={"one of their NPCs dies": K.npcs(foe, t, end) > 0, "more of theirs die than of ours": dB(end) > dA(end)}, beside=bes(end), ruled=False, **kw))
            else: out.append(_play(M, "numbers", "up", tm, t, end, [], scen, "Turn the extra player into a kill before the numbers are level", {"more of theirs die than of ours": dB(end) > dA(end)}, beside=bes(end), **kw))
        else:
            if src == "kills": end = min(end, st.next_res(t) + NUMBERS_TAIL_S, T)        # gap 5: a team with dead players waits for the res
            if back: out.append(_play(M, "numbers", "down", tm, t, end, [], scen, "Reach cover a player down without losing another", {"nobody of ours dies": dA(end) == 0, "no NPC lost": K.npcs(tm, t, end) == 0}, beside=bes(end), ruled=False, **kw))
            elif push or c == "split": out.append(_play(M, "numbers", "down", tm, t, end, [], scen, "Trade a player down: take something on their ground for it", {},
                                                        any_of={"one of their NPCs dies": K.npcs(foe, t, end) > 0, "more of theirs die than of ours": dB(end) > dA(end)}, beside=bes(end), ruled=False, **kw))
            else: out.append(_play(M, "numbers", "down", tm, t, end, [], scen, "Hold the ground a player down and lose no more until it is level, or the base res", {"nobody of ours dies": dA(end) == 0}, beside=bes(end), ruled=False, **kw))
    return out


# ---- their boost is coming (gap 2)
def boost_plays(M, K, recs, pinned_at):
    out, T = [], M.T
    for x in recs:
        if x["family"] != 1 or "boost" not in x["triggers"] or pinned_at(x["tm"], x["t"]): continue
        tm, foe, t = x["tm"], 3 - x["tm"], x["t"]
        lands = t + BOOST_WARN_S
        ran = (x["call"].get("runners") or 0) >= 1 or x["state"]["own_flag"]
        t1 = min(lands + 5, T)
        denied = not any(h == foe and t < u <= t1 for u, h in M._boosts())
        bes = {"boost_worth": x["state"]["enemy_boost"], "denied": denied, "deaths": [K.died(tm, t, t1 + 10), K.died(foe, t, t1 + 10)], "flag_lead": [K.lead(tm, t), K.lead(tm, t1)]}
        scen = f"{M.m.tag[foe]}'s boost is {BOOST_WARN_S} s away; {x['team']}: {x['call']['label'].lower()}"
        if ran: out.append(_play(M, "boost", "own", tm, t, t1, x["call"]["shape"]["who"], scen, "Deny their boost", {"their boost does not land": denied}, beside=bes, call="run"))
        else: out.append(_play(M, "boost", "own", tm, t, min(t1 + 10, T), [], scen, "Concede the boost for kills", {"more of theirs die than of ours": bes["deaths"][1] > bes["deaths"][0]}, beside=bes, call="concede"))
    return out


# ---- pinned in the base or pit (gap 1)
def pinned(M):
    """Stretches of PINNED_S or longer in which a team's main team stands in its own base or pit while the enemy's
    main team stands on that team's ground (its doors, base or pit): [(team, from, to)], read every 4 s."""
    if getattr(M, "_pinned", None) is not None: return M._pinned
    out, S = [], 4
    for tm in M.st.teams:
        cur = None
        for t in range(0, M.T + 1, S):
            a, b = M._main_step(tm, t)[0], M._main_step(3 - tm, t)[0]
            on = a is not None and b is not None and a >= 3 and b <= -2
            if on and cur and t - cur[2] <= S: cur[2] = t
            else:
                if cur and cur[2] - cur[1] >= PINNED_S: out.append(tuple(cur))
                cur = [tm, t, t] if on else None
        if cur and cur[2] - cur[1] >= PINNED_S: out.append(tuple(cur))
    M._pinned = out
    return out


def pinned_plays(M, K):
    out, T, st = [], M.T, M.st
    def out_of_base(tm, a, b):
        own = st.side.get(tm)
        for u in range(a - a % 2, b + 1, 2):
            live = [x for x in st.players[tm] if M.AL[x][u]]
            away = [x for x in live if not (M.place_at(x, u)[1] == own and M.place_at(x, u)[0] in ("pit", "base"))]
            if len(away) >= 4 and len(away) * 2 >= len(live): return True
        return False
    for tm, a, b in pinned(M):
        t = a
        while t < b:                                                      # one play to each base res while it lasts
            dead = sum(1 for x in st.players[tm] if not M.AL[x][min(t, T)])
            t1 = min(st.next_res(t), b + 4, T) if dead else min(b + 4, T)      # with nobody dead there is no res to hold out for: one play for as long as it is held in (his mark, hdm v hook 12:00)
            if t1 - t >= 10:
                s1 = M._main_step(tm, min(t1 + 10, T))[0]
                alive = sum(M.AL[x][min(t1 + 10, T)] for x in st.players[tm])
                hold = {"no pit NPC lost and nobody dies until the base res": K.npcs(tm, t, t1, pit=True) == 0 and K.died(tm, t, t1) == 0,
                        "it breaks out (half its living players or more, four at least, out of its base and pit)": out_of_base(tm, t, min(t1 + 10, T))}      # by any door: four or five out by the back door is a break-out (his mark, TFS v 옷옷옷옷 0:36)
                out.append(_play(M, "pinned", "own", tm, t, t1, [], f"{M.m.tag[tm]} is held in its own base or pit by {M.m.tag[3 - tm]}'s main team ({st.pit_npcs(tm, t)} alive; base res in {round(st.next_res(t) - t)} s)",
                                 "Hold the NPCs and lose nobody until the base res, or break out" if dead else "Lose no player and no NPC while held in, or break out", {}, any_of=hold,
                                 beside={"deaths": [K.died(tm, t, t1), K.died(3 - tm, t, t1)], "pit_npcs_lost": K.npcs(tm, t, t1, pit=True), "pinned_s": b - a}))
            t = st.next_res(t) if dead else b
    return out


# ---- in their base as their dead come back (gap 5)
def res_plays(M, K):
    out, T = [], M.T
    for r in M.caught():
        B, tm = r["t"], r["tm"]
        out.append(_play(M, "base res", "own", tm, B - 20, B + 30, [], f"{r['team']} has {r['attackers']} in {M.m.tag[3 - tm]}'s base at the base res ({r['defenders']} defending, {r['coming_back']} coming back): {r['stayed']} stay",
                         "Be out, or set for the fight, when they res", {"nobody of ours dies in the 30 s after the res": K.died(tm, B, B + 30) == 0}, beside={"deaths_after": K.died(tm, B, B + 30), "outnumbered": r["outnumbered"]}, call="stayed through the res"))
    for r in M.timing():
        if r["kind"] != "left before res": continue
        B, tm = r["t"] + r["s"], r["tm"]
        out.append(_play(M, "base res", "own", tm, r["t"], B + 30, r["who"], f"{r['team']} leaves {r['foe']}'s base {r['s']} s before the base res ({r['coming_back']} coming back)",
                         "Be out, or set for the fight, when they res", {"nobody of ours dies in the 30 s after the res": K.died(tm, B, B + 30) == 0}, beside={"deaths_after": K.died(tm, B, B + 30)}, call="left before the res"))
    return out


# ---- the Lord push, from LORD_PUSH_FROM (R-435)
def lord_plays(M, K):
    st, m, T, out = M.st, M.m, M.T, []
    res = m.o["meta"].get("result") or {}
    won = res.get("winning_team_id")
    dead = {tm: next((r[0] / 10 for r in m.o["ev"] if r[1] == "dt" and isinstance(r[2], int) and r[2] < len(m.A) and m.A[r[2]].get("npc") == "guild_lord" and m.A[r[2]].get("team") == tm), None) for tm in st.teams}
    taken = {l["team"]: l.get("taken") for l in m.o.get("lords", [])}          # gvg.report's own Lord damage total for the match
    how = "a Lord kill" if any(v is not None for v in dead.values()) else ("Lord damage at 28:00" if T >= 1670 else "the match ending early")
    for r in M.on_lord():
        tm, foe = r["tm"], 3 - r["tm"]
        t0, t1 = int(r["t"]), int(r["t1"])
        if t1 < LORD_PUSH_FROM or t0 < LORD_PUSH_FROM - 30 or t1 - t0 < 6 or M.hall is None: continue
        t0 = max(t0, 0); fs = st.side.get(foe)
        lp = M.hall.lord[fs]
        att, dfn = [], []                                # who is in their base: on their ground (not out in the field) within LORD_BASE_R of the Lord; the defenders in their own base or pit (R-446: he counts the players in the base, not only those next to the Lord)
        for u in range(max(t0 - 6, 0) // SPLIT_STEP * SPLIT_STEP, min(t1, T) + 1, SPLIT_STEP):
            att.append(frozenset(a for a in st.players[tm] if M.AL[a][u] and M.place_at(a, u)[1] == fs and M.place_at(a, u)[0] != "field" and d(M.P[a][u], lp) <= LORD_BASE_R))
            dfn.append(frozenset(b for b in st.players[foe] if M.AL[b][u] and M.place_at(b, u)[1] == fs and M.place_at(b, u)[0] in ("pit", "base")))
        def held(sets):                                  # the most that were there together for 8 s or more, who they were, and how many at the end
            n = max((c for c in range(8, 0, -1) if sum(1 for g in sets if len(g) >= c) >= 4), default=max((len(g) for g in sets), default=0))
            who = collections.Counter(a for g in sets if len(g) >= n for a in g)
            return n, [a for a, _ in who.most_common(n)], len(sets[-1]) if sets else 0
        (n, ids_a, n_end), (nd, ids_d, nd_end) = held(att), held(dfn)
        monks, dmonks = M._mk(ids_a), M._mk(ids_d)
        pit = sum(1 for a, v in st.geo.npcs.items() if v["team"] == foe and v.get("pit") and v["kind"] != "guild_lord" and st.npc_dead.get(a, 1e9) > t0)
        rel = "more attackers than pit NPCs" if n > pit else "as many attackers as pit NPCs" if n == pit else "fewer attackers than pit NPCs"
        ids = set(r["ids"])
        on_lord = sum(1 for u, a, _ in M.lord_hits.get(foe, ()) if t0 <= u <= t1)
        on_players = sum(1 for u in range(t0, min(t1, T) + 1) for a, b in M.hits.get(u, ()) if a in st.players[tm] and d(M.P[a][u], lp) <= LORD_BASE_R)
        aim = "Lord damage" if on_lord >= on_players else "killing the defenders"
        dmg = round(sum(v for u, _, v in M.lord_hits.get(foe, ()) if t0 <= u <= t1))
        own = round(sum(v for u, _, v in M.lord_hits.get(tm, ()) if t0 <= u <= t1))
        bes = {"attackers": n, "attackers_at_the_end": n_end, "pit_npcs": pit, "monks_with_the_push": monks, "aim": aim, "lord_damage": dmg, "own_lord_damage_meanwhile": own, "defenders": nd, "defenders_at_the_end": nd_end, "defender_monks": dmonks,
               "deaths": [K.died(tm, t0, t1 + 5), K.died(foe, t0, t1 + 5)], "match_decided_by": how, "match_lord_damage_gvg_report": [taken.get(foe), taken.get(tm)],
               "lord_killed_in_it": dead[foe] is not None and t0 <= dead[foe] <= t1 + 5}
        then = lambda a_, b_: "" if a_ == b_ else f", {b_} by the end"
        out.append(_play(M, "lord", "attacker", tm, t0, t1, [m.roles[a] for a in ids_a], f"{M.m.tag[tm]} pushes {M.m.tag[foe]}'s Guild Lord with {n} in the base ({monks} monk{'s' if monks != 1 else ''}{then(n, n_end)}) against {pit} pit NPCs: {rel}; playing for {aim}",
                         "Most Lord damage, or the kill, while keeping the own Lord up (the result is the match)", {"the match is won": won == tm}, beside=bes, relation=rel, monks=monks, aim=aim, attackers=n, pit=pit))
        out.append(_play(M, "lord", "defender", foe, t0, t1, [m.roles[b] for b in ids_d], f"{M.m.tag[foe]} defends its Guild Lord with {nd} ({dmonks} monk{'s' if dmonks != 1 else ''}{then(nd, nd_end)}) against {n}{then(n, n_end)}",
                         "Do not die, keep Lord damage down, keep the Lord alive (the result is the match)", {"the match is won": won == foe}, beside=bes, defenders=nd, monks=dmonks))
    return out


def plays(M, recs=None):
    """Every play of the match with its job, in time order."""
    if M.hall is None: return []
    recs = recs if recs is not None else M.records()
    K = _K(M)
    P = pinned(M)
    pinned_at = lambda tm, t: any(k == tm and a <= t <= b for k, a, b in P)
    out = flag_plays(M, K, pinned_at) + push_plays(M, K) + split_plays(M, K) + numbers_plays(M, K, M.triggers(), recs, pinned_at) + boost_plays(M, K, recs, pinned_at) + pinned_plays(M, K) + res_plays(M, K) + lord_plays(M, K)
    out.sort(key=lambda p: (p["t0"], p["tm"], p["play"]))
    rid = M.m.o["meta"]["id"]
    for i, p in enumerate(out): p["rid"], p["id"] = rid, f"{rid[:8]}-{p['play'].replace(' ', '_')}-{p['tm']}-{p['t0']}-{i}"
    allocation(recs, out, pinned_at)
    return out


def allocation(recs, plays_, pinned_at=None):
    """The call as an allocation (R-425): each moment gets the plays its team began from 10 s before it to the end
    of the read window, as (play, side, who), and each play the moment of its team nearest its start."""
    by = collections.defaultdict(list)
    for p in plays_: by[p["tm"]].append(p)
    for x in recs:
        x["alloc"] = [{"play": p["play"], "side": p["side"], "who": p["who"], "id": p["id"]} for p in by[x["tm"]] if x["t"] - 10 <= p["t0"] <= x["t"] + READ_TO]
        if pinned_at is not None: x["pinned"] = bool(pinned_at(x["tm"], x["t"]))
    for p in plays_:
        near = [x for x in recs if x["tm"] == p["tm"] and abs(x["t"] - p["t0"]) <= READ_TO and not x.get("merged")]
        p["moment"] = min(near, key=lambda x: abs(x["t"] - p["t0"]))["id"] if near else None


def bench_rows(M):
    """One row a flag that was run, for the usual arrival time by hall and side (bench): how it ended, its form, the
    side, whether it was pushed, and the seconds from the pickup to arriving at the stand."""
    pushed = [(3 - p["tm"], p["flagger"], p["t"], p["t1"]) for p in M.flag_pushes()]
    return [{"how": f["how"], "form": f["form"], "side": M.st.side.get(f["tm"]), "arrive": (f["e"] - f["held_s"]) - f["pick"], "soh": f["soh"],
             "pushed": any(tm == f["tm"] and a in f["ids"] and f["s0"] - 60 <= t <= f["e"] + 2 for tm, a, t, _ in pushed)} for f in _flag_rows(M)]


# ---- reports
def clock(t): return f"{int(t) // 60}:{int(t) % 60:02d}"


def summary(path):
    D = json.load(open(path)); P = D["plays"]
    print(len(P), "plays in", len(D["matches"]), "matches;", sum(1 for p in P if p["moment"]), "with a decision moment of the team within", READ_TO, "s")
    R = D["records"]
    print("moments:", len(R), "; merged into the flag decision (R-431):", sum(1 for x in R if x.get("merged")), "; read while pinned:", sum(1 for x in R if x.get("pinned")))
    for verb in ("push flagger", "split", "flag"):
        print(f"  moments whose allocation holds a '{verb}' play:", sum(1 for x in R if any(a["play"] == verb for a in x.get("alloc", []))))
    def key(p):
        if p["play"] == "flag": return f"they {p['their']}, we {p['ours']}"
        if p["play"] == "split": return f"{p['side']}: {p.get('answer') or p.get('call')}".split(" (")[0]
        if p["play"] == "numbers": return f"{p['side']} ({p['source']}): {p['job']}"
        if p["play"] == "lord": return f"{p['side']}: {p.get('relation', '')}" + (f", {min(p['monks'], 3)} monk(s)" if p["side"] == "attacker" else "")
        if p["play"] == "push flagger": return "by its main team" if p["main"] else "by one player" if p["pushers"] == 1 else "by two or more"
        if p["play"] == "numbers" and p["side"] == "after a wipe": return "after a wipe: " + p.get("call2", "")
        if p["play"] == "flagger pushed": return "sent help" if p["helped"] else "flagged through it"
        return p.get("call") or p["job"]
    rows = collections.defaultdict(list)
    print("set aside in the counts below: plays on a flag carried by a player with Shadow of Haste:", sum(1 for p in P if p.get("soh")))
    for p in P:
        if not p.get("soh"): rows[(p["play"], key(p), p["job"], p["ruled"])].append(p["met"])
    last = None
    for (play, k, job, ruled), v in sorted(rows.items(), key=lambda kv: (kv[0][0], -len(kv[1]))):
        if play != last: print(f"\n{play}"); last = play
        print(f"  {len(v):5}  met {100 * sum(v) / len(v):3.0f}%  {k[:60]:60}  {job}{'' if ruled else '  [draft, not ruled]'}")


def bench(path):
    D = json.load(open(path)); base = collections.defaultdict(list)
    for rid, v in D["flag_cost"].items():
        for f in (v or {}).get("flags", []):
            if f["how"] == "captured" and not f["pushed"] and not f.get("soh") and f["form"] == "single run": base[f"{D['matches'][rid]['map']}|{f['side']}"].append(f["arrive"])
    old = json.load(open(os.path.join(REPO, "data", "benchmarks", "flag_arrival.json")))
    old.update(usual={k: statistics.median(v) for k, v in sorted(base.items()) if len(v) >= 5}, flags={k: len(v) for k, v in sorted(base.items())})
    json.dump(old, open(os.path.join(REPO, "data", "benchmarks", "flag_arrival.json"), "w"), indent=1)
    print(len(old["usual"]), "hall sides")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "summary": summary(a[1])
    elif a and a[0] == "bench": bench(a[1])
    elif a:
        from replaylib import Match
        from state import GameState
        import common, moments
        rid = next((r for r in common.replay_ids() if r.startswith(a[0])), a[0])
        M = moments.Moments(GameState(Match.from_branch(rid)))
        for p in plays(M):
            print(f"{clock(p['t0']):>5}-{clock(p['t1']):>5} {p['team']:5} {p['play']:14} {'MET ' if p['met'] else 'not '} {p['scenario']}\n{'':30}job: {p['job']}  "
                  + "; ".join(f"{k}: {'yes' if v else 'no'}" for k, v in list(p["tests"].items()) + list(p["any_of"].items())))
    else: print(__doc__)
