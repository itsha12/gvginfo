"""Standard review tables for one match: builds, phases, stand holds, pit NPC kills and Entourage, lord damage,
deaths with support context, team totals. Usage: python3 report.py <report id or path to .json.gz> [section ...]
Sections: builds phases stand npcs lord deaths totals (default: all). Interpret with knowledge/tactics.md."""
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
    caps = [(t, a) for t, typ, a in m.o["flags"] if typ == "flagstand_captured"]
    end = m.o["meta"]["match_length_s"] * 10
    for i, (t, a) in enumerate(caps):
        e = caps[i + 1][0] if i + 1 < len(caps) else end
        print(f"  {m.f(t)}-{m.f(e)} {m.tag[m.team(a)]:5} held {(e - t) / 10:4.0f}s, capped by {m.role(a)}")
    print("  morale boosts:", [(m.f(r[0]), m.tag[m.team(r[2])]) for r in m.o["ev"] if r[1] == "mo" and (r[5] or 0) > 0
                                and m.A[r[2]].get("slot") == 1])
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
    for la, l in lords.items():   # Entourage: recast about every 10 s while allowed; gaps over 15 s = suppressed
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
        print(f"\n{m.f(t)} {m.role(v)} died ({m.loc(v, t - 10)}) | alive {al[tm]} v {al[3 - tm]} | carrying {[m.role(a) for a in m.carrier_at(t - 30)]}")
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


SECTIONS = dict(builds=builds, phases=phases, stand=stand, npcs=npcs, lord=lord, deaths=deaths, totals=totals)

if __name__ == "__main__":
    src = sys.argv[1]
    m = Match.load(src) if src.endswith((".gz", ".json")) else Match.from_branch(src)
    meta = m.o["meta"]
    print(meta["map"], meta["match_length_s"], "s |", [(t["tag"], t["rating"], "deaths", t["deaths"], "caps", t["captures"]) for t in meta["teams"]],
          "| winner", m.tag.get((meta.get("result") or {}).get("winning_team_id")))
    for s in (sys.argv[2:] or SECTIONS):
        print(f"\n== {s}"); SECTIONS[s](m)
