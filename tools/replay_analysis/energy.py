"""Energy (R-664 to R-689): one reading, `Match.energy()`.

The replays hold no energy. gvg.report models it: for every player the least and the most energy he can have, every
two seconds, and his maximum as it changes with the weapon set he holds and with his death penalty or morale boost.
That estimate is kept in the file beside each replay (extras.py) and is what is read here. It is an estimate with
bounds, and every reading from it carries both (`lo`, `hi`); `mid` is their middle. A match gvg.report has no energy
for (before 27 August 2026, and 18 counted matches of 2 to 5 September) reads blank: `ok` is False and every figure
is None (R-672).

Whose energy (R-665, R-670, R-675): the backline monks' first; the midline's, which for energy is the Ritualist, the
Mesmer, the Elementalist, the Necromancer and the smite monk; nobody else's (`kind` is None for the frontline, the
Ranger and the Paragon, and nothing here answers for them).

The scale (R-667, R-668, R-686): energy is read as what the player would have if he took up his double high set now.
A monk can always change sets, so a monk at 10 on a 40/40 set has 30 more to call on, at the price of regeneration.
On that scale the top is 72 for a Monk, and for a Mesmer, a Ritualist and a Necromancer, whose casting sets hold 42
as a monk's does (their highest set seen in the stored matches is 72 too); for an Elementalist, whose maximum moves
with Energy Storage, it is the highest maximum he holds in that match. The top moves with death penalty and morale
as every maximum does: `top = 72 x (1 + morale / 100)`. So `scaled = shown + (top - the maximum of the set held)`,
never less than what is shown. At no death penalty this is his own formula, "the energy shown plus 72 less the
maximum of the set he holds".

Out of energy, for the excuse (R-681, R-682): a monk under 20, a midline player under 15, on that scale. `out` is
"yes" where even the most he can have is under the line, "maybe" where only the least is, else "no". These two lines
are his set points for the excuse only: where energy is an input to a decision no line is set, and what followed is
read across the range of energy at that decision (R-669).

    E = Match.from_branch("<report id>").energy()
    E.ok                      False where gvg.report has no energy for the match
    E.kind(a)                 "monk", "midline" or None
    E.at(a, t)                {lo, hi, mid, shown: (lo, hi), cap, top, out} at second t on the scale; None where unread or he is dead
    E.group(ids, t)           the read players among ids, alive: {n, mean, low, mean_lo, mean_hi, out, maybe}; `low` is the lowest
                              player's middle (R-683: the average, the lowest monk and how many, the data to say which tells)
    E.monks(ids), E.midline(ids)    the backline monks and the midline among ids

    python3 energy.py <report id>     each read player's energy through one match
    python3 energy.py cover           coverage, and the checks of the record over every counted match (does it read as a player knows)
"""
import bisect, collections

TOP = 72                        # a double high set (R-667): 40 on a staff, 42 on a 40/40 set, 62 in single high, 72 in double high
OUT_MONK = 20                   # a monk under this is out, for the excuse (R-681: "Anything less than 20e in my mind would likely be not the monk's fault")
OUT_MIDLINE = 15                # a midline player under this is out (R-682), on the same scale (R-686)
MIDLINE = ("Ritualist", "Mesmer", "Elementalist", "Necromancer")      # R-670; the smite monk is told below


def backline_monk(m, a):
    """A backline monk, as `jobs.plays` tells one (R-457): a Monk in a monk's slot who does not smite."""
    r = m.roles.get(a) or ""
    return m.A[a].get("p") == "Monk" and not r.startswith("Monk ") and "WoC" not in r


