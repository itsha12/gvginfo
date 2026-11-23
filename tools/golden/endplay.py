"""The play for 28:00, a DRAFT reading (R-640 to R-642, R-644). Not in the engine: no play reads it and it moves none.

His description: late in the match each team decides whom it sends to the enemy's base (for the kill, or for the most
Lord damage) and whom it keeps to defend, and where both teams do so the two are one play. "28" is the end of the
match, not the clock: a replay may run past 28:00, and a play for 28:00 may end in a Lord kill before it.

What this reads, from where the players stand and never from hits on a Lord: at the end of play (the Lord's death,
or 6 s before the match is over, the base res of 28:00 being recorded a few seconds early) every player's last place
alive: SENT, on the enemy's ground within LORD_BASE_R of their Guild Lord (R-446: in the base, not only beside him; a
player who stops at their footmen or their door has not been sent: Crew v cope 24:29, three of Crew's four never came
within 4,000 of cope's Lord, his "NO corresponding push"); KEPT, on his own ground; or neither (out in the field, at
their footmen or door, or dead since before LOOK_FROM). A player dead at the end counts where he died. Each player's "since" is
when his last unbroken stay there began (other places for JOIN_S or less do not break it; a death does). A team's send
is the middle of its sent players' "since", and the play is SET at the later team's send.

A play for 28:00 against a push before it (R-641, R-646). His three signs of a push before it, which he reads together:
it is early (CUT, 25:00, his "maybe"), one team is already in the enemy's base, and the other makes no push of its
own in return. As read here: a match run to its end always ends in a play for 28:00; a match ended by a Lord kill
holds one only when the team that killed him sent its players at CUT or later. The summary sets the other two signs beside the clock.

    python3 tools/golden/endplay.py <report id> ...        one match or more, as sentences
    python3 tools/golden/endplay.py all <out.json>         every counted match that ends at FROM or later, and the summary
"""
import collections, json, math, multiprocessing, os, statistics, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools", "replay_analysis"))
import common

LOOK_FROM = 20 * 60          # how far back a player's last stay is followed (Claude's draft)
CUT = 25 * 60                # an arrangement set before this is a push before the play for 28:00 (R-646, his "Maybe we should even make the cut off at 25": Claude's draft as a line, his to confirm)
FROM = CUT                   # matches over before this are not summarised
ALREADY_S = 120              # "already in the enemy's base": a team's first sent player there this long before the arrangement is set (Claude's draft)
END_BACK = 6                 # read this long before the match is over: the base res of 28:00 is recorded a few seconds early
cl = lambda t: f"{int(t) // 60}:{int(t) % 60:02d}"


def load(rid):
    from replaylib import Match
    from state import GameState
    from moments import Moments
    return Moments(GameState(Match.from_branch(rid)))


def lord_death(M):
    m = M.m
    for tm in M.st.teams:
        td = next((r[0] / 10 for r in m.o["ev"] if r[1] == "dt" and isinstance(r[2], int) and r[2] < len(m.A) and m.A[r[2]].get("npc") == "guild_lord" and m.A[r[2]].get("team") == tm), None)
        if td is not None: return tm, td
    return None, None


def where(M, a, t, tm):
    if not M.AL[a][t]: return "dead"
    k, s = M.place_at(a, t)
    if s is None or k in ("stand", "greater stand", "field"): return "field"
    if s == M.st.side.get(tm): return "kept"
    return "sent" if math.dist(M.P[a][t], M.hall.lord[s]) <= common.LORD_BASE_R else "field"


def end_play(M):
    st = M.st
    ltm, ltd = lord_death(M)
    E = min(int(ltd) if ltd is not None else M.over, 28 * 60, M.T) - (0 if ltd is not None else END_BACK)
    out = {"end": E, "lord_killed": M.m.tag[ltm] if ltm else None, "teams": [M.m.tag[tm] for tm in st.teams], "map": M.m.o["meta"].get("map"), "date": M.day, "players": {}}
    if E < LOOK_FROM + 60: return dict(out, short=True)
    for tm in st.teams:
        rec = []
        for a in st.players[tm]:
            s = [where(M, a, t, tm) for t in range(LOOK_FROM, E + 1)]
            i, died = len(s) - 1, None
            while i >= 0 and s[i] == "dead": i -= 1
            if i < 0: rec.append({"role": M.m.roles[a], "place": "dead", "since": None, "died": None}); continue
            if i < len(s) - 1: died = LOOK_FROM + i + 1
            F, j, first = s[i], i, i
            while j >= 0:
                if s[j] == F: first = j; j -= 1; continue
                k = j
                while k >= 0 and s[k] != F: k -= 1
                if k < 0 or j - k > common.JOIN_S or "dead" in s[k + 1:j + 1]: break
                j = k
            rec.append({"role": M.m.roles[a], "place": F, "since": LOOK_FROM + first, "before": first == 0, "died": died})
        out["players"][M.m.tag[tm]] = rec
    sends = {}
    for tg, rec in out["players"].items():
        xs = sorted(r["since"] for r in rec if r["place"] == "sent")
        sends[tg] = {"sent": len(xs), "kept": sum(1 for r in rec if r["place"] == "kept"), "send": statistics.median(xs) if xs else None, "first": xs[0] if xs else None}
    out["sends"] = sends
    ss = [v["send"] for v in sends.values() if v["send"] is not None]
    out["set"] = max(ss) if ss else None
    out["shape"] = "both send" if len(ss) == 2 else "one sends" if ss else "neither sends"
    firsts = [v["first"] for v in sends.values() if v["first"] is not None]
    out["already"] = bool(ss) and min(firsts) <= out["set"] - ALREADY_S          # a team stood in the enemy's base well before the arrangement was set
    # A match ended by a Lord kill is read on the send of the team that killed him, not on the later team's: one player of the other team reaching
    # their pit late does not make a push in return (Crew v cope: cope in Crew's base since before 20:00, Crew's Mes/A alone in cope's pit for 9 s at 25:07).
    killer = next((tg for tg in out["teams"] if tg != out["lord_killed"]), None) if out["lord_killed"] else None
    out["killer_send"] = sends[killer]["send"] if killer else None
    out["in_return"] = sends[out["lord_killed"]]["sent"] if killer else None       # how many of the other team were sent in return
    out["kind"] = None if not ss else "play for 28:00" if not killer or (out["killer_send"] is not None and out["killer_send"] >= CUT) else "push before it"
    return out


def say(rid, o):
    print(f"{' v '.join(o['teams'])}, {o['date']}: https://gvg.report/report/{rid}#map")
    if o.get("short"): print(f"  over at {cl(o['end'])}: too early to read"); return
    print(f"  read at {cl(o['end'])}" + (f", {o['lord_killed']}'s Guild Lord killed" if o["lord_killed"] else ", the match run to its end") + f"; {o['shape']}" + (f", set at {cl(o['set'])}: a {o['kind']}" if o["set"] is not None else ""))
    for tg, rec in o["players"].items():
        for place, word in (("sent", "sends"), ("kept", "keeps"), ("field", "in the field"), ("dead", "dead throughout")):
            xs = sorted((r for r in rec if r["place"] == place), key=lambda r: r["since"] or 0)
            if xs: print(f"    {tg} {word} {len(xs)}: " + ", ".join(f"{r['role']} ({'before ' if r.get('before') else ''}{cl(r['since']) if r['since'] is not None else ''}{', died ' + cl(r['died']) if r['died'] else ''})" for r in xs))


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
    else:
        for pre in a:
            rid = next((r for r in common.replay_ids() if r.startswith(pre)), pre)
            say(*_one(rid))
