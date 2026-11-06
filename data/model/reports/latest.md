# Learning report, batch 1

Trained on 30 matches (6 new in this batch). Variables in use: 17; build variables from 60 matches, interactions from 40.

## 1. The honest test

**Beats strength alone.** Held-out accuracy (matches held out whole), log loss in brackets (lower is better):

- strength only: all 64% (0.633), 0-5 min 74% (0.519), 5-10 min 69% (0.611), 10-15 min 60% (0.728), 15-end min 51% (0.726)
- glass box: all 79% (0.553), 0-5 min 84% (0.457), 5-10 min 86% (0.344), 10-15 min 82% (0.583), 15-end min 65% (0.846)
- black box: all 77% (0.786), 0-5 min 78% (0.755), 5-10 min 77% (0.751), 10-15 min 78% (0.689), 15-end min 76% (0.927)
- Change since batch 0: glass box log loss 0.636 -> 0.553; strength only 0.534 -> 0.633.

## 2. What it leans on

- **morale_diff** 1.893 (was 1.648): own minus enemy morale summed over players (boosts +, death penalty -)
- **knights_diff** 1.217 (was 1.26): own minus enemy pit knights alive
- **bodyguard_diff** 1.209 (was 0.898): own minus enemy Bodyguard alive
- **stand** 0.313 (was 0.206): who holds the flag stand: 1 own, 0 nobody, -1 enemy
- **lord_damage_diff** 0.295 (was 0.292): own minus enemy Lord damage dealt so far (the 28:00 tiebreak; players can't see it)
- **pit_pressure_diff** 0.256 (was 0.199): own players in the enemy pit minus enemy players in the own pit
- **flag_lead** 0.234 (was 0.321): seconds up (+) or down (-) on flags: enemy's response minus own on the next capture exchange
- **archers_diff** 0.203 (was 0.157): own minus enemy pit archers alive
- **down_diff_s** 0.147 (was 0.103): enemy minus own seconds until all dead players are back (+ = the enemy has more time down)
- **alive_diff** 0.105 (was 0.069): own minus enemy players alive
- **main_diff** 0.102 (was 0.104): own minus enemy players in each team's main group
- **boost_clock** 0.085 (was 0.105): seconds until the stand holder's next boost (+ if own boost is coming, - if the enemy's, 0 nobody)

## 3. The curves in words

Points = win-chance points added to an otherwise even game at each range of the variable.

- **morale_diff** rises from -48.0 to +47.7 points (-470.0..-199.0: -48.0; -159.0..-110.5: -45.5; -86.0..-46.5: -39.8; -15.5..-1.0: -3.4; 1.0..23.0: +3.1; 56.0..97.0: +40.8; 144.0..196.0: +47.3)
- **knights_diff** falls from +40.8 to -40.4 points (-2.0..-1.5: +40.8; -1.5..-0.5: +37.6; -0.5..0.5: -0.9; 0.5..1.5: -36.9; 1.5..2.0: -40.4)
- **bodyguard_diff** falls from +36.1 to -35.7 points (-1.0..-0.5: +36.1; -0.5..0.5: -0.8; 0.5..1.0: -35.7)
- **stand** rises from -8.2 to +8.2 points (-1.0..-0.5: -8.2; -0.5..0.5: +0.3; 0.5..1.0: +8.2)
- **lord_damage_diff** falls from +49.0 to -48.8 points (-9661.0..-5219.0: +49.0; -3355.0..-2101.5: -13.5; -1317.5..-530.5: -21.7; -102.0..-8.5: -26.6; 8.5..102.0: +23.7; 688.5..1338.0: +19.9; 3001.0..4965.0: +0.8)
- **pit_pressure_diff** falls from +0.2 to -15.6 points (-8.0..-5.5: +0.2; -4.5..-3.5: +13.3; -2.5..-1.5: +14.7; -0.5..0.5: +1.8; 1.5..2.5: -20.1; 3.5..5.5: -17.4)
- **flag_lead** falls from +4.6 to -1.7 points (-86.0..-68.5: +4.6; -55.5..-44.5: -8.7; -32.5..-21.5: -8.5; -10.5..-0.5: -4.2; 9.5..20.5: +7.5; 31.5..44.5: +8.4; 55.5..68.5: -0.7)
- **archers_diff** rises from -20.5 to +23.8 points (-4.0..-3.5: -20.5; -3.5..-2.5: -18.1; -2.5..-1.5: +4.0; -1.5..-0.5: +6.6; -0.5..0.5: -0.6; 0.5..1.5: -6.4; 1.5..2.5: -4.0; 2.5..3.5: +22.3; 3.5..4.0: +23.8)
- **down_diff_s** rises from -22.1 to +29.3 points (-960.0..-195.0: -22.1; -127.5..-97.5: -15.2; -67.5..-52.5: -9.4; -37.5..-7.5: -3.9; 7.5..37.5: +3.6; 67.5..97.5: +8.4; 127.5..195.0: +14.5)
- **alive_diff** rises from -26.5 to +29.7 points (-8.0..-4.5: -26.5; -3.5..-2.5: -10.2; -1.5..-0.5: -3.3; 0.5..1.5: +3.1; 2.5..3.5: +10.1; 4.5..8.0: +29.7)

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

