"""Check Denning's map labels for anything missing or lopsided. Reads the labels; never writes them.

What it checks on each hall:
  roster     each pit holds 1 Guild Lord, 1 Bodyguard, 2 Knights and 2 Archers; each side has 1 Res shrine and
             1 Flag spawn; both sides have the same number of every other NPC, area and route
  mirror     the hall's symmetry is measured from the outline (a half turn about the centre, or a mirror line), each
             labelled point is carried to the other side, and a label with no partner of its type there is listed
             with the spot where the partner would stand
  replays    res shrines, flag spawns and NPCs the replays show with no label of that type near them

Output: the findings per hall, printed. Sides are named by where each Guild Lord sits on the Maps page.
Usage:  python3 tools/maps/audit_labels.py [map id ...]
Kept outside tools/replay_analysis on purpose (every .py there is part of the engine's cache key).
"""
import collections, json, math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draft_labels import Land, MAPS, CELL, cell, in_poly

PIT = {"Guild Lord": 1, "Bodyguard": 1, "Knight": 2, "Archer": 2}
ONE_EACH = ("Res shrine", "Flag spawn")
MUST_MATCH = {"Guild Lord", "Bodyguard", "Knight", "Archer", "Footman", "Res shrine", "Flag spawn", "Base", "Pit"}
NPC = ("Guild Lord", "Bodyguard", "Knight", "Archer", "Footman")
KIND = {"guild_lord": "Guild Lord", "bodyguard": "Bodyguard", "knight": "Knight", "archer": "Archer", "footman": "Footman"}
PAIR_TOL = 1000       # a mirrored label counts as matched within this many units (halls are not exact mirrors)
SYM_MIN = 0.9         # the mirror check runs only when this share of the outline lands on the outline when carried across
DOUBLE = 60           # two labels of one type this close are one label saved twice (pit knights stand about 100 apart)
AREA_TOL = 1300       # the same, for the middle of a mirrored area
PIT_PAD = 150         # a point this close outside the pit's edge still counts as in the pit
NEAR = {"Res shrine": 700, "Flag spawn": 500, "npc": 1500}   # a replay point is "labelled" within these distances


def centre(l):
    p = l["pts"]
    return (sum(q[0] for q in p) / len(p), sum(q[1] for q in p) / len(p))


def near_poly(p, pts, pad):
    if in_poly(p[0], p[1], pts): return True
    for a, b in zip(pts, pts[1:] + pts[:1]):
        dx, dy = b[0] - a[0], b[1] - a[1]; L = dx * dx + dy * dy or 1
        t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L))
        if math.dist(p, (a[0] + t * dx, a[1] + t * dy)) <= pad: return True
    return False


def rigid(pairs, flip):
    """Best rigid move (turn and shift, with a mirror when flip) carrying each a to its b, by least squares."""
    A = [complex(*a) for a, _ in pairs]; B = [complex(*b) for _, b in pairs]
    if flip: A = [z.conjugate() for z in A]
    ma, mb = sum(A) / len(A), sum(B) / len(B)
    r = sum((b - mb) * (a - ma).conjugate() for a, b in zip(A, B))
    r = r / abs(r) if abs(r) else 1
    def T(p):
        z = complex(*p); z = z.conjugate() if flip else z
        w = r * (z - ma) + mb
        return (w.real, w.imag)
    return T


def outline_fit(land, T):
    hit = 0
    for q in land.cells:
        x, y = cell(T(((q[0] + 0.5) * CELL, (q[1] + 0.5) * CELL)))
        hit += any((x + i, y + j) in land.cells for i in (-1, 0, 1) for j in (-1, 0, 1))
    return hit / len(land.cells)


def symmetry(land, pairs):
    """The move that carries one side of the hall onto the other, fitted to labels that come one per side
    (and to the reverse pairs, so it works both ways). Returns it, its kind, and the share of the outline it keeps."""
    both = pairs + [(b, a) for a, b in pairs]
    best = None
    for flip, name in ((False, "half turn"), (True, "mirror")):
        T = rigid(both, flip); f = outline_fit(land, T)
        if not best or f > best[2]: best = (T, name, f)
    return best


