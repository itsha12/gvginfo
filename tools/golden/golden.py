"""Golden moments (R-303): moments Denning labels by hand, which the engine's reading must match before a rebuild is
accepted and after every later engine change. docs/REDESIGN.md "Tests".

  pick <moments.json> [--n 30]   choose the moments from a run of `moments.py all` (one for every scenario of
                                 families 1 to 3, then the hard cases: a forced read, a double run, a hall with
                                 teleporters, a call no named option covers) and write data/model/golden_moments.json.
                                 Moments Denning already labelled are kept as they are; the file never carries the
                                 engine's own reading, so the page cannot show it.
  score                          run the engine on each labelled moment and compare: detection (is it a moment of that
                                 family), what the leave became, each part of the scenario, the call, forced. The
                                 sealed "should have done" field is never read here.

Kept outside tools/replay_analysis on purpose (every .py there is part of the engine's cache key)."""
import collections, datetime, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools", "replay_analysis"))
PATH = os.path.join(REPO, "data", "model", "golden_moments.json")
COMMS_S = 30         # a decision within this many seconds of a call on comms is the decision it speaks of (the read window, R-294)
NEAR_S = 20          # an engine moment within this many seconds of a golden one (same family, same team) is the same moment

REST = ["stay at the stand", "fall to footmen", "retreat to the pit", "fall back into the base", "push their flagger",
        "push the flag through as a team"]
FAMILIES = {
    "1": {"name": "Flag decision",
          "question": "The enemy sends a runner, a boost is coming, or the team has its own flag in hand: who runs, and where does everyone else go?",
          "became": True,
          "scenario": [{"id": "trigger", "q": "What set it off?", "options": [
                            ["enemy_run", "an enemy player leaves to run a flag"], ["boost", "the enemy's boost is 30 s away"],
                            ["own_flag", "an own player picks up a fresh flag"]]},
                       {"id": "stand", "q": "Who holds the stand?", "options": [["own", "the deciding team"], ["enemy", "the enemy"], ["nobody", "nobody"]]}],
          "call": [{"id": "runners", "q": "Runners (players on flag duty 20 to 30 s later)", "options": [["0", "none"], ["1", "one"], ["2", "two (a double run)"]]},
                   {"id": "rest", "q": "Where the rest go", "options": [[x, x] for x in REST], "other": True}]},
    "2": {"name": "Answer to a split",
          "question": "An enemy group leaves its main and turns out to be a split: how is it answered?",
          "became": True,
          "scenario": [{"id": "size", "q": "How many players split?", "options": [["1", "one"], ["2", "two"], ["3", "three"], ["4", "four or more"]]},
                       {"id": "home", "q": "Who is home when they leave?", "options": [["empty", "nobody"], ["home", "a defender or two"], ["main", "the main group"]]}],
          "call": [{"id": "call", "q": "The answer (who is home or on the way 30 s later)", "options": [[x, x] for x in
                    ("no answer", "one defender", "mirror", "two monks", "add one", "full collapse")], "other": True}]},
    "3": {"name": "Numbers advantage",
          "question": "Numbers differ where the main groups meet: what does the deciding team do with it (up), or about it (down)?",
          "became": False,
          "scenario": [{"id": "side", "q": "Is the deciding team up or down?", "options": [["up", "up"], ["down", "down"]]},
                       {"id": "source", "q": "Why is the short side short?", "options": [["kills", "kills"], ["runner away", "a runner is away"],
                                                                                        ["split elsewhere", "players are split elsewhere"], ["wipe", "a wipe"]]}],
          "call": [{"id": "call", "q": "The call", "options": [[x, x] for x in
                    ("stay and kill", "push their flagger", "run again for a backup", "push the pit for NPCs", "chase DP", "take the flag and reset",
                     "fight on", "fall to footmen", "retreat to the pit", "fall back into the base", "trade with a split")], "other": True,
                    "by": {"id": "side", "up": ["stay and kill", "push their flagger", "run again for a backup", "push the pit for NPCs", "chase DP", "take the flag and reset"],
                           "down": ["fight on", "fall to footmen", "retreat to the pit", "fall back into the base", "trade with a split"]}}]},
}
BECAME = [["run", "a flag run"], ["split", "a split"], ["collapse", "a collapse (home to defend)"], ["retreat", "a retreat (home, nobody to defend against)"],
          ["return", "back to the main group"], ["other", "something else"], ["none", "nobody left"]]


