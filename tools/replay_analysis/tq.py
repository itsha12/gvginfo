"""The TQs (Denning's four question categories, answered after every training batch; METHODS.md "The TQs"):

  1. flags   one instance in a batched match where a team got behind on flags, and why; then how a different play
             could have increased its win chances
  2. monk    one instance where a monk died, and why; then how it could have been prevented
  3. power   one instance where a team couldn't kill on a power play, and why; then how it could have been converted
  4. npcs    one instance where a team lost pit NPCs, and why; then how it could have been prevented

Each answer has two halves, both from measurement:
- Why: the event's account from events.py and forensics.py (every number placed against the same role or situation in
  every stored match), then "why, in short" from the measured causes.
- The different play: only alternatives the data can price, each with its source:
  * the usual play (usual.py): what teams did in the 15 most similar decisions of that kind in other matches, and each
    choice's effect in win chance against the most common one (90% range, placebo check);
  * node-model readings with one variable changed (nodes.py, models that never saw the match): the same moment read
    again with the alternative (a prot up, another healer in range, one more defender, a different target...), the
    change in the result's chance priced in win points with values.py;
  * forensics' options that were there and unused (prots ready and in range, attackers left free);
  * benchmarks (how fast splits are usually answered, power-play damage against every stored power play).
  Where the engine can't price an alternative, the answer says so.
- Confidence: from the evidence, not a guess: how well the node model does on unseen matches, whether a usual-play
  effect is clear (its range excludes 0) and whether it is partly who chooses it.

Instances: the biggest of each kind in the newest batch (a kind with none there is taken from all trained matches).

Usage:  python3 tq.py [--matches id ...]     the four answers for the latest batch (needs analyze.py --all --out /tmp/ga)
In code: lines(new_ids, ids, recs, usual_res) -> markdown lines (learning.py passes the usual-play records it built)."""
import collections, copy, json, os, statistics, sys, warnings
warnings.filterwarnings("ignore")
import model as M
import nodes as N
from common import REPO

GA = "/tmp/ga"
HEALER_ROLES = ("8 Monk", "7 Monk", "Prot")


def _n(n, word): return f"{n} {word}" + ("" if n == 1 else "s")


def clock(t): return f"{int(t // 60)}:{int(t % 60):02d}"


# ------------------------------------------------------------------ shared measured alternatives
_VAL = None
def value(name, default=None):
    """Win points of a result (values.py, measured in the latest report)."""
    global _VAL
    if _VAL is None:
        try: _VAL = json.load(open(os.path.join(REPO, "data", "model", "values.json")))
        except (OSError, ValueError): _VAL = {}
    v = (_VAL.get("values") or {}).get(name) or {}
    return v.get("result", default)


def cause_value(node):
    value("capture")                                  # loads values.json
    return ((_VAL.get("causes") or {}).get(node) or {}).get("result_value")


_NODE_VAL = {}
def node_validation(node):
    """The node's honest test as last fitted (data/model/nodes/<node>.json)."""
    if node not in _NODE_VAL:
        try: _NODE_VAL[node] = json.load(open(os.path.join(N.NODE_DIR, f"{node}.json")))["validation"]
        except (OSError, ValueError, KeyError): _NODE_VAL[node] = None
    return _NODE_VAL[node]


def node_trust(node):
    v = node_validation(node)
    if not v: return None, "not validated yet"
    if node in N.REGRESSION:
        g, b = v["glass box"], v["simple baseline"]
        return v["verdict"].startswith("adds"), f"typical error {g['mae_s']} s against {b['mae_s']} s for the median on unseen matches"
    g, b = v["glass box"], v["simple baseline"]
    return v["verdict"].startswith("adds"), f"AUC {g['auc']} on unseen matches against {b['auc']} for {' and '.join(v['baseline uses'])} alone"


def what_if(node, rid, row, changes):
    """The node's reading of the same moment with variables changed (a model that never saw the match).
    changes: [(label, {var: new value})]; returns (base reading, [(label, reading, change)])."""
    e, feats = N.heldout_node(node, _ids(), rid)
    def read(r):
        if node in N.REGRESSION:
            import pandas as pd
            x = pd.DataFrame([{k: r.get(k) for k in feats}]).astype(float)
            return round(float(e.predict(x)[0]), 1)
        return N.explain_row(e, r, feats)[0]
    base = read(row); out = []
    for label, ch in changes:
        r2 = dict(row); r2.update(ch)
        v = read(r2); out.append((label, v, round(v - base, 1)))
    return base, out


_IDS = None
def _ids():
    global _IDS
    if _IDS is None: _IDS = [m for b in M.batches() for m in b["matches"]]
    return _IDS


def _analysis(rid):
    import events
    return events.analysis(rid)


