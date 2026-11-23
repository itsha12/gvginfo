#!/usr/bin/env python3
"""The review key (R-450, R-491 to R-497): every row Denning has marked.

From 2026-11-15 he grades each situation on a fresh game (R-492): Classic, Visible, Weak, No decision (or Repeat), and
for a decision says whether the engine read it Correct, Partly or Incorrect. Only a Classic row is a test the reading
must go on passing (R-494); a Visible, Weak or No decision row is reported. The rows marked before that day (sets 1,
w1p1, w1p2, w2) are history (R-491): scored and reported after every change, and they never block one.

  python3 tools/golden/review.py score <plays file> [--key <path>]   score a run (from `moments.py all <file> --dev`)
  python3 tools/golden/review.py rows [--key <path>]                 the rows and their marks
  python3 tools/golden/review.py game <report id> <plays file>       one whole game, every situation the engine reads, as a
                                                                     table for him to mark while he watches it (R-454)
  python3 tools/golden/review.py file <report id> <rows.json> <marks.json> --set w2
                                                                     his marks on one game of the page into the key (rows, his words,
                                                                     the text he saw; no checks), with the game's score
  python3 tools/golden/review.py numbers [--steps 0.5,0.75,1.25,2] [--names FIGHT_LINK,JOIN_S]
                                                                     the numbers test (R-470): each draft number of the fight reading
                                                                     at those shares of its value, against every marked row (about a
                                                                     minute a value, one at a time: a run already uses every core)
  python3 tools/golden/review.py compare <report id> <rows.json> <marks.json> <plays he marked> name=<plays> ...
                                                                     one marked game, several engines against his verdicts on
                                                                     it (the before-and-after test)
  python3 tools/golden/review.py export <plays file> <out.json> --part N --confidence <file from confidence.py run> [--set f1] [--label "game 1"] [--drop <id>,<id>]
                                                                     the games of that part of a whole-game set (dev_set.json) as
                                                                     the rows of the site's Model > Game review page, where he
                                                                     marks the reading of each situation and each side's call
                                                                     (R-455; written to main's data/model/game_reviews.json; his
                                                                     marks are saved by the page to game_review_marks.json)
  python3 tools/golden/review.py lord <out.json> <report id>:<m:ss> ... [--gvg <main>/data/model/lord_gvg.json]
                                                                     picked Lord pushes as the rows of the site's Model > Game review
                                                                     > Lord push view (R-633; written to main's data/model/lord_rows.json;
                                                                     his marks are saved by the page to lord_row_marks.json). Reads the
                                                                     matches itself, with no plays file. Each row sets gvg.report's own
                                                                     Lord damage total for the match beside the engine's summed hits (R-632),
                                                                     and with --gvg gvg.report's own record of the push: its Lord damage,
                                                                     Entourage, each team's aggressiveness going in and coming out, the
                                                                     Lord's health
  python3 tools/golden/review.py lord-record <out.json> <probe file> ...
                                                                     gvg.report's Lord damage record of single matches, from files of the
                                                                     probe branch fetched with pick summary.objectives.guild_lord_damage,
                                                                     kept small (scores, every hit, heal and effect on a Lord by the
                                                                     second, the pit NPCs' deaths, Entourage, health where it changes);
                                                                     matches already in the file are kept. A stand-in until the trim
                                                                     keeps this record for every match (R-632)

The key (`data/model/review_key.json`, on main; a copy rides on the branch) holds, for each row he was shown: the match,
the window, what the engine said then (`shown`), his mark and his words (`said`), and `checks`: Claude's reading of his
mark as things the plays must hold or must not hold, which he corrects. A check names plays by `play`, `side`, `team` and
a window in seconds of match time (`at` = the play overlaps it, `start` = the play begins inside it, `end` = it ends inside it), and `want` gives the
fields they must carry (`who~` = these roles among who, `who#` = how many, `scenario~` = these words in the scenario, `tests` = a test of the play by its words and whether it held; a
list of values = any of them; a dotted name such as `clock.their_waited_back` reads inside a field). `has` passes when one play fits, `none` when no play fits. A check marked `open` is a
fault known and not yet fixed: it is reported apart and does not fail the row. Engine faults go here as checks, never
into RULINGS.md (R-452). An accuracy figure by kind of play comes from the rows of a whole-game review (R-454), where
every call of a game is marked, not from rows picked to cover rare plays."""
import collections, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
KEY = os.path.join(REPO, "data", "model", "review_key.json")
cl = lambda t: f"{int(t) // 60}:{int(t) % 60:02d}"


def fits(p, sel, want):
    for k in ("play", "side", "team"):
        if k in sel and p.get(k) != sel[k]: return False
    if "at" in sel and not (p["t1"] >= sel["at"][0] and p["t0"] <= sel["at"][1]): return False
    if "start" in sel and not (sel["start"][0] <= p["t0"] <= sel["start"][1]): return False
    if "end" in sel and not (sel["end"][0] <= p["t1"] <= sel["end"][1]): return False
    for k, v in (want or {}).items():
        if k == "who~":
            if not all(any(w in r for r in p.get("who", [])) or w in p.get("scenario", "") for w in v): return False
        elif k == "who#":
            if len(p.get("who", [])) != v: return False
        elif k == "tests":                                   # {words of a test: held or not}, among the play's tests
            T = dict(p.get("tests", {}), **p.get("any_of", {}))
            for w, val in v.items():
                got = [x for q, x in T.items() if w in q]
                if not got or bool(got[0]) != val: return False
        elif k == "scenario~":
            if not all(w in p.get("scenario", "") for w in ([v] if isinstance(v, str) else v)): return False
        elif isinstance(v, list):
            if _get(p, k) not in v: return False
        elif _get(p, k) != v: return False
    return True


def _get(p, k):
    """A field of a play, or one inside it by a dotted name (`clock.their_waited_back`: what a flag card is written from)."""
    for part in k.split("."):
        p = p.get(part) if isinstance(p, dict) else None
    return p


def check(plays, c):
    kind = "has" if "has" in c else "none"
    sel = c[kind]
    hit = [p for p in plays if fits(p, sel, c.get("want") if kind == "has" else sel.get("want"))]
    return bool(hit) if kind == "has" else not hit


def binding(r):
    """Only a row he graded Classic is a test the reading must pass (R-494). A row of the earlier marking (no grade) is
    history (R-491), and a Visible, Weak or No decision row is reported: none of them blocks a change."""
    return r.get("grade") == "classic"


