"""Episodes: the situations a match is made of, each with who was involved, the response, the outcome and the cost.
Built on state.GameState. So far: splits and flag runs (plus the stand ledger).

Usage:  python3 episodes.py <report id> [splits] [flags]
In code: splits(st), flag_runs(st), stand_ledger(st) -> lists of dicts (also written by analyze.py).

Split = players away from their team's main group on the enemy half or in the enemy base, not carrying a flag.
Response = enemy players who came within DEFEND_R of a splitter for 5 s or more: who, role, when (latency from the
splitter entering the enemy base), and whether they came from the enemy's main group (a collapse) or were already in base.
Flag run = a carry from pickup to cap or drop: escort, pushers (enemies who damaged, snared, knocked down or interrupted
the carrier), who came back to help and how fast, and what the main fight was doing meanwhile."""
import collections, math, sys
from replaylib import Match
from state import GameState, d, PIT_R, BASE_R, NEAR_R

SPLIT_FAR = 2500       # away from own main group
DEFEND_R = 1500
SNARES = {"crippled", "dazed"}
FRONTLINE = {"Warrior", "Dervish", "Assassin"}


def line(m, a):
    """Denning: frontline = dervishes, warriors, melee assassins; midline = elementalists, rangers, paragons, mesmers,
    caster assassins (and ritualists, to confirm); backline = monks. Decided by build, not profession alone."""
    p = m.A[a].get("p")
    if p == "Monk": return "backline"
    if p in ("Warrior", "Dervish"): return "frontline"
    if p == "Assassin":
        bar = " ".join(m.sk(b) for b in m.A[a].get("bar", []) if b)
        return "frontline" if any(w in bar for w in ("Strike", "Blossom", "Fang", "Jagged", "Wild Blow", "Twisting")) else "midline"
    return "midline"


def _hostile(st, target, t0, t1):
    """Enemy actions on target between t0 and t1 (seconds): [(t, actor, kind, skill)]."""
    m, out = st.m, []
    T0, T1 = t0 * 10, t1 * 10
    for r in m.o["ev"]:
        if not (T0 <= r[0] <= T1) or r[3] != target or r[2] not in m.PL or m.team(r[2]) == m.team(target): continue
        if r[1] == "dm" and (r[5] or 0) > 0: out.append((r[0] / 10, r[2], "damage", r[4]))
    for r in m.o.get("knockdowns", []):
        if T0 <= r[0] <= T1 and r[2] == target and r[1] in m.PL: out.append((r[0] / 10, r[1], "knockdown", r[3]))
    for r in m.o.get("interrupts", []):
        if T0 <= r[0] <= T1 and r[3] == target and r[1] in m.PL: out.append((r[0] / 10, r[1], "interrupt", r[2]))
    for e in m.o.get("effects", []):     # snares (conditions) on the target, from the effects intervals
        if e[2] == "c" and e[5] == target and e[0] is not None and T0 <= e[0] <= T1 and (e[7] or "") in SNARES \
                and e[4] in m.PL and m.team(e[4]) != m.team(target):
            out.append((e[0] / 10, e[4], "snare:" + e[7], e[3]))
    return sorted(out)


def splits(st, min_len=15):
    m, out = st.m, []
    for tm in st.teams:
        cur = None
        for t in range(0, st.end + 1):
            main = st.main_group(tm, t)
            c = st.centroid(main, t)
            carriers = set(st.carrier(t))
            away = []
            for a in st.players[tm]:
                if a in main or a in carriers: continue
                p, s = st.pos(a, t)
                if not p or not m.alive(s): continue
                enemy_half = d(p, st.geo.pit[3 - tm]) < d(p, st.geo.pit[tm])
                if enemy_half and d(p, c) > SPLIT_FAR: away.append(a)
            if away:
                if not (cur and t - cur["last"] <= 5):
                    if cur: out.append(cur)
                    cur = {"team": tm, "start": t, "last": t, "members": collections.Counter(), "secs": []}
                cur["last"] = t; cur["secs"].append((t, away))
                for a in away: cur["members"][a] += 1
        if cur: out.append(cur)
    eps = [e for e in out if e["last"] - e["start"] >= min_len]
    res = []
    for e in eps:
        # a flank of the main fight is not a split: splitters stay near the enemy's main group most of the time
        dist = []
        for t, aw in e["secs"][::3]:
            c = st.centroid(st.main_group(3 - e["team"], t), t)
            dist.append(min(d(st.pos(a, t)[0], c) for a in aw))
        far = sum(1 for x in dist if x > SPLIT_FAR) / max(len(dist), 1)
        det = _split_detail(st, e)
        det["kind"] = "split" if far >= 0.5 or det["entered_base"] is not None else "flank"
        # Denning: when (nearly) the whole enemy team turns on the group, it's a full team collapse, not a split answer
        if len(det["defenders"]) >= 6 and sum(1 for x in det["defenders"] if x["came"] == "collapse from main") >= 4:
            det["kind"] = "full team collapse"
        res.append(det)
    return res


