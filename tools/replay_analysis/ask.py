"""The query tool: the engine's end product (Denning, November 2026 review; docs/SPEC.md section 7).

A match and a moment in; out: the state, the decisions the team made around the moment with the usual play and the
data-favoured choice (the advice built from the other matches, with the cases behind it), the macro answer (was the
call right), the micro answer (given the call, what went wrong in execution, from the execution node that covers the
moment), and what the enemy did (described, never a cause). Everything comes from models that never saw the match.

Usage:  python3 ask.py <report id> <m:ss> [team tag]        (team defaults to the team with a decision nearest the moment)
        python3 ask.py kinds                                  the decision kinds the tool can answer about
A situation without a match ("builds X against Y, flag lead +30, 8v7 at main, 12:00") is the next form: it needs a
situation row built without a replay; the pieces (usual.py's situation columns, advice.advise) are in place.
Report layer: no cache key."""
import json, os, sys
from common import REPO

NEAR_S = 45          # decisions within this many seconds of the moment are "around" it
# which execution node reads which decision kind's moment
EXEC_NODE = {"power_play": ("power_play", True), "offence_or_defence": ("fight_outcome", True), "eight_v_eight_or_flag": ("fight_outcome", True),
             "split_in_base": ("pit_npc_loss", False), "who_defends": ("collapse", True), "enemy_pickup": ("run_defence", False),
             "boost_clock": ("run_outcome", True), "runner_choice": ("run_outcome", True), "split_or_stay": ("split_effect", True),
             "after_wipe": ("pit_npc_loss", False), "npcs_or_dp": ("pit_npc_loss", False), "play_for_28_or_lord": ("fight_outcome", True)}


def clock(t): return f"{int(t // 60)}:{int(t % 60):02d}"


def parse_clock(s):
    if ":" in s: m, s_ = s.split(":"); return int(m) * 60 + float(s_)
    return float(s)


def _recs():
    import usual as U
    src = "/tmp/ga"
    if not os.path.isdir(src): raise SystemExit("analysis files missing: run analyze.py --all --out /tmp/ga first")
    return U.wp_change(U.load(src))


def state_lines(rid, team, t):
    import tq
    a = tq._analysis(rid)
    sb = a["scoreboard"]
    row = max((r for r in sb if r["t"] <= t), key=lambda r: r["t"], default=None)
    if not row: return ["- no scoreboard row"]
    foe = [x["tag"] for x in a["meta"]["teams"] if x["tag"] != team][0]
    me, en = row[team], row[foe]
    owner = row["stand"]["owner"]
    return [f"- At {clock(row['t'])}: {team} {me['alive']} alive ({me['main']} at main) against {foe} {en['alive']} ({en['main']}); flag lead {me['flag_lead']:+} s, "
            f"stand {'own' if owner == team else ('enemy' if owner == foe else 'nobody')}, boost in {row['stand'].get('boost_in')} s; morale {me['morale_sum']:+} v {en['morale_sum']:+}; "
            f"pit NPC value {me['npc_value']} v {en['npc_value']}; Lord damage {me['lord_damage_dealt']} v {en['lord_damage_dealt']}."]


def answer(rid, t, team=None):
    import advice as ADV, usual as U, tq, learnednodes as LN
    recs = _recs()
    mine = [r for r in recs if r["match"] == rid]
    if not mine: return [f"No decision records for {rid} (is it analysed and trained on?)."]
    near = sorted((r for r in mine if abs(r["t"] - t) <= NEAR_S), key=lambda r: abs(r["t"] - t))
    if team is None:
        team = near[0]["team"] if near else mine[0]["team"]
    near = [r for r in near if r["team"] == team]
    a = tq._analysis(rid)
    L = [f"# {team} at {clock(t)} in {a['meta']['teams'][0]['tag']} v {a['meta']['teams'][1]['tag']} ({rid[:8]})", "", "## State"] + state_lines(rid, team, t) + [""]
    if not near:
        L += ["## Decisions", "", f"- No recorded decision of {team} within {NEAR_S} s of {clock(t)}. Kinds the engine recognizes: " + ", ".join(sorted({r['kind'] for r in recs})) + ".", ""]
    seen_nodes = set()
    for r in near[:3]:
        kind = r["kind"]
        p = ADV._prep(recs, kind)
        L += [f"## Decision: {kind.replace('_', ' ')} at {clock(r['t'])}", ""]
        choice = U.refine(r)
        L.append(f"- Chosen: **{choice}**. Win chance over the window: {r.get('wp_change', 0):+} points (a model that never saw the match).")
        if p:
            Lk, choices, ZN, ZA, y = p
            i = next((j for j, x in enumerate(Lk) if x["match"] == rid and x["team"] == team and x["t"] == r["t"]), None)
            if i is not None:
                import numpy as np
                tr = np.array([j for j in range(len(Lk)) if Lk[j]["match"] != rid])
                best, usual, n = ADV.advise(i, tr, Lk, ZN, y)
                d = np.sqrt(((ZN[tr] - ZN[i]) ** 2).sum(1)); nearest = [tr[j] for j in np.argsort(d)[:ADV.K]]
                by = {}
                for j in nearest: by.setdefault(Lk[j]["choice2"], []).append(y[j])
                tbl = ", ".join(f"{c}: {np.mean(v):+.1f} ({len(v)})" for c, v in sorted(by.items(), key=lambda kv: -len(kv[1])))
                L.append(f"- **Macro**: among the {len(nearest)} most similar decisions in other matches the usual play is **{usual}**; the data favours **{best}**"
                         + (f" ({n} cases, {ADV.MARGIN:g}+ points better than the usual play)" if best != usual else " (nothing beats it by the margin)")
                         + f". Mean win change by choice there: {tbl}.")
                L.append("- Verdict: " + ("the call matched the data-favoured choice." if choice == best else f"the data favoured **{best}** over the chosen **{choice}**."))
            else: L.append("- Macro: this decision isn't in the usual-play set (too few cases of its kind).")
        else: L.append("- Macro: not enough decisions of this kind yet to compare.")
        node, good_high = EXEC_NODE.get(kind, (None, None))
        if node and node in LN.SPEC and node not in seen_nodes:
            seen_nodes.add(node)
            L.append(f"- **Micro** ({node.replace('_', ' ')} node):")
            try:
                ex, faults = tq.execution_lines(node, rid, team, r["t"], good_high=good_high, window=NEAR_S)
                L += ["  " + x for x in ex]
            except Exception as ex_: L.append(f"  - not read: {ex_}")
        L.append("")
    return L


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["kinds"]:
        import decisions as D
        for k, v in D.KINDS.items(): print(f"{k:24} {v['moment']}: {v['choices']} [{v['source']}]")
    elif len(a) >= 2:
        print("\n".join(answer(a[0], parse_clock(a[1]), a[2] if len(a) > 2 else None)))
    else: print(__doc__)