def decision_alternatives(recs, usual_res, rid, team, t0, t1, kinds=None):
    """The decision points of a team between t0 and t1 with the usual play there and every choice's measured effect."""
    out = []
    for r in recs:
        if r["match"] != rid or r["team"] != team or not (t0 <= r["t"] <= t1): continue
        if kinds and r["kind"] not in kinds: continue
        k = usual_res.get(r["kind"]) or {}
        if "choices" not in k: out.append({"r": r, "kind": k}); continue
        eff = {c["choice"]: c for c in k["choices"]}
        out.append({"r": r, "kind": k, "chosen": eff.get(r.get("choice2")), "usual": eff.get(r.get("usual")),
                    "best": max(k["choices"], key=lambda c: c["effect_vs_usual"])})
    return sorted(out, key=lambda x: x["r"]["t"])


def _eff(c):
    if not c: return "not measured"
    s = f"{c['effect_vs_usual']:+} [{c['interval'][0]:+}, {c['interval'][1]:+}]"
    if c.get("clear"): s += " CLEAR"
    if c.get("selection_warning"): s += ", partly who chooses it"
    return s


def better_options(x, margin=2.0):
    """Choices that did measurably better than the one made (effects are against the kind's most common choice, so a
    difference between two other choices is approximate). Each: (choice row, difference, clear, partly who chooses)."""
    k, ch = x["kind"], x.get("chosen")
    if "choices" not in k or not ch: return []
    ce, ref = ch["effect_vs_usual"], k["reference"]
    out = []
    for c in k["choices"]:
        if c["choice"] == ch["choice"]: continue
        d = round(c["effect_vs_usual"] - ce, 1)
        if d < margin: continue
        if c["choice"] == ref: clear, sel = bool(ch.get("clear")), bool(ch.get("selection_warning"))      # chosen against the reference
        elif ch["choice"] == ref: clear, sel = bool(c.get("clear")), bool(c.get("selection_warning"))
        else: clear, sel = bool(c.get("clear") and ch.get("clear") is not True), bool(c.get("selection_warning"))
        out.append((c, d, clear, sel))
    return sorted(out, key=lambda o: (-o[2], -o[1]))


def decision_conf(x):
    b = better_options(x)
    if not b: return None
    c, d, clear, sel = b[0]
    return ("usual" if clear and not sel else "usual-sel" if clear else "weak", True)


def decision_lines(dec):
    L = []
    for x in dec:
        r, k = x["r"], x["kind"]
        kind = r["kind"].replace("_", " ")
        if "choices" not in k: L.append(f"- {kind} at {clock(r['t'])}: chose '{r.get('choice2') or r['choice']}'; not enough decisions of this kind yet to price the alternatives"); continue
        ch, us = x["chosen"], x["usual"]
        line = (f"- {kind} at {clock(r['t'])} (main {r['state']['main']}, flags {r['state']['flag_lead']:+} s, boost in "
                f"{r['state']['boost_in']}, fight state {r.get('fight_state')}): chose **{r['choice2']}** ({_eff(ch)} against the most "
                f"common choice, {k['reference']}); in the 15 most similar decisions teams usually chose **{r.get('usual')}**")
        b = better_options(x)
        if b:
            line += "; measured better: " + "; ".join(
                f"**{c['choice']}** ({d:+} points against the choice made, {'clear' if clr else 'not clear yet'}"
                + (", partly who chooses it" if sel else "") + f", n {c['n']})" for c, d, clr, sel in b[:2])
        else:
            line += "; no choice of this kind did measurably better than the one made"
        band = _band(k, r)
        if band: line += f". {band}"
        L.append(line + ".")
    return L


def _band(k, r):
    cells = [b for b in k.get("by_build", []) if "fight" in b and b["choice"] == r.get("choice2")]
    if not cells or r.get("fight_state") is None: return None
    for b in cells:
        lab = b["fight"]
        if ("lowest third" in lab and r["fight_state"] <= _num(lab)) or ("top third" in lab and r["fight_state"] > _num(lab)) or lab == "middle third":
            if lab == "middle third" and any(("lowest third" in c["fight"] and r["fight_state"] <= _num(c["fight"])) or
                                            ("top third" in c["fight"] and r["fight_state"] > _num(c["fight"])) for c in cells): continue
            if "raw_difference" in b:
                return f"In the same fight-state third ({lab}) this choice did {b['raw_difference']:+} against the usual choice (n {b['n']} against {b['n_usual']}, raw)"
            return f"In the same fight-state third ({lab}) there are too few cases yet (n {b['n']} against {b['n_usual']})"
    return None


def _num(lab):
    import re
    m = re.search(r"([+-]\d+\.\d+)", lab)
    return float(m.group(1)) if m else 0.0


