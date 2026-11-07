# Learning report, batch 6

Trained on 61 matches (8 new in this batch). Variables in use: 33; build variables from 60 matches, interactions from 40.

## 0. Data integrity

- Lengths repaired: 3 (1f65fd3b 150 s -> 1027 s) (bbef1904 617 s -> 599 s) (36a65ac6 1319 s -> 1294 s) 
- Matches with a team's Lord damage not observed (left blank, not zero): 3
- Pit NPCs added from the standard roster (never seen in the replay): 198 in 52 matches
- Left out of training: 0

## 1. The honest test

**Not yet better than strength alone: treat the curves as noise.** Held-out accuracy (matches held out whole), log loss in brackets (lower is better):

- strength only: all 77% (0.418), 0-5 min 82% (0.362), 5-10 min 79% (0.404), 10-15 min 73% (0.483), 15-end min 71% (0.464), matches lasting 15 min+ 72% (0.498), matches even on strength (gap under 200) 57% (0.642)
- glass box: all 77% (0.554), 0-5 min 84% (0.378), 5-10 min 79% (0.516), 10-15 min 71% (0.73), 15-end min 71% (0.714), matches lasting 15 min+ 71% (0.694), matches even on strength (gap under 200) 59% (0.981)
- glass box without corrections: all 78% (0.557), 0-5 min 84% (0.376), 5-10 min 79% (0.505), 10-15 min 74% (0.702), 15-end min 70% (0.763), matches lasting 15 min+ 71% (0.698), matches even on strength (gap under 200) 59% (0.973)
- black box: all 72% (1.077), 0-5 min 78% (0.851), 5-10 min 74% (0.983), 10-15 min 67% (1.242), 15-end min 64% (1.383), matches lasting 15 min+ 65% (1.365), matches even on strength (gap under 200) 55% (1.739)
- Gain over strength alone (log loss, resampling whole matches): -0.136 (90% range -0.313 to -0.002).
- Change since batch 5: glass box log loss 0.53 -> 0.554; strength only 0.439 -> 0.418.

## 2. What it leans on

- **lord_dps_enemy** 0.695 (new): enemy build's measured Lord damage per second
- **lord_dps_own** 0.687 (new): own build's measured Lord damage per second if all its non-healers were at the Lord
- **knights_diff & map_flag_run** 0.457 (new): own minus enemy pit knights alive TOGETHER WITH the map's flag run Y: distance from the flag spawn to the stand (average of both sides)
- **spike_killable_diff** 0.45 (was 0.302): enemy minus own players within one spike of the other side (DP stacking; 0 unless a spike build is involved)
- **morale_diff & map_pit_to_stand** 0.394 (new): own minus enemy morale summed over players (boosts +, death penalty -) TOGETHER WITH the map's distance from a pit to the stand (average of both sides)
- **morale_diff & map_flag_run** 0.354 (new): own minus enemy morale summed over players (boosts +, death penalty -) TOGETHER WITH the map's flag run Y: distance from the flag spawn to the stand (average of both sides)
- **morale_diff** 0.353 (was 0.563): own minus enemy morale summed over players (boosts +, death penalty -)
- **knights_diff** 0.346 (was 0.242): own minus enemy pit knights alive
- **archers_diff & map_flag_run** 0.271 (new): own minus enemy pit archers alive TOGETHER WITH the map's flag run Y: distance from the flag spawn to the stand (average of both sides)
- **spike_build_own** 0.27 (new): own build is a spike build (1) or not (0)
- **spike_build_enemy** 0.27 (new): enemy build is a spike build
- **stand** 0.206 (was 0.202): who holds the flag stand: 1 own, 0 nobody, -1 enemy

## 3. The curves in words

Points = win-chance points added to an otherwise even game at each range of the variable.

- **lord_dps_enemy** rises from +9.4 to +22.2 points (35.8..65.45: +9.4; 78.4..83.15: +8.3; 83.7..88.5: -11.4; 91.2..98.6: +4.6; 102.6..105.45: -18.2; 106.0..111.8: +4.4; 117.1..135.25: +22.3)
- **lord_dps_own** falls from -9.2 to -21.5 points (35.8..65.45: -9.2; 78.4..83.15: -8.6; 83.7..88.5: +11.0; 91.2..98.6: -4.9; 102.6..105.45: +17.9; 106.0..111.8: -4.4; 117.1..135.25: -21.6)
- **knights_diff & map_flag_run** (interaction): see wp_model.md
- **spike_killable_diff** rises from -47.1 to +47.2 points (-8.0..-7.5: -47.1; -6.5..-4.5: -46.5; -2.5..-1.5: -45.5; -0.5..0.5: -0.2; 1.5..2.5: +46.3; 4.5..7.5: +46.9)
- **morale_diff & map_pit_to_stand** (interaction): see wp_model.md
- **morale_diff & map_flag_run** (interaction): see wp_model.md
- **morale_diff** rises from -15.8 to +19.4 points (-470.0..-186.5: -15.8; -141.0..-109.5: -12.7; -83.5..-46.5: -9.8; -15.5..-0.5: -2.2; 0.5..19.5: +1.4; 52.5..91.5: +9.4; 124.5..169.5: +13.0)
- **knights_diff** rises from -18.7 to +18.8 points (-2.0..-1.5: -18.7; -1.5..-0.5: -16.0; -0.5..0.5: +0.0; 0.5..1.5: +15.7; 1.5..2.0: +18.8)
- **archers_diff & map_flag_run** (interaction): see wp_model.md
- **spike_build_own** rises from -4.0 to +20.0 points (0.0..0.5: -4.0; 0.5..1.0: +20.0)

## 4. Discovery

**Interaction candidates** (a screen: pairs whose combination seems to matter beyond each alone; untested until held-out matches confirm them; switched on in the model from 40 matches):

- morale_diff with map_flag_run (screen 0.096)
- morale_diff with spike_build_enemy (screen 0.092)
- morale_diff with spike_build_own (screen 0.092)
- alive_diff with morale_diff (screen 0.088)
- morale_diff with spike_killable_diff (screen 0.087)
- morale_diff with map_pit_to_stand (screen 0.086)
- down_diff_s with morale_diff (screen 0.085)
- morale_diff with lord_dps_own (screen 0.084)

**Candidate variables** (proposed variables, tested on unseen matches; log loss, lower is better):

