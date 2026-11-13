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
from common import (REPO, READ_TO, SPLIT_STEP, FIGHT_LINK, JOIN_LOOK_S, RES_EVERY, BOOST_EVERY, BOOST_WARN_S, BOOST_LATE_S, LEAD_HALF, LEAD_ONE, CARRY_SPEED, PIT_R,
                    FLAG_GAIN, PART_RUN_GAIN, LATE_FLAG, ANSWER_CAP_S, COLLAPSE_VISIT_S, COLLAPSE_MIN_S, PINNED_S, LORD_PUSH_FROM, RACE_MIN_S, NUMBERS_TAIL_S, FLAG_JOB_MAX_S)
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
    out = []
    for f in M.flags_record():
        if f["pregame"]: continue
        out.append(dict(f, s0=int(f["set_off"] if f["set_off"] is not None else f["start"]), pick=int(f["start"]), e=int(f["end"]),
                        double=(f["form"] or "").startswith("double")))
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
        if inhand:                                                        # in hand means at the fight: standing in the stand area or with its main team. A flag still on its way is our run, begun first
            c = next((a for a in inhand["ids"] if M.carrying(a, w0) and M.AL[a][w0]), None)
            held = c is not None and (M.place_at(c, w0)[0] in ("stand", "greater stand") or c in M.main_team(A, w0 - w0 % SPLIT_STEP))
            if not held: new, inhand = inhand, None
        theirs = "double run" if f["double"] else "single run"
        ours = "a flag already in hand" if inhand else "stay" if not new else "double run" if new["double"] else "single run"
        g = inhand or new
        who = [role[a] for a in dict.fromkeys(g["ids"])] if g else []
        scen = f"They {theirs.replace(' run', '')} run ({M.m.tag[B]}'s {f['runner']}); {M.m.tag[A]}: {ours}"
        end = min(max(w1, g["e"] if g else w1), w0 + FLAG_JOB_MAX_S, T)
        bes = lambda t1: {"flag_lead": [K.lead(A, w0), K.lead(A, t1)], "deaths": [K.died(A, w0, t1), K.died(B, w0, t1)], "their_flag": f["how"], "their_form": f["form"], "our_form": g and g["form"]}
        kw = dict(their=theirs, ours=ours)
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
            out.append(_play(M, "flag", "own", A, w0, t1, [], scen, job, {"more of theirs die than of ours": K.died(B, w0, t1) > K.died(A, w0, t1)}, beside=bes(t1), **kw))
        elif (ours == "double run") == f["double"]:                      # single against single, double against double
            lv = K.lead(A, end)
            out.append(_play(M, "flag", "own", A, w0, end, who, scen, "Get the flag in, lose no more players than they do, and end no worse than half a flag behind",
                             {"our flag is capped": new["how"] == "captured", "no more of ours die than of theirs": K.died(A, w0, end) <= K.died(B, w0, end),
                              "no worse than half a flag behind at the end": lv is None or lv >= -LEAD_HALF}, beside=bes(end), **kw))
        elif ours == "double run":                                        # they single run, we double
            t1 = min(w1 + ANSWER_CAP_S + 5, T)                            # through their cap, and the answer to it
            gn = K.gain(A, w0, t1)
            out.append(_play(M, "flag", "own", A, w0, t1, who, scen, "Gain flag advantage through their next cap, and lose nobody while two are away",
                             {f"flag lead better by {FLAG_GAIN} or more": gn is not None and gn >= FLAG_GAIN, "nobody of ours dies": K.died(A, w0, t1) == 0}, beside=bes(t1), **kw))
        else:                                                             # they double run, we single
            lv = K.lead(A, end)
            s0, s1 = M._main_step(A, w0)[0], M._main_step(A, end)[0]
            out.append(_play(M, "flag", "own", A, w0, end, who, scen, "Kill or take ground with the extra player, and end no worse than a flag behind",
                             {"no worse than a flag behind at the end": lv is None or lv >= -LEAD_ONE},
                             any_of={"more of theirs die than of ours": K.died(B, w0, end) > K.died(A, w0, end), "ground taken": s0 is not None and s1 is not None and s1 < s0,
                                     "one of their NPCs dies": K.npcs(B, w0, end) > 0}, beside=bes(end), **kw))
    return out


