"""The event layer (step 1 of the learned causal map, Denning 2026-11-07): every play the causal chains need, measured
in every match as time-stamped records, so node models can learn from them and chains can be built from data.

Per match (cached: cache.prepared("eventlayer", rid)), lists of records:
  strips     every enchantment stripped: who stripped, from whom (healer, midline, frontline), the enchantment, whether it
             was a prot, whether the stripper's team was hitting that target (3 s), useful = a prot off a target under
             attack, or an enchantment off a midline/frontline player (defensive strip); plus removal casts that removed
             nothing (wasted)
  blinds     every Blind put on an enemy, with when it ended (time spent Blind is what counts, Denning): on a frontline
             player or not, on a physical attacker or not, and whether that player had hit the blinder's healers in the
             3 s before (defensive Blind)
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
Step 2a (Denning: what counts as right comes from data, not a list):
  strips     plus "available": every enchantment on an enemy within cast range of the stripper at that moment, so the
             strip can be judged against the best target it had (values: values(), read at use, never cached)
  hex_removals  every hex-removal cast on an ally: the hex it removed (or none), how long it had been on, and every hex
             on allies within the remover's cast range at that moment (the choice it had)
  hexes      plus the target's output change while hexed, and its same-class allies' change over the same seconds, the
             data behind each hex's measured cost
  casts      plus damage on enemy players and the fight's seconds (damage output against the role's usual, at use)
  team       per team, 5 s buckets of damage on enemy players and healing; prot casts; uptime of every enchantment and
             hex; each skill's recorded output in the match (gvg.report: damage + healing + damage prevented)
Values (values(ids) -> data/benchmarks/eventlayer_values.json, rebuilt from the cached records, read with valued()):
  an enchantment's value per second = its recorded output (damage + healing + prevented) over its uptime + the drop in
  the bearer's output in the 10 s after a strip (energy enchantments such as attunements record no output of their
  own); a hex's value per second = its recorded damage over its uptime + the drop in the hexed player's output while it
  was on (against the same length before and after). Both drops take out the fight's own rise or fall: the change for
  allies of the same class over the same seconds is subtracted. Negative values read as 0 (no measurable cost). A
  role's usual damage = median damage per second per player per fight on enemy players.
Usage:  python3 eventlayer.py <report id>      prints a summary of the match's records"""
import bisect, collections, glob, json, os, statistics, sys

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


def _is_heal(x): return x[2] == "hl"


def _on(iv, a, t):
    return any(s <= t <= e for s, e in iv.get(a, ()))


def norm(name):
    """Skill names joined across sources (replay effects, match records): PvP suffixes dropped."""
    return str(name).replace(" (PvP)", "").replace(" PvP", "").strip()


_MATCHES = None
def _match_players(rid):
    """gvg.report's per-player record of the match (data/matches): {skill id: [casts, damage, healing, prevented, ...]}."""
    global _MATCHES
    if _MATCHES is None:
        from common import REPO
        _MATCHES = {}
        for f in glob.glob(os.path.join(REPO, "data", "matches", "20*.json")):
            for r in json.load(open(f)): _MATCHES[r["id"]] = r.get("players") or []
    return _MATCHES.get(rid, [])


BUCKET = 5
_IDN = None
def _id_names():
    global _IDN
    if _IDN is None:
        from forensics import skilldata
        _IDN = {str(d.get("id")): k for k, d in skilldata().items() if d.get("id") is not None}
    return _IDN


VALUES_PATH = None
def _values_path():
    from common import REPO
    return os.path.join(REPO, "data", "benchmarks", "eventlayer_values.json")


MIN_N = 20      # below this many cases a role's usual damage falls back to its class (healer, midline, frontline)


