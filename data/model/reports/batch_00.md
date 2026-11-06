# Learning report, batch 0

Trained on 24 matches (24 new in this batch). Variables in use: 20; build variables from 60 matches, interactions from 40.

## 0. Data integrity

- Lengths repaired: 2 (1f65fd3b 150 s -> 1027 s) (bbef1904 617 s -> 599 s) 
- Matches with a team's Lord damage not observed (left blank, not zero): 2
- Pit NPCs added from the standard roster (never seen in the replay): 66 in 18 matches
- Left out of training: 0

## 1. The honest test

**Not yet better than strength alone: treat the curves as noise.** Held-out accuracy (matches held out whole), log loss in brackets (lower is better):

- strength only: all 71% (0.442), 0-5 min 79% (0.389), 5-10 min 75% (0.424), 10-15 min 68% (0.469), 15-end min 60% (0.502), matches lasting 15 min+ 66% (0.497), matches even on strength (gap under 200) 49% (0.697)
- glass box: all 68% (0.692), 0-5 min 72% (0.494), 5-10 min 73% (0.537), 10-15 min 68% (0.81), 15-end min 61% (0.994), matches lasting 15 min+ 62% (0.831), matches even on strength (gap under 200) 58% (0.971)
- black box: all 79% (0.849), 0-5 min 83% (0.669), 5-10 min 80% (0.795), 10-15 min 74% (1.025), 15-end min 75% (0.986), matches lasting 15 min+ 74% (1.04), matches even on strength (gap under 200) 62% (1.497)
- Gain over strength alone (log loss, resampling whole matches): -0.25 (90% range -0.523 to -0.007).

## 2. What it leans on

- **morale_diff** 0.808: own minus enemy morale summed over players (boosts +, death penalty -)
- **flag_lead** 0.29: seconds up (+) or down (-) on flags: enemy's response minus own on the next capture exchange
- **main_diff** 0.239: own minus enemy players in each team's main group
- **lord_damage_diff** 0.204: own minus enemy Lord damage dealt so far (the 28:00 tiebreak; players can't see it); blank when either team's Lord damage wasn't observed
- **stand** 0.196: who holds the flag stand: 1 own, 0 nobody, -1 enemy
- **pit_pressure_diff** 0.189: own players in the enemy pit minus enemy players in the own pit
- **archers_diff** 0.188: own minus enemy pit archers alive
- **down_diff_s** 0.125: enemy minus own seconds until all dead players are back (+ = the enemy has more time down)
- **boost_clock** 0.122: seconds until the stand holder's next boost (+ if own boost is coming, - if the enemy's, 0 nobody)
- **carrying_diff** 0.109: own minus enemy players carrying a flag
- **lord_health_diff** 0.089: own minus enemy Lord health as a share of its max (rebuilt from damage, healing and measured regeneration, lord.py); blank if unobserved
- **spike_killable_diff** 0.08: enemy minus own players within one spike of the other side (DP stacking; 0 unless a spike build is involved)

## 3. The curves in words

Points = win-chance points added to an otherwise even game at each range of the variable.

- **morale_diff** rises from -36.9 to +34.3 points (-470.0..-199.0: -36.9; -157.5..-110.5: -28.1; -91.5..-48.0: -26.6; -15.5..-1.0: -1.4; 1.0..15.5: +1.2; 48.0..94.5: +28.6; 124.5..170.5: +30.5)
- **flag_lead** falls from +20.9 to -20.3 points (-86.0..-72.5: +20.9; -55.5..-43.5: -5.9; -31.5..-20.5: -6.4; -9.5..-0.5: -1.9; 8.5..20.5: +4.0; 31.5..43.5: +6.2; 55.5..72.5: -2.6)
- **main_diff** rises from -23.0 to +20.0 points (-8.0..-4.5: -23.0; -3.5..-2.5: -8.5; -1.5..-0.5: -5.1; 0.5..1.5: +5.6; 2.5..3.5: +8.2; 4.5..8.0: +20.0)
- **lord_damage_diff** falls from +47.5 to -48.0 points (-9661.0..-5100.5: +47.5; -3309.5..-1594.0: +2.7; -1167.5..-491.0: +1.0; -111.0..-8.5: +0.2; 8.5..111.0: -0.7; 631.0..1323.5: -2.6; 2868.5..4965.0: -18.8)
- **stand** rises from -5.1 to +5.1 points (-1.0..-0.5: -5.1; -0.5..0.5: -0.8; 0.5..1.0: +5.1)
- **pit_pressure_diff** rises from -11.1 to +13.1 points (-8.0..-5.5: -11.1; -4.5..-3.5: +12.0; -2.5..-1.5: +13.1; -0.5..0.5: +0.1; 1.5..2.5: -14.2; 3.5..4.5: -12.8)
- **archers_diff** falls from +4.5 to -3.0 points (-3.0..-2.5: +4.5; -2.5..-1.5: +10.0; -1.5..-0.5: +10.6; -0.5..0.5: -0.1; 0.5..1.5: -10.2; 1.5..2.5: -9.8; 2.5..3.0: -3.0)
- **down_diff_s** rises from -35.7 to +37.2 points (-960.0..-195.0: -35.7; -127.5..-97.5: -8.7; -67.5..-52.5: -4.6; -37.5..-7.5: -1.9; 7.5..37.5: +1.5; 52.5..82.5: +4.9; 112.5..165.0: +9.1)
- **boost_clock** rises from -3.5 to +3.5 points (-120.0..-109.5: -3.5; -98.5..-87.5: -3.5; -75.5..-58.5: -3.2; -34.5..-0.5: -2.5; 10.5..44.5: +2.8; 65.5..81.5: +3.4; 95.5..108.5: +3.4)
- **carrying_diff** rises from -8.8 to +9.7 points (-1.0..-0.5: -8.8; -0.5..0.5: -0.2; 0.5..1.0: +9.7)

