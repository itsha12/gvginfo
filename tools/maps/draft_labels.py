"""Draft map labels from the stored replays, for Denning to accept, adjust or remove on the Maps page.

What it drafts, and from what (all from the replays and the outline; nothing here reads Denning's labels):
  Flag stand (point and area)   where captures happen, and where players stand while near the stand
  Flag spawn, Res shrine        where new flags are picked up; where dead players reappear on the res timer
  Pit                           the ground around the Guild Lord that the pit NPCs occupy
  Base                          the ground still joined to the Lord with both drafted doors shut at their narrowest;
                                failing that, the half of the walk to the stand that lies nearer the Lord (rough)
  Flag run                      the path carriers actually walked from the spawn to the stand
  Front door, Back door         the two busiest ways players cross out of (or into) each base
  Teleporter                    places players jump from and to, again and again, with the direction
Not drafted: choke points, archers, knights, footmen, gates, hazards (Denning labels those).

Output: data/maps/draft/<map id>.json, the same shape as a labels file, each label with "how" (the evidence).
Usage:  python3 tools/maps/draft_labels.py [map id ...]          write drafts (all halls by default)
        python3 tools/maps/draft_labels.py --score 541 358 542   compare drafts with Denning's labels on those halls
        python3 tools/maps/draft_labels.py 541 "--only=Flag spawn,Flag stand"   write only those types (for a hall he
                                                                 has already labelled, where the audit found a type missing)
Kept outside tools/replay_analysis on purpose (every .py there is part of the engine's cache key).
"""
import bisect, collections, gzip, heapq, json, math, os, statistics, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAPS = os.path.join(REPO, "data", "maps")
CELL = 100
STATIC = ("guild_lord", "bodyguard", "knight", "archer", "footman")
MELEE = {"Warrior", "Dervish", "Assassin"}
DOOR_SHARE = 0.36       # crossings are read as doors this share of the way from the Lord to the stand, by foot (2,500 to 4,200 units)
STAND_SHARE = 0.75      # share of time-near-the-stand the stand area must hold
BASE_SHARE = 0.5        # an open-sided base: this share of the walk from the Lord to the stand (0.45 to 0.55 read alike on the three halls scored)
RES_EVERY = 1200        # tenths of a second between base resurrections


def blob(path):
    return subprocess.run(["git", "-C", REPO, "cat-file", "-p", "origin/replays:" + path], capture_output=True, check=True).stdout


