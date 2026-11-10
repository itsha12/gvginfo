"""The learned causal map, step 2b (Denning 2026-11-07): node models built from the event layer, each using only the
causal-map links into it, so every link's strength is measured on matches the model never saw.

Each node: one row per event (a run, a fight, a split, a power play) or per sampled moment, a label after it, and
features measured at or before it, grouped by the causal-map link they stand for (from node -> the node's map target).
Glass box (Explainable Boosting Machine, main effects only, so every curve reads on its own), held out by match.

A link's strength = how much worse the node predicts unseen matches without that link's features (refit without them,
same folds): log loss for yes/no nodes, mean absolute error (s) for number nodes. Status: supported when the gain is
more than twice its spread across folds, rejected when dropping it helps by more than twice its spread, otherwise not
clear yet. Written into data/model/causal_map.json (field "measured", status changed only from hypothesis) and logged in
data/model/link_log.json. A link that a node needs and the map lacked is added as a hypothesis, logged, with its source.

Nodes (map target):
  run_outcome      (R.3)  a flag run is captured; read at the same point of every run (5, 15, 30 s in): control and
                          damage on the runner so far, not over the whole run (a run that gets far gets Crippled)
  flag_swing       (R.3)  change in flag lead over the next 60 s (s), every 20 s
  run_defence      (R.3)  an enemy run is captured, from the defending side, at 5, 15, 30 s in (every run, stopped or not)
  capture_speed    (R.3)  seconds an enemy capture took (captures only, so it can't show what pushing stops)
  power_play       (K.4)  a power play of any size kills
  fight_outcome    (R.2)  a fight is won; play measured before its first death (wrong casts over the fight, as rates)
  split_chance     (A.allocation)  a team starts a split in the next 30 s (for "failed to split")
  split_answer     (P.11) seconds until the first defender reaches a split in the base (60 = never)
  split_effect     (R.5)  a split in the base kills a pit NPC
  pit_npc_loss     (R.5)  a pit NPC dies in the next 15 s while enemies are in the pit (defending side; nodes.py's
                          npc_loss moments, learned here so NPC chains price fixes)
  collapse         (R.1)  a split member dies during the split; collapse timing read five ways and split depth two ways
                          (each also tested alone)
Usage:  python3 learnednodes.py fit [node ...]     fit, measure links, write data/model/nodes/L_<node>.json, print
        python3 learnednodes.py write              fit all, write link strengths into the causal map and the log
In code: fit_all(ids) -> {node: summary}; whatif(node, row, changes) -> (before, after)."""
import collections, datetime, hashlib, json, math, os, statistics, sys, warnings
import numpy as np
warnings.filterwarnings("ignore")
from common import REPO
import model as M

NODE_DIR = os.path.join(REPO, "data", "model", "nodes")
MAP = os.path.join(REPO, "data", "model", "causal_map.json")
LINK_LOG = os.path.join(REPO, "data", "model", "link_log.json")
from lnrows import CHECKPOINTS, CLIP, NEVER
REGRESSION = {"flag_swing", "capture_speed", "split_answer"}

