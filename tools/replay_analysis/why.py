"""Why chains (Denning: the point is the WHY). For one event, the engine's account of why it happened, walked backwards
along the causal map from the result to its causes, every learned number from models that never saw the match:

1. What happened and what it was worth: the fight's result (deaths, wipe, NPCs, captures, death penalty) and the change
   in win chance across it, with the variables that moved it (win model fitted without the match).
2. The mechanics (why the players died): for each death, the deaths node's reading a few seconds before it (the
   contributions that raised the victim's risk most), from a deaths model fitted without the match.
3. The setup (why the fight was lopsided): the phase just before, per team: where every group was and its job (main,
   split, flag duty, dead), the numbers where it was fought, and each side's capacities there (damage dealers and
   healers, pressure, incoming, sustain margin, damage uptime, control received).
4. The decision (why they were in that setup): the decision point just before for the losing team, what it chose, what
   teams usually do there and what that choice is worth in the data (usual_play.json).
5. The context: flag position, boost clock, death penalty, pit NPCs, builds and strength just before.
Then one line: the chain in words, the strongest link at each step.

Usage:  python3 why.py <report id> <m:ss>        the fight nearest that time
        python3 why.py top N [--matches ids...]  the N fights with the largest win-chance change (default: latest batch)
Needs the analysis files (analyze.py --all --out /tmp/ga). In code: why(rid, fight) -> list of markdown lines."""
import json, os, sys, warnings
warnings.filterwarnings("ignore")
import model as M
import nodes as N
from common import REPO

SRC = "/tmp/ga"
_WP, _DN = {}, {}


def clock(t): return f"{int(t // 60)}:{int(t % 60):02d}"


def _ids():
    return [m for b in M.batches() for m in b["matches"]]


def wp_without(rid):
    if rid not in _WP: _WP[rid] = M.WPModel.fit_on([x for x in _ids() if x != rid])
    return _WP[rid]


def deaths_without(rid):
    if rid not in _DN:
        df, X, y, g, w = N._frame("deaths", [x for x in _ids() if x != rid])
        _DN[rid] = (N._ebm(g.nunique()).fit(X, y, sample_weight=w), list(X.columns))
    return _DN[rid]


def analysis(rid): return json.load(open(os.path.join(SRC, rid + ".json")))


def _row(tab, team, t):
    ts = sorted(x for (tm, x) in tab if tm == team)
    if not ts: return None
    best = min(ts, key=lambda x: abs(x - t))
    return tab[(team, best)]


def win_change(rid, team, t0, t1):
    wp = wp_without(rid)
    tab = {(r["team"], r["t"]): r for r in M.match_table(rid)}
    a, b = _row(tab, team, t0), _row(tab, team, t1)
    if not a or not b: return None
    pa, ca = wp.explain(a); pb, cb = wp.explain(b)
    da, db = dict(ca), dict(cb)
    moved = sorted(((k, round(db.get(k, 0) - da.get(k, 0), 1)) for k in set(da) | set(db)), key=lambda kv: -abs(kv[1]))
    return pa, pb, [m for m in moved if abs(m[1]) >= 2][:5]


def death_reading(rid, team, role, t):
    e, feats = deaths_without(rid)
    rows = [r for r in N.node_rows("deaths_all", rid) if r["team"] == team and r["role"] == role and t - 8 <= r["t"] <= t - 2]
    if not rows: return None
    r = max(rows, key=lambda r: r["t"])
    p, parts = N.explain_row(e, r, feats)
    up = [(k, v) for k, v in parts if v > 0][:4]
    facts = {k: r.get(k) for k in ("health_pct", "health_ceiling", "enemies_near", "allies_near", "healers_in_range", "dazed",
                                    "knocked_down_now", "hexes_on", "hexes_on_own_healers", "prot_up", "dist_from_group", "attackers_5s")}
    return r["t"], p, up, facts


def phase_before(a, t):
    ph = [p for p in a["phases"] if p["start"] <= t - 3]
    return ph[-1] if ph else None


def decision_before(a, team, t):
    ds = [d for d in a["decisions"] if d["team"] == team and t - 45 <= d["t"] <= t]
    return ds[-1] if ds else None


