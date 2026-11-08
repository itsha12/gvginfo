"""Why chains for the smaller events (Denning: not only deaths). Each kind answers its own questions with measurements
from forensics.py (placed against every stored match), the analysis files and the node models:

  flag    a team went from up to down on flags: the flag lead before and after; every capture, run and cycle in the
          window with seconds lost against the fastest possible (flag model) and why: runner killed (with the death's
          forensics), dropped, pushed (who, with which control), waiting, slow pick-up; the enemy's capture timing (just
          before a boost?); the fight at the stand (both teams' output, numbers); the cascade after.
  power   a power play (more players at main) that did not kill: numbers through the window; the target team giving
          ground (distance between the groups, retreat speed); own output (damage per second, concentration, dealers,
          uptime lost to moving) against the benchmark; the enemy's healing per second and prots (knockdown immunity
          against own knockdowns); control on the enemy healers; snares put on retreating players; whether the enemy
          regrouped and when.
  spike   a spike (400+ in 3 s) the target survived: who joined it and when each hit landed (spread from first to last,
          share inside 0.5 s and 1 s, waves), compared with spikes that killed and spikes that were saved in every stored
          match; pre-prots up at the first hit; prots and heals during it with timing; defensive control on the spikers;
          the target's set; the target's health line.
  npc     a pit NPC lost: who was in the pit and how long, who defended and from when, the defenders' numbers and
          output, where the rest of the team was and what it was doing (fight, flag, dead).
  split   a split in base and its answer: first defender and latency, who collapsed from main and what main lost
          meanwhile, the split's damage on NPCs and players, how it ended.

Usage:  python3 events.py flag  <report id> <team> <m:ss> [<m:ss end>]
        python3 events.py power <report id> <team> <m:ss>
        python3 events.py spike <report id> <attacking team> <m:ss>
        python3 events.py npc   <report id> <team that lost it> <m:ss>
        python3 events.py split <report id> <splitting team> <m:ss>
        python3 events.py find <kind> [--matches id ...]       the biggest events of that kind (default: every trained match)
        python3 events.py bench                                spike-landing benchmarks (kills against saves)
In code: explain(kind, rid, team, t) -> markdown lines; find(kind, ids) -> [(score, rid, team, t, text)].
<report id> may be its first 8 characters."""
import collections, json, math, os, statistics, subprocess, sys
import forensics as FX
from forensics import Forensics, clock, place, death, bench as fbench
from common import REPO, CAST_R

SPIKE_BENCH = os.path.join(REPO, "data", "benchmarks", "spikes.json")


def _rid(x):
    if len(x) >= 36: return x
    idx = json.loads(subprocess.check_output(["git", "-C", REPO, "show", "origin/replays:index.json"]))["matches"]
    return [k for k in idx if k.startswith(x)][0]


def analysis(rid):
    import cache, analyze
    return cache.prepared("analysis", rid, lambda: analyze.analyze(rid))


def _t(s):
    if isinstance(s, (int, float)): return float(s)
    mm, ss = s.split(":"); return int(mm) * 60 + float(ss)


def _sb(a, t, tag):
    """Scoreboard row (every 5 s) for a team at or before t."""
    rows = [r for r in a["scoreboard"] if r["t"] <= t]
    return (rows[-1] if rows else a["scoreboard"][0])[tag], (rows[-1] if rows else a["scoreboard"][0])


def _fmt(d): return ", ".join(f"{k} {v}" for k, v in d.items() if v not in (None, [], {}))


# ---------------------------------------------------------------- flag swings
SWING_HOLD_S = 15   # a flag deficit counts as real only if it lasts this long or the enemy captures (see _real_low)


def _real_low(rows, j, tag, foe):
    """True if the team's flag lead at rows[j] is a real deficit, not a blip: it stays below -15 s for SWING_HOLD_S or
    more, or the enemy takes the stand within 30 s. Added 2026-11-07 after batch 7's TQ 1 picked [Team v Men] 3:30, where
    Men's last living player picked up a dropped flag next to eight enemies: the scoreboard counts any carrier as a
    capture in its carry time, the lead read -55 s for 10 s, and he died at 3:40 without capturing."""
    t = rows[j]["t"]; held = 0
    for x in rows[j:]:
        if x["stand"]["owner"] == foe and x["t"] <= t + 30: return True
        if x[tag]["flag_lead"] >= -15: break
        held = x["t"] - t
    if held >= SWING_HOLD_S: return True
    return any(x["stand"]["owner"] == foe for x in rows[j:] if x["t"] <= t + 30)