- split_diff: 0.553 without, 0.603 with: does not improve yet. own minus enemy players on a split (away from their main group on the enemy half, not carrying). Proposed batch 1 by Claude: the knights curve runs backwards, maybe standing in for the cost of splitting

**Surprises** (moments where the held-out model was most confident about the team that went on to lose; each points to something the variables don't capture yet):

- hdm v HC (28447c4a) at 23:30: a model that never saw this match gave HC 1.6%, and HC won. Why it thought so: morale_diff -47.9, knights_diff +41.9, team strength -41.8, bodyguard_diff +40.7, lord_damage_diff -38.0
- OG v cope (84586253) at 15:45: a model that never saw this match gave cope 4.0%, and cope won. Why it thought so: archers_diff -35.9, team strength -21.2, pit_pressure_diff -10.1, stand +8.7, flag_lead -8.5
- hdm v Men (0f1fd794) at 24:00: a model that never saw this match gave Men 0.7%, and Men won. Why it thought so: bodyguard_diff -47.3, pit_pressure_diff -26.4, morale_diff +14.4, flag_lead -8.2, main_diff -8.2
- OG v hold (49eec28d) at 3:30: a model that never saw this match gave OG 2.0%, and OG won. Why it thought so: morale_diff -46.2, team strength +25.9, pit_pressure_diff -23.9, stand -8.5, main_diff -5.3
- RACK v MBP (cb5a5f57) at 26:30: a model that never saw this match gave MBP 97.4%, and MBP lost. Why it thought so: morale_diff -45.5, knights_diff +43.4, lord_damage_diff +40.6, bodyguard_diff +39.2, team strength -38.9
- Team v push (2df9b7fd) at 22:30: a model that never saw this match gave push 89.7%, and push lost. Why it thought so: team strength -48.4, spike_killable_diff +44.7, knights_diff +39.4, morale_diff +28.7, lord_damage_diff -19.8

## 5. Denning's rulings seen through the model

Win chance from a model that never saw the match, 20 s before and 60 s after each ruled moment. Contributions are points for an otherwise even game (the curves' scale).

- hdm v HC (28447c4a) 5:01 (split answered), HC: 3.2% 20 s before -> 96.4% 60 s after (+93.2). After: knights_diff +41.9, team strength -41.8, morale_diff +25.2, pit_pressure_diff +21.7
- hdm v HC (28447c4a) 5:01 (split answered), hdm: 96.9% 20 s before -> 3.5% 60 s after (-93.4). After: team strength +41.8, knights_diff -41.7, morale_diff -22.7, pit_pressure_diff -22.5
- hdm v HC (28447c4a) 1:02 (split detection), HC: 9.3% 20 s before -> 3.5% 60 s after (-5.8). After: team strength -41.8, flag_lead -13.1, stand -11.5, carrying_diff -8.7
- hdm v HC (28447c4a) 1:02 (split detection), hdm: 92.6% 20 s before -> 97.4% 60 s after (+4.8). After: team strength +41.8, flag_lead +13.1, stand +11.4, carrying_diff +8.6
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), HC: 93.1% 20 s before -> 89.7% 60 s after (-3.4). After: knights_diff +41.9, team strength -41.8, bodyguard_diff +40.7, lord_damage_diff -36.8
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), hdm: 7.9% 20 s before -> 10.7% 60 s after (+2.8). After: team strength +41.8, knights_diff -41.7, bodyguard_diff -40.8, lord_damage_diff +37.2
- hdm v HC (bbef1904) 8:10 (death), HC: 0.3% 20 s before -> 0.0% 60 s after (-0.3). After: team strength -43.2, knights_diff -40.2, morale_diff -39.2, bodyguard_diff -36.3
- hdm v HC (bbef1904) 8:10 (death), hdm: 99.8% 20 s before -> 100.0% 60 s after (+0.2). After: team strength +43.2, knights_diff +40.4, bodyguard_diff +36.3, morale_diff +27.9
- Men v HC (faec428a) 9:31 (death), HC: 3.7% 20 s before -> 3.7% 60 s after (+0.0). After: team strength -44.8, knights_diff +38.1, bodyguard_diff -36.0, stand -8.4
- Men v HC (faec428a) 9:31 (death), Men: 96.5% 20 s before -> 96.8% 60 s after (+0.3). After: team strength +44.8, knights_diff -37.7, bodyguard_diff +36.0, stand +8.4