# ---- pushing the flagger (R-427), and the flagger's side (gap 8)
def push_plays(M, K):
    FR, out, role, done = _flag_rows(M), [], M.m.roles, {}
    for p in M.flag_pushes():
        tm, foe = p["tm"], 3 - p["tm"]
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
        q = _play(M, "push flagger", "own", tm, p["t"], t1, p["roles"], scen, "Stop their flag, or make it 30% late", {},
                  any_of={"their flag is stopped": bool(stopped), "it arrives 30% or more later than usual": bool(late)}, beside=bes, pushers=n, main=bool(p["main"]))
        done[key] = q; out.append(q)
        helped = bool(p["helped"])                                        # the flagger's side: send help, or flag through it
        on_time = f is not None and f["how"] == "captured" and not late
        tests = {"the flag gets in, less than 30% late": on_time}
        if helped: tests["nobody else of ours dies meanwhile"] = K.died(foe, p["t"], t1, ids=set(M.st.players[foe]) - {p["flagger"]}) == 0
        out.append(_play(M, "flagger pushed", "own", foe, p["t"], t1, [p["role"]] + list(p["helped"]),
                         f"{M.m.tag[foe]}'s flagger ({p['role']}) is pushed by {n}; {M.m.tag[foe]} " + ("sends help (" + ", ".join(p["helped"]) + ")" if helped else "flags through it"),
                         "Get the flag in on time" + (", without losing a player for the help sent" if helped else ""), tests, beside=bes, helped=helped))
    return out


