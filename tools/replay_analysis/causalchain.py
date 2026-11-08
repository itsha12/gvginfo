"""Step 4 of the learned causal map: chains generated from the node models, and fixes priced by carrying a change
forward (Denning, 2026-11-07: the causal chains must be reflected in the model, not only in the TQ reasoning).

How a chain is built, backwards from a result:
  1. The result's node (a lost fight, a power play with no kill, a flag swing, a split that took a pit NPC ...) reads
     the moment with a model that never saw the match (learnednodes.py keeps each node's held-out fold models).
  2. The node's own breakdown says which variables pushed toward the result (each variable's contribution at that
     moment, from the glass-box curves).
  3. A variable that is itself the result of another node is followed back to that node (the flag lead to the flag
     swing before it, numbers and deaths to the fight before it, a split answer's latency to the split-answer node),
     up to the last reset or BACK_S, the TOP biggest causes at each link (Denning).
  4. A variable that is play (P, K, A.mesa_free groups) is a possible fix: it is set to its usual value (the median over
     every trained row of that node), the node is read again, and the change is carried forward link by link (a fight
     won more often means fewer own deaths in the next node; a flag swing of more seconds means more flag lead; a faster
     split answer means a shorter latency), until the result's node; there it is priced in win points (values.py).
  Context (strength, builds, clock, map) is never a fix (Denning, after batch 9).

Nothing here is a weight: the readings are the nodes' held-out models, the usual values are medians, the carry sizes
are measured (deaths in a lost fight), and the prices are values.py's.

In code: Chain(rid, team).build(node, row, t_end) -> self; .lines() -> markdown; .fixes -> priced fixes.
Entry points for the TQs: start_flags, start_fight, start_power, start_split."""
import collections, json, math, os, statistics
import numpy as np

BACK_S = 180            # Denning: back at most 3 minutes (or the last reset)
TOP = 2                 # causes followed at each link
MAX_DEPTH = 4
FIXES = 2
MIN_PUSH = {"prob": 1.0, "sec": 1.0}   # a contribution smaller than this (points, or seconds) isn't a cause worth showing
# Denning: a change too small to matter (a -0.01 difference) can't count as a cause or a fix: the value must be at least
# this share of the variable's spread (interquartile range over every trained row of the node) from its usual value
MIN_CHANGE = 0.25

# a variable that is the result of another node: (node, how a change there moves this variable)
UPSTREAM = {
    "flag_lead": ("flag_swing", "seconds"),
    "own_deaths_30s": ("fight_outcome", "own_deaths"), "own_alive": ("fight_outcome", "own_alive"),
    "own_main": ("fight_outcome", "own_alive"), "own_local": ("fight_outcome", "own_alive"),
    "def_alive": ("fight_outcome", "own_alive"), "def_free": ("fight_outcome", "own_alive"), "def_main": ("fight_outcome", "own_alive"),
    "latency": ("split_answer", "seconds"),
}
# what a node's result is, for the team it is read for: (label, unit, price name or None, sign of a "1"/more for that team)
RESULT = {
    "fight_outcome": ("won the fight", "prob", "fight", +1),
    "power_play": ("killed on the power play", "prob", "death (any)", +1),
    "collapse": ("a split member died", "prob", "death (any)", -1),
    "split_effect": ("the split took a pit NPC", "prob", "pit NPC lost (any): taken by other builds", +1),
    "run_outcome": ("the run was captured", "prob", "capture", +1),
    "run_defence": ("the enemy run was captured", "prob", "capture", -1),
    "flag_swing": ("flag lead change over 60 s", "sec", "flag", +1),
    "capture_speed": ("seconds the enemy capture took", "sec", None, +1),
    "split_answer": ("seconds to the first defender", "sec", None, -1),
    "split_chance": ("started a split", "prob", None, +1),
}
ACTIONABLE = ("P.", "K.", "A.mesa_free")
# a variable is followed back only when it sits on the bad side of its usual value for the team (a high flag lead pushes
# the next swing down by reverting, but it is a good state, not a cause to trace)
BAD_SIDE = {"flag_lead": -1, "own_deaths_30s": +1, "own_alive": -1, "own_main": -1, "own_local": -1, "def_alive": -1,
            "def_free": -1, "def_main": -1, "latency": +1}