def clock(t): return f"{int(t) // 60}:{int(t) % 60:02d}"


def _context(x):
    """What the page shows for a moment: who, when, the trigger in words, roles and routes to tick. No engine reading."""
    from replaylib import Match
    from state import GameState
    st = GameState(Match.from_branch(x["rid"])); m = st.m
    tm, foe, t = x["tm"], 3 - x["tm"], x["t"]
    own, enemy = m.tag[tm], m.tag[foe]
    origin = {"main": "the main group", "res shrine": "the res shrine", "base": "the base"}
    said = []
    if x["family"] == 1:
        import moments as MO
        M = MO.Moments(st)
        trig = next(g for g in M.triggers() if g["family"] == 1 and g["tm"] == tm and g["t"] == t)
        for kind, ref in zip(trig["triggers"], trig["refs"]):
            if kind == "enemy_run": said.append(f"{enemy}'s {m.roles[ref['a']]} leaves {origin[ref['origin']]} at {clock(ref['t'])}")
            elif kind == "boost": said.append(f"{enemy}'s boost is 30 s away (it lands at {clock(t + 30)})")
            else: said.append(f"{own}'s {m.roles[ref]} picks up a fresh flag at the spawn")
    elif x["family"] == 2:
        said.append(f"{enemy}'s {', '.join(x['who'])} leave{'s' if len(x['who']) == 1 else ''} {origin.get(x['origin'], 'the main group')}")
    else:
        n = x["state"]["main"]
        said.append(f"numbers differ where the main groups meet: {own} {n[0]} v {n[1]} {enemy}")
    routes = sorted({r["type"] for r in st.hall.routes})
    for fr in st.hall.features.get("flag_routes", []): routes.append("Flag run " + fr["name"])
    if st.hall.hops: routes.append("Through a teleporter")
    by = lambda k: [m.roles[a] for a in sorted(st.players[k], key=lambda a: m.A[a].get("slot") or 0)]
    return {"id": x["id"], "match": x["rid"], "map": m.o["meta"]["map"], "team": own, "opponent": enemy, "t": t, "family": x["family"],
            "trigger": "; ".join(said), "watch": [max(t - 15, 0), min(t + 60, st.end)], "roles": by(tm), "enemy_roles": by(foe),
            "routes": routes, "label": None, "sealed": None}


def pick(src, n=30, seed=11):
    D = json.load(open(src)); R = D["records"]; rnd = random.Random(seed)
    old = {}
    if os.path.exists(PATH):
        old = {g["id"]: g for g in json.load(open(PATH)).get("moments", []) if g.get("label") or g.get("sealed")}
    used, picks, halls, calls = set(g["match"] for g in old.values()), [], collections.Counter(), collections.Counter()

    def take(cands, why):
        cands = [x for x in cands if x["rid"] not in used and x["t"] >= 30]
        if not cands: return
        rnd.shuffle(cands)
        # spread over halls and over calls: the least used hall, then the least used call
        x = min(cands, key=lambda x: (halls[D["matches"][x["rid"]]["map"]], calls[(x["family"], x["call"]["key"])]))
        used.add(x["rid"]); halls[D["matches"][x["rid"]]["map"]] += 1; calls[(x["family"], x["call"]["key"])] += 1
        picks.append((x, why))

    for fam in (1, 2, 3):
        F = [x for x in R if x["family"] == fam and not x["forced"]]
        for key, _ in collections.Counter(x["scenario"]["key"] for x in F).most_common():
            take([x for x in F if x["scenario"]["key"] == key], "scenario")
    take([x for x in R if x["family"] == 1 and x["call"].get("runners") == 2 and not x["forced"]], "double run")
    take([x for x in R if x["family"] == 2 and x["forced"]], "forced read")
    take([x for x in R if x["family"] == 3 and x["forced"] and x["triggers"] == ["down"]], "forced read")
    take([x for x in R if x["family"] == 1 and x["call"]["key"].endswith("other: on the backside")], "no named call")
    take([x for x in R if x["family"] == 2 and D["matches"][x["rid"]]["map"] in ("Isle of Jade", "Nomad's Isle", "Isle of Solitude") and not x["forced"]], "teleporter hall")
    picks = picks[:n]
    moments = list(old.values())
    for x, why in picks:
        g = _context(x); g["picked_for"] = why
        moments.append(g)
    moments.sort(key=lambda g: (g["family"], g["id"]))
    out = {"about": "Golden moments (R-303): Denning labels each by hand on Model > Golden moments; the engine's reading of the same "
                    "moment must match before a rebuild is accepted (tools/golden/golden.py score). The engine's own reading is "
                    "never stored here. `sealed` holds his optional view of what the team should have done, encoded so it is not "
                    "read by accident: never decode or print it in a chat.",
           "version": 1, "generated": datetime.date.today().isoformat(), "read_window": [20, 30],
           "families": FAMILIES, "became": BECAME, "moments": moments}
    json.dump(out, open(PATH, "w"), indent=1)
    print(len(moments), "moments;", collections.Counter(g["family"] for g in moments), "; halls", collections.Counter(g["map"] for g in moments))


