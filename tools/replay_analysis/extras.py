"""What the trim of a replay leaves out, read from the file kept beside each stored replay
(`<month>/<report id>.x.json.gz` on the `replays` branch, format gvginfo.extras.v1; the layout is documented at the top
of tools/gvgreport/replay_extras.mjs). gvg.report's own records: its flag objects (R-481), its Lord damage record
(R-632, R-634, R-635), what each prot did, degen, interrupt attempts, death and spike-save recaps (R-636 to R-639) and
its energy model (R-664). Agent numbers and the clock are the stored replay's; times here are given in seconds.

    from replaylib import Match
    x = Match.from_branch("<report id>").extras()      # an Extras, read once and kept on the match
    x.flag_objects      [(second, object id, type id, (x, y))]
    x.lord              gvg.report's Lord record as stored, or None
    x.lord_record()     the same as a LordRecord: hits, damage, aggressiveness and Lord health by the second
    x.energy            its energy model as stored, or None where gvg.report has none (before 27 August 2026)

A match whose file cannot be read stops the reading (R-460): every stored match has one, so a missing file is a fault,
never "not in the replay". A part gvg.report did not record (energy in 65 matches) is None, and each reading built on
it says what it does with such a match.

    python3 extras.py <report id>      what the file of one match holds
    python3 extras.py cover            the same counted over every stored match
"""
import bisect, gzip, json, os, subprocess

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FORMAT = "gvginfo.extras.v1"
MIN_VERSION = 2                 # the version every stored match was fetched at (2026-11-24); an older file is read as a fault
BLIND_WORTH = 30                # gvg.report scores a Blind put on the enemy Lord at this, for the team that put it there (found 2026-11-24: with it every team score rebuilds)


class ExtrasMissing(RuntimeError):
    """The file beside a stored replay is not there, is older than MIN_VERSION or is not in the format: a fault (R-460)."""


def path_of(replay_file):
    """`2026-11/<id>.json.gz` -> `2026-11/<id>.x.json.gz`."""
    if not replay_file.endswith(".json.gz"): raise ExtrasMissing(f"extras: {replay_file} is not a stored replay's file name")
    return replay_file[:-len(".json.gz")] + ".x.json.gz"


class LordRecord:
    """gvg.report's own Lord damage record (R-632), by the second. Lord damage is its figure everywhere: what decides
    28:00 is aggressiveness (R-634), raw damage matters only for killing the Lord, and for that the Lord's health is
    its own estimate (R-635). Teams are 1 and 2 as in the replay; `lord_team` is the team whose Lord it is.
      hits(lord_team)             [(second, source agent, damage)]: every hit and every life steal on that Lord by the other
                                  team (a life steal counts as a hit of no damage: gvg.report leaves life steal out of Lord
                                  damage, and so does every figure here; the Lord's health has it)
      damage(lord_team, t0, t1)   damage on that Lord in [t0, t1], seconds; by=agents for those sources only
      aggressiveness(team, t)     the team's aggressiveness by second t: each point of damage to the enemy Lord, 30 for an
                                  attack on him missed through Blind and for a Blind put on him, less 50 for an enchantment
                                  or weapon spell on its own Lord, 300 with Entourage up (the worths are the record's own)
      health(lord_team, t)        (health, maximum) of that Lord at second t, gvg.report's estimate; None where it has no sample of him
      rebuilds()                  {team: (built from the events, gvg.report's own score)}: the two agree within 5 in every
                                  stored match once a Blind put on the enemy Lord counts (found 2026-11-24)"""
    def __init__(self, L):
        self.raw = L
        self.worth = L.get("worth") or {}
        bw = self.worth.get("blind_miss") or BLIND_WORTH
        self.events = sorted(((e[0] / 10, e[1], e[2], e[3] or 0, e[4] or 0, e[5] or 0, bool(e[6]), e[7], e[8], e[9], e[10] or "", e[11]) for e in L.get("events") or [] if e[0] is not None), key=lambda e: e[0])
        self._hits, self._ag = {1: [], 2: []}, {1: [], 2: []}
        for t, lt, kind, amt, blind, cost, ent, src, st_, skill, eff, alive in self.events:
            if lt not in (1, 2): continue
            if kind in ("d", "l") and st_ == 3 - lt: self._hits[lt].append((t, src, amt if kind == "d" else 0.0))
            if kind == "d" and st_ == 3 - lt and (amt or blind): self._ag[st_].append((t, amt + blind))
            elif kind == "condition" and st_ == 3 - lt: self._ag[st_].append((t, bw))
            elif kind == "e" and st_ == lt and cost: self._ag[lt].append((t, -cost))
        self._agt, self._agc = {}, {}
        for tm, v in self._ag.items():
            self._agt[tm] = [x[0] for x in v]; c, run = [], 0.0
            for x in v: run += x[1]; c.append(run)
            self._agc[tm] = c
        self._hp = {int(k): [(r[0] / 10, r[1], r[2]) for r in v] for k, v in (L.get("health") or {}).items()}
        self._hpt = {k: [r[0] for r in v] for k, v in self._hp.items()}
        self.scores = {int(k): v for k, v in (L.get("scores") or {}).items()}
        self.lords = {int(k): v for k, v in (L.get("lords") or {}).items()}

    def hits(self, lord_team): return self._hits.get(lord_team, [])

    def damage(self, lord_team, t0=None, t1=None, by=None):
        return sum(v for t, a, v in self._hits.get(lord_team, []) if (t0 is None or t >= t0) and (t1 is None or t <= t1) and (by is None or a in by))

    def aggressiveness(self, team, t=None):
        c = self._agc.get(team) or []
        if not c: return 0.0
        if t is None: return c[-1]
        i = bisect.bisect_right(self._agt[team], t)
        return c[i - 1] if i else 0.0

    def health(self, lord_team, t):
        v = self._hp.get(lord_team) or []
        if not v: return None
        i = max(bisect.bisect_right(self._hpt[lord_team], t), 1)      # before its first sample (a fifth of a second in) the Lord is as that sample has him
        return (v[i - 1][1], v[i - 1][2])

    def rebuilds(self):
        return {tm: (round(self.aggressiveness(tm), 1), (self.scores.get(tm) or {}).get("aggressiveness")) for tm in (1, 2)}


