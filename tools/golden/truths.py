#!/usr/bin/env python3
"""The known truths (R-533): a sanity check of the reading on obvious things.

A decision card shows one moment; an error that shifts every row a little looks fine on each card. So beside the
review key (his marks, row by row) there is this: a short list of things any GvG player knows to be true, each asked
of every counted match at once. An undefended split takes more NPCs than a defended one; the side up on numbers kills
more than it loses; a team that answers a run with a run is better off in flags than one that stays. If the engine's
plays do not show one of them, the reading, the window it is measured over, or the way the question is put is wrong
somewhere, and that is looked into before anything is built on those plays.

Rules (his, 2026-11-18):
  - A truth that fails is a reason to look, never proof of an error by itself: the cause may be a misreading, a window
    that differs between the two sides of the comparison (a stay row ends at their cap, a run row at ours: compare at
    the fixed 90 s record), or teams choosing differently by situation.
  - The truths are tests only. Nothing here feeds the engine's values, its similar cases or its advice.
  - Only near-certain truths go on the list. Contested wisdom (heal an archer over a knight) is a question for the
    data, never a truth. A truth is his, or Claude's once he has approved it; Claude's proposals not yet approved are
    reported apart and never fail the run. Ids are never used again: T5, T6, T11 and P6 were taken off on 2026-11-18,
    and P1 to P5 are approved under the ids they were proposed with.

Each truth compares two groups of plays on one measure, says which should be higher, and is given a 90% range by
drawing whole matches again 400 times (plays of one match are not independent). HOLDS: the range lies wholly on the
expected side. FAILS: wholly on the other side (the run exits 1 when an approved truth fails). NOT CLEAR: the range
includes no difference. TOO FEW: under 30 plays, or under 15 matches, in a group.

Usage:  python3 tools/golden/truths.py <plays file from `moments.py all <file>`> [--json <out.json>]
Run it at every checkpoint (a run over every match). On the development set most truths are too few to call.
A reading tool: it is in no cache key."""
import collections, json, random, sys

MIN_PLAYS, MIN_MATCHES, DRAWS = 30, 15, 400
ms = lambda p: max(p["t1"] - p["t0"], 1) / 60.0
att = lambda P: [p for p in P if p["play"] == "split" and p["side"] == "attacker" and not p.get("change") and "size" in p]
n1 = lambda xs: 1


def _splits_defended(D):
    for p in att(D["plays"]):
        yield ("undefended" if p["defenders"] == 0 else "defended"), p["rid"], len(p["beside"].get("npcs_taken", [])), ms(p)


def _numbers_kills(D):
    for p in D["plays"]:
        if p["play"] == "numbers" and p.get("numbers_side") == "up":
            m = max(p["beside"].get("lasted_s", 0), 1) / 60.0
            yield "kills", p["rid"], p["beside"]["deaths"][1], m
            yield "losses", p["rid"], p["beside"]["deaths"][0], m


def _numbers_margin(D):
    for p in D["plays"]:
        if p["play"] == "numbers" and p.get("numbers_side") == "up" and "numbers" in p:
            a, b = (int(x) for x in p["numbers"].split("v"))
            yield ("up by two or more" if abs(a - b) >= 2 else "up by one"), p["rid"], p["beside"]["deaths"][1], max(p["beside"].get("lasted_s", 0), 1) / 60.0


def _numbers_length(D):
    for p in D["plays"]:
        if p["play"] == "numbers" and p.get("numbers_side") == "up":
            s = p["beside"].get("lasted_s", 0)
            if s >= 30 or s < 15: yield ("30 s or longer" if s >= 30 else "under 15 s"), p["rid"], int(p["beside"]["deaths"][1] > 0), 1


def _push_size(D):
    for p in D["plays"]:
        if p["play"] == "push flagger" and not p.get("soh") and (p.get("main") or p.get("pushers") == 1):
            yield ("the main team" if p.get("main") else "one player"), p["rid"], int(bool(p["any_of"].get("their flag is stopped"))), 1


def _push_late(D):
    for p in D["plays"]:
        if p["play"] == "push flagger" and not p.get("soh") and p["beside"].get("against_usual"):
            yield "a pushed flag that still caps", p["rid"], p["beside"]["against_usual"], 1
            yield "the usual run", p["rid"], 1, 1


def _carrier_died(D):
    for p in D["plays"]:
        if p["play"] == "push flagger" and not p.get("soh") and p["beside"].get("flag") in ("captured", "returned", "put down"):
            yield ("the carrier lives" if not p["beside"].get("carrier_died") else "the carrier dies"), p["rid"], int(p["beside"]["flag"] == "captured"), 1


def _pinned(D):
    for p in D["plays"]:
        if p["play"] == "pinned":
            s = p["beside"].get("pinned_s", 0)
            if s >= 60 or s < 30: yield ("held 60 s or longer" if s >= 60 else "held under 30 s"), p["rid"], int(p["beside"].get("pit_npcs_lost", 0) > 0), 1


