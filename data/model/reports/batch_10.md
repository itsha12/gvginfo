# Learning report, batch 10

Trained on 181 matches (48 new in this batch). Variables in use: 31; build variables from 60 matches, interactions from 40.

## 0. Data integrity

- Lengths repaired: 7 (1f65fd3b 150 s -> 1027 s) (bbef1904 617 s -> 599 s) (36a65ac6 1319 s -> 1294 s) (ba85aafc 811 s -> 793 s) (f9d6932f 235 s -> 218 s) (82fa12be 488 s -> 467 s) (cf2968cd 178 s -> 363 s) 
- Matches with a team's Lord damage not observed (left blank, not zero): 11
- Pit NPCs added from the standard roster (never seen in the replay): 655 in 157 matches
- Left out of training: 0

## 1. The honest test

**Beats strength alone (clear: the range excludes 0).** Held-out accuracy (matches held out whole), log loss in brackets (lower is better):

- strength only: all 77% (0.433), 0-5 min 83% (0.347), 5-10 min 79% (0.407), 10-15 min 72% (0.503), 15-end min 65% (0.576), matches lasting 15 min+ 70% (0.539), matches even on strength (gap under 200) 57% (0.618)
- glass box: all 87% (0.314), 0-5 min 86% (0.297), 5-10 min 87% (0.315), 10-15 min 84% (0.398), 15-end min 90% (0.275), matches lasting 15 min+ 84% (0.384), matches even on strength (gap under 200) 75% (0.558)
- glass box without corrections: all 86% (0.344), 0-5 min 85% (0.362), 5-10 min 87% (0.309), 10-15 min 84% (0.395), 15-end min 88% (0.314), matches lasting 15 min+ 82% (0.431), matches even on strength (gap under 200) 74% (0.605)
- black box: all 82% (0.637), 0-5 min 84% (0.564), 5-10 min 82% (0.625), 10-15 min 79% (0.758), 15-end min 79% (0.692), matches lasting 15 min+ 78% (0.765), matches even on strength (gap under 200) 73% (0.915)
- Gain over strength alone (log loss, resampling whole matches): +0.119 (90% range +0.017 to +0.214).
- Change since batch 9: glass box log loss 0.37 -> 0.314; strength only 0.463 -> 0.433.
- Cap test on spike_killable_diff (held-out log loss, 181 matches): none 0.314, 10 points 0.323, 15 points 0.3197, 20 points 0.3167, 25 points 0.3143; chosen: no cap (no option beat it on unseen matches).
- Pair test (morale_diff with map_flag_run, map_pit_to_stand, map_bases_apart; morale_total with map_flag_run, map_pit_to_stand, map_bases_apart; held-out log loss, 181 matches): allowed 0.314, blocked 0.3152; chosen: allowed (blocking didn't predict unseen matches better).
- Calibration by minute (held-out predictions on 181 matches; pooled cells joined by straight lines, blended by minute; every win chance below and in values, usual play and the TQs goes through it). Predicted -> how often those teams won -> calibrated:
  - 0 to 6 min: 0.5% -> won 0.3% (113 matches) -> 0.5%; 3.2% -> won 5.3% (94 matches) -> 5.2%; 42.0% -> won 46.4% (58 matches) -> 46.0%; 58.3% -> won 55.0% (57 matches) -> 55.3%; 92.6% -> won 89.6% (92 matches) -> 89.8%; 99.5% -> won 99.4% (114 matches) -> 99.4%
  - 6 to 12 min: 0.4% -> won 0.9% (114 matches) -> 0.9%; 3.3% -> won 19.6% (57 matches) -> 10.4%; 42.0% -> won 44.0% (39 matches) -> 43.7%; 58.1% -> won 55.1% (35 matches) -> 55.5%; 92.9% -> won 86.7% (58 matches) -> 85.1%; 99.5% -> won 97.9% (111 matches) -> 98.0%
  - 12 to 18 min: 0.5% -> won 5.8% (59 matches) -> 5.4%; 3.3% -> won 10.6% (31 matches) -> 9.6%; 42.3% -> won 46.0% (20 matches) -> 45.3%; 58.1% -> won 56.5% (18 matches) -> 56.8%; 92.8% -> won 84.4% (34 matches) -> 85.5%; 99.5% -> won 94.2% (57 matches) -> 95.2%
  - 18 to end min: 0.4% -> won 6.1% (41 matches) -> 5.5%; 3.3% -> won 6.8% (25 matches) -> 5.7%; 42.8% -> won 45.4% (10 matches) -> 44.5%; 58.0% -> won 63.6% (13 matches) -> 62.0%; 92.8% -> won 93.9% (15 matches) -> 93.7%; 99.6% -> won 94.2% (42 matches) -> 95.6%

## 2. What it leans on

- **morale_diff** 0.59 (was 0.638): own minus enemy morale summed over players (boosts +, death penalty -)
- **spike_killable_diff** 0.44 (was 0.211): enemy minus own players within one spike of the other side (DP stacking; 0 unless a spike build is involved)
- **knights_diff** 0.389 (was 0.304): own minus enemy pit knights alive
- **morale_diff & map_bases_apart** 0.366 (new): own minus enemy morale summed over players (boosts +, death penalty -) TOGETHER WITH the map's distance between the two bases
- **morale_diff & map_flag_run** 0.353 (new): own minus enemy morale summed over players (boosts +, death penalty -) TOGETHER WITH the map's flag run Y: distance from the flag spawn to the stand (average of both sides)
- **alive_diff** 0.259 (was 0.385): own minus enemy players alive
- **knights_diff & map_flag_run** 0.217 (was 0.229): own minus enemy pit knights alive TOGETHER WITH the map's flag run Y: distance from the flag spawn to the stand (average of both sides)
- **lord_damage_diff & lord_dps_own** 0.211 (new): own minus enemy Lord damage dealt so far (the 28:00 tiebreak; players can't see it); blank when either team's Lord damage wasn't observed TOGETHER WITH own build's measured Lord damage per second if all its non-healers were at the Lord
- **spike_build_own** 0.21 (was 0.225): own build is a spike build (1) or not (0)
- **spike_build_enemy** 0.203 (was 0.213): enemy build is a spike build
- **lord_dps_enemy** 0.163 (was 0.178): enemy build's measured Lord damage per second
- **stand** 0.162 (was 0.195): who holds the flag stand: 1 own, 0 nobody, -1 enemy

## 3. The curves in words

Points = win-chance points added to an otherwise even game at each range of the variable.

- **morale_diff** rises from -26.3 to +22.1 points (-500.0..-201.5: -26.3; -153.5..-110.5: -19.3; -84.5..-45.5: -21.2; -15.5..-0.5: -1.2; 0.5..16.5: +2.8; 48.5..91.5: +24.9; 134.5..188.5: +20.1)
- **spike_killable_diff** rises from -44.8 to +44.5 points (-8.0..-7.5: -44.8; -5.5..-4.5: -45.9; -3.5..-2.5: -44.8; -1.5..-0.5: -34.0; 0.5..1.5: +35.1; 2.5..4.5: +45.0; 5.5..7.5: +43.3)
- **knights_diff** rises from -23.0 to +23.5 points (-2.0..-1.5: -23.0; -1.5..-0.5: -14.8; -0.5..0.5: -0.3; 0.5..1.5: +15.7; 1.5..2.0: +23.5)
- **morale_diff & map_bases_apart** (interaction): see wp_model.md
- **morale_diff & map_flag_run** (interaction): see wp_model.md
- **alive_diff** rises from -30.6 to +29.2 points (-8.0..-6.5: -30.6; -4.5..-3.5: -20.5; -2.5..-1.5: -15.6; -0.5..0.5: +0.1; 1.5..2.5: +15.7; 3.5..4.5: +21.0)
- **knights_diff & map_flag_run** (interaction): see wp_model.md
- **lord_damage_diff & lord_dps_own** (interaction): see wp_model.md
- **spike_build_own** rises from -3.2 to +13.2 points (0.0..0.5: -3.2; 0.5..1.0: +13.2)
- **spike_build_enemy** falls from +3.1 to -12.8 points (0.0..0.5: +3.1; 0.5..1.0: -12.8)

## 4. Discovery

**Interaction candidates** (a screen: pairs whose combination seems to matter beyond each alone; untested until held-out matches confirm them; switched on in the model from 40 matches):

- morale_diff with spike_killable_diff (screen 0.165)
- morale_diff with spike_build_enemy (screen 0.158)
- morale_diff with spike_build_own (screen 0.158)
- morale_diff with knights_diff (screen 0.146)
- alive_diff with morale_diff (screen 0.145)
- morale_diff with lord_dps_enemy (screen 0.143)
- morale_diff with lord_dps_own (screen 0.143)
- minute with morale_diff (screen 0.141)

**Candidate variables** (proposed variables, tested on unseen matches; log loss, lower is better):

- split_diff: 0.314 without, 0.307 with: improves: ready to move into the model. own minus enemy players on a split (away from their main group on the enemy half, not carrying). Proposed batch 1 by Claude: the knights curve runs backwards, maybe standing in for the cost of splitting
- turtle_diff: 0.314 without, 0.315 with: does not improve yet. own minus enemy share of live players at home (own base or pit). Proposed 2026-11-06 from OG comms ([ohno v One], [ohno v Crew]: 'they are turtling, we have to make a play'); comms_vars.py: teams that turtled 60 s won 3 of 13 times
- footmen_diff: 0.314 without, 0.316 with: does not improve yet. own minus enemy footmen alive (base NPCs, not pit NPCs). Proposed 2026-11-06 from OG comms ([ohno v NwAy]: 'this way we don't lose footmen'; [ohno v Fun]: fake collapse to the footmen)
- no_healer_groups_diff: 0.314 without, 0.315 with: does not improve yet. own minus enemy groups of 2+ with no healer. Proposed 2026-11-06 from OG comms ([ohno v One]: keep a prot and a monk on one side, the Rit and a monk on the other); comms_vars.py: such groups lose players twice as often
- solo_healers_diff: 0.314 without, 0.315 with: does not improve yet. own minus enemy healers with no other own healer within casting range. Proposed 2026-11-06 from OG comms ('solo monk, go on the monk'); Denning: a monk alone has no other monk to support it

**Surprises** (moments where the held-out model was most confident about the team that went on to lose; each points to something the variables don't capture yet):

- Fun v hold (99d9b260) at 2:15: a model that never saw this match gave hold 7.5%, and hold won. Why it thought so: spike_killable_diff -42.5, team strength +22.8, morale_diff & map_flag_run +21.6, morale_diff -21.1, spike_build_enemy -14.5
- hdm v HC (28447c4a) at 15:15: a model that never saw this match gave HC 5.4%, and HC won. Why it thought so: morale_diff & map_bases_apart -45.6, lord_exposed_diff -38.5, knights_diff -33.3, morale_diff -17.3, morale_diff & map_pit_to_stand +15.4
- Crew v BcS (3ee18c0c) at 12:45: a model that never saw this match gave BcS 6.1%, and BcS won. Why it thought so: knights_diff -17.2, morale_diff -15.7, alive_diff -11.5, lord_damage_diff & lord_dps_own -10.5, bodyguard_diff -7.0
- RACK v hdm (1f65fd3b) at 14:45: a model that never saw this match gave RACK 5.2%, and RACK won. Why it thought so: knights_diff -26.3, morale_diff -23.4, morale_diff & map_flag_run +16.0, lord_damage_diff & map_bases_apart -16.0, team strength -14.0
- Dz v TFS (0881f8b3) at 3:00: a model that never saw this match gave TFS 1.0%, and TFS won. Why it thought so: team strength -46.5, morale_diff -15.7, spike_build_own +13.2, spike_build_enemy -12.9, fight_state -7.9
- cope v Team (427c825b) at 5:45: a model that never saw this match gave Team 3.0%, and Team won. Why it thought so: morale_diff -36.4, morale_diff & map_flag_run -21.6, alive_diff -12.5, spike_build_own +10.9, team strength -9.9

## 5. Denning's rulings seen through the model

Win chance from a model that never saw the match, 20 s before and 60 s after each ruled moment. Contributions are points for an otherwise even game (the curves' scale).

- hdm v HC (28447c4a) 5:01 (split answered), HC: 32.1% 20 s before -> 39.1% 60 s after (+7.0). After: morale_diff & map_bases_apart +39.3, knights_diff -33.3, morale_diff & map_flag_run -17.0, knights_diff & map_flag_run -15.3
- hdm v HC (28447c4a) 5:01 (split answered), hdm: 72.3% 20 s before -> 58.3% 60 s after (-14.0). After: morale_diff & map_bases_apart -40.1, knights_diff +33.3, morale_diff & map_flag_run +17.5, knights_diff & map_flag_run +13.7
- hdm v HC (28447c4a) 1:02 (split detection), HC: 45.6% 20 s before -> 50.7% 60 s after (+5.1). After: morale_diff & map_bases_apart +34.9, morale_diff & map_flag_run -24.4, stand -5.6, carrying_diff -5.6
- hdm v HC (28447c4a) 1:02 (split detection), hdm: 54.7% 20 s before -> 52.9% 60 s after (-1.8). After: morale_diff & map_bases_apart -32.7, morale_diff & map_flag_run +24.7, stand +5.7, team strength +5.4
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), HC: 13.8% 20 s before -> 10.6% 60 s after (-3.2). After: morale_diff & map_bases_apart +39.3, lord_exposed_diff -38.5, knights_diff -33.3, morale_diff & map_flag_run -17.0
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), hdm: 88.8% 20 s before -> 94.8% 60 s after (+6.0). After: morale_diff & map_bases_apart -40.1, lord_exposed_diff +39.2, knights_diff +33.3, lord_damage_diff & minute +19.6
- hdm v HC (bbef1904) 8:10 (death), HC: 60.8% 20 s before -> 15.3% 60 s after (-45.5). After: morale_diff -22.9, alive_diff -15.1, fight_state -7.3, morale_diff & map_flag_run -7.1
- hdm v HC (bbef1904) 8:10 (death), hdm: 39.1% 20 s before -> 87.4% 60 s after (+48.3). After: morale_diff +22.3, alive_diff +15.8, morale_diff & map_flag_run +10.5, fight_state +6.5
- Men v HC (faec428a) 9:31 (death), HC: 40.2% 20 s before -> 32.6% 60 s after (-7.6). After: knights_diff -15.1, archers_diff +7.3, stand -5.6, knights_diff & map_pit_to_stand -5.3
- Men v HC (faec428a) 9:31 (death), Men: 57.5% 20 s before -> 65.4% 60 s after (+7.9). After: knights_diff +15.2, archers_diff -7.5, stand +5.7, lord_dps_own +5.0

## 6. Why: the node models

Each explains one result from what happened before it (time order enforced), tested on matches it never saw. AUC = how often a moment that led to the result scores above one that didn't (0.5 = guessing, 1 = perfect).

**deaths** (181 matches, 354591 moments, 10810 results): adds to the simple baseline (AUC 0.921 against 0.799 for health_pct and damage_taken_3s alone).
- **enemies_near** (enemies within 1,500) rises from -22.2 to +23.7 points (0.0..0.5: -22.2; 0.5..1.5: -12.2; 1.5..2.5: -2.1; 2.5..3.5: +4.4; 3.5..4.5: +7.9; 4.5..5.5: +10.3; 5.5..6.5: +13.5; 6.5..7.5: +16.0; 7.5..8.0: +23.7)
- **strength_gap** (own minus enemy team strength) falls from +15.5 to -18.5 points (-1183.0..-616.5: +15.5; -485.0..-371.5: +9.7; -251.5..-106.0: +9.6; -64.0..-4.5: +2.3; 51.0..96.5: -2.4; 183.5..324.0: -3.1; 449.5..606.0: -15.9)
- **health_pct** (current health %) falls from +40.6 to -6.1 points (1.0..47.5: +40.6; 59.5..67.5: +20.5; 73.5..78.5: +8.8; 82.5..85.5: +4.5; 88.5..91.5: +0.6; 93.5..95.5: -2.4; 97.5..99.5: -5.3)
- **local_diff** (allies minus enemies within 2,000) falls from +24.7 to -23.1 points (-8.0..-3.5: +24.7; -2.5..-1.5: +12.9; -0.5..0.5: -3.4; 1.5..2.5: -3.9; 3.5..4.5: +4.5; 5.5..7.0: -23.1)
- **allies_near** (allies within 1,500) falls from +21.0 to -8.3 points (0.0..0.5: +21.0; 0.5..1.5: +11.0; 1.5..2.5: +5.5; 2.5..3.5: -1.1; 3.5..4.5: -2.1; 4.5..5.5: -3.9; 5.5..6.5: -5.4; 6.5..7.0: -8.3)
- **own_prots** (own prot skills) falls from +2.9 to -7.6 points (0.0..4.5: +2.9; 6.5..7.5: +11.0; 8.5..9.5: +1.5; 10.5..11.5: +1.6; 12.5..13.5: -3.7; 14.5..15.5: -1.4; 16.5..18.0: -7.6)
- **enemy_interrupts** (enemy interrupt skills) rises from -9.7 to +14.4 points (0.0..0.5: -9.7; 1.5..2.5: +3.2; 3.5..4.5: -1.3; 5.5..6.5: -2.0; 7.5..8.5: +9.9)
- **dist_own_pit** (distance from its own pit) rises from -2.6 to +8.7 points (6.0..1309.5: -2.6; 2297.5..3971.5: -2.4; 5190.5..6170.5: -2.5; 6935.5..7564.5: -1.3; 8188.5..8803.5: -2.0; 9645.5..10677.5: +0.3; 11994.5..13560.5: +8.8)
- **minute** (match minute) rises from -1.9 to +14.5 points (0.1..1.15: -1.9; 2.05..2.95: -4.2; 3.95..4.95: -3.6; 6.05..7.25: +0.1; 8.75..10.25: -2.5; 12.05..14.25: -2.2; 17.05..20.65: +4.5)

**kill conversion** (178 matches, 2943 moments, 906 results): adds to the simple baseline (AUC 0.794 against 0.68 for burst_damage and target_health_pct alone).
- **target_healers_in_range** (target's healers in range) falls from +27.1 to +0.5 points (0.0..0.5: +27.1; 0.5..1.5: +3.7; 1.5..2.5: -5.4; 2.5..3.5: -8.3; 3.5..4.0: +0.5)
- **burst_damage** (damage in the 2 s burst) rises from -9.4 to +23.3 points (250.0..256.5: -9.4; 264.5..275.5: -9.1; 285.5..295.5: -6.5; 308.5..323.5: -4.2; 338.5..355.5: -1.8; 377.5..406.5: +5.0; 443.5..500.5: +21.3)
- **target_health_pct** (target health % when the burst started) falls from +26.3 to -12.7 points (0.0..40.5: +26.3; 51.5..57.5: +9.7; 63.5..68.5: +3.5; 72.5..76.5: +0.9; 80.5..83.5: -0.4; 87.5..91.5: -2.3; 95.5..99.5: -11.6)
- **target_ceiling** (target's health ceiling) falls from +26.3 to -11.1 points (0.4..0.69: +26.3; 0.7..0.73: +17.4; 0.84..0.85: +11.0; 0.86..0.88: +8.1; 0.94..0.95: +4.7; 0.99..1.02: -3.9; 1.1..1.1: -11.1)
- **strength_gap** (attacking minus target team strength) rises from -12.5 to +15.7 points (-1183.0..-565.5: -12.5; -308.5..-168.5: -9.5; -88.0..-17.5: -2.8; 51.0..86.0: -0.5; 127.5..183.5: -0.2; 289.0..419.0: +8.3; 554.0..647.0: +10.7)
- **target_prot_up** (a prot on the target) falls from +4.0 to -7.7 points (0.0..0.5: +4.0; 0.5..1.0: -7.7)
- **enemy_prots** (target team's prot skills) falls from +7.3 to -7.0 points (1.0..5.5: +7.3; 6.5..7.5: +9.2; 8.5..9.5: +3.6; 10.5..11.5: -0.8; 12.5..13.5: -3.2; 14.5..15.5: -4.8; 16.5..18.0: -7.0)

**flag answer** (seconds an answer to an enemy capture was slower than possible; 152 matches, 1255 rows): adds to the simple baseline (typical error 16.4s against 28.8s for the median; explains 72% of the spread).
- **parked_s** (seconds the flag lay parked (dropped 5 s or more: not running yet)): 0.0..2.5: -5.4 s; 9.5..14.5: +7.9 s; 18.5..25.5: +17.6 s; 31.5..37.5: +35.3 s; 45.5..58.5: +53.9 s; 72.5..99.5: +64.9 s; 118.0..246.5: +68.8 s
- **enemies_in_the_way** (enemy presence along the runner's trip back to the spawn): 0.0..0.5: -5.2 s; 4.5..10.5: -5.1 s; 16.5..21.5: -4.0 s; 28.5..38.5: -1.4 s; 48.5..60.5: +2.7 s; 85.5..107.5: +8.1 s; 141.0..203.0: +17.0 s
- **carrier_damage_taken** (damage the carrier took while carrying): 0.0..0.5: -5.2 s; 30.5..56.0: -3.6 s; 86.0..113.0: -2.7 s; 155.5..225.5: -0.9 s; 270.5..336.0: +2.4 s; 444.0..566.0: +8.6 s; 789.5..1117.0: +16.8 s
- **enemy_deaths_during** (enemy deaths during the answer): 0.0..0.5: -3.7 s; 0.5..1.5: +9.0 s; 1.5..2.5: +16.2 s; 2.5..3.5: +21.5 s; 3.5..4.5: +21.1 s; 4.5..5.5: +20.8 s; 5.5..12.0: +40.1 s
- **own_deaths_during** (own deaths during the answer): 0.0..0.5: -3.4 s; 0.5..1.5: +6.8 s; 1.5..2.5: +12.5 s; 2.5..3.5: +15.9 s; 3.5..4.5: +26.3 s; 4.5..5.5: +32.6 s; 5.5..6.5: +46.8 s; 6.5..9.5: +61.4 s; 9.5..17.0: +58.9 s
- **possible_s** (fastest possible answer (s) from the flag model at the enemy's capture): 0.0..3.5: -8.8 s; 7.5..12.5: -6.7 s; 18.5..22.5: -1.5 s; 26.5..29.5: +4.0 s; 32.5..36.5: +5.7 s; 40.5..44.5: +5.4 s; 49.5..55.5: +3.1 s
- **runner_to_spawn** (runner's distance to its flag spawn when the enemy captured): 16.0..739.5: -7.6 s; 1382.5..1970.0: -3.2 s; 2779.5..3523.0: -0.0 s; 4084.5..4455.5: +1.6 s; 4903.5..5618.0: +1.9 s; 6320.5..6958.5: +3.6 s; 7611.5..8459.0: +1.8 s
- **morale_diff** (own minus enemy morale): -269.0..-97.0: +9.1 s; -60.5..-35.5: +4.1 s; -16.0..-14.5: +2.3 s; -1.0..1.0: -0.2 s; 14.5..17.0: -1.0 s; 32.5..60.5: -3.0 s; 89.0..128.5: -6.2 s
- **quick_handoffs** (quick hand-offs (a teammate picked it up within 5 s)): 0.0..0.5: -1.2 s; 0.5..1.5: +4.7 s; 1.5..2.5: +3.2 s; 2.5..4.0: +5.4 s
- **runner_line** (runner 0 frontline, 1 midline, 2 backline): 0.0..0.5: -1.2 s; 0.5..1.5: +1.7 s; 1.5..2.0: -3.6 s

**npc loss** (180 matches, 17464 moments, 3585 results): adds to the simple baseline (AUC 0.854 against 0.757 for attackers and defenders alone).
- **npc_damage_5s** (damage on the pit NPCs in the last 5 s) rises from -17.4 to +35.5 points (0.0..0.5: -17.4; 22.5..37.5: +3.6; 50.5..69.5: +8.1; 88.5..110.5: +16.8; 135.5..162.5: +24.2; 195.5..238.5: +27.5; 298.5..398.5: +34.0)
- **defenders** (own players in the pit) falls from +33.5 to -33.3 points (0.0..0.5: +33.5; 0.5..1.5: +16.7; 1.5..2.5: +12.1; 2.5..3.5: +2.9; 3.5..4.5: -7.4; 4.5..5.5: -14.7; 5.5..6.5: -16.7; 6.5..7.5: -27.1; 7.5..8.0: -33.3)
- **defenders_elsewhere** (own players alive outside the pit) falls from +22.3 to -10.6 points (0.0..0.5: +22.3; 0.5..1.5: +13.4; 1.5..2.5: +8.4; 2.5..3.5: -1.3; 3.5..4.5: -8.8; 4.5..5.5: -14.1; 5.5..6.5: -15.1; 6.5..7.5: -14.6; 7.5..8.0: -10.6)
- **attackers** (enemy players in the pit) rises from -12.0 to +13.1 points (1.0..1.5: -12.0; 1.5..2.5: -4.4; 2.5..3.5: -2.6; 3.5..4.5: +2.2; 4.5..5.5: +7.1; 5.5..6.5: +8.9; 6.5..7.5: +11.5; 7.5..8.0: +13.1)
- **defender_healers** (of which healers) falls from +21.1 to -9.9 points (0.0..0.5: +21.1; 0.5..1.5: -1.1; 1.5..2.5: -5.2; 2.5..3.5: -8.3; 3.5..4.0: -9.9)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -10.5 to +4.3 points (1.9..14.15: -10.5; 22.7..31.1: -7.9; 32.8..43.15: -5.1; 53.2..63.95: +2.7; 66.65..75.75: +5.9; 82.35..88.45: +7.9; 99.35..111.75: +4.2)
- **strength_gap** (attacking minus defending team strength) rises from -6.7 to +5.5 points (-989.0..-433.0: -6.7; -295.0..-145.5: -10.7; -44.0..31.0: +2.9; 84.0..133.5: +1.9; 255.0..317.5: +3.0; 417.5..474.5: +3.6; 576.0..767.0: +5.0)
- **npc_healing_10s** (healing on own pit NPCs and Lord in the last 10 s) falls from +3.2 to -13.3 points (0.0..1.5: +3.2; 41.5..50.5: +1.9; 85.5..125.5: +1.0; 157.5..194.5: -4.4; 232.5..280.5: -6.8; 339.5..401.5: -7.8; 495.5..649.0: -12.3)
- **minute** (match minute) falls from +4.6 to -0.2 points (0.2..2.65: +4.6; 3.55..4.55: +2.2; 5.55..6.65: +4.3; 7.85..9.25: +2.6; 10.65..12.25: -5.0; 14.35..17.05: -5.2; 20.25..23.75: -3.6)

**lord damage** (Lord damage dealt in the next 10 s while players are in the enemy pit; 175 matches, 19976 rows): adds to the simple baseline (typical error 79.3 against 101.9 for the median; explains 38% of the spread).
  ('chance of any' curves: points of the chance of any Lord damage in the window; 'amount' curves: % more Lord damage when there is some.)
- **defenders (chance of any)** (own players in the pit): 0.0..0.5: +38.1 points; 0.5..1.5: +29.4 points; 1.5..2.5: +23.3 points; 2.5..3.5: +3.7 points; 3.5..4.5: -10.4 points; 4.5..5.5: -26.0 points; 5.5..6.5: -33.2 points; 6.5..7.5: -40.3 points; 7.5..8.0: -44.6 points
- **bodyguard (chance of any)** (own Bodyguard alive): 0.0..0.5: +25.1 points; 0.5..1.0: -11.1 points
- **knights (chance of any)** (own knights alive): 0.0..0.5: +13.0 points; 0.5..1.5: -8.9 points; 1.5..2.0: -14.1 points
- **attackers_share (chance of any)** (share of the attacking team's live players in the pit (OG comms: merge before pushing the pit)): 0.12..0.13: -13.4 points; 0.16..0.23: -10.4 points; 0.27..0.35: -8.1 points; 0.42..0.53: -4.1 points; 0.61..0.65: +10.0 points; 0.73..0.84: +14.1 points; 0.94..1.0: +16.5 points
- **npc_healing_10s (chance of any)** (healing on own pit NPCs and Lord in the last 10 s): 0.0..1.5: -8.0 points; 41.5..54.5: +10.0 points; 88.5..126.5: +11.4 points; 157.5..194.5: +12.9 points; 231.5..279.5: +14.2 points; 334.5..399.5: +15.3 points; 489.5..646.5: +15.9 points
- **minute (chance of any)** (match minute): 0.5..2.75: -23.5 points; 3.75..4.85: -10.6 points; 5.85..6.95: -6.5 points; 8.15..9.55: -0.1 points; 10.95..12.55: -2.4 points; 14.75..17.45: +0.6 points; 20.35..23.95: +16.3 points
- **attacker_healers (chance of any)** (of which healers): 0.0..0.5: -9.1 points; 0.5..1.5: +4.4 points; 1.5..2.5: +7.9 points; 2.5..3.5: +8.4 points; 3.5..4.0: +42.9 points
- **attackers_lord_dps (chance of any)** (attackers' measured damage per second against a Lord (benchmarks)): 1.9..18.45: -11.2 points; 23.95..32.0: -9.3 points; 32.8..44.55: -5.3 points; 57.55..64.35: -0.4 points; 70.15..76.15: +1.5 points; 84.35..93.05: +16.1 points; 102.85..113.45: +7.6 points
- **attackers (chance of any)** (enemy players in the pit): 1.0..1.5: -8.1 points; 1.5..2.5: -2.4 points; 2.5..3.5: -1.7 points; 3.5..4.5: -0.2 points; 4.5..5.5: +2.1 points; 5.5..6.5: +3.2 points; 6.5..7.5: +4.2 points; 7.5..8.0: +13.8 points
- **defenders_elsewhere (chance of any)** (own players alive outside the pit): 0.0..0.5: +3.6 points; 0.5..1.5: +4.5 points; 1.5..2.5: +5.0 points; 2.5..3.5: +5.4 points; 3.5..4.5: +5.6 points; 4.5..5.5: -2.5 points; 5.5..6.5: -6.3 points; 6.5..7.5: -8.0 points; 7.5..8.0: -7.9 points

**lord kill** (175 matches, 19962 moments, 1547 results): adds to the simple baseline (AUC 0.968 against 0.936 for attackers and defenders alone).
- **defenders** (own players in the pit) falls from +44.4 to -48.6 points (0.0..0.5: +44.4; 0.5..1.5: +37.0; 1.5..2.5: +18.4; 2.5..3.5: +11.4; 3.5..4.5: -18.9; 4.5..5.5: -22.8; 5.5..6.5: -36.0; 6.5..7.5: -44.0; 7.5..8.0: -48.6)
- **minute** (match minute) rises from -46.3 to +24.9 points (0.5..2.75: -46.3; 3.75..4.85: -34.2; 5.85..6.95: +8.5; 8.15..9.45: +15.3; 10.85..12.55: +16.3; 14.75..17.45: +24.0; 20.35..23.95: +24.9)
- **defenders_elsewhere** (own players alive outside the pit) falls from +30.6 to -25.1 points (0.0..0.5: +30.6; 0.5..1.5: +14.6; 1.5..2.5: +13.7; 2.5..3.5: +12.2; 3.5..4.5: +8.3; 4.5..5.5: -23.6; 5.5..6.5: -25.3; 6.5..7.5: -27.4; 7.5..8.0: -25.1)
- **attackers_share** (share of the attacking team's live players in the pit (OG comms: merge before pushing the pit)) rises from -17.2 to +20.8 points (0.12..0.13: -17.2; 0.16..0.23: -13.9; 0.27..0.35: -10.5; 0.42..0.53: -6.6; 0.61..0.65: +16.5; 0.73..0.84: +19.2; 0.94..1.0: +20.8)
- **res_in** (seconds until the next res) rises from -39.4 to -8.5 points (1.0..8.5: -39.4; 17.5..26.5: +5.2; 35.5..44.5: +12.4; 53.5..59.5: +11.5; 65.5..71.5: +9.5; 77.5..86.5: +6.9; 95.5..107.5: +4.0)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -12.1 to +13.5 points (1.9..18.45: -12.1; 23.95..32.0: -19.8; 32.8..43.3: -13.7; 56.95..64.35: -2.4; 70.15..76.15: +16.2; 84.35..93.05: +19.3; 102.85..113.45: +21.2)
- **defender_healers** (of which healers) falls from +25.2 to -25.7 points (0.0..0.5: +25.2; 0.5..1.5: +4.1; 1.5..2.5: -7.0; 2.5..3.5: -19.1; 3.5..4.0: -25.7)
- **attackers** (enemy players in the pit) rises from -20.5 to +16.3 points (1.0..1.5: -20.5; 1.5..2.5: -3.9; 2.5..3.5: +0.4; 3.5..4.5: +5.6; 4.5..5.5: +10.5; 5.5..6.5: +12.7; 6.5..7.5: +14.3; 7.5..8.0: +16.3)
- **lord_health** (the Lord's rebuilt health as a share of its max (lord.py)) falls from +47.1 to -6.3 points (0.0..0.1: +47.1; 0.35..0.54: +40.3; 0.66..0.75: +32.1; 0.82..0.86: +20.4; 0.9..0.93: +15.3; 0.95..0.97: +5.5; 0.99..1.0: +1.7)
- **npc_healing_10s** (healing on own pit NPCs and Lord in the last 10 s) falls from +6.4 to -20.6 points (0.0..1.5: +6.4; 41.5..54.5: +0.4; 88.5..126.5: -2.7; 157.5..194.5: -10.3; 231.5..279.5: -14.8; 334.5..399.5: -17.3; 489.5..646.5: -19.1)


## 6b. The learned nodes (step 2 of the learned causal map)

Each node uses only the causal-map links into it. A link's strength is how much worse the node predicts matches it never saw without that link's features (refit without them, same folds); supported when the gain is more than twice its spread across folds, rejected when dropping it helps by more than that, otherwise not clear yet.

**run outcome** (map R.3; 181 matches, 5688 cases, result rate 61%): log loss 0.5914 against 0.6724 for the simple baseline (adds to the simple baseline).
- link K.13 -> R.3: gain +0.0394 (+/- 0.0066), supported (min_capture_s, runner_escapes)
- link S.scoreboard -> R.3: gain +0.0084 (+/- 0.0038), supported (morale_diff, boost_clock)
- link C.builds -> R.3: gain +0.0025 (+/- 0.0015), not clear yet (enemy_snares)
- link C.map -> R.3: gain +0.0004 (+/- 0.0023), not clear yet (run_dist)
- link C.strength -> R.3: gain -0.0006 (+/- 0.0014), not clear yet (strength_gap)
- link A.allocation -> R.3: gain -0.0022 (+/- 0.002), not clear yet (escort, own_main, enemy_main, enemy_power_play)
- link K.11 -> R.3: gain -0.0035 (+/- 0.0012), rejected (crippled_so_far, knocked_down_so_far, other_control_so_far, damage_so_far...)
- link P.10 -> R.3: gain -0.0046 (+/- 0.0038), not clear yet (stand_own, stand_enemy, enemy_boost_in, flag_lead...)
  - leans on **min_capture_s** (seconds the carrier needs at least to reach the stand from here, at its fastest expected carry speed (its speed skills; Denning)): +32.0 points at 0.0 to 3.85, -31.9 at 32.25 to 50.5
  - leans on **boost_clock** (boost clock (discovery, approved)): +9.5 points at -120.0 to -112.5, -15.8 at 102.5 to 119.0
  - leans on **morale_diff** (morale, own minus enemy (discovery, approved)): -15.2 points at -400.0 to -141.0, -7.1 at 130.0 to 335.0

**flag swing** (map R.3; 181 matches, 6464 cases, average 0.2 s): mean absolute error (s) 26.477 against 27.9264 for the simple baseline (adds to the simple baseline).
- link P.10 -> R.3: gain +0.77 (+/- 0.11), supported (waiting_runner, backup_flag, stand_own, stand_enemy...)
- link S.scoreboard -> R.3: gain +0.59 (+/- 0.09), supported (flag_lead, morale_diff)
- link C.strength -> R.3: gain +0.11 (+/- 0.09), not clear yet (strength_gap)
- link R.1 -> R.3: gain +0.01 (+/- 0.02), not clear yet (own_deaths_30s, enemy_deaths_30s)
- link C.clock -> R.3: gain -0.01 (+/- 0.02), not clear yet (minute, res_in)
- link C.map -> R.3: gain -0.02 (+/- 0.01), not clear yet (run_dist)
- link A.allocation -> R.3: gain -0.03 (+/- 0.01), rejected (own_alive, enemy_alive, own_main, enemy_main...)
  - leans on **flag_lead** (flag lead now (s)): +14.3 s at -124.0 to -66.5, -14.4 at 64.5 to 109.0
  - leans on **morale_diff** (morale, own minus enemy (discovery, approved)): -12.3 s at -445.0 to -169.0, +11.8 at 182.5 to 430.0
  - leans on **strength_gap** (team strength gap): -6.4 s at -1183.0 to -598.5, +7.0 at 602.5 to 1183.0

**run defence** (map R.3; 181 matches, 5688 cases, result rate 61%): log loss 0.5801 against 0.6724 for the simple baseline (adds to the simple baseline).
- link K.13 -> R.3: gain +0.0406 (+/- 0.0056), supported (min_capture_s)
- link S.scoreboard -> R.3: gain +0.0359 (+/- 0.0041), supported (boost_clock, stand, flag_lead, morale_diff...)
- link C.builds -> R.3: gain +0.0006 (+/- 0.0016), not clear yet (own_snares)
- link C.map -> R.3: gain +0.0006 (+/- 0.0022), not clear yet (run_dist)
- link P.10 -> R.3: gain -0.0006 (+/- 0.0029), not clear yet (runner_class)
- link K.11 -> R.3: gain -0.0012 (+/- 0.0003), rejected (def_snare_near)
- link C.strength -> R.3: gain -0.0016 (+/- 0.0015), not clear yet (strength_gap)
- link A.allocation -> R.3: gain -0.0023 (+/- 0.0021), not clear yet (escort, att_main, def_main)
- link A.mesa_free -> R.3: gain -0.0027 (+/- 0.0013), rejected (def_free, pushers_so_far, control_so_far, damage_so_far)
  - leans on **min_capture_s** (seconds the carrier needs at least to reach the stand from here (its speed skills)): +31.8 points at 0.0 to 3.85, -31.1 at 32.25 to 50.5
  - leans on **boost_clock** (boost clock (discovery, approved)): -8.7 points at -119.0 to -102.5, +1.7 at 112.5 to 120.0
  - leans on **stand** (stand (discovery, approved)): -8.0 points at -1.0 to -0.5, +4.5 at 0.5 to 1.0

**capture speed** (map R.3; 172 matches, 1334 cases, average 41.2 s): mean absolute error (s) 14.9721 against 17.1867 for the simple baseline (adds to the simple baseline).
- link K.13 -> R.3: gain +2.15 (+/- 0.25), supported (min_capture_s)
- link A.allocation -> R.3: gain +0.4 (+/- 0.16), supported (defenders_free, escort)
- link C.map -> R.3: gain +0.31 (+/- 0.16), not clear yet (run_dist)
- link P.10 -> R.3: gain +0.12 (+/- 0.11), not clear yet (runner_class)
- link C.strength -> R.3: gain -0.04 (+/- 0.04), not clear yet (strength_gap)
- link K.11 -> R.3: gain -0.13 (+/- 0.06), rejected (pushers_10s, control_10s, damage_10s, def_snare_near)
  - leans on **min_capture_s** (seconds the carrier needed at least, at its fastest expected carry speed (its speed skills)): -13.3 s at 1.6 to 10.05, +13.8 at 36.45 to 45.4
  - leans on **escort** (the runner's escorts): -3.8 s at 0.0 to 0.5, +18.3 at 6.5 to 7.0
  - leans on **run_dist** (distance from the runner's spawn to the stand): +4.4 s at 3105.0 to 4271.0, -4.5 at 9249.5 to 9335.0

**power play** (map K.4; 181 matches, 1500 cases, result rate 40%): log loss 0.3499 against 0.673 for the simple baseline (adds to the simple baseline).
- link A.allocation -> K.4: gain +0.0519 (+/- 0.0132), supported (size, own_main, enemy_main, short_dead...)
- link K.2 -> K.4: gain +0.0338 (+/- 0.0074), supported (dps_v_usual)
- link S.scoreboard -> K.4: gain +0.0169 (+/- 0.005), supported (down_diff_s, carrying_diff)
- link K.5 -> K.4: gain +0.0084 (+/- 0.0057), not clear yet (enemy_prots_10s, enemy_heal_s)
- link P.1 -> K.4: gain +0.0038 (+/- 0.0028), not clear yet (spikes_on_healers, healer_damage_share)
- link P.14 -> K.4: gain +0.0033 (+/- 0.0034), not clear yet (pushed)
- link C.strength -> K.4: gain +0.0032 (+/- 0.0046), not clear yet (strength_gap)
- link R.3 -> K.4: gain +0.0002 (+/- 0.0013), not clear yet (flag_lead)
- link P.2 -> K.4: gain +0.0 (+/- 0.0085), not clear yet (spikes_10s, spike_spread)
- link K.11 -> K.4: gain -0.0006 (+/- 0.0014), not clear yet (blind_secs_on_own_10s)
  - leans on **short_dead** (share of the enemy's missing player-seconds: dead): -19.7 points at 0.0 to 0.01, +16.1 at 0.99 to 1.0
  - leans on **dps_v_usual** (own damage per second against the usual of the players alive): -31.6 points at 0.0 to 0.49, +24.2 at 3.15 to 14.92
  - leans on **window_s** (seconds the power play lasted): -16.8 points at 14.0 to 31.5, +32.5 at 105.5 to 290.0

**fight outcome** (map R.2; 181 matches, 1286 cases, result rate 46%): log loss 0.2711 against 0.6904 for the simple baseline (adds to the simple baseline).
- link S.scoreboard -> R.2: gain +0.0891 (+/- 0.0208), supported (morale_diff, fight_state, down_diff_s, alive_diff...)
- link K.1 -> R.2: gain +0.0221 (+/- 0.008), supported (dps_v_usual_diff)
- link P.2 -> R.2: gain +0.0161 (+/- 0.0069), supported (spike_spread_diff, spikes_diff)
- link A.allocation -> R.2: gain +0.0132 (+/- 0.0028), supported (own_local, enemy_local)
- link P.17 -> R.2: gain +0.0088 (+/- 0.0044), supported (ready_interrupt_diff, dazed_casts_diff, blind_attacks_diff)
- link P.13 -> R.2: gain +0.0014 (+/- 0.0052), not clear yet (peel_defensive_diff)
- link C.strength -> R.2: gain +0.0005 (+/- 0.0018), not clear yet (strength_gap)
- link P.19 -> R.2: gain -0.0011 (+/- 0.001), not clear yet (blind_front_secs_diff, blind_defensive_secs_diff)
- link P.18 -> R.2: gain -0.0012 (+/- 0.0029), not clear yet (strip_right_diff, strip_value_diff)
- link P.5 -> R.2: gain -0.0013 (+/- 0.0023), not clear yet (hex_secs_diff, hex_right_diff)
- link P.1 -> R.2: gain -0.0027 (+/- 0.0009), rejected (healer_focus_diff)
  - leans on **morale_diff** (morale, own minus enemy (discovery, approved)): -15.9 points at -421.0 to -206.5, +30.5 at 211.0 to 410.0
  - leans on **dps_v_usual_diff** (damage against the usual of the players alive, own minus enemy): -23.0 points at -14.43 to -2.01, +21.7 at 1.81 to 9.92
  - leans on **ready_interrupt_diff** (interrupted after casting into a ready interrupt, per cast, own minus enemy): +18.2 points at -0.28 to -0.08, -25.3 at 0.09 to 0.28

**split chance** (map A.allocation; 181 matches, 12651 cases, result rate 13%): log loss 0.3515 against 0.3899 for the simple baseline (adds to the simple baseline).
- link S.scoreboard -> A.allocation: gain +0.0313 (+/- 0.0017), supported (flag_lead, own_alive, enemy_alive, own_main...)
- link C.clock -> A.allocation: gain +0.0015 (+/- 0.0011), not clear yet (minute, res_in)
- link C.builds -> A.allocation: gain +0.0002 (+/- 0.0025), not clear yet (own_speed_power, own_escapes, own_snare_power, enemy_snare_power)
- link C.strength -> A.allocation: gain -0.0013 (+/- 0.0008), not clear yet (strength_gap)
  - leans on **own_main** (own main): +27.0 points at 0.0 to 2.5, -18.6 at 7.5 to 8.0
  - leans on **split_diff** (players splitting, own minus enemy (discovery, approved)): -7.4 points at -6.0 to -4.5, -4.7 at 1.5 to 4.0
  - leans on **turtle_diff** (turtling, own minus enemy (discovery, approved)): +3.8 points at -1.0 to -0.94, -29.3 at 0.94 to 1.0

**split answer** (map P.11; 125 matches, 453 cases, average -3.6 s): mean absolute error (s) 16.9659 against 18.9117 for the simple baseline (adds to the simple baseline).
- link A.allocation -> P.11: gain +1.02 (+/- 0.2), supported (size)
- link A.mesa_free -> P.11: gain +0.69 (+/- 0.2), supported (def_free, nearest_to_base)
- link C.strength -> P.11: gain -0.08 (+/- 0.07), not clear yet (strength_gap)
- link S.scoreboard -> P.11: gain -0.11 (+/- 0.19), not clear yet (flag_lead, def_alive, att_main, split_diff)
- link C.clock -> P.11: gain -0.22 (+/- 0.12), not clear yet (minute)
  - leans on **size** (split size): +16.7 s at 1.0 to 1.5, -13.7 at 5.5 to 7.0
  - leans on **nearest_to_base** (nearest defender to its base at the split's entry): +5.3 s at 31.0 to 451.5, +13.4 at 7194.0 to 13776.0
  - leans on **strength_gap** (defending team's strength gap): -2.9 s at -1059.0 to -689.0, -2.7 at 521.0 to 976.0

**split effect** (map R.5; 125 matches, 453 cases, result rate 41%): log loss 0.6318 against 0.6777 for the simple baseline (adds to the simple baseline).
- link S.scoreboard -> R.5: gain +0.0328 (+/- 0.0057), supported (def_npc_value, def_free, morale_diff, flag_lead...)
- link C.builds -> R.5: gain +0.0102 (+/- 0.005), supported (enemy_prots)
- link K.11 -> R.5: gain +0.0061 (+/- 0.0021), supported (def_snare_present)
- link K.13 -> R.5: gain +0.0056 (+/- 0.0022), supported (split_speed_power)
- link P.11 -> R.5: gain +0.0034 (+/- 0.0016), supported (latency, defenders)
- link K.8 -> R.5: gain +0.0002 (+/- 0.0013), not clear yet (split_healers)
- link C.strength -> R.5: gain -0.0032 (+/- 0.0031), not clear yet (strength_gap)
- link A.allocation -> R.5: gain -0.0088 (+/- 0.0023), rejected (size, main_diff)
  - leans on **enemy_prots** (prot skills on the defenders' bars (discovery, approved)): +3.7 points at 1.0 to 7.5, -5.3 at 13.5 to 18.0
  - leans on **lord_damage_diff** (Lord damage, own minus enemy (discovery, approved)): +0.8 points at -7465.0 to -2.5, -13.3 at 2157.0 to 16474.0
  - leans on **def_npc_value** (defenders' pit NPC value when the split entered the base): -10.7 points at 0.0 to 0.75, +1.1 at 11.25 to 13.5

**collapse** (map R.1; 164 matches, 1071 cases, result rate 12%): log loss 0.3263 against 0.3675 for the simple baseline (adds to the simple baseline).
- link P.9 -> R.1: gain +0.0073 (+/- 0.0048), not clear yet (defenders_10s, contact_diff, npc_hit_to_arrival, res_in_at_arrival)
  - alone: defenders_10s (defenders arriving within 10 s of the first (arrival spread)): gain -0.0017 (+/- 0.0018), not clear yet
  - alone: contact_diff (defenders arriving within 5 s of the first, minus the split's size (numbers at contact)): gain -0.0029 (+/- 0.0019), not clear yet
  - alone: npc_hit_to_arrival (seconds from the split's first hit on an NPC to the first defender's arrival): gain -0.0001 (+/- 0.0022), not clear yet
  - alone: res_in_at_arrival (seconds to the next res when the first defender arrived): gain -0.0012 (+/- 0.0017), not clear yet
- link K.11 -> R.1: gain +0.006 (+/- 0.0037), not clear yet (def_snare_present)
- link A.allocation -> R.1: gain +0.0016 (+/- 0.0047), not clear yet (size, main_diff)
- link P.20 -> R.1: gain -0.0013 (+/- 0.0017), not clear yet (depth_at_arrival, depth_median)
  - alone: depth_at_arrival (nearest split member's distance to the defending pit when the first defender arrived): gain -0.0024 (+/- 0.0016), not clear yet
  - alone: depth_median (nearest split member's median distance to the defending pit over the split): gain -0.0007 (+/- 0.0017), not clear yet
- link P.11 -> R.1: gain -0.0014 (+/- 0.0007), rejected (latency)
- link C.strength -> R.1: gain -0.0023 (+/- 0.0055), not clear yet (strength_gap)
- link K.13 -> R.1: gain -0.0033 (+/- 0.0009), rejected (escape_ready, split_speed_power, split_escapes)
  - leans on **def_snare_present** (snare power of the defenders who came (movepower.py; how strong, not just whether)): -6.1 points at 0.0 to 2.05, +18.3 at 100.75 to 162.8
  - leans on **main_diff** (own main minus enemy main meanwhile): +8.8 points at -6.3 to -2.45, -19.1 at 2.05 to 6.8
  - leans on **defenders_10s** (defenders arriving within 10 s of the first (arrival spread)): -6.2 points at 0.0 to 0.5, +13.9 at 7.5 to 8.0

## 7. The usual play

Each choice against the most common one in that kind of decision, in win-chance points over the decision's window, adjusted for the situation, with a 90% range from resampling whole matches. CLEAR = the range excludes 0. Win chance comes from a model that never saw the match. The same comparison over the 30 s BEFORE the decision is a placebo test: a choice can't cause what came before it, so a clear difference there means the effect is partly who makes that choice.

**after wipe** (399 decisions, 170 matches; usual: pushed the pit)
- reset (n 55): -1.3 [-4.3, +1.6]; in the 30 s before: +0.4 [-2.7, +3.5]
- took the flag (n 46): -4.4 [-8.3, -0.7] CLEAR; in the 30 s before: +0.3 [-3.2, +4.5]
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - reset, Corrupted Isle: -0.6 (n 12 against 48)
  - reset, Isle of Meditation: -0.5 (n 10 against 63)
  - took the flag, Corrupted Isle: +0.9 (n 11 against 48)
  - took the flag, Isle of Meditation: -5.9 (n 13 against 63)

**boost clock** (637 decisions, 165 matches; usual: not running, fought)
- not running, fell back (n 103): -0.9 [-2.2, +0.9]; in the 30 s before: -0.9 [-2.5, +0.5]
- running, advanced (n 97): +2.4 [-0.1, +4.8]; in the 30 s before: +1.3 [-0.2, +2.6]
- not running, advanced (n 88): -0.7 [-3.1, +1.8]; in the 30 s before: +1.2 [-0.5, +2.5]
- running, fought (n 61): +2.3 [-0.0, +4.8]; in the 30 s before: -0.2 [-2.7, +2.2]
- not running, held (n 60): +1.5 [+0.2, +3.7] CLEAR; in the 30 s before: +0.1 [-1.5, +1.3]
- running, held (n 33): +1.4 [-1.4, +4.2]; in the 30 s before: +0.2 [-1.2, +1.7]
- running, fell back (n 33): +4.6 [+1.9, +7.8] CLEAR; in the 30 s before: -2.7 [-5.3, -0.2] ALREADY DIFFERENT BEFORE: partly who chooses it
- not running, to the spawn (n 11): +1.7 [-0.7, +4.0]; in the 30 s before: -0.1 [-2.5, +1.9]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - not running, fell back, behind in the fight (lowest third, -0.11 or less): +1.2 (n 46 against 78)
  - not running, fell back, middle third: -1.9 (n 38 against 43)
  - not running, fell back, ahead in the fight (top third, above -0.01): -5.0 (n 19 against 30)
  - running, advanced, behind in the fight (lowest third, -0.11 or less): -0.2 (n 15 against 78)
  - running, advanced, middle third: -1.3 (n 38 against 43)
  - running, advanced, ahead in the fight (top third, above -0.01): +4.5 (n 44 against 30)
  - not running, advanced, behind in the fight (lowest third, -0.11 or less): -1.7 (n 26 against 78)
  - not running, advanced, middle third: +0.8 (n 33 against 43)
  - not running, advanced, ahead in the fight (top third, above -0.01): -2.3 (n 29 against 30)
  - running, fought, behind in the fight (lowest third, -0.11 or less): -0.0 (n 13 against 78)
  - running, fought, middle third: -0.2 (n 21 against 43)
  - running, fought, ahead in the fight (top third, above -0.01): +3.5 (n 27 against 30)
  - not running, held, behind in the fight (lowest third, -0.11 or less): +0.2 (n 21 against 78)
  - not running, held, middle third: -0.6 (n 15 against 43)
  - not running, held, ahead in the fight (top third, above -0.01): +2.8 (n 24 against 30)
  - running, held, behind in the fight (lowest third, -0.11 or less): too few yet (n 1 against 78; means 0.0 against -1.1)
  - running, held, middle third: -1.6 (n 13 against 43)
  - running, held, ahead in the fight (top third, above -0.01): +2.2 (n 19 against 30)
  - running, fell back, behind in the fight (lowest third, -0.11 or less): too few yet (n 9 against 78; means 2.8 against -1.1)
  - running, fell back, middle third: +0.9 (n 14 against 43)
  - running, fell back, ahead in the fight (top third, above -0.01): +6.4 (n 10 against 30)
  - not running, to the spawn, behind in the fight (lowest third, -0.11 or less): too few yet (n 6 against 78; means 0.1 against -1.1)
  - not running, to the spawn, middle third: too few yet (n 1 against 43; means -0.2 against -0.3)
  - not running, to the spawn, ahead in the fight (top third, above -0.01): too few yet (n 4 against 30; means -2.7 against -2.6)
  By snare matchup (movepower.py: enemy snare power of the live players minus own speed power; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - not running, fell back, little enemy snare for own speed (lowest third, -18 or less): +0.7 (n 39 against 36)
  - not running, fell back, middle third: -0.1 (n 37 against 55)
  - not running, fell back, a lot of enemy snare for own speed (top third, above +10): -2.7 (n 27 against 60)
  - running, advanced, little enemy snare for own speed (lowest third, -18 or less): +4.6 (n 40 against 36)
  - running, advanced, middle third: +0.2 (n 33 against 55)
  - running, advanced, a lot of enemy snare for own speed (top third, above +10): -0.6 (n 24 against 60)
  - not running, advanced, little enemy snare for own speed (lowest third, -18 or less): -0.4 (n 37 against 36)
  - not running, advanced, middle third: -1.4 (n 25 against 55)
  - not running, advanced, a lot of enemy snare for own speed (top third, above +10): +0.3 (n 26 against 60)
  - running, fought, little enemy snare for own speed (lowest third, -18 or less): +3.3 (n 18 against 36)
  - running, fought, middle third: +4.7 (n 17 against 55)
  - running, fought, a lot of enemy snare for own speed (top third, above +10): -2.3 (n 26 against 60)
  - not running, held, little enemy snare for own speed (lowest third, -18 or less): +3.5 (n 12 against 36)
  - not running, held, middle third: -0.0 (n 25 against 55)
  - not running, held, a lot of enemy snare for own speed (top third, above +10): -0.3 (n 23 against 60)
  - running, held, little enemy snare for own speed (lowest third, -18 or less): +2.0 (n 15 against 36)
  - running, held, middle third: too few yet (n 7 against 55; means 5.2 against -0.7)
  - running, held, a lot of enemy snare for own speed (top third, above +10): -3.8 (n 11 against 60)
  - running, fell back, little enemy snare for own speed (lowest third, -18 or less): +5.8 (n 15 against 36)
  - running, fell back, middle third: too few yet (n 9 against 55; means -1.5 against -0.7)
  - running, fell back, a lot of enemy snare for own speed (top third, above +10): too few yet (n 9 against 60; means 5.8 against -0.1)
  - not running, to the spawn, little enemy snare for own speed (lowest third, -18 or less): too few yet (n 3 against 36; means -4.4 against -3.7)
  - not running, to the spawn, middle third: too few yet (n 2 against 55; means 1.1 against -0.7)
  - not running, to the spawn, a lot of enemy snare for own speed (top third, above +10): too few yet (n 6 against 60; means 0.1 against -0.1)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - not running, fell back, Corrupted Isle: +1.9 (n 17 against 26)
  - not running, fell back, Isle of Jade: -8.4 (n 14 against 27)
  - not running, fell back, Isle of Meditation: +0.2 (n 16 against 30)
  - not running, fell back, Isle of Solitude: +5.6 (n 11 against 14)
  - not running, fell back, Uncharted Isle: -1.9 (n 18 against 18)
  - running, advanced, Corrupted Isle: +8.1 (n 16 against 26)
  - running, advanced, Isle of Meditation: +6.4 (n 24 against 30)
  - running, advanced, Isle of Solitude: +1.6 (n 16 against 14)
  - not running, advanced, Corrupted Isle: -2.0 (n 22 against 26)
  - not running, advanced, Isle of Meditation: +1.5 (n 16 against 30)
  - not running, advanced, Isle of Solitude: +3.2 (n 13 against 14)
  - not running, advanced, Uncharted Isle: +0.9 (n 15 against 18)
  - running, fought, Isle of Meditation: +2.0 (n 13 against 30)
  - not running, held, Isle of Jade: -0.3 (n 13 against 27)
  - not running, held, Isle of Solitude: +2.9 (n 12 against 14)
  - running, held, Isle of Jade: -2.9 (n 13 against 27)

**enemy pickup** (2215 decisions, 174 matches; usual: held, advanced)
- already running, advanced (n 305): -2.0 [-5.1, +1.0]; in the 30 s before: +2.8 [-0.5, +6.4]
- held, fell back (n 294): -2.8 [-7.5, +1.2]; in the 30 s before: +1.6 [-1.8, +5.8]
- already running, fell back (n 222): -1.2 [-4.1, +2.1]; in the 30 s before: +3.5 [+0.1, +7.1] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, fought (n 196): -1.6 [-5.3, +0.8]; in the 30 s before: +1.3 [-1.5, +3.5]
- already running, fought (n 176): -2.2 [-5.7, +1.6]; in the 30 s before: +3.2 [-0.1, +6.6]
- ran, fell back (n 163): -1.2 [-4.1, +1.7]; in the 30 s before: +1.8 [-1.7, +5.4]
- ran, advanced (n 145): -1.0 [-4.4, +2.8]; in the 30 s before: +1.4 [-1.7, +4.7]
- already running, held (n 95): -0.3 [-3.6, +3.6]; in the 30 s before: +1.6 [-2.5, +5.4]
- ran, fought (n 94): -1.4 [-4.2, +1.6]; in the 30 s before: +1.8 [-1.4, +4.7]
- held, held (n 88): +2.0 [-2.3, +5.9]; in the 30 s before: +2.2 [-1.1, +5.4]
- ran, held (n 69): +0.3 [-4.1, +5.0]; in the 30 s before: +3.3 [-1.4, +7.9]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - already running, advanced, behind in the fight (lowest third, -0.01 or less): +2.4 (n 81 against 95)
  - already running, advanced, middle third: -3.8 (n 127 against 128)
  - already running, advanced, ahead in the fight (top third, above +0.02): -6.0 (n 97 against 145)
  - held, fell back, behind in the fight (lowest third, -0.01 or less): -1.0 (n 128 against 95)
  - held, fell back, middle third: -1.0 (n 86 against 128)
  - held, fell back, ahead in the fight (top third, above +0.02): -5.4 (n 80 against 145)
  - already running, fell back, behind in the fight (lowest third, -0.01 or less): +4.2 (n 106 against 95)
  - already running, fell back, middle third: -4.4 (n 62 against 128)
  - already running, fell back, ahead in the fight (top third, above +0.02): -4.7 (n 54 against 145)
  - held, fought, behind in the fight (lowest third, -0.01 or less): +0.7 (n 61 against 95)
  - held, fought, middle third: -3.7 (n 31 against 128)
  - held, fought, ahead in the fight (top third, above +0.02): -3.7 (n 104 against 145)
  - already running, fought, behind in the fight (lowest third, -0.01 or less): +0.9 (n 62 against 95)
  - already running, fought, middle third: -2.3 (n 36 against 128)
  - already running, fought, ahead in the fight (top third, above +0.02): -6.1 (n 78 against 145)
  - ran, fell back, behind in the fight (lowest third, -0.01 or less): +4.3 (n 74 against 95)
  - ran, fell back, middle third: -2.3 (n 47 against 128)
  - ran, fell back, ahead in the fight (top third, above +0.02): -4.7 (n 42 against 145)
  - ran, advanced, behind in the fight (lowest third, -0.01 or less): +5.1 (n 48 against 95)
  - ran, advanced, middle third: -2.5 (n 54 against 128)
  - ran, advanced, ahead in the fight (top third, above +0.02): -4.3 (n 43 against 145)
  - already running, held, behind in the fight (lowest third, -0.01 or less): +6.2 (n 26 against 95)
  - already running, held, middle third: -2.1 (n 48 against 128)
  - already running, held, ahead in the fight (top third, above +0.02): -4.7 (n 21 against 145)
  - ran, fought, behind in the fight (lowest third, -0.01 or less): +6.1 (n 31 against 95)
  - ran, fought, middle third: -9.1 (n 24 against 128)
  - ran, fought, ahead in the fight (top third, above +0.02): -3.0 (n 39 against 145)
  - held, held, behind in the fight (lowest third, -0.01 or less): +3.8 (n 21 against 95)
  - held, held, middle third: +3.6 (n 42 against 128)
  - held, held, ahead in the fight (top third, above +0.02): -1.1 (n 25 against 145)
  - ran, held, behind in the fight (lowest third, -0.01 or less): +7.2 (n 18 against 95)
  - ran, held, middle third: -0.8 (n 42 against 128)
  - ran, held, ahead in the fight (top third, above +0.02): too few yet (n 9 against 145; means -4.7 against 5.3)
  By snare matchup (movepower.py: enemy snare power of the live players minus own speed power; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - already running, advanced, little enemy snare for own speed (lowest third, -20 or less): -2.9 (n 139 against 87)
  - already running, advanced, middle third: -4.9 (n 80 against 175)
  - already running, advanced, a lot of enemy snare for own speed (top third, above +13): -0.4 (n 86 against 106)
  - held, fell back, little enemy snare for own speed (lowest third, -20 or less): -3.9 (n 88 against 87)
  - held, fell back, middle third: -3.1 (n 105 against 175)
  - held, fell back, a lot of enemy snare for own speed (top third, above +13): -3.8 (n 101 against 106)
  - already running, fell back, little enemy snare for own speed (lowest third, -20 or less): -1.2 (n 98 against 87)
  - already running, fell back, middle third: -2.7 (n 56 against 175)
  - already running, fell back, a lot of enemy snare for own speed (top third, above +13): -2.2 (n 68 against 106)
  - held, fought, little enemy snare for own speed (lowest third, -20 or less): -2.1 (n 61 against 87)
  - held, fought, middle third: +0.3 (n 71 against 175)
  - held, fought, a lot of enemy snare for own speed (top third, above +13): -5.3 (n 64 against 106)
  - already running, fought, little enemy snare for own speed (lowest third, -20 or less): -3.6 (n 59 against 87)
  - already running, fought, middle third: -3.4 (n 54 against 175)
  - already running, fought, a lot of enemy snare for own speed (top third, above +13): -2.6 (n 63 against 106)
  - ran, fell back, little enemy snare for own speed (lowest third, -20 or less): +2.7 (n 48 against 87)
  - ran, fell back, middle third: -2.2 (n 53 against 175)
  - ran, fell back, a lot of enemy snare for own speed (top third, above +13): -4.0 (n 62 against 106)
  - ran, advanced, little enemy snare for own speed (lowest third, -20 or less): +1.4 (n 46 against 87)
  - ran, advanced, middle third: -2.3 (n 42 against 175)
  - ran, advanced, a lot of enemy snare for own speed (top third, above +13): -2.2 (n 57 against 106)
  - already running, held, little enemy snare for own speed (lowest third, -20 or less): -0.7 (n 41 against 87)
  - already running, held, middle third: +1.1 (n 20 against 175)
  - already running, held, a lot of enemy snare for own speed (top third, above +13): -1.4 (n 34 against 106)
  - ran, fought, little enemy snare for own speed (lowest third, -20 or less): -2.6 (n 24 against 87)
  - ran, fought, middle third: -0.6 (n 32 against 175)
  - ran, fought, a lot of enemy snare for own speed (top third, above +13): -2.7 (n 38 against 106)
  - held, held, little enemy snare for own speed (lowest third, -20 or less): -1.2 (n 30 against 87)
  - held, held, middle third: +5.6 (n 30 against 175)
  - held, held, a lot of enemy snare for own speed (top third, above +13): +2.8 (n 28 against 106)
  - ran, held, little enemy snare for own speed (lowest third, -20 or less): +2.5 (n 19 against 87)
  - ran, held, middle third: +9.3 (n 22 against 175)
  - ran, held, a lot of enemy snare for own speed (top third, above +13): -9.9 (n 28 against 106)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - already running, advanced, Corrupted Isle: -2.8 (n 59 against 103)
  - already running, advanced, Imperial Isle: -4.2 (n 27 against 15)
  - already running, advanced, Isle of Jade: +0.8 (n 16 against 43)
  - already running, advanced, Isle of Meditation: -5.7 (n 57 against 46)
  - already running, advanced, Isle of Solitude: +1.8 (n 30 against 24)
  - already running, advanced, Isle of Weeping Stone: -2.8 (n 24 against 16)
  - already running, advanced, Uncharted Isle: -5.4 (n 61 against 85)
  - held, fell back, Corrupted Isle: -6.1 (n 70 against 103)
  - held, fell back, Imperial Isle: +0.9 (n 14 against 15)
  - held, fell back, Isle of Jade: +2.0 (n 32 against 43)
  - held, fell back, Isle of Meditation: -6.2 (n 51 against 46)
  - held, fell back, Isle of Solitude: +1.6 (n 27 against 24)
  - held, fell back, Isle of Weeping Stone: +1.5 (n 13 against 16)
  - held, fell back, Nomad's Isle: +1.1 (n 12 against 13)
  - held, fell back, Uncharted Isle: -9.5 (n 58 against 85)
  - already running, fell back, Corrupted Isle: -0.4 (n 38 against 103)
  - already running, fell back, Imperial Isle: -3.0 (n 15 against 15)
  - already running, fell back, Isle of Jade: +6.2 (n 11 against 43)
  - already running, fell back, Isle of Meditation: +0.3 (n 26 against 46)
  - already running, fell back, Isle of Solitude: -3.9 (n 22 against 24)
  - already running, fell back, Isle of Weeping Stone: +1.4 (n 15 against 16)
  - already running, fell back, Nomad's Isle: -0.5 (n 10 against 13)
  - already running, fell back, Uncharted Isle: -7.3 (n 73 against 85)
  - held, fought, Corrupted Isle: +0.0 (n 38 against 103)
  - held, fought, Isle of Jade: +4.9 (n 17 against 43)
  - held, fought, Isle of Meditation: -2.5 (n 33 against 46)
  - held, fought, Isle of Solitude: -5.8 (n 15 against 24)
  - held, fought, Nomad's Isle: -1.7 (n 24 against 13)
  - held, fought, Uncharted Isle: -7.0 (n 32 against 85)
  - already running, fought, Corrupted Isle: -5.0 (n 33 against 103)
  - already running, fought, Imperial Isle: -1.1 (n 18 against 15)
  - already running, fought, Isle of Meditation: -6.7 (n 26 against 46)
  - already running, fought, Isle of Solitude: -3.6 (n 22 against 24)
  - already running, fought, Isle of Weeping Stone: -1.7 (n 13 against 16)
  - already running, fought, Nomad's Isle: +1.3 (n 22 against 13)
  - already running, fought, Uncharted Isle: -8.1 (n 17 against 85)
  - ran, fell back, Corrupted Isle: +2.0 (n 28 against 103)
  - ran, fell back, Imperial Isle: -3.0 (n 16 against 15)
  - ran, fell back, Isle of Jade: +1.0 (n 13 against 43)
  - ran, fell back, Isle of Meditation: -2.3 (n 17 against 46)
  - ran, fell back, Isle of Solitude: -6.6 (n 16 against 24)
  - ran, fell back, Isle of Weeping Stone: +4.8 (n 14 against 16)
  - ran, fell back, Uncharted Isle: -3.8 (n 41 against 85)
  - ran, advanced, Corrupted Isle: -8.2 (n 14 against 103)
  - ran, advanced, Imperial Isle: -6.1 (n 22 against 15)
  - ran, advanced, Isle of Jade: +6.4 (n 24 against 43)
  - ran, advanced, Isle of Meditation: +2.7 (n 16 against 46)
  - ran, advanced, Isle of Solitude: -3.2 (n 12 against 24)
  - ran, advanced, Isle of Weeping Stone: +11.5 (n 10 against 16)
  - ran, advanced, Uncharted Isle: -4.8 (n 36 against 85)
  - already running, held, Isle of Jade: +5.7 (n 14 against 43)
  - already running, held, Isle of Meditation: -6.1 (n 11 against 46)
  - already running, held, Isle of Solitude: -0.4 (n 11 against 24)
  - already running, held, Uncharted Isle: -1.2 (n 17 against 85)
  - ran, fought, Corrupted Isle: +3.1 (n 11 against 103)
  - ran, fought, Imperial Isle: -2.0 (n 19 against 15)
  - ran, fought, Isle of Meditation: +0.9 (n 13 against 46)
  - ran, fought, Nomad's Isle: -2.1 (n 10 against 13)
  - held, held, Isle of Jade: +11.7 (n 29 against 43)
  - held, held, Nomad's Isle: +2.5 (n 12 against 13)
  - ran, held, Imperial Isle: -2.3 (n 10 against 15)
  - ran, held, Isle of Jade: +7.0 (n 21 against 43)
  - ran, held, Uncharted Isle: -7.2 (n 11 against 85)

**late game** (50 decisions, 25 matches; usual: 2 to 3 at the enemy Lord)
- 0 to 1 at the enemy Lord (n 21): -7.3 [-22.2, +9.8]; in the 30 s before: +2.1 [-3.2, +6.1]
- 4+ at the enemy Lord (n 7): -4.9 [-14.6, +5.8]; in the 30 s before: -0.3 [-5.3, +2.7]

**power play** (1497 decisions, 181 matches; usual: pushed, advanced)
- pushed, fought (n 303): +0.3 [-1.1, +1.7]; in the 30 s before: -0.8 [-1.8, +0.0]
- held, fought (n 181): -0.0 [-1.5, +1.5]; in the 30 s before: -0.3 [-1.4, +0.8]
- pushed, fell back (n 175): +1.0 [-0.3, +2.2]; in the 30 s before: -1.0 [-1.8, -0.1] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, fell back (n 150): -1.0 [-2.4, +0.3]; in the 30 s before: -1.3 [-2.4, -0.0] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, advanced (n 115): +0.4 [-1.2, +1.8]; in the 30 s before: +0.0 [-1.2, +1.5]
- pushed, held (n 54): +3.0 [+0.2, +5.0] CLEAR; in the 30 s before: -0.3 [-2.0, +1.0]
- held, held (n 50): -0.8 [-2.4, +0.7]; in the 30 s before: +1.0 [-0.6, +2.9]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - pushed, fought, behind in the fight (lowest third, +0.00 or less): +2.7 (n 88 against 139)
  - pushed, fought, middle third: -2.5 (n 79 against 178)
  - pushed, fought, ahead in the fight (top third, above +0.08): -1.1 (n 136 against 152)
  - held, fought, behind in the fight (lowest third, +0.00 or less): +1.6 (n 65 against 139)
  - held, fought, middle third: -0.9 (n 52 against 178)
  - held, fought, ahead in the fight (top third, above +0.08): -3.1 (n 64 against 152)
  - pushed, fell back, behind in the fight (lowest third, +0.00 or less): +2.2 (n 63 against 139)
  - pushed, fell back, middle third: -0.0 (n 56 against 178)
  - pushed, fell back, ahead in the fight (top third, above +0.08): -0.5 (n 56 against 152)
  - held, fell back, behind in the fight (lowest third, +0.00 or less): -2.0 (n 71 against 139)
  - held, fell back, middle third: +0.2 (n 47 against 178)
  - held, fell back, ahead in the fight (top third, above +0.08): -1.3 (n 32 against 152)
  - held, advanced, behind in the fight (lowest third, +0.00 or less): +1.4 (n 40 against 139)
  - held, advanced, middle third: -2.0 (n 43 against 178)
  - held, advanced, ahead in the fight (top third, above +0.08): +2.5 (n 32 against 152)
  - pushed, held, behind in the fight (lowest third, +0.00 or less): +2.0 (n 21 against 139)
  - pushed, held, middle third: +3.5 (n 20 against 178)
  - pushed, held, ahead in the fight (top third, above +0.08): +3.5 (n 13 against 152)
  - held, held, behind in the fight (lowest third, +0.00 or less): +1.1 (n 21 against 139)
  - held, held, middle third: -2.3 (n 18 against 178)
  - held, held, ahead in the fight (top third, above +0.08): -5.0 (n 11 against 152)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - pushed, fought, Corrupted Isle: +0.3 (n 52 against 99)
  - pushed, fought, Druid's Isle: +3.3 (n 18 against 18)
  - pushed, fought, Imperial Isle: +4.7 (n 14 against 29)
  - pushed, fought, Isle of Jade: +4.2 (n 30 against 41)
  - pushed, fought, Isle of Meditation: -2.6 (n 60 against 95)
  - pushed, fought, Isle of Solitude: -2.7 (n 28 against 44)
  - pushed, fought, Isle of Weeping Stone: -1.3 (n 12 against 31)
  - pushed, fought, Nomad's Isle: +0.7 (n 30 against 14)
  - pushed, fought, Uncharted Isle: +0.4 (n 39 against 70)
  - held, fought, Corrupted Isle: +2.1 (n 30 against 99)
  - held, fought, Druid's Isle: +0.0 (n 14 against 18)
  - held, fought, Imperial Isle: +2.1 (n 13 against 29)
  - held, fought, Isle of Jade: -2.9 (n 18 against 41)
  - held, fought, Isle of Meditation: -0.7 (n 24 against 95)
  - held, fought, Isle of Solitude: -3.8 (n 21 against 44)
  - held, fought, Nomad's Isle: +3.0 (n 27 against 14)
  - held, fought, Uncharted Isle: -4.5 (n 15 against 70)
  - pushed, fell back, Corrupted Isle: -0.4 (n 30 against 99)
  - pushed, fell back, Imperial Isle: +2.0 (n 11 against 29)
  - pushed, fell back, Isle of Jade: +6.8 (n 13 against 41)
  - pushed, fell back, Isle of Meditation: +1.0 (n 24 against 95)
  - pushed, fell back, Isle of Solitude: +1.6 (n 24 against 44)
  - pushed, fell back, Isle of Weeping Stone: +3.1 (n 13 against 31)
  - pushed, fell back, Nomad's Isle: -1.3 (n 10 against 14)
  - pushed, fell back, Uncharted Isle: -3.5 (n 30 against 70)
  - held, fell back, Corrupted Isle: -2.5 (n 25 against 99)
  - held, fell back, Imperial Isle: +5.4 (n 10 against 29)
  - held, fell back, Isle of Jade: -2.0 (n 11 against 41)
  - held, fell back, Isle of Meditation: -1.8 (n 28 against 95)
  - held, fell back, Isle of Solitude: -6.6 (n 15 against 44)
  - held, fell back, Nomad's Isle: +0.4 (n 14 against 14)
  - held, fell back, Uncharted Isle: -3.6 (n 23 against 70)
  - held, advanced, Corrupted Isle: +1.2 (n 20 against 99)
  - held, advanced, Imperial Isle: +2.1 (n 13 against 29)
  - held, advanced, Isle of Jade: -2.0 (n 12 against 41)
  - held, advanced, Isle of Meditation: -1.0 (n 27 against 95)
  - held, advanced, Uncharted Isle: -0.6 (n 17 against 70)
  - pushed, held, Uncharted Isle: -1.1 (n 11 against 70)
  - held, held, Druid's Isle: -0.4 (n 12 against 18)

**runner choice** (1547 decisions, 168 matches; usual: mesmer)
- monk (n 277): -0.8 [-2.5, +0.6]; in the 30 s before: +1.0 [-0.0, +2.2]
- dervish (n 260): -0.5 [-2.0, +1.1]; in the 30 s before: +0.4 [-0.6, +1.4]
- ritualist (n 211): +0.0 [-1.7, +2.0]; in the 30 s before: -0.2 [-1.1, +1.1]
- warrior (n 187): -1.8 [-3.7, -0.0] CLEAR; in the 30 s before: +0.8 [-0.3, +1.9]
- elementalist (n 140): -1.8 [-3.3, -0.2] CLEAR; in the 30 s before: +2.1 [+0.5, +3.3] ALREADY DIFFERENT BEFORE: partly who chooses it
- necromancer (n 59): +3.1 [-0.8, +6.1]; in the 30 s before: -1.6 [-2.8, +0.5]
- ranger (n 33): -2.0 [-7.7, +3.2]; in the 30 s before: +1.8 [-0.1, +3.9]
- assassin (n 19): -9.6 [-14.7, -4.2] CLEAR; in the 30 s before: +3.2 [+0.7, +6.2] ALREADY DIFFERENT BEFORE: partly who chooses it
- paragon (n 16): -3.1 [-6.8, -0.3] CLEAR; in the 30 s before: +4.4 [-1.1, +9.6]
  By snare matchup (movepower.py: enemy snare power of the live players minus own speed power; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - monk, little enemy snare for own speed (lowest third, -26 or less): -2.5 (n 95 against 94)
  - monk, middle third: +1.8 (n 108 against 100)
  - monk, a lot of enemy snare for own speed (top third, above +11): -0.9 (n 74 against 151)
  - dervish, little enemy snare for own speed (lowest third, -26 or less): +0.3 (n 73 against 94)
  - dervish, middle third: -0.4 (n 93 against 100)
  - dervish, a lot of enemy snare for own speed (top third, above +11): -0.4 (n 94 against 151)
  - ritualist, little enemy snare for own speed (lowest third, -26 or less): -1.6 (n 80 against 94)
  - ritualist, middle third: -0.2 (n 69 against 100)
  - ritualist, a lot of enemy snare for own speed (top third, above +11): +1.8 (n 62 against 151)
  - warrior, little enemy snare for own speed (lowest third, -26 or less): -1.1 (n 63 against 94)
  - warrior, middle third: -0.9 (n 76 against 100)
  - warrior, a lot of enemy snare for own speed (top third, above +11): -1.7 (n 48 against 151)
  - elementalist, little enemy snare for own speed (lowest third, -26 or less): -2.2 (n 54 against 94)
  - elementalist, middle third: -2.1 (n 40 against 100)
  - elementalist, a lot of enemy snare for own speed (top third, above +11): +0.5 (n 46 against 151)
  - necromancer, little enemy snare for own speed (lowest third, -26 or less): -0.2 (n 33 against 94)
  - necromancer, middle third: too few yet (n 6 against 100; means 10.1 against 0.4)
  - necromancer, a lot of enemy snare for own speed (top third, above +11): +3.7 (n 20 against 151)
  - ranger, little enemy snare for own speed (lowest third, -26 or less): -5.2 (n 13 against 94)
  - ranger, middle third: too few yet (n 9 against 100; means -0.3 against 0.4)
  - ranger, a lot of enemy snare for own speed (top third, above +11): +0.6 (n 11 against 151)
  - assassin, little enemy snare for own speed (lowest third, -26 or less): too few yet (n 8 against 94; means -10.2 against 1.0)
  - assassin, middle third: too few yet (n 3 against 100; means 1.0 against 0.4)
  - assassin, a lot of enemy snare for own speed (top third, above +11): too few yet (n 8 against 151; means -7.7 against 0.5)
  - paragon, little enemy snare for own speed (lowest third, -26 or less): too few yet (n 5 against 94; means 1.8 against 1.0)
  - paragon, middle third: too few yet (n 9 against 100; means -0.8 against 0.4)
  - paragon, a lot of enemy snare for own speed (top third, above +11): too few yet (n 2 against 151; means -12.2 against 0.5)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - monk, Corrupted Isle: +3.1 (n 63 against 47)
  - monk, Druid's Isle: -1.0 (n 42 against 12)
  - monk, Isle of Jade: +1.3 (n 28 against 17)
  - monk, Isle of Meditation: -3.5 (n 40 against 62)
  - monk, Isle of Solitude: -0.7 (n 37 against 18)
  - monk, Isle of Weeping Stone: -6.1 (n 14 against 29)
  - monk, Nomad's Isle: -0.7 (n 16 against 27)
  - monk, Uncharted Isle: -0.3 (n 18 against 78)
  - dervish, Corrupted Isle: +5.1 (n 39 against 47)
  - dervish, Druid's Isle: -1.9 (n 10 against 12)
  - dervish, Imperial Isle: -1.1 (n 28 against 48)
  - dervish, Isle of Jade: -3.7 (n 12 against 17)
  - dervish, Isle of Meditation: -2.0 (n 45 against 62)
  - dervish, Isle of Solitude: -2.7 (n 27 against 18)
  - dervish, Isle of Weeping Stone: +2.9 (n 16 against 29)
  - dervish, Uncharted Isle: -0.6 (n 53 against 78)
  - ritualist, Corrupted Isle: +1.3 (n 30 against 47)
  - ritualist, Isle of Jade: +1.2 (n 19 against 17)
  - ritualist, Isle of Meditation: -2.1 (n 49 against 62)
  - ritualist, Isle of Solitude: +0.1 (n 39 against 18)
  - ritualist, Isle of Weeping Stone: -2.7 (n 23 against 29)
  - ritualist, Uncharted Isle: +3.9 (n 39 against 78)
  - warrior, Corrupted Isle: +5.3 (n 33 against 47)
  - warrior, Imperial Isle: -4.1 (n 20 against 48)
  - warrior, Isle of Jade: +3.1 (n 21 against 17)
  - warrior, Isle of Meditation: -2.8 (n 26 against 62)
  - warrior, Isle of Solitude: -4.9 (n 14 against 18)
  - warrior, Isle of Weeping Stone: -0.6 (n 10 against 29)
  - warrior, Nomad's Isle: -4.9 (n 14 against 27)
  - warrior, Uncharted Isle: +0.2 (n 36 against 78)
  - elementalist, Corrupted Isle: -0.4 (n 15 against 47)
  - elementalist, Imperial Isle: -1.1 (n 24 against 48)
  - elementalist, Isle of Jade: +0.9 (n 16 against 17)
  - elementalist, Isle of Meditation: +0.3 (n 37 against 62)
  - elementalist, Uncharted Isle: -4.5 (n 20 against 78)
  - necromancer, Isle of Solitude: -2.0 (n 13 against 18)
  - necromancer, Uncharted Isle: +2.4 (n 18 against 78)

**split in base** (334 decisions, 112 matches; usual: defended without a collapse)
- collapsed (n 137): -4.0 [-7.3, -0.7] CLEAR; in the 30 s before: +0.1 [-1.0, +1.4]
- missed (n 38): +0.0 [-5.0, +4.5]; in the 30 s before: +0.9 [-1.3, +3.6]
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - collapsed, Corrupted Isle: -2.9 (n 27 against 29)
  - collapsed, Isle of Meditation: -3.6 (n 30 against 19)
  - collapsed, Isle of Solitude: -4.8 (n 15 against 50)
  - collapsed, Uncharted Isle: -6.9 (n 14 against 32)

**split or stay** (6186 decisions, 181 matches; usual: stayed)
- split (n 599): +0.1 [-0.7, +0.9]; in the 30 s before: +0.3 [-0.2, +0.9]
  By snare matchup (movepower.py: enemy snare power of the live players minus own speed power; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - split, little enemy snare for own speed (lowest third, -24 or less): +0.3 (n 234 against 1830)
  - split, middle third: +0.7 (n 177 against 1885)
  - split, a lot of enemy snare for own speed (top third, above +10): -0.9 (n 188 against 1872)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - split, Corrupted Isle: +0.5 (n 117 against 826)
  - split, Druid's Isle: -2.3 (n 15 against 401)
  - split, Frozen Isle: -3.1 (n 10 against 81)
  - split, Imperial Isle: -0.6 (n 36 against 321)
  - split, Isle of Jade: -0.6 (n 37 against 860)
  - split, Isle of Meditation: -0.3 (n 99 against 908)
  - split, Isle of Solitude: +2.2 (n 81 against 592)
  - split, Isle of Weeping Stone: -0.1 (n 37 against 232)
  - split, Nomad's Isle: +0.0 (n 39 against 361)
  - split, Uncharted Isle: -1.1 (n 110 against 747)

**Collapses on a split: time away and its cost** (`S32`; per collapse, averages; main = what the main fight lost while the collapsers were away)

| Group | Cases | Away (median s) | Split killed | Collapser died | Own deaths at main | Enemy deaths at main | Flag lead change | DP change | Win change |
|---|---|---|---|---|---|---|---|---|---|
| all | 151 | 22 | 31 | 14 | 0.64 | 0.41 | +0.1 | -4.4 | -2.1 |
| away under 30 s | 87 | 6 | 23 | 1 | 0.06 | 0.15 | +0.9 | -0.0 | -1.7 |
| away 30 to 60 s | 25 | 43 | 3 | 3 | 0.72 | 0.36 | -9.6 | -10.0 | -0.5 |
| away 60 s or more | 39 | 102 | 5 | 10 | 1.9 | 1.03 | +4.5 | -10.4 | -4.2 |
| before 20:00 | 126 | 22 | 23 | 10 | 0.49 | 0.33 | -0.3 | -5.6 | -1.8 |
| from 20:00 | 25 | 24 | 8 | 4 | 1.4 | 0.84 | +1.7 | +1.8 | -3.6 |
| split member killed | 31 | 16 | 31 | 1 | 0.06 | 1.19 | +0.8 | +0.4 | +3.7 |
| no kill | 120 | 25.5 | 0 | 13 | 0.79 | 0.21 | -0.1 | -5.6 | -3.7 |

**Leverage: where the choice matters most** (share of the spread in win-chance change explained by the choice beyond the situation; range = best minus worst choice, in points)

- boost clock (637): choice explains 2.3% (situation 5.9%); range 5.5 points, best running, fell back, worst not running, fell back
- split in base (334): choice explains 1.8% (situation 2.6%); range 4.2 points, best missed, worst collapsed
- after wipe (399): choice explains 1.5% (situation 6.7%); range 4.2 points, best pushed the pit, worst took the flag
- late game (50): choice explains 1.5% (situation 30.8%); range 7.3 points, best 2 to 3 at the enemy Lord, worst 0 to 1 at the enemy Lord
- runner choice (1547): choice explains 1.0% (situation 1.9%); range 12.0 points, best necromancer, worst assassin
- enemy pickup (2215): choice explains 0.7% (situation 2.6%); range 5.0 points, best held, held, worst held, fell back
- power play (1497): choice explains 0.5% (situation 2.1%); range 4.0 points, best pushed, held, worst held, fell back
- split or stay (6186): choice explains 0.0% (situation 0.8%); range 0.1 points, best split, worst stayed

**Behaviour clusters: what teams actually did** (each decision's response grouped by what every player did in the next 20 s; UNNAMED = a group no single named choice covers: a response for Denning to name or reject)

*after wipe* (2 groups, separation 0.32):
- n 243: fought (midline, 2.0 of 8), fought (backline, 1.5 of 8), fought (frontline, 0.9 of 8), held (backline, 0.7 of 8); named as {'pushed the pit': 206, 'reset': 20, 'took the flag': 17}; win change -0.0
- n 156: advanced (midline, 2.5 of 8), advanced (backline, 2.5 of 8), advanced (frontline, 1.2 of 8); named as {'pushed the pit': 92, 'reset': 35, 'took the flag': 29}; win change 1.0 UNNAMED
*boost clock* (4 groups, separation 0.19):
- n 234: fought (midline, 2.3 of 8), fought (backline, 2.1 of 8), fought (frontline, 1.0 of 8); named as {'not running, fought': 95, 'running, fought': 39, 'not running, fell back': 29}; win change -0.5 UNNAMED
- n 177: held (backline, 1.4 of 8), fought (midline, 0.8 of 8), held (midline, 0.7 of 8), fought (frontline, 0.7 of 8); named as {'not running, held': 38, 'not running, fell back': 33, 'not running, fought': 32}; win change -0.8 UNNAMED
- n 129: advanced (midline, 2.1 of 8), advanced (backline, 2.0 of 8), advanced (frontline, 0.8 of 8), fought (midline, 0.5 of 8); named as {'running, advanced': 46, 'not running, advanced': 45, 'not running, fought': 9}; win change -0.9 UNNAMED
- n 100: fell back (midline, 2.1 of 8), fell back (backline, 1.9 of 8), fell back (frontline, 0.7 of 8); named as {'not running, fell back': 36, 'running, fell back': 15, 'not running, fought': 15}; win change -2.0 UNNAMED
*enemy pickup* (3 groups, separation 0.21):
- n 928: fought (midline, 2.0 of 8), fought (backline, 1.6 of 8), fought (frontline, 1.0 of 8), held (backline, 0.8 of 8); named as {'held, fought': 150, 'already running, fought': 131, 'held, advanced': 124}; win change -0.6 UNNAMED
- n 682: advanced (midline, 2.1 of 8), advanced (backline, 1.9 of 8), advanced (frontline, 0.9 of 8); named as {'held, advanced': 202, 'already running, advanced': 179, 'ran, advanced': 95}; win change 2.6 UNNAMED
- n 613: fell back (midline, 1.7 of 8), fell back (backline, 1.6 of 8), fell back (frontline, 0.7 of 8), held (backline, 0.5 of 8); named as {'held, fell back': 161, 'already running, fell back': 113, 'ran, fell back': 102}; win change -0.7 UNNAMED
*late game* (6 groups, separation 0.25):
- n 15: fought (midline, 2.3 of 8), fought (backline, 1.7 of 8), fought (frontline, 0.9 of 8), held (backline, 0.5 of 8); named as {'0 to 1 at the enemy Lord': 6, '4+ at the enemy Lord': 5, '2 to 3 at the enemy Lord': 4}; win change 5.6 UNNAMED
- n 14: fell back (backline, 2.0 of 8), fell back (midline, 1.6 of 8), fell back (frontline, 1.0 of 8), advanced (midline, 0.8 of 8); named as {'0 to 1 at the enemy Lord': 8, '2 to 3 at the enemy Lord': 6}; win change 1.5 UNNAMED
- n 11: advanced (backline, 1.9 of 8), advanced (midline, 1.4 of 8), advanced (frontline, 1.2 of 8), fought (backline, 0.9 of 8); named as {'2 to 3 at the enemy Lord': 7, '0 to 1 at the enemy Lord': 4}; win change -7.0
- n 4: held (backline, 2.8 of 8), advanced (midline, 1.0 of 8), held (midline, 1.0 of 8), held (frontline, 0.7 of 8); named as {'2 to 3 at the enemy Lord': 2, '0 to 1 at the enemy Lord': 2}; win change 0.3 UNNAMED
- n 4: advanced (midline, 4.8 of 8), advanced (backline, 1.0 of 8), held (midline, 0.5 of 8), fell back (backline, 0.5 of 8); named as {'4+ at the enemy Lord': 2, '2 to 3 at the enemy Lord': 2}; win change 0.7 UNNAMED
- n 2: died (backline, 4.0 of 8), died (frontline, 2.0 of 8), died (midline, 2.0 of 8); named as {'2 to 3 at the enemy Lord': 1, '0 to 1 at the enemy Lord': 1}; win change -0.1 UNNAMED
*power play* (2 groups, separation 0.27):
- n 1020: fought (midline, 1.8 of 8), fought (backline, 1.5 of 8), fought (frontline, 1.0 of 8), held (backline, 0.7 of 8); named as {'pushed, fought': 245, 'held, fought': 173, 'pushed, advanced': 151}; win change 0.7 UNNAMED
- n 480: advanced (midline, 2.3 of 8), advanced (backline, 2.3 of 8), advanced (frontline, 1.1 of 8); named as {'pushed, advanced': 318, 'pushed, fought': 58, 'pushed, fell back': 36}; win change 2.5
*runner choice* (3 groups, separation 0.21):
- n 576: fought (midline, 1.9 of 8), fought (backline, 1.8 of 8), fought (frontline, 1.0 of 8), held (backline, 0.7 of 8); named as {'mesmer': 120, 'monk': 106, 'dervish': 103}; win change 0.6 UNNAMED
- n 517: fell back (backline, 1.4 of 8), fell back (midline, 1.3 of 8), held (backline, 0.8 of 8), carrying (midline, 0.6 of 8); named as {'mesmer': 111, 'dervish': 91, 'warrior': 80}; win change -0.7 UNNAMED
- n 454: advanced (backline, 2.0 of 8), advanced (midline, 1.8 of 8), advanced (frontline, 0.8 of 8), carrying (midline, 0.7 of 8); named as {'mesmer': 114, 'monk': 97, 'dervish': 66}; win change 0.6 UNNAMED
*split in base* (3 groups, separation 0.19):
- n 144: fought (midline, 2.3 of 8), fought (backline, 1.4 of 8), fought (frontline, 0.9 of 8), held (backline, 0.7 of 8); named as {'defended without a collapse': 79, 'collapsed': 48, 'missed': 17}; win change 0.4 UNNAMED
- n 97: advanced (midline, 2.0 of 8), advanced (backline, 1.3 of 8), advanced (frontline, 0.7 of 8); named as {'defended without a collapse': 45, 'collapsed': 41, 'missed': 11}; win change 0.3 UNNAMED
- n 92: fell back (midline, 2.1 of 8), fell back (backline, 1.7 of 8), fell back (frontline, 0.8 of 8), fought (backline, 0.5 of 8); named as {'collapsed': 48, 'defended without a collapse': 34, 'missed': 10}; win change -1.7 UNNAMED
*split or stay* (3 groups, separation 0.24):
- n 2977: fought (midline, 2.3 of 8), fought (backline, 1.9 of 8), fought (frontline, 1.1 of 8), held (backline, 0.8 of 8); named as {'stayed': 2745, 'split': 232}; win change 0.2
- n 1833: fell back (midline, 1.4 of 8), fell back (backline, 1.4 of 8), held (backline, 0.7 of 8), fell back (frontline, 0.6 of 8); named as {'stayed': 1662, 'split': 171}; win change -0.6
- n 1376: advanced (midline, 2.2 of 8), advanced (backline, 2.0 of 8), advanced (frontline, 0.9 of 8); named as {'stayed': 1180, 'split': 196}; win change 0.2

## 8. What results and causes are worth

Win points for the team it happened to, from 181 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. Both against matched moments without the event (same minute and win chance). A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 504 | +3.4 | -0.0 to +6.5 | +2.2 | no |
| capture | 1440 | +1.3 | +0.9 to +1.8 | +1.4 | yes |
| capture: held longer | 1219 | +2.3 | +0.8 to +3.6 | +1.5 | yes |
| capture: overcapped within 10 s (Bounty, F36) | 221 | -3.8 | -11.1 to +3.0 | +1.0 | no |
| death (any) | 3486 | -7.6 | -8.8 to -6.5 | -4.7 | yes |
| death: against a spike build | 929 | -7.2 | -10.0 to -4.6 | -3.4 | yes |
| death: against other builds | 2557 | -7.8 | -9.3 to -6.4 | -5.1 | yes |
| death: back within 20 s | 606 | -5.8 | -8.3 to -3.4 | -3.0 | yes |
| death: down 20 to 60 s | 1256 | -7.2 | -8.8 to -5.6 | -3.8 | yes |
| death: down 60 s or more | 1624 | -8.7 | -10.3 to -7.0 | -5.9 | yes |
| death: healer | 1192 | -7.8 | -9.5 to -6.3 | -4.5 | yes |
| death: healer in own base or pit, back within 15 s (possibly deliberate; energy not tracked) | 82 | -3.1 | -4.7 to -1.0 | -0.6 | yes |
| death: healer, other | 1110 | -8.1 | -9.8 to -6.6 | -4.8 | yes |
| death: not a healer | 2294 | -7.6 | -8.8 to -6.4 | -4.7 | yes |
| footman lost (base NPC) | 529 | +1.2 | -0.6 to +3.2 | +0.5 | no |
| pit NPC lost (any): taken by a spike build | 295 | -3.6 | -5.8 to -1.5 | -1.2 | yes |
| pit NPC lost (any): taken by other builds | 1112 | -3.7 | -5.3 to -2.1 | -1.9 | yes |
| pit NPC lost: archer | 797 | -2.2 | -3.5 to -0.7 | -0.3 | yes |
| pit NPC lost: bodyguard | 194 | -5.0 | -7.0 to -3.2 | -2.3 | yes |
| pit NPC lost: knight | 416 | -6.1 | -7.9 to -4.3 | -4.4 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value. Context (strength, build skill counts, flag lead, morale, the clock) is left out: it describes the situation, it is not a cause to fix.

*deaths* (per 10 s in that state; result worth -7.6 points, base rate 1.5%):

- enemies within 1,500 7.5 to 8: result chance +3.0 points, worth -0.23 win points
- current health % 1 to 48.5: result chance +10.9 points, worth -0.83 win points
- allies within 1,500 0 to 0.5: result chance +1.9 points, worth -0.15 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.5 points, worth -0.19 win points

*kill conversion* (per burst, for the attacking team; result worth +7.6 points, base rate 29.6%):

- damage in the 2 s burst 506.5 to 839: result chance +24.6 points, worth +1.87 win points
- target's healers in range 0 to 0.5: result chance +28.7 points, worth +2.18 win points
- target health % when the burst started 0 to 39.5: result chance +23.7 points, worth +1.8 win points
- target's health ceiling 0.4 to 0.69: result chance +29.4 points, worth +2.24 win points
- a prot on the target 0.5 to 1: result chance -4.8 points, worth -0.37 win points

*npc loss* (per case, for the defending team; result worth -3.7 points, base rate 19.5%):

- damage on the pit NPCs in the last 5 s 398.5 to 1370: result chance +39.3 points, worth -1.47 win points
- own players in the pit 0 to 0.5: result chance +35.9 points, worth -1.34 win points
- own players alive outside the pit 0 to 0.5: result chance +18.3 points, worth -0.68 win points
- of which healers 0 to 0.5: result chance +17.5 points, worth -0.65 win points
- attackers' measured damage per second against a Lord (benchmarks) 1.9 to 12.25: result chance -9.8 points, worth +0.37 win points
- enemy players in the pit 7.5 to 8: result chance +7.6 points, worth -0.28 win points
- share of the attacking team's live players in the pit (OG comms: merge before pushing the pit) 0.94 to 1: result chance +5.6 points, worth -0.21 win points

## The TQs

Denning's four questions, each from the batch's matches. The why comes from forensics and events (every number placed against the same role or situation in every stored match); the different play comes only from measurement: the usual play's choice effects (usual.py), node models read again with the variable changed (models that never saw the match, changes priced in win points with values.py), options that were ready and unused, and benchmarks. Points = win-chance points.

## TQ 1. Behind on flags

*The biggest flag swing in the new matches: dR +63 -> -90 by 6:35.0.*

### Flag swing: dR v Team (73d36ead), 6:00.0 to 6:35.0
**Result**: dR's flag lead +63 s -> -90 s (-153 s). Stand: dR -> dR.
**Captures** (flag model: fastest possible answer after the enemy's capture):
**Runs** (each run: outcome, and what was done to the runner):
**Deaths in the window**: 6:00.0 dR Ritualist 2 (own pit, [4, 8]); 6:05.0 dR Monk 3 (own pit, [4, 8]); 6:20.0 dR Mes/A (own pit, [6, 8]); 6:24.0 dR Hammer A (own pit, [5, 8]); 6:28.0 dR Ranger (own pit, [4, 8]); 6:33.0 dR Hammer B (own pit, [3, 8])
- dR output in the 20 s before 6:00.0: 31.9 damage per second (below the 50th percentile for team (median 38.4, n 9019)), top target share 0.31, spikes 0
- Team output in the 20 s before 6:00.0: 88.6 damage per second (above the 90th percentile for team (median 38.4, n 9019)), top target share 0.26, spikes 0
**Why dR Ritualist 2 died at 6:00.0** (forensics):
  - Position: yes (in the last 3 s: nearest allied healer 1001, nearest enemy 71, allies in casting range 3.0, enemies 8.0; over the whole window the nearest enemy's median was 498)
  - Prots: no prots (0 from teammates, 0 self; 0 of 0 landed); damage 526 (55% attacks, 47% armor-ignoring), burst 301 in 2 s at 5:57.2; ready and in range but not used: dR Monk 3 Guardian, dR Monk 3 Shielding Hands, dR Monk 4 Guardian
  - Healers under interrupt pressure: yes (healers 3, interrupts_per_min 9.0, interrupted 3, casts 6, finished_share 0.5, dazed 0, knockdowns 0, hexes 3)
  - Damage off shield sets: usual (team share 0.26, a shield would have stopped about 90)
  - Own damage: usual (23.4 per second on [('Team Ranger', 197), ('Team 7 Monk', 126)]); enemy damage: high (89.2 per second)
  - Peel: partly (controlled, but an attacker was left free for 20.0 s) (1 of 3 attackers controlled; longest free 20.0 s)
  - Casting: interrupted far more than usual (casts 1, interrupted 1, cancelled 0, while_dazed 0)
**Why dR Monk 3 died at 6:05.0** (forensics):
  - Position: partly (in the last 3 s: nearest allied healer 1535, nearest enemy 86, allies in casting range 2.0, enemies 8.0; over the whole window the nearest enemy's median was 90)
  - Prots: late or interrupted (0 from teammates, 1 self; 1 of 1 landed); damage 484 (62% attacks, 22% armor-ignoring), burst 140 in 2 s at 5:59.6
  - Healers under interrupt pressure: yes (healers 3, interrupts_per_min 9.0, interrupted 3, casts 6, finished_share 0.5, dazed 0, knockdowns 0, hexes 3)
  - Damage off shield sets: usual (team share 0.28, a shield would have stopped about 115)
  - Own damage: no (14.9 per second on [('Team 7 Monk', 154), ('Team 8 Monk', 69)]); enemy damage: high (92.3 per second)
  - Peel: partly (controlled, but an attacker was left free for 20.0 s) (2 of 4 attackers controlled; longest free 20.0 s)
  - Casting: interrupted far more than usual (casts 2, interrupted 1, cancelled 0, while_dazed 0)
**After**: 6:37.0 dR Monk 4; 6:50.0 dR Ritualist 1
**Why, in short**: deaths in the window: dR 6.

**How it got there, from the node models** (step 4: each link read by the node's held-out model; the biggest pushes toward the result, against the variable's usual value over every trained moment; a variable that is another node's result is followed back to it):
- 6:00 flag swing: flag lead change over 60 s -32.4 s; pushed by flag lead now (s) 63 (usual 0): +12.8 s; morale, own minus enemy (discovery, approved) -335 (usual 0): +12.1 s; own team holds the stand 1 (usual 0): +4.9 s
*Fixes carried forward*: none worth half a win point at the result.

**A different play (measured)**

*The decisions in the swing* (usual.py: win-chance points over the decision's window, against the kind's most common choice):
- split or stay at 5:30 (main 8v8, flags +59 s, boost in 73, fight state -1.237): chose **stayed** (+0.0 [+0.0, +0.0] against the most common choice, stayed); in the 15 most similar decisions teams usually chose **stayed**; no choice of this kind did measurably better than the one made.

**Confidence**: low (the engine can't price an alternative here yet).

## TQ 2. A monk death

*The monk death that cost the most win chance in the new matches: NwAy v SKT (457b3a21), SKT Prot at 21:03 (backside, numbers [5, 5]); win chance -66.6 points from 10 s before to 30 s after.*

**Why** (forensics, against the same role in every stored match):
- Position: partly (in the last 3 s: nearest allied healer 1150, nearest enemy 223, allies in casting range 4.0, enemies 5.0; over the whole window the nearest enemy's median was 211)
- Prots: no prots (0 from teammates, 0 self; 0 of 0 landed); damage 314 (32% attacks, 71% armor-ignoring), burst 200 in 2 s at 20:47.2; knockdowns 1, knockdown immunity up for 0
- Healers under interrupt pressure: yes (healers 3, interrupts_per_min 6.0, interrupted 2, casts 16, finished_share 0.88, dazed 0, knockdowns 1, hexes 1)
- Damage off shield sets: usual (team share 0.33, a shield would have stopped about 98)
- Own damage: usual (39.6 per second on [('NwAy Hammer', 248), ('NwAy Mes/A', 176)]); enemy damage: high (109.8 per second)
- Peel: partly (controlled, but an attacker was left free for 10.5 s) (1 of 3 attackers controlled; longest free 10.5 s)
- Casting: interrupted far more than usual (casts 5, interrupted 1, cancelled 0, while_dazed 0)
**Why, in short**: the Prot died because no prot landed in time (0 of 0 landed), knocked down 1 times with no knockdown immunity up, its casts were interrupted (1 of 5), the enemy hit unusually hard (109.8 per second).

**How it got there, from the node models** (step 4: each link read by the node's held-out model; the biggest pushes toward the result, against the variable's usual value over every trained moment; a variable that is another node's result is followed back to it):
- 20:34 fight outcome: won the fight 31.8%; pushed by damage against the usual of the players alive, own minus enemy -0.84 (usual -0.06): +21.9 points; interrupted after casting into a ready interrupt, per cast, own minus enemy 0.07 (usual 0): +19.9 points; share of strips on the best target in range, own minus enemy 0.50 (usual 0): +7.2 points
*Fixes, carried forward to the result* (the variable set to its usual value, the node read again, the change carried link by link and priced with values.py):
- damage against the usual of the players alive, own minus enemy at 20:34: -0.84 -> -0.06; fight outcome +22.1; worth +1.7 win points at the result
- interrupted after casting into a ready interrupt, per cast, own minus enemy at 20:34: 0.07 -> 0; fight outcome +20.0; worth +1.5 win points at the result

**How it could have been prevented (measured)**

- Further back: the fixes along the chain are priced above ("Fixes, carried forward"). The readings below are what was still possible in the last seconds.
- Knockdowns with knockdown immunity ready and in range: 20:48.5 Hammer Bash by NwAy Hammer (SKT Prot Balanced Stance ready)
- Attackers left free (no snare, Blind, Weakness, interrupt, knockdown or hex from its team): NwAy AoB Derv 10.5 s free (nearest own non-healer 140); NwAy Stand Mes 6.8 s free (nearest own non-healer 527)
- Deaths node at 21:00: none of the variables it reads were in a state a teammate could change.

**Confidence**: low (measured, but the ranges include no effect yet).

## power: could not be answered (ValueError: max() iterable argument is empty)

## TQ 4. Pit NPCs lost

*The NPC loss that cost the most win chance in the new matches: HH lost knight (push) at 9:20; win chance -23.3 points from 20 s before to 20 s after.*

### Pit NPCs lost: HH v Men (6bd57984) around 9:20.0
**Lost**: 9:20.0 knight (push); 9:20.0 knight (push)
**HH at 9:20.0**: Dervish: enemy base (split (on NPCs)); AoB Derv: own base (hold); Hammer: enemy base (split (on NPCs)); Mes/A: enemy base (split (on NPCs)); Stand Mes: own base (hold); Prot: own base (hold); 7 Monk: own base (hold); 8 Monk: enemy base (split (on NPCs))
- Men output 8:50.0 to 9:20.0: 37.4 per second
- HH output 8:50.0 to 9:20.0: 16.4 per second
**Why, in short**: at 9:17 the pit had 1 attackers against 3 defenders (2 of them healers), with 5 of HH elsewhere.

*Node-model chain: no node row for this moment.*

**How it could have been prevented (measured)**

- NPC-loss node at 9:17 (AUC 0.854 on unseen matches against 0.757 for attackers and defenders alone): 1 attackers (0 healers) against 3 defenders (2 healers), 5 of HH elsewhere; read 3.1% to lose an NPC; read again with
  - one more defender [unreliable: more of the same doesn't keep moving the reading the same way; the node is reading outside its data]: 2.8% (-0.3 points; at this loss's measured cost of -23.3 win points, about +0.1 expected; at a typical NPC loss's -3.7, +0.0)
  - one more defender, a healer: 2.5% (-0.6 points; at this loss's measured cost of -23.3 win points, about +0.1 expected; at a typical NPC loss's -3.7, +0.0)
  - two more defenders [unreliable: more of the same doesn't keep moving the reading the same way; the node is reading outside its data]: 3.0% (-0.1 points; at this loss's measured cost of -23.3 win points, about +0.0 expected; at a typical NPC loss's -3.7, +0.0)
  - Readings marked unreliable or from a pairing are left out of the confidence and the fixes.

**Confidence**: low (measured, but the ranges include no effect yet).

## 9. Detailed learnings snapshot

Descriptive measurements across all 181 trained matches (the latest batch, 48 matches, in brackets where it differs). Not causal on their own: they point to questions and candidate variables.

**Runners** (spawn to capture; pushed = an enemy hit the carrier):

| Runner | Runs | Captured | Median s to capture | Dropped | Pushed | Runs by eventual winners (includes who was ahead) |
|---|---|---|---|---|---|---|
| Ritualist | 324 | 46% | 36.0 (32) | 167 | 40% | 57% |
| Mes/A | 283 | 52% | 42 (54) | 126 | 48% | 48% |
| Mesmer | 281 | 56% | 36.5 (42.5) | 114 | 48% | 54% |
| AoB Derv | 267 | 54% | 30 (28) | 119 | 39% | 51% |
| Dervish | 211 | 60% | 28 (30.5) | 75 | 49% | 36% |
| Hammer | 191 | 43% | 27 (32) | 107 | 35% | 57% |
| 8 Monk | 149 | 29% | 29 (32.0) | 104 | 19% | 58% |
| Monk 4 (WoC) | 130 | 62% | 36.5 (39.0) | 49 | 47% | 55% |
| Necromancer | 107 | 65% | 32.0 (41) | 35 | 39% | 48% |
| Warrior | 91 | 44% | 30.5 (30.0) | 49 | 38% | 37% |

Double running: single 2155 runs (49% by eventual winners, includes who was ahead); half 659 runs (53% by eventual winners, includes who was ahead).
Winners against losers below are compared at moments when a win model that never saw the match gave the team 35 to 65% (so the gap is not just who was already ahead), with every moment beside it, labelled.


**Flag answers** (answering the enemy's capture): winners at even win chance: 144 answers, median 36.0 s, 8.0 s slower than possible, 32 answers 30 s+ slower; losers at even win chance: 143 answers, median 47 s, 13 s slower than possible, 46 answers 30 s+ slower; winners every moment (includes who was ahead): 655 answers, median 38 s, 8 s slower than possible, 178 answers 30 s+ slower; losers every moment (includes who was ahead): 607 answers, median 53 s, 18 s slower than possible, 242 answers 30 s+ slower.

**Skills: kill participation** (share of casts at an enemy who died within 5 s; 15+ casts):

- Highest: Deep Freeze 33% of 33; Vapor Blade 31% of 176; Chest Thumper 27% of 496; Disrupting Throw 27% of 82; Wounding Strike PvP 27% of 63; Barbarous Slice 27% of 15; Invoke Lightning 26% of 1877; Twisting Fangs 25% of 113; Shadow Shroud PvP 25% of 125; Decapitate 24% of 561; Shatter Storm 23% of 294; Eviscerate 23% of 78
- Lowest: 3187 0% of 15; Debilitating Shot 0% of 22; 3266 0% of 40; Merciless Spear 0% of 17; Star Burst 0% of 16; Shared Burden PvP 0% of 22; Magebane Shot 0% of 25; Water Trident 0% of 53

**Interrupts:** skills interrupted most (whose): Healing Burst on the 7 Monk 520; Guardian on the Prot 355; Guardian on the 8 Monk 335; Spirit Light Weapon on the Ritualist 326; Blessed Light on the 8 Monk 294; Guardian on the 7 Monk 278; Shield Guardian PvP on the Prot 219; Cure Hex on the 7 Monk 196; Signet of Rejuvenation on the 7 Monk 175; Blessed Light on the 7 Monk 166. Interrupt skills landing most: Power Spike 2397; Complicate 2322; Psychic Instability PvP 965; Power Leak 954; Savage Shot 709; Cry of Frustration 671; Hammer Bash 448; Distracting Shot 447.

**Knockdowns by skill:** Hammer Bash 2648; Coward 2582; Psychic Instability PvP 1098; Lightning Surge 767; Mind Shock PvP 622; Grapple 394; Bull's Strike 377; "Coward!" 377.

**Spikes survived** (400+ damage in 3 s on one player; survived = alive 8 s later): losers (every moment, includes who was ahead) 584 of 1001 (58%); losers at even win chance 60 of 86 (70%); winners (every moment, includes who was ahead) 365 of 468 (78%); winners at even win chance 58 of 76 (76%). By target: Prot 62% of 177; 7 Monk 63% of 172; Mesmer 68% of 142; 8 Monk 56% of 129; AoB Derv 66% of 114; Stand Mes 76% of 113; Mes/A 84% of 80; Air Ele 60% of 63; Dervish 56% of 62; Necromancer 49% of 59; Ritualist 66% of 58; Warrior 53% of 49; Hammer 64% of 47; Paragon 68% of 38; Fire Ele 50% of 26; Ranger 60% of 25; Monk 4 (WoC) 74% of 23; Water Ele 68% of 19; Assassin 88% of 17; Monk 47% of 17; Monk 5 (WoC) 82% of 11; Monk 3 (WoC) 100% of 10.

**Monks** (per 2-minute phase alive 60 s+): winners at even win chance: 12.5 casts a minute, 0.52 fakes, idle 0 s while an ally was hurt, reaction 1.4 s, bursts answered 75%; losers at even win chance: 12.0 casts a minute, 0.5 fakes, idle 0 s while an ally was hurt, reaction 1.5 s, bursts answered 64%; winners every moment (includes who was ahead): 11.5 casts a minute, 0.54 fakes, idle 0.0 s while an ally was hurt, reaction 1.5 s, bursts answered 70%; losers every moment (includes who was ahead): 12.0 casts a minute, 0.53 fakes, idle 1.0 s while an ally was hurt, reaction 1.4 s, bursts answered 60%.

**Deaths** (3087): 952 with a knockdown on the victim; 935 had a monk cast on the victim in the last 5 s. Monk skills interrupted in the 6 s before a death: Healing Burst 130; Blessed Light 126; Guardian 96; Shield Guardian PvP 47; Reversal of Fortune 36; Cure Hex 34; Word of Healing 28; Patient Spirit 23.

## 10. For Denning

- Which curves look wrong to you? A correction (direction, cap, drop, or a pair to always test) is logged with your reason and tested on held-out matches.
- Do any surprises remind you of something the variables don't capture (a missing variable)?
- Any variable you think matters that isn't listed?

