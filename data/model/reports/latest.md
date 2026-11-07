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
- glass box: all 77% (0.549), 0-5 min 84% (0.377), 5-10 min 78% (0.51), 10-15 min 71% (0.716), 15-end min 71% (0.711), matches lasting 15 min+ 70% (0.687), matches even on strength (gap under 200) 59% (0.972)
- glass box without corrections: all 78% (0.552), 0-5 min 84% (0.375), 5-10 min 79% (0.499), 10-15 min 74% (0.688), 15-end min 70% (0.76), matches lasting 15 min+ 71% (0.692), matches even on strength (gap under 200) 59% (0.964)
- black box: all 72% (1.085), 0-5 min 77% (0.858), 5-10 min 74% (0.989), 10-15 min 67% (1.248), 15-end min 64% (1.397), matches lasting 15 min+ 65% (1.375), matches even on strength (gap under 200) 55% (1.74)
- Gain over strength alone (log loss, resampling whole matches): -0.131 (90% range -0.307 to -0.0).
- Change since batch 5: glass box log loss 0.53 -> 0.549; strength only 0.439 -> 0.418.

## 2. What it leans on

- **lord_dps_enemy** 0.696 (new): enemy build's measured Lord damage per second
- **lord_dps_own** 0.687 (new): own build's measured Lord damage per second if all its non-healers were at the Lord
- **knights_diff & map_flag_run** 0.458 (new): own minus enemy pit knights alive TOGETHER WITH the map's flag run Y: distance from the flag spawn to the stand (average of both sides)
- **spike_killable_diff** 0.452 (was 0.302): enemy minus own players within one spike of the other side (DP stacking; 0 unless a spike build is involved)
- **morale_diff & map_pit_to_stand** 0.393 (new): own minus enemy morale summed over players (boosts +, death penalty -) TOGETHER WITH the map's distance from a pit to the stand (average of both sides)
- **morale_diff & map_flag_run** 0.354 (new): own minus enemy morale summed over players (boosts +, death penalty -) TOGETHER WITH the map's flag run Y: distance from the flag spawn to the stand (average of both sides)
- **morale_diff** 0.351 (was 0.563): own minus enemy morale summed over players (boosts +, death penalty -)
- **knights_diff** 0.343 (was 0.242): own minus enemy pit knights alive
- **spike_build_enemy** 0.273 (new): enemy build is a spike build
- **archers_diff & map_flag_run** 0.27 (new): own minus enemy pit archers alive TOGETHER WITH the map's flag run Y: distance from the flag spawn to the stand (average of both sides)
- **spike_build_own** 0.269 (new): own build is a spike build (1) or not (0)
- **fight_state** 0.214 (was 0.047): who is winning the fight now: enemy minus own expected deaths in the next 10 s, from a deaths model that never saw the match (fightstate.py)

## 3. The curves in words

Points = win-chance points added to an otherwise even game at each range of the variable.

- **lord_dps_enemy** rises from +9.2 to +22.3 points (35.8..65.45: +9.2; 78.4..83.15: +8.2; 83.7..88.5: -11.5; 91.2..98.6: +4.5; 102.6..105.45: -18.1; 106.0..111.8: +4.5; 117.1..135.25: +22.4)
- **lord_dps_own** falls from -9.2 to -21.6 points (35.8..65.45: -9.2; 78.4..83.15: -8.6; 83.7..88.5: +11.0; 91.2..98.6: -4.7; 102.6..105.45: +17.8; 106.0..111.8: -4.5; 117.1..135.25: -21.6)
- **knights_diff & map_flag_run** (interaction): see wp_model.md
- **spike_killable_diff** rises from -47.1 to +47.3 points (-8.0..-7.5: -47.1; -6.5..-4.5: -46.4; -2.5..-1.5: -45.5; -0.5..0.5: -0.2; 1.5..2.5: +46.4; 4.5..7.5: +47.0)
- **morale_diff & map_pit_to_stand** (interaction): see wp_model.md
- **morale_diff & map_flag_run** (interaction): see wp_model.md
- **morale_diff** rises from -15.8 to +19.3 points (-470.0..-186.5: -15.8; -141.0..-109.5: -12.7; -83.5..-46.5: -9.7; -15.5..-0.5: -2.1; 0.5..19.5: +1.4; 52.5..91.5: +9.4; 124.5..169.5: +13.0)
- **knights_diff** rises from -18.5 to +18.7 points (-2.0..-1.5: -18.5; -1.5..-0.5: -15.9; -0.5..0.5: +0.0; 0.5..1.5: +15.6; 1.5..2.0: +18.7)
- **spike_build_enemy** falls from +4.0 to -20.3 points (0.0..0.5: +4.0; 0.5..1.0: -20.3)
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

- split_diff: 0.549 without, 0.55 with: does not improve yet. own minus enemy players on a split (away from their main group on the enemy half, not carrying). Proposed batch 1 by Claude: the knights curve runs backwards, maybe standing in for the cost of splitting
- turtle_diff: 0.549 without, 0.57 with: does not improve yet. own minus enemy share of live players at home (own base or pit). Proposed 2026-11-06 from OG comms ([ohno v One], [ohno v Crew]: 'they are turtling, we have to make a play'); comms_vars.py: teams that turtled 60 s won 3 of 13 times

