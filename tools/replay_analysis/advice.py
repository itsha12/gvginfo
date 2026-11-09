"""Does the advice work? The goal test (Denning, November 2026 review, P2; docs/SPEC.md section 1).

For every decision kind: the matches are split into 6 groups; for each group the advice is built from the other five
only (so the test matches are unseen), then read on the test group: did teams whose choice matched the advice do
better than teams whose choice didn't, in win-chance change over the decision's window, adjusted for the situation?

The advice for a decision = among the K most similar decisions in the training groups (usual.py's similarity: the
situation, build axes and map), the choice with the best mean win-chance change, if it has MIN_CASES cases among
them and beats the most common choice there by MARGIN points; otherwise the usual play (the most common choice).
"Matched" = the team chose what the advice says. The effect = the adjusted difference in win-chance change between
matched and unmatched decisions (a regression on the situation plus a matched flag, like usual.py's choice effects),
with a 90% range from resampling whole matches. A kind passes when the range excludes 0 and the effect is positive.

The second reading, "the blind test": sealed rounds in data/model/blind_tests.json (one added per chunk, never refreshed;
8 picks: 6 random, 2 where the advice differs from the usual play), answered by Denning on the site (Model > Blind
test) and scored there in the browser or with `advice.py blind_score [round]`; both calls are recorded before the
outcome is read.

Usage: python3 advice.py [DIR] [--blind | --blind-only]   (reads the decision records usual.py builds; prints the table;
       --blind also adds a sealed blind-test round, --blind-only adds only that; --batch=N labels the round)
       python3 advice.py blind_score [round id]
In code: advice_test(recs) -> {kind: {...}}; lines(res) -> report lines. Report layer: no cache key."""
import collections, json, os, random, sys
import numpy as np
from common import REPO

K = 15
MIN_CASES = 5
MARGIN = 2.0
FOLDS = 6
BOOT = 200
OUT = os.path.join(REPO, "data", "model", "advice_test.json")


def _prep(recs, kind):
    import usual as U
    L = [r for r in recs if r["kind"] == kind and "wp_change" in r]
    for r in L:
        r["choice2"] = U.refine(r); r["sit"] = U.situation(r, r.get("gap"))
    counts = collections.Counter(r["choice2"] for r in L)
    choices = [c for c, n in counts.most_common() if n >= MIN_CASES]
    L = [r for r in L if r["choice2"] in choices]
    if len(L) < 40 or len(choices) < 2: return None
    build_cols = [f"{side}_{a}" for side in ("own", "enemy") for a in U.AXES]
    nb_cols = U.SIT + U.SIT_EXTRA.get(kind, []) + build_cols + U.MAP_COLS
    adj_cols = U.SIT + U.SIT_EXTRA.get(kind, [])
    XN = np.array([[r["sit"][k] for k in nb_cols] for r in L], float)
    ZN = (XN - XN.mean(0)) / (XN.std(0) + 1e-9)
    XA = np.array([[r["sit"][k] for k in adj_cols] for r in L], float)
    ZA = (XA - XA.mean(0)) / (XA.std(0) + 1e-9)
    y = np.array([r["wp_change"] for r in L], float)
    return L, choices, ZN, ZA, y


def _fold_of(match):
    import cache
    return cache.fold_of(match, FOLDS)


def advise(i, train_idx, L, ZN, y):
    """The advice for decision i from the training decisions: (recommended choice, usual choice, cases behind it)."""
    d = np.sqrt(((ZN[train_idx] - ZN[i]) ** 2).sum(1))
    near = [train_idx[j] for j in np.argsort(d)[:K]]
    by = collections.defaultdict(list)
    for j in near: by[L[j]["choice2"]].append(y[j])
    usual = max(by.items(), key=lambda kv: len(kv[1]))[0]
    best, bval = usual, float(np.mean(by[usual]))
    for c, v in by.items():
        if len(v) >= MIN_CASES and float(np.mean(v)) >= bval + MARGIN: best, bval = c, float(np.mean(v))
    return best, usual, len(by.get(best, []))


