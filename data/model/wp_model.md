# Win-probability model (batch 1, 30 matches)

Every number is win-chance points for an otherwise even game (50%), learned from the matches so far; "+-" is the uncertainty across bags. Few matches = rough curves.

## How well it predicts (matches held out whole)

**Verdict: beats strength alone.** Team strength alone is the baseline; the curves below are what the game state adds to it.

- strength only: accuracy 64%, log loss 0.633 (0-5 min 74%; 5-10 min 69%; 10-15 min 60%; 15-end min 51%)
- glass box: accuracy 79%, log loss 0.562 (0-5 min 84%; 5-10 min 86%; 10-15 min 82%; 15-end min 64%)
- black box: accuracy 76%, log loss 0.791 (0-5 min 78%; 5-10 min 76%; 10-15 min 76%; 15-end min 74%)

## What it learned, most important first

### morale_diff (importance 1.951)
own minus enemy morale summed over players (boosts +, death penalty -)
-470.0 to -199.0: -48.3 (+-1.6); -199.0 to -159.0: -48.1 (+-2.3); -159.0 to -110.5: -45.6 (+-1.6); -110.5 to -86.0: -45.2 (+-1.0); -86.0 to -46.5: -39.6 (+-1.0); -46.5 to -15.5: -18.7 (+-2.8); -15.5 to -1.0: -4.8 (+-1.0); -1.0 to 1.0: -0.7 (+-0.4); 1.0 to 23.0: +3.3 (+-1.1); 23.0 to 56.0: +27.2 (+-0.7); 56.0 to 97.0: +41.3 (+-2.0); 97.0 to 144.0: +46.5 (+-2.5); 144.0 to 196.0: +47.7 (+-1.3); 196.0 to 470.0: +48.0 (+-2.3)

### knights_diff (importance 1.266)
own minus enemy pit knights alive
-2.0 to -1.5: +41.5 (+-0.6); -1.5 to -0.5: +38.5 (+-1.2); -0.5 to 0.5: -0.8 (+-0.5); 0.5 to 1.5: -37.9 (+-0.9); 1.5 to 2.0: -41.2 (+-1.0)

### bodyguard_diff (importance 1.218)
own minus enemy Bodyguard alive
-1.0 to -0.5: +36.3 (+-1.2); -0.5 to 0.5: -0.6 (+-0.6); 0.5 to 1.0: -36.0 (+-1.4)

### flag_lead (importance 0.342)
seconds up (+) or down (-) on flags: enemy's response minus own on the next capture exchange
-81.0 to -64.5: -9.7 (+-1.3); -64.5 to -54.5: -9.9 (+-0.5); -54.5 to -36.5: -9.3 (+-0.6); -36.5 to -27.5: -9.0 (+-0.6); -27.5 to -17.5: -8.1 (+-0.4); -17.5 to -8.5: -7.4 (+-0.2); -8.5 to -0.5: -6.3 (+-0.3); -0.5 to 6.5: +2.3 (+-1.7); 6.5 to 16.5: +7.3 (+-0.7); 16.5 to 27.5: +8.3 (+-0.9); 27.5 to 36.5: +9.4 (+-0.5); 36.5 to 54.5: +9.7 (+-0.7); 54.5 to 64.5: +10.2 (+-0.5); 64.5 to 81.0: +10.8 (+-0.4)

