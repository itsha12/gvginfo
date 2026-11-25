"""Monk casting efficiency (R-689, piece 4; R-666 the first aspect: "are monks casting in an energy-optimal manner, maximizing the healing/damage prevention
per energy spent, or are they wasting energy overhealing or using prots on targets that didn't need it"), per character, against the same monk role across
all matches (R-671). An execution measure: it needs no energy record, so it reads the 18 counted matches that have none too.

What is read, and from where (read this before changing any of it):
  whose        the backline monks, told by their bars (`common.monk_kind`, R-698). A smite monk and a healing Ritualist are not read (R-457, R-699).
  energy spent the listed cost of every cast he started from 0:00, whatever became of it (R-680: a cancelled cast still costs its energy), from the replay's
               own casts (`forensics.Forensics.casts`, the one reading of how a cast ended: finished, interrupted, hit while Dazed, cancelled).
  useful       healing that landed, Divine Favor's counted, plus damage prevented, point for point (R-678): gvg.report's figures for every skill he cast
               (the file beside the replay, `skills`: match totals, no time). Overhealing is what did not land; it is in no useful figure.
               A blocked attack is in `prevented` already: gvg.report scores every attack a skill blocked at 36 damage (found 2026-11-24: prevented is
               36 x blocks on all 4,950 rows with a block), so any blocking skill is credited with its blocks, not Aegis by name (R-687).
               No cast is marked "not needed" (R-679): a prot that prevented nothing adds its energy and no points, and that is the whole of it.
  apart        hex and condition removals, a count (R-678: the replay's own credit by skill, `outcomes`); knockdowns prevented, a count (gvg.report's
               estimate, Aura of Stability mostly). Neither is in the points.
  cancelled    his cancelled casts and their energy, shown apart (R-680), each told as a bait that worked or energy burned: a bait where gvg.report reads
               an enemy interrupt on him as missed because he cancelled (the attempts of R-639, its read "cancel"), the attempt begun inside the cast or
               within BAIT_S of its end. A cancel that scared an interrupter off without drawing the skill cannot be seen, and reads as burned.
  interrupted  the energy of the casts an interrupt took (context: it is spent too, and bought nothing).

What gvg.report's figures do not hold, to say whenever a figure is shown (found 2026-11-24, over the 564 counted matches):
  - Aegis (PvP) makes attacks on its target fail and stops hostile spells being cast on him, for 1 to 3 s: the spike save R-679 names as the exception.
    gvg.report scores almost none of it (0.02 blocks a cast, 0.6 points; Guardian 0.83 blocks a cast): an attack that fails is no block in its record and
    a spell that could not be cast leaves nothing. So Aegis reads as nearly worthless here, which it is not.
  - Protective Spirit and Aura of Stability prevent nothing in its figures (Protective Spirit caps a hit; Aura of Stability stops a knockdown), so their
    energy counts and only their Divine Favor heal comes back. Knockdowns prevented are kept apart as a count.
  - `uses` is casts started (43,210 against 43,012 in the replays of 47 matches), so the energy here and its figures cover the same casts.

What a monk is placed against (R-704, his answers of 2026-11-24):
  (a) by his bar, never his slot: `role_of` is his elite (R-698), and a bar whose elite has fewer than MIN_GROUP placed monk-games over every counted
      match is placed among "another bar" (every such bar pooled), so no monk is left unplaced for a rare elite;
  (b) beside monks whose team was hit about as hard: the thirds of `team_taken_min` (damage in hits on his team's players a minute) over every placed
      monk-game; a monk is placed within his bar and his third where that holds MIN_GROUP or more, else within his bar alone, and the sentence says which;
  (c) Aegis, Protective Spirit and Aura of Stability (APART): gvg.report credits them with almost nothing, so their energy is out of `spent` and of every
      share and figure made from it, and their casts are shown apart as counts (`apart_casts`, `apart_energy`). `spent_all` keeps every cast's energy.

    from casting import record
    record(m)                        {"monks": {agent: row}}: every backline monk's row (`row` below)
    python3 casting.py <report id>   a match's monks in sentences, each placed against the same role (the report must exist)
    python3 casting.py report [--jobs N]   every counted match: the table by role and by skill, written to data/model/casting_cases.json
    python3 casting.py cover         the checks of the record against the replays' own casts and against gvg.report's totals
"""
import collections, json, os, sys
import common
from common import REPO, backline_monk, skill_row

