"""Rows for the learned node models (learnednodes.py), kept apart so a change to the fitting never rebuilds them
(cache kind "lrows" is keyed by this file and what it imports)."""
import collections, hashlib, json, math, statistics
CHECKPOINTS = (5, 15, 30)
CLIP = 150
NEVER = 60
CAP_AT = 10



def _blind_secs(blinds, t0, t1):
    """Seconds spent Blind inside [t0, t1], added over the players Blinded (Denning: time Blind, not the count).
    Overlapping Blinds on one player count once."""
    by = {}
    for r in blinds:
        e = r.get("end", r["t"] + 3)        # records from before the end was kept: Blind's usual few seconds
        s, e = max(r["t"], t0), min(e, t1)
        if e > s: by.setdefault(r["target"], []).append((s, e))
    tot = 0.0
    for iv in by.values():
        iv.sort(); cs, ce = iv[0]
        for s, e in iv[1:]:
            if s > ce: tot += ce - cs; cs, ce = s, e
            else: ce = max(ce, e)
        tot += ce - cs
    return round(tot, 1)

def _ctx(rid):
    """What every node's rows need from one match."""
    import tq, eventlayer as EL
    from replaylib import Match
    from state import GameState, d
    from strength import strength_gap
    from buildfeat import matchup
    a = tq._analysis(rid); R = EL.records(rid)
    st = GameState(Match.from_branch(rid)); m = st.m
    tags = [t["tag"] for t in a["meta"]["teams"]]
    tm_of = {m.tag[k]: k for k in (1, 2)}
    gaps = {}
    for tm in (1, 2):
        gaps[m.tag[tm]] = strength_gap(m.o["meta"]["id"], m.tag[tm], m.o["meta"].get("started"), m.tag[3 - tm],
                                       {x["tag"]: x.get("rating") for x in m.o["meta"]["teams"]},
                                       {m.tag[k]: [m.nm(x) for x in m.PL if m.team(x) == k] for k in (1, 2)})[1]
    mus = {m.tag[tm]: matchup(m, tm) for tm in (1, 2)}
    run_dist = {}
    for tg, tm in tm_of.items():
        try: run_dist[tg] = round(d(st.geo.spawn[tm], st.geo.stand))
        except Exception: run_dist[tg] = None
    return a, R, st, m, tags, tm_of, gaps, mus, run_dist


def _row(rows, t):
    best = None
    for r in rows:
        if r["t"] <= t: best = r
        else: break
    return best or rows[0]


def _short(why):
    tot = sum((why or {}).values()) or 1
    g = lambda ks: round(sum((why or {}).get(k, 0) for k in ks) / tot, 2)
    return {"short_dead": g(["dead"]), "short_running": g(["running flag"]), "short_backside": g(["backside", "push side"]),
            "short_base": g(["own base", "own pit", "enemy base", "enemy pit"])}


def _power_near(st, P, tm, at, t, r=1300, kind="snare"):
    """Snare (or speed) power of team tm's live players within r of agent at, at t seconds (movepower.py)."""
    from state import d
    p0 = st.pos(at, t)[0] if at is not None else None
    if p0 is None: return None
    return round(sum(P[b][kind] for b in st.players[tm] if st.alive(b, t) and st.pos(b, t)[0] and d(st.pos(b, t)[0], p0) <= r), 1)


def _min_capture(st, m, a, t):
    """Seconds the carrier would need at least to bring the flag to the stand from where it is at t (Denning: the
    runner's speed skills set the minimum time required to capture): distance / its fastest expected carry speed."""
    import movepower
    from common import CARRY_SPEED
    from state import d
    p0 = st.pos(a, t)[0] if a is not None else None
    if p0 is None: return None
    return round(d(p0, st.geo.stand) / movepower.carry_speed(m, a, CARRY_SPEED), 1)


