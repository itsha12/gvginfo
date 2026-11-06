# Learning report, batch 2

Trained on 34 matches (4 new in this batch). Variables in use: 20; build variables from 60 matches, interactions from 40.

## 0. Data integrity

- Lengths repaired: 2 (1f65fd3b 150 s -> 1027 s) (bbef1904 617 s -> 599 s) 
- Matches with a team's Lord damage not observed (left blank, not zero): 2
- Pit NPCs added from the standard roster (never seen in the replay): 107 in 28 matches
- Left out of training: 0

## 1. The honest test

**Not yet better than strength alone: treat the curves as noise.** Held-out accuracy (matches held out whole), log loss in brackets (lower is better):

- strength only: all 66% (0.514), 0-5 min 76% (0.43), 5-10 min 70% (0.504), 10-15 min 61% (0.586), 15-end min 55% (0.574), matches lasting 15 min+ 59% (0.603), matches even on strength (gap under 200) 44% (0.699)
- glass box: all 75% (0.581), 0-5 min 77% (0.475), 5-10 min 78% (0.457), 10-15 min 71% (0.711), 15-end min 74% (0.74), matches lasting 15 min+ 69% (0.71), matches even on strength (gap under 200) 63% (0.909)
- black box: all 57% (1.544), 0-5 min 59% (1.488), 5-10 min 58% (1.508), 10-15 min 58% (1.572), 15-end min 53% (1.631), matches lasting 15 min+ 50% (1.808), matches even on strength (gap under 200) 44% (1.999)
- Gain over strength alone (log loss, resampling whole matches): -0.067 (90% range -0.306 to +0.141).
- Change since batch 1: glass box log loss 0.657 -> 0.581; strength only 0.562 -> 0.514.

## 2. What it leans on

- **morale_diff** 1.191 (was 1.146): own minus enemy morale summed over players (boosts +, death penalty -)
- **stand** 0.298 (was 0.309): who holds the flag stand: 1 own, 0 nobody, -1 enemy
- **main_diff** 0.281 (was 0.28): own minus enemy players in each team's main group
- **spike_killable_diff** 0.273 (was 0.301): enemy minus own players within one spike of the other side (DP stacking; 0 unless a spike build is involved)
- **lord_damage_diff** 0.206 (was 0.234): own minus enemy Lord damage dealt so far (the 28:00 tiebreak; players can't see it); blank when either team's Lord damage wasn't observed
- **flag_lead** 0.205 (was 0.281): seconds up (+) or down (-) on flags: enemy's response minus own on the next capture exchange
- **boost_clock** 0.191 (was 0.172): seconds until the stand holder's next boost (+ if own boost is coming, - if the enemy's, 0 nobody)
- **down_diff_s** 0.189 (was 0.163): enemy minus own seconds until all dead players are back (+ = the enemy has more time down)
- **fight_state** 0.189 (was 0.146): who is winning the fight now: enemy minus own expected deaths in the next 10 s, from a deaths model that never saw the match (fightstate.py)
- **pit_pressure_diff** 0.188 (was 0.168): own players in the enemy pit minus enemy players in the own pit
- **archers_diff** 0.161 (was 0.154): own minus enemy pit archers alive
- **carrying_diff** 0.114 (was 0.117): own minus enemy players carrying a flag

## 3. The curves in words

Points = win-chance points added to an otherwise even game at each range of the variable.

- **morale_diff** rises from -44.0 to +43.0 points (-470.0..-199.0: -44.0; -154.0..-110.5: -40.7; -89.0..-46.5: -27.7; -15.5..-1.0: -2.2; 1.0..15.5: +3.2; 56.0..97.0: +29.8; 139.5..187.5: +42.4)
- **stand** rises from -7.8 to +7.8 points (-1.0..-0.5: -7.8; -0.5..0.5: +0.2; 0.5..1.0: +7.8)
- **main_diff** rises from -21.6 to +20.2 points (-8.0..-4.5: -21.6; -3.5..-2.5: -10.9; -1.5..-0.5: -7.1; 0.5..1.5: +7.3; 2.5..3.5: +10.5; 4.5..8.0: +20.2)
- **spike_killable_diff** rises from -29.1 to +30.5 points (-8.0..-7.5: -29.1; -5.5..-3.5: -31.0; -2.5..-1.5: -26.1; -0.5..0.5: -0.0; 1.5..2.5: +26.0; 4.5..7.5: +30.2)
- **lord_damage_diff** falls from +49.2 to -48.8 points (-9661.0..-4893.5: +49.2; -2590.5..-1323.5: +1.7; -631.0..-146.5: +0.4; -95.5..-2.5: -1.4; 2.5..95.5: +1.6; 161.0..784.0: -0.8; 1960.0..4259.0: -4.2)
- **flag_lead** falls from +19.1 to -20.9 points (-86.0..-70.5: +19.1; -55.5..-43.5: +0.6; -31.5..-20.5: -0.1; -10.5..-0.5: +0.3; 9.5..20.5: +0.5; 31.5..43.5: +0.2; 55.5..70.5: -10.8)
- **boost_clock** rises from -6.1 to +5.2 points (-120.0..-109.5: -6.1; -98.5..-85.5: -5.4; -71.5..-54.5: -4.6; -32.5..-0.5: -3.1; 9.5..42.5: +4.6; 64.5..81.5: +5.5; 95.5..108.5: +5.6)
- **down_diff_s** rises from -35.1 to +39.6 points (-960.0..-195.0: -35.1; -127.5..-97.5: -13.0; -67.5..-52.5: -7.3; -37.5..-7.5: -3.1; 7.5..52.5: +1.7; 67.5..82.5: +8.3; 97.5..142.5: +13.6)
- **fight_state** falls from +10.4 to -7.7 points (-3.29..-0.28: +10.4; -0.12..-0.06: +4.6; -0.03..-0.02: +4.7; -0.01..-0.0: +1.7; 0.01..0.02: -3.9; 0.03..0.06: -4.5; 0.12..0.28: -5.5)
- **pit_pressure_diff** rises from -13.3 to -6.6 points (-8.0..-5.5: -13.3; -4.5..-3.5: +15.0; -2.5..-1.5: +12.8; -0.5..0.5: +0.7; 1.5..2.5: -10.4; 3.5..5.5: -10.2)