# node -> (map target, {group (map node the link comes from): {feature: description}}, base features kept in every fit)
SPEC = {
 "run_outcome": ("R.3", {
    "P.10": {"stand_own": "own team holds the stand", "stand_enemy": "the enemy holds the stand",
             "enemy_boost_in": "seconds to the enemy's boost (if it holds)", "flag_lead": "flag lead at the start (s)",
             "runner_line": "runner 0 frontline, 1 midline, 2 backline",
             "runner_class": "who carries: 0 warrior, 1 dervish, 2 assassin, 3 paragon, 4 ranger, 5 mesmer, 6 elementalist, 7 necromancer, 8 ritualist, 9 monk"},
    "S.scoreboard": {"morale_diff": "morale, own minus enemy (discovery, approved)", "boost_clock": "boost clock (discovery, approved)"},
    "A.allocation": {"escort": "escorts at the start", "own_main": "own main", "enemy_main": "enemy main",
                     "enemy_power_play": "running into an enemy power play"},
    "K.11": {"crippled_so_far": "runner Crippled by this point", "knocked_down_so_far": "runner knocked down by this point",
             "other_control_so_far": "other conditions on the runner by this point", "damage_so_far": "damage on the runner by this point",
             "pushers_so_far": "enemies who pushed the runner by this point",
             "enemy_snare_near": "snare power of live enemies within 1,300 of the runner (movepower.py)"},
    "K.13": {"min_capture_s": "seconds the carrier needs at least to reach the stand from here, at its fastest expected carry speed (its speed skills; Denning)",
             },
    "C.builds": {"enemy_snares": "snare skills on enemy bars (discovery, approved)"},
    "C.map": {"run_dist": "distance from the team's spawn to the stand"},
    "C.strength": {"strength_gap": "team strength gap"}}, {"checkpoint_s": "seconds into the run"}),
 "flag_swing": ("R.3", {
    "S.scoreboard": {"flag_lead": "flag lead now (s)", "morale_diff": "morale, own minus enemy (discovery, approved)"},
    "P.10": {"waiting_runner": "a runner waiting", "backup_flag": "a backup flag", "stand_own": "own team holds the stand",
             "stand_enemy": "the enemy holds the stand", "own_boost_in": "seconds to own boost", "enemy_boost_in": "seconds to the enemy's boost",
             "own_eta": "flag model: seconds until own team could capture", "enemy_eta": "flag model: seconds until the enemy could capture",
             "own_carrying": "own flag being carried now", "enemy_carrying": "enemy flag being carried now",
             "own_cap_before_boost": "own team can capture before the enemy's boost", "enemy_cap_before_boost": "the enemy can capture before own boost"},
    "A.allocation": {"own_alive": "own players alive", "enemy_alive": "enemy players alive", "own_main": "own main", "enemy_main": "enemy main",
                     "own_flag_duty": "own players on flag duty", "enemy_flag_duty": "enemy players on flag duty",
                     "own_in_enemy_base": "own players in the enemy base", "enemy_in_own_base": "enemy players in own base"},
    "R.1": {"own_deaths_30s": "own deaths in the last 30 s", "enemy_deaths_30s": "enemy deaths in the last 30 s"},
    "C.clock": {"minute": "minute", "res_in": "seconds to the next res"},
    "C.map": {"run_dist": "distance from the team's spawn to the stand"},
    "C.strength": {"strength_gap": "team strength gap"}}, {}),
 "run_defence": ("R.3", {
    "A.mesa_free": {"def_free": "defenders alive and not on flag duty at the run's start", "pushers_so_far": "defenders who pushed the runner by this point",
                    "control_so_far": "conditions and knockdowns on the runner by this point", "damage_so_far": "damage on the runner by this point"},
    "K.11": {"def_snare_near": "snare power of live defenders within 1,300 of the runner (movepower.py)"},
    "K.13": {"min_capture_s": "seconds the carrier needs at least to reach the stand from here (its speed skills)"},
    "P.10": {"runner_class": "who carries: 0 warrior, 1 dervish, 2 assassin, 3 paragon, 4 ranger, 5 mesmer, 6 elementalist, 7 necromancer, 8 ritualist, 9 monk"},
    "S.scoreboard": {"boost_clock": "boost clock (discovery, approved)", "stand": "stand (discovery, approved)",
                     "flag_lead": "flag lead (discovery, approved)", "morale_diff": "morale, own minus enemy (discovery, approved)",
                     "down_diff_s": "time down: enemy minus own seconds until the dead are back (+ = the enemy has more time down) (discovery, approved)"},
    "C.builds": {"own_snares": "snare skills on own bars (discovery, approved)", "own_area_damage": "area-damage skills on own bars (discovery, approved)",
                 "enemy_snares_v_own_speed": "enemy snares against own speed (discovery, approved)"},
    "K.5": {"healing_monks_own": "own healing monks (discovery, approved)"},
    "A.allocation": {"escort": "the runner's escorts", "att_main": "attackers' main", "def_main": "defenders' main"},
    "C.map": {"run_dist": "distance from the runner's spawn to the stand"},
    "C.strength": {"strength_gap": "defending team's strength gap"}}, {"checkpoint_s": "seconds into the run"}),
 "capture_speed": ("R.3", {
    "A.allocation": {"defenders_free": "defenders alive and not on flag duty", "escort": "the runner's escorts"},
    "K.11": {"pushers_10s": "defenders who pushed the runner in the first 10 s", "control_10s": "conditions and knockdowns on the runner in the first 10 s",
             "damage_10s": "damage on the runner in the first 10 s",
             "def_snare_near": "snare power of live defenders within 1,300 of the runner 10 s in (movepower.py)"},
    "K.13": {"min_capture_s": "seconds the carrier needed at least, at its fastest expected carry speed (its speed skills)"},
    "P.10": {"runner_class": "who carries: 0 warrior, 1 dervish, 2 assassin, 3 paragon, 4 ranger, 5 mesmer, 6 elementalist, 7 necromancer, 8 ritualist, 9 monk"},
    "C.map": {"run_dist": "distance from the runner's spawn to the stand"},
    "C.strength": {"strength_gap": "defending team's strength gap"}}, {}),
 "power_play": ("K.4", {
    "A.allocation": {"size": "players up", "own_main": "own main", "enemy_main": "enemy main",
                     "short_dead": "share of the enemy's missing player-seconds: dead", "short_running": "running the flag",
                     "short_backside": "on the back side or push side", "short_base": "in a base or pit"},
    "R.3": {"flag_lead": "flag lead (s)"},
    "S.scoreboard": {"down_diff_s": "time down: enemy minus own seconds until the dead are back (+ = the enemy has more time down) (discovery, approved)", "carrying_diff": "players carrying a flag, own minus enemy (discovery, approved)"},
    "P.14": {"pushed": "pushed (1) or held (0)"},
    "K.2": {"dps_v_usual": "own damage per second against the usual of the players alive"},
    "P.2": {"spikes_10s": "own spikes per 10 s", "spike_spread": "median spread of own spikes (s)"},
    "P.1": {"spikes_on_healers": "share of own spikes on healers",
            "healer_damage_share": "share of own damage on enemy players that landed on enemy healers (Bounty: going after the monks)"},
    "K.11": {"blind_secs_on_own_10s": "seconds own attackers spent Blind, per 10 s"},
    "P.24": {"knockdowns_10s": "knockdowns landed on the enemy per 10 s (Denning: offensive knockdowns)",
             "knockdowns_on_casting_10s": "of which on a target that was casting, per 10 s"},
    "P.25": {"disable_10s": "skill-seconds disabled on the enemy per 10 s (Complicate, Power Lock, Power Block, Blackout)"},
    "P.26": {"castprev_10s": "enemy casts that Shame, Guilt or Diversion punished, per 10 s"},
    "P.22": {"degen_10s": "degeneration put on the enemy, pip-seconds per 10 s (conditions and degen hexes)"},
    "C.builds": {"enemy_strips_v_own_prots": "enemy strips against own prots (discovery, approved)"},
    "C.strength": {"strength_gap": "team strength gap"}}, {"window_s": "seconds the power play lasted"}),
 "fight_outcome": ("R.2", {
    "A.allocation": {"own_local": "own players in the fight", "enemy_local": "enemy players in the fight"},
    "P.13": {"peel_defensive_diff": "own frontline damage share on attackers of own backline, minus the enemy's"},
    "P.17": {"ready_interrupt_diff": "interrupted after casting into a ready interrupt, per cast, own minus enemy",
             "dazed_casts_diff": "casts while Dazed, per cast, own minus enemy", "blind_attacks_diff": "attacks while Blind per player, own minus enemy"},
    "P.18": {"strip_right_diff": "share of strips on the best target in range, own minus enemy",
             "strip_value_diff": "value of enchantments stripped per 10 s, own minus enemy"},
    "P.19": {"blind_front_secs_diff": "seconds the enemy frontline spent Blind, own minus enemy", "blind_defensive_secs_diff": "seconds Blind from defensive Blinds, own minus enemy"},
    "P.1": {"healer_focus_diff": "share of damage on enemy healers, own minus enemy (Bounty: going after the monks)"},
    "S.scoreboard": {"morale_diff": "morale, own minus enemy (discovery, approved)", "fight_state": "who is winning the fight (fightstate.py; discovery, approved)",
                     "down_diff_s": "time down: enemy minus own seconds until the dead are back (+ = the enemy has more time down) (discovery, approved)", "alive_diff": "alive, own minus enemy (discovery, approved)",
                     "stand": "stand (discovery, approved)", "spike_killable_diff": "players within one spike, own minus enemy (discovery, approved)"},
    "P.2": {"spike_spread_diff": "median spike spread (s), own minus enemy", "spikes_diff": "spikes, own minus enemy"},
    "K.1": {"dps_v_usual_diff": "damage against the usual of the players alive, own minus enemy"},
    "P.5": {"hex_secs_diff": "value-weighted seconds hexes stayed on own players, own minus enemy",
            "hex_right_diff": "share of hex removals that took the most costly hex in range, own minus enemy"},
    "P.21": {"kite_secs_diff": "seconds own players kited enemy melee (chased without being hit), per 10 s, own minus enemy"},
    "P.27": {"prekite_secs_diff": "seconds own players kept their distance from melee heading for them, per 10 s, own minus enemy"},
    "P.22": {"degen_diff": "degeneration put on the other team, pip-seconds per 10 s, own minus enemy"},
    "P.23": {"baits_diff": "enemy interrupts baited (landed on nothing after a cancel), per 10 s, own minus enemy"},
    "P.24": {"knockdowns_diff": "knockdowns landed per 10 s, own minus enemy", "knockdowns_on_casting_diff": "knockdowns on casting targets per 10 s, own minus enemy"},
    "P.25": {"disable_diff": "skill-seconds disabled on the other team per 10 s, own minus enemy"},
    "P.26": {"castprev_diff": "casts punished by Shame, Guilt or Diversion per 10 s, own minus enemy"},
    "C.builds": {"own_hexes": "hex skills on own bars (discovery, approved)", "own_heals": "heal skills on own bars (discovery, approved)"},
    "C.strength": {"strength_gap": "team strength gap"}}, {}),
 "split_chance": ("A.allocation", {
    "S.scoreboard": {"flag_lead": "flag lead (s)", "own_alive": "own alive", "enemy_alive": "enemy alive", "own_main": "own main",
                     "enemy_main": "enemy main", "stand_own": "own team holds the stand", "stand_enemy": "the enemy holds the stand",
                     "split_diff": "players splitting, own minus enemy (discovery, approved)", "turtle_diff": "turtling, own minus enemy (discovery, approved)",
                     "pit_pressure_diff": "pit pressure, own minus enemy (discovery, approved)"},
    "C.clock": {"minute": "minute", "res_in": "seconds to the next res"},
    "C.builds": {"own_speed_power": "speed power on own bars (movepower.py)", "own_escapes": "Shadow Step skills on own bars",
                 "own_snare_power": "snare power on own bars", "enemy_snare_power": "snare power on enemy bars",
                 "spike_build_own": "own build is a spike build (discovery, approved)", "own_knockdowns": "knockdown skills on own bars (discovery, approved)"},
    "C.strength": {"strength_gap": "team strength gap"}}, {}),
 "split_answer": ("P.11", {
    "S.scoreboard": {"flag_lead": "defenders' flag lead (s)", "def_alive": "defenders alive", "att_main": "attackers' main",
                     "split_diff": "players splitting, own minus enemy (discovery, approved)"},
    "A.mesa_free": {"def_free": "defenders alive and not on flag duty", "nearest_to_base": "nearest defender to its base at the split's entry"},
    "C.builds": {"own_area_damage": "area-damage skills on the defenders' bars (discovery, approved)"},
    "A.allocation": {"size": "split size"},
    "C.clock": {"minute": "minute"},
    "C.strength": {"strength_gap": "defending team's strength gap"}}, {}),
 "split_effect": ("R.5", {
    "P.11": {"latency": "seconds until the first defender arrived (60 = never)", "defenders": "defenders who came"},
    "A.allocation": {"size": "split size", "main_diff": "own main minus enemy main meanwhile"},
    "K.8": {"split_healers": "healers in the split"},
    "S.scoreboard": {"def_npc_value": "defenders' pit NPC value when the split entered the base", "def_free": "defenders alive and not on flag duty at entry",
                     "morale_diff": "morale, own minus enemy (discovery, approved)", "flag_lead": "flag lead (discovery, approved)",
                     "lord_damage_diff": "Lord damage, own minus enemy (discovery, approved)"},
    "C.builds": {"enemy_prots": "prot skills on the defenders' bars (discovery, approved)"},
    "K.11": {"def_snare_present": "snare power of the defenders who came (movepower.py)"},
    "K.13": {"split_speed_power": "split members' speed power (movepower.py)",
             "own_escapes_power": "escape power on the splitting team's bars (discovery, approved)"},
    "C.strength": {"strength_gap": "splitting team's strength gap"}}, {}),
 "pit_npc_loss": ("R.5", {
    "A.allocation": {"attackers": "enemy players in the pit", "attacker_healers": "of which healers",
                     "attackers_share": "share of the enemy's live players in the pit",
                     "attackers_outside": "enemy players hitting the pit NPCs from outside the pit (ranged; Denning, session 4u)"},
    "P.11": {"defenders": "own players in the pit", "defender_healers": "of which healers",
             "defenders_elsewhere": "own players alive outside the pit"},
    "S.scoreboard": {"knights": "own knights alive", "archers": "own pit archers alive", "bodyguard": "own Bodyguard alive",
                     "full_pit_targets": "pit NPCs alive (targets the defending monks must watch)"},
    "K.6": {"npc_healing_10s": "healing on own pit NPCs and Lord in the last 10 s"},
    "C.builds": {"attackers_lord_dps": "attackers' measured damage per second against NPCs", "attackers_area_damage": "area-damage skills on the attackers' bars"},
    "C.clock": {"seconds_in_pit": "seconds the enemy has been in the pit", "res_in": "seconds to the next res", "minute": "minute"},
    "C.strength": {"strength_gap": "defending team's strength gap"}}, {}),
 "collapse": ("R.1", {
    "P.11": {"latency": "seconds until the first defender arrived (60 = never)"},
    "P.9": {"defenders_10s": "defenders arriving within 10 s of the first (arrival spread)",
            "contact_diff": "defenders arriving within 5 s of the first, minus the split's size (numbers at contact)",
            "npc_hit_to_arrival": "seconds from the split's first hit on an NPC to the first defender's arrival",
            "res_in_at_arrival": "seconds to the next res when the first defender arrived"},
    "K.13": {"escape_ready": "split members' speed skills off recharge when the first defender arrived",
             "split_speed_power": "split members' speed power (movepower.py)", "split_escapes": "split members' Shadow Step skills"},
    "K.11": {"def_snare_present": "snare power of the defenders who came (movepower.py; how strong, not just whether)"},
    "K.9": {"split_dp": "worst morale among the split members (death penalty lowers max health; Denning)"},
    "K.5": {"split_healers": "healers on the split", "split_self_defence": "self-heals and self-defence skills on the split members' bars (Denning: can it be killed)",
            "healing_monks_enemy": "healing monks on the defending team (discovery, approved)"},
    "K.1": {"def_dps": "the defenders who came: their usual damage per second, summed (Denning: can they kill it)"},
    "S.scoreboard": {"def_npc_value": "defending pit NPCs alive, in win points (Denning: what the split can get)"},
    "C.builds": {"split_npc_dps": "split members' measured damage per second against NPCs (Denning: what the split can get)"},
    "P.20": {"depth_at_arrival": "nearest split member's distance to the defending pit when the first defender arrived",
             "depth_median": "nearest split member's median distance to the defending pit over the split"},
    "A.allocation": {"size": "split size", "main_diff": "own main minus enemy main meanwhile"},
    "C.strength": {"strength_gap": "splitting team's strength gap"}}, {}),
}
# links whose features are also tested one at a time (Denning: which reading of collapse timing matters is for the data)
EACH = {"collapse": ["P.9", "P.20"]}

