# Learning report, batch 1

Trained on 30 matches (6 new in this batch). Variables in use: 17; build variables from 60 matches, interactions from 40.

## 1. The honest test

**Beats strength alone.** Held-out accuracy (matches held out whole), log loss in brackets (lower is better):

- strength only: all 64% (0.633), 0-5 min 74% (0.519), 5-10 min 69% (0.611), 10-15 min 60% (0.728), 15-end min 51% (0.726)
- glass box: all 79% (0.562), 0-5 min 84% (0.466), 5-10 min 86% (0.36), 10-15 min 82% (0.58), 15-end min 64% (0.859)
- black box: all 76% (0.791), 0-5 min 78% (0.743), 5-10 min 76% (0.75), 10-15 min 76% (0.715), 15-end min 74% (0.943)
- Change since batch 0: glass box log loss 0.636 -> 0.562; strength only 0.534 -> 0.633.

## 2. What it leans on

- **morale_diff** 1.951 (was 1.648): own minus enemy morale summed over players (boosts +, death penalty -)
- **knights_diff** 1.266 (was 1.26): own minus enemy pit knights alive
- **bodyguard_diff** 1.218 (was 0.898): own minus enemy Bodyguard alive
- **flag_lead** 0.342 (was 0.321): seconds up (+) or down (-) on flags: enemy's response minus own on the next capture exchange
- **lord_damage_diff** 0.304 (was 0.292): own minus enemy Lord damage dealt so far (the 28:00 tiebreak; players can't see it)
- **stand** 0.294 (was 0.206): who holds the flag stand: 1 own, 0 nobody, -1 enemy
- **pit_pressure_diff** 0.238 (was 0.199): own players in the enemy pit minus enemy players in the own pit
- **archers_diff** 0.199 (was 0.157): own minus enemy pit archers alive
- **down_diff_s** 0.147 (was 0.103): enemy minus own seconds until all dead players are back (+ = the enemy has more time down)
- **boost_clock** 0.142 (was 0.105): seconds until the stand holder's next boost (+ if own boost is coming, - if the enemy's, 0 nobody)
- **alive_diff** 0.102 (was 0.069): own minus enemy players alive
- **main_diff** 0.102 (was 0.104): own minus enemy players in each team's main group

## 3. The curves in words

Points = win-chance points added to an otherwise even game at each range of the variable.

- **morale_diff** rises from -48.3 to +48.0 points (-470.0..-199.0: -48.3; -159.0..-110.5: -45.6; -86.0..-46.5: -39.6; -15.5..-1.0: -4.8; 1.0..23.0: +3.3; 56.0..97.0: +41.3; 144.0..196.0: +47.7)
- **knights_diff** falls from +41.5 to -41.2 points (-2.0..-1.5: +41.5; -1.5..-0.5: +38.5; -0.5..0.5: -0.8; 0.5..1.5: -37.9; 1.5..2.0: -41.2)
- **bodyguard_diff** falls from +36.3 to -36.0 points (-1.0..-0.5: +36.3; -0.5..0.5: -0.6; 0.5..1.0: -36.0)
- **flag_lead** rises from -9.7 to +10.8 points (-81.0..-64.5: -9.7; -54.5..-36.5: -9.3; -27.5..-17.5: -8.1; -8.5..-0.5: -6.3; 6.5..16.5: +7.3; 27.5..36.5: +9.4; 54.5..64.5: +10.2)
- **lord_damage_diff** falls from +49.1 to -49.0 points (-9661.0..-5219.0: +49.1; -3355.0..-2101.5: -13.8; -1317.5..-530.5: -22.0; -102.0..-8.5: -27.0; 8.5..102.0: +24.5; 688.5..1338.0: +20.8; 3001.0..4965.0: -1.4)
- **stand** rises from -7.8 to +7.7 points (-1.0..-0.5: -7.8; -0.5..0.5: +0.3; 0.5..1.0: +7.7)
- **pit_pressure_diff** falls from -0.7 to -14.1 points (-8.0..-5.5: -0.7; -4.5..-3.5: +12.5; -2.5..-1.5: +13.5; -0.5..0.5: +1.7; 1.5..2.5: -18.8; 3.5..5.5: -16.0)
- **archers_diff** rises from -20.1 to +24.4 points (-4.0..-3.5: -20.1; -3.5..-2.5: -17.9; -2.5..-1.5: +3.7; -1.5..-0.5: +6.4; -0.5..0.5: -0.8; 0.5..1.5: -6.6; 1.5..2.5: -2.9; 2.5..3.5: +23.0; 3.5..4.0: +24.4)
- **down_diff_s** rises from -21.2 to +30.2 points (-960.0..-195.0: -21.2; -127.5..-97.5: -15.6; -67.5..-52.5: -9.5; -37.5..-7.5: -3.9; 7.5..37.5: +3.6; 67.5..97.5: +8.3; 127.5..195.0: +14.5)
- **boost_clock** falls from +6.4 to -4.1 points (-120.0..-109.5: +6.4; -98.5..-85.5: +6.6; -71.5..-54.5: +1.1; -32.5..-0.5: -2.6; 9.5..43.5: +0.1; 64.5..81.5: -3.9; 95.5..108.5: -4.3)

