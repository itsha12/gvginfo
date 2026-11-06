"""Detailed learnings snapshot (Denning: after each batch, a snapshot across all learnings, favouring the detailed
ones: skills cast, run times, runners...). Descriptive measurements from every trained match, with the latest batch
shown beside all matches so changes are visible. Not causal on their own: they feed questions and candidate variables.

Sections:
- runners: per runner (role): runs, share captured, median spawn-to-capture time, drops, pushed; double running.
- flag answers: cap delay and seconds slower than possible, winners against losers.
- skills: per skill cast at an enemy, how often that enemy died within 5 s of the cast (kill participation), with casts;
  the skills interrupted most (whose and which), and the interrupt skills that landed most; knockdown skills.
- spikes survived: spikes (400+ in 3 s) and how many the target survived, by role, winners against losers.
- monks: casts per minute, fakes, time idle while an ally was hurt, reaction to bursts; winners against losers.
- deaths: damage kinds, interrupts on monks just before a death (which skills), knockdowns on the victim.

Usage:  python3 snapshot.py [--src /tmp/gl]      prints the snapshot (markdown); learning.py adds it to the report
In code: snapshot(ids, new_ids, src) -> list of markdown lines."""
import collections, json, os, statistics, sys

MIN_N = 15          # casts (or cases) behind a skill or role before it is listed


def _lib(src, kind, ids):
    p = os.path.join(src, kind + ".jsonl")
    if not os.path.exists(p): return []
    return [r for r in (json.loads(l) for l in open(p)) if r["match"] in ids]


def _med(xs): return round(statistics.median(xs), 1) if xs else None


def runners(src, ids):
    R = _lib(src, "flag_runs", ids)
    by = collections.defaultdict(list)
    for r in R: by[r["runner"]].append(r)
    rows = []
    for role, L in by.items():
        cap = [r for r in L if r["outcome"] == "captured"]
        rows.append({"runner": role, "runs": len(L), "captured": round(len(cap) / len(L), 2),
                     "median_s_captured": _med([r["secs"] for r in cap]), "dropped": sum(1 for r in L if r["outcome"] == "dropped"),
                     "pushed": round(sum(1 for r in L if r["pushers"]) / len(L), 2), "winners_share": round(sum(r["won"] for r in L) / len(L), 2)})
    dbl = collections.Counter((r["double"] or "single", r["won"]) for r in R)
    return sorted(rows, key=lambda x: -x["runs"]), dbl


def flag_answers(src, ids):
    C = [c for c in _lib(src, "flag_cycles", ids) if c.get("slower_than_possible_s") is not None]
    out = {}
    for w in (True, False):
        L = [c for c in C if c["won"] == w]
        out["winners" if w else "losers"] = {"answers": len(L), "median_cap_delay": _med([c["cap_delay"] for c in L]),
                                             "median_slower_than_possible": _med([c["slower_than_possible_s"] for c in L]),
                                             "30s+_slower": sum(1 for c in L if c["slower_than_possible_s"] >= 30)}
    return out


def skills(ids):
    """From the replays: kill participation per skill, interrupts and knockdowns."""
    from replaylib import Match
    land = collections.defaultdict(lambda: [0, 0])           # skill -> [landed on an enemy, enemy died within 5 s]
    intr_on = collections.Counter(); intr_by = collections.Counter(); kd_by = collections.Counter()
    for rid in ids:
        m = Match.from_branch(rid)
        deaths = collections.defaultdict(list)
        for e in m.o["ev"]:
            if e[1] == "dt" and e[2] in m.PL: deaths[e[2]].append(e[0] / 10)
        seen = set()
        for e in m.o["ev"]:
            if e[1] != "cs" or e[2] not in m.PL or e[3] not in m.PL or m.team(e[2]) == m.team(e[3]) or e[4] is None: continue
            key = (e[0], e[2], e[3], e[4])
            if key in seen: continue
            seen.add(key)
            t = e[0] / 10; name = m.sk(e[4])
            land[name][0] += 1
            if any(t <= d <= t + 5 for d in deaths[e[3]]): land[name][1] += 1
        for i in m.o.get("interrupts", []):
            if i[4] is not None and i[3] in m.PL: intr_on[(m.roles[i[3]].rstrip(" 0123456789"), m.sk(i[4]))] += 1
            if i[2] is not None: intr_by[m.sk(i[2])] += 1
        for k in m.o.get("knockdowns", []):
            if k[3] is not None: kd_by[m.sk(k[3])] += 1
    kp = sorted(((n, c, round(k / c, 2)) for n, (c, k) in land.items() if c >= MIN_N), key=lambda x: -x[2])
    return kp, intr_on, intr_by, kd_by