# ---- the kind of every input (Denning, November 2026 review; docs/SPEC.md section 3 and 5). The kind decides what a
# model may do with it: context and state are adjustment and never a fix; decision and execution inputs are the only
# candidates for "what should have been done" and "what went wrong"; concurrent response is not an input at all.
KIND_BY_GROUP = {"C.builds": "context", "C.matchup": "context", "C.strength": "context", "C.map": "context", "C.flux": "context",
                 "S.scoreboard": "state", "C.clock": "state", "A.allocation": "state", "A.mesa_free": "state", "R.1": "state",
                 "R.3": "state", "K.9": "state", "K.8": "state"}
# features whose kind is not their group's: choices a team made at the moment
DECISION_FEATURES = {"pushed", "runner_class", "runner_line", "escort", "size", "defenders", "defenders_10s", "contact_diff",
                     "split_healers", "split_size", "own_flag_duty", "enemy_flag_duty"}
# the kind of an input in one node when it differs from the feature's usual kind: the same count is the acting team's
# own choice in one node and the enemy's situation in another (the readability test, 2026-11-09: perspective)
NODE_KINDS = {
    "run_defence": {"escort": "state", "runner_class": "state", "min_capture_s": "state"},     # the enemy's runner, escorts and carry
    "capture_speed": {"escort": "state", "runner_class": "state", "min_capture_s": "state", "defenders_free": "decision"},
    "power_play": {"size": "state"},                                               # how many the enemy is short
    "flag_swing": {"enemy_flag_duty": "state"},
    "split_answer": {"size": "state"},                                             # the enemy's split
    "split_effect": {"latency": "state", "defenders": "state", "def_snare_present": "state"},   # the defenders' answer
    "pit_npc_loss": {"defenders": "decision", "defender_healers": "decision", "defenders_elsewhere": "decision"},
    "collapse": {"healing_monks_enemy": "state", "latency": "state", "defenders_10s": "state", "contact_diff": "state",
                 "def_snare_present": "state", "def_dps": "state", "res_in_at_arrival": "state"},   # rows are the split's; the defenders are the enemy
}
# allocation decisions (Denning, R-282): how many to send, escort, defend with, keep on flag duty. The selection check
# flags them like markers (they persist through a match), but they are choices a team can change, so they may still be
# a fix; the report says so beside them.
ALLOCATION = {
    "run_outcome": {"escort"}, "capture_speed": {"defenders_free"}, "flag_swing": {"own_flag_duty"},
    "split_effect": {"size", "split_healers"}, "pit_npc_loss": {"defenders", "defender_healers", "defenders_elsewhere"},
    "collapse": {"size", "split_healers"},
}
# expected direction of every execution input (Denning, R-285: as the win model has direction corrections): +1 = more of
# it should help the row's team, -1 = more of it should hurt. An input whose fitted curve runs the other way is
# labelled "reads backwards: likely a reaction" (disabling more because the kill is not coming; healing NPCs because
# they are being hit) and is never a fault or a fix, though it stays in the fit as adjustment. Signs ruled by Denning
# 2026-11-09 (R-288 to R-291); an input with no entry has no expected direction yet and is read as the data says.
EXPECTED = {
    "run_outcome": {"crippled_so_far": -1, "knocked_down_so_far": -1, "other_control_so_far": -1, "damage_so_far": -1, "pushers_so_far": -1,
                    "min_capture_s": -1},                     # runner_escapes retired (R-289: a Shadow Step drops the flag now)
    "run_defence": {"pushers_so_far": +1, "control_so_far": +1, "damage_so_far": +1, "def_snare_near": +1},
    "capture_speed": {"pushers_10s": +1, "control_10s": +1, "damage_10s": +1, "def_snare_near": +1},
    "power_play": {"dps_v_usual": +1, "spikes_10s": +1, "spike_spread": -1, "spikes_on_healers": +1, "healer_damage_share": +1,
                   "blind_secs_on_own_10s": -1, "knockdowns_10s": +1, "knockdowns_on_casting_10s": +1, "disable_10s": +1,
                   "castprev_10s": +1, "degen_10s": +1},
    # fight outcome (Denning, R-290): good = Blind on their frontline, defensive Blind, damage v the usual, the right hex
    # removed, kiting, degen, baited interrupts, knockdowns (and on casters), disables, cast prevention, strips on the
    # right target and their value; bad = casting into a ready interrupt, casting while Dazed, attacking while Blind,
    # loose spikes, impactful hexes on own players (value-weighted). No sign yet for pre-kiting (unknown), peel (good
    # when playing defensively, not for a global fight), damage focus on healers (left unsigned by Denning, R-331: it depends on offence or defence, R-304): the data reads it.
    "fight_outcome": {"ready_interrupt_diff": -1, "dazed_casts_diff": -1, "blind_attacks_diff": -1,
                      "strip_right_diff": +1, "strip_value_diff": +1, "blind_front_secs_diff": +1, "blind_defensive_secs_diff": +1,
                      "spike_spread_diff": -1, "spikes_diff": +1, "dps_v_usual_diff": +1, "hex_secs_diff": -1,      # spikes: more helps (R-331)
                      "hex_right_diff": +1, "kite_secs_diff": +1, "degen_diff": +1, "baits_diff": +1,
                      "knockdowns_diff": +1, "knockdowns_on_casting_diff": +1, "disable_diff": +1, "castprev_diff": +1},
    "split_effect": {"split_speed_power": +1, "own_escapes_power": +1},
    "pit_npc_loss": {"npc_healing_10s": +1},
    "collapse": {"escape_ready": +1, "split_speed_power": +1, "split_escapes": +1},
}
# is a high result good for the row's team? (collapse rows are the split's: a member dying is bad; run defence and pit
# NPC loss rows are the defender's: the enemy capturing or an NPC falling is bad; split answer: more seconds is bad)
GOOD_HIGH = {"collapse": False, "run_defence": False, "pit_npc_loss": False, "split_answer": False}
# features in a play group (P.10 run timing) that describe the situation, not a play: the flag model's readings
STATE_FEATURES = {"stand_own", "stand_enemy", "enemy_boost_in", "own_boost_in", "flag_lead", "own_eta", "enemy_eta", "own_carrying",
                  "enemy_carrying", "own_cap_before_boost", "enemy_cap_before_boost", "waiting_runner", "backup_flag", "enemy_power_play",
                  "window_s", "checkpoint_s"}
# what the other team did during the window: measured (lnrows.py keeps it in every row) and shown beside the node's
# reading as "what the enemy did", never fitted (M2: a cause must be measured before the result's window)
CONCURRENT = {
    "power_play": {"enemy_prots_10s": "enemy prot casts per 10 s", "enemy_heal_s": "enemy healing per second",
                   "enemy_kite_10s": "seconds the enemy kited or pre-kited own melee, per 10 s",
                   "enemy_baits_10s": "own interrupts the enemy baited (landed on nothing after a cancel), per 10 s"},
    "pit_npc_loss": {"npc_damage_5s": "damage on the pit NPCs in the last 5 s (the loss happening, not a cause)"},
}
# the links those measures used to stand for, kept on the map with the status "concurrent" (not fitted)
CONCURRENT_LINKS = {("K.5", "K.4"), ("P.21", "K.4"), ("P.23", "K.4"), ("K.1", "R.5")}
# inputs the data can carry (M4): one input per EVENTS_PER_INPUT events (the rarer class for yes/no nodes; rows / 40 for
# number nodes). Pruning order: Claude's links not clear yet, Claude's links rejected, approved discoveries not clear
# yet, then Denning's links not clear yet (R-278; they return as the data grows). Supported links, and links Denning
# ruled to keep ("denning_keep" on the map), are never pruned. Pruned inputs go to the map's waiting list.
EVENTS_PER_INPUT = 20
REGRESSION_ROWS_PER_INPUT = 40


def kind_of(node, f):
    """context, state, decision or execution for a node's input (concurrent measures are not inputs)."""
    if f in CONCURRENT.get(node, {}): return "concurrent"
    if f in NODE_KINDS.get(node, {}): return NODE_KINDS[node][f]
    if f in STATE_FEATURES: return "state"
    if f in DECISION_FEATURES: return "decision"
    g = group_of(node, f)
    if g is None: return "state"
    return KIND_BY_GROUP.get(g, "execution")