def _split_detail(st, e):
    m, tm = st.m, e["team"]
    foe = 3 - tm
    members = [a for a, n in e["members"].most_common() if n >= 0.3 * (e["last"] - e["start"])] or [e["members"].most_common(1)[0][0]]
    t0, t1 = e["start"], e["last"]
    # entering the enemy base
    entered = next((t for t, aw in e["secs"] if any(d(st.pos(a, t)[0], st.geo.base[foe]) < BASE_R
                                                    or d(st.pos(a, t)[0], st.geo.pit[foe]) < PIT_R for a in aw)), None)
    ref = entered if entered is not None else t0
    # defenders and collapses
    near_secs = collections.Counter()
    first_near = {}
    for t in range(t0, t1 + 1):
        sp = [st.pos(a, t)[0] for a in members]
        for b in st.players[foe]:
            p, s = st.pos(b, t)
            if not p or not m.alive(s): continue
            if min(d(p, q) for q in sp) < DEFEND_R:
                near_secs[b] += 1; first_near.setdefault(b, t)
    defenders = []
    for b, n in near_secs.items():
        if n < 5: continue
        ft = first_near[b]
        before = max(ft - 20, 0)
        was_main = b in st.main_group(foe, before)
        in_base = st.zone(b, before) in ("own pit", "own base")
        defenders.append({"who": m.role(b), "role": m.roles[b], "first": ft, "latency": ft - ref, "secs": n,
                          "came": "collapse from main" if was_main and not in_base else ("already in base" if in_base else "from field")})
    defenders.sort(key=lambda x: x["first"])
    # what the split did
    npc_dmg = collections.Counter(); kills = []
    pdmg = collections.Counter()
    for r in m.o["ev"]:
        if not (t0 * 10 <= r[0] <= (t1 + 2) * 10) or r[2] not in members: continue
        if r[1] == "dm" and isinstance(r[3], int) and r[3] < len(m.A):
            tgt = m.A[r[3]]
            if tgt.get("npc"): npc_dmg[tgt["npc"]] += r[5] or 0
            elif tgt.get("player") and m.team(r[3]) == foe: pdmg[m.roles[r[3]]] += r[5] or 0
    for a, tdead in st.npc_dead.items():
        v = st.geo.npcs.get(a)
        if v and v["team"] == foe and t0 <= tdead <= t1 + 2:
            dfn = [x["role"] for x in defenders if x["first"] <= tdead]
            kills.append({"npc": v["kind"] + ("" if v.get("pit") else " (outside)"), "t": round(tdead), "defenders_present": dfn})
    deaths = [(m.roles[a], round(t)) for a in members for t in st.death_times.get(a, []) if t0 <= t <= t1 + 2]
    # cost at main while the split ran
    nums = [(len(st.main_group(tm, t)), len(st.main_group(foe, t))) for t in range(t0, t1 + 1, 5)]
    avg = (round(sum(x for x, _ in nums) / len(nums), 1), round(sum(y for _, y in nums) / len(nums), 1)) if nums else None
    return {"team": m.tag[tm], "start": t0, "end": t1, "members": [m.roles[a] for a in members], "entered_base": entered,
            "defenders": defenders, "npc_damage": {k: round(v) for k, v in npc_dmg.items()}, "player_damage": {k: round(v) for k, v in pdmg.items()},
            "npc_kills": kills, "deaths": deaths, "main_numbers": avg}