def clock(t): return f"{int(t // 60)}:{int(t % 60):02d}"


def good1(node, row, team):
    """Is a "1" (or more seconds) of this node's result good for team? Rows are read for row["team"]."""
    own = row["team"] == team
    if node in ("collapse", "run_defence"): return not own      # own splitter dying / the enemy capturing is bad
    if node == "split_answer": return False                       # more seconds to answer is bad for the defenders
    return own


_IDS = None
def _ids():
    global _IDS
    if _IDS is None:
        import model as M
        _IDS = [m for b in M.batches() for m in b["matches"]]
    return _IDS


_HO = {}
def heldout(node):
    import learnednodes as LN
    if node not in _HO: _HO[node] = LN.load_heldout(node, _ids())
    return _HO[node]


def group_of(node, f):
    import learnednodes as LN
    for g, fs in LN.SPEC[node][1].items():
        if f in fs: return g
    return "base"


def _model(node, rid):
    h = heldout(node)
    if not h: return None, None
    i = h["fold_of"].get(rid)
    if i is None: return None, None
    return h["models"][i], h


def read(node, rid, row):
    """(reading, {feature: contribution}) for one row: a chance in % or seconds; contributions in points or seconds."""
    import pandas as pd
    e, h = _model(node, rid)
    if e is None: return None, {}
    x = pd.DataFrame([{c: row.get(c) for c in h["cols"]}]).astype(float)
    inner = getattr(e, "inner", e)
    terms = inner.eval_terms(x)[0]
    names = list(inner.feature_names_in_)
    contrib = {}
    for k, tf in enumerate(inner.term_features_):
        if len(tf) == 1: contrib[names[tf[0]]] = float(terms[k])
    if h["regression"]:
        return round(float(e.predict(x)[0]), 1), {k: round(v, 1) for k, v in contrib.items()}
    p = float(e.predict_proba(x)[0, 1])
    return round(p * 100, 1), {k: round((1 / (1 + math.exp(-v)) - .5) * 100, 1) for k, v in contrib.items()}


def _rows(node, rid):
    import lnrows, eventlayer as EL
    global _V
    try: _V
    except NameError: _V = EL.load_values() or {}
    return lnrows.node_rows(node, rid, _V)


_LOSER = None
def loser_deaths():
    """Measured: deaths of the losing side in a fight (median over every trained fight), the carry size of a fight."""
    global _LOSER
    if _LOSER is None:
        import tq
        L = []
        for rid in _ids():
            try: a = tq._analysis(rid)
            except Exception: continue
            for f in a.get("fights") or []:
                n = sum((f.get("losses") or {}).values())
                if n: L.append(n)
        _LOSER = float(statistics.median(L)) if L else 2.0
    return _LOSER


def flag_points(rid, team, t, seconds):
    """Seconds of flag lead read by the held-out win model at t (as TQ 1 does)."""
    import model as M
    wp = M.WPModel.heldout(_ids(), rid)
    tab = {(x["team"], x["t"]): x for x in M.match_table(rid)}
    row = tab.get((team, int(t - t % 5)))
    if not row: return None
    p0 = wp.explain(row)[0]; r2 = dict(row); r2["flag_lead"] = (row.get("flag_lead") or 0) + seconds
    return round(wp.explain(r2)[0] - p0, 1)


def _value(name):
    import tq
    return tq.value(name)


