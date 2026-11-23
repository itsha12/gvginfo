"""NPC damage by kind of bar (R-433): how fast a group kills footmen, archers, knights, the Bodyguard and the Guild Lord.

Measured by rough classes of similar bars, not bar by bar (his ruling): a player's class is his profession and what he
hits with (`bar_class`: a warrior by weapon, an elementalist by attunement, a monk by whether he heals). For every class
and every kind of NPC, over the matches that count: the damage its players dealt to NPCs of that kind and the seconds
their group spent on them, which give a rate (damage a second, one player of the group); and for every kind of NPC, the damage it takes to
kill one (the middle of the damage recorded on those that died). A group's NPC damage is then the sum of its players'
rates, and the seconds it needs for one NPC of a kind is that kind's damage to kill over the sum.

A group is "on" a kind of NPC for a stretch: its team's hits on NPCs of that kind with no more than ON_GAP_S between
them, from the first hit to ON_PAD_S after the last. Every player hitting in it, and every living team mate standing
within WITH_R of one of them at its middle, is in the group for the whole stretch, whether he hits or not: a monk on a
split adds almost nothing to how fast it kills, and the rate says so. Kept beside it: the rate while the player is
himself hitting (`dps_hitting`) and the share of the group's time he is (`hitting`).

The Lord's figures here are the engine's sum of recorded hits, which is a rate for comparing bars, not a total: Lord
damage totals are gvg.report's to say (R-632). Healing and armour are inside the measure (damage is as applied), and
so is the Amulet of Protection's limit on the Lord.

The benchmark is `data/benchmarks/npc_damage.json` (`python3 npcpower.py bench`). `group(m, ids)` reads it: the rate
of a group against each kind and the seconds to kill one. A class with fewer than MIN_STRETCHES stretches on a kind
takes the rate of all classes pooled (said in the file as `pooled`): a blank would read as "does no damage".

Usage:  python3 npcpower.py bench            rebuild the benchmark over every match that counts
        python3 npcpower.py show             print it
        python3 npcpower.py <report id>      each player's class and his team's NPC damage as a group"""
import collections, json, os, statistics, sys
from common import REPO

KINDS = ("footman", "archer", "knight", "bodyguard", "guild_lord")
KIND_WORDS = {"footman": "a footman", "archer": "an archer", "knight": "a knight", "bodyguard": "the Bodyguard", "guild_lord": "the Guild Lord"}
ON_GAP_S = 5                # hits on a kind of NPC no further apart than this are one stretch (Claude's draft)
ON_PAD_S = 2                # a stretch runs this long past its last hit (an attack or cast takes about this long to come round)
WITH_R = 1500               # a team mate this close to a player hitting the NPCs is with the group that is on them (about a cast range and a half; Claude's draft)
MIN_STRETCHES = 30          # a class needs this many stretches on a kind for a rate of its own (the floor of plays, R-538)
PATH = os.path.join(REPO, "data", "benchmarks", "npc_damage.json")
WEAPONS = {"Hammer Mastery": "Hammer warrior", "Axe Mastery": "Axe warrior", "Swordsmanship": "Sword warrior"}


def bar_class(m, a):
    """The rough class of a player's bar for damage on NPCs: profession and what he hits with."""
    from buildfeat import _skills
    from phases import healer
    S, p = _skills(), m.A[a].get("p") or "?"
    bar = [S.get(m.sk(b)) for b in m.A[a].get("bar", []) if b]
    bar = [s for s in bar if s]
    names = {s["name"] for s in bar}
    if healer(m, a): return "Backline (heals and prots)"
    if p == "Monk": return "Smiting monk"
    if p == "Warrior":
        c = collections.Counter(s.get("attr") for s in bar if s.get("attr") in WEAPONS)
        return WEAPONS[c.most_common(1)[0][0]] if c else "Warrior"
    if p == "Elementalist":
        for e in ("Fire", "Air", "Earth", "Water"):
            if f"{e} Attunement" in names: return f"{e} elementalist"
        return "Elementalist"
    return p


