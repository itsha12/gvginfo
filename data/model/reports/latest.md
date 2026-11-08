# Learning report, batch 9

Trained on 133 matches (20 new in this batch). Variables in use: 31; build variables from 60 matches, interactions from 40.

## 0. Data integrity

- Lengths repaired: 5 (1f65fd3b 150 s -> 1027 s) (bbef1904 617 s -> 599 s) (36a65ac6 1319 s -> 1294 s) (ba85aafc 811 s -> 793 s) (f9d6932f 235 s -> 218 s) 
- Matches with a team's Lord damage not observed (left blank, not zero): 9
- Pit NPCs added from the standard roster (never seen in the replay): 465 in 114 matches
- Left out of training: 0

## 1. The honest test

**Beats strength alone (not yet clear: the range includes 0).** Held-out accuracy (matches held out whole), log loss in brackets (lower is better):

- strength only: all 76% (0.463), 0-5 min 81% (0.378), 5-10 min 79% (0.426), 10-15 min 72% (0.531), 15-end min 66% (0.595), matches lasting 15 min+ 70% (0.567), matches even on strength (gap under 200) 57% (0.628)
- glass box: all 84% (0.375), 0-5 min 83% (0.378), 5-10 min 84% (0.383), 10-15 min 83% (0.439), 15-end min 89% (0.307), matches lasting 15 min+ 83% (0.423), matches even on strength (gap under 200) 72% (0.637)
- glass box without corrections: all 81% (0.489), 0-5 min 79% (0.505), 5-10 min 81% (0.448), 10-15 min 77% (0.612), 15-end min 85% (0.413), matches lasting 15 min+ 77% (0.58), matches even on strength (gap under 200) 66% (0.816)
- black box: all 77% (0.809), 0-5 min 80% (0.709), 5-10 min 78% (0.766), 10-15 min 74% (0.924), 15-end min 72% (0.935), matches lasting 15 min+ 72% (0.97), matches even on strength (gap under 200) 64% (1.15)
- Gain over strength alone (log loss, resampling whole matches): +0.088 (90% range -0.032 to +0.196).
- Change since batch 8: glass box log loss 0.367 -> 0.375; strength only 0.412 -> 0.463.
- Cap test on spike_killable_diff (held-out log loss, 133 matches): none 0.3758, 10 points 0.3869, 15 points 0.383, 20 points 0.3794, 25 points 0.3761; chosen: no cap (no option beat it on unseen matches).
- Calibration by minute (held-out predictions on 133 matches; every win chance below and in values, usual play and the TQs goes through it). Predicted -> how often those teams won -> calibrated:
  - 0 to 6 min: 0.5% -> won 1.1% (81 matches) -> 1.0%; 3.2% -> won 5.7% (77 matches) -> 5.5%; 93.0% -> won 82.0% (70 matches) -> 82.8%; 96.7% -> won 93.9% (76 matches) -> 94.1%; 99.4% -> won 99.0% (79 matches) -> 99.1%
  - 6 to 12 min: 0.4% -> won 1.0% (82 matches) -> 1.0%; 3.5% -> won 21.0% (44 matches) -> 19.2%; 92.7% -> won 72.9% (41 matches) -> 75.0%; 96.4% -> won 78.9% (44 matches) -> 80.7%; 99.6% -> won 98.7% (80 matches) -> 98.7%
  - 12 to 18 min: 0.5% -> won 9.6% (48 matches) -> 7.4%; 3.4% -> won 5.6% (28 matches) -> 7.4%; 93.0% -> won 91.5% (24 matches) -> 91.2%; 96.5% -> won 90.1% (29 matches) -> 91.2%; 99.5% -> won 90.2% (48 matches) -> 91.2%
  - 18 to end min: 0.4% -> won 7.6% (37 matches) -> 4.0%; 3.5% -> won 0.9% (16 matches) -> 4.0%; 92.5% -> won 100.0% (14 matches) -> 95.9%; 96.6% -> won 98.9% (19 matches) -> 95.9%; 99.6% -> won 92.6% (37 matches) -> 95.9%

## 2. What it leans on

- **morale_diff & map_pit_to_stand** 0.717 (was 0.464): own minus enemy morale summed over players (boosts +, death penalty -) TOGETHER WITH the map's distance from a pit to the stand (average of both sides)
- **morale_diff** 0.641 (was 0.444): own minus enemy morale summed over players (boosts +, death penalty -)
- **spike_killable_diff** 0.489 (was 0.315): enemy minus own players within one spike of the other side (DP stacking; 0 unless a spike build is involved)
- **alive_diff** 0.383 (was 0.131): own minus enemy players alive
- **knights_diff** 0.304 (was 0.442): own minus enemy pit knights alive
- **knights_diff & map_flag_run** 0.258 (was 0.088): own minus enemy pit knights alive TOGETHER WITH the map's flag run Y: distance from the flag spawn to the stand (average of both sides)
- **spike_build_own** 0.225 (was 0.176): own build is a spike build (1) or not (0)
- **spike_build_enemy** 0.213 (was 0.169): enemy build is a spike build
- **stand** 0.205 (was 0.192): who holds the flag stand: 1 own, 0 nobody, -1 enemy
- **lord_dps_enemy** 0.178 (was 0.159): enemy build's measured Lord damage per second
- **lord_dps_own** 0.177 (was 0.151): own build's measured Lord damage per second if all its non-healers were at the Lord
- **archers_diff & map_flag_run** 0.146 (new): own minus enemy pit archers alive TOGETHER WITH the map's flag run Y: distance from the flag spawn to the stand (average of both sides)

## 3. The curves in words

Points = win-chance points added to an otherwise even game at each range of the variable.

- **morale_diff & map_pit_to_stand** (interaction): see wp_model.md
- **morale_diff** rises from -30.1 to +25.2 points (-470.0..-199.0: -30.1; -151.5..-110.5: -21.4; -84.5..-45.5: -20.5; -15.5..-0.5: +1.4; 0.5..18.5: -0.7; 47.5..90.5: +25.9; 134.5..180.5: +22.9)
- **spike_killable_diff** rises from -44.5 to +44.6 points (-8.0..-7.5: -44.5; -5.5..-4.5: -45.5; -3.5..-2.5: -44.2; -1.5..-0.5: -33.8; 0.5..1.5: +33.7; 2.5..4.5: +44.8; 5.5..7.5: +43.9)
- **alive_diff** rises from -41.3 to +40.4 points (-8.0..-5.5: -41.3; -4.5..-3.5: -26.9; -2.5..-1.5: -22.4; -0.5..0.5: +0.2; 1.5..2.5: +21.4; 3.5..4.5: +26.0)
- **knights_diff** rises from -20.9 to +21.2 points (-2.0..-1.5: -20.9; -1.5..-0.5: -9.7; -0.5..0.5: +0.0; 0.5..1.5: +8.9; 1.5..2.0: +21.2)
- **knights_diff & map_flag_run** (interaction): see wp_model.md
- **spike_build_own** rises from -3.6 to +12.1 points (0.0..0.5: -3.6; 0.5..1.0: +12.1)
- **spike_build_enemy** falls from +3.4 to -11.4 points (0.0..0.5: +3.4; 0.5..1.0: -11.4)
- **stand** rises from -5.7 to +5.6 points (-1.0..-0.5: -5.7; -0.5..0.5: +0.2; 0.5..1.0: +5.6)
- **lord_dps_enemy** falls from +5.0 to +2.0 points (35.8..69.05: +5.0; 77.7..78.4: +5.0; 83.55..88.85: -5.0; 95.6..102.6: +5.0; 102.95..106.0: -5.0; 111.6..113.25: +3.9; 121.35..146.3: +1.5)

## 4. Discovery

**Interaction candidates** (a screen: pairs whose combination seems to matter beyond each alone; untested until held-out matches confirm them; switched on in the model from 40 matches):

- morale_diff with spike_killable_diff (screen 0.182)
- morale_diff with spike_build_enemy (screen 0.168)
- morale_diff with spike_build_own (screen 0.168)
- morale_diff with lord_dps_enemy (screen 0.154)
- morale_diff with lord_dps_own (screen 0.154)
- alive_diff with morale_diff (screen 0.151)
- minute with morale_diff (screen 0.151)
- morale_diff with map_pit_to_stand (screen 0.150)

**Candidate variables** (proposed variables, tested on unseen matches; log loss, lower is better):