class Chain:
    def __init__(self, rid, team):
        self.rid, self.team = rid, team
        self.links = []       # (depth, node, row, reading, pushes [(feature, contribution, value, usual)], parent index, feature into parent)
        self.fixes = []
        self.t_end = None

    # ---- building
    def build(self, node, row, t_end=None):
        self.t_end = t_end or row["t"]
        self.t_stop = max(self.t_end - BACK_S, self._last_reset(self.t_end))
        self._walk(node, row, not good1(node, row, self.team), 0, None, None)
        self._price()
        return self

    def _last_reset(self, t):
        import tq
        a = tq._analysis(self.rid)
        rs = [r["t"] for r in a["scoreboard"] if r["t"] < t - 20 and all(r[x]["alive"] == 8 for x in r if isinstance(r.get(x), dict) and "alive" in r[x])
              and abs(r[self.team]["flag_lead"]) <= 10]
        return max(rs) if rs else 0

    def _walk(self, node, row, bad_high, depth, parent, into):
        h = heldout(node)
        if not h: return
        reading, contrib = read(node, self.rid, row)
        if reading is None: return
        unit = RESULT[node][1]
        sign = 1 if bad_high else -1          # pushes toward the bad result are positive after this
        med = h.get("medians") or {}
        spr = h.get("spreads") or {}
        def big(f):
            v, u, sp = row.get(f), med.get(f), spr.get(f)
            return v is not None and u is not None and (not sp or abs(v - u) >= MIN_CHANGE * sp)
        # each variable against its usual value: its curve at this moment minus its curve at the usual value (the node is
        # additive, so the two readings separate by variable)
        _, at_usual = read(node, self.rid, {**row, **{k: v for k, v in med.items() if v is not None}})
        pushes = sorted(((f, (c - at_usual.get(f, 0)) * sign, row.get(f), med.get(f)) for f, c in contrib.items()
                         if big(f) and (c - at_usual.get(f, 0)) * sign >= MIN_PUSH[unit]), key=lambda x: -x[1])
        idx = len(self.links)
        self.links.append({"depth": depth, "node": node, "row": row, "reading": reading, "pushes": pushes[:6],
                           "parent": parent, "into": into, "bad_high": bad_high})
        # any play variable among the pushes is a possible fix
        for f, c, v, u in pushes[:6]:
            if group_of(node, f).startswith(ACTIONABLE) and u is not None and v is not None:
                self.fixes.append({"link": idx, "feature": f, "value": v, "usual": u, "push": c})
        # follow the biggest causes: up to TOP groups, one variable each
        seen_g = []
        for f, c, v, u in pushes:
            g = group_of(node, f)
            if g in seen_g: continue
            seen_g.append(g)
            if len(seen_g) > TOP: break
            # a row read from the enemy's side: its "enemy_" numbers are this team's own
            fk = f.replace("enemy_", "own_", 1) if row["team"] != self.team and f.startswith("enemy_") else f
            mine = row["team"] == self.team or node == "split_effect" or fk != f or not f.startswith(("own_", "def_"))
            bad_side = fk in BAD_SIDE and v is not None and u is not None and (v - u) * BAD_SIDE[fk] > 0
            if fk in UPSTREAM and depth < MAX_DEPTH and mine and bad_side:
                up, how = UPSTREAM[fk]
                r2, flip = self._upstream_row(up, row)
                if r2 is not None:
                    # the upstream result that pushed this variable the bad way: a lost fight, a flag swing against, a slow answer
                    self._walk(up, r2, not good1(up, r2, self.team), depth + 1, idx, f)

    def _upstream_row(self, up, row):
        """The upstream node's latest row before this one, for this team (a fight row read from the other side counts,
        flipped)."""
        t = row["t"]
        best, flip = None, False
        for r in _rows(up, self.rid):
            if not (self.t_stop <= r["t"] < t): continue
            same = r["team"] == self.team
            if up != "fight_outcome" and not same: continue
            if best is None or r["t"] > best["t"]: best, flip = r, not same
        return best, flip

    # ---- pricing fixes by carrying the change forward
    def _delta(self, node, row, changes):
        before, _ = read(node, self.rid, row)
        r2 = dict(row); r2.update(changes)
        after, _ = read(node, self.rid, r2)
        if before is None or after is None: return None
        return after - before

    def _child_delta(self, child, f, how, d_up, flip):
        """How the child node's result moves when its variable f is fed a change d_up from its upstream node. Seconds
        carry as they are; a fight's chance carries as that share of a lost fight's deaths (measured), read at full size
        and scaled (the node's curves are in steps, so a fraction of a death would read as nothing)."""
        row = child["row"]; v0 = row.get(f)
        if v0 is None: return None
        if how == "seconds":
            d = self._delta(child["node"], row, {f: v0 + d_up})
            if d is None: return None
            # the flag swing's result is read as the lead it ends with: a lead carried in stays, less what reverts
            return d + (d_up if child["node"] == "flag_swing" and f == "flag_lead" else 0)
        win = (d_up / 100) * (-1 if flip else 1)          # change in this team's chance of winning that fight
        L = loser_deaths()
        full = {"own_deaths": -L, "own_alive": +L}[how]
        d = self._delta(child["node"], row, {f: v0 + full})
        return None if d is None else d * win

    def _price(self):
        out = []
        for fx in self.fixes:
            li = fx["link"]; L = self.links[li]
            node, row = L["node"], L["row"]
            d = self._delta(node, row, {fx["feature"]: fx["usual"]})
            if d is None or abs(d) < 0.05: continue
            steps = [(node, d)]
            cur, i = d, li
            while self.links[i]["parent"] is not None:
                child = self.links[self.links[i]["parent"]]
                f = self.links[i]["into"]
                fk = f.replace("enemy_", "own_", 1) if child["row"]["team"] != self.team and f.startswith("enemy_") else f
                up, how = UPSTREAM[fk]
                flip = self.links[i]["row"]["team"] != self.team and self.links[i]["node"] == "fight_outcome"
                cur = self._child_delta(child, f, how, cur, flip)
                if cur is None: break
                steps.append((child["node"], round(cur, 2))); i = self.links[i]["parent"]
            top = self.links[i]
            pts = self._points(top, cur) if i != li or True else None
            own = self._points(L, d)
            out.append({**fx, "node": node, "t": row["t"], "steps": steps, "win_points": pts, "own_points": own, "carried_to": top["node"]})
        out.sort(key=lambda x: -(x["win_points"] if x["win_points"] is not None else -99))
        self.fixes = [x for x in out if (x["win_points"] or 0) >= 0.5][:FIXES]
        self.all_fixes = out

    def _points(self, link, d):
        """A change d at the result's node (points of its chance, or seconds) in win points for the team: values.py for
        deaths, captures and pit NPCs (a fight = the deaths of its losing side), flag seconds through the win model."""
        node, row = link["node"], link["row"]
        price = RESULT[node][2]
        if price is None or d is None: return None
        sign = 1 if good1(node, row, self.team) else -1
        if price == "flag": return flag_points(self.rid, self.team, row["t"] + 60, d)
        v = _value("death (any)" if price == "fight" else price)
        if v is None: return None
        size = loser_deaths() if price == "fight" else 1
        return round(abs(v) * size * d / 100 * sign, 1)

    # ---- words
    def lines(self):
        import learnednodes as LN
        if not self.links: return []
        L = ["**How it got there, from the node models** (step 4: each link read by the node's held-out model; the biggest "
             "pushes toward the result, against the variable's usual value over every trained moment; a variable that is "
             "another node's result is followed back to it):"]
        for x in self.links:
            label, unit, _, _ = RESULT[x["node"]]
            rd = f"{x['reading']}%" if unit == "prob" else f"{x['reading']:+} s"
            via = f" (behind {x['into']} in the link above)" if x["parent"] is not None else ""
            if x["row"]["team"] != self.team: via += f"; read from {x['row']['team']}'s side (own = {x['row']['team']})"
            pushes = "; ".join(f"{LN.describe(x['node'], f) or f} {_fmt(v)} (usual {_fmt(u)}): {c:+.1f} {'points' if unit == 'prob' else 's'}"
                               for f, c, v, u in x["pushes"][:3])
            L.append(f"{'  ' * x['depth']}- {clock(x['row']['t'])} {x['node'].replace('_', ' ')}: {label} {rd}{via}; "
                     + (f"pushed by {pushes}" if pushes else "no single variable pushed much"))
        if self.fixes:
            L.append("*Fixes, carried forward to the result* (the variable set to its usual value, the node read again, the "
                     "change carried link by link and priced with values.py):")
            for fx in self.fixes:
                path = " -> ".join(f"{n.replace('_', ' ')} {d:+.1f}{'' if RESULT[n][1] == 'prob' else ' s'}" for n, d in fx["steps"])
                own = f" ({fx['own_points']:+.1f} at its own node)" if fx.get("own_points") is not None and len(fx["steps"]) > 1 else ""
                L.append(f"- {LN.describe(fx['node'], fx['feature']) or fx['feature']} at {clock(fx['t'])}: {_fmt(fx['value'])} -> "
                         f"{_fmt(fx['usual'])}; {path}; worth {fx['win_points']:+.1f} win points at the result{own}")
        elif self.links:
            near = [x for x in getattr(self, "all_fixes", []) if x.get("own_points")]
            near.sort(key=lambda x: -x["own_points"])
            txt = "; ".join(f"{LN.describe(x['node'], x['feature']) or x['feature']} at {clock(x['t'])} {_fmt(x['value'])} -> {_fmt(x['usual'])}: "
                            f"{x['own_points']:+.1f} at its own node, {x['win_points'] if x['win_points'] is not None else 'n/a'} carried to the result"
                            for x in near[:2])
            L.append("*Fixes carried forward*: none worth half a win point at the result" + (f" (closest: {txt})" if txt else "") + ".")
        return L

    def short(self):
        bits = []
        for x in self.links[:4]:
            if x["pushes"]:
                f = x["pushes"][0][0]
                bits.append(f"{x['node'].replace('_', ' ')} at {clock(x['row']['t'])} ({f})")
        return " <- ".join(bits)


