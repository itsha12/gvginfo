"""Standard review tables for one match: builds, phases, stand holds, pit NPC kills and Entourage, lord damage,
deaths with support context, team totals. Usage: python3 report.py <report id or path to .json.gz> [section ...]
Sections: builds phases stand npcs lord deaths spikes splits output totals (default: all). Interpret with knowledge/tactics.md."""
import collections, sys
from replaylib import Match, PROT_SKILLS


def builds(m):
    for tag, rows in m.builds().items():
        print(tag)
        for r, prof, bar in rows: print(f"  {r:10} {prof:20} {', '.join(bar)}")


def phases(m, step=150):
    end = int(m.o["meta"]["match_length_s"] * 10)
    for t in range(0, end, step):
        cars = set(m.carrier_at(t)); line = []
        for tm in (1, 2):
            gs = m.groups(tm, t)
            line.append(m.tag[tm] + ": " + " | ".join(
                f"{len(g)}@{m.loc(g[0], t)}[" + ",".join(m.roles[a] + ("*" if a in cars else "") for a in g) + "]" for g in gs))
        print(m.f(t), "   ".join(line))


def stand(m):
    caps = [(t, a) for t, typ, a in m.o["flags"] if typ == "flagstand_captured" and m.team(a) in m.tag]
    end = m.o["meta"]["match_length_s"] * 10
    for i, (t, a) in enumerate(caps):
        e = caps[i + 1][0] if i + 1 < len(caps) else end
        print(f"  {m.f(t)}-{m.f(e)} {m.tag[m.team(a)]:5} held {(e - t) / 10:4.0f}s, capped by {m.role(a)}")
    print("  morale boosts:", [(m.f(r[0]), m.tag[m.team(r[2])]) for r in m.o["ev"] if r[1] == "mo" and (r[5] or 0) > 0
                                and m.A[r[2]].get("slot") == 1])
    near = [(m.f(t), m.tag[m.team(a)], round((e - t) / 10)) for i, (t, a) in enumerate(caps)
            for e in [caps[i + 1][0] if i + 1 < len(caps) else end] if 100 <= (e - t) / 10 < 120]
    if near: print("  holds that just missed a boost (100-119 s):", near)
    long = [(m.f(c["s"]), m.f(c["e"]), m.role(c["a"]), round((c["e"] - max(c["s"], 0)) / 10)) for c in m.carries
            if c["e"] > 0 and c["e"] - max(c["s"], 0) >= 600]
    print("  long carries (60 s+, holding the flag):", long)
    print("  carries:", [(m.f(c["s"]), m.f(c["e"]), m.role(c["a"]), c["how"].split("_")[-1]) for c in m.carries if c["e"] > 0])


def npcs(m):
    lords = {l["a"]: l for l in m.o.get("lords", [])}
    for r in m.o["ev"]:
        if r[1] == "dt" and not m.A[r[2]].get("player") and m.A[r[2]].get("team") in (1, 2) and r[2] not in lords:
            t, owner = r[0], m.A[r[2]]["team"]
            hits = collections.Counter(m.role(x[2]) for x in m.o["ev"] if x[1] == "dm" and x[3] == r[2] and t - 150 <= x[0] <= t)
            att = [m.role(a) for a in m.PL if m.team(a) != owner and m.alive(m.snap(a, t)) and m.loc(a, t) == "enemy base"]
            dfn = sum(1 for a in m.PL if m.team(a) == owner and m.alive(m.snap(a, t)) and m.loc(a, t) == "base")
            dfn60 = sum(1 for a in m.PL if m.team(a) == owner and m.alive(m.snap(a, t - 600)) and m.loc(a, t - 600) == "base")
            print(f"  {m.f(t)} {m.tag[owner]} {m.nm(r[2]):22} hits by {dict(hits.most_common(3))} | attackers in base {att} | "
                  f"defenders {dfn} (a minute before {dfn60})")
    for la, l in lords.items():   # Entourage casts; a gap only means suppressed when attackers were at the Lord (lords don't always cast it idle)
        ts = sorted(r[0] for r in m.o["ev"] if r[2] == la and r[1] in ("cs", "ca") and m.sk(r[4]) == "Entourage")
        gaps = [(m.f(a), m.f(b)) for a, b in zip(ts, ts[1:]) if b - a > 150 and b > 0]
        last = m.f(ts[-1]) if ts else None
        print(f"  {m.tag[l['team']]} Lord: Entourage last cast {last}; gaps {gaps}; pit at end {l.get('defenders_end')}")