def flag(rid, tag, t0, t1=None, F=None):
    a = analysis(rid); F = F or Forensics(rid)
    foe = [t["tag"] for t in a["meta"]["teams"] if t["tag"] != tag][0]
    # the window: from the last moment the team was at its best lead before t0 to its worst after (within 120 s)
    rows = [r for r in a["scoreboard"] if t0 - 60 <= r["t"] <= (t1 or t0 + 120)]
    best = max([r for r in rows if r["t"] <= t0 + 30] or rows, key=lambda r: r[tag]["flag_lead"])
    after = [i for i, r in enumerate(rows) if r["t"] >= best["t"]]
    real = [rows[i] for i in after if _real_low(rows, i, tag, foe)] or [rows[i] for i in after]
    worst = min(real, key=lambda r: r[tag]["flag_lead"])
    s, e = best["t"], worst["t"]
    L = [f"### Flag swing: {tag} v {foe} ({rid[:8]}), {clock(s)} to {clock(e)}",
         f"**Result**: {tag}'s flag lead {best[tag]['flag_lead']:+} s -> {worst[tag]['flag_lead']:+} s "
         f"({worst[tag]['flag_lead'] - best[tag]['flag_lead']:+} s). Stand: {best['stand']['owner']} -> {worst['stand']['owner']}."]
    # captures and cycles in the window, with the seconds each cost against the fastest possible
    L.append("**Captures** (flag model: fastest possible answer after the enemy's capture):")
    for c in a["flag_cycles"]:
        if s - 30 <= c.get("own_cap", -1) <= e + 30:
            L.append(f"- {c['team']} capped {clock(c['own_cap'])} by {c.get('capper')}, {c.get('cap_delay')} s after {c['enemy']}'s "
                     f"capture; fastest possible {c.get('possible_s')} s, so {c.get('slower_than_possible_s')} s slower"
                     + (f"; enemies in the way {c.get('enemies_in_the_way')}" if c.get("enemies_in_the_way") else ""))
    for f in a["findings"]:
        if f["rule"] == "capped just before a boost" and s - 30 <= f["t"] <= e: L.append(f"- {f['team']}: {f['evidence']}")
    # runs in the window
    L.append("**Runs** (each run: outcome, and what was done to the runner):")
    deaths = []
    for r in a["flag_runs"]:
        if r["end"] < s - 10 or r["start"] > e: continue
        runner = F.role_of(r["team"], r["runner"])
        ctrl = []
        if runner is not None:
            ctrl += [f"{k[0] and clock(k[0])} knockdown by {F.name(k[1])} {k[2]}" for k in F.kds_on(runner, r["start"], r["end"])]
            ctrl += [f"{clock(c[0])} {c[2]} by {F.name(c[1])}" for c in F.conds_on(runner, r["start"], r["end"]) if c[2] in FX.SNARES]
            ctrl += [f"{clock(i[0])} interrupted {i[3]} by {F.name(i[1])} {i[2]}" for i in F.intr_on(runner, r["start"], r["end"])]
        L.append(f"- {r['team']} {r['runner']} {clock(r['start'])} to {clock(r['end'])} ({r['secs']} s): {r['outcome']}, lowest health "
                 f"{r['min_hp']}%, escort {r.get('escort') or 'none'}, pushed by {list(r.get('pushers', {})) or 'nobody'}"
                 + (f"; control on the runner: {'; '.join(ctrl[:8])}" if ctrl else ""))
        if r["outcome"] == "died": deaths.append((r["team"], r["runner"], r["end"]))
    # the fight that decided it: deaths in the window and the stand fight's output
    ds = [d for d in a["deaths"] if s - 5 <= d["t"] <= e]
    if ds:
        L.append("**Deaths in the window**: " + "; ".join(f"{clock(d['t'])} {d['team']} {d['victim']} ({d.get('zone')}, {d.get('numbers')})" for d in ds))
    stand_t = min([d["t"] for d in ds if d["team"] == tag] or [e])
    for tm_tag in (tag, foe):
        o = F.output(F.team_of(tm_tag), stand_t - 20, stand_t)["measures"]
        p, _ = place("team", "dps", o["dps"])
        L.append(f"- {tm_tag} output in the 20 s before {clock(stand_t)}: {o['dps']} damage per second ({p}), top target share "
                 f"{o['top_target_share']}, spikes {o['spikes_400_in_3s']}")
    # the first deaths on the losing side, each with its forensics (short form)
    first = sorted([d for d in ds if d["team"] == tag], key=lambda d: d["t"])[:2]
    for d in first:
        L.append(f"**Why {tag} {d['victim']} died at {clock(d['t'])}** (forensics):")
        L += ["  " + x for x in short(death(rid, tag, d["victim"], d["t"] + .5, F))]
    # cascade
    late = [d for d in a["deaths"] if e < d["t"] <= e + 60]
    if late: L.append("**After**: " + "; ".join(f"{clock(d['t'])} {d['team']} {d['victim']}" for d in late))
    return L


