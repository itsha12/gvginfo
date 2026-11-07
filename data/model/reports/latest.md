# Learning report, batch 8

Trained on 113 matches (22 new in this batch). Variables in use: 33; build variables from 60 matches, interactions from 40.

## 0. Data integrity

- Lengths repaired: 5 (1f65fd3b 150 s -> 1027 s) (bbef1904 617 s -> 599 s) (36a65ac6 1319 s -> 1294 s) (ba85aafc 811 s -> 793 s) (f9d6932f 235 s -> 218 s) 
- Matches with a team's Lord damage not observed (left blank, not zero): 7
- Pit NPCs added from the standard roster (never seen in the replay): 392 in 96 matches
- Left out of training: 0

## 1. The honest test

**Beats strength alone (not yet clear: the range includes 0).** Held-out accuracy (matches held out whole), log loss in brackets (lower is better):

- strength only: all 77% (0.412), 0-5 min 81% (0.344), 5-10 min 79% (0.38), 10-15 min 72% (0.469), 15-end min 70% (0.521), matches lasting 15 min+ 71% (0.515), matches even on strength (gap under 200) 55% (0.63)
- glass box: all 84% (0.36), 0-5 min 84% (0.375), 5-10 min 85% (0.315), 10-15 min 84% (0.391), 15-end min 86% (0.365), matches lasting 15 min+ 82% (0.44), matches even on strength (gap under 200) 71% (0.65)
- glass box without corrections: all 84% (0.376), 0-5 min 84% (0.38), 5-10 min 85% (0.326), 10-15 min 84% (0.426), 15-end min 84% (0.391), matches lasting 15 min+ 81% (0.463), matches even on strength (gap under 200) 71% (0.689)
- black box: all 78% (0.803), 0-5 min 80% (0.715), 5-10 min 78% (0.802), 10-15 min 75% (0.889), 15-end min 76% (0.886), matches lasting 15 min+ 74% (0.939), matches even on strength (gap under 200) 67% (1.242)
- Gain over strength alone (log loss, resampling whole matches): +0.052 (90% range -0.058 to +0.172).
- Change since batch 7: glass box log loss 0.416 -> 0.36; strength only 0.361 -> 0.412.

## 2. What it leans on

- **morale_diff & map_flag_run** 0.485 (was 0.447): own minus enemy morale summed over players (boosts +, death penalty -) TOGETHER WITH the map's flag run Y: distance from the flag spawn to the stand (average of both sides)
- **morale_diff** 0.456 (was 0.515): own minus enemy morale summed over players (boosts +, death penalty -)
- **morale_diff & lord_dps_own** 0.449 (new): own minus enemy morale summed over players (boosts +, death penalty -) TOGETHER WITH own build's measured Lord damage per second if all its non-healers were at the Lord
- **knights_diff** 0.438 (was 0.446): own minus enemy pit knights alive
- **healing_monks_enemy** 0.377 (was 0.197): enemy healing monks in the build
- **healing_monks_own** 0.372 (was 0.19): own healing monks in the build
- **spike_killable_diff** 0.361 (was 0.238): enemy minus own players within one spike of the other side (DP stacking; 0 unless a spike build is involved)
- **archers_diff & map_bases_apart** 0.276 (new): own minus enemy pit archers alive TOGETHER WITH the map's distance between the two bases
- **morale_diff & map_bases_apart** 0.237 (new): own minus enemy morale summed over players (boosts +, death penalty -) TOGETHER WITH the map's distance between the two bases
- **knights_diff & map_flag_run** 0.232 (was 0.146): own minus enemy pit knights alive TOGETHER WITH the map's flag run Y: distance from the flag spawn to the stand (average of both sides)
- **morale_diff & map_pit_to_stand** 0.216 (was 0.197): own minus enemy morale summed over players (boosts +, death penalty -) TOGETHER WITH the map's distance from a pit to the stand (average of both sides)
- **stand** 0.194 (was 0.233): who holds the flag stand: 1 own, 0 nobody, -1 enemy

## 3. The curves in words

Points = win-chance points added to an otherwise even game at each range of the variable.

- **morale_diff & map_flag_run** (interaction): see wp_model.md
- **morale_diff** rises from -21.3 to +19.6 points (-470.0..-188.5: -21.3; -146.0..-110.5: -16.6; -85.5..-45.5: -13.0; -15.5..-0.5: -1.7; 0.5..17.5: +2.1; 52.5..93.5: +14.7; 134.5..173.5: +18.1)
- **morale_diff & lord_dps_own** (interaction): see wp_model.md
- **knights_diff** rises from -28.5 to +28.3 points (-2.0..-1.5: -28.5; -1.5..-0.5: -11.6; -0.5..0.5: +0.3; 0.5..1.5: +10.1; 1.5..2.0: +28.3)
- **healing_monks_enemy** falls from -21.8 to -25.1 points (0.0..0.5: -21.8; 0.5..1.5: +19.3; 1.5..2.5: -18.5; 2.5..3.5: +5.0; 3.5..4.0: -25.1)
- **healing_monks_own** rises from +20.0 to +22.9 points (0.0..0.5: +20.0; 0.5..1.5: -18.2; 1.5..2.5: +18.7; 2.5..3.5: -5.0; 3.5..4.0: +22.9)
- **spike_killable_diff** rises from -44.5 to +44.2 points (-8.0..-7.5: -44.5; -5.5..-4.5: -42.9; -3.5..-2.5: -40.2; -1.5..-0.5: -27.4; 0.5..1.5: +26.3; 2.5..4.5: +40.7; 5.5..7.5: +43.1)
- **archers_diff & map_bases_apart** (interaction): see wp_model.md
- **morale_diff & map_bases_apart** (interaction): see wp_model.md
- **knights_diff & map_flag_run** (interaction): see wp_model.md

## 4. Discovery

**Interaction candidates** (a screen: pairs whose combination seems to matter beyond each alone; untested until held-out matches confirm them; switched on in the model from 40 matches):

- morale_diff with spike_killable_diff (screen 0.137)
- morale_diff with spike_build_own (screen 0.125)
- morale_diff with spike_build_enemy (screen 0.125)
- alive_diff with morale_diff (screen 0.116)
- morale_diff with map_pit_to_stand (screen 0.115)
- morale_diff with healing_monks_enemy (screen 0.114)
- morale_diff with healing_monks_own (screen 0.114)
- down_diff_s with morale_diff (screen 0.113)

**Candidate variables** (proposed variables, tested on unseen matches; log loss, lower is better):

