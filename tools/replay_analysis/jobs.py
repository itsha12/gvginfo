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
from common import (MEET_R, OPEN_FROM_S, OPEN_BY_S, OPEN_S, STAND_R, MERGE_S, FIGHT_ACT, FIGHT_CLOSE, FIGHT_HOLD_S, HOLD_S, HANDOFF_GAP_S, REPO, READ_TO, SPLIT_STEP, SPLIT_GAP_S, FIGHT_LINK, JOIN_S, JOIN_LOOK_S, NPC_NEAR, can_kill, SOH_REMOVED, RUN_SPEED, GROUND_JUMP, RES_EVERY, BOOST_EVERY, BOOST_WARN_S, BOOST_LATE_S, LEAD_HALF, LEAD_ONE, CARRY_SPEED, PIT_R,
                    FLAG_GAIN, PART_RUN_GAIN, LATE_FLAG, ANSWER_CAP_S, COLLAPSE_VISIT_S, PINNED_S, LORD_PUSH_FROM, LORD_BASE_R, AFTER_WIPE_MIN_S, NUMBERS_TAIL_S, FLAG_JOB_MAX_S, MAIN_BIG, TURN_S, TURN_CLOSE)
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
        (R-466: a flag run is held to the deaths at the main fight, not to those of a split that was collapsed on), and
        those of players who died defending an enemy split (R-499: his words on HC v Team 11:58, Team's 8 Monk at its
        own back door, "it happened on split (the flag decision didn't really affect this death at all)")."""
        M = self.M
        sp = [x for x in M.attempts() if x["kind"] == "split" and x["tm"] == tm]
        theirs = [x for x in M.attempts() if x["kind"] == "split" and x["tm"] != tm]
        on_split = lambda x_, td: any(x_ in s["ids"] and q["from"] - 2 <= td <= q["to"] + 8 for s in sp for a_, q in zip(s["ids"], s["members"]) if a_ == x_)
        def defending(x_, td):                             # within reach of an enemy split player who is out on his split just before the death
            u = min(max(int(td) - 1, 0), self.T)
            return bool(M.P[x_][u]) and any(q["from"] - 2 <= td <= q["to"] + 8 and M.AL[a_][u] and M.P[a_][u] and d(M.P[x_][u], M.P[a_][u]) < FIGHT_LINK
                                             for s in theirs for a_, q in zip(s["ids"], s["members"]))
        return sum(1 for td, x in self.deaths[tm] if a < td <= b and not on_split(x, td) and not defending(x, td))

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


FLAG_AFTER_S = (60, 90, 180)           # what followed a flag decision, read at three seconds so that the effect can be followed as it grows and fades (R-543; 90 and 180 s are R-294's; 120 s was read too and dropped, R-544: it sat between the two and changed no verdict)
FLAG_BEFORE_S = 60                     # how long before a flag decision the position is read again, for the test of a call against what came before it
FLAG_TRACK_S = tuple(range(0, 241, 15))  # the seconds from their runner's set-off at which the flag lead and the holder of the stand are kept on a flag play (`track`)
FLAG_TRACK_FOR = 300                   # ... and for how long after it every cap and morale boost is kept, by its second
SPLIT_TRACK_S = (0, 15, 20, 30, 40, 45, 60, 90)  # the seconds from when a split is told at which its numbers are kept on its plays (`split.numbers`), so that the answer to it can be read at a fixed second (the split family, R-558)


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
    splits = [x for x in M.attempts() if x["kind"] == "split"]
    others = [tuple(x["pts"][0]) for x in (M.hall.labels or []) if x.get("type") == "Flag stand" and x.get("pts") and d(tuple(x["pts"][0]), M.hall.stand) > 500]
    second = set()                                                        # a double run is a pair of runs (his marks, cope v Team 2:43: "derv 1 going back for next flag before 2 warrior has even capped"): the flag its second player goes back for is part of it
    for f in M.flags_record():
        if not (f["form"] or "").startswith("double"): continue
        r2 = min((q for q in M.run_starts() if q["tm"] == f["tm"] and q["pickup"] > int(f["end"]) - 2), key=lambda q: q["pickup"], default=None)
        went_at = r2 and next((v for v in (r2["set_off"], r2["waited"], r2["pickup"]) if v is not None), None)
        # ... a second player who goes back to run the next flag (his account of hdm v hook 5:52 to 7:24: hook's Mesmer "already on the way"); a player who is home because he came back from a split is not one (R-472)
        if r2 is not None and not any(x["tm"] == f["tm"] and a_ == r2["a"] and qm["from"] <= went_at and qm["to"] >= went_at - SPLIT_GAP_S for x in splits for a_, qm in zip(x["ids"], x["members"])):
            # ... and at the opening, where the first flag is one decision from the gates to its cap (R-479), a second player who turns back for the next flag before that
            # cap makes it a double run (his mark, Men v RACK 0:00, Classic: "Men double ran with warrior waiting back": Hammer A turns back at 0:04 and waits at the spawn from 0:12, the first flag capped at 0:30)
            if went_at <= int(f["start"]) + SPLIT_STEP or (f["pregame"] and went_at <= int(f["end"]) + SPLIT_STEP): second.add((f["tm"], int(f["start"])))      # the second player was back before the first flag was picked up (left at the spawn at the opening): a double run from its start
            if went_at <= int(f["end"]) + SPLIT_STEP: second.add((f["tm"], int(r2["pickup"])))                     # ... and it is a double run only from then (R-484; his mark, RJT v RACK 1:41: "derv single runs twice"): the first run of the pair is a single run when the other team decides against it. The second player has to have gone back by the cap (R-472: "while the first is still capping"; his mark, Men v Crew 11:32, "a single run half run for Men": the AoB Derv caps at 11:36 and the Ranger sets off at 11:43)
    for f in M.flags_record():
        r = next((rs[k] for k in ((f["tm"], int(f["start"]) + dt) for dt in (0, -1, 1)) if k in rs), None)
        s0, runner, pick, ids, carries = int(f["start"]), f["runner"], int(f["start"]), f["ids"], (r["carries"] if r is not None else [])
        off = None                                                        # the second its runner turned for home, when he went back for it (R-498)
        soh = M.day < SOH_REMOVED and any(m.sk(b) == "Shadow of Haste" for a in f["ids"] for b in m.A[a].get("bar", []) if b)      # R-456: only while the mechanic was in the game
        dbl = any((f["tm"], int(f["start"]) + dt) in second for dt in (0, -1, 1))
        if r is not None and f["pregame"]:                               # who held the flag before the gates opened did not carry it in the match (Men v RACK 0:00: Hammer A, who then waits back for the next one)
            ids = [a for a in ids if any(c[0] == a and (c[2] is None or c[2] > 0) for c in r["carries"])] or ids
        if r is not None and M.not_run(r): continue                      # only brought up with the team, never capped or pushed for the stand: no run (R-505; 옷옷옷옷 v RACK 0:00, his mark: "RACK brings flag up on Warrior, but DOES NOT run the flag")
        if r is not None:
            went = r["set_off"] is not None and not pin(f["tm"], r["set_off"]) and not pin(f["tm"], r["pickup"])      # he walked back for it, his team not held in its base (a player falling back into his base with his team did not go to run)
            # the opening's first flag is one run from the opening (R-479), though its runner put it down on the way and took it up again to cap (옷옷옷옷 v RACK: the
            # 8 Monk runs it to the stand area by 0:21 and caps at 0:45, his mark: "this is the opening run")
            opening = f["pregame"] and f["how"] == "captured" and r["chain"] is not None and r["out_by"] is not None
            if opening: runner, ids = m.roles[r["out_by"]], r["chain_ids"]
            if not opening and r["chain"] is not None and r["under_way"] is not None:
                # the flag lay on the ground and was taken up again: two runs. The first, to where it was put down, is a run if its runner went back for it (cope v Team
                # 2:43, his mark: "derv 1 going back for next flag"; a flag picked up at home and put down again is none: TFS v 옷옷옷옷 1:20 and 11:01); the second starts
                # where it was taken up, with that player (RJT v RACK 4:37)
                first = [c for c in r["carries"] if c[2] is not None and c[2] <= r["first_end"]]
                if went and M.travelled(f["tm"], first):
                    out.append(dict(f, runner=runner, s0=min(int(r["moment"]), s0, int(r["first_end"])), pick=pick, e=int(r["first_end"]), how="put down", form=None, ids=r["first_ids"], held_s=0, other_stand=False, double=dbl, soh=soh))
                s0, runner, pick, ids, dbl = int(r["under_way"]), m.roles[r["out_by"]], int(r["chain"]), r["chain_ids"], False
                carries = [c for c in r["carries"] if c[1] >= r["chain"] - 1]
            elif went and not opening: s0, off = min(int(r["moment"]), s0), int(r["set_off"])      # when he goes to run, by the hall (R-461); and when he set off
            elif not opening and r["under_way"] is not None and r["under_way"] > r["pickup"] + SPLIT_STEP:
                # picked up by a player who was already at home and did not go back for it: it is a run only from when he commits to it, the second the flag is taken out of
                # the base, by whoever carries it then (R-488: "yes, they picked up the flag, but it doesn't really look like a flag run. It's not something the team would
                # have to respond to ... until the time we can tell he actually commits to flagging"). This replaces the wait of FLAG_TAKEN_OUT_S: no length of time makes it a run
                s0, runner = int(r["under_way"]), m.roles[r["out_by"]]
        if r is not None and f["how"] != "captured" and not M.travelled(f["tm"], carries): continue      # picked up and put down at home: not a run
        e, other = int(f["end"]), False
        if r is not None and f["how"] != "captured" and carries and carries[-1][2] is not None and carries[-1][2] < e:
            e = int(carries[-1][2])                                       # put down for good: the run ends there, not when the flag goes back to the spawn
            p = M.P[carries[-1][0]][min(e, M.T)]
            other = bool(p) and any(d(p, o) < 400 for o in others)        # at the hall's other flag stand (his answer on TFS v 옷옷옷옷 2:54: the Obelisk flag stand)
        out.append(dict(f, runner=runner, s0=min(s0, e), off=min(off if off is not None else s0, s0, e), pick=pick, e=e, ids=ids, other_stand=other, double=dbl, soh=soh,
                        waited_back=bool(r is not None and r.get("waited_back") and r.get("waited") is not None), waited=r and r.get("waited")))
    M._frows = out
    return out


def opening(M):
    """How the game starts (R-520, his words: "The beginning of the game is very important ... We need to know a) who went where (e.g. 8 to stand for each team or
    7 to stand with 1 waiting back, etc.) b) who brought up the flag; c) who captures and when (e.g. HC caps first at 0:12 and RACK overcaps at 0:24) and THEN the
    first run decision (or e.g. both teams hold the flag, no one captures for the first 1:32; or e.g. hold brings up first flag on rit, retreats before capping).
    We shouldn't be describing these as single runs for the opening"). One record a match: for each team where its players went from the gates (to the stand with
    the team, out on a split and by which door, or back at home), who waits at the flag spawn for the next flag, who brought the first flag up and what became of
    it; then who capped first and who capped over it, and when. `words` says it in one line."""
    if getattr(M, "_opening", None) is not None: return M._opening
    st, m, T, S, role = M.st, M.m, M.T, SPLIT_STEP, M.m.roles
    def met(t):
        c1, c2 = (M.centre([a for a in M.main_team(tm, t) if M.AL[a][t]], t) for tm in st.teams)
        return c1 is not None and c2 is not None and d(c1, c2) < MEET_R
    t_o = next((t for t in range(OPEN_FROM_S, min(OPEN_BY_S, T) + 1, S) if met(t)), min(OPEN_BY_S, T - T % S))
    win = list(range(t_o, min(t_o + OPEN_S, T) + 1, S))
    FR, splits = _flag_rows(M), [x for x in M.attempts() if x["kind"] == "split" and x["t0"] <= t_o + OPEN_S]      # a split from the gates: it set out by then
    names = lambda ids: ", ".join(role[a] for a in ids)
    count = lambda n, word: f"{n} {word}"
    out = {"t": t_o, "teams": {}}
    first_cap = {tm: next((int(u) for u, h in st.caps if h == tm), None) for tm in st.teams}
    for tm in st.teams:
        spl, back, stand, way = [], [], [], None
        for a in st.players[tm]:
            x = next((x for x in splits if x["tm"] == tm and any(q["role"] == role[a] and q["from"] <= t_o + 2 * OPEN_S for q in x["members"])), None)
            if x is not None: spl.append(a); way = way or x.get("way")
            elif sum(1 for t in win if M.AL[a][t] and M.P[a][t] and M.at_home(a, t, tm)) * 2 > len(win): back.append(a)
            else: stand.append(a)
        # who waits at the flag spawn for the next flag (a double run from the gates), among those at home
        went_back = lambda q: min(v for v in (q["set_off"], q["waited"]) if v is not None) if (q["set_off"] is not None or q["waited"] is not None) else None      # left at the spawn from the gates, or turned back for it in the first seconds (Men v RACK 0:04: "Men double ran with warrior waiting back")
        waits = list(dict.fromkeys(q["a"] for q in M.run_starts() if q["tm"] == tm and q["pickup"] > 2 and went_back(q) is not None and went_back(q) <= t_o and q["a"] in back))
        rows = sorted((x for x in FR if x["tm"] == tm), key=lambda x: x["s0"])
        pre = next((x for x in rows if x["pregame"]), None)
        up = next((q for q in M.run_starts() if q["tm"] == tm and q["pickup"] <= 2 and M.not_run(q)), None)      # brought up with the team and not run (R-505)
        flag = {"brought": None, "by": [], "how": None, "at": None, "held_s": 0, "sent_back": None}
        if pre is not None:
            by = list(dict.fromkeys(role[a] for a in pre["ids"])) or [pre["runner"]]      # who carried it once the gates were open: the player who held it before them and stays back is not one
            flag.update(brought=True, by=by, how=pre["how"], at=int(pre["e"]), held_s=int(pre.get("held_s") or 0))
        elif rows and rows[0].get("off", rows[0]["s0"]) <= OPEN_BY_S * 2:      # no flag came up with the team and a player went back for the first one (his words on Men v hold 0:00: "hold did not bring the first flag and had to send ele back for it"), though a flag was carried a few steps and put down
            nxt = rows[0]
            flag.update(brought=False, sent_back={"who": nxt["runner"], "at": int(nxt.get("off", nxt["s0"])), "how": nxt["how"], "end": int(nxt["e"])})
        elif up is not None:
            flag.update(brought=True, by=list(dict.fromkeys(role[c[0]] for c in sorted(up["carries"], key=lambda c: c[1]) if c[0] in up["serious"])), how="not run")
        else: flag["brought"] = False
        out["teams"][tm] = {"stand": stand, "split": spl, "way": way, "back": back, "waits": waits, "flag": flag, "first_cap": first_cap[tm]}
    caps = sorted((u, tm) for tm, u in first_cap.items() if u is not None)
    out["caps"] = caps
    def team_words(tm):
        x = out["teams"][tm]; f = x["flag"]
        w = [count(len(x["stand"]), "to the stand")]
        if x["split"]: w.append((f"{len(x['split'])} out" if len(x["split"]) >= 4 else f"{len(x['split'])} on a split") + (f" by the {x['way']}" if x["way"] else "") + f" ({names(x['split'])})")
        rest = [a for a in x["back"] if a not in x["waits"]]
        if x["waits"]: w.append(f"{names(x['waits'])} {'waits' if len(x['waits']) == 1 else 'wait'} back at the flag spawn for the next flag")
        if rest: w.append(f"{names(rest)} {'stays' if len(rest) == 1 else 'stay'} back at home" + (" to defend" if out["teams"].get(3 - tm, {}).get("split") or any(x["tm"] != tm for x in splits) else ""))
        if f["brought"] and f["how"] == "not run": fw = f"its first flag brought part of the way with the team ({', '.join(f['by'])}) and not run"
        elif f["brought"]:
            fw = f"its first flag brought up by {f['by'][0]}" + (f", handed to {' and '.join(f['by'][1:])}" if len(f["by"]) > 1 else "")
            if f["how"] == "captured": fw += (f", held at the stand for {f['held_s']} s" if f["held_s"] >= HOLD_S else "") + f" and capped at {clock(f['at'])}"
            else: fw += f", {f['how']} at {clock(f['at'])} without a cap"
        else:
            sb = f["sent_back"]
            fw = "no flag brought up" + ("" if sb is None else f"; {sb['who']} goes back for its first at {clock(sb['at'])}" + (f", capped at {clock(sb['end'])}" if sb["how"] == "captured" else f", {sb['how']} at {clock(sb['end'])} without a cap"))
        return f"{m.tag[tm]}: " + ", ".join(w) + "; " + fw
    if not caps: cw = "Nobody has capped a flag" + (f" by {clock(min(T, 180))}" if T >= 180 else " in the game")
    elif len(caps) == 1: cw = f"{m.tag[caps[0][1]]} caps first at {clock(caps[0][0])}; {m.tag[3 - caps[0][1]]} never caps"
    else: cw = f"{m.tag[caps[0][1]]} caps first at {clock(caps[0][0])}; {m.tag[caps[1][1]]} caps over it at {clock(caps[1][0])}"
    if caps and caps[0][0] >= 60: cw = f"Nobody caps for the first {clock(caps[0][0])}. " + cw
    order = [tm for _, tm in caps] + [tm for tm in st.teams if tm not in [k for _, k in caps]]
    out["words"] = "The opening. " + ". ".join(team_words(tm) for tm in order) + ". " + cw
    M._opening = out
    return out


def opening_plays(M, K):
    """Each team's first flag as a job under the opening (R-520, R-500), the same for both teams (his mark on HC v hdm 0:00, Classic: "this should be the same goal
    for both teams, no?": only the team whose first flag answered the other's had been given it). One play a team: get the first flag in, on its own clock, from the
    gates to where that flag was capped or lost."""
    o, out = opening(M), []
    for tm in M.st.teams:
        f = o["teams"][tm]["flag"]
        sb = f.get("sent_back")
        capped = (f["how"] == "captured") if f["brought"] else bool(sb and sb["how"] == "captured")
        end = f["at"] if (f["brought"] and f["at"] is not None) else (sb["end"] if sb else o["t"])
        who = f["by"] if f["brought"] else ([sb["who"]] if sb else [])
        out.append(_play(M, "opening", "own", tm, 0, max(int(end), o["t"]), who, o["words"], "Get the first flag in", {"our flag is capped": capped},
                         beside={"first_cap": o["teams"][tm]["first_cap"], "flag": dict(f)}, call="the first flag", opening=o["words"]))
    return out


def flag_plays(M, K, pinned_at):
    FR, out, T, role = _flag_rows(M), [], M.T, M.m.roles
    runs = []                                                             # their runs: a flag dropped or returned and taken again at once is one run, the one that got further
    for f in sorted(FR, key=lambda f: (f["tm"], f["s0"])):
        if runs and runs[-1]["tm"] == f["tm"] and f["s0"] - runs[-1]["s0"] <= 10:
            if (f["how"] == "captured", f["e"]) > (runs[-1]["how"] == "captured", runs[-1]["e"]): runs[-1] = f
        else: runs.append(f)
    canon = {}                                                            # two flags of one team set off for within 10 s of one another are one decision (the two legs of a double run): one name for both
    for tm_ in M.st.teams:
        last = None
        for x_ in sorted((x_ for x_ in FR if x_["tm"] == tm_), key=lambda x_: x_["s0"]):
            if last is not None and x_["s0"] - last[1] <= 10: canon[(tm_, x_["s0"])] = last[0]; last = (last[0], x_["s0"])
            else: canon[(tm_, x_["s0"])] = x_["s0"]; last = (x_["s0"], x_["s0"])
    for f in sorted(runs, key=lambda f: f["s0"]):
        B, A = f["tm"], 3 - f["tm"]
        w0, w1 = f["s0"], min(f["e"], T)
        if w1 - w0 < 10 or pinned_at(A, w0): continue
        mine = [g for g in FR if g["tm"] == A]
        # Who set off first is read on the one clock of R-546, the second a runner turned for home (`off`, R-498), not the second the hall's rule tells his run (`s0`,
        # R-461): a runner who turned for home 11 s before theirs ran first, and theirs is the answer, though the hall's rule tells his run after theirs (his words on
        # hold v RACK 11:00, 2026-11-19: "How can hold have a decision point of whether to run or not when they already sent their earth ele 11s before? Wouldn't this
        # rather be described as hold sending an earth ele and RACK responding with air ele 11s later?")
        go = lambda g_: g_.get("off", g_["s0"]); fo = go(f)
        # Whoever set off first is sending and the other is answering, by however little: two runners gone within 2 s of one another were told from both sides,
        # the second time as a decision for the team that had already sent its runner (his mark on hold v RACK 3:58, incorrect, 2026-11-20: "a repeat of the
        # previous row" that "states a decision point for something that has already happened"). Runners gone in the same second are ordered by when the hall's
        # rule tells the run, then by team, so that the pair is still told once
        # ... and the two first flags, both brought from the gates, are neither one before the other: each team's first flag is told under the opening (R-520)
        first = lambda g_: not (g_["pregame"] and f["pregame"]) and (go(g_), g_["s0"], g_["tm"]) < (fo, f["s0"], f["tm"])
        earlier = next((g for g in mine if first(g) and g["e"] > w0 + 5), None)      # our flag already set off for when theirs sets off
        # a run of ours set off for while theirs is out: it is the answer to theirs when its runner turned for home before their flag went in, though the hall's rule
        # (R-461) reads the run itself a few seconds later (R-498: his mark on HC v Team 5:58, Classic: HC caps at 6:36, Team's Monk 5 sets off at 6:34 and leaves the
        # stand area at 6:40, "Team response with single run classic at 6:33")
        # ... and within this play's own clock: a flag of theirs that is held for minutes is answered by what we do in the FLAG_JOB_MAX_S the play runs, not by a run of
        # ours five minutes on (his mark on Men v Crew 5:52, Classic: Men's AoB Derv holds the flag until 11:36 and Crew's Water Ele sets off at 11:32: "crew does not run a flag")
        new = next((g for g in mine if not first(g) and go(g) <= min(w1, w0 + FLAG_JOB_MAX_S)), None)
        inhand = None
        if earlier:
            # in hand means close to the flag stand (his mark, TFS v 옷옷옷옷 1:40), and waiting there. A team that holds the stand cannot cap its flag until the other team
            # caps (R-483), so its flag at the stand is in hand; a team that does not hold the stand can cap on arrival, so its flag is in hand only if it is still uncapped
            # when theirs gets in, or the flag record reads it as held at the stand (R-400, R-407), or it is capped just before their boost (his mark, RJT v RACK 4:37).
            # A runner walking through the stand area to cap is a run begun first (his mark, RJT v RACK 6:32: "this is backwards; RJT is running, RACK responds")
            c = next((a for a in earlier["ids"] if M.carrying(a, w0) and M.AL[a][w0]), None)
            held = c is not None and M.place_at(c, w0)[0] in ("stand", "greater stand")
            to_boost = earlier["how"] == "captured" and earlier.get("cap_boost_in") is not None and earlier["cap_boost_in"] <= BOOST_LATE_S      # kept until just before their boost
            held = held and (M.st.stand_owner(w0)[0] == A or earlier["how"] != "captured" or earlier["e"] >= w1 or (earlier.get("held_s") or 0) >= HOLD_S or to_boost)
            if held: inhand = earlier
            elif earlier["how"] == "captured" or new is None:
                # we set off first: their run is the answer to ours and is told from their side (his mark, hdm v hook 7:07: "it's hdm's decision, hook starts running first").
                # Once ours is in, with theirs still on its way, we answer theirs in turn: we run again before it gets in, or we stay (his mark, RJT v RACK 6:32:
                # "RJT does not run again and does not answer run"); that decision is ours from our cap. A flag of ours still out when theirs gets in left us none
                if not (earlier["how"] == "captured" and earlier["e"] < w1): continue
                w0 = max(w0, earlier["e"])
                new = next((g for g in mine if g is not earlier and earlier["e"] - 2 <= g["s0"] and g.get("off", g["s0"]) <= min(w1, w0 + FLAG_JOB_MAX_S)), None)
                if w1 - w0 < 10: continue
            # else ours never gets in (carried off on a split, put down) and we set off again while theirs is out: that run is our answer
        theirs = "double run" if f["double"] else "single run"
        ours = "a flag already in hand" if inhand else "stay" if not new else "double run" if new["double"] else "single run"
        g = inhand or new
        who = [role[a] for a in dict.fromkeys(g["ids"])] if g else []
        # each side is named with what it does and who does it (his words on HC v Team: "Team single run (Monk 5 (WoC)); HC single run (Mes/A)", not "They ...")
        def both(x_, names):                                              # a double run is two players (R-472, R-485): one caps a flag while the other is already back for the next. Both are named (his words)
            if not x_["double"]: return names
            prev = max((y for y in FR if y["tm"] == x_["tm"] and y is not x_ and y["s0"] < x_["s0"] and (y.get("form") or "").startswith("double")), key=lambda y: y["s0"], default=None)
            if prev is not None and x_["s0"] - prev["e"] <= 60: return f"first runner {prev.get('capper') or prev['runner']}, capping the flag before; second runner {names}, back for this one"
            nxt = min((y for y in FR if y["tm"] == x_["tm"] and y is not x_ and y["s0"] >= x_["s0"]), key=lambda y: y["s0"], default=None)
            if nxt is not None and nxt["s0"] - x_["s0"] <= 10 and nxt["how"] == "captured" and nxt["e"] < x_["e"]:      # the two flags set off for together: the one capped first is the first runner's, and the player named here went back for the next (hold v Men 1:38: the Ritualist 1 and the AoB Derv cap at 2:03, the Hammer, back at the spawn, at 2:36)
                return f"first runner {carried(nxt)}; second runner {names}, back for the next flag"
            if nxt is not None: return f"first runner {names}; second runner {nxt['runner']}, back for the next flag"
            return names + "; no second runner found"
        def carried(x_):                                                  # who ran it, and who it was handed on to (a half run: "single run half run to stand mes", his words on 옷옷옷옷 v RACK 6:15)
            c = list(dict.fromkeys([x_["runner"]] + [role[a] for a in x_["ids"]]))
            return c[0] + (", handing it to " + " and ".join(c[1:]) if len(c) > 1 else "")
        mine_ = f" ({both(g, carried(g))})" if g else ""
        # a flag of ours only brought up with the team meanwhile is said, since it is no run and no stay either (R-505; his words on 옷옷옷옷 v RACK 0:00: "RACK
        # brings flag up on Warrior, but DOES NOT run the flag")
        bu = next((q for q in M.run_starts() if q["tm"] == A and M.not_run(q) and q["pickup"] <= w1 and any((c[2] is None or c[2] >= w0) and c[1] <= w1 for c in q["carries"] if c[0] in q["serious"])), None)
        up = bu and f"brings a flag up with its team ({', '.join(dict.fromkeys(role[c[0]] for c in sorted(bu['carries'], key=lambda c: c[1]) if c[0] in bu['serious'] and (c[2] is None or c[2] >= w0) and c[1] <= w1))}) but does not run it"
        said0 = f"{M.m.tag[B]} {theirs} ({both(f, carried(f))}{', to the Obelisk flag stand' if f['other_stand'] else ''})"
        said1 = f"{M.m.tag[A]} has a flag already in hand{mine_}" if inhand else f"{M.m.tag[A]} {up or 'stays'}" if not new else f"{M.m.tag[A]} {ours}{mine_}"
        scen = said0 + "; " + said1
        first_flags = not any(u < w0 + 1 for u, _ in M.st.caps)          # nobody has capped yet: each team's first flag (R-500)
        if not (f["pregame"] or (g and g["pregame"])) and first_flags: scen = "The opening. " + scen
        if f["pregame"] or (g and g["pregame"]):                         # the opening (R-479): each team's first flag is a run, and a player left at the spawn for the next one is part of the call
            back = lambda tm, x: [role[q["a"]] for q in M.run_starts() if q["tm"] == tm and q["pickup"] > 2 and q["set_off"] is None and q["waited"] is not None and q["waited"] < x["e"]]
            left = [f"{M.m.tag[tm]}'s {', '.join(back(tm, x))}" for tm, x in ((B, f), (A, g)) if x and x["pregame"] and back(tm, x)]
            # a team that brought no flag up at the opening and had to send a player back for its first one is said (his words, Men v hold 0:00: "hold did not bring
            # the first flag and had to send ele back for it. wasting over a minute of player time"); a second runner already named is not said again as left back
            late = [f"{M.m.tag[tm]} brought no flag up at the opening and sent {x['runner']} back for it" for tm, x in ((B, f), (A, g)) if x and not x["pregame"] and x is not inhand]
            left = [l for l in left if not any(f"second runner {nm}" in scen for nm in l.split("'s ", 1)[1].split(", "))]
            scen = "The opening. " + scen + (f"; left back for the next flag: {' and '.join(left)}" if left else "") + ("".join("; " + l for l in late))
        # our own run is judged from the decision to run to its cap; what follows the cap is another decision (R-471: TFS v 옷옷옷옷 3:26)
        ran = g is not None and not inhand
        end = min(g["e"], w0 + FLAG_JOB_MAX_S, T) if ran else min(w1, w0 + FLAG_JOB_MAX_S, T)
        d0 = min(max(g["s0"], w0), end) if ran else w0
        dA, dB = (lambda t1: K.died_main(A, d0, t1)), (lambda t1: K.died_main(B, d0, t1))      # deaths at the main fights only (R-466)
        bes = lambda t1: {"flag_lead": [K.lead(A, w0), K.lead(A, t1)], "deaths_at_the_main_fight": [dA(t1), dB(t1)], "deaths_anywhere": [K.died(A, w0, t1), K.died(B, w0, t1)], "their_flag": f["how"], "their_form": f["form"], "our_form": g and g["form"]}
        rid_ = lambda x_: f"{x_['tm']}-{canon[(x_['tm'], x_['s0'])]}"
        is_open = scen.startswith("The opening.")
        kw = dict(their=theirs, ours=ours, soh=bool(f["soh"] or (g and g["soh"])),
                  run_id=rid_(f), answer_id=rid_(new) if (new is not None and not inhand) else None,      # R-521: the run this play answers and the run it answers with, so that every run is told once on the page
                  said=[said0, said1],
                  **({"opening": opening(M)["words"]} if is_open else {}))
        # the position the answer is chosen from and what followed it on the fixed 90 and 180 s record (R-294), both read at the second the decision arises: what the
        # similar cases match on and are judged by (cases.py). The play's own clock ends at a cap, theirs for a stay and ours for a run, so it cannot be compared across calls
        # One clock (2026-11-19, the timing ladder; his word on the three faults it found): the reads of an answer (cases.py), the windows of `after` and the position
        # in `state` are all counted from one second, `anchor`. It is their runner's set-off (the second he turned for home, R-498), not the second the hall's rule
        # tells the run (R-461; that stays the play's own t0, the time on the page). Where our own runner was already out when theirs set off (`from_cap`), the
        # decision is ours only from our cap and is another decision, run again or not (R-546): its clock is our cap
        o_ = int(f.get("off", f["s0"]))
        from_cap = int(w0) > int(f["s0"]) + 2
        anc = int(w0) if from_cap else min(o_, int(w0))
        kw["state"], kw["after"] = M._state(A, anc), M.consequence(A, anc, FLAG_AFTER_S)
        # ... and the position FLAG_BEFORE_S before that second, read the same way, so that a call can be tested against what came before it (SPEC 5, rule 4: a call
        # that goes with the team's fortunes before it was made marks the situation and is no advice; 2026-11-19, the teams that sent nobody were already winning)
        b_ = anc - FLAG_BEFORE_S
        kw["before"] = None if b_ < 0 else {"state": M._state(A, b_), "after": M.consequence(A, b_, (FLAG_BEFORE_S,))[str(FLAG_BEFORE_S)]}
        # ... and the clock of the two runs, so that an answer can be read at a fixed second after theirs set off (his word, 2026-11-19: a run within 15 s of theirs is
        # not a run 45 s after it; and a "stay" read from having sent nobody before their run ended takes in every run of theirs that came to nothing): when their runner
        # set off and when their run ended; when our next runner set off, whenever that was; and how long their flag should take from here (to his spawn at a run, then
        # the usual carry for the hall and side; from where he stands when he already carries it)
        lead_ = lambda x_: list(dict.fromkeys(x_["ids"]))[:1]                # the player who sets off with it
        nxt_ = min((x_ for x_ in mine if (x_["s0"] >= w0 - 2 if from_cap else not first(x_))), key=go, default=None)
        a_ = next(iter(lead_(f)), None); u_ = min(anc, T); eta = None
        if a_ is not None and M.hall is not None and M.P[a_][u_]:
            if M.carrying(a_, u_): w_ = M.hall.walk(M.P[a_][u_], M.hall.stand); eta = w_ / CARRY_SPEED if w_ else None
            else:
                w_ = M.hall.walk(M.P[a_][u_], M.spawn[B]) if M.spawn.get(B) else None; us_ = _usual_arrival(M, B)
                eta = (w_ / RUN_SPEED + us_) if (w_ is not None and us_) else None
        kw["clock"] = {"their_off": int(f.get("off", f["s0"])), "their_end": int(f["e"]), "their_eta_s": eta and round(eta), "our_off": nxt_ and int(nxt_.get("off", nxt_["s0"])), "our_s0": nxt_ and int(nxt_["s0"]), "our_double": bool(nxt_ and nxt_["double"]),
                       "our_end": nxt_ and int(nxt_["e"]), "our_how": nxt_ and nxt_["how"], "anchor": anc, "from_cap": from_cap,
                       "their_waited_back": f.get("waited") if f.get("waited_back") else None, "their_pick": int(f["pick"]),
                       "cap_over": (lambda own_: int(own_[1]) if from_cap and own_[0] == B and not any(h == A and u < w0 - 2 for u, h in M.st.caps) else None)(M.st.stand_owner(max(int(w0) - 2, 0)))}
        # (`their_waited_back`: their runner had waited back at his flag spawn since the gates, from that second, and did not set off; `their_pick`: when he took the
        # flag up; `cap_over`: our cap is our first flag of the match and goes in over theirs, in since that second: they capped first)
        # the answer to a run is never before the run (R-460: a fault here stops the run; the mirror card of 2026-11-19 came back once)
        if not from_cap and kw["clock"]["our_off"] is not None and kw["clock"]["our_off"] < o_ and not (f["pregame"] and nxt_["pregame"]):      # (the two first flags, from the gates, are the opening's)
            raise ValueError(f"flag play of team {A} at {w0}: its runner set off at {kw['clock']['our_off']}, before theirs at {o_}, yet he is told as the answer")
        # ... and our own flag already up the field at that second, carried or lying where it was put down (his word on Men v hold 2:07): said on the card; the
        # play stays what he graded it (a stay), and whether such a spot belongs with the flag in hand is his to rule
        kw["our_flag_up"] = None if inhand else M.flag_up(A, min(anc, T))
        # ... and the raw record on one clock, their runner's set-off, for the check of the readings themselves (his word, 2026-11-19: do the run, stay and timing
        # readings go with flag advantage; `cases.py ladder`): the flag lead (R-408) and the holder of the stand at fixed seconds from it, and the second of every cap
        # and every morale boost in the FLAG_TRACK_FOR that follow, by side. `told_after` is the seconds from it to the play's own t0 (the second the run is told by the
        # hall's rule, R-461, or our own cap when we ran first), and `run_told_after` the part of it that is the hall's rule. Nothing here is matched on or judged by
        side_ = lambda h: "own" if h == A else "theirs"
        kw["track"] = {"told_after": int(w0) - o_, "run_told_after": int(f["s0"]) - o_, "left_s": int(T) - o_, "at": list(FLAG_TRACK_S),
                       "lead": [M.lead_value(A, o_ + h) if o_ + h <= T else None for h in FLAG_TRACK_S],
                       "stand": [(lambda h_: "own" if h_ == A else "theirs" if h_ == B else "nobody")(M.st.stand_owner(o_ + h)[0]) if o_ + h <= T else None for h in FLAG_TRACK_S],
                       "caps": [[int(u) - o_, side_(h)] for u, h in M.st.caps if o_ < u <= o_ + FLAG_TRACK_FOR],
                       "boosts": [[int(u) - o_, side_(h)] for u, h in M._boosts() if o_ < u <= o_ + FLAG_TRACK_FOR]}
        # ... and what else a team can see at that second (R-539: a build is a fixed state, never a call, but it bears on which call is right): who their runner is and who
        # ours is, as properties (a backline monk away is not a warrior away); where each main team stands, as a step on its ladder; each whole team's snares and speed
        if getattr(M, "_team_props", None) is None: M._team_props = {k: M._props(list(M.st.players[k])) for k in M.st.teams}
        kw["their_runner"] = dict(M._props(lead_(f)), role=f["runner"])
        kw["our_runner"] = dict(M._props(lead_(g)), role=g["runner"]) if (g is not None and not inhand) else None
        kw["steps"] = [M._main_step(A, int(w0))[0], M._main_step(B, int(w0))[0]]
        kw["teams"] = {k: [M._team_props[A][k], M._team_props[B][k]] for k in ("snare", "speed", "self_defence")}
        if ours == "a flag already in hand":
            # R-486: the flag in hand is a timing choice. When their flag gets in, the team with a flag in hand overcaps at once, or holds it and plays on with eight
            # (in position at the stand, or with the carrier kept in the fight: "do we GET in position to overcap or do we use the 8v7/8v8 time to hold the flag; and
            # if we do get in position, do we cap instantly or do we hold?"). A hold is judged by what the time bought and by whether it gave up a boost, on its own
            # clock: from their cap to ours, or to their boost, or to where our flag was put down
            caps_b = K.caps(B, w0, w1 + 1)
            tc = caps_b[-1] if caps_b else None
            ans = tc is not None and bool(K.caps(A, tc - 1, tc + ANSWER_CAP_S))
            u = min(int(tc), T) if tc is not None else None
            c = next((a for a in g["ids"] if M.AL[a][u] and M.carrying(a, u)), None) if tc is not None else None
            if tc is None or ans:
                t1 = min(w1 + ANSWER_CAP_S, T)
                if tc is not None: kw["hand"] = "overcap at once"; scen += ", capped at once"; kw["said"][1] += ", capped at once"
                out.append(_play(M, "flag", "own", A, w0, t1, who, scen, "Answer their cap at once", {},
                                 any_of={"their flag does not get in": not caps_b, f"our cap follows theirs within {ANSWER_CAP_S} s": ans}, beside=bes(t1), **kw))
            elif c is None:
                # no flag of ours in hand any more when theirs gets in: capped first (the team did not hold the stand and took it; kept to just before their boost, that
                # is the timing of R-400 and R-407), or put down
                t1 = min(w1 + ANSWER_CAP_S, T)
                first = g["how"] == "captured" and g["e"] <= tc
                owner, since = M.st.stand_owner(max(g["e"] - 1, 0))
                pre = first and owner == B and (BOOST_EVERY - (g["e"] - since) % BOOST_EVERY) <= BOOST_LATE_S
                kw["hand"] = "capped before theirs got in" if first else "put down before theirs got in"
                scen += ", capped before theirs got in" if first else ", put down before theirs got in"
                kw["said"][1] += ", capped before theirs got in" if first else ", put down before theirs got in"
                out.append(_play(M, "flag", "own", A, w0, t1, who, scen, "Cap just before their boost, or keep the flag for their cap", {"our cap lands just before their boost": bool(pre)}, beside=bes(t1), ruled=False, **kw))
            else:
                placed = d(M.P[c][u], M.hall.stand) < STAND_R          # in position to overcap: at the stand itself, not somewhere in the stand area (RJT v RACK 2:30: RACK's Stand Mes, a long way from it, "is not in position to overcap")
                ours_cap = g["e"] if g["how"] == "captured" and g["e"] > tc else None
                their_boost = next((v for v, h in M._boosts() if h == B and v > tc), None)
                t1 = int(min(x for x in (ours_cap, their_boost, g["e"] if g["e"] > tc else None, tc + FLAG_JOB_MAX_S, T) if x is not None))
                kw["hand"] = "in position, hold" if placed else "hold, not in position to overcap"
                held_for = (ours_cap or t1) - tc
                scen += (", held in position at the stand" if placed else ", held, its carrier not in position to overcap") + (f" (capped {int(held_for)} s after theirs)" if ours_cap else " (not capped)")
                kw["said"][1] += (", held in position at the stand" if placed else ", held, its carrier not in position to overcap") + (f" (capped {int(held_for)} s after theirs)" if ours_cap else " (not capped)")
                hA, hB = K.died_main(A, tc, t1), K.died_main(B, tc, t1)
                b_ = dict(bes(t1), held_s=int(held_for), in_position=bool(placed), deaths_while_held=[hA, hB], their_boost_landed=bool(their_boost is not None and their_boost <= t1 and (ours_cap is None or their_boost < ours_cap)))
                out.append(_play(M, "flag", "own", A, w0, t1, who, scen, "Hold the flag and play on with eight: give up no boost, and lose no more players than they do while it is held",
                                 {"our flag is capped before their boost lands": ours_cap is not None and (their_boost is None or ours_cap <= their_boost), "no more of ours die at the main fight than of theirs while it is held": hA <= hB},
                                 beside=b_, ruled=False, **kw))
        elif ours == "stay":
            # A team that runs no first flag carries no stay job at the opening (R-565; his mark on Men v NwAy 0:00, Classic, the call incorrect: "they don't have 2
            # extra players"): the first flag walks up with their team, so nobody is away for it, and the team that brought none may have nobody at the stand at all
            # (NwAy: four out by the back door, four at home). Its job is the opening's, get the first flag in (`opening_plays`, R-500); what it did instead is told
            # and judged by its own rows (the split). The opening is another decision than the answer to a run (R-541)
            if f["pregame"] and first_flags: continue
            t1 = w1                                                      # the decision to stay ends when their flag is in (his mark, HC v Team 2:57, Classic: "should end when they cap"); the 10 s tail was Claude's
            job = "Kill with the two extra players before their flag is in" if f["double"] else "Kill with the extra player while their runner is away"
            out.append(_play(M, "flag", "own", A, w0, t1, [], scen, job + ", or their flag does not get in", {},
                             any_of={"more of theirs die at the main fight than of ours": dB(t1) > dA(t1), "their flag does not get in": f["how"] != "captured"}, beside=bes(t1), **kw))      # R-467: staying costs nothing if their flag fails
        elif (ours == "double run") == f["double"]:                      # single against single, double against double
            lv = K.lead(A, end)
            if first_flags and not f["double"]:      # R-500: at the opening nobody has a flag capped and nobody is behind on flags (his words on HC v Team 0:03): the job is the first flag, with no test of the flag lead or of deaths
                out.append(_play(M, "flag", "own", A, w0, end, who, scen, "Get the first flag in", {"our flag is capped": new["how"] == "captured"}, beside=bes(end), **kw))
                continue
            out.append(_play(M, "flag", "own", A, w0, end, who, scen, "Get the flag in, lose no more players than they do, and end no worse than half a flag behind",
                             {"our flag is capped": new["how"] == "captured", "no more of ours die at the main fight than of theirs": dA(end) <= dB(end),
                              "no worse than half a flag behind at the end, or no further behind than at the start": lv is None or lv >= -LEAD_HALF or (K.lead(A, w0) is not None and lv >= K.lead(A, w0))}, beside=bes(end), **kw))      # a run cannot answer for a deficit it started with (his mark, TFS v 옷옷옷옷 3:26; R-426: going less negative counts)
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
def _push_not_split(M, x, p):
    """Whether a split attempt x is the push p on a flagger and no split (his marks, Men v RACK 0:36 and 1:32, HC v Team 4:24,
    HC v cope 3:24: "this is a flag push rather than a split"): its players came to a flagger already on his run (going back,
    at his spawn or carrying), were on him within SPLIT_GAP_S of crossing, and left the enemy's ground within SPLIT_GAP_S of the
    push ending: they were there for the flag. Players who stay on after the flag has gone, or who die there, are a split whose defender carries his flag (R-430;
    HC v cope 0:20 and 0:32, Classic: "the lone defender carries his flag"; TFS v 옷옷옷옷 6:20)."""
    if x["tm"] != p["tm"] or set(p["ids"]) != set(x["ids"]) or x.get("end") != "left": return False      # every player who went is on the flagger
    if not (x["t_in"] - JOIN_S <= p["t"] <= x["t_in"] + SPLIT_GAP_S and x["t1"] <= p["t1"] + SPLIT_GAP_S): return False      # on him within SPLIT_GAP_S of crossing, gone within SPLIT_GAP_S of the push ending
    b, u = p["flagger"], int(p["t"]) - int(p["t"]) % SPLIT_STEP
    near = lambda v: bool(M.AL[b][v]) and any(M.AL[a][v] and M.P[a][v] and d(M.P[a][v], M.P[b][v]) < FIGHT_LINK for a in p["ids"])
    while u - SPLIT_STEP >= 0 and near(u - SPLIT_STEP): u -= SPLIT_STEP
    return bool(M._flagger(b, 3 - p["tm"], u))


def _split_on_carrier(M, p, splits):
    """A split player on a defender who carries his flag is a split with a part-run (R-430), not a push on a flagger (his mark, TFS v 옷옷옷옷 6:20),
    unless its players came for the flagger and left when the flag had gone (R-530)."""
    tm = p["tm"]
    return any(x["tm"] == tm and x["t_in"] <= p["t"] <= x["t1"] + 4 and set(p["roles"]) <= {q["role"] for q in x["members"]} for x in splits) and not any(_push_not_split(M, x, p) for x in splits)


def push_plays(M, K):
    FR, out, role, done = _flag_rows(M), [], M.m.roles, {}
    splits = [x for x in M.attempts() if x["kind"] == "split"]
    for p in M.flag_pushes():
        tm, foe = p["tm"], 3 - p["tm"]
        # a split player on a defender who carries his flag is a split with a part-run (R-430), not a push on a flagger (his mark, TFS v 옷옷옷옷 6:20)
        if _split_on_carrier(M, p, splits): continue
        f = next((f for f in FR if f["tm"] == foe and p["flagger"] in f["ids"] and f["s0"] - 60 <= p["t"] <= f["e"] + 2), None)
        key = (foe, f["pick"]) if f else (foe, p["t"])
        if key in done:                                                   # a second push on the same flag: one play, everyone who pushed
            q = done[key]
            for r in p["roles"]:
                if r not in q["who"]: q["who"].append(r)
            continue
        usual = _usual_arrival(M, foe)
        arrive = ((f["e"] - f["held_s"]) - max(f["pick"], f["s0"]) + (p["delay_s"] or 0)) if f and f["how"] == "captured" else None      # from when the flag is taken out: a flag kept at home before its run was not made late by the push (his mark, hook v hold 5:40: "a very very fast cap")
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
    # (a short stretch joins the numbers it turns into as well as those it came from: the seconds in which a fight is forming are part of that fight. His marks,
    # Men v Apes 1:02, "four defenders, and one split", and hook v hold 12:47. Telling each numbers only from the second it was first true was tried on
    # 2026-11-15 and failed both rows)
    return [tuple(r) for r in runs]


def split_plays(M, K):
    st, m, T, out, tl, S_ = M.st, M.m, M.T, [], M._tl(), SPLIT_STEP
    M._split_at = []                                                     # who each told phase counts, second by second (the self-check, R-488)
    role, hall = m.roles, M.hall
    A = [x for x in M.attempts() if x["kind"] == "split" and x.get("solo") != "other"]
    pushed = {id(x) for x in A if any(_push_not_split(M, x, p) for p in M.flag_pushes())}      # players who came for a flagger on his run and left when the flag had gone: the push on the flagger, told there (the record still ends the attempt before it)
    is_monk = lambda a: m.A[a].get("p") == "Monk" and not role[a].startswith("Monk ") and "WoC" not in role[a]      # a backline monk; a smiter (the WoC monks, whatever their slot) is damage (R-457; TFS v 옷옷옷옷 4:06)
    for x in A:
        if id(x) in pushed: continue
        tm, foe, an = x["tm"], 3 - x["tm"], x["answer"]
        own_d = st.side.get(foe)
        frm = {a: int(q["from"]) for a, q in zip(x["ids"], x["members"])}
        to = {a: int(q["to"]) for a, q in zip(x["ids"], x["members"])}
        on_ground = lambda a, u: M.AL[a][u] and (M._deep(a, u - u % S_) is not None or M.held_out(tm, a, u - u % S_))      # on the enemy's ground, or out of his own base while it is held in (R-506)
        held = lambda a, u: any(on_ground(a, v) for v in range(max(u - FIGHT_HOLD_S, 0), min(u + FIGHT_HOLD_S, T) + 1, S_))      # on the enemy's ground a few seconds either side
        # on the split: on the enemy's ground, or standing with a player of the split who is, or was a few seconds either side: its back line (a monk or a mesmer a
        # little behind the players he came with; his marks, RJT v RACK 3:10 and 8:00), and a split that steps back off the ground together for a moment. A player on
        # his own gets no such hold (Men v Apes 2:30: a Mesmer crossing the field alone is not on the split, and the Prot who follows him is not defending it).
        # The 12 s of R-350 below still decides who is a player more and who was brief support (RJT v RACK 5:30: "really a 3v3")
        deep = lambda a, u: bool(M.AL[a][u] and M.P[a][u]) and (on_ground(a, u) or any(b != a and M.AL[b][u] and held(b, u) and d(M.P[a][u], M.P[b][u]) < FIGHT_CLOSE for b in x["ids"]))
        # a chase is not a split: players following an enemy split out of their own base, who never reach a door (Denning, NwAy v hook 3:04: the split is hook's, chased out, and its Air Ele dies at 3:48)
        # (it sets off while that split is still out and takes no NPC: hdm v 옷옷옷옷 3:46 is a split of its own, after theirs had gone home, and takes an archer; review key s1-26)
        chased = next((y for y in A if y["tm"] == foe and y["t_in"] <= x["t_in"] <= y["t1"] + 4 and x["where"] == "field" and not x["npcs"]
                       and len(set(x["ids"]) & (set(y["answer"]["ids"]) | set(y["answer"].get("went_back_ids") or []))) * 2 >= len(x["ids"])), None)
        if chased is not None: continue
        # follow its players for as long as they stay on the enemy's ground, past the record's own end (the label can change under them: a split that becomes the only players left, or is renamed a push)
        # ... but not once its main team has come to it: then it is a main team push, and the split is over (his marks on Men v Apes: "not a split" from 3:10 to 7:00 and from 8:28 to 11:16, where the record itself had ended "main team joined")
        # three or more of the rest of his team are with him; or two of them are, and with them he stands in a group of five or more of his team: the larger part of
        # the team is at the split, and it is the main team's push from there (R-487; his marks on HC v Team 13:20 to 14:06, "this is mainteam pushing backdoor": two more
        # of HC join the four at Team's back door). The engine's own main team label is not asked: where it is wrong a split would end with it (xxx v Men 2:36)
        mates = [b for b in st.players[tm] if b not in x["ids"]]
        # Who is on a split is who is there at that moment, not everyone it ever had (R-439), and so is who the rest of his team is when it comes to the split: a
        # player who went home from it is of the rest, though the record lists him (one still to come to it is not: he set out with it, a step behind). Men v
        # hold 9:18 to 11:46: one record of six of Men, the Hammer and the Ranger at hold's front door, the Ranger home at 9:54, and five by the back door from
        # 10:18; the rest of the team was read as the two who never were in it, so that no three of the rest could come to the split, and the Hammer was read on
        # a split of one against hold's whole team, in hold's pit beside Men's main team, until 11:46 (his mark: "warrior is just jointing the mainteam fight that
        # is now in pit"). xxx v NwAy 12:20: NwAy's Hammer comes to its five at xxx's front door and its main team holds xxx in its base from there (his mark on the
        # row, "correct identification"), where the five were read as a split for 80 s more
        team_ = [b for b in st.players[tm]]
        joined = lambda a, u, rest: M.with_rest(a, rest, u) or (M.with_rest(a, rest, u, need=2) and M.with_rest(a, [b for b in team_ if b != a], u, need=MAIN_BIG - 1))
        end, gap, stopped = dict(to), dict.fromkeys(x["ids"], 0), set()      # each player followed past his own end in the record, all of them second by second together
        v = min(to.values())
        while v + S_ <= T and any(a not in stopped for a in x["ids"]):
            v += S_
            rest = [b for b in team_ if b not in frm or b in stopped]      # those who never were on it and those who have left it; a player still to come to it is coming with it
            for a in [a for a in x["ids"] if a not in stopped and to[a] < v and end[a] == v - S_]:
                if gap[a] > SPLIT_GAP_S or joined(a, v, rest): stopped.add(a); continue
                end[a] = v
                gap[a] = 0 if deep(a, v) else gap[a] + S_
            stopped |= {a for a in x["ids"] if a not in stopped and to[a] < v and end[a] < v}
        ext = {a: end[a] - gap[a] for a in x["ids"]}
        nxt = min((y["t_in"] for y in A if y["tm"] == tm and y["t_in"] > x["t_in"] and set(y["ids"]) & set(x["ids"])), default=T + 1)
        t0, t9 = int(x["t_in"]) - int(x["t_in"]) % S_, min(max(ext.values()), nxt - S_, T)
        times = list(range(t0, t9 + 1, S_))
        if len(times) < 3: continue
        hop = lambda a, u: any(0 <= v - S_ and v <= T and M.P[a][v] and M.P[a][v - S_] and d(M.P[a][v], M.P[a][v - S_]) > GROUND_JUMP for v in (u, u + S_))      # just through a teleporter
        # A defence that turns into a split is told from the last turn-off, not from the crossing (Denning, 2026-11-21). Players who go out after the split they
        # defended, still on it or not, could yet turn through mid to their main team, to a flag or to the front door: "Before they cross, we don't really know
        # (in game) whether they are going to continue through mid to join main or run a flag or push front door or if they are going to push back door as a split.
        # When they cross the 'alternative' path, we know there is nothing else they could be doing by running that way so we know it's now an offensive split"
        # (Men v hold 10:24, "they are just running into backdoor, no split yet": four who had defended hold's split chase it over the half-way line, kill its Fire
        # Ele there at 10:28 and run on; he times the split at about 10:36, "where the most forward player of the split crosses the path that by clicking would
        # have gone to the collapse route/mid"). A player who was not defending is read as before, from the crossing or from his leaving (the Ranger of Men v RACK
        # 13:52: "there is nothing else he could be doing that way"). Read as: the players of the record who were defenders of an enemy split still out, or over
        # for no longer than SPLIT_GAP_S, when they joined it; while they are half or more of those on the enemy's ground nobody is on the split until one of its
        # players has passed the last turn-off to mid (`Hall.past_turnoff`), and if none does, it never was a split
        def was_defending(a, y):                          # he had come to that split's defence, or gone home for it, before he joined this one
            an = y["answer"]
            came = min((ta for ta, r_ in an.get("arrivals") or [] if r_ == role[a]), default=None) if a in an["ids"] else None
            if came is None and a in (an.get("went_back_ids") or []): came = an.get("went_back_t")
            return came is not None and came <= frm[a]
        dturn = {a for a in x["ids"] if any(y["tm"] == foe and y["t_in"] <= frm[a] <= y["t1"] + SPLIT_GAP_S and was_defending(a, y) for y in A)}
        wait = None
        if dturn and hall is not None:
            g0 = min(frm[a] for a in dturn); g0 -= g0 % S_
            there_ = lambda u: [a for a in x["ids"] if frm[a] <= u <= ext[a] and deep(a, u)]
            passed = next((u for u in range(g0, t9 + 1, S_) if any(hall.past_turnoff(M.P[a][u], own_d) for a in there_(u))), t9 + S_)
            # ... or it is in a fight of its own there: enemy players on it for JOIN_S (R-350) on the enemy's ground are a split fight wherever it stands (R-365),
            # and it is told from when that began (Crew v True 1:00, four who met True's split at home and fought it 4 v 4 on True's back path for 88 s; RACK v OG
            # 15:54). A few seconds of hitting a player they are chasing down is not that (Men v hold 10:23 to 10:28, the Fire Ele)
            def fought(u):
                T_ = there_(u)
                return any(M.AL[b][u] and M.P[b][u] and M.fight_side(b, u) != "main" and any(d(M.P[b][u], M.P[a][u]) < FIGHT_LINK or (d(M.P[b][u], M.P[a][u]) < FIGHT_ACT and ((a, b) if a < b else (b, a)) in M._acting(u, aid=False)) for a in T_)
                           for b in st.players[foe])
            us_, run_ = list(range(g0, min(passed, t9) + 1, S_)), 0
            for i_, u in enumerate(us_):
                run_ = run_ + 1 if fought(u) else 0
                if run_ * S_ >= JOIN_S: passed = min(passed, us_[i_ - run_ + 1]); break
            wait = (g0, passed, there_)
        waiting = lambda u: wait is not None and wait[0] <= u < wait[1] and len([a for a in wait[2](u) if a in dturn]) * 2 >= max(len(wait[2](u)), 1)
        raw = lambda a, u: frm[a] <= u <= ext[a] and deep(a, u) and not waiting(u) and not hop(a, u) and not M.with_rest(a, mates, u) and M.fight_side(a, u) != "main"      # not while he stands in the fight the rest of his team is in, nor while he is in the main fight by whom he trades with (R-519)
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
        at_main = lambda b, u: M.with_rest(b, mates, u)   # an enemy standing among three or more of the attackers' other players is at the main fight, not on the split's defence
        pit_way = M.hall.to(M.hall.lord[own_d]) if M.hall is not None and own_d in M.hall.lord else {}
        to_pit = lambda p: pit_way.get(M.hall.snap(p), 1e9)
        # Who killed him was on him: an enemy who hit a split player in the seconds before he died there counts on the split then, wherever he stands (R-519: a
        # player is counted in the fight of those he trades with before the fight of those he stands with). Without it a main team that falls back onto a split
        # and kills it in passing was read as never having touched it (his words on NwAy v ohno 5:24 and QenK v Fun 6:37, picked rows: "both mainteam collapses
        # and should be read as such": ohno's main team, pushed back to its front door, kills the Dervish in its pit in 6 s; the row was 1 v 1 against the 8 Monk)
        # Only one who came from his main team's fight: a player who had just resurrected at his base onto the split has not collapsed on it (his words on Team v
        # BcS 18:11: "not a collapse, the split just had a bunch of people base res on him and he died")
        def with_main(b, td):                             # he stood with his main team, away from home, in the 45 s before (as a collapser is told from a defender, R-429), and has not died since
            lo = max((int(x_) for x_ in st.death_times.get(b, []) if x_ <= td), default=-1)
            return any(u > lo and M.AL[b][u] and b in M.main_team(foe, u) and len(M.main_team(foe, u)) >= 3 and not (M.place_at(b, u)[1] == own_d and M.place_at(b, u)[0] in HOMEG)
                       for u in range(max(int(td) - 45, 0) // S_ * S_, max(int(td) - JOIN_S, 0) + 1, S_))
        # (asked only of the deaths that end the split: a main fight beside a split, some of whose players turn their damage on it for a moment while it goes on,
        # is not read anew by this)
        foes_all, killers = set(st.players[foe]), {}
        last_on = next((s_ for s_ in reversed(Ss) if s_), [])
        ends_dead = times[-1] < T - S_ - 1 and bool(last_on) and all(any(times[-1] - 2 <= td <= times[-1] + 4 for td in st.death_times.get(a, [])) for a in last_on)
        for a in (last_on if ends_dead else ()):
            for td in st.death_times.get(a, []):
                if times[-1] - 2 <= td <= times[-1] + 4:
                    for u_ in range(max(int(td) - FIGHT_HOLD_S, 0), int(td) + 1):
                        for x_, y_ in M.hits.get(u_, ()):
                            if y_ == a and x_ in foes_all and with_main(x_, td): killers.setdefault(x_, set()).add(int(td))
        killing = lambda b, u: any(td - FIGHT_HOLD_S - S_ < u <= td + S_ for td in killers.get(b, ()))
        def defends(b):                                   # a defender is on the split: within reach of a split player, or further off with one of them hitting or casting on the other (Moments' reading of who is in a fight, without the hold: a player hovering at the edge of reach is not defending, 옷옷옷옷 v Men 6:50); for 12 s, or at a death (his own, or the split player's: R-464)
            def on(a, u):
                dist = d(M.P[b][u], M.P[a][u])
                return dist < FIGHT_LINK or (dist < FIGHT_ACT and ((a, b) if a < b else (b, a)) in M._acting(u, aid=False))
            # R-512: defending a split is keeping it from what it came for. A player on his own ground who stands in his pit, or between the split and his pit NPCs, is
            # defending it though nobody has hit anybody: the split cannot take NPCs past him, and it is holding him there ("they are PREVENTING THE SPLIT FROM
            # ACCOMPLISHING THEIR OBJECTIVE. They are standing sometimes in pit, sometimes fighting with NPCs, sometimes just standing (without fighting) between the
            # split and their goal"; Men v hold 0:48 to 5:30). Read as: he is on his own ground, the split stands on his side of the hall, his walk to his own Lord
            # is no longer than the walk of the nearest split player to it, and it is the split he faces: no group of the attackers' other players (two or more of them
            # together) is nearer to him than the split is ("Position is not just absolute": a player fallen back to his own footmen in front of the enemy's main team
            # is at home and near his pit, but he is there for the main team, hdm v hook 7:12, hook's Mesmer; one enemy walking up alone draws nobody off the defence,
            # Men v hold 10:48, "5 players defending")
            def blocks(u, s):
                if not (M.place_at(b, u)[1] == own_d and M.place_at(b, u)[0] in HOMEG): return False
                there = [a for a in s if M.AL[a][u] and M.P[a][u] and M.place_at(a, u)[1] == own_d]
                if not there or to_pit(M.P[b][u]) > min(to_pit(M.P[a][u]) for a in there): return False
                up = [m for m in mates if M.AL[m][u] and M.P[m][u]]
                front = [m for m in up if any(n is not m and d(M.P[m][u], M.P[n][u]) < FIGHT_LINK for n in up)]
                return min(d(M.P[b][u], M.P[a][u]) for a in there) <= min((d(M.P[b][u], M.P[m][u]) for m in front), default=1e9)
            reach = [bool(M.AL[b][u]) and bool(M.P[b][u]) and (((any(M.AL[a][u] and on(a, u) for a in s) or blocks(u, s)) and not at_main(b, u)) or killing(b, u)) and M.fight_side(b, u) != "main" for u, s in zip(times, Ss)]
            return M.visits(times, reach, reach, list(st.death_times.get(b, [])) + split_deaths, to_end=at_end0)      # a defender kites and heals at range: being on the split is enough
        at_end0 = times[-1] >= T - S_ - 1
        d_on = {b: defends(b) for b in st.players[foe]}
        Ds = [[b for b in st.players[foe] if d_on[b][i]] for i in range(len(times))]
        # its numbers change only when a player's stay on it starts or ends (each stay is JOIN_S or longer, R-350), and a change is told only if it lasts JOIN_S
        # (R-488: "if a 4v4 turns into a 3v4 for 3s and then a 4v4 again, it doesn't really matter"): no smoothing of the counts over that
        kn = [(len(s), len(dn)) for s, dn in zip(Ss, Ds)]
        # it counts from when it can do something: at their footies, in their base or pit, or met by a defender (Denning, Book v One 18:54: "when the split actually reaches base/NPCs")
        reach = next((u for u, s, dn in zip(times, Ss, Ds) if dn or any(M.place_at(a, u)[0] in ("pit", "base", "front footies", "back footies") for a in s)), None)
        # ... but the decision is the crossing (R-458), and that is when the other team sees it and has to answer (his marks on Men v RACK, Classic: the Ranger's
        # solo splits at 10:44 and 13:52, "split starts at 13:52, that's when Men would see and have to respond", and the Mes/A's at 16:51; the rows began at 11:54,
        # 14:38 and 18:06, when a defender met them): a split is told from the second it stands on the enemy's side
        reach0 = reach                                    # when it can do something: said in the row, so that a split still on its way is not read as one that took nothing (his note on Book v One 18:54: "see when the split actually reaches base/NPCs")
        reach = next((u for u, s_ in zip(times, Ss) if s_), reach)
        out0 = next((u for u, s_ in zip(times, Ss) if any(M.held_out(tm, a, u) for a in s_)), None)      # a split out of a held base counts from when it leaves: the enemy has to deal with it at once (R-506)
        if out0 is not None and (reach is None or out0 < reach): reach = out0
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
        runs_ = _runs(kn, times, JOIN_S, keep_last=at_end)
        # ... and so do the seconds in which it is killed, where it had not been outnumbered until then and players then come to it from their main team's fight
        # and kill it: a collapse that kills within seconds is a collapse (a death in it counts at once, as for who is on it). All who came must have come from
        # their main team's fight, none by the base res (Team v BcS 18:11: four of BcS resurrect onto the Ritualist in their pit, "not a collapse")
        killed_end = False
        if ends_dead and runs_ and 0 < runs_[-1][0][0] and runs_[-1][0][1] <= runs_[-1][0][0]:
            i0 = len(times)
            while i0 - 1 >= 0 and times[i0 - 1] > runs_[-1][1] and kn[i0 - 1][0] > 0 and kn[i0 - 1][1] >= kn[i0 - 1][0] + 1: i0 -= 1      # the readings at its end in which the defence is a player or more up (R-441)
            if i0 < len(times):
                was_ = {b for i, u_ in enumerate(times) if runs_[-1][1] <= u_ < times[i0] for b in Ds[i]}
                new_ = {b for i in range(i0, len(times)) for b in Ds[i] if b not in was_}
                if new_ and all(with_main(b, times[-1]) for b in new_):
                    runs_ = runs_[:-1] + [(runs_[-1][0], runs_[-1][1], times[i0 - 1]), (collections.Counter(kn[i0:]).most_common(1)[0][0], times[i0], times[-1])]
                    killed_end = True
        phases = [(v, max(a_, reach), b_) for v, a_, b_ in runs_ if v[0] > 0 and b_ >= reach and (b_ - max(a_, reach) + S_ >= JOIN_S or ((at_end or killed_end) and b_ == times[-1]))]
        # R-508: a full collapse counts from the turn, whether or not the team reaches the split ("it's the turn that matters ... when I (in a game) would be able to
        # recognize they are going to collapse so likely a few seconds after the turn"; his four rows of 옷옷옷옷 v RACK: the engine read 1:51 and 6:01 at arrival, 15 and
        # 27 s late, and not at all 4:39 and 8:16, where the team leaves RACK's base after RACK's five and does not reach them). A defender is making for the split when
        # he is TURN_CLOSE nearer, over 4 s, to where it stood 4 s before (his own move: a split running toward him is not his turn; a walk through a teleporter is). The
        # team has turned when five or more make for it (as "five or more gone back for it"), or all the team but one are on it or making for it, for TURN_S; the full
        # collapse is told from TURN_S after the turn began. A team driven home by the split's own main team has not turned (R-358, as for those who went back).
        heads = []
        for u, s_ in zip(times, Ss):
            near, closing = [], []
            if s_ and u >= 4:
                was = [M.P[a][u - 4] for a in s_ if M.AL[a][u - 4] and M.P[a][u - 4]]
                driven = bool(M._over(tm, u)[1])
                for b in st.players[foe]:
                    if not (M.AL[b][u] and M.P[b][u]) or at_main(b, u): continue
                    if any(M.AL[a][u] and M.P[a][u] and d(M.P[b][u], M.P[a][u]) < FIGHT_LINK for a in s_): near.append(b)
                    elif was and not driven and M.AL[b][u - 4] and M.P[b][u - 4] and min(d(M.P[b][u - 4], q) for q in was) - min(d(M.P[b][u], q) for q in was) >= TURN_CLOSE: closing.append(b)
            heads.append((near, closing))
        alive_at = lambda u: sum(1 for b in st.players[foe] if M.AL[b][u])
        turned = [len(c_) >= 5 or (bool(c_) and len(n_) + len(c_) >= max(6, alive_at(u) - 1)) for u, (n_, c_) in zip(times, heads)]
        turns, i_ = [], 0
        while i_ < len(times):
            if not turned[i_]: i_ += 1; continue
            j_ = i_
            while j_ + 1 < len(times) and (turned[j_ + 1] or (j_ + 2 < len(times) and turned[j_ + 2])): j_ += 1
            if times[j_] - times[i_] >= TURN_S and times[i_] + TURN_S >= reach:
                q1 = next(q for q in range(i_, j_ + 1) if times[q] >= times[i_] + TURN_S)      # who turned: those making for it, and those on it, up to the second it is told
                turns.append({"t0": times[i_], "told": times[i_] + TURN_S, "t1": times[j_], "ids": list(dict.fromkeys(b for q in range(i_, q1 + 1) for b in heads[q][1] + heads[q][0]))})
            i_ = j_ + 1
        wb = set(an.get("went_back_ids") or [])
        # a split fight is told once (R-365; his marks on hdm v hook, "still the same split", and his agreement of 2026-11-14): neighbouring phases in which it is
        # defended and nobody collapses on it are one situation, with the numbers it had for longest and each change of them told beside it. It is cut only where
        # the kind of answer changes: nobody defending, defended, a collapse, the whole team
        def kind_of(i_, ph):
            (k_, n_), a_, b_ = ph
            if n_ == 0: return "nobody"
            if (n_ >= max(6, sum(M.AL[b][(a_ + b_) // 2 // S_ * S_] for b in st.players[foe]) - 1) and k_ < n_) or (len(wb) >= 5 and an.get("went_back_t") is not None and a_ - 10 <= an["went_back_t"] <= b_): return "whole team"
            if i_ > 0 and n_ >= k_ + 1 and b_ - a_ <= COLLAPSE_VISIT_S: return "collapse"
            return "defended"
        told, parts_of = [], {}
        for i_, ph in enumerate(phases):
            kd = kind_of(i_, ph)
            if told and kd == "defended" and told[-1][3] == "defended":
                parts = parts_of[told[-1][1]]; parts.append(ph)
                # its numbers are those it had for longest before anybody in it died: a death changes them by the fight's own result, not by how it was set up (옷옷옷옷 v Men 6:46: three against two, then two against two once a split player is dead)
                first = min((td for td, _ in dA + dD if td >= parts[0][1]), default=T + 1)
                w = collections.Counter()
                for v_, a_, b_ in parts: w[v_] += max(min(b_ + S_, first) - a_, 0)
                if not any(w.values()):
                    for v_, a_, b_ in parts: w[v_] += b_ - a_ + S_
                told[-1] = (w.most_common(1)[0][0], told[-1][1], ph[2], "defended")
            else:
                told.append((ph[0], ph[1], ph[2], kd)); parts_of[ph[1]] = [ph]
        # the collapse is a situation of its own beside what the split met meanwhile (his marks on 옷옷옷옷 v RACK 1:34 and 6:00, Classic and correct: the split against
        # the two who defend it, and at 1:51 and 6:01 the full team collapsing on it); the team arriving is the same collapse, so the phases in which the whole team is
        # on the split, from the turn on, are told with it and not again (his marks on 2:06 and 6:28: "NOT a split, just RACK split team ... leaving portal/dying")
        turn_of, cur = {}, None
        def absorb(tn):                                   # the phases in which the whole team is on the split, from the turn on, belong to the collapse
            for ph in sorted(told, key=lambda ph: ph[1]):
                if ph[3] == "whole team" and tn["told"] - JOIN_S <= ph[1] <= tn["end"] + S_:
                    tn["end"] = max(tn["end"], ph[2]); told.remove(ph); tn.setdefault("took", []).append(ph)
        for tn in turns:
            if cur is not None and tn["told"] <= cur["end"] + JOIN_S:      # the team stalls and comes on again, or is on it already: still the collapse it began
                cur["end"] = max(cur["end"], min(tn["t1"] + JOIN_S, times[-1])); cur["t1"] = tn["t1"]; absorb(cur); continue
            cur = tn; cur["end"] = min(tn["t1"] + JOIN_S, times[-1]); absorb(cur); turn_of[cur["told"]] = cur
        for tn in turn_of.values():
            idx_ = [q for q, u in enumerate(times) if tn["told"] <= u <= tn["end"]]
            tn["reached"] = any(len(heads[q][0]) >= 5 for q in idx_)
            # a team that does not reach the split has collapsed on it only if it made for it for JOIN_S: a few seconds toward a split and away again is passing by
            # (R-350; 옷옷옷옷 v RACK 9:36 and 15:58: 옷옷옷옷 leaving RACK's base before a base res moves toward a split for 4 s, and he reads no collapse there)
            if not tn["reached"] and tn["t1"] - tn["t0"] < JOIN_S:
                told.extend(tn.get("took", [])); continue
            v_ = collections.Counter(kn[q] for q in idx_ if kn[q][0] > 0).most_common(1)
            if v_: told.append((v_[0][0], tn["told"], tn["end"], "whole team")); parts_of[tn["told"]] = [(v_[0][0], tn["told"], tn["end"])]
        turn_of = {t0_: tn for t0_, tn in turn_of.items() if t0_ in parts_of}
        told.sort(key=lambda ph: (ph[1], ph[1] in turn_of))
        phases = [(v_, a_, b_) for v_, a_, b_, _ in told]
        # When a split is told from (R-458, R-510): the second it crosses to the enemy's side; and where its players went straight across, crossing within SPLIT_GAP_S
        # of leaving their team, from TURN_S after they left, as a collapse is told from its turn (R-508): "that's when Men would see and have to respond" (Men v
        # RACK: the Ranger leaves at 10:42 and 13:45 and crosses at 11:00 and 14:00, the Mes/A leaves at 16:41 and crosses at 16:56; he times them 10:44, 13:52, 16:51)
        if phases and phases[0][1] not in turn_of and phases[0][1] - times[0] <= SPLIT_GAP_S and not (wait is not None and wait[0] <= times[0] + S_):      # a defence turned split is told from the turn-off alone
            seen = int(x["t_in"]) if not (0 < x["t_in"] - x["t0"] <= SPLIT_GAP_S) else int(x["t0"]) + TURN_S
            # A team held in its base (`pinned`): a player who goes out of the base and on to the split has left for it when he goes out, however long he is in
            # crossing, for his team is in the base and he can be going nowhere else (his mark, Men v hold 17:01, Classic, missed: "fire ele splits front door": he
            # is out past hold's back door at 16:58, walks round by its front door and crosses at 17:38, where the row began; his guide: a split is in its own
            # base only when leaving or returning). Out is past his own doors, after the last time he stood in his pit or base.
            own_, tin_ = st.side.get(tm), int(x["t_in"]) - int(x["t_in"]) % S_
            inside = lambda a, u, kinds: bool(M.AL[a][u]) and bool(M.P[a][u]) and M.place_at(a, u)[1] == own_ and M.place_at(a, u)[0] in kinds
            def out_at(a):
                u = next((v for v in range(tin_, max(tin_ - 90, 0) - 1, -S_) if inside(a, v, ("pit", "base")) or not M.AL[a][v]), None)
                if u is None or not M.AL[a][u]: return None
                return next((v for v in range(u + S_, tin_ + 1, S_) if not inside(a, v, ("pit", "base", "front door", "back door"))), None)
            outs = [out_at(a) for a in x["ids"] if frm[a] <= x["t_in"] + S_]
            if outs and None not in outs and any(p_[0] == tm and p_[1] - 4 <= max(outs) <= p_[2] + 4 for p_ in pinned(M)): seen = min(seen, max(outs) + TURN_S)
            seen = min(seen - seen % S_, phases[0][1])
            if seen < phases[0][1]:
                parts_of[seen] = parts_of.pop(phases[0][1])      # its parts keep their own times: the numbers it had are told from when it had them
                phases[0] = (phases[0][0], seen, phases[0][2])
        along = lambda p0: ("; numbers along the way: " + ", ".join(f"{k_} v {n_} from {int(a_) // 60}:{int(a_) % 60:02d}" for (k_, n_), a_, b_ in parts_of[p0])) if len(parts_of[p0]) > 1 else ""
        prevD, way = set(), x["way"]
        DOOR_OF = {"front door": "front door", "front footies": "front door", "back door": "back door", "back footies": "back door"}
        # The split family, stage 1 (R-558): what the answer to a split is read from and judged by, kept on every play of the split (`split`) and changing none of
        # them (as `_numbers_at` for a numbers play). The clock is the second the split is told (R-562: when its players are committed and the other team has to
        # answer): when it left, crossed, could first do something and was first met by a defender; the base res; its size (the numbers its first told fight had
        # for longest); at fixed seconds from the telling how many of it stand on the enemy's ground, how many defend it, how many of those are backline monks and how many monks it brought;
        # every stretch it is told in with the kind of answer it met (nobody, defended, a collapse, the whole team); and, on the split's own account, each death
        # on it, each defender's death and each NPC it took, by the second. The plays of its first told stretch also carry the position each team chose from
        # and the fixed 60, 90 and 180 s record from that second, with the position 60 s before (`at_told`; not `state`, which the price of a position is
        # fitted on: adding a family must not move the prices the flag readings were shown on)
        srec = at_told = None
        if phases:
            told0 = int(phases[0][1]); hist = sorted(told, key=lambda ph: (ph[1], ph[1] in turn_of))
            def num_at(h):
                u = told0 + h
                if u > t9: return None                                   # over by then
                if u < t0: return [0, 0, 0, 0]                             # told from its leaving (R-510), not yet on their ground
                i_ = (u - t0) // S_
                return [len(Ss[i_]), len(Ds[i_]), sum(map(is_monk, Ds[i_])), sum(map(is_monk, Ss[i_]))]
            def props_at(h):                                              # what the players on it at that second can do
                u = told0 + h
                return M._props(Ss[(u - t0) // S_]) if t0 <= u <= t9 and Ss[(u - t0) // S_] else None
            srec = {"id": f"{tm}-{told0}", "told": told0, "left": int(x["t0"]), "crossed": int(x["t_in"]), "reached": None if reach0 is None else int(reach0),
                    "first_defender": next((int(u) for u, dn in zip(times, Ds) if dn), None), "end": int(t9), "res_in": int(st.next_res(min(told0, T)) - told0), "size": int(phases[0][0][0]),
                    "monks": sum(map(is_monk, [a for a, _ in collections.Counter(a for i_, u in enumerate(times) if phases[0][1] <= u <= phases[0][2] for a in Ss[i_]).most_common(phases[0][0][0])])),
                    "at": list(SPLIT_TRACK_S), "numbers": [num_at(h) for h in SPLIT_TRACK_S],
                    "stretches": [[0 if q_ == 0 else int(max(a_, told0)) - told0, int(b_) - told0, int(v_[0]), int(v_[1]), kd] for q_, (v_, a_, b_, kd) in enumerate(hist)],
                    # what else a like spot is matched on (his list of 2026-11-21): each side's dead when it is told (they res at the base, on the split, and are missing from
                    # the main fight), where each main team stands on its ladder, and what the players of the split can do, as properties and never as a build (R-539)
                    "dead": [sum(1 for a in st.players[k_] if not M.AL[a][min(told0, T)]) for k_ in (tm, foe)],
                    "steps": [M._main_step(k_, min(told0, T) - min(told0, T) % S_)[0] for k_ in (tm, foe)],
                    "props": [props_at(h) for h in SPLIT_TRACK_S],
                    # ... and what else the team it is sent against can see when it has to answer (the other factors, R-568): which of its pit NPCs are left, how many of
                    # its players are already at home (a runner, a player just risen at the base, one waiting back), whether a flag run or a split of its own is under way
                    "pit_alive": (lambda N_: {k_: sum(1 for z, kd in N_ if kd == k_ and st.npc_dead.get(z, 1e9) > told0) for k_ in ("knight", "archer", "bodyguard")})(
                        [(z, v["kind"]) for z, v in st.geo.npcs.items() if v["team"] == foe and v.get("pit") and v["kind"] != "guild_lord"]),
                    "home": (lambda u_: sum(1 for b in st.players[foe] if M.AL[b][u_] and M.P[b][u_] and M.place_at(b, u_)[1] == own_d and M.place_at(b, u_)[0] in HOMEG))(min(told0, T) - min(told0, T) % S_),
                    "tm": tm,      # (`runner_out`, a flag run of each team under way when it is told, is added in `plays`: the flag rows must not be asked for here. This reading is
                    # entered while `run_starts` is still being built (the part-carries are read from the split's candidates), and `_flag_rows` would keep the half-built runs:
                    # tried 2026-11-21, 30 flag plays of the development set moved)
                    "own_split": any(y is not x and y["tm"] == foe and y["t_in"] <= told0 <= y["t1"] for y in A),
                    # ... and the damage its players did to the Guild Lord while it was out (his word: a split that clears the pit later in the game does more of it), by the second
                    "lord_damage": [[int(u) - told0, round(v)] for u, a, v in sorted(M.lord_hits.get(foe, ())) if a in frm and frm[a] <= u <= ext[a] + 4 and v],
                    "split_deaths": [int(td) - told0 for td, _ in dA], "defender_deaths": [int(td) - told0 for td, _ in dD], "npcs": [[int(td) - told0, kind, bool(pit)] for td, kind, pit in sorted(npc_ev)]}
            def _at_told(k_, u=min(told0, T)):
                o = {"state": M._state(k_, u), "after": M.consequence(k_, u, FLAG_AFTER_S)}
                b_ = u - FLAG_BEFORE_S
                o["before"] = None if b_ < 0 else {"state": M._state(k_, b_), "after": M.consequence(k_, b_, (FLAG_BEFORE_S,))[str(FLAG_BEFORE_S)]}
                return o
            at_told = {}
        first_pi = None
        for pi, ((k, n), p0, p1) in enumerate(phases):
            last = pi == len(phases) - 1
            mark = len(out)
            idx = [i for i, u in enumerate(times) if p0 <= u <= p1]
            cs, cd = collections.Counter(a for i in idx for a in Ss[i]), collections.Counter(b for i in idx for b in Ds[i])
            Sp, Dp = [a for a, _ in cs.most_common(k)], [b for b, _ in cd.most_common(n)]
            tn = turn_of.get(p0) if (k, n) == parts_of[p0][0][0] and p1 == parts_of[p0][0][2] else None
            if tn is not None:                             # a collapse from the turn (R-508): those on the split and those making for it
                Dp = Dp + [b for b in tn["ids"] if b not in Dp]; n = len(Dp)
            # R-381 asked of the moment (R-439): a lone player is splitting only when he hits NPCs or trades damage with a defender. A player left on the enemy's
            # ground by the others of his split, who then does neither while he is alone, is not splitting on (his mark, Men v hold 9:56: "he is running away from a
            # previous split to join mainteam; he is not splitting": the Hammer at hold's back door from 9:56, the Ranger gone home, 44 s without a hit until five of
            # Men came round to him). A lone player on his way in has not been left by anyone, and is read as before (Men v RACK 16:51, hold v RACK 12:40, Classic)
            if tn is None and all(v_[0] == 1 for v_, _, _ in parts_of[p0]) and any(v_[0] >= 2 for v_, a_, _ in phases[:pi] if a_ not in turn_of):
                alone = [u_ for i, u_ in enumerate(times) if p0 <= u_ <= p1 and len(Ss[i]) == 1]
                foes_, w0, w1 = set(st.players[foe]), min(alone, default=int(p0)), max(alone, default=int(p0)) + S_ - 1
                busy_ = (any(w0 <= td <= w1 for td, _, _ in npc_ev) or any(w0 <= u_ <= w1 for a in Sp for u_ in M.npc_hits.get(a, ()))
                         or sum(1 for u_ in range(w0, w1 + 1) for x_, y_ in M.hits.get(u_, ()) if (x_ in Sp and y_ in foes_) or (y_ in Sp and x_ in foes_)) >= 2)
                if not busy_: continue
            e1 = min(p1 + 4, T)
            # a death that made the numbers of this phase belongs to the phase before it (his mark, hdm v hook 7:52: "they are only 4 v 3 because they killed a defender"): at its first seconds only the deaths of players counted in it are its own
            # ... and a death after a team has turned on the split belongs to that collapse alone, not also to the row the split was in beside it (QenK v Fun 6:37:
            # the Hammer dies to Fun's collapse, told from 6:28; the 1 v 1 against the 8 Monk beside it, 6:10 to 6:40, had "the split player survives: no")
            in_turn = lambda td: tn is None and any(tn_["t0"] <= td <= tn_["end"] + 4 for tn_ in turn_of.values())
            lostp = [a for td, a in dA if p0 - 1 <= td <= (max(e1, end_chase + 2) if last else e1) and (pi == 0 or td > p0 + 4 or a in Sp) and not in_turn(td)]
            killp = [b for td, b in dD if p0 - 1 <= td <= e1 and (pi == 0 or td > p0 + 4 or b in Dp) and not in_turn(td)]
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
            full = full or tn is not None
            collapse = bool(came) and n >= k + 1 and short and pi > 0 and not full
            whoA, whoD = [role[a] for a in Sp], [role[b] for b in Dp]
            size = {1: "one player", 2: "two players", 3: "three players"}.get(k, f"{k} players")
            if tn is None: M._split_at.append({"tm": tm, "name": f"{m.tag[tm]}'s split from {clock(p0)}", "at": {times[i]: (frozenset(Ss[i]), frozenset(Ds[i])) for i in idx}})
            # R-487: a team in two even groups, both along the main flag path (this one forward at the enemy's front door, the other at home), is a push team and a
            # defence team, not a main team and a split ("frontside" and "backside"); in two different areas of the map the non-flag side is the split
            # The door is read phase by phase (his mark, Men v hold 10:40, Classic: "a split through the backdoor not front": the record's door was the front door
            # two of its players had come to minutes before): the enemy's door, or the footmen in front of it, the players of the phase come to first in it, as the
            # record reads its own. Only a phase whose players all start it out in the field comes to a door anew: one that starts with a player already on the
            # enemy's ground (a door, the footmen, the pit or the base) keeps the door it came in by, as does one that comes to no door.
            if all(M._deep(a, int(p0)) in (None, "field") for a in Sp) or (wait is not None and wait[0] < wait[1] and abs(int(p0) - wait[1]) <= S_):      # ... and a defence turned split, told from the turn-off it passed in the field, comes to its door anew
                atd = min((u for a in Sp for u in range(int(p0), int(p1) + 1, S_) if M._deep(a, u) in DOOR_OF), default=None)
                if atd is not None:
                    way = collections.Counter(DOOR_OF[M._deep(a, u)] for a in Sp for u in range(atd, min(atd + JOIN_S, int(p1)) + 1, S_) if M._deep(a, u) in DOOR_OF).most_common(1)[0][0]
            base0 = f"{m.tag[tm]}'s split" + (f" by the {way}" if way else "")      # no door is named where none is read (his words, HC v Team 4:24: '"by the door" means nothing')
            rest = [a for a in st.players[tm] if a not in Sp and M.AL[a][mid] and M.P[a][mid]]
            push_team = k >= 3 and k == len(rest) and way == "front door" and sum(1 for a in rest if M.place_at(a, mid)[1] == st.side.get(tm) and M.place_at(a, mid)[0] in HOMEG) * 2 > len(rest)
            base = f"{m.tag[tm]}'s push team at the front door (its defence team at home)" if push_team else base0
            scen_a = f"{base}: {size} ({', '.join(whoA)}) against {n} defending" + (f" ({', '.join(whoD)})" if n else "") + along(p0)
            way_in = "" if tn is not None or pi > 0 or (reach0 is not None and reach0 <= x["t_in"] + S_) else (f"; it crosses at {clock(x['t_in'])} and reaches their base, their footmen or a defender at {clock(reach0)}" if reach0 is not None and reach0 <= p1 else f"; it crosses at {clock(x['t_in'])} and has not reached their base, their footmen or a defender by {clock(p1)}")
            scen_a += way_in
            if tn is not None: scen_a = f"{base}: {size} ({', '.join(whoA)}); {m.tag[foe]} turns on it from {clock(tn['t0'])} with {n} ({', '.join(whoD)})" + ("" if tn["reached"] else ", and does not reach it")
            besA = {"npcs_taken": [kind for kind, _ in npcs], "kills": [role[b] for b in killp], "lost": [role[a] for a in lostp], "flag_lead": [K.lead(tm, p0), K.lead(tm, e1)], "deaths_away_from_the_split": [away_a, away_d],
                    "split": [dmg_s, ms], "defence": [dmg_d, md], "main": main, "main_can_kill": main_can, "reached": reach, "phase": [pi + 1, len(phases)], "chased_until": end_chase if last and end_chase > t9 else None}
            besD = {"pit_npcs_lost": [kind for kind, pit in npcs if pit], "other_npcs_lost": [kind for kind, pit in npcs if not pit], "lost": [role[b] for b in killp], "split_killed": [role[a] for a in lostp],
                    "flag_lead": [K.lead(foe, p0), K.lead(foe, e1)], "deaths_away_from_the_split": [away_d, away_a], "split": [dmg_s, ms], "defence": [dmg_d, md], "main": {"own": main["theirs"], "theirs": main["own"]}, "main_can_kill": main_can[::-1], "phase": [pi + 1, len(phases)]}
            elsewhere = {"more of theirs die away from the split than of ours": away_d > away_a, f"flag lead better by {FLAG_GAIN} or more": ga is not None and ga >= FLAG_GAIN}
            kill_or_npc = {"a defender killed": n_kill > 0, "an NPC taken": n_npc > 0}
            kw = dict(size=k, defenders=n, split_damage=dmg_s, defending_monks=md, group="push team" if push_team else "split")
            # R-511: who comes to a split fight and who leaves it are decisions of their own, told beside the fight (his marks on Men v RACK 12:48 and 18:25 and Men v
            # hold 1:09, 5:18 and 6:11, all Classic: "very clear and important collapse (8 monk hammer) on RACK's split; and rack's simultaneous split join (7 monk,
            # hammer)"; "The players are correctly identified in the split, but the collapse and join itself are decision points for the respective teams"; "he
            # leaves defence at 1:09 to rejoin mainteam (giving them player advantage)"). One row a side at each change of the numbers inside a fight that is told
            # once (R-365): defenders who come are a collapse when they make the defence one more than the split was (R-441), else a join; a player who dies has not left
            if tn is None and len(parts_of[p0]) > 1:
                parts = parts_of[p0]
                who_in = lambda L, lo, hi, n_: [z for z, _ in collections.Counter(z for i, u in enumerate(times) if lo <= u <= hi for z in L[i]).most_common(n_)]
                for q in range(1, len(parts)):
                    (k0, n0), a0, b0 = parts[q - 1]; (k1, n1), a1, b1 = parts[q]
                    S0, S1, D0, D1 = who_in(Ss, a0, b0, k0), who_in(Ss, a1, b1, k1), who_in(Ds, a0, b0, n0), who_in(Ds, a1, b1, n1)
                    died = lambda z: any(a1 - JOIN_S <= td <= a1 + S_ for td in st.death_times.get(z, []))
                    came_s, came_d = [z for z in S1 if z not in S0], [z for z in D1 if z not in D0]
                    left_s, left_d = [z for z in S0 if z not in S1 and not died(z)], [z for z in D0 if z not in D1 and not died(z)]
                    c1 = min(b1 + 4, T)
                    lost_c, kill_c = sum(1 for td, _ in dA if a1 <= td <= c1), sum(1 for td, _ in dD if a1 <= td <= c1)
                    pit_c = sum(1 for td, _, pit in npc_ev if pit and a1 <= td <= c1)
                    npc_c = sum(1 for td, _, _ in npc_ev if a1 <= td <= c1)
                    nums = f"{k0} v {n0} becomes {k1} v {n1}"
                    names = lambda L: ", ".join(role[z] for z in L)
                    kwc = dict(size=k1, defenders=n1, group="split", change=True, of=[tm, int(p0)], at=int(a1))      # of: the split it belongs to (its team, and the start of the fight as told): each change is a decision of its own in the data (R-514), shown in the split's row
                    if came_d:
                        col = n1 >= k1 + 1                  # one more than the split as it then stands (R-441, NwAy v Men 11:50: a defender who comes as a split player joins, 3 v 3 to 4 v 4, has joined)
                        out.append(_play(M, "split", "defender", foe, a1, c1, [role[z] for z in came_d],
                                         f"{m.tag[foe]}: {names(came_d)} {('collapses on' if len(came_d) == 1 else 'collapse on') if col else ('joins the defence against' if len(came_d) == 1 else 'join the defence against')} {base} at {clock(a1)}: {nums}" + (f", as {names(came_s)} {'joins' if len(came_s) == 1 else 'join'} the split" if came_s else ""),
                                         "Kill a split player before going back (what it cost at the main fight and in flags is beside it)" if col else "Hold it even or better: lose no pit NPC and no more players than the split does",
                                         {"a split player dies after they come": lost_c > 0} if col else {"no pit NPC lost": pit_c == 0, "no more defenders die than split players": kill_c <= lost_c},
                                         beside={"flag_lead": [K.lead(foe, a1), K.lead(foe, c1)]}, ruled=col, call="collapse" if col else "join", **kwc))
                    if came_s:
                        out.append(_play(M, "split", "attacker", tm, a1, c1, [role[z] for z in came_s],
                                         f"{m.tag[tm]}: {names(came_s)} {'joins' if len(came_s) == 1 else 'join'} {base} at {clock(a1)}: {nums}" + (f", as {names(came_d)} {'comes' if len(came_d) == 1 else 'come'} to defend it" if came_d else ""),
                                         "Kill or take NPCs with the players added", {}, any_of={"a defender killed": kill_c > 0, "an NPC taken": npc_c > 0},
                                         beside={"flag_lead": [K.lead(tm, a1), K.lead(tm, c1)]}, ruled=False, answer="join", **kwc))
                    if left_d:
                        out.append(_play(M, "split", "defender", foe, a1, c1, [role[z] for z in left_d],
                                         f"{m.tag[foe]}: {names(left_d)} {'leaves' if len(left_d) == 1 else 'leave'} the defence against {base} at {clock(a1)}: {nums}",
                                         "Gain at the main fight with the player back, and lose no pit NPC for it", {"no pit NPC lost": pit_c == 0},
                                         any_of={"more of theirs die away from the split than of ours": K.died(tm, a1, c1) - lost_c > K.died(foe, a1, c1) - kill_c, f"flag lead better by {FLAG_GAIN} or more": (K.gain(foe, a1, c1) or 0) >= FLAG_GAIN},
                                         beside={"flag_lead": [K.lead(foe, a1), K.lead(foe, c1)]}, ruled=False, call="leave", **kwc))
                    if left_s:
                        out.append(_play(M, "split", "attacker", tm, a1, c1, [role[z] for z in left_s],
                                         f"{m.tag[tm]}: {names(left_s)} {'leaves' if len(left_s) == 1 else 'leave'} {base} at {clock(a1)}: {nums}",
                                         "Gain at the main fight with the player back", {},
                                         any_of={"more of theirs die away from the split than of ours": K.died(foe, a1, c1) - kill_c > K.died(tm, a1, c1) - lost_c, f"flag lead better by {FLAG_GAIN} or more": (K.gain(tm, a1, c1) or 0) >= FLAG_GAIN},
                                         beside={"flag_lead": [K.lead(tm, a1), K.lead(tm, c1)]}, ruled=False, answer="leave", **kwc))
            # the attacker's job, set by the answer it meets (R-428)
            if full or collapse:
                ans = "met by a full collapse" if full else "collapsed on"
                # R-523 (his answer of 2026-11-18, "Yes", as R-517 for a split a player down): a split that is collapsed on has drawn players off the main fight, and has done its
                # job when it loses nobody; what its team gained elsewhere meanwhile is the main team's to answer for, and is kept beside the row
                out.append(_play(M, "split", "attacker", tm, p0, e1, whoA, scen_a + ("" if tn is not None else "; the whole team turns on it" if full else f"; {', '.join(role[b] for b in came)} collapse from the main fight"),
                                 "Survive the collapse and lose nobody (what the team gained elsewhere meanwhile is beside it)", {"nobody on the split dies": n_lost == 0}, beside=dict(besA, gained_elsewhere=elsewhere), answer=ans, **kw))
            elif n == 0: out.append(_play(M, "split", "attacker", tm, p0, e1, whoA, scen_a, "Take NPCs", {"an NPC taken": n_npc > 0}, beside=besA, answer="undefended", **kw))
            # R-517 (his answer of 2026-11-17, from R-512: a split holding more defenders than its own number "is ALREADY ACCOMPLISHING THEIR GOAL. They are keeping 4 people occupied
            # without dying, providing a player advantage elsewhere on the map"): its job is met by holding them there and losing nobody. What its team made of the extra player
            # elsewhere is the main team's to answer for (its numbers row), and is kept beside this one, not in its test: a test covers only what the players of the play control
            elif k < n: out.append(_play(M, "split", "attacker", tm, p0, e1, whoA, scen_a, "Hold more defenders there than its own number and lose nobody (what the team made of the extra player elsewhere is beside it)",
                                         {"nobody on the split dies": n_lost == 0}, beside=dict(besA, gained_elsewhere=elsewhere), answer="a player or more down", **kw))
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
            scen_d = (f"{m.tag[foe]} against {base}: {n} ({', '.join(whoD)}) against {size}" if n else f"{m.tag[foe]} against {base}: nobody against {size}") + along(p0)
            scen_d += way_in
            if tn is not None: scen_d = f"{m.tag[foe]} against {base}: {n} turn for it from {clock(tn['t0'])} ({', '.join(whoD)}) against {size}" + ("" if tn["reached"] else "; they do not reach it")
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
            if n >= 1 and not collapse:                                    # a defender part-running his flag: the lone defender of R-430, and one of several (R-535: meow v One 7:03, the 8 Monk, one of three; the job is R-430's, Claude's reading for more than one defender, his to confirm)
                lone = k == 1 and n == 1
                for b in Dp:
                    carried = sum(S_ for u in range(max(p0 - JOIN_S, 0), p1 + 1, S_) if (M.carrying(b, u) if lone else M.part_run_at(b, u)))      # from when he got there: he counts as the defender only JOIN_S later (review key s1-28); one of several defenders, only a part-run carry (`part_run_at`)
                    if carried >= 6:
                        out.append(_play(M, "split", "defender", foe, p0, e1, [role[b]], scen_d + (f": the lone defender carries his flag for {carried} s" if lone else f": {role[b]} carries his flag for {carried} s while defending"), "Gain a slight flag advantage while losing no pit NPC and not dying",
                                         dict(pit_ok, **{f"flag lead better by {PART_RUN_GAIN} or more": gd is not None and gd >= PART_RUN_GAIN, "the defender does not die": n_kill == 0}), beside=dict(besD, carried_s=carried), ruled=lone, call="part-run", **kw))
            if tn is None: prevD = set(Dp)
            if len(out) > mark and first_pi is None: first_pi = pi
            for q_ in out[mark:]:
                q_["split"] = srec
                if pi == first_pi and not q_.get("change"):
                    if q_["tm"] not in at_told: at_told[q_["tm"]] = _at_told(q_["tm"])
                    q_["at_told"] = at_told[q_["tm"]]
    return out


# ---- a numbers difference in the main team's fight (R-431, gaps 4, 5 and 7)
NUMBERS_TRACK_S = (0, 15, 20, 30, 60)  # where each main team stands at these seconds of a numbers situation, so that a call can be read at a fixed early second (20 and 60 s are his, R-556)
HARD_RES_DEAD_S = 3                    # a player back up sooner than this was not dead in the fight (a death and a reading of him alive a second apart)


def _hard_res(M):
    """Every resurrection in the fight, by team: [second, player] for a player who is alive again away from the base res (R-552: a res signet, Death Pact Signet
    and the like; "if a res gets off, a numbers advantage from kills is pretty much over"). The replay records no resurrection: it is read from a dead player alive
    again more than 3 s off the two-minute base res (on four games, 21 such returns all stood by their corpse and 40 of 42 at the base res did not)."""
    if getattr(M, "_hres", None) is None:
        out = {tm: [] for tm in M.st.teams}
        for tm in M.st.teams:
            for a in M.st.players[tm]:
                for td in M.st.death_times.get(a, []):
                    u = min(int(td) + 1, M.T)
                    while u <= M.T and not M.AL[a][u]: u += 1
                    if u > M.T or u - td < HARD_RES_DEAD_S: continue
                    if abs(u - round(u / RES_EVERY) * RES_EVERY) > 3: out[tm].append([u, a])
        M._hres = {tm: sorted(v) for tm, v in out.items()}
    return M._hres


def _numbers_at(M, tm, t, e):
    """What a numbers situation is read from and judged by (the numbers family, stage 1; R-550 to R-552), at the second it is told: the position and the fixed
    60, 90 and 180 s record, as on a flag play (cases.py), with the position 60 s before; its clock (when the numbers arose and ended, the base res, each side's
    dead, and every resurrection in the fight over the next three minutes); and where each main team stands at fixed seconds, with any runner of ours gone by
    then, so that the call can be read early and not from the whole situation (a team that pushes up over a minute is mostly a team that is already winning).
    Nothing here changes what the play is, its job or its test."""
    T, st, foe = M.T, M.st, 3 - tm
    u = min(t, T)
    kw = {"state": M._state(tm, u), "after": M.consequence(tm, u, FLAG_AFTER_S)}
    b_ = u - FLAG_BEFORE_S
    kw["before"] = None if b_ < 0 else {"state": M._state(tm, b_), "after": M.consequence(tm, b_, (FLAG_BEFORE_S,))[str(FLAG_BEFORE_S)]}
    dead = lambda k: sum(1 for a in st.players[k] if not M.AL[a][u])
    res = sorted([v - u, "own" if k == tm else "theirs", M.m.roles[a]] for k in st.teams for v, a in _hard_res(M)[k] if u < v <= u + 180)
    kw["clock"] = {"arose": int(e["start"]), "end": int(e["last"]), "res_in": int(st.next_res(u) - u), "dead": [dead(tm), dead(foe)], "hard_res": res}
    step = lambda k, v: M._main_step(k, v - v % SPLIT_STEP)[0] if v <= T else None
    runs = [int(f_.get("off", f_["s0"])) for f_ in _flag_rows(M) if f_["tm"] == tm]
    kw["track"] = {"at": list(NUMBERS_TRACK_S), "steps": [[step(tm, u + h), step(foe, u + h)] for h in NUMBERS_TRACK_S],
                   "runner_out": [any(u < r <= u + h for r in runs) for h in NUMBERS_TRACK_S]}
    return kw


def numbers_plays(M, K, trig, recs, pinned_at):
    out, T, st = [], M.T, M.st
    M._numbers_told = []                                                 # the numbers stretches that are told as plays (the self-check, R-488)
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
        # a fight is told once: where the players of one side in this fight are a split, from its first reading to its last, it is that split's fight and is told there,
        # with its numbers along the way (his mark, RJT v RACK 11:08: "sort of true, but you called this fight and period a split already")
        on_split = lambda u: any(ids and sum(1 for a in ids if a in M._over(k, u - u % SPLIT_STEP)[0]) * 2 >= len(ids) for k, ids in e["ids"].items())
        # ... and by the players themselves (R-488: "a player cannot be part of 2 fights at once"): the seconds of this stretch in which its counted players are
        # counted on a split or its defence. Where that is half of it or more, it is the split's fight; where it is less, but a player is in both for JOIN_S or
        # longer, the two readings disagree and no clear decision is read from the numbers
        both = collections.Counter()
        for u, ids in e["at"].items():
            for sp in M._split_at:
                if u in sp["at"]:
                    for a in ids & (sp["at"][u][0] | sp["at"][u][1]): both[a] += SPLIT_STEP
        tot = sum(len(ids) for ids in e["at"].values()) * SPLIT_STEP
        if (on_split(int(e["start"])) and on_split(int(e["last"]))) or (tot and sum(both.values()) * 2 >= tot):
            x["merged"] = "the split"
            continue
        twice = sorted(M.m.roles[a] for a, v in both.items() if v >= JOIN_S)
        end = min(e["last"] + NUMBERS_TAIL_S, T)
        if not any(e is q for q in M._numbers_told): M._numbers_told.append(e)
        inf = set(e["all"])                                               # the players of this fight: a death is its result only if it is one of theirs. The deaths that made the numbers are its cause
        dA, dB = (lambda b: K.died(tm, t, b, inf)), (lambda b: K.died(foe, t, b, inf))      # (his marks, hook v hold 14:56: "if it is 5 v 7 because 2 players died, the 5 v 7 didn't cause the 2 players to die"; hdm v hook 7:52 for a split)
        scen = x["scenario"]["label"] + f"; {x['team']}: {x['call']['label'].lower()}"
        bes = lambda b: {"deaths": [dA(b), dB(b)], "npcs": [K.npcs(tm, t, b), K.npcs(foe, t, b)], "flag_lead": [K.lead(tm, t), K.lead(tm, b)], "lasted_s": e["last"] - e["start"]}
        back, push = c in ("retreat down the ladder", "fall out"), c in ("push up", "push in", "push their flagger")
        monk = lambda a: M.m.A[a].get("p") == "Monk" and not M.m.roles[a].startswith("Monk ") and "WoC" not in M.m.roles[a]
        dmg_own, monks_their = sum(1 for a in e["ids"][tm] if not monk(a)), sum(1 for a in e["ids"][foe] if monk(a))
        kill_on = can_kill(dmg_own, monks_their)                          # R-457 in the main fight too (his marks, hdm v hook 4:12, 6:52: "2 damage v 2 monks again")
        kw = dict(source=src, numbers_side=side, call=c, numbers=x["scenario"]["parts"]["numbers"], numbers_end=int(e["last"]))
        kw.update(_numbers_at(M, tm, int(t), e))
        if not x["scenario"]["parts"].get("clear", True): kw.update(clear=False, unclear="the numbers never held for 12 s")
        elif twice: kw.update(clear=False, unclear=f"{', '.join(twice)} also counted on a split in the same seconds")
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
    # the row ends when the numbers do: the job is judged a short tail longer (R-424), kept as `judged_to`, but the time told is the time of the numbers (his mark on
    # HC v hdm 5:46, Classic: "they lose player advantage a bit sooner (around 6:03) when WoC 4 leaves through portal": the numbers ended at 6:02 and the row said 6:12)
    for p in out:
        if p.get("numbers_end") is not None and p["side"] != "after a wipe" and p["t1"] > p["numbers_end"] + SPLIT_STEP:
            p["judged_to"], p["t1"] = p["t1"], max(p["numbers_end"] + SPLIT_STEP, p["t0"] + SPLIT_STEP)
    return out


# ---- their boost is coming (gap 2)
def boost_plays(M, K, recs, pinned_at):
    out, T = [], M.T
    for x in recs:
        if x["family"] != 1 or "boost" not in x["triggers"] or pinned_at(x["tm"], x["t"]): continue
        tm, foe = x["tm"], 3 - x["tm"]
        owner, since = M.st.stand_owner(x["t"])                           # the boost has its own clock: a moment that began with another trigger up to MERGE_S earlier is not the boost's time
        if owner != foe: continue                                         # (his marks, hook v hold 9:22: the boost was 51 s away and landed at 10:13; cope v Team 13:28: it landed at 14:07)
        lands = next((u for u in (since + BOOST_EVERY * k for k in range(1, int(T // BOOST_EVERY) + 2)) if u - BOOST_WARN_S >= x["t"] - 2), None)
        if lands is None or lands - BOOST_WARN_S > x["t"] + MERGE_S + 2: continue
        t = int(lands - BOOST_WARN_S)
        capped = any(f_["tm"] == tm and f_["how"] == "captured" and f_["start"] <= t <= f_["end"] for f_ in M.flags_record())
        carr = [a for a in M.st.players[tm] if capped and M.carrying(a, min(t, T))]      # a flag on its way: carried at that moment, and it goes on to be capped (a flag carried about at home is not a run)
        runners = (x["call"].get("runners") or 0) >= 1
        ran = runners or bool(carr)
        t1 = min(lands + 5, T)
        denied = not any(h == foe and t < u <= t1 for u, h in M._boosts())
        bes = {"boost_worth": x["state"]["enemy_boost"], "denied": denied, "deaths": [K.died(tm, t, t1 + 10), K.died(foe, t, t1 + 10)], "flag_lead": [K.lead(tm, t), K.lead(tm, t1)]}
        # the runners are named, each flag's carriers in order (his words on Men v Crew and 옷옷옷옷 v RACK: "one runner" does not say who)
        named = "; ".join(r[0] + (", handing it to " + " and ".join(r[1:]) if len(r) > 1 else "") for r in x["call"]["shape"].get("runs") or [])
        lab_ = x["call"]["label"].lower()
        if named: lab_ = lab_.replace("one runner", f"one runner ({named})", 1).replace("two runners", f"two runners ({named})", 1)
        scen = f"{M.m.tag[foe]}'s boost is {BOOST_WARN_S} s away; {x['team']}: " + (lab_ if runners or not carr else f"a flag already on its way ({', '.join(M.m.role(a).split(' ', 1)[1] for a in carr)})")
        # the position and the fixed 90 and 180 s record at the second the boost decision is read, and where the rest of the team went, for the similar cases (cases.py)
        # (`runner_soh`: the flag is on a Shadow of Haste runner while the mechanic was in the game, R-456; kept apart from `soh` so that the row told on the page does not change)
        ids_ = list(x["call"]["shape"].get("ids") or []) + carr
        at = dict(state=M._state(tm, min(t, T)), after=M.consequence(tm, min(t, T)), rest=x["call"].get("rest"),
                  runner_soh=bool(M.day < SOH_REMOVED and any(M.m.sk(b) == "Shadow of Haste" for a in ids_ for b in M.m.A[a].get("bar", []) if b)))
        if ran: out.append(_play(M, "boost", "own", tm, t, t1, x["call"]["shape"]["who"], scen, "Deny their boost", {"their boost does not land": denied}, beside=bes, call="run", **at))
        else: out.append(_play(M, "boost", "own", tm, t, min(t1 + 10, T), [], scen, "Concede the boost for kills", {"more of theirs die than of ours": bes["deaths"][1] > bes["deaths"][0]}, beside=bes, call="concede", **at))
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
            on = a is not None and b is not None and a >= 2 and b <= -2 and (a >= 3 or b <= -3)      # held in: on its own ground no further out than its doors, with their main team on that ground too, and not just a fight at the doors (his mark, hook v hold 17:04: hook at its door with hold in its pit is "still stuck in their base")
            if on and cur and t - cur[2] <= S: cur[2] = t
            else:
                if cur and cur[2] - cur[1] >= PINNED_S: out.append(tuple(cur))
                cur = [tm, t, t] if on else None
        if cur and cur[2] - cur[1] >= PINNED_S: out.append(tuple(cur))
    M._pinned = out
    return out


def pinned_plays(M, K):
    out, T, st = [], M.T, M.st
    def out_of_base(tm, a, b):                                            # the second it breaks out, or None
        own = st.side.get(tm)
        for u in range(a - a % 2, b + 1, 2):
            live = [x for x in st.players[tm] if M.AL[x][u]]
            away = [x for x in live if not (M.place_at(x, u)[1] == own and M.place_at(x, u)[0] in ("pit", "base", "front door", "back door"))]      # out past its doors: a team standing in its own doorway is still held in, as `pinned` reads it (his mark, hook v hold 17:04)
            if len(away) >= 4 and len(away) * 2 >= len(live): return u
        return None
    for tm, a, b in pinned(M):
        t = a
        while t < b:                                                      # one play to each base res while it lasts
            dead = sum(1 for x in st.players[tm] if not M.AL[x][min(t, T)])
            t1 = min(st.next_res(t), b + 4, T) if dead else min(b + 4, T)      # with nobody dead there is no res to hold out for: one play for as long as it is held in (his mark, hdm v hook 12:00)
            if t1 - t >= 10:
                s1 = M._main_step(tm, min(t1 + 10, T))[0]
                alive = sum(M.AL[x][min(t1 + 10, T)] for x in st.players[tm])
                bo = out_of_base(tm, max(t, b - 4), min(t1 + 10, T)) if t1 >= b else None      # it breaks out where being held in ends: while the stretch lasts it is held in, wherever some of its players stand
                lost = bo is not None and (K.npcs(tm, t, bo, pit=True) > 0 or K.died(tm, t, bo) > 0)
                said = "it does not break out" if bo is None else f"it breaks out at {int(bo) // 60}:{int(bo) % 60:02d}, {'after losing a player or a pit NPC' if lost else 'having lost nothing'}"
                hold = {"no pit NPC lost and nobody dies until the base res": K.npcs(tm, t, t1, pit=True) == 0 and K.died(tm, t, t1) == 0,      # R-478: a break-out meets the job only if nothing was lost before it (cope v Team 10:42: a knight lost, then out)
                        f"it breaks out having lost no player and no pit NPC first ({said}; a break-out is half its living players or more, four at least, out past its doors)": bo is not None and not lost}
                out.append(_play(M, "pinned", "own", tm, t, t1, [], f"{M.m.tag[tm]} is held in its own base or pit by {M.m.tag[3 - tm]}'s main team ({_pit_words(M, tm, t, t1)}; base res in {round(st.next_res(t) - t)} s)",
                                 "Hold the NPCs and lose nobody until the base res, or break out" if dead else "Lose no player and no NPC while held in, or break out", {}, any_of=hold,
                                 beside={"deaths": [K.died(tm, t, t1), K.died(3 - tm, t, t1)], "pit_npcs_lost": K.npcs(tm, t, t1, pit=True), "pinned_s": b - a}, broke_out=bo is not None))
            t = st.next_res(t) if dead else b
    return out


# ---- in their base as their dead come back (gap 5)
def res_plays(M, K):
    out, T = [], M.T
    for r in M.caught():
        B, tm = r["t"], r["tm"]
        out.append(_play(M, "base res", "own", tm, B - 20, B + 30, [], f"{r['team']} has {r['attackers']} in {M.m.tag[3 - tm]}'s base at the base res ({r['defenders']} defending, {r['coming_back']} coming back): {r['stayed']} stay" + (f", {r['attackers'] - r['stayed']} leave as the res lands or die" if r['stayed'] < r['attackers'] else ""),
                         "Be out, or set for the fight, when they res", {"none of the players in their base dies in the 30 s after the res": K.died(tm, B, B + 30, set(r["ids"])) == 0},      # the test covers the players of the play: a team mate who dies elsewhere, defending a split at home, did not die of the base res (his mark on hold v Men 4:00, Classic: "ranger dies on split, not because of base res")
                         beside={"deaths_after": K.died(tm, B, B + 30, set(r["ids"])), "deaths_elsewhere": K.died(tm, B, B + 30) - K.died(tm, B, B + 30, set(r["ids"])), "outnumbered": r["outnumbered"]}, call="stayed through the res"))
    for r in M.timing():
        if r["kind"] != "left before res": continue
        B, tm = r["t"] + r["s"], r["tm"]
        out.append(_play(M, "base res", "own", tm, r["t"], B + 30, r["who"], f"{r['team']} leaves {r['foe']}'s base {r['s']} s before the base res ({r['coming_back']} coming back)",
                         "Be out, or set for the fight, when they res", {"nobody of ours dies in the 30 s after the res": K.died(tm, B, B + 30) == 0}, beside={"deaths_after": K.died(tm, B, B + 30)}, call="left before the res"))
    return out


def _pit_words(M, tm, t, t1):
    """The pit NPCs alive at the start of a stretch, written out with the hall's own roster (three pit archers on Isle of Solitude), and those lost in it
    (his words on Men v Crew 24:48 and 옷옷옷옷 v RACK 9:00: "check NPC counts": "K2 A2 B1" was the count at the start, with a knight dying 9 s later)."""
    st = M.st
    N = [(z, v["kind"]) for z, v in st.geo.npcs.items() if v["team"] == tm and v.get("pit") and v["kind"] != "guild_lord"]
    tot = collections.Counter(k for _, k in N); live = collections.Counter(k for z, k in N if st.npc_dead.get(z, 1e9) > t)
    lost = sorted((st.npc_dead[z], k) for z, k in N if t < st.npc_dead.get(z, 1e9) <= t1)
    words = f"pit NPCs alive at {clock(t)}: {live['knight']} of {tot['knight']} knights, {live['archer']} of {tot['archer']} pit archers, the Bodyguard {'alive' if live['bodyguard'] else 'dead'}"
    return words + ("; lost while held: " + ", ".join(f"{'the Bodyguard' if k == 'bodyguard' else 'a pit archer' if k == 'archer' else 'a ' + k} at {clock(td)}" for td, k in lost) if lost else "")


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
    out = opening_plays(M, K) + flag_plays(M, K, pinned_at) + push_plays(M, K) + split_plays(M, K) + numbers_plays(M, K, M.triggers(), recs, pinned_at) + boost_plays(M, K, recs, pinned_at) + pinned_plays(M, K) + res_plays(M, K) + lord_plays(M, K)
    fr = _flag_rows(M)
    for p in out:                                                          # on each split's record: a flag run of the split's team, and of the team it is sent against, under way when it is told
        s_ = p.get("split")
        if s_ is not None and "runner_out" not in s_: s_["runner_out"] = [any(int(f_.get("off", f_["s0"])) <= s_["told"] <= f_["e"] and f_["tm"] == k_ for f_ in fr) for k_ in (s_["tm"], 3 - s_["tm"])]
    out = [p for p in out if p["t0"] < M.over - SPLIT_STEP and not (p["play"] == "base res" and p["t0"] + 20 >= M.over - SPLIT_STEP)]      # nothing is told from the second the match is over, and a base res that falls on it is none (Moments.over)
    out.sort(key=lambda p: (p["t0"], p["tm"], p["play"]))
    rid = M.m.o["meta"]["id"]
    for i, p in enumerate(out): p["rid"], p["id"] = rid, f"{rid[:8]}-{p['play'].replace(' ', '_')}-{p['tm']}-{p['t0']}-{i}"
    allocation(recs, out, pinned_at)
    return out


def selfcheck(M):
    """The engine checks itself (R-488: "a player cannot be part of 2 fights at once"): every player counted, for JOIN_S or longer, both in a main fight's numbers
    and on a split or its defence in the same seconds. Each is a fault in one of the two readings, counted aloud (R-460) and shown with the game."""
    out, role = [], M.m.roles
    for sp in getattr(M, "_split_at", None) or []:
        for e in getattr(M, "_numbers_told", None) or []:
            both = collections.defaultdict(list)
            for t, (s_, d_) in sp["at"].items():
                for a in (s_ | d_) & e["at"].get(t, frozenset()): both[a].append(t)
            for a, ts in both.items():
                if len(ts) * SPLIT_STEP >= JOIN_S:
                    out.append({"who": f"{M.m.tag[M.m.team(a)]}'s {role[a]}", "from": min(ts), "to": max(ts), "s": len(ts) * SPLIT_STEP, "in": [sp["name"], f"the main fight's numbers from {clock(e['start'])}"]})
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
