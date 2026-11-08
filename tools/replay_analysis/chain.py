"""The causal chain: how a result came about, as a chain of game states each caused by the one before (Denning,
2026-11-07). Example: a knight dies <- the pit was pushed 8v4 <- a wipe <- two backline deaths (dual knockdown with
Aura of Stability unused, Healing Burst interrupted with no cancel, a Mesmer playing offensively) <- a forced 7v8 fight
while running a flag <- behind on flags against a power play <- the flagger crippled a minute earlier.

Built backwards from the result, one link at a time. Each link is a game state with the measured event that produced
it (from the stored analysis, forensics and the scoreboard), its time, and the held-out win model's change over it.
Link kinds and what each looks back to:
  npc_loss      pit numbers at the loss -> own players dead (deaths) or away on flag duty (flag_duty)
  deaths        each death's measured causes (forensics: knockdowns with knockdown immunity ready, casts into ready
                interrupts, prots, peel, position) and the team's Mesmers' defensive play -> the fight's numbers when
                it started (outnumbered) and the flag state (flag_deficit) if the team was behind on flags
  outnumbered   the main group short of players -> who was missing and why: dead earlier (deaths), on flag duty
                (flag_duty), elsewhere
  flag_duty     players carrying, escorting or waiting -> the flag deficit that forced the run (flag_deficit)
  flag_deficit  when the flag lead turned against the team, and what turned it: own runs dropped or killed (control
                on the runner: Cripple, knockdowns, interrupts), the enemy capture, a slow answer -> own deaths then
A link is kept only when its measured state is unusual (numbers down, a flag deficit, a death...). The chain follows
the TOP biggest causes at each link (by win change) and stops at the last reset (both teams at full strength and even
on flags) or BACK_S before the result, whichever is later (Denning). Fixes: only the FIXES links where a different
play would have mattered most, each priced in win points from measurement (usual play, node models read again with the
variable changed, the run benchmark).

In code: c = Chain(rid, team, recs, usual_res); c.build(kind, t, payload); c.lines() -> markdown lines."""
import collections, statistics

BACK_S = 180            # Denning: trace back at most 3 minutes
TOP = 2                 # causes followed at each link (Denning: the biggest few)
FIXES = 2               # fixes shown (Denning: the few where a fix would have mattered most)
MAX_LINKS = 10
ONGOING = {"split", "isolated", "flag_duty"}     # states that can start before the reset and still be going on
CLUSTER_S = 15          # deaths this close together are one fight
OUTNUMBERED = 2         # main group this many or more below the enemy's counts as outnumbered


def clock(t): return f"{int(t // 60)}:{int(t % 60):02d}"


