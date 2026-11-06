# Win-probability model (batch 2, 34 matches)

Every number is win-chance points for an otherwise even game (50%), learned from the matches so far; "+-" is the uncertainty across bags. Few matches = rough curves.

## How well it predicts (matches held out whole)

**Verdict: not yet better than strength alone: treat the curves as noise.** Team strength alone is the baseline; the curves below are what the game state adds to it.

Gain over strength alone (log loss, resampling whole matches): -0.067, 90% range -0.306 to +0.141.

- strength only: accuracy 66%, log loss 0.514 (0-5 min 76%; 5-10 min 70%; 10-15 min 61%; 15-end min 55%; matches lasting 15 min+ 59%; matches even on strength (gap under 200) 44%)
- glass box: accuracy 75%, log loss 0.581 (0-5 min 77%; 5-10 min 78%; 10-15 min 71%; 15-end min 74%; matches lasting 15 min+ 69%; matches even on strength (gap under 200) 63%)
- black box: accuracy 57%, log loss 1.544 (0-5 min 59%; 5-10 min 58%; 10-15 min 58%; 15-end min 53%; matches lasting 15 min+ 50%; matches even on strength (gap under 200) 44%)

## What it learned, most important first

### morale_diff (importance 1.191)
own minus enemy morale summed over players (boosts +, death penalty -)
-470.0 to -199.0: -44.0 (+-2.8); -199.0 to -154.0: -43.2 (+-3.1); -154.0 to -110.5: -40.7 (+-1.2); -110.5 to -89.0: -29.2 (+-1.1); -89.0 to -46.5: -27.7 (+-1.3); -46.5 to -15.5: -5.1 (+-1.6); -15.5 to -1.0: -2.2 (+-0.7); -1.0 to 1.0: +0.7 (+-1.3); 1.0 to 15.5: +3.2 (+-1.0); 15.5 to 56.0: +10.7 (+-1.6); 56.0 to 97.0: +29.8 (+-0.8); 97.0 to 139.5: +33.6 (+-1.7); 139.5 to 187.5: +42.4 (+-1.9); 187.5 to 470.0: +43.0 (+-1.5)

### stand (importance 0.298)
who holds the flag stand: 1 own, 0 nobody, -1 enemy
-1.0 to -0.5: -7.8 (+-0.2); -0.5 to 0.5: +0.2 (+-0.5); 0.5 to 1.0: +7.8 (+-0.1)

### main_diff (importance 0.281)
own minus enemy players in each team's main group
-8.0 to -4.5: -21.6 (+-1.3); -4.5 to -3.5: -24.5 (+-5.1); -3.5 to -2.5: -10.9 (+-0.5); -2.5 to -1.5: -8.6 (+-0.4); -1.5 to -0.5: -7.1 (+-0.3); -0.5 to 0.5: -0.1 (+-0.1); 0.5 to 1.5: +7.3 (+-0.4); 1.5 to 2.5: +8.6 (+-0.4); 2.5 to 3.5: +10.5 (+-0.3); 3.5 to 4.5: +25.2 (+-2.0); 4.5 to 8.0: +20.2 (+-4.9)

### spike_killable_diff (importance 0.273)
enemy minus own players within one spike of the other side (DP stacking; 0 unless a spike build is involved)
-8.0 to -7.5: -29.1 (+-2.0); -7.5 to -5.5: -28.9 (+-0.6); -5.5 to -3.5: -31.0 (+-0.9); -3.5 to -2.5: -28.5 (+-1.1); -2.5 to -1.5: -26.1 (+-2.4); -1.5 to -0.5: -23.2 (+-1.4); -0.5 to 0.5: -0.0 (+-0.1); 0.5 to 1.5: +22.7 (+-1.7); 1.5 to 2.5: +26.0 (+-1.1); 2.5 to 4.5: +28.7 (+-1.2); 4.5 to 7.5: +30.2 (+-0.7); 7.5 to 8.0: +30.5 (+-1.4)