def match_rows(rid):
    """One match: per player his class and, per kind of NPC, [damage, seconds on it, stretches]; and per NPC that died, its kind and the damage recorded on it."""
    from replaylib import Match
    m = Match.from_branch(rid)
    pl = set(m.PL)
    hits = collections.defaultdict(list)                 # (player, kind) -> [(second, amount)]
    taken, died = collections.Counter(), set()
    for r in m.o["ev"]:
        if r[0] is None or not isinstance(r[2], int) or r[2] >= len(m.A): continue
        if r[1] == "dt" and m.A[r[2]].get("npc") in KINDS: died.add(r[2]); continue
        if r[1] != "dm" or not isinstance(r[3], int) or r[3] >= len(m.A): continue
        k, n = m.A[r[3]].get("npc"), (r[5] if len(r) > 5 and isinstance(r[5], (int, float)) else 0)
        if k not in KINDS or n <= 0: continue
        taken[r[3]] += n
        if r[2] in pl and m.A[r[3]].get("team") not in (None, m.team(r[2])): hits[(r[2], k)].append((r[0] / 10, n))
    by_team = collections.defaultdict(list)              # (team, kind) -> [(second, player)]
    for (a, k), v in hits.items():
        for t, _ in v: by_team[(m.team(a), k)].append((t, a))
    with_group = collections.defaultdict(lambda: [0.0, 0.0, 0])           # (player, kind) -> damage, seconds his group was on that kind, stretches
    for (tm, k), v in by_team.items():
        v.sort()
        cuts, s0, last, who = [], v[0][0], v[0][0], {v[0][1]}
        for t, a in v[1:]:
            if t - last > ON_GAP_S: cuts.append((s0, last + ON_PAD_S, who)); s0, who = t, set()
            last = t; who.add(a)
        cuts.append((s0, last + ON_PAD_S, who))
        for s0, s1, who in cuts:
            mid = round((s0 + min(s1, s0 + (s1 - s0) / 2)) * 10)
            there = set(who)
            for b in m.PL:                               # a team mate standing with the players hitting counts in the group though he hits nothing (a monk on a split)
                if b in there or m.team(b) != tm or not m.alive(m.snap(b, mid)): continue
                if any(m.alive(m.snap(h, mid)) and m.dist(b, h, mid) < WITH_R for h in who): there.add(b)
            for b in there:
                g = with_group[(b, k)]
                g[0] += sum(n for t, n in hits.get((b, k), ()) if s0 <= t <= s1); g[1] += s1 - s0; g[2] += 1
    players = []
    for a in m.PL:
        row = {"cls": bar_class(m, a), "role": m.roles.get(a), "team": m.tag.get(m.team(a))}
        for k in KINDS:
            g = with_group.get((a, k))
            if not g: continue
            v = sorted(hits.get((a, k), ()))
            secs = 0.0
            if v:
                s0, last = v[0][0], v[0][0]
                for t, _ in v[1:]:
                    if t - last > ON_GAP_S: secs += last - s0 + ON_PAD_S; s0 = t
                    last = t
                secs += last - s0 + ON_PAD_S
            row[k] = [round(g[0]), round(g[1], 1), g[2], round(secs, 1)]
        players.append(row)
    return {"rid": rid, "players": players, "killed": [[m.A[x]["npc"], round(taken[x])] for x in sorted(died) if taken[x] > 0]}


def _job(rid):
    try: return match_rows(rid)
    except Exception as e: return {"rid": rid, "error": f"{type(e).__name__}: {e}"}