**Surprises** (moments where the held-out model was most confident about the team that went on to lose; each points to something the variables don't capture yet):

- OG v hold (49eec28d) at 4:15: a model that never saw this match gave OG 0.0%, and OG won. Why it thought so: lord_damage_diff & lord_dps_own -32.7, lord_dps_enemy -27.9, archers_diff & map_flag_run -27.6, morale_diff & map_flag_run -25.0, knights_diff & map_flag_run -20.0
- RACK v hdm (1f65fd3b) at 15:15: a model that never saw this match gave RACK 1.3%, and RACK won. Why it thought so: knights_diff -33.0, healing_monks_enemy -22.5, lord_damage_diff & lord_dps_own +19.3, morale_diff -16.8, team strength -14.0
- 옷옷옷옷 v Men (36a65ac6) at 17:30: a model that never saw this match gave 옷옷옷옷 12.6%, and 옷옷옷옷 won. Why it thought so: lord_dps_enemy -33.0, morale_diff -22.6, team strength +17.5, archers_diff & map_pit_to_stand -12.9, morale_diff & map_flag_run +12.2
- hdm v HC (28447c4a) at 24:00: a model that never saw this match gave HC 0.2%, and HC won. Why it thought so: morale_diff & map_bases_apart -32.5, knights_diff -29.6, morale_diff -23.4, morale_diff & lord_dps_enemy -22.3, morale_diff & map_flag_run -19.6
- Team v cope (6c7dfcaa) at 7:30: a model that never saw this match gave Team 11.5%, and Team won. Why it thought so: morale_diff -16.3, team strength -11.0, fight_state -8.1, healing_monks_own +7.0, stand -6.2
- BcS v yM (b88983e3) at 11:15: a model that never saw this match gave yM 8.9%, and yM won. Why it thought so: morale_diff & lord_dps_own -36.9, morale_diff -28.5, team strength +19.5, lord_dps_own +16.8, lord_dps_enemy +12.6

## 5. Denning's rulings seen through the model

Win chance from a model that never saw the match, 20 s before and 60 s after each ruled moment. Contributions are points for an otherwise even game (the curves' scale).

- hdm v HC (28447c4a) 5:01 (split answered), HC: 10.3% 20 s before -> 70.6% 60 s after (+60.3). After: knights_diff -29.6, morale_diff & map_bases_apart +28.7, team strength -16.4, archers_diff & map_bases_apart +13.4
- hdm v HC (28447c4a) 5:01 (split answered), hdm: 88.4% 20 s before -> 32.6% 60 s after (-55.8). After: knights_diff +30.4, morale_diff & map_bases_apart -29.1, team strength +16.4, archers_diff & map_bases_apart -13.3
- hdm v HC (28447c4a) 1:02 (split detection), HC: 25.6% 20 s before -> 28.7% 60 s after (+3.1). After: morale_diff & map_bases_apart +26.8, team strength -16.4, morale_diff & lord_dps_enemy -13.2, lord_dps_enemy +12.4
- hdm v HC (28447c4a) 1:02 (split detection), hdm: 64.4% 20 s before -> 71.0% 60 s after (+6.6). After: morale_diff & map_bases_apart -28.8, team strength +16.4, flag_lead & map_flag_run +12.8, lord_dps_own -11.9
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), HC: 42.1% 20 s before -> 19.8% 60 s after (-22.3). After: knights_diff -29.6, morale_diff & map_bases_apart +28.7, archers_diff -23.3, team strength -16.4
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), hdm: 71.2% 20 s before -> 85.6% 60 s after (+14.4). After: knights_diff +30.4, morale_diff & map_bases_apart -29.1, archers_diff +24.0, team strength +16.4
- hdm v HC (bbef1904) 8:10 (death), HC: 52.5% 20 s before -> 8.4% 60 s after (-44.1). After: team strength -16.0, lord_dps_own -14.6, down_diff_s -12.8, morale_diff -12.8
- hdm v HC (bbef1904) 8:10 (death), hdm: 42.6% 20 s before -> 90.0% 60 s after (+47.4). After: team strength +16.0, lord_dps_enemy +14.0, morale_diff +12.9, alive_diff +11.1
- Men v HC (faec428a) 9:31 (death), HC: 3.8% 20 s before -> 3.7% 60 s after (-0.1). After: lord_dps_own -21.2, knights_diff -18.0, archers_diff & map_flag_run +17.0, team strength -14.9
- Men v HC (faec428a) 9:31 (death), Men: 96.0% 20 s before -> 95.8% 60 s after (-0.2). After: lord_dps_enemy +21.8, knights_diff +18.4, archers_diff & map_flag_run -17.1, team strength +14.9

## 6. Why: the node models

Each explains one result from what happened before it (time order enforced), tested on matches it never saw. AUC = how often a moment that led to the result scores above one that didn't (0.5 = guessing, 1 = perfect).

**deaths** (61 matches, 134313 moments, 3716 results): adds to the simple baseline (AUC 0.916 against 0.799 for health_pct and damage_taken_3s alone).
- **enemies_near** (enemies within 1,500) rises from -22.1 to +24.8 points (0.0..0.5: -22.1; 0.5..1.5: -9.9; 1.5..2.5: +1.3; 2.5..3.5: +2.8; 3.5..4.5: +11.7; 4.5..5.5: +13.6; 5.5..6.5: +15.0; 6.5..7.5: +17.5; 7.5..8.0: +24.8)
- **health_pct** (current health %) falls from +40.9 to -6.4 points (1.0..47.5: +40.9; 59.5..67.5: +24.4; 73.5..78.5: +10.7; 82.5..85.5: +6.4; 88.5..91.5: +1.4; 93.5..95.5: -1.5; 97.5..99.5: -4.3)
- **strength_gap** (own minus enemy team strength) falls from +16.5 to -10.7 points (-901.0..-523.0: +16.5; -360.5..-274.5: +10.4; -122.5..-102.0: +3.9; -45.0..0.0: +1.0; 60.5..104.5: -8.0; 122.5..274.5: -9.5; 360.5..523.0: -10.8)
- **local_diff** (allies minus enemies within 2,000) falls from +23.4 to -10.2 points (-8.0..-3.5: +23.4; -2.5..-1.5: +12.0; -0.5..0.5: -4.3; 1.5..2.5: -8.5; 3.5..4.5: +8.6; 5.5..7.0: -10.2)
- **healers_in_range** (own healers alive within cast range) falls from +12.5 to -10.2 points (0.0..0.5: +12.5; 0.5..1.5: -3.6; 1.5..2.5: -5.6; 2.5..3.5: -2.7; 3.5..4.0: -10.2)
- **allies_near** (allies within 1,500) falls from +14.6 to -8.6 points (0.0..0.5: +14.6; 0.5..1.5: +8.7; 1.5..2.5: +6.6; 2.5..3.5: -0.5; 3.5..4.5: -1.9; 4.5..5.5: -3.3; 5.5..6.5: -5.5; 6.5..7.0: -8.6)
- **health_ceiling** (maximum health after death penalty, as a share of normal) falls from +24.9 to -7.0 points (0.4..0.69: +24.9; 0.72..0.84: +17.7; 0.85..0.89: +12.7; 0.94..0.95: +6.9; 0.99..1.0: -0.8; 1.1..1.1: -7.0)
- **minute** (match minute) rises from -5.6 to +18.7 points (0.1..1.25: -5.6; 2.25..3.35: -10.7; 4.45..5.45: -3.2; 6.65..8.05: +0.4; 9.55..11.15: +0.4; 13.05..15.15: +1.0; 17.75..20.95: +6.3)
- **enemy_strips** (enemy enchantment removal skills) falls from +7.2 to -44.7 points (0.0..0.5: +7.2; 0.5..1.5: +5.8; 1.5..2.5: +4.0; 2.5..3.5: -3.3; 3.5..4.5: -4.3; 4.5..5.5: -4.9; 5.5..6.0: -44.7)

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
- **defenders** (own players in the pit) falls from +33.9 to -37.4 points (0.0..0.5: +33.9; 0.5..1.5: +22.6; 1.5..2.5: +14.4; 2.5..3.5: +1.7; 3.5..4.5: -12.1; 4.5..5.5: -13.1; 5.5..6.5: -14.0; 6.5..7.5: -27.8; 7.5..8.0: -37.4)
- **npc_damage_5s** (damage on the pit NPCs in the last 5 s) rises from -16.5 to +34.4 points (0.0..0.5: -16.5; 22.5..36.5: -1.9; 50.5..69.5: +5.7; 88.5..109.5: +13.0; 131.5..157.5: +23.4; 188.5..227.5: +26.3; 278.5..367.0: +30.7)
- **defenders_elsewhere** (own players alive outside the pit) falls from +20.5 to -5.5 points (0.0..0.5: +20.5; 0.5..1.5: +12.8; 1.5..2.5: +12.6; 2.5..3.5: +5.6; 3.5..4.5: -4.7; 4.5..5.5: -14.5; 5.5..6.5: -16.1; 6.5..7.5: -14.9; 7.5..8.0: -5.5)
- **attackers** (enemy players in the pit) rises from -15.3 to +18.6 points (1.0..1.5: -15.3; 1.5..2.5: -8.5; 2.5..3.5: -4.0; 3.5..4.5: +1.7; 4.5..5.5: +14.8; 5.5..6.5: +17.0; 6.5..7.5: +18.0; 7.5..8.0: +18.6)
- **defender_healers** (of which healers) falls from +19.6 to -6.5 points (0.0..0.5: +19.6; 0.5..1.5: -1.8; 1.5..2.5: -4.7; 2.5..3.0: -6.5)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -10.3 to +6.6 points (1.9..18.75: -10.3; 28.65..32.15: -5.2; 33.95..43.25: -3.3; 54.55..63.75: +3.1; 65.7..73.15: +6.0; 77.95..86.8: +7.9; 99.1..110.5: +7.6)
- **npc_healing_10s** (healing on own pit NPCs and Lord in the last 10 s) falls from +3.9 to -18.0 points (0.0..3.0: +3.9; 42.5..73.5: +3.7; 104.5..142.5: +2.1; 180.5..222.5: -4.9; 268.5..318.5: -6.3; 379.0..439.5: -7.8; 534.5..688.5: -14.1)
- **minute** (match minute) falls from +2.0 to -8.1 points (0.5..2.55: +2.0; 3.65..4.65: +7.3; 5.65..6.65: +6.1; 7.75..9.15: +5.0; 10.65..12.25: -7.4; 14.25..16.05: -1.1; 19.35..23.45: -7.7)
- **strength_gap** (attacking minus defending team strength) rises from -4.4 to +4.5 points (-901.0..-415.5: -4.4; -287.5..-133.0: -10.9; -31.0..53.0: +3.3; 91.5..106.0: -1.9; 191.5..256.0: +3.1; 303.5..386.0: +2.5; 459.0..570.0: -0.8)