## 4. Discovery

**Interaction candidates** (a screen: pairs whose combination seems to matter beyond each alone; untested until held-out matches confirm them; switched on in the model from 40 matches):

- morale_diff with lord_exposed_diff (screen 0.076)
- morale_diff with knights_diff (screen 0.072)
- morale_diff with bodyguard_diff (screen 0.070)
- main_diff with morale_diff (screen 0.069)
- morale_diff with lord_damage_diff (screen 0.062)
- down_diff_s with morale_diff (screen 0.061)
- alive_diff with morale_diff (screen 0.061)
- morale_diff with archers_diff (screen 0.058)

**Candidate variables** (proposed variables, tested on unseen matches; log loss, lower is better):

- split_diff: 0.692 without, 0.693 with: does not improve yet. own minus enemy players on a split (away from their main group on the enemy half, not carrying). Proposed batch 1 by Claude: the knights curve runs backwards, maybe standing in for the cost of splitting

**Surprises** (moments where the held-out model was most confident about the team that went on to lose; each points to something the variables don't capture yet):

- RACK v hdm (1f65fd3b) at 13:45: a model that never saw this match gave RACK 2.1%, and RACK won. Why it thought so: morale_diff -37.7, team strength -14.0, lord_damage_diff -13.8, flag_lead -8.8, stand -7.5
- hdm v HC (28447c4a) at 16:00: a model that never saw this match gave HC 0.1%, and HC won. Why it thought so: lord_damage_diff -36.2, morale_diff -31.7, bodyguard_diff -27.3, knights_diff -24.2, team strength -16.4
- Men v HC (faec428a) at 15:45: a model that never saw this match gave Men 1.4%, and Men won. Why it thought so: main_diff -33.9, lord_damage_diff -21.8, team strength +14.9, pit_pressure_diff -14.1, alive_diff -13.2
- OG v hold (49eec28d) at 3:45: a model that never saw this match gave OG 4.2%, and OG won. Why it thought so: morale_diff -28.4, pit_pressure_diff -25.2, flag_lead -20.8, team strength +19.0, main_diff -9.0
- Team v push (2df9b7fd) at 20:00: a model that never saw this match gave Team 17.1%, and Team won. Why it thought so: team strength +48.1, spike_killable_diff -43.3, archers_diff -16.0, pit_pressure_diff -12.8, lord_exposed_diff -7.4
- cope v hdm (1d073205) at 14:30: a model that never saw this match gave hdm 15.5%, and hdm won. Why it thought so: morale_diff -35.7, team strength +35.3, flag_lead -24.3, pit_pressure_diff -19.2, stand +4.1

## 5. Denning's rulings seen through the model

Win chance from a model that never saw the match, 20 s before and 60 s after each ruled moment. Contributions are points for an otherwise even game (the curves' scale).

- hdm v HC (28447c4a) 5:01 (split answered), HC: 31.1% 20 s before -> 51.6% 60 s after (+20.5). After: knights_diff -24.2, pit_pressure_diff +18.4, team strength -16.4, carrying_diff +11.1
- hdm v HC (28447c4a) 5:01 (split answered), hdm: 71.4% 20 s before -> 53.0% 60 s after (-18.4). After: knights_diff +23.6, pit_pressure_diff -16.9, team strength +16.4, carrying_diff -11.4
- hdm v HC (28447c4a) 1:02 (split detection), HC: 34.2% 20 s before -> 31.8% 60 s after (-2.4). After: team strength -16.4, carrying_diff -11.4, flag_lead +10.5, main_diff +6.6
- hdm v HC (28447c4a) 1:02 (split detection), hdm: 67.9% 20 s before -> 71.0% 60 s after (+3.1). After: team strength +16.4, carrying_diff +11.1, flag_lead -9.0, main_diff -6.4
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), HC: 8.4% 20 s before -> 10.0% 60 s after (+1.6). After: bodyguard_diff -27.3, knights_diff -24.2, pit_pressure_diff +18.4, team strength -16.4
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), hdm: 93.0% 20 s before -> 92.5% 60 s after (-0.5). After: bodyguard_diff +29.7, knights_diff +23.6, pit_pressure_diff -16.9, team strength +16.4
- hdm v HC (bbef1904) 8:10 (death), HC: 44.4% 20 s before -> 4.5% 60 s after (-39.9). After: morale_diff -26.7, team strength -16.0, main_diff -10.7, down_diff_s -9.8
- hdm v HC (bbef1904) 8:10 (death), hdm: 55.6% 20 s before -> 95.3% 60 s after (+39.7). After: morale_diff +28.8, team strength +16.0, main_diff +11.0, down_diff_s +8.8
- Men v HC (faec428a) 9:31 (death), HC: 33.3% 20 s before -> 35.4% 60 s after (+2.1). After: team strength -14.9, knights_diff +9.2, stand -4.0, boost_clock -2.5
- Men v HC (faec428a) 9:31 (death), Men: 69.6% 20 s before -> 68.6% 60 s after (-1.0). After: team strength +14.9, knights_diff -6.8, stand +4.0, morale_diff +3.5

## 6. Why: the node models

Each explains one result from what happened before it (time order enforced), tested on matches it never saw. AUC = how often a moment that led to the result scores above one that didn't (0.5 = guessing, 1 = perfect).

