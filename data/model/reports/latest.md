# Learning report, batch 1

Trained on 30 matches (6 new in this batch). Variables in use: 20; build variables from 60 matches, interactions from 40.

## 0. Data integrity

- Lengths repaired: 2 (1f65fd3b 150 s -> 1027 s) (bbef1904 617 s -> 599 s) 
- Matches with a team's Lord damage not observed (left blank, not zero): 2
- Pit NPCs added from the standard roster (never seen in the replay): 91 in 24 matches
- Left out of training: 0

## 1. The honest test

**Not yet better than strength alone: treat the curves as noise.** Held-out accuracy (matches held out whole), log loss in brackets (lower is better):

- strength only: all 62% (0.562), 0-5 min 73% (0.47), 5-10 min 66% (0.555), 10-15 min 57% (0.64), 15-end min 50% (0.622), matches lasting 15 min+ 54% (0.663), matches even on strength (gap under 200) 44% (0.699)
- glass box: all 72% (0.657), 0-5 min 74% (0.508), 5-10 min 75% (0.582), 10-15 min 67% (0.768), 15-end min 69% (0.828), matches lasting 15 min+ 65% (0.79), matches even on strength (gap under 200) 64% (0.908)
- black box: all 65% (1.289), 0-5 min 63% (1.363), 5-10 min 64% (1.308), 10-15 min 67% (1.323), 15-end min 68% (1.154), matches lasting 15 min+ 62% (1.406), matches even on strength (gap under 200) 68% (1.196)
- Gain over strength alone (log loss, resampling whole matches): -0.095 (90% range -0.369 to +0.154).
- Change since batch 0: glass box log loss 0.692 -> 0.657; strength only 0.442 -> 0.562.

## 2. What it leans on

- **morale_diff** 1.146 (was 0.808): own minus enemy morale summed over players (boosts +, death penalty -)
- **stand** 0.309 (was 0.196): who holds the flag stand: 1 own, 0 nobody, -1 enemy
- **spike_killable_diff** 0.301 (was 0.08): enemy minus own players within one spike of the other side (DP stacking; 0 unless a spike build is involved)
- **flag_lead** 0.281 (was 0.29): seconds up (+) or down (-) on flags: enemy's response minus own on the next capture exchange
- **main_diff** 0.28 (was 0.239): own minus enemy players in each team's main group
- **lord_damage_diff** 0.234 (was 0.204): own minus enemy Lord damage dealt so far (the 28:00 tiebreak; players can't see it); blank when either team's Lord damage wasn't observed
- **boost_clock** 0.172 (was 0.122): seconds until the stand holder's next boost (+ if own boost is coming, - if the enemy's, 0 nobody)
- **pit_pressure_diff** 0.168 (was 0.189): own players in the enemy pit minus enemy players in the own pit
- **down_diff_s** 0.163 (was 0.125): enemy minus own seconds until all dead players are back (+ = the enemy has more time down)
- **archers_diff** 0.154 (was 0.188): own minus enemy pit archers alive
- **fight_state** 0.146 (was 0.019): who is winning the fight now: enemy minus own expected deaths in the next 10 s, from a deaths model that never saw the match (fightstate.py)
- **carrying_diff** 0.117 (was 0.109): own minus enemy players carrying a flag

## 3. The curves in words

Points = win-chance points added to an otherwise even game at each range of the variable.

- **morale_diff** rises from -44.1 to +42.2 points (-470.0..-199.0: -44.1; -154.0..-109.5: -34.1; -83.5..-46.5: -24.2; -15.5..-1.0: -1.8; 1.0..18.5: +2.8; 46.5..94.5: +28.5; 139.5..184.0: +41.6)
- **stand** rises from -8.1 to +8.1 points (-1.0..-0.5: -8.1; -0.5..0.5: +0.5; 0.5..1.0: +8.1)
- **spike_killable_diff** rises from -29.1 to +29.6 points (-8.0..-7.5: -29.1; -5.5..-3.5: -31.1; -2.5..-1.5: -26.3; -0.5..0.5: +0.2; 1.5..2.5: +25.2; 4.5..7.5: +28.3)
- **flag_lead** falls from +21.3 to -20.4 points (-86.0..-70.5: +21.3; -55.5..-42.5: -1.7; -29.5..-19.5: -2.4; -9.5..-0.5: -1.5; 8.5..19.5: +2.6; 30.5..43.5: +2.3; 55.5..70.5: -14.3)
- **main_diff** rises from -17.5 to +21.3 points (-8.0..-4.5: -17.5; -3.5..-2.5: -10.4; -1.5..-0.5: -7.0; 0.5..1.5: +7.6; 2.5..3.5: +10.6; 4.5..8.0: +21.3)
- **lord_damage_diff** falls from +48.8 to -49.0 points (-9661.0..-5002.0: +48.8; -3309.5..-1698.5: +1.8; -1213.5..-491.0: -0.2; -102.0..-8.5: -1.5; 8.5..102.0: -0.4; 610.0..1323.5: -2.7; 2691.0..4893.5: -33.4)
- **boost_clock** rises from -5.1 to +5.2 points (-120.0..-109.5: -5.1; -98.5..-85.5: -5.1; -71.5..-54.5: -4.5; -32.5..-0.5: -2.8; 9.5..42.5: +4.0; 64.5..81.5: +4.8; 95.5..108.5: +5.1)
- **pit_pressure_diff** falls from -3.4 to -8.6 points (-8.0..-5.5: -3.4; -4.5..-3.5: +15.1; -2.5..-1.5: +11.5; -0.5..0.5: +0.6; 1.5..2.5: -13.1; 3.5..5.5: -11.0)
- **down_diff_s** rises from -35.9 to +39.6 points (-960.0..-195.0: -35.9; -127.5..-97.5: -13.2; -67.5..-52.5: -9.1; -37.5..-7.5: -4.1; 7.5..37.5: +3.4; 67.5..97.5: +8.8; 127.5..195.0: +19.8)
- **archers_diff** falls from +4.4 to -4.0 points (-3.0..-2.5: +4.4; -2.5..-1.5: +9.5; -1.5..-0.5: +8.8; -0.5..0.5: +0.1; 0.5..1.5: -9.3; 1.5..2.5: -9.6; 2.5..3.0: -4.0)

