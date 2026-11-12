"""Line up timestamped commentary and comms with the engine's record (R-362: the record is the work).

Each transcript is filed as paraphrased statements, never the transcript itself, in data/lineup/<report id>.<source>.txt:
header lines "# key: value" (match, source, teams in the story's order, clock, held_out), then one statement a line:

    m:ss | kind | team | who | arg | what was said, paraphrased

m:ss is the transcript's own clock; "clock" turns it into match time (a fixed offset in seconds, or anchors
"m:ss=m:ss, ..." read as transcript=match and joined by straight lines). A kind may carry a prefix: "i." an intent
called before the move, "s." a call about the enemy.

Checked kinds are looked for in the engine's story and fight numbers within a window of the statement; the rest are
things the story has no word for yet and are counted by kind, so the list of missing words comes from the data.

The four held-out games (R-370) are filed in data/lineup/held/ (R-397); --show prints their lines only with --gate.

Usage:  python3 tools/golden/lineup.py score [--data DIR] [--held] [--show [--gate]] [report id ...]
        python3 tools/golden/lineup.py lines <report id> <from m:ss> <to m:ss> [word]
A report tool: it is in no cache key and writes nothing but its own cache of stories (LINEUP_CACHE, default /tmp)."""
import collections, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "replay_analysis")
CACHE = os.environ.get("LINEUP_CACHE", "/tmp/lineup_cache")
BEFORE, AFTER = 40, 40            # a spoken line trails or leads the event: seconds searched either side
INTENT_AFTER = 75                 # an intent, or a call about the enemy, comes before the move
TO_BUILD = ()                     # the words Denning ruled the record needs (R-373, R-378) are built and checked: route, pushflag, lead, posture, timing, monks, lord
SEALED = ("judge", "cause")                                         # kept as tests of verdicts and of execution (R-372, R-373)
OUT = ("plan", "option", "reason", "micro", "build", "question", "energy")   # outside what the engine reads (R-373, R-353)
OPEN = ("pull", "support", "trade", "standoff", "unsure", "clock", "object")   # not ruled yet
LEVEL = {0: "level on flags or behind", 1: "about half a flag up", 2: "a flag up", 3: "a flag and a half up", 4: "two flags up"}      # the bands of the flag lead (R-408)
NO_WORD = TO_BUILD + SEALED + OUT + OPEN
NUM = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight"}


def secs(s):
    m, x = s.strip().split(":"); return int(m) * 60 + int(x)
def clock(t): return f"{int(t) // 60}:{int(t) % 60:02d}"


def record(rid):
    """The engine's story and fight numbers for one match, cached."""
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, rid[:8] + ".json")
    if os.path.exists(p): return json.load(open(p))
    sys.path.insert(0, ENGINE); cwd = os.getcwd(); os.chdir(ENGINE)
    from replaylib import Match
    from state import GameState
    import moments, story
    st = GameState(Match.from_branch(rid)); M = moments.Moments(st); m = st.m
    fights = [[t, [[f["n"][1], f["n"][2], f["place"], f["monks"][1], f["monks"][2]] for f in M.fights(t) if f["n"][1] and f["n"][2]]] for t in range(0, M.T + 1, 3)]
    lv, lead = M._lead_levels(), []                    # the records that run over a stretch are checked as stretches: a line said in the middle of one agrees with it
    for tm in (1, 2):
        for t in sorted(lv[tm]):
            if lead and lead[-1][2] == m.tag[tm] and lead[-1][3] == lv[tm][t] and t - lead[-1][1] <= 2: lead[-1][1] = t
            elif lv[tm][t]: lead.append([t, t, m.tag[tm], lv[tm][t]])
    spans = {"lead": lead,
             "pushflag": [[r["t"], r["t1"], r["team"], r["roles"], r["role"]] for r in M.flag_pushes()]        # and a main team push walked onto a flag held in its team (R-401)
                         + [[x["onto_flag"]["t"], x["onto_flag"]["t"] + x["onto_flag"]["s"], x["team"], [q["role"] for q in x["members"]], x["onto_flag"]["role"]] for x in M.attempts() if x.get("onto_flag")],
             "posture": [[r["t"], r["t1"], tg, r["place"]] for r in M.standoffs() for tg in r["teams"]],        # a posture said of a team is checked against the stand-off it stands in (R-405)
             "lord": [[r["t"], r["t1"], r["team"], r["roles"]] for r in M.on_lord() if r["hits"] >= 3]}
    out = {"id": rid, "map": m.o["meta"]["map"], "teams": [m.tag[1], m.tag[2]], "T": M.T,
           "roster": {m.tag[tm]: {str(m.A[a].get("slot")): m.roles[a] for a in m.PL if m.team(a) == tm} for tm in (1, 2)},
           "story": [[t, s] for t, s in story.story(M, 0, None)], "fights": fights, "spans": spans}
    os.chdir(cwd); json.dump(out, open(p, "w"), ensure_ascii=False)
    return out