def confidence(items):
    """items: [(kind, ok)] where kind is 'node' (validated on unseen matches), 'usual' (clear, not selection),
    'usual-sel' (clear but partly who chooses it), 'weak' (measured but not clear). Returns a word and the reason."""
    strong = [k for k, ok in items if ok and k in ("node", "usual")]
    mid = [k for k, ok in items if ok and k == "usual-sel"]
    if len(strong) >= 2: return "medium to high", "two independent measurements agree"
    if strong or mid: return "medium", "one measurement supports it" + (" (partly who chooses it)" if mid and not strong else "")
    if items: return "low", "measured, but the ranges include no effect yet"
    return "low", "the engine can't price an alternative here yet"


def _row_near(node, rid, team, role, t, lo, hi):
    rows = [r for r in N.node_rows(node, rid) if r["team"] == team and (role is None or r["role"] == role) and t + lo <= r["t"] <= t + hi]
    return max(rows, key=lambda r: r["t"]) if rows else None


def _pts(d_pct, val):
    """Win points from a change in a result's chance (points of chance) and what the result is worth to the team."""
    return None if val is None else round(d_pct / 100 * val, 1)


def meaningful(base, d):
    """A node reading that moves the chance by at least 5 points or 15% of itself (a change worth reporting as an
    alternative; smaller ones are within what the models can't tell apart)."""
    return abs(d) >= max(5.0, 0.15 * base)


# ------------------------------------------------------------------ 1. flags
def flags(new_ids, recs, usual_res):
    import events as EV
    found = EV.find("flag", new_ids); src = "the new matches"
    if not found: found = EV.find("flag", _ids()); src = "all trained matches (none in the new matches)"
    if not found: return ["## TQ 1. Behind on flags", "", "No team fell behind on flags (a +15 s lead turned into -15 s or worse) yet.", ""]
    _, rid, tag, t, txt = found[0]
    a = _analysis(rid)
    L = ["## TQ 1. Behind on flags", "", f"*The biggest flag swing in {src}: {txt}.*", ""]
    L += EV.flag(rid, tag, t)
    # the window flag() used
    rows = [r for r in a["scoreboard"] if t - 60 <= r["t"] <= t + 120]
    best = max([r for r in rows if r["t"] <= t + 30] or rows, key=lambda r: r[tag]["flag_lead"])
    worst = min([r for r in rows if r["t"] >= best["t"]], key=lambda r: r[tag]["flag_lead"])
    s, e = best["t"], worst["t"]
    foe = [x["tag"] for x in a["meta"]["teams"] if x["tag"] != tag][0]
    short = []
    caps = [c for c in a["flag_cycles"] if c["team"] == foe and s - 30 <= (c.get("own_cap") or -1) <= e + 30]
    for c in caps[:1]:
        runs = [r for r in a["flag_runs"] if r["team"] == foe and r["end"] <= c["own_cap"] + 1 and r["start"] >= c["own_cap"] - (c.get("cap_delay") or 60)]
        last = runs[-1] if runs else None
        short.append(f"{foe} capped at {clock(c['own_cap'])}, {c.get('cap_delay')} s after {tag}'s capture"
                     + (f", on its {len(runs)}{'st' if len(runs) == 1 else 'nd' if len(runs) == 2 else 'rd' if len(runs) == 3 else 'th'} run"
                        f" ({sum(1 for r in runs if r['outcome'] == 'dropped')} dropped)" if runs else "")
                     + (f"; {tag} pushed the last carrier with {', '.join(last.get('pushers') or {}) or 'nobody'} but its health never went below "
                        f"{last['min_hp']}%" if last and last["outcome"] == "captured" else ""))
    mine = [c for c in a["flag_cycles"] if c["team"] == tag and s - 30 <= (c.get("own_cap") or -1) <= e + 60]
    for c in mine[:1]:
        short.append(f"{tag}'s answer was {c.get('slower_than_possible_s')} s slower than possible")
    dd = collections.Counter(d["team"] for d in a["deaths"] if s - 5 <= d["t"] <= e)
    if dd: short.append("deaths in the window: " + ", ".join(f"{k} {v}" for k, v in dd.items()))
    if short: L.append(f"**Why, in short**: " + "; ".join(short) + ".")
    L += ["", "**A different play (measured)**", ""]
    conf = []
    # the decisions that set it up
    dec = decision_alternatives(recs, usual_res, rid, tag, s - 30, e)
    if dec:
        L.append("*The decisions in the swing* (usual.py: win-chance points over the decision's window, against the kind's most common choice):")
        L += decision_lines(dec[:3])
        conf += [c for c in (decision_conf(x) for x in dec[:3]) if c]
    else:
        L.append("- No decision point for the team in the swing.")
    # the flag answers in the window, read by the flag-answer node with the alternative
    ans = [r for r in N.node_rows("flag_answer", rid) if r["team"] == tag and s - 30 <= r["t"] <= e + 30]
    ok, trust = node_trust("flag_answer")
    if ans:
        L.append(f"*The answers to the enemy's captures* (flag-answer node: seconds slower than possible; {trust}):")
        saved_best = 0
        for r in ans[:3]:
            ch = []
            if not r.get("waiting_runner"): ch.append(("a runner waiting at the spawn", {"waiting_runner": 1, "runner_to_spawn": 0}))
            if r.get("runner_dead_at_enemy_cap"): ch.append(("the runner alive at the enemy's capture", {"runner_dead_at_enemy_cap": 0}))
            if r.get("forced_drops"): ch.append(("no forced drops (carrier protected)", {"forced_drops": 0, "carrier_damage_taken": 0, "pushers": 0}))
            if r.get("parked_s"): ch.append(("no parking (running at once)", {"parked_s": 0, "parked_in_base_s": 0}))
            if r.get("own_deaths_during"): ch.append(("no own deaths during the answer", {"own_deaths_during": 0}))
            if (r.get("enemies_in_the_way") or 0) > 0: ch.append(("no enemies on the way back", {"enemies_in_the_way": 0}))
            if not ch: L.append(f"- answer at {clock(r['t'])} by the {r['role']}: {r['y']} s slower than possible; nothing to change the engine can read"); continue
            base, out = what_if("flag_answer", rid, r, ch)
            L.append(f"- answer at {clock(r['t'])} by the {r['role']}: {r['y']} s slower than possible (model reads {base} s); with "
                     + "; ".join(f"{lab}: {v} s ({d:+} s)" for lab, v, d in out))
            saved_best = max([saved_best] + [-d for _, _, d in out])
        if saved_best >= 3:
            # the seconds saved, read by the win model as flag lead at the end of the swing
            wp = M.WPModel.heldout(_ids(), rid)
            tab = {(x["team"], x["t"]): x for x in M.match_table(rid)}
            row = tab.get((tag, e - e % 5))
            if row:
                p0 = wp.explain(row)[0]; r2 = dict(row); r2["flag_lead"] = (row.get("flag_lead") or 0) + saved_best
                p1 = wp.explain(r2)[0]
                L.append(f"- Those {saved_best:.0f} s, read by the win model as flag lead at {clock(e)}: {tag} {p0}% -> {p1}% ({p1 - p0:+.1f} points)"
                         + (" (the win model's flag-lead curve still bends the wrong way at the extremes, a known issue, so it can't price "
                            "these seconds here yet)" if p1 < p0 else ""))
        conf.append(("node", bool(ok) and saved_best >= 5))
    c, why = confidence(conf)
    L += ["", f"**Confidence**: {c} ({why}).", ""]
    return L