### lord_damage_diff (importance 0.206)
own minus enemy Lord damage dealt so far (the 28:00 tiebreak; players can't see it); blank when either team's Lord damage wasn't observed
-9661.0 to -4893.5: +49.2 (+-6.2); -4893.5 to -2590.5: +26.7 (+-5.6); -2590.5 to -1323.5: +1.7 (+-0.8); -1323.5 to -631.0: +1.0 (+-0.8); -631.0 to -146.5: +0.4 (+-0.8); -146.5 to -95.5: -0.6 (+-0.9); -95.5 to -2.5: -1.4 (+-1.0); -2.5 to 2.5: -0.4 (+-0.2); 2.5 to 95.5: +1.6 (+-1.7); 95.5 to 161.0: +0.6 (+-1.3); 161.0 to 784.0: -0.8 (+-1.1); 784.0 to 1960.0: -2.2 (+-0.5); 1960.0 to 4259.0: -4.2 (+-0.9); 4259.0 to 9661.0: -48.8 (+-1.4)

### flag_lead (importance 0.205)
seconds up (+) or down (-) on flags: enemy's response minus own on the next capture exchange
-86.0 to -70.5: +19.1 (+-1.2); -70.5 to -55.5: +10.6 (+-1.4); -55.5 to -43.5: +0.6 (+-1.0); -43.5 to -31.5: +0.2 (+-0.9); -31.5 to -20.5: -0.1 (+-0.8); -20.5 to -10.5: -0.2 (+-0.8); -10.5 to -0.5: +0.3 (+-0.6); -0.5 to 9.5: +0.7 (+-0.2); 9.5 to 20.5: +0.5 (+-0.2); 20.5 to 31.5: +0.4 (+-0.3); 31.5 to 43.5: +0.2 (+-0.3); 43.5 to 55.5: -0.3 (+-0.4); 55.5 to 70.5: -10.8 (+-0.8); 70.5 to 86.0: -20.9 (+-1.4)

### boost_clock (importance 0.191)
seconds until the stand holder's next boost (+ if own boost is coming, - if the enemy's, 0 nobody)
-120.0 to -109.5: -6.1 (+-0.6); -109.5 to -98.5: -5.8 (+-0.5); -98.5 to -85.5: -5.4 (+-0.5); -85.5 to -71.5: -5.0 (+-0.4); -71.5 to -54.5: -4.6 (+-0.3); -54.5 to -32.5: -4.0 (+-0.4); -32.5 to -0.5: -3.1 (+-0.3); -0.5 to 9.5: -1.1 (+-0.5); 9.5 to 42.5: +4.6 (+-0.4); 42.5 to 64.5: +5.1 (+-0.4); 64.5 to 81.5: +5.5 (+-0.4); 81.5 to 95.5: +5.5 (+-0.8); 95.5 to 108.5: +5.6 (+-0.7); 108.5 to 120.0: +5.2 (+-0.3)

### down_diff_s (importance 0.189)
enemy minus own seconds until all dead players are back (+ = the enemy has more time down)
-960.0 to -195.0: -35.1 (+-14.5); -195.0 to -127.5: -17.2 (+-2.2); -127.5 to -97.5: -13.0 (+-1.9); -97.5 to -67.5: -9.5 (+-1.2); -67.5 to -52.5: -7.3 (+-0.9); -52.5 to -37.5: -4.9 (+-1.4); -37.5 to -7.5: -3.1 (+-0.6); -7.5 to 7.5: -0.7 (+-0.2); 7.5 to 52.5: +1.7 (+-1.1); 52.5 to 67.5: +5.4 (+-0.4); 67.5 to 82.5: +8.3 (+-0.1); 82.5 to 97.5: +11.1 (+-0.8); 97.5 to 142.5: +13.6 (+-1.3); 142.5 to 960.0: +39.6 (+-2.7)

### fight_state (importance 0.189)
who is winning the fight now: enemy minus own expected deaths in the next 10 s, from a deaths model that never saw the match (fightstate.py)
-3.29 to -0.28: +10.4 (+-1.1); -0.28 to -0.12: +5.9 (+-0.5); -0.12 to -0.06: +4.6 (+-0.9); -0.06 to -0.03: +4.6 (+-0.8); -0.03 to -0.02: +4.7 (+-0.7); -0.02 to -0.01: +2.1 (+-1.2); -0.01 to -0.0: +1.7 (+-1.2); -0.0 to 0.01: -2.6 (+-0.9); 0.01 to 0.02: -3.9 (+-0.6); 0.02 to 0.03: -4.5 (+-0.2); 0.03 to 0.06: -4.5 (+-0.2); 0.06 to 0.12: -4.3 (+-0.4); 0.12 to 0.28: -5.5 (+-1.5); 0.28 to 3.29: -7.7 (+-1.2)

### pit_pressure_diff (importance 0.188)
own players in the enemy pit minus enemy players in the own pit
-8.0 to -5.5: -13.3 (+-10.2); -5.5 to -4.5: -11.1 (+-10.1); -4.5 to -3.5: +15.0 (+-1.7); -3.5 to -2.5: +16.3 (+-1.0); -2.5 to -1.5: +12.8 (+-0.8); -1.5 to -0.5: +13.5 (+-0.9); -0.5 to 0.5: +0.7 (+-0.5); 0.5 to 1.5: -11.4 (+-1.0); 1.5 to 2.5: -10.4 (+-0.9); 2.5 to 3.5: -11.6 (+-2.6); 3.5 to 5.5: -10.2 (+-2.2); 5.5 to 8.0: -6.6 (+-2.0)

### archers_diff (importance 0.161)
own minus enemy pit archers alive
-3.0 to -2.5: +2.5 (+-1.4); -2.5 to -1.5: +8.9 (+-0.8); -1.5 to -0.5: +9.2 (+-0.7); -0.5 to 0.5: -0.3 (+-0.3); 0.5 to 1.5: -8.4 (+-0.5); 1.5 to 2.5: -8.4 (+-0.5); 2.5 to 3.0: -2.0 (+-1.6)

