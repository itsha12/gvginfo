"""Degen as damage (R-638, R-649, R-655, R-661): one reading, `Match.degen()`.

The replays record degeneration as no damage at all, so every damage figure read from hits alone left it out: a
ranger's poison, a paragon's burning, disease. gvg.report's summary has it, as totals for the match: what each player
took from each source by condition or skill (what landed, net of regen), and what each player's degen did to each NPC
and Guild Lord. Those totals are kept in the file beside each replay (extras.py) and are the amounts here. Only the
timing is ours: a total is laid over the seconds the replay shows that condition or hex on that target (for an NPC or
a Lord, which the replay's intervals never name, over the stretches its caster or his team was hitting it, R-661).

    D = Match.from_branch("<report id>").degen()
    D.rows[target]      [(second, amount, source, kind)] in time order; source is an agent of the replay, "map" for a
                        hall's own degen (the Miasma of Isle of Meditation, the lava of Burning Isle) or None where
                        gvg.report names nobody (its "Observed Burning": the burning was seen, who lit it was not)
    D.taken(a, t0, t1, by=None)     degen on agent a in (t0, t1]; by=agents for those sources only
    D.dealt(by, t0, t1, on=None)    degen those agents put on others in (t0, t1]; on=agents for those targets only
    D.account           what was done with every point of gvg.report's degen in this match (R-460: nothing is dropped
                        without being counted)

What is degen dealt by the enemy, and what is not:
  - a row whose source is an enemy player or NPC is that source's;
  - a row gvg.report credits to nobody (observed conditions, conditions drawn or passed on by a team mate, its
    unattributed remainders) is damage taken with no source: in every amount a player or a team took, in no figure of
    what a player dealt;
  - a hall's own degen is taken, source "map";
  - a Vampiric weapon's upkeep (one pip on its holder; 11% of all degen gvg.report records) is the holder's own and is
    no damage: left out, counted in the account as `own_weapon`. A row from a team mate is left out the same way (`own`).

Amounts take degen in; who is in which fight, a stand-off, who killed a player and who is on an NPC or a Lord stay
read from hits and casts (R-655): degen runs on after the player who put it there has left. So `rows` is never read
to say who is where.

A total with no second to lie on (the condition is nowhere on that target in the replay; the Miasma of Isle of
Meditation, five pips on whoever stands on the outer path, which no interval records) is untimed: it is in `account`
and in no timed figure. Over the 658 stored matches (2026-11-24): 10.2 million health of degen on players is laid on
its seconds (the recorded hits of players on players come to 35.6 million), 1.3 million on NPCs (hits: 9.4 million)
and 0.3 million on Lords; 1.3 million is weapon upkeep; 0.6 million is the Miasma, untimed; 35 thousand else is untimed. Lord damage stays gvg.report's Lord record
(R-632): the degen on a Lord is kept here and read by nothing yet.

    python3 degen.py <report id>      the account of one match and its largest sources
    python3 degen.py cover            the account over every stored match (exit 1 where a match cannot be read)
"""
import bisect, collections, math, re

OWN_WEAPON = ("Vampiric Weapon",)                  # gvg.report's source names for a weapon's own upkeep: no damage
MAP_SOURCES = ("Isle of Meditation Miasma", "Lava Pits")      # a hall's own degen: taken, from nobody
ON_GAP_S = 5                                       # as npcpower.py: hits on an NPC no further apart are one stretch
ON_PAD_S = 2                                       # ... which runs this long past its last hit
CONDS = ("bleeding", "burning", "poison", "disease")


def _base(name): return re.sub(r"\s*\(?PvP\)?$", "", name or "").strip()