# ------------------------------------------------------------------ 2. monk death
def monk(new_ids, recs, usual_res):
    import why as WHY, events as EV
    cands = []
    for pool, src in ((new_ids, "the new matches"), (_ids(), "all trained matches (none in the new matches)")):
        for rid in pool:
            a = _analysis(rid)
            for d in a["deaths"]:
                if d["victim"] not in HEALER_ROLES: continue
                if d.get("zone") in ("own base", "own pit") and (d.get("down_for") or 99) <= 15: continue     # likely deliberate (K14)
                wc = WHY.win_change(rid, d["team"], d["t"] - 10, d["t"] + 30)
                if wc: cands.append((wc[1] - wc[0], rid, d, src))
        if cands: break
    if not cands: return ["## TQ 2. A monk death", "", "No monk death to explain yet.", ""]
    cands.sort(key=lambda c: c[0])
    drop, rid, d, src = cands[0]
    team, role, t = d["team"], d["victim"], d["t"]
    a = _analysis(rid); tags = list(a["archetypes"])
    F = WHY._forensics(rid)
    ans = EV.death(rid, team, role, t + .5, F)
    L = ["## TQ 2. A monk death", "",
         f"*The monk death that cost the most win chance in {src}: {' v '.join(tags)} ({rid[:8]}), {team} {role} at {clock(t)} "
         f"({d.get('zone')}, numbers {d.get('numbers')}); win chance {drop:+.1f} points from 10 s before to 30 s after.*", "",
         "**Why** (forensics, against the same role in every stored match):"]
    L += EV.short(ans)
    kc = EV.key_causes(ans)
    if kc: L.append(f"**Why, in short**: the {role} died because " + ", ".join(kc[:4]) + ".")
    L += ["", "**How it could have been prevented (measured)**", ""]
    conf = []
    # options that were there and unused
    pr = ans["prots"]
    if pr["ready_unused"]:
        L.append("- Ready and in range but not used: " + "; ".join(f"{x['healer']} {x['skill']} (casting {', '.join(x['busy_with']) or 'nothing'})" for x in pr["ready_unused"][:4]))
    kd = [k for k in (pr.get("knockdowns") or []) if not k["immunity_up"] and k["ready_in_range"]]
    if kd: L.append("- Knockdowns with knockdown immunity ready and in range: " + "; ".join(f"{k['t']} {k['skill']} by {k['by']} ({', '.join(k['ready_in_range'])} ready)" for k in kd[:3]))
    free = sorted(((n, v) for n, v in ans["peel"]["attackers"].items() if not (v["snares_blind_weakness"] or v["interrupted"] or v["knocked_down"] or v["hexed"])),
                  key=lambda kv: -kv[1]["longest_free_s"])
    if free: L.append("- Attackers left free (no snare, Blind, Weakness, interrupt, knockdown or hex from its team): "
                      + "; ".join(f"{n} {v['longest_free_s']} s free (nearest own non-healer {v['nearest_own_non_healer']})" for n, v in free[:3]))
    # the deaths node with the alternatives
    row = _row_near("deaths_all", rid, team, role, t, -8, -2)
    ok, trust = node_trust("deaths")
    if row:
        ch = []
        if not row.get("prot_up") and pr["ready_unused"]: ch.append((f"a prot up ({pr['ready_unused'][0]['skill']})", {"prot_up": 1}))
        if (row.get("healers_in_range") or 0) == 0 or row.get("solo_healer"): ch.append(("another healer in range", {"healers_in_range": (row.get("healers_in_range") or 0) + 1, "solo_healer": 0}))
        if row.get("dazed"): ch.append(("the Daze removed", {"dazed": 0}))
        if row.get("crippled"): ch.append(("the Cripple removed", {"crippled": 0}))
        if row.get("knocked_down_now") or row.get("knockdowns_10s"): ch.append(("knockdown immunity (no knockdowns)", {"knocked_down_now": 0, "knockdowns_10s": 0}))
        if (row.get("dist_from_group") or 0) > 600: ch.append(("staying with its group", {"dist_from_group": 0, "away_3000": 0}))
        if (row.get("attackers_5s") or 0) >= 2: ch.append(("one attacker peeled off", {"attackers_5s": row["attackers_5s"] - 1}))
        if (row.get("hexes_on") or 0) > 0: ch.append(("its hexes removed", {"hexes_on": 0}))
        if len(ch) > 1: ch.append(("all of these together", {k: v for _, c in ch for k, v in c.items()}))
        if ch:
            base, out = what_if("deaths", rid, row, ch)
            hv = value("death: healer", value("death (any)"))
            L.append(f"- Deaths node at {clock(row['t'])} ({trust}): risk {base}% of dying in the next 10 s; read again with")
            for lab, v, dd in out:
                L.append(f"  - {lab}: {v}% ({dd:+} points of risk; at this death's measured cost of {drop:+.1f} win points, "
                         f"about {_pts(dd, drop):+} expected" + (f"; at a typical healer death's {hv:+}, {_pts(dd, hv):+}" if hv is not None else "") + ")")
            best = min(out, key=lambda x: x[2])
            conf.append(("node", bool(ok) and best[2] < 0 and meaningful(base, best[2])))
        else: L.append(f"- Deaths node at {clock(row['t'])}: none of the variables it reads were in a state a teammate could change.")
    else: L.append("- Deaths node: no reading in the seconds before the death.")
    dec = decision_alternatives(recs, usual_res, rid, team, t - 45, t)
    if dec:
        L.append("- The decision before it (usual.py):")
        L += ["  " + x for x in decision_lines(dec[-1:])]
        conf += [c for c in [decision_conf(dec[-1])] if c]
    c, why = confidence(conf)
    L += ["", f"**Confidence**: {c} ({why}).", ""]
    return L


