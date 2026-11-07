"""One match as a single time-ordered list of events, for lining up commentary and comms with match time (they have no
timestamps: anchors are the kills, captures, boosts, NPC losses and resurrections they mention).

Each line: match time, team, what (deaths with role and character, captures, boosts, pit NPCs lost, splits starting,
fights and wipes, Lord damage per minute), plus the base res every two minutes.

Usage:  python3 timeline.py <report id> [--people]     --people adds each character's person name from aliases.json
In code: events(rid) -> [(t, team, text)]."""
import json, os, sys
from common import REPO


def clock(t): return f"{int(t // 60)}:{int(t % 60):02d}"


def events(rid, people=False):
    import events as EV
    a = EV.analysis(rid)
    who = {}
    if people:
        al = json.load(open(os.path.join(REPO, "data", "aliases.json")))
        who = {c: p for p, cs in al["people"].items() for c in cs}
    roles = a["roles"]           # "TAG Role" -> character
    def nm(tag, role):
        c = roles.get(f"{tag} {role}", "")
        return f"{role} ({c}{', ' + who[c] if c in who else ''})" if c else role
    out = []
    for d in a["deaths"]:
        out.append((d["t"], d["team"], f"death {nm(d['team'], d['victim'])} at {d.get('zone')} {d.get('numbers')}"))
    for l in a["ledger"]:
        if l["edge"] == "NPC lost": out.append((l["t"], l["team"], f"lost {l['what']} ({l['cause']})"))
        elif l["edge"] == "boost": out.append((l["t"], l["team"], f"morale boost ({l.get('what')})"))
        elif l["edge"] == "Lord damage dealt": out.append((l["t"], l["team"], f"Lord damage dealt this minute {l['what']}"))
    for c in a["flag_cycles"]:
        out.append((c["own_cap"], c["team"], f"captured by {c.get('capper')} ({c.get('cap_delay')} s after the enemy)"))
    for s in a["splits"]:
        out.append((s["start"], s["team"], f"split {s['kind']} {s['members']} until {clock(s['end'])}"))
    for f in a["fights"]:
        if f.get("wipe"): out.append((f["start"], f["team"], f"fight lost, wipe ({f.get('local_numbers')})"))
    for t in range(120, int(a["meta"].get("match_length_s") or 0) + 1, 120): out.append((t, "", "base res"))
    return sorted(out, key=lambda x: (x[0], x[1]))


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit()
    rid = a[0]
    if len(rid) < 36:
        import events as EV
        rid = EV._rid(rid)
    for t, tm, txt in events(rid, "--people" in a): print(f"{clock(t):>6} {tm:<6} {txt}")