## 6. Why: the node models

Each explains one result from what happened before it (time order enforced), tested on matches it never saw. AUC = how often a moment that led to the result scores above one that didn't (0.5 = guessing, 1 = perfect).

**deaths** (30 matches, 69889 moments, 1829 results): adds to the simple baseline (AUC 0.89 against 0.764 for health_pct and damage_taken_3s alone).
- **enemies_near** (enemies within 1,500) rises from -17.6 to +26.0 points (0.0..0.5: -17.6; 0.5..1.5: -8.5; 1.5..2.5: -0.2; 2.5..3.5: +1.6; 3.5..4.5: +5.2; 4.5..5.5: +7.1; 5.5..6.5: +11.7; 6.5..7.5: +13.9; 7.5..8.0: +26.0)
- **health_pct** (current health %) falls from +41.4 to -6.3 points (1.0..48.5: +41.4; 60.5..68.5: +23.1; 74.5..78.5: +9.5; 82.5..85.5: +6.2; 88.5..91.5: +2.6; 93.5..95.5: -1.6; 97.5..99.5: -4.4)
- **strength_gap** (own minus enemy team strength) falls from +11.2 to -19.1 points (-1092.0..-480.5: +11.2; -382.0..-334.0: -1.9; -168.5..-130.5: +5.1; -38.0..0.0: +9.6; 38.0..130.5: +8.8; 181.0..334.0: -8.3; 382.0..480.5: -0.4)
- **health_ceiling** (maximum health after death penalty, as a share of normal) falls from +35.2 to -13.4 points (0.4..0.64: +35.2; 0.71..0.84: +24.0; 0.85..0.9: +18.2; 0.94..0.99: +11.0; 1.0..1.1: -1.5)
- **local_diff** (allies minus enemies within 2,000) falls from +32.1 to -19.0 points (-8.0..-3.5: +32.1; -2.5..-1.5: +11.0; -0.5..0.5: -6.0; 1.5..2.5: -6.3; 3.5..4.5: +17.8; 5.5..7.0: -19.0)
- **dist_own_pit** (distance from its own pit) rises from +7.1 to +18.1 points (10.0..1710.5: +7.1; 2929.5..4656.5: -6.7; 5577.5..6359.5: -8.5; 7136.5..7805.5: -3.1; 8361.5..8874.5: -3.7; 9615.5..10481.5: -0.8; 11606.5..13044.5: +12.3)
- **healers_in_range** (own healers alive within cast range) falls from +10.8 to +1.1 points (0.0..0.5: +10.8; 0.5..1.5: -3.3; 1.5..2.5: -6.4; 2.5..3.0: +1.1)
- **minute** (match minute) rises from -3.3 to +16.3 points (0.1..1.25: -3.3; 2.35..3.45: -7.8; 4.55..5.75: +3.3; 7.15..8.75: +3.8; 10.35..12.15: -2.2; 14.05..16.25: -0.7; 18.65..21.75: +6.3)