# ------------------------------------------------------------------ 3. power play without a kill
_PP_BENCH = None
def power_bench():
    """Damage per second and top-target share of every stored power play (3+ more at main), killed against not."""
    global _PP_BENCH
    if _PP_BENCH is None:
        import cache, events as EV
        from forensics import Forensics
        out = {"killed": collections.defaultdict(list), "no kill": collections.defaultdict(list)}
        for rid in _ids():
            def build(rid=rid):
                a = _analysis(rid); F = None; res = []
                for d in a["decisions"]:
                    if d["kind"] != "power_play": continue
                    try: own, en = map(int, d["state"]["main"].split("v"))
                    except ValueError: continue
                    if own - en < 3: continue
                    F = F or Forensics(rid)
                    foe = [x["tag"] for x in a["meta"]["teams"] if x["tag"] != d["team"]][0]
                    o = F.output(F.team_of(d["team"]), d["t"], d["t"] + d["outcome"]["window_s"])["measures"]
                    up = _uptime(a, d["team"], d["t"])
                    res.append({"killed": bool(d["outcome"]["deaths"].get(foe, 0)), "dps": o["dps"], "top_target_share": o["top_target_share"],
                                "uptime": up[0] if up else None})
                return res
            for x in cache.prepared("power_bench", rid, build):
                g = out["killed" if x["killed"] else "no kill"]
                for k in ("dps", "top_target_share", "uptime"):
                    if x.get(k) is not None: g[k].append(x[k])
        _PP_BENCH = {g: {k: (round(statistics.median(v), 2), len(v)) for k, v in d.items() if v} for g, d in out.items()}
    return _PP_BENCH