def values(ids, save=True):
    """Measured values from the cached records of ids (Denning: right targets and right hexes come from data).
    enchantments / hexes: value per second; roles: usual damage per second per player per fight."""
    out_e, up_e, out_h, up_h = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    drops = collections.defaultdict(list); sdrops = collections.defaultdict(list); role_d = collections.defaultdict(list); cls_d = collections.defaultdict(list)
    for rid in ids:
        R = records(rid)
        tm = (R.get("team") or [{}])[0]
        so = tm.get("skill_output") or {}
        for k, v in (tm.get("ench_uptime") or {}).items():
            up_e[k] += v; out_e[k] += so.get(k, 0)
        for k, v in (tm.get("hex_uptime") or {}).items():
            up_h[k] += v; out_h[k] += so.get(k, 0)
        for h in R.get("hexes", []):
            if h.get("out_change") is not None and h.get("allies_out_change") is not None:
                drops[norm(h["hex"])].append(h["allies_out_change"] - h["out_change"])
        for r in R.get("strips", []):
            if r.get("out_change") is not None and r.get("allies_out_change") is not None:
                sdrops[norm(r["enchantment"])].append(r["allies_out_change"] - r["out_change"])
        for c in R.get("casts", []):
            if c.get("secs"):
                role_d[c["role"]].append(c.get("damage", 0) / c["secs"]); cls_d[c["class"]].append(c.get("damage", 0) / c["secs"])
    ench = {}
    for k in set(up_e) | set(sdrops):
        d = sdrops.get(k, [])
        direct = out_e[k] / up_e[k] if up_e[k] >= 30 else 0.0
        drop = statistics.mean(d) if len(d) >= 5 else 0.0
        ench[k] = {"per_s": round(direct + drop, 2), "direct_per_s": round(direct, 2), "strip_output_drop_per_s": round(drop, 2), "strips": len(d), "uptime_s": up_e[k]}
    hexes = {}
    for k in set(up_h) | set(drops):
        d = drops.get(k, [])
        direct = out_h[k] / up_h[k] if up_h[k] >= 30 else 0.0
        drop = statistics.mean(d) if len(d) >= 5 else 0.0
        hexes[k] = {"per_s": round(direct + drop, 2), "direct_per_s": round(direct, 2), "output_drop_per_s": round(drop, 2), "n": len(d), "uptime_s": up_h[k]}
    roles = {k: {"median": round(statistics.median(v), 1), "n": len(v)} for k, v in role_d.items()}
    classes = {k: {"median": round(statistics.median(v), 1), "n": len(v)} for k, v in cls_d.items()}
    V = {"about": "eventlayer.values(): measured from the cached event-layer records of every trained match. enchantments: "
                  "recorded output (damage + healing + prevented) per second of uptime, plus the drop in the bearer's output (damage + "
                  "healing per second) in the 10 s after it was stripped against the 10 s before, less the same change for its "
                  "allies of the same class (5+ strips); hexes: recorded damage per second of "
                  "uptime plus the drop in the hexed player's output (damage + healing per second) while it was on, against the "
                  "same length before and after, less the same change for its allies of the same class over the same seconds (5+ cases); roles: median damage per second on enemy players per player per fight.",
         "matches": len(ids), "enchantments": ench, "hexes": hexes, "roles": roles, "classes": classes}
    if save: json.dump(V, open(_values_path(), "w"), indent=1)
    return V


_V = None
def load_values():
    global _V
    if _V is None:
        _V = json.load(open(_values_path())) if os.path.exists(_values_path()) else None
    return _V


def usual_dps(V, role, cl):
    r = V["roles"].get(role)
    if r and r["n"] >= MIN_N: return r["median"]
    c = V["classes"].get(cl); return c["median"] if c else None


def ench_value(V, name): return max(0.0, (V["enchantments"].get(norm(name)) or {}).get("per_s", 0.0))
def hex_value(V, name): return max(0.0, (V["hexes"].get(norm(name)) or {}).get("per_s", 0.0))