def bench(jobs=2):
    import multiprocessing, common
    ids = common.replay_ids()
    with multiprocessing.Pool(jobs) as pool: rows = pool.map(_job, ids, chunksize=8)
    bad = [r for r in rows if "error" in r]
    if bad: raise SystemExit(f"npcpower: {len(bad)} matches failed to read (R-460), first: {bad[0]}")
    agg = collections.defaultdict(lambda: [0.0, 0.0, 0, set(), 0.0])       # (class, kind) -> damage, seconds his group was on that kind, stretches, matches, seconds he was hitting
    players = collections.Counter()
    kill = collections.defaultdict(list)
    for r in rows:
        for p in r["players"]:
            players[p["cls"]] += 1
            for k in KINDS:
                if k in p:
                    g = agg[(p["cls"], k)]; g[0] += p[k][0]; g[1] += p[k][1]; g[2] += p[k][2]; g[3].add(r["rid"]); g[4] += p[k][3]
        for k, n in r["killed"]: kill[k].append(n)
    out = {"about": "NPC damage by kind of bar (R-433; npcpower.py): damage a second added by one player of a class to a group that is on a kind of NPC (he is with it whether he hits or not), and the damage it takes to kill one. "
                    "A class under the floor on a kind takes the pooled rate.", "matches": len(rows), "floor": MIN_STRETCHES,
           "to_kill": {k: {"damage": round(statistics.median(v)), "n": len(v)} for k, v in kill.items() if v}, "pooled": {}, "classes": {}}
    for k in KINDS:
        d = sum(g[0] for (c, kk), g in agg.items() if kk == k); s = sum(g[1] for (c, kk), g in agg.items() if kk == k)
        out["pooled"][k] = round(d / s, 1) if s else None
    for c in sorted(players, key=lambda c: -players[c]):
        e = out["classes"][c] = {"players": players[c]}
        for k in KINDS:
            g = agg.get((c, k))
            if g and g[2] >= MIN_STRETCHES: e[k] = {"dps": round(g[0] / g[1], 1), "dps_hitting": round(g[0] / g[4], 1) if g[4] else None, "hitting": round(g[4] / g[1], 2), "seconds": round(g[1]), "stretches": g[2], "matches": len(g[3])}
            else: e[k] = {"dps": out["pooled"][k], "pooled": True, "stretches": g[2] if g else 0}
    json.dump(out, open(PATH, "w"), indent=1)
    return out


_B = None
def load():
    global _B
    if _B is None:
        if not os.path.exists(PATH): raise FileNotFoundError(f"{PATH} is not built: run `python3 npcpower.py bench` (R-460)")
        _B = json.load(open(PATH))
    return _B


def group(m, ids):
    """A group of players as NPC damage (R-433): {kind: [damage a second together, seconds to kill one]}. Seconds are blank where the damage to kill a kind is not measured."""
    B, out = load(), {}
    cl = [bar_class(m, a) for a in ids]
    for k in KINDS:
        rate = sum(((B["classes"].get(c) or {}).get(k) or {}).get("dps") or B["pooled"][k] or 0 for c in cl)
        need = (B["to_kill"].get(k) or {}).get("damage")
        out[k] = [round(rate, 1), round(need / rate) if need and rate else None]
    return out


def show():
    B = load()
    print(f"NPC damage by kind of bar, {B['matches']} matches. Damage a second added by one player of a class to a group that is on that kind of NPC; * = the pooled rate (under {B['floor']} stretches).")
    print(f"{'':28} {'players':>7}  " + "  ".join(f"{k.replace('_', ' '):>12}" for k in KINDS))
    for c, e in B["classes"].items():
        print(f"{c:28} {e['players']:7}  " + "  ".join(f"{(str(e[k]['dps']) + ('*' if e[k].get('pooled') else '')):>12}" for k in KINDS))
    print(f"{'all classes pooled':28} {'':7}  " + "  ".join(f"{str(B['pooled'][k]):>12}" for k in KINDS))
    print(f"{'damage to kill one (middle)':28} {'':7}  " + "  ".join(f"{(str(B['to_kill'][k]['damage']) + ' (' + str(B['to_kill'][k]['n']) + ')') if k in B['to_kill'] else '':>12}" for k in KINDS))


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: print(__doc__)
    elif a[0] == "bench": bench(); show()
    elif a[0] == "show": show()
    else:
        from replaylib import Match
        m = Match.from_branch(a[0])
        for tm in (1, 2):
            ids = [x for x in m.PL if m.team(x) == tm]
            print(m.tag[tm], {m.roles[x]: bar_class(m, x) for x in ids})
            print("   as a group:", {k: v for k, v in group(m, ids).items()})