BENCH = os.path.join(REPO, "data", "model", "casting_cases.json")
MIN_SPENT = 100                 # a monk-game is placed, and counts in the usual of his role, only where he spent this much energy (Claude's draft: about twenty casts)
BAIT_S = 1.0                    # an interrupt attempt begun within this many seconds of the end of a cancelled cast was drawn by it (the attempts read "cancel" begin a median 0.1 s after the cast ends, 90% within 0.3 s)
CUT = (20, 80)                  # percentiles: under and over these a figure is low or high for the role (as the death accounts place a player, forensics.BENCH_CUT)
BLOCK_WORTH = 36                # gvg.report's worth of a blocked attack, in `prevented` already: a check in `cover`, never added here
SLOT_ROLE = {6: "Prot", 7: "7 Monk", 8: "8 Monk"}     # his name by slot, said in the sentence only (R-704: he is placed by his bar)
MIN_GROUP = 40                  # placed monk-games a bar (or a bar and a third) needs to be a group of its own; fewer go to "another bar" (bars) or the bar alone (thirds)
OTHER_BAR = "another bar"
APART = {"Aegis", "Aegis (PvP)", "Protective Spirit", "Protective Spirit (PvP)", "Aura of Stability"}   # R-704 c: energy out of the points, casts counted apart
MEASURES = (                    # (key, what a higher figure is: +1 better, -1 worse, 0 no direction, words)
    ("per_energy", +1, "useful points (healing landed and damage prevented) a point of energy"),
    ("over_share", -1, "share of his healing that was overhealing"),
    ("cancel_share", 0, "share of his energy spent on cancelled casts"),
    ("bait_share", +1, "share of his cancelled casts that drew an interrupt"),
    ("interrupted_share", -1, "share of his energy spent on casts an interrupt took"),
    ("removals_100", 0, "hexes and conditions removed, a 100 energy"),
    ("spent_min", 0, "energy spent a minute alive"),
)


def role_of(m, a):
    """The bar a backline monk is placed against (R-704 a): his elite, or "no elite seen". Rare bars are pooled at placing (`group_of`)."""
    return next((r["name"] for r in (skill_row(b, m.sk(b)) for b in m.A[a].get("bar") or [] if b) if r and r.get("elite")), None) or "no elite seen"


def group_of(bench, r):
    """(group, third, key) a row is placed in: his bar, or OTHER_BAR where the bench holds too few of it; and the bar and third where that holds MIN_GROUP."""
    roles = (bench or {}).get("roles") or {}
    g = r["group"] if (roles.get(r["group"]) or {}).get("games", 0) >= MIN_GROUP else OTHER_BAR
    cuts = (bench or {}).get("pressure_cuts")
    third = None if not cuts else ("hit least" if r["team_taken_min"] < cuts[0] else "the middle third" if r["team_taken_min"] < cuts[1] else "hit hardest")
    k = f"{g} | {third}"
    return g, third, (k if third and (roles.get(k) or {}).get("games", 0) >= MIN_GROUP else g)


def _cost(sid, name):
    try: return float((skill_row(sid, name) or {}).get("energy") or 0)
    except (TypeError, ValueError): return 0.0