**lord damage** (Lord damage dealt in the next 10 s while players are in the enemy pit; 59 matches, 8008 rows): adds to the simple baseline (typical error 124.8 against 85.7 for the median; explains 29% of the spread).
- **defenders** (own players in the pit): 0.0..0.5: +199.5; 0.5..1.5: +110.5; 1.5..2.5: +54.0; 2.5..3.5: -13.5; 3.5..4.5: -63.3; 4.5..5.5: -103.2; 5.5..6.5: -136.9; 6.5..7.5: -148.3; 7.5..8.0: -150.7
- **defenders_elsewhere** (own players alive outside the pit): 0.0..0.5: +70.7; 0.5..1.5: +73.1; 1.5..2.5: +72.9; 2.5..3.5: +68.7; 3.5..4.5: +25.6; 4.5..5.5: -7.9; 5.5..6.5: -51.0; 6.5..7.5: -109.0; 7.5..8.0: -170.8
- **bodyguard** (own Bodyguard alive): 0.0..0.5: +106.2; 0.5..1.0: -42.1
- **attackers** (enemy players in the pit): 1.0..1.5: -44.6; 1.5..2.5: -20.5; 2.5..3.5: -27.8; 3.5..4.5: -15.6; 4.5..5.5: +42.3; 5.5..6.5: +55.3; 6.5..7.5: +68.6; 7.5..8.0: +73.8
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)): 1.9..18.75: -54.9; 28.8..32.15: -41.8; 32.8..43.25: -32.5; 54.8..64.25: -6.9; 65.7..72.55: +23.2; 76.6..86.35: +49.4; 99.2..110.5: +63.5
- **defender_healers** (of which healers): 0.0..0.5: +58.2; 0.5..1.5: -5.4; 1.5..2.5: -5.2; 2.5..3.0: -38.5
- **npc_healing_10s** (healing on own pit NPCs and Lord in the last 10 s): 0.0..3.0: -16.9; 42.5..73.5: +3.3; 106.5..142.5: +19.5; 174.5..218.5: +19.8; 262.5..313.5: +24.6; 373.5..436.5: +28.6; 532.5..685.5: +40.7
- **seconds_in_pit** (seconds the attackers have been in the pit): 0.0..4.5: -20.3; 10.5..16.5: -19.5; 22.5..28.5: -10.4; 37.5..46.5: -2.7; 58.5..73.5: +15.8; 91.5..112.5: +9.1; 142.5..193.5: +28.1
- **attacker_healers** (of which healers): 0.0..0.5: +13.5; 0.5..1.5: -8.7; 1.5..2.5: +16.0; 2.5..3.0: -41.9
- **npc_damage_5s** (damage on the pit NPCs in the last 5 s): 0.0..0.5: +11.3; 22.5..36.5: -3.9; 50.5..69.5: -11.4; 88.5..109.5: -16.8; 131.5..157.5: -22.7; 189.5..228.5: -25.8; 281.5..372.0: -19.2

