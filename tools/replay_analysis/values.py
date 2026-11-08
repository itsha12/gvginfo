"""What results are worth, and what their causes are worth, in win chance: the currency that lets the engine compare a
death with a knight, a capture with a boost, and Daze with a parked flag.

Result values (one per kind of event, for the team it happened to):
- deaths (all; healers and others; by how long the player stays down: back within 20 s, 20 to 60 s, 60 s or more),
  pit NPCs lost by kind, captures, boosts.
- Measured two ways, both from a win model fitted WITHOUT that match (it never saw the result), each against matched
  moments without the event (same minute band, same win chance band; measure()):
  * result: how the match actually ended against what the model expected just before the event (won minus win chance
    5 s before, less the same gap at the matched moments). This is data, not the model's opinion: it includes what the
    event usually led to (a death that starts a wipe carries the wipe).
  * model's view: the change in the model's win chance over the next 30 s. Where the two disagree, the win model's
    curve for that variable is suspect (the knights curve has run backwards since batch 0).
- 90% intervals by bootstrap over whole matches.

Cause values: a node model says how much a state raises the chance of a result (Daze raises the chance of dying in the
next 10 s); multiplied by what that result is worth, the state gets a price in win chance. Classification nodes only
for now (deaths, kill conversion, pit NPC loss); the flag and Lord nodes need a value per second of flag answer and
per point of Lord damage, measured next.

Usage:  python3 values.py            measure and write data/model/values.json and knowledge/values.md
In code: measure(ids) -> dict; report_lines(values) -> markdown lines for the learning report."""
import collections, json, math, os, random, statistics, sys, warnings
warnings.filterwarnings("ignore")
from common import REPO, BOOST_EVERY
import model as M


OUT = os.path.join(REPO, "data", "model", "values.json")
MD = os.path.join(REPO, "knowledge", "values.md")
AFTER = 30          # seconds for the model's view
MIN_N = 8           # events needed before a value is shown
BOOT = 1000


def _events(rid):
    """Deaths, pit NPC losses, captures and boosts in one match, each for the team it happened to."""
    import cache
    return cache.prepared("events", rid, lambda: _build_events(rid))


def _build_events(rid):
    from replaylib import Match
    from state import GameState
    from phases import healer, zone_of
    from scoreboard import archetype
    st = GameState(Match.from_branch(rid)); m = st.m
    from scoreboard import Scoreboard
    from features import footmen
    sb = Scoreboard(st)
    spike = {tm: archetype(m, tm)["spike"] for tm in st.teams}
    def morale(tm, t):     # the team's morale just before (sum over players; positive = boosted)
        try: return (sb.at(max(t - 1, 0))[m.tag[tm]] or {}).get("morale_sum", 0) or 0
        except Exception: return 0
    ev = []
    for tm in st.teams:
        for a in st.players[tm]:
            for tt in st.death_times.get(a, []):
                where, _ = st.pos(a, max(tt - 0.5, 0))
                ev.append({"kind": "death", "team": m.tag[tm], "t": tt, "healer": bool(healer(m, a)),
                           "down_s": round(st.next_res(tt) - tt), "role": m.roles.get(a),
                           "zone": zone_of(st, tm, where) if where else None, "enemy_spike": spike[3 - tm],
                           "morale": morale(tm, tt)})
    for tm in st.teams:            # footmen (base NPCs, not pit NPCs)
        for a, tt in footmen(m)[tm]:
            if tt is not None: ev.append({"kind": "footman", "team": m.tag[tm], "t": tt})
    for a, tt in st.npc_dead.items():
        n = st.geo.npcs.get(a)
        if n and n["kind"] != "guild_lord" and n.get("team") in st.teams:
            ev.append({"kind": "npc", "npc": n["kind"], "team": m.tag[n["team"]], "t": tt, "enemy_spike": spike[3 - n["team"]]})
    for tt, tm in st.caps:
        if tm in st.teams: ev.append({"kind": "capture", "team": m.tag[tm], "t": tt})
    cl = st.caps + [(st.end, None)]
    for (c, tm), (c2, _) in zip(cl, cl[1:]):
        k = 1
        while tm in st.teams and c + BOOST_EVERY * k < c2:
            ev.append({"kind": "boost", "team": m.tag[tm], "t": c + BOOST_EVERY * k}); k += 1
    return ev


def _wp_series(rid, ids):
    """Win chance at every table row of one match, from a model fitted without it (cached per training set)."""
    import cache
    def series(train):
        wp = M.WPModel.heldout(ids, rid)
        return [[r["team"], r["t"], wp.explain(r)[0], r["won"]] for r in M.match_table(rid)]
    rows = cache.heldout("wp", rid, list(ids), series, sub="series_" + M.calib_key(), per_match=True)
    return {(r[0], r[1]): (r[2], r[3]) for r in rows}


