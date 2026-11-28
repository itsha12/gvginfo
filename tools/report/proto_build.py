# Builds the match report prototype's data file (data/report_proto/<id>.json) from main's flag cards, execution rows and
# game reviews plus the match's replay and its .x file. Prototype only: the real files come from the exporter.
# python3 tools/report/proto_build.py . 51683de9 data/report_proto/51683de9.json <replay .json.gz> <replay .x.json.gz>
import json, re, sys, gzip, collections
R, rid8, OUT, REPLAY, XFILE = sys.argv[1:6]
L = lambda p: json.load(open(f"{R}/{p}"))
m = [x for x in L("data/recent.json")["matches"] if x["id"].startswith(rid8)][0]
fc = [g for g in L("data/model/flag_cards.json")["games"] if g["rid"].startswith(rid8)][0]
er = [g for g in L("data/model/execution_rows.json")["games"] if g["rid"].startswith(rid8)][0]
gr = [g for g in L("data/model/game_reviews.json")["games"] if g["rid"].startswith(rid8)]
rp = json.load(gzip.open(REPLAY)); xf = json.load(gzip.open(XFILE))
SK = {s_['name']: s_ for s_ in L('data/skills.json')['skills']}
side = {t["tag"]: t["side"] for t in rp["meta"]["teams"]}
A, B = m["teams"][0]["tag"], m["teams"][1]["tag"]
winner = next(t["tag"] for t in m["teams"] if t["won"])
ending = "on Lord damage" if m["dur"] >= 28 * 60 else "by Lord kill"
outline = L(f"data/maps/outline/{rp['meta']['map_id']}.json")
sits = [s for g in gr for s in g["situations"]]
ag, tr = rp["agents"], rp["tracks"]

def pos(a, t10):
    k = tr[str(a)]; i = max((j for j, x in enumerate(k["t"]) if x <= t10), default=0)
    return [k["x"][i], k["y"][i]]