class Energy:
    def __init__(self, m):
        self.m = m
        E = m.extras().energy
        self.ok = bool(E and E.get("players"))
        self._k = {}
        for a in m.PL:
            p = m.A[a].get("p")
            self._k[a] = "monk" if backline_monk(m, a) else "midline" if p in MIDLINE or p == "Monk" else None
        if not self.ok: return
        self.step, self.start = E["step"] / 10, E["start"] / 10
        self._p = {int(a): v for a, v in E["players"].items()}
        self._cap = {a: ([c[0] / 10 for c in v.get("cap") or []], [c[1] for c in v.get("cap") or []]) for a, v in self._p.items()}
        self._mo = collections.defaultdict(lambda: ([], []))      # player -> (seconds, death penalty or morale boost in % of his maximum)
        for e in m.o.get("ev") or []:
            if e[1] == "mo" and e[0] is not None and e[2] in self._k and isinstance(e[5], (int, float)):
                ts, vs = self._mo[e[2]]; ts.append(e[0] / 10); vs.append(e[5])
        self._own_top = {}                                        # an Elementalist's own top: the highest maximum he holds in the match, morale taken out
        for a in m.PL:
            if m.A[a].get("p") == "Elementalist" and a in self._cap:
                ts, vs = self._cap[a]
                self._own_top[a] = max((v / self._f(a, t) for t, v in zip(ts, vs) if v), default=None)

    def kind(self, a): return self._k.get(a)
    def monks(self, ids): return [a for a in ids if self._k.get(a) == "monk"]
    def midline(self, ids): return [a for a in ids if self._k.get(a) == "midline"]

    def _f(self, a, t):
        ts, vs = self._mo[a] if a in self._mo else ((), ())
        i = bisect.bisect_right(ts, t) - 1
        return 1 + (vs[i] if i >= 0 else 0) / 100

    def at(self, a, t):
        if not self.ok or self._k.get(a) is None or a not in self._p: return None
        s = self.m.snap(a, round(t * 10))
        if not self.m.alive(s): return None
        v = self._p[a]
        i = int(round((t - self.start) / self.step))
        if i < 0 or i >= len(v["lo"]) or v["lo"][i] is None or v["hi"][i] is None: return None
        ts, cs = self._cap[a]
        j = bisect.bisect_right(ts, t) - 1
        cap = cs[max(j, 0)] if cs else None
        if cap is None: return None
        base = self._own_top.get(a) if a in self._own_top else TOP
        top = max((base or cap) * self._f(a, t), cap)
        lo, hi = v["lo"][i] + top - cap, v["hi"][i] + top - cap
        line = OUT_MONK if self._k[a] == "monk" else OUT_MIDLINE
        return {"lo": round(lo, 1), "hi": round(hi, 1), "mid": round((lo + hi) / 2, 1), "shown": (v["lo"][i], v["hi"][i]), "cap": cap, "top": round(top, 1),
                "out": "yes" if hi < line else "maybe" if lo < line else "no"}

    def group(self, ids, t):
        """The read players among ids who are alive at t, together (R-683). None where the match has no energy; n 0 where none of them is read or alive."""
        if not self.ok: return None
        r = [x for x in (self.at(a, t) for a in ids) if x]
        if not r: return {"n": 0, "mean": None, "low": None, "mean_lo": None, "mean_hi": None, "out": 0, "maybe": 0}
        n = len(r)
        return {"n": n, "mean": round(sum(x["mid"] for x in r) / n, 1), "low": min(x["mid"] for x in r), "mean_lo": round(sum(x["lo"] for x in r) / n, 1),
                "mean_hi": round(sum(x["hi"] for x in r) / n, 1), "out": sum(x["out"] == "yes" for x in r), "maybe": sum(x["out"] == "maybe" for x in r)}


# ---- each fight's energy on every play (R-689, piece 2; R-666 the third aspect, R-683): a record kept beside the plays, `flag_cost[rid].energy`.
# It tells no play and changes none. For every play: the second its decision arises (`decision_second`), and at that second and BEFORE_S before it, the
# energy of the backline monks and of the midline in that fight, the team's own and the enemy's, each as `Energy.group` (the average, the lowest player
# and how many: the data to say which tells, R-683). Whose (R-666: "on a split, only split monk energy matters"): on a split play (a split or its
# defence) our side is the players it names (`who`); on every other play our main team at that second, the fight the decision is about (a flag, a boost or
# a push play names its runners or pushers, who are not that fight; a runner away is the reason the fight is 8 v 7); their side is every enemy player in
# the same fight as one of ours in the FIGHT_WIN seconds to the decision (`Moments.linked`, the one reading of who is in which fight, R-464), else, where
# nobody of theirs is in a fight with ours (a run answered from a stand-off), their main team (`their_from` says which). The minute before reads the same
# players, those of them alive then: whether the energy at the decision was already so a minute before (SPEC 5, rule 4). Beside it, `team`: every living
# backline monk of each team, wherever he stands. It is what the answer to their split reads (R-688: by our own monks): on the defending side the
# defenders are the call itself, so their monks alone would read the energy of the answer chosen, not of the team choosing it. The like spots of the base res
# and of the decision to split at all (`res_spots`, `split_ticks`, records beside the plays too) carry the same reading.
BEFORE_S = 60                   # the minute before, as for every other factor of a decision (`jobs.FLAG_BEFORE_S`)
FIGHT_WIN = 4                   # who is in the fight is read over the 4 s to the decision, every other second as execution reads it (Claude's draft: one reading alone misses a player between casts)
FIGHT_STEP = 2
RES_READ_S = 20                 # a base res is a decision this long before the res (`jobs.RES_READ_S`, R-592)


def decision_second(p):
    """The second a play's decision arises: a flag play's one clock (`clock.anchor`, R-546: their runner's set-off, or our cap where we run again);
    a base res 20 s before the res (R-592, `res.early`); every other play its own start."""
    if p["play"] == "flag" and (p.get("clock") or {}).get("anchor") is not None: return int(p["clock"]["anchor"])
    if p["play"] == "base res": return int(p["t0"]) - RES_READ_S
    return int(p["t0"])


