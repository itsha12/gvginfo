"""The thresholds behind joins, swaps, split fights, ground moves, side fights, the pit and undefended splits (common.py;
confirmed, R-390) and the draft thresholds of reading step 2 (pushing the flagger, flag route, flag lead, posture, the
the stand-off, the
timing choices, monk counts, who is on the Guild Lord; confirmed, R-404 to R-407), with what each yields over every
counted match beside it.

Usage:  python3 tools/golden/thresholds.py run /tmp/thresholds.json [--jobs 2] [--every N]     (every counted match, about 15 minutes)
        python3 tools/golden/thresholds.py show /tmp/thresholds.json
        python3 tools/golden/thresholds.py sweep NAME value [value ...] [--every 4] [--data <main>/data/lineup]
            what a looser or tighter threshold would do: the records it adds or removes, and the line-up statements
            it gains or loses on the building games (common.py GVG_TRY; nothing is changed in the engine)
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
            "lead": [[r["level"], r["t1"] - r["t"], r["lead"], bool(r["holds"])] for r in M.flag_lead()],
            "lead_s": (lambda lv: [sum(1 for tm in lv for v in lv[tm].values() if v == k) * 2 for k in (0, 1, 2, 3, 4)])(M._lead_levels()),
            "standoffs": [[r["t1"] - r["t"], min(r["n"]), max(r["n"]), bool(r["fought"]), r["end"], r["rate"], r["apart"], bool(r["away"][1] or r["away"][2]), r["kind"]] for r in M.standoffs()],
            "onto_flag": sum(1 for x in at if x.get("onto_flag")),
            "timing": [[r["kind"], r["s"], r.get("boost_in")] for r in M.timing()],
            "holds": [[fr["held_s"], fr["cap_boost_in"]] for fr in M.flags_record() if fr["how"] == "captured"],
            "monks": [[r["n"], r["was"], r["of"]] for r in M.monk_counts()],
            "lord": [[round(r["t1"] - r["t"]), len(r["ids"]), r["hits"], r["defenders"]] for r in M.on_lord()],
            "pregame": [bool(v["holder"] is not None) for v in M.pregame().values()],
            "story_lines": len(story.story(M, 0, None)),
            "way_out": [[g["door"], g["n"]] for g in M.way_out()],
            "answers": [("defended" if x["answer"]["defenders"] else "sent back" if x["answer"]["went_back"] else "none") for x in at if x["kind"] == "split" and x.get("solo") != "other"],
            "answer_swaps": sum(len(x["answer"].get("swaps", ())) for x in at),
            "caught": len(M.caught()),
        }
    except Exception as e:
        return rid, {"error": f"{type(e).__name__}: {e}"}


def run(path, jobs, every=1):
    import multiprocessing
    sys.path.insert(0, ENGINE); os.chdir(ENGINE)
    import common
    out = {}
    with multiprocessing.Pool(jobs) as pool:
        for rid, rec in pool.imap_unordered(one, sorted(common.replay_ids())[::every], chunksize=4):
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
    for lv in ("half a flag", "a flag", "a flag and a half", "two flags"):
        xs = [x for x in X if x[0] == lv]
        print(f"flag lead, {lv} up: {len(xs)} stretches ({len(xs) / n:.1f} a match); length (s): {q([x[1] for x in xs])}; by the team holding the stand {sum(x[3] for x in xs)}")
    ls = [sum(v["lead_s"][i] for v in D.values()) for i in range(5)]; tot = max(sum(D[k]["T"] for k in D), 1)
    print(f"  of the match time, a team is two flags up {100 * ls[4] // tot}%, a flag and a half {100 * ls[3] // tot}%, a flag {100 * ls[2] // tot}%, about half a flag {100 * ls[1] // tot}%; nobody leads by half a flag {100 * (2 * tot - sum(ls[1:])) // (2 * tot) * 2 - 100}%")
    Y = [x for x in cat("standoffs") if x[8] == "split"]
    print(f"stand-offs on a split (R-415): {len(Y)} ({len(Y) / n:.2f} a match; matches with none {sum(not any(x[8] == 'split' for x in v['standoffs']) for v in D.values())}); length (s): {q([x[0] for x in Y])}; smaller group: {q([x[1] for x in Y], (25, 50, 75))}; furthest apart: {q([x[6] for x in Y], (25, 50, 75))}; after a fight {sum(x[3] for x in Y)}; ended {dict(C(x[4] for x in Y))}")
    X = [x for x in cat("standoffs") if x[8] == "main"]
    print(f"stand-offs (R-405, R-411): {len(X)} ({len(X) / n:.2f} a match; matches with none {sum(not v['standoffs'] for v in D.values())}); length (s): {q([x[0] for x in X])}; hits a player in 10 s: {q([x[5] for x in X])}; furthest apart: {q([x[6] for x in X], (25, 50, 75))}")
    print(f"  smaller main team: {q([x[1] for x in X], (25, 50, 75))}; after a fight {sum(x[3] for x in X)}, without one {sum(not x[3] for x in X)}; a player away from a main team {sum(x[7] for x in X)}; ended {dict(C(x[4] for x in X))}")
    print(f"main team pushes walked onto a flag held in its team (R-401): {sum(v['onto_flag'] for v in D.values())}")
    X = cat("timing")
    for k in ("delayed pickup", "held to the boost", "stayed to help", "left before res", "held back", "left at the spawn"):
        xs = [x[1] for x in X if x[0] == k]
        print(f"timing, {k}: {len(xs)} ({len(xs) / n:.2f} a match); seconds: {q(xs)}")
    H = cat("holds"); hb = [x for x in H if x[1] is not None]
    print(f"  captures {len(H)}; in hand at the stand before the cap (s): {q([x[0] for x in H])}; held HOLD_S or longer {sum(x[0] >= 15 for x in H)}; of {len(hb)} capped against the enemy's stand, seconds to the enemy's boost: {q([x[1] for x in hb])}")
    X = cat("monks")
    print(f"monk count changes in the main fight: {len(X)} ({len(X) / n:.1f} a match); down {sum(x[1] is None or x[0] < x[1] for x in X)}, back up {sum(x[1] is not None and x[0] > x[1] for x in X)}; down to one {sum(x[0] == 1 and (x[1] is None or x[1] > 1) for x in X)}, to none {sum(x[0] == 0 for x in X)}")
    X = cat("lord"); told = [x for x in X if x[2] >= 3 and x[0] >= 4]
    print(f"on the Guild Lord: {len(X)} stretches, {len(told)} told ({len(told) / n:.1f} a match); length (s): {q([x[0] for x in told])}; players: {q([x[1] for x in told], (25, 50, 75))}; nobody of the defenders in the pit {sum(x[3] == 0 for x in told)}")
    wo = [x for v in D.values() for x in v.get("way_out", ())]; an = collections.Counter(x for v in D.values() for x in v.get("answers", ()))
    print(f"going out of the base by a door: {len(wo)} ({len(wo) / n:.1f} a match), by the back door {sum(1 for x in wo if x[0] == 'back door')}; split answers: {dict(an)}; swaps in an answer {sum(v.get('answer_swaps', 0) for v in D.values())}; caught at a base res {sum(v.get('caught', 0) for v in D.values())}")
    pg = cat("pregame")
    print(f"pre-game flag: in hand at the gates for {sum(pg)} of {len(pg)} teams")


def tally(path):
    """The count of every kind of record in a run, for comparing runs."""
    D = {k: v for k, v in json.load(open(path)).items() if "error" not in v}
    cat = lambda k: [x for v in D.values() for x in v[k]]
    t = {"joins": len(cat("joins")), "leaves": len(cat("leaves")), "split fights": len(cat("split_fights")), "swaps": len(cat("swaps")),
         "ground moves": len(cat("ground")), "ground moves told": sum(1 for x in cat("ground") if x[5]), "undefended": len(cat("undefended")), "on pit NPCs": len(cat("on_pit")),
         "split attempts": sum(v["attempts"][0] for v in D.values()), "main team pushes": sum(v["attempts"][1] for v in D.values()),
         "flagger pushes": len(cat("pushes")), "pushes onto a held flag": sum(v["onto_flag"] for v in D.values()), "routes read": sum(1 for x in cat("routes") if x[0]),
         "lead, half a flag": sum(1 for x in cat("lead") if x[0] == "half a flag"), "lead, a flag": sum(1 for x in cat("lead") if x[0] == "a flag"),
         "lead, a flag and a half": sum(1 for x in cat("lead") if x[0] == "a flag and a half"), "lead, two flags": sum(1 for x in cat("lead") if x[0] == "two flags"),
         "stand-offs": sum(1 for x in cat("standoffs") if x[8] == "main"), "stand-offs on a split": sum(1 for x in cat("standoffs") if x[8] == "split"),
         "monk changes": len(cat("monks")), "on the Lord": len(cat("lord")), "story lines": sum(v["story_lines"] for v in D.values())}
    t.update({"going out by a door": sum(len(v.get("way_out", ())) for v in D.values()), "swaps in an answer": sum(v.get("answer_swaps", 0) for v in D.values()), "caught at a base res": sum(v.get("caught", 0) for v in D.values())})
    for k in ("defended", "sent back", "none"): t["split answer, " + k] = sum(1 for v in D.values() for x in v.get("answers", ()) if x == k)
    for k in ("delayed pickup", "held to the boost", "stayed to help", "left before res", "held back", "left at the spawn"): t["timing, " + k] = sum(1 for x in cat("timing") if x[0] == k)
    return len(D), t


def sweep(name, values, every, data, jobs):
    """What a looser or tighter threshold would do (Denning: which thresholds cause problems). For each value of one
    threshold of the reading, rerun the records over every `every`-th counted match with that value in place of the
    one in common.py (GVG_TRY), and, with --data, rescore the building games of the line-up: the records it adds or
    removes are shown beside the statements it gains or loses. A value that gains statements for few extra records
    is a threshold to loosen; one that adds many records and gains none is not the cause of the misses."""
    import subprocess, re
    me, rows = os.path.abspath(__file__), []
    for v in [None] + values:
        tag = "now" if v is None else v
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", **({} if v is None else {"GVG_TRY": f"{name}={v}"}))
        p = f"/tmp/sweep_{name}_{tag}.json"
        subprocess.run([sys.executable, me, "run", p, "--jobs", str(jobs), "--every", str(every)], env=env, check=True, stdout=subprocess.DEVNULL)
        seen, kinds = None, {}
        if data:
            env["LINEUP_CACHE"] = f"/tmp/sweep_{name}_{tag}_lineup"
            subprocess.run(["rm", "-rf", env["LINEUP_CACHE"]])
            txt = subprocess.run([sys.executable, os.path.join(HERE, "lineup.py"), "score", "--data", data], env=env, capture_output=True, text=True).stdout
            mm = re.search(r"something seen happening: checked (\d+), agrees (\d+)", txt); seen = (int(mm.group(2)), int(mm.group(1))) if mm else None
            for ln in txt.splitlines():
                c = ln.split()
                if len(c) == 7 and c[0].isalpha() and all(x.isdigit() for x in c[1:]): kinds[c[0]] = (int(c[1]), int(c[2]))
        rows.append((tag, tally(p), seen, kinds))
    n0, base = rows[0][1]; k0 = rows[0][3]
    print(f"{name}: every {every}{'th' if every > 1 else ''} counted match ({n0} matches)" + (f"; the line-up's building games: seen events {rows[0][2][0]} of {rows[0][2][1]}" if rows[0][2] else ""))
    for tag, (_, t), seen, kinds in rows[1:]:
        ch = [f"{k} {base[k]} -> {t[k]}" for k in base if t[k] != base[k]]
        lk = [f"{k} {k0[k][0]} -> {kinds[k][0]} of {sum(kinds[k])}" for k in kinds if k in k0 and kinds[k] != k0[k]]
        print(f"  {name} = {tag}: " + ("; ".join(ch) if ch else "no record changes"))
        if seen: print(f"      line-up: seen events {seen[0]} of {seen[1]}" + (" (" + "; ".join(lk) + ")" if lk else " (no kind changes)"))


if __name__ == "__main__":
    a = sys.argv[1:]
    opt = lambda k, dflt: a[a.index(k) + 1] if k in a else dflt
    if len(a) >= 3 and a[0] == "sweep":
        vals = [x for i, x in enumerate(a) if i >= 2 and not x.startswith("--") and a[i - 1] not in ("--every", "--data", "--jobs")]
        sweep(a[1], vals, int(opt("--every", 4)), opt("--data", None), int(opt("--jobs", 2)))
    elif len(a) >= 2 and a[0] == "run": run(a[1], int(opt("--jobs", 2)), int(opt("--every", 1)))
    elif len(a) >= 2 and a[0] == "show": show(a[1])
    else: print(__doc__)