def record(m, rid=None):
    """{"monks": {agent: row}} for every backline monk of the match. A row:
      team, role (his name), group (the role he is placed against), name, elite, won,
      alive_s            seconds alive from 0:00;  team_taken_min  damage in hits on his team's players a minute (how hard his team was hit: context)
      casts, spent       casts started from 0:00 and their listed energy;  by_end {finished | interrupted | hit while Dazed | cancelled: [casts, energy]}
      healed, over       healing landed and overhealing (Divine Favor in both);  prevented, blocks  damage prevented (blocks at 36 in it) and attacks blocked
      useful             healed + prevented;  per_energy  useful / spent (None under MIN_SPENT);  over_share  over / (healed + over)
      removals, kd_prevented   counts apart
      cancelled {n, energy, baited, burned}   his cancelled casts (R-680);  cancel_share, bait_share, interrupted_share, removals_100, spent_min
      skills             [[skill, casts started, energy, healed, over, prevented, blocks]] by energy spent, his own casts and gvg.report's figures side by side
    gvg.report's summary is in every stored match's file; a file without it stops the reading (R-460)."""
    from forensics import Forensics
    X = m.extras()
    if not X.summary: raise RuntimeError(f"casting: the file beside {rid or m.o.get('meta', {}).get('id')} holds no summary of gvg.report's, so no healing or prevention by skill (R-460)")
    monks = [a for a in m.PL if backline_monk(m, a)]
    out = {"monks": {}}
    if not monks: return out
    F = Forensics(rid or m.o["meta"].get("id"), m)
    C = collections.defaultdict(list)
    for x in F.casts():
        if x[0] in monks and x[2] >= 0: C[x[0]].append(x)
    att = collections.defaultdict(list)                                   # the interrupt attempts gvg.report reads as missed because the target cancelled, by target (seconds)
    for r in X.o.get("attempts") or []:
        if r[5] == 0 and r[6] == "cancel" and r[0] is not None: att[r[4]].append(r[0] / 10)
    taken = collections.Counter()
    for e in m.o["ev"]:
        if e[1] == "dm" and e[0] is not None and e[0] >= 0 and e[3] in m.PL and e[5]: taken[m.team(e[3])] += e[5]
    mins = max(m.o["meta"].get("match_length_s") or (m.o["ev"][-1][0] / 10), 60) / 60
    win = (m.o["meta"].get("result") or {}).get("winning_team_id")
    for a in monks:
        T = m.TR.get(str(a)) or {"t": [], "st": []}
        alive = sum(1 for t, s in zip(T["t"], T["st"]) if t >= 0 and s != "d")              # about a sample a second
        by_end, by_skill = collections.defaultdict(lambda: [0, 0.0]), collections.defaultdict(lambda: [0, 0.0, 0.0, 0.0, 0.0, 0])
        canc = {"n": 0, "energy": 0.0, "baited": 0, "burned": 0}
        used = set()
        ap = [0, 0.0]
        for _, sid, t0, t1, end, _tg in C[a]:
            c = _cost(sid, m.sk(sid))
            if m.sk(sid) in APART:                                         # R-704 c: counted apart, out of the points
                ap[0] += 1; ap[1] += c; by_skill[sid][0] += 1; by_skill[sid][1] += c
                continue
            by_end[end][0] += 1; by_end[end][1] += c
            by_skill[sid][0] += 1; by_skill[sid][1] += c
            if end == "cancelled":
                canc["n"] += 1; canc["energy"] += c
                hit = next((i for i, u in enumerate(att.get(a, ())) if i not in used and t0 <= u <= t1 + BAIT_S), None)      # each attempt is drawn by one cast only
                if hit is not None: used.add(hit); canc["baited"] += 1
                else: canc["burned"] += 1
        healed = over = prevented = 0.0; blocks = kd = 0
        for r in X.o.get("skills", {}).get(str(a), ()):
            if not str(r[0]).startswith("skill:"): continue             # the other rows are degen by condition, which is no cast of his
            if m.sk(r[1]) in APART:                                        # R-704 c: its credit is out of the points as its energy is
                s = by_skill[r[1]]; s[2] += (r[7] or 0) + (r[9] or 0); s[3] += (r[8] or 0) + (r[10] or 0); s[4] += r[11] or 0; s[5] += r[5] or 0
                kd += r[6] or 0
                continue
            h, o_ = (r[7] or 0) + (r[9] or 0), (r[8] or 0) + (r[10] or 0)
            healed += h; over += o_; prevented += r[11] or 0; blocks += r[5] or 0; kd += r[6] or 0
            s = by_skill[r[1]]; s[2] += h; s[3] += o_; s[4] += r[11] or 0; s[5] += r[5] or 0
        rem = sum((v[3] or 0) + (v[4] or 0) for v in ((m.o.get("outcomes") or {}).get(str(a)) or {}).values())
        casts, spent = sum(v[0] for v in by_end.values()), sum(v[1] for v in by_end.values())
        ok = spent >= MIN_SPENT
        out["monks"][a] = {
            "team": m.tag[m.team(a)], "role": m.roles[a], "group": role_of(m, a), "name": m.nm(a), "won": None if win not in (1, 2) else m.team(a) == win,
            "elite": next((r["name"] for r in (skill_row(b, m.sk(b)) for b in m.A[a].get("bar") or [] if b) if r and r.get("elite")), None),
            "slot_name": SLOT_ROLE.get(m.A[a].get("slot"), "Monk, another slot"),
            "alive_s": alive, "team_taken_min": round(taken[m.team(a)] / mins), "casts": casts, "spent": round(spent),
            "apart_casts": ap[0], "apart_energy": round(ap[1]), "spent_all": round(spent + ap[1]),
            "by_end": {k: [v[0], round(v[1])] for k, v in by_end.items()},
            "healed": round(healed), "over": round(over), "prevented": round(prevented), "blocks": blocks, "useful": round(healed + prevented),
            "per_energy": round((healed + prevented) / spent, 2) if ok else None, "over_share": round(over / (healed + over), 3) if healed + over > 0 else None,
            "removals": rem, "kd_prevented": kd, "cancelled": {k: (round(v) if k == "energy" else v) for k, v in canc.items()},
            "cancel_share": round(canc["energy"] / spent, 3) if ok else None, "bait_share": round(canc["baited"] / canc["n"], 3) if canc["n"] else None,
            "interrupted_share": round(by_end["interrupted"][1] / spent, 3) if ok else None, "removals_100": round(100 * rem / spent, 2) if ok else None,
            "spent_min": round(60 * spent / alive, 1) if alive >= 60 else None,
            "skills": sorted(([m.sk(k), v[0], round(v[1]), round(v[2]), round(v[3]), round(v[4]), v[5]] for k, v in by_skill.items()), key=lambda r: -r[2]),
        }
    return out


