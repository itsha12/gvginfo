"""Shared constants and skill helpers for the replay analysis engine, so every layer uses the same thresholds.

Distances are game units, times seconds unless named *_t (tenths). Thresholds are Denning's anchors where he gave one
(knowledge/tactics.md), otherwise first guesses to calibrate on data/review_labels.json and, after the bulk pull, on
benchmarks."""
import json, os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ---- which matches count (Denning, session 4u): replays played before TRAIN_FROM are left out of training and of
# every benchmark built from replays; new picks come from PICK_FROM on. Team strength and lineup ratings still use every
# stored result (they only rate who is good). Dates are the replay index's UTC dates.
TRAIN_FROM = "2026-09-01"
PICK_FROM = "2026-09-02"
_INDEX = None


def replay_index(all_dates=False):
    """{report id: index entry} of the stored replays, without those before TRAIN_FROM unless all_dates."""
    global _INDEX
    if _INDEX is None:
        import subprocess
        _INDEX = json.loads(subprocess.check_output(["git", "-C", REPO, "show", "origin/replays:index.json"]))["matches"]
    return dict(_INDEX) if all_dates else {k: v for k, v in _INDEX.items() if str(v.get("date", ""))[:10] >= TRAIN_FROM}


def replay_ids():
    """Ids of the stored replays that count (from TRAIN_FROM on)."""
    return list(replay_index())


def period(rid):
    """The month a stored replay was played (YYYY-MM), for readings by period (Denning, November 2026 review: a model
    trained on one meta can mislead on the next; show whether readings hold across months). None if unknown."""
    e = replay_index(all_dates=True).get(rid)
    d = str((e or {}).get("date", ""))[:7]
    return d if len(d) == 7 else None


STRENGTH_BANDS = (("even (gap under 200)", 0, 200), ("moderate (200 to 600)", 200, 600), ("uneven (600+)", 600, 10 ** 9))


def strength_band(gap):
    """Which strength band a match sits in (Denning: whether a best play holds at the top and in close games)."""
    g = abs(gap or 0)
    return next(n for n, lo, hi in STRENGTH_BANDS if lo <= g < hi)


def counts(rid):
    """Whether a stored replay counts (played from TRAIN_FROM on); unknown ids count."""
    e = replay_index(all_dates=True).get(rid)
    return e is None or str(e.get("date", ""))[:10] >= TRAIN_FROM

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


def split_context(st, members, t, def_npc_value=None):
    """Denning (batch 10): whether a collapse is right depends on what the split can get NPC-wise, the death penalty on
    the split characters, and whether they can be killed. Measured at t for the split members (agent ids):
      split_dp          worst morale among the split members (negative = death penalty; lower max health, easier kill)
      split_npc_dps     the split members' measured damage per second against NPCs and the Lord (benchmarks)
      def_npc_value     the defending team's pit NPCs still alive, in win points (scoreboard npc_value)
      split_healers     healers on the split
      split_self_defence  self-heals and self-defence skills on the split members' bars (buildfeat.player_flags)"""
    from scoreboard import lord_dps
    from buildfeat import player_flags
    m = st.m
    alive = [a for a in members if st.alive(a, t)] or list(members)
    fl = [player_flags(m, a) for a in alive]
    return {"split_dp": min([st.morale(a, t) for a in alive] or [0]),
            "split_npc_dps": round(sum(lord_dps(m.roles[a], m.A[a].get("p")) or 0 for a in alive), 1),
            "def_npc_value": def_npc_value,
            "split_healers": sum(1 for a in alive if line(m, a) == "backline"),
            "split_self_defence": sum(f.get("self_defence", 0) + f.get("self_heal", 0) for f in fl)}