def score(path, key=KEY):
    K = json.load(open(key)); D = json.load(open(path))
    by = collections.defaultdict(list)
    for p in D["plays"]: by[p["rid"]].append(p)
    res, missing, by_type = collections.Counter(), [], collections.defaultdict(lambda: [0, 0])
    opened = collections.defaultdict(lambda: [0, 0])          # set -> [open checks that now hold, open checks]
    for r in K["rows"]:
        if not r.get("checks"): res["no check (not marked, or nothing to test)"] += 1; continue
        if r["rid"] not in by: missing.append(r["id"]); continue
        firm = [c for c in r["checks"] if not c.get("open")]; opn = [c for c in r["checks"] if c.get("open")]
        bad = [c for c in firm if not check(by[r["rid"]], c)]
        still = [c for c in opn if not check(by[r["rid"]], c)]
        opened[r.get("set")][0] += len(opn) - len(still); opened[r.get("set")][1] += len(opn)
        ok = not bad
        what = "classic" if binding(r) else (r.get("grade") or "history")
        if not binding(r):
            res[f"{what}, holds" if ok else f"{what}, does not hold (reported; blocks nothing)"] += 1
            if bad: print(f"{what} {r['id']} ({r['type']}; his mark: {r.get('mark')}) {r['match']} {cl(r['window'][0])}-{cl(r['window'][1])}: no longer holds")
        else:
            res["classic, pass" if ok else "FAIL"] += 1
            by_type[r["type"]][0] += ok; by_type[r["type"]][1] += 1
            if bad:
                print(f"FAIL classic {r['id']} ({r['type']}; his mark: {r['mark']}) {r['match']} {cl(r['window'][0])}-{cl(r['window'][1])}")
                for c in bad: print("     ", json.dumps(c, ensure_ascii=False))
        for c in still: print(f"open {r['id']} ({r['type']}; {what}): {c.get('why', '')}")
        for c in opn:
            if c not in still: print(f"now passes, was open: {r['id']} ({r['type']}): {c.get('why', '')}")
    print("\nThe review key:", ", ".join(f"{v} {k}" for k, v in sorted(res.items())), (f"; matches not in the run: {missing}" if missing else ""))
    print("Open checks that hold now, of the open checks, by set: " + "; ".join(f"{k}: {a} of {b}" for k, (a, b) in sorted(opened.items(), key=str) if b))
    if by_type: print("Classic rows by kind of play (passing of checked): " + "; ".join(f"{k} {a}/{b}" for k, (a, b) in sorted(by_type.items())))
    return res["FAIL"]


def situations(plays):
    """A game's plays grouped into situations: the two sides of one split phase, of one numbers moment, of one push on
    a flagger or of one Lord push are one situation, read once and judged from each side."""
    G = collections.OrderedDict()
    flags = [p for p in plays if (p["play"] == "flag" and p.get("run_id")) or p["play"] == "opening"]
    for p in sorted([p for p in plays if p not in flags], key=lambda p: (p["t0"], p["t1"])):
        kind = {"flagger pushed": "push flagger"}.get(p["play"], p["play"])
        k = (kind, p["t0"]) if kind == "numbers" else (kind, p["t0"], p["t1"]) if kind in ("lord", "push flagger") else (kind, p["t0"], p.get("size"), p.get("defenders")) if kind == "split" else (kind, p["t0"], p["team"])
        if kind == "split" and p.get("change") and p.get("of"):       # R-514: who joins, collapses on or leaves a split fight is a decision of its own in the data, shown in the row of the split it belongs to
            k = next((q for q in G if q[0] == "split" and abs(q[1] - p["of"][1]) <= 2 and any(x["side"] == "attacker" and x["tm"] == p["of"][0] and not x.get("change") for x in G[q])), k)
        elif kind == "split":                             # the attacker's and the defender's play of a phase can end a few seconds apart
            k = next((q for q in G if q[0] == "split" and q[2:] == k[2:] and abs(q[1] - k[1]) <= 2 and not all(x.get("change") for x in G[q])), k)
        G.setdefault(k, []).append(p)
    return sorted(list(G.values()) + flag_rows(flags), key=lambda g: (min(p["t0"] for p in g), max(p["t1"] for p in g)))


def flag_rows(flags):
    """The flag plays of a game as rows in which every run is told once (R-521, his words: "We have many runs being counted or explained twice ... the opening
    is described twice, single runs are described from both players sides even though one is really responding to the other and it's duplicated"). A flag play
    is one team's answer to the other's run, and the run it answers with is in turn answered, so each run stood in two rows. Here the opening is one row (R-520),
    and after it a row is a run and the run that answers it: the play that judges each of the two is under it, a stay or a flag in hand that follows the answer
    is said in the same row, and the two legs of a double run are one run. A run that only answers one already told gets a row of its own, said as an answer."""
    rows, P = [], sorted(flags, key=lambda p: (p["t0"], p["t1"]))
    op = [p for p in P if p.get("opening")]
    told = {x for p in op for x in (p.get("run_id"), p.get("answer_id")) if x}
    if op:
        own = [p for p in op if p["play"] == "opening"]      # each team's first flag, the same job for both (R-520); a first flag that was more than that (a double run from the gates, a flag held in hand) keeps its own call beside them
        op = (own + [p for p in op if p["play"] != "opening" and p["job"] != "Get the first flag in"]) if own else op
        for p in op: p["_row"] = op[0]["opening"]
        rows.append(op)
    P = [p for p in P if not p.get("opening")]
    when = lambda r: int(r.split("-", 1)[1])
    by_trigger, by_answer = {}, collections.defaultdict(list)
    for p in P:
        by_trigger.setdefault(p["run_id"], p)
        if p.get("answer_id"): by_answer[p["answer_id"]].append(p)
    for r in sorted({x for p in P for x in (p["run_id"], p.get("answer_id")) if x}, key=lambda r: (when(r), r)):
        if r in told: continue
        told.add(r)
        lead = by_trigger.get(r)
        ans = lead.get("answer_id") if lead is not None else None
        pair = [r] + ([ans] if ans and ans not in told else [])
        told.update(pair)
        row = [p for x in pair for p in by_answer.get(x, [])]
        row += [p for x in pair for p in [by_trigger.get(x)] if p is not None and not p.get("answer_id") and p not in row]      # they stay, or have a flag in hand: said with the run it answers
        if lead is not None and lead not in row and (ans is None or ans in told) and not any(lead is q for g in rows for q in g): row.append(lead)      # its answer was told already, as the answer to an earlier run
        row = [p for i, p in enumerate(row) if not any(p is q for q in row[:i]) and not any(p is q for g in rows for q in g)]
        if not row: continue
        if lead is not None:
            text = lead["said"][0] + "; " + lead["said"][1]
            after = by_trigger.get(ans) if len(pair) > 1 else None
            if after is not None and not after.get("answer_id") and after in row: text += "; " + after["said"][1].replace(" stays", " then stays", 1)
        else:
            q = by_answer[r][0]
            text = q["said"][1] + ", in answer to " + q["said"][0]
        for p in row: p["_row"] = text
        rows.append(sorted(row, key=lambda p: (p["t0"], p["t1"])))
    left = [p for p in P if not any(p is q for g in rows for q in g)]      # nothing is dropped: a play no row took is a row of its own
    for p in left: p["_row"] = p["scenario"]
    return rows + [[p] for p in left]


def game(rid, path, set_id="w"):
    """One game, every situation the engine reads, as a table for Denning to mark while he watches it (R-454)."""
    D = json.load(open(path)); rid = next(r for r in D["matches"] if r.startswith(rid)); m = D["matches"][rid]
    P = [p for p in D["plays"] if p["rid"] == rid]
    print(f"**{' v '.join(m['teams'])}, {m['map']}, {m['date']}** ([replay](https://gvg.report/report/{rid}#map)); {len(situations(P))} situations\n")
    print("| # | Time | What the engine reads | Each side's job & result |\n|---|---|---|---|")
    for i, g in enumerate(situations(P), 1):
        read = _reads(g)
        res = []
        for p in g:
            tests = [("yes: " if v else "no: ") + k for k, v in list(p["tests"].items()) + list(p.get("any_of", {}).items())]
            lab = label_of(p)
            res.append(f"**{p['team']}**" + (f" ({p['side']})" if p["side"] not in ("own",) and p["play"] in ("split", "lord") else "") + (f" [{lab}]" if lab else "") + f": {p['job']}. **{'Met' if p['met'] else 'Not met'}**" + (" (" + "; ".join(tests) + ")" if tests else "") + ("" if p.get("ruled", True) else " *(job is a draft)*"))
        print(f"| {i} | {cl(g[0]['t0'])}–{cl(max(p['t1'] for p in g))} | {read} | " + "<br>".join(res) + " |")