**deaths** (24 matches, 60118 moments, 1413 results): adds to the simple baseline (AUC 0.908 against 0.778 for health_pct and damage_taken_3s alone).
- **strength_gap** (own minus enemy team strength) falls from +17.2 to -11.3 points (-682.0..-426.0: +17.2; -302.5..-159.0: +19.5; -117.5..-111.0: +7.2; -102.5..-31.0: +16.1; 17.5..102.5: -4.6; 116.0..128.5: -13.4; 302.5..426.0: -17.1)
- **enemies_near** (enemies within 1,500) rises from -13.8 to +24.1 points (0.0..0.5: -13.8; 0.5..1.5: -9.1; 1.5..2.5: -0.5; 2.5..3.5: +1.2; 3.5..4.5: +6.0; 4.5..5.5: +9.3; 5.5..6.5: +12.1; 6.5..7.5: +13.9; 7.5..8.0: +24.1)
- **health_pct** (current health %) falls from +40.3 to -5.8 points (1.0..47.5: +40.3; 60.5..68.5: +23.5; 74.5..78.5: +11.6; 82.5..85.5: +5.4; 88.5..91.5: +1.7; 93.5..95.5: -1.8; 97.5..99.5: -5.2)
- **local_diff** (allies minus enemies within 2,000) falls from +34.3 to -11.9 points (-8.0..-3.5: +34.3; -2.5..-1.5: +10.7; -0.5..0.5: -8.2; 1.5..2.5: -6.0; 3.5..4.5: +21.8; 5.5..7.0: -11.9)
- **dist_own_pit** (distance from its own pit) rises from +7.5 to +19.1 points (10.0..1557.5: +7.5; 2644.5..4446.5: -5.6; 5447.5..6211.5: -6.5; 6993.5..7686.5: -4.8; 8248.5..8687.5: -4.7; 9284.5..10272.5: -3.9; 11557.5..12950.5: +12.9)
- **minute** (match minute) rises from -5.2 to +20.2 points (0.1..1.35: -5.2; 2.55..3.75: -6.4; 4.95..6.15: +6.2; 7.45..8.95: +5.0; 10.55..12.25: -5.3; 14.05..16.25: -0.1; 18.75..21.95: +9.2)
- **healers_in_range** (own healers alive within cast range) is flat from +8.8 to +7.5 points (0.0..0.5: +8.8; 0.5..1.5: -4.4; 1.5..2.5: -6.3; 2.5..3.0: +7.5)
- **health_ceiling** (maximum health after death penalty, as a share of normal) falls from +28.3 to -4.2 points (0.4..0.61: +28.3; 0.69..0.7: +26.5; 0.77..0.84: +15.2; 0.85..0.88: +11.5; 0.92..0.94: +4.4; 0.95..0.99: +0.4; 1.0..1.1: -3.3)
- **allies_near** (allies within 1,500) falls from +6.2 to -7.2 points (0.0..0.5: +6.2; 0.5..1.5: +5.2; 1.5..2.5: +6.7; 2.5..3.5: -1.1; 3.5..4.5: -2.2; 4.5..5.5: -1.5; 5.5..6.5: -5.7; 6.5..7.0: -7.2)
- **res_in** (seconds until the next res) is flat from +10.3 to +8.9 points (1.0..11.5: +10.3; 20.5..29.5: -1.6; 38.5..47.5: -1.7; 56.5..65.5: +0.5; 74.5..83.5: -0.6; 92.5..98.5: -3.5; 104.5..110.5: -6.4)

