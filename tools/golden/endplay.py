"""The play for 28:00 (R-640 to R-646, R-650 to R-654). The record is in the engine, `Moments.end_play` (moments.py), and
`jobs.lord_plays` tells the Lord play from it. This tool says the record, summarises it over every match and writes
rows of it for the Lord push page (the eight he marked on 2026-11-23 were written as its draft).

His description: late in the match each team decides whom it sends to the enemy's base (for the kill, or for the most
Lord damage) and whom it keeps to defend, and where both teams do so the two are one play. "28" is the end of the
match, not the clock: a replay may run past 28:00, and a play for 28:00 may end in a Lord kill before it.

What this reads, from where the players stand and never from hits on a Lord: at the end of play (the Lord's death,
or 6 s before the match is over, the base res of 28:00 being recorded a few seconds early) every player's last place
alive: SENT, on the enemy's ground within LORD_BASE_R of their Guild Lord (R-446: in the base, not only beside him; a
player who stops at their footmen or their door has not been sent: Crew v cope 24:29, three of Crew's four never came
within 4,000 of cope's Lord, his "NO corresponding push"); KEPT, on his own ground; or neither (out in the field, at
their footmen or door, or dead since before LOOK_FROM). A player dead at the end counts where he died, and one who
died on his way into their base was sent (his mark on hold v Dz 26:15, Classic: "hold sends 3 but they die before
reaching base"): on the enemy's ground at their door, base or pit with no turn-off to mid left ahead, for JOIN_S or
having stood within LORD_BASE_R on it; the row says where he died. A living player who stops short is not sent. Each
player's "since" is when his last unbroken stay there began (other places for JOIN_S or less do not break it; a death
does). A team's send is read while the play is on, not at its last second (R-654): a living player who left their base
or his home less than JOIN_S before the end counts where he stood (R-579), and the row says when he left. A team's send
is the middle of its sent players' "since", and the play is SET at the later team's send.

A play for 28:00 against a push before it (R-641, R-646). His three signs of a push before it, which he reads together:
it is early (CUT, 25:00, his line, R-653), one team is already in the enemy's base, and the other makes no push of its
own in return. As read here: a match run to its end always ends in a play for 28:00; a match ended by a Lord kill
holds one only when the team that killed him sent its players at CUT or later. The summary sets the other two signs beside the clock.

    python3 tools/golden/endplay.py <report id> ...        one match or more, as sentences
    python3 tools/golden/endplay.py all <out.json>         every counted match that ends at FROM or later, and the summary
    python3 tools/golden/endplay.py rows <main>/data/model/lord_rows.json <report id>=<why picked> ...
                                                           rows of the draft for him to mark on Model > Game review > Lord push
                                                           (R-633), one row a match for both teams; rows are added, and a row
                                                           already in the file is never written again (his marks keep their text)
"""
import collections, json, multiprocessing, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools", "replay_analysis"))
import common

LOOK_FROM, CUT, ALREADY_S = common.END_LOOK_FROM, common.PLAY28_FROM, common.END_ALREADY_S        # the settings are the engine's (common.py): CUT is his line (R-653)
FROM = CUT                   # matches over before this are not summarised
cl = lambda t: f"{int(t) // 60}:{int(t) % 60:02d}"


def load(rid):
    from replaylib import Match
    from state import GameState
    from moments import Moments
    return Moments(GameState(Match.from_branch(rid)))


def end_play(M):
    """The record is the engine's, `Moments.end_play` (R-362): this tool only says it, summarises it and writes its rows."""
    return M.end_play()


def died(r):
    """How a player's death is said: where he died when he died on his way into their base (the record's `on_way`), or sent and dead outside their base."""
    if not r.get("died"): return f", left {cl(r['left'])}" if r.get("left") else ""
    return f", died {cl(r['died'])}" + (f" at {r['died_at']}" + ("" if r.get("reached") else ", never in their base") if r.get("on_way") else "")