_UP = None
def usual_effect(kind, choice):
    global _UP
    if _UP is None:
        try: _UP = json.load(open(os.path.join(REPO, "data", "model", "usual_play.json")))["kinds"]
        except (OSError, ValueError, KeyError): _UP = {}
    k = _UP.get(kind) or {}
    for c in k.get("choices", []):
        if c["choice"].split(",")[0] == choice.split(":")[0]:
            return k.get("reference"), c
    return k.get("reference"), None


def _caps(g):
    c = g.get("capacities") or {}
    cr = c.get("control_received") or {}
    return (f"{c.get('damage_dealers')} damage, {c.get('healers')} healers, pressure {c.get('pressure')}/s, incoming "
            f"{c.get('incoming')}/s, sustain margin {c.get('sustain_margin'):+}, uptime {c.get('damage_uptime', 0):.0%}, "
            f"control received {cr.get('interrupts', 0)} interrupts ({cr.get('on healers', 0)} on healers), "
            f"{cr.get('knockdowns', 0)} knockdowns" if c.get("sustain_margin") is not None else "no capacities")


NAMES = {"health_ceiling": "health ceiling (death penalty)", "enemies_near": "enemies within 1,500", "local_diff": "local numbers",
         "health_pct": "health", "healers_in_range": "healers in range", "dist_own_pit": "distance from own pit",
         "dazed": "Dazed", "knocked_down_now": "knocked down", "hexes_on": "hexes on it", "attackers_5s": "attackers on it",
         "dist_from_group": "distance from its group", "damage_taken_3s": "damage taken (3 s)", "allies_near": "allies near",
         "interrupted_10s": "interrupted", "prot_up": "prot up", "minute": "match minute", "strength_gap": "strength gap",
         "healers_dead": "own healers dead", "res_in & minute": "the res timer with the clock",
         "hexes_on_own_healers": "hexes on its healers", "conditions_self_taken": "conditions taken on itself",
         "deep_wound": "Deep Wound", "crippled": "Crippled", "away_3000": "3,000+ from its group", "line": "its line"}


