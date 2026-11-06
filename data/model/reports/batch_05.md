# Learning report, batch 5

Trained on 53 matches (7 new in this batch). Variables in use: 20; build variables from 60 matches, interactions from 40.

## 0. Data integrity

- Lengths repaired: 3 (1f65fd3b 150 s -> 1027 s) (bbef1904 617 s -> 599 s) (36a65ac6 1319 s -> 1294 s) 
- Matches with a team's Lord damage not observed (left blank, not zero): 2
- Pit NPCs added from the standard roster (never seen in the replay): 172 in 45 matches
- Left out of training: 0

## 1. The honest test

**Not yet better than strength alone: treat the curves as noise.** Held-out accuracy (matches held out whole), log loss in brackets (lower is better):

- strength only: all 73% (0.439), 0-5 min 79% (0.371), 5-10 min 75% (0.422), 10-15 min 69% (0.504), 15-end min 64% (0.509), matches lasting 15 min+ 67% (0.534), matches even on strength (gap under 200) 49% (0.665)
- glass box: all 77% (0.53), 0-5 min 82% (0.381), 5-10 min 81% (0.428), 10-15 min 74% (0.586), 15-end min 66% (0.834), matches lasting 15 min+ 70% (0.674), matches even on strength (gap under 200) 57% (0.941)
- glass box without corrections: all 76% (0.535), 0-5 min 82% (0.381), 5-10 min 81% (0.428), 10-15 min 74% (0.587), 15-end min 65% (0.86), matches lasting 15 min+ 70% (0.682), matches even on strength (gap under 200) 57% (0.938)
- black box: all 70% (1.169), 0-5 min 79% (0.822), 5-10 min 74% (1.039), 10-15 min 64% (1.4), 15-end min 57% (1.664), matches lasting 15 min+ 59% (1.611), matches even on strength (gap under 200) 63% (1.419)
- Gain over strength alone (log loss, resampling whole matches): -0.091 (90% range -0.275 to +0.059).
- Change since batch 4: glass box log loss 0.53 -> 0.53; strength only 0.448 -> 0.439.

## 2. What it leans on

