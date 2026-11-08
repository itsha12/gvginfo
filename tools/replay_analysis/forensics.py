"""Forensics: the questions behind an event, each answered with a measurement and that measurement's place among the
same role in every stored match (benchmarks in data/benchmarks/forensics.json, rebuilt with `bench`).

Death questions (why a player died), each over the 20 s before the death unless named:
  position     out of position? distance to the nearest allied healer (and in casting range or not), allies and
               enemies within casting range, nearest enemy, whether the victim was the closest of its team to the enemy
  prots        did it get prots, on time, and the right ones? every prot or heal cast on it (pre-prot, reaction,
               late, interrupted, cancelled), what each prot can act on (from the skill data: blocks act on attacks only,
               damage reduction and heal-on-hit on all damage, knockdown immunity on knockdowns) against the damage mix
               it took, and the allied healers' prots that were ready and in range but not used
  monk_pressure were the healers under interrupt pressure? interrupts, knockdowns, Daze and hexes on the team's healers,
               casts started against casts finished
  sets         was the team taking unnecessary damage off its shield sets? damage taken while holding a set without a
               shield and not casting, and an estimate of what a shield would have stopped (armor 16, knowledge/armor.md:
               armor-respecting damage x (1 - 2^(-16/40)), about 24%); also the HP the shield set adds
  output       was the other team's damage performing? its damage per second on players, how concentrated, the share
               that ignores armor, spikes it landed, against its own matches and the benchmark
  peel         did the victim get peel? what its own team did to the players hitting it (damage, knockdowns,
               interrupts, snares, Blind, Weakness, hexes) and how long each attacker was left free
  casting      did it cast into ready interrupts, and cancel? every cast it started: outcome (finished, interrupted,
               cancelled), whether an enemy with an interrupt that was off recharge was in range (bow range from the
               bow type; spells 1248), whether it was Dazed
  conditions   who applied each condition on it, from how far, whether the attacker was being pressured, the victim's
               set and position then, and whether and how fast the condition was removed (and removal on its own bar)
Each answer carries a verdict (yes / no / partly / unclear) from where the measurement falls among the benchmark: the
cut-offs (BENCH_CUT) are the data's 20th and 80th percentiles for that role, provisional until Denning's rulings
(data/review_labels.json) calibrate them.

Usage:  python3 forensics.py death <report id> <team> <role> <m:ss>   every question for one death
        python3 forensics.py bench                                    rebuild the benchmarks from every stored replay
In code: Forensics(rid); death(rid, team, role, t) -> {question: answer}; lines(answers) -> markdown lines."""
import bisect, collections, json, math, os, statistics, sys
from common import REPO, CAST_R, line
from replaylib import Match

BENCH = os.path.join(REPO, "data", "benchmarks", "forensics.json")
SKILLS = os.path.join(REPO, "data", "skills.json")
BOW_RANGE = {"longbow": 1498, "flatbow": 1498, "recurve": 1273, "hornbow": 1273, "shortbow": 1004}
DEFAULT_BOW = 1498
SHIELD_ARMOR = 16                      # knowledge/armor.md: base shield armor when the requirement is met
SHIELD_CUT = 1 - 2 ** (-SHIELD_ARMOR / 40)
WINDOW = 20                            # seconds before a death that the questions look at
BENCH_CUT = (20, 80)                   # percentiles: below / above = clearly low / high for that role
POS_WINDOWS = (3, 5, 8)                # seconds before a death that position is judged on; the data picks one (bench)
POS_DEFAULT = 5
SNARES = {"crippled", "dazed", "blind", "weakness"}


def _act(s):
    """Activation time in seconds from the skill data's text (¼, ½, ¾, 1, 2, 1½ ...)."""
    if not s: return 0.0
    v = 0.0
    for ch in str(s):
        if ch.isdigit(): v = v * 10 + int(ch)
        elif ch in "¼½¾": v += {"¼": .25, "½": .5, "¾": .75}[ch]
    return v


_SK = None
def skilldata():
    global _SK
    if _SK is None:
        o = json.load(open(SKILLS)); L = o if isinstance(o, list) else o.get("skills", o)
        _SK = {}
        for s in L:
            for n in {s["name"], s["name"].replace(" (PvP)", ""), s["name"].replace(" (PvP)", " PvP")}:
                if n not in _SK or "(PvP)" in s["name"]: _SK[n] = s
    return _SK


def clock(t): return f"{int(t // 60)}:{t % 60:04.1f}"


def role_group(m, a):
    r = m.roles.get(a, "")
    if r in ("8 Monk", "7 Monk", "Prot"): return r
    from phases import healer
    return "healer" if healer(m, a) else line(m, a)