def load(path):
    head, rows = {}, []
    for ln in open(path, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if ln.startswith("#"):
            if ":" in ln: k, v = ln[1:].split(":", 1); head[k.strip()] = v.strip()
            continue
        if not ln.strip(): continue
        c = [x.strip() for x in ln.split("|")]
        c += [""] * (6 - len(c))
        rows.append({"at": secs(c[0]), "kind": c[1], "team": c[2], "who": [w.strip() for w in c[3].split(",") if w.strip()], "arg": c[4], "say": c[5]})
    ck = head.get("clock", "0")
    anchors = sorted((secs(a.split("=")[0]), secs(a.split("=")[1])) for a in ck.split(",")) if "=" in ck else None
    def to_match(s):
        if not anchors: return s - int(ck)
        if s <= anchors[0][0]: return s - (anchors[0][0] - anchors[0][1])
        for (a0, m0), (a1, m1) in zip(anchors, anchors[1:]):
            if s <= a1: return m0 + (s - a0) * (m1 - m0) / max(a1 - a0, 1)
        return s - (anchors[-1][0] - anchors[-1][1])
    for r in rows: r["t"] = max(to_match(r["at"]), 0)      # said before the gates: read against the opening
    return head, rows


def _seg(line, tag):
    """A team's part of a STATE line."""
    m = re.search(rf"(?:^|\. ){re.escape(tag)}: (.*?)(?=\. [^ ]+: |$)", line)
    return m.group(1) if m else ""


def check(r, rec):
    """(verdict, the engine line that agrees or the nearest lines of the kind)."""
    kind = r["kind"].split(".")[-1]
    if r["kind"].startswith("ok."): return "agrees", "Denning confirmed the engine's reading of this moment"
    if kind in NO_WORD:
        return ("to build" if kind in TO_BUILD else "sealed" if kind in SEALED else "out of scope" if kind in OUT else "not ruled"), ""
    T = r["team"]; E = next((x for x in rec["teams"] if x != T), "")
    te, ee = re.escape(T), re.escape(E)
    who = r["who"]; arg = r["arg"]
    lo, hi = r["t"] - BEFORE, r["t"] + (INTENT_AFTER if r["kind"][:2] in ("i.", "s.") or kind == "join" else AFTER)      # a join is called as the player sets off and recorded when he arrives
    has = lambda s: all(re.search(rf"(?<![\w]){re.escape(w)}", s) for w in who)
    near = [(t, s) for t, s in rec["story"] if lo <= t <= hi]
    wide = [(t, s) for t, s in rec["story"] if lo - 60 <= t <= hi + 60]
    state = lambda pool: [(t, _seg(s, T)) for t, s in pool if s.startswith("STATE")]
    one = (who[0] if who else r"[^']*?")
    R = rf"{te}'s {re.escape(who[0]) + '(?: [A-Z0-9])?' if who else '[^.;]*?'}"
    def find(pat, pool=None, need_who=False):
        for t, s in (near if pool is None else pool):
            if s.startswith("STATE"): continue
            if re.search(pat, s) and (not need_who or has(s)): return t, s
    hit = None; fam = None
    def small_fight(names, team=T):                 # a split or its answer told as a small fight away from the main one: these players named in a fight of four a side or fewer
        for t_, s_ in near:
            mf = re.match(rf"A (?:split )?fight at [^:]*: \S+ (\d) v (\d) \S+ \((.*)\)$", s_)
            if not mf or max(int(mf.group(1)), int(mf.group(2))) > 4: continue
            seg = next((x for x in mf.group(3).split("; ") if x.startswith(team + ":")), "")
            if names and all(re.search(rf"(?<![\w]){re.escape(w)}(?![\w])", seg) for w in names): return t_, s_
    if kind == "go":
        fam = rf"{te}'s .*(go back for the flag|picks up the flag at the spawn|waits back|takes the next flag)"
        hit = find(rf"{R}\S* (leaves .*to go back for the flag|picks up the flag at the spawn|waits back at the flag spawn)") \
            or find(rf"^{te}'s .*; {re.escape(one)} (went back for it|was waiting back).*takes the next flag")
        if not hit:
            hit = next(((t, s) for t, s in state(near) if re.search(rf"{re.escape(one)} (going back for the flag|running the flag|waiting back)", s)), None)
    elif kind == "wait":
        fam = rf"{te}'s .*wait"
        hit = find(rf"{R}\S* waits back") or find(rf"^{te}'s .*; {re.escape(one)} was waiting back") \
            or next(((t, s) for t, s in state(near) if re.search(rf"{re.escape(one)} waiting back", s)), None)
    elif kind == "pickup": fam = rf"{te}'s .*picks"; hit = find(rf"{R}\S* picks (up the flag|the flag up)")
    elif kind == "cap": fam = rf"{te}'s .*caps"; hit = find(rf"{R}\S* (over)?caps")
    elif kind == "overcap": fam = rf"{te}'s .*caps"; hit = find(rf"{R}\S* overcaps")
    elif kind == "hand":
        fam = rf"{te}'s .*hands the flag"
        hit = find(rf"{R}\S* hands the flag to {re.escape(arg)}") or find(rf"{R}\S* drops the flag.*{re.escape(arg)} picks it up")
    elif kind == "drop": fam = rf"{te}'s .*drops the flag"; hit = find(rf"{R}\S* drops the flag")
    elif kind == "ret": fam = rf"{te}'s .*returns|flag is back"; hit = find(rf"{R}\S* returns {ee}'s flag") or find(rf"^{ee}'s flag is back at the spawn")      # a return the observer missed is read from the flag being back
    elif kind == "hold":
        fam = rf"{te}.*holding the flag"
        hit = next(((t, s) for t, s in state(near) if re.search(rf"{re.escape(one)} holding the flag", s) or (not who and "holding the flag" in s)), None)
        if not hit: hit = find(rf"{R}\S* (picks up the flag|picks the flag up)") or find(rf"{te}'s .* hands the flag to {re.escape(one)}") or find(rf"^At the gates {R}\S* has the flag")
    elif kind == "form":
        fam = rf"^{te}'s .*double run"; hit = find(rf"^{te}'s .*double run, each {arg} running")
    elif kind == "split":
        fam = rf"^{te} splits"
        n = NUM.get(int(arg)) if arg.isdigit() else None
        hit = find(rf"^{te} splits {n or ''}", need_who=True)
        if not hit: hit = next(((t, s) for t, s in state(near) if re.search(r"splitting", s) and all(re.search(rf"{re.escape(w)}[^;]*splitting", s) for w in who)), None)
        if not hit: hit = small_fight(who)
    elif kind == "answer":
        fam = rf"^{te} (answers|does not answer|sends)"
        hit = find(rf"^{te} answers {ee}'s split with", need_who=True) or find(rf"^{te} sends .* back for {ee}'s split", need_who=True)
        if not hit: hit = next(((t, s) for t, s in state(near) if all(re.search(rf"{re.escape(w)}[^;]*(defending|against)", s) for w in who) and "defending" in s), None)
        if not hit and who:                         # the same thing told another way: the defender in a fight, or joining one, on his own ground
            w = re.escape(one)
            hit = find(rf"^{te}'s [^:]*{w}[^:]* (?:joins?|(?:now )?defends?) [^:]*at {te}'s") or find(rf"^A fight at {te}'s [^:]*: .*{te}: [^;)]*{w}") or small_fight(who[:1])
    elif kind == "noanswer":
        fam = rf"^{te} (answers|does not answer|leaves)"; hit = find(rf"^{te} does not answer {ee}'s split") or find(rf"^{te} leaves {ee}'s split undefended")
        if not hit:                                 # or the state of play says it: a player of theirs splitting with nobody against him
            for t_, s_ in near:
                if s_.startswith("STATE") and any("against" not in c for c in re.findall(r"splitting at [^;.]*", _seg(s_, E))): hit = (t_, s_); break
    elif kind == "fight":
        fam = None
        m = re.match(r"(\d)\s*v\s*(\d)(?:\s*@\s*(.*))?", arg); a, b, pl = int(m.group(1)), int(m.group(2)), (m.group(3) or "").lower()
        seen = collections.Counter()
        for t, fs in rec["fights"]:
            if lo <= t <= hi:
                for x, y, p, *_ in fs:                      # numbers said of a place are who stands there, damage or not (the story words a stand-off apart, R-405)
                    seen[(x, y, p)] += 1
                    if (x, y) == (a, b) and pl in p.lower(): hit = (t, f"{rec['teams'][0]} {x} v {y} {rec['teams'][1]} at {p}")
        if not hit:
            top = [f"{x}v{y} {p}" for (x, y, p), c in seen.most_common(4)]
            return "differs", "engine's numbers in the window: " + "; ".join(top)
    elif kind in ("pushflag", "posture", "lord"):      # records that run over a stretch: the team's stretch of that kind overlaps the window (who = the players pushing, or on the Lord)
        named = lambda roles: all(any(x == w or x.startswith(w + " ") for x in roles) for w in who)
        sp = [x for x in rec["spans"][kind] if x[2] == T and x[0] <= hi and x[1] >= lo]
        ok = [x for x in sp if kind == "posture" or named(x[3])]
        other = lambda tg: next((y for y in rec["teams"] if y != tg), "")
        word = {"pushflag": lambda x: f"{x[2]}'s {', '.join(x[3])} on {other(x[2])}'s flagger ({x[4]})", "posture": lambda x: f"{x[2]} stands off ({x[3]})", "lord": lambda x: f"{x[2]}'s {', '.join(x[3])} on {other(x[2])}'s Guild Lord"}[kind]
        if ok: return "agrees", f"{clock(ok[0][0])} to {clock(ok[0][1])} {word(ok[0])}"
        wide_sp = [x for x in rec["spans"][kind] if x[0] <= hi + 60 and x[1] >= lo - 60]
        return "differs", " // ".join(f"{clock(x[0])} to {clock(x[1])} " + word(x) for x in wide_sp[:3]) or f"no {kind} record within two minutes"
    elif kind == "lead":                                # R-408: the team named leads on the flag tally in the window
        need = {"full": 2, "half": 1, "up": 1}.get(arg) or (1 if "nearly a full" in r["say"] else 2 if re.search(r"\bfull flag", r["say"]) else 1)      # "a full flag" asks for a flag up or more; any other lead for half a flag or more
        best = max((x[3] for x in rec["spans"]["lead"] if x[2] == T and x[0] <= hi and x[1] >= lo), default=0)
        return ("agrees" if best >= need else "differs"), f"in the window {T} is at most {LEVEL[best]}" + ("" if best >= need else f"; the statement asks for {LEVEL[need]}")
    elif kind == "monks":                               # R-378: the team's biggest fight in the window has that many monks in it
        n = int(arg) if arg.isdigit() else (0 if re.search(r"\bno monks?\b", r["say"]) else 1 if re.search(r"\b(solo|one) monk", r["say"]) else 2 if re.search(r"\btwo monks", r["say"]) else 3 if "three monks" in r["say"] else None)
        if n is None: return "not ruled", ""
        i = rec["teams"].index(T); seen = collections.Counter()
        for t, fs in rec["fights"]:
            if lo <= t <= hi and fs:
                f = max(fs, key=lambda f: f[i])
                if f[i] >= 2: seen[f[3 + i]] += 1
                if f[i] >= 2 and f[3 + i] == n: hit = (t, f"{T} has {n} monk{'' if n == 1 else 's'} in its biggest fight ({rec['teams'][0]} {f[0]} v {f[1]} {rec['teams'][1]} at {f[2]})")
        if not hit: return "differs", f"monks in {T}'s biggest fight in the window: " + ", ".join(f"{k} ({v * 3} s)" for k, v in seen.most_common())
    elif kind == "route":
        a_ = re.escape(arg)
        fam = rf"{te}'s .*(runs it the|by the back door|go back for the flag the)|^{te} splits .* by the"
        hit = find(rf"{R}\S* (?:picks up the flag at the spawn|leaves .*to go back for the flag)[^;]* (?:the|by the) {a_}") or ((find(rf"^{te} splits [^(]*by the {a_}") or find(rf"^{te}'s [^:]*by the {a_}", need_who=True)) if "door" in arg else None)      # a door: the split or the player told going by it
    elif kind == "timing":                              # R-377: one of the four timing choices by that team; the statement's own words pick which
        pats = {"pick": rf"^{te}'s .* waits \d+ s at the flag spawn before picking up", "boost": rf"^{te} holds its flag at the stand", "help": rf"^{te}'s .* stays \d+ s to help the flag in", "res": rf"^{te}'s .* leaves {ee}'s base \d+ s before",
                "hold": rf"^{te}'s .* holds the flag back|^{te} leaves its flag at the spawn"}
        key = "pick" if "pick up" in r["say"] and "push" not in arg else "boost" if "boost" in r["say"] else "help" if "help the flag" in r["say"] else "res" if "base res" in r["say"] \
            else "hold" if re.search(r"not (try to )?run|keeps the flag|holds? (on to )?the flag", r["say"]) else None
        fam = "|".join(pats.values())
        hit = find(pats[key] if key else fam, [(t, s) for t, s in rec["story"] if lo - (60 if key == "hold" else 0) <= t <= hi])      # a flag held back is told when the hold began: a remark on it comes during it
    elif kind == "death": fam = rf"^{te} loses"; hit = find(rf"^{te} loses (?:(?! at ).)*{re.escape(one)}")
    elif kind == "baseres": fam = rf"^Base res: {te}"; hit = find(rf"^Base res: {te}'s [^.]*{re.escape(one)}")
    elif kind == "res": fam = rf"^{te}'s .*resurrected"; hit = find(rf"{R}\S* is resurrected")
    elif kind == "npc": fam = rf"^{te} takes"; hit = find(rf"^{te} takes {ee}'s {arg}")
    elif kind == "fall":            # the story often tells a retreat from the pusher's side: both tellings count
        fam = rf"^{te}(?:'s split)? (falls back|gives ground|has fallen back)|^The fight moves|^{ee} pushes"
        hit = find(rf"^{te}(?:'s split)? (falls back|gives ground|has fallen back)[^(]*{re.escape(arg)}")
        if not hit: hit = find(rf"^{ee} pushes {te} back[^(]*{re.escape(arg)}")
        if not hit and arg: hit = find(rf"^(?:{ee} pushes|The fight moves) [^(]*to {te}'s {re.escape(arg)}")
    elif kind == "push":
        fam = rf"^{te}(?:'s main team|'s split)? (pushes|has pushed)"; hit = find(rf"^{te}(?:'s main team|'s split)? (?:pushes|has pushed)[^(]*{re.escape(arg)}")
    elif kind == "join":
        fam = rf"{te}'s [^;)]*joins?"; hit = find(rf"{te}'s [^;)]*{re.escape(one)}[^;)]* joins?[^;)]*{re.escape(arg)}")
        if not hit and len(who) > 1:               # several players named: the line must name at least half of them
            for t_, s_ in near:
                mj = re.search(rf"{te}'s ([^;)]*?) joins?[^;)]*{re.escape(arg)}", s_)
                if mj and sum(1 for w in who if re.search(rf"(?<![\w]){re.escape(w)}", mj.group(1))) * 2 >= len(who): hit = (t_, s_); break
    elif kind == "leave": fam = rf"{te}'s [^;)]*leaves?"; hit = find(rf"{te}'s [^;)]*{re.escape(one)}[^;)]* leaves?")
    elif kind == "boost": fam = rf"^{te} boosts"; hit = find(rf"^{te} boosts")
    elif kind == "caught": fam = rf"^{te} is in"; hit = find(rf"^{te} is in {ee}'s base")
    elif kind == "swap": fam = rf"{te} swaps"; hit = find(rf"{te} swaps")
    elif kind == "end":
        fam = rf"^{te}'s (split|push) ends|^The split fight ends"; hit = find(rf"^{te}'s (split|push) ends[^;]*{re.escape(arg)}")
        if not hit and not arg: hit = find(r"^The split fight ends")      # a split kept as one split fight (R-365) ends with that record
    else: return "unknown kind", kind
    if hit: return "agrees", f"{clock(hit[0])} {hit[1][:150]}"
    alt = [f"{clock(t)} {s[:110]}" for t, s in wide if fam and not s.startswith("STATE") and re.search(fam, s)][:3]
    return "differs", " // ".join(alt) if alt else "nothing of this kind within two minutes"


def score(paths, show=False):
    tot = collections.defaultdict(collections.Counter); per = {}; said = collections.defaultdict(collections.Counter)
    for p in paths:
        head, rows = load(p); rec = record(head["match"])
        c = collections.Counter(); name = f"{'-v-'.join(rec['teams'])} ({head['source']})"
        for r in rows:
            v, why = check(r, rec); c[v] += 1; tot[r["kind"].split(".")[-1]][v] += 1
            said["a call on comms (what a team means to do, or says the enemy is doing)" if r["kind"][:2] in ("i.", "s.") else "something seen happening"][v] += 1
            if show and v == "differs": print(f"  {name} {clock(r['at'])} (match {clock(max(r['t'], 0))}) {r['kind']} {r['team']} {','.join(r['who'])} {r['arg']}: {r['say']}\n      -> {why}")
            if v == "unknown kind": print("  UNKNOWN", r)
        per[name] = c
    cols = ("agrees", "differs", "to build", "not ruled", "sealed", "out of scope")
    print(f"{'game':34}" + "".join(f"{c:>13}" for c in cols))
    for k, c in per.items(): print(f"{k:34}" + "".join(f"{c[x]:13}" for x in cols))
    print(f"\n{'kind':10}" + "".join(f"{c:>13}" for c in cols))
    for k, c in sorted(tot.items(), key=lambda kv: -sum(kv[1].values())): print(f"{k:10}" + "".join(f"{c[x]:13}" for x in cols))
    sm = {x: sum(c[x] for c in per.values()) for x in cols}; chk = sm["agrees"] + sm["differs"]
    print(f"\nall: {sum(sm.values())} statements; checked {chk}: agrees {sm['agrees']} ({round(100 * sm['agrees'] / max(chk, 1))}%), differs {sm['differs']}; "
          f"to build {sm['to build']}, not ruled {sm['not ruled']}, sealed {sm['sealed']}, out of scope {sm['out of scope']}")
    for k, c in said.items():
        n = c["agrees"] + c["differs"]
        print(f"  {k}: checked {n}, agrees {c['agrees']} ({round(100 * c['agrees'] / max(n, 1))}%)")


def files(data):
    """The statement files: the building games in the folder itself, the held-out games in its `held` subfolder (R-397)."""
    return sorted(glob.glob(os.path.join(data, "*.txt")) + glob.glob(os.path.join(data, "held", "*.txt")))


if __name__ == "__main__":
    av = sys.argv[1:]
    if not av: print(__doc__); sys.exit()
    data = os.path.join(HERE, "..", "..", "data", "lineup")
    if "--data" in av: i = av.index("--data"); data = av[i + 1]; del av[i:i + 2]
    if av[0] == "lines":
        rec = record(next((os.path.basename(f).split(".")[0] for f in files(data) if os.path.basename(f).startswith(av[1])), av[1]))
        for t, s in rec["story"]:
            if secs(av[2]) <= t <= secs(av[3]) and (len(av) < 5 or re.search(av[4], s)): print(clock(t), s[:260])
    elif av[0] == "score":
        show = "--show" in av; held = "--held" in av
        ids = [x for x in av[1:] if not x.startswith("--")]
        if held and show and "--gate" not in av: sys.exit("The held-out games' lines are read once, by Denning, at the gate (R-370, R-396): add --gate for that review.")
        paths = [p for p in files(data) if not ids or any(os.path.basename(p).startswith(i) for i in ids)]
        paths = [p for p in paths if (load(p)[0].get("held_out", "no") == "yes") == held]
        score(paths, show)
