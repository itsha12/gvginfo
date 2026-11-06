"""Add gvg.report's player assignments (data/gvgreport/players.json) to the portal's (data/aliases.json).

Denning's own assignments always win:
- a character he already assigned stays with his person;
- a gvg.report player sharing characters with exactly one of his people adds its other (unassigned) characters there;
- a gvg.report player sharing none becomes a new person under gvg.report's name (with " (gvg.report)" added if a
  different person already has that name);
- a gvg.report player whose characters are split between two or more of his people is left alone and listed as a
  conflict for him to decide.
What was added is recorded under "gvgreport_added" in aliases.json ({person: [characters]}), so it can be reviewed or
undone; the Players page keeps that key when it saves.

Usage: python3 tools/gvgreport/merge_players.py [--dry-run]"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def merge(aliases, gr):
    people = aliases.setdefault("people", {})
    added = aliases.setdefault("gvgreport_added", {})
    owner = {c: p for p, cs in people.items() for c in cs}
    conflicts, new_people, extended = [], 0, 0
    for e in gr["players"]:
        chars = [c["name"] for c in e["characters"] if c.get("name")]
        mine = {owner[c] for c in chars if c in owner}
        if len(mine) > 1:
            conflicts.append({"gvg.report player": e["name"], "your people": sorted(mine)}); continue
        free = [c for c in chars if c not in owner]
        if not free: continue
        if mine:
            who = mine.pop(); extended += 1
        else:
            who = e["name"]
            if who in people: who = f"{e['name']} (gvg.report)"
            new_people += 1
        people.setdefault(who, []).extend(free)
        added.setdefault(who, []).extend(free)
        for c in free: owner[c] = who
    return {"new_people": new_people, "extended_people": extended,
            "characters_added": sum(len(v) for v in added.values()), "conflicts": conflicts}


if __name__ == "__main__":
    ap = os.path.join(ROOT, "data", "aliases.json")
    aliases = json.load(open(ap)) if os.path.exists(ap) else {"people": {}}
    gr = json.load(open(os.path.join(ROOT, "data", "gvgreport", "players.json")))
    res = merge(aliases, gr)
    print(json.dumps(res, ensure_ascii=False, indent=1))
    if "--dry-run" not in sys.argv:
        json.dump(aliases, open(ap, "w"), ensure_ascii=False, indent=1); open(ap, "a").write("\n")