# variables discovery found and Denning approved (2026-11-08; discover.py, knowledge/discovery.md), joined from the
# win model's state table and the build features at the row's moment (same team, the 5 s state at or before)
APPROVED = {
    "fight_outcome": ["morale_diff", "fight_state", "down_diff_s", "alive_diff", "stand", "spike_killable_diff"],
    "flag_swing": ["morale_diff"],
    "run_defence": ["boost_clock", "stand", "flag_lead", "morale_diff", "down_diff_s", "b.own_snares"],
    "split_effect": ["morale_diff", "flag_lead", "lord_damage_diff", "b.enemy_prots"],
    "run_outcome": ["morale_diff", "boost_clock", "b.enemy_snares"],
    "power_play": ["down_diff_s", "carrying_diff"],
    "split_chance": ["split_diff", "turtle_diff", "pit_pressure_diff"],
    "split_answer": ["split_diff"],
}


def _approved(node, rows, rid, m):
    """Join the approved discoveries onto the rows (b. = build feature, else the state table)."""
    want = APPROVED.get(node)
    if not want or not rows: return rows
    import model as M
    from buildfeat import matchup
    tab = {(r["team"], int(r["t"])): r for r in M.match_table(rid)}
    build = {m.tag[tm]: matchup(m, tm) for tm in (1, 2)}
    for r in rows:
        t5 = int(r["t"]) - int(r["t"]) % 5
        st_ = tab.get((r["team"], t5)) or tab.get((r["team"], t5 - 5)) or {}
        for v in want:
            name = v.split(".", 1)[1] if v.startswith("b.") else v
            if name in r: continue
            r[name] = (build.get(r["team"]) or {}).get(name) if v.startswith("b.") else st_.get(v)
    return rows


def _healer_share(m, ev, team, t0, t1):
    """Share of team's damage on enemy players that landed on enemy healers in [t0, t1] (seconds): Bounty's 'going
    after the monks', measured (Denning, after Bounty's and Nick's commentary)."""
    from phases import healer
    on_h = tot = 0
    for e in ev:
        if e[0] < t0 * 10: continue
        if e[0] > t1 * 10: break
        if e[1] != "dm" or not (e[5] or 0) > 0 or e[2] not in m.PL or m.team(e[2]) != team: continue
        b = e[3]
        if not isinstance(b, int) or b >= len(m.A) or not m.A[b].get("player") or m.team(b) == team: continue
        tot += e[5]
        if healer(m, b): on_h += e[5]
    return round(on_h / tot, 2) if tot else None