def say(rid, o):
    print(f"{' v '.join(o['teams'])}, {o['date']}: https://gvg.report/report/{rid}#map")
    if o.get("short"): print(f"  over at {cl(o['end'])}: too early to read"); return
    print(f"  read at {cl(o['end'])}" + (f", {o['lord_killed']}'s Guild Lord killed" if o["lord_killed"] else ", the match run to its end") + f"; {o['shape']}" + (f", set at {cl(o['set'])}: a {o['kind']}" if o["set"] is not None else ""))
    for tg, rec in o["players"].items():
        for place, word in (("sent", "sends"), ("kept", "keeps"), ("field", "in the field"), ("dead", "dead throughout")):
            xs = sorted((r for r in rec if r["place"] == place), key=lambda r: r["since"] or 0)
            if xs: print(f"    {tg} {word} {len(xs)}: " + ", ".join(f"{r['role']} ({'before ' if r.get('before') else ''}{cl(r['since']) if r['since'] is not None else ''}{died(r)})" for r in xs))


def row(rid, why):
    """One row of the page for a match: the draft's reading of its end as sentences, with what each team had when the arrangement was set."""
    M = load(rid); o = end_play(M); st, m = M.st, M.m
    if o.get("short") or o["set"] is None: sys.exit(f"endplay rows: {rid[:8]} has no arrangement to tell")
    n = lambda v: f"{round(v):,}"
    tms = list(st.teams); A, B = (m.tag[t] for t in tms); S = o["sends"]
    t0 = int(min(v["send"] for v in S.values() if v["send"] is not None)); t1, tset = int(o["end"]), int(o["set"])
    won = m.tag.get((m.o["meta"].get("result") or {}).get("winning_team_id"))
    def grp(tg, place):
        xs = sorted((r for r in o["players"][tg] if r["place"] == place), key=lambda r: r["since"] or 0)
        return ", ".join(f"{r['role']} ({'before ' if r.get('before') else 'from '}{cl(r['since'])}{died(r)})" for r in xs)
    side = lambda tg: f"{tg} sends {S[tg]['sent'] or 'nobody'} and keeps {S[tg]['kept'] or 'nobody'}"
    if o["kind"] == "play for 28:00":
        reads = f"A play for 28:00, as the draft reads it: {side(A)}; {side(B)}; set at {cl(tset)}."
    else:
        K = next(t for t in o["teams"] if t != o["lord_killed"]); L = o["lord_killed"]
        reads = (f"A push before the play for 28:00, as the draft reads it: {K} has {S[K]['sent']} in {L}'s base, sent at {cl(o['killer_send'])}, and keeps {S[K]['kept'] or 'nobody'}; "
                 f"{L} sends {S[L]['sent'] or 'nobody'} in return" + (f" at {cl(S[L]['send'])}" if S[L]["send"] is not None else "") + f" and keeps {S[L]['kept'] or 'nobody'}.")
    lines = []
    for tg in (A, B):
        for place, word in (("sent", "sent to the enemy's base"), ("kept", "kept at home"), ("field", "in the field or at the enemy's footmen")):
            g = grp(tg, place)
            if g: lines.append(f"{tg} {word}: {g}.")
    pit = lambda tm, t: sum(1 for z, v in st.geo.npcs.items() if v["team"] == tm and v.get("pit") and v["kind"] != "guild_lord" and st.npc_dead.get(z, 1e9) > t)
    mor = lambda tm, t: sum(st.morale(a, t) for a in st.players[tm])
    alive = lambda tm, t: sum(1 for a in st.players[tm] if M.AL[a][t])
    hits = lambda tm, a, b: sum(v for u, _, v in M.lord_hits.get(tm, ()) if a <= u <= b)          # the engine's sum of the recorded hits on tm's Lord
    for t, word in ((t0, "the first group went"), (tset, "it was set")):
        if word == "it was set" and tset - t0 < 20: continue
        lines.append(f"What each team had when {word} ({cl(t)}): pit NPCs alive, {A} {pit(tms[0], t)} and {B} {pit(tms[1], t)}; morale summed over the eight, {A} {mor(tms[0], t):+d} and {B} {mor(tms[1], t):+d}; "
                     f"players alive, {A} {alive(tms[0], t)} and {B} {alive(tms[1], t)}; Lord damage so far by the engine's sum of the recorded hits, {n(hits(tms[1], 0, t))} by {A} and {n(hits(tms[0], 0, t))} by {B}; the next base res at {cl(st.next_res(t))}.")
    dead = lambda tm: sum(1 for a in st.players[tm] for td in st.death_times.get(a, []) if t0 <= td <= t1)
    lines.append((f"{o['lord_killed']}'s Guild Lord is killed at {cl(t1)}" if o["lord_killed"] else "The match runs to its end and is decided by Lord damage") + f"; {won} wins. Deaths from {cl(t0)}: {A} {dead(tms[0])}, {B} {dead(tms[1])}.")
    if o["lord_killed"]:
        lines.append(f"Your three signs of a push before it (R-646): the team that kills the Lord sent at {cl(o['killer_send'])}, {'before' if o['killer_send'] < CUT else 'after'} {cl(CUT)}; "
                     f"a team already in the enemy's base two minutes or more before it was set, {'yes' if o['already'] else 'no'}; sent in return by {o['lord_killed']}, {o['in_return'] or 'nobody'}.")
    lines.append(f"Picked for: {why}.")
    gvg = {l["team"]: l.get("taken") for l in m.o.get("lords", [])}
    unseen = set(m.o.get("integrity", {}).get("lord_damage_unobserved", []))
    dmg = {"push": [round(hits(tms[0], t0, t1 + 6)), round(hits(tms[1], t0, t1 + 6))], "match_gvg": [gvg.get(tms[0]), gvg.get(tms[1])], "match_hits": [round(hits(tms[0], 0, M.T)), round(hits(tms[1], 0, M.T))],
           "lords": [A, B], "unobserved": [3 - tms[0] in unseen, 3 - tms[1] in unseen]}
    if None in dmg["match_gvg"]: sys.exit(f"endplay rows: {rid[:8]} has no gvg.report Lord total (R-460)")
    said = (f"Lord damage. From {cl(t0)}, by the engine's sum of the recorded hits: {n(dmg['push'][0])} on {A}'s Lord, {n(dmg['push'][1])} on {B}'s. Whole match, gvg.report's own total: {n(dmg['match_gvg'][0])} on {A}'s Lord, "
            f"{n(dmg['match_gvg'][1])} on {B}'s (the engine's summed hits: {n(dmg['match_hits'][0])} and {n(dmg['match_hits'][1])}).")
    return {"id": f"e:{rid[:8]}-end", "kind": "end", "play": None, "rid": rid, "teams": [A, B], "map": o["map"], "date": o["date"], "length_s": int(M.T), "t0": t0, "t1": t1, "reads": reads, "lines": lines,
            "damage": dmg, "damage_said": said, "gvg_lines": [], "calls": [], "draft": {k: o[k] for k in ("end", "lord_killed", "set", "shape", "kind", "sends", "killer_send", "in_return", "already")}, "picked_for": why,
            "text": " | ".join([reads] + lines + [said])}