def short(ans):
    """One line per question with the answer and the deciding numbers."""
    out = []
    p = ans["position"]; m = p["measures"]; n = p.get("judged_on_last_s", 5); ln = m.get(f"last{n}s") or {}
    f0 = lambda v: f"{v:.0f}" if isinstance(v, (int, float)) else "?"
    out.append(f"- Position: {p['answer']} (in the last {n} s: nearest allied healer {f0(ln.get('healer_dist'))}, nearest enemy "
               f"{f0(ln.get('nearest_enemy'))}, allies in casting range {ln.get('allies_in_range')}, enemies {ln.get('enemies_in_range')}; "
               f"over the whole window the nearest enemy's median was {f0(m.get('nearest_enemy_median'))})")
    pr = ans["prots"]; pm = pr["measures"]
    kd = pr.get("knockdowns") or []
    out.append(f"- Prots: {pr['answer']}; damage {pm['damage']} ({pm['attack_share']:.0%} attacks, {pm['armor_ignoring_share']:.0%} armor-ignoring), "
               f"burst {pm['burst_2s']} in 2 s at {pm['burst_at']}"
               + (f"; ready and in range but not used: {', '.join(x['healer'] + ' ' + x['skill'] for x in pr['ready_unused'][:4])}" if pr["ready_unused"] else "")
               + (f"; knockdowns {len(kd)}, knockdown immunity up for {sum(1 for k in kd if k['immunity_up'])}" if kd else ""))
    mp = ans["monk_pressure"]
    out.append(f"- Healers under interrupt pressure: {mp['answer']} ({_fmt(mp['measures'])})")
    st = ans["sets"]
    out.append(f"- Damage off shield sets: {st['answer']} (team share {st['measures']['off_shield_share']}, a shield would have stopped about {st['measures']['shield_would_stop']})")
    oo, eo = ans["own_output"], ans["enemy_output"]
    out.append(f"- Own damage: {oo['answer']} ({oo['measures']['dps']} per second on {oo['targets'][:2]}); enemy damage: {eo['answer']} ({eo['measures']['dps']} per second)")
    pe = ans["peel"]
    out.append(f"- Peel: {pe['answer']} ({pe['measures']['pressured']} of {pe['measures']['attackers']} attackers controlled; longest free {pe['measures']['longest_free_s']} s)")
    ca = ans["casting"]
    out.append(f"- Casting: {ca['answer']} ({_fmt({k: ca['measures'][k] for k in ('casts', 'interrupted', 'cancelled', 'while_dazed')})})")
    return out