class Forensics:
    """One match, indexed for the questions."""
    def __init__(self, rid, m=None):
        self.rid = rid; self.m = m or Match.from_branch(rid); o = self.m.o
        self.tag = {t["id"]: t["tag"] for t in o["meta"]["teams"]}
        self.SN = {int(k): v for k, v in (o.get("skills") or {}).items()}
        self.ev = sorted(o["ev"], key=lambda e: e[0]); self.T = [e[0] for e in self.ev]
        self.sets = {int(k): v for k, v in (o.get("sets") or {}).items()}
        from phases import healer
        self.healers = {a for a in self.m.PL if healer(self.m, a)}
        self._casts = None

    # ---- basics
    def name(self, a): return f"{self.tag.get(self.m.team(a), '?')} {self.m.roles.get(a, a)}" if a in self.m.PL else f"NPC {a}"
    def team_of(self, tag): return [k for k, v in self.tag.items() if v == tag][0]
    def players(self, tm): return [a for a in self.m.PL if self.m.team(a) == tm]
    def enemies(self, a): return [b for b in self.m.PL if self.m.team(b) != self.m.team(a)]
    def snap(self, a, t): return self.m.snap(a, round(t * 10))
    def alive(self, a, t): return Match.alive(self.snap(a, t))
    def dist(self, a, b, t): return self.m.dist(a, b, round(t * 10))
    def sname(self, sid): return self.SN.get(sid, str(sid)) if sid is not None else "attack"
    def sdata(self, sid): return skilldata().get(self.sname(sid)) or {}
    def events(self, t0, t1, codes=None):
        i, j = bisect.bisect_left(self.T, t0 * 10), bisect.bisect_right(self.T, t1 * 10)
        return [e for e in self.ev[i:j] if codes is None or e[1] in codes]
    def role_of(self, tag, role):
        hit = [a for a in self.m.PL if self.tag.get(self.m.team(a)) == tag and self.m.roles.get(a) == role]
        return hit[0] if hit else None

    def weapon_set(self, a, t):
        s = self.snap(a, t); L = self.sets.get(a) or []
        if not s or s.get("w", -1) is None or s.get("w", -1) < 0 or s["w"] >= len(L): return None
        return L[s["w"]]

    def shield(self, a, t):
        w = self.weapon_set(a, t)
        return None if w is None else "Shield" in w["label"]

    def bow_range(self, a, t):
        w = self.weapon_set(a, t)
        lab = (w or {}).get("label", "").lower()
        for k, v in BOW_RANGE.items():
            if k in lab: return v
        return DEFAULT_BOW

    def hit_skill(self, a, t, sid):
        """The skill behind a hit: the recorded one, else a skill a finished within 1.5 s before the hit (spells and
        signets are often recorded without their id), else None (an auto-attack)."""
        if sid is not None or a not in self.m.PL: return sid
        self.casts()
        best = None
        for c in self._by_agent.get(a, []):
            if c[4] == "finished" and t - 1.5 <= (c[3] or c[2]) <= t + .1: best = c
        return best[1] if best else None

    def hit_name(self, a, t, sid):
        s2 = self.hit_skill(a, t, sid)
        return self.sname(s2) if s2 is not None else "auto-attack"

    def is_attack(self, sid, kind=None):
        """An attack (can be blocked). Unnamed hits are auto-attacks unless they ignore armor (hex and spell effects)."""
        if sid is None: return kind != "armor_ignoring"
        return "Attack" in (self.sdata(sid).get("type") or "")

    def casts(self):
        """Every cast started: (agent, skill, start s, end s, outcome, target). Outcome: finished; interrupted (an
        interrupt recorded on that cast); "hit while Dazed" (stopped with no recorded interrupt, Dazed, and hit by an
        attack during the cast: Daze makes any attack interrupt a spell); cancelled (stopped otherwise: a fake cast or a
        deliberate cancel). Self casts get the caster as target."""
        if self._casts is None:
            out, open_ = [], {}
            irs = collections.defaultdict(list)
            for i in (self.m.o.get("interrupts") or []): irs[i[3]].append((i[0] / 10, i[4]))
            for e in self.ev:
                c, a = e[1], e[2]
                if c == "cs": open_[a] = [a, e[4], e[0] / 10, None, None, e[3] if e[3] is not None else a]
                elif c in ("cf", "ir", "cx") and a in open_:
                    x = open_.pop(a); x[3] = e[0] / 10
                    hit = [k for k, (t, sk) in enumerate(irs.get(a, [])) if abs(t - x[3]) <= .3 and (sk == x[1] or sk is None)]
                    if hit or c == "ir":
                        if hit: irs[a].pop(hit[0])          # each recorded interrupt explains one cast only
                        x[4] = "interrupted"
                    elif c == "cf": x[4] = "finished"
                    elif self.has(a, "c", "dazed", x[2]) and any(d[2] is None or self.is_attack(d[2]) for d in
                                                               [(f[0], f[2], f[4]) for f in self.events(x[2], x[3] + .2, {"dm"}) if f[3] == a]):
                        x[4] = "hit while Dazed"
                    else: x[4] = "cancelled"
                    out.append(tuple(x))
            self._casts = out
            self._use = collections.defaultdict(list); self._by_agent = collections.defaultdict(list)
            for x in out: self._use[(x[0], x[1])].append(x[2]); self._by_agent[x[0]].append(x)
        return self._casts

    def last_use(self, a, sid, t):
        self.casts(); L = self._use.get((a, sid), [])
        i = bisect.bisect_right(L, t)
        return L[i - 1] if i else -99

    def casting_at(self, a, t):
        return any(c[0] == a and c[2] <= t <= (c[3] or c[2] + 1) for c in self.casts())

    def damage_on(self, a, t0, t1):
        return [(e[0] / 10, e[2], e[4], e[5] or 0, e[6] if len(e) > 6 else None) for e in self.events(t0, t1, {"dm"})
                if e[3] == a and e[2] in self.m.PL and self.m.team(e[2]) != self.m.team(a) and (e[5] or 0) > 0]

    def effects_on(self, a, fam, t0, t1):
        """Effects (family c condition, h hex, e enchantment) on a that started in the window:
        (start s, end s or None, caster, name or skill, how it ended)."""
        return [(e[0] / 10, e[1] / 10 if e[1] is not None else None, e[4], e[7] if fam == "c" else self.sname(e[3]), e[6])
                for e in self.m.o.get("effects", []) if e[2] == fam and e[5] == a and e[0] is not None and t0 * 10 <= e[0] <= t1 * 10]

    def conds_on(self, a, t0, t1):
        return [(x[0], x[2], x[3]) for x in self.effects_on(a, "c", t0, t1) if x[3]]

    def has(self, a, fam, name, t):
        """Was effect name (condition name, or skill name) on a at time t?"""
        for e in self.m.o.get("effects", []):
            if e[2] != fam or e[5] != a or e[0] is None or e[0] > t * 10: continue
            if (e[7] if fam == "c" else self.sname(e[3])) == name and (e[1] is None or e[1] >= t * 10): return True
        return False

    def kds_on(self, a, t0, t1):
        return [(k[0] / 10, k[1], self.sname(k[3])) for k in (self.m.o.get("knockdowns") or []) if k[2] == a and t0 * 10 <= k[0] <= t1 * 10]

    def intr_on(self, a, t0, t1):
        """Interrupts a suffered: (t, interrupter, interrupt skill, skill interrupted, its target, cast ms)."""
        return [(i[0] / 10, i[1], self.sname(i[2]), self.sname(i[4]), i[5], i[6]) for i in (self.m.o.get("interrupts") or [])
                if i[3] == a and t0 * 10 <= i[0] <= t1 * 10]

    # ---- the questions
    def position(self, a, t0, t1):
        """Out of position? Per second: nearest allied healer (other than itself), allies and enemies within casting range,
        nearest enemy, and whether it was its team's closest player to the enemy."""
        own = [b for b in self.players(self.m.team(a)) if b != a]; foes = self.enemies(a)
        rows = []
        for t in range(int(t0), int(t1) + 1):
            if not self.alive(a, t): continue
            dh = [self.dist(a, b, t) for b in own if b in self.healers and self.alive(b, t)]
            dh = [d for d in dh if d is not None]
            al = sum(1 for b in own if self.alive(b, t) and (self.dist(a, b, t) or 1e9) <= CAST_R)
            de = [d for d in (self.dist(a, b, t) for b in foes if self.alive(b, t)) if d is not None]
            en = sum(1 for d in de if d <= CAST_R)
            mine = min(de) if de else None
            closer = sum(1 for b in own if self.alive(b, t) and (min([d for d in (self.dist(b, f, t) for f in foes if self.alive(f, t)) if d is not None] or [1e9]) < (mine or 0)))
            rows.append({"t": t, "healer": min(dh) if dh else None, "allies": al, "enemies": en, "enemy": mine, "front": closer == 0})
        if not rows: return {"answer": "unclear", "why": "no positions recorded"}
        def med(k, L=rows):
            v = [r[k] for r in L if r[k] is not None]
            return statistics.median(v) if v else None
        last = rows[-6:]
        meas = {"healer_dist_median": med("healer"), "healer_dist_last5s": statistics.median([r["healer"] for r in last if r["healer"] is not None] or [0]),
                "out_of_healer_range_share": round(sum(1 for r in rows if r["healer"] is None or r["healer"] > CAST_R) / len(rows), 2),
                "allies_in_range_median": med("allies"), "enemies_in_range_median": med("enemies"),
                "nearest_enemy_median": med("enemy"), "front_share": round(sum(r["front"] for r in rows) / len(rows), 2)}
        # the last seconds (Denning, after batch 9: a ranged spike that closes in only for the last seconds read "not in
        # position" from the window's median); every tested length, the chosen one (position_window()) is judged on
        for n in POS_WINDOWS:
            L = rows[-(n + 1):]
            meas[f"last{n}s"] = {"healer_dist": med("healer", L), "nearest_enemy": med("enemy", L), "enemies_in_range": med("enemies", L),
                                 "allies_in_range": med("allies", L), "front_share": round(sum(r["front"] for r in L) / len(L), 2)}
        return {"measures": meas, "rows": rows}

    def prots(self, a, t0, t1):
        """Prots and heals on it: when each came against the burst, and what each could act on."""
        dmg = self.damage_on(a, t0, t1)
        tot = sum(d[3] for d in dmg) or 1
        att = sum(d[3] for d in dmg if self.is_attack(self.hit_skill(d[1], d[0], d[2]), d[4]))
        ign = sum(d[3] for d in dmg if d[4] == "armor_ignoring")
        kd_n = len(self.kds_on(a, t0, t1))
        # first big hit: the start of the 2 s with the most damage
        burst_t, burst = None, 0
        for i, d in enumerate(dmg):
            s = sum(x[3] for x in dmg[i:] if x[0] <= d[0] + 2)
            if s > burst: burst, burst_t = s, d[0]
        own = set(self.players(self.m.team(a)))
        got = []
        for c in self.casts():
            if c[0] not in own or c[5] != a or not (t0 <= c[2] <= t1): continue
            sd = self.sdata(c[1]); causes = sd.get("causes") or []
            if not (set(causes) & {"Block", "Damage Reduction", "Knockdown Immunity", "Healing"}): continue
            kind = ("block" if "Block" in causes else "reduce" if "Damage Reduction" in causes else
                    "kd immunity" if "Knockdown Immunity" in causes else "heal")
            acts_on = {"block": att / tot, "reduce": 1.0, "kd immunity": 1.0 if kd_n else 0.0, "heal": 1.0}[kind]
            when = ("pre-prot" if burst_t is not None and c[2] < burst_t else
                    "reaction" if burst_t is not None and c[2] <= burst_t + 1.5 else "late" if burst_t is not None else "no burst")
            got.append({"t": round(c[2], 1), "by": self.name(c[0]), "skill": self.sname(c[1]), "kind": kind, "outcome": c[4],
                        "when": when, "acts_on_share": round(acts_on, 2)})
        # ready prots on allied healers in range, never used on it
        unused = []
        for h in own:
            if h == a or h not in self.healers or not self.alive(h, t1 - 1): continue
            bar = [self.sname(s) for s in (self.m.A[h].get("bar") or []) if s]
            for sk in bar:
                sd = skilldata().get(sk) or {}
                if not (set(sd.get("causes") or []) & {"Block", "Damage Reduction"}) or "allies" not in (sd.get("target") or ""): continue
                used = [c for c in self.casts() if c[0] == h and self.sname(c[1]) == sk and c[2] <= t1]
                last = max([c[2] for c in used], default=-99)
                ready = (burst_t or t1) - last >= _act(sd.get("recharge"))
                inrange = (self.dist(a, h, burst_t or t1) or 1e9) <= CAST_R
                on_it = any(c[5] == a and (burst_t or t1) - 2 <= c[2] <= t1 for c in used)
                busy = [f"{self.sname(c[1])} on {self.name(c[5]) if c[5] is not None else '-'}" for c in self.casts()
                        if c[0] == h and (burst_t or t1) - 1 <= c[2] <= t1]
                if ready and inrange and not on_it:
                    unused.append({"healer": self.name(h), "skill": sk, "busy_with": busy[:3]})
        # each knockdown: was knockdown immunity on it, and which allied healer had it ready and in range
        kd_rows = []
        for tk, src, sk in self.kds_on(a, t0, t1):
            imm = [sk2 for sk2, sd in skilldata().items() if "Knockdown Immunity" in (sd.get("causes") or []) and self.has(a, "e", sk2, tk)]
            ready = []
            for h in own:
                if h not in self.healers or not self.alive(h, tk): continue
                for sid in (self.m.A[h].get("bar") or []):
                    sd = self.sdata(sid)
                    if not sid or "Knockdown Immunity" not in (sd.get("causes") or []): continue
                    tgt = sd.get("target") or ""
                    if h == a and "other" in tgt: continue          # e.g. Aura of Stability: other allies only
                    if tk - self.last_use(h, sid, tk) >= _act(sd.get("recharge")) and (h == a or (self.dist(a, h, tk) or 1e9) <= CAST_R):
                        ready.append(f"{self.name(h)} {self.sname(sid)}")
            prev = [x for x in self.m.o.get("effects", []) if x[2] == "e" and x[5] == a and x[0] is not None and x[0] <= tk * 10
                    and "Knockdown Immunity" in (self.sdata(x[3]).get("causes") or [])]
            last = max(prev, key=lambda x: x[0]) if prev else None
            kd_rows.append({"t": clock(tk), "by": self.name(src), "skill": sk, "immunity_up": bool(imm), "ready_in_range": ready,
                            "last_immunity": (f"{self.sname(last[3])} by {self.name(last[4])} {clock(last[0] / 10)} to "
                                              f"{clock(last[1] / 10) if last[1] else '?'}") if last else None})
        meas = {"burst_2s": round(burst), "burst_at": clock(burst_t) if burst_t is not None else None,
                "damage": round(tot), "attack_share": round(att / tot, 2), "armor_ignoring_share": round(ign / tot, 2),
                "knockdowns": kd_n, "prots_cast": sum(1 for g in got if g["kind"] != "heal"),
                "prots_landed": sum(1 for g in got if g["kind"] != "heal" and g["outcome"] == "finished"),
                "reaction_prots": sum(1 for g in got if g["kind"] != "heal" and g["when"] in ("pre-prot", "reaction") and g["outcome"] == "finished")}
        meas["self_prots"] = sum(1 for g in got if g["kind"] != "heal" and g["by"] == self.name(a))
        meas["teammate_prots"] = sum(1 for g in got if g["kind"] != "heal" and g["by"] != self.name(a))
        return {"measures": meas, "cast": got, "ready_unused": unused, "knockdowns": kd_rows}

    def monk_pressure(self, tm, t0, t1):
        """Interrupts, knockdowns, Daze and hexes on the team's healers; casts started against finished."""
        hs = [h for h in self.players(tm) if h in self.healers]
        mins = max((t1 - t0) / 60, 1 / 60)
        cs = [c for c in self.casts() if c[0] in hs and t0 <= c[2] <= t1]
        ir = [c for c in cs if c[4] == "interrupted"]
        daze = [x for h in hs for x in self.conds_on(h, t0, t1) if x[2] == "dazed"]
        kd = [k for h in hs for k in self.kds_on(h, t0, t1)]
        hexes = [x for h in hs for x in self.effects_on(h, "h", t0, t1)]
        meas = {"healers": len(hs), "interrupts_per_min": round(len(ir) / mins, 1), "interrupted": len(ir),
                "casts": len(cs), "finished_share": round(sum(1 for c in cs if c[4] == "finished") / len(cs), 2) if cs else None,
                "dazed": len(daze), "knockdowns": len(kd), "hexes": len(hexes)}
        detail = [f"{clock(i[0])} {self.name(h)} {i[3]} by {self.name(i[1])} {i[2]}" for h in hs for i in self.intr_on(h, t0, t1)]
        detail += [f"{clock(x[0])} {self.name(h)} hexed: {x[3]} by {self.name(x[2])}" for h in hs for x in self.effects_on(h, "h", t0, t1)]
        detail += [f"{clock(x[0])} {self.name(h)} Dazed by {self.name(x[1])}" for h in hs for x in self.conds_on(h, t0, t1) if x[2] == "dazed"]
        return {"measures": meas, "interrupted": detail}

    def sets_damage(self, tm, t0, t1, who=None):
        """Damage taken while holding a set without a shield and not casting, and what a shield would have stopped."""
        out = {}
        for a in (who or self.players(tm)):
            tot = off = off_ar = 0
            for t, src, sid, n, kind in self.damage_on(a, t0, t1):
                tot += n
                sh = self.shield(a, t)
                if sh is False and not self.casting_at(a, t):
                    off += n
                    if kind != "armor_ignoring": off_ar += n
            has_shield = any("Shield" in s["label"] for s in self.sets.get(a, []))
            if tot: out[self.name(a)] = {"taken": round(tot), "off_shield_not_casting": round(off), "shield_would_stop": round(off_ar * SHIELD_CUT),
                                         "has_shield_set": has_shield}
        tot = sum(v["taken"] for v in out.values()) or 1
        meas = {"taken": round(tot), "off_shield_share": round(sum(v["off_shield_not_casting"] for v in out.values() if v["has_shield_set"]) / tot, 2),
                "shield_would_stop": sum(v["shield_would_stop"] for v in out.values() if v["has_shield_set"])}
        return {"measures": meas, "players": out}

    def output(self, tm, t0, t1):
        """The team's damage on enemy players: per second, concentration, armor-ignoring share, spikes landed."""
        dmg = [(e[0] / 10, e[2], e[3], e[5] or 0, e[6] if len(e) > 6 else None) for e in self.events(t0, t1, {"dm"})
               if e[2] in self.m.PL and self.m.team(e[2]) == tm and e[3] in self.m.PL and self.m.team(e[3]) != tm and (e[5] or 0) > 0]
        secs = max(t1 - t0, 1); tot = sum(d[3] for d in dmg)
        by_t = collections.Counter(); by_src = collections.Counter()
        for d in dmg: by_t[d[2]] += d[3]; by_src[d[1]] += d[3]
        spikes = 0
        for tgt in by_t:
            L = sorted((d[0], d[3]) for d in dmg if d[2] == tgt); last = -99
            for i, (t, _) in enumerate(L):
                if t - last >= 6 and sum(v for tt, v in L[i:] if tt <= t + 3) >= 400: spikes += 1; last = t
        meas = {"dps": round(tot / secs, 1), "top_target_share": round(by_t.most_common(1)[0][1] / tot, 2) if tot else None,
                "armor_ignoring_share": round(sum(d[3] for d in dmg if d[4] == "armor_ignoring") / tot, 2) if tot else None,
                "spikes_400_in_3s": spikes, "dealers": sum(1 for v in by_src.values() if v >= 0.1 * tot)}
        return {"measures": meas, "targets": [(self.name(k), round(v)) for k, v in by_t.most_common(4)],
                "dealers": [(self.name(k), round(v)) for k, v in by_src.most_common(5)]}

    def peel(self, a, t0, t1, attackers=None):
        """What the victim's team did to the players hitting it."""
        if attackers is None:
            c = collections.Counter()
            for _, src, _, n, _ in self.damage_on(a, t0, t1): c[src] += n
            for _, src, _ in self.conds_on(a, t0, t1):
                if src in self.m.PL: c[src] += 1
            attackers = [k for k, v in c.items() if v >= 30]
        own = set(self.players(self.m.team(a))) - {a}
        out = {}
        for x in attackers:
            hits = [e for e in self.events(t0, t1, {"dm"}) if e[2] in own and e[3] == x and (e[5] or 0) > 0]
            conds = [c for c in self.conds_on(x, t0, t1) if c[2] in SNARES and c[1] in own]
            irs = self.intr_on(x, t0, t1)
            kd = self.kds_on(x, t0, t1)
            hx = [h for h in self.effects_on(x, "h", t0, t1) if h[2] in own]
            touched = sorted({e[0] / 10 for e in hits} | {c[0] for c in conds} | {i[0] for i in irs} | {k[0] for k in kd} | {h[0] for h in hx})
            free = 0; prev = t0
            for t in touched + [t1]:
                free = max(free, t - prev); prev = t
            near = [d for d in (self.dist(x, b, t1 - 2) for b in own if b not in self.healers and self.alive(b, t1 - 2)) if d is not None]
            out[self.name(x)] = {"damage_taken": round(sum(e[5] for e in hits)), "snares_blind_weakness": [c[2] for c in conds],
                                 "interrupted": len(irs), "knocked_down": len(kd), "hexed": len(hx),
                                 "longest_free_s": round(free, 1), "nearest_own_non_healer": round(min(near)) if near else None}
        # peel = something that cut the attacker's output: a snare, Blind or Weakness, an interrupt, a knockdown or a hex
        # from the victim's team (damage on the attacker is reported but is not peel by itself)
        meas = {"attackers": len(out), "pressured": sum(1 for v in out.values() if v["snares_blind_weakness"] or v["interrupted"] or v["knocked_down"] or v["hexed"]),
                "longest_free_s": max([v["longest_free_s"] for v in out.values()], default=None)}
        return {"measures": meas, "attackers": out}

    def casting(self, a, t0, t1):
        """Every cast it started: outcome, whether a ready enemy interrupt was in range, whether it was Dazed."""
        foes = self.enemies(a); rows = []
        intr = {}
        for f in foes:
            for sid in (self.m.A[f].get("bar") or []):
                sd = self.sdata(sid)
                if sid and "Interrupt" in (sd.get("causes") or []): intr.setdefault(f, []).append((sid, sd))
        for c in self.casts():
            if c[0] != a or not (t0 <= c[2] <= t1): continue
            t = c[2]
            dazed = self.has(a, "c", "dazed", t)
            ready = []
            for f, L in intr.items():
                if not self.alive(f, t): continue
                d = self.dist(a, f, t)
                if d is None: continue
                for sid, sd in L:
                    rng = self.bow_range(f, t) if "Bow" in (sd.get("type") or "") else CAST_R
                    last = self.last_use(f, sid, t - .01)
                    if d <= rng and t - last >= _act(sd.get("recharge")): ready.append(f"{self.name(f)} {self.sname(sid)}")
            rows.append({"t": round(t, 1), "skill": self.sname(c[1]), "activation": _act(self.sdata(c[1]).get("activation")),
                         "outcome": c[4], "dazed": dazed, "ready_interrupts": ready})
        risky = [r for r in rows if r["ready_interrupts"]]
        n = len(rows) or 1
        meas = {"casts": len(rows), "interrupted_share": round(sum(1 for r in rows if r["outcome"] == "interrupted") / n, 2),
                "cancelled_share": round(sum(1 for r in rows if r["outcome"] == "cancelled") / n, 2),
                "dazed_share": round(sum(1 for r in rows if r["dazed"]) / n, 2),
                "interrupted": sum(1 for r in rows if r["outcome"] == "interrupted"),
                "hit_while_dazed": sum(1 for r in rows if r["outcome"] == "hit while Dazed"),
                "cancelled": sum(1 for r in rows if r["outcome"] == "cancelled"),
                "into_ready_interrupt": len(risky), "while_dazed": sum(1 for r in rows if r["dazed"]),
                "cancelled_when_threatened": sum(1 for r in risky if r["outcome"] == "cancelled")}
        return {"measures": meas, "casts": rows}

    def disruption(self, a, t0, t1):
        """Defensive or offensive play by a disrupting player (Denning, 2026-11-07, for Mesmers: defensive = interrupting
        offensive skills and casting on the enemy midline and frontline; offensive = interrupting the enemy monks). Counts
        a's interrupts landed and a's casts aimed at an enemy in the window, split by the target's line (healer against
        midline or frontline). defensive_share = the midline/frontline share of both together (None if a did neither)."""
        foe = 3 - self.m.team(a)
        def cls(b): return "healer" if b in self.healers else "mid/front"
        intr = collections.Counter(cls(i[3]) for i in (self.m.o.get("interrupts") or [])
                                   if i[1] == a and i[3] in self.m.PL and self.m.team(i[3]) == foe and t0 * 10 <= i[0] <= t1 * 10)
        casts = collections.Counter(cls(c[5]) for c in self.casts()
                                    if c[0] == a and t0 <= c[2] <= t1 and c[5] in self.m.PL and self.m.team(c[5]) == foe)
        n = sum(intr.values()) + sum(casts.values())
        return {"interrupts": dict(intr), "casts_on_enemies": dict(casts),
                "defensive_share": round((intr["mid/front"] + casts["mid/front"]) / n, 2) if n else None, "actions": n}

    def conditions(self, a, t0, t1):
        """Each condition put on it: by whom, from how far, was the attacker pressured, the victim's set and position,
        and whether it was removed."""
        own = set(self.players(self.m.team(a)))
        bar = {self.sname(s) for s in (self.m.A[a].get("bar") or []) if s}
        own_removal = sorted(s for s in bar if "Condition" in ((skilldata().get(s) or {}).get("removes") or []))
        rows = []
        for t, end, src, name, how in self.effects_on(a, "c", t0, t1):
            if not name: continue
            rem = [c for c in self.casts() if c[0] in own and c[5] == a and t <= c[2] <= t1 + 1
                   and "Condition" in (self.sdata(c[1]).get("removes") or [])]
            by = [f"{clock(c[2])} {self.name(c[0])} {self.sname(c[1])} ({c[4]})" for c in rem]
            # removed = a removal finished within a second of the condition ending (the replay does not say why it ended)
            removed = [end] if end is not None and any(c[4] == "finished" and abs((c[3] or c[2]) - end) <= 1.0 for c in rem) else []
            pres = self.peel(a, t - 6, t, [src]) if src in self.m.PL else None
            hl = [d for d in (self.dist(a, h, t) for h in own if h in self.healers and h != a and self.alive(h, t)) if d is not None]
            rows.append({"t": round(t, 1), "condition": name, "by": self.name(src) if src in self.m.PL else "?",
                         "range": round(self.dist(a, src, t)) if src in self.m.PL and self.dist(a, src, t) else None,
                         "attacker_pressured_6s": (list(pres["attackers"].values())[0] if pres and pres["attackers"] else None),
                         "victim_shield": self.shield(a, t), "victim_casting": self.casting_at(a, t),
                         "nearest_allied_healer": round(min(hl)) if hl else None,
                         "removed_after_s": round(removed[0] - t, 1) if removed else None, "ended": f"{clock(end)} ({how})" if end is not None else None,
                         "removal_casts": by})
        return {"measures": {"conditions": len(rows), "removed": sum(1 for r in rows if r["removed_after_s"] is not None),
                             "own_removal_on_bar": own_removal}, "rows": rows}


