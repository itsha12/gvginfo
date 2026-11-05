"""Case library: every episode from every analysed match in one place, with its match context, so situations can be
compared across matches.

Build:  python3 library.py build [--src DIR] [--out DIR]     (default src /tmp/ga from analyze.py --all, out /tmp/gl)
Query:  python3 library.py query <kind> [--where EXPR] [--show f1,f2,...] [--sort FIELD] [--limit N]
        kinds: splits, flag_runs, stand, deaths, monks, windows, findings
        EXPR is a Python expression over a record's fields, e.g.
          --where "members == ['Ranger'] and entered_base is not None"
          --where "victim.endswith('Monk') and monk_distance and max(monk_distance.values()) > 5000"
Every record carries: match, map, team (the episode's team), opponent, won (did the episode's team win), plus the
episode's own fields (see episodes.py, fights.py, rules.py)."""
import glob, json, os, sys

KINDS = ("splits", "flag_runs", "stand", "deaths", "monks", "windows", "findings")


def build(src="/tmp/ga", out="/tmp/gl"):
    os.makedirs(out, exist_ok=True)
    rows = {k: [] for k in KINDS}
    for f in sorted(glob.glob(os.path.join(src, "*.json"))):
        a = json.load(open(f))
        tags = {t["id"]: t["tag"] for t in a["meta"]["teams"]}
        win = tags.get((a["meta"].get("result") or {}).get("winning_team_id"))
        for k in KINDS:
            for r in a.get(k, []):
                team = r.get("team")
                opp = next((t for t in tags.values() if t != team), None)
                rows[k].append({"match": a["id"], "map": a["meta"]["map"], "teams": "v".join(tags.values()),
                                "opponent": opp, "won": team == win if team else None, **r})
    for k, L in rows.items():
        with open(os.path.join(out, k + ".jsonl"), "w") as fh:
            for r in L: fh.write(json.dumps(r, default=list) + "\n")
    print({k: len(v) for k, v in rows.items()})


def load(kind, lib="/tmp/gl"):
    return [json.loads(l) for l in open(os.path.join(lib, kind + ".jsonl"))]


def query(kind, where=None, show=None, sort=None, limit=50, lib="/tmp/gl"):
    rows = load(kind, lib)
    if where:
        keep = []
        for r in rows:
            try:
                if eval(where, {}, dict(r)): keep.append(r)
            except Exception: pass
        rows = keep
    if sort: rows.sort(key=lambda r: (r.get(sort) is None, r.get(sort)))
    print(f"{len(rows)} {kind}")
    for r in rows[:limit]:
        print({k: r.get(k) for k in show} if show else r)
    return rows


if __name__ == "__main__":
    args = sys.argv[1:]
    opt = lambda name, default=None: (args[args.index(name) + 1] if name in args else default)
    if args[0] == "build": build(opt("--src", "/tmp/ga"), opt("--out", "/tmp/gl"))
    else:
        query(args[1], opt("--where"), (opt("--show") or "").split(",") if opt("--show") else None, opt("--sort"),
              int(opt("--limit", 50)), opt("--lib", "/tmp/gl"))
