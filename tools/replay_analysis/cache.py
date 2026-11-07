"""Shared cache for the analysis engine: each match's prepared data and every "without this match" model, built once and
reused by every layer (learning report, values, usual play, why chains, event explanations).

Two kinds of entry, both keyed so a stale entry can never be read:
- Prepared data (per match): match tables, node rows, fight state, value events. Keyed by the match id and a hash of
  the engine code they are built from (the analysis modules they import, found automatically) plus the data files
  they read (strength, lineup, context). Change the engine and the old entries are simply not found.
- Held-out models ("without this match"): the win model and node models fitted on every training match except one.
  Keyed by the kind, the match left out, a hash of the training set and a hash of the model code and corrections.
  A new batch changes the training set, so every held-out model is refitted once per batch, then reused.

Where: ~/.cache/gvginfo (or $GVG_CACHE). Prepared data and the fight-state predictions (fightstate.py) can be kept
between sessions on the repo's `cache` branch (`sync pull` at the start of a session, `sync push` after building), so a
new session (or a rerun of the Train batch workflow on the same matches) does not rebuild them.

Usage:  python3 cache.py warm [--jobs N]     build prepared data and the held-out win models (one per group of matches,
                                             FOLDS) for the current batches, in parallel (once per batch); deaths
                                             models are fitted when a why chain first needs them
        python3 cache.py sync pull|push      fetch or store prepared data on the `cache` branch
        python3 cache.py info                what is cached and the current keys
        python3 cache.py clear [fits|prepared|all]
In code:  cache.prepared(kind, rid, build)   -> JSON value (build() called only on a miss)
          cache.heldout(kind, rid, ids, fit) -> fitted model (fit(training ids) called only on a miss)"""
import gzip, hashlib, json, modulefinder, os, pickle, shutil, subprocess, sys, tarfile, time
from common import REPO

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("GVG_CACHE", os.path.expanduser("~/.cache/gvginfo"))
DATA_DEPS = ["data/model/strength.json", "data/model/lineup.json", "data/model/context.json",
             "data/model/integrity.json", "data/review_labels.json"]
FIT_DEPS = ["data/model_corrections.json"]
# the entry modules each kind of prepared data is built from; their local imports are followed automatically
PREPARED_FROM = {"table": ["features.py", "model.py"], "rows": ["nodes.py"], "events": ["values.py"],
                 "analysis": ["analyze.py"], "power_bench": ["tq.py"], "run_bench": ["tq.py"], "mes_bench": ["chain.py"], "eventlayer": ["eventlayer.py"]}
FIT_FROM = {"wp": ["model.py"], "node": ["nodes.py"]}
_KEYS = {}


NOT_ENGINE = {"cache.py", "status.py"}      # bookkeeping only: changing them never changes a result


def _local_deps(entries):
    """Every analysis module the entry modules import, directly or not (bookkeeping modules left out)."""
    seen, todo = set(), list(entries)
    while todo:
        f = todo.pop()
        if f in seen or not os.path.exists(os.path.join(HERE, f)): continue
        seen.add(f)
        mf = modulefinder.ModuleFinder(path=[HERE])
        try: mf.load_file(os.path.join(HERE, f))
        except Exception: pass
        for name in mf.badmodules.keys() | mf.modules.keys():
            if os.path.exists(os.path.join(HERE, name + ".py")): todo.append(name + ".py")
    return sorted(seen - NOT_ENGINE)


def _hash_files(files):
    h = hashlib.sha1()
    for f in files:
        p = f if os.path.isabs(f) else os.path.join(HERE if f.endswith(".py") else REPO, f)
        h.update(f.encode())
        if os.path.exists(p): h.update(open(p, "rb").read())
    return h.hexdigest()[:12]


def code_key(kind):
    """Hash of the code (and data files) a kind of prepared data depends on."""
    if kind not in _KEYS:
        _KEYS[kind] = _hash_files(_local_deps(PREPARED_FROM[kind]) + DATA_DEPS)
    return _KEYS[kind]


def fit_key(kind):
    k = "fit_" + kind
    if k not in _KEYS: _KEYS[k] = _hash_files(_local_deps(FIT_FROM[kind]) + DATA_DEPS + FIT_DEPS)
    return _KEYS[k]


def ids_key(ids): return hashlib.sha1(",".join(sorted(ids)).encode()).hexdigest()[:12]


def _path(*parts):
    p = os.path.join(ROOT, *parts); os.makedirs(os.path.dirname(p), exist_ok=True); return p