### carrying_diff (importance 0.114)
own minus enemy players carrying a flag
-1.0 to -0.5: -10.9 (+-1.1); -0.5 to 0.5: +0.1 (+-0.3); 0.5 to 1.0: +10.5 (+-1.2)

### alive_diff (importance 0.094)
own minus enemy players alive
-8.0 to -4.5: -17.5 (+-0.9); -4.5 to -3.5: -14.1 (+-1.1); -3.5 to -2.5: -11.6 (+-0.6); -2.5 to -1.5: -8.4 (+-0.4); -1.5 to -0.5: -4.5 (+-0.9); -0.5 to 0.5: +0.0 (+-0.2); 0.5 to 1.5: +4.0 (+-0.5); 1.5 to 2.5: +8.0 (+-1.7); 2.5 to 3.5: +10.4 (+-1.1); 3.5 to 4.5: +15.2 (+-1.3); 4.5 to 8.0: +19.7 (+-1.9)

### knights_diff (importance 0.08)
own minus enemy pit knights alive
-2.0 to -1.5: -6.6 (+-1.7); -1.5 to -0.5: +0.5 (+-0.5); -0.5 to 0.5: +0.5 (+-0.4); 0.5 to 1.5: +0.8 (+-0.5); 1.5 to 2.0: +4.2 (+-1.1)

### lord_health_diff (importance 0.062)
own minus enemy Lord health as a share of its max (rebuilt from damage, healing and measured regeneration, lord.py); blank if unobserved
-1.0 to -0.82: -15.3 (+-4.0); -0.82 to -0.39: -15.1 (+-4.1); -0.39 to -0.23: -22.5 (+-8.0); -0.23 to -0.15: -27.7 (+-4.5); -0.15 to -0.07: -15.9 (+-5.8); -0.07 to -0.03: -0.4 (+-0.3); -0.03 to -0.0: -0.1 (+-0.3); -0.0 to 0.0: +0.1 (+-0.3); 0.0 to 0.03: +0.4 (+-0.2); 0.03 to 0.08: +5.6 (+-5.0); 0.08 to 0.18: +23.1 (+-4.1); 0.18 to 0.32: +24.1 (+-3.6); 0.32 to 0.7: +16.6 (+-10.7); 0.7 to 1.0: +19.0 (+-10.8)

### bodyguard_diff (importance 0.032)
own minus enemy Bodyguard alive
-1.0 to -0.5: +0.4 (+-2.2); -0.5 to 0.5: -0.5 (+-0.5); 0.5 to 1.0: +3.9 (+-3.8)

### lord_exposed_diff (importance 0.025)
enemy Lord exposed (its Bodyguard and knights dead) minus own: +1 = only the enemy's is exposed
-1.0 to -0.5: -0.1 (+-5.3); -0.5 to 0.5: +0.4 (+-0.6); 0.5 to 1.0: -3.5 (+-3.7)

### res_in (importance 0.006)
seconds until the next base res
15.0 to 22.5: -0.2 (+-0.4); 22.5 to 37.5: -0.2 (+-0.3); 37.5 to 52.5: -0.1 (+-0.1); 52.5 to 67.5: -0.0 (+-0.0); 67.5 to 82.5: +0.0 (+-0.1); 82.5 to 97.5: +0.1 (+-0.2); 97.5 to 112.5: +0.2 (+-0.2); 112.5 to 120.0: +0.2 (+-0.3)

### minute (importance 0.002)
match clock in minutes
0.0 to 1.12: -0.1 (+-0.5); 1.12 to 2.38: -0.1 (+-0.4); 2.38 to 3.62: -0.0 (+-0.3); 3.62 to 4.88: -0.0 (+-0.1); 4.88 to 6.12: +0.0 (+-0.1); 6.12 to 7.62: +0.0 (+-0.0); 7.62 to 9.12: +0.0 (+-0.1); 9.12 to 10.88: +0.1 (+-0.2); 10.88 to 12.62: +0.0 (+-0.2); 12.62 to 14.38: +0.1 (+-0.2); 14.38 to 16.38: +0.0 (+-0.2); 16.38 to 18.88: +0.0 (+-0.2); 18.88 to 21.88: +0.0 (+-0.2); 21.88 to 28.0: -0.0 (+-0.3)

### morale_total (importance 0.002)
both teams' morale summed (how much death penalty is in the game overall)
-310.0 to -116.0: +0.2 (+-0.1); -116.0 to -86.0: +0.1 (+-0.2); -86.0 to -60.5: +0.1 (+-0.2); -60.5 to -47.5: +0.1 (+-0.2); -47.5 to -30.5: +0.0 (+-0.1); -30.5 to -16.5: +0.0 (+-0.0); -16.5 to -14.0: +0.0 (+-0.1); -14.0 to -0.5: -0.0 (+-0.1); -0.5 to 0.5: -0.0 (+-0.1); 0.5 to 18.0: -0.0 (+-0.1); 18.0 to 34.5: -0.1 (+-0.1); 34.5 to 49.5: -0.1 (+-0.1); 49.5 to 64.0: -0.1 (+-0.1); 64.0 to 119.0: -0.2 (+-0.1)

