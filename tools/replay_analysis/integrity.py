"""Data integrity: checks every replay before anything learns from it, repairs what can be repaired, and says what
can't be trusted. Runs inside Match() on load, so every layer sees the same repaired match.

Checks (each recorded in m.o["integrity"]):
- length: the recorded match length against the last event and a Lord's death (RACK v hdm 1f65fd3b was stored as
  2:30 but runs to 17:18). The match ends at the first Lord death, else at the later of the recorded length and the
  last event. The recorded value is kept as meta.match_length_recorded_s.
- lord_damage: a Lord that died with no recorded damage on it means the attackers' Lord damage wasn't observed; that
  team's Lord damage is then unknown (None), not zero (OG v cope 29b7eca0, Men v RACK 45cf6756).
- roster: pit NPCs only appear in a replay once something touches them, so an untouched pit looked empty (winners
  "lost" their Bodyguard in 19 of 30 matches). Every pit starts with the standard roster (ROSTER; Denning) and the
  NPCs never seen are added as alive all match (state.MapGeo, counted in integrity.roster_added).
- window: gvg.report's observed match clock window and joined-mid-match flag, for reference.
- exclude: a match is left out of training when a problem can't be repaired (EXCLUDE_IF); none so far.

Usage:  python3 integrity.py        every replay: what was found and repaired; writes data/model/integrity.json"""
import json, os, subprocess, sys
from common import REPO

# Standard pit roster (Denning): 2 knights, 2 archers, 1 Bodyguard, 1 Guild Lord; Isle of Solitude has a third archer.
ROSTER = {"knight": 2, "archer": 2, "bodyguard": 1, "guild_lord": 1}
EXTRA_ARCHER_MAPS = {"542"}            # Isle of Solitude
OUT = os.path.join(REPO, "data", "model", "integrity.json")


def roster(map_id):
    r = dict(ROSTER)
    if str(map_id) in EXTRA_ARCHER_MAPS: r["archer"] += 1
    return r


def repair(o):
    """Repairs o in place and records what it found in o["integrity"]."""
    meta, ev, agents = o["meta"], o.get("ev", []), o.get("agents", [])
    rec = meta.get("match_length_s") or 0
    lords = {i: a.get("team") for i, a in enumerate(agents) if a.get("npc") == "guild_lord"}
    lord_death = min((e[0] / 10 for e in ev if e[1] == "dt" and e[2] in lords), default=None)
    last = max((e[0] / 10 for e in ev), default=0)
    end = int(lord_death + 1) if lord_death is not None else int(max(rec, last))
    out = {"length": {"recorded_s": rec, "last_event_s": round(last), "lord_death_s": round(lord_death) if lord_death else None,
                      "used_s": end, "repaired": abs(end - rec) > 15}}
    if out["length"]["repaired"]:
        meta.setdefault("match_length_recorded_s", rec)
        meta["match_length_s"] = end
    hit = {i: sum(1 for e in ev if e[1] == "dm" and e[3] == i) for i in lords}
    dead = {i for i in lords if any(e[1] == "dt" and e[2] == i for e in ev)}
    # the team attacking a Lord is the other team
    out["lord_damage_unobserved"] = sorted({3 - lords[i] for i in dead if hit[i] == 0 and lords[i] in (1, 2)})
    q = o.get("quality") or {}
    out["window"] = {"observed": q.get("match_clock_window_observed"), "joined_mid_match": meta.get("joined_mid_match")}
    out["roster_added"] = {}            # filled by state.MapGeo
    out["exclude"] = EXCLUDE_IF(out)
    o["integrity"] = out
    return out


def EXCLUDE_IF(chk):
    """Reasons a match can't be used for training (empty = usable)."""
    why = []
    if chk["window"].get("joined_mid_match"): why.append("observer joined mid match")
    return why


_USABLE = {}
def usable(ids):
    """ids without the matches integrity leaves out of training (cached)."""
    key = tuple(ids)
    if key not in _USABLE:
        bad = excluded(ids); _USABLE[key] = [x for x in ids if x not in bad]
    return _USABLE[key]


def excluded(ids):
    """The subset of report ids that integrity leaves out of training, with reasons."""
    from replaylib import Match
    out = {}
    for rid in ids:
        r = Match.from_branch(rid).o["integrity"]["exclude"]
        if r: out[rid] = r
    return out


if __name__ == "__main__":
    from replaylib import Match
    from state import GameState
    idx = json.loads(subprocess.check_output(["git", "-C", REPO, "show", "origin/replays:index.json"]))["matches"]
    res = {}
    for rid, v in idx.items():
        st = GameState(Match.from_branch(rid))
        chk = st.m.o["integrity"]
        res[rid] = chk
        flags = []
        if chk["length"]["repaired"]: flags.append(f"length {chk['length']['recorded_s']}s -> {chk['length']['used_s']}s")
        if chk["lord_damage_unobserved"]: flags.append("Lord damage unobserved for " + ",".join(st.m.tag[t] for t in chk["lord_damage_unobserved"]))
        add = {st.m.tag[int(t)]: n for t, n in chk["roster_added"].items() if n}
        if add: flags.append(f"NPCs added {add}")
        if chk["exclude"]: flags.append("EXCLUDED: " + "; ".join(chk["exclude"]))
        print(rid[:8], " v ".join(v["teams"]), "|", "; ".join(flags) or "ok")
    json.dump(res, open(OUT, "w"), indent=1)
    print("wrote", OUT)
