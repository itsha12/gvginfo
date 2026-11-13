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
DOOR_CLEAR = 300                # a door is named only where its drawn route is this much nearer than the side's other door; where they run together it is the front door (Claude's draft)
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

# ---- reading step 2: the words of R-371, R-373 and R-375 to R-378 (moments.py). Confirmed by Denning as they stand
# (R-404), with the delayed pickup at 10 s (R-406); the thresholds his later rulings added (R-400 to R-407: STANDOFF_S,
# STANDOFF_HITS, STANDOFF_MIN, STANDOFF_R, HOLD_BACK_S, LEFT_AT_SPAWN_S) are Claude's, left to its judgement; the bands of the flag lead are his (R-408). Their counts over
# every counted match: tools/golden/thresholds.py show; what a looser or tighter value would do: thresholds.py sweep.
PUSHFLAG_R = 1400         # an enemy player is on the flagger when he stands this close to him (a cast range and a little: a ranger pushes from range)
PUSHFLAG_S = 6            # ... for this long, and has hit him or landed a skill on him at least once
PUSHFLAG_SHORT_S = 4      # ... or for this long when he reaches his team with them still on him (R-418)
PUSHFLAG_LATE_S = 4       # ... the hit or skill then landing up to this long after he reaches it (R-418; Claude's draft)
PUSHFLAG_GAP_S = 10       # a push broken for no longer than this is still the same push
PUSHFLAG_MATES = 3        # the flagger is on his own with fewer than this many team mates around him (with more, it is the fight he stands in)
PUSHFLAG_AHEAD_S = 45     # a player is his team's flagger from this long before his pickup, once he is on his way back or at the spawn
ROUTE_ENDS = 1000         # a flag route is read away from the spawn and the stand, where the drawn flag runs lie apart
ROUTE_OFF = 800           # the carrier followed a drawn flag run when he stayed this close to it on average ...
ROUTE_CLEAR = 400         # ... and this much closer to it than to the other one
ROUTE_MIN_S = 6           # ... over at least this many seconds of walking
LEAD_S = 6                # a flag lead counts once it has lasted this long
LEAD_HALF = 0.35          # the flag lead (R-408): a team's tally (1 for the stand, plus the share of its next flag run done, plus up to half a run
LEAD_ONE = 0.8            # for the following runner already back at the spawn) less the enemy's. The bands are Denning's: about half a flag up
LEAD_ONE_HALF = 1.3       # from 0.35, a flag up from 0.8, a flag and a half from 1.3, two flags from 1.7; under 0.35 the teams are level
LEAD_TWO = 1.7
STANDOFF_S = 35           # a stand-off (R-405, framed on OG v hdm, R-411; 35 s and 0.4 hits by R-413): the two main teams standing off this long (the classic example: about 60 s, 42 of them without a hit) ...
STANDOFF_HITS = 0.4       # ... trading no more than this many hits for each of their players in any 10 s (the example's tail: 0.2 to 0.6; the fight before and after it: 1.3 to 2.5)
STANDOFF_MIN = 5          # ... with at least this many alive in each main team (the example: 8 and 7)
STANDOFF_R = 4000         # ... and their middles no further apart than this (the example: 1,900 to 3,400; they need not be near enough to be one fight)
STANDOFF_SPLIT_MIN = 2    # a stand-off on a split (R-415): two groups, at least one not its team's main team, this many or more in each ...
STANDOFF_SPLIT_S = 25     # ... for this long (shorter than the main teams' 35 s: his example, NwAy v SKT, has two of 26 to 35 s) ...
STANDOFF_STILL = 1000     # ... each staying this close to where it stood when the stand-off began (a split running to collapse covers this in 4 s; the example's groups moved 400 to 800)
STANDOFF_NEAR = 1200      # ... and their middles at least this far apart (about a cast range: not on top of each other), and no more than STANDOFF_R
PICKUP_DELAY_S = 10       # a pickup is delayed while pushed when the flagger stands at his spawn this long with an enemy on him (R-377; 12 s by R-404, 10 s by R-406 after the sweep)
HOLD_S = 15               # a flag is held when it stands in hand at the stand this long before it is capped ...
BOOST_LATE_S = 20         # ... and held until just before the boost when the cap lands this close to the enemy's boost (R-377)
HOLD_BACK_S = 45          # a flag is held back, clear and deliberate (R-407): in hand around the stand (the stand or the greater stand area) while the enemy holds the stand, this long without capping
LEFT_AT_SPAWN_S = 45      # a flag is left at the spawn, not run yet, when it is picked up this much later than the walk back for it needed (R-400, R-407)
HELP_IN_S = 8             # a player stays to help a flag in when he hands it off and is still with it this long later, at the cap (R-377)
HELP_BACK_S = 45          # ... and picks the next flag up himself within this long of that cap (later than that he had not stayed for the flag)
LEAVE_RES_S = 20          # leaving a base just before the base res: out of it within this long before the defenders' dead come back (R-377; as CAUGHT_S, R-359)
MONK_S = 12               # a monk count in a fight is told once it has lasted this long (as JOIN_S, R-350)
MONK_MIN = 4              # ... in the main team's fight, with at least this many of the team in it (a two or three player fight has its monks in its numbers)
LORD_GAP_S = 30           # damage on the Guild Lord broken for no longer than this is one stretch on him (as on_pit)