# ---- benchmarks: the same measurements in every stored replay, by role group
def _bench_match(rid):
    F = Forensics(rid); m = F.m; out = collections.defaultdict(lambda: collections.defaultdict(list))
    end = int(m.o["meta"].get("match_length_s") or max(F.T) / 10)
    for a in m.PL:
        g = role_group(m, a)
        foes = F.enemies(a); own = [b for b in F.players(m.team(a)) if b != a]
        for t in range(10, end, 3):
            if not F.alive(a, t): continue
            de = [d for d in (F.dist(a, b, t) for b in foes if F.alive(b, t)) if d is not None]
            if not de or min(de) > 1500: continue            # only seconds in a fight
            dh = [d for d in (F.dist(a, b, t) for b in own if b in F.healers and F.alive(b, t)) if d is not None]
            if dh: out[g]["healer_dist"].append(min(dh))
            out[g]["nearest_enemy"].append(min(de))
            out[g]["enemies_in_range"].append(sum(1 for d in de if d <= CAST_R))
            out[g]["allies_in_range"].append(sum(1 for b in own if F.alive(b, t) and (F.dist(a, b, t) or 1e9) <= CAST_R))
    # which last-seconds window explains deaths best: each death's last N s against moments the same player was in a
    # fight and didn't die in the next 15 s (sampled every 9 s), nearest enemy and enemies in casting range
    dmap = collections.defaultdict(list)
    for e in m.o["ev"]:
        if e[1] == "dt" and e[2] in m.PL: dmap[e[2]].append(e[0] / 10)
    for a in m.PL:
        foes = F.enemies(a); dts = [x for x in dmap[a] if 10 < x < end]
        def lastn(t, n):
            ne, er = [], []
            for tt in range(int(t) - n, int(t) + 1):
                if not F.alive(a, tt): continue
                de = [d for d in (F.dist(a, b, tt) for b in foes if F.alive(b, tt)) if d is not None]
                if de: ne.append(min(de)); er.append(sum(1 for d in de if d <= CAST_R))
            return (statistics.median(ne), statistics.median(er)) if ne else None
        for t in dts:
            for n in POS_WINDOWS:
                v = lastn(t - 0.5, n)
                if v: out["position_test"][f"death_{n}"].append(v)
        for t in range(20, end - 15, 9):
            if not F.alive(a, t) or any(t <= x <= t + 15 for x in dts): continue
            de = [d for d in (F.dist(a, b, t) for b in foes if F.alive(b, t)) if d is not None]
            if not de or min(de) > 1500: continue
            for n in POS_WINDOWS:
                v = lastn(t, n)
                if v: out["position_test"][f"control_{n}"].append(v)
    # per 20 s window: monk pressure, team output, off-shield damage, casting into ready interrupts
    for tm in F.tag:
        for t0 in range(20, end - 20, 20):
            mp = F.monk_pressure(tm, t0, t0 + 20)["measures"]
            if mp["casts"]: out["team"]["healer_interrupts_per_min"].append(mp["interrupts_per_min"])
            o = F.output(tm, t0, t0 + 20)["measures"]
            if o["dps"] > 5:
                out["team"]["dps"].append(o["dps"])
                if o["top_target_share"] is not None: out["team"]["top_target_share"].append(o["top_target_share"])
            sd = F.sets_damage(tm, t0, t0 + 20)["measures"]
            if sd["taken"] > 200: out["team"]["off_shield_share"].append(sd["off_shield_share"])
    for a in m.PL:
        g = role_group(m, a)
        if a in F.healers:
            for t0 in range(0, end - 20, 20):
                c = [x for x in F.casts() if x[0] == a and t0 <= x[2] < t0 + 20]
                if len(c) < 3: continue
                n = len(c)
                out[g]["casts_interrupted_share"].append(sum(1 for x in c if x[4] == "interrupted") / n)
                out[g]["casts_cancelled_share"].append(sum(1 for x in c if x[4] == "cancelled") / n)
                out[g]["casts_dazed_share"].append(sum(1 for x in c if F.has(a, "c", "dazed", x[2])) / n)
        # peel: for each burst on this player (250+ in 2 s), how pressured its attackers were in the 6 s before
        dmg = F.damage_on(a, 0, end); last = -99
        for i, d in enumerate(dmg):
            if d[0] - last < 6 or sum(x[3] for x in dmg[i:] if x[0] <= d[0] + 2) < 250: continue
            last = d[0]
            p = F.peel(a, d[0] - 6, d[0] + 2)["measures"]
            if p["attackers"]: out[g]["peel_share"].append(p["pressured"] / p["attackers"])
            pr = F.prots(a, d[0] - 3, d[0] + 3)["measures"]
            out[g]["reaction_prot"].append(1.0 if pr["reaction_prots"] else 0.0)
    return {g: dict(v) for g, v in out.items()}