def prepared(kind, rid, build, sub=None):
    """Prepared data for one match (sub: a variant name, e.g. a node), built on a miss and saved gzipped."""
    name = f"{rid}.json.gz" if sub is None else f"{sub}_{rid}.json.gz"
    p = _path("prepared", kind, code_key(kind), name)
    if os.path.exists(p):
        try:
            with gzip.open(p, "rt") as fh: return json.load(fh)
        except (OSError, ValueError): pass
    v = build()
    tmp = p + f".{os.getpid()}.tmp"
    with gzip.open(tmp, "wt") as fh: json.dump(v, fh, separators=(",", ":"), default=list)
    v = json.loads(json.dumps(v, default=list))       # same value on a hit and on a miss
    os.replace(tmp, p)
    return v


FOLDS = 10     # held-out models: matches split into 10 fixed groups; 0 = leave one match out (slower, same accuracy)
# Measured 2026-11-06 on 61 matches: leave-one-out 78.2% accuracy, log loss 0.601; 10 groups 77.6%, 0.546. Every match is
# still explained by a model that never saw it; 10 fits per batch instead of one per match.


def fold_of(rid, k=FOLDS):
    """A match's fixed group (from its id, so it never changes as batches are added)."""
    return int(hashlib.sha1(rid.encode()).hexdigest(), 16) % k


def heldout_train(rid, ids, k=FOLDS):
    """The training set for explaining rid: every match outside rid's group (or every match but rid with k=0)."""
    if not k or rid not in ids: return [x for x in ids if x != rid]
    f = fold_of(rid, k)
    return [x for x in ids if fold_of(x, k) != f]


def heldout(kind, rid, ids, fit, sub=None, per_match=False):
    """A model fitted without rid (without rid's whole group of matches, see FOLDS), fitted once per training set and
    code version, then reused. per_match: the stored value is specific to rid (e.g. a series computed for it)."""
    train = heldout_train(rid, ids)
    shared = FOLDS and rid in ids and not per_match
    name = f"{sub + '_' if sub else ''}{('fold%d' % fold_of(rid)) if shared else rid}.pkl"
    p = _path("fits", kind, fit_key(kind), ids_key(train), name)
    if os.path.exists(p):
        try: return pickle.load(open(p, "rb"))
        except Exception: pass
    v = fit(train)
    tmp = p + f".{os.getpid()}.tmp"
    pickle.dump(v, open(tmp, "wb")); os.replace(tmp, p)
    return v


def full(kind, ids, fit, sub=None):
    """A model fitted on all of ids (cached the same way)."""
    name = f"{sub + '_' if sub else ''}all.pkl"
    p = _path("fits", kind, fit_key(kind), ids_key(ids), name)
    if os.path.exists(p):
        try: return pickle.load(open(p, "rb"))
        except Exception: pass
    v = fit(list(ids)); pickle.dump(v, open(p, "wb")); return v


# ---- building everything for a batch, in parallel
def _ids():
    import model as M
    return [m for b in M.batches() for m in b["matches"]]


def _rows_one(rid):
    import nodes as N
    for node in list(N.DESC) + ["deaths_all"]: N.node_rows(node, rid)
    return rid


def _table_one(rid):
    import model as M, values as V
    M.match_table(rid); V._events(rid)
    return rid


def _fit_one(args):
    kind, rid = args
    import model as M, nodes as N
    ids = _ids()
    if kind == "wp": M.WPModel.heldout(ids, rid)
    else: N.heldout_node(kind, ids, rid)
    return kind, rid


def warm(jobs=None, kinds=("wp",)):
    from multiprocessing import Pool
    ids = _ids(); jobs = jobs or os.cpu_count() or 2
    t = time.time()
    import fightstate
    with Pool(jobs) as p:
        for _ in p.imap_unordered(_rows_one, ids): pass
    fightstate.build(ids)                       # tables read the fight state, so it comes before them
    with Pool(jobs) as p:
        for _ in p.imap_unordered(_table_one, ids): pass
    print(f"prepared data: {len(ids)} matches in {time.time() - t:.0f} s")
    t = time.time()
    reps = {}                  # one match per group is enough: the group shares its model
    for r in ids: reps.setdefault(fold_of(r) if FOLDS else r, r)
    with Pool(jobs) as p:
        n = sum(1 for _ in p.imap_unordered(_fit_one, [(k, r) for k in kinds for r in reps.values()]))
    print(f"held-out models: {n} in {time.time() - t:.0f} s")


