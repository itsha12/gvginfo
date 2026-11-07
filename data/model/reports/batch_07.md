# Learning report, batch 7

Trained on 91 matches (30 new in this batch). Variables in use: 33; build variables from 60 matches, interactions from 40.

## 0. Data integrity

- Lengths repaired: 3 (1f65fd3b 150 s -> 1027 s) (bbef1904 617 s -> 599 s) (36a65ac6 1319 s -> 1294 s) 
- Matches with a team's Lord damage not observed (left blank, not zero): 5
- Pit NPCs added from the standard roster (never seen in the replay): 321 in 79 matches
- Left out of training: 0

## 1. The honest test

**Not yet better than strength alone: treat the curves as noise.** Held-out accuracy (matches held out whole), log loss in brackets (lower is better):

- strength only: all 78% (0.361), 0-5 min 81% (0.332), 5-10 min 80% (0.351), 10-15 min 73% (0.417), 15-end min 73% (0.378), matches lasting 15 min+ 74% (0.412), matches even on strength (gap under 200) 54% (0.632)
- glass box: all 83% (0.416), 0-5 min 81% (0.397), 5-10 min 84% (0.369), 10-15 min 78% (0.561), 15-end min 86% (0.387), matches lasting 15 min+ 79% (0.485), matches even on strength (gap under 200) 67% (0.772)
- glass box without corrections: all 83% (0.41), 0-5 min 81% (0.395), 5-10 min 85% (0.362), 10-15 min 79% (0.546), 15-end min 86% (0.383), matches lasting 15 min+ 79% (0.477), matches even on strength (gap under 200) 67% (0.76)
- black box: all 81% (0.71), 0-5 min 82% (0.679), 5-10 min 81% (0.689), 10-15 min 80% (0.724), 15-end min 77% (0.783), matches lasting 15 min+ 79% (0.786), matches even on strength (gap under 200) 63% (1.356)
- Gain over strength alone (log loss, resampling whole matches): -0.055 (90% range -0.161 to +0.041).
- Change since batch 6: glass box log loss 0.55 -> 0.416; strength only 0.418 -> 0.361.

## 2. What it leans on

