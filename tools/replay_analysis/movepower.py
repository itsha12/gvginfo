"""Snare and speed power (Denning, after Bounty's and Nick's commentary): how much a bar can slow enemies and speed up
its own player, as single numbers, so a collapse, a flag run or a split decision can weigh how strong the snares
really are, not just whether a snare skill is on a bar.

Per skill, at the player's attribute rank (data/matches attrs; rank 12 when unknown):
  snare power  = slow fraction x seconds slowed per use x targets x uses per minute
                 (Crippled = 50% slower; hex snares from their text, e.g. Ice Spikes 66%; seconds per use capped at the
                 recharge for one target; adjacent = 1.5 targets, nearby or in an area = 2; adrenal skills recharge
                 about 1.4 s per adrenaline point). Unit: slowed target-seconds per minute (at full slow).
  speed power  = speed bonus x seconds per use x uses per minute (Dash 50% for 3 s every 12 s ...).
  escapes      = Shadow Step skills (Return counts here, never as a snare: Denning).
Measured check (`python3 movepower.py bench`, data/benchmarks/snare_measured.json): for every hex snare (Siphon
Speed, Ice Spikes, Deep Freeze ...), the slowed target-seconds each finished use actually produced in the stored
replays, removal included (a hex snare removed at once counts for little). With 15+ uses measured, the measured figure
replaces the formula's seconds x targets. Crippled can't be measured this way: the replays record it only now and
then (e.g. Team v push: 12 Caltrops uses, no Crippled recorded from them), so condition snares keep the formula.

In code: player_power(m, a) -> {"snare", "speed", "escapes"}; skill_power(record, rank) -> same for one skill."""
import collections, functools, glob, json, math, os, re, subprocess, sys
from common import REPO

BENCH = os.path.join(REPO, "data", "benchmarks", "snare_measured.json")
NOT_SNARE = {"Return"}                # an escape (Denning)
# Denning (session 4u): an area snare is worth no more than a single-target one (rarely is more than one player
# snared), so every snare counts one target; what a snare is worth is how long it keeps one player slowed, with its
# recharge (uptime) taken into account
TARGETS = {}
DEFAULT_RANK = 12
MIN_MEASURED = 15
RECORDED_MIN = 0.5       # condition snares: share of uses with a recorded Crippled before the measured figure is trusted


def _num(x):
    try: return float(str(x).replace("¼", ".25").replace("½", ".5").replace("¾", ".75"))
    except (TypeError, ValueError): return None


def _recharge(s):
    r = _num(s.get("recharge"))
    if r: return r
    a = _num(s.get("adrenaline"))
    return a * 1.4 if a else None


def _duration(s, rank, prefer):
    progs = s.get("prog") or []
    for p in progs:
        if prefer and prefer in p.get("name", "").lower(): return p["values"][min(rank, len(p["values"]) - 1)]
    for p in progs:
        if "duration" in p.get("name", "").lower(): return p["values"][min(rank, len(p["values"]) - 1)]
    d = s.get("desc") or ""
    m = re.search(r"(\d+)\.\.(\d+) seconds", d)
    if m:
        lo, hi = int(m.group(1)), int(m.group(2)); return lo + (hi - lo) * min(rank, 15) / 15
    m = re.search(r"(\d+) seconds", d)
    return int(m.group(1)) if m else None


def is_snare(s):
    c = set(s.get("causes") or [])
    return s.get("name") not in NOT_SNARE and bool({"Crippled", "Decreased Movement Speed"} & c)


def slow_fraction(s):
    c = set(s.get("causes") or []); f = 0.0
    if "Crippled" in c: f = 0.5
    m = re.search(r"(\d+)% slower", s.get("desc") or "")
    if "Decreased Movement Speed" in c and m: f = max(f, int(m.group(1)) / 100)
    return f


def targets(s):
    return max([TARGETS.get(x.lower(), 1.0) for x in (s.get("aoe") or [])] or [1.0])


@functools.lru_cache(maxsize=1)
def _measured():
    try: return json.load(open(BENCH)).get("skills", {})
    except (OSError, ValueError): return {}


