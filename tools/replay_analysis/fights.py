"""Fight-level episodes: deaths (what happened in the 15 s before), monk profiles (casting, reaction, spacing),
numbers windows (who had more players in the main fight, why, and what they did with it) and team posture (offensive
or defensive against the situation).

Usage:  python3 fights.py <report id> [deaths] [monks] [windows] [posture]
In code: deaths(st), monks(st), windows(st), posture(st) -> lists of dicts (written by analyze.py)."""
import collections, json, math, os, statistics, sys
from replaylib import Match
from state import GameState, d, PIT_R, NEAR_R, REPO

PRE = 15                  # seconds looked at before a death
CAST_R = 1250             # about spell range
SPIKE = (250, 2)          # damage, seconds: a burst a monk should react to

_SK = None
def skill_kind(sid, name=""):
    """heal, prot, removal or other, from the skill data (attribute and what the skill removes)."""
    global _SK
    if _SK is None:
        data = json.load(open(os.path.join(REPO, "data", "skills.json")))
        rows = data["skills"] if isinstance(data, dict) and "skills" in data else data
        _SK = {}
        for s in (rows.values() if isinstance(rows, dict) else rows):
            k = "other"
            if s["name"].startswith(("Infuse Health", "Shield of Absorption", "Protective Spirit", "Reversal of Fortune")): k = "prot"
            elif s["attr"] == "Protection Prayers": k = "removal" if s.get("removes") and s["type"] == "Spell" else "prot"
            elif s["attr"] in ("Healing Prayers", "Divine Favor") or "Heal" in s["name"]: k = "removal" if s.get("removes") and "Hex" in s["name"] else "heal"
            elif s.get("removes"): k = "removal"
            _SK[s["id"]] = k
            _SK[s["name"]] = k
    return _SK.get(sid) or _SK.get(name) or _SK.get(name + " (PvP)") or "other"


def _monks(st, tm): return [a for a in st.players[tm] if st.m.A[a].get("p") == "Monk" and st.m.A[a].get("slot") in (6, 7, 8)]


def _casts(st):
    """Monk-relevant casts: [(t, caster, target, skill id, name, kind, finished?)]."""
    m, out = st.m, []
    starts = [r for r in m.o["ev"] if r[1] == "cs" and r[2] in m.PL]
    for r in starts:
        nm = m.sk(r[4]) if r[4] else ""
        out.append((r[0] / 10, r[2], r[3], r[4], nm, skill_kind(r[4], nm)))
    return out