class Degen:
    def __init__(self, m):
        self.m = m
        x = m.extras(); o = x.o
        self.summary = x.summary
        self.rows = collections.defaultdict(list)
        self.account = collections.Counter()
        self.untimed = []                              # [(target, source, kind, amount)]: in gvg.report's totals, on no second
        if not x.summary:                              # no summary when the file was written: no degen for this match, and every reading says so (`summary` False)
            self._index(); return
        A, PL = m.A, set(m.PL)
        end = self._end()
        keys = {a["a"]: a.get("n") or a.get("k") or "" for a in x.agents}
        team = lambda a: A[a].get("team") if isinstance(a, int) and a < len(A) else None

        # the seconds the replay shows each condition or degen hex on each player: (target, kind) -> {second: {casters}}
        on = collections.defaultdict(lambda: collections.defaultdict(set))
        for e in m.o.get("effects") or []:
            if e[0] is None or e[5] not in PL: continue
            if e[2] == "c" and e[7] in CONDS: kind = e[7]
            elif e[2] == "h": kind = "hex:" + _base(m.sk(e[3]))
            else: continue
            s0, s1 = max(e[0] / 10, 0), min((e[1] if e[1] is not None else end * 10) / 10, end)
            for u in range(int(math.floor(s0)), int(math.ceil(s1))):
                on[(e[5], kind)][u].add(e[4] if isinstance(e[4], int) else None)

        # ---- players: what each took, by source and kind (gvg.report's `received` rows: net of regen)
        for r in o.get("received") or []:
            tg, src, skill, cond, amt = r[0], r[1], r[2], r[3], r[11]
            if not amt or amt <= 0 or tg not in PL: continue
            name = keys.get(src)
            if name is not None and any(n in name for n in OWN_WEAPON): self.account["own_weapon"] += amt; continue
            if name is None and team(src) is not None and team(src) == team(tg): self.account["own"] += amt; continue
            who = "map" if name is not None and any(n in name for n in MAP_SOURCES) else src if name is None and isinstance(src, int) and src < len(A) else None
            kind = cond if cond in CONDS else ("hex:" + _base(m.sk(skill))) if skill else None
            secs = self._seconds(on, tg, kind, who)
            if not secs:
                self.account["untimed_map" if who == "map" else "untimed"] += amt; self.untimed.append((tg, who, kind, amt)); continue
            each = amt / len(secs)
            for u in secs: self.rows[tg].append((u, each, who, kind))
            self.account["players"] += amt
            self.account["by enemy" if isinstance(who, int) else "from the map" if who == "map" else "no source"] += amt

        # ---- NPCs and Guild Lords: gvg.report credits the degen on them to the player (R-661), with no time
        hits = collections.defaultdict(list)           # (actor, target) -> [seconds he hit it]
        for e in m.o.get("ev") or []:
            if e[0] is not None and e[1] == "dm" and e[2] in PL and isinstance(e[3], int) and e[3] < len(A) and e[3] not in PL: hits[(e[2], e[3])].append(e[0] / 10)
        for r in o.get("targets") or []:
            if r[2] != "d" or not r[10] or r[10] <= 0: continue
            src, tg, amt, cond = r[0], r[3], r[10], r[12]
            if tg in PL or not isinstance(tg, int) or tg >= len(A): continue          # players are read from `received`, which has every source
            if src not in PL or team(tg) is None or team(tg) == team(src): self.account["npc_other"] += amt; continue
            v = hits.get((src, tg)) or sorted(t for (a, b), ts in hits.items() if b == tg and team(a) == team(src) for t in ts)
            secs = self._stretches(v, end)
            kind = cond if cond in CONDS else ("hex:" + _base(m.sk(r[1]))) if r[1] else None
            if not secs:
                self.account["untimed_npc"] += amt; self.untimed.append((tg, src, kind, amt)); continue
            each = amt / len(secs)
            for u in secs: self.rows[tg].append((u, each, src, kind))
            self.account["lord" if A[tg].get("npc") == "lord" or "Guild Lord" in (A[tg].get("n") or "") else "npcs"] += amt
        self._index()

    def _end(self):
        return max((T["t"][-1] for T in self.m.TR.values() if T.get("t")), default=0) / 10

    @staticmethod
    def _seconds(on, tg, kind, who):
        """The seconds a total lies on: those the replay shows that condition or hex on the target, put there by this
        source or by nobody named; else every second of it, whoever is named; else, for a total of no kind (gvg.report's
        remainders), every second any degen is on the target. None where there is no such second."""
        if kind is not None:
            d = on.get((tg, kind))
            if d:
                own = sorted(u for u, cs in d.items() if (who in cs if isinstance(who, int) else False) or None in cs)
                return own or sorted(d)
            if kind.startswith("hex:"): return None
        if kind is None and who == "map": return None     # a hall's own degen with no condition to see (the Miasma): where a player stood, which no interval says
        if kind is None or who is None:                   # no kind, or a kind seen under no interval and no source: any degen on the target
            s = set()
            for (t, k), d in on.items():
                if t == tg and (k in CONDS or kind is None): s.update(d)
            return sorted(s) or None
        return None

    @staticmethod
    def _stretches(v, end):
        if not v: return None
        v = sorted(v); out, s0, last = [], v[0], v[0]
        for t in v[1:]:
            if t - last > ON_GAP_S: out.append((s0, last + ON_PAD_S)); s0 = t
            last = t
        out.append((s0, last + ON_PAD_S))
        secs = sorted({u for a, b in out for u in range(int(a), int(min(b, end)) + 1)})
        return secs or None

    def _index(self):
        for a in self.rows: self.rows[a].sort(key=lambda r: r[0])
        self._t = {a: [r[0] for r in v] for a, v in self.rows.items()}
        self._by = None

    def cut(self, a, t0, t1):
        """The rows on agent a in (t0, t1]."""
        v = self.rows.get(a)
        if not v: return ()
        T = self._t[a]
        return v[bisect.bisect_right(T, t0):bisect.bisect_right(T, t1)]

    def taken(self, a, t0, t1, by=None):
        return sum(r[1] for r in self.cut(a, t0, t1) if by is None or r[2] in by)

    def dealt(self, by, t0, t1, on=None):
        if self._by is None:                              # source -> [(second, amount, target, kind)]
            self._by = collections.defaultdict(list)
            for tg, v in self.rows.items():
                for u, n, src, kind in v:
                    if isinstance(src, int): self._by[src].append((u, n, tg, kind))
            for s in self._by: self._by[s].sort(key=lambda r: r[0])
            self._byt = {s: [r[0] for r in v] for s, v in self._by.items()}
        tot = 0.0
        for s in by:
            v = self._by.get(s)
            if not v: continue
            T = self._byt[s]
            tot += sum(r[1] for r in v[bisect.bisect_right(T, t0):bisect.bisect_right(T, t1)] if on is None or r[2] in on)
        return tot

    def dealt_rows(self, s):
        """[(second, amount, target, kind)] of what agent s's degen did, in time order."""
        self.dealt((), 0, 0)
        return self._by.get(s, ())


