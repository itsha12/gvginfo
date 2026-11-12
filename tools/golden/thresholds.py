"""The thresholds behind joins, swaps, split fights, ground moves, side fights, the pit and undefended splits (common.py;
confirmed, R-390) and the draft thresholds of reading step 2 (pushing the flagger, flag route, flag lead, posture, the
timing choices, monk counts, who is on the Guild Lord; Claude's drafts, to confirm), with what each yields over every
counted match beside it.

Usage:  python3 tools/golden/thresholds.py run /tmp/thresholds.json [--jobs 2]     (every counted match, about 20 minutes)
        python3 tools/golden/thresholds.py show /tmp/thresholds.json
A report tool (outside the engine folder, in no cache key). Where a record keeps the measured quantity, its spread is
shown, so the effect of a stricter threshold can be read without another run; a looser one needs a run."""
import collections, json, os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "replay_analysis")


def one(rid):
    try:
        from replaylib import Match
        from state import GameState
        import moments, story
        st = GameState(Match.from_branch(rid))
        if not st.hall: return rid, None
        M = moments.Moments(st)
        mv, sf, gr, at = M.moves(), M.split_fights(), M.ground(), M.attempts()
        others = lambda x: sum(1 for a in st.players[x["tm"]] if a not in x["ids"] and M.AL[a][min(int(x["t_in"]), M.T)])      # team mates alive who are not in it
        dead = lambda x: sum(1 for a in st.players[x["tm"]] if not M.AL[a][min(int(x["t_in"]), M.T)])
        renamed = [x for x in at if x["kind"] == "push" and others(x) <= 2 and dead(x) >= 2 and any(y["kind"] == "split" and y["tm"] == x["tm"] and 0 <= x["t_in"] - y["t1"] <= 20
                                                                                 and len(set(y["ids"]) & set(x["ids"])) * 2 >= len(x["ids"]) for y in at)]
        return rid, {
            "T": M.T,
            "joins": [[len(x["ids"]), min(s for _, _, s in x["each"])] for x in mv if x["kind"] == "join"],
            "leaves": [[len(x["ids"]), min(s for _, _, s in x["each"])] for x in mv if x["kind"] == "leave"],
            "split_fights": [[r["t1"] - r["t0"], r["linked_s"], min(r["n"]), len(r["attempts"])] for r in sf],
            "swaps": [[abs(s["t_in"] - s["t_out"])] for r in sf for s in r["swaps"]],
            "ground": [[g["group"], g["way"], g["dist"], g["t1"] - g["t0"], g["n"], bool(story._ground_told(M, g))] for g in gr],
            "undefended": [[r["t1"] - r["t"], bool(r["had"])] for r in M.undefended()],
            "on_pit": [[r["t1"] - r["t"], len(r["ids"])] for r in M.on_pit()],
            "lone": [x.get("solo") for x in at if x.get("solo")],
            "attempts": [sum(1 for x in at if x["kind"] == "split"), sum(1 for x in at if x["kind"] == "push"), len(renamed)],
            "pulled": sum(len(r["pulled"]) for r in sf),
            "side_cut_s": len(M.side_cut) * 2,
            "missed_pickups": len(M.missed_pickups),
            "captures": sum(1 for L in M.flag_lives() if L["how"] == "captured"),
            # reading step 2 (R-371, R-373, R-375 to R-378)
            "pushes": [[r["t1"] - r["t"], len(r["ids"]), r["acts"], bool(r["main"]), r["doing"], bool(r["died"]), bool(r["dropped"]), r["delay_s"], r["flag"]] for r in M.flag_pushes()],
            "routes": [[fr["route"], fr["back_route"], fr["door"], fr["how"]] for fr in M.flags_record()],
            "lead": [[r["level"], r["t1"] - r["t"]] for r in M.flag_lead()],
            "posture": [[r["t1"] - r["t"], r["n"], bool(r["main"]), r["kind"], r["end"], r["facing"], len(r["joined"])] for r in M.posture()],
            "timing": [[r["kind"], r["s"], r.get("boost_in")] for r in M.timing()],
            "holds": [[fr["held_s"], fr["cap_boost_in"]] for fr in M.flags_record() if fr["how"] == "captured"],
            "monks": [[r["n"], r["was"], r["of"]] for r in M.monk_counts()],
            "lord": [[round(r["t1"] - r["t"]), len(r["ids"]), r["hits"], r["defenders"]] for r in M.on_lord()],
            "pregame": [bool(v["holder"] is not None) for v in M.pregame().values()],
            "story_lines": len(story.story(M, 0, None)),
        }
    except Exception as e:
        return rid, {"error": f"{type(e).__name__}: {e}"}


