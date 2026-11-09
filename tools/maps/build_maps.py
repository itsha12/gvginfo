"""Build the map page's data for every guild hall in the stored replays (site only; the engine does not read these).

For each hall (gvg.report map id):
  data/maps/outline/<id>.json   the walkable outline: gvg.report's pathing trapezoids where it publishes them
                                (source "gvg.report"), otherwise the area players walked in the stored replays
                                (source "walked": 100-unit cells, as runs per row)
  data/maps/auto/<id>.json      points the replays give: flag stand, both res shrines (where each team starts),
                                both flag spawns, and NPC positions estimated from where their attackers stood
  data/maps/index.json          the list of halls (id, name, replays, outline source, wiki page)
Denning's own labels live in data/maps/labels/<id>.json, written by the site's Maps page; this script never touches them.

Kept outside tools/replay_analysis on purpose: every .py file in that folder is part of the engine's cache key.

Usage: python3 tools/maps/build_maps.py      (needs the replays branch: git fetch --depth 1 origin +replays:refs/remotes/origin/replays)
"""
import bisect, collections, datetime, gzip, json, math, os, statistics, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "data", "maps")
CELL = 100                    # size of a walked cell, in game units
MIN_VISITS = 2                # a cell counts as walkable once players crossed it in this many matches
STATIC = ("guild_lord", "bodyguard", "knight", "archer", "footman")
MELEE = {"Warrior", "Dervish", "Assassin"}
WIKI = {"Isle of the Dead": "Isle_of_the_Dead_(guild_hall)"}


def blob(path):
    return subprocess.run(["git", "-C", REPO, "cat-file", "-p", "origin/replays:" + path], capture_output=True, check=True).stdout


def med(pts):
    return [round(statistics.median(p[0] for p in pts)), round(statistics.median(p[1] for p in pts))]


def snap(track, t):
    """Position of a track at time t (tenths of a second), or None when the nearest sample is over 2 s away."""
    T = track["t"]
    i = min(max(bisect.bisect_left(T, t), 0), len(T) - 1)
    if i > 0 and abs(T[i - 1] - t) < abs(T[i] - t): i -= 1
    if abs(T[i] - t) > 20: return None
    return (track["x"][i], track["y"][i])


def clusters(pts, radius):
    """Greedy clusters of (x, y, weight, ...) points: densest first. Returns [(members)]."""
    left, out = list(pts), []
    while left:
        best = max(left, key=lambda p: sum(1 for q in left if math.dist(p[:2], q[:2]) < radius))
        mem = [q for q in left if math.dist(best[:2], q[:2]) < radius]
        out.append(mem)
        left = [q for q in left if q not in mem]
    return out


