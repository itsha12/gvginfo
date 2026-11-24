"""Compare the plays of two runs of `moments.py all` (the standing check after a change to a record: "compare the
plays with the run before; nothing may differ" but the keys the change is meant to move).

    python3 tools/golden/compare.py <before.json> <after.json> [--skip key,key] [--show N]

A play is matched on its match, kind, team and start (its id ends in its place in the match, which moves when a play
comes or goes). Prints how many plays are the same, changed, gone and new; which keys changed and on how many plays;
and examples of each, with the scenario as it read before and as it reads now. `--skip` leaves keys out at any depth
(for a record a change was meant to move: `--skip lord,aggr,flag_lead`). It reads the two files and nothing else."""
import json, sys, collections, re
a = sys.argv[1:]
skip = set(a[a.index("--skip") + 1].split(",")) if "--skip" in a else set()
show = int(a[a.index("--show") + 1]) if "--show" in a else 12
A, B = json.load(open(a[0])), json.load(open(a[1]))
ids = set(A["matches"]) & set(B["matches"])
print("matches", len(A["matches"]), len(B["matches"]), "common", len(ids), "errors", len(A.get("errors") or {}), len(B.get("errors") or {}), list((B.get("errors") or {}).items())[:3])
def rid_of(p): return p.get("rid") or p.get("match") or p["id"].split("-")[0]
def key(p): return re.sub(r"-\d+$", "", p["id"])          # a play's id ends in its place in the match
def strip(v, top=True):
    if isinstance(v, dict): return {k: strip(x, False) for k, v_ in v.items() for x in [v_] if not (k in skip) and not (top and k == "id")}
    if isinstance(v, list): return [strip(x, False) for x in v]
    return v
def idx(D):
    out = collections.defaultdict(list)
    for p in D["plays"]: out[(p["id"].split("-")[0], p["play"], p.get("tm"), p.get("t0"))].append(p)
    return out
IA, IB = idx(A), idx(B)
print("plays", len(A["plays"]), len(B["plays"]))
gone = [k for k in IA if k not in IB]; new = [k for k in IB if k not in IA]
chg = collections.Counter(); ex = collections.defaultdict(list); same = 0; kindc = collections.Counter()
def paths(x, y, pre=""):
    if isinstance(x, dict) and isinstance(y, dict):
        out = []
        for k in set(x) | set(y):
            if k not in x or k not in y: out.append(pre + k)
            elif x[k] != y[k]: out += paths(x[k], y[k], pre + k + ".")
        return out
    return [pre.rstrip(".")]
for k in IA:
    if k not in IB: continue
    for pa, pb in zip(IA[k], IB[k]):
        sa, sb = strip(pa), strip(pb)
        if sa == sb: same += 1; continue
        ps = sorted(set(re.sub(r"\.\d+(\.|$)", r".#\1", q) for q in paths(sa, sb)))
        kindc[pa["play"]] += 1
        for q in ps: chg[q] += 1
        ex[tuple(ps)].append((k, pa.get("scenario") or "", pb.get("scenario") or ""))
print("same", same, "changed", sum(kindc.values()), dict(kindc)); print("gone", len(gone), collections.Counter(k[1] for k in gone)); print("new", len(new), collections.Counter(k[1] for k in new))
print("changed keys:", chg.most_common(40))
tm_ = lambda t: f"{int(t)//60}:{int(t)%60:02d}" if isinstance(t, (int, float)) else t
names = {r: "%s v %s" % tuple(m["teams"]) for r, m in B["matches"].items()}
full = {r.split("-")[0]: r for r in B["matches"]}
for k in sorted(gone)[:show]: print("  GONE", names.get(full.get(k[0], ""), k[0]), k[1], k[2], tm_(k[3]), (IA[k][0].get("scenario") or "")[:150])
for k in sorted(new)[:show]: print("  NEW ", names.get(full.get(k[0], ""), k[0]), k[1], k[2], tm_(k[3]), (IB[k][0].get("scenario") or "")[:150])
for ps, v in sorted(ex.items(), key=lambda kv: -len(kv[1]))[:show]:
    print(len(v), ps[:6])
    for k, wa, wb in v[:3]:
        print("     ", names.get(full.get(k[0], ""), k[0]), k[1], k[2], tm_(k[3]));
        if wa != wb: print("        was:", wa[:230]); print("        now:", wb[:230])