def saves(ids):
    """Spikes (400+ damage within 3 s on one player) and whether the target survived the next 5 s; one spike per
    target per 6 s. By the target's role and for winners against losers."""
    from replaylib import Match
    by = collections.defaultdict(lambda: [0, 0]); wl = collections.defaultdict(lambda: [0, 0])
    for rid in ids:
        m = Match.from_branch(rid); win = (m.o["meta"].get("result") or {}).get("winning_team_id")
        hits = collections.defaultdict(list); deaths = collections.defaultdict(list)
        for e in m.o["ev"]:
            if e[1] == "dm" and e[3] in m.PL and e[2] in m.PL and m.team(e[2]) != m.team(e[3]) and (e[5] or 0) > 0: hits[e[3]].append((e[0] / 10, e[5]))
            if e[1] == "dt" and e[2] in m.PL: deaths[e[2]].append(e[0] / 10)
        for a, L in hits.items():
            last = -99
            for i, (t, _) in enumerate(L):
                if t - last < 6 or sum(v for tt, v in L[i:] if tt <= t + 3) < 400: continue
                last = t; ok = not any(t <= d <= t + 8 for d in deaths[a])
                role = m.roles[a].rstrip(" 0123456789")
                by[role][0] += 1; by[role][1] += int(ok)
                k = "winners" if m.team(a) == win else "losers"; wl[k][0] += 1; wl[k][1] += int(ok)
    return by, wl


def monks(src, ids):
    M = _lib(src, "monks", ids)
    out = {}
    for w in (True, False):
        L = [r for r in M if r["won"] == w and r["alive_s"] >= 60]
        out["winners" if w else "losers"] = {"monk_phases": len(L), "casts_per_min": _med([r["casts_per_min"] for r in L]),
            "fakes_per_phase": round(sum(r["fakes"] for r in L) / max(len(L), 1), 2),
            "idle_while_ally_hurt_s": _med([r["idle_while_ally_hurt_s"] for r in L]),
            "median_reaction_s": _med([r["median_reaction"] for r in L if r.get("median_reaction") is not None]),
            "bursts_answered": round(sum(r["answered"] for r in L) / max(sum(r["bursts_in_range"] for r in L), 1), 2)}
    return out


def deaths(src, ids):
    D = _lib(src, "deaths", ids)
    kinds = collections.Counter(); intr = collections.Counter(); kd = 0; prot5 = 0
    for d in D:
        for k, v in (d.get("damage_kind") or {}).items(): kinds[k] += v
        for x in d.get("interrupts_on_monks") or []:
            if x[0] >= -6: intr[x[2]] += 1
        kd += bool(d.get("knockdowns"))
        prot5 += any(x[0] >= -5 for x in d.get("monk_casts_on_victim") or [])
    return {"deaths": len(D), "with_a_knockdown": kd, "monk_cast_on_victim_last_5s": prot5,
            "damage_kinds": dict(kinds.most_common(6)), "monk_skills_interrupted_6s_before": intr.most_common(8)}


