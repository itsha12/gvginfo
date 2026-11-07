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
- glass box: all 77% (0.55), 0-5 min 84% (0.378), 5-10 min 79% (0.51), 10-15 min 71% (0.717), 15-end min 71% (0.712), matches lasting 15 min+ 71% (0.688), matches even on strength (gap under 200) 59% (0.972)
- glass box without corrections: all 78% (0.553), 0-5 min 84% (0.376), 5-10 min 79% (0.5), 10-15 min 74% (0.689), 15-end min 70% (0.761), matches lasting 15 min+ 71% (0.693), matches even on strength (gap under 200) 59% (0.964)
- black box: all 72% (1.077), 0-5 min 78% (0.851), 5-10 min 74% (0.982), 10-15 min 67% (1.241), 15-end min 64% (1.383), matches lasting 15 min+ 65% (1.366), matches even on strength (gap under 200) 55% (1.737)
- Gain over strength alone (log loss, resampling whole matches): -0.132 (90% range -0.309 to -0.001).
- Change since batch 5: glass box log loss 0.53 -> 0.55; strength only 0.439 -> 0.418.

## 2. What it leans on

- **lord_dps_enemy** 0.694 (new): enemy build's measured Lord damage per second
- **lord_dps_own** 0.688 (new): own build's measured Lord damage per second if all its non-healers were at the Lord
- **knights_diff & map_flag_run** 0.456 (new): own minus enemy pit knights alive TOGETHER WITH the map's flag run Y: distance from the flag spawn to the stand (average of both sides)
- **spike_killable_diff** 0.451 (was 0.302): enemy minus own players within one spike of the other side (DP stacking; 0 unless a spike build is involved)
- **morale_diff & map_pit_to_stand** 0.393 (new): own minus enemy morale summed over players (boosts +, death penalty -) TOGETHER WITH the map's distance from a pit to the stand (average of both sides)
- **morale_diff & map_flag_run** 0.354 (new): own minus enemy morale summed over players (boosts +, death penalty -) TOGETHER WITH the map's flag run Y: distance from the flag spawn to the stand (average of both sides)
- **morale_diff** 0.353 (was 0.563): own minus enemy morale summed over players (boosts +, death penalty -)
- **knights_diff** 0.347 (was 0.242): own minus enemy pit knights alive
- **spike_build_enemy** 0.271 (new): enemy build is a spike build
- **archers_diff & map_flag_run** 0.271 (new): own minus enemy pit archers alive TOGETHER WITH the map's flag run Y: distance from the flag spawn to the stand (average of both sides)
- **spike_build_own** 0.269 (new): own build is a spike build (1) or not (0)
- **stand** 0.206 (was 0.202): who holds the flag stand: 1 own, 0 nobody, -1 enemy

## 3. The curves in words

Points = win-chance points added to an otherwise even game at each range of the variable.

- **lord_dps_enemy** rises from +9.4 to +22.2 points (35.8..65.45: +9.4; 78.4..83.15: +8.4; 83.7..88.5: -11.4; 91.2..98.6: +4.7; 102.6..105.45: -18.2; 106.0..111.8: +4.3; 117.1..135.25: +22.3)
- **lord_dps_own** falls from -9.3 to -21.6 points (35.8..65.45: -9.3; 78.4..83.15: -8.7; 83.7..88.5: +11.0; 91.2..98.6: -4.9; 102.6..105.45: +17.9; 106.0..111.8: -4.4; 117.1..135.25: -21.6)
- **knights_diff & map_flag_run** (interaction): see wp_model.md
- **spike_killable_diff** rises from -47.1 to +47.3 points (-8.0..-7.5: -47.1; -6.5..-4.5: -46.5; -2.5..-1.5: -45.6; -0.5..0.5: -0.2; 1.5..2.5: +46.3; 4.5..7.5: +47.0)
- **morale_diff & map_pit_to_stand** (interaction): see wp_model.md
- **morale_diff & map_flag_run** (interaction): see wp_model.md
- **morale_diff** rises from -15.8 to +19.4 points (-470.0..-186.5: -15.8; -141.0..-109.5: -12.7; -83.5..-46.5: -9.7; -15.5..-0.5: -2.2; 0.5..19.5: +1.4; 52.5..91.5: +9.4; 124.5..169.5: +13.0)
- **knights_diff** rises from -18.7 to +18.9 points (-2.0..-1.5: -18.7; -1.5..-0.5: -16.1; -0.5..0.5: +0.0; 0.5..1.5: +15.8; 1.5..2.0: +18.9)
- **spike_build_enemy** falls from +4.0 to -20.1 points (0.0..0.5: +4.0; 0.5..1.0: -20.1)
- **archers_diff & map_flag_run** (interaction): see wp_model.md

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