def flag_runs(st):
    m, out = st.m, []
    for c in st.carries:
        if c["e"] <= 0: continue
        a, tm = c["a"], m.team(c["a"])
        s, e = max(c["s"], 0), c["e"]
        hostile = _hostile(st, a, s, e)
        pushers = collections.OrderedDict()
        for t, b, kind, sk in hostile:
            pushers.setdefault(m.roles[b], {"first": round(t), "actions": collections.Counter()})["actions"][kind] += 1
        first_push = hostile[0][0] if hostile else None
        escort, helpers = [], []
        steps = [s + i for i in range(int(e - s) + 1)] or [s]
        for b in st.players[tm]:
            if b == a: continue
            near = [t for t in steps if d(st.pos(b, t)[0], st.pos(a, t)[0]) < NEAR_R and st.alive(b, t)]
            if len(near) >= 0.5 * len(steps): escort.append(m.roles[b])
            elif first_push is not None and st.alive(b, first_push) and d(st.pos(b, first_push)[0], st.pos(a, first_push)[0]) > 2500:
                # help = a teammate who was far away when the push started and reached the carrier within 30 s
                came = [t for t in near if first_push <= t <= first_push + 30]
                if came: helpers.append({"role": m.roles[b], "latency": round(came[0] - first_push)})
        died = any(s <= t <= e + 1 for t in st.death_times.get(a, []))
        nums = [(len(st.main_group(tm, t)), len(st.main_group(3 - tm, t))) for t in steps[::5]]
        hp = [st.pos(a, t)[1]["hp"] for t in steps if st.pos(a, t)[1]]
        role = m.roles[a]
        out.append({"team": m.tag[tm], "runner": role, "line": line(m, a),
                    "start": round(s), "end": round(e), "secs": round(e - s), "outcome": "died" if died else c["how"].replace("flagstand_", "").replace("flag_", ""),
                    "min_hp": min(hp) if hp else None, "escort": escort, "pushers": {k: {"first": v["first"], "actions": dict(v["actions"])} for k, v in pushers.items()},
                    "first_push": round(first_push) if first_push is not None else None, "helpers": helpers,
                    "main_numbers": (round(sum(x for x, _ in nums) / len(nums), 1), round(sum(y for _, y in nums) / len(nums), 1)) if nums else None})
    # double running: a teammate picks up within 15 s of a drop, or two teammates carrying at once
    for i, r in enumerate(out):
        # half running: a teammate takes over within 15 s of this drop; full running: a teammate carries at the same time
        mates = [o for o in out if o is not r and o["team"] == r["team"] and o["runner"] != r["runner"]]
        half = any(r["outcome"] == "dropped" and 0 <= o["start"] - r["end"] <= 15 for o in mates)
        full = any(o["start"] < r["end"] and r["start"] < o["end"] for o in mates)
        r["double"] = "half" if half else ("full" if full else None)
    return out


def flag_cycles(st):
    """Flag timing (Denning: in the flag game, cap as soon as reasonably possible after the enemy). For every cap, the
    other team's answer: when it picked up its next flag compared with the enemy's pickup (positive = later), how long
    after the enemy's cap it capped, and the runner's trip back to base after its own previous cap (how long, and
    whether enemies stood in the way)."""
    m, out = st.m, []
    picks = [(t / 10, m.team(a), a) for t, typ, a in m.o.get("flags", []) if typ == "flag_picked_up" and m.team(a)]
    caps = [(t, tm, None) for t, tm in st.caps]
    capper = {round(t / 10): a for t, typ, a in m.o.get("flags", []) if typ == "flagstand_captured"}
    for i, (tc, tm, _) in enumerate(caps):
        foe = 3 - tm
        nxt = next((t for t, x, _ in caps[i + 1:] if x == foe), None)
        my_pick = next((t for t, x, a in picks if x == tm and t > (caps[i - 1][0] if i else -1e9) and t <= tc), None)
        foe_pick = next((t for t, x, a in picks if x == foe and t > tc - 60 and (nxt is None or t <= nxt)), None)
        prev_foe_cap = max((t for t, x, _ in caps[:i + 1] if x == foe), default=None)
        row = {"team": m.tag[foe], "enemy_cap": round(tc), "enemy": m.tag[tm], "own_next_cap": round(nxt) if nxt else None,
               "cap_delay": round(nxt - tc) if nxt else None,
               "own_pickup": round(foe_pick) if foe_pick else None,
               "pickup_vs_enemy_pickup": round(foe_pick - my_pick) if foe_pick and my_pick else None}
        # the runner's trip back to base after its own previous cap, and enemies in the way
        if prev_foe_cap is not None and foe_pick:
            r = capper.get(round(prev_foe_cap))
            if r is not None and m.team(r) == foe:
                trip = [t for t in range(int(prev_foe_cap), int(foe_pick))]
                blocked = collections.Counter(m.roles[e] for t in trip[::2] for e in st.players[tm]
                                              if st.alive(e, t) and d(st.pos(e, t)[0], st.pos(r, t)[0]) < NEAR_R)
                row.update(runner=m.roles[r], trip_s=len(trip), enemies_in_the_way=dict(blocked.most_common(4)))
        # full running: was a second runner already waiting near its base when the team capped?
        cap_team = tm
        if capper.get(round(tc)) is not None:
            c_a = capper[round(tc)]
            ready = [m.roles[b] for b in st.players[cap_team] if b != c_a and st.alive(b, tc)
                     and d(st.pos(b, tc)[0], st.geo.base[cap_team]) < BASE_R]
            row["capper"] = m.roles[c_a]
            row["capping_team_next_runner_waiting"] = ready
        out.append(row)
    return out


