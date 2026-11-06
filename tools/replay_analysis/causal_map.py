"""The causal map (data/model/causal_map.json): render it as a readable page and check it.

Usage:  python3 causal_map.py render     -> knowledge/causal-map.md (the site page "Causal map")
        python3 causal_map.py check      -> links to unknown nodes, nodes nothing explains, loops within one moment
The map is the model's structure: each node's model may only use the links pointing into it (causes measured earlier
in time); the data decides how much each link matters. Denning edits the JSON (or tells Claude); each change goes in
its "log" with a reason."""
import collections, json, os, sys
from common import REPO

PATH = os.path.join(REPO, "data", "model", "causal_map.json")
LAYERS = [("context", "Context (fixed for the match or set by the clock)"), ("allocation", "Allocation and plans (macro)"),
          ("play", "Plays (decisions and micro)"), ("capacity", "Capacities (what a group can do in its fight)"),
          ("result", "Results"), ("score", "Scoreboard and win")]


def load(): return json.load(open(PATH))


def render():
    m = load(); nodes = {x["id"]: x for x in m["nodes"]}
    into = collections.defaultdict(list)
    for l in m["links"]: into[l["to"]].append(l)
    L = ["*Generated from data/model/causal_map.json by tools/replay_analysis/causal_map.py: don't edit this page; tell "
         "Claude or edit the JSON (each change is logged with a reason).*", "",
         f"# Causal map (version {m['version']})", "",
         "What can cause what in a GvG match. Each concept is measured from the replays; the model for each concept may only "
         "use the causes listed under it, measured earlier in time, and the data decides how much each matters. "
         "Status: **hypothesis** (not yet tested), **supported** or **rejected** by data, **mechanical** (a formula). "
         "\"Confirmed\" = Denning has confirmed the reasoning; the size of the effect still comes from data.", ""]
    for layer, title in LAYERS:
        L += [f"## {title}", ""]
        for nid, x in nodes.items():
            if x["layer"] != layer: continue
            L.append(f"### {x['name']} `{nid}`")
            L.append(f"{x['description']}. *Measured: {x['how']}.*")
            groups = collections.OrderedDict()
            for l in into.get(nid, []):
                groups.setdefault((l["why"], l["source"], l["status"], l["confirmed_by_denning"], tuple(l["tactics"])), []).append(nodes[l["from"]]["name"])
            if groups:
                L.append("")
                L.append("Caused by:")
                for (why, src, st, conf, tac), frm in groups.items():
                    L.append(f"- **{', '.join(frm)}**: {why} ({src}{', confirmed' if conf and src != 'Denning' else ''}; {st}"
                             + (f"; {' '.join('`' + t + '`' for t in tac)}" if tac else "") + ")")
            L.append("")
    L += ["## Change log", ""] + [f"- {x['date']}: {x['change']} ({x['by']})" for x in m["log"]]
    out = os.path.join(REPO, "knowledge", "causal-map.md")
    open(out, "w").write("\n".join(L) + "\n")
    return out


def check():
    m = load(); ids = {x["id"] for x in m["nodes"]}
    bad = [l for l in m["links"] if l["from"] not in ids or l["to"] not in ids]
    explained = {l["to"] for l in m["links"]}
    orphans = [x["name"] for x in m["nodes"] if x["id"] not in explained and x["layer"] not in ("context",)]
    print(f"{len(m['nodes'])} nodes, {len(m['links'])} links; unknown nodes in links: {len(bad)}; nothing explains: {orphans}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "render"
    print(render() if cmd == "render" else check())
