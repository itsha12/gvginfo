# Learning report, batch 8

Trained on 113 matches (22 new in this batch). Variables in use: 31; build variables from 60 matches, interactions from 40.

## 0. Data integrity

- Lengths repaired: 5 (1f65fd3b 150 s -> 1027 s) (bbef1904 617 s -> 599 s) (36a65ac6 1319 s -> 1294 s) (ba85aafc 811 s -> 793 s) (f9d6932f 235 s -> 218 s) 
- Matches with a team's Lord damage not observed (left blank, not zero): 7
- Pit NPCs added from the standard roster (never seen in the replay): 392 in 96 matches
- Left out of training: 0

## 1. The honest test

**Beats strength alone (not yet clear: the range includes 0).** Held-out accuracy (matches held out whole), log loss in brackets (lower is better):

- strength only: all 77% (0.412), 0-5 min 81% (0.344), 5-10 min 79% (0.38), 10-15 min 72% (0.469), 15-end min 70% (0.521), matches lasting 15 min+ 71% (0.515), matches even on strength (gap under 200) 55% (0.63)
- glass box: all 84% (0.367), 0-5 min 84% (0.343), 5-10 min 86% (0.328), 10-15 min 82% (0.444), 15-end min 84% (0.394), matches lasting 15 min+ 81% (0.449), matches even on strength (gap under 200) 71% (0.63)
- glass box without corrections: all 84% (0.405), 0-5 min 83% (0.384), 5-10 min 85% (0.354), 10-15 min 82% (0.492), 15-end min 84% (0.436), matches lasting 15 min+ 80% (0.509), matches even on strength (gap under 200) 70% (0.738)
- black box: all 78% (0.783), 0-5 min 82% (0.65), 5-10 min 79% (0.757), 10-15 min 74% (0.931), 15-end min 74% (0.924), matches lasting 15 min+ 72% (1.007), matches even on strength (gap under 200) 63% (1.347)
- Gain over strength alone (log loss, resampling whole matches): +0.045 (90% range -0.067 to +0.163).
- Change since batch 7: glass box log loss 0.416 -> 0.367; strength only 0.361 -> 0.412.

## 2. What it leans on

- **morale_diff & map_pit_to_stand** 0.464 (was 0.197): own minus enemy morale summed over players (boosts +, death penalty -) TOGETHER WITH the map's distance from a pit to the stand (average of both sides)
- **morale_diff** 0.444 (was 0.515): own minus enemy morale summed over players (boosts +, death penalty -)
- **knights_diff** 0.442 (was 0.446): own minus enemy pit knights alive
- **morale_diff & map_bases_apart** 0.375 (new): own minus enemy morale summed over players (boosts +, death penalty -) TOGETHER WITH the map's distance between the two bases
- **archers_diff & map_bases_apart** 0.35 (new): own minus enemy pit archers alive TOGETHER WITH the map's distance between the two bases
- **knights_diff & map_pit_to_stand** 0.33 (new): own minus enemy pit knights alive TOGETHER WITH the map's distance from a pit to the stand (average of both sides)
- **spike_killable_diff** 0.315 (was 0.238): enemy minus own players within one spike of the other side (DP stacking; 0 unless a spike build is involved)
- **stand** 0.192 (was 0.233): who holds the flag stand: 1 own, 0 nobody, -1 enemy
- **spike_build_own** 0.176 (was 0.347): own build is a spike build (1) or not (0)
- **spike_build_enemy** 0.169 (was 0.328): enemy build is a spike build
- **morale_diff & map_flag_run** 0.167 (was 0.447): own minus enemy morale summed over players (boosts +, death penalty -) TOGETHER WITH the map's flag run Y: distance from the flag spawn to the stand (average of both sides)
- **lord_dps_enemy** 0.159 (was 0.714): enemy build's measured Lord damage per second

## 3. The curves in words

Points = win-chance points added to an otherwise even game at each range of the variable.

- **morale_diff & map_pit_to_stand** (interaction): see wp_model.md
- **morale_diff** rises from -21.2 to +19.3 points (-470.0..-188.5: -21.2; -146.0..-110.5: -16.0; -85.5..-45.5: -12.6; -15.5..-0.5: -1.3; 0.5..17.5: +2.2; 52.5..93.5: +14.0; 134.5..173.5: +17.6)
- **knights_diff** rises from -28.6 to +28.7 points (-2.0..-1.5: -28.6; -1.5..-0.5: -11.9; -0.5..0.5: +0.2; 0.5..1.5: +10.4; 1.5..2.0: +28.7)
- **morale_diff & map_bases_apart** (interaction): see wp_model.md
- **archers_diff & map_bases_apart** (interaction): see wp_model.md
- **knights_diff & map_pit_to_stand** (interaction): see wp_model.md
- **spike_killable_diff** rises from -43.1 to +42.3 points (-8.0..-7.5: -43.1; -5.5..-4.5: -40.4; -3.5..-2.5: -36.5; -1.5..-0.5: -22.5; 0.5..1.5: +21.6; 2.5..4.5: +39.0; 5.5..7.5: +41.1)
- **stand** rises from -5.3 to +5.3 points (-1.0..-0.5: -5.3; -0.5..0.5: -0.1; 0.5..1.0: +5.3)
- **spike_build_own** rises from -2.7 to +11.7 points (0.0..0.5: -2.7; 0.5..1.0: +11.7)
- **spike_build_enemy** falls from +2.6 to -11.3 points (0.0..0.5: +2.6; 0.5..1.0: -11.3)

## 4. Discovery

**Interaction candidates** (a screen: pairs whose combination seems to matter beyond each alone; untested until held-out matches confirm them; switched on in the model from 40 matches):

- spike_killable_diff with map_pit_to_stand (screen 0.151)
- morale_diff with spike_killable_diff (screen 0.137)
- morale_diff with spike_build_own (screen 0.125)
- morale_diff with spike_build_enemy (screen 0.125)
- alive_diff with morale_diff (screen 0.116)
- morale_diff with map_pit_to_stand (screen 0.115)
- down_diff_s with morale_diff (screen 0.113)
- morale_diff with lord_dps_enemy (screen 0.113)

**Candidate variables** (proposed variables, tested on unseen matches; log loss, lower is better):