**lord kill** (59 matches, 8004 moments, 528 results): no better than the simple baseline yet (AUC 0.948 against 0.934 for attackers and defenders alone).
- **defenders** (own players in the pit) falls from +47.4 to -48.0 points (0.0..0.5: +47.4; 0.5..1.5: +41.6; 1.5..2.5: +17.8; 2.5..3.5: -2.2; 3.5..4.5: -23.8; 4.5..5.5: -36.1; 5.5..6.5: -41.4; 6.5..7.5: -42.7; 7.5..8.0: -48.0)
- **attackers** (enemy players in the pit) rises from -46.8 to +37.8 points (1.0..1.5: -46.8; 1.5..2.5: +3.7; 2.5..3.5: +12.7; 3.5..4.5: +16.6; 4.5..5.5: +33.4; 5.5..6.5: +42.2; 6.5..7.5: +42.3; 7.5..8.0: +37.8)
- **defenders_elsewhere** (own players alive outside the pit) falls from +40.5 to -42.5 points (0.0..0.5: +40.5; 0.5..1.5: +20.2; 1.5..2.5: +19.7; 2.5..3.5: +18.3; 3.5..4.5: +16.7; 4.5..5.5: -18.0; 5.5..6.5: -21.8; 6.5..7.5: -41.6; 7.5..8.0: -42.5)
- **minute** (match minute) rises from -46.2 to +28.0 points (0.5..2.85: -46.2; 4.05..5.15: -11.7; 6.25..7.35: +4.1; 8.85..10.35: +7.8; 11.75..13.85: +10.7; 15.65..18.25: +24.2; 20.45..24.75: +27.6)
- **attackers_area_damage** (area-damage skills on the attackers' bars (Denning P9)) rises from -17.2 to +18.5 points (0.0..0.5: -17.2; 0.5..1.5: +14.8; 1.5..2.5: +16.7; 2.5..3.5: +13.2; 3.5..5.0: +17.1; 5.0..6.0: +18.5)
- **defender_healers** (of which healers) falls from +25.2 to -31.2 points (0.0..0.5: +25.2; 0.5..1.5: +9.6; 1.5..2.5: -2.5; 2.5..3.0: -31.2)
- **seconds_in_pit** (seconds the attackers have been in the pit) rises from -9.7 to +34.8 points (0.0..4.5: -9.7; 10.5..16.5: -15.0; 22.5..28.5: -13.3; 37.5..46.5: -10.4; 58.5..73.5: +6.2; 91.5..112.5: +18.5; 142.5..193.5: +29.3)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -17.2 to +18.6 points (1.9..18.75: -17.2; 28.8..32.15: -14.5; 32.8..43.25: -8.3; 54.8..64.25: -7.5; 65.7..72.55: -0.7; 76.6..86.35: +25.6; 99.2..110.5: +18.2)
- **res_in** (seconds until the next res) rises from -42.2 to -0.3 points (1.0..8.5: -42.2; 17.5..26.5: +5.9; 35.5..44.5: +12.4; 53.5..62.5: +11.7; 68.5..74.5: +8.9; 80.5..86.5: +6.8; 95.5..107.5: +2.0)

## 7. The usual play

Each choice against the most common one in that kind of decision, in win-chance points over the decision's window, adjusted for the situation, with a 90% range from resampling whole matches. CLEAR = the range excludes 0. Win chance comes from a model that never saw the match. The same comparison over the 30 s BEFORE the decision is a placebo test: a choice can't cause what came before it, so a clear difference there means the effect is partly who makes that choice.

**after wipe** (128 decisions, 56 matches; usual: pushed the pit)
- took the flag (n 16): -9.8 [-19.8, -1.9] CLEAR; in the 30 s before: +0.9 [-7.8, +10.9]
- reset (n 13): -1.7 [-8.0, +7.6]; in the 30 s before: -2.1 [-8.5, +2.0]

**boost clock** (242 decisions, 58 matches; usual: not running, fought)
- not running, fell back (n 37): -3.9 [-9.4, +0.4]; in the 30 s before: -1.4 [-5.3, +1.5]
- running, fought (n 35): +0.6 [-2.3, +3.5]; in the 30 s before: +0.9 [-3.0, +3.7]
- not running, advanced (n 30): +0.4 [-3.1, +4.0]; in the 30 s before: +0.1 [-4.2, +3.5]
- running, advanced (n 25): +4.3 [-0.8, +10.5]; in the 30 s before: -0.3 [-7.2, +3.8]
- not running, held (n 14): -3.7 [-8.2, -0.7] CLEAR; in the 30 s before: +1.7 [-1.5, +3.7]
- not running, to the spawn (n 13): -0.1 [-5.0, +3.9]; in the 30 s before: +2.1 [-2.4, +4.7]
- running, fell back (n 9): +0.5 [-5.6, +6.7]; in the 30 s before: -3.9 [-7.7, +1.0]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - not running, fell back, behind in the fight (lowest third, -0.08 or less): +1.5 (n 11 against 41)
  - not running, fell back, middle third: -2.2 (n 15 against 25)
  - not running, fell back, ahead in the fight (top third, above -0.01): -5.6 (n 11 against 13)
  - running, fought, behind in the fight (lowest third, -0.08 or less): +0.4 (n 10 against 41)
  - running, fought, middle third: +2.4 (n 10 against 25)
  - running, fought, ahead in the fight (top third, above -0.01): +3.1 (n 15 against 13)
  - not running, advanced, behind in the fight (lowest third, -0.08 or less): too few yet (n 4 against 41; means -0.1 against -0.0)
  - not running, advanced, middle third: too few yet (n 8 against 25; means -5.5 against -2.1)
  - not running, advanced, ahead in the fight (top third, above -0.01): +3.8 (n 18 against 13)
  - running, advanced, behind in the fight (lowest third, -0.08 or less): too few yet (n 3 against 41; means -1.9 against -0.0)
  - running, advanced, middle third: +5.1 (n 10 against 25)
  - running, advanced, ahead in the fight (top third, above -0.01): +4.6 (n 12 against 13)
  - not running, held, behind in the fight (lowest third, -0.08 or less): too few yet (n 4 against 41; means -0.6 against -0.0)
  - not running, held, middle third: too few yet (n 2 against 25; means -15.2 against -2.1)
  - not running, held, ahead in the fight (top third, above -0.01): too few yet (n 8 against 13; means -1.6 against -3.1)
  - not running, to the spawn, behind in the fight (lowest third, -0.08 or less): too few yet (n 7 against 41; means -1.9 against -0.0)
  - not running, to the spawn, middle third: too few yet (n 4 against 25; means -1.4 against -2.1)
  - not running, to the spawn, ahead in the fight (top third, above -0.01): too few yet (n 2 against 13; means 0.0 against -3.1)
  - running, fell back, behind in the fight (lowest third, -0.08 or less): too few yet (n 1 against 41; means -0.2 against -0.0)
  - running, fell back, middle third: too few yet (n 6 against 25; means -5.0 against -2.1)
  - running, fell back, ahead in the fight (top third, above -0.01): too few yet (n 2 against 13; means 8.0 against -3.1)

**enemy pickup** (925 decisions, 59 matches; usual: held, fought)
- already running, fought (n 137): -2.7 [-5.9, -0.0] CLEAR; in the 30 s before: +1.4 [-0.6, +3.4]
- held, advanced (n 106): +2.1 [-1.1, +7.0]; in the 30 s before: +3.0 [+0.9, +5.5] ALREADY DIFFERENT BEFORE: partly who chooses it
- already running, advanced (n 92): -0.5 [-3.6, +2.6]; in the 30 s before: +3.8 [+1.7, +6.4] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, fell back (n 77): -1.3 [-5.5, +1.8]; in the 30 s before: -1.9 [-4.0, +0.8]
- ran, fell back (n 67): +1.0 [-2.5, +4.2]; in the 30 s before: -2.8 [-5.9, -0.6] ALREADY DIFFERENT BEFORE: partly who chooses it
- already running, fell back (n 61): -2.3 [-5.6, +1.1]; in the 30 s before: -1.5 [-3.8, +0.9]
- ran, fought (n 58): +1.3 [-1.2, +4.6]; in the 30 s before: -4.3 [-6.9, -2.0] ALREADY DIFFERENT BEFORE: partly who chooses it
- ran, advanced (n 51): -0.8 [-4.6, +3.0]; in the 30 s before: +2.3 [-0.0, +4.9]
- already running, held (n 28): +1.6 [-2.5, +6.3]; in the 30 s before: -1.4 [-3.4, +0.0]
- held, held (n 20): -2.1 [-13.1, +7.4]; in the 30 s before: -0.7 [-10.4, +11.3]
- ran, held (n 15): +2.0 [-2.4, +5.5]; in the 30 s before: -2.5 [-5.8, +0.1]
- held, to the spawn (n 8): +6.4 [-0.1, +10.4]; in the 30 s before: -3.4 [-7.8, +1.5]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - already running, fought, behind in the fight (lowest third, -0.01 or less): +2.3 (n 47 against 53)
  - already running, fought, middle third: -2.7 (n 38 against 81)
  - already running, fought, ahead in the fight (top third, above +0.01): -3.7 (n 52 against 71)
  - held, advanced, behind in the fight (lowest third, -0.01 or less): +5.6 (n 18 against 53)
  - held, advanced, middle third: +2.0 (n 45 against 81)
  - held, advanced, ahead in the fight (top third, above +0.01): +2.7 (n 43 against 71)
  - already running, advanced, behind in the fight (lowest third, -0.01 or less): +6.3 (n 23 against 53)
  - already running, advanced, middle third: +1.2 (n 34 against 81)
  - already running, advanced, ahead in the fight (top third, above +0.01): -2.2 (n 35 against 71)
  - held, fell back, behind in the fight (lowest third, -0.01 or less): -0.7 (n 35 against 53)
  - held, fell back, middle third: -4.3 (n 16 against 81)
  - held, fell back, ahead in the fight (top third, above +0.01): +1.6 (n 26 against 71)
  - ran, fell back, behind in the fight (lowest third, -0.01 or less): +3.5 (n 34 against 53)
  - ran, fell back, middle third: -5.0 (n 17 against 81)
  - ran, fell back, ahead in the fight (top third, above +0.01): +7.5 (n 16 against 71)
  - already running, fell back, behind in the fight (lowest third, -0.01 or less): +1.1 (n 29 against 53)
  - already running, fell back, middle third: -2.8 (n 20 against 81)
  - already running, fell back, ahead in the fight (top third, above +0.01): +0.0 (n 12 against 71)
  - ran, fought, behind in the fight (lowest third, -0.01 or less): +5.3 (n 27 against 53)
  - ran, fought, middle third: -0.9 (n 12 against 81)
  - ran, fought, ahead in the fight (top third, above +0.01): +2.0 (n 19 against 71)
  - ran, advanced, behind in the fight (lowest third, -0.01 or less): +6.2 (n 13 against 53)
  - ran, advanced, middle third: -3.9 (n 24 against 81)
  - ran, advanced, ahead in the fight (top third, above +0.01): -0.4 (n 14 against 71)
  - already running, held, behind in the fight (lowest third, -0.01 or less): +5.1 (n 10 against 53)
  - already running, held, middle third: -1.2 (n 11 against 81)
  - already running, held, ahead in the fight (top third, above +0.01): too few yet (n 7 against 71; means 4.0 against -1.1)
  - held, held, behind in the fight (lowest third, -0.01 or less): too few yet (n 8 against 53; means 1.6 against -3.1)
  - held, held, middle third: too few yet (n 9 against 81; means -11.1 against 1.3)
  - held, held, ahead in the fight (top third, above +0.01): too few yet (n 3 against 71; means 7.6 against -1.1)
  - ran, held, behind in the fight (lowest third, -0.01 or less): too few yet (n 5 against 53; means 2.3 against -3.1)
  - ran, held, middle third: -3.9 (n 10 against 81)
  - held, to the spawn, behind in the fight (lowest third, -0.01 or less): too few yet (n 7 against 53; means 1.0 against -3.1)
  - held, to the spawn, ahead in the fight (top third, above +0.01): too few yet (n 1 against 71; means 20.6 against -1.1)

- **late_game**: not enough decisions yet (20)
**power play** (619 decisions, 61 matches; usual: pushed, advanced)
- pushed, fought (n 171): +0.8 [-1.2, +2.9]; in the 30 s before: +0.3 [-1.6, +2.1]
- held, fought (n 126): -1.4 [-3.1, +0.4]; in the 30 s before: -2.0 [-4.3, +0.2]
- held, fell back (n 48): -1.1 [-4.6, +2.1]; in the 30 s before: -3.8 [-7.8, +0.2]
- pushed, fell back (n 25): -2.0 [-7.0, +5.5]; in the 30 s before: -2.4 [-7.4, +1.6]
- held, advanced (n 18): +1.7 [-0.6, +5.4]; in the 30 s before: -2.1 [-4.5, -0.5] ALREADY DIFFERENT BEFORE: partly who chooses it
- pushed, held (n 9): +1.9 [-2.5, +8.1]; in the 30 s before: +3.8 [-2.2, +9.3]
- held, held (n 7): +0.6 [-2.2, +4.8]; in the 30 s before: -3.8 [-9.7, +3.6]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - pushed, fought, behind in the fight (lowest third, -0.00 or less): +0.2 (n 48 against 71)
  - pushed, fought, middle third: -0.1 (n 61 against 59)
  - pushed, fought, ahead in the fight (top third, above +0.06): +0.5 (n 62 against 85)
  - held, fought, behind in the fight (lowest third, -0.00 or less): -0.4 (n 44 against 71)
  - held, fought, middle third: -4.4 (n 42 against 59)
  - held, fought, ahead in the fight (top third, above +0.06): -2.3 (n 40 against 85)
  - held, fell back, behind in the fight (lowest third, -0.00 or less): -0.3 (n 21 against 71)
  - held, fell back, middle third: -6.0 (n 16 against 59)
  - held, fell back, ahead in the fight (top third, above +0.06): +3.8 (n 11 against 85)
  - pushed, fell back, behind in the fight (lowest third, -0.00 or less): -3.6 (n 10 against 71)
  - pushed, fell back, middle third: -5.0 (n 12 against 59)
  - pushed, fell back, ahead in the fight (top third, above +0.06): too few yet (n 3 against 85; means 7.4 against 0.9)
  - held, advanced, behind in the fight (lowest third, -0.00 or less): too few yet (n 8 against 71; means 1.3 against 1.2)
  - held, advanced, middle third: too few yet (n 6 against 59; means 4.5 against 1.3)
  - held, advanced, ahead in the fight (top third, above +0.06): too few yet (n 4 against 85; means 4.2 against 0.9)
  - pushed, held, behind in the fight (lowest third, -0.00 or less): too few yet (n 7 against 71; means 5.6 against 1.2)
  - pushed, held, middle third: too few yet (n 2 against 59; means -1.0 against 1.3)
  - held, held, behind in the fight (lowest third, -0.00 or less): too few yet (n 6 against 71; means -0.5 against 1.2)
  - held, held, middle third: too few yet (n 1 against 59; means 10.3 against 1.3)

**split in base** (148 decisions, 42 matches; usual: defended without a collapse)
- collapsed (n 61): -6.0 [-11.3, -1.6] CLEAR; in the 30 s before: +1.2 [-2.3, +4.8]
- missed (n 12): -7.0 [-16.7, -0.6] CLEAR; in the 30 s before: +3.5 [-3.2, +13.3]

**Collapses on a split: time away and its cost** (`S32`; per collapse, averages; main = what the main fight lost while the collapsers were away)

| Group | Cases | Away (median s) | Split killed | Collapser died | Own deaths at main | Enemy deaths at main | Flag lead change | DP change | Win change |
|---|---|---|---|---|---|---|---|---|---|
| all | 66 | 18 | 13 | 7 | 0.55 | 0.23 | +2.4 | -2.9 | -4.7 |
| away under 30 s | 42 | 8 | 10 | 1 | 0.02 | 0.1 | +0.8 | +0.2 | -3.2 |
| away 30 to 60 s | 11 | 42 | 0 | 1 | 0.18 | 0.09 | +11.6 | -2.7 | -4.2 |
| away 60 s or more | 13 | 90 | 3 | 5 | 2.54 | 0.77 | -0.4 | -13.2 | -9.9 |
| before 20:00 | 58 | 17.5 | 9 | 5 | 0.33 | 0.21 | +4.2 | -4.3 | -4.7 |
| from 20:00 | 8 | 18 | 4 | 2 | 2.12 | 0.38 | -10.8 | +6.9 | -4.7 |
| split member killed | 13 | 16 | 13 | 1 | 0.08 | 0.77 | +3.6 | +1.4 | -3.8 |
| no kill | 53 | 19 | 0 | 6 | 0.66 | 0.09 | +2.1 | -4.0 | -4.9 |

**Leverage: where the choice matters most** (share of the spread in win-chance change explained by the choice beyond the situation; range = best minus worst choice, in points)

- after wipe (128): choice explains 5.0% (situation 11.1%); range 9.8 points, best pushed the pit, worst took the flag
- boost clock (242): choice explains 4.3% (situation 2.8%); range 7.8 points, best running, advanced, worst not running, held
- split in base (148): choice explains 2.5% (situation 13.4%); range 7.0 points, best defended without a collapse, worst missed
- enemy pickup (925): choice explains 1.2% (situation 4.0%); range 11.5 points, best held, to the spawn, worst already running, fought
- power play (619): choice explains 0.7% (situation 1.7%); range 4.9 points, best pushed, held, worst held, fought

**Behaviour clusters: what teams actually did** (each decision's response grouped by what every player did in the next 20 s; UNNAMED = a group no single named choice covers: a response for Denning to name or reject)

*after wipe* (2 groups, separation 0.31):
- n 78: fought (midline, 1.9 of 8), fought (backline, 1.5 of 8), held (backline, 0.9 of 8), fought (frontline, 0.9 of 8); named as {'pushed the pit': 70, 'reset': 4, 'took the flag': 4}; win change 1.1
- n 50: advanced (backline, 2.9 of 8), advanced (midline, 2.0 of 8), advanced (frontline, 1.3 of 8); named as {'pushed the pit': 29, 'took the flag': 12, 'reset': 9}; win change 3.8 UNNAMED
*boost clock* (4 groups, separation 0.18):
- n 92: fought (midline, 2.2 of 8), fought (backline, 1.8 of 8), fought (frontline, 1.0 of 8); named as {'not running, fought': 60, 'running, fought': 27, 'running, advanced': 2}; win change -0.7
- n 64: held (backline, 1.6 of 8), fought (midline, 0.9 of 8), held (midline, 0.8 of 8), fought (frontline, 0.6 of 8); named as {'not running, fought': 17, 'not running, held': 14, 'not running, to the spawn': 10}; win change 0.2 UNNAMED
- n 58: advanced (midline, 2.2 of 8), advanced (backline, 1.8 of 8), fought (midline, 0.6 of 8), advanced (frontline, 0.5 of 8); named as {'not running, advanced': 29, 'running, advanced': 20, 'running, fought': 2}; win change -1.2 UNNAMED
- n 37: fell back (midline, 2.8 of 8), fell back (backline, 1.9 of 8), fell back (frontline, 0.8 of 8); named as {'not running, fell back': 30, 'running, fell back': 7}; win change -4.1
*enemy pickup* (3 groups, separation 0.2):
- n 370: fought (midline, 2.1 of 8), fought (backline, 1.4 of 8), fought (frontline, 1.1 of 8), held (backline, 0.9 of 8); named as {'held, fought': 160, 'already running, fought': 124, 'ran, fought': 46}; win change -1.9 UNNAMED
- n 307: advanced (midline, 1.9 of 8), advanced (backline, 1.9 of 8), advanced (frontline, 0.9 of 8), fought (backline, 0.6 of 8); named as {'held, advanced': 102, 'already running, advanced': 86, 'ran, advanced': 48}; win change 1.6 UNNAMED
- n 250: fell back (midline, 1.7 of 8), fell back (backline, 1.7 of 8), fell back (frontline, 0.6 of 8), held (backline, 0.6 of 8); named as {'held, fell back': 72, 'ran, fell back': 65, 'already running, fell back': 57}; win change -0.8 UNNAMED
*power play* (3 groups, separation 0.25):
- n 311: fought (midline, 2.1 of 8), fought (backline, 1.7 of 8), fought (frontline, 1.1 of 8), held (backline, 0.8 of 8); named as {'pushed, fought': 160, 'held, fought': 117, 'pushed, advanced': 18}; win change 0.3 UNNAMED
- n 212: advanced (backline, 2.5 of 8), advanced (midline, 2.2 of 8), advanced (frontline, 1.1 of 8); named as {'pushed, advanced': 191, 'held, advanced': 15, 'pushed, fought': 3}; win change 1.6
- n 103: fell back (backline, 2.0 of 8), fell back (midline, 1.7 of 8), fought (midline, 0.6 of 8), fell back (frontline, 0.6 of 8); named as {'held, fell back': 46, 'pushed, fell back': 24, 'held, fought': 8}; win change -0.6 UNNAMED
*split in base* (3 groups, separation 0.2):
- n 71: fought (midline, 2.2 of 8), fought (backline, 1.1 of 8), fought (frontline, 0.9 of 8), held (backline, 0.9 of 8); named as {'defended without a collapse': 43, 'collapsed': 24, 'missed': 4}; win change 0.4
- n 41: fell back (midline, 2.7 of 8), fell back (backline, 1.4 of 8), fell back (frontline, 0.8 of 8); named as {'collapsed': 21, 'defended without a collapse': 15, 'missed': 5}; win change -4.6 UNNAMED
- n 35: advanced (midline, 2.4 of 8), advanced (backline, 1.3 of 8), advanced (frontline, 0.5 of 8), died (midline, 0.5 of 8); named as {'collapsed': 16, 'defended without a collapse': 16, 'missed': 3}; win change -4.2 UNNAMED

## 8. What results and causes are worth

Win points for the team it happened to, from 61 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 208 | +0.6 | -8.0 to +9.2 | +2.7 | no |
| capture | 587 | +3.1 | +2.0 to +4.4 | +2.8 | yes |
| death (any) | 1204 | -6.4 | -9.3 to -3.6 | -3.0 | yes |
| death: against a spike build | 288 | -9.4 | -15.3 to -2.3 | -1.3 | yes |
| death: against other builds | 916 | -5.5 | -8.8 to -2.3 | -3.5 | yes |
| death: back within 20 s | 190 | -5.6 | -10.7 to -0.6 | -1.8 | yes |
| death: down 20 to 60 s | 447 | -8.5 | -12.2 to -4.5 | -2.0 | yes |
| death: down 60 s or more | 567 | -5.1 | -7.8 to -2.4 | -4.1 | yes |
| death: healer | 411 | -4.9 | -7.6 to -2.2 | -3.2 | yes |
| death: healer in own base or pit, back within 15 s (likely deliberate) | 26 | -0.4 | -8.2 to +9.0 | +0.3 | no |
| death: healer, other | 385 | -5.2 | -8.1 to -2.8 | -3.4 | yes |
| death: not a healer | 793 | -7.2 | -10.8 to -3.5 | -2.9 | yes |
| pit NPC lost (any): taken by a spike build | 88 | -7.6 | -14.3 to +1.7 | -4.1 | no |
| pit NPC lost (any): taken by other builds | 417 | -4.1 | -7.4 to -1.0 | -1.2 | yes |
| pit NPC lost: archer | 291 | -2.6 | -5.3 to +0.2 | -0.4 | no |
| pit NPC lost: bodyguard | 71 | -2.7 | -6.7 to +1.0 | +2.1 | no |
| pit NPC lost: knight | 143 | -10.0 | -14.2 to -6.1 | -6.2 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value.

*deaths* (per 10 s in that state; result worth -6.4 points, base rate 1.4%):

- enemies within 1,500 7.5 to 8: result chance +2.6 points, worth -0.16 win points
- current health % 1 to 47.5: result chance +10.7 points, worth -0.69 win points
- own minus enemy team strength -901 to -523: result chance +1.3 points, worth -0.08 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.3 points, worth -0.15 win points
- own healers alive within cast range 0 to 0.5: result chance +0.9 points, worth -0.06 win points
- allies within 1,500 0 to 0.5: result chance +1.1 points, worth -0.07 win points
- maximum health after death penalty, as a share of normal 0.4 to 0.69: result chance +2.6 points, worth -0.17 win points
- match minute 20.95 to 28: result chance +1.6 points, worth -0.1 win points

*kill conversion* (per burst, for the attacking team; result worth +6.4 points, base rate 29.7%):

- damage in the 2 s burst 518.5 to 839: result chance +31.7 points, worth +2.03 win points
- target's health ceiling 0.4 to 0.56: result chance +34.3 points, worth +2.2 win points
- target health % when the burst started 0 to 38.5: result chance +25.9 points, worth +1.66 win points
- target's healers in range 0 to 0.5: result chance +32.2 points, worth +2.06 win points
- attacking minus target team strength 459 to 901: result chance +23.0 points, worth +1.47 win points
- target team's prot skills 5.5 to 6.5: result chance +19.9 points, worth +1.28 win points
- a prot on the target 0.5 to 1: result chance -7.7 points, worth -0.49 win points
- match minute 0.3 to 1.45: result chance -14.8 points, worth -0.95 win points

*npc loss* (per case, for the defending team; result worth -4.7 points, base rate 18.5%):

- own players in the pit 7.5 to 8: result chance -15.3 points, worth +0.72 win points
- damage on the pit NPCs in the last 5 s 367 to 1170: result chance +36.6 points, worth -1.72 win points
- own players alive outside the pit 0 to 0.5: result chance +16.7 points, worth -0.79 win points
- enemy players in the pit 7.5 to 8: result chance +14.7 points, worth -0.69 win points
- of which healers 0 to 0.5: result chance +15.7 points, worth -0.74 win points
- attackers' measured damage per second against a Lord (benchmarks) 18.75 to 28.65: result chance -6.9 points, worth +0.33 win points
- healing on own pit NPCs and Lord in the last 10 s 688.5 to 1747: result chance -8.9 points, worth +0.42 win points
- match minute 23.45 to 28: result chance -4.4 points, worth +0.21 win points

## Why: five events of the new matches

For each, the engine's account of why it happened, every number measured and placed against the same role or situation in every stored match (forensics.py, events.py), with models that never saw the match.

### OG v Dz (a921418b), 4:17 to 4:32: Dz lost 1 player on the own base

1. **Result**: deaths Dz 3 until all were back; Dz lost knight, knight; flag lead -8 s; death penalty {'Dz': -30, 'OG': 0}. Win chance for Dz 77.5% -> 29.3% (-48.2); moved by knights_diff -24.2, knights_diff & map_flag_run -24.0, down_diff_s +11.8, morale_diff & lord_dps_enemy -8.2, pit_pressure_diff -5.4.
2. **Mechanics** (deaths model that never saw this match, a few seconds before each death; what raised the risk most):
   - Dz Assassin 1 at 4:32 (engine's cause: positioning: out of range of its monks): risk 5.0% at 4:30; health +40.9, enemies within 1,500 +13.3, healers in range +12.2, enemy_blind +7.2 [health 42%, ceiling 1.0, 5 enemies and 2 allies near, 0 healers in range]
   - why Dz Assassin 1's health dropped (forensics, against the same role in every stored match):
     - Position: partly (nearest allied healer 1623 in the last 5 s, nearest enemy 108, allies in casting range 3.5, enemies 3.0)
     - Prots: no prots (0 from teammates, 0 self; 0 of 0 landed); damage 665 (37% attacks, 12% armor-ignoring), burst 266 in 2 s at 4:29.6; knockdowns 2, knockdown immunity up for 0
     - Healers under interrupt pressure: usual (healers 3, interrupts_per_min 0.0, interrupted 0, casts 18, finished_share 0.94, dazed 0, knockdowns 0, hexes 1)
     - Damage off shield sets: yes (team share 0.63, a shield would have stopped about 223)
     - Own damage: usual (47.9 per second on [('OG 7 Monk', 284), ('OG Air Ele 2', 257)]); enemy damage: high (94.0 per second)
     - Peel: partly (controlled, but an attacker was left free for 16.1 s) (2 of 2 attackers controlled; longest free 16.1 s)
     - Casting: unclear (casts 8, interrupted 0, cancelled 0, while_dazed 0)
3. **Setup** (phase 3:59 to 4:22):
   - Dz plan 8v8 brawl: backside 7v8 hold (Ritualist, 7 Monk, Prot, Stand Mes, Mes/A, Paragon, Assassin 1)
     where the deaths came: 7v8, 4 damage, 3 healers, pressure 35/s, incoming 26/s, sustain margin +29, uptime 33%, control received 1 interrupts (1 on healers), 3 knockdowns
   - OG plan 8v8 brawl: push side 8v7 convert (8 Monk, 7 Monk, Prot, Mesmer, Air Ele 2, Air Ele 1, Assassin 2, Assassin 1)
     where the deaths came: 8v7, 5 damage, 3 healers, pressure 56/s, incoming 36/s, sustain margin +36, uptime 43%, control received 0 interrupts (0 on healers), 0 knockdowns
4. **Decision** (split in base at 4:00): Dz chose 'on time: Assassin 2 (from field), Stand Mes (from field), Ritualist (from field)' (to the spawn 3, fought 2, held 2); usual there: on time; that choice is worth +0.0 points against the usual [+0.0, +0.0].
**Why, in short**: Dz fought 7v8 on the backside (job: hold) with sustain margin +29 with everyone there; the Assassin 1 died because no prot landed in time (0 of 0 landed), knocked down 2 times with no knockdown immunity up, the enemy hit unusually hard (94.0 per second); after choosing 'on time: Assassin 2 (from field), Stand Mes (from field), Ritualist (from field)' at the split in base.
5. **Context**: Dz: 8 up (main 8), flags up +32 s, DP -45, NPCs K2 A2 B1, Lord dmg 0; OG: 8 up (main 8), flags down -32 s, DP 80, NPCs K2 A2 B1, Lord dmg 0; stand OG, boost in 92 s; builds balance v balance; situation: lost while up in numbers where it fought 6v5, defending its own pit (K2 A2 B1 alive).

### ohno v Crew (77206c78), 1:09 to 1:24: Crew lost 1 player on the backside

1. **Result**: deaths Crew 2 until all were back; Crew lost archer, knight; captures {'ohno': 1}; flag lead -95 s; death penalty {'Crew': -30, 'ohno': 0}. Win chance for Crew 37.4% -> 3.0% (-34.4); moved by knights_diff -19.6, stand -10.4, knights_diff & map_flag_run -10.1, morale_diff -8.9, alive_diff -7.9.
2. **Mechanics** (deaths model that never saw this match, a few seconds before each death; what raised the risk most):
   - Crew 8 Monk at 1:24 (engine's cause: positioning: chased down while retreating): risk 32.8% at 1:20; health +40.9, healers in range +12.0, enemies within 1,500 +11.6, strength gap +8.5 [health 29%, ceiling 1.0, 4 enemies and 4 allies near, 0 healers in range]
   - why Crew 8 Monk's health dropped (forensics, against the same role in every stored match):
     - Position: yes (nearest allied healer 6740 in the last 5 s, nearest enemy 153, allies in casting range 3.0, enemies 3.0)
     - Prots: late or interrupted (0 from teammates, 1 self; 0 of 1 landed); damage 892 (53% attacks, 49% armor-ignoring), burst 264 in 2 s at 1:05.7
     - Healers under interrupt pressure: usual (healers 3, interrupts_per_min 3.0, interrupted 1, casts 12, finished_share 0.92, dazed 0, knockdowns 0, hexes 1)
     - Damage off shield sets: usual (team share 0.25, a shield would have stopped about 40)
     - Own damage: usual (46.6 per second on [('ohno Mesmer', 431), ('ohno Dervish', 421)]); enemy damage: usual (56.5 per second)
     - Peel: no (peel on a burst is rare: most bursts on this role get none) (0 of 2 attackers controlled; longest free 8.2 s)
     - Casting: interrupted far more than usual (casts 5, interrupted 1, cancelled 0, while_dazed 0)
3. **Setup** (phase 0:52 to 1:23):
   - Crew plan flag game: push side 4v4 contest (8 Monk, Stand Mes, Paragon, Warrior); backside 3v3 contest (7 Monk, Prot (WoC), Mes/A); backside 1v0 free (Monk 5 (WoC))
     where the deaths came: 4v4, 3 damage, 1 healers, pressure 37/s, incoming 37/s, sustain margin -2, uptime 47%, control received 1 interrupts (1 on healers), 0 knockdowns
   - ohno plan regrouping: backside 4v4 contest (7 Monk, Prot, Mesmer, Dervish); push side 3v3 contest (8 Monk, Fire Ele, Air Ele); backside 1v0 free (Ritualist)
     where the deaths came: 4v4, 2 damage, 2 healers, pressure 37/s, incoming 37/s, sustain margin +11, uptime 65%, control received 1 interrupts (1 on healers), 0 knockdowns
4. **Decision** (enemy pickup at 1:07): Crew chose 'already running' (fell back 4, carrying 1, died 1, fought 1, to the spawn 1); usual there: already running, fought; that choice is worth +0.0 points against the usual [+0.0, +0.0].
**Why, in short**: Crew fought 4v4 on the push side (job: contest) with sustain margin -2 while the rest were backside (contest), backside (free); the 8 Monk died because no prot landed in time (0 of 1 landed), its casts were interrupted (1 of 5), position (no allied healer within casting range, nearest enemy 153); after choosing 'already running' at the enemy pickup.
5. **Context**: Crew: 8 up (main 4), flags up +59 s, DP 0, NPCs K2 A2 B1, Lord dmg 0; ohno: 8 up (main 4), flags down -59 s, DP 0, NPCs K2 A2 B1, Lord dmg 0; stand Crew, boost in 103 s; builds WoC spike v balance; situation: fought away from pit while up on flags (+59 s): could fall back, a monk died first.

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

### Power play without a kill: One v ohno (c553716d), 8:08.0 to 9:04.0
**Situation**: main 7v3, alive 8v8, flags down (-62 s), DP -125, boost in 108; choice held (held 5, carrying 1, fought 1, to the spawn 1); deaths {'One': 0, 'ohno': 0} in 56 s
**The fight's shape** (every 5 s: own main, the enemy group it faced, distance between them, that group's distance to the rest of its team): 8:08.0 7v3 1714 apart, 2223 from its others; 8:13.0 8v3 1274 apart, 3012 from its others; 8:18.0 8v3 1156 apart, 1950 from its others; 8:23.0 8v4 889 apart, 4486 from its others; 8:28.0 8v4 782 apart, 4355 from its others; 8:33.0 8v4 937 apart, 4585 from its others; 8:38.0 8v4 845 apart, 4503 from its others; 8:43.0 8v4 975 apart, 5479 from its others; 8:48.0 8v4 1829 apart, 5740 from its others; 8:53.0 8v4 3212 apart, 3548 from its others; 8:58.0 8v4 3620 apart, 1794 from its others; 9:03.0 8v8 3072 apart, None from its others
**One's damage**: 12.0 per second (below the 20th percentile for team (median 37.1, n 3825)); top target share 0.41 (below the 50th percentile for team (median 0.49, n 3825)); targets [('ohno Mesmer', 274), ('ohno AoB Derv', 261), ('ohno Prot', 137)]; dealers [('One Monk 4 (WoC)', 672)]
- phase 8:00.0 to 8:18.0: 8v3 (own pit, job defend), damage uptime 0.07, damage-seconds lost {'idle': 54, 'moving': 20, 'carrying': 10}
- phase 8:18.0 to 8:27.0: 8v4 (own pit, job defend), damage uptime 0.29, damage-seconds lost {'idle': 18, 'moving': 14}
- phase 8:27.0 to 8:49.0: 8v4 (own pit, job defend), damage uptime 0.09, damage-seconds lost {'idle': 58, 'moving': 42}
- phase 8:49.0 to 8:58.0: 8v0 (own pit, job free), damage uptime 0.07, damage-seconds lost {'idle': 29, 'moving': 13}
- phase 8:58.0 to 9:13.0: 8v0 (own pit, job free), damage uptime 0.03, damage-seconds lost {'idle': 48, 'moving': 25}
**ohno's answer**: healing 22 per second ({'ohno 7 Monk': 814, 'ohno 8 Monk': 279, 'ohno Mesmer': 56, 'ohno Prot': 47}); prots {'Guardian': 1}
- One's knockdowns landed 1; ohno's knockdown immunity casts 0
- Pressure on ohno's healers: healers 3, interrupts_per_min 0.0, interrupted 0, casts 9, finished_share 1.0, dazed 0, knockdowns 0, hexes 0 (around the median for team (median 0, n 4312))
- Snares, Blind and Weakness One put on ohno: none

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