### lord_damage_diff (importance 0.304)
own minus enemy Lord damage dealt so far (the 28:00 tiebreak; players can't see it)
-9661.0 to -5219.0: +49.1 (+-7.5); -5219.0 to -3355.0: +34.9 (+-3.4); -3355.0 to -2101.5: -13.8 (+-1.7); -2101.5 to -1317.5: -19.3 (+-3.2); -1317.5 to -530.5: -22.0 (+-2.3); -530.5 to -102.0: -24.4 (+-2.2); -102.0 to -8.5: -27.0 (+-2.1); -8.5 to 8.5: +0.2 (+-0.3); 8.5 to 102.0: +24.5 (+-1.3); 102.0 to 688.5: +22.7 (+-0.6); 688.5 to 1338.0: +20.8 (+-1.0); 1338.0 to 3001.0: +7.2 (+-2.2); 3001.0 to 4965.0: -1.4 (+-2.1); 4965.0 to 9661.0: -49.0 (+-5.0)

### stand (importance 0.294)
who holds the flag stand: 1 own, 0 nobody, -1 enemy
-1.0 to -0.5: -7.8 (+-0.3); -0.5 to 0.5: +0.3 (+-1.0); 0.5 to 1.0: +7.7 (+-0.4)

### pit_pressure_diff (importance 0.238)
own players in the enemy pit minus enemy players in the own pit
-8.0 to -5.5: -0.7 (+-6.5); -5.5 to -4.5: +2.6 (+-6.3); -4.5 to -3.5: +12.5 (+-1.6); -3.5 to -2.5: +14.7 (+-1.6); -2.5 to -1.5: +13.5 (+-1.1); -1.5 to -0.5: +14.7 (+-1.3); -0.5 to 0.5: +1.7 (+-0.4); 0.5 to 1.5: -19.5 (+-1.0); 1.5 to 2.5: -18.8 (+-1.1); 2.5 to 3.5: -18.0 (+-1.4); 3.5 to 5.5: -16.0 (+-1.0); 5.5 to 8.0: -14.1 (+-1.6)

### archers_diff (importance 0.199)
own minus enemy pit archers alive
-4.0 to -3.5: -20.1 (+-2.4); -3.5 to -2.5: -17.9 (+-2.7); -2.5 to -1.5: +3.7 (+-2.0); -1.5 to -0.5: +6.4 (+-0.3); -0.5 to 0.5: -0.8 (+-0.7); 0.5 to 1.5: -6.6 (+-0.4); 1.5 to 2.5: -2.9 (+-2.1); 2.5 to 3.5: +23.0 (+-1.4); 3.5 to 4.0: +24.4 (+-1.2)

### down_diff_s (importance 0.147)
enemy minus own seconds until all dead players are back (+ = the enemy has more time down)
-960.0 to -195.0: -21.2 (+-2.7); -195.0 to -127.5: -17.7 (+-1.0); -127.5 to -97.5: -15.6 (+-1.3); -97.5 to -67.5: -12.7 (+-0.6); -67.5 to -52.5: -9.5 (+-0.3); -52.5 to -37.5: -7.7 (+-0.9); -37.5 to -7.5: -3.9 (+-0.6); -7.5 to 7.5: +0.3 (+-0.3); 7.5 to 37.5: +3.6 (+-0.8); 37.5 to 67.5: +5.5 (+-0.5); 67.5 to 97.5: +8.3 (+-0.6); 97.5 to 127.5: +11.5 (+-0.9); 127.5 to 195.0: +14.5 (+-0.3); 195.0 to 960.0: +30.2 (+-15.9)

### boost_clock (importance 0.142)
seconds until the stand holder's next boost (+ if own boost is coming, - if the enemy's, 0 nobody)
-120.0 to -109.5: +6.4 (+-0.6); -109.5 to -98.5: +6.5 (+-0.6); -98.5 to -85.5: +6.6 (+-0.7); -85.5 to -71.5: +3.6 (+-2.0); -71.5 to -54.5: +1.1 (+-1.5); -54.5 to -32.5: -3.6 (+-1.3); -32.5 to -0.5: -2.6 (+-1.2); -0.5 to 9.5: -1.2 (+-0.9); 9.5 to 43.5: +0.1 (+-0.8); 43.5 to 64.5: +0.8 (+-0.9); 64.5 to 81.5: -3.9 (+-1.2); 81.5 to 95.5: -4.5 (+-0.4); 95.5 to 108.5: -4.3 (+-0.3); 108.5 to 120.0: -4.1 (+-0.5)

### alive_diff (importance 0.102)
own minus enemy players alive
-8.0 to -4.5: -25.5 (+-4.5); -4.5 to -3.5: -20.5 (+-6.0); -3.5 to -2.5: -10.2 (+-1.6); -2.5 to -1.5: -6.9 (+-1.3); -1.5 to -0.5: -3.3 (+-0.5); -0.5 to 0.5: -0.0 (+-0.2); 0.5 to 1.5: +3.1 (+-1.2); 1.5 to 2.5: +6.8 (+-2.3); 2.5 to 3.5: +10.2 (+-1.7); 3.5 to 4.5: +20.8 (+-9.7); 4.5 to 8.0: +28.1 (+-9.7)

