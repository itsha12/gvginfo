"""The variable catalogue (Denning, November 2026 review, bundle 2; docs/SPEC.md section 8).

Candidate play variables generated mechanically from the replay schema, so that finding variables is a search rather
than Denning's memory: every combination of

  recorded thing   x  subject                      x  window before the moment
  (what the replay  (own team, enemy team, and the   (the 10 s and the 30 s ending at the moment: strictly before it,
   records)          own team by line: frontline,     so a candidate joined to a node row at the row's time is
                     midline, backline)                measured before the result's window)

Recorded things (replay codes in tools/gvgreport/replay_trim.mjs): damage on enemy players (dm), of which on enemy
healers, damage on NPCs, healing (hl), casts finished (cf) and of which on enemy healers and on the enemy midline and
frontline, casts cancelled (cx), attacks finished (af), interrupts landed (the replay's interrupt list) and of which on
healers, conditions put on enemies (co), knockdown seconds suffered (track state k), seconds moving (track state m),
deaths (dt). Team-level things also come as own minus enemy.

Every candidate is a decision or execution variable by construction (what the team did), never state or build, so
discovery offers only what can become advice (M6). Values are per 10 s. Built once per match as prepared data
(cache kind "catalogue", keyed by this file and the measurement layer), {"team|t": {variable: value}} every 5 s.

Usage: python3 catalogue.py <report id>     prints the variable names and one moment
In code: panel(rid) -> {(team, t): {name: value}}; names() -> [variable names]."""
import collections, json, os, sys
from common import REPO

WINDOWS = (10, 30)
LINES = ("frontline", "midline", "backline")
STEP = 5


def _series(m):
    """Per team (1, 2) and per line, one value per second of each recorded thing."""
    from phases import healer
    from common import line
    end = int(m.o["meta"].get("match_length_s") or (max((e[0] for e in m.o.get("ev") or [] if e[0] is not None), default=0) / 10)) + 2
    H = {a for a in m.PL if healer(m, a)}
    LN = {a: line(m, a) for a in m.PL}
    things = ["dm_players", "dm_healers", "dm_npcs", "heal", "casts", "casts_on_healers", "casts_on_midfront", "cancels", "attacks",
              "interrupts", "interrupts_on_healers", "conditions_on_enemies", "knockdown_s", "moving_s", "deaths"]
    S = {(tm, ln): {k: [0.0] * end for k in things} for tm in (1, 2) for ln in ("team",) + LINES}
    def add(a, k, t, v=1.0):
        if a not in m.PL: return
        tm = m.team(a); sec = int(t)
        if sec < 0 or sec >= end: return
        S[(tm, "team")][k][sec] += v; S[(tm, LN[a])][k][sec] += v
    for e in m.o.get("ev") or []:
        t = e[0]
        if t is None or t < 0: continue
        t = t / 10; code, a, b = e[1], e[2], e[3]
        if code == "dm" and (e[5] or 0) > 0 and a in m.PL and isinstance(b, int) and b < len(m.A):
            if m.A[b].get("player") and m.team(b) != m.team(a):
                add(a, "dm_players", t, e[5])
                if b in H: add(a, "dm_healers", t, e[5])
            elif m.A[b].get("npc"): add(a, "dm_npcs", t, e[5])
        elif code == "hl" and (e[5] or 0) > 0: add(a, "heal", t, e[5])
        elif code == "cf":
            add(a, "casts", t)
            if isinstance(b, int) and b in m.PL and m.team(b) != m.team(a):
                add(a, "casts_on_healers" if b in H else "casts_on_midfront", t)
        elif code == "cx": add(a, "cancels", t)
        elif code == "af": add(a, "attacks", t)
        elif code == "co" and a in m.PL:
            # condition applied to a: credit the enemy team as a whole (the replay does not name the source here)
            tm = 3 - m.team(a); sec = int(t)
            if 0 <= sec < end: S[(tm, "team")]["conditions_on_enemies"][sec] += 1
        elif code == "dt": add(a, "deaths", t)
    for i in m.o.get("interrupts") or []:
        a, b = i[1], i[3]
        if a in m.PL:
            add(a, "interrupts", i[0] / 10)
            if b in H: add(a, "interrupts_on_healers", i[0] / 10)
    for a in m.PL:
        tr = m.TR.get(str(a)) or m.TR.get(a) or {}
        ts, st = tr.get("t") or [], tr.get("st") or []
        for t, s_ in zip(ts, st):
            if t is None or t < 0: continue
            if s_ == "k": add(a, "knockdown_s", t / 10)
            elif s_ == "m": add(a, "moving_s", t / 10)
    return S, end, things


def names():
    things = ["dm_players", "dm_healers", "dm_npcs", "heal", "casts", "casts_on_healers", "casts_on_midfront", "cancels", "attacks",
              "interrupts", "interrupts_on_healers", "conditions_on_enemies", "knockdown_s", "moving_s", "deaths"]
    out = []
    for w in WINDOWS:
        for k in things:
            out += [f"p.own_{k}_{w}s", f"p.enemy_{k}_{w}s", f"p.diff_{k}_{w}s"]
            for ln in LINES: out.append(f"p.own_{ln}_{k}_{w}s")
    return out


def build(rid):
    from replaylib import Match
    m = Match.from_branch(rid)
    S, end, things = _series(m)
    cum = {key: {k: _cum(v) for k, v in d.items()} for key, d in S.items()}
    def win(key, k, t, w):
        c = cum[key][k]; hi = min(int(t), end); lo = max(hi - w, 0)
        return round((c[hi] - c[lo]) * 10.0 / w, 2)
    out = {}
    for tm in (1, 2):
        tag = m.tag[tm]; foe = 3 - tm
        for t in range(STEP, end, STEP):
            v = {}
            for w in WINDOWS:
                for k in things:
                    o, e = win((tm, "team"), k, t, w), win((foe, "team"), k, t, w)
                    v[f"p.own_{k}_{w}s"] = o; v[f"p.enemy_{k}_{w}s"] = e; v[f"p.diff_{k}_{w}s"] = round(o - e, 2)
                    for ln in LINES: v[f"p.own_{ln}_{k}_{w}s"] = win((tm, ln), k, t, w)
            out[f"{tag}|{t}"] = v
    return out


def _cum(v):
    c = [0.0]
    for x in v: c.append(c[-1] + x)
    return c


def panel(rid):
    import cache
    d = cache.prepared("catalogue", rid, lambda: build(rid))
    return {(k.split("|")[0], int(k.split("|")[1])): v for k, v in d.items()}


if __name__ == "__main__":
    rid = sys.argv[1]
    P = panel(rid)
    print(len(names()), "variables;", len(P), "team-moments")
    k = sorted(P)[len(P) // 2]
    print(k, json.dumps({a: b for a, b in list(P[k].items())[:12]}))