## 4. Discovery

**Interaction candidates** (a screen: pairs whose combination seems to matter beyond each alone; untested until held-out matches confirm them; switched on in the model from 40 matches):

- morale_diff with bodyguard_diff (screen 0.352)
- morale_diff with lord_damage_diff (screen 0.345)
- morale_diff with archers_diff (screen 0.328)
- knights_diff with bodyguard_diff (screen 0.319)
- bodyguard_diff with lord_damage_diff (screen 0.304)
- morale_total with bodyguard_diff (screen 0.303)
- archers_diff with bodyguard_diff (screen 0.303)
- spike_killable_diff with bodyguard_diff (screen 0.276)

**Candidate variables** (proposed variables, tested on unseen matches; log loss, lower is better):

- split_diff: 0.562 without, 0.613 with: does not improve yet. own minus enemy players on a split (away from their main group on the enemy half, not carrying). Proposed batch 1 by Claude: the knights curve runs backwards, maybe standing in for the cost of splitting

**Surprises** (moments where the held-out model was most confident about the team that went on to lose; each points to something the variables don't capture yet):

- hdm v HC (28447c4a) at 22:30: a model that never saw this match gave HC 0.3%, and HC won. Why it thought so: morale_diff -47.7, knights_diff +42.0, team strength -41.8, bodyguard_diff +40.2, lord_damage_diff -38.1
- OG v hold (49eec28d) at 3:30: a model that never saw this match gave OG 3.7%, and OG won. Why it thought so: morale_diff -46.2, team strength +25.9, pit_pressure_diff -23.1, flag_lead +8.7, stand -8.0
- hdm v Men (0f1fd794) at 24:00: a model that never saw this match gave Men 0.8%, and Men won. Why it thought so: bodyguard_diff -47.4, pit_pressure_diff -25.0, morale_diff +17.2, flag_lead -12.7, main_diff -7.4
- OG v cope (84586253) at 15:45: a model that never saw this match gave cope 5.1%, and cope won. Why it thought so: archers_diff -36.2, team strength -21.2, pit_pressure_diff -10.1, stand +8.4, boost_clock -1.8
- RACK v MBP (cb5a5f57) at 26:30: a model that never saw this match gave MBP 97.5%, and MBP lost. Why it thought so: morale_diff -45.8, knights_diff +43.8, lord_damage_diff +41.3, bodyguard_diff +39.3, team strength -38.9
- Team v push (2df9b7fd) at 23:15: a model that never saw this match gave push 90.7%, and push lost. Why it thought so: team strength -48.4, spike_killable_diff +45.1, knights_diff +40.2, morale_diff +29.4, lord_damage_diff -18.7

## 5. Denning's rulings seen through the model

Win chance from a model that never saw the match, 20 s before and 60 s after each ruled moment. Contributions are points for an otherwise even game (the curves' scale).

- hdm v HC (28447c4a) 5:01 (split answered), HC: 2.7% 20 s before -> 96.7% 60 s after (+94.0). After: knights_diff +42.0, team strength -41.8, morale_diff +25.7, pit_pressure_diff +20.9
- hdm v HC (28447c4a) 5:01 (split answered), hdm: 97.3% 20 s before -> 3.2% 60 s after (-94.1). After: team strength +41.8, knights_diff -41.7, morale_diff -23.2, pit_pressure_diff -21.8
- hdm v HC (28447c4a) 1:02 (split detection), HC: 9.7% 20 s before -> 3.6% 60 s after (-6.1). After: team strength -41.8, flag_lead -18.8, stand -11.1, morale_diff +9.5
- hdm v HC (28447c4a) 1:02 (split detection), hdm: 89.7% 20 s before -> 97.5% 60 s after (+7.8). After: team strength +41.8, flag_lead +18.6, stand +11.1, carrying_diff +6.6
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), HC: 93.9% 20 s before -> 91.7% 60 s after (-2.2). After: knights_diff +42.0, team strength -41.8, bodyguard_diff +40.2, lord_damage_diff -37.0
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), hdm: 7.1% 20 s before -> 8.7% 60 s after (+1.6). After: team strength +41.8, knights_diff -41.7, bodyguard_diff -40.4, lord_damage_diff +37.0
- hdm v HC (bbef1904) 8:10 (death), HC: 0.3% 20 s before -> 0.0% 60 s after (-0.3). After: team strength -43.2, knights_diff -40.8, morale_diff -39.0, bodyguard_diff -36.3
- hdm v HC (bbef1904) 8:10 (death), hdm: 99.7% 20 s before -> 100.0% 60 s after (+0.3). After: team strength +43.2, knights_diff +40.8, bodyguard_diff +36.2, morale_diff +28.2
- Men v HC (faec428a) 9:31 (death), HC: 4.3% 20 s before -> 6.7% 60 s after (+2.4). After: team strength -44.8, knights_diff +39.1, bodyguard_diff -36.0, flag_lead +9.5
- Men v HC (faec428a) 9:31 (death), Men: 95.9% 20 s before -> 94.2% 60 s after (-1.7). After: team strength +44.8, knights_diff -38.8, bodyguard_diff +35.9, flag_lead -9.2