def _groups(e):
    """The value groups an event belongs to."""
    k = e["kind"]
    if k == "death":
        d = e["down_s"]
        g = ["death (any)", "death: healer" if e["healer"] else "death: not a healer",
             "death: back within 20 s" if d <= 20 else "death: down 20 to 60 s" if d < 60 else "death: down 60 s or more",
             "death: against a spike build" if e.get("enemy_spike") else "death: against other builds"]
        if e["healer"]:   # Denning (K14): a monk dying in its own base just before the base res is likely deliberate
            g.append("death: healer in own base or pit, back within 15 s (likely deliberate)"
                     if d <= 15 and e.get("zone") in ("own base", "own pit") else "death: healer, other")
        # boosted / not boosted split dropped (Denning, K18): a death while boosted is no different in kind; the split measured
        # where the team stood (later, already winning), not the death. Matched by minute and win chance it showed no
        # consistent difference (133 matches)
        return g
    if k == "footman":
        return ["footman lost (base NPC)"]
    if k == "npc":
        return [f"pit NPC lost: {e['npc']}", "pit NPC lost (any): taken by a spike build" if e.get("enemy_spike")
                else "pit NPC lost (any): taken by other builds"]
    return {"capture": ["capture"], "boost": ["boost"]}[k]


MATCH_MIN_S = 120    # minute bands of matched moments (seconds)
MATCH_WP = 10        # win-chance bands of matched moments (points)
MATCH_MIN_N = 20     # matched moments needed in a cell, else the win-chance band alone is used


