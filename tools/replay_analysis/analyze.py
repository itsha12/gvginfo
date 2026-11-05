"""Run the whole analysis for one or more matches and write one structured file per match.

Usage:  python3 analyze.py <report id> [...] [--out DIR] [--save-maps]   (default DIR: /tmp/gvginfo-analysis)
        python3 analyze.py --all [--out DIR] [--save-maps]                 every match on the replays branch
--save-maps adds each match's NPC position estimates to data/maps/ (once per match; commit the files if they change).
Output: <DIR>/<report id>.json with format gvginfo.analysis.v1: meta, ENGINE version, build archetypes, state and
scoreboard samples every 5 s, episodes (splits, flag runs and cycles, stand ledger, deaths, fights, monk profiles,
numbers windows, posture), decision points, findings and the edge ledger. Files are regenerated from the replays and
this code, so bump ENGINE when the logic changes."""
import json, os, subprocess, sys
from replaylib import Match
from state import GameState
from scoreboard import Scoreboard
import episodes as E
import fights as F
import rules as R
import decisions as D

ENGINE = 15


def analyze(rid, save_maps=False):
    m = Match.from_branch(rid)
    st = GameState(m, save_maps)
    sb = Scoreboard(st)
    ds = F.deaths(st, sb)
    out = {
        "format": "gvginfo.analysis.v1", "engine": ENGINE, "id": rid,
        "meta": {k: m.o["meta"][k] for k in ("map", "map_id", "match_length_s", "teams", "result") if k in m.o["meta"]},
        "roles": {m.tag[m.team(a)] + " " + m.roles[a]: m.nm(a) for a in m.PL},
        "archetypes": {m.tag[tm]: sb.arch[tm] for tm in st.teams},
        "inferred_caps": m.inferred_caps,
        "state": [st.at(t) for t in range(0, st.end + 1, 5)],
        "scoreboard": [sb.at(t) for t in range(0, st.end + 1, 5)],
        "splits": E.splits(st), "flag_runs": E.flag_runs(st), "stand": E.stand_ledger(st), "flag_cycles": E.flag_cycles(st, sb),
        "deaths": ds, "fights": F.engagements(st, sb, ds), "monks": F.monks(st), "windows": F.windows(st),
        "posture": F.posture(st),
    }
    ep = {k: out[k] for k in ("splits", "flag_runs", "stand", "deaths", "windows", "fights")}
    out["decisions"] = D.decision_points(st, sb, ep)
    out["findings"] = R.findings(st, ep)
    out["ledger"] = R.ledger(st, ep)
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    out = "/tmp/gvginfo-analysis"
    save = "--save-maps" in args
    if save: args.remove("--save-maps")
    if "--out" in args: i = args.index("--out"); out = args[i + 1]; del args[i:i + 2]
    if args == ["--all"]:
        repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        args = list(json.loads(subprocess.check_output(["git", "-C", repo, "show", "origin/replays:index.json"]))["matches"])
    os.makedirs(out, exist_ok=True)
    for rid in args:
        json.dump(analyze(rid, save), open(os.path.join(out, rid + ".json"), "w"), separators=(",", ":"), default=list)
        print("wrote", rid)