### main_diff (importance 0.102)
own minus enemy players in each team's main group
-8.0 to -4.5: -11.7 (+-0.8); -4.5 to -3.5: -7.9 (+-0.4); -3.5 to -2.5: -5.4 (+-0.3); -2.5 to -1.5: -3.6 (+-0.2); -1.5 to -0.5: -2.0 (+-0.3); -0.5 to 0.5: +0.3 (+-0.3); 0.5 to 1.5: +1.8 (+-0.5); 1.5 to 2.5: +3.3 (+-0.4); 2.5 to 3.5: +4.7 (+-0.3); 3.5 to 4.5: +7.6 (+-0.7); 4.5 to 8.0: +11.6 (+-0.9)

### spike_killable_diff (importance 0.074)
enemy minus own players within one spike of the other side (DP stacking; 0 unless a spike build is involved)
-8.0 to -7.5: +0.4 (+-1.6); -7.5 to -5.5: +3.5 (+-1.8); -5.5 to -3.5: -17.2 (+-1.6); -3.5 to -2.5: -13.8 (+-1.5); -2.5 to -1.5: -10.5 (+-1.8); -1.5 to -0.5: -6.3 (+-1.7); -0.5 to 0.5: -0.1 (+-0.3); 0.5 to 1.5: +6.2 (+-0.8); 1.5 to 2.5: +11.0 (+-1.1); 2.5 to 4.5: +13.9 (+-1.5); 4.5 to 7.5: +1.8 (+-1.0); 7.5 to 8.0: +4.1 (+-1.6)

### carrying_diff (importance 0.053)
own minus enemy players carrying a flag
-1.0 to -0.5: -4.1 (+-0.5); -0.5 to 0.5: -0.2 (+-0.1); 0.5 to 1.0: +4.9 (+-0.9)

### minute (importance 0.009)
match clock in minutes
0.0 to 1.12: -0.3 (+-0.5); 1.12 to 2.38: -0.3 (+-0.3); 2.38 to 3.62: -0.3 (+-0.1); 3.62 to 4.88: -0.2 (+-0.1); 4.88 to 6.12: -0.2 (+-0.0); 6.12 to 7.62: -0.1 (+-0.1); 7.62 to 9.12: -0.1 (+-0.1); 9.12 to 10.88: +0.0 (+-0.2); 10.88 to 12.62: +0.1 (+-0.2); 12.62 to 14.38: +0.2 (+-0.2); 14.38 to 16.62: +0.2 (+-0.2); 16.62 to 19.12: +0.3 (+-0.2); 19.12 to 22.38: +0.3 (+-0.2); 22.38 to 28.0: +0.6 (+-0.2)

### morale_total (importance 0.006)
both teams' morale summed (how much death penalty is in the game overall)
-310.0 to -116.0: +0.3 (+-0.2); -116.0 to -88.0: +0.3 (+-0.2); -88.0 to -64.5: +0.3 (+-0.2); -64.5 to -54.5: +0.3 (+-0.2); -54.5 to -44.5: +0.2 (+-0.1); -44.5 to -30.5: +0.1 (+-0.1); -30.5 to -16.5: +0.0 (+-0.1); -16.5 to -14.0: -0.1 (+-0.1); -14.0 to -0.5: -0.1 (+-0.1); -0.5 to 0.5: -0.2 (+-0.1); 0.5 to 25.5: -0.2 (+-0.1); 25.5 to 48.5: -0.2 (+-0.1); 48.5 to 64.0: -0.2 (+-0.2); 64.0 to 119.0: +0.0 (+-0.2)

### res_in (importance 0.004)
seconds until the next base res
15.0 to 22.5: -0.2 (+-0.3); 22.5 to 37.5: -0.2 (+-0.2); 37.5 to 52.5: -0.1 (+-0.1); 52.5 to 67.5: -0.0 (+-0.0); 67.5 to 82.5: +0.0 (+-0.1); 82.5 to 97.5: +0.1 (+-0.1); 97.5 to 112.5: +0.1 (+-0.2); 112.5 to 120.0: +0.1 (+-0.2)

