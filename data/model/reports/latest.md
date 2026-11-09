# Learning report, batch 15

Trained on 356 matches (45 new in this batch). Variables in use: 33; build variables from 60 matches, interactions from 40.

## 0. Data integrity

- Lengths repaired: 11 (1f65fd3b 150 s -> 1027 s) (bbef1904 617 s -> 599 s) (36a65ac6 1319 s -> 1294 s) (ba85aafc 811 s -> 793 s) (f9d6932f 235 s -> 218 s) (82fa12be 488 s -> 467 s) (cf2968cd 178 s -> 363 s) (713d9cd0 376 s -> 353 s) (366b75bc 667 s -> 650 s) (90ad5f3b 167 s -> 651 s) (dc8e5146 175 s -> 321 s) 
- Matches with a team's Lord damage not observed (left blank, not zero): 28
- Pit NPCs added from the standard roster (never seen in the replay): 1229 in 307 matches
- Left out of training: 0

## 1. The honest test

**Beats strength alone (clear: the range excludes 0).** Held-out accuracy (matches held out whole), log loss in brackets (lower is better):

- strength only: all 77% (0.472), 0-5 min 82% (0.389), 5-10 min 79% (0.451), 10-15 min 74% (0.535), 15-end min 70% (0.582), matches lasting 15 min+ 72% (0.562), matches even on strength (gap under 200) 59% (0.65)
- glass box: all 84% (0.358), 0-5 min 85% (0.339), 5-10 min 85% (0.349), 10-15 min 82% (0.395), 15-end min 85% (0.37), matches lasting 15 min+ 81% (0.427), matches even on strength (gap under 200) 76% (0.525)
- glass box without corrections: all 83% (0.387), 0-5 min 83% (0.371), 5-10 min 83% (0.385), 10-15 min 82% (0.437), 15-end min 85% (0.378), matches lasting 15 min+ 80% (0.441), matches even on strength (gap under 200) 77% (0.55)
- black box: all 79% (0.626), 0-5 min 82% (0.552), 5-10 min 80% (0.6), 10-15 min 76% (0.711), 15-end min 77% (0.708), matches lasting 15 min+ 74% (0.785), matches even on strength (gap under 200) 64% (0.959)
- Gain over strength alone (log loss, resampling whole matches): +0.114 (90% range +0.064 to +0.161).
- Change since batch 14: glass box log loss 0.367 -> 0.358; strength only 0.452 -> 0.472.
- Cap test on spike_killable_diff (held-out log loss, 356 matches): none 0.3699, 10 points 0.3625, 15 points 0.3621, 20 points 0.3621, 25 points 0.3626; chosen: cap at 15 points.
- Pair test (morale_diff with map_flag_run, map_pit_to_stand, map_bases_apart; morale_total with map_flag_run, map_pit_to_stand, map_bases_apart; held-out log loss, 356 matches): allowed 0.3699, blocked 0.3628; chosen: blocked (it predicts unseen matches better).
- Calibration by minute (held-out predictions on 356 matches; pooled cells joined by straight lines, blended by minute; every win chance below and in values, usual play and the TQs goes through it). Predicted -> how often those teams won -> calibrated:
  - 0 to 6 min: 0.6% -> won 1.4% (207 matches) -> 1.4%; 3.3% -> won 4.0% (200 matches) -> 4.0%; 42.5% -> won 41.1% (136 matches) -> 41.2%; 57.4% -> won 58.4% (137 matches) -> 58.3%; 92.6% -> won 92.2% (207 matches) -> 92.2%; 99.4% -> won 98.6% (207 matches) -> 98.6%
  - 6 to 12 min: 0.5% -> won 1.7% (195 matches) -> 1.6%; 3.3% -> won 5.7% (137 matches) -> 5.7%; 42.3% -> won 44.6% (72 matches) -> 44.4%; 57.6% -> won 51.4% (68 matches) -> 51.9%; 92.7% -> won 88.4% (134 matches) -> 88.6%; 99.5% -> won 98.3% (196 matches) -> 98.3%
  - 12 to 18 min: 0.6% -> won 4.5% (113 matches) -> 3.4%; 3.2% -> won 2.1% (79 matches) -> 5.2%; 42.7% -> won 43.5% (45 matches) -> 43.4%; 56.9% -> won 54.3% (46 matches) -> 54.5%; 92.8% -> won 91.0% (75 matches) -> 91.2%; 99.4% -> won 95.9% (117 matches) -> 96.2%
  - 18 to end min: 0.5% -> won 3.7% (94 matches) -> 3.6%; 3.4% -> won 12.0% (66 matches) -> 11.4%; 42.2% -> won 44.6% (32 matches) -> 44.3%; 57.5% -> won 56.0% (33 matches) -> 56.2%; 92.7% -> won 80.7% (54 matches) -> 81.7%; 99.5% -> won 96.6% (94 matches) -> 96.8%

## 2. What it leans on