def deaths(st):
    m, out = st.m, []
    casts = st.__dict__.setdefault("_casts", _casts(st))
    kd = m.o.get("knockdowns", []); ir = m.o.get("interrupts", [])
    for a in m.PL:
        for td in st.death_times.get(a, []):
            if td >= st.end - 1: continue
            tm, foe = m.team(a), 3 - m.team(a)
            t0 = td - PRE
            hits = [r for r in m.o["ev"] if r[1] == "dm" and r[3] == a and t0 * 10 <= r[0] <= td * 10 and (r[5] or 0) > 0]
            src = collections.Counter(); kinds = collections.Counter()
            for r in hits:
                src[m.role(r[2]) if r[2] is not None else "?"] += r[5]; kinds[r[6] or "?"] += r[5]
            # tightest burst
            best = 0
            for r in hits:
                w = sum(h[5] for h in hits if r[0] <= h[0] <= r[0] + 20)
                best = max(best, w)
            first_big = next((r[0] / 10 for r in hits if sum(h[5] for h in hits if r[0] <= h[0] <= r[0] + 20) >= 200), None)
            monks = _monks(st, tm)
            p_end = st.pos(a, td - 1)[0]
            monk_dist = {m.roles[b]: round(d(st.pos(b, td - 1)[0], p_end)) for b in monks if b != a and st.alive(b, td - 1)}
            main = st.main_group(tm, int(t0 + 5))
            mc = st.centroid(main, int(t0 + 5))
            isolated = d(st.pos(a, int(t0 + 5))[0], mc) > 2000 if a not in main else False
            own_casts = [(round(c[0] - (first_big or td), 1), m.roles[c[1]], c[4]) for c in casts
                         if c[2] == a and c[1] in monks and t0 <= c[0] <= td and c[5] in ("prot", "heal")]
            monk_busy = {}
            for b in monks:
                if b == a: continue
                cs = [c for c in casts if c[1] == b and (first_big or td) - 3 <= c[0] <= td and c[2] is not None]
                monk_busy[m.roles[b]] = [f"{c[4]}->{m.roles.get(c[2], m.nm(c[2]))}" for c in cs][:6]
            kds = [(round(r[0] / 10 - td, 1), m.roles.get(r[1])) for r in kd if r[2] == a and t0 * 10 <= r[0] <= td * 10]
            irs_t = [(round(r[0] / 10 - td, 1), m.roles.get(r[1]), m.sk(r[4])) for r in ir if r[3] == a and t0 * 10 <= r[0] <= td * 10]
            irs_m = [(round(r[0] / 10 - td, 1), m.roles.get(r[3]), m.sk(r[4])) for r in ir if r[3] in monks and t0 * 10 <= r[0] <= td * 10]
            attackers = {r[2] for r in hits if r[2] in m.PL}
            peel = sum(1 for r in m.o["ev"] if r[1] == "dm" and r[2] in st.players[tm] and r[3] in attackers and t0 * 10 <= r[0] <= td * 10)
            res = st.next_res(td)
            after_time = (td % 120) <= 15
            # what the enemy did with the death in the next 60 s
            npc = [st.geo.npcs[x]["kind"] for x, tt in st.npc_dead.items() if x in st.geo.npcs and st.geo.npcs[x]["team"] == tm and td <= tt <= td + 60]
            more = sum(1 for b in st.players[tm] for tt in st.death_times.get(b, []) if td < tt <= td + 60)
            caps = [m.tag[c] for tt, c in st.caps if td <= tt <= td + 60]
            out.append({
                "t": round(td), "team": m.tag[tm], "victim": m.roles[a], "zone": st.zone(a, td - 1), "after_time": after_time,
                "down_for": round(res - td), "burst_max_2s": round(best), "first_big_hit": round(first_big - td, 1) if first_big else None,
                "damage_by": {k: round(v) for k, v in src.most_common(5)}, "damage_kind": {k: round(v) for k, v in kinds.items()},
                "knockdowns": kds, "interrupts_on_victim": irs_t, "interrupts_on_monks": irs_m,
                "monk_casts_on_victim": own_casts, "monks_busy_with": monk_busy, "monk_distance": monk_dist,
                "isolated": isolated, "peel_hits": peel, "numbers": (len(st.main_group(tm, int(td - 2))), len(st.main_group(foe, int(td - 2)))),
                "then": {"npcs_lost_60s": npc, "more_deaths_60s": more, "caps_60s": caps},
            })
    return sorted(out, key=lambda x: x["t"])


