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


def regen(ids=None):
    """Lord regeneration (lord.py; Denning: 10 per second always, plus out-of-combat regeneration from +2 to +10 per
    second once the Lord hasn't been hit for a few seconds). Measured here: the delay before the out-of-combat part
    starts and how many seconds each +2 step takes, as the pair that best puts the rebuilt health (no floor at 0) at 0
    when Lords die, without any surviving Lord's health reaching 0. Lords whose damage wasn't observed are skipped."""
    from lord import LordState, simulate
    cases = []
    for rid in ids or match_ids():
        st = GameState(Match.from_branch(rid)); L = LordState(st)
        for tm in (1, 2):
            if 3 - tm in L.unobserved or not L.ev[tm]: continue
            cases.append({"ev": L.ev[tm], "base": L.base_hp[tm], "dead": L.dead[tm], "end": st.end})
    def score(delay, ramp, cap):
        err, contra = [], 0
        for c in cases:
            S = simulate(c["ev"], c["base"], c["end"], delay, ramp, floor=False, cap=cap)
            if c["dead"] is not None: err.append(abs(S[min(int(c["dead"]), len(S) - 1)]))
            elif min(S) <= 0: contra += 1
        err.sort()
        return (round(err[len(err) // 2]) if err else None), contra, len(err)
    res = {(dl, rp, cap): score(dl, rp, cap) for dl in (2, 3, 4, 5, 6, 8, 10, 12, 15, 20) for rp in (1, 2, 3, 4, 6) for cap in (False, True)}
    ok = [k for k in res if res[k][1] == 0] or list(res)
    best = min(ok, key=lambda k: res[k][0])
    out = {"about": regen.__doc__.strip() + " Also tried: applying the Amulet of Protection cap to the recorded damage "
           "(if gvg.report records damage before the cap) or not (after).", "delay_s": best[0], "ramp_s": best[1],
           "amulet_cap_applied": best[2], "deaths_used": res[best][2],
           "surviving_lords": sum(1 for c in cases if c["dead"] is None), "median_error_at_death": res[best][0],
           "grid": {f"delay {k[0]} s, step {k[1]} s, cap {'applied' if k[2] else 'not applied'}": {"median_error": v[0], "survivors_contradicted": v[1]} for k, v in res.items()}}
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