def why(rid, f):
    a = analysis(rid)
    tags = list(a["archetypes"]); loser = next(iter(f["losses"]))
    winner = next(t for t in tags if t != loser)
    L = [f"### {' v '.join(tags)} ({rid[:8]}), {clock(f['start'])} to {clock(f['end'])}: "
         f"{loser} lost {sum(f['losses'].values())} player{'s' if sum(f['losses'].values()) > 1 else ''}"
         + (" (a wipe)" if f["wipe"] else "") + f" on the {f.get('where')}", ""]
    con = f["consequence"]
    wc = win_change(rid, loser, f["start"] - 10, min(f["end"] + 30, f["start"] + con["window_s"]))
    res = [f"{k} {v}" for k, v in con["deaths"].items() if v]
    npc = [f"{k} lost {', '.join(v)}" for k, v in con["npcs_lost"].items() if v]
    L.append(f"1. **Result**: deaths {', '.join(res) or 'none'} until all were back; " + ("; ".join(npc) + "; " if npc else "")
             + (f"captures {con['caps']}; " if con["caps"] else "") + f"flag lead {con['flag_lead_change']:+} s; "
             f"death penalty {con['dp_change']}."
             + (f" Win chance for {loser} {wc[0]}% -> {wc[1]}% ({wc[1] - wc[0]:+.1f}); moved by "
                + ", ".join(f"{k} {v:+}" for k, v in wc[2]) + "." if wc else ""))
    L.append("2. **Mechanics** (deaths model that never saw this match, a few seconds before each death; what raised the risk most):")
    for t, team, role, cause in f["deaths"][:4]:
        dr = death_reading(rid, team, role, t)
        if not dr: L.append(f"   - {team} {role} at {clock(t)}: no reading"); continue
        tt, p, up, fx = dr
        L.append(f"   - {team} {role} at {clock(t)} (engine's cause: {cause}): risk {p}% at {clock(tt)}; "
                 + ", ".join(f"{NAMES.get(k, k)} {v:+}" for k, v in up)
                 + f" [health {fx['health_pct']}%, ceiling {fx['health_ceiling']}, {fx['enemies_near']} enemies and "
                 f"{fx['allies_near']} allies near, {fx['healers_in_range']} healers in range"
                 + (", Dazed" if fx["dazed"] else "") + (", knocked down" if fx["knocked_down_now"] else "")
                 + (f", {fx['hexes_on']} hexes" if fx["hexes_on"] else "") + "]")
    ph = phase_before(a, f["start"])
    if ph:
        L.append(f"3. **Setup** (phase {clock(ph['start'])} to {clock(ph['end'])}):")
        vic = {d[2] for d in f["deaths"] if d[1] == loser}
        for team in (loser, winner):
            x = ph["teams"].get(team) or {}
            gs = x.get("groups", [])
            L.append(f"   - {team} plan {', '.join(x.get('plan', [])) or '?'}: "
                     + "; ".join(f"{g['zone']} {g['numbers']} {g['job']} ({', '.join(g['members'])})" for g in gs))
            hot = [g for g in gs if vic & set(g["members"] if team == loser else g.get("enemies", []))]
            for g in hot[:1]: L.append(f"     where the deaths came: {g['numbers']}, {_caps(g)}")
    d = decision_before(a, loser, f["start"])
    if d:
        ref, c = usual_effect(d["kind"], d["choice"])
        L.append(f"4. **Decision** ({d['kind'].replace('_', ' ')} at {clock(d['t'])}): {loser} chose '{d['choice']}' "
                 f"({d['actions']['key']}); usual there: {ref}"
                 + (f"; that choice is worth {c['effect_vs_usual']:+} points against the usual [{c['interval'][0]:+}, {c['interval'][1]:+}]"
                    + (" (partly who chooses it)" if c.get("selection_warning") else "") if c else "") + ".")
    else:
        L.append(f"4. **Decision**: no decision point for {loser} in the 45 s before.")
    b = f["before"]
    short = []
    if ph:
        x = ph["teams"].get(loser) or {}
        vic = {dd[2] for dd in f["deaths"] if dd[1] == loser}
        g = next((g for g in x.get("groups", []) if vic & set(g["members"])), None)
        if g:
            c = g.get("capacities") or {}
            rest = [f"{h['zone']} ({h['job']})" for h in x.get("groups", []) if h is not g]
            short.append(f"{loser} fought {g['numbers']} on the {g['zone']} (job: {g['job']}) with sustain margin "
                         f"{c.get('sustain_margin', 0):+}" + (" while the rest were " + ", ".join(rest) if rest else " with everyone there"))
    tops = []
    for t, team, role, _ in f["deaths"][:2]:
        dr = death_reading(rid, team, role, t)
        if dr and dr[2]: tops.append(f"the {role} died mainly from {NAMES.get(dr[2][0][0], dr[2][0][0])}")
    short += tops
    if d: short.append(f"after choosing '{d['choice']}' at the {d['kind'].replace('_', ' ')}")
    L.append(f"**Why, in short**: " + "; ".join(short) + ".")
    L.append(f"5. **Context**: {loser}: {b.get(loser)}; {winner}: {b.get(winner)}; stand {b.get('stand')}, boost in {b.get('boost_in')} s; "
             f"builds {a['archetypes'][loser]['kind']} v {a['archetypes'][winner]['kind']}; situation: {', '.join(f.get('situation') or [])}.")
    L.append("")
    return L


def top(n, matches):
    cands = []
    for rid in matches:
        a = analysis(rid)
        for f in a["fights"]:
            if not f["losses"]: continue
            loser = next(iter(f["losses"]))
            wc = win_change(rid, loser, f["start"] - 10, min(f["end"] + 30, f["start"] + f["consequence"]["window_s"]))
            if wc: cands.append((abs(wc[1] - wc[0]), rid, f))
    cands.sort(key=lambda c: -c[0])
    out, per = [], {}
    for _, rid, f in cands:
        if per.get(rid, 0) >= 2: continue
        per[rid] = per.get(rid, 0) + 1; out.append((rid, f))
        if len(out) == n: break
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "top":
        n = int(a[1]); ms = a[a.index("--matches") + 1:] if "--matches" in a else M.batches()[-1]["matches"]
        for rid, f in top(n, ms): print("\n".join(why(rid, f)))
    elif len(a) == 2:
        rid, t = a[0], int(a[1].split(":")[0]) * 60 + int(a[1].split(":")[1])
        f = min(analysis(rid)["fights"], key=lambda f: abs(f["start"] - t))
        print("\n".join(why(rid, f)))
    else: print(__doc__)
