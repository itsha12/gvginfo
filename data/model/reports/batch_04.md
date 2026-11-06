# Learning report, batch 4

Trained on 46 matches (6 new in this batch). Variables in use: 20; build variables from 60 matches, interactions from 40.

## 0. Data integrity

- Lengths repaired: 3 (1f65fd3b 150 s -> 1027 s) (bbef1904 617 s -> 599 s) (36a65ac6 1319 s -> 1294 s) 
- Matches with a team's Lord damage not observed (left blank, not zero): 2
- Pit NPCs added from the standard roster (never seen in the replay): 143 in 39 matches
- Left out of training: 0

## 1. The honest test

**Not yet better than strength alone: treat the curves as noise.** Held-out accuracy (matches held out whole), log loss in brackets (lower is better):

- strength only: all 73% (0.448), 0-5 min 80% (0.376), 5-10 min 76% (0.434), 10-15 min 69% (0.509), 15-end min 64% (0.509), matches lasting 15 min+ 67% (0.534), matches even on strength (gap under 200) 52% (0.649)
- glass box: all 76% (0.53), 0-5 min 81% (0.406), 5-10 min 78% (0.462), 10-15 min 72% (0.605), 15-end min 72% (0.71), matches lasting 15 min+ 70% (0.65), matches even on strength (gap under 200) 59% (0.895)
- glass box without corrections: all 76% (0.53), 0-5 min 81% (0.404), 5-10 min 78% (0.454), 10-15 min 72% (0.6), 15-end min 71% (0.726), matches lasting 15 min+ 70% (0.651), matches even on strength (gap under 200) 59% (0.895)
- black box: all 71% (1.16), 0-5 min 77% (0.924), 5-10 min 72% (1.093), 10-15 min 65% (1.38), 15-end min 65% (1.37), matches lasting 15 min+ 62% (1.511), matches even on strength (gap under 200) 61% (1.536)
- Gain over strength alone (log loss, resampling whole matches): -0.083 (90% range -0.263 to +0.058).
- Change since batch 3: glass box log loss 0.563 -> 0.53; strength only 0.469 -> 0.448.

## 2. What it leans on