def group_of(node, f):
    tgt, groups, base = SPEC[node]
    for g, fs in groups.items():
        if f in fs: return g
    return None
# why each link that a node needs and the map may lack is a hypothesis, and who it came from
NEW_LINK_WHY = {
    ("P.21", "R.2"): ("a player who kites enemy melee avoids damage and wastes the frontline's time (Denning, session 4u)", "Denning"),
    ("P.27", "R.2"): ("keeping distance from melee heading for you avoids the first hit (Denning, session 4u; split from P.21, R-283)", "Denning"),
    ("P.22", "R.2"): ("degen pressure (a ranger's poison on the whole team, a degen mesmer) wears a team down without showing as damage (Denning, session 4u)", "Denning"),
    ("P.23", "R.2"): ("a player who fakes out an interrupt wastes it (Denning, session 4u)", "Denning"),
    ("P.24", "R.2"): ("offensive knockdowns (a warrior landing many) stop casts and set up kills (Denning, session 4u)", "Denning"),
    ("P.25", "R.2"): ("disables (Complicate, Blackout, Power Lock, Power Block) take the enemy's key skills away (Denning, session 4u)", "Denning"),
    ("P.26", "R.2"): ("cast prevention (Shame, Diversion, Guilt) stops the enemy's casts (Denning, session 4u)", "Denning"),
    ("P.21", "K.4"): ("enemies kiting a power play's melee waste its time (Denning, session 4u)", "Denning"),
    ("P.22", "K.4"): ("degen pressure helps a power play wear the enemy down (Denning, session 4u)", "Denning"),
    ("P.23", "K.4"): ("baited interrupts leave the enemy healers free (Denning, session 4u)", "Denning"),
    ("P.24", "K.4"): ("offensive knockdowns convert a power play (Denning, session 4u)", "Denning"),
    ("P.25", "K.4"): ("disables on the enemy healers convert a power play (Denning, session 4u)", "Denning"),
    ("P.26", "K.4"): ("cast prevention on the enemy healers converts a power play (Denning, session 4u)", "Denning"),
    ("C.builds", "R.2"): ("hex and heal skills on the bars change fights: found by discovery, approved by Denning", "Denning"),
    ("C.builds", "K.4"): ("enemy strips against own prots change power plays: found by discovery, approved by Denning", "Denning"),
    ("C.builds", "P.11"): ("area damage on the defenders' bars changes split answers: found by discovery, approved by Denning", "Denning"),
    ("K.5", "R.3"): ("own healing monks help defend against runs: found by discovery, approved by Denning", "Denning"),
    ("K.11", "R.3"): ("control on the runner (Cripple, knockdowns) stops a run; read at the same point of every run", "Denning"),
    ("C.strength", "R.3"): ("stronger teams play better at everything; kept in every model so play isn't confused with strength", "Claude"),
    ("S.scoreboard", "R.3"): ("a flag lead tends to grow or shrink by how it stands now (boost and run timing)", "Claude"),
    ("R.1", "R.3"): ("deaths lose flag position: the runner, the escort or the main", "Claude"),
    ("C.clock", "R.3"): ("the res clock and the minute change what a run can do", "Claude"),
    ("A.mesa_free", "R.3"): ("defenders free to push a runner slow or stop the enemy's capture", "Denning"),
    ("A.allocation", "K.4"): ("a power play is any numbers advantage at main, an 8v7 while the enemy runs included", "Denning"),
    ("A.allocation", "R.2"): ("numbers in a fight decide much of it", "Denning"),
    ("P.13", "R.2"): ("frontline defensive peel (hitting or snaring enemies on its own backline) protects the healers", "Denning"),
    ("P.17", "R.2"): ("wrong casts lose fights: casting into ready interrupts without cancelling, casting while Dazed, attacking while Blind", "Denning"),
    ("P.18", "R.2"): ("strips on the right target (Elementalist enchantments when defensive, prots off a target under attack)", "Denning"),
    ("P.19", "R.2"): ("Blind on the enemy frontline, above all on players hitting own healers, is defensive play", "Denning"),
    ("P.2", "R.2"): ("off spike timing fails to kill", "Denning"),
    ("K.1", "R.2"): ("damage output against the role's usual", "Denning"),
    ("P.5", "R.2"): ("the right hexes removed, and fast", "Denning"),
    ("C.strength", "R.2"): ("stronger teams play better at everything; kept in every model so play isn't confused with strength", "Claude"),
    ("S.scoreboard", "A.allocation"): ("a team splits from the situation: flag lead, stand, numbers", "Claude"),
    ("C.clock", "A.allocation"): ("the res clock and the minute change when a split pays", "Claude"),
    ("C.builds", "A.allocation"): ("split builds (speed, snares) and the enemy's snares decide whether a split is possible", "Claude"),
    ("K.13", "R.3"): ("the runner's speed skills and Shadow Steps decide how fast a flag comes in (Nick: Shadow of Haste at main keeps a team ahead on flags)", "Denning"),
    ("K.11", "R.1"): ("how strong the defenders' snares are, not just whether there is one, decides whether a collapse kills (Bounty, Denning)", "Denning"),
    ("K.13", "R.1"): ("the splitters' speed and Shadow Steps let them escape a collapse", "Denning"),
    ("K.11", "R.5"): ("the defenders' snares slow a split's work on the NPCs", "Denning"),
    ("K.13", "R.5"): ("a fast split gets in and out of the base", "Denning"),
    ("S.scoreboard", "R.2"): ("the state at the fight's start (morale, numbers, time down, the stand, players within one spike): found by discovery, approved by Denning", "Denning"),
    ("S.scoreboard", "K.4"): ("time down and flag carriers when the power play starts: found by discovery, approved by Denning", "Denning"),
    ("S.scoreboard", "R.5"): ("morale, flag lead and Lord damage when a split enters: found by discovery, approved by Denning", "Denning"),
    ("C.builds", "R.5"): ("the defenders' prots make a split's NPC kills harder: found by discovery, approved by Denning", "Denning"),
    ("C.builds", "R.3"): ("snare skills on the bars change whether runs get through: found by discovery, approved by Denning", "Denning"),
    ("P.10", "R.3"): ("who carries the flag (warrior, dervish, midline, monk) is a strategic choice (Denning)", "Denning"),
    ("S.scoreboard", "P.11"): ("a defending team that is itself splitting answers later: found by discovery, approved by Denning", "Denning"),
    ("P.1", "R.2"): ("going after the healers (Bounty: target choice costs time; the data: groups on the healers kill more)", "Bounty"),
    ("C.strength", "A.allocation"): ("stronger teams play better at everything; kept in every model so play isn't confused with strength", "Claude"),
    ("A.mesa_free", "P.11"): ("free defenders near the base answer a split sooner", "Denning"),
    ("A.allocation", "P.11"): ("a bigger split draws more defenders", "Claude"),
    ("P.9", "R.1"): ("collapse timing: defenders arriving together kill a split member", "Denning"),
    ("C.builds", "R.1"): ("a snare on the split defender makes a collapse on a lone attacker much more likely to kill", "Denning"),
    ("A.allocation", "R.1"): ("a split outnumbered at the point of contact dies", "Claude"),
    ("C.strength", "R.1"): ("stronger teams play better at everything; kept in every model so play isn't confused with strength", "Claude"),
    ("C.strength", "R.5"): ("stronger teams play better at everything; kept in every model so play isn't confused with strength", "Claude"),
    ("C.strength", "P.11"): ("stronger teams play better at everything; kept in every model so play isn't confused with strength", "Claude"),
    ("C.clock", "P.11"): ("the res clock and the minute change how a split is answered", "Claude"),
    ("K.11", "R.3"): ("control on the runner (Cripple, knockdowns) stops a run; read at the same point of every run", "Denning"),
    ("P.20", "R.1"): ("the deeper the splitters are in the base (nearer the pit), the more likely they die to a collapse", "Denning"),
    ("S.scoreboard", "R.5"): ("a pit already short of NPCs, or a base with few free defenders, loses an NPC to a split more easily", "Claude"),
    ("P.11", "R.5"): ("defenders and healers back in the pit keep the NPCs alive (pit NPC loss node, Denning batch 10)", "Denning"),
    ("K.6", "R.5"): ("healing on the pit NPCs keeps them alive", "Claude"),
    ("K.1", "R.5"): ("damage landing on the pit NPCs", "Claude"),
    ("C.clock", "R.5"): ("time in the pit and the res clock", "Claude"),
    ("K.9", "R.1"): ("death penalty on the split character lowers its health, so a collapse kills it more easily (Denning, batch 10)", "Denning"),
    ("K.5", "R.1"): ("a split that can heal or defend itself may not be killable, so collapsing on it wastes players (Denning, batch 10)", "Denning"),
    ("K.1", "R.1"): ("the defenders' damage decides whether they can kill the split (Denning, batch 10)", "Denning"),
    ("S.scoreboard", "R.1"): ("what the split can get NPC-wise sets how much a collapse is worth (Denning, batch 10)", "Denning"),
}
# fitting settings per node (after batch 9, the three nodes that never beat their baseline, reworked): the number nodes
# judged on typical error are fitted with a robust loss (pseudo-Huber: big swings don't drag every reading toward
# them, so the readings sit nearer the middle that typical error rewards); split effect (a few hundred cases) with
# fewer bins, larger leaves and more smoothing, so its curves don't memorize matches
NODE_FIT = {"flag_swing": {"objective": "pseudo_huber"}, "capture_speed": {"objective": "pseudo_huber"},
            "split_effect": {"max_bins": 8, "min_samples_leaf": 40, "smoothing_rounds": 300, "max_rounds": 200}}