def _one(rid):
    M = load(rid)
    return rid, (end_play(M) if M.hall is not None else None)


def summary(R):
    late = [v for v in R.values() if v and not v.get("short") and v["end"] >= FROM]
    q = lambda xs, p: cl(sorted(xs)[int(p * (len(xs) - 1))])
    print(f"{len(R)} counted matches; {sum(1 for v in R.values() if v and not v.get('short'))} are still played at {cl(LOOK_FROM + 60)}; {len(late)} end at {cl(FROM)} or later")
    for name, grp in (("run to the end", [v for v in late if not v["lord_killed"]]), ("ended by a Lord kill", [v for v in late if v["lord_killed"]])):
        sets = [v["set"] for v in grp if v["set"] is not None]
        print(f"\n{name}: {len(grp)}; " + ", ".join(f"{k} {n}" for k, n in collections.Counter(v["shape"] for v in grp).most_common()))
        print("  sent, the larger group against the smaller: " + ", ".join(f"{a} v {b} ({n})" for (a, b), n in collections.Counter(tuple(sorted((s["sent"] for s in v["sends"].values()), reverse=True)) for v in grp).most_common(8)))
        if sets:
            print(f"  set at: a tenth by {q(sets, .1)}, a quarter by {q(sets, .25)}, half by {q(sets, .5)}, three quarters by {q(sets, .75)}, nine tenths by {q(sets, .9)}")
            print(f"  set before {cl(CUT)}: {sum(1 for x in sets if x < CUT)}; from then to 26:00: {sum(1 for x in sets if CUT <= x < 1560)}; at 26:00 or later: {sum(1 for x in sets if x >= 1560)}")
        for kind in ("play for 28:00", "push before it"):
            g = [v for v in grp if v.get("kind") == kind]
            if g: print(f"  {kind}: {len(g)}; both send {sum(1 for v in g if v['shape'] == 'both send')}, one sends {sum(1 for v in g if v['shape'] == 'one sends')}; a team already in the enemy's base {ALREADY_S} s or more before it is set: {sum(1 for v in g if v['already'])}"
                        + (f"; sent in return by the team whose Lord died: nobody {sum(1 for v in g if v['in_return'] == 0)}, one player {sum(1 for v in g if v['in_return'] == 1)}, two or more {sum(1 for v in g if (v['in_return'] or 0) >= 2)}" if g[0]["lord_killed"] else ""))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "all":
        with multiprocessing.Pool(int(a[a.index("--jobs") + 1]) if "--jobs" in a else 2) as pool:
            R = dict(pool.imap_unordered(_one, list(common.replay_ids()), chunksize=4))
        json.dump({"about": "The play for 28:00, a draft reading (tools/golden/endplay.py; R-640 to R-642): for every counted match ending at 24:30 or later, each player's last place alive at the end of play (sent, kept, field) and since when, each team's send and the second the play is set. A draft: nothing in the engine reads it.",
                   "matches": {k: v for k, v in R.items() if v and not v.get("short") and v["end"] >= FROM}}, open(a[1], "w"), ensure_ascii=False, separators=(",", ":"))
        summary(R)
    elif a and a[0] == "rows":
        D = json.load(open(a[1], encoding="utf-8")); have = {r["id"] for r in D["rows"]}; new = []
        for arg in a[2:]:
            pre, _, why = arg.partition("=")
            r = row(next((x for x in common.replay_ids() if x.startswith(pre)), pre), why or "the draft reading")
            if r["id"] in have: print(f"already on the page, left as it is: {r['id']}"); continue
            new.append(r); print(f"\n{' v '.join(r['teams'])}, {r['date']}, {cl(r['t0'])} to {cl(r['t1'])}\n  " + "\n  ".join([r["reads"]] + r["lines"] + [r["damage_said"]]))
        D["rows"] += new
        note = " Rows with `kind` \"end\" are the draft reading of the play for 28:00 (tools/golden/endplay.py rows, R-640 to R-646): one row a match for both teams, whom each sends and keeps and since when; their Lord damage is the engine's sum of the recorded hits from the first send, beside gvg.report's match total."
        if note not in D["about"]: D["about"] += note
        json.dump(D, open(a[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print(f"\n{len(new)} rows added; {len(D['rows'])} on the page")
    else:
        for pre in a:
            rid = next((r for r in common.replay_ids() if r.startswith(pre)), pre)
            say(*_one(rid))