def _team_dps(team, tg, t0, t1, V, alive_roles):
    """A team's damage on enemy players per second in [t0, t1] against the sum of the usual of the players alive."""
    import eventlayer as EL
    b = team["bucket_s"]; L = team["dmg5"][tg]
    i0, i1 = int(t0 // b), max(int(t0 // b) + 1, int(math.ceil(t1 / b)))
    dmg = sum(L[i0:i1]); secs = (i1 - i0) * b
    us = sum(EL.usual_dps(V, r, None) or 0 for r in alive_roles)
    return round(dmg / secs / us, 2) if us and secs else None


def _build(node, rid, V):
    import eventlayer as EL
    a, R, st, m, tags, tm_of, gaps, mus, run_dist = _ctx(rid)
    R = EL.valued(json.loads(json.dumps(R)), V)
    sb, sr = a["scoreboard"], a["state"]
    foe = lambda tg: tags[1] if tg == tags[0] else tags[0]
    team = (R.get("team") or [{}])[0]
    roles_alive = lambda tg, t: (_row(sr, t)[tg].get("main_roles") or []) if sr else []
    deaths = a["deaths"]
    import movepower as MP
    from common import runner_code
    P = MP.powers(m)
    ev = sorted((e for e in m.o.get("ev") or [] if e[0] is not None), key=lambda e: e[0])
    def agent_of(tg, role):
        return next((x for x in st.players[tm_of[tg]] if m.roles.get(x) == role), None)
    def team_power(tg, kind):
        return round(sum(P[x][kind] for x in st.players[tm_of[tg]]), 1)
    rows = []
    def add(tg, t, y, **f):
        rows.append({"match": rid, "team": tg, "t": t, "y": y, **f})
    if node == "run_outcome":
        rec = {(r["team"], r["t"]): r for r in R.get("runs", [])}
        for fr in a["flag_runs"]:
            r = rec.get((fr["team"], fr["start"]))
            if not r: continue
            tg = fr["team"]
            for k in CHECKPOINTS:
                if fr["secs"] <= k: continue
                ct = [c for c in r.get("control_times") or [] if c[0] <= k]
                add(tg, fr["start"] + k, int(fr["outcome"] == "captured"), checkpoint_s=k,
                    stand_own=int(r["stand"] == "own"), stand_enemy=int(r["stand"] == "enemy"), enemy_boost_in=r["enemy_boost_in"],
                    flag_lead=max(min(r["flag_lead"], CLIP), -CLIP), runner_line={"frontline": 0, "midline": 1, "backline": 2}.get(fr.get("line")),
                    escort=r["escort"], own_main=r["main"][0], enemy_main=r["main"][1], enemy_power_play=int(r["enemy_power_play"]),
                    crippled_so_far=int(any(c[1] == "crippled" for c in ct)), knocked_down_so_far=sum(1 for c in ct if c[1] == "knockdown"),
                    other_control_so_far=sum(1 for c in ct if c[1] not in ("crippled", "knockdown")),
                    damage_so_far=sum(x[1] for x in r.get("damage_times") or [] if x[0] <= k),
                    pushers_so_far=sum(1 for x in r.get("pusher_first") or [] if x <= k),
                    min_capture_s=_min_capture(st, m, ra := agent_of(tg, fr["runner"]), fr["start"] + k),
                    runner_class=runner_code(m, ra) if ra is not None else None,
                    runner_escapes=P[ra]["escapes"] if ra is not None else None,
                    enemy_snare_near=_power_near(st, P, tm_of[foe(tg)], ra, fr["start"] + k),
                    run_dist=run_dist.get(tg), strength_gap=gaps[tg])
    elif node == "flag_swing":
        by_t = {r["t"]: r for r in sb}; i = 0
        for r in sb:
            t = r["t"]
            if t < 20 or t % 20 or t + 60 not in by_t: continue
            tg = tags[i % 2]; i += 1; fg = foe(tg); s2 = by_t[t + 60]
            stt = _row(sr, t)
            zones = lambda x, z: sum(1 for v in (stt[x].get("zones") or {}).values() if v == z)
            own_b = r["stand"].get("boost_in") if r["stand"]["owner"] == tg else None
            en_b = r["stand"].get("boost_in") if r["stand"]["owner"] == fg else None
            lead = max(min(r[tg]["flag_lead"], CLIP), -CLIP)
            add(tg, t, max(min(s2[tg]["flag_lead"], CLIP), -CLIP) - lead, flag_lead=lead,
                waiting_runner=int(r[tg].get("waiting_runner") is not None), backup_flag=int(bool(r[tg].get("backup_flag"))),
                stand_own=int(r["stand"]["owner"] == tg), stand_enemy=int(r["stand"]["owner"] == fg), own_boost_in=own_b, enemy_boost_in=en_b,
                own_alive=r[tg]["alive"], enemy_alive=r[fg]["alive"], own_main=r[tg]["main"], enemy_main=r[fg]["main"],
                own_flag_duty=len(r[tg].get("flag_duty") or []), enemy_flag_duty=len(r[fg].get("flag_duty") or []),
                own_in_enemy_base=zones(tg, "enemy base") + zones(tg, "enemy pit"), enemy_in_own_base=zones(fg, "enemy base") + zones(fg, "enemy pit"),
                own_eta=min(r[tg].get("flag_eta") or NEVER * 3, NEVER * 3), enemy_eta=min(r[fg].get("flag_eta") or NEVER * 3, NEVER * 3),
                own_carrying=int(any(w == "carrying" for _, w in (r[tg].get("flag_duty") or []))),
                enemy_carrying=int(any(w == "carrying" for _, w in (r[fg].get("flag_duty") or []))),
                own_cap_before_boost=int(bool(r[tg].get("can_cap_before_boost"))), enemy_cap_before_boost=int(bool(r[fg].get("can_cap_before_boost"))),
                own_deaths_30s=sum(1 for x in deaths if x["team"] == tg and t - 30 < x["t"] <= t),
                enemy_deaths_30s=sum(1 for x in deaths if x["team"] == fg and t - 30 < x["t"] <= t),
                minute=round(t / 60, 1), res_in=r.get("res_in"), run_dist=run_dist.get(tg), strength_gap=gaps[tg])
    elif node == "run_defence":
        # every enemy run, from the defending side, read at the same points as run_outcome (5, 15, 30 s in)
        rec = {(r["team"], r["t"]): r for r in R.get("runs", [])}
        for fr in a["flag_runs"]:
            r = rec.get((fr["team"], fr["start"]))
            if not r: continue
            att = fr["team"]; dfn = foe(att); s0 = _row(sb, fr["start"])
            for k in CHECKPOINTS:
                if fr["secs"] <= k: continue
                pf = r.get("pusher_first") or []
                add(dfn, fr["start"] + k, int(fr["outcome"] == "captured"), checkpoint_s=k,
                    def_free=s0[dfn]["alive"] - len(s0[dfn].get("flag_duty") or []), pushers_so_far=sum(1 for x in pf if x <= k),
                    control_so_far=sum(1 for c in r.get("control_times") or [] if c[0] <= k),
                    damage_so_far=sum(x[1] for x in r.get("damage_times") or [] if x[0] <= k),
                    escort=r["escort"], att_main=r["main"][0], def_main=r["main"][1],
                    min_capture_s=_min_capture(st, m, ra := agent_of(att, fr["runner"]), fr["start"] + k),
                    runner_class=runner_code(m, ra) if ra is not None else None,
                    def_snare_near=_power_near(st, P, tm_of[dfn], ra, fr["start"] + k),
                    run_dist=run_dist.get(att), strength_gap=gaps[dfn])
    elif node == "capture_speed":
        # defence read at the same point of every capture (10 s in): counts over the whole run grow with its length
        rec = {(r["team"], r["t"]): r for r in R.get("runs", [])}
        for c in R.get("caps", []):
            if c["secs"] <= CAP_AT: continue
            r = rec.get((c["team"], c["t"] - c["secs"])) or next((x for x in R.get("runs", []) if x["team"] == c["team"] and abs(x["t"] + x["secs"] - c["t"]) <= 2), None)
            if not r: continue
            pf = r.get("pusher_first") or []
            ct = [x for x in r.get("control_times") or [] if x[0] <= CAP_AT]
            add(c["defender"], c["t"], c["secs"], defenders_free=c["defenders_free"], escort=c["escort"],
                pushers_10s=sum(1 for x in pf if x <= CAP_AT), control_10s=len(ct),
                damage_10s=sum(x[1] for x in r.get("damage_times") or [] if x[0] <= CAP_AT),
                min_capture_s=_min_capture(st, m, ra, c["t"] - c["secs"]) if (ra := next((fr_["runner"] for fr_ in a["flag_runs"] if fr_["team"] == c["team"] and abs(fr_["end"] - c["t"]) <= 3), None)) and (ra := agent_of(c["team"], ra)) is not None else None,
                runner_class=runner_code(m, ra) if ra is not None else None,
                def_snare_near=_power_near(st, P, tm_of[c["defender"]], ra, c["t"] - c["secs"] + CAP_AT) if ra is not None else None,
                run_dist=run_dist.get(c["team"]), strength_gap=gaps[c["defender"]])
    elif node == "power_play":
        for p in R.get("power", []):
            tg, fg = p["team"], foe(p["team"]); t0, t1 = p["t"], p["t"] + max(p["window_s"], 5)
            # damage, pushing, control and the enemy's defence read only up to the first kill (Denning, after batch 9;
            # as the fight node does): after a kill they are partly its result. window_s stays the whole window (exposure)
            tw = max(min(p["first_kill"], t1), t0 + 5) if p.get("first_kill") is not None else t1; w = (tw - t0) / 10
            sp = [x for x in R.get("spikes", []) if x["team"] == tg and t0 <= x["t"] <= tw]
            hb = team.get("heal5", {}).get(fg) or []; b = team.get("bucket_s", 5)
            eh = sum(hb[int(t0 // b):max(int(t0 // b) + 1, int(math.ceil(tw / b)))]) / max(tw - t0, 1)
            try: own, en = map(int, p["main"].split("v"))
            except ValueError: continue
            add(tg, t0, int(p["kills"] > 0), window_s=round(t1 - t0), size=p["size"], own_main=own, enemy_main=en, **_short(p["enemy_short_because"]),
                flag_lead=max(min(p["flag_lead"], CLIP), -CLIP), pushed=int(p["choice"] == "pushed"),
                dps_v_usual=_team_dps(team, tg, t0, tw, V, roles_alive(tg, t0)),
                enemy_prots_10s=round(sum(1 for x in team.get("prot_casts", []) if x[1] == fg and t0 <= x[0] <= tw) / w, 2), enemy_heal_s=round(eh, 1),
                spikes_10s=round(len(sp) / w, 2), spike_spread=statistics.median([x["spread_s"] for x in sp]) if sp else None,
                spikes_on_healers=round(sum(1 for x in sp if x["target_class"] == "healer") / len(sp), 2) if sp else None,
                healer_damage_share=_healer_share(m, ev, tm_of[tg], t0, tw),
                blind_secs_on_own_10s=round(_blind_secs([x for x in R.get("blinds", []) if x["team"] == fg and x.get("attacker", True)], t0, tw) / w, 2),
                strength_gap=gaps[tg])
    elif node == "fight_outcome":
        for fi, f in enumerate(a.get("fights") or []):
            # fights.py stores each fight from the side that lost it; alternate the side read so both outcomes appear
            tg = f["team"] if fi % 2 == 0 else foe(f["team"]); fg = foe(tg)
            if f.get("opponent_won_fight") is None: continue
            t0 = f["start"] - 5
            first = min([x[0] for x in f.get("deaths") or []] or [f["end"]])
            t1 = max(first, f["start"] + 5)
            def side(x):
                cs = [c for c in R.get("casts", []) if c["fight"] == fi and c["team"] == x]
                n = sum(c["casts"] for c in cs) or None
                pl = len(cs) or None
                pe = [c["defensive_share"] for c in R.get("peel", []) if c["fight"] == fi and c["team"] == x]
                s_ = [r for r in R.get("strips", []) if r["team"] == x and t0 <= r["t"] <= t1]
                sa = [r for r in s_ if r.get("available")]
                blall = R.get("blinds", [])
                sp = [r for r in R.get("spikes", []) if r["team"] == x and t0 <= r["t"] <= t1]
                hx = [r for r in R.get("hexes", []) if r["team"] == x and t0 <= r["t"] <= t1 and r.get("value", 0) > 0]
                hr = [r for r in R.get("hex_removals", []) if r["team"] == x and t0 <= r["t"] <= t1 and r.get("available")]
                hs = (sum(r["value"] * min(r["secs"] if r["secs"] is not None else t1 - r["t"], 30) for r in hx) / sum(r["value"] for r in hx)) if hx else None
                return {"ready": sum(c["interrupted_after_ready"] for c in cs) / n if n else None, "dazed": sum(c["while_dazed"] for c in cs) / n if n else None,
                        "blind_att": sum(c["attacks_while_blind"] for c in cs) / pl if pl else None,
                        "peel": statistics.mean(pe) if pe else None, "strip_right": sum(r["right_target"] for r in sa) / len(sa) if sa else None,
                        "strip_value": sum(r["value"] for r in s_) / max(t1 - t0, 1) * 10,
                        "blind_front": _blind_secs([r for r in blall if r["team"] == x and r["target_class"] == "frontline"], t0, t1),
                        "blind_def": _blind_secs([r for r in blall if r["team"] == x and r["defensive"]], t0, t1),
                        "spread": statistics.median([r["spread_s"] for r in sp]) if sp else None, "spikes": len(sp),
                        "dps": _team_dps(team, x, t0, t1, V, roles_alive(x, f["start"])),
                        "hex_secs": hs, "hex_right": sum(r["right_hex"] for r in hr) / len(hr) if hr else None}
            o, e = side(tg), side(fg)
            df = lambda k: (o[k] - e[k]) if o[k] is not None and e[k] is not None else None
            ln = f.get("local_numbers") or [None, None]
            if tg != f["team"]: ln = ln[::-1]
            add(tg, f["start"], int(f.get("opponent_won_fight") == tg), own_local=ln[0], enemy_local=ln[1],
                peel_defensive_diff=df("peel"), ready_interrupt_diff=df("ready"), dazed_casts_diff=df("dazed"), blind_attacks_diff=df("blind_att"),
                strip_right_diff=df("strip_right"), strip_value_diff=df("strip_value"), blind_front_secs_diff=df("blind_front"), blind_defensive_secs_diff=df("blind_def"),
                spike_spread_diff=df("spread"), spikes_diff=df("spikes"), dps_v_usual_diff=df("dps"), hex_secs_diff=df("hex_secs"), hex_right_diff=df("hex_right"),
                healer_focus_diff=(lambda o_, e_: round(o_ - e_, 2) if o_ is not None and e_ is not None else None)(
                    _healer_share(m, ev, tm_of[tg], t0, t1), _healer_share(m, ev, tm_of[fg], t0, t1)),
                strength_gap=gaps[tg])
    elif node == "split_chance":
        spl = collections.defaultdict(list)
        for s_ in a.get("splits", []): spl[s_["team"]].append((s_["start"], s_["end"]))
        for r in sb:
            t = r["t"]
            if t < 30 or t % 15 or t > (sb[-1]["t"] - 30): continue
            for tg in tags:
                if any(s0 <= t <= s1 for s0, s1 in spl[tg]): continue
                fg = foe(tg); mu = mus[tg]
                add(tg, t, int(any(t < s0 <= t + 30 for s0, _ in spl[tg])), flag_lead=max(min(r[tg]["flag_lead"], CLIP), -CLIP),
                    own_alive=r[tg]["alive"], enemy_alive=r[fg]["alive"], own_main=r[tg]["main"], enemy_main=r[fg]["main"],
                    stand_own=int(r["stand"]["owner"] == tg), stand_enemy=int(r["stand"]["owner"] == fg), minute=round(t / 60, 1), res_in=r.get("res_in"),
                    own_speed_power=team_power(tg, "speed"), own_escapes=team_power(tg, "escapes"),
                    own_snare_power=team_power(tg, "snare"), enemy_snare_power=team_power(fg, "snare"), strength_gap=gaps[tg])
    elif node in ("split_answer", "split_effect", "collapse"):
        from state import d
        rec = {(r["team"], r["t"]): r for r in R.get("splits", [])}
        for s_ in a.get("splits", []):
            r = rec.get((s_["team"], s_["start"]))
            if not r: continue
            tg, fg = s_["team"], foe(s_["team"])
            lat = [x["latency"] for x in s_.get("defenders") or []]
            first = min(lat) if lat else None
            latency = max(min(first, NEVER), -30) if first is not None else NEVER
            if node == "split_answer":
                if s_.get("entered_base") is None: continue
                te = s_["entered_base"]; srow = _row(sb, te); dtm = tm_of[fg]
                near = [d(st.pos(b, te)[0], st.geo.base[dtm]) for b in st.players[dtm] if st.alive(b, te)] if getattr(st.geo, "base", None) else []
                add(fg, te, latency, flag_lead=max(min(srow[fg]["flag_lead"], CLIP), -CLIP), def_alive=srow[fg]["alive"], att_main=srow[tg]["main"],
                    def_free=srow[fg]["alive"] - len(srow[fg].get("flag_duty") or []), nearest_to_base=round(min(near)) if near else None,
                    size=r["size"], minute=round(te / 60, 1), strength_gap=gaps[fg])
            elif node == "split_effect":
                if s_.get("entered_base") is None: continue
                from common import line as LINE
                heal = sum(1 for x in s_["members"] if "Monk" in x or x in ("Prot",))
                se = _row(sb, s_["entered_base"])
                add(tg, s_["start"], int(r["pit_kills"] > 0), latency=latency, defenders=r["defenders"], size=r["size"],
                    main_diff=r["main_diff"], split_healers=heal, def_npc_value=se[fg].get("npc_value"),
                    def_free=se[fg]["alive"] - len(se[fg].get("flag_duty") or []),
                    def_snare_present=round(sum(P[x]["snare"] for x in (agent_of(fg, dd["role"]) for dd in s_.get("defenders") or []) if x is not None), 1),
                    split_speed_power=round(sum(P[x]["speed"] for x in st.players[tm_of[tg]] if m.roles.get(x) in s_["members"]), 1),
                    strength_gap=gaps[tg])
            else:
                # collapse timing, several readings (Denning: which one matters is for the data to say)
                arr = sorted(x["first"] for x in s_.get("defenders") or [] if x.get("first") is not None)
                ta = arr[0] if arr else None
                mem = [x for x in st.players[tm_of[tg]] if m.roles[x] in s_["members"]]
                npc_first = next((e[0] / 10 for e in m.o["ev"] if e[1] == "dm" and e[2] in mem and isinstance(e[3], int) and e[3] < len(m.A)
                                  and m.A[e[3]].get("npc") and e[0] / 10 >= s_["start"]), None)
                esc = None
                if ta is not None and mem:
                    esc = 0
                    for x in mem:
                        for sid in (m.A[x].get("bar") or []):
                            sd = SK().get(m.o.get("skills", {}).get(str(sid)) or "") or {}
                            if "Increased Movement Speed" not in (sd.get("causes") or []): continue
                            used = [e[0] / 10 for e in m.o["ev"] if e[1] == "cf" and e[2] == x and e[4] == sid and e[0] / 10 <= ta]
                            if not used or ta - used[-1] >= (sd.get("recharge") or 0): esc += 1
                # split depth (Denning, after the batch 9 rebuild: the deeper the splitters are in the base, the more likely
                # they die to a collapse): the split's nearest member to the defending pit, at the first defender's
                # arrival, and its median over the split (every 2 s, from entering the base or the start)
                pit = st.geo.pit.get(tm_of[fg])
                def depth(t):
                    ds = [d(st.pos(x, t)[0], pit) for x in mem if st.alive(x, t) and st.pos(x, t)[0]] if pit else []
                    return min(ds) if ds else None
                t_in = s_.get("entered_base") if s_.get("entered_base") is not None else s_["start"]
                dl = [v for v in (depth(t) for t in range(int(t_in), int(s_["end"]) + 1, 2)) if v is not None]
                d_arr = depth(ta) if ta is not None else None
                add(tg, s_["start"], int(r["split_deaths"] > 0), latency=latency,
                    depth_at_arrival=round(d_arr) if d_arr is not None else None, depth_median=round(statistics.median(dl)) if dl else None,
                    defenders_10s=sum(1 for x in arr if x <= ta + 10) if ta is not None else 0,
                    contact_diff=(sum(1 for x in arr if x <= ta + 5) - r["size"]) if ta is not None else None,
                    npc_hit_to_arrival=round(ta - npc_first, 1) if ta is not None and npc_first is not None else None,
                    res_in_at_arrival=_row(sb, ta).get("res_in") if ta is not None else None,
                    escape_ready=esc,
                    def_snare_present=round(sum(P[x]["snare"] for x in (agent_of(fg, dd["role"]) for dd in s_.get("defenders") or []) if x is not None), 1),
                    split_speed_power=round(sum(P[x]["speed"] for x in mem), 1), split_escapes=sum(P[x]["escapes"] for x in mem),
                    size=r["size"], main_diff=r["main_diff"], strength_gap=gaps[tg])
    return _approved(node, rows, rid, m)


_SK = None
def SK():
    global _SK
    if _SK is None:
        from forensics import skilldata
        _SK = skilldata()
    return _SK


def _vhash(V): return hashlib.sha1(json.dumps(V, sort_keys=True).encode()).hexdigest()[:10]


def node_rows(node, rid, V):
    import cache
    return cache.prepared("lrows", rid, lambda: _build(node, rid, V), sub=f"{node}-{_vhash(V)}")


def _rows_job(job):
    node, rid, V = job
    return node_rows(node, rid, V)