def _fight(M, X, foe, u):
    Y = set()
    for v in range(max(u - FIGHT_WIN, 0), u + 1, FIGHT_STEP):
        live = [a for a in X if M.AL[a][v]]
        for b in M.st.players[foe]:
            if b not in Y and M.AL[b][v] and any(M.linked(a, b, v) for a in live): Y.add(b)
    if Y: return sorted(Y), "fight"
    return [b for b in M.main_team(foe, u) if M.AL[b][u]], "main team"


def _read(E, M, tm, X, Y, u, how):
    side = lambda ids, v: {"monks": E.group(E.monks(ids), v), "midline": E.group(E.midline(ids), v)}
    team = lambda k, v: E.group(E.monks(M.st.players[k]), v)
    b = u - BEFORE_S
    return {"u": u, "own": side(X, u), "their": side(Y, u), "their_from": how, "ids": [E.monks(X), E.monks(Y)], "team": [team(tm, u), team(3 - tm, u)],
            "before": None if b < 0 else {"own": side(X, b), "their": side(Y, b), "team": [team(tm, b), team(3 - tm, b)]}}


def record(M, plays, ticks=(), spots=()):
    """{"ok", "plays": {play id: reading}, "split_ticks": {tick id: reading}, "res_spots": [reading, in the order of the spots]} for one match.
    `ok` False and nothing else where gvg.report has no energy for the match (R-672): every reading of it is blank, and the reports count such matches."""
    E = M.m.energy()
    if not E.ok: return {"ok": False}
    m, T = M.m, M.T
    agent = {(m.tag[m.team(a)], m.roles[a]): a for a in m.PL}
    out = {"ok": True, "plays": {}, "split_ticks": {}, "res_spots": []}
    for p in plays:
        tm, u = p["tm"], min(max(decision_second(p), 0), T)
        X = [agent[(m.tag[tm], r)] for r in (p.get("who") or ()) if (m.tag[tm], r) in agent] if p.get("split") is not None else []
        X = [a for a in X if M.AL[a][u]] or [a for a in M.main_team(tm, u) if M.AL[a][u]] or [a for a in M.st.players[tm] if M.AL[a][u]]
        Y, how = _fight(M, X, 3 - tm, u)
        out["plays"][p["id"]] = _read(E, M, tm, X, Y, u, how)
    for k in ticks:
        tm, u = k["tm"], min(int(k["t0"]), T)
        X = [a for a in M.main_team(tm, u) if M.AL[a][u]] or [a for a in M.st.players[tm] if M.AL[a][u]]
        Y, how = _fight(M, X, 3 - tm, u)
        out["split_ticks"][k["id"]] = _read(E, M, tm, X, Y, u, how)
    inb = M.base_zones() if spots else None
    for s in spots:                                       # the players in their base at the spot (as `jobs.res_spots` counts them), and the enemy players they fight
        tm, u = s["tm"], min(int(s["t"]), T)
        X = [a for a in M.st.players[tm] if M.AL[a][u] and M.P[a][u] and M._deep(a, u) in inb]
        Y, how = _fight(M, X, 3 - tm, u)
        out["res_spots"].append(_read(E, M, tm, X, Y, u, how))
    return out


# ---- the checks of the record: does it read as any player knows (a report; nothing is fitted and nothing reads it)
FIRE = 150                      # a team that took this much in hits in 10 s is under fire; one that took nothing is at rest (for the checks only)

def _check(rid):
    from replaylib import Match
    try:
        m = Match.from_branch(rid); E = m.energy()
    except Exception as e: return {"rid": rid, "error": f"{type(e).__name__}: {e}"}
    if not E.ok: return {"rid": rid, "ok": False}
    end = int(max(T["t"][-1] for T in m.TR.values() if T.get("t")) / 10)
    PL = set(m.PL)
    hit = {1: collections.Counter(), 2: collections.Counter()}; died = {1: [], 2: []}
    for e in m.o.get("ev") or []:
        if e[0] is None: continue
        if e[1] == "dm" and e[3] in PL and e[2] in PL and m.team(e[2]) != m.team(e[3]) and len(e) > 5 and isinstance(e[5], (int, float)): hit[m.team(e[3])][int(e[0] / 10)] += e[5]
        elif e[1] == "dt" and e[2] in PL: died[m.team(e[2])].append(e[0] / 10)
    out = {"rid": rid, "ok": True, "rows": [], "time": collections.Counter()}
    for tm in (1, 2):
        ids = [a for a in m.PL if m.team(a) == tm]
        mk, md = E.monks(ids), E.midline(ids)
        for t in range(60, end - 20, 10):
            g = E.group(mk, t)
            for a in mk + md:
                x = E.at(a, t)
                if x: out["time"][(E.kind(a), x["out"])] += 1
            if not g or not g["n"]: continue
            g2 = E.group(mk, t + 10)
            took = sum(hit[tm][u] for u in range(t, t + 10))
            out["rows"].append((g["mean"], g["low"], g["n"], (g2["mean"] - g["mean"]) if g2 and g2["n"] == g["n"] else None, took, int(any(t < d <= t + 20 for d in died[tm]))))
    out["time"] = {f"{k[0]}|{k[1]}": v for k, v in out["time"].items()}
    return out


