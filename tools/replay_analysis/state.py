"""Per-second game state for one match: where every player is (zone), who is alive and when the dead come back,
death penalty, fight groups and the numbers in the main fight, the flag (carrier, stand owner, hold time, time to a
boost), pit NPCs alive, and estimated NPC and pit positions per map.

Usage:  python3 state.py <report id> [step seconds]   prints a compact timeline.
In code: st = GameState(Match.from_branch(id)); st.at(t_seconds) -> dict for that second.

Positions are game units; PIT_R ~ casting range around the Lord. NPC positions are not in the replay data, so they are
estimated from where melee players stood when hitting each NPC, and saved per map in data/maps/<map id>.json so later
matches on the same map reuse (and refine) them."""
import collections, json, math, os, statistics, sys
from replaylib import Match
from common import STAND_R, PIT_R, BASE_R, NEAR_R, REPO, RES_EVERY

MELEE = {"Warrior", "Dervish", "Assassin"}
STATIC_NPCS = ("guild_lord", "bodyguard", "knight", "archer")


def d(p, q): return math.dist(p, q) if p and q else 1e9


class MapGeo:
    """Bases, stand, pit and static NPC positions for one match, merged with what earlier matches learned."""

    def __init__(self, m, save=False):
        self.m = m
        self.map_id = str(m.o["meta"].get("map_id") or m.o["meta"]["map"])
        self.base = {tm: tuple(m.base[tm]) for tm in m.base}
        self.stand = tuple(m.stand)     # replaylib fills a missing stand from the map table
        self.spawn = self._flag_spawns()        # team -> where its flag appears (near its base)
        self.npcs = self._estimate()            # agent -> {kind, team, pos, n (samples), conf}
        self._merge_store(save)
        self.pit = {}
        for tm in (1, 2):
            lord = [v["pos"] for v in self.npcs.values() if v["team"] == tm and v["kind"] == "guild_lord" and v["pos"]]
            core = [v["pos"] for v in self.npcs.values() if v["team"] == tm and v["kind"] in ("bodyguard", "knight") and v["pos"]]
            if lord: self.pit[tm] = lord[0]
            elif core: self.pit[tm] = (statistics.mean(p[0] for p in core), statistics.mean(p[1] for p in core))
            else: self.pit[tm] = self.base.get(tm)
        for v in self.npcs.values():    # archers far from their Lord are outside archers
            v["pit"] = v["kind"] in ("guild_lord", "bodyguard", "knight") or (
                v["pos"] is not None and d(v["pos"], self.pit.get(v["team"])) < 3000)
        self._fill_roster()

    def _fill_roster(self):
        """Pit NPCs only appear in a replay once something touches them, so an untouched pit looked empty. Every pit
        starts with the standard roster (integrity.ROSTER, Denning); the ones never seen are added as alive all match
        at the pit (keys "roster:<team>:<kind>:<n>", never in npc_dead). If more archers than the roster sit near a
        pit, the nearest count as pit archers and the rest as outside archers."""
        from integrity import roster
        want = roster(self.map_id)
        added = {}
        for tm in (1, 2):
            pit = self.pit.get(tm)
            arch = sorted((a for a, v in self.npcs.items() if v["team"] == tm and v["kind"] == "archer" and v["pit"]),
                          key=lambda a: d(self.npcs[a]["pos"], pit))
            for a in arch[want["archer"]:]: self.npcs[a]["pit"] = False
            n = 0
            for kind, k in want.items():
                have = sum(1 for v in self.npcs.values() if v["team"] == tm and v["kind"] == kind and v["pit"])
                for i in range(have, k):
                    self.npcs[f"roster:{tm}:{kind}:{i}"] = dict(kind=kind, team=tm, pos=pit, n=0, conf="roster", pit=True)
                    n += 1
            added[tm] = n
        integ = self.m.o.get("integrity")
        if integ is not None: integ["roster_added"] = added

    SPAWN_CLUSTER_R = 400       # pickups within this of each other count as the same spot

    def _flag_spawns(self):
        """Each team's flag spawn: the densest cluster of its pickups on its own half (a new flag always appears at the
        same spot, so spawn pickups land together, while dropped flags are picked up all over). Until 2026-11-07 this
        took pickups more than 6,000 from the stand only, which missed maps with a short flag run: on Imperial Isle the
        spawns are about 4,300 from the stand and the estimate fell back to the bases (twice the real run). Needs 3+
        pickups in the cluster; otherwise the old rule, then the base."""
        m, out = self.m, {}
        tab = _spawn_table().get(m.o["meta"].get("map")) or {}
        sp = [x for x in tab.get("spawns", []) if x[2] >= _spawn_table_min()]
        if len(sp) == 2 and self.base.get(1) and self.base.get(2):
            for tm in (1, 2):
                own = min(sp, key=lambda x: d(x[:2], self.base[tm]))
                out[tm] = (float(own[0]), float(own[1]))
            if out[1] != out[2]: return out        # the map's measured spawns (benchmarks.py spawns)
            out = {}
        for tm in (1, 2):
            pts = []
            for t, typ, a in m.o.get("flags", []):
                if typ != "flag_picked_up" or m.team(a) != tm: continue
                q = m.snap(a, t)
                if not q: continue
                p = (q["x"], q["y"])
                if self.base.get(tm) and self.base.get(3 - tm) and d(p, self.base[tm]) < d(p, self.base[3 - tm]): pts.append(p)
            best = max(([q for q in pts if d(p, q) < self.SPAWN_CLUSTER_R] for p in pts), key=len, default=[])
            if len(best) >= 3:
                out[tm] = (statistics.median(p[0] for p in best), statistics.median(p[1] for p in best)); continue
            far = [p for p in pts if d(p, self.stand) > 6000]
            out[tm] = (statistics.median(p[0] for p in far), statistics.median(p[1] for p in far)) if far else self.base.get(tm)
        return out

    def _estimate(self):
        m, out = self.m, {}
        hits = collections.defaultdict(list)
        for r in m.o["ev"]:
            if r[1] in ("dm", "af") and isinstance(r[3], int) and r[3] < len(m.A) and m.A[r[3]].get("npc") in STATIC_NPCS \
                    and r[2] in m.PL:
                s = m.snap(r[2], r[0])
                if s: hits[r[3]].append(((s["x"], s["y"]), m.A[r[2]].get("p") in MELEE))
        for a, ag in enumerate(m.A):
            if ag.get("npc") not in STATIC_NPCS: continue
            h = hits.get(a, [])
            mel = [p for p, isml in h if isml]
            use, conf = (mel, "melee") if len(mel) >= 3 else ([p for p, _ in h], "ranged")
            pos = (statistics.median(p[0] for p in use), statistics.median(p[1] for p in use)) if use else None
            if conf == "ranged" and pos and ag.get("team") in self.base:   # ranged attackers stand off: pull toward own base
                b = self.base[ag["team"]]; pos = (pos[0] + (b[0] - pos[0]) * 0.25, pos[1] + (b[1] - pos[1]) * 0.25)
            out[a] = dict(kind=ag["npc"], team=ag.get("team"), pos=pos, n=len(use), conf=conf if use else "none")
        return out

    def _merge_store(self, save=False):
        """Fill NPCs with no samples from earlier matches on this map, and (with save=True, i.e. analyze.py --save-maps)
        add this match's estimates to data/maps/<map id>.json: side-agnostic absolute positions matched by kind and
        distance. A match already in the store is never added twice, so re-runs don't change the files."""
        path = os.path.join(REPO, "data", "maps", f"{self.map_id}.json")
        try: store = json.load(open(path))
        except (OSError, ValueError): store = {"map_id": self.map_id, "map": self.m.o["meta"]["map"], "npcs": []}
        mid = self.m.o["meta"]["id"]
        changed = False
        for a, v in self.npcs.items():
            if v["pos"] is None:
                near = [s for s in store["npcs"] if s["kind"] == v["kind"] and v["team"] in self.base
                        and d(tuple(s["pos"]), self.base[v["team"]]) < 6000]
                if near:
                    best = min(near, key=lambda s: d(tuple(s["pos"]), self.base[v["team"]]))
                    v.update(pos=tuple(best["pos"]), conf="map")
                continue
            if v["conf"] != "melee" or not save: continue
            match = [s for s in store["npcs"] if s["kind"] == v["kind"] and d(tuple(s["pos"]), v["pos"]) < 400]
            # a match is only ever added once (also when an earlier merge moved the stored position a little)
            if any(mid in x.get("matches", []) for x in store["npcs"] if x["kind"] == v["kind"] and d(tuple(x["pos"]), v["pos"]) < 1200): continue
            changed = True
            if match:
                s = match[0]; w = s["n"]
                s["pos"] = [round((s["pos"][0] * w + v["pos"][0] * v["n"]) / (w + v["n"])),
                            round((s["pos"][1] * w + v["pos"][1] * v["n"]) / (w + v["n"]))]
                s["n"] = w + v["n"]; s["matches"] = sorted(set(s.get("matches", [])) | {self.m.o["meta"]["id"]})
            else:
                store["npcs"].append({"kind": v["kind"], "pos": [round(v["pos"][0]), round(v["pos"][1])], "n": v["n"],
                                      "matches": [self.m.o["meta"]["id"]]})
        if changed:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            json.dump(store, open(path, "w"), indent=1)


