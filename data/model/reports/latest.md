# Learning report, batch 17

Trained on 506 matches (60 new in this batch). Variables in use: 33; build variables from 60 matches, interactions from 40.

## 0. Data integrity

- Lengths repaired: 19 (1f65fd3b 150 s -> 1027 s) (bbef1904 617 s -> 599 s) (36a65ac6 1319 s -> 1294 s) (ba85aafc 811 s -> 793 s) (f9d6932f 235 s -> 218 s) (82fa12be 488 s -> 467 s) (cf2968cd 178 s -> 363 s) (713d9cd0 376 s -> 353 s) (366b75bc 667 s -> 650 s) (90ad5f3b 167 s -> 651 s) (dc8e5146 175 s -> 321 s) (149fbdc6 700 s -> 676 s) (1796f9bc 1679 s -> 1661 s) (681495c7 153 s -> 980 s) (74be0781 247 s -> 231 s) (74e9e7f5 1195 s -> 1178 s) (81c3fba6 337 s -> 320 s) (9b962f38 338 s -> 318 s) (ad5a505f 718 s -> 700 s) 
- Matches with a team's Lord damage not observed (left blank, not zero): 35
- Pit NPCs added from the standard roster (never seen in the replay): 1760 in 438 matches
- Left out of training: 0

## 1. The honest test

**Beats strength alone (clear: the range excludes 0).** Held-out accuracy (matches held out whole), log loss in brackets (lower is better):