def _account(rid, entry=None):
    from replaylib import Match
    try:
        m = Match.from_branch(rid); D = m.degen()
    except Exception as e: return {"rid": rid, "error": f"{type(e).__name__}: {e}"}
    hits = collections.Counter()
    for e in m.o.get("ev") or []:
        if e[1] == "dm" and e[2] in m.PL and e[3] in m.PL and m.team(e[2]) != m.team(e[3]) and len(e) > 5 and isinstance(e[5], (int, float)): hits["players"] += e[5]
        elif e[1] == "dm" and e[2] in m.PL and isinstance(e[3], int) and e[3] < len(m.A) and m.A[e[3]].get("npc") and len(e) > 5 and isinstance(e[5], (int, float)): hits["npcs"] += e[5]
    unt = collections.Counter()
    for tg, who, kind, amt in D.untimed: unt[kind or "no kind"] += amt
    return {"rid": rid, "summary": D.summary, "account": dict(D.account), "hits": dict(hits), "untimed": dict(unt)}


if __name__ == "__main__":
    import sys
    a = sys.argv[1:]
    if a and a[0] == "cover":
        import multiprocessing, json, subprocess, common
        idx = json.loads(subprocess.check_output(["git", "-C", common.REPO, "show", "origin/replays:index.json"]))["matches"]
        with multiprocessing.Pool(int(a[a.index("--jobs") + 1]) if "--jobs" in a else 2) as pool: rows = pool.map(_account, sorted(idx), chunksize=8)
        bad = [r for r in rows if "error" in r]
        tot, hits, unt = collections.Counter(), collections.Counter(), collections.Counter()
        for r in rows:
            if "error" in r: continue
            tot.update(r["account"]); hits.update(r["hits"]); unt.update(r["untimed"])
        print(f"{len(rows)} stored matches; {len(bad)} could not be read; {sum(1 for r in rows if 'error' not in r and not r['summary'])} with no summary (no degen)")
        for k, v in tot.most_common(): print(f"  {k:14} {v:12,.0f}")
        print(f"  beside it, recorded hits: players on players {hits['players']:,.0f}, players on NPCs {hits['npcs']:,.0f}")
        print("  untimed, by kind: " + ", ".join(f"{k} {v:,.0f}" for k, v in unt.most_common(12)))
        for r in bad[:10]: print("  " + r["rid"][:8], r["error"])
        sys.exit(1 if bad else 0)
    elif a:
        from replaylib import Match
        import json, subprocess, common
        idx = json.loads(subprocess.check_output(["git", "-C", common.REPO, "show", "origin/replays:index.json"]))["matches"]
        rid = next(r for r in idx if r.startswith(a[0]))
        m = Match.from_branch(rid); D = m.degen()
        print(" v ".join(idx[rid]["teams"]), "summary", D.summary)
        for k, v in D.account.most_common(): print(f"  {k:14} {v:10,.0f}")
        by = collections.Counter()
        for tg, v in D.rows.items():
            for u, n, src, kind in v: by[(m.role(src) if isinstance(src, int) else str(src), kind, "players" if tg in m.PL else "NPCs and Lords")] += n
        for k, v in by.most_common(14): print(f"  {v:8,.0f}  {k[0]:22} {str(k[1]):18} on {k[2]}")
        for tg, who, kind, amt in sorted(D.untimed, key=lambda r: -r[3])[:8]: print(f"  untimed {amt:8,.0f}  on {m.role(tg)} from {m.role(who) if isinstance(who, int) else who} ({kind})")
    else: print(__doc__)