- split_diff: 0.375 without, 0.384 with: does not improve yet. own minus enemy players on a split (away from their main group on the enemy half, not carrying). Proposed batch 1 by Claude: the knights curve runs backwards, maybe standing in for the cost of splitting
- turtle_diff: 0.375 without, 0.375 with: does not improve yet. own minus enemy share of live players at home (own base or pit). Proposed 2026-11-06 from OG comms ([ohno v One], [ohno v Crew]: 'they are turtling, we have to make a play'); comms_vars.py: teams that turtled 60 s won 3 of 13 times
- footmen_diff: 0.375 without, 0.405 with: does not improve yet. own minus enemy footmen alive (base NPCs, not pit NPCs). Proposed 2026-11-06 from OG comms ([ohno v NwAy]: 'this way we don't lose footmen'; [ohno v Fun]: fake collapse to the footmen)
- no_healer_groups_diff: 0.375 without, 0.375 with: does not improve yet. own minus enemy groups of 2+ with no healer. Proposed 2026-11-06 from OG comms ([ohno v One]: keep a prot and a monk on one side, the Rit and a monk on the other); comms_vars.py: such groups lose players twice as often
- solo_healers_diff: 0.375 without, 0.376 with: does not improve yet. own minus enemy healers with no other own healer within casting range. Proposed 2026-11-06 from OG comms ('solo monk, go on the monk'); Denning: a monk alone has no other monk to support it

**Surprises** (moments where the held-out model was most confident about the team that went on to lose; each points to something the variables don't capture yet):

- RACK v hdm (1f65fd3b) at 14:30: a model that never saw this match gave RACK 2.8%, and RACK won. Why it thought so: knights_diff & map_flag_run -35.4, morale_diff -22.0, knights_diff -21.6, team strength -14.0, lord_damage_diff & map_flag_run -7.8
- hdm v HC (28447c4a) at 24:45: a model that never saw this match gave HC 0.1%, and HC won. Why it thought so: morale_diff & map_bases_apart -45.5, morale_diff -40.0, lord_exposed_diff -36.1, knights_diff -31.0, morale_diff & map_pit_to_stand +13.9
- Crew v BcS (3ee18c0c) at 12:45: a model that never saw this match gave BcS 7.7%, and BcS won. Why it thought so: morale_diff -17.8, alive_diff -14.0, knights_diff -12.0, archers_diff & map_flag_run +11.2, bodyguard_diff & map_flag_run -9.3
- cope v Team (427c825b) at 6:00: a model that never saw this match gave Team 19.0%, and Team won. Why it thought so: morale_diff -36.4, morale_diff & map_flag_run -33.3, morale_diff & map_bases_apart +16.9, team strength -9.9, spike_build_own +9.5
- Fun v hold (99d9b260) at 2:15: a model that never saw this match gave hold 1.9%, and hold won. Why it thought so: spike_killable_diff -45.3, morale_diff & map_flag_run +26.8, archers_diff & map_flag_run -25.9, morale_diff -23.6, team strength +22.8
- Fun v hdm (d5d66293) at 3:45: a model that never saw this match gave hdm 17.5%, and hdm won. Why it thought so: team strength +48.7, spike_killable_diff -46.8, knights_diff & map_flag_run -22.1, morale_diff -20.0, morale_diff & map_flag_run +12.1

## 5. Denning's rulings seen through the model

Win chance from a model that never saw the match, 20 s before and 60 s after each ruled moment. Contributions are points for an otherwise even game (the curves' scale).

- hdm v HC (28447c4a) 5:01 (split answered), HC: 41.1% 20 s before -> 65.1% 60 s after (+24.0). After: morale_diff & map_bases_apart +39.9, knights_diff -31.0, morale_diff +12.2, archers_diff -11.0
- hdm v HC (28447c4a) 5:01 (split answered), hdm: 65.0% 20 s before -> 35.1% 60 s after (-29.9). After: morale_diff & map_bases_apart -40.6, knights_diff +31.7, archers_diff +10.1, morale_diff -8.8
- hdm v HC (28447c4a) 1:02 (split detection), HC: 54.0% 20 s before -> 63.1% 60 s after (+9.1). After: morale_diff & map_bases_apart +34.0, morale_diff & map_flag_run -16.0, carrying_diff -6.6, stand -6.3
- hdm v HC (28447c4a) 1:02 (split detection), hdm: 48.0% 20 s before -> 38.9% 60 s after (-9.1). After: morale_diff & map_bases_apart -34.2, morale_diff & map_flag_run +15.5, carrying_diff +6.6, stand +6.4
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), HC: 35.1% 20 s before -> 35.1% 60 s after (+0.0). After: morale_diff & map_bases_apart +39.9, lord_exposed_diff -36.1, knights_diff -31.0, archers_diff & map_bases_apart +14.0
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), hdm: 65.1% 20 s before -> 66.8% 60 s after (+1.7). After: morale_diff & map_bases_apart -40.6, lord_exposed_diff +36.6, knights_diff +31.7, archers_diff & map_bases_apart -12.4
- hdm v HC (bbef1904) 8:10 (death), HC: 60.6% 20 s before -> 21.9% 60 s after (-38.7). After: alive_diff -28.0, morale_diff -20.0, morale_diff & map_pit_to_stand -8.7, stand +5.3
- hdm v HC (bbef1904) 8:10 (death), hdm: 46.3% 20 s before -> 77.3% 60 s after (+31.0). After: alive_diff +27.8, morale_diff +24.6, morale_diff & map_pit_to_stand +6.5, stand -5.3
- Men v HC (faec428a) 9:31 (death), HC: 35.1% 20 s before -> 35.1% 60 s after (+0.0). After: knights_diff -10.9, archers_diff +10.1, archers_diff & map_bases_apart -10.0, knights_diff & map_pit_to_stand -8.0
- Men v HC (faec428a) 9:31 (death), Men: 64.6% 20 s before -> 65.1% 60 s after (+0.5). After: knights_diff +11.3, archers_diff -11.0, archers_diff & map_bases_apart +10.6, knights_diff & map_pit_to_stand +7.8

## 6. Why: the node models

Each explains one result from what happened before it (time order enforced), tested on matches it never saw. AUC = how often a moment that led to the result scores above one that didn't (0.5 = guessing, 1 = perfect).

**deaths** (133 matches, 275590 moments, 8095 results): adds to the simple baseline (AUC 0.921 against 0.79 for health_pct and damage_taken_3s alone).
- **enemies_near** (enemies within 1,500) rises from -22.9 to +26.2 points (0.0..0.5: -22.9; 0.5..1.5: -12.0; 1.5..2.5: -0.7; 2.5..3.5: +4.6; 3.5..4.5: +8.8; 4.5..5.5: +10.4; 5.5..6.5: +13.1; 6.5..7.5: +17.0; 7.5..8.0: +26.2)
- **strength_gap** (own minus enemy team strength) falls from +17.4 to -9.3 points (-989.0..-583.0: +17.4; -437.5..-322.5: +8.1; -203.5..-96.5: +8.5; -60.5..0.0: +4.7; 60.5..92.5: -5.2; 194.0..304.5: -7.7; 434.5..576.0: -15.5)
- **health_pct** (current health %) falls from +40.5 to -5.5 points (1.0..48.5: +40.5; 60.5..68.5: +20.5; 74.5..78.5: +8.1; 82.5..85.5: +3.9; 88.5..91.5: +1.1; 93.5..95.5: -2.9; 97.5..99.5: -4.8)
- **allies_near** (allies within 1,500) falls from +20.2 to -7.3 points (0.0..0.5: +20.2; 0.5..1.5: +10.5; 1.5..2.5: +4.8; 2.5..3.5: -1.5; 3.5..4.5: -2.6; 4.5..5.5: -3.9; 5.5..6.5: -5.2; 6.5..7.0: -7.3)
- **local_diff** (allies minus enemies within 2,000) falls from +23.6 to -16.9 points (-8.0..-3.5: +23.6; -2.5..-1.5: +12.8; -0.5..0.5: -4.1; 1.5..2.5: -4.0; 3.5..4.5: +6.5; 5.5..7.0: -16.9)
- **own_prots** (own prot skills) falls from +9.3 to -6.1 points (1.0..4.5: +9.3; 6.5..7.5: +10.4; 8.5..9.5: +1.4; 10.5..11.5: +0.0; 12.5..13.5: -5.0; 14.5..15.5: -0.3; 16.5..18.0: -6.1)
- **enemy_strips** (enemy enchantment removal skills) falls from +25.4 to -1.1 points (0.0..0.5: +25.4; 0.5..1.5: +1.9; 1.5..2.5: +2.0; 2.5..3.5: -4.2; 3.5..4.5: -4.8; 4.5..5.5: -3.6; 5.5..6.5: -7.4; 6.5..7.0: -1.1)
- **dist_own_pit** (distance from its own pit) rises from -2.4 to +10.2 points (6.0..1352.5: -2.4; 2334.5..3975.5: -1.5; 5182.5..6137.5: -3.1; 6889.5..7523.5: -1.1; 8176.5..8831.5: -1.4; 9718.5..10709.5: -0.6; 11916.5..13380.5: +9.7)
- **minute** (match minute) rises from -0.1 to +15.1 points (0.1..1.15: -0.1; 2.15..3.15: -3.8; 4.25..5.35: -3.5; 6.55..7.95: -1.2; 9.45..11.05: -1.8; 12.95..15.05: -1.2; 17.75..21.05: +3.7)

**kill conversion** (132 matches, 2448 moments, 725 results): adds to the simple baseline (AUC 0.783 against 0.683 for burst_damage and target_health_pct alone).
- **burst_damage** (damage in the 2 s burst) rises from -10.6 to +23.8 points (250.0..256.5: -10.6; 264.5..275.5: -10.3; 285.5..296.5: -8.6; 310.5..325.5: -3.2; 342.5..359.5: -0.4; 382.5..409.5: +7.6; 447.5..506.5: +20.4)
- **target_healers_in_range** (target's healers in range) falls from +26.9 to -7.9 points (0.0..0.5: +26.9; 0.5..1.5: +2.2; 1.5..2.5: -4.2; 2.5..3.0: -7.9)
- **target_health_pct** (target health % when the burst started) falls from +23.1 to -10.3 points (0.0..39.5: +23.1; 51.5..57.5: +9.1; 63.5..68.5: +3.1; 72.5..76.5: +1.1; 80.5..84.5: -1.4; 87.5..91.5: -3.7; 95.5..99.5: -9.7)
- **target_ceiling** (target's health ceiling) falls from +27.4 to -10.1 points (0.4..0.69: +27.4; 0.7..0.73: +13.6; 0.84..0.85: +10.1; 0.88..0.91: +5.7; 0.94..0.95: +3.5; 0.99..1.02: -3.4; 1.1..1.1: -10.1)
- **strength_gap** (attacking minus target team strength) rises from -11.0 to +18.2 points (-958.0..-565.5: -11.0; -381.5..-226.0: -10.5; -92.5..-40.0: -1.8; 0.0..79.5: +1.6; 104.5..151.5: -1.4; 281.5..416.5: +0.9; 565.5..625.5: +8.1)
- **target_prot_up** (a prot on the target) falls from +3.3 to -6.1 points (0.0..0.5: +3.3; 0.5..1.0: -6.1)
- **enemy_prots** (target team's prot skills) falls from +9.6 to -6.5 points (1.0..4.5: +9.6; 6.5..7.5: +9.0; 8.5..9.5: +2.0; 10.5..11.5: +0.3; 12.5..13.5: -1.9; 14.5..15.5: -3.4; 16.5..17.5: -5.4)

**flag answer** (seconds an answer to an enemy capture was slower than possible; 111 matches, 1014 rows): adds to the simple baseline (typical error 16.7s against 27.8s for the median; explains 71% of the spread).
- **parked_s** (seconds the flag lay parked (dropped 5 s or more: not running yet)): 0.0..2.5: -5.2 s; 8.5..13.5: +5.2 s; 19.5..27.5: +15.3 s; 32.5..36.5: +33.1 s; 44.5..58.5: +49.6 s; 76.5..99.5: +61.6 s; 118.0..259.0: +65.4 s
- **enemies_in_the_way** (enemy presence along the runner's trip back to the spawn): 0.0..0.5: -5.9 s; 4.5..10.5: -4.5 s; 15.5..20.5: -2.2 s; 26.5..37.5: -0.7 s; 47.5..60.5: +2.8 s; 85.5..110.5: +8.3 s; 143.0..203.0: +14.6 s
- **enemy_deaths_during** (enemy deaths during the answer): 0.0..0.5: -3.7 s; 0.5..1.5: +8.4 s; 1.5..2.5: +17.2 s; 2.5..3.5: +23.7 s; 3.5..4.5: +25.2 s; 4.5..7.0: +23.8 s
- **own_deaths_during** (own deaths during the answer): 0.0..0.5: -3.4 s; 0.5..1.5: +5.9 s; 1.5..2.5: +11.2 s; 2.5..3.5: +21.1 s; 3.5..4.5: +29.6 s; 4.5..5.5: +38.5 s; 5.5..6.5: +49.2 s; 6.5..9.5: +60.8 s; 9.5..17.0: +69.6 s
- **carrier_damage_taken** (damage the carrier took while carrying): 0.0..0.5: -4.0 s; 30.5..54.5: -3.7 s; 81.5..105.0: -1.9 s; 141.5..207.5: -0.2 s; 261.5..316.5: +1.4 s; 419.5..553.0: +5.5 s; 741.5..1116.0: +14.5 s
- **runner_to_spawn** (runner's distance to its flag spawn when the enemy captured): 16.0..711.5: -9.4 s; 1341.0..1882.0: -4.2 s; 2705.5..3430.0: -0.9 s; 4028.5..4397.5: +1.5 s; 4885.5..5577.5: +3.3 s; 6313.5..6922.0: +4.5 s; 7622.5..8562.5: +3.8 s
- **morale_diff** (own minus enemy morale): -219.0..-91.5: +8.2 s; -59.5..-33.5: +3.6 s; -17.0..-14.5: +2.2 s; -1.0..1.0: +0.2 s; 14.5..17.0: -1.3 s; 32.5..60.5: -3.9 s; 87.5..126.5: -5.9 s
- **possible_s** (fastest possible answer (s) from the flag model at the enemy's capture): 0.0..3.5: -3.9 s; 8.5..13.5: -2.8 s; 20.5..25.5: -1.3 s; 30.5..33.5: +0.9 s; 36.5..40.5: +3.9 s; 44.5..49.5: +2.5 s; 55.5..62.5: -0.0 s
- **quick_handoffs** (quick hand-offs (a teammate picked it up within 5 s)): 0.0..0.5: -1.4 s; 0.5..1.5: +5.0 s; 1.5..2.5: +7.0 s; 2.5..3.0: +12.2 s
- **forced_drops** (drops with the carrier hit in the 5 s before, or dying): 0.0..0.5: -1.1 s; 0.5..1.5: +15.4 s; 1.5..4.0: +14.5 s

**npc loss** (133 matches, 13799 moments, 2691 results): adds to the simple baseline (AUC 0.844 against 0.752 for attackers and defenders alone).
- **npc_damage_5s** (damage on the pit NPCs in the last 5 s) rises from -17.2 to +35.5 points (0.0..0.5: -17.2; 22.5..36.5: +2.7; 50.5..69.5: +7.2; 89.5..111.5: +15.0; 135.5..162.5: +23.9; 195.5..237.5: +27.9; 297.5..398.5: +34.3)
- **defenders** (own players in the pit) falls from +33.7 to -31.6 points (0.0..0.5: +33.7; 0.5..1.5: +18.1; 1.5..2.5: +10.2; 2.5..3.5: +1.7; 3.5..4.5: -11.5; 4.5..5.5: -14.2; 5.5..6.5: -15.4; 6.5..7.5: -26.9; 7.5..8.0: -31.6)
- **defenders_elsewhere** (own players alive outside the pit) falls from +21.5 to -9.4 points (0.0..0.5: +21.5; 0.5..1.5: +12.5; 1.5..2.5: +12.0; 2.5..3.5: +2.2; 3.5..4.5: -7.0; 4.5..5.5: -14.2; 5.5..6.5: -14.2; 6.5..7.5: -13.3; 7.5..8.0: -9.4)
- **defender_healers** (of which healers) falls from +20.8 to -7.3 points (0.0..0.5: +20.8; 0.5..1.5: -1.4; 1.5..2.5: -5.7; 2.5..3.5: -7.2; 3.5..4.0: -7.3)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -19.4 to +4.7 points (1.9..12.25: -19.4; 22.5..27.7: -5.9; 32.15..36.95: -3.4; 46.45..57.65: +3.3; 64.35..70.95: +5.7; 76.15..84.55: +7.4; 94.15..110.1: +4.7)
- **attackers** (enemy players in the pit) rises from -8.7 to +10.5 points (1.0..1.5: -8.7; 1.5..2.5: -2.8; 2.5..3.5: -1.7; 3.5..4.5: +0.8; 4.5..5.5: +5.9; 5.5..6.5: +7.6; 6.5..7.5: +9.5; 7.5..8.0: +10.5)
- **attackers_share** (share of the attacking team's live players in the pit (OG comms: merge before pushing the pit)) rises from -5.9 to +8.2 points (0.12..0.13: -5.9; 0.23..0.27: -4.9; 0.35..0.42: -3.3; 0.53..0.61: +3.7; 0.65..0.73: +5.7; 0.78..0.87: +6.8; 0.94..1.0: +8.2)
- **strength_gap** (attacking minus defending team strength) rises from -5.1 to +9.1 points (-989.0..-494.0: -5.1; -295.0..-151.5: -8.4; -55.5..40.0: +1.7; 81.5..108.0: -2.5; 251.5..301.5: +1.2; 386.0..447.5: +2.9; 547.0..665.0: +5.1)
- **npc_healing_10s** (healing on own pit NPCs and Lord in the last 10 s) falls from +3.1 to -17.8 points (0.0..1.5: +3.1; 41.5..60.5: +2.1; 90.5..134.5: +0.8; 160.5..202.5: -0.6; 241.5..288.5: -5.5; 348.5..408.5: -7.0; 500.5..651.5: -13.3)

**lord damage** (Lord damage dealt in the next 10 s while players are in the enemy pit; 128 matches, 15526 rows): adds to the simple baseline (typical error 71.2 against 92.4 for the median; explains 33% of the spread).
  ('chance of any' curves: points of the chance of any Lord damage in the window; 'amount' curves: % more Lord damage when there is some.)
- **defenders (chance of any)** (own players in the pit): 0.0..0.5: +37.5 points; 0.5..1.5: +27.1 points; 1.5..2.5: +24.8 points; 2.5..3.5: +4.6 points; 3.5..4.5: -12.5 points; 4.5..5.5: -25.1 points; 5.5..6.5: -36.7 points; 6.5..7.5: -38.8 points; 7.5..8.0: -44.8 points
- **bodyguard (chance of any)** (own Bodyguard alive): 0.0..0.5: +24.9 points; 0.5..1.0: -10.4 points
- **knights (chance of any)** (own knights alive): 0.0..0.5: +14.1 points; 0.5..1.5: -9.5 points; 1.5..2.0: -12.6 points
- **minute (chance of any)** (match minute): 0.5..2.85: -18.5 points; 3.85..5.05: -13.3 points; 6.15..7.35: +0.6 points; 8.75..10.15: +1.7 points; 11.55..13.55: -5.4 points; 15.75..18.35: +2.8 points; 21.05..24.35: +12.6 points
- **attacker_healers (chance of any)** (of which healers): 0.0..0.5: -10.6 points; 0.5..1.5: +4.0 points; 1.5..2.5: +12.4 points; 2.5..3.5: +12.7 points; 3.5..4.0: +2.4 points
- **npc_healing_10s (chance of any)** (healing on own pit NPCs and Lord in the last 10 s): 0.0..1.5: -7.5 points; 41.5..60.5: +9.0 points; 90.5..133.5: +10.3 points; 158.5..200.5: +11.4 points; 239.5..285.5: +12.4 points; 347.5..405.5: +13.1 points; 501.5..651.5: +13.6 points
- **attackers_lord_dps (chance of any)** (attackers' measured damage per second against a Lord (benchmarks)): 1.9..12.55: -15.6 points; 22.7..31.1: -14.2 points; 32.8..43.0: -2.8 points; 53.2..64.25: -1.1 points; 66.25..73.15: +0.1 points; 80.0..85.85: +17.9 points; 99.35..111.4: +14.2 points
- **attackers_share (chance of any)** (share of the attacking team's live players in the pit (OG comms: merge before pushing the pit)): 0.12..0.13: -10.5 points; 0.23..0.27: -5.6 points; 0.35..0.42: -5.2 points; 0.53..0.61: +6.7 points; 0.65..0.73: +11.0 points; 0.78..0.87: +12.4 points; 0.94..1.0: +13.4 points
- **attackers (chance of any)** (enemy players in the pit): 1.0..1.5: -9.5 points; 1.5..2.5: -3.1 points; 2.5..3.5: -2.3 points; 3.5..4.5: +1.9 points; 4.5..5.5: +4.9 points; 5.5..6.5: +5.6 points; 6.5..7.5: +6.5 points; 7.5..8.0: +15.4 points
- **strength_gap (chance of any)** (attacking minus defending team strength): -989.0..-423.5: -5.2 points; -289.0..-84.0: +6.6 points; -6.0..64.0: +7.7 points; 101.0..226.0: -5.2 points; 295.0..375.0: -6.0 points; 432.5..490.0: -3.6 points; 572.5..665.0: -7.5 points

**lord kill** (128 matches, 15516 moments, 1119 results): adds to the simple baseline (AUC 0.965 against 0.938 for attackers and defenders alone).
- **defenders** (own players in the pit) falls from +44.2 to -47.9 points (0.0..0.5: +44.2; 0.5..1.5: +37.8; 1.5..2.5: +15.1; 2.5..3.5: +3.8; 3.5..4.5: -18.8; 4.5..5.5: -23.1; 5.5..6.5: -35.9; 6.5..7.5: -43.9; 7.5..8.0: -47.9)
- **minute** (match minute) rises from -48.3 to +26.5 points (0.5..2.85: -48.3; 3.85..5.05: -13.9; 6.15..7.35: +3.3; 8.75..10.15: +14.7; 11.55..13.55: +16.6; 15.75..18.35: +21.9; 21.05..24.35: +26.0)
- **defenders_elsewhere** (own players alive outside the pit) falls from +35.6 to -31.3 points (0.0..0.5: +35.6; 0.5..1.5: +17.5; 1.5..2.5: +16.3; 2.5..3.5: +15.1; 3.5..4.5: +3.5; 4.5..5.5: -21.8; 5.5..6.5: -23.2; 6.5..7.5: -31.2; 7.5..8.0: -31.3)
- **defender_healers** (of which healers) falls from +32.9 to -34.7 points (0.0..0.5: +32.9; 0.5..1.5: +8.9; 1.5..2.5: -10.6; 2.5..3.5: -30.0; 3.5..4.0: -34.7)
- **attackers** (enemy players in the pit) rises from -29.6 to +20.7 points (1.0..1.5: -29.6; 1.5..2.5: +2.9; 2.5..3.5: +6.2; 3.5..4.5: +9.5; 4.5..5.5: +14.4; 5.5..6.5: +15.3; 6.5..7.5: +18.0; 7.5..8.0: +20.7)
- **attackers_share** (share of the attacking team's live players in the pit (OG comms: merge before pushing the pit)) rises from -16.5 to +24.1 points (0.12..0.13: -16.5; 0.23..0.27: -13.2; 0.35..0.42: -9.9; 0.53..0.61: -5.4; 0.65..0.73: +20.2; 0.78..0.87: +22.1; 0.94..1.0: +24.1)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from +14.2 to +18.9 points (1.9..12.55: +14.2; 22.7..31.1: -17.2; 32.8..43.0: -14.3; 53.2..64.25: -7.4; 66.25..73.15: -3.7; 80.0..85.85: +17.7; 99.35..111.4: +19.9)
- **res_in** (seconds until the next res) rises from -42.8 to -1.8 points (1.0..8.5: -42.8; 17.5..26.5: -0.9; 35.5..44.5: +14.1; 53.5..62.5: +13.0; 68.5..74.5: +11.1; 80.5..86.5: +9.0; 95.5..107.5: +3.4)
- **lord_health** (the Lord's rebuilt health as a share of its max (lord.py)) falls from +48.7 to -5.7 points (0.0..0.15: +48.7; 0.4..0.59: +36.8; 0.7..0.78: +27.8; 0.83..0.87: +17.7; 0.91..0.94: +12.5; 0.96..0.98: +7.9; 0.99..1.0: +2.9)


## 6b. The learned nodes (step 2 of the learned causal map)

Each node uses only the causal-map links into it. A link's strength is how much worse the node predicts matches it never saw without that link's features (refit without them, same folds); supported when the gain is more than twice its spread across folds, rejected when dropping it helps by more than that, otherwise not clear yet.

**run outcome** (map R.3; 133 matches, 4490 cases, result rate 61%): log loss 0.6444 against 0.6698 for the simple baseline (adds to the simple baseline).
- link P.10 -> R.3: gain +0.0107 (+/- 0.0053), supported (stand_own, stand_enemy, enemy_boost_in, flag_lead...)
- link C.map -> R.3: gain +0.0009 (+/- 0.0025), not clear yet (run_dist)
- link K.11 -> R.3: gain +0.0002 (+/- 0.0012), not clear yet (crippled_so_far, knocked_down_so_far, other_control_so_far, damage_so_far...)
- link C.strength -> R.3: gain -0.001 (+/- 0.0029), not clear yet (strength_gap)
- link A.allocation -> R.3: gain -0.0031 (+/- 0.0037), not clear yet (escort, own_main, enemy_main, enemy_power_play)
  - leans on **checkpoint_s** (seconds into the run): -6.2 points at 5.0 to 10.0, +13.5 at 22.5 to 30.0
  - leans on **flag_lead** (flag lead at the start (s)): +1.0 points at -80.0 to -60.5, -11.9 at 58.5 to 129.0
  - leans on **run_dist** (distance from the team's spawn to the stand): +8.3 points at 4170.0 to 4296.0, -1.8 at 9255.5 to 9335.0

**flag swing** (map R.3; 133 matches, 5131 cases, average 0.2 s): mean absolute error (s) 28.8927 against 29.5919 for the simple baseline (adds to the simple baseline).
- link P.10 -> R.3: gain +0.36 (+/- 0.13), supported (waiting_runner, backup_flag, stand_own, stand_enemy...)
- link S.scoreboard -> R.3: gain +0.18 (+/- 0.18), not clear yet (flag_lead)
- link C.strength -> R.3: gain +0.17 (+/- 0.11), not clear yet (strength_gap)
- link R.1 -> R.3: gain +0.05 (+/- 0.02), supported (own_deaths_30s, enemy_deaths_30s)
- link C.clock -> R.3: gain +0.0 (+/- 0.04), not clear yet (minute, res_in)
- link C.map -> R.3: gain -0.02 (+/- 0.02), not clear yet (run_dist)
- link A.allocation -> R.3: gain -0.03 (+/- 0.11), not clear yet (own_alive, enemy_alive, own_main, enemy_main...)
  - leans on **flag_lead** (flag lead now (s)): +12.8 s at -129.0 to -69.5, -13.9 at 65.5 to 110.0
  - leans on **strength_gap** (team strength gap): -3.2 s at -989.0 to -576.0, +4.1 at 576.0 to 989.0
  - leans on **own_eta** (flag model: seconds until own team could capture): -4.8 s at 1.0 to 8.5, +2.2 at 72.5 to 180.0

**run defence** (map R.3; 133 matches, 4490 cases, result rate 61%): log loss 0.6564 against 0.6698 for the simple baseline (adds to the simple baseline).
- link C.map -> R.3: gain +0.0014 (+/- 0.0031), not clear yet (run_dist)
- link A.mesa_free -> R.3: gain +0.0008 (+/- 0.0011), not clear yet (def_free, pushers_so_far, control_so_far, damage_so_far)
- link C.strength -> R.3: gain -0.0023 (+/- 0.0022), not clear yet (strength_gap)
- link A.allocation -> R.3: gain -0.0031 (+/- 0.0028), not clear yet (escort, att_main, def_main)
  - leans on **checkpoint_s** (seconds into the run): -5.9 points at 5.0 to 10.0, +13.3 at 22.5 to 30.0
  - leans on **run_dist** (distance from the runner's spawn to the stand): +12.4 points at 4170.0 to 4296.0, -2.7 at 9255.5 to 9335.0
  - leans on **def_free** (defenders alive and not on flag duty at the run's start): +6.8 points at 0.0 to 3.5, -3.0 at 7.5 to 8.0

**capture speed** (map R.3; 125 matches, 1060 cases, average 40.2 s): mean absolute error (s) 16.005 against 16.0736 for the simple baseline (no better than the simple baseline yet).
- link K.11 -> R.3: gain +0.12 (+/- 0.05), supported (pushers_10s, control_10s, damage_10s)
- link C.strength -> R.3: gain +0.1 (+/- 0.03), supported (strength_gap)
- link A.allocation -> R.3: gain +0.01 (+/- 0.13), not clear yet (defenders_free, escort)
- link C.map -> R.3: gain -0.08 (+/- 0.08), not clear yet (run_dist)
  - leans on **escort** (the runner's escorts): -1.5 s at 0.0 to 0.5, +11.4 at 6.5 to 7.0
  - leans on **strength_gap** (defending team's strength gap): -4.1 s at -989.0 to -576.0, +1.1 at 547.0 to 976.0
  - leans on **defenders_free** (defenders alive and not on flag duty): -4.8 s at 2.0 to 3.5, +1.0 at 7.5 to 8.0

**power play** (map K.4; 133 matches, 1162 cases, result rate 39%): log loss 0.3831 against 0.6698 for the simple baseline (adds to the simple baseline).
- link A.allocation -> K.4: gain +0.0611 (+/- 0.0084), supported (size, own_main, enemy_main, short_dead...)
- link K.2 -> K.4: gain +0.0311 (+/- 0.0074), supported (dps_v_usual)
- link K.5 -> K.4: gain +0.0125 (+/- 0.0052), supported (enemy_prots_10s, enemy_heal_s)
- link P.2 -> K.4: gain +0.007 (+/- 0.0053), not clear yet (spikes_10s, spike_spread)
- link C.strength -> K.4: gain +0.007 (+/- 0.0067), not clear yet (strength_gap)
- link P.14 -> K.4: gain +0.0066 (+/- 0.0034), not clear yet (pushed)
- link R.3 -> K.4: gain +0.0039 (+/- 0.0028), not clear yet (flag_lead)
- link K.11 -> K.4: gain -0.0016 (+/- 0.0022), not clear yet (blind_secs_on_own_10s)
- link P.1 -> K.4: gain -0.0027 (+/- 0.002), not clear yet (spikes_on_healers)
  - leans on **short_dead** (share of the enemy's missing player-seconds: dead): -16.8 points at 0.0 to 0.01, +14.8 at 0.99 to 1.0
  - leans on **dps_v_usual** (own damage per second against the usual of the players alive): -27.6 points at 0.04 to 0.51, +27.5 at 3.25 to 19.89
  - leans on **window_s** (seconds the power play lasted): -16.0 points at 14.0 to 31.5, +31.7 at 104.5 to 290.0

**fight outcome** (map R.2; 133 matches, 989 cases, result rate 47%): log loss 0.3966 against 0.6909 for the simple baseline (adds to the simple baseline).
- link C.strength -> R.2: gain +0.0478 (+/- 0.0119), supported (strength_gap)
- link A.allocation -> R.2: gain +0.0439 (+/- 0.0086), supported (own_local, enemy_local)
- link P.2 -> R.2: gain +0.0335 (+/- 0.0119), supported (spike_spread_diff, spikes_diff)
- link K.1 -> R.2: gain +0.032 (+/- 0.0134), supported (dps_v_usual_diff)
- link P.17 -> R.2: gain +0.0155 (+/- 0.0103), not clear yet (ready_interrupt_diff, dazed_casts_diff, blind_attacks_diff)
- link P.18 -> R.2: gain +0.0038 (+/- 0.0036), not clear yet (strip_right_diff, strip_value_diff)
- link P.13 -> R.2: gain +0.0007 (+/- 0.0009), not clear yet (peel_defensive_diff)
- link P.19 -> R.2: gain -0.0006 (+/- 0.0017), not clear yet (blind_front_secs_diff, blind_defensive_secs_diff)
- link P.5 -> R.2: gain -0.0028 (+/- 0.0031), not clear yet (hex_secs_diff, hex_right_diff)
  - leans on **own_local** (own players in the fight): -36.6 points at 0.0 to 0.5, +24.5 at 7.5 to 8.0
  - leans on **enemy_local** (enemy players in the fight): +30.8 points at 0.0 to 0.5, -24.1 at 7.5 to 8.0
  - leans on **strength_gap** (team strength gap): -29.7 points at -989.0 to -616.5, +31.9 at 616.5 to 989.0

**split chance** (map A.allocation; 133 matches, 10033 cases, result rate 13%): log loss 0.3628 against 0.3905 for the simple baseline (adds to the simple baseline).
- link S.scoreboard -> A.allocation: gain +0.0153 (+/- 0.0039), supported (flag_lead, own_alive, enemy_alive, own_main...)
- link C.clock -> A.allocation: gain +0.0007 (+/- 0.0019), not clear yet (minute, res_in)
- link C.builds -> A.allocation: gain -0.0005 (+/- 0.0032), not clear yet (own_speed, own_snares, enemy_snares)
- link C.strength -> A.allocation: gain -0.0009 (+/- 0.0026), not clear yet (strength_gap)
  - leans on **own_main** (own main): +22.5 points at 0.0 to 2.5, -16.9 at 7.5 to 8.0
  - leans on **own_alive** (own alive): -40.0 points at 0.0 to 3.5, +3.4 at 7.5 to 8.0
  - leans on **own_snares** (snares on own bars): -8.6 points at 0.0 to 0.5, -5.6 at 11.5 to 14.0

**split answer** (map P.11; 94 matches, 375 cases, average -4.1 s): mean absolute error (s) 17.2204 against 18.5587 for the simple baseline (adds to the simple baseline).
- link A.allocation -> P.11: gain +0.81 (+/- 0.37), supported (size)
- link A.mesa_free -> P.11: gain +0.53 (+/- 0.22), supported (def_free, nearest_to_base)
- link S.scoreboard -> P.11: gain +0.09 (+/- 0.14), not clear yet (flag_lead, def_alive, att_main)
- link C.strength -> P.11: gain +0.04 (+/- 0.06), not clear yet (strength_gap)
- link C.clock -> P.11: gain +0.02 (+/- 0.07), not clear yet (minute)
  - leans on **size** (split size): +15.2 s at 1.0 to 1.5, -14.2 at 5.5 to 7.0
  - leans on **nearest_to_base** (nearest defender to its base at the split's entry): +5.0 s at 31.0 to 404.5, +13.0 at 7018.0 to 13776.0
  - leans on **strength_gap** (defending team's strength gap): -3.3 s at -958.0 to -609.5, -3.1 at 538.0 to 976.0

**split effect** (map R.5; 94 matches, 375 cases, result rate 39%): log loss 0.6717 against 0.6744 for the simple baseline (adds to the simple baseline).
- link S.scoreboard -> R.5: gain +0.0056 (+/- 0.0146), not clear yet (def_npc_value, def_free)
- link P.11 -> R.5: gain -0.0002 (+/- 0.003), not clear yet (latency, defenders)
- link A.allocation -> R.5: gain -0.0027 (+/- 0.0042), not clear yet (size, main_diff)
- link K.8 -> R.5: gain -0.0037 (+/- 0.0021), not clear yet (split_healers)
- link C.strength -> R.5: gain -0.0044 (+/- 0.0079), not clear yet (strength_gap)
  - leans on **def_npc_value** (defenders' pit NPC value when the split entered the base): -17.1 points at 0.0 to 0.75, +3.9 at 11.25 to 13.5
  - leans on **def_free** (defenders alive and not on flag duty at entry): +18.5 points at 0.0 to 4.5, -1.0 at 7.5 to 8.0
  - leans on **strength_gap** (splitting team's strength gap): -4.3 points at -976.0 to -375.0, +2.7 at 461.0 to 958.0

**collapse** (map R.1; 120 matches, 848 cases, result rate 12%): log loss 0.3289 against 0.3679 for the simple baseline (adds to the simple baseline).
- link P.9 -> R.1: gain +0.0145 (+/- 0.0033), supported (defenders_10s, contact_diff, npc_hit_to_arrival, res_in_at_arrival)
  - alone: defenders_10s (defenders arriving within 10 s of the first (arrival spread)): gain +0.0072 (+/- 0.0028), supported
  - alone: contact_diff (defenders arriving within 5 s of the first, minus the split's size (numbers at contact)): gain +0.0003 (+/- 0.0008), not clear yet
  - alone: npc_hit_to_arrival (seconds from the split's first hit on an NPC to the first defender's arrival): gain +0.006 (+/- 0.0017), supported
  - alone: res_in_at_arrival (seconds to the next res when the first defender arrived): gain +0.0035 (+/- 0.0014), supported
- link C.builds -> R.1: gain +0.0083 (+/- 0.0028), supported (def_snares, split_speed)
- link P.11 -> R.1: gain +0.0041 (+/- 0.002), supported (latency)
- link A.allocation -> R.1: gain +0.0041 (+/- 0.0027), not clear yet (size, main_diff)
- link C.strength -> R.1: gain +0.0036 (+/- 0.0021), not clear yet (strength_gap)
- link K.13 -> R.1: gain -0.0003 (+/- 0.0017), not clear yet (escape_ready)
  - leans on **defenders_10s** (defenders arriving within 10 s of the first (arrival spread)): -12.3 points at 0.0 to 0.5, +19.1 at 7.5 to 8.0
  - leans on **def_snares** (snares on the defending team's bars): -1.4 points at 0.0 to 0.5, +33.2 at 12.5 to 14.0
  - leans on **main_diff** (own main minus enemy main meanwhile): +10.0 points at -6.0 to -2.25, -20.9 at 1.95 to 6.2

## 7. The usual play

Each choice against the most common one in that kind of decision, in win-chance points over the decision's window, adjusted for the situation, with a 90% range from resampling whole matches. CLEAR = the range excludes 0. Win chance comes from a model that never saw the match. The same comparison over the 30 s BEFORE the decision is a placebo test: a choice can't cause what came before it, so a clear difference there means the effect is partly who makes that choice.

**after wipe** (292 decisions, 124 matches; usual: pushed the pit)
- took the flag (n 37): -5.3 [-9.4, -1.2] CLEAR; in the 30 s before: +1.4 [-2.6, +6.3]
- reset (n 36): -2.4 [-5.9, +1.4]; in the 30 s before: -0.3 [-5.1, +4.1]
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - took the flag, Corrupted Isle: -0.3 (n 10 against 30)

**boost clock** (504 decisions, 121 matches; usual: not running, fought)
- not running, fell back (n 82): -2.1 [-4.4, +0.7]; in the 30 s before: +0.5 [-0.8, +1.7]
- running, advanced (n 74): +3.1 [+0.4, +6.2] CLEAR; in the 30 s before: +2.1 [+0.3, +4.0] ALREADY DIFFERENT BEFORE: partly who chooses it
- not running, advanced (n 70): -0.4 [-2.5, +2.0]; in the 30 s before: +1.1 [-0.5, +2.7]
- not running, held (n 52): +1.2 [-0.9, +3.9]; in the 30 s before: +0.6 [-1.2, +2.3]
- running, fought (n 48): +1.2 [-2.0, +4.8]; in the 30 s before: +1.5 [-0.9, +4.3]
- running, held (n 27): +1.5 [-1.6, +4.1]; in the 30 s before: +2.0 [-0.9, +4.6]
- running, fell back (n 27): +2.3 [-1.2, +5.6]; in the 30 s before: -0.4 [-2.7, +1.9]
- not running, to the spawn (n 10): -3.7 [-9.5, +2.3]; in the 30 s before: -0.8 [-4.9, +3.1]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - not running, fell back, behind in the fight (lowest third, -0.09 or less): +1.1 (n 33 against 57)
  - not running, fell back, middle third: -4.7 (n 32 against 30)
  - not running, fell back, ahead in the fight (top third, above -0.01): -6.9 (n 17 against 27)
  - running, advanced, behind in the fight (lowest third, -0.09 or less): +3.6 (n 10 against 57)
  - running, advanced, middle third: -2.3 (n 31 against 30)
  - running, advanced, ahead in the fight (top third, above -0.01): +2.6 (n 33 against 27)
  - not running, advanced, behind in the fight (lowest third, -0.09 or less): -0.0 (n 24 against 57)
  - not running, advanced, middle third: +0.5 (n 25 against 30)
  - not running, advanced, ahead in the fight (top third, above -0.01): -2.0 (n 21 against 27)
  - not running, held, behind in the fight (lowest third, -0.09 or less): -1.8 (n 16 against 57)
  - not running, held, middle third: +0.1 (n 14 against 30)
  - not running, held, ahead in the fight (top third, above -0.01): +1.3 (n 22 against 27)
  - running, fought, behind in the fight (lowest third, -0.09 or less): -3.2 (n 12 against 57)
  - running, fought, middle third: +0.1 (n 13 against 30)
  - running, fought, ahead in the fight (top third, above -0.01): -0.4 (n 23 against 27)
  - running, held, behind in the fight (lowest third, -0.09 or less): too few yet (n 1 against 57; means -0.1 against -2.3)
  - running, held, middle third: -2.1 (n 14 against 30)
  - running, held, ahead in the fight (top third, above -0.01): -0.6 (n 12 against 27)
  - running, fell back, behind in the fight (lowest third, -0.09 or less): +3.0 (n 10 against 57)
  - running, fell back, middle third: too few yet (n 9 against 30; means -5.5 against 0.1)
  - running, fell back, ahead in the fight (top third, above -0.01): too few yet (n 8 against 27; means 3.7 against -0.2)
  - not running, to the spawn, behind in the fight (lowest third, -0.09 or less): too few yet (n 5 against 57; means -7.5 against -2.3)
  - not running, to the spawn, middle third: too few yet (n 2 against 30; means -3.0 against 0.1)
  - not running, to the spawn, ahead in the fight (top third, above -0.01): too few yet (n 3 against 27; means -5.1 against -0.2)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - not running, fell back, Corrupted Isle: +1.8 (n 10 against 17)
  - not running, fell back, Isle of Jade: -8.9 (n 14 against 27)
  - not running, fell back, Isle of Meditation: -1.3 (n 15 against 24)
  - not running, fell back, Isle of Solitude: +5.3 (n 10 against 13)
  - not running, fell back, Uncharted Isle: -2.3 (n 13 against 13)
  - running, advanced, Corrupted Isle: +10.7 (n 13 against 17)
  - running, advanced, Isle of Meditation: +9.3 (n 15 against 24)
  - running, advanced, Isle of Solitude: +0.4 (n 12 against 13)
  - not running, advanced, Corrupted Isle: +1.3 (n 13 against 17)
  - not running, advanced, Isle of Meditation: +0.9 (n 15 against 24)
  - not running, advanced, Uncharted Isle: +1.6 (n 14 against 13)
  - not running, held, Isle of Jade: +1.0 (n 13 against 27)
  - not running, held, Isle of Solitude: +2.5 (n 12 against 13)
  - running, fought, Isle of Meditation: +4.6 (n 11 against 24)
  - running, held, Isle of Jade: -0.6 (n 13 against 27)

**enemy pickup** (1790 decisions, 128 matches; usual: held, advanced)
- already running, advanced (n 238): -1.5 [-4.9, +2.3]; in the 30 s before: +2.3 [-1.5, +6.3]
- held, fell back (n 234): -3.5 [-9.0, +1.8]; in the 30 s before: +2.5 [-1.3, +7.7]
- already running, fell back (n 180): -2.1 [-5.6, +2.0]; in the 30 s before: +3.5 [-0.5, +7.7]
- held, fought (n 154): -2.0 [-5.7, +1.2]; in the 30 s before: +1.4 [-2.3, +4.8]
- ran, fell back (n 138): -2.7 [-6.1, +1.3]; in the 30 s before: +2.1 [-1.8, +5.9]
- already running, fought (n 129): -2.7 [-6.6, +1.3]; in the 30 s before: +3.2 [-1.0, +7.5]
- ran, advanced (n 116): -1.4 [-5.7, +3.4]; in the 30 s before: +1.0 [-2.5, +5.2]
- already running, held (n 85): -1.1 [-4.8, +3.3]; in the 30 s before: +1.7 [-2.8, +6.5]
- held, held (n 80): +1.8 [-3.0, +6.9]; in the 30 s before: +2.8 [-0.9, +7.1]
- ran, fought (n 71): -0.2 [-3.9, +3.5]; in the 30 s before: +1.5 [-2.6, +5.9]
- ran, held (n 60): -0.1 [-4.7, +4.4]; in the 30 s before: +2.5 [-2.9, +7.4]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - already running, advanced, behind in the fight (lowest third, -0.01 or less): +0.9 (n 66 against 79)
  - already running, advanced, middle third: -0.8 (n 100 against 91)
  - already running, advanced, ahead in the fight (top third, above +0.02): -5.1 (n 72 against 135)
  - held, fell back, behind in the fight (lowest third, -0.01 or less): -1.8 (n 101 against 79)
  - held, fell back, middle third: -1.4 (n 63 against 91)
  - held, fell back, ahead in the fight (top third, above +0.02): -4.7 (n 70 against 135)
  - already running, fell back, behind in the fight (lowest third, -0.01 or less): +1.3 (n 81 against 79)
  - already running, fell back, middle third: -0.7 (n 57 against 91)
  - already running, fell back, ahead in the fight (top third, above +0.02): -6.0 (n 42 against 135)
  - held, fought, behind in the fight (lowest third, -0.01 or less): -0.9 (n 43 against 79)
  - held, fought, middle third: -1.4 (n 28 against 91)
  - held, fought, ahead in the fight (top third, above +0.02): -4.7 (n 83 against 135)
  - ran, fell back, behind in the fight (lowest third, -0.01 or less): +1.4 (n 57 against 79)
  - ran, fell back, middle third: +0.6 (n 45 against 91)
  - ran, fell back, ahead in the fight (top third, above +0.02): -8.8 (n 36 against 135)
  - already running, fought, behind in the fight (lowest third, -0.01 or less): +1.6 (n 40 against 79)
  - already running, fought, middle third: -1.0 (n 32 against 91)
  - already running, fought, ahead in the fight (top third, above +0.02): -8.5 (n 57 against 135)
  - ran, advanced, behind in the fight (lowest third, -0.01 or less): +1.9 (n 40 against 79)
  - ran, advanced, middle third: +0.8 (n 45 against 91)
  - ran, advanced, ahead in the fight (top third, above +0.02): -4.9 (n 31 against 135)
  - already running, held, behind in the fight (lowest third, -0.01 or less): +3.9 (n 26 against 79)
  - already running, held, middle third: +0.9 (n 40 against 91)
  - already running, held, ahead in the fight (top third, above +0.02): -7.6 (n 19 against 135)
  - held, held, behind in the fight (lowest third, -0.01 or less): +3.1 (n 20 against 79)
  - held, held, middle third: +4.5 (n 38 against 91)
  - held, held, ahead in the fight (top third, above +0.02): -2.1 (n 22 against 135)
  - ran, fought, behind in the fight (lowest third, -0.01 or less): +3.8 (n 23 against 79)
  - ran, fought, middle third: -0.1 (n 25 against 91)
  - ran, fought, ahead in the fight (top third, above +0.02): -3.5 (n 23 against 135)
  - ran, held, behind in the fight (lowest third, -0.01 or less): +9.6 (n 24 against 79)
  - ran, held, middle third: -0.8 (n 30 against 91)
  - ran, held, ahead in the fight (top third, above +0.02): too few yet (n 6 against 135; means -4.8 against 7.2)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - already running, advanced, Corrupted Isle: -2.5 (n 36 against 96)
  - already running, advanced, Imperial Isle: -5.5 (n 25 against 14)
  - already running, advanced, Isle of Jade: +2.4 (n 16 against 43)
  - already running, advanced, Isle of Meditation: -2.5 (n 45 against 44)
  - already running, advanced, Isle of Solitude: +0.1 (n 29 against 22)
  - already running, advanced, Uncharted Isle: -9.3 (n 55 against 54)
  - held, fell back, Corrupted Isle: -2.9 (n 54 against 96)
  - held, fell back, Imperial Isle: -0.6 (n 12 against 14)
  - held, fell back, Isle of Jade: +3.9 (n 32 against 43)
  - held, fell back, Isle of Meditation: -7.8 (n 40 against 44)
  - held, fell back, Isle of Solitude: -3.0 (n 19 against 22)
  - held, fell back, Nomad's Isle: +2.0 (n 12 against 10)
  - held, fell back, Uncharted Isle: -12.2 (n 49 against 54)
  - already running, fell back, Corrupted Isle: -0.9 (n 23 against 96)
  - already running, fell back, Imperial Isle: -4.1 (n 14 against 14)
  - already running, fell back, Isle of Jade: +5.9 (n 11 against 43)
  - already running, fell back, Isle of Meditation: +1.4 (n 19 against 44)
  - already running, fell back, Isle of Solitude: -4.8 (n 22 against 22)
  - already running, fell back, Uncharted Isle: -10.3 (n 71 against 54)
  - held, fought, Corrupted Isle: +0.1 (n 31 against 96)
  - held, fought, Isle of Jade: +7.0 (n 17 against 43)
  - held, fought, Isle of Meditation: -1.7 (n 29 against 44)
  - held, fought, Isle of Solitude: -9.0 (n 14 against 22)
  - held, fought, Nomad's Isle: -1.6 (n 20 against 10)
  - held, fought, Uncharted Isle: -11.0 (n 17 against 54)
  - ran, fell back, Corrupted Isle: -2.1 (n 17 against 96)
  - ran, fell back, Imperial Isle: -6.1 (n 16 against 14)
  - ran, fell back, Isle of Jade: +0.9 (n 13 against 43)
  - ran, fell back, Isle of Meditation: -1.9 (n 12 against 44)
  - ran, fell back, Isle of Solitude: -3.9 (n 16 against 22)
  - ran, fell back, Uncharted Isle: -6.3 (n 40 against 54)
  - already running, fought, Corrupted Isle: -4.0 (n 15 against 96)
  - already running, fought, Imperial Isle: -2.4 (n 15 against 14)
  - already running, fought, Isle of Meditation: -9.5 (n 17 against 44)
  - already running, fought, Isle of Solitude: -2.7 (n 19 against 22)
  - already running, fought, Nomad's Isle: -0.4 (n 20 against 10)
  - already running, fought, Uncharted Isle: -8.4 (n 17 against 54)
  - ran, advanced, Imperial Isle: -4.1 (n 20 against 14)
  - ran, advanced, Isle of Jade: +5.0 (n 24 against 43)
  - ran, advanced, Isle of Meditation: +5.0 (n 11 against 44)
  - ran, advanced, Isle of Solitude: +1.1 (n 11 against 22)
  - ran, advanced, Uncharted Isle: -8.4 (n 33 against 54)
  - already running, held, Isle of Jade: +8.8 (n 14 against 43)
  - already running, held, Isle of Meditation: -6.8 (n 11 against 44)
  - already running, held, Isle of Solitude: +1.0 (n 11 against 22)
  - already running, held, Uncharted Isle: -5.8 (n 17 against 54)
  - held, held, Isle of Jade: +14.0 (n 29 against 43)
  - held, held, Nomad's Isle: +3.9 (n 10 against 10)
  - ran, fought, Imperial Isle: +2.1 (n 18 against 14)
  - ran, held, Isle of Jade: +8.8 (n 21 against 43)
  - ran, held, Uncharted Isle: -12.7 (n 11 against 54)

**late game** (44 decisions, 22 matches; usual: 0 to 1 at the enemy Lord)
- 2 to 3 at the enemy Lord (n 18): +6.1 [-11.2, +17.1]; in the 30 s before: -3.2 [-7.1, +1.9]
- 4+ at the enemy Lord (n 6): -4.0 [-19.7, +6.4]; in the 30 s before: -1.8 [-5.7, +1.9]

**power play** (1160 decisions, 133 matches; usual: pushed, advanced)
- pushed, fought (n 231): +1.0 [-0.5, +2.7]; in the 30 s before: -1.3 [-2.4, -0.1] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, fought (n 137): -0.4 [-2.6, +1.8]; in the 30 s before: -1.0 [-2.0, +0.4]
- pushed, fell back (n 132): +1.0 [-0.7, +2.9]; in the 30 s before: -2.0 [-3.2, -0.8] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, fell back (n 118): -0.8 [-2.4, +1.0]; in the 30 s before: -1.5 [-3.1, -0.0] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, advanced (n 91): +0.2 [-1.2, +1.9]; in the 30 s before: -1.1 [-2.8, +0.6]
- pushed, held (n 42): +1.0 [-1.7, +4.7]; in the 30 s before: -1.4 [-3.3, +0.0]
- held, held (n 41): -0.5 [-2.7, +1.8]; in the 30 s before: +1.6 [+0.2, +3.4] ALREADY DIFFERENT BEFORE: partly who chooses it
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - pushed, fought, behind in the fight (lowest third, +0.00 or less): +2.7 (n 67 against 108)
  - pushed, fought, middle third: -0.5 (n 61 against 129)
  - pushed, fought, ahead in the fight (top third, above +0.07): -0.3 (n 103 against 131)
  - held, fought, behind in the fight (lowest third, +0.00 or less): +0.7 (n 51 against 108)
  - held, fought, middle third: -0.6 (n 43 against 129)
  - held, fought, ahead in the fight (top third, above +0.07): -3.0 (n 43 against 131)
  - pushed, fell back, behind in the fight (lowest third, +0.00 or less): +2.3 (n 40 against 108)
  - pushed, fell back, middle third: -0.1 (n 54 against 129)
  - pushed, fell back, ahead in the fight (top third, above +0.07): -0.2 (n 38 against 131)
  - held, fell back, behind in the fight (lowest third, +0.00 or less): -1.6 (n 57 against 108)
  - held, fell back, middle third: +0.9 (n 42 against 129)
  - held, fell back, ahead in the fight (top third, above +0.07): -2.3 (n 19 against 131)
  - held, advanced, behind in the fight (lowest third, +0.00 or less): +2.3 (n 29 against 108)
  - held, advanced, middle third: -3.7 (n 32 against 129)
  - held, advanced, ahead in the fight (top third, above +0.07): +2.7 (n 30 against 131)
  - pushed, held, behind in the fight (lowest third, +0.00 or less): +0.8 (n 18 against 108)
  - pushed, held, middle third: +1.2 (n 13 against 129)
  - pushed, held, ahead in the fight (top third, above +0.07): +2.2 (n 11 against 131)
  - held, held, behind in the fight (lowest third, +0.00 or less): +2.8 (n 19 against 108)
  - held, held, middle third: -2.6 (n 12 against 129)
  - held, held, ahead in the fight (top third, above +0.07): -6.9 (n 10 against 131)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - pushed, fought, Corrupted Isle: +0.5 (n 29 against 65)
  - pushed, fought, Druid's Isle: +6.6 (n 17 against 18)
  - pushed, fought, Imperial Isle: +5.9 (n 11 against 25)
  - pushed, fought, Isle of Jade: +1.8 (n 30 against 41)
  - pushed, fought, Isle of Meditation: +1.1 (n 49 against 81)
  - pushed, fought, Isle of Solitude: -2.4 (n 28 against 38)
  - pushed, fought, Nomad's Isle: +1.3 (n 23 against 13)
  - pushed, fought, Uncharted Isle: +0.9 (n 30 against 61)
  - held, fought, Corrupted Isle: +1.9 (n 22 against 65)
  - held, fought, Druid's Isle: +1.5 (n 14 against 18)
  - held, fought, Isle of Jade: -3.9 (n 18 against 41)
  - held, fought, Isle of Meditation: +2.2 (n 18 against 81)
  - held, fought, Isle of Solitude: -5.5 (n 19 against 38)
  - held, fought, Nomad's Isle: +1.1 (n 18 against 13)
  - held, fought, Uncharted Isle: -4.7 (n 12 against 61)
  - pushed, fell back, Corrupted Isle: -0.8 (n 15 against 65)
  - pushed, fell back, Imperial Isle: +5.3 (n 10 against 25)
  - pushed, fell back, Isle of Jade: +4.4 (n 13 against 41)
  - pushed, fell back, Isle of Meditation: +3.2 (n 19 against 81)
  - pushed, fell back, Isle of Solitude: +0.4 (n 23 against 38)
  - pushed, fell back, Uncharted Isle: -5.6 (n 24 against 61)
  - held, fell back, Corrupted Isle: -2.9 (n 17 against 65)
  - held, fell back, Imperial Isle: +4.8 (n 10 against 25)
  - held, fell back, Isle of Jade: -2.3 (n 11 against 41)
  - held, fell back, Isle of Meditation: +0.5 (n 22 against 81)
  - held, fell back, Isle of Solitude: -2.9 (n 14 against 38)
  - held, fell back, Nomad's Isle: -1.8 (n 10 against 13)
  - held, fell back, Uncharted Isle: -4.5 (n 20 against 61)
  - held, advanced, Corrupted Isle: -1.2 (n 11 against 65)
  - held, advanced, Imperial Isle: +1.7 (n 13 against 25)
  - held, advanced, Isle of Jade: +0.2 (n 12 against 41)
  - held, advanced, Isle of Meditation: +0.9 (n 22 against 81)
  - held, advanced, Uncharted Isle: -2.7 (n 17 against 61)
  - held, held, Druid's Isle: +1.2 (n 12 against 18)

**split in base** (284 decisions, 87 matches; usual: defended without a collapse)
- collapsed (n 117): -4.1 [-8.0, -1.0] CLEAR; in the 30 s before: +0.9 [-0.6, +2.6]
- missed (n 30): -0.6 [-7.7, +5.0]; in the 30 s before: +0.7 [-1.0, +3.5]
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - collapsed, Corrupted Isle: +1.0 (n 20 against 25)
  - collapsed, Isle of Meditation: -2.8 (n 29 against 17)
  - collapsed, Isle of Solitude: -0.1 (n 14 against 44)
  - collapsed, Uncharted Isle: -7.1 (n 13 against 31)

**Collapses on a split: time away and its cost** (`S32`; per collapse, averages; main = what the main fight lost while the collapsers were away)

| Group | Cases | Away (median s) | Split killed | Collapser died | Own deaths at main | Enemy deaths at main | Flag lead change | DP change | Win change |
|---|---|---|---|---|---|---|---|---|---|
| all | 130 | 22 | 28 | 12 | 0.58 | 0.44 | +1.4 | -4.4 | -2.7 |
| away under 30 s | 76 | 6 | 20 | 1 | 0.01 | 0.16 | +1.6 | +0.7 | -2.4 |
| away 30 to 60 s | 21 | 43 | 3 | 3 | 0.71 | 0.43 | -9.1 | -9.8 | +0.3 |
| away 60 s or more | 33 | 102 | 5 | 8 | 1.82 | 1.09 | +7.5 | -12.6 | -5.3 |
| before 20:00 | 107 | 22 | 20 | 10 | 0.5 | 0.34 | +0.6 | -5.6 | -3.1 |
| from 20:00 | 23 | 18 | 8 | 2 | 0.96 | 0.91 | +5.1 | +1.3 | -0.5 |
| split member killed | 28 | 17.5 | 28 | 1 | 0.07 | 1.29 | +5.5 | +0.4 | +2.9 |
| no kill | 102 | 23.5 | 0 | 11 | 0.73 | 0.21 | +0.3 | -5.7 | -4.2 |

**Leverage: where the choice matters most** (share of the spread in win-chance change explained by the choice beyond the situation; range = best minus worst choice, in points)

- boost clock (504): choice explains 2.3% (situation 3.5%); range 6.2 points, best running, advanced, worst not running, to the spawn
- after wipe (292): choice explains 2.0% (situation 13.2%); range 5.4 points, best pushed the pit, worst took the flag
- late game (44): choice explains 1.4% (situation 63.7%); range 10.1 points, best 2 to 3 at the enemy Lord, worst 4+ at the enemy Lord
- split in base (284): choice explains 1.2% (situation 4.5%); range 3.5 points, best missed, worst collapsed
- enemy pickup (1790): choice explains 0.9% (situation 1.0%); range 5.3 points, best held, held, worst held, fell back
- power play (1160): choice explains 0.4% (situation 1.8%); range 2.0 points, best pushed, held, worst held, fell back

**Behaviour clusters: what teams actually did** (each decision's response grouped by what every player did in the next 20 s; UNNAMED = a group no single named choice covers: a response for Denning to name or reject)

*after wipe* (2 groups, separation 0.31):
- n 176: fought (midline, 2.0 of 8), fought (backline, 1.5 of 8), fought (frontline, 0.9 of 8), held (backline, 0.8 of 8); named as {'pushed the pit': 150, 'reset': 13, 'took the flag': 13}; win change 0.4
- n 116: advanced (midline, 2.6 of 8), advanced (backline, 2.5 of 8), advanced (frontline, 1.2 of 8); named as {'pushed the pit': 69, 'took the flag': 24, 'reset': 23}; win change 2.5 UNNAMED
*boost clock* (4 groups, separation 0.19):
- n 194: fought (midline, 2.2 of 8), fought (backline, 1.9 of 8), fought (frontline, 0.9 of 8); named as {'not running, fought': 77, 'running, fought': 33, 'not running, fell back': 25}; win change -1.0 UNNAMED
- n 118: held (backline, 1.7 of 8), held (midline, 1.0 of 8), fought (frontline, 0.7 of 8), fought (midline, 0.6 of 8); named as {'not running, held': 31, 'not running, fell back': 22, 'not running, fought': 17}; win change -1.0 UNNAMED
- n 116: advanced (midline, 2.2 of 8), advanced (backline, 1.8 of 8), advanced (frontline, 0.6 of 8), fought (midline, 0.5 of 8); named as {'running, advanced': 39, 'not running, advanced': 37, 'not running, fell back': 8}; win change -0.8 UNNAMED
- n 78: fell back (midline, 2.2 of 8), fell back (backline, 1.9 of 8), fell back (frontline, 0.6 of 8), fought (midline, 0.5 of 8); named as {'not running, fell back': 27, 'running, fell back': 13, 'not running, fought': 12}; win change -4.4 UNNAMED
*enemy pickup* (3 groups, separation 0.21):
- n 773: fought (midline, 1.9 of 8), fought (backline, 1.5 of 8), fought (frontline, 1.0 of 8), held (backline, 0.9 of 8); named as {'held, fought': 116, 'already running, fought': 104, 'held, advanced': 93}; win change -0.4 UNNAMED
- n 578: advanced (midline, 2.2 of 8), advanced (backline, 2.0 of 8), advanced (frontline, 0.9 of 8); named as {'held, advanced': 181, 'already running, advanced': 145, 'ran, advanced': 78}; win change 2.5 UNNAMED
- n 445: fell back (midline, 1.9 of 8), fell back (backline, 1.8 of 8), fell back (frontline, 0.7 of 8); named as {'held, fell back': 123, 'already running, fell back': 90, 'ran, fell back': 83}; win change -1.0 UNNAMED
*late game* (5 groups, separation 0.22):
- n 15: advanced (midline, 1.5 of 8), held (backline, 1.1 of 8), advanced (backline, 0.9 of 8), fought (backline, 0.7 of 8); named as {'2 to 3 at the enemy Lord': 9, '0 to 1 at the enemy Lord': 6}; win change -8.4
- n 13: fought (midline, 2.3 of 8), fought (backline, 1.5 of 8), fought (frontline, 0.9 of 8), advanced (backline, 0.7 of 8); named as {'0 to 1 at the enemy Lord': 6, '4+ at the enemy Lord': 4, '2 to 3 at the enemy Lord': 3}; win change 8.9 UNNAMED
- n 11: fell back (backline, 2.3 of 8), fell back (midline, 1.7 of 8), fell back (frontline, 1.1 of 8), advanced (backline, 0.7 of 8); named as {'0 to 1 at the enemy Lord': 7, '2 to 3 at the enemy Lord': 4}; win change -0.2
- n 3: advanced (midline, 5.3 of 8), advanced (backline, 1.0 of 8), fell back (backline, 0.7 of 8); named as {'4+ at the enemy Lord': 2, '2 to 3 at the enemy Lord': 1}; win change 0.1
- n 2: died (backline, 4.0 of 8), died (frontline, 2.0 of 8), died (midline, 2.0 of 8); named as {'2 to 3 at the enemy Lord': 1, '0 to 1 at the enemy Lord': 1}; win change -1.9 UNNAMED
*power play* (2 groups, separation 0.27):
- n 768: fought (midline, 1.9 of 8), fought (backline, 1.4 of 8), fought (frontline, 1.0 of 8), held (backline, 0.7 of 8); named as {'pushed, fought': 179, 'held, fought': 130, 'held, fell back': 111}; win change 1.3 UNNAMED
- n 394: advanced (midline, 2.3 of 8), advanced (backline, 2.3 of 8), advanced (frontline, 1.1 of 8); named as {'pushed, advanced': 258, 'pushed, fought': 52, 'held, advanced': 29}; win change 2.3
*split in base* (3 groups, separation 0.19):
- n 124: fought (midline, 2.4 of 8), fought (backline, 1.4 of 8), fought (frontline, 0.9 of 8), held (backline, 0.7 of 8); named as {'defended without a collapse': 70, 'collapsed': 40, 'missed': 14}; win change 0.8 UNNAMED
- n 81: advanced (midline, 2.0 of 8), advanced (backline, 1.3 of 8), advanced (frontline, 0.6 of 8), fell back (backline, 0.5 of 8); named as {'collapsed': 37, 'defended without a collapse': 37, 'missed': 7}; win change -2.1 UNNAMED
- n 78: fell back (midline, 2.3 of 8), fell back (backline, 1.7 of 8), fell back (frontline, 0.7 of 8), fought (backline, 0.6 of 8); named as {'collapsed': 40, 'defended without a collapse': 29, 'missed': 9}; win change -3.6 UNNAMED

## 8. What results and causes are worth

Win points for the team it happened to, from 133 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. Both against matched moments without the event (same minute and win chance). A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 396 | +5.2 | +1.1 to +9.1 | +2.9 | yes |
| capture | 1150 | +1.5 | +1.0 to +2.0 | +1.5 | yes |
| death (any) | 2596 | -8.9 | -10.4 to -7.3 | -5.8 | yes |
| death: against a spike build | 820 | -8.0 | -11.4 to -4.2 | -4.2 | yes |
| death: against other builds | 1776 | -9.2 | -11.4 to -7.2 | -6.5 | yes |
| death: back within 20 s | 438 | -8.5 | -11.7 to -5.1 | -4.4 | yes |
| death: down 20 to 60 s | 946 | -9.5 | -12.0 to -7.1 | -5.3 | yes |
| death: down 60 s or more | 1212 | -8.5 | -10.2 to -6.8 | -6.6 | yes |
| death: healer | 875 | -9.5 | -11.7 to -7.2 | -6.3 | yes |
| death: healer in own base or pit, back within 15 s (likely deliberate) | 54 | -7.2 | -13.1 to -1.6 | -2.4 | yes |
| death: healer, other | 821 | -9.7 | -12.0 to -7.5 | -6.6 | yes |
| death: not a healer | 1721 | -8.5 | -10.1 to -6.9 | -5.5 | yes |
| footman lost (base NPC) | 390 | +0.7 | -1.7 to +3.2 | +0.6 | no |
| pit NPC lost (any): taken by a spike build | 255 | -4.8 | -8.1 to -1.5 | -1.9 | yes |
| pit NPC lost (any): taken by other builds | 799 | -5.8 | -8.1 to -3.4 | -2.6 | yes |
| pit NPC lost: archer | 603 | -3.2 | -5.0 to -1.2 | -0.6 | yes |
| pit NPC lost: bodyguard | 143 | -8.3 | -10.9 to -5.6 | -3.7 | yes |
| pit NPC lost: knight | 308 | -9.0 | -11.4 to -6.5 | -5.6 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value. Context (strength, build skill counts, flag lead, morale, the clock) is left out: it describes the situation, it is not a cause to fix.

*deaths* (per 10 s in that state; result worth -8.9 points, base rate 1.5%):

- enemies within 1,500 7.5 to 8: result chance +3.1 points, worth -0.27 win points
- current health % 1 to 48.5: result chance +10.9 points, worth -0.97 win points
- allies within 1,500 0 to 0.5: result chance +1.9 points, worth -0.17 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.5 points, worth -0.22 win points

*kill conversion* (per burst, for the attacking team; result worth +8.9 points, base rate 29.6%):

- damage in the 2 s burst 506.5 to 839: result chance +25.7 points, worth +2.28 win points
- target's healers in range 0 to 0.5: result chance +29.7 points, worth +2.64 win points
- target health % when the burst started 0 to 39.5: result chance +24.0 points, worth +2.13 win points
- target's health ceiling 0.4 to 0.69: result chance +29.8 points, worth +2.66 win points
- a prot on the target 0.5 to 1: result chance -5.1 points, worth -0.45 win points

*npc loss* (per case, for the defending team; result worth -5.6 points, base rate 19.5%):

- damage on the pit NPCs in the last 5 s 398.5 to 1370: result chance +39.3 points, worth -2.2 win points
- own players in the pit 0 to 0.5: result chance +35.9 points, worth -2.01 win points
- own players alive outside the pit 0 to 0.5: result chance +18.3 points, worth -1.02 win points
- of which healers 0 to 0.5: result chance +17.5 points, worth -0.98 win points
- attackers' measured damage per second against a Lord (benchmarks) 1.9 to 12.25: result chance -9.8 points, worth +0.55 win points
- enemy players in the pit 7.5 to 8: result chance +7.6 points, worth -0.42 win points
- share of the attacking team's live players in the pit (OG comms: merge before pushing the pit) 0.94 to 1: result chance +5.7 points, worth -0.32 win points

## The TQs

Denning's four questions, each from the batch's matches. The why comes from forensics and events (every number placed against the same role or situation in every stored match); the different play comes only from measurement: the usual play's choice effects (usual.py), node models read again with the variable changed (models that never saw the match, changes priced in win points with values.py), options that were ready and unused, and benchmarks. Points = win-chance points.

## TQ 1. Behind on flags

*The biggest flag swing in the new matches: Apes +80 -> -78 by 4:30.0.*

### Flag swing: Apes v Fun (d9d75e55), 1:45.0 to 4:30.0
**Result**: Apes's flag lead +80 s -> -78 s (-158 s). Stand: Apes -> Fun.
**Captures** (flag model: fastest possible answer after the enemy's capture):
- Fun capped 1:15.0 by 8 Monk, 43 s after Apes's capture; fastest possible 83 s, so -40 s slower
- Apes capped 1:44.0 by AoB Derv, 29 s after Fun's capture; fastest possible 30 s, so -1 s slower; enemies in the way {'Air Ele 3': 2, '8 Monk': 2, 'Fire Ele 1': 1}
- Fun capped 3:39.0 by 8 Monk, 115 s after Apes's capture; fastest possible 76 s, so 39 s slower; enemies in the way {'Warrior': 8, 'AoB Derv': 6}
- Fun: Apes held 115 s; Fun capped 5 s before a boost, so was down on flags
**Runs** (each run: outcome, and what was done to the runner):
- Apes AoB Derv 1:18.0 to 1:44.0 (26 s): captured, lowest health 100%, escort ['Warrior', 'Necromancer', 'Mesmer', '7 Monk'], pushed by nobody
- Apes Necromancer 2:33.0 to 2:37.0 (4 s): dropped, lowest health 100%, escort ['Ritualist', 'Prot', '8 Monk'], pushed by nobody
- Apes Necromancer 3:07.0 to 3:11.0 (4 s): dropped, lowest health 100%, escort ['AoB Derv', 'Warrior', 'Ritualist', 'Mesmer', 'Prot', '8 Monk'], pushed by nobody
- Fun 8 Monk 3:03.0 to 3:39.0 (35 s): captured, lowest health 54%, escort none, pushed by nobody
**Deaths in the window**: 1:54.0 Apes Necromancer (stand, [7, 8]); 2:02.0 Apes Warrior (backside, [6, 8]); 2:56.0 Apes 7 Monk (push side, [8, 7]); 3:10.0 Apes AoB Derv (stand, [7, 7]); 3:32.0 Apes Necromancer (stand, [4, 7]); 3:38.0 Apes Warrior (stand, [4, 8])
- Apes output in the 20 s before 1:54.0: 2.4 damage per second (below the 10th percentile for team (median 38.4, n 9019)), top target share 0.6, spikes 0
- Fun output in the 20 s before 1:54.0: 45.2 damage per second (above the 50th percentile for team (median 38.4, n 9019)), top target share 1.0, spikes 1
**Why Apes Necromancer died at 1:54.0** (forensics):
  - Position: no (in the last 3 s: nearest allied healer 713, nearest enemy 701, allies in casting range 5.5, enemies 7.0; over the whole window the nearest enemy's median was 1648)
  - Prots: no prots (0 from teammates, 0 self; 0 of 0 landed); damage 951 (0% attacks, 0% armor-ignoring), burst 582 in 2 s at 1:50.8; ready and in range but not used: Apes Prot Guardian, Apes Prot Shielding Hands
  - Healers under interrupt pressure: usual (healers 3, interrupts_per_min 0.0, interrupted 0, casts 5, finished_share 0.8, dazed 0, knockdowns 0, hexes 0)
  - Damage off shield sets: no (team share 0.0, a shield would have stopped about 0)
  - Own damage: no (2.4 per second on [('Fun Water Ele', 28), ('Fun 7 Monk', 19)]); enemy damage: usual (47.5 per second)
  - Peel: usual (1 of 6 attackers controlled; longest free 20.0 s)
  - Casting: unclear (casts 3, interrupted 1, cancelled 0, while_dazed 0)
**Why Apes Warrior died at 2:02.0** (forensics):
  - Position: yes (in the last 3 s: nearest allied healer 1641, nearest enemy 116, allies in casting range 0.0, enemies 8.0; over the whole window the nearest enemy's median was 224)
  - Prots: no prots (0 from teammates, 0 self; 0 of 0 landed); damage 396 (0% attacks, 0% armor-ignoring), burst 346 in 2 s at 1:59.8
  - Healers under interrupt pressure: usual (healers 3, interrupts_per_min 0.0, interrupted 0, casts 8, finished_share 0.88, dazed 0, knockdowns 0, hexes 0)
  - Damage off shield sets: no (team share 0.0, a shield would have stopped about 0)
  - Own damage: no (15.6 per second on [('Fun Air Ele 2', 202), ('Fun Fire Ele 2', 47)]); enemy damage: high (67.3 per second)
  - Peel: partly (controlled, but an attacker was left free for 20.0 s) (2 of 6 attackers controlled; longest free 20.0 s)
  - Casting: unclear (casts 3, interrupted 0, cancelled 0, while_dazed 0)
**After**: 5:16.0 Apes Prot; 5:29.0 Apes 7 Monk
**Why, in short**: Apes's Necromancer dropped the flag at 3:11 after 4 s of carrying, 23 s from capturing (main 6v7, alive 6v8); Fun capped at 3:39, 115 s after Apes's capture, on its 1st run (0 dropped); Apes pushed the last carrier with nobody but its health never went below 54%; Apes's answer was 36 s slower than possible; deaths in the window: Apes 6.

**How it got there** (the chain of game states, earliest first; traced back to 4:15, the last reset or 3 minutes before; win = the held-out win model's change over each link):
1. 4:15: **Apes already behind on flags at 4:15** (win -2.8 points) (the result)
   - flag lead -8 s since the start of the window

**Where a fix would have mattered most** (measured, in win points):
- no alternative along the chain could be priced from the data yet

**A different play (measured)**

*The decisions in the swing* (usual.py: win-chance points over the decision's window, against the kind's most common choice):
- enemy pickup at 2:18 (main 7v7, flags +46 s, boost in 87, fight state -0.025): chose **ran, advanced** (-1.4 [-5.7, +3.4] against the most common choice, held, advanced); in the 15 most similar decisions teams usually chose **held, advanced**; measured better: **held, held** (+3.2 points against the choice made, not clear yet, n 80). In the same fight-state third (behind in the fight (lowest third, -0.01 or less)) this choice did +1.9 against the usual choice (n 40 against 79, raw).
- enemy pickup at 2:20 (main 7v7, flags +80 s, boost in 84, fight state 0.008): chose **ran, advanced** (-1.4 [-5.7, +3.4] against the most common choice, held, advanced); in the 15 most similar decisions teams usually chose **held, advanced**; measured better: **held, held** (+3.2 points against the choice made, not clear yet, n 80). In the same fight-state third (middle third) this choice did +0.8 against the usual choice (n 45 against 91, raw).
- enemy pickup at 2:33 (main 8v6, flags +80 s, boost in 71, fight state 0.03): chose **already running, advanced** (-1.5 [-4.9, +2.3] against the most common choice, held, advanced); in the 15 most similar decisions teams usually chose **held, advanced**; measured better: **held, held** (+3.3 points against the choice made, not clear yet, n 80). In the same fight-state third (ahead in the fight (top third, above +0.02)) this choice did -5.1 against the usual choice (n 72 against 135, raw).
*The answers to the enemy's captures* (flag-answer node: seconds slower than possible; typical error 16.7 s against 27.8 s for the median on unseen matches):
- answer at 1:15 by the AoB Derv: -1 s slower than possible (model reads 5.7 s); with a runner waiting at the spawn: 2.9 s (-2.8 s); no enemies on the way back: 4.4 s (-1.3 s)
- answer at 3:39 by the AoB Derv: 36 s slower than possible (model reads 41.9 s); with a runner waiting at the spawn: 50.8 s (+8.9 s); the runner alive at the enemy's capture: 20.1 s (-21.8 s); no own deaths during the answer: 31.2 s (-10.7 s); no enemies on the way back: 33.0 s (-8.9 s)
- Those 22 s, read by the win model as flag lead at 4:30: Apes 6.6% -> 6.6% (+0.0 points)

**Confidence**: medium (one measurement supports it).

## TQ 2. A monk death

*The monk death that cost the most win chance in the new matches: NwAy v Men (862d6629), Men 8 Monk at 27:00 (backside, numbers [3, 5]); win chance -51.8 points from 10 s before to 30 s after.*

**Why** (forensics, against the same role in every stored match):
- Position: yes (in the last 3 s: nearest allied healer 10461, nearest enemy 83, allies in casting range 1.0, enemies 3.0; over the whole window the nearest enemy's median was 113)
- Prots: yes (0 from teammates, 4 self; 3 of 4 landed); damage 681 (86% attacks, 12% armor-ignoring), burst 228 in 2 s at 26:57.3; knockdowns 1, knockdown immunity up for 0
- Healers under interrupt pressure: usual (healers 3, interrupts_per_min 3.0, interrupted 1, casts 10, finished_share 0.8, dazed 0, knockdowns 1, hexes 0)
- Damage off shield sets: yes (team share 0.66, a shield would have stopped about 73)
- Own damage: no (9.8 per second on [('NwAy Hammer', 128), ('NwAy 7 Monk', 68)]); enemy damage: high (70.5 per second)
- Peel: no (peel on a burst is rare: most bursts on this role get none) (0 of 3 attackers controlled; longest free 20.0 s)
- Casting: interrupted far more than usual; cancelled more than usual (casts 8, interrupted 1, cancelled 1, while_dazed 0)
**Why, in short**: the 8 Monk died because knocked down 1 times with no knockdown immunity up, its casts were interrupted (1 of 8), the enemy hit unusually hard (70.5 per second), its own team's damage was low (9.8 per second). How the game got there: Men fell behind on flags (26:55) -> deaths: 2 of Men died 26:57 to 27:00 (27:00).

**How it got there** (the chain of game states, earliest first; traced back to 24:00, the last reset or 3 minutes before; win = the held-out win model's change over each link):
1. 25:10: **Men fell behind on flags** (win +4.9 points) -> led to step 2
   - flag lead +29 s at 25:10 -> -15 s at 25:15
   - NwAy capped at 25:16
2. 26:47: **deaths: 2 of Men died 26:57 to 27:00** (win -39.7 points) (the result)
   - 26:57 Hammer died (enemy pit, numbers [6, 5]): no prot landed in time (0 of 0 landed); knocked down 1 times with no knockdown immunity up; its own team's damage was low (8.8 per second); position (no allied healer within casting range, nearest enemy 721 in the last 3 s)
   - 27:00 8 Monk died (backside, numbers [3, 5]): knocked down 1 times with no knockdown immunity up; its casts were interrupted (1 of 8); the enemy hit unusually hard (70.5 per second); its own team's damage was low (9.8 per second)
   - Mesmer in the 20 s before: 100% of its interrupts and casts on the enemy midline or frontline (interrupts {'mid/front': 1}, casts on enemies {'mid/front': 2}; typical before an own healer death: 86%, 579 cases)
   - when the fight started: main 6v5, alive 8v8, flag lead -72 s, stand NwAy

**Where a fix would have mattered most** (measured, in win points):
- step 2: boost clock at 26:46 (main 3v5): running, advanced instead of not running, advanced: about +3.5 win points (usual.py: measured choice effect against the choice made, partly who chooses it; not clear yet)
- step 2: another healer in range of the 8 Monk: about +2.8 win points (deaths node: risk 15.7% -> 10.2% of dying in the next 10 s, times this death's cost (-51.8 points); clear)

**How it could have been prevented (measured)**

- Further back: the fixes along the chain are priced above ("Where a fix would have mattered most"). The readings below are what was still possible in the last seconds.
- Attackers left free (no snare, Blind, Weakness, interrupt, knockdown or hex from its team): NwAy AoB Derv 20.0 s free (nearest own non-healer 281); NwAy 7 Monk 15.4 s free (nearest own non-healer 755); NwAy Hammer 8.4 s free (nearest own non-healer 373)
- Deaths node at 26:55 (AUC 0.921 on unseen matches against 0.79 for health_pct and damage_taken_3s alone): risk 15.7% of dying in the next 10 s; read again with
  - another healer in range: 10.2% (-5.5 points of risk; at this death's measured cost of -51.8 win points, about +2.8 expected; at a typical healer death's -9.5, +0.5)
  - the Cripple removed: 9.8% (-5.9 points of risk; at this death's measured cost of -51.8 win points, about +3.1 expected; at a typical healer death's -9.5, +0.6)
  - knockdown immunity (no knockdowns): 9.4% (-6.3 points of risk; at this death's measured cost of -51.8 win points, about +3.3 expected; at a typical healer death's -9.5, +0.6)
  - staying with its group: 16.0% (+0.3 points of risk; at this death's measured cost of -51.8 win points, about -0.2 expected; at a typical healer death's -9.5, -0.0)
  - one attacker peeled off: 13.2% (-2.5 points of risk; at this death's measured cost of -51.8 win points, about +1.3 expected; at a typical healer death's -9.5, +0.2)
  - all of these together: 3.0% (-12.7 points of risk; at this death's measured cost of -51.8 win points, about +6.6 expected; at a typical healer death's -9.5, +1.2)

**Confidence**: medium (one measurement supports it).

## TQ 3. A power play without a kill

*The power play without a kill that cost the most win chance in the new matches: main 6v4, pushed, no kill in 109 s; win chance -12.2 points over it.*

### Power play without a kill: BcS v Team (92b0a4af), 9:28.0 to 11:17.0
**Situation**: main 6v4, alive 8v8, flags even (-9 s), DP -90, boost in 98; choice pushed (advanced 5, fought 3); deaths {'BcS': 5, 'Team': 0} in 109 s
**The fight's shape** (every 5 s: own main, the enemy group it faced, distance between them, that group's distance to the rest of its team): 9:28.0 6v4 1290 apart, 1348 from its others; 9:33.0 6v4 947 apart, 2003 from its others; 9:38.0 5v4 855 apart, 3198 from its others; 9:43.0 5v4 557 apart, 4344 from its others; 9:48.0 5v4 602 apart, 5440 from its others; 9:53.0 5v4 686 apart, 5808 from its others; 9:58.0 6v4 898 apart, 5352 from its others; 10:03.0 6v4 272 apart, 6224 from its others; 10:08.0 6v4 416 apart, 7453 from its others; 10:13.0 6v4 265 apart, 7258 from its others; 10:18.0 6v4 325 apart, 7348 from its others; 10:23.0 6v4 430 apart, 6107 from its others; 10:28.0 6v4 416 apart, 5519 from its others; 10:33.0 6v4 596 apart, 4938 from its others; 10:38.0 6v4 418 apart, 2923 from its others; 10:43.0 6v5 284 apart, 13028 from its others; 10:48.0 6v5 108 apart, 13458 from its others; 10:53.0 6v5 108 apart, 13971 from its others; 10:58.0 5v5 140 apart, 13664 from its others; 11:03.0 5v5 76 apart, 13918 from its others; 11:08.0 5v4 304 apart, 2115 from its others; 11:13.0 5v4 73 apart, 3248 from its others
**BcS's damage**: 32.8 per second (below the 50th percentile for team (median 38.4, n 9019)); top target share 0.35 (below the 20th percentile for team (median 0.48, n 9019)); targets [('Team Mes/A', 1259), ('Team 7 Monk', 871), ('Team Prot', 707), ('Team AoB Derv', 456)]; dealers [('BcS Fire Ele', 1252), ('BcS Necromancer 2', 1096), ('BcS Stand Mes', 826), ('BcS Ritualist', 254), ('BcS Necromancer 1', 139)]
- phase 9:08.0 to 9:41.0: 6v5 (push side, job convert), damage uptime 0.33, damage-seconds lost {'moving': 102, 'idle': 9}
- phase 9:41.0 to 9:49.0: 5v4 (enemy pit, job convert), damage uptime 0.53, damage-seconds lost {'moving': 13, 'idle': 2}
- phase 9:49.0 to 9:52.0: 5v4 (enemy pit, job convert), damage uptime 0.67, damage-seconds lost {'idle': 2, 'moving': 2}
- phase 9:52.0 to 9:59.0: 6v4 (enemy pit, job convert), damage uptime 0.29, damage-seconds lost {'moving': 21, 'idle': 3, 'knocked down': 1}
- phase 9:59.0 to 10:17.0: 6v4 (enemy pit, job convert), damage uptime 0.51, damage-seconds lost {'moving': 38, 'idle': 5, 'knocked down': 1}
- phase 10:17.0 to 10:25.0: 6v4 (enemy pit, job convert), damage uptime 0.53, damage-seconds lost {'moving': 13, 'idle': 6}
- phase 10:25.0 to 10:35.0: 6v4 (enemy pit, job convert), damage uptime 0.48, damage-seconds lost {'moving': 18, 'idle': 8}
- phase 10:35.0 to 10:46.0: 6v5 (enemy pit, job convert), damage uptime 0.4, damage-seconds lost {'moving': 20, 'idle': 13}
- phase 10:46.0 to 10:49.0: 6v5 (enemy pit, job convert), damage uptime 0.73, damage-seconds lost {'moving': 3, 'idle': 1}
- phase 10:49.0 to 10:58.0: 6v5 (enemy pit, job convert), damage uptime 0.6, damage-seconds lost {'moving': 15, 'idle': 3}
- phase 10:58.0 to 11:17.0: 6v5 (enemy pit, job convert), damage uptime 0.55, damage-seconds lost {'moving': 41, 'idle': 2}
- phase 11:17.0 to 11:20.0: 3v4 (enemy pit, job fight in the enemy pit), damage uptime 0.56, damage-seconds lost {'moving': 3, 'idle': 1}
**Team's answer**: healing 142 per second ({'Team Ritualist': 5485.599999999998, 'Team 7 Monk': 4613, 'Team 8 Monk': 2821, 'Team Prot': 1864}); prots {'Shielding Hands': 6, 'Reversal of Fortune': 7, 'Shield Guardian PvP': 1}
- BcS's knockdowns landed 0; Team's knockdown immunity casts 0
- Pressure on Team's healers: healers 3, interrupts_per_min 1.7, interrupted 3, casts 84, finished_share 0.95, dazed 0, knockdowns 0, hexes 19 (above the 50th percentile for team (median 0, n 10272))
- Snares, Blind and Weakness BcS put on Team: none
**Where the power play came from** (why the enemy was short, player-seconds over it): enemy pit 71, enemy base 19, running flag 17
**Why, in short**: BcS had 6v4 at main for 109 s; Team healed 142 per second; worse than in power plays that killed: damage 32.8 per second (killing 45.3, not killing 35.8); not the cause (on the side of power plays that killed): damage uptime in contact 49% (killing 50%, not killing 39%; most lost to moving), top-target share 0.35 over 4 targets (killing 0.37, not killing 0.41).

**How it could have been converted (measured)**

- Against every stored power play (2 up): those that killed had a median 45.3 damage per second and top-target share 0.37 (69 cases); those that didn't, 35.8 and 0.41 (139 cases). BcS here: 32.8 and 0.35. Damage uptime: 50% in those that killed, 39% in those that didn't, 49% here.
- No burst (a 2 s burst that the kill-conversion node reads) in the window: the damage never came together on one target.
- The choice at the power play (usual.py):
  - power play at 9:28 (main 6v4, flags -9 s, boost in 98, fight state 0.15): chose **pushed, advanced** (+0.0 [+0.0, +0.0] against the most common choice, pushed, advanced); in the 15 most similar decisions teams usually chose **pushed, advanced**; no choice of this kind did measurably better than the one made.

**Confidence**: low (the engine can't price an alternative here yet).

## TQ 4. Pit NPCs lost

*The NPC loss that cost the most win chance in the new matches: cope lost knight (hold split Prot+8 Monk+Monk 5 (WoC)) at 15:52; win chance -39.8 points from 20 s before to 20 s after.*

### Pit NPCs lost: cope v hold (3b9c897a) around 15:52.0
**Lost**: 15:23.0 archer (outside) (converted from the fight at 14:29 (wipe)); 15:52.0 knight (hold split Prot+8 Monk+Monk 5 (WoC)); 16:08.0 knight (push)
**hold's split** 15:23.0 to 15:53.0: ['Prot', '8 Monk', 'Monk 5 (WoC)'] (split), entered base no, NPC damage {'knight': 36}, NPC kills [{'npc': 'knight', 't': 952, 'defenders_present': ['Hammer', '8 Monk', 'Mesmer', 'Monk 3 (WoC)']}]
- defender Hammer: first 15:43.0 (latency 20 s, from field), 11 s defending
- defender 8 Monk: first 15:44.0 (latency 21 s, collapse from main), 10 s defending
- defender Mesmer: first 15:47.0 (latency 24 s, collapse from main), 6 s defending
- defender Monk 3 (WoC): first 15:49.0 (latency 26 s, already in base), 5 s defending
- main numbers meanwhile [5.4, 2.9]
**cope at 15:52.0**: Warrior: dead; Hammer: own base (hold); Monk 3 (WoC): own base (hold); Monk 4 (WoC): dead; Mesmer: own base (hold); Prot: dead; 7 Monk: dead; 8 Monk: own base (hold)
- hold output 15:23.0 to 15:53.0: 2.7 per second
- cope output 15:23.0 to 15:53.0: 1.1 per second
**Why, in short**: hold split Prot+8 Monk+Monk 5 (WoC) into cope's base; at 15:47 the pit had 2 attackers against 4 defenders (1 of them healers), with 0 of cope elsewhere; defenders present at the kill: Hammer, 8 Monk, Mesmer, Monk 3 (WoC); 4 of cope were dead at the time (Monk 4 (WoC) 14:44, Warrior 14:55, 7 Monk 15:13, Prot 15:16); the Monk 4 (WoC) died at 14:44 (push side, numbers [4, 5]) because knocked down 1 times with no knockdown immunity up, the enemy hit unusually hard (113.2 per second), its healers were under interrupt pressure; the Warrior died at 14:55 (backside, numbers [3, 5]) because no prot landed in time (0 of 0 landed; Prot Shielding Hands, Prot Guardian ready and unused), knocked down 2 times with no knockdown immunity up, the enemy hit unusually hard (121.6 per second); how the game got there: cope already behind on flags at 12:55 (14:42) -> deaths: 2 of cope died 14:44 to 14:55 (14:44) -> cope lost knight (15:52).

**How it got there** (the chain of game states, earliest first; traced back to 12:52, the last reset or 3 minutes before; win = the held-out win model's change over each link):
1. 12:55: **cope already behind on flags at 12:55** (win +29.1 points) -> led to step 2
   - flag lead -71 s since the start of the window
2. 14:34: **deaths: 2 of cope died 14:44 to 14:55** (win -14.0 points) -> led to step 3
   - 14:44 Monk 4 (WoC) died (push side, numbers [4, 5]): knocked down 1 times with no knockdown immunity up; the enemy hit unusually hard (113.2 per second); its healers were under interrupt pressure; position (in contact with the enemy, nearest enemy 99 in the last 3 s)
   - 14:55 Warrior died (backside, numbers [3, 5]): no prot landed in time (0 of 0 landed; Prot Shielding Hands, Prot Guardian ready and unused); knocked down 2 times with no knockdown immunity up; the enemy hit unusually hard (121.6 per second); its own team's damage was low (17.7 per second)
   - Mesmer in the 20 s before: 0% of its interrupts and casts on the enemy midline or frontline (interrupts {'healer': 2}, casts on enemies {'healer': 4}; typical before an own healer death: 86%, 579 cases)
   - when the fight started: main 4v5, alive 8v8, flag lead -71 s, stand hold
3. 15:32: **cope lost knight** (win -39.8 points) (the result)
   - pit at 15:50: 1 attackers against 4 defenders (1 healers)
   - 4 of cope dead (Monk 4 (WoC) 14:44, Warrior 14:55, 7 Monk 15:13, Prot 15:16)

**Where a fix would have mattered most** (measured, in win points):
- step 2: Aura of Stability (or other knockdown immunity) on the Monk 4 (WoC): cope Prot Aura of Stability, cope Prot Balanced Stance had it ready: about +0.6 win points (deaths node: risk 11.1% -> 6.5% of dying in the next 10 s, times this death's cost (-14.1 points); not clear yet)

**How it could have been prevented (measured)**

- Further back: with 4 of cope dead, more defenders were not available; the fixes along the chain are priced above.
- First defender: 20 s after it entered the base; every stored split into a base: median 8 s before it entered the base, quickest fifth 34 s before it entered the base or sooner (350 splits). Denning: about 15 s is on time, 60 s is late.
- NPC-loss node at 15:47 (AUC 0.844 on unseen matches against 0.752 for attackers and defenders alone): 2 attackers (0 healers) against 4 defenders (1 healer), 0 of cope elsewhere; read 27.5% to lose an NPC; read again with
  - one more defender: 31.1% (+3.6 points; at this loss's measured cost of -39.8 win points, about -1.4 expected; at a typical NPC loss's -5.6, -0.2)
  - one more defender, a healer: 28.2% (+0.7 points; at this loss's measured cost of -39.8 win points, about -0.3 expected; at a typical NPC loss's -5.6, -0.0)
  - two more defenders: 34.3% (+6.8 points; at this loss's measured cost of -39.8 win points, about -2.7 expected; at a typical NPC loss's -5.6, -0.4)

**Confidence**: low (measured, but the ranges include no effect yet).

## 9. Detailed learnings snapshot

Descriptive measurements across all 133 trained matches (the latest batch, 20 matches, in brackets where it differs). Not causal on their own: they point to questions and candidate variables.

**Runners** (spawn to capture; pushed = an enemy hit the carrier):

| Runner | Runs | Captured | Median s to capture | Dropped | Pushed | Runs by eventual winners (includes who was ahead) |
|---|---|---|---|---|---|---|
| Mes/A | 253 | 51% | 41.0 (45.5) | 114 | 46% | 46% |
| Ritualist | 230 | 46% | 38 (37) | 116 | 37% | 57% |
| AoB Derv | 220 | 54% | 30.5 (27) | 99 | 37% | 53% |
| Mesmer | 209 | 55% | 36.0 (45) | 89 | 45% | 58% |
| Dervish | 145 | 64% | 28 (28.5) | 49 | 46% | 34% |
| Hammer | 142 | 46% | 26.0 (27) | 75 | 34% | 54% |
| 8 Monk | 118 | 33% | 29 (33.0) | 78 | 20% | 59% |
| Monk 4 (WoC) | 117 | 60% | 36.0 (35) | 46 | 47% | 56% |
| Necromancer | 93 | 66% | 31 (36) | 30 | 38% | 41% |
| Warrior | 77 | 39% | 30.5 (38) | 45 | 36% | 36% |

Double running: single 1705 runs (49% by eventual winners, includes who was ahead); half 522 runs (52% by eventual winners, includes who was ahead).
Winners against losers below are compared at moments when a win model that never saw the match gave the team 35 to 65% (so the gap is not just who was already ahead), with every moment beside it, labelled.


**Flag answers** (answering the enemy's capture): winners at even win chance: 134 answers, median 40.5 s, 4.5 s slower than possible, 27 answers 30 s+ slower; losers at even win chance: 134 answers, median 52.0 s, 7.5 s slower than possible, 41 answers 30 s+ slower; winners every moment (includes who was ahead): 526 answers, median 41.0 s, 4.0 s slower than possible, 123 answers 30 s+ slower; losers every moment (includes who was ahead): 493 answers, median 54 s, 11 s slower than possible, 170 answers 30 s+ slower.

**Skills: kill participation** (share of casts at an enemy who died within 5 s; 15+ casts):

- Highest: Deep Freeze 50% of 22; Vapor Blade 31% of 150; Chest Thumper 27% of 464; Disrupting Throw 27% of 82; Wounding Strike PvP 27% of 63; Invoke Lightning 25% of 1698; Twisting Fangs 25% of 107; Shadow Shroud PvP 24% of 121; Shatter Storm 23% of 254; Decapitate 23% of 537; Leaping Mantis Sting 23% of 160; Falling Lotus Strike 22% of 120
- Lowest: Images of Remorse 0% of 20; Ether Feast 0% of 16; Flare 0% of 41; Crippling Slash 0% of 23; Arcane Languor 0% of 89; Soothing Images 0% of 32; Ether Phantom 0% of 16; Hidden Caltrops 0% of 35

**Interrupts:** skills interrupted most (whose): Healing Burst on the 7 Monk 371; Guardian on the Prot 260; Guardian on the 8 Monk 244; Blessed Light on the 8 Monk 243; Spirit Light Weapon on the Ritualist 224; Guardian on the 7 Monk 201; Shield Guardian PvP on the Prot 182; Cure Hex on the 7 Monk 149; Blessed Light on the 7 Monk 146; Shield Guardian PvP on the 7 Monk 140. Interrupt skills landing most: Power Spike 1820; Complicate 1775; Psychic Instability PvP 809; Power Leak 786; Cry of Frustration 566; Savage Shot 474; Hammer Bash 327; Distracting Shot 275.

**Knockdowns by skill:** Coward 2091; Hammer Bash 1952; Psychic Instability PvP 924; Lightning Surge 524; Mind Shock PvP 483; Grapple 355; Bull's Strike 318; Bane Signet 309.

**Spikes survived** (400+ damage in 3 s on one player; survived = alive 8 s later): losers (every moment, includes who was ahead) 489 of 830 (59%); losers at even win chance 69 of 99 (70%); winners (every moment, includes who was ahead) 319 of 412 (77%); winners at even win chance 52 of 67 (78%). By target: 7 Monk 63% of 144; Prot 62% of 143; Mesmer 68% of 112; 8 Monk 56% of 106; Stand Mes 75% of 104; AoB Derv 65% of 94; Mes/A 84% of 73; Air Ele 61% of 61; Ritualist 68% of 53; Necromancer 46% of 52; Warrior 53% of 47; Hammer 67% of 43; Dervish 65% of 40; Paragon 68% of 38; Fire Ele 52% of 23; Monk 4 (WoC) 73% of 22; Ranger 65% of 20; Water Ele 67% of 18; Assassin 91% of 11; Monk 3 (WoC) 100% of 10.

**Monks** (per 2-minute phase alive 60 s+): winners at even win chance: 12.0 casts a minute, 0.55 fakes, idle 0 s while an ally was hurt, reaction 1.5 s, bursts answered 73%; losers at even win chance: 12.5 casts a minute, 0.51 fakes, idle 0 s while an ally was hurt, reaction 1.4 s, bursts answered 65%; winners every moment (includes who was ahead): 11.5 casts a minute, 0.54 fakes, idle 0.0 s while an ally was hurt, reaction 1.5 s, bursts answered 71%; losers every moment (includes who was ahead): 12.0 casts a minute, 0.51 fakes, idle 1.0 s while an ally was hurt, reaction 1.4 s, bursts answered 61%.

**Deaths** (2293): 702 with a knockdown on the victim; 714 had a monk cast on the victim in the last 5 s. Monk skills interrupted in the 6 s before a death: Blessed Light 106; Healing Burst 87; Guardian 64; Shield Guardian PvP 38; Reversal of Fortune 28; Cure Hex 21; Patient Spirit 17; Signet of Rejuvenation 14.

## 10. For Denning

- Which curves look wrong to you? A correction (direction, cap, drop, or a pair to always test) is logged with your reason and tested on held-out matches.
- Do any surprises remind you of something the variables don't capture (a missing variable)?
- Any variable you think matters that isn't listed?