def _flag_answer(D):
    """Their single run, answered by a single run or a stay: the change in flag lead at the fixed 90 s record (never at the
    play's own end: a stay row ends when their flag is in, a run row when ours is), within the same start: behind, level
    or ahead on flags. The three starts are three strata; the difference is their plain mean."""
    R = {r["id"]: r for r in D["records"]}
    for p in D["plays"]:
        if p["play"] != "flag" or p.get("soh") or p.get("their") != "single run" or p.get("ours") not in ("single run", "stay"): continue
        r = R.get(p.get("moment"))
        if not r or r["state"].get("flag_lead") is None or not r["after"].get("90") or r["after"]["90"].get("lead_change") is None: continue
        L = r["state"]["flag_lead"]; band = "behind" if L < -0.35 else "ahead" if L >= 0.35 else "level"
        yield ("a single run in answer" if p["ours"] == "single run" else "a stay"), p["rid"], r["after"]["90"]["lead_change"], 1, band


def _wipe(D):
    for r in D["records"]:
        a, b = r["after"].get("90"), r["after"].get("180")
        if not a or not b or r["state"]["alive"][0] < 7: continue
        d = a["deaths"][0]
        if d >= 6 or d <= 2: yield ("six or more of its players die within 90 s" if d >= 6 else "two or fewer die"), r["rid"], int(b["npcs"][0] > 0), 1


def _collapse_or_mirror(D):
    for p in att(D["plays"]):
        a = p.get("answer")
        if a in ("collapsed on", "met by a full collapse", "even"):
            yield ("collapsed on" if a != "even" else "mirrored"), p["rid"], int(bool(p["beside"].get("lost"))), 1


def _split_up_down(D):
    for p in att(D["plays"]):
        if p["defenders"] and p["defenders"] != p["size"]:
            yield ("more split players than defenders" if p["size"] > p["defenders"] else "more defenders than split players"), p["rid"], int(bool(p["beside"].get("kills"))), 1


def _split_damage(D):
    for p in att(D["plays"]):
        if p["defenders"] == 0 and p.get("split_damage"):
            yield ("two or more damage players" if p["split_damage"] >= 2 else "one damage player"), p["rid"], len(p["beside"].get("npcs_taken", [])), ms(p)


# id, whose, approved, the truth in his words, the measure, the group expected higher, the other group, rows
TRUTHS = [
    ("T1", "Denning", True, "An undefended split takes more NPCs than a defended one.", "NPCs taken a minute", "undefended", "defended", _splits_defended),
    ("T2", "Claude, approved", True, "The side up on numbers at the main fight kills more than it loses.", "deaths a minute while the numbers last", "kills", "losses", _numbers_kills),
    ("T3", "Claude, approved", True, "A main team pushing a flagger stops the flag more often than one player does.", "share of pushes that stop the flag", "the main team", "one player", _push_size),
    ("T4", "Claude, approved", True, "The longer a team is held in its base, the more often it loses a pit NPC.", "share that lose a pit NPC", "held 60 s or longer", "held under 30 s", _pinned),
    ("T7", "Claude, approved", True, "Answering their run with a run leaves a team better off in flags than staying (same start: behind, level or ahead).", "change in flag lead 90 s on, in flags", "a single run in answer", "a stay", _flag_answer),
    ("T8", "Claude, approved", True, "A team that wipes loses NPCs.", "share that lose an NPC within 3 minutes", "six or more of its players die within 90 s", "two or fewer die", _wipe),
    ("T9", "Claude, approved", True, "A flag whose carrier dies under a push gets in less often than one whose carrier lives.", "share of pushed flags that are capped", "the carrier lives", "the carrier dies", _carrier_died),
    ("T10", "Claude, approved", True, "A split that is collapsed on loses a player more often than one that is mirrored.", "share of split phases that lose a split player", "collapsed on", "mirrored", _collapse_or_mirror),
    ("P1", "Claude, approved", True, "A split with more players than defenders kills a defender more often than one with fewer.", "share of split phases that kill a defender", "more split players than defenders", "more defenders than split players", _split_up_down),
    ("P2", "Claude, approved", True, "An undefended split of two or more damage players takes NPCs faster than a solo one.", "NPCs taken a minute", "two or more damage players", "one damage player", _split_damage),
    ("P3", "Claude, approved", True, "Up by two or more at the main fight kills faster than up by one.", "kills a minute while the numbers last", "up by two or more", "up by one", _numbers_margin),
    ("P4", "Claude, approved", True, "The longer a numbers advantage lasts, the more often it gets a kill.", "share with a kill", "30 s or longer", "under 15 s", _numbers_length),
    ("P5", "Claude, approved", True, "A flag that is pushed and still caps arrives later than the usual run for that hall and side.", "arrival against the usual run (1 = on time)", "a pushed flag that still caps", "the usual run", _push_late),
]


# What looking into a truth found (the date, what was measured, what it means): printed under the truth every run, so that a
# truth that does not hold is never read without its reason. Replace a note when the plays change what it says.
NOTES = {}