def build_bench():
    import subprocess
    from multiprocessing import Pool
    ids = list(json.loads(subprocess.check_output(["git", "-C", REPO, "show", "origin/replays:index.json"]))["matches"])
    allv = collections.defaultdict(lambda: collections.defaultdict(list))
    with Pool(os.cpu_count() or 2) as p:
        for r in p.imap_unordered(_bench_match, ids):
            for g, d in r.items():
                for k, v in d.items(): allv[g][k] += v
    pt = allv.pop("position_test", {})
    pw = _position_auc(pt)
    q = lambda L: {str(p): round(statistics.quantiles(L, n=100, method="inclusive")[p - 1], 2) for p in (10, 20, 50, 80, 90)} if len(L) >= 20 else None
    res = {"about": "Forensics benchmarks: percentiles of each measurement by role group over every stored replay "
                    "(positions sampled every 3 s while an enemy is within 1,500; team measures per 20 s window; peel and "
                    "reaction prots per burst of 250+ damage in 2 s). Rebuilt by forensics.py bench.",
           "matches": len(ids), "position_window": pw,
           "groups": {g: {k: {"n": len(v), "p": q(v), "mean": round(statistics.mean(v), 3)} for k, v in d.items() if v}
                      for g, d in allv.items()}}
    os.makedirs(os.path.dirname(BENCH), exist_ok=True)
    json.dump(res, open(BENCH, "w"), indent=1)
    return res


