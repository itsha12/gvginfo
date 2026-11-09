# Learning report, batch 13

Trained on 266 matches (45 new in this batch). Variables in use: 32; build variables from 60 matches, interactions from 40.

## 0. Data integrity

- Lengths repaired: 9 (1f65fd3b 150 s -> 1027 s) (bbef1904 617 s -> 599 s) (36a65ac6 1319 s -> 1294 s) (ba85aafc 811 s -> 793 s) (f9d6932f 235 s -> 218 s) (82fa12be 488 s -> 467 s) (cf2968cd 178 s -> 363 s) (713d9cd0 376 s -> 353 s) (366b75bc 667 s -> 650 s) 
- Matches with a team's Lord damage not observed (left blank, not zero): 19
- Pit NPCs added from the standard roster (never seen in the replay): 907 in 228 matches
- Left out of training: 0

## 1. The honest test

**Beats strength alone (not yet clear: the range includes 0).** Held-out accuracy (matches held out whole), log loss in brackets (lower is better):

- strength only: all 77% (0.455), 0-5 min 82% (0.361), 5-10 min 80% (0.405), 10-15 min 74% (0.508), 15-end min 66% (0.622), matches lasting 15 min+ 70% (0.578), matches even on strength (gap under 200) 56% (0.642)
- glass box: all 83% (0.384), 0-5 min 85% (0.331), 5-10 min 84% (0.366), 10-15 min 80% (0.465), 15-end min 81% (0.426), matches lasting 15 min+ 78% (0.478), matches even on strength (gap under 200) 73% (0.594)
- glass box without corrections: all 82% (0.427), 0-5 min 84% (0.368), 5-10 min 83% (0.415), 10-15 min 78% (0.514), 15-end min 80% (0.468), matches lasting 15 min+ 77% (0.519), matches even on strength (gap under 200) 73% (0.635)
- black box: all 82% (0.64), 0-5 min 85% (0.522), 5-10 min 84% (0.567), 10-15 min 79% (0.735), 15-end min 77% (0.838), matches lasting 15 min+ 76% (0.849), matches even on strength (gap under 200) 71% (0.947)
- Gain over strength alone (log loss, resampling whole matches): +0.071 (90% range -0.001 to +0.134).
- Change since batch 12: glass box log loss 0.344 -> 0.384; strength only 0.421 -> 0.455.
- Cap test on spike_killable_diff (held-out log loss, 266 matches): none 0.3881, 10 points 0.3969, 15 points 0.395, 20 points 0.3934, 25 points 0.3918; chosen: no cap (no option beat it on unseen matches).
- Pair test (morale_diff with map_flag_run, map_pit_to_stand, map_bases_apart; morale_total with map_flag_run, map_pit_to_stand, map_bases_apart; held-out log loss, 266 matches): allowed 0.3881, blocked 0.3841; chosen: blocked (it predicts unseen matches better).
- Calibration by minute (held-out predictions on 266 matches; pooled cells joined by straight lines, blended by minute; every win chance below and in values, usual play and the TQs goes through it). Predicted -> how often those teams won -> calibrated:
  - 0 to 6 min: 0.6% -> won 0.5% (161 matches) -> 0.5%; 3.3% -> won 5.1% (150 matches) -> 5.0%; 42.7% -> won 47.5% (89 matches) -> 47.2%; 57.4% -> won 53.6% (91 matches) -> 53.8%; 92.7% -> won 90.8% (154 matches) -> 90.8%; 99.4% -> won 99.4% (162 matches) -> 99.4%
  - 6 to 12 min: 0.6% -> won 1.4% (152 matches) -> 1.4%; 3.2% -> won 10.8% (102 matches) -> 10.4%; 42.8% -> won 50.3% (56 matches) -> 45.5%; 56.7% -> won 47.5% (52 matches) -> 53.1%; 92.8% -> won 78.5% (93 matches) -> 79.2%; 99.5% -> won 98.2% (151 matches) -> 98.2%
  - 12 to 18 min: 0.7% -> won 3.9% (86 matches) -> 3.7%; 3.3% -> won 10.8% (60 matches) -> 10.2%; 42.7% -> won 40.6% (35 matches) -> 47.0%; 57.7% -> won 53.3% (33 matches) -> 53.9%; 92.6% -> won 82.5% (55 matches) -> 83.3%; 99.3% -> won 96.4% (85 matches) -> 96.6%
  - 18 to end min: 0.6% -> won 7.2% (67 matches) -> 6.8%; 3.4% -> won 7.1% (56 matches) -> 9.5%; 42.9% -> won 38.7% (30 matches) -> 39.3%; 57.6% -> won 57.8% (29 matches) -> 57.8%; 92.8% -> won 87.0% (47 matches) -> 87.6%; 99.4% -> won 92.8% (65 matches) -> 93.7%

## 2. What it leans on

- **morale_diff** 0.62 (was 0.524): own minus enemy morale summed over players (boosts +, death penalty -)
- **knights_diff** 0.413 (was 0.473): own minus enemy pit knights alive
- **knights_diff & lord_dps_own** 0.237 (was 0.338): own minus enemy pit knights alive TOGETHER WITH own build's measured Lord damage per second if all its non-healers were at the Lord
- **knights_diff & lord_dps_enemy** 0.236 (was 0.345): own minus enemy pit knights alive TOGETHER WITH enemy build's measured Lord damage per second
- **spike_killable_diff** 0.213 (was 0.083): enemy minus own players within one spike of the other side (DP stacking; 0 unless a spike build is involved)
- **stand** 0.21 (was 0.182): who holds the flag stand: 1 own, 0 nobody, -1 enemy
- **alive_diff** 0.181 (was 0.22): own minus enemy players alive
- **lord_dps_enemy** 0.172 (was 0.161): enemy build's measured Lord damage per second
- **lord_dps_own** 0.171 (was 0.161): own build's measured Lord damage per second if all its non-healers were at the Lord
- **split_diff** 0.149 (was 0.112): own minus enemy players on a split (away from their main group on the enemy half, not carrying). Proposed batch 1 by Claude (the knights curve ran backwards, maybe standing in for the cost of splitting); moved in batch 10 on Denning's approval (held-out log loss 0.314 to 0.307)
- **map_flag_run & split_diff** 0.148 (was 0.139): the map's flag run Y: distance from the flag spawn to the stand (average of both sides) TOGETHER WITH own minus enemy players on a split (away from their main group on the enemy half, not carrying). Proposed batch 1 by Claude (the knights curve ran backwards, maybe standing in for the cost of splitting); moved in batch 10 on Denning's approval (held-out log loss 0.314 to 0.307)
- **knights_diff & map_flag_run** 0.145 (was 0.119): own minus enemy pit knights alive TOGETHER WITH the map's flag run Y: distance from the flag spawn to the stand (average of both sides)

## 3. The curves in words

Points = win-chance points added to an otherwise even game at each range of the variable.

- **morale_diff** rises from -29.4 to +27.1 points (-483.0..-200.5: -29.4; -154.5..-110.5: -24.0; -80.5..-45.5: -15.2; -15.5..-0.5: -2.7; 0.5..15.5: +3.1; 48.5..90.5: +17.6; 134.5..187.5: +25.1)
- **knights_diff** rises from -24.3 to +24.4 points (-2.0..-1.5: -24.3; -1.5..-0.5: -18.2; -0.5..0.5: +0.0; 0.5..1.5: +18.1; 1.5..2.0: +24.4)
- **knights_diff & lord_dps_own** (interaction): see wp_model.md
- **knights_diff & lord_dps_enemy** (interaction): see wp_model.md
- **spike_killable_diff** rises from -32.3 to +32.0 points (-8.0..-7.5: -32.3; -5.5..-3.5: -26.5; -2.5..-1.5: -19.9; -0.5..0.5: +0.1; 1.5..2.5: +18.7; 3.5..5.5: +26.2; 7.5..8.0: +32.0)
- **stand** rises from -5.8 to +5.8 points (-1.0..-0.5: -5.8; -0.5..0.5: -0.1; 0.5..1.0: +5.8)
- **alive_diff** rises from -29.1 to +20.0 points (-8.0..-6.5: -29.1; -4.5..-3.5: -15.7; -2.5..-1.5: -11.1; -0.5..0.5: -0.1; 1.5..2.5: +12.5; 3.5..4.5: +17.1)
- **lord_dps_enemy** is flat from -5.0 to -4.4 points (56.3..77.6: -5.0; 82.65..84.05: +0.9; 86.55..90.1: -4.1; 94.7..96.2: +5.0; 96.8..96.95: +5.0; 100.75..106.35: +3.3; 112.4..126.75: -5.0)
- **lord_dps_own** is flat from +5.0 to +3.7 points (56.3..77.6: +5.0; 82.65..84.05: -0.8; 86.55..90.1: +4.3; 94.7..96.2: -5.0; 96.8..96.95: -5.0; 100.75..106.35: -3.0; 112.4..126.75: +5.0)
- **split_diff** falls from +19.5 to -20.4 points (-5.0..-3.5: +19.5; -3.5..-2.5: +6.5; -2.5..-1.5: +5.8; -1.5..-0.5: +5.6; -0.5..0.5: +0.1; 0.5..1.5: -5.6; 1.5..2.5: -5.9; 2.5..3.5: -6.5; 3.5..5.0: -20.4)

## 4. Discovery

**Interaction candidates** (a screen: pairs whose combination seems to matter beyond each alone; untested until held-out matches confirm them; switched on in the model from 40 matches):

- morale_diff with spike_killable_diff (screen 0.150)
- minute with morale_diff (screen 0.139)
- alive_diff with morale_diff (screen 0.138)
- stand with morale_diff (screen 0.136)
- boost_clock with morale_diff (screen 0.136)
- morale_diff with spike_build_own (screen 0.135)
- morale_diff with spike_build_enemy (screen 0.135)
- morale_diff with knights_diff (screen 0.135)

**Candidate variables** (proposed variables, tested on unseen matches; log loss, lower is better):