def key_causes(ans):
    """The findings that stand out in a death's forensics, strongest first, in plain words (for "why, in short")."""
    out = []
    pr = ans["prots"]; pm = pr["measures"]
    if pr["answer"].startswith(("no prots", "late")):
        out.append(f"no prot landed in time ({pm['prots_landed']} of {pm['prots_cast']} landed"
                   + (f"; {', '.join(x['healer'].split(' ', 1)[1] + ' ' + x['skill'] for x in pr['ready_unused'][:2])} ready and unused" if pr["ready_unused"] else "") + ")")
    kd = pr.get("knockdowns") or []
    if kd and not any(k["immunity_up"] for k in kd): out.append(f"knocked down {len(kd)} times with no knockdown immunity up")
    ca = ans["casting"]
    if "far more" in ca["answer"]: out.append(f"its casts were interrupted ({ca['measures']['interrupted']} of {ca['measures']['casts']}"
                                              + (f", {ca['measures']['while_dazed']} while Dazed" if ca['measures']['while_dazed'] else "") + ")")
    if ans["enemy_output"]["answer"] == "high": out.append(f"the enemy hit unusually hard ({ans['enemy_output']['measures']['dps']} per second)")
    if ans["own_output"]["answer"] == "no": out.append(f"its own team's damage was low ({ans['own_output']['measures']['dps']} per second)")
    if ans["monk_pressure"]["answer"] == "yes": out.append("its healers were under interrupt pressure")
    if ans["position"]["answer"] in ("yes", "partly"):
        m = ans["position"]["measures"]; n = ans["position"].get("judged_on_last_s", 5); ln = m.get(f"last{n}s") or {}
        out.append(f"position ({'no allied healer within casting range' if (m.get('out_of_healer_range_share') or 0) >= .5 else 'in contact with the enemy'}, "
                   f"nearest enemy {ln.get('nearest_enemy') or 0:.0f} in the last {n} s)")
    if ans["peel"]["answer"].startswith(("no", "partly")): out.append(f"its attackers were not peeled ({ans['peel']['answer']})")
    if ans["sets"]["answer"] == "yes": out.append("its team took unusual damage off its shield sets")
    return out


# ---------------------------------------------------------------- power plays without a kill
def power(rid, tag, t, F=None, window=None):
    a = analysis(rid); F = F or Forensics(rid)
    foe = [x["tag"] for x in a["meta"]["teams"] if x["tag"] != tag][0]
    dp = min([d for d in a["decisions"] if d["kind"] == "power_play" and d["team"] == tag], key=lambda d: abs(d["t"] - t), default=None)
    t0 = dp["t"] if dp else t; w = window or (dp["outcome"]["window_s"] if dp else 40); t1 = t0 + w
    tm, fm = F.team_of(tag), F.team_of(foe)
    L = [f"### Power play without a kill: {tag} v {foe} ({rid[:8]}), {clock(t0)} to {clock(t1)}"]
    if dp:
        L.append(f"**Situation**: main {dp['state']['main']}, alive {dp['state']['alive']}, flags {dp['state']['flag']} ({dp['state']['flag_lead']:+} s), "
                 f"DP {dp['state']['dp']}, boost in {dp['state']['boost_in']}; choice {dp['choice']} ({dp['actions']['key']}); "
                 f"deaths {dp['outcome']['deaths']} in {w} s")
    # where the enemy's main group went: distance from own main group, every 5 s
    track = []
    for tt in range(int(t0), int(t1) + 1, 5):
        og, eg = F.m.groups(tm, tt * 10), F.m.groups(fm, tt * 10)
        if not og or not eg: continue
        big = og[0]; near = [g for g in eg if min((F.dist(x, y, tt) or 1e9) for x in big for y in g) < 2500]
        tgt = max(near, key=len) if near else eg[0]
        dmin = min((F.dist(x, y, tt) or 1e9) for x in big for y in tgt)
        rest = [g for g in eg if g is not tgt]
        dr = min([min((F.dist(x, y, tt) or 1e9) for x in tgt for y in g) for g in rest] or [None]) if rest else None
        track.append((tt, len(big), len(tgt), round(dmin), round(dr) if dr and dr < 1e8 else None))
    if track:
        L.append("**The fight's shape** (every 5 s: own main, the enemy group it faced, distance between them, that group's distance "
                 "to the rest of its team): " + "; ".join(f"{clock(x[0])} {x[1]}v{x[2]} {x[3]} apart, {x[4]} from its others" for x in track))
        merged = next((x for x in track if x[4] is not None and x[4] < 1300), None)
        if merged: L.append(f"- The enemy group reached its others at about {clock(merged[0])}.")
    # own output against the benchmark
    o = F.output(tm, t0, t1); p, _ = place("team", "dps", o["measures"]["dps"])
    L.append(f"**{tag}'s damage**: {o['measures']['dps']} per second ({p}); top target share {o['measures']['top_target_share']} "
             f"({place('team', 'top_target_share', o['measures']['top_target_share'])[0]}); targets {o['targets']}; dealers {o['dealers']}")
    ph = [x for x in a["phases"] if x["start"] <= t1 and x["end"] >= t0]
    for x in ph:
        gs = (x["teams"].get(tag) or {}).get("groups") or []
        if not gs: continue                      # a phase with the whole team dead or unseen: nothing to read
        g = max(gs, key=lambda g: len(g["members"]))
        c = g["capacities"]
        L.append(f"- phase {clock(x['start'])} to {clock(x['end'])}: {g['numbers']} ({g['zone']}, job {g['job']}), damage uptime {c['damage_uptime']}, "
                 f"damage-seconds lost {c['lost_damage_s']}")
    # enemy healing and prots
    heal = collections.Counter(); prot = collections.Counter()
    for e in F.events(t0, t1, {"hl"}):
        if e[2] in F.m.PL and F.m.team(e[2]) == fm: heal[F.name(e[2])] += e[5] or 0
    for c in F.casts():
        if c[0] in F.m.PL and F.m.team(c[0]) == fm and t0 <= c[2] <= t1:
            sd = F.sdata(c[1]); cz = set(sd.get("causes") or [])
            if cz & {"Block", "Damage Reduction", "Knockdown Immunity"}: prot[F.sname(c[1])] += 1
    L.append(f"**{foe}'s answer**: healing {round(sum(heal.values()) / max(w, 1))} per second ({dict(heal.most_common(4))}); prots {dict(prot)}")
    kd_own = sum(1 for k in (F.m.o.get("knockdowns") or []) if k[1] in F.m.PL and F.m.team(k[1]) == tm and t0 * 10 <= k[0] <= t1 * 10)
    L.append(f"- {tag}'s knockdowns landed {kd_own}; {foe}'s knockdown immunity casts {sum(v for k, v in prot.items() if 'Stability' in k)}")
    mp = F.monk_pressure(fm, t0, t1)["measures"]; pp, _ = place("team", "healer_interrupts_per_min", mp["interrupts_per_min"])
    L.append(f"- Pressure on {foe}'s healers: {_fmt(mp)} ({pp})")
    sn = collections.Counter()
    for x in F.players(fm):
        for c in F.conds_on(x, t0, t1):
            if c[2] in FX.SNARES and c[1] in F.m.PL and F.m.team(c[1]) == tm: sn[c[2]] += 1
    L.append(f"- Snares, Blind and Weakness {tag} put on {foe}: {dict(sn) or 'none'}")
    return L