def stand_ledger(st):
    m, out = st.m, []
    caps = st.caps + [(st.end, None)]
    for (t, tm), (t2, _) in zip(caps, caps[1:]):
        held = t2 - t
        out.append({"team": m.tag[tm], "from": round(t), "to": round(t2), "held": round(held), "boosts": int(held // 120),
                    "short_of_boost": round(120 - held % 120) if held % 120 >= 90 else None})
    return out


def show(st, what=("splits", "flags")):
    m = st.m; f = lambda t: m.f(int(t * 10)) if t is not None else "-"
    if "splits" in what:
        print("== splits")
        for e in splits(st):
            if e["kind"] != "split": continue
            print(f"{e['team']} {f(e['start'])}-{f(e['end'])} {'+'.join(e['members'])} | in base {f(e['entered_base'])} | main "
                  f"{e['main_numbers'][0]} v {e['main_numbers'][1]} meanwhile")
            for x in e["defenders"]:
                print(f"    answered by {x['who']} at {f(x['first'])} ({x['latency']:+} s from entering), {x['came']}, {x['secs']} s near")
            if not e["defenders"]: print("    NOT ANSWERED")
            if e["npc_kills"]: print("    killed:", ", ".join(f"{k['npc']} {f(k['t'])} (defenders: {','.join(k['defenders_present']) or 'none'})" for k in e["npc_kills"]))
            if e["npc_damage"]: print("    NPC damage:", e["npc_damage"], "| player damage:", e["player_damage"])
            if e["deaths"]: print("    splitter deaths:", e["deaths"])
    if "flags" in what:
        print("== flag runs")
        for r in flag_runs(st):
            print(f"{r['team']} {r['runner']} ({r['line']}) {f(r['start'])}-{f(r['end'])} {r['secs']} s -> {r['outcome']}"
                  f"{(' DOUBLE ' + r['double']) if r['double'] else ''} | min HP {r['min_hp']}% | escort {','.join(r['escort']) or '-'} | main {r['main_numbers']}")
            for k, v in r["pushers"].items(): print(f"    pushed by {k} from {f(v['first'])}: {v['actions']}")
            for h in r["helpers"]: print(f"    help: {h['role']} +{h['latency']} s")
        print("== flag timing (answer to each enemy cap)")
        for c in flag_cycles(st):
            print(f"  {c['team']} after {c['enemy']}'s cap at {f(c['enemy_cap'])}: picked up {f(c['own_pickup'])} "
                  f"({c['pickup_vs_enemy_pickup']:+} s vs their pickup)" if c['pickup_vs_enemy_pickup'] is not None else f"  {c['team']} after {c['enemy']}'s cap at {f(c['enemy_cap'])}: pickup -",
                  f"| capped {c['cap_delay']} s after" if c['cap_delay'] is not None else "| no cap",
                  f"| runner {c.get('runner')} trip back {c.get('trip_s')} s, in the way: {c.get('enemies_in_the_way')}" if c.get('runner') else "")
        print("== stand")
        for h in stand_ledger(st):
            print(f"  {h['team']} {f(h['from'])}-{f(h['to'])} {h['held']} s, boosts {h['boosts']}" + (f", {h['short_of_boost']} s short" if h["short_of_boost"] else ""))


if __name__ == "__main__":
    st = GameState(Match.from_branch(sys.argv[1]))
    show(st, sys.argv[2:] or ("splits", "flags"))