- split_diff: 0.554 without, 0.548 with: improves: ready to move into the model. own minus enemy players on a split (away from their main group on the enemy half, not carrying). Proposed batch 1 by Claude: the knights curve runs backwards, maybe standing in for the cost of splitting
- turtle_diff: 0.554 without, 0.575 with: does not improve yet. own minus enemy share of live players at home (own base or pit). Proposed 2026-11-06 from OG comms ([ohno v One], [ohno v Crew]: 'they are turtling, we have to make a play'); comms_vars.py: teams that turtled 60 s won 3 of 13 times
- footmen_diff: 0.554 without, 0.565 with: does not improve yet. own minus enemy footmen alive (base NPCs, not pit NPCs). Proposed 2026-11-06 from OG comms ([ohno v NwAy]: 'this way we don't lose footmen'; [ohno v Fun]: fake collapse to the footmen)
- no_healer_groups_diff: 0.554 without, 0.558 with: does not improve yet. own minus enemy groups of 2+ with no healer. Proposed 2026-11-06 from OG comms ([ohno v One]: keep a prot and a monk on one side, the Rit and a monk on the other); comms_vars.py: such groups lose players twice as often
- solo_healers_diff: 0.554 without, 0.572 with: does not improve yet. own minus enemy healers with no other own healer within casting range. Proposed 2026-11-06 from OG comms ('solo monk, go on the monk'); Denning: a monk alone has no other monk to support it

**Surprises** (moments where the held-out model was most confident about the team that went on to lose; each points to something the variables don't capture yet):

- 옷옷옷옷 v Men (36a65ac6) at 11:30: a model that never saw this match gave 옷옷옷옷 14.3%, and 옷옷옷옷 won. Why it thought so: team strength +17.5, morale_diff -16.8, alive_diff -15.7, stand -6.6, down_diff_s -6.6
- BcS v yM (b88983e3) at 11:15: a model that never saw this match gave yM 4.9%, and yM won. Why it thought so: morale_diff -30.5, morale_diff & archers_diff -28.6, team strength +19.5, morale_diff & morale_total -13.3, alive_diff -7.5
- OG v hold (49eec28d) at 4:30: a model that never saw this match gave OG 1.2%, and OG won. Why it thought so: lord_health_diff -37.7, morale_total & archers_diff -34.4, morale_diff & archers_diff -27.2, morale_diff -22.8, team strength +19.0
- Team v cope (6c7dfcaa) at 7:00: a model that never saw this match gave Team 3.7%, and Team won. Why it thought so: morale_diff -22.8, morale_diff & morale_total -22.5, team strength -11.0, stand -6.0, boost_clock -3.9
- hdm v HC (28447c4a) at 26:30: a model that never saw this match gave HC 0.2%, and HC won. Why it thought so: minute & morale_diff -46.2, morale_diff -26.8, morale_diff & archers_diff -25.0, lord_damage_diff & minute -22.3, pit_pressure_diff -20.7
- RACK v hdm (1f65fd3b) at 15:00: a model that never saw this match gave RACK 0.4%, and RACK won. Why it thought so: morale_diff -28.7, knights_diff -27.9, morale_diff & archers_diff -17.4, knights_diff & lord_damage_diff -16.0, team strength -14.0

## 5. Denning's rulings seen through the model

Win chance from a model that never saw the match, 20 s before and 60 s after each ruled moment. Contributions are points for an otherwise even game (the curves' scale).

- hdm v HC (28447c4a) 5:01 (split answered), HC: 29.9% 20 s before -> 29.3% 60 s after (-0.6). After: knights_diff -36.3, team strength -16.4, pit_pressure_diff +14.7, flag_lead & morale_diff +11.1
- hdm v HC (28447c4a) 5:01 (split answered), hdm: 71.2% 20 s before -> 72.9% 60 s after (+1.7). After: knights_diff +37.5, team strength +16.4, flag_lead & morale_diff -15.9, pit_pressure_diff -15.8
- hdm v HC (28447c4a) 1:02 (split detection), HC: 32.7% 20 s before -> 12.6% 60 s after (-20.1). After: flag_lead & morale_diff -18.0, team strength -16.4, flag_lead & knights_diff -8.0, carrying_diff -7.6
- hdm v HC (28447c4a) 1:02 (split detection), hdm: 67.0% 20 s before -> 85.4% 60 s after (+18.4). After: team strength +16.4, flag_lead & morale_diff +15.8, flag_lead -7.7, carrying_diff +7.4
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), HC: 3.2% 20 s before -> 1.4% 60 s after (-1.8). After: knights_diff -36.3, archers_diff -29.8, morale_diff & archers_diff -22.3, team strength -16.4
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), hdm: 96.1% 20 s before -> 97.3% 60 s after (+1.2). After: knights_diff +37.5, archers_diff +29.2, morale_diff & archers_diff +20.1, team strength +16.4
- hdm v HC (bbef1904) 8:10 (death), HC: 47.9% 20 s before -> 5.9% 60 s after (-42.0). After: team strength -16.0, alive_diff -14.2, down_diff_s -11.9, morale_diff -11.5
- hdm v HC (bbef1904) 8:10 (death), hdm: 49.8% 20 s before -> 94.3% 60 s after (+44.5). After: down_diff_s +17.1, team strength +16.0, alive_diff +13.3, morale_diff +12.9
- Men v HC (faec428a) 9:31 (death), HC: 25.3% 20 s before -> 33.1% 60 s after (+7.8). After: team strength -14.9, archers_diff +10.2, stand -6.3, knights_diff -4.2
- Men v HC (faec428a) 9:31 (death), Men: 76.2% 20 s before -> 71.0% 60 s after (-5.2). After: team strength +14.9, archers_diff -8.7, stand +6.2, flag_lead & knights_diff +3.9

## 6. Why: the node models

Each explains one result from what happened before it (time order enforced), tested on matches it never saw. AUC = how often a moment that led to the result scores above one that didn't (0.5 = guessing, 1 = perfect).

**deaths** (61 matches, 134313 moments, 3716 results): adds to the simple baseline (AUC 0.916 against 0.799 for health_pct and damage_taken_3s alone).
- **enemies_near** (enemies within 1,500) rises from -21.8 to +24.5 points (0.0..0.5: -21.8; 0.5..1.5: -9.8; 1.5..2.5: +0.9; 2.5..3.5: +3.0; 3.5..4.5: +12.1; 4.5..5.5: +13.4; 5.5..6.5: +14.8; 6.5..7.5: +16.8; 7.5..8.0: +24.5)
- **health_pct** (current health %) falls from +40.9 to -6.3 points (1.0..47.5: +40.9; 59.5..67.5: +24.2; 73.5..78.5: +10.6; 82.5..85.5: +6.4; 88.5..91.5: +1.5; 93.5..95.5: -2.1; 97.5..99.5: -4.8)
- **strength_gap** (own minus enemy team strength) falls from +16.5 to -10.9 points (-901.0..-523.0: +16.5; -360.5..-274.5: +10.2; -122.5..-102.0: +3.9; -45.0..0.0: +1.1; 60.5..104.5: -7.6; 122.5..274.5: -9.6; 360.5..523.0: -10.8)
- **local_diff** (allies minus enemies within 2,000) falls from +24.4 to -12.2 points (-8.0..-3.5: +24.4; -2.5..-1.5: +12.2; -0.5..0.5: -4.1; 1.5..2.5: -8.5; 3.5..4.5: +8.8; 5.5..7.0: -12.2)
- **allies_near** (allies within 1,500) falls from +18.9 to -8.4 points (0.0..0.5: +18.9; 0.5..1.5: +7.5; 1.5..2.5: +5.3; 2.5..3.5: -1.3; 3.5..4.5: -2.2; 4.5..5.5: -3.7; 5.5..6.5: -5.6; 6.5..7.0: -8.4)
- **minute** (match minute) rises from -5.7 to +18.9 points (0.1..1.25: -5.7; 2.25..3.35: -10.8; 4.45..5.45: -3.6; 6.65..8.05: +0.2; 9.55..11.15: +0.6; 13.05..15.15: +1.2; 17.75..20.95: +6.7)
- **enemy_strips** (enemy enchantment removal skills) falls from +4.8 to -45.1 points (0.0..0.5: +4.8; 0.5..1.5: +5.9; 1.5..2.5: +4.1; 2.5..3.5: -3.3; 3.5..4.5: -4.4; 4.5..5.5: -5.0; 5.5..6.0: -45.1)
- **own_condition_removal** (own condition removal skills) falls from -15.8 to -24.4 points (1.0..1.5: -15.8; 1.5..2.5: +4.8; 2.5..3.5: +5.7; 3.5..4.5: +0.4; 4.5..5.5: +1.3; 5.5..6.5: -11.4; 6.5..7.5: -21.8; 7.5..8.0: -24.4)
- **enemy_interrupts** (enemy interrupt skills) rises from -9.7 to +0.7 points (0.0..0.5: -9.7; 0.5..1.5: +20.0; 1.5..2.5: +6.8; 2.5..3.5: -3.8; 3.5..4.5: -4.6; 4.5..5.5: -0.2; 5.5..6.5: -0.1; 6.5..7.0: +0.7)

**kill conversion** (61 matches, 1025 moments, 304 results): adds to the simple baseline (AUC 0.785 against 0.665 for burst_damage and target_health_pct alone).
- **burst_damage** (damage in the 2 s burst) rises from -8.9 to +28.9 points (250.0..257.5: -8.9; 264.5..274.5: -14.7; 285.5..294.5: -10.5; 307.5..322.5: -4.8; 337.5..354.5: -0.9; 375.0..410.5: +4.0; 449.5..518.5: +25.0)
- **target_ceiling** (target's health ceiling) falls from +30.7 to -15.4 points (0.4..0.56: +30.7; 0.69..0.7: +16.7; 0.78..0.83: +17.3; 0.86..0.9: +13.6; 0.94..0.95: +8.1; 0.99..1.02: -3.3; 1.1..1.1: -15.4)
- **target_health_pct** (target health % when the burst started) falls from +24.7 to -10.5 points (0.0..38.5: +24.7; 50.5..56.5: +8.9; 62.5..68.5: +7.0; 72.5..76.5: +6.5; 79.5..82.5: -4.2; 86.5..90.5: -9.3; 95.5..99.5: -10.1)
- **target_healers_in_range** (target's healers in range) falls from +29.4 to -6.1 points (0.0..0.5: +29.4; 0.5..1.5: -3.1; 1.5..2.5: -7.0; 2.5..3.0: -6.1)
- **strength_gap** (attacking minus target team strength) rises from -15.4 to +22.4 points (-815.0..-434.0: -15.4; -316.5..-226.0: -10.8; -117.5..-10.0: -0.9; 0.0..63.5: +0.8; 75.5..133.0: -3.3; 248.5..274.5: -4.0; 386.0..459.0: +16.0)
- **enemy_prots** (target team's prot skills) is flat from -10.2 to -9.0 points (1.0..4.0: -10.2; 5.5..6.5: +19.8; 7.5..8.5: +8.9; 9.5..10.5: +11.3; 11.5..12.5: -4.6; 13.5..14.5: -6.3; 15.5..16.0: -9.0)
- **target_prot_up** (a prot on the target) falls from +5.0 to -10.0 points (0.0..0.5: +5.0; 0.5..1.0: -10.0)
- **minute** (match minute) rises from -20.7 to +11.7 points (0.3..1.45: -20.7; 2.65..3.75: -2.9; 4.95..6.15: -3.1; 6.95..8.15: -3.0; 9.45..10.85: +3.4; 12.85..15.05: +7.0; 17.15..20.65: +9.4)
- **enemy_blind** (target team's Blind skills) falls from +3.1 to -29.7 points (0.0..0.5: +3.1; 0.5..1.5: -10.6; 1.5..2.5: -21.0; 2.5..3.0: -29.7)
- **own_interrupts_v_enemy_heals** (attackers' interrupt skills minus target team's heals) is flat from -0.6 to -0.3 points (-16.0..-15.5: -0.6; -14.5..-13.5: +6.3; -12.5..-11.5: -0.7; -10.5..-9.5: -2.9; -8.5..-7.5: +3.5; -6.5..-5.5: -6.4; -4.5..-4.0: -0.3)

**flag answer** (seconds an answer to an enemy capture was slower than possible; 56 matches, 523 rows): adds to the simple baseline (typical error 17.1s against 27.4s for the median; explains 70% of the spread).
- **parked_s** (seconds the flag lay parked (dropped 5 s or more: not running yet)): 0.0..2.5: -5.6 s; 11.5..16.5: +2.8 s; 23.5..30.5: +19.4 s; 37.5..44.5: +39.0 s; 55.5..65.5: +51.0 s; 83.0..101.5: +59.4 s; 124.5..259.0: +63.4 s
- **enemy_deaths_during** (enemy deaths during the answer): 0.0..0.5: -3.9 s; 0.5..1.5: +11.2 s; 1.5..2.5: +19.3 s; 2.5..3.5: +28.1 s; 3.5..5.0: +28.7 s
- **enemies_in_the_way** (enemy presence along the runner's trip back to the spawn): 0.0..0.5: -6.1 s; 4.5..9.5: -4.0 s; 14.5..19.5: -2.4 s; 25.0..34.5: -1.2 s; 46.5..55.5: +4.2 s; 75.5..107.5: +10.0 s; 142.0..217.0: +15.1 s
- **own_deaths_during** (own deaths during the answer): 0.0..0.5: -3.6 s; 0.5..1.5: +5.8 s; 1.5..2.5: +13.9 s; 2.5..3.5: +19.9 s; 3.5..4.5: +31.2 s; 4.5..5.5: +44.6 s; 5.5..6.5: +52.4 s; 6.5..8.0: +57.6 s; 8.0..17.0: +57.6 s
- **carrier_damage_taken** (damage the carrier took while carrying): 0.0..1.0: -3.0 s; 26.5..47.5: -3.7 s; 67.5..91.5: -2.0 s; 122.0..168.5: +1.0 s; 241.5..274.5: +3.6 s; 369.5..498.0: +6.3 s; 626.5..962.5: +9.0 s
- **runner_to_spawn** (runner's distance to its flag spawn when the enemy captured): 4.0..866.5: -10.2 s; 1472.5..2239.0: -4.4 s; 3243.5..3943.0: -1.2 s; 4485.5..5020.5: +1.8 s; 5755.5..6501.5: +3.6 s; 6983.0..7553.0: +3.7 s; 8289.0..9061.0: +4.2 s
- **quick_handoffs** (quick hand-offs (a teammate picked it up within 5 s)): 0.0..0.5: -2.0 s; 0.5..1.5: +6.1 s; 1.5..2.5: +10.0 s; 2.5..3.0: +23.6 s
- **possible_s** (fastest possible answer (s) from the flag model at the enemy's capture): 0.0..4.5: -0.9 s; 9.5..17.5: +1.6 s; 23.5..28.5: +2.2 s; 31.5..34.5: +3.4 s; 38.5..42.5: +3.2 s; 47.5..52.5: -1.0 s; 59.5..67.5: -5.1 s
- **flag_lead_at_enemy_cap** (own flag lead when the enemy captured): -81.0..-69.5: -7.5 s; -60.5..-50.5: -0.8 s; -39.5..-34.5: +2.1 s; -26.5..-17.5: +2.7 s; -9.5..-1.5: +2.5 s; 8.5..19.5: +0.5 s; 34.5..53.5: -1.1 s
- **morale_diff** (own minus enemy morale): -200.0..-112.5: +10.5 s; -76.0..-51.5: +4.4 s; -31.0..-18.0: +1.6 s; -7.5..6.5: -0.4 s; 17.0..31.0: -2.4 s; 48.0..74.0: -4.1 s; 97.0..132.0: -2.9 s

**npc loss** (61 matches, 6867 moments, 1271 results): adds to the simple baseline (AUC 0.809 against 0.748 for attackers and defenders alone).
- **defenders** (own players in the pit) falls from +34.1 to -37.8 points (0.0..0.5: +34.1; 0.5..1.5: +23.1; 1.5..2.5: +14.5; 2.5..3.5: +1.9; 3.5..4.5: -12.4; 4.5..5.5: -13.2; 5.5..6.5: -14.0; 6.5..7.5: -28.1; 7.5..8.0: -37.8)
- **npc_damage_5s** (damage on the pit NPCs in the last 5 s) rises from -16.6 to +34.3 points (0.0..0.5: -16.6; 22.5..36.5: -2.1; 50.5..69.5: +5.6; 88.5..109.5: +12.8; 131.5..157.5: +23.1; 188.5..227.5: +26.3; 278.5..367.0: +30.8)
- **defenders_elsewhere** (own players alive outside the pit) falls from +21.3 to -5.5 points (0.0..0.5: +21.3; 0.5..1.5: +12.7; 1.5..2.5: +12.6; 2.5..3.5: +5.6; 3.5..4.5: -5.2; 4.5..5.5: -15.0; 5.5..6.5: -16.2; 6.5..7.5: -15.1; 7.5..8.0: -5.5)
- **attackers_share** (share of the attacking team's live players in the pit (OG comms: merge before pushing the pit)) rises from -10.3 to +8.7 points (0.12..0.13: -10.3; 0.16..0.23: -6.6; 0.27..0.35: -5.1; 0.42..0.53: +5.7; 0.61..0.65: +8.4; 0.73..0.78: +10.2; 0.87..0.94: +11.1)
- **defender_healers** (of which healers) falls from +19.8 to -6.7 points (0.0..0.5: +19.8; 0.5..1.5: -1.8; 1.5..2.5: -4.7; 2.5..3.0: -6.7)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -9.6 to +6.5 points (1.9..18.75: -9.6; 28.65..32.15: -4.7; 33.95..43.25: -3.4; 54.55..63.75: +2.9; 65.7..73.15: +5.6; 77.95..86.8: +7.5; 99.1..110.5: +7.4)
- **attackers** (enemy players in the pit) rises from -7.2 to +10.1 points (1.0..1.5: -7.2; 1.5..2.5: -3.9; 2.5..3.5: -2.5; 3.5..4.5: -0.8; 4.5..5.5: +7.1; 5.5..6.5: +8.6; 6.5..7.5: +9.8; 7.5..8.0: +10.1)
- **minute** (match minute) falls from +1.8 to -8.7 points (0.5..2.55: +1.8; 3.65..4.65: +7.9; 5.65..6.65: +6.9; 7.75..9.15: +5.1; 10.65..12.25: -7.9; 14.25..16.05: -0.8; 19.35..23.45: -8.6)
- **npc_healing_10s** (healing on own pit NPCs and Lord in the last 10 s) falls from +3.8 to -17.7 points (0.0..3.0: +3.8; 42.5..73.5: +3.8; 104.5..142.5: +2.5; 180.5..222.5: -5.1; 268.5..318.5: -6.3; 379.0..439.5: -7.4; 534.5..688.5: -14.0)
- **strength_gap** (attacking minus defending team strength) rises from -6.0 to +4.7 points (-901.0..-415.5: -6.0; -287.5..-133.0: -11.2; -31.0..53.0: +3.7; 91.5..106.0: -2.4; 191.5..256.0: +3.2; 303.5..386.0: +2.8; 459.0..570.0: -0.8)

**lord damage** (Lord damage dealt in the next 10 s while players are in the enemy pit; 59 matches, 8008 rows): adds to the simple baseline (typical error 125.3 against 85.7 for the median; explains 29% of the spread).
- **defenders** (own players in the pit): 0.0..0.5: +197.3; 0.5..1.5: +111.4; 1.5..2.5: +53.9; 2.5..3.5: -13.4; 3.5..4.5: -66.2; 4.5..5.5: -101.8; 5.5..6.5: -135.9; 6.5..7.5: -147.4; 7.5..8.0: -148.3
- **defenders_elsewhere** (own players alive outside the pit): 0.0..0.5: +68.2; 0.5..1.5: +72.6; 1.5..2.5: +72.8; 2.5..3.5: +69.0; 3.5..4.5: +28.8; 4.5..5.5: -6.8; 5.5..6.5: -48.9; 6.5..7.5: -111.3; 7.5..8.0: -170.9
- **bodyguard** (own Bodyguard alive): 0.0..0.5: +103.7; 0.5..1.0: -41.1
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)): 1.9..18.75: -49.8; 28.8..32.15: -36.0; 32.8..43.25: -30.1; 54.8..64.25: -2.6; 65.7..72.55: +25.1; 76.6..86.35: +44.6; 99.2..110.5: +51.3
- **attackers** (enemy players in the pit): 1.0..1.5: -29.6; 1.5..2.5: -10.4; 2.5..3.5: -15.2; 3.5..4.5: -9.1; 4.5..5.5: +35.2; 5.5..6.5: +35.6; 6.5..7.5: +38.1; 7.5..8.0: +39.2
- **defender_healers** (of which healers): 0.0..0.5: +58.1; 0.5..1.5: -5.5; 1.5..2.5: -4.4; 2.5..3.0: -39.6
- **attackers_share** (share of the attacking team's live players in the pit (OG comms: merge before pushing the pit)): 0.12..0.13: -13.4; 0.16..0.23: -17.3; 0.27..0.35: -17.2; 0.42..0.53: -25.6; 0.61..0.65: +5.4; 0.73..0.78: +18.8; 0.87..0.94: +40.2
- **npc_healing_10s** (healing on own pit NPCs and Lord in the last 10 s): 0.0..3.0: -16.8; 42.5..73.5: +4.0; 106.5..142.5: +20.7; 174.5..218.5: +21.4; 262.5..313.5: +24.4; 373.5..436.5: +28.2; 532.5..685.5: +38.8
- **seconds_in_pit** (seconds the attackers have been in the pit): 0.0..4.5: -20.8; 10.5..16.5: -18.6; 22.5..28.5: -9.6; 37.5..46.5: -2.7; 58.5..73.5: +16.7; 91.5..112.5: +9.4; 142.5..193.5: +26.6
- **attacker_healers** (of which healers): 0.0..0.5: +14.4; 0.5..1.5: -3.6; 1.5..2.5: +12.5; 2.5..3.0: -50.7

**lord kill** (59 matches, 8004 moments, 528 results): no better than the simple baseline yet (AUC 0.942 against 0.934 for attackers and defenders alone).
- **defenders** (own players in the pit) falls from +47.3 to -47.5 points (0.0..0.5: +47.3; 0.5..1.5: +40.4; 1.5..2.5: +18.2; 2.5..3.5: -1.8; 3.5..4.5: -26.7; 4.5..5.5: -35.8; 5.5..6.5: -40.3; 6.5..7.5: -41.4; 7.5..8.0: -47.5)
- **attackers** (enemy players in the pit) rises from -45.4 to +28.3 points (1.0..1.5: -45.4; 1.5..2.5: +9.8; 2.5..3.5: +16.1; 3.5..4.5: +20.0; 4.5..5.5: +34.1; 5.5..6.5: +35.7; 6.5..7.5: +34.9; 7.5..8.0: +28.3)
- **defenders_elsewhere** (own players alive outside the pit) falls from +40.3 to -42.2 points (0.0..0.5: +40.3; 0.5..1.5: +22.2; 1.5..2.5: +21.7; 2.5..3.5: +20.7; 3.5..4.5: +19.2; 4.5..5.5: -20.8; 5.5..6.5: -25.3; 6.5..7.5: -41.5; 7.5..8.0: -42.2)
- **minute** (match minute) rises from -48.4 to +32.0 points (0.5..2.85: -48.4; 4.05..5.15: -15.4; 6.25..7.35: +6.8; 8.85..10.35: +14.1; 11.75..13.85: +15.6; 15.65..18.25: +25.9; 20.45..24.75: +31.5)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -27.4 to +25.0 points (1.9..18.75: -27.4; 28.8..32.15: -26.5; 32.8..43.25: -7.3; 54.8..64.25: -3.5; 65.7..72.55: +8.7; 76.6..86.35: +27.6; 99.2..110.5: +24.5)
- **defender_healers** (of which healers) falls from +25.3 to -31.9 points (0.0..0.5: +25.3; 0.5..1.5: +9.9; 1.5..2.5: -2.1; 2.5..3.0: -31.9)
- **attackers_share** (share of the attacking team's live players in the pit (OG comms: merge before pushing the pit)) rises from -17.0 to +24.4 points (0.12..0.13: -17.0; 0.16..0.23: -12.7; 0.27..0.35: -5.2; 0.42..0.53: -8.6; 0.61..0.65: -3.3; 0.73..0.78: +22.8; 0.87..0.94: +24.9)
- **seconds_in_pit** (seconds the attackers have been in the pit) rises from -6.1 to +32.8 points (0.0..4.5: -6.1; 10.5..16.5: -13.8; 22.5..28.5: -12.7; 37.5..46.5: -10.5; 58.5..73.5: +4.3; 91.5..112.5: +17.8; 142.5..193.5: +26.6)
- **res_in** (seconds until the next res) rises from -42.3 to +0.4 points (1.0..8.5: -42.3; 17.5..26.5: +7.1; 35.5..44.5: +12.2; 53.5..62.5: +11.3; 68.5..74.5: +8.7; 80.5..86.5: +6.6; 95.5..107.5: +1.7)

## 7. The usual play

Each choice against the most common one in that kind of decision, in win-chance points over the decision's window, adjusted for the situation, with a 90% range from resampling whole matches. CLEAR = the range excludes 0. Win chance comes from a model that never saw the match. The same comparison over the 30 s BEFORE the decision is a placebo test: a choice can't cause what came before it, so a clear difference there means the effect is partly who makes that choice.

**after wipe** (128 decisions, 56 matches; usual: pushed the pit)
- took the flag (n 16): -14.1 [-24.7, -5.4] CLEAR; in the 30 s before: +2.6 [-5.8, +10.8]
- reset (n 13): -3.1 [-9.0, +3.8]; in the 30 s before: -6.7 [-17.0, -1.0] ALREADY DIFFERENT BEFORE: partly who chooses it

**boost clock** (242 decisions, 58 matches; usual: not running, fought)
- not running, fell back (n 37): -6.3 [-10.4, -1.5] CLEAR; in the 30 s before: +1.0 [-2.1, +3.6]
- running, fought (n 35): -3.2 [-8.0, +0.9]; in the 30 s before: +3.9 [+0.5, +7.3] ALREADY DIFFERENT BEFORE: partly who chooses it
- not running, advanced (n 30): -7.2 [-11.2, -0.4] CLEAR; in the 30 s before: +8.1 [+4.5, +11.4] ALREADY DIFFERENT BEFORE: partly who chooses it
- running, advanced (n 25): +1.6 [-3.0, +7.7]; in the 30 s before: +2.1 [-3.2, +5.7]
- not running, held (n 14): -4.4 [-11.9, +3.0]; in the 30 s before: +4.8 [-1.7, +10.7]
- not running, to the spawn (n 13): -4.5 [-10.9, +3.7]; in the 30 s before: +1.0 [-2.4, +3.5]
- running, fell back (n 9): +4.8 [-7.4, +17.4]; in the 30 s before: +2.1 [-2.9, +8.9]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - not running, fell back, behind in the fight (lowest third, -0.08 or less): +0.2 (n 11 against 41)
  - not running, fell back, middle third: -5.3 (n 14 against 26)
  - not running, fell back, ahead in the fight (top third, above -0.01): -10.0 (n 12 against 12)
  - running, fought, behind in the fight (lowest third, -0.08 or less): -0.3 (n 10 against 41)
  - running, fought, middle third: -5.3 (n 10 against 26)
  - running, fought, ahead in the fight (top third, above -0.01): +1.5 (n 15 against 12)
  - not running, advanced, behind in the fight (lowest third, -0.08 or less): too few yet (n 4 against 41; means -15.6 against 0.0)
  - not running, advanced, middle third: too few yet (n 9 against 26; means -8.4 against 1.6)
  - not running, advanced, ahead in the fight (top third, above -0.01): -3.9 (n 17 against 12)
  - running, advanced, behind in the fight (lowest third, -0.08 or less): too few yet (n 3 against 41; means -1.4 against 0.0)
  - running, advanced, middle third: too few yet (n 9 against 26; means 4.0 against 1.6)
  - running, advanced, ahead in the fight (top third, above -0.01): +2.9 (n 13 against 12)
  - not running, held, behind in the fight (lowest third, -0.08 or less): too few yet (n 4 against 41; means -5.8 against 0.0)
  - not running, held, middle third: too few yet (n 2 against 26; means -26.6 against 1.6)
  - not running, held, ahead in the fight (top third, above -0.01): too few yet (n 8 against 12; means 5.3 against -2.9)
  - not running, to the spawn, behind in the fight (lowest third, -0.08 or less): too few yet (n 7 against 41; means -1.3 against 0.0)
  - not running, to the spawn, middle third: too few yet (n 4 against 26; means -8.6 against 1.6)
  - not running, to the spawn, ahead in the fight (top third, above -0.01): too few yet (n 2 against 12; means -4.7 against -2.9)
  - running, fell back, behind in the fight (lowest third, -0.08 or less): too few yet (n 1 against 41; means 8.8 against 0.0)
  - running, fell back, middle third: too few yet (n 6 against 26; means -6.0 against 1.6)
  - running, fell back, ahead in the fight (top third, above -0.01): too few yet (n 2 against 12; means 29.5 against -2.9)

**enemy pickup** (925 decisions, 59 matches; usual: held, fought)
- already running, fought (n 137): -5.9 [-9.8, -0.2] CLEAR; in the 30 s before: -0.2 [-2.7, +2.7]
- held, advanced (n 106): -2.4 [-6.5, +4.5]; in the 30 s before: +0.4 [-2.2, +3.2]
- already running, advanced (n 92): -4.9 [-8.4, +1.0]; in the 30 s before: +2.3 [-0.8, +5.4]
- held, fell back (n 77): -6.8 [-13.1, -0.1] CLEAR; in the 30 s before: -0.6 [-3.9, +3.2]
- ran, fell back (n 67): -3.9 [-8.0, +1.0]; in the 30 s before: -3.6 [-5.9, -1.1] ALREADY DIFFERENT BEFORE: partly who chooses it
- already running, fell back (n 61): -3.5 [-9.2, +3.4]; in the 30 s before: -2.5 [-5.6, +0.8]
- ran, fought (n 58): -2.9 [-5.8, +2.8]; in the 30 s before: -4.5 [-6.8, -1.8] ALREADY DIFFERENT BEFORE: partly who chooses it
- ran, advanced (n 51): -4.9 [-8.5, +0.9]; in the 30 s before: +1.9 [-0.6, +4.2]
- already running, held (n 28): -3.1 [-7.1, +3.4]; in the 30 s before: -2.8 [-7.7, +2.7]
- held, held (n 20): +2.8 [-4.0, +16.7]; in the 30 s before: -7.3 [-17.1, -0.7] ALREADY DIFFERENT BEFORE: partly who chooses it
- ran, held (n 15): -0.0 [-5.7, +4.9]; in the 30 s before: -4.6 [-7.9, -1.7] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, to the spawn (n 8): +0.0 [-12.9, +19.1]; in the 30 s before: -10.2 [-29.3, +9.0]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - already running, fought, behind in the fight (lowest third, -0.01 or less): -0.4 (n 48 against 55)
  - already running, fought, middle third: -8.8 (n 34 against 78)
  - already running, fought, ahead in the fight (top third, above +0.01): -4.5 (n 55 against 72)
  - held, advanced, behind in the fight (lowest third, -0.01 or less): -2.8 (n 18 against 55)
  - held, advanced, middle third: -6.8 (n 45 against 78)
  - held, advanced, ahead in the fight (top third, above +0.01): +3.2 (n 43 against 72)
  - already running, advanced, behind in the fight (lowest third, -0.01 or less): +3.0 (n 23 against 55)
  - already running, advanced, middle third: -9.8 (n 35 against 78)
  - already running, advanced, ahead in the fight (top third, above +0.01): -1.8 (n 34 against 72)
  - held, fell back, behind in the fight (lowest third, -0.01 or less): -6.8 (n 36 against 55)
  - held, fell back, middle third: -15.3 (n 18 against 78)
  - held, fell back, ahead in the fight (top third, above +0.01): -0.5 (n 23 against 72)
  - ran, fell back, behind in the fight (lowest third, -0.01 or less): -2.2 (n 35 against 55)
  - ran, fell back, middle third: -9.5 (n 18 against 78)
  - ran, fell back, ahead in the fight (top third, above +0.01): +1.9 (n 14 against 72)
  - already running, fell back, behind in the fight (lowest third, -0.01 or less): -0.1 (n 30 against 55)
  - already running, fell back, middle third: -6.7 (n 20 against 78)
  - already running, fell back, ahead in the fight (top third, above +0.01): +0.8 (n 11 against 72)
  - ran, fought, behind in the fight (lowest third, -0.01 or less): +1.6 (n 25 against 55)
  - ran, fought, middle third: -6.1 (n 14 against 78)
  - ran, fought, ahead in the fight (top third, above +0.01): -2.5 (n 19 against 72)
  - ran, advanced, behind in the fight (lowest third, -0.01 or less): -5.2 (n 12 against 55)
  - ran, advanced, middle third: -4.4 (n 24 against 78)
  - ran, advanced, ahead in the fight (top third, above +0.01): -6.4 (n 15 against 72)
  - already running, held, behind in the fight (lowest third, -0.01 or less): +0.6 (n 11 against 55)
  - already running, held, middle third: -6.7 (n 10 against 78)
  - already running, held, ahead in the fight (top third, above +0.01): too few yet (n 7 against 72; means -3.9 against 0.7)
  - held, held, behind in the fight (lowest third, -0.01 or less): +4.3 (n 10 against 55)
  - held, held, middle third: too few yet (n 8 against 78; means 2.1 against 9.4)
  - held, held, ahead in the fight (top third, above +0.01): too few yet (n 2 against 72; means 17.4 against 0.7)
  - ran, held, behind in the fight (lowest third, -0.01 or less): too few yet (n 5 against 55; means 0.7 against 1.1)
  - ran, held, middle third: -9.7 (n 10 against 78)
  - held, to the spawn, behind in the fight (lowest third, -0.01 or less): too few yet (n 7 against 55; means 2.6 against 1.1)
  - held, to the spawn, ahead in the fight (top third, above +0.01): too few yet (n 1 against 72; means 0.3 against 0.7)

- **late_game**: not enough decisions yet (20)
**power play** (539 decisions, 61 matches; usual: pushed, advanced)
- pushed, fought (n 150): +2.6 [+0.3, +5.0] CLEAR; in the 30 s before: -1.8 [-3.8, +0.1]
- held, fought (n 118): -1.3 [-3.6, +0.6]; in the 30 s before: -2.8 [-4.8, -0.5] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, fell back (n 40): -2.0 [-4.9, +0.8]; in the 30 s before: -6.3 [-12.0, -0.3] ALREADY DIFFERENT BEFORE: partly who chooses it
- pushed, fell back (n 25): +3.6 [-1.8, +8.3]; in the 30 s before: -4.5 [-7.7, -0.2] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, advanced (n 16): +4.0 [-1.3, +12.5]; in the 30 s before: -4.6 [-11.2, +1.0]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - pushed, fought, behind in the fight (lowest third, +0.00 or less): +3.2 (n 42 against 65)
  - pushed, fought, middle third: +2.9 (n 50 against 49)
  - pushed, fought, ahead in the fight (top third, above +0.07): -1.1 (n 58 against 76)
  - held, fought, behind in the fight (lowest third, +0.00 or less): +1.7 (n 43 against 65)
  - held, fought, middle third: -2.5 (n 43 against 49)
  - held, fought, ahead in the fight (top third, above +0.07): -5.0 (n 32 against 76)
  - held, fell back, behind in the fight (lowest third, +0.00 or less): +0.6 (n 18 against 65)
  - held, fell back, middle third: -3.2 (n 14 against 49)
  - held, fell back, ahead in the fight (top third, above +0.07): too few yet (n 8 against 76; means -4.6 against 3.0)
  - pushed, fell back, behind in the fight (lowest third, +0.00 or less): -0.2 (n 10 against 65)
  - pushed, fell back, middle third: +4.6 (n 12 against 49)
  - pushed, fell back, ahead in the fight (top third, above +0.07): too few yet (n 3 against 76; means 11.5 against 3.0)
  - held, advanced, behind in the fight (lowest third, +0.00 or less): too few yet (n 7 against 65; means 0.9 against -1.0)
  - held, advanced, middle third: too few yet (n 6 against 49; means 5.3 against -0.3)
  - held, advanced, ahead in the fight (top third, above +0.07): too few yet (n 3 against 76; means 10.9 against 3.0)

**split in base** (148 decisions, 42 matches; usual: defended without a collapse)
- collapsed (n 61): -8.5 [-13.5, -2.5] CLEAR; in the 30 s before: +1.3 [-1.6, +4.5]
- missed (n 12): -6.0 [-16.2, +2.1]; in the 30 s before: -1.0 [-6.5, +6.9]

**Collapses on a split: time away and its cost** (`S32`; per collapse, averages; main = what the main fight lost while the collapsers were away)

| Group | Cases | Away (median s) | Split killed | Collapser died | Own deaths at main | Enemy deaths at main | Flag lead change | DP change | Win change |
|---|---|---|---|---|---|---|---|---|---|
| all | 66 | 18 | 13 | 7 | 0.55 | 0.23 | +2.4 | -2.9 | -3.7 |
| away under 30 s | 42 | 8 | 10 | 1 | 0.02 | 0.1 | +0.8 | +0.2 | -0.7 |
| away 30 to 60 s | 11 | 42 | 0 | 1 | 0.18 | 0.09 | +11.6 | -2.7 | -4.9 |
| away 60 s or more | 13 | 90 | 3 | 5 | 2.54 | 0.77 | -0.4 | -13.2 | -12.5 |
| before 20:00 | 58 | 17.5 | 9 | 5 | 0.33 | 0.21 | +4.2 | -4.3 | -2.4 |
| from 20:00 | 8 | 18 | 4 | 2 | 2.12 | 0.38 | -10.8 | +6.9 | -13.6 |
| split member killed | 13 | 16 | 13 | 1 | 0.08 | 0.77 | +3.6 | +1.4 | -4.7 |
| no kill | 53 | 19 | 0 | 6 | 0.66 | 0.09 | +2.1 | -4.0 | -3.5 |

**Leverage: where the choice matters most** (share of the spread in win-chance change explained by the choice beyond the situation; range = best minus worst choice, in points)

- after wipe (128): choice explains 8.0% (situation 12.6%); range 14.1 points, best pushed the pit, worst took the flag
- boost clock (242): choice explains 5.7% (situation 1.8%); range 11.5 points, best running, fell back, worst not running, advanced
- split in base (148): choice explains 3.4% (situation 12.1%); range 8.5 points, best defended without a collapse, worst collapsed
- power play (539): choice explains 1.6% (situation 1.5%); range 6.3 points, best held, advanced, worst held, fell back
- enemy pickup (925): choice explains 1.5% (situation 3.2%); range 9.8 points, best held, held, worst held, fell back

**Behaviour clusters: what teams actually did** (each decision's response grouped by what every player did in the next 20 s; UNNAMED = a group no single named choice covers: a response for Denning to name or reject)

*after wipe* (2 groups, separation 0.31):
- n 78: fought (midline, 1.9 of 8), fought (backline, 1.5 of 8), held (backline, 0.9 of 8), fought (frontline, 0.9 of 8); named as {'pushed the pit': 70, 'reset': 4, 'took the flag': 4}; win change -0.5
- n 50: advanced (backline, 2.9 of 8), advanced (midline, 2.0 of 8), advanced (frontline, 1.3 of 8); named as {'pushed the pit': 29, 'took the flag': 12, 'reset': 9}; win change -2.9 UNNAMED
*boost clock* (4 groups, separation 0.18):
- n 92: fought (midline, 2.2 of 8), fought (backline, 1.8 of 8), fought (frontline, 1.0 of 8); named as {'not running, fought': 60, 'running, fought': 27, 'running, advanced': 2}; win change -1.2
- n 64: held (backline, 1.6 of 8), fought (midline, 0.9 of 8), held (midline, 0.8 of 8), fought (frontline, 0.6 of 8); named as {'not running, fought': 17, 'not running, held': 14, 'not running, to the spawn': 10}; win change -0.8 UNNAMED
- n 58: advanced (midline, 2.2 of 8), advanced (backline, 1.8 of 8), fought (midline, 0.6 of 8), advanced (frontline, 0.5 of 8); named as {'not running, advanced': 29, 'running, advanced': 20, 'running, fought': 2}; win change -4.1 UNNAMED
- n 37: fell back (midline, 2.8 of 8), fell back (backline, 1.9 of 8), fell back (frontline, 0.8 of 8); named as {'not running, fell back': 30, 'running, fell back': 7}; win change -3.2
*enemy pickup* (3 groups, separation 0.2):
- n 370: fought (midline, 2.1 of 8), fought (backline, 1.4 of 8), fought (frontline, 1.1 of 8), held (backline, 0.9 of 8); named as {'held, fought': 160, 'already running, fought': 124, 'ran, fought': 46}; win change -0.3 UNNAMED
- n 307: advanced (midline, 1.9 of 8), advanced (backline, 1.9 of 8), advanced (frontline, 0.9 of 8), fought (backline, 0.6 of 8); named as {'held, advanced': 102, 'already running, advanced': 86, 'ran, advanced': 48}; win change 4.3 UNNAMED
- n 250: fell back (midline, 1.7 of 8), fell back (backline, 1.7 of 8), fell back (frontline, 0.6 of 8), held (backline, 0.6 of 8); named as {'held, fell back': 72, 'ran, fell back': 65, 'already running, fell back': 57}; win change -1.1 UNNAMED
*power play* (3 groups, separation 0.26):
- n 272: fought (midline, 2.1 of 8), fought (backline, 1.7 of 8), fought (frontline, 1.1 of 8), held (backline, 0.7 of 8); named as {'pushed, fought': 139, 'held, fought': 109, 'pushed, advanced': 16}; win change 0.4 UNNAMED
- n 185: advanced (backline, 2.4 of 8), advanced (midline, 2.2 of 8), advanced (frontline, 1.1 of 8); named as {'pushed, advanced': 168, 'held, advanced': 13, 'pushed, fought': 3}; win change 1.6
- n 94: fell back (backline, 2.0 of 8), fell back (midline, 1.7 of 8), fought (midline, 0.6 of 8), fell back (frontline, 0.6 of 8); named as {'held, fell back': 38, 'pushed, fell back': 25, 'held, fought': 8}; win change -0.2 UNNAMED
*split in base* (3 groups, separation 0.2):
- n 71: fought (midline, 2.2 of 8), fought (backline, 1.1 of 8), fought (frontline, 0.9 of 8), held (backline, 0.9 of 8); named as {'defended without a collapse': 43, 'collapsed': 24, 'missed': 4}; win change 2.1
- n 41: fell back (midline, 2.7 of 8), fell back (backline, 1.4 of 8), fell back (frontline, 0.8 of 8); named as {'collapsed': 21, 'defended without a collapse': 15, 'missed': 5}; win change -5.1 UNNAMED
- n 35: advanced (midline, 2.4 of 8), advanced (backline, 1.3 of 8), advanced (frontline, 0.5 of 8), died (midline, 0.5 of 8); named as {'collapsed': 16, 'defended without a collapse': 16, 'missed': 3}; win change 0.8 UNNAMED

## 8. What results and causes are worth

Win points for the team it happened to, from 61 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 208 | +0.9 | -7.9 to +9.4 | +2.4 | no |
| capture | 587 | +2.4 | +1.3 to +3.3 | +2.8 | yes |
| death (any) | 1204 | -4.9 | -7.5 to -2.7 | -3.6 | yes |
| death: against a spike build | 288 | -7.2 | -10.6 to -2.6 | -2.5 | yes |
| death: against other builds | 916 | -4.2 | -7.1 to -1.4 | -3.9 | yes |
| death: back within 20 s | 190 | -1.7 | -5.2 to +2.0 | -0.1 | no |
| death: down 20 to 60 s | 447 | -6.2 | -9.7 to -2.5 | -2.5 | yes |
| death: down 60 s or more | 567 | -5.0 | -7.8 to -2.3 | -5.6 | yes |
| death: healer | 411 | -4.4 | -6.9 to -2.0 | -4.4 | yes |
| death: healer in own base or pit, back within 15 s (likely deliberate) | 26 | +2.1 | -2.0 to +9.0 | +2.8 | no |
| death: healer, other | 385 | -4.8 | -7.3 to -2.5 | -4.9 | yes |
| death: not a healer | 793 | -5.2 | -8.1 to -2.1 | -3.1 | yes |
| death: team boosted (morale above zero) | 171 | -22.3 | -36.1 to -9.7 | -7.0 | yes |
| death: team not boosted | 1033 | -2.0 | -5.9 to +2.1 | -3.0 | no |
| footman lost (base NPC) | 188 | +2.7 | -2.1 to +7.4 | +1.5 | no |
| pit NPC lost (any): taken by a spike build | 88 | -4.9 | -9.3 to +1.0 | -1.5 | no |
| pit NPC lost (any): taken by other builds | 417 | -1.9 | -4.8 to +1.0 | -1.3 | no |
| pit NPC lost: archer | 291 | -0.1 | -2.5 to +2.8 | +0.6 | no |
| pit NPC lost: bodyguard | 71 | -2.1 | -6.0 to +0.8 | -0.1 | no |
| pit NPC lost: knight | 143 | -7.4 | -11.3 to -3.8 | -5.8 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value.

*deaths* (per 10 s in that state; result worth -4.9 points, base rate 1.4%):

- enemies within 1,500 7.5 to 8: result chance +2.5 points, worth -0.12 win points
- current health % 1 to 47.5: result chance +10.7 points, worth -0.53 win points
- own minus enemy team strength -901 to -523: result chance +1.3 points, worth -0.06 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.5 points, worth -0.12 win points
- allies within 1,500 0 to 0.5: result chance +1.6 points, worth -0.08 win points
- match minute 20.95 to 28: result chance +1.6 points, worth -0.08 win points
- enemy enchantment removal skills 5.5 to 6: result chance -1.3 points, worth +0.06 win points

*kill conversion* (per burst, for the attacking team; result worth +4.9 points, base rate 29.7%):

- damage in the 2 s burst 518.5 to 839: result chance +31.5 points, worth +1.55 win points
- target's health ceiling 0.4 to 0.56: result chance +34.1 points, worth +1.67 win points
- target health % when the burst started 0 to 38.5: result chance +25.8 points, worth +1.26 win points
- target's healers in range 0 to 0.5: result chance +32.2 points, worth +1.58 win points
- attacking minus target team strength 459 to 901: result chance +22.9 points, worth +1.12 win points
- target team's prot skills 5.5 to 6.5: result chance +19.7 points, worth +0.97 win points
- a prot on the target 0.5 to 1: result chance -7.7 points, worth -0.38 win points
- match minute 0.3 to 1.45: result chance -14.8 points, worth -0.72 win points

*npc loss* (per case, for the defending team; result worth -2.4 points, base rate 18.5%):

- own players in the pit 7.5 to 8: result chance -15.5 points, worth +0.38 win points
- damage on the pit NPCs in the last 5 s 367 to 1170: result chance +36.4 points, worth -0.89 win points
- own players alive outside the pit 0 to 0.5: result chance +17.6 points, worth -0.43 win points
- share of the attacking team's live players in the pit (OG comms: merge before pushing the pit) 0.87 to 0.94: result chance +7.8 points, worth -0.19 win points
- of which healers 0 to 0.5: result chance +15.9 points, worth -0.39 win points
- attackers' measured damage per second against a Lord (benchmarks) 18.75 to 28.65: result chance -6.7 points, worth +0.17 win points
- enemy players in the pit 7.5 to 8: result chance +7.0 points, worth -0.17 win points
- match minute 23.45 to 28: result chance -4.7 points, worth +0.12 win points

## Why: five events of the new matches

For each, the engine's account of why it happened, every number measured and placed against the same role or situation in every stored match (forensics.py, events.py), with models that never saw the match.

### Men v hook (ad75813a), 6:22 to 6:40: Men lost 2 players on the push side

1. **Result**: deaths Men 4 until all were back; hook lost bodyguard; captures {'hook': 1}; flag lead +7 s; death penalty {'Men': 20, 'hook': 0}. Win chance for Men 99.2% -> 28.1% (-71.1); moved by alive_diff -32.1, lord_health_diff +22.3, minute & lord_damage_diff -21.8, down_diff_s -19.2, morale_diff & morale_total -19.0.
2. **Mechanics** (deaths model that never saw this match, a few seconds before each death; what raised the risk most):
   - Men Earth Ele at 6:37 (engine's cause: backline down (1 monk dead)): risk 79.2% at 6:35; health +41.1, health_pct & hexes_on_own_healers +27.0, own healers dead +20.0, local numbers +19.5 [health 15%, ceiling 1.0, 7 enemies and 3 allies near, 1 healers in range, 2 hexes]
   - Men Water Ele at 6:40 (engine's cause: backline down (1 monk dead)): risk 14.7% at 6:35; health +41.1, health_pct & hexes_on_own_healers +26.2, own healers dead +20.0, local numbers +13.4 [health 18%, ceiling 1.0, 3 enemies and 4 allies near, 2 healers in range, 1 hexes]
   - why Men Earth Ele's health dropped (forensics, against the same role in every stored match):
     - Position: yes (nearest allied healer 814 in the last 5 s, nearest enemy 205, allies in casting range 1, enemies 6)
     - Prots: no prots (0 from teammates, 0 self; 0 of 0 landed); damage 625 (26% attacks, 8% armor-ignoring), burst 225 in 2 s at 6:30.1; knockdowns 1, knockdown immunity up for 0
     - Healers under interrupt pressure: usual (healers 3, interrupts_per_min 3.0, interrupted 1, casts 16, finished_share 0.81, dazed 0, knockdowns 0, hexes 10)
     - Damage off shield sets: no (team share 0.07, a shield would have stopped about 0)
     - Own damage: usual (31.3 per second on [('hook 8 Monk', 264), ('hook Air Ele', 137)]); enemy damage: high (68.1 per second)
     - Peel: no (peel on a burst is rare: most bursts on this role get none) (0 of 4 attackers controlled; longest free 20.0 s)
     - Casting: unclear (casts 6, interrupted 1, cancelled 2, while_dazed 0)
   - why Men Water Ele's health dropped (forensics, against the same role in every stored match):
     - Position: no (nearest allied healer 188 in the last 5 s, nearest enemy 744, allies in casting range 3.0, enemies 3.0)
     - Prots: late or interrupted (1 from teammates, 1 self; 2 of 2 landed); damage 404 (17% attacks, 30% armor-ignoring), burst 129 in 2 s at 6:20.8; ready and in range but not used: Men 8 Monk Shielding Hands
     - Healers under interrupt pressure: usual (healers 3, interrupts_per_min 3.0, interrupted 1, casts 14, finished_share 0.71, dazed 0, knockdowns 0, hexes 9)
     - Damage off shield sets: usual (team share 0.18, a shield would have stopped about 17)
     - Own damage: usual (28.6 per second on [('hook Necromancer 1', 232), ('hook 8 Monk', 166)]); enemy damage: high (78.1 per second)
     - Peel: partly (controlled, but an attacker was left free for 20.0 s) (1 of 3 attackers controlled; longest free 20.0 s)
     - Casting: unclear (casts 3, interrupted 0, cancelled 0, while_dazed 0)
3. **Setup** (phase 6:09 to 6:30):
   - Men plan weak side holding: push side 5v7 hold (8 Monk, 7 Monk, Water Ele, Air Ele 2, Earth Ele); push side 2v1 convert (Fire Ele, Air Ele 1)
     where the deaths came: 5v7, 3 damage, 2 healers, pressure 23/s, incoming 46/s, sustain margin +40, uptime 33%, control received 4 interrupts (1 on healers), 0 knockdowns
   - hook plan power play, weak side holding: backside 7v5 convert (7 Monk, Prot, Stand Mes, Mes/A, Necromancer 2, Necromancer 1, Air Ele); backside 1v2 hold (8 Monk)
     where the deaths came: 7v5, 5 damage, 2 healers, pressure 58/s, incoming 23/s, sustain margin +2, uptime 73%, control received 0 interrupts (0 on healers), 1 knockdowns
4. **Decision**: no decision point for Men in the 45 s before.
**Why, in short**: Men fought 5v7 on the push side (job: hold) with sustain margin +40 while the rest were push side (convert); the Earth Ele died because no prot landed in time (0 of 0 landed), knocked down 1 times with no knockdown immunity up, the enemy hit unusually hard (68.1 per second); the Water Ele died because no prot landed in time (2 of 2 landed; 8 Monk Shielding Hands ready and unused), the enemy hit unusually hard (78.1 per second), its attackers were not peeled (partly (controlled, but an attacker was left free for 20.0 s)).
5. **Context**: Men: 7 up (main 5), flags down -18 s, DP -45, NPCs K2 A2 B1, Lord dmg 0; hook: 8 up (main 7), flags up +18 s, DP 80, NPCs K0 A2 B1, Lord dmg 0; stand Men, boost in 69 s; builds other v other; situation: outnumbered where it fought 5v7 (Prot down).

### ohno v Fun (1cb73c20), 20:04 to 20:19: Fun lost 1 player on the backside

1. **Result**: deaths Fun 2 until all were back; flag lead +26 s; death penalty {'Fun': -30, 'ohno': 1}. Win chance for Fun 45.3% -> 3.3% (-42.0); moved by lord_damage_diff & pit_pressure_diff -43.9, alive_diff -14.0, pit_pressure_diff +13.3, down_diff_s -13.2, morale_diff & archers_diff -6.0.
2. **Mechanics** (deaths model that never saw this match, a few seconds before each death; what raised the risk most):
   - Fun Air Ele 1 at 20:19 (engine's cause: positioning: out of range of its monks): risk 6.6% at 20:15; health +29.4, enemies within 1,500 +12.9, group_no_healer +12.1, damage taken (3 s) +9.2 [health 51%, ceiling 1.0, 6 enemies and 5 allies near, 0 healers in range]
   - why Fun Air Ele 1's health dropped (forensics, against the same role in every stored match):
     - Position: yes (nearest allied healer 4925 in the last 5 s, nearest enemy 322, allies in casting range 5.0, enemies 4.0)
     - Prots: no prots (0 from teammates, 0 self; 0 of 0 landed); damage 574 (34% attacks, 66% armor-ignoring), burst 290 in 2 s at 20:14.2
     - Healers under interrupt pressure: usual (healers 2, interrupts_per_min 0.0, interrupted 0, casts 5, finished_share 1.0, dazed 0, knockdowns 0, hexes 0)
     - Damage off shield sets: usual (team share 0.56, a shield would have stopped about 24)
     - Own damage: usual (43.9 per second on [('ohno Dervish 2', 527), ('ohno Mesmer', 351)]); enemy damage: usual (39.5 per second)
     - Peel: no (peel on a burst is rare: most bursts on this role get none) (0 of 2 attackers controlled; longest free 20.0 s)
     - Casting: unclear (casts 5, interrupted 0, cancelled 1, while_dazed 0)
3. **Setup** (phase 20:00 to 20:09):
   - Fun plan holding in the pit: own pit 5v0 free (8 Monk, 7 Monk, Air Ele 4, Air Ele 2, Fire Ele); backside 3v6 hold (Air Ele 5, Air Ele 3, Air Ele 1)
     where the deaths came: 3v6, 3 damage, 0 healers, pressure 0/s, incoming 0/s, sustain margin +0, uptime 11%, control received 0 interrupts (0 on healers), 0 knockdowns
   - ohno plan power play: push side 6v3 convert (8 Monk, 7 Monk, Dervish 2, Mesmer, Dervish 1, Monk 5 (WoC)); push side 2v0 free (Fire Ele, Water Ele)
     where the deaths came: 6v3, 4 damage, 2 healers, pressure 0/s, incoming 0/s, sustain margin +10, uptime 8%, control received 0 interrupts (0 on healers), 0 knockdowns
4. **Decision** (boost clock at 19:39): Fun chose 'not running' (fell back 6, held 2); usual there: not running, fought; that choice is worth +0.0 points against the usual [+0.0, +0.0].
**Why, in short**: Fun fought 3v6 on the backside (job: hold) with sustain margin +0 while the rest were own pit (free); the Air Ele 1 died because no prot landed in time (0 of 0 landed), position (no allied healer within casting range, nearest enemy 322), its attackers were not peeled (no (peel on a burst is rare: most bursts on this role get none)); after choosing 'not running' at the boost clock.
5. **Context**: Fun: 8 up (main 5), flags down -54 s, DP -30, NPCs K0 A0 B0, Lord dmg 0; ohno: 8 up (main 6), flags up +54 s, DP 79, NPCs K1 A0 B1, Lord dmg 13981; stand ohno, boost in 5 s; builds invoke spike v balance; situation: even fight.

### Flag swing: ohno v xxx (29aad8d4), 1:30.0 to 2:50.0
**Result**: ohno's flag lead +79 s -> -73 s (-152 s). Stand: ohno -> xxx.
**Captures** (flag model: fastest possible answer after the enemy's capture):
- xxx capped 2:50.0 by AoB Derv, 125 s after ohno's capture; fastest possible 21 s, so 104 s slower
**Runs** (each run: outcome, and what was done to the runner):
- xxx Mesmer 0:47.0 to 1:25.0 (38 s): dropped, lowest health 92%, escort ['AoB Derv', 'Prot', '7 Monk'], pushed by ['Hammer']
- xxx AoB Derv 2:03.0 to 2:13.0 (10 s): dropped, lowest health 83%, escort none, pushed by nobody
- xxx Prot 2:16.0 to 2:18.0 (2 s): dropped, lowest health 100%, escort ['AoB Derv', 'Mesmer', '7 Monk'], pushed by nobody
- xxx AoB Derv 2:19.0 to 2:50.0 (31 s): captured, lowest health 77%, escort ['7 Monk'], pushed by ['Mesmer', 'AoB Derv']
- ohno output in the 20 s before 2:50.0: 57.1 damage per second (above the 50th percentile for team (median 37.1, n 3825)), top target share 0.41, spikes 0
- xxx output in the 20 s before 2:50.0: 44.8 damage per second (above the 50th percentile for team (median 37.1, n 3825)), top target share 0.47, spikes 0

### Power play without a kill: ohno v xxx (29aad8d4), 25:07.0 to 26:05.0
**Situation**: main 7v4, alive 8v8, flags down (-29 s), DP 1, boost in 58; choice pushed (advanced 6, fell back 1, held 1); deaths {'ohno': 0, 'xxx': 0} in 58 s
**The fight's shape** (every 5 s: own main, the enemy group it faced, distance between them, that group's distance to the rest of its team): 25:07.0 7v4 1753 apart, 5528 from its others; 25:12.0 6v4 1010 apart, 3917 from its others; 25:17.0 6v4 940 apart, 2751 from its others; 25:22.0 6v5 484 apart, 5708 from its others; 25:27.0 6v5 99 apart, 5409 from its others; 25:32.0 6v5 129 apart, 5251 from its others; 25:37.0 6v5 237 apart, 4337 from its others; 25:42.0 6v5 89 apart, 2857 from its others; 25:47.0 6v6 296 apart, 11159 from its others; 25:52.0 6v6 292 apart, 10945 from its others; 25:57.0 6v5 245 apart, 2145 from its others; 26:02.0 6v5 144 apart, 2943 from its others
**ohno's damage**: 17.9 per second (below the 20th percentile for team (median 37.1, n 3825)); top target share 0.35 (below the 20th percentile for team (median 0.49, n 3825)); targets [('xxx AoB Derv', 367), ('xxx 7 Monk', 355), ('xxx Prot', 210), ('xxx Mesmer', 108)]; dealers [('ohno Hammer', 447), ('ohno Mesmer', 278), ('ohno AoB Derv', 174), ('ohno Ritualist', 141)]
- phase 24:09.0 to 25:27.0: 8v4 (backside, job convert), damage uptime 0.2, damage-seconds lost {'moving': 261, 'idle': 38, 'carrying': 12, 'knocked down': 2}
- phase 25:27.0 to 26:00.0: 6v5 (push side, job convert), damage uptime 0.45, damage-seconds lost {'moving': 62, 'idle': 9, 'knocked down': 1}
- phase 26:00.0 to 26:41.0: 6v4 (enemy pit, job convert), damage uptime 0.59, damage-seconds lost {'moving': 48, 'idle': 20, 'weakness (attacking weakened)': 13}
**xxx's answer**: healing 56 per second ({'xxx Ritualist': 1156.6999999999998, 'xxx Prot': 561, 'xxx 8 Monk': 443, 'xxx Fire Ele': 428}); prots {'Guardian': 9, 'Shielding Hands': 1, 'Aura of Stability': 2, 'Shield Guardian PvP': 2, 'Reversal of Fortune': 1}
- ohno's knockdowns landed 2; xxx's knockdown immunity casts 2
- Pressure on xxx's healers: healers 3, interrupts_per_min 0.0, interrupted 0, casts 21, finished_share 1.0, dazed 0, knockdowns 1, hexes 0 (around the median for team (median 0, n 4312))
- Snares, Blind and Weakness ohno put on xxx: none

### Spike by BcS on Apes 8 Monk (04befe7e) at 8:26.4: 806 in 3 s, survived
**Hits**: 8:26.4 Dervish Wounding Strike PvP 5; 8:26.4 Dervish Wounding Strike PvP 23; 8:26.5 Mesmer Energy Burn 90; 8:26.7 Dervish Wounding Strike PvP 26; 8:27.1 Water Ele Mind Freeze PvP 49; 8:27.1 Water Ele Mind Freeze PvP 49; 8:27.2 Paragon auto-attack 58; 8:27.8 Dervish Wounding Strike PvP 5; 8:27.8 Dervish Wounding Strike PvP 38; 8:28.3 Mesmer Power Spike 120; 8:28.5 Paragon auto-attack 59; 8:28.6 Mesmer Power Spike 14; 8:28.6 Air Ele 2 Lightning Bolt 69; 8:28.9 Water Ele Glowing Ice 53; 8:28.9 Dervish auto-attack 5; 8:28.9 Dervish auto-attack 33; 8:29.2 Air Ele 1 Lightning Bolt 55; 8:29.2 Air Ele 1 Lightning Bolt 55
**Landing**: spread 2.1 s first to last big hit (median of spikes that killed 1.1, of spikes survived 1.7); 37% of the damage inside 1 s (median of spikes that killed 0.75, of spikes survived 0.65); 6 attackers (median of spikes that killed 4.0, of spikes survived 4.0)
- Follow-up 3 to 6 s later: 100 damage (Shatter Enchantment)
**Up on the target at the first hit**: nothing
**Cast on the target** (from 3 s before): 8:27.9 Apes Prot Spirit Bond PvP (finished, +1.5 s); 8:28.2 Apes 7 Monk Infuse Health (finished, +1.8 s); 8:27.9 Apes 8 Monk Word of Healing (interrupted, +1.5 s); 8:28.4 Apes Necromancer Foul Feast (finished, +2.0 s); 8:28.1 Apes Ritualist Spirit Light Weapon (finished, +1.7 s); 8:29.4 Apes Prot Life Sheath (finished, +3.0 s); 8:30.1 Apes 7 Monk Heal Other (finished, +3.7 s)
- Healing on the target in the next 6 s: 1142 ({"Apes Prot unnamed (an enchantment's proc or a heal recorded without its skill)": 605, "Apes 7 Monk unnamed (an enchantment's proc or a heal recorded without its skill)": 424, "Apes Ritualist unnamed (an enchantment's proc or a heal recorded without its skill)": 63, "Apes 8 Monk unnamed (an enchantment's proc or a heal recorded without its skill)": 50})
**Control on the spikers** (2 s before to 3 s after): 8:26.3 BcS Air Ele 1 interrupted (Invoke Lightning) by Apes Mesmer; 8:27.1 BcS Air Ele 2 blind
- Target's set: Wand #1 + Focus #1; health 8:25.4 100%, 8:26.4 100%, 8:27.4 66%, 8:28.4 26%, 8:29.4 75%, 8:30.4 82%, 8:31.4 100%, 8:32.4 100%

### Pit NPCs lost: Apes v BcS (04befe7e) around 6:32.0
**Lost**: 6:32.0 knight (push); 6:35.0 knight (push)
**BcS's split** 5:41.0 to 6:04.0: ['Water Ele'] (split), entered base no, NPC damage {}, NPC kills []
- main numbers meanwhile [7.0, 5.2]
**Apes at 6:32.0**: Dervish: own base (contest); Warrior: own base (contest); Necromancer: own base (contest); Ritualist: own base (contest); Mesmer: own base (contest); Prot: own base (contest); 7 Monk: own base (contest); 8 Monk: own base (contest)
- BcS output 5:41.0 to 6:04.0: 55.8 per second
- Apes output 5:41.0 to 6:04.0: 28.5 per second

## 9. Detailed learnings snapshot

Descriptive measurements across all 61 trained matches (the latest batch, 8 matches, in brackets where it differs). Not causal on their own: they point to questions and candidate variables.

**Runners** (spawn to capture; pushed = an enemy hit the carrier):

| Runner | Runs | Captured | Median s to capture | Dropped | Pushed | Runs by winners |
|---|---|---|---|---|---|---|
| Mes/A | 155 | 52% | 42 (36) | 70 | 52% | 42% |
| AoB Derv | 139 | 58% | 31.0 (34.0) | 57 | 40% | 56% |
| Ritualist | 101 | 50% | 35.0 (27.5) | 49 | 32% | 62% |
| Mesmer | 94 | 53% | 36.0 (41) | 43 | 37% | 57% |
| 8 Monk | 60 | 30% | 32.0 (11.5) | 41 | 20% | 45% |
| Hammer | 55 | 49% | 27 (29) | 27 | 29% | 51% |
| Dervish | 53 | 58% | 26 (13.0) | 21 | 45% | 60% |
| Stand Mes | 47 | 66% | 31 (38) | 15 | 34% | 49% |
| Monk 4 (WoC) | 39 | 62% | 42.5 (19) | 15 | 54% | 59% |
| Necromancer | 33 | 61% | 24.0 | 12 | 39% | 9% |

Double running: single 843 runs (49% by winners); half 262 runs (52% by winners).

**Flag answers** (answering the enemy's capture): winners: 271 answers, median 38 s, 2 s slower than possible, 43 answers 30 s+ slower; losers: 255 answers, median 53 s, 8 s slower than possible, 81 answers 30 s+ slower.

**Skills: kill participation** (share of casts at an enemy who died within 5 s; 15+ casts):

- Highest: Augury of Death 33% of 82; Shatter Storm 31% of 144; Word of Censure 30% of 1338; Signet of Rage 29% of 68; Wounding Strike PvP 27% of 63; Decapitate 25% of 102; Knee Cutter 25% of 24; Horns of the Ox 23% of 26; Chest Thumper 22% of 172; Disrupting Throw 21% of 66; Castigation Signet 20% of 478; Invoke Lightning 20% of 529
- Lowest: Parasitic Bond 0% of 155; Reckless Haste 0% of 40; Spiteful Spirit 0% of 55; Images of Remorse 0% of 20; Diversion 0% of 17; Flare 0% of 41; Axe Rake 0% of 19; Crippling Slash 0% of 16

**Interrupts:** skills interrupted most (whose): Healing Burst on the 7 Monk 209; Guardian on the Prot 144; Guardian on the 8 Monk 131; Spirit Light Weapon on the Ritualist 102; Blessed Light on the 8 Monk 101; Guardian on the 7 Monk 88; Cure Hex on the 7 Monk 87; Shield Guardian PvP on the Prot 77; Lightning Strike on the Air Ele 70; Word of Censure on the Monk 4 (WoC) 69. Interrupt skills landing most: Power Spike 894; Complicate 879; Power Leak 415; Psychic Instability PvP 366; Cry of Frustration 235; Savage Shot 230; Hammer Bash 189; Distracting Shot 109.

**Knockdowns by skill:** Coward 1311; Hammer Bash 1179; Psychic Instability PvP 415; Lightning Surge 361; Mind Shock PvP 210; "Coward!" 134; Bull's Strike 85; Gale 78.

**Spikes survived** (400+ damage in 3 s on one player; survived = alive 8 s later): winners 142 of 179 (79%); losers 216 of 367 (59%). By target: 7 Monk 69% of 59; Prot 60% of 57; Stand Mes 72% of 53; 8 Monk 54% of 52; AoB Derv 61% of 49; Mes/A 86% of 37; Mesmer 63% of 30; Necromancer 61% of 28; Hammer 64% of 28; Air Ele 71% of 24; Dervish 62% of 24; Ritualist 70% of 23; Paragon 59% of 17; Ranger 62% of 16; Water Ele 73% of 11.

**Monks** (per 2-minute phase alive 60 s+): winners: 11.0 casts a minute, 0.44 fakes, idle 0 s while an ally was hurt, reaction 1.6 s, bursts answered 70%; losers: 11.5 casts a minute, 0.51 fakes, idle 0 s while an ally was hurt, reaction 1.3 s, bursts answered 61%.

**Deaths** (1056): 366 with a knockdown on the victim; 319 had a monk cast on the victim in the last 5 s. Monk skills interrupted in the 6 s before a death: Healing Burst 43; Blessed Light 43; Guardian 33; Reversal of Fortune 21; Shield Guardian PvP 19; Signet of Rejuvenation 12; Cure Hex 12; Word of Healing 10.

## 10. For Denning

- Which curves look wrong to you? A correction (direction, cap, drop, or a pair to always test) is logged with your reason and tested on held-out matches.
- Do any surprises remind you of something the variables don't capture (a missing variable)?
- Any variable you think matters that isn't listed?