def cell(p): return (int(p[0] // CELL), int(p[1] // CELL))
def mid(c): return ((c[0] + 0.5) * CELL, (c[1] + 0.5) * CELL)
def med(pts): return [round(statistics.median(p[0] for p in pts)), round(statistics.median(p[1] for p in pts))]


def clusters(pts, radius):
    left, out = list(pts), []
    while left:
        best = max(left, key=lambda p: sum(1 for q in left if math.dist(p[:2], q[:2]) < radius))
        mem = [q for q in left if math.dist(best[:2], q[:2]) < radius]
        out.append(mem); left = [q for q in left if q not in mem]
    return out


class Land:
    """The walkable ground of a hall as 100-unit cells, with path distances over it."""
    def __init__(self, mid_):
        o = json.load(open(os.path.join(MAPS, "outline", f"{mid_}.json")))
        self.cells = set()
        if o["source"] == "gvg.report":
            for xtl, xtr, yt, xbl, xbr, yb in o["traps"]:
                lo, hi = min(yt, yb), max(yt, yb)
                if hi <= lo: continue
                for iy in range(int(lo // CELL), int(hi // CELL) + 1):
                    y = min(max((iy + 0.5) * CELL, lo), hi)
                    f = (y - yb) / (yt - yb); xl = xbl + (xtl - xbl) * f; xr = xbr + (xtr - xbr) * f
                    a, b = min(xl, xr), max(xl, xr)
                    for ix in range(int(a // CELL), int(b // CELL) + 1):
                        if a <= (ix + 0.5) * CELL <= b or b - a < CELL: self.cells.add((ix, iy))
        else:
            for iy, runs in o["rows"].items():
                for a, b in runs:
                    for ix in range(a, b + 1): self.cells.add((ix, int(iy)))
        self.name = o["map"]

    def where(self, p):
        """A point's place on the map in words, as the Maps page draws it (game y runs up the screen)."""
        xs = [c[0] for c in self.cells]; ys = [c[1] for c in self.cells]
        fx = (p[0] / CELL - min(xs)) / max(max(xs) - min(xs), 1); fy = (p[1] / CELL - min(ys)) / max(max(ys) - min(ys), 1)
        v = "top" if fy > 0.6 else "bottom" if fy < 0.4 else ""; h = "left" if fx < 0.4 else "right" if fx > 0.6 else ""
        return (v + " " + h).strip() or "middle"

    def snap(self, p):
        """The walkable cell at or nearest a point."""
        c = cell(p)
        if c in self.cells: return c
        return min(self.cells, key=lambda q: (q[0] - c[0]) ** 2 + (q[1] - c[1]) ** 2)

    def field(self, start, blocked=()):
        """Path distance in units from a point to every walkable cell (8 directions)."""
        s = self.snap(start); dist = {s: 0.0}; pq = [(0.0, s)]; blocked = set(blocked)
        while pq:
            d, c = heapq.heappop(pq)
            if d > dist[c]: continue
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if not dx and not dy: continue
                    n = (c[0] + dx, c[1] + dy)
                    if n not in self.cells or n in blocked: continue
                    nd = d + CELL * (1.4142 if dx and dy else 1)
                    if nd < dist.get(n, 1e18): dist[n] = nd; heapq.heappush(pq, (nd, n))
        return dist


def clearance(land):
    """For every walkable cell, how many cells to the nearest wall (how wide the ground is there)."""
    out = {}; q = collections.deque()
    for c in land.cells:
        if any((c[0] + dx, c[1] + dy) not in land.cells for dx in (-1, 0, 1) for dy in (-1, 0, 1)): out[c] = 1; q.append(c)
    while q:
        c = q.popleft()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                n = (c[0] + dx, c[1] + dy)
                if n in land.cells and n not in out: out[n] = out[c] + 1; q.append(n)
    return out


def padded_hull(points, pad):
    return hull([(x + dx, y + dy) for x, y in points for dx in (-pad, pad) for dy in (-pad, pad)])


def hull(points):
    pts = sorted(set(map(tuple, points)))
    if len(pts) < 3: return [list(p) for p in pts]
    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2 and (h[-1][0] - h[-2][0]) * (p[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0]) <= 0: h.pop()
            h.append(p)
        return h
    lo, up = half(pts), half(reversed(pts))
    return [[round(x), round(y)] for x, y in lo[:-1] + up[:-1]]


def cells_hull(cs):
    """A tidy outline around a set of cells: the hull of their corners, thinned to at most 14 points."""
    corners = [(c[0] * CELL + dx, c[1] * CELL + dy) for c in cs for dx in (0, CELL) for dy in (0, CELL)]
    h = hull(corners)
    while len(h) > 14:      # drop the corner that changes the outline least
        def lost(i): a, b, c = h[i - 1], h[i], h[(i + 1) % len(h)]; return abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
        h.pop(min(range(len(h)), key=lost))
    return h


def in_poly(x, y, pts):
    c = False
    for i in range(len(pts)):
        x1, y1 = pts[i]; x2, y2 = pts[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c


def poly_cells(land, pts):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return {(ix, iy) for ix in range(int(min(xs) // CELL), int(max(xs) // CELL) + 1) for iy in range(int(min(ys) // CELL), int(max(ys) // CELL) + 1)
            if (ix, iy) in land.cells and in_poly(*mid((ix, iy)), pts)}


def resample(path, n=40):
    d = [0.0]
    for a, b in zip(path, path[1:]): d.append(d[-1] + math.dist(a, b))
    if d[-1] == 0: return [path[0]] * n
    out = []
    for k in range(n):
        t = d[-1] * k / (n - 1); i = min(bisect.bisect_right(d, t) - 1, len(path) - 2)
        f = (t - d[i]) / ((d[i + 1] - d[i]) or 1)
        out.append((path[i][0] + (path[i + 1][0] - path[i][0]) * f, path[i][1] + (path[i + 1][1] - path[i][1]) * f))
    return out


def medoid(paths):
    """The real path most like all the others (so the draft is a way somebody actually walked)."""
    R = [resample(p) for p in paths[:120]]
    cost = lambda a: sum(sum(math.dist(p, q) for p, q in zip(a, b)) for b in R)
    return min(R, key=cost)


def simplify(path, tol=100):
    if len(path) < 3: return [[round(p[0]), round(p[1])] for p in path]
    a, b = path[0], path[-1]; L = math.dist(a, b) or 1
    i, far = max(((k, abs((b[0] - a[0]) * (a[1] - p[1]) - (a[0] - p[0]) * (b[1] - a[1])) / L) for k, p in enumerate(path[1:-1], 1)), key=lambda kv: kv[1])
    if far <= tol: return [[round(a[0]), round(a[1])], [round(b[0]), round(b[1])]]
    return simplify(path[:i + 1], tol)[:-1] + simplify(path[i:], tol)


def path_len(p): return sum(math.dist(a, b) for a, b in zip(p, p[1:]))


def snap_at(T, t):
    i = min(max(bisect.bisect_left(T["t"], t), 0), len(T["t"]) - 1)
    if i > 0 and abs(T["t"][i - 1] - t) < abs(T["t"][i] - t): i -= 1
    return (T["x"][i], T["y"][i]) if abs(T["t"][i] - t) <= 20 else None


def read_hall(mid_, land, limit=None):
    """Everything the drafts need from the hall's replays, pooled."""
    idx = json.loads(blob("index.json"))
    files = [v["file"] for v in idx["matches"].values() if v.get("file") and v.get("map") == land.name][:limit]
    H = dict(n=len(files), caps=[], pickups=[], lord_hits=collections.defaultdict(list), npc=collections.defaultdict(list), runs=[], tracks=[],
             respawn=[], jumps=[], near_stand=collections.Counter())
    for f in files:
        o = json.loads(gzip.decompress(blob(f)))
        A, TR = o["agents"], o["tracks"]
        players = [i for i, a in enumerate(A) if a.get("player") and str(i) in TR]
        open_c = {}
        for t, typ, a, *_ in o.get("flags", []):
            if not isinstance(a, int) or str(a) not in TR: continue
            p = snap_at(TR[str(a)], t)
            if typ == "flag_picked_up":
                if p: H["pickups"].append(p); open_c[a] = t
            elif typ == "flag_dropped": open_c.pop(a, None)
            elif typ == "flagstand_captured":
                if p: H["caps"].append(p)
                if a in open_c:
                    T = TR[str(a)]; t0 = open_c.pop(a)
                    seg = [(T["x"][i], T["y"][i]) for i in range(len(T["t"])) if t0 <= T["t"][i] <= t and T["st"][i] != "d"]
                    if len(seg) >= 8 and t - t0 < 1500: H["runs"].append(seg)
        hits = collections.defaultdict(list)
        for r in o["ev"]:
            if r[1] in ("dm", "af") and isinstance(r[3], int) and r[3] < len(A) and A[r[3]].get("npc") in STATIC and r[2] in players:
                p = snap_at(TR[str(r[2])], r[0])
                if p: hits[r[3]].append((p, A[r[2]].get("p") in MELEE))
        for a, h in hits.items():
            mel = [p for p, m in h if m]; use = mel if len(mel) >= 3 else [p for p, _ in h]
            if len(use) >= 3: H["npc"][A[a]["npc"]].append((*med(use), len(mel) >= 3))
        for a in players:
            T = TR[str(a)]; ts, xs, ys, st = T["t"], T["x"], T["y"], T["st"]
            seg = []
            for i in range(len(ts)):
                if st[i] == "d":
                    if len(seg) > 5: H["tracks"].append(seg)
                    seg = []; continue
                if i and st[i - 1] == "d" and ts[i] > 0 and (ts[i] % RES_EVERY) <= 40: H["respawn"].append((xs[i], ys[i], f, ts[i] // RES_EVERY))
                if i and st[i - 1] != "d" and ts[i] - ts[i - 1] <= 15:
                    d = math.hypot(xs[i] - xs[i - 1], ys[i] - ys[i - 1])
                    if d > 1300:                                        # a jump: a teleporter, or a Shadow Step
                        H["jumps"].append(((xs[i - 1], ys[i - 1]), (xs[i], ys[i]), f))
                        if len(seg) > 5: H["tracks"].append(seg)
                        seg = []
                seg.append((ts[i], xs[i], ys[i]))
            if len(seg) > 5: H["tracks"].append(seg)
    return H


def pooled(mid_, land, limit=None):
    """read_hall, kept between runs when DRAFT_CACHE names a folder (reading a hall's replays takes about 25 s)."""
    d = os.environ.get("DRAFT_CACHE")
    if not d: return read_hall(mid_, land, limit)
    import pickle
    f = os.path.join(d, f"hall_{mid_}.pkl")
    if os.path.exists(f): return pickle.load(open(f, "rb"))
    H = read_hall(mid_, land, limit); H["npc"] = dict(H["npc"]); H.pop("lord_hits", None); H.pop("near_stand", None)
    pickle.dump(H, open(f, "wb")); return H


def draft(mid_, limit=None):
    land = Land(mid_); H = pooled(mid_, land, limit)
    L = []; note = []
    seen_ids = collections.Counter()
    def add(kind, typ, pts, how, name="", key=None):
        # ids stay the same from one run to the next (sides are in a fixed order, a teleporter is keyed by where it starts),
        # so a draft Denning accepted or removed stays that way when the drafts are rebuilt with more replays
        slug = typ.lower().replace(" (one way)", "").replace(" ", "-")
        if key is None: key = seen_ids[slug]; seen_ids[slug] += 1
        L.append({"id": f"{slug}-{key}", "kind": kind, "type": typ, "name": name, "note": "", "pts": pts, "how": how})
    if not H["caps"]: return {"map_id": mid_, "map": land.name, "replays": H["n"], "labels": [], "notes": ["no captures in the stored replays: nothing drafted"]}
    stand = med(clusters(H["caps"], 500)[0])
    add("point", "Flag stand", [stand], f"{len(H['caps'])} captures in {H['n']} replays")
    # the two Lords: where melee attackers stood when they hit a Guild Lord
    lords = sorted(med(m) for m in clusters(H["npc"].get("guild_lord", []), 600)[:2])      # fixed order: lower x first
    if len(lords) < 2: note.append("fewer than two Guild Lords located: pits, bases and doors need more replays")
    D = [land.field(p) for p in lords]; DS = land.field(stand)
    side = lambda p: min(range(len(lords)), key=lambda i: D[i].get(land.snap(p), 1e18)) if lords else 0
    # flag spawns: the densest pickup cluster on each side, away from the stand
    spawns = {}
    for m in clusters(H["pickups"], 300):
        c = med(m)
        if len(m) >= 3 and math.dist(c, stand) > 1500 and lords and side(c) not in spawns: spawns[side(c)] = (c, len(m))
    for s, (c, n) in sorted(spawns.items()): add("point", "Flag spawn", [c], f"{n} pickups here")
    # res shrines: where dead players came back on the two-minute timer
    shrine = {}
    for s in range(len(lords)):
        # a base res brings back everyone who is dead together: keep timed returns that landed beside another one
        waves = collections.defaultdict(list)
        for p in H["respawn"]:
            if side(p) == s: waves[(p[2], p[3])].append(p)
        pts = [p for w in waves.values() for p in w if any(q is not p and math.dist(p[:2], q[:2]) < 500 for q in w)]
        pts = pts if len(pts) >= 6 else [p for w in waves.values() for p in w]
        if len(pts) >= 3:
            m = clusters(pts, 400)[0]
            if len(m) >= 3:
                shrine[s] = med(m)
                add("point", "Res shrine", [shrine[s]], f"{len(m)} of {len(pts)} resurrections on the two-minute timer landed here")
    # flag stand area: the cells that hold most of the time players spend within reach of the stand
    near = collections.Counter()
    for seg in H["tracks"]:
        for _, x, y in seg[::3]:
            c = cell((x, y))
            if DS.get(c, 1e18) <= 2600: near[c] += 1
    tot = sum(near.values()); acc = 0; keep = set()
    for c, n in sorted(near.items(), key=lambda kv: DS[kv[0]]):       # grow outward from the stand until the share is held
        keep.add(c); acc += n
        if acc >= STAND_SHARE * tot: break
    if len(keep) >= 6: add("area", "Flag stand area", cells_hull(keep), f"holds {STAND_SHARE:.0%} of the time players spent within 2,600 units of the stand")
    CL = clearance(land)
    for s, lord in enumerate(lords):
        mine = lambda kind, melee_only=False: [p for p in H["npc"].get(kind, []) if side(p) == s and (p[2] or not melee_only)]
        seen = lambda kind: [med(m) for m in clusters(mine(kind), 500) if len(m) >= max(2, H["n"] // 12)]
        # pit: the Guild Lord, the Bodyguard, the knights and the archers standing with them, as attackers found them
        core = [lord] + [p for k in ("bodyguard", "knight") for p in seen(k) if math.dist(p, lord) < 1800] + [p for p in seen("archer") if math.dist(p, lord) < 1300]
        add("area", "Pit", padded_hull(core, 380), f"around the Guild Lord and the {len(core) - 1} pit NPC positions attackers found within reach of him")
        # flag run: the carrier path most like the others, spawn to stand
        run = None
        if s in spawns:
            runs = [r for r in H["runs"] if math.dist(r[0], spawns[s][0]) < 700 and math.dist(r[-1], stand) < 700]
            if len(runs) >= 3:
                run = medoid(runs); add("route", "Flag run", simplify(run), f"the most typical of {len(runs)} runs from this spawn to the stand")
            else: note.append(f"the {land.where(lord)} base: too few complete flag runs in the replays to draft its flag run")
        # doors: where players cross a ring some way out from the Lord, in either direction; each crossing keeps the walk
        # from the edge of the pit to well past the ring
        ring = min(max(DOOR_SHARE * D[s].get(land.snap(stand), 9000), 2500), 4200); near, far = 1300, ring + 2600
        cross = []
        for seg in H["tracks"]:
            d = [D[s].get(cell((x, y))) for _, x, y in seg]
            for i in range(1, len(seg)):
                if d[i] is None or d[i - 1] is None or (d[i - 1] - ring) * (d[i] - ring) > 0 or d[i] == d[i - 1]: continue
                j0 = i; j1 = i
                while j0 > 0 and d[j0] is not None and near < d[j0] < far and i - j0 < 90: j0 -= 1
                while j1 < len(seg) - 1 and d[j1] is not None and near < d[j1] < far and j1 - i < 90: j1 += 1
                if d[j0] is None or d[j1] is None: continue
                whole = min(d[j0], d[j1]) <= near + 150 and max(d[j0], d[j1]) >= far - 150       # walked the full stretch
                path = [(x, y) for _, x, y in seg[j0:j1 + 1]]
                if len(path) >= 6 and path_len(path) > 1500:
                    if d[j0] > d[j1]: path = path[::-1]                                             # always from inside outward
                    cross.append((seg[i][1], seg[i][2], path, whole))
        # a way out is one that players walk right through: a pocket such as the res shrine's is crossed but never walked on from
        doors = [m for m in clusters(cross, 600) if len(m) >= max(6, 0.04 * len(cross)) and sum(1 for x in m if x[3]) >= max(4, 0.15 * len(m))][:5]
        # the front door is the busiest way out that the flag run goes through; the back door is the busiest way out
        # that is a different way (not a second stream down the same passage)
        on_run = lambda m: min(math.dist(med(m), q) for q in run) if run else DS.get(land.snap(med(m)), 1e18)
        way = lambda m: medoid([x[2] for x in m if x[3]] if sum(1 for x in m if x[3]) >= 5 else [x[2] for x in m])
        onr = [m for m in doors if on_run(m) <= 800]
        front = max(onr, key=len) if onr else (min(doors, key=on_run) if doors else None)
        picked = [(front, way(front))] if front else []
        for m in sorted([m for m in doors if m is not front], key=len, reverse=True):
            r = way(m)
            if route_gap(r, picked[0][1]) > 700 and route_gap(picked[0][1], r) > 700: picked.append((m, r)); break
        cuts = []
        for k, (m, route) in enumerate(picked):
            typ = "Front door" if k == 0 else "Back door"
            full = [x[2] for x in m if x[3]]
            add("route", typ, simplify(route), f"{len(m)} of {len(cross)} crossings {round(ring)} units' walk from the Guild Lord went this way"
                + ("" if len(full) >= 5 else "; few players walked the whole stretch, so the ends are rough"))
            # where this way out is narrowest, furthest from the Lord: the door itself
            pts = [q for q in resample(route, 80) if cell(q) in CL and D[s].get(cell(q), 0) >= 1800]
            if pts:
                w = min(CL[cell(q)] for q in pts)
                door = [q for q in pts if CL[cell(q)] <= w + 1][-1]
                cuts.append((door, (w + 2.5) * CELL))
        if len(picked) < 2: note.append(f"the {land.where(lord)} base: only {['no', 'one'][len(picked)]} busy way out found, so {'no door' if not picked else 'no back door'} is drafted")
        # base: the ground still joined to the Guild Lord with the narrowest point of each drafted way out shut; where
        # that does not close it off (an open-sided base), the half of the walk to the stand that lies nearer the Lord.
        # (Shutting Denning's own choke points was tried and reads worse: his chokes sit beyond the edge of his bases.)
        other = [land.snap(q) for q in lords if q is not lord] + [land.snap(stand)]
        blocked = {c for c in land.cells for door, r in cuts if math.dist(mid(c), door) <= r}
        inside = set(land.field(lord, blocked)) | {c for c in blocked}
        if len(cuts) == 2 and len(inside) < 0.6 * len(land.cells) and not any(c in inside for c in other):
            add("area", "Base", cells_hull(inside), "the ground still joined to the Guild Lord with both drafted doors shut at their narrowest")
        else:
            rb = BASE_SHARE * D[s].get(land.snap(stand), 9000)
            add("area", "Base", cells_hull({c for c, d in D[s].items() if d <= rb}), f"rough: the ground within {round(rb)} units' walk of the Guild Lord, half the walk to the stand (the doors did not close the base off)")
    # teleporters: the same long jump, from one exact spot to another, in a good share of the replays (a Shadow Step or
    # Recall lands somewhere different each time and is used by few teams)
    found = []
    for m in clusters([(a[0], a[1], b, f) for a, b, f in H["jumps"]], 250):
        ends = clusters([(x[2][0], x[2][1], x[3]) for x in m], 300)[0]
        reps = len({e[2] for e in ends})
        if reps < max(3, 0.2 * H["n"]) or len(ends) < 6: continue
        a, b = med([x for x in m if any(math.dist(x[2], e[:2]) < 1 for e in ends)] or m), med(ends)
        if any(math.dist(a, fa) < 500 and math.dist(b, fb) < 500 for fa, fb in found): continue
        found.append((a, b))
        add("route", "Teleporter (one way)", [a, b], f"{len(ends)} jumps from here to there in {reps} of {H['n']} replays", key=f"{round(a[0] / 300)}_{round(a[1] / 300)}")
    return {"map_id": mid_, "map": land.name, "replays": H["n"], "labels": L, "notes": note}


# ---- scoring against Denning's labels
def route_gap(a, b):
    """Mean distance from points along route a to route b (units)."""
    A, B = resample(a, 60), resample(b, 200)
    return statistics.mean(min(math.dist(p, q) for q in B) for p in A)


def score(mid_, d):
    land = Land(mid_)
    mine = d["labels"]; his = json.load(open(os.path.join(MAPS, "labels", f"{mid_}.json")))["labels"]
    lords = [l["pts"][0] for l in his if l["type"] == "Guild Lord"]
    side = lambda p: min(range(len(lords)), key=lambda i: math.dist(p, lords[i]))
    cen = lambda l: [statistics.mean(p[0] for p in l["pts"]), statistics.mean(p[1] for p in l["pts"])]
    rows = []
    for typ in ("Flag stand", "Res shrine", "Flag spawn"):
        for h in [l for l in his if l["kind"] == "point" and l["type"] == typ]:
            c = [m for m in mine if m["kind"] == "point" and m["type"] == typ]
            if c: rows.append((typ, "point", f"{round(min(math.dist(h['pts'][0], m['pts'][0]) for m in c))} units from Denning's"))
            else: rows.append((typ, "point", "not drafted"))
    for typ in ("Flag stand area", "Pit", "Base"):
        for h in [l for l in his if l["kind"] == "area" and l["type"] == typ]:
            c = [m for m in mine if m["kind"] == "area" and m["type"] == typ and (typ == "Flag stand area" or side(cen(m)) == side(cen(h)))]
            if not c: rows.append((typ, "area", "not drafted")); continue
            hc = poly_cells(land, h["pts"]); mc = poly_cells(land, c[0]["pts"])
            rows.append((typ, "area", f"overlap {len(hc & mc) / max(len(hc | mc), 1):.0%} (covers {len(hc & mc) / max(len(hc), 1):.0%} of Denning's; {len(mc - hc) / max(len(mc), 1):.0%} of the draft is outside it)"))
    for typ in ("Flag run", "Front door", "Back door"):
        for h in [l for l in his if l["kind"] == "route" and l["type"] == typ]:
            c = [m for m in mine if m["kind"] == "route" and m["type"] == typ and side(m["pts"][0]) == side(h["pts"][0])]
            if not c: rows.append((typ, "route", "not drafted")); continue
            rows.append((typ, "route", f"Denning's line is {round(route_gap(h['pts'], c[0]['pts']))} units from the draft on average (draft {round(path_len(c[0]['pts']))} long, his {round(path_len(h['pts']))})"))
    ht = [l["pts"][0] for l in his if l["type"].startswith("Teleporter")]
    mt = [m for m in mine if m["type"].startswith("Teleporter")]
    if ht or mt:
        ends = [p for m in mt for p in m["pts"]]
        rows.append(("Teleporter", "route", f"{len(mt)} drafted against {len(ht) // 2} labelled pairs; " + (f"Denning's points are {', '.join(str(round(min(math.dist(h, e) for e in ends))) for h in ht)} units from a drafted end" if ends else "none found")))
    return rows


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    ids = args or [h["id"] for h in json.load(open(os.path.join(MAPS, "index.json")))["halls"]]
    os.makedirs(os.path.join(MAPS, "draft"), exist_ok=True)
    only = next((set(a[7:].split(",")) for a in sys.argv[1:] if a.startswith("--only=")), None)
    for mid_ in ids:
        d = draft(mid_)
        if only: d["labels"] = [l for l in d["labels"] if l["type"] in only and l["kind"] == "point"]; d["notes"] = []; d["only"] = sorted(only)
        if "--score" in sys.argv:
            print(f"\n== {d['map']} ({d['replays']} replays) ==")
            for typ, kind, text in score(mid_, d): print(f"  {typ:<16} {text}")
            for n in d["notes"]: print("  note:", n)
        if "--dry" not in sys.argv:
            json.dump(d, open(os.path.join(MAPS, "draft", f"{mid_}.json"), "w"), indent=1)
            print(f"{mid_} {d['map']}: {len(d['labels'])} draft labels" + (f"; {'; '.join(d['notes'])}" if d["notes"] else ""), file=sys.stderr)