## 6. Why: the node models

Each explains one result from what happened before it (time order enforced), tested on matches it never saw. AUC = how often a moment that led to the result scores above one that didn't (0.5 = guessing, 1 = perfect).

**deaths** (30 matches, 69889 moments, 1829 results): adds to the simple baseline (AUC 0.896 against 0.764 for health_pct and damage_taken_3s alone).
- **enemies_near** (enemies within 1,500) rises from -17.2 to +25.9 points (0.0..0.5: -17.2; 0.5..1.5: -8.3; 1.5..2.5: -0.4; 2.5..3.5: +1.3; 3.5..4.5: +4.7; 4.5..5.5: +6.6; 5.5..6.5: +11.8; 6.5..7.5: +14.0; 7.5..8.0: +25.9)
- **health_pct** (current health %) falls from +41.4 to -6.3 points (1.0..48.5: +41.4; 60.5..68.5: +22.9; 74.5..78.5: +9.5; 82.5..85.5: +6.2; 88.5..91.5: +2.6; 93.5..95.5: -1.6; 97.5..99.5: -4.4)
- **health_ceiling** (maximum health after death penalty, as a share of normal) falls from +34.8 to -13.3 points (0.4..0.64: +34.8; 0.71..0.84: +24.0; 0.85..0.9: +18.1; 0.94..0.99: +11.0; 1.0..1.1: -1.6)
- **strength_gap** (own minus enemy team strength) falls from +11.4 to -18.8 points (-1092.0..-480.5: +11.4; -382.0..-334.0: -2.7; -168.5..-130.5: +5.1; -38.0..0.0: +8.7; 38.0..130.5: +8.2; 181.0..334.0: -7.4; 382.0..480.5: -0.7)
- **local_diff** (allies minus enemies within 2,000) falls from +32.2 to -18.7 points (-8.0..-3.5: +32.2; -2.5..-1.5: +11.0; -0.5..0.5: -6.0; 1.5..2.5: -6.5; 3.5..4.5: +17.2; 5.5..7.0: -18.7)
- **dist_own_pit** (distance from its own pit) rises from +6.6 to +17.9 points (10.0..1710.5: +6.6; 2929.5..4656.5: -6.9; 5577.5..6359.5: -8.6; 7136.5..7805.5: -3.0; 8361.5..8874.5: -3.6; 9615.5..10481.5: -0.3; 11606.5..13044.5: +11.8)
- **healers_in_range** (own healers alive within cast range) falls from +10.6 to +1.6 points (0.0..0.5: +10.6; 0.5..1.5: -3.3; 1.5..2.5: -6.4; 2.5..3.0: +1.6)
- **minute** (match minute) rises from -3.7 to +16.6 points (0.1..1.25: -3.7; 2.35..3.45: -7.7; 4.55..5.75: +3.2; 7.15..8.75: +3.7; 10.35..12.15: -2.4; 14.05..16.25: -0.7; 18.65..21.75: +7.1)
- **flag_lead** (own flag lead (s)) rises from -10.0 to -4.0 points (-81.0..-64.5: -10.0; -54.5..-36.5: +4.8; -26.5..-16.5: +0.8; -7.5..0.5: -1.8; 8.5..17.5: -3.2; 27.5..36.5: -3.2; 54.5..64.5: +2.8)