- strength only: all 78% (0.475), 0-5 min 83% (0.386), 5-10 min 80% (0.451), 10-15 min 75% (0.548), 15-end min 71% (0.599), matches lasting 15 min+ 73% (0.584), matches even on strength (gap under 200) 64% (0.632)
- glass box: all 84% (0.382), 0-5 min 84% (0.36), 5-10 min 85% (0.355), 10-15 min 82% (0.429), 15-end min 83% (0.414), matches lasting 15 min+ 80% (0.465), matches even on strength (gap under 200) 76% (0.517)
- glass box without corrections: all 84% (0.392), 0-5 min 84% (0.375), 5-10 min 84% (0.374), 10-15 min 82% (0.434), 15-end min 83% (0.408), matches lasting 15 min+ 80% (0.46), matches even on strength (gap under 200) 76% (0.533)
- black box: all 81% (0.563), 0-5 min 82% (0.52), 5-10 min 82% (0.53), 10-15 min 80% (0.612), 15-end min 79% (0.636), matches lasting 15 min+ 77% (0.701), matches even on strength (gap under 200) 71% (0.74)
- By month played (glass box against strength alone, log loss; matches): 2026-09 0.425 v 0.54 (236); 2026-10 0.356 v 0.434 (217); 2026-11 0.289 v 0.353 (53)
- By strength band (glass box against strength alone, log loss; matches): even (gap under 200) 0.517 v 0.632 (145); moderate (200 to 600) 0.37 v 0.475 (265); uneven (600+) 0.074 v 0.066 (96)
- Gain over strength alone (log loss, resampling whole matches): +0.094 (90% range +0.057 to +0.133).
- Change since batch 16: glass box log loss 0.355 -> 0.382; strength only 0.47 -> 0.475.
- Cap test on spike_killable_diff (held-out log loss, 506 matches): none 0.3816, 10 points 0.3832, 15 points 0.3821, 20 points 0.3817, 25 points 0.3816; chosen: no cap (no option beat it on unseen matches).
- Pair test (morale_diff with map_flag_run, map_pit_to_stand, map_bases_apart; morale_total with map_flag_run, map_pit_to_stand, map_bases_apart; held-out log loss, 506 matches): allowed 0.3816, blocked 0.3853; chosen: allowed (blocking didn't predict unseen matches better).
- Calibration by minute (held-out predictions on 506 matches; pooled cells joined by straight lines, blended by minute; every win chance below and in values, usual play and the TQs goes through it). Predicted -> how often those teams won -> calibrated:
  - 0 to 6 min: 0.6% -> won 1.0% (292 matches) -> 1.0%; 3.3% -> won 4.4% (266 matches) -> 4.4%; 42.6% -> won 42.5% (170 matches) -> 42.5%; 57.3% -> won 58.2% (174 matches) -> 58.1%; 92.6% -> won 92.1% (288 matches) -> 92.1%; 99.4% -> won 98.9% (287 matches) -> 98.9%
  - 6 to 12 min: 0.6% -> won 2.1% (279 matches) -> 2.0%; 3.3% -> won 6.2% (163 matches) -> 6.1%; 42.5% -> won 45.1% (107 matches) -> 45.0%; 57.6% -> won 56.3% (110 matches) -> 56.4%; 92.7% -> won 87.5% (179 matches) -> 87.7%; 99.4% -> won 97.6% (274 matches) -> 97.6%
  - 12 to 18 min: 0.6% -> won 4.8% (157 matches) -> 4.6%; 3.3% -> won 8.2% (106 matches) -> 8.0%; 42.2% -> won 40.3% (63 matches) -> 46.7%; 57.8% -> won 57.3% (65 matches) -> 57.3%; 92.7% -> won 79.3% (102 matches) -> 79.9%; 99.4% -> won 95.0% (158 matches) -> 95.1%
  - 18 to end min: 0.5% -> won 3.8% (127 matches) -> 3.7%; 3.3% -> won 12.5% (84 matches) -> 12.0%; 42.3% -> won 48.3% (47 matches) -> 47.7%; 58.1% -> won 49.7% (47 matches) -> 50.5%; 92.6% -> won 78.9% (76 matches) -> 79.7%; 99.4% -> won 96.4% (125 matches) -> 96.5%

## What changed since the last batch

- Learned-node links: 22 status changes since 2026-11-08: run_outcome P.10 -> R.3: rejected -> supported (+0.0025); run_outcome K.11 -> R.3: not clear yet -> rejected (-0.001); run_outcome C.map -> R.3: not clear yet -> supported (+0.0031); flag_swing A.allocation -> R.3: rejected -> not clear yet (-0.01); flag_swing C.clock -> R.3: rejected -> not clear yet (-0.01); flag_swing C.map -> R.3: rejected -> not clear yet (-0.01); run_defence P.10 -> R.3: not clear yet -> supported (+0.0011); run_defence C.map -> R.3: not clear yet -> supported (+0.0036); capture_speed K.11 -> R.3: rejected -> not clear yet (+0.0); power_play P.1 -> K.4: not clear yet -> supported (+0.0071); split_chance C.builds -> A.allocation: not clear yet -> supported (+0.01); split_chance C.strength -> A.allocation: rejected -> not clear yet (-0.0001); split_effect P.11 -> R.5: not clear yet -> supported (+0.0029); split_effect A.allocation -> R.5: not clear yet -> supported (+0.0028); split_effect C.strength -> R.5: rejected -> not clear yet (-0.0016); pit_npc_loss A.allocation -> R.5: not clear yet -> supported (+0.003); pit_npc_loss S.scoreboard -> R.5: not clear yet -> supported (+0.0054); pit_npc_loss K.6 -> R.5: not clear yet -> supported (+0.0006); pit_npc_loss C.builds -> R.5: not clear yet -> supported (+0.0029); pit_npc_loss C.clock -> R.5: rejected -> supported (+0.0021); collapse K.5 -> R.1: not clear yet -> supported (+0.002); collapse C.strength -> R.1: not clear yet -> supported (+0.0111).
- Links measured for the first time: run_defence K.5 -> R.3, power_play P.24 -> K.4, power_play P.25 -> K.4, power_play P.26 -> K.4, power_play P.22 -> K.4, power_play P.21 -> K.4, power_play P.23 -> K.4, power_play C.builds -> K.4, fight_outcome P.21 -> R.2, fight_outcome P.22 -> R.2, fight_outcome P.23 -> R.2, fight_outcome P.24 -> R.2....
- Links held as the enemy's concurrent response (measured, not fitted): K.5 -> K.4; K.1 -> R.5; P.21 -> K.4; P.23 -> K.4.
- Inputs that mark the situation (never a fix): fight_outcome castprev_diff, power_play degen_10s.

## 2. What it leans on

- **morale_diff** 0.8 (was 0.828): own minus enemy morale summed over players (boosts +, death penalty -)
- **knights_diff** 0.405 (was 0.367): own minus enemy pit knights alive
- **footmen_lost_diff** 0.232 (was 0.322): own minus enemy footmen lost so far (base NPCs, not pit NPCs). Proposed 2026-11-06 from OG comms ([ohno v NwAy]: 'this way we don't lose footmen'); moved in as footmen alive after chunk 4, then counted as losses after chunk 5 (Denning): a footman only enters the replay once something touches it, so 'alive' marked a base that was visited and read backwards (-42 points at +4); deaths are always recorded
- **stand** 0.184 (was 0.199): who holds the flag stand: 1 own, 0 nobody, -1 enemy
- **lord_dps_enemy** 0.174 (was 0.185): enemy build's measured Lord damage per second
- **lord_dps_own** 0.172 (was 0.186): own build's measured Lord damage per second if all its non-healers were at the Lord
- **alive_diff** 0.145 (was 0.136): own minus enemy players alive
- **lord_damage_diff & map_bases_apart** 0.144 (was 0.145): own minus enemy Lord damage dealt so far (the 28:00 tiebreak; players can't see it); blank when either team's Lord damage wasn't observed TOGETHER WITH the map's distance between the two bases
- **fight_state** 0.143 (was 0.19): who is winning the fight now: enemy minus own expected deaths in the next 10 s, from a deaths model that never saw the match (fightstate.py)
- **flag_lead** 0.137 (was 0.159): seconds up (+) or down (-) on flags: enemy's response minus own on the next capture exchange
- **down_diff_s** 0.131 (was 0.134): enemy minus own seconds until all dead players are back (+ = the enemy has more time down)
- **spike_killable_diff** 0.11 (was 0.194): enemy minus own players within one spike of the other side (DP stacking; 0 unless a spike build is involved)

## 3. The curves in words

Points = win-chance points added to an otherwise even game at each range of the variable.

- **morale_diff** rises from -44.8 to +39.1 points (-485.0..-210.5: -44.8; -154.5..-110.5: -20.8; -79.5..-45.5: -16.4; -15.5..-0.5: -5.3; 0.5..17.5: +7.7; 52.5..90.5: +18.3; 134.5..196.5: +25.4)
- **knights_diff** rises from -25.9 to +26.3 points (-2.0..-1.5: -25.9; -1.5..-0.5: -18.0; -0.5..0.5: -0.1; 0.5..1.5: +18.0; 1.5..2.0: +26.3)
- **footmen_lost_diff** rises from -31.1 to +31.5 points (-4.0..-3.5: -31.1; -3.5..-2.5: -31.1; -2.5..-1.5: -10.4; -1.5..-0.5: -10.1; -0.5..0.5: +0.1; 0.5..1.5: +9.8; 1.5..2.5: +10.3; 2.5..3.5: +31.4; 3.5..4.0: +31.5)
- **stand** rises from -5.0 to +5.0 points (-1.0..-0.5: -5.0; -0.5..0.5: +0.1; 0.5..1.0: +5.0)
- **lord_dps_enemy** is flat from -5.0 to -5.0 points (45.5..77.6: -5.0; 82.65..84.05: -3.1; 86.9..91.25: +4.2; 94.75..96.2: +5.0; 96.85..96.95: +2.9; 100.55..106.65: +5.0; 112.35..126.75: -5.0)
- **lord_dps_own** is flat from +5.0 to +5.0 points (45.5..77.6: +5.0; 82.65..84.05: +2.8; 86.9..91.25: -4.3; 94.75..96.2: -4.9; 96.85..96.95: -3.2; 100.55..106.65: -5.0; 112.35..126.75: +5.0)
- **alive_diff** rises from -22.8 to +20.3 points (-8.0..-6.5: -22.8; -4.5..-3.5: -16.4; -2.5..-1.5: -8.3; -0.5..0.5: -0.1; 1.5..2.5: +8.8; 3.5..4.5: +16.8)
- **lord_damage_diff & map_bases_apart** (interaction): see wp_model.md
- **fight_state** rises from -10.9 to +11.3 points (-3.98..-0.37: -10.9; -0.16..-0.08: -4.1; -0.04..-0.02: -1.5; -0.01..-0.0: -0.6; 0.01..0.02: +0.4; 0.04..0.08: +2.4; 0.16..0.37: +5.6)
- **flag_lead** rises from -12.5 to +12.6 points (-140.0..-62.5: -12.5; -52.5..-37.5: -2.8; -26.5..-16.5: -1.6; -7.5..-0.5: -0.3; 6.5..15.5: +0.8; 25.5..37.5: +2.0; 52.5..62.5: +3.4)

## 4. Discovery

**Interaction candidates** (a screen: pairs whose combination seems to matter beyond each alone; untested until held-out matches confirm them; switched on in the model from 40 matches):

- morale_diff with knights_diff (screen 0.127)
- morale_diff with spike_killable_diff (screen 0.126)
- morale_diff with morale_total (screen 0.126)
- alive_diff with morale_diff (screen 0.125)
- morale_diff with lord_damage_diff (screen 0.124)
- down_diff_s with morale_diff (screen 0.123)
- boost_clock with morale_diff (screen 0.121)
- stand with morale_diff (screen 0.121)

**Candidate variables** (proposed variables, tested on unseen matches; log loss, lower is better):

- turtle_diff: 0.382 without, 0.382 with: does not improve yet. own minus enemy share of live players at home (own base or pit). Proposed 2026-11-06 from OG comms ([ohno v One], [ohno v Crew]: 'they are turtling, we have to make a play'); comms_vars.py: teams that turtled 60 s won 3 of 13 times
- no_healer_groups_diff: 0.382 without, 0.382 with: does not improve yet. own minus enemy groups of 2+ with no healer. Proposed 2026-11-06 from OG comms ([ohno v One]: keep a prot and a monk on one side, the Rit and a monk on the other); comms_vars.py: such groups lose players twice as often
- solo_healers_diff: 0.382 without, 0.381 with: does not improve yet. own minus enemy healers with no other own healer within casting range. Proposed 2026-11-06 from OG comms ('solo monk, go on the monk'); Denning: a monk alone has no other monk to support it

**Surprises** (moments where the held-out model was most confident about the team that went on to lose; each points to something the variables don't capture yet):

- hold v Fun (7cb3ef17) at 3:30: a model that never saw this match gave hold 1.1%, and hold won. Why it thought so: alive_diff -31.1, team strength +30.3, morale_diff -24.0, knights_diff -23.6, down_diff_s -20.1
- hdm v HC (28447c4a) at 24:00: a model that never saw this match gave HC 3.6%, and HC won. Why it thought so: knights_diff -28.0, morale_diff & map_bases_apart -24.9, morale_diff -23.9, morale_diff & map_flag_run -18.4, lord_health_diff -16.6
- One v cope (fabafc13) at 19:00: a model that never saw this match gave cope 28.1%, and cope won. Why it thought so: lord_damage_diff & map_bases_apart -38.0, team strength +17.3, lord_health_diff -17.3, morale_diff -16.3, flag_lead +12.6
- BcS v Book (349561f3) at 10:45: a model that never saw this match gave Book 6.4%, and Book won. Why it thought so: knights_diff & lord_damage_diff -29.3, morale_diff -24.6, lord_damage_diff & map_bases_apart +21.2, knights_diff -19.9, footmen_lost_diff -12.8
- Team v RACK (2966a590) at 14:15: a model that never saw this match gave Team 4.5%, and Team won. Why it thought so: team strength -41.0, spike_killable_diff -22.6, morale_diff -20.2, stand -5.0, lord_dps_own -5.0
- Dz v TFS (0881f8b3) at 1:30: a model that never saw this match gave TFS 2.9%, and TFS won. Why it thought so: team strength -46.5, fight_state -7.4, morale_diff -6.5, lord_dps_own -5.0, lord_dps_enemy +5.0

## 5. Denning's rulings seen through the model

Win chance from a model that never saw the match, 20 s before and 60 s after each ruled moment. Contributions are points for an otherwise even game (the curves' scale).

- hdm v HC (28447c4a) 5:01 (split answered), HC: 37.9% 20 s before -> 49.0% 60 s after (+11.1). After: knights_diff -28.0, morale_diff & map_bases_apart +16.3, morale_diff +14.7, knights_diff & map_flag_run -8.3
- hdm v HC (28447c4a) 5:01 (split answered), hdm: 64.3% 20 s before -> 56.4% 60 s after (-7.9). After: knights_diff +28.7, morale_diff -13.9, morale_diff & map_bases_apart -13.7, knights_diff & map_flag_run +8.6
- hdm v HC (28447c4a) 1:02 (split detection), HC: 43.0% 20 s before -> 34.3% 60 s after (-8.7). After: morale_diff & map_flag_run -11.1, morale_diff +6.7, team strength -5.4, stand -5.4
- hdm v HC (28447c4a) 1:02 (split detection), hdm: 56.3% 20 s before -> 64.3% 60 s after (+8.0). After: morale_diff & map_flag_run +9.9, morale_diff -5.5, team strength +5.4, stand +5.3
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), HC: 26.1% 20 s before -> 31.8% 60 s after (+5.7). After: knights_diff -28.0, morale_diff & map_bases_apart +16.3, morale_diff +14.7, lord_exposed_diff -12.2
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), hdm: 87.2% 20 s before -> 58.0% 60 s after (-29.2). After: knights_diff +28.7, lord_damage_diff & map_bases_apart -27.1, morale_diff -13.9, morale_diff & map_bases_apart -13.7
- hdm v HC (bbef1904) 8:10 (death), HC: 55.6% 20 s before -> 11.8% 60 s after (-43.8). After: down_diff_s -16.9, morale_diff -14.8, footmen_lost_diff -10.9, alive_diff -10.3
- hdm v HC (bbef1904) 8:10 (death), hdm: 44.3% 20 s before -> 88.9% 60 s after (+44.6). After: morale_diff +18.9, down_diff_s +15.1, alive_diff +10.6, footmen_lost_diff +10.4
- Men v HC (faec428a) 9:31 (death), HC: 32.1% 20 s before -> 27.0% 60 s after (-5.1). After: knights_diff -17.8, footmen_lost_diff -7.2, morale_diff -5.5, stand -5.4
- Men v HC (faec428a) 9:31 (death), Men: 65.4% 20 s before -> 71.8% 60 s after (+6.4). After: knights_diff +16.6, footmen_lost_diff +7.2, morale_diff +6.7, stand +5.3

## 6. Why: the node models

Each explains one result from what happened before it (time order enforced), tested on matches it never saw. AUC = how often a moment that led to the result scores above one that didn't (0.5 = guessing, 1 = perfect).

**deaths** (506 matches, 1029321 moments, 32069 results): adds to the simple baseline (AUC 0.927 against 0.791 for health_pct and damage_taken_3s alone).
- **enemies_near** (enemies within 1,500) rises from -24.0 to +26.2 points (0.0..0.5: -24.0; 0.5..1.5: -14.1; 1.5..2.5: -1.8; 2.5..3.5: +2.8; 3.5..4.5: +7.0; 4.5..5.5: +9.7; 5.5..6.5: +13.5; 6.5..7.5: +18.1; 7.5..8.0: +26.2)
- **strength_gap** (own minus enemy team strength) falls from +12.6 to -14.4 points (-1183.0..-575.5: +12.6; -434.5..-355.5: +8.6; -251.5..-168.0: +8.1; -81.0..-4.5: +2.3; 75.5..160.5: -1.8; 243.0..348.5: -4.7; 434.5..577.5: -13.5)
- **allies_near** (allies within 1,500) falls from +21.0 to -7.5 points (0.0..0.5: +21.0; 0.5..1.5: +10.4; 1.5..2.5: +4.9; 2.5..3.5: -0.5; 3.5..4.5: -2.4; 4.5..5.5: -5.1; 5.5..6.5: -6.3; 6.5..7.0: -7.5)
- **health_pct** (current health %) falls from +39.6 to -4.8 points (1.0..46.5: +39.6; 59.5..67.5: +18.1; 73.5..78.5: +7.2; 82.5..85.5: +2.0; 88.5..91.5: -1.0; 93.5..95.5: -3.4; 97.5..99.5: -4.1)
- **local_diff** (allies minus enemies within 2,000) falls from +23.3 to -9.7 points (-8.0..-3.5: +23.3; -2.5..-1.5: +12.2; -0.5..0.5: -5.7; 1.5..2.5: -6.6; 3.5..4.5: +4.7; 5.5..7.0: -9.7)
- **healers_in_range** (own healers alive within cast range (other than the player)) falls from +7.4 to -1.4 points (0.0..0.5: +7.4; 0.5..1.5: +0.1; 1.5..2.5: -5.1; 2.5..3.5: -0.6; 3.5..4.0: -1.4)
- **prot_up** (a prot (Guardian, Spirit Bond, Life Sheath, Protective Spirit...) on the player now) falls from +2.0 to -7.9 points (0.0..0.5: +2.0; 0.5..1.0: -7.9)
- **health_ceiling** (maximum health after death penalty, as a share of normal) falls from +17.0 to -4.9 points (0.4..0.69: +17.0; 0.71..0.84: +11.2; 0.85..0.89: +7.1; 0.94..0.95: +2.8; 0.99..1.06: -0.6)
- **own_morale** (the player's own morale: negative = death penalty, positive = boost (OG comms: fight the player with 30 DP)) falls from +17.7 to -4.9 points (-60.0..-31.5: +17.7; -28.5..-15.5: +10.4; -14.5..-11.5: +7.2; -5.5..-4.5: +3.6; -0.5..5.5: -0.5)
- **dist_own_pit** (distance from its own pit) rises from -2.0 to +9.1 points (4.0..1373.5: -2.0; 2436.5..4132.5: -2.2; 5295.5..6177.5: -3.4; 6855.5..7372.5: -2.4; 7943.5..8605.5: -2.0; 9475.5..10502.5: +0.9; 11691.5..13119.5: +5.8)

**kill conversion** (493 matches, 8914 moments, 2632 results): adds to the simple baseline (AUC 0.811 against 0.675 for burst_damage and target_health_pct alone).
- **burst_damage** (damage in the 2 s burst) rises from -13.0 to +27.0 points (250.0..258.5: -13.0; 267.5..278.5: -12.9; 289.5..301.5: -9.3; 315.5..330.5: -7.8; 347.5..367.5: +2.5; 390.5..416.5: +7.5; 454.5..510.5: +22.0)
- **target_ceiling** (target's health ceiling) falls from +38.1 to -14.4 points (0.4..0.56: +38.1; 0.69..0.7: +25.7; 0.76..0.84: +21.5; 0.85..0.86: +14.7; 0.88..0.94: +6.0; 0.95..0.99: +0.9; 1.06..1.1: -14.4)
- **target_healers_in_range** (target's healers in range) falls from +31.9 to -8.8 points (0.0..0.5: +31.9; 0.5..1.5: +6.3; 1.5..2.5: -5.7; 2.5..3.5: -8.6; 3.5..4.0: -8.8)
- **target_prot_up** (a prot on the target) falls from +6.0 to -10.9 points (0.0..0.5: +6.0; 0.5..1.0: -10.9)
- **target_health_pct** (target health % when the burst started) falls from +28.4 to -9.8 points (0.0..37.5: +28.4; 48.5..55.5: +11.3; 61.5..67.5: +4.6; 72.5..76.5: -0.1; 80.5..84.5: -2.2; 87.5..91.5: -4.9; 95.5..99.5: -8.9)
- **strength_gap** (attacking minus target team strength) rises from -8.3 to +12.3 points (-1183.0..-547.0: -8.3; -376.5..-276.5: -9.9; -173.5..-84.0: -2.4; 0.0..92.5: +0.6; 177.5..230.5: +2.4; 320.5..383.5: +5.8; 521.5..678.0: +11.3)
- **enemy_prots** (target team's prot skills) falls from +7.5 to -3.8 points (0.0..5.5: +7.5; 7.5..8.5: +4.9; 9.5..10.5: +2.8; 11.5..12.5: -0.1; 13.5..14.5: -3.6; 15.5..16.5: -2.9; 17.5..20.0: -3.8)
- **target_degen_pips** (degeneration on the target, pips (pressure.py)) rises from -1.5 to +7.0 points (0.0..1.2: -1.5; 1.2..2.95: -0.8; 2.95..3.1: +6.4; 3.1..3.9: +6.7; 3.9..4.1: +5.9; 4.1..6.95: +6.1; 6.95..7.1: +1.0; 7.1..9.95: +5.2; 9.95..10.0: +7.0)

**flag answer** (seconds an answer to an enemy capture was slower than possible; 425 matches, 3922 rows): adds to the simple baseline (typical error 15.8s against 28.4s for the median; explains 73% of the spread).
- **parked_s** (seconds the flag lay parked (dropped 5 s or more: not running yet)): 0.0..2.5: -5.8 s; 7.5..12.5: +5.8 s; 16.5..22.5: +17.2 s; 29.5..38.5: +33.6 s; 46.5..61.5: +52.9 s; 85.5..105.5: +69.4 s; 147.5..249.0: +80.2 s
- **own_deaths_during** (own deaths during the answer): 0.0..0.5: -3.9 s; 0.5..1.5: +7.6 s; 1.5..2.5: +15.9 s; 2.5..3.5: +24.0 s; 3.5..4.5: +31.3 s; 4.5..5.5: +40.8 s; 5.5..6.5: +46.4 s; 6.5..8.5: +48.4 s; 8.5..24.0: +49.8 s
- **enemy_deaths_during** (enemy deaths during the answer): 0.0..0.5: -3.9 s; 0.5..1.5: +7.9 s; 1.5..2.5: +16.3 s; 2.5..3.5: +21.1 s; 3.5..4.5: +25.6 s; 4.5..5.5: +22.9 s; 5.5..12.0: +39.5 s
- **carrier_damage_taken** (damage the carrier took while carrying): 0.0..0.5: -4.7 s; 30.5..57.5: -3.5 s; 88.5..121.5: -1.9 s; 172.5..227.5: -0.2 s; 281.0..352.5: +1.5 s; 451.5..586.5: +7.6 s; 787.5..1156.0: +14.9 s
- **enemies_in_the_way** (enemy presence along the runner's trip back to the spawn): 0.0..0.5: -5.0 s; 5.5..11.5: -4.3 s; 17.5..23.5: -2.4 s; 31.5..41.5: -0.1 s; 52.5..64.5: +1.1 s; 83.5..107.5: +5.8 s; 144.5..215.5: +15.4 s
- **possible_s** (fastest possible answer (s) from the flag model at the enemy's capture): 0.0..3.5: -8.9 s; 8.5..13.5: -4.5 s; 18.5..22.5: -0.7 s; 25.5..28.5: +2.1 s; 31.5..34.5: +4.4 s; 37.5..41.5: +3.8 s; 46.5..51.5: +4.2 s
- **runner_to_spawn** (runner's distance to its flag spawn when the enemy captured): 1.0..768.0: -6.1 s; 1521.5..2186.5: -3.3 s; 3030.5..3798.5: -0.8 s; 4310.5..4616.5: +1.4 s; 5062.0..5668.5: +1.4 s; 6315.5..6853.5: +2.3 s; 7454.0..8452.5: +2.6 s
- **flag_lead_at_enemy_cap** (own flag lead when the enemy captured): -80.0..-59.5: -1.8 s; -50.5..-40.5: +1.7 s; -33.5..-26.5: +3.2 s; -20.5..-14.5: +2.2 s; -7.5..-1.5: +0.2 s; 5.5..16.5: -2.5 s; 27.5..41.5: -3.3 s
- **morale_diff** (own minus enemy morale): -303.0..-111.5: +5.0 s; -75.5..-52.5: +5.5 s; -30.5..-15.5: +2.4 s; -2.5..3.5: -0.1 s; 15.5..30.5: -1.4 s; 52.5..75.5: -2.3 s; 99.5..147.5: -6.1 s
- **quick_handoffs** (quick hand-offs (a teammate picked it up within 5 s)): 0.0..0.5: -1.3 s; 0.5..1.5: +4.1 s; 1.5..2.5: +7.8 s; 2.5..6.0: +27.5 s

**lord damage** (Lord damage dealt in the next 10 s while players are in the enemy pit; 485 matches, 56335 rows): adds to the simple baseline (typical error 77.1 against 102.7 for the median; explains 44% of the spread).
  ('chance of any' curves: points of the chance of any Lord damage in the window; 'amount' curves: % more Lord damage when there is some.)
- **defenders (chance of any)** (own players in the pit): 0.0..0.5: +37.4 points; 0.5..1.5: +29.6 points; 1.5..2.5: +19.2 points; 2.5..3.5: -4.3 points; 3.5..4.5: -10.6 points; 4.5..5.5: -28.9 points; 5.5..6.5: -32.9 points; 6.5..7.5: -37.1 points; 7.5..8.0: -41.9 points
- **bodyguard (chance of any)** (own Bodyguard alive): 0.0..0.5: +24.5 points; 0.5..1.0: -10.4 points
- **npc_healing_10s (chance of any)** (healing on own pit NPCs and Lord in the last 10 s): 0.0..1.5: -8.7 points; 41.5..51.5: +10.5 points; 87.5..126.5: +12.2 points; 155.5..186.5: +13.8 points; 221.5..267.5: +15.4 points; 316.5..379.5: +17.0 points; 469.5..623.5: +18.0 points
- **minute (chance of any)** (match minute): 0.3..2.65: -23.1 points; 3.75..4.95: -8.6 points; 6.15..7.45: -6.8 points; 8.95..10.45: -4.3 points; 12.15..14.15: -2.0 points; 16.35..19.05: +0.7 points; 21.95..24.85: +15.3 points
- **attackers_lord_dps (chance of any)** (attackers' measured damage per second against a Lord (benchmarks)): 2.7..23.55: -27.1 points; 24.8..28.85: -12.1 points; 37.25..48.15: +0.4 points; 53.95..63.55: -0.7 points; 68.55..77.05: +6.4 points; 84.15..92.65: +11.6 points; 102.15..108.15: +12.3 points
- **knights (chance of any)** (own knights alive): 0.0..0.5: +9.1 points; 0.5..1.5: -7.2 points; 1.5..2.0: -9.3 points
- **attackers_share (chance of any)** (share of the attacking team's live players in the pit (OG comms: merge before pushing the pit)): 0.12..0.13: -9.3 points; 0.16..0.23: -9.0 points; 0.27..0.31: -7.0 points; 0.35..0.39: -8.0 points; 0.46..0.58: +2.1 points; 0.69..0.84: +8.4 points; 0.94..1.0: +12.5 points
- **full_pit_targets (chance of any)** (pit NPCs alive (targets the defending monks must watch, P9)): 0.0..0.5: +11.2 points; 0.5..1.5: +8.0 points; 1.5..2.5: +3.6 points; 2.5..3.5: -1.7 points; 3.5..4.5: -4.2 points; 4.5..5.5: -7.1 points; 5.5..6.0: -9.0 points
- **attacker_healers (chance of any)** (of which healers): 0.0..0.5: -6.5 points; 0.5..1.5: +1.0 points; 1.5..2.5: +6.1 points; 2.5..3.5: +9.0 points; 3.5..4.0: +39.3 points
- **attackers (chance of any)** (enemy players in the pit): 1.0..1.5: -5.1 points; 1.5..2.5: -3.0 points; 2.5..3.5: -4.3 points; 3.5..4.5: -2.8 points; 4.5..5.5: +3.2 points; 5.5..6.5: +5.5 points; 6.5..7.5: +6.2 points; 7.5..8.0: +10.0 points


## 6b. The learned nodes (step 2 of the learned causal map)

Each node uses only the causal-map links into it. A link's strength is how much worse the node predicts matches it never saw without that link's features (refit without them, same folds); supported when the gain is more than twice its spread across folds, rejected when dropping it helps by more than that, otherwise not clear yet.

**run outcome** (map R.3; 505 matches, 15912 cases, result rate 66%): log loss 0.5406 against 0.6379 for the simple baseline (adds to the simple baseline). Inputs 23 of a cap of 266.
- marks the situation but is an allocation decision (R-282: may still be a fix): escort
- reads backwards: likely a reaction, not a cause (R-285; never a fault or a fix): damage_so_far, knocked_down_so_far, other_control_so_far
- link K.13 -> R.3 [execution]: gain +0.0333 (+/- 0.0028), supported (min_capture_s)
- link S.scoreboard -> R.3 [state]: gain +0.0106 (+/- 0.002), supported (morale_diff, boost_clock)
- link C.map -> R.3 [context]: gain +0.0031 (+/- 0.0008), supported (run_dist)
- link P.10 -> R.3 [decision/state]: gain +0.0025 (+/- 0.0012), supported (stand_own, stand_enemy, enemy_boost_in, flag_lead...)
- link C.strength -> R.3 [context]: gain +0.0005 (+/- 0.0007), not clear yet (strength_gap)
- link A.allocation -> R.3 [decision/state]: gain -0.0001 (+/- 0.0009), not clear yet (escort, own_main, enemy_main, enemy_power_play)
- link C.builds -> R.3 [context]: gain -0.0001 (+/- 0.0007), not clear yet (enemy_snares)
- link K.11 -> R.3 [execution]: gain -0.001 (+/- 0.0005), rejected (crippled_so_far, knocked_down_so_far, other_control_so_far, damage_so_far...)
  - leans on **min_capture_s** (seconds the carrier needs at least to reach the stand from here, at its fastest expected carry speed (its speed skills; Denning)): +30.4 points at 0.0 to 3.75, -28.4 at 31.25 to 52.2
  - leans on **boost_clock** (boost clock (discovery, approved)): +4.6 points at -120.0 to -112.5, -20.1 at 101.5 to 120.0
  - leans on **run_dist** (distance from the team's spawn to the stand): +8.4 points at 3206.0 to 4446.5, +6.1 at 9245.5 to 9974.0

**flag swing** (map R.3; 506 matches, 18780 cases, average 0.3 s): mean absolute error (s) 26.8275 against 28.4249 for the simple baseline (adds to the simple baseline). Inputs 28 of a cap of 469.
- marks the situation but is an allocation decision (R-282: may still be a fix): own_flag_duty
- link P.10 -> R.3 [state]: gain +0.78 (+/- 0.07), supported (waiting_runner, backup_flag, stand_own, stand_enemy...)
- link S.scoreboard -> R.3 [state]: gain +0.66 (+/- 0.07), supported (flag_lead, morale_diff)
- link C.strength -> R.3 [context]: gain +0.06 (+/- 0.04), not clear yet (strength_gap)
- link R.1 -> R.3 [state]: gain -0.0 (+/- 0.01), not clear yet (own_deaths_30s, enemy_deaths_30s)
- link A.allocation -> R.3 [decision/state]: gain -0.01 (+/- 0.02), not clear yet (own_alive, enemy_alive, own_main, enemy_main...)
- link C.clock -> R.3 [state]: gain -0.01 (+/- 0.01), not clear yet (minute, res_in)
- link C.map -> R.3 [context]: gain -0.01 (+/- 0.01), not clear yet (run_dist)
  - leans on **flag_lead** (flag lead now (s)): +15.0 s at -137.0 to -62.5, -15.9 at 61.5 to 128.0
  - leans on **morale_diff** (morale, own minus enemy (discovery, approved)): -11.7 s at -445.0 to -175.5, +12.0 at 194.5 to 430.0
  - leans on **strength_gap** (team strength gap): -5.0 s at -1183.0 to -573.5, +4.3 at 577.5 to 1183.0

**run defence** (map R.3; 505 matches, 15912 cases, result rate 66%): log loss 0.5341 against 0.6379 for the simple baseline (adds to the simple baseline). Inputs 22 of a cap of 266.
- link S.scoreboard -> R.3 [state]: gain +0.0403 (+/- 0.0031), supported (boost_clock, stand, flag_lead, morale_diff...)
- link K.13 -> R.3 [state]: gain +0.0327 (+/- 0.0027), supported (min_capture_s)
- link C.map -> R.3 [context]: gain +0.0036 (+/- 0.0009), supported (run_dist)
- link P.10 -> R.3 [state]: gain +0.0011 (+/- 0.0004), supported (runner_class)
- link C.strength -> R.3 [context]: gain +0.0008 (+/- 0.0006), not clear yet (strength_gap)
- link A.mesa_free -> R.3 [state]: gain +0.0002 (+/- 0.0006), not clear yet (def_free, pushers_so_far, control_so_far, damage_so_far)
- link C.builds -> R.3 [context]: gain +0.0001 (+/- 0.0005), not clear yet (own_snares, own_area_damage, enemy_snares_v_own_speed)
- link K.11 -> R.3 [execution]: gain +0.0 (+/- 0.0003), not clear yet (def_snare_near)
- link K.5 -> R.3 [execution]: gain -0.0 (+/- 0.0004), not clear yet (healing_monks_own)
- link A.allocation -> R.3 [state]: gain -0.0002 (+/- 0.0005), not clear yet (escort, att_main, def_main)
  - leans on **min_capture_s** (seconds the carrier needs at least to reach the stand from here (its speed skills)): +31.3 points at 0.0 to 3.75, -28.5 at 31.25 to 52.2
  - leans on **stand** (stand (discovery, approved)): -8.6 points at -1.0 to -0.5, +5.6 at 0.5 to 1.0
  - leans on **flag_lead** (flag lead (discovery, approved)): -16.4 points at -137.0 to -58.5, +1.7 at 59.5 to 86.0

**capture speed** (map R.3; 486 matches, 4103 cases, average 39.3 s): mean absolute error (s) 12.984 against 15.6242 for the simple baseline (adds to the simple baseline). Inputs 10 of a cap of 102.
- link K.13 -> R.3 [state]: gain +2.31 (+/- 0.11), supported (min_capture_s)
- link A.allocation -> R.3 [decision/state]: gain +0.41 (+/- 0.1), supported (defenders_free, escort)
- link C.map -> R.3 [context]: gain +0.41 (+/- 0.04), supported (run_dist)
- link P.10 -> R.3 [state]: gain +0.19 (+/- 0.07), supported (runner_class)
- link C.strength -> R.3 [context]: gain +0.04 (+/- 0.03), not clear yet (strength_gap)
- link K.11 -> R.3 [execution]: gain +0.0 (+/- 0.01), not clear yet (pushers_10s, control_10s, damage_10s, def_snare_near)
  - leans on **min_capture_s** (seconds the carrier needed at least, at its fastest expected carry speed (its speed skills)): -15.8 s at 0.9 to 9.55, +14.8 at 36.15 to 45.4
  - leans on **escort** (the runner's escorts): -3.8 s at 0.0 to 0.5, +12.2 at 6.5 to 7.0
  - leans on **run_dist** (distance from the runner's spawn to the stand): +5.7 s at 4133.0 to 4432.5, -5.1 at 9244.5 to 9974.0

**power play** (map K.4; 503 matches, 4647 cases, result rate 40%): log loss 0.3614 against 0.6753 for the simple baseline (adds to the simple baseline). Inputs 25 of a cap of 94.
- marks the situation (predicts the previous result as well as the next; never a fix): degen_10s
- reads backwards: likely a reaction, not a cause (R-285; never a fault or a fix): blind_secs_on_own_10s
- measured but not fitted (the enemy's response during the window): enemy_prots_10s, enemy_heal_s, enemy_kite_10s, enemy_baits_10s
- link A.allocation -> K.4 [state]: gain +0.0398 (+/- 0.0063), supported (size, own_main, enemy_main, short_dead...)
- link K.2 -> K.4 [execution]: gain +0.0211 (+/- 0.002), supported (dps_v_usual)
- link P.2 -> K.4 [execution]: gain +0.0075 (+/- 0.0021), supported (spikes_10s, spike_spread)
- link C.strength -> K.4 [context]: gain +0.0074 (+/- 0.001), supported (strength_gap)
- link P.1 -> K.4 [execution]: gain +0.0071 (+/- 0.0011), supported (spikes_on_healers, healer_damage_share)
- link P.24 -> K.4 [execution]: gain +0.0069 (+/- 0.0047), not clear yet (knockdowns_10s, knockdowns_on_casting_10s)
- link P.25 -> K.4 [execution]: gain +0.0063 (+/- 0.0008), supported (disable_10s)
- link S.scoreboard -> K.4 [state]: gain +0.0051 (+/- 0.0009), supported (down_diff_s, carrying_diff)
- link P.22 -> K.4 [execution]: gain +0.0019 (+/- 0.001), not clear yet (degen_10s)
- link P.14 -> K.4 [decision]: gain +0.0 (+/- 0.0008), not clear yet (pushed)
- link P.26 -> K.4 [execution]: gain +0.0 (+/- 0.0004), not clear yet (castprev_10s)
- link R.3 -> K.4 [state]: gain -0.0001 (+/- 0.0002), not clear yet (flag_lead)
- link K.11 -> K.4 [execution]: gain -0.0003 (+/- 0.0004), not clear yet (blind_secs_on_own_10s)
- link C.builds -> K.4 [context]: gain -0.0007 (+/- 0.0005), not clear yet (enemy_strips_v_own_prots)
  - leans on **short_dead** (share of the enemy's missing player-seconds: dead): -19.6 points at 0.0 to 0.01, +19.2 at 0.99 to 1.0
  - leans on **dps_v_usual** (own damage per second against the usual of the players alive): -30.6 points at 0.0 to 0.56, +23.6 at 3.2 to 21.09
  - leans on **window_s** (seconds the power play lasted): -11.9 points at 14.0 to 30.5, +33.6 at 94.5 to 351.0

**fight outcome** (map R.2; 505 matches, 3863 cases, result rate 47%): log loss 0.2218 against 0.691 for the simple baseline (adds to the simple baseline). Inputs 33 of a cap of 90.
- marks the situation (predicts the previous result as well as the next; never a fix): castprev_diff
- reads backwards: likely a reaction, not a cause (R-285; never a fault or a fix): blind_attacks_diff, blind_defensive_secs_diff, castprev_diff, disable_diff, hex_secs_diff, knockdowns_on_casting_diff, strip_right_diff
- link S.scoreboard -> R.2 [state]: gain +0.0914 (+/- 0.0045), supported (morale_diff, fight_state, down_diff_s, alive_diff...)
- link K.1 -> R.2 [execution]: gain +0.0234 (+/- 0.004), supported (dps_v_usual_diff)
- link P.2 -> R.2 [execution]: gain +0.0199 (+/- 0.0044), supported (spike_spread_diff, spikes_diff)
- link A.allocation -> R.2 [state]: gain +0.0191 (+/- 0.0024), supported (own_local, enemy_local)
- link P.17 -> R.2 [execution]: gain +0.0121 (+/- 0.0024), supported (ready_interrupt_diff, dazed_casts_diff, blind_attacks_diff)
- link C.builds -> R.2 [context]: gain +0.0021 (+/- 0.0012), not clear yet (own_hexes, own_heals)
- link P.5 -> R.2 [execution]: gain +0.0013 (+/- 0.0011), not clear yet (hex_secs_diff, hex_right_diff)
- link P.1 -> R.2 [execution]: gain +0.0006 (+/- 0.0006), not clear yet (healer_focus_diff)
- link C.strength -> R.2 [context]: gain +0.0001 (+/- 0.0013), not clear yet (strength_gap)
- link P.13 -> R.2 [execution]: gain -0.0 (+/- 0.0003), not clear yet (peel_defensive_diff)
- link P.21 -> R.2 [execution]: gain -0.0 (+/- 0.0003), not clear yet (kite_secs_diff)
- link P.24 -> R.2 [execution]: gain -0.0 (+/- 0.0024), not clear yet (knockdowns_diff, knockdowns_on_casting_diff)
- link P.23 -> R.2 [execution]: gain -0.0001 (+/- 0.0004), not clear yet (baits_diff)
- link P.25 -> R.2 [execution]: gain -0.0002 (+/- 0.0007), not clear yet (disable_diff)
- link P.18 -> R.2 [execution]: gain -0.0003 (+/- 0.0012), not clear yet (strip_right_diff, strip_value_diff)
- link P.27 -> R.2 [execution]: gain -0.0003 (+/- 0.0006), not clear yet (prekite_secs_diff)
- link P.22 -> R.2 [execution]: gain -0.0003 (+/- 0.0004), not clear yet (degen_diff)
- link P.26 -> R.2 [execution]: gain -0.0009 (+/- 0.0004), rejected (castprev_diff)
- link P.19 -> R.2 [execution]: gain -0.001 (+/- 0.0008), not clear yet (blind_front_secs_diff, blind_defensive_secs_diff)
  - leans on **morale_diff** (morale, own minus enemy (discovery, approved)): -24.3 points at -470.0 to -214.5, +36.3 at 214.5 to 410.0
  - leans on **enemy_local** (enemy players in the fight): +21.5 points at 0.0 to 0.5, -22.6 at 7.5 to 8.0
  - leans on **own_local** (own players in the fight): -40.4 points at 0.0 to 0.5, +23.8 at 7.5 to 8.0

**split chance** (map A.allocation; 506 matches, 36203 cases, result rate 14%): log loss 0.352 against 0.4048 for the simple baseline (adds to the simple baseline). Inputs 19 of a cap of 253.
- link S.scoreboard -> A.allocation [state]: gain +0.029 (+/- 0.0018), supported (flag_lead, own_alive, enemy_alive, own_main...)
- link C.builds -> A.allocation [context]: gain +0.01 (+/- 0.0033), supported (own_speed_power, own_escapes, own_snare_power, enemy_snare_power...)
- link C.clock -> A.allocation [state]: gain +0.0025 (+/- 0.0006), supported (minute, res_in)
- link C.strength -> A.allocation [context]: gain -0.0001 (+/- 0.0003), not clear yet (strength_gap)
  - leans on **own_main** (own main): +30.1 points at 0.0 to 2.5, -17.2 at 7.5 to 8.0
  - leans on **spike_build_own** (own build is a spike build (discovery, approved)): +6.3 points at 0.0 to 0.5, -14.4 at 0.5 to 1.0
  - leans on **split_diff** (players splitting, own minus enemy (discovery, approved)): -16.4 points at -6.0 to -4.5, -3.5 at 1.5 to 5.0

**split answer** (map P.11; 357 matches, 1362 cases, average -5.2 s): mean absolute error (s) 16.0378 against 18.3818 for the simple baseline (adds to the simple baseline). Inputs 10 of a cap of 34.
- link A.allocation -> P.11 [state]: gain +1.04 (+/- 0.16), supported (size)
- link A.mesa_free -> P.11 [state]: gain +0.59 (+/- 0.15), supported (def_free, nearest_to_base)
- link S.scoreboard -> P.11 [state]: gain +0.47 (+/- 0.13), supported (flag_lead, def_alive, att_main, split_diff)
- link C.builds -> P.11 [context]: gain +0.12 (+/- 0.09), not clear yet (own_area_damage)
- link C.clock -> P.11 [state]: gain +0.06 (+/- 0.08), not clear yet (minute)
- link C.strength -> P.11 [context]: gain +0.05 (+/- 0.09), not clear yet (strength_gap)
  - leans on **size** (split size): +15.4 s at 1.0 to 1.5, -11.8 at 5.5 to 8.0
  - leans on **nearest_to_base** (nearest defender to its base at the split's entry): +9.1 s at 17.0 to 386.5, +10.9 at 7068.5 to 16553.0
  - leans on **split_diff** (players splitting, own minus enemy (discovery, approved)): +5.0 s at -6.0 to -5.5, +9.6 at 2.5 to 4.0

**split effect** (map R.5; 357 matches, 1362 cases, result rate 39%): log loss 0.6353 against 0.6697 for the simple baseline (adds to the simple baseline). Inputs 15 of a cap of 26.
- link S.scoreboard -> R.5 [state]: gain +0.0271 (+/- 0.0078), supported (def_npc_value, def_free, morale_diff, flag_lead...)
- link C.builds -> R.5 [context]: gain +0.0034 (+/- 0.0028), not clear yet (enemy_prots)
- link P.11 -> R.5 [state]: gain +0.0029 (+/- 0.001), supported (latency, defenders)
- link A.allocation -> R.5 [decision/state]: gain +0.0028 (+/- 0.0007), supported (size, main_diff)
- link K.13 -> R.5 [execution]: gain +0.0001 (+/- 0.0018), not clear yet (split_speed_power, own_escapes_power)
- link K.11 -> R.5 [state]: gain -0.0014 (+/- 0.0009), not clear yet (def_snare_present)
- link C.strength -> R.5 [context]: gain -0.0016 (+/- 0.001), not clear yet (strength_gap)
- link K.8 -> R.5 [decision]: gain -0.002 (+/- 0.0011), not clear yet (split_healers)
  - leans on **def_npc_value** (defenders' pit NPC value when the split entered the base): -16.9 points at 0.0 to 0.75, +4.0 at 11.25 to 13.5
  - leans on **enemy_prots** (prot skills on the defenders' bars (discovery, approved)): +5.3 points at 0.0 to 9.5, -5.4 at 14.5 to 19.0
  - leans on **morale_diff** (morale, own minus enemy (discovery, approved)): -7.4 points at -430.0 to -126.5, +4.8 at 89.0 to 395.0

**pit npc loss** (map R.5; 504 matches, 50165 cases, result rate 21%): log loss 0.3954 against 0.5136 for the simple baseline (adds to the simple baseline). Inputs 18 of a cap of 525.
- reads backwards: likely a reaction, not a cause (R-285; never a fault or a fix): npc_healing_10s
- measured but not fitted (the enemy's response during the window): npc_damage_5s
- link P.11 -> R.5 [decision]: gain +0.0737 (+/- 0.0031), supported (defenders, defender_healers, defenders_elsewhere)
- link S.scoreboard -> R.5 [state]: gain +0.0054 (+/- 0.0007), supported (knights, archers, bodyguard, full_pit_targets)
- link A.allocation -> R.5 [state]: gain +0.003 (+/- 0.0008), supported (attackers, attacker_healers, attackers_share, attackers_outside)
- link C.builds -> R.5 [context]: gain +0.0029 (+/- 0.0008), supported (attackers_lord_dps, attackers_area_damage)
- link C.strength -> R.5 [context]: gain +0.0026 (+/- 0.001), supported (strength_gap)
- link C.clock -> R.5 [state]: gain +0.0021 (+/- 0.0006), supported (seconds_in_pit, res_in, minute)
- link K.6 -> R.5 [execution]: gain +0.0006 (+/- 0.0002), supported (npc_healing_10s)
  - leans on **defenders** (own players in the pit): +36.8 points at 0.0 to 0.5, -35.2 at 7.5 to 8.0
  - leans on **attackers_lord_dps** (attackers' measured damage per second against NPCs): -25.1 points at 2.7 to 23.55, +17.0 at 107.45 to 189.4
  - leans on **defenders_elsewhere** (own players alive outside the pit): +15.5 points at 0.0 to 0.5, -6.2 at 7.5 to 8.0

**collapse** (map R.1; 457 matches, 3216 cases, result rate 13%): log loss 0.312 against 0.393 for the simple baseline (adds to the simple baseline). Inputs 21 of a cap of 21.
- marks the situation but is an allocation decision (R-282: may still be a fix): split_healers
- reads backwards: likely a reaction, not a cause (R-285; never a fault or a fix): split_speed_power
- link K.1 -> R.1 [state]: gain +0.0112 (+/- 0.0027), supported (def_dps)
- link C.strength -> R.1 [context]: gain +0.0111 (+/- 0.0033), supported (strength_gap)
- link K.9 -> R.1 [state]: gain +0.0056 (+/- 0.0019), supported (split_dp)
- link A.allocation -> R.1 [decision/state]: gain +0.0028 (+/- 0.0007), supported (size, main_diff)
- link P.20 -> R.1 [execution]: gain +0.0023 (+/- 0.0009), supported (depth_at_arrival, depth_median)
  - alone: depth_at_arrival (nearest split member's distance to the defending pit when the first defender arrived): gain +0.0002 (+/- 0.0008), not clear yet
  - alone: depth_median (nearest split member's median distance to the defending pit over the split): gain -0.0001 (+/- 0.001), not clear yet
- link K.5 -> R.1 [decision/execution/state]: gain +0.002 (+/- 0.0007), supported (split_healers, split_self_defence, healing_monks_enemy)
- link P.11 -> R.1 [state]: gain +0.001 (+/- 0.0006), not clear yet (latency)
- link K.13 -> R.1 [execution]: gain +0.0003 (+/- 0.0005), not clear yet (escape_ready, split_speed_power, split_escapes)
- link K.11 -> R.1 [state]: gain +0.0001 (+/- 0.0013), not clear yet (def_snare_present)
- link S.scoreboard -> R.1 [state]: gain +0.0001 (+/- 0.0006), not clear yet (def_npc_value)
- link C.builds -> R.1 [context]: gain -0.0002 (+/- 0.0005), not clear yet (split_npc_dps)
- link P.9 -> R.1 [execution/state]: gain -0.0016 (+/- 0.0017), not clear yet (defenders_10s, contact_diff, npc_hit_to_arrival, res_in_at_arrival)
  - alone: defenders_10s (defenders arriving within 10 s of the first (arrival spread)): gain +0.0 (+/- 0.0006), not clear yet
  - alone: contact_diff (defenders arriving within 5 s of the first, minus the split's size (numbers at contact)): gain +0.0003 (+/- 0.0005), not clear yet
  - alone: npc_hit_to_arrival (seconds from the split's first hit on an NPC to the first defender's arrival): gain -0.0003 (+/- 0.0011), not clear yet
  - alone: res_in_at_arrival (seconds to the next res when the first defender arrived): gain -0.0007 (+/- 0.0008), not clear yet
  - leans on **def_dps** (the defenders who came: their usual damage per second, summed (Denning: can they kill it)): -18.9 points at 0.0 to 1.2, +19.9 at 41.35 to 58.8
  - leans on **strength_gap** (splitting team's strength gap): +16.4 points at -1183.0 to -547.0, -8.9 at 616.5 to 1183.0
  - leans on **split_dp** (worst morale among the split members (death penalty lowers max health; Denning)): +19.7 points at -60.0 to -44.5, -6.9 at 9.5 to 10.0

## 7. The usual play

Each choice against the most common one in that kind of decision, in win-chance points over the decision's window, adjusted for the situation, with a 90% range from resampling whole matches. CLEAR = the range excludes 0. Win chance comes from a model that never saw the match. The same comparison over the 30 s BEFORE the decision is a placebo test: a choice can't cause what came before it, so a clear difference there means the effect is partly who makes that choice.

**after wipe** (1183 decisions, 482 matches; usual: pushed the pit)
- reset (n 183): -3.5 [-5.2, -1.6] CLEAR; in the 30 s before: +0.4 [-0.9, +1.8]
- took the flag (n 124): -2.0 [-4.4, +0.5]; in the 30 s before: +0.7 [-1.3, +3.2]
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - reset, Corrupted Isle: -5.1 (n 28 against 111)
  - reset, Druid's Isle: +0.5 (n 26 against 126)
  - reset, Isle of Jade: -3.4 (n 31 against 118)
  - reset, Isle of Meditation: -1.2 (n 31 against 144)
  - reset, Isle of Solitude: -5.5 (n 23 against 160)
  - reset, Isle of Weeping Stone: -6.2 (n 14 against 66)
  - reset, Uncharted Isle: -9.3 (n 13 against 111)
  - took the flag, Corrupted Isle: +2.2 (n 21 against 111)
  - took the flag, Druid's Isle: +0.5 (n 20 against 126)
  - took the flag, Isle of Jade: -7.0 (n 26 against 118)
  - took the flag, Isle of Meditation: -3.9 (n 23 against 144)
  - took the flag, Isle of Weeping Stone: -3.8 (n 10 against 66)
  - took the flag, Uncharted Isle: -2.8 (n 12 against 111)

**boost clock** (1841 decisions, 471 matches; usual: not running, fought)
- not running, fell back (n 306): -0.4 [-1.5, +1.0]; in the 30 s before: -0.6 [-1.4, +0.3]
- running, advanced (n 253): +2.2 [+0.9, +3.5] CLEAR; in the 30 s before: +0.9 [+0.1, +1.9] ALREADY DIFFERENT BEFORE: partly who chooses it
- not running, advanced (n 250): +0.6 [-0.3, +1.7]; in the 30 s before: +0.5 [-0.3, +1.3]
- running, fought (n 205): +3.0 [+1.8, +4.3] CLEAR; in the 30 s before: +0.3 [-0.6, +1.2]
- not running, held (n 150): +0.7 [-0.4, +2.0]; in the 30 s before: -0.2 [-1.0, +0.7]
- running, fell back (n 148): +3.0 [+1.6, +4.3] CLEAR; in the 30 s before: -0.6 [-1.8, +0.4]
- running, held (n 97): +1.9 [+0.8, +3.4] CLEAR; in the 30 s before: +0.7 [-0.2, +1.7]
- not running, to the spawn (n 31): +0.0 [-2.4, +2.3]; in the 30 s before: +0.7 [-1.0, +2.3]
- running, to the spawn (n 8): +2.4 [-0.1, +5.8]; in the 30 s before: +0.6 [-9.1, +7.7]
- not running (n 7): +2.1 [-1.2, +4.9]; in the 30 s before: +0.0 [-6.2, +4.4]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - not running, fell back, behind in the fight (lowest third, -0.12 or less): +0.5 (n 152 against 177)
  - not running, fell back, middle third: -1.4 (n 96 against 119)
  - not running, fell back, ahead in the fight (top third, above -0.01): -2.0 (n 58 against 90)
  - running, advanced, behind in the fight (lowest third, -0.12 or less): +2.2 (n 36 against 177)
  - running, advanced, middle third: +1.7 (n 92 against 119)
  - running, advanced, ahead in the fight (top third, above -0.01): +1.8 (n 125 against 90)
  - not running, advanced, behind in the fight (lowest third, -0.12 or less): +1.5 (n 70 against 177)
  - not running, advanced, middle third: -0.7 (n 91 against 119)
  - not running, advanced, ahead in the fight (top third, above -0.01): +1.2 (n 89 against 90)
  - running, fought, behind in the fight (lowest third, -0.12 or less): +1.2 (n 44 against 177)
  - running, fought, middle third: +1.0 (n 76 against 119)
  - running, fought, ahead in the fight (top third, above -0.01): +4.1 (n 85 against 90)
  - not running, held, behind in the fight (lowest third, -0.12 or less): +0.9 (n 55 against 177)
  - not running, held, middle third: +0.0 (n 47 against 119)
  - not running, held, ahead in the fight (top third, above -0.01): +0.8 (n 48 against 90)
  - running, fell back, behind in the fight (lowest third, -0.12 or less): +0.3 (n 42 against 177)
  - running, fell back, middle third: +2.0 (n 53 against 119)
  - running, fell back, ahead in the fight (top third, above -0.01): +4.5 (n 53 against 90)
  - running, held, behind in the fight (lowest third, -0.12 or less): +2.6 (n 13 against 177)
  - running, held, middle third: +1.5 (n 30 against 119)
  - running, held, ahead in the fight (top third, above -0.01): +1.4 (n 54 against 90)
  - not running, to the spawn, behind in the fight (lowest third, -0.12 or less): +0.5 (n 21 against 177)
  - not running, to the spawn, middle third: too few yet (n 4 against 119; means 1.3 against 0.3)
  - not running, to the spawn, ahead in the fight (top third, above -0.01): too few yet (n 6 against 90; means 0.6 against -2.0)
  - running, to the spawn, behind in the fight (lowest third, -0.12 or less): too few yet (n 4 against 177; means 0.9 against -1.2)
  - running, to the spawn, middle third: too few yet (n 3 against 119; means 3.9 against 0.3)
  - running, to the spawn, ahead in the fight (top third, above -0.01): too few yet (n 1 against 90; means 0.3 against -2.0)
  - not running, behind in the fight (lowest third, -0.12 or less): too few yet (n 3 against 177; means 0.1 against -1.2)
  - not running, ahead in the fight (top third, above -0.01): too few yet (n 4 against 90; means -0.8 against -2.0)
  By snare matchup (movepower.py: enemy snare power of the live players minus own speed power; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - not running, fell back, little enemy snare for own speed (lowest third, -28 or less): -0.1 (n 98 against 97)
  - not running, fell back, middle third: +0.1 (n 102 against 148)
  - not running, fell back, a lot of enemy snare for own speed (top third, above -2): -1.3 (n 106 against 141)
  - running, advanced, little enemy snare for own speed (lowest third, -28 or less): +3.0 (n 95 against 97)
  - running, advanced, middle third: +1.4 (n 87 against 148)
  - running, advanced, a lot of enemy snare for own speed (top third, above -2): +1.2 (n 71 against 141)
  - not running, advanced, little enemy snare for own speed (lowest third, -28 or less): +1.2 (n 97 against 97)
  - not running, advanced, middle third: +1.1 (n 87 against 148)
  - not running, advanced, a lot of enemy snare for own speed (top third, above -2): -0.1 (n 66 against 141)
  - running, fought, little enemy snare for own speed (lowest third, -28 or less): +3.8 (n 85 against 97)
  - running, fought, middle third: +0.5 (n 57 against 148)
  - running, fought, a lot of enemy snare for own speed (top third, above -2): +2.7 (n 63 against 141)
  - not running, held, little enemy snare for own speed (lowest third, -28 or less): +2.2 (n 41 against 97)
  - not running, held, middle third: -0.6 (n 45 against 148)
  - not running, held, a lot of enemy snare for own speed (top third, above -2): +0.2 (n 64 against 141)
  - running, fell back, little enemy snare for own speed (lowest third, -28 or less): +3.0 (n 61 against 97)
  - running, fell back, middle third: +3.7 (n 46 against 148)
  - running, fell back, a lot of enemy snare for own speed (top third, above -2): +1.1 (n 41 against 141)
  - running, held, little enemy snare for own speed (lowest third, -28 or less): +2.6 (n 34 against 97)
  - running, held, middle third: +0.8 (n 33 against 148)
  - running, held, a lot of enemy snare for own speed (top third, above -2): +1.1 (n 30 against 141)
  - not running, to the spawn, little enemy snare for own speed (lowest third, -28 or less): too few yet (n 5 against 97; means -2.7 against -2.2)
  - not running, to the spawn, middle third: too few yet (n 5 against 148; means 0.5 against -1.0)
  - not running, to the spawn, a lot of enemy snare for own speed (top third, above -2): +0.2 (n 21 against 141)
  - running, to the spawn, little enemy snare for own speed (lowest third, -28 or less): too few yet (n 2 against 97; means 0.9 against -2.2)
  - running, to the spawn, middle third: too few yet (n 2 against 148; means 0.1 against -1.0)
  - running, to the spawn, a lot of enemy snare for own speed (top third, above -2): too few yet (n 4 against 141; means 3.4 against -0.0)
  - not running, a lot of enemy snare for own speed (top third, above -2): too few yet (n 7 against 141; means -0.4 against -0.0)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - not running, fell back, Corrupted Isle: +3.8 (n 49 against 48)
  - not running, fell back, Druid's Isle: -1.1 (n 45 against 46)
  - not running, fell back, Imperial Isle: +10.2 (n 11 against 11)
  - not running, fell back, Isle of Jade: -2.8 (n 27 against 58)
  - not running, fell back, Isle of Meditation: +0.2 (n 50 against 77)
  - not running, fell back, Isle of Solitude: -1.4 (n 45 against 60)
  - not running, fell back, Isle of Weeping Stone: -8.0 (n 19 against 17)
  - not running, fell back, Uncharted Isle: -1.8 (n 50 against 52)
  - running, advanced, Corrupted Isle: +3.7 (n 43 against 48)
  - running, advanced, Druid's Isle: -0.3 (n 28 against 46)
  - running, advanced, Isle of Jade: -2.3 (n 17 against 58)
  - running, advanced, Isle of Meditation: +3.6 (n 57 against 77)
  - running, advanced, Isle of Solitude: +1.7 (n 39 against 60)
  - running, advanced, Isle of Weeping Stone: -3.9 (n 33 against 17)
  - running, advanced, Uncharted Isle: -0.2 (n 22 against 52)
  - not running, advanced, Corrupted Isle: +4.8 (n 49 against 48)
  - not running, advanced, Druid's Isle: +3.3 (n 20 against 46)
  - not running, advanced, Imperial Isle: +5.3 (n 13 against 11)
  - not running, advanced, Isle of Jade: -1.1 (n 20 against 58)
  - not running, advanced, Isle of Meditation: +0.6 (n 43 against 77)
  - not running, advanced, Isle of Solitude: -0.6 (n 41 against 60)
  - not running, advanced, Isle of Weeping Stone: -6.3 (n 15 against 17)
  - not running, advanced, Uncharted Isle: -1.8 (n 45 against 52)
  - running, fought, Corrupted Isle: +3.7 (n 23 against 48)
  - running, fought, Druid's Isle: +0.5 (n 41 against 46)
  - running, fought, Isle of Jade: +0.9 (n 11 against 58)
  - running, fought, Isle of Meditation: +1.4 (n 46 against 77)
  - running, fought, Isle of Solitude: +3.9 (n 38 against 60)
  - running, fought, Isle of Weeping Stone: -0.6 (n 12 against 17)
  - running, fought, Uncharted Isle: +1.2 (n 22 against 52)
  - not running, held, Corrupted Isle: +1.4 (n 22 against 48)
  - not running, held, Druid's Isle: +0.8 (n 22 against 46)
  - not running, held, Isle of Jade: +0.1 (n 30 against 58)
  - not running, held, Isle of Meditation: +2.1 (n 16 against 77)
  - not running, held, Isle of Solitude: -0.1 (n 35 against 60)
  - running, fell back, Corrupted Isle: +6.8 (n 20 against 48)
  - running, fell back, Druid's Isle: +2.9 (n 16 against 46)
  - running, fell back, Isle of Meditation: +0.9 (n 26 against 77)
  - running, fell back, Isle of Solitude: +2.4 (n 28 against 60)
  - running, fell back, Isle of Weeping Stone: -4.7 (n 19 against 17)
  - running, fell back, Uncharted Isle: +2.8 (n 28 against 52)
  - running, held, Druid's Isle: -0.9 (n 10 against 46)
  - running, held, Isle of Jade: -0.1 (n 31 against 58)
  - running, held, Isle of Solitude: +1.6 (n 14 against 60)
  - running, held, Uncharted Isle: +3.7 (n 10 against 52)
  - not running, to the spawn, Isle of Jade: +0.6 (n 10 against 58)

**eight v eight or flag** (4374 decisions, 464 matches; usual: flag game)
- commit all 8 (n 1255): +0.5 [-0.8, +1.6]; in the 30 s before: -1.2 [-1.7, -0.8] ALREADY DIFFERENT BEFORE: partly who chooses it
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - commit all 8, Corrupted Isle: +2.3 (n 134 against 516)
  - commit all 8, Druid's Isle: -2.0 (n 238 against 232)
  - commit all 8, Imperial Isle: -2.0 (n 54 against 196)
  - commit all 8, Isle of Jade: -0.1 (n 230 against 179)
  - commit all 8, Isle of Meditation: +0.2 (n 185 against 401)
  - commit all 8, Isle of Solitude: -0.9 (n 180 against 473)
  - commit all 8, Isle of Weeping Stone: -0.8 (n 99 against 342)
  - commit all 8, Nomad's Isle: +1.9 (n 31 against 97)
  - commit all 8, Uncharted Isle: +1.0 (n 101 against 680)

**enemy pickup** (6098 decisions, 482 matches; usual: held, advanced)
- already running, advanced (n 825): -0.6 [-1.8, +0.9]; in the 30 s before: +1.3 [+0.4, +2.4] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, fell back (n 825): -0.7 [-1.8, +0.7]; in the 30 s before: -0.6 [-1.5, +0.5]
- held, fought (n 648): -1.0 [-2.1, +0.1]; in the 30 s before: +0.0 [-0.7, +0.8]
- already running, fell back (n 622): -0.3 [-1.7, +1.2]; in the 30 s before: +0.5 [-0.4, +1.6]
- already running, fought (n 487): -1.4 [-2.7, +0.3]; in the 30 s before: +1.1 [+0.1, +2.0] ALREADY DIFFERENT BEFORE: partly who chooses it
- ran, fell back (n 460): +1.1 [-0.1, +2.5]; in the 30 s before: +0.2 [-0.7, +1.2]
- ran, advanced (n 377): -0.6 [-1.9, +1.2]; in the 30 s before: +1.1 [-0.0, +2.4]
- ran, fought (n 262): -0.2 [-1.3, +1.1]; in the 30 s before: +0.5 [-0.5, +1.8]
- already running, held (n 255): -1.6 [-3.0, +0.1]; in the 30 s before: +1.5 [+0.4, +2.6] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, held (n 252): -0.2 [-1.3, +1.4]; in the 30 s before: -0.2 [-1.3, +0.9]
- ran, held (n 150): +0.1 [-1.1, +2.1]; in the 30 s before: +1.1 [-0.2, +2.2]
- held, to the spawn (n 13): -0.4 [-5.4, +8.7]; in the 30 s before: +1.5 [-2.0, +4.7]
- held (n 12): -9.2 [-15.6, -4.2] CLEAR; in the 30 s before: +7.9 [+5.2, +11.1] ALREADY DIFFERENT BEFORE: partly who chooses it
- ran, to the spawn (n 10): -1.1 [-3.4, +1.7]; in the 30 s before: +0.8 [-0.8, +3.7]
- already running, to the spawn (n 9): +4.4 [-2.3, +12.4]; in the 30 s before: +0.3 [-1.9, +3.0]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - already running, advanced, behind in the fight (lowest third, -0.01 or less): +1.5 (n 235 against 225)
  - already running, advanced, middle third: +0.3 (n 365 against 264)
  - already running, advanced, ahead in the fight (top third, above +0.02): -0.7 (n 225 against 402)
  - held, fell back, behind in the fight (lowest third, -0.01 or less): +0.2 (n 361 against 225)
  - held, fell back, middle third: -0.1 (n 217 against 264)
  - held, fell back, ahead in the fight (top third, above +0.02): -1.3 (n 247 against 402)
  - held, fought, behind in the fight (lowest third, -0.01 or less): -0.9 (n 171 against 225)
  - held, fought, middle third: -0.7 (n 125 against 264)
  - held, fought, ahead in the fight (top third, above +0.02): -1.7 (n 352 against 402)
  - already running, fell back, behind in the fight (lowest third, -0.01 or less): +1.1 (n 274 against 225)
  - already running, fell back, middle third: +0.9 (n 228 against 264)
  - already running, fell back, ahead in the fight (top third, above +0.02): +0.4 (n 120 against 402)
  - already running, fought, behind in the fight (lowest third, -0.01 or less): +0.7 (n 166 against 225)
  - already running, fought, middle third: -0.3 (n 135 against 264)
  - already running, fought, ahead in the fight (top third, above +0.02): -2.0 (n 186 against 402)
  - ran, fell back, behind in the fight (lowest third, -0.01 or less): +2.6 (n 175 against 225)
  - ran, fell back, middle third: +2.4 (n 162 against 264)
  - ran, fell back, ahead in the fight (top third, above +0.02): -1.0 (n 123 against 402)
  - ran, advanced, behind in the fight (lowest third, -0.01 or less): +2.3 (n 111 against 225)
  - ran, advanced, middle third: -0.1 (n 143 against 264)
  - ran, advanced, ahead in the fight (top third, above +0.02): -2.4 (n 123 against 402)
  - ran, fought, behind in the fight (lowest third, -0.01 or less): +2.1 (n 98 against 225)
  - ran, fought, middle third: +0.2 (n 77 against 264)
  - ran, fought, ahead in the fight (top third, above +0.02): -2.4 (n 87 against 402)
  - already running, held, behind in the fight (lowest third, -0.01 or less): -0.0 (n 74 against 225)
  - already running, held, middle third: -0.4 (n 132 against 264)
  - already running, held, ahead in the fight (top third, above +0.02): -1.1 (n 49 against 402)
  - held, held, behind in the fight (lowest third, -0.01 or less): -1.2 (n 65 against 225)
  - held, held, middle third: +2.7 (n 103 against 264)
  - held, held, ahead in the fight (top third, above +0.02): -2.1 (n 84 against 402)
  - ran, held, behind in the fight (lowest third, -0.01 or less): +1.7 (n 62 against 225)
  - ran, held, middle third: +1.9 (n 61 against 264)
  - ran, held, ahead in the fight (top third, above +0.02): -2.6 (n 27 against 402)
  - held, to the spawn, behind in the fight (lowest third, -0.01 or less): too few yet (n 7 against 225; means 5.9 against -1.0)
  - held, to the spawn, middle third: too few yet (n 5 against 264; means -0.5 against -0.6)
  - held, to the spawn, ahead in the fight (top third, above +0.02): too few yet (n 1 against 402; means -6.0 against 0.9)
  - held, behind in the fight (lowest third, -0.01 or less): too few yet (n 6 against 225; means -5.8 against -1.0)
  - held, middle third: too few yet (n 5 against 264; means -0.3 against -0.6)
  - held, ahead in the fight (top third, above +0.02): too few yet (n 1 against 402; means 0.0 against 0.9)
  - ran, to the spawn, behind in the fight (lowest third, -0.01 or less): too few yet (n 4 against 225; means -1.9 against -1.0)
  - ran, to the spawn, middle third: too few yet (n 2 against 264; means 0.8 against -0.6)
  - ran, to the spawn, ahead in the fight (top third, above +0.02): too few yet (n 4 against 402; means -0.1 against 0.9)
  - already running, to the spawn, behind in the fight (lowest third, -0.01 or less): too few yet (n 6 against 225; means 8.5 against -1.0)
  - already running, to the spawn, middle third: too few yet (n 2 against 264; means -4.1 against -0.6)
  - already running, to the spawn, ahead in the fight (top third, above +0.02): too few yet (n 1 against 402; means -0.1 against 0.9)
  By snare matchup (movepower.py: enemy snare power of the live players minus own speed power; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - already running, advanced, little enemy snare for own speed (lowest third, -33 or less): +1.7 (n 315 against 292)
  - already running, advanced, middle third: -4.3 (n 258 against 307)
  - already running, advanced, a lot of enemy snare for own speed (top third, above -6): +3.0 (n 252 against 292)
  - held, fell back, little enemy snare for own speed (lowest third, -33 or less): -0.4 (n 264 against 292)
  - held, fell back, middle third: -2.4 (n 266 against 307)
  - held, fell back, a lot of enemy snare for own speed (top third, above -6): +1.2 (n 295 against 292)
  - held, fought, little enemy snare for own speed (lowest third, -33 or less): +0.6 (n 216 against 292)
  - held, fought, middle third: -3.0 (n 230 against 307)
  - held, fought, a lot of enemy snare for own speed (top third, above -6): -1.0 (n 202 against 292)
  - already running, fell back, little enemy snare for own speed (lowest third, -33 or less): +1.7 (n 234 against 292)
  - already running, fell back, middle third: -3.4 (n 196 against 307)
  - already running, fell back, a lot of enemy snare for own speed (top third, above -6): +3.1 (n 192 against 292)
  - already running, fought, little enemy snare for own speed (lowest third, -33 or less): +0.2 (n 142 against 292)
  - already running, fought, middle third: -4.4 (n 180 against 307)
  - already running, fought, a lot of enemy snare for own speed (top third, above -6): +2.1 (n 165 against 292)
  - ran, fell back, little enemy snare for own speed (lowest third, -33 or less): +3.9 (n 155 against 292)
  - ran, fell back, middle third: -2.6 (n 146 against 307)
  - ran, fell back, a lot of enemy snare for own speed (top third, above -6): +2.7 (n 159 against 292)
  - ran, advanced, little enemy snare for own speed (lowest third, -33 or less): +1.9 (n 120 against 292)
  - ran, advanced, middle third: -3.8 (n 121 against 307)
  - ran, advanced, a lot of enemy snare for own speed (top third, above -6): +1.1 (n 136 against 292)
  - ran, fought, little enemy snare for own speed (lowest third, -33 or less): +0.3 (n 79 against 292)
  - ran, fought, middle third: -1.9 (n 92 against 307)
  - ran, fought, a lot of enemy snare for own speed (top third, above -6): +1.0 (n 91 against 292)
  - already running, held, little enemy snare for own speed (lowest third, -33 or less): +1.2 (n 95 against 292)
  - already running, held, middle third: -5.5 (n 83 against 307)
  - already running, held, a lot of enemy snare for own speed (top third, above -6): +1.9 (n 77 against 292)
  - held, held, little enemy snare for own speed (lowest third, -33 or less): +1.1 (n 82 against 292)
  - held, held, middle third: -3.4 (n 75 against 307)
  - held, held, a lot of enemy snare for own speed (top third, above -6): +2.3 (n 95 against 292)
  - ran, held, little enemy snare for own speed (lowest third, -33 or less): +2.1 (n 43 against 292)
  - ran, held, middle third: -2.1 (n 52 against 307)
  - ran, held, a lot of enemy snare for own speed (top third, above -6): +1.8 (n 55 against 292)
  - held, to the spawn, little enemy snare for own speed (lowest third, -33 or less): too few yet (n 4 against 292; means -4.2 against -1.7)
  - held, to the spawn, middle third: too few yet (n 2 against 307; means -5.8 against 3.7)
  - held, to the spawn, a lot of enemy snare for own speed (top third, above -6): too few yet (n 7 against 292; means 8.8 against -2.3)
  - held, little enemy snare for own speed (lowest third, -33 or less): too few yet (n 1 against 292; means -35.0 against -1.7)
  - held, a lot of enemy snare for own speed (top third, above -6): +2.2 (n 11 against 292)
  - ran, to the spawn, little enemy snare for own speed (lowest third, -33 or less): too few yet (n 5 against 292; means -0.0 against -1.7)
  - ran, to the spawn, middle third: too few yet (n 4 against 307; means -1.6 against 3.7)
  - ran, to the spawn, a lot of enemy snare for own speed (top third, above -6): too few yet (n 1 against 292; means 0.3 against -2.3)
  - already running, to the spawn, little enemy snare for own speed (lowest third, -33 or less): too few yet (n 1 against 292; means 1.4 against -1.7)
  - already running, to the spawn, middle third: too few yet (n 5 against 307; means 2.4 against 3.7)
  - already running, to the spawn, a lot of enemy snare for own speed (top third, above -6): too few yet (n 3 against 292; means 9.9 against -2.3)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - already running, advanced, Corrupted Isle: -0.9 (n 168 against 159)
  - already running, advanced, Druid's Isle: -0.7 (n 57 against 73)
  - already running, advanced, Imperial Isle: -3.0 (n 40 against 51)
  - already running, advanced, Isle of Jade: -1.7 (n 50 against 88)
  - already running, advanced, Isle of Meditation: -0.3 (n 118 against 126)
  - already running, advanced, Isle of Solitude: +2.2 (n 123 against 120)
  - already running, advanced, Isle of Weeping Stone: +4.1 (n 96 against 83)
  - already running, advanced, Uncharted Isle: -0.7 (n 162 against 174)
  - held, fell back, Corrupted Isle: -2.7 (n 159 against 159)
  - held, fell back, Druid's Isle: -2.6 (n 60 against 73)
  - held, fell back, Imperial Isle: -1.6 (n 31 against 51)
  - held, fell back, Isle of Jade: +3.7 (n 70 against 88)
  - held, fell back, Isle of Meditation: -1.6 (n 126 against 126)
  - held, fell back, Isle of Solitude: +1.3 (n 119 against 120)
  - held, fell back, Isle of Weeping Stone: +1.9 (n 86 against 83)
  - held, fell back, Nomad's Isle: +0.1 (n 17 against 17)
  - held, fell back, Uncharted Isle: -1.1 (n 156 against 174)
  - held, fought, Corrupted Isle: +1.4 (n 74 against 159)
  - held, fought, Druid's Isle: -2.4 (n 120 against 73)
  - held, fought, Imperial Isle: -3.7 (n 23 against 51)
  - held, fought, Isle of Jade: -2.4 (n 57 against 88)
  - held, fought, Isle of Meditation: -0.5 (n 124 against 126)
  - held, fought, Isle of Solitude: -0.6 (n 86 against 120)
  - held, fought, Isle of Weeping Stone: +2.9 (n 49 against 83)
  - held, fought, Nomad's Isle: -2.9 (n 40 against 17)
  - held, fought, Uncharted Isle: -4.4 (n 73 against 174)
  - already running, fell back, Corrupted Isle: +0.4 (n 114 against 159)
  - already running, fell back, Druid's Isle: -0.1 (n 36 against 73)
  - already running, fell back, Imperial Isle: -2.1 (n 21 against 51)
  - already running, fell back, Isle of Jade: +2.0 (n 25 against 88)
  - already running, fell back, Isle of Meditation: -0.3 (n 94 against 126)
  - already running, fell back, Isle of Solitude: +2.0 (n 92 against 120)
  - already running, fell back, Isle of Weeping Stone: +4.0 (n 63 against 83)
  - already running, fell back, Nomad's Isle: -2.6 (n 19 against 17)
  - already running, fell back, Uncharted Isle: -1.2 (n 158 against 174)
  - already running, fought, Corrupted Isle: -3.1 (n 63 against 159)
  - already running, fought, Druid's Isle: -4.6 (n 63 against 73)
  - already running, fought, Imperial Isle: +0.8 (n 30 against 51)
  - already running, fought, Isle of Jade: +2.4 (n 21 against 88)
  - already running, fought, Isle of Meditation: -1.3 (n 70 against 126)
  - already running, fought, Isle of Solitude: +0.9 (n 85 against 120)
  - already running, fought, Isle of Weeping Stone: +4.4 (n 59 against 83)
  - already running, fought, Nomad's Isle: -2.0 (n 28 against 17)
  - already running, fought, Uncharted Isle: -1.9 (n 68 against 174)
  - ran, fell back, Corrupted Isle: +3.4 (n 86 against 159)
  - ran, fell back, Druid's Isle: -2.8 (n 30 against 73)
  - ran, fell back, Imperial Isle: -0.5 (n 24 against 51)
  - ran, fell back, Isle of Jade: +3.8 (n 30 against 88)
  - ran, fell back, Isle of Meditation: -0.7 (n 53 against 126)
  - ran, fell back, Isle of Solitude: +0.9 (n 75 against 120)
  - ran, fell back, Isle of Weeping Stone: +5.0 (n 48 against 83)
  - ran, fell back, Uncharted Isle: +0.9 (n 107 against 174)
  - ran, advanced, Corrupted Isle: -2.2 (n 52 against 159)
  - ran, advanced, Druid's Isle: -3.1 (n 17 against 73)
  - ran, advanced, Imperial Isle: -2.8 (n 44 against 51)
  - ran, advanced, Isle of Jade: +3.6 (n 41 against 88)
  - ran, advanced, Isle of Meditation: +1.0 (n 49 against 126)
  - ran, advanced, Isle of Solitude: +0.1 (n 45 against 120)
  - ran, advanced, Isle of Weeping Stone: +5.2 (n 43 against 83)
  - ran, advanced, Uncharted Isle: -3.1 (n 84 against 174)
  - ran, fought, Corrupted Isle: +3.1 (n 20 against 159)
  - ran, fought, Druid's Isle: +0.5 (n 42 against 73)
  - ran, fought, Imperial Isle: -5.1 (n 35 against 51)
  - ran, fought, Isle of Jade: -3.0 (n 14 against 88)
  - ran, fought, Isle of Meditation: +0.7 (n 37 against 126)
  - ran, fought, Isle of Solitude: +1.2 (n 40 against 120)
  - ran, fought, Isle of Weeping Stone: +1.7 (n 35 against 83)
  - ran, fought, Nomad's Isle: -2.7 (n 12 against 17)
  - ran, fought, Uncharted Isle: -1.3 (n 27 against 174)
  - already running, held, Corrupted Isle: -3.0 (n 18 against 159)
  - already running, held, Druid's Isle: -2.8 (n 31 against 73)
  - already running, held, Isle of Jade: +0.4 (n 28 against 88)
  - already running, held, Isle of Meditation: -3.4 (n 25 against 126)
  - already running, held, Isle of Solitude: +0.4 (n 50 against 120)
  - already running, held, Isle of Weeping Stone: +0.1 (n 28 against 83)
  - already running, held, Nomad's Isle: +1.2 (n 10 against 17)
  - already running, held, Uncharted Isle: +0.5 (n 55 against 174)
  - held, held, Corrupted Isle: -3.0 (n 19 against 159)
  - held, held, Druid's Isle: -1.6 (n 50 against 73)
  - held, held, Isle of Jade: +4.7 (n 54 against 88)
  - held, held, Isle of Meditation: -4.1 (n 31 against 126)
  - held, held, Isle of Solitude: +1.0 (n 28 against 120)
  - held, held, Isle of Weeping Stone: +0.1 (n 27 against 83)
  - held, held, Nomad's Isle: +1.7 (n 17 against 17)
  - held, held, Uncharted Isle: +0.7 (n 20 against 174)
  - ran, held, Corrupted Isle: -0.6 (n 14 against 159)
  - ran, held, Druid's Isle: -2.4 (n 20 against 73)
  - ran, held, Imperial Isle: -4.2 (n 17 against 51)
  - ran, held, Isle of Jade: +5.6 (n 31 against 88)
  - ran, held, Isle of Meditation: -0.9 (n 13 against 126)
  - ran, held, Isle of Solitude: +0.8 (n 20 against 120)
  - ran, held, Isle of Weeping Stone: +5.4 (n 13 against 83)
  - ran, held, Uncharted Isle: -1.6 (n 17 against 174)

**late game** (164 decisions, 82 matches; usual: 0 to 1 at the enemy Lord)
- 2 to 3 at the enemy Lord (n 60): +26.8 [+16.8, +36.8] CLEAR; in the 30 s before: -0.6 [-2.4, +1.2]
- 4+ at the enemy Lord (n 38): +43.4 [+24.7, +59.7] CLEAR; in the 30 s before: -1.0 [-3.0, +1.1]
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - 2 to 3 at the enemy Lord, Isle of Solitude: +10.4 (n 13 against 12)
  - 2 to 3 at the enemy Lord, Uncharted Isle: +16.7 (n 15 against 12)

**npcs or dp** (296 decisions, 227 matches; usual: NPCs)
- DP (n 63): -1.5 [-4.3, +0.8]; in the 30 s before: -0.7 [-2.9, +1.3]
- both (n 58): -0.1 [-2.2, +1.9]; in the 30 s before: -0.8 [-2.9, +1.7]
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - DP, Druid's Isle: -1.9 (n 11 against 21)
  - DP, Isle of Jade: +1.6 (n 10 against 31)
  - DP, Isle of Meditation: -0.1 (n 15 against 30)
  - DP, Isle of Solitude: -1.3 (n 11 against 24)
  - both, Druid's Isle: +3.9 (n 11 against 21)
  - both, Isle of Solitude: +0.1 (n 12 against 24)
  - both, Uncharted Isle: -3.3 (n 10 against 22)

**offence or defence** (1274 decisions, 423 matches; usual: defensive)
- offensive (n 462): +2.2 [+1.0, +3.5] CLEAR; in the 30 s before: +0.1 [-0.6, +0.8]
- mixed (n 308): +0.9 [-0.4, +2.4]; in the 30 s before: -0.1 [-0.9, +0.6]
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - offensive, Corrupted Isle: +5.1 (n 69 against 59)
  - offensive, Druid's Isle: +1.6 (n 57 against 72)
  - offensive, Imperial Isle: +2.2 (n 21 against 21)
  - offensive, Isle of Jade: +1.8 (n 50 against 85)
  - offensive, Isle of Meditation: +3.3 (n 84 against 91)
  - offensive, Isle of Solitude: +4.4 (n 61 against 64)
  - offensive, Isle of Weeping Stone: +4.7 (n 35 against 21)
  - offensive, Nomad's Isle: +0.1 (n 16 against 13)
  - offensive, Uncharted Isle: +1.3 (n 66 against 70)
  - mixed, Corrupted Isle: +3.5 (n 56 against 59)
  - mixed, Druid's Isle: -1.9 (n 42 against 72)
  - mixed, Isle of Jade: +3.1 (n 37 against 85)
  - mixed, Isle of Meditation: -1.4 (n 47 against 91)
  - mixed, Isle of Solitude: +3.6 (n 49 against 64)
  - mixed, Isle of Weeping Stone: +3.5 (n 24 against 21)
  - mixed, Uncharted Isle: +1.0 (n 34 against 70)

**play for 28 or lord** (4046 decisions, 256 matches; usual: play for 28)
- push for the kill (n 1202): +1.5 [+0.7, +2.4] CLEAR; in the 30 s before: -0.2 [-0.6, +0.2]
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - push for the kill, Corrupted Isle: +0.9 (n 182 against 468)
  - push for the kill, Druid's Isle: +2.2 (n 76 against 129)
  - push for the kill, Imperial Isle: +2.4 (n 26 against 117)
  - push for the kill, Isle of Jade: +0.2 (n 82 against 187)
  - push for the kill, Isle of Meditation: +2.9 (n 166 against 478)
  - push for the kill, Isle of Solitude: +0.0 (n 254 against 509)
  - push for the kill, Isle of Weeping Stone: +2.5 (n 137 against 348)
  - push for the kill, Nomad's Isle: +3.2 (n 10 against 83)
  - push for the kill, Uncharted Isle: +1.2 (n 269 against 525)

**power play** (4646 decisions, 503 matches; usual: pushed, advanced)
- pushed, fought (n 985): +0.2 [-0.4, +0.9]; in the 30 s before: -0.1 [-0.7, +0.4]
- held, fought (n 557): -1.3 [-2.0, -0.5] CLEAR; in the 30 s before: -0.6 [-1.1, -0.1] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, fell back (n 510): -2.0 [-2.7, -1.3] CLEAR; in the 30 s before: -0.8 [-1.4, -0.3] ALREADY DIFFERENT BEFORE: partly who chooses it
- pushed, fell back (n 507): -0.6 [-1.3, +0.2]; in the 30 s before: -0.9 [-1.6, -0.4] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, advanced (n 351): -1.6 [-2.4, -0.9] CLEAR; in the 30 s before: -0.3 [-0.9, +0.1]
- pushed, held (n 171): -1.2 [-2.3, -0.2] CLEAR; in the 30 s before: +0.1 [-0.9, +0.9]
- held, held (n 170): -1.4 [-2.4, -0.4] CLEAR; in the 30 s before: -0.5 [-1.3, +0.3]
- pushed, to the spawn (n 15): +3.3 [-4.3, +12.8]; in the 30 s before: -1.5 [-4.6, +1.6]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - pushed, fought, behind in the fight (lowest third, +0.00 or less): +1.4 (n 281 against 409)
  - pushed, fought, middle third: -0.4 (n 273 against 471)
  - pushed, fought, ahead in the fight (top third, above +0.08): -0.2 (n 431 against 500)
  - held, fought, behind in the fight (lowest third, +0.00 or less): -0.3 (n 167 against 409)
  - held, fought, middle third: -1.3 (n 176 against 471)
  - held, fought, ahead in the fight (top third, above +0.08): -2.4 (n 214 against 500)
  - held, fell back, behind in the fight (lowest third, +0.00 or less): -2.3 (n 237 against 409)
  - held, fell back, middle third: -2.1 (n 178 against 471)
  - held, fell back, ahead in the fight (top third, above +0.08): -1.2 (n 95 against 500)
  - pushed, fell back, behind in the fight (lowest third, +0.00 or less): +0.6 (n 210 against 409)
  - pushed, fell back, middle third: -0.2 (n 160 against 471)
  - pushed, fell back, ahead in the fight (top third, above +0.08): -3.3 (n 137 against 500)
  - held, advanced, behind in the fight (lowest third, +0.00 or less): -0.6 (n 130 against 409)
  - held, advanced, middle third: -2.9 (n 112 against 471)
  - held, advanced, ahead in the fight (top third, above +0.08): -1.3 (n 109 against 500)
  - pushed, held, behind in the fight (lowest third, +0.00 or less): -1.0 (n 73 against 409)
  - pushed, held, middle third: -0.5 (n 61 against 471)
  - pushed, held, ahead in the fight (top third, above +0.08): -1.9 (n 37 against 500)
  - held, held, behind in the fight (lowest third, +0.00 or less): +0.1 (n 73 against 409)
  - held, held, middle third: -2.3 (n 73 against 471)
  - held, held, ahead in the fight (top third, above +0.08): -1.8 (n 24 against 500)
  - pushed, to the spawn, behind in the fight (lowest third, +0.00 or less): +6.7 (n 13 against 409)
  - pushed, to the spawn, middle third: too few yet (n 1 against 471; means -22.3 against 0.9)
  - pushed, to the spawn, ahead in the fight (top third, above +0.08): too few yet (n 1 against 500; means -0.2 against 2.5)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - pushed, fought, Corrupted Isle: +1.1 (n 121 against 251)
  - pushed, fought, Druid's Isle: -0.8 (n 169 against 137)
  - pushed, fought, Imperial Isle: -0.4 (n 32 against 56)
  - pushed, fought, Isle of Jade: +1.6 (n 101 against 107)
  - pushed, fought, Isle of Meditation: -0.5 (n 146 against 273)
  - pushed, fought, Isle of Solitude: -0.3 (n 163 against 195)
  - pushed, fought, Isle of Weeping Stone: +1.1 (n 84 against 132)
  - pushed, fought, Nomad's Isle: -0.1 (n 48 against 17)
  - pushed, fought, Uncharted Isle: +1.3 (n 116 against 209)
  - held, fought, Corrupted Isle: -0.2 (n 56 against 251)
  - held, fought, Druid's Isle: -2.8 (n 100 against 137)
  - held, fought, Imperial Isle: -2.7 (n 24 against 56)
  - held, fought, Isle of Jade: -3.2 (n 52 against 107)
  - held, fought, Isle of Meditation: -2.3 (n 98 against 273)
  - held, fought, Isle of Solitude: -1.2 (n 100 against 195)
  - held, fought, Isle of Weeping Stone: -1.3 (n 36 against 132)
  - held, fought, Nomad's Isle: +2.0 (n 41 against 17)
  - held, fought, Uncharted Isle: -0.4 (n 50 against 209)
  - held, fell back, Corrupted Isle: -1.9 (n 66 against 251)
  - held, fell back, Druid's Isle: -2.7 (n 51 against 137)
  - held, fell back, Imperial Isle: -2.4 (n 27 against 56)
  - held, fell back, Isle of Jade: -3.6 (n 29 against 107)
  - held, fell back, Isle of Meditation: -2.1 (n 85 against 273)
  - held, fell back, Isle of Solitude: -2.1 (n 102 against 195)
  - held, fell back, Isle of Weeping Stone: -3.9 (n 43 against 132)
  - held, fell back, Nomad's Isle: +0.9 (n 20 against 17)
  - held, fell back, Uncharted Isle: -1.5 (n 87 against 209)
  - pushed, fell back, Corrupted Isle: -1.1 (n 90 against 251)
  - pushed, fell back, Druid's Isle: -1.8 (n 36 against 137)
  - pushed, fell back, Imperial Isle: -1.5 (n 18 against 56)
  - pushed, fell back, Isle of Jade: -3.3 (n 34 against 107)
  - pushed, fell back, Isle of Meditation: -0.4 (n 70 against 273)
  - pushed, fell back, Isle of Solitude: +0.9 (n 106 against 195)
  - pushed, fell back, Isle of Weeping Stone: -2.5 (n 44 against 132)
  - pushed, fell back, Nomad's Isle: -0.4 (n 18 against 17)
  - pushed, fell back, Uncharted Isle: +0.4 (n 86 against 209)
  - held, advanced, Corrupted Isle: -0.1 (n 52 against 251)
  - held, advanced, Druid's Isle: -2.0 (n 34 against 137)
  - held, advanced, Imperial Isle: -1.6 (n 21 against 56)
  - held, advanced, Isle of Jade: -1.3 (n 31 against 107)
  - held, advanced, Isle of Meditation: -1.4 (n 65 against 273)
  - held, advanced, Isle of Solitude: -1.8 (n 57 against 195)
  - held, advanced, Isle of Weeping Stone: -2.8 (n 32 against 132)
  - held, advanced, Uncharted Isle: -3.2 (n 53 against 209)
  - pushed, held, Corrupted Isle: -5.3 (n 15 against 251)
  - pushed, held, Druid's Isle: -3.8 (n 27 against 137)
  - pushed, held, Isle of Jade: +1.0 (n 15 against 107)
  - pushed, held, Isle of Meditation: -1.4 (n 29 against 273)
  - pushed, held, Isle of Solitude: -1.4 (n 29 against 195)
  - pushed, held, Isle of Weeping Stone: -2.4 (n 23 against 132)
  - pushed, held, Uncharted Isle: +0.9 (n 25 against 209)
  - held, held, Corrupted Isle: -2.1 (n 10 against 251)
  - held, held, Druid's Isle: -3.9 (n 51 against 137)
  - held, held, Isle of Jade: -7.3 (n 10 against 107)
  - held, held, Isle of Meditation: -1.8 (n 17 against 273)
  - held, held, Isle of Solitude: -0.1 (n 26 against 195)
  - held, held, Isle of Weeping Stone: -1.3 (n 15 against 132)
  - held, held, Nomad's Isle: +2.4 (n 11 against 17)
  - held, held, Uncharted Isle: +0.4 (n 24 against 209)

**runner choice** (4218 decisions, 447 matches; usual: monk)
- dervish (n 780): -0.1 [-0.9, +1.0]; in the 30 s before: -0.4 [-1.1, +0.2]
- mesmer (n 775): +0.2 [-0.6, +1.3]; in the 30 s before: +0.2 [-0.3, +0.9]
- warrior (n 589): -0.9 [-1.8, -0.0] CLEAR; in the 30 s before: +0.3 [-0.3, +0.9]
- ritualist (n 522): +0.3 [-0.5, +1.4]; in the 30 s before: -0.5 [-1.1, +0.2]
- elementalist (n 270): +0.2 [-1.2, +1.4]; in the 30 s before: -0.0 [-1.0, +0.9]
- necromancer (n 171): +1.2 [-0.4, +3.0]; in the 30 s before: -1.5 [-2.8, -0.5] ALREADY DIFFERENT BEFORE: partly who chooses it
- ranger (n 86): +1.3 [-1.0, +3.6]; in the 30 s before: +0.9 [-0.1, +1.9]
- assassin (n 34): -0.7 [-4.4, +2.6]; in the 30 s before: +3.6 [+1.4, +5.6] ALREADY DIFFERENT BEFORE: partly who chooses it
- paragon (n 23): -0.4 [-2.9, +2.5]; in the 30 s before: +1.8 [-0.4, +4.1]
  By snare matchup (movepower.py: enemy snare power of the live players minus own speed power; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - dervish, little enemy snare for own speed (lowest third, -36 or less): -0.4 (n 231 against 298)
  - dervish, middle third: +1.3 (n 264 against 390)
  - dervish, a lot of enemy snare for own speed (top third, above -7): -0.6 (n 285 against 280)
  - mesmer, little enemy snare for own speed (lowest third, -36 or less): -0.5 (n 287 against 298)
  - mesmer, middle third: -1.5 (n 179 against 390)
  - mesmer, a lot of enemy snare for own speed (top third, above -7): +1.3 (n 309 against 280)
  - warrior, little enemy snare for own speed (lowest third, -36 or less): -1.2 (n 202 against 298)
  - warrior, middle third: -1.0 (n 201 against 390)
  - warrior, a lot of enemy snare for own speed (top third, above -7): -0.1 (n 186 against 280)
  - ritualist, little enemy snare for own speed (lowest third, -36 or less): -1.6 (n 207 against 298)
  - ritualist, middle third: +0.9 (n 188 against 390)
  - ritualist, a lot of enemy snare for own speed (top third, above -7): +1.9 (n 127 against 280)
  - elementalist, little enemy snare for own speed (lowest third, -36 or less): -2.5 (n 61 against 298)
  - elementalist, middle third: +0.5 (n 100 against 390)
  - elementalist, a lot of enemy snare for own speed (top third, above -7): +1.7 (n 109 against 280)
  - necromancer, little enemy snare for own speed (lowest third, -36 or less): -0.2 (n 69 against 298)
  - necromancer, middle third: +2.8 (n 41 against 390)
  - necromancer, a lot of enemy snare for own speed (top third, above -7): +1.4 (n 61 against 280)
  - ranger, little enemy snare for own speed (lowest third, -36 or less): -1.6 (n 33 against 298)
  - ranger, middle third: +0.4 (n 20 against 390)
  - ranger, a lot of enemy snare for own speed (top third, above -7): +4.4 (n 33 against 280)
  - assassin, little enemy snare for own speed (lowest third, -36 or less): too few yet (n 9 against 298; means -3.7 against 0.9)
  - assassin, middle third: +0.5 (n 15 against 390)
  - assassin, a lot of enemy snare for own speed (top third, above -7): +4.3 (n 10 against 280)
  - paragon, little enemy snare for own speed (lowest third, -36 or less): too few yet (n 9 against 298; means -0.1 against 0.9)
  - paragon, middle third: too few yet (n 8 against 390; means 3.9 against 0.1)
  - paragon, a lot of enemy snare for own speed (top third, above -7): too few yet (n 6 against 280; means -3.8 against -0.2)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - dervish, Corrupted Isle: -0.5 (n 98 against 220)
  - dervish, Druid's Isle: -2.9 (n 51 against 188)
  - dervish, Imperial Isle: +0.6 (n 39 against 15)
  - dervish, Isle of Jade: +0.7 (n 14 against 90)
  - dervish, Isle of Meditation: -0.8 (n 141 against 115)
  - dervish, Isle of Solitude: +1.2 (n 181 against 120)
  - dervish, Isle of Weeping Stone: -0.1 (n 82 against 119)
  - dervish, Uncharted Isle: +2.8 (n 167 against 84)
  - mesmer, Corrupted Isle: -0.2 (n 119 against 220)
  - mesmer, Druid's Isle: -2.5 (n 33 against 188)
  - mesmer, Imperial Isle: +0.6 (n 63 against 15)
  - mesmer, Isle of Jade: +1.1 (n 35 against 90)
  - mesmer, Isle of Meditation: +1.6 (n 102 against 115)
  - mesmer, Isle of Solitude: -0.1 (n 120 against 120)
  - mesmer, Isle of Weeping Stone: -1.1 (n 120 against 119)
  - mesmer, Nomad's Isle: -2.0 (n 20 against 17)
  - mesmer, Uncharted Isle: +2.8 (n 163 against 84)
  - warrior, Corrupted Isle: -2.6 (n 96 against 220)
  - warrior, Druid's Isle: -2.2 (n 46 against 188)
  - warrior, Imperial Isle: +1.5 (n 35 against 15)
  - warrior, Isle of Jade: +1.9 (n 37 against 90)
  - warrior, Isle of Meditation: -1.1 (n 71 against 115)
  - warrior, Isle of Solitude: +0.3 (n 94 against 120)
  - warrior, Isle of Weeping Stone: -1.0 (n 81 against 119)
  - warrior, Uncharted Isle: +1.6 (n 124 against 84)
  - ritualist, Corrupted Isle: -2.1 (n 57 against 220)
  - ritualist, Druid's Isle: -0.0 (n 26 against 188)
  - ritualist, Imperial Isle: +0.7 (n 11 against 15)
  - ritualist, Isle of Jade: +1.1 (n 30 against 90)
  - ritualist, Isle of Meditation: +0.8 (n 128 against 115)
  - ritualist, Isle of Solitude: +2.3 (n 93 against 120)
  - ritualist, Isle of Weeping Stone: -1.3 (n 73 against 119)
  - ritualist, Uncharted Isle: +3.0 (n 102 against 84)
  - elementalist, Corrupted Isle: +0.1 (n 59 against 220)
  - elementalist, Druid's Isle: -1.1 (n 27 against 188)
  - elementalist, Imperial Isle: +3.1 (n 29 against 15)
  - elementalist, Isle of Jade: +2.5 (n 32 against 90)
  - elementalist, Isle of Meditation: +1.3 (n 36 against 115)
  - elementalist, Isle of Solitude: -1.8 (n 30 against 120)
  - elementalist, Isle of Weeping Stone: +0.4 (n 29 against 119)
  - elementalist, Uncharted Isle: -0.2 (n 21 against 84)
  - necromancer, Druid's Isle: +0.1 (n 29 against 188)
  - necromancer, Isle of Jade: +0.3 (n 13 against 90)
  - necromancer, Isle of Meditation: +1.8 (n 33 against 115)
  - necromancer, Isle of Solitude: +1.8 (n 27 against 120)
  - necromancer, Isle of Weeping Stone: +3.9 (n 12 against 119)
  - necromancer, Uncharted Isle: +2.6 (n 41 against 84)
  - ranger, Corrupted Isle: +3.3 (n 12 against 220)
  - ranger, Isle of Meditation: -0.8 (n 22 against 115)
  - ranger, Uncharted Isle: +3.5 (n 17 against 84)
  - assassin, Isle of Solitude: +0.5 (n 10 against 120)

**split in base** (999 decisions, 323 matches; usual: defended without a collapse)
- collapsed (n 420): -1.8 [-3.2, -0.3] CLEAR; in the 30 s before: +0.5 [-0.2, +1.4]
- missed (n 114): -1.2 [-3.2, +1.1]; in the 30 s before: +1.6 [+0.5, +2.9] ALREADY DIFFERENT BEFORE: partly who chooses it
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - collapsed, Corrupted Isle: -1.8 (n 71 against 78)
  - collapsed, Druid's Isle: -0.6 (n 34 against 16)
  - collapsed, Isle of Meditation: -1.0 (n 78 against 58)
  - collapsed, Isle of Solitude: +0.2 (n 83 against 128)
  - collapsed, Isle of Weeping Stone: +1.7 (n 27 against 52)
  - collapsed, Uncharted Isle: -0.4 (n 63 against 115)
  - missed, Corrupted Isle: -0.9 (n 14 against 78)
  - missed, Isle of Solitude: -0.9 (n 40 against 128)
  - missed, Uncharted Isle: -4.4 (n 27 against 115)

**split or stay** (17779 decisions, 505 matches; usual: stayed)
- split (n 1793): -0.5 [-1.0, -0.2] CLEAR; in the 30 s before: +0.2 [-0.1, +0.4]
  By snare matchup (movepower.py: enemy snare power of the live players minus own speed power; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - split, little enemy snare for own speed (lowest third, -34 or less): -0.4 (n 655 against 5361)
  - split, middle third: +0.1 (n 559 against 5303)
  - split, a lot of enemy snare for own speed (top third, above -7): -1.5 (n 579 against 5322)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - split, Corrupted Isle: -2.2 (n 275 against 2201)
  - split, Druid's Isle: +1.1 (n 147 against 2343)
  - split, Imperial Isle: -0.7 (n 59 against 556)
  - split, Isle of Jade: +1.4 (n 102 against 2014)
  - split, Isle of Meditation: -0.2 (n 299 against 2496)
  - split, Isle of Solitude: -0.9 (n 317 against 2373)
  - split, Isle of Weeping Stone: -1.6 (n 165 against 1438)
  - split, Nomad's Isle: -0.9 (n 53 against 464)
  - split, Uncharted Isle: -0.3 (n 374 against 2033)

**who defends** (899 decisions, 306 matches; usual: midline alone)
- frontline with a collapse (n 128): -0.9 [-3.1, +1.4]; in the 30 s before: +1.0 [-0.2, +2.3]
- frontline alone (n 118): +0.7 [-1.4, +3.1]; in the 30 s before: -0.1 [-1.6, +1.2]
- midline with a collapse (n 109): -0.9 [-3.4, +1.6]; in the 30 s before: +0.8 [-0.6, +1.9]
- 8 Monk alone (n 79): +2.9 [-0.5, +6.7]; in the 30 s before: +1.9 [+0.5, +3.7] ALREADY DIFFERENT BEFORE: partly who chooses it
- 8 Monk with a collapse (n 74): +0.1 [-2.2, +3.5]; in the 30 s before: +0.5 [-0.9, +1.7]
- healer alone (n 50): -0.1 [-4.7, +5.3]; in the 30 s before: +0.4 [-1.1, +1.8]
- healer with a collapse (n 47): -2.1 [-6.1, +2.0]; in the 30 s before: +2.4 [+0.3, +4.0] ALREADY DIFFERENT BEFORE: partly who chooses it
- Mes/A alone (n 45): +0.6 [-2.8, +4.0]; in the 30 s before: +0.4 [-1.4, +2.3]
- Mes/A with a collapse (n 42): +0.6 [-3.2, +4.9]; in the 30 s before: +1.0 [-0.8, +2.6]
- backline alone (n 36): +3.1 [-1.9, +8.5]; in the 30 s before: -0.2 [-2.0, +1.5]
- backline with a collapse (n 20): -0.2 [-5.8, +5.7]; in the 30 s before: -2.4 [-4.5, -0.5] ALREADY DIFFERENT BEFORE: partly who chooses it
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - frontline with a collapse, Corrupted Isle: +2.3 (n 17 against 22)
  - frontline with a collapse, Isle of Meditation: +1.2 (n 22 against 21)
  - frontline with a collapse, Isle of Solitude: +2.2 (n 34 against 44)
  - frontline with a collapse, Isle of Weeping Stone: +3.0 (n 12 against 21)
  - frontline with a collapse, Uncharted Isle: -2.1 (n 27 against 36)
  - frontline alone, Corrupted Isle: +2.5 (n 12 against 22)
  - frontline alone, Isle of Meditation: -1.6 (n 16 against 21)
  - frontline alone, Isle of Solitude: +5.0 (n 31 against 44)
  - frontline alone, Uncharted Isle: -0.9 (n 45 against 36)
  - midline with a collapse, Corrupted Isle: +0.4 (n 19 against 22)
  - midline with a collapse, Isle of Meditation: -3.4 (n 27 against 21)
  - midline with a collapse, Isle of Solitude: +3.5 (n 25 against 44)
  - midline with a collapse, Uncharted Isle: -0.9 (n 16 against 36)
  - 8 Monk alone, Corrupted Isle: +0.7 (n 17 against 22)
  - 8 Monk alone, Isle of Solitude: +4.0 (n 30 against 44)
  - 8 Monk alone, Isle of Weeping Stone: +13.4 (n 10 against 21)
  - 8 Monk with a collapse, Corrupted Isle: -1.0 (n 10 against 22)
  - 8 Monk with a collapse, Isle of Meditation: +3.9 (n 12 against 21)
  - 8 Monk with a collapse, Isle of Solitude: +3.7 (n 13 against 44)
  - healer alone, Isle of Solitude: -0.1 (n 12 against 44)
  - healer alone, Uncharted Isle: +4.8 (n 11 against 36)
  - healer with a collapse, Corrupted Isle: -0.6 (n 12 against 22)
  - Mes/A alone, Isle of Solitude: +4.2 (n 10 against 44)
  - Mes/A alone, Uncharted Isle: -3.5 (n 16 against 36)
  - backline alone, Corrupted Isle: +4.1 (n 15 against 22)

**Collapses on a split: time away and its cost** (`S32`; per collapse, averages; main = what the main fight lost while the collapsers were away)

| Group | Cases | Away (median s) | Split killed | Collapser died | Own deaths at main | Enemy deaths at main | Flag lead change | DP change | Win change |
|---|---|---|---|---|---|---|---|---|---|
| all | 455 | 25 | 119 | 40 | 0.61 | 0.64 | +1.7 | -3.2 | -1.6 |
| away under 30 s | 244 | 6 | 62 | 3 | 0.09 | 0.14 | +0.3 | -0.5 | -2.3 |
| away 30 to 60 s | 74 | 43 | 14 | 9 | 0.78 | 0.45 | -5.1 | -9.0 | -0.1 |
| away 60 s or more | 137 | 98 | 43 | 28 | 1.46 | 1.63 | +7.7 | -4.6 | -1.0 |
| before 20:00 | 384 | 25 | 96 | 31 | 0.56 | 0.61 | +1.5 | -3.7 | -1.4 |
| from 20:00 | 71 | 24 | 23 | 9 | 0.9 | 0.75 | +2.3 | +0.0 | -2.3 |
| split member killed | 119 | 27 | 119 | 5 | 0.34 | 1.39 | +3.3 | +0.4 | +1.4 |
| no kill | 336 | 25 | 0 | 35 | 0.71 | 0.37 | +1.1 | -4.4 | -2.6 |

**Leverage: where the choice matters most** (share of the spread in win-chance change explained by the choice beyond the situation; range = best minus worst choice, in points)

- late game (164): choice explains 16.1% (situation 8.4%); range 38.6 points, best 4+ at the enemy Lord, worst 0 to 1 at the enemy Lord
- boost clock (1841): choice explains 1.9% (situation 2.1%); range 3.6 points, best running, fought, worst not running, fell back
- after wipe (1183): choice explains 1.2% (situation 3.7%); range 3.4 points, best pushed the pit, worst reset
- who defends (899): choice explains 1.1% (situation 2.0%); range 5.4 points, best 8 Monk alone, worst healer with a collapse
- offence or defence (1274): choice explains 0.9% (situation 1.2%); range 2.6 points, best offensive, worst defensive
- power play (4646): choice explains 0.8% (situation 1.8%); range 5.5 points, best pushed, to the spawn, worst held, fell back
- split in base (999): choice explains 0.5% (situation 2.6%); range 2.0 points, best defended without a collapse, worst collapsed
- enemy pickup (6098): choice explains 0.4% (situation 2.2%); range 13.7 points, best already running, to the spawn, worst held
- npcs or dp (296): choice explains 0.4% (situation 4.9%); range 1.6 points, best both, worst DP
- play for 28 or lord (4046): choice explains 0.3% (situation 1.9%); range 1.5 points, best push for the kill, worst play for 28
- runner choice (4218): choice explains 0.2% (situation 2.8%); range 2.2 points, best ranger, worst warrior
- eight v eight or flag (4374): choice explains 0.0% (situation 2.2%); range 0.5 points, best commit all 8, worst flag game
- split or stay (17779): choice explains 0.0% (situation 2.1%); range 0.5 points, best stayed, worst split

**Behaviour clusters: what teams actually did** (25 UNNAMED responses for Denning to name or reject; the full list with example moments is on the page "What teams actually do", knowledge/behaviour.md)

## Does the advice work? (the goal test)

For each decision kind, the advice is built from five groups of matches and read on the sixth (unseen): teams whose choice matched the advice against teams whose didn't, win-chance change over the decision's window adjusted for the situation, 90% range from resampling whole matches. The advice = the best choice among the 15 most similar decisions (at least 5 cases, 2+ points better than the usual play), else the usual play. "Specific" = the advice differed from the usual play.

**6 of 13 kinds pass** (effect positive, range excludes 0): after_wipe, late_game, npcs_or_dp, power_play, runner_choice, split_or_stay.

- after_wipe (1183 decisions, 482 matches): matched the advice 74% of the time; effect of matching +3.0 points (90% +1.4 to +4.5; clear); raw 0.7 matched against -2.6 not; specific advice in 6% of cases, raw effect there +4.1. Most recommended: pushed the pit (1084), took the flag (67), reset (32).
- boost_clock (1841 decisions, 471 matches): matched the advice 22% of the time; effect of matching +0.2 points (90% -0.5 to +0.9; not clear); raw 0.1 matched against -0.2 not; specific advice in 1% of cases, raw effect there -3.7. Most recommended: not running, fought (606), running, advanced (320), not running, fell back (294), running, fought (265), not running, advanced (177), running, fell back (91).
- eight_v_eight_or_flag (4374 decisions, 464 matches): matched the advice 73% of the time; effect of matching +0.9 points (90% -0.3 to +2.2; not clear); raw -0.1 matched against -1.5 not; specific advice in 11% of cases, raw effect there +1.7. Most recommended: flag game (3667), commit all 8 (707).
- enemy_pickup (6098 decisions, 482 matches): matched the advice 21% of the time; effect of matching -0.6 points (90% -1.8 to +0.5; not clear); raw -0.6 matched against -0.1 not; specific advice in 2% of cases, raw effect there +3.1. Most recommended: already running, advanced (1148), held, fell back (946), held, advanced (904), held, fought (789), already running, fell back (743), already running, fought (652).
- late_game (164 decisions, 82 matches): matched the advice 54% of the time; effect of matching +11.6 points (90% +3.0 to +19.7; clear); raw 5.4 matched against -6.7 not; specific advice in 32% of cases, raw effect there +13.1. Most recommended: 2 to 3 at the enemy Lord (91), 0 to 1 at the enemy Lord (47), 4+ at the enemy Lord (26).
- npcs_or_dp (296 decisions, 227 matches): matched the advice 65% of the time; effect of matching +1.9 points (90% +0.2 to +4.0; clear); raw 0.9 matched against -0.2 not; specific advice in 5% of cases. Most recommended: NPCs (223), DP (40), both (33).
- offence_or_defence (1274 decisions, 423 matches): matched the advice 46% of the time; effect of matching +0.3 points (90% -0.8 to +1.3; not clear); raw 1.1 matched against 0.8 not; specific advice in 21% of cases, raw effect there +0.6. Most recommended: offensive (667), defensive (445), mixed (162).
- play_for_28_or_lord (4046 decisions, 256 matches): matched the advice 71% of the time; effect of matching -1.0 points (90% -1.8 to -0.3; not clear); raw -0.1 matched against 0.8 not; specific advice in 14% of cases, raw effect there +0.2. Most recommended: play for 28 (3214), push for the kill (832).
- power_play (4646 decisions, 503 matches): matched the advice 27% of the time; effect of matching +0.8 points (90% +0.3 to +1.4; clear); raw 1.3 matched against 0.5 not; specific advice in 3% of cases, raw effect there +0.6. Most recommended: pushed, advanced (2317), pushed, fought (1178), held, fought (402), pushed, fell back (316), held, fell back (312), held, advanced (88).
- runner_choice (4218 decisions, 447 matches): matched the advice 34% of the time; effect of matching +0.9 points (90% +0.4 to +1.4; clear); raw 0.9 matched against 0.0 not; specific advice in 6% of cases, raw effect there +1.6. Most recommended: dervish (1255), monk (917), mesmer (781), ritualist (707), warrior (410), elementalist (98).
- split_in_base (999 decisions, 323 matches): matched the advice 49% of the time; effect of matching +0.9 points (90% -0.5 to +2.3; not clear); raw -0.6 matched against -1.5 not; specific advice in 25% of cases, raw effect there +1.5. Most recommended: defended without a collapse (543), collapsed (422), missed (34).
- split_or_stay (17779 decisions, 505 matches): matched the advice 89% of the time; effect of matching +0.6 points (90% +0.1 to +1.0; clear); raw -0.1 matched against -0.7 not; specific advice in 1% of cases, raw effect there +2.2. Most recommended: stayed (17610), split (169).
- who_defends (899 decisions, 306 matches): matched the advice 19% of the time; effect of matching +0.1 points (90% -2.2 to +1.8; not clear); raw -0.7 matched against -1.0 not; specific advice in 1% of cases. Most recommended: midline alone (292), frontline with a collapse (182), frontline alone (128), midline with a collapse (99), 8 Monk alone (61), backline alone (46).

## 8. What results and causes are worth

Win points for the team it happened to, from 506 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. Both against matched moments without the event (same minute and win chance). A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 1406 | +4.5 | +2.5 to +6.7 | +1.8 | yes |
| capture | 4442 | +2.1 | +1.9 to +2.4 | +2.6 | yes |
| capture: held longer | 3847 | +2.8 | +2.0 to +3.5 | +2.8 | yes |
| capture: overcapped within 10 s (Bounty, F36) | 595 | -2.0 | -6.3 to +2.1 | +0.9 | no |
| death (any) | 10206 | -8.7 | -9.5 to -7.9 | -4.7 | yes |
| death: against a spike build | 2923 | -8.3 | -10.8 to -5.7 | -4.7 | yes |
| death: against other builds | 7283 | -8.9 | -10.0 to -7.9 | -4.7 | yes |
| death: back within 20 s | 1772 | -7.8 | -9.5 to -6.2 | -2.5 | yes |
| death: down 20 to 60 s | 3650 | -7.6 | -8.7 to -6.3 | -4.1 | yes |
| death: down 60 s or more | 4784 | -9.9 | -11.0 to -8.7 | -6.0 | yes |
| death: healer | 3443 | -8.3 | -9.4 to -7.2 | -4.8 | yes |
| death: healer in own base or pit, back within 15 s (possibly deliberate; energy not tracked) | 239 | -5.2 | -7.5 to -3.1 | -1.7 | yes |
| death: healer, other | 3204 | -8.5 | -9.6 to -7.4 | -5.1 | yes |
| death: not a healer | 6763 | -8.9 | -9.9 to -8.0 | -4.7 | yes |
| footman lost (base NPC) | 1430 | +0.5 | -0.7 to +1.6 | +3.8 | no |
| pit NPC lost (any): taken by a spike build | 881 | -5.2 | -7.9 to -2.5 | -2.1 | yes |
| pit NPC lost (any): taken by other builds | 3199 | -5.1 | -6.2 to -4.0 | -2.3 | yes |
| pit NPC lost: archer | 2306 | -4.2 | -5.2 to -3.4 | -0.7 | yes |
| pit NPC lost: bodyguard | 548 | -5.4 | -6.5 to -4.4 | -2.5 | yes |
| pit NPC lost: knight | 1226 | -6.6 | -7.7 to -5.7 | -5.0 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value. Context (strength, build skill counts, flag lead, morale, the clock) is left out: it describes the situation, it is not a cause to fix.

*deaths* (per 10 s in that state; result worth -8.7 points, base rate 1.6%):

- enemies within 1,500 7.5 to 8: result chance +3.2 points, worth -0.28 win points
- allies within 1,500 0 to 0.5: result chance +2.1 points, worth -0.18 win points
- current health % 1 to 47.5: result chance +10.3 points, worth -0.89 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.6 points, worth -0.23 win points
- a prot (Guardian, Spirit Bond, Life Sheath, Protective Spirit...) on the player now 0.5 to 1: result chance -0.4 points, worth +0.04 win points
- own healers alive within cast range (other than the player) 0 to 0.5: result chance +0.5 points, worth -0.04 win points

*kill conversion* (per burst, for the attacking team; result worth +8.7 points, base rate 29.6%):

- damage in the 2 s burst 509.5 to 1069: result chance +30.1 points, worth +2.62 win points
- target's health ceiling 0.4 to 0.56: result chance +46.4 points, worth +4.04 win points
- target's healers in range 0 to 0.5: result chance +35.5 points, worth +3.09 win points
- target health % when the burst started 0 to 36.5: result chance +30.8 points, worth +2.68 win points
- a prot on the target 0.5 to 1: result chance -7.4 points, worth -0.65 win points

*pit npc loss* (per case, for the defending team; result worth -5.1 points, base rate 20.8%):

- own players in the pit 0 to 0.5: result chance +42.1 points, worth -2.14 win points
- own players alive outside the pit 0 to 0.5: result chance +12.5 points, worth -0.63 win points
- of which healers 0 to 0.5: result chance +16.1 points, worth -0.82 win points

## The TQs

Not run this chunk (batch 17; the TQs run every other chunk, or with GVG_TQS=yes).

## 9. Detailed learnings snapshot

Not run this chunk (every other chunk, or with GVG_TQS=yes).

## 10. For Denning

- Links of yours the data says to reject (rule: override yes, or not yet): P.26 -> R.2.
- Waiting list: 4 items (data/model/causal_map.json, waiting); nothing moves in until the next bundled engine change.
- Behaviour clusters no named choice covers: 25 to name or reject (knowledge/behaviour.md).