NEW_NODES = [
    {"id": "P.21", "layer": "play", "name": "Kiting", "description": "kiting enemy melee (warriors, dervishes, assassins): seconds chased without being hit", "how": "pressure.py"},
    {"id": "P.27", "layer": "play", "name": "Pre-kiting", "description": "distance kept from enemy melee heading for the player, before contact (split from P.21, Denning R-283: kiting stays by his ruling, pre-kiting sits as the data reads it)", "how": "pressure.py"},
    {"id": "P.22", "layer": "play", "name": "Degen pressure", "description": "degeneration put on the enemy (conditions and degen hexes), pip-seconds; the replays record degen as no damage", "how": "pressure.py"},
    {"id": "P.23", "layer": "play", "name": "Baited interrupts", "description": "enemy interrupts that landed on nothing because the player cancelled", "how": "pressure.py"},
    {"id": "P.24", "layer": "play", "name": "Offensive knockdowns", "description": "knockdowns landed on enemies, and on casting targets", "how": "pressure.py"},
    {"id": "P.25", "layer": "play", "name": "Disables", "description": "skill-seconds disabled on enemies by Complicate, Power Lock, Power Block and Blackout", "how": "pressure.py"},
    {"id": "P.26", "layer": "play", "name": "Cast prevention", "description": "Shame, Guilt and Diversion on enemies: the casts they punished (a hex that catches a cast ends at once, so seconds up counted the misses: R-330)", "how": "pressure.py"},
    {"id": "P.17", "layer": "play", "name": "Wrong casts", "description": "casting into a ready interrupt without cancelling, casting while Dazed, attacking while Blind (every role)", "how": "eventlayer.py casts"},
    {"id": "P.18", "layer": "play", "name": "Enchantment strips", "description": "strips on the best target in range, valued from data (an enchantment's recorded output plus the bearer's measured drop after a strip)", "how": "eventlayer.py strips, values()"},
    {"id": "P.20", "layer": "play", "name": "Split depth", "description": "how deep a split plays in the enemy base: its nearest member's distance to the defending pit", "how": "lnrows.py collapse rows"},
    {"id": "P.19", "layer": "play", "name": "Blind on enemies", "description": "Blind on the enemy frontline, and on players hitting own healers (defensive)", "how": "eventlayer.py blinds"},
]


def features(node):
    tgt, groups, base = SPEC[node]
    return list(base) + [f for g in groups.values() for f in g]


def describe(node, f):
    tgt, groups, base = SPEC[node]
    if f in base: return base[f]
    for g in groups.values():
        if f in g: return g[f]
    return CONCURRENT.get(node, {}).get(f, "")