- **morale_diff** 0.81 (was 0.653): own minus enemy morale summed over players (boosts +, death penalty -)
- **knights_diff** 0.414 (was 0.486): own minus enemy pit knights alive
- **footmen_lost_diff** 0.339 (new): own minus enemy footmen lost so far (base NPCs, not pit NPCs). Proposed 2026-11-06 from OG comms ([ohno v NwAy]: 'this way we don't lose footmen'); moved in as footmen alive after chunk 4, then counted as losses after chunk 5 (Denning): a footman only enters the replay once something touches it, so 'alive' marked a base that was visited and read backwards (-42 points at +4); deaths are always recorded
- **alive_diff** 0.23 (was 0.164): own minus enemy players alive
- **stand** 0.219 (was 0.211): who holds the flag stand: 1 own, 0 nobody, -1 enemy
- **knights_diff & map_flag_run** 0.198 (was 0.114): own minus enemy pit knights alive TOGETHER WITH the map's flag run Y: distance from the flag spawn to the stand (average of both sides)
- **flag_lead** 0.176 (was 0.154): seconds up (+) or down (-) on flags: enemy's response minus own on the next capture exchange
- **lord_dps_own** 0.17 (was 0.168): own build's measured Lord damage per second if all its non-healers were at the Lord
- **lord_dps_enemy** 0.17 (was 0.168): enemy build's measured Lord damage per second
- **fight_state** 0.162 (was 0.163): who is winning the fight now: enemy minus own expected deaths in the next 10 s, from a deaths model that never saw the match (fightstate.py)
- **knights_diff & map_bases_apart** 0.133 (new): own minus enemy pit knights alive TOGETHER WITH the map's distance between the two bases
- **spike_killable_diff** 0.12 (was 0.227): enemy minus own players within one spike of the other side (DP stacking; 0 unless a spike build is involved)

## 3. The curves in words

Points = win-chance points added to an otherwise even game at each range of the variable.

- **morale_diff** rises from -43.3 to +39.1 points (-485.0..-210.5: -43.3; -154.5..-110.5: -27.1; -79.5..-45.5: -14.7; -15.5..-0.5: -1.7; 0.5..16.5: +3.7; 50.5..90.5: +18.0; 135.5..197.5: +30.2)
- **knights_diff** rises from -26.2 to +26.4 points (-2.0..-1.5: -26.2; -1.5..-0.5: -16.4; -0.5..0.5: -0.2; 0.5..1.5: +17.2; 1.5..2.0: +26.4)
- **footmen_lost_diff** rises from -37.1 to +37.3 points (-4.0..-3.5: -37.1; -3.5..-2.5: -36.2; -2.5..-1.5: -16.0; -1.5..-0.5: -15.0; -0.5..0.5: +0.0; 0.5..1.5: +15.1; 1.5..2.5: +15.9; 2.5..3.5: +36.0; 3.5..4.0: +37.3)
- **alive_diff** rises from -44.4 to +30.5 points (-8.0..-6.5: -44.4; -4.5..-3.5: -16.6; -2.5..-1.5: -12.0; -0.5..0.5: -0.2; 1.5..2.5: +14.2; 3.5..4.5: +19.1)
- **stand** rises from -5.9 to +6.0 points (-1.0..-0.5: -5.9; -0.5..0.5: -0.5; 0.5..1.0: +6.0)
- **knights_diff & map_flag_run** (interaction): see wp_model.md
- **flag_lead** rises from -11.8 to +9.7 points (-140.0..-62.5: -11.8; -54.5..-40.5: -5.6; -30.5..-18.5: -2.3; -8.5..-0.5: -0.3; 6.5..16.5: +1.7; 28.5..39.5: +3.0; 54.5..63.5: +8.1)
- **lord_dps_own** is flat from +5.0 to +5.0 points (56.3..77.6: +5.0; 82.65..84.05: +5.0; 86.55..89.75: -0.3; 94.7..96.2: -5.0; 96.85..96.95: -5.0; 100.55..106.35: -5.0; 112.05..126.45: +5.0)
- **lord_dps_enemy** is flat from -5.0 to -5.0 points (56.3..77.6: -5.0; 82.65..84.05: -5.0; 86.55..89.75: -0.1; 94.7..96.2: +5.0; 96.85..96.95: +5.0; 100.55..106.35: +5.0; 112.05..126.45: -5.0)
- **fight_state** rises from -13.7 to +13.7 points (-3.1..-0.37: -13.7; -0.16..-0.08: -4.1; -0.04..-0.02: -1.6; -0.01..-0.0: -0.7; 0.01..0.02: +1.1; 0.04..0.08: +2.6; 0.15..0.36: +5.3)

## 4. Discovery

**Interaction candidates** (a screen: pairs whose combination seems to matter beyond each alone; untested until held-out matches confirm them; switched on in the model from 40 matches):

- morale_diff with spike_killable_diff (screen 0.152)
- stand with morale_diff (screen 0.142)
- boost_clock with morale_diff (screen 0.142)
- alive_diff with morale_diff (screen 0.141)
- minute with morale_diff (screen 0.140)
- morale_diff with morale_total (screen 0.138)
- flag_lead with morale_diff (screen 0.138)
- down_diff_s with morale_diff (screen 0.137)

**Candidate variables** (proposed variables, tested on unseen matches; log loss, lower is better):

- turtle_diff: 0.357 without, 0.357 with: does not improve yet. own minus enemy share of live players at home (own base or pit). Proposed 2026-11-06 from OG comms ([ohno v One], [ohno v Crew]: 'they are turtling, we have to make a play'); comms_vars.py: teams that turtled 60 s won 3 of 13 times
- no_healer_groups_diff: 0.357 without, 0.354 with: does not improve yet. own minus enemy groups of 2+ with no healer. Proposed 2026-11-06 from OG comms ([ohno v One]: keep a prot and a monk on one side, the Rit and a monk on the other); comms_vars.py: such groups lose players twice as often
- solo_healers_diff: 0.357 without, 0.355 with: does not improve yet. own minus enemy healers with no other own healer within casting range. Proposed 2026-11-06 from OG comms ('solo monk, go on the monk'); Denning: a monk alone has no other monk to support it

**Surprises** (moments where the held-out model was most confident about the team that went on to lose; each points to something the variables don't capture yet):

- One v DUM (db72bb2e) at 4:15: a model that never saw this match gave DUM 1.4%, and DUM won. Why it thought so: team strength -48.9, morale_diff -12.9, alive_diff -11.0, down_diff_s -8.9, stand -6.3
- hold v Fun (7cb3ef17) at 7:00: a model that never saw this match gave hold 2.5%, and hold won. Why it thought so: morale_diff -33.0, team strength +30.3, knights_diff -26.3, knights_diff & map_flag_run -14.2, lord_exposed_diff & map_flag_run -12.3
- hdm v HC (28447c4a) at 10:30: a model that never saw this match gave HC 2.3%, and HC won. Why it thought so: knights_diff -29.0, lord_health_diff -15.2, archers_diff +10.8, bodyguard_diff -10.7, lord_exposed_diff -9.0
- Dz v TFS (0881f8b3) at 9:00: a model that never saw this match gave TFS 8.1%, and TFS won. Why it thought so: team strength -46.5, spike_killable_diff +13.5, spike_build_enemy -7.6, spike_build_own +7.5, stand -5.7
- げえええ v chic (f42e3d5b) at 19:15: a model that never saw this match gave げえええ 6.3%, and げえええ won. Why it thought so: team strength -39.7, knights_diff -20.5, alive_diff -15.7, spike_killable_diff +10.9, knights_diff & map_flag_run -10.0
- DMG v Free (d9e8531e) at 12:15: a model that never saw this match gave Free 2.6%, and Free won. Why it thought so: team strength -46.3, knights_diff & map_flag_run -30.7, knights_diff -27.2, morale_diff +20.9, footmen_lost_diff +19.0

## 5. Denning's rulings seen through the model

Win chance from a model that never saw the match, 20 s before and 60 s after each ruled moment. Contributions are points for an otherwise even game (the curves' scale).

- hdm v HC (28447c4a) 5:01 (split answered), HC: 38.5% 20 s before -> 40.2% 60 s after (+1.7). After: knights_diff -29.0, morale_diff +14.6, stand +6.8, flag_lead +6.2
- hdm v HC (28447c4a) 5:01 (split answered), hdm: 61.6% 20 s before -> 59.0% 60 s after (-2.6). After: knights_diff +29.5, morale_diff -13.3, flag_lead -7.2, stand -6.8
- hdm v HC (28447c4a) 1:02 (split detection), HC: 42.6% 20 s before -> 33.3% 60 s after (-9.3). After: flag_lead -7.2, stand -6.8, team strength -5.4, lord_dps_own -5.0
- hdm v HC (28447c4a) 1:02 (split detection), hdm: 55.2% 20 s before -> 64.4% 60 s after (+9.2). After: stand +6.8, flag_lead +6.2, team strength +5.4, lord_dps_own -5.0
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), HC: 8.1% 20 s before -> 9.8% 60 s after (+1.7). After: knights_diff -29.0, morale_diff +14.6, archers_diff +10.8, bodyguard_diff -10.7
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), hdm: 93.1% 20 s before -> 91.5% 60 s after (-1.6). After: knights_diff +29.5, morale_diff -13.3, archers_diff -10.8, lord_damage_diff & lord_dps_own +10.3
- hdm v HC (bbef1904) 8:10 (death), HC: 49.1% 20 s before -> 11.7% 60 s after (-37.4). After: alive_diff -15.8, morale_diff -15.8, footmen_lost_diff -13.4, down_diff_s -7.9
- hdm v HC (bbef1904) 8:10 (death), hdm: 46.8% 20 s before -> 88.0% 60 s after (+41.2). After: morale_diff +17.8, alive_diff +15.8, footmen_lost_diff +13.8, down_diff_s +8.6
- Men v HC (faec428a) 9:31 (death), HC: 26.8% 20 s before -> 13.9% 60 s after (-12.9). After: footmen_lost_diff -15.8, knights_diff -15.0, map_bases_apart & footmen_lost_diff -7.1, stand -6.8
- Men v HC (faec428a) 9:31 (death), Men: 72.4% 20 s before -> 83.5% 60 s after (+11.1). After: footmen_lost_diff +15.7, knights_diff +15.4, stand +6.8, map_bases_apart & footmen_lost_diff +6.3

## 6. Why: the node models

Each explains one result from what happened before it (time order enforced), tested on matches it never saw. AUC = how often a moment that led to the result scores above one that didn't (0.5 = guessing, 1 = perfect).

**deaths** (356 matches, 741724 moments, 22517 results): adds to the simple baseline (AUC 0.927 against 0.79 for health_pct and damage_taken_3s alone).
- **enemies_near** (enemies within 1,500) rises from -23.9 to +25.9 points (0.0..0.5: -23.9; 0.5..1.5: -13.7; 1.5..2.5: -2.3; 2.5..3.5: +4.1; 3.5..4.5: +7.2; 4.5..5.5: +10.3; 5.5..6.5: +12.6; 6.5..7.5: +17.6; 7.5..8.0: +25.9)
- **strength_gap** (own minus enemy team strength) falls from +14.6 to -17.3 points (-1183.0..-596.0: +14.6; -472.0..-372.0: +9.1; -274.0..-170.5: +8.4; -78.5..0.0: +2.4; 75.5..164.0: -2.3; 253.5..368.0: -4.4; 455.5..590.0: -14.1)
- **allies_near** (allies within 1,500) falls from +21.6 to -8.6 points (0.0..0.5: +21.6; 0.5..1.5: +10.1; 1.5..2.5: +5.3; 2.5..3.5: +0.2; 3.5..4.5: -1.7; 4.5..5.5: -5.0; 5.5..6.5: -6.3; 6.5..7.0: -8.6)
- **local_diff** (allies minus enemies within 2,000) falls from +23.9 to -15.8 points (-8.0..-3.5: +23.9; -2.5..-1.5: +13.0; -0.5..0.5: -5.9; 1.5..2.5: -6.5; 3.5..4.5: +6.7; 5.5..7.0: -15.8)
- **health_pct** (current health %) falls from +39.5 to -5.1 points (1.0..48.5: +39.5; 60.5..68.5: +17.1; 74.5..78.5: +7.1; 82.5..85.5: +2.6; 88.5..91.5: -0.0; 93.5..95.5: -2.0; 97.5..99.5: -4.1)
- **prot_up** (a prot (Guardian, Spirit Bond, Life Sheath, Protective Spirit...) on the player now) falls from +2.1 to -8.4 points (0.0..0.5: +2.1; 0.5..1.0: -8.4)
- **dist_own_pit** (distance from its own pit) rises from -2.0 to +10.2 points (6.0..1373.5: -2.0; 2443.5..4184.5: -3.2; 5352.5..6247.5: -3.9; 6905.5..7414.5: -1.7; 7995.5..8626.5: -2.1; 9456.5..10494.5: +1.2; 11703.5..13165.5: +6.5)
- **own_morale** (the player's own morale: negative = death penalty, positive = boost (OG comms: fight the player with 30 DP)) falls from +17.2 to -4.4 points (-60.0..-33.5: +17.2; -28.5..-15.5: +11.0; -14.5..-11.5: +7.1; -5.5..-4.5: +3.1; -0.5..5.5: -0.8)
- **healers_in_range** (own healers alive within cast range (other than the player)) falls from +5.8 to -11.0 points (0.0..0.5: +5.8; 0.5..1.5: +0.1; 1.5..2.5: -4.5; 2.5..3.5: +0.6; 3.5..4.0: -11.0)
- **health_ceiling** (maximum health after death penalty, as a share of normal) falls from +16.9 to -4.5 points (0.4..0.67: +16.9; 0.71..0.84: +11.3; 0.85..0.89: +6.4; 0.94..0.95: +2.5; 0.99..1.06: -0.6)

**kill conversion** (348 matches, 6603 moments, 1922 results): adds to the simple baseline (AUC 0.808 against 0.682 for burst_damage and target_health_pct alone).
- **burst_damage** (damage in the 2 s burst) rises from -12.0 to +27.3 points (250.0..257.5: -12.0; 266.5..277.5: -12.6; 287.5..299.5: -9.9; 312.5..326.5: -8.3; 343.5..362.5: +2.6; 385.5..411.5: +9.6; 449.5..505.5: +20.8)
- **target_healers_in_range** (target's healers in range) falls from +31.6 to -5.2 points (0.0..0.5: +31.6; 0.5..1.5: +8.6; 1.5..2.5: -6.3; 2.5..3.5: -8.5; 3.5..4.0: -5.2)
- **target_ceiling** (target's health ceiling) falls from +38.8 to -13.7 points (0.4..0.56: +38.8; 0.69..0.7: +24.9; 0.74..0.84: +20.2; 0.85..0.86: +11.9; 0.88..0.94: +5.5; 0.99..1.0: -5.3; 1.1..1.1: -13.7)
- **target_health_pct** (target health % when the burst started) falls from +29.8 to -11.4 points (0.0..36.5: +29.8; 47.5..55.5: +12.8; 61.5..67.5: +6.7; 72.5..76.5: +0.3; 80.5..84.5: -2.2; 87.5..91.5: -5.1; 95.5..99.5: -9.6)
- **target_prot_up** (a prot on the target) falls from +5.6 to -10.3 points (0.0..0.5: +5.6; 0.5..1.0: -10.3)
- **strength_gap** (attacking minus target team strength) rises from -9.8 to +13.8 points (-1183.0..-559.5: -9.8; -381.5..-303.5: -12.5; -216.5..-91.5: -2.9; -5.5..66.5: -0.6; 141.5..218.0: +1.3; 289.5..378.0: +9.0; 523.5..678.0: +13.6)
- **enemy_prots** (target team's prot skills) falls from +10.5 to -5.0 points (1.0..5.5: +10.5; 7.5..8.5: +7.3; 9.5..10.5: +2.6; 11.5..12.5: -1.1; 13.5..14.5: -2.8; 15.5..16.5: -3.6; 17.5..20.0: -5.0)
- **attackers** (attackers in the burst) falls from -1.3 to -13.6 points (3.0..3.5: -1.3; 3.5..4.5: +1.7; 4.5..5.5: +3.7; 5.5..6.5: -10.7; 6.5..7.0: -13.6)
- **target_degen_pips** (degeneration on the target, pips (pressure.py)) rises from -1.3 to +7.7 points (0.0..1.2: -1.3; 1.2..2.95: -0.3; 2.95..3.1: +4.7; 3.1..3.9: +5.1; 3.9..4.1: +5.5; 4.1..6.95: +5.6; 6.95..7.1: +0.6; 7.1..9.95: +6.2; 9.95..10.0: +7.7)

**flag answer** (seconds an answer to an enemy capture was slower than possible; 302 matches, 2882 rows): adds to the simple baseline (typical error 15.6s against 27.8s for the median; explains 73% of the spread).
- **parked_s** (seconds the flag lay parked (dropped 5 s or more: not running yet)): 0.0..2.5: -5.1 s; 7.5..12.5: +7.1 s; 16.5..22.5: +20.6 s; 29.5..38.5: +36.8 s; 49.0..68.5: +50.6 s; 90.5..114.0: +59.7 s; 168.0..281.5: +68.1 s
- **own_deaths_during** (own deaths during the answer): 0.0..0.5: -3.3 s; 1.5..2.5: +14.6 s; 3.5..4.5: +29.3 s; 5.5..6.5: +47.4 s; 7.5..9.5: +50.3 s
- **enemies_in_the_way** (enemy presence along the runner's trip back to the spawn): 0.0..0.5: -5.2 s; 4.5..10.5: -4.0 s; 16.5..22.5: -2.5 s; 29.5..39.5: -0.1 s; 50.5..62.5: +1.6 s; 82.5..108.5: +6.2 s; 146.5..220.5: +14.8 s
- **enemy_deaths_during** (enemy deaths during the answer): 0.0..0.5: -3.2 s; 0.5..1.5: +5.4 s; 1.5..2.5: +15.0 s; 2.5..3.5: +21.0 s; 3.5..4.5: +25.4 s; 4.5..5.5: +25.6 s; 5.5..12.0: +41.6 s
- **carrier_damage_taken** (damage the carrier took while carrying): 0.0..0.5: -4.0 s; 30.5..59.5: -2.8 s; 91.5..123.5: -1.5 s; 181.0..238.5: -0.3 s; 286.0..357.5: +1.6 s; 454.0..590.5: +5.6 s; 795.5..1170.5: +12.7 s
- **possible_s** (fastest possible answer (s) from the flag model at the enemy's capture): 0.0..3.5: -8.4 s; 8.5..13.5: -4.6 s; 18.5..22.5: -0.9 s; 27.5..30.5: +1.3 s; 33.5..36.5: +3.6 s; 39.5..43.5: +4.9 s; 47.5..53.5: +5.1 s
- **flag_lead_at_enemy_cap** (own flag lead when the enemy captured): -80.0..-58.5: -0.5 s; -49.5..-40.5: +2.6 s; -33.5..-27.5: +3.3 s; -21.5..-16.5: +2.0 s; -10.5..-3.5: +0.2 s; 2.5..12.5: -2.5 s; 24.5..39.5: -4.0 s
- **runner_to_spawn** (runner's distance to its flag spawn when the enemy captured): 8.0..758.0: -5.3 s; 1492.0..2108.0: -2.8 s; 2923.5..3680.5: -0.8 s; 4268.0..4566.5: +0.7 s; 4943.5..5554.0: +1.1 s; 6174.5..6719.5: +2.2 s; 7339.0..8376.5: +2.3 s
- **morale_diff** (own minus enemy morale): -303.0..-110.5: +6.2 s; -74.5..-49.5: +4.8 s; -30.5..-15.5: +2.4 s; -2.5..3.5: -0.3 s; 15.5..30.5: -1.2 s; 49.5..74.0: -2.0 s; 95.5..142.0: -5.5 s
- **quick_handoffs** (quick hand-offs (a teammate picked it up within 5 s)): 0.0..0.5: -1.2 s; 0.5..1.5: +4.0 s; 1.5..2.5: +6.8 s; 2.5..3.0: +21.4 s

**npc loss** (354 matches, 35789 moments, 7391 results): adds to the simple baseline (AUC 0.855 against 0.757 for attackers and defenders alone).
- **defenders** (own players in the pit) falls from +33.7 to -32.9 points (0.0..0.5: +33.7; 0.5..1.5: +19.1; 1.5..2.5: +12.6; 2.5..3.5: +1.4; 3.5..4.5: -9.4; 4.5..5.5: -16.9; 5.5..6.5: -18.6; 6.5..7.5: -29.6; 7.5..8.0: -32.9)
- **npc_damage_5s** (damage on the pit NPCs in the last 5 s) rises from -16.0 to +33.3 points (0.0..0.5: -16.0; 22.5..36.5: +3.6; 50.5..68.5: +7.0; 86.5..108.5: +16.4; 133.5..160.5: +21.7; 194.5..236.5: +26.3; 294.5..385.5: +31.1)
- **defenders_elsewhere** (own players alive outside the pit) falls from +20.6 to -11.5 points (0.0..0.5: +20.6; 0.5..1.5: +14.6; 1.5..2.5: +11.7; 2.5..3.5: -0.2; 3.5..4.5: -8.5; 4.5..5.5: -10.6; 5.5..6.5: -15.0; 6.5..7.5: -14.6; 7.5..8.0: -11.5)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -23.7 to +16.3 points (2.7..18.1: -23.7; 24.65..28.65: -9.2; 36.45..45.65: -10.6; 53.65..62.45: +1.2; 67.55..77.05: +9.4; 83.45..92.25: +11.6; 101.65..106.65: +15.4)
- **defender_healers** (of which healers) falls from +21.2 to -6.5 points (0.0..0.5: +21.2; 0.5..1.5: -0.9; 1.5..2.5: -6.6; 2.5..3.5: -7.1; 3.5..4.0: -6.5)
- **strength_gap** (attacking minus defending team strength) rises from -7.7 to +7.6 points (-1108.0..-504.5: -7.7; -329.0..-211.5: -9.6; -79.5..7.5: +1.7; 92.5..181.0: +1.2; 267.5..324.0: +1.7; 393.5..479.5: +2.8; 568.5..692.5: +4.3)
- **attackers** (enemy players in the pit) rises from -5.9 to +5.9 points (1.0..1.5: -5.9; 1.5..2.5: -2.7; 2.5..3.5: -1.1; 3.5..4.5: +2.5; 4.5..5.5: +4.3; 5.5..6.5: +3.3; 6.5..7.5: +4.4; 7.5..8.0: +5.9)
- **npc_healing_10s** (healing on own pit NPCs and Lord in the last 10 s) falls from +2.7 to -13.1 points (0.0..1.5: +2.7; 41.5..49.5: +1.5; 85.5..125.5: +0.4; 155.5..188.5: -3.3; 224.5..269.5: -5.8; 319.5..384.5: -6.7; 472.5..623.5: -10.7)
- **attackers_share** (share of the attacking team's live players in the pit (OG comms: merge before pushing the pit)) rises from -4.1 to +5.4 points (0.12..0.13: -4.1; 0.16..0.23: -3.0; 0.27..0.35: -2.3; 0.42..0.53: -0.6; 0.61..0.65: +1.5; 0.73..0.84: +3.3; 0.94..1.0: +5.4)

**lord damage** (Lord damage dealt in the next 10 s while players are in the enemy pit; 339 matches, 39929 rows): adds to the simple baseline (typical error 77.8 against 102.5 for the median; explains 39% of the spread).
  ('chance of any' curves: points of the chance of any Lord damage in the window; 'amount' curves: % more Lord damage when there is some.)
- **defenders (chance of any)** (own players in the pit): 0.0..0.5: +35.7 points; 0.5..1.5: +27.9 points; 1.5..2.5: +19.1 points; 2.5..3.5: -0.9 points; 3.5..4.5: -10.8 points; 4.5..5.5: -26.6 points; 5.5..6.5: -31.1 points; 6.5..7.5: -36.6 points; 7.5..8.0: -41.3 points
- **bodyguard (chance of any)** (own Bodyguard alive): 0.0..0.5: +25.3 points; 0.5..1.0: -10.5 points
- **minute (chance of any)** (match minute): 0.5..2.75: -22.2 points; 3.85..5.05: -10.7 points; 6.25..7.55: -7.6 points; 9.15..10.75: -4.5 points; 12.65..14.65: -1.8 points; 16.85..19.55: +1.1 points; 22.25..25.05: +16.3 points
- **npc_healing_10s (chance of any)** (healing on own pit NPCs and Lord in the last 10 s): 0.0..1.5: -8.4 points; 42.5..68.5: +9.4 points; 103.5..141.5: +11.4 points; 158.5..200.5: +12.9 points; 240.5..286.5: +14.3 points; 333.5..397.5: +15.8 points; 487.5..641.5: +17.3 points
- **attackers_lord_dps (chance of any)** (attackers' measured damage per second against a Lord (benchmarks)): 2.7..22.6: -26.0 points; 24.8..28.85: -12.2 points; 37.25..48.15: +4.1 points; 53.95..63.45: -2.5 points; 68.95..77.15: +4.7 points; 84.45..92.65: +12.4 points; 102.45..109.8: +14.4 points
- **knights (chance of any)** (own knights alive): 0.0..0.5: +9.8 points; 0.5..1.5: -7.5 points; 1.5..2.0: -9.5 points
- **attackers_share (chance of any)** (share of the attacking team's live players in the pit (OG comms: merge before pushing the pit)): 0.12..0.13: -8.8 points; 0.16..0.23: -7.9 points; 0.27..0.35: -5.8 points; 0.42..0.53: -3.6 points; 0.61..0.65: +5.9 points; 0.73..0.84: +10.5 points; 0.94..1.0: +11.9 points
- **attackers (chance of any)** (enemy players in the pit): 1.0..1.5: -7.9 points; 1.5..2.5: -5.2 points; 2.5..3.5: -3.7 points; 3.5..4.5: +1.4 points; 4.5..5.5: +5.1 points; 5.5..6.5: +6.5 points; 6.5..7.5: +7.0 points; 7.5..8.0: +12.4 points
- **full_pit_targets (chance of any)** (pit NPCs alive (targets the defending monks must watch, P9)): 0.0..0.5: +10.4 points; 0.5..1.5: +8.2 points; 1.5..2.5: +3.5 points; 2.5..3.5: -1.1 points; 3.5..4.5: -4.1 points; 4.5..5.5: -6.8 points; 5.5..6.0: -9.0 points
- **defenders_elsewhere (chance of any)** (own players alive outside the pit): 0.0..0.5: +2.9 points; 0.5..1.5: +3.5 points; 1.5..2.5: +4.1 points; 2.5..3.5: +4.4 points; 3.5..4.5: +4.7 points; 4.5..5.5: -0.4 points; 5.5..6.5: -0.3 points; 6.5..7.5: -11.4 points; 7.5..8.0: -11.8 points

**lord kill** (339 matches, 39891 moments, 2888 results): adds to the simple baseline (AUC 0.977 against 0.937 for attackers and defenders alone).
- **defenders** (own players in the pit) falls from +41.7 to -48.1 points (0.0..0.5: +41.7; 0.5..1.5: +34.8; 1.5..2.5: +22.9; 2.5..3.5: +3.2; 3.5..4.5: -19.1; 4.5..5.5: -30.1; 5.5..6.5: -35.7; 6.5..7.5: -37.5; 7.5..8.0: -48.1)
- **minute** (match minute) rises from -49.4 to +15.0 points (0.5..2.75: -49.4; 3.85..5.05: -12.3; 6.25..7.55: +11.9; 9.15..10.75: +18.7; 12.65..14.65: +22.1; 16.85..19.55: +22.2; 22.25..25.05: +21.2)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -26.2 to +33.2 points (2.7..22.6: -26.2; 24.8..28.85: -38.0; 37.25..48.15: -8.3; 53.95..63.45: +0.1; 68.95..77.15: +12.6; 84.45..92.65: +30.6; 102.45..109.8: +33.8)
- **defenders_elsewhere** (own players alive outside the pit) falls from +27.6 to -25.6 points (0.0..0.5: +27.6; 0.5..1.5: +21.2; 1.5..2.5: +17.7; 2.5..3.5: +15.5; 3.5..4.5: -0.8; 4.5..5.5: -16.3; 5.5..6.5: -24.8; 6.5..7.5: -27.1; 7.5..8.0: -25.6)
- **defender_healers** (of which healers) falls from +30.7 to -33.2 points (0.0..0.5: +30.7; 0.5..1.5: +8.9; 1.5..2.5: -7.5; 2.5..3.5: -27.8; 3.5..4.0: -33.2)
- **res_in** (seconds until the next res) rises from -45.8 to -3.7 points (1.0..8.5: -45.8; 17.5..26.5: -0.2; 35.5..44.5: +13.7; 53.5..59.5: +14.7; 65.5..71.5: +13.3; 77.5..86.5: +11.7; 95.5..107.5: +8.2)
- **lord_health** (the Lord's rebuilt health as a share of its max (lord.py)) falls from +48.3 to -5.8 points (0.0..0.17: +48.3; 0.43..0.6: +34.1; 0.7..0.78: +28.4; 0.83..0.88: +15.6; 0.91..0.94: +11.7; 0.96..0.98: +3.5; 0.99..1.0: -4.1)
- **attackers** (enemy players in the pit) rises from -11.4 to +13.7 points (1.0..1.5: -11.4; 1.5..2.5: -8.2; 2.5..3.5: -2.0; 3.5..4.5: +3.1; 4.5..5.5: +7.2; 5.5..6.5: +9.7; 6.5..7.5: +11.4; 7.5..8.0: +13.7)


## 6b. The learned nodes (step 2 of the learned causal map)

Each node uses only the causal-map links into it. A link's strength is how much worse the node predicts matches it never saw without that link's features (refit without them, same folds); supported when the gain is more than twice its spread across folds, rejected when dropping it helps by more than that, otherwise not clear yet.

**run outcome** (map R.3; 355 matches, 11585 cases, result rate 67%): log loss 0.5376 against 0.6365 for the simple baseline (adds to the simple baseline).
- link K.13 -> R.3: gain +0.0288 (+/- 0.0045), supported (min_capture_s, runner_escapes)
- link S.scoreboard -> R.3: gain +0.0111 (+/- 0.0023), supported (morale_diff, boost_clock)
- link C.map -> R.3: gain +0.0031 (+/- 0.0014), supported (run_dist)
- link P.10 -> R.3: gain +0.002 (+/- 0.0014), not clear yet (stand_own, stand_enemy, enemy_boost_in, flag_lead...)
- link A.allocation -> R.3: gain +0.0013 (+/- 0.0012), not clear yet (escort, own_main, enemy_main, enemy_power_play)
- link C.builds -> R.3: gain +0.0006 (+/- 0.0014), not clear yet (enemy_snares)
- link C.strength -> R.3: gain +0.0004 (+/- 0.0005), not clear yet (strength_gap)
- link K.11 -> R.3: gain -0.0001 (+/- 0.0007), not clear yet (crippled_so_far, knocked_down_so_far, other_control_so_far, damage_so_far...)
  - leans on **min_capture_s** (seconds the carrier needs at least to reach the stand from here, at its fastest expected carry speed (its speed skills; Denning)): +28.0 points at 0.0 to 3.65, -27.9 at 31.05 to 46.4
  - leans on **boost_clock** (boost clock (discovery, approved)): +6.4 points at -120.0 to -112.5, -21.1 at 101.5 to 120.0
  - leans on **run_dist** (distance from the team's spawn to the stand): +8.8 points at 3654.0 to 4432.5, +4.6 at 9244.0 to 9974.0

**flag swing** (map R.3; 356 matches, 13520 cases, average 0.3 s): mean absolute error (s) 26.5689 against 28.0692 for the simple baseline (adds to the simple baseline).
- link P.10 -> R.3: gain +0.8 (+/- 0.1), supported (waiting_runner, backup_flag, stand_own, stand_enemy...)
- link S.scoreboard -> R.3: gain +0.58 (+/- 0.07), supported (flag_lead, morale_diff)
- link C.strength -> R.3: gain +0.05 (+/- 0.03), not clear yet (strength_gap)
- link A.allocation -> R.3: gain -0.0 (+/- 0.01), not clear yet (own_alive, enemy_alive, own_main, enemy_main...)
- link R.1 -> R.3: gain -0.01 (+/- 0.02), not clear yet (own_deaths_30s, enemy_deaths_30s)
- link C.clock -> R.3: gain -0.01 (+/- 0.0), not clear yet (minute, res_in)
- link C.map -> R.3: gain -0.01 (+/- 0.01), not clear yet (run_dist)
  - leans on **flag_lead** (flag lead now (s)): +14.0 s at -137.0 to -62.5, -14.7 at 61.5 to 109.0
  - leans on **morale_diff** (morale, own minus enemy (discovery, approved)): -11.6 s at -445.0 to -178.5, +12.0 at 196.5 to 430.0
  - leans on **strength_gap** (team strength gap): -5.5 s at -1183.0 to -590.0, +4.9 at 590.0 to 1183.0

**run defence** (map R.3; 355 matches, 11585 cases, result rate 67%): log loss 0.5336 against 0.6365 for the simple baseline (adds to the simple baseline).
- link S.scoreboard -> R.3: gain +0.0411 (+/- 0.0039), supported (boost_clock, stand, flag_lead, morale_diff...)
- link K.13 -> R.3: gain +0.0276 (+/- 0.0036), supported (min_capture_s)
- link C.map -> R.3: gain +0.0037 (+/- 0.0018), supported (run_dist)
- link A.allocation -> R.3: gain +0.0013 (+/- 0.001), not clear yet (escort, att_main, def_main)
- link P.10 -> R.3: gain +0.0009 (+/- 0.0009), not clear yet (runner_class)
- link C.strength -> R.3: gain +0.0003 (+/- 0.0005), not clear yet (strength_gap)
- link K.11 -> R.3: gain +0.0 (+/- 0.0005), not clear yet (def_snare_near)
- link A.mesa_free -> R.3: gain -0.0002 (+/- 0.0008), not clear yet (def_free, pushers_so_far, control_so_far, damage_so_far)
- link K.5 -> R.3: gain -0.0003 (+/- 0.0005), not clear yet (healing_monks_own)
- link C.builds -> R.3: gain -0.0005 (+/- 0.0013), not clear yet (own_snares, own_area_damage, enemy_snares_v_own_speed)
  - leans on **min_capture_s** (seconds the carrier needs at least to reach the stand from here (its speed skills)): +28.9 points at 0.0 to 3.65, -27.6 at 31.05 to 46.4
  - leans on **stand** (stand (discovery, approved)): -10.1 points at -1.0 to -0.5, +6.2 at 0.5 to 1.0
  - leans on **run_dist** (distance from the runner's spawn to the stand): +9.9 points at 3654.0 to 4432.5, +4.5 at 9244.0 to 9974.0

**capture speed** (map R.3; 340 matches, 2988 cases, average 39.5 s): mean absolute error (s) 13.1475 against 15.6824 for the simple baseline (adds to the simple baseline).
- link K.13 -> R.3: gain +2.23 (+/- 0.19), supported (min_capture_s)
- link C.map -> R.3: gain +0.41 (+/- 0.09), supported (run_dist)
- link A.allocation -> R.3: gain +0.38 (+/- 0.06), supported (defenders_free, escort)
- link P.10 -> R.3: gain +0.21 (+/- 0.03), supported (runner_class)
- link C.strength -> R.3: gain +0.05 (+/- 0.03), not clear yet (strength_gap)
- link K.11 -> R.3: gain -0.0 (+/- 0.03), not clear yet (pushers_10s, control_10s, damage_10s, def_snare_near)
  - leans on **min_capture_s** (seconds the carrier needed at least, at its fastest expected carry speed (its speed skills)): -15.1 s at 0.9 to 9.95, +14.6 at 35.95 to 45.4
  - leans on **escort** (the runner's escorts): -4.0 s at 0.0 to 0.5, +11.8 at 6.5 to 7.0
  - leans on **run_dist** (distance from the runner's spawn to the stand): +5.6 s at 4133.0 to 4417.0, -5.1 at 9242.0 to 9974.0

**power play** (map K.4; 353 matches, 3277 cases, result rate 39%): log loss 0.3342 against 0.67 for the simple baseline (adds to the simple baseline).
- link A.allocation -> K.4: gain +0.0329 (+/- 0.0049), supported (size, own_main, enemy_main, short_dead...)
- link K.2 -> K.4: gain +0.0307 (+/- 0.004), supported (dps_v_usual)
- link K.5 -> K.4: gain +0.0132 (+/- 0.0032), supported (enemy_prots_10s, enemy_heal_s)
- link P.21 -> K.4: gain +0.008 (+/- 0.002), supported (enemy_kite_10s)
- link P.2 -> K.4: gain +0.0079 (+/- 0.0021), supported (spikes_10s, spike_spread)
- link S.scoreboard -> K.4: gain +0.007 (+/- 0.0013), supported (down_diff_s, carrying_diff)
- link P.24 -> K.4: gain +0.007 (+/- 0.0026), supported (knockdowns_10s, knockdowns_on_casting_10s)
- link C.strength -> K.4: gain +0.0059 (+/- 0.0022), supported (strength_gap)
- link P.25 -> K.4: gain +0.0047 (+/- 0.0015), supported (disable_10s)
- link P.1 -> K.4: gain +0.0042 (+/- 0.001), supported (spikes_on_healers, healer_damage_share)
- link P.22 -> K.4: gain +0.0018 (+/- 0.0013), not clear yet (degen_10s)
- link R.3 -> K.4: gain +0.0012 (+/- 0.0012), not clear yet (flag_lead)
- link P.23 -> K.4: gain +0.0012 (+/- 0.001), not clear yet (enemy_baits_10s)
- link P.14 -> K.4: gain +0.0009 (+/- 0.0015), not clear yet (pushed)
- link C.builds -> K.4: gain +0.0007 (+/- 0.0007), not clear yet (enemy_strips_v_own_prots)
- link P.26 -> K.4: gain +0.0006 (+/- 0.0004), not clear yet (castprev_10s)
- link K.11 -> K.4: gain -0.0001 (+/- 0.0006), not clear yet (blind_secs_on_own_10s)
  - leans on **short_dead** (share of the enemy's missing player-seconds: dead): -17.5 points at 0.0 to 0.01, +18.7 at 0.99 to 1.0
  - leans on **dps_v_usual** (own damage per second against the usual of the players alive): -38.7 points at 0.0 to 0.56, +26.2 at 3.16 to 21.09
  - leans on **window_s** (seconds the power play lasted): -13.7 points at 14.0 to 30.5, +34.7 at 95.5 to 351.0

**fight outcome** (map R.2; 355 matches, 2718 cases, result rate 46%): log loss 0.2323 against 0.6908 for the simple baseline (adds to the simple baseline).
- link S.scoreboard -> R.2: gain +0.101 (+/- 0.0092), supported (morale_diff, fight_state, down_diff_s, alive_diff...)
- link P.2 -> R.2: gain +0.0234 (+/- 0.0062), supported (spike_spread_diff, spikes_diff)
- link K.1 -> R.2: gain +0.0216 (+/- 0.002), supported (dps_v_usual_diff)
- link A.allocation -> R.2: gain +0.0158 (+/- 0.0013), supported (own_local, enemy_local)
- link P.17 -> R.2: gain +0.0099 (+/- 0.003), supported (ready_interrupt_diff, dazed_casts_diff, blind_attacks_diff)
- link C.builds -> R.2: gain +0.0046 (+/- 0.0012), supported (own_hexes, own_heals)
- link C.strength -> R.2: gain +0.0015 (+/- 0.0016), not clear yet (strength_gap)
- link P.13 -> R.2: gain +0.0006 (+/- 0.0009), not clear yet (peel_defensive_diff)
- link P.25 -> R.2: gain +0.0002 (+/- 0.0011), not clear yet (disable_diff)
- link P.26 -> R.2: gain +0.0001 (+/- 0.0007), not clear yet (castprev_diff)
- link P.18 -> R.2: gain -0.0001 (+/- 0.0015), not clear yet (strip_right_diff, strip_value_diff)
- link P.23 -> R.2: gain -0.0003 (+/- 0.0008), not clear yet (baits_diff)
- link P.1 -> R.2: gain -0.0006 (+/- 0.0007), not clear yet (healer_focus_diff)
- link P.22 -> R.2: gain -0.0008 (+/- 0.0008), not clear yet (degen_diff)
- link P.24 -> R.2: gain -0.0008 (+/- 0.0007), not clear yet (knockdowns_diff, knockdowns_on_casting_diff)
- link P.19 -> R.2: gain -0.0014 (+/- 0.0006), rejected (blind_front_secs_diff, blind_defensive_secs_diff)
- link P.5 -> R.2: gain -0.0017 (+/- 0.0018), not clear yet (hex_secs_diff, hex_right_diff)
- link P.21 -> R.2: gain -0.0019 (+/- 0.0005), rejected (kite_secs_diff, prekite_secs_diff)
  - leans on **morale_diff** (morale, own minus enemy (discovery, approved)): -18.3 points at -470.0 to -213.5, +35.7 at 214.5 to 410.0
  - leans on **dps_v_usual_diff** (damage against the usual of the players alive, own minus enemy): -30.5 points at -15.06 to -1.87, +33.9 at 1.9 to 13.46
  - leans on **own_local** (own players in the fight): -36.6 points at 0.0 to 0.5, +20.1 at 7.5 to 8.0

**split chance** (map A.allocation; 356 matches, 26277 cases, result rate 14%): log loss 0.343 against 0.3962 for the simple baseline (adds to the simple baseline).
- link S.scoreboard -> A.allocation: gain +0.029 (+/- 0.0017), supported (flag_lead, own_alive, enemy_alive, own_main...)
- link C.builds -> A.allocation: gain +0.0104 (+/- 0.0026), supported (own_speed_power, own_escapes, own_snare_power, enemy_snare_power...)
- link C.clock -> A.allocation: gain +0.0033 (+/- 0.0012), supported (minute, res_in)
- link C.strength -> A.allocation: gain -0.0002 (+/- 0.0003), not clear yet (strength_gap)
  - leans on **own_main** (own main): +27.5 points at 0.0 to 2.5, -17.5 at 7.5 to 8.0
  - leans on **spike_build_own** (own build is a spike build (discovery, approved)): +5.9 points at 0.0 to 0.5, -13.8 at 0.5 to 1.0
  - leans on **turtle_diff** (turtling, own minus enemy (discovery, approved)): +1.0 points at -1.0 to -0.94, -29.9 at 0.94 to 1.0

**split answer** (map P.11; 250 matches, 968 cases, average -5.5 s): mean absolute error (s) 15.6319 against 17.9628 for the simple baseline (adds to the simple baseline).
- link A.allocation -> P.11: gain +0.86 (+/- 0.2), supported (size)
- link A.mesa_free -> P.11: gain +0.59 (+/- 0.14), supported (def_free, nearest_to_base)
- link S.scoreboard -> P.11: gain +0.41 (+/- 0.09), supported (flag_lead, def_alive, att_main, split_diff)
- link C.builds -> P.11: gain +0.09 (+/- 0.05), not clear yet (own_area_damage)
- link C.clock -> P.11: gain +0.07 (+/- 0.06), not clear yet (minute)
- link C.strength -> P.11: gain +0.0 (+/- 0.04), not clear yet (strength_gap)
  - leans on **size** (split size): +15.9 s at 1.0 to 1.5, -10.1 at 5.5 to 7.0
  - leans on **nearest_to_base** (nearest defender to its base at the split's entry): +8.3 s at 17.0 to 368.5, +11.6 at 6896.0 to 13999.0
  - leans on **split_diff** (players splitting, own minus enemy (discovery, approved)): +9.5 s at -6.0 to -5.5, +12.0 at 2.5 to 4.0

**split effect** (map R.5; 250 matches, 968 cases, result rate 38%): log loss 0.6335 against 0.6676 for the simple baseline (adds to the simple baseline).
- link S.scoreboard -> R.5: gain +0.0281 (+/- 0.0101), supported (def_npc_value, def_free, morale_diff, flag_lead...)
- link C.builds -> R.5: gain +0.008 (+/- 0.0018), supported (enemy_prots)
- link P.11 -> R.5: gain +0.0027 (+/- 0.0019), not clear yet (latency, defenders)
- link A.allocation -> R.5: gain +0.0011 (+/- 0.001), not clear yet (size, main_diff)
- link K.11 -> R.5: gain +0.0003 (+/- 0.0012), not clear yet (def_snare_present)
- link K.13 -> R.5: gain +0.0001 (+/- 0.0011), not clear yet (split_speed_power, own_escapes_power)
- link C.strength -> R.5: gain +0.0001 (+/- 0.0005), not clear yet (strength_gap)
- link K.8 -> R.5: gain -0.0003 (+/- 0.001), not clear yet (split_healers)
  - leans on **enemy_prots** (prot skills on the defenders' bars (discovery, approved)): +5.5 points at 0.0 to 9.5, -5.4 at 14.5 to 19.0
  - leans on **flag_lead** (flag lead (discovery, approved)): -7.1 points at -80.0 to -53.5, +4.2 at 54.5 to 80.0
  - leans on **def_npc_value** (defenders' pit NPC value when the split entered the base): -13.3 points at 0.0 to 0.75, +3.0 at 11.25 to 13.5

**pit npc loss** (map R.5; 354 matches, 35789 cases, result rate 21%): log loss 0.3619 against 0.5093 for the simple baseline (adds to the simple baseline).
- link P.11 -> R.5: gain +0.049 (+/- 0.0023), supported (defenders, defender_healers, defenders_elsewhere)
- link K.1 -> R.5: gain +0.0303 (+/- 0.0012), supported (npc_damage_5s)
- link C.builds -> R.5: gain +0.0028 (+/- 0.0007), supported (attackers_lord_dps, attackers_area_damage)
- link C.strength -> R.5: gain +0.0019 (+/- 0.0008), supported (strength_gap)
- link S.scoreboard -> R.5: gain +0.0017 (+/- 0.0008), supported (knights, archers, bodyguard, full_pit_targets)
- link K.6 -> R.5: gain +0.0014 (+/- 0.0005), supported (npc_healing_10s)
- link C.clock -> R.5: gain +0.0006 (+/- 0.0005), not clear yet (seconds_in_pit, res_in, minute)
- link A.allocation -> R.5: gain -0.0001 (+/- 0.0005), not clear yet (attackers, attacker_healers, attackers_share, attackers_outside)
  - leans on **defenders** (own players in the pit): +32.9 points at 0.0 to 0.5, -31.9 at 7.5 to 8.0
  - leans on **npc_damage_5s** (damage on the pit NPCs in the last 5 s): -15.8 points at 0.0 to 0.5, +33.0 at 385.5 to 1370.0
  - leans on **defenders_elsewhere** (own players alive outside the pit): +19.6 points at 0.0 to 0.5, -10.3 at 7.5 to 8.0

**collapse** (map R.1; 325 matches, 2251 cases, result rate 13%): log loss 0.3117 against 0.3927 for the simple baseline (adds to the simple baseline).
- link C.strength -> R.1: gain +0.0086 (+/- 0.0032), supported (strength_gap)
- link K.1 -> R.1: gain +0.0076 (+/- 0.002), supported (def_dps)
- link K.9 -> R.1: gain +0.0069 (+/- 0.0021), supported (split_dp)
- link A.allocation -> R.1: gain +0.0034 (+/- 0.0022), not clear yet (size, main_diff)
- link K.5 -> R.1: gain +0.0025 (+/- 0.0012), supported (split_healers, split_self_defence, healing_monks_enemy)
- link P.20 -> R.1: gain +0.0023 (+/- 0.0008), supported (depth_at_arrival, depth_median)
  - alone: depth_at_arrival (nearest split member's distance to the defending pit when the first defender arrived): gain +0.0008 (+/- 0.0005), not clear yet
  - alone: depth_median (nearest split member's median distance to the defending pit over the split): gain +0.0002 (+/- 0.001), not clear yet
- link P.11 -> R.1: gain +0.0018 (+/- 0.0005), supported (latency)
- link K.11 -> R.1: gain +0.0013 (+/- 0.0011), not clear yet (def_snare_present)
- link C.builds -> R.1: gain +0.0 (+/- 0.0004), not clear yet (split_npc_dps)
- link K.13 -> R.1: gain -0.0005 (+/- 0.0011), not clear yet (escape_ready, split_speed_power, split_escapes)
- link S.scoreboard -> R.1: gain -0.0006 (+/- 0.0006), not clear yet (def_npc_value)
- link P.9 -> R.1: gain -0.0016 (+/- 0.0009), not clear yet (defenders_10s, contact_diff, npc_hit_to_arrival, res_in_at_arrival)
  - alone: defenders_10s (defenders arriving within 10 s of the first (arrival spread)): gain +0.0001 (+/- 0.0003), not clear yet
  - alone: contact_diff (defenders arriving within 5 s of the first, minus the split's size (numbers at contact)): gain +0.0003 (+/- 0.0007), not clear yet
  - alone: npc_hit_to_arrival (seconds from the split's first hit on an NPC to the first defender's arrival): gain +0.0002 (+/- 0.0005), not clear yet
  - alone: res_in_at_arrival (seconds to the next res when the first defender arrived): gain -0.0001 (+/- 0.0008), not clear yet
  - leans on **def_dps** (the defenders who came: their usual damage per second, summed (Denning: can they kill it)): -17.2 points at 0.0 to 1.7, +19.1 at 41.7 to 53.7
  - leans on **strength_gap** (splitting team's strength gap): +14.3 points at -1183.0 to -592.5, -6.9 at 621.0 to 1183.0
  - leans on **split_dp** (worst morale among the split members (death penalty lowers max health; Denning)): +26.4 points at -60.0 to -44.5, -7.5 at 9.5 to 10.0

## 7. The usual play

Each choice against the most common one in that kind of decision, in win-chance points over the decision's window, adjusted for the situation, with a 90% range from resampling whole matches. CLEAR = the range excludes 0. Win chance comes from a model that never saw the match. The same comparison over the 30 s BEFORE the decision is a placebo test: a choice can't cause what came before it, so a clear difference there means the effect is partly who makes that choice.

**after wipe** (821 decisions, 337 matches; usual: pushed the pit)
- reset (n 122): -2.6 [-4.2, -1.0] CLEAR; in the 30 s before: +0.4 [-1.4, +2.2]
- took the flag (n 96): -1.2 [-3.9, +2.0]; in the 30 s before: +1.9 [+0.1, +4.7] ALREADY DIFFERENT BEFORE: partly who chooses it
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - reset, Corrupted Isle: -3.1 (n 20 against 76)
  - reset, Druid's Isle: -3.0 (n 13 against 74)
  - reset, Isle of Jade: -4.0 (n 22 against 81)
  - reset, Isle of Meditation: -2.1 (n 21 against 113)
  - reset, Isle of Solitude: -2.5 (n 13 against 107)
  - reset, Isle of Weeping Stone: -0.6 (n 10 against 49)
  - reset, Uncharted Isle: -7.4 (n 10 against 74)
  - took the flag, Corrupted Isle: +3.7 (n 19 against 76)
  - took the flag, Druid's Isle: -0.9 (n 16 against 74)
  - took the flag, Isle of Jade: -5.3 (n 14 against 81)
  - took the flag, Isle of Meditation: -4.0 (n 21 against 113)

**boost clock** (1322 decisions, 330 matches; usual: not running, fought)
- not running, fell back (n 211): -0.5 [-1.8, +1.2]; in the 30 s before: -0.3 [-1.3, +0.8]
- running, advanced (n 193): +2.3 [+0.7, +3.7] CLEAR; in the 30 s before: +1.5 [+0.5, +2.3] ALREADY DIFFERENT BEFORE: partly who chooses it
- not running, advanced (n 174): +0.6 [-0.9, +2.0]; in the 30 s before: +0.6 [-0.3, +1.6]
- running, fought (n 146): +3.2 [+1.5, +4.7] CLEAR; in the 30 s before: +0.7 [-0.5, +1.9]
- not running, held (n 118): +1.3 [-0.1, +2.7]; in the 30 s before: -0.0 [-1.1, +0.8]
- running, fell back (n 98): +5.6 [+3.5, +7.9] CLEAR; in the 30 s before: -1.0 [-2.4, +0.3]
- running, held (n 66): +2.3 [+0.3, +3.7] CLEAR; in the 30 s before: +1.5 [+0.2, +2.8] ALREADY DIFFERENT BEFORE: partly who chooses it
- not running, to the spawn (n 21): -0.8 [-3.3, +1.3]; in the 30 s before: +2.3 [-0.0, +4.8]
- running, to the spawn (n 5): +1.8 [+0.3, +3.5] CLEAR; in the 30 s before: +1.5 [-0.8, +3.5]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - not running, fell back, behind in the fight (lowest third, -0.12 or less): +0.3 (n 104 against 127)
  - not running, fell back, middle third: -2.6 (n 67 against 95)
  - not running, fell back, ahead in the fight (top third, above -0.01): -0.3 (n 40 against 68)
  - running, advanced, behind in the fight (lowest third, -0.12 or less): +1.3 (n 31 against 127)
  - running, advanced, middle third: +0.5 (n 69 against 95)
  - running, advanced, ahead in the fight (top third, above -0.01): +4.2 (n 93 against 68)
  - not running, advanced, behind in the fight (lowest third, -0.12 or less): +0.2 (n 49 against 127)
  - not running, advanced, middle third: +0.7 (n 68 against 95)
  - not running, advanced, ahead in the fight (top third, above -0.01): +0.6 (n 57 against 68)
  - running, fought, behind in the fight (lowest third, -0.12 or less): +0.2 (n 37 against 127)
  - running, fought, middle third: +1.4 (n 45 against 95)
  - running, fought, ahead in the fight (top third, above -0.01): +5.8 (n 64 against 68)
  - not running, held, behind in the fight (lowest third, -0.12 or less): +0.9 (n 48 against 127)
  - not running, held, middle third: -0.7 (n 34 against 95)
  - not running, held, ahead in the fight (top third, above -0.01): +4.1 (n 36 against 68)
  - running, fell back, behind in the fight (lowest third, -0.12 or less): +1.6 (n 25 against 127)
  - running, fell back, middle third: +5.7 (n 40 against 95)
  - running, fell back, ahead in the fight (top third, above -0.01): +7.3 (n 33 against 68)
  - running, held, behind in the fight (lowest third, -0.12 or less): too few yet (n 7 against 127; means 0.4 against -1.1)
  - running, held, middle third: +1.5 (n 25 against 95)
  - running, held, ahead in the fight (top third, above -0.01): +3.2 (n 34 against 68)
  - not running, to the spawn, behind in the fight (lowest third, -0.12 or less): -1.4 (n 13 against 127)
  - not running, to the spawn, middle third: too few yet (n 3 against 95; means 1.1 against -0.2)
  - not running, to the spawn, ahead in the fight (top third, above -0.01): too few yet (n 5 against 68; means -1.4 against -3.5)
  - running, to the spawn, behind in the fight (lowest third, -0.12 or less): too few yet (n 2 against 127; means 0.0 against -1.1)
  - running, to the spawn, middle third: too few yet (n 2 against 95; means 1.2 against -0.2)
  - running, to the spawn, ahead in the fight (top third, above -0.01): too few yet (n 1 against 68; means 2.0 against -3.5)
  By snare matchup (movepower.py: enemy snare power of the live players minus own speed power; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - not running, fell back, little enemy snare for own speed (lowest third, -28 or less): -2.1 (n 65 against 69)
  - not running, fell back, middle third: +0.7 (n 73 against 114)
  - not running, fell back, a lot of enemy snare for own speed (top third, above -1): -0.7 (n 73 against 107)
  - running, advanced, little enemy snare for own speed (lowest third, -28 or less): +2.0 (n 76 against 69)
  - running, advanced, middle third: +3.6 (n 60 against 114)
  - running, advanced, a lot of enemy snare for own speed (top third, above -1): +0.2 (n 57 against 107)
  - not running, advanced, little enemy snare for own speed (lowest third, -28 or less): +0.6 (n 71 against 69)
  - not running, advanced, middle third: +0.6 (n 58 against 114)
  - not running, advanced, a lot of enemy snare for own speed (top third, above -1): +0.6 (n 45 against 107)
  - running, fought, little enemy snare for own speed (lowest third, -28 or less): +2.6 (n 57 against 69)
  - running, fought, middle third: +2.8 (n 38 against 114)
  - running, fought, a lot of enemy snare for own speed (top third, above -1): +2.3 (n 51 against 107)
  - not running, held, little enemy snare for own speed (lowest third, -28 or less): +1.4 (n 33 against 69)
  - not running, held, middle third: +1.6 (n 39 against 114)
  - not running, held, a lot of enemy snare for own speed (top third, above -1): +0.6 (n 46 against 107)
  - running, fell back, little enemy snare for own speed (lowest third, -28 or less): +5.5 (n 43 against 69)
  - running, fell back, middle third: +6.3 (n 26 against 114)
  - running, fell back, a lot of enemy snare for own speed (top third, above -1): +3.5 (n 29 against 107)
  - running, held, little enemy snare for own speed (lowest third, -28 or less): +1.9 (n 24 against 69)
  - running, held, middle third: +2.8 (n 24 against 114)
  - running, held, a lot of enemy snare for own speed (top third, above -1): +1.0 (n 18 against 107)
  - not running, to the spawn, little enemy snare for own speed (lowest third, -28 or less): too few yet (n 3 against 69; means -8.8 against -2.0)
  - not running, to the spawn, middle third: too few yet (n 5 against 114; means -0.5 against -2.4)
  - not running, to the spawn, a lot of enemy snare for own speed (top third, above -1): -0.7 (n 13 against 107)
  - running, to the spawn, little enemy snare for own speed (lowest third, -28 or less): too few yet (n 2 against 69; means 2.2 against -2.0)
  - running, to the spawn, middle third: too few yet (n 1 against 114; means 0.0 against -2.4)
  - running, to the spawn, a lot of enemy snare for own speed (top third, above -1): too few yet (n 2 against 107; means 0.0 against 0.1)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - not running, fell back, Corrupted Isle: +4.4 (n 34 against 33)
  - not running, fell back, Druid's Isle: +1.2 (n 32 against 26)
  - not running, fell back, Isle of Jade: -3.7 (n 22 against 48)
  - not running, fell back, Isle of Meditation: -0.9 (n 37 against 66)
  - not running, fell back, Isle of Solitude: -1.0 (n 32 against 41)
  - not running, fell back, Uncharted Isle: -0.0 (n 29 against 38)
  - running, advanced, Corrupted Isle: +5.7 (n 37 against 33)
  - running, advanced, Druid's Isle: +1.6 (n 15 against 26)
  - running, advanced, Isle of Jade: -4.3 (n 13 against 48)
  - running, advanced, Isle of Meditation: +3.4 (n 49 against 66)
  - running, advanced, Isle of Solitude: +1.5 (n 27 against 41)
  - running, advanced, Isle of Weeping Stone: -5.0 (n 27 against 13)
  - running, advanced, Uncharted Isle: +0.3 (n 14 against 38)
  - not running, advanced, Corrupted Isle: +6.3 (n 32 against 33)
  - not running, advanced, Druid's Isle: +3.6 (n 10 against 26)
  - not running, advanced, Isle of Jade: -3.0 (n 18 against 48)
  - not running, advanced, Isle of Meditation: +1.0 (n 33 against 66)
  - not running, advanced, Isle of Solitude: +1.7 (n 34 against 41)
  - not running, advanced, Isle of Weeping Stone: -11.2 (n 11 against 13)
  - not running, advanced, Uncharted Isle: -2.7 (n 26 against 38)
  - running, fought, Corrupted Isle: +3.4 (n 17 against 33)
  - running, fought, Druid's Isle: +4.1 (n 29 against 26)
  - running, fought, Isle of Jade: +1.0 (n 11 against 48)
  - running, fought, Isle of Meditation: -0.2 (n 30 against 66)
  - running, fought, Isle of Solitude: +2.9 (n 23 against 41)
  - running, fought, Uncharted Isle: +4.5 (n 15 against 38)
  - not running, held, Corrupted Isle: +0.6 (n 15 against 33)
  - not running, held, Druid's Isle: +3.3 (n 18 against 26)
  - not running, held, Isle of Jade: +0.3 (n 25 against 48)
  - not running, held, Isle of Meditation: +2.3 (n 16 against 66)
  - not running, held, Isle of Solitude: +2.5 (n 27 against 41)
  - running, fell back, Corrupted Isle: +8.4 (n 16 against 33)
  - running, fell back, Isle of Meditation: +4.1 (n 16 against 66)
  - running, fell back, Isle of Solitude: +5.2 (n 17 against 41)
  - running, fell back, Isle of Weeping Stone: -3.4 (n 16 against 13)
  - running, fell back, Uncharted Isle: +5.3 (n 18 against 38)
  - running, held, Isle of Jade: -1.4 (n 21 against 48)
  - running, held, Isle of Solitude: +3.0 (n 10 against 41)

**enemy pickup** (4443 decisions, 339 matches; usual: held, advanced)
- already running, advanced (n 615): -1.0 [-2.6, +0.8]; in the 30 s before: +2.1 [+1.0, +3.7] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, fell back (n 572): -0.8 [-2.4, +0.7]; in the 30 s before: -0.1 [-1.2, +1.2]
- already running, fell back (n 470): -1.0 [-2.4, +0.9]; in the 30 s before: +1.3 [+0.3, +2.8] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, fought (n 455): -1.3 [-2.8, +0.3]; in the 30 s before: +0.2 [-0.6, +1.2]
- already running, fought (n 381): -2.0 [-3.7, -0.2] CLEAR; in the 30 s before: +1.6 [+0.5, +3.0] ALREADY DIFFERENT BEFORE: partly who chooses it
- ran, fell back (n 338): +1.8 [+0.4, +3.4] CLEAR; in the 30 s before: +0.7 [-0.4, +2.0]
- ran, advanced (n 266): -0.3 [-1.9, +2.0]; in the 30 s before: +1.9 [+0.6, +3.4] ALREADY DIFFERENT BEFORE: partly who chooses it
- ran, fought (n 195): +0.2 [-1.1, +1.8]; in the 30 s before: +0.8 [-0.5, +2.4]
- held, held (n 191): -0.2 [-1.7, +1.6]; in the 30 s before: +0.7 [-0.3, +2.0]
- already running, held (n 189): -2.2 [-4.0, -0.0] CLEAR; in the 30 s before: +1.6 [+0.4, +3.4] ALREADY DIFFERENT BEFORE: partly who chooses it
- ran, held (n 117): +0.6 [-1.4, +3.1]; in the 30 s before: +0.6 [-0.7, +2.2]
- held, to the spawn (n 10): -3.4 [-7.7, +0.5]; in the 30 s before: +1.9 [-1.6, +6.4]
- held (n 8): -11.3 [-19.9, -3.6] CLEAR; in the 30 s before: +9.4 [+4.8, +14.0] ALREADY DIFFERENT BEFORE: partly who chooses it
- ran, to the spawn (n 5): +0.5 [-1.5, +2.9]; in the 30 s before: -2.0 [-6.0, +1.8]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - already running, advanced, behind in the fight (lowest third, -0.01 or less): +2.3 (n 164 against 160)
  - already running, advanced, middle third: -0.2 (n 273 against 189)
  - already running, advanced, ahead in the fight (top third, above +0.02): -1.2 (n 178 against 282)
  - held, fell back, behind in the fight (lowest third, -0.01 or less): +0.0 (n 262 against 160)
  - held, fell back, middle third: +0.8 (n 149 against 189)
  - held, fell back, ahead in the fight (top third, above +0.02): -2.7 (n 161 against 282)
  - already running, fell back, behind in the fight (lowest third, -0.01 or less): +2.1 (n 204 against 160)
  - already running, fell back, middle third: -0.7 (n 176 against 189)
  - already running, fell back, ahead in the fight (top third, above +0.02): -1.0 (n 90 against 282)
  - held, fought, behind in the fight (lowest third, -0.01 or less): -1.6 (n 125 against 160)
  - held, fought, middle third: +0.4 (n 79 against 189)
  - held, fought, ahead in the fight (top third, above +0.02): -2.8 (n 251 against 282)
  - already running, fought, behind in the fight (lowest third, -0.01 or less): +1.2 (n 131 against 160)
  - already running, fought, middle third: -0.3 (n 113 against 189)
  - already running, fought, ahead in the fight (top third, above +0.02): -3.0 (n 137 against 282)
  - ran, fell back, behind in the fight (lowest third, -0.01 or less): +2.9 (n 143 against 160)
  - ran, fell back, middle third: +3.0 (n 115 against 189)
  - ran, fell back, ahead in the fight (top third, above +0.02): +0.8 (n 80 against 282)
  - ran, advanced, behind in the fight (lowest third, -0.01 or less): +1.6 (n 79 against 160)
  - ran, advanced, middle third: +1.0 (n 104 against 189)
  - ran, advanced, ahead in the fight (top third, above +0.02): -2.5 (n 83 against 282)
  - ran, fought, behind in the fight (lowest third, -0.01 or less): +2.8 (n 67 against 160)
  - ran, fought, middle third: +0.2 (n 57 against 189)
  - ran, fought, ahead in the fight (top third, above +0.02): -2.0 (n 71 against 282)
  - held, held, behind in the fight (lowest third, -0.01 or less): -1.5 (n 54 against 160)
  - held, held, middle third: +3.1 (n 78 against 189)
  - held, held, ahead in the fight (top third, above +0.02): -2.1 (n 59 against 282)
  - already running, held, behind in the fight (lowest third, -0.01 or less): -0.5 (n 55 against 160)
  - already running, held, middle third: -0.7 (n 98 against 189)
  - already running, held, ahead in the fight (top third, above +0.02): -0.9 (n 36 against 282)
  - ran, held, behind in the fight (lowest third, -0.01 or less): +2.1 (n 48 against 160)
  - ran, held, middle third: +1.6 (n 50 against 189)
  - ran, held, ahead in the fight (top third, above +0.02): +1.6 (n 19 against 282)
  - held, to the spawn, behind in the fight (lowest third, -0.01 or less): too few yet (n 6 against 160; means -2.1 against -0.9)
  - held, to the spawn, middle third: too few yet (n 3 against 189; means 2.4 against -0.3)
  - held, to the spawn, ahead in the fight (top third, above +0.02): too few yet (n 1 against 282; means -1.0 against 1.2)
  - held, behind in the fight (lowest third, -0.01 or less): too few yet (n 3 against 160; means -11.5 against -0.9)
  - held, middle third: too few yet (n 4 against 189; means 0.0 against -0.3)
  - held, ahead in the fight (top third, above +0.02): too few yet (n 1 against 282; means 0.0 against 1.2)
  - ran, to the spawn, middle third: too few yet (n 2 against 189; means 1.4 against -0.3)
  - ran, to the spawn, ahead in the fight (top third, above +0.02): too few yet (n 3 against 282; means 0.5 against 1.2)
  By snare matchup (movepower.py: enemy snare power of the live players minus own speed power; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - already running, advanced, little enemy snare for own speed (lowest third, -33 or less): +1.9 (n 260 against 185)
  - already running, advanced, middle third: -3.9 (n 182 against 238)
  - already running, advanced, a lot of enemy snare for own speed (top third, above -5): +2.2 (n 173 against 208)
  - held, fell back, little enemy snare for own speed (lowest third, -33 or less): -1.1 (n 179 against 185)
  - held, fell back, middle third: -2.1 (n 185 against 238)
  - held, fell back, a lot of enemy snare for own speed (top third, above -5): +1.1 (n 208 against 208)
  - already running, fell back, little enemy snare for own speed (lowest third, -33 or less): +0.3 (n 174 against 185)
  - already running, fell back, middle third: -2.7 (n 146 against 238)
  - already running, fell back, a lot of enemy snare for own speed (top third, above -5): +3.0 (n 150 against 208)
  - held, fought, little enemy snare for own speed (lowest third, -33 or less): -0.5 (n 145 against 185)
  - held, fought, middle third: -2.2 (n 159 against 238)
  - held, fought, a lot of enemy snare for own speed (top third, above -5): -2.1 (n 151 against 208)
  - already running, fought, little enemy snare for own speed (lowest third, -33 or less): -0.9 (n 107 against 185)
  - already running, fought, middle third: -3.3 (n 143 against 238)
  - already running, fought, a lot of enemy snare for own speed (top third, above -5): +1.6 (n 131 against 208)
  - ran, fell back, little enemy snare for own speed (lowest third, -33 or less): +4.8 (n 109 against 185)
  - ran, fell back, middle third: -2.1 (n 120 against 238)
  - ran, fell back, a lot of enemy snare for own speed (top third, above -5): +4.0 (n 109 against 208)
  - ran, advanced, little enemy snare for own speed (lowest third, -33 or less): +1.2 (n 88 against 185)
  - ran, advanced, middle third: -2.8 (n 85 against 238)
  - ran, advanced, a lot of enemy snare for own speed (top third, above -5): +1.6 (n 93 against 208)
  - ran, fought, little enemy snare for own speed (lowest third, -33 or less): +1.4 (n 56 against 185)
  - ran, fought, middle third: -1.3 (n 67 against 238)
  - ran, fought, a lot of enemy snare for own speed (top third, above -5): +0.9 (n 72 against 208)
  - held, held, little enemy snare for own speed (lowest third, -33 or less): +1.7 (n 60 against 185)
  - held, held, middle third: -4.6 (n 61 against 238)
  - held, held, a lot of enemy snare for own speed (top third, above -5): +3.2 (n 70 against 208)
  - already running, held, little enemy snare for own speed (lowest third, -33 or less): +0.7 (n 75 against 185)
  - already running, held, middle third: -5.8 (n 58 against 238)
  - already running, held, a lot of enemy snare for own speed (top third, above -5): +2.3 (n 56 against 208)
  - ran, held, little enemy snare for own speed (lowest third, -33 or less): +4.2 (n 34 against 185)
  - ran, held, middle third: -0.1 (n 39 against 238)
  - ran, held, a lot of enemy snare for own speed (top third, above -5): +0.9 (n 44 against 208)
  - held, to the spawn, little enemy snare for own speed (lowest third, -33 or less): too few yet (n 4 against 185; means -0.7 against -1.3)
  - held, to the spawn, middle third: too few yet (n 1 against 238; means 0.7 against 3.2)
  - held, to the spawn, a lot of enemy snare for own speed (top third, above -5): too few yet (n 5 against 208; means -0.9 against -1.9)
  - held, little enemy snare for own speed (lowest third, -33 or less): too few yet (n 1 against 185; means -34.9 against -1.3)
  - held, a lot of enemy snare for own speed (top third, above -5): too few yet (n 7 against 208; means 0.1 against -1.9)
  - ran, to the spawn, little enemy snare for own speed (lowest third, -33 or less): too few yet (n 4 against 185; means 0.3 against -1.3)
  - ran, to the spawn, middle third: too few yet (n 1 against 238; means 2.7 against 3.2)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - already running, advanced, Corrupted Isle: -0.7 (n 125 against 131)
  - already running, advanced, Druid's Isle: -0.7 (n 45 against 42)
  - already running, advanced, Imperial Isle: -4.1 (n 33 against 20)
  - already running, advanced, Isle of Jade: -2.0 (n 31 against 64)
  - already running, advanced, Isle of Meditation: -0.5 (n 98 against 100)
  - already running, advanced, Isle of Solitude: +2.3 (n 87 against 74)
  - already running, advanced, Isle of Weeping Stone: +1.2 (n 77 against 59)
  - already running, advanced, Uncharted Isle: -0.1 (n 110 against 124)
  - held, fell back, Corrupted Isle: -3.9 (n 119 against 131)
  - held, fell back, Druid's Isle: -1.3 (n 35 against 42)
  - held, fell back, Imperial Isle: +1.2 (n 19 against 20)
  - held, fell back, Isle of Jade: +5.0 (n 52 against 64)
  - held, fell back, Isle of Meditation: -2.8 (n 100 against 100)
  - held, fell back, Isle of Solitude: +1.9 (n 75 against 74)
  - held, fell back, Isle of Weeping Stone: -0.2 (n 58 against 59)
  - held, fell back, Nomad's Isle: +0.1 (n 15 against 17)
  - held, fell back, Uncharted Isle: -1.4 (n 98 against 124)
  - already running, fell back, Corrupted Isle: +0.0 (n 84 against 131)
  - already running, fell back, Druid's Isle: -2.8 (n 28 against 42)
  - already running, fell back, Imperial Isle: -0.2 (n 17 against 20)
  - already running, fell back, Isle of Jade: +0.5 (n 20 against 64)
  - already running, fell back, Isle of Meditation: +0.1 (n 71 against 100)
  - already running, fell back, Isle of Solitude: -0.1 (n 65 against 74)
  - already running, fell back, Isle of Weeping Stone: +2.1 (n 53 against 59)
  - already running, fell back, Nomad's Isle: -1.8 (n 19 against 17)
  - already running, fell back, Uncharted Isle: -0.7 (n 113 against 124)
  - held, fought, Corrupted Isle: +1.3 (n 64 against 131)
  - held, fought, Druid's Isle: -4.9 (n 83 against 42)
  - held, fought, Imperial Isle: -6.8 (n 13 against 20)
  - held, fought, Isle of Jade: +1.2 (n 42 against 64)
  - held, fought, Isle of Meditation: -1.3 (n 80 against 100)
  - held, fought, Isle of Solitude: -0.5 (n 47 against 74)
  - held, fought, Isle of Weeping Stone: -0.7 (n 40 against 59)
  - held, fought, Nomad's Isle: -3.2 (n 39 against 17)
  - held, fought, Uncharted Isle: -5.3 (n 45 against 124)
  - already running, fought, Corrupted Isle: -2.9 (n 59 against 131)
  - already running, fought, Druid's Isle: -4.3 (n 42 against 42)
  - already running, fought, Imperial Isle: +1.2 (n 22 against 20)
  - already running, fought, Isle of Jade: +3.8 (n 19 against 64)
  - already running, fought, Isle of Meditation: -1.3 (n 59 against 100)
  - already running, fought, Isle of Solitude: +1.3 (n 62 against 74)
  - already running, fought, Isle of Weeping Stone: +2.3 (n 51 against 59)
  - already running, fought, Nomad's Isle: -1.4 (n 27 against 17)
  - already running, fought, Uncharted Isle: -5.1 (n 40 against 124)
  - ran, fell back, Corrupted Isle: +2.9 (n 69 against 131)
  - ran, fell back, Druid's Isle: -0.2 (n 23 against 42)
  - ran, fell back, Imperial Isle: -0.1 (n 20 against 20)
  - ran, fell back, Isle of Jade: +4.1 (n 21 against 64)
  - ran, fell back, Isle of Meditation: -0.0 (n 41 against 100)
  - ran, fell back, Isle of Solitude: +1.8 (n 50 against 74)
  - ran, fell back, Isle of Weeping Stone: +4.9 (n 40 against 59)
  - ran, fell back, Uncharted Isle: +2.6 (n 67 against 124)
  - ran, advanced, Corrupted Isle: -4.5 (n 35 against 131)
  - ran, advanced, Druid's Isle: -4.1 (n 15 against 42)
  - ran, advanced, Imperial Isle: -4.0 (n 24 against 20)
  - ran, advanced, Isle of Jade: +6.6 (n 33 against 64)
  - ran, advanced, Isle of Meditation: +0.3 (n 42 against 100)
  - ran, advanced, Isle of Solitude: +1.4 (n 32 against 74)
  - ran, advanced, Isle of Weeping Stone: +4.6 (n 32 against 59)
  - ran, advanced, Uncharted Isle: -2.2 (n 51 against 124)
  - ran, fought, Corrupted Isle: +2.1 (n 17 against 131)
  - ran, fought, Druid's Isle: +1.7 (n 29 against 42)
  - ran, fought, Imperial Isle: -1.5 (n 23 against 20)
  - ran, fought, Isle of Jade: -0.9 (n 13 against 64)
  - ran, fought, Isle of Meditation: +0.5 (n 26 against 100)
  - ran, fought, Isle of Solitude: +2.3 (n 26 against 74)
  - ran, fought, Isle of Weeping Stone: +1.1 (n 31 against 59)
  - ran, fought, Nomad's Isle: -5.6 (n 12 against 17)
  - ran, fought, Uncharted Isle: -2.9 (n 18 against 124)
  - held, held, Corrupted Isle: +0.1 (n 14 against 131)
  - held, held, Druid's Isle: -2.1 (n 38 against 42)
  - held, held, Isle of Jade: +5.9 (n 41 against 64)
  - held, held, Isle of Meditation: -3.9 (n 23 against 100)
  - held, held, Isle of Solitude: +0.8 (n 22 against 74)
  - held, held, Isle of Weeping Stone: -6.8 (n 16 against 59)
  - held, held, Nomad's Isle: +0.9 (n 16 against 17)
  - held, held, Uncharted Isle: +1.2 (n 16 against 124)
  - already running, held, Corrupted Isle: -4.6 (n 16 against 131)
  - already running, held, Druid's Isle: -3.9 (n 24 against 42)
  - already running, held, Isle of Jade: +1.9 (n 24 against 64)
  - already running, held, Isle of Meditation: -2.5 (n 19 against 100)
  - already running, held, Isle of Solitude: +0.6 (n 29 against 74)
  - already running, held, Isle of Weeping Stone: -2.5 (n 19 against 59)
  - already running, held, Uncharted Isle: +1.1 (n 39 against 124)
  - ran, held, Druid's Isle: -2.3 (n 15 against 42)
  - ran, held, Imperial Isle: -2.0 (n 10 against 20)
  - ran, held, Isle of Jade: +6.6 (n 25 against 64)
  - ran, held, Isle of Meditation: -1.4 (n 11 against 100)
  - ran, held, Isle of Solitude: +1.5 (n 19 against 74)
  - ran, held, Isle of Weeping Stone: +2.8 (n 10 against 59)
  - ran, held, Uncharted Isle: +1.6 (n 13 against 124)

**late game** (128 decisions, 64 matches; usual: 2 to 3 at the enemy Lord)
- 0 to 1 at the enemy Lord (n 48): -19.8 [-31.9, -6.0] CLEAR; in the 30 s before: +0.2 [-1.5, +2.1]
- 4+ at the enemy Lord (n 27): +5.7 [-4.6, +18.2]; in the 30 s before: +0.7 [-1.4, +2.3]

**power play** (3276 decisions, 353 matches; usual: pushed, advanced)
- pushed, fought (n 715): +0.1 [-0.7, +1.0]; in the 30 s before: +0.0 [-0.5, +0.6]
- held, fought (n 392): -1.0 [-1.9, -0.1] CLEAR; in the 30 s before: -0.7 [-1.4, -0.0] ALREADY DIFFERENT BEFORE: partly who chooses it
- pushed, fell back (n 364): -0.4 [-1.6, +0.7]; in the 30 s before: -0.3 [-1.1, +0.4]
- held, fell back (n 358): -1.3 [-2.3, -0.2] CLEAR; in the 30 s before: -0.4 [-1.2, +0.3]
- held, advanced (n 251): -1.3 [-2.4, -0.4] CLEAR; in the 30 s before: -0.3 [-1.3, +0.4]
- held, held (n 123): -1.2 [-2.6, -0.0] CLEAR; in the 30 s before: -0.1 [-1.3, +1.0]
- pushed, held (n 113): -1.4 [-2.9, +0.1]; in the 30 s before: -0.4 [-1.6, +0.5]
- pushed, to the spawn (n 7): +12.4 [-1.8, +29.5]; in the 30 s before: -3.8 [-7.8, -0.2] ALREADY DIFFERENT BEFORE: partly who chooses it
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - pushed, fought, behind in the fight (lowest third, +0.00 or less): +0.5 (n 205 against 288)
  - pushed, fought, middle third: -0.3 (n 198 against 331)
  - pushed, fought, ahead in the fight (top third, above +0.08): -0.4 (n 312 against 334)
  - held, fought, behind in the fight (lowest third, +0.00 or less): +0.2 (n 121 against 288)
  - held, fought, middle third: -0.8 (n 131 against 331)
  - held, fought, ahead in the fight (top third, above +0.08): -3.1 (n 140 against 334)
  - pushed, fell back, behind in the fight (lowest third, +0.00 or less): +0.7 (n 149 against 288)
  - pushed, fell back, middle third: -0.1 (n 109 against 331)
  - pushed, fell back, ahead in the fight (top third, above +0.08): -2.9 (n 106 against 334)
  - held, fell back, behind in the fight (lowest third, +0.00 or less): -1.2 (n 166 against 288)
  - held, fell back, middle third: -1.8 (n 125 against 331)
  - held, fell back, ahead in the fight (top third, above +0.08): -0.3 (n 67 against 334)
  - held, advanced, behind in the fight (lowest third, +0.00 or less): -0.2 (n 87 against 288)
  - held, advanced, middle third: -2.8 (n 86 against 331)
  - held, advanced, ahead in the fight (top third, above +0.08): -1.1 (n 78 against 334)
  - held, held, behind in the fight (lowest third, +0.00 or less): +0.7 (n 56 against 288)
  - held, held, middle third: -3.7 (n 47 against 331)
  - held, held, ahead in the fight (top third, above +0.08): -2.0 (n 20 against 334)
  - pushed, held, behind in the fight (lowest third, +0.00 or less): -0.5 (n 51 against 288)
  - pushed, held, middle third: -1.7 (n 38 against 331)
  - pushed, held, ahead in the fight (top third, above +0.08): -1.5 (n 24 against 334)
  - pushed, to the spawn, behind in the fight (lowest third, +0.00 or less): too few yet (n 6 against 288; means 16.9 against 0.3)
  - pushed, to the spawn, ahead in the fight (top third, above +0.08): too few yet (n 1 against 334; means 0.0 against 2.2)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - pushed, fought, Corrupted Isle: -0.2 (n 91 against 182)
  - pushed, fought, Druid's Isle: +0.5 (n 121 against 83)
  - pushed, fought, Imperial Isle: +1.1 (n 22 against 37)
  - pushed, fought, Isle of Jade: +2.3 (n 66 against 71)
  - pushed, fought, Isle of Meditation: -2.0 (n 111 against 200)
  - pushed, fought, Isle of Solitude: -1.3 (n 106 against 131)
  - pushed, fought, Isle of Weeping Stone: -0.2 (n 72 against 95)
  - pushed, fought, Nomad's Isle: +0.3 (n 46 against 17)
  - pushed, fought, Uncharted Isle: +2.3 (n 76 against 134)
  - held, fought, Corrupted Isle: +0.8 (n 40 against 182)
  - held, fought, Druid's Isle: -3.2 (n 66 against 83)
  - held, fought, Imperial Isle: -1.9 (n 18 against 37)
  - held, fought, Isle of Jade: -2.9 (n 42 against 71)
  - held, fought, Isle of Meditation: -2.4 (n 71 against 200)
  - held, fought, Isle of Solitude: -1.3 (n 49 against 131)
  - held, fought, Isle of Weeping Stone: +0.2 (n 32 against 95)
  - held, fought, Nomad's Isle: +1.9 (n 40 against 17)
  - held, fought, Uncharted Isle: -1.0 (n 34 against 134)
  - pushed, fell back, Corrupted Isle: -0.7 (n 68 against 182)
  - pushed, fell back, Druid's Isle: -3.2 (n 21 against 83)
  - pushed, fell back, Imperial Isle: -6.4 (n 11 against 37)
  - pushed, fell back, Isle of Jade: -0.5 (n 23 against 71)
  - pushed, fell back, Isle of Meditation: -0.9 (n 57 against 200)
  - pushed, fell back, Isle of Solitude: +1.4 (n 70 against 131)
  - pushed, fell back, Isle of Weeping Stone: -2.6 (n 36 against 95)
  - pushed, fell back, Nomad's Isle: +0.2 (n 18 against 17)
  - pushed, fell back, Uncharted Isle: +0.9 (n 55 against 134)
  - held, fell back, Corrupted Isle: -0.3 (n 51 against 182)
  - held, fell back, Druid's Isle: -1.1 (n 33 against 83)
  - held, fell back, Imperial Isle: -5.1 (n 14 against 37)
  - held, fell back, Isle of Jade: -1.1 (n 22 against 71)
  - held, fell back, Isle of Meditation: -1.7 (n 69 against 200)
  - held, fell back, Isle of Solitude: -2.4 (n 66 against 131)
  - held, fell back, Isle of Weeping Stone: -2.8 (n 36 against 95)
  - held, fell back, Nomad's Isle: +0.5 (n 18 against 17)
  - held, fell back, Uncharted Isle: -0.3 (n 49 against 134)
  - held, advanced, Corrupted Isle: -0.2 (n 39 against 182)
  - held, advanced, Druid's Isle: -1.2 (n 20 against 83)
  - held, advanced, Imperial Isle: -2.1 (n 17 against 37)
  - held, advanced, Isle of Jade: -3.7 (n 24 against 71)
  - held, advanced, Isle of Meditation: -1.0 (n 51 against 200)
  - held, advanced, Isle of Solitude: -2.5 (n 34 against 131)
  - held, advanced, Isle of Weeping Stone: -1.8 (n 27 against 95)
  - held, advanced, Uncharted Isle: -2.4 (n 33 against 134)
  - held, held, Druid's Isle: -2.6 (n 36 against 83)
  - held, held, Isle of Meditation: -3.3 (n 13 against 200)
  - held, held, Isle of Solitude: -1.1 (n 19 against 131)
  - held, held, Isle of Weeping Stone: -1.4 (n 14 against 95)
  - held, held, Nomad's Isle: +3.1 (n 11 against 17)
  - held, held, Uncharted Isle: +0.5 (n 13 against 134)
  - pushed, held, Corrupted Isle: -5.7 (n 10 against 182)
  - pushed, held, Druid's Isle: -4.3 (n 16 against 83)
  - pushed, held, Isle of Jade: +0.5 (n 10 against 71)
  - pushed, held, Isle of Meditation: -0.8 (n 16 against 200)
  - pushed, held, Isle of Solitude: -1.1 (n 22 against 131)
  - pushed, held, Isle of Weeping Stone: -2.4 (n 19 against 95)
  - pushed, held, Uncharted Isle: +2.5 (n 13 against 134)

**runner choice** (3097 decisions, 319 matches; usual: monk)
- mesmer (n 614): +0.9 [-0.1, +2.0]; in the 30 s before: +0.7 [-0.1, +1.5]
- dervish (n 541): +0.3 [-1.0, +1.6]; in the 30 s before: -0.0 [-1.0, +0.8]
- warrior (n 404): -0.9 [-2.2, +0.4]; in the 30 s before: +0.9 [+0.0, +1.6] ALREADY DIFFERENT BEFORE: partly who chooses it
- ritualist (n 365): +1.2 [+0.0, +2.6] CLEAR; in the 30 s before: -0.2 [-1.1, +0.5]
- elementalist (n 219): +0.9 [-0.5, +2.4]; in the 30 s before: +0.4 [-0.6, +1.4]
- necromancer (n 129): +0.8 [-1.1, +2.6]; in the 30 s before: -1.3 [-2.6, -0.2] ALREADY DIFFERENT BEFORE: partly who chooses it
- ranger (n 66): +1.7 [-0.5, +4.8]; in the 30 s before: +1.6 [+0.2, +3.0] ALREADY DIFFERENT BEFORE: partly who chooses it
- paragon (n 20): +1.3 [-3.0, +6.7]; in the 30 s before: +1.5 [-1.4, +4.6]
- assassin (n 12): -0.7 [-6.2, +7.0]; in the 30 s before: +1.7 [-1.3, +5.1]
  By snare matchup (movepower.py: enemy snare power of the live players minus own speed power; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - mesmer, little enemy snare for own speed (lowest third, -37 or less): +0.3 (n 231 against 223)
  - mesmer, middle third: -0.0 (n 152 against 288)
  - mesmer, a lot of enemy snare for own speed (top third, above -6): +1.0 (n 231 against 216)
  - dervish, little enemy snare for own speed (lowest third, -37 or less): +0.5 (n 156 against 223)
  - dervish, middle third: +1.3 (n 176 against 288)
  - dervish, a lot of enemy snare for own speed (top third, above -6): -0.4 (n 209 against 216)
  - warrior, little enemy snare for own speed (lowest third, -37 or less): -1.1 (n 143 against 223)
  - warrior, middle third: -0.2 (n 149 against 288)
  - warrior, a lot of enemy snare for own speed (top third, above -6): -1.0 (n 112 against 216)
  - ritualist, little enemy snare for own speed (lowest third, -37 or less): -1.0 (n 128 against 223)
  - ritualist, middle third: +1.7 (n 134 against 288)
  - ritualist, a lot of enemy snare for own speed (top third, above -6): +2.8 (n 103 against 216)
  - elementalist, little enemy snare for own speed (lowest third, -37 or less): -2.0 (n 55 against 223)
  - elementalist, middle third: +2.1 (n 82 against 288)
  - elementalist, a lot of enemy snare for own speed (top third, above -6): +1.1 (n 82 against 216)
  - necromancer, little enemy snare for own speed (lowest third, -37 or less): -0.6 (n 61 against 223)
  - necromancer, middle third: +3.0 (n 28 against 288)
  - necromancer, a lot of enemy snare for own speed (top third, above -6): +1.5 (n 40 against 216)
  - ranger, little enemy snare for own speed (lowest third, -37 or less): +0.9 (n 30 against 223)
  - ranger, middle third: +0.9 (n 17 against 288)
  - ranger, a lot of enemy snare for own speed (top third, above -6): +1.3 (n 19 against 216)
  - paragon, little enemy snare for own speed (lowest third, -37 or less): too few yet (n 9 against 223; means -0.3 against 0.2)
  - paragon, middle third: too few yet (n 6 against 288; means 8.7 against -0.3)
  - paragon, a lot of enemy snare for own speed (top third, above -6): too few yet (n 5 against 216; means -3.4 against -0.1)
  - assassin, little enemy snare for own speed (lowest third, -37 or less): too few yet (n 3 against 223; means -10.7 against 0.2)
  - assassin, middle third: too few yet (n 5 against 288; means 5.4 against -0.3)
  - assassin, a lot of enemy snare for own speed (top third, above -6): too few yet (n 4 against 216; means 0.8 against -0.1)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - mesmer, Corrupted Isle: -0.1 (n 103 against 166)
  - mesmer, Druid's Isle: -0.7 (n 23 against 138)
  - mesmer, Imperial Isle: +0.1 (n 55 against 15)
  - mesmer, Isle of Jade: -0.4 (n 29 against 64)
  - mesmer, Isle of Meditation: +1.9 (n 88 against 89)
  - mesmer, Isle of Solitude: +0.9 (n 90 against 88)
  - mesmer, Isle of Weeping Stone: +1.8 (n 86 against 91)
  - mesmer, Nomad's Isle: -0.5 (n 18 against 17)
  - mesmer, Uncharted Isle: +3.0 (n 122 against 59)
  - dervish, Corrupted Isle: -0.2 (n 66 against 166)
  - dervish, Druid's Isle: -2.2 (n 28 against 138)
  - dervish, Imperial Isle: +2.4 (n 29 against 15)
  - dervish, Isle of Jade: -6.7 (n 11 against 64)
  - dervish, Isle of Meditation: +0.2 (n 99 against 89)
  - dervish, Isle of Solitude: +1.3 (n 128 against 88)
  - dervish, Isle of Weeping Stone: +2.5 (n 76 against 91)
  - dervish, Uncharted Isle: +2.7 (n 97 against 59)
  - warrior, Corrupted Isle: -1.3 (n 77 against 166)
  - warrior, Druid's Isle: -4.2 (n 32 against 138)
  - warrior, Imperial Isle: -0.7 (n 29 against 15)
  - warrior, Isle of Jade: +0.6 (n 29 against 64)
  - warrior, Isle of Meditation: -0.6 (n 54 against 89)
  - warrior, Isle of Solitude: -0.7 (n 52 against 88)
  - warrior, Isle of Weeping Stone: +0.6 (n 62 against 91)
  - warrior, Uncharted Isle: +2.5 (n 64 against 59)
  - ritualist, Corrupted Isle: -0.7 (n 39 against 166)
  - ritualist, Druid's Isle: -0.3 (n 20 against 138)
  - ritualist, Isle of Jade: -1.1 (n 19 against 64)
  - ritualist, Isle of Meditation: +1.0 (n 100 against 89)
  - ritualist, Isle of Solitude: +2.9 (n 56 against 88)
  - ritualist, Isle of Weeping Stone: +1.0 (n 58 against 91)
  - ritualist, Uncharted Isle: +6.5 (n 68 against 59)
  - elementalist, Corrupted Isle: +0.5 (n 48 against 166)
  - elementalist, Druid's Isle: -1.8 (n 24 against 138)
  - elementalist, Imperial Isle: +2.9 (n 29 against 15)
  - elementalist, Isle of Jade: +2.3 (n 24 against 64)
  - elementalist, Isle of Meditation: +1.3 (n 34 against 89)
  - elementalist, Isle of Solitude: -2.1 (n 19 against 88)
  - elementalist, Isle of Weeping Stone: +3.3 (n 22 against 91)
  - elementalist, Uncharted Isle: +0.6 (n 12 against 59)
  - necromancer, Druid's Isle: -0.0 (n 19 against 138)
  - necromancer, Isle of Meditation: +2.4 (n 26 against 89)
  - necromancer, Isle of Solitude: -0.1 (n 20 against 88)
  - necromancer, Isle of Weeping Stone: +5.6 (n 12 against 91)
  - necromancer, Uncharted Isle: +1.9 (n 34 against 59)
  - ranger, Corrupted Isle: +4.2 (n 12 against 166)
  - ranger, Isle of Meditation: +0.8 (n 19 against 89)
  - ranger, Uncharted Isle: +4.1 (n 11 against 59)

**split in base** (702 decisions, 226 matches; usual: defended without a collapse)
- collapsed (n 297): -1.6 [-3.5, +0.1]; in the 30 s before: +1.1 [-0.0, +2.2]
- missed (n 75): -2.4 [-6.8, +0.4]; in the 30 s before: +2.5 [+1.1, +4.4] ALREADY DIFFERENT BEFORE: partly who chooses it
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - collapsed, Corrupted Isle: -1.5 (n 47 against 55)
  - collapsed, Druid's Isle: -2.7 (n 22 against 12)
  - collapsed, Isle of Meditation: -0.1 (n 57 against 34)
  - collapsed, Isle of Solitude: +0.6 (n 61 against 92)
  - collapsed, Isle of Weeping Stone: +0.1 (n 19 against 39)
  - collapsed, Uncharted Isle: -2.3 (n 44 against 85)
  - missed, Corrupted Isle: -1.0 (n 12 against 55)
  - missed, Isle of Solitude: -1.7 (n 26 against 92)
  - missed, Uncharted Isle: -5.4 (n 13 against 85)

**split or stay** (12924 decisions, 356 matches; usual: stayed)
- split (n 1255): -0.6 [-1.1, +0.1]; in the 30 s before: +0.3 [-0.0, +0.7]
  By snare matchup (movepower.py: enemy snare power of the live players minus own speed power; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - split, little enemy snare for own speed (lowest third, -34 or less): -1.0 (n 473 against 3907)
  - split, middle third: +0.3 (n 379 against 3860)
  - split, a lot of enemy snare for own speed (top third, above -6): -1.2 (n 403 against 3902)
  By map (raw win-chance change against the usual choice on the same map; maps with 10+ cases of both):
  - split, Corrupted Isle: -3.8 (n 200 against 1649)
  - split, Druid's Isle: +1.3 (n 82 against 1581)
  - split, Imperial Isle: -1.3 (n 43 against 439)
  - split, Isle of Jade: -0.4 (n 73 against 1530)
  - split, Isle of Meditation: +0.5 (n 231 against 1960)
  - split, Isle of Solitude: -0.3 (n 226 against 1589)
  - split, Isle of Weeping Stone: +0.4 (n 119 against 1114)
  - split, Nomad's Isle: -0.0 (n 53 against 445)
  - split, Uncharted Isle: -1.2 (n 226 against 1302)

**Collapses on a split: time away and its cost** (`S32`; per collapse, averages; main = what the main fight lost while the collapsers were away)

| Group | Cases | Away (median s) | Split killed | Collapser died | Own deaths at main | Enemy deaths at main | Flag lead change | DP change | Win change |
|---|---|---|---|---|---|---|---|---|---|
| all | 320 | 22 | 89 | 27 | 0.64 | 0.57 | -0.3 | -4.1 | -1.8 |
| away under 30 s | 180 | 6 | 50 | 1 | 0.07 | 0.15 | -0.3 | -0.2 | -2.1 |
| away 30 to 60 s | 48 | 43 | 12 | 8 | 1 | 0.5 | -10.2 | -11.5 | +0.9 |
| away 60 s or more | 92 | 100.5 | 27 | 18 | 1.55 | 1.41 | +4.8 | -8.1 | -2.5 |
| before 20:00 | 268 | 23.5 | 73 | 21 | 0.58 | 0.56 | -0.3 | -4.9 | -1.5 |
| from 20:00 | 52 | 19 | 16 | 6 | 0.94 | 0.6 | -0.2 | -0.0 | -2.9 |
| split member killed | 89 | 24 | 89 | 3 | 0.31 | 1.24 | -1.2 | -0.1 | +2.4 |
| no kill | 231 | 22 | 0 | 24 | 0.76 | 0.31 | +0.0 | -5.7 | -3.4 |

**Leverage: where the choice matters most** (share of the spread in win-chance change explained by the choice beyond the situation; range = best minus worst choice, in points)

- late game (128): choice explains 7.4% (situation 4.3%); range 25.4 points, best 4+ at the enemy Lord, worst 0 to 1 at the enemy Lord
- boost clock (1322): choice explains 3.3% (situation 1.7%); range 6.3 points, best running, fell back, worst not running, to the spawn
- after wipe (821): choice explains 0.7% (situation 4.5%); range 2.6 points, best pushed the pit, worst reset
- enemy pickup (4443): choice explains 0.7% (situation 2.5%); range 12.1 points, best ran, fell back, worst held
- power play (3276): choice explains 0.7% (situation 1.8%); range 14.2 points, best pushed, to the spawn, worst held, advanced
- split in base (702): choice explains 0.4% (situation 3.3%); range 2.1 points, best defended without a collapse, worst missed
- runner choice (3097): choice explains 0.3% (situation 3.0%); range 2.4 points, best paragon, worst warrior
- split or stay (12924): choice explains 0.0% (situation 2.7%); range 0.5 points, best stayed, worst split

**Behaviour clusters: what teams actually did** (each decision's response grouped by what every player did in the next 20 s; UNNAMED = a group no single named choice covers: a response for Denning to name or reject)

*after wipe* (2 groups, separation 0.31):
- n 488: fought (midline, 1.9 of 8), fought (backline, 1.5 of 8), fought (frontline, 0.9 of 8), held (backline, 0.8 of 8); named as {'pushed the pit': 407, 'reset': 47, 'took the flag': 34}; win change -1.1
- n 333: advanced (backline, 2.5 of 8), advanced (midline, 2.5 of 8), advanced (frontline, 1.2 of 8); named as {'pushed the pit': 196, 'reset': 75, 'took the flag': 62}; win change 0.5 UNNAMED
*boost clock* (4 groups, separation 0.18):
- n 499: fought (midline, 2.3 of 8), fought (backline, 2.2 of 8), fought (frontline, 0.9 of 8), held (backline, 0.5 of 8); named as {'not running, fought': 188, 'running, fought': 93, 'not running, fell back': 47}; win change 0.1 UNNAMED
- n 343: held (backline, 1.3 of 8), fought (midline, 0.9 of 8), fought (frontline, 0.6 of 8), to the spawn (backline, 0.6 of 8); named as {'not running, fought': 66, 'not running, fell back': 63, 'not running, held': 58}; win change -1.0 UNNAMED
- n 263: advanced (midline, 2.1 of 8), advanced (backline, 2.0 of 8), advanced (frontline, 0.8 of 8); named as {'running, advanced': 98, 'not running, advanced': 83, 'running, fought': 19}; win change 0.6 UNNAMED
- n 219: fell back (midline, 1.8 of 8), fell back (backline, 1.8 of 8), fell back (frontline, 0.7 of 8); named as {'not running, fell back': 86, 'running, fell back': 38, 'not running, advanced': 23}; win change -1.2 UNNAMED
*enemy pickup* (3 groups, separation 0.22):
- n 2040: fought (midline, 1.9 of 8), fought (backline, 1.7 of 8), fought (frontline, 1.0 of 8), held (backline, 0.9 of 8); named as {'held, fought': 354, 'already running, fought': 298, 'held, advanced': 225}; win change -0.6 UNNAMED
- n 1255: advanced (backline, 2.0 of 8), advanced (midline, 1.9 of 8), advanced (frontline, 0.9 of 8); named as {'already running, advanced': 359, 'held, advanced': 339, 'ran, advanced': 152}; win change 0.7 UNNAMED
- n 1146: fell back (backline, 1.9 of 8), fell back (midline, 1.7 of 8), fell back (frontline, 0.7 of 8); named as {'held, fell back': 347, 'already running, fell back': 229, 'ran, fell back': 192}; win change 0.1 UNNAMED
*late game* (4 groups, separation 0.2):
- n 44: fought (midline, 2.1 of 8), fought (backline, 1.8 of 8), fought (frontline, 1.0 of 8), held (backline, 0.7 of 8); named as {'2 to 3 at the enemy Lord': 16, '4+ at the enemy Lord': 15, '0 to 1 at the enemy Lord': 13}; win change -0.1 UNNAMED
- n 39: advanced (backline, 1.9 of 8), advanced (midline, 1.7 of 8), advanced (frontline, 1.0 of 8); named as {'2 to 3 at the enemy Lord': 20, '0 to 1 at the enemy Lord': 11, '4+ at the enemy Lord': 8}; win change 8.1 UNNAMED
- n 36: fell back (backline, 1.7 of 8), fell back (midline, 1.4 of 8), fell back (frontline, 1.0 of 8), held (backline, 0.9 of 8); named as {'0 to 1 at the enemy Lord': 17, '2 to 3 at the enemy Lord': 15, '4+ at the enemy Lord': 4}; win change -7.5 UNNAMED
- n 7: died (backline, 2.8 of 8), died (midline, 1.8 of 8), died (frontline, 1.3 of 8), fell back (backline, 0.6 of 8); named as {'0 to 1 at the enemy Lord': 5, '2 to 3 at the enemy Lord': 2}; win change -6.8
*power play* (2 groups, separation 0.27):
- n 2212: fought (midline, 1.8 of 8), fought (backline, 1.6 of 8), fought (frontline, 1.0 of 8), held (backline, 0.7 of 8); named as {'pushed, fought': 568, 'held, fought': 372, 'held, fell back': 333}; win change 0.1 UNNAMED
- n 1065: advanced (backline, 2.3 of 8), advanced (midline, 2.1 of 8), advanced (frontline, 1.1 of 8); named as {'pushed, advanced': 672, 'pushed, fought': 147, 'pushed, fell back': 80}; win change 1.5
*runner choice* (3 groups, separation 0.22):
- n 1265: fought (backline, 1.9 of 8), fought (midline, 1.8 of 8), fought (frontline, 1.0 of 8), held (backline, 0.7 of 8); named as {'monk': 323, 'mesmer': 231, 'dervish': 222}; win change 0.9 UNNAMED
- n 974: fell back (backline, 1.5 of 8), fell back (midline, 1.3 of 8), held (backline, 0.7 of 8), fell back (frontline, 0.6 of 8); named as {'mesmer': 204, 'dervish': 183, 'monk': 171}; win change 0.3 UNNAMED
- n 858: advanced (backline, 2.2 of 8), advanced (midline, 1.7 of 8), advanced (frontline, 0.8 of 8), carrying (midline, 0.5 of 8); named as {'monk': 233, 'mesmer': 179, 'dervish': 136}; win change -0.6 UNNAMED
*split in base* (3 groups, separation 0.17):
- n 332: fought (midline, 1.9 of 8), fought (backline, 1.3 of 8), fought (frontline, 0.9 of 8), held (backline, 0.7 of 8); named as {'defended without a collapse': 171, 'collapsed': 119, 'missed': 42}; win change -0.7 UNNAMED
- n 200: fell back (backline, 1.9 of 8), fell back (midline, 1.8 of 8), fell back (frontline, 0.8 of 8); named as {'collapsed': 103, 'defended without a collapse': 81, 'missed': 16}; win change -1.8 UNNAMED
- n 165: advanced (midline, 2.0 of 8), advanced (backline, 1.9 of 8), advanced (frontline, 0.9 of 8), fought (midline, 0.5 of 8); named as {'defended without a collapse': 75, 'collapsed': 73, 'missed': 17}; win change -1.9 UNNAMED
*split or stay* (3 groups, separation 0.25):
- n 6373: fought (midline, 2.2 of 8), fought (backline, 2.0 of 8), fought (frontline, 1.1 of 8), held (backline, 0.8 of 8); named as {'stayed': 5884, 'split': 489}; win change 0.0
- n 3540: fell back (backline, 1.6 of 8), fell back (midline, 1.4 of 8), fell back (frontline, 0.7 of 8), held (backline, 0.6 of 8); named as {'stayed': 3192, 'split': 348}; win change -0.5
- n 3011: advanced (backline, 2.1 of 8), advanced (midline, 2.0 of 8), advanced (frontline, 1.0 of 8); named as {'stayed': 2593, 'split': 418}; win change 0.0

## 8. What results and causes are worth

Win points for the team it happened to, from 356 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. Both against matched moments without the event (same minute and win chance). A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 1011 | +5.2 | +2.7 to +7.6 | +2.0 | yes |
| capture | 3247 | +2.5 | +2.2 to +2.9 | +3.3 | yes |
| capture: held longer | 2800 | +3.3 | +2.4 to +4.2 | +3.6 | yes |
| capture: overcapped within 10 s (Bounty, F36) | 447 | -2.4 | -7.9 to +3.1 | +1.1 | no |
| death (any) | 7194 | -7.9 | -8.8 to -7.0 | -4.8 | yes |
| death: against a spike build | 2089 | -8.1 | -11.1 to -5.2 | -4.7 | yes |
| death: against other builds | 5105 | -7.8 | -9.0 to -6.8 | -4.8 | yes |
| death: back within 20 s | 1203 | -7.2 | -9.0 to -5.5 | -2.5 | yes |
| death: down 20 to 60 s | 2552 | -6.9 | -8.4 to -5.6 | -4.3 | yes |
| death: down 60 s or more | 3439 | -8.9 | -10.2 to -7.6 | -5.9 | yes |
| death: healer | 2428 | -7.5 | -8.7 to -6.2 | -4.7 | yes |
| death: healer in own base or pit, back within 15 s (possibly deliberate; energy not tracked) | 153 | -3.4 | -5.1 to -1.4 | -1.6 | yes |
| death: healer, other | 2275 | -7.8 | -9.0 to -6.5 | -4.9 | yes |
| death: not a healer | 4766 | -8.1 | -9.2 to -7.0 | -4.8 | yes |
| footman lost (base NPC) | 998 | +1.3 | -0.2 to +2.8 | +4.6 | no |
| pit NPC lost (any): taken by a spike build | 619 | -3.8 | -7.6 to +0.1 | -2.3 | no |
| pit NPC lost (any): taken by other builds | 2243 | -4.7 | -6.0 to -3.3 | -2.2 | yes |
| pit NPC lost: archer | 1624 | -3.3 | -4.4 to -2.3 | -0.6 | yes |
| pit NPC lost: bodyguard | 379 | -4.8 | -5.8 to -3.7 | -2.2 | yes |
| pit NPC lost: knight | 859 | -6.5 | -7.7 to -5.4 | -5.4 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value. Context (strength, build skill counts, flag lead, morale, the clock) is left out: it describes the situation, it is not a cause to fix.

*deaths* (per 10 s in that state; result worth -7.9 points, base rate 1.5%):

- enemies within 1,500 7.5 to 8: result chance +2.9 points, worth -0.23 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.7 points, worth -0.21 win points
- allies within 1,500 0 to 0.5: result chance +2.2 points, worth -0.17 win points
- current health % 1 to 49.5: result chance +9.9 points, worth -0.78 win points
- a prot (Guardian, Spirit Bond, Life Sheath, Protective Spirit...) on the player now 0.5 to 1: result chance -0.4 points, worth +0.03 win points
- distance from its own pit 13260.5 to 18468: result chance +0.7 points, worth -0.06 win points

*kill conversion* (per burst, for the attacking team; result worth +7.9 points, base rate 28.7%):

- target's health ceiling 0.4 to 0.56: result chance +43.9 points, worth +3.47 win points
- damage in the 2 s burst 508.5 to 1069: result chance +27.6 points, worth +2.18 win points
- target's healers in range 0 to 0.5: result chance +34.3 points, worth +2.71 win points
- target health % when the burst started 0 to 37.5: result chance +34.0 points, worth +2.69 win points
- a prot on the target 0.5 to 1: result chance -7.8 points, worth -0.62 win points

*npc loss* (per case, for the defending team; result worth -4.5 points, base rate 20.8%):

- own players in the pit 0 to 0.5: result chance +37.7 points, worth -1.68 win points
- damage on the pit NPCs in the last 5 s 386.5 to 1370: result chance +35.6 points, worth -1.59 win points
- own players alive outside the pit 0 to 0.5: result chance +17.8 points, worth -0.79 win points
- attackers' measured damage per second against a Lord (benchmarks) 2.7 to 21.1: result chance -12.2 points, worth +0.54 win points
- of which healers 0 to 0.5: result chance +18.2 points, worth -0.81 win points
- enemy players in the pit 1 to 1.5: result chance -4.7 points, worth +0.21 win points
- healing on own pit NPCs and Lord in the last 10 s 621.5 to 2034: result chance -7.4 points, worth +0.33 win points

## The TQs

Denning's four questions, each from the batch's matches. The why comes from forensics and events (every number placed against the same role or situation in every stored match); the different play comes only from measurement: the usual play's choice effects (usual.py), node models read again with the variable changed (models that never saw the match, changes priced in win points with values.py), options that were ready and unused, and benchmarks. Points = win-chance points.

## TQ 1. Behind on flags

*The biggest flag swing in the new matches: DUM +35 -> -128 by 2:30.0.*

### Flag swing: DUM v chic (427f6a9f), 1:00.0 to 2:30.0
**Result**: DUM's flag lead +35 s -> -128 s (-163 s). Stand: DUM -> DUM.
**Captures** (flag model: fastest possible answer after the enemy's capture):
- DUM capped 0:57.0 by Assassin 1, 6 s after chic's capture; fastest possible 4 s, so 2 s slower
- chic capped 2:31.0 by Ritualist, 94 s after DUM's capture; fastest possible 32 s, so 62 s slower; enemies in the way {'Assassin 2': 12, 'Warrior': 8, 'Fire Ele': 7, 'Assassin 1': 5}
**Runs** (each run: outcome, and what was done to the runner):
- chic Ritualist 0:18.0 to 0:52.0 (34 s): captured, lowest health 89%, escort none, pushed by nobody
- DUM Assassin 1 0:20.0 to 0:57.0 (37 s): captured, lowest health 72%, escort ['Assassin 2'], pushed by ['Necromancer 1']
- chic Ritualist 1:40.0 to 2:31.0 (51 s): captured, lowest health 62%, escort none, pushed by ['Assassin 1']; control on the runner: 1:46.1 crippled by DUM Assassin 1; 1:57.6 crippled by DUM Assassin 1; 2:15.8 crippled by DUM Assassin 1; 2:27.4 crippled by DUM Assassin 1
**Deaths in the window**: 1:14.0 DUM Fire Ele (stand, [6, 8]); 1:21.0 DUM Assassin 2 (stand, [7, 8]); 1:52.0 DUM Fire Ele (backside, [7, 7]); 1:56.0 DUM Assassin 2 (backside, [4, 7]); 2:06.0 DUM Prot (backside, [5, 7]); 2:16.0 DUM Ritualist (backside, [5, 7]); 2:30.0 DUM Assassin 1 (stand, [3, 6])
- DUM output in the 20 s before 1:14.0: 62.2 damage per second (above the 80th percentile for team (median 38.6, n 21300)), top target share 0.27, spikes 0
- chic output in the 20 s before 1:14.0: 93.1 damage per second (above the 90th percentile for team (median 38.6, n 21300)), top target share 0.31, spikes 1
**Why DUM Fire Ele died at 1:14.0** (forensics):
  - Position: partly (in the last 3 s: nearest allied healer 917, nearest enemy 222, allies in casting range 4.0, enemies 8.0; over the whole window the nearest enemy's median was 263)
  - Prots: no prots (0 from teammates, 0 self; 0 of 0 landed); damage 586 (0% attacks, 90% armor-ignoring), burst 313 in 2 s at 1:12.1
  - Healers under interrupt pressure: usual (healers 3, interrupts_per_min 3.0, interrupted 1, casts 14, finished_share 0.93, dazed 0, knockdowns 0, hexes 4)
  - Damage off shield sets: no (team share 0.11, a shield would have stopped about 5)
  - Own damage: usual (60.3 per second on [('chic Water Ele', 286), ('chic 7 Monk', 278)]); enemy damage: high (91.5 per second)
  - Peel: no (peel on a burst is rare: most bursts on this role get none) (0 of 2 attackers controlled; longest free 19.3 s)
  - Casting: unclear (casts 7, interrupted 2, cancelled 0, while_dazed 0)
  - Kiting, degen, disables (in the 20 s before): kited melee 0 s, kept its distance 0 s; degen on it 22.2 pip-seconds (0 pips at death); its healers disabled 0 skill-seconds, under Shame, Guilt or Diversion 0.0 s
**Why DUM Assassin 2 died at 1:21.0** (forensics):
  - Position: yes (in the last 3 s: nearest allied healer 1010, nearest enemy 74, allies in casting range 4.0, enemies 8.0; over the whole window the nearest enemy's median was 82)
  - Prots: no prots (0 from teammates, 0 self; 0 of 0 landed); damage 530 (0% attacks, 40% armor-ignoring), burst 282 in 2 s at 1:19.2
  - Healers under interrupt pressure: usual (healers 3, interrupts_per_min 3.0, interrupted 1, casts 14, finished_share 0.86, dazed 0, knockdowns 0, hexes 5)
  - Damage off shield sets: no (team share 0.07, a shield would have stopped about 5)
  - Own damage: usual (31.4 per second on [('chic Necromancer 1', 260), ('chic Necromancer 2', 231)]); enemy damage: high (96.7 per second)
  - Peel: partly (controlled, but an attacker was left free for 17.4 s) (2 of 2 attackers controlled; longest free 17.4 s)
  - Casting: unclear (casts 5, interrupted 0, cancelled 0, while_dazed 0)
  - Kiting, degen, disables (in the 20 s before): kited melee 0 s, kept its distance 0 s; degen on it 48.0 pip-seconds (0 pips at death); its healers disabled 0 skill-seconds, under Shame, Guilt or Diversion 0.0 s
**After**: 2:43.0 DUM Assassin 2; 2:47.0 DUM Warrior; 2:52.0 DUM 7 Monk; 3:13.0 DUM Air Ele
**Why, in short**: chic capped at 2:31, 94 s after DUM's capture, on its 1st run (0 dropped); DUM pushed the last carrier with Assassin 1 but its health never went below 62%; deaths in the window: DUM 7.

**How it got there, from the node models** (step 4: each link read by the node's held-out model; the biggest pushes toward the result, against the variable's usual value over every trained moment; a variable that is another node's result is followed back to it):
- 1:20 flag swing: flag lead change over 60 s -26.4 s; pushed by flag lead now (s) 35 (usual 0): +6.9 s; own team holds the stand 1 (usual 0): +4.6 s; morale, own minus enemy (discovery, approved) -30 (usual 0): +3.5 s
*Fixes carried forward*: none worth half a win point at the result.

**A different play (measured)**

*The decisions in the swing* (usual.py: win-chance points over the decision's window, against the kind's most common choice):
- split or stay at 1:00 (main 6v8, flags +35 s, boost in 117, fight state -1.328): chose **stayed** (+0.0 [+0.0, +0.0] against the most common choice, stayed); in the 15 most similar decisions teams usually chose **stayed**; no choice of this kind did measurably better than the one made.
- split or stay at 1:30 (main 8v7, flags +35 s, boost in 87, fight state -0.046): chose **split** (-0.6 [-1.1, +0.1] against the most common choice, stayed); in the 15 most similar decisions teams usually chose **stayed**; no choice of this kind did measurably better than the one made.
- enemy pickup at 1:40 (main 7v7, flags -8 s, boost in 78, fight state -0.138): chose **held, fought** (-1.3 [-2.8, +0.3] against the most common choice, held, advanced); in the 15 most similar decisions teams usually chose **already running, advanced**; measured better: **ran, fell back** (+3.1 points against the choice made, clear, n 338). In the same fight-state third (behind in the fight (lowest third, -0.01 or less)) this choice did -1.6 against the usual choice (n 125 against 160, raw).
*The answers to the enemy's captures* (flag-answer node: seconds slower than possible; typical error 15.6 s against 27.8 s for the median on unseen matches):
- answer at 0:52 by the Assassin 1: 2 s slower than possible (model reads 4.2 s); with a runner waiting at the spawn: 0.8 s (-3.4 s)
- Those 3 s, read by the win model as flag lead at 2:30: DUM 3.4% -> 3.4% (+0.0 points)

**Confidence**: medium (one measurement supports it).

## TQ 2. A monk death

*The monk death that cost the most win chance in the new matches: chic v DMG (e906615a), DMG Prot at 9:04 (backside, numbers [6, 7]); win chance -46.3 points from 10 s before to 30 s after.*

**Why** (forensics, against the same role in every stored match):
- Position: yes (in the last 3 s: nearest allied healer 828, nearest enemy 119, allies in casting range 2.0, enemies 7.0; over the whole window the nearest enemy's median was 115)
- Prots: partly the wrong kind (1 from teammates, 3 self; 2 of 4 landed); damage 709 (54% attacks, 15% armor-ignoring), burst 323 in 2 s at 9:02.2; ready and in range but not used: DMG 8 Monk Guardian, DMG 8 Monk Shielding Hands
- Healers under interrupt pressure: usual (healers 3, interrupts_per_min 0.0, interrupted 0, casts 13, finished_share 0.85, dazed 0, knockdowns 0, hexes 2)
- Damage off shield sets: usual (team share 0.56, a shield would have stopped about 268)
- Own damage: usual (32.6 per second on [('chic 8 Monk', 408), ('chic Warrior', 164)]); enemy damage: high (108.3 per second)
- Peel: usual (1 of 5 attackers controlled; longest free 20.0 s)
- Casting: usual; cancelled more than usual (casts 4, interrupted 0, cancelled 2, while_dazed 0)
- Kiting, degen, disables (in the 20 s before): kited melee 1 s, kept its distance 0 s; degen on it 26.6 pip-seconds (7 pips at death); its healers disabled 0 skill-seconds, under Shame, Guilt or Diversion 0 s
**Why, in short**: the Prot died because the enemy hit unusually hard (108.3 per second), position (in contact with the enemy, nearest enemy 119 in the last 3 s), heavy degeneration on it (26.6 pip-seconds, 7 pips at death).

**How it got there, from the node models** (step 4: each link read by the node's held-out model; the biggest pushes toward the result, against the variable's usual value over every trained moment; a variable that is another node's result is followed back to it):
- 8:13 fight outcome: won the fight 98.6%; pushed by seconds the enemy frontline spent Blind, own minus enemy -5.70 (usual 0): +1.7 points; value-weighted seconds hexes stayed on own players, own minus enemy 3.59 (usual -0.06): +1.1 points
*Fixes carried forward*: none worth half a win point at the result.

**How it could have been prevented (measured)**

- Further back: the fixes along the chain are priced above ("Fixes, carried forward"). The readings below are what was still possible in the last seconds.
- Ready and in range but not used: DMG 8 Monk Guardian (casting nothing); DMG 8 Monk Shielding Hands (casting nothing)
- Attackers left free (no snare, Blind, Weakness, interrupt, knockdown or hex from its team): chic Fire Ele 20.0 s free (nearest own non-healer 1953); chic Paragon 20.0 s free (nearest own non-healer 773); chic Assassin 20.0 s free (nearest own non-healer 1047)
- Deaths node at 9:00 (AUC 0.927 on unseen matches against 0.79 for health_pct and damage_taken_3s alone): risk 1.2% of dying in the next 10 s; read again with
  - one attacker peeled off: 1.0% (-0.2 points of risk; at this death's measured cost of -46.3 win points, about +0.1 expected; at a typical healer death's -7.5, +0.0)
  - its hexes removed: 1.0% (-0.2 points of risk; at this death's measured cost of -46.3 win points, about +0.1 expected; at a typical healer death's -7.5, +0.0)
  - all of these together: 0.9% (-0.3 points of risk; at this death's measured cost of -46.3 win points, about +0.1 expected; at a typical healer death's -7.5, +0.0)
- The decision before it (usual.py):
  - boost clock at 8:45 (main 7v7, flags -52 s, boost in 31, fight state 0.023): chose **not running, fought** (+0.0 [+0.0, +0.0] against the most common choice, not running, fought); in the 15 most similar decisions teams usually chose **running, advanced**; measured better: **running, fell back** (+5.6 points against the choice made, clear, n 98); **running, fought** (+3.2 points against the choice made, clear, n 146).

**Confidence**: medium (one measurement supports it).

## TQ 3. A power play without a kill

*The power play without a kill that cost the most win chance in the new matches: main 8v5, held, no kill in 51 s; win chance -38.5 points over it.*

### Power play without a kill: Dz v One (604b7218), 7:14.0 to 8:05.0
**Situation**: main 8v5, alive 8v6, flags down (-52 s), DP 100, boost in 86; choice held (fought 4, fell back 3, advanced 1); deaths {'Dz': 0, 'One': 0} in 51 s
**The fight's shape** (every 5 s: own main, the enemy group it faced, distance between them, that group's distance to the rest of its team): 7:14.0 8v5 115 apart, 2323 from its others; 7:19.0 8v5 120 apart, 1771 from its others; 7:24.0 8v7 75 apart, None from its others; 7:29.0 8v7 92 apart, None from its others; 7:34.0 8v7 84 apart, None from its others; 7:39.0 8v7 100 apart, None from its others; 7:44.0 8v7 90 apart, None from its others; 7:49.0 8v7 43 apart, None from its others; 7:54.0 8v7 85 apart, None from its others; 7:59.0 8v8 94 apart, None from its others; 8:04.0 8v8 164 apart, None from its others
**Dz's damage**: 33.2 per second (below the 50th percentile for team (median 38.6, n 21300)); top target share 0.32 (below the 20th percentile for team (median 0.48, n 21300)); targets [('One Ritualist', 542), ('One Hammer', 527), ('One Warrior', 271), ('One Prot', 202)]; dealers [('Dz Mes/A', 669), ('Dz Hammer', 337), ('Dz AoB Derv', 311), ('Dz Stand Mes', 197), ('Dz Dervish', 177)]
- phase 7:07.0 to 7:18.0: 8v6 (enemy base, job convert), damage uptime 0.67, damage-seconds lost {'moving': 12, 'idle': 3, 'knocked down': 3}
- phase 7:18.0 to 7:46.0: 8v7 (enemy base, job convert), damage uptime 0.51, damage-seconds lost {'moving': 53, 'idle': 10, 'knocked down': 6}
- phase 7:46.0 to 7:59.0: 8v7 (push side, job convert), damage uptime 0.38, damage-seconds lost {'idle': 20, 'moving': 18, 'knocked down': 2}
- phase 7:59.0 to 8:36.0: 8v8 (push side, job contest), damage uptime 0.12, damage-seconds lost {'idle': 128, 'moving': 30, 'knocked down': 4}
**One's answer**: healing 91 per second ({'One 7 Monk': 1745.0000000000002, 'One 8 Monk': 1278.9, 'One Ritualist': 787.8, 'One Prot': 639}); prots {'Shielding Hands': 3, 'Guardian': 6, 'Shield Guardian PvP': 1, 'Reversal of Fortune': 2, 'Aura of Stability': 2}
- Dz's knockdowns landed 4; One's knockdown immunity casts 2
- Pressure on One's healers: healers 3, interrupts_per_min 0.0, interrupted 0, casts 29, finished_share 0.97, dazed 0, knockdowns 1, hexes 0 (around the median for team (median 0, n 23895))
- Snares, Blind and Weakness Dz put on One: none
**Where the power play came from** (why the enemy was short, player-seconds over it): dead 13, own pit 4
**Why, in short**: Dz had 8v5 at main for 51 s; One healed 91 per second; worse than in power plays that killed: damage 33.2 per second (killing 42.0, not killing 26.0); not the cause (on the side of power plays that killed): damage uptime in contact 44% (killing 49%, not killing 38%; most lost to moving), top-target share 0.32 over 4 targets (killing 0.39, not killing 0.44).

**How it got there, from the node models** (step 4: each link read by the node's held-out model; the biggest pushes toward the result, against the variable's usual value over every trained moment; a variable that is another node's result is followed back to it):
- 7:14 power play: killed on the power play 24.3%; pushed by skill-seconds disabled on the enemy per 10 s (Complicate, Power Lock, Power Block, Blackout) 2.16 (usual 0): +16.0 points; pushed (1) or held (0) 0 (usual 1): +10.3 points; time down, own minus enemy (discovery, approved) 100 (usual 0): +5.3 points
*Fixes, carried forward to the result* (the variable set to its usual value, the node read again, the change carried link by link and priced with values.py):
- skill-seconds disabled on the enemy per 10 s (Complicate, Power Lock, Power Block, Blackout) at 7:14: 2.16 -> 0; power play +13.7; worth +1.1 win points at the result
- pushed (1) or held (0) at 7:14: 0 -> 1; power play +8.3; worth +0.7 win points at the result

**How it could have been converted (measured)**

- Against every stored power play (3+ up): those that killed had a median 42.0 damage per second and top-target share 0.39 (163 cases); those that didn't, 26.0 and 0.44 (131 cases). Dz here: 33.2 and 0.32. Damage uptime: 49% in those that killed, 38% in those that didn't, 44% here.
- No burst (a 2 s burst that the kill-conversion node reads) in the window: the damage never came together on one target.
- The choice at the power play (usual.py):
  - power play at 7:14 (main 8v5, flags -52 s, boost in 86, fight state 0.011): chose **held, advanced** (-1.3 [-2.4, -0.4] CLEAR against the most common choice, pushed, advanced); in the 15 most similar decisions teams usually chose **pushed, advanced**; measured better: **pushed, to the spawn** (+13.7 points against the choice made, not clear yet, partly who chooses it, n 7). In the same fight-state third (middle third) this choice did -2.8 against the usual choice (n 86 against 331, raw).

**Confidence**: low (measured, but the ranges include no effect yet).

## TQ 4. Pit NPCs lost

*The NPC loss that cost the most win chance in the new matches: Men lost knight (NwAy split Dervish+Mes/A+8 Monk+Hammer) at 1:48; win chance -47.4 points from 20 s before to 20 s after.*

### Pit NPCs lost: Men v NwAy (c19f13e3) around 1:48.0
**Lost**: 1:48.0 knight (NwAy split Dervish+Mes/A+8 Monk+Hammer); 2:10.0 archer (NwAy split Dervish+Mes/A+8 Monk+Hammer)
**NwAy's split** 0:16.0 to 2:55.0: ['Dervish', 'Mes/A', '8 Monk', 'Hammer'] (full team collapse), entered base 0:51.0, NPC damage {'footman': 843, 'knight': 2575, 'archer': 1934}, NPC kills [{'npc': 'knight', 't': 108, 'defenders_present': ['Mes/A', '8 Monk', 'Prot']}, {'npc': 'archer', 't': 130, 'defenders_present': ['Mes/A', '8 Monk']}, {'npc': 'knight', 't': 152, 'defenders_present': ['Mes/A', '8 Monk']}]
- defender Mes/A: first 0:55.0 (latency 4 s, from field), 121 s defending
- defender 8 Monk: first 0:56.0 (latency 5 s, from field), 120 s defending
- defender Prot: first 0:59.0 (latency 8 s, from field), 85 s defending
- defender Stand Mes 1: first 2:17.0 (latency 86 s, collapse from main), 39 s defending
- defender 7 Monk: first 2:17.0 (latency 86 s, collapse from main), 39 s defending
- defender AoB Derv: first 2:18.0 (latency 87 s, collapse from main), 38 s defending
- defender Stand Mes 2: first 2:18.0 (latency 87 s, collapse from main), 36 s defending
- main numbers meanwhile [4.5, 5.0]
**Men at 1:48.0**: Hammer: enemy pit (convert); AoB Derv: enemy pit (convert); Stand Mes 1: enemy base (convert); Mes/A: own pit (defend); Stand Mes 2: push side (convert); Prot: own pit (defend); 7 Monk: push side (convert); 8 Monk: own pit (defend)
- NwAy output 0:16.0 to 1:53.0: 26.2 per second
- Men output 0:16.0 to 1:53.0: 15.7 per second
**Why, in short**: NwAy split Dervish+Mes/A+8 Monk+Hammer into Men's base at 0:51; at 1:44 the pit had 4 attackers against 3 defenders (2 of them healers), with 5 of Men elsewhere; defenders present at the kill: Mes/A, 8 Monk, Prot.

**How it got there, from the node models** (step 4: each link read by the node's held-out model; the biggest pushes toward the result, against the variable's usual value over every trained moment; a variable that is another node's result is followed back to it):
- 1:47 pit npc loss: lost a pit NPC within 15 s 38.5%; pushed by damage on the pit NPCs in the last 5 s 336 (usual 0): +46.9 points; minute 1.80 (usual 9.90): +5.0 points; pit NPCs alive (targets the defending monks must watch) 5 (usual 4): +3.5 points
*Fixes, carried forward to the result* (the variable set to its usual value, the node read again, the change carried link by link and priced with values.py):
- damage on the pit NPCs in the last 5 s at 1:47: 336 -> 0; pit npc loss -31.5; worth +1.5 win points at the result

**How it could have been prevented (measured)**

- First defender: 4 s after it entered the base; every stored split into a base: median 11 s before it entered the base, quickest fifth 34 s before it entered the base or sooner (902 splits). Denning: about 15 s is on time, 60 s is late.
- The split was answered on time, so the loss came from what the defence did once there (below), not from a late answer.
- NPC-loss node at 1:44 (AUC 0.855 on unseen matches against 0.757 for attackers and defenders alone): 4 attackers (1 healer) against 3 defenders (2 healers), 5 of Men elsewhere; read 48.8% to lose an NPC; read again with
  - one more defender [unreliable: more of the same doesn't keep moving the reading the same way; the node is reading outside its data]: 40.3% (-8.5 points; at this loss's measured cost of -47.4 win points, about +4.0 expected; at a typical NPC loss's -4.5, +0.4)
  - one more defender, a healer: 42.2% (-6.6 points; at this loss's measured cost of -47.4 win points, about +3.1 expected; at a typical NPC loss's -4.5, +0.3)
  - two more defenders [unreliable: more of the same doesn't keep moving the reading the same way; the node is reading outside its data]: 41.7% (-7.1 points; at this loss's measured cost of -47.4 win points, about +3.4 expected; at a typical NPC loss's -4.5, +0.3)
  - Readings marked unreliable or from a pairing are left out of the confidence and the fixes.

**Confidence**: low (measured, but the ranges include no effect yet).

## 9. Detailed learnings snapshot

Descriptive measurements across all 356 trained matches (the latest batch, 45 matches, in brackets where it differs). Not causal on their own: they point to questions and candidate variables.

**Runners** (spawn to capture; pushed = an enemy hit the carrier; holds = carries of 10 s+ that never closed a quarter of the way to the stand, kept out of runs and captured, Denning: an 8 Monk may hold without trying to cap):

| Runner | Runs | Holds | Captured | Median s to capture | Dropped | Pushed | Runs by eventual winners (includes who was ahead) |
|---|---|---|---|---|---|---|---|
| Ritualist | 606 | 49 | 51% | 36.0 (36) | 278 | 40% | 58% |
| Mesmer | 581 | 36 | 56% | 36.0 (35) | 235 | 42% | 49% |
| Mes/A | 476 | 44 | 57% | 37 (30.5) | 185 | 43% | 54% |
| AoB Derv | 475 | 39 | 63% | 33 (38) | 169 | 40% | 50% |
| Hammer | 460 | 27 | 51% | 28 (29.0) | 221 | 35% | 54% |
| Dervish | 413 | 16 | 67% | 29.5 (26) | 130 | 45% | 43% |
| Monk 4 (WoC) | 312 | 23 | 68% | 35.0 (37.0) | 89 | 50% | 52% |
| 8 Monk | 304 | 41 | 37% | 35 (38.0) | 187 | 21% | 61% |
| Necromancer | 249 | 12 | 73% | 35 (35.0) | 64 | 48% | 45% |
| Monk 5 (WoC) | 191 | 10 | 69% | 39 (81) | 56 | 48% | 47% |

Double running: half 1331 runs (50% by eventual winners, includes who was ahead); single 4681 runs (49% by eventual winners, includes who was ahead).
Winners against losers below are compared at moments when a win model that never saw the match gave the team 35 to 65% (so the gap is not just who was already ahead), with every moment beside it, labelled.


**Flag answers** (answering the enemy's capture): winners at even win chance: 317 answers, median 38 s, 11 s slower than possible, 86 answers 30 s+ slower; losers at even win chance: 358 answers, median 43.0 s, 13.0 s slower than possible, 111 answers 30 s+ slower; winners every moment (includes who was ahead): 1491 answers, median 38 s, 10 s slower than possible, 394 answers 30 s+ slower; losers every moment (includes who was ahead): 1404 answers, median 52.0 s, 18.0 s slower than possible, 554 answers 30 s+ slower.

**Skills: kill participation** (share of casts at an enemy who died within 5 s; 15+ casts):

- Highest: Deep Freeze 50% of 22; Punishing Shot 42% of 78; Forked Arrow 38% of 303; Dual Shot 36% of 25; Twisting Fangs 34% of 200; Falling Lotus Strike 29% of 198; Mark of Fury 29% of 17; Wounding Strike PvP 27% of 63; Shadow Shroud PvP 26% of 284; Augury of Death 25% of 488; Vapor Blade 25% of 240; Jungle Strike 24% of 127
- Lowest: Lightning Orb 0% of 35; Symbols of Inspiration 0% of 39; Images of Remorse 0% of 16; Backbreaker 0% of 15; Leviathan's Sweep 0% of 16; Melandru's Shot PvP 0% of 73; Plague Touch 0% of 18; Heavy Blow 0% of 17

**Interrupts:** skills interrupted most (whose): Healing Burst on the 7 Monk 1207; Blessed Light on the 8 Monk 770; Guardian on the Prot 715; Spirit Light Weapon on the Ritualist 688; Guardian on the 7 Monk 681; Guardian on the 8 Monk 656; Shield Guardian PvP on the Prot 517; Shield Guardian PvP on the 7 Monk 420; Lightning Strike on the Air Ele 408; Cure Hex on the 7 Monk 398. Interrupt skills landing most: Complicate 5045; Power Spike 4977; Power Leak 2119; Psychic Instability PvP 1847; Cry of Frustration 1537; Savage Shot 1336; Distracting Shot 938; Hammer Bash 863.

**Knockdowns by skill:** Coward 5322; Hammer Bash 5144; Psychic Instability PvP 2071; Lightning Surge 1854; Mind Shock PvP 1310; Bull's Strike 1277; Shove 1017; Bane Signet 965.

**Spikes survived** (400+ damage in 3 s on one player; survived = alive 8 s later): losers (every moment, includes who was ahead) 1245 of 2139 (58%); losers at even win chance 210 of 295 (71%); winners (every moment, includes who was ahead) 1021 of 1273 (80%); winners at even win chance 192 of 234 (82%). By target: Prot 63% of 395; Mesmer 76% of 358; 7 Monk 62% of 346; 8 Monk 54% of 284; Stand Mes 69% of 216; Paragon 75% of 214; Warrior 70% of 203; AoB Derv 69% of 185; Mes/A 72% of 173; Air Ele 66% of 157; Ritualist 64% of 125; Hammer 64% of 100; Necromancer 50% of 98; Dervish 65% of 98; Monk 4 (WoC) 66% of 85; Monk 5 (WoC) 83% of 76; Fire Ele 62% of 53; Ranger 62% of 52; Monk 3 (WoC) 80% of 45; Assassin 67% of 42; Water Ele 65% of 34; Monk 57% of 30; Ele 80% of 10.

**Monks** (per 2-minute phase alive 60 s+): winners at even win chance: 12.5 casts a minute, 0.47 fakes, idle 0 s while an ally was hurt, reaction 1.4 s, bursts answered 71%; losers at even win chance: 12.5 casts a minute, 0.45 fakes, idle 0.0 s while an ally was hurt, reaction 1.4 s, bursts answered 67%; winners every moment (includes who was ahead): 11.5 casts a minute, 0.49 fakes, idle 0 s while an ally was hurt, reaction 1.4 s, bursts answered 72%; losers every moment (includes who was ahead): 12.0 casts a minute, 0.51 fakes, idle 1.0 s while an ally was hurt, reaction 1.4 s, bursts answered 59%.

**Pressure beyond damage** (Denning, session 4u; per player per minute played, all trained matches; kiting counts only warriors, dervishes and assassins chasing; degen in pip-seconds, 1 pip = 2 health a second; disables in skill-seconds; baits = enemy interrupts that landed on nothing after a cancel):

| Role | Kited s | Pre-kited s | Melee s wasted chasing | Degen | Baits | Knockdowns (on casters) | Disables | Shame/Guilt/Diversion s (triggered) |
|---|---|---|---|---|---|---|---|---|
| 7 Monk | 0.83 | 0.35 | 0.0 | 0.0 | 0.052 | 0.0 (0.0) | 0.0 | 0.0 (0.0) |
| 8 Monk | 0.62 | 0.32 | 0.0 | 0.3 | 0.015 | 0.0 (0.0) | 0.0 | 0.0 (0.0) |
| Prot | 0.83 | 0.37 | 0.0 | 0.0 | 0.017 | 0.0 (0.0) | 0.0 | 0.0 (0.0) |
| Mesmer | 0.85 | 0.34 | 0.0 | 0.2 | 0.022 | 0.21 (0.18) | 8.46 | 1.04 (0.1) |
| Hammer | 1.03 | 0.27 | 4.12 | 0.0 | 0.003 | 2.02 (0.22) | 0.0 | 0.0 (0.0) |
| Ritualist | 0.42 | 0.26 | 0.0 | 60.5 | 0.029 | 0.0 (0.0) | 0.0 | 0.0 (0.0) |
| AoB Derv | 1.09 | 0.34 | 3.27 | 129.0 | 0.015 | 0.0 (0.0) | 0.0 | 0.0 (0.0) |
| Mes/A | 0.76 | 0.28 | 0.0 | 21.1 | 0.019 | 0.08 (0.07) | 4.3 | 0.17 (0.014) |
| Stand Mes | 0.78 | 0.29 | 0.0 | 5.8 | 0.019 | 0.14 (0.12) | 6.14 | 0.4 (0.025) |
| Warrior | 1.21 | 0.33 | 4.69 | 14.6 | 0.006 | 0.56 (0.04) | 0.0 | 0.0 (0.0) |
| Ranger | 0.71 | 0.26 | 0.0 | 250.1 | 0.008 | 0.01 (0.0) | 0.0 | 0.0 (0.0) |
| Air Ele | 0.53 | 0.22 | 0.0 | 0.0 | 0.022 | 1.2 (0.16) | 0.0 | 0.0 (0.0) |
| Dervish | 0.96 | 0.42 | 2.67 | 23.0 | 0.009 | 0.0 (0.0) | 0.0 | 0.0 (0.0) |
| Fire Ele | 0.53 | 0.27 | 0.0 | 90.4 | 0.027 | 0.03 (0.0) | 0.0 | 0.0 (0.0) |
| Monk 4 (WoC) | 0.73 | 0.31 | 0.0 | 0.7 | 0.045 | 0.22 (0.03) | 0.0 | 0.0 (0.0) |
| Necromancer | 0.6 | 0.36 | 0.0 | 119.1 | 0.019 | 0.0 (0.0) | 0.0 | 0.0 (0.0) |
| Monk 5 (WoC) | 0.61 | 0.27 | 0.0 | 1.2 | 0.026 | 0.19 (0.02) | 0.01 | 0.0 (0.0) |
| Monk 3 (WoC) | 0.65 | 0.19 | 0.0 | 0.0 | 0.036 | 0.17 (0.03) | 0.03 | 0.0 (0.0) |
| Water Ele | 0.46 | 0.16 | 0.0 | 10.0 | 0.037 | 0.0 (0.0) | 0.0 | 0.0 (0.0) |
| Paragon | 0.93 | 0.2 | 0.0 | 17.7 | 0.008 | 0.0 (0.0) | 0.0 | 0.0 (0.0) |
| Paragon 1 | 0.88 | 0.11 | 0.0 | 0.0 | 0.013 | 0.0 (0.0) | 0.0 | 0.0 (0.0) |
| Paragon 2 | 0.88 | 0.1 | 0.0 | 0.0 | 0.018 | 0.0 (0.0) | 0.0 | 0.0 (0.0) |

**Deaths** (6367): 2046 with a knockdown on the victim; 2016 had a monk cast on the victim in the last 5 s. Monk skills interrupted in the 6 s before a death: Blessed Light 286; Healing Burst 263; Guardian 221; Shield Guardian PvP 120; Reversal of Fortune 64; Cure Hex 61; Word of Healing 54; Patient Spirit 53.

## 10. For Denning

- Which curves look wrong to you? A correction (direction, cap, drop, or a pair to always test) is logged with your reason and tested on held-out matches.
- Do any surprises remind you of something the variables don't capture (a missing variable)?
- Any variable you think matters that isn't listed?