def monks(st, phase=120):
    """Per monk per 2-minute phase: casts by kind, top targets, reaction to bursts on allies, idle time while allies were
    hurt, interrupts and knockdowns received, cancelled casts (fakes), distance to the nearest enemy mesmer or ranger."""
    m, out = st.m, []
    casts = st.__dict__.setdefault("_casts", _casts(st))
    dmg = collections.defaultdict(list)
    for r in m.o["ev"]:
        if r[1] == "dm" and r[3] in m.PL and (r[5] or 0) > 0: dmg[r[3]].append((r[0] / 10, r[5]))
    bursts = []      # (t, ally) where ally took SPIKE[0]+ in SPIKE[1] s
    for a, L in dmg.items():
        last = -99
        for i, (t, _) in enumerate(L):
            tot = sum(x for tt, x in L[i:] if tt <= t + SPIKE[1])
            if tot >= SPIKE[0] and t - last > 5: bursts.append((t, a)); last = t
    stopped = [r for r in m.o["ev"] if r[1] == "cx"]
    irs = m.o.get("interrupts", []); kds = m.o.get("knockdowns", [])
    for tm in st.teams:
        foes_shut = [b for b in st.players[3 - tm] if m.A[b].get("p") in ("Mesmer", "Ranger")]
        for b in _monks(st, tm):
            for p0 in range(0, st.end, phase):
                p1 = min(p0 + phase, st.end)
                alive = sum(1 for t in range(p0, p1) if st.alive(b, t))
                if alive < 10: continue
                mine = [c for c in casts if c[1] == b and p0 <= c[0] < p1]
                kinds = collections.Counter(c[5] for c in mine)
                tg = collections.Counter(m.roles.get(c[2], "self" if c[2] == b else "other") for c in mine if c[2] is not None)
                react = []
                for t, a in bursts:
                    if not (p0 <= t < p1) or m.team(a) != tm or not st.alive(b, t): continue
                    if d(st.pos(b, t)[0], st.pos(a, t)[0]) > CAST_R: continue
                    first = next((c[0] - t for c in mine if c[2] == a and c[5] in ("prot", "heal") and t - 1 <= c[0] <= t + 4), None)
                    react.append(round(first, 1) if first is not None else None)
                idle_hurt = 0
                for t in range(p0, p1):
                    _, s = st.pos(b, t)
                    if not s or not m.alive(s) or s["st"] not in ("i", "m"): continue
                    if any(m.team(a) == tm and abs(tt - t) <= 1 and d(st.pos(a, t)[0], st.pos(b, t)[0]) < CAST_R for tt, a in bursts): idle_hurt += 1
                fakes = sum(1 for r in stopped if r[2] == b and p0 * 10 <= r[0] < p1 * 10
                            and not any(i[3] == b and abs(i[0] - r[0]) <= 3 for i in irs))
                spacing = []
                for t in range(p0, p1, 3):
                    p = st.pos(b, t)[0]
                    if not p or not st.alive(b, t): continue
                    ds = [d(p, st.pos(f, t)[0]) for f in foes_shut if st.alive(f, t)]
                    if ds: spacing.append(min(ds))
                caught = [x for x in react if x is not None]
                out.append({
                    "team": m.tag[tm], "monk": m.roles[b], "phase": f"{p0 // 60}-{p1 // 60} min", "alive_s": alive,
                    "casts_per_min": round(len(mine) / alive * 60, 1), "kinds": dict(kinds), "top_targets": tg.most_common(4),
                    "bursts_in_range": len(react), "answered": len(caught), "median_reaction": round(statistics.median(caught), 1) if caught else None,
                    "idle_while_ally_hurt_s": idle_hurt, "fakes": fakes,
                    "interrupted": sum(1 for i in irs if i[3] == b and p0 * 10 <= i[0] < p1 * 10),
                    "knocked_down": sum(1 for k in kds if k[2] == b and p0 * 10 <= k[0] < p1 * 10),
                    "median_dist_to_enemy_mes_or_ranger": round(statistics.median(spacing)) if spacing else None,
                })
    return out


def windows(st, min_len=10):
    """Stretches where one team had more players in the main fight (both mains within 2,500 of each other)."""
    m, out = st.m, []
    cur = None
    def numbers(t):
        a, b = st.main_group(1, t), st.main_group(2, t)
        ca, cb = st.centroid(a, t), st.centroid(b, t)
        return (len(a), len(b)) if d(ca, cb) < 2500 else None
    for t in range(0, st.end + 1):
        n = numbers(t)
        adv = None if not n or n[0] == n[1] else (1 if n[0] > n[1] else 2)
        if adv and cur and cur["adv"] == adv and t - cur["last"] <= 2:
            cur["last"] = t; cur["n"].append(n)
        else:
            if cur and cur["last"] - cur["start"] >= min_len: out.append(cur)
            cur = {"adv": adv, "start": t, "last": t, "n": [n]} if adv else None
    if cur and cur["last"] - cur["start"] >= min_len: out.append(cur)
    res = []
    for w in out:
        tm, foe, t0, t1 = w["adv"], 3 - w["adv"], w["start"], w["last"]
        # why the other side was short: its players away (carrying, splitting, dead)
        why = collections.Counter()
        for t in range(t0, t1 + 1, 3):
            main = st.main_group(foe, t); car = set(st.carrier(t))
            for b in st.players[foe]:
                if b in main: continue
                why["dead" if not st.alive(b, t) else ("running flag" if b in car else st.zone(b, t))] += 1
        dmg = sum(r[5] or 0 for r in m.o["ev"] if r[1] == "dm" and r[2] in st.players[tm] and r[3] in st.players[foe] and t0 * 10 <= r[0] <= t1 * 10)
        base = sum(r[5] or 0 for r in m.o["ev"] if r[1] == "dm" and r[2] in st.players[tm] and r[3] in st.players[foe]) / st.end
        kills = [(round(tt), m.roles[b]) for b in st.players[foe] for tt in st.death_times.get(b, []) if t0 <= tt <= t1 + 5]
        losses = [(round(tt), m.roles[b]) for b in st.players[tm] for tt in st.death_times.get(b, []) if t0 <= tt <= t1 + 5]
        c0 = st.centroid(st.main_group(tm, t0), t0); c1 = st.centroid(st.main_group(tm, t1), t1)
        moved = round(d(c0, st.geo.pit[foe]) - d(c1, st.geo.pit[foe])) if c0 and c1 else None
        res.append({"team": m.tag[tm], "start": t0, "end": t1, "secs": t1 - t0,
                    "numbers": collections.Counter(f"{a}v{b}" if tm == 1 else f"{b}v{a}" for a, b in w["n"]).most_common(2),
                    "enemy_short_because": dict(why.most_common(3)), "pressure_vs_avg": round(dmg / max(t1 - t0, 1) / max(base, 1), 2),
                    "kills": kills, "losses": losses, "pushed_toward_enemy_pit": moved})
    return res