**kill conversion** (29 matches, 553 moments, 165 results): adds to the simple baseline (AUC 0.784 against 0.647 for burst_damage and target_health_pct alone).
- **target_ceiling** (target's health ceiling) falls from +27.8 to -18.8 points (0.4..0.56: +27.8; 0.68..0.71: +21.7; 0.83..0.86: +15.8; 0.91..0.92: +9.0; 0.94..0.95: +6.0; 0.98..1.02: -3.3; 1.08..1.1: -18.8)
- **burst_damage** (damage in the 2 s burst) rises from -7.7 to +19.9 points (250.0..257.5: -7.7; 267.5..280.5: -10.0; 290.5..304.0: -7.1; 320.5..336.5: -4.1; 358.5..377.0: -1.9; 409.0..440.0: +0.9; 476.0..547.5: +18.5)
- **target_health_pct** (target health % when the burst started) falls from +22.9 to -7.1 points (0.0..41.5: +22.9; 53.5..58.5: +10.1; 66.5..72.5: +4.1; 76.5..78.5: +1.4; 81.5..85.5: -4.5; 88.5..92.5: -8.4; 96.5..99.5: -7.5)
- **target_healers_in_range** (target's healers in range) falls from +22.0 to -4.4 points (0.0..0.5: +22.0; 0.5..1.5: +0.9; 1.5..2.5: -6.5; 2.5..3.0: -4.4)
- **target_prot_up** (a prot on the target) falls from +4.3 to -9.7 points (0.0..0.5: +4.3; 0.5..1.0: -9.7)
- **minute** (match minute) rises from -11.8 to +9.3 points (0.3..1.35: -11.8; 2.55..3.75: -3.7; 4.95..6.15: -2.4; 7.15..8.45: -1.3; 10.35..12.65: +0.9; 14.45..16.35: +6.6; 18.75..22.0: +8.1)
- **attackers** (attackers in the burst) falls from -2.3 to -7.7 points (3.0..3.5: -2.3; 3.5..4.5: +2.7; 4.5..5.5: +5.0; 5.5..6.5: -4.4; 6.5..7.0: -7.7)
- **target_knocked_down** (target knocked down) falls from +1.6 to -11.0 points (0.0..0.5: +1.6; 0.5..1.0: -11.0)

**flag answer** (seconds an answer to an enemy capture was slower than possible; 27 matches, 306 answers): adds to the simple baseline (typical error 17.3 s against 27.2 s for the median; explains 67% of the spread).
- **handoffs** (hand-offs (drops picked up by a teammate)): 0.0..0.5: -7.4 s; 0.5..1.5: +3.8 s; 1.5..2.5: +25.9 s; 2.5..3.5: +50.4 s; 3.5..6.0: +69.6 s
- **enemies_in_the_way** (enemy presence along the runner's trip back to the spawn): 0.0..0.5: -7.3 s; 4.5..9.5: -5.1 s; 15.5..20.5: -3.6 s; 25.0..37.5: -1.1 s; 50.5..57.0: +5.4 s; 71.5..101.0: +12.7 s; 120.5..171.5: +17.3 s
- **own_deaths_during** (own deaths during the answer): 0.0..0.5: -4.6 s; 0.5..1.5: +6.9 s; 1.5..2.5: +19.8 s; 2.5..4.5: +34.4 s; 4.5..5.5: +54.8 s; 5.5..6.5: +68.6 s; 6.5..8.0: +82.5 s; 8.0..11.0: +95.7 s
- **carrier_damage_taken** (damage the carrier took while carrying): 0.0..2.0: -4.0 s; 26.5..49.0: -3.4 s; 66.0..96.5: -1.6 s; 125.5..177.5: +0.7 s; 244.0..277.5: +3.0 s; 378.0..491.5: +6.0 s; 573.5..944.0: +8.7 s
- **possible_s** (fastest possible answer (s) from the flag model at the enemy's capture): 2.0..6.5: +2.9 s; 12.5..19.5: +3.2 s; 24.5..28.5: +3.4 s; 34.5..38.5: +3.6 s; 40.5..43.5: +1.7 s; 48.5..54.5: -2.6 s; 63.5..75.5: -7.9 s
- **enemy_deaths_during** (enemy deaths during the answer): 0.0..0.5: -2.1 s; 0.5..1.5: +8.5 s; 1.5..2.5: +11.6 s; 2.5..3.5: +14.0 s; 3.5..5.0: +17.3 s
- **runner_to_spawn** (runner's distance to its flag spawn when the enemy captured): 94.0..976.0: -5.6 s; 1503.0..2101.5: -2.6 s; 3384.5..4354.5: +0.5 s; 4871.0..5542.0: +3.3 s; 6234.5..6701.0: +2.8 s; 7263.5..7825.0: +1.1 s; 8439.0..9139.5: +0.6 s
- **flag_lead_at_enemy_cap** (own flag lead when the enemy captured): -80.0..-72.5: -0.4 s; -62.5..-54.5: +2.9 s; -41.5..-36.5: +3.9 s; -26.0..-18.5: +1.8 s; -10.5..-4.5: +0.2 s; 11.5..21.5: -1.7 s; 34.0..52.5: -3.2 s
- **pushers** (enemies who hit the carrier): 0.0..0.5: -1.5 s; 0.5..1.5: -1.4 s; 1.5..2.5: +1.8 s; 2.5..3.5: +2.2 s; 3.5..4.5: +5.2 s; 4.5..5.5: +5.9 s; 5.5..7.0: +4.0 s
- **strength_gap** (own minus enemy team strength): -1092.0..-480.5: +1.9 s; -366.5..-334.0: +1.0 s; -169.5..-58.5: +1.4 s; -25.0..58.5: +2.2 s; 169.5..224.5: -0.1 s; 359.5..406.5: -3.0 s; 480.5..636.0: -3.6 s

## 7. For Denning

- Which curves look wrong to you? A correction (direction, cap, drop, or a pair to always test) is logged with your reason and tested on held-out matches.
- Do any surprises remind you of something the variables don't capture (a missing variable)?
- Any variable you think matters that isn't listed?