FIRST = {"split": ("attacker", "defender", "attacker's main team", "defender's main team"), "lord": ("attacker", "defender")}


def label_of(p):
    """The call of a play in a word or two. At the opening a team's first flag is not called a run (R-520)."""
    if p.get("opening"): return "the first flag" + ("" if p.get("ours") in (None, "single run") else f": {p.get('ours')}")
    return p.get("call") or p.get("answer") or p.get("ours") or ""


def _reads(g):
    """What the engine reads in a situation, in one line; sorts its plays (the attacker first, then the defender)."""
    g.sort(key=lambda p: (bool(p.get("change")), p.get("at", 0) if p.get("change") else 0, FIRST.get(p["play"], ()).index(p["side"]) if p["side"] in FIRST.get(p["play"], ()) else 0, p["play"] != "push flagger"))
    if g[0].get("_row"): return g[0]["_row"] + (" (Shadow of Haste run: set aside)" if any(p.get("soh") for p in g) else "")      # a flag row: every run told once (R-521), the opening as one description (R-520)
    read = g[0]["scenario"] + ("; ".join([""] + [p["scenario"].split(": ", 1)[-1] for p in g[1:] if p["play"] == "split" and not p.get("change") and p["side"] == "defender" and p.get("call") in ("collapse", "full collapse", "part-run")]))
    def move(p):                                          # "Ranger joins the split at 18:28"; "Hammer B, 8 Monk join the defence at 12:48"
        one, what = len(p["who"]) == 1, p.get("call") or p.get("answer")
        verb = {"join": "joins" if one else "join", "leave": "leaves" if one else "leave", "collapse": "collapses on it" if one else "collapse on it"}.get(what, what)
        return f"{', '.join(p['who'])} ({p['team']}) {verb}" + ("" if what == "collapse" else " the split" if p["side"] == "attacker" else " the defence") + f" at {cl(p.get('at', p['t0']))}"
    moves = [move(p) for p in g if p.get("change")]
    if moves and not g[0].get("change"): read += ". Who came and went, each a decision of its own: " + "; ".join(dict.fromkeys(moves))
    if g[0]["play"] == "numbers" and len(g) > 1:
        o = g[1]["scenario"]; k = o.find("), from ")                    # the other side's call: what follows the numbers and their source (the numbers themselves can hold "; then ...")
        read += " | " + o[max(k, 0):].split("; ", 1)[-1]
    if g[0].get("soh"): read += " (Shadow of Haste run: set aside)"
    return read


BANDS = ("none", "low", "medium", "high")
REASONS = {"brief": "too brief", "small": "impact too small to make a difference", "nofight": "no real fight, nothing at stake", "unclear": "weak or unclear small edge in a real game"}      # his four reasons for a Weak or No decision grade (2026-11-16), ticked on the page


import confidence as bands_of                              # tools/golden/confidence.py: the band of a reading


def export(path, out, part, set_id="f1", label=None, drop=(), confidence=None):
    """The games of one part of a whole-game set as the rows of the site's Game review page (R-455): for each situation
    what the engine reads, and under it each side's call with its job, the result and the tests behind the result. He
    marks the reading and every call on its own. Games already in the file from another part are kept."""
    import datetime, subprocess
    D = json.load(open(path))
    if not confidence: sys.exit("export: give --confidence <file from tools/golden/confidence.py run>: every situation is put to him with the engine's confidence (R-492)")
    C = json.load(open(confidence))["plays"]
    whole = json.load(open(os.path.join(REPO, "data", "model", "dev_set.json")))["whole_game"]
    want = [w["rid"] for w in whole if w["set"] == set_id and w.get("part") == part]
    kept_back = {w["rid"] for w in whole if w.get("part") in ("hidden", "spare")}                                    # R-467: never on the page, whatever is asked for
    main_labels, own_labels = os.path.join(os.path.dirname(os.path.abspath(out)), "..", "maps", "labels"), os.path.join(REPO, "data", "maps", "labels")
    if os.path.isdir(main_labels):                                                                                   # his hall labels are saved to main: rows read from older labels would be put to him as the engine's reading
        differ = [f for f in sorted(os.listdir(main_labels)) if f.endswith(".json") and (not os.path.exists(os.path.join(own_labels, f)) or open(os.path.join(main_labels, f), "rb").read() != open(os.path.join(own_labels, f), "rb").read())]
        if differ: sys.exit("export: hall labels on main differ from the branch (" + ", ".join(differ) + "): copy them over, run the development set again, then export")
    old = json.load(open(out)) if os.path.exists(out) else {"games": []}
    games = [g for g in old["games"] if g["rid"] not in want and g["rid"] not in kept_back and not any(g["rid"].startswith(x) for x in drop)]      # drop: games taken off the page
    for rid in want:
        m = D["matches"][rid]; P = [p for p in D["plays"] if p["rid"] == rid]; sits = []
        if rid not in C or any(p["id"] not in C[rid] for p in P): sys.exit(f"export: {rid[:8]} has plays the confidence file does not hold: run confidence.py on this engine first (R-460)")
        for i, g in enumerate(situations(P), 1):
            read = _reads(g); calls = []
            unclear = g[0].get("unclear") if all(p.get("clear") is False for p in g) else None      # R-488: nothing a team clearly had to decide: told as context, with no call under it
            for p in ([] if unclear else g):
                side = p["side"] if p["side"] not in ("own",) and p["play"] in ("split", "lord", "numbers") else ""
                moved = f": {', '.join(p['who'])} at {cl(p['at'])}" if p.get("change") and p.get("at") is not None else ""
                calls.append({"id": p["id"], "team": p["team"], "side": side, "label": label_of(p) + moved + (f": {p['hand']}" if p.get("hand") else ""), "job": p["job"], "met": bool(p["met"]),
                              "tests": [[bool(v), k] for k, v in list(p["tests"].items()) + list(p.get("any_of", {}).items())], "any": bool(p.get("any_of")) and bool(p["tests"]) is False, "draft": not p.get("ruled", True)})
            # one band a situation (R-515): low when a quarter's move makes the engine stop reading it, medium when it is still read but its details move, or it goes at half or double (confidence.py, fitted to his grades of five games)
            both = bands_of.band_of([C[rid][p["id"]] for p in g if not p.get("change")] or [C[rid][p["id"]] for p in g], [C[rid][p["id"]] for p in g if p.get("change")] if not all(p.get("change") for p in g) else ())
            conf = {"band": "none", "why": unclear[0].upper() + unclear[1:] + "."} if unclear else {"band": both["band"], "why": both["why"]}
            sits.append({"n": i, "id": "s:" + g[0]["id"], "kind": "opening" if g[0].get("opening") else {"flagger pushed": "push flagger"}.get(g[0]["play"], g[0]["play"]), "t0": g[0]["t0"], "t1": max(p["t1"] for p in g), "reads": read, "confidence": conf,
                         "plays": [{"play": p["play"], "team": p["team"], "t0": p["t0"]} for p in g], "calls": calls, **({"unclear": unclear} if unclear else {})})
        twice = (D.get("flag_cost", {}).get(rid) or {}).get("selfcheck") or []
        games.append({"scheme": 2, "set": set_id, "part": part, "label": label or f"part {part}", "rid": rid, "teams": m["teams"], "map": m["map"], "date": m["date"], "situations": sits,
                      "selfcheck": [f"{c['who']} {cl(c['from'])} to {cl(c['to'])}: {c['in'][0]} and {c['in'][1]}" for c in twice]})
    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    json.dump({"about": "The rows of Model > Game review (R-454, R-455, R-492): every situation the engine reads in each review game, with the engine's confidence that it is a decision, written by tools/golden/review.py export on the engine branch. Games with scheme 2 are graded his new way; the others are history (R-491). His marks are in game_review_marks.json, never here.",
               "generated": datetime.date.today().isoformat(), "engine": commit, "games": games}, open(out, "w"), ensure_ascii=False, indent=1)
    print("; ".join(f"{' v '.join(g['teams'])}: {len(g['situations'])} situations, {sum(len(s['calls']) for s in g['situations'])} calls" for g in games))