def score():
    import moments as MO
    G = json.load(open(PATH)); rows = []
    tally = collections.defaultdict(lambda: [0, 0])
    def mark(k, ok): tally[k][0] += bool(ok); tally[k][1] += 1
    for g in G["moments"]:
        L = g.get("label")
        if not L: continue
        recs = MO.match_records(g["match"]) or []
        near = [x for x in recs if x["family"] == g["family"] and x["team"] == g["team"] and abs(x["t"] - g["t"]) <= NEAR_S]
        x = min(near, key=lambda x: abs(x["t"] - g["t"])) if near else None
        real = L.get("real") == "yes"
        mark("moment found", bool(x) == real)
        miss = []
        if real and x:
            if L.get("became") and x["family"] != 3:
                eng = "run" if x["family"] == 1 and "enemy_run" in x["triggers"] else ("split" if x["family"] == 2 else None)
                if eng: mark("what the leave became", L["became"] == eng); miss += [] if L["became"] == eng else [f"became: his {L['became']}, engine {eng}"]
            parts = {k: str(v) for k, v in x["scenario"]["parts"].items()}
            if x["family"] == 2: parts["size"] = str(min(int(parts["size"]), 4)); parts["home"] = x["scenario"]["key"].split("|")[1]
            for k, v in (L.get("scenario") or {}).items():
                ok = parts.get(k) == str(v); mark("scenario: " + k, ok)
                if not ok: miss.append(f"{k}: his {v}, engine {parts.get(k)}")
            c, e = L.get("call") or {}, x["call"]
            eng_call = {"runners": str(e.get("runners")), "rest": e.get("rest"), "call": e["key"]}
            for k, v in c.items():
                if k.endswith("_text"): continue
                ev = eng_call.get(k); ok = (str(v) == str(ev)) or (v == "other" and str(ev).startswith("other"))
                mark("call: " + k, ok)
                if not ok: miss.append(f"{k}: his {v}{' (' + c[k + '_text'] + ')' if c.get(k + '_text') else ''}, engine {ev}")
            if "forced" in L:
                ok = bool(L["forced"]) == x["forced"]; mark("forced", ok)
                if not ok: miss.append(f"forced: his {L['forced']}, engine {x['forced']}")
        elif real and not x: miss.append("the engine has no moment of this family here")
        elif not real and x: miss.append(f"he says {L.get('real')}; the engine reads {x['scenario']['label']}")
        rows.append((g["id"], g["family"], clock(g["t"]), g["team"], miss))
    print(f"{len(rows)} labelled of {len(G['moments'])}")
    for k, (a, b) in tally.items(): print(f"  {k:28} {a}/{b}")
    for r in rows:
        if r[4]: print(f"  {r[0]} F{r[1]} {r[2]} {r[3]}: " + "; ".join(r[4]))