def _position_auc(pt):
    """For each tested window: how well the last N s separate deaths from fight moments without one (AUC: the chance
    a death's reading is worse than a moment's; closer nearest enemy, more enemies in casting range), averaged over
    the two measures. The highest is chosen."""
    def auc(pos, neg):
        if not pos or not neg: return None
        neg = sorted(neg); import bisect
        tot = sum(bisect.bisect_left(neg, x) + 0.5 * (bisect.bisect_right(neg, x) - bisect.bisect_left(neg, x)) for x in pos)
        return tot / (len(pos) * len(neg))
    res = {}
    for n in POS_WINDOWS:
        dth, ctl = pt.get(f"death_{n}") or [], pt.get(f"control_{n}") or []
        a1 = auc([-x[0] for x in dth], [-x[0] for x in ctl]); a2 = auc([x[1] for x in dth], [x[1] for x in ctl])
        if a1 is None or a2 is None: continue
        res[str(n)] = {"deaths": len(dth), "moments": len(ctl), "auc_nearest_enemy": round(a1, 3), "auc_enemies_in_range": round(a2, 3),
                       "auc": round((a1 + a2) / 2, 3)}
    chosen = int(max(res, key=lambda k: res[k]["auc"])) if res else POS_DEFAULT
    return {"chosen_s": chosen, "tested": res, "about": "seconds before a death that position is judged on: the window whose "
            "nearest enemy and enemies in casting range best separate deaths from fight moments without one (AUC)"}