def posture(st, step=30):
    """Every 30 s: how far forward each team's main group is (0 = own pit, 1 = enemy pit) and the situation (numbers,
    morale, stand, NPCs), so offensive play in a bad situation stands out."""
    m, out = st.m, []
    for t in range(0, st.end + 1, step):
        s = st.at(t)
        row = {"t": t}
        for tm in st.teams:
            c = st.centroid(st.main_group(tm, t), t)
            a, b = d(c, st.geo.pit[tm]), d(c, st.geo.pit[3 - tm])
            fwd = round(a / (a + b), 2) if c else None
            x = s[m.tag[tm]]
            row[m.tag[tm]] = {"forward": fwd, "alive": x["alive"], "main": x["main"],
                              "morale_sum": sum(x["morale"].values()), "npcs": x["pit_npcs"]}
        row["stand"] = s["stand"]["owner"]
        out.append(row)
    return out


def show(st, what):
    m = st.m; f = lambda t: m.f(int(t * 10))
    if "deaths" in what:
        print("== deaths")
        for x in deaths(st):
            print(f"{f(x['t'])} {x['team']} {x['victim']} at {x['zone']}{' AFTER TIME' if x['after_time'] else ''} (down {x['down_for']} s)"
                  f" | burst {x['burst_max_2s']} in 2 s | {x['numbers'][0]}v{x['numbers'][1]} | isolated {x['isolated']} | peel hits {x['peel_hits']}")
            print(f"    damage {x['damage_by']} | KDs {x['knockdowns']} | interrupts on victim {x['interrupts_on_victim']}")
            print(f"    own monk casts on victim {x['monk_casts_on_victim']} | interrupts on monks {x['interrupts_on_monks']}")
            print(f"    monks busy with {x['monks_busy_with']} | monk distance {x['monk_distance']} | then {x['then']}")
    if "monks" in what:
        print("== monks (per 2 minutes)")
        for x in monks(st):
            print(f"{x['team']} {x['monk']:7} {x['phase']:9} {x['casts_per_min']:5}/min {x['kinds']} | bursts {x['answered']}/{x['bursts_in_range']}"
                  f" react {x['median_reaction']} s | idle while hurt {x['idle_while_ally_hurt_s']} s | fakes {x['fakes']} | int {x['interrupted']}"
                  f" KD {x['knocked_down']} | to mes/ranger {x['median_dist_to_enemy_mes_or_ranger']}")
    if "windows" in what:
        print("== numbers windows")
        for x in windows(st):
            print(f"{x['team']} up {f(x['start'])}-{f(x['end'])} ({x['secs']} s) {x['numbers']} | enemy short: {x['enemy_short_because']}"
                  f" | pressure x{x['pressure_vs_avg']} | kills {x['kills']} | losses {x['losses']} | pushed {x['pushed_toward_enemy_pit']}")
    if "posture" in what:
        print("== posture (forward: 0 own pit, 1 enemy pit)")
        for x in posture(st):
            print(f"{f(x['t'])} " + " | ".join(f"{k}: fwd {v['forward']} up {v['alive']} main {v['main']} morale {v['morale_sum']} {v['npcs']}"
                                               for k, v in x.items() if isinstance(v, dict)) + f" | stand {x['stand']}")


if __name__ == "__main__":
    st = GameState(Match.from_branch(sys.argv[1]))
    show(st, sys.argv[2:] or ("deaths", "monks", "windows", "posture"))
