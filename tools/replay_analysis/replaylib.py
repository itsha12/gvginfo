"""Helpers for analyzing one trimmed replay (format gvginfo.replay.v1, see tools/gvgreport/replay_trim.mjs).

Usage:
    from replaylib import Match
    m = Match.load("path/to/<report id>.json.gz")      # or Match.from_branch("<report id>") inside the repo
    m.f(t)            # tenths of a second -> "m:ss"
    m.snap(a, t)      # position, hp, state, weapon set of agent a at time t
    m.role(a)         # "RACK Prot", "MBP Hammer A", ... (build-based role name, see role_names)
Run report.py for the standard review tables. Terms follow knowledge/tactics.md (base, backside, push side, pit, ...).
"""
import bisect, collections, gzip, json, math, os, statistics, subprocess

PROT_SKILLS = {"Guardian", "Aegis PvP", "Shielding Hands", "Reversal of Fortune", "Spirit Bond PvP", "Shield Guardian PvP",
               "Life Sheath", "Aura of Faith", "Aura of Stability", "Protective Spirit"}
RUN_SKILLS = {"Enchanted Haste", "Illusion of Haste PvP", "Dash", "Sprint", "Storm Djinn's Haste", "Charging Strike"}
FIGHT_RANGE = 1300      # players closer than this to a group member are in the same group
STAND_R, BASE_R = 1500, 2000