def advice_test(recs):
    out = {}
    kinds = sorted({r["kind"] for r in recs})
    for kind in kinds:
        p = _prep(recs, kind)
        if not p: out[kind] = {"note": "not enough decisions yet"}; continue
        L, choices, ZN, ZA, y = p
        fold = np.array([_fold_of(r["match"]) for r in L])
        matched = np.zeros(len(L)); specific = np.zeros(len(L), bool)
        rec_counts = collections.Counter()
        for f in range(FOLDS):
            te = np.where(fold == f)[0]; tr = np.where(fold != f)[0]
            if len(te) == 0 or len(tr) < 20: continue
            for i in te:
                best, usual, n = advise(i, tr, L, ZN, y)
                matched[i] = 1.0 if L[i]["choice2"] == best else 0.0
                specific[i] = best != usual
                rec_counts[best] += 1
        # adjusted difference: win-chance change on the situation plus the matched flag
        def effect(idx):
            A = np.hstack([np.ones((len(idx), 1)), ZA[idx], matched[idx, None]])
            coef, *_ = np.linalg.lstsq(A, y[idx], rcond=None)
            return float(coef[-1])
        allidx = np.arange(len(L))
        est = effect(allidx)
        matches = sorted({r["match"] for r in L}); mi = collections.defaultdict(list)
        for i, r in enumerate(L): mi[r["match"]].append(i)
        rnd = random.Random(7); boots = []
        for _ in range(BOOT):
            idx = np.array([i for mm in (rnd.choice(matches) for _ in matches) for i in mi[mm]])
            try: boots.append(effect(idx))
            except Exception: pass
        lo, hi = (np.percentile(boots, [5, 95]) if boots else (None, None))
        raw_m = float(np.mean(y[matched == 1])) if (matched == 1).any() else None
        raw_u = float(np.mean(y[matched == 0])) if (matched == 0).any() else None
        sp = specific.astype(bool)
        spec_eff = None
        if sp.sum() >= 20 and (matched[sp] == 1).any() and (matched[sp] == 0).any():
            spec_eff = round(float(np.mean(y[sp & (matched == 1)]) - np.mean(y[sp & (matched == 0)])), 1)
        out[kind] = {"n": len(L), "matches": len(matches), "matched_share": round(float(matched.mean()), 2),
                     "effect_matched_vs_not": round(est, 1), "interval": [round(float(lo), 1), round(float(hi), 1)] if lo is not None else None,
                     "clear": bool(lo is not None and lo > 0), "raw_matched": round(raw_m, 1) if raw_m is not None else None,
                     "raw_unmatched": round(raw_u, 1) if raw_u is not None else None,
                     "specific_advice_share": round(float(sp.mean()), 2),
                     "specific_advice_effect_raw": spec_eff,
                     "recommended": dict(rec_counts.most_common(6))}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"about": __doc__.split("\n\n")[1].strip(), "kinds": out}, open(OUT, "w"), indent=1)
    return out


def lines(res):
    L = ["## Does the advice work? (the goal test)", "",
         "For each decision kind, the advice is built from five groups of matches and read on the sixth (unseen): teams whose "
         "choice matched the advice against teams whose didn't, win-chance change over the decision's window adjusted for the "
         "situation, 90% range from resampling whole matches. The advice = the best choice among the 15 most similar decisions "
         f"(at least {MIN_CASES} cases, {MARGIN:g}+ points better than the usual play), else the usual play. \"Specific\" = the "
         "advice differed from the usual play.", ""]
    passed = [k for k, v in res.items() if v.get("clear")]
    L.append(f"**{len(passed)} of {sum(1 for v in res.values() if 'n' in v)} kinds pass** (effect positive, range excludes 0): {', '.join(passed) or 'none yet'}.")
    L.append("")
    for k, v in res.items():
        if "n" not in v: L.append(f"- {k}: {v['note']}"); continue
        iv = f"{v['interval'][0]:+} to {v['interval'][1]:+}" if v.get("interval") else "?"
        L.append(f"- {k} ({v['n']} decisions, {v['matches']} matches): matched the advice {v['matched_share']:.0%} of the time; "
                 f"effect of matching {v['effect_matched_vs_not']:+} points (90% {iv}; {'clear' if v['clear'] else 'not clear'}); "
                 f"raw {v['raw_matched']} matched against {v['raw_unmatched']} not; specific advice in {v['specific_advice_share']:.0%} of cases"
                 + (f", raw effect there {v['specific_advice_effect_raw']:+}" if v.get("specific_advice_effect_raw") is not None else "")
                 + f". Most recommended: {', '.join(f'{c} ({n})' for c, n in v['recommended'].items())}.")
    L.append("")
    return L