def position_window():
    return int((bench().get("position_window") or {}).get("chosen_s") or POS_DEFAULT)


_B = None
def bench():
    global _B
    if _B is None: _B = json.load(open(BENCH)) if os.path.exists(BENCH) else {"groups": {}}
    return _B


def place(group, key, v):
    """Where v falls for that role group: (percentile band text, low/mid/high) or (None, None) without a benchmark."""
    b = (bench()["groups"].get(group) or {}).get(key) or (bench()["groups"].get("team") or {}).get(key)
    if v is None or not b or not b.get("p"): return None, None
    p = {int(k): x for k, x in b["p"].items()}
    lo, hi = p[BENCH_CUT[0]], p[BENCH_CUT[1]]
    band = "low" if v < lo else "high" if v > hi else "usual"
    pct = next((f"below the {k}th percentile" for k in (10, 20, 50) if v < p[k]), None) or \
          next((f"above the {k}th percentile" for k in (90, 80, 50) if v > p[k]), "around the median")
    return f"{pct} for {group} (median {p[50]:g}, n {b['n']})", band


# ---- one death, every question
def death(rid, tag, role, t, F=None):
    F = F or Forensics(rid)
    a = F.role_of(tag, role)
    if a is None: return {"error": f"no {tag} {role}"}
    g = role_group(F.m, a); tm = F.m.team(a); foe = 3 - tm if tm in (1, 2) else None
    t0 = t - WINDOW
    pos = F.position(a, t0, t); pr = F.prots(a, t0, t); mp = F.monk_pressure(tm, t0, t)
    sd = F.sets_damage(tm, t0, t); out = F.output(foe, t0, t); own_out = F.output(tm, t0, t)
    pe = F.peel(a, t0, t); ca = F.casting(a, t0, t); co = F.conditions(a, t0, t)
    ans = {}
    # position
    pm = pos.get("measures", {})
    n = position_window(); ln = pm.get(f"last{n}s") or {}
    ph, bh = place(g, "healer_dist", ln.get("healer_dist")); pe_, be = place(g, "nearest_enemy", ln.get("nearest_enemy"))
    pn, bn = place(g, "allies_in_range", ln.get("allies_in_range"))
    flags = [bh == "high", be == "low", bn == "low", (ln.get("front_share") or 0) >= 0.5]
    ans["position"] = {"q": "Out of position?", "answer": "yes" if sum(flags) >= 2 else "partly" if sum(flags) == 1 else "no",
                       "judged_on_last_s": n, "measures": pm,
                       "placed": {f"healer_dist_last{n}s": ph, f"nearest_enemy_last{n}s": pe_, f"allies_in_range_last{n}s": pn},
                       "window_context": {"nearest_enemy_median": pm.get("nearest_enemy_median"), "allies_in_range_median": pm.get("allies_in_range_median"),
                                          "healer_dist_median": pm.get("healer_dist_median")}}
    # prots
    m = pr["measures"]
    right = [c for c in pr["cast"] if c["kind"] != "heal"]
    wrong = [c for c in right if c["acts_on_share"] < 0.5]
    rp = ((bench()["groups"].get(g) or {}).get("reaction_prot") or {}).get("mean")
    ans["prots"] = {"q": "Did it get prots, on time, and the right ones?",
                    "placed": f"bursts on a {g} get a pre-prot or reaction prot {rp:.0%} of the time" if rp is not None else None,
                    "answer": (("no prots" if not right else "late or interrupted" if not m["reaction_prots"] else
                                "partly the wrong kind" if wrong else "yes")
                               + f" ({m['teammate_prots']} from teammates, {m['self_prots']} self; {m['prots_landed']} of {m['prots_cast']} landed)"),
                    "measures": m, "cast": pr["cast"], "ready_unused": pr["ready_unused"], "knockdowns": pr["knockdowns"]}
    # monk pressure
    mm = mp["measures"]; pmp, bmp = place("team", "healer_interrupts_per_min", mm["interrupts_per_min"])
    ans["monk_pressure"] = {"q": "Were the healers under interrupt pressure?", "answer": {"high": "yes", "usual": "usual", "low": "no"}.get(bmp, "unclear"),
                            "measures": mm, "placed": pmp, "interrupted": mp["interrupted"]}
    # sets
    sm = sd["measures"]; ps, bs = place("team", "off_shield_share", sm["off_shield_share"])
    ans["sets"] = {"q": "Was the team taking unnecessary damage off its shield sets?", "answer": {"high": "yes", "usual": "usual", "low": "no"}.get(bs, "unclear"),
                   "measures": sm, "placed": ps, "players": sd["players"]}
    # enemy output and own output
    om = out["measures"]; po, bo = place("team", "dps", om["dps"])
    oo = own_out["measures"]; poo, boo = place("team", "dps", oo["dps"])
    ans["enemy_output"] = {"q": "How hard was the killing team hitting?", "answer": bo or "unclear", "measures": om, "placed": po,
                           "targets": out["targets"], "dealers": out["dealers"]}
    ans["own_output"] = {"q": "Was the victim's team's damage performing (pressure that keeps the enemy busy)?",
                         "answer": {"low": "no", "usual": "usual", "high": "yes"}.get(boo, "unclear"), "measures": oo, "placed": poo,
                         "targets": own_out["targets"], "dealers": own_out["dealers"]}
    # peel
    pk = pe["measures"]; share = pk["pressured"] / pk["attackers"] if pk["attackers"] else None
    pp, bp = place(g, "peel_share", share)
    pans = {"low": "no", "usual": "usual", "high": "yes"}.get(bp, "unclear" if share is None else ("no" if share == 0 else "partly"))
    if pans == "yes" and (pk["longest_free_s"] or 0) >= 8: pans = f"partly (controlled, but an attacker was left free for {pk['longest_free_s']} s)"
    if share == 0: pans = "no" + (" (peel on a burst is rare: most bursts on this role get none)" if bp == "usual" else "")
    ans["peel"] = {"q": "Did it get peel?", "answer": pans,
                   "measures": dict(pk, pressured_share=round(share, 2) if share is not None else None), "placed": pp, "attackers": pe["attackers"]}
    # casting
    cm = ca["measures"]
    pi, bi = place(g, "casts_interrupted_share", cm["interrupted_share"]); pc, bc = place(g, "casts_cancelled_share", cm["cancelled_share"])
    pd_, bd = place(g, "casts_dazed_share", cm["dazed_share"])
    ans["casting"] = {"q": "Did it cast into ready interrupts, and cancel?",
                      "answer": ("interrupted far more than usual" if bi == "high" else "usual" if bi == "usual" else "rarely interrupted" if bi == "low" else "unclear")
                                + ("; cancelled less than usual" if bc == "low" else "; cancelled more than usual" if bc == "high" else ""),
                      "measures": cm, "placed": {"interrupted_share": pi, "cancelled_share": pc, "dazed_share": pd_}, "casts": ca["casts"]}
    ans["conditions"] = {"q": "How did the conditions land, and were they removed?", "measures": co["measures"], "rows": co["rows"]}
    ans["victim"] = {"name": F.name(a), "group": g, "set_now": (F.weapon_set(a, t - 1) or {}).get("label")}
    return ans