LORD_KIND = {"damage": "d", "life_steal": "l", "heal": "h", "effect": "e"}


def lord_record(out, files):
    """gvg.report's own Lord damage record of single matches (R-632), from probe files fetched with the pick
    `summary.objectives.guild_lord_damage`, kept small. Per match: `scores` (each team's damage to the enemy Lord, the
    attacks missed through Blind at 30 each, what it cast on its own Lord and what that cost, and its aggressiveness,
    gvg.report's `lord_damage_equivalent`), `lords` (each Lord's damage, life steal, which is no Lord damage, healing),
    `events` ([second, the Lord's team, kind (d damage, l life steal, h heal, e effect), amount, Blind miss worth,
    effect cost, Entourage up, the source's team, the effect's name]), `deaths` (the pit NPCs: [second, the Lord's
    team, kind]), `entourage` ([the Lord's team, second, seconds]) and `health` (each Lord's health where it changes:
    [second, health, max]; gvg.report's own estimate). Fails where the scores cannot be rebuilt from the events (R-460)."""
    import datetime, re
    D = json.load(open(out)) if os.path.exists(out) else {"matches": {}}
    for f in files:
        rid = "-".join(re.search(r"reports_([0-9a-f]{8})_([0-9a-f]{4})_([0-9a-f]{4})_([0-9a-f]{4})_([0-9a-f]{12})_payload_summary", os.path.basename(f)).groups())
        txt = open(f, encoding="utf-8").read(); key = '{"summary.objectives.guild_lord_damage"'
        if key not in txt: sys.exit(f"lord-record: {f} holds no Lord damage record ({txt[:60]!r})")
        g = json.loads(txt[txt.index(key):])["summary.objectives.guild_lord_damage"]
        if not g: sys.exit(f"lord-record: {rid[:8]} has an empty Lord damage record")
        r1 = lambda v: round(v or 0, 1)
        ev = [[r1(e["match_time_ms"] / 1000), e["guild_lord_team_id"], LORD_KIND[e["kind"]], r1(e.get("amount_estimate")), r1(e.get("blind_miss_activity_equivalent")) if e["kind"] == "damage" else 0,
               r1(e.get("activity_equivalent")) if e["kind"] == "effect" else 0, int(bool(e.get("entourage_active"))), e.get("source_team_id"), e.get("effect_name") or ""] for e in g["events"]]
        ev.sort(key=lambda x: x[0])
        scores = {}
        for sc in g["team_scores"]:
            tm = sc["team_id"]
            if tm not in (1, 2): continue                                    # "map": what a hall's own objects did to a Lord (a trebuchet), which gvg.report credits to no team
            built = sum(x[3] + x[4] for x in ev if x[2] == "d" and x[1] == 3 - tm and x[7] == tm) - sum(x[5] for x in ev if x[2] == "e" and x[1] == tm and x[7] == tm)
            if abs(built - sc["lord_damage_equivalent"]) > 2: sys.exit(f"lord-record: {rid[:8]} team {tm}: the events come to {built:.0f}, gvg.report's own score is {sc['lord_damage_equivalent']:.0f}")
            scores[str(tm)] = {"damage": r1(sc["damage_to_enemy_lord"]), "blind": r1(sc["blind_miss_equivalent_to_enemy_lord"]), "own_effects": sc["own_lord_effect_events"], "penalty": r1(sc["own_lord_penalty_equivalent"]),
                               "aggressiveness": r1(sc["lord_damage_equivalent"])}
        health = {"1": [], "2": []}
        for h in g["health_samples"]["samples"]:
            L = health[str(h["guild_lord_team_id"])]; row = [h["match_time_ms"] // 1000, round(h["current_hp"]), round(h["max_hp"])]
            if not L or L[-1][1:] != row[1:]: L.append(row)
        D["matches"][rid] = {"scores": scores, "events": ev, "health": health,
                             "lords": {str(l["team_id"]): {"damage": r1(l["damage_taken"]), "life_steal": r1(l["life_steal_health_loss"]), "healing": r1(l["healing_received"]), "hits_under_entourage": l["entourage_damage_events"]} for l in g["guild_lords"]},
                             "deaths": [[r1(d["match_time_ms"] / 1000), d["guild_lord_team_id"], d["defender_kind"]] for d in g["defender_deaths"]["events"]],
                             "entourage": [[i["team_id"], r1(i["match_time_ms"] / 1000), r1(i["duration_ms"] / 1000)] for i in g["entourage_intervals"]],
                             "worth": {"blind_miss": g["constants"]["blind_miss_activity_equivalent"], "effect": g["constants"]["lord_effect_base_equivalent"], "effect_under_entourage": g["constants"]["lord_effect_entourage_equivalent"]}}
        print(f"{rid[:8]}: {len(ev)} events; aggressiveness " + ", ".join(f"team {k} {v['aggressiveness']:,.0f}" for k, v in scores.items()))
    D["about"] = "gvg.report's own Lord damage record (`summary.objectives.guild_lord_damage`) for single matches, kept small by tools/golden/review.py lord-record on the engine branch from files of the probe branch. A stand-in until the trim keeps this record for every match (R-632); the Lord push rows read it (review.py lord --gvg). Seconds are match time."
    D["generated"] = datetime.date.today().isoformat()
    json.dump(D, open(out, "w"), ensure_ascii=False, separators=(",", ":"))


def _lord_gvg(rec, tm, foe, t0, t1, tag, n):
    """gvg.report's own record of one push (R-632): team tm on foe's Lord from t0 to t1. The figures, and the lines the
    row says them in."""
    E = rec["events"]; inp = lambda x: t0 <= x[0] < t1 + 1
    # a hit counts for the team that dealt it, a cast against the team that cast it on its own Lord; what a hall's own objects did to a Lord (source "map") is nobody's
    dmg = lambda lord, f=inp: sum(x[3] for x in E if x[2] == "d" and x[1] == lord and x[7] == 3 - lord and f(x))
    steal = lambda lord: sum(x[3] for x in E if x[2] == "l" and x[1] == lord and x[7] == 3 - lord and inp(x))
    hits = [x for x in E if x[2] == "d" and x[1] == foe and x[7] == tm and inp(x) and x[3] > 0]; under = sum(1 for x in hits if x[6])
    blind = sum(x[4] for x in E if x[2] == "d" and x[1] == foe and x[7] == tm and inp(x))
    agg = lambda k, t: sum(x[3] + x[4] for x in E if x[2] == "d" and x[1] == 3 - k and x[7] == k and x[0] < t) - sum(x[5] for x in E if x[2] == "e" and x[1] == k and x[7] == k and x[0] < t)
    cast = {k: [x for x in E if x[2] == "e" and x[1] == k and x[7] == k and inp(x)] for k in (tm, foe)}
    def hp(lord, t):
        H = [h for h in rec["health"][str(lord)] if h[0] <= t]
        return H[-1][1:] if H else None
    a0, a1, fin = {k: agg(k, t0) for k in (tm, foe)}, {k: agg(k, t1 + 1) for k in (tm, foe)}, {k: rec["scores"][str(k)]["aggressiveness"] for k in (tm, foe)}
    us, them = tag[tm], tag[foe]; h0, h1 = hp(foe, t0), hp(foe, t1)
    lines = [f"Lord damage in this push by gvg.report's own record: {n(dmg(foe))} on {them}'s Lord" + (f" ({n(steal(foe))} more is life steal, which gvg.report does not count)" if steal(foe) >= 0.5 else "")
             + (f", {under} of its {len(hits)} hit{'s' if len(hits) != 1 else ''} with Entourage up" if hits else "") + (f", and {n(blind)} for attacks missed through Blind" if blind else "") + f"; {n(dmg(tm))} on {us}'s Lord meanwhile."]
    for k in (foe, tm):
        if cast[k]:
            ent = sum(1 for x in cast[k] if x[6]); cost = sum(x[5] for x in cast[k])
            lines.append(f"{tag[k]} cast {len(cast[k])} enchantment{'s' if len(cast[k]) != 1 else ''} or weapon spell{'s' if len(cast[k]) != 1 else ''} on its own Lord during it" + (f", {ent} with Entourage up" if ent else "") + f": {n(cost)} off its aggressiveness.")
    lines.append(f"Aggressiveness by gvg.report's count, {us} against {them}: {n(a0[tm])} against {n(a0[foe])} going in, {n(a1[tm])} against {n(a1[foe])} coming out; {n(fin[tm])} against {n(fin[foe])} when the match ends.")
    if h0 and h1: lines.append(f"{them}'s Lord by gvg.report's estimate: {n(h0[0])} of {n(h0[1])} health going in, {n(h1[0])} coming out.")
    return {"push": [round(dmg(foe)), round(dmg(tm))], "life_steal": [round(steal(foe)), round(steal(tm))], "hits": len(hits), "under_entourage": under, "blind": round(blind),
            "aggressiveness": {"in": [round(a0[tm]), round(a0[foe])], "out": [round(a1[tm]), round(a1[foe])], "end": [round(fin[tm]), round(fin[foe])]}, "own_lord_casts": [len(cast[foe]), len(cast[tm])],
            "their_lord_health": [h0, h1]}, lines


def gvg_total(m, lord_team):
    """gvg.report's own Lord damage total on a team's Lord, as the stored replay keeps it."""
    return next((l.get("taken") or 0 for l in m.o.get("lords", []) if l["team"] == lord_team), 0)


def lord_rows(out, picks, gvg=None):
    """Picked Lord pushes as the rows of the site's Lord push view (R-633): one row a push, told from the attacker's
    play with the defender's beside it. Lord damage (R-632): gvg.report's own figure is the one of record, and what is
    stored of it is each Lord's total for the match, so the row sets that total beside the engine's sum of the recorded
    hits, for the push and for the match; the two differ where gvg.report leaves hits out (life steal, on the one
    match probed). A pick is <report id or its start>:<m:ss>, the second the push begins."""
    import datetime, subprocess
    sys.path.insert(0, os.path.join(REPO, "tools", "replay_analysis"))
    import common, jobs, moments
    from replaylib import Match
    from state import GameState
    idx = common.replay_index(all_dates=True); n = lambda v: f"{int(round(v)):,}"
    rows = []
    G = json.load(open(gvg))["matches"] if gvg else {}
    for pick in picks:
        head, at = pick.split(":", 1); mm, ss = at.split(":"); want = int(mm) * 60 + int(ss)
        rid = next((r for r in idx if r.startswith(head)), None)
        if rid is None: sys.exit(f"lord: no stored replay starts with {head}")
        M = moments.Moments(GameState(Match.from_branch(rid))); m = M.m; e = idx[rid]
        P = [p for p in jobs.plays(M) if p["play"] == "lord"]
        att = [p for p in P if p["side"] == "attacker" and abs(p["t0"] - want) <= 2]
        if len(att) != 1: sys.exit(f"lord: {rid[:8]} has {len(att)} Lord pushes beginning at {at} (it reads them at " + ", ".join(cl(p["t0"]) for p in P if p["side"] == "attacker") + ")")      # R-460
        a = att[0]; d = next(p for p in P if p["side"] == "defender" and p["t0"] == a["t0"] and p["t1"] == a["t1"] and p["tm"] != a["tm"])
        tm, foe, b = a["tm"], d["tm"], a["beside"]; us, them = m.tag[tm], m.tag[foe]
        hits = {k: sum(v for _, _, v in M.lord_hits.get(k, ())) for k in (1, 2)}                 # the engine's sum of the recorded hits on each team's Lord, the whole match
        gvg = {l["team"]: l.get("taken") for l in m.o.get("lords", [])}                          # gvg.report's own total on each team's Lord
        unseen = set(m.o.get("integrity", {}).get("lord_damage_unobserved", []))                # attacking teams whose Lord damage was not observed
        if gvg.get(foe) is None or gvg.get(tm) is None: sys.exit(f"lord: {rid[:8]} holds no Lord damage total from gvg.report")
        won = next((m.tag[k] for k in (1, 2) if (m.o["meta"].get("result") or {}).get("winning_team_id") == k), None)
        reads = a["scenario"].replace(" 1 pit NPCs", " 1 pit NPC")
        lines = [f"Pushing ({us}): {', '.join(a['who']) or 'nobody counted'}. Defending ({them}): {', '.join(d['who']) or 'nobody counted'}.",
                 f"{them} defends with {b['defenders']}" + (f", {b['defenders_at_the_end']} by the end" if b["defenders_at_the_end"] != b["defenders"] else "") + f" ({b['defender_monks']} monk{'s' if b['defender_monks'] != 1 else ''}). "
                 f"Deaths during it: {us} {b['deaths'][0]}, {them} {b['deaths'][1]}." + (f" {them}'s Guild Lord is killed in it." if b["lord_killed_in_it"] else ""),
                 f"The match is decided by {b['match_decided_by']}" + (f"; {won} wins." if won else ".")]
        dmg = {"push": [b["lord_damage"], b["own_lord_damage_meanwhile"]], "match_gvg": [gvg[foe], gvg[tm]], "match_hits": [round(hits[foe]), round(hits[tm])], "lords": [them, us],
               "unobserved": [3 - foe in unseen, 3 - tm in unseen]}
        said = (f"Lord damage. In this push, by the engine's sum of the recorded hits: {n(dmg['push'][0])} on {them}'s Lord, {n(dmg['push'][1])} on {us}'s meanwhile. "
                f"Whole match, gvg.report's own total: {n(dmg['match_gvg'][0])} on {them}'s Lord, {n(dmg['match_gvg'][1])} on {us}'s (the engine's summed hits: {n(dmg['match_hits'][0])} and {n(dmg['match_hits'][1])}).")
        gl = []
        if gvg:
            if rid not in G: sys.exit(f"lord: {gvg} holds no gvg.report record for {rid[:8]} (review.py lord-record)")      # R-460
            dmg["gvg"], gl = _lord_gvg(G[rid], tm, foe, a["t0"], a["t1"], m.tag, n)
            if abs(G[rid]["lords"][str(foe)]["damage"] - gvg_total(m, foe)) > 2: sys.exit(f"lord: {rid[:8]}: the record's damage on {them}'s Lord is not the stored replay's total")      # the same record, read twice (R-460)
        call = lambda p: {"team": p["team"], "side": p["side"], "job": p["job"], "met": bool(p["met"]), "tests": [[bool(v), k] for k, v in p["tests"].items()]}
        rows.append({"id": f"s:{rid[:8]}-lord-{tm}-{a['t0']}", "play": a["id"], "rid": rid, "teams": e["teams"], "map": e["map"], "date": str(e["date"])[:10], "length_s": int(M.T), "t0": a["t0"], "t1": a["t1"],
                     "reads": reads, "lines": lines, "damage": dmg, "damage_said": said, "gvg_lines": gl, "calls": [call(a), call(d)],
                     "text": " | ".join([reads] + lines + gl + [said])})
        print(f"{' v '.join(e['teams'])} {cl(a['t0'])}-{cl(a['t1'])}: {reads}\n    {said}" + "".join("\n    " + x for x in gl))
    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    json.dump({"about": "The rows of Model > Game review > Lord push (R-633): Lord pushes picked from late games for his grade and mark, written by tools/golden/review.py lord on the engine branch. Lord damage (R-632): gvg.report's own figure is the one of record; what is stored of it is each Lord's total for the match (`damage.match_gvg`, their Lord then the pushing team's own), set beside the engine's sum of the recorded hits for the push (`damage.push`) and for the match (`damage.match_hits`). His marks are in lord_row_marks.json, never here.",
               "generated": datetime.date.today().isoformat(), "engine": commit, "rows": rows}, open(out, "w"), ensure_ascii=False, indent=1)


def compare(rid, rows_file, marks_file, shown_file, others):
    """One marked game, several engines side by side (the before-and-after test): each engine's calls for the game are
    matched to the calls he was shown (same play, team, side, call, sizes and numbers, starting within 6 s) and take his
    verdict on them; a call he was never shown is counted apart, since nobody has judged it. `shown_file` is the plays
    file of the engine whose rows he marked; `others` are name=plays-file pairs. The test leans toward the engine he
    marked for the calls he called right, and against it for the wrong ones, because only its calls were judged."""
    import re
    R, Mk = json.load(open(rows_file)), json.load(open(marks_file))
    g = next(g for g in R["games"] if g["rid"].startswith(rid)); mk = Mk["games"][g["rid"]]["marks"]
    num = lambda p: (re.search(r"\((\d+ v \d+)", p["scenario"]) or [None, None])[1] if p["play"] == "numbers" else None
    sig = lambda p: (p["play"], p["team"], p.get("side"), p.get("call") or p.get("answer") or p.get("ours"), p.get("size"), p.get("defenders"), num(p))
    load = lambda f: [p for p in json.load(open(f))["plays"] if p["rid"] == g["rid"]]
    shown, verdict = load(shown_file), {}
    for s_ in g["situations"]:
        sm = mk.get(s_["id"], {}).get("mark")
        for c in s_["calls"]:
            cm = mk.get(c["id"], {}).get("mark")
            verdict[c["id"]] = sm if sm in ("repeat", "unclear") else "unmarked" if not sm else "wrong" if "wrong" in (sm, cm) else "partly" if "partly" in (sm, cm) else "right" if cm == "right" else "unmarked"
    right = [i for i, v in verdict.items() if v == "right"]
    print(f"{' v '.join(g['teams'])}: he was shown {len(verdict)} calls: " + ", ".join(f"{v} {k}" for k, v in collections.Counter(verdict.values()).most_common()))
    for name, f in others:
        res, hit = collections.Counter(), set()
        for p in load(f):
            m = [q for q in shown if q["id"] in verdict and sig(q) == sig(p) and abs(q["t0"] - p["t0"]) <= 6]
            if not m: res["never shown to him"] += 1; continue
            q = min(m, key=lambda q: abs(q["t0"] - p["t0"])); hit.add(q["id"])
            res[verdict[q["id"]] if verdict[q["id"]] != "right" or bool(q["met"]) == bool(p["met"]) else "right reading, another result"] += 1
        print(f"  {name}: {sum(res.values())} calls: " + ", ".join(f"{v} {k}" for k, v in res.most_common()) + f"; says {sum(1 for i in right if i in hit)} of his {len(right)} right calls")


def file_marks(rid, rows_file, marks_file, set_id, key=KEY):
    """His marks on one game of the Game review page into the review key (the same session, his words as he wrote them):
    one row a situation with his mark and words and the text he saw, its calls under `calls` with theirs, and one
    `missed` row for his notes on the game. Checks are not written here: they are Claude's reading of his words, added
    by hand to each row afterwards. A game filed before keeps the checks and answers already on its rows."""
    R, Mk, K = json.load(open(rows_file)), json.load(open(marks_file)), json.load(open(key))
    g = next(g for g in R["games"] if g["rid"].startswith(rid)); e = Mk["games"][g["rid"]]; mk = e["marks"]
    if g.get("scheme") == 2:                                    # graded his new way (R-492)
        file_graded(g, e, set_id, K)
        open(key, "w", encoding="utf-8").write(json.dumps(K, ensure_ascii=False, indent=1) + "\n"); return
    hall = g["map"].replace("Isle of ", "").replace(" Isle", ""); match = f"{' v '.join(g['teams'])}, {hall}"; pre = f"{set_id}-{g['rid'][:4]}-"
    old = {r["id"]: r for r in K["rows"] if r["id"].startswith(pre)}; new = []
    for s_ in g["situations"]:
        v = mk.get(s_["id"], {}); i = pre + str(s_["n"])
        row = {"id": i, "set": set_id, "row": s_["n"], "rid": g["rid"], "match": match, "window": [s_["t0"], s_["t1"]], "type": s_["kind"], "call": "", "shown": v.get("text") or s_["reads"], "mark": v.get("mark") or "not marked"}
        if v.get("why"): row["said"] = v["why"]
        row["calls"] = []
        for c in s_["calls"]:
            cv = mk.get(c["id"], {}); d = {"play": c["id"], "shown": cv.get("text", ""), "mark": cv.get("mark") or "not marked"}
            if cv.get("why"): d["said"] = cv["why"]
            row["calls"].append(d)
        row["checks"] = old.get(i, {}).get("checks", [])
        if row["mark"] == "unclear": row["tier"] = "borderline"      # R-490: no clear decision; never a row to build from
        for k_ in old.get(i, {}):
            if k_.startswith("answered") or k_ in ("tier", "tier_why", "retired_checks"): row[k_] = old[i][k_]
        new.append(row)
    i = pre + "missed"
    new.append({"id": i, "set": set_id, "row": 0, "rid": g["rid"], "match": match, "window": [0, 0], "type": "missed", "call": "", "shown": "(his notes on the game: what the engine did not read, and his questions)", "mark": "missed", "said": e.get("notes") or "", "checks": old.get(i, {}).get("checks", [])})
    K["rows"] = [r for r in K["rows"] if not r["id"].startswith(pre)] + new
    open(key, "w", encoding="utf-8").write(json.dumps(K, ensure_ascii=False, indent=1) + "\n")
    c = collections.Counter(r["mark"] for r in new if r["type"] != "missed"); j = c["right"] + c["partly"] + c["wrong"]
    print(f"{match} (engine {e.get('engine')}): situations right {c['right']}, partly {c['partly']}, wrong {c['wrong']} of {j} judged ({100 * c['right'] // max(j, 1)}%, R-475); no clear decision {c['unclear']}, repeat {c['repeat']}, not marked {c['not marked']}")
    by = collections.defaultdict(collections.Counter)
    for r in new:
        if r["type"] != "missed": by[r["type"]][r["mark"]] += 1
    print("  by kind (right of judged): " + "; ".join(f"{k} {v['right']}/{v['right'] + v['partly'] + v['wrong']}" for k, v in sorted(by.items())))
    cc = collections.Counter(d["mark"] for r in new if r["mark"] == "right" for d in r["calls"])
    print(f"  calls where the situation was right: right {cc['right']} of {sum(cc.values())}")


GRADES = ("classic", "visible", "weak", "none", "repeat")
SEC = lambda t: (lambda m: int(m[0]) * 60 + int(m[1]) if len(m) == 2 and all(x.strip().isdigit() for x in m) else None)(str(t).split(":"))


def file_graded(g, e, set_id, K):
    """His marks on one game graded the new way (R-492 to R-497) into the review key: one row a situation with the engine's
    confidence as he saw it, his grade (classic, visible, weak, none = no decision, repeat), whether the engine read it
    correct, partly or incorrect, what he ticked as off, his words, and the calls under it; one row for each decision he
    added as missed; one for his notes. Checks written here are the plain ones (`auto`): a Classic row read Correct must
    go on being read (firm: it binds, R-494); a row he graded No decision should stop being read, and a moment the engine
    told as context that he graded a decision should be read (both open: reported, built from by R-495). What a Partly
    or an Incorrect means is Claude's reading of his words and ticks, written by hand afterwards and kept on refiling."""
    mk = e["marks"]
    hall = g["map"].replace("Isle of ", "").replace(" Isle", ""); match = f"{' v '.join(g['teams'])}, {hall}"; pre = f"{set_id}-{g['rid'][:4]}-"
    old = {r["id"]: r for r in K["rows"] if r["id"].startswith(pre)}; new = []
    for s_ in g["situations"]:
        v = mk.get(s_["id"], {}); i = pre + str(s_["n"]); band = s_["confidence"]["band"]
        grade = v.get("grade") or ("none" if band == "none" else "not marked")       # a context row he left alone: he agrees there was nothing to decide
        row = {"id": i, "set": set_id, "scheme": 2, "row": s_["n"], "rid": g["rid"], "match": match, "window": [s_["t0"], s_["t1"]], "type": s_["kind"], "call": "", "shown": v.get("text") or s_["reads"],
               "band": band, "grade": grade, "mark": v.get("mark") or ("" if grade in ("none", "repeat", "not marked") or band == "none" else "not marked")}
        if v.get("off"): row["off"] = v["off"]
        if v.get("reason"): row["reason"] = v["reason"]        # why it is Weak or No decision, or not Classic (his ticks: brief, small, nofight, unclear)
        if v.get("why"): row["said"] = v["why"]
        row["calls"] = []
        for c in s_["calls"]:
            cv = mk.get(c["id"], {}); d = {"play": c["id"], "shown": cv.get("text", ""), "mark": cv.get("mark") or "not marked"}
            if cv.get("why"): d["said"] = cv["why"]
            row["calls"].append(d)
        sel = [{"play": p["play"], "team": p["team"], "start": [p["t0"] - 6, p["t0"] + 6]} for p in s_.get("plays", [])]
        auto = []
        if band != "none" and grade == "classic" and row["mark"] == "correct": auto = [{"has": x, "want": {"clear": None}, "auto": True} for x in sel]
        elif band != "none" and grade == "none": auto = [{"none": dict(x, want={"clear": None}), "open": True, "auto": True, "why": f"{match} {cl(s_['t0'])}: he graded it No decision" + (f": {v['why']}" if v.get("why") else "")} for x in sel]
        elif band == "none" and grade in ("classic", "visible", "weak"): auto = [{"has": x, "want": {"clear": None}, "open": True, "auto": True, "why": f"{match} {cl(s_['t0'])}: told as context; he graded it a {grade} decision" + (f": {v['why']}" if v.get("why") else "")} for x in sel[:1]]
        gone = [c.get("has") or c.get("none") for c in old.get(i, {}).get("retired_checks", []) if c.get("auto")]      # a plain check retired at his word (R-565: the play it asked for is no longer told) is not written again on refiling
        auto = [c for c in auto if (c.get("has") or c.get("none")) not in gone]
        row["checks"] = auto + [c for c in old.get(i, {}).get("checks", []) if not c.get("auto")]
        for k_ in old.get(i, {}):
            if k_.startswith("answered") or k_ in ("retired_checks", "later"): row[k_] = old[i][k_]      # `later`: a mark he withdrew or confirmed afterwards, in his words
        new.append(row)
    for n, x in enumerate(e.get("missed") or [], 1):
        i = pre + f"missed-{n}"; t = SEC(x.get("t", ""))
        new.append({**{k_: v_ for k_, v_ in old.get(i, {}).items() if k_.startswith("answered") or k_ in ("retired_checks", "later")},
                    **{"id": i, "set": set_id, "scheme": 2, "row": 0, "rid": g["rid"], "match": match, "window": [t if t is not None else 0, (t if t is not None else 0) + 30], "type": x.get("kind") or "missed", "call": "",
                    "shown": "(a decision the engine did not read, added by him)", "band": "not read", "grade": x.get("grade") or "classic", "mark": "missed", "at": x.get("t", ""), "said": x.get("why", ""), "checks": [c for c in old.get(i, {}).get("checks", []) if not c.get("auto")]}})
    i = pre + "notes"
    new.append({"id": i, "set": set_id, "scheme": 2, "row": 0, "rid": g["rid"], "match": match, "window": [0, 0], "type": "notes", "call": "", "shown": "(his notes on the game)", "band": "", "grade": "", "mark": "notes", "said": e.get("notes") or "", "checks": old.get(i, {}).get("checks", [])})
    K["rows"] = [r for r in K["rows"] if not r["id"].startswith(pre)] + new
    S = [r for r in new if r["mark"] not in ("missed", "notes")]
    print(f"{match} (engine {e.get('engine')}): {len(S)} situations; his grade against the engine's confidence:")
    print("   his grade      " + "".join(f"{b:>8}" for b in ("high", "medium", "low", "none")) + "   read correct / partly / incorrect")
    for gr in GRADES + ("not marked",):
        R = [r for r in S if r["grade"] == gr]
        if not R: continue
        c = collections.Counter(r["mark"] for r in R)
        print(f"   {({'none': 'no decision'}.get(gr, gr)):14} " + "".join(f"{sum(1 for r in R if r['band'] == b):8}" for b in ("high", "medium", "low", "none")) + (f"   {c['correct']} / {c['partly']} / {c['incorrect']}" if gr in ("classic", "visible", "weak") else ""))
    why = collections.Counter((r["grade"], x) for r in S for x in r.get("reason", []))
    if why: print("   his reasons (ticks), by grade: " + "; ".join(f"{({'none': 'no decision'}.get(gr, gr))}: " + ", ".join(f"{REASONS[x]} {why[(gr, x)]}" for x in REASONS if why[(gr, x)]) for gr in ("visible", "weak", "none") if any(why[(gr, x)] for x in REASONS)))
    M = [r for r in new if r["mark"] == "missed"]
    print(f"   decisions he added as missed: {len(M)}" + ("".join(f"\n      {r['at']} {r['type']} ({r['grade']}): {r.get('said', '')}" for r in M)))
    first = [r for r in new if r["grade"] == "classic" and r["mark"] in ("partly", "incorrect", "missed")] + [r for r in S if r["band"] == "none" and r["grade"] == "classic"]
    later = [r for r in first if r.get("later")]; first = [r for r in first if not r.get("later")]      # a mark he withdrew, or a reading he confirmed afterwards, is nothing to fix
    if later: print(f"   answered by him afterwards (the engine's reading stands, or the check on the row says what holds): {len(later)}" + "".join(f"\n      {cl(r['window'][0])} {r['type']} ({r['later'].get('at', '')}): {r['later'].get('said', '')}" for r in later))
    print(f"   to fix first (R-494: a Classic decision not read as he reads it): {len(first)}" + "".join(f"\n      {cl(r['window'][0])} {r['type']} [{r['mark']}{', off: ' + ', '.join(r['off']) if r.get('off') else ''}]: {r.get('said', '')}" for r in first))
    cc = collections.Counter(d["mark"] for r in S if r["grade"] in ("classic", "visible") and r["mark"] in ("correct", "partly") for d in r["calls"])
    print(f"   calls under a Classic or Visible situation read correct or partly: correct {cc['correct']}, partly {cc['partly']}, incorrect {cc['incorrect']} of {sum(cc.values())}")
    by = collections.defaultdict(collections.Counter)
    for r in S: by[r["type"]][(r["grade"], r["mark"])] += 1
    print("   by kind (classic and visible read correct, of classic and visible): " + "; ".join(f"{k} {sum(n for (gr, m), n in v.items() if gr in ('classic', 'visible') and m == 'correct')}/{sum(n for (gr, m), n in v.items() if gr in ('classic', 'visible'))}" for k, v in sorted(by.items())))


NUMBERS = ("FIGHT_LINK", "JOIN_S", "FIGHT_HOLD_S", "FIGHT_ACT", "FIGHT_HOLD", "FIGHT_CLOSE", "FOUGHT", "DOUBLE_NEXT_S")


def numbers(steps=(0.5, 0.75, 1.25, 2.0), names=NUMBERS, jobs=1, key=KEY, work="/tmp/numbers"):
    """The numbers test (R-470): each draft number of the fight reading tried at these shares of its value, one at a time,
    over the development set, and scored against every row he has marked. For each value: the marked rows that then
    fail, and the open checks that then hold. It shows where a number sits (a wide stretch where nothing changes, or an
    edge where a small step breaks rows); it is not a way to pick a value (R-465, R-470)."""
    import concurrent.futures, subprocess
    sys.path.insert(0, os.path.join(REPO, "tools", "replay_analysis")); import common
    os.makedirs(work, exist_ok=True); K = json.load(open(key))

    def read(path):
        by = collections.defaultdict(list)
        for p in json.load(open(path))["plays"]: by[p["rid"]].append(p)
        bad, held = [], []
        for r in K["rows"]:
            if not r.get("checks") or r["rid"] not in by: continue
            if r.get("tier") != "borderline" and any(not check(by[r["rid"]], c) for c in r["checks"] if not c.get("open")): bad.append(r["id"])
            held += [r["id"] for c in r["checks"] if c.get("open") and check(by[r["rid"]], c)]
        return bad, held

    def run(name, v):
        out = os.path.join(work, f"{name}_{v}.json"); env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        if name: env["GVG_TRY"] = f"{name}={v}"
        r = subprocess.run([sys.executable, "moments.py", "all", out, "--dev"], cwd=os.path.join(REPO, "tools", "replay_analysis"), env=env, capture_output=True, text=True)
        if not os.path.exists(out): return name, v, None, (r.stdout + r.stderr)[-300:]
        res = read(out); os.remove(out); return name, v, res, ""

    todo = [("", 0)]
    for n in names:
        base = getattr(common, n)
        for k in steps:
            v = base * k; v = int(round(v)) if isinstance(base, int) else round(v, 3)
            if v != base and (n, v) not in todo: todo.append((n, v))
    got = {}
    with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
        for n, v, res, err in ex.map(lambda t: run(*t), todo):
            got[(n, v)] = res; print(f"  ran {n or 'as it is'} {v if n else ''}" + (f" FAILED: {err}" if res is None else ""), file=sys.stderr, flush=True)
    b0, h0 = got[("", 0)]
    print(f"As it is: {len(b0)} marked rows fail {b0 or ''}; {len(h0)} open checks hold")
    for n in names:
        print(f"{n} = {getattr(common, n)}")
        for (m, v), res in got.items():
            if m != n: continue
            if res is None: print(f"   {v}: the run failed"); continue
            bad, held = res; new_bad = [x for x in bad if x not in b0]; new_held = [x for x in held if x not in h0]; lost = [x for x in h0 if x not in held]
            print(f"   {v}: {len(new_bad)} marked rows fail" + (f" ({', '.join(new_bad)})" if new_bad else "") + (f"; open checks that then hold: {', '.join(new_held)}" if new_held else "") + (f"; open checks that no longer hold: {', '.join(lost)}" if lost else ""))


def rows(key=KEY):
    for r in json.load(open(key))["rows"]:
        print(f"{r['id']:8} {r['mark']:12} {r['type']:34} {r['match']} {cl(r['window'][0])}-{cl(r['window'][1])} | {len(r.get('checks', []))} checks" + (" | " + r["note"] if r.get("note") else ""))


if __name__ == "__main__":
    a = sys.argv[1:]
    key = a[a.index("--key") + 1] if "--key" in a else KEY
    if a and a[0] == "score": sys.exit(1 if score(a[1], key) else 0)
    elif a and a[0] == "rows": rows(key)
    elif a and a[0] == "file": file_marks(a[1], a[2], a[3], a[a.index("--set") + 1], key)
    elif a and a[0] == "numbers": numbers(tuple(float(x) for x in a[a.index("--steps") + 1].split(",")) if "--steps" in a else (0.5, 0.75, 1.25, 2.0), tuple(a[a.index("--names") + 1].split(",")) if "--names" in a else NUMBERS, key=key)
    elif a and a[0] == "game": game(a[1], a[2])
    elif a and a[0] == "compare": compare(a[1], a[2], a[3], a[4], [x.split("=", 1) for x in a[5:]])
    elif a and a[0] == "export": export(a[1], a[2], int(a[a.index("--part") + 1]), a[a.index("--set") + 1] if "--set" in a else "f1", a[a.index("--label") + 1] if "--label" in a else None, a[a.index("--drop") + 1].split(",") if "--drop" in a else (), a[a.index("--confidence") + 1] if "--confidence" in a else None)
    elif a and a[0] == "lord": lord_rows(a[1], [x for i, x in enumerate(a[2:]) if x != "--gvg" and a[2:][i - 1] != "--gvg"], a[a.index("--gvg") + 1] if "--gvg" in a else None)
    elif a and a[0] == "lord-record": lord_record(a[1], a[2:])
    else: print(__doc__)