- split_diff: 0.367 without, 0.37 with: does not improve yet. own minus enemy players on a split (away from their main group on the enemy half, not carrying). Proposed batch 1 by Claude: the knights curve runs backwards, maybe standing in for the cost of splitting
- turtle_diff: 0.367 without, 0.368 with: does not improve yet. own minus enemy share of live players at home (own base or pit). Proposed 2026-11-06 from OG comms ([ohno v One], [ohno v Crew]: 'they are turtling, we have to make a play'); comms_vars.py: teams that turtled 60 s won 3 of 13 times
- footmen_diff: 0.367 without, 0.373 with: does not improve yet. own minus enemy footmen alive (base NPCs, not pit NPCs). Proposed 2026-11-06 from OG comms ([ohno v NwAy]: 'this way we don't lose footmen'; [ohno v Fun]: fake collapse to the footmen)
- no_healer_groups_diff: 0.367 without, 0.368 with: does not improve yet. own minus enemy groups of 2+ with no healer. Proposed 2026-11-06 from OG comms ([ohno v One]: keep a prot and a monk on one side, the Rit and a monk on the other); comms_vars.py: such groups lose players twice as often
- solo_healers_diff: 0.367 without, 0.369 with: does not improve yet. own minus enemy healers with no other own healer within casting range. Proposed 2026-11-06 from OG comms ('solo monk, go on the monk'); Denning: a monk alone has no other monk to support it

**Surprises** (moments where the held-out model was most confident about the team that went on to lose; each points to something the variables don't capture yet):

- hdm v HC (28447c4a) at 16:45: a model that never saw this match gave HC 0.0%, and HC won. Why it thought so: morale_diff & map_bases_apart -43.1, lord_damage_diff -36.1, knights_diff -33.4, morale_diff -22.1, knights_diff & map_flag_run -19.4
- BcS v Apes (5cb6a1d7) at 5:45: a model that never saw this match gave Apes 20.6%, and Apes won. Why it thought so: team strength -26.0, knights_diff & map_pit_to_stand +12.7, morale_diff & map_pit_to_stand +11.0, fight_state -9.7, morale_diff & map_bases_apart -7.0
- RACK v hdm (1f65fd3b) at 14:30: a model that never saw this match gave RACK 0.8%, and RACK won. Why it thought so: knights_diff -30.1, morale_diff -15.7, team strength -14.0, knights_diff & map_flag_run -11.1, lord_damage_diff & lord_dps_enemy -8.8
- OG v hold (49eec28d) at 4:00: a model that never saw this match gave OG 0.8%, and OG won. Why it thought so: morale_diff & map_pit_to_stand -28.7, morale_diff -24.9, team strength +19.0, morale_diff & lord_dps_enemy -13.1, morale_diff & lord_dps_own -12.2
- Crew v BcS (3ee18c0c) at 8:00: a model that never saw this match gave BcS 7.1%, and BcS won. Why it thought so: knights_diff -11.5, morale_diff & lord_dps_enemy -11.3, morale_diff -9.8, lord_damage_diff & lord_dps_enemy -5.8, stand -5.3
- Team v push (2df9b7fd) at 2:30: a model that never saw this match gave push 97.0%, and push lost. Why it thought so: team strength -48.1, spike_killable_diff +46.0, morale_diff & lord_dps_own +40.0, morale_diff & map_pit_to_stand +19.0, knights_diff & map_pit_to_stand -13.8

## 5. Denning's rulings seen through the model

Win chance from a model that never saw the match, 20 s before and 60 s after each ruled moment. Contributions are points for an otherwise even game (the curves' scale).

- hdm v HC (28447c4a) 5:01 (split answered), HC: 38.5% 20 s before -> 50.2% 60 s after (+11.7). After: morale_diff & map_bases_apart +42.1, knights_diff -33.4, knights_diff & map_flag_run -19.4, archers_diff & map_bases_apart +14.0
- hdm v HC (28447c4a) 5:01 (split answered), hdm: 61.0% 20 s before -> 47.0% 60 s after (-14.0). After: morale_diff & map_bases_apart -42.7, knights_diff +33.3, knights_diff & map_flag_run +20.8, archers_diff & map_bases_apart -13.2
- hdm v HC (28447c4a) 1:02 (split detection), HC: 39.4% 20 s before -> 68.7% 60 s after (+29.3). After: morale_diff & map_bases_apart +37.6, morale_diff & lord_dps_enemy -9.1, stand -6.1, carrying_diff -5.8
- hdm v HC (28447c4a) 1:02 (split detection), hdm: 59.6% 20 s before -> 31.5% 60 s after (-28.1). After: morale_diff & map_bases_apart -37.2, morale_diff & lord_dps_own +8.0, stand +6.2, team strength +5.4
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), HC: 40.4% 20 s before -> 26.2% 60 s after (-14.2). After: morale_diff & map_bases_apart +42.1, knights_diff -33.4, knights_diff & map_flag_run -19.4, lord_exposed_diff -18.3
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), hdm: 59.8% 20 s before -> 69.0% 60 s after (+9.2). After: morale_diff & map_bases_apart -42.7, knights_diff +33.3, knights_diff & map_flag_run +20.8, lord_exposed_diff +20.2
- hdm v HC (bbef1904) 8:10 (death), HC: 42.9% 20 s before -> 28.0% 60 s after (-14.9). After: down_diff_s -11.2, fight_state -9.7, morale_diff & map_bases_apart +9.4, morale_diff -8.0
- hdm v HC (bbef1904) 8:10 (death), hdm: 49.9% 20 s before -> 67.4% 60 s after (+17.5). After: fight_state +9.5, morale_diff & map_pit_to_stand -9.5, down_diff_s +8.5, morale_diff & map_bases_apart -7.0
- Men v HC (faec428a) 9:31 (death), HC: 15.1% 20 s before -> 27.7% 60 s after (+12.6). After: archers_diff & map_bases_apart -12.4, archers_diff +9.5, knights_diff & map_pit_to_stand -7.5, knights_diff -6.3
- Men v HC (faec428a) 9:31 (death), Men: 84.3% 20 s before -> 71.3% 60 s after (-13.0). After: archers_diff & map_bases_apart +13.2, archers_diff -9.3, knights_diff & map_pit_to_stand +7.4, knights_diff +6.7

## 6. Why: the node models

Each explains one result from what happened before it (time order enforced), tested on matches it never saw. AUC = how often a moment that led to the result scores above one that didn't (0.5 = guessing, 1 = perfect).

**deaths** (113 matches, 225220 moments, 6766 results): adds to the simple baseline (AUC 0.921 against 0.799 for health_pct and damage_taken_3s alone).
- **enemies_near** (enemies within 1,500) rises from -23.6 to +27.1 points (0.0..0.5: -23.6; 0.5..1.5: -12.9; 1.5..2.5: +1.6; 2.5..3.5: +6.4; 3.5..4.5: +10.4; 4.5..5.5: +12.4; 5.5..6.5: +14.8; 6.5..7.5: +18.4; 7.5..8.0: +27.1)
- **strength_gap** (own minus enemy team strength) falls from +18.0 to -14.0 points (-989.0..-581.0: +18.0; -434.5..-353.5: +7.1; -248.0..-103.5: +11.7; -40.0..4.5: -2.8; 64.0..108.0: -0.9; 251.5..353.5: -4.7; 434.5..572.5: -14.6)
- **health_pct** (current health %) falls from +40.6 to -5.9 points (1.0..48.5: +40.6; 60.5..68.5: +21.1; 74.5..78.5: +8.7; 82.5..85.5: +3.9; 88.5..91.5: +0.8; 93.5..95.5: -2.3; 97.5..99.5: -4.7)
- **allies_near** (allies within 1,500) falls from +20.0 to -8.2 points (0.0..0.5: +20.0; 0.5..1.5: +8.5; 1.5..2.5: +4.5; 2.5..3.5: -0.9; 3.5..4.5: -1.8; 4.5..5.5: -4.1; 5.5..6.5: -5.4; 6.5..7.0: -8.2)
- **local_diff** (allies minus enemies within 2,000) falls from +23.4 to -11.7 points (-8.0..-3.5: +23.4; -2.5..-1.5: +12.0; -0.5..0.5: -4.0; 1.5..2.5: -7.9; 3.5..4.5: +5.6; 5.5..7.0: -11.7)
- **enemy_strips** (enemy enchantment removal skills) falls from +25.5 to +0.3 points (0.0..0.5: +25.5; 0.5..1.5: +3.7; 1.5..2.5: +2.9; 2.5..3.5: -4.6; 3.5..4.5: -5.1; 4.5..5.5: -5.1; 5.5..6.5: -7.5; 6.5..7.0: +0.3)
- **own_prots** (own prot skills) is flat from +4.8 to +4.6 points (1.0..4.5: +4.8; 6.5..7.5: +10.0; 8.5..9.5: +1.0; 10.5..11.5: +0.3; 12.5..13.5: -5.3; 14.5..15.5: -3.0)
- **dist_own_pit** (distance from its own pit) rises from -3.1 to +11.5 points (10.0..1354.5: -3.1; 2315.5..3930.5: -2.6; 5110.5..6021.5: -3.7; 6829.5..7544.5: -1.3; 8219.5..8903.5: -1.8; 9818.5..10744.5: +0.9; 11930.5..13437.5: +11.2)
- **minute** (match minute) rises from -0.7 to +15.3 points (0.1..1.15: -0.7; 2.05..3.05: -4.7; 4.15..5.15: -4.5; 6.25..7.55: +1.6; 9.05..10.65: -2.4; 12.55..14.75: -2.2; 17.55..20.95: +5.7)

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

**flag answer** (seconds an answer to an enemy capture was slower than possible; 94 matches, 825 rows): adds to the simple baseline (typical error 17.1s against 28.7s for the median; explains 72% of the spread).
- **parked_s** (seconds the flag lay parked (dropped 5 s or more: not running yet)): 0.0..2.5: -5.9 s; 9.5..14.5: +4.2 s; 20.5..28.5: +18.9 s; 33.5..38.5: +36.8 s; 45.5..60.0: +53.1 s; 76.5..98.5: +63.7 s; 115.5..246.5: +65.2 s
- **own_deaths_during** (own deaths during the answer): 0.0..0.5: -4.2 s; 0.5..1.5: +8.6 s; 1.5..2.5: +15.7 s; 2.5..3.5: +23.9 s; 3.5..4.5: +32.2 s; 4.5..5.5: +38.4 s; 5.5..6.5: +52.8 s; 6.5..9.5: +65.5 s; 9.5..17.0: +80.7 s
- **enemies_in_the_way** (enemy presence along the runner's trip back to the spawn): 0.0..0.5: -6.2 s; 4.5..10.5: -4.7 s; 15.5..20.5: -2.8 s; 26.5..36.5: -0.5 s; 48.5..61.5: +3.1 s; 85.5..108.5: +8.6 s; 144.5..203.0: +17.2 s
- **enemy_deaths_during** (enemy deaths during the answer): 0.0..0.5: -3.8 s; 0.5..1.5: +9.2 s; 1.5..2.5: +16.7 s; 2.5..3.5: +22.5 s; 3.5..4.5: +24.6 s; 4.5..7.0: +25.5 s
- **carrier_damage_taken** (damage the carrier took while carrying): 0.0..0.5: -4.2 s; 28.5..51.5: -4.3 s; 76.5..101.5: -2.9 s; 135.5..198.5: +0.7 s; 251.5..300.0: +2.9 s; 400.5..538.5: +6.3 s; 678.5..1095.0: +14.1 s
- **runner_to_spawn** (runner's distance to its flag spawn when the enemy captured): 16.0..704.0: -12.1 s; 1277.5..1827.0: -5.7 s; 2519.0..3266.5: -0.8 s; 3880.5..4288.0: +2.0 s; 4740.0..5384.0: +4.1 s; 6172.5..6851.5: +5.2 s; 7561.5..8659.5: +5.6 s
- **quick_handoffs** (quick hand-offs (a teammate picked it up within 5 s)): 0.0..0.5: -1.8 s; 0.5..1.5: +6.1 s; 1.5..2.5: +7.8 s; 2.5..3.0: +11.1 s
- **morale_diff** (own minus enemy morale): -219.0..-110.5: +5.9 s; -76.5..-48.0: +4.9 s; -31.0..-17.5: +2.5 s; -6.5..1.0: +0.7 s; 14.0..17.0: -0.9 s; 41.5..67.5: -4.6 s; 92.5..134.0: -6.2 s
- **possible_s** (fastest possible answer (s) from the flag model at the enemy's capture): 0.0..3.5: -2.6 s; 8.5..13.5: -1.8 s; 21.5..26.5: +0.1 s; 31.5..34.5: +1.7 s; 37.5..40.5: +3.6 s; 44.5..49.5: +1.0 s; 55.5..62.5: -1.6 s
- **own_fighting_at_enemy_cap** (own players fighting when the enemy captured): 0.0..0.5: +6.6 s; 0.5..1.5: +1.5 s; 1.5..2.5: -1.0 s; 2.5..3.5: -0.4 s; 3.5..4.5: -1.7 s; 4.5..5.5: -1.6 s; 5.5..6.5: +0.0 s; 6.5..7.5: -2.7 s; 7.5..8.0: -17.5 s

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


## 6b. The learned nodes (step 2 of the learned causal map)

Each node uses only the causal-map links into it. A link's strength is how much worse the node predicts matches it never saw without that link's features (refit without them, same folds); supported when the gain is more than twice its spread across folds, rejected when dropping it helps by more than that, otherwise not clear yet.

**run outcome** (map R.3; 113 matches, 3695 cases, result rate 60%): log loss 0.6462 against 0.6746 for the simple baseline (adds to the simple baseline).
- link P.10 -> R.3: gain +0.0136 (+/- 0.0061), supported (stand_own, stand_enemy, enemy_boost_in, flag_lead...)
- link A.allocation -> R.3: gain +0.0029 (+/- 0.0044), not clear yet (escort, own_main, enemy_main, enemy_power_play)
- link C.map -> R.3: gain +0.0025 (+/- 0.0018), not clear yet (run_dist)
- link K.11 -> R.3: gain +0.0012 (+/- 0.0017), not clear yet (crippled_so_far, knocked_down_so_far, other_control_so_far, damage_so_far...)
- link C.strength -> R.3: gain -0.0052 (+/- 0.004), not clear yet (strength_gap)
  - leans on **checkpoint_s** (seconds into the run): -6.1 points at 5.0 to 10.0, +13.1 at 22.5 to 30.0
  - leans on **flag_lead** (flag lead at the start (s)): +2.3 points at -80.0 to -58.5, -11.2 at 60.5 to 129.0
  - leans on **enemy_boost_in** (seconds to the enemy's boost (if it holds)): -17.7 points at 0.0 to 26.5, +7.8 at 116.5 to 120.0

**flag swing** (map R.3; 113 matches, 4234 cases, average -0.2 s): mean absolute error (s) 29.3941 against 29.7057 for the simple baseline (no better than the simple baseline yet).
- link P.10 -> R.3: gain +0.41 (+/- 0.12), supported (waiting_runner, backup_flag, stand_own, stand_enemy...)
- link C.strength -> R.3: gain +0.25 (+/- 0.16), not clear yet (strength_gap)
- link S.scoreboard -> R.3: gain +0.15 (+/- 0.42), not clear yet (flag_lead)
- link R.1 -> R.3: gain +0.06 (+/- 0.08), not clear yet (own_deaths_30s, enemy_deaths_30s)
- link C.map -> R.3: gain -0.0 (+/- 0.03), not clear yet (run_dist)
- link C.clock -> R.3: gain -0.01 (+/- 0.03), not clear yet (minute, res_in)
- link A.allocation -> R.3: gain -0.1 (+/- 0.05), rejected (own_alive, enemy_alive, own_main, enemy_main...)
  - leans on **flag_lead** (flag lead now (s)): +27.9 s at -129.0 to -63.5, -28.2 at 62.5 to 110.0
  - leans on **strength_gap** (team strength gap): -6.2 s at -989.0 to -565.5, +7.4 at 572.5 to 989.0
  - leans on **own_boost_in** (seconds to own boost): +1.2 s at 0.0 to 17.5, -1.8 at 114.5 to 120.0

**run defence** (map R.3; 113 matches, 3695 cases, result rate 60%): log loss 0.6615 against 0.6746 for the simple baseline (adds to the simple baseline).
- link C.map -> R.3: gain +0.0035 (+/- 0.0036), not clear yet (run_dist)
- link A.allocation -> R.3: gain -0.0007 (+/- 0.0027), not clear yet (escort, att_main, def_main)
- link A.mesa_free -> R.3: gain -0.0014 (+/- 0.0011), not clear yet (def_free, pushers_so_far, control_so_far, damage_so_far)
- link C.strength -> R.3: gain -0.0074 (+/- 0.0041), not clear yet (strength_gap)
  - leans on **checkpoint_s** (seconds into the run): -5.8 points at 5.0 to 10.0, +12.7 at 22.5 to 30.0
  - leans on **run_dist** (distance from the runner's spawn to the stand): +13.8 points at 4170.0 to 4275.0, +0.2 at 9258.0 to 9329.0
  - leans on **pushers_so_far** (defenders who pushed the runner by this point): -1.3 points at 0.0 to 0.5, +7.6 at 3.5 to 7.0

**capture speed** (map R.3; 105 matches, 859 cases, average 40.0 s): mean absolute error (s) 16.8976 against 16.2398 for the simple baseline (no better than the simple baseline yet).
- link A.allocation -> R.3: gain +0.38 (+/- 0.26), not clear yet (defenders_free, escort)
- link C.strength -> R.3: gain +0.2 (+/- 0.06), supported (strength_gap)
- link C.map -> R.3: gain +0.05 (+/- 0.09), not clear yet (run_dist)
  - leans on **escort** (the runner's escorts): -4.4 s at 0.0 to 0.5, +29.5 at 6.5 to 7.0
  - leans on **defenders_free** (defenders alive and not on flag duty): -6.8 s at 2.0 to 3.5, +3.4 at 7.5 to 8.0
  - leans on **strength_gap** (defending team's strength gap): -7.1 s at -989.0 to -545.0, -0.7 at 530.0 to 976.0

**power play** (map K.4; 113 matches, 948 cases, result rate 40%): log loss 0.3968 against 0.6787 for the simple baseline (adds to the simple baseline).
- link A.allocation -> K.4: gain +0.0506 (+/- 0.0164), supported (size, own_main, enemy_main, short_dead...)
- link K.5 -> K.4: gain +0.0197 (+/- 0.0056), supported (enemy_prots_10s, enemy_heal_s)
- link P.14 -> K.4: gain +0.0092 (+/- 0.0064), not clear yet (pushed)
- link K.2 -> K.4: gain +0.0051 (+/- 0.0057), not clear yet (dps_v_usual)
- link C.strength -> K.4: gain +0.0042 (+/- 0.0088), not clear yet (strength_gap)
- link K.11 -> K.4: gain +0.0011 (+/- 0.0005), supported (blinds_on_own_10s)
- link R.3 -> K.4: gain -0.0001 (+/- 0.0013), not clear yet (flag_lead)
- link P.1 -> K.4: gain -0.0022 (+/- 0.0012), not clear yet (spikes_on_healers)
- link P.2 -> K.4: gain -0.0042 (+/- 0.0033), not clear yet (spikes_10s, spike_spread)
  - leans on **short_dead** (share of the enemy's missing player-seconds: dead): -19.0 points at 0.0 to 0.01, +20.6 at 0.99 to 1.0
  - leans on **window_s** (seconds the power play lasted): -12.9 points at 14.0 to 31.5, +31.8 at 105.5 to 290.0
  - leans on **enemy_prots_10s** (enemy prot casts per 10 s): +19.2 points at 0.0 to 0.58, -18.2 at 4.51 to 6.77

**fight outcome** (map R.2; 113 matches, 831 cases, result rate 47%): log loss 0.3866 against 0.6908 for the simple baseline (adds to the simple baseline).
- link C.strength -> R.2: gain +0.0579 (+/- 0.0083), supported (strength_gap)
- link A.allocation -> R.2: gain +0.0399 (+/- 0.0095), supported (own_local, enemy_local)
- link K.1 -> R.2: gain +0.0313 (+/- 0.0142), supported (dps_v_usual_diff)
- link P.2 -> R.2: gain +0.0222 (+/- 0.0102), supported (spike_spread_diff, spikes_diff)
- link P.17 -> R.2: gain +0.0105 (+/- 0.0086), not clear yet (ready_interrupt_diff, dazed_casts_diff, blind_attacks_diff)
- link P.5 -> R.2: gain +0.0005 (+/- 0.0029), not clear yet (hex_secs_diff, hex_right_diff)
- link P.18 -> R.2: gain -0.0012 (+/- 0.005), not clear yet (strip_right_diff, strip_value_diff)
- link P.13 -> R.2: gain -0.0013 (+/- 0.0019), not clear yet (peel_defensive_diff)
- link P.19 -> R.2: gain -0.0028 (+/- 0.0012), rejected (blind_front_diff, blind_defensive_diff)
  - leans on **strength_gap** (team strength gap): -32.1 points at -989.0 to -623.0, +30.8 at 639.0 to 989.0
  - leans on **own_local** (own players in the fight): -34.0 points at 0.0 to 0.5, +22.7 at 7.5 to 8.0
  - leans on **enemy_local** (enemy players in the fight): +31.9 points at 0.0 to 0.5, -26.2 at 7.5 to 8.0

**split chance** (map A.allocation; 113 matches, 8133 cases, result rate 14%): log loss 0.3786 against 0.4081 for the simple baseline (adds to the simple baseline).
- link S.scoreboard -> A.allocation: gain +0.0167 (+/- 0.0056), supported (flag_lead, own_alive, enemy_alive, own_main...)
- link C.builds -> A.allocation: gain +0.0029 (+/- 0.0053), not clear yet (own_speed, own_snares, enemy_snares)
- link C.strength -> A.allocation: gain +0.001 (+/- 0.0037), not clear yet (strength_gap)
- link C.clock -> A.allocation: gain +0.0009 (+/- 0.0019), not clear yet (minute, res_in)
  - leans on **own_main** (own main): +22.2 points at 0.0 to 2.5, -17.4 at 7.5 to 8.0
  - leans on **own_snares** (snares on own bars): -10.8 points at 0.0 to 0.5, +0.7 at 11.5 to 14.0
  - leans on **strength_gap** (team strength gap): -10.3 points at -989.0 to -581.0, +7.4 at 556.0 to 989.0

**split answer** (map P.11; 78 matches, 314 cases, average -4.8 s): mean absolute error (s) 16.9482 against 18.1847 for the simple baseline (adds to the simple baseline).
- link A.mesa_free -> P.11: gain +0.57 (+/- 0.31), not clear yet (def_free, nearest_to_base)
- link A.allocation -> P.11: gain +0.54 (+/- 0.4), not clear yet (size)
- link S.scoreboard -> P.11: gain +0.04 (+/- 0.2), not clear yet (flag_lead, def_alive, att_main)
- link C.strength -> P.11: gain -0.02 (+/- 0.12), not clear yet (strength_gap)
- link C.clock -> P.11: gain -0.06 (+/- 0.08), not clear yet (minute)
  - leans on **size** (split size): +11.2 s at 1.0 to 1.5, -10.2 at 5.5 to 7.0
  - leans on **nearest_to_base** (nearest defender to its base at the split's entry): +3.3 s at 31.0 to 383.5, +12.7 at 6688.5 to 12934.0
  - leans on **att_main** (attackers' main): +9.7 s at 1.0 to 1.5, -2.4 at 7.5 to 8.0

**split effect** (map R.5; 78 matches, 314 cases, result rate 41%): log loss 0.6807 against 0.6807 for the simple baseline (no better than the simple baseline yet).
- link P.11 -> R.5: gain +0.0035 (+/- 0.0031), not clear yet (latency, defenders)
- link K.8 -> R.5: gain +0.0005 (+/- 0.0008), not clear yet (split_healers)
- link C.strength -> R.5: gain +0.0005 (+/- 0.0033), not clear yet (strength_gap)
- link A.allocation -> R.5: gain -0.0011 (+/- 0.0017), not clear yet (size, main_diff)
  - leans on **latency** (seconds until the first defender arrived (60 = never)): +0.3 points at -30.0 to -29.5, -0.0 at 56.5 to 60.0
  - leans on **defenders** (defenders who came): +0.2 points at 0.0 to 0.5, +0.0 at 7.5 to 8.0
  - leans on **main_diff** (own main minus enemy main meanwhile): -0.1 points at -5.1 to -2.45, +0.3 at 1.7 to 6.0

**collapse** (map R.1; 103 matches, 742 cases, result rate 12%): log loss 0.3391 against 0.3726 for the simple baseline (adds to the simple baseline).
- link P.9 -> R.1: gain +0.0121 (+/- 0.0021), supported (defenders_10s, contact_diff, npc_hit_to_arrival, res_in_at_arrival)
  - alone: defenders_10s (defenders arriving within 10 s of the first (arrival spread)): gain +0.0028 (+/- 0.0024), not clear yet
  - alone: contact_diff (defenders arriving within 5 s of the first, minus the split's size (numbers at contact)): gain -0.0003 (+/- 0.0015), not clear yet
  - alone: npc_hit_to_arrival (seconds from the split's first hit on an NPC to the first defender's arrival): gain +0.0053 (+/- 0.0044), not clear yet
  - alone: res_in_at_arrival (seconds to the next res when the first defender arrived): gain +0.0002 (+/- 0.0015), not clear yet
- link C.builds -> R.1: gain +0.0064 (+/- 0.0036), not clear yet (def_snares, split_speed)
- link A.allocation -> R.1: gain +0.0047 (+/- 0.0016), supported (size, main_diff)
- link C.strength -> R.1: gain +0.004 (+/- 0.0035), not clear yet (strength_gap)
- link P.11 -> R.1: gain +0.0022 (+/- 0.0016), not clear yet (latency)
- link K.13 -> R.1: gain -0.0009 (+/- 0.0011), not clear yet (escape_ready)
  - leans on **defenders_10s** (defenders arriving within 10 s of the first (arrival spread)): -10.2 points at 0.0 to 0.5, +18.9 at 7.5 to 8.0
  - leans on **npc_hit_to_arrival** (seconds from the split's first hit on an NPC to the first defender's arrival): -5.1 points at -1537.9 to -248.9, +14.1 at 10.55 to 194.5
  - leans on **def_snares** (snares on the defending team's bars): -4.8 points at 0.0 to 0.5, +21.9 at 9.5 to 14.0

## 7. The usual play

Each choice against the most common one in that kind of decision, in win-chance points over the decision's window, adjusted for the situation, with a 90% range from resampling whole matches. CLEAR = the range excludes 0. Win chance comes from a model that never saw the match. The same comparison over the 30 s BEFORE the decision is a placebo test: a choice can't cause what came before it, so a clear difference there means the effect is partly who makes that choice.

**after wipe** (247 decisions, 106 matches; usual: pushed the pit)
- reset (n 31): -4.2 [-7.3, -0.6] CLEAR; in the 30 s before: +0.1 [-4.0, +4.1]
- took the flag (n 29): -10.4 [-14.8, -4.9] CLEAR; in the 30 s before: +2.5 [-4.7, +9.0]

**boost clock** (411 decisions, 102 matches; usual: not running, fought)
- running, fought (n 65): +4.3 [+1.2, +7.5] CLEAR; in the 30 s before: -0.1 [-1.8, +1.6]
- not running, advanced (n 49): -1.0 [-3.2, +1.0]; in the 30 s before: +1.2 [-0.6, +2.7]
- not running, fell back (n 44): -4.1 [-7.9, -0.4] CLEAR; in the 30 s before: +1.2 [-1.6, +4.2]
- running, advanced (n 43): +3.9 [-0.3, +8.2]; in the 30 s before: -0.2 [-3.0, +2.2]
- not running, held (n 27): +0.8 [-1.1, +3.0]; in the 30 s before: +1.0 [-1.3, +2.2]
- not running, to the spawn (n 22): +0.6 [-1.3, +3.4]; in the 30 s before: +1.8 [-0.8, +3.8]
- running, fell back (n 19): -1.3 [-6.0, +3.5]; in the 30 s before: +0.2 [-2.9, +2.4]
- running, held (n 12): +4.5 [+0.1, +11.3] CLEAR; in the 30 s before: +6.5 [+2.1, +15.4] ALREADY DIFFERENT BEFORE: partly who chooses it
- not running (n 5): +6.2 [-1.9, +17.2]; in the 30 s before: +3.3 [-2.2, +10.9]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - running, fought, behind in the fight (lowest third, -0.09 or less): -1.0 (n 17 against 61)
  - running, fought, middle third: +2.6 (n 23 against 41)
  - running, fought, ahead in the fight (top third, above -0.01): +2.1 (n 25 against 23)
  - not running, advanced, behind in the fight (lowest third, -0.09 or less): +0.1 (n 11 against 61)
  - not running, advanced, middle third: +0.8 (n 16 against 41)
  - not running, advanced, ahead in the fight (top third, above -0.01): -2.2 (n 22 against 23)
  - not running, fell back, behind in the fight (lowest third, -0.09 or less): -0.5 (n 18 against 61)
  - not running, fell back, middle third: +3.6 (n 14 against 41)
  - not running, fell back, ahead in the fight (top third, above -0.01): -21.8 (n 12 against 23)
  - running, advanced, behind in the fight (lowest third, -0.09 or less): too few yet (n 1 against 61; means 2.3 against -0.5)
  - running, advanced, middle third: -5.3 (n 19 against 41)
  - running, advanced, ahead in the fight (top third, above -0.01): +5.9 (n 23 against 23)
  - not running, held, behind in the fight (lowest third, -0.09 or less): too few yet (n 7 against 61; means -1.0 against -0.5)
  - not running, held, middle third: too few yet (n 6 against 41; means -0.7 against -2.7)
  - not running, held, ahead in the fight (top third, above -0.01): +0.2 (n 14 against 23)
  - not running, to the spawn, behind in the fight (lowest third, -0.09 or less): -1.3 (n 13 against 61)
  - not running, to the spawn, middle third: too few yet (n 5 against 41; means -1.3 against -2.7)
  - not running, to the spawn, ahead in the fight (top third, above -0.01): too few yet (n 4 against 23; means -3.6 against -1.9)
  - running, fell back, behind in the fight (lowest third, -0.09 or less): too few yet (n 4 against 61; means -0.7 against -0.5)
  - running, fell back, middle third: too few yet (n 9 against 41; means -8.6 against -2.7)
  - running, fell back, ahead in the fight (top third, above -0.01): too few yet (n 6 against 23; means -4.5 against -1.9)
  - running, held, behind in the fight (lowest third, -0.09 or less): too few yet (n 1 against 61; means 0.0 against -0.5)
  - running, held, middle third: too few yet (n 8 against 41; means -0.4 against -2.7)
  - running, held, ahead in the fight (top third, above -0.01): too few yet (n 3 against 23; means 4.1 against -1.9)
  - not running, behind in the fight (lowest third, -0.09 or less): too few yet (n 4 against 61; means -0.1 against -0.5)
  - not running, middle third: too few yet (n 1 against 41; means 0.1 against -2.7)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - running, fought, Isle of Jade: -1.4 (n 10 against 29)
  - running, fought, Isle of Meditation: +3.2 (n 10 against 30)
  - running, fought, Isle of Solitude: -1.0 (n 12 against 12)
  - running, fought, Uncharted Isle: +5.9 (n 11 against 19)
  - not running, advanced, Isle of Meditation: +0.5 (n 14 against 30)
  - not running, advanced, Uncharted Isle: +1.0 (n 10 against 19)
  - not running, fell back, Isle of Meditation: -6.1 (n 10 against 30)
  - not running, fell back, Isle of Solitude: -3.3 (n 10 against 12)
  - running, advanced, Isle of Meditation: +1.1 (n 12 against 30)
  - not running, held, Isle of Jade: +2.7 (n 10 against 29)

**enemy pickup** (1503 decisions, 108 matches; usual: held, fought)
- already running, fought (n 207): -1.0 [-3.3, +1.7]; in the 30 s before: +1.7 [-0.2, +3.6]
- held, advanced (n 196): +3.1 [-1.7, +9.6]; in the 30 s before: -1.6 [-6.4, +3.3]
- already running, advanced (n 174): +1.0 [-1.4, +4.4]; in the 30 s before: +2.6 [+1.2, +4.5] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, fell back (n 147): -4.3 [-7.6, -0.9] CLEAR; in the 30 s before: +0.1 [-1.9, +2.7]
- already running, fell back (n 94): -0.2 [-2.8, +3.6]; in the 30 s before: +1.0 [-0.6, +2.6]
- ran, fought (n 93): +1.7 [-0.5, +5.3]; in the 30 s before: -0.3 [-2.2, +1.6]
- ran, fell back (n 89): +0.2 [-2.2, +3.3]; in the 30 s before: -0.5 [-3.1, +1.8]
- ran, advanced (n 89): +0.6 [-3.1, +4.3]; in the 30 s before: +0.1 [-2.4, +2.2]
- already running, held (n 47): -2.4 [-4.7, +0.6]; in the 30 s before: +1.0 [-0.7, +2.6]
- ran, held (n 33): -4.8 [-9.9, +1.8]; in the 30 s before: +1.7 [-1.6, +4.7]
- held, held (n 31): -0.4 [-6.1, +5.4]; in the 30 s before: -1.0 [-6.1, +4.6]
- held, to the spawn (n 16): -6.6 [-13.4, +1.5]; in the 30 s before: +2.2 [-8.8, +11.2]
- ran, to the spawn (n 6): -6.6 [-15.9, +2.8]; in the 30 s before: +5.7 [-3.0, +16.4]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - already running, fought, behind in the fight (lowest third, -0.01 or less): +3.2 (n 62 against 99)
  - already running, fought, middle third: -1.6 (n 72 against 48)
  - already running, fought, ahead in the fight (top third, above +0.02): -4.3 (n 73 against 134)
  - held, advanced, behind in the fight (lowest third, -0.01 or less): +9.1 (n 37 against 99)
  - held, advanced, middle third: +1.9 (n 77 against 48)
  - held, advanced, ahead in the fight (top third, above +0.02): +0.9 (n 82 against 134)
  - already running, advanced, behind in the fight (lowest third, -0.01 or less): +4.7 (n 45 against 99)
  - already running, advanced, middle third: -0.6 (n 73 against 48)
  - already running, advanced, ahead in the fight (top third, above +0.02): -1.3 (n 56 against 134)
  - held, fell back, behind in the fight (lowest third, -0.01 or less): -3.4 (n 63 against 99)
  - held, fell back, middle third: -3.5 (n 44 against 48)
  - held, fell back, ahead in the fight (top third, above +0.02): -3.6 (n 40 against 134)
  - already running, fell back, behind in the fight (lowest third, -0.01 or less): +5.8 (n 45 against 99)
  - already running, fell back, middle third: -3.2 (n 31 against 48)
  - already running, fell back, ahead in the fight (top third, above +0.02): -3.0 (n 18 against 134)
  - ran, fought, behind in the fight (lowest third, -0.01 or less): +6.3 (n 32 against 99)
  - ran, fought, middle third: -0.8 (n 37 against 48)
  - ran, fought, ahead in the fight (top third, above +0.02): +0.3 (n 24 against 134)
  - ran, fell back, behind in the fight (lowest third, -0.01 or less): +4.3 (n 37 against 99)
  - ran, fell back, middle third: -1.3 (n 31 against 48)
  - ran, fell back, ahead in the fight (top third, above +0.02): -2.1 (n 21 against 134)
  - ran, advanced, behind in the fight (lowest third, -0.01 or less): +5.8 (n 27 against 99)
  - ran, advanced, middle third: +2.5 (n 34 against 48)
  - ran, advanced, ahead in the fight (top third, above +0.02): -5.2 (n 28 against 134)
  - already running, held, behind in the fight (lowest third, -0.01 or less): +0.8 (n 13 against 99)
  - already running, held, middle third: -3.0 (n 28 against 48)
  - already running, held, ahead in the fight (top third, above +0.02): too few yet (n 6 against 134; means -1.3 against 3.0)
  - ran, held, behind in the fight (lowest third, -0.01 or less): +10.7 (n 15 against 99)
  - ran, held, middle third: -0.5 (n 10 against 48)
  - ran, held, ahead in the fight (top third, above +0.02): too few yet (n 8 against 134; means -34.6 against 3.0)
  - held, held, behind in the fight (lowest third, -0.01 or less): +9.4 (n 10 against 99)
  - held, held, middle third: -0.8 (n 17 against 48)
  - held, held, ahead in the fight (top third, above +0.02): too few yet (n 4 against 134; means -5.7 against 3.0)
  - held, to the spawn, behind in the fight (lowest third, -0.01 or less): -0.9 (n 13 against 99)
  - held, to the spawn, middle third: too few yet (n 1 against 48; means -0.4 against 0.9)
  - held, to the spawn, ahead in the fight (top third, above +0.02): too few yet (n 2 against 134; means -4.2 against 3.0)
  - ran, to the spawn, behind in the fight (lowest third, -0.01 or less): too few yet (n 3 against 99; means -11.3 against -3.0)
  - ran, to the spawn, middle third: too few yet (n 1 against 48; means 0.0 against 0.9)
  - ran, to the spawn, ahead in the fight (top third, above +0.02): too few yet (n 2 against 134; means -2.6 against 3.0)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - already running, fought, Corrupted Isle: -1.5 (n 15 against 89)
  - already running, fought, Imperial Isle: -1.7 (n 34 against 14)
  - already running, fought, Isle of Jade: +2.5 (n 15 against 38)
  - already running, fought, Isle of Meditation: -5.0 (n 25 against 36)
  - already running, fought, Isle of Solitude: +4.0 (n 26 against 18)
  - already running, fought, Nomad's Isle: -2.2 (n 28 against 27)
  - already running, fought, Uncharted Isle: +7.7 (n 54 against 41)
  - held, advanced, Corrupted Isle: -2.9 (n 42 against 89)
  - held, advanced, Imperial Isle: +0.7 (n 11 against 14)
  - held, advanced, Isle of Jade: -4.9 (n 34 against 38)
  - held, advanced, Isle of Meditation: -2.6 (n 33 against 36)
  - held, advanced, Isle of Solitude: +7.6 (n 11 against 18)
  - held, advanced, Nomad's Isle: +7.3 (n 15 against 27)
  - held, advanced, Uncharted Isle: +23.3 (n 38 against 41)
  - already running, advanced, Corrupted Isle: -0.8 (n 11 against 89)
  - already running, advanced, Imperial Isle: -5.8 (n 16 against 14)
  - already running, advanced, Isle of Jade: -3.1 (n 14 against 38)
  - already running, advanced, Isle of Meditation: +2.2 (n 40 against 36)
  - already running, advanced, Isle of Solitude: +12.0 (n 23 against 18)
  - already running, advanced, Uncharted Isle: +6.1 (n 48 against 41)
  - held, fell back, Corrupted Isle: -16.7 (n 14 against 89)
  - held, fell back, Isle of Jade: -7.5 (n 16 against 38)
  - held, fell back, Isle of Meditation: -3.6 (n 31 against 36)
  - held, fell back, Isle of Solitude: +3.1 (n 18 against 18)
  - held, fell back, Uncharted Isle: +2.0 (n 44 against 41)
  - already running, fell back, Isle of Meditation: -1.6 (n 10 against 36)
  - already running, fell back, Isle of Solitude: +11.6 (n 10 against 18)
  - already running, fell back, Uncharted Isle: +6.1 (n 43 against 41)
  - ran, fought, Imperial Isle: +4.4 (n 25 against 14)
  - ran, fought, Isle of Jade: -0.8 (n 11 against 38)
  - ran, fought, Nomad's Isle: -1.7 (n 11 against 27)
  - ran, fought, Uncharted Isle: +6.6 (n 20 against 41)
  - ran, fell back, Imperial Isle: +4.1 (n 17 against 14)
  - ran, fell back, Isle of Meditation: +3.2 (n 10 against 36)
  - ran, fell back, Uncharted Isle: +5.8 (n 28 against 41)
  - ran, advanced, Imperial Isle: -1.6 (n 17 against 14)
  - ran, advanced, Isle of Jade: +2.2 (n 14 against 38)
  - ran, advanced, Uncharted Isle: +8.3 (n 37 against 41)
  - already running, held, Uncharted Isle: +5.0 (n 15 against 41)
  - ran, held, Isle of Jade: -13.9 (n 16 against 38)
  - held, held, Isle of Jade: +1.2 (n 11 against 38)

**late game** (31 decisions, 17 matches; usual: 0 to 1 at the enemy Lord)
- 2 to 3 at the enemy Lord (n 14): +2.1 [-13.6, +7.7]; in the 30 s before: -0.6 [-2.2, +4.2]

**power play** (945 decisions, 113 matches; usual: pushed, advanced)
- pushed, fought (n 264): +0.0 [-1.8, +1.5]; in the 30 s before: -1.9 [-2.9, -0.8] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, fought (n 196): -2.1 [-4.1, -0.6] CLEAR; in the 30 s before: -0.4 [-1.2, +1.0]
- held, fell back (n 68): -2.2 [-4.8, +0.2]; in the 30 s before: -2.4 [-4.2, -0.3] ALREADY DIFFERENT BEFORE: partly who chooses it
- pushed, fell back (n 49): +0.9 [-3.3, +5.0]; in the 30 s before: -2.0 [-3.4, -0.1] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, advanced (n 28): +0.4 [-2.3, +3.0]; in the 30 s before: -1.6 [-3.5, +0.7]
- pushed, held (n 6): -6.0 [-11.1, -1.5] CLEAR; in the 30 s before: -1.7 [-10.7, +6.6]
- held, held (n 6): -3.5 [-8.0, -0.7] CLEAR; in the 30 s before: -0.6 [-3.6, +2.8]
- held, to the spawn (n 5): -0.2 [-6.3, +5.4]; in the 30 s before: -5.3 [-11.4, +0.6]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - pushed, fought, behind in the fight (lowest third, +0.00 or less): -0.8 (n 78 against 92)
  - pushed, fought, middle third: +0.3 (n 80 against 106)
  - pushed, fought, ahead in the fight (top third, above +0.07): -0.8 (n 106 against 125)
  - held, fought, behind in the fight (lowest third, +0.00 or less): -2.2 (n 81 against 92)
  - held, fought, middle third: -3.1 (n 65 against 106)
  - held, fought, ahead in the fight (top third, above +0.07): -5.2 (n 50 against 125)
  - held, fell back, behind in the fight (lowest third, +0.00 or less): -2.4 (n 27 against 92)
  - held, fell back, middle third: -2.7 (n 25 against 106)
  - held, fell back, ahead in the fight (top third, above +0.07): -4.4 (n 16 against 125)
  - pushed, fell back, behind in the fight (lowest third, +0.00 or less): +1.4 (n 19 against 92)
  - pushed, fell back, middle third: +0.1 (n 21 against 106)
  - pushed, fell back, ahead in the fight (top third, above +0.07): too few yet (n 9 against 125; means 3.2 against 4.4)
  - held, advanced, behind in the fight (lowest third, +0.00 or less): +0.4 (n 14 against 92)
  - held, advanced, middle third: too few yet (n 9 against 106; means 1.4 against 1.5)
  - held, advanced, ahead in the fight (top third, above +0.07): too few yet (n 5 against 125; means 8.5 against 4.4)
  - pushed, held, behind in the fight (lowest third, +0.00 or less): too few yet (n 4 against 92; means -3.3 against 1.5)
  - pushed, held, middle third: too few yet (n 1 against 106; means -15.8 against 1.5)
  - pushed, held, ahead in the fight (top third, above +0.07): too few yet (n 1 against 125; means 1.4 against 4.4)
  - held, held, behind in the fight (lowest third, +0.00 or less): too few yet (n 4 against 92; means 0.0 against 1.5)
  - held, held, middle third: too few yet (n 2 against 106; means -2.4 against 1.5)
  - held, to the spawn, behind in the fight (lowest third, +0.00 or less): too few yet (n 2 against 92; means 0.1 against 1.5)
  - held, to the spawn, middle third: too few yet (n 1 against 106; means 0.5 against 1.5)
  - held, to the spawn, ahead in the fight (top third, above +0.07): too few yet (n 2 against 125; means 7.2 against 4.4)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - pushed, fought, Corrupted Isle: -0.7 (n 30 against 32)
  - pushed, fought, Imperial Isle: +2.6 (n 20 against 21)
  - pushed, fought, Isle of Jade: -5.4 (n 38 against 47)
  - pushed, fought, Isle of Meditation: +1.7 (n 61 against 80)
  - pushed, fought, Isle of Solitude: -1.6 (n 36 against 32)
  - pushed, fought, Nomad's Isle: -0.9 (n 24 against 13)
  - pushed, fought, Uncharted Isle: -1.2 (n 37 against 73)
  - held, fought, Corrupted Isle: -5.5 (n 16 against 32)
  - held, fought, Imperial Isle: -1.2 (n 26 against 21)
  - held, fought, Isle of Jade: -6.9 (n 20 against 47)
  - held, fought, Isle of Meditation: -1.0 (n 30 against 80)
  - held, fought, Isle of Solitude: -6.4 (n 27 against 32)
  - held, fought, Nomad's Isle: -2.7 (n 28 against 13)
  - held, fought, Uncharted Isle: -1.8 (n 32 against 73)
  - held, fell back, Isle of Meditation: -4.3 (n 17 against 80)
  - held, fell back, Uncharted Isle: -4.0 (n 13 against 73)
  - pushed, fell back, Uncharted Isle: -4.9 (n 12 against 73)

**split in base** (236 decisions, 72 matches; usual: defended without a collapse)
- collapsed (n 99): -4.8 [-9.2, +0.7]; in the 30 s before: +0.2 [-1.5, +2.5]
- missed (n 25): -4.4 [-11.0, +1.1]; in the 30 s before: -0.0 [-2.9, +5.6]
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - collapsed, Corrupted Isle: -9.3 (n 14 against 12)
  - collapsed, Isle of Meditation: -0.9 (n 28 against 17)
  - collapsed, Isle of Solitude: +2.5 (n 11 against 40)
  - collapsed, Uncharted Isle: -2.9 (n 13 against 31)

**Collapses on a split: time away and its cost** (`S32`; per collapse, averages; main = what the main fight lost while the collapsers were away)

| Group | Cases | Away (median s) | Split killed | Collapser died | Own deaths at main | Enemy deaths at main | Flag lead change | DP change | Win change |
|---|---|---|---|---|---|---|---|---|---|
| all | 111 | 22 | 24 | 11 | 0.61 | 0.41 | +2.2 | -4.1 | -3.0 |
| away under 30 s | 65 | 7 | 18 | 1 | 0.02 | 0.14 | +2.0 | +0.9 | -1.8 |
| away 30 to 60 s | 19 | 43 | 2 | 3 | 0.79 | 0.47 | -10.6 | -10.8 | +0.7 |
| away 60 s or more | 27 | 102 | 4 | 7 | 1.93 | 1 | +11.6 | -11.3 | -8.7 |
| before 20:00 | 94 | 22.5 | 17 | 9 | 0.5 | 0.35 | +2.5 | -5.2 | -3.7 |
| from 20:00 | 17 | 18 | 7 | 2 | 1.24 | 0.71 | +0.1 | +2.2 | +0.4 |
| split member killed | 24 | 13.5 | 24 | 1 | 0.04 | 1.04 | +5 | +1.1 | +1.7 |
| no kill | 87 | 25 | 0 | 10 | 0.77 | 0.23 | +1.4 | -5.5 | -4.4 |

**Leverage: where the choice matters most** (share of the spread in win-chance change explained by the choice beyond the situation; range = best minus worst choice, in points)

- after wipe (247): choice explains 8.3% (situation 10.5%); range 10.5 points, best pushed the pit, worst took the flag
- boost clock (411): choice explains 4.4% (situation 6.0%); range 8.5 points, best running, fought, worst not running, fell back
- enemy pickup (1503): choice explains 1.7% (situation 0.8%); range 10.5 points, best held, advanced, worst ran, to the spawn
- split in base (236): choice explains 1.3% (situation 4.7%); range 4.2 points, best defended without a collapse, worst collapsed
- power play (945): choice explains 1.1% (situation 4.3%); range 7.4 points, best held, to the spawn, worst pushed, held
- late game (31): choice explains 0.0% (situation 89.9%); range 2.1 points, best 2 to 3 at the enemy Lord, worst 0 to 1 at the enemy Lord

**Behaviour clusters: what teams actually did** (each decision's response grouped by what every player did in the next 20 s; UNNAMED = a group no single named choice covers: a response for Denning to name or reject)

*after wipe* (2 groups, separation 0.32):
- n 150: fought (midline, 1.9 of 8), fought (backline, 1.4 of 8), fought (frontline, 0.9 of 8), held (backline, 0.8 of 8); named as {'pushed the pit': 129, 'reset': 11, 'took the flag': 10}; win change 0.1
- n 97: advanced (midline, 2.7 of 8), advanced (backline, 2.5 of 8), advanced (frontline, 1.3 of 8); named as {'pushed the pit': 58, 'reset': 20, 'took the flag': 19}; win change 1.5 UNNAMED
*boost clock* (4 groups, separation 0.2):
- n 172: fought (midline, 2.3 of 8), fought (backline, 1.7 of 8), fought (frontline, 1.0 of 8); named as {'not running, fought': 108, 'running, fought': 54, 'not running, to the spawn': 4}; win change -0.8
- n 106: advanced (midline, 2.2 of 8), advanced (backline, 1.6 of 8), advanced (frontline, 0.6 of 8), fought (midline, 0.5 of 8); named as {'not running, advanced': 46, 'running, advanced': 41, 'not running, fell back': 5}; win change -2.5 UNNAMED
- n 80: held (backline, 1.7 of 8), held (midline, 1.2 of 8), to the spawn (midline, 0.5 of 8), to the spawn (backline, 0.5 of 8); named as {'not running, held': 27, 'not running, to the spawn': 15, 'running, held': 12}; win change -0.1 UNNAMED
- n 57: fell back (midline, 2.6 of 8), fell back (backline, 1.8 of 8), fell back (frontline, 0.6 of 8); named as {'not running, fell back': 37, 'running, fell back': 15, 'not running, fought': 2}; win change -7.6
*enemy pickup* (3 groups, separation 0.21):
- n 658: fought (midline, 1.9 of 8), fought (backline, 1.3 of 8), fought (frontline, 0.9 of 8), held (backline, 0.9 of 8); named as {'held, fought': 243, 'already running, fought': 194, 'ran, fought': 85}; win change -0.8 UNNAMED
- n 498: advanced (midline, 2.2 of 8), advanced (backline, 1.9 of 8), advanced (frontline, 0.9 of 8); named as {'held, advanced': 187, 'already running, advanced': 159, 'ran, advanced': 84}; win change 3.0 UNNAMED
- n 348: fell back (midline, 2.1 of 8), fell back (backline, 1.8 of 8), fell back (frontline, 0.7 of 8); named as {'held, fell back': 133, 'ran, fell back': 83, 'already running, fell back': 83}; win change -1.1 UNNAMED
*late game* (4 groups, separation 0.25):
- n 11: fell back (backline, 2.3 of 8), fell back (midline, 1.7 of 8), fell back (frontline, 1.0 of 8), advanced (midline, 0.8 of 8); named as {'0 to 1 at the enemy Lord': 7, '2 to 3 at the enemy Lord': 4}; win change 6.7
- n 10: advanced (midline, 2.9 of 8), advanced (backline, 1.5 of 8), advanced (frontline, 0.8 of 8), fought (backline, 0.5 of 8); named as {'2 to 3 at the enemy Lord': 5, '0 to 1 at the enemy Lord': 3, '4+ at the enemy Lord': 2}; win change -10.0 UNNAMED
- n 9: fought (midline, 2.6 of 8), fought (backline, 1.7 of 8), fought (frontline, 0.9 of 8), held (backline, 0.8 of 8); named as {'0 to 1 at the enemy Lord': 5, '2 to 3 at the enemy Lord': 3, '4+ at the enemy Lord': 1}; win change -8.5 UNNAMED
- n 4: held (backline, 2.8 of 8), advanced (midline, 1.0 of 8), held (midline, 1.0 of 8), held (frontline, 0.8 of 8); named as {'2 to 3 at the enemy Lord': 2, '0 to 1 at the enemy Lord': 2}; win change 19.5 UNNAMED
*power play* (2 groups, separation 0.27):
- n 617: fought (midline, 1.9 of 8), fought (backline, 1.4 of 8), fought (frontline, 0.9 of 8), fell back (backline, 0.7 of 8); named as {'pushed, fought': 258, 'held, fought': 195, 'held, fell back': 67}; win change 0.9 UNNAMED
- n 331: advanced (midline, 2.4 of 8), advanced (backline, 2.2 of 8), advanced (frontline, 1.1 of 8); named as {'pushed, advanced': 294, 'held, advanced': 26, 'pushed, fought': 6}; win change 2.5
*split in base* (3 groups, separation 0.19):
- n 108: fought (midline, 2.3 of 8), fought (backline, 1.3 of 8), fought (frontline, 0.9 of 8), held (backline, 0.7 of 8); named as {'defended without a collapse': 57, 'collapsed': 37, 'missed': 14}; win change -0.5 UNNAMED
- n 68: advanced (midline, 2.1 of 8), advanced (backline, 1.1 of 8), advanced (frontline, 0.6 of 8), held (backline, 0.5 of 8); named as {'defended without a collapse': 33, 'collapsed': 29, 'missed': 6}; win change -1.7 UNNAMED
- n 59: fell back (midline, 2.6 of 8), fell back (backline, 1.6 of 8), fell back (frontline, 0.8 of 8); named as {'collapsed': 33, 'defended without a collapse': 21, 'missed': 5}; win change -3.4 UNNAMED

## 8. What results and causes are worth

Win points for the team it happened to, from 113 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 331 | -0.5 | -5.9 to +4.3 | +3.1 | no |
| capture | 940 | +2.2 | +1.5 to +3.0 | +2.4 | yes |
| death (any) | 2174 | -5.2 | -6.9 to -3.4 | -3.8 | yes |
| death: against a spike build | 591 | -5.7 | -9.8 to -2.1 | -3.0 | yes |
| death: against other builds | 1583 | -5.0 | -7.3 to -2.8 | -4.1 | yes |
| death: back within 20 s | 359 | -4.9 | -8.0 to -2.0 | -2.0 | yes |
| death: down 20 to 60 s | 809 | -6.1 | -9.2 to -3.2 | -3.5 | yes |
| death: down 60 s or more | 1006 | -4.5 | -6.3 to -2.9 | -4.7 | yes |
| death: healer | 731 | -5.4 | -7.6 to -3.4 | -4.4 | yes |
| death: healer in own base or pit, back within 15 s (likely deliberate) | 44 | -2.3 | -7.1 to +3.1 | +0.3 | no |
| death: healer, other | 687 | -5.6 | -7.7 to -3.6 | -4.7 | yes |
| death: not a healer | 1443 | -5.0 | -7.1 to -3.4 | -3.5 | yes |
| death: team boosted (morale above zero) | 227 | -23.1 | -33.8 to -12.8 | -8.8 | yes |
| death: team not boosted | 1947 | -3.1 | -5.6 to -0.7 | -3.2 | yes |
| footman lost (base NPC) | 327 | +1.9 | -1.1 to +4.7 | +1.3 | no |
| pit NPC lost (any): taken by a spike build | 186 | -1.0 | -4.5 to +2.9 | -0.6 | no |
| pit NPC lost (any): taken by other builds | 708 | -2.9 | -5.4 to -0.4 | -1.7 | yes |
| pit NPC lost: archer | 513 | -0.6 | -2.5 to +1.5 | +0.1 | no |
| pit NPC lost: bodyguard | 124 | -2.7 | -5.4 to -0.2 | -0.8 | yes |
| pit NPC lost: knight | 257 | -6.0 | -8.8 to -3.8 | -4.7 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value.

*deaths* (per 10 s in that state; result worth -5.2 points, base rate 1.5%):

- enemies within 1,500 7.5 to 8: result chance +3.3 points, worth -0.17 win points
- own minus enemy team strength 353.5 to 434.5: result chance -0.9 points, worth +0.04 win points
- current health % 1 to 48.5: result chance +11.2 points, worth -0.58 win points
- allies within 1,500 0 to 0.5: result chance +1.9 points, worth -0.1 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.5 points, worth -0.13 win points
- enemy enchantment removal skills 0 to 0.5: result chance +2.9 points, worth -0.15 win points
- own prot skills 6.5 to 7.5: result chance +0.7 points, worth -0.04 win points
- distance from its own pit 13437.5 to 18468: result chance +0.9 points, worth -0.04 win points

*kill conversion* (per burst, for the attacking team; result worth +5.2 points, base rate 29.8%):

- damage in the 2 s burst 508.5 to 839: result chance +27.1 points, worth +1.41 win points
- target's healers in range 0 to 0.5: result chance +32.1 points, worth +1.67 win points
- attacking minus target team strength 623 to 989: result chance +24.9 points, worth +1.3 win points
- target health % when the burst started 0 to 37.5: result chance +22.4 points, worth +1.16 win points
- target's health ceiling 0.4 to 0.69: result chance +32.1 points, worth +1.67 win points
- target team's prot skills 16.5 to 17: result chance -16.2 points, worth -0.84 win points
- a prot on the target 0.5 to 1: result chance -4.6 points, worth -0.24 win points
- attackers' interrupt skills minus target team's heals -3.5 to 1: result chance -10.4 points, worth -0.54 win points

*npc loss* (per case, for the defending team; result worth -2.4 points, base rate 20.1%):

- damage on the pit NPCs in the last 5 s 397.5 to 1370: result chance +38.1 points, worth -0.93 win points
- own players in the pit 0 to 0.5: result chance +34.0 points, worth -0.83 win points
- own players alive outside the pit 0 to 0.5: result chance +17.8 points, worth -0.43 win points
- of which healers 0 to 0.5: result chance +19.2 points, worth -0.47 win points
- enemy players in the pit 7.5 to 8: result chance +10.6 points, worth -0.26 win points
- attackers' measured damage per second against a Lord (benchmarks) 85.75 to 97: result chance +7.5 points, worth -0.18 win points
- attacking minus defending team strength -416.5 to -289: result chance -10.1 points, worth +0.25 win points

## The TQs

Denning's four questions, each from the batch's matches. The why comes from forensics and events (every number placed against the same role or situation in every stored match); the different play comes only from measurement: the usual play's choice effects (usual.py), node models read again with the variable changed (models that never saw the match, changes priced in win points with values.py), options that were ready and unused, and benchmarks. Points = win-chance points.

## TQ 1. Behind on flags

*The biggest flag swing in the new matches: push +73 -> -79 by 4:35.0.*

### Flag swing: push v OG (99494912), 3:35.0 to 4:35.0
**Result**: push's flag lead +73 s -> -79 s (-152 s). Stand: push -> OG.
**Captures** (flag model: fastest possible answer after the enemy's capture):
- push capped 3:06.0 by Dervish, 52 s after OG's capture; fastest possible 56 s, so -4 s slower; enemies in the way {'AoB Derv': 2}
- OG capped 4:23.0 by AoB Derv, 77 s after push's capture; fastest possible 40 s, so 37 s slower; enemies in the way {'Prot': 37, '7 Monk': 31, 'AoB Derv': 22, 'Mesmer': 19}
**Runs** (each run: outcome, and what was done to the runner):
- push Mesmer 3:30.0 to 3:45.0 (15 s): dropped, lowest health 100%, escort none, pushed by nobody
- OG AoB Derv 3:41.0 to 4:23.0 (41 s): captured, lowest health 100%, escort none, pushed by ['AoB Derv']; control on the runner: 3:57.2 crippled by push AoB Derv; 4:06.5 crippled by push AoB Derv; 4:15.6 crippled by push AoB Derv
- push Mesmer 4:18.0 to 4:32.0 (14 s): dropped, lowest health 100%, escort none, pushed by nobody
**Deaths in the window**: 4:16.0 push Air Ele (backside, [3, 4])
- push output in the 20 s before 4:16.0: 5.7 damage per second (below the 10th percentile for team (median 37.1, n 3825)), top target share 0.56, spikes 0
- OG output in the 20 s before 4:16.0: 57.9 damage per second (above the 50th percentile for team (median 37.1, n 3825)), top target share 0.73, spikes 0
**Why push Air Ele died at 4:16.0** (forensics):
  - Position: yes (nearest allied healer 894 in the last 5 s, nearest enemy 104, allies in casting range 2, enemies 4)
  - Prots: late or interrupted (1 from teammates, 0 self; 1 of 1 landed); damage 912 (48% attacks, 40% armor-ignoring), burst 285 in 2 s at 4:12.1; knockdowns 1, knockdown immunity up for 0
  - Healers under interrupt pressure: usual (healers 3, interrupts_per_min 3.0, interrupted 1, casts 10, finished_share 0.9, dazed 0, knockdowns 0, hexes 2)
  - Damage off shield sets: yes (team share 0.66, a shield would have stopped about 75)
  - Own damage: no (5.7 per second on [('OG Hammer', 64), ('OG Prot', 50)]); enemy damage: high (61.3 per second)
  - Peel: no (peel on a burst is rare: most bursts on this role get none) (0 of 4 attackers controlled; longest free 20.0 s)
  - Casting: unclear (casts 3, interrupted 0, cancelled 0, while_dazed 0)
**Why, in short**: push's Mesmer dropped the flag at 4:32 after 14 s of carrying, 20 s from capturing (main 2v4, alive 7v8); OG capped at 4:23, 77 s after push's capture, on its 1st run (0 dropped); push pushed the last carrier with AoB Derv but its health never went below 100%; deaths in the window: push 1; how the game got there: deaths: 1 of push died 4:16 (4:16) -> push fell behind on flags (4:35).

**How it got there** (the chain of game states, earliest first; traced back to 3:20, the last reset or 3 minutes before; win = the held-out win model's change over each link):
1. 4:06: **deaths: 1 of push died 4:16** (win -0.4 points) -> led to step 2
   - 4:16 Air Ele died (backside, numbers [3, 4]): no prot landed in time (1 of 1 landed); knocked down 1 times with no knockdown immunity up; the enemy hit unusually hard (61.3 per second); its own team's damage was low (5.7 per second)
   - Mesmer in the 20 s before: 50% of its interrupts and casts on the enemy midline or frontline (interrupts none, casts on enemies {'healer': 1, 'mid/front': 1}; typical before an own healer death: 86%, 493 cases)
   - when the fight started: main 3v4, alive 8v8, flag lead +23 s, stand push
2. 4:25: **push fell behind on flags** (win +0.0 points) (the result)
   - flag lead +13 s at 4:25 -> -79 s at 4:35
   - push Mesmer run 3:30 to 3:45: dropped
   - push Mesmer run 4:18 to 4:32: dropped
   - OG capped at 4:23

**Where a fix would have mattered most** (measured, in win points):
- no alternative along the chain could be priced from the data yet

**A different play (measured)**

*The decisions in the swing* (usual.py: win-chance points over the decision's window, against the kind's most common choice):
- enemy pickup at 3:41 (main 4v4, flags +41 s, boost in 84, fight state -0.022): chose **already running, fell back** (-0.2 [-2.8, +3.6] against the most common choice, held, fought); in the 15 most similar decisions teams usually chose **held, fought**; measured better: **held, advanced** (+3.3 points against the choice made, not clear yet, n 196). In the same fight-state third (behind in the fight (lowest third, -0.01 or less)) this choice did +5.8 against the usual choice (n 45 against 99, raw).
*The answers to the enemy's captures* (flag-answer node: seconds slower than possible; typical error 17.1 s against 28.7 s for the median on unseen matches):
- answer at 4:23 by the Mesmer: 64 s slower than possible (model reads 69.8 s); with a runner waiting at the spawn: 64.4 s (-5.4 s); no parking (running at once): 37.7 s (-32.1 s); no enemies on the way back: 63.0 s (-6.8 s)
- Those 32 s, read by the win model as flag lead at 4:35: push 1.2% -> 1.4% (+0.2 points)

**Confidence**: medium (one measurement supports it).

## TQ 2. A monk death

*The monk death that cost the most win chance in the new matches: Dz v Crew (1729daac), Dz 8 Monk at 25:07 (own pit, numbers [7, 6]); win chance -82.9 points from 10 s before to 30 s after.*

**Why** (forensics, against the same role in every stored match):
- Position: yes (nearest allied healer 10956 in the last 5 s, nearest enemy 1148, allies in casting range 0, enemies 1)
- Prots: late or interrupted (0 from teammates, 1 self; 1 of 1 landed); damage 248 (0% attacks, 60% armor-ignoring), burst 125 in 2 s at 24:52.5
- Healers under interrupt pressure: usual (healers 3, interrupts_per_min 0.0, interrupted 0, casts 18, finished_share 1.0, dazed 0, knockdowns 0, hexes 5)
- Damage off shield sets: usual (team share 0.34, a shield would have stopped about 59)
- Own damage: usual (29.8 per second on [('Crew Warrior', 335), ('Crew Necromancer', 231)]); enemy damage: high (80.0 per second)
- Peel: no (peel on a burst is rare: most bursts on this role get none) (0 of 1 attackers controlled; longest free 20.0 s)
- Casting: usual (casts 5, interrupted 0, cancelled 0, while_dazed 0)
**Why, in short**: the 8 Monk died because no prot landed in time (1 of 1 landed), the enemy hit unusually hard (80.0 per second), position (no allied healer within casting range, nearest enemy 1148), its attackers were not peeled (no (peel on a burst is rare: most bursts on this role get none)). How the game got there: Crew's split in Dz's base (22:07) -> Dz's 8 Monk isolated (25:06) -> Dz fell behind on flags (25:05) -> deaths: 1 of Dz died 25:07 (25:07).

**How it got there** (the chain of game states, earliest first; traced back to 22:07, the last reset or 3 minutes before; win = the held-out win model's change over each link):
1. 19:55: **Crew's split in Dz's base** (ongoing state) -> led to step 2
   - Crew split Monk 1+Ritualist into Dz's base at 19:55
   - first defender 0 s after it entered (every stored split: median -10 s; Denning: about 15 s is on time, 60 s is late)
   - NPCs it killed: guild_lord 25:13 (defenders there: none), archer 25:14 (defenders there: none), archer 25:14 (defenders there: none)
   - meanwhile Dz's main 3v5
2. 22:10: **Dz's 8 Monk isolated** (ongoing state) -> led to step 4
   - 8 Monk away from its main group from 22:10 (mostly own pit 100 s, own base 80 s)
   - Crew had a split of Monk 1+Ritualist on the map then, in the base from 19:55
3. 23:50: **Dz fell behind on flags** (win -2.8 points) -> led to step 4
   - flag lead +26 s at 23:50 -> -34 s at 23:55
4. 24:57: **deaths: 1 of Dz died 25:07** (win -82.9 points) (the result)
   - 25:07 8 Monk died (own pit, numbers [7, 6]): no prot landed in time (1 of 1 landed); the enemy hit unusually hard (80.0 per second); position (no allied healer within casting range, nearest enemy 1148); its attackers were not peeled (no (peel on a burst is rare: most bursts on this role get none))
   - Mesmer in the 20 s before: 100% of its interrupts and casts on the enemy midline or frontline (interrupts {'mid/front': 1}, casts on enemies {'mid/front': 1}; typical before an own healer death: 86%, 493 cases)
   - when the fight started: main 7v6, alive 8v8, flag lead -22 s, stand Dz

**Where a fix would have mattered most** (measured, in win points):
- step 4: another healer in range of the 8 Monk: about +10.9 win points (deaths node: risk 55.8% -> 42.6% of dying in the next 10 s, times this death's cost (-82.9 points); clear)
- step 1: enemy pickup at 20:28 (main 8v4): held, advanced instead of already running, held: about +5.5 win points (usual.py: measured choice effect against the choice made; not clear yet)

**How it could have been prevented (measured)**

- Further back: the fixes along the chain are priced above ("Where a fix would have mattered most"). The readings below are what was still possible in the last seconds.
- Attackers left free (no snare, Blind, Weakness, interrupt, knockdown or hex from its team): Crew Ritualist 20.0 s free (nearest own non-healer 10821)
- Deaths node at 25:05 (AUC 0.921 on unseen matches against 0.799 for health_pct and damage_taken_3s alone): risk 55.8% of dying in the next 10 s; read again with
  - another healer in range: 42.6% (-13.2 points of risk; at this death's measured cost of -82.9 win points, about +10.9 expected; at a typical healer death's -5.4, +0.7)
  - staying with its group: 53.9% (-1.9 points of risk; at this death's measured cost of -82.9 win points, about +1.6 expected; at a typical healer death's -5.4, +0.1)
  - its hexes removed: 49.2% (-6.6 points of risk; at this death's measured cost of -82.9 win points, about +5.5 expected; at a typical healer death's -5.4, +0.4)
  - all of these together: 34.5% (-21.3 points of risk; at this death's measured cost of -82.9 win points, about +17.7 expected; at a typical healer death's -5.4, +1.2)

**Confidence**: medium (one measurement supports it).

## TQ 3. A power play without a kill

*The power play without a kill that cost the most win chance in the new matches: main 8v6, pushed, no kill in 59 s; win chance -32.3 points over it.*

### Power play without a kill: Fun v hold (566a6ddf), 4:31.0 to 5:30.0
**Situation**: main 8v6, alive 8v7, flags down (-18 s), DP -11, boost in None; choice pushed (advanced 6, carrying 1, to the spawn 1); deaths {'Fun': 0, 'hold': 0} in 59 s
**The fight's shape** (every 5 s: own main, the enemy group it faced, distance between them, that group's distance to the rest of its team): 4:31.0 8v6 886 apart, 3346 from its others; 4:36.0 7v6 525 apart, 3949 from its others; 4:41.0 7v6 729 apart, 5487 from its others; 4:46.0 7v6 568 apart, 7414 from its others; 4:51.0 7v6 632 apart, 7915 from its others; 4:56.0 7v6 710 apart, 8533 from its others; 5:01.0 7v6 313 apart, 8652 from its others; 5:06.0 7v6 849 apart, 8294 from its others; 5:11.0 6v6 651 apart, 7865 from its others; 5:16.0 6v6 683 apart, 6471 from its others; 5:21.0 6v6 206 apart, 5701 from its others; 5:26.0 6v6 391 apart, 3548 from its others
**Fun's damage**: 51.2 per second (above the 50th percentile for team (median 37.1, n 3825)); top target share 0.48 (below the 50th percentile for team (median 0.49, n 3825)); targets [('hold 7 Monk', 1437), ('hold Stand Mes', 576), ('hold 8 Monk', 538), ('hold Prot', 387)]; dealers [('Fun Air Ele 3', 735), ('Fun Air Ele 4', 664), ('Fun Fire Ele 2', 480), ('Fun Air Ele 2', 474), ('Fun Fire Ele 1', 430)]
- phase 4:00.0 to 4:41.0: 8v0 (own base, job free), damage uptime 0.22, damage-seconds lost {'moving': 165, 'carrying': 21, 'idle': 6}
- phase 4:41.0 to 5:24.0: 7v6 (push side, job convert), damage uptime 0.33, damage-seconds lost {'moving': 106, 'carrying': 43, 'idle': 15, 'knocked down': 8}
- phase 5:24.0 to 6:00.0: 7v6 (backside, job convert), damage uptime 0.18, damage-seconds lost {'moving': 158, 'idle': 18, 'knocked down': 1}
**hold's answer**: healing 108 per second ({'hold 7 Monk': 2428, 'hold Ritualist': 1432.8000000000004, 'hold 8 Monk': 1422, 'hold Prot': 891}); prots {'Reversal of Fortune': 5, 'Aura of Stability': 4, 'Shield Guardian PvP': 1, 'Aura of Faith': 4, 'Shielding Hands': 2}
- Fun's knockdowns landed 0; hold's knockdown immunity casts 4
- Pressure on hold's healers: healers 3, interrupts_per_min 0.0, interrupted 0, casts 37, finished_share 1.0, dazed 0, knockdowns 0, hexes 15 (around the median for team (median 0, n 4312))
- Snares, Blind and Weakness Fun put on hold: {'weakness': 2}
**Where the power play came from** (why the enemy was short, player-seconds over it): push side 15, dead 10, backside 3
**Why, in short**: Fun had 8v6 at main for 59 s; hold healed 108 per second; worse than in power plays that killed: damage uptime in contact 31% (killing 50%, not killing 39%; most lost to moving), top-target share 0.48 over 4 targets (killing 0.37, not killing 0.41); not the cause (on the side of power plays that killed): damage 51.2 per second (killing 45.5, not killing 36.7); the biggest burst went on the hold Stand Mes (15.4% to kill), while the same burst on the hold AoB Derv read 48.6%.

**How it could have been converted (measured)**

- Against every stored power play (2 up): those that killed had a median 45.5 damage per second and top-target share 0.37 (60 cases); those that didn't, 36.7 and 0.41 (115 cases). Fun here: 51.2 and 0.48. Damage uptime: 50% in those that killed, 39% in those that didn't, 31% here.
- Kill-conversion node (AUC 0.777 on unseen matches against 0.668 for burst_damage and target_health_pct alone): the biggest burst, 495 on the hold Stand Mes at 4:48 with 5 attackers, read 15.4% to kill within 8 s; read again with
  - on the hold AoB Derv instead: 48.6% (+33.2 points, about +1.7 win points at a converted burst's +5.2)
  - a hex on the target's healers: 15.7% (+0.3 points, about +0.0 win points at a converted burst's +5.2)
  - on the hold 7 Monk instead: 12.3% (-3.1 points, about -0.2 win points at a converted burst's +5.2)
  - on the hold 8 Monk instead: 11.7% (-3.7 points, about -0.2 win points at a converted burst's +5.2)
  - on the hold Hammer instead: 9.3% (-6.1 points, about -0.3 win points at a converted burst's +5.2)
  - on the hold Prot instead: 7.6% (-7.8 points, about -0.4 win points at a converted burst's +5.2)
- Bursts in the window: 4, on Stand Mes (495), Prot (367), 7 Monk (308), 7 Monk (472)
- The choice at the power play (usual.py):
  - power play at 4:31 (main 8v6, flags -18 s, boost in None, fight state -0.001): chose **pushed, advanced** (+0.0 [+0.0, +0.0] against the most common choice, pushed, advanced); in the 15 most similar decisions teams usually chose **pushed, fought**; no choice of this kind did measurably better than the one made.

**Confidence**: medium (one measurement supports it).

## TQ 4. Pit NPCs lost

*The NPC loss that cost the most win chance in the new matches: BcS lost knight (converted from the fight at 16:29) at 17:41; win chance -32.0 points from 20 s before to 20 s after.*

### Pit NPCs lost: BcS v cope (81b3dd52) around 17:41.0
**Lost**: 17:41.0 knight (converted from the fight at 16:29); 17:56.0 archer (outside) (converted from the fight at 16:29); 17:56.0 knight (converted from the fight at 16:29)
**BcS at 17:41.0**: Warrior: own pit (hold); Paragon: dead; Monk 3 (WoC): own pit (hold); Monk 4 (WoC): own pit (hold); Mesmer: dead; Prot: own pit (hold); 7 Monk: own pit (hold); 8 Monk: own pit (hold)
- cope output 17:11.0 to 17:41.0: 33.2 per second
- BcS output 17:11.0 to 17:41.0: 29.2 per second
**Why, in short**: at 17:38 the pit had 8 attackers against 6 defenders (3 of them healers), with 0 of BcS elsewhere; 2 of BcS were dead at the time (Mesmer 16:44, Paragon 17:09); the Mesmer died at 16:44 (own pit, numbers [8, 8]) because no prot landed in time (0 of 0 landed; Prot Guardian, Prot Shielding Hands ready and unused), its attackers were not peeled (partly (controlled, but an attacker was left free for 14.3 s)); the Paragon died at 17:09 (own pit, numbers [7, 8]) because position (in contact with the enemy, nearest enemy 170), its attackers were not peeled (partly (controlled, but an attacker was left free for 19.5 s)); how the game got there: BcS already behind on flags at 14:45 (16:42) -> deaths: 1 of BcS died 16:44 (16:44) -> BcS lost knight (17:41).

**How it got there** (the chain of game states, earliest first; traced back to 14:41, the last reset or 3 minutes before; win = the held-out win model's change over each link):
1. 14:45: **BcS already behind on flags at 14:45** (win -8.5 points) -> led to step 2
   - flag lead -79 s since the start of the window
2. 16:34: **deaths: 1 of BcS died 16:44** (win -0.4 points) -> led to step 3
   - 16:44 Mesmer died (own pit, numbers [8, 8]): no prot landed in time (0 of 0 landed; Prot Guardian, Prot Shielding Hands ready and unused); its attackers were not peeled (partly (controlled, but an attacker was left free for 14.3 s))
   - Mesmer in the 20 s before: 100% of its interrupts and casts on the enemy midline or frontline (interrupts none, casts on enemies {'mid/front': 1}; typical before an own healer death: 86%, 493 cases)
   - when the fight started: main 8v8, alive 8v8, flag lead -79 s, stand cope
3. 17:21: **BcS lost knight** (win -32.0 points) (the result)
   - pit at 17:41: 8 attackers against 6 defenders (3 healers)
   - 2 of BcS dead (Mesmer 16:44, Paragon 17:09)

**Where a fix would have mattered most** (measured, in win points):
- step 2: boost clock at 16:34 (main 8v8): running, held instead of not running, fought: about +4.5 win points (usual.py: measured choice effect against the choice made, partly who chooses it; not clear yet)

**How it could have been prevented (measured)**

- Further back: with 2 of BcS dead, more defenders were not available; the fixes along the chain are priced above.
- NPC-loss node at 17:38 (AUC 0.843 on unseen matches against 0.752 for attackers and defenders alone): 8 attackers (3 healers) against 6 defenders (3 healers), 0 of BcS elsewhere; read 9.7% to lose an NPC; read again with
  - one more defender: 5.7% (-4.0 points; at this loss's measured cost of -32.0 win points, about +1.3 expected; at a typical NPC loss's -2.4, +0.1)
  - one more defender, a healer: 5.7% (-4.0 points; at this loss's measured cost of -32.0 win points, about +1.3 expected; at a typical NPC loss's -2.4, +0.1)
  - two more defenders: 4.1% (-5.6 points; at this loss's measured cost of -32.0 win points, about +1.8 expected; at a typical NPC loss's -2.4, +0.1)

**Confidence**: medium (one measurement supports it).

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

**Flag answers** (answering the enemy's capture): winners: 428 answers, median 38.0 s, 4.0 s slower than possible, 93 answers 30 s+ slower; losers: 402 answers, median 56.0 s, 11.5 s slower than possible, 145 answers 30 s+ slower.

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