# ---- a split, from both sides (R-428, R-429, R-430), and the race back when it ends (gap 6)
def split_plays(M, K):
    st, m, T, out, tl = M.st, M.m, M.T, [], M._tl()
    role = m.roles
    for x in M.attempts():
        if x["kind"] != "split" or x.get("solo") == "other": continue
        tm, foe, an = x["tm"], 3 - x["tm"], x["answer"]
        t_in, t1 = int(x["t_in"]), int(x["t1"])
        own_d = st.side.get(foe)
        span = {a: (q["from"], q["to"]) for a, q in zip(x["ids"], x["members"])}
        near = lambda b, u: M.AL[b][u] and any(span[a][0] <= u <= span[a][1] and M.AL[a][u] and d(M.P[b][u], M.P[a][u]) < FIGHT_LINK for a in span)
        home = lambda b, u: M.AL[b][u] and M.place_at(b, u)[1] == own_d and M.place_at(b, u)[0] in HOMEG
        visits, coll = {}, []
        for b in an["ids"]:
            us = [u for u in range(t_in - t_in % 2, min(t1, T) + 1, SPLIT_STEP) if near(b, u)]
            if us: visits[b] = (us[0], us[-1])
        for b, (v0, v1) in visits.items():                               # a collapser comes from the main team after the split is on the ground, and goes back (R-429)
            u0, u1 = max(v0 - JOIN_LOOK_S, 0), min(v1 + JOIN_LOOK_S, T)
            u0 -= u0 % 2; u1 -= u1 % 2
            from_main = M.AL[b][u0] and b in M.main_team(foe, u0) and not home(b, u0) and v0 > t_in
            back = (M.AL[b][u1] and b in M.main_team(foe, u1) and not near(b, u1)) or v1 >= t1 - 4
            killed = any(v0 <= td <= v1 + 5 for a in x["ids"] for td in st.death_times.get(a, []))
            if from_main and back and (v1 - v0 >= COLLAPSE_MIN_S or killed) and v1 - v0 <= COLLAPSE_VISIT_S and b not in (an.get("went_back_ids") or []): coll.append(b)
        alive_d = sum(M.AL[b][min(t_in + READ_TO, T)] for b in st.players[foe])
        full = len(an.get("went_back") or []) >= 5 or an["n"] >= max(6, alive_d - 1)
        stay = [b for b in an["ids"] if b not in coll]
        k = max(x["size"], 1)
        n = 0 if not stay else max(min(an["n"], len(stay)), 1) if an["n"] else 0
        monk_def = any(m.A[b].get("p") == "Monk" and not role[b].startswith("Monk ") for b in stay[:max(n, 1)]) if stay else False
        lost_t = sorted(td for a in x["ids"] for td in st.death_times.get(a, []) if t_in - 1 <= td <= t1 + SPLIT_STEP * 10)
        n_lost, n_kill, n_npc = len(x["lost"]), len(x["kills"]), len(x["npcs"])
        e1 = min(t1 + 4, T)
        away_a, away_d = K.died(tm, t_in, e1) - n_lost, K.died(foe, t_in, e1) - n_kill      # deaths away from the split
        gain_a = K.gain(tm, t_in, e1)
        elsewhere = {"more of theirs die away from the split than of ours": away_d > away_a, f"flag lead better by {FLAG_GAIN} or more": gain_a is not None and gain_a >= FLAG_GAIN}
        size = {1: "a solo split", 2: "a two-player split", 3: "a three-player split"}.get(k, f"a split of {k}")
        if len(x["members"]) > k: size += f" at a time, {len(x['members'])} players in all"
        whoA, whoD = [q["role"] for q in x["members"]], [role[b] for b in stay]
        besA = {"npcs_taken": x["npcs"], "kills": x["kills"], "lost": x["lost"], "main": x["main"], "flag_lead": [K.lead(tm, t_in), K.lead(tm, e1)], "end": x["end"], "way": x["way"]}
        besD = {"npcs_lost": x["npcs"], "lost": x["kills"], "split_killed": x["lost"], "flag_lead": [K.lead(foe, t_in), K.lead(foe, e1)], "behind_s": an["behind_s"], "end": x["end"],
                "main_down_s": x["main"]["up_s"], "main_up_s": x["main"]["down_s"]}
        base = f"{M.m.tag[tm]}: {size} ({', '.join(whoA)}) by the {x['way'] or 'door'}"
        # the attacker's job, set by the answer it met
        if full: sa, ja, ta, aa = "met by a full collapse", "Survive and gain an advantage elsewhere on the map", {"nobody on the split dies": n_lost == 0}, elsewhere
        elif n == 0 and coll: sa, ja, ta, aa = None, None, None, None      # nobody stayed to defend it: the collapse below is the answer it met
        elif n == 0: sa, ja, ta, aa = "undefended", "Take NPCs", {"an NPC taken": n_npc > 0}, None
        elif k == 1 and n == 1 and monk_def: sa, ja, ta, aa = "1 v 1, defended by a monk", "Hold the monk there; the main team's job is to kill", {"the split player survives": n_lost == 0}, None
        elif k == 1 and n == 1: sa, ja, ta, aa = "1 v 1, the defender not a monk", "Kill or take NPCs", {}, {"a defender killed": n_kill > 0, "an NPC taken": n_npc > 0}
        elif k > n: sa, ja, ta, aa = f"a player or more up ({k} v {n})", "Kill or take NPCs", {}, {"a defender killed": n_kill > 0, "an NPC taken": n_npc > 0}
        elif k == n: sa, ja, ta, aa = f"even ({k} v {n})", "Take NPCs or kills", {}, {"a defender killed": n_kill > 0, "an NPC taken": n_npc > 0}
        else: sa, ja, ta, aa = f"a player or more down ({k} v {n})", "Survive and gain an advantage elsewhere on the map", {"nobody on the split dies": n_lost == 0}, elsewhere
        if sa: out.append(_play(M, "split", "attacker", tm, t_in, e1, whoA, f"{base}; {sa}", ja, ta, any_of=aa, beside=besA, answer=sa, size=k, defenders=n))
        if k == 1 and n == 1 and monk_def and not full:
            out.append(_play(M, "split", "attacker's main team", tm, t_in, e1, [], f"{base}; a monk of theirs is held in its base", "Kill at the main fight while their monk is away",
                             {"more of theirs die away from the split than of ours": away_d > away_a}, beside=besA, answer=sa, size=k, defenders=n))
        # the defender's side
        dbase = f"{M.m.tag[foe]} against {size} of {M.m.tag[tm]}"
        if full:
            out.append(_play(M, "split", "defender", foe, t_in, e1, an.get("went_back") or whoD, f"{dbase}: full collapse", "Kill the split or drive it out (the flags it costs are beside it)", {},
                             any_of={"a split player dies": n_lost > 0, "the split is driven out as the defenders arrive": bool(x["forced_out"])}, beside=besD, call="full collapse", size=k, defenders=an["n"]))
        else:
            if n == 0 and not coll:
                gd = K.gain(foe, t_in, e1)
                out.append(_play(M, "split", "defender", foe, t_in, e1, [], f"{dbase}: no answer", "Win elsewhere before the split costs more than it gains", {},
                                 any_of={"more of theirs die away from the split than of ours": away_a > away_d, f"flag lead better by {FLAG_GAIN} or more": gd is not None and gd >= FLAG_GAIN},
                                 beside=besD, ruled=False, call="no answer", size=k, defenders=0))
            elif n and n < k:
                out.append(_play(M, "split", "defender", foe, t_in, e1, whoD[:n], f"{dbase}: {'one defender' if n == 1 else str(n) + ' defenders'}, a player or more down", "Delay: keep the split off the NPCs and stay alive",
                                 {"no NPC lost": n_npc == 0, "no defender dies": n_kill == 0}, beside=besD, call="one defender" if n == 1 else "a player down", size=k, defenders=n))
            elif n and n == k:
                out.append(_play(M, "split", "defender", foe, t_in, e1, whoD[:n], f"{dbase}: mirror ({n} v {k})", "Hold it even: lose nothing at home and nothing for it",
                                 {"no NPC lost": n_npc == 0, "no more defenders die than split players": n_kill <= n_lost}, beside=besD, call="mirror", size=k, defenders=n))
            elif n:
                out.append(_play(M, "split", "defender", foe, t_in, e1, whoD[:n], f"{dbase}: {'add one' if n == k + 1 else 'send ' + str(n)} ({n} v {k})", "Kill it or drive it out with the extra player, and lose nothing for it",
                                 {"no NPC lost": n_npc == 0}, any_of={"a split player dies": n_lost > 0, "the split is driven out as the defenders arrive": bool(x["forced_out"])},
                                 beside=besD, call="add one", size=k, defenders=n))
            groups = []                                                   # one play a collapse: collapsers whose visits overlap came together
            for b in sorted(coll, key=lambda b: visits[b][0]):
                if groups and visits[b][0] <= groups[-1]["v1"] + 10: groups[-1]["ids"].append(b); groups[-1]["v1"] = max(groups[-1]["v1"], visits[b][1])
                else: groups.append({"ids": [b], "v0": visits[b][0], "v1": visits[b][1]})
            for gr in groups:                                             # who came, for how long, what it cost at the main fight
                cl, v0, v1 = gr["ids"], gr["v0"], gr["v1"]
                rows = [tl[u][foe]["main"] for u in range(v0 - v0 % 2, min(v1, T) + 1, SPLIT_STEP) if tl[u][foe]["main"]]
                cost = {"visit_s": v1 - v0, "flag_lead": [K.lead(foe, v0), K.lead(foe, min(v1 + 10, T))], "main_net": sum(r[0] - r[1] for r in rows) * SPLIT_STEP,
                        "deaths_away_from_the_split": K.died(foe, v0, v1 + 5) - sum(1 for td, a in K.deaths[foe] if v0 < td <= v1 + 5 and a in an["ids"]), "npcs_lost": x["npcs"]}
                names = ", ".join(role[b] for b in cl)
                whole = len(cl) >= 5 or len(cl) + n >= max(6, alive_d - 1)      # five or more coming together, or nearly everyone alive on it: a full collapse
                if whole:
                    out.append(_play(M, "split", "defender", foe, v0, min(v1 + 5, T), [role[b] for b in cl], f"{dbase}: full collapse ({len(cl)} from the main fight, {n} defending it)",
                                     "Kill the split or drive it out (the flags it costs are beside it)", {},
                                     any_of={"a split player dies": any(v0 <= td <= v1 + 5 for td in lost_t), "the split is driven out as the defenders arrive": any(v0 - 8 <= fo["left"] <= v1 + 15 for fo in x["forced_out"])},
                                     beside=cost, call="full collapse", size=k, defenders=n + len(cl)))
                else:
                    out.append(_play(M, "split", "defender", foe, v0, min(v1 + 5, T), [role[b] for b in cl], f"{dbase}: collapse by {names} from the main fight ({n} defending it)",
                                     "Kill a split player before going back (what it cost at the main fight and in flags is beside it)",
                                     {"a split player dies during the collapse": any(v0 <= td <= v1 + 5 for td in lost_t)}, beside=cost, call="collapse", size=k, defenders=n))
                ga = K.gain(tm, v0, min(v1 + 10, T))                # the attacker's side of the same collapse (R-429: as against a full collapse)
                d_a, d_d = K.died(tm, v0, v1 + 5) - sum(1 for td in lost_t if v0 < td <= v1 + 5), K.died(foe, v0, v1 + 5) - sum(1 for td, a in K.deaths[foe] if v0 < td <= v1 + 5 and a in an["ids"])
                out.append(_play(M, "split", "attacker", tm, v0, min(v1 + 5, T), whoA, f"{base}; " + ("met by a full collapse" if whole else f"collapsed on by {names}"), "Survive and gain an advantage elsewhere on the map",
                                 {"nobody on the split dies": not any(v0 <= td <= v1 + 5 for td in lost_t)},
                                 any_of={"more of theirs die away from the split than of ours": d_d > d_a, f"flag lead better by {FLAG_GAIN} or more": ga is not None and ga >= FLAG_GAIN},
                                 beside=dict(besA, visit_s=v1 - v0), answer="met by a full collapse" if whole else "collapsed on", size=k, defenders=n))
            if k == 1 and n == 1:                                         # a lone defender part-running his flag (R-430)
                b = stay[0]
                carried = sum(SPLIT_STEP for u in range(t_in - t_in % 2, min(t1, T) + 1, SPLIT_STEP) if M.carrying(b, u))
                if carried >= 6:
                    gd = K.gain(foe, t_in, e1)
                    out.append(_play(M, "split", "defender", foe, t_in, e1, [role[b]], f"{dbase}: the lone defender ({role[b]}) carries his flag while defending", "Gain a slight flag advantage while losing no NPC and not dying",
                                     {f"flag lead better by {PART_RUN_GAIN} or more": gd is not None and gd >= PART_RUN_GAIN, "no NPC lost": n_npc == 0, "the defender does not die": n_kill == 0},
                                     beside=dict(besD, carried_s=carried), call="part-run", size=1, defenders=1))
        ah = x.get("ahead")                                               # the race back (gap 6): the team back first has the seconds ahead
        if ah and abs(ah["lead_s"]) >= RACE_MIN_S:
            first = tm if ah["lead_s"] > 0 else foe
            kf, ka = (ah["kills_for"], ah["kills_against"]) if first == tm else (ah["kills_against"], ah["kills_for"])
            out.append(_play(M, "split", "race back", first, min(ah["split_back"], ah["defenders_back"]), max(ah["split_back"], ah["defenders_back"]) + 10, [],
                             f"The split ends: {M.m.tag[first]}'s players are back at the main fight {abs(ah['lead_s'])} s before {M.m.tag[3 - first]}'s", "Use the seconds ahead for a kill at the main fight",
                             {"more of theirs die than of ours in those seconds": kf > ka}, beside={"lead_s": abs(ah["lead_s"]), "kills": [kf, ka]}, call="race back"))
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
        kw = dict(source=src, numbers_side=side, call=c)
        if src == "wipe" or (src == "kills" and side == "up" and x["scenario"]["parts"].get("step", 0) <= -2 and x["scenario"]["parts"]["short_because"].get("kills", 0) >= 3):
            if side != "up": continue                                     # gap 4: after a wipe, or kills at their base
            res = min(st.next_res(t) + 5, T)
            out.append(_play(M, "numbers", "after a wipe", tm, t, res, [], scen, "Take pit NPCs before their base res", {"one of their pit NPCs dies before the res": K.npcs(foe, t, res, pit=True) > 0},
                             beside=dict(bes(res), res_in=x["state"]["res_in"]), **kw))
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
    for tm, a, b in pinned(M):
        t = a
        while t < b:                                                      # one play to each base res while it lasts
            t1 = min(st.next_res(t), b + 4, T)
            if t1 - t >= 10:
                s1 = M._main_step(tm, min(t1 + 10, T))[0]
                alive = sum(M.AL[x][min(t1 + 10, T)] for x in st.players[tm])
                hold = {"no pit NPC lost and nobody dies until the base res": K.npcs(tm, t, t1, pit=True) == 0 and K.died(tm, t, t1) == 0,
                        "it breaks out (five or more, out of its base)": s1 is not None and s1 <= 1 and alive >= 5 and t1 < st.next_res(t)}
                out.append(_play(M, "pinned", "own", tm, t, t1, [], f"{M.m.tag[tm]} is held in its own base or pit by {M.m.tag[3 - tm]}'s main team ({st.pit_npcs(tm, t)} alive; base res in {round(st.next_res(t) - t)} s)",
                                 "Hold the NPCs and lose nobody until the base res, or break out", {}, any_of=hold,
                                 beside={"deaths": [K.died(tm, t, t1), K.died(3 - tm, t, t1)], "pit_npcs_lost": K.npcs(tm, t, t1, pit=True), "pinned_s": b - a}))
            t = st.next_res(t)
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
        att, mk, dfn, dmk = [], [], [], []
        for u in range(t0 - t0 % 2, min(t1, T) + 1, SPLIT_STEP):
            A = [a for a in st.players[tm] if M.AL[a][u] and d(M.P[a][u], lp) <= PIT_R]
            Dn = [b for b in st.players[foe] if M.AL[b][u] and M.place_at(b, u)[1] == fs and M.place_at(b, u)[0] in ("pit", "base")]
            att.append(len(A)); mk.append(M._mk(A)); dfn.append(len(Dn)); dmk.append(M._mk(Dn))
        med = lambda xs: sorted(xs)[len(xs) // 2] if xs else 0
        n, monks = med(att), med(mk)
        pit = sum(1 for a, v in st.geo.npcs.items() if v["team"] == foe and v.get("pit") and v["kind"] != "guild_lord" and st.npc_dead.get(a, 1e9) > t0)
        rel = "more attackers than pit NPCs" if n > pit else "as many attackers as pit NPCs" if n == pit else "fewer attackers than pit NPCs"
        ids = set(r["ids"])
        on_lord = sum(1 for u, a, _ in M.lord_hits.get(foe, ()) if t0 <= u <= t1)
        on_players = sum(1 for u in range(t0, min(t1, T) + 1) for a, b in M.hits.get(u, ()) if a in st.players[tm] and d(M.P[a][u], lp) <= 2 * PIT_R)
        aim = "Lord damage" if on_lord >= on_players else "killing the defenders"
        dmg = round(sum(v for u, _, v in M.lord_hits.get(foe, ()) if t0 <= u <= t1))
        own = round(sum(v for u, _, v in M.lord_hits.get(tm, ()) if t0 <= u <= t1))
        bes = {"attackers": n, "pit_npcs": pit, "monks_with_the_push": monks, "aim": aim, "lord_damage": dmg, "own_lord_damage_meanwhile": own, "defenders": med(dfn), "defender_monks": med(dmk),
               "deaths": [K.died(tm, t0, t1 + 5), K.died(foe, t0, t1 + 5)], "match_decided_by": how, "match_lord_damage_gvg_report": [taken.get(foe), taken.get(tm)],
               "lord_killed_in_it": dead[foe] is not None and t0 <= dead[foe] <= t1 + 5}
        out.append(_play(M, "lord", "attacker", tm, t0, t1, r["roles"], f"{M.m.tag[tm]} pushes {M.m.tag[foe]}'s Guild Lord with {n} ({monks} monk{'s' if monks != 1 else ''}) against {pit} pit NPCs: {rel}; playing for {aim}",
                         "Most Lord damage, or the kill, while keeping the own Lord up (the result is the match)", {"the match is won": won == tm}, beside=bes, relation=rel, monks=monks, aim=aim, attackers=n, pit=pit))
        out.append(_play(M, "lord", "defender", foe, t0, t1, [], f"{M.m.tag[foe]} defends its Guild Lord with {med(dfn)} ({med(dmk)} monk{'s' if med(dmk) != 1 else ''}) against {n}",
                         "Do not die, keep Lord damage down, keep the Lord alive (the result is the match)", {"the match is won": won == foe}, beside=bes, defenders=med(dfn), monks=med(dmk)))
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
    return [{"how": f["how"], "form": f["form"], "side": M.st.side.get(f["tm"]), "arrive": (f["e"] - f["held_s"]) - f["pick"],
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
        if p["play"] == "flagger pushed": return "sent help" if p["helped"] else "flagged through it"
        return p.get("call") or p["job"]
    rows = collections.defaultdict(list)
    for p in P: rows[(p["play"], key(p), p["job"], p["ruled"])].append(p["met"])
    last = None
    for (play, k, job, ruled), v in sorted(rows.items(), key=lambda kv: (kv[0][0], -len(kv[1]))):
        if play != last: print(f"\n{play}"); last = play
        print(f"  {len(v):5}  met {100 * sum(v) / len(v):3.0f}%  {k[:60]:60}  {job}{'' if ruled else '  [draft, not ruled]'}")


def bench(path):
    D = json.load(open(path)); base = collections.defaultdict(list)
    for rid, v in D["flag_cost"].items():
        for f in (v or {}).get("flags", []):
            if f["how"] == "captured" and not f["pushed"] and f["form"] == "single run": base[f"{D['matches'][rid]['map']}|{f['side']}"].append(f["arrive"])
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