if __name__ == "__main__":
    import sys, json, subprocess
    a = sys.argv[1:]
    if a and a[0] == "cover":
        import multiprocessing, common
        ids = common.replay_ids()
        with multiprocessing.Pool(int(a[a.index("--jobs") + 1]) if "--jobs" in a else 2) as pool: res = pool.map(_check, ids, chunksize=8)
        bad = [r for r in res if "error" in r]; ok = [r for r in res if r.get("ok")]
        print(f"{len(ids)} counted matches: {len(ok)} with gvg.report's energy, {len(res) - len(ok) - len(bad)} without (blank, R-672), {len(bad)} that could not be read")
        rows = [x for r in ok for x in r["rows"]]
        tm = collections.Counter()
        for r in ok: tm.update(r["time"])
        for k in ("monk", "midline"):
            tot = sum(v for kk, v in tm.items() if kk.startswith(k + "|")) or 1
            print(f"  a {k} player is out (under {OUT_MONK if k == 'monk' else OUT_MIDLINE} on the double high scale): for certain {100 * tm[k + '|yes'] / tot:.1f}% of his time alive, possibly {100 * tm[k + '|maybe'] / tot:.1f}%")
        mean = lambda v: sum(v) / len(v) if v else float("nan")
        print(f"  a team's backline monks, read every 10 s from 1:00 ({len(rows):,} readings): average {mean([x[0] for x in rows]):.1f}, the lowest monk {mean([x[1] for x in rows]):.1f}")
        fire, rest = [x[3] for x in rows if x[3] is not None and x[4] >= FIRE], [x[3] for x in rows if x[3] is not None and x[4] == 0]
        print(f"  E1, energy falls under fire and comes back at rest: over the next 10 s a team's monks change by {mean(fire):+.1f} when it takes {FIRE} or more in hits ({len(fire):,}) and by {mean(rest):+.1f} when it takes none ({len(rest):,}): {'HOLDS' if mean(fire) < 0 < mean(rest) else 'DOES NOT HOLD'}")
        print("  E2, a death on the team in the next 20 s, by its monks' average and by its lowest monk:")
        for name, i in (("average", 0), ("lowest monk", 1)):
            cells = []
            for lo_, hi_ in ((0, 20), (20, 30), (30, 40), (40, 50), (50, 60), (60, 200)):
                v = [x[5] for x in rows if lo_ <= x[i] < hi_]
                cells.append(f"{lo_}-{hi_ if hi_ < 200 else ''}: {100 * mean(v):.0f}% ({len(v):,})" if v else f"{lo_}-{hi_}: none")
            print(f"     {name:12} " + "; ".join(cells))
        for r in bad[:10]: print("  " + r["rid"][:8], r["error"])
        sys.exit(1 if bad else 0)
    elif a:
        from replaylib import Match
        import common
        idx = json.loads(subprocess.check_output(["git", "-C", common.REPO, "show", "origin/replays:index.json"]))["matches"]
        rid = next(r for r in idx if r.startswith(a[0]))
        m = Match.from_branch(rid); E = m.energy()
        print(" v ".join(idx[rid]["teams"]), "| energy", "read" if E.ok else "not in gvg.report's record: blank (R-672)")
        if E.ok:
            end = int(max(T["t"][-1] for T in m.TR.values() if T.get("t")) / 10)
            for b in sorted(m.PL, key=lambda b: (m.team(b), m.A[b].get("slot") or 0)):
                if E.kind(b) is None: continue
                xs = [x for x in (E.at(b, t) for t in range(60, end, 10)) if x]
                if not xs: continue
                mids = sorted(x["mid"] for x in xs)
                print(f"  {m.role(b):20} {E.kind(b):8} middle {mids[len(mids) // 2]:5.1f}  lowest tenth {mids[len(mids) // 10]:5.1f}  out for certain {100 * sum(x['out'] == 'yes' for x in xs) / len(xs):4.1f}%  possibly {100 * sum(x['out'] == 'maybe' for x in xs) / len(xs):4.1f}%  bounds within 2: {100 * sum(x['hi'] - x['lo'] <= 2 for x in xs) / len(xs):3.0f}%")
    else: print(__doc__)