def run(path, jobs):
    import multiprocessing
    sys.path.insert(0, ENGINE); os.chdir(ENGINE)
    import common
    out = {}
    with multiprocessing.Pool(jobs) as pool:
        for rid, rec in pool.imap_unordered(one, common.replay_ids(), chunksize=4):
            if rec is not None: out[rid] = rec
    json.dump(out, open(path, "w"))
    print(len(out), "matches;", sum("error" in v for v in out.values()), "errors", [(k[:8], v["error"]) for k, v in out.items() if "error" in v][:5])


def q(xs, ps=(10, 25, 50, 75, 90)):
    xs = sorted(xs)
    return "no cases" if not xs else ", ".join(f"{p}%: {xs[min(int(len(xs) * p / 100), len(xs) - 1)]:g}" for p in ps)


def show(path):
    D = {k: v for k, v in json.load(open(path)).items() if "error" not in v}
    n = len(D); mins = sum(v["T"] for v in D.values()) / 60
    cat = lambda k: [x for v in D.values() for x in v[k]]
    J, L, SF, SW, G, U, P = (cat(k) for k in ("joins", "leaves", "split_fights", "swaps", "ground", "undefended", "on_pit"))
    print(f"{n} matches, {round(mins)} minutes of play")
    print(f"joins {len(J)} ({len(J) / mins * 10:.1f} per 10 minutes; players arriving together count once), leaves {len(L)} ({len(L) / mins * 10:.1f} per 10 minutes)")
    print(f"  how long the joiner then stayed (s): {q([x[1] for x in J])}; joins of one player {sum(x[0] == 1 for x in J)}, of two or more {sum(x[0] > 1 for x in J)}")
    print(f"split fights {len(SF)} ({len(SF) / n:.2f} a match); length (s): {q([x[0] for x in SF])}; opening two a side {sum(x[2] == 2 for x in SF)}, three or more {sum(x[2] >= 3 for x in SF)}")
    print(f"  covering two or more split attempts as one fight: {sum(x[3] >= 2 for x in SF)}")
    print(f"swaps {len(SW)} ({len(SW) / n:.2f} a match); seconds between the one going out and the one coming in: {q([x[0] for x in SW])}")
    for grp in ("main", "split"):
        g = [x for x in G if x[0] == grp]
        print(f"ground moves, {grp}: {len(g)} ({len(g) / n:.1f} a match), told in the story {sum(x[5] for x in g)} ({sum(x[5] for x in g) / n:.1f} a match); back {sum(x[1] == 'back' for x in g)}, up {sum(x[1] == 'up' for x in g)}")
        print(f"  distance walked: {q([x[2] for x in g])}; seconds start to end: {q([x[3] for x in g])}; players: {q([x[4] for x in g], (25, 50, 75))}")
    print(f"undefended stretches {len(U)} ({len(U) / n:.2f} a match), of which defended earlier {sum(x[1] for x in U)}; length (s): {q([x[0] for x in U])}")
    print(f"on the pit NPCs: {len(P)} stretches ({len(P) / n:.2f} a match); length (s): {q([x[0] for x in P])}; players on them: {q([x[1] for x in P], (25, 50, 75))}")
    at = [v["attempts"] for v in D.values()]
    print(f"split attempts {sum(x[0] for x in at)}, main team pushes {sum(x[1] for x in at)}; pushes that are a split renamed the main team with two or more team mates dead and two or fewer alive elsewhere (R-392 keeps these splits): {sum(x[2] for x in at)} (in {sum(1 for x in at if x[2])} matches)")
    print(f"pulled off a split fight onto the main fight: {sum(v['pulled'] for v in D.values())} (in {sum(1 for v in D.values() if v['pulled'])} matches)")
    lone = collections.Counter(cat("lone"))
    print(f"lone attempts {sum(lone.values())}: splits by R-381 {lone['split']}, other {lone['other']}")
    sc = [v["side_cut_s"] for v in D.values()]
    print(f"side fights cut from a bigger fight: in {sum(1 for x in sc if x)} matches; seconds a match where it happens: {q(sc)}")
    mp, cp = sum(v["missed_pickups"] for v in D.values()), sum(v["captures"] for v in D.values())
    print(f"captures {cp}; pickups the observer missed, read from the capture {mp} (in {sum(1 for v in D.values() if v['missed_pickups'])} matches)")
    if not all("pushes" in v for v in D.values()): return
    C = collections.Counter
    print(f"\nReading step 2 (drafts to confirm). Story lines a match: {q([v['story_lines'] for v in D.values()])}")
    X = cat("pushes")
    print(f"pushing the flagger: {len(X)} ({len(X) / n:.1f} a match; matches with none {sum(not v['pushes'] for v in D.values())}); length (s): {q([x[0] for x in X])}; players pushing: {q([x[1] for x in X], (25, 50, 75))}; by the main team {sum(x[3] for x in X)}")
    print(f"  the flagger was: {dict(C(x[4] for x in X))}; he died {sum(x[5] for x in X)}, dropped the flag {sum(x[6] for x in X)}; shorter than PUSHFLAG_S (kept for the drop or the death) {sum(x[0] < 6 for x in X)}; one hit or skill only {sum(x[2] == 1 for x in X)}")
    print(f"  what became of that flag: {dict(C(x[8] for x in X))}")
    X = cat("routes")
    print(f"flag routes: {len(X)} flags; way to the stand read {dict(C(x[0] for x in X if x[0]))}; way back read {dict(C(x[1] for x in X if x[1]))}; out by the own back door {sum(x[2] == 'back door' for x in X)}, front door {sum(x[2] == 'front door' for x in X)}")
    X = cat("lead")
    for lv in ("full", "half"):
        xs = [x[1] for x in X if x[0] == lv]
        print(f"flag lead, {lv} a flag up: {len(xs)} stretches ({len(xs) / n:.1f} a match); length (s): {q(xs)}")
    X = cat("posture")
    print(f"posture: {len(X)} ({len(X) / n:.2f} a match); length (s): {q([x[0] for x in X])}; players: {q([x[1] for x in X], (25, 50, 75))}; main team {sum(x[2] for x in X)}; at {dict(C(x[3] for x in X))}")
    print(f"  ended: {dict(C(x[4] for x in X))}; nobody facing it {sum(x[5] == 0 for x in X)}; a team mate joined while it waited {sum(x[6] > 0 for x in X)}")
    X = cat("timing")
    for k in ("delayed pickup", "held to the boost", "stayed to help", "left before res"):
        xs = [x[1] for x in X if x[0] == k]
        print(f"timing, {k}: {len(xs)} ({len(xs) / n:.2f} a match); seconds: {q(xs)}")
    H = cat("holds"); hb = [x for x in H if x[1] is not None]
    print(f"  captures {len(H)}; in hand at the stand before the cap (s): {q([x[0] for x in H])}; held HOLD_S or longer {sum(x[0] >= 15 for x in H)}; of {len(hb)} capped against the enemy's stand, seconds to the enemy's boost: {q([x[1] for x in hb])}")
    X = cat("monks")
    print(f"monk count changes in the main fight: {len(X)} ({len(X) / n:.1f} a match); down {sum(x[1] is None or x[0] < x[1] for x in X)}, back up {sum(x[1] is not None and x[0] > x[1] for x in X)}; down to one {sum(x[0] == 1 and (x[1] is None or x[1] > 1) for x in X)}, to none {sum(x[0] == 0 for x in X)}")
    X = cat("lord"); told = [x for x in X if x[2] >= 3 and x[0] >= 4]
    print(f"on the Guild Lord: {len(X)} stretches, {len(told)} told ({len(told) / n:.1f} a match); length (s): {q([x[0] for x in told])}; players: {q([x[1] for x in told], (25, 50, 75))}; nobody of the defenders in the pit {sum(x[3] == 0 for x in told)}")
    pg = cat("pregame")
    print(f"pre-game flag: in hand at the gates for {sum(pg)} of {len(pg)} teams")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "run": run(a[1], int(a[a.index("--jobs") + 1]) if "--jobs" in a else 2)
    elif len(a) >= 2 and a[0] == "show": show(a[1])
    else: print(__doc__)
