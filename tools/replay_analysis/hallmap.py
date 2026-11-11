"""The guild hall as Denning labelled it: named zones and walked distances (docs/REDESIGN.md step 2, items 2.1, 2.2).

Reads, never writes: data/maps/outline/<map id>.json (the walkable ground), data/maps/labels/<map id>.json (Denning's
points, areas and routes) and data/maps/hall_features.json. A hall with no labels gives None from Hall.get and every
caller keeps its old straight-line reading.

Zones (R-306): the zone of a point is the smallest labelled Pit, Base or Flag stand area containing it, cut to the
  walkable ground; outside all of them it is the backside or the push side, by which Guild Lord is the shorter walk.
  The smallest labelled area of any type at the point (a choke point, a bridge, lava...) is its "spot".
Sides: a label belongs to the side of the nearer Guild Lord; a team's side is the one whose res shrine its players
  start at.
Walked distance (R-316): the shortest way over the walkable ground in 100-unit cells (8 directions), with every
  labelled teleporter an edge of no length in its own direction (a two-way teleporter is two labels). Grid paths run a
  few percent long against a straight line; every distance in the engine now has the same bias.
Footmen (R-307, R-311): there is no footmen zone. A team is "at its footmen" when its players stand within the reach
  at which footmen actually hit players on that hall, measured from every replay around Denning's Footman labels
  (data/benchmarks/footmen_reach.json, `python3 hallmap.py reach`), while a footman of that side is alive.

Usage:  python3 hallmap.py numbers           the map numbers of every hall, old straight lines beside the walked ones
        python3 hallmap.py routes            labelled routes: drawn and walked length, and the grid's own shortest way
        python3 hallmap.py reach [--write]   measure the footmen reach per hall from the stored replays
In code: h = Hall.get(map_id); h.zone(p, side); h.walk(p, q); h.to(point)[cell]; h.numbers()."""
import collections, heapq, json, math, os, sys
from common import REPO

CELL = 100
MAPS = os.path.join(REPO, "data", "maps")
REACH_FILE = os.path.join(REPO, "data", "benchmarks", "footmen_reach.json")
TERRITORY = ("Pit", "Base", "Flag stand area")
HOP_END, HOP_MIN = 600, 1500      # a drawn route leg between two teleporter ends, this long, is a hop (audit_labels.py)
SNAP_RING = 6                     # cells searched around a point that is just off the walkable ground
REACH_PCT = 0.75                  # the share of footman hits on players that the reach covers (R-326)
REACH_MIN_HITS = 30               # fewer hits than this on a hall: the pooled reach of all halls is used