def snapshot(ids, new_ids, src="/tmp/gl"):
    L = ["## 9. Detailed learnings snapshot", "",
         f"Descriptive measurements across all {len(ids)} trained matches (the latest batch, {len(new_ids)} matches, in "
         "brackets where it differs). Not causal on their own: they point to questions and candidate variables.", ""]
    rr, dbl = runners(src, ids); rn, _ = runners(src, new_ids)
    rn = {r["runner"]: r for r in rn}
    L += ["**Runners** (spawn to capture; pushed = an enemy hit the carrier):", "",
          "| Runner | Runs | Captured | Median s to capture | Dropped | Pushed | Runs by winners |", "|---|---|---|---|---|---|---|"]
    for r in rr[:10]:
        n = rn.get(r["runner"])
        L.append(f"| {r['runner']} | {r['runs']} | {r['captured']:.0%} | {r['median_s_captured']}"
                 + (f" ({n['median_s_captured']})" if n and n["median_s_captured"] is not None else "")
                 + f" | {r['dropped']} | {r['pushed']:.0%} | {r['winners_share']:.0%} |")
    L.append("")
    tot = collections.Counter(); wins = collections.Counter()
    for (k, w), c in dbl.items(): tot[k] += c; wins[k] += c * w
    L.append("Double running: " + "; ".join(f"{k} {tot[k]} runs ({wins[k] / tot[k]:.0%} by winners)" for k in tot) + ".")
    fa = flag_answers(src, ids)
    L += ["", "**Flag answers** (answering the enemy's capture): " + "; ".join(
        f"{k}: {v['answers']} answers, median {v['median_cap_delay']} s, {v['median_slower_than_possible']} s slower than possible, "
        f"{v['30s+_slower']} answers 30 s+ slower" for k, v in fa.items()) + ".", ""]
    kp, intr_on, intr_by, kd_by = skills(ids)
    L += [f"**Skills: kill participation** (share of casts at an enemy who died within 5 s; {MIN_N}+ casts):", ""]
    L.append("- Highest: " + "; ".join(f"{n} {r:.0%} of {c}" for n, c, r in kp[:12]))
    L.append("- Lowest: " + "; ".join(f"{n} {r:.0%} of {c}" for n, c, r in kp[-8:]))
    L += ["", "**Interrupts:** skills interrupted most (whose): " + "; ".join(f"{s} on the {r} {n}" for (r, s), n in intr_on.most_common(10))
          + ". Interrupt skills landing most: " + "; ".join(f"{s} {n}" for s, n in intr_by.most_common(8)) + ".",
          "", "**Knockdowns by skill:** " + "; ".join(f"{s} {n}" for s, n in kd_by.most_common(8)) + ".", ""]
    by, wl = saves(ids)
    L.append("**Spikes survived** (400+ damage in 3 s on one player; survived = alive 8 s later): " + "; ".join(f"{k} {v[1]} of {v[0]} ({v[1] / v[0]:.0%})" for k, v in wl.items() if v[0])
             + ". By target: " + "; ".join(f"{k} {v[1] / v[0]:.0%} of {v[0]}" for k, v in sorted(by.items(), key=lambda kv: -kv[1][0]) if v[0] >= 10) + ".")
    mk = monks(src, ids)
    L += ["", "**Monks** (per 2-minute phase alive 60 s+): " + "; ".join(
        f"{k}: {v['casts_per_min']} casts a minute, {v['fakes_per_phase']} fakes, idle {v['idle_while_ally_hurt_s']} s while an ally was hurt, "
        f"reaction {v['median_reaction_s']} s, bursts answered {v['bursts_answered']:.0%}" for k, v in mk.items()) + ".", ""]
    dd = deaths(src, ids)
    L += [f"**Deaths** ({dd['deaths']}): {dd['with_a_knockdown']} with a knockdown on the victim; {dd['monk_cast_on_victim_last_5s']} had a "
          "monk cast on the victim in the last 5 s. Monk skills interrupted in the 6 s before a death: "
          + "; ".join(f"{s} {n}" for s, n in dd["monk_skills_interrupted_6s_before"]) + ".", ""]
    return L


if __name__ == "__main__":
    import model as M
    a = sys.argv[1:]
    src = a[a.index("--src") + 1] if "--src" in a else "/tmp/gl"
    bs = M.batches(); ids = [m for b in bs for m in b["matches"]]
    print("\n".join(snapshot(ids, bs[-1]["matches"], src)))