# ---------------------------------------------------------------- spikes survived
def _spikes(F, tm):
    """Every spike by team tm: (start, target, damage in 3 s, hits [(t, attacker, skill, n)], died within 8 s)."""
    hits = collections.defaultdict(list)
    for e in F.ev:
        if e[1] == "dm" and e[2] in F.m.PL and e[3] in F.m.PL and F.m.team(e[2]) == tm and F.m.team(e[3]) != tm and (e[5] or 0) > 0:
            hits[e[3]].append((e[0] / 10, e[2], e[4], e[5]))
    deaths = collections.defaultdict(list)
    for e in F.ev:
        if e[1] == "dt": deaths[e[2]].append(e[0] / 10)
    out = []
    for tgt, H in hits.items():
        last = -99
        for i, h in enumerate(H):
            win = [x for x in H[i:] if x[0] <= h[0] + 3]
            if h[0] - last < 6 or sum(x[3] for x in win) < 400: continue
            last = h[0]
            out.append((h[0], tgt, sum(x[3] for x in win), win, any(h[0] <= d <= h[0] + 8 for d in deaths[tgt])))
    return sorted(out)


def _landing(win):
    """How tightly a spike landed: spread from first to last big hit (60+), and the share of its damage inside the
    first 0.5 s and 1 s."""
    big = [x for x in win if x[3] >= 60] or win
    tot = sum(x[3] for x in win); t0 = big[0][0]
    return {"spread_s": round(big[-1][0] - t0, 2), "in_0.5s": round(sum(x[3] for x in win if x[0] <= t0 + .5) / tot, 2),
            "in_1s": round(sum(x[3] for x in win if x[0] <= t0 + 1) / tot, 2), "attackers": len({x[1] for x in win})}