## 4. Discovery

**Interaction candidates** (a screen: pairs whose combination seems to matter beyond each alone; untested until held-out matches confirm them; switched on in the model from 40 matches):

- morale_diff with spike_killable_diff (screen 0.176)
- alive_diff with morale_diff (screen 0.168)
- down_diff_s with morale_diff (screen 0.168)
- morale_diff with lord_exposed_diff (screen 0.167)
- morale_diff with lord_damage_diff (screen 0.163)
- morale_diff with bodyguard_diff (screen 0.162)
- main_diff with morale_diff (screen 0.160)
- morale_diff with knights_diff (screen 0.151)

**Candidate variables** (proposed variables, tested on unseen matches; log loss, lower is better):

- split_diff: 0.657 without, 0.67 with: does not improve yet. own minus enemy players on a split (away from their main group on the enemy half, not carrying). Proposed batch 1 by Claude: the knights curve runs backwards, maybe standing in for the cost of splitting

**Surprises** (moments where the held-out model was most confident about the team that went on to lose; each points to something the variables don't capture yet):

- RACK v hdm (1f65fd3b) at 10:00: a model that never saw this match gave RACK 2.7%, and RACK won. Why it thought so: morale_diff -41.7, team strength -14.0, stand -10.0, knights_diff -9.4, flag_lead +4.0
- hdm v HC (28447c4a) at 25:00: a model that never saw this match gave HC 0.0%, and HC won. Why it thought so: morale_diff -48.6, lord_damage_diff -33.6, bodyguard_diff -33.4, knights_diff -24.2, lord_exposed_diff -18.8
- OG v hold (49eec28d) at 4:30: a model that never saw this match gave OG 8.8%, and OG won. Why it thought so: morale_diff -40.6, lord_health_diff -32.7, team strength +19.0, pit_pressure_diff +13.9, archers_diff +10.2
- hdm v Men (0f1fd794) at 28:00: a model that never saw this match gave Men 0.3%, and Men won. Why it thought so: lord_damage_diff -49.7, bodyguard_diff -24.4, morale_diff +22.6, pit_pressure_diff -14.4, lord_health_diff +12.3
- Team v push (2df9b7fd) at 15:15: a model that never saw this match gave Team 1.7%, and Team won. Why it thought so: team strength +48.1, spike_killable_diff -47.5, main_diff -34.0, archers_diff -22.4, carrying_diff +11.3
- Men v HC (faec428a) at 15:45: a model that never saw this match gave HC 92.2%, and HC lost. Why it thought so: main_diff +27.5, morale_diff +20.5, alive_diff +18.5, team strength -14.9, lord_exposed_diff +14.0

## 5. Denning's rulings seen through the model

Win chance from a model that never saw the match, 20 s before and 60 s after each ruled moment. Contributions are points for an otherwise even game (the curves' scale).

- hdm v HC (28447c4a) 5:01 (split answered), HC: 29.4% 20 s before -> 61.4% 60 s after (+32.0). After: knights_diff -24.2, team strength -16.4, flag_lead -15.0, pit_pressure_diff +12.9
- hdm v HC (28447c4a) 5:01 (split answered), hdm: 71.8% 20 s before -> 45.7% 60 s after (-26.1). After: knights_diff +25.1, team strength +16.4, flag_lead +15.1, pit_pressure_diff -14.0
- hdm v HC (28447c4a) 1:02 (split detection), HC: 37.2% 20 s before -> 32.4% 60 s after (-4.8). After: team strength -16.4, flag_lead +15.1, carrying_diff -11.8, stand -9.4
- hdm v HC (28447c4a) 1:02 (split detection), hdm: 65.5% 20 s before -> 68.2% 60 s after (+2.7). After: team strength +16.4, flag_lead -15.0, carrying_diff +11.3, stand +9.4
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), HC: 8.8% 20 s before -> 6.7% 60 s after (-2.1). After: bodyguard_diff -33.4, knights_diff -24.2, lord_exposed_diff -18.8, team strength -16.4
- hdm v HC (28447c4a) 7:10 (8 monk in base after the pit died), hdm: 93.9% 20 s before -> 95.4% 60 s after (+1.5). After: bodyguard_diff +31.6, knights_diff +25.1, team strength +16.4, lord_exposed_diff +14.5
- hdm v HC (bbef1904) 8:10 (death), HC: 40.3% 20 s before -> 6.7% 60 s after (-33.6). After: morale_diff -20.9, down_diff_s -17.9, team strength -16.0, fight_state +14.0
- hdm v HC (bbef1904) 8:10 (death), hdm: 60.0% 20 s before -> 92.4% 60 s after (+32.4). After: down_diff_s +17.0, team strength +16.0, morale_diff +15.4, alive_diff +12.5
- Men v HC (faec428a) 9:31 (death), HC: 24.8% 20 s before -> 25.9% 60 s after (+1.1). After: team strength -14.9, stand -7.5, boost_clock -4.5, knights_diff +3.5
- Men v HC (faec428a) 9:31 (death), Men: 73.8% 20 s before -> 76.3% 60 s after (+2.5). After: team strength +14.9, stand +7.5, morale_diff +4.7, boost_clock +4.6

## 6. Why: the node models

Each explains one result from what happened before it (time order enforced), tested on matches it never saw. AUC = how often a moment that led to the result scores above one that didn't (0.5 = guessing, 1 = perfect).

**deaths** (30 matches, 71914 moments, 1832 results): adds to the simple baseline (AUC 0.904 against 0.77 for health_pct and damage_taken_3s alone).
- **enemies_near** (enemies within 1,500) rises from -17.2 to +25.5 points (0.0..0.5: -17.2; 0.5..1.5: -8.1; 1.5..2.5: -0.7; 2.5..3.5: +0.8; 3.5..4.5: +5.7; 4.5..5.5: +7.7; 5.5..6.5: +12.8; 6.5..7.5: +14.7; 7.5..8.0: +25.5)
- **strength_gap** (own minus enemy team strength) falls from +11.5 to -14.1 points (-721.0..-426.0: +11.5; -316.5..-210.5: +10.7; -116.0..-102.5: -5.1; -17.5..17.5: +10.2; 86.5..111.0: -12.4; 128.5..267.5: -13.6; 316.5..426.0: -13.8)
- **health_pct** (current health %) falls from +41.0 to -6.0 points (1.0..48.5: +41.0; 60.5..68.5: +22.9; 74.5..78.5: +10.7; 82.5..85.5: +6.0; 88.5..91.5: +2.2; 93.5..95.5: -2.1; 97.5..99.5: -4.8)
- **local_diff** (allies minus enemies within 2,000) falls from +31.4 to -14.1 points (-8.0..-3.5: +31.4; -2.5..-1.5: +10.5; -0.5..0.5: -5.7; 1.5..2.5: -7.1; 3.5..4.5: +15.3; 5.5..7.0: -14.1)
- **health_ceiling** (maximum health after death penalty, as a share of normal) falls from +33.3 to -9.9 points (0.4..0.64: +33.3; 0.71..0.84: +20.9; 0.85..0.9: +15.3; 0.94..0.99: +9.4; 1.0..1.1: -2.9)
- **healers_in_range** (own healers alive within cast range) falls from +10.8 to +1.4 points (0.0..0.5: +10.8; 0.5..1.5: -3.7; 1.5..2.5: -6.1; 2.5..3.0: +1.4)
- **dist_own_pit** (distance from its own pit) rises from +6.1 to +15.7 points (10.0..1641.5: +6.1; 2786.5..4550.0: -6.6; 5521.5..6316.5: -8.1; 7114.5..7799.5: -2.1; 8370.5..8901.5: -3.0; 9655.5..10514.5: +0.8; 11628.5..13000.5: +10.7)
- **minute** (match minute) rises from -4.1 to +16.6 points (0.1..1.25: -4.1; 2.35..3.45: -4.8; 4.65..5.75: +4.4; 7.15..8.75: +4.8; 10.35..12.05: -5.1; 13.85..15.95: -0.9; 18.45..21.55: +6.6)

**kill conversion** (30 matches, 556 moments, 167 results): adds to the simple baseline (AUC 0.775 against 0.648 for burst_damage and target_health_pct alone).
- **target_ceiling** (target's health ceiling) falls from +26.7 to -17.8 points (0.4..0.56: +26.7; 0.68..0.71: +19.8; 0.83..0.86: +15.2; 0.91..0.92: +8.3; 0.94..0.95: +4.7; 0.98..1.02: -2.8; 1.08..1.1: -17.8)
- **burst_damage** (damage in the 2 s burst) rises from -5.4 to +18.5 points (250.0..257.5: -5.4; 267.5..280.5: -9.5; 290.5..302.5: -6.6; 319.5..336.5: -4.5; 357.5..377.0: -2.5; 409.0..440.0: +1.6; 476.0..547.5: +17.7)
- **target_health_pct** (target health % when the burst started) falls from +22.9 to -5.5 points (0.0..40.5: +22.9; 52.5..56.5: +11.9; 62.5..68.5: +4.9; 72.5..76.5: +2.7; 79.5..83.5: -4.3; 87.5..91.5: -8.7; 96.5..99.5: -9.0)
- **target_healers_in_range** (target's healers in range) falls from +21.1 to -3.9 points (0.0..0.5: +21.1; 0.5..1.5: +1.5; 1.5..2.5: -7.2; 2.5..3.0: -3.9)
- **target_prot_up** (a prot on the target) falls from +4.5 to -10.1 points (0.0..0.5: +4.5; 0.5..1.0: -10.1)
- **minute** (match minute) rises from -13.6 to +8.3 points (0.3..1.45: -13.6; 2.75..3.95: -0.1; 5.05..6.35: -2.6; 7.35..8.45: -1.5; 10.35..12.65: +2.4; 14.45..16.35: +6.5; 18.75..22.0: +8.5)
- **strength_gap** (attacking minus target team strength) rises from -4.2 to +10.7 points (-721.0..-316.5: -4.2; -193.5..-117.5: -2.2; -102.5..-10.0: -0.1; 0.0..86.5: +4.4; 116.0..140.5: -3.4; 252.5..267.5: -6.0; 332.5..511.5: +2.7)
- **target_knocked_down** (target knocked down) falls from +1.8 to -12.4 points (0.0..0.5: +1.8; 0.5..1.0: -12.4)

**flag answer** (seconds an answer to an enemy capture was slower than possible; 27 matches, 306 rows): adds to the simple baseline (typical error 16.7s against 26.1s for the median; explains 67% of the spread).
- **parked_s** (seconds the flag lay parked (dropped 5 s or more: not running yet)): 0.0..3.5: -4.7 s; 10.5..14.0: +4.9 s; 18.0..27.5: +16.6 s; 32.0..41.0: +28.7 s; 48.5..62.5: +43.3 s; 83.0..99.0: +50.9 s; 117.5..259.0: +55.9 s
- **enemies_in_the_way** (enemy presence along the runner's trip back to the spawn): 0.0..0.5: -6.5 s; 4.5..9.5: -4.2 s; 15.5..20.5: -2.0 s; 25.0..37.5: -0.0 s; 50.5..57.0: +3.8 s; 71.5..101.0: +8.8 s; 120.5..171.5: +16.3 s
- **own_deaths_during** (own deaths during the answer): 0.0..0.5: -3.8 s; 0.5..1.5: +5.0 s; 1.5..2.5: +12.0 s; 2.5..4.5: +26.6 s; 4.5..5.5: +46.9 s; 5.5..6.5: +61.4 s; 6.5..8.0: +76.2 s; 8.0..11.0: +87.6 s
- **enemy_deaths_during** (enemy deaths during the answer): 0.0..0.5: -2.1 s; 0.5..1.5: +8.0 s; 1.5..2.5: +11.7 s; 2.5..3.5: +14.1 s; 3.5..5.0: +21.4 s
- **carrier_damage_taken** (damage the carrier took while carrying): 0.0..2.0: -2.8 s; 26.5..49.0: -3.1 s; 66.0..96.5: -1.7 s; 125.5..177.5: +0.4 s; 244.0..277.5: +2.5 s; 378.0..491.5: +4.7 s; 573.5..944.0: +6.7 s
- **forced_drops** (drops with the carrier hit in the 5 s before, or dying): 0.0..0.5: -1.7 s; 0.5..1.5: +16.5 s; 1.5..2.0: +27.1 s
- **quick_handoffs** (quick hand-offs (a teammate picked it up within 5 s)): 0.0..0.5: -1.9 s; 0.5..1.5: +4.5 s; 1.5..2.5: +10.3 s; 2.5..3.0: +22.3 s
- **possible_s** (fastest possible answer (s) from the flag model at the enemy's capture): 0.0..3.5: -0.4 s; 7.5..13.5: +1.0 s; 22.5..28.5: +1.9 s; 33.5..36.5: +2.7 s; 41.5..45.5: +1.6 s; 50.5..55.5: -0.2 s; 63.5..74.5: -5.5 s
- **flag_lead_at_enemy_cap** (own flag lead when the enemy captured): -81.0..-74.5: -6.7 s; -62.5..-54.5: -0.7 s; -42.5..-35.5: +1.6 s; -27.5..-18.5: +1.5 s; -10.5..-3.5: +1.9 s; 10.5..19.5: +1.0 s; 35.5..56.5: -0.1 s
- **runner_to_spawn** (runner's distance to its flag spawn when the enemy captured): 94.0..976.0: -4.5 s; 1503.0..2101.5: -2.1 s; 3384.5..4354.5: -0.1 s; 4871.0..5542.0: +2.0 s; 6234.5..6701.0: +2.0 s; 7263.5..7825.0: +0.9 s; 8439.0..9139.5: +1.2 s

**npc loss** (30 matches, 3381 moments, 593 results): no better than the simple baseline yet (AUC 0.776 against 0.755 for attackers and defenders alone).
- **defenders** (own players in the pit) falls from +35.5 to -41.7 points (0.0..0.5: +35.5; 0.5..1.5: +23.6; 1.5..2.5: +19.2; 2.5..3.5: -1.2; 3.5..4.5: -16.6; 4.5..5.5: -17.8; 5.5..6.5: -18.7; 6.5..7.5: -39.0; 7.5..8.0: -41.7)
- **npc_damage_5s** (damage on the pit NPCs in the last 5 s) rises from -13.7 to +29.6 points (0.0..0.5: -13.7; 22.5..36.5: -0.6; 50.5..66.5: +2.4; 84.5..105.5: +7.8; 127.5..151.5: +22.3; 179.5..217.5: +24.9; 270.5..363.5: +28.0)
- **attackers** (enemy players in the pit) rises from -15.7 to +26.3 points (1.0..1.5: -15.7; 1.5..2.5: -7.5; 2.5..3.5: -5.8; 3.5..4.5: +6.4; 4.5..5.5: +16.9; 5.5..6.5: +20.6; 6.5..7.5: +21.8; 7.5..8.0: +26.3)
- **defenders_elsewhere** (own players alive outside the pit) falls from +25.7 to +0.3 points (0.0..0.5: +25.7; 0.5..1.5: +12.5; 1.5..2.5: +13.9; 2.5..3.5: +3.3; 3.5..4.5: -3.6; 4.5..5.5: -5.5; 5.5..6.5: -15.9; 6.5..7.5: -15.1; 7.5..8.0: +0.3)
- **strength_gap** (attacking minus defending team strength) rises from -19.4 to +10.4 points (-682.0..-377.0: -19.4; -287.5..-157.5: -6.2; -106.0..-17.5: -2.3; 57.5..102.5: -3.7; 106.0..128.5: +16.5; 252.5..302.5: +7.4; 363.0..511.5: +9.1)
- **defender_healers** (of which healers) falls from +12.1 to +6.1 points (0.0..0.5: +12.1; 0.5..1.5: -4.8; 1.5..2.5: -5.2; 2.5..3.0: +6.1)
- **archers** (own pit archers alive) rises from -0.8 to +21.1 points (0.0..0.5: -0.8; 0.5..1.5: -6.9; 1.5..2.5: +4.1; 2.5..3.0: +21.1)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -9.3 to +12.5 points (2.4..20.1: -9.3; 24.35..33.05: -7.3; 36.4..36.55: -2.1; 43.35..55.55: -1.2; 64.1..66.8: +2.6; 74.65..79.45: +5.1; 87.75..101.65: +5.0)

**lord damage** (Lord damage dealt in the next 10 s while players are in the enemy pit; 29 matches, 3988 rows): adds to the simple baseline (typical error 121.2 against 86.1 for the median; explains 35% of the spread).
- **bodyguard** (own Bodyguard alive): 0.0..0.5: +149.5; 0.5..1.0: -52.2
- **defenders** (own players in the pit): 0.0..0.5: +173.4; 0.5..1.5: +82.2; 1.5..2.5: +15.1; 2.5..3.5: -35.5; 3.5..4.5: -64.6; 4.5..5.5: -106.1; 5.5..6.5: -112.7; 6.5..7.5: -125.9; 7.5..8.0: -96.2
- **defenders_elsewhere** (own players alive outside the pit): 0.0..0.5: +66.3; 0.5..1.5: +80.2; 1.5..2.5: +87.0; 2.5..3.5: +92.0; 3.5..4.5: +56.7; 4.5..5.5: +11.0; 5.5..6.5: -39.5; 6.5..7.5: -100.6; 7.5..8.0: -188.1
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)): 2.4..17.6: -57.2; 24.1..33.05: -40.3; 36.4..36.55: -49.8; 42.75..54.85: -12.2; 64.1..66.65: +5.8; 73.45..79.45: +25.9; 86.6..100.6: +88.6
- **defender_healers** (of which healers): 0.0..0.5: +78.9; 0.5..1.5: +2.4; 1.5..2.5: -28.4; 2.5..3.0: -67.1
- **attackers** (enemy players in the pit): 1.0..1.5: -33.2; 1.5..2.5: -17.6; 2.5..3.5: -26.4; 3.5..4.5: -9.5; 4.5..5.5: +81.1; 5.5..6.5: +71.0; 6.5..7.5: +25.1; 7.5..8.0: +68.7
- **seconds_in_pit** (seconds the attackers have been in the pit): 0.0..4.5: -23.5; 10.5..16.5: -23.2; 22.5..28.5: -26.0; 34.5..43.5: -12.4; 52.5..64.5: +19.5; 79.5..94.5: +31.4; 115.5..145.5: +53.2
- **archers** (own pit archers alive): 0.0..0.5: -53.4; 0.5..1.5: -0.9; 1.5..2.5: +26.2; 2.5..3.0: +12.1
- **attackers_area_damage** (area-damage skills on the attackers' bars (Denning P9)): 0.0..0.5: +17.2; 0.5..1.0: -47.4
- **strength_gap** (attacking minus defending team strength): -682.0..-332.5: +10.4; -287.5..-128.5: +26.2; -31.0..57.5: +31.7; 102.5..106.0: -1.1; 128.5..285.5: -17.4; 332.5..403.0: -22.9; 511.5..648.0: -6.9

**lord kill** (29 matches, 3984 moments, 256 results): no better than the simple baseline yet (AUC 0.952 against 0.96 for attackers and defenders alone).
- **defenders** (own players in the pit) falls from +47.8 to -49.9 points (0.0..0.5: +47.8; 0.5..1.5: +45.4; 1.5..2.5: +22.7; 2.5..3.5: +0.1; 3.5..4.5: -38.5; 4.5..5.5: -45.1; 5.5..6.5: -48.8; 6.5..7.5: -48.9; 7.5..8.0: -49.9)
- **attackers** (enemy players in the pit) rises from -43.8 to +47.7 points (1.0..1.5: -43.8; 1.5..2.5: -23.0; 2.5..3.5: -18.4; 3.5..4.5: +18.4; 4.5..5.5: +47.3; 5.5..6.5: +48.2; 6.5..7.5: +47.8; 7.5..8.0: +47.7)
- **defenders_elsewhere** (own players alive outside the pit) falls from +47.0 to -48.9 points (0.0..0.5: +47.0; 0.5..1.5: +42.3; 1.5..2.5: +32.1; 2.5..3.5: +31.4; 3.5..4.5: +30.2; 4.5..5.5: +7.5; 5.5..6.5: -3.1; 6.5..7.5: -48.7; 7.5..8.0: -48.9)
- **minute** (match minute) rises from -44.4 to +28.6 points (0.6..2.65: -44.4; 3.95..5.05: -26.4; 6.05..7.15: +17.1; 8.75..10.45: +17.7; 12.05..14.05: +3.5; 15.85..18.65: +20.6; 20.95..24.45: +26.0)
- **attackers_lord_dps** (attackers' measured damage per second against a Lord (benchmarks)) rises from -23.2 to +42.6 points (2.4..17.6: -23.2; 24.1..33.05: -29.1; 36.4..36.55: -26.7; 42.75..54.85: +11.7; 64.1..66.65: -1.6; 73.45..79.45: +21.9; 87.15..101.15: +17.5)
- **seconds_in_pit** (seconds the attackers have been in the pit) rises from +4.6 to +42.5 points (0.0..4.5: +4.6; 10.5..16.5: -14.3; 22.5..28.5: -29.2; 37.5..46.5: -27.0; 55.5..67.5: +12.1; 79.5..94.5: +13.8; 115.5..145.5: +34.4)
- **defender_healers** (of which healers) falls from +23.7 to -30.8 points (0.0..0.5: +23.7; 0.5..1.5: +12.3; 1.5..2.5: -14.8; 2.5..3.0: -30.8)
- **attacker_healers** (of which healers) falls from +14.9 to -2.1 points (0.0..0.5: +14.9; 0.5..1.5: -19.6; 1.5..2.5: -10.4; 2.5..3.0: -2.1)

## 7. The usual play

Each choice against the most common one in that kind of decision, in win-chance points over the decision's window, adjusted for the situation, with a 90% range from resampling whole matches. CLEAR = the range excludes 0. Win chance comes from a model that never saw the match. The same comparison over the 30 s BEFORE the decision is a placebo test: a choice can't cause what came before it, so a clear difference there means the effect is partly who makes that choice.

**after wipe** (65 decisions, 27 matches; usual: pushed the pit)
- took the flag (n 12): -6.3 [-20.2, +9.4]; in the 30 s before: +10.5 [-8.0, +23.2]
- reset (n 7): -0.2 [-11.0, +12.3]; in the 30 s before: +1.3 [-5.6, +8.0]

**boost clock** (113 decisions, 30 matches; usual: not running, fought)
- running, fought (n 21): +0.3 [-6.0, +8.3]; in the 30 s before: -2.1 [-7.4, +3.6]
- not running, advanced (n 18): -1.8 [-7.0, +7.9]; in the 30 s before: -2.4 [-10.0, +7.8]
- running, advanced (n 15): +2.5 [-9.9, +14.3]; in the 30 s before: -0.5 [-7.7, +4.6]
- not running, fell back (n 15): -8.4 [-16.8, +1.3]; in the 30 s before: +2.8 [-5.2, +9.3]
- not running, held (n 6): -12.8 [-35.2, +3.2]; in the 30 s before: +1.8 [-11.1, +18.8]

**enemy pickup** (450 decisions, 29 matches; usual: already running, fought)
- held, fought (n 67): +1.5 [-6.0, +7.4]; in the 30 s before: +1.7 [-4.4, +7.5]
- already running, advanced (n 52): -0.5 [-8.9, +6.0]; in the 30 s before: +4.2 [-1.9, +9.9]
- held, fell back (n 38): -0.1 [-9.6, +6.6]; in the 30 s before: +0.2 [-6.8, +6.6]
- ran, fought (n 36): +0.5 [-6.7, +9.3]; in the 30 s before: -1.7 [-9.0, +4.7]
- held, advanced (n 35): +1.7 [-7.1, +8.8]; in the 30 s before: -0.5 [-5.5, +4.8]
- already running, fell back (n 34): -2.4 [-7.3, +2.0]; in the 30 s before: -0.8 [-5.0, +3.8]
- ran, fell back (n 33): -0.6 [-7.0, +6.6]; in the 30 s before: -0.7 [-5.6, +3.4]
- ran, advanced (n 28): -0.5 [-8.3, +7.4]; in the 30 s before: +6.4 [+0.4, +12.0] ALREADY DIFFERENT BEFORE: partly who chooses it
- already running, held (n 16): -2.2 [-12.4, +7.3]; in the 30 s before: -5.4 [-15.7, +3.5]
- held, held (n 8): -3.1 [-20.4, +18.6]; in the 30 s before: -5.1 [-21.3, +4.3]
- ran, held (n 7): -3.9 [-19.2, +8.8]; in the 30 s before: -5.8 [-14.9, +3.7]

- **late_game**: not enough decisions yet (13)
**power play** (331 decisions, 30 matches; usual: pushed, advanced)
- pushed, fought (n 90): +2.4 [-1.0, +6.1]; in the 30 s before: -1.1 [-3.9, +3.1]
- held, fought (n 67): -2.2 [-4.4, +0.6]; in the 30 s before: +0.0 [-2.8, +4.0]
- held, fell back (n 27): -1.6 [-5.9, +4.5]; in the 30 s before: -11.8 [-20.2, -3.3] ALREADY DIFFERENT BEFORE: partly who chooses it
- held, advanced (n 11): +4.4 [-0.4, +15.0]; in the 30 s before: -2.8 [-13.4, +4.7]
- pushed, fell back (n 8): -1.7 [-12.7, +10.7]; in the 30 s before: -3.4 [-10.3, +2.2]
- pushed, held (n 5): +1.9 [-8.2, +15.8]; in the 30 s before: -11.0 [-16.5, -0.3] ALREADY DIFFERENT BEFORE: partly who chooses it

**split in base** (75 decisions, 22 matches; usual: collapsed)
- defended without a collapse (n 30): +4.7 [-3.7, +14.7]; in the 30 s before: +1.0 [-3.8, +6.2]
- missed (n 8): -5.7 [-21.2, +9.6]; in the 30 s before: +0.7 [-3.7, +6.2]

**Collapses on a split: time away and its cost** (`S32`; per collapse, averages; main = what the main fight lost while the collapsers were away)

| Group | Cases | Away (median s) | Split killed | Collapser died | Own deaths at main | Enemy deaths at main | Flag lead change | DP change | Win change |
|---|---|---|---|---|---|---|---|---|---|
| all | 39 | 16 | 6 | 3 | 0.59 | 0.15 | -0.6 | -2.1 | -2.5 |
| away under 30 s | 26 | 8 | 6 | 0 | 0 | 0.15 | -2.8 | +1.0 | -3.0 |
| away 30 to 60 s | 7 | 44 | 0 | 1 | 0.29 | 0.14 | +23.1 | -4.3 | +9.8 |
| away 60 s or more | 6 | 89 | 0 | 2 | 3.5 | 0.17 | -18.7 | -12.5 | -14.6 |
| before 20:00 | 33 | 16 | 2 | 2 | 0.42 | 0.09 | +0.9 | -5.5 | -1.0 |
| from 20:00 | 6 | 17 | 4 | 1 | 1.5 | 0.5 | -8.8 | +16.7 | -10.4 |
| split member killed | 6 | 6 | 6 | 0 | 0 | 0.67 | -3.3 | +4.2 | -7.7 |
| no kill | 33 | 18 | 0 | 3 | 0.7 | 0.06 | -0.1 | -3.2 | -1.5 |

**Leverage: where the choice matters most** (share of the spread in win-chance change explained by the choice beyond the situation; range = best minus worst choice, in points)

- boost clock (113): choice explains 7.3% (situation 6.1%); range 15.3 points, best running, advanced, worst not running, held
- split in base (75): choice explains 1.9% (situation 13.0%); range 10.4 points, best defended without a collapse, worst missed
- power play (331): choice explains 1.6% (situation 3.7%); range 9.5 points, best pushed, held, worst held, fought
- after wipe (65): choice explains 1.1% (situation 26.8%); range 6.3 points, best pushed the pit, worst took the flag
- enemy pickup (450): choice explains 0.5% (situation 6.2%); range 6.5 points, best held, advanced, worst ran, held

**Behaviour clusters: what teams actually did** (each decision's response grouped by what every player did in the next 20 s; UNNAMED = a group no single named choice covers: a response for Denning to name or reject)

*after wipe* (2 groups, separation 0.29):
- n 45: fought (midline, 1.6 of 8), fought (backline, 1.4 of 8), held (backline, 0.9 of 8), fell back (backline, 0.7 of 8); named as {'pushed the pit': 34, 'took the flag': 6, 'reset': 5}; win change -0.9
- n 20: advanced (backline, 3.9 of 8), advanced (midline, 2.0 of 8), advanced (frontline, 1.1 of 8); named as {'pushed the pit': 12, 'took the flag': 6, 'reset': 2}; win change -0.7
*boost clock* (3 groups, separation 0.2):
- n 58: fought (midline, 1.8 of 8), fought (backline, 1.6 of 8), fought (frontline, 1.4 of 8), held (backline, 0.8 of 8); named as {'not running, fought': 36, 'running, fought': 20, 'not running, held': 1}; win change -3.4
- n 50: advanced (backline, 1.5 of 8), advanced (midline, 1.4 of 8), fought (midline, 0.5 of 8); named as {'not running, advanced': 18, 'running, advanced': 14, 'not running, held': 5}; win change -1.9 UNNAMED
- n 15: fell back (backline, 3.0 of 8), fell back (midline, 1.4 of 8), fell back (frontline, 0.8 of 8), fought (midline, 0.5 of 8); named as {'not running, fell back': 10, 'running, fell back': 3, 'running, advanced': 1}; win change -5.4
*enemy pickup* (3 groups, separation 0.2):
- n 205: fought (midline, 1.9 of 8), fought (backline, 1.5 of 8), held (backline, 1.0 of 8), fought (frontline, 0.9 of 8); named as {'already running, fought': 86, 'held, fought': 61, 'ran, fought': 30}; win change -0.0 UNNAMED
- n 130: fell back (backline, 1.8 of 8), fell back (midline, 1.5 of 8), fell back (frontline, 0.7 of 8), fought (midline, 0.5 of 8); named as {'held, fell back': 38, 'already running, fell back': 33, 'ran, fell back': 31}; win change -1.1 UNNAMED
- n 118: advanced (backline, 2.3 of 8), advanced (midline, 1.9 of 8), advanced (frontline, 0.8 of 8), fought (midline, 0.5 of 8); named as {'already running, advanced': 48, 'held, advanced': 33, 'ran, advanced': 25}; win change -0.3 UNNAMED
*power play* (3 groups, separation 0.27):
- n 168: fought (backline, 2.0 of 8), fought (midline, 1.8 of 8), fought (frontline, 1.1 of 8), held (backline, 0.8 of 8); named as {'pushed, fought': 85, 'held, fought': 61, 'pushed, advanced': 10}; win change 0.5 UNNAMED
- n 124: advanced (backline, 2.8 of 8), advanced (midline, 1.9 of 8), advanced (frontline, 1.0 of 8); named as {'pushed, advanced': 113, 'held, advanced': 9, 'pushed, fought': 1}; win change 2.3
- n 45: fell back (backline, 2.6 of 8), fell back (midline, 1.4 of 8), fought (midline, 0.7 of 8), fell back (frontline, 0.5 of 8); named as {'held, fell back': 25, 'pushed, fell back': 7, 'held, fought': 6}; win change -2.5 UNNAMED
*split in base* (3 groups, separation 0.2):
- n 41: fought (midline, 1.9 of 8), fought (backline, 1.0 of 8), held (backline, 0.9 of 8), fought (frontline, 0.9 of 8); named as {'defended without a collapse': 21, 'collapsed': 16, 'missed': 4}; win change -2.4 UNNAMED
- n 31: fell back (midline, 2.0 of 8), fell back (backline, 1.2 of 8), advanced (backline, 0.8 of 8), fell back (frontline, 0.8 of 8); named as {'collapsed': 21, 'defended without a collapse': 7, 'missed': 3}; win change 0.4
- n 2: died (midline, 7.0 of 8), died (backline, 1.0 of 8); named as {'defended without a collapse': 1, 'missed': 1}; win change -0.9 UNNAMED

## 8. What results and causes are worth

Win points for the team it happened to, from 30 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 101 | +4.0 | -9.7 to +15.8 | +2.6 | no |
| capture | 339 | +4.3 | +2.5 to +6.1 | +6.3 | yes |
| death (any) | 599 | -9.3 | -14.4 to -4.5 | -6.6 | yes |
| death: against a spike build | 220 | -7.2 | -17.1 to +6.5 | -4.2 | no |
| death: against other builds | 379 | -10.5 | -17.7 to -3.2 | -8.0 | yes |
| death: back within 20 s | 100 | -6.9 | -16.5 to +2.4 | -3.7 | no |
| death: down 20 to 60 s | 212 | -10.2 | -17.0 to -3.4 | -6.2 | yes |
| death: down 60 s or more | 287 | -9.5 | -16.5 to -2.7 | -7.9 | yes |
| death: healer | 210 | -4.3 | -9.7 to +0.9 | -5.5 | no |
| death: healer in own base or pit, back within 15 s (likely deliberate) | 13 | -6.8 | -33.5 to +19.1 | -4.3 | no |
| death: healer, other | 197 | -4.1 | -9.0 to +0.7 | -5.6 | no |
| death: not a healer | 389 | -12.0 | -18.8 to -5.5 | -7.2 | yes |
| pit NPC lost (any): taken by a spike build | 60 | +0.4 | -5.7 to +11.2 | +0.5 | no |
| pit NPC lost (any): taken by other builds | 189 | -5.2 | -11.7 to +0.8 | -0.9 | no |
| pit NPC lost: archer | 141 | -1.3 | -5.7 to +3.3 | -0.5 | no |
| pit NPC lost: bodyguard | 36 | -3.7 | -9.2 to +1.6 | -2.2 | no |
| pit NPC lost: knight | 72 | -8.8 | -17.3 to -1.4 | +0.3 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value.

*deaths* (per 10 s in that state; result worth -9.3 points, base rate 1.3%):

- enemies within 1,500 7.5 to 8: result chance +2.5 points, worth -0.24 win points
- own minus enemy team strength 426 to 721: result chance -0.6 points, worth +0.05 win points
- current health % 1 to 48.5: result chance +10.2 points, worth -0.95 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +4.1 points, worth -0.38 win points
- maximum health after death penalty, as a share of normal 0.4 to 0.64: result chance +4.8 points, worth -0.44 win points
- own healers alive within cast range 0 to 0.5: result chance +0.7 points, worth -0.06 win points
- distance from its own pit 13000.5 to 18468: result chance +1.1 points, worth -0.11 win points

*kill conversion* (per burst, for the attacking team; result worth +9.3 points, base rate 30.0%):

- target's health ceiling 0.4 to 0.56: result chance +28.5 points, worth +2.65 win points
- damage in the 2 s burst 547.5 to 839: result chance +18.2 points, worth +1.7 win points
- target health % when the burst started 0 to 40.5: result chance +23.6 points, worth +2.19 win points
- target's healers in range 0 to 0.5: result chance +21.3 points, worth +1.98 win points
- a prot on the target 0.5 to 1: result chance -7.9 points, worth -0.73 win points
- match minute 0.3 to 1.45: result chance -10.3 points, worth -0.96 win points

*npc loss* (per case, for the defending team; result worth -3.8 points, base rate 17.5%):

- own players in the pit 7.5 to 8: result chance -15.7 points, worth +0.6 win points
- damage on the pit NPCs in the last 5 s 363.5 to 1170: result chance +27.8 points, worth -1.06 win points
- enemy players in the pit 7.5 to 8: result chance +23.1 points, worth -0.88 win points
- own players alive outside the pit 0 to 0.5: result chance +22.3 points, worth -0.85 win points
- attacking minus defending team strength -682 to -377: result chance -9.0 points, worth +0.34 win points
- of which healers 0 to 0.5: result chance +8.3 points, worth -0.32 win points
- own pit archers alive 2.5 to 3: result chance +16.8 points, worth -0.64 win points

## 9. For Denning

- Which curves look wrong to you? A correction (direction, cap, drop, or a pair to always test) is logged with your reason and tested on held-out matches.
- Do any surprises remind you of something the variables don't capture (a missing variable)?
- Any variable you think matters that isn't listed?