def input_cap(node, y):
    """How many inputs the node's data can carry (M4)."""
    n = len(y)
    if node in REGRESSION: return max(3, int(n // REGRESSION_ROWS_PER_INPUT))
    pos = int(np.sum(np.asarray(y) == 1)); return max(3, int(min(pos, n - pos) // EVENTS_PER_INPUT))


def _map_links():
    try: c = json.load(open(MAP))
    except Exception: return {}
    return {(l["from"], l["to"]): l for l in c.get("links", [])}


def prune_plan(node, X, y, prev=None):
    """Which inputs to leave out so the count fits the data (M4), in the pruning order; never supported links or links
    Denning ruled to keep (R-278 lets his not-clear links go last). prev = the node's last summary (its link statuses and term importances), if any.
    Returns (kept features, [{feature, group, reason}])."""
    feats = [c for c in X.columns]
    cap = input_cap(node, y)
    tgt, groups, base = SPEC[node]
    if len(feats) <= cap: return feats, [], cap
    links = _map_links()
    status = {l["from"]: l["status"] for l in (prev or {}).get("links", [])}
    imp = {t["term"]: t.get("importance") or 0 for t in (prev or {}).get("terms", [])}
    from lnrows import APPROVED
    approved = set(v.split(".", 1)[-1] for v in APPROVED.get(node, []))
    def rank(f):
        g = group_of(node, f)
        if f in base or g is None: return None
        L = links.get((g, tgt), {})
        src = L.get("source", "Claude"); st = status.get(g, L.get("status", "hypothesis"))
        if st == "supported" or L.get("denning_keep"): return None
        if src == "Denning" and f not in approved: return (3, imp.get(f, 0), "Denning's link, not clear yet (R-278)")
        if f in approved: return (2, imp.get(f, 0), "approved discovery, not clear yet")
        if st == "rejected": return (1, imp.get(f, 0), "Claude's link, rejected")
        return (0, imp.get(f, 0), "Claude's link, not clear yet")
    cands = sorted(((rank(f), f) for f in feats if rank(f) is not None), key=lambda x: (x[0][0], x[0][1]))
    drop = []
    for r, f in cands:
        if len(feats) - len(drop) <= cap: break
        drop.append({"feature": f, "group": group_of(node, f), "reason": r[2]})
    dropped = {d["feature"] for d in drop}
    return [f for f in feats if f not in dropped], drop, cap


def selection_check(node, df, X, y, kinds, folds=None):
    """M5: does a decision or execution input predict the same team's PREVIOUS result of this kind in the match as well
    as the next one? If so it marks the situation rather than causing the result (Crippled runners capture more
    because runs that get far get Crippled). Association = AUC for yes/no nodes, |Spearman| for number nodes; spread
    from resampling whole matches. Flag when the previous association is at least three quarters of the next one and
    its range stays clear of none."""
    from sklearn.metrics import roc_auc_score
    from scipy.stats import spearmanr
    reg = node in REGRESSION
    d = df[["match", "team", "t"]].copy(); d["y"] = np.asarray(y, float)
    d = d.sort_values(["match", "team", "t"])
    d["y_prev"] = d.groupby(["match", "team"])["y"].shift(1)
    yp = d["y_prev"].reindex(df.index).values
    ok = ~np.isnan(yp)
    if ok.sum() < 60: return {}
    matches = df["match"].values
    rng = np.random.default_rng(7); um = np.unique(matches[ok])
    def assoc(v, lab, idx):
        v, lab = v[idx], lab[idx]
        m = ~np.isnan(v)
        if m.sum() < 30: return None
        v, lab = v[m], lab[m]
        if reg:
            if np.std(v) == 0 or np.std(lab) == 0: return None
            return abs(float(spearmanr(v, lab).correlation))
        if len(set(lab)) < 2 or np.std(v) == 0: return None
        return abs(float(roc_auc_score(lab, v)) - 0.5)
    out = {}
    for f in X.columns:
        if kinds.get(f) not in ("decision", "execution"): continue
        v = X[f].values.astype(float)
        a_next = assoc(v, np.asarray(y, float), ok); a_prev = assoc(v, yp, ok)
        if a_next is None or a_prev is None: continue
        boots = []
        for _ in range(25):
            pick = set(rng.choice(um, len(um), replace=True))
            idx = ok & np.isin(matches, list(pick))
            b = assoc(v, yp, idx)
            if b is not None: boots.append(b)
        lo = float(np.percentile(boots, 5)) if len(boots) >= 10 else 0.0
        # "as well as the next" (Denning): the previous association at least as strong as the next one and clearly above
        # none. A persistent cause (defenders standing in the pit) reads much like a marker here; the flag says the test
        # can't tell them apart, and the ruling is that such an input is not offered as a fix
        marks = bool(a_prev >= 1.0 * a_next and lo > 0.02 and a_prev > 0.03)
        alloc = f in ALLOCATION.get(node, set())
        out[f] = {"next": round(a_next, 3), "previous": round(a_prev, 3), "previous_low": round(lo, 3), "marks_situation": marks,
                  "allocation": alloc, "fix_allowed": (not marks) or alloc}
    return out


def direction_check(node, terms):
    """R-285: for every execution input with an expected direction, does the fitted curve run that way? Returns
    {feature: {"expected": +1/-1, "fitted": +1/-1/0, "reads_backwards": bool}}; fitted = the sign of the Spearman
    correlation between the curve's bin midpoints and its points (0 when |rho| < 0.3, read as flat), turned to the
    row team's good side with GOOD_HIGH so the two can be compared."""
    from scipy.stats import spearmanr
    good_high = GOOD_HIGH.get(node, True)
    out = {}
    for t in terms:
        f = t["term"]; exp = EXPECTED.get(node, {}).get(f)
        if exp is None or t.get("kind") != "execution": continue
        cv = [c for c in t.get("curve", []) if c.get("from") is not None and c.get("to") is not None]
        if len(cv) < 3: continue
        xs = [(c["from"] + c["to"]) / 2 for c in cv]; ys = [c["points"] for c in cv]
        if len(set(xs)) < 3 or len(set(ys)) < 2: continue
        rho = spearmanr(xs, ys).correlation
        fitted = 0 if rho != rho or abs(rho) < 0.3 else (1 if rho > 0 else -1)
        toward_good = fitted * (1 if good_high else -1)          # +1: more of it reads as good for the row's team
        out[f] = {"expected": exp, "fitted_toward_good": toward_good, "rho": round(float(rho), 2) if rho == rho else None,
                  "reads_backwards": bool(toward_good != 0 and toward_good != exp)}
    return out


# ---------------------------------------------------------------- rows (lnrows.py)
from lnrows import node_rows, _rows_job, _vhash


# ---------------------------------------------------------------- fitting
def _ebm(n_matches, regression, bags=4, node=None, y=None):
    from interpret.glassbox import ExplainableBoostingClassifier as EBM, ExplainableBoostingRegressor as EBR
    kw = dict(max_bins=16, outer_bags=bags, min_samples_leaf=20 if not regression else 8, max_rounds=400, interactions=0, random_state=7)
    kw.update({k: v for k, v in NODE_FIT.get(node, {}).items() if regression or k != "objective"})
    if kw.get("objective") == "pseudo_huber" and y is not None:
        # the loss turns from squared to absolute at delta, set to the training rows' typical spread (median absolute
        # deviation); the library's default of 1 diverges on results measured in tens of seconds (found 2026-11-07)
        yy = np.asarray(y, float); kw["objective"] = f"pseudo_huber:delta={max(1.0, float(np.median(np.abs(yy - np.median(yy))))):.2f}"
    return (EBR if regression else EBM)(**kw)


class Centered:
    """A regression EBM fitted on the result less its training median (added back when predicting): a robust loss
    started far from the data's level takes huge steps and diverges (capture speed, about 40 s, found 2026-11-07).
    Everything else (curves, importances) is read from the inner model."""
    def __init__(self, e): self.inner, self.offset = e, 0.0

    def fit(self, X, y):
        y = np.asarray(y, float); self.offset = float(np.median(y))
        self.inner.fit(X, y - self.offset); return self

    def predict(self, X): return self.inner.predict(X) + self.offset

    def __getattr__(self, k):
        if k.startswith("__") or k in ("inner", "offset"): raise AttributeError(k)
        return getattr(self.inner, k)


def _job(job):
    """One fit: a held-out fold's score (and the baseline's), or the final model. Top level for parallel.py."""
    kind, regression, n, Xtr, ytr, Xte, yte = job[:7]
    node = job[7] if len(job) > 7 else None
    keep = len(job) > 8 and job[8]        # the "all" variant's fold models are kept: held-out models for step 4
    # the held-out link tests use 2 bags (the same for every variant, so the comparison is fair; measured 2026-11-07:
    # half the time); the final readable model uses 4
    e = _ebm(n, regression, 4 if kind == "full" else 2, node, ytr)
    if regression and NODE_FIT.get(node, {}).get("objective") == "pseudo_huber": e = Centered(e)
    e = e.fit(Xtr, ytr)
    if kind == "full": return e
    if regression:
        p = e.predict(Xte); return {"score": float(np.mean(np.abs(yte - p))), "base": float(np.mean(np.abs(yte - np.median(ytr)))), "n": len(yte),
                                    **({"model": e} if keep else {})}
    p = np.clip(e.predict_proba(Xte)[:, 1], .002, .998); q = float(np.clip(np.mean(ytr), .002, .998))
    ll = lambda pp: float(np.mean(-(yte * np.log(pp) + (1 - yte) * np.log(1 - pp))))
    return {"score": ll(p), "base": ll(np.full(len(yte), q)), "n": len(yte), **({"model": e} if keep else {})}


def frame(node, ids, V):
    import pandas as pd, parallel
    from integrity import usable
    ids = usable(list(ids))
    rows = [r for L in parallel.run(_rows_job, [(node, rid, V) for rid in ids]) for r in L]
    df = pd.DataFrame(rows)
    feats = features(node)
    for f in feats:
        if f not in df: df[f] = np.nan
    y = df["y"].astype(float if node in REGRESSION else int)
    return df, df[feats].astype(float), y, df["match"]


def fit_all(ids, nodes=None, V=None):
    """Fit every node, its held-out score, and each link's strength (refit without the link's features), all fits
    pooled on every core. Returns {node: summary}; writes data/model/nodes/L_<node>.json."""
    import parallel, eventlayer as EL
    from sklearn.model_selection import GroupKFold
    V = V or EL.load_values() or EL.values(ids)
    nodes = nodes or list(SPEC)
    prep, jobs, owner = {}, [], []
    for node in nodes:
        df, X, y, g = frame(node, ids, V)
        if len(df) < 40 or g.nunique() < 6 or (node not in REGRESSION and y.nunique() < 2): continue
        reg = node in REGRESSION
        # M4: inputs the data can carry; the plan reads the node's last summary for statuses and importances
        prev = None
        try: prev = json.load(open(os.path.join(NODE_DIR, f"L_{node}.json")))
        except Exception: pass
        keep, pruned, cap = prune_plan(node, X, y, prev)
        X = X[keep]
        folds = list(GroupKFold(n_splits=6).split(X, y, g))
        groups_in = {grp: [f for f in fs if f in keep] for grp, fs in SPEC[node][1].items()}
        groups_in = {grp: fs for grp, fs in groups_in.items() if fs}
        variants = [("all", list(X.columns))] + [(grp, [c for c in X.columns if c not in fs]) for grp, fs in groups_in.items()]
        for grp in EACH.get(node, []):
            variants += [(f"{grp}:{f}", [c for c in X.columns if c != f]) for f in groups_in.get(grp, [])]
        prep[node] = (df, X, y, g, folds, variants, pruned, cap, groups_in)
        for vn, cols in variants:
            for tr, te in folds:
                jobs.append(("fold", reg, g.iloc[tr].nunique(), X.iloc[tr][cols], y.iloc[tr].values, X.iloc[te][cols], y.iloc[te].values, node,
                             vn == "all")); owner.append((node, vn))
        jobs.append(("full", reg, g.nunique(), X, y.values, None, None, node)); owner.append((node, "full"))
    res = parallel.run(_job, jobs)
    out = {}
    for node, (df, X, y, g, folds, variants, pruned, cap, groups_in) in prep.items():
        reg = node in REGRESSION
        R_ = collections.defaultdict(list)
        for o, r in zip(owner, res):
            if o[0] == node: R_[o[1]].append(r)
        e = R_["full"][0]
        allf = R_["all"]
        wavg = lambda L, k: sum(x[k] * x["n"] for x in L) / sum(x["n"] for x in L)
        val = {"glass box": round(wavg(allf, "score"), 4), "simple baseline": round(wavg(allf, "base"), 4),
               "metric": "mean absolute error (s)" if reg else "log loss"}
        val["verdict"] = "adds to the simple baseline" if val["glass box"] < val["simple baseline"] - (0.5 if reg else 0.0005) else "no better than the simple baseline yet"
        links = []
        for grp, fs in groups_in.items():
            d_ = [w["score"] - a_["score"] for w, a_ in zip(R_[grp], allf)]       # positive = the link helps on unseen matches
            mu = statistics.mean(d_); se = statistics.stdev(d_) / math.sqrt(len(d_)) if len(d_) > 1 else float("inf")
            status = "supported" if mu - 2 * se > 0 else "rejected" if mu + 2 * se < 0 else "not clear yet"
            each = []
            for f in (fs if grp in EACH.get(node, []) else []):
                d2 = [w["score"] - a_["score"] for w, a_ in zip(R_[f"{grp}:{f}"], allf)]
                m2 = statistics.mean(d2); s2 = statistics.stdev(d2) / math.sqrt(len(d2))
                each.append({"feature": f, "strength": round(m2, 4), "plus_minus": round(s2, 4),
                             "status": "supported" if m2 - 2 * s2 > 0 else "rejected" if m2 + 2 * s2 < 0 else "not clear yet"})
            links.append({"from": grp, "to": SPEC[node][0], "features": list(fs), "strength": round(mu, 4 if not reg else 2),
                          "plus_minus": round(se, 4 if not reg else 2), "status": status, **({"each": each} if each else {})})
        terms = M.readable(e, list(X.columns), X) if not reg else __import__("nodes").readable_seconds(e, list(X.columns), X)
        kinds = {f: kind_of(node, f) for f in X.columns}
        for t in terms: t["description"] = describe(node, t["term"]); t["kind"] = kinds.get(t["term"])
        rate = None if reg else round(float(y.mean()), 3)
        # M5: the selection check on every decision and execution input
        sel = selection_check(node, df, X, y, kinds)
        # marks_situation is the set that blocks fixes: flagged inputs that are not allocation decisions (R-282);
        # marks_allocation lists the flagged allocation decisions, labelled on the page but still allowed as fixes
        marks = sorted(f for f, v in sel.items() if v["marks_situation"] and not v.get("allocation"))
        marks_alloc = sorted(f for f, v in sel.items() if v["marks_situation"] and v.get("allocation"))
        dirs = direction_check(node, terms)
        backwards = sorted(f for f, v in dirs.items() if v["reads_backwards"])
        for t in terms:
            if t["term"] in backwards: t["reads_backwards"] = True
        for l in links: l["kinds"] = sorted({kinds[f] for f in l["features"]})
        summary = {"node": node, "target": SPEC[node][0], "matches": int(g.nunique()), "rows": int(len(y)), "rate": rate,
                   "mean": round(float(y.mean()), 1) if reg else None, "validation": val, "links": links, "terms": terms,
                   "kinds": kinds, "input_cap": cap, "inputs": len(X.columns), "pruned": pruned,
                   "concurrent": {f: describe(node, f) for f in CONCURRENT.get(node, {})},
                   "selection": sel, "marks_situation": marks, "marks_allocation": marks_alloc,
                   "directions": dirs, "reads_backwards": backwards,
                   "note": ("seconds added to (or taken off) the result, against the average" if reg else
                            "points = change in the chance of the result for an otherwise even (50%) case")}
        os.makedirs(NODE_DIR, exist_ok=True)
        json.dump(summary, open(os.path.join(NODE_DIR, f"L_{node}.json"), "w"), indent=1)
        _MODELS[node] = (e, list(X.columns))
        # held-out models for step 4 (causalchain.py): each match is explained by the fold model that never saw it
        fold_of = {}
        for i, (tr, te) in enumerate(folds):
            for mm in set(g.iloc[te]): fold_of[mm] = i
        save_heldout(node, ids, {"cols": list(X.columns), "models": [r["model"] for r in allf], "fold_of": fold_of,
                                 "regression": reg, "rate": rate, "mean": float(y.mean()), "kinds": kinds, "marks_situation": marks,
                                 "marks_allocation": marks_alloc, "reads_backwards": backwards,
                                 "medians": {c: (None if np.isnan(v) else float(v)) for c, v in X.median().items()},
                                 # each variable's spread (interquartile range, else standard deviation): the smallest
                                 # change that can count as a cause or a fix in a chain (Denning: not a -0.01 difference)
                                 "spreads": {c: float(((X[c].quantile(.75) - X[c].quantile(.25)) or X[c].std() or 0)) if X[c].notna().any() else None
                                             for c in X.columns}})
        out[node] = summary
    return out


_MODELS = {}


def _heldout_path(node, ids):
    import cache
    # keyed by this file and the rows' key (not the report layer: an edit to the TQs must not lose the fitted models;
    # an edit to how rows are measured must)
    return cache._path("fits", "lnode", cache._hash_files(["learnednodes.py"]) + "-" + cache.code_key("lrows"),
                       cache.ids_key(list(ids)), f"{node}.pkl")


def save_heldout(node, ids, obj):
    import pickle
    p = _heldout_path(node, ids); tmp = p + f".{os.getpid()}.tmp"
    pickle.dump(obj, open(tmp, "wb")); os.replace(tmp, p)


def load_heldout(node, ids):
    """The node's held-out fold models from the last fit_all on these matches (None if not fitted yet)."""
    import pickle
    p = _heldout_path(node, ids)
    try: return pickle.load(open(p, "rb"))
    except Exception: return None


def whatif(node, row, changes):
    """The node's reading for one row, and again with some features changed: (before, after) as a chance (%) or
    seconds. The fitted model is the one from the last fit_all in this process."""
    import pandas as pd
    e, cols = _MODELS[node]
    x0 = pd.DataFrame([{c: row.get(c) for c in cols}]).astype(float)
    x1 = x0.copy()
    for k, v in changes.items(): x1[k] = v
    if node in REGRESSION: return round(float(e.predict(x0)[0]), 1), round(float(e.predict(x1)[0]), 1)
    return round(float(e.predict_proba(x0)[0, 1]) * 100, 1), round(float(e.predict_proba(x1)[0, 1]) * 100, 1)


# ---------------------------------------------------------------- the causal map
def write_map(summaries):
    """Each measured link's strength and status into causal_map.json (adding the links and nodes the nodes need),
    every change logged in the map and in link_log.json."""
    c = json.load(open(MAP)); today = datetime.date.today().isoformat()
    have = {n["id"] for n in c["nodes"]}
    for n in NEW_NODES:
        if n["id"] not in have:
            c["nodes"].append(n); c["log"].append({"date": today, "change": f"node {n['id']} {n['name']} added (step 2b: {n['how']})", "by": "Claude, from Denning's list"})
    for nid, frm, why in (("P.17", "C.matchup", "the enemy's interrupts, Daze and Blind against own cancels and removal set how many casts go wrong"),
                          ("P.18", "C.builds", "strips come from the enchantment removal on own bars, and the targets from the enemy's enchantments"),
                          ("P.19", "C.builds", "Blind comes from the Blind skills on own bars")):
        if not any(l["to"] == nid for l in c["links"]):
            c["links"].append({"from": frm, "to": nid, "why": why, "source": "Claude", "confirmed_by_denning": False, "status": "hypothesis", "tactics": []})
            c["log"].append({"date": today, "change": f"link {frm} -> {nid} added as a hypothesis: {why}", "by": "Claude"})
    for n in c["nodes"]:
        if n["id"] == "P.5" and "hex" not in n.get("description", "").lower():
            n["description"] = (n.get("description", "") + "; hex removal: the right hexes removed (valued from data) and how fast").strip("; ")
            n["how"] = (n.get("how", "") + "; eventlayer.py hex_removals").strip("; ")
    log = json.load(open(LINK_LOG)) if os.path.exists(LINK_LOG) else []
    # a node that no longer uses a link drops its old measurement of it
    for l in c["links"]:
        for node in list((l.get("measured") or {}).keys()):
            if node in summaries and not any(x["from"] == l["from"] and x["to"] == l["to"] for x in summaries[node]["links"]):
                del l["measured"][node]
                c["log"].append({"date": today, "change": f"link {l['from']} -> {l['to']}: the {node} node no longer uses it; its measurement there removed", "by": "Claude"})
    changes = 0
    for node, s in summaries.items():
        for L in s["links"]:
            pair = [l for l in c["links"] if l["from"] == L["from"] and l["to"] == L["to"]]
            if not pair:
                why, src = NEW_LINK_WHY.get((L["from"], L["to"]), ("needed by the node model " + node, "Claude"))
                nl = {"from": L["from"], "to": L["to"], "why": why, "source": src, "confirmed_by_denning": False, "status": "hypothesis", "tactics": []}
                c["links"].append(nl); pair = [nl]
                c["log"].append({"date": today, "change": f"link {L['from']} -> {L['to']} added as a hypothesis (node {node}): {why}", "by": src})
            meas = {"node": node, "strength": L["strength"], "plus_minus": L["plus_minus"], "status": L["status"],
                    "metric": s["validation"]["metric"], "matches": s["matches"], "features": L["features"], "date": today}
            for l in pair:
                old = l.get("measured", {}).get(node, {}).get("status")
                l.setdefault("measured", {})[node] = meas
                if old != L["status"]: changes += 1
            log.append({"date": today, "node": node, "from": L["from"], "to": L["to"], **{k: meas[k] for k in ("strength", "plus_minus", "status", "metric", "matches")}})
    # status from data: a link still a hypothesis, or one whose status the data set, follows its latest measurements
    # (supported if any node supports it, rejected if every node that measured it rejects it, else a hypothesis);
    # statuses set by Denning or by a formula are never changed (the measurement is recorded beside them)
    for l in c["links"]:
        ms = [v["status"] for v in (l.get("measured") or {}).values()]
        if not ms or not (l["status"] == "hypothesis" or l.get("status_by") == "data"): continue
        new = "supported" if "supported" in ms else "rejected" if all(x == "rejected" for x in ms) else "hypothesis"
        # Denning's links are never rejected by data without his approval: held as "data says rejected" for him to rule
        # on ("override_approved": true lets the data reject it, and then follow the data both ways)
        if l.get("denning_keep"):          # R-283: kept by Denning's ruling whatever the data says; the measurement is recorded beside it
            l.pop("pending_rejection", None); continue
        if new == "rejected" and l.get("source") == "Denning" and not l.get("override_approved"):
            if not l.get("pending_rejection"):
                c["log"].append({"date": today, "change": f"link {l['from']} -> {l['to']}: the data says rejected; held for Denning's ruling", "by": "data"})
            l["pending_rejection"] = True; new = "hypothesis"
        else:
            l.pop("pending_rejection", None)
        if new != l["status"]:
            c["log"].append({"date": today, "change": f"link {l['from']} -> {l['to']}: {l['status']} -> {new} by data ("
                             + ", ".join(f"{k} {v['status']} {v['strength']:+}" for k, v in l["measured"].items()) + ")", "by": "data"})
            l["status"] = new
        if new == "hypothesis": l.pop("status_by", None)
        else: l["status_by"] = "data"
    # M2: links whose measures are the other team's concurrent response are not fitted; they keep the map entry with
    # the status "concurrent" so nobody re-proposes them as causes
    for l in c["links"]:
        if (l["from"], l["to"]) in CONCURRENT_LINKS and l["status"] != "concurrent":
            c["log"].append({"date": today, "change": f"link {l['from']} -> {l['to']}: {l['status']} -> concurrent (the enemy's response during the window; shown beside the node, not fitted; Denning, November 2026 review)", "by": "Denning"})
            l["status"] = "concurrent"; l["status_by"] = "Denning"
    # M4: inputs pruned for the data's sake go on the waiting list (and come off it when a node carries them again)
    waiting = [w for w in c.get("waiting", []) if w.get("kind") != "pruned input"]
    for node, s in summaries.items():
        for pr in s.get("pruned", []):
            waiting.append({"kind": "pruned input", "node": node, "feature": pr["feature"], "group": pr["group"], "why": pr["reason"],
                            "cap": s.get("input_cap"), "date": today})
    c["waiting"] = waiting
    c["version"] = max(c.get("version", 10), 12)
    json.dump(c, open(MAP, "w"), indent=1, ensure_ascii=False)
    json.dump(log, open(LINK_LOG, "w"), indent=1)
    return changes


# ---------------------------------------------------------------- report lines
def report_lines(summaries):
    L = ["", "## 6b. The learned nodes (step 2 of the learned causal map)", "",
         "Each node uses only the causal-map links into it. A link's strength is how much worse the node predicts matches it "
         "never saw without that link's features (refit without them, same folds); supported when the gain is more than twice "
         "its spread across folds, rejected when dropping it helps by more than that, otherwise not clear yet.", ""]
    for node, s in summaries.items():
        v = s["validation"]; reg = node in REGRESSION
        what = (f"{s['rows']} cases, average {s['mean']} s" if reg else f"{s['rows']} cases, result rate {s['rate']:.0%}")
        L.append(f"**{node.replace('_', ' ')}** (map {s['target']}; {s['matches']} matches, {what}): {v['metric']} {v['glass box']} against "
                 f"{v['simple baseline']} for the simple baseline ({v['verdict']}). Inputs {s.get('inputs')} of a cap of {s.get('input_cap')}"
                 + (f"; pruned: {', '.join(p['feature'] for p in s['pruned'])}" if s.get("pruned") else "") + ".")
        if s.get("marks_situation"):
            L.append(f"- marks the situation (predicts the previous result as well as the next; never a fix): {', '.join(s['marks_situation'])}")
        if s.get("marks_allocation"):
            L.append(f"- marks the situation but is an allocation decision (R-282: may still be a fix): {', '.join(s['marks_allocation'])}")
        if s.get("reads_backwards"):
            L.append(f"- reads backwards: likely a reaction, not a cause (R-285; never a fault or a fix): {', '.join(s['reads_backwards'])}")
        if s.get("concurrent"):
            L.append(f"- measured but not fitted (the enemy's response during the window): {', '.join(s['concurrent'])}")
        for l in sorted(s["links"], key=lambda l: -l["strength"]):
            L.append(f"- link {l['from']} -> {l['to']} [{'/'.join(l.get('kinds', []))}]: gain {l['strength']:+} (+/- {l['plus_minus']}), {l['status']} ({', '.join(l['features'][:4])}{'...' if len(l['features']) > 4 else ''})")
            for x in l.get("each", []):
                L.append(f"  - alone: {x['feature']} ({describe(node, x['feature'])}): gain {x['strength']:+} (+/- {x['plus_minus']}), {x['status']}")
        top = [t for t in s["terms"] if "curve" in t][:3]
        for t in top:
            cv = t["curve"]; lo, hi = cv[0], cv[-1]
            unit = "s" if reg else "points"
            L.append(f"  - leans on **{t['term']}** ({t['description']}): {lo['points']:+} {unit} at {lo['from']} to {lo['to']}, {hi['points']:+} at {hi['from']} to {hi['to']}")
        L.append("")
    return L


PLAIN = {
    "run_outcome": "Does a flag run get captured? Read at 5, 15 and 30 s into every run.",
    "flag_swing": "How much will the flag lead change over the next minute?",
    "run_defence": "Does an enemy run get captured? From the defending side, every run, read at 5, 15 and 30 s in.",
    "capture_speed": "How long does an enemy capture take? (Captures only.)",
    "power_play": "Does a power play (any numbers advantage at main) kill?",
    "fight_outcome": "Who wins a fight? Play measured before the fight's first death.",
    "split_chance": "Does a team start a split in the next 30 s?",
    "split_answer": "How long until the first defender reaches a split in the base?",
    "split_effect": "Does a split in the base kill a pit NPC?",
    "collapse": "Does a split member die when the defenders collapse on it?",
    "pit_npc_loss": "Does the defending team lose a pit NPC in the next 15 s while enemies are in its pit?",
}
STATUS_WORDS = {"supported": "**supported**: it clearly helps predict matches the model never saw",
                "rejected": "**rejected for now**: leaving it out predicts unseen matches slightly better",
                "not clear yet": "not clear yet: more matches needed"}


def _curve_words(t, reg):
    cv = [c for c in t.get("curve", []) if c["from"] is not None]
    if len(cv) < 2: return ""
    lo, hi = cv[0], cv[-1]
    u = " s" if reg else " points"
    return f"at {lo['from']:g} to {lo['to']:g}: {lo['points']:+g}{u}; at {hi['from']:g} to {hi['to']:g}: {hi['points']:+g}{u}"


def render_overview(summaries):
    """knowledge/learned-model.md: what the model measures and what it has learned so far, in words (rebuilt each batch)."""
    c = json.load(open(MAP)); names = {n["id"]: n["name"] for n in c["nodes"]}
    import eventlayer as EL
    V = EL.load_values() or {}
    m = max([s["matches"] for s in summaries.values()] or [0])
    L = ["*Generated by tools/replay_analysis/learnednodes.py after each batch: don't edit; the full map with every "
         "hypothesis is on the Causal map page.*", "", "# What the model has learned", "",
         f"Trained on {m} matches. Each question below is answered by its own small model that may only use the causes the "
         "causal map allows. Each cause is tested by refitting the model without it and checking predictions on matches the "
         "model never saw. \"Points\" = change in the chance of the result for an otherwise even (50%) case.", ""]
    for node, s in summaries.items():
        reg = node in REGRESSION; v = s["validation"]
        good = "better than a simple guess" if v["verdict"].startswith("adds") else "not yet better than a simple guess"
        L += [f"## {PLAIN.get(node, node)}", "",
              f"{s['rows']} cases from {s['matches']} matches; " + (f"average {s['mean']} s" if reg else f"happens {s['rate']:.0%} of the time")
              + f". Predicts unseen matches {good}.", "", "Causes tested:"]
        terms = {t["term"]: t for t in s["terms"] if "curve" in t}
        marks = set(s.get("marks_situation") or []); alloc = set(s.get("marks_allocation") or []); back = set(s.get("reads_backwards") or [])
        kinds = s.get("kinds") or {}
        for l in sorted(s["links"], key=lambda l: -l["strength"]):
            kw = "/".join(l.get("kinds", [])) or "input"
            L.append(f"- **{names.get(l['from'], l['from'])}** ({kw}): {STATUS_WORDS[l['status']]}.")
            feats = sorted(l["features"], key=lambda f: -(terms.get(f, {}).get("importance") or 0))
            for f in feats[:3]:
                if f in terms and terms[f]["importance"] > 0:
                    tag = (" [marks the situation]" if f in marks else " [allocation; marks the situation, may still be a fix]" if f in alloc else "") + (" [reads backwards: likely a reaction]" if f in back else "")
                    L.append(f"  - {describe(node, f)}: {_curve_words(terms[f], reg)}{tag}")
            for x in l.get("each", []):
                L.append(f"  - tested alone, {describe(node, x['feature'])}: {x['status']}")
        if s.get("concurrent"):
            L.append("- Measured beside the node, not as a cause (what the enemy did during the window): " + "; ".join(s["concurrent"].values()) + ".")
        if s.get("pruned"):
            L.append(f"- Left out for now so the inputs fit the data ({s['inputs']} of a cap of {s['input_cap']}): " + ", ".join(f"{describe(node, p['feature'])} ({p['reason']})" for p in s["pruned"]) + ".")
        L.append("")
    if V:
        L += ["## Values measured from the data", "",
              "Used to judge strips and hex removal (what the right target was) and damage output.", ""]
        e = sorted(V.get("enchantments", {}).items(), key=lambda kv: -kv[1]["per_s"])[:10]
        h = sorted(V.get("hexes", {}).items(), key=lambda kv: -kv[1]["per_s"])[:10]
        L.append("- Most valuable enchantments to strip (output per second up): " + ", ".join(f"{k} {v['per_s']:g}" for k, v in e))
        L.append("- Most costly hexes to leave on (output per second on): " + ", ".join(f"{k} {v['per_s']:g}" for k, v in h))
        r = sorted(((k, v) for k, v in V.get("roles", {}).items() if v["n"] >= 100 and v["median"] > 0), key=lambda kv: -kv[1]["median"])[:8]
        L.append("- Usual damage per second on players in a fight, by role: " + ", ".join(f"{k} {v['median']:g}" for k, v in r))
        L.append("")
    L += ["## What is measured in every match (the event layer)", "",
          "- Strips: who stripped what from whom, and the best enchantment that was in range",
          "- Hex removal: which hex was removed, how long it had been on, and the most costly hex in range",
          "- Hexes: how long each stayed on, and the hexed player's output while it was on",
          "- Blind on enemies: on the frontline, and on players hitting own healers",
          "- Frontline peel: damage share on enemies attacking own backline, and on enemy healers",
          "- Wrong casts: casting into a ready interrupt without cancelling, casting while Dazed, attacking while Blind",
          "- Damage output against the role's usual",
          "- Spikes: how tightly the big hits landed, and whether they killed",
          "- Flag runs: stand and boost clock at the start, escort, control and damage on the runner over time, outcome",
          "- Splits: size, how fast and how many defenders came, NPCs killed, enemies drawn, deaths",
          "- Power plays of every size: why the enemy was short, prots and healing against them, spikes",
          "- Enemy captures: defenders free, escort, how long they took", ""]
    out = os.path.join(REPO, "knowledge", "learned-model.md")
    open(out, "w").write("\n".join(L) + "\n")
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    ids = [m for b in M.batches() for m in b["matches"]]
    if a and a[0] in ("fit", "write"):
        import time; t0 = time.time()
        S = fit_all(ids, a[1:] if a[0] == "fit" and len(a) > 1 else None)
        print("\n".join(report_lines(S)))
        if a[0] == "write": print("link status changes:", write_map(S)); print(render_overview(S))
        print(f"{time.time() - t0:.0f} s")
