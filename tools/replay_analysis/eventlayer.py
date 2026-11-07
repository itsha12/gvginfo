"""The event layer (step 1 of the learned causal map, Denning 2026-11-07): every play the causal chains need, measured
in every match as time-stamped records, so node models can learn from them and chains can be built from data.

Per match (cached: cache.prepared("eventlayer", rid)), lists of records:
  strips     every enchantment stripped: who stripped, from whom (healer, midline, frontline), the enchantment, whether it
             was a prot, whether the stripper's team was hitting that target (3 s), useful = a prot off a target under
             attack, or an enchantment off a midline/frontline player (defensive strip); plus removal casts that removed
             nothing (wasted)
  blinds     every Blind put on an enemy: on a frontline player or not, and whether that player had hit the blinder's
             healers in the 3 s before (defensive Blind)
  hexes      every hex on a player: target healer or not, how long it stayed, removed or expired
  peel       frontline damage: share on enemies within 1,200 of the frontliner's own healers (defensive peel), on enemy
             healers, on others; per player per fight
  casts      per player per fight: casts, interrupted, cast into a ready interrupt (and cancelled when threatened),
             cast while Dazed, attacks while Blind (wrong casts, every role)
  spikes     every spike (400+ in 3 s on one player): spread of its big hits, attackers, killed or not
  runs       every flag run: the moment it started (stand owner, enemy boost clock, flag lead, both mains, an enemy power
             play), escort, control on the runner, pushers, outcome
  splits     every split: size, entered base, defenders and the first's latency, NPC damage and kills, enemies drawn
             (enemy players in their base), own main against the enemy main meanwhile, deaths of split members and at main
  power      every power play (any numbers advantage at main for 10 s+ away from home, decisions.py; 8v7 included): size,
             why the enemy was short (decisions.py), flag lead, whether it killed
  caps       every capture from the defending side: the capturing run's pushers, escort, the runner's lowest health, how
             many defenders were alive and not on flag duty, the nearest defender's distance at mid-run
Usage:  python3 eventlayer.py <report id>      prints a summary of the match's records"""
import bisect, collections, json, statistics, sys

FIGHT_PAD = 5
NEAR_HEALER = 1200      # an enemy this close to a frontliner's own healer is attacking its backline
PROT_CAUSES = {"Block", "Damage Reduction"}


def _intervals(F, fam, names):
    """{agent: [(start, end)]} for effects of family fam named in names (conditions by name)."""
    out = collections.defaultdict(list)
    for e in F.m.o.get("effects", []):
        if e[2] != fam or e[0] is None: continue
        nm = e[7] if fam == "c" else F.sname(e[3])
        if nm in names: out[e[5]].append((e[0] / 10, (e[1] / 10) if e[1] is not None else 1e9))
    for k in out: out[k].sort()
    return out


def _on(iv, a, t):
    return any(s <= t <= e for s, e in iv.get(a, ()))


