"""Slow training, one batch at a time.

  python3 batch.py pick N [--seed S]   choose N matches at random from the stored results that have no replay yet (a
                                       random pick keeps the model unbiased; Denning can add matches he wants) and
                                       append them to replays/requests.txt under a "# training batch" comment; pushing
                                       that file starts the "Fetch replays" workflow
  python3 batch.py add                 once fetched: add every stored replay not yet trained on as the next batch in
                                       data/model/batches.json; then run learning.py for the report
Matches from the last day or so may not have replays on gvg.report yet; the workflow skips what it can't fetch."""
import datetime, glob, json, os, random, subprocess, sys
from common import REPO

BATCHES = os.path.join(REPO, "data", "model", "batches.json")
REQ = os.path.join(REPO, "replays", "requests.txt")


def stored():
    try: return set(json.loads(subprocess.check_output(["git", "-C", REPO, "show", "origin/replays:index.json"]))["matches"])
    except subprocess.CalledProcessError: return set()


def pick(n, seed=None):
    have = stored()
    req = open(REQ).read()
    pool = [r["id"] for f in glob.glob(os.path.join(REPO, "data", "matches", "2*.json")) for r in json.load(open(f))
            if r["id"] not in have and r["id"] not in req]
    rnd = random.Random(seed)
    chosen = rnd.sample(sorted(pool), min(n, len(pool)))
    with open(REQ, "a") as fh:
        fh.write(f"# training batch {datetime.date.today()} (random pick)\n" + "".join(c + "\n" for c in chosen))
    return chosen


def add():
    b = json.load(open(BATCHES))
    done = {m for x in b["batches"] for m in x["matches"]}
    new = sorted(stored() - done)
    if new:
        b["batches"].append({"batch": len(b["batches"]), "added": str(datetime.date.today()), "matches": new})
        json.dump(b, open(BATCHES, "w"), indent=1)
    return new


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "pick":
        print(pick(int(a[1]), int(a[a.index("--seed") + 1]) if "--seed" in a else None))
    elif a and a[0] == "add":
        print(add())
    else:
        print(__doc__)
