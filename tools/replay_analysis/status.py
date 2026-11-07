"""How far each stored match has been taken, match by match (data/model/match_status.json).

Derived fields (rebuilt by `sync`, never edited by hand):
  teams, map, batch (training batch it joined, or null), engine (analysis engine version that last analysed it, from
  analyze.py), review (tag of its entry on knowledge/match-reviews.md), sources (commentary or comms behind that review),
  labels (Denning's rulings on its moments in data/review_labels.json).
Recorded fields (set with `mark`, kept by `sync`):
  why_shown   events whose why was walked through with Denning (time, kind, what), e.g. "4:01 death RACK 8 Monk"
  reviewed    Denning reviewed it with Claude (a short note)
  commentary  per source: "pending", "checked" (claims checked against the engine) or "done" (claims filed)
  notes       anything else worth knowing about the match

Usage:  python3 status.py                         one line per match, then what still needs doing
        python3 status.py sync                    rebuild the derived fields (run after analyze.py --all or batch.py add)
        python3 status.py mark <id> why "<m:ss> <kind> <what>"
        python3 status.py mark <id> reviewed "<note>"
        python3 status.py mark <id> commentary <source> pending|checked|done
        python3 status.py mark <id> notes "<text>"
<id> may be the first 8 characters of the report id."""
import json, os, re, subprocess, sys
from common import REPO

PATH = os.path.join(REPO, "data", "model", "match_status.json")
REVIEWS = os.path.join(REPO, "knowledge", "match-reviews.md")
LABELS = os.path.join(REPO, "data", "review_labels.json")
BATCHES = os.path.join(REPO, "data", "model", "batches.json")
SRC = "/tmp/ga"
RECORDED = ("why_shown", "reviewed", "commentary", "notes")


def load():
    try: return json.load(open(PATH))
    except (OSError, ValueError): return {"about": __doc__.split("\n\n")[0], "matches": {}}


def save(s):
    s["matches"] = dict(sorted(s["matches"].items(), key=lambda kv: (kv[1].get("batch") is None, kv[1].get("batch") or 0, kv[0])))
    json.dump(s, open(PATH, "w"), indent=1, ensure_ascii=False)


def stored():
    try: return json.loads(subprocess.check_output(["git", "-C", REPO, "show", "origin/replays:index.json"]))["matches"]
    except subprocess.CalledProcessError: return {}


def _reviews():
    """{report id: (tag, sources)} from the reviews page: each entry names its gvg.report id and its source."""
    out, text = {}, open(REVIEWS).read()
    for block in re.split(r"\n## ", text):
        head = block.split("\n", 1)[0]
        tag = re.match(r"\[([^\]]+)\]", head)
        ids = re.findall(r"gvg\.report ([0-9a-f]{8}-[0-9a-f-]{27})", block)
        if tag and ids:
            src = re.search(r"Source: ([^.(]+)", block)
            s = (src.group(1).strip() if src else "")
            out[ids[0]] = (tag.group(1), [] if s.startswith("replay only") else [s])
    sources = text.split("## Sources", 1)[-1].split("\n## ", 1)[0]
    bounty = sources.split("**Bounty:**", 1)[-1].split("- **", 1)[0]
    for rid in re.findall(r"[0-9a-f]{8}-[0-9a-f-]{27}", bounty):
        tag, s = out.get(rid, (None, []))
        out[rid] = (tag, sorted(set(s) | {"Bounty"}))
    return out


def sync():
    s = load(); M = s["matches"]
    idx = stored()
    batch = {m: b["batch"] for b in json.load(open(BATCHES))["batches"] for m in b["matches"]}
    labels = {}
    for l in json.load(open(LABELS)).get("labels", []): labels[l["match"]] = labels.get(l["match"], 0) + 1
    rev = _reviews()
    for rid in idx:
        e = M.setdefault(rid, {})
        e["batch"] = batch.get(rid)
        p = os.path.join(SRC, rid + ".json")
        if os.path.exists(p):
            a = json.load(open(p)); meta = a["meta"]
            e["teams"] = " v ".join(t["tag"] for t in meta["teams"]); e["map"] = meta["map"]; e["engine"] = a.get("engine")
        tag, src = rev.get(rid, (None, []))
        e["review"] = tag; e["sources"] = src; e["labels"] = labels.get(rid, 0)
        for k in RECORDED:
            if k == "commentary":
                e.setdefault(k, {})
                for x in src: e[k].setdefault(x, "pending")
            else: e.setdefault(k, [] if k == "why_shown" else None)
    save(s)
    return s


def find(s, prefix):
    hits = [k for k in s["matches"] if k.startswith(prefix)]
    if len(hits) != 1: sys.exit(f"{len(hits)} matches start with {prefix}")
    return hits[0]


def mark(prefix, field, *val):
    s = load(); rid = find(s, prefix); e = s["matches"][rid]
    if field == "why": e.setdefault("why_shown", []).append(val[0])
    elif field == "reviewed": e["reviewed"] = val[0]
    elif field == "commentary": e.setdefault("commentary", {})[val[0]] = val[1]
    elif field == "notes": e["notes"] = val[0]
    else: sys.exit("field: why, reviewed, commentary or notes")
    save(s)


def show():
    s = load(); rows = s["matches"]
    print(f"{'match':<9} {'teams':<22} {'batch':>5} {'engine':<10} {'why':>3} {'rev':>3} {'lab':>3}  commentary")
    for rid, e in rows.items():
        c = ", ".join(f"{k} {v}" for k, v in (e.get("commentary") or {}).items())
        print(f"{rid[:8]:<9} {(e.get('teams') or '?')[:22]:<22} {str(e.get('batch')):>5} {str(e.get('engine'))[:10]:<10} "
              f"{len(e.get('why_shown') or []):>3} {'yes' if e.get('reviewed') or e.get('review') else '':>3} {e.get('labels', 0):>3}  {c}")
    todo_batch = [r for r, e in rows.items() if e.get("batch") is None]
    todo_c = [(r, k) for r, e in rows.items() for k, v in (e.get("commentary") or {}).items() if v != "done"]
    no_why = [r for r, e in rows.items() if e.get("batch") is not None and not e.get("why_shown")]
    print(f"\nnot in a training batch: {len(todo_batch)}; commentary not yet filed: {len(todo_c)} "
          f"({', '.join(sorted({k for _, k in todo_c}))}); trained but no why shown yet: {len(no_why)}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: show()
    elif a[0] == "sync": sync(); show()
    elif a[0] == "mark": mark(*a[1:])
    else: print(__doc__)