**kill conversion** (24 matches, 409 moments, 119 results): adds to the simple baseline (AUC 0.708 against 0.61 for burst_damage and target_health_pct alone).
- **target_ceiling** (target's health ceiling) falls from +27.6 to -15.9 points (0.4..0.56: +27.6; 0.66..0.71: +19.4; 0.82..0.86: +11.7; 0.88..0.94: +8.0; 0.98..1.02: -3.2; 1.08..1.1: -15.9)
- **target_healers_in_range** (target's healers in range) falls from +21.7 to -4.1 points (0.0..0.5: +21.7; 0.5..1.5: -1.8; 1.5..2.5: -6.7; 2.5..3.0: -4.1)
- **strength_gap** (attacking minus target team strength) rises from -12.4 to +15.0 points (-682.0..-300.5: -12.4; -193.5..-117.5: -11.2; -106.0..-17.5: -1.2; 57.5..86.5: +11.4; 116.0..140.5: -1.5; 159.0..252.5: +9.3; 280.0..426.0: -0.6)
- **burst_damage** (damage in the 2 s burst) rises from -3.9 to +16.2 points (250.0..256.5: -3.9; 266.5..277.5: -8.9; 288.5..300.5: -7.5; 315.0..328.5: -0.3; 348.5..368.5: -0.8; 396.5..422.5: +2.3; 466.5..521.0: +14.2)
- **target_health_pct** (target health % when the burst started) falls from +20.9 to -4.4 points (0.0..39.5: +20.9; 52.5..57.5: +6.8; 63.5..71.5: +2.7; 76.5..79.5: +0.5; 82.5..86.5: -4.3; 88.5..92.5: -6.2; 96.5..99.5: -6.9)
- **target_prot_up** (a prot on the target) falls from +3.5 to -9.2 points (0.0..0.5: +3.5; 0.5..1.0: -9.2)
- **minute** (match minute) rises from -12.0 to +11.4 points (0.3..1.5: -12.0; 2.75..3.95: -3.4; 4.95..6.05: -2.8; 6.85..7.75: -1.6; 8.85..11.05: -0.3; 13.25..15.25: +5.1; 17.4..21.4: +10.0)
- **attackers_interrupted** (interrupts on the attackers (5 s before to 2 s after)) falls from +2.7 to -32.1 points (0.0..0.5: +2.7; 0.5..1.5: -18.8; 1.5..2.0: -32.1)
- **attackers** (attackers in the burst) falls from -2.6 to -6.4 points (3.0..3.5: -2.6; 3.5..4.5: +4.5; 4.5..5.5: +2.4; 5.5..6.5: +1.8; 6.5..7.0: -6.4)
- **target_knocked_down** (target knocked down) falls from +1.6 to -8.5 points (0.0..0.5: +1.6; 0.5..1.0: -8.5)

**flag answer** (seconds an answer to an enemy capture was slower than possible; 21 matches, 276 rows): adds to the simple baseline (typical error 16.4s against 23.7s for the median; explains 62% of the spread).
- **parked_s** (seconds the flag lay parked (dropped 5 s or more: not running yet)): 0.0..3.5: -4.8 s; 10.5..15.5: +3.2 s; 18.0..26.0: +14.4 s; 29.0..34.5: +32.1 s; 41.0..48.5: +52.6 s; 59.5..72.0: +64.9 s; 95.0..115.5: +63.0 s
- **enemies_in_the_way** (enemy presence along the runner's trip back to the spawn): 0.0..0.5: -4.5 s; 3.5..8.0: -3.0 s; 13.5..18.5: -2.4 s; 22.5..26.5: -0.8 s; 38.5..50.5: +1.6 s; 55.5..70.5: +6.1 s; 105.5..135.0: +11.4 s
- **own_deaths_during** (own deaths during the answer): 0.0..0.5: -2.5 s; 0.5..1.5: +4.8 s; 1.5..3.0: +5.1 s; 3.0..4.5: +22.4 s; 4.5..5.5: +36.9 s; 5.5..6.5: +54.9 s; 6.5..11.0: +81.7 s
- **carrier_damage_taken** (damage the carrier took while carrying): 0.0..2.0: -2.9 s; 25.5..44.5: -3.5 s; 57.5..91.5: -2.6 s; 119.0..164.0: -0.0 s; 227.0..265.0: +2.2 s; 348.5..448.0: +5.0 s; 550.5..937.5: +7.5 s
- **enemy_deaths_during** (enemy deaths during the answer): 0.0..0.5: -2.0 s; 0.5..1.5: +10.3 s; 1.5..2.5: +12.5 s; 2.5..3.5: +17.6 s; 3.5..5.0: +23.7 s
- **forced_drops** (drops with the carrier hit in the 5 s before, or dying): 0.0..0.5: -1.5 s; 0.5..1.5: +14.5 s; 1.5..2.0: +23.1 s
- **quick_handoffs** (quick hand-offs (a teammate picked it up within 5 s)): 0.0..0.5: -1.7 s; 0.5..1.5: +4.4 s; 1.5..2.5: +7.7 s; 2.5..3.0: +13.4 s
- **possible_s** (fastest possible answer (s) from the flag model at the enemy's capture): 0.0..3.5: +0.3 s; 7.5..13.5: +1.7 s; 22.5..28.5: +1.1 s; 33.5..36.5: +2.8 s; 41.5..44.5: +2.2 s; 49.5..55.5: -1.3 s; 64.5..75.5: -6.3 s
- **runner_to_spawn** (runner's distance to its flag spawn when the enemy captured): 94.0..976.0: -5.3 s; 1533.5..2052.0: -2.8 s; 3282.0..4238.0: -0.6 s; 4849.0..5542.0: +2.4 s; 6075.5..6634.5: +2.5 s; 7071.5..7759.0: +1.4 s; 8387.5..9134.5: +1.5 s
- **own_fighting_at_enemy_cap** (own players fighting when the enemy captured): 0.0..0.5: +5.1 s; 0.5..1.5: +2.6 s; 1.5..2.5: +1.3 s; 2.5..3.5: +0.4 s; 3.5..4.5: -0.9 s; 4.5..5.5: -1.5 s; 5.5..6.5: -3.2 s; 6.5..7.5: -6.9 s; 7.5..8.0: -11.4 s

**npc loss** (24 matches, 2985 moments, 509 results): adds to the simple baseline (AUC 0.784 against 0.748 for attackers and defenders alone).
- **defenders** (own players in the pit) falls from +38.6 to -38.9 points (0.0..0.5: +38.6; 0.5..1.5: +28.0; 1.5..2.5: +17.3; 2.5..3.5: -6.3; 3.5..4.5: -18.8; 4.5..5.5: -20.2; 5.5..6.5: -21.2; 6.5..7.5: -36.1; 7.5..8.0: -38.9)
- **npc_damage_5s** (damage on the pit NPCs in the last 5 s) rises from -13.9 to +31.3 points (0.0..0.5: -13.9; 22.5..36.5: -3.2; 50.5..65.5: +0.6; 81.5..100.5: +9.0; 118.5..143.5: +22.4; 172.5..204.5: +25.9; 257.5..356.5: +29.4)
- **strength_gap** (attacking minus defending team strength) rises from -25.0 to +13.1 points (-682.0..-377.0: -25.0; -280.0..-128.5: -3.5; -102.5..31.0: -0.8; 86.5..102.5: -12.8; 106.0..128.5: +17.5; 252.5..302.5: +11.3; 377.0..511.5: +12.5)
- **attackers** (enemy players in the pit) rises from -13.3 to +23.2 points (1.0..1.5: -13.3; 1.5..2.5: -7.3; 2.5..3.5: -5.8; 3.5..4.5: +3.5; 4.5..5.5: +17.6; 5.5..6.5: +21.0; 6.5..7.5: +22.5; 7.5..8.0: +23.2)
- **defenders_elsewhere** (own players alive outside the pit) falls from +22.7 to -3.0 points (0.0..0.5: +22.7; 0.5..1.5: +9.7; 1.5..2.5: +18.9; 2.5..3.5: +1.2; 3.5..4.5: -0.8; 4.5..5.5: -1.1; 5.5..6.5: -15.9; 6.5..7.5: -14.8; 7.5..8.0: -3.0)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -6.0 to +8.1 points (2.4..21.8: -6.0; 24.35..32.9: -11.0; 36.4..36.55: -2.6; 43.8..57.3: -1.9; 65.85..67.3: +5.2; 76.2..80.9: +7.2; 87.75..101.75: +5.2)
- **archers** (own pit archers alive) rises from -3.7 to +25.0 points (0.0..0.5: -3.7; 0.5..1.5: -6.1; 1.5..2.5: +4.3; 2.5..3.0: +25.0)
- **npc_healing_10s** (healing on own pit NPCs and Lord in the last 10 s) falls from +3.0 to -7.0 points (0.0..5.5: +3.0; 43.0..77.0: +2.4; 104.0..136.5: +0.7; 174.5..207.0: -4.0; 243.5..292.5: -7.1; 329.5..389.0: -8.5; 454.5..594.0: -9.8)
- **full_pit_targets** (pit NPCs alive (targets the defending monks must watch, P9)) rises from -8.9 to +15.4 points (1.0..1.5: -8.9; 1.5..2.5: -8.7; 2.5..3.5: +2.9; 3.5..4.5: +1.7; 4.5..5.5: +3.0; 5.5..6.0: +15.4)
- **minute** (match minute) is flat from +1.0 to +2.4 points (0.6..2.65: +1.0; 3.85..4.85: +2.8; 5.75..6.75: +2.0; 7.75..9.45: +1.1; 11.15..12.85: -2.1; 14.65..16.15: +5.6; 19.75..23.35: -14.8)

**lord damage** (Lord damage dealt in the next 10 s while players are in the enemy pit; 23 matches, 3567 rows): adds to the simple baseline (typical error 116.6 against 82.0 for the median; explains 32% of the spread).
- **bodyguard** (own Bodyguard alive): 0.0..0.5: +142.2; 0.5..1.0: -50.5
- **defenders** (own players in the pit): 0.0..0.5: +146.4; 0.5..1.5: +63.7; 1.5..2.5: +12.5; 2.5..3.5: -32.6; 3.5..4.5: -50.8; 4.5..5.5: -93.9; 5.5..6.5: -102.4; 6.5..7.5: -117.1; 7.5..8.0: -78.5
- **defenders_elsewhere** (own players alive outside the pit): 0.0..0.5: +58.3; 0.5..1.5: +75.7; 1.5..2.5: +84.1; 2.5..3.5: +87.7; 3.5..4.5: +40.6; 4.5..5.5: +7.7; 5.5..6.5: -33.1; 6.5..7.5: -80.9; 7.5..8.0: -143.5
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)): 2.4..20.1: -54.8; 24.1..33.05: -43.7; 36.4..36.55: -48.4; 42.75..55.55: -9.2; 65.85..67.3: +10.0; 75.35..79.55: +19.2; 87.75..101.15: +89.6
- **attackers** (enemy players in the pit): 1.0..1.5: -32.6; 1.5..2.5: -23.2; 2.5..3.5: -21.8; 3.5..4.5: -4.3; 4.5..5.5: +88.9; 5.5..6.5: +69.4; 6.5..7.5: +39.7; 7.5..8.0: +58.6
- **defender_healers** (of which healers): 0.0..0.5: +61.3; 0.5..1.5: +9.9; 1.5..2.5: -25.2; 2.5..3.0: -71.2
- **seconds_in_pit** (seconds the attackers have been in the pit): 0.0..4.5: -22.6; 10.5..16.5: -24.9; 22.5..28.5: -24.7; 37.5..46.5: -12.8; 55.5..67.5: +17.4; 79.5..97.5: +36.6; 121.5..157.5: +60.6
- **archers** (own pit archers alive): 0.0..0.5: -35.3; 0.5..1.5: -12.2; 1.5..2.5: +28.1; 2.5..3.0: -38.6
- **attackers_area_damage** (area-damage skills on the attackers' bars (Denning P9)): 0.0..0.5: +15.9; 0.5..1.0: -45.6
- **strength_gap** (attacking minus defending team strength): -682.0..-321.0: +31.4; -157.5..-106.0: +32.8; -17.5..57.5: +18.9; 102.5..106.0: -3.9; 128.5..210.5: -15.9; 298.0..321.0: -24.8; 377.0..511.5: -21.1

**lord kill** (23 matches, 3565 moments, 198 results): no better than the simple baseline yet (AUC 0.934 against 0.961 for attackers and defenders alone).
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -47.6 to +47.8 points (2.4..20.1: -47.6; 24.1..33.05: -47.2; 36.4..36.55: -46.5; 42.75..55.55: +40.3; 65.85..67.3: +35.5; 75.35..79.55: +38.5; 87.75..101.5: +36.0)
- **attackers** (enemy players in the pit) rises from -34.7 to +47.4 points (1.0..1.5: -34.7; 1.5..2.5: -32.6; 2.5..3.5: -29.4; 3.5..4.5: +6.8; 4.5..5.5: +46.5; 5.5..6.5: +48.5; 6.5..7.5: +48.5; 7.5..8.0: +47.4)
- **defenders** (own players in the pit) falls from +46.7 to -49.7 points (0.0..0.5: +46.7; 0.5..1.5: +43.2; 1.5..2.5: +13.2; 2.5..3.5: -9.4; 3.5..4.5: -37.7; 4.5..5.5: -40.3; 5.5..6.5: -46.1; 6.5..7.5: -46.9; 7.5..8.0: -49.7)
- **defenders_elsewhere** (own players alive outside the pit) falls from +47.2 to -48.3 points (0.0..0.5: +47.2; 0.5..1.5: +36.4; 1.5..2.5: +33.2; 2.5..3.5: +32.2; 3.5..4.5: +30.4; 4.5..5.5: +11.5; 5.5..6.5: -1.8; 6.5..7.5: -48.0; 7.5..8.0: -48.3)
- **minute** (match minute) rises from -48.2 to +21.8 points (0.6..2.95: -48.2; 4.25..5.35: -22.3; 6.35..7.35: +3.3; 9.15..10.85: +19.4; 12.55..14.55: +21.0; 16.15..18.85: +31.2; 20.85..24.95: +30.9)
- **defender_healers** (of which healers) falls from +23.4 to -40.6 points (0.0..0.5: +23.4; 0.5..1.5: +22.2; 1.5..2.5: -19.2; 2.5..3.0: -40.6)
- **seconds_in_pit** (seconds the attackers have been in the pit) rises from -7.3 to +44.7 points (0.0..4.5: -7.3; 10.5..16.5: -20.2; 22.5..28.5: -26.9; 37.5..46.5: -23.1; 55.5..67.5: +16.9; 79.5..97.5: +19.6; 121.5..157.5: +41.8)
- **archers** (own pit archers alive) rises from -12.9 to +6.8 points (0.0..0.5: -12.9; 0.5..1.5: -11.8; 1.5..2.5: +14.5; 2.5..3.0: +6.8)
- **npc_healing_10s** (healing on own pit NPCs and Lord in the last 10 s) falls from +10.2 to -27.7 points (0.0..5.5: +10.2; 43.0..76.5: +3.0; 105.5..141.5: -9.7; 174.5..209.0: -15.2; 244.5..295.0: -16.6; 328.0..383.5: -16.5; 444.5..573.5: -22.4)
- **res_in** (seconds until the next res) rises from -38.5 to +18.2 points (1.0..8.5: -38.5; 17.5..26.5: +2.1; 35.5..44.5: +4.0; 53.5..62.5: +7.2; 71.5..80.5: +4.7; 86.5..92.5: +1.3; 98.5..110.5: +18.6)

## 7. The usual play

Each choice against the most common one in that kind of decision, in win-chance points over the decision's window, adjusted for the situation, with a 90% range from resampling whole matches. CLEAR = the range excludes 0. Win chance comes from a model that never saw the match. The same comparison over the 30 s BEFORE the decision is a placebo test: a choice can't cause what came before it, so a clear difference there means the effect is partly who makes that choice.

**after wipe** (41 decisions, 20 matches; usual: pushed the pit)
- took the flag (n 7): -1.3 [-20.8, +29.9]; in the 30 s before: +7.6 [-4.7, +20.2]

**boost clock** (88 decisions, 24 matches; usual: not running, fought)
- running, fought (n 18): +1.4 [-7.4, +10.5]; in the 30 s before: +1.1 [-3.3, +7.9]
- not running, advanced (n 14): +2.3 [-8.8, +14.9]; in the 30 s before: -3.6 [-10.2, +8.6]
- running, advanced (n 12): +0.4 [-14.4, +15.4]; in the 30 s before: -3.8 [-10.1, +4.5]
- not running, fell back (n 10): -3.0 [-14.5, +11.3]; in the 30 s before: +1.9 [-4.2, +9.9]
- not running, held (n 6): -12.5 [-47.2, +10.7]; in the 30 s before: +8.8 [-2.7, +31.6]

**enemy pickup** (387 decisions, 24 matches; usual: already running, fought)
- held, fought (n 59): +0.9 [-4.5, +6.4]; in the 30 s before: +2.0 [-4.1, +7.1]
- already running, advanced (n 42): +1.9 [-6.4, +8.4]; in the 30 s before: +2.2 [-3.4, +7.2]
- held, fell back (n 32): +2.6 [-6.8, +10.2]; in the 30 s before: +0.7 [-6.3, +8.1]
- already running, fell back (n 31): +0.4 [-5.1, +4.5]; in the 30 s before: -3.3 [-7.4, +2.5]
- ran, fought (n 31): +1.9 [-4.3, +8.5]; in the 30 s before: -0.4 [-8.6, +8.8]
- held, advanced (n 27): -0.6 [-7.9, +6.2]; in the 30 s before: +1.3 [-4.7, +8.6]
- ran, fell back (n 26): -1.0 [-8.2, +8.6]; in the 30 s before: +0.3 [-4.9, +3.4]
- ran, advanced (n 26): -2.6 [-9.8, +5.2]; in the 30 s before: +6.8 [+1.3, +12.6] ALREADY DIFFERENT BEFORE: partly who chooses it
- already running, held (n 14): -0.5 [-10.9, +9.8]; in the 30 s before: -7.8 [-16.6, +2.3]
- ran, held (n 7): -12.8 [-31.8, +6.4]; in the 30 s before: -2.8 [-18.5, +5.8]
- held, held (n 5): -9.5 [-25.8, +37.7]; in the 30 s before: -12.9 [-58.5, +2.1]

- **late_game**: not enough decisions yet (11)
**power play** (274 decisions, 24 matches; usual: pushed, advanced)
- pushed, fought (n 77): -0.3 [-6.3, +4.3]; in the 30 s before: +0.8 [-2.4, +4.5]
- held, fought (n 56): -3.5 [-7.2, +0.1]; in the 30 s before: +1.3 [-1.5, +5.2]
- held, fell back (n 20): -1.7 [-6.7, +4.1]; in the 30 s before: -8.8 [-16.8, -2.6] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, advanced (n 9): +6.9 [+0.0, +17.2] CLEAR; in the 30 s before: -6.0 [-10.6, -2.2] ALREADY DIFFERENT BEFORE: partly who chooses it
- pushed, fell back (n 7): -2.7 [-18.7, +13.0]; in the 30 s before: -2.0 [-8.2, +5.0]

**split in base** (66 decisions, 17 matches; usual: collapsed)
- defended without a collapse (n 24): +8.0 [-8.1, +17.2]; in the 30 s before: -2.3 [-7.9, +4.4]
- missed (n 6): -8.2 [-27.7, +4.4]; in the 30 s before: -2.5 [-7.7, +6.6]

**Collapses on a split: time away and its cost** (`S32`; per collapse, averages; main = what the main fight lost while the collapsers were away)

| Group | Cases | Away (median s) | Split killed | Collapser died | Own deaths at main | Enemy deaths at main | Flag lead change | DP change | Win change |
|---|---|---|---|---|---|---|---|---|---|
| all | 38 | 16 | 6 | 2 | 0.47 | 0.16 | -0.8 | -0.5 | -1.9 |
| away under 30 s | 26 | 8 | 6 | 0 | 0 | 0.15 | -2.8 | +1.0 | -1.8 |
| away 30 to 60 s | 7 | 44 | 0 | 1 | 0.29 | 0.14 | +23.1 | -4.3 | +5.3 |
| away 60 s or more | 5 | 90 | 0 | 1 | 3.2 | 0.2 | -24 | -3 | -12.2 |
| before 20:00 | 32 | 15.5 | 2 | 1 | 0.28 | 0.09 | +0.7 | -3.8 | -1.8 |
| from 20:00 | 6 | 17 | 4 | 1 | 1.5 | 0.5 | -8.8 | +16.7 | -1.9 |
| split member killed | 6 | 6 | 6 | 0 | 0 | 0.67 | -3.3 | +4.2 | -0.6 |
| no kill | 32 | 17 | 0 | 2 | 0.56 | 0.06 | -0.4 | -1.4 | -2.1 |

**Leverage: where the choice matters most** (share of the spread in win-chance change explained by the choice beyond the situation; range = best minus worst choice, in points)

- split in base (66): choice explains 6.3% (situation 14.1%); range 16.2 points, best defended without a collapse, worst missed
- boost clock (88): choice explains 4.0% (situation 5.4%); range 14.8 points, best not running, advanced, worst not running, held
- enemy pickup (387): choice explains 1.3% (situation 4.5%); range 12.9 points, best already running, advanced, worst ran, held
- power play (274): choice explains 1.3% (situation 0.8%); range 9.9 points, best held, advanced, worst held, fought
- after wipe (41): choice explains 0.0% (situation 36.1%); range 1.3 points, best pushed the pit, worst took the flag

**Behaviour clusters: what teams actually did** (each decision's response grouped by what every player did in the next 20 s; UNNAMED = a group no single named choice covers: a response for Denning to name or reject)

*after wipe* (4 groups, separation 0.27):
- n 24: fought (midline, 2.2 of 8), fought (backline, 1.3 of 8), held (backline, 0.8 of 8), held (midline, 0.8 of 8); named as {'pushed the pit': 21, 'took the flag': 2, 'reset': 1}; win change -0.1
- n 16: advanced (midline, 2.3 of 8), advanced (backline, 2.0 of 8), advanced (frontline, 1.4 of 8), fell back (backline, 0.6 of 8); named as {'pushed the pit': 8, 'took the flag': 5, 'reset': 3}; win change 0.7 UNNAMED
- n 4: advanced (backline, 6.2 of 8), advanced (midline, 1.0 of 8); named as {'pushed the pit': 4}; win change -24.7
- n 1: died (midline, 6.9 of 8), died (backline, 1.1 of 8); named as {'pushed the pit': 1}; win change -68.3
*boost clock* (5 groups, separation 0.19):
- n 34: fought (backline, 2.0 of 8), fought (midline, 1.9 of 8), fought (frontline, 1.3 of 8); named as {'not running, fought': 20, 'running, fought': 14}; win change -5.3 UNNAMED
- n 31: advanced (backline, 1.7 of 8), advanced (midline, 1.5 of 8), advanced (frontline, 0.7 of 8), fought (midline, 0.7 of 8); named as {'not running, advanced': 14, 'running, advanced': 10, 'not running, fell back': 3}; win change -3.4 UNNAMED
- n 15: held (backline, 2.3 of 8), fought (frontline, 1.1 of 8), fought (midline, 1.0 of 8); named as {'not running, fought': 6, 'not running, held': 4, 'running, fought': 3}; win change -2.5 UNNAMED
- n 10: fell back (backline, 2.8 of 8), fell back (midline, 1.0 of 8), fell back (frontline, 0.8 of 8), fought (midline, 0.7 of 8); named as {'not running, fell back': 5, 'running, fell back': 3, 'running, advanced': 1}; win change -2.5 UNNAMED
- n 7: died (backline, 1.7 of 8), died (midline, 1.1 of 8), to the spawn (backline, 1.0 of 8), held (midline, 0.9 of 8); named as {'not running, held': 2, 'running, to the spawn': 2, 'not running, fell back': 1}; win change -3.1 UNNAMED
*enemy pickup* (2 groups, separation 0.19):
- n 284: fought (midline, 1.5 of 8), fought (backline, 1.0 of 8), held (backline, 0.9 of 8), fell back (backline, 0.8 of 8); named as {'already running, fought': 81, 'held, fought': 55, 'held, fell back': 32}; win change 0.0 UNNAMED
- n 106: advanced (backline, 2.1 of 8), advanced (midline, 1.9 of 8), advanced (frontline, 0.8 of 8), carrying (midline, 0.6 of 8); named as {'already running, advanced': 40, 'held, advanced': 26, 'ran, advanced': 24}; win change -0.8 UNNAMED
*power play* (2 groups, separation 0.26):
- n 176: fought (midline, 1.6 of 8), fought (backline, 1.5 of 8), fought (frontline, 1.0 of 8), held (backline, 0.7 of 8); named as {'pushed, fought': 76, 'held, fought': 55, 'held, fell back': 20}; win change -0.2 UNNAMED
- n 107: advanced (backline, 2.5 of 8), advanced (midline, 2.1 of 8), advanced (frontline, 1.0 of 8), fought (midline, 0.5 of 8); named as {'pushed, advanced': 97, 'held, advanced': 7, 'pushed, fought': 1}; win change 1.3
*split in base* (4 groups, separation 0.22):
- n 33: fought (midline, 1.9 of 8), fought (backline, 1.0 of 8), held (backline, 0.9 of 8), fought (frontline, 0.9 of 8); named as {'defended without a collapse': 18, 'collapsed': 14, 'missed': 1}; win change 2.9 UNNAMED
- n 24: fell back (midline, 2.4 of 8), fell back (backline, 1.5 of 8), fell back (frontline, 1.0 of 8); named as {'collapsed': 17, 'defended without a collapse': 4, 'missed': 3}; win change -4.3
- n 7: advanced (backline, 3.4 of 8), advanced (midline, 1.3 of 8), fought (midline, 0.7 of 8), advanced (frontline, 0.6 of 8); named as {'collapsed': 5, 'missed': 1, 'defended without a collapse': 1}; win change 6.7
- n 2: died (midline, 7.0 of 8), died (backline, 1.0 of 8); named as {'defended without a collapse': 1, 'missed': 1}; win change -1.8 UNNAMED

## 8. What results and causes are worth

Win points for the team it happened to, from 24 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 79 | +1.0 | -14.4 to +13.3 | +2.1 | no |
| capture | 303 | +3.5 | +1.2 to +5.9 | +4.7 | yes |
| death (any) | 467 | -5.8 | -10.7 to -1.8 | -5.3 | yes |
| death: against a spike build | 152 | -2.1 | -6.7 to +6.2 | -2.8 | no |
| death: against other builds | 315 | -7.7 | -14.7 to -1.7 | -6.6 | yes |
| death: back within 20 s | 76 | -3.4 | -9.6 to +4.0 | -3.9 | no |
| death: down 20 to 60 s | 166 | -7.3 | -14.2 to -0.2 | -4.8 | yes |
| death: down 60 s or more | 225 | -5.6 | -12.3 to +0.3 | -6.3 | no |
| death: healer | 173 | -4.0 | -8.8 to +0.8 | -5.0 | no |
| death: healer in own base or pit, back within 15 s (likely deliberate) | 11 | +3.0 | -10.0 to +22.9 | -0.9 | no |
| death: healer, other | 162 | -4.5 | -9.2 to +0.1 | -5.3 | no |
| death: not a healer | 294 | -6.9 | -12.6 to -1.8 | -5.5 | yes |
| pit NPC lost (any): taken by a spike build | 47 | -1.2 | -8.5 to +11.0 | -1.4 | no |
| pit NPC lost (any): taken by other builds | 161 | -3.9 | -10.4 to +2.7 | +0.8 | no |
| pit NPC lost: archer | 118 | -1.4 | -6.4 to +4.1 | -0.5 | no |
| pit NPC lost: bodyguard | 29 | -4.4 | -11.0 to +1.8 | -1.0 | no |
| pit NPC lost: knight | 61 | -6.5 | -15.7 to +2.0 | +2.4 | no |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value.

*deaths* (per 10 s in that state; result worth -5.8 points, base rate 1.2%):

- own minus enemy team strength -302.5 to -159: result chance +1.5 points, worth -0.08 win points
- enemies within 1,500 7.5 to 8: result chance +2.1 points, worth -0.12 win points
- current health % 1 to 47.5: result chance +8.8 points, worth -0.51 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +4.8 points, worth -0.28 win points
- distance from its own pit 12950.5 to 18468: result chance +1.4 points, worth -0.08 win points
- match minute 21.95 to 28: result chance +1.5 points, worth -0.09 win points
- own healers alive within cast range 0 to 0.5: result chance +0.5 points, worth -0.03 win points
- maximum health after death penalty, as a share of normal 0.4 to 0.61: result chance +2.9 points, worth -0.17 win points

*kill conversion* (per burst, for the attacking team; result worth +5.8 points, base rate 29.1%):

- target's health ceiling 0.4 to 0.56: result chance +29.6 points, worth +1.72 win points
- target's healers in range 0 to 0.5: result chance +21.9 points, worth +1.27 win points
- attacking minus target team strength 426 to 682: result chance +14.2 points, worth +0.82 win points
- damage in the 2 s burst 521 to 728: result chance +15.5 points, worth +0.9 win points
- target health % when the burst started 0 to 39.5: result chance +20.9 points, worth +1.21 win points
- a prot on the target 0.5 to 1: result chance -7.1 points, worth -0.41 win points
- match minute 0.3 to 1.5: result chance -9.0 points, worth -0.52 win points
- interrupts on the attackers (5 s before to 2 s after) 1.5 to 2: result chance -20.9 points, worth -1.21 win points

*npc loss* (per case, for the defending team; result worth -3.3 points, base rate 17.1%):

- own players in the pit 7.5 to 8: result chance -14.5 points, worth +0.48 win points
- damage on the pit NPCs in the last 5 s 356.5 to 1170: result chance +30.1 points, worth -1.0 win points
- attacking minus defending team strength -682 to -377: result chance -10.6 points, worth +0.35 win points
- enemy players in the pit 7.5 to 8: result chance +18.9 points, worth -0.63 win points
- own players alive outside the pit 0 to 0.5: result chance +18.3 points, worth -0.61 win points
- attackers' measured damage per second against a Lord (benchmarks) 21.8 to 24.35: result chance -6.0 points, worth +0.2 win points
- own pit archers alive 2.5 to 3: result chance +21.1 points, worth -0.7 win points
- healing on own pit NPCs and Lord in the last 10 s 454.5 to 594: result chance -4.9 points, worth +0.16 win points

## 9. For Denning

- Which curves look wrong to you? A correction (direction, cap, drop, or a pair to always test) is logged with your reason and tested on held-out matches.
- Do any surprises remind you of something the variables don't capture (a missing variable)?
- Any variable you think matters that isn't listed?