## 4. Discovery

**Interaction candidates** (a screen: pairs whose combination seems to matter beyond each alone; untested until held-out matches confirm them; switched on in the model from 40 matches):

- morale_diff with spike_killable_diff (screen 0.161)
- alive_diff with morale_diff (screen 0.155)
- down_diff_s with morale_diff (screen 0.155)
- morale_diff with lord_exposed_diff (screen 0.150)
- morale_diff with lord_damage_diff (screen 0.147)
- morale_diff with bodyguard_diff (screen 0.146)
- main_diff with morale_diff (screen 0.146)
- morale_diff with knights_diff (screen 0.138)

**Candidate variables** (proposed variables, tested on unseen matches; log loss, lower is better):

- split_diff: 0.581 without, 0.633 with: does not improve yet. own minus enemy players on a split (away from their main group on the enemy half, not carrying). Proposed batch 1 by Claude: the knights curve runs backwards, maybe standing in for the cost of splitting

**Surprises** (moments where the held-out model was most confident about the team that went on to lose; each points to something the variables don't capture yet):

- hdm v HC (28447c4a) at 14:15: a model that never saw this match gave HC 0.1%, and HC won. Why it thought so: lord_damage_diff -35.7, morale_diff -30.7, knights_diff -29.4, bodyguard_diff -26.3, lord_exposed_diff -24.1
- RACK v hdm (1f65fd3b) at 10:45: a model that never saw this match gave RACK 1.3%, and RACK won. Why it thought so: morale_diff -43.2, knights_diff -14.3, team strength -14.0, stand -10.2, fight_state -5.6
- hdm v Men (0f1fd794) at 28:00: a model that never saw this match gave Men 1.3%, and Men won. Why it thought so: lord_damage_diff -49.3, morale_diff +24.5, bodyguard_diff -18.7, lord_health_diff +15.9, main_diff -12.2
- Men v HC (faec428a) at 15:45: a model that never saw this match gave HC 93.8%, and HC lost. Why it thought so: main_diff +29.0, alive_diff +22.7, morale_diff +20.1, team strength -14.9, lord_exposed_diff +14.0
- OG v hold (49eec28d) at 3:45: a model that never saw this match gave OG 0.4%, and OG won. Why it thought so: morale_diff -42.1, pit_pressure_diff -40.5, flag_lead -21.6, team strength +19.0, main_diff -10.5
- Team v push (2df9b7fd) at 15:15: a model that never saw this match gave Team 1.4%, and Team won. Why it thought so: team strength +48.1, spike_killable_diff -47.6, main_diff -38.9, archers_diff -15.0, carrying_diff +11.5

## 5. Denning's rulings seen through the model

Win chance from a model that never saw the match, 20 s before and 60 s after each ruled moment. Contributions are points for an otherwise even game (the curves' scale).

- hdm v HC (28447c4a) 5:01 (split answered), HC: 33.6% 20 s before -> 51.6% 60 s after (+18.0). After: knights_diff -29.4, team strength -16.4, flag_lead -15.1, pit_pressure_diff +12.7
- hdm v HC (28447c4a) 5:01 (split answered), hdm: 69.1% 20 s before -> 53.1% 60 s after (-16.0). After: knights_diff +28.9, team strength +16.4, flag_lead +14.2, carrying_diff -11.9
- hdm v HC (28447c4a) 1:02 (split detection), HC: 37.2% 20 s before -> 27.3% 60 s after (-9.9). After: team strength -16.4, flag_lead +14.2, carrying_diff -11.9, stand -9.2
- hdm v HC (28447c4a) 1:02 (split detection), hdm: 64.3% 20 s before -> 73.0% 60 s after (+8.7). After: team strength +16.4, flag_lead -15.1, carrying_diff +10.4, stand +9.1
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), HC: 6.5% 20 s before -> 4.1% 60 s after (-2.4). After: knights_diff -29.4, bodyguard_diff -26.3, lord_exposed_diff -24.1, team strength -16.4
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), hdm: 95.3% 20 s before -> 97.9% 60 s after (+2.6). After: bodyguard_diff +31.6, knights_diff +28.9, team strength +16.4, lord_exposed_diff +16.0
- hdm v HC (bbef1904) 8:10 (death), HC: 46.9% 20 s before -> 5.9% 60 s after (-41.0). After: morale_diff -27.7, down_diff_s -16.4, team strength -16.0, fight_state +15.1
- hdm v HC (bbef1904) 8:10 (death), hdm: 56.4% 20 s before -> 98.8% 60 s after (+42.4). After: down_diff_s +36.2, morale_diff +29.4, team strength +16.0, main_diff +11.9
- Men v HC (faec428a) 9:31 (death), HC: 22.2% 20 s before -> 20.7% 60 s after (-1.5). After: team strength -14.9, stand -7.9, fight_state -4.4, boost_clock -3.6
- Men v HC (faec428a) 9:31 (death), Men: 74.7% 20 s before -> 77.9% 60 s after (+3.2). After: team strength +14.9, stand +8.0, boost_clock +3.7, morale_diff +3.5

## 6. Why: the node models

Each explains one result from what happened before it (time order enforced), tested on matches it never saw. AUC = how often a moment that led to the result scores above one that didn't (0.5 = guessing, 1 = perfect).