def valued(R, V):
    """The step 2a judgements on a match's records: each strip against the best enchantment it could have stripped,
    each hex removal against the most costly hex it could have removed, each player's fight damage against its role's
    usual. Adds fields in place and returns R."""
    for r in R.get("strips", []):
        v = ench_value(V, r["enchantment"]); best = max([ench_value(V, x[0]) for x in r.get("available") or []] + [v])
        r["value"], r["best_value"] = v, best
        r["right_target"] = best <= 0 or v >= best * 0.999
        r["value_share"] = round(v / best, 2) if best > 0 else None
    for r in R.get("hex_removals", []):
        v = hex_value(V, r["removed"]) if r.get("removed") else 0.0
        best = max([hex_value(V, x[0]) for x in r.get("available") or []] + [v])
        r["value"], r["best_value"] = v, best
        r["right_hex"] = bool(r.get("removed")) and (best <= 0 or v >= best * 0.999)
        r["value_share"] = round(v / best, 2) if best > 0 else None
    for r in R.get("hexes", []): r["value"] = hex_value(V, r["hex"])
    for r in R.get("casts", []):
        u = usual_dps(V, r["role"], r["class"])
        r["dps"] = round(r.get("damage", 0) / r["secs"], 1) if r.get("secs") else None
        r["dps_v_usual"] = round(r["dps"] / u, 2) if u and r["dps"] is not None else None
    return R