def _pct(v, p):
    v = sorted(v)
    if not v: return None
    i = p / 100 * (len(v) - 1); lo = int(i)
    return v[lo] + (v[min(lo + 1, len(v) - 1)] - v[lo]) * (i - lo)


def place(bench, r, key):
    """low, usual or high among the monks he is placed against (`group_of`: his bar, and his team's third of how hard it was hit where that group is
    large enough), under the 20th percentile or over the 80th; with the band and the group's words. None where there is no usual (under 20 monk-games)."""
    g, third, k = group_of(bench, r)
    b = (((bench or {}).get("roles") or {}).get(k) or {}).get(key)
    x = r.get(key)
    if x is None or not b or b["n"] < 20: return None
    words = f"monks on {g}" + ({"hit least": " whose team was among the third hit least", "the middle third": " whose team was hit about as hard (the middle third)",
                                "hit hardest": " whose team was among the third hit hardest"}[third] if k != g else " (too few of them hit as hard as his team to place him by that too)")
    return ("low" if x < b["p20"] else "high" if x > b["p80"] else "usual"), b, words


def say(r, bench=None):
    """A monk's row in sentences (R-329: nothing in shorthand)."""
    def placed(key, fmt):
        p = place(bench or {}, r, key)
        return "" if not p else f" ({p[0]} among {p[2]}: three in five of them lie between {fmt(p[1]['p20'])} and {fmt(p[1]['p80'])})"
    f2, pc = (lambda x: f"{x:.1f}"), (lambda x: f"{100 * x:.0f}%")
    s = [f"{r['team']} {r['role']} ({r['name']}, {r['elite'] or 'no elite seen'}): {r['casts']} casts started for {r['spent']} energy."]
    if r.get("apart_casts"): s[0] += (f" Apart, {r['apart_casts']} casts of Aegis, Protective Spirit or Aura of Stability for {r['apart_energy']} energy, out of every figure"
                                      f" below: gvg.report credits them with almost nothing (R-704).")
    if r["per_energy"] is None: return s[0] + f" Under {MIN_SPENT} energy spent: not placed."
    s.append(f"{r['healed']:,} healing landed and {r['prevented']:,} damage prevented ({r['blocks']} attacks blocked, at {BLOCK_WORTH} each, among it): "
             f"{f2(r['per_energy'])} useful points a point of energy{placed('per_energy', f2)}.")
    if r["over_share"] is not None: s.append(f"{pc(r['over_share'])} of his healing was overhealing ({r['over']:,}){placed('over_share', pc)}.")
    s.append(f"Apart: {r['removals']} hexes and conditions removed, {r['kd_prevented']} knockdowns prevented.")
    c = r["cancelled"]
    s.append((f"{c['n']} casts cancelled, {c['energy']} energy ({pc(r['cancel_share'])} of what he spent{placed('cancel_share', pc)}): {c['baited']} drew an enemy interrupt, "
              f"{c['burned']} did not (energy burned, or an interrupter scared off unseen).") if c["n"] else "No cast cancelled.")
    i = r["by_end"].get("interrupted")
    if i: s.append(f"{i[0]} casts interrupted, {i[1]} energy ({pc(r['interrupted_share'])}{placed('interrupted_share', pc)}).")
    return " ".join(s)