**kill conversion** (29 matches, 553 moments, 165 results): adds to the simple baseline (AUC 0.784 against 0.647 for burst_damage and target_health_pct alone).
- **target_ceiling** (target's health ceiling) falls from +27.8 to -18.8 points (0.4..0.56: +27.8; 0.68..0.71: +21.7; 0.83..0.86: +15.8; 0.91..0.92: +9.0; 0.94..0.95: +6.0; 0.98..1.02: -3.3; 1.08..1.1: -18.8)
- **burst_damage** (damage in the 2 s burst) rises from -7.7 to +19.9 points (250.0..257.5: -7.7; 267.5..280.5: -10.0; 290.5..304.0: -7.1; 320.5..336.5: -4.1; 358.5..377.0: -1.9; 409.0..440.0: +0.9; 476.0..547.5: +18.5)
- **target_health_pct** (target health % when the burst started) falls from +22.9 to -7.1 points (0.0..41.5: +22.9; 53.5..58.5: +10.1; 66.5..72.5: +4.1; 76.5..78.5: +1.4; 81.5..85.5: -4.5; 88.5..92.5: -8.4; 96.5..99.5: -7.5)
- **target_healers_in_range** (target's healers in range) falls from +22.0 to -4.4 points (0.0..0.5: +22.0; 0.5..1.5: +0.9; 1.5..2.5: -6.5; 2.5..3.0: -4.4)
- **target_prot_up** (a prot on the target) falls from +4.3 to -9.7 points (0.0..0.5: +4.3; 0.5..1.0: -9.7)
- **minute** (match minute) rises from -11.8 to +9.3 points (0.3..1.35: -11.8; 2.55..3.75: -3.7; 4.95..6.15: -2.4; 7.15..8.45: -1.3; 10.35..12.65: +0.9; 14.45..16.35: +6.6; 18.75..22.0: +8.1)
- **attackers** (attackers in the burst) falls from -2.3 to -7.7 points (3.0..3.5: -2.3; 3.5..4.5: +2.7; 4.5..5.5: +5.0; 5.5..6.5: -4.4; 6.5..7.0: -7.7)
- **target_knocked_down** (target knocked down) falls from +1.6 to -11.0 points (0.0..0.5: +1.6; 0.5..1.0: -11.0)

**flag answer** (seconds an answer to an enemy capture was slower than possible; 27 matches, 306 rows): adds to the simple baseline (typical error 16.8s against 26.1s for the median; explains 68% of the spread).
- **parked_s** (seconds the flag lay parked (dropped 5 s or more: not running yet)): 0.0..3.5: -4.8 s; 10.5..14.0: +4.8 s; 18.0..27.5: +17.0 s; 32.0..41.0: +30.6 s; 48.5..62.5: +46.8 s; 83.0..99.0: +53.2 s; 117.5..259.0: +56.0 s
- **own_deaths_during** (own deaths during the answer): 0.0..0.5: -4.0 s; 0.5..1.5: +5.8 s; 1.5..2.5: +11.6 s; 2.5..4.5: +28.4 s; 4.5..5.5: +51.3 s; 5.5..6.5: +65.2 s; 6.5..8.0: +79.5 s; 8.0..11.0: +90.1 s
- **enemies_in_the_way** (enemy presence along the runner's trip back to the spawn): 0.0..0.5: -6.6 s; 4.5..9.5: -4.0 s; 15.5..20.5: -1.8 s; 25.0..37.5: +0.3 s; 50.5..57.0: +4.3 s; 71.5..101.0: +8.9 s; 120.5..171.5: +15.9 s
- **enemy_deaths_during** (enemy deaths during the answer): 0.0..0.5: -2.4 s; 0.5..1.5: +9.8 s; 1.5..2.5: +12.3 s; 2.5..3.5: +15.0 s; 3.5..5.0: +21.8 s
- **carrier_damage_taken** (damage the carrier took while carrying): 0.0..2.0: -3.2 s; 26.5..49.0: -3.8 s; 66.0..96.5: -1.8 s; 125.5..177.5: +0.6 s; 244.0..277.5: +2.8 s; 378.0..491.5: +5.1 s; 573.5..944.0: +7.3 s
- **quick_handoffs** (quick hand-offs (a teammate picked it up within 5 s)): 0.0..0.5: -1.9 s; 0.5..1.5: +4.6 s; 1.5..2.5: +11.7 s; 2.5..3.0: +20.3 s
- **forced_drops** (drops with the carrier hit in the 5 s before, or dying): 0.0..0.5: -1.6 s; 0.5..1.5: +15.6 s; 1.5..2.0: +23.6 s
- **possible_s** (fastest possible answer (s) from the flag model at the enemy's capture): 0.0..3.5: +0.8 s; 7.5..13.5: +1.7 s; 22.5..28.5: +1.7 s; 33.5..36.5: +2.9 s; 41.5..45.5: +1.9 s; 50.5..55.5: -0.7 s; 63.5..74.5: -6.7 s
- **runner_to_spawn** (runner's distance to its flag spawn when the enemy captured): 94.0..976.0: -5.8 s; 1503.0..2101.5: -2.8 s; 3384.5..4354.5: -0.2 s; 4871.0..5542.0: +2.7 s; 6234.5..6701.0: +2.7 s; 7263.5..7825.0: +0.9 s; 8439.0..9139.5: +1.7 s
- **flag_lead_at_enemy_cap** (own flag lead when the enemy captured): -81.0..-74.5: -6.4 s; -62.5..-54.5: -0.2 s; -42.5..-35.5: +2.4 s; -27.5..-18.5: +1.5 s; -10.5..-3.5: +2.0 s; 10.5..19.5: +0.3 s; 35.5..56.5: -0.5 s

**npc loss** (29 matches, 3236 moments, 618 results): adds to the simple baseline (AUC 0.797 against 0.736 for attackers and defenders alone).
- **defenders** (own players in the pit) falls from +37.6 to -41.5 points (0.0..0.5: +37.6; 0.5..1.5: +20.5; 1.5..2.5: +17.6; 2.5..3.5: -6.1; 3.5..4.5: -16.8; 4.5..5.5: -18.5; 5.5..6.5: -18.9; 6.5..7.5: -38.1; 7.5..8.0: -41.5)
- **npc_damage_5s** (damage on the pit NPCs in the last 5 s) rises from -14.3 to +29.5 points (0.0..0.5: -14.3; 22.5..36.5: -1.5; 50.5..65.5: +2.5; 84.5..104.5: +9.7; 126.5..148.5: +22.5; 177.5..212.5: +26.2; 267.5..360.5: +29.2)
- **defenders_elsewhere** (own players alive outside the pit) falls from +24.5 to -9.0 points (0.0..0.5: +24.5; 0.5..1.5: +17.9; 1.5..2.5: +19.6; 2.5..3.5: +6.3; 3.5..4.5: -0.1; 4.5..5.5: -2.9; 5.5..6.5: -17.3; 6.5..7.5: -20.1; 7.5..8.0: -9.0)
- **attackers** (enemy players in the pit) rises from -12.4 to +23.5 points (1.0..1.5: -12.4; 1.5..2.5: -8.2; 2.5..3.5: -6.9; 3.5..4.5: +6.2; 4.5..5.5: +13.1; 5.5..6.5: +16.4; 6.5..7.5: +17.8; 7.5..8.0: +23.5)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -11.2 to +18.6 points (2.4..20.1: -11.2; 24.35..33.05: -7.9; 36.4..36.55: -5.2; 42.75..55.85: -4.0; 64.1..66.8: +3.9; 74.65..79.55: +6.1; 87.3..101.65: +8.5)
- **strength_gap** (attacking minus defending team strength) rises from -11.9 to +9.9 points (-712.0..-463.5: -11.9; -382.0..-265.0: -9.5; -148.0..-92.0: -3.6; 0.0..92.0: +0.6; 148.0..168.5: -10.1; 359.5..382.0: +4.2; 480.5..636.0: +18.4)
- **full_pit_targets** (pit NPCs alive (targets the defending monks must watch, P9)) rises from -10.7 to +27.7 points (1.0..1.5: -10.7; 1.5..2.5: -10.6; 2.5..3.5: +3.8; 3.5..4.5: +3.2; 4.5..5.5: +3.3; 5.5..6.5: +12.4; 6.5..9.0: +27.7)
- **defender_healers** (of which healers) falls from +15.4 to -4.3 points (0.0..0.5: +15.4; 0.5..1.5: -2.1; 1.5..2.5: -4.6; 2.5..3.0: -4.3)

**lord damage** (Lord damage dealt in the next 10 s while players are in the enemy pit; 29 matches, 3939 rows): adds to the simple baseline (typical error 127.0 against 86.4 for the median; explains 36% of the spread).
- **defenders** (own players in the pit): 0.0..0.5: +168.4; 0.5..1.5: +83.9; 1.5..2.5: +12.7; 2.5..3.5: -41.1; 3.5..4.5: -63.9; 4.5..5.5: -93.0; 5.5..6.5: -100.0; 6.5..7.5: -130.6; 7.5..8.0: -137.2
- **bodyguard** (own Bodyguard alive): 0.0..0.5: +98.9; 0.5..1.0: -56.9
- **defenders_elsewhere** (own players alive outside the pit): 0.0..0.5: +60.2; 0.5..1.5: +77.6; 1.5..2.5: +89.1; 2.5..3.5: +97.1; 3.5..4.5: +59.3; 4.5..5.5: +10.7; 5.5..6.5: -39.6; 6.5..7.5: -98.4; 7.5..8.0: -184.7
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)): 2.4..18.65: -75.2; 24.35..33.05: -47.9; 36.4..36.55: -47.4; 42.75..55.85: -11.7; 65.25..66.8: +21.0; 73.25..79.45: +38.9; 87.3..101.65: +91.0
- **defender_healers** (of which healers): 0.0..0.5: +87.9; 0.5..1.5: +5.7; 1.5..2.5: -36.7; 2.5..3.0: -78.0
- **attackers** (enemy players in the pit): 1.0..1.5: -25.8; 1.5..2.5: -15.8; 2.5..3.5: -20.9; 3.5..4.5: -16.0; 4.5..5.5: +57.9; 5.5..6.5: +66.6; 6.5..7.5: +20.5; 7.5..8.0: +52.9
- **seconds_in_pit** (seconds the attackers have been in the pit): 0.0..4.5: -21.9; 10.5..16.5: -26.4; 22.5..28.5: -26.1; 37.5..46.5: -8.4; 58.5..70.5: +25.2; 85.5..103.5: +36.6; 124.5..160.5: +55.6
- **attackers_area_damage** (area-damage skills on the attackers' bars (Denning P9)): 0.0..0.5: +16.9; 0.5..1.0: -45.4
- **minute** (match minute): 0.6..2.65: -11.5; 3.95..5.15: +9.9; 6.25..7.35: +4.7; 8.95..10.45: -1.8; 12.25..14.45: -15.8; 16.25..19.05: -26.6; 21.15..24.75: +1.6
- **strength_gap** (attacking minus defending team strength): -712.0..-420.5: -13.2; -334.0..-148.0: +6.5; -38.0..43.5: +29.3; 148.0..168.5: +13.8; 359.5..366.5: -6.7; 406.5..420.5: -32.1; 570.5..674.5: -7.9

## 7. The usual play

Each choice against the most common one in that kind of decision, in win-chance points over the decision's window, adjusted for the situation, with a 90% range from resampling whole matches. CLEAR = the range excludes 0. Win chance comes from a model that never saw the match.

**after wipe** (65 decisions, 27 matches; usual: pushed the pit)
- took the flag (n 12): +11.5 [+1.7, +22.1] CLEAR
- reset (n 7): +2.1 [-5.0, +7.1]

**boost clock** (107 decisions, 29 matches; usual: not running, fought)
- running, fought (n 20): +4.8 [-0.5, +12.6]
- not running, advanced (n 17): +0.4 [-4.7, +6.1]
- running, advanced (n 15): +1.7 [-9.4, +13.6]
- not running, fell back (n 14): -11.7 [-21.3, -4.4] CLEAR
- not running, held (n 5): -11.1 [-37.7, +6.5]

**enemy pickup** (447 decisions, 29 matches; usual: already running, fought)
- held, fought (n 67): +2.3 [-2.2, +8.3]
- already running, advanced (n 52): +1.6 [-3.3, +6.0]
- held, fell back (n 38): -4.9 [-12.3, +0.7]
- ran, fought (n 37): +1.8 [-2.7, +6.6]
- already running, fell back (n 34): +2.3 [-0.5, +4.8]
- held, advanced (n 34): -0.8 [-6.1, +3.6]
- ran, fell back (n 33): -0.9 [-6.9, +5.0]
- ran, advanced (n 26): -0.4 [-3.3, +3.6]
- already running, held (n 15): +0.2 [-3.7, +3.6]
- held, held (n 8): -10.6 [-25.0, +12.2]
- ran, held (n 7): -2.8 [-9.8, +2.4]

- **late_game**: not enough decisions yet (13)
**power play** (329 decisions, 30 matches; usual: pushed, advanced)
- pushed, fought (n 90): -0.2 [-4.6, +4.0]
- held, fought (n 67): -3.7 [-7.6, -1.5] CLEAR
- held, fell back (n 26): -4.2 [-8.7, -0.4] CLEAR
- held, advanced (n 10): +3.4 [-5.3, +17.4]
- pushed, fell back (n 8): -4.1 [-8.4, -0.8] CLEAR
- pushed, held (n 5): -4.0 [-10.4, +2.6]

**split in base** (72 decisions, 21 matches; usual: on time)
- missed (n 8): -2.2 [-7.4, +3.1]

## 8. For Denning

- Which curves look wrong to you? A correction (direction, cap, drop, or a pair to always test) is logged with your reason and tested on held-out matches.
- Do any surprises remind you of something the variables don't capture (a missing variable)?
- Any variable you think matters that isn't listed?