def build(rid):
    from forensics import Forensics
    import tq
    F = Forensics(rid); m = F.m; a = tq._analysis(rid)
    tag = F.tag; heal = F.healers
    from common import line
    cls = lambda b: "healer" if b in heal else ("frontline" if line(m, b) == "frontline" else "midline")
    out = collections.defaultdict(list)
    casts = F.casts()
    from common import CAST_R, PROT_SKILLS
    end_t = (F.T[-1] / 10) if F.T else 0
    ench_iv, hex_iv = collections.defaultdict(list), collections.defaultdict(list)
    upt = {"e": collections.Counter(), "h": collections.Counter()}
    for e in m.o.get("effects", []):
        if e[2] not in ("e", "h") or e[0] is None or e[5] not in m.PL: continue
        s0, s1 = e[0] / 10, (e[1] / 10 if e[1] is not None else end_t)
        (ench_iv if e[2] == "e" else hex_iv)[e[5]].append((s0, s1, F.sname(e[3]), e))
        upt[e[2]][norm(F.sname(e[3]))] += max(0.0, s1 - s0)
    def on_now(iv, a, t): return [x for x in iv.get(a, ()) if x[0] <= t <= x[1]]
    # output (damage on enemy players + healing on allies) per agent, and team buckets
    outp = collections.defaultdict(list); nb = int(end_t // BUCKET) + 1
    dmg5 = {tg: [0] * nb for tg in tag.values()}; heal5 = {tg: [0] * nb for tg in tag.values()}
    for e in F.ev:
        if e[1] not in ("dm", "hl") or e[2] not in m.PL or e[3] not in m.PL or not (e[5] or 0) or e[0] is None or e[0] < 0: continue
        same = m.team(e[2]) == m.team(e[3])
        if (e[1] == "dm" and same) or (e[1] == "hl" and not same): continue
        outp[e[2]].append((e[0] / 10, e[5], e[1]))
        b = min(int(e[0] / 10 // BUCKET), nb - 1)
        (dmg5 if e[1] == "dm" else heal5)[tag[m.team(e[2])]][b] += e[5]
    for k in outp: outp[k].sort()
    otimes = {k: [x[0] for x in v] for k, v in outp.items()}
    def out_rate(a, t0, t1):
        if t1 - t0 < 0.5: return None
        L, T = outp.get(a, []), otimes.get(a, [])
        i, j = bisect.bisect_left(T, t0), bisect.bisect_right(T, t1)
        return round(sum(x[1] for x in L[i:j]) / (t1 - t0), 1)
    def change(a, base_w, test_w):
        """(a's output change from base windows to the test window, the same change for its allies of the same class):
        the difference is the effect on a, with the fight's own rise or fall taken out (difference in differences)."""
        def ch(x):
            b = [r for r in (out_rate(x, *w) for w in base_w) if r is not None]
            d = out_rate(x, *test_w)
            return (d - statistics.mean(b)) if b and d is not None else None
        own = ch(a)
        if own is None: return None, None
        t_ = test_w[0]
        al = [b for b in m.PL if b != a and m.team(b) == m.team(a) and cls(b) == cls(a) and F.alive(b, t_)]
        al = al or [b for b in m.PL if b != a and m.team(b) == m.team(a) and F.alive(b, t_)]
        oc = [v for v in (ch(b) for b in al) if v is not None]
        return round(own, 1), (round(statistics.mean(oc), 1) if oc else None)
    sk_out = collections.Counter()
    for p in _match_players(m.o["meta"]["id"]):
        for sid, v in (p.get("sk") or {}).items():
            try: nm = F.sname(int(sid))
            except ValueError: continue
            if nm == str(sid): nm = _id_names().get(str(sid), nm)
            sk_out[norm(nm)] += (v[1] or 0) + (v[2] or 0) + (v[3] or 0)
    out["team"] = [{"dmg5": dmg5, "heal5": heal5, "bucket_s": BUCKET, "ench_uptime": {k: round(v) for k, v in upt["e"].items()},
                    "hex_uptime": {k: round(v) for k, v in upt["h"].items()}, "skill_output": dict(sk_out),
                    "prot_casts": [[round(c[3], 1), tag[m.team(c[0])]] for c in casts if c[4] == "finished" and c[0] in m.PL and F.sname(c[1]) in PROT_SKILLS],
                    "players": {tg: [m.roles[p] for p in m.PL if tag[m.team(p)] == tg] for tg in tag.values()}}]
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
        avail = []
        for b in F.players(m.team(tgt)):
            if not F.alive(b, by[0]) or (F.dist(by[1], b, by[0]) or 1e9) > CAST_R: continue
            for x in on_now(ench_iv, b, by[0] - 0.1): avail.append([norm(x[2]), cls(b)])
        own_ch, ally_ch = change(tgt, [(t - 10, t)], (t, t + 10)) if t + 10 <= end_t else (None, None)
        out["strips"].append({"t": round(t, 1), "team": tag[m.team(by[1])], "by": m.roles[by[1]], "skill": by[2], "target": m.roles[tgt],
                              "target_class": cls(tgt), "enchantment": F.sname(e[3]), "prot": prot, "target_under_attack": hit >= 100,
                              "useful": (prot and hit >= 100) or (not prot and cls(tgt) != "healer"), "available": avail,
                              "out_change": own_ch, "allies_out_change": ally_ch})
    for tgt, L in rm_casts.items():
        for end, by, sk in L:
            if (tgt, end, by) not in used:
                out["strips_wasted"].append({"t": round(end, 1), "team": tag[m.team(by)], "by": m.roles[by], "skill": sk, "target": m.roles[tgt]})
    # ---- Blind on enemies
    for e in m.o.get("effects", []):
        # the caster is unknown for over half of the Blinds in the replays (44% known in 133 matches): the Blind is credited
        # to the target's opponents, which is all the time-Blind measures need
        if e[2] != "c" or e[7] != "blind" or e[0] is None or e[5] not in m.PL: continue
        if e[4] in m.PL and m.team(e[4]) == m.team(e[5]): continue
        t = e[0] / 10; tgt, by = e[5], e[4]
        foe_tm = next(x for x in {m.team(q) for q in m.PL} if x != m.team(tgt))
        own_heal = [h for h in heal if m.team(h) == foe_tm]
        hit_heal = sum(x[3] for h in own_heal for x in F.damage_on(h, t - 3, t) if x[1] == tgt)
        # Denning: the time spent Blind matters, not the number of Blinds. end = when the Blind ended (expired, removed or
        # the target died; the match end if never seen ending); attacker = a player whose damage comes from attacks
        # (frontline, rangers, paragons), the only players Blind slows
        t_end = min(e[1] / 10, end_t) if e[1] is not None else end_t
        out["blinds"].append({"t": round(t, 1), "end": round(max(t_end, t), 1), "team": tag[foe_tm], "by": m.roles[by] if by in m.PL else None, "target": m.roles[tgt],
                              "target_class": cls(tgt), "attacker": cls(tgt) == "frontline" or m.A[tgt].get("p") in ("Ranger", "Paragon"),
                              "defensive": hit_heal > 0})
    # ---- hex removal casts on allies: what was removed and what the remover could have chosen
    removed_by = {}
    for c in casts:
        if c[4] != "finished" or c[0] not in m.PL or c[5] not in m.PL or m.team(c[5]) != m.team(c[0]): continue
        if "Hex spell" not in (F.sdata(c[1]).get("removes") or []): continue
        t = c[3]; tgt = c[5]
        gone = [x for x in hex_iv.get(tgt, ()) if -0.5 <= x[1] - t <= 1.0 and x[0] < t and id(x[3]) not in removed_by]
        hit = min(gone, key=lambda x: abs(x[1] - t), default=None)
        if hit: removed_by[id(hit[3])] = t
        avail = []
        for b in F.players(m.team(c[0])):
            if not F.alive(b, t) or (b != c[0] and (F.dist(c[0], b, t) or 1e9) > CAST_R): continue
            for x in on_now(hex_iv, b, t - 0.1): avail.append([norm(x[2]), cls(b), round(t - x[0], 1)])
        out["hex_removals"].append({"t": round(t, 1), "team": tag[m.team(c[0])], "by": m.roles[c[0]], "skill": F.sname(c[1]), "target": m.roles[tgt],
                                    "target_class": cls(tgt), "removed": norm(hit[2]) if hit else None,
                                    "secs_on": round(t - hit[0], 1) if hit else None, "available": avail})
    # ---- hexes
    for e in m.o.get("effects", []):
        if e[2] != "h" or e[0] is None or e[5] not in m.PL: continue
        s, en = e[0] / 10, (e[1] / 10 if e[1] is not None else None)
        span = min((en if en is not None else end_t) - s, 10)
        out["hexes"].append({"t": round(s, 1), "team": tag[m.team(e[5])], "target": m.roles[e[5]], "target_class": cls(e[5]), "hex": F.sname(e[3]),
                             "secs": round(en - s, 1) if en is not None else None, "removed": id(e) in removed_by or e[6] == "hex_removed_lifo",
                             **dict(zip(("out_change", "allies_out_change"), change(e[5], [(s - span, s)] + ([(en, en + span)] if en is not None and en + span <= end_t else []), (s, s + span)) if span >= 1 else (None, None)))})
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
                                     "attacks_while_blind": sum(1 for t in att.get(p, []) if t0 <= t <= t1 and _on(blind, p, t)),
                                     "damage": round(sum(x[1] for x in outp.get(p, []) if t0 <= x[0] <= t1 and not _is_heal(x))), "secs": round(t1 - t0)})
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
        runner = F.role_of(r["team"], r["runner"]); ctrl = collections.Counter(); ctimes, dtimes = [], []
        if runner is not None:
            for c in F.conds_on(runner, r["start"], r["end"]): ctrl[c[2]] += 1; ctimes.append([round(c[0] - r["start"], 1), c[2]])
            kds = F.kds_on(runner, r["start"], r["end"]); ctrl["knockdown"] += len(kds)
            for k in kds: ctimes.append([round((k[0] if isinstance(k, (list, tuple)) else k) - r["start"], 1), "knockdown"])
            dtimes = [[round(x[0] - r["start"], 1), round(x[3])] for x in F.damage_on(runner, r["start"], r["end"])]
        own_m, en_m = st[r["team"]]["main"], st[foe]["main"]
        out["runs"].append({"t": r["start"], "team": r["team"], "runner": r["runner"], "secs": r["secs"], "outcome": r["outcome"], "hold": bool(r.get("hold")),
                            "stand": "own" if s["stand"]["owner"] == r["team"] else "enemy" if s["stand"]["owner"] == foe else "nobody",
                            "enemy_boost_in": s["stand"].get("boost_in") if s["stand"]["owner"] == foe else None,
                            "flag_lead": s[r["team"]]["flag_lead"], "main": [own_m, en_m],
                            "enemy_power_play": en_m - own_m >= 1 and s[foe]["flag_lead"] >= 10, "escort": len(r.get("escort") or []),
                            "control_on_runner": dict((k, v) for k, v in ctrl.items() if v), "pushers": len(r.get("pushers") or {}), "min_hp": r.get("min_hp"),
                            "control_times": ctimes, "damage_times": dtimes, "pusher_first": sorted(round(v["first"] - r["start"]) for v in (r.get("pushers") or {}).values())})
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
                             "kills": d["outcome"]["deaths"].get(foe, 0), "losses": d["outcome"]["deaths"].get(d["team"], 0), "window_s": d["outcome"]["window_s"],
                             "first_kill": d.get("first_kill")})
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
    # step 2a
    V = load_values()
    if V:
        for rid in ids: valued(R[rid], V)
        L += ["", "## Step 2a: right strip targets, right hexes removed, damage against the role's usual",
              "Values from data (eventlayer_values.json): enchantments by recorded output per second up, hexes by recorded "
              "damage plus the drop in the hexed player's output."]
        top_e = sorted(V["enchantments"].items(), key=lambda kv: -kv[1]["per_s"])[:8]
        L.append("- most valuable enchantments to strip (per second up): " + ", ".join(f"{k} {v['per_s']}" for k, v in top_e))
        top_h = sorted(V["hexes"].items(), key=lambda kv: -kv[1]["per_s"])[:8]
        L.append("- most costly hexes (per second on): " + ", ".join(f"{k} {v['per_s']} (direct {v['direct_per_s']}, output drop {v['output_drop_per_s']}, {v['n']})" for k, v in top_h))
        more = [("strips on the best target in range (share)", lambda x, tg: (lambda s_: sum(r["right_target"] for r in s_) / len(s_) if s_ else None)([r for r in x.get("strips", []) if r["team"] == tg and r.get("available")])),
                ("hex removals that took the most costly hex in range (share)", lambda x, tg: (lambda s_: sum(r["right_hex"] for r in s_) / len(s_) if s_ else None)([r for r in x.get("hex_removals", []) if r["team"] == tg and r.get("available")])),
                ("value-weighted seconds a removed hex stayed on", lambda x, tg: (lambda s_: sum(r["value"] * r["secs_on"] for r in s_) / sum(r["value"] for r in s_) if s_ and sum(r["value"] for r in s_) > 0 else None)([r for r in x.get("hex_removals", []) if r["team"] == tg and r.get("removed") and r["value"] > 0]))]
        for lab, fn in more:
            w_, l_ = tm_rate(fn); L.append(f"- {lab}: winners {w_[0]}, losers {l_[0]} ({w_[1]} / {l_[1]} team-matches)")
        for cl in ("healer", "midline", "frontline"):
            g = by_fight("casts", "dps_v_usual", lambda r, cl=cl: r["class"] == cl and r.get("dps_v_usual") is not None)
            a_, b_ = _rate(g["fight winners"]), _rate(g["fight losers"])
            if a_[1] and b_[1]: L.append(f"- {cl}, damage against the role's usual: winners {a_[0]} ({a_[1]}), losers {b_[0]} ({b_[1]})")
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


def _warm_one(rid):
    records(rid); return rid


def warm(ids):
    """Build every match's records side by side (all cores); cached afterwards."""
    import multiprocessing as mp
    with mp.Pool(max(1, mp.cpu_count())) as p:
        for _ in p.imap_unordered(_warm_one, ids): pass


if __name__ == "__main__":
    if sys.argv[1:2] == ["values"]:
        import model as M
        warm([m for b in M.batches() for m in b["matches"]])
        V = values([m for b in M.batches() for m in b["matches"]]); print(json.dumps({k: (len(v) if isinstance(v, dict) else v) for k, v in V.items()})); sys.exit()
    if sys.argv[1:2] == ["report"]:
        import model as M, os
        from common import REPO
        bs = M.batches(); ids = [m for b in bs[-2:] for m in b["matches"]] if "--all" not in sys.argv else [m for b in bs for m in b["matches"]]
        L = report(ids); open(os.path.join(REPO, "data", "model", "reports", "measures.md"), "w").write("\n".join(L) + "\n"); print("\n".join(L)); sys.exit()
    rec = build(sys.argv[1])
    for k, v in rec.items(): print(k, len(v), json.dumps(v[:2], ensure_ascii=False)[:400])