def _one(rid):
    from replaylib import Match
    try:
        m = Match.from_branch(rid)
        return rid, {str(a): r for a, r in record(m, rid)["monks"].items()}, None
    except Exception as e:      # said, never hidden (R-460): the report counts the matches that failed and stops on any
        return rid, None, f"{type(e).__name__}: {e}"


def _rows(jobs=2):
    import multiprocessing
    ids = sorted(common.replay_ids())
    with multiprocessing.Pool(jobs) as pool: res = pool.map(_one, ids, chunksize=8)
    bad = [(rid, e) for rid, r, e in res if e]
    if bad: raise RuntimeError(f"casting: {len(bad)} of {len(ids)} matches could not be read (R-460): {bad[:3]}")
    return {rid: r for rid, r, _ in res}


def report(jobs=2, out=BENCH):
    """Every counted match: the usual of each role (the 20th, 50th and 80th percentile of every measure over the monk-games with MIN_SPENT energy or more),
    the same by how hard the monk's team was hit, by skill, and winners beside losers. Written to data/model/casting_cases.json; prints the tables."""
    M = _rows(jobs)
    R = [dict(r, rid=rid) for rid, rows in M.items() for r in rows.values()]
    ok = [r for r in R if r["per_energy"] is not None]
    pr = print
    res = {"matches": len(M), "monk_games": len(R), "placed": len(ok), "min_spent": MIN_SPENT, "cut": CUT, "roles": {}, "pressure": {}, "skills": {}, "won": {}}
    pr(f"Monk casting efficiency (R-666, R-678 to R-680, R-687; R-671): {len(M)} counted matches, {len(R)} backline monk-games, {len(ok)} with {MIN_SPENT} energy spent or more.")
    pr("Useful points are healing that landed (Divine Favor counted) and damage prevented (an attack blocked is 36 in it, gvg.report's worth), for the listed")
    pr("energy of every cast started. Figures are gvg.report's estimates. Aegis, Protective Spirit and Aura of Stability, which it credits with almost nothing,")
    pr("are out of every figure and counted apart (R-704 c).")
    def band(rows, key):
        v = [r[key] for r in rows if r.get(key) is not None]
        return None if not v else {"n": len(v), "p20": round(_pct(v, CUT[0]), 3), "p50": round(_pct(v, 50), 3), "p80": round(_pct(v, CUT[1]), 3)}
    def table(title, groups, store):
        pr(f"\n{title}")
        pr(f"   {'':30} {'games':>6} " + " ".join(f"{k:>22}" for k, _, _ in MEASURES))
        for g, rows in groups:
            if not rows: continue
            store[g] = {k: band(rows, k) for k, _, _ in MEASURES}; store[g]["games"] = len(rows)
            def cell(k):
                b = store[g][k]
                if not b: return f"{'':>22}"
                f = (lambda x: f"{100 * x:.0f}%") if k.endswith("share") else (lambda x: f"{x:.1f}")
                return f"{f(b['p50']) + ' (' + f(b['p20']) + ' to ' + f(b['p80']) + ')':>22}"
            pr(f"   {g:30} {len(rows):6} " + " ".join(cell(k) for k, _, _ in MEASURES))
    t3 = [_pct([r["team_taken_min"] for r in ok], p) for p in (33.3, 66.7)]
    res["pressure_cuts"] = [round(x) for x in t3]
    gn = collections.Counter(r["group"] for r in ok)
    bars = [g for g, n in gn.most_common() if n >= MIN_GROUP]
    of_bar = lambda r: r["group"] if r["group"] in bars else OTHER_BAR
    thirds = ("hit least", "the middle third", "hit hardest")
    third_of = lambda r: thirds[0] if r["team_taken_min"] < t3[0] else thirds[1] if r["team_taken_min"] < t3[1] else thirds[2]
    table(f"A. By bar, his elite (R-704 a; bars with fewer than {MIN_GROUP} placed monk-games pooled as '{OTHER_BAR}'): the middle monk-game, and the band three in five lie in",
          [(g, [r for r in ok if of_bar(r) == g]) for g in bars + [OTHER_BAR]] + [("every backline monk", ok)], res["roles"])
    table(f"A2. By bar and how hard his team was hit (R-704 b; thirds at {t3[0]:.0f} and {t3[1]:.0f} damage in hits a minute): what a monk is placed against where the group holds {MIN_GROUP}",
          [(f"{g} | {t}", [r for r in ok if of_bar(r) == g and third_of(r) == t]) for g in bars + [OTHER_BAR] for t in thirds], res["roles"])
    for k in [k for k, v in res["roles"].items() if " | " in k and v["games"] < MIN_GROUP]: del res["roles"][k]
    sn = ["Prot", "7 Monk", "8 Monk", "Monk, another slot"]
    table("B. By his name by slot (said only, never placed by it: R-704 a)", [(g, [r for r in ok if r.get("slot_name") == g]) for g in sn], res.setdefault("slots", {}))
    table(f"C. By how hard his team was hit (damage in hits on its players a minute; thirds at {t3[0]:.0f} and {t3[1]:.0f}): a team hit harder gives its monks more to heal",
          [("hit least", [r for r in ok if r["team_taken_min"] < t3[0]]), ("the middle third", [r for r in ok if t3[0] <= r["team_taken_min"] < t3[1]]), ("hit hardest", [r for r in ok if r["team_taken_min"] >= t3[1]])], res["pressure"])
    table("D. Winners beside losers (no cause is read from it: the losing side is hit harder and heals more)", [("won", [r for r in ok if r["won"]]), ("lost", [r for r in ok if r["won"] is False])], res["won"])
    S = collections.defaultdict(lambda: [0, 0, 0.0, 0.0, 0.0, 0.0, 0])            # skill: monk-games, casts, energy, healed, over, prevented, blocks
    for r in R:
        for nm, n, e, h, o_, p, b in r["skills"]:
            s = S[nm]; s[0] += 1; s[1] += n; s[2] += e; s[3] += h; s[4] += o_; s[5] += p; s[6] += b
    pr("\nE. By skill, over every backline monk-game (energy is the listed cost of the casts started; a signet costs none)")
    pr(f"   {'skill':28} {'games':>6} {'casts':>7} {'energy':>8} {'healed':>9} {'overheal':>9} {'prevented':>10} {'blocks':>7} {'useful a point':>14} {'overheal share':>14}")
    for nm, s in sorted(S.items(), key=lambda kv: -kv[1][2]):
        if s[1] < 200: continue
        res["skills"][nm] = {"games": s[0], "casts": s[1], "energy": round(s[2]), "healed": round(s[3]), "over": round(s[4]), "prevented": round(s[5]), "blocks": s[6],
                             "per_energy": round((s[3] + s[5]) / s[2], 2) if s[2] else None, "over_share": round(s[4] / (s[3] + s[4]), 3) if s[3] + s[4] else None}
        k = res["skills"][nm]
        pr(f"   {nm[:28]:28} {s[0]:6} {s[1]:7} {s[2]:8.0f} {s[3]:9.0f} {s[4]:9.0f} {s[5]:10.0f} {s[6]:7} {('%.1f' % k['per_energy']) if k['per_energy'] is not None else '':>14} {('%.0f%%' % (100 * k['over_share'])) if k['over_share'] is not None else '':>14}")
    cn = [r["cancelled"] for r in R]
    res["cancelled"] = {"casts": sum(c["n"] for c in cn), "energy": sum(c["energy"] for c in cn), "baited": sum(c["baited"] for c in cn), "burned": sum(c["burned"] for c in cn),
                        "share_of_energy": round(sum(c["energy"] for c in cn) / max(sum(r["spent"] for r in R), 1), 4)}
    c = res["cancelled"]
    pr(f"\nF. Cancelled casts (R-680): {c['casts']:,} in all, {c['energy']:,} energy, {100 * c['share_of_energy']:.1f}% of what the monks spent; {c['baited']:,} drew an enemy interrupt "
       f"({100 * c['baited'] / max(c['casts'], 1):.0f}%), {c['burned']:,} did not.")
    ie = sum((r["by_end"].get("interrupted") or [0, 0])[1] for r in R)
    res["interrupted_share_of_energy"] = round(ie / max(sum(r["spent"] for r in R), 1), 4)
    pr(f"   Casts an interrupt took: {100 * res['interrupted_share_of_energy']:.1f}% of the energy spent.")
    res["apart"] = {"casts": sum(r.get("apart_casts", 0) for r in R), "energy": sum(r.get("apart_energy", 0) for r in R),
                    "share_of_energy": round(sum(r.get("apart_energy", 0) for r in R) / max(sum(r.get("spent_all", r["spent"]) for r in R), 1), 4)}
    pr(f"   Counted apart (R-704 c): {res['apart']['casts']:,} casts of Aegis, Protective Spirit and Aura of Stability, {res['apart']['energy']:,} energy, "
       f"{100 * res['apart']['share_of_energy']:.1f}% of all the monks spent.")
    res["rows"] = {rid: rows for rid, rows in M.items()}
    if out:
        with open(out, "w") as fh: json.dump(res, fh, ensure_ascii=False, separators=(",", ":"))
        pr(f"\nwritten: {os.path.relpath(out, REPO)}")
    return res