def gate(recs_cache={}):
    """The decision gate, part one (R-394): each golden moment's scenario and call, read from Denning's notes
    (data/model/golden_key.json, Claude's reading of them, R-341), against the engine's record of the same family and
    team nearest the key's time (within NEAR_S). Rates of R-327: the moment found in 9 of 10, each part in 8 of 10."""
    import moments as MO
    K = json.load(open(os.path.join(REPO, "data", "model", "golden_key.json")))
    G = {g["id"]: g for g in json.load(open(PATH))["moments"]}
    tally = collections.defaultdict(lambda: [0, 0]); rows = []
    for gid, k in K["moments"].items():
        g = G[gid]
        if g["match"] not in recs_cache: recs_cache[g["match"]] = MO.match_records(g["match"]) or []
        recs = recs_cache[g["match"]]
        near = [x for x in recs if x["family"] == k["family"] and x["team"] == k["team"] and abs(x["t"] - k["t"]) <= NEAR_S]
        x = min(near, key=lambda x: abs(x["t"] - k["t"])) if near else None
        tally["moment found"][0] += bool(x); tally["moment found"][1] += 1
        miss = []
        if k.get("not_at") is not None:
            bad = [y for y in recs if y["family"] == k["family"] and y["team"] == k["team"] and abs(y["t"] - k["not_at"]) <= 5]
            tally["no moment where he says none"][0] += not bad; tally["no moment where he says none"][1] += 1
            if bad: miss.append(f"a moment at {clock(bad[0]['t'])}, where his notes put none")
        if x is None:
            miss.append("no engine moment of this family within %d s" % NEAR_S)
        else:
            sc, c = x["scenario"]["parts"], x["call"]
            eng = {"trigger": sc.get("trigger"), "stand": sc.get("stand"), "runners": str(c.get("runners")), "rest": c.get("rest"),
                   "size": str(min(int(sc["size"]), 4)) if "size" in sc else None, "home": ("home" if sc.get("home") else "empty") if "home" in sc else None,
                   "side": sc.get("side"), "source": sc.get("source"), "call": c.get("key")}
            for part, ok_words in k["parts"].items():
                ok = eng.get(part) in ok_words
                tally[part][0] += ok; tally[part][1] += 1
                if not ok: miss.append(f"{part}: his notes {' / '.join(ok_words)}, engine {eng.get(part)}")
            if "forced" in k:
                ok = bool(k["forced"]) == bool(x["forced"]); tally["forced"][0] += ok; tally["forced"][1] += 1
                if not ok: miss.append(f"forced: his notes {k['forced']}, engine {x['forced']}")
        rows.append((gid, k["family"], clock(k["t"]), k["team"], x and clock(x["t"]), x and x["scenario"]["label"], x and x["call"]["label"], miss))
    print(f"Decision gate, part one: {len(rows)} golden moments read from his notes ({', '.join(K.get('not_scored', {}))} not scored)")
    for part, (a, b) in tally.items():
        need = 0.9 if part == "moment found" else 0.8
        print(f"  {part:30} {a}/{b}  {'pass' if b and a / b >= need else 'FAIL'} (needs {int(need * 100)}%)")
    for r in rows:
        print(f"  {r[0]} F{r[1]} {r[2]} {r[3]}: engine {r[4]}: {r[5]} | {r[6]}" + ("" if not r[7] else "\n      MISS " + "; ".join(r[7])))
    return tally, rows


COMMS_CALL = {           # a team's own call on comms (R-394 part two) and the engine calls that read the same
    "fall": ("fall back into the base", "retreat to the pit", "fall to footmen", "fall back", "fall out", "retreat down the ladder"),
    "push": ("push in", "push up", "push up to their front door", "push up to their back door", "push up to their base"),
    "pushflag": ("push their flagger",),
    "split": ("split",),
    "join": ("answer",), "answer": ("answer",),
    "go": ("run",), "wait": ("run",), "cap": ("run",)}


