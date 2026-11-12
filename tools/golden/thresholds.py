"""The draft thresholds behind joins, swaps, split fights, ground moves, side fights, the pit and undefended splits
(common.py; Claude's drafts, to confirm), with what each yields over every counted match beside it.

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


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "run": run(a[1], int(a[a.index("--jobs") + 1]) if "--jobs" in a else 2)
    elif len(a) >= 2 and a[0] == "show": show(a[1])
    else: print(__doc__)