def build(rid):
    from forensics import Forensics
    import tq
    F = Forensics(rid); m = F.m; a = tq._analysis(rid)
    tag = F.tag; heal = F.healers
    from common import line
    cls = lambda b: "healer" if b in heal else ("frontline" if line(m, b) == "frontline" else "midline")
    out = collections.defaultdict(list)
    casts = F.casts()
    # ---- strips
    rm_casts = collections.defaultdict(list)          # target -> [(end, caster, skill)]
    for c in casts:
        if c[4] == "finished" and c[0] in m.PL and c[5] in m.PL and "Enchantment" in (F.sdata(c[1]).get("removes") or []) and m.team(c[5]) != m.team(c[0]):
            rm_casts[c[5]].append((c[3], c[0], F.sname(c[1])))
    used = set()
    for e in m.o.get("effects", []):
        if e[2] != "e" or e[6] != "enchantment_removed_lifo" or e[1] is None or e[5] not in m.PL: continue
        t = e[1] / 10; tgt = e[5]
        by = min((x for x in rm_casts.get(tgt, []) if -0.5 <= t - x[0] <= 1.0), key=lambda x: abs(t - x[0]), default=None)
        if not by: continue
        used.add((tgt, by[0], by[1]))
        sd = F.sdata(e[3]); prot = bool(set(sd.get("causes") or []) & PROT_CAUSES)
        hit = sum(x[3] for x in F.damage_on(tgt, t - 3, t) if m.team(x[1]) == m.team(by[1]))
        out["strips"].append({"t": round(t, 1), "team": tag[m.team(by[1])], "by": m.roles[by[1]], "skill": by[2], "target": m.roles[tgt],
                              "target_class": cls(tgt), "enchantment": F.sname(e[3]), "prot": prot, "target_under_attack": hit >= 100,
                              "useful": (prot and hit >= 100) or (not prot and cls(tgt) != "healer")})
    for tgt, L in rm_casts.items():
        for end, by, sk in L:
            if (tgt, end, by) not in used:
                out["strips_wasted"].append({"t": round(end, 1), "team": tag[m.team(by)], "by": m.roles[by], "skill": sk, "target": m.roles[tgt]})
    # ---- Blind on enemies
    for e in m.o.get("effects", []):
        if e[2] != "c" or e[7] != "blind" or e[0] is None or e[5] not in m.PL or e[4] not in m.PL or m.team(e[4]) == m.team(e[5]): continue
        t = e[0] / 10; tgt, by = e[5], e[4]
        own_heal = [h for h in heal if m.team(h) == m.team(by)]
        hit_heal = sum(x[3] for h in own_heal for x in F.damage_on(h, t - 3, t) if x[1] == tgt)
        out["blinds"].append({"t": round(t, 1), "team": tag[m.team(by)], "by": m.roles[by], "target": m.roles[tgt], "target_class": cls(tgt),
                              "defensive": hit_heal > 0})
    # ---- hexes
    for e in m.o.get("effects", []):
        if e[2] != "h" or e[0] is None or e[5] not in m.PL: continue
        s, en = e[0] / 10, (e[1] / 10 if e[1] is not None else None)
        out["hexes"].append({"t": round(s, 1), "team": tag[m.team(e[5])], "target": m.roles[e[5]], "target_class": cls(e[5]), "hex": F.sname(e[3]),
                             "secs": round(en - s, 1) if en is not None else None, "removed": e[6] in ("hex_removed_lifo",)})
    # ---- fights: peel and casts per player
    blind = _intervals(F, "c", {"blind"}); dazed = _intervals(F, "c", {"dazed"})
    fights = a.get("fights") or []
    by_agent = collections.defaultdict(list)
    for c in casts: by_agent[c[0]].append(c)
    att = collections.defaultdict(list)
    for e in F.ev:
        if e[1] == "at" and e[2] in m.PL: att[e[2]].append(e[0] / 10)
    for fi, f in enumerate(fights):
        t0, t1 = f["start"] - FIGHT_PAD, f["end"] + FIGHT_PAD
        won = {f["team"]: f.get("opponent_won_fight") != f["team"]}
        for p in m.PL:
            ptag = tag[m.team(p)]
            # casts
            cs = [c for c in by_agent.get(p, []) if t0 <= c[2] <= t1]
            if cs:
                cz = F.casting(p, t0, t1); ca = cz["measures"]
                ca["interrupted_after_ready"] = sum(1 for r in cz["casts"] if r["ready_interrupts"] and r["outcome"] == "interrupted")
                out["casts"].append({"fight": fi, "t": f["start"], "team": ptag, "role": m.roles[p], "class": cls(p),
                                     "casts": ca["casts"], "interrupted": ca["interrupted"], "into_ready_interrupt": ca["into_ready_interrupt"],
                                     "interrupted_after_ready": ca["interrupted_after_ready"],
                                     "cancelled_when_threatened": ca["cancelled_when_threatened"], "while_dazed": ca["while_dazed"],
                                     "attacks_while_blind": sum(1 for t in att.get(p, []) if t0 <= t <= t1 and _on(blind, p, t))})
            # frontline peel
            if cls(p) == "frontline":
                own_heal = [h for h in heal if m.team(h) == m.team(p)]
                d = collections.Counter()
                for e in F.events(t0, t1, {"dm"}):
                    if e[2] != p or e[3] not in m.PL or m.team(e[3]) == m.team(p) or not (e[5] or 0): continue
                    tt = e[0] / 10
                    if e[3] in heal: k = "enemy healers"
                    elif any((F.dist(e[3], h, tt) or 1e9) < NEAR_HEALER for h in own_heal if F.alive(h, tt)): k = "attackers of own backline"
                    else: k = "others"
                    d[k] += e[5]
                tot = sum(d.values())
                if tot: out["peel"].append({"fight": fi, "t": f["start"], "team": ptag, "role": m.roles[p], "damage": tot,
                                            "defensive_share": round(d["attackers of own backline"] / tot, 2), "on_healers_share": round(d["enemy healers"] / tot, 2)})
    # ---- spikes
    import events as EV
    for tm in (1, 2):
        for t, tgt, dmg, win, died in EV._spikes(F, tm):
            ld = EV._landing(win)
            out["spikes"].append({"t": round(t, 1), "team": tag[tm], "target": m.roles[tgt], "target_class": cls(tgt), "damage": round(dmg),
                                  "spread_s": ld["spread_s"], "in_1s": ld["in_1s"], "attackers": ld["attackers"], "killed": died})
    # ---- runs (timing and outcome)
    sbrows = a["scoreboard"]; strows = a["state"]
    def row(rows, t): return max([r for r in rows if r["t"] <= t] or rows[:1], key=lambda r: r["t"])
    for r in a["flag_runs"]:
        foe = [x for x in tag.values() if x != r["team"]][0]
        s, st = row(sbrows, r["start"]), row(strows, r["start"])
        runner = F.role_of(r["team"], r["runner"]); ctrl = collections.Counter()
        if runner is not None:
            for c in F.conds_on(runner, r["start"], r["end"]): ctrl[c[2]] += 1
            ctrl["knockdown"] += len(F.kds_on(runner, r["start"], r["end"]))
        own_m, en_m = st[r["team"]]["main"], st[foe]["main"]
        out["runs"].append({"t": r["start"], "team": r["team"], "runner": r["runner"], "secs": r["secs"], "outcome": r["outcome"],
                            "stand": "own" if s["stand"]["owner"] == r["team"] else "enemy" if s["stand"]["owner"] == foe else "nobody",
                            "enemy_boost_in": s["stand"].get("boost_in") if s["stand"]["owner"] == foe else None,
                            "flag_lead": s[r["team"]]["flag_lead"], "main": [own_m, en_m],
                            "enemy_power_play": en_m - own_m >= 1 and s[foe]["flag_lead"] >= 10, "escort": len(r.get("escort") or []),
                            "control_on_runner": dict((k, v) for k, v in ctrl.items() if v), "pushers": len(r.get("pushers") or {}), "min_hp": r.get("min_hp")})
    # ---- splits
    for sp in a.get("splits", []):
        foe = [x for x in tag.values() if x != sp["team"]][0]
        lat = [d["latency"] for d in sp.get("defenders") or []]
        rows = [x for x in strows if sp["start"] <= x["t"] <= sp["end"]]
        drawn = statistics.mean([sum(1 for z in x[foe]["zones"].values() if z in ("own base", "own pit")) for x in rows]) if rows else None
        main_diff = statistics.mean([x[sp["team"]]["main"] - x[foe]["main"] for x in rows]) if rows else None
        out["splits"].append({"t": sp["start"], "team": sp["team"], "size": len(sp["members"]), "members": sp["members"],
                              "entered_base": sp.get("entered_base"), "secs": round(sp["end"] - sp["start"]),
                              "defenders": len(lat), "first_defender_latency": min(lat) if lat else None,
                              "npc_damage": round(sum((sp.get("npc_damage") or {}).values())), "npc_kills": len(sp.get("npc_kills") or []),
                              "pit_kills": sum(1 for k in sp.get("npc_kills") or [] if "outside" not in k["npc"]),
                              "enemies_drawn": round(drawn, 1) if drawn is not None else None, "main_diff": round(main_diff, 1) if main_diff is not None else None,
                              "split_deaths": sum(1 for d in a["deaths"] if d["team"] == sp["team"] and d["victim"] in sp["members"] and sp["start"] <= d["t"] <= sp["end"]),
                              "main_deaths": {t_: sum(1 for d in a["deaths"] if d["team"] == t_ and d["victim"] not in sp["members"] and sp["start"] <= d["t"] <= sp["end"]) for t_ in (sp["team"], foe)}})
    # ---- power plays (all sizes)
    for d in a["decisions"]:
        if d["kind"] != "power_play": continue
        foe = [x for x in tag.values() if x != d["team"]][0]
        try: own, en = map(int, d["state"]["main"].split("v"))
        except ValueError: continue
        out["power"].append({"t": d["t"], "team": d["team"], "size": own - en, "main": d["state"]["main"], "flag_lead": d["state"]["flag_lead"],
                             "enemy_short_because": d.get("enemy_short"), "choice": d["choice"],
                             "kills": d["outcome"]["deaths"].get(foe, 0), "losses": d["outcome"]["deaths"].get(d["team"], 0), "window_s": d["outcome"]["window_s"]})
    # ---- enemy captures, from the defending side
    for r in a["flag_runs"]:
        if r["outcome"] != "captured": continue
        dfn = [x for x in tag.values() if x != r["team"]][0]
        st = row(strows, (r["start"] + r["end"]) / 2); s = row(sbrows, r["start"])
        runner = F.role_of(r["team"], r["runner"]); tmid = (r["start"] + r["end"]) / 2
        dtm = F.team_of(dfn)
        near = min([F.dist(runner, b, tmid) or 1e9 for b in F.players(dtm) if F.alive(b, tmid)] or [1e9]) if runner is not None else None
        duty = {x[0] for x in (s[dfn].get("flag_duty") or [])}
        out["caps"].append({"t": r["end"], "team": r["team"], "defender": dfn, "runner": r["runner"], "secs": r["secs"], "escort": len(r.get("escort") or []),
                            "pushers": len(r.get("pushers") or {}), "min_hp": r.get("min_hp"),
                            "defenders_free": st[dfn]["alive"] - len(duty), "nearest_defender": round(near) if near and near < 1e8 else None})
    return {k: v for k, v in out.items()}