**deaths** (34 matches, 81079 moments, 2099 results): adds to the simple baseline (AUC 0.899 against 0.77 for health_pct and damage_taken_3s alone).
- **enemies_near** (enemies within 1,500) rises from -18.5 to +23.3 points (0.0..0.5: -18.5; 0.5..1.5: -7.4; 1.5..2.5: -1.1; 2.5..3.5: +0.8; 3.5..4.5: +5.8; 4.5..5.5: +10.2; 5.5..6.5: +12.1; 6.5..7.5: +14.2; 7.5..8.0: +23.3)
- **strength_gap** (own minus enemy team strength) falls from +14.6 to -14.5 points (-721.0..-415.5: +14.6; -332.5..-285.5: +11.4; -140.5..-111.0: +0.0; -86.5..-17.5: +8.1; 17.5..102.5: -1.5; 117.5..267.5: -10.5; 332.5..415.5: -13.9)
- **health_pct** (current health %) falls from +40.6 to -6.0 points (1.0..48.5: +40.6; 60.5..68.5: +22.3; 74.5..78.5: +10.9; 82.5..85.5: +5.7; 88.5..91.5: +1.6; 93.5..95.5: -1.5; 97.5..99.5: -4.7)
- **local_diff** (allies minus enemies within 2,000) falls from +29.7 to -16.3 points (-8.0..-3.5: +29.7; -2.5..-1.5: +12.1; -0.5..0.5: -6.7; 1.5..2.5: -7.1; 3.5..4.5: +16.9; 5.5..7.0: -16.3)
- **health_ceiling** (maximum health after death penalty, as a share of normal) falls from +33.8 to -10.0 points (0.4..0.67: +33.8; 0.71..0.84: +22.4; 0.85..0.9: +14.7; 0.94..0.99: +7.2; 1.0..1.1: -2.6)
- **healers_in_range** (own healers alive within cast range) falls from +11.7 to -3.0 points (0.0..0.5: +11.7; 0.5..1.5: -2.9; 1.5..2.5: -5.7; 2.5..3.0: -3.0)
- **minute** (match minute) rises from -4.5 to +15.6 points (0.1..1.25: -4.5; 2.35..3.45: -4.8; 4.65..5.75: +4.4; 7.15..8.65: +4.9; 10.35..12.05: -4.4; 13.85..15.95: -0.4; 18.45..21.25: +9.9)
- **dist_own_pit** (distance from its own pit) rises from +3.5 to +17.9 points (10.0..1506.5: +3.5; 2509.5..4289.5: -5.6; 5437.5..6285.5: -7.3; 7089.5..7724.5: -2.3; 8339.5..8915.5: -3.3; 9738.5..10657.5: -0.3; 11856.5..13157.5: +8.4)

