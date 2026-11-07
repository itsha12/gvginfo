# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

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