- **morale_diff** 0.645 (was 0.714): own minus enemy morale summed over players (boosts +, death penalty -)
- **morale_diff & morale_total** 0.279 (was 0.275): own minus enemy morale summed over players (boosts +, death penalty -) TOGETHER WITH both teams' morale summed (how much death penalty is in the game overall)
- **spike_killable_diff** 0.277 (was 0.301): enemy minus own players within one spike of the other side (DP stacking; 0 unless a spike build is involved)
- **morale_diff & archers_diff** 0.266 (was 0.286): own minus enemy morale summed over players (boosts +, death penalty -) TOGETHER WITH own minus enemy pit archers alive
- **stand** 0.245 (was 0.25): who holds the flag stand: 1 own, 0 nobody, -1 enemy
- **morale_total & archers_diff** 0.245 (was 0.271): both teams' morale summed (how much death penalty is in the game overall) TOGETHER WITH own minus enemy pit archers alive
- **main_diff** 0.23 (was 0.219): own minus enemy players in each team's main group
- **knights_diff** 0.217 (was 0.162): own minus enemy pit knights alive
- **flag_lead** 0.206 (was 0.205): seconds up (+) or down (-) on flags: enemy's response minus own on the next capture exchange
- **knights_diff & lord_damage_diff** 0.188 (was 0.206): own minus enemy pit knights alive TOGETHER WITH own minus enemy Lord damage dealt so far (the 28:00 tiebreak; players can't see it); blank when either team's Lord damage wasn't observed
- **pit_pressure_diff** 0.186 (was 0.188): own players in the enemy pit minus enemy players in the own pit
- **lord_damage_diff** 0.179 (was 0.151): own minus enemy Lord damage dealt so far (the 28:00 tiebreak; players can't see it); blank when either team's Lord damage wasn't observed

## 3. The curves in words

Points = win-chance points added to an otherwise even game at each range of the variable.

- **morale_diff** rises from -37.1 to +31.1 points (-470.0..-190.5: -37.1; -144.5..-114.5: -16.9; -88.5..-46.5: -13.8; -15.5..-1.0: +0.3; 1.0..23.0: +1.6; 55.0..96.0: +17.4; 134.5..170.5: +23.5)
- **morale_diff & morale_total** (interaction): see wp_model.md
- **spike_killable_diff** rises from -36.8 to +37.4 points (-8.0..-7.5: -36.8; -5.5..-3.5: -35.3; -2.5..-1.5: -32.1; -0.5..0.5: -0.1; 1.5..2.5: +33.0; 4.5..7.5: +37.0)
- **morale_diff & archers_diff** (interaction): see wp_model.md
- **stand** rises from -6.5 to +6.5 points (-1.0..-0.5: -6.5; -0.5..0.5: +0.2; 0.5..1.0: +6.5)
- **morale_total & archers_diff** (interaction): see wp_model.md
- **main_diff** rises from -19.3 to +18.4 points (-8.0..-4.5: -19.3; -3.5..-2.5: -9.4; -1.5..-0.5: -5.7; 0.5..1.5: +5.6; 2.5..3.5: +9.0; 4.5..8.0: +18.4)
- **knights_diff** rises from -18.7 to +16.8 points (-2.0..-1.5: -18.7; -1.5..-0.5: -0.1; -0.5..0.5: +0.4; 0.5..1.5: +0.7; 1.5..2.0: +16.8)
- **flag_lead** falls from +11.2 to -12.6 points (-86.0..-70.5: +11.2; -55.5..-41.5: -3.7; -29.5..-18.5: -4.2; -8.5..-0.5: -1.9; 8.5..18.5: +4.3; 29.5..41.5: +4.7; 55.5..70.5: -4.9)
- **knights_diff & lord_damage_diff** (interaction): see wp_model.md

## 4. Discovery

**Interaction candidates** (a screen: pairs whose combination seems to matter beyond each alone; untested until held-out matches confirm them; switched on in the model from 40 matches):

- morale_diff with spike_killable_diff (screen 0.103)
- alive_diff with morale_diff (screen 0.099)
- down_diff_s with morale_diff (screen 0.097)
- alive_diff with spike_killable_diff (screen 0.092)
- main_diff with morale_diff (screen 0.091)
- down_diff_s with spike_killable_diff (screen 0.090)
- boost_clock with spike_killable_diff (screen 0.089)
- stand with spike_killable_diff (screen 0.089)

**Candidate variables** (proposed variables, tested on unseen matches; log loss, lower is better):

- split_diff: 0.53 without, 0.531 with: does not improve yet. own minus enemy players on a split (away from their main group on the enemy half, not carrying). Proposed batch 1 by Claude: the knights curve runs backwards, maybe standing in for the cost of splitting

**Surprises** (moments where the held-out model was most confident about the team that went on to lose; each points to something the variables don't capture yet):

- hdm v HC (28447c4a) at 16:45: a model that never saw this match gave HC 0.3%, and HC won. Why it thought so: morale_diff -33.2, knights_diff -32.8, lord_damage_diff -20.7, team strength -16.4, lord_exposed_diff -15.5
- Men v HC (faec428a) at 20:00: a model that never saw this match gave Men 0.7%, and Men won. Why it thought so: lord_damage_diff -47.3, pit_pressure_diff -16.3, team strength +14.9, lord_health_diff +13.4, bodyguard_diff -11.9
- OG v hold (49eec28d) at 4:45: a model that never saw this match gave OG 2.3%, and OG won. Why it thought so: lord_health_diff -35.5, morale_diff -32.5, morale_diff & archers_diff -20.7, morale_diff & morale_total -20.1, team strength +19.0
- hdm v Men (0f1fd794) at 28:00: a model that never saw this match gave hdm 99.2%, and hdm lost. Why it thought so: lord_damage_diff +48.3, minute & lord_damage_diff +38.0, lord_health_diff -23.5, minute & bodyguard_diff +21.1, main_diff +9.3
- RACK v hdm (1f65fd3b) at 15:15: a model that never saw this match gave hdm 98.4%, and hdm lost. Why it thought so: morale_diff +25.2, knights_diff +22.2, minute & lord_damage_diff +18.5, knights_diff & lord_damage_diff +14.5, team strength +14.0
- Team v push (2df9b7fd) at 2:15: a model that never saw this match gave Team 7.5%, and Team won. Why it thought so: spike_killable_diff -48.2, team strength +48.1, main_diff -27.0, pit_pressure_diff -16.7, stand -6.6

## 5. Denning's rulings seen through the model

Win chance from a model that never saw the match, 20 s before and 60 s after each ruled moment. Contributions are points for an otherwise even game (the curves' scale).

- hdm v HC (28447c4a) 5:01 (split answered), HC: 12.8% 20 s before -> 37.0% 60 s after (+24.2). After: knights_diff -32.8, flag_lead & morale_diff +28.0, team strength -16.4, pit_pressure_diff +15.2
- hdm v HC (28447c4a) 5:01 (split answered), hdm: 88.8% 20 s before -> 63.3% 60 s after (-25.5). After: knights_diff +33.6, flag_lead & morale_diff -29.5, team strength +16.4, pit_pressure_diff -14.5
- hdm v HC (28447c4a) 1:02 (split detection), HC: 39.5% 20 s before -> 6.8% 60 s after (-32.7). After: flag_lead & morale_diff -26.2, team strength -16.4, carrying_diff -10.4, flag_lead +8.0
- hdm v HC (28447c4a) 1:02 (split detection), hdm: 61.0% 20 s before -> 92.1% 60 s after (+31.1). After: flag_lead & morale_diff +23.8, team strength +16.4, carrying_diff +8.7, flag_lead -8.1
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), HC: 10.5% 20 s before -> 1.5% 60 s after (-9.0). After: knights_diff -32.8, morale_diff & archers_diff -26.4, team strength -16.4, lord_exposed_diff -15.5
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), hdm: 72.2% 20 s before -> 95.8% 60 s after (+23.6). After: knights_diff +33.6, lord_damage_diff & minute -30.4, morale_diff & archers_diff +19.7, team strength +16.4
- hdm v HC (bbef1904) 8:10 (death), HC: 39.8% 20 s before -> 6.9% 60 s after (-32.9). After: team strength -16.0, down_diff_s -13.6, morale_diff -13.4, alive_diff -12.9
- hdm v HC (bbef1904) 8:10 (death), hdm: 60.7% 20 s before -> 94.0% 60 s after (+33.3). After: down_diff_s +25.1, alive_diff +16.3, team strength +16.0, fight_state -12.8
- Men v HC (faec428a) 9:31 (death), HC: 29.2% 20 s before -> 40.3% 60 s after (+11.1). After: team strength -14.9, archers_diff +10.6, stand -6.2, minute & morale_diff +3.1
- Men v HC (faec428a) 9:31 (death), Men: 75.6% 20 s before -> 65.0% 60 s after (-10.6). After: team strength +14.9, archers_diff -10.4, stand +6.2, morale_diff & morale_total -4.3

## 6. Why: the node models

Each explains one result from what happened before it (time order enforced), tested on matches it never saw. AUC = how often a moment that led to the result scores above one that didn't (0.5 = guessing, 1 = perfect).

**deaths** (46 matches, 107777 moments, 2898 results): adds to the simple baseline (AUC 0.913 against 0.802 for health_pct and damage_taken_3s alone).
- **enemies_near** (enemies within 1,500) rises from -18.0 to +24.3 points (0.0..0.5: -18.0; 0.5..1.5: -9.7; 1.5..2.5: -0.0; 2.5..3.5: +1.4; 3.5..4.5: +7.4; 4.5..5.5: +9.2; 5.5..6.5: +11.0; 6.5..7.5: +13.7; 7.5..8.0: +24.3)
- **local_diff** (allies minus enemies within 2,000) falls from +29.1 to -20.1 points (-8.0..-3.5: +29.1; -2.5..-1.5: +14.4; -0.5..0.5: -7.7; 1.5..2.5: -8.8; 3.5..4.5: +13.6; 5.5..7.0: -20.1)
- **health_pct** (current health %) falls from +40.3 to -6.2 points (1.0..47.5: +40.3; 59.5..67.5: +23.5; 73.5..78.5: +9.7; 82.5..85.5: +4.5; 88.5..91.5: +1.0; 93.5..95.5: -1.6; 97.5..99.5: -4.5)
- **strength_gap** (own minus enemy team strength) falls from +7.1 to -8.3 points (-815.0..-498.5: +7.1; -332.5..-267.0: +10.4; -117.5..-86.5: +0.7; -17.5..11.0: +7.6; 86.5..117.5: -11.2; 226.0..301.0: -3.3; 360.0..498.5: -12.1)
- **health_ceiling** (maximum health after death penalty, as a share of normal) falls from +31.3 to -10.7 points (0.4..0.69: +31.3; 0.72..0.84: +21.0; 0.85..0.89: +15.2; 0.94..0.95: +9.6; 0.99..1.0: -0.7; 1.1..1.1: -10.7)
- **healers_in_range** (own healers alive within cast range) falls from +11.7 to -11.8 points (0.0..0.5: +11.7; 0.5..1.5: -3.1; 1.5..2.5: -5.3; 2.5..3.5: -3.7; 3.5..4.0: -11.8)
- **allies_near** (allies within 1,500) falls from +10.4 to -5.6 points (0.0..0.5: +10.4; 0.5..1.5: +7.2; 1.5..2.5: +5.4; 2.5..3.5: -2.4; 3.5..4.5: -1.5; 4.5..5.5: -2.7; 5.5..6.5: -4.2; 6.5..7.0: -5.6)
- **minute** (match minute) rises from -2.6 to +14.0 points (0.1..1.25: -2.6; 2.35..3.45: -4.3; 4.55..5.65: +2.8; 6.95..8.45: +3.4; 10.05..11.75: -3.0; 13.55..15.45: +2.5; 17.85..20.75: +6.4)
- **dist_own_pit** (distance from its own pit) rises from +0.5 to +16.9 points (10.0..1473.5: +0.5; 2487.5..4168.5: -3.4; 5241.5..6074.5: -5.7; 6913.5..7615.5: -2.0; 8282.5..8872.5: -2.5; 9696.5..10621.5: +0.8; 11778.5..13072.5: +10.5)

**kill conversion** (46 matches, 797 moments, 243 results): adds to the simple baseline (AUC 0.787 against 0.677 for burst_damage and target_health_pct alone).
- **target_ceiling** (target's health ceiling) falls from +33.4 to -18.3 points (0.4..0.56: +33.4; 0.69..0.7: +21.2; 0.78..0.83: +19.1; 0.86..0.88: +15.8; 0.91..0.94: +11.3; 0.95..0.99: +7.5; 1.02..1.1: -7.3)
- **burst_damage** (damage in the 2 s burst) rises from -9.6 to +25.4 points (250.0..257.5: -9.6; 266.5..276.5: -14.2; 286.5..296.5: -7.4; 313.5..325.5: -2.8; 343.5..363.5: -0.9; 391.0..421.0: +2.0; 467.5..540.0: +24.0)
- **target_health_pct** (target health % when the burst started) falls from +27.4 to -9.4 points (0.0..38.5: +27.4; 50.5..55.5: +10.3; 61.5..67.5: +4.8; 72.5..76.5: +3.0; 79.5..82.5: -4.6; 86.5..90.5: -9.8; 95.5..99.5: -9.3)
- **target_healers_in_range** (target's healers in range) falls from +26.8 to -7.5 points (0.0..0.5: +26.8; 0.5..1.5: -0.3; 1.5..2.5: -5.4; 2.5..3.0: -7.5)
- **target_prot_up** (a prot on the target) falls from +5.1 to -10.7 points (0.0..0.5: +5.1; 0.5..1.0: -10.7)
- **minute** (match minute) rises from -10.1 to +7.2 points (0.3..1.45: -10.1; 2.75..3.95: -2.2; 4.95..6.35: -1.8; 7.35..8.65: -0.1; 10.25..11.45: +2.4; 13.55..15.35: +3.4; 17.45..20.65: +4.3)
- **attackers** (attackers in the burst) falls from -2.3 to -13.2 points (3.0..3.5: -2.3; 3.5..4.5: +3.0; 4.5..5.5: +6.0; 5.5..6.5: -7.9; 6.5..7.0: -13.2)
- **attackers_interrupted** (interrupts on the attackers (5 s before to 2 s after)) falls from +1.8 to -24.3 points (0.0..0.5: +1.8; 0.5..1.5: -14.4; 1.5..2.0: -24.3)
- **strength_gap** (attacking minus target team strength) rises from -5.8 to +15.5 points (-815.0..-360.0: -5.8; -252.5..-133.0: -3.6; -117.5..-10.0: -1.3; 0.0..68.0: -0.2; 117.5..252.5: +0.9; 267.0..287.5: -0.4; 401.5..498.5: +6.6)

**flag answer** (seconds an answer to an enemy capture was slower than possible; 43 matches, 436 rows): adds to the simple baseline (typical error 17.4s against 27.5s for the median; explains 70% of the spread).
- **parked_s** (seconds the flag lay parked (dropped 5 s or more: not running yet)): 0.0..2.5: -5.6 s; 11.5..16.5: +4.1 s; 27.5..30.5: +20.0 s; 36.5..41.0: +40.5 s; 52.5..62.5: +57.1 s; 89.0..101.5: +58.6 s; 124.5..291.0: +58.4 s
- **enemy_deaths_during** (enemy deaths during the answer): 0.0..0.5: -4.2 s; 0.5..1.5: +12.7 s; 1.5..2.5: +21.3 s; 2.5..3.5: +32.3 s; 3.5..5.0: +32.8 s
- **own_deaths_during** (own deaths during the answer): 0.0..0.5: -3.9 s; 0.5..1.5: +5.5 s; 1.5..2.5: +6.4 s; 2.5..3.5: +13.0 s; 3.5..4.5: +31.4 s; 4.5..5.5: +42.7 s; 5.5..6.5: +59.6 s; 6.5..8.0: +63.4 s; 8.0..17.0: +62.4 s
- **enemies_in_the_way** (enemy presence along the runner's trip back to the spawn): 0.0..0.5: -5.8 s; 4.5..9.5: -4.3 s; 14.5..20.5: -2.5 s; 25.0..35.0: -1.5 s; 47.5..55.5: +3.1 s; 75.5..106.5: +8.5 s; 133.5..183.5: +16.5 s
- **carrier_damage_taken** (damage the carrier took while carrying): 0.0..1.0: -3.2 s; 29.0..50.5: -4.3 s; 77.0..100.5: -2.2 s; 135.5..189.5: +1.1 s; 248.5..278.0: +4.5 s; 369.5..503.0: +6.5 s; 623.5..1040.0: +7.3 s
- **runner_to_spawn** (runner's distance to its flag spawn when the enemy captured): 4.0..870.5: -11.4 s; 1472.5..2149.5: -3.5 s; 3362.5..4097.0: -0.2 s; 4553.0..5220.0: +2.4 s; 5872.0..6648.5: +3.3 s; 7174.0..7742.5: +3.2 s; 8359.0..9110.0: +4.0 s
- **possible_s** (fastest possible answer (s) from the flag model at the enemy's capture): 0.0..4.5: +0.5 s; 9.5..17.5: +2.1 s; 24.5..30.5: +2.7 s; 34.5..38.5: +4.4 s; 42.5..46.5: +2.0 s; 50.5..56.5: -2.3 s; 62.5..69.5: -6.9 s
- **quick_handoffs** (quick hand-offs (a teammate picked it up within 5 s)): 0.0..0.5: -1.9 s; 0.5..1.5: +6.5 s; 1.5..2.5: +6.0 s; 2.5..3.0: +15.8 s
- **morale_diff** (own minus enemy morale): -200.0..-120.0: +8.0 s; -76.0..-53.0: +4.9 s; -31.0..-18.0: +1.3 s; -14.0..-1.0: +0.2 s; 6.5..18.0: -0.5 s; 32.5..62.0: -3.8 s; 90.0..132.0: -4.4 s
- **alive_diff** (own minus enemy players alive): -4.0..-2.5: +17.0 s; -2.5..-1.5: +17.5 s; -1.5..-0.5: +6.8 s; -0.5..0.5: -0.8 s; 0.5..1.5: -6.7 s; 1.5..6.0: -1.0 s

**npc loss** (46 matches, 5270 moments, 954 results): adds to the simple baseline (AUC 0.798 against 0.763 for attackers and defenders alone).
- **defenders** (own players in the pit) falls from +38.7 to -39.8 points (0.0..0.5: +38.7; 0.5..1.5: +25.3; 1.5..2.5: +17.9; 2.5..3.5: -2.9; 3.5..4.5: -20.2; 4.5..5.5: -21.1; 5.5..6.5: -22.2; 6.5..7.5: -33.4; 7.5..8.0: -39.8)
- **npc_damage_5s** (damage on the pit NPCs in the last 5 s) rises from -16.0 to +31.3 points (0.0..0.5: -16.0; 23.5..38.5: -1.7; 53.5..72.5: +7.7; 91.5..113.5: +13.6; 135.5..160.5: +24.4; 189.5..227.5: +26.7; 280.5..369.5: +29.4)
- **defenders_elsewhere** (own players alive outside the pit) falls from +22.1 to -0.9 points (0.0..0.5: +22.1; 0.5..1.5: +13.2; 1.5..2.5: +15.3; 2.5..3.5: +4.8; 3.5..4.5: -2.1; 4.5..5.5: -11.6; 5.5..6.5: -17.5; 6.5..7.5: -16.8; 7.5..8.0: -0.9)
- **attackers** (enemy players in the pit) rises from -13.8 to +22.0 points (1.0..1.5: -13.8; 1.5..2.5: -11.5; 2.5..3.5: -3.4; 3.5..4.5: +1.7; 4.5..5.5: +16.7; 5.5..6.5: +18.9; 6.5..7.5: +20.0; 7.5..8.0: +22.0)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -10.0 to +3.3 points (2.0..15.8: -10.0; 22.2..28.7: -8.6; 31.4..34.1: -5.7; 42.85..52.75: -3.8; 62.75..67.05: +8.8; 74.45..81.2: +7.9; 90.95..103.95: +10.0)
- **strength_gap** (attacking minus defending team strength) rises from -6.8 to +5.3 points (-815.0..-415.5: -6.8; -316.5..-233.5: -10.5; -117.5..-6.0: -4.0; 52.5..102.5: +2.1; 117.5..267.0: +7.9; 303.5..386.0: +5.2; 498.5..570.0: -0.7)
- **archers** (own pit archers alive) rises from -0.9 to +33.8 points (0.0..0.5: -0.9; 0.5..1.5: -6.9; 1.5..2.5: +4.4; 2.5..3.0: +33.8)

**lord damage** (Lord damage dealt in the next 10 s while players are in the enemy pit; 45 matches, 6165 rows): adds to the simple baseline (typical error 118.4 against 78.1 for the median; explains 33% of the spread).
- **defenders** (own players in the pit): 0.0..0.5: +163.3; 0.5..1.5: +91.6; 1.5..2.5: +33.5; 2.5..3.5: -21.1; 3.5..4.5: -61.3; 4.5..5.5: -101.2; 5.5..6.5: -123.8; 6.5..7.5: -125.4; 7.5..8.0: -109.5
- **defenders_elsewhere** (own players alive outside the pit): 0.0..0.5: +61.8; 0.5..1.5: +72.4; 1.5..2.5: +74.8; 2.5..3.5: +72.3; 3.5..4.5: +35.2; 4.5..5.5: -2.4; 5.5..6.5: -51.0; 6.5..7.5: -101.0; 7.5..8.0: -155.3
- **bodyguard** (own Bodyguard alive): 0.0..0.5: +106.6; 0.5..1.0: -43.2
- **attackers** (enemy players in the pit): 1.0..1.5: -43.2; 1.5..2.5: -29.2; 2.5..3.5: -29.7; 3.5..4.5: -15.5; 4.5..5.5: +54.5; 5.5..6.5: +67.6; 6.5..7.5: +66.5; 7.5..8.0: +101.0
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)): 2.0..15.8: -46.9; 22.6..30.15: -32.7; 33.95..34.1: -35.3; 42.85..54.25: -13.6; 62.85..69.15: +14.9; 76.0..82.35: +48.8; 93.25..105.0: +58.4
- **defender_healers** (of which healers): 0.0..0.5: +62.4; 0.5..1.5: -2.9; 1.5..2.5: -17.4; 2.5..3.0: -42.4
- **seconds_in_pit** (seconds the attackers have been in the pit): 0.0..4.5: -22.1; 10.5..16.5: -24.1; 22.5..28.5: -18.2; 37.5..46.5: -9.2; 58.5..70.5: +15.4; 85.5..103.5: +20.9; 130.5..181.5: +49.0
- **archers** (own pit archers alive): 0.0..0.5: -26.2; 0.5..1.5: -8.9; 1.5..2.5: +18.8; 2.5..3.0: -0.0
- **attacker_healers** (of which healers): 0.0..0.5: +7.7; 0.5..1.5: -3.3; 1.5..2.5: +26.8; 2.5..3.0: -45.1
- **strength_gap** (attacking minus defending team strength): -815.0..-375.5: -8.2; -267.0..-117.5: +23.2; 1.0..86.5: +11.4; 106.0..122.5: +1.7; 226.0..285.5: -11.0; 332.5..401.5: -10.5; 498.5..611.0: -5.8

**lord kill** (45 matches, 6161 moments, 401 results): no better than the simple baseline yet (AUC 0.943 against 0.951 for attackers and defenders alone).
- **defenders_elsewhere** (own players alive outside the pit) falls from +45.3 to -48.4 points (0.0..0.5: +45.3; 0.5..1.5: +35.9; 1.5..2.5: +34.3; 2.5..3.5: +33.3; 3.5..4.5: +31.7; 4.5..5.5: -12.7; 5.5..6.5: -25.8; 6.5..7.5: -48.2; 7.5..8.0: -48.4)
- **defenders** (own players in the pit) falls from +46.3 to -46.6 points (0.0..0.5: +46.3; 0.5..1.5: +42.2; 1.5..2.5: +16.4; 2.5..3.5: -7.9; 3.5..4.5: -30.8; 4.5..5.5: -41.0; 5.5..6.5: -43.4; 6.5..7.5: -44.2; 7.5..8.0: -46.6)
- **attackers** (enemy players in the pit) rises from -42.1 to +40.1 points (1.0..1.5: -42.1; 1.5..2.5: -5.9; 2.5..3.5: -2.3; 3.5..4.5: +2.7; 4.5..5.5: +39.6; 5.5..6.5: +42.9; 6.5..7.5: +43.1; 7.5..8.0: +40.1)
- **minute** (match minute) rises from -40.8 to +24.6 points (0.6..2.85: -40.8; 4.05..5.15: -19.3; 6.15..7.25: -7.3; 8.75..10.35: +7.1; 11.85..13.75: +16.8; 15.45..17.95: +22.5; 19.95..22.85: +24.2)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -2.4 to +32.6 points (2.0..15.8: -2.4; 22.6..30.15: -36.9; 33.95..34.1: -16.2; 42.85..54.25: -0.7; 62.85..69.15: -17.3; 76.0..82.35: +32.7; 93.25..105.0: +18.3)
- **defender_healers** (of which healers) falls from +24.5 to -37.0 points (0.0..0.5: +24.5; 0.5..1.5: +12.2; 1.5..2.5: -5.8; 2.5..3.0: -37.0)
- **seconds_in_pit** (seconds the attackers have been in the pit) rises from -1.0 to +30.9 points (0.0..4.5: -1.0; 10.5..16.5: -15.7; 22.5..28.5: -13.7; 37.5..46.5: -8.7; 58.5..70.5: +4.8; 85.5..103.5: +7.0; 130.5..181.5: +30.5)
- **res_in** (seconds until the next res) rises from -41.3 to +8.8 points (1.0..8.5: -41.3; 17.5..26.5: +2.8; 35.5..44.5: +8.2; 53.5..62.5: +7.3; 71.5..77.5: +7.3; 83.5..89.5: +10.6; 98.5..110.5: +9.7)
- **strength_gap** (attacking minus defending team strength) falls from +7.2 to -9.7 points (-815.0..-375.5: +7.2; -267.0..-117.5: +9.4; 1.0..86.5: +15.3; 106.0..122.5: +14.5; 226.0..285.5: -2.9; 332.5..401.5: -5.9; 498.5..611.0: -32.9)

## 7. The usual play

Each choice against the most common one in that kind of decision, in win-chance points over the decision's window, adjusted for the situation, with a 90% range from resampling whole matches. CLEAR = the range excludes 0. Win chance comes from a model that never saw the match. The same comparison over the 30 s BEFORE the decision is a placebo test: a choice can't cause what came before it, so a clear difference there means the effect is partly who makes that choice.

**after wipe** (100 decisions, 43 matches; usual: pushed the pit)
- took the flag (n 14): -13.5 [-27.6, -0.9] CLEAR; in the 30 s before: -0.8 [-9.4, +7.1]
- reset (n 11): -7.0 [-16.3, +2.5]; in the 30 s before: -1.6 [-8.0, +3.9]

**boost clock** (185 decisions, 45 matches; usual: not running, fought)
- running, fought (n 29): -4.0 [-10.5, +1.1]; in the 30 s before: +1.7 [-4.3, +6.7]
- not running, fell back (n 26): -5.5 [-12.2, +3.9]; in the 30 s before: +2.9 [-3.3, +8.6]
- not running, advanced (n 23): -12.8 [-24.0, -3.9] CLEAR; in the 30 s before: +3.5 [-2.0, +12.4]
- running, advanced (n 22): -1.5 [-11.1, +7.1]; in the 30 s before: +2.3 [-4.4, +7.5]
- not running, held (n 9): -6.4 [-12.1, +3.4]; in the 30 s before: +5.4 [-7.1, +16.0]
- not running, to the spawn (n 8): +3.7 [-2.7, +14.3]; in the 30 s before: -1.0 [-9.3, +5.5]
- running, fell back (n 7): +6.2 [-8.0, +22.2]; in the 30 s before: -1.1 [-8.3, +10.2]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - running, fought, behind in the fight (lowest third, -0.10 or less): too few yet (n 7 against 29; means 0.9 against -6.1)
  - running, fought, middle third: -4.1 (n 10 against 19)
  - running, fought, ahead in the fight (top third, above -0.00): -3.5 (n 12 against 13)
  - not running, fell back, behind in the fight (lowest third, -0.10 or less): too few yet (n 8 against 29; means -5.0 against -6.1)
  - not running, fell back, middle third: -0.1 (n 12 against 19)
  - not running, fell back, ahead in the fight (top third, above -0.00): too few yet (n 6 against 13; means -12.2 against 4.1)
  - not running, advanced, behind in the fight (lowest third, -0.10 or less): too few yet (n 3 against 29; means -20.9 against -6.1)
  - not running, advanced, middle third: too few yet (n 5 against 19; means -3.9 against 0.5)
  - not running, advanced, ahead in the fight (top third, above -0.00): -16.0 (n 15 against 13)
  - running, advanced, behind in the fight (lowest third, -0.10 or less): too few yet (n 3 against 29; means -1.1 against -6.1)
  - running, advanced, middle third: too few yet (n 9 against 19; means -1.4 against 0.5)
  - running, advanced, ahead in the fight (top third, above -0.00): -4.0 (n 10 against 13)
  - not running, held, behind in the fight (lowest third, -0.10 or less): too few yet (n 4 against 29; means -4.5 against -6.1)
  - not running, held, middle third: too few yet (n 2 against 19; means -14.9 against 0.5)
  - not running, held, ahead in the fight (top third, above -0.00): too few yet (n 3 against 13; means -2.6 against 4.1)
  - not running, to the spawn, behind in the fight (lowest third, -0.10 or less): too few yet (n 7 against 29; means -2.2 against -6.1)
  - not running, to the spawn, middle third: too few yet (n 1 against 19; means 5.7 against 0.5)
  - running, fell back, behind in the fight (lowest third, -0.10 or less): too few yet (n 1 against 29; means -4.8 against -6.1)
  - running, fell back, middle third: too few yet (n 4 against 19; means -2.2 against 0.5)
  - running, fell back, ahead in the fight (top third, above -0.00): too few yet (n 2 against 13; means 30.9 against 4.1)

**enemy pickup** (671 decisions, 45 matches; usual: already running, fought)
- held, fought (n 109): -0.0 [-3.8, +4.1]; in the 30 s before: -0.3 [-3.8, +2.9]
- already running, advanced (n 76): -0.6 [-5.2, +3.2]; in the 30 s before: +3.8 [+0.2, +8.0] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, fell back (n 61): -0.5 [-6.0, +4.5]; in the 30 s before: -1.4 [-6.0, +3.2]
- held, advanced (n 55): +2.0 [-5.0, +8.0]; in the 30 s before: -1.8 [-5.2, +2.4]
- ran, fell back (n 55): -2.4 [-6.0, +1.4]; in the 30 s before: -4.1 [-7.6, -0.3] ALREADY DIFFERENT BEFORE: partly who chooses it
- ran, fought (n 52): -0.5 [-5.1, +5.7]; in the 30 s before: -4.8 [-10.7, -0.4] ALREADY DIFFERENT BEFORE: partly who chooses it
- already running, fell back (n 45): -0.2 [-3.7, +2.7]; in the 30 s before: -3.9 [-8.2, +0.0]
- ran, advanced (n 43): -1.5 [-8.3, +5.9]; in the 30 s before: +3.0 [-2.1, +7.0]
- already running, held (n 20): +1.0 [-4.6, +5.5]; in the 30 s before: -6.3 [-11.2, -1.1] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, held (n 14): +4.5 [-4.0, +14.9]; in the 30 s before: -6.4 [-16.1, +4.2]
- ran, held (n 10): +1.8 [-5.6, +8.2]; in the 30 s before: -5.6 [-10.9, -1.1] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, to the spawn (n 5): +7.3 [-0.3, +13.1]; in the 30 s before: -2.3 [-14.5, +11.9]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - held, fought, behind in the fight (lowest third, -0.01 or less): -3.0 (n 36 against 40)
  - held, fought, middle third: -6.7 (n 22 against 43)
  - held, fought, ahead in the fight (top third, above +0.01): +0.5 (n 51 against 43)
  - already running, advanced, behind in the fight (lowest third, -0.01 or less): +4.2 (n 17 against 40)
  - already running, advanced, middle third: -2.2 (n 33 against 43)
  - already running, advanced, ahead in the fight (top third, above +0.01): -3.6 (n 26 against 43)
  - held, fell back, behind in the fight (lowest third, -0.01 or less): -4.9 (n 24 against 40)
  - held, fell back, middle third: -11.3 (n 18 against 43)
  - held, fell back, ahead in the fight (top third, above +0.01): +5.4 (n 19 against 43)
  - held, advanced, behind in the fight (lowest third, -0.01 or less): too few yet (n 8 against 40; means 0.9 against 1.0)
  - held, advanced, middle third: -1.1 (n 13 against 43)
  - held, advanced, ahead in the fight (top third, above +0.01): +2.4 (n 34 against 43)
  - ran, fell back, behind in the fight (lowest third, -0.01 or less): -1.5 (n 25 against 40)
  - ran, fell back, middle third: -6.5 (n 22 against 43)
  - ran, fell back, ahead in the fight (top third, above +0.01): too few yet (n 8 against 43; means -1.1 against -2.9)
  - ran, fought, behind in the fight (lowest third, -0.01 or less): -3.3 (n 20 against 40)
  - ran, fought, middle third: -3.3 (n 14 against 43)
  - ran, fought, ahead in the fight (top third, above +0.01): +2.2 (n 18 against 43)
  - already running, fell back, behind in the fight (lowest third, -0.01 or less): -1.9 (n 25 against 40)
  - already running, fell back, middle third: -2.7 (n 14 against 43)
  - already running, fell back, ahead in the fight (top third, above +0.01): too few yet (n 6 against 43; means 4.8 against -2.9)
  - ran, advanced, behind in the fight (lowest third, -0.01 or less): -8.0 (n 12 against 40)
  - ran, advanced, middle third: +0.6 (n 20 against 43)
  - ran, advanced, ahead in the fight (top third, above +0.01): +0.0 (n 11 against 43)
  - already running, held, behind in the fight (lowest third, -0.01 or less): too few yet (n 7 against 40; means 2.6 against 1.0)
  - already running, held, middle third: too few yet (n 8 against 43; means 2.0 against 3.5)
  - already running, held, ahead in the fight (top third, above +0.01): too few yet (n 5 against 43; means -6.0 against -2.9)
  - held, held, behind in the fight (lowest third, -0.01 or less): too few yet (n 5 against 40; means -0.9 against 1.0)
  - held, held, middle third: too few yet (n 8 against 43; means 6.4 against 3.5)
  - held, held, ahead in the fight (top third, above +0.01): too few yet (n 1 against 43; means 3.7 against -2.9)
  - ran, held, behind in the fight (lowest third, -0.01 or less): too few yet (n 2 against 40; means 2.1 against 1.0)
  - ran, held, middle third: too few yet (n 8 against 43; means -1.7 against 3.5)
  - held, to the spawn, behind in the fight (lowest third, -0.01 or less): too few yet (n 3 against 40; means 5.3 against 1.0)
  - held, to the spawn, middle third: too few yet (n 1 against 43; means -3.4 against 3.5)
  - held, to the spawn, ahead in the fight (top third, above +0.01): too few yet (n 1 against 43; means 3.5 against -2.9)

- **late_game**: not enough decisions yet (15)
**power play** (501 decisions, 46 matches; usual: pushed, advanced)
- pushed, fought (n 137): +3.3 [+0.4, +5.9] CLEAR; in the 30 s before: -2.1 [-4.5, +0.4]
- held, fought (n 108): -0.9 [-2.5, +1.0]; in the 30 s before: -2.9 [-5.1, -0.3] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, fell back (n 44): -1.5 [-4.0, +0.8]; in the 30 s before: -5.2 [-12.1, -0.3] ALREADY DIFFERENT BEFORE: partly who chooses it
- pushed, fell back (n 17): +2.9 [-4.0, +9.8]; in the 30 s before: -5.2 [-9.0, -1.9] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, advanced (n 13): +2.7 [-1.2, +8.0]; in the 30 s before: -3.4 [-18.8, +5.7]
- pushed, held (n 6): -7.6 [-24.0, +10.2]; in the 30 s before: +9.1 [-9.7, +33.6]
- held, held (n 5): +3.4 [-0.1, +14.1]; in the 30 s before: -7.1 [-19.2, +1.4]
  By fight state (fightstate.py: enemy minus own expected deaths in the next 10 s; decisions split into thirds; raw win-chance change, against the usual choice in the same third):
  - pushed, fought, behind in the fight (lowest third, +0.00 or less): +8.0 (n 43 against 53)
  - pushed, fought, middle third: +0.5 (n 44 against 49)
  - pushed, fought, ahead in the fight (top third, above +0.05): +1.9 (n 50 against 69)
  - held, fought, behind in the fight (lowest third, +0.00 or less): +4.5 (n 44 against 53)
  - held, fought, middle third: -2.7 (n 35 against 49)
  - held, fought, ahead in the fight (top third, above +0.05): -6.0 (n 29 against 69)
  - held, fell back, behind in the fight (lowest third, +0.00 or less): +6.4 (n 16 against 53)
  - held, fell back, middle third: -5.9 (n 15 against 49)
  - held, fell back, ahead in the fight (top third, above +0.05): -3.3 (n 13 against 69)
  - pushed, fell back, behind in the fight (lowest third, +0.00 or less): too few yet (n 7 against 53; means -4.7 against -5.3)
  - pushed, fell back, middle third: too few yet (n 7 against 49; means 4.2 against 0.5)
  - pushed, fell back, ahead in the fight (top third, above +0.05): too few yet (n 3 against 69; means 10.7 against 5.2)
  - held, advanced, behind in the fight (lowest third, +0.00 or less): too few yet (n 5 against 53; means 0.9 against -5.3)
  - held, advanced, middle third: too few yet (n 6 against 49; means 6.9 against 0.5)
  - held, advanced, ahead in the fight (top third, above +0.05): too few yet (n 2 against 69; means 6.8 against 5.2)
  - pushed, held, behind in the fight (lowest third, +0.00 or less): too few yet (n 5 against 53; means -4.2 against -5.3)
  - pushed, held, middle third: too few yet (n 1 against 49; means 0.1 against 0.5)
  - held, held, behind in the fight (lowest third, +0.00 or less): too few yet (n 4 against 53; means 0.1 against -5.3)
  - held, held, middle third: too few yet (n 1 against 49; means 9.1 against 0.5)

**split in base** (107 decisions, 32 matches; usual: collapsed)
- defended without a collapse (n 45): +7.1 [-0.9, +16.6]; in the 30 s before: -2.3 [-6.1, +1.1]
- missed (n 11): +0.1 [-12.1, +9.6]; in the 30 s before: -9.1 [-15.7, +1.4]

**Collapses on a split: time away and its cost** (`S32`; per collapse, averages; main = what the main fight lost while the collapsers were away)

| Group | Cases | Away (median s) | Split killed | Collapser died | Own deaths at main | Enemy deaths at main | Flag lead change | DP change | Win change |
|---|---|---|---|---|---|---|---|---|---|
| all | 55 | 18 | 11 | 5 | 0.49 | 0.24 | +1.7 | -2.4 | -4.5 |
| away under 30 s | 34 | 9 | 9 | 0 | 0 | 0.12 | -0.6 | +0.7 | -4.3 |
| away 30 to 60 s | 11 | 42 | 0 | 1 | 0.18 | 0.09 | +11.6 | -2.7 | -4.0 |
| away 60 s or more | 10 | 125 | 2 | 4 | 2.5 | 0.8 | -1.1 | -12.7 | -5.6 |
| before 20:00 | 48 | 21.5 | 7 | 4 | 0.38 | 0.21 | +3.8 | -4.8 | -3.5 |
| from 20:00 | 7 | 18 | 4 | 1 | 1.29 | 0.43 | -12.3 | +14.3 | -11.4 |
| split member killed | 11 | 16 | 11 | 1 | 0.09 | 0.73 | +4.5 | +1.6 | -7.0 |
| no kill | 44 | 22 | 0 | 4 | 0.59 | 0.11 | +1.0 | -3.4 | -3.9 |

**Leverage: where the choice matters most** (share of the spread in win-chance change explained by the choice beyond the situation; range = best minus worst choice, in points)

- boost clock (185): choice explains 5.8% (situation 2.7%); range 18.9 points, best running, fell back, worst not running, advanced
- after wipe (100): choice explains 5.2% (situation 13.4%); range 13.5 points, best pushed the pit, worst took the flag
- split in base (107): choice explains 2.2% (situation 9.7%); range 7.1 points, best defended without a collapse, worst collapsed
- power play (501): choice explains 1.6% (situation 3.7%); range 8.6 points, best held, advanced, worst pushed, held
- enemy pickup (671): choice explains 0.6% (situation 5.6%); range 9.3 points, best held, to the spawn, worst ran, fell back

**Behaviour clusters: what teams actually did** (each decision's response grouped by what every player did in the next 20 s; UNNAMED = a group no single named choice covers: a response for Denning to name or reject)

*after wipe* (2 groups, separation 0.31):
- n 62: fought (midline, 1.7 of 8), fought (backline, 1.5 of 8), held (backline, 0.9 of 8), fought (frontline, 0.9 of 8); named as {'pushed the pit': 54, 'took the flag': 4, 'reset': 4}; win change 0.4
- n 38: advanced (backline, 3.1 of 8), advanced (midline, 2.2 of 8), advanced (frontline, 1.3 of 8); named as {'pushed the pit': 21, 'took the flag': 10, 'reset': 7}; win change 1.4 UNNAMED
*boost clock* (5 groups, separation 0.18):
- n 62: fought (midline, 2.2 of 8), fought (backline, 2.0 of 8), fought (frontline, 1.1 of 8); named as {'not running, fought': 42, 'running, fought': 20}; win change -3.5
- n 47: advanced (midline, 1.9 of 8), advanced (backline, 1.9 of 8), fought (midline, 0.6 of 8), advanced (frontline, 0.6 of 8); named as {'not running, advanced': 22, 'running, advanced': 19, 'running, fought': 2}; win change -5.9 UNNAMED
- n 34: held (backline, 2.1 of 8), fought (frontline, 1.1 of 8), fought (midline, 1.0 of 8), held (midline, 0.5 of 8); named as {'not running, fought': 14, 'running, fought': 7, 'not running, held': 7}; win change 0.9 UNNAMED
- n 30: fell back (backline, 2.4 of 8), fell back (midline, 1.9 of 8), fell back (frontline, 0.7 of 8), fought (midline, 0.7 of 8); named as {'not running, fell back': 21, 'running, fell back': 7, 'running, advanced': 1}; win change -1.6
- n 18: died (backline, 1.2 of 8), fought (midline, 1.2 of 8), to the spawn (backline, 1.0 of 8), to the spawn (frontline, 0.9 of 8); named as {'not running, to the spawn': 7, 'not running, fought': 3, 'not running': 2}; win change -1.1 UNNAMED
*enemy pickup* (3 groups, separation 0.2):
- n 283: fought (midline, 2.0 of 8), fought (backline, 1.5 of 8), fought (frontline, 1.0 of 8), held (backline, 0.9 of 8); named as {'already running, fought': 114, 'held, fought': 99, 'ran, fought': 44}; win change -1.2 UNNAMED
- n 205: fell back (backline, 1.7 of 8), fell back (midline, 1.6 of 8), held (backline, 0.6 of 8), fell back (frontline, 0.6 of 8); named as {'held, fell back': 58, 'ran, fell back': 53, 'already running, fell back': 43}; win change -1.1 UNNAMED
- n 185: advanced (backline, 2.1 of 8), advanced (midline, 1.9 of 8), advanced (frontline, 0.9 of 8); named as {'already running, advanced': 71, 'held, advanced': 50, 'ran, advanced': 40}; win change 0.1 UNNAMED
*power play* (3 groups, separation 0.26):
- n 260: fought (midline, 1.9 of 8), fought (backline, 1.8 of 8), fought (frontline, 1.1 of 8), held (backline, 0.8 of 8); named as {'pushed, fought': 127, 'held, fought': 102, 'pushed, advanced': 16}; win change 1.2 UNNAMED
- n 165: advanced (backline, 2.7 of 8), advanced (midline, 2.1 of 8), advanced (frontline, 1.1 of 8); named as {'pushed, advanced': 152, 'held, advanced': 9, 'pushed, fought': 3}; win change 1.4
- n 82: fell back (backline, 2.1 of 8), fell back (midline, 1.7 of 8), fought (midline, 0.6 of 8), fell back (frontline, 0.6 of 8); named as {'held, fell back': 42, 'pushed, fell back': 16, 'pushed, fought': 7}; win change -0.1 UNNAMED
*split in base* (3 groups, separation 0.19):
- n 50: fought (midline, 2.3 of 8), fought (backline, 1.3 of 8), fought (frontline, 0.9 of 8), held (backline, 0.8 of 8); named as {'defended without a collapse': 27, 'collapsed': 20, 'missed': 3}; win change -0.2 UNNAMED
- n 35: fell back (midline, 2.4 of 8), fell back (backline, 1.3 of 8), fell back (frontline, 0.9 of 8); named as {'collapsed': 20, 'defended without a collapse': 10, 'missed': 5}; win change -6.1 UNNAMED
- n 21: advanced (backline, 1.7 of 8), advanced (midline, 1.5 of 8), died (midline, 0.8 of 8), advanced (frontline, 0.7 of 8); named as {'collapsed': 11, 'defended without a collapse': 7, 'missed': 3}; win change 0.0 UNNAMED

## 8. What results and causes are worth

Win points for the team it happened to, from 46 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 155 | +0.8 | -9.3 to +10.4 | +1.6 | no |
| capture | 485 | +3.8 | +2.6 to +5.1 | +4.4 | yes |
| death (any) | 940 | -6.9 | -10.6 to -3.7 | -5.3 | yes |
| death: against a spike build | 238 | -7.2 | -11.6 to -0.1 | -3.3 | yes |
| death: against other builds | 702 | -6.8 | -11.5 to -2.8 | -5.9 | yes |
| death: back within 20 s | 152 | -3.5 | -9.0 to +1.7 | -2.8 | no |
| death: down 20 to 60 s | 343 | -9.0 | -13.4 to -4.3 | -5.0 | yes |
| death: down 60 s or more | 445 | -6.5 | -10.6 to -2.6 | -6.4 | yes |
| death: healer | 323 | -6.1 | -10.1 to -2.6 | -5.6 | yes |
| death: healer in own base or pit, back within 15 s (likely deliberate) | 22 | -1.4 | -14.3 to +10.7 | -2.5 | no |
| death: healer, other | 301 | -6.5 | -10.3 to -2.8 | -5.8 | yes |
| death: not a healer | 617 | -7.3 | -11.4 to -3.4 | -5.1 | yes |
| pit NPC lost (any): taken by a spike build | 67 | -1.4 | -7.4 to +8.1 | -2.4 | no |
| pit NPC lost (any): taken by other builds | 315 | -2.9 | -6.6 to +0.5 | -2.2 | no |
| pit NPC lost: archer | 217 | +0.5 | -2.4 to +3.6 | -0.8 | no |
| pit NPC lost: bodyguard | 57 | -2.2 | -6.9 to +2.4 | -0.5 | no |
| pit NPC lost: knight | 108 | -9.1 | -15.0 to -4.1 | -5.9 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value.

*deaths* (per 10 s in that state; result worth -6.9 points, base rate 1.3%):

- enemies within 1,500 7.5 to 8: result chance +2.4 points, worth -0.17 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +3.5 points, worth -0.24 win points
- current health % 1 to 47.5: result chance +9.9 points, worth -0.68 win points
- own minus enemy team strength 360 to 498.5: result chance -0.5 points, worth +0.04 win points
- maximum health after death penalty, as a share of normal 0.4 to 0.69: result chance +4.2 points, worth -0.29 win points
- own healers alive within cast range 3.5 to 4: result chance -0.5 points, worth +0.04 win points
- allies within 1,500 0 to 0.5: result chance +0.7 points, worth -0.05 win points

*kill conversion* (per burst, for the attacking team; result worth +6.9 points, base rate 30.5%):

- target's health ceiling 0.4 to 0.56: result chance +38.3 points, worth +2.64 win points
- damage in the 2 s burst 540 to 839: result chance +26.9 points, worth +1.85 win points
- target health % when the burst started 0 to 38.5: result chance +29.5 points, worth +2.04 win points
- target's healers in range 0 to 0.5: result chance +28.7 points, worth +1.98 win points
- a prot on the target 0.5 to 1: result chance -8.4 points, worth -0.58 win points
- match minute 0.3 to 1.45: result chance -7.9 points, worth -0.55 win points
- attackers in the burst 6.5 to 7: result chance -10.1 points, worth -0.7 win points

*npc loss* (per case, for the defending team; result worth -2.6 points, base rate 18.1%):

- own players in the pit 7.5 to 8: result chance -15.7 points, worth +0.41 win points
- damage on the pit NPCs in the last 5 s 369.5 to 1170: result chance +30.9 points, worth -0.81 win points
- own players alive outside the pit 0 to 0.5: result chance +18.3 points, worth -0.48 win points
- enemy players in the pit 7.5 to 8: result chance +18.1 points, worth -0.47 win points
- attackers' measured damage per second against a Lord (benchmarks) 15.8 to 22.2: result chance -5.7 points, worth +0.15 win points
- attacking minus defending team strength -415.5 to -316.5: result chance -6.7 points, worth +0.18 win points
- own pit archers alive 2.5 to 3: result chance +35.2 points, worth -0.92 win points

## 9. Detailed learnings snapshot

Descriptive measurements across all 46 trained matches (the latest batch, 6 matches, in brackets where it differs). Not causal on their own: they point to questions and candidate variables.

**Runners** (spawn to capture; pushed = an enemy hit the carrier):

| Runner | Runs | Captured | Median s to capture | Dropped | Pushed | Runs by winners |
|---|---|---|---|---|---|---|
| Mes/A | 145 | 52% | 42.5 (43.0) | 66 | 52% | 43% |
| AoB Derv | 105 | 58% | 30 (29) | 43 | 43% | 56% |
| Ritualist | 71 | 52% | 34 (36) | 32 | 37% | 66% |
| Mesmer | 68 | 50% | 31.0 (27.5) | 33 | 34% | 47% |
| Hammer | 49 | 47% | 27 (34) | 25 | 29% | 49% |
| 8 Monk | 46 | 28% | 33 (25) | 32 | 22% | 41% |
| Stand Mes | 45 | 67% | 30.5 | 14 | 33% | 51% |
| Dervish | 42 | 60% | 26 (36) | 16 | 48% | 62% |
| Necromancer | 33 | 61% | 24.0 (24) | 12 | 39% | 9% |
| Monk 4 (WoC) | 31 | 68% | 44 | 10 | 65% | 74% |

Double running: half 221 runs (53% by winners); single 690 runs (48% by winners).

**Flag answers** (answering the enemy's capture): winners: 225 answers, median 38 s, 2 s slower than possible, 33 answers 30 s+ slower; losers: 214 answers, median 53.0 s, 8.0 s slower than possible, 70 answers 30 s+ slower.

**Skills: kill participation** (share of casts at an enemy who died within 5 s; 15+ casts):

- Highest: Augury of Death 36% of 64; Word of Censure 32% of 1107; Decapitate 31% of 72; Horns of the Ox 30% of 20; Shatter Storm 27% of 136; Body Blow 26% of 38; Invoke Lightning 24% of 319; Chest Thumper 24% of 142; Castigation Signet 23% of 411; Disrupting Throw 21% of 66; Agonizing Chop 20% of 83; Vapor Blade 20% of 45
- Lowest: Winter's Embrace 0% of 16; Soul Bind 0% of 92; Parasitic Bond 0% of 108; Reckless Haste 0% of 40; Spiteful Spirit 0% of 55; Images of Remorse 0% of 20; Diversion 0% of 17; Flare 0% of 41

**Interrupts:** skills interrupted most (whose): Healing Burst on the 7 Monk 167; Guardian on the Prot 121; Guardian on the 8 Monk 117; Blessed Light on the 8 Monk 80; Spirit Light Weapon on the Ritualist 77; Shield Guardian PvP on the Prot 71; Guardian on the 7 Monk 69; Cure Hex on the 7 Monk 68; Word of Censure on the Monk 4 (WoC) 62; Rapid Fire on the Ranger 52. Interrupt skills landing most: Power Spike 724; Complicate 704; Power Leak 336; Psychic Instability PvP 257; Savage Shot 200; Cry of Frustration 178; Hammer Bash 161; Distracting Shot 75.

**Knockdowns by skill:** Coward 1214; Hammer Bash 1040; Psychic Instability PvP 297; Lightning Surge 253; Mind Shock PvP 132; "Coward!" 109; Bull's Strike 67; Shock 56.

**Spikes survived** (400+ damage in 3 s on one player; survived = alive 8 s later): winners 100 of 131 (76%); losers 179 of 303 (59%). By target: Stand Mes 71% of 49; 7 Monk 70% of 47; Prot 62% of 47; AoB Derv 62% of 42; 8 Monk 45% of 40; Mes/A 88% of 32; Necromancer 60% of 25; Hammer 58% of 24; Mesmer 53% of 19; Air Ele 71% of 17; Ritualist 65% of 17; Ranger 64% of 14; Paragon 62% of 13; Water Ele 73% of 11.

**Monks** (per 2-minute phase alive 60 s+): winners: 11.5 casts a minute, 0.42 fakes, idle 0 s while an ally was hurt, reaction 1.6 s, bursts answered 68%; losers: 11.5 casts a minute, 0.54 fakes, idle 0.0 s while an ally was hurt, reaction 1.3 s, bursts answered 62%.

**Deaths** (824): 291 with a knockdown on the victim; 252 had a monk cast on the victim in the last 5 s. Monk skills interrupted in the 6 s before a death: Blessed Light 35; Guardian 29; Healing Burst 27; Reversal of Fortune 19; Shield Guardian PvP 14; Signet of Rejuvenation 9; Cure Hex 9; Dismiss Condition 8.

## 10. For Denning

- Which curves look wrong to you? A correction (direction, cap, drop, or a pair to always test) is logged with your reason and tested on held-out matches.
- Do any surprises remind you of something the variables don't capture (a missing variable)?
- Any variable you think matters that isn't listed?