_SPAWNS = None
def _spawn_table():
    """data/benchmarks/flag_spawns.json maps (benchmarks.py spawns)."""
    global _SPAWNS
    if _SPAWNS is None:
        import json, os
        from common import REPO
        try: _SPAWNS = json.load(open(os.path.join(REPO, "data", "benchmarks", "flag_spawns.json")))
        except (OSError, ValueError): _SPAWNS = {}
    return _SPAWNS.get("maps") or {}


def _spawn_table_min():
    return (_SPAWNS or {}).get("min_n", 8)


class GameState:
    def __init__(self, m, save_maps=False):
        self.m, self.geo = m, MapGeo(m, save_maps)
        self.end = int(m.o["meta"]["match_length_s"])
        self.teams = (1, 2)
        self.players = {tm: [a for a in m.PL if m.team(a) == tm] for tm in self.teams}
        self._deaths()
        self._flag()
        self._npc_deaths()
        self._dp()

    # ---- building blocks
    def _deaths(self):
        self.death_times = collections.defaultdict(list)
        for r in self.m.o["ev"]:
            if r[1] == "dt" and r[2] in self.m.PL: self.death_times[r[2]].append(r[0] / 10)

    def next_res(self, t):
        """Base res happens every 2 minutes of match clock."""
        return (int(t // RES_EVERY) + 1) * RES_EVERY

    def _flag(self):
        caps = [(t / 10, self.m.team(a)) for t, typ, a in self.m.o.get("flags", []) if typ == "flagstand_captured" and self.m.team(a)]
        self.caps = caps
        self.carries = [dict(c, s=c["s"] / 10, e=c["e"] / 10) for c in self.m.carries]

    def _npc_deaths(self):
        self.npc_dead = {}
        for r in self.m.o["ev"]:
            if r[1] == "dt" and isinstance(r[2], int) and r[2] < len(self.m.A) and self.m.A[r[2]].get("npc") in STATIC_NPCS:
                self.npc_dead.setdefault(r[2], r[0] / 10)

    def _dp(self):
        self.dp_ev = collections.defaultdict(list)          # agent -> [(t, net max HP %)]
        for r in self.m.o["ev"]:
            if r[1] == "mo" and r[2] in self.m.PL and r[5] is not None: self.dp_ev[r[2]].append((r[0] / 10, r[5]))

    # ---- queries
    def pos(self, a, t):
        s = self.m.snap(a, int(t * 10))
        return ((s["x"], s["y"]), s) if s else (None, None)

    def alive(self, a, t):
        _, s = self.pos(a, t); return self.m.alive(s)

    def morale(self, a, t):
        v = 0
        for tt, n in self.dp_ev.get(a, []):
            if tt <= t: v = n
        return v

    def zone(self, a, t):
        p, s = self.pos(a, t)
        if not p: return "?"
        if not self.m.alive(s): return "dead"
        tm, geo = self.m.team(a), self.geo
        if d(p, geo.pit.get(tm)) < PIT_R: return "own pit"
        if d(p, geo.pit.get(3 - tm)) < PIT_R: return "enemy pit"
        if d(p, geo.stand) < STAND_R: return "stand"
        if d(p, geo.base.get(tm)) < BASE_R: return "own base"
        if d(p, geo.base.get(3 - tm)) < BASE_R: return "enemy base"
        return "backside" if d(p, geo.base.get(tm)) < d(p, geo.base.get(3 - tm)) else "push side"

    def carrier(self, t):
        return [c["a"] for c in self.carries if c["s"] <= t <= c["e"]]

    def stand_owner(self, t):
        own, since = None, 0
        for ct, tm in self.caps:
            if ct <= t: own, since = tm, ct
        return own, since

    def groups(self, tm, t): return self.m.groups(tm, int(t * 10))

    def main_group(self, tm, t):
        key = (tm, int(t))
        cache = self.__dict__.setdefault("_mg", {})
        if key not in cache: cache[key] = self._main_group(tm, int(t))
        return cache[key]

    def _main_group(self, tm, t):
        gs = self.groups(tm, t)
        if not gs: return []
        monks = lambda g: sum(1 for a in g if self.m.A[a].get("p") == "Monk")
        return max(gs, key=lambda g: (len(g), monks(g)))

    def centroid(self, g, t):
        pts = [self.pos(a, t)[0] for a in g]; pts = [p for p in pts if p]
        return (statistics.mean(p[0] for p in pts), statistics.mean(p[1] for p in pts)) if pts else None

    def pit_npcs(self, tm, t):
        """Pit NPCs alive: e.g. 'K2 A2 B1' (knights, pit archers, Bodyguard)."""
        c = collections.Counter(v["kind"] for a, v in self.geo.npcs.items() if v["team"] == tm and v.get("pit")
                                and v["kind"] != "guild_lord" and self.npc_dead.get(a, 1e9) > t)
        return f"K{c['knight']} A{c['archer']} B{c['bodyguard']}"

    def at(self, t):
        """Everything known at second t."""
        out = {"t": t, "res_in": round(self.next_res(t) - t)}
        owner, since = self.stand_owner(t)
        held = t - since if owner else 0
        out["stand"] = {"owner": self.m.tag.get(owner), "held_s": round(held), "boost_in": round(120 - held % 120) if owner else None}
        out["carriers"] = [self.m.role(a) for a in self.carrier(t)]
        mains = {tm: self.main_group(tm, t) for tm in self.teams}
        for tm in self.teams:
            tag = self.m.tag[tm]
            zones = {self.m.roles[a]: self.zone(a, t) for a in self.players[tm]}
            dead = [a for a in self.players[tm] if zones[self.m.roles[a]] == "dead"]
            out[tag] = {
                "alive": len(self.players[tm]) - len(dead),
                "dead": [self.m.roles[a] for a in dead],
                "main": len(mains[tm]), "main_roles": [self.m.roles[a] for a in mains[tm]],
                "zones": zones,
                "morale": {self.m.roles[a]: self.morale(a, t) for a in self.players[tm] if self.morale(a, t)},
                "pit_npcs": self.pit_npcs(tm, t),
            }
        c1, c2 = (self.centroid(mains[tm], t) for tm in self.teams)
        out["mains_apart"] = round(d(c1, c2)) if c1 and c2 else None
        return out


def timeline(st, step=15):
    m = st.m
    t1, t2 = (m.tag[1], m.tag[2])
    for t in range(0, st.end + 1, step):
        s = st.at(t)
        row = [f"{m.f(t * 10):>5}", f"res {s['res_in']:3}s"]
        o = s["stand"]
        row.append(f"stand {o['owner'] or '-':5} {o['held_s']:3}s" + (f" boost in {o['boost_in']:3}s" if o['owner'] else " " * 13))
        for tag in (t1, t2):
            x = s[tag]
            away = [r for r, z in x["zones"].items() if r not in x["main_roles"] and z != "dead"]
            row.append(f"{tag}: {x['alive']} up, main {x['main']}, NPCs {x['pit_npcs']}"
                       + (f", away {','.join(f'{r}@{x['zones'][r]}' for r in away)}" if away else "")
                       + (f", dead {','.join(x['dead'])}" if x['dead'] else ""))
        if s["carriers"]: row.append("flag: " + ", ".join(s["carriers"]))
        print(" | ".join(row))


if __name__ == "__main__":
    m = Match.from_branch(sys.argv[1])
    st = GameState(m)
    print(m.o["meta"]["map"], "| pit from", {m.tag[tm]: next((v["conf"] for v in st.geo.npcs.values() if v["team"] == tm and v["kind"] == "guild_lord"), "?") for tm in (1, 2)})
    timeline(st, int(sys.argv[2]) if len(sys.argv) > 2 else 15)