- split_diff: 0.55 without, 0.548 with: does not improve yet. own minus enemy players on a split (away from their main group on the enemy half, not carrying). Proposed batch 1 by Claude: the knights curve runs backwards, maybe standing in for the cost of splitting
- turtle_diff: 0.55 without, 0.574 with: does not improve yet. own minus enemy share of live players at home (own base or pit). Proposed 2026-11-06 from OG comms ([ohno v One], [ohno v Crew]: 'they are turtling, we have to make a play'); comms_vars.py: teams that turtled 60 s won 3 of 13 times
- footmen_diff: 0.55 without, 0.565 with: does not improve yet. own minus enemy footmen alive (base NPCs, not pit NPCs). Proposed 2026-11-06 from OG comms ([ohno v NwAy]: 'this way we don't lose footmen'; [ohno v Fun]: fake collapse to the footmen)
- no_healer_groups_diff: 0.55 without, 0.558 with: does not improve yet. own minus enemy groups of 2+ with no healer. Proposed 2026-11-06 from OG comms ([ohno v One]: keep a prot and a monk on one side, the Rit and a monk on the other); comms_vars.py: such groups lose players twice as often
- solo_healers_diff: 0.55 without, 0.568 with: does not improve yet. own minus enemy healers with no other own healer within casting range. Proposed 2026-11-06 from OG comms ('solo monk, go on the monk'); Denning: a monk alone has no other monk to support it

**Surprises** (moments where the held-out model was most confident about the team that went on to lose; each points to something the variables don't capture yet):

- 옷옷옷옷 v Men (36a65ac6) at 14:15: a model that never saw this match gave 옷옷옷옷 13.8%, and 옷옷옷옷 won. Why it thought so: morale_diff -30.2, team strength +17.5, morale_diff & morale_total -10.5, stand -6.7, boost_clock -5.3
- hdm v HC (28447c4a) at 15:30: a model that never saw this match gave HC 2.5%, and HC won. Why it thought so: knights_diff -36.3, archers_diff -29.9, morale_diff -26.8, morale_diff & morale_total +17.0, team strength -16.4
- OG v hold (49eec28d) at 4:30: a model that never saw this match gave OG 1.2%, and OG won. Why it thought so: lord_health_diff -37.8, morale_total & archers_diff -34.4, morale_diff & archers_diff -27.1, morale_diff -22.9, team strength +19.0
- Team v cope (6c7dfcaa) at 10:00: a model that never saw this match gave Team 2.6%, and Team won. Why it thought so: morale_diff -23.9, morale_diff & morale_total -22.8, morale_total & archers_diff -21.0, pit_pressure_diff +11.4, team strength -11.0
- RACK v hdm (1f65fd3b) at 15:15: a model that never saw this match gave RACK 0.3%, and RACK won. Why it thought so: morale_diff -30.5, morale_diff & archers_diff -28.6, knights_diff -27.8, knights_diff & lord_damage_diff -16.0, team strength -14.0
- BcS v yM (b88983e3) at 11:15: a model that never saw this match gave yM 4.9%, and yM won. Why it thought so: morale_diff -30.5, morale_diff & archers_diff -28.6, team strength +19.5, morale_diff & morale_total -13.2, alive_diff -7.6

## 5. Denning's rulings seen through the model

Win chance from a model that never saw the match, 20 s before and 60 s after each ruled moment. Contributions are points for an otherwise even game (the curves' scale).

- hdm v HC (28447c4a) 5:01 (split answered), HC: 28.6% 20 s before -> 29.3% 60 s after (+0.7). After: knights_diff -36.3, team strength -16.4, pit_pressure_diff +14.7, flag_lead & morale_diff +11.2
- hdm v HC (28447c4a) 5:01 (split answered), hdm: 71.0% 20 s before -> 72.8% 60 s after (+1.8). After: knights_diff +37.5, team strength +16.4, flag_lead & morale_diff -16.2, pit_pressure_diff -15.8
- hdm v HC (28447c4a) 1:02 (split detection), HC: 32.6% 20 s before -> 12.7% 60 s after (-19.9). After: flag_lead & morale_diff -17.9, team strength -16.4, flag_lead & knights_diff -8.0, carrying_diff -7.6
- hdm v HC (28447c4a) 1:02 (split detection), hdm: 66.9% 20 s before -> 84.7% 60 s after (+17.8). After: team strength +16.4, flag_lead & morale_diff +16.0, flag_lead -7.7, carrying_diff +7.3
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), HC: 3.2% 20 s before -> 1.4% 60 s after (-1.8). After: knights_diff -36.3, archers_diff -29.9, morale_diff & archers_diff -22.2, team strength -16.4
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), hdm: 96.0% 20 s before -> 97.4% 60 s after (+1.4). After: knights_diff +37.5, archers_diff +29.3, morale_diff & archers_diff +20.0, team strength +16.4
- hdm v HC (bbef1904) 8:10 (death), HC: 47.9% 20 s before -> 6.0% 60 s after (-41.9). After: team strength -16.0, alive_diff -14.2, down_diff_s -11.9, morale_diff -11.5
- hdm v HC (bbef1904) 8:10 (death), hdm: 49.7% 20 s before -> 94.4% 60 s after (+44.7). After: down_diff_s +17.1, team strength +16.0, alive_diff +13.3, morale_diff +13.0
- Men v HC (faec428a) 9:31 (death), HC: 25.8% 20 s before -> 33.0% 60 s after (+7.2). After: team strength -14.9, archers_diff +10.3, stand -6.3, knights_diff -4.2
- Men v HC (faec428a) 9:31 (death), Men: 76.2% 20 s before -> 70.9% 60 s after (-5.3). After: team strength +14.9, archers_diff -8.8, stand +6.2, flag_lead & knights_diff +3.9

## 6. Why: the node models

Each explains one result from what happened before it (time order enforced), tested on matches it never saw. AUC = how often a moment that led to the result scores above one that didn't (0.5 = guessing, 1 = perfect).

**deaths** (61 matches, 134313 moments, 3716 results): adds to the simple baseline (AUC 0.916 against 0.799 for health_pct and damage_taken_3s alone).
- **enemies_near** (enemies within 1,500) rises from -21.8 to +24.5 points (0.0..0.5: -21.8; 0.5..1.5: -9.8; 1.5..2.5: +0.9; 2.5..3.5: +3.0; 3.5..4.5: +12.1; 4.5..5.5: +13.4; 5.5..6.5: +14.9; 6.5..7.5: +16.8; 7.5..8.0: +24.5)
- **health_pct** (current health %) falls from +40.9 to -6.3 points (1.0..47.5: +40.9; 59.5..67.5: +24.2; 73.5..78.5: +10.6; 82.5..85.5: +6.4; 88.5..91.5: +1.5; 93.5..95.5: -2.1; 97.5..99.5: -4.8)
- **strength_gap** (own minus enemy team strength) falls from +16.5 to -10.9 points (-901.0..-523.0: +16.5; -360.5..-274.5: +10.1; -122.5..-102.0: +4.0; -45.0..0.0: +1.1; 60.5..104.5: -7.6; 122.5..274.5: -9.6; 360.5..523.0: -10.8)
- **local_diff** (allies minus enemies within 2,000) falls from +24.4 to -12.1 points (-8.0..-3.5: +24.4; -2.5..-1.5: +12.2; -0.5..0.5: -4.1; 1.5..2.5: -8.5; 3.5..4.5: +8.8; 5.5..7.0: -12.1)
- **allies_near** (allies within 1,500) falls from +18.9 to -8.5 points (0.0..0.5: +18.9; 0.5..1.5: +7.5; 1.5..2.5: +5.3; 2.5..3.5: -1.3; 3.5..4.5: -2.2; 4.5..5.5: -3.7; 5.5..6.5: -5.6; 6.5..7.0: -8.5)
- **minute** (match minute) rises from -5.7 to +18.9 points (0.1..1.25: -5.7; 2.25..3.35: -10.8; 4.45..5.45: -3.6; 6.65..8.05: +0.2; 9.55..11.15: +0.6; 13.05..15.15: +1.2; 17.75..20.95: +6.7)
- **enemy_strips** (enemy enchantment removal skills) falls from +4.8 to -45.2 points (0.0..0.5: +4.8; 0.5..1.5: +5.9; 1.5..2.5: +4.1; 2.5..3.5: -3.3; 3.5..4.5: -4.4; 4.5..5.5: -5.0; 5.5..6.0: -45.2)
- **own_condition_removal** (own condition removal skills) falls from -15.8 to -24.4 points (1.0..1.5: -15.8; 1.5..2.5: +4.8; 2.5..3.5: +5.7; 3.5..4.5: +0.4; 4.5..5.5: +1.3; 5.5..6.5: -11.4; 6.5..7.5: -21.8; 7.5..8.0: -24.4)
- **enemy_interrupts** (enemy interrupt skills) rises from -9.7 to +0.7 points (0.0..0.5: -9.7; 0.5..1.5: +20.0; 1.5..2.5: +6.8; 2.5..3.5: -3.8; 3.5..4.5: -4.6; 4.5..5.5: -0.2; 5.5..6.5: -0.1; 6.5..7.0: +0.7)

**kill conversion** (61 matches, 1025 moments, 304 results): adds to the simple baseline (AUC 0.785 against 0.665 for burst_damage and target_health_pct alone).
- **burst_damage** (damage in the 2 s burst) rises from -8.9 to +29.0 points (250.0..257.5: -8.9; 264.5..274.5: -14.8; 285.5..294.5: -10.5; 307.5..322.5: -4.8; 337.5..354.5: -0.8; 375.0..410.5: +4.1; 449.5..518.5: +25.0)
- **target_ceiling** (target's health ceiling) falls from +30.8 to -15.4 points (0.4..0.56: +30.8; 0.69..0.7: +16.6; 0.78..0.83: +17.3; 0.86..0.9: +13.7; 0.94..0.95: +8.1; 0.99..1.02: -3.3; 1.1..1.1: -15.4)
- **target_health_pct** (target health % when the burst started) falls from +24.8 to -10.5 points (0.0..38.5: +24.8; 50.5..56.5: +8.9; 62.5..68.5: +7.0; 72.5..76.5: +6.6; 79.5..82.5: -4.2; 86.5..90.5: -9.3; 95.5..99.5: -10.2)
- **target_healers_in_range** (target's healers in range) falls from +29.4 to -6.1 points (0.0..0.5: +29.4; 0.5..1.5: -3.2; 1.5..2.5: -7.0; 2.5..3.0: -6.1)
- **strength_gap** (attacking minus target team strength) rises from -15.6 to +22.5 points (-815.0..-434.0: -15.6; -316.5..-226.0: -10.9; -117.5..-10.0: -0.8; 0.0..63.5: +0.8; 75.5..133.0: -3.4; 248.5..274.5: -4.0; 386.0..459.0: +16.2)
- **enemy_prots** (target team's prot skills) is flat from -10.3 to -9.2 points (1.0..4.0: -10.3; 5.5..6.5: +20.0; 7.5..8.5: +8.9; 9.5..10.5: +11.5; 11.5..12.5: -4.6; 13.5..14.5: -6.3; 15.5..16.0: -9.2)
- **target_prot_up** (a prot on the target) falls from +5.0 to -10.0 points (0.0..0.5: +5.0; 0.5..1.0: -10.0)
- **minute** (match minute) rises from -20.8 to +11.8 points (0.3..1.45: -20.8; 2.65..3.75: -2.8; 4.95..6.15: -3.1; 6.95..8.15: -3.1; 9.45..10.85: +3.4; 12.85..15.05: +7.0; 17.15..20.65: +9.4)
- **enemy_blind** (target team's Blind skills) falls from +3.1 to -29.8 points (0.0..0.5: +3.1; 0.5..1.5: -10.8; 1.5..2.5: -21.2; 2.5..3.0: -29.8)
- **own_interrupts_v_enemy_heals** (attackers' interrupt skills minus target team's heals) is flat from -0.6 to -0.3 points (-16.0..-15.5: -0.6; -14.5..-13.5: +6.5; -12.5..-11.5: -0.8; -10.5..-9.5: -3.0; -8.5..-7.5: +3.6; -6.5..-5.5: -6.4; -4.5..-4.0: -0.3)

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

**npc loss** (61 matches, 6867 moments, 1271 results): adds to the simple baseline (AUC 0.808 against 0.748 for attackers and defenders alone).
- **defenders** (own players in the pit) falls from +34.1 to -37.8 points (0.0..0.5: +34.1; 0.5..1.5: +23.1; 1.5..2.5: +14.4; 2.5..3.5: +1.9; 3.5..4.5: -12.3; 4.5..5.5: -13.2; 5.5..6.5: -14.0; 6.5..7.5: -28.1; 7.5..8.0: -37.8)
- **npc_damage_5s** (damage on the pit NPCs in the last 5 s) rises from -16.6 to +34.3 points (0.0..0.5: -16.6; 22.5..36.5: -2.1; 50.5..69.5: +5.6; 88.5..109.5: +12.8; 131.5..157.5: +23.1; 188.5..227.5: +26.3; 278.5..367.0: +30.8)
- **defenders_elsewhere** (own players alive outside the pit) falls from +21.3 to -5.4 points (0.0..0.5: +21.3; 0.5..1.5: +12.6; 1.5..2.5: +12.5; 2.5..3.5: +5.6; 3.5..4.5: -5.2; 4.5..5.5: -15.0; 5.5..6.5: -16.2; 6.5..7.5: -15.0; 7.5..8.0: -5.4)
- **attackers_share** (share of the attacking team's live players in the pit (OG comms: merge before pushing the pit)) rises from -10.3 to +8.7 points (0.12..0.13: -10.3; 0.16..0.23: -6.6; 0.27..0.35: -5.1; 0.42..0.53: +5.7; 0.61..0.65: +8.4; 0.73..0.78: +10.2; 0.87..0.94: +11.1)
- **defender_healers** (of which healers) falls from +19.8 to -6.7 points (0.0..0.5: +19.8; 0.5..1.5: -1.7; 1.5..2.5: -4.7; 2.5..3.0: -6.7)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -9.6 to +6.5 points (1.9..18.75: -9.6; 28.65..32.15: -4.7; 33.95..43.25: -3.4; 54.55..63.75: +2.9; 65.7..73.15: +5.6; 77.95..86.8: +7.5; 99.1..110.5: +7.4)
- **attackers** (enemy players in the pit) rises from -7.2 to +10.1 points (1.0..1.5: -7.2; 1.5..2.5: -4.0; 2.5..3.5: -2.5; 3.5..4.5: -0.8; 4.5..5.5: +7.1; 5.5..6.5: +8.7; 6.5..7.5: +9.8; 7.5..8.0: +10.1)
- **minute** (match minute) falls from +1.8 to -8.7 points (0.5..2.55: +1.8; 3.65..4.65: +7.9; 5.65..6.65: +6.9; 7.75..9.15: +5.1; 10.65..12.25: -7.8; 14.25..16.05: -0.8; 19.35..23.45: -8.6)
- **npc_healing_10s** (healing on own pit NPCs and Lord in the last 10 s) falls from +3.8 to -17.7 points (0.0..3.0: +3.8; 42.5..73.5: +3.8; 104.5..142.5: +2.5; 180.5..222.5: -5.1; 268.5..318.5: -6.3; 379.0..439.5: -7.4; 534.5..688.5: -14.0)
- **strength_gap** (attacking minus defending team strength) rises from -6.0 to +4.7 points (-901.0..-415.5: -6.0; -287.5..-133.0: -11.3; -31.0..53.0: +3.8; 91.5..106.0: -2.4; 191.5..256.0: +3.2; 303.5..386.0: +2.8; 459.0..570.0: -0.8)

**lord damage** (Lord damage dealt in the next 10 s while players are in the enemy pit; 59 matches, 8008 rows): adds to the simple baseline (typical error 125.0 against 85.7 for the median; explains 29% of the spread).
- **defenders** (own players in the pit): 0.0..0.5: +197.3; 0.5..1.5: +111.4; 1.5..2.5: +54.3; 2.5..3.5: -13.3; 3.5..4.5: -66.1; 4.5..5.5: -101.2; 5.5..6.5: -135.6; 6.5..7.5: -148.1; 7.5..8.0: -149.7
- **defenders_elsewhere** (own players alive outside the pit): 0.0..0.5: +67.8; 0.5..1.5: +73.1; 1.5..2.5: +73.7; 2.5..3.5: +69.6; 3.5..4.5: +28.9; 4.5..5.5: -7.2; 5.5..6.5: -48.8; 6.5..7.5: -111.6; 7.5..8.0: -171.0
- **bodyguard** (own Bodyguard alive): 0.0..0.5: +105.3; 0.5..1.0: -41.7
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)): 1.9..18.75: -50.3; 28.8..32.15: -36.0; 32.8..43.25: -29.2; 54.8..64.25: -1.2; 65.7..72.55: +25.6; 76.6..86.35: +44.6; 99.2..110.5: +49.5
- **attackers** (enemy players in the pit): 1.0..1.5: -29.7; 1.5..2.5: -10.6; 2.5..3.5: -15.0; 3.5..4.5: -8.8; 4.5..5.5: +35.6; 5.5..6.5: +35.8; 6.5..7.5: +37.0; 7.5..8.0: +39.8
- **attackers_share** (share of the attacking team's live players in the pit (OG comms: merge before pushing the pit)): 0.12..0.13: -13.3; 0.16..0.23: -17.4; 0.27..0.35: -17.4; 0.42..0.53: -25.4; 0.61..0.65: +6.1; 0.73..0.78: +19.6; 0.87..0.94: +39.8
- **defender_healers** (of which healers): 0.0..0.5: +57.2; 0.5..1.5: -5.9; 1.5..2.5: -3.9; 2.5..3.0: -38.8
- **npc_healing_10s** (healing on own pit NPCs and Lord in the last 10 s): 0.0..3.0: -16.6; 42.5..73.5: +4.2; 106.5..142.5: +20.7; 174.5..218.5: +21.3; 262.5..313.5: +24.2; 373.5..436.5: +27.7; 532.5..685.5: +38.1
- **seconds_in_pit** (seconds the attackers have been in the pit): 0.0..4.5: -20.7; 10.5..16.5: -18.3; 22.5..28.5: -9.1; 37.5..46.5: -2.4; 58.5..73.5: +16.6; 91.5..112.5: +9.1; 142.5..193.5: +25.6
- **attacker_healers** (of which healers): 0.0..0.5: +13.3; 0.5..1.5: -4.0; 1.5..2.5: +13.2; 2.5..3.0: -47.1

**lord kill** (59 matches, 8004 moments, 528 results): no better than the simple baseline yet (AUC 0.936 against 0.934 for attackers and defenders alone).
- **defenders** (own players in the pit) falls from +47.4 to -47.2 points (0.0..0.5: +47.4; 0.5..1.5: +40.2; 1.5..2.5: +17.7; 2.5..3.5: +0.5; 3.5..4.5: -27.2; 4.5..5.5: -36.8; 5.5..6.5: -40.4; 6.5..7.5: -41.5; 7.5..8.0: -47.2)
- **attackers** (enemy players in the pit) rises from -45.0 to +28.0 points (1.0..1.5: -45.0; 1.5..2.5: +11.2; 2.5..3.5: +15.3; 3.5..4.5: +19.3; 4.5..5.5: +32.6; 5.5..6.5: +34.4; 6.5..7.5: +34.0; 7.5..8.0: +28.0)
- **defenders_elsewhere** (own players alive outside the pit) falls from +39.9 to -42.4 points (0.0..0.5: +39.9; 0.5..1.5: +23.3; 1.5..2.5: +23.2; 2.5..3.5: +22.2; 3.5..4.5: +20.7; 4.5..5.5: -21.1; 5.5..6.5: -26.6; 6.5..7.5: -41.7; 7.5..8.0: -42.4)
- **minute** (match minute) rises from -48.9 to +32.1 points (0.5..2.85: -48.9; 4.05..5.15: -11.1; 6.25..7.35: +8.7; 8.85..10.35: +15.8; 11.75..13.85: +17.1; 15.65..18.25: +26.3; 20.45..24.75: +31.6)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -30.0 to +26.3 points (1.9..18.75: -30.0; 28.8..32.15: -30.9; 32.8..43.25: -6.8; 54.8..64.25: -3.2; 65.7..72.55: +11.4; 76.6..86.35: +29.7; 99.2..110.5: +25.8)
- **defender_healers** (of which healers) falls from +25.2 to -31.3 points (0.0..0.5: +25.2; 0.5..1.5: +9.6; 1.5..2.5: -2.3; 2.5..3.0: -31.3)
- **attackers_share** (share of the attacking team's live players in the pit (OG comms: merge before pushing the pit)) rises from -17.9 to +25.0 points (0.12..0.13: -17.9; 0.16..0.23: -13.6; 0.27..0.35: -6.2; 0.42..0.53: -6.9; 0.61..0.65: -1.8; 0.73..0.78: +23.3; 0.87..0.94: +25.4)
- **seconds_in_pit** (seconds the attackers have been in the pit) rises from -5.7 to +34.0 points (0.0..4.5: -5.7; 10.5..16.5: -13.4; 22.5..28.5: -12.4; 37.5..46.5: -10.6; 58.5..73.5: +2.1; 91.5..112.5: +18.1; 142.5..193.5: +26.5)
- **res_in** (seconds until the next res) rises from -42.4 to +0.6 points (1.0..8.5: -42.4; 17.5..26.5: +7.8; 35.5..44.5: +12.3; 53.5..62.5: +11.4; 68.5..74.5: +8.6; 80.5..86.5: +6.5; 95.5..107.5: +1.8)

## 7. The usual play

Each choice against the most common one in that kind of decision, in win-chance points over the decision's window, adjusted for the situation, with a 90% range from resampling whole matches. CLEAR = the range excludes 0. Win chance comes from a model that never saw the match. The same comparison over the 30 s BEFORE the decision is a placebo test: a choice can't cause what came before it, so a clear difference there means the effect is partly who makes that choice.

**after wipe** (128 decisions, 56 matches; usual: pushed the pit)
- took the flag (n 16): -14.2 [-24.8, -5.5] CLEAR; in the 30 s before: +2.6 [-5.6, +10.8]
- reset (n 13): -3.1 [-9.0, +3.8]; in the 30 s before: -6.7 [-17.1, -1.0] ALREADY DIFFERENT BEFORE: partly who chooses it

**boost clock** (242 decisions, 58 matches; usual: not running, fought)
- not running, fell back (n 37): -6.3 [-10.4, -1.5] CLEAR; in the 30 s before: +1.1 [-2.1, +3.7]
- running, fought (n 35): -3.2 [-7.9, +0.9]; in the 30 s before: +3.9 [+0.6, +7.4] ALREADY DIFFERENT BEFORE: partly who chooses it
- not running, advanced (n 30): -7.2 [-11.1, -0.3] CLEAR; in the 30 s before: +8.1 [+4.5, +11.5] ALREADY DIFFERENT BEFORE: partly who chooses it
- running, advanced (n 25): +1.5 [-3.1, +7.6]; in the 30 s before: +2.1 [-3.2, +5.8]
- not running, held (n 14): -4.4 [-11.9, +3.0]; in the 30 s before: +4.8 [-1.7, +10.6]
- not running, to the spawn (n 13): -4.5 [-10.9, +3.6]; in the 30 s before: +1.0 [-2.4, +3.5]
- running, fell back (n 9): +4.8 [-7.3, +17.4]; in the 30 s before: +2.1 [-2.9, +8.9]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - not running, fell back, behind in the fight (lowest third, -0.08 or less): +0.2 (n 11 against 41)
  - not running, fell back, middle third: -5.2 (n 14 against 26)
  - not running, fell back, ahead in the fight (top third, above -0.01): -9.9 (n 12 against 12)
  - running, fought, behind in the fight (lowest third, -0.08 or less): -0.3 (n 10 against 41)
  - running, fought, middle third: -5.3 (n 10 against 26)
  - running, fought, ahead in the fight (top third, above -0.01): +1.5 (n 15 against 12)
  - not running, advanced, behind in the fight (lowest third, -0.08 or less): too few yet (n 4 against 41; means -15.4 against -0.0)
  - not running, advanced, middle third: too few yet (n 9 against 26; means -8.4 against 1.6)
  - not running, advanced, ahead in the fight (top third, above -0.01): -3.8 (n 17 against 12)
  - running, advanced, behind in the fight (lowest third, -0.08 or less): too few yet (n 3 against 41; means -1.4 against -0.0)
  - running, advanced, middle third: too few yet (n 9 against 26; means 4.0 against 1.6)
  - running, advanced, ahead in the fight (top third, above -0.01): +2.9 (n 13 against 12)
  - not running, held, behind in the fight (lowest third, -0.08 or less): too few yet (n 4 against 41; means -5.8 against -0.0)
  - not running, held, middle third: too few yet (n 2 against 26; means -26.4 against 1.6)
  - not running, held, ahead in the fight (top third, above -0.01): too few yet (n 8 against 12; means 5.2 against -2.9)
  - not running, to the spawn, behind in the fight (lowest third, -0.08 or less): too few yet (n 7 against 41; means -1.3 against -0.0)
  - not running, to the spawn, middle third: too few yet (n 4 against 26; means -8.4 against 1.6)
  - not running, to the spawn, ahead in the fight (top third, above -0.01): too few yet (n 2 against 12; means -4.7 against -2.9)
  - running, fell back, behind in the fight (lowest third, -0.08 or less): too few yet (n 1 against 41; means 8.8 against -0.0)
  - running, fell back, middle third: too few yet (n 6 against 26; means -6.0 against 1.6)
  - running, fell back, ahead in the fight (top third, above -0.01): too few yet (n 2 against 12; means 29.5 against -2.9)

**enemy pickup** (925 decisions, 59 matches; usual: held, fought)
- already running, fought (n 137): -5.9 [-9.8, -0.2] CLEAR; in the 30 s before: -0.2 [-2.7, +2.7]
- held, advanced (n 106): -2.4 [-6.5, +4.5]; in the 30 s before: +0.4 [-2.2, +3.2]
- already running, advanced (n 92): -5.0 [-8.5, +1.0]; in the 30 s before: +2.4 [-0.8, +5.4]
- held, fell back (n 77): -6.8 [-13.0, -0.1] CLEAR; in the 30 s before: -0.6 [-3.9, +3.2]
- ran, fell back (n 67): -3.9 [-8.1, +1.0]; in the 30 s before: -3.6 [-6.0, -1.1] ALREADY DIFFERENT BEFORE: partly who chooses it
- already running, fell back (n 61): -3.5 [-9.1, +3.4]; in the 30 s before: -2.5 [-5.6, +0.8]
- ran, fought (n 58): -2.9 [-5.8, +2.8]; in the 30 s before: -4.4 [-6.8, -1.8] ALREADY DIFFERENT BEFORE: partly who chooses it
- ran, advanced (n 51): -4.9 [-8.5, +0.9]; in the 30 s before: +1.9 [-0.5, +4.2]
- already running, held (n 28): -3.1 [-7.1, +3.4]; in the 30 s before: -2.8 [-7.7, +2.7]
- held, held (n 20): +2.8 [-4.0, +16.6]; in the 30 s before: -7.3 [-17.0, -0.7] ALREADY DIFFERENT BEFORE: partly who chooses it
- ran, held (n 15): -0.0 [-5.7, +5.0]; in the 30 s before: -4.6 [-7.9, -1.7] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, to the spawn (n 8): -0.0 [-12.9, +19.0]; in the 30 s before: -10.2 [-29.3, +8.9]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - already running, fought, behind in the fight (lowest third, -0.01 or less): -0.3 (n 48 against 55)
  - already running, fought, middle third: -8.8 (n 34 against 78)
  - already running, fought, ahead in the fight (top third, above +0.01): -4.5 (n 55 against 72)
  - held, advanced, behind in the fight (lowest third, -0.01 or less): -2.7 (n 18 against 55)
  - held, advanced, middle third: -6.8 (n 45 against 78)
  - held, advanced, ahead in the fight (top third, above +0.01): +3.2 (n 43 against 72)
  - already running, advanced, behind in the fight (lowest third, -0.01 or less): +2.9 (n 23 against 55)
  - already running, advanced, middle third: -9.8 (n 35 against 78)
  - already running, advanced, ahead in the fight (top third, above +0.01): -1.8 (n 34 against 72)
  - held, fell back, behind in the fight (lowest third, -0.01 or less): -6.8 (n 36 against 55)
  - held, fell back, middle third: -15.3 (n 18 against 78)
  - held, fell back, ahead in the fight (top third, above +0.01): -0.5 (n 23 against 72)
  - ran, fell back, behind in the fight (lowest third, -0.01 or less): -2.1 (n 35 against 55)
  - ran, fell back, middle third: -9.6 (n 18 against 78)
  - ran, fell back, ahead in the fight (top third, above +0.01): +1.9 (n 14 against 72)
  - already running, fell back, behind in the fight (lowest third, -0.01 or less): -0.1 (n 30 against 55)
  - already running, fell back, middle third: -6.7 (n 20 against 78)
  - already running, fell back, ahead in the fight (top third, above +0.01): +0.8 (n 11 against 72)
  - ran, fought, behind in the fight (lowest third, -0.01 or less): +1.6 (n 25 against 55)
  - ran, fought, middle third: -6.2 (n 14 against 78)
  - ran, fought, ahead in the fight (top third, above +0.01): -2.5 (n 19 against 72)
  - ran, advanced, behind in the fight (lowest third, -0.01 or less): -5.1 (n 12 against 55)
  - ran, advanced, middle third: -4.4 (n 24 against 78)
  - ran, advanced, ahead in the fight (top third, above +0.01): -6.5 (n 15 against 72)
  - already running, held, behind in the fight (lowest third, -0.01 or less): +0.6 (n 11 against 55)
  - already running, held, middle third: -6.7 (n 10 against 78)
  - already running, held, ahead in the fight (top third, above +0.01): too few yet (n 7 against 72; means -3.9 against 0.7)
  - held, held, behind in the fight (lowest third, -0.01 or less): +4.4 (n 10 against 55)
  - held, held, middle third: too few yet (n 8 against 78; means 2.1 against 9.4)
  - held, held, ahead in the fight (top third, above +0.01): too few yet (n 2 against 72; means 17.3 against 0.7)
  - ran, held, behind in the fight (lowest third, -0.01 or less): too few yet (n 6 against 55; means 1.1 against 1.1)
  - ran, held, middle third: too few yet (n 9 against 78; means -0.6 against 9.4)
  - held, to the spawn, behind in the fight (lowest third, -0.01 or less): too few yet (n 7 against 55; means 2.5 against 1.1)
  - held, to the spawn, ahead in the fight (top third, above +0.01): too few yet (n 1 against 72; means 0.4 against 0.7)

- **late_game**: not enough decisions yet (20)
**power play** (539 decisions, 61 matches; usual: pushed, advanced)
- pushed, fought (n 150): +2.6 [+0.3, +5.0] CLEAR; in the 30 s before: -1.8 [-3.8, +0.1]
- held, fought (n 118): -1.3 [-3.6, +0.6]; in the 30 s before: -2.8 [-4.8, -0.5] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, fell back (n 40): -2.1 [-4.9, +0.8]; in the 30 s before: -6.3 [-12.0, -0.3] ALREADY DIFFERENT BEFORE: partly who chooses it
- pushed, fell back (n 25): +3.6 [-1.8, +8.3]; in the 30 s before: -4.5 [-7.7, -0.2] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, advanced (n 16): +3.9 [-1.4, +12.5]; in the 30 s before: -4.6 [-11.2, +1.0]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - pushed, fought, behind in the fight (lowest third, +0.00 or less): +3.2 (n 42 against 65)
  - pushed, fought, middle third: +2.9 (n 50 against 49)
  - pushed, fought, ahead in the fight (top third, above +0.07): -1.1 (n 58 against 76)
  - held, fought, behind in the fight (lowest third, +0.00 or less): +1.7 (n 43 against 65)
  - held, fought, middle third: -2.5 (n 43 against 49)
  - held, fought, ahead in the fight (top third, above +0.07): -5.1 (n 32 against 76)
  - held, fell back, behind in the fight (lowest third, +0.00 or less): +0.6 (n 18 against 65)
  - held, fell back, middle third: -3.2 (n 14 against 49)
  - held, fell back, ahead in the fight (top third, above +0.07): too few yet (n 8 against 76; means -4.7 against 3.0)
  - pushed, fell back, behind in the fight (lowest third, +0.00 or less): -0.2 (n 10 against 65)
  - pushed, fell back, middle third: +4.6 (n 12 against 49)
  - pushed, fell back, ahead in the fight (top third, above +0.07): too few yet (n 3 against 76; means 11.5 against 3.0)
  - held, advanced, behind in the fight (lowest third, +0.00 or less): too few yet (n 7 against 65; means 0.9 against -1.0)
  - held, advanced, middle third: too few yet (n 6 against 49; means 5.3 against -0.3)
  - held, advanced, ahead in the fight (top third, above +0.07): too few yet (n 3 against 76; means 10.8 against 3.0)

**split in base** (148 decisions, 42 matches; usual: defended without a collapse)
- collapsed (n 61): -8.6 [-13.5, -2.6] CLEAR; in the 30 s before: +1.3 [-1.6, +4.5]
- missed (n 12): -6.0 [-16.2, +2.1]; in the 30 s before: -0.9 [-6.5, +6.9]

**Collapses on a split: time away and its cost** (`S32`; per collapse, averages; main = what the main fight lost while the collapsers were away)

| Group | Cases | Away (median s) | Split killed | Collapser died | Own deaths at main | Enemy deaths at main | Flag lead change | DP change | Win change |
|---|---|---|---|---|---|---|---|---|---|
| all | 66 | 18 | 13 | 7 | 0.55 | 0.23 | +2.4 | -2.9 | -3.7 |
| away under 30 s | 42 | 8 | 10 | 1 | 0.02 | 0.1 | +0.8 | +0.2 | -0.7 |
| away 30 to 60 s | 11 | 42 | 0 | 1 | 0.18 | 0.09 | +11.6 | -2.7 | -5.1 |
| away 60 s or more | 13 | 90 | 3 | 5 | 2.54 | 0.77 | -0.4 | -13.2 | -12.5 |
| before 20:00 | 58 | 17.5 | 9 | 5 | 0.33 | 0.21 | +4.2 | -4.3 | -2.4 |
| from 20:00 | 8 | 18 | 4 | 2 | 2.12 | 0.38 | -10.8 | +6.9 | -13.6 |
| split member killed | 13 | 16 | 13 | 1 | 0.08 | 0.77 | +3.6 | +1.4 | -4.7 |
| no kill | 53 | 19 | 0 | 6 | 0.66 | 0.09 | +2.1 | -4.0 | -3.5 |

**Leverage: where the choice matters most** (share of the spread in win-chance change explained by the choice beyond the situation; range = best minus worst choice, in points)

- after wipe (128): choice explains 8.1% (situation 12.5%); range 14.2 points, best pushed the pit, worst took the flag
- boost clock (242): choice explains 5.7% (situation 1.7%); range 11.5 points, best running, fell back, worst not running, advanced
- split in base (148): choice explains 3.4% (situation 12.1%); range 8.6 points, best defended without a collapse, worst collapsed
- power play (539): choice explains 1.6% (situation 1.5%); range 6.3 points, best held, advanced, worst held, fell back
- enemy pickup (925): choice explains 1.5% (situation 3.3%); range 9.8 points, best held, held, worst held, fell back

**Behaviour clusters: what teams actually did** (each decision's response grouped by what every player did in the next 20 s; UNNAMED = a group no single named choice covers: a response for Denning to name or reject)

*after wipe* (2 groups, separation 0.31):
- n 78: fought (midline, 1.9 of 8), fought (backline, 1.5 of 8), held (backline, 0.9 of 8), fought (frontline, 0.9 of 8); named as {'pushed the pit': 70, 'reset': 4, 'took the flag': 4}; win change -0.5
- n 50: advanced (backline, 2.9 of 8), advanced (midline, 2.0 of 8), advanced (frontline, 1.3 of 8); named as {'pushed the pit': 29, 'took the flag': 12, 'reset': 9}; win change -2.8 UNNAMED
*boost clock* (4 groups, separation 0.18):
- n 92: fought (midline, 2.2 of 8), fought (backline, 1.8 of 8), fought (frontline, 1.0 of 8); named as {'not running, fought': 60, 'running, fought': 27, 'running, advanced': 2}; win change -1.2
- n 64: held (backline, 1.6 of 8), fought (midline, 0.9 of 8), held (midline, 0.8 of 8), fought (frontline, 0.6 of 8); named as {'not running, fought': 17, 'not running, held': 14, 'not running, to the spawn': 10}; win change -0.8 UNNAMED
- n 58: advanced (midline, 2.2 of 8), advanced (backline, 1.8 of 8), fought (midline, 0.6 of 8), advanced (frontline, 0.5 of 8); named as {'not running, advanced': 29, 'running, advanced': 20, 'running, fought': 2}; win change -4.1 UNNAMED
- n 37: fell back (midline, 2.8 of 8), fell back (backline, 1.9 of 8), fell back (frontline, 0.8 of 8); named as {'not running, fell back': 30, 'running, fell back': 7}; win change -3.2
*enemy pickup* (3 groups, separation 0.2):
- n 370: fought (midline, 2.1 of 8), fought (backline, 1.4 of 8), fought (frontline, 1.1 of 8), held (backline, 0.9 of 8); named as {'held, fought': 160, 'already running, fought': 124, 'ran, fought': 46}; win change -0.2 UNNAMED
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
| death: down 20 to 60 s | 447 | -6.2 | -9.8 to -2.5 | -2.5 | yes |
| death: down 60 s or more | 567 | -5.0 | -7.8 to -2.3 | -5.6 | yes |
| death: healer | 411 | -4.4 | -6.9 to -2.0 | -4.4 | yes |
| death: healer in own base or pit, back within 15 s (likely deliberate) | 26 | +2.1 | -2.1 to +8.9 | +2.9 | no |
| death: healer, other | 385 | -4.8 | -7.4 to -2.5 | -4.9 | yes |
| death: not a healer | 793 | -5.2 | -8.2 to -2.2 | -3.2 | yes |
| death: team boosted (morale above zero) | 171 | -22.3 | -36.1 to -9.7 | -7.0 | yes |
| death: team not boosted | 1033 | -2.1 | -5.9 to +2.1 | -3.0 | no |
| footman lost (base NPC) | 188 | +2.7 | -2.1 to +7.4 | +1.5 | no |
| pit NPC lost (any): taken by a spike build | 88 | -4.9 | -9.3 to +1.0 | -1.5 | no |
| pit NPC lost (any): taken by other builds | 417 | -1.9 | -4.8 to +1.0 | -1.3 | no |
| pit NPC lost: archer | 291 | -0.1 | -2.5 to +2.8 | +0.6 | no |
| pit NPC lost: bodyguard | 71 | -2.1 | -6.0 to +0.8 | -0.1 | no |
| pit NPC lost: knight | 143 | -7.4 | -11.4 to -3.8 | -5.9 | yes |

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

- damage in the 2 s burst 518.5 to 839: result chance +31.7 points, worth +1.55 win points
- target's health ceiling 0.4 to 0.56: result chance +34.3 points, worth +1.68 win points
- target health % when the burst started 0 to 38.5: result chance +25.9 points, worth +1.27 win points
- target's healers in range 0 to 0.5: result chance +32.2 points, worth +1.58 win points
- attacking minus target team strength 459 to 901: result chance +23.0 points, worth +1.13 win points
- target team's prot skills 5.5 to 6.5: result chance +19.9 points, worth +0.98 win points
- a prot on the target 0.5 to 1: result chance -7.7 points, worth -0.38 win points
- match minute 0.3 to 1.45: result chance -14.8 points, worth -0.73 win points

*npc loss* (per case, for the defending team; result worth -2.4 points, base rate 18.5%):

- own players in the pit 7.5 to 8: result chance -15.5 points, worth +0.38 win points
- damage on the pit NPCs in the last 5 s 367 to 1170: result chance +36.4 points, worth -0.89 win points
- own players alive outside the pit 0 to 0.5: result chance +17.6 points, worth -0.43 win points
- share of the attacking team's live players in the pit (OG comms: merge before pushing the pit) 0.87 to 0.94: result chance +7.8 points, worth -0.19 win points
- of which healers 0 to 0.5: result chance +15.9 points, worth -0.39 win points
- attackers' measured damage per second against a Lord (benchmarks) 18.75 to 28.65: result chance -6.8 points, worth +0.17 win points
- enemy players in the pit 7.5 to 8: result chance +7.0 points, worth -0.17 win points
- match minute 23.45 to 28: result chance -4.7 points, worth +0.12 win points

## The TQs

Denning's four questions, each from the batch's matches. The why comes from forensics and events (every number placed against the same role or situation in every stored match); the different play comes only from measurement: the usual play's choice effects (usual.py), node models read again with the variable changed (models that never saw the match, changes priced in win points with values.py), options that were ready and unused, and benchmarks. Points = win-chance points.

## TQ 1. Behind on flags

*The biggest flag swing in the new matches: ohno +79 -> -73 by 2:50.0.*

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
**Why, in short**: xxx capped at 2:50, 125 s after ohno's capture, on its 4th run (3 dropped); ohno pushed the last carrier with Mesmer, AoB Derv but its health never went below 77%.

**A different play (measured)**

*The decisions in the swing* (usual.py: win-chance points over the decision's window, against the kind's most common choice):
- split in base at 1:15 (main 5v4, flags +37 s, boost in 90, fight state -0.019): chose **defended without a collapse** (+0.0 [+0.0, +0.0] against the most common choice, defended without a collapse); in the 15 most similar decisions teams usually chose **defended without a collapse**; no choice of this kind did measurably better than the one made.
- enemy pickup at 2:03 (main 4v4, flags +15 s, boost in 43, fight state -0.002): chose **held, fought** (+0.0 [+0.0, +0.0] against the most common choice, held, fought); in the 15 most similar decisions teams usually chose **already running, fought**; measured better: **held, held** (+2.8 points against the choice made, not clear yet, partly who chooses it, n 20).
*The answers to the enemy's captures* (flag-answer node: seconds slower than possible; typical error 17.1 s against 27.4 s for the median on unseen matches):
- answer at 2:50 by the AoB Derv: 16 s slower than possible (model reads 8.4 s); with a runner waiting at the spawn: -2.8 s (-11.2 s); no enemies on the way back: -17.7 s (-26.1 s)
- Those 26 s, read by the win model as flag lead at 2:50: ohno 96.1% -> 87.7% (-8.4 points) (the win model's flag-lead curve still bends the wrong way at the extremes, a known issue, so it can't price these seconds here yet)

**Confidence**: medium (one measurement supports it).

## TQ 2. A monk death

*The monk death that cost the most win chance in the new matches: ohno v Fun (1cb73c20), Fun 7 Monk at 25:33 (enemy pit, numbers [7, 5]); win chance -46.3 points from 10 s before to 30 s after.*

**Why** (forensics, against the same role in every stored match):
- Position: yes (nearest allied healer 11692 in the last 5 s, nearest enemy 106, allies in casting range 6, enemies 3)
- Prots: no prots (0 from teammates, 0 self; 0 of 0 landed); damage 528 (73% attacks, 23% armor-ignoring), burst 143 in 2 s at 25:24.9; knockdowns 1, knockdown immunity up for 0
- Healers under interrupt pressure: yes (healers 2, interrupts_per_min 9.0, interrupted 3, casts 18, finished_share 0.83, dazed 0, knockdowns 1, hexes 2)
- Damage off shield sets: usual (team share 0.43, a shield would have stopped about 114)
- Own damage: usual (29.9 per second on [('ohno Dervish 2', 559), ('ohno 7 Monk', 38)]); enemy damage: usual (55.7 per second)
- Peel: no (peel on a burst is rare: most bursts on this role get none) (0 of 2 attackers controlled; longest free 20.0 s)
- Casting: interrupted far more than usual (casts 9, interrupted 3, cancelled 0, while_dazed 0)
**Why, in short**: the 7 Monk died because no prot landed in time (0 of 0 landed), knocked down 1 times with no knockdown immunity up, its casts were interrupted (3 of 9), its healers were under interrupt pressure.

**How it could have been prevented (measured)**

- Knockdowns with knockdown immunity ready and in range: 25:31.4 Psychic Instability PvP by ohno Mesmer (Fun 7 Monk Balanced Stance ready)
- Attackers left free (no snare, Blind, Weakness, interrupt, knockdown or hex from its team): ohno Dervish 1 20.0 s free (nearest own non-healer 412); ohno Mesmer 20.0 s free (nearest own non-healer 175)
- Deaths node at 25:30 (AUC 0.916 on unseen matches against 0.799 for health_pct and damage_taken_3s alone): risk 12.5% of dying in the next 10 s; read again with
  - another healer in range: 7.4% (-5.1 points of risk; at this death's measured cost of -46.3 win points, about +2.4 expected; at a typical healer death's -4.4, +0.2)
  - one attacker peeled off: 10.8% (-1.7 points of risk; at this death's measured cost of -46.3 win points, about +0.8 expected; at a typical healer death's -4.4, +0.1)
  - all of these together: 6.3% (-6.2 points of risk; at this death's measured cost of -46.3 win points, about +2.9 expected; at a typical healer death's -4.4, +0.3)

**Confidence**: medium (one measurement supports it).

## TQ 3. A power play without a kill

*The biggest in the new matches: main 7v4, pushed, no kill in 58 s.*

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
**Why, in short**: ohno had 7v4 at main for 58 s but dealt 17.9 damage per second (below the 20th percentile for team (median 37.1, n 3825)); damage uptime 20% (most damage-seconds lost to moving); spread over 4 targets (top share 0.35); xxx healed 56 per second.

**How it could have been converted (measured)**

- Against every stored power play (3+ more at main): those that killed had a median 36.6 damage per second and top-target share 0.4 (29 cases); those that didn't, 22.3 and 0.54 (31 cases). ohno here: 17.9 and 0.35. Damage uptime: 40% in those that killed, 33% in those that didn't, 20% here.
- No burst (a 2 s burst that the kill-conversion node reads) in the window: the damage never came together on one target.
- The choice at the power play (usual.py):
  - power play at 25:07 (main 7v4, flags -29 s, boost in 58, fight state -0.003): chose **pushed, advanced** (+0.0 [+0.0, +0.0] against the most common choice, pushed, advanced); in the 15 most similar decisions teams usually chose **held, fought**; measured better: **pushed, fought** (+2.6 points against the choice made, clear, n 150); **held, advanced** (+3.9 points against the choice made, not clear yet, n 16).

**Confidence**: medium (one measurement supports it).

## TQ 4. Pit NPCs lost

*The NPC loss that cost the most win chance in the new matches: One lost knight (ohno split Hammer+8 Monk+Ranger) at 2:42; win chance -7.2 points from 20 s before to 20 s after.*

### Pit NPCs lost: One v ohno (c553716d) around 2:42.0
**Lost**: 2:42.0 knight (ohno split Hammer+8 Monk+Ranger)
**ohno's split** 1:53.0 to 3:00.0: ['Hammer', '8 Monk', 'Ranger'] (split), entered base 2:18.0, NPC damage {'footman': 23, 'archer': 115, 'knight': 362}, NPC kills [{'npc': 'knight', 't': 162, 'defenders_present': ['Warrior', 'Paragon 1', 'Mesmer', 'Prot', '8 Monk']}]
- defender Warrior: first 1:58.0 (latency -20 s, collapse from main), 8 s defending
- defender Paragon 1: first 2:00.0 (latency -18 s, collapse from main), 12 s defending
- defender Mesmer: first 2:00.0 (latency -18 s, collapse from main), 6 s defending
- defender Prot: first 2:08.0 (latency -10 s, already in base), 16 s defending
- defender 8 Monk: first 2:23.0 (latency 5 s, already in base), 26 s defending
- main numbers meanwhile [3.8, 5.4]
**One at 2:42.0**: Warrior: stand (convert); Paragon 1: stand (convert); Paragon 2: stand (convert); Monk 4 (WoC): stand (convert); Mesmer: stand (convert); Prot: stand (convert); 7 Monk: stand (convert); 8 Monk: own pit (defend)
- ohno output 1:53.0 to 2:47.0: 7.1 per second
- One output 1:53.0 to 2:47.0: 9.9 per second
**Why, in short**: ohno split Hammer+8 Monk+Ranger into One's base at 2:18; at 2:38 the pit had 3 attackers against 2 defenders (2 of them healers), with 6 of One elsewhere; defenders present at the kill: Warrior, Paragon 1, Mesmer, Prot, 8 Monk.

**How it could have been prevented (measured)**

- First defender: 20 s before it entered the base; every stored split into a base: median 8 s before it entered the base, quickest fifth 34 s before it entered the base or sooner (192 splits). Denning: about 15 s is on time, 60 s is late.
- The split was answered on time, so the loss came from what the defence did once there (below), not from a late answer.
- NPC-loss node at 2:38 (AUC 0.808 on unseen matches against 0.748 for attackers and defenders alone): 3 attackers (1 healer) against 2 defenders (2 healers), 6 of One elsewhere; read 78.2% to lose an NPC; read again with
  - one more defender: 66.3% (-11.9 points; at this loss's measured cost of -7.2 win points, about +0.9 expected; at a typical NPC loss's -2.4, +0.3)
  - one more defender, a healer: 69.7% (-8.5 points; at this loss's measured cost of -7.2 win points, about +0.6 expected; at a typical NPC loss's -2.4, +0.2)
  - two more defenders: 61.6% (-16.6 points; at this loss's measured cost of -7.2 win points, about +1.2 expected; at a typical NPC loss's -2.4, +0.4)
  - healing on the NPCs (as much as the attackers' damage in 5 s): 74.4% (-3.8 points; at this loss's measured cost of -7.2 win points, about +0.3 expected; at a typical NPC loss's -2.4, +0.1)
- The answer to the split (usual.py; this prices the whole decision, including what the main fight lost while defenders were away, which the NPC-loss node above does not):
  - split in base at 2:18 (main 6v4, flags +33 s, boost in 109, fight state -0.002): chose **collapsed** (-8.6 [-13.5, -2.6] CLEAR against the most common choice, defended without a collapse); in the 15 most similar decisions teams usually chose **collapsed**; measured better: **defended without a collapse** (+8.6 points against the choice made, clear, n 75); **missed** (+2.6 points against the choice made, not clear yet, n 12).

**Confidence**: medium to high (two independent measurements agree).

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