def lord(m):
    lords = {l["a"]: l for l in m.o.get("lords", [])}
    per = collections.defaultdict(collections.Counter); who = collections.defaultdict(collections.Counter)
    for r in m.o["ev"]:
        if r[1] == "dm" and r[3] in lords and isinstance(r[2], int) and m.A[r[2]].get("player"):
            per[m.tag[m.team(r[2])]][int(r[0] // 600)] += r[5] or 0; who[m.tag[m.team(r[2])]][m.role(r[2])] += r[5] or 0
    for k in per: print(f"  {k} lord damage by minute {dict((a, round(b)) for a, b in sorted(per[k].items()))}; by player "
                        f"{dict((a, round(b)) for a, b in who[k].most_common())}")
    # base race: both teams with 3+ players in the enemy base at once
    end = int(m.o["meta"]["match_length_s"] * 10); race = []
    for t in range(0, end, 50):
        n = {tm: sum(1 for a in m.PL if m.team(a) == tm and m.alive(m.snap(a, t)) and m.loc(a, t) == "enemy base") for tm in (1, 2)}
        if n[1] >= 3 and n[2] >= 3: race.append(t)
    if race: print(f"  base race (3+ of each team in the enemy base): {m.f(race[0])} to {m.f(race[-1])}")
    own = collections.Counter(m.tag[m.team(r[2])] for r in m.o["ev"] if r[1] == "cs" and r[3] in lords and m.A[r[2]].get("player")
                              and m.team(r[2]) == lords[r[3]]["team"] and m.sk(r[4]) in PROT_SKILLS | {"Patient Spirit", "Vigorous Spirit"})
    print("  enchantments on own Lord (approx., -50 aggressiveness each):", dict(own))


def deaths(m):
    for x in m.o["deaths"]:
        v = x["who"]
        if not m.A[v].get("player"): continue
        t, tm = x["t"], m.team(v)
        al = {k: sum(1 for a in m.PL if m.team(a) == k and m.alive(m.snap(a, t - 30))) for k in (1, 2)}
        dmg = collections.Counter()
        for r in m.o["ev"]:
            if r[1] == "dm" and r[3] == v and t - 60 <= r[0] <= t and isinstance(r[2], int): dmg[m.role(r[2])] += r[5] or 0
        kd = [(m.f(k[0]), m.role(k[1]), m.sk(k[3])) for k in m.o.get("knockdowns", []) if k[2] == v and t - 80 <= k[0] <= t]
        rt = [(m.f(i[0]), m.role(i[1]), m.sk(i[2]), "on", m.sk(i[4])) for i in m.o.get("interrupts", []) if i[3] == v and t - 80 <= i[0] <= t]
        rm = [(m.f(i[0]), m.role(i[1]), m.sk(i[2]), "on", m.role(i[3]), m.sk(i[4])) for i in m.o.get("interrupts", [])
              if m.team(i[3]) == tm and m.A[i[3]].get("p") == "Monk" and i[3] != v and t - 80 <= i[0] <= t]
        sup = [(m.f(r[0]), m.role(r[2]), m.sk(r[4])) for r in m.o["ev"] if r[1] == "cs" and r[3] == v and m.team(r[2]) == tm
               and r[2] != v and t - 80 <= r[0] <= t]
        monks = [(m.role(a), round(m.dist(a, v, t - 20) or -1)) for a in m.PL if m.team(a) == tm and m.A[a].get("p") == "Monk" and a != v]
        hp = [m.snap(v, tt)["hp"] for tt in range(int(t - 60), int(t) + 1, 10) if m.snap(v, tt)]
        after = "  AFTER TIME (waits ~2 min)" if 0 <= t % 1200 <= 150 and t > 150 else ""
        print(f"\n{m.f(t)} {m.role(v)} died ({m.loc(v, t - 10)}){after} | alive {al[tm]} v {al[3 - tm]} | carrying {[m.role(a) for a in m.carrier_at(t - 30)]}")
        print(f"  hp {hp} | damage {dict((k, round(n)) for k, n in dmg.most_common(4))}")
        print(f"  knockdowns {kd} | interrupts on target {rt} | interrupts on own monks {rm}")
        print(f"  ally casts on target {sup} | own monks (distance) {monks}")


def totals(m):
    tot = collections.defaultdict(lambda: [0] * 6)
    for a, sks in m.o.get("outcomes", {}).items():
        for v in sks.values():
            for i in range(6): tot[m.role(int(a))][i] += v[i] or 0
    for k in sorted(tot): print(f"  {k:16} KD {tot[k][0]:3} INT {tot[k][1]:3} ENCH- {tot[k][2]:3} HEX- {tot[k][3]:3} COND- {tot[k][4]:3}")
    print("  knockdowns received:", collections.Counter(m.role(k[2]) for k in m.o.get("knockdowns", [])).most_common(6))


def spikes(m):
    """Per death: tightest big burst (armor ignoring vs other), sources, set, prots and Infuse with timing, interrupts.
    Not saveable (Denning's anchors, knowledge/tactics.md): target at 60%+ health, and 550+ armor ignoring within 0.35 s or
    more than the target's health within 0.35 s. 400 armor respecting in 0.6 s on a shield set should be survivable."""
    from replaylib import PROT_SKILLS
    for x in m.o["deaths"]:
        v = x["who"]
        if not m.A[v].get("player"): continue
        t, tm = x["t"], m.team(v)
        hits = sorted((r[0], r[2], r[5] or 0, (r[6] if len(r) > 6 else None) or "?") for r in m.o["ev"]
                      if r[1] == "dm" and r[3] == v and t - 80 <= r[0] <= t and isinstance(r[2], int) and m.team(r[2]) not in (None, tm))
        if not hits: continue
        big = [h for h in hits if h[2] >= 60]
        first = big[0][0] if big else hits[0][0]
        def window(w):   # most damage within w tenths, and how much of it was armor ignoring
            best = (0, 0, set(), first)
            for i, h in enumerate(hits):
                ws = [k for k in hits[i:] if k[0] - h[0] <= w]
                tot = sum(k[2] for k in ws); ai = sum(k[2] for k in ws if k[3] == "armor_ignoring")
                if tot > best[0]: best = (tot, ai, {k[1] for k in ws}, h[0])
            return best
        b35, b6 = window(3.5), window(6)
        s = m.snap(v, first - 3) or {}
        sets = m.o.get("sets", {}).get(str(v), [])
        setl = sets[s["w"]]["label"] if s and 0 <= s.get("w", -1) < len(sets) else "?"
        maxhp = (sets[s["w"]]["hp"] if s and 0 <= s.get("w", -1) < len(sets) else None) or m.A[v].get("hp") or 0
        hpnow = round(maxhp * s.get("hp", 100) / 100) if maxhp else None
        sup = [(f"{(r[0] - first) / 10:+.1f}s", m.role(r[2]), m.sk(r[4])) for r in m.o["ev"]
               if r[1] == "cs" and r[3] == v and m.team(r[2]) == tm and first - 30 <= r[0] <= t
               and (m.sk(r[4]) in PROT_SKILLS or "Infuse" in m.sk(r[4]))]
        spikers = {h[1] for h in hits if h[0] >= first}
        rupts = [m.sk(i[4]) for i in m.o.get("interrupts", []) if i[3] in spikers and first - 30 <= i[0] <= t]
        # only a real spike counts: target at 60%+ health when it started
        nots = (s.get("hp", 0) >= 60) and (b35[1] >= 550 or bool(hpnow and b35[0] > hpnow))
        print(f"  {m.f(t)} {m.role(v):18} 0.35s: {round(b35[0])} ({round(b35[1])} armor ignoring) from {len(b35[2])} | "
              f"0.6s: {round(b6[0])} | set {setl}, health ~{hpnow} | first big hit to death {(t - first) / 10:.1f}s")
        print(f"      prots/Infuse {sup} | interrupts on spikers {rupts}{'  NOT SAVEABLE' if nots else ''}")


def splits(m, min_s=30):
    """Small groups (1-4 players) away from their team's main group for 30 s or more: where, who shadowed them
    (nearest enemy), snares and damage they took, deaths, and pit NPCs they killed."""
    from replaylib import Match as _M
    SNARES = {"Mind Freeze PvP", "Shard Storm", "Freezing Gust", "Ice Spikes", "Deep Freeze", "Pin Down", "Crippling Shot",
              "Mantis Touch", "Caltrops", "Return", "Shadowy Burden", "Siphon Speed", "Hamstring", "Crippling Anguish PvP",
              "Grasping Earth", "Ward Against Foes", "Snaring Web"}
    end = int(m.o["meta"]["match_length_s"] * 10)
    for tm in (1, 2):
        runs, cur = [], None
        for t in range(0, end, 20):
            gs = m.groups(tm, t)
            cars = set(m.carrier_at(t))
            sp = [g for g in gs[1:] if len(g) <= 4 and not (set(g) & cars) and not all(m.loc(a, t) == "base" for a in g)] if len(gs) > 1 else []
            key = frozenset(sp[0]) if sp else None
            if cur and key == cur[0]: cur[2] = t
            else:
                if cur and cur[2] - cur[1] >= min_s * 10: runs.append(cur)
                cur = [key, t, t] if key else None
        if cur and cur[2] - cur[1] >= min_s * 10: runs.append(cur)
        for g, a0, a1 in runs:
            g = list(g); mid = (a0 + a1) // 2
            enemies = [b for b in m.PL if m.team(b) != tm]
            near = sorted(enemies, key=lambda b: min((m.dist(b, a, mid) or 1e9) for a in g))[:2]
            snares = sum(1 for r in m.o["ev"] if r[1] == "cs" and r[3] in g and a0 <= r[0] <= a1 and m.sk(r[4]) in SNARES and m.team(r[2]) != tm)
            dead = [(m.f(x["t"]), m.role(x["who"])) for x in m.o["deaths"] if x["who"] in g and a0 <= x["t"] <= a1 + 50]
            kills = [m.nm(r[2]) for r in m.o["ev"] if r[1] == "dt" and a0 <= r[0] <= a1 and not m.A[r[2]].get("player")
                     and m.A[r[2]].get("team") not in (None, tm)
                     and any(x[1] == "dm" and x[3] == r[2] and x[2] in g and r[0] - 150 <= x[0] <= r[0] for x in m.o["ev"])]
            print(f"  {m.tag[tm]} {m.f(a0)}-{m.f(a1)} split {[m.roles[a] for a in g]} at {m.loc(g[0], mid)} | nearest enemies "
                  f"{[m.role(b) for b in near]} | enemy snares on it {snares} | deaths {dead} | NPCs killed {kills}")


def output(m):
    """Damage to enemy players per player per minute (spots passive damage dealers, e.g. during an 8v7)."""
    dm = collections.defaultdict(collections.Counter)
    for r in m.o["ev"]:
        if (r[1] == "dm" and isinstance(r[2], int) and isinstance(r[3], int) and r[3] < len(m.A) and m.A[r[2]].get("player")
                and m.A[r[3]].get("player") and m.team(r[3]) != m.team(r[2])):
            dm[m.role(r[2])][int(r[0] // 600)] += r[5] or 0
    end = int(m.o["meta"]["match_length_s"] // 60) + 1
    print("  minute:          " + " ".join(f"{i:5}" for i in range(end)))
    for k in sorted(dm):
        print(f"  {k:16} " + " ".join(f"{round(dm[k][i]):5}" for i in range(end)))


SECTIONS = dict(output=output, splits=splits, spikes=spikes, builds=builds, phases=phases, stand=stand, npcs=npcs, lord=lord, deaths=deaths, totals=totals)

if __name__ == "__main__":
    src = sys.argv[1]
    m = Match.load(src) if src.endswith((".gz", ".json")) else Match.from_branch(src)
    meta = m.o["meta"]
    print(meta["map"], meta["match_length_s"], "s |", [(t["tag"], t["rating"], "deaths", t["deaths"], "caps", t["captures"]) for t in meta["teams"]],
          "| winner", m.tag.get((meta.get("result") or {}).get("winning_team_id")))
    for s in (sys.argv[2:] or SECTIONS):
        print(f"\n== {s}"); SECTIONS[s](m)
