"""Run the whole analysis for one or more matches and write one structured file per match.

Usage:  python3 analyze.py <report id> [...] [--out DIR]      (default DIR: /tmp/gvginfo-analysis)
        python3 analyze.py --all [--out DIR]                  every match on the replays branch
Output: <DIR>/<report id>.json with format gvginfo.analysis.v1: meta, ENGINE version, state samples every 5 s, and
episodes (splits, flag runs, stand ledger, deaths, monk profiles, numbers windows, posture). Later layers (findings,
edge ledger, win probability) add keys here. Files are regenerated from the replays and this code, so bump ENGINE when the logic changes."""
import json, os, subprocess, sys
from replaylib import Match
from state import GameState
import episodes as E
import fights as F

ENGINE = 2


def analyze(rid):
    m = Match.from_branch(rid)
    st = GameState(m)
    return {
        "format": "gvginfo.analysis.v1", "engine": ENGINE, "id": rid,
        "meta": {k: m.o["meta"][k] for k in ("map", "map_id", "match_length_s", "teams", "result") if k in m.o["meta"]},
        "roles": {m.tag[m.team(a)] + " " + m.roles[a]: m.nm(a) for a in m.PL},
        "state": [st.at(t) for t in range(0, st.end + 1, 5)],
        "splits": E.splits(st), "flag_runs": E.flag_runs(st), "stand": E.stand_ledger(st),
        "deaths": F.deaths(st), "monks": F.monks(st), "windows": F.windows(st), "posture": F.posture(st),
    }


if __name__ == "__main__":
    args = sys.argv[1:]
    out = "/tmp/gvginfo-analysis"
    if "--out" in args: i = args.index("--out"); out = args[i + 1]; del args[i:i + 2]
    if args == ["--all"]:
        repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        args = list(json.loads(subprocess.check_output(["git", "-C", repo, "show", "origin/replays:index.json"]))["matches"])
    os.makedirs(out, exist_ok=True)
    for rid in args:
        json.dump(analyze(rid), open(os.path.join(out, rid + ".json"), "w"), separators=(",", ":"), default=list)
        print("wrote", rid)