def spike_bench():
    from multiprocessing import Pool
    ids = list(json.loads(subprocess.check_output(["git", "-C", REPO, "show", "origin/replays:index.json"]))["matches"])
    res = {"killed": collections.defaultdict(list), "survived": collections.defaultdict(list)}
    with Pool(os.cpu_count() or 2) as p:
        for r in p.imap_unordered(_spike_match, ids):
            for k in r:
                for kk, v in r[k].items(): res[k][kk] += v
    q = lambda L: {str(p): round(statistics.quantiles(L, n=100, method="inclusive")[p - 1], 2) for p in (20, 50, 80)} if len(L) >= 10 else None
    out = {"about": "Spikes (400+ damage in 3 s on one player) in every stored replay: how tightly they landed, for spikes "
                    "that killed (within 8 s) and spikes the target survived. Rebuilt by events.py bench.",
           "matches": len(ids), **{k: {kk: {"n": len(v), "p": q(v)} for kk, v in d.items()} for k, d in res.items()}}
    json.dump(out, open(SPIKE_BENCH, "w"), indent=1)
    return out


def _spike_match(rid):
    F = Forensics(rid); r = {"killed": collections.defaultdict(list), "survived": collections.defaultdict(list)}
    for tm in F.tag:
        for t, tgt, dmg, win, died in _spikes(F, tm):
            l = _landing(win); k = "killed" if died else "survived"
            for kk in ("spread_s", "in_0.5s", "in_1s", "attackers"): r[k][kk].append(l[kk])
            r[k]["damage_3s"].append(dmg)
            pre = sum(1 for x in F.m.o.get("effects", []) if x[2] == "e" and x[5] == tgt and x[0] is not None and x[0] <= t * 10
                      and (x[1] is None or x[1] >= t * 10) and set(F.sdata(x[3]).get("causes") or []) & {"Block", "Damage Reduction"})
            r[k]["preprots_up"].append(pre)
    return {k: dict(v) for k, v in r.items()}


def spike(rid, tag, t, F=None):
    F = F or Forensics(rid); tm = F.team_of(tag)
    sp = min(_spikes(F, tm), key=lambda x: abs(x[0] - t))
    t0, tgt, dmg, win, died = sp
    l = _landing(win)
    sb = json.load(open(SPIKE_BENCH)) if os.path.exists(SPIKE_BENCH) else {}
    def cmp(k):
        kk, ss = (sb.get("killed") or {}).get(k, {}).get("p"), (sb.get("survived") or {}).get(k, {}).get("p")
        return f"median of spikes that killed {kk['50']}, of spikes survived {ss['50']}" if kk and ss else "no benchmark yet"
    L = [f"### Spike by {tag} on {F.name(tgt)} ({rid[:8]}) at {clock(t0)}: {round(dmg)} in 3 s, {'killed' if died else 'survived'}"]
    L.append("**Hits**: " + "; ".join(f"{clock(x[0])} {F.name(x[1]).split(' ', 1)[1]} {F.hit_name(x[1], x[0], x[2])} {round(x[3])}" for x in win))
    L.append(f"**Landing**: spread {l['spread_s']} s first to last big hit ({cmp('spread_s')}); {l['in_1s']:.0%} of the damage inside 1 s "
             f"({cmp('in_1s')}); {l['attackers']} attackers ({cmp('attackers')})")
    # what came 3 to 6 s after the first wave (a second wave)
    after = [d for d in F.damage_on(tgt, t0 + 3, t0 + 6)]
    if after: L.append(f"- Follow-up 3 to 6 s later: {round(sum(d[3] for d in after))} damage ({', '.join(sorted({F.hit_name(d[1], d[0], d[2]) for d in after}))})")
    # pre-prots up at the first hit, and everything cast on the target
    pre = [(F.sname(x[3]), F.name(x[4]), clock(x[0] / 10)) for x in F.m.o.get("effects", []) if x[2] == "e" and x[5] == tgt and x[0] is not None
           and x[0] <= t0 * 10 and (x[1] is None or x[1] >= t0 * 10)]
    L.append(f"**Up on the target at the first hit**: {pre or 'nothing'}")
    own = set(F.players(F.m.team(tgt)))
    cs = [c for c in F.casts() if c[0] in own and c[5] == tgt and t0 - 3 <= c[2] <= t0 + 6]
    L.append("**Cast on the target** (from 3 s before): " + ("; ".join(f"{clock(c[2])} {F.name(c[0])} {F.sname(c[1])} ({c[4]}, {c[2] - t0:+.1f} s)" for c in cs) or "nothing"))
    heals = [e for e in F.events(t0 - 1, t0 + 6, {"hl"}) if e[3] == tgt]
    hs = collections.Counter()
    for e in heals: hs[F.name(e[2]) + " " + (F.sname(e[4]) if e[4] is not None else "unnamed (an enchantment's proc or a heal recorded without its skill)")] += e[5] or 0
    L.append(f"- Healing on the target in the next 6 s: {round(sum(hs.values()))} ({dict(hs.most_common(5))})")
    # defensive control on the spikers
    spikers = sorted({x[1] for x in win})
    ctrl = []
    for x in spikers:
        ctrl += [f"{clock(i[0])} {F.name(x)} interrupted ({i[3]}) by {F.name(i[1])}" for i in F.intr_on(x, t0 - 2, t0 + 3)]
        ctrl += [f"{clock(k[0])} {F.name(x)} knocked down by {F.name(k[1])}" for k in F.kds_on(x, t0 - 2, t0 + 3)]
        ctrl += [f"{clock(c[0])} {F.name(x)} {c[2]}" for c in F.conds_on(x, t0 - 4, t0 + 3) if c[2] in ("blind", "weakness")]
    L.append(f"**Control on the spikers** (2 s before to 3 s after): {'; '.join(ctrl) or 'none'}")
    ws = F.weapon_set(tgt, t0)
    L.append(f"- Target's set: {(ws or {}).get('label')}; health " + ", ".join(
        f"{clock(tt)} {F.snap(tgt, tt)['hp']}%" for tt in [t0 - 1 + i for i in range(0, 8)] if F.snap(tgt, tt)))
    return L