# ---- decision moments (moments.py; docs/REDESIGN.md step 2). Definitions: Denning's where a ruling is cited, otherwise
# Claude's draft to confirm (tested against the golden moments, R-303).
READ_FROM, READ_TO = 20, 30     # a call is read from where players stand 20 to 30 s after the trigger (R-294)
AREA_SHARE = 0.5                # a group is "at" a place when more than this share of its living players stand in it (R-319)
PURPOSE_S = 60                  # a leave's purpose is fixed this long after it, earlier on a pickup or on entering the enemy base (R-325)
LEAVE_MIN_S = 8                 # a player out of the main group for less than this never left (a flank, a kite)
HOME_WAIT_S = 5                 # this long in the own base (or at the own flag spawn) before leaving it: a leave from the base or res shrine
SPAWN_R = 800                   # at the flag spawn: waiting for the flag, or picking a fresh one up
GROUP_LEAVE_S = 15              # leaves of one purpose within this many seconds are one group (a three-player split)
MEET_R = 2500                   # the mains meet when their middles are this close (fights.windows, Denning's power play)
NUMBERS_MIN_S = 10              # a numbers difference shorter than this is not a moment (fights.windows)
MERGE_S = 20                    # triggers of one family for one team within this many seconds are one moment
BOOST_WARN_S = 30               # "a boost is coming": the enemy's boost is this far away (Denning, boost clock)
DOOR_R = 700                    # at a door: this close to a labelled Front door or Back door route (its whole drawn length; Claude's draft)
RETURN_R = 250                  # a returned flag: the enemy who came closest to where it lay, within this distance (returns are not recorded)
DOOR_OUT = 1500                 # a door reaches this far along its route outside the base ("in front of their front door"); Claude's draft
FOOT_ENGAGED_S = 10             # footmen are engaged when they dealt or took damage this recently (R-307)
PRESSURE_MIN = 3                # falling back under pressure is said of a group of at least this many
GREATER_STAND_WALK = 3500       # the greater stand area until Denning's drawn areas exist (R-334, R-342): this far from the stand, walked
JOIN_S = 12                     # a player counts in a fight after this long in it; shorter is support, not a player more (R-350)
ON_TIME_S = round(1.5 * CAST_R / RUN_SPEED)   # "on time": the answer arrives within the time to run 1 to 1.5 cast ranges unboosted, about 5 to 7 s (R-348)
LATE_S = 30                     # an answer this far behind is late (R-348); between the two the seconds are stated
PRESSURE_HP = 85                # low team health: under 85% (R-352; about the lowest fifth of team health in fights of 3+ a side), to adjust if needed
PRESSURE_DEATH_S = 30           # or a death in this many seconds. Under pressure is health, energy and deaths (R-349); energy is not in the replays
                                # and is left out for now: a monk energy estimate is to be added only if needed (R-353)
OVERCAP_S = 45                  # a capture this soon after the enemy's is an overcap (Claude's draft)
FIGHT_LINK = 1600               # players of either team this close are in the same fight (Claude's draft: about a cast range and a bit)
SERIOUS_CARRY_S = 5              # a pickup dropped sooner than this, without capping, is not an attempt to run (Denning: "like 3 s")
FLAGGER_R = 2500                # the main group is on the enemy flagger when its middle is this close to that player

HOLD_MIN_S = 10          # a carry this long that closed under HOLD_PROGRESS of the way to the stand is a hold
HOLD_PROGRESS = 0.25


def carry_progress(st, c):
    """Share of the distance from the pickup to the stand the carrier closed at its closest (0 = never got nearer,
    1 = reached the stand), for one carry from GameState.carries (times in seconds)."""
    from state import d
    a, s, e = c["a"], max(c["s"], 0), c["e"]
    p0 = st.pos(a, s)[0]
    if not p0: return None
    d0 = d(p0, st.geo.stand)
    if d0 <= 0: return 1.0
    ds = [d(p, st.geo.stand) for t in range(int(s), int(e) + 1) if (p := st.pos(a, t)[0])]
    return round(max(0.0, 1 - min(ds or [d0]) / d0), 2)


def is_hold(st, c):
    """Denning (batch 10): 8 Monks sometimes hold the flag for a while without trying to capture. A hold = a carry of
    HOLD_MIN_S+ that did not end in a capture and never closed HOLD_PROGRESS of the way to the stand. Holds are kept
    out of the run models, the runner choice and the runners' capture rates, so they don't count as failed runs."""
    if c.get("how") == "flagstand_captured" or c["e"] - max(c["s"], 0) < HOLD_MIN_S: return False
    pr = carry_progress(st, c)
    return pr is not None and pr < HOLD_PROGRESS


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

# ---- split attempts and main team pushes (moments.py; R-355, R-357 to R-364)
SPLIT_STEP = 2            # the records are read every 2 s
SPLIT_MIN_S = 15          # a player is on a split after this long on the enemy's ground away from his team
SPLIT_GAP_S = 20          # back on the own side of the stand this long ends the attempt (R-363)
FORCED_OUT_S = 15         # a defender arrives and the attackers leave the base within this: one linked move (R-358)
AHEAD_LOOK_S = 60         # after a split ends: how long to look for it and its defenders rejoining the main fight
CAUGHT_S = 20             # in the enemy's base this close to the defenders' base res, outnumbered or about to be (R-359)
NPC_NEAR = 2500           # an NPC's death belongs to a split or push with a player this near
FLUX = ["Odran's Razor", "Amateur Hour", "Hidden Talent", "There Can Be Only One", "Meek Shall Inherit", "Jack of All Trades",
        "Chain Combo", "Xinrae's Revenge", "Like a Boss", "Minion Apocalypse", "All In", "Parting Gift"]


def flux_at(ms):
    """The flux in effect at a time (unix ms): by month, changing at 07:00 UTC on the 1st (Guild Wars Wiki, Flux; R-356)."""
    import datetime
    t = datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc) - datetime.timedelta(hours=7)
    return FLUX[t.month - 1]
