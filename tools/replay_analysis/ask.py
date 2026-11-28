"""The query tool (R-272, rewired to the new engine at the close, R-845): a match and a moment in, the engine's reading of it out.

    python3 ask.py <report id> <m:ss> [team tag] [--plays <plays file from `moments.py all`>] [--within N]

What it says, for the team named (else both), each part from the engine's own records and in their words:
  1. The position at that second (the state a call is made from: flags, the stand and its boost, players alive and at the main
     fight, the base res, NPCs lost).
  2. The decisions around the moment: every play that covers it or starts within N seconds of it (60 by default), with what each team
     did, the play's job and whether its tests were met (`jobs.plays`; a job met is a result, never a verdict on the call).
  3. How it was carried out: every death in those seconds with the chances missed and what was done (`execution.deaths`), and every
     spike that did not kill with the attack's ruled misses (`execution.fails`).
  4. With `--plays`: for the flag or boost decision nearest the moment, its card with the nearest cases (`cases.case`). That needs
     the plays file of a full run, since similar cases come from every other match; a verdict there is a reading, not advice, until
     the held-out test shows a gain for its scenario.
The form that takes a situation with no match is decided after family 4 (R-845). It reads the engine and writes nothing: a report
module, in no cache key."""
import sys

NEAR_S = 60          # the seconds either side of the moment that count as "around" it


def clock(t): return f"{int(t // 60)}:{int(t % 60):02d}"


def parse_clock(s):
    m, _, x = s.partition(":")
    return int(m) * 60 + int(float(x or 0))


def position_lines(M, tm, t):
    """The position of team tm at second t, in a sentence or two (`Moments._state`)."""
    s, tag, foe = M._state(tm, t), M.m.tag[tm], M.m.tag[3 - tm]
    lead = s["flag_lead"]
    flags = "flag lead not read on this hall" if lead is None else "flags level" if abs(lead) < 0.35 else f"{tag if lead > 0 else foe} ahead on flags by {abs(lead):.1f}"
    stand = {"own": f"{tag} holds the stand", "enemy": f"{foe} holds the stand", "nobody": "nobody holds the stand"}[s["stand"]]
    boost = "" if s["boost_in"] is None else f", boost in {s['boost_in']} s"
    flag = [f"{k} has a flag in hand" for k, v in ((tag, s["own_flag"]), (foe, s["enemy_flag"])) if v]
    return [f"{clock(t)}  {tag}: {flags}; {stand}{boost}; alive {tag} {s['alive'][0]} v {foe} {s['alive'][1]}, at the main fight {s['main'][0]} v {s['main'][1]}; "
            f"base res in {s['res_in']} s; pit NPCs lost {tag} {s['npcs_lost'][0][0]} v {foe} {s['npcs_lost'][1][0]}" + ("; " + "; ".join(flag) if flag else "") + "."]


def answer(rid, t, team=None, plays_file=None, within=NEAR_S):
    from replaylib import Match
    from state import GameState
    from scoreboard import Scoreboard
    import common, moments, jobs, execution as EX
    rid = next((r for r in common.replay_ids() if r.startswith(rid)), rid)
    st = GameState(Match.from_branch(rid))
    M = moments.Moments(st, Scoreboard(st))
    tags = [M.m.tag[k] for k in (1, 2)]
    if team is not None and team not in tags: raise SystemExit(f"no team {team} in this match: {' v '.join(tags)}")
    tms = [k for k in (1, 2) if team is None or M.m.tag[k] == team]
    t = min(max(int(t), 0), M.T)
    L = [f"{' v '.join(tags)}, {clock(t)}: https://gvg.report/report/{rid}#map", "", "1. The position"]
    for k in tms: L += ["   " + x for x in position_lines(M, k, t)]
    # the decisions: the plays that cover the moment, or start within `within` s of it
    P = [p for p in jobs.plays(M) if (p["t0"] <= t <= p["t1"] or abs(p["t0"] - t) <= within) and (team is None or p["team"] == team)]
    L += ["", f"2. The decisions around it ({len(P)} play{'s' if len(P) != 1 else ''}; a job met is a result, not a verdict on the call)"]
    for p in sorted(P, key=lambda p: (p["t0"], p["tm"])):
        tests = "; ".join(f"{k}: {'yes' if v else 'no'}" for k, v in list(p["tests"].items()) + list(p["any_of"].items()))
        L.append(f"   {clock(p['t0'])} to {clock(p['t1'])}  {p['team']}, {p['play']}: {p['scenario']}")
        L.append(f"      job: {p['job']}. {'Met' if p['met'] else 'Not met'}" + (f" ({tests})." if tests else "."))
    if not P: L.append("   No play of the engine's covers this moment.")
    # how it was carried out: the deaths and the spikes that did not kill, in those seconds
    E = EX.Exec(M, rid)
    A = EX.attempts(E); PR = EX.pressure(E, A); TR = EX.triggers(E)
    EX.tagged_parts(E, A, PR, TR); EX.position_parts(E, A, PR, EX.positions(E))
    D = [d for d in EX.deaths(E, A, PR, TR) if abs(d["t"] - t) <= within and (team is None or d["team"] == team)]
    F = [f for f in EX.fails(E, A) if abs(f["t"] - t) <= within and (f["faults"] or f["taken"]) and (team is None or f["team"] == team)]
    L += ["", f"3. How it was carried out ({len(D)} death{'s' if len(D) != 1 else ''}" + ("" if team is None else f" of {team}'s")
          + f", {len(F)} spike{'s' if len(F) != 1 else ''} that did not kill with a ruled miss or its good play, within {within} s)"]
    for d in D: L += ["   " + x for x in EX.death_lines(d, TR)] + [""]
    for f in F: L += ["   " + EX.say_fail(f, TR), ""]
    if not D and not F: L.append("   Nobody died and no failed spike carries a ruled miss in those seconds.")
    out = "\n".join(L).rstrip() + "\n"
    if plays_file:                                         # the flag or boost decision nearest the moment, as its card with the nearest cases
        import contextlib, io, cases
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf): cases.case(plays_file, rid, clock(t))
            out += "\n4. The nearest flag or boost decision, with similar cases (a reading, not advice, until the held-out test shows a gain for its scenario)\n" + "\n".join("   " + x for x in buf.getvalue().splitlines()) + "\n"
        except SystemExit as e: out += f"\n4. No card: {e}\n"
    else: out += "\n4. Similar cases: pass --plays <the plays file of a full run> for the card of the nearest flag or boost decision.\n"
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    opt = lambda k: a[a.index(k) + 1] if k in a else None
    pos = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or a[i - 1] not in ("--plays", "--within"))]
    if len(pos) >= 2: print(answer(pos[0], parse_clock(pos[1]), pos[2] if len(pos) > 2 else None, opt("--plays"), int(opt("--within") or NEAR_S)), end="")
    else: print(__doc__)