def skill_power(s, rank=DEFAULT_RANK):
    out = {"snare": 0.0, "speed": 0.0, "escapes": 0}
    if not s: return out
    rech = _recharge(s)
    c = set(s.get("causes") or [])
    if "Shadow Step" in c: out["escapes"] = 1
    if not rech: return out
    if is_snare(s):
        dur = _duration(s, rank, "crippled") or 0
        per_use = min(dur, rech) * targets(s)
        ms = _measured().get(s["name"])
        # measured once 15+ uses; a condition snare only where the replays record its Crippled on most uses (some skills'
        # Crippled is recorded every time, e.g. Pin Down; others almost never, e.g. Hamstring: those keep the formula)
        hexs = "Hex" in (s.get("type") or "")
        if ms and ms.get("uses", 0) >= MIN_MEASURED and (ms.get("secs_per_use") or 0) > 0 and (hexs or (ms.get("recorded_share") or 0) >= RECORDED_MIN):
            per_use = min(ms["secs_per_use"], rech)      # uptime on one player can't pass 100% (Denning, session 4u)
        out["snare"] = round(slow_fraction(s) * per_use * 60 / rech, 1)
    m = re.search(r"(\d+)% faster", s.get("desc") or "")
    if "Increased Movement Speed" in c and m:
        dur = _duration(s, rank, None) or 0
        out["speed"] = round(int(m.group(1)) / 100 * min(dur, rech) * 60 / rech, 1)
    return out


@functools.lru_cache(maxsize=1)
def _ranks():
    """{(match id, character): {attribute: rank}} from the match records."""
    out = {}
    for f in glob.glob(os.path.join(REPO, "data", "matches", "20*.json")):
        d = json.load(open(f))
        for mt in (d["matches"] if isinstance(d, dict) else d):
            for p in mt.get("players") or []:
                if p.get("attrs"): out[(mt["id"], p["n"])] = p["attrs"]
    return out


_PP = {}
def player_power(m, a):
    """Snare, speed and escape power of player a's bar (memoized per match and player: called for every row)."""
    k = (m.o["meta"]["id"], a)
    if k not in _PP: _PP[k] = _player_power(m, a)
    return _PP[k]


def _player_power(m, a):
    from buildfeat import _skills
    S = _skills(); rid = m.o["meta"]["id"]
    attrs = _ranks().get((rid, m.nm(a)), {})
    out = {"snare": 0.0, "speed": 0.0, "escapes": 0}
    for b in m.A[a].get("bar", []):
        s = S.get(m.sk(b)) if b else None
        if not s: continue
        p = skill_power(s, attrs.get(s.get("attr"), DEFAULT_RANK))
        for k in out: out[k] += p[k]
    return {k: round(v, 1) if isinstance(v, float) else v for k, v in out.items()}


_SB = {}
def speed_bonus(m, a):
    k = (m.o["meta"]["id"], a)
    if k not in _SB: _SB[k] = _speed_bonus(m, a)
    return _SB[k]


def _speed_bonus(m, a):
    """The bar's average movement bonus while running (fraction): speed power / 60 (a 50% stance up a quarter of the
    time = 12.5%), capped at the bar's biggest single bonus (speed boosts don't add up; the strongest applies)."""
    from buildfeat import _skills
    S = _skills(); top = 0.0
    for b in m.A[a].get("bar", []):
        s_ = S.get(m.sk(b)) if b else None
        mm = re.search(r"(\d+)% faster", (s_ or {}).get("desc") or "") if s_ and "Increased Movement Speed" in (s_.get("causes") or []) else None
        if mm: top = max(top, int(mm.group(1)) / 100)
    return round(min(player_power(m, a)["speed"] / 60, top), 3)


def carry_speed(m, a, base):
    """A carrier's fastest expected carry speed from its bar (Denning: the runner's speed skills set the minimum time
    required to capture): the average carry speed times one plus its speed bonus."""
    return base * (1 + speed_bonus(m, a))


def powers(m):
    """{agent: player_power} for every player of a match."""
    return {a: player_power(m, a) for a in m.PL}