def audit(mid_):
    land = Land(mid_)
    L = json.load(open(os.path.join(MAPS, "labels", f"{mid_}.json")))["labels"]
    auto = json.load(open(os.path.join(MAPS, "auto", f"{mid_}.json")))
    out = {"map_id": mid_, "map": land.name, "labels": len(L), "issues": [], "roster": {}, "pit": {}, "features": {}}
    issue = lambda kind, text, at=None: out["issues"].append({"kind": kind, "text": text, **({"at": [round(at[0]), round(at[1])]} if at else {})})
    lords = sorted((centre(l) for l in L if l["kind"] == "point" and l["type"] == "Guild Lord"))
    if len(lords) != 2:
        issue("roster", f"{len(lords)} Guild Lords labelled; two are needed before the rest can be checked"); return out
    fields = [land.field(p) for p in lords]
    def side(p):
        c = land.snap(p); d = [f.get(c, 1e9) for f in fields]
        if abs(d[0] - d[1]) < 0.12 * max(d): return "mid"
        return "AB"[d.index(min(d))]
    names = {"A": land.where(lords[0]), "B": land.where(lords[1])}
    if names["A"] == names["B"]: names = {"A": names["A"] + " (lower x)", "B": names["B"] + " (higher x)"}
    out["sides"] = names
    # roster by side
    by = collections.defaultdict(lambda: collections.defaultdict(list)); counted = {}
    for l in L:
        p = l["pts"][0] if l["kind"] == "route" else centre(l)
        typ = l["type"] if l["type"] != "Other" or not l.get("name") else f"Other ({l['name']})"
        by[(l["kind"], typ)][side(p)].append(l)
    for (kind, typ), s in sorted(by.items()):
        out["roster"][f"{kind}: {typ}"] = {k: len(v) for k, v in sorted(s.items())}
        a, b = len(s.get("A", [])), len(s.get("B", []))
        counted[(kind, typ)] = (a, b)
        if a != b and (typ in MUST_MATCH or kind == "route"):
            issue("lopsided", f"{typ} ({kind}): {a} on the {names['A']} side, {b} on the {names['B']} side")
    for typ in ONE_EACH:
        s = by.get(("point", typ), {})
        for k in "AB":
            if len(s.get(k, [])) != 1: issue("roster", f"{typ}: {len(s.get(k, []))} on the {names[k]} side (one expected)")
    for typ in NPC:
        if ("point", typ) not in by:
            out["features"]["no_" + typ.lower().replace(" ", "_")] = True
            if typ != "Footman": issue("roster", f"No {typ} labelled anywhere")
    out["features"]["footmen_per_side"] = len(by.get(("point", "Footman"), {}).get("A", []))
    out["features"]["archers_per_side"] = len(by.get(("point", "Archer"), {}).get("A", []))

    # the hall's symmetry, fitted to everything labelled once per side
    pairs = [(lords[0], lords[1])]
    for (kind, typ), sd in by.items():
        if kind != "route" and typ != "Guild Lord" and len(sd.get("A", [])) == 1 and len(sd.get("B", [])) == 1:
            pairs.append((centre(sd["A"][0]), centre(sd["B"][0])))
    T, sym, fitness = symmetry(land, pairs)
    out["symmetry"] = {"kind": sym, "outline_fit": round(fitness, 3), "fitted_on": len(pairs)}

    # pits
    pits = [l for l in L if l["kind"] == "area" and l["type"] == "Pit"]
    for k, lord in zip("AB", lords):
        pit = next((p for p in pits if near_poly(lord, p["pts"], PIT_PAD)), None)
        if not pit: issue("pit", f"No Pit area around the {names[k]} Guild Lord"); continue
        got = {t: sum(1 for l in L if l["kind"] == "point" and l["type"] == t and near_poly(centre(l), pit["pts"], PIT_PAD)) for t in PIT}
        out["pit"][k] = got
        for t, want in PIT.items():
            if got[t] != want: issue("pit", f"{names[k]} pit holds {got[t]} {t}{'s' if got[t] != 1 else ''} ({want} expected)", lord)

    # doubles: two labels of one type on the same spot
    pts = [l for l in L if l["kind"] == "point"]
    for i, l in enumerate(pts):
        for m in pts[i + 1:]:
            if m["type"] == l["type"] and math.dist(centre(l), centre(m)) < DOUBLE:
                p = centre(l); issue("double", f"Two {l['type']} labels on the same spot at {land.where(p)} ({round(p[0])}, {round(p[1])})", p)

    # mirror partners (only where the outline shows the hall is close to symmetric)
    if fitness < SYM_MIN:
        out["symmetry"]["used"] = False                 # too far from symmetric to place partners: fall back to counts per side
        for (kind, typ), (a, b) in sorted(counted.items()):
            if a != b and typ not in MUST_MATCH and kind != "route":
                issue("lopsided", f"{typ} ({kind}): {a} on the {names['A']} side, {b} on the {names['B']} side (counted by the nearer Guild Lord; one may sit near the middle)")
    else:
        out["symmetry"]["used"] = True
        for kind, typ, tol in sorted({(l["kind"], l["type"], PAIR_TOL if l["kind"] == "point" else AREA_TOL) for l in L if l["kind"] != "route"}):
            grp = [l for l in L if l["kind"] == kind and l["type"] == typ]
            rest = grp
            cand = sorted((math.dist(T(centre(l)), centre(m)), i, j) for i, l in enumerate(rest) for j, m in enumerate(rest) if i < j)
            done = set()
            for d, i, j in cand:
                if d > tol: break
                if i in done or j in done: continue
                done |= {i, j}
            # what is left may sit on the centre line, where a label is its own partner
            done |= {i for i, l in enumerate(rest) if i not in done and math.dist(centre(l), T(centre(l))) <= tol}
            for i, l in enumerate(rest):
                if i in done: continue
                p = centre(l); image = T(p)
                gap = min((math.dist(centre(m), image) for m in rest if m is not l), default=None)
                issue("mirror", f"{typ}{' area' if kind == 'area' else ''}{' (' + l['name'] + ')' if l.get('name') else ''} at {land.where(p)} ({round(p[0])}, {round(p[1])}) "
                      f"has no partner across the hall"
                      + (f" (the nearest {typ} is {round(gap)} units from where the partner would stand)" if gap is not None else ""), image)

    # what the replays show
    def nearest(typ, p):
        return min((math.dist(centre(l), p) for l in pts if l["type"] == typ), default=None)
    for p in auto.get("flag_spawns") or []:
        d = nearest("Flag spawn", p)
        if d is None or d > NEAR["Flag spawn"]:
            issue("replays", f"Flags are picked up at {land.where(p)} ({p[0]}, {p[1]}) in the replays; "
                  + (f"the nearest Flag spawn label is {round(d)} units away" if d is not None else "no Flag spawn is labelled"), p)
    dp = os.path.join(MAPS, "draft", f"{mid_}.json")
    drafted = [l["pts"][0] for l in json.load(open(dp))["labels"] if l["type"] == "Res shrine"] if os.path.exists(dp) else []
    for p in drafted:
        d = nearest("Res shrine", p)
        if d is None or d > NEAR["Res shrine"]:
            issue("replays", f"Dead players come back at {land.where(p)} ({p[0]}, {p[1]}) in the replays; "
                  + (f"the nearest Res shrine label is {round(d)} units away" if d is not None else "no Res shrine is labelled"), p)
    for n in auto.get("npcs") or []:
        typ = KIND.get(n["kind"])
        if not typ or n.get("matches", 0) < 5: continue
        d = nearest(typ, n["pos"])
        if d is None or d > NEAR["npc"]:
            issue("replays", f"A {typ} was attacked at {land.where(n['pos'])} ({n['pos'][0]}, {n['pos'][1]}) in {n['matches']} matches (rough: read from where its attackers stood); "
                  + (f"the nearest {typ} label is {round(d)} units away" if d is not None else f"no {typ} is labelled"), n["pos"])
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    ids = args or [h["id"] for h in json.load(open(os.path.join(MAPS, "index.json")))["halls"]
                   if os.path.exists(os.path.join(MAPS, "labels", f"{h['id']}.json"))]
    for m in ids:
        r = audit(m)
        s = r.get("symmetry", {})
        print(f"\n{r['map']} ({m}): {r['labels']} labels; {s.get('kind', '?')} symmetry, outline fit {s.get('outline_fit', '?')}; pits {r['pit']}")
        for i in r["issues"]: print(f"  [{i['kind']}] {i['text']}" + (f"  -> {i['at']}" if i.get("at") and i["kind"] == "mirror" else ""))
        if not r["issues"]: print("  nothing found")


if __name__ == "__main__":
    main()