def lines(ans):
    """Markdown lines for a death's answers."""
    L = []
    v = ans.get("victim", {})
    L.append(f"**{v.get('name')}** ({v.get('group')}), set at death: {v.get('set_now')}")
    for k in ("position", "prots", "monk_pressure", "sets", "own_output", "enemy_output", "peel", "casting", "conditions"):
        x = ans[k]
        L.append(f"- **{x['q']}** {x.get('answer', '')}" + (f" ({x['placed']})" if isinstance(x.get('placed'), str) else ""))
        L.append(f"  - measures: {json.dumps(x.get('measures'), ensure_ascii=False)}")
        if isinstance(x.get("placed"), dict):
            for kk, vv in x["placed"].items():
                if vv: L.append(f"  - {kk}: {vv}")
        for key in ("cast", "ready_unused", "knockdowns", "interrupted", "attackers", "targets", "dealers", "rows"):
            if x.get(key):
                L.append(f"  - {key}: {json.dumps(x[key], ensure_ascii=False)[:900]}")
        if k == "casting":
            for c in x["casts"]: L.append(f"  - {c}")
        if k == "sets":
            for n, p in x["players"].items():
                if p["off_shield_not_casting"]: L.append(f"  - {n}: {p}")
    return L


def _t(s):
    mm, ss = s.split(":"); return int(mm) * 60 + float(ss)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["bench"]:
        r = build_bench(); print("benchmarks from", r["matches"], "matches:", ", ".join(r["groups"]))
    elif a[:1] == ["death"]:
        rid = a[1]
        if len(rid) < 36:
            import subprocess
            idx = json.loads(subprocess.check_output(["git", "-C", REPO, "show", "origin/replays:index.json"]))["matches"]
            rid = [k for k in idx if k.startswith(rid)][0]
        print("\n".join(lines(death(rid, a[2], a[3], _t(a[4])))))
    else: print(__doc__)
