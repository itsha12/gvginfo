"""A digest of the plays of a run of `moments.py all`, so that the next run can be compared with it without the old run's file, and without
reading the old commit again (a full run's plays file is near a gigabyte and is not kept; until 2026-11-27 the comparison meant a second full run).

    python3 tools/golden/digest.py make  <plays.json> <digest.json>     one short hash of each match's plays and of its moments
    python3 tools/golden/digest.py check <plays.json> <digest.json>     which matches' plays or moments differ from the digest; matches the
                                                                        digest does not hold are counted and not compared

A play is hashed without its id (which ends in its place in the match), as `compare.py` matches plays. Where a match differs, read both runs of that
match with `compare.py` (the development set, or `moments.py all` on those ids alone). The digest of the last full run is kept on the engine branch as
`data/model/plays_digest.json`: check against it, then make it again. It reads the files it is given and nothing else."""
import collections, hashlib, json, re, sys


def digest(path):
    D = json.load(open(path))
    h = lambda rows: hashlib.sha1(json.dumps(sorted(json.dumps(r, sort_keys=True) for r in rows)).encode()).hexdigest()[:16]
    plays, recs = collections.defaultdict(list), collections.defaultdict(list)
    for p in D["plays"]: plays[p["id"].split("-")[0] if "rid" not in p else p["rid"]].append({k: v for k, v in p.items() if k != "id"})
    for r in D["records"]: recs[r["rid"]].append(r)
    by8 = {r[:8]: r for r in D["matches"]}
    out = {}
    for rid in sorted(D["matches"]):
        P = plays.get(rid) or plays.get(rid[:8]) or []
        out[rid] = {"plays": len(P), "plays_hash": h(P), "moments": len(recs.get(rid, [])), "moments_hash": h(recs.get(rid, []))}
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 3 and a[0] == "make":
        d = digest(a[1])
        json.dump({"about": "One hash of each match's plays and moments, from the last run kept as the yardstick: tools/golden/digest.py.", "matches": d}, open(a[2], "w"), indent=0)
        print(f"digest of {len(d)} matches, {sum(v['plays'] for v in d.values()):,} plays, {sum(v['moments'] for v in d.values()):,} moments: {a[2]}")
    elif len(a) == 3 and a[0] == "check":
        new, old = digest(a[1]), json.load(open(a[2]))["matches"]
        both = [r for r in new if r in old]
        dp = [r for r in both if (new[r]["plays"], new[r]["plays_hash"]) != (old[r]["plays"], old[r]["plays_hash"])]
        dm = [r for r in both if (new[r]["moments"], new[r]["moments_hash"]) != (old[r]["moments"], old[r]["moments_hash"])]
        print(f"{len(both)} matches compared ({sum(new[r]['plays'] for r in both):,} plays); {len(new) - len(both)} in this run and not in the digest, {len([r for r in old if r not in new])} in the digest and not in this run")
        print(f"plays differ in {len(dp)} matches" + (": " + ", ".join(f"{r[:8]} ({old[r]['plays']} to {new[r]['plays']})" for r in dp[:20]) if dp else "") + f"; moments differ in {len(dm)}" + (": " + ", ".join(r[:8] for r in dm[:20]) if dm else ""))
        sys.exit(1 if dp or dm else 0)
    else: print(__doc__)