class Chain:
    def __init__(self, rid, team, recs=None, usual_res=None):
        import tq, why as WHY
        self.rid, self.team, self.recs, self.usual_res = rid, team, recs, usual_res
        self.a = tq._analysis(rid)
        self.foe = [x["tag"] for x in self.a["meta"]["teams"] if x["tag"] != team][0]
        self.F = WHY._forensics(rid)
        self.links, self.fixes, self.seen = [], [], set()

    # ---------------------------------------------------------------- helpers
    def win(self, t0, t1):
        import why as WHY
        w = WHY.win_change(self.rid, self.team, max(t0, 0), t1)
        return round(w[1] - w[0], 1) if w else None

    def sb(self, t):
        rows = [r for r in self.a["scoreboard"] if r["t"] <= t]
        return rows[-1] if rows else self.a["scoreboard"][0]

    def st(self, t):
        rows = [r for r in self.a["state"] if r["t"] <= t]
        return rows[-1] if rows else self.a["state"][0]

    def floor(self, t):
        """The last reset before t (both teams 8 alive and flag lead within 10 s), or t - BACK_S, whichever is later."""
        rs = [r["t"] for r in self.a["scoreboard"] if r["t"] < t - 5 and r[self.team]["alive"] == 8 and r[self.foe]["alive"] == 8
              and abs(r[self.team]["flag_lead"]) <= 10]
        return max([t - BACK_S] + rs[-1:])

    def own_deaths(self, t0, t1):
        return [d for d in self.a["deaths"] if d["team"] == self.team and t0 <= d["t"] <= t1]

    def cluster(self, t):
        """The own deaths in the fight around t (gaps of CLUSTER_S or less)."""
        ds = sorted(self.a["deaths"], key=lambda d: d["t"])
        own = [d for d in ds if d["team"] == self.team]
        near = [d for d in own if abs(d["t"] - t) <= CLUSTER_S]
        if not near: return []
        lo, hi = min(d["t"] for d in near), max(d["t"] for d in near)
        changed = True
        while changed:
            changed = False
            for d in own:
                if lo - CLUSTER_S <= d["t"] < lo or hi < d["t"] <= hi + CLUSTER_S:
                    lo, hi = min(lo, d["t"]), max(hi, d["t"]); changed = True
        return [d for d in own if lo <= d["t"] <= hi]

    def add_fix(self, label, points, link_i, how, clear):
        if points is not None and points > 0:
            self.fixes.append({"label": label, "points": round(points, 1), "link": link_i, "how": how, "clear": clear})

    def decision_fixes(self, t0, t1, link_i):
        if self.recs is None or self.usual_res is None: return
        import tq
        for x in tq.decision_alternatives(self.recs, self.usual_res, self.rid, self.team, t0, t1):
            b = tq.better_options(x)
            if not b: continue
            c, d, clear, sel = b[0]; r = x["r"]
            self.add_fix(f"{r['kind'].replace('_', ' ')} at {clock(r['t'])} (main {r['state'].get('main')}): {c['choice']} instead of {r.get('choice2')}",
                         d, link_i, "usual.py: measured choice effect against the choice made" + (", partly who chooses it" if sel else ""),
                         clear and not sel)

    # ---------------------------------------------------------------- the links
    def link_npc_loss(self, t, p):
        import nodes as N
        rows = [r for r in N.node_rows("npc_loss", self.rid) if r["team"] == self.foe and t - 30 <= r["t"] <= t]
        r = max(rows, key=lambda r: r["t"]) if rows else {}
        dead = [d for d in self.a["deaths"] if d["team"] == self.team and t - 150 <= d["t"] <= t and d["t"] + (d.get("down_for") or 0) >= t]
        s = self.st(t)
        away = [k for k, z in s[self.team]["zones"].items() if z not in ("dead", "own pit", "own base")]
        ev = [f"pit at {clock(r['t'])}: {r.get('attackers')} attackers against {r.get('defenders')} defenders "
              f"({r.get('defender_healers')} healers)" if r else "pit numbers not read",
              f"{len(dead)} of {self.team} dead ({', '.join(d['victim'] + ' ' + clock(d['t']) for d in dead[:6])})" if dead else "",
              f"away from base: {', '.join(away)}" if away else ""]
        causes = []
        dead_in = [d for d in dead if d["t"] >= self.lo]
        if dead_in:
            first = min(d["t"] for d in dead_in); causes.append(("deaths", first, {"deaths": self.cluster(first) or dead_in}))
        sp = [x for x in self.a["splits"] if x["team"] == self.foe and x.get("entered_base") and x["entered_base"] <= t <= x["end"] + 5]
        if sp: causes.append(("split", sp[0]["entered_base"], {"split": sp[0]}))
        duty = [x for x in self.sb(t)[self.team].get("flag_duty") or []]
        if duty: causes.append(("flag_duty", t, {}))
        return {"title": f"{self.team} lost {p.get('what', 'a pit NPC')}", "t0": t - 20, "t1": t, "evidence": [e for e in ev if e], "causes": causes}

    def link_deaths(self, t, p):
        import events as EV, tq
        ds = p.get("deaths") or self.cluster(t)
        if not ds: return None
        t0, t1 = min(d["t"] for d in ds), max(d["t"] for d in ds)
        ev, worst = [], None
        for d in sorted(ds, key=lambda d: d["t"])[:4]:
            try: ans = EV.death(self.rid, self.team, d["victim"], d["t"] + .5, self.F)
            except Exception: continue
            kc = EV.key_causes(ans)
            ca = ans["casting"]["measures"]
            if ca.get("into_ready_interrupt") and ca.get("interrupted"):
                kc.append(f"cast into ready interrupts {ca['into_ready_interrupt']} times, cancelled {ca.get('cancelled_when_threatened', 0)}, "
                          f"interrupted {ca['interrupted']}")
            ev.append(f"{clock(d['t'])} {d['victim']} died ({d.get('zone')}, numbers {d.get('numbers')}): " + ("; ".join(kc[:4]) or "no standout cause measured"))
            self.death_fixes(d, ans, len(self.links))
        # the team's disrupting players (Mesmers): defensive or offensive in the 20 s before the first death
        for a in self.F.players(self.F.team_of(self.team)):
            role = self.F.m.roles.get(a, "")
            if "Mes" not in role or not self.F.alive(a, t0 - 1): continue
            x = self.F.disruption(a, t0 - 20, t0)
            if not x["actions"]: continue
            bm = mes_benchmark()
            ev.append(f"{role} in the 20 s before: {x['defensive_share']:.0%} of its interrupts and casts on the enemy midline or frontline "
                      f"(interrupts {x['interrupts'] or 'none'}, casts on enemies {x['casts_on_enemies'] or 'none'}; typical before an own healer death: "
                      + (f"{bm['median']:.0%}, {bm['n']} cases" if bm else "not measured yet") + ")")
        s = self.st(t0 - 2); sb = self.sb(t0 - 2)
        own_m, en_m = s[self.team]["main"], s[self.foe]["main"]
        ev.append(f"when the fight started: main {own_m}v{en_m}, alive {s[self.team]['alive']}v{s[self.foe]['alive']}, "
                  f"flag lead {sb[self.team]['flag_lead']:+} s, stand {sb['stand']['owner'] or 'nobody'}")
        causes = []
        for d in ds:
            if d.get("isolated") or (d.get("victim") in tq.HEALER_ROLES and (d.get("monk_distance") or {}) and
                                      min((d.get("monk_distance") or {}).values() or [0]) > 2500):
                causes.append(("isolated", d["t"] - 1, {"role": d["victim"]}))
        if own_m - en_m <= -OUTNUMBERED: causes.append(("outnumbered", t0 - 2, {}))
        if sb[self.team]["flag_lead"] <= -10 or (sb["stand"]["owner"] == self.foe and (sb["stand"].get("boost_in") or 999) <= 60):
            causes.append(("flag_deficit", t0 - 2, {}))
        wipe = len(ds) >= 4
        return {"title": f"{'wipe' if wipe else 'deaths'}: {len(ds)} of {self.team} died {clock(t0)}" + (f" to {clock(t1)}" if t1 > t0 else ""),
                "t0": t0 - 10, "t1": t1 + 5, "evidence": ev, "causes": causes}

    def death_fixes(self, d, ans, link_i):
        import tq
        row = tq._row_near("deaths_all", self.rid, self.team, d["victim"], d["t"], -8, -2)
        if not row: return
        ch = []
        pr = ans["prots"]
        kd = [k for k in (pr.get("knockdowns") or []) if not k["immunity_up"] and k["ready_in_range"]]
        if kd: ch.append((f"Aura of Stability (or other knockdown immunity) on the {d['victim']}: {', '.join(kd[0]['ready_in_range'])} had it ready",
                          {"knocked_down_now": 0, "knockdowns_10s": 0}))
        if not row.get("prot_up") and pr["ready_unused"]:
            ch.append((f"a prot on the {d['victim']}: {pr['ready_unused'][0]['healer']} {pr['ready_unused'][0]['skill']} ready and unused", {"prot_up": 1}))
        if (row.get("healers_in_range") or 0) == 0: ch.append((f"another healer in range of the {d['victim']}", {"healers_in_range": 1, "solo_healer": 0}))
        if not ch: return
        base, out = tq.what_if("deaths", self.rid, row, ch)
        cost = self.win(d["t"] - 10, d["t"] + 30)
        for lab, v, dd in tq.reliable(out):
            if dd < 0 and cost is not None and cost < 0:
                self.add_fix(lab, -dd / 100 * -cost, link_i,
                             f"deaths node: risk {base}% -> {v}% of dying in the next 10 s, times this death's cost ({cost:+} points)",
                             tq.meaningful(base, dd))

    def link_outnumbered(self, t, p):
        s = self.st(t)
        main = set(s[self.team]["main_roles"])
        runs = [r for r in self.a["flag_runs"] if r["team"] == self.team and r["start"] <= t <= r["end"] + 5]
        miss = collections.OrderedDict()
        for role, z in s[self.team]["zones"].items():
            if role in main: continue
            if z == "dead": why_ = "dead"
            elif any(r["runner"] == role for r in runs): why_ = "carrying the flag"
            elif any(role in (r.get("escort") or []) for r in runs): why_ = "escorting the flag"
            else: why_ = f"elsewhere ({z})"
            miss[role] = why_
        ev = [f"main {s[self.team]['main']}v{s[self.foe]['main']}: missing " + "; ".join(f"{k} {v}" for k, v in miss.items())]
        causes = []
        dead_roles = [k for k, v in miss.items() if v == "dead"]
        if dead_roles:
            dd = [d for d in self.a["deaths"] if d["team"] == self.team and d["victim"] in dead_roles and d["t"] < t - 3]
            if dd: causes.append(("deaths", max(d["t"] for d in dd), {}))
        if any(v.endswith("flag") for v in miss.values()): causes.append(("flag_duty", t, {}))
        return {"title": f"{self.team}'s main outnumbered {s[self.team]['main']}v{s[self.foe]['main']}", "t0": t - 10, "t1": t + 10,
                "evidence": ev, "causes": causes}

    def link_flag_duty(self, t, p):
        import tq
        runs = [r for r in self.a["flag_runs"] if r["team"] == self.team and r["start"] <= t + 5 and r["end"] >= t - 30]
        sb = self.sb(t)
        ev = [f"flag lead {sb[self.team]['flag_lead']:+} s, stand {sb['stand']['owner'] or 'nobody'}"
              + (f", boost in {sb['stand']['boost_in']} s" if sb["stand"].get("boost_in") else "")]
        for r in runs[:2]:
            k = tq._run_key(r["main_numbers"], len(r.get("escort") or [])) if r.get("main_numbers") else None
            ev.append(f"{clock(r['start'])} {r['runner']}" + (f" with {', '.join(r['escort'])}" if r.get("escort") else " alone")
                      + (f", main left {r['main_numbers'][0]:.0f}v{r['main_numbers'][1]:.0f}" if r.get("main_numbers") else "")
                      + f": {r['outcome']}" + (f"; runs like it: {tq._bench_txt(k)}" if k and sb["stand"]["owner"] == self.foe else ""))
            if k and k[1] == "escort 2+" and sb["stand"]["owner"] == self.foe:
                b, ba = tq.run_bench().get(k), tq.run_bench().get((k[0], "escort 0-1"))
                if b and ba and b["win"] is not None and ba["win"] is not None:
                    self.add_fix(f"run at {clock(r['start'])} with 0 to 1 escorts instead of {len(r['escort'])}", ba["win"] - b["win"], len(self.links),
                                 f"run benchmark: {_short(ba)} against {_short(b)}", b["n"] >= 10 and ba["n"] >= 10)
        causes = []
        if sb[self.team]["flag_lead"] <= -10 or sb["stand"]["owner"] == self.foe: causes.append(("flag_deficit", (runs[0]["start"] if runs else t), {}))
        return {"title": f"{self.team} on flag duty" + (f" ({runs[0]['runner']} running)" if runs else ""), "t0": (runs[0]["start"] if runs else t) - 5,
                "t1": t + 5, "evidence": ev, "causes": causes}

    def link_flag_deficit(self, t, p):
        rows = [r for r in self.a["scoreboard"] if self.lo <= r["t"] <= t]
        if not rows: return None
        up = [r for r in rows if r[self.team]["flag_lead"] >= 0]
        if not up: return {"title": f"{self.team} already behind on flags at {clock(rows[0]['t'])}", "t0": rows[0]["t"], "t1": t,
                           "evidence": [f"flag lead {rows[0][self.team]['flag_lead']:+} s since the start of the window"], "causes": []}
        ts = up[-1]["t"]
        down = [r for r in rows if r["t"] > ts and r[self.team]["flag_lead"] <= -10]
        te = down[0]["t"] if down else t
        ev = [f"flag lead {up[-1][self.team]['flag_lead']:+} s at {clock(ts)} -> {self.sb(te)[self.team]['flag_lead']:+} s at {clock(te)}"]
        for r in self.a["flag_runs"]:
            if r["team"] != self.team or not (ts - 40 <= r["end"] <= te + 5): continue
            a_ = self.F.role_of(self.team, r["runner"]); ctrl = []
            if a_ is not None:
                ctrl += [f"{c[2]} at {clock(c[0])} by {self.F.name(c[1])}" for c in self.F.conds_on(a_, r["start"], r["end"]) if c[2] in ("crippled", "dazed", "blind")]
                ctrl += [f"knocked down at {clock(k[0])} by {self.F.name(k[1])}" for k in self.F.kds_on(a_, r["start"], r["end"])]
            ev.append(f"{self.team} {r['runner']} run {clock(r['start'])} to {clock(r['end'])}: {r['outcome']}"
                      + (f" ({'; '.join(ctrl[:4])})" if ctrl else ""))
        for c in self.a["flag_cycles"]:
            if ts - 10 <= (c.get("own_cap") or -1) <= te + 10:
                ev.append(f"{c['team']} capped at {clock(c['own_cap'])}" + (f", {c.get('slower_than_possible_s')} s slower than possible"
                                                                            if c["team"] == self.team and c.get("slower_than_possible_s") else ""))
        causes = []
        dd = self.own_deaths(ts - 10, te)
        if dd: causes.append(("deaths", dd[0]["t"], {"deaths": self.cluster(dd[0]["t"])}))
        self.decision_fixes(ts - 10, te, len(self.links))
        return {"title": f"{self.team} fell behind on flags", "t0": ts, "t1": te, "evidence": ev, "causes": causes}

    def link_split(self, t, p):
        x = p["split"]
        lat = [dd["latency"] for dd in x.get("defenders") or []]
        first = min(lat) if lat else None
        bm = split_benchmark()
        ev = [f"{self.foe} split {'+'.join(x['members'])} into {self.team}'s base at {clock(x['entered_base'])}",
              ("first defender " + ("never" if first is None else f"{first:.0f} s after it entered" if first >= 0 else f"{-first:.0f} s before it entered")
               + (f" (every stored split: median {bm['median']:+.0f} s; Denning: about 15 s is on time, 60 s is late)" if bm else ""))]
        kills = [k for k in x.get("npc_kills") or []]
        if kills: ev.append("NPCs it killed: " + ", ".join(f"{k['npc']} {clock(k['t'])} (defenders there: {', '.join(k['defenders_present']) or 'none'})" for k in kills[:5]))
        s = self.st(x["entered_base"]); ev.append(f"meanwhile {self.team}'s main {s[self.team]['main']}v{s[self.foe]['main']}")
        self.decision_fixes(x["entered_base"] - 30, x["entered_base"] + 60, len(self.links))
        return {"title": f"{self.foe}'s split in {self.team}'s base", "t0": x["entered_base"], "t1": min(x["end"], t + 60), "evidence": ev, "causes": []}

    def link_isolated(self, t, p):
        role = p["role"]
        rows = [r for r in self.a["state"] if t - BACK_S <= r["t"] <= t]
        # the latest continuous stretch away from the main group (alive) before t; none = it was with its group
        left = None
        for r in reversed(rows):
            if role in r[self.team]["main_roles"] or r[self.team]["zones"].get(role) == "dead": break
            left = r["t"]
        if left is None or t - left < 5: return None
        z = [r[self.team]["zones"].get(role) for r in rows if r["t"] >= left]
        zc = collections.Counter(z).most_common(2)
        ev = [f"{role} away from its main group from {clock(left)}" + (f" (mostly {', '.join(f'{k} {v * 5} s' for k, v in zc)})" if zc else "")]
        causes = []
        sp = [x for x in self.a["splits"] if x["team"] == self.foe and x["start"] <= t and x["end"] >= left - 20]
        if sp:
            ev.append(f"{self.foe} had a split of {'+'.join(sp[0]['members'])} on the map then" + (f", in the base from {clock(sp[0]['entered_base'])}" if sp[0].get("entered_base") else ""))
            if sp[0].get("entered_base"): causes.append(("split", sp[0]["entered_base"], {"split": sp[0]}))
        runs = [r for r in self.a["flag_runs"] if r["team"] == self.team and r["start"] <= t and r["end"] >= left - 10 and (r["runner"] == role or role in (r.get("escort") or []))]
        if runs: ev.append(f"on flag duty: {runs[0]['runner']} run {clock(runs[0]['start'])}"); causes.append(("flag_duty", runs[0]["start"], {}))
        self.decision_fixes(left - 20, t, len(self.links))
        return {"title": f"{self.team}'s {role} isolated", "t0": left, "t1": t, "evidence": ev, "causes": causes}

    # ---------------------------------------------------------------- building
    def build(self, kind, t, payload=None):
        self.lo = self.floor(t)
        todo = [(kind, t, payload or {}, None)]
        while todo and len(self.links) < MAX_LINKS:
            k, tt, p, parent = todo.pop(0)
            key = (k, int(tt // 10))
            if key in self.seen or (tt < self.lo and k not in ONGOING): continue
            self.seen.add(key)
            fn = getattr(self, "link_" + k)
            x = fn(tt, p)
            if not x: continue
            # win change over the link and what it led to in the next 20 s (from the reset on, for a state that began earlier)
            # ongoing states (a split, a player away, flag duty) get no win figure: over minutes it mixes in everything else
            x.update(kind=k, t=tt, parent=parent, win=None if k in ONGOING else self.win(max(x["t0"], self.lo), x["t1"] + 20))
            i = len(self.links); self.links.append(x)
            if k in ("deaths", "outnumbered", "flag_duty"): self.decision_fixes(x["t0"] - 20, x["t1"], i)
            nxt = []
            for ck, ct, cp in x["causes"]:
                if ct < self.lo:
                    if ck not in ONGOING: continue
                    ct = self.lo        # a state still going on at the reset (a split in the base, a player away) stays in the chain
                w = self.win(ct - 10, ct + 10)
                nxt.append((abs(w) if w is not None else 0, ck, ct, cp))
            nxt.sort(key=lambda z: -z[0])
            todo += [(ck, ct, cp, i) for _, ck, ct, cp in nxt[:TOP]]
        return self

    def short(self):
        """One line: the chain from its earliest link to the result."""
        L = sorted(self.links, key=lambda x: x["t0"])
        return " -> ".join(f"{x['title']} ({clock(x['t'])})" for x in L)

    def lines(self):
        if not self.links: return []
        L = [f"**How it got there** (the chain of game states, earliest first; traced back to {clock(self.lo)}, the last reset or 3 "
             "minutes before; win = the held-out win model's change over each link):"]
        order = sorted(range(len(self.links)), key=lambda i: self.links[i]["t0"])
        num = {i: n + 1 for n, i in enumerate(order)}
        for i in order:
            x = self.links[i]
            led = f" -> led to step {num[x['parent']]}" if x["parent"] is not None else " (the result)"
            L.append(f"{num[i]}. {clock(x['t0'])}: **{x['title']}**" + (f" (win {x['win']:+} points)" if x["win"] is not None
                     else " (ongoing state)" if x["kind"] in ONGOING else "") + led)
            L += [f"   - {e}" for e in x["evidence"]]
        fx = sorted(self.fixes, key=lambda f: -f["points"])
        seen, top = set(), []
        for f in fx:
            if f["label"] in seen: continue
            seen.add(f["label"]); top.append(f)
            if len(top) == FIXES: break
        L += ["", "**Where a fix would have mattered most** (measured, in win points):"]
        if top:
            for f in top:
                L.append(f"- step {num.get(f['link'], '?')}: {f['label']}: about {f['points']:+} win points ({f['how']}; "
                         + ("clear" if f["clear"] else "not clear yet") + ")")
        else:
            L.append("- no alternative along the chain could be priced from the data yet")
        return L

    def confidence_items(self):
        fx = sorted(self.fixes, key=lambda f: -f["points"])[:FIXES]
        return [("chain fix", f["clear"]) for f in fx]


def _short(b):
    return f"captured {b['captured']} of {b['n']}, win {b['win']:+}"


_MES = None
def mes_benchmark():
    """How defensively Mesmers usually play in the 20 s before one of their healers dies (forensics.disruption): median
    defensive share over every stored own-healer death with a living Mesmer that interrupted or cast on an enemy."""
    global _MES
    if _MES is None:
        import cache, tq, why as WHY
        vals = []
        for rid in tq._ids():
            def build(rid=rid):
                a = tq._analysis(rid); F = None; out = []
                for d in a["deaths"]:
                    if d["victim"] not in tq.HEALER_ROLES: continue
                    F = F or WHY._forensics(rid); tm = F.team_of(d["team"])
                    for p in F.players(tm):
                        if "Mes" in F.m.roles.get(p, "") and F.alive(p, d["t"] - 1):
                            x = F.disruption(p, d["t"] - 20, d["t"])
                            if x["defensive_share"] is not None: out.append(x["defensive_share"])
                return out
            vals += cache.prepared("mes_bench", rid, build)
        _MES = {"median": statistics.median(vals), "n": len(vals)} if vals else {}
    return _MES or None


_SPLIT = None
def split_benchmark():
    """First-defender latency of every stored split into a base (seconds after it entered; negative = before)."""
    global _SPLIT
    if _SPLIT is None:
        import tq
        lat = []
        for rid in tq._ids():
            for x in tq._analysis(rid).get("splits", []):
                if x.get("entered_base") and x.get("defenders"): lat.append(min(d["latency"] for d in x["defenders"]))
        _SPLIT = {"median": statistics.median(lat), "n": len(lat)} if lat else {}
    return _SPLIT or None
