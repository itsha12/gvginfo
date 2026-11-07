"""Rows for the learned node models (learnednodes.py), kept apart so a change to the fitting never rebuilds them
(cache kind "lrows" is keyed by this file and what it imports)."""
import collections, hashlib, json, math, statistics
CHECKPOINTS = (5, 15, 30)
CLIP = 150
NEVER = 60
CAP_AT = 10


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
                own_deaths_30s=sum(1 for x in deaths if x["team"] == tg and t - 30 < x["t"] <= t),
                enemy_deaths_30s=sum(1 for x in deaths if x["team"] == fg and t - 30 < x["t"] <= t),
                minute=round(t / 60, 1), res_in=r.get("res_in"), run_dist=run_dist.get(tg), strength_gap=gaps[tg])
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
                run_dist=run_dist.get(c["team"]), strength_gap=gaps[c["defender"]])
    elif node == "power_play":
        for p in R.get("power", []):
            tg, fg = p["team"], foe(p["team"]); t0, t1 = p["t"], p["t"] + max(p["window_s"], 5); w = (t1 - t0) / 10
            sp = [x for x in R.get("spikes", []) if x["team"] == tg and t0 <= x["t"] <= t1]
            hb = team.get("heal5", {}).get(fg) or []; b = team.get("bucket_s", 5)
            eh = sum(hb[int(t0 // b):max(int(t0 // b) + 1, int(math.ceil(t1 / b)))]) / max(t1 - t0, 1)
            try: own, en = map(int, p["main"].split("v"))
            except ValueError: continue
            add(tg, t0, int(p["kills"] > 0), window_s=round(t1 - t0), size=p["size"], own_main=own, enemy_main=en, **_short(p["enemy_short_because"]),
                flag_lead=max(min(p["flag_lead"], CLIP), -CLIP), pushed=int(p["choice"] == "pushed"),
                dps_v_usual=_team_dps(team, tg, t0, t1, V, roles_alive(tg, t0)),
                enemy_prots_10s=round(sum(1 for x in team.get("prot_casts", []) if x[1] == fg and t0 <= x[0] <= t1) / w, 2), enemy_heal_s=round(eh, 1),
                spikes_10s=round(len(sp) / w, 2), spike_spread=statistics.median([x["spread_s"] for x in sp]) if sp else None,
                spikes_on_healers=round(sum(1 for x in sp if x["target_class"] == "healer") / len(sp), 2) if sp else None,
                blinds_on_own_10s=round(sum(1 for x in R.get("blinds", []) if x["team"] == fg and t0 <= x["t"] <= t1) / w, 2),
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
                bl = [r for r in R.get("blinds", []) if r["team"] == x and t0 <= r["t"] <= t1]
                sp = [r for r in R.get("spikes", []) if r["team"] == x and t0 <= r["t"] <= t1]
                hx = [r for r in R.get("hexes", []) if r["team"] == x and t0 <= r["t"] <= t1 and r.get("value", 0) > 0]
                hr = [r for r in R.get("hex_removals", []) if r["team"] == x and t0 <= r["t"] <= t1 and r.get("available")]
                hs = (sum(r["value"] * min(r["secs"] if r["secs"] is not None else t1 - r["t"], 30) for r in hx) / sum(r["value"] for r in hx)) if hx else None
                return {"ready": sum(c["interrupted_after_ready"] for c in cs) / n if n else None, "dazed": sum(c["while_dazed"] for c in cs) / n if n else None,
                        "blind_att": sum(c["attacks_while_blind"] for c in cs) / pl if pl else None,
                        "peel": statistics.mean(pe) if pe else None, "strip_right": sum(r["right_target"] for r in sa) / len(sa) if sa else None,
                        "strip_value": sum(r["value"] for r in s_) / max(t1 - t0, 1) * 10,
                        "blind_front": sum(1 for r in bl if r["target_class"] == "frontline"), "blind_def": sum(1 for r in bl if r["defensive"]),
                        "spread": statistics.median([r["spread_s"] for r in sp]) if sp else None, "spikes": len(sp),
                        "dps": _team_dps(team, x, t0, t1, V, roles_alive(x, f["start"])),
                        "hex_secs": hs, "hex_right": sum(r["right_hex"] for r in hr) / len(hr) if hr else None}
            o, e = side(tg), side(fg)
            df = lambda k: (o[k] - e[k]) if o[k] is not None and e[k] is not None else None
            ln = f.get("local_numbers") or [None, None]
            if tg != f["team"]: ln = ln[::-1]
            add(tg, f["start"], int(f.get("opponent_won_fight") == tg), own_local=ln[0], enemy_local=ln[1],
                peel_defensive_diff=df("peel"), ready_interrupt_diff=df("ready"), dazed_casts_diff=df("dazed"), blind_attacks_diff=df("blind_att"),
                strip_right_diff=df("strip_right"), strip_value_diff=df("strip_value"), blind_front_diff=df("blind_front"), blind_defensive_diff=df("blind_def"),
                spike_spread_diff=df("spread"), spikes_diff=df("spikes"), dps_v_usual_diff=df("dps"), hex_secs_diff=df("hex_secs"), hex_right_diff=df("hex_right"),
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
                    own_speed=mu.get("own_speed"), own_snares=mu.get("own_snares"), enemy_snares=mu.get("enemy_snares"), strength_gap=gaps[tg])
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
                add(tg, s_["start"], int(r["pit_kills"] > 0), latency=latency, defenders=r["defenders"], size=r["size"],
                    main_diff=r["main_diff"], split_healers=heal, strength_gap=gaps[tg])
            else:
                add(tg, s_["start"], int(r["split_deaths"] > 0), latency=latency,
                    defenders_10s=sum(1 for x in lat if first is not None and x <= first + 10), def_snares=mus[fg].get("own_snares"),
                    split_speed=mus[tg].get("own_speed"), size=r["size"], main_diff=r["main_diff"], strength_gap=gaps[tg])
    return rows


def _vhash(V): return hashlib.sha1(json.dumps(V, sort_keys=True).encode()).hexdigest()[:10]


def node_rows(node, rid, V):
    import cache
    return cache.prepared("lrows", rid, lambda: _build(node, rid, V), sub=f"{node}-{_vhash(V)}")


def _rows_job(job):
    node, rid, V = job
    return node_rows(node, rid, V)