def _uptime(a, tag, t):
    """The main group's damage uptime in the phase a moment falls in, and what lost the most damage-seconds."""
    ph = [p for p in a["phases"] if p["start"] <= t + 2 <= p["end"]] or [p for p in a["phases"] if p["start"] <= t]
    if not ph: return None
    gs = (ph[-1]["teams"].get(tag) or {}).get("groups") or []
    if not gs: return None
    c = max(gs, key=lambda g: len(g["members"])).get("capacities") or {}
    if c.get("damage_uptime") is None: return None
    lost = c.get("lost_damage_s") or {}
    return c["damage_uptime"], (max(lost, key=lost.get) if lost else "nothing")


def power(new_ids, recs, usual_res):
    import events as EV
    from forensics import Forensics
    found = EV.find("power", new_ids); src = "the new matches"
    if not found: found = EV.find("power", _ids()); src = "all trained matches (none in the new matches)"
    if not found: return ["## TQ 3. A power play without a kill", "", "No power play (3+ more at main) without a kill yet.", ""]
    _, rid, tag, t, txt = found[0]
    a = _analysis(rid); F = Forensics(rid)
    L = ["## TQ 3. A power play without a kill", "", f"*The biggest in {src}: {txt}.*", ""]
    L += EV.power(rid, tag, t, F)
    dp = min([d for d in a["decisions"] if d["kind"] == "power_play" and d["team"] == tag], key=lambda d: abs(d["t"] - t))
    t0, t1 = dp["t"], dp["t"] + dp["outcome"]["window_s"]
    foe = [x["tag"] for x in a["meta"]["teams"] if x["tag"] != tag][0]
    from forensics import place
    o0 = F.output(F.team_of(tag), t0, t1)
    om = o0["measures"]; heal = 0
    for ev in F.events(t0, t1, {"hl"}):
        if ev[2] in F.m.PL and F.m.team(ev[2]) == F.team_of(foe): heal += ev[5] or 0
    up = _uptime(a, tag, t0)
    short = [f"{tag} had {dp['state']['main']} at main for {t1 - t0:.0f} s but dealt {om['dps']} damage per second "
             f"({place('team', 'dps', om['dps'])[0]})"]
    if up: short.append(f"damage uptime {up[0]:.0%} (most damage-seconds lost to {up[1]})")
    short.append(f"spread over {len(o0['targets'])} targets (top share {om['top_target_share']})")
    short.append(f"{foe} healed {round(heal / max(t1 - t0, 1))} per second")
    L.append("**Why, in short**: " + "; ".join(short) + ".")
    L += ["", "**How it could have been converted (measured)**", ""]
    conf = []
    o = om
    pb = power_bench()
    if pb.get("killed"):
        k, n = pb["killed"], pb.get("no kill", {})
        L.append(f"- Against every stored power play (3+ more at main): those that killed had a median {k['dps'][0]} damage per second "
                 f"and top-target share {k.get('top_target_share', ('?', 0))[0]} ({k['dps'][1]} cases); those that didn't, "
                 f"{n.get('dps', ('?', 0))[0]} and {n.get('top_target_share', ('?', 0))[0]} ({n.get('dps', ('?', 0))[1]} cases). "
                 f"{tag} here: {o['dps']} and {o['top_target_share']}."
                 + (f" Damage uptime: {k['uptime'][0]:.0%} in those that killed, {n['uptime'][0]:.0%} in those that didn't"
                    + (f", {up[0]:.0%} here." if up else ".") if "uptime" in k and "uptime" in n else ""))
    # the kill-conversion node: each burst in the window, and the same burst on a different target or with more players
    bursts = [r for r in N.node_rows("kill_conversion", rid) if r["team"] == tag and t0 <= r["t"] <= t1]
    ok, trust = node_trust("kill_conversion")
    kv = cause_value("kill_conversion")
    if bursts:
        b = max(bursts, key=lambda r: r.get("burst_damage") or 0)
        enemy_rows = {r["role"]: r for r in N.node_rows("deaths_all", rid) if r["team"] == foe and abs(r["t"] - (b["t"] - b["t"] % 5)) <= 2}
        ch = []
        dealers = len(F.output(F.team_of(tag), t0, t1).get("dealers") or [])
        if dealers > (b.get("attackers") or 0): ch.append((f"all {dealers} damage dealers in the burst", {"attackers": dealers}))
        for role, er in enemy_rows.items():
            if role == b["role"]: continue
            ch.append((f"on the {foe} {role} instead", {"target_is_healer": er.get("is_healer"), "target_line": er.get("line"),
                       "target_health_pct": er.get("health_pct"), "target_ceiling": er.get("health_ceiling"), "target_prot_up": er.get("prot_up"),
                       "target_block_up": er.get("block_up"), "target_healers_in_range": er.get("healers_in_range"), "target_dazed": er.get("dazed"),
                       "target_deep_wound": er.get("deep_wound"), "target_dist_from_group": er.get("dist_from_group"),
                       "target_hexes": er.get("hexes_on"), "target_away_3000": er.get("away_3000"), "target_knocked_down": er.get("knocked_down_now")}))
        from buildfeat import team_features
        tf = team_features(F.m, F.team_of(tag))
        if tf.get("knockdowns") and not b.get("target_knocked_down"): ch.append(("the target knocked down", {"target_knocked_down": 1}))
        if tf.get("daze") and not b.get("target_dazed"): ch.append(("the target Dazed", {"target_dazed": 1}))
        if (b.get("target_healers_hexed") or 0) == 0 and tf.get("interrupts", 0) + tf.get("energy_denial", 0) + tf.get("daze", 0) > 0:
            ch.append(("a hex on the target's healers", {"target_healers_hexed": 1}))
        if ch:
            base, out = what_if("kill_conversion", rid, b, ch)
            out.sort(key=lambda x: -x[2])
            L.append(f"- Kill-conversion node ({trust}): the biggest burst, {b['burst_damage']} on the {foe} {b['role']} at {clock(b['t'])} "
                     f"with {b['attackers']} attackers, read {base}% to kill within 8 s; read again with")
            for lab, v, dd in out[:6]:
                L.append(f"  - {lab}: {v}% ({dd:+} points" + (f", about {_pts(dd, kv):+} win points at a converted burst's {kv:+}" if kv is not None else "") + ")")
            conf.append(("node", bool(ok) and out[0][2] > 0 and meaningful(base, out[0][2])))
        L.append(f"- Bursts in the window: {len(bursts)}, on " + ", ".join(f"{r['role']} ({r['burst_damage']})" for r in bursts[:6]))
    else:
        L.append("- No burst (a 2 s burst that the kill-conversion node reads) in the window: the damage never came together on one target.")
    dec = decision_alternatives(recs, usual_res, rid, tag, t0 - 2, t0 + 2, kinds={"power_play"})
    if dec:
        L.append("- The choice at the power play (usual.py):")
        L += ["  " + x for x in decision_lines(dec)]
        conf += [c for c in [decision_conf(dec[0])] if c]
    c, why = confidence(conf)
    L += ["", f"**Confidence**: {c} ({why}).", ""]
    return L