def cover(jobs=2):
    """The checks of the record (R-460): do gvg.report's casts and ours cover the same casts, is a block 36 in every row, and how the cancelled casts read."""
    import multiprocessing
    ids = sorted(common.replay_ids())
    with multiprocessing.Pool(jobs) as pool: res = pool.map(_check, ids, chunksize=8)
    t = collections.Counter()
    for c in res: t.update(c)
    print(f"{len(ids)} counted matches, {t['monks']} backline monk-games.")
    print(f"  casts started, the replays' own: {t['ours']:,}; gvg.report's uses of the same skills: {t['theirs']:,} ({100 * t['theirs'] / max(t['ours'], 1):.1f}%).")
    print(f"  rows with a block: {t['block_rows']:,}; prevented is {BLOCK_WORTH} a block and no more in {t['block_36']:,} of them (the others hold a reduction too).")
    print(f"  interrupt attempts gvg.report reads as missed on a cancel, on these monks: {t['cancel_attempts']:,}; matched to a cancelled cast of his in the replay: {t['matched']:,}.")


def _check(rid):
    from replaylib import Match
    m = Match.from_branch(rid); R = record(m, rid)["monks"]; X = m.extras().o
    t = collections.Counter(monks=len(R))
    for a, r in R.items():
        t["ours"] += r["casts"]; t["matched"] += r["cancelled"]["baited"]
        for row in X.get("skills", {}).get(str(a), ()):
            if not str(row[0]).startswith("skill:"): continue
            t["theirs"] += row[4] or 0
            if row[5]: t["block_rows"] += 1; t["block_36"] += int(abs((row[11] or 0) - BLOCK_WORTH * row[5]) < 1)
        t["cancel_attempts"] += sum(1 for x in X.get("attempts") or [] if x[4] == a and x[5] == 0 and x[6] == "cancel")
    return t


if __name__ == "__main__":
    a = sys.argv[1:]
    jobs = int(a[a.index("--jobs") + 1]) if "--jobs" in a else 2
    if not a: print(__doc__)
    elif a[0] == "report": report(jobs)
    elif a[0] == "cover": cover(jobs)
    else:
        from replaylib import Match
        rid = next((r for r in sorted(common.replay_ids()) if r.startswith(a[0])), a[0])
        m = Match.from_branch(rid)
        bench = json.load(open(BENCH)) if os.path.exists(BENCH) else {}
        if not bench: print("(no data/model/casting_cases.json yet: run `python3 casting.py report`; the monks are not placed)")
        for _, r in sorted(record(m, rid)["monks"].items(), key=lambda kv: (kv[1]["team"], kv[1]["role"])): print(say(r, bench), "\n")