# ---------------------------------------------------------------- pit NPC lost
def npc(rid, tag, t, F=None):
    a = analysis(rid); F = F or Forensics(rid); tm = F.team_of(tag)
    foe = [x["tag"] for x in a["meta"]["teams"] if x["tag"] != tag][0]
    lost = [l for l in a["ledger"] if l["edge"] == "NPC lost" and l["team"] == tag and abs(l["t"] - t) <= 40]
    L = [f"### Pit NPCs lost: {tag} v {foe} ({rid[:8]}) around {clock(t)}",
         "**Lost**: " + "; ".join(f"{clock(l['t'])} {l['what']} ({l['cause']})" for l in lost)]
    sp = [s for s in a["splits"] if s["team"] == foe and s["start"] <= t + 5 and s["end"] >= t - 40]
    for s in sp:
        L.append(f"**{foe}'s split** {clock(s['start'])} to {clock(s['end'])}: {s['members']} ({s['kind']}), entered base "
                 f"{clock(s['entered_base']) if s.get('entered_base') else 'no'}, NPC damage {s.get('npc_damage')}, NPC kills {s.get('npc_kills')}")
        for d in s["defenders"]:
            L.append(f"- defender {d['role']}: first {clock(d['first'])} (latency {d['latency']} s, {d['came']}), {d['secs']} s defending")
        L.append(f"- main numbers meanwhile {s.get('main_numbers')}")
        t0, t1 = s["start"], min(s["end"], t + 5)
    if not sp: t0, t1 = t - 30, t
    # where the rest of the team was
    rest = []
    for x in F.players(tm):
        z = [p for p in a["phases"] if p["start"] <= t <= p["end"]]
        role = F.m.roles.get(x)
        where = next((g["zone"] + " (" + g["job"] + ")" for p in z for g in p["teams"][tag]["groups"] if role in g["members"]), "dead" if not F.alive(x, t - 5) else "?")
        rest.append(f"{role}: {where}")
    L.append(f"**{tag} at {clock(t)}**: " + "; ".join(rest))
    for side, team in ((foe, F.team_of(foe)), (tag, tm)):
        o = F.output(team, t0, t1)["measures"]
        L.append(f"- {side} output {clock(t0)} to {clock(t1)}: {o['dps']} per second")
    return L


