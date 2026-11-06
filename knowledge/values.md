# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

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

