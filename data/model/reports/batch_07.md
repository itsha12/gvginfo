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
- glass box: all 82% (0.415), 0-5 min 81% (0.397), 5-10 min 84% (0.368), 10-15 min 78% (0.561), 15-end min 86% (0.386), matches lasting 15 min+ 79% (0.486), matches even on strength (gap under 200) 67% (0.768)
- glass box without corrections: all 83% (0.409), 0-5 min 81% (0.395), 5-10 min 84% (0.362), 10-15 min 79% (0.545), 15-end min 87% (0.382), matches lasting 15 min+ 79% (0.477), matches even on strength (gap under 200) 67% (0.755)
- black box: all 81% (0.722), 0-5 min 82% (0.679), 5-10 min 81% (0.677), 10-15 min 81% (0.723), 15-end min 78% (0.859), matches lasting 15 min+ 79% (0.817), matches even on strength (gap under 200) 64% (1.343)
- Gain over strength alone (log loss, resampling whole matches): -0.054 (90% range -0.163 to +0.041).
- Change since batch 6: glass box log loss 0.55 -> 0.415; strength only 0.418 -> 0.361.

## 2. What it leans on

- **lord_dps_enemy** 0.711 (was 0.694): enemy build's measured Lord damage per second
- **lord_dps_own** 0.706 (was 0.688): own build's measured Lord damage per second if all its non-healers were at the Lord
- **morale_diff** 0.521 (was 0.353): own minus enemy morale summed over players (boosts +, death penalty -)
- **knights_diff** 0.445 (was 0.347): own minus enemy pit knights alive
- **morale_diff & map_flag_run** 0.445 (was 0.354): own minus enemy morale summed over players (boosts +, death penalty -) TOGETHER WITH the map's flag run Y: distance from the flag spawn to the stand (average of both sides)
- **spike_build_own** 0.341 (was 0.269): own build is a spike build (1) or not (0)
- **spike_build_enemy** 0.322 (was 0.271): enemy build is a spike build
- **archers_diff & map_flag_run** 0.266 (was 0.271): own minus enemy pit archers alive TOGETHER WITH the map's flag run Y: distance from the flag spawn to the stand (average of both sides)
- **spike_killable_diff** 0.239 (was 0.451): enemy minus own players within one spike of the other side (DP stacking; 0 unless a spike build is involved)
- **lord_damage_diff & lord_dps_own** 0.236 (was 0.162): own minus enemy Lord damage dealt so far (the 28:00 tiebreak; players can't see it); blank when either team's Lord damage wasn't observed TOGETHER WITH own build's measured Lord damage per second if all its non-healers were at the Lord
- **stand** 0.233 (was 0.206): who holds the flag stand: 1 own, 0 nobody, -1 enemy
- **lord_damage_diff & lord_dps_enemy** 0.219 (was 0.193): own minus enemy Lord damage dealt so far (the 28:00 tiebreak; players can't see it); blank when either team's Lord damage wasn't observed TOGETHER WITH enemy build's measured Lord damage per second

## 3. The curves in words

Points = win-chance points added to an otherwise even game at each range of the variable.

- **lord_dps_enemy** rises from -21.1 to +14.4 points (35.8..76.0: -21.1; 78.4..83.15: +15.9; 87.85..89.8: -24.3; 97.95..102.3: +16.5; 102.95..105.45: -25.2; 106.0..111.8: +4.8; 117.1..134.25: +14.9)
- **lord_dps_own** falls from +19.1 to -14.0 points (35.8..76.0: +19.1; 78.4..83.15: -17.9; 87.85..89.8: +24.8; 97.95..102.3: -15.6; 102.95..105.45: +25.4; 106.0..111.8: -4.9; 117.1..134.25: -14.5)
- **morale_diff** rises from -22.6 to +21.1 points (-470.0..-196.0: -22.6; -144.5..-112.5: -19.1; -88.5..-46.0: -16.1; -15.5..-0.5: -1.5; 0.5..21.5: +1.7; 58.5..95.5: +17.4; 136.5..181.5: +19.5)
- **knights_diff** rises from -24.4 to +24.5 points (-2.0..-1.5: -24.4; -1.5..-0.5: -21.5; -0.5..0.5: +0.1; 0.5..1.5: +20.9; 1.5..2.0: +24.5)
- **morale_diff & map_flag_run** (interaction): see wp_model.md
- **spike_build_own** rises from -5.1 to +23.3 points (0.0..0.5: -5.1; 0.5..1.0: +23.3)
- **spike_build_enemy** falls from +4.8 to -22.2 points (0.0..0.5: +4.8; 0.5..1.0: -22.2)
- **archers_diff & map_flag_run** (interaction): see wp_model.md
- **spike_killable_diff** rises from -37.1 to +37.0 points (-8.0..-7.5: -37.1; -5.5..-4.5: -35.2; -3.5..-2.5: -33.1; -1.5..-0.5: -23.6; 0.5..1.5: +23.1; 2.5..4.5: +33.7; 5.5..7.5: +36.1)
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

- split_diff: 0.415 without, 0.424 with: does not improve yet. own minus enemy players on a split (away from their main group on the enemy half, not carrying). Proposed batch 1 by Claude: the knights curve runs backwards, maybe standing in for the cost of splitting
- turtle_diff: 0.415 without, 0.422 with: does not improve yet. own minus enemy share of live players at home (own base or pit). Proposed 2026-11-06 from OG comms ([ohno v One], [ohno v Crew]: 'they are turtling, we have to make a play'); comms_vars.py: teams that turtled 60 s won 3 of 13 times
- footmen_diff: 0.415 without, 0.439 with: does not improve yet. own minus enemy footmen alive (base NPCs, not pit NPCs). Proposed 2026-11-06 from OG comms ([ohno v NwAy]: 'this way we don't lose footmen'; [ohno v Fun]: fake collapse to the footmen)
- no_healer_groups_diff: 0.415 without, 0.416 with: does not improve yet. own minus enemy groups of 2+ with no healer. Proposed 2026-11-06 from OG comms ([ohno v One]: keep a prot and a monk on one side, the Rit and a monk on the other); comms_vars.py: such groups lose players twice as often
- solo_healers_diff: 0.415 without, 0.419 with: does not improve yet. own minus enemy healers with no other own healer within casting range. Proposed 2026-11-06 from OG comms ('solo monk, go on the monk'); Denning: a monk alone has no other monk to support it

**Surprises** (moments where the held-out model was most confident about the team that went on to lose; each points to something the variables don't capture yet):

- RACK v hdm (1f65fd3b) at 12:00: a model that never saw this match gave RACK 5.4%, and RACK won. Why it thought so: knights_diff -28.2, healing_monks_enemy -21.3, morale_diff & map_flag_run +18.3, morale_diff -17.6, team strength -14.0
- OG v hold (49eec28d) at 5:15: a model that never saw this match gave OG 0.1%, and OG won. Why it thought so: archers_diff & map_flag_run -33.1, lord_dps_enemy -33.0, morale_diff & map_flag_run -32.6, morale_diff -24.6, lord_dps_own -21.4
- cope v Team (427c825b) at 12:15: a model that never saw this match gave Team 2.1%, and Team won. Why it thought so: lord_dps_enemy -34.3, lord_dps_own -28.4, archers_diff & map_flag_run +27.8, morale_diff -19.2, knights_diff -18.6
- hdm v HC (28447c4a) at 24:45: a model that never saw this match gave HC 0.3%, and HC won. Why it thought so: morale_diff & map_bases_apart -40.5, morale_diff -34.5, knights_diff -30.1, morale_diff & lord_dps_enemy -21.2, archers_diff & map_flag_run +17.5
- Fun v hold (99d9b260) at 2:30: a model that never saw this match gave hold 2.4%, and hold won. Why it thought so: spike_killable_diff -39.6, spike_build_enemy -24.1, team strength +22.8, healing_monks_enemy -21.8, morale_diff & map_bases_apart -21.3
- Crew v BcS (3ee18c0c) at 11:00: a model that never saw this match gave BcS 0.7%, and BcS won. Why it thought so: lord_dps_enemy -27.7, lord_damage_diff & lord_dps_own -21.3, knights_diff -19.1, lord_dps_own -18.3, morale_diff -17.6

## 5. Denning's rulings seen through the model

Win chance from a model that never saw the match, 20 s before and 60 s after each ruled moment. Contributions are points for an otherwise even game (the curves' scale).

- hdm v HC (28447c4a) 5:01 (split answered), HC: 43.3% 20 s before -> 82.6% 60 s after (+39.3). After: morale_diff & map_bases_apart +39.1, knights_diff -30.1, archers_diff & map_flag_run +17.5, morale_diff +14.6
- hdm v HC (28447c4a) 5:01 (split answered), hdm: 56.8% 20 s before -> 21.1% 60 s after (-35.7). After: morale_diff & map_bases_apart -39.5, knights_diff +30.9, archers_diff & map_flag_run -17.9, morale_diff & map_flag_run +15.2
- hdm v HC (28447c4a) 1:02 (split detection), HC: 47.5% 20 s before -> 66.3% 60 s after (+18.8). After: morale_diff & map_bases_apart +39.1, lord_dps_own +13.2, morale_diff & map_flag_run -9.9, morale_diff & lord_dps_own -9.2
- hdm v HC (28447c4a) 1:02 (split detection), hdm: 51.1% 20 s before -> 32.1% 60 s after (-19.0). After: morale_diff & map_bases_apart -39.5, lord_dps_enemy -13.0, morale_diff & lord_dps_enemy +10.6, boost_clock & map_bases_apart +9.0
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), HC: 82.1% 20 s before -> 58.7% 60 s after (-23.4). After: morale_diff & map_bases_apart +39.1, knights_diff -30.1, archers_diff & map_flag_run +25.4, morale_diff +14.6
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), hdm: 20.8% 20 s before -> 41.4% 60 s after (+20.6). After: morale_diff & map_bases_apart -39.5, knights_diff +30.9, archers_diff & map_flag_run -27.8, morale_diff & map_flag_run +15.2
- hdm v HC (bbef1904) 8:10 (death), HC: 83.0% 20 s before -> 40.0% 60 s after (-43.0). After: lord_dps_enemy +22.0, alive_diff -11.4, down_diff_s -10.3, morale_diff & map_flag_run -6.9
- hdm v HC (bbef1904) 8:10 (death), hdm: 9.3% 20 s before -> 44.3% 60 s after (+35.0). After: lord_dps_own -22.7, alive_diff +11.3, down_diff_s +9.5, lord_health_diff & lord_dps_own -9.1
- Men v HC (faec428a) 9:31 (death), HC: 9.9% 20 s before -> 13.1% 60 s after (+3.2). After: knights_diff -21.8, lord_dps_own -15.3, archers_diff & map_flag_run +15.1, lord_dps_enemy -13.0
- Men v HC (faec428a) 9:31 (death), Men: 89.4% 20 s before -> 85.9% 60 s after (-3.5). After: knights_diff +21.3, archers_diff & map_flag_run -14.8, lord_dps_enemy +14.7, lord_dps_own +13.2

## 6. Why: the node models

Each explains one result from what happened before it (time order enforced), tested on matches it never saw. AUC = how often a moment that led to the result scores above one that didn't (0.5 = guessing, 1 = perfect).

**deaths** (91 matches, 179804 moments, 5519 results): adds to the simple baseline (AUC 0.918 against 0.804 for health_pct and damage_taken_3s alone).
- **enemies_near** (enemies within 1,500) rises from -22.3 to +26.6 points (0.0..0.5: -22.3; 0.5..1.5: -11.8; 1.5..2.5: +1.5; 2.5..3.5: +4.1; 3.5..4.5: +10.7; 4.5..5.5: +12.8; 5.5..6.5: +14.7; 6.5..7.5: +18.7; 7.5..8.0: +26.6)
- **strength_gap** (own minus enemy team strength) falls from +18.3 to -12.8 points (-976.0..-579.5: +18.3; -433.5..-317.5: +5.6; -188.0..-111.0: +9.3; -64.5..-6.0: +7.0; 60.5..106.0: -8.2; 159.5..317.5: -4.3; 433.5..579.5: -15.2)
- **health_pct** (current health %) falls from +40.8 to -6.1 points (1.0..46.5: +40.8; 58.5..66.5: +24.4; 72.5..77.5: +12.0; 81.5..84.5: +5.5; 87.5..90.5: +1.0; 93.5..95.5: -2.5; 97.5..99.5: -5.1)
- **local_diff** (allies minus enemies within 2,000) falls from +24.4 to -20.9 points (-8.0..-3.5: +24.4; -2.5..-1.5: +12.5; -0.5..0.5: -2.9; 1.5..2.5: -7.5; 3.5..4.5: +4.4; 5.5..7.0: -20.9)
- **allies_near** (allies within 1,500) falls from +20.0 to -7.7 points (0.0..0.5: +20.0; 0.5..1.5: +9.7; 1.5..2.5: +5.7; 2.5..3.5: -1.4; 3.5..4.5: -2.5; 4.5..5.5: -4.6; 5.5..6.5: -6.1; 6.5..7.0: -7.7)
- **minute** (match minute) rises from -2.7 to +16.1 points (0.1..1.15: -2.7; 2.05..3.05: -6.3; 4.15..5.15: -5.7; 6.25..7.55: +1.6; 8.95..10.55: -2.2; 12.45..14.55: -1.9; 17.25..20.45: +6.9)
- **own_condition_removal** (own condition removal skills) falls from -7.0 to -28.5 points (1.0..1.5: -7.0; 1.5..2.5: +6.4; 2.5..3.5: +6.8; 3.5..4.5: -0.2; 4.5..5.5: -0.7; 5.5..6.5: -9.9; 6.5..7.5: -10.8; 7.5..8.0: -28.5)
- **enemy_strips** (enemy enchantment removal skills) falls from +34.8 to -7.0 points (0.0..0.5: +34.8; 0.5..1.5: +3.8; 1.5..2.5: +1.0; 2.5..3.5: -3.6; 3.5..4.5: -4.2; 4.5..5.5: -3.9; 5.5..7.0: -7.0)
- **enemy_interrupts** (enemy interrupt skills) rises from -2.5 to +22.0 points (0.0..0.5: -2.5; 1.5..2.5: +5.9; 3.5..4.5: -1.0; 5.5..6.5: -4.4; 7.5..8.5: +2.8)
- **dist_own_pit** (distance from its own pit) rises from -3.6 to +11.9 points (10.0..1363.5: -3.6; 2248.5..3790.5: -1.4; 5071.5..6021.5: -2.7; 6894.5..7630.5: -1.3; 8319.5..8994.5: -1.9; 9878.5..10788.5: +0.8; 12027.5..13424.5: +9.5)

**kill conversion** (91 matches, 1559 moments, 479 results): adds to the simple baseline (AUC 0.759 against 0.672 for burst_damage and target_health_pct alone).
- **burst_damage** (damage in the 2 s burst) rises from -11.9 to +23.2 points (250.0..256.5: -11.9; 264.5..274.5: -10.5; 284.5..294.5: -8.8; 306.5..321.5: -2.4; 335.5..353.5: +1.5; 374.5..403.5: +5.3; 443.5..506.5: +21.7)
- **target_healers_in_range** (target's healers in range) falls from +27.2 to -7.5 points (0.0..0.5: +27.2; 0.5..1.5: -0.4; 1.5..2.5: -5.3; 2.5..3.0: -7.5)
- **target_health_pct** (target health % when the burst started) falls from +20.2 to -11.3 points (0.0..38.5: +20.2; 50.5..57.5: +9.5; 63.5..68.5: +6.3; 72.5..76.5: +4.2; 79.5..83.5: -2.0; 87.5..91.5: -6.5; 95.5..99.5: -10.9)
- **target_ceiling** (target's health ceiling) falls from +25.2 to -9.4 points (0.4..0.69: +25.2; 0.7..0.76: +12.4; 0.84..0.85: +10.2; 0.88..0.91: +6.6; 0.94..0.95: +4.1; 0.99..1.02: -3.2; 1.1..1.1: -9.4)
- **strength_gap** (attacking minus target team strength) rises from -13.1 to +14.5 points (-958.0..-561.5: -13.1; -376.0..-226.0: -11.1; -126.5..-74.0: -2.1; -8.0..51.0: +0.0; 71.5..140.5: +1.1; 256.0..353.5: +1.3; 518.5..611.0: +12.8)
- **enemy_prots** (target team's prot skills) falls from +8.7 to -4.2 points (1.0..2.5: +8.7; 3.5..4.5: +6.4; 6.5..7.5: +5.8; 8.5..9.5: +3.6; 10.5..11.5: -1.4; 12.5..13.5: -3.0; 14.5..15.5: -4.3)
- **target_prot_up** (a prot on the target) falls from +2.6 to -5.0 points (0.0..0.5: +2.6; 0.5..1.0: -5.0)
- **own_interrupts_v_enemy_heals** (attackers' interrupt skills minus target team's heals) falls from +4.4 to -5.4 points (-16.0..-15.5: +4.4; -14.5..-13.5: +4.8; -12.5..-11.5: +2.7; -10.5..-9.5: +0.6; -8.5..-7.5: -2.1; -6.5..-5.5: -5.2; -4.5..-1.0: -5.4)
- **target_hexes** (hexes on the target) rises from -1.5 to +30.3 points (0.0..0.5: -1.5; 1.5..2.5: +0.6; 3.5..4.5: +3.6; 5.5..6.5: +8.4; 7.5..8.5: +28.4)

**flag answer** (seconds an answer to an enemy capture was slower than possible; 77 matches, 653 rows): adds to the simple baseline (typical error 17.6s against 28.6s for the median; explains 70% of the spread).
- **parked_s** (seconds the flag lay parked (dropped 5 s or more: not running yet)): 0.0..2.5: -6.2 s; 9.5..14.5: +5.0 s; 19.5..28.5: +16.3 s; 35.5..41.0: +35.2 s; 50.0..65.0: +51.4 s; 87.5..106.0: +63.5 s; 135.0..291.0: +69.6 s
- **own_deaths_during** (own deaths during the answer): 0.0..0.5: -3.9 s; 0.5..1.5: +7.7 s; 1.5..2.5: +12.9 s; 2.5..3.5: +22.0 s; 3.5..4.5: +25.0 s; 4.5..5.5: +31.1 s; 5.5..8.0: +48.4 s; 8.0..17.0: +72.1 s
- **enemy_deaths_during** (enemy deaths during the answer): 0.0..0.5: -3.8 s; 0.5..1.5: +7.9 s; 1.5..2.5: +16.0 s; 2.5..3.5: +22.1 s; 3.5..4.5: +24.1 s; 4.5..7.0: +26.9 s
- **enemies_in_the_way** (enemy presence along the runner's trip back to the spawn): 0.0..0.5: -5.7 s; 5.5..11.5: -2.9 s; 16.5..20.5: -1.8 s; 26.5..37.5: -0.9 s; 51.5..66.5: +2.3 s; 88.5..110.0: +7.1 s; 144.5..217.0: +16.1 s
- **carrier_damage_taken** (damage the carrier took while carrying): 0.0..1.0: -3.4 s; 27.5..50.5: -4.0 s; 77.0..100.5: -1.9 s; 131.5..193.0: +0.5 s; 248.5..288.5: +3.7 s; 388.0..515.5: +6.1 s; 650.0..1040.0: +11.7 s
- **runner_to_spawn** (runner's distance to its flag spawn when the enemy captured): 4.0..782.0: -10.2 s; 1428.5..2252.0: -3.1 s; 3356.5..4010.5: -0.4 s; 4544.0..5243.5: +1.9 s; 5851.0..6483.5: +3.6 s; 6952.0..7508.0: +3.5 s; 8238.5..9061.0: +2.7 s
- **quick_handoffs** (quick hand-offs (a teammate picked it up within 5 s)): 0.0..0.5: -2.0 s; 0.5..1.5: +5.7 s; 1.5..2.5: +10.5 s; 2.5..3.0: +19.9 s
- **possible_s** (fastest possible answer (s) from the flag model at the enemy's capture): 0.0..4.5: -1.1 s; 9.5..17.5: +0.4 s; 23.5..29.5: +1.3 s; 33.5..37.5: +3.8 s; 41.5..46.5: +2.4 s; 50.5..55.5: -0.5 s; 62.5..69.5: -4.9 s
- **strength_gap** (own minus enemy team strength): -976.0..-527.5: +3.6 s; -376.0..-267.0: +2.3 s; -122.0..-102.5: +1.0 s; -17.5..11.0: -0.1 s; 80.5..111.0: -1.2 s; 159.5..303.5: -2.4 s; 415.5..579.5: -2.6 s
- **morale_diff** (own minus enemy morale): -219.0..-112.5: +7.0 s; -76.0..-48.0: +3.5 s; -31.0..-17.5: +2.1 s; -7.5..1.0: -0.1 s; 14.0..17.0: -1.5 s; 41.5..64.5: -3.9 s; 94.0..135.5: -3.1 s

**npc loss** (91 matches, 9098 moments, 1795 results): adds to the simple baseline (AUC 0.832 against 0.756 for attackers and defenders alone).
- **npc_damage_5s** (damage on the pit NPCs in the last 5 s) rises from -17.1 to +34.5 points (0.0..0.5: -17.1; 22.5..37.5: +1.2; 51.5..70.5: +7.0; 90.5..113.5: +11.0; 136.5..162.5: +24.1; 194.5..234.5: +27.2; 289.5..382.5: +32.6)
- **defenders** (own players in the pit) falls from +31.4 to -34.8 points (0.0..0.5: +31.4; 0.5..1.5: +18.4; 1.5..2.5: +12.0; 2.5..3.5: +3.2; 3.5..4.5: -10.5; 4.5..5.5: -11.6; 5.5..6.5: -12.7; 6.5..7.5: -26.3; 7.5..8.0: -34.8)
- **defenders_elsewhere** (own players alive outside the pit) falls from +18.5 to -4.2 points (0.0..0.5: +18.5; 0.5..1.5: +9.6; 1.5..2.5: +9.1; 2.5..3.5: +4.2; 3.5..4.5: -6.8; 4.5..5.5: -13.2; 5.5..6.5: -13.5; 6.5..7.5: -13.1; 7.5..8.0: -4.2)
- **defender_healers** (of which healers) falls from +22.7 to -8.3 points (0.0..0.5: +22.7; 0.5..1.5: -1.5; 1.5..2.5: -5.8; 2.5..3.0: -8.3)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -12.9 to +8.5 points (1.9..18.75: -12.9; 28.8..32.15: -6.2; 34.9..45.65: -4.1; 54.8..64.25: +3.3; 66.25..73.15: +5.6; 77.9..86.85: +7.9; 99.1..111.3: +9.0)
- **attackers_share** (share of the attacking team's live players in the pit (OG comms: merge before pushing the pit)) rises from -11.4 to +8.8 points (0.12..0.13: -11.4; 0.16..0.18: -5.6; 0.23..0.27: -4.1; 0.35..0.39: -2.8; 0.46..0.53: +4.5; 0.61..0.69: +7.1; 0.84..0.94: +8.9)
- **attackers** (enemy players in the pit) rises from -7.2 to +10.3 points (1.0..1.5: -7.2; 1.5..2.5: -3.8; 2.5..3.5: -2.5; 3.5..4.5: -1.0; 4.5..5.5: +5.0; 5.5..6.5: +7.4; 6.5..7.5: +9.1; 7.5..8.0: +10.3)
- **strength_gap** (attacking minus defending team strength) rises from -5.9 to +7.0 points (-976.0..-415.5: -5.9; -274.5..-106.0: -8.6; 13.0..75.5: +0.9; 106.0..226.0: +12.5; 285.5..353.5: +1.7; 415.5..437.0: +2.7; 545.0..664.0: +5.3)
- **npc_healing_10s** (healing on own pit NPCs and Lord in the last 10 s) falls from +3.3 to -16.0 points (0.0..3.0: +3.3; 42.5..68.0: +2.4; 101.5..139.5: +1.2; 174.5..212.5: -0.3; 257.5..307.5: -6.6; 362.5..428.5: -8.0; 515.5..674.5: -14.5)

**lord damage** (Lord damage dealt in the next 10 s while players are in the enemy pit; 88 matches, 10491 rows): adds to the simple baseline (typical error 128.7 against 91.2 for the median; explains 39% of the spread).
- **defenders** (own players in the pit): 0.0..0.5: +239.8; 0.5..1.5: +109.0; 1.5..2.5: +56.2; 2.5..3.5: -12.8; 3.5..4.5: -64.3; 4.5..5.5: -106.1; 5.5..6.5: -140.8; 6.5..7.5: -158.9; 7.5..8.0: -159.1
- **defenders_elsewhere** (own players alive outside the pit): 0.0..0.5: +69.1; 0.5..1.5: +82.4; 1.5..2.5: +75.0; 2.5..3.5: +66.7; 3.5..4.5: +26.2; 4.5..5.5: -12.9; 5.5..6.5: -58.5; 6.5..7.5: -119.3; 7.5..8.0: -229.0
- **bodyguard** (own Bodyguard alive): 0.0..0.5: +128.7; 0.5..1.0: -49.4
- **attackers** (enemy players in the pit): 1.0..1.5: -33.9; 1.5..2.5: -18.6; 2.5..3.5: -21.5; 3.5..4.5: -8.4; 4.5..5.5: +32.2; 5.5..6.5: +32.7; 6.5..7.5: +44.1; 7.5..8.0: +53.4
- **defender_healers** (of which healers): 0.0..0.5: +79.6; 0.5..1.5: -11.1; 1.5..2.5: -10.7; 2.5..3.0: -38.9
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)): 1.9..18.75: -42.6; 28.8..32.15: -28.3; 32.8..43.0: -30.3; 54.55..64.25: -3.6; 66.25..73.15: +19.6; 79.15..87.45: +41.9; 99.95..111.75: +39.3
- **npc_healing_10s** (healing on own pit NPCs and Lord in the last 10 s): 0.0..3.0: -16.4; 42.5..70.5: +5.4; 105.5..142.5: +18.6; 174.5..213.5: +23.3; 259.5..307.5: +25.5; 365.5..431.5: +32.0; 522.5..676.5: +42.6
- **seconds_in_pit** (seconds the attackers have been in the pit): 0.0..4.5: -26.3; 10.5..16.5: -22.1; 22.5..28.5: -4.3; 37.5..46.5: +6.6; 58.5..73.5: +21.4; 91.5..115.5: +11.8; 151.5..208.5: +19.9
- **attacker_healers** (of which healers): 0.0..0.5: +13.5; 0.5..1.5: -10.8; 1.5..2.5: +18.1; 2.5..3.0: -39.0
- **attackers_share** (share of the attacking team's live players in the pit (OG comms: merge before pushing the pit)): 0.12..0.13: -10.9; 0.16..0.18: -20.7; 0.23..0.27: -6.6; 0.35..0.39: -14.8; 0.46..0.53: -18.5; 0.61..0.69: +3.6; 0.84..0.94: +25.9

**lord kill** (88 matches, 10485 moments, 799 results): adds to the simple baseline (AUC 0.965 against 0.944 for attackers and defenders alone).
- **defenders** (own players in the pit) falls from +46.0 to -47.8 points (0.0..0.5: +46.0; 0.5..1.5: +39.6; 1.5..2.5: +22.9; 2.5..3.5: +7.1; 3.5..4.5: -26.8; 4.5..5.5: -32.4; 5.5..6.5: -40.3; 6.5..7.5: -42.6; 7.5..8.0: -47.8)
- **defenders_elsewhere** (own players alive outside the pit) falls from +39.0 to -42.7 points (0.0..0.5: +39.0; 0.5..1.5: +21.6; 1.5..2.5: +20.9; 2.5..3.5: +19.7; 3.5..4.5: +18.0; 4.5..5.5: -21.4; 5.5..6.5: -30.3; 6.5..7.5: -42.1; 7.5..8.0: -42.7)
- **minute** (match minute) rises from -45.4 to +27.9 points (0.5..2.75: -45.4; 3.75..4.85: -40.9; 5.85..6.95: +7.0; 8.15..9.55: +17.9; 11.05..12.85: +19.2; 15.05..17.65: +26.0; 20.05..23.25: +27.3)
- **attackers** (enemy players in the pit) rises from -33.8 to +31.2 points (1.0..1.5: -33.8; 1.5..2.5: -12.7; 2.5..3.5: -0.5; 3.5..4.5: +3.1; 4.5..5.5: +26.3; 5.5..6.5: +28.6; 6.5..7.5: +30.0; 7.5..8.0: +31.2)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -25.8 to +24.3 points (1.9..18.75: -25.8; 28.8..32.15: -27.9; 32.8..43.0: -10.9; 54.55..64.25: -7.3; 66.25..73.15: +6.4; 79.15..87.45: +27.2; 99.95..111.75: +27.5)
- **defender_healers** (of which healers) falls from +32.7 to -33.7 points (0.0..0.5: +32.7; 0.5..1.5: +8.7; 1.5..2.5: -4.5; 2.5..3.0: -33.7)
- **res_in** (seconds until the next res) rises from -43.9 to +2.6 points (1.0..8.5: -43.9; 17.5..26.5: +3.2; 35.5..44.5: +13.7; 53.5..62.5: +11.2; 68.5..74.5: +9.6; 80.5..86.5: +9.0; 95.5..107.5: +4.6)
- **seconds_in_pit** (seconds the attackers have been in the pit) rises from +1.5 to +28.6 points (0.0..4.5: +1.5; 10.5..16.5: -13.3; 22.5..28.5: -12.5; 37.5..46.5: -10.4; 58.5..73.5: +4.1; 91.5..115.5: +10.0; 151.5..208.5: +20.7)

## 7. The usual play

Each choice against the most common one in that kind of decision, in win-chance points over the decision's window, adjusted for the situation, with a 90% range from resampling whole matches. CLEAR = the range excludes 0. Win chance comes from a model that never saw the match. The same comparison over the 30 s BEFORE the decision is a placebo test: a choice can't cause what came before it, so a clear difference there means the effect is partly who makes that choice.

**after wipe** (208 decisions, 86 matches; usual: pushed the pit)
- reset (n 25): -3.0 [-7.9, +2.4]; in the 30 s before: -2.5 [-6.8, +2.4]
- took the flag (n 25): +0.1 [-6.4, +6.6]; in the 30 s before: +1.5 [-6.3, +10.0]

**boost clock** (333 decisions, 83 matches; usual: not running, fought)
- running, fought (n 48): +2.5 [-1.1, +5.5]; in the 30 s before: -1.1 [-2.8, +1.6]
- not running, fell back (n 46): -4.8 [-8.6, -0.6] CLEAR; in the 30 s before: +1.3 [-1.4, +4.1]
- not running, advanced (n 40): -0.4 [-4.0, +3.0]; in the 30 s before: +0.5 [-1.2, +2.5]
- running, advanced (n 39): +3.0 [-0.2, +6.2]; in the 30 s before: +2.1 [-0.9, +5.4]
- not running, held (n 19): -2.1 [-4.9, +0.4]; in the 30 s before: +0.5 [-1.8, +2.3]
- not running, to the spawn (n 17): -2.2 [-6.8, +1.3]; in the 30 s before: +1.7 [-0.4, +3.8]
- running, fell back (n 13): +0.6 [-2.8, +4.1]; in the 30 s before: +0.9 [-2.4, +4.0]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - running, fought, behind in the fight (lowest third, -0.08 or less): +0.6 (n 14 against 51)
  - running, fought, middle third: -4.7 (n 17 against 34)
  - running, fought, ahead in the fight (top third, above -0.00): +4.9 (n 17 against 26)
  - not running, fell back, behind in the fight (lowest third, -0.08 or less): -8.2 (n 18 against 51)
  - not running, fell back, middle third: -0.5 (n 17 against 34)
  - not running, fell back, ahead in the fight (top third, above -0.00): -9.7 (n 11 against 26)
  - not running, advanced, behind in the fight (lowest third, -0.08 or less): too few yet (n 7 against 51; means -0.3 against 0.0)
  - not running, advanced, middle third: -1.4 (n 13 against 34)
  - not running, advanced, ahead in the fight (top third, above -0.00): -0.4 (n 20 against 26)
  - running, advanced, behind in the fight (lowest third, -0.08 or less): too few yet (n 3 against 51; means 7.3 against 0.0)
  - running, advanced, middle third: -4.9 (n 16 against 34)
  - running, advanced, ahead in the fight (top third, above -0.00): +2.8 (n 20 against 26)
  - not running, held, behind in the fight (lowest third, -0.08 or less): too few yet (n 4 against 51; means -0.6 against 0.0)
  - not running, held, middle third: too few yet (n 9 against 34; means -1.5 against -1.1)
  - not running, held, ahead in the fight (top third, above -0.00): too few yet (n 6 against 26; means -3.1 against -1.1)
  - not running, to the spawn, behind in the fight (lowest third, -0.08 or less): -1.0 (n 10 against 51)
  - not running, to the spawn, middle third: too few yet (n 5 against 34; means -1.6 against -1.1)
  - not running, to the spawn, ahead in the fight (top third, above -0.00): too few yet (n 2 against 26; means -16.8 against -1.1)
  - running, fell back, behind in the fight (lowest third, -0.08 or less): too few yet (n 4 against 51; means 0.2 against 0.0)
  - running, fell back, middle third: too few yet (n 4 against 34; means -3.9 against -1.1)
  - running, fell back, ahead in the fight (top third, above -0.00): too few yet (n 5 against 26; means 0.8 against -1.1)

**enemy pickup** (1211 decisions, 87 matches; usual: held, fought)
- already running, fought (n 161): -1.5 [-4.7, +1.4]; in the 30 s before: +2.4 [+0.4, +4.0] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, advanced (n 153): +3.8 [-0.0, +7.8]; in the 30 s before: +1.6 [-0.5, +3.2]
- already running, advanced (n 134): -0.6 [-2.9, +2.1]; in the 30 s before: +2.9 [+0.8, +5.1] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, fell back (n 105): -4.1 [-7.6, -1.4] CLEAR; in the 30 s before: +0.3 [-2.2, +1.9]
- ran, fell back (n 79): -2.2 [-5.5, +0.8]; in the 30 s before: +0.9 [-1.8, +3.7]
- already running, fell back (n 74): -1.5 [-5.4, +2.4]; in the 30 s before: -0.7 [-4.2, +1.7]
- ran, fought (n 69): +0.0 [-2.2, +3.2]; in the 30 s before: -0.2 [-3.7, +2.8]
- ran, advanced (n 69): -0.3 [-3.4, +2.8]; in the 30 s before: +1.9 [-0.0, +3.5]
- already running, held (n 42): -0.7 [-4.7, +3.3]; in the 30 s before: +0.4 [-1.0, +1.6]
- ran, held (n 32): -0.0 [-3.2, +3.3]; in the 30 s before: +0.3 [-2.1, +2.7]
- held, held (n 26): -0.1 [-5.6, +3.7]; in the 30 s before: -1.1 [-8.1, +7.4]
- held, to the spawn (n 12): -1.4 [-8.2, +3.5]; in the 30 s before: +0.4 [-6.4, +4.7]
- ran, to the spawn (n 6): -3.1 [-15.2, +5.0]; in the 30 s before: +6.1 [-3.1, +19.4]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - already running, fought, behind in the fight (lowest third, -0.01 or less): +5.9 (n 53 against 84)
  - already running, fought, middle third: -6.5 (n 48 against 70)
  - already running, fought, ahead in the fight (top third, above +0.01): -4.0 (n 60 against 95)
  - held, advanced, behind in the fight (lowest third, -0.01 or less): +10.7 (n 24 against 84)
  - held, advanced, middle third: -2.8 (n 60 against 70)
  - held, advanced, ahead in the fight (top third, above +0.01): +2.2 (n 69 against 95)
  - already running, advanced, behind in the fight (lowest third, -0.01 or less): +7.4 (n 37 against 84)
  - already running, advanced, middle third: -6.9 (n 52 against 70)
  - already running, advanced, ahead in the fight (top third, above +0.01): -1.2 (n 45 against 95)
  - held, fell back, behind in the fight (lowest third, -0.01 or less): +3.1 (n 51 against 84)
  - held, fell back, middle third: -8.9 (n 26 against 70)
  - held, fell back, ahead in the fight (top third, above +0.01): -7.6 (n 28 against 95)
  - ran, fell back, behind in the fight (lowest third, -0.01 or less): +4.8 (n 38 against 84)
  - ran, fell back, middle third: -9.6 (n 20 against 70)
  - ran, fell back, ahead in the fight (top third, above +0.01): -3.4 (n 21 against 95)
  - already running, fell back, behind in the fight (lowest third, -0.01 or less): +6.3 (n 33 against 84)
  - already running, fell back, middle third: -4.5 (n 20 against 70)
  - already running, fell back, ahead in the fight (top third, above +0.01): -1.7 (n 21 against 95)
  - ran, fought, behind in the fight (lowest third, -0.01 or less): +7.1 (n 28 against 84)
  - ran, fought, middle third: -7.2 (n 17 against 70)
  - ran, fought, ahead in the fight (top third, above +0.01): +2.1 (n 24 against 95)
  - ran, advanced, behind in the fight (lowest third, -0.01 or less): +5.7 (n 19 against 84)
  - ran, advanced, middle third: -3.0 (n 30 against 70)
  - ran, advanced, ahead in the fight (top third, above +0.01): -2.0 (n 20 against 95)
  - already running, held, behind in the fight (lowest third, -0.01 or less): +8.6 (n 12 against 84)
  - already running, held, middle third: -7.1 (n 25 against 70)
  - already running, held, ahead in the fight (top third, above +0.01): too few yet (n 5 against 95; means -1.9 against 2.5)
  - ran, held, behind in the fight (lowest third, -0.01 or less): +15.1 (n 14 against 84)
  - ran, held, middle third: -8.7 (n 13 against 70)
  - ran, held, ahead in the fight (top third, above +0.01): too few yet (n 5 against 95; means -17.1 against 2.5)
  - held, held, behind in the fight (lowest third, -0.01 or less): too few yet (n 7 against 84; means 7.7 against -6.2)
  - held, held, middle third: -7.0 (n 13 against 70)
  - held, held, ahead in the fight (top third, above +0.01): too few yet (n 6 against 95; means -0.1 against 2.5)
  - held, to the spawn, behind in the fight (lowest third, -0.01 or less): too few yet (n 9 against 84; means -2.0 against -6.2)
  - held, to the spawn, middle third: too few yet (n 2 against 70; means -0.4 against 6.3)
  - held, to the spawn, ahead in the fight (top third, above +0.01): too few yet (n 1 against 95; means -0.3 against 2.5)
  - ran, to the spawn, behind in the fight (lowest third, -0.01 or less): too few yet (n 2 against 84; means -1.6 against -6.2)
  - ran, to the spawn, middle third: too few yet (n 1 against 70; means 0.0 against 6.3)
  - ran, to the spawn, ahead in the fight (top third, above +0.01): too few yet (n 3 against 95; means -10.3 against 2.5)

- **late_game**: not enough decisions yet (22)
**power play** (742 decisions, 91 matches; usual: pushed, advanced)
- pushed, fought (n 209): -0.3 [-1.8, +1.2]; in the 30 s before: -1.0 [-2.4, +0.1]
- held, fought (n 152): -2.5 [-4.2, -1.0] CLEAR; in the 30 s before: -1.4 [-2.6, -0.1] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, fell back (n 57): -3.4 [-5.8, -1.0] CLEAR; in the 30 s before: -3.7 [-7.4, -0.3] ALREADY DIFFERENT BEFORE: partly who chooses it
- pushed, fell back (n 36): -1.8 [-4.3, +1.1]; in the 30 s before: -2.8 [-4.9, -0.4] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, advanced (n 21): +1.3 [-1.9, +5.4]; in the 30 s before: -1.8 [-4.0, +0.1]
- pushed, held (n 5): -3.9 [-7.8, +1.3]; in the 30 s before: +5.4 [-3.7, +13.7]
- held, held (n 5): -3.9 [-7.9, -0.0] CLEAR; in the 30 s before: -8.7 [-25.3, +3.4]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - pushed, fought, behind in the fight (lowest third, +0.00 or less): +0.1 (n 63 against 80)
  - pushed, fought, middle third: +0.9 (n 61 against 75)
  - pushed, fought, ahead in the fight (top third, above +0.08): -3.2 (n 85 against 102)
  - held, fought, behind in the fight (lowest third, +0.00 or less): -1.6 (n 62 against 80)
  - held, fought, middle third: -2.6 (n 58 against 75)
  - held, fought, ahead in the fight (top third, above +0.08): -5.5 (n 32 against 102)
  - held, fell back, behind in the fight (lowest third, +0.00 or less): -5.8 (n 23 against 80)
  - held, fell back, middle third: -0.6 (n 20 against 75)
  - held, fell back, ahead in the fight (top third, above +0.08): -5.5 (n 14 against 102)
  - pushed, fell back, behind in the fight (lowest third, +0.00 or less): -0.8 (n 14 against 80)
  - pushed, fell back, middle third: +0.4 (n 14 against 75)
  - pushed, fell back, ahead in the fight (top third, above +0.08): too few yet (n 8 against 102; means -3.4 against 5.5)
  - held, advanced, behind in the fight (lowest third, +0.00 or less): too few yet (n 9 against 80; means 2.8 against 1.9)
  - held, advanced, middle third: too few yet (n 7 against 75; means 2.8 against 1.1)
  - held, advanced, ahead in the fight (top third, above +0.08): too few yet (n 5 against 102; means 9.0 against 5.5)
  - pushed, held, behind in the fight (lowest third, +0.00 or less): too few yet (n 3 against 80; means -5.3 against 1.9)
  - pushed, held, middle third: too few yet (n 1 against 75; means -1.1 against 1.1)
  - pushed, held, ahead in the fight (top third, above +0.08): too few yet (n 1 against 102; means 3.8 against 5.5)
  - held, held, behind in the fight (lowest third, +0.00 or less): too few yet (n 3 against 80; means -0.9 against 1.9)
  - held, held, middle third: too few yet (n 2 against 75; means 0.1 against 1.1)

**split in base** (180 decisions, 57 matches; usual: defended without a collapse)
- collapsed (n 80): -8.1 [-13.1, -3.2] CLEAR; in the 30 s before: -0.4 [-2.4, +2.2]
- missed (n 14): -2.6 [-14.1, +5.8]; in the 30 s before: -0.1 [-3.0, +7.7]

**Collapses on a split: time away and its cost** (`S32`; per collapse, averages; main = what the main fight lost while the collapsers were away)

| Group | Cases | Away (median s) | Split killed | Collapser died | Own deaths at main | Enemy deaths at main | Flag lead change | DP change | Win change |
|---|---|---|---|---|---|---|---|---|---|
| all | 88 | 22 | 18 | 10 | 0.59 | 0.41 | +1.2 | -3.4 | -4.4 |
| away under 30 s | 51 | 7 | 13 | 1 | 0.02 | 0.1 | -0.4 | +0.3 | -3.3 |
| away 30 to 60 s | 16 | 43 | 2 | 3 | 0.88 | 0.56 | -7 | -11.9 | +4.2 |
| away 60 s or more | 21 | 108 | 3 | 6 | 1.76 | 1.05 | +11.2 | -6.0 | -13.7 |
| before 20:00 | 80 | 23 | 14 | 8 | 0.44 | 0.41 | +2.4 | -4.5 | -4.8 |
| from 20:00 | 8 | 18 | 4 | 2 | 2.12 | 0.38 | -10.8 | +6.9 | -0.6 |
| split member killed | 18 | 13.5 | 18 | 1 | 0.06 | 1 | +0.3 | +1.2 | +1.1 |
| no kill | 70 | 25 | 0 | 9 | 0.73 | 0.26 | +1.4 | -4.6 | -5.8 |

**Leverage: where the choice matters most** (share of the spread in win-chance change explained by the choice beyond the situation; range = best minus worst choice, in points)

- boost clock (333): choice explains 5.3% (situation 5.9%); range 7.8 points, best running, fought, worst not running, fell back
- split in base (180): choice explains 3.2% (situation 9.2%); range 7.6 points, best defended without a collapse, worst collapsed
- power play (742): choice explains 1.4% (situation 3.1%); range 5.8 points, best held, advanced, worst pushed, held
- enemy pickup (1211): choice explains 1.1% (situation 3.1%); range 8.7 points, best held, advanced, worst ran, to the spawn
- after wipe (208): choice explains 0.4% (situation 15.0%); range 2.8 points, best took the flag, worst reset

**Behaviour clusters: what teams actually did** (each decision's response grouped by what every player did in the next 20 s; UNNAMED = a group no single named choice covers: a response for Denning to name or reject)

*after wipe* (2 groups, separation 0.31):
- n 126: fought (midline, 1.9 of 8), fought (backline, 1.4 of 8), fought (frontline, 0.9 of 8), held (backline, 0.9 of 8); named as {'pushed the pit': 109, 'reset': 9, 'took the flag': 8}; win change -1.3
- n 82: advanced (backline, 2.5 of 8), advanced (midline, 2.5 of 8), advanced (frontline, 1.3 of 8); named as {'pushed the pit': 49, 'took the flag': 17, 'reset': 16}; win change 2.4 UNNAMED
*boost clock* (4 groups, separation 0.2):
- n 165: fought (midline, 2.2 of 8), fought (backline, 1.4 of 8), fought (frontline, 1.0 of 8), held (backline, 0.6 of 8); named as {'not running, fought': 105, 'running, fought': 44, 'not running, to the spawn': 8}; win change -0.1
- n 81: advanced (midline, 2.3 of 8), advanced (backline, 1.8 of 8), fought (midline, 0.6 of 8), advanced (frontline, 0.5 of 8); named as {'not running, advanced': 37, 'running, advanced': 35, 'not running, fought': 4}; win change -2.1 UNNAMED
- n 76: fell back (midline, 1.9 of 8), fell back (backline, 1.5 of 8), fell back (frontline, 0.6 of 8), fought (midline, 0.5 of 8); named as {'not running, fell back': 45, 'running, fell back': 12, 'not running, to the spawn': 6}; win change -4.7 UNNAMED
- n 23: held (midline, 3.0 of 8), held (backline, 2.4 of 8), held (frontline, 0.5 of 8); named as {'not running, held': 18, 'running, held': 4, 'not running, to the spawn': 1}; win change -1.2
*enemy pickup* (4 groups, separation 0.21):
- n 450: fought (midline, 2.3 of 8), fought (backline, 1.4 of 8), fought (frontline, 1.0 of 8), held (backline, 0.8 of 8); named as {'held, fought': 208, 'already running, fought': 149, 'ran, fought': 58}; win change -1.6 UNNAMED
- n 378: advanced (midline, 2.2 of 8), advanced (backline, 1.9 of 8), advanced (frontline, 0.9 of 8), fought (backline, 0.5 of 8); named as {'held, advanced': 146, 'already running, advanced': 119, 'ran, advanced': 63}; win change 4.4 UNNAMED
- n 279: fell back (midline, 1.9 of 8), fell back (backline, 1.8 of 8), fell back (frontline, 0.7 of 8); named as {'held, fell back': 97, 'ran, fell back': 72, 'already running, fell back': 68}; win change -1.7 UNNAMED
- n 104: held (midline, 2.2 of 8), held (backline, 1.8 of 8), fought (midline, 0.6 of 8); named as {'already running, held': 39, 'ran, held': 30, 'held, held': 21}; win change 0.6 UNNAMED
*power play* (3 groups, separation 0.27):
- n 354: fought (midline, 2.4 of 8), fought (backline, 1.7 of 8), fought (frontline, 1.1 of 8), held (backline, 0.8 of 8); named as {'pushed, fought': 192, 'held, fought': 137, 'pushed, advanced': 16}; win change 1.1 UNNAMED
- n 261: advanced (midline, 2.4 of 8), advanced (backline, 2.3 of 8), advanced (frontline, 1.1 of 8); named as {'pushed, advanced': 236, 'held, advanced': 18, 'pushed, fought': 5}; win change 3.3
- n 132: fell back (backline, 1.9 of 8), fell back (midline, 1.8 of 8), fell back (frontline, 0.7 of 8), fought (midline, 0.7 of 8); named as {'held, fell back': 55, 'pushed, fell back': 36, 'held, fought': 14}; win change -0.5 UNNAMED
*split in base* (3 groups, separation 0.2):
- n 85: fought (midline, 2.3 of 8), fought (backline, 1.2 of 8), fought (frontline, 0.9 of 8), held (backline, 0.8 of 8); named as {'defended without a collapse': 46, 'collapsed': 34, 'missed': 5}; win change 0.1 UNNAMED
- n 48: advanced (midline, 2.3 of 8), advanced (backline, 1.2 of 8), advanced (frontline, 0.6 of 8), fought (midline, 0.5 of 8); named as {'defended without a collapse': 22, 'collapsed': 22, 'missed': 4}; win change -1.4 UNNAMED
- n 46: fell back (midline, 2.7 of 8), fell back (backline, 1.5 of 8), fell back (frontline, 0.8 of 8); named as {'collapsed': 24, 'defended without a collapse': 17, 'missed': 5}; win change -3.2 UNNAMED

## 8. What results and causes are worth

Win points for the team it happened to, from 91 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 281 | -0.8 | -6.4 to +4.8 | +2.9 | no |
| capture | 746 | +2.6 | +1.9 to +3.4 | +2.5 | yes |
| death (any) | 1768 | -5.1 | -7.2 to -3.2 | -3.8 | yes |
| death: against a spike build | 455 | -8.2 | -15.6 to -1.6 | -3.3 | yes |
| death: against other builds | 1313 | -4.1 | -6.5 to -1.8 | -4.0 | yes |
| death: back within 20 s | 281 | -3.1 | -7.1 to +0.6 | -1.4 | no |
| death: down 20 to 60 s | 668 | -5.1 | -7.8 to -2.4 | -2.3 | yes |
| death: down 60 s or more | 819 | -5.9 | -8.4 to -3.6 | -5.9 | yes |
| death: healer | 599 | -5.2 | -8.3 to -2.5 | -4.4 | yes |
| death: healer in own base or pit, back within 15 s (likely deliberate) | 37 | +1.2 | -2.8 to +6.7 | +1.2 | no |
| death: healer, other | 562 | -5.6 | -8.5 to -3.0 | -4.8 | yes |
| death: not a healer | 1169 | -5.1 | -8.0 to -2.8 | -3.5 | yes |
| death: team boosted (morale above zero) | 206 | -24.6 | -37.2 to -13.4 | -8.1 | yes |
| death: team not boosted | 1562 | -2.6 | -5.4 to +0.2 | -3.3 | no |
| footman lost (base NPC) | 257 | +1.3 | -2.8 to +5.1 | -0.3 | no |
| pit NPC lost (any): taken by a spike build | 142 | -2.9 | -6.9 to +1.7 | -2.3 | no |
| pit NPC lost (any): taken by other builds | 573 | -1.5 | -3.6 to +1.0 | -0.3 | no |
| pit NPC lost: archer | 410 | +0.6 | -1.9 to +3.5 | +0.3 | no |
| pit NPC lost: bodyguard | 100 | -3.6 | -6.6 to -0.8 | +0.2 | yes |
| pit NPC lost: knight | 205 | -5.5 | -8.1 to -3.2 | -3.2 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value.

*deaths* (per 10 s in that state; result worth -5.1 points, base rate 1.5%):

- enemies within 1,500 7.5 to 8: result chance +3.2 points, worth -0.17 win points
- own minus enemy team strength -976 to -579.5: result chance +1.7 points, worth -0.09 win points
- current health % 1 to 46.5: result chance +11.6 points, worth -0.59 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.7 points, worth -0.14 win points
- allies within 1,500 0 to 0.5: result chance +1.9 points, worth -0.1 win points
- match minute 20.45 to 28: result chance +1.4 points, worth -0.07 win points
- own condition removal skills 7.5 to 8: result chance -1.1 points, worth +0.06 win points
- enemy enchantment removal skills 0 to 0.5: result chance +6.3 points, worth -0.32 win points

*kill conversion* (per burst, for the attacking team; result worth +5.1 points, base rate 30.7%):

- damage in the 2 s burst 506.5 to 839: result chance +24.1 points, worth +1.23 win points
- target's healers in range 0 to 0.5: result chance +29.3 points, worth +1.49 win points
- target health % when the burst started 0 to 38.5: result chance +20.4 points, worth +1.04 win points
- target's health ceiling 0.4 to 0.69: result chance +26.6 points, worth +1.36 win points
- attacking minus target team strength 611 to 976: result chance +13.9 points, worth +0.71 win points
- target team's prot skills 1 to 2.5: result chance +7.9 points, worth +0.4 win points
- a prot on the target 0.5 to 1: result chance -4.1 points, worth -0.21 win points
- attackers' interrupt skills minus target team's heals -5.5 to -4.5: result chance -4.6 points, worth -0.23 win points

*npc loss* (per case, for the defending team; result worth -1.7 points, base rate 19.7%):

- damage on the pit NPCs in the last 5 s 382.5 to 1170: result chance +37.5 points, worth -0.65 win points
- own players in the pit 7.5 to 8: result chance -15.5 points, worth +0.27 win points
- own players alive outside the pit 0 to 0.5: result chance +15.1 points, worth -0.26 win points
- of which healers 0 to 0.5: result chance +19.8 points, worth -0.34 win points
- attackers' measured damage per second against a Lord (benchmarks) 1.9 to 18.75: result chance -7.1 points, worth +0.12 win points
- share of the attacking team's live players in the pit (OG comms: merge before pushing the pit) 0.12 to 0.13: result chance -6.3 points, worth +0.11 win points
- enemy players in the pit 7.5 to 8: result chance +7.5 points, worth -0.13 win points

## The TQs

Denning's four questions, each from the batch's matches. The why comes from forensics and events (every number placed against the same role or situation in every stored match); the different play comes only from measurement: the usual play's choice effects (usual.py), node models read again with the variable changed (models that never saw the match, changes priced in win points with values.py), options that were ready and unused, and benchmarks. Points = win-chance points.

## TQ 1. Behind on flags

*The biggest flag swing in the new matches: Team +129 -> -55 by 3:40.0.*

### Flag swing: Team v Men (0f3c18b0), 2:10.0 to 3:40.0
**Result**: Team's flag lead +129 s -> -55 s (-184 s). Stand: None -> Team.
**Captures** (flag model: fastest possible answer after the enemy's capture):
**Runs** (each run: outcome, and what was done to the runner):
- Team Ritualist 2:12.0 to 2:34.0 (21 s): captured, lowest health 100%, escort none, pushed by nobody
**Deaths in the window**: 2:07.0 Men Mes/A (backside, [6, 8]); 2:09.0 Men 8 Monk (backside, [5, 7]); 2:16.0 Men Stand Mes 1 (dead, [3, 7]); 2:59.0 Men Prot (own pit, [2, 7]); 3:28.0 Men Stand Mes 2 (own pit, [1, 7]); 3:40.0 Men Hammer (stand, [1, 8])
- Team output in the 20 s before 3:40.0: 8.9 damage per second (below the 10th percentile for team (median 37.1, n 3825)), top target share 1.0, spikes 0
- Men output in the 20 s before 3:40.0: 1.4 damage per second (below the 10th percentile for team (median 37.1, n 3825)), top target share 1.0, spikes 0
**Why, in short**: deaths in the window: Men 6.

**A different play (measured)**

*The decisions in the swing* (usual.py: win-chance points over the decision's window, against the kind's most common choice):
- power play at 2:02 (main 8v6, flags -8 s, boost in None, fight state 0.355): chose **pushed, advanced** (+0.0 [+0.0, +0.0] against the most common choice, pushed, advanced); in the 15 most similar decisions teams usually chose **pushed, fought**; no choice of this kind did measurably better than the one made.
- after wipe at 2:16 (main 7v3, flags +129 s, boost in None, fight state 0.156): chose **pushed the pit** (+0.0 [+0.0, +0.0] against the most common choice, pushed the pit); in the 15 most similar decisions teams usually chose **pushed the pit**; no choice of this kind did measurably better than the one made.
- enemy pickup at 3:27 (main 7v1, flags +69 s, boost in 68, fight state 0.803): chose **held, fought** (+0.0 [+0.0, +0.0] against the most common choice, held, fought); in the 15 most similar decisions teams usually chose **held, advanced**; measured better: **held, advanced** (+3.8 points against the choice made, not clear yet, n 153).

**Confidence**: low (measured, but the ranges include no effect yet).

## TQ 2. A monk death

*The monk death that cost the most win chance in the new matches: cope v Team (427c825b), cope Prot at 14:08 (backside, numbers [4, 8]); win chance -93.0 points from 10 s before to 30 s after.*

**Why** (forensics, against the same role in every stored match):
- Position: partly (nearest allied healer 340 in the last 5 s, nearest enemy 172, allies in casting range 4, enemies 8)
- Prots: partly the wrong kind (0 from teammates, 1 self; 1 of 1 landed); damage 391 (0% attacks, 23% armor-ignoring), burst 323 in 2 s at 14:04.2; ready and in range but not used: cope 7 Monk Guardian, cope 8 Monk Guardian
- Healers under interrupt pressure: usual (healers 3, interrupts_per_min 3.0, interrupted 1, casts 21, finished_share 0.95, dazed 0, knockdowns 0, hexes 6)
- Damage off shield sets: usual (team share 0.31, a shield would have stopped about 204)
- Own damage: no (14.0 per second on [('Team Dervish', 105), ('Team Air Ele 3', 100)]); enemy damage: high (151.8 per second)
- Peel: no (peel on a burst is rare: most bursts on this role get none) (0 of 4 attackers controlled; longest free 20.0 s)
- Casting: usual (casts 8, interrupted 0, cancelled 0, while_dazed 0)
**Why, in short**: the Prot died because the enemy hit unusually hard (151.8 per second), its own team's damage was low (14.0 per second), position (in contact with the enemy, nearest enemy 172), its attackers were not peeled (no (peel on a burst is rare: most bursts on this role get none)).

**How it could have been prevented (measured)**

- Ready and in range but not used: cope 7 Monk Guardian (casting Healing Burst on cope 7 Monk); cope 8 Monk Guardian (casting Reversal of Fortune on cope 7 Monk)
- Attackers left free (no snare, Blind, Weakness, interrupt, knockdown or hex from its team): Team Mesmer 20.0 s free (nearest own non-healer 4840); Team Air Ele 2 20.0 s free (nearest own non-healer 5911); Team Air Ele 1 20.0 s free (nearest own non-healer 4758)
- Deaths node at 14:05 (AUC 0.918 on unseen matches against 0.804 for health_pct and damage_taken_3s alone): risk 7.5% of dying in the next 10 s; read again with
  - staying with its group: 6.8% (-0.7 points of risk; at this death's measured cost of -93.0 win points, about +0.7 expected; at a typical healer death's -5.2, +0.0)
  - its hexes removed: 6.4% (-1.1 points of risk; at this death's measured cost of -93.0 win points, about +1.0 expected; at a typical healer death's -5.2, +0.1)
  - all of these together: 5.7% (-1.8 points of risk; at this death's measured cost of -93.0 win points, about +1.7 expected; at a typical healer death's -5.2, +0.1)
- The decision before it (usual.py):
  - boost clock at 13:38 (main 4v8, flags +27 s, boost in 30, fight state -0.012): chose **running, advanced** (+3.0 [-0.2, +6.2] against the most common choice, not running, fought); in the 15 most similar decisions teams usually chose **not running, fell back**; no choice of this kind did measurably better than the one made. In the same fight-state third (middle third) this choice did -4.9 against the usual choice (n 16 against 34, raw).

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
**Why, in short**: hook had 8v4 at main for 71 s but dealt 74.3 damage per second (above the 90th percentile for team (median 37.1, n 3825)); damage uptime 1% (most damage-seconds lost to moving); spread over 4 targets (top share 0.37); cope healed 97 per second.

**How it could have been converted (measured)**

- Against every stored power play (3+ more at main): those that killed had a median 36.6 damage per second and top-target share 0.39 (49 cases); those that didn't, 21.1 and 0.53 (38 cases). hook here: 74.3 and 0.37. Damage uptime: 40% in those that killed, 35% in those that didn't, 1% here.
- Kill-conversion node (AUC 0.759 on unseen matches against 0.672 for burst_damage and target_health_pct alone): the biggest burst, 299 on the cope Prot at 0:36 with 3 attackers, read 4.3% to kill within 8 s; read again with
  - on the cope Mes/A instead: 24.8% (+20.5 points, about +1.0 win points at a converted burst's +5.1)
  - on the cope Stand Mes instead: 11.4% (+7.1 points, about +0.4 win points at a converted burst's +5.1)
  - the target Dazed: 9.0% (+4.7 points, about +0.2 win points at a converted burst's +5.1)
  - on the cope 8 Monk instead: 6.3% (+2.0 points, about +0.1 win points at a converted burst's +5.1)
  - all 5 damage dealers in the burst: 5.1% (+0.8 points, about +0.0 win points at a converted burst's +5.1)
  - on the cope Hammer instead: 5.0% (+0.7 points, about +0.0 win points at a converted burst's +5.1)
- Bursts in the window: 2, on Prot (299), Prot (258)
- The choice at the power play (usual.py):
  - power play at 0:11 (main 8v4, flags +1 s, boost in None, fight state 0.0): chose **pushed, fought** (-0.3 [-1.8, +1.2] against the most common choice, pushed, advanced); in the 15 most similar decisions teams usually chose **held, fought**; no choice of this kind did measurably better than the one made. In the same fight-state third (behind in the fight (lowest third, +0.00 or less)) this choice did +0.1 against the usual choice (n 63 against 80, raw).

**Confidence**: medium (one measurement supports it).

## TQ 4. Pit NPCs lost

*The NPC loss that cost the most win chance in the new matches: cope lost bodyguard (converted from the fight at 13:30 (wipe)) at 14:27; win chance -92.3 points from 20 s before to 20 s after.*

### Pit NPCs lost: cope v Team (427c825b) around 14:27.0
**Lost**: 14:27.0 bodyguard (converted from the fight at 13:30 (wipe)); 14:36.0 knight (converted from the fight at 13:30 (wipe))
**cope at 14:27.0**: AoB Derv: own pit (hold); Hammer: backside (free); Mes/A: own pit (hold); Stand Mes 1: own pit (hold); Stand Mes 2: dead; Prot: dead; 7 Monk: dead; 8 Monk: dead
- Team output 13:57.0 to 14:27.0: 67.3 per second
- cope output 13:57.0 to 14:27.0: 5.8 per second
**Why, in short**: at 14:23 the pit had 8 attackers against 2 defenders (0 of them healers), with 2 of cope elsewhere.

**How it could have been prevented (measured)**

- NPC-loss node at 14:23 (AUC 0.832 on unseen matches against 0.756 for attackers and defenders alone): 8 attackers (2 healers) against 2 defenders (0 healers), 2 of cope elsewhere; read 70.9% to lose an NPC; read again with
  - one more defender: 60.6% (-10.3 points; at this loss's measured cost of -92.3 win points, about +9.5 expected; at a typical NPC loss's -1.7, +0.2)
  - one more defender, a healer: 40.7% (-30.2 points; at this loss's measured cost of -92.3 win points, about +27.9 expected; at a typical NPC loss's -1.7, +0.5)
  - two more defenders: 55.1% (-15.8 points; at this loss's measured cost of -92.3 win points, about +14.6 expected; at a typical NPC loss's -1.7, +0.3)
  - healing on the NPCs (as much as the attackers' damage in 5 s): 70.9% (+0.0 points; at this loss's measured cost of -92.3 win points, about -0.0 expected; at a typical NPC loss's -1.7, -0.0)

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