# ---- the blind test (sealed rounds; answered on the site's Model > Blind test page, scored there or by `advice.py blind_score`)
BLIND = os.path.join(REPO, "data", "model", "blind_tests.json")
BLIND_N, BLIND_SPECIFIC = 8, 2       # Denning (R-284): 8 picks a round, 6 random and 2 where the advice differs from the usual play


def _seal(obj):
    import base64
    return base64.b64encode(json.dumps(obj).encode()).decode()


def _unseal(txt):
    import base64
    return json.loads(base64.b64decode(txt.encode()).decode())


def _load_blind():
    if os.path.exists(BLIND): return json.load(open(BLIND))
    return {"about": "The blind test (Denning, November 2026 review): sealed moments where Denning's call and the model's are both "
                     "recorded before the outcome is read. A round is added after every training chunk and never refreshed: open "
                     "rounds wait until Denning answers them on the site (Model > Blind test). Each pick carries the model's call, "
                     "the usual play, and a sealed part (base64, never printed: the actual choice, its win-chance change, and the "
                     "mean win-chance change of each choice among the 15 most similar decisions in other matches). Scoring: each "
                     "call's expected win-chance change in that situation, and whether it matched what the team did.", "rounds": []}


_SRC = ["/tmp/ga"]


def _meta(match):
    """Map and teams of a match, from its analysis record (the --out directory of analyze.py)."""
    try: return json.load(open(os.path.join(_SRC[0], match + ".json"))).get("meta", {})
    except (OSError, ValueError): return {}