class Extras:
    def __init__(self, o, where="?"):
        if o.get("format") != FORMAT or (o.get("v") or 0) < MIN_VERSION:
            raise ExtrasMissing(f"extras: {where} is format {o.get('format')!r} version {o.get('v')!r}; {FORMAT} version {MIN_VERSION} or later is read")
        self.o, self.where = o, where
        self.summary = bool(o.get("summary"))                 # gvg.report's summary was there when the file was written (the Lord record, prots, degen, attempts and recaps come from it)
        self.flag_objects = [(r[0] / 10, r[1], r[2], (r[3], r[4])) for r in o.get("flag_objects") or [] if r[0] is not None]
        self.lord = o.get("lord") or None
        self.energy = o.get("energy") or None
        self.agents = o.get("agents") or []                   # the agents the stored replay lacks, numbered on from its own
        self._lord = None

    def lord_record(self):
        """gvg.report's Lord record as a LordRecord. Every stored match has one; a file without it is a fault (R-460)."""
        if self._lord is None:
            if self.lord is None: raise ExtrasMissing(f"extras: {self.where} holds no Lord record (gvg.report's summary was {'there' if self.summary else 'not there'} when it was written)")
            self._lord = LordRecord(self.lord)
        return self._lord

    @classmethod
    def from_branch(cls, report_id, repo=None, entry=None):
        repo = repo or REPO
        if entry is None:
            entry = json.loads(subprocess.check_output(["git", "-C", repo, "show", "origin/replays:index.json"]))["matches"][report_id]
        p = path_of(entry["file"])
        try: raw = subprocess.check_output(["git", "-C", repo, "show", "origin/replays:" + p], stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError: raise ExtrasMissing(f"extras: no file {p} on the replays branch for {report_id} (fetch the branch again, or run \"Fetch replays\")") from None
        return cls(json.loads(gzip.decompress(raw)), p)

    @classmethod
    def load(cls, replay_path):
        p = path_of(replay_path)
        if not os.path.exists(p): raise ExtrasMissing(f"extras: no file {p} beside {replay_path}")
        with gzip.open(p, "rt") as fh: return cls(json.load(fh), p)

    def holds(self):
        """What the file holds, for the cover report: {part: count, or True/False}."""
        o = self.o
        return {"summary": self.summary, "flag objects": len(self.flag_objects), "lord": self.lord is not None,
                "lord events": len((self.lord or {}).get("events") or []), "energy": self.energy is not None,
                "attempts": len(o.get("attempts") or []), "recaps": len(o.get("recaps") or []), "degen": len(o.get("degen") or {}),
                "targets": len(o.get("targets") or []), "received": len(o.get("received") or []), "lord effects": len(o.get("lord_effects") or [])}


if __name__ == "__main__":
    import collections, sys
    a = sys.argv[1:]
    if a and a[0] == "cover":
        idx = json.loads(subprocess.check_output(["git", "-C", REPO, "show", "origin/replays:index.json"]))["matches"]
        c, bad = collections.Counter(), []
        for rid, e in idx.items():
            try: h = Extras.from_branch(rid, entry=e).holds()
            except ExtrasMissing as ex: bad.append(str(ex)); continue
            for k, v in h.items(): c[k] += bool(v)
        print(f"{len(idx)} stored matches; {len(bad)} without a readable file")
        for k, v in c.items(): print(f"  {k:14} in {v}")
        off = []
        for rid, e in idx.items():
            try: rb = Extras.from_branch(rid, entry=e).lord_record().rebuilds()
            except ExtrasMissing: continue
            off += [(rid[:8], e["teams"], tm, b, sc) for tm, (b, sc) in rb.items() if sc is None or abs(b - sc) > 5]
        print(f"  aggressiveness rebuilt from the events is more than 5 off gvg.report's own score for {len(off)} of {2 * (len(idx) - len(bad))} teams", off[:10])
        for b in bad[:20]: print("  " + b)
        sys.exit(1 if bad else 0)
    elif a:
        for k, v in Extras.from_branch(a[0]).holds().items(): print(f"{k:14} {v}")
    else: print(__doc__)