- turtle_diff: 0.384 without, 0.385 with: does not improve yet. own minus enemy share of live players at home (own base or pit). Proposed 2026-11-06 from OG comms ([ohno v One], [ohno v Crew]: 'they are turtling, we have to make a play'); comms_vars.py: teams that turtled 60 s won 3 of 13 times
- footmen_diff: 0.384 without, 0.371 with: improves: ready to move into the model. own minus enemy footmen alive (base NPCs, not pit NPCs). Proposed 2026-11-06 from OG comms ([ohno v NwAy]: 'this way we don't lose footmen'; [ohno v Fun]: fake collapse to the footmen)
- no_healer_groups_diff: 0.384 without, 0.383 with: does not improve yet. own minus enemy groups of 2+ with no healer. Proposed 2026-11-06 from OG comms ([ohno v One]: keep a prot and a monk on one side, the Rit and a monk on the other); comms_vars.py: such groups lose players twice as often
- solo_healers_diff: 0.384 without, 0.384 with: does not improve yet. own minus enemy healers with no other own healer within casting range. Proposed 2026-11-06 from OG comms ('solo monk, go on the monk'); Denning: a monk alone has no other monk to support it

**Surprises** (moments where the held-out model was most confident about the team that went on to lose; each points to something the variables don't capture yet):

- hdm v HC (28447c4a) at 24:15: a model that never saw this match gave HC 6.8%, and HC won. Why it thought so: morale_diff -28.3, knights_diff -27.7, lord_damage_diff & minute -17.8, down_diff_s +9.3, knights_diff & lord_dps_enemy -9.2
- DMG v Free (d9e8531e) at 6:30: a model that never saw this match gave Free 1.4%, and Free won. Why it thought so: team strength -46.3, spike_killable_diff +35.7, knights_diff & spike_build_own -28.7, knights_diff -27.0, knights_diff & map_flag_run -10.1
- hold v Fun (7cb3ef17) at 13:15: a model that never saw this match gave hold 5.5%, and hold won. Why it thought so: team strength +30.3, morale_diff -27.9, knights_diff & map_pit_to_stand -23.0, knights_diff -18.6, alive_diff -14.2
- RACK v hdm (1f65fd3b) at 4:00: a model that never saw this match gave RACK 3.0%, and RACK won. Why it thought so: knights_diff -23.2, team strength -14.0, alive_diff -13.8, flag_lead & map_bases_apart -12.7, flag_lead -6.8
- Crew v BcS (3ee18c0c) at 11:00: a model that never saw this match gave BcS 37.3%, and BcS won. Why it thought so: map_flag_run & split_diff +19.4, knights_diff -14.7, morale_diff -13.5, knights_diff & map_flag_run +11.6, fight_state -11.1
- Team v Crew (1af4f8f8) at 24:00: a model that never saw this match gave Crew 9.2%, and Crew won. Why it thought so: morale_diff -22.5, team strength -19.2, knights_diff -17.7, knights_diff & lord_dps_own -11.5, flag_lead -8.5

## 5. Denning's rulings seen through the model

Win chance from a model that never saw the match, 20 s before and 60 s after each ruled moment. Contributions are points for an otherwise even game (the curves' scale).

- hdm v HC (28447c4a) 5:01 (split answered), HC: 38.9% 20 s before -> 38.1% 60 s after (-0.8). After: knights_diff -27.7, morale_diff +15.1, knights_diff & lord_dps_enemy -9.2, split_diff +7.0
- hdm v HC (28447c4a) 5:01 (split answered), hdm: 59.0% 20 s before -> 62.5% 60 s after (+3.5). After: knights_diff +28.1, morale_diff -13.9, knights_diff & lord_dps_own +9.0, split_diff -7.2
- hdm v HC (28447c4a) 1:02 (split detection), HC: 48.2% 20 s before -> 35.6% 60 s after (-12.6). After: stand -6.6, flag_lead -6.4, team strength -5.4, flag_lead & map_bases_apart -5.4
- hdm v HC (28447c4a) 1:02 (split detection), hdm: 52.7% 20 s before -> 62.9% 60 s after (+10.2). After: flag_lead +6.6, stand +6.6, team strength +5.4, lord_dps_own -5.0
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), HC: 21.7% 20 s before -> 20.8% 60 s after (-0.9). After: knights_diff -27.7, morale_diff +15.1, knights_diff & lord_dps_enemy -9.2, lord_exposed_diff -7.6
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), hdm: 80.3% 20 s before -> 85.3% 60 s after (+5.0). After: knights_diff +28.1, morale_diff -13.9, lord_damage_diff & minute +12.7, knights_diff & lord_dps_own +9.0
- hdm v HC (bbef1904) 8:10 (death), HC: 57.7% 20 s before -> 27.2% 60 s after (-30.5). After: morale_diff -14.7, alive_diff -11.2, down_diff_s -10.7, fight_state -9.2
- hdm v HC (bbef1904) 8:10 (death), hdm: 41.6% 20 s before -> 75.3% 60 s after (+33.7). After: morale_diff +17.4, alive_diff +12.0, down_diff_s +9.9, fight_state +8.3
- Men v HC (faec428a) 9:31 (death), HC: 37.8% 20 s before -> 32.4% 60 s after (-5.4). After: knights_diff -17.7, knights_diff & lord_dps_enemy -7.0, stand -6.6, lord_dps_own -5.0
- Men v HC (faec428a) 9:31 (death), Men: 63.1% 20 s before -> 68.5% 60 s after (+5.4). After: knights_diff +18.4, knights_diff & lord_dps_own +6.9, stand +6.6, lord_dps_own +5.0

## 6. Why: the node models

Each explains one result from what happened before it (time order enforced), tested on matches it never saw. AUC = how often a moment that led to the result scores above one that didn't (0.5 = guessing, 1 = perfect).

**deaths** (266 matches, 568275 moments, 16449 results): adds to the simple baseline (AUC 0.925 against 0.79 for health_pct and damage_taken_3s alone).
- **enemies_near** (enemies within 1,500) rises from -24.0 to +25.2 points (0.0..0.5: -24.0; 0.5..1.5: -13.7; 1.5..2.5: -2.2; 2.5..3.5: +4.4; 3.5..4.5: +7.7; 4.5..5.5: +9.8; 5.5..6.5: +13.1; 6.5..7.5: +16.5; 7.5..8.0: +25.2)
- **strength_gap** (own minus enemy team strength) falls from +15.8 to -16.2 points (-1183.0..-582.5: +15.8; -454.5..-375.0: +8.6; -282.5..-159.5: +10.4; -81.5..-4.5: +2.7; 61.5..140.0: -1.2; 251.5..364.5: -6.2; 446.5..582.5: -14.9)
- **health_pct** (current health %) falls from +40.7 to -5.5 points (1.0..48.5: +40.7; 60.5..68.5: +18.8; 74.5..78.5: +7.9; 82.5..85.5: +2.5; 88.5..91.5: +0.1; 93.5..95.5: -2.4; 97.5..99.5: -4.5)
- **allies_near** (allies within 1,500) falls from +21.3 to -8.7 points (0.0..0.5: +21.3; 0.5..1.5: +11.2; 1.5..2.5: +4.7; 2.5..3.5: +0.3; 3.5..4.5: -1.5; 4.5..5.5: -4.5; 5.5..6.5: -6.3; 6.5..7.0: -8.7)
- **local_diff** (allies minus enemies within 2,000) falls from +24.1 to -14.9 points (-8.0..-3.5: +24.1; -2.5..-1.5: +12.8; -0.5..0.5: -5.5; 1.5..2.5: -7.4; 3.5..4.5: +4.9; 5.5..7.0: -14.9)
- **dist_own_pit** (distance from its own pit) rises from -1.5 to +9.2 points (6.0..1398.5: -1.5; 2438.5..4185.5: -3.0; 5359.5..6279.5: -3.3; 6939.5..7475.5: -2.2; 8071.5..8674.5: -2.6; 9486.5..10523.5: +1.7; 11769.5..13289.5: +6.9)
- **enemy_interrupts** (enemy interrupt skills) rises from -1.8 to +4.4 points (0.0..0.5: -1.8; 1.5..2.5: +4.2; 3.5..4.5: +1.2; 5.5..6.5: -2.2; 7.5..8.5: +1.8)
- **prot_up** (a prot (Guardian, Spirit Bond, Life Sheath, Protective Spirit...) on the player now) falls from +1.9 to -7.5 points (0.0..0.5: +1.9; 0.5..1.0: -7.5)
- **health_ceiling** (maximum health after death penalty, as a share of normal) falls from +15.7 to -4.2 points (0.4..0.69: +15.7; 0.71..0.84: +11.0; 0.85..0.88: +6.5; 0.94..0.95: +2.8; 0.99..1.06: -0.7)

**kill conversion** (259 matches, 5013 moments, 1427 results): adds to the simple baseline (AUC 0.813 against 0.683 for burst_damage and target_health_pct alone).
- **target_healers_in_range** (target's healers in range) falls from +30.3 to -1.4 points (0.0..0.5: +30.3; 0.5..1.5: +6.1; 1.5..2.5: -5.4; 2.5..3.5: -8.2; 3.5..4.0: -1.4)
- **target_ceiling** (target's health ceiling) falls from +35.3 to -11.7 points (0.4..0.56: +35.3; 0.69..0.7: +24.6; 0.73..0.84: +21.8; 0.85..0.88: +10.6; 0.94..0.95: +5.9; 0.99..1.0: -5.2; 1.1..1.1: -11.7)
- **burst_damage** (damage in the 2 s burst) rises from -11.7 to +24.3 points (250.0..257.5: -11.7; 266.5..277.5: -11.1; 287.5..299.5: -7.1; 312.5..327.5: -4.9; 343.5..361.5: -0.5; 383.5..410.5: +8.1; 446.5..505.5: +17.8)
- **target_health_pct** (target health % when the burst started) falls from +28.7 to -10.9 points (0.0..38.5: +28.7; 49.5..56.5: +10.6; 61.5..67.5: +5.2; 72.5..76.5: +0.7; 80.5..84.5: -1.8; 87.5..91.5: -6.0; 95.5..99.5: -9.3)
- **strength_gap** (attacking minus target team strength) rises from -10.0 to +16.1 points (-1183.0..-565.5: -10.0; -384.5..-295.5: -10.8; -154.0..-69.0: -2.8; -4.5..81.5: -0.9; 147.0..230.5: +1.1; 313.0..399.5: +9.1; 536.5..639.0: +12.4)
- **target_prot_up** (a prot on the target) falls from +4.9 to -8.7 points (0.0..0.5: +4.9; 0.5..1.0: -8.7)
- **enemy_prots** (target team's prot skills) falls from +9.2 to -5.4 points (1.0..5.5: +9.2; 7.5..8.5: +5.5; 9.5..10.5: +3.4; 11.5..12.5: -1.1; 13.5..14.5: -2.7; 15.5..16.5: -4.8; 17.5..19.0: -5.4)
- **attackers** (attackers in the burst) falls from -1.7 to -6.3 points (3.0..3.5: -1.7; 3.5..4.5: +2.0; 4.5..5.5: +3.9; 5.5..6.5: -4.7; 6.5..7.0: -6.3)
- **attackers_interrupted** (interrupts on the attackers (5 s before to 2 s after)) falls from +1.0 to -15.0 points (0.0..0.5: +1.0; 0.5..1.5: -6.8; 1.5..2.5: -13.9; 2.5..4.0: -15.0)

**flag answer** (seconds an answer to an enemy capture was slower than possible; 229 matches, 2189 rows): adds to the simple baseline (typical error 15.6s against 27.7s for the median; explains 73% of the spread).
- **parked_s** (seconds the flag lay parked (dropped 5 s or more: not running yet)): 0.0..2.5: -5.2 s; 7.5..11.5: +3.6 s; 15.5..21.5: +16.4 s; 29.5..38.5: +32.1 s; 47.0..68.0: +52.4 s; 90.5..111.5: +68.6 s; 164.0..275.0: +71.0 s
- **own_deaths_during** (own deaths during the answer): 0.0..0.5: -3.3 s; 0.5..1.5: +6.4 s; 1.5..2.5: +14.5 s; 2.5..3.5: +19.6 s; 3.5..4.5: +28.3 s; 4.5..5.5: +36.8 s; 5.5..6.5: +50.1 s; 6.5..8.5: +57.3 s; 8.5..17.0: +48.1 s
- **enemy_deaths_during** (enemy deaths during the answer): 0.0..0.5: -3.2 s; 0.5..1.5: +7.7 s; 1.5..2.5: +16.3 s; 2.5..3.5: +19.2 s; 3.5..4.5: +19.1 s; 4.5..5.5: +18.9 s; 5.5..12.0: +41.9 s
- **enemies_in_the_way** (enemy presence along the runner's trip back to the spawn): 0.0..0.5: -4.6 s; 4.5..10.5: -3.6 s; 16.5..21.5: -2.8 s; 28.5..38.5: -1.1 s; 48.5..60.5: +2.0 s; 80.5..106.5: +6.1 s; 139.5..213.0: +12.6 s
- **carrier_damage_taken** (damage the carrier took while carrying): 0.0..0.5: -4.2 s; 30.5..58.5: -3.2 s; 88.5..120.5: -2.5 s; 173.5..239.5: -1.2 s; 287.5..363.5: +0.9 s; 458.5..590.5: +6.0 s; 795.5..1178.5: +15.2 s
- **possible_s** (fastest possible answer (s) from the flag model at the enemy's capture): 0.0..3.5: -8.6 s; 8.5..13.5: -5.2 s; 18.5..22.5: -1.4 s; 27.5..30.5: +2.6 s; 33.5..36.5: +4.5 s; 39.5..42.5: +4.4 s; 46.5..51.5: +5.1 s
- **runner_to_spawn** (runner's distance to its flag spawn when the enemy captured): 17.0..770.0: -6.4 s; 1442.0..2033.0: -3.1 s; 2840.0..3615.0: -0.7 s; 4214.5..4536.5: +0.9 s; 4928.5..5552.0: +1.0 s; 6174.5..6709.5: +2.2 s; 7319.0..8319.0: +2.6 s
- **flag_lead_at_enemy_cap** (own flag lead when the enemy captured): -80.0..-57.5: -1.8 s; -48.5..-40.5: +1.6 s; -33.5..-26.5: +3.1 s; -20.5..-14.5: +2.3 s; -7.5..-1.5: +0.9 s; 4.5..15.5: -2.4 s; 26.5..41.5: -3.7 s
- **morale_diff** (own minus enemy morale): -303.0..-110.5: +6.8 s; -74.5..-48.5: +4.6 s; -30.5..-15.5: +2.5 s; -2.5..3.5: -0.1 s; 15.5..30.5: -0.8 s; 48.5..72.5: -2.7 s; 95.5..140.5: -6.7 s
- **quick_handoffs** (quick hand-offs (a teammate picked it up within 5 s)): 0.0..0.5: -1.3 s; 0.5..1.5: +4.2 s; 1.5..2.5: +7.3 s; 2.5..3.0: +19.9 s

**npc loss** (264 matches, 27063 moments, 5485 results): adds to the simple baseline (AUC 0.85 against 0.757 for attackers and defenders alone).
- **defenders** (own players in the pit) falls from +34.4 to -33.7 points (0.0..0.5: +34.4; 0.5..1.5: +18.6; 1.5..2.5: +11.4; 2.5..3.5: +3.6; 3.5..4.5: -11.3; 4.5..5.5: -15.6; 5.5..6.5: -17.2; 6.5..7.5: -29.5; 7.5..8.0: -33.7)
- **npc_damage_5s** (damage on the pit NPCs in the last 5 s) rises from -17.1 to +34.5 points (0.0..0.5: -17.1; 21.5..36.5: +4.1; 50.5..69.5: +8.5; 87.5..109.5: +17.6; 134.5..160.5: +23.7; 193.5..234.5: +27.5; 292.5..385.5: +32.7)
- **defenders_elsewhere** (own players alive outside the pit) falls from +22.0 to -13.0 points (0.0..0.5: +22.0; 0.5..1.5: +16.8; 1.5..2.5: +10.0; 2.5..3.5: +0.6; 3.5..4.5: -9.2; 4.5..5.5: -12.4; 5.5..6.5: -13.7; 6.5..7.5: -15.8; 7.5..8.0: -13.0)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -23.1 to +13.8 points (2.7..17.95: -23.1; 24.65..27.15: -9.1; 34.4..42.4: -8.7; 50.85..56.55: -1.1; 64.45..72.25: +6.3; 79.85..89.85: +11.2; 99.05..105.45: +15.2)
- **defender_healers** (of which healers) falls from +21.1 to +0.9 points (0.0..0.5: +21.1; 0.5..1.5: -0.9; 1.5..2.5: -6.1; 2.5..3.5: -7.9; 3.5..4.0: +0.9)
- **attackers** (enemy players in the pit) rises from -6.7 to +7.9 points (1.0..1.5: -6.7; 1.5..2.5: -2.2; 2.5..3.5: -1.1; 3.5..4.5: +1.2; 4.5..5.5: +2.5; 5.5..6.5: +4.4; 6.5..7.5: +6.0; 7.5..8.0: +7.9)
- **strength_gap** (attacking minus defending team strength) rises from -5.9 to +7.2 points (-1108.0..-479.5: -5.9; -340.0..-181.0: -11.4; -46.5..18.0: +0.4; 101.0..185.5: +1.2; 295.0..352.0: +2.4; 416.5..486.5: +3.5; 568.5..692.5: +5.1)
- **npc_healing_10s** (healing on own pit NPCs and Lord in the last 10 s) falls from +2.5 to -10.8 points (0.0..1.5: +2.5; 41.5..49.5: +1.5; 85.5..124.5: +0.7; 155.5..187.5: -3.5; 220.5..264.5: -5.1; 315.5..378.5: -6.4; 465.5..610.5: -10.4)
- **minute** (match minute) rises from +2.8 to +5.3 points (0.2..2.55: +2.8; 3.65..4.85: +3.1; 5.95..7.25: +1.3; 8.65..10.05: -0.2; 11.75..13.75: -3.4; 15.95..18.65: -2.9; 21.65..24.75: -2.3)

**lord damage** (Lord damage dealt in the next 10 s while players are in the enemy pit; 255 matches, 30614 rows): adds to the simple baseline (typical error 75.3 against 96.6 for the median; explains 40% of the spread).
  ('chance of any' curves: points of the chance of any Lord damage in the window; 'amount' curves: % more Lord damage when there is some.)
- **defenders (chance of any)** (own players in the pit): 0.0..0.5: +35.5 points; 0.5..1.5: +28.0 points; 1.5..2.5: +19.9 points; 2.5..3.5: +0.6 points; 3.5..4.5: -10.9 points; 4.5..5.5: -27.2 points; 5.5..6.5: -30.7 points; 6.5..7.5: -36.8 points; 7.5..8.0: -42.0 points
- **bodyguard (chance of any)** (own Bodyguard alive): 0.0..0.5: +25.6 points; 0.5..1.0: -10.0 points
- **minute (chance of any)** (match minute): 0.5..2.75: -23.2 points; 3.85..5.15: -12.3 points; 6.35..7.65: -8.3 points; 9.15..10.65: -5.3 points; 12.25..14.25: -0.8 points; 16.55..19.35: +3.5 points; 22.05..24.95: +15.9 points
- **npc_healing_10s (chance of any)** (healing on own pit NPCs and Lord in the last 10 s): 0.0..1.5: -9.2 points; 42.5..67.5: +11.3 points; 100.5..138.5: +13.1 points; 158.5..199.5: +14.6 points; 236.5..281.5: +16.0 points; 329.5..391.5: +17.5 points; 474.5..621.5: +18.4 points
- **knights (chance of any)** (own knights alive): 0.0..0.5: +11.4 points; 0.5..1.5: -8.9 points; 1.5..2.0: -11.5 points
- **attackers_lord_dps (chance of any)** (attackers' measured damage per second against a Lord (benchmarks)): 2.7..21.9: -27.0 points; 24.8..28.65: -7.2 points; 36.25..44.25: +3.8 points; 52.25..58.25: +0.3 points; 65.45..73.55: +2.0 points; 81.25..90.15: +10.8 points; 99.95..105.95: +11.7 points
- **attackers_share (chance of any)** (share of the attacking team's live players in the pit (OG comms: merge before pushing the pit)): 0.12..0.13: -11.1 points; 0.16..0.23: -10.5 points; 0.27..0.35: -8.5 points; 0.42..0.53: +0.1 points; 0.61..0.65: +5.9 points; 0.73..0.84: +13.4 points; 0.94..1.0: +14.4 points
- **attacker_healers (chance of any)** (of which healers): 0.0..0.5: -6.6 points; 0.5..1.5: +1.7 points; 1.5..2.5: +6.9 points; 2.5..3.5: +7.7 points; 3.5..4.0: +42.5 points
- **attackers (chance of any)** (enemy players in the pit): 1.0..1.5: -6.4 points; 1.5..2.5: -4.1 points; 2.5..3.5: -3.1 points; 3.5..4.5: +1.8 points; 4.5..5.5: +3.4 points; 5.5..6.5: +4.5 points; 6.5..7.5: +5.3 points; 7.5..8.0: +11.2 points
- **defender_healers (chance of any)** (of which healers): 0.0..0.5: +12.0 points; 0.5..1.5: +0.8 points; 1.5..2.5: -1.0 points; 2.5..3.5: -9.6 points; 3.5..4.0: -15.8 points

**lord kill** (255 matches, 30587 moments, 2171 results): adds to the simple baseline (AUC 0.975 against 0.938 for attackers and defenders alone).
- **defenders** (own players in the pit) falls from +42.8 to -47.8 points (0.0..0.5: +42.8; 0.5..1.5: +36.8; 1.5..2.5: +21.5; 2.5..3.5: +2.6; 3.5..4.5: -20.4; 4.5..5.5: -28.5; 5.5..6.5: -37.8; 6.5..7.5: -40.4; 7.5..8.0: -47.8)
- **minute** (match minute) rises from -49.6 to +19.9 points (0.5..2.75: -49.6; 3.85..5.15: -21.2; 6.35..7.65: +15.2; 9.15..10.65: +17.2; 12.25..14.25: +20.7; 16.55..19.35: +21.1; 22.05..24.95: +22.9)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -26.1 to +25.3 points (2.7..21.9: -26.1; 24.8..28.65: -38.6; 36.25..44.25: -9.0; 52.25..58.25: -5.0; 65.45..73.55: +9.1; 81.25..90.15: +25.4; 99.95..105.75: +29.6)
- **defenders_elsewhere** (own players alive outside the pit) falls from +29.7 to -22.8 points (0.0..0.5: +29.7; 0.5..1.5: +22.9; 1.5..2.5: +17.2; 2.5..3.5: +10.2; 3.5..4.5: -5.2; 4.5..5.5: -21.1; 5.5..6.5: -23.1; 6.5..7.5: -24.2; 7.5..8.0: -22.8)
- **defender_healers** (of which healers) falls from +29.7 to -31.8 points (0.0..0.5: +29.7; 0.5..1.5: +7.6; 1.5..2.5: -6.3; 2.5..3.5: -26.9; 3.5..4.0: -31.8)
- **res_in** (seconds until the next res) rises from -43.2 to -1.5 points (1.0..8.5: -43.2; 17.5..26.5: +1.8; 35.5..44.5: +11.4; 50.5..56.5: +12.6; 62.5..68.5: +11.5; 74.5..83.5: +9.9; 95.5..107.5: +7.2)
- **lord_health** (the Lord's rebuilt health as a share of its max (lord.py)) falls from +48.0 to -5.8 points (0.0..0.19: +48.0; 0.43..0.61: +36.4; 0.71..0.78: +30.5; 0.83..0.87: +18.9; 0.91..0.94: +14.6; 0.96..0.98: +5.7; 0.99..1.0: -1.7)
- **attackers** (enemy players in the pit) rises from -11.6 to +16.1 points (1.0..1.5: -11.6; 1.5..2.5: -7.9; 2.5..3.5: -2.6; 3.5..4.5: +2.5; 4.5..5.5: +6.8; 5.5..6.5: +9.0; 6.5..7.5: +11.0; 7.5..8.0: +16.1)


## 6b. The learned nodes (step 2 of the learned causal map)

Each node uses only the causal-map links into it. A link's strength is how much worse the node predicts matches it never saw without that link's features (refit without them, same folds); supported when the gain is more than twice its spread across folds, rejected when dropping it helps by more than that, otherwise not clear yet.

**run outcome** (map R.3; 265 matches, 8816 cases, result rate 66%): log loss 0.5436 against 0.6411 for the simple baseline (adds to the simple baseline).
- link K.13 -> R.3: gain +0.0295 (+/- 0.0026), supported (min_capture_s, runner_escapes)
- link S.scoreboard -> R.3: gain +0.0127 (+/- 0.0024), supported (morale_diff, boost_clock)
- link C.map -> R.3: gain +0.0031 (+/- 0.0012), supported (run_dist)
- link C.builds -> R.3: gain +0.0011 (+/- 0.0009), not clear yet (enemy_snares)
- link P.10 -> R.3: gain +0.0006 (+/- 0.0013), not clear yet (stand_own, stand_enemy, enemy_boost_in, flag_lead...)
- link K.11 -> R.3: gain +0.0004 (+/- 0.0009), not clear yet (crippled_so_far, knocked_down_so_far, other_control_so_far, damage_so_far...)
- link C.strength -> R.3: gain -0.0003 (+/- 0.0013), not clear yet (strength_gap)
- link A.allocation -> R.3: gain -0.002 (+/- 0.0018), not clear yet (escort, own_main, enemy_main, enemy_power_play)
  - leans on **min_capture_s** (seconds the carrier needs at least to reach the stand from here, at its fastest expected carry speed (its speed skills; Denning)): +29.3 points at 0.0 to 3.65, -26.5 at 31.05 to 46.4
  - leans on **boost_clock** (boost clock (discovery, approved)): +7.7 points at -120.0 to -112.5, -19.6 at 101.5 to 120.0
  - leans on **run_dist** (distance from the team's spawn to the stand): +10.8 points at 4170.0 to 4417.0, +4.1 at 9242.0 to 9335.0

**flag swing** (map R.3; 266 matches, 10306 cases, average 0.2 s): mean absolute error (s) 26.7421 against 28.1451 for the simple baseline (adds to the simple baseline).
- link P.10 -> R.3: gain +0.73 (+/- 0.12), supported (waiting_runner, backup_flag, stand_own, stand_enemy...)
- link S.scoreboard -> R.3: gain +0.54 (+/- 0.13), supported (flag_lead, morale_diff)
- link C.strength -> R.3: gain +0.06 (+/- 0.06), not clear yet (strength_gap)
- link R.1 -> R.3: gain -0.0 (+/- 0.01), not clear yet (own_deaths_30s, enemy_deaths_30s)
- link C.clock -> R.3: gain -0.01 (+/- 0.01), not clear yet (minute, res_in)
- link C.map -> R.3: gain -0.01 (+/- 0.01), not clear yet (run_dist)
- link A.allocation -> R.3: gain -0.02 (+/- 0.02), not clear yet (own_alive, enemy_alive, own_main, enemy_main...)
  - leans on **flag_lead** (flag lead now (s)): +14.1 s at -124.0 to -62.5, -15.0 at 61.5 to 109.0
  - leans on **morale_diff** (morale, own minus enemy (discovery, approved)): -13.0 s at -445.0 to -170.5, +12.4 at 184.5 to 430.0
  - leans on **strength_gap** (team strength gap): -5.1 s at -1183.0 to -576.0, +5.9 at 587.5 to 1183.0

**run defence** (map R.3; 265 matches, 8816 cases, result rate 66%): log loss 0.5386 against 0.6411 for the simple baseline (adds to the simple baseline).
- link S.scoreboard -> R.3: gain +0.038 (+/- 0.0047), supported (boost_clock, stand, flag_lead, morale_diff...)
- link K.13 -> R.3: gain +0.0298 (+/- 0.0033), supported (min_capture_s)
- link C.map -> R.3: gain +0.0031 (+/- 0.001), supported (run_dist)
- link P.10 -> R.3: gain +0.0007 (+/- 0.001), not clear yet (runner_class)
- link C.builds -> R.3: gain +0.0007 (+/- 0.0009), not clear yet (own_snares)
- link K.11 -> R.3: gain +0.0004 (+/- 0.0004), not clear yet (def_snare_near)
- link C.strength -> R.3: gain +0.0001 (+/- 0.0011), not clear yet (strength_gap)
- link A.mesa_free -> R.3: gain -0.0008 (+/- 0.0007), not clear yet (def_free, pushers_so_far, control_so_far, damage_so_far)
- link A.allocation -> R.3: gain -0.0009 (+/- 0.0017), not clear yet (escort, att_main, def_main)
  - leans on **min_capture_s** (seconds the carrier needs at least to reach the stand from here (its speed skills)): +30.3 points at 0.0 to 3.65, -26.9 at 31.05 to 46.4
  - leans on **run_dist** (distance from the runner's spawn to the stand): +10.6 points at 4170.0 to 4417.0, +4.6 at 9242.0 to 9335.0
  - leans on **stand** (stand (discovery, approved)): -7.4 points at -1.0 to -0.5, +4.6 at 0.5 to 1.0

**capture speed** (map R.3; 253 matches, 2255 cases, average 39.5 s): mean absolute error (s) 13.4438 against 15.8967 for the simple baseline (adds to the simple baseline).
- link K.13 -> R.3: gain +2.13 (+/- 0.15), supported (min_capture_s)
- link C.map -> R.3: gain +0.33 (+/- 0.09), supported (run_dist)
- link P.10 -> R.3: gain +0.31 (+/- 0.06), supported (runner_class)
- link A.allocation -> R.3: gain +0.3 (+/- 0.17), not clear yet (defenders_free, escort)
- link C.strength -> R.3: gain +0.01 (+/- 0.02), not clear yet (strength_gap)
- link K.11 -> R.3: gain -0.04 (+/- 0.03), not clear yet (pushers_10s, control_10s, damage_10s, def_snare_near)
  - leans on **min_capture_s** (seconds the carrier needed at least, at its fastest expected carry speed (its speed skills)): -14.1 s at 0.9 to 9.55, +15.0 at 35.85 to 45.4
  - leans on **escort** (the runner's escorts): -3.6 s at 0.0 to 0.5, +9.9 at 6.5 to 7.0
  - leans on **run_dist** (distance from the runner's spawn to the stand): +4.8 s at 4170.0 to 4309.5, -5.3 at 9238.5 to 9335.0

**power play** (map K.4; 265 matches, 2503 cases, result rate 38%): log loss 0.3714 against 0.6656 for the simple baseline (adds to the simple baseline).
- link A.allocation -> K.4: gain +0.0483 (+/- 0.0069), supported (size, own_main, enemy_main, short_dead...)
- link K.2 -> K.4: gain +0.0281 (+/- 0.0081), supported (dps_v_usual)
- link C.strength -> K.4: gain +0.0109 (+/- 0.0027), supported (strength_gap)
- link K.5 -> K.4: gain +0.0098 (+/- 0.0038), supported (enemy_prots_10s, enemy_heal_s)
- link S.scoreboard -> K.4: gain +0.0083 (+/- 0.0019), supported (down_diff_s, carrying_diff)
- link P.1 -> K.4: gain +0.0081 (+/- 0.0012), supported (spikes_on_healers, healer_damage_share)
- link P.2 -> K.4: gain +0.0057 (+/- 0.0026), supported (spikes_10s, spike_spread)
- link P.14 -> K.4: gain +0.0016 (+/- 0.0012), not clear yet (pushed)
- link K.11 -> K.4: gain +0.0002 (+/- 0.0009), not clear yet (blind_secs_on_own_10s)
- link R.3 -> K.4: gain +0.0001 (+/- 0.0006), not clear yet (flag_lead)
  - leans on **short_dead** (share of the enemy's missing player-seconds: dead): -18.2 points at 0.0 to 0.01, +17.3 at 0.99 to 1.0
  - leans on **dps_v_usual** (own damage per second against the usual of the players alive): -38.3 points at 0.03 to 0.54, +26.1 at 3.1 to 12.16
  - leans on **window_s** (seconds the power play lasted): -11.8 points at 14.0 to 30.5, +31.4 at 96.5 to 351.0

**fight outcome** (map R.2; 265 matches, 2009 cases, result rate 46%): log loss 0.2421 against 0.6907 for the simple baseline (adds to the simple baseline).
- link S.scoreboard -> R.2: gain +0.1002 (+/- 0.0089), supported (morale_diff, fight_state, down_diff_s, alive_diff...)
- link P.2 -> R.2: gain +0.0263 (+/- 0.0035), supported (spike_spread_diff, spikes_diff)
- link K.1 -> R.2: gain +0.0191 (+/- 0.0076), supported (dps_v_usual_diff)
- link A.allocation -> R.2: gain +0.0181 (+/- 0.0032), supported (own_local, enemy_local)
- link P.17 -> R.2: gain +0.0132 (+/- 0.0052), supported (ready_interrupt_diff, dazed_casts_diff, blind_attacks_diff)
- link C.strength -> R.2: gain +0.0028 (+/- 0.0011), supported (strength_gap)
- link P.1 -> R.2: gain +0.0003 (+/- 0.0009), not clear yet (healer_focus_diff)
- link P.13 -> R.2: gain -0.0009 (+/- 0.001), not clear yet (peel_defensive_diff)
- link P.19 -> R.2: gain -0.0012 (+/- 0.0018), not clear yet (blind_front_secs_diff, blind_defensive_secs_diff)
- link P.5 -> R.2: gain -0.0014 (+/- 0.003), not clear yet (hex_secs_diff, hex_right_diff)
- link P.18 -> R.2: gain -0.0033 (+/- 0.0019), not clear yet (strip_right_diff, strip_value_diff)
  - leans on **morale_diff** (morale, own minus enemy (discovery, approved)): -18.4 points at -411.0 to -210.5, +41.1 at 213.5 to 410.0
  - leans on **dps_v_usual_diff** (damage against the usual of the players alive, own minus enemy): -28.1 points at -14.73 to -1.98, +26.8 at 1.86 to 12.38
  - leans on **own_local** (own players in the fight): -40.5 points at 0.0 to 0.5, +21.6 at 7.5 to 8.0

**split chance** (map A.allocation; 266 matches, 20099 cases, result rate 13%): log loss 0.3479 against 0.3903 for the simple baseline (adds to the simple baseline).
- link S.scoreboard -> A.allocation: gain +0.029 (+/- 0.0018), supported (flag_lead, own_alive, enemy_alive, own_main...)
- link C.builds -> A.allocation: gain +0.0028 (+/- 0.0029), not clear yet (own_speed_power, own_escapes, own_snare_power, enemy_snare_power)
- link C.clock -> A.allocation: gain +0.0026 (+/- 0.0005), supported (minute, res_in)
- link C.strength -> A.allocation: gain -0.0008 (+/- 0.0004), rejected (strength_gap)
  - leans on **own_main** (own main): +29.8 points at 0.0 to 2.5, -18.7 at 7.5 to 8.0
  - leans on **split_diff** (players splitting, own minus enemy (discovery, approved)): -14.5 points at -5.0 to -4.5, -2.8 at 1.5 to 5.0
  - leans on **turtle_diff** (turtling, own minus enemy (discovery, approved)): +4.5 points at -1.0 to -0.94, -30.7 at 0.94 to 1.0

**split answer** (map P.11; 189 matches, 743 cases, average -4.6 s): mean absolute error (s) 16.4548 against 18.3513 for the simple baseline (adds to the simple baseline).
- link A.allocation -> P.11: gain +0.89 (+/- 0.19), supported (size)
- link A.mesa_free -> P.11: gain +0.37 (+/- 0.22), not clear yet (def_free, nearest_to_base)
- link S.scoreboard -> P.11: gain +0.27 (+/- 0.21), not clear yet (flag_lead, def_alive, att_main, split_diff)
- link C.clock -> P.11: gain -0.11 (+/- 0.18), not clear yet (minute)
- link C.strength -> P.11: gain -0.11 (+/- 0.14), not clear yet (strength_gap)
  - leans on **size** (split size): +15.7 s at 1.0 to 1.5, -10.7 at 5.5 to 7.0
  - leans on **nearest_to_base** (nearest defender to its base at the split's entry): +6.3 s at 17.0 to 394.5, +10.8 at 7038.0 to 13999.0
  - leans on **split_diff** (players splitting, own minus enemy (discovery, approved)): -3.6 s at -6.0 to -5.5, +10.0 at 2.5 to 4.0

**split effect** (map R.5; 189 matches, 743 cases, result rate 40%): log loss 0.6431 against 0.6733 for the simple baseline (adds to the simple baseline).
- link S.scoreboard -> R.5: gain +0.0278 (+/- 0.005), supported (def_npc_value, def_free, morale_diff, flag_lead...)
- link P.11 -> R.5: gain +0.0035 (+/- 0.002), not clear yet (latency, defenders)
- link C.builds -> R.5: gain +0.0033 (+/- 0.0017), not clear yet (enemy_prots)
- link K.8 -> R.5: gain -0.0003 (+/- 0.0006), not clear yet (split_healers)
- link A.allocation -> R.5: gain -0.001 (+/- 0.0018), not clear yet (size, main_diff)
- link K.13 -> R.5: gain -0.0011 (+/- 0.0007), not clear yet (split_speed_power)
- link K.11 -> R.5: gain -0.0024 (+/- 0.0024), not clear yet (def_snare_present)
- link C.strength -> R.5: gain -0.003 (+/- 0.0014), rejected (strength_gap)
  - leans on **enemy_prots** (prot skills on the defenders' bars (discovery, approved)): +5.8 points at 0.0 to 9.5, -7.6 at 14.5 to 19.0
  - leans on **flag_lead** (flag lead (discovery, approved)): -8.2 points at -79.0 to -53.5, +5.5 at 54.0 to 80.0
  - leans on **def_npc_value** (defenders' pit NPC value when the split entered the base): -13.1 points at 0.0 to 0.75, +2.0 at 11.25 to 13.5

**pit npc loss** (map R.5; 264 matches, 27063 cases, result rate 20%): log loss 0.3594 against 0.5042 for the simple baseline (adds to the simple baseline).
- link P.11 -> R.5: gain +0.049 (+/- 0.0041), supported (defenders, defender_healers, defenders_elsewhere)
- link K.1 -> R.5: gain +0.036 (+/- 0.0017), supported (npc_damage_5s)
- link C.builds -> R.5: gain +0.0023 (+/- 0.0012), not clear yet (attackers_lord_dps, attackers_area_damage)
- link C.strength -> R.5: gain +0.0014 (+/- 0.0011), not clear yet (strength_gap)
- link K.6 -> R.5: gain +0.0011 (+/- 0.0006), not clear yet (npc_healing_10s)
- link C.clock -> R.5: gain -0.0002 (+/- 0.0009), not clear yet (seconds_in_pit, res_in, minute)
- link S.scoreboard -> R.5: gain -0.0004 (+/- 0.0006), not clear yet (knights, archers, bodyguard, full_pit_targets)
- link A.allocation -> R.5: gain -0.0007 (+/- 0.0004), not clear yet (attackers, attacker_healers, attackers_share)
  - leans on **defenders** (own players in the pit): +33.9 points at 0.0 to 0.5, -33.1 at 7.5 to 8.0
  - leans on **npc_damage_5s** (damage on the pit NPCs in the last 5 s): -16.9 points at 0.0 to 0.5, +34.3 at 385.5 to 1370.0
  - leans on **defenders_elsewhere** (own players alive outside the pit): +21.0 points at 0.0 to 0.5, -11.9 at 7.5 to 8.0

**collapse** (map R.1; 242 matches, 1687 cases, result rate 13%): log loss 0.3032 against 0.3835 for the simple baseline (adds to the simple baseline).
- link K.9 -> R.1: gain +0.0093 (+/- 0.0015), supported (split_dp)
- link K.1 -> R.1: gain +0.0085 (+/- 0.0023), supported (def_dps)
- link C.strength -> R.1: gain +0.0057 (+/- 0.0024), supported (strength_gap)
- link K.11 -> R.1: gain +0.0038 (+/- 0.0014), supported (def_snare_present)
- link P.20 -> R.1: gain +0.0034 (+/- 0.0032), not clear yet (depth_at_arrival, depth_median)
  - alone: depth_at_arrival (nearest split member's distance to the defending pit when the first defender arrived): gain +0.002 (+/- 0.0024), not clear yet
  - alone: depth_median (nearest split member's median distance to the defending pit over the split): gain +0.0016 (+/- 0.0015), not clear yet
- link A.allocation -> R.1: gain +0.0017 (+/- 0.0031), not clear yet (size, main_diff)
- link K.5 -> R.1: gain +0.0003 (+/- 0.0007), not clear yet (split_healers, split_self_defence)
- link P.11 -> R.1: gain -0.0001 (+/- 0.0016), not clear yet (latency)
- link S.scoreboard -> R.1: gain -0.0002 (+/- 0.001), not clear yet (def_npc_value)
- link P.9 -> R.1: gain -0.0007 (+/- 0.0014), not clear yet (defenders_10s, contact_diff, npc_hit_to_arrival, res_in_at_arrival)
  - alone: defenders_10s (defenders arriving within 10 s of the first (arrival spread)): gain -0.0003 (+/- 0.0008), not clear yet
  - alone: contact_diff (defenders arriving within 5 s of the first, minus the split's size (numbers at contact)): gain -0.0001 (+/- 0.0007), not clear yet
  - alone: npc_hit_to_arrival (seconds from the split's first hit on an NPC to the first defender's arrival): gain +0.0014 (+/- 0.0007), supported
  - alone: res_in_at_arrival (seconds to the next res when the first defender arrived): gain +0.0007 (+/- 0.0008), not clear yet
- link C.builds -> R.1: gain -0.0008 (+/- 0.0013), not clear yet (split_npc_dps)
- link K.13 -> R.1: gain -0.0009 (+/- 0.0019), not clear yet (escape_ready, split_speed_power, split_escapes)
  - leans on **def_dps** (the defenders who came: their usual damage per second, summed (Denning: can they kill it)): -13.1 points at 0.0 to 1.4, +14.9 at 42.8 to 55.5
  - leans on **strength_gap** (splitting team's strength gap): +10.4 points at -1183.0 to -582.5, -6.7 at 627.5 to 1183.0
  - leans on **split_dp** (worst morale among the split members (death penalty lowers max health; Denning)): +22.0 points at -60.0 to -44.5, -5.0 at 9.5 to 10.0

## 7. The usual play

Each choice against the most common one in that kind of decision, in win-chance points over the decision's window, adjusted for the situation, with a 90% range from resampling whole matches. CLEAR = the range excludes 0. Win chance comes from a model that never saw the match. The same comparison over the 30 s BEFORE the decision is a placebo test: a choice can't cause what came before it, so a clear difference there means the effect is partly who makes that choice.

**after wipe** (585 decisions, 252 matches; usual: pushed the pit)
- reset (n 83): -2.2 [-4.3, -0.3] CLEAR; in the 30 s before: +1.2 [-1.1, +3.5]
- took the flag (n 69): -3.0 [-6.4, +0.6]; in the 30 s before: +1.3 [-2.6, +5.2]
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - reset, Corrupted Isle: -0.8 (n 17 against 55)
  - reset, Isle of Jade: -5.6 (n 16 against 61)
  - reset, Isle of Meditation: -2.5 (n 16 against 90)
  - took the flag, Corrupted Isle: +3.5 (n 18 against 55)
  - took the flag, Isle of Jade: -10.2 (n 10 against 61)
  - took the flag, Isle of Meditation: -4.4 (n 18 against 90)

**boost clock** (1012 decisions, 245 matches; usual: not running, fought)
- not running, fell back (n 169): -1.1 [-2.4, +0.4]; in the 30 s before: +0.2 [-1.0, +1.2]
- running, advanced (n 155): +2.0 [+0.5, +4.2] CLEAR; in the 30 s before: +0.8 [-0.5, +2.1]
- not running, advanced (n 135): -0.1 [-1.5, +1.7]; in the 30 s before: +1.9 [+0.8, +3.2] ALREADY DIFFERENT BEFORE: partly who chooses it
- running, fought (n 108): +3.2 [+1.3, +5.0] CLEAR; in the 30 s before: +0.1 [-1.0, +1.4]
- not running, held (n 86): +1.6 [+0.2, +3.3] CLEAR; in the 30 s before: +0.6 [-0.4, +1.5]
- running, fell back (n 68): +3.2 [+1.1, +5.1] CLEAR; in the 30 s before: -0.5 [-1.9, +0.8]
- running, held (n 49): +3.7 [+1.5, +5.9] CLEAR; in the 30 s before: +1.5 [-0.0, +3.4]
- not running, to the spawn (n 15): -2.1 [-7.3, +2.2]; in the 30 s before: +3.4 [-0.6, +8.3]
- running, to the spawn (n 5): +3.9 [-1.1, +9.9]; in the 30 s before: -0.3 [-3.4, +2.9]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - not running, fell back, behind in the fight (lowest third, -0.11 or less): -1.0 (n 88 against 107)
  - not running, fell back, middle third: -3.1 (n 45 against 69)
  - not running, fell back, ahead in the fight (top third, above -0.01): +0.3 (n 36 against 46)
  - running, advanced, behind in the fight (lowest third, -0.11 or less): -0.2 (n 22 against 107)
  - running, advanced, middle third: +1.0 (n 57 against 69)
  - running, advanced, ahead in the fight (top third, above -0.01): +4.1 (n 76 against 46)
  - not running, advanced, behind in the fight (lowest third, -0.11 or less): -0.8 (n 40 against 107)
  - not running, advanced, middle third: -1.2 (n 54 against 69)
  - not running, advanced, ahead in the fight (top third, above -0.01): +1.8 (n 41 against 46)
  - running, fought, behind in the fight (lowest third, -0.11 or less): -1.2 (n 20 against 107)
  - running, fought, middle third: +2.6 (n 42 against 69)
  - running, fought, ahead in the fight (top third, above -0.01): +5.8 (n 46 against 46)
  - not running, held, behind in the fight (lowest third, -0.11 or less): +0.2 (n 31 against 107)
  - not running, held, middle third: -1.3 (n 25 against 69)
  - not running, held, ahead in the fight (top third, above -0.01): +5.5 (n 30 against 46)
  - running, fell back, behind in the fight (lowest third, -0.11 or less): -0.4 (n 15 against 107)
  - running, fell back, middle third: +0.2 (n 26 against 69)
  - running, fell back, ahead in the fight (top third, above -0.01): +7.9 (n 27 against 46)
  - running, held, behind in the fight (lowest third, -0.11 or less): too few yet (n 4 against 107; means 2.9 against -0.4)
  - running, held, middle third: +2.2 (n 19 against 69)
  - running, held, ahead in the fight (top third, above -0.01): +4.6 (n 26 against 46)
  - not running, to the spawn, behind in the fight (lowest third, -0.11 or less): too few yet (n 9 against 107; means -0.5 against -0.4)
  - not running, to the spawn, middle third: too few yet (n 4 against 69; means -12.8 against -0.0)
  - not running, to the spawn, ahead in the fight (top third, above -0.01): too few yet (n 2 against 46; means -0.1 against -3.0)
  - running, to the spawn, behind in the fight (lowest third, -0.11 or less): too few yet (n 2 against 107; means 0.2 against -0.4)
  - running, to the spawn, middle third: too few yet (n 2 against 69; means -0.4 against -0.0)
  - running, to the spawn, ahead in the fight (top third, above -0.01): too few yet (n 1 against 46; means 17.0 against -3.0)
  By snare matchup (movepower.py: enemy snare power of the live players minus own speed power; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - not running, fell back, little enemy snare for own speed (lowest third, -17 or less): -3.3 (n 54 against 57)
  - not running, fell back, middle third: -0.4 (n 59 against 81)
  - not running, fell back, a lot of enemy snare for own speed (top third, above +12): -0.4 (n 56 against 84)
  - running, advanced, little enemy snare for own speed (lowest third, -17 or less): +2.1 (n 60 against 57)
  - running, advanced, middle third: +0.9 (n 54 against 81)
  - running, advanced, a lot of enemy snare for own speed (top third, above +12): +1.6 (n 41 against 84)
  - not running, advanced, little enemy snare for own speed (lowest third, -17 or less): -0.9 (n 55 against 57)
  - not running, advanced, middle third: +0.9 (n 41 against 81)
  - not running, advanced, a lot of enemy snare for own speed (top third, above +12): -1.3 (n 39 against 84)
  - running, fought, little enemy snare for own speed (lowest third, -17 or less): -0.0 (n 33 against 57)
  - running, fought, middle third: +5.3 (n 33 against 81)
  - running, fought, a lot of enemy snare for own speed (top third, above +12): +2.8 (n 42 against 84)
  - not running, held, little enemy snare for own speed (lowest third, -17 or less): +2.2 (n 19 against 57)
  - not running, held, middle third: +1.4 (n 33 against 81)
  - not running, held, a lot of enemy snare for own speed (top third, above +12): +0.6 (n 34 against 84)
  - running, fell back, little enemy snare for own speed (lowest third, -17 or less): +3.3 (n 29 against 57)
  - running, fell back, middle third: +0.6 (n 21 against 81)
  - running, fell back, a lot of enemy snare for own speed (top third, above +12): +3.7 (n 18 against 84)
  - running, held, little enemy snare for own speed (lowest third, -17 or less): +0.4 (n 26 against 57)
  - running, held, middle third: +3.9 (n 12 against 81)
  - running, held, a lot of enemy snare for own speed (top third, above +12): +6.4 (n 11 against 84)
  - not running, to the spawn, little enemy snare for own speed (lowest third, -17 or less): too few yet (n 3 against 57; means -13.2 against -0.4)
  - not running, to the spawn, middle third: too few yet (n 3 against 81; means 3.5 against -0.9)
  - not running, to the spawn, a lot of enemy snare for own speed (top third, above +12): too few yet (n 9 against 84; means -3.0 against -1.1)
  - running, to the spawn, little enemy snare for own speed (lowest third, -17 or less): too few yet (n 3 against 57; means 4.7 against -0.4)
  - running, to the spawn, a lot of enemy snare for own speed (top third, above +12): too few yet (n 2 against 84; means 1.2 against -1.1)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - not running, fell back, Corrupted Isle: +2.7 (n 29 against 27)
  - not running, fell back, Druid's Isle: -0.1 (n 22 against 12)
  - not running, fell back, Isle of Jade: -5.4 (n 21 against 36)
  - not running, fell back, Isle of Meditation: -1.3 (n 32 against 54)
  - not running, fell back, Isle of Solitude: -0.3 (n 23 against 33)
  - not running, fell back, Uncharted Isle: -2.2 (n 23 against 25)
  - running, advanced, Corrupted Isle: +6.2 (n 33 against 27)
  - running, advanced, Isle of Jade: -8.8 (n 13 against 36)
  - running, advanced, Isle of Meditation: +3.6 (n 34 against 54)
  - running, advanced, Isle of Solitude: +2.6 (n 23 against 33)
  - running, advanced, Isle of Weeping Stone: -1.2 (n 23 against 11)
  - running, advanced, Uncharted Isle: -5.3 (n 11 against 25)
  - not running, advanced, Corrupted Isle: +3.9 (n 26 against 27)
  - not running, advanced, Isle of Jade: -4.8 (n 13 against 36)
  - not running, advanced, Isle of Meditation: +0.7 (n 28 against 54)
  - not running, advanced, Isle of Solitude: +1.7 (n 27 against 33)
  - not running, advanced, Uncharted Isle: -4.1 (n 19 against 25)
  - running, fought, Corrupted Isle: +1.7 (n 12 against 27)
  - running, fought, Druid's Isle: +5.9 (n 18 against 12)
  - running, fought, Isle of Meditation: +0.7 (n 23 against 54)
  - running, fought, Isle of Solitude: +2.4 (n 18 against 33)
  - not running, held, Corrupted Isle: +4.5 (n 12 against 27)
  - not running, held, Druid's Isle: +2.8 (n 14 against 12)
  - not running, held, Isle of Jade: +0.2 (n 18 against 36)
  - not running, held, Isle of Meditation: +1.2 (n 13 against 54)
  - not running, held, Isle of Solitude: +2.0 (n 18 against 33)
  - running, fell back, Corrupted Isle: +4.4 (n 14 against 27)
  - running, fell back, Isle of Meditation: +1.2 (n 10 against 54)
  - running, fell back, Isle of Solitude: +4.9 (n 13 against 33)
  - running, fell back, Isle of Weeping Stone: -2.8 (n 12 against 11)
  - running, held, Isle of Jade: +0.8 (n 17 against 36)

**enemy pickup** (3460 decisions, 255 matches; usual: held, advanced)
- already running, advanced (n 469): -1.0 [-2.9, +1.2]; in the 30 s before: +1.6 [+0.3, +3.0] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, fell back (n 450): -0.8 [-3.1, +1.3]; in the 30 s before: +0.3 [-1.0, +1.7]
- already running, fell back (n 364): -1.7 [-4.2, +0.4]; in the 30 s before: +1.6 [-0.0, +3.3]
- held, fought (n 349): -1.2 [-3.2, +0.6]; in the 30 s before: +0.6 [-0.5, +1.8]
- already running, fought (n 303): -2.3 [-4.7, -0.0] CLEAR; in the 30 s before: +1.3 [-0.1, +2.7]
- ran, fell back (n 262): +0.0 [-2.0, +1.9]; in the 30 s before: +0.8 [-0.7, +2.3]
- ran, advanced (n 199): -0.8 [-3.1, +1.3]; in the 30 s before: +1.8 [+0.1, +3.4] ALREADY DIFFERENT BEFORE: partly who chooses it
- ran, fought (n 162): -0.8 [-2.7, +1.0]; in the 30 s before: +1.8 [+0.3, +3.2] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, held (n 144): +2.0 [-1.2, +5.3]; in the 30 s before: +0.2 [-0.9, +1.4]
- already running, held (n 138): -3.2 [-6.2, -0.6] CLEAR; in the 30 s before: +1.3 [-1.0, +3.6]
- ran, held (n 97): +1.0 [-1.2, +3.4]; in the 30 s before: +0.3 [-1.3, +2.3]
- held, to the spawn (n 7): -0.4 [-5.9, +4.3]; in the 30 s before: +1.6 [-1.9, +5.7]
- held (n 5): -4.3 [-13.6, +3.2]; in the 30 s before: +7.4 [+2.9, +13.2] ALREADY DIFFERENT BEFORE: partly who chooses it
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - already running, advanced, behind in the fight (lowest third, -0.01 or less): +0.8 (n 128 against 129)
  - already running, advanced, middle third: +1.2 (n 206 against 154)
  - already running, advanced, ahead in the fight (top third, above +0.02): -1.1 (n 135 against 228)
  - held, fell back, behind in the fight (lowest third, -0.01 or less): -1.3 (n 202 against 129)
  - held, fell back, middle third: +1.7 (n 122 against 154)
  - held, fell back, ahead in the fight (top third, above +0.02): -3.2 (n 126 against 228)
  - already running, fell back, behind in the fight (lowest third, -0.01 or less): +0.4 (n 171 against 129)
  - already running, fell back, middle third: +0.8 (n 114 against 154)
  - already running, fell back, ahead in the fight (top third, above +0.02): -2.6 (n 79 against 228)
  - held, fought, behind in the fight (lowest third, -0.01 or less): -1.3 (n 97 against 129)
  - held, fought, middle third: -0.8 (n 59 against 154)
  - held, fought, ahead in the fight (top third, above +0.02): -3.3 (n 193 against 228)
  - already running, fought, behind in the fight (lowest third, -0.01 or less): -1.3 (n 103 against 129)
  - already running, fought, middle third: +1.9 (n 89 against 154)
  - already running, fought, ahead in the fight (top third, above +0.02): -3.7 (n 111 against 228)
  - ran, fell back, behind in the fight (lowest third, -0.01 or less): +1.4 (n 115 against 129)
  - ran, fell back, middle third: +1.1 (n 84 against 154)
  - ran, fell back, ahead in the fight (top third, above +0.02): -0.8 (n 63 against 228)
  - ran, advanced, behind in the fight (lowest third, -0.01 or less): +1.3 (n 56 against 129)
  - ran, advanced, middle third: +0.6 (n 80 against 154)
  - ran, advanced, ahead in the fight (top third, above +0.02): -2.2 (n 63 against 228)
  - ran, fought, behind in the fight (lowest third, -0.01 or less): +2.2 (n 54 against 129)
  - ran, fought, middle third: +1.5 (n 50 against 154)
  - ran, fought, ahead in the fight (top third, above +0.02): -5.0 (n 58 against 228)
  - held, held, behind in the fight (lowest third, -0.01 or less): -0.7 (n 37 against 129)
  - held, held, middle third: +6.8 (n 59 against 154)
  - held, held, ahead in the fight (top third, above +0.02): -1.0 (n 48 against 228)
  - already running, held, behind in the fight (lowest third, -0.01 or less): -3.0 (n 46 against 129)
  - already running, held, middle third: +0.8 (n 67 against 154)
  - already running, held, ahead in the fight (top third, above +0.02): -3.8 (n 25 against 228)
  - ran, held, behind in the fight (lowest third, -0.01 or less): +1.8 (n 39 against 129)
  - ran, held, middle third: +5.1 (n 44 against 154)
  - ran, held, ahead in the fight (top third, above +0.02): -3.4 (n 14 against 228)
  - held, to the spawn, behind in the fight (lowest third, -0.01 or less): too few yet (n 3 against 129; means -2.1 against 0.0)
  - held, to the spawn, middle third: too few yet (n 3 against 154; means 4.3 against -0.9)
  - held, to the spawn, ahead in the fight (top third, above +0.02): too few yet (n 1 against 228; means -3.1 against 2.8)
  - held, behind in the fight (lowest third, -0.01 or less): too few yet (n 2 against 129; means -6.1 against 0.0)
  - held, middle third: too few yet (n 3 against 154; means -0.7 against -0.9)
  By snare matchup (movepower.py: enemy snare power of the live players minus own speed power; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - already running, advanced, little enemy snare for own speed (lowest third, -23 or less): +2.0 (n 195 against 148)
  - already running, advanced, middle third: -1.9 (n 136 against 212)
  - already running, advanced, a lot of enemy snare for own speed (top third, above +7): -0.5 (n 138 against 151)
  - held, fell back, little enemy snare for own speed (lowest third, -23 or less): -0.3 (n 146 against 148)
  - held, fell back, middle third: -1.4 (n 144 against 212)
  - held, fell back, a lot of enemy snare for own speed (top third, above +7): -2.4 (n 160 against 151)
  - already running, fell back, little enemy snare for own speed (lowest third, -23 or less): +0.4 (n 147 against 148)
  - already running, fell back, middle third: -1.5 (n 106 against 212)
  - already running, fell back, a lot of enemy snare for own speed (top third, above +7): -1.0 (n 111 against 151)
  - held, fought, little enemy snare for own speed (lowest third, -23 or less): +0.3 (n 115 against 148)
  - held, fought, middle third: -1.7 (n 120 against 212)
  - held, fought, a lot of enemy snare for own speed (top third, above +7): -4.1 (n 114 against 151)
  - already running, fought, little enemy snare for own speed (lowest third, -23 or less): -1.3 (n 83 against 148)
  - already running, fought, middle third: -2.5 (n 117 against 212)
  - already running, fought, a lot of enemy snare for own speed (top third, above +7): -0.5 (n 103 against 151)
  - ran, fell back, little enemy snare for own speed (lowest third, -23 or less): +3.5 (n 81 against 148)
  - ran, fell back, middle third: -1.2 (n 85 against 212)
  - ran, fell back, a lot of enemy snare for own speed (top third, above +7): -1.2 (n 96 against 151)
  - ran, advanced, little enemy snare for own speed (lowest third, -23 or less): +0.0 (n 68 against 148)
  - ran, advanced, middle third: -0.5 (n 57 against 212)
  - ran, advanced, a lot of enemy snare for own speed (top third, above +7): -0.9 (n 74 against 151)
  - ran, fought, little enemy snare for own speed (lowest third, -23 or less): -0.1 (n 46 against 148)
  - ran, fought, middle third: +0.9 (n 56 against 212)
  - ran, fought, a lot of enemy snare for own speed (top third, above +7): -3.2 (n 60 against 151)
  - held, held, little enemy snare for own speed (lowest third, -23 or less): +2.7 (n 56 against 148)
  - held, held, middle third: +1.5 (n 42 against 212)
  - held, held, a lot of enemy snare for own speed (top third, above +7): +1.8 (n 46 against 151)
  - already running, held, little enemy snare for own speed (lowest third, -23 or less): -0.7 (n 53 against 148)
  - already running, held, middle third: -3.5 (n 44 against 212)
  - already running, held, a lot of enemy snare for own speed (top third, above +7): -2.1 (n 41 against 151)
  - ran, held, little enemy snare for own speed (lowest third, -23 or less): +2.9 (n 25 against 148)
  - ran, held, middle third: +4.9 (n 34 against 212)
  - ran, held, a lot of enemy snare for own speed (top third, above +7): -2.5 (n 38 against 151)
  - held, to the spawn, little enemy snare for own speed (lowest third, -23 or less): too few yet (n 3 against 148; means 1.7 against -0.4)
  - held, to the spawn, middle third: too few yet (n 1 against 212; means 4.8 against 1.5)
  - held, to the spawn, a lot of enemy snare for own speed (top third, above +7): too few yet (n 3 against 151; means -2.1 against 1.6)
  - held, little enemy snare for own speed (lowest third, -23 or less): too few yet (n 1 against 148; means -12.2 against -0.4)
  - held, a lot of enemy snare for own speed (top third, above +7): too few yet (n 4 against 151; means -0.5 against 1.6)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - already running, advanced, Corrupted Isle: +1.0 (n 109 against 124)
  - already running, advanced, Druid's Isle: +2.7 (n 26 against 19)
  - already running, advanced, Imperial Isle: -6.4 (n 32 against 20)
  - already running, advanced, Isle of Jade: -2.1 (n 25 against 55)
  - already running, advanced, Isle of Meditation: -0.6 (n 81 against 74)
  - already running, advanced, Isle of Solitude: +5.1 (n 60 against 58)
  - already running, advanced, Isle of Weeping Stone: -1.1 (n 62 against 49)
  - already running, advanced, Uncharted Isle: -2.4 (n 66 against 97)
  - held, fell back, Corrupted Isle: -4.1 (n 106 against 124)
  - held, fell back, Druid's Isle: +1.0 (n 19 against 19)
  - held, fell back, Imperial Isle: -1.2 (n 19 against 20)
  - held, fell back, Isle of Jade: +8.3 (n 45 against 55)
  - held, fell back, Isle of Meditation: -2.0 (n 77 against 74)
  - held, fell back, Isle of Solitude: +2.4 (n 57 against 58)
  - held, fell back, Isle of Weeping Stone: -2.2 (n 45 against 49)
  - held, fell back, Nomad's Isle: +1.2 (n 12 against 15)
  - held, fell back, Uncharted Isle: -5.2 (n 69 against 97)
  - already running, fell back, Corrupted Isle: -0.9 (n 74 against 124)
  - already running, fell back, Druid's Isle: -0.7 (n 15 against 19)
  - already running, fell back, Imperial Isle: -4.0 (n 17 against 20)
  - already running, fell back, Isle of Jade: +3.4 (n 16 against 55)
  - already running, fell back, Isle of Meditation: +1.3 (n 51 against 74)
  - already running, fell back, Isle of Solitude: +3.5 (n 51 against 58)
  - already running, fell back, Isle of Weeping Stone: -1.6 (n 44 against 49)
  - already running, fell back, Nomad's Isle: -2.6 (n 18 against 15)
  - already running, fell back, Uncharted Isle: -5.5 (n 78 against 97)
  - held, fought, Corrupted Isle: +2.5 (n 57 against 124)
  - held, fought, Druid's Isle: -5.1 (n 58 against 19)
  - held, fought, Imperial Isle: -6.0 (n 11 against 20)
  - held, fought, Isle of Jade: +2.5 (n 35 against 55)
  - held, fought, Isle of Meditation: -0.3 (n 58 against 74)
  - held, fought, Isle of Solitude: -1.9 (n 29 against 58)
  - held, fought, Isle of Weeping Stone: +0.6 (n 32 against 49)
  - held, fought, Nomad's Isle: -2.3 (n 31 against 15)
  - held, fought, Uncharted Isle: -7.3 (n 36 against 97)
  - already running, fought, Corrupted Isle: -0.8 (n 57 against 124)
  - already running, fought, Druid's Isle: -2.8 (n 30 against 19)
  - already running, fought, Imperial Isle: -2.1 (n 22 against 20)
  - already running, fought, Isle of Jade: +8.7 (n 11 against 55)
  - already running, fought, Isle of Meditation: -1.8 (n 48 against 74)
  - already running, fought, Isle of Solitude: +1.2 (n 44 against 58)
  - already running, fought, Isle of Weeping Stone: +0.5 (n 46 against 49)
  - already running, fought, Nomad's Isle: +1.9 (n 21 against 15)
  - already running, fought, Uncharted Isle: -11.2 (n 24 against 97)
  - ran, fell back, Corrupted Isle: +1.0 (n 63 against 124)
  - ran, fell back, Druid's Isle: +1.0 (n 15 against 19)
  - ran, fell back, Imperial Isle: -0.2 (n 19 against 20)
  - ran, fell back, Isle of Jade: -0.5 (n 17 against 55)
  - ran, fell back, Isle of Meditation: +0.7 (n 30 against 74)
  - ran, fell back, Isle of Solitude: +3.7 (n 33 against 58)
  - ran, fell back, Isle of Weeping Stone: +1.5 (n 34 against 49)
  - ran, fell back, Uncharted Isle: -3.4 (n 45 against 97)
  - ran, advanced, Corrupted Isle: -4.0 (n 30 against 124)
  - ran, advanced, Imperial Isle: -2.1 (n 24 against 20)
  - ran, advanced, Isle of Jade: +3.0 (n 29 against 55)
  - ran, advanced, Isle of Meditation: +0.8 (n 28 against 74)
  - ran, advanced, Isle of Solitude: +3.7 (n 21 against 58)
  - ran, advanced, Isle of Weeping Stone: +5.8 (n 23 against 49)
  - ran, advanced, Uncharted Isle: -6.9 (n 35 against 97)
  - ran, fought, Corrupted Isle: +2.1 (n 15 against 124)
  - ran, fought, Druid's Isle: +4.1 (n 19 against 19)
  - ran, fought, Imperial Isle: -3.4 (n 23 against 20)
  - ran, fought, Isle of Meditation: +1.8 (n 21 against 74)
  - ran, fought, Isle of Solitude: +2.9 (n 19 against 58)
  - ran, fought, Isle of Weeping Stone: -3.1 (n 31 against 49)
  - ran, fought, Nomad's Isle: -2.4 (n 10 against 15)
  - ran, fought, Uncharted Isle: -4.7 (n 15 against 97)
  - held, held, Corrupted Isle: +3.6 (n 12 against 124)
  - held, held, Druid's Isle: +1.4 (n 23 against 19)
  - held, held, Isle of Jade: +14.3 (n 35 against 55)
  - held, held, Isle of Meditation: -2.8 (n 17 against 74)
  - held, held, Isle of Solitude: +0.8 (n 16 against 58)
  - held, held, Isle of Weeping Stone: -7.6 (n 15 against 49)
  - held, held, Nomad's Isle: +2.0 (n 13 against 15)
  - already running, held, Corrupted Isle: -1.3 (n 15 against 124)
  - already running, held, Druid's Isle: -10.1 (n 12 against 19)
  - already running, held, Isle of Jade: +7.5 (n 19 against 55)
  - already running, held, Isle of Meditation: -1.9 (n 17 against 74)
  - already running, held, Isle of Solitude: -1.6 (n 19 against 58)
  - already running, held, Isle of Weeping Stone: -5.2 (n 15 against 49)
  - already running, held, Uncharted Isle: -5.9 (n 22 against 97)
  - ran, held, Imperial Isle: -2.4 (n 10 against 20)
  - ran, held, Isle of Jade: +8.1 (n 24 against 55)
  - ran, held, Isle of Solitude: +1.1 (n 12 against 58)
  - ran, held, Uncharted Isle: +3.8 (n 12 against 97)

**late game** (100 decisions, 50 matches; usual: 2 to 3 at the enemy Lord)
- 0 to 1 at the enemy Lord (n 38): -20.2 [-36.1, -1.5] CLEAR; in the 30 s before: +0.5 [-2.9, +4.3]
- 4+ at the enemy Lord (n 20): +5.5 [-5.9, +19.0]; in the 30 s before: +1.7 [-1.9, +4.5]

**power play** (2499 decisions, 265 matches; usual: pushed, advanced)
- pushed, fought (n 545): +0.2 [-1.0, +1.2]; in the 30 s before: -0.1 [-0.7, +0.6]
- held, fought (n 305): -0.2 [-1.3, +0.8]; in the 30 s before: -0.7 [-1.4, +0.0]
- pushed, fell back (n 288): -0.0 [-1.1, +1.0]; in the 30 s before: -1.0 [-1.9, -0.1] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, fell back (n 280): -1.0 [-2.1, +0.2]; in the 30 s before: -0.9 [-1.7, +0.1]
- held, advanced (n 198): -0.9 [-2.0, +0.5]; in the 30 s before: -0.1 [-1.0, +1.0]
- held, held (n 89): -1.3 [-2.6, +0.3]; in the 30 s before: +1.1 [-0.6, +2.7]
- pushed, held (n 84): -0.2 [-1.4, +1.3]; in the 30 s before: -0.4 [-2.2, +1.3]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - pushed, fought, behind in the fight (lowest third, +0.00 or less): +1.2 (n 162 against 211)
  - pushed, fought, middle third: -1.7 (n 149 against 245)
  - pushed, fought, ahead in the fight (top third, above +0.07): -0.5 (n 234 against 254)
  - held, fought, behind in the fight (lowest third, +0.00 or less): +0.5 (n 102 against 211)
  - held, fought, middle third: -0.7 (n 101 against 245)
  - held, fought, ahead in the fight (top third, above +0.07): -2.4 (n 102 against 254)
  - pushed, fell back, behind in the fight (lowest third, +0.00 or less): +0.5 (n 110 against 211)
  - pushed, fell back, middle third: -0.3 (n 90 against 245)
  - pushed, fell back, ahead in the fight (top third, above +0.07): -1.8 (n 88 against 254)
  - held, fell back, behind in the fight (lowest third, +0.00 or less): -2.4 (n 121 against 211)
  - held, fell back, middle third: +0.1 (n 106 against 245)
  - held, fell back, ahead in the fight (top third, above +0.07): -1.9 (n 53 against 254)
  - held, advanced, behind in the fight (lowest third, +0.00 or less): -0.3 (n 74 against 211)
  - held, advanced, middle third: -2.0 (n 64 against 245)
  - held, advanced, ahead in the fight (top third, above +0.07): -0.8 (n 60 against 254)
  - held, held, behind in the fight (lowest third, +0.00 or less): -0.8 (n 38 against 211)
  - held, held, middle third: -4.2 (n 33 against 245)
  - held, held, ahead in the fight (top third, above +0.07): -2.1 (n 18 against 254)
  - pushed, held, behind in the fight (lowest third, +0.00 or less): -1.1 (n 36 against 211)
  - pushed, held, middle third: +0.5 (n 31 against 245)
  - pushed, held, ahead in the fight (top third, above +0.07): -0.6 (n 17 against 254)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - pushed, fought, Corrupted Isle: +1.4 (n 78 against 144)
  - pushed, fought, Druid's Isle: -0.2 (n 72 against 45)
  - pushed, fought, Imperial Isle: +0.3 (n 21 against 37)
  - pushed, fought, Isle of Jade: +1.4 (n 50 against 56)
  - pushed, fought, Isle of Meditation: -0.5 (n 87 against 151)
  - pushed, fought, Isle of Solitude: -2.0 (n 78 against 98)
  - pushed, fought, Isle of Weeping Stone: +1.5 (n 62 against 74)
  - pushed, fought, Nomad's Isle: +0.4 (n 42 against 14)
  - pushed, fought, Uncharted Isle: -0.6 (n 53 against 89)
  - held, fought, Corrupted Isle: +0.9 (n 36 against 144)
  - held, fought, Druid's Isle: -3.4 (n 41 against 45)
  - held, fought, Imperial Isle: -0.5 (n 18 against 37)
  - held, fought, Isle of Jade: -2.7 (n 29 against 56)
  - held, fought, Isle of Meditation: -1.4 (n 55 against 151)
  - held, fought, Isle of Solitude: -2.3 (n 38 against 98)
  - held, fought, Isle of Weeping Stone: +3.0 (n 29 against 74)
  - held, fought, Nomad's Isle: +3.2 (n 37 against 14)
  - held, fought, Uncharted Isle: -1.5 (n 22 against 89)
  - pushed, fell back, Corrupted Isle: -1.2 (n 59 against 144)
  - pushed, fell back, Druid's Isle: -5.9 (n 16 against 45)
  - pushed, fell back, Imperial Isle: -4.1 (n 11 against 37)
  - pushed, fell back, Isle of Jade: -0.4 (n 18 against 56)
  - pushed, fell back, Isle of Meditation: -0.4 (n 45 against 151)
  - pushed, fell back, Isle of Solitude: +3.3 (n 60 against 98)
  - pushed, fell back, Isle of Weeping Stone: -1.6 (n 29 against 74)
  - pushed, fell back, Nomad's Isle: +2.0 (n 15 against 14)
  - pushed, fell back, Uncharted Isle: -0.6 (n 33 against 89)
  - held, fell back, Corrupted Isle: +0.3 (n 47 against 144)
  - held, fell back, Druid's Isle: -2.2 (n 16 against 45)
  - held, fell back, Imperial Isle: -2.5 (n 13 against 37)
  - held, fell back, Isle of Jade: -2.3 (n 17 against 56)
  - held, fell back, Isle of Meditation: -1.9 (n 47 against 151)
  - held, fell back, Isle of Solitude: -1.2 (n 55 against 98)
  - held, fell back, Isle of Weeping Stone: -2.1 (n 32 against 74)
  - held, fell back, Nomad's Isle: +1.4 (n 18 against 14)
  - held, fell back, Uncharted Isle: -1.7 (n 35 against 89)
  - held, advanced, Corrupted Isle: -1.7 (n 33 against 144)
  - held, advanced, Druid's Isle: +9.2 (n 11 against 45)
  - held, advanced, Imperial Isle: -3.2 (n 16 against 37)
  - held, advanced, Isle of Jade: -3.5 (n 19 against 56)
  - held, advanced, Isle of Meditation: -1.0 (n 44 against 151)
  - held, advanced, Isle of Solitude: -3.3 (n 25 against 98)
  - held, advanced, Isle of Weeping Stone: -1.2 (n 24 against 74)
  - held, advanced, Uncharted Isle: -3.2 (n 21 against 89)
  - held, held, Druid's Isle: -3.5 (n 21 against 45)
  - held, held, Isle of Meditation: -1.9 (n 12 against 151)
  - held, held, Isle of Solitude: -0.9 (n 17 against 98)
  - pushed, held, Druid's Isle: -4.1 (n 10 against 45)
  - pushed, held, Isle of Meditation: -1.3 (n 12 against 151)
  - pushed, held, Isle of Solitude: +0.5 (n 17 against 98)
  - pushed, held, Isle of Weeping Stone: -1.3 (n 16 against 74)
  - pushed, held, Uncharted Isle: +3.8 (n 11 against 89)

**runner choice** (2375 decisions, 238 matches; usual: monk)
- mesmer (n 479): +0.1 [-1.0, +1.3]; in the 30 s before: -0.4 [-1.5, +0.9]
- dervish (n 396): -0.3 [-1.7, +0.8]; in the 30 s before: +0.2 [-1.1, +1.4]
- warrior (n 295): -1.7 [-2.9, -0.5] CLEAR; in the 30 s before: +0.9 [-0.2, +2.0]
- ritualist (n 291): +1.0 [-0.4, +2.3]; in the 30 s before: -0.8 [-1.8, +0.4]
- elementalist (n 179): -0.4 [-1.6, +0.9]; in the 30 s before: +0.9 [-0.6, +2.3]
- necromancer (n 88): -0.2 [-3.2, +2.0]; in the 30 s before: -1.6 [-3.4, +0.1]
- ranger (n 54): -0.2 [-2.8, +2.7]; in the 30 s before: +1.1 [-0.4, +2.8]
- paragon (n 14): -2.9 [-5.3, -0.5] CLEAR; in the 30 s before: +4.6 [+0.3, +8.4] ALREADY DIFFERENT BEFORE: partly who chooses it
- assassin (n 8): +3.7 [-1.6, +9.6]; in the 30 s before: +2.1 [-1.1, +6.9]
  By snare matchup (movepower.py: enemy snare power of the live players minus own speed power; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - mesmer, little enemy snare for own speed (lowest third, -29 or less): -0.2 (n 157 against 184)
  - mesmer, middle third: -1.6 (n 136 against 233)
  - mesmer, a lot of enemy snare for own speed (top third, above +7): +0.8 (n 186 against 154)
  - dervish, little enemy snare for own speed (lowest third, -29 or less): +0.0 (n 122 against 184)
  - dervish, middle third: -0.3 (n 124 against 233)
  - dervish, a lot of enemy snare for own speed (top third, above +7): -0.0 (n 150 against 154)
  - warrior, little enemy snare for own speed (lowest third, -29 or less): -1.7 (n 100 against 184)
  - warrior, middle third: -2.6 (n 114 against 233)
  - warrior, a lot of enemy snare for own speed (top third, above +7): -0.3 (n 81 against 154)
  - ritualist, little enemy snare for own speed (lowest third, -29 or less): -0.5 (n 108 against 184)
  - ritualist, middle third: +1.6 (n 109 against 233)
  - ritualist, a lot of enemy snare for own speed (top third, above +7): +1.3 (n 74 against 154)
  - elementalist, little enemy snare for own speed (lowest third, -29 or less): -1.8 (n 54 against 184)
  - elementalist, middle third: -0.3 (n 51 against 233)
  - elementalist, a lot of enemy snare for own speed (top third, above +7): +0.2 (n 74 against 154)
  - necromancer, little enemy snare for own speed (lowest third, -29 or less): +0.3 (n 38 against 184)
  - necromancer, middle third: +0.9 (n 15 against 233)
  - necromancer, a lot of enemy snare for own speed (top third, above +7): -0.5 (n 35 against 154)
  - ranger, little enemy snare for own speed (lowest third, -29 or less): -1.0 (n 22 against 184)
  - ranger, middle third: -0.5 (n 13 against 233)
  - ranger, a lot of enemy snare for own speed (top third, above +7): -0.2 (n 19 against 154)
  - paragon, little enemy snare for own speed (lowest third, -29 or less): too few yet (n 6 against 184; means -0.7 against 0.2)
  - paragon, middle third: too few yet (n 6 against 233; means -1.3 against 0.2)
  - paragon, a lot of enemy snare for own speed (top third, above +7): too few yet (n 2 against 154; means -7.3 against 0.2)
  - assassin, little enemy snare for own speed (lowest third, -29 or less): too few yet (n 2 against 184; means 8.8 against 0.2)
  - assassin, middle third: too few yet (n 3 against 233; means 7.8 against 0.2)
  - assassin, a lot of enemy snare for own speed (top third, above +7): too few yet (n 3 against 154; means -0.2 against 0.2)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - mesmer, Corrupted Isle: -2.3 (n 83 against 159)
  - mesmer, Druid's Isle: +0.2 (n 15 against 89)
  - mesmer, Imperial Isle: -0.6 (n 55 against 15)
  - mesmer, Isle of Jade: -0.8 (n 24 against 37)
  - mesmer, Isle of Meditation: +1.4 (n 81 against 74)
  - mesmer, Isle of Solitude: +1.0 (n 51 against 73)
  - mesmer, Isle of Weeping Stone: +0.9 (n 77 against 82)
  - mesmer, Nomad's Isle: +5.7 (n 16 against 16)
  - mesmer, Uncharted Isle: +4.3 (n 77 against 26)
  - dervish, Corrupted Isle: +0.3 (n 58 against 159)
  - dervish, Druid's Isle: -2.7 (n 18 against 89)
  - dervish, Imperial Isle: +1.1 (n 29 against 15)
  - dervish, Isle of Jade: -2.9 (n 11 against 37)
  - dervish, Isle of Meditation: +0.0 (n 67 against 74)
  - dervish, Isle of Solitude: +0.6 (n 79 against 73)
  - dervish, Isle of Weeping Stone: +2.0 (n 60 against 82)
  - dervish, Uncharted Isle: +3.7 (n 67 against 26)
  - warrior, Corrupted Isle: -2.9 (n 66 against 159)
  - warrior, Druid's Isle: -8.1 (n 12 against 89)
  - warrior, Imperial Isle: -0.7 (n 29 against 15)
  - warrior, Isle of Jade: +0.4 (n 26 against 37)
  - warrior, Isle of Meditation: -2.0 (n 37 against 74)
  - warrior, Isle of Solitude: -1.6 (n 34 against 73)
  - warrior, Isle of Weeping Stone: -1.0 (n 44 against 82)
  - warrior, Uncharted Isle: +4.7 (n 42 against 26)
  - ritualist, Corrupted Isle: +0.7 (n 34 against 159)
  - ritualist, Isle of Jade: +0.8 (n 19 against 37)
  - ritualist, Isle of Meditation: +0.4 (n 76 against 74)
  - ritualist, Isle of Solitude: +2.1 (n 52 against 73)
  - ritualist, Isle of Weeping Stone: +0.9 (n 48 against 82)
  - ritualist, Uncharted Isle: +7.7 (n 51 against 26)
  - elementalist, Corrupted Isle: -1.6 (n 39 against 159)
  - elementalist, Druid's Isle: -5.8 (n 14 against 89)
  - elementalist, Imperial Isle: +0.9 (n 29 against 15)
  - elementalist, Isle of Jade: -1.7 (n 20 against 37)
  - elementalist, Isle of Meditation: +1.8 (n 32 against 74)
  - elementalist, Isle of Solitude: -1.7 (n 14 against 73)
  - elementalist, Isle of Weeping Stone: +5.2 (n 13 against 82)
  - elementalist, Uncharted Isle: +2.3 (n 11 against 26)
  - necromancer, Druid's Isle: -0.4 (n 19 against 89)
  - necromancer, Isle of Solitude: +0.6 (n 20 against 73)
  - necromancer, Uncharted Isle: +2.3 (n 17 against 26)
  - ranger, Corrupted Isle: -0.7 (n 12 against 159)
  - ranger, Isle of Meditation: -0.5 (n 17 against 74)

**split in base** (536 decisions, 176 matches; usual: defended without a collapse)
- collapsed (n 216): -3.2 [-5.3, -1.2] CLEAR; in the 30 s before: +0.9 [-0.5, +1.9]
- missed (n 62): -2.2 [-5.6, +1.5]; in the 30 s before: +2.3 [+0.2, +4.6] ALREADY DIFFERENT BEFORE: partly who chooses it
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - collapsed, Corrupted Isle: -2.0 (n 42 against 47)
  - collapsed, Isle of Meditation: -2.1 (n 42 against 30)
  - collapsed, Isle of Solitude: -0.7 (n 37 against 74)
  - collapsed, Isle of Weeping Stone: +2.3 (n 18 against 31)
  - collapsed, Uncharted Isle: -9.6 (n 23 against 59)
  - missed, Corrupted Isle: +0.5 (n 12 against 47)
  - missed, Isle of Solitude: -0.3 (n 21 against 74)

**split or stay** (9943 decisions, 266 matches; usual: stayed)
- split (n 933): -0.6 [-1.4, +0.1]; in the 30 s before: +0.5 [+0.1, +1.0] ALREADY DIFFERENT BEFORE: partly who chooses it
  By snare matchup (movepower.py: enemy snare power of the live players minus own speed power; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - split, little enemy snare for own speed (lowest third, -26 or less): -1.2 (n 366 against 2963)
  - split, middle third: -0.2 (n 275 against 3032)
  - split, a lot of enemy snare for own speed (top third, above +5): -0.5 (n 292 against 3015)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - split, Corrupted Isle: -2.6 (n 173 against 1428)
  - split, Druid's Isle: +3.0 (n 38 against 971)
  - split, Imperial Isle: +1.1 (n 42 against 432)
  - split, Isle of Jade: -1.9 (n 58 against 1190)
  - split, Isle of Meditation: -0.2 (n 173 against 1570)
  - split, Isle of Solitude: +0.7 (n 157 against 1183)
  - split, Isle of Weeping Stone: -0.0 (n 94 against 917)
  - split, Nomad's Isle: +1.2 (n 49 against 379)
  - split, Uncharted Isle: -2.4 (n 149 against 908)

**Collapses on a split: time away and its cost** (`S32`; per collapse, averages; main = what the main fight lost while the collapsers were away)

| Group | Cases | Away (median s) | Split killed | Collapser died | Own deaths at main | Enemy deaths at main | Flag lead change | DP change | Win change |
|---|---|---|---|---|---|---|---|---|---|
| all | 236 | 22 | 59 | 21 | 0.6 | 0.54 | +2.6 | -4.2 | -3.1 |
| away under 30 s | 134 | 6 | 35 | 1 | 0.04 | 0.16 | +0.1 | +0.4 | -3.4 |
| away 30 to 60 s | 36 | 43.5 | 8 | 5 | 1 | 0.53 | -4.8 | -11.3 | -0.9 |
| away 60 s or more | 66 | 96 | 16 | 15 | 1.5 | 1.33 | +11.5 | -9.7 | -3.8 |
| before 20:00 | 199 | 22 | 47 | 16 | 0.5 | 0.51 | +2.9 | -5.0 | -3.3 |
| from 20:00 | 37 | 20 | 12 | 5 | 1.11 | 0.7 | +0.6 | +0.3 | -1.9 |
| split member killed | 59 | 23 | 59 | 1 | 0.1 | 1.36 | +5.4 | +0.6 | +0.2 |
| no kill | 177 | 22 | 0 | 20 | 0.76 | 0.27 | +1.6 | -5.8 | -4.2 |

**Leverage: where the choice matters most** (share of the spread in win-chance change explained by the choice beyond the situation; range = best minus worst choice, in points)

- late game (100): choice explains 8.8% (situation 15.2%); range 25.7 points, best 4+ at the enemy Lord, worst 0 to 1 at the enemy Lord
- boost clock (1012): choice explains 3.2% (situation 2.0%); range 6.8 points, best running, to the spawn, worst not running, to the spawn
- after wipe (585): choice explains 1.1% (situation 4.3%); range 3.0 points, best pushed the pit, worst took the flag
- split in base (536): choice explains 0.9% (situation 4.2%); range 2.9 points, best defended without a collapse, worst collapsed
- enemy pickup (3460): choice explains 0.7% (situation 2.7%); range 5.7 points, best held, held, worst held
- runner choice (2375): choice explains 0.5% (situation 2.3%); range 6.7 points, best assassin, worst paragon
- power play (2499): choice explains 0.2% (situation 2.1%); range 1.7 points, best pushed, advanced, worst held, held
- split or stay (9943): choice explains 0.0% (situation 2.1%); range 0.6 points, best stayed, worst split

**Behaviour clusters: what teams actually did** (each decision's response grouped by what every player did in the next 20 s; UNNAMED = a group no single named choice covers: a response for Denning to name or reject)

*after wipe* (2 groups, separation 0.31):
- n 341: fought (midline, 1.9 of 8), fought (backline, 1.5 of 8), fought (frontline, 0.9 of 8), held (backline, 0.7 of 8); named as {'pushed the pit': 290, 'reset': 30, 'took the flag': 21}; win change -0.8
- n 244: advanced (backline, 2.6 of 8), advanced (midline, 2.5 of 8), advanced (frontline, 1.3 of 8); named as {'pushed the pit': 143, 'reset': 53, 'took the flag': 48}; win change 1.4 UNNAMED
*boost clock* (4 groups, separation 0.19):
- n 401: fought (midline, 2.3 of 8), fought (backline, 2.1 of 8), fought (frontline, 0.9 of 8), held (backline, 0.6 of 8); named as {'not running, fought': 146, 'running, fought': 75, 'not running, fell back': 45}; win change 0.3 UNNAMED
- n 234: held (backline, 1.3 of 8), fought (midline, 0.7 of 8), to the spawn (backline, 0.7 of 8), held (midline, 0.7 of 8); named as {'not running, fought': 47, 'not running, fell back': 46, 'not running, held': 43}; win change -0.2 UNNAMED
- n 205: advanced (backline, 2.1 of 8), advanced (midline, 2.1 of 8), advanced (frontline, 0.8 of 8); named as {'running, advanced': 81, 'not running, advanced': 64, 'running, fought': 15}; win change 0.5 UNNAMED
- n 174: fell back (midline, 1.8 of 8), fell back (backline, 1.8 of 8), fell back (frontline, 0.7 of 8), fought (midline, 0.5 of 8); named as {'not running, fell back': 70, 'running, fell back': 31, 'not running, advanced': 19}; win change -1.7 UNNAMED
*enemy pickup* (3 groups, separation 0.22):
- n 1615: fought (midline, 1.9 of 8), fought (backline, 1.7 of 8), fought (frontline, 1.0 of 8), held (backline, 0.9 of 8); named as {'held, fought': 274, 'already running, fought': 245, 'held, advanced': 179}; win change -0.2 UNNAMED
- n 997: advanced (backline, 2.1 of 8), advanced (midline, 1.9 of 8), advanced (frontline, 0.9 of 8); named as {'already running, advanced': 285, 'held, advanced': 281, 'ran, advanced': 121}; win change 1.4 UNNAMED
- n 853: fell back (backline, 1.9 of 8), fell back (midline, 1.7 of 8), fell back (frontline, 0.7 of 8); named as {'held, fell back': 264, 'already running, fell back': 169, 'ran, fell back': 146}; win change 0.0 UNNAMED
*late game* (6 groups, separation 0.22):
- n 25: fought (midline, 2.3 of 8), fought (backline, 2.1 of 8), fought (frontline, 0.9 of 8); named as {'4+ at the enemy Lord': 9, '0 to 1 at the enemy Lord': 8, '2 to 3 at the enemy Lord': 8}; win change 1.5 UNNAMED
- n 25: advanced (backline, 2.2 of 8), advanced (midline, 1.1 of 8), advanced (frontline, 1.1 of 8), fought (backline, 0.6 of 8); named as {'2 to 3 at the enemy Lord': 13, '0 to 1 at the enemy Lord': 9, '4+ at the enemy Lord': 3}; win change 5.7 UNNAMED
- n 22: fell back (backline, 2.2 of 8), fell back (midline, 1.4 of 8), fell back (frontline, 1.1 of 8); named as {'0 to 1 at the enemy Lord': 11, '2 to 3 at the enemy Lord': 8, '4+ at the enemy Lord': 3}; win change -6.3 UNNAMED
- n 17: held (backline, 1.7 of 8), advanced (midline, 1.0 of 8), fell back (midline, 0.6 of 8); named as {'2 to 3 at the enemy Lord': 8, '0 to 1 at the enemy Lord': 6, '4+ at the enemy Lord': 3}; win change -1.9 UNNAMED
- n 5: advanced (midline, 4.6 of 8), fell back (backline, 0.8 of 8), advanced (backline, 0.8 of 8); named as {'2 to 3 at the enemy Lord': 3, '4+ at the enemy Lord': 2}; win change 12.6
- n 4: died (backline, 3.4 of 8), died (midline, 2.8 of 8), died (frontline, 1.8 of 8); named as {'2 to 3 at the enemy Lord': 2, '0 to 1 at the enemy Lord': 2}; win change -10.3 UNNAMED
*power play* (2 groups, separation 0.27):
- n 1712: fought (midline, 1.8 of 8), fought (backline, 1.6 of 8), fought (frontline, 1.0 of 8), held (backline, 0.7 of 8); named as {'pushed, fought': 430, 'held, fought': 293, 'held, fell back': 261}; win change 0.1 UNNAMED
- n 791: advanced (backline, 2.4 of 8), advanced (midline, 2.0 of 8), advanced (frontline, 1.1 of 8); named as {'pushed, advanced': 496, 'pushed, fought': 115, 'held, advanced': 60}; win change 1.4
*runner choice* (3 groups, separation 0.22):
- n 973: fought (backline, 1.9 of 8), fought (midline, 1.8 of 8), fought (frontline, 1.0 of 8), held (backline, 0.7 of 8); named as {'monk': 250, 'mesmer': 177, 'dervish': 160}; win change 0.4 UNNAMED
- n 737: fell back (backline, 1.5 of 8), fell back (midline, 1.3 of 8), held (backline, 0.7 of 8), fell back (frontline, 0.6 of 8); named as {'mesmer': 158, 'dervish': 134, 'monk': 134}; win change -0.6 UNNAMED
- n 665: advanced (backline, 2.2 of 8), advanced (midline, 1.7 of 8), advanced (frontline, 0.8 of 8), carrying (midline, 0.5 of 8); named as {'monk': 187, 'mesmer': 144, 'dervish': 102}; win change 0.1 UNNAMED
*split in base* (3 groups, separation 0.18):
- n 237: fought (midline, 2.1 of 8), fought (backline, 1.5 of 8), fought (frontline, 0.9 of 8), held (backline, 0.7 of 8); named as {'defended without a collapse': 125, 'collapsed': 84, 'missed': 28}; win change -1.4 UNNAMED
- n 151: advanced (midline, 1.8 of 8), advanced (backline, 1.6 of 8), advanced (frontline, 0.8 of 8); named as {'defended without a collapse': 70, 'collapsed': 61, 'missed': 20}; win change -0.9 UNNAMED
- n 144: fell back (midline, 1.9 of 8), fell back (backline, 1.9 of 8), fell back (frontline, 0.7 of 8), fought (backline, 0.5 of 8); named as {'collapsed': 70, 'defended without a collapse': 60, 'missed': 14}; win change -2.6 UNNAMED
*split or stay* (3 groups, separation 0.25):
- n 4892: fought (midline, 2.1 of 8), fought (backline, 2.0 of 8), fought (frontline, 1.1 of 8), held (backline, 0.8 of 8); named as {'stayed': 4525, 'split': 367}; win change -0.1
- n 2741: fell back (backline, 1.6 of 8), fell back (midline, 1.4 of 8), fell back (frontline, 0.7 of 8), held (backline, 0.6 of 8); named as {'stayed': 2481, 'split': 260}; win change -1.2
- n 2310: advanced (backline, 2.2 of 8), advanced (midline, 2.0 of 8), advanced (frontline, 0.9 of 8); named as {'stayed': 2004, 'split': 306}; win change 0.2

## 8. What results and causes are worth

Win points for the team it happened to, from 266 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. Both against matched moments without the event (same minute and win chance). A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 772 | +5.7 | +2.7 to +8.4 | +1.9 | yes |
| capture | 2464 | +2.2 | +1.8 to +2.5 | +2.8 | yes |
| capture: held longer | 2112 | +3.0 | +1.9 to +3.9 | +3.1 | yes |
| capture: overcapped within 10 s (Bounty, F36) | 352 | -2.3 | -8.2 to +4.2 | +0.9 | no |
| death (any) | 5259 | -8.6 | -9.8 to -7.4 | -4.5 | yes |
| death: against a spike build | 1610 | -7.8 | -11.1 to -4.0 | -4.3 | yes |
| death: against other builds | 3649 | -9.0 | -10.5 to -7.6 | -4.6 | yes |
| death: back within 20 s | 885 | -8.1 | -10.4 to -6.0 | -2.2 | yes |
| death: down 20 to 60 s | 1846 | -7.8 | -9.4 to -6.0 | -3.9 | yes |
| death: down 60 s or more | 2528 | -9.4 | -11.1 to -7.8 | -5.8 | yes |
| death: healer | 1782 | -8.6 | -10.2 to -6.9 | -4.5 | yes |
| death: healer in own base or pit, back within 15 s (possibly deliberate; energy not tracked) | 116 | -4.3 | -6.4 to -2.1 | -1.8 | yes |
| death: healer, other | 1666 | -8.9 | -10.6 to -7.4 | -4.6 | yes |
| death: not a healer | 3477 | -8.6 | -10.0 to -7.4 | -4.5 | yes |
| footman lost (base NPC) | 762 | -1.7 | -3.5 to -0.1 | -0.1 | yes |
| pit NPC lost (any): taken by a spike build | 506 | -4.6 | -9.2 to +0.3 | -2.2 | no |
| pit NPC lost (any): taken by other builds | 1648 | -5.9 | -7.8 to -4.3 | -2.7 | yes |
| pit NPC lost: archer | 1225 | -4.2 | -5.4 to -2.8 | -1.0 | yes |
| pit NPC lost: bodyguard | 288 | -5.6 | -7.1 to -4.1 | -1.9 | yes |
| pit NPC lost: knight | 641 | -8.4 | -9.8 to -7.1 | -5.7 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value. Context (strength, build skill counts, flag lead, morale, the clock) is left out: it describes the situation, it is not a cause to fix.

*deaths* (per 10 s in that state; result worth -8.6 points, base rate 1.5%):

- enemies within 1,500 7.5 to 8: result chance +2.8 points, worth -0.24 win points
- current health % 1 to 48.5: result chance +11.2 points, worth -0.97 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.6 points, worth -0.23 win points
- allies within 1,500 0 to 0.5: result chance +2.0 points, worth -0.18 win points
- own healers alive within cast range (other than the player) 3.5 to 4: result chance +0.4 points, worth -0.03 win points

*kill conversion* (per burst, for the attacking team; result worth +8.6 points, base rate 28.9%):

- target's healers in range 0 to 0.5: result chance +30.4 points, worth +2.62 win points
- target's health ceiling 0.4 to 0.56: result chance +37.8 points, worth +3.25 win points
- damage in the 2 s burst 506.5 to 840: result chance +25.8 points, worth +2.22 win points
- target health % when the burst started 0 to 38.5: result chance +30.8 points, worth +2.65 win points
- a prot on the target 0.5 to 1: result chance -6.7 points, worth -0.58 win points

*npc loss* (per case, for the defending team; result worth -5.6 points, base rate 19.9%):

- own players in the pit 7.5 to 8: result chance -15.4 points, worth +0.87 win points
- damage on the pit NPCs in the last 5 s 387.5 to 1370: result chance +37.3 points, worth -2.1 win points
- own players alive outside the pit 0 to 0.5: result chance +17.4 points, worth -0.98 win points
- attackers' measured damage per second against a Lord (benchmarks) 2.7 to 21.35: result chance -10.6 points, worth +0.6 win points
- of which healers 0 to 0.5: result chance +17.3 points, worth -0.97 win points
- enemy players in the pit 7.5 to 8: result chance +5.3 points, worth -0.3 win points
- healing on own pit NPCs and Lord in the last 10 s 623.5 to 1801: result chance -6.3 points, worth +0.36 win points

## The TQs

Denning's four questions, each from the batch's matches. The why comes from forensics and events (every number placed against the same role or situation in every stored match); the different play comes only from measurement: the usual play's choice effects (usual.py), node models read again with the variable changed (models that never saw the match, changes priced in win points with values.py), options that were ready and unused, and benchmarks. Points = win-chance points.

## TQ 1. Behind on flags

*The biggest flag swing in the new matches: cope +80 -> -83 by 22:55.0.*

### Flag swing: cope v hold (0ab1d6cd), 21:25.0 to 22:55.0
**Result**: cope's flag lead +80 s -> -83 s (-163 s). Stand: cope -> cope.
**Captures** (flag model: fastest possible answer after the enemy's capture):
- cope capped 21:24.0 by Mesmer, 75 s after hold's capture; fastest possible 29 s, so 46 s slower; enemies in the way {'Necromancer 1': 5, 'Stand Mes': 5, 'Ritualist': 5, 'Air Ele': 5}
- hold capped 23:06.0 by Air Ele, 102 s after cope's capture; fastest possible 49 s, so 53 s slower; enemies in the way {'Paragon 1': 25, 'Prot': 24, 'Warrior': 24, 'Paragon 2': 24}
**Runs** (each run: outcome, and what was done to the runner):
- cope Mesmer 20:32.0 to 21:24.0 (52 s): captured, lowest health 99%, escort ['Warrior', 'Paragon 1', 'Paragon 2', 'Prot', '7 Monk', '8 Monk'], pushed by nobody
- cope Monk 4 (WoC) 21:32.0 to 22:09.0 (37 s): dropped, lowest health 77%, escort none, pushed by nobody
- hold Stand Mes 22:43.0 to 22:43.0 (0 s): dropped, lowest health 80%, escort ['Air Ele', 'Necromancer 1', 'Necromancer 2', 'Prot', 'Ritualist'], pushed by nobody
- hold Air Ele 22:48.0 to 23:06.0 (18 s): captured, lowest health 95%, escort ['Ritualist'], pushed by nobody
**Deaths in the window**: 22:40.0 cope Paragon 2 (backside, [8, 8]); 22:40.0 cope Prot (backside, [7, 8]); 22:40.0 cope 7 Monk (backside, [8, 8]); 22:45.0 cope Monk 4 (WoC) (backside, [4, 8]); 22:48.0 cope Warrior (backside, [2, 8]); 22:52.0 cope Mesmer (push side, [1, 8])
- cope output in the 20 s before 22:40.0: 67.7 damage per second (above the 80th percentile for team (median 39.1, n 11875)), top target share 0.47, spikes 1
- hold output in the 20 s before 22:40.0: 93.4 damage per second (above the 90th percentile for team (median 39.1, n 11875)), top target share 0.26, spikes 0
**Why cope Paragon 2 died at 22:40.0** (forensics):
  - Position: partly (in the last 3 s: nearest allied healer 142, nearest enemy 160, allies in casting range 6.5, enemies 8.0; over the whole window the nearest enemy's median was 212)
  - Prots: late or interrupted (0 from teammates, 1 self; 1 of 1 landed); damage 297 (0% attacks, 58% armor-ignoring), burst 120 in 2 s at 22:24.2; ready and in range but not used: cope Prot Shielding Hands, cope 7 Monk Guardian, cope 8 Monk Protective Spirit
  - Healers under interrupt pressure: yes (healers 3, interrupts_per_min 6.0, interrupted 2, casts 20, finished_share 0.8, dazed 0, knockdowns 0, hexes 9)
  - Damage off shield sets: usual (team share 0.18, a shield would have stopped about 35)
  - Own damage: yes (69.0 per second on [('hold Air Ele', 630), ('hold Necromancer 1', 319)]); enemy damage: high (103.2 per second)
  - Peel: no (peel on a burst is rare: most bursts on this role get none) (0 of 3 attackers controlled; longest free 15.4 s)
  - Casting: unclear (casts 1, interrupted 0, cancelled 0, while_dazed 0)
**Why cope Prot died at 22:40.0** (forensics):
  - Position: no (in the last 3 s: nearest allied healer 164, nearest enemy 388, allies in casting range 6.5, enemies 8.0; over the whole window the nearest enemy's median was 443)
  - Prots: yes (1 from teammates, 0 self; 1 of 1 landed); damage 319 (0% attacks, 55% armor-ignoring), burst 104 in 2 s at 22:40.1; ready and in range but not used: cope 7 Monk Guardian
  - Healers under interrupt pressure: yes (healers 3, interrupts_per_min 6.0, interrupted 2, casts 20, finished_share 0.8, dazed 0, knockdowns 0, hexes 9)
  - Damage off shield sets: usual (team share 0.18, a shield would have stopped about 35)
  - Own damage: yes (69.0 per second on [('hold Air Ele', 630), ('hold Necromancer 1', 319)]); enemy damage: high (103.2 per second)
  - Peel: no (peel on a burst is rare: most bursts on this role get none) (0 of 4 attackers controlled; longest free 15.4 s)
  - Casting: usual; cancelled more than usual (casts 6, interrupted 0, cancelled 1, while_dazed 0)
**After**: 23:11.0 cope Paragon 1; 23:17.0 cope 8 Monk
**Why, in short**: cope's Monk 4 (WoC) dropped the flag at 22:09 after 37 s of carrying, 6 s from capturing (main 7v8, alive 8v8); hold capped at 23:06, 102 s after cope's capture, on its 2nd run (1 dropped); cope pushed the last carrier with nobody but its health never went below 95%; deaths in the window: cope 6.

**How it got there, from the node models** (step 4: each link read by the node's held-out model; the biggest pushes toward the result, against the variable's usual value over every trained moment; a variable that is another node's result is followed back to it):
- 22:20 flag swing: flag lead change over 60 s -35.3 s; pushed by flag lead now (s) 80 (usual 0): +16.2 s; morale, own minus enemy (discovery, approved) -288 (usual 0): +12.9 s; own team holds the stand 1 (usual 0): +5.1 s
*Fixes carried forward*: none worth half a win point at the result.

**A different play (measured)**

*The decisions in the swing* (usual.py: win-chance points over the decision's window, against the kind's most common choice):
- split or stay at 21:00 (main 7v8, flags -1 s, boost in 70, fight state 0.0): chose **stayed** (+0.0 [+0.0, +0.0] against the most common choice, stayed); in the 15 most similar decisions teams usually chose **stayed**; no choice of this kind did measurably better than the one made.
- split or stay at 21:30 (main 6v5, flags +80 s, boost in 114, fight state 0.003): chose **stayed** (+0.0 [+0.0, +0.0] against the most common choice, stayed); in the 15 most similar decisions teams usually chose **stayed**; no choice of this kind did measurably better than the one made.
- runner choice at 21:32 (main 6v5, flags +80 s, boost in 112, fight state 0.003): chose **monk** (+0.0 [+0.0, +0.0] against the most common choice, monk); in the 15 most similar decisions teams usually chose **mesmer**; measured better: **assassin** (+3.7 points against the choice made, not clear yet, n 8).

**Confidence**: low (measured, but the ranges include no effect yet).

## TQ 2. A monk death

*The monk death that cost the most win chance in the new matches: Crew v hook (07b6b99a), Crew 8 Monk at 25:14 (own pit, numbers [6, 5]); win chance -52.1 points from 10 s before to 30 s after.*

**Why** (forensics, against the same role in every stored match):
- Position: partly (in the last 3 s: nearest allied healer 681, nearest enemy 566, allies in casting range 1.0, enemies 4.5; over the whole window the nearest enemy's median was 440)
- Prots: yes (0 from teammates, 1 self; 1 of 1 landed); damage 702 (24% attacks, 46% armor-ignoring), burst 216 in 2 s at 25:12.5; ready and in range but not used: Crew Prot Guardian
- Healers under interrupt pressure: usual (healers 3, interrupts_per_min 3.0, interrupted 1, casts 17, finished_share 0.94, dazed 0, knockdowns 1, hexes 6)
- Damage off shield sets: usual (team share 0.29, a shield would have stopped about 49)
- Own damage: usual (35.3 per second on [('hook 8 Monk', 605), ('hook Prot', 101)]); enemy damage: usual (58.4 per second)
- Peel: no (peel on a burst is rare: most bursts on this role get none) (0 of 4 attackers controlled; longest free 20.0 s)
- Casting: interrupted far more than usual (casts 8, interrupted 1, cancelled 0, while_dazed 0)
**Why, in short**: the 8 Monk died because its casts were interrupted (1 of 8), position (in contact with the enemy, nearest enemy 566 in the last 3 s), its attackers were not peeled (no (peel on a burst is rare: most bursts on this role get none)).

**How it got there, from the node models** (step 4: each link read by the node's held-out model; the biggest pushes toward the result, against the variable's usual value over every trained moment; a variable that is another node's result is followed back to it):
- 24:39 fight outcome: won the fight 14.8%; read from hook's side (own = hook); pushed by morale, own minus enemy (discovery, approved) 113 (usual 0): +51.5 points; stand (discovery, approved) 1 (usual 0): +7.8 points; value of enchantments stripped per 10 s, own minus enemy 5.68 (usual 0): +2.6 points
*Fixes carried forward*: none worth half a win point at the result (closest: value of enchantments stripped per 10 s, own minus enemy at 24:39 5.68 -> 0: +0.1 at its own node, 0.1 carried to the result; share of strips on the best target in range, own minus enemy at 24:39 1 -> 0: +0.1 at its own node, 0.1 carried to the result).

**How it could have been prevented (measured)**

- Further back: the fixes along the chain are priced above ("Fixes, carried forward"). The readings below are what was still possible in the last seconds.
- Ready and in range but not used: Crew Prot Guardian (casting nothing)
- Attackers left free (no snare, Blind, Weakness, interrupt, knockdown or hex from its team): hook Hammer 20.0 s free (nearest own non-healer 14944); hook Fire Ele 20.0 s free (nearest own non-healer 14695); hook Mesmer 20.0 s free (nearest own non-healer 15106)
- Deaths node at 25:10 (AUC 0.925 on unseen matches against 0.79 for health_pct and damage_taken_3s alone): risk 12.9% of dying in the next 10 s; read again with
  - staying with its group: 12.7% (-0.2 points of risk; at this death's measured cost of -52.1 win points, about +0.1 expected; at a typical healer death's -8.6, +0.0)
  - one attacker peeled off: 13.4% (+0.5 points of risk; at this death's measured cost of -52.1 win points, about -0.3 expected; at a typical healer death's -8.6, -0.0)
  - its hexes removed: 11.0% (-1.9 points of risk; at this death's measured cost of -52.1 win points, about +1.0 expected; at a typical healer death's -8.6, +0.2)
  - all of these together: 11.3% (-1.6 points of risk; at this death's measured cost of -52.1 win points, about +0.8 expected; at a typical healer death's -8.6, +0.1)

**Confidence**: low (measured, but the ranges include no effect yet).

## TQ 3. A power play without a kill

*The power play without a kill that cost the most win chance in the new matches: main 7v4, pushed, no kill in 57 s; win chance -34.8 points over it.*

### Power play without a kill: RV v DUM (b3621d94), 0:35.0 to 1:32.0
**Situation**: main 7v4, alive 8v7, flags even (+1 s), DP 0, boost in None; choice pushed (fought 4, advanced 2, died 1, held 1); deaths {'RV': 2, 'DUM': 0} in 57 s
**The fight's shape** (every 5 s: own main, the enemy group it faced, distance between them, that group's distance to the rest of its team): 0:35.0 7v4 1723 apart, 1534 from its others; 0:40.0 7v5 130 apart, 8534 from its others; 0:45.0 7v5 88 apart, 8598 from its others; 0:50.0 7v5 92 apart, 8061 from its others; 0:55.0 6v5 70 apart, 7289 from its others; 1:00.0 6v5 69 apart, 6691 from its others; 1:05.0 6v5 85 apart, 5452 from its others; 1:10.0 6v5 85 apart, 4718 from its others; 1:15.0 5v5 107 apart, 4618 from its others; 1:20.0 5v5 103 apart, 4543 from its others; 1:25.0 6v5 75 apart, 4786 from its others; 1:30.0 6v5 178 apart, 4139 from its others
**RV's damage**: 16.4 per second (below the 20th percentile for team (median 39.1, n 11875)); top target share 0.56 (above the 50th percentile for team (median 0.48, n 11875)); targets [('DUM Dervish 1', 524), ('DUM Dervish 2', 203), ('DUM Hammer', 168), ('DUM Monk 5', 38)]; dealers [('RV Monk 5 (WoC)', 420), ('RV Paragon 2', 342), ('RV Warrior', 134), ('RV Paragon 1', 37)]
- phase 0:33.0 to 0:41.0: 7v5 (stand, job convert), damage uptime 0.33, damage-seconds lost {'moving': 18, 'carrying': 8, 'idle': 1}
- phase 0:41.0 to 0:52.0: 7v5 (stand, job convert), damage uptime 0.51, damage-seconds lost {'moving': 16, 'blind': 6, 'idle': 5}
- phase 0:52.0 to 1:11.0: 6v5 (stand, job convert), damage uptime 0.55, damage-seconds lost {'moving': 16, 'knocked down': 10, 'idle': 5, 'blind': 3}
- phase 1:11.0 to 1:24.0: 5v5 (stand, job contest), damage uptime 0.69, damage-seconds lost {'moving': 11, 'idle': 1}
- phase 1:24.0 to 1:35.0: 6v5 (stand, job convert), damage uptime 0.25, damage-seconds lost {'moving': 12, 'knocked down': 10, 'blind': 10, 'idle': 1}
**DUM's answer**: healing 71 per second ({'DUM Ritualist': 1789.7000000000005, 'DUM Prot': 1082.9, 'DUM Monk 5': 736, 'DUM Air Ele': 454}); prots {'Shielding Hands': 2, 'Shield Guardian PvP': 2, 'Guardian': 1}
- RV's knockdowns landed 1; DUM's knockdown immunity casts 0
- Pressure on DUM's healers: healers 2, interrupts_per_min 0.0, interrupted 0, casts 14, finished_share 0.86, dazed 0, knockdowns 0, hexes 0 (around the median for team (median 0, n 13441))
- Snares, Blind and Weakness RV put on DUM: none
**Where the power play came from** (why the enemy was short, player-seconds over it): push side 17, enemy base 9, stand 1
**Why, in short**: RV had 7v4 at main for 57 s; DUM healed 71 per second; worse than in power plays that killed: damage 16.4 per second (killing 40.1, not killing 23.6), top-target share 0.56 over 4 targets (killing 0.4, not killing 0.45); not the cause (on the side of power plays that killed): damage uptime in contact 51% (killing 47%, not killing 36%; most lost to moving).

**How it got there, from the node models** (step 4: each link read by the node's held-out model; the biggest pushes toward the result, against the variable's usual value over every trained moment; a variable that is another node's result is followed back to it):
- 0:35 power play: killed on the power play 8.8%; pushed by own damage per second against the usual of the players alive 0.32 (usual 1.46): +40.0 points; in a base or pit 0.33 (usual 0): +3.9 points; seconds own attackers spent Blind, per 10 s 2.95 (usual 0): +3.6 points
*Fixes, carried forward to the result* (the variable set to its usual value, the node read again, the change carried link by link and priced with values.py):
- own damage per second against the usual of the players alive at 0:35: 0.32 -> 1.46; power play +33.3; worth +2.9 win points at the result

**How it could have been converted (measured)**

- Against every stored power play (3+ up): those that killed had a median 40.1 damage per second and top-target share 0.4 (128 cases); those that didn't, 23.6 and 0.45 (105 cases). RV here: 16.4 and 0.56. Damage uptime: 47% in those that killed, 36% in those that didn't, 51% here.
- No burst (a 2 s burst that the kill-conversion node reads) in the window: the damage never came together on one target.
- The choice at the power play (usual.py):
  - power play at 0:35 (main 7v4, flags +1 s, boost in None, fight state 0.256): chose **pushed, advanced** (+0.0 [+0.0, +0.0] against the most common choice, pushed, advanced); in the 15 most similar decisions teams usually chose **pushed, advanced**; no choice of this kind did measurably better than the one made.

**Confidence**: low (the engine can't price an alternative here yet).

## TQ 4. Pit NPCs lost

*The NPC loss that cost the most win chance in the new matches: Free lost knight (converted from the fight at 6:11) at 6:14; win chance -40.7 points from 20 s before to 20 s after.*

### Pit NPCs lost: Free v DMG (d9e8531e) around 6:14.0
**Lost**: 6:14.0 knight (converted from the fight at 6:11); 6:24.0 knight (converted from the fight at 6:11)
**DMG's split** 4:55.0 to 5:57.0: ['7 Monk (WoC)', 'Dervish 2'] (split), entered base no, NPC damage {'footman': 779}, NPC kills []
- defender Monk 5 (WoC): first 5:30.0 (latency 35 s, from field), 27 s defending
- defender 8 Monk: first 5:35.0 (latency 40 s, from field), 19 s defending
- defender Prot (WoC): first 5:50.0 (latency 55 s, collapse from main), 7 s defending
- defender Monk 1 (WoC): first 5:52.0 (latency 57 s, collapse from main), 6 s defending
- defender Monk 3 (WoC): first 5:52.0 (latency 57 s, collapse from main), 6 s defending
- main numbers meanwhile [4.6, 6.5]
**Free at 6:14.0**: Monk 1 (WoC): backside (free); Monk 2 (WoC): backside (free); Monk 3 (WoC): backside (free); Monk 4 (WoC): backside (free); Monk 5 (WoC): own base (defend); Prot (WoC): backside (free); Mesmer: backside (free); 8 Monk: own base (defend)
- DMG output 4:55.0 to 5:57.0: 0.7 per second
- Free output 4:55.0 to 5:57.0: 15.1 per second
**Why, in short**: DMG split 7 Monk (WoC)+Dervish 2 into Free's base; at 6:11 the pit had 1 attackers against 1 defenders (0 of them healers), with 7 of Free elsewhere.

**How it got there, from the node models** (step 4: each link read by the node's held-out model; the biggest pushes toward the result, against the variable's usual value over every trained moment; a variable that is another node's result is followed back to it):
- 6:14 pit npc loss: lost a pit NPC within 15 s 37.7%; pushed by damage on the pit NPCs in the last 5 s 337 (usual 0): +48.5 points; own players in the pit 2 (usual 3): +7.2 points; of which healers 1 (usual 2): +4.6 points
*Fixes, carried forward to the result* (the variable set to its usual value, the node read again, the change carried link by link and priced with values.py):
- damage on the pit NPCs in the last 5 s at 6:14: 337 -> 0; pit npc loss -31.4; worth +1.9 win points at the result

**How it could have been prevented (measured)**

- First defender: 35 s after the split started; the split never entered the base, so the benchmark for splits into a base doesn't apply.
- NPC-loss node at 6:11 (AUC 0.85 on unseen matches against 0.757 for attackers and defenders alone): 1 attackers (0 healers) against 1 defenders (0 healers), 7 of Free elsewhere; read 54.7% to lose an NPC; read again with
  - one more defender: 51.3% (-3.4 points; at this loss's measured cost of -40.7 win points, about +1.4 expected; at a typical NPC loss's -5.6, +0.2)
  - one more defender, a healer: 29.2% (-25.5 points; at this loss's measured cost of -40.7 win points, about +10.4 expected; at a typical NPC loss's -5.6, +1.4)
  - two more defenders: 46.4% (-8.3 points; at this loss's measured cost of -40.7 win points, about +3.4 expected; at a typical NPC loss's -5.6, +0.5)
  - healing on the NPCs (as much as the attackers' damage in 5 s): 45.6% (-9.1 points; at this loss's measured cost of -40.7 win points, about +3.7 expected; at a typical NPC loss's -5.6, +0.5)

**Confidence**: medium (one measurement supports it).

## 9. Detailed learnings snapshot

Descriptive measurements across all 266 trained matches (the latest batch, 45 matches, in brackets where it differs). Not causal on their own: they point to questions and candidate variables.

**Runners** (spawn to capture; pushed = an enemy hit the carrier; holds = carries of 10 s+ that never closed a quarter of the way to the stand, kept out of runs and captured, Denning: an 8 Monk may hold without trying to cap):

| Runner | Runs | Holds | Captured | Median s to capture | Dropped | Pushed | Runs by eventual winners (includes who was ahead) |
|---|---|---|---|---|---|---|---|
| Ritualist | 465 | 35 | 50% | 36 (33.5) | 223 | 39% | 55% |
| Mesmer | 410 | 27 | 56% | 37 (40.5) | 166 | 43% | 50% |
| Mes/A | 394 | 34 | 57% | 38 (34) | 156 | 45% | 52% |
| AoB Derv | 375 | 32 | 63% | 30 (29) | 135 | 38% | 50% |
| Hammer | 346 | 18 | 50% | 26.0 (26.0) | 171 | 36% | 58% |
| Dervish | 291 | 12 | 64% | 29 (32) | 99 | 47% | 39% |
| Monk 4 (WoC) | 252 | 16 | 69% | 35.0 (26) | 74 | 49% | 56% |
| 8 Monk | 221 | 32 | 34% | 34 (33) | 143 | 20% | 61% |
| Necromancer | 165 | 6 | 68% | 35.0 (41) | 50 | 48% | 48% |
| Monk 5 (WoC) | 155 | 8 | 69% | 39 (40) | 46 | 46% | 47% |

Double running: single 3550 runs (49% by eventual winners, includes who was ahead); half 1052 runs (50% by eventual winners, includes who was ahead).
Winners against losers below are compared at moments when a win model that never saw the match gave the team 35 to 65% (so the gap is not just who was already ahead), with every moment beside it, labelled.


**Flag answers** (answering the enemy's capture): winners at even win chance: 329 answers, median 44 s, 13 s slower than possible, 104 answers 30 s+ slower; losers at even win chance: 339 answers, median 42 s, 11 s slower than possible, 102 answers 30 s+ slower; winners every moment (includes who was ahead): 1132 answers, median 38.0 s, 10.0 s slower than possible, 299 answers 30 s+ slower; losers every moment (includes who was ahead): 1068 answers, median 52.0 s, 18.0 s slower than possible, 424 answers 30 s+ slower.

**Skills: kill participation** (share of casts at an enemy who died within 5 s; 15+ casts):

- Highest: Forked Arrow 58% of 45; Deep Freeze 50% of 22; Twisting Fangs 32% of 116; Mark of Fury 29% of 17; Jungle Strike 28% of 36; Falling Lotus Strike 28% of 110; Vapor Blade 27% of 230; Wounding Strike PvP 27% of 63; Shadow Shroud PvP 25% of 177; Invoke Lightning 24% of 2895; Leaping Mantis Sting 22% of 198; Harriers Toss PvP 22% of 41
- Lowest: Chaos Storm 0% of 65; Debilitating Shot 0% of 29; Star Burst 0% of 16; Shared Burden PvP 0% of 32; Expunge Enchantments 0% of 19; Lightning Orb 0% of 35; Symbols of Inspiration 0% of 20; Images of Remorse 0% of 16

**Interrupts:** skills interrupted most (whose): Healing Burst on the 7 Monk 933; Blessed Light on the 8 Monk 606; Guardian on the Prot 579; Guardian on the 8 Monk 551; Guardian on the 7 Monk 510; Spirit Light Weapon on the Ritualist 509; Shield Guardian PvP on the Prot 395; Shield Guardian PvP on the 7 Monk 317; Lightning Strike on the Air Ele 313; Cure Hex on the 7 Monk 308. Interrupt skills landing most: Power Spike 3894; Complicate 3817; Power Leak 1670; Psychic Instability PvP 1472; Cry of Frustration 1214; Savage Shot 1083; Hammer Bash 739; Distracting Shot 675.

**Knockdowns by skill:** Coward 4410; Hammer Bash 4275; Psychic Instability PvP 1653; Lightning Surge 1377; Mind Shock PvP 866; Bull's Strike 850; Bane Signet 754; Shove 708.

**Spikes survived** (400+ damage in 3 s on one player; survived = alive 8 s later): losers (every moment, includes who was ahead) 940 of 1591 (59%); losers at even win chance 169 of 238 (71%); winners (every moment, includes who was ahead) 771 of 970 (79%); winners at even win chance 165 of 204 (81%). By target: Prot 64% of 313; 7 Monk 65% of 272; Mesmer 75% of 264; 8 Monk 54% of 201; Stand Mes 70% of 179; AoB Derv 70% of 168; Mes/A 75% of 145; Paragon 78% of 141; Warrior 69% of 117; Air Ele 58% of 110; Ritualist 65% of 96; Hammer 66% of 85; Dervish 64% of 84; Necromancer 47% of 75; Monk 5 (WoC) 82% of 55; Monk 4 (WoC) 74% of 50; Ranger 59% of 39; Fire Ele 58% of 31; Monk 54% of 28; Assassin 73% of 26; Water Ele 62% of 26; Monk 3 (WoC) 81% of 21; Ele 80% of 10.

**Monks** (per 2-minute phase alive 60 s+): winners at even win chance: 12.5 casts a minute, 0.55 fakes, idle 0 s while an ally was hurt, reaction 1.4 s, bursts answered 73%; losers at even win chance: 12.5 casts a minute, 0.46 fakes, idle 0 s while an ally was hurt, reaction 1.5 s, bursts answered 65%; winners every moment (includes who was ahead): 11.5 casts a minute, 0.51 fakes, idle 0 s while an ally was hurt, reaction 1.4 s, bursts answered 71%; losers every moment (includes who was ahead): 12.0 casts a minute, 0.51 fakes, idle 1 s while an ally was hurt, reaction 1.4 s, bursts answered 60%.

**Deaths** (4609): 1475 with a knockdown on the victim; 1473 had a monk cast on the victim in the last 5 s. Monk skills interrupted in the 6 s before a death: Blessed Light 231; Healing Burst 195; Guardian 157; Shield Guardian PvP 89; Reversal of Fortune 56; Cure Hex 42; Patient Spirit 38; Word of Healing 36.

## 10. For Denning

- Which curves look wrong to you? A correction (direction, cap, drop, or a pair to always test) is logged with your reason and tested on held-out matches.
- Do any surprises remind you of something the variables don't capture (a missing variable)?
- Any variable you think matters that isn't listed?