# ------------------------------------------------------------------ 4. NPCs lost
def npcs(new_ids, recs, usual_res):
    import why as WHY, events as EV
    cands = []
    for pool, src in ((new_ids, "the new matches"), (_ids(), "all trained matches (none in the new matches)")):
        for _, rid, tag, t, txt in EV.find("npc", pool):
            wc = WHY.win_change(rid, tag, t - 20, t + 20)
            what = next((l["what"] for l in _analysis(rid)["ledger"] if l["edge"] == "NPC lost" and l["team"] == tag and l["t"] == t), "")
            cands.append(((wc[1] - wc[0]) if wc else 0, rid, tag, t, txt, src))
        if cands: break
    if not cands: return ["## TQ 4. Pit NPCs lost", "", "No knight or Bodyguard lost yet.", ""]
    cands.sort(key=lambda c: c[0])
    drop, rid, tag, t, txt, src = cands[0]
    a = _analysis(rid)
    foe = [x["tag"] for x in a["meta"]["teams"] if x["tag"] != tag][0]
    L = ["## TQ 4. Pit NPCs lost", "", f"*The NPC loss that cost the most win chance in {src}: {txt} at {clock(t)}; win chance {drop:+.1f} "
         "points from 20 s before to 20 s after.*", ""]
    L += EV.npc(rid, tag, t)
    sp = [s for s in a["splits"] if s["team"] == foe and s["start"] <= t + 5 and s["end"] >= t - 40]
    rows = [r for r in N.node_rows("npc_loss", rid) if r["team"] == foe and t - 30 <= r["t"] <= t - 3]
    short = []
    if sp: short.append(f"{foe} split {'+'.join(sp[0]['members'])} into {tag}'s base" + (f" at {clock(sp[0]['entered_base'])}" if sp[0].get("entered_base") else ""))
    if rows:
        r = max(rows, key=lambda r: r["t"])
        short.append(f"at {clock(r['t'])} the pit had {r.get('attackers')} attackers against {r.get('defenders')} defenders "
                     f"({r.get('defender_healers')} of them healers), with {r.get('defenders_elsewhere')} of {tag} elsewhere")
    nk = [k for s_ in sp for k in (s_.get("npc_kills") or []) if abs(k["t"] - t) <= 5]
    if nk and nk[0].get("defenders_present"): short.append(f"defenders present at the kill: {', '.join(nk[0]['defenders_present'])}")
    if short: L.append("**Why, in short**: " + "; ".join(short) + ".")
    L += ["", "**How it could have been prevented (measured)**", ""]
    conf = []
    if sp:
        lats = []
        for f in os.listdir(GA) if os.path.isdir(GA) else []:
            if not f.endswith(".json"): continue
            for s in json.load(open(os.path.join(GA, f))).get("splits", []):
                if s.get("entered_base") and s["defenders"]: lats.append(min(d["latency"] for d in s["defenders"]))
        s = sp[0]; lat = min([d["latency"] for d in s["defenders"]] or [None]) if s["defenders"] else None
        if lats:
            def when(x): return "never" if x is None else (f"{-x:.0f} s before it entered the base" if x < 0 else f"{x:.0f} s after it entered the base")
            L.append(f"- First defender: {when(lat)}; every stored split into a base: median {when(statistics.median(lats))}, "
                     f"quickest fifth {when(sorted(lats)[len(lats) // 5])} or sooner ({len(lats)} splits). Denning: about 15 s is on time, 60 s is late.")
            if lat is not None and lat <= 15:
                L.append("- The split was answered on time, so the loss came from what the defence did once there (below), not from a late answer.")
    # the NPC-loss node with more defenders (rows are per attacking team)
    ok, trust = node_trust("npc_loss")
    nv = cause_value("npc_loss")
    if rows:
        r = max(rows, key=lambda r: r["t"])
        ch = [("one more defender", {"defenders": (r.get("defenders") or 0) + 1, "defenders_elsewhere": max((r.get("defenders_elsewhere") or 0) - 1, 0)}),
              ("one more defender, a healer", {"defenders": (r.get("defenders") or 0) + 1, "defender_healers": (r.get("defender_healers") or 0) + 1,
                                              "defenders_elsewhere": max((r.get("defenders_elsewhere") or 0) - 1, 0)}),
              ("two more defenders", {"defenders": (r.get("defenders") or 0) + 2, "defenders_elsewhere": max((r.get("defenders_elsewhere") or 0) - 2, 0)})]
        if (r.get("npc_healing_10s") or 0) == 0: ch.append(("healing on the NPCs (as much as the attackers' damage in 5 s)", {"npc_healing_10s": r.get("npc_damage_5s") or 0}))
        base, out = what_if("npc_loss", rid, r, ch)
        L.append(f"- NPC-loss node at {clock(r['t'])} ({trust}): {r.get('attackers')} attackers ({_n(r.get('attacker_healers'), 'healer')}) against "
                 f"{r.get('defenders')} defenders ({_n(r.get('defender_healers'), 'healer')}), {r.get('defenders_elsewhere')} of {tag} elsewhere; "
                 f"read {base}% to lose an NPC; read again with")
        for lab, v, dd in out:
            L.append(f"  - {lab}: {v}% ({dd:+} points; at this loss's measured cost of {drop:+.1f} win points, about {_pts(dd, drop):+} expected"
                     + (f"; at a typical NPC loss's {nv:+}, {_pts(dd, nv):+}" if nv is not None else "") + ")")
        bestn = min(out, key=lambda x: x[2])
        conf.append(("node", bool(ok) and bestn[2] < 0 and meaningful(base, bestn[2])))
    else: L.append("- NPC-loss node: no reading of the pit in the 30 s before (the attackers weren't counted in the pit).")
    dec = decision_alternatives(recs, usual_res, rid, tag, t - 60, t, kinds={"split_in_base"})
    if dec:
        L.append("- The answer to the split (usual.py; this prices the whole decision, including what the main fight lost while "
                 "defenders were away, which the NPC-loss node above does not):")
        L += ["  " + x for x in decision_lines(dec[-1:])]
        conf += [c for c in [decision_conf(dec[-1])] if c]
    c, why = confidence(conf)
    L += ["", f"**Confidence**: {c} ({why}).", ""]
    return L


# ------------------------------------------------------------------ the section
def lines(new_ids, ids=None, recs=None, usual_res=None):
    import usual as U
    if recs is None:
        recs = U.wp_change(U.load(GA))
    if usual_res is None:
        usual_res = U.analyse(recs)        # adds choice2 and the usual play to every record
    L = ["## The TQs", "",
         "Denning's four questions, each from the batch's matches. The why comes from forensics and events (every number "
         "placed against the same role or situation in every stored match); the different play comes only from "
         "measurement: the usual play's choice effects (usual.py), node models read again with the variable changed "
         "(models that never saw the match, changes priced in win points with values.py), options that were ready and "
         "unused, and benchmarks. Points = win-chance points.", ""]
    for fn in (flags, monk, power, npcs):
        try: L += fn(new_ids, recs, usual_res)
        except Exception as ex:
            import traceback; traceback.print_exc()
            L += [f"## {fn.__name__}: could not be answered ({type(ex).__name__}: {ex})", ""]
    return L


if __name__ == "__main__":
    a = sys.argv[1:]
    new = a[a.index("--matches") + 1:] if "--matches" in a else M.batches()[-1]["matches"]
    print("\n".join(lines(new)))