# Taken off the list by him on 2026-11-18 (R-533, amended): "a runner denies the boost; conceding does not" (true by how the
# two are told apart), "staying through a base res costs more deaths than leaving" (75 rows of leaving: not clear), and his own
# "a solo split defended by a monk dies less often than one defended by a damage player" (not clear: 18% against 15% of
# phases; the pit NPCs do the killing where a monk holds him, and a main team collapse that killed at once was left with
# the 1 v 1: his marks on QenK v Fun 6:37 and NwAy v ohno 5:24, in the review key). Not added: "staying through a base res
# outnumbered costs deaths more often than staying with the numbers".


def measure(rows, hi, lo, rng):
    """rows: (group, match, numerator, denominator[, stratum]). The value of a group is sum of numerators over sum of
    denominators (within a stratum; strata are averaged). Returns the two values, the counts, the difference and its 90% range."""
    S = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0, 0.0]))      # (stratum, group) -> match -> [num, den]
    cnt, mat = collections.Counter(), collections.defaultdict(set)
    for r in rows:
        g, rid, n, dn = r[:4]; st = r[4] if len(r) > 4 else ""
        c = S[(st, g)][rid]; c[0] += n; c[1] += dn; cnt[g] += 1; mat[g].add(rid)
    strata = sorted({st for st, _ in S})
    def val(g, w=None):
        vs = []
        for st in strata:
            n = d = 0.0
            for rid, (a, b) in S[(st, g)].items():
                k = 1 if w is None else w.get(rid, 0)
                n += a * k; d += b * k
            if d: vs.append(n / d)
        return sum(vs) / len(vs) if vs else None
    out = {"hi": val(hi), "lo": val(lo), "n": [cnt[hi], cnt[lo]], "matches": [len(mat[hi]), len(mat[lo])]}
    if min(out["n"]) < MIN_PLAYS or min(out["matches"]) < MIN_MATCHES or out["hi"] is None or out["lo"] is None:
        return dict(out, verdict="TOO FEW")
    rids = sorted(mat[hi] | mat[lo]); diffs = []
    for _ in range(DRAWS):
        w = collections.Counter(rng.choice(rids) for _ in rids)
        a, b = val(hi, w), val(lo, w)
        if a is not None and b is not None: diffs.append(a - b)
    diffs.sort(); a, b = diffs[int(0.05 * len(diffs))], diffs[int(0.95 * len(diffs)) - 1]
    return dict(out, diff=out["hi"] - out["lo"], range=[a, b], verdict="HOLDS" if a > 0 else "FAILS" if b < 0 else "NOT CLEAR")


def run(path, out=None):
    D = json.load(open(path)); rng = random.Random(533); res, failed = [], 0
    n = len(D["matches"])
    print(f"The known truths (R-533), on {n} matches, {len(D['plays'])} plays" + ("" if n >= 300 else "  [not a run over every match: most truths will be too few to call]"))
    f = lambda v, share: (f"{100 * v:.0f}%" if share else f"{v:.2f}")
    for block, title in ((True, "Truths (a FAILS here stops the run: look before building on these plays)"), (False, "Claude's proposals, his to approve (reported, never failing)")):
        print("\n" + title)
        for tid, by, ok, words, what, hi, lo, fn in TRUTHS:
            if ok != block: continue
            m = measure(list(fn(D)), hi, lo, rng); share = what.startswith("share")
            res.append({"id": tid, "by": by, "approved": ok, "truth": words, "measure": what, "higher": hi, "lower": lo, **m, **({"note": NOTES[tid]} if tid in NOTES else {})})
            failed += ok and m["verdict"] == "FAILS"
            print(f"  {m['verdict']:9} {tid:3} [{by}] {words}")
            if m["hi"] is None or m["lo"] is None: print(f"            {what}: no plays in one group ({hi}: {m['n'][0]}; {lo}: {m['n'][1]})"); continue
            line = f"            {what}: {hi} {f(m['hi'], share)} ({m['n'][0]:,} in {m['matches'][0]} matches); {lo} {f(m['lo'], share)} ({m['n'][1]:,} in {m['matches'][1]})"
            if "diff" in m: line += f"; difference {'+' if m['diff'] >= 0 else ''}{f(m['diff'], share)} (90% range {f(m['range'][0], share)} to {f(m['range'][1], share)})"
            print(line)
            if tid in NOTES: print(f"            note: {NOTES[tid]}")
    c = collections.Counter(r["verdict"] for r in res if r["approved"])
    print(f"\nApproved truths: {c['HOLDS']} hold, {c['FAILS']} fail, {c['NOT CLEAR']} not clear, {c['TOO FEW']} too few to call.")
    if out: json.dump({"matches": n, "truths": res}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return failed


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"): print(__doc__); sys.exit()
    sys.exit(1 if run(a[0], a[a.index("--json") + 1] if "--json" in a else None) else 0)