# ---------------------------------------------------------------- split answers
def split(rid, tag, t, F=None):
    a = analysis(rid); F = F or Forensics(rid)
    s = min([x for x in a["splits"] if x["team"] == tag], key=lambda x: abs(x["start"] - t))
    foe = [x["tag"] for x in a["meta"]["teams"] if x["tag"] != tag][0]
    L = [f"### Split by {tag} ({rid[:8]}) {clock(s['start'])} to {clock(s['end'])}: {s['members']} ({s['kind']})",
         f"- entered base {clock(s['entered_base']) if s.get('entered_base') else 'no'}; NPC damage {s.get('npc_damage')}, kills {s.get('npc_kills')}; "
         f"player damage {s.get('player_damage')}; deaths {s.get('deaths')}; main numbers meanwhile {s.get('main_numbers')}"]
    for d in s["defenders"]:
        L.append(f"- {foe} {d['role']}: first {clock(d['first'])}, latency {d['latency']} s ({d['came']}), {d['secs']} s")
    main_deaths = [d for d in a["deaths"] if s["start"] <= d["t"] <= s["end"] + 10 and d.get("zone") not in ("own base", "enemy base")]
    L.append("**Meanwhile at main**: " + ("; ".join(f"{clock(d['t'])} {d['team']} {d['victim']} ({d['zone']})" for d in main_deaths) or "no deaths"))
    return L


# ---------------------------------------------------------------- finding events
def find(kind, ids):
    out = []
    for rid in ids:
        a = analysis(rid); tags = [x["tag"] for x in a["meta"]["teams"]]
        if kind == "flag":
            for tag in tags:
                rows = a["scoreboard"]; foe = [x for x in tags if x != tag][0]
                for i, r in enumerate(rows):
                    later = [x for k, x in enumerate(rows[i:i + 24], i) if _real_low(rows, k, tag, foe)]
                    if not later: continue
                    w = min(later, key=lambda x: x[tag]["flag_lead"])
                    drop = r[tag]["flag_lead"] - w[tag]["flag_lead"]
                    if r[tag]["flag_lead"] > 15 and w[tag]["flag_lead"] < -15 and drop > 60:
                        out.append((drop, rid, tag, r["t"], f"{tag} {r[tag]['flag_lead']:+} -> {w[tag]['flag_lead']:+} by {clock(w['t'])}"))
        elif kind == "power":
            for d in a["decisions"]:
                if d["kind"] != "power_play": continue
                foe = [x for x in tags if x != d["team"]][0]
                try: own, en = map(int, d["state"]["main"].split("v"))
                except ValueError: continue
                # every size counts (Denning: an 8v7 while the enemy runs a flag is a power play); until 2026-11-07 only 3+ up
                if d["outcome"]["deaths"].get(foe, 0) == 0 and own - en >= 1:
                    out.append((own - en + d["outcome"]["window_s"] / 60, rid, d["team"], d["t"], f"main {d['state']['main']}, {d['choice']}, no kill in {d['outcome']['window_s']} s"))
        elif kind == "spike":
            F = Forensics(rid)
            for tm, tag in F.tag.items():
                for t, tgt, dmg, win, died in _spikes(F, tm):
                    if not died and dmg >= 600: out.append((dmg, rid, tag, t, f"{tag} on {F.name(tgt)} {round(dmg)} in 3 s, survived"))
        elif kind == "npc":
            for l in a["ledger"]:
                if l["edge"] == "NPC lost" and l["what"] in ("knight", "bodyguard"): out.append((1, rid, l["team"], l["t"], f"{l['team']} lost {l['what']} ({l['cause']})"))
        elif kind == "split":
            for s in a["splits"]:
                lat = min([d["latency"] for d in s["defenders"]] or [999])
                if s.get("entered_base") and (lat >= 30 or s.get("npc_kills")): out.append((lat, rid, s["team"], s["start"], f"{s['team']} split {s['members']}, first defender after {lat} s, NPC kills {s.get('npc_kills')}"))
    # one per match per kind, biggest first
    best = {}
    for x in sorted(out, key=lambda x: -x[0]):
        best.setdefault((x[1], x[2]), x)
    return sorted(best.values(), key=lambda x: -x[0])


KINDS = {"flag": flag, "power": power, "spike": spike, "npc": npc, "split": split}


def explain(kind, rid, tag, t, *rest):
    return KINDS[kind](_rid(rid), tag, _t(t), *[_t(x) for x in rest])


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: print(__doc__)
    elif a[0] == "bench": print(spike_bench()["matches"], "matches")
    elif a[0] == "find":
        import model as M
        ids = a[a.index("--matches") + 1:] if "--matches" in a else [m for b in M.batches() for m in b["matches"]]
        for x in find(a[1], [_rid(i) for i in ids])[:15]: print(f"{x[1][:8]} {x[2]} {clock(x[3])}: {x[4]}")
    else: print("\n".join(explain(*a)))
