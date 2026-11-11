"""Draft the "greater stand area" of every hall for Denning to accept or redraw on the map page (R-334, R-342).

The greater stand area is where the main groups stand when they fight around the flag stand: wider than the labelled
Flag stand area, and still "at the stand" in his words. Drafted from the replays: every 5 s of every counted match,
each fight with three or more players a side that is not in a pit or base, at a door or at the footmen, and whose
middle is within 5,000 units' walk of the stand, adds its players' positions. The draft is the hull of the busiest
ground holding 85% of those positions and joined to the stand.

Writes one area of type "Greater stand area" (id greater-stand-0) into data/maps/draft/<map id>.json beside the other
drafts; never touches Denning's labels. Needs the engine of the bundle-4 branch. Kept outside tools/replay_analysis.
Usage:  python3 tools/maps/draft_greater_stand.py [--jobs N] [--dry]"""
import collections, json, math, multiprocessing, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools", "replay_analysis"))
SIDE_MIN, WALK_MAX, SHARE, STEP = 3, 5000, 0.85, 5
OPEN = ("stand", "greater stand", "field")


def _one(rid):
    from replaylib import Match
    from state import GameState
    import moments
    try:
        st = GameState(Match.from_branch(rid))
        if not st.hall: return None
        M, h, c = moments.Moments(st), st.hall, collections.Counter()
        to = h.to(h.stand)
        for t in range(30, M.T + 1, STEP):
            for f in M.fights(t):
                if min(f["n"].values()) < SIDE_MIN or f["kind"] not in OPEN: continue
                ids = list(f["ids"][1] | f["ids"][2])
                mid = (sum(M.P[a][t][0] for a in ids) / len(ids), sum(M.P[a][t][1] for a in ids) / len(ids))
                if to.get(h.snap(mid), 1e9) > WALK_MAX: continue
                for a in ids: c[h.snap(M.P[a][t])] += 1
        return h.id, dict(c)
    except Exception as e:
        return None


def hull(pts):
    pts = sorted(set(pts))
    if len(pts) < 3: return pts
    cross = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def main():
    import common, hallmap
    jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 2
    cells, n = collections.defaultdict(collections.Counter), collections.Counter()
    with multiprocessing.Pool(jobs) as pool:
        for r in pool.imap_unordered(_one, common.replay_ids(), chunksize=4):
            if r: cells[r[0]].update(r[1]); n[r[0]] += 1
    for mid_ in hallmap.hall_ids():
        h, c = hallmap.Hall.get(mid_), cells.get(mid_)
        if not h or not c or sum(c.values()) < 2000:
            print(f"{h.name if h else mid_}: too few fights around the stand in the stored replays ({sum((c or {}).values())} positions): no draft"); continue
        tot, acc, keep = sum(c.values()), 0, set()
        for cell_, v in c.most_common():
            if acc >= SHARE * tot: break
            keep.add(cell_); acc += v
        seen, todo = set(), [min(keep, key=lambda q: (q[0] - h.snap(h.stand)[0]) ** 2 + (q[1] - h.snap(h.stand)[1]) ** 2)]
        while todo:                                   # the part joined to the stand (a gap of one cell is bridged)
            q = todo.pop()
            if q in seen: continue
            seen.add(q)
            todo += [(q[0] + dx, q[1] + dy) for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2) if (q[0] + dx, q[1] + dy) in keep and (q[0] + dx, q[1] + dy) not in seen]
        poly = [[round(x), round(y)] for x, y in hull([hallmap.mid(q) for q in seen])]
        far = max(math.dist(p, h.stand) for p in poly)
        lab = {"id": "greater-stand-0", "kind": "area", "type": "Greater stand area", "name": "", "note": "", "pts": poly,
               "how": f"where fights of {SIDE_MIN}+ a side stood around the stand in {n[mid_]} replays ({round(100 * sum(c[q] for q in seen) / tot)}% of those positions); reaches {round(far / 100) * 100} units from the stand"}
        print(f"{h.name}: {len(poly)} corners, reaches {round(far)} from the stand, {n[mid_]} replays")
        if "--dry" in sys.argv: continue
        path = os.path.join(REPO, "data", "maps", "draft", f"{mid_}.json")
        try: d = json.load(open(path))
        except (OSError, ValueError): d = {"map_id": mid_, "map": h.name, "labels": [], "notes": []}
        d["labels"] = [l for l in d.get("labels", []) if l.get("id") != lab["id"]] + [lab]
        json.dump(d, open(path, "w"), indent=1)


if __name__ == "__main__":
    main()