def _rate(xs):
    xs = [x for x in xs if x is not None]
    return (round(statistics.mean(xs), 2), len(xs)) if xs else (None, 0)


def report(ids):
    """What the measures show across matches (descriptive: who won the fight or the match, and outcome rates by
    situation; the node models of step 2 test them as causes on unseen matches)."""
    import tq
    R = {rid: records(rid) for rid in ids}
    win = {}
    for rid in ids:
        mt = tq._analysis(rid)["meta"]; wid = (mt.get("result") or {}).get("winning_team_id")
        win[rid] = next((t["tag"] for t in mt["teams"] if t["id"] == wid), None)
    fw = {}
    for rid in ids:
        for i, f in enumerate(tq._analysis(rid).get("fights") or []):
            fw[(rid, i)] = f.get("opponent_won_fight")
    L = [f"# Event-layer measures (step 1), {len(ids)} matches", "",
         "Descriptive only: each measure split by who won the fight (or how a run, split or power play turned out). "
         "Step 2's node models test these as causes on unseen matches.", ""]
    def by_fight(kind, key, cond=lambda r: True):
        g = {"fight winners": [], "fight losers": []}
        for rid in ids:
            for r in R[rid].get(kind, []):
                if not cond(r): continue
                w = fw.get((rid, r.get("fight")))
                if w is None: continue
                g["fight winners" if w == r["team"] else "fight losers"].append(r[key] if not callable(key) else key(r))
        return g
    # wrong casts
    L.append("## Wrong casts (per player per fight)")
    for cl in ("healer", "midline", "frontline"):
        for key, lab in (("interrupted_after_ready", "interrupted after casting into a ready interrupt (no cancel)"), ("interrupted", "casts interrupted"),
                         ("while_dazed", "casts while Dazed"), ("attacks_while_blind", "attacks while Blind")):
            g = by_fight("casts", key, lambda r, cl=cl: r["class"] == cl)
            a_, b_ = _rate(g["fight winners"]), _rate(g["fight losers"])
            if a_[1] and b_[1]: L.append(f"- {cl}, {lab}: winners {a_[0]} ({a_[1]}), losers {b_[0]} ({b_[1]})")
    L += ["", "## Frontline peel (share of frontline damage, per player per fight)"]
    for key, lab in (("defensive_share", "on attackers of own backline"), ("on_healers_share", "on enemy healers")):
        g = by_fight("peel", key); L.append(f"- {lab}: winners {_rate(g['fight winners'])[0]}, losers {_rate(g['fight losers'])[0]} ({_rate(g['fight winners'])[1]} / {_rate(g['fight losers'])[1]})")
    # strips, blinds, hexes per team-match against match result
    L += ["", "## Strips, Blind and hex removal (per team per match; winners against losers of the match)"]
    def tm_rate(fn):
        g = {"won": [], "lost": []}
        for rid in ids:
            if not win[rid]: continue
            for tg in {r["team"] for k in R[rid].values() for r in k if "team" in r}:
                v = fn(R[rid], tg)
                if v is not None: g["won" if tg == win[rid] else "lost"].append(v)
        return _rate(g["won"]), _rate(g["lost"])
    rows = [("strips per match", lambda x, tg: sum(1 for r in x.get("strips", []) if r["team"] == tg)),
            ("useful share of strips", lambda x, tg: (lambda s: sum(r["useful"] for r in s) / len(s) if s else None)([r for r in x.get("strips", []) if r["team"] == tg])),
            ("prots stripped off targets under attack", lambda x, tg: sum(1 for r in x.get("strips", []) if r["team"] == tg and r["prot"] and r["target_under_attack"])),
            ("wasted removal casts", lambda x, tg: sum(1 for r in x.get("strips_wasted", []) if r["team"] == tg)),
            ("Blinds on enemy frontline", lambda x, tg: sum(1 for r in x.get("blinds", []) if r["team"] == tg and r["target_class"] == "frontline")),
            ("defensive Blinds (on a player hitting own healers)", lambda x, tg: sum(1 for r in x.get("blinds", []) if r["team"] == tg and r["defensive"])),
            ("hexes on own healers removed (share)", lambda x, tg: (lambda h: sum(r["removed"] for r in h) / len(h) if h else None)([r for r in x.get("hexes", []) if r["team"] == tg and r["target_class"] == "healer"])),
            ("median seconds a hex stayed on own healers", lambda x, tg: (lambda h: statistics.median(h) if h else None)([r["secs"] for r in x.get("hexes", []) if r["team"] == tg and r["target_class"] == "healer" and r["secs"] is not None]))]
    for lab, fn in rows:
        w_, l_ = tm_rate(fn); L.append(f"- {lab}: winners {w_[0]}, losers {l_[0]} ({w_[1]} / {l_[1]} team-matches)")
    # spikes
    L += ["", "## Spike timing (kill rate by how tightly the big hits landed)"]
    sp = [r for rid in ids for r in R[rid].get("spikes", [])]
    for lo, hi in ((0, .5), (.5, 1.5), (1.5, 9)):
        g = [r for r in sp if lo <= r["spread_s"] < hi]
        if g: L.append(f"- spread {lo} to {hi} s: killed {sum(r['killed'] for r in g)} of {len(g)} ({sum(r['killed'] for r in g) / len(g):.0%})")
    # runs
    L += ["", "## Run timing (capture rate)"]
    runs = [r for rid in ids for r in R[rid].get("runs", [])]
    def cap(g): return f"{sum(r['outcome'] == 'captured' for r in g)} of {len(g)} ({sum(r['outcome'] == 'captured' for r in g) / len(g):.0%})" if g else "none"
    L.append(f"- into an enemy power play: {cap([r for r in runs if r['enemy_power_play']])}; otherwise {cap([r for r in runs if not r['enemy_power_play']])}")
    for lo, hi in ((0, 30), (30, 60), (60, 121)):
        L.append(f"- enemy holds, its boost in {lo} to {hi} s: {cap([r for r in runs if r['enemy_boost_in'] is not None and lo <= r['enemy_boost_in'] < hi])}")
    L.append(f"- runner Crippled during the run: {cap([r for r in runs if r['control_on_runner'].get('crippled')])}; not: {cap([r for r in runs if not r['control_on_runner'].get('crippled')])} "
             "(read with care: runs that get far are the ones that get Crippled; the run-outcome node of step 2 reads it at the same point of the run)")
    L.append(f"- runner knocked down: {cap([r for r in runs if r['control_on_runner'].get('knockdown')])}")
    # enemy captures
    L += ["", "## Enemy captures (from the defending side)"]
    caps = [r for rid in ids for r in R[rid].get("caps", [])]
    if caps:
        L.append(f"- captures: {len(caps)}; runner never pushed: {sum(1 for r in caps if not r['pushers'])}; median run {statistics.median(r['secs'] for r in caps)} s; "
                 f"median defenders free {statistics.median(r['defenders_free'] for r in caps)}; nearest defender at mid-run, median {statistics.median([r['nearest_defender'] for r in caps if r['nearest_defender']] or [0])}")
    # splits
    L += ["", "## Splits"]
    sps = [r for rid in ids for r in R[rid].get("splits", [])]
    base = [r for r in sps if r["entered_base"] is not None]
    L.append(f"- splits: {len(sps)}, into the base: {len(base)}")
    for lo, hi, lab in ((-999, 15, "answered on time (15 s or less)"), (15, 60, "answered in 15 to 60 s"), (60, 9999, "answered after 60 s")):
        g = [r for r in base if r["first_defender_latency"] is not None and lo <= r["first_defender_latency"] < hi]
        if g: L.append(f"- {lab}: {len(g)}; pit NPCs killed per split {statistics.mean(r['pit_kills'] for r in g):.2f}, split deaths {statistics.mean(r['split_deaths'] for r in g):.2f}")
    g = [r for r in base if r["first_defender_latency"] is None]
    if g: L.append(f"- never answered: {len(g)}; pit NPCs killed per split {statistics.mean(r['pit_kills'] for r in g):.2f}")
    for n in (1, 2, 3):
        g = [r for r in sps if (r["size"] == n if n < 3 else r["size"] >= 3)]
        if g: L.append(f"- size {n}{'+' if n == 3 else ''}: {len(g)}; enemies drawn {statistics.mean(r['enemies_drawn'] or 0 for r in g):.1f}, own main minus enemy main {statistics.mean(r['main_diff'] or 0 for r in g):+.1f}, pit kills {statistics.mean(r['pit_kills'] for r in g):.2f}")
    # power plays
    L += ["", "## Power plays (all sizes)"]
    pp = [r for rid in ids for r in R[rid].get("power", [])]
    for n in (1, 2, 3):
        g = [r for r in pp if (r["size"] == n if n < 3 else r["size"] >= 3)]
        if g: L.append(f"- {n}{'+' if n == 3 else ''} up: {len(g)}; killed in {sum(1 for r in g if r['kills'])} ({sum(1 for r in g if r['kills']) / len(g):.0%}); lost a player in {sum(1 for r in g if r['losses'])}")
    why = collections.Counter()
    for r in pp:
        for k, v in (r["enemy_short_because"] or {}).items(): why[k] += v
    if why: L.append("- why the enemy was short (player-seconds): " + ", ".join(f"{k} {v}" for k, v in why.most_common(6)))
    return L


def records(rid):
    import cache
    return cache.prepared("eventlayer", rid, lambda: build(rid))


if __name__ == "__main__":
    if sys.argv[1:2] == ["report"]:
        import model as M, os
        from common import REPO
        bs = M.batches(); ids = [m for b in bs[-2:] for m in b["matches"]] if "--all" not in sys.argv else [m for b in bs for m in b["matches"]]
        L = report(ids); open(os.path.join(REPO, "data", "model", "reports", "measures.md"), "w").write("\n".join(L) + "\n"); print("\n".join(L)); sys.exit()
    rec = build(sys.argv[1])
    for k, v in rec.items(): print(k, len(v), json.dumps(v[:2], ensure_ascii=False)[:400])