# ---- keeping prepared data between sessions (branch `cache`, one tarball per code version and kind)
def sync(direction):
    work = _path("branch", ".keep"); work = os.path.dirname(work)
    def git(*a, **k): return subprocess.run(["git", "-C", REPO, *a], check=k.get("check", True), capture_output=True, text=True)
    if direction == "pull":
        if git("fetch", "--depth", "1", "origin", "+cache:refs/remotes/origin/cache", check=False).returncode: print("no cache branch yet"); return
        names = git("ls-tree", "--name-only", "origin/cache").stdout.split()
        got = 0
        for kind in PREPARED_FROM:
            name = f"{kind}-{code_key(kind)}.tar.gz"
            if name not in names: continue
            raw = subprocess.run(["git", "-C", REPO, "show", f"origin/cache:{name}"], check=True, capture_output=True).stdout
            p = os.path.join(work, name); open(p, "wb").write(raw)
            with tarfile.open(p) as tf: tf.extractall(os.path.join(ROOT, "prepared", kind), filter="data")
            got += 1
        # the fight-state predictions for the current training set and death-model code (fightstate.py)
        import fightstate
        d = fightstate._dir(); name = "fightstate-" + "-".join(d.split(os.sep)[-2:]) + ".tar.gz"
        if name in names:
            raw = subprocess.run(["git", "-C", REPO, "show", f"origin/cache:{name}"], check=True, capture_output=True).stdout
            p = os.path.join(work, name); open(p, "wb").write(raw)
            os.makedirs(d, exist_ok=True)
            with tarfile.open(p) as tf: tf.extractall(d, filter="data")
            got += 1
        print(f"pulled {got} kinds of prepared data for the current engine")
    else:
        files = {}
        for kind in PREPARED_FROM:
            d = os.path.join(ROOT, "prepared", kind, code_key(kind))
            if not os.path.isdir(d) or not os.listdir(d): continue
            name = f"{kind}-{code_key(kind)}.tar.gz"; p = os.path.join(work, name)
            with tarfile.open(p, "w:gz") as tf: tf.add(d, arcname=code_key(kind))
            files[name] = p
        import fightstate
        d = fightstate._dir()
        if os.path.isdir(d) and os.listdir(d):
            name = "fightstate-" + "-".join(d.split(os.sep)[-2:]) + ".tar.gz"; p = os.path.join(work, name)
            with tarfile.open(p, "w:gz") as tf:
                for f in os.listdir(d): tf.add(os.path.join(d, f), arcname=f)
            files[name] = p
        if not files: print("nothing to push"); return
        # one commit holding only the current versions (older versions are dropped), as an orphan branch
        env = dict(os.environ, GIT_INDEX_FILE=os.path.join(work, "index"))
        if os.path.exists(env["GIT_INDEX_FILE"]): os.remove(env["GIT_INDEX_FILE"])
        for name, p in files.items():
            sha = subprocess.run(["git", "-C", REPO, "hash-object", "-w", p], check=True, capture_output=True, text=True).stdout.strip()
            subprocess.run(["git", "-C", REPO, "update-index", "--add", "--cacheinfo", f"100644,{sha},{name}"], env=env, check=True)
        tree = subprocess.run(["git", "-C", REPO, "write-tree"], env=env, check=True, capture_output=True, text=True).stdout.strip()
        commit = subprocess.run(["git", "-C", REPO, "commit-tree", tree, "-m", "Prepared match data for the current engine"],
                                check=True, capture_output=True, text=True).stdout.strip()
        r = git("push", "-f", "origin", f"{commit}:refs/heads/cache", check=False)
        print("pushed" if r.returncode == 0 else "push failed: " + r.stderr[-300:], ", ".join(files))


def info():
    for kind in PREPARED_FROM:
        d = os.path.join(ROOT, "prepared", kind, code_key(kind))
        n = len(os.listdir(d)) if os.path.isdir(d) else 0
        print(f"prepared {kind:<11} key {code_key(kind)}: {n} files")
    for kind in FIT_FROM:
        d = os.path.join(ROOT, "fits", "node" if kind == "node" else kind)
        print(f"fits {kind:<4} key {fit_key(kind)}")
    fits = os.path.join(ROOT, "fits")
    if os.path.isdir(fits):
        n = sum(len(f) for _, _, f in os.walk(fits)); print(f"held-out models stored: {n}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["warm"]: warm(int(a[a.index("--jobs") + 1]) if "--jobs" in a else None)
    elif a[:1] == ["sync"]: sync(a[1])
    elif a[:1] == ["info"]: info()
    elif a[:1] == ["clear"]:
        what = a[1] if len(a) > 1 else "all"
        for d in (["fits", "prepared"] if what == "all" else [what]): shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)
    else: print(__doc__)