def centre(tag, t):  # the deciding team's living players at the moment: where the call was made
    tm = 1 if tag == A else 2
    ps = [pos(i, t * 10) for i, x in enumerate(ag) if x.get("player") and x["team"] == tm and str(i) in tr]
    alive = [p for i, p in zip([i for i, x in enumerate(ag) if x.get("player") and x["team"] == tm and str(i) in tr], ps)]
    xs = sorted(p[0] for p in alive); ys = sorted(p[1] for p in alive)
    return [xs[len(xs) // 2], ys[len(ys) // 2]]

def morale(txt, tag):
    x = re.search(rf"{tag} (no death penalty or boost|[-+]\d+)", txt)
    return 0 if not x or x[1].startswith("no") else int(x[1])

mm = next((x for f in ["2026-09", "2026-10", "2026-11"] for x in (lambda d: d if isinstance(d, list) else d.get("matches", d))(L(f"data/matches/{f}.json")) if x["id"] == m["id"]), {})
# deaths: the rows on main, matched to the replay's deaths for place, damage, heals and energy
rd = rp["deaths"]
skname = {int(k): v for k, v in rp["skills"].items()}
EN = xf["energy"]
def energy(a, t10):
    e = EN["players"].get(str(a)); i = (t10 - EN["start"]) // EN["step"]
    if not e or i < 0 or i >= len(e["lo"]): return None, None
    return e["lo"][i], e["hi"][i]
def cost(names):
    c = [int(SK[n]["energy"]) for n in names if n in SK and str(SK[n]["energy"]).isdigit()]
    return min(c) if c else 0
def enough(a, names, t10):
    lo, hi = energy(a, t10); c = cost(names)
    if lo is None: return "energy not known"
    return "sufficient energy" if lo >= c else ("may have had the energy" if (hi or 0) >= c else "not enough energy")
def role_agent(team, role, names):
    known = [a for a, r_ in ROLE.items() if r_ == role and ag[a]["team"] == team]
    if known: return known[0]
    cand = [i for i, x in enumerate(ag) if x.get("player") and x["team"] == team and all(any(skname.get(b) == n or (skname.get(b) or "").startswith(n + " (") for b in x["bar"]) for n in names)]
    return cand[0] if len(cand) == 1 else None
ROLE = {}
SA = collections.defaultdict(list)
for e in rp["ev"]:
    if e[1] in ("cs", "sa") and e[4]: SA[e[2]].append(e)
def skill_of(e):  # the skill behind a hit or heal: that actor's latest cast on that player before it (cast start carries the id)
    best = None
    for x in SA[e[2]]:
        if x[3] == e[3] and 0 <= e[0] - x[0] <= 45 and (best is None or x[0] > best[0]): best = x
    return skname.get(best[4]) if best else None
ACT = {"¼": 0.25, "½": 0.5, "¾": 0.75}
def act(nm): a_ = str(SK.get(nm, {}).get("activation") or "1"); return ACT.get(a_) or float(a_ or 1)
def per_cast(a_, nm):  # this player's average heal a cast of that skill in this match (Divine Favor included)
    q = next((q for q in mm.get("players", []) if q["n"] == ag[a_]["n"]), None); sid = SK.get(nm, {}).get("id")
    row = (q or {}).get("sk", {}).get(str(sid)) if sid else None
    return (row[2] / row[0]) if row and row[0] else None
def heal_save(v, f10, t10, hp_first, a_, names):
    """For each heal ready: what it would have healed and the latest start that still lands before the killing hit."""
    hits = sorted((e[0], e[5] or 0) for e in rp["ev"] if e[1] == "dm" and e[3] == v and f10 <= e[0] <= t10)
    tot, cum, kill = sum(h for _, h in hits), 0, t10
    for t_, h in hits:
        cum += h
        if cum >= hp_first: kill = t_; break
    best = None
    for nm in names:
        H = per_cast(a_, nm) if a_ is not None else None
        if not H: continue
        latest = (kill - act(nm) * 10 - f10) / 10
        o = (tot < hp_first + H and latest >= 0, latest, round(H), nm)
        if best is None or o > best: best = o
    if not best: return "Would have healed: not known (no cast of it this match)."
    ok, latest, H, nm = best
    if latest < 0: return f"{nm} would have healed {H}, but no cast could have landed before the killing hit."
    return f"{nm} would have healed {H}" + (f" and saved the spike if cast within {latest:.2f} s of the first big hit." if ok else f", not enough on its own to save him (latest start {latest:.2f} s after the first big hit).")
def items_any(txt):
    return [(m_[1], [n.strip() for n in m_[2].split(",")]) for m_ in re.finditer(r"(?:^|; )([\w/ ]+?) had ([^;.]+)", txt)]
def items(txt):  # "Prot had Shielding Hands ready, in reach, his hands free; 8 Monk had Guardian ready, ..."
    return [(m_[1], [n.strip() for n in m_[2].split(",")]) for m_ in re.finditer(r"(?:^|; )([\w/ ]+?) had (.+?) ready", txt)]
maxhp = {}
for t in (mm.get("teams") or []): pass
FAULT = ("Missed ", "Late ", "Trigger Fault", "Shield set", "Cast into a ready interrupt", "Positioning")
GOOD = ("Success", "No fault")
def KIND(l): return "miss" if l.startswith(FAULT) else ("ok" if l.startswith(GOOD) else "info")
deaths = []
for g in er["groups"]:
    for d in g["deaths"]:
        tm = 1 if d["team"] == A else 2
        hit = min((x for x in rd if ag[x["who"]]["team"] == tm), key=lambda x: abs(x["t"] - d["t"] * 10))
        v, t10, f10 = hit["who"], hit["t"], round(d["first"] * 10)
        ROLE[v] = d["who"]
        win = [e for e in rp["ev"] if f10 <= e[0] <= t10 and e[3] == v]
        dmg = round(sum(e[5] or 0 for e in win if e[1] == "dm"))
        hp_max = next((q.get("hp") for q in mm.get("players", []) if q["n"] == ag[v]["n"]), None) or 0
        k = tr[str(v)]; j = max((i for i, x in enumerate(k["t"]) if x <= f10), default=0)
        hp_first = round(k["hp"][j] / 100 * hp_max) if hp_max else None
        # the engine's own lines, word for word (stage X4 writes them in the report's wording); only their colour is set here
        lines = [[KIND(l), l] for l in d["lines"][1:]]
        head = d["lines"][0]
        mh = re.search(r"Missed: ([^.]+)\.", head)
        missed = [x.strip() for x in mh[1].split(",")] if mh else []
        deaths.append({"t": d["t"], "team": d["team"], "who": d["who"], "name": ag[v]["n"], "spike": d["spike"], "first": d["first"],
                       "dur": round(d["t"] - d["first"], 1), "dmg": dmg, "missed": missed, "head": head, "lines": lines, "at": pos(v, t10)})
deaths.sort(key=lambda d: d["t"])

def reason(t, tag_up):
    s = next((s for s in sits if s["kind"] == "numbers" and s["t0"] - 5 <= t <= s["t1"] + 5), None)
    if not s: return None
    x = re.search(r"\), (from [^;]+);", s["reads"])
    return x[1] if x else None

CAPS = [(c_["t"], 1 if c_["party"] == "party_one" else 2) for c_ in rp["objectives"]["flagstand_captures"]]
def in_hand(t10):  # the teams with a flag in hand at that moment
    hold = {}
    evs = sorted([(e[0], e[1], e[2]) for e in rp["flags"] if e[1] in ("flag_picked_up", "flag_dropped")] + [(t_, "cap", tm_) for t_, tm_ in CAPS])
    for t_, kind, x in evs:
        if t_ > t10: break
        if kind == "flag_picked_up": hold[x] = t_
        elif kind == "flag_dropped": hold.pop(x, None)
        else:
            for a_ in [a_ for a_ in hold if ag[a_]["team"] == x]: hold.pop(a_)
    return sorted({ag[a_]["team"] for a_, t_ in hold.items() if t10 - t_ <= 1200})
moments, used = [], set()
for c in fc["cards"]:
    x = re.search(r"chance of winning (\d+)% to (\d+)% \(([-+][\d.]+)\)", c["followed"])
    b, a_, dlt = int(x[1]), int(x[2]), float(x[3])
    tb, ta = b, a_
    if c["team"] != A: b, a_ = 100 - b, 100 - a_
    us, them = c["team"], (B if c["team"] == A else A)
    sp, hd, fo = c["spot"].removeprefix("The spot: "), c["head"], c["followed"]
    ev, stand = (hd.split(". ", 1) + [""])[:2]
    fight = re.search(r"main fight (\w+) (\d+) v (\w+) (\d+) \(([^)]*)\)", sp)
    up = re.search(r"(\w+) up by (\d+)", fight[5]) if fight else None
    places = re.search(r"main fight [^;]+; (\w+)'s main team at ([^,]+), (\w+)'s at ([^;]+);", sp)
    fl = re.search(r"(\w+) ahead on flags by ([\d.]+)", sp)
    lead0 = (float(fl[2]) if fl[1] == us else -float(fl[2])) if fl else 0.0
    lc = re.search(r"flag lead ([-+][\d.]+) for", fo)
    bits = re.search(r"180 s on: (.*?); flag lead", fo)[1].split("; ")
    dz = re.search(r"deaths (\w+) (\d+), (\w+) (\d+)", fo); bz = re.search(r"boosts (\w+) (\d+), (\w+) (\d+)", fo)
    res = re.search(r"base res in (\d+) s", sp)
    t0, t1 = c["t"], c["t"] + 180
    inside = [i for i, d in enumerate(deaths) if t0 <= d["t"] <= t1]; used.update(inside)
    pk = min((e for e in rp["flags"] if e[1] == "flag_picked_up" and abs(e[0] - t0 * 10) <= 150), key=lambda e: abs(e[0] - t0 * 10), default=None)
    moments.append({"t": t0, "team": us, "foe": them, "scenario": "run again, or not" if "Run again" in hd else "answer to a run",
        "event": ev.strip().rstrip(".") + ".", "stand": stand.strip(),
        "flags": f"{fl[1]} ahead by {fl[2]} flags" if fl else "Flags level",
        "fight": f"{fight[1]} {fight[2]} v {fight[3]} {fight[4]}" if fight else None,
        "fight_up": (f"{up[1]} up by {up[2]}" + (f" {reason(t0, up[1])}" if reason(t0, up[1]) else "")) if up else "even",
        "places": [f"{places[1]}'s main team at {places[2]}", f"{places[3]}'s main team at {places[4]}"] if places else [],
        "morale": {A: morale(sp, A), B: morale(sp, B)}, "base_res": int(res[1]) if res else None,
        "decision": c["answer"].removeprefix("The answer: "),
        "result": bits, "lead0": lead0, "lead_change": float(lc[1]) if lc else None, "in_hand": [[A, B][i - 1] for i in in_hand(t1 * 10)],
        "alts": [(o[1].strip(), o[2], o[3]) for o in re.finditer(r"(?:: |; )([^:;]+?) ([-+][\d.]+) \((\d+) cases\)", c["similar"])],
        "alt_verdict": (lambda v_: v_[1] if v_ else "")(re.search(r"cases\): (no clear difference \([^)]*\)|the data favours .*? win points \([^)]*\))", c["similar"])),
        "alt_head": re.match(r"Similar spots, ([^:]+):", c["similar"])[1] if re.match(r"Similar spots, ([^:]+):", c["similar"]) else "",
        "deaths_n": [dz[1], int(dz[2]), dz[3], int(dz[4])] if dz else None, "boosts_n": [bz[1], int(bz[2]), bz[3], int(bz[4])] if bz else None,
        "chance": [tb, ta, dlt], "a_before": b, "a_after": a_, "swing": dlt,
        "similar": c["similar"].removeprefix("Similar spots, "), "verdict": c.get("verdict"), "deaths": inside,
        "at": centre(us, t0)})
names = {}
for t in m["teams"]:
    for p in t["players"]: names[(t["tag"], p["pos"])] = p["n"]
out = {"prototype": True, "rid": m["id"], "map": m["map"], "occ": m["occ"], "date": m["date"], "dur": m["dur"], "result": f"{winner} won {ending}",
       "teams": [{"tag": t["tag"], "guild": t["guild"], "won": t["won"], "deaths": t["deaths"], "side": side[t["tag"]],
                  "players": [{"pos": p["pos"], "name": p["n"], "build": p.get("build"), "p": p["p"], "s": p["s"], "bar": p["bar"],
                               "deaths": next((q["deaths"] for q in mm.get("players", []) if q["team"] == ti + 1 and q["pos"] == p["pos"]), None)}
                              for p in sorted(t["players"], key=lambda p: p["pos"])]} for ti, t in enumerate(m["teams"])],
       "start_chance": None, "moments": moments, "deaths": deaths, "lone_deaths": [i for i in range(len(deaths)) if i not in used],
       "outline": {"bounds": outline["bounds"], "traps": outline["traps"]},
       "other_moments": [{"kind": s["kind"], "t": s["t0"], "reads": s["reads"]} for s in sits if s["kind"] != "flag"]}
json.dump(out, open(OUT, "w"), ensure_ascii=False, separators=(",", ":"))
print(len(moments), "moments;", len(deaths), "deaths;", out["result"], side)
for d in deaths[:4]: print(d["t"], d["who"], d["name"], d["dmg"], d["dur"], d["missed"], d["at"])
for mo in moments[:2]: print({k: mo[k] for k in ("event", "stand", "flags", "fight", "fight_up", "places", "morale", "result", "lead0", "lead_change", "at")})