def near(m, P, team, x, y, t10, r=1300, kind="snare"):
    """Total power of team's live players within r of (x, y) at time t10 (tenths of a second)."""
    tot = 0.0
    for a in m.PL:
        if m.team(a) != team: continue
        s = m.snap(a, t10)
        if s and m.alive(s) and math.dist((s["x"], s["y"]), (x, y)) <= r: tot += P[a][kind]
    return round(tot, 1)


# ---------------------------------------------------------------- measured check
def _bench_one(rid):
    from replaylib import Match
    from buildfeat import _skills
    S = _skills(); m = Match.from_branch(rid); out = collections.defaultdict(lambda: [0, 0.0, 0])
    eff = m.o.get("effects") or []
    hexes = [e for e in eff if e[2] == "h" and e[0] is not None]
    cripples = [e for e in eff if e[2] == "c" and e[0] is not None and (e[7] or "") == "crippled"]
    end_t = max((e[0] for e in m.o.get("ev") or [] if e[0] is not None), default=0)
    open_ = {}
    for e in m.o.get("ev") or []:
        if e[1] == "cs": open_[e[2]] = e[4]
        elif e[1] in ("cf", "ca") and e[2] in open_:      # attack skills end on "activated", spells on "finished"
            sid = open_.pop(e[2]); s = S.get(m.sk(sid))
            if not s or not is_snare(s) or e[2] not in m.PL: continue
            t = e[0]; caster = e[2]; foe = 3 - m.team(caster); secs = 0.0
            # hex snares: the hex's interval; condition snares: the Crippled interval the skill caused (recorded with its
            # skill and caster in the newer replays; session 4u)
            if "Hex" in (s.get("type") or ""): cand = [h for h in hexes if h[3] == sid]
            elif "Crippled" in (s.get("causes") or []): cand = [c for c in cripples if c[3] == sid]
            else: continue
            for x in cand:
                if not (t - 3 <= x[0] <= t + 15) or m.team(x[5]) != foe: continue
                if x[4] not in (caster, None): continue
                secs += ((x[1] if x[1] is not None else min(end_t, x[0] + 200)) - x[0]) / 10
            out[s["name"]][0] += 1; out[s["name"]][1] += secs; out[s["name"]][2] += int(secs > 0)
        elif e[1] in ("ir", "cx"): open_.pop(e[2], None)
    return dict(out)


def bench():
    from multiprocessing import Pool
    ids = __import__("common").replay_ids()
    tot = collections.defaultdict(lambda: [0, 0.0, 0])
    with Pool(os.cpu_count() or 2) as p:
        for r in p.imap_unordered(_bench_one, ids):
            for k, (n, s, h) in r.items(): tot[k][0] += n; tot[k][1] += s; tot[k][2] += h
    from buildfeat import _skills
    S = _skills()
    skills = {}
    for k, (n, s, h) in sorted(tot.items()):
        rec = S.get(k); f = skill_power(rec) if rec else {}
        dur = _duration(rec, DEFAULT_RANK, "crippled") if rec else None
        skills[k] = {"uses": n, "secs_per_use": round(s / n, 2) if n else None, "recorded_share": round(h / n, 2) if n else None,
                     "formula_secs_per_use": round(min(dur or 0, _recharge(rec) or 0) * targets(rec), 2) if rec else None,
                     "recharge": _recharge(rec) if rec else None}
    json.dump({"about": "Slowed target-seconds each finished use of a snare produced in the stored replays (the hex, or "
                        "the Crippled condition the skill caused, on enemies, by this caster or an unrecorded one; removal "
                        "included). movepower.py uses it in place of the formula once a skill has 15+ uses, capped at the "
                        "recharge (one player can't be slowed more than all the time). Area snares count one target in the "
                        "formula (Denning, session 4u).",
               "matches": len(ids), "skills": skills}, open(BENCH, "w"), indent=1)
    return skills


if __name__ == "__main__":
    if sys.argv[1:2] == ["bench"]:
        for k, v in bench().items(): print(k, v)
    elif sys.argv[1:]:
        from replaylib import Match
        m = Match.from_branch(sys.argv[1])
        for a, p in powers(m).items(): print(m.tag[m.team(a)], m.roles.get(a), p)
    else: print(__doc__)