- **lord_dps_enemy** 0.714 (was 0.694): enemy build's measured Lord damage per second
- **lord_dps_own** 0.71 (was 0.688): own build's measured Lord damage per second if all its non-healers were at the Lord
- **morale_diff** 0.515 (was 0.353): own minus enemy morale summed over players (boosts +, death penalty -)
- **morale_diff & map_flag_run** 0.447 (was 0.354): own minus enemy morale summed over players (boosts +, death penalty -) TOGETHER WITH the map's flag run Y: distance from the flag spawn to the stand (average of both sides)
- **knights_diff** 0.446 (was 0.347): own minus enemy pit knights alive
- **spike_build_own** 0.347 (was 0.269): own build is a spike build (1) or not (0)
- **spike_build_enemy** 0.328 (was 0.271): enemy build is a spike build
- **archers_diff & map_flag_run** 0.265 (was 0.271): own minus enemy pit archers alive TOGETHER WITH the map's flag run Y: distance from the flag spawn to the stand (average of both sides)
- **spike_killable_diff** 0.238 (was 0.451): enemy minus own players within one spike of the other side (DP stacking; 0 unless a spike build is involved)
- **lord_damage_diff & lord_dps_own** 0.238 (was 0.162): own minus enemy Lord damage dealt so far (the 28:00 tiebreak; players can't see it); blank when either team's Lord damage wasn't observed TOGETHER WITH own build's measured Lord damage per second if all its non-healers were at the Lord
- **stand** 0.233 (was 0.206): who holds the flag stand: 1 own, 0 nobody, -1 enemy
- **lord_damage_diff & lord_dps_enemy** 0.219 (was 0.193): own minus enemy Lord damage dealt so far (the 28:00 tiebreak; players can't see it); blank when either team's Lord damage wasn't observed TOGETHER WITH enemy build's measured Lord damage per second

## 3. The curves in words

Points = win-chance points added to an otherwise even game at each range of the variable.

- **lord_dps_enemy** rises from -21.0 to +14.6 points (35.8..76.0: -21.0; 78.4..83.15: +15.9; 87.85..89.8: -24.7; 97.95..102.3: +16.8; 102.95..105.45: -25.1; 106.0..111.8: +4.3; 117.1..134.25: +15.0)
- **lord_dps_own** falls from +18.9 to -14.2 points (35.8..76.0: +18.9; 78.4..83.15: -18.0; 87.85..89.8: +25.1; 97.95..102.3: -15.8; 102.95..105.45: +25.3; 106.0..111.8: -4.4; 117.1..134.25: -14.7)
- **morale_diff** rises from -22.2 to +20.9 points (-470.0..-196.0: -22.2; -144.5..-112.5: -18.9; -88.5..-46.0: -15.9; -15.5..-0.5: -1.5; 0.5..21.5: +1.7; 58.5..95.5: +17.2; 136.5..181.5: +19.3)
- **morale_diff & map_flag_run** (interaction): see wp_model.md
- **knights_diff** rises from -24.4 to +24.5 points (-2.0..-1.5: -24.4; -1.5..-0.5: -21.6; -0.5..0.5: +0.1; 0.5..1.5: +21.0; 1.5..2.0: +24.5)
- **spike_build_own** rises from -5.2 to +23.6 points (0.0..0.5: -5.2; 0.5..1.0: +23.6)
- **spike_build_enemy** falls from +4.9 to -22.5 points (0.0..0.5: +4.9; 0.5..1.0: -22.5)
- **archers_diff & map_flag_run** (interaction): see wp_model.md
- **spike_killable_diff** rises from -37.0 to +37.0 points (-8.0..-7.5: -37.0; -5.5..-4.5: -35.1; -3.5..-2.5: -32.9; -1.5..-0.5: -23.7; 0.5..1.5: +23.0; 2.5..4.5: +33.7; 5.5..7.5: +36.0)
- **lord_damage_diff & lord_dps_own** (interaction): see wp_model.md

## 4. Discovery

**Interaction candidates** (a screen: pairs whose combination seems to matter beyond each alone; untested until held-out matches confirm them; switched on in the model from 40 matches):

- morale_diff with map_flag_run (screen 0.087)
- morale_diff with map_pit_to_stand (screen 0.083)
- morale_diff with spike_build_enemy (screen 0.078)
- morale_diff with spike_build_own (screen 0.078)
- morale_diff with spike_killable_diff (screen 0.077)
- alive_diff with morale_diff (screen 0.077)
- down_diff_s with morale_diff (screen 0.074)
- morale_diff with map_bases_apart (screen 0.069)

**Candidate variables** (proposed variables, tested on unseen matches; log loss, lower is better):

- split_diff: 0.416 without, 0.426 with: does not improve yet. own minus enemy players on a split (away from their main group on the enemy half, not carrying). Proposed batch 1 by Claude: the knights curve runs backwards, maybe standing in for the cost of splitting
- turtle_diff: 0.416 without, 0.424 with: does not improve yet. own minus enemy share of live players at home (own base or pit). Proposed 2026-11-06 from OG comms ([ohno v One], [ohno v Crew]: 'they are turtling, we have to make a play'); comms_vars.py: teams that turtled 60 s won 3 of 13 times
- footmen_diff: 0.416 without, 0.44 with: does not improve yet. own minus enemy footmen alive (base NPCs, not pit NPCs). Proposed 2026-11-06 from OG comms ([ohno v NwAy]: 'this way we don't lose footmen'; [ohno v Fun]: fake collapse to the footmen)
- no_healer_groups_diff: 0.416 without, 0.416 with: does not improve yet. own minus enemy groups of 2+ with no healer. Proposed 2026-11-06 from OG comms ([ohno v One]: keep a prot and a monk on one side, the Rit and a monk on the other); comms_vars.py: such groups lose players twice as often
- solo_healers_diff: 0.416 without, 0.419 with: does not improve yet. own minus enemy healers with no other own healer within casting range. Proposed 2026-11-06 from OG comms ('solo monk, go on the monk'); Denning: a monk alone has no other monk to support it

**Surprises** (moments where the held-out model was most confident about the team that went on to lose; each points to something the variables don't capture yet):

- hdm v HC (28447c4a) at 22:45: a model that never saw this match gave HC 1.8%, and HC won. Why it thought so: morale_diff & map_bases_apart -40.1, knights_diff -30.0, morale_diff -18.3, archers_diff & map_flag_run +17.6, morale_diff & map_flag_run +15.1
- Fun v hold (99d9b260) at 2:00: a model that never saw this match gave hold 3.3%, and hold won. Why it thought so: spike_killable_diff -39.0, morale_diff & lord_dps_enemy +25.1, spike_build_enemy -24.9, team strength +22.8, morale_diff & map_bases_apart -22.7
- cope v Team (427c825b) at 11:30: a model that never saw this match gave Team 1.1%, and Team won. Why it thought so: lord_dps_enemy -35.2, lord_dps_own -29.4, archers_diff & map_flag_run +27.5, morale_diff -19.0, knights_diff -18.5
- OG v hold (49eec28d) at 4:00: a model that never saw this match gave OG 0.1%, and OG won. Why it thought so: lord_dps_enemy -33.2, morale_diff & map_flag_run -31.1, morale_diff -24.5, lord_dps_own -21.5, knights_diff -19.1
- RACK v hdm (1f65fd3b) at 13:45: a model that never saw this match gave RACK 1.9%, and RACK won. Why it thought so: knights_diff -28.2, healing_monks_enemy -21.0, morale_diff & map_flag_run +18.8, morale_diff -17.3, lord_dps_own -14.4
- Crew v BcS (3ee18c0c) at 10:45: a model that never saw this match gave Crew 99.6%, and Crew lost. Why it thought so: lord_dps_own +27.4, lord_damage_diff & lord_dps_own +26.5, knights_diff +19.5, lord_dps_enemy +18.5, morale_diff +17.2

## 5. Denning's rulings seen through the model

Win chance from a model that never saw the match, 20 s before and 60 s after each ruled moment. Contributions are points for an otherwise even game (the curves' scale).

- hdm v HC (28447c4a) 5:01 (split answered), HC: 42.0% 20 s before -> 83.5% 60 s after (+41.5). After: morale_diff & map_bases_apart +39.3, knights_diff -30.0, archers_diff & map_flag_run +17.6, morale_diff +14.6
- hdm v HC (28447c4a) 5:01 (split answered), hdm: 58.8% 20 s before -> 20.2% 60 s after (-38.6). After: morale_diff & map_bases_apart -39.6, knights_diff +30.8, archers_diff & map_flag_run -17.9, morale_diff & map_flag_run +15.7
- hdm v HC (28447c4a) 1:02 (split detection), HC: 45.3% 20 s before -> 67.3% 60 s after (+22.0). After: morale_diff & map_bases_apart +39.2, lord_dps_own +12.9, morale_diff & map_flag_run -9.8, morale_diff & lord_dps_own -9.4
- hdm v HC (28447c4a) 1:02 (split detection), hdm: 52.9% 20 s before -> 31.7% 60 s after (-21.2). After: morale_diff & map_bases_apart -39.6, lord_dps_enemy -12.7, morale_diff & lord_dps_enemy +11.0, boost_clock & map_bases_apart +9.4
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), HC: 83.4% 20 s before -> 60.2% 60 s after (-23.2). After: morale_diff & map_bases_apart +39.3, knights_diff -30.0, archers_diff & map_flag_run +25.3, morale_diff +14.6
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), hdm: 19.1% 20 s before -> 39.7% 60 s after (+20.6). After: morale_diff & map_bases_apart -39.6, knights_diff +30.8, archers_diff & map_flag_run -27.7, morale_diff & map_flag_run +15.7
- hdm v HC (bbef1904) 8:10 (death), HC: 87.1% 20 s before -> 36.1% 60 s after (-51.0). After: lord_dps_enemy +21.3, alive_diff -10.4, down_diff_s -10.2, fight_state -7.9
- hdm v HC (bbef1904) 8:10 (death), hdm: 7.2% 20 s before -> 46.9% 60 s after (+39.7). After: lord_dps_own -22.2, alive_diff +10.2, lord_health_diff & lord_dps_own -10.1, down_diff_s +9.4
- Men v HC (faec428a) 9:31 (death), HC: 8.7% 20 s before -> 12.3% 60 s after (+3.6). After: knights_diff -21.7, lord_dps_own -15.5, archers_diff & map_flag_run +15.0, lord_dps_enemy -12.7
- Men v HC (faec428a) 9:31 (death), Men: 90.5% 20 s before -> 86.2% 60 s after (-4.3). After: knights_diff +21.3, lord_dps_enemy +14.9, archers_diff & map_flag_run -14.8, lord_dps_own +12.9

## 6. Why: the node models

Each explains one result from what happened before it (time order enforced), tested on matches it never saw. AUC = how often a moment that led to the result scores above one that didn't (0.5 = guessing, 1 = perfect).

**deaths** (91 matches, 179804 moments, 5519 results): adds to the simple baseline (AUC 0.918 against 0.804 for health_pct and damage_taken_3s alone).
- **enemies_near** (enemies within 1,500) rises from -22.4 to +26.5 points (0.0..0.5: -22.4; 0.5..1.5: -11.9; 1.5..2.5: +1.8; 2.5..3.5: +4.3; 3.5..4.5: +10.7; 4.5..5.5: +12.8; 5.5..6.5: +14.8; 6.5..7.5: +18.6; 7.5..8.0: +26.5)
- **strength_gap** (own minus enemy team strength) falls from +19.0 to -12.9 points (-976.0..-581.0: +19.0; -433.5..-303.5: +9.9; -142.5..-87.5: +9.7; -32.5..4.5: -1.6; 51.0..106.0: -8.1; 188.0..322.5: -4.0; 433.5..581.0: -16.6)
- **health_pct** (current health %) falls from +40.7 to -6.0 points (1.0..46.5: +40.7; 58.5..66.5: +24.2; 72.5..77.5: +12.0; 81.5..84.5: +5.4; 87.5..90.5: +1.0; 93.5..95.5: -2.4; 97.5..99.5: -5.0)
- **allies_near** (allies within 1,500) falls from +19.9 to -7.4 points (0.0..0.5: +19.9; 0.5..1.5: +9.5; 1.5..2.5: +5.6; 2.5..3.5: -1.4; 3.5..4.5: -2.5; 4.5..5.5: -4.6; 5.5..6.5: -6.1; 6.5..7.0: -7.4)
- **local_diff** (allies minus enemies within 2,000) falls from +24.2 to -20.6 points (-8.0..-3.5: +24.2; -2.5..-1.5: +12.3; -0.5..0.5: -2.8; 1.5..2.5: -7.5; 3.5..4.5: +3.9; 5.5..7.0: -20.6)
- **minute** (match minute) rises from -2.9 to +15.9 points (0.1..1.15: -2.9; 2.05..3.05: -6.2; 4.15..5.15: -5.6; 6.25..7.55: +1.6; 8.95..10.55: -1.9; 12.45..14.55: -1.5; 17.25..20.45: +6.5)
- **own_condition_removal** (own condition removal skills) falls from -7.0 to -22.0 points (1.0..1.5: -7.0; 1.5..2.5: +6.2; 2.5..3.5: +5.8; 3.5..4.5: -0.5; 4.5..5.5: -1.0; 5.5..6.5: -7.5; 6.5..7.5: -8.3; 7.5..8.0: -22.0)
- **enemy_strips** (enemy enchantment removal skills) falls from +35.8 to -3.2 points (0.0..0.5: +35.8; 0.5..1.5: +3.6; 1.5..2.5: +0.9; 2.5..3.5: -3.4; 3.5..4.5: -4.4; 4.5..5.5: -4.1; 5.5..7.0: -3.2)
- **dist_own_pit** (distance from its own pit) rises from -4.0 to +11.9 points (10.0..1363.5: -4.0; 2248.5..3790.5: -1.4; 5071.5..6021.5: -2.8; 6894.5..7630.5: -1.2; 8319.5..8994.5: -1.7; 9878.5..10788.5: +1.0; 12027.5..13424.5: +9.7)

**kill conversion** (91 matches, 1559 moments, 479 results): adds to the simple baseline (AUC 0.76 against 0.672 for burst_damage and target_health_pct alone).
- **burst_damage** (damage in the 2 s burst) rises from -12.0 to +23.5 points (250.0..256.5: -12.0; 264.5..274.5: -10.5; 284.5..294.5: -8.8; 306.5..321.5: -2.6; 335.5..353.5: +1.4; 374.5..403.5: +5.3; 443.5..506.5: +21.9)
- **target_healers_in_range** (target's healers in range) falls from +27.3 to -7.5 points (0.0..0.5: +27.3; 0.5..1.5: -0.4; 1.5..2.5: -5.3; 2.5..3.0: -7.5)
- **target_health_pct** (target health % when the burst started) falls from +20.4 to -11.4 points (0.0..38.5: +20.4; 50.5..57.5: +9.5; 63.5..68.5: +6.4; 72.5..76.5: +4.2; 79.5..83.5: -2.1; 87.5..91.5: -6.7; 95.5..99.5: -10.9)
- **target_ceiling** (target's health ceiling) falls from +25.2 to -9.8 points (0.4..0.69: +25.2; 0.7..0.76: +12.8; 0.84..0.85: +10.6; 0.88..0.91: +6.9; 0.94..0.95: +4.2; 0.99..1.02: -3.2; 1.1..1.1: -9.8)
- **strength_gap** (attacking minus target team strength) rises from -11.2 to +14.6 points (-958.0..-561.5: -11.2; -381.5..-145.5: -6.4; -74.0..-8.0: -1.6; 0.0..71.5: +0.1; 104.5..145.5: -1.0; 274.5..381.5: +0.1; 518.5..611.0: +12.8)
- **enemy_prots** (target team's prot skills) falls from +8.5 to -4.3 points (1.0..2.5: +8.5; 3.5..4.5: +7.0; 6.5..7.5: +5.6; 8.5..9.5: +3.7; 10.5..11.5: -1.3; 12.5..13.5: -2.9; 14.5..15.5: -4.4)
- **target_prot_up** (a prot on the target) falls from +2.6 to -5.0 points (0.0..0.5: +2.6; 0.5..1.0: -5.0)
- **own_interrupts_v_enemy_heals** (attackers' interrupt skills minus target team's heals) falls from +4.1 to -5.0 points (-16.0..-15.5: +4.1; -14.5..-13.5: +4.1; -12.5..-11.5: +2.6; -10.5..-9.5: +0.1; -8.5..-7.5: -1.8; -6.5..-5.5: -4.8; -4.5..-1.0: -5.0)
- **target_hexes** (hexes on the target) rises from -1.6 to +30.9 points (0.0..0.5: -1.6; 1.5..2.5: +0.7; 3.5..4.5: +3.5; 5.5..6.5: +8.4; 7.5..8.5: +29.0)

**flag answer** (seconds an answer to an enemy capture was slower than possible; 77 matches, 653 rows): adds to the simple baseline (typical error 17.6s against 28.6s for the median; explains 70% of the spread).
- **parked_s** (seconds the flag lay parked (dropped 5 s or more: not running yet)): 0.0..2.5: -6.3 s; 9.5..14.5: +5.0 s; 19.5..28.5: +16.4 s; 35.5..41.0: +35.3 s; 50.0..65.0: +51.4 s; 87.5..106.0: +63.4 s; 135.0..291.0: +69.7 s
- **own_deaths_during** (own deaths during the answer): 0.0..0.5: -3.9 s; 0.5..1.5: +7.6 s; 1.5..2.5: +12.9 s; 2.5..3.5: +21.9 s; 3.5..4.5: +24.8 s; 4.5..5.5: +30.9 s; 5.5..8.0: +48.3 s; 8.0..17.0: +71.7 s
- **enemy_deaths_during** (enemy deaths during the answer): 0.0..0.5: -3.8 s; 0.5..1.5: +7.9 s; 1.5..2.5: +15.9 s; 2.5..3.5: +22.0 s; 3.5..4.5: +24.0 s; 4.5..7.0: +26.6 s
- **enemies_in_the_way** (enemy presence along the runner's trip back to the spawn): 0.0..0.5: -5.6 s; 5.5..11.5: -2.9 s; 16.5..20.5: -1.8 s; 26.5..37.5: -0.9 s; 51.5..66.5: +2.2 s; 88.5..110.0: +7.1 s; 144.5..217.0: +16.0 s
- **carrier_damage_taken** (damage the carrier took while carrying): 0.0..1.0: -3.4 s; 27.5..50.5: -4.0 s; 77.0..100.5: -1.9 s; 131.5..193.0: +0.5 s; 248.5..288.5: +3.7 s; 388.0..515.5: +6.1 s; 650.0..1040.0: +11.7 s
- **runner_to_spawn** (runner's distance to its flag spawn when the enemy captured): 4.0..782.0: -10.2 s; 1428.5..2252.0: -3.1 s; 3356.5..4010.5: -0.3 s; 4544.0..5243.5: +2.0 s; 5851.0..6483.5: +3.7 s; 6952.0..7508.0: +3.5 s; 8238.5..9061.0: +2.6 s
- **quick_handoffs** (quick hand-offs (a teammate picked it up within 5 s)): 0.0..0.5: -2.0 s; 0.5..1.5: +5.8 s; 1.5..2.5: +10.3 s; 2.5..3.0: +20.0 s
- **possible_s** (fastest possible answer (s) from the flag model at the enemy's capture): 0.0..4.5: -1.0 s; 9.5..17.5: +0.4 s; 23.5..29.5: +1.3 s; 33.5..37.5: +3.8 s; 41.5..46.5: +2.4 s; 50.5..55.5: -0.5 s; 62.5..69.5: -5.0 s
- **strength_gap** (own minus enemy team strength): -976.0..-572.5: +4.9 s; -425.0..-321.5: +3.7 s; -185.5..-101.0: +1.2 s; -32.5..-4.5: -0.6 s; 19.0..80.5: -1.4 s; 142.5..303.5: -2.4 s; 415.5..581.0: -2.7 s
- **forced_drops** (drops with the carrier hit in the 5 s before, or dying): 0.0..0.5: -1.0 s; 0.5..1.5: +10.6 s; 1.5..4.0: +16.7 s

**npc loss** (91 matches, 9098 moments, 1795 results): adds to the simple baseline (AUC 0.835 against 0.756 for attackers and defenders alone).
- **npc_damage_5s** (damage on the pit NPCs in the last 5 s) rises from -17.1 to +34.5 points (0.0..0.5: -17.1; 22.5..37.5: +1.3; 51.5..70.5: +7.0; 90.5..113.5: +10.9; 136.5..162.5: +24.2; 194.5..234.5: +27.3; 289.5..382.5: +32.6)
- **defenders** (own players in the pit) falls from +31.5 to -35.1 points (0.0..0.5: +31.5; 0.5..1.5: +18.8; 1.5..2.5: +12.4; 2.5..3.5: +3.0; 3.5..4.5: -10.7; 4.5..5.5: -11.7; 5.5..6.5: -12.8; 6.5..7.5: -26.8; 7.5..8.0: -35.1)
- **defenders_elsewhere** (own players alive outside the pit) falls from +18.6 to -3.5 points (0.0..0.5: +18.6; 0.5..1.5: +9.8; 1.5..2.5: +9.4; 2.5..3.5: +4.4; 3.5..4.5: -6.4; 4.5..5.5: -13.6; 5.5..6.5: -13.8; 6.5..7.5: -13.5; 7.5..8.0: -3.5)
- **defender_healers** (of which healers) falls from +22.5 to -8.1 points (0.0..0.5: +22.5; 0.5..1.5: -1.5; 1.5..2.5: -5.8; 2.5..3.0: -8.1)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -13.0 to +7.9 points (1.9..18.75: -13.0; 28.8..32.15: -5.9; 34.9..45.65: -3.8; 54.8..64.25: +3.5; 66.25..73.15: +5.7; 77.9..86.85: +8.0; 99.1..111.3: +8.2)
- **attackers_share** (share of the attacking team's live players in the pit (OG comms: merge before pushing the pit)) rises from -11.5 to +9.0 points (0.12..0.13: -11.5; 0.16..0.18: -5.7; 0.23..0.27: -4.2; 0.35..0.39: -2.8; 0.46..0.53: +4.5; 0.61..0.69: +7.2; 0.84..0.94: +8.9)
- **attackers** (enemy players in the pit) rises from -7.4 to +10.5 points (1.0..1.5: -7.4; 1.5..2.5: -3.9; 2.5..3.5: -2.6; 3.5..4.5: -1.0; 4.5..5.5: +5.3; 5.5..6.5: +7.6; 6.5..7.5: +9.4; 7.5..8.0: +10.5)
- **strength_gap** (attacking minus defending team strength) rises from -5.9 to +9.0 points (-976.0..-415.5: -5.9; -274.5..-102.5: -11.9; -4.5..60.5: +3.7; 96.0..108.0: -0.3; 248.5..303.5: +0.7; 381.5..434.5: +1.6; 545.0..639.0: +3.4)
- **archers** (own pit archers alive) rises from -6.7 to +5.7 points (0.0..0.5: -6.7; 0.5..1.5: -5.2; 1.5..2.5: +3.6; 2.5..3.0: +5.7)

**lord damage** (Lord damage dealt in the next 10 s while players are in the enemy pit; 88 matches, 10491 rows): adds to the simple baseline (typical error 128.5 against 91.2 for the median; explains 39% of the spread).
- **defenders** (own players in the pit): 0.0..0.5: +240.0; 0.5..1.5: +109.3; 1.5..2.5: +56.4; 2.5..3.5: -12.7; 3.5..4.5: -64.5; 4.5..5.5: -106.3; 5.5..6.5: -140.8; 6.5..7.5: -158.8; 7.5..8.0: -160.1
- **defenders_elsewhere** (own players alive outside the pit): 0.0..0.5: +69.2; 0.5..1.5: +82.5; 1.5..2.5: +74.9; 2.5..3.5: +66.4; 3.5..4.5: +25.6; 4.5..5.5: -13.1; 5.5..6.5: -58.2; 6.5..7.5: -119.0; 7.5..8.0: -229.0
- **bodyguard** (own Bodyguard alive): 0.0..0.5: +128.1; 0.5..1.0: -49.2
- **attackers** (enemy players in the pit): 1.0..1.5: -34.1; 1.5..2.5: -18.7; 2.5..3.5: -21.7; 3.5..4.5: -8.6; 4.5..5.5: +32.2; 5.5..6.5: +33.0; 6.5..7.5: +44.7; 7.5..8.0: +53.7
- **defender_healers** (of which healers): 0.0..0.5: +79.4; 0.5..1.5: -11.0; 1.5..2.5: -10.9; 2.5..3.0: -38.5
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)): 1.9..18.75: -41.3; 28.8..32.15: -27.9; 32.8..43.0: -30.6; 54.55..64.25: -4.0; 66.25..73.15: +18.9; 79.15..87.45: +41.4; 99.95..111.75: +39.6
- **npc_healing_10s** (healing on own pit NPCs and Lord in the last 10 s): 0.0..3.0: -16.3; 42.5..70.5: +5.4; 105.5..142.5: +18.7; 174.5..213.5: +23.3; 259.5..307.5: +25.3; 365.5..431.5: +31.8; 522.5..676.5: +42.1
- **attacker_healers** (of which healers): 0.0..0.5: +14.0; 0.5..1.5: -11.0; 1.5..2.5: +18.2; 2.5..3.0: -40.3
- **seconds_in_pit** (seconds the attackers have been in the pit): 0.0..4.5: -26.2; 10.5..16.5: -22.2; 22.5..28.5: -4.4; 37.5..46.5: +6.5; 58.5..73.5: +21.5; 91.5..115.5: +12.0; 151.5..208.5: +20.0
- **attackers_share** (share of the attacking team's live players in the pit (OG comms: merge before pushing the pit)): 0.12..0.13: -12.4; 0.16..0.18: -21.5; 0.23..0.27: -7.0; 0.35..0.39: -14.8; 0.46..0.53: -18.2; 0.61..0.69: +4.3; 0.84..0.94: +27.0

**lord kill** (88 matches, 10485 moments, 799 results): adds to the simple baseline (AUC 0.961 against 0.944 for attackers and defenders alone).
- **defenders** (own players in the pit) falls from +45.6 to -47.4 points (0.0..0.5: +45.6; 0.5..1.5: +39.2; 1.5..2.5: +21.5; 2.5..3.5: +6.0; 3.5..4.5: -25.9; 4.5..5.5: -31.2; 5.5..6.5: -39.5; 6.5..7.5: -42.5; 7.5..8.0: -47.4)
- **defenders_elsewhere** (own players alive outside the pit) falls from +38.3 to -42.8 points (0.0..0.5: +38.3; 0.5..1.5: +21.3; 1.5..2.5: +20.5; 2.5..3.5: +19.3; 3.5..4.5: +17.6; 4.5..5.5: -19.2; 5.5..6.5: -29.0; 6.5..7.5: -42.2; 7.5..8.0: -42.8)
- **minute** (match minute) rises from -45.6 to +28.7 points (0.5..2.75: -45.6; 3.75..4.85: -40.4; 5.85..6.95: +7.5; 8.15..9.55: +17.2; 11.05..12.85: +18.0; 15.05..17.65: +26.9; 20.05..23.25: +28.2)
- **attackers** (enemy players in the pit) rises from -32.0 to +28.8 points (1.0..1.5: -32.0; 1.5..2.5: -9.0; 2.5..3.5: -1.0; 3.5..4.5: +2.7; 4.5..5.5: +23.5; 5.5..6.5: +25.9; 6.5..7.5: +27.5; 7.5..8.0: +28.8)
- **defender_healers** (of which healers) falls from +32.7 to -35.8 points (0.0..0.5: +32.7; 0.5..1.5: +10.2; 1.5..2.5: -3.3; 2.5..3.0: -35.8)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -24.6 to +23.0 points (1.9..18.75: -24.6; 28.8..32.15: -25.9; 32.8..43.0: -11.2; 54.55..64.25: -7.7; 66.25..73.15: +4.9; 79.15..87.45: +26.2; 99.95..111.75: +27.1)
- **res_in** (seconds until the next res) rises from -43.9 to +2.6 points (1.0..8.5: -43.9; 17.5..26.5: +2.8; 35.5..44.5: +13.7; 53.5..62.5: +11.2; 68.5..74.5: +9.5; 80.5..86.5: +9.0; 95.5..107.5: +5.1)
- **seconds_in_pit** (seconds the attackers have been in the pit) rises from +1.6 to +25.9 points (0.0..4.5: +1.6; 10.5..16.5: -12.8; 22.5..28.5: -12.5; 37.5..46.5: -10.5; 58.5..73.5: +4.2; 91.5..115.5: +10.5; 151.5..208.5: +20.6)

## 7. The usual play

Each choice against the most common one in that kind of decision, in win-chance points over the decision's window, adjusted for the situation, with a 90% range from resampling whole matches. CLEAR = the range excludes 0. Win chance comes from a model that never saw the match. The same comparison over the 30 s BEFORE the decision is a placebo test: a choice can't cause what came before it, so a clear difference there means the effect is partly who makes that choice.

**after wipe** (208 decisions, 86 matches; usual: pushed the pit)
- reset (n 25): -3.2 [-8.1, +2.2]; in the 30 s before: -2.5 [-7.1, +3.1]
- took the flag (n 25): -1.6 [-7.5, +4.4]; in the 30 s before: +1.7 [-6.1, +10.2]

**boost clock** (333 decisions, 83 matches; usual: not running, fought)
- running, fought (n 48): +2.1 [-1.7, +5.2]; in the 30 s before: -1.4 [-3.0, +1.5]
- not running, fell back (n 46): -4.8 [-8.8, -0.8] CLEAR; in the 30 s before: +1.7 [-1.4, +4.4]
- not running, advanced (n 40): -0.2 [-4.1, +3.5]; in the 30 s before: +0.2 [-1.5, +2.1]
- running, advanced (n 39): +2.8 [-0.4, +5.7]; in the 30 s before: +1.0 [-2.0, +4.1]
- not running, held (n 19): -2.7 [-5.5, -0.2] CLEAR; in the 30 s before: +0.2 [-2.8, +2.0]
- not running, to the spawn (n 17): -0.6 [-3.4, +1.8]; in the 30 s before: +0.8 [-1.3, +2.9]
- running, fell back (n 13): +0.4 [-3.0, +4.5]; in the 30 s before: -0.7 [-4.8, +2.7]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - running, fought, behind in the fight (lowest third, -0.08 or less): -0.7 (n 15 against 52)
  - running, fought, middle third: -0.7 (n 16 against 35)
  - running, fought, ahead in the fight (top third, above -0.00): +2.7 (n 17 against 24)
  - not running, fell back, behind in the fight (lowest third, -0.08 or less): -7.9 (n 17 against 52)
  - not running, fell back, middle third: +0.3 (n 16 against 35)
  - not running, fell back, ahead in the fight (top third, above -0.00): -8.9 (n 13 against 24)
  - not running, advanced, behind in the fight (lowest third, -0.08 or less): too few yet (n 7 against 52; means -0.1 against 0.5)
  - not running, advanced, middle third: -0.6 (n 13 against 35)
  - not running, advanced, ahead in the fight (top third, above -0.00): -0.3 (n 20 against 24)
  - running, advanced, behind in the fight (lowest third, -0.08 or less): too few yet (n 2 against 52; means 10.2 against 0.5)
  - running, advanced, middle third: -2.1 (n 17 against 35)
  - running, advanced, ahead in the fight (top third, above -0.00): +1.5 (n 20 against 24)
  - not running, held, behind in the fight (lowest third, -0.08 or less): too few yet (n 4 against 52; means -0.6 against 0.5)
  - not running, held, middle third: too few yet (n 9 against 35; means -0.9 against -1.1)
  - not running, held, ahead in the fight (top third, above -0.00): too few yet (n 6 against 24; means -3.6 against -1.6)
  - not running, to the spawn, behind in the fight (lowest third, -0.08 or less): -1.6 (n 10 against 52)
  - not running, to the spawn, middle third: too few yet (n 6 against 35; means -1.6 against -1.1)
  - not running, to the spawn, ahead in the fight (top third, above -0.00): too few yet (n 1 against 24; means 2.0 against -1.6)
  - running, fell back, behind in the fight (lowest third, -0.08 or less): too few yet (n 4 against 52; means 0.3 against 0.5)
  - running, fell back, middle third: too few yet (n 5 against 35; means -4.7 against -1.1)
  - running, fell back, ahead in the fight (top third, above -0.00): too few yet (n 4 against 24; means 1.4 against -1.6)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - running, fought, Isle of Meditation: +3.4 (n 10 against 29)
  - running, fought, Uncharted Isle: -2.1 (n 10 against 18)
  - not running, fell back, Isle of Meditation: -3.4 (n 10 against 29)
  - not running, advanced, Isle of Meditation: +1.4 (n 14 against 29)
  - running, advanced, Isle of Meditation: +2.4 (n 11 against 29)

**enemy pickup** (1211 decisions, 87 matches; usual: held, fought)
- already running, fought (n 161): -2.2 [-5.2, +0.7]; in the 30 s before: +1.9 [-0.1, +3.8]
- held, advanced (n 153): +3.3 [-0.4, +7.1]; in the 30 s before: +1.6 [-0.3, +3.3]
- already running, advanced (n 134): -0.5 [-2.9, +2.4]; in the 30 s before: +2.0 [-0.0, +4.3]
- held, fell back (n 105): -4.1 [-7.6, -1.3] CLEAR; in the 30 s before: +0.1 [-2.2, +1.7]
- ran, fell back (n 79): -2.6 [-5.7, +0.5]; in the 30 s before: +0.8 [-1.8, +4.0]
- already running, fell back (n 74): -2.0 [-5.6, +1.8]; in the 30 s before: -1.0 [-4.0, +1.2]
- ran, fought (n 69): +0.5 [-1.7, +4.1]; in the 30 s before: -1.2 [-4.8, +2.1]
- ran, advanced (n 69): -1.6 [-4.6, +1.9]; in the 30 s before: +1.7 [-0.7, +3.5]
- already running, held (n 42): -1.9 [-6.4, +2.2]; in the 30 s before: +0.1 [-1.1, +1.6]
- ran, held (n 32): -2.1 [-5.4, +0.9]; in the 30 s before: +0.2 [-2.2, +2.7]
- held, held (n 26): -0.7 [-7.1, +4.0]; in the 30 s before: -1.7 [-9.4, +7.3]
- held, to the spawn (n 12): -1.5 [-8.0, +3.4]; in the 30 s before: -0.5 [-9.7, +5.4]
- ran, to the spawn (n 6): -4.1 [-16.2, +4.0]; in the 30 s before: +6.0 [-3.3, +18.7]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - already running, fought, behind in the fight (lowest third, -0.01 or less): +4.6 (n 54 against 82)
  - already running, fought, middle third: -4.8 (n 50 against 69)
  - already running, fought, ahead in the fight (top third, above +0.02): -6.3 (n 57 against 98)
  - held, advanced, behind in the fight (lowest third, -0.01 or less): +11.5 (n 25 against 82)
  - held, advanced, middle third: -0.2 (n 61 against 69)
  - held, advanced, ahead in the fight (top third, above +0.02): +0.2 (n 67 against 98)
  - already running, advanced, behind in the fight (lowest third, -0.01 or less): +5.5 (n 37 against 82)
  - already running, advanced, middle third: -2.3 (n 55 against 69)
  - already running, advanced, ahead in the fight (top third, above +0.02): -3.4 (n 42 against 98)
  - held, fell back, behind in the fight (lowest third, -0.01 or less): +1.6 (n 51 against 82)
  - held, fell back, middle third: -5.7 (n 24 against 69)
  - held, fell back, ahead in the fight (top third, above +0.02): -8.8 (n 30 against 98)
  - ran, fell back, behind in the fight (lowest third, -0.01 or less): +5.0 (n 36 against 82)
  - ran, fell back, middle third: -9.8 (n 22 against 69)
  - ran, fell back, ahead in the fight (top third, above +0.02): -4.7 (n 21 against 98)
  - already running, fell back, behind in the fight (lowest third, -0.01 or less): +3.9 (n 34 against 82)
  - already running, fell back, middle third: -1.1 (n 21 against 69)
  - already running, fell back, ahead in the fight (top third, above +0.02): -3.0 (n 19 against 98)
  - ran, fought, behind in the fight (lowest third, -0.01 or less): +6.7 (n 27 against 82)
  - ran, fought, middle third: -2.9 (n 17 against 69)
  - ran, fought, ahead in the fight (top third, above +0.02): +0.4 (n 25 against 98)
  - ran, advanced, behind in the fight (lowest third, -0.01 or less): +4.3 (n 19 against 82)
  - ran, advanced, middle third: -0.6 (n 29 against 69)
  - ran, advanced, ahead in the fight (top third, above +0.02): -5.4 (n 21 against 98)
  - already running, held, behind in the fight (lowest third, -0.01 or less): +12.2 (n 13 against 82)
  - already running, held, middle third: -8.6 (n 24 against 69)
  - already running, held, ahead in the fight (top third, above +0.02): too few yet (n 5 against 98; means -1.8 against 4.1)
  - ran, held, behind in the fight (lowest third, -0.01 or less): +13.2 (n 13 against 82)
  - ran, held, middle third: -7.2 (n 14 against 69)
  - ran, held, ahead in the fight (top third, above +0.02): too few yet (n 5 against 98; means -17.5 against 4.1)
  - held, held, behind in the fight (lowest third, -0.01 or less): too few yet (n 9 against 82; means 7.6 against -4.4)
  - held, held, middle third: -5.7 (n 12 against 69)
  - held, held, ahead in the fight (top third, above +0.02): too few yet (n 5 against 98; means 0.1 against 4.1)
  - held, to the spawn, behind in the fight (lowest third, -0.01 or less): too few yet (n 9 against 82; means -1.7 against -4.4)
  - held, to the spawn, middle third: too few yet (n 2 against 69; means -0.7 against 3.5)
  - held, to the spawn, ahead in the fight (top third, above +0.02): too few yet (n 1 against 98; means -0.3 against 4.1)
  - ran, to the spawn, behind in the fight (lowest third, -0.01 or less): too few yet (n 1 against 82; means -2.7 against -4.4)
  - ran, to the spawn, middle third: too few yet (n 2 against 69; means -0.1 against 3.5)
  - ran, to the spawn, ahead in the fight (top third, above +0.02): too few yet (n 3 against 98; means -10.7 against 4.1)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - already running, fought, Corrupted Isle: +0.8 (n 14 against 85)
  - already running, fought, Imperial Isle: -0.8 (n 25 against 11)
  - already running, fought, Isle of Jade: +1.0 (n 10 against 34)
  - already running, fought, Isle of Meditation: -5.5 (n 22 against 33)
  - already running, fought, Nomad's Isle: -2.6 (n 28 against 25)
  - already running, fought, Uncharted Isle: +3.4 (n 46 against 31)
  - held, advanced, Corrupted Isle: +1.5 (n 42 against 85)
  - held, advanced, Isle of Jade: -1.4 (n 27 against 34)
  - held, advanced, Isle of Meditation: +1.7 (n 29 against 33)
  - held, advanced, Nomad's Isle: +10.7 (n 12 against 25)
  - held, advanced, Uncharted Isle: +7.9 (n 16 against 31)
  - already running, advanced, Corrupted Isle: -2.7 (n 10 against 85)
  - already running, advanced, Isle of Jade: -3.7 (n 10 against 34)
  - already running, advanced, Isle of Meditation: +1.8 (n 39 against 33)
  - already running, advanced, Uncharted Isle: +1.9 (n 38 against 31)
  - held, fell back, Corrupted Isle: -13.1 (n 12 against 85)
  - held, fell back, Isle of Jade: -10.0 (n 11 against 34)
  - held, fell back, Isle of Meditation: -0.8 (n 27 against 33)
  - held, fell back, Uncharted Isle: +1.2 (n 25 against 31)
  - ran, fell back, Imperial Isle: -3.0 (n 12 against 11)
  - ran, fell back, Uncharted Isle: +0.5 (n 26 against 31)
  - already running, fell back, Isle of Meditation: +0.7 (n 10 against 33)
  - already running, fell back, Uncharted Isle: +3.1 (n 32 against 31)
  - ran, fought, Imperial Isle: +2.2 (n 14 against 11)
  - ran, fought, Uncharted Isle: +0.5 (n 16 against 31)
  - ran, advanced, Imperial Isle: -3.2 (n 10 against 11)
  - ran, advanced, Isle of Jade: +0.5 (n 13 against 34)
  - ran, advanced, Uncharted Isle: +3.2 (n 30 against 31)
  - already running, held, Uncharted Isle: +6.3 (n 14 against 31)
  - ran, held, Isle of Jade: -5.2 (n 15 against 34)

- **late_game**: not enough decisions yet (22)
**power play** (742 decisions, 91 matches; usual: pushed, advanced)
- pushed, fought (n 209): +0.0 [-1.5, +1.5]; in the 30 s before: -1.1 [-2.4, +0.2]
- held, fought (n 152): -2.3 [-4.1, -0.8] CLEAR; in the 30 s before: -0.6 [-2.1, +0.8]
- held, fell back (n 57): -2.9 [-5.2, -0.6] CLEAR; in the 30 s before: -3.2 [-6.7, -0.0] ALREADY DIFFERENT BEFORE: partly who chooses it
- pushed, fell back (n 36): -1.8 [-4.8, +1.2]; in the 30 s before: -2.2 [-4.2, +0.3]
- held, advanced (n 21): +2.0 [-1.7, +7.0]; in the 30 s before: -2.9 [-6.3, -0.1] ALREADY DIFFERENT BEFORE: partly who chooses it
- pushed, held (n 5): -3.2 [-7.4, +1.3]; in the 30 s before: +6.9 [-3.5, +16.1]
- held, held (n 5): -4.1 [-8.4, -0.1] CLEAR; in the 30 s before: -9.1 [-28.1, +3.6]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - pushed, fought, behind in the fight (lowest third, +0.00 or less): +2.0 (n 60 against 79)
  - pushed, fought, middle third: -1.2 (n 64 against 76)
  - pushed, fought, ahead in the fight (top third, above +0.09): -2.2 (n 85 against 102)
  - held, fought, behind in the fight (lowest third, +0.00 or less): -2.0 (n 61 against 79)
  - held, fought, middle third: -4.3 (n 58 against 76)
  - held, fought, ahead in the fight (top third, above +0.09): -3.8 (n 33 against 102)
  - held, fell back, behind in the fight (lowest third, +0.00 or less): -5.7 (n 24 against 79)
  - held, fell back, middle third: -1.2 (n 20 against 76)
  - held, fell back, ahead in the fight (top third, above +0.09): -4.3 (n 13 against 102)
  - pushed, fell back, behind in the fight (lowest third, +0.00 or less): -2.7 (n 14 against 79)
  - pushed, fell back, middle third: -1.1 (n 17 against 76)
  - pushed, fell back, ahead in the fight (top third, above +0.09): too few yet (n 5 against 102; means -3.0 against 4.1)
  - held, advanced, behind in the fight (lowest third, +0.00 or less): +3.2 (n 10 against 79)
  - held, advanced, middle third: too few yet (n 6 against 76; means 0.2 against 1.9)
  - held, advanced, ahead in the fight (top third, above +0.09): too few yet (n 5 against 102; means 8.9 against 4.1)
  - pushed, held, behind in the fight (lowest third, +0.00 or less): too few yet (n 3 against 79; means -4.4 against 2.5)
  - pushed, held, middle third: too few yet (n 1 against 76; means -0.4 against 1.9)
  - pushed, held, ahead in the fight (top third, above +0.09): too few yet (n 1 against 102; means 3.2 against 4.1)
  - held, held, behind in the fight (lowest third, +0.00 or less): too few yet (n 2 against 79; means -0.6 against 2.5)
  - held, held, middle third: too few yet (n 3 against 76; means -0.8 against 1.9)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - pushed, fought, Corrupted Isle: -4.6 (n 28 against 28)
  - pushed, fought, Imperial Isle: +5.1 (n 14 against 19)
  - pushed, fought, Isle of Jade: -5.0 (n 30 against 32)
  - pushed, fought, Isle of Meditation: -0.7 (n 55 against 71)
  - pushed, fought, Isle of Solitude: +0.6 (n 17 against 18)
  - pushed, fought, Nomad's Isle: +2.7 (n 21 against 13)
  - pushed, fought, Uncharted Isle: -3.0 (n 26 against 51)
  - held, fought, Corrupted Isle: -5.6 (n 13 against 28)
  - held, fought, Imperial Isle: -4.5 (n 17 against 19)
  - held, fought, Isle of Jade: -9.1 (n 12 against 32)
  - held, fought, Isle of Meditation: -1.2 (n 31 against 71)
  - held, fought, Isle of Solitude: -0.5 (n 11 against 18)
  - held, fought, Nomad's Isle: -3.5 (n 26 against 13)
  - held, fought, Uncharted Isle: -1.4 (n 25 against 51)
  - held, fell back, Isle of Meditation: -5.9 (n 16 against 71)
  - held, fell back, Uncharted Isle: -2.9 (n 11 against 51)

**split in base** (180 decisions, 57 matches; usual: defended without a collapse)
- collapsed (n 80): -7.7 [-12.9, -2.8] CLEAR; in the 30 s before: -1.4 [-3.6, +1.5]
- missed (n 14): -6.1 [-16.4, +1.9]; in the 30 s before: -0.1 [-3.1, +7.9]
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - collapsed, Corrupted Isle: -5.3 (n 11 against 10)
  - collapsed, Isle of Meditation: -0.7 (n 27 against 15)

**Collapses on a split: time away and its cost** (`S32`; per collapse, averages; main = what the main fight lost while the collapsers were away)

| Group | Cases | Away (median s) | Split killed | Collapser died | Own deaths at main | Enemy deaths at main | Flag lead change | DP change | Win change |
|---|---|---|---|---|---|---|---|---|---|
| all | 88 | 22 | 18 | 10 | 0.59 | 0.41 | +1.2 | -3.4 | -4.2 |
| away under 30 s | 51 | 7 | 13 | 1 | 0.02 | 0.1 | -0.4 | +0.3 | -3.0 |
| away 30 to 60 s | 16 | 43 | 2 | 3 | 0.88 | 0.56 | -7 | -11.9 | +4.6 |
| away 60 s or more | 21 | 108 | 3 | 6 | 1.76 | 1.05 | +11.2 | -6.0 | -13.6 |
| before 20:00 | 80 | 23 | 14 | 8 | 0.44 | 0.41 | +2.4 | -4.5 | -4.5 |
| from 20:00 | 8 | 18 | 4 | 2 | 2.12 | 0.38 | -10.8 | +6.9 | -0.9 |
| split member killed | 18 | 13.5 | 18 | 1 | 0.06 | 1 | +0.3 | +1.2 | +0.6 |
| no kill | 70 | 25 | 0 | 9 | 0.73 | 0.26 | +1.4 | -4.6 | -5.4 |

**Leverage: where the choice matters most** (share of the spread in win-chance change explained by the choice beyond the situation; range = best minus worst choice, in points)

- boost clock (333): choice explains 4.6% (situation 4.5%); range 7.3 points, best running, fought, worst not running, fell back
- split in base (180): choice explains 3.4% (situation 7.5%); range 7.5 points, best defended without a collapse, worst collapsed
- power play (742): choice explains 1.3% (situation 2.9%); range 5.8 points, best held, advanced, worst pushed, held
- enemy pickup (1211): choice explains 1.2% (situation 3.0%); range 9.0 points, best held, advanced, worst ran, to the spawn
- after wipe (208): choice explains 0.5% (situation 12.4%); range 2.8 points, best pushed the pit, worst reset

**Behaviour clusters: what teams actually did** (each decision's response grouped by what every player did in the next 20 s; UNNAMED = a group no single named choice covers: a response for Denning to name or reject)

*after wipe* (2 groups, separation 0.31):
- n 126: fought (midline, 1.9 of 8), fought (backline, 1.4 of 8), fought (frontline, 0.9 of 8), held (backline, 0.9 of 8); named as {'pushed the pit': 109, 'reset': 9, 'took the flag': 8}; win change -0.9
- n 82: advanced (backline, 2.5 of 8), advanced (midline, 2.5 of 8), advanced (frontline, 1.3 of 8); named as {'pushed the pit': 49, 'took the flag': 17, 'reset': 16}; win change 2.1 UNNAMED
*boost clock* (4 groups, separation 0.2):
- n 165: fought (midline, 2.2 of 8), fought (backline, 1.4 of 8), fought (frontline, 1.0 of 8), held (backline, 0.6 of 8); named as {'not running, fought': 105, 'running, fought': 44, 'not running, to the spawn': 8}; win change 0.1
- n 81: advanced (midline, 2.3 of 8), advanced (backline, 1.8 of 8), fought (midline, 0.6 of 8), advanced (frontline, 0.5 of 8); named as {'not running, advanced': 37, 'running, advanced': 35, 'not running, fought': 4}; win change -2.0 UNNAMED
- n 76: fell back (midline, 1.9 of 8), fell back (backline, 1.5 of 8), fell back (frontline, 0.6 of 8), fought (midline, 0.5 of 8); named as {'not running, fell back': 45, 'running, fell back': 12, 'not running, to the spawn': 6}; win change -4.1 UNNAMED
- n 23: held (midline, 3.0 of 8), held (backline, 2.4 of 8), held (frontline, 0.5 of 8); named as {'not running, held': 18, 'running, held': 4, 'not running, to the spawn': 1}; win change -1.1
*enemy pickup* (4 groups, separation 0.21):
- n 450: fought (midline, 2.3 of 8), fought (backline, 1.4 of 8), fought (frontline, 1.0 of 8), held (backline, 0.8 of 8); named as {'held, fought': 208, 'already running, fought': 149, 'ran, fought': 58}; win change -1.4 UNNAMED
- n 378: advanced (midline, 2.2 of 8), advanced (backline, 1.9 of 8), advanced (frontline, 0.9 of 8), fought (backline, 0.5 of 8); named as {'held, advanced': 146, 'already running, advanced': 119, 'ran, advanced': 63}; win change 4.5 UNNAMED
- n 279: fell back (midline, 1.9 of 8), fell back (backline, 1.8 of 8), fell back (frontline, 0.7 of 8); named as {'held, fell back': 97, 'ran, fell back': 72, 'already running, fell back': 68}; win change -1.4 UNNAMED
- n 104: held (midline, 2.2 of 8), held (backline, 1.8 of 8), fought (midline, 0.6 of 8); named as {'already running, held': 39, 'ran, held': 30, 'held, held': 21}; win change -0.1 UNNAMED
*power play* (3 groups, separation 0.27):
- n 354: fought (midline, 2.4 of 8), fought (backline, 1.7 of 8), fought (frontline, 1.1 of 8), held (backline, 0.8 of 8); named as {'pushed, fought': 192, 'held, fought': 137, 'pushed, advanced': 16}; win change 1.1 UNNAMED
- n 261: advanced (midline, 2.4 of 8), advanced (backline, 2.3 of 8), advanced (frontline, 1.1 of 8); named as {'pushed, advanced': 236, 'held, advanced': 18, 'pushed, fought': 5}; win change 3.2
- n 132: fell back (backline, 1.9 of 8), fell back (midline, 1.8 of 8), fell back (frontline, 0.7 of 8), fought (midline, 0.7 of 8); named as {'held, fell back': 55, 'pushed, fell back': 36, 'held, fought': 14}; win change -0.6 UNNAMED
*split in base* (3 groups, separation 0.2):
- n 85: fought (midline, 2.3 of 8), fought (backline, 1.2 of 8), fought (frontline, 0.9 of 8), held (backline, 0.8 of 8); named as {'defended without a collapse': 46, 'collapsed': 34, 'missed': 5}; win change 0.2 UNNAMED
- n 48: advanced (midline, 2.3 of 8), advanced (backline, 1.2 of 8), advanced (frontline, 0.6 of 8), fought (midline, 0.5 of 8); named as {'defended without a collapse': 22, 'collapsed': 22, 'missed': 4}; win change -2.0 UNNAMED
- n 46: fell back (midline, 2.7 of 8), fell back (backline, 1.5 of 8), fell back (frontline, 0.8 of 8); named as {'collapsed': 24, 'defended without a collapse': 17, 'missed': 5}; win change -3.0 UNNAMED

## 8. What results and causes are worth

Win points for the team it happened to, from 91 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 281 | -0.8 | -6.4 to +4.8 | +2.9 | no |
| capture | 746 | +2.6 | +1.7 to +3.5 | +2.4 | yes |
| death (any) | 1768 | -5.2 | -7.2 to -3.2 | -3.8 | yes |
| death: against a spike build | 455 | -8.0 | -15.4 to -1.4 | -3.1 | yes |
| death: against other builds | 1313 | -4.2 | -6.8 to -1.8 | -4.0 | yes |
| death: back within 20 s | 281 | -3.6 | -7.8 to -0.1 | -1.1 | yes |
| death: down 20 to 60 s | 668 | -5.0 | -7.8 to -2.4 | -2.3 | yes |
| death: down 60 s or more | 819 | -5.9 | -8.4 to -3.6 | -5.8 | yes |
| death: healer | 599 | -5.2 | -8.3 to -2.5 | -4.3 | yes |
| death: healer in own base or pit, back within 15 s (likely deliberate) | 37 | +1.2 | -2.8 to +6.9 | +2.0 | no |
| death: healer, other | 562 | -5.6 | -8.6 to -2.9 | -4.7 | yes |
| death: not a healer | 1169 | -5.2 | -8.1 to -2.8 | -3.5 | yes |
| death: team boosted (morale above zero) | 206 | -24.0 | -36.6 to -12.7 | -7.7 | yes |
| death: team not boosted | 1562 | -2.7 | -5.6 to +0.0 | -3.2 | no |
| footman lost (base NPC) | 257 | +1.1 | -3.1 to +5.0 | -0.0 | no |
| pit NPC lost (any): taken by a spike build | 142 | -2.8 | -6.8 to +1.6 | -2.4 | no |
| pit NPC lost (any): taken by other builds | 573 | -1.7 | -3.8 to +0.8 | -0.3 | no |
| pit NPC lost: archer | 410 | +0.5 | -1.8 to +3.4 | +0.1 | no |
| pit NPC lost: bodyguard | 100 | -3.7 | -6.7 to -1.0 | +0.3 | yes |
| pit NPC lost: knight | 205 | -5.8 | -8.5 to -3.3 | -2.9 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value.

*deaths* (per 10 s in that state; result worth -5.2 points, base rate 1.5%):

- enemies within 1,500 7.5 to 8: result chance +3.2 points, worth -0.17 win points
- own minus enemy team strength -976 to -581: result chance +1.8 points, worth -0.09 win points
- current health % 1 to 46.5: result chance +11.4 points, worth -0.59 win points
- allies within 1,500 0 to 0.5: result chance +1.9 points, worth -0.1 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.7 points, worth -0.14 win points
- match minute 20.45 to 28: result chance +1.4 points, worth -0.07 win points
- own condition removal skills 7.5 to 8: result chance -0.9 points, worth +0.05 win points

*kill conversion* (per burst, for the attacking team; result worth +5.2 points, base rate 30.7%):

- damage in the 2 s burst 506.5 to 839: result chance +24.4 points, worth +1.27 win points
- target's healers in range 0 to 0.5: result chance +29.4 points, worth +1.53 win points
- target health % when the burst started 0 to 38.5: result chance +20.6 points, worth +1.07 win points
- target's health ceiling 0.4 to 0.69: result chance +26.6 points, worth +1.38 win points
- attacking minus target team strength 611 to 976: result chance +14.0 points, worth +0.73 win points
- target team's prot skills 1 to 2.5: result chance +7.7 points, worth +0.4 win points
- a prot on the target 0.5 to 1: result chance -4.1 points, worth -0.21 win points
- attackers' interrupt skills minus target team's heals -5.5 to -4.5: result chance -4.2 points, worth -0.22 win points

*npc loss* (per case, for the defending team; result worth -1.9 points, base rate 19.7%):

- damage on the pit NPCs in the last 5 s 382.5 to 1170: result chance +37.5 points, worth -0.71 win points
- own players in the pit 7.5 to 8: result chance -15.6 points, worth +0.3 win points
- own players alive outside the pit 0 to 0.5: result chance +15.2 points, worth -0.29 win points
- of which healers 0 to 0.5: result chance +19.6 points, worth -0.37 win points
- attackers' measured damage per second against a Lord (benchmarks) 1.9 to 18.75: result chance -7.1 points, worth +0.13 win points
- share of the attacking team's live players in the pit (OG comms: merge before pushing the pit) 0.12 to 0.13: result chance -6.4 points, worth +0.12 win points
- enemy players in the pit 7.5 to 8: result chance +7.6 points, worth -0.14 win points

## The TQs

Denning's four questions, each from the batch's matches. The why comes from forensics and events (every number placed against the same role or situation in every stored match); the different play comes only from measurement: the usual play's choice effects (usual.py), node models read again with the variable changed (models that never saw the match, changes priced in win points with values.py), options that were ready and unused, and benchmarks. Points = win-chance points.

## TQ 1. Behind on flags

*The biggest flag swing in the new matches: push +83 -> -81 by 16:55.0.*

### Flag swing: push v Fun (94d74d87), 16:45.0 to 16:55.0
**Result**: push's flag lead +83 s -> -81 s (-164 s). Stand: Fun -> Fun.
**Captures** (flag model: fastest possible answer after the enemy's capture):
- Fun capped 16:18.0 by 8 Monk, 99 s after push's capture; fastest possible 83 s, so 16 s slower; enemies in the way {'Water Ele': 11, 'Stand Mes': 10, 'Warrior': 8, 'Mes/A': 4}
- Fun: push held 99 s; Fun capped 21 s before a boost, so was down on flags
**Runs** (each run: outcome, and what was done to the runner):
- push Mes/A 15:33.0 to 16:50.0 (77 s): died, lowest health 0%, escort ['Water Ele', 'Warrior', 'Stand Mes', 'Prot', '8 Monk'], pushed by ['Air Ele 2', '8 Monk', 'Air Ele 1', 'Fire Ele 1', 'Fire Ele 2', 'Water Ele']; control on the runner: 16:40.4 crippled by Fun 8 Monk
**Deaths in the window**: 16:50.0 push Mes/A (stand, [1, 8])
- push output in the 20 s before 16:50.0: 0.0 damage per second (below the 10th percentile for team (median 37.1, n 3825)), top target share None, spikes 0
- Fun output in the 20 s before 16:50.0: 102.5 damage per second (above the 90th percentile for team (median 37.1, n 3825)), top target share 0.33, spikes 2
**Why push Mes/A died at 16:50.0** (forensics):
  - Position: yes (nearest allied healer 2888 in the last 5 s, nearest enemy 95, allies in casting range 0, enemies 7)
  - Prots: no prots (0 from teammates, 0 self; 0 of 0 landed); damage 664 (2% attacks, 0% armor-ignoring), burst 655 in 2 s at 16:48.7
  - Healers under interrupt pressure: usual (healers 3, interrupts_per_min 0.0, interrupted 0, casts 6, finished_share 0.83, dazed 0, knockdowns 0, hexes 6)
  - Damage off shield sets: usual (team share 0.19, a shield would have stopped about 107)
  - Own damage: no (0.0 per second on []); enemy damage: high (118.8 per second)
  - Peel: no (peel on a burst is rare: most bursts on this role get none) (0 of 5 attackers controlled; longest free 20.0 s)
  - Casting: unclear (casts 0, interrupted 0, cancelled 0, while_dazed 0)
**After**: 16:58.0 push Warrior
**Why, in short**: push's Mes/A died at 16:50 after 77 s of carrying, 1 s from capturing (main 1v8, alive 6v8); Fun capped at 16:18, 99 s after push's capture, on its 1st run (0 dropped); push pushed the last carrier with Water Ele, Warrior, Earth Ele but its health never went below 52%; deaths in the window: push 1; the position came from earlier: push sent 6 players on a flag run at 15:33 (main left 6v8), the shape that captured 111 of 249 stored runs.

**How it got there** (traced back from 16:55 to when push's main was first outnumbered by 3+, at 16:25):
- At 16:25: main 5v8, alive 6v8, stand Fun (boost in 113 s), push's flag lead +69 s, DP -172 against 77.
- Away from the main: 7 Monk dead 16:10 to 16:55; Earth Ele away (stand) 16:25; Stand Mes dead 16:25 to 16:30; 8 Monk dead 16:35 to 16:55; Water Ele escorting the flag 16:40 to 16:55; Mes/A carrying the flag 16:40 to 16:50; Stand Mes escorting the flag 16:45 to 16:50; Prot escorting the flag 16:45; Earth Ele away (backside) 16:50; Warrior escorting the flag 16:50 to 16:55; Mes/A dead 16:55
- Own deaths on the way: 16:05 7 Monk (stand, [8, 8]); 16:24 Stand Mes (stand, [6, 8]); 16:33 8 Monk (backside, [6, 8]); 16:50 Mes/A (stand, [1, 8])
- push's flag runs in that window, each against every stored run made while the enemy held the stand (run_bench):
  - 15:33 Mes/A with Water Ele, Warrior, Stand Mes, Prot, 8 Monk, main left at 6v8: died. Runs like it: escort 2+ with the main within 2: captured 111 of 249, 0.31 own deaths in the next 40 s, win chance -0.0 points.
    Instead, escort 0-1 with the main within 2: captured 278 of 478, 0.25 own deaths in the next 40 s, win chance +1.4 points.

**A different play (measured)**

- No decision point for the team in the swing.

**Confidence**: low (measured, but the ranges include no effect yet).

## TQ 2. A monk death

*The monk death that cost the most win chance in the new matches: cope v Team (427c825b), cope Prot at 14:08 (backside, numbers [4, 8]); win chance -92.4 points from 10 s before to 30 s after.*

**Why** (forensics, against the same role in every stored match):
- Position: partly (nearest allied healer 340 in the last 5 s, nearest enemy 172, allies in casting range 4, enemies 8)
- Prots: partly the wrong kind (0 from teammates, 1 self; 1 of 1 landed); damage 391 (0% attacks, 23% armor-ignoring), burst 323 in 2 s at 14:04.2; ready and in range but not used: cope 7 Monk Guardian, cope 8 Monk Guardian
- Healers under interrupt pressure: usual (healers 3, interrupts_per_min 3.0, interrupted 1, casts 21, finished_share 0.95, dazed 0, knockdowns 0, hexes 6)
- Damage off shield sets: usual (team share 0.31, a shield would have stopped about 204)
- Own damage: no (14.0 per second on [('Team Dervish', 105), ('Team Air Ele 3', 100)]); enemy damage: high (151.8 per second)
- Peel: no (peel on a burst is rare: most bursts on this role get none) (0 of 4 attackers controlled; longest free 20.0 s)
- Casting: usual (casts 8, interrupted 0, cancelled 0, while_dazed 0)
**Why, in short**: the Prot died because the enemy hit unusually hard (151.8 per second), its own team's damage was low (14.0 per second), position (in contact with the enemy, nearest enemy 172), its attackers were not peeled (no (peel on a burst is rare: most bursts on this role get none)). The position itself came from earlier: cope sent 3 players on a flag run at 13:28 (main left 5v8), the shape that captured 0 of 6 stored runs.

**How it got there** (traced back from 14:08 to when cope's main was first outnumbered by 3+, at 13:30):
- At 13:30: main 5v8, alive 8v8, stand Team (boost in 38 s), cope's flag lead +7 s, DP 50 against -101.
- Away from the main: AoB Derv away (own base) 13:00 to 14:05; AoB Derv carrying the flag 13:05 to 13:15; AoB Derv escorting the flag 13:30 to 13:40; Hammer carrying the flag 13:30 to 13:35; Stand Mes 2 escorting the flag 13:30 to 13:35; Prot away (backside) 13:35 to 14:05; 7 Monk away (backside) 13:35 to 14:05; Hammer away (push side) 13:40; Prot away (stand) 13:45; 8 Monk away (push side) 13:45; AoB Derv dead 13:55; Hammer away (backside) 14:00
- Own deaths on the way: 13:45 Stand Mes 2 (push side, [4, 7]); 13:51 AoB Derv (push side, [5, 7]); 14:08 Prot (backside, [4, 8])
- cope's flag runs in that window, each against every stored run made while the enemy held the stand (run_bench):
  - 13:01 AoB Derv alone, main left at 7v8: dropped. Runs like it: escort 0-1 with the main within 2: captured 278 of 478, 0.25 own deaths in the next 40 s, win chance +1.4 points.
  - 13:28 Hammer with AoB Derv, Stand Mes 2, main left at 5v8: dropped. Runs like it: escort 2+ with the main outnumbered by 3+: captured 0 of 6, 1.33 own deaths in the next 40 s, win chance -2.6 points.
    Instead, escort 0-1 with the main outnumbered by 3+: captured 10 of 21, 2 own deaths in the next 40 s, win chance -0.7 points.
  - 14:06 AoB Derv with Hammer, Mes/A, Stand Mes 1, main left at 5v6: dropped. Runs like it: escort 2+ with the main within 2: captured 111 of 249, 0.31 own deaths in the next 40 s, win chance -0.0 points.
    Instead, escort 0-1 with the main within 2: captured 278 of 478, 0.25 own deaths in the next 40 s, win chance +1.4 points.
- Decisions in the lead-up (usual.py):
  - boost clock at 13:38 (main 4v8, flags +27 s, boost in 30, fight state -0.01): chose **running, advanced** (+2.8 [-0.4, +5.7] against the most common choice, not running, fought); in the 15 most similar decisions teams usually chose **running, advanced**; no choice of this kind did measurably better than the one made. In the same fight-state third (middle third) this choice did -2.1 against the usual choice (n 17 against 35, raw).

**How it could have been prevented (measured)**

- Further back (above): the bad numbers were set up before the fight; the earlier choices are priced in "How it got there". The readings below are what was still possible in the last seconds.
- Ready and in range but not used: cope 7 Monk Guardian (casting Healing Burst on cope 7 Monk); cope 8 Monk Guardian (casting Reversal of Fortune on cope 7 Monk)
- Attackers left free (no snare, Blind, Weakness, interrupt, knockdown or hex from its team): Team Mesmer 20.0 s free (nearest own non-healer 4840); Team Air Ele 2 20.0 s free (nearest own non-healer 5911); Team Air Ele 1 20.0 s free (nearest own non-healer 4758)
- Deaths node at 14:05 (AUC 0.918 on unseen matches against 0.804 for health_pct and damage_taken_3s alone): risk 6.3% of dying in the next 10 s; read again with
  - staying with its group: 5.6% (-0.7 points of risk; at this death's measured cost of -92.4 win points, about +0.6 expected; at a typical healer death's -5.2, +0.0)
  - its hexes removed: 5.3% (-1.0 points of risk; at this death's measured cost of -92.4 win points, about +0.9 expected; at a typical healer death's -5.2, +0.1)
  - all of these together: 4.7% (-1.6 points of risk; at this death's measured cost of -92.4 win points, about +1.5 expected; at a typical healer death's -5.2, +0.1)

**Confidence**: low (measured, but the ranges include no effect yet).

## TQ 3. A power play without a kill

*The biggest in the new matches: main 8v4, pushed, no kill in 71 s.*

### Power play without a kill: hook v cope (d93289f2), 0:11.0 to 1:22.0
**Situation**: main 8v4, alive 8v8, flags even (+1 s), DP 0, boost in None; choice pushed (fought 4, advanced 2, carrying 1, held 1); deaths {'hook': 0, 'cope': 0} in 71 s
**The fight's shape** (every 5 s: own main, the enemy group it faced, distance between them, that group's distance to the rest of its team): 0:11.0 8v4 1743 apart, 1432 from its others; 0:16.0 8v7 366 apart, 4062 from its others; 0:21.0 8v7 60 apart, 4995 from its others; 0:26.0 8v7 79 apart, 5446 from its others; 0:31.0 8v7 79 apart, 5467 from its others; 0:36.0 8v7 67 apart, 5592 from its others; 0:41.0 8v7 101 apart, 5498 from its others; 0:46.0 8v7 96 apart, 5169 from its others; 0:51.0 8v7 81 apart, 4308 from its others; 0:56.0 8v7 64 apart, 3008 from its others; 1:01.0 8v7 111 apart, 1986 from its others; 1:06.0 8v8 95 apart, None from its others; 1:11.0 8v8 106 apart, None from its others; 1:16.0 8v8 114 apart, None from its others; 1:21.0 8v8 70 apart, None from its others
**hook's damage**: 74.3 per second (above the 90th percentile for team (median 37.1, n 3825)); top target share 0.37 (below the 50th percentile for team (median 0.49, n 3825)); targets [('cope Prot', 1949), ('cope Stand Mes', 1311), ('cope Hammer', 628), ('cope Ranger', 544)]; dealers [('hook Warrior', 1444), ('hook Necromancer', 1129), ('hook AoB Derv', 1115), ('hook Mes/A', 988), ('hook Stand Mes', 600)]
- phase 0:00.0 to 0:17.0: 8v0 (backside, job free), damage uptime 0.01, damage-seconds lost {'moving': 61, 'carrying': 17, 'idle': 6}
- phase 0:17.0 to 0:34.0: 8v7 (stand, job convert), damage uptime 0.51, damage-seconds lost {'moving': 18, 'carrying': 14, 'idle': 6, 'knocked down': 4}
- phase 0:34.0 to 0:40.0: 8v7 (stand, job convert), damage uptime 0.53, damage-seconds lost {'moving': 6, 'carrying': 6, 'idle': 2}
- phase 0:40.0 to 0:43.0: 8v7 (stand, job convert), damage uptime 0.73, damage-seconds lost {'moving': 3, 'idle': 1}
- phase 0:43.0 to 0:51.0: 8v7 (stand, job convert), damage uptime 0.68, damage-seconds lost {'moving': 8, 'idle': 5}
- phase 0:51.0 to 1:01.0: 8v7 (stand, job convert), damage uptime 0.66, damage-seconds lost {'moving': 11, 'idle': 6}
- phase 1:01.0 to 1:18.0: 8v8 (stand, job contest), damage uptime 0.44, damage-seconds lost {'moving': 30, 'idle': 17, 'knocked down': 1}
- phase 1:18.0 to 1:21.0: 8v8 (stand, job contest), damage uptime 0.6, damage-seconds lost {'moving': 3, 'idle': 3}
- phase 1:21.0 to 1:47.0: 8v8 (stand, job contest), damage uptime 0.54, damage-seconds lost {'moving': 47, 'idle': 13}
**cope's answer**: healing 97 per second ({'cope 7 Monk': 4246, 'cope 8 Monk': 1148, 'cope Prot': 1128, 'cope AoB Derv': 175}); prots {'Shield Guardian PvP': 5, 'Shielding Hands': 4, 'Guardian': 11, 'Aura of Stability': 2, 'Reversal of Fortune': 2}
- hook's knockdowns landed 2; cope's knockdown immunity casts 2
- Pressure on cope's healers: healers 3, interrupts_per_min 5.9, interrupted 7, casts 67, finished_share 0.9, dazed 0, knockdowns 1, hexes 14 (above the 90th percentile for team (median 0, n 4312))
- Snares, Blind and Weakness hook put on cope: {'weakness': 2}
**Why, in short**: hook had 8v4 at main for 71 s; cope healed 97 per second; not the cause (on the side of power plays that killed): damage 74.3 per second (killing 36.6, not killing 21.1), damage uptime in contact 55% (killing 46%, not killing 35%; most lost to moving), top-target share 0.37 over 4 targets (killing 0.39, not killing 0.53); the biggest burst went on the cope Prot (5.2% to kill), while the same burst on the cope Mes/A read 28.6%.

**How it could have been converted (measured)**

- Against every stored power play (3+ more at main): those that killed had a median 36.6 damage per second and top-target share 0.39 (49 cases); those that didn't, 21.1 and 0.53 (38 cases). hook here: 74.3 and 0.37. Damage uptime: 46% in those that killed, 35% in those that didn't, 55% here.
- Kill-conversion node (AUC 0.76 on unseen matches against 0.672 for burst_damage and target_health_pct alone): the biggest burst, 299 on the cope Prot at 0:36 with 3 attackers, read 5.2% to kill within 8 s; read again with
  - on the cope Mes/A instead: 28.6% (+23.4 points, about +1.2 win points at a converted burst's +5.2)
  - on the cope Stand Mes instead: 13.4% (+8.2 points, about +0.4 win points at a converted burst's +5.2)
  - the target Dazed: 10.6% (+5.4 points, about +0.3 win points at a converted burst's +5.2)
  - on the cope 8 Monk instead: 7.5% (+2.3 points, about +0.1 win points at a converted burst's +5.2)
  - all 5 damage dealers in the burst: 6.1% (+0.9 points, about +0.0 win points at a converted burst's +5.2)
  - on the cope Hammer instead: 6.0% (+0.8 points, about +0.0 win points at a converted burst's +5.2)
- Bursts in the window: 2, on Prot (299), Prot (258)
- The choice at the power play (usual.py):
  - power play at 0:11 (main 8v4, flags +1 s, boost in None, fight state 0.0): chose **pushed, fought** (+0.0 [-1.5, +1.5] against the most common choice, pushed, advanced); in the 15 most similar decisions teams usually chose **held, fought**; measured better: **held, advanced** (+2.0 points against the choice made, not clear yet, partly who chooses it, n 21). In the same fight-state third (behind in the fight (lowest third, +0.00 or less)) this choice did +2.0 against the usual choice (n 60 against 79, raw).

**Confidence**: medium (one measurement supports it).

## TQ 4. Pit NPCs lost

*The NPC loss that cost the most win chance in the new matches: Men lost knight (One split Fire Ele+8 Monk+Air Ele 1) at 7:10; win chance -67.0 points from 20 s before to 20 s after.*

### Pit NPCs lost: Men v One (137d4b45) around 7:10.0
**Lost**: 7:10.0 knight (One split Fire Ele+8 Monk+Air Ele 1); 7:12.0 knight (One split Fire Ele+8 Monk+Air Ele 1)
**One's split** 3:53.0 to 10:13.0: ['Fire Ele', '8 Monk', 'Air Ele 1'] (split), entered base 6:18.0, NPC damage {'footman': 2297, 'archer': 1579, 'knight': 1653}, NPC kills [{'npc': 'archer (outside)', 't': 357, 'defenders_present': ['Ranger']}, {'npc': 'knight', 't': 430, 'defenders_present': ['Ranger']}, {'npc': 'knight', 't': 432, 'defenders_present': ['Ranger']}, {'npc': 'archer (outside)', 't': 529, 'defenders_present': ['Ranger', '8 Monk']}]
- defender Ritualist: first 3:57.0 (latency -141 s, from field), 69 s defending
- defender Ranger: first 3:58.0 (latency -140 s, collapse from main), 78 s defending
- defender 8 Monk: first 3:59.0 (latency -139 s, collapse from main), 85 s defending
- defender Hammer: first 5:01.0 (latency -77 s, from field), 21 s defending
- main numbers meanwhile [3.9, 4.4]
**Men at 7:10.0**: Hammer: push side (convert); AoB Derv: push side (convert); Ranger: backside (hold); Ritualist: dead; Mesmer: push side (convert); Prot: push side (convert); 7 Monk: push side (convert); 8 Monk: dead
- One output 3:53.0 to 7:15.0: 20.0 per second
- Men output 3:53.0 to 7:15.0: 17.4 per second
**Why, in short**: One split Fire Ele+8 Monk+Air Ele 1 into Men's base at 6:18; at 6:59 the pit had 2 attackers against 1 defenders (0 of them healers), with 5 of Men elsewhere; defenders present at the kill: Ranger; 2 of Men were dead at the time (8 Monk 6:49, Ritualist 6:56); the 8 Monk died at 6:49 (own pit, numbers [5, 4]) because no prot landed in time (0 of 0 landed), knocked down 1 times with no knockdown immunity up, position (no allied healer within casting range, nearest enemy 733); the Ritualist died at 6:56 (own pit, numbers [5, 4]) because no prot landed in time (0 of 0 landed), knocked down 1 times with no knockdown immunity up, position (in contact with the enemy, nearest enemy 767).

**How it could have been prevented (measured)**

- Further back: with 2 of Men dead, more defenders were not available; the deaths are explained above, and the split's answer is priced below.
- First defender: 141 s before it entered the base; every stored split into a base: median 10 s before it entered the base, quickest fifth 37 s before it entered the base or sooner (241 splits). Denning: about 15 s is on time, 60 s is late.
- The split was answered on time, so the loss came from what the defence did once there (below), not from a late answer.
- NPC-loss node at 6:59 (AUC 0.835 on unseen matches against 0.756 for attackers and defenders alone): 2 attackers (0 healers) against 1 defenders (0 healers), 5 of Men elsewhere; read 7.9% to lose an NPC; read again with
  - one more defender: 8.3% (+0.4 points; at this loss's measured cost of -67.0 win points, about -0.3 expected; at a typical NPC loss's -1.9, -0.0)
  - one more defender, a healer: 3.3% (-4.6 points; at this loss's measured cost of -67.0 win points, about +3.1 expected; at a typical NPC loss's -1.9, +0.1)
  - two more defenders: 8.0% (+0.1 points; at this loss's measured cost of -67.0 win points, about -0.1 expected; at a typical NPC loss's -1.9, -0.0)
- The answer to the split (usual.py; this prices the whole decision, including what the main fight lost while defenders were away, which the NPC-loss node above does not):
  - split in base at 6:18 (main 5v5, flags +56 s, boost in 99, fight state -0.003): chose **collapsed** (-7.7 [-12.9, -2.8] CLEAR against the most common choice, defended without a collapse); in the 15 most similar decisions teams usually chose **defended without a collapse**; measured better: **defended without a collapse** (+7.7 points against the choice made, clear, n 86).

**Confidence**: medium (one measurement supports it).

## 9. Detailed learnings snapshot

Descriptive measurements across all 91 trained matches (the latest batch, 30 matches, in brackets where it differs). Not causal on their own: they point to questions and candidate variables.

**Runners** (spawn to capture; pushed = an enemy hit the carrier):

| Runner | Runs | Captured | Median s to capture | Dropped | Pushed | Runs by winners |
|---|---|---|---|---|---|---|
| Mes/A | 181 | 51% | 42 (41.5) | 83 | 50% | 43% |
| AoB Derv | 170 | 55% | 30.0 (22.0) | 73 | 38% | 54% |
| Ritualist | 142 | 46% | 35.0 (40.0) | 73 | 33% | 63% |
| Mesmer | 133 | 51% | 34.0 (32.0) | 61 | 37% | 53% |
| 8 Monk | 84 | 31% | 29.0 (26.0) | 57 | 20% | 55% |
| Hammer | 81 | 43% | 24 (19.5) | 45 | 28% | 52% |
| Dervish | 80 | 61% | 26 (26.0) | 30 | 44% | 53% |
| Monk 4 (WoC) | 52 | 60% | 36 (26) | 21 | 46% | 62% |
| Stand Mes | 52 | 67% | 32 (41.5) | 16 | 38% | 52% |
| Air Ele 2 | 45 | 44% | 36.0 (42.5) | 25 | 29% | 67% |

Double running: single 1120 runs (49% by winners); half 356 runs (51% by winners).

**Flag answers** (answering the enemy's capture): winners: 340 answers, median 40.5 s, 3.0 s slower than possible, 63 answers 30 s+ slower; losers: 317 answers, median 54 s, 8 s slower than possible, 111 answers 30 s+ slower.

**Skills: kill participation** (share of casts at an enemy who died within 5 s; 15+ casts):

- Highest: Deep Freeze 50% of 22; Shadow Shroud PvP 31% of 55; Decapitate 30% of 189; Signet of Rage 29% of 68; Knee Cutter 29% of 35; Word of Censure 28% of 1589; Augury of Death 27% of 110; Horns of the Ox 27% of 30; Wounding Strike PvP 27% of 63; Shatter Storm 26% of 195; Wild Throw 26% of 27; Fierce Blow 24% of 33
- Lowest: Spiteful Spirit 0% of 55; Images of Remorse 0% of 20; Ether Feast 0% of 16; Diversion 0% of 48; Flare 0% of 41; Axe Rake 0% of 19; Crippling Slash 0% of 16; Arcane Languor 0% of 20

**Interrupts:** skills interrupted most (whose): Healing Burst on the 7 Monk 264; Guardian on the Prot 185; Guardian on the 8 Monk 175; Spirit Light Weapon on the Ritualist 159; Blessed Light on the 8 Monk 144; Guardian on the 7 Monk 109; Shield Guardian PvP on the Prot 108; Cure Hex on the 7 Monk 108; Lightning Strike on the Air Ele 102; Blessed Light on the 7 Monk 84. Interrupt skills landing most: Power Spike 1191; Complicate 1143; Power Leak 544; Psychic Instability PvP 477; Savage Shot 350; Cry of Frustration 325; Hammer Bash 223; Distracting Shot 182.

**Knockdowns by skill:** Coward 1541; Hammer Bash 1393; Psychic Instability PvP 541; Lightning Surge 465; Mind Shock PvP 363; Bull's Strike 162; "Coward!" 134; Grapple 117.

**Spikes survived** (400+ damage in 3 s on one player; survived = alive 8 s later): winners 200 of 262 (76%); losers 322 of 546 (59%). By target: Prot 61% of 92; 7 Monk 61% of 88; Stand Mes 74% of 84; 8 Monk 50% of 72; AoB Derv 65% of 65; Mes/A 84% of 56; Mesmer 65% of 54; Air Ele 66% of 47; Necromancer 55% of 38; Dervish 66% of 32; Ritualist 71% of 31; Hammer 67% of 30; Water Ele 67% of 18; Paragon 59% of 17; Ranger 62% of 16; Fire Ele 64% of 14; Warrior 57% of 14.

**Monks** (per 2-minute phase alive 60 s+): winners: 11.0 casts a minute, 0.45 fakes, idle 0 s while an ally was hurt, reaction 1.5 s, bursts answered 71%; losers: 11.5 casts a minute, 0.52 fakes, idle 0.0 s while an ally was hurt, reaction 1.4 s, bursts answered 61%.

**Deaths** (1607): 513 with a knockdown on the victim; 496 had a monk cast on the victim in the last 5 s. Monk skills interrupted in the 6 s before a death: Blessed Light 71; Healing Burst 65; Guardian 43; Shield Guardian PvP 29; Reversal of Fortune 23; Cure Hex 19; Signet of Rejuvenation 13; Patient Spirit 12.

## 10. For Denning

- Which curves look wrong to you? A correction (direction, cap, drop, or a pair to always test) is logged with your reason and tested on held-out matches.
- Do any surprises remind you of something the variables don't capture (a missing variable)?
- Any variable you think matters that isn't listed?

