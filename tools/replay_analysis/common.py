"""Shared constants and skill helpers for the replay analysis engine, so every layer uses the same thresholds.

Distances are game units, times seconds unless named *_t (tenths). Thresholds are Denning's anchors where he gave one
(knowledge/tactics.md), otherwise first guesses to calibrate on data/review_labels.json and, after the bulk pull, on
benchmarks."""
import json, os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ---- geometry
CAST_R = 1250            # about spell range
IN_AREA = 322            # 'in the area' (knowledge/ranges.md): the largest offensive-spell area
FIGHT_RANGE = 1300       # players closer than this to a group member are in the same group
STAND_R = 1500           # around the flag stand
BASE_R = 2500            # around a team's res shrine
PIT_R = 1500             # around a Lord
NEAR_R = 1200            # "near" (escort, enemies in the way)
SPLIT_FAR = 2500         # away from the own main group
DEFEND_R = 1500          # a split defender

# ---- movement and the flag (measured on 24 matches: spawn to cap carries median 41 s over ~8,400 units)
RUN_SPEED = 270          # units per second, straight line, moving freely
CARRY_SPEED = 205        # units per second, straight line, carrying (25% slower plus pathing)
RES_EVERY = 120          # base res every 2 minutes of match clock
BOOST_EVERY = 120        # a morale boost every 2 minutes of holding the stand

# ---- spikes and support (Denning's anchors)
SPIKE_BURST = (450, 2.0)        # damage within seconds on a healthy target: a spike, judged on prot timing
SPIKE_REACT = (250, 2.0)        # a burst a monk should react to (monk profiles, catches)
UNSAVEABLE_AI = (550, 0.35)     # armor ignoring damage within seconds: no prot or Infuse saves it
SURVIVABLE_AR = (400, 0.6)      # armor respecting within seconds on a shield set: should be survivable
SUPPORT_SHARE = 0.6             # a monk "in range" of a victim for this share of the alive seconds in the window
PRE = 15                        # seconds looked at before a death
CHAIN_GAP = 20                  # deaths of one team within this many seconds belong to one chain
AFTER_TIME = 15                 # a death within this many seconds after a res is "after time"

# ---- skills
PROT_SKILLS = {"Guardian", "Aegis PvP", "Shielding Hands", "Reversal of Fortune", "Spirit Bond PvP", "Shield Guardian PvP",
               "Life Sheath", "Aura of Faith", "Aura of Stability", "Protective Spirit", "Infuse Health",
               "Shield of Absorption", "Protective Bond"}
CRITICAL = PROT_SKILLS | {"Healing Burst", "Blessed Light", "Dismiss Condition", "Patient Spirit", "Word of Healing"}
BLOCKS = {"Guardian", "Aegis PvP", "Shield Guardian PvP"}
RUN_SKILLS = {"Enchanted Haste", "Illusion of Haste PvP", "Dash", "Sprint", "Storm Djinn's Haste", "Charging Strike"}
GAP_CLOSERS = {"Death's Charge", "Sprint", "Rush", "Shadow of Haste", "Dash", "Death's Retreat", "Charging Strike", "Harrier's Haste"}
SNARE_CONDITIONS = {"crippled", "dazed"}
STRIP_SKILLS = ("Shatter", "Energy Surge", "Energy Burn", "Drain Enchantment", "Power Leak", "Signet of Disenchantment")

_DATA = None


def _skills():
    global _DATA
    if _DATA is None:
        data = json.load(open(os.path.join(REPO, "data", "skills.json")))
        rows = data["skills"] if isinstance(data, dict) and "skills" in data else data
        _DATA = list(rows.values() if isinstance(rows, dict) else rows)
    return _DATA


_KIND = None
def skill_kind(sid, name=""):
    """heal, prot, removal or other, from the skill data (attribute and what the skill removes)."""
    global _KIND
    if _KIND is None:
        _KIND = {}
        for s in _skills():
            k = "other"
            if s["name"].startswith(("Infuse Health", "Shield of Absorption", "Protective Spirit", "Reversal of Fortune")): k = "prot"
            elif s["attr"] == "Protection Prayers": k = "removal" if s.get("removes") and s["type"] == "Spell" else "prot"
            elif s["attr"] in ("Healing Prayers", "Divine Favor") or "Heal" in s["name"]:
                k = "removal" if s.get("removes") and "Hex" in s["name"] else "heal"
            elif s.get("removes"): k = "removal"
            _KIND[s["id"]] = k; _KIND[s["name"]] = k
    return _KIND.get(sid) or _KIND.get(name) or _KIND.get(name + " (PvP)") or "other"


_ACT = None
def activation(name):
    """Cast time in seconds from the skill data (0 for attacks, shouts and stances)."""
    global _ACT
    if _ACT is None:
        _ACT = {}
        for x in _skills():
            a = (x.get("activation") or "").replace(" s", "").strip()
            v = {"¼": .25, "½": .5, "¾": .75, "1½": 1.5}.get(a)
            if v is None:
                try: v = float(a)
                except ValueError: v = 0
            _ACT[x["name"]] = v
    return _ACT.get(name, _ACT.get(name.replace(" PvP", " (PvP)"), 1))


_TYPE = None
def skill_type(name):
    global _TYPE
    if _TYPE is None: _TYPE = {x["name"]: x.get("type") or "" for x in _skills()}
    return _TYPE.get(name, _TYPE.get(name.replace(" PvP", " (PvP)"), ""))


RUNNER_CLASSES = ["warrior", "dervish", "assassin", "paragon", "ranger", "mesmer", "elementalist", "necromancer", "ritualist", "monk"]


def runner_class(m, a):
    """Who carries (Denning: capping on a warrior, a midline, a dervish or a monk is a strategic decision): the carrier's
    primary profession. Coded 0-9 in the order of RUNNER_CLASSES for the node models (each code its own bin)."""
    p = (m.A[a].get("p") or "").lower()
    return p if p in RUNNER_CLASSES else "other"


def runner_code(m, a):
    c = runner_class(m, a)
    return RUNNER_CLASSES.index(c) if c in RUNNER_CLASSES else None


def line(m, a):
    """Denning: frontline = dervishes, warriors, melee assassins; midline = elementalists, rangers, paragons, mesmers,
    caster assassins (and ritualists, to confirm); backline = monks. Decided by build, not profession alone."""
    p = m.A[a].get("p")
    if p == "Monk": return "backline"
    if p in ("Warrior", "Dervish"): return "frontline"
    if p == "Assassin":
        bar = " ".join(m.sk(b) for b in m.A[a].get("bar", []) if b)
        return "frontline" if any(w in bar for w in ("Strike", "Blossom", "Fang", "Jagged", "Wild Blow", "Twisting")) else "midline"
    return "midline"