- **morale_diff** 0.563 (was 0.645): own minus enemy morale summed over players (boosts +, death penalty -)
- **morale_diff & archers_diff** 0.329 (was 0.266): own minus enemy morale summed over players (boosts +, death penalty -) TOGETHER WITH own minus enemy pit archers alive
- **spike_killable_diff** 0.302 (was 0.277): enemy minus own players within one spike of the other side (DP stacking; 0 unless a spike build is involved)
- **minute & morale_diff** 0.271 (new): match clock in minutes TOGETHER WITH own minus enemy morale summed over players (boosts +, death penalty -)
- **knights_diff** 0.242 (was 0.217): own minus enemy pit knights alive
- **alive_diff** 0.227 (was 0.167): own minus enemy players alive
- **flag_lead & morale_total** 0.206 (new): seconds up (+) or down (-) on flags: enemy's response minus own on the next capture exchange TOGETHER WITH both teams' morale summed (how much death penalty is in the game overall)
- **stand** 0.202 (was 0.245): who holds the flag stand: 1 own, 0 nobody, -1 enemy
- **main_diff** 0.195 (was 0.23): own minus enemy players in each team's main group
- **knights_diff & lord_damage_diff** 0.193 (was 0.188): own minus enemy pit knights alive TOGETHER WITH own minus enemy Lord damage dealt so far (the 28:00 tiebreak; players can't see it); blank when either team's Lord damage wasn't observed
- **down_diff_s** 0.178 (was 0.172): enemy minus own seconds until all dead players are back (+ = the enemy has more time down)
- **pit_pressure_diff** 0.174 (was 0.186): own players in the enemy pit minus enemy players in the own pit

## 3. The curves in words

Points = win-chance points added to an otherwise even game at each range of the variable.

- **morale_diff** rises from -32.0 to +30.8 points (-470.0..-189.5: -32.0; -143.5..-110.5: -16.2; -87.5..-46.5: -13.1; -19.5..-1.0: +1.2; 1.0..24.5: -2.6; 57.5..96.0: +12.6; 134.5..175.5: +23.7)
- **morale_diff & archers_diff** (interaction): see wp_model.md
- **spike_killable_diff** rises from -38.1 to +37.5 points (-8.0..-7.5: -38.1; -6.5..-4.5: -38.1; -2.5..-1.5: -35.2; -0.5..0.5: +0.1; 2.5..4.5: +35.8; 6.5..7.5: +36.3)
- **minute & morale_diff** (interaction): see wp_model.md
- **knights_diff** rises from -20.5 to +18.2 points (-2.0..-1.5: -20.5; -1.5..-0.5: +0.2; -0.5..0.5: +0.5; 0.5..1.5: +1.1; 1.5..2.0: +18.2)
- **alive_diff** rises from -30.8 to +27.0 points (-8.0..-4.5: -30.8; -3.5..-2.5: -17.4; -1.5..-0.5: -10.0; 0.5..1.5: +10.6; 2.5..3.5: +17.7; 4.5..8.0: +27.0)
- **flag_lead & morale_total** (interaction): see wp_model.md
- **stand** rises from -5.3 to +5.4 points (-1.0..-0.5: -5.3; -0.5..0.5: -0.4; 0.5..1.0: +5.4)
- **main_diff** rises from -16.8 to +18.7 points (-8.0..-5.5: -16.8; -4.5..-3.5: -11.6; -2.5..-1.5: -6.2; -0.5..0.5: -0.5; 1.5..2.5: +6.2; 3.5..4.5: +15.7)
- **knights_diff & lord_damage_diff** (interaction): see wp_model.md

## 4. Discovery

**Interaction candidates** (a screen: pairs whose combination seems to matter beyond each alone; untested until held-out matches confirm them; switched on in the model from 40 matches):

- alive_diff with morale_diff (screen 0.092)
- alive_diff with spike_killable_diff (screen 0.091)
- morale_diff with spike_killable_diff (screen 0.091)
- down_diff_s with morale_diff (screen 0.088)
- down_diff_s with spike_killable_diff (screen 0.087)
- alive_diff with down_diff_s (screen 0.083)
- main_diff with morale_diff (screen 0.081)
- main_diff with spike_killable_diff (screen 0.081)

**Candidate variables** (proposed variables, tested on unseen matches; log loss, lower is better):

- split_diff: 0.53 without, 0.537 with: does not improve yet. own minus enemy players on a split (away from their main group on the enemy half, not carrying). Proposed batch 1 by Claude: the knights curve runs backwards, maybe standing in for the cost of splitting

**Surprises** (moments where the held-out model was most confident about the team that went on to lose; each points to something the variables don't capture yet):

- hdm v HC (28447c4a) at 26:45: a model that never saw this match gave HC 3.8%, and HC won. Why it thought so: minute & morale_diff -47.1, alive_diff +43.4, morale_diff -34.9, down_diff_s +33.6, main_diff +25.2
- 옷옷옷옷 v Men (36a65ac6) at 18:00: a model that never saw this match gave 옷옷옷옷 1.0%, and 옷옷옷옷 won. Why it thought so: morale_diff -40.5, morale_diff & lord_damage_diff -36.6, team strength +17.5, archers_diff -10.9, stand -6.9
- hdm v Men (0f1fd794) at 28:00: a model that never saw this match gave Men 10.9%, and Men won. Why it thought so: lord_damage_diff -46.5, morale_diff & lord_damage_diff -31.0, lord_health_diff +21.3, lord_damage_diff & minute +16.9, knights_diff & lord_damage_diff +14.3
- RACK v hdm (1f65fd3b) at 14:30: a model that never saw this match gave RACK 4.7%, and RACK won. Why it thought so: knights_diff -23.2, morale_diff -17.5, team strength -14.0, minute & lord_damage_diff -10.5, pit_pressure_diff +9.2
- Men v HC (faec428a) at 20:30: a model that never saw this match gave Men 1.0%, and Men won. Why it thought so: lord_damage_diff -47.0, pit_pressure_diff -17.1, team strength +14.9, bodyguard_diff -10.8, lord_health_diff +9.2
- OG v hold (49eec28d) at 4:45: a model that never saw this match gave OG 1.9%, and OG won. Why it thought so: lord_health_diff -35.3, morale_diff -32.1, morale_total & archers_diff -28.9, morale_diff & archers_diff -23.7, team strength +19.0

## 5. Denning's rulings seen through the model

Win chance from a model that never saw the match, 20 s before and 60 s after each ruled moment. Contributions are points for an otherwise even game (the curves' scale).

- hdm v HC (28447c4a) 5:01 (split answered), HC: 49.3% 20 s before -> 70.9% 60 s after (+21.6). After: knights_diff -32.9, flag_lead & morale_diff +31.1, pit_pressure_diff +17.0, team strength -16.4
- hdm v HC (28447c4a) 5:01 (split answered), hdm: 52.0% 20 s before -> 32.1% 60 s after (-19.9). After: knights_diff +33.0, flag_lead & morale_diff -32.7, pit_pressure_diff -16.9, team strength +16.4
- hdm v HC (28447c4a) 1:02 (split detection), HC: 36.6% 20 s before -> 7.9% 60 s after (-28.7). After: flag_lead & morale_diff -29.9, team strength -16.4, flag_lead +8.1, carrying_diff -7.1
- hdm v HC (28447c4a) 1:02 (split detection), hdm: 65.6% 20 s before -> 90.6% 60 s after (+25.0). After: flag_lead & morale_diff +29.4, team strength +16.4, flag_lead -9.5, morale_diff +7.6
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), HC: 6.0% 20 s before -> 1.8% 60 s after (-4.2). After: knights_diff -32.9, morale_diff & archers_diff -20.2, pit_pressure_diff +17.0, team strength -16.4
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), hdm: 97.4% 20 s before -> 99.1% 60 s after (+1.7). After: knights_diff +33.0, morale_diff & archers_diff +21.5, morale_diff & lord_damage_diff +19.3, lord_damage_diff & minute -18.4
- hdm v HC (bbef1904) 8:10 (death), HC: 35.6% 20 s before -> 4.0% 60 s after (-31.6). After: alive_diff -17.8, team strength -16.0, morale_diff -14.8, down_diff_s -14.1
- hdm v HC (bbef1904) 8:10 (death), hdm: 59.2% 20 s before -> 94.7% 60 s after (+35.5). After: alive_diff +18.4, team strength +16.0, down_diff_s +10.3, morale_diff +10.0
- Men v HC (faec428a) 9:31 (death), HC: 22.2% 20 s before -> 42.9% 60 s after (+20.7). After: team strength -14.9, archers_diff +7.8, stand -5.1, morale_diff & morale_total +3.7
- Men v HC (faec428a) 9:31 (death), Men: 80.1% 20 s before -> 61.6% 60 s after (-18.5). After: team strength +14.9, archers_diff -7.6, stand +5.1, minute & morale_diff -3.3

## 6. Why: the node models

Each explains one result from what happened before it (time order enforced), tested on matches it never saw. AUC = how often a moment that led to the result scores above one that didn't (0.5 = guessing, 1 = perfect).

**deaths** (53 matches, 115914 moments, 3258 results): adds to the simple baseline (AUC 0.917 against 0.804 for health_pct and damage_taken_3s alone).
- **enemies_near** (enemies within 1,500) rises from -18.5 to +23.0 points (0.0..0.5: -18.5; 0.5..1.5: -9.0; 1.5..2.5: -0.9; 2.5..3.5: +1.0; 3.5..4.5: +7.4; 4.5..5.5: +9.4; 5.5..6.5: +11.2; 6.5..7.5: +15.6; 7.5..8.0: +23.0)
- **strength_gap** (own minus enemy team strength) falls from +14.8 to -10.1 points (-815.0..-529.0: +14.8; -360.5..-298.0: +8.0; -159.5..-116.0: +7.6; -68.0..-6.0: -2.5; 31.0..106.0: -9.1; 122.5..274.5: -7.1; 337.5..498.5: -9.6)
- **health_pct** (current health %) falls from +40.7 to -6.5 points (1.0..47.5: +40.7; 59.5..67.5: +23.7; 73.5..78.5: +11.3; 82.5..85.5: +5.9; 88.5..91.5: +1.1; 93.5..95.5: -3.0; 97.5..99.5: -4.8)
- **local_diff** (allies minus enemies within 2,000) falls from +26.9 to -21.2 points (-8.0..-3.5: +26.9; -2.5..-1.5: +12.8; -0.5..0.5: -5.7; 1.5..2.5: -7.5; 3.5..4.5: +14.6; 5.5..7.0: -21.2)
- **health_ceiling** (maximum health after death penalty, as a share of normal) falls from +31.5 to -9.6 points (0.4..0.66: +31.5; 0.71..0.84: +20.2; 0.85..0.89: +15.2; 0.94..0.95: +9.4; 0.99..1.0: -1.2; 1.1..1.1: -9.6)
- **healers_in_range** (own healers alive within cast range) falls from +11.1 to -10.1 points (0.0..0.5: +11.1; 0.5..1.5: -3.1; 1.5..2.5: -5.1; 2.5..3.5: -2.4; 3.5..4.0: -10.1)
- **allies_near** (allies within 1,500) falls from +11.8 to -6.1 points (0.0..0.5: +11.8; 0.5..1.5: +8.7; 1.5..2.5: +5.3; 2.5..3.5: -1.3; 3.5..4.5: -2.1; 4.5..5.5: -3.3; 5.5..6.5: -4.5; 6.5..7.0: -6.1)

**kill conversion** (53 matches, 851 moments, 265 results): adds to the simple baseline (AUC 0.802 against 0.68 for burst_damage and target_health_pct alone).
- **target_ceiling** (target's health ceiling) falls from +28.3 to -14.2 points (0.4..0.56: +28.3; 0.69..0.7: +18.7; 0.78..0.83: +16.0; 0.86..0.88: +12.7; 0.91..0.94: +7.7; 0.95..0.99: +4.2; 1.02..1.1: -8.7)
- **target_health_pct** (target health % when the burst started) falls from +22.8 to -7.8 points (0.0..36.5: +22.8; 48.5..54.5: +6.6; 61.5..67.5: +6.2; 72.5..76.5: +4.0; 79.5..82.5: -4.0; 86.5..90.5: -8.4; 95.5..99.5: -7.6)
- **burst_damage** (damage in the 2 s burst) rises from -5.0 to +21.2 points (250.0..257.5: -5.0; 266.5..276.5: -9.6; 286.5..296.5: -5.6; 313.5..325.5: -3.0; 341.5..362.5: -1.4; 388.5..418.0: +1.4; 466.5..542.0: +19.7)
- **target_healers_in_range** (target's healers in range) falls from +22.9 to -6.5 points (0.0..0.5: +22.9; 0.5..1.5: +0.2; 1.5..2.5: -4.8; 2.5..3.0: -6.5)
- **target_prot_up** (a prot on the target) falls from +4.0 to -8.4 points (0.0..0.5: +4.0; 0.5..1.0: -8.4)
- **strength_gap** (attacking minus target team strength) rises from -10.1 to +14.4 points (-815.0..-360.0: -10.1; -252.5..-133.0: -6.2; -117.5..-10.0: +0.1; 0.0..68.0: +1.2; 111.0..140.5: -2.0; 252.5..274.5: -1.3; 386.0..498.5: +8.3)
- **minute** (match minute) rises from -8.7 to +6.5 points (0.3..1.35: -8.7; 2.45..3.45: -2.4; 4.65..5.55: -1.0; 6.75..8.05: -0.3; 9.45..10.85: +1.6; 12.85..14.95: +2.7; 17.05..20.25: +3.6)

**flag answer** (seconds an answer to an enemy capture was slower than possible; 49 matches, 456 rows): adds to the simple baseline (typical error 17.3s against 27.4s for the median; explains 68% of the spread).
- **parked_s** (seconds the flag lay parked (dropped 5 s or more: not running yet)): 0.0..2.5: -4.9 s; 11.5..16.5: +7.9 s; 26.0..30.5: +18.4 s; 36.5..41.0: +32.3 s; 52.5..62.5: +47.5 s; 89.0..101.5: +50.1 s; 124.5..291.0: +56.7 s
- **own_deaths_during** (own deaths during the answer): 0.0..0.5: -4.1 s; 0.5..1.5: +6.5 s; 1.5..2.5: +11.9 s; 2.5..3.5: +20.4 s; 3.5..4.5: +27.8 s; 4.5..5.5: +41.5 s; 5.5..6.5: +57.7 s; 6.5..8.0: +62.4 s; 8.0..17.0: +61.3 s
- **enemy_deaths_during** (enemy deaths during the answer): 0.0..0.5: -3.8 s; 0.5..1.5: +10.6 s; 1.5..2.5: +17.7 s; 2.5..3.5: +28.8 s; 3.5..5.0: +26.4 s
- **enemies_in_the_way** (enemy presence along the runner's trip back to the spawn): 0.0..0.5: -5.9 s; 4.5..9.5: -3.7 s; 14.5..20.5: -2.3 s; 25.0..34.5: -0.7 s; 46.5..54.5: +3.0 s; 70.5..105.5: +8.6 s; 132.5..183.5: +16.1 s
- **carrier_damage_taken** (damage the carrier took while carrying): 0.0..1.0: -2.8 s; 29.0..50.5: -3.7 s; 77.0..100.5: -1.7 s; 135.5..191.0: +1.0 s; 250.0..282.5: +3.1 s; 388.0..515.5: +5.1 s; 636.5..1040.0: +7.5 s
- **quick_handoffs** (quick hand-offs (a teammate picked it up within 5 s)): 0.0..0.5: -2.1 s; 0.5..1.5: +7.0 s; 1.5..2.5: +8.8 s; 2.5..3.0: +22.9 s
- **runner_to_spawn** (runner's distance to its flag spawn when the enemy captured): 4.0..913.0: -9.1 s; 1524.5..2225.0: -3.6 s; 3384.5..4131.5: -0.5 s; 4551.5..5280.0: +2.6 s; 5945.0..6648.5: +3.1 s; 7124.0..7649.0: +2.8 s; 8289.0..9094.0: +3.4 s
- **possible_s** (fastest possible answer (s) from the flag model at the enemy's capture): 0.0..4.5: +0.4 s; 9.5..17.5: +1.9 s; 24.5..30.5: +2.8 s; 34.5..38.5: +3.6 s; 42.5..46.5: +1.4 s; 50.5..55.5: -1.8 s; 62.5..69.5: -6.0 s
- **alive_diff** (own minus enemy players alive): -4.0..-2.5: +15.5 s; -2.5..-1.5: +15.4 s; -1.5..-0.5: +6.2 s; -0.5..0.5: -0.6 s; 0.5..1.5: -6.4 s; 1.5..6.0: -2.2 s
- **morale_diff** (own minus enemy morale): -200.0..-110.0: +6.0 s; -74.0..-48.0: +4.2 s; -31.0..-18.0: +1.5 s; -14.0..-1.0: -0.2 s; 6.5..17.0: -0.5 s; 32.5..62.0: -3.0 s; 90.0..132.0: -3.4 s

**npc loss** (53 matches, 5754 moments, 1098 results): adds to the simple baseline (AUC 0.826 against 0.759 for attackers and defenders alone).
- **defenders** (own players in the pit) falls from +34.8 to -33.5 points (0.0..0.5: +34.8; 0.5..1.5: +20.8; 1.5..2.5: +16.6; 2.5..3.5: -1.9; 3.5..4.5: -17.9; 4.5..5.5: -18.9; 5.5..6.5: -20.3; 6.5..7.5: -27.3; 7.5..8.0: -33.5)
- **npc_damage_5s** (damage on the pit NPCs in the last 5 s) rises from -16.6 to +32.1 points (0.0..0.5: -16.6; 22.5..37.5: +0.5; 52.5..72.5: +9.0; 91.5..113.5: +14.9; 135.5..161.5: +23.1; 190.5..228.5: +26.4; 282.5..372.5: +30.1)
- **attackers** (enemy players in the pit) rises from -14.3 to +20.0 points (1.0..1.5: -14.3; 1.5..2.5: -10.6; 2.5..3.5: -4.2; 3.5..4.5: +0.7; 4.5..5.5: +15.5; 5.5..6.5: +17.7; 6.5..7.5: +19.2; 7.5..8.0: +20.0)
- **defenders_elsewhere** (own players alive outside the pit) falls from +18.4 to -3.9 points (0.0..0.5: +18.4; 0.5..1.5: +12.4; 1.5..2.5: +12.1; 2.5..3.5: +6.2; 3.5..4.5: -2.6; 4.5..5.5: -9.5; 5.5..6.5: -16.8; 6.5..7.5: -16.1; 7.5..8.0: -3.9)
- **defender_healers** (of which healers) falls from +17.8 to -6.3 points (0.0..0.5: +17.8; 0.5..1.5: -3.2; 1.5..2.5: -4.4; 2.5..3.0: -6.3)
- **strength_gap** (attacking minus defending team strength) rises from -4.3 to +8.9 points (-815.0..-415.5: -4.3; -316.5..-191.5: -9.6; -104.5..11.0: +0.8; 89.0..106.0: -5.5; 191.5..285.5: +9.7; 316.5..401.5: +5.0; 498.5..598.0: -6.3)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -5.4 to +2.1 points (1.9..17.9: -5.4; 19.45..30.65: -13.1; 32.15..34.05: -2.5; 43.25..53.95: -0.7; 63.75..70.2: +5.9; 75.9..84.55: +7.4; 94.25..106.55: +9.7)
- **archers** (own pit archers alive) rises from -6.9 to +26.4 points (0.0..0.5: -6.9; 0.5..1.5: -5.9; 1.5..2.5: +4.3; 2.5..3.0: +26.4)

**lord damage** (Lord damage dealt in the next 10 s while players are in the enemy pit; 52 matches, 6704 rows): adds to the simple baseline (typical error 120.3 against 82.0 for the median; explains 37% of the spread).
- **defenders** (own players in the pit): 0.0..0.5: +198.0; 0.5..1.5: +107.1; 1.5..2.5: +42.9; 2.5..3.5: -22.3; 3.5..4.5: -64.6; 4.5..5.5: -110.0; 5.5..6.5: -139.4; 6.5..7.5: -151.6; 7.5..8.0: -153.4
- **defenders_elsewhere** (own players alive outside the pit): 0.0..0.5: +80.3; 0.5..1.5: +87.7; 1.5..2.5: +80.6; 2.5..3.5: +71.8; 3.5..4.5: +33.7; 4.5..5.5: -7.3; 5.5..6.5: -59.5; 6.5..7.5: -121.1; 7.5..8.0: -191.4
- **bodyguard** (own Bodyguard alive): 0.0..0.5: +115.8; 0.5..1.0: -46.3
- **attackers** (enemy players in the pit): 1.0..1.5: -46.7; 1.5..2.5: -31.7; 2.5..3.5: -32.9; 3.5..4.5: -14.9; 4.5..5.5: +46.9; 5.5..6.5: +61.8; 6.5..7.5: +65.0; 7.5..8.0: +102.4
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)): 1.9..18.15: -53.9; 20.85..30.95: -36.8; 32.65..32.8: -39.1; 43.25..54.55: -16.4; 64.25..71.55: +11.5; 76.15..85.2: +51.8; 97.3..108.0: +68.0
- **defender_healers** (of which healers): 0.0..0.5: +68.0; 0.5..1.5: -2.2; 1.5..2.5: -17.7; 2.5..3.0: -49.6
- **seconds_in_pit** (seconds the attackers have been in the pit): 0.0..4.5: -27.1; 10.5..16.5: -27.6; 22.5..28.5: -18.8; 37.5..46.5: -8.9; 58.5..73.5: +18.3; 91.5..112.5: +24.0; 142.5..193.5: +49.8
- **archers** (own pit archers alive): 0.0..0.5: -24.2; 0.5..1.5: -13.4; 1.5..2.5: +19.9; 2.5..3.0: +3.2
- **attackers_area_damage** (area-damage skills on the attackers' bars (Denning P9)): 0.0..0.5: +13.0; 0.5..1.0: -26.5
- **strength_gap** (attacking minus defending team strength): -815.0..-376.0: -24.3; -267.0..-117.5: +22.7; 1.0..89.0: +18.3; 106.0..122.5: +3.0; 267.0..303.5: -10.9; 360.5..434.0: -6.1; 529.0..657.0: +10.4

**lord kill** (52 matches, 6700 moments, 471 results): adds to the simple baseline (AUC 0.968 against 0.953 for attackers and defenders alone).
- **defenders_elsewhere** (own players alive outside the pit) falls from +44.8 to -48.7 points (0.0..0.5: +44.8; 0.5..1.5: +34.6; 1.5..2.5: +32.7; 2.5..3.5: +31.5; 3.5..4.5: +30.4; 4.5..5.5: -3.0; 5.5..6.5: -28.9; 6.5..7.5: -48.6; 7.5..8.0: -48.7)
- **defenders** (own players in the pit) falls from +46.8 to -46.5 points (0.0..0.5: +46.8; 0.5..1.5: +40.2; 1.5..2.5: +20.4; 2.5..3.5: -1.3; 3.5..4.5: -28.7; 4.5..5.5: -41.1; 5.5..6.5: -43.8; 6.5..7.5: -44.8; 7.5..8.0: -46.5)
- **attackers** (enemy players in the pit) rises from -43.2 to +41.7 points (1.0..1.5: -43.2; 1.5..2.5: -10.0; 2.5..3.5: -5.1; 3.5..4.5: +1.8; 4.5..5.5: +38.8; 5.5..6.5: +43.3; 6.5..7.5: +42.4; 7.5..8.0: +41.7)
- **minute** (match minute) rises from -46.7 to +26.8 points (0.6..2.85: -46.7; 3.85..4.85: -44.2; 5.85..6.95: +2.1; 8.25..9.85: +15.3; 11.25..12.95: +25.3; 14.95..17.15: +27.1; 19.55..22.35: +30.9)
- **defender_healers** (of which healers) falls from +26.7 to -39.3 points (0.0..0.5: +26.7; 0.5..1.5: +11.8; 1.5..2.5: -1.3; 2.5..3.0: -39.3)
- **seconds_in_pit** (seconds the attackers have been in the pit) rises from -5.8 to +32.5 points (0.0..4.5: -5.8; 10.5..16.5: -17.7; 22.5..28.5: -16.1; 37.5..46.5: -15.1; 58.5..73.5: +8.3; 91.5..112.5: +21.1; 142.5..193.5: +30.6)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -19.5 to +24.8 points (1.9..18.15: -19.5; 20.85..30.95: -27.7; 32.65..32.8: -12.8; 43.25..54.55: -5.2; 64.25..71.55: -2.3; 76.15..85.2: +30.8; 97.3..108.0: +22.6)
- **res_in** (seconds until the next res) rises from -42.0 to +6.2 points (1.0..8.5: -42.0; 17.5..26.5: +3.3; 35.5..44.5: +9.1; 53.5..62.5: +8.2; 71.5..77.5: +11.7; 83.5..89.5: +8.9; 98.5..110.5: +7.4)

## 7. The usual play

Each choice against the most common one in that kind of decision, in win-chance points over the decision's window, adjusted for the situation, with a 90% range from resampling whole matches. CLEAR = the range excludes 0. Win chance comes from a model that never saw the match. The same comparison over the 30 s BEFORE the decision is a placebo test: a choice can't cause what came before it, so a clear difference there means the effect is partly who makes that choice.

**after wipe** (116 decisions, 49 matches; usual: pushed the pit)
- took the flag (n 15): -16.0 [-27.1, -5.7] CLEAR; in the 30 s before: +6.0 [-3.3, +13.9]
- reset (n 12): -6.4 [-15.1, +0.9]; in the 30 s before: +2.6 [-4.6, +9.1]

**boost clock** (200 decisions, 50 matches; usual: not running, fought)
- running, fought (n 33): -8.2 [-14.4, -2.7] CLEAR; in the 30 s before: +0.9 [-5.3, +5.6]
- not running, fell back (n 28): -6.1 [-12.0, -0.5] CLEAR; in the 30 s before: +0.8 [-4.3, +6.1]
- not running, advanced (n 24): -13.3 [-22.0, -4.5] CLEAR; in the 30 s before: +3.9 [-1.2, +9.7]
- running, advanced (n 22): -5.8 [-13.4, +3.4]; in the 30 s before: +2.3 [-3.9, +7.0]
- not running, to the spawn (n 9): -2.0 [-7.8, +8.6]; in the 30 s before: +0.2 [-7.3, +6.1]
- not running, held (n 9): -11.3 [-20.7, +0.6]; in the 30 s before: +1.1 [-5.6, +6.3]
- running, fell back (n 7): +5.0 [-7.6, +17.6]; in the 30 s before: -1.3 [-10.8, +12.1]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - running, fought, behind in the fight (lowest third, -0.11 or less): too few yet (n 9 against 33; means -0.3 against -4.0)
  - running, fought, middle third: -10.5 (n 13 against 23)
  - running, fought, ahead in the fight (top third, above -0.01): -9.6 (n 11 against 12)
  - not running, fell back, behind in the fight (lowest third, -0.11 or less): too few yet (n 8 against 33; means -1.9 against -4.0)
  - not running, fell back, middle third: -9.9 (n 11 against 23)
  - not running, fell back, ahead in the fight (top third, above -0.01): too few yet (n 9 against 12; means 4.4 against 12.1)
  - not running, advanced, behind in the fight (lowest third, -0.11 or less): too few yet (n 3 against 33; means -4.9 against -4.0)
  - not running, advanced, middle third: too few yet (n 5 against 23; means -6.7 against 5.2)
  - not running, advanced, ahead in the fight (top third, above -0.01): -21.7 (n 16 against 12)
  - running, advanced, behind in the fight (lowest third, -0.11 or less): too few yet (n 1 against 33; means 9.5 against -4.0)
  - running, advanced, middle third: too few yet (n 9 against 23; means 0.6 against 5.2)
  - running, advanced, ahead in the fight (top third, above -0.01): -13.7 (n 12 against 12)
  - not running, to the spawn, behind in the fight (lowest third, -0.11 or less): too few yet (n 8 against 33; means -0.6 against -4.0)
  - not running, to the spawn, middle third: too few yet (n 1 against 23; means 7.8 against 5.2)
  - not running, held, behind in the fight (lowest third, -0.11 or less): too few yet (n 4 against 33; means -8.8 against -4.0)
  - not running, held, middle third: too few yet (n 1 against 23; means -0.1 against 5.2)
  - not running, held, ahead in the fight (top third, above -0.01): too few yet (n 4 against 12; means -8.2 against 12.1)
  - running, fell back, behind in the fight (lowest third, -0.11 or less): too few yet (n 1 against 33; means 1.5 against -4.0)
  - running, fell back, middle third: too few yet (n 3 against 23; means -4.9 against 5.2)
  - running, fell back, ahead in the fight (top third, above -0.01): too few yet (n 3 against 12; means 21.3 against 12.1)

**enemy pickup** (810 decisions, 52 matches; usual: held, fought)
- already running, fought (n 129): -3.6 [-6.9, +1.5]; in the 30 s before: +2.9 [-1.2, +5.5]
- held, advanced (n 90): -2.5 [-5.9, +3.0]; in the 30 s before: +3.7 [+0.7, +7.0] ALREADY DIFFERENT BEFORE: partly who chooses it
- already running, advanced (n 79): -1.7 [-5.0, +3.6]; in the 30 s before: +3.6 [-0.5, +7.1]
- held, fell back (n 64): -3.0 [-9.9, +3.1]; in the 30 s before: -0.6 [-4.7, +2.4]
- ran, fell back (n 56): -4.8 [-7.6, +0.7]; in the 30 s before: +0.5 [-2.9, +2.4]
- ran, fought (n 56): -3.8 [-7.3, +1.6]; in the 30 s before: -0.1 [-4.0, +4.3]
- already running, fell back (n 48): -1.7 [-7.2, +4.5]; in the 30 s before: -3.4 [-7.7, +0.1]
- ran, advanced (n 43): -6.7 [-9.8, -1.3] CLEAR; in the 30 s before: +5.7 [+0.4, +9.5] ALREADY DIFFERENT BEFORE: partly who chooses it
- already running, held (n 24): -3.9 [-6.1, +1.7]; in the 30 s before: -1.4 [-9.1, +4.2]
- held, held (n 15): +3.1 [-10.6, +13.4]; in the 30 s before: -4.1 [-13.3, +5.9]
- ran, held (n 13): +0.4 [-5.9, +6.9]; in the 30 s before: -3.4 [-8.5, +0.3]
- held, to the spawn (n 7): -0.3 [-5.7, +11.1]; in the 30 s before: +3.3 [-18.1, +15.9]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - already running, fought, behind in the fight (lowest third, -0.01 or less): +9.7 (n 46 against 65)
  - already running, fought, middle third: -13.3 (n 28 against 58)
  - already running, fought, ahead in the fight (top third, above +0.01): -3.6 (n 55 against 63)
  - held, advanced, behind in the fight (lowest third, -0.01 or less): +5.2 (n 11 against 65)
  - held, advanced, middle third: -11.8 (n 43 against 58)
  - held, advanced, ahead in the fight (top third, above +0.01): -0.7 (n 36 against 63)
  - already running, advanced, behind in the fight (lowest third, -0.01 or less): +14.3 (n 18 against 65)
  - already running, advanced, middle third: -13.8 (n 32 against 58)
  - already running, advanced, ahead in the fight (top third, above +0.01): -2.0 (n 29 against 63)
  - held, fell back, behind in the fight (lowest third, -0.01 or less): +5.7 (n 27 against 65)
  - held, fell back, middle third: -21.1 (n 17 against 58)
  - held, fell back, ahead in the fight (top third, above +0.01): -1.6 (n 20 against 63)
  - ran, fell back, behind in the fight (lowest third, -0.01 or less): +9.9 (n 25 against 65)
  - ran, fell back, middle third: -12.8 (n 20 against 58)
  - ran, fell back, ahead in the fight (top third, above +0.01): -10.5 (n 11 against 63)
  - ran, fought, behind in the fight (lowest third, -0.01 or less): +8.6 (n 25 against 65)
  - ran, fought, middle third: -11.8 (n 11 against 58)
  - ran, fought, ahead in the fight (top third, above +0.01): -3.9 (n 20 against 63)
  - already running, fell back, behind in the fight (lowest third, -0.01 or less): +9.0 (n 26 against 65)
  - already running, fell back, middle third: -12.2 (n 12 against 58)
  - already running, fell back, ahead in the fight (top third, above +0.01): -0.8 (n 10 against 63)
  - ran, advanced, behind in the fight (lowest third, -0.01 or less): +4.7 (n 13 against 65)
  - ran, advanced, middle third: -15.1 (n 19 against 58)
  - ran, advanced, ahead in the fight (top third, above +0.01): -6.5 (n 11 against 63)
  - already running, held, behind in the fight (lowest third, -0.01 or less): too few yet (n 8 against 65; means 4.0 against -8.2)
  - already running, held, middle third: -18.5 (n 10 against 58)
  - already running, held, ahead in the fight (top third, above +0.01): too few yet (n 6 against 63; means -3.1 against 2.3)
  - held, held, behind in the fight (lowest third, -0.01 or less): too few yet (n 7 against 65; means 6.6 against -8.2)
  - held, held, middle third: too few yet (n 6 against 58; means 4.5 against 13.1)
  - held, held, ahead in the fight (top third, above +0.01): too few yet (n 2 against 63; means -14.2 against 2.3)
  - ran, held, behind in the fight (lowest third, -0.01 or less): too few yet (n 5 against 65; means 1.2 against -8.2)
  - ran, held, middle third: too few yet (n 8 against 58; means 1.6 against 13.1)
  - held, to the spawn, behind in the fight (lowest third, -0.01 or less): too few yet (n 6 against 65; means -6.4 against -8.2)
  - held, to the spawn, ahead in the fight (top third, above +0.01): too few yet (n 1 against 63; means 22.5 against 2.3)

- **late_game**: not enough decisions yet (15)
**power play** (537 decisions, 53 matches; usual: pushed, advanced)
- pushed, fought (n 152): +3.0 [-0.2, +5.8]; in the 30 s before: -2.3 [-4.3, +0.2]
- held, fought (n 113): -0.6 [-3.4, +1.5]; in the 30 s before: -3.9 [-5.4, -1.7] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, fell back (n 45): -0.6 [-4.4, +3.2]; in the 30 s before: -4.6 [-11.7, +0.1]
- pushed, fell back (n 19): -0.2 [-5.4, +4.8]; in the 30 s before: -4.9 [-9.6, -0.8] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, advanced (n 14): +6.5 [+0.9, +14.4] CLEAR; in the 30 s before: -4.7 [-18.0, +4.0]
- pushed, held (n 7): -3.9 [-11.5, +2.5]; in the 30 s before: -3.0 [-14.4, +9.1]
- held, held (n 5): +5.4 [+0.0, +14.1]; in the 30 s before: -10.7 [-18.2, +0.0]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - pushed, fought, behind in the fight (lowest third, -0.00 or less): +4.9 (n 48 against 58)
  - pushed, fought, middle third: +3.4 (n 52 against 48)
  - pushed, fought, ahead in the fight (top third, above +0.05): +2.6 (n 52 against 76)
  - held, fought, behind in the fight (lowest third, -0.00 or less): +3.2 (n 45 against 58)
  - held, fought, middle third: -0.7 (n 36 against 48)
  - held, fought, ahead in the fight (top third, above +0.05): -5.3 (n 32 against 76)
  - held, fell back, behind in the fight (lowest third, -0.00 or less): +2.5 (n 17 against 58)
  - held, fell back, middle third: -0.7 (n 15 against 48)
  - held, fell back, ahead in the fight (top third, above +0.05): -1.3 (n 13 against 76)
  - pushed, fell back, behind in the fight (lowest third, -0.00 or less): too few yet (n 7 against 58; means -0.9 against -4.0)
  - pushed, fell back, middle third: too few yet (n 9 against 48; means -5.6 against -0.3)
  - pushed, fell back, ahead in the fight (top third, above +0.05): too few yet (n 3 against 76; means 14.7 against 3.2)
  - held, advanced, behind in the fight (lowest third, -0.00 or less): too few yet (n 5 against 58; means -0.0 against -4.0)
  - held, advanced, middle third: too few yet (n 6 against 48; means 8.6 against -0.3)
  - held, advanced, ahead in the fight (top third, above +0.05): too few yet (n 3 against 76; means 21.3 against 3.2)
  - pushed, held, behind in the fight (lowest third, -0.00 or less): too few yet (n 5 against 58; means -2.3 against -4.0)
  - pushed, held, middle third: too few yet (n 2 against 48; means -0.7 against -0.3)
  - held, held, behind in the fight (lowest third, -0.00 or less): too few yet (n 3 against 58; means 3.3 against -4.0)
  - held, held, middle third: too few yet (n 2 against 48; means 3.5 against -0.3)

**split in base** (113 decisions, 35 matches; usual: collapsed)
- defended without a collapse (n 49): +10.7 [+2.5, +20.1] CLEAR; in the 30 s before: +2.0 [-2.3, +6.4]
- missed (n 12): +0.7 [-11.9, +14.1]; in the 30 s before: -3.8 [-12.0, +4.2]

**Collapses on a split: time away and its cost** (`S32`; per collapse, averages; main = what the main fight lost while the collapsers were away)

| Group | Cases | Away (median s) | Split killed | Collapser died | Own deaths at main | Enemy deaths at main | Flag lead change | DP change | Win change |
|---|---|---|---|---|---|---|---|---|---|
| all | 56 | 18 | 11 | 5 | 0.48 | 0.23 | +1.7 | -2.4 | -3.3 |
| away under 30 s | 35 | 9 | 9 | 0 | 0 | 0.11 | -0.6 | +0.7 | -0.1 |
| away 30 to 60 s | 11 | 42 | 0 | 1 | 0.18 | 0.09 | +11.6 | -2.7 | -3.3 |
| away 60 s or more | 10 | 125 | 2 | 4 | 2.5 | 0.8 | -1.1 | -12.7 | -14.4 |
| before 20:00 | 49 | 19 | 7 | 4 | 0.37 | 0.2 | +3.7 | -4.7 | -2.1 |
| from 20:00 | 7 | 18 | 4 | 1 | 1.29 | 0.43 | -12.3 | +14.3 | -11.8 |
| split member killed | 11 | 16 | 11 | 1 | 0.09 | 0.73 | +4.5 | +1.6 | -0.8 |
| no kill | 45 | 19 | 0 | 4 | 0.58 | 0.11 | +1.1 | -3.3 | -3.9 |

**Leverage: where the choice matters most** (share of the spread in win-chance change explained by the choice beyond the situation; range = best minus worst choice, in points)

- after wipe (116): choice explains 9.1% (situation 17.1%); range 16.0 points, best pushed the pit, worst took the flag
- boost clock (200): choice explains 8.0% (situation 4.9%); range 17.6 points, best running, fell back, worst not running, advanced
- split in base (113): choice explains 4.2% (situation 6.9%); range 10.7 points, best defended without a collapse, worst collapsed
- power play (537): choice explains 1.6% (situation 3.1%); range 9.2 points, best held, advanced, worst pushed, held
- enemy pickup (810): choice explains 0.8% (situation 4.1%); range 7.7 points, best held, held, worst ran, advanced

**Behaviour clusters: what teams actually did** (each decision's response grouped by what every player did in the next 20 s; UNNAMED = a group no single named choice covers: a response for Denning to name or reject)

*after wipe* (2 groups, separation 0.32):
- n 69: fought (midline, 1.8 of 8), fought (backline, 1.6 of 8), fought (frontline, 1.0 of 8), held (backline, 0.9 of 8); named as {'pushed the pit': 62, 'took the flag': 4, 'reset': 3}; win change -0.3
- n 47: advanced (backline, 3.0 of 8), advanced (midline, 2.0 of 8), advanced (frontline, 1.3 of 8); named as {'pushed the pit': 27, 'took the flag': 11, 'reset': 9}; win change -0.6 UNNAMED
*boost clock* (3 groups, separation 0.18):
- n 101: fought (midline, 2.1 of 8), fought (backline, 1.5 of 8), fought (frontline, 1.1 of 8), held (backline, 0.7 of 8); named as {'not running, fought': 65, 'running, fought': 31, 'not running, to the spawn': 3}; win change 1.0
- n 73: advanced (midline, 1.5 of 8), advanced (backline, 1.3 of 8), fought (midline, 0.5 of 8), held (backline, 0.5 of 8); named as {'not running, advanced': 24, 'running, advanced': 21, 'not running, held': 8}; win change -3.9 UNNAMED
- n 33: fell back (backline, 2.2 of 8), fell back (midline, 2.1 of 8), fell back (frontline, 0.8 of 8), fought (midline, 0.6 of 8); named as {'not running, fell back': 24, 'running, fell back': 7, 'not running, held': 1}; win change 0.9
*enemy pickup* (3 groups, separation 0.2):
- n 326: fought (midline, 2.1 of 8), fought (backline, 1.5 of 8), fought (frontline, 1.1 of 8), held (backline, 0.9 of 8); named as {'held, fought': 144, 'already running, fought': 114, 'ran, fought': 45}; win change -1.6 UNNAMED
- n 269: advanced (backline, 1.9 of 8), advanced (midline, 1.8 of 8), advanced (frontline, 0.9 of 8), fought (backline, 0.6 of 8); named as {'held, advanced': 88, 'already running, advanced': 75, 'ran, advanced': 41}; win change 3.3 UNNAMED
- n 217: fell back (backline, 1.7 of 8), fell back (midline, 1.5 of 8), held (backline, 0.6 of 8), fell back (frontline, 0.6 of 8); named as {'held, fell back': 60, 'ran, fell back': 55, 'already running, fell back': 46}; win change -0.8 UNNAMED
*power play* (3 groups, separation 0.26):
- n 283: fought (midline, 1.9 of 8), fought (backline, 1.7 of 8), fought (frontline, 1.1 of 8), held (backline, 0.8 of 8); named as {'pushed, fought': 143, 'held, fought': 107, 'pushed, advanced': 17}; win change 1.3 UNNAMED
- n 175: advanced (backline, 2.6 of 8), advanced (midline, 2.1 of 8), advanced (frontline, 1.2 of 8); named as {'pushed, advanced': 162, 'held, advanced': 10, 'pushed, fought': 2}; win change 1.1
- n 85: fell back (backline, 2.2 of 8), fell back (midline, 1.6 of 8), fought (midline, 0.6 of 8), fell back (frontline, 0.6 of 8); named as {'held, fell back': 43, 'pushed, fell back': 18, 'pushed, fought': 7}; win change -1.3 UNNAMED
*split in base* (4 groups, separation 0.21):
- n 56: fought (midline, 2.2 of 8), fought (backline, 1.2 of 8), fought (frontline, 1.0 of 8), held (backline, 0.8 of 8); named as {'defended without a collapse': 32, 'collapsed': 20, 'missed': 4}; win change 1.9 UNNAMED
- n 33: fell back (midline, 2.4 of 8), fell back (backline, 1.3 of 8), fell back (frontline, 0.9 of 8), to the spawn (midline, 0.5 of 8); named as {'collapsed': 20, 'defended without a collapse': 8, 'missed': 5}; win change -4.6
- n 21: advanced (backline, 1.8 of 8), advanced (midline, 1.8 of 8), advanced (frontline, 0.7 of 8), fought (midline, 0.5 of 8); named as {'collapsed': 12, 'defended without a collapse': 7, 'missed': 2}; win change 4.1 UNNAMED
- n 2: died (midline, 7.0 of 8), died (backline, 1.0 of 8); named as {'defended without a collapse': 1, 'missed': 1}; win change -0.1 UNNAMED

## 8. What results and causes are worth

Win points for the team it happened to, from 53 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 168 | -0.1 | -9.8 to +9.7 | +1.4 | no |
| capture | 512 | +3.2 | +1.9 to +4.5 | +2.8 | yes |
| death (any) | 1056 | -6.0 | -9.6 to -3.1 | -5.3 | yes |
| death: against a spike build | 254 | -3.9 | -8.3 to +2.9 | -2.7 | no |
| death: against other builds | 802 | -6.6 | -11.0 to -2.6 | -6.1 | yes |
| death: back within 20 s | 164 | -2.6 | -7.7 to +2.2 | -1.8 | no |
| death: down 20 to 60 s | 385 | -7.1 | -11.5 to -2.7 | -4.7 | yes |
| death: down 60 s or more | 507 | -6.2 | -10.1 to -2.7 | -6.9 | yes |
| death: healer | 365 | -5.8 | -9.5 to -2.3 | -5.6 | yes |
| death: healer in own base or pit, back within 15 s (likely deliberate) | 23 | -0.8 | -10.8 to +9.7 | -0.7 | no |
| death: healer, other | 342 | -6.2 | -10.0 to -2.7 | -6.0 | yes |
| death: not a healer | 691 | -6.1 | -9.7 to -2.3 | -5.1 | yes |
| pit NPC lost (any): taken by a spike build | 72 | -1.8 | -7.2 to +6.4 | -1.6 | no |
| pit NPC lost (any): taken by other builds | 360 | -2.2 | -5.7 to +1.3 | -1.5 | no |
| pit NPC lost: archer | 243 | +0.7 | -2.2 to +3.9 | +0.0 | no |
| pit NPC lost: bodyguard | 65 | -1.6 | -6.1 to +2.6 | -0.2 | no |
| pit NPC lost: knight | 124 | -7.8 | -14.0 to -2.7 | -5.3 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value.

*deaths* (per 10 s in that state; result worth -6.0 points, base rate 1.4%):

- enemies within 1,500 7.5 to 8: result chance +2.3 points, worth -0.14 win points
- own minus enemy team strength -815 to -529: result chance +1.1 points, worth -0.07 win points
- current health % 1 to 47.5: result chance +10.8 points, worth -0.65 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +3.1 points, worth -0.19 win points
- maximum health after death penalty, as a share of normal 0.4 to 0.66: result chance +4.5 points, worth -0.27 win points
- own healers alive within cast range 0 to 0.5: result chance +0.8 points, worth -0.05 win points
- allies within 1,500 0 to 0.5: result chance +0.8 points, worth -0.05 win points

*kill conversion* (per burst, for the attacking team; result worth +6.0 points, base rate 31.1%):

- target's health ceiling 0.4 to 0.56: result chance +30.9 points, worth +1.85 win points
- target health % when the burst started 0 to 36.5: result chance +23.6 points, worth +1.42 win points
- damage in the 2 s burst 542 to 839: result chance +21.6 points, worth +1.3 win points
- target's healers in range 0 to 0.5: result chance +23.7 points, worth +1.42 win points
- a prot on the target 0.5 to 1: result chance -6.8 points, worth -0.41 win points
- attacking minus target team strength 498.5 to 815: result chance +13.9 points, worth +0.83 win points

*npc loss* (per case, for the defending team; result worth -2.1 points, base rate 19.1%):

- own players in the pit 0 to 0.5: result chance +37.7 points, worth -0.79 win points
- damage on the pit NPCs in the last 5 s 372.5 to 1170: result chance +32.9 points, worth -0.69 win points
- enemy players in the pit 7.5 to 8: result chance +16.4 points, worth -0.34 win points
- own players alive outside the pit 0 to 0.5: result chance +14.7 points, worth -0.31 win points
- of which healers 0 to 0.5: result chance +14.1 points, worth -0.29 win points
- attacking minus defending team strength -415.5 to -316.5: result chance -5.8 points, worth +0.12 win points
- attackers' measured damage per second against a Lord (benchmarks) 17.9 to 19.45: result chance -7.4 points, worth +0.15 win points

## Why: the biggest moments of the new matches

For each, the engine's account of why it happened, from models that never saw the match: result and worth, the mechanics of each death, the setup (where every group was and what it could do), the decision before, and the context.

### Team v cope (6c7dfcaa), 9:59 to 10:14: cope lost 1 player on the backside

1. **Result**: deaths cope 8, Team 1 until all were back; cope lost bodyguard, knight, knight, archer; flag lead -23 s; death penalty {'cope': -75, 'Team': 15}. Win chance for cope 91.5% -> 28.5% (-63.0); moved by down_diff_s -31.9, alive_diff -16.5, morale_diff & morale_total -10.3, flag_lead -9.2, main_diff -7.0.
2. **Mechanics** (deaths model that never saw this match, a few seconds before each death; what raised the risk most):
   - cope Mes/A at 10:14 (engine's cause: coordinated enemy pressure (great enemy play)): risk 5.0% at 10:10; health +40.3, enemies within 1,500 +14.8, hexes on it +10.4, damage taken (3 s) +7.7 [health 31%, ceiling 1.1, 7 enemies and 6 allies near, 3 healers in range, 3 hexes]
3. **Setup** (phase 9:36 to 10:00):
   - cope plan 8v8 brawl: push side 8v8 contest (8 Monk, 7 Monk, Prot, Mes/A, Stand Mes, Dervish, AoB Derv, Hammer)
     where the deaths came: 8v8, 5 damage, 3 healers, pressure 3/s, incoming 47/s, sustain margin +51, uptime 12%, control received 0 interrupts (0 on healers), 0 knockdowns
   - Team plan 8v8 brawl: backside 8v8 contest (Ritualist, 7 Monk, Prot, Necromancer 2, Stand Mes, Mes/A, Fire Ele, Necromancer 1)
     where the deaths came: 8v8, 5 damage, 3 healers, pressure 47/s, incoming 3/s, sustain margin +17, uptime 42%, control received 2 interrupts (0 on healers), 2 knockdowns
4. **Decision** (enemy pickup at 9:58): cope chose 'held' (fell back 6, died 1, fought 1); usual there: already running, fought; that choice is worth +2.3 points against the usual [-3.1, +6.6].
**Why, in short**: cope fought 8v8 on the push side (job: contest) with sustain margin +51 while the rest were ; the Mes/A died mainly from health; after choosing 'held' at the enemy pickup.
5. **Context**: cope: 8 up (main 7), flags up +28 s, DP 80, NPCs K2 A2 B1, Lord dmg 0; Team: 8 up (main 7), flags down -28 s, DP -45, NPCs K1 A1 B1, Lord dmg 0; stand cope, boost in 12 s; builds balance v hex way; situation: fought away from pit while up on flags (+28 s): could fall back, first death after time.

### Team v cope (6c7dfcaa), 10:27 to 11:31: cope lost 8 players (a wipe) on the backside

1. **Result**: deaths cope 7, Team 1 until all were back; cope lost bodyguard, knight, knight, archer; flag lead +0 s; death penalty {'cope': -60, 'Team': 9}. Win chance for cope 70.5% -> 12.3% (-58.2); moved by lord_health_diff -24.9, main_diff -16.6, alive_diff -13.8, lord_damage_diff & minute +10.5, morale_total & archers_diff -9.7.
2. **Mechanics** (deaths model that never saw this match, a few seconds before each death; what raised the risk most):
   - cope 8 Monk at 10:42 (engine's cause: coordinated enemy pressure (great enemy play)): risk 2.8% at 10:40; health +40.3, health_pct & health_ceiling +24.7, local numbers +12.8, health_pct & minute +11.5 [health 11%, ceiling 1.1, 0 enemies and 4 allies near, 2 healers in range, 2 hexes]
   - cope AoB Derv at 10:45 (engine's cause: coordinated enemy pressure (great enemy play)): risk 8.8% at 10:40; health +40.3, local numbers +28.1, enemies within 1,500 +14.8, damage taken (3 s) +7.3 [health 37%, ceiling 1.1, 7 enemies and 3 allies near, 2 healers in range, 2 hexes]
   - cope Prot at 11:01 (engine's cause: backline down (1 monk dead, in a chain)): risk 9.8% at 10:55; local numbers +28.1, health +27.1, own healers dead +17.5, healers in range +11.2 [health 51%, ceiling 1.1, 6 enemies and 2 allies near, 0 healers in range, 3 hexes]
   - cope Stand Mes at 11:13 (engine's cause: backline down (2 monks dead, in a chain)): risk 27.7% at 11:10; health +40.3, own healers dead +27.8, health_pct & health_ceiling +24.7, health_pct & minute +11.5 [health 9%, ceiling 1.1, 1 enemies and 0 allies near, 0 healers in range]
3. **Setup** (phase 10:14 to 10:25):
   - cope plan 8v8 brawl, split pressure: backside 6v7 hold (8 Monk, 7 Monk, Prot, Stand Mes, AoB Derv, Hammer); enemy pit 1v1 split (on NPCs) (Dervish)
     where the deaths came: 6v7, 3 damage, 3 healers, pressure 0/s, incoming 27/s, sustain margin +45, uptime 21%, control received 0 interrupts (0 on healers), 0 knockdowns
   - Team plan 8v8 brawl, flag game: push side 7v6 convert (7 Monk, Prot, Necromancer 2, Stand Mes, Mes/A, Fire Ele, Necromancer 1); own pit 1v1 cap and return (Ritualist)
     where the deaths came: 7v6, 5 damage, 2 healers, pressure 37/s, incoming 0/s, sustain margin +68, uptime 40%, control received 0 interrupts (0 on healers), 0 knockdowns
4. **Decision** (enemy pickup at 10:17): cope chose 'held' (fell back 6, advanced 1); usual there: already running, fought; that choice is worth +2.3 points against the usual [-3.1, +6.6].
**Why, in short**: cope fought 6v7 on the backside (job: hold) with sustain margin +45 while the rest were enemy pit (split (on NPCs)); the 8 Monk died mainly from health; the AoB Derv died mainly from health; after choosing 'held' at the enemy pickup.
5. **Context**: cope: 7 up (main 6), flags even +5 s, DP 65, NPCs K2 A2 B1, Lord dmg 0; Team: 8 up (main 7), flags even -5 s, DP -39, NPCs K1 A1 B1, Lord dmg 0; stand cope, boost in 104 s; builds balance v hex way; situation: lost while up in numbers where it fought 6v2, a monk died first.

### hook v EDGE (e14811f2), 3:27 to 3:42: EDGE lost 1 player on the backside

1. **Result**: deaths EDGE 1 until all were back; EDGE lost knight; flag lead -2 s; death penalty {'EDGE': -15, 'hook': 0}. Win chance for EDGE 45.7% -> 12.8% (-32.9); moved by knights_diff -19.7, knights_diff & lord_damage_diff -14.5, pit_pressure_diff -14.2, morale_diff +4.3.
2. **Mechanics** (deaths model that never saw this match, a few seconds before each death; what raised the risk most):
   - EDGE Air Ele at 3:42 (engine's cause: coordinated enemy pressure (great enemy play)): risk 27.9% at 3:40; health +40.1, enemies within 1,500 +23.7, health ceiling (death penalty) +16.9, local numbers +12.8 [health 28%, ceiling 0.85, 8 enemies and 6 allies near, 2 healers in range]
3. **Setup** (phase 3:18 to 3:42):
   - EDGE plan 8v8 brawl, holding in the pit: own base 7v8 hold (7 Monk, Prot, Assassin, Mesmer, Air Ele, Fire Ele, AoB Derv)
     where the deaths came: 7v8, 5 damage, 2 healers, pressure 32/s, incoming 72/s, sustain margin +16, uptime 47%, control received 3 interrupts (1 on healers), 2 knockdowns
   - hook plan 8v8 brawl: enemy base 8v7 convert (8 Monk, 7 Monk, Prot, Mesmer, Ritualist, Ranger, Hammer, AoB Derv)
     where the deaths came: 8v7, 5 damage, 3 healers, pressure 72/s, incoming 32/s, sustain margin +50, uptime 66%, control received 1 interrupts (0 on healers), 3 knockdowns
4. **Decision**: no decision point for EDGE in the 45 s before.
**Why, in short**: EDGE fought 7v8 on the own base (job: hold) with sustain margin +16 while the rest were ; the Air Ele died mainly from health.
5. **Context**: EDGE: 7 up (main 7), flags up +19 s, DP -75, NPCs K1 A2 B1, Lord dmg 0; hook: 8 up (main 8), flags down -19 s, DP 0, NPCs K2 A2 B1, Lord dmg 0; stand hook, boost in 62 s; builds balance v balance; situation: outnumbered where it fought 7v8.

### hook v EDGE (e14811f2), 1:00 to 1:40: EDGE lost 4 players (a wipe) on the backside

1. **Result**: deaths EDGE 4 until all were back; flag lead +7 s; death penalty {'EDGE': -60, 'hook': 0}. Win chance for EDGE 67.4% -> 41.5% (-25.9); moved by morale_diff -13.9, carrying_diff -8.3, morale_diff & lord_damage_diff -3.4.
2. **Mechanics** (deaths model that never saw this match, a few seconds before each death; what raised the risk most):
   - EDGE Prot at 1:15 (engine's cause: positioning: out of range of its monks): risk 3.8% at 1:10; health +26.5, healers in range +11.7, health_pct & minute +11.2, damage taken (3 s) +7.6 [health 59%, ceiling 1.0, 4 enemies and 3 allies near, 0 healers in range]
   - EDGE Assassin at 1:19 (engine's cause: backline down (1 monk dead, in a chain)): risk 2.6% at 1:15; health +40.1, health_pct & minute +35.1, healers in range +11.7, allies near +7.9 [health 5%, ceiling 1.0, 0 enemies and 1 allies near, 0 healers in range, 1 hexes]
   - EDGE Air Ele at 1:26 (engine's cause: backline down (1 monk dead, in a chain)): risk 37.6% at 1:20; Dazed +23.7, local numbers +19.9, own healers dead +18.0, health +15.1 [health 71%, ceiling 1.0, 4 enemies and 1 allies near, 0 healers in range, Dazed]
   - EDGE Fire Ele at 1:40 (engine's cause: backline down (1 monk dead)): risk 44.3% at 1:35; local numbers +26.7, health +23.4, own healers dead +18.0, Crippled +14.1 [health 66%, ceiling 1.0, 4 enemies and 0 allies near, 0 healers in range, 1 hexes]
3. **Setup** (phase 0:47 to 1:15):
   - EDGE plan flag game: push side 4v4 contest (Prot, Assassin, Air Ele, Fire Ele); stand 3v4 hold (7 Monk, Mesmer, AoB Derv)
     where the deaths came: 4v4, 3 damage, 1 healers, pressure 21/s, incoming 59/s, sustain margin -14, uptime 32%, control received 5 interrupts (0 on healers), 3 knockdowns
   - hook plan regrouping: backside 4v4 contest (8 Monk, Ritualist, Ranger, Hammer); stand 4v3 convert (7 Monk, Prot, Mesmer, AoB Derv)
     where the deaths came: 4v4, 3 damage, 1 healers, pressure 59/s, incoming 21/s, sustain margin +0, uptime 67%, control received 0 interrupts (0 on healers), 3 knockdowns
4. **Decision** (enemy pickup at 0:41): EDGE chose 'held' (fought 4, fell back 3); usual there: already running, fought; that choice is worth +2.3 points against the usual [-3.1, +6.6].
**Why, in short**: EDGE fought 4v4 on the push side (job: contest) with sustain margin -14 while the rest were stand (hold); the Prot died mainly from health; the Assassin died mainly from health; after choosing 'held' at the enemy pickup.
5. **Context**: EDGE: 7 up (main 4), flags even +5 s, DP 0, NPCs K2 A2 B1, Lord dmg 0; hook: 8 up (main 4), flags even -5 s, DP 0, NPCs K2 A2 B1, Lord dmg 0; stand None, boost in None s; builds balance v balance; situation: a monk died first.

### BcS v Men (1037e655), 0:56 to 1:37: BcS lost 5 players (a wipe) on the backside

1. **Result**: deaths BcS 5 until all were back; captures {'Men': 1}; flag lead -9 s; death penalty {'BcS': -75, 'Men': 0}. Win chance for BcS 14.5% -> 4.5% (-10.0); moved by pit_pressure_diff +13.0, morale_diff -11.9, stand -10.7, minute & morale_diff -9.2, boost_clock -8.0.
2. **Mechanics** (deaths model that never saw this match, a few seconds before each death; what raised the risk most):
   - BcS Prot at 1:11 (engine's cause: coordinated enemy pressure (great enemy play)): risk 1.5% at 1:05; health +15.5, enemies within 1,500 +12.0, health_pct & minute +6.8, damage taken (3 s) +5.1 [health 71%, ceiling 1.0, 6 enemies and 6 allies near, 2 healers in range]
   - BcS 7 Monk at 1:14 (engine's cause: out-pressured despite support (prots cast, one monk tied up)): risk 9.5% at 1:10; health +40.5, health_pct & minute +24.3, enemies within 1,500 +12.0, attackers on it +7.1 [health 25%, ceiling 1.0, 6 enemies and 5 allies near, 2 healers in range]
   - BcS Mesmer at 1:20 (engine's cause: out-pressured despite support (prots cast, one monk tied up)): risk 4.5% at 1:15; own healers dead +27.3, local numbers +20.2, health +15.5, enemies within 1,500 +12.0 [health 69%, ceiling 1.0, 6 enemies and 3 allies near, 1 healers in range]
   - BcS 8 Monk at 1:26 (engine's cause: backline down (2 monks dead, in a chain)): risk 26.4% at 1:20; own healers dead +27.3, health +27.2, local numbers +27.2, enemies within 1,500 +16.8 [health 54%, ceiling 1.0, 7 enemies and 3 allies near, 0 healers in range]
3. **Setup** (phase 0:35 to 1:00):
   - BcS plan 8v8 brawl: stand 8v7 convert (8 Monk, 7 Monk, Prot, Ritualist, Mesmer, Paragon, Warrior, Hammer)
     where the deaths came: 8v7, 5 damage, 3 healers, pressure 47/s, incoming 110/s, sustain margin +20, uptime 62%, control received 4 interrupts (4 on healers), 3 knockdowns
   - Men plan 8v8 brawl: stand 7v8 hold (Ritualist 2, 7 Monk, Prot, Mesmer, Ranger, AoB Derv, Hammer); backside 1v0 free (Ritualist 1)
     where the deaths came: 7v8, 4 damage, 3 healers, pressure 98/s, incoming 47/s, sustain margin +5, uptime 75%, control received 1 interrupts (1 on healers), 0 knockdowns
4. **Decision** (enemy pickup at 0:51): BcS chose 'held' (fought 5, fell back 2, died 1); usual there: already running, fought; that choice is worth +2.3 points against the usual [-3.1, +6.6].
**Why, in short**: BcS fought 8v7 on the stand (job: convert) with sustain margin +20 while the rest were ; the Prot died mainly from health; the 7 Monk died mainly from health; after choosing 'held' at the enemy pickup.
5. **Context**: BcS: 8 up (main 8), flags up +17 s, DP 0, NPCs K2 A2 B1, Lord dmg 0; Men: 8 up (main 7), flags down -17 s, DP 0, NPCs K2 A2 B1, Lord dmg 0; stand BcS, boost in 99 s; builds balance v balance; situation: fought away from pit while up on flags (+17 s): could fall back, a monk died first.

## 9. Detailed learnings snapshot

Descriptive measurements across all 53 trained matches (the latest batch, 7 matches, in brackets where it differs). Not causal on their own: they point to questions and candidate variables.

**Runners** (spawn to capture; pushed = an enemy hit the carrier):

| Runner | Runs | Captured | Median s to capture | Dropped | Pushed | Runs by winners |
|---|---|---|---|---|---|---|
| Mes/A | 152 | 53% | 42.5 (34.0) | 68 | 52% | 43% |
| AoB Derv | 106 | 58% | 30.0 (11) | 43 | 43% | 57% |
| Ritualist | 88 | 50% | 35.0 (44) | 42 | 34% | 65% |
| Mesmer | 71 | 52% | 32 (35) | 33 | 35% | 46% |
| Hammer | 53 | 49% | 25.5 (22) | 26 | 28% | 49% |
| 8 Monk | 51 | 31% | 33.0 (36) | 34 | 24% | 47% |
| Dervish | 47 | 57% | 27 (67.5) | 19 | 43% | 57% |
| Stand Mes | 46 | 65% | 30.5 | 15 | 33% | 50% |
| Necromancer | 33 | 61% | 24.0 | 12 | 39% | 9% |
| Monk 4 (WoC) | 32 | 66% | 44 | 11 | 62% | 72% |

Double running: half 232 runs (52% by winners); single 733 runs (48% by winners).

**Flag answers** (answering the enemy's capture): winners: 236 answers, median 40.5 s, 2.0 s slower than possible, 37 answers 30 s+ slower; losers: 223 answers, median 53 s, 8 s slower than possible, 71 answers 30 s+ slower.

**Skills: kill participation** (share of casts at an enemy who died within 5 s; 15+ casts):

- Highest: Augury of Death 36% of 64; Word of Censure 33% of 1200; Shatter Storm 31% of 144; Decapitate 31% of 72; Signet of Rage 29% of 68; Knee Cutter 25% of 24; Invoke Lightning 24% of 319; Chest Thumper 24% of 142; Horns of the Ox 23% of 26; Castigation Signet 22% of 432; Disrupting Throw 21% of 66; Vapor Blade 20% of 45
- Lowest: Parasitic Bond 0% of 108; Reckless Haste 0% of 40; Spiteful Spirit 0% of 55; Images of Remorse 0% of 20; Diversion 0% of 17; Flare 0% of 41; Axe Rake 0% of 19; Crippling Slash 0% of 16

**Interrupts:** skills interrupted most (whose): Healing Burst on the 7 Monk 201; Guardian on the Prot 136; Guardian on the 8 Monk 125; Blessed Light on the 8 Monk 94; Spirit Light Weapon on the Ritualist 84; Cure Hex on the 7 Monk 77; Shield Guardian PvP on the Prot 75; Guardian on the 7 Monk 75; Word of Censure on the Monk 4 (WoC) 66; Signet of Rejuvenation on the 7 Monk 58. Interrupt skills landing most: Power Spike 801; Complicate 769; Power Leak 383; Psychic Instability PvP 280; Savage Shot 214; Cry of Frustration 188; Hammer Bash 179; Lyssa's Haste PvP 89.

**Knockdowns by skill:** Coward 1259; Hammer Bash 1120; Psychic Instability PvP 323; Lightning Surge 282; "Coward!" 134; Mind Shock PvP 132; Bull's Strike 84; Shock 56.

**Spikes survived** (400+ damage in 3 s on one player; survived = alive 8 s later): winners 106 of 137 (77%); losers 186 of 320 (58%). By target: Stand Mes 71% of 52; Prot 60% of 52; 7 Monk 69% of 51; AoB Derv 62% of 42; 8 Monk 45% of 40; Mes/A 88% of 34; Necromancer 60% of 25; Hammer 58% of 24; Air Ele 67% of 21; Mesmer 57% of 21; Ritualist 65% of 17; Ranger 64% of 14; Paragon 62% of 13; Water Ele 73% of 11.

**Monks** (per 2-minute phase alive 60 s+): winners: 11.5 casts a minute, 0.43 fakes, idle 0.0 s while an ally was hurt, reaction 1.6 s, bursts answered 69%; losers: 12.0 casts a minute, 0.52 fakes, idle 0 s while an ally was hurt, reaction 1.3 s, bursts answered 61%.

**Deaths** (935): 331 with a knockdown on the victim; 280 had a monk cast on the victim in the last 5 s. Monk skills interrupted in the 6 s before a death: Healing Burst 41; Blessed Light 37; Guardian 30; Reversal of Fortune 21; Shield Guardian PvP 17; Signet of Rejuvenation 11; Cure Hex 11; Dismiss Condition 8.

## 10. For Denning

- Which curves look wrong to you? A correction (direction, cap, drop, or a pair to always test) is logged with your reason and tested on held-out matches.
- Do any surprises remind you of something the variables don't capture (a missing variable)?
- Any variable you think matters that isn't listed?