class Match:
    def __init__(self, o):
        self.o = o
        self.A = o["agents"]
        self.TR = o["tracks"]
        self.SK = {int(k): v for k, v in o["skills"].items()}
        self.tag = {t["id"]: t["tag"] for t in o["meta"]["teams"]}
        self.PL = [i for i, a in enumerate(self.A) if a.get("player")]
        self.carries = self._carries()
        self.stand, self.base = self._geometry()
        self.roles = self._role_names()

    @classmethod
    def load(cls, path):
        op = gzip.open if path.endswith(".gz") else open
        with op(path, "rt") as fh:
            return cls(json.load(fh))

    @classmethod
    def from_branch(cls, report_id, repo=None):
        repo = repo or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        idx = json.loads(subprocess.check_output(["git", "-C", repo, "show", "origin/replays:index.json"]))
        raw = subprocess.check_output(["git", "-C", repo, "show", "origin/replays:" + idx["matches"][report_id]["file"]])
        return cls(json.loads(gzip.decompress(raw)))

    # ---- basics
    def team(self, a): return self.A[a].get("team") if isinstance(a, int) and a < len(self.A) else None
    def nm(self, a): return self.A[a]["n"] if isinstance(a, int) and a < len(self.A) else "?"
    def sk(self, s): return self.SK.get(s, str(s))
    @staticmethod
    def f(t): return f"{'-' if t < 0 else ''}{int(abs(t) // 600)}:{int(abs(t) / 10 % 60):02d}"

    def snap(self, a, t):
        T = self.TR.get(str(a))
        if not T: return None
        i = bisect.bisect_left(T["t"], t); i = min(max(i, 0), len(T["t"]) - 1)
        if i > 0 and abs(T["t"][i - 1] - t) < abs(T["t"][i] - t): i -= 1
        if abs(T["t"][i] - t) > 20: return None
        return dict(x=T["x"][i], y=T["y"][i], hp=T["hp"][i], st=T["st"][i], w=T["w"][i] if "w" in T else -1, sk=T["sk"][i])

    @staticmethod
    def alive(s): return s is not None and s["st"] != "d" and s["hp"] > 0

    def dist(self, a, b, t):
        s1, s2 = self.snap(a, t), self.snap(b, t)
        return math.dist((s1["x"], s1["y"]), (s2["x"], s2["y"])) if s1 and s2 else None

    # ---- flag and map
    def _carries(self):
        out, op = [], {}
        for t, typ, a in self.o.get("flags", []):
            if typ == "flag_picked_up": op[a] = t
            elif typ in ("flag_dropped", "flagstand_captured") and a in op:
                out.append(dict(s=op.pop(a), e=t, a=a, how=typ))
        return out

    def carrier_at(self, t): return [c["a"] for c in self.carries if c["s"] <= t <= c["e"]]

    def _geometry(self):
        caps = [self.snap(a, t) for t, typ, a in self.o.get("flags", []) if typ == "flagstand_captured"]
        caps = [c for c in caps if c]
        stand = (statistics.median(c["x"] for c in caps), statistics.median(c["y"] for c in caps)) if caps else (0, 0)
        base = {}
        for tm in (1, 2):    # each team spawns at its base (res shrine): median of its players' first positions
            pts = [(self.TR[str(a)]["x"][0], self.TR[str(a)]["y"][0]) for a in self.PL if self.team(a) == tm and str(a) in self.TR]
            if pts: base[tm] = (statistics.median(p[0] for p in pts), statistics.median(p[1] for p in pts))
        return stand, base

    def loc(self, a, t):
        """stand, base, enemy base, backside (nearer own base) or push (nearer enemy base)"""
        s = self.snap(a, t); p = (s["x"], s["y"]); tm = self.team(a)
        if math.dist(p, self.stand) < STAND_R: return "stand"
        if tm in self.base and math.dist(p, self.base[tm]) < BASE_R: return "base"
        if (3 - tm) in self.base and math.dist(p, self.base[3 - tm]) < BASE_R: return "enemy base"
        if tm in self.base and (3 - tm) in self.base:
            return "backside" if math.dist(p, self.base[tm]) < math.dist(p, self.base[3 - tm]) else "push"
        return "field"

    def groups(self, tm, t):
        live = [a for a in self.PL if self.team(a) == tm and self.alive(self.snap(a, t))]
        gs = []
        for a in live:
            hit = [g for g in gs if any((self.dist(a, b, t) or 1e9) < FIGHT_RANGE for b in g)]
            gs = [g for g in gs if g not in hit] + [[a] + [x for g in hit for x in g]]
        return sorted(gs, key=len, reverse=True)

    # ---- roles (Denning's naming: prot, 7 monk, 8 monk, Mes/A, stand mes, hammer, AoB derv, ...)
    def _role_names(self):
        names = {}
        for tm in (1, 2):
            ps = [a for a in self.PL if self.team(a) == tm]
            runs = collections.Counter(c["a"] for c in self.carries if c["e"] > 0)
            mes = [a for a in ps if self.A[a].get("p") == "Mesmer"]
            mesa = None
            if mes:   # Mes/A: the mesmer with a running skill, else the one who carried most
                withrun = [a for a in mes if RUN_SKILLS & {self.sk(b) for b in self.A[a].get("bar", []) if b}]
                mesa = (withrun or sorted(mes, key=lambda a: -runs[a]))[0] if len(mes) > 1 or withrun else None
            hammers = []
            for a in ps:
                p, sl = self.A[a].get("p"), self.A[a].get("slot")
                bar = {self.sk(b) for b in self.A[a].get("bar", []) if b}
                if p == "Monk":
                    r = {6: "Prot", 7: "7 Monk", 8: "8 Monk"}.get(sl, f"Monk {sl}")
                    if "Word of Censure" in bar: r += " (WoC)"     # smite monks in a WoC spike
                elif p == "Mesmer": r = "Mes/A" if a == mesa else ("Stand Mes" if len(mes) > 1 else "Mesmer")
                elif p == "Warrior" and "Hammer Bash" in bar: r = "Hammer"; hammers.append(a)
                elif p == "Dervish" and "Avatar of Balthazar" in bar: r = "AoB Derv"
                elif p == "Elementalist":   # by attunement: Air Ele, Fire Ele, Earth Ele, Water Ele
                    el = [e for e in ("Air", "Fire", "Earth", "Water") if f"{e} Attunement" in bar]
                    r = (el[0] + " Ele") if el else "Ele"
                elif p == "Ritualist" and self.A[a].get("s") == "Paragon": r = "Rit/Para"
                else: r = p or "?"
                names[a] = r
            # number duplicates within a team (e.g. three Air Eles -> Air Ele 1, 2, 3)
            cnt = collections.Counter(names[a] for a in ps)
            seen = collections.Counter()
            for a in sorted(ps, key=lambda a: self.A[a].get("slot") or 0):
                if cnt[names[a]] > 1 and not names[a].startswith(("Monk ", "Hammer")):
                    seen[names[a]] += 1; names[a] = f"{names[a]} {seen[names[a]]}"
            if len(hammers) > 1:
                for i, a in enumerate(sorted(hammers, key=lambda a: self.A[a].get("slot") or 0)): names[a] = "Hammer " + "AB"[i]
        return names

    def role(self, a):
        if isinstance(a, int) and a < len(self.A) and self.A[a].get("player"):
            return f"{self.tag[self.team(a)]} {self.roles.get(a, '?')}"
        return self.nm(a)

    def builds(self):
        out = {}
        for a in sorted(self.PL, key=lambda a: (self.team(a), self.A[a].get("slot") or 0)):
            out.setdefault(self.tag[self.team(a)], []).append(
                (self.roles[a], f"{self.A[a].get('p')}/{self.A[a].get('s')}", [self.sk(b) for b in self.A[a].get("bar", []) if b]))
        return out