def _cell(t, w): return (int(t // MATCH_MIN_S), int(min(w, 99.9) // MATCH_WP))


def measure(ids):
    """Each event against matched moments without it (Denning, after batch 9): moments of the same minute band and the
    same win chance band (from the same held-out win model) where the team had no event of that kind in the same
    window. Result = (won minus win chance) at the event less the same at its matched moments; model's view = the win
    chance change over the next 30 s less the same at its matched moments."""
    rows = collections.defaultdict(list)       # group -> [(match, event t0, kind, result residual, model change, cell)]
    moments = []                                # (match, team, t0, residual, change, cell)
    ev_at = collections.defaultdict(set)        # (match, team, kind) -> event times
    for rid in ids:
        s = _wp_series(rid, ids)
        last = {tm: max(t for (x, t) in s if x == tm) for tm in {x for x, _ in s}}
        for (tm, t), (w, won) in s.items():
            b = s.get((tm, min(t + 5 + AFTER, last[tm])))
            if b: moments.append((rid, tm, t, 100 * won - w, b[0] - w, _cell(t, w)))
        for e in _events(rid):
            if e["team"] not in last: continue
            ev_at[(rid, e["team"], e["kind"])].add(e["t"])
            t0 = int(e["t"]) - int(e["t"]) % 5 - 5
            t1 = min(t0 + 5 + AFTER, last[e["team"]])
            a, b = s.get((e["team"], t0)), s.get((e["team"], t1))
            if not a or not b or t0 < 0: continue
            for g in _groups(e): rows[g].append((rid, e["kind"], 100 * a[1] - a[0], b[0] - a[0], _cell(t0, a[0])))
    # matched moments per kind of event: no event of that kind for that team in the moment's window
    base = {}
    for kind in {k for (_, _, k) in ev_at}:
        cells = collections.defaultdict(list); bands = collections.defaultdict(list)
        for rid, tm, t, r, c, cl in moments:
            ts = ev_at.get((rid, tm, kind))
            if ts and any(t < x <= t + 5 + AFTER for x in ts): continue
            cells[cl].append((r, c)); bands[cl[1]].append((r, c))
        mean2 = lambda L: (statistics.mean(x for x, _ in L), statistics.mean(y for _, y in L)) if L else (0.0, 0.0)
        base[kind] = ({k: mean2(v) for k, v in cells.items() if len(v) >= MATCH_MIN_N}, {k: mean2(v) for k, v in bands.items()})
    def matched(kind, cl):
        c, b = base[kind]
        return c.get(cl) or b.get(cl[1]) or (0.0, 0.0)
    offset = statistics.mean(m[3] for m in moments) if moments else 0.0
    rnd = random.Random(7)
    out = {"matches": len(ids), "offset": round(offset, 1), "compared_with": "matched moments without the event (same minute band "
           f"of {MATCH_MIN_S // 60} min and win-chance band of {MATCH_WP} points)", "values": {}}
    for g, L in sorted(rows.items()):
        if len(L) < MIN_N: out["values"][g] = {"n": len(L), "note": "too few yet"}; continue
        by = collections.defaultdict(list)
        for rid, kind, r, c, cl in L:
            mr, mc = matched(kind, cl); by[rid].append((r - mr, c - mc))
        keys = list(by)
        def stat(sample):
            xs = [v for k in sample for v in by[k]]
            return statistics.mean(r for r, _ in xs), statistics.mean(c for _, c in xs)
        res, mod = stat(keys)
        boots = sorted(stat([rnd.choice(keys) for _ in keys]) for _ in range(BOOT))
        rb = sorted(x[0] for x in boots); mb = sorted(x[1] for x in boots)
        q = lambda v, f: round(v[int(f * (len(v) - 1))], 1)
        out["values"][g] = {"n": len(L), "matches": len(keys), "result": round(res, 1),
                            "result_90": [q(rb, .05), q(rb, .95)], "model": round(mod, 1), "model_90": [q(mb, .05), q(mb, .95)],
                            "clear": q(rb, .05) > 0 or q(rb, .95) < 0}
    out["causes"] = causes(out["values"])
    return out


def _logit(p): return math.log(p / (1 - p))


# Context, not causes (Denning, after batch 9): strength, build skill counts (fixed for the match), flag lead, morale and
# the clock describe the situation; they are never priced as causes or offered as fixes
CONTEXT_ONLY = {"strength_gap", "minute", "flag_lead", "morale_diff", "morale_total", "morale_sum", "res_in"}


def context_only(node, term):
    import nodes as N
    return (term in CONTEXT_ONLY or term in N.MATCH_FIXED.get(node, set()) or "morale" in term or "flag_lead" in term
            or term.startswith(("own_", "enemy_")) and term in N.MATCHUP_KEYS)


def causes(values):
    """Price states from the node models: change in the result's chance (at the node's real base rate) x the result's
    value. Uses the strongest range of each of the node's top terms."""
    V = lambda g: (values.get(g) or {}).get("result")
    npc = [(v["n"], v["result"]) for g, v in values.items() if g.startswith("pit NPC lost: ") and "result" in v]
    plan = {"deaths": ("death (any)", V("death (any)"), "per 10 s in that state"),
            "kill_conversion": ("death (any)", -V("death (any)") if V("death (any)") is not None else None,
                                "per burst, for the attacking team"),
            "npc_loss": ("pit NPC lost", sum(n * r for n, r in npc) / sum(n for n, _ in npc) if npc else None,
                         "per case, for the defending team")}
    import nodes as N
    out = {}
    for node, (res, val, unit) in plan.items():
        p = os.path.join(REPO, "data", "model", "nodes", node + ".json")
        if val is None or not os.path.exists(p): continue
        d = json.load(open(p)); rate = d["validation"]["glass box"]["rate"]
        L = []
        for t in sorted(d["terms"], key=lambda t: -t["importance"])[:8]:
            if "&" in t["term"] or not t.get("curve") or context_only(node, t["term"]): continue
            b = max(t["curve"], key=lambda c: abs(c["points"]))
            pts = max(min(b["points"], 49), -49)
            dp = 1 / (1 + math.exp(-(_logit(rate) + _logit(0.5 + pts / 100)))) - rate
            L.append({"term": t["term"], "description": t.get("description", t["term"]), "range": [b["from"], b["to"]],
                      "result_chance_change": round(100 * dp, 1), "win_points": round(dp * val, 2)})
        out[node] = {"result": res, "result_value": round(val, 1), "base_rate": rate, "unit": unit, "terms": L}
    return out


def _rng(r): return f"{r[0]:g} to {r[1]:g}"


def report_lines(v, short=False):
    L = [f"Win points for the team it happened to, from {v['matches']} matches. **Result** = how matches actually ended "
         "against what a win model that never saw the match expected just before (so it includes what the event "
         "usually led to); **model** = the win model's own change over the next 30 s. Both against matched moments "
         "without the event (same minute and win chance). A gap between the two points at a win-model curve to check.", "",
         "| Event | Cases | Result | 90% range | Model (30 s) | Clear |", "|---|---|---|---|---|---|"]
    for g, x in v["values"].items():
        if "result" not in x: L.append(f"| {g} | {x['n']} | too few yet | | | |"); continue
        L.append(f"| {g} | {x['n']} | {x['result']:+} | {x['result_90'][0]:+} to {x['result_90'][1]:+} | {x['model']:+} | "
                 f"{'yes' if x['clear'] else 'no'} |")
    if short: return L
    L += ["", "**What causes are worth.** A node model's strongest range for each top variable, turned into win points: "
          "the change in the result's chance (at its real rate) times the result's value. Context (strength, build skill "
          "counts, flag lead, morale, the clock) is left out: it describes the situation, it is not a cause to fix.", ""]
    for node, c in v["causes"].items():
        L += [f"*{node.replace('_', ' ')}* ({c['unit']}; result worth {c['result_value']:+} points, base rate "
              f"{100 * c['base_rate']:.1f}%):", ""]
        for t in c["terms"]:
            L.append(f"- {t['description']} {_rng(t['range'])}: result chance {t['result_chance_change']:+} points, "
                     f"worth {t['win_points']:+} win points")
        L.append("")
    return L


def write(v):
    json.dump(v, open(OUT, "w"), indent=1)
    md = ["# What results and causes are worth", "",
          "Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points "
          "(percentage points of win chance) for the team the event happened to.", ""] + report_lines(v)
    open(MD, "w").write("\n".join(md) + "\n")


if __name__ == "__main__":
    ids = [m for b in M.batches() for m in b["matches"]]
    v = measure(ids); write(v)
    print("\n".join(report_lines(v)))