def comms(data=None, recs_cache={}):
    """The decision gate, part two (R-394): where a team says on comms what it means to do (the line-up's "i." calls),
    does the engine find a decision of that team there (a moment within COMMS_S of the call) and read the same call?
    Calls the engine has no decision for (NPCs, a plan, a boost, a swap, a drop) are counted apart. The pass rate is set
    by Denning when this is first measured."""
    import moments as MO
    sys.path.insert(0, HERE); import lineup as LU, common
    data = data or os.path.join(REPO, "data", "lineup")
    tally, out, other = collections.Counter(), [], collections.Counter()
    for f in LU.files(data):
        head, rows = LU.load(f)
        rid = os.path.basename(f).split(".")[0]
        rid = next((r for r in common.replay_ids() if r.startswith(rid[:8])), rid)
        calls = [r for r in rows if r["kind"].startswith("i.")]
        if not calls: continue
        if rid not in recs_cache: recs_cache[rid] = MO.match_records(rid) or []
        recs = recs_cache[rid]
        for r in calls:
            k = r["kind"][2:]
            if k not in COMMS_CALL: other[k] += 1; continue
            mine = [x for x in recs if x["team"] == r["team"] and -COMMS_S <= x["t"] - r["t"] <= COMMS_S]
            def reads(x):
                c, v = x["call"], {k_ for k_, _ in x.get("verbs", [])}
                who = lambda verb: {w for k_, w in x.get("verbs", []) if k_ == verb}
                named = lambda verb: verb in v and (not r["who"] or any(w in who(verb) for w in r["who"]) or verb in ("fall back", "fall out", "push up", "push in"))
                if k in ("go", "wait", "cap"): return named("run")
                if k in ("join", "answer"): return named("join") or named("answer")
                if k == "split": return named("split") or (c.get("rest") or "").startswith("split")
                if k == "pushflag": return named("push their flagger") or c.get("rest") == "push their flagger"
                if k == "fall": return bool(v & {"fall back", "fall out"}) or c.get("rest") in COMMS_CALL[k] or c.get("key") in COMMS_CALL[k]
                if k == "push": return bool(v & {"push in", "push up"}) or c.get("rest") in COMMS_CALL[k] or c.get("key") in COMMS_CALL[k]
                return False
            tally["called"] += 1
            if mine: tally["a decision found there"] += 1
            ok = any(reads(x) for x in mine)
            tally["the same call read"] += ok
            if not ok: out.append((os.path.basename(f)[:8], LU.clock(r["t"]), r["team"], r["kind"], r["say"][:90], [(LU.clock(x["t"]), x["family"], x["call"]["label"]) for x in mine][:3]))
    n = tally["called"] or 1
    print(f"Decision gate, part two: {tally['called']} calls a team made on comms about what it means to do")
    print(f"  a decision of that team found within {COMMS_S} s: {tally['a decision found there']} ({tally['a decision found there'] * 100 // n}%)")
    print(f"  the same call read: {tally['the same call read']} ({tally['the same call read'] * 100 // n}%)")
    print(f"  calls the engine has no decision for: {sum(other.values())} ({', '.join(f'{k} {v}' for k, v in other.most_common())})")
    for row in out: print("  MISS", *row)
    return tally, out


def stories():
    """The engine's story of each golden moment's game, up to a minute after the moment. Denning reads it on the page,
    ticks the lines that are wrong and adds his own notes or corrections (R-354). Kept in its own file so the labels
    file holds only what he wrote."""
    from replaylib import Match
    from state import GameState
    import moments as MO, story as ST
    G = json.load(open(PATH)); out = {}
    for g in G["moments"]:
        M = MO.Moments(GameState(Match.from_branch(g["match"])))
        out[g["id"]] = [[int(t), s] for t, s in ST.story(M, 0, g["t"] + 60)]
    json.dump({"about": "The engine's story of each golden moment's game (tools/golden/golden.py stories; story.py on the bundle-4 "
                        "branch). Shown on Model > Golden moments for Denning to mark (R-354).",
               "generated": datetime.date.today().isoformat(), "draft": 9, "stories": out},
              open(os.path.join(REPO, "data", "model", "golden_stories.json"), "w"), indent=0)
    print(len(out), "stories;", sum(len(v) for v in out.values()), "lines")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "pick": pick(a[1], int(a[a.index("--n") + 1]) if "--n" in a else 30)
    elif a and a[0] == "score": score()
    elif a and a[0] == "gate": gate(); print(); comms(a[a.index("--data") + 1] if "--data" in a else None)
    elif a and a[0] == "stories": stories()
    else: print(__doc__)