def cell(p): return (int(p[0] // CELL), int(p[1] // CELL))
def mid(c): return ((c[0] + 0.5) * CELL, (c[1] + 0.5) * CELL)


def in_poly(x, y, pts):
    ins = False
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: ins = not ins
    return ins


def _centre(pts): return (sum(q[0] for q in pts) / len(pts), sum(q[1] for q in pts) / len(pts))


class Hall:
    _halls = {}

    @classmethod
    def get(cls, map_id):
        k = str(map_id)
        if k not in cls._halls:
            try: cls._halls[k] = cls(k)
            except (OSError, ValueError, KeyError, IndexError): cls._halls[k] = None
        return cls._halls[k]

    def __init__(self, map_id):
        self.id = map_id
        o = json.load(open(os.path.join(MAPS, "outline", f"{map_id}.json")))
        lab = json.load(open(os.path.join(MAPS, "labels", f"{map_id}.json")))
        self.name, self.labels = o["map"], lab["labels"]
        try: self.features = json.load(open(os.path.join(MAPS, "hall_features.json")))["halls"].get(map_id, {})
        except (OSError, ValueError): self.features = {}
        self.cells = self._ground(o)
        L = self.labels
        pt = lambda typ: [tuple(l["pts"][0]) for l in L if l["kind"] == "point" and l["type"] == typ]
        lords = sorted(pt("Guild Lord"))
        if len(lords) != 2: raise ValueError("a labelled hall needs two Guild Lords")
        self.lord = {"A": lords[0], "B": lords[1]}
        self.stand = self._stand(pt("Flag stand"))
        one = lambda typ: {self.side(p): p for p in pt(typ)}
        self.res, self.spawn = one("Res shrine"), one("Flag spawn")
        self.npc = {s: collections.defaultdict(list) for s in "AB"}
        for typ in ("Bodyguard", "Knight", "Archer", "Footman"):
            for p in pt(typ): self.npc[self.side(p)][typ].append(p)
        self.footmen = {s: self.npc[s]["Footman"] for s in "AB"}
        self.areas = []
        for l in L:
            if l["kind"] != "area" or len(l["pts"]) < 3: continue
            pts = [tuple(q) for q in l["pts"]]
            xs, ys = [q[0] for q in pts], [q[1] for q in pts]
            cs = {(ix, iy) for ix in range(int(min(xs) // CELL), int(max(xs) // CELL) + 1)
                  for iy in range(int(min(ys) // CELL), int(max(ys) // CELL) + 1)
                  if (ix, iy) in self.cells and in_poly((ix + 0.5) * CELL, (iy + 0.5) * CELL, pts)}
            if cs: self.areas.append({"id": l["id"], "type": l["type"], "name": l.get("name") or "", "side": self.side(_centre(pts)),
                                      "pts": pts, "cells": cs})
        self.areas.sort(key=lambda a: len(a["cells"]))               # smallest first: the first hit names the place
        self._zone, self._spot = {}, {}
        for i, a in enumerate(self.areas):
            for c in a["cells"]:
                self._spot.setdefault(c, i)
                if a["type"] in TERRITORY: self._zone.setdefault(c, i)
        self.hops = self._teleporters()
        self._fwd, self._back = collections.defaultdict(list), collections.defaultdict(list)
        for a, b in self.hops:
            self._fwd[a].append(b); self._back[b].append(a)
        self._fields, self._snap = {}, {}
        self.routes = self._routes()
        # doors: where each labelled door route leaves its base; footmen by the door they stand nearer (front or back footies)
        self.doors = {s: {"front": [], "back": []} for s in "AB"}
        base = {s: set().union(*[a["cells"] for a in self.areas if a["type"] in ("Base", "Pit") and a["side"] == s] or [set()]) for s in "AB"}
        for r in self.routes:
            k = {"Front door": "front", "Back door": "back"}.get(r["type"])
            if not k: continue
            pt = r["pts"][-1]
            for a, b in zip(r["pts"], r["pts"][1:]):
                n = max(int(math.dist(a, b) // 50), 1)
                out = next(((a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n + 1)
                            if cell((a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n)) not in base[r["side"]]), None)
                if out: pt = out; break
            self.doors[r["side"]][k].append(pt)
        self.footies = {s: {"front": [], "back": []} for s in "AB"}
        for s in "AB":
            for f in self.footmen[s]:
                near = lambda k: min((math.dist(f, q) for q in self.doors[s][k]), default=1e9)
                self.footies[s]["front" if near("front") <= near("back") else "back"].append(f)

    def _stand(self, pts):
        """The flag stand that gives morale: the Flag stand label inside (or nearest) the Flag stand area (Isle of
        Meditation's second label is the obelisk, R-308); with no label (Warrior's Isle) the stand the replays show
        (data/maps/auto), else the middle of the area."""
        area = next((_centre(l["pts"]) for l in self.labels if l["kind"] == "area" and l["type"] == "Flag stand area"), None)
        if pts: return min(pts, key=lambda p: math.dist(p, area)) if area else pts[0]
        try: return tuple(json.load(open(os.path.join(MAPS, "auto", f"{self.id}.json")))["stand"])
        except (OSError, ValueError, KeyError): pass
        if area: return area
        raise ValueError("no flag stand")

    # ---- ground, sides, teleporters
    @staticmethod
    def _ground(o):
        cells = set()
        if o.get("source") == "gvg.report":
            for xtl, xtr, yt, xbl, xbr, yb in o["traps"]:
                lo, hi = min(yt, yb), max(yt, yb)
                if hi <= lo: continue
                for iy in range(int(lo // CELL), int(hi // CELL) + 1):
                    y = min(max((iy + 0.5) * CELL, lo), hi)
                    f = (y - yb) / (yt - yb); xl = xbl + (xtl - xbl) * f; xr = xbr + (xtr - xbr) * f
                    a, b = min(xl, xr), max(xl, xr)
                    for ix in range(int(a // CELL), int(b // CELL) + 1):
                        if a <= (ix + 0.5) * CELL <= b or b - a < CELL: cells.add((ix, iy))
        else:
            for iy, runs in o["rows"].items():
                for a, b in runs:
                    for ix in range(a, b + 1): cells.add((ix, int(iy)))
        return cells

    def side(self, p):
        return "A" if math.dist(p, self.lord["A"]) <= math.dist(p, self.lord["B"]) else "B"

    def team_sides(self, base):
        """{team: side} from where each team's players start (replaylib's base: the median first position)."""
        if base.get(1) is None or base.get(2) is None: return {}
        a = min((1, 2), key=lambda tm: math.dist(base[tm], self.res.get("A") or self.lord["A"]) - math.dist(base[tm], self.res.get("B") or self.lord["B"]))
        return {a: "A", 3 - a: "B"}

    def _teleporters(self):
        """Directed hops (cell in, cell out). A route label of a Teleporter type runs from its first point to its
        last. Teleporter points (Isle of Solitude) pair up by nearness; the way in is the end nearer a Guild Lord
        (R-309: in beside the Lord, out on the field)."""
        hops = []
        for l in self.labels:
            if l["kind"] == "route" and l["type"].startswith("Teleporter"):
                hops.append((self.snap(l["pts"][0]), self.snap(l["pts"][-1])))
        pts = [tuple(l["pts"][0]) for l in self.labels if l["kind"] == "point" and l["type"].startswith("Teleporter")]
        while len(pts) >= 2:
            p = pts.pop(0); q = min(pts, key=lambda x: math.dist(p, x)); pts.remove(q)
            near = lambda x: min(math.dist(x, self.lord["A"]), math.dist(x, self.lord["B"]))
            a, b = (p, q) if near(p) <= near(q) else (q, p)
            hops.append((self.snap(a), self.snap(b)))
        return hops

    def tele_ends(self):
        return [mid(c) for h in self.hops for c in h]

    # ---- places
    def snap(self, p):
        """The walkable cell at or nearest a point."""
        c = cell(p)
        if c in self.cells: return c
        if c not in self._snap:
            best = None
            for r in range(1, SNAP_RING + 1):
                ring = [(c[0] + dx, c[1] + dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1)
                        if max(abs(dx), abs(dy)) == r and (c[0] + dx, c[1] + dy) in self.cells]
                if ring: best = min(ring, key=lambda q: (q[0] - c[0]) ** 2 + (q[1] - c[1]) ** 2); break
            self._snap[c] = best or min(self.cells, key=lambda q: (q[0] - c[0]) ** 2 + (q[1] - c[1]) ** 2)
        return self._snap[c]

    def area_at(self, p, territory=False):
        i = (self._zone if territory else self._spot).get(self.snap(p))
        return None if i is None else self.areas[i]

    def zone(self, p, side):
        """own pit, enemy pit, stand, own base, enemy base, backside or push side, for a player of `side` (R-306)."""
        a = self.area_at(p, True)
        if a:
            if a["type"] == "Flag stand area": return "stand"
            return ("own " if a["side"] == side else "enemy ") + a["type"].lower()
        c = self.snap(p); other = "B" if side == "A" else "A"
        return "backside" if self.to(self.lord[side]).get(c, 1e9) <= self.to(self.lord[other]).get(c, 1e9) else "push side"

    def place(self, p):
        """A point in Denning's words (his golden notes): (kind, side). kind is pit, front door, back door, front
        footies, back footies, stand, base, greater stand or field; side is whose ground it is (None at the stand).
        Smaller and more specific places first."""
        from common import DOOR_R, GREATER_STAND_WALK
        a = self.area_at(p, True)
        if a and a["type"] == "Pit": return "pit", a["side"]
        if a and a["type"] == "Flag stand area": return "stand", None
        for s in "AB":
            for k in ("front", "back"):
                if any(math.dist(p, q) <= DOOR_R for q in self.doors[s][k]): return k + " door", s
        r = self.reach()
        if r:
            for s in "AB":
                for k in ("front", "back"):
                    if any(math.dist(p, f) <= r for f in self.footies[s][k]): return k + " footies", s
        if a and a["type"] == "Base": return "base", a["side"]
        c = self.snap(p)
        if self.to(self.stand).get(c, 1e9) <= GREATER_STAND_WALK: return "greater stand", None
        return "field", ("A" if self.to(self.lord["A"]).get(c, 1e9) <= self.to(self.lord["B"]).get(c, 1e9) else "B")

    def spot(self, p):
        """The smallest labelled area of any type at the point, in words ("Choke point", "Bridge", "Lava", a name)."""
        a = self.area_at(p)
        return None if not a else (a["name"] or a["type"])

    # ---- walked distance
    def _field(self, start, graph):
        s = self.snap(start); dist = {s: 0.0}; pq = [(0.0, s)]
        while pq:
            d, c = heapq.heappop(pq)
            if d > dist[c]: continue
            for n in graph.get(c, ()):                                # a teleporter: no length
                if d < dist.get(n, 1e18): dist[n] = d; heapq.heappush(pq, (d, n))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if not dx and not dy: continue
                    n = (c[0] + dx, c[1] + dy)
                    if n not in self.cells: continue
                    nd = d + CELL * (1.4142 if dx and dy else 1)
                    if nd < dist.get(n, 1e18): dist[n] = nd; heapq.heappush(pq, (nd, n))
        return dist

    def to(self, point):
        """Walked distance from every cell to `point` (teleporters taken in their own direction)."""
        k = ("to", self.snap(point))
        if k not in self._fields: self._fields[k] = self._field(point, self._back)
        return self._fields[k]

    def frm(self, point):
        """Walked distance from `point` to every cell."""
        k = ("from", self.snap(point))
        if k not in self._fields: self._fields[k] = self._field(point, self._fwd)
        return self._fields[k]

    def walk(self, p, q):
        """Walked distance from p to q; None when q cannot be reached."""
        v = self.to(q).get(self.snap(p))          # fields are kept by their target: the anchors are few, the players many
        return None if v is None else round(v)

    # ---- routes and map numbers
    def _routes(self):
        ends = self.tele_ends(); out = []
        for l in self.labels:
            if l["kind"] != "route" or l["type"].startswith("Teleporter") or len(l["pts"]) < 2: continue
            pts = [tuple(q) for q in l["pts"]]
            drawn = hop = 0.0; n = 0
            for a, b in zip(pts, pts[1:]):
                leg = math.dist(a, b); drawn += leg
                if leg >= HOP_MIN and ends and min(math.dist(a, e) for e in ends) <= HOP_END and min(math.dist(b, e) for e in ends) <= HOP_END:
                    hop += leg; n += 1
            typ = l["type"] if l["type"] != "Other" else (l.get("name") or "Other")
            # a flag run starts at its side's spawn; doors and collapse routes start inside the base (drawn outward)
            out.append({"id": l["id"], "type": typ, "side": self.side(pts[0]), "pts": pts, "drawn": round(drawn),
                        "walked": round(drawn - hop), "hops": n})
        return out

    def route_followed(self, track, typ, side, within=600):
        """Which labelled route of a type a walked track followed: the one whose line the track stayed nearest
        (mean distance of the track's points to the route), None when no route is within `within` on average."""
        best = None
        for r in self.routes:
            if r["type"] != typ or r["side"] != side: continue
            dd = [min(_seg_dist(p, a, b) for a, b in zip(r["pts"], r["pts"][1:])) for p in track]
            if dd:
                v = sum(dd) / len(dd)
                if v <= within and (best is None or v < best[0]): best = (v, r)
        return best[1] if best else None

    def numbers(self):
        """The hall in numbers, for pooling halls by their features (R-302). Averages of the two sides."""
        avg = lambda xs: (round(sum(xs) / len(xs)) if xs else None)
        both = [s for s in "AB"]
        w = lambda p, q: self.walk(p, q) if p and q else None
        ok = lambda xs: [x for x in xs if x is not None]
        rt = lambda typ: ok([min((r["walked"] for r in self.routes if r["type"] == typ and r["side"] == s), default=None) for s in both])
        n = {"flag_run": avg(ok([w(self.spawn.get(s), self.stand) for s in both])),
             "pit_to_stand": avg(ok([w(self.lord[s], self.stand) for s in both])),
             "bases_apart": avg(ok([w(self.res.get("A"), self.res.get("B")), w(self.res.get("B"), self.res.get("A"))])),
             "way_home": avg(ok([w(self.stand, self.lord[s]) for s in both])),
             "front_door": avg(rt("Front door")), "back_door": avg(rt("Back door")),
             "footmen": avg([len(self.footmen[s]) for s in both]), "teleporters": len(self.hops),
             "flag_routes": max(sum(1 for r in self.routes if r["type"] == "Flag run" and r["side"] == s) for s in both)}
        return n

    # ---- footmen
    def reach(self):
        global _REACH
        if _REACH is None:
            try: _REACH = json.load(open(REACH_FILE))
            except (OSError, ValueError): _REACH = {}
        h = (_REACH.get("halls") or {}).get(self.id) or {}
        return h.get("reach") if h.get("hits", 0) >= REACH_MIN_HITS else _REACH.get("pooled")

    def at_footmen(self, pts, side):
        """The share of these points within the footmen's reach of a labelled Footman of `side`; None on a hall
        without footmen (R-311) or before the reach is measured."""
        F, r = self.footmen[side], self.reach()
        if not F or not r or not pts: return None
        return sum(1 for p in pts if min(math.dist(p, f) for f in F) <= r) / len(pts)


_REACH = None


def _seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = dx * dx + dy * dy or 1
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L))
    return math.dist(p, (a[0] + t * dx, a[1] + t * dy))


def hall_ids():
    return sorted(f[:-5] for f in os.listdir(os.path.join(MAPS, "labels")) if f.endswith(".json"))


def measure_reach(write=False):
    """How far from Denning's Footman labels players stand when a footman hits them, per hall, from every stored
    replay. The reach is the distance covering REACH_PCT of those hits."""
    import gzip, subprocess
    idx = json.loads(subprocess.check_output(["git", "-C", REPO, "show", "origin/replays:index.json"]))["matches"]
    from replaylib import Match
    hits = collections.defaultdict(list)
    for rid, info in idx.items():
        raw = subprocess.run(["git", "-C", REPO, "cat-file", "-p", "origin/replays:" + info["file"]], capture_output=True).stdout
        try: m = Match(json.loads(gzip.decompress(raw)))
        except Exception: continue
        h = Hall.get(m.o["meta"].get("map_id"))
        if not h or not (h.footmen["A"] or h.footmen["B"]): continue
        sides = h.team_sides(m.base)
        for r in m.o["ev"]:
            if r[1] != "dm" or not isinstance(r[2], int) or r[2] >= len(m.A) or m.A[r[2]].get("npc") != "footman" or r[3] not in m.PL: continue
            s = m.snap(r[3], r[0]); F = h.footmen.get(sides.get(m.A[r[2]].get("team")))
            if s and F: hits[h.id].append(min(math.dist((s["x"], s["y"]), f) for f in F))
    q = lambda xs: round(sorted(xs)[min(int(len(xs) * REACH_PCT), len(xs) - 1)]) if xs else None
    allh = [x for v in hits.values() for x in v]
    out = {"about": f"Distance from a labelled Footman within which {round(REACH_PCT * 100)}% of footman hits on players land, per hall "
                    "(hallmap.py reach). A team is at its footmen inside this distance while a footman is alive (R-307).",
           "pct": REACH_PCT, "pooled": q(allh),
           "halls": {k: {"map": Hall.get(k).name, "hits": len(v), "reach": q(v), "median": round(sorted(v)[len(v) // 2])}
                     for k, v in sorted(hits.items())}}
    if write: json.dump(out, open(REACH_FILE, "w"), indent=1)
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "numbers"
    if cmd == "reach":
        print(json.dumps(measure_reach("--write" in sys.argv), indent=1))
    for k in hall_ids() if cmd in ("numbers", "routes") else []:
        h = Hall.get(k)
        if not h: print(k, "not readable"); continue
        if cmd == "numbers":
            sl = {"flag_run": round(sum(math.dist(h.spawn[s], h.stand) for s in "AB" if s in h.spawn) / max(len(h.spawn), 1)),
                  "pit_to_stand": round(sum(math.dist(h.lord[s], h.stand) for s in "AB") / 2),
                  "bases_apart": round(math.dist(h.res["A"], h.res["B"])) if len(h.res) == 2 else None}
            n = h.numbers()
            print(f"{h.name} ({k}): " + ", ".join(f"{a} {sl[a]} -> {n[a]}" for a in sl) + " | "
                  + ", ".join(f"{a} {n[a]}" for a in n if a not in sl) + f" | areas {len(h.areas)}, cells {len(h.cells)}")
        else:
            for r in h.routes:
                g = h.walk(r["pts"][0], r["pts"][-1])
                print(f"{h.name}: {r['type']} ({r['side']}) drawn {r['drawn']}, walked {r['walked']}, hops {r['hops']}, grid shortest {g}")