**kill conversion** (34 matches, 634 moments, 183 results): adds to the simple baseline (AUC 0.788 against 0.673 for burst_damage and target_health_pct alone).
- **burst_damage** (damage in the 2 s burst) rises from -6.6 to +24.7 points (250.0..257.5: -6.6; 267.5..280.5: -13.3; 289.5..302.5: -7.8; 318.5..331.5: -6.0; 351.0..372.5: -3.2; 404.5..434.0: +1.0; 476.0..547.5: +24.3)
- **target_ceiling** (target's health ceiling) falls from +32.4 to -20.1 points (0.4..0.56: +32.4; 0.68..0.71: +23.8; 0.83..0.86: +18.0; 0.91..0.92: +5.7; 0.94..0.95: +2.1; 0.98..1.02: -2.5; 1.08..1.1: -20.1)
- **target_healers_in_range** (target's healers in range) falls from +30.5 to -4.2 points (0.0..0.5: +30.5; 0.5..1.5: -0.3; 1.5..2.5: -9.5; 2.5..3.0: -4.2)
- **target_health_pct** (target health % when the burst started) falls from +21.5 to -6.8 points (0.0..43.0: +21.5; 54.5..61.5: +16.2; 67.5..72.5: +5.7; 75.5..78.5: +3.6; 81.5..85.5: -8.3; 88.5..92.5: -12.6; 96.5..99.5: -7.6)
- **minute** (match minute) rises from -18.2 to +13.0 points (0.3..1.45: -18.2; 2.75..3.95: -3.3; 4.95..6.25: -3.9; 7.45..8.6: -2.9; 10.45..12.4: -1.0; 14.25..15.95: +8.9; 18.0..21.15: +12.3)
- **target_prot_up** (a prot on the target) falls from +4.8 to -10.7 points (0.0..0.5: +4.8; 0.5..1.0: -10.7)
- **strength_gap** (attacking minus target team strength) rises from -8.1 to +19.5 points (-721.0..-360.0: -8.1; -267.5..-128.5: -6.4; -111.0..-10.0: -2.5; 0.0..86.5: +2.6; 116.0..140.5: -4.6; 252.5..267.5: -7.7; 360.0..426.0: +3.6)
- **attackers_interrupted** (interrupts on the attackers (5 s before to 2 s after)) falls from +2.0 to -30.5 points (0.0..0.5: +2.0; 0.5..1.5: -15.5; 1.5..2.0: -30.5)

**flag answer** (seconds an answer to an enemy capture was slower than possible; 31 matches, 337 rows): adds to the simple baseline (typical error 17.1s against 26.2s for the median; explains 67% of the spread).
- **parked_s** (seconds the flag lay parked (dropped 5 s or more: not running yet)): 0.0..3.5: -5.1 s; 11.5..15.5: +1.9 s; 22.0..29.0: +16.5 s; 34.5..38.5: +33.0 s; 48.0..59.5: +42.0 s; 76.5..95.0: +53.5 s; 117.5..259.0: +61.2 s
- **own_deaths_during** (own deaths during the answer): 0.0..0.5: -3.8 s; 0.5..1.5: +7.7 s; 1.5..2.5: +10.5 s; 2.5..4.5: +28.3 s; 4.5..5.5: +43.2 s; 5.5..6.5: +56.6 s; 6.5..8.0: +67.4 s; 8.0..11.0: +78.7 s
- **enemies_in_the_way** (enemy presence along the runner's trip back to the spawn): 0.0..0.5: -5.0 s; 3.5..8.0: -3.2 s; 12.5..17.5: -1.3 s; 22.5..29.0: +0.0 s; 46.5..54.5: +3.5 s; 68.5..92.5: +6.1 s; 123.0..177.5: +11.7 s
- **carrier_damage_taken** (damage the carrier took while carrying): 0.0..2.0: -3.0 s; 26.5..50.5: -4.0 s; 74.0..98.5: -2.6 s; 135.5..189.5: +0.1 s; 248.5..293.5: +1.9 s; 391.5..506.5: +4.8 s; 603.5..1015.5: +8.7 s
- **enemy_deaths_during** (enemy deaths during the answer): 0.0..0.5: -2.2 s; 0.5..1.5: +8.4 s; 1.5..2.5: +11.3 s; 2.5..3.5: +15.1 s; 3.5..4.5: +27.4 s; 4.5..5.0: +17.1 s
- **quick_handoffs** (quick hand-offs (a teammate picked it up within 5 s)): 0.0..0.5: -2.3 s; 0.5..1.5: +6.4 s; 1.5..2.5: +12.7 s; 2.5..3.0: +24.7 s
- **runner_to_spawn** (runner's distance to its flag spawn when the enemy captured): 64.0..895.5: -6.3 s; 1472.5..2149.5: -4.5 s; 3384.5..4280.0: -1.8 s; 4826.5..5494.5: +2.3 s; 6181.5..6758.0: +3.0 s; 7311.5..7832.5: +1.9 s; 8448.5..9165.5: +3.4 s
- **possible_s** (fastest possible answer (s) from the flag model at the enemy's capture): 0.0..3.5: -0.3 s; 7.5..14.5: +1.8 s; 22.5..27.5: +1.2 s; 32.5..35.5: +2.8 s; 39.5..43.5: +2.8 s; 48.5..54.5: +0.4 s; 62.5..71.5: -5.0 s
- **forced_drops** (drops with the carrier hit in the 5 s before, or dying): 0.0..0.5: -1.2 s; 0.5..1.5: +12.6 s; 1.5..2.5: +9.7 s; 2.5..3.0: +9.7 s
- **flag_lead_at_enemy_cap** (own flag lead when the enemy captured): -81.0..-73.5: -6.7 s; -61.5..-54.5: -1.0 s; -42.5..-34.5: +2.2 s; -27.5..-18.5: +1.4 s; -10.5..-3.5: +2.4 s; 10.5..18.5: +0.8 s; 32.5..55.5: +0.5 s

**npc loss** (34 matches, 4020 moments, 679 results): adds to the simple baseline (AUC 0.798 against 0.761 for attackers and defenders alone).
- **defenders** (own players in the pit) falls from +37.5 to -43.9 points (0.0..0.5: +37.5; 0.5..1.5: +25.2; 1.5..2.5: +21.9; 2.5..3.5: -1.1; 3.5..4.5: -15.6; 4.5..5.5: -16.6; 5.5..6.5: -17.8; 6.5..7.5: -36.7; 7.5..8.0: -43.9)
- **npc_damage_5s** (damage on the pit NPCs in the last 5 s) rises from -15.8 to +31.7 points (0.0..0.5: -15.8; 23.5..39.5: -0.4; 53.5..71.5: +4.1; 90.5..111.5: +11.6; 134.5..158.5: +23.1; 186.5..225.5: +26.4; 279.5..375.5: +29.4)
- **defenders_elsewhere** (own players alive outside the pit) falls from +27.8 to -5.3 points (0.0..0.5: +27.8; 0.5..1.5: +10.5; 1.5..2.5: +13.5; 2.5..3.5: +6.2; 3.5..4.5: -3.2; 4.5..5.5: -7.8; 5.5..6.5: -17.7; 6.5..7.5: -16.6; 7.5..8.0: -5.3)
- **attackers** (enemy players in the pit) rises from -13.5 to +22.2 points (1.0..1.5: -13.5; 1.5..2.5: -9.2; 2.5..3.5: -6.5; 3.5..4.5: +4.8; 4.5..5.5: +16.3; 5.5..6.5: +18.6; 6.5..7.5: +20.5; 7.5..8.0: +22.2)
- **strength_gap** (attacking minus defending team strength) rises from -23.0 to +7.4 points (-682.0..-415.5: -23.0; -332.5..-267.5: -9.9; -117.5..-17.5: -3.0; 57.5..102.5: -1.7; 106.0..210.5: +15.0; 285.5..303.5: +10.9; 360.0..426.0: +11.2)
- **archers** (own pit archers alive) rises from -8.1 to +25.1 points (0.0..0.5: -8.1; 0.5..1.5: -6.5; 1.5..2.5: +5.8; 2.5..3.0: +25.1)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -8.5 to +9.5 points (0.0..16.0: -8.5; 24.1..31.3: -6.1; 35.65..35.8: -3.6; 41.8..53.8: -3.5; 62.95..66.15: +5.9; 73.25..78.85: +7.6; 87.55..101.05: +6.0)
- **defender_healers** (of which healers) falls from +13.1 to +4.0 points (0.0..0.5: +13.1; 0.5..1.5: -4.5; 1.5..2.5: -4.9; 2.5..3.0: +4.0)

**lord damage** (Lord damage dealt in the next 10 s while players are in the enemy pit; 33 matches, 4730 rows): adds to the simple baseline (typical error 116.6 against 78.7 for the median; explains 34% of the spread).
- **defenders** (own players in the pit): 0.0..0.5: +182.4; 0.5..1.5: +88.8; 1.5..2.5: +28.0; 2.5..3.5: -25.7; 3.5..4.5: -60.2; 4.5..5.5: -106.7; 5.5..6.5: -126.1; 6.5..7.5: -126.2; 7.5..8.0: -107.6
- **defenders_elsewhere** (own players alive outside the pit): 0.0..0.5: +80.7; 0.5..1.5: +85.1; 1.5..2.5: +84.7; 2.5..3.5: +81.4; 3.5..4.5: +46.2; 4.5..5.5: +0.9; 5.5..6.5: -46.7; 6.5..7.5: -108.9; 7.5..8.0: -184.7
- **bodyguard** (own Bodyguard alive): 0.0..0.5: +124.6; 0.5..1.0: -41.8
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)): 0.0..15.4: -64.0; 23.85..31.3: -38.9; 35.65..35.8: -44.7; 41.8..55.9: -13.2; 63.8..68.45: +5.4; 75.15..78.85: +43.4; 87.55..101.05: +73.3
- **attackers** (enemy players in the pit): 1.0..1.5: -35.6; 1.5..2.5: -21.4; 2.5..3.5: -22.7; 3.5..4.5: -9.7; 4.5..5.5: +66.5; 5.5..6.5: +68.1; 6.5..7.5: +51.7; 7.5..8.0: +57.0
- **defender_healers** (of which healers): 0.0..0.5: +65.0; 0.5..1.5: +10.5; 1.5..2.5: -26.6; 2.5..3.0: -54.0
- **seconds_in_pit** (seconds the attackers have been in the pit): 0.0..4.5: -17.5; 10.5..16.5: -19.0; 22.5..28.5: -21.2; 37.5..46.5: -8.2; 58.5..73.5: +20.5; 88.5..106.5: +23.5; 130.5..181.5: +46.3
- **strength_gap** (attacking minus defending team strength): -682.0..-375.5: +19.8; -267.5..-117.5: +32.0; -17.5..57.5: +16.8; 102.5..106.0: -5.8; 128.5..267.5: -18.5; 301.0..332.5: -37.9; 386.0..511.5: -8.3
- **archers** (own pit archers alive): 0.0..0.5: -35.8; 0.5..1.5: -2.0; 1.5..2.5: +21.7; 2.5..3.0: -7.8
- **attackers_area_damage** (area-damage skills on the attackers' bars (Denning P9)): 0.0..0.5: +13.1; 0.5..1.0: -36.4

**lord kill** (33 matches, 4726 moments, 296 results): no better than the simple baseline yet (AUC 0.949 against 0.954 for attackers and defenders alone).
- **defenders** (own players in the pit) falls from +46.2 to -48.8 points (0.0..0.5: +46.2; 0.5..1.5: +44.1; 1.5..2.5: +29.3; 2.5..3.5: +6.9; 3.5..4.5: -35.0; 4.5..5.5: -44.6; 5.5..6.5: -47.9; 6.5..7.5: -48.2; 7.5..8.0: -48.8)
- **defenders_elsewhere** (own players alive outside the pit) falls from +46.9 to -49.2 points (0.0..0.5: +46.9; 0.5..1.5: +39.7; 1.5..2.5: +33.7; 2.5..3.5: +31.7; 3.5..4.5: +30.5; 4.5..5.5: +1.8; 5.5..6.5: -10.2; 6.5..7.5: -49.0; 7.5..8.0: -49.2)
- **attackers** (enemy players in the pit) rises from -37.8 to +41.7 points (1.0..1.5: -37.8; 1.5..2.5: -19.4; 2.5..3.5: -13.8; 3.5..4.5: +1.4; 4.5..5.5: +43.5; 5.5..6.5: +44.7; 6.5..7.5: +43.6; 7.5..8.0: +41.7)
- **minute** (match minute) rises from -44.7 to +31.8 points (0.6..2.75: -44.7; 3.95..5.05: -19.2; 6.15..7.25: +5.3; 8.85..10.35: +7.8; 11.95..14.05: +9.2; 15.85..18.45: +26.1; 20.55..23.55: +30.6)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -9.1 to +32.6 points (0.0..15.4: -9.1; 23.85..31.3: -32.8; 35.65..35.8: -30.6; 41.8..55.9: +10.0; 63.8..68.45: +11.7; 75.15..78.85: +22.4; 87.55..101.05: +16.6)
- **defender_healers** (of which healers) falls from +23.7 to -32.6 points (0.0..0.5: +23.7; 0.5..1.5: +13.3; 1.5..2.5: -11.0; 2.5..3.0: -32.6)
- **seconds_in_pit** (seconds the attackers have been in the pit) rises from +7.5 to +38.5 points (0.0..4.5: +7.5; 10.5..16.5: -13.1; 22.5..28.5: -21.1; 37.5..46.5: -20.7; 58.5..73.5: +1.7; 88.5..106.5: +4.0; 130.5..181.5: +32.5)
- **res_in** (seconds until the next res) rises from -42.3 to +14.3 points (1.0..8.5: -42.3; 17.5..26.5: +7.5; 35.5..44.5: +7.2; 53.5..62.5: +5.6; 71.5..77.5: +1.4; 83.5..92.5: +10.1; 101.5..110.5: +15.5)

## 7. The usual play

Each choice against the most common one in that kind of decision, in win-chance points over the decision's window, adjusted for the situation, with a 90% range from resampling whole matches. CLEAR = the range excludes 0. Win chance comes from a model that never saw the match. The same comparison over the 30 s BEFORE the decision is a placebo test: a choice can't cause what came before it, so a clear difference there means the effect is partly who makes that choice.

**after wipe** (74 decisions, 31 matches; usual: pushed the pit)
- took the flag (n 12): -7.1 [-17.9, +6.7]; in the 30 s before: +7.5 [-7.6, +21.8]
- reset (n 8): -0.5 [-6.3, +6.9]; in the 30 s before: +1.8 [-4.6, +6.0]

**boost clock** (129 decisions, 34 matches; usual: not running, fought)
- running, fought (n 24): +1.4 [-3.7, +8.7]; in the 30 s before: -2.7 [-8.3, +2.6]
- not running, advanced (n 19): -1.5 [-6.1, +6.1]; in the 30 s before: -0.3 [-6.9, +7.1]
- running, advanced (n 18): -0.6 [-10.8, +9.1]; in the 30 s before: +0.4 [-5.5, +4.3]
- not running, fell back (n 15): -8.2 [-17.5, -0.1] CLEAR; in the 30 s before: +0.9 [-4.4, +7.1]
- not running, held (n 7): -12.2 [-33.3, +2.4]; in the 30 s before: +4.0 [-9.5, +19.8]
  By fight state (fightstate.py; losing/winning = 0.25+ more expected deaths in the next 10 s; raw win-chance change, against the usual choice in the same band):
  - running, fought, losing the fight: too few yet (n 2 against 7; means 1.1 against -0.4)
  - running, fought, even fight: +0.4 (n 22 against 38)
  - not running, advanced, losing the fight: too few yet (n 1 against 7; means -0.6 against -0.4)
  - not running, advanced, even fight: -0.5 (n 15 against 38)
  - not running, advanced, winning the fight: too few yet (n 3 against 1; means 4.3 against -0.4)
  - running, advanced, even fight: -1.7 (n 18 against 38)
  - not running, fell back, losing the fight: too few yet (n 3 against 7; means -0.3 against -0.4)
  - not running, fell back, even fight: -12.7 (n 12 against 38)
  - not running, held, losing the fight: too few yet (n 3 against 7; means -5.1 against -0.4)
  - not running, held, even fight: too few yet (n 4 against 38; means -14.2 against -1.1)

**enemy pickup** (492 decisions, 33 matches; usual: already running, fought)
- held, fought (n 74): -0.2 [-6.8, +5.8]; in the 30 s before: +1.9 [-3.7, +6.0]
- already running, advanced (n 59): -0.3 [-8.1, +6.0]; in the 30 s before: +4.5 [-1.3, +8.9]
- held, fell back (n 41): -1.3 [-10.5, +5.6]; in the 30 s before: +0.3 [-5.8, +5.8]
- held, advanced (n 39): +1.6 [-4.5, +8.3]; in the 30 s before: -1.5 [-5.4, +1.6]
- already running, fell back (n 38): -3.3 [-7.1, +0.1]; in the 30 s before: -0.1 [-5.2, +4.3]
- ran, fell back (n 37): -4.1 [-8.5, +2.4]; in the 30 s before: +0.6 [-4.3, +5.2]
- ran, fought (n 37): -1.2 [-8.0, +6.4]; in the 30 s before: -1.0 [-8.6, +6.0]
- ran, advanced (n 30): +0.6 [-6.2, +8.7]; in the 30 s before: +5.8 [+0.8, +9.4] ALREADY DIFFERENT BEFORE: partly who chooses it
- already running, held (n 17): -1.7 [-7.9, +5.7]; in the 30 s before: -3.4 [-13.4, +5.6]
- ran, held (n 10): -2.7 [-15.5, +5.9]; in the 30 s before: -5.0 [-12.7, -0.1] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, held (n 8): -5.2 [-21.0, +13.9]; in the 30 s before: -1.2 [-12.9, +7.3]
  By fight state (fightstate.py; losing/winning = 0.25+ more expected deaths in the next 10 s; raw win-chance change, against the usual choice in the same band):
  - held, fought, losing the fight: too few yet (n 2 against 1; means 1.6 against -25.6)
  - held, fought, even fight: -6.0 (n 63 against 99)
  - held, fought, winning the fight: too few yet (n 9 against 2; means -0.1 against -15.1)
  - already running, advanced, losing the fight: too few yet (n 1 against 1; means -8.8 against -25.6)
  - already running, advanced, even fight: -1.7 (n 56 against 99)
  - already running, advanced, winning the fight: too few yet (n 2 against 2; means 1.0 against -15.1)
  - held, fell back, losing the fight: too few yet (n 4 against 1; means 0.9 against -25.6)
  - held, fell back, even fight: -6.2 (n 36 against 99)
  - held, fell back, winning the fight: too few yet (n 1 against 2; means 1.2 against -15.1)
  - held, advanced, losing the fight: too few yet (n 1 against 1; means 18.1 against -25.6)
  - held, advanced, even fight: -3.8 (n 30 against 99)
  - held, advanced, winning the fight: too few yet (n 8 against 2; means 0.7 against -15.1)
  - already running, fell back, losing the fight: too few yet (n 2 against 1; means -1.4 against -25.6)
  - already running, fell back, even fight: -3.7 (n 36 against 99)
  - ran, fell back, even fight: -6.1 (n 37 against 99)
  - ran, fought, losing the fight: too few yet (n 4 against 1; means -30.2 against -25.6)
  - ran, fought, even fight: -3.1 (n 33 against 99)
  - ran, advanced, losing the fight: too few yet (n 1 against 1; means -0.7 against -25.6)
  - ran, advanced, even fight: -1.8 (n 27 against 99)
  - ran, advanced, winning the fight: too few yet (n 2 against 2; means 16.1 against -15.1)
  - already running, held, even fight: -4.0 (n 17 against 99)
  - ran, held, even fight: -4.2 (n 10 against 99)
  - held, held, losing the fight: too few yet (n 1 against 1; means 0.1 against -25.6)
  - held, held, even fight: too few yet (n 7 against 99; means -5.3 against 3.1)

- **late_game**: not enough decisions yet (13)
**power play** (366 decisions, 34 matches; usual: pushed, advanced)
- pushed, fought (n 99): +3.1 [-1.8, +6.5]; in the 30 s before: -1.6 [-5.0, +1.6]
- held, fought (n 77): -2.1 [-4.8, +0.4]; in the 30 s before: -0.2 [-3.9, +2.7]
- held, fell back (n 31): -1.7 [-6.1, +2.4]; in the 30 s before: -9.2 [-18.5, -2.5] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, advanced (n 11): +2.8 [-1.9, +10.5]; in the 30 s before: -1.0 [-13.6, +9.0]
- pushed, fell back (n 8): -1.5 [-12.7, +13.0]; in the 30 s before: -2.8 [-8.9, +2.7]
- pushed, held (n 6): +4.1 [-1.8, +13.1]; in the 30 s before: -5.8 [-11.2, +1.3]
  By fight state (fightstate.py; losing/winning = 0.25+ more expected deaths in the next 10 s; raw win-chance change, against the usual choice in the same band):
  - pushed, fought, losing the fight: too few yet (n 3 against 3; means -0.3 against -18.3)
  - pushed, fought, even fight: +1.7 (n 82 against 106)
  - pushed, fought, winning the fight: +9.6 (n 14 against 25)
  - held, fought, losing the fight: too few yet (n 1 against 3; means 0.1 against -18.3)
  - held, fought, even fight: -2.9 (n 70 against 106)
  - held, fought, winning the fight: too few yet (n 6 against 25; means -2.9 against 3.4)
  - held, fell back, losing the fight: too few yet (n 2 against 3; means -16.0 against -18.3)
  - held, fell back, even fight: -0.8 (n 28 against 106)
  - held, fell back, winning the fight: too few yet (n 1 against 25; means 6.4 against 3.4)
  - held, advanced, even fight: too few yet (n 9 against 106; means 3.3 against 0.5)
  - held, advanced, winning the fight: too few yet (n 2 against 25; means 12.4 against 3.4)
  - pushed, fell back, even fight: too few yet (n 7 against 106; means -1.6 against 0.5)
  - pushed, fell back, winning the fight: too few yet (n 1 against 25; means 2.1 against 3.4)
  - pushed, held, even fight: too few yet (n 6 against 106; means 6.2 against 0.5)

**split in base** (82 decisions, 25 matches; usual: collapsed)
- defended without a collapse (n 32): +3.3 [-3.9, +10.8]; in the 30 s before: -1.2 [-5.1, +2.4]
- missed (n 9): -8.3 [-21.3, +1.5]; in the 30 s before: -1.3 [-6.7, +4.8]

**Collapses on a split: time away and its cost** (`S32`; per collapse, averages; main = what the main fight lost while the collapsers were away)

| Group | Cases | Away (median s) | Split killed | Collapser died | Own deaths at main | Enemy deaths at main | Flag lead change | DP change | Win change |
|---|---|---|---|---|---|---|---|---|---|
| all | 43 | 16 | 7 | 3 | 0.53 | 0.14 | -1.0 | -1.9 | -1.8 |
| away under 30 s | 29 | 9 | 7 | 0 | 0 | 0.14 | -3.8 | +0.9 | -1.9 |
| away 30 to 60 s | 8 | 43.5 | 0 | 1 | 0.25 | 0.12 | +22.5 | -3.8 | +5.7 |
| away 60 s or more | 6 | 89 | 0 | 2 | 3.5 | 0.17 | -18.7 | -12.5 | -11.1 |
| before 20:00 | 37 | 16 | 3 | 2 | 0.38 | 0.08 | +0.3 | -4.9 | -0.6 |
| from 20:00 | 6 | 17 | 4 | 1 | 1.5 | 0.5 | -8.8 | +16.7 | -9.2 |
| split member killed | 7 | 7 | 7 | 0 | 0 | 0.57 | -12 | +3.6 | -7.3 |
| no kill | 36 | 18.5 | 0 | 3 | 0.64 | 0.06 | +1.2 | -2.9 | -0.7 |

**Leverage: where the choice matters most** (share of the spread in win-chance change explained by the choice beyond the situation; range = best minus worst choice, in points)

- boost clock (129): choice explains 5.8% (situation 7.1%); range 13.6 points, best running, fought, worst not running, held
- split in base (82): choice explains 3.3% (situation 11.9%); range 11.6 points, best defended without a collapse, worst missed
- after wipe (74): choice explains 2.2% (situation 18.1%); range 7.1 points, best pushed the pit, worst took the flag
- power play (366): choice explains 1.9% (situation 3.0%); range 8.4 points, best pushed, held, worst held, fought
- enemy pickup (492): choice explains 0.9% (situation 5.9%); range 7.4 points, best held, advanced, worst held, held

**Behaviour clusters: what teams actually did** (each decision's response grouped by what every player did in the next 20 s; UNNAMED = a group no single named choice covers: a response for Denning to name or reject)

*after wipe* (2 groups, separation 0.3):
- n 47: fought (midline, 1.7 of 8), fought (backline, 1.6 of 8), held (backline, 0.9 of 8), fought (frontline, 0.8 of 8); named as {'pushed the pit': 40, 'took the flag': 4, 'reset': 3}; win change -0.3
- n 27: advanced (backline, 3.3 of 8), advanced (midline, 2.0 of 8), advanced (frontline, 1.3 of 8); named as {'pushed the pit': 14, 'took the flag': 8, 'reset': 5}; win change 0.3 UNNAMED
*boost clock* (5 groups, separation 0.2):
- n 48: fought (midline, 2.2 of 8), fought (backline, 2.2 of 8), fought (frontline, 1.2 of 8); named as {'not running, fought': 32, 'running, fought': 16}; win change -3.4
- n 40: advanced (backline, 2.0 of 8), advanced (midline, 1.7 of 8), fought (midline, 0.7 of 8), advanced (frontline, 0.5 of 8); named as {'not running, advanced': 19, 'running, advanced': 15, 'not running, fell back': 3}; win change -1.4 UNNAMED
- n 36: held (backline, 1.6 of 8), fought (frontline, 1.1 of 8), fought (midline, 0.9 of 8); named as {'not running, fought': 13, 'running, fought': 8, 'not running, held': 7}; win change 0.4 UNNAMED
- n 15: fell back (backline, 3.0 of 8), fell back (midline, 1.4 of 8), fell back (frontline, 0.8 of 8), fought (midline, 0.5 of 8); named as {'not running, fell back': 10, 'running, fell back': 3, 'running, advanced': 1}; win change -5.7
- n 2: died (frontline, 6.0 of 8), to the spawn (frontline, 2.0 of 8); named as {'not running, to the spawn': 1, 'not running': 1}; win change 1.6 UNNAMED
*enemy pickup* (3 groups, separation 0.2):
- n 205: fought (midline, 2.0 of 8), fought (backline, 1.6 of 8), fought (frontline, 1.0 of 8), held (backline, 1.0 of 8); named as {'already running, fought': 90, 'held, fought': 66, 'ran, fought': 30}; win change -0.3 UNNAMED
- n 152: fell back (backline, 1.7 of 8), fell back (midline, 1.4 of 8), fell back (frontline, 0.7 of 8), held (backline, 0.6 of 8); named as {'held, fell back': 41, 'already running, fell back': 37, 'ran, fell back': 36}; win change -2.0 UNNAMED
- n 139: advanced (backline, 2.2 of 8), advanced (midline, 1.8 of 8), advanced (frontline, 0.8 of 8), carrying (midline, 0.5 of 8); named as {'already running, advanced': 55, 'held, advanced': 37, 'ran, advanced': 28}; win change 0.5 UNNAMED
*power play* (3 groups, separation 0.28):
- n 204: fought (midline, 1.8 of 8), fought (backline, 1.8 of 8), fought (frontline, 1.1 of 8), held (backline, 0.8 of 8); named as {'pushed, fought': 98, 'held, fought': 76, 'pushed, advanced': 14}; win change 0.4 UNNAMED
- n 130: advanced (backline, 2.8 of 8), advanced (midline, 2.0 of 8), advanced (frontline, 1.1 of 8); named as {'pushed, advanced': 120, 'held, advanced': 8, 'pushed, fought': 1}; win change 2.2
- n 39: fell back (backline, 2.7 of 8), fell back (midline, 1.7 of 8), fell back (frontline, 0.6 of 8), fought (midline, 0.6 of 8); named as {'held, fell back': 29, 'pushed, fell back': 7, 'held, fought': 1}; win change -2.0
*split in base* (4 groups, separation 0.2):
- n 33: fought (midline, 2.3 of 8), fought (backline, 1.5 of 8), fought (frontline, 0.9 of 8), held (backline, 0.8 of 8); named as {'defended without a collapse': 16, 'collapsed': 14, 'missed': 3}; win change -1.6 UNNAMED
- n 28: fell back (midline, 2.4 of 8), fell back (backline, 1.4 of 8), fell back (frontline, 0.9 of 8), held (backline, 0.5 of 8); named as {'collapsed': 17, 'defended without a collapse': 7, 'missed': 4}; win change -4.6
- n 18: advanced (backline, 1.9 of 8), advanced (midline, 1.3 of 8), fought (midline, 0.9 of 8), advanced (frontline, 0.6 of 8); named as {'collapsed': 10, 'defended without a collapse': 7, 'missed': 1}; win change 5.1 UNNAMED
- n 2: died (midline, 7.0 of 8), died (backline, 1.0 of 8); named as {'defended without a collapse': 1, 'missed': 1}; win change -1.4 UNNAMED

## 8. What results and causes are worth

Win points for the team it happened to, from 34 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 115 | +3.0 | -8.4 to +13.8 | +2.6 | no |
| capture | 374 | +4.1 | +2.3 to +5.9 | +5.7 | yes |
| death (any) | 685 | -7.3 | -12.1 to -2.7 | -4.8 | yes |
| death: against a spike build | 225 | -6.3 | -15.8 to +5.5 | -3.9 | no |
| death: against other builds | 460 | -7.7 | -14.3 to -2.1 | -5.3 | yes |
| death: back within 20 s | 122 | -5.8 | -14.0 to +1.4 | -3.9 | no |
| death: down 20 to 60 s | 236 | -9.3 | -15.3 to -3.5 | -4.2 | yes |
| death: down 60 s or more | 327 | -6.3 | -11.9 to -1.0 | -5.6 | yes |
| death: healer | 231 | -2.6 | -7.3 to +2.0 | -3.5 | no |
| death: healer in own base or pit, back within 15 s (likely deliberate) | 15 | -6.0 | -28.3 to +15.1 | -6.0 | no |
| death: healer, other | 216 | -2.4 | -6.3 to +1.5 | -3.4 | no |
| death: not a healer | 454 | -9.6 | -15.6 to -4.3 | -5.5 | yes |
| pit NPC lost (any): taken by a spike build | 60 | +0.4 | -5.7 to +11.3 | -0.3 | no |
| pit NPC lost (any): taken by other builds | 216 | -4.6 | -9.8 to +0.3 | -0.0 | no |
| pit NPC lost: archer | 155 | -1.3 | -5.3 to +2.7 | -0.2 | no |
| pit NPC lost: bodyguard | 41 | -2.3 | -7.5 to +2.2 | +0.2 | no |
| pit NPC lost: knight | 80 | -8.3 | -15.5 to -2.0 | -0.1 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value.

*deaths* (per 10 s in that state; result worth -7.3 points, base rate 1.3%):

- enemies within 1,500 7.5 to 8: result chance +2.2 points, worth -0.16 win points
- own minus enemy team strength -285.5 to -140.5: result chance +1.1 points, worth -0.08 win points
- current health % 1 to 48.5: result chance +10.0 points, worth -0.73 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +3.6 points, worth -0.26 win points
- maximum health after death penalty, as a share of normal 0.4 to 0.67: result chance +5.1 points, worth -0.37 win points
- own healers alive within cast range 0 to 0.5: result chance +0.8 points, worth -0.06 win points
- match minute 21.25 to 28: result chance +1.2 points, worth -0.08 win points

*kill conversion* (per burst, for the attacking team; result worth +7.3 points, base rate 28.9%):

- damage in the 2 s burst 547.5 to 839: result chance +25.6 points, worth +1.87 win points
- target's health ceiling 0.4 to 0.56: result chance +36.6 points, worth +2.68 win points
- target's healers in range 0 to 0.5: result chance +33.8 points, worth +2.46 win points
- target health % when the burst started 0 to 43: result chance +21.6 points, worth +1.58 win points
- match minute 0.3 to 1.45: result chance -13.0 points, worth -0.95 win points
- a prot on the target 0.5 to 1: result chance -8.1 points, worth -0.59 win points
- attacking minus target team strength 426 to 721: result chance +19.2 points, worth +1.4 win points

*npc loss* (per case, for the defending team; result worth -3.5 points, base rate 16.9%):

- own players in the pit 7.5 to 8: result chance -15.6 points, worth +0.54 win points
- damage on the pit NPCs in the last 5 s 375.5 to 1170: result chance +30.7 points, worth -1.07 win points
- own players alive outside the pit 0 to 0.5: result chance +24.7 points, worth -0.86 win points
- enemy players in the pit 7.5 to 8: result chance +17.7 points, worth -0.61 win points
- attacking minus defending team strength -682 to -415.5: result chance -9.9 points, worth +0.34 win points
- own pit archers alive 2.5 to 3: result chance +21.1 points, worth -0.73 win points
- attackers' measured damage per second against a Lord (benchmarks) 101.05 to 148.9: result chance +6.1 points, worth -0.21 win points

## 9. For Denning

- Which curves look wrong to you? A correction (direction, cap, drop, or a pair to always test) is logged with your reason and tested on held-out matches.
- Do any surprises remind you of something the variables don't capture (a missing variable)?
- Any variable you think matters that isn't listed?