class Hall:
    def __init__(self, mid, name):
        self.id, self.name, self.replays = mid, name, 0
        self.cells = collections.Counter()          # (ix, iy) -> matches that crossed it
        self.stand, self.bases, self.pickups = [], [], []
        self.npcs = collections.defaultdict(list)   # kind -> [(x, y, samples, melee, base point of its team)]

    def add(self, o):
        self.replays += 1
        A, TR = o["agents"], o["tracks"]
        players = [i for i, a in enumerate(A) if a.get("player") and str(i) in TR]
        seen = set()
        for a in players:
            T = TR[str(a)]
            xs, ys, ts, st = T["x"], T["y"], T["t"], T["st"]
            for i in range(len(ts)):
                if st[i] == "d": continue
                seen.add((int(xs[i] // CELL), int(ys[i] // CELL)))
                # fill the cells between two samples about a second apart (a Shadow Step or a res is not walking)
                if i and st[i - 1] != "d" and ts[i] - ts[i - 1] <= 15:
                    dx, dy = xs[i] - xs[i - 1], ys[i] - ys[i - 1]
                    dist = math.hypot(dx, dy)
                    if CELL < dist < 500:
                        n = int(dist // (CELL / 2))
                        for k in range(1, n):
                            seen.add((int((xs[i - 1] + dx * k / n) // CELL), int((ys[i - 1] + dy * k / n) // CELL)))
        for c in seen: self.cells[c] += 1
        base = {}
        for tm in (1, 2):
            pts = [(TR[str(a)]["x"][0], TR[str(a)]["y"][0]) for a in players if A[a].get("team") == tm]
            if pts: base[tm] = med(pts); self.bases.append(tuple(base[tm]))
        for t, typ, a, *_ in o.get("flags", []):
            if not isinstance(a, int) or str(a) not in TR: continue
            p = snap(TR[str(a)], t)
            if not p: continue
            if typ == "flagstand_captured": self.stand.append(p)
            elif typ == "flag_picked_up": self.pickups.append(p)
        hits = collections.defaultdict(list)
        for r in o["ev"]:
            if r[1] in ("dm", "af") and isinstance(r[3], int) and r[3] < len(A) and A[r[3]].get("npc") in STATIC \
                    and isinstance(r[2], int) and r[2] in players:
                p = snap(TR[str(r[2])], r[0])
                if p: hits[r[3]].append((p, A[r[2]].get("p") in MELEE))
        for a, h in hits.items():
            mel = [p for p, m in h if m]
            use, melee = (mel, True) if len(mel) >= 3 else ([p for p, _ in h], False)
            if len(use) < 3: continue
            x, y = med(use)
            self.npcs[A[a]["npc"]].append((x, y, len(use), melee, tuple(base.get(A[a].get("team")) or (0, 0))))

    def auto(self):
        out = {"map_id": self.id, "map": self.name, "replays": self.replays}
        if self.stand: out["stand"] = med(self.stand)
        b = clusters(self.bases, 1500)[:2]
        out["res_shrines"] = [med(m) for m in b if len(m) >= 2 or self.replays < 3]
        sp = [m for m in clusters(self.pickups, 300) if len(m) >= 3]
        spawns = []
        for m in sp:                                # the two densest pickup clusters that are apart: where new flags appear
            c = med(m)
            if all(math.dist(c, s) > 2000 for s in spawns) and (not out.get("stand") or math.dist(c, out["stand"]) > 1500):
                spawns.append(c)
            if len(spawns) == 2: break
        out["flag_spawns"] = spawns
        npcs = []
        for kind in STATIC:
            pts = self.npcs.get(kind, [])
            firm = clusters([p for p in pts if p[3]], 500)
            for m in firm:
                npcs.append({"kind": kind, "pos": med(m), "matches": len(m), "samples": sum(p[2] for p in m), "how": "melee"})
            for m in clusters([p for p in pts if not p[3]], 700):
                c = med(m)
                if any(n["kind"] == kind and math.dist(c, n["pos"]) < 1200 for n in npcs): continue
                npcs.append({"kind": kind, "pos": c, "matches": len(m), "samples": sum(p[2] for p in m), "how": "ranged"})
        # a spot seen in a single match is usually a stray estimate: keep it only while the hall has few replays
        floor = 2 if self.replays >= 10 else 1
        npcs = [n for n in npcs if n["matches"] >= floor]
        lords = sorted((n for n in npcs if n["kind"] == "guild_lord"), key=lambda n: -n["matches"])[:2]
        out["npcs"] = lords + [n for n in npcs if n["kind"] != "guild_lord"]
        return out

    def walked(self):
        rows = collections.defaultdict(list)
        for (ix, iy), n in self.cells.items():
            if n >= min(MIN_VISITS, self.replays): rows[iy].append(ix)
        runs = {}
        for iy, xs in rows.items():
            xs.sort(); r = [[xs[0], xs[0]]]
            for x in xs[1:]:
                if x == r[-1][1] + 1: r[-1][1] = x
                else: r.append([x, x])
            runs[str(iy)] = r
        return runs


def main():
    idx = json.loads(blob("index.json"))
    halls = {}
    files = [v["file"] for v in idx["matches"].values() if v.get("file")]
    for n, f in enumerate(files, 1):
        try: o = json.loads(gzip.decompress(blob(f)))
        except Exception as e: print("skipped", f, e, file=sys.stderr); continue
        mid = str(o["meta"].get("map_id") or o["meta"]["map"])
        halls.setdefault(mid, Hall(mid, o["meta"]["map"])).add(o)
        if n % 100 == 0: print(n, "of", len(files), "replays read", file=sys.stderr)
    have = set(subprocess.run(["git", "-C", REPO, "ls-tree", "--name-only", "origin/replays", "maps/"], capture_output=True,
                              text=True).stdout.split())
    os.makedirs(os.path.join(OUT, "outline"), exist_ok=True); os.makedirs(os.path.join(OUT, "auto"), exist_ok=True)
    index = []
    for mid, h in sorted(halls.items(), key=lambda kv: -kv[1].replays):
        runs = h.walked()
        xs = [x * CELL for r in runs.values() for run in r for x in (run[0], run[1] + 1)]
        ys = [int(iy) * CELL for iy in runs] + [(int(iy) + 1) * CELL for iy in runs]
        if f"maps/{mid}.json.gz" in have:
            g = json.loads(gzip.decompress(blob(f"maps/{mid}.json.gz")))
            traps = [[round(v) for v in t] for p in g["planes"] for t in p["trapezoids"]]
            b = g["bounds"]
            outline = {"map_id": mid, "map": h.name, "source": "gvg.report",
                       "bounds": [math.floor(min(b["min"]["x"], min(xs))), math.floor(min(b["min"]["y"], min(ys))),
                                  math.ceil(max(b["max"]["x"], max(xs))), math.ceil(max(b["max"]["y"], max(ys)))],
                       "traps": traps}
        else:
            outline = {"map_id": mid, "map": h.name, "source": "walked", "cell": CELL, "replays": h.replays,
                       "bounds": [min(xs), min(ys), max(xs), max(ys)], "rows": runs}
        json.dump(outline, open(os.path.join(OUT, "outline", f"{mid}.json"), "w"), separators=(",", ":"))
        json.dump(h.auto(), open(os.path.join(OUT, "auto", f"{mid}.json"), "w"), indent=1)
        index.append({"id": mid, "map": h.name, "replays": h.replays, "outline": outline["source"],
                      "wiki": "https://wiki.guildwars.com/wiki/" + WIKI.get(h.name, h.name.replace(" ", "_"))})
    json.dump({"generated": datetime.date.today().isoformat(), "halls": index}, open(os.path.join(OUT, "index.json"), "w"), indent=1)
    for x in index: print(f"{x['id']:>4} {x['map']:<24} {x['replays']:>3} replays  outline: {x['outline']}")


if __name__ == "__main__":
    main()