# ---- joins, leaves, swaps and the split fight record (moments.py; R-365, R-374). Confirmed by Denning as they stand (R-390),
# from JOIN_LOOK_S to SPLIT_FIGHT_MIN, with their counts over 606 matches beside them (tools/golden/thresholds.py).
JOIN_LOOK_S = 16          # a join or a leave is read over this long before or after it
JOIN_MOVE = 800           # the player moved at least this far in that time ...
JOIN_LEAD = 1.3           # ... and this many times further than the players he joined or left: otherwise the fight came to him
JOIN_ENGAGE = 1000        # a join or a leave is at a fight only where the two sides stand this close (an aggro bubble) or trade damage within JOIN_ENGAGE_S: a team regrouping within linking range of one enemy is not joining a fight (golden game 1, 7:50; Claude's)
JOIN_ENGAGE_S = 30        # ... damage or a skill between the two sides this close in time, either side (Claude's)
SWAP_S = 40               # a leave and a join by one team at the same fight within this long is a swap
SWAP_STAY_S = 30          # ... when the one going out had been in it this long, the one coming in stays this long, and the first does not come straight back
GROUND_MOVE = 2000              # the main team has moved up or back when it covers this much walked distance toward a base (about a fifth of the walk from the stand to the pit)
GROUND_S = 60                   # ... within this long (a fighting retreat is slow; a drift over minutes is not a move)
GROUND_BACK = 1000              # ... and the move ends once the team has come this far back the other way
GROUND_SPLIT_MOVE = 1000        # a split group's move is told from this much (a split fights over shorter ground: back to its footies is a move, R-374)
PIT_S = 10                      # at the enemy's pit: trading damage with its knight, bodyguard or Guild Lord this recently (R-387)
WAY_OUT_GAP_S = 10              # going out by a door: players passing out along the same door this close together are one group, and it is still out this long after (Claude's draft)
SIDE_FIGHT_MAX = 4              # a fight hanging off a bigger one is its own fight when its players trade damage only with each other: at most this many players
SIDE_FIGHT_S = 10               # ... read over this many seconds either side
UNDEFENDED_S = 15               # a split is left undefended when no defender is near it for this long
GROUND_MIN = 3                  # a move of the main team is told when it is at least this many players
GROUND_JUMP = 1200              # more than this in one 2 s step is not walking (a wipe and a base res, the main team redefined): the reading starts again
SPLIT_FIGHT_GAP_S = 60    # the same two groups out of contact no longer than this are still one split fight (R-365)
SPLIT_FIGHT_MIN = 2       # a split fight opens with at least this many players a side



# ---- trying a threshold (tools/golden/thresholds.py sweep): GVG_TRY="NAME=value,NAME=value" replaces thresholds of the
# reading for one run, so their effect on the records and on the line-up can be seen without editing this file.
# For the reading tools only (moments.py, story.py, the line-up, the thresholds table): never set it in a training run.
TRY_NAMES = ("JOIN_S", "JOIN_LOOK_S", "JOIN_MOVE", "JOIN_LEAD", "SWAP_S", "SWAP_STAY_S", "GROUND_MOVE", "GROUND_S", "GROUND_BACK", "GROUND_SPLIT_MOVE", "PIT_S",
             "SIDE_FIGHT_MAX", "SIDE_FIGHT_S", "UNDEFENDED_S", "GROUND_MIN", "GROUND_JUMP", "SPLIT_FIGHT_GAP_S", "SPLIT_FIGHT_MIN", "SPLIT_MIN_S", "SPLIT_GAP_S", "FIGHT_LINK",
             "PUSHFLAG_R", "PUSHFLAG_S", "PUSHFLAG_SHORT_S", "PUSHFLAG_LATE_S", "PUSHFLAG_GAP_S", "PUSHFLAG_MATES", "PUSHFLAG_AHEAD_S", "ROUTE_ENDS", "ROUTE_OFF", "ROUTE_CLEAR", "ROUTE_MIN_S", "LEAD_S", "LEAD_HALF",
             "LEAD_ONE", "LEAD_ONE_HALF", "LEAD_TWO", "STANDOFF_S", "STANDOFF_HITS", "STANDOFF_MIN", "STANDOFF_R", "STANDOFF_SPLIT_MIN", "STANDOFF_SPLIT_S", "STANDOFF_STILL", "STANDOFF_NEAR", "PICKUP_DELAY_S", "HOLD_S", "BOOST_LATE_S",
             "HOLD_BACK_S", "LEFT_AT_SPAWN_S", "HELP_IN_S", "HELP_BACK_S", "LEAVE_RES_S", "MONK_S", "MONK_MIN", "LORD_GAP_S")
for _kv in filter(None, (os.environ.get("GVG_TRY") or "").split(",")):
    _k, _v = _kv.split("=")
    if _k not in TRY_NAMES: raise SystemExit(f"GVG_TRY: {_k} is not a threshold of the reading")
    globals()[_k] = int(float(_v)) if isinstance(globals()[_k], int) else float(_v)