def _fmt(v):
    if v is None: return "n/a"
    return f"{v:g}" if isinstance(v, (int, float)) and abs(v) >= 10 or float(v).is_integer() else f"{v:.2f}"


# ---- entry points for the TQs
def _nearest(node, rid, team, lo, hi, key=None, any_team=False):
    rows = [r for r in _rows(node, rid) if lo <= r["t"] <= hi and (any_team or r["team"] == team)]
    if not rows: return None
    return min(rows, key=key) if key else max(rows, key=lambda r: r["t"])


def start_flags(rid, team, s, e):
    r = _nearest("flag_swing", rid, team, s - 40, e, key=lambda r: r["y"])
    return Chain(rid, team).build("flag_swing", r, e) if r else None


def start_fight(rid, team, t):
    r = _nearest("fight_outcome", rid, team, t - 90, t, any_team=True)
    if not r: return None
    # the row may be read from the other side: the bad result for team is the other side winning
    return Chain(rid, team).build("fight_outcome", r, t)


def start_power(rid, team, t0):
    r = _nearest("power_play", rid, team, t0 - 3, t0 + 3)
    return Chain(rid, team).build("power_play", r, t0) if r else None


def start_npc(rid, defending_team, t):
    """A pit NPC lost: the enemy split that took it (split-effect node) if one was in the base, else the fight before."""
    rows = [r for r in _rows("split_effect", rid) if r["team"] != defending_team and r["t"] <= t <= r["t"] + 240]
    if rows: return Chain(rid, defending_team).build("split_effect", max(rows, key=lambda r: r["t"]), t)
    return start_fight(rid, defending_team, t)