def _at(rows, t):
    """The 5 s record at or just before t."""
    i = min(max(int(t // 5), 0), len(rows) - 1)
    while i > 0 and rows[i].get("t", 0) > t: i -= 1
    return rows[i]


def blind_context(match, team, t, kind):
    """What a player needs to call the moment (Denning, 2026-11-09): whose decision it is, where every player of both
    teams is, flags, stand and boost, morale, pit NPCs, Lord damage, the builds, the split in play. Read from the
    analysis record at the decision time, before the choice; nothing that reveals what the team then did."""
    try: a = json.load(open(os.path.join(_SRC[0], match + ".json")))
    except (OSError, ValueError): return {}
    meta = a.get("meta", {}); teams = [x["tag"] for x in meta.get("teams", [])]
    foe = next((x for x in teams if x != team), None)
    st = _at(a["state"], t); sb = _at(a["scoreboard"], t)
    arch = a.get("archetypes", {})
    roles = collections.defaultdict(list)
    for key in a.get("roles", {}):
        tag, role = key.split(" ", 1); roles[tag].append(role)
    def side(tag):
        s_, b_ = st.get(tag, {}), sb.get(tag, {})
        zones = collections.defaultdict(list)
        for role, z in (s_.get("zones") or {}).items(): zones[z].append(role)
        carrying = [c.split(" ", 1)[1] for c in (st.get("carriers") or []) if c.startswith(tag + " ")]
        ar = arch.get(tag, {})
        return {"tag": tag, "alive": s_.get("alive"), "dead": s_.get("dead") or [], "main": s_.get("main"), "main_roles": s_.get("main_roles") or [],
                "zones": dict(zones), "carrying": carrying, "flag_lead": b_.get("flag_lead"), "flag_how": b_.get("flag_how"),
                "flag_eta": b_.get("flag_eta"), "waiting_runner": b_.get("waiting_runner"), "morale": b_.get("morale_sum"),
                "pit_npcs": b_.get("pit_npcs"), "npc_value": b_.get("npc_value"), "lord_damage": b_.get("lord_damage_dealt"),
                "lord_health": b_.get("lord_health"), "build": ar.get("kind"), "healing_monks": ar.get("healing_monks"),
                "spike_build": ar.get("spike"), "roles": roles.get(tag, [])}
    out = {"team": team, "opponent": foe, "map": meta.get("map"), "t": t, "res_in": st.get("res_in"),
           "stand": st.get("stand"), "mains_apart": st.get("mains_apart"), "own": side(team), "enemy": side(foe) if foe else None}
    # the split in play: the enemy's for a defence decision, own for a split decision; either within 20 s of t
    want = {"who_defends": "enemy", "split_in_base": "enemy", "collapse": "enemy", "split_or_stay": "own", "split_effect": "own"}.get(kind)
    for sp in a.get("splits", []):
        who = "own" if sp["team"] == team else "enemy"
        near = (sp.get("entered_base") is not None and abs(sp["entered_base"] - t) <= 20) or (sp["start"] - 20 <= t <= sp["end"])
        if near and (want is None or who == want):
            out["split"] = {"team": sp["team"], "members": sp["members"], "start": sp["start"], "entered_base": sp.get("entered_base"),
                            "main_numbers": sp.get("main_numbers")}
            break
    return out


def blind_enrich():
    """Fill in the context for every pick of every round that lacks it (needs the analysis records in the --out dir)."""
    data = _load_blind(); n = 0
    for rd in data["rounds"]:
        for p in rd["picks"]:
            if p.get("context"): continue
            p["context"] = blind_context(p["match"], p["team"], p["t"], p["kind"]); n += bool(p["context"])
    json.dump(data, open(BLIND, "w"), indent=1)
    return n


def _pick_one(rnd, L, ZN, y, choices, k, want_specific, tries=400):
    """One pick from kind k: a random decision, or one where the advice differs from the usual play."""
    for _ in range(tries if want_specific else 1):
        i = rnd.randrange(len(L))
        tr = np.array([j for j in range(len(L)) if L[j]["match"] != L[i]["match"]])
        best, usual, nn = advise(i, tr, L, ZN, y)
        if want_specific and best == usual: continue
        d = np.sqrt(((ZN[tr] - ZN[i]) ** 2).sum(1))
        near = [tr[j] for j in np.argsort(d)[:K]]
        by = collections.defaultdict(list)
        for j in near: by[L[j]["choice2"]].append(float(y[j]))
        effects = {c: {"mean_wp_change": round(float(np.mean(v)), 1), "cases": len(v)} for c, v in by.items()}
        r = L[i]
        meta = _meta(r["match"])
        return {"match": r["match"], "team": r["team"], "opponent": next((t["tag"] for t in meta.get("teams", []) if t["tag"] != r["team"]), None),
                "map": meta.get("map"), "t": r["t"], "kind": k, "situation": r["state"], "choices_seen": choices,
                "model_call": best, "usual_play": usual, "specific": best != usual, "denning_call": None, "denning_reason": "",
                "context": blind_context(r["match"], r["team"], r["t"], k),
                "sealed": _seal({"actual_choice": r["choice2"], "wp_change": r["wp_change"], "choice_effects": effects})}
    return None


def blind_pick(recs, n=BLIND_N, specific=BLIND_SPECIFIC, seed=None, batch=None):
    """Add one sealed round of n picks to data/model/blind_tests.json (open rounds are kept, never refreshed): n - specific
    random decisions spread over kinds, plus `specific` decisions where the advice differs from the usual play."""
    data = _load_blind()
    rid = max([r["id"] for r in data["rounds"]], default=0) + 1
    rnd = random.Random(seed if seed is not None else 1000 + rid)
    byk = collections.defaultdict(list)
    for r in recs:
        if "wp_change" in r and r["kind"] not in ("late_game",): byk[r["kind"]].append(r)
    kinds = [k for k in byk if len(byk[k]) >= 40]; rnd.shuffle(kinds)
    prepared = {}
    def prep(k):
        if k not in prepared: prepared[k] = _prep(recs, k)
        return prepared[k]
    picks = []
    ki = 0
    while len(picks) < n - specific and kinds:
        k = kinds[ki % len(kinds)]; ki += 1
        p = prep(k)
        if not p: kinds.remove(k); continue
        L, choices, ZN, ZA, y = p
        x = _pick_one(rnd, L, ZN, y, choices, k, False)
        if x: picks.append(x)
    sp_kinds = list(kinds); rnd.shuffle(sp_kinds); guard = 0
    while len(picks) < n and sp_kinds and guard < 3 * len(sp_kinds):
        k = sp_kinds[guard % len(sp_kinds)]; guard += 1
        p = prep(k)
        if not p: continue
        L, choices, ZN, ZA, y = p
        x = _pick_one(rnd, L, ZN, y, choices, k, True)
        if x: picks.append(x)
    for i, x in enumerate(picks, 1): x["id"] = i
    matches = len({r["match"] for r in recs})
    data["rounds"].append({"id": rid, "created": __import__("datetime").date.today().isoformat(), "batch": batch,
                           "matches_trained": matches, "status": "open", "picks": picks})
    json.dump(data, open(BLIND, "w"), indent=1)
    return data["rounds"][-1]


def blind_score(rid=None):
    """Reveal and score one round (the oldest open one by default). Refuses until every denning_call is filled in. For each
    pick: the mean win-chance change of teams that made each caller's choice in that situation (sealed at pick time),
    whether each call matched what the team actually did, and the actual outcome. Totals per caller."""
    data = _load_blind()
    rounds = [r for r in data["rounds"] if (rid is None and r["status"] == "open") or r["id"] == rid]
    if not rounds: print("No such round, or nothing open."); return None
    rd = rounds[0]
    missing = [p["id"] for p in rd["picks"] if not p.get("denning_call")]
    if missing: print(f"Round {rd['id']} not scored: denning_call is empty for picks {missing}. Fill every call in first."); return None
    tot = collections.Counter(); hit = collections.Counter(); rows = []
    for p in rd["picks"]:
        s = _unseal(p["sealed"]); eff = s["choice_effects"]
        row = {"id": p["id"], "actual_choice": s["actual_choice"], "outcome_wp_change": s["wp_change"]}
        for who, call in (("model", p["model_call"]), ("denning", p["denning_call"]), ("usual", p["usual_play"])):
            e = eff.get(call)
            row[who] = {"call": call, "expected": e["mean_wp_change"] if e else None, "cases": e["cases"] if e else 0,
                        "matched_actual": call == s["actual_choice"]}
            if e: tot[who] += e["mean_wp_change"]
            if call == s["actual_choice"]: hit[who] += 1
        rows.append(row)
    rd["status"] = "scored"
    rd["scored"] = {"at": __import__("datetime").date.today().isoformat(), "picks": rows,
                    "totals": {who: {"expected_wp_change_sum": round(tot[who], 1), "matched_actual": hit[who]} for who in ("model", "denning", "usual")}}
    json.dump(data, open(BLIND, "w"), indent=1)
    for p, r in zip(rd["picks"], rows):
        print(f"{r['id']:>2} {p['kind']:<24} {p['match'][:8]} {p['team']:<6} {p['t']:>5}  actual: {r['actual_choice']} ({r['outcome_wp_change']:+})")
        for who in ("model", "denning", "usual"):
            c = r[who]; print(f"     {who:<8} {c['call']:<28} expected {c['expected'] if c['expected'] is not None else 'n/a (no similar case)'} ({c['cases']} cases){'  = actual' if c['matched_actual'] else ''}")
    print("Totals:", json.dumps(rd["scored"]["totals"]))
    return rd


if __name__ == "__main__":
    if "blind_enrich" in sys.argv:
        _SRC[0] = next((a for a in sys.argv[1:] if not a.startswith("--") and a != "blind_enrich"), "/tmp/ga")
        print(blind_enrich(), "picks given their context"); sys.exit()
    if "blind_score" in sys.argv:
        arg = [a for a in sys.argv[1:] if a.isdigit()]
        blind_score(int(arg[0]) if arg else None); sys.exit()
    import usual as U
    src = next((a for a in sys.argv[1:] if not a.startswith("--")), "/tmp/ga"); _SRC[0] = src
    recs = U.wp_change(U.load(src))
    if "--blind-only" not in sys.argv:
        res = advice_test(recs)
        print("\n".join(lines(res)))
    if "--blind" in sys.argv or "--blind-only" in sys.argv:
        bt = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--batch=")), None)
        rd = blind_pick(recs, batch=bt)
        print(f"Blind test round {rd['id']}: {len(rd['picks'])} sealed picks added to {BLIND} (nothing sealed is printed).")
        for p in rd["picks"]: print(f"  {p['id']:>2} {p['kind']:<24} {p['match'][:8]} {p['team']:<6} {p['t']:>5}  model: {p['model_call']}; usual: {p['usual_play']}{'  (specific)' if p['specific'] else ''}")