- split_diff: 0.36 without, 0.367 with: does not improve yet. own minus enemy players on a split (away from their main group on the enemy half, not carrying). Proposed batch 1 by Claude: the knights curve runs backwards, maybe standing in for the cost of splitting
- turtle_diff: 0.36 without, 0.373 with: does not improve yet. own minus enemy share of live players at home (own base or pit). Proposed 2026-11-06 from OG comms ([ohno v One], [ohno v Crew]: 'they are turtling, we have to make a play'); comms_vars.py: teams that turtled 60 s won 3 of 13 times
- footmen_diff: 0.36 without, 0.373 with: does not improve yet. own minus enemy footmen alive (base NPCs, not pit NPCs). Proposed 2026-11-06 from OG comms ([ohno v NwAy]: 'this way we don't lose footmen'; [ohno v Fun]: fake collapse to the footmen)
- no_healer_groups_diff: 0.36 without, 0.362 with: does not improve yet. own minus enemy groups of 2+ with no healer. Proposed 2026-11-06 from OG comms ([ohno v One]: keep a prot and a monk on one side, the Rit and a monk on the other); comms_vars.py: such groups lose players twice as often
- solo_healers_diff: 0.36 without, 0.362 with: does not improve yet. own minus enemy healers with no other own healer within casting range. Proposed 2026-11-06 from OG comms ('solo monk, go on the monk'); Denning: a monk alone has no other monk to support it

**Surprises** (moments where the held-out model was most confident about the team that went on to lose; each points to something the variables don't capture yet):

- OG v hold (49eec28d) at 4:15: a model that never saw this match gave OG 0.3%, and OG won. Why it thought so: morale_diff & map_flag_run -28.3, healing_monks_enemy -25.3, morale_diff -23.7, team strength +19.0, morale_diff & lord_dps_enemy -18.6
- hdm v HC (28447c4a) at 23:30: a model that never saw this match gave HC 0.1%, and HC won. Why it thought so: morale_diff & map_bases_apart -41.7, knights_diff -33.6, morale_diff & map_flag_run +25.9, lord_damage_diff -25.6, morale_diff -25.2
- RACK v hdm (1f65fd3b) at 15:45: a model that never saw this match gave RACK 0.6%, and RACK won. Why it thought so: knights_diff -33.5, healing_monks_enemy -20.4, morale_diff -19.8, team strength -14.0, lord_damage_diff & lord_dps_enemy -14.0
- hold v Fun (566a6ddf) at 3:00: a model that never saw this match gave hold 13.6%, and hold won. Why it thought so: spike_killable_diff -44.7, team strength +34.1, healing_monks_enemy -20.4, spike_build_enemy -12.7, morale_diff & lord_dps_enemy +9.2
- Crew v BcS (3ee18c0c) at 14:15: a model that never saw this match gave BcS 3.5%, and BcS won. Why it thought so: healing_monks_enemy -42.4, knights_diff -13.9, morale_diff -13.0, fight_state +6.7, healing_monks_own -6.3
- Team v push (2df9b7fd) at 2:30: a model that never saw this match gave push 45.2%, and push lost. Why it thought so: team strength -48.1, spike_killable_diff +46.2, healing_monks_own -32.1, morale_diff & map_flag_run +16.7, morale_diff +16.0

## 5. Denning's rulings seen through the model

Win chance from a model that never saw the match, 20 s before and 60 s after each ruled moment. Contributions are points for an otherwise even game (the curves' scale).

- hdm v HC (28447c4a) 5:01 (split answered), HC: 34.2% 20 s before -> 42.0% 60 s after (+7.8). After: morale_diff & map_bases_apart +36.2, knights_diff -33.6, morale_diff & map_flag_run -24.3, knights_diff & map_pit_to_stand -12.1
- hdm v HC (28447c4a) 5:01 (split answered), hdm: 52.9% 20 s before -> 44.2% 60 s after (-8.7). After: morale_diff & map_bases_apart -41.3, knights_diff +33.0, morale_diff & map_flag_run +27.8, knights_diff & map_pit_to_stand +12.8
- hdm v HC (28447c4a) 1:02 (split detection), HC: 46.0% 20 s before -> 39.7% 60 s after (-6.3). After: morale_diff & map_bases_apart +32.4, morale_diff & map_flag_run -27.2, morale_diff & lord_dps_enemy -8.0, stand -6.1
- hdm v HC (28447c4a) 1:02 (split detection), hdm: 61.7% 20 s before -> 53.6% 60 s after (-8.1). After: morale_diff & map_bases_apart -34.5, morale_diff & map_flag_run +29.2, stand +6.1, team strength +5.4
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), HC: 39.5% 20 s before -> 32.1% 60 s after (-7.4). After: morale_diff & map_bases_apart +36.2, knights_diff -33.6, lord_exposed_diff -24.4, morale_diff & map_flag_run -24.3
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), hdm: 46.0% 20 s before -> 50.3% 60 s after (+4.3). After: morale_diff & map_bases_apart -41.3, knights_diff +33.0, lord_exposed_diff +28.8, morale_diff & map_flag_run +27.8
- hdm v HC (bbef1904) 8:10 (death), HC: 75.4% 20 s before -> 14.3% 60 s after (-61.1). After: morale_diff & map_flag_run -16.3, down_diff_s -12.3, fight_state -9.9, morale_diff -8.9
- hdm v HC (bbef1904) 8:10 (death), hdm: 19.3% 20 s before -> 77.0% 60 s after (+57.7). After: morale_diff & map_flag_run +14.9, fight_state +10.3, down_diff_s +8.6, morale_diff & map_bases_apart -7.9
- Men v HC (faec428a) 9:31 (death), HC: 18.0% 20 s before -> 28.4% 60 s after (+10.4). After: archers_diff & map_bases_apart -9.9, knights_diff & map_pit_to_stand -9.5, archers_diff & map_flag_run +7.8, knights_diff -7.2
- Men v HC (faec428a) 9:31 (death), Men: 83.8% 20 s before -> 74.7% 60 s after (-9.1). After: archers_diff & map_bases_apart +9.3, knights_diff & map_pit_to_stand +9.0, morale_diff & map_flag_run -8.3, knights_diff +7.4

## 6. Why: the node models

Each explains one result from what happened before it (time order enforced), tested on matches it never saw. AUC = how often a moment that led to the result scores above one that didn't (0.5 = guessing, 1 = perfect).

**deaths** (113 matches, 225220 moments, 6766 results): adds to the simple baseline (AUC 0.921 against 0.799 for health_pct and damage_taken_3s alone).
- **enemies_near** (enemies within 1,500) rises from -23.4 to +27.0 points (0.0..0.5: -23.4; 0.5..1.5: -12.6; 1.5..2.5: +1.5; 2.5..3.5: +6.4; 3.5..4.5: +10.3; 4.5..5.5: +12.3; 5.5..6.5: +14.7; 6.5..7.5: +18.3; 7.5..8.0: +27.0)
- **strength_gap** (own minus enemy team strength) falls from +18.3 to -14.3 points (-989.0..-581.0: +18.3; -434.5..-353.5: +7.0; -248.0..-103.5: +11.7; -40.0..4.5: -2.4; 64.0..108.0: -0.9; 251.5..353.5: -5.0; 434.5..572.5: -14.7)
- **health_pct** (current health %) falls from +40.5 to -5.9 points (1.0..48.5: +40.5; 60.5..68.5: +21.0; 74.5..78.5: +8.7; 82.5..85.5: +3.9; 88.5..91.5: +0.8; 93.5..95.5: -2.3; 97.5..99.5: -4.6)
- **allies_near** (allies within 1,500) falls from +20.1 to -8.1 points (0.0..0.5: +20.1; 0.5..1.5: +8.5; 1.5..2.5: +4.5; 2.5..3.5: -1.0; 3.5..4.5: -1.9; 4.5..5.5: -4.2; 5.5..6.5: -5.4; 6.5..7.0: -8.1)
- **local_diff** (allies minus enemies within 2,000) falls from +23.5 to -11.9 points (-8.0..-3.5: +23.5; -2.5..-1.5: +12.0; -0.5..0.5: -4.0; 1.5..2.5: -7.9; 3.5..4.5: +5.0; 5.5..7.0: -11.9)
- **enemy_strips** (enemy enchantment removal skills) falls from +25.8 to +1.6 points (0.0..0.5: +25.8; 0.5..1.5: +3.7; 1.5..2.5: +2.9; 2.5..3.5: -4.6; 3.5..4.5: -5.1; 4.5..5.5: -5.0; 5.5..6.5: -7.6; 6.5..7.0: +1.6)
- **own_prots** (own prot skills) is flat from +4.9 to +5.2 points (1.0..4.5: +4.9; 6.5..7.5: +10.3; 8.5..9.5: +0.9; 10.5..11.5: -0.1; 12.5..13.5: -5.2; 14.5..15.5: -3.2)
- **dist_own_pit** (distance from its own pit) rises from -3.0 to +11.7 points (10.0..1354.5: -3.0; 2315.5..3930.5: -2.7; 5110.5..6021.5: -3.7; 6829.5..7544.5: -1.4; 8219.5..8903.5: -1.8; 9818.5..10744.5: +0.8; 11930.5..13437.5: +11.4)
- **minute** (match minute) rises from -1.0 to +15.5 points (0.1..1.15: -1.0; 2.05..3.05: -4.7; 4.15..5.15: -4.5; 6.25..7.55: +1.2; 9.05..10.65: -2.4; 12.55..14.75: -2.2; 17.55..20.95: +6.1)

**kill conversion** (113 matches, 1965 moments, 585 results): adds to the simple baseline (AUC 0.777 against 0.668 for burst_damage and target_health_pct alone).
- **burst_damage** (damage in the 2 s burst) rises from -12.8 to +25.7 points (250.0..256.5: -12.8; 264.5..274.5: -12.5; 284.5..294.5: -9.3; 307.5..322.5: -6.4; 338.5..357.5: +2.8; 380.5..407.5: +6.9; 447.5..508.5: +22.8)
- **target_healers_in_range** (target's healers in range) falls from +29.3 to -8.7 points (0.0..0.5: +29.3; 0.5..1.5: +2.2; 1.5..2.5: -5.7; 2.5..3.0: -8.7)
- **strength_gap** (attacking minus target team strength) rises from -11.6 to +24.0 points (-958.0..-565.5: -11.6; -386.0..-248.0: -15.9; -106.0..-19.0: -1.3; 0.0..71.5: +1.1; 117.5..173.5: -1.4; 281.5..381.5: +0.3; 538.0..623.0: +19.3)
- **target_health_pct** (target health % when the burst started) falls from +22.0 to -10.3 points (0.0..37.5: +22.0; 48.5..55.5: +8.2; 61.5..67.5: +5.8; 72.5..76.5: +2.9; 80.5..83.5: -0.4; 87.5..91.5: -7.9; 95.5..99.5: -8.9)
- **target_ceiling** (target's health ceiling) falls from +29.3 to -9.9 points (0.4..0.69: +29.3; 0.7..0.76: +13.2; 0.84..0.85: +10.4; 0.86..0.88: +8.1; 0.94..0.95: +3.3; 0.99..1.02: -3.5; 1.1..1.1: -9.9)
- **enemy_prots** (target team's prot skills) falls from +11.0 to -22.9 points (1.0..2.5: +11.0; 4.5..6.5: +15.1; 7.5..8.5: +10.7; 9.5..10.5: +3.8; 11.5..12.5: -2.2; 13.5..14.5: -4.8; 15.5..16.5: -11.6)
- **target_prot_up** (a prot on the target) falls from +3.1 to -5.8 points (0.0..0.5: +3.1; 0.5..1.0: -5.8)
- **own_interrupts_v_enemy_heals** (attackers' interrupt skills minus target team's heals) falls from -0.9 to -13.9 points (-16.0..-15.5: -0.9; -14.5..-13.5: +7.2; -12.5..-11.5: +2.5; -10.5..-9.5: +1.7; -8.5..-7.5: -2.7; -6.5..-5.5: -7.0; -3.5..1.0: -13.9)
- **attackers_interrupted** (interrupts on the attackers (5 s before to 2 s after)) falls from +1.7 to -20.9 points (0.0..0.5: +1.7; 0.5..1.5: -11.5; 1.5..2.5: -18.0; 2.5..3.0: -20.9)

**flag answer** (seconds an answer to an enemy capture was slower than possible; 94 matches, 825 rows): adds to the simple baseline (typical error 17.4s against 28.4s for the median; explains 71% of the spread).
- **parked_s** (seconds the flag lay parked (dropped 5 s or more: not running yet)): 0.0..2.5: -6.1 s; 9.5..14.5: +4.9 s; 20.5..28.5: +20.0 s; 33.5..38.5: +38.1 s; 45.5..60.0: +54.7 s; 76.5..98.5: +64.8 s; 115.5..246.5: +65.7 s
- **own_deaths_during** (own deaths during the answer): 0.0..0.5: -4.2 s; 0.5..1.5: +8.2 s; 1.5..2.5: +15.4 s; 2.5..3.5: +23.6 s; 3.5..4.5: +32.4 s; 4.5..5.5: +38.8 s; 5.5..6.5: +53.6 s; 6.5..9.5: +65.2 s; 9.5..17.0: +82.9 s
- **enemies_in_the_way** (enemy presence along the runner's trip back to the spawn): 0.0..0.5: -5.6 s; 4.5..10.5: -4.6 s; 15.5..20.5: -3.6 s; 26.5..36.5: -1.5 s; 48.5..61.5: +2.2 s; 85.5..108.5: +8.0 s; 144.5..203.0: +17.3 s
- **enemy_deaths_during** (enemy deaths during the answer): 0.0..0.5: -3.8 s; 0.5..1.5: +9.0 s; 1.5..2.5: +17.6 s; 2.5..3.5: +23.1 s; 3.5..4.5: +25.5 s; 4.5..7.0: +25.7 s
- **carrier_damage_taken** (damage the carrier took while carrying): 0.0..0.5: -3.7 s; 28.5..51.5: -4.3 s; 76.5..101.5: -3.1 s; 135.5..198.5: +0.5 s; 251.5..300.0: +2.8 s; 400.5..538.5: +6.3 s; 678.5..1095.0: +13.1 s
- **runner_to_spawn** (runner's distance to its flag spawn when the enemy captured): 4.0..876.0: -10.8 s; 1565.0..2441.0: -2.9 s; 3509.5..4326.0: -0.5 s; 4850.0..5555.5: +2.6 s; 6245.0..6787.5: +3.9 s; 7293.0..7872.0: +3.6 s; 8757.0..9254.0: +2.5 s
- **quick_handoffs** (quick hand-offs (a teammate picked it up within 5 s)): 0.0..0.5: -1.9 s; 0.5..1.5: +6.2 s; 1.5..2.5: +10.4 s; 2.5..3.0: +13.7 s
- **possible_s** (fastest possible answer (s) from the flag model at the enemy's capture): 0.0..3.5: +0.4 s; 8.5..13.5: +0.9 s; 20.0..24.5: +1.8 s; 29.5..33.5: +2.3 s; 38.5..43.5: +3.7 s; 47.5..53.5: +0.3 s; 61.5..70.5: -4.7 s
- **morale_diff** (own minus enemy morale): -219.0..-110.5: +6.6 s; -76.5..-48.0: +5.5 s; -31.0..-17.5: +2.7 s; -6.5..1.0: +0.2 s; 14.0..17.0: -1.6 s; 41.5..67.5: -4.4 s; 92.5..134.0: -4.9 s
- **minute** (match minute): 0.3..0.65: +5.1 s; 1.45..2.25: +3.3 s; 3.15..4.15: +0.1 s; 5.25..6.55: -0.8 s; 8.05..9.65: -1.0 s; 11.55..13.55: -2.3 s; 15.75..18.15: -3.4 s

**npc loss** (113 matches, 11391 moments, 2291 results): adds to the simple baseline (AUC 0.843 against 0.752 for attackers and defenders alone).
- **npc_damage_5s** (damage on the pit NPCs in the last 5 s) rises from -17.5 to +34.7 points (0.0..0.5: -17.5; 22.5..37.5: +2.2; 52.5..71.5: +7.4; 90.5..113.5: +15.0; 136.5..162.5: +25.7; 195.5..237.5: +28.3; 296.5..397.5: +32.9)
- **defenders** (own players in the pit) falls from +32.4 to -32.1 points (0.0..0.5: +32.4; 0.5..1.5: +17.8; 1.5..2.5: +12.8; 2.5..3.5: +0.9; 3.5..4.5: -11.3; 4.5..5.5: -14.1; 5.5..6.5: -15.4; 6.5..7.5: -27.6; 7.5..8.0: -32.1)
- **defenders_elsewhere** (own players alive outside the pit) falls from +20.8 to -5.0 points (0.0..0.5: +20.8; 0.5..1.5: +10.0; 1.5..2.5: +9.6; 2.5..3.5: +2.5; 3.5..4.5: -6.9; 4.5..5.5: -13.9; 5.5..6.5: -14.3; 6.5..7.5: -14.0; 7.5..8.0: -5.0)
- **defender_healers** (of which healers) falls from +22.0 to -7.9 points (0.0..0.5: +22.0; 0.5..1.5: -1.6; 1.5..2.5: -6.1; 2.5..3.5: -8.0; 3.5..4.0: -7.9)
- **attackers** (enemy players in the pit) rises from -11.3 to +13.8 points (1.0..1.5: -11.3; 1.5..2.5: -3.9; 2.5..3.5: -2.7; 3.5..4.5: -0.6; 4.5..5.5: +8.9; 5.5..6.5: +10.8; 6.5..7.5: +12.4; 7.5..8.0: +13.8)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -9.7 to +2.6 points (1.9..12.55: -9.7; 22.85..30.95: -7.4; 32.35..37.75: -4.8; 49.55..60.3: +4.4; 64.45..72.05: +6.4; 78.15..85.75: +9.5; 97.0..110.9: +0.9)
- **strength_gap** (attacking minus defending team strength) rises from -1.5 to +8.6 points (-989.0..-416.5: -1.5; -289.0..-93.5: -12.4; -4.5..67.5: +2.0; 101.0..173.5: +2.6; 263.0..371.5: +3.7; 431.5..456.5: +3.2; 545.0..692.5: +5.7)
- **npc_healing_10s** (healing on own pit NPCs and Lord in the last 10 s) falls from +3.2 to -14.6 points (0.0..1.5: +3.2; 42.5..67.5: +1.4; 102.5..141.5: +0.6; 173.5..205.5: -2.5; 252.5..303.5: -3.5; 360.5..423.5: -7.5; 515.5..673.5: -14.0)
- **attackers_share** (share of the attacking team's live players in the pit (OG comms: merge before pushing the pit)) rises from -4.8 to +6.8 points (0.12..0.13: -4.8; 0.16..0.23: -3.8; 0.27..0.35: -2.8; 0.42..0.53: +0.6; 0.61..0.65: +3.1; 0.78..0.87: +5.1; 0.94..1.0: +6.8)

**lord damage** (Lord damage dealt in the next 10 s while players are in the enemy pit; 108 matches, 12889 rows): adds to the simple baseline (typical error 131.1 against 96.5 for the median; explains 40% of the spread).
- **defenders** (own players in the pit): 0.0..0.5: +239.1; 0.5..1.5: +115.3; 1.5..2.5: +55.8; 2.5..3.5: -17.3; 3.5..4.5: -63.4; 4.5..5.5: -119.5; 5.5..6.5: -163.9; 6.5..7.5: -180.4; 7.5..8.0: -185.9
- **defenders_elsewhere** (own players alive outside the pit): 0.0..0.5: +95.7; 0.5..1.5: +105.2; 1.5..2.5: +83.0; 2.5..3.5: +65.5; 3.5..4.5: +20.0; 4.5..5.5: -17.1; 5.5..6.5: -63.9; 6.5..7.5: -132.9; 7.5..8.0: -231.7
- **bodyguard** (own Bodyguard alive): 0.0..0.5: +110.8; 0.5..1.0: -47.6
- **defender_healers** (of which healers): 0.0..0.5: +83.6; 0.5..1.5: -10.2; 1.5..2.5: -14.5; 2.5..3.5: -43.4; 3.5..4.0: -173.1
- **attackers** (enemy players in the pit): 1.0..1.5: -32.9; 1.5..2.5: -12.0; 2.5..3.5: -16.9; 3.5..4.5: -4.0; 4.5..5.5: +28.0; 5.5..6.5: +27.4; 6.5..7.5: +32.4; 7.5..8.0: +57.3
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)): 1.9..18.15: -40.3; 22.8..31.15: -24.0; 32.8..43.55: -17.0; 58.85..64.35: -1.0; 68.4..75.9: +26.5; 83.95..90.6: +49.5; 102.75..113.4: +22.3
- **npc_healing_10s** (healing on own pit NPCs and Lord in the last 10 s): 0.0..3.0: -20.4; 42.5..70.5: +5.2; 109.5..143.5: +22.3; 176.5..211.5: +27.7; 253.5..303.5: +38.3; 359.5..419.5: +44.3; 515.5..673.5: +49.4
- **minute** (match minute): 0.5..2.75: -14.2; 3.75..4.85: +8.4; 5.95..7.15: +6.1; 8.45..9.85: -10.7; 11.25..13.05: -18.6; 15.35..18.15: -17.1; 20.55..24.55: +4.8
- **attackers_share** (share of the attacking team's live players in the pit (OG comms: merge before pushing the pit)): 0.12..0.13: -10.6; 0.16..0.23: -16.8; 0.27..0.35: -13.4; 0.42..0.53: -16.8; 0.61..0.65: +5.6; 0.73..0.84: +8.3; 0.94..1.0: +41.8
- **seconds_in_pit** (seconds the attackers have been in the pit): 0.0..4.5: -22.4; 10.5..16.5: -20.7; 22.5..28.5: -2.1; 37.5..46.5: +9.6; 58.5..73.5: +22.4; 91.5..115.5: +13.1; 148.5..199.5: +8.1

**lord kill** (108 matches, 12881 moments, 950 results): adds to the simple baseline (AUC 0.953 against 0.939 for attackers and defenders alone).
- **defenders** (own players in the pit) falls from +44.4 to -47.7 points (0.0..0.5: +44.4; 0.5..1.5: +37.8; 1.5..2.5: +16.7; 2.5..3.5: +6.3; 3.5..4.5: -24.6; 4.5..5.5: -28.6; 5.5..6.5: -40.1; 6.5..7.5: -42.6; 7.5..8.0: -47.7)
- **minute** (match minute) rises from -46.4 to +28.7 points (0.5..2.75: -46.4; 3.75..4.85: -37.7; 5.95..7.15: +12.8; 8.45..9.85: +17.7; 11.25..13.05: +18.5; 15.35..18.15: +24.8; 20.55..24.55: +26.5)
- **defenders_elsewhere** (own players alive outside the pit) falls from +36.6 to -34.1 points (0.0..0.5: +36.6; 0.5..1.5: +17.9; 1.5..2.5: +17.2; 2.5..3.5: +15.1; 3.5..4.5: +12.4; 4.5..5.5: -22.5; 5.5..6.5: -27.1; 6.5..7.5: -33.6; 7.5..8.0: -34.1)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from +7.3 to +19.6 points (1.9..18.15: +7.3; 22.8..31.15: -24.3; 32.8..43.55: -17.5; 58.85..64.35: -11.2; 68.4..75.9: +20.6; 83.95..90.6: +23.9; 102.75..113.4: +25.6)
- **defender_healers** (of which healers) falls from +31.1 to -34.3 points (0.0..0.5: +31.1; 0.5..1.5: +6.2; 1.5..2.5: -6.8; 2.5..3.5: -30.0; 3.5..4.0: -34.3)
- **attackers_share** (share of the attacking team's live players in the pit (OG comms: merge before pushing the pit)) rises from -18.1 to +25.7 points (0.12..0.13: -18.1; 0.16..0.23: -15.3; 0.27..0.35: -10.9; 0.42..0.53: -7.3; 0.61..0.65: +18.0; 0.73..0.84: +22.6; 0.94..1.0: +25.7)
- **res_in** (seconds until the next res) rises from -40.7 to -2.8 points (1.0..8.5: -40.7; 17.5..26.5: +3.4; 35.5..44.5: +13.9; 53.5..62.5: +11.7; 68.5..74.5: +9.6; 80.5..86.5: +7.7; 95.5..107.5: +1.1)
- **attackers** (enemy players in the pit) rises from -20.6 to +18.2 points (1.0..1.5: -20.6; 1.5..2.5: -1.8; 2.5..3.5: +1.6; 3.5..4.5: +5.8; 4.5..5.5: +10.0; 5.5..6.5: +12.8; 6.5..7.5: +16.1; 7.5..8.0: +18.2)
- **strength_gap** (attacking minus defending team strength) rises from -43.4 to +4.6 points (-989.0..-416.5: -43.4; -289.0..-79.0: +10.0; 25.0..79.0: +5.6; 106.0..274.5: +10.7; 371.5..416.5: +3.3; 435.5..526.0: -2.0; 594.0..702.0: -0.3)

## 7. The usual play

Each choice against the most common one in that kind of decision, in win-chance points over the decision's window, adjusted for the situation, with a 90% range from resampling whole matches. CLEAR = the range excludes 0. Win chance comes from a model that never saw the match. The same comparison over the 30 s BEFORE the decision is a placebo test: a choice can't cause what came before it, so a clear difference there means the effect is partly who makes that choice.

**after wipe** (247 decisions, 106 matches; usual: pushed the pit)
- reset (n 31): -3.4 [-6.6, -0.2] CLEAR; in the 30 s before: +2.9 [-0.9, +6.6]
- took the flag (n 29): -7.0 [-10.5, -1.7] CLEAR; in the 30 s before: +5.0 [-0.9, +11.2]

**boost clock** (411 decisions, 102 matches; usual: not running, fought)
- running, fought (n 64): +1.9 [-1.2, +4.9]; in the 30 s before: +1.5 [+0.0, +3.0] ALREADY DIFFERENT BEFORE: partly who chooses it
- not running, advanced (n 50): -0.0 [-3.9, +3.0]; in the 30 s before: +1.6 [+0.2, +3.1] ALREADY DIFFERENT BEFORE: partly who chooses it
- not running, fell back (n 47): -5.7 [-10.5, -0.7] CLEAR; in the 30 s before: +1.9 [-0.2, +4.0]
- running, advanced (n 43): +3.6 [-0.0, +7.8]; in the 30 s before: +1.9 [-0.3, +3.9]
- not running, held (n 25): -0.5 [-2.5, +1.5]; in the 30 s before: +0.9 [-1.0, +2.2]
- running, fell back (n 20): +0.1 [-4.6, +4.7]; in the 30 s before: -0.8 [-3.9, +1.8]
- not running, to the spawn (n 19): -0.9 [-3.7, +1.3]; in the 30 s before: +1.3 [-0.5, +3.1]
- running, held (n 12): +3.8 [-0.6, +9.0]; in the 30 s before: +5.9 [+2.5, +15.5] ALREADY DIFFERENT BEFORE: partly who chooses it
- not running (n 5): +1.9 [-4.8, +10.1]; in the 30 s before: +3.9 [-1.4, +9.1]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - running, fought, behind in the fight (lowest third, -0.09 or less): +0.0 (n 15 against 59)
  - running, fought, middle third: -2.3 (n 23 against 43)
  - running, fought, ahead in the fight (top third, above -0.00): +0.9 (n 26 against 24)
  - not running, advanced, behind in the fight (lowest third, -0.09 or less): +0.3 (n 13 against 59)
  - not running, advanced, middle third: -0.6 (n 16 against 43)
  - not running, advanced, ahead in the fight (top third, above -0.00): -0.6 (n 21 against 24)
  - not running, fell back, behind in the fight (lowest third, -0.09 or less): -3.0 (n 20 against 59)
  - not running, fell back, middle third: -2.6 (n 13 against 43)
  - not running, fell back, ahead in the fight (top third, above -0.00): -16.6 (n 14 against 24)
  - running, advanced, behind in the fight (lowest third, -0.09 or less): too few yet (n 1 against 59; means 1.7 against -1.0)
  - running, advanced, middle third: -4.4 (n 20 against 43)
  - running, advanced, ahead in the fight (top third, above -0.00): +4.4 (n 22 against 24)
  - not running, held, behind in the fight (lowest third, -0.09 or less): too few yet (n 6 against 59; means -2.6 against -1.0)
  - not running, held, middle third: too few yet (n 5 against 43; means -0.6 against -0.5)
  - not running, held, ahead in the fight (top third, above -0.00): -1.6 (n 14 against 24)
  - running, fell back, behind in the fight (lowest third, -0.09 or less): too few yet (n 6 against 59; means 0.8 against -1.0)
  - running, fell back, middle third: too few yet (n 7 against 43; means -6.8 against -0.5)
  - running, fell back, ahead in the fight (top third, above -0.00): too few yet (n 7 against 24; means -1.7 against -0.1)
  - not running, to the spawn, behind in the fight (lowest third, -0.09 or less): +0.6 (n 11 against 59)
  - not running, to the spawn, middle third: too few yet (n 5 against 43; means -2.7 against -0.5)
  - not running, to the spawn, ahead in the fight (top third, above -0.00): too few yet (n 3 against 24; means -7.7 against -0.1)
  - running, held, behind in the fight (lowest third, -0.09 or less): too few yet (n 1 against 59; means 0.0 against -1.0)
  - running, held, middle third: too few yet (n 9 against 43; means 1.5 against -0.5)
  - running, held, ahead in the fight (top third, above -0.00): too few yet (n 2 against 24; means -3.0 against -0.1)
  - not running, behind in the fight (lowest third, -0.09 or less): too few yet (n 5 against 59; means -0.1 against -1.0)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - running, fought, Isle of Jade: -6.3 (n 10 against 29)
  - running, fought, Isle of Meditation: +4.8 (n 10 against 30)
  - running, fought, Isle of Solitude: -1.2 (n 12 against 13)
  - running, fought, Uncharted Isle: +1.2 (n 11 against 19)
  - not running, advanced, Isle of Meditation: +3.3 (n 14 against 30)
  - not running, advanced, Uncharted Isle: +2.8 (n 10 against 19)
  - not running, fell back, Isle of Meditation: -0.3 (n 10 against 30)
  - not running, fell back, Isle of Solitude: -3.3 (n 10 against 13)
  - running, advanced, Isle of Meditation: +6.7 (n 12 against 30)

**enemy pickup** (1504 decisions, 108 matches; usual: held, fought)
- already running, fought (n 207): -0.9 [-2.9, +2.1]; in the 30 s before: +1.4 [-0.1, +3.0]
- held, advanced (n 196): +3.7 [-0.5, +10.1]; in the 30 s before: -1.8 [-7.4, +3.6]
- already running, advanced (n 174): +0.5 [-1.7, +3.7]; in the 30 s before: +1.9 [+0.1, +4.2] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, fell back (n 147): -3.2 [-5.7, -0.7] CLEAR; in the 30 s before: +0.6 [-1.1, +2.9]
- already running, fell back (n 95): -0.3 [-2.9, +3.3]; in the 30 s before: +0.5 [-1.2, +2.4]
- ran, fell back (n 92): -0.6 [-3.1, +2.7]; in the 30 s before: +0.4 [-2.0, +3.2]
- ran, fought (n 90): +0.5 [-1.5, +4.2]; in the 30 s before: -1.0 [-2.9, +1.0]
- ran, advanced (n 89): +1.6 [-1.8, +5.5]; in the 30 s before: +0.7 [-1.3, +2.8]
- already running, held (n 47): -2.3 [-4.9, +1.1]; in the 30 s before: +0.8 [-0.7, +2.2]
- ran, held (n 33): +0.4 [-2.1, +4.3]; in the 30 s before: +1.6 [-1.4, +4.7]
- held, held (n 31): +0.8 [-3.6, +5.9]; in the 30 s before: -2.4 [-8.5, +2.0]
- held, to the spawn (n 16): -6.7 [-12.4, -1.5] CLEAR; in the 30 s before: -0.8 [-8.7, +5.0]
- ran, to the spawn (n 6): -5.1 [-11.4, +1.4]; in the 30 s before: +4.7 [-2.3, +11.9]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - already running, fought, behind in the fight (lowest third, -0.01 or less): +7.9 (n 64 against 98)
  - already running, fought, middle third: -0.7 (n 71 against 49)
  - already running, fought, ahead in the fight (top third, above +0.02): -7.9 (n 72 against 134)
  - held, advanced, behind in the fight (lowest third, -0.01 or less): +16.5 (n 37 against 98)
  - held, advanced, middle third: +4.1 (n 76 against 49)
  - held, advanced, ahead in the fight (top third, above +0.02): -2.6 (n 83 against 134)
  - already running, advanced, behind in the fight (lowest third, -0.01 or less): +7.5 (n 47 against 98)
  - already running, advanced, middle third: +0.1 (n 71 against 49)
  - already running, advanced, ahead in the fight (top third, above +0.02): -4.4 (n 56 against 134)
  - held, fell back, behind in the fight (lowest third, -0.01 or less): +3.8 (n 63 against 98)
  - held, fell back, middle third: -3.0 (n 43 against 49)
  - held, fell back, ahead in the fight (top third, above +0.02): -8.6 (n 41 against 134)
  - already running, fell back, behind in the fight (lowest third, -0.01 or less): +9.5 (n 43 against 98)
  - already running, fell back, middle third: +0.3 (n 35 against 49)
  - already running, fell back, ahead in the fight (top third, above +0.02): -7.7 (n 17 against 134)
  - ran, fell back, behind in the fight (lowest third, -0.01 or less): +8.7 (n 39 against 98)
  - ran, fell back, middle third: -2.1 (n 35 against 49)
  - ran, fell back, ahead in the fight (top third, above +0.02): -6.3 (n 18 against 134)
  - ran, fought, behind in the fight (lowest third, -0.01 or less): +9.0 (n 30 against 98)
  - ran, fought, middle third: -0.2 (n 34 against 49)
  - ran, fought, ahead in the fight (top third, above +0.02): -3.6 (n 26 against 134)
  - ran, advanced, behind in the fight (lowest third, -0.01 or less): +12.4 (n 27 against 98)
  - ran, advanced, middle third: +3.3 (n 34 against 49)
  - ran, advanced, ahead in the fight (top third, above +0.02): -7.1 (n 28 against 134)
  - already running, held, behind in the fight (lowest third, -0.01 or less): +6.3 (n 14 against 98)
  - already running, held, middle third: -3.2 (n 27 against 49)
  - already running, held, ahead in the fight (top third, above +0.02): too few yet (n 6 against 134; means -1.6 against 6.6)
  - ran, held, behind in the fight (lowest third, -0.01 or less): +14.3 (n 14 against 98)
  - ran, held, middle third: -1.1 (n 13 against 49)
  - ran, held, ahead in the fight (top third, above +0.02): too few yet (n 6 against 134; means -13.7 against 6.6)
  - held, held, behind in the fight (lowest third, -0.01 or less): +14.5 (n 11 against 98)
  - held, held, middle third: -1.7 (n 16 against 49)
  - held, held, ahead in the fight (top third, above +0.02): too few yet (n 4 against 134; means -1.1 against 6.6)
  - held, to the spawn, behind in the fight (lowest third, -0.01 or less): +0.5 (n 13 against 98)
  - held, to the spawn, middle third: too few yet (n 1 against 49; means -0.1 against 0.2)
  - held, to the spawn, ahead in the fight (top third, above +0.02): too few yet (n 2 against 134; means -7.3 against 6.6)
  - ran, to the spawn, behind in the fight (lowest third, -0.01 or less): too few yet (n 3 against 98; means -11.7 against -8.3)
  - ran, to the spawn, middle third: too few yet (n 1 against 49; means 0.0 against 0.2)
  - ran, to the spawn, ahead in the fight (top third, above +0.02): too few yet (n 2 against 134; means -3.5 against 6.6)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - already running, fought, Corrupted Isle: -0.5 (n 15 against 89)
  - already running, fought, Imperial Isle: +0.0 (n 34 against 14)
  - already running, fought, Isle of Jade: +2.1 (n 15 against 38)
  - already running, fought, Isle of Meditation: -3.0 (n 25 against 36)
  - already running, fought, Isle of Solitude: +3.7 (n 26 against 19)
  - already running, fought, Nomad's Isle: -2.1 (n 28 against 26)
  - already running, fought, Uncharted Isle: +4.0 (n 54 against 41)
  - held, advanced, Corrupted Isle: +0.4 (n 42 against 89)
  - held, advanced, Imperial Isle: -2.7 (n 11 against 14)
  - held, advanced, Isle of Jade: -1.5 (n 34 against 38)
  - held, advanced, Isle of Meditation: +1.4 (n 33 against 36)
  - held, advanced, Isle of Solitude: +7.8 (n 11 against 19)
  - held, advanced, Nomad's Isle: +6.4 (n 15 against 26)
  - held, advanced, Uncharted Isle: +20.8 (n 38 against 41)
  - already running, advanced, Corrupted Isle: -3.1 (n 11 against 89)
  - already running, advanced, Imperial Isle: -3.4 (n 16 against 14)
  - already running, advanced, Isle of Jade: -1.6 (n 14 against 38)
  - already running, advanced, Isle of Meditation: +0.1 (n 40 against 36)
  - already running, advanced, Isle of Solitude: +10.3 (n 23 against 19)
  - already running, advanced, Uncharted Isle: +3.7 (n 48 against 41)
  - held, fell back, Corrupted Isle: -14.2 (n 14 against 89)
  - held, fell back, Isle of Jade: -0.9 (n 16 against 38)
  - held, fell back, Isle of Meditation: -2.8 (n 31 against 36)
  - held, fell back, Isle of Solitude: +2.6 (n 18 against 19)
  - held, fell back, Uncharted Isle: +0.2 (n 44 against 41)
  - already running, fell back, Isle of Meditation: +0.0 (n 10 against 36)
  - already running, fell back, Isle of Solitude: +8.9 (n 10 against 19)
  - already running, fell back, Uncharted Isle: +4.2 (n 43 against 41)
  - ran, fell back, Imperial Isle: -0.4 (n 17 against 14)
  - ran, fell back, Isle of Meditation: +4.6 (n 10 against 36)
  - ran, fell back, Uncharted Isle: +3.8 (n 28 against 41)
  - ran, fought, Imperial Isle: +1.1 (n 25 against 14)
  - ran, fought, Isle of Jade: +0.2 (n 10 against 38)
  - ran, fought, Uncharted Isle: +3.9 (n 20 against 41)
  - ran, advanced, Imperial Isle: +0.3 (n 17 against 14)
  - ran, advanced, Isle of Jade: +3.7 (n 14 against 38)
  - ran, advanced, Uncharted Isle: +6.9 (n 37 against 41)
  - already running, held, Uncharted Isle: +2.4 (n 15 against 41)
  - ran, held, Isle of Jade: -1.5 (n 16 against 38)
  - held, held, Isle of Jade: +1.6 (n 11 against 38)

**late game** (31 decisions, 17 matches; usual: 0 to 1 at the enemy Lord)
- 2 to 3 at the enemy Lord (n 14): +3.2 [-7.7, +7.6]; in the 30 s before: -4.0 [-5.9, +2.6]

**power play** (943 decisions, 113 matches; usual: pushed, advanced)
- pushed, fought (n 264): -0.2 [-1.5, +1.0]; in the 30 s before: -1.1 [-2.1, +0.2]
- held, fought (n 197): -2.3 [-4.1, -0.8] CLEAR; in the 30 s before: -0.3 [-1.5, +0.9]
- held, fell back (n 69): -1.9 [-4.4, +0.4]; in the 30 s before: -3.3 [-5.7, -0.5] ALREADY DIFFERENT BEFORE: partly who chooses it
- pushed, fell back (n 49): +0.1 [-3.2, +3.7]; in the 30 s before: -2.0 [-3.1, -0.3] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, advanced (n 28): +0.9 [-1.9, +4.0]; in the 30 s before: -2.6 [-4.3, -0.5] ALREADY DIFFERENT BEFORE: partly who chooses it
- pushed, held (n 6): -3.5 [-6.3, -1.4] CLEAR; in the 30 s before: -0.7 [-9.5, +8.3]
- held, held (n 6): -3.2 [-6.2, -1.2] CLEAR; in the 30 s before: -3.1 [-9.8, +3.1]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - pushed, fought, behind in the fight (lowest third, +0.00 or less): +0.5 (n 76 against 95)
  - pushed, fought, middle third: -0.1 (n 82 against 101)
  - pushed, fought, ahead in the fight (top third, above +0.08): -1.8 (n 106 against 128)
  - held, fought, behind in the fight (lowest third, +0.00 or less): -0.9 (n 83 against 95)
  - held, fought, middle third: -3.1 (n 65 against 101)
  - held, fought, ahead in the fight (top third, above +0.08): -5.3 (n 49 against 128)
  - held, fell back, behind in the fight (lowest third, +0.00 or less): -4.4 (n 27 against 95)
  - held, fell back, middle third: -0.6 (n 25 against 101)
  - held, fell back, ahead in the fight (top third, above +0.08): -0.7 (n 17 against 128)
  - pushed, fell back, behind in the fight (lowest third, +0.00 or less): +2.2 (n 19 against 95)
  - pushed, fell back, middle third: -0.4 (n 22 against 101)
  - pushed, fell back, ahead in the fight (top third, above +0.08): too few yet (n 8 against 128; means -0.1 against 4.2)
  - held, advanced, behind in the fight (lowest third, +0.00 or less): +2.0 (n 13 against 95)
  - held, advanced, middle third: -1.1 (n 10 against 101)
  - held, advanced, ahead in the fight (top third, above +0.08): too few yet (n 5 against 128; means 9.6 against 4.2)
  - pushed, held, behind in the fight (lowest third, +0.00 or less): too few yet (n 4 against 95; means -3.4 against 0.7)
  - pushed, held, middle third: too few yet (n 1 against 101; means -1.1 against 1.4)
  - pushed, held, ahead in the fight (top third, above +0.08): too few yet (n 1 against 128; means 0.7 against 4.2)
  - held, held, behind in the fight (lowest third, +0.00 or less): too few yet (n 3 against 95; means -0.1 against 0.7)
  - held, held, middle third: too few yet (n 3 against 101; means -0.6 against 1.4)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - pushed, fought, Corrupted Isle: -2.7 (n 30 against 32)
  - pushed, fought, Imperial Isle: +3.8 (n 20 against 22)
  - pushed, fought, Isle of Jade: -3.8 (n 38 against 47)
  - pushed, fought, Isle of Meditation: +0.1 (n 61 against 80)
  - pushed, fought, Isle of Solitude: -1.0 (n 36 against 32)
  - pushed, fought, Nomad's Isle: -0.6 (n 24 against 13)
  - pushed, fought, Uncharted Isle: -1.5 (n 37 against 73)
  - held, fought, Corrupted Isle: -7.5 (n 16 against 32)
  - held, fought, Imperial Isle: -1.3 (n 26 against 22)
  - held, fought, Isle of Jade: -5.9 (n 21 against 47)
  - held, fought, Isle of Meditation: -0.6 (n 31 against 80)
  - held, fought, Isle of Solitude: -5.3 (n 27 against 32)
  - held, fought, Nomad's Isle: -3.6 (n 27 against 13)
  - held, fought, Uncharted Isle: -1.4 (n 32 against 73)
  - held, fell back, Isle of Meditation: -5.7 (n 16 against 80)
  - held, fell back, Uncharted Isle: -3.1 (n 13 against 73)
  - pushed, fell back, Uncharted Isle: -1.9 (n 12 against 73)

**split in base** (236 decisions, 72 matches; usual: defended without a collapse)
- collapsed (n 99): -4.8 [-8.9, +0.2]; in the 30 s before: +1.3 [-0.6, +3.1]
- missed (n 25): -2.0 [-8.7, +3.3]; in the 30 s before: +2.2 [-0.7, +6.7]
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - collapsed, Corrupted Isle: -9.6 (n 14 against 12)
  - collapsed, Isle of Meditation: +0.8 (n 28 against 17)
  - collapsed, Isle of Solitude: -0.3 (n 11 against 40)
  - collapsed, Uncharted Isle: -1.0 (n 13 against 31)

**Collapses on a split: time away and its cost** (`S32`; per collapse, averages; main = what the main fight lost while the collapsers were away)

| Group | Cases | Away (median s) | Split killed | Collapser died | Own deaths at main | Enemy deaths at main | Flag lead change | DP change | Win change |
|---|---|---|---|---|---|---|---|---|---|
| all | 111 | 22 | 24 | 11 | 0.61 | 0.41 | +1.1 | -4.1 | -3.2 |
| away under 30 s | 65 | 7 | 18 | 1 | 0.02 | 0.14 | +0.1 | +0.9 | -3.0 |
| away 30 to 60 s | 19 | 43 | 2 | 3 | 0.79 | 0.47 | -11.8 | -10.8 | +3.5 |
| away 60 s or more | 27 | 102 | 4 | 7 | 1.93 | 1 | +12.8 | -11.3 | -8.5 |
| before 20:00 | 94 | 22.5 | 17 | 9 | 0.5 | 0.35 | +1.8 | -5.2 | -3.7 |
| from 20:00 | 17 | 18 | 7 | 2 | 1.24 | 0.71 | -2.6 | +2.2 | -0.7 |
| split member killed | 24 | 13.5 | 24 | 1 | 0.04 | 1.04 | +0.4 | +1.1 | +3.9 |
| no kill | 87 | 25 | 0 | 10 | 0.77 | 0.23 | +1.3 | -5.5 | -5.2 |

**Leverage: where the choice matters most** (share of the spread in win-chance change explained by the choice beyond the situation; range = best minus worst choice, in points)

- after wipe (247): choice explains 5.1% (situation 8.8%); range 7.5 points, best pushed the pit, worst took the flag
- boost clock (411): choice explains 4.9% (situation 3.5%); range 9.4 points, best running, advanced, worst not running, fell back
- enemy pickup (1504): choice explains 1.8% (situation 2.9%); range 11.2 points, best held, advanced, worst ran, to the spawn
- split in base (236): choice explains 1.3% (situation 5.0%); range 3.9 points, best defended without a collapse, worst collapsed
- power play (943): choice explains 1.0% (situation 2.1%); range 4.9 points, best held, advanced, worst pushed, held
- late game (31): choice explains 0.1% (situation 85.7%); range 3.2 points, best 2 to 3 at the enemy Lord, worst 0 to 1 at the enemy Lord

**Behaviour clusters: what teams actually did** (each decision's response grouped by what every player did in the next 20 s; UNNAMED = a group no single named choice covers: a response for Denning to name or reject)

*after wipe* (2 groups, separation 0.32):
- n 150: fought (midline, 1.9 of 8), fought (backline, 1.4 of 8), fought (frontline, 0.9 of 8), held (backline, 0.8 of 8); named as {'pushed the pit': 129, 'reset': 11, 'took the flag': 10}; win change 0.0
- n 97: advanced (midline, 2.7 of 8), advanced (backline, 2.5 of 8), advanced (frontline, 1.3 of 8); named as {'pushed the pit': 58, 'reset': 20, 'took the flag': 19}; win change 1.3 UNNAMED
*boost clock* (4 groups, separation 0.19):
- n 162: fought (midline, 2.2 of 8), fought (backline, 1.8 of 8), fought (frontline, 1.0 of 8); named as {'not running, fought': 103, 'running, fought': 49, 'not running, to the spawn': 4}; win change -0.4
- n 104: advanced (midline, 2.2 of 8), advanced (backline, 1.6 of 8), advanced (frontline, 0.6 of 8), fought (midline, 0.6 of 8); named as {'not running, advanced': 47, 'running, advanced': 39, 'not running, fought': 6}; win change -0.9 UNNAMED
- n 91: held (backline, 1.8 of 8), held (midline, 1.1 of 8), fought (midline, 0.7 of 8), fought (frontline, 0.5 of 8); named as {'not running, held': 25, 'not running, fought': 16, 'not running, to the spawn': 12}; win change -1.1 UNNAMED
- n 58: fell back (midline, 2.5 of 8), fell back (backline, 1.9 of 8), fell back (frontline, 0.6 of 8); named as {'not running, fell back': 39, 'running, fell back': 16, 'running, fought': 2}; win change -6.8
*enemy pickup* (4 groups, separation 0.21):
- n 531: fought (midline, 2.2 of 8), fought (backline, 1.5 of 8), fought (frontline, 1.0 of 8), held (backline, 0.7 of 8); named as {'held, fought': 234, 'already running, fought': 184, 'ran, fought': 79}; win change -1.6 UNNAMED
- n 480: advanced (midline, 2.2 of 8), advanced (backline, 2.0 of 8), advanced (frontline, 0.9 of 8), fought (backline, 0.5 of 8); named as {'held, advanced': 187, 'already running, advanced': 156, 'ran, advanced': 82}; win change 4.2 UNNAMED
- n 339: fell back (midline, 2.1 of 8), fell back (backline, 1.9 of 8), fell back (frontline, 0.8 of 8); named as {'held, fell back': 135, 'already running, fell back': 85, 'ran, fell back': 83}; win change -1.7 UNNAMED
- n 154: held (backline, 1.7 of 8), held (midline, 1.7 of 8), fought (midline, 0.6 of 8); named as {'already running, held': 46, 'ran, held': 32, 'held, held': 27}; win change -0.2 UNNAMED
*late game* (4 groups, separation 0.24):
- n 11: advanced (midline, 2.8 of 8), advanced (backline, 1.4 of 8), advanced (frontline, 0.7 of 8); named as {'2 to 3 at the enemy Lord': 5, '0 to 1 at the enemy Lord': 4, '4+ at the enemy Lord': 2}; win change -10.1 UNNAMED
- n 10: fell back (backline, 2.2 of 8), fell back (midline, 1.6 of 8), fell back (frontline, 1.1 of 8), advanced (backline, 0.6 of 8); named as {'0 to 1 at the enemy Lord': 6, '2 to 3 at the enemy Lord': 4}; win change 3.6
- n 8: fought (midline, 2.6 of 8), fought (backline, 1.9 of 8), fought (frontline, 0.9 of 8), held (backline, 0.8 of 8); named as {'0 to 1 at the enemy Lord': 4, '2 to 3 at the enemy Lord': 3, '4+ at the enemy Lord': 1}; win change 3.7 UNNAMED
- n 5: held (backline, 2.5 of 8), held (midline, 1.0 of 8), advanced (midline, 0.8 of 8), fought (midline, 0.8 of 8); named as {'0 to 1 at the enemy Lord': 3, '2 to 3 at the enemy Lord': 2}; win change 7.2
*power play* (2 groups, separation 0.27):
- n 615: fought (midline, 1.9 of 8), fought (backline, 1.4 of 8), fought (frontline, 0.9 of 8), fell back (backline, 0.7 of 8); named as {'pushed, fought': 258, 'held, fought': 196, 'held, fell back': 68}; win change 0.7 UNNAMED
- n 333: advanced (midline, 2.4 of 8), advanced (backline, 2.2 of 8), advanced (frontline, 1.1 of 8); named as {'pushed, advanced': 296, 'held, advanced': 26, 'pushed, fought': 6}; win change 2.1
*split in base* (3 groups, separation 0.19):
- n 103: fought (midline, 2.4 of 8), fought (backline, 1.3 of 8), fought (frontline, 0.9 of 8), held (backline, 0.7 of 8); named as {'defended without a collapse': 54, 'collapsed': 37, 'missed': 12}; win change -0.2 UNNAMED
- n 69: advanced (midline, 2.0 of 8), advanced (backline, 1.1 of 8), advanced (frontline, 0.6 of 8), held (backline, 0.5 of 8); named as {'defended without a collapse': 34, 'collapsed': 29, 'missed': 6}; win change -1.1 UNNAMED
- n 63: fell back (midline, 2.5 of 8), fell back (backline, 1.5 of 8), fell back (frontline, 0.8 of 8), fought (backline, 0.5 of 8); named as {'collapsed': 33, 'defended without a collapse': 23, 'missed': 7}; win change -4.6 UNNAMED

## 8. What results and causes are worth

Win points for the team it happened to, from 113 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 331 | +0.5 | -4.9 to +5.8 | +2.7 | no |
| capture | 940 | +1.8 | +0.9 to +2.8 | +2.1 | yes |
| death (any) | 2174 | -6.0 | -8.1 to -3.9 | -3.6 | yes |
| death: against a spike build | 591 | -6.2 | -11.5 to -1.3 | -2.4 | yes |
| death: against other builds | 1583 | -6.0 | -8.5 to -3.6 | -4.1 | yes |
| death: back within 20 s | 359 | -5.1 | -8.8 to -1.8 | -2.4 | yes |
| death: down 20 to 60 s | 809 | -7.3 | -10.7 to -4.1 | -3.1 | yes |
| death: down 60 s or more | 1006 | -5.4 | -7.5 to -3.4 | -4.5 | yes |
| death: healer | 731 | -5.6 | -8.0 to -3.3 | -4.0 | yes |
| death: healer in own base or pit, back within 15 s (likely deliberate) | 44 | +0.0 | -3.3 to +4.4 | +1.0 | no |
| death: healer, other | 687 | -6.0 | -8.4 to -3.6 | -4.4 | yes |
| death: not a healer | 1443 | -6.3 | -8.9 to -4.0 | -3.4 | yes |
| death: team boosted (morale above zero) | 227 | -22.1 | -33.3 to -11.5 | -7.1 | yes |
| death: team not boosted | 1947 | -4.2 | -7.1 to -1.5 | -3.2 | yes |
| footman lost (base NPC) | 327 | +0.5 | -2.5 to +3.3 | +1.0 | no |
| pit NPC lost (any): taken by a spike build | 186 | -1.5 | -5.6 to +3.1 | -0.2 | no |
| pit NPC lost (any): taken by other builds | 708 | -3.4 | -5.7 to -1.3 | -1.8 | yes |
| pit NPC lost: archer | 513 | -1.0 | -2.9 to +1.0 | +0.0 | no |
| pit NPC lost: bodyguard | 124 | -2.9 | -5.3 to -0.5 | -0.2 | yes |
| pit NPC lost: knight | 257 | -7.1 | -9.6 to -4.9 | -4.9 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value.

*deaths* (per 10 s in that state; result worth -6.0 points, base rate 1.5%):

- enemies within 1,500 7.5 to 8: result chance +3.3 points, worth -0.2 win points
- own minus enemy team strength 353.5 to 434.5: result chance -0.9 points, worth +0.05 win points
- current health % 1 to 48.5: result chance +11.0 points, worth -0.66 win points
- allies within 1,500 0 to 0.5: result chance +1.9 points, worth -0.12 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.5 points, worth -0.15 win points
- enemy enchantment removal skills 0 to 0.5: result chance +3.0 points, worth -0.18 win points
- own prot skills 6.5 to 7.5: result chance +0.8 points, worth -0.05 win points
- distance from its own pit 13437.5 to 18468: result chance +0.9 points, worth -0.05 win points

*kill conversion* (per burst, for the attacking team; result worth +6.0 points, base rate 29.8%):

- damage in the 2 s burst 508.5 to 839: result chance +27.1 points, worth +1.63 win points
- target's healers in range 0 to 0.5: result chance +32.1 points, worth +1.93 win points
- attacking minus target team strength 623 to 989: result chance +24.9 points, worth +1.49 win points
- target health % when the burst started 0 to 37.5: result chance +22.4 points, worth +1.34 win points
- target's health ceiling 0.4 to 0.69: result chance +32.1 points, worth +1.93 win points
- target team's prot skills 16.5 to 17: result chance -16.2 points, worth -0.97 win points
- a prot on the target 0.5 to 1: result chance -4.6 points, worth -0.28 win points
- attackers' interrupt skills minus target team's heals -3.5 to 1: result chance -10.4 points, worth -0.63 win points

*npc loss* (per case, for the defending team; result worth -3.0 points, base rate 20.1%):

- damage on the pit NPCs in the last 5 s 397.5 to 1370: result chance +38.1 points, worth -1.15 win points
- own players in the pit 0 to 0.5: result chance +34.0 points, worth -1.03 win points
- own players alive outside the pit 0 to 0.5: result chance +17.8 points, worth -0.54 win points
- of which healers 0 to 0.5: result chance +19.2 points, worth -0.58 win points
- enemy players in the pit 7.5 to 8: result chance +10.6 points, worth -0.32 win points
- attackers' measured damage per second against a Lord (benchmarks) 85.75 to 97: result chance +7.5 points, worth -0.23 win points
- attacking minus defending team strength -416.5 to -289: result chance -10.1 points, worth +0.3 win points

## The TQs

Denning's four questions, each from the batch's matches. The why comes from forensics and events (every number placed against the same role or situation in every stored match); the different play comes only from measurement: the usual play's choice effects (usual.py), node models read again with the variable changed (models that never saw the match, changes priced in win points with values.py), options that were ready and unused, and benchmarks. Points = win-chance points.

## TQ 1. Behind on flags

*The biggest flag swing in the new matches: RACK +80 -> -85 by 11:30.0.*

### Flag swing: RACK v chic (bb669b6f), 9:50.0 to 11:30.0
**Result**: RACK's flag lead +80 s -> -85 s (-165 s). Stand: RACK -> RACK.
**Captures** (flag model: fastest possible answer after the enemy's capture):
- chic capped 9:34.0 by Dervish, 60 s after RACK's capture; fastest possible 75 s, so -14 s slower; enemies in the way {'Hammer A': 14, '8 Monk': 13, 'Hammer B': 12, '7 Monk': 11}
- RACK capped 9:44.0 by Hammer A, 9 s after chic's capture; fastest possible 9 s, so 0 s slower; enemies in the way {'Dervish': 10, 'Warrior': 10, '7 Monk': 9, 'Mes/A': 1}
- chic capped 10:51.0 by Dervish, 67 s after RACK's capture; fastest possible 67 s, so 0 s slower; enemies in the way {'Hammer A': 6, '8 Monk': 5, '7 Monk': 4, 'Stand Mes': 2}
- RACK capped 10:53.0 by Mes/A, 2 s after chic's capture; fastest possible 1 s, so 1 s slower
- chic capped 11:44.0 by Dervish, 51 s after RACK's capture; fastest possible 70 s, so -19 s slower; enemies in the way {'Mes/A': 8, 'Hammer A': 2}
- RACK capped 11:53.0 by Mes/A, 9 s after chic's capture; fastest possible 15 s, so -6 s slower; enemies in the way {'Dervish': 7, '7 Monk': 4}
**Runs** (each run: outcome, and what was done to the runner):
- RACK Hammer A 9:34.0 to 9:44.0 (10 s): captured, lowest health 68%, escort none, pushed by ['Dervish']
- chic Dervish 10:10.0 to 10:51.0 (41 s): captured, lowest health 35%, escort none, pushed by ['Stand Mes', 'Hammer A']
- RACK Mes/A 9:49.0 to 10:53.0 (64 s): captured, lowest health 73%, escort ['Hammer A'], pushed by nobody
- chic Dervish 11:23.0 to 11:44.0 (21 s): captured, lowest health 88%, escort none, pushed by nobody
- RACK output in the 20 s before 11:30.0: 66.8 damage per second (above the 80th percentile for team (median 37.1, n 3825)), top target share 0.75, spikes 0
- chic output in the 20 s before 11:30.0: 51.9 damage per second (above the 50th percentile for team (median 37.1, n 3825)), top target share 0.32, spikes 0
**Why, in short**: chic capped at 9:34, 60 s after RACK's capture, on its 1st run (0 dropped); RACK pushed the last carrier with nobody but its health never went below 81%; RACK's answer was 0 s slower than possible.

**A different play (measured)**

*The decisions in the swing* (usual.py: win-chance points over the decision's window, against the kind's most common choice):
- enemy pickup at 10:10 (main 5v6, flags +80 s, boost in 95, fight state 0.019): chose **already running, fought** (-0.9 [-2.9, +2.1] against the most common choice, held, fought); in the 15 most similar decisions teams usually chose **ran, fought**; measured better: **held, advanced** (+4.6 points against the choice made, not clear yet, n 196); **ran, advanced** (+2.5 points against the choice made, not clear yet, n 89). In the same fight-state third (middle third) this choice did -0.7 against the usual choice (n 71 against 49, raw).
- enemy pickup at 11:23 (main 6v7, flags +46 s, boost in 91, fight state 0.036): chose **ran, fought** (+0.5 [-1.5, +4.2] against the most common choice, held, fought); in the 15 most similar decisions teams usually chose **held, fought**; measured better: **held, advanced** (+3.2 points against the choice made, not clear yet, n 196). In the same fight-state third (ahead in the fight (top third, above +0.02)) this choice did -3.6 against the usual choice (n 26 against 134, raw).
*The answers to the enemy's captures* (flag-answer node: seconds slower than possible; typical error 17.4 s against 28.4 s for the median on unseen matches):
- answer at 9:34 by the Mes/A: 0 s slower than possible (model reads -3.0 s); with a runner waiting at the spawn: -11.7 s (-8.7 s); no enemies on the way back: -7.8 s (-4.8 s)
- answer at 10:51 by the Mes/A: 1 s slower than possible (model reads -11.4 s); with a runner waiting at the spawn: -20.1 s (-8.7 s)
- answer at 11:44 by the Mes/A: -6 s slower than possible (model reads 0.2 s); with a runner waiting at the spawn: -8.5 s (-8.7 s); no enemies on the way back: -2.3 s (-2.5 s)
- Those 9 s, read by the win model as flag lead at 11:30: RACK 64.1% -> 64.1% (+0.0 points)

**Confidence**: medium (one measurement supports it).

## TQ 2. A monk death

*The monk death that cost the most win chance in the new matches: Dz v Crew (1729daac), Dz 8 Monk at 25:07 (own pit, numbers [7, 6]); win chance -61.7 points from 10 s before to 30 s after.*

**Why** (forensics, against the same role in every stored match):
- Position: yes (nearest allied healer 10956 in the last 5 s, nearest enemy 1148, allies in casting range 0, enemies 1)
- Prots: late or interrupted (0 from teammates, 1 self; 1 of 1 landed); damage 248 (0% attacks, 60% armor-ignoring), burst 125 in 2 s at 24:52.5
- Healers under interrupt pressure: usual (healers 3, interrupts_per_min 0.0, interrupted 0, casts 18, finished_share 1.0, dazed 0, knockdowns 0, hexes 5)
- Damage off shield sets: usual (team share 0.34, a shield would have stopped about 59)
- Own damage: usual (29.8 per second on [('Crew Warrior', 335), ('Crew Necromancer', 231)]); enemy damage: high (80.0 per second)
- Peel: no (peel on a burst is rare: most bursts on this role get none) (0 of 1 attackers controlled; longest free 20.0 s)
- Casting: usual (casts 5, interrupted 0, cancelled 0, while_dazed 0)
**Why, in short**: the 8 Monk died because no prot landed in time (1 of 1 landed), the enemy hit unusually hard (80.0 per second), position (no allied healer within casting range, nearest enemy 1148), its attackers were not peeled (no (peel on a burst is rare: most bursts on this role get none)).

**How it could have been prevented (measured)**

- Attackers left free (no snare, Blind, Weakness, interrupt, knockdown or hex from its team): Crew Ritualist 20.0 s free (nearest own non-healer 10821)
- Deaths node at 25:05 (AUC 0.921 on unseen matches against 0.799 for health_pct and damage_taken_3s alone): risk 55.7% of dying in the next 10 s; read again with
  - another healer in range: 42.6% (-13.1 points of risk; at this death's measured cost of -61.7 win points, about +8.1 expected; at a typical healer death's -5.6, +0.7)
  - staying with its group: 53.9% (-1.8 points of risk; at this death's measured cost of -61.7 win points, about +1.1 expected; at a typical healer death's -5.6, +0.1)
  - its hexes removed: 49.0% (-6.7 points of risk; at this death's measured cost of -61.7 win points, about +4.1 expected; at a typical healer death's -5.6, +0.4)
  - all of these together: 34.6% (-21.1 points of risk; at this death's measured cost of -61.7 win points, about +13.0 expected; at a typical healer death's -5.6, +1.2)
- The decision before it (usual.py):
  - power play at 24:25 (main 7v6, flags -22 s, boost in 84, fight state -0.363): chose **held, fought** (-2.3 [-4.1, -0.8] CLEAR against the most common choice, pushed, advanced); in the 15 most similar decisions teams usually chose **pushed, advanced**; measured better: **pushed, advanced** (+2.3 points against the choice made, clear, n 324); **held, advanced** (+3.2 points against the choice made, not clear yet, partly who chooses it, n 28). In the same fight-state third (behind in the fight (lowest third, +0.00 or less)) this choice did -0.9 against the usual choice (n 83 against 95, raw).

**Confidence**: medium to high (two independent measurements agree).

## TQ 3. A power play without a kill

*The biggest in the new matches: main 8v3, held, no kill in 33 s.*

### Power play without a kill: Apes v Crew (6db63508), 8:55.0 to 9:28.0
**Situation**: main 8v3, alive 8v8, flags up (+62 s), DP 63, boost in 67; choice held (advanced 3, fell back 2, carrying 1, fought 1, held 1); deaths {'Apes': 0, 'Crew': 0} in 33 s
**The fight's shape** (every 5 s: own main, the enemy group it faced, distance between them, that group's distance to the rest of its team): 8:55.0 8v3 72 apart, 1420 from its others; 9:00.0 5v4 943 apart, 2376 from its others; 9:05.0 7v4 384 apart, 2177 from its others; 9:10.0 4v4 1499 apart, 1450 from its others; 9:15.0 7v5 79 apart, 1376 from its others; 9:20.0 6v6 77 apart, 5957 from its others; 9:25.0 5v6 561 apart, 5879 from its others
**Apes's damage**: 44.2 per second (above the 50th percentile for team (median 37.1, n 3825)); top target share 0.37 (below the 50th percentile for team (median 0.49, n 3825)); targets [('Crew AoB Derv', 536), ('Crew Ritualist', 532), ('Crew Hammer', 231), ('Crew 7 Monk', 85)]; dealers [('Apes Warrior', 552), ('Apes Hammer', 223), ('Apes Mesmer', 221), ('Apes Necromancer', 217), ('Apes Ritualist', 202)]
- phase 8:00.0 to 9:00.0: 7v6 (stand, job convert), damage uptime 0.32, damage-seconds lost {'idle': 160, 'carrying': 45}
- phase 9:00.0 to 9:19.0: 8v6 (stand, job convert), damage uptime 0.28, damage-seconds lost {'idle': 49, 'carrying': 19}
- phase 9:19.0 to 9:23.0: 7v6 (stand, job convert), damage uptime 0.2, damage-seconds lost {'idle': 12, 'carrying': 4}
- phase 9:23.0 to 10:00.0: 5v7 (stand, job hold), damage uptime 0.32, damage-seconds lost {'idle': 74, 'moving': 1}
**Crew's answer**: healing 59 per second ({'Crew 8 Monk': 574.8, 'Crew 7 Monk': 552.9, 'Crew Ritualist': 492, 'Crew Prot': 287}); prots {'Shielding Hands': 1, 'Reversal of Fortune': 2, 'Guardian': 1}
- Apes's knockdowns landed 0; Crew's knockdown immunity casts 0
- Pressure on Crew's healers: healers 4, interrupts_per_min 0.0, interrupted 0, casts 22, finished_share 0.86, dazed 0, knockdowns 0, hexes 1 (around the median for team (median 0, n 4312))
- Snares, Blind and Weakness Apes put on Crew: {'crippled': 1}
**Why, in short**: Apes had 8v3 at main for 33 s; Crew healed 59 per second; worse than in power plays that killed: damage uptime in contact 28% (killing 46%, not killing 33%; most lost to idle); not the cause (on the side of power plays that killed): damage 44.2 per second (killing 37.55, not killing 22.4), top-target share 0.37 over 4 targets (killing 0.4, not killing 0.5).

**How it could have been converted (measured)**

- Against every stored power play (3+ more at main): those that killed had a median 37.55 damage per second and top-target share 0.4 (56 cases); those that didn't, 22.4 and 0.5 (49 cases). Apes here: 44.2 and 0.37. Damage uptime: 46% in those that killed, 33% in those that didn't, 28% here.
- No burst (a 2 s burst that the kill-conversion node reads) in the window: the damage never came together on one target.
- The choice at the power play (usual.py):
  - power play at 8:55 (main 8v3, flags +62 s, boost in 67, fight state -0.012): chose **held, advanced** (+0.9 [-1.9, +4.0], partly who chooses it against the most common choice, pushed, advanced); in the 15 most similar decisions teams usually chose **pushed, advanced**; no choice of this kind did measurably better than the one made. In the same fight-state third (behind in the fight (lowest third, +0.00 or less)) this choice did +2.0 against the usual choice (n 13 against 95, raw).

**Confidence**: low (the engine can't price an alternative here yet).

## TQ 4. Pit NPCs lost

*The NPC loss that cost the most win chance in the new matches: Fun lost knight (hold split Ritualist) at 3:46; win chance -33.2 points from 20 s before to 20 s after.*

### Pit NPCs lost: Fun v hold (566a6ddf) around 3:46.0
**Lost**: 3:33.0 archer (outside) (hold split Ritualist); 3:46.0 knight (hold split Ritualist); 3:52.0 knight (hold split Ritualist)
**hold's split** 0:15.0 to 4:03.0: ['Ritualist'] (split), entered base 2:23.0, NPC damage {'footman': 658, 'spirit': 24, 'archer': 1053, 'bodyguard': 642}, NPC kills [{'npc': 'archer (outside)', 't': 136, 'defenders_present': []}, {'npc': 'archer (outside)', 't': 213, 'defenders_present': []}, {'npc': 'knight', 't': 226, 'defenders_present': []}, {'npc': 'knight', 't': 232, 'defenders_present': ['Air Ele 1', 'Fire Ele 2']}]
- defender Air Ele 1: first 3:51.0 (latency 88 s, already in base), 13 s defending
- defender Fire Ele 2: first 3:51.0 (latency 88 s, already in base), 13 s defending
- defender Air Ele 2: first 3:58.0 (latency 95 s, already in base), 6 s defending
- defender Air Ele 3: first 3:59.0 (latency 96 s, already in base), 5 s defending
- main numbers meanwhile [6.8, 7.4]
**Fun at 3:46.0**: Air Ele 1: own base (contest); Fire Ele 1: own base (contest); Air Ele 2: own base (contest); Air Ele 3: own base (contest); Air Ele 4: own base (contest); Fire Ele 2: own base (contest); 7 Monk: dead; 8 Monk: own base (contest)
- hold output 0:15.0 to 3:51.0: 35.5 per second
- Fun output 0:15.0 to 3:51.0: 32.4 per second
**Why, in short**: hold split Ritualist into Fun's base at 2:23; at 3:41 the pit had 1 attackers against 7 defenders (1 of them healers), with 0 of Fun elsewhere; 2 of Fun were dead at the time (Fire Ele 1 2:47, 7 Monk 3:08); the Fire Ele 1 died at 2:47 (backside, numbers [7, 6]) because no prot landed in time (0 of 0 landed; 7 Monk Guardian ready and unused), its attackers were not peeled (partly (controlled, but an attacker was left free for 20.0 s)); the 7 Monk died at 3:08 (backside, numbers [7, 7]) because knocked down 1 times with no knockdown immunity up, the enemy hit unusually hard (65.8 per second), its own team's damage was low (12.2 per second).

**How it could have been prevented (measured)**

- Further back: with 2 of Fun dead, more defenders were not available; the deaths are explained above, and the split's answer is priced below.
- First defender: 88 s after it entered the base; every stored split into a base: median 10 s before it entered the base, quickest fifth 34 s before it entered the base or sooner (294 splits). Denning: about 15 s is on time, 60 s is late.
- NPC-loss node at 3:41 (AUC 0.843 on unseen matches against 0.752 for attackers and defenders alone): 1 attackers (0 healers) against 7 defenders (1 healer), 0 of Fun elsewhere; read 12.4% to lose an NPC; read again with
  - one more defender: 10.8% (-1.6 points; at this loss's measured cost of -33.2 win points, about +0.5 expected; at a typical NPC loss's -3.0, +0.0)
  - one more defender, a healer: 9.3% (-3.1 points; at this loss's measured cost of -33.2 win points, about +1.0 expected; at a typical NPC loss's -3.0, +0.1)
  - two more defenders: 10.8% (-1.6 points; at this loss's measured cost of -33.2 win points, about +0.5 expected; at a typical NPC loss's -3.0, +0.0)

**Confidence**: low (measured, but the ranges include no effect yet).

## 9. Detailed learnings snapshot

Descriptive measurements across all 113 trained matches (the latest batch, 22 matches, in brackets where it differs). Not causal on their own: they point to questions and candidate variables.

**Runners** (spawn to capture; pushed = an enemy hit the carrier):

| Runner | Runs | Captured | Median s to capture | Dropped | Pushed | Runs by winners |
|---|---|---|---|---|---|---|
| Mes/A | 227 | 51% | 40.5 (26) | 104 | 45% | 47% |
| AoB Derv | 196 | 55% | 31 (39) | 86 | 37% | 55% |
| Ritualist | 180 | 46% | 39.0 (52.0) | 93 | 34% | 60% |
| Mesmer | 161 | 53% | 35 (47) | 72 | 40% | 53% |
| Dervish | 129 | 66% | 28 (35.0) | 41 | 49% | 33% |
| Hammer | 100 | 45% | 25 (26.0) | 54 | 30% | 54% |
| 8 Monk | 94 | 33% | 29 (23) | 62 | 20% | 55% |
| Necromancer | 81 | 67% | 29.0 (35) | 26 | 38% | 44% |
| Warrior | 60 | 35% | 28 (20) | 37 | 30% | 37% |
| Monk 4 (WoC) | 58 | 64% | 39 (61.0) | 21 | 50% | 59% |

Double running: single 1402 runs (49% by winners); half 433 runs (51% by winners).

**Flag answers** (answering the enemy's capture): winners: 428 answers, median 38.0 s, 2.0 s slower than possible, 81 answers 30 s+ slower; losers: 402 answers, median 56.0 s, 8.0 s slower than possible, 137 answers 30 s+ slower.

**Skills: kill participation** (share of casts at an enemy who died within 5 s; 15+ casts):

- Highest: Deep Freeze 50% of 22; Signet of Rage 29% of 68; Disrupting Throw 27% of 82; Wounding Strike PvP 27% of 63; Word of Censure 26% of 1869; Chest Thumper 26% of 350; Decapitate 25% of 310; Invoke Lightning 24% of 1543; Twisting Fangs 24% of 89; Fierce Blow 24% of 33; Shatter Storm 23% of 249; Leaping Mantis Sting 23% of 129
- Lowest: Images of Remorse 0% of 20; Ether Feast 0% of 16; Flare 0% of 41; Axe Rake 0% of 19; Crippling Slash 0% of 23; Arcane Languor 0% of 47; Soothing Images 0% of 32; Disrupting Dagger 0% of 22

**Interrupts:** skills interrupted most (whose): Healing Burst on the 7 Monk 295; Guardian on the Prot 223; Guardian on the 8 Monk 207; Blessed Light on the 8 Monk 193; Spirit Light Weapon on the Ritualist 192; Guardian on the 7 Monk 143; Shield Guardian PvP on the Prot 140; Cure Hex on the 7 Monk 132; Blessed Light on the 7 Monk 126; Lightning Strike on the Air Ele 115. Interrupt skills landing most: Power Spike 1603; Complicate 1439; Power Leak 700; Psychic Instability PvP 601; Savage Shot 402; Cry of Frustration 388; Hammer Bash 275; Distracting Shot 207.

**Knockdowns by skill:** Coward 1882; Hammer Bash 1705; Psychic Instability PvP 693; Lightning Surge 514; Mind Shock PvP 393; Bull's Strike 207; Grapple 197; Bane Signet 140.

**Spikes survived** (400+ damage in 3 s on one player; survived = alive 8 s later): winners 268 of 343 (78%); losers 381 of 654 (58%). By target: 7 Monk 65% of 123; Prot 62% of 117; Stand Mes 74% of 90; Mesmer 67% of 86; 8 Monk 54% of 83; AoB Derv 66% of 71; Mes/A 84% of 61; Air Ele 60% of 58; Necromancer 48% of 44; Ritualist 73% of 37; Dervish 66% of 32; Hammer 67% of 30; Warrior 50% of 30; Paragon 69% of 29; Ranger 67% of 18; Water Ele 67% of 18; Fire Ele 50% of 18; Monk 4 (WoC) 77% of 13; Assassin 90% of 10.

**Monks** (per 2-minute phase alive 60 s+): winners: 11.0 casts a minute, 0.49 fakes, idle 0.0 s while an ally was hurt, reaction 1.5 s, bursts answered 71%; losers: 11.6 casts a minute, 0.51 fakes, idle 0 s while an ally was hurt, reaction 1.4 s, bursts answered 60%.

**Deaths** (1940): 603 with a knockdown on the victim; 600 had a monk cast on the victim in the last 5 s. Monk skills interrupted in the 6 s before a death: Blessed Light 94; Healing Burst 70; Guardian 50; Shield Guardian PvP 33; Reversal of Fortune 26; Cure Hex 20; Patient Spirit 15; Word of Healing 13.

## 10. For Denning

- Which curves look wrong to you? A correction (direction, cap, drop, or a pair to always test) is logged with your reason and tested on held-out matches.
- Do any surprises remind you of something the variables don't capture (a missing variable)?
- Any variable you think matters that isn't listed?

