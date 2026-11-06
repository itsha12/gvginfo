"""Benchmarks measured from every stored replay, so the engine uses measured values instead of guessed weights.
Rebuild after new replays are fetched; the scoreboard reads the files.

Usage:  python3 benchmarks.py lord        -> data/benchmarks/lord_damage.json
        python3 benchmarks.py regen       -> data/benchmarks/lord_regen.json

lord: Lord damage per second while at the enemy Lord, by profession and by role. "At the Lord" = alive and within
PIT_R + 500 of the enemy Lord's estimated position, in a second when at least one teammate hit the Lord (so time spent
walking past or fighting players in the pit without attacking the Lord doesn't count against a profession). Reported
with seconds and matches behind each number; a value with fewer than MIN_SECS seconds is marked thin."""
import collections, json, os, subprocess, sys
from replaylib import Match
from state import GameState, d
from common import PIT_R, REPO

MIN_SECS = 120
OUT = os.path.join(REPO, "data", "benchmarks")


def match_ids():
    idx = json.loads(subprocess.check_output(["git", "-C", REPO, "show", "origin/replays:index.json"]))["matches"]
    return list(idx)


def lord(ids=None):
    by_prof = collections.defaultdict(lambda: [0.0, 0, set()])     # damage, seconds, matches
    by_role = collections.defaultdict(lambda: [0.0, 0, set()])
    for rid in ids or match_ids():
        m = Match.from_branch(rid); st = GameState(m)
        lords = {m.A[a].get("team"): a for a in range(len(m.A)) if m.A[a].get("npc") == "guild_lord"}
        hits = collections.defaultdict(float)          # (player, second) -> Lord damage
        for r in m.o["ev"]:
            if r[1] == "dm" and r[2] in m.PL and r[3] in lords.values() and m.team(r[2]) != m.A[r[3]].get("team"):
                hits[(r[2], int(r[0] // 10))] += r[5] or 0
        active = collections.defaultdict(set)          # team -> seconds with any Lord hit
        for (a, t) in hits: active[m.team(a)].add(t)
        for a in m.PL:
            tm = m.team(a); pit = st.geo.pit.get(3 - tm)
            if pit is None: continue
            secs = [t for t in sorted(active[tm]) if st.alive(a, t) and d(st.pos(a, t)[0], pit) < PIT_R + 500]
            if not secs: continue
            dmg = sum(hits.get((a, t), 0) for t in secs)
            for key, tab in ((m.A[a].get("p") or "?", by_prof), (m.roles[a].rstrip(" 0123456789").replace("Hammer A", "Hammer").replace("Hammer B", "Hammer"), by_role)):
                tab[key][0] += dmg; tab[key][1] += len(secs); tab[key][2].add(rid)
    fmt = lambda tab: {k: {"dps": round(v[0] / v[1], 1), "seconds": v[1], "matches": len(v[2]), "thin": v[1] < MIN_SECS}
                       for k, v in sorted(tab.items(), key=lambda kv: -kv[1][0] / max(kv[1][1], 1))}
    out = {"about": __doc__.split("\n\n")[2].strip(), "matches": len(ids or match_ids()),
           "by_profession": fmt(by_prof), "by_role": fmt(by_role)}
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(os.path.join(OUT, "lord_damage.json"), "w"), indent=1, ensure_ascii=False)
    return out


def _unclamped(ev, base, rate, delay, end):
    """Lord health without the floor at 0: [(t, health)] after each event (max health capped, regeneration between)."""
    hp, last, t0, out = base, -1e9, 0.0, []
    for t, v in ev:
        start = max(t0, last + delay)
        if rate and t > start: hp = min(base, hp + rate * (t - start))
        hp = min(base, hp + v)
        if v < 0: last = t
        t0 = t; out.append((t, hp))
    return out


def regen(ids=None):
    """Lord natural regeneration, measured: the rate (health per second after lord.REGEN_DELAY s without damage) that
    best puts the rebuilt health at 0 when a Lord dies, without any surviving Lord's health reaching 0. Lords whose
    damage wasn't observed are skipped. Boosts are left out here (at most +10% max health)."""
    from lord import LordState, REGEN_DELAY
    cases = []
    for rid in ids or match_ids():
        st = GameState(Match.from_branch(rid)); L = LordState(st, rate=0)
        for tm in (1, 2):
            if 3 - tm in L.unobserved or not L.ev[tm]: continue
            cases.append({"match": rid, "team": tm, "ev": L.ev[tm], "base": L.base_hp[tm], "dead": L.dead[tm], "end": st.end})
    def score(rate):
        err, contra = [], 0
        for c in cases:
            S = _unclamped(c["ev"], c["base"], rate, REGEN_DELAY, c["end"])
            if c["dead"] is not None:
                at = [h for t, h in S if t <= c["dead"] + 0.5]
                if at: err.append(abs(at[-1]))
            elif min(h for _, h in S) <= 0: contra += 1
        err.sort()
        return (err[len(err) // 2] if err else None), contra, len(err)
    grid = [x / 2 for x in range(0, 61)]
    res = {r: score(r) for r in grid}
    ok = [r for r in grid if res[r][1] == 0] or grid
    best = min(ok, key=lambda r: res[r][0])
    near = [r for r in ok if res[r][0] <= res[best][0] * 1.25 + 25]
    out = {"about": regen.__doc__.strip(), "rate": best, "delay_s": REGEN_DELAY, "plausible_range": [min(near), max(near)],
           "deaths_used": res[best][2], "surviving_lords": sum(1 for c in cases if c["dead"] is None),
           "median_error_at_death": res[best][0], "with_no_regeneration": {"median_error_at_death": res[0][0], "survivors_contradicted": res[0][1]},
           "grid": {str(r): {"median_error": res[r][0], "survivors_contradicted": res[r][1]} for r in grid if r == int(r)}}
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(os.path.join(OUT, "lord_regen.json"), "w"), indent=1)
    return out


if __name__ == "__main__":
    what = sys.argv[1:] or ["lord"]
    if "regen" in what:
        o = regen(); print({k: v for k, v in o.items() if k not in ("grid", "about")})
    what = sys.argv[1:] or ["lord"]
    if "lord" in what:
        o = lord()
        for k, v in o["by_profession"].items(): print(f"  {k:14} {v['dps']:6} dps over {v['seconds']:5} s in {v['matches']:2} matches{' (thin)' if v['thin'] else ''}")
        print("  by role:", {k: v["dps"] for k, v in o["by_role"].items() if not v["thin"]})
