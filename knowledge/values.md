# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

Win points for the team it happened to, from 30 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 95 | +5.0 | -0.8 to +10.1 | +1.7 | no |
| capture | 336 | +2.0 | +0.3 to +4.0 | +3.0 | yes |
| death (any) | 586 | -4.2 | -7.5 to -1.6 | -3.0 | yes |
| death: against a spike build | 220 | -3.8 | -9.6 to +3.2 | -1.8 | no |
| death: against other builds | 366 | -4.5 | -9.3 to -0.6 | -3.7 | yes |
| death: back within 20 s | 100 | -3.1 | -8.6 to +1.8 | -2.6 | no |
| death: down 20 to 60 s | 203 | -4.2 | -10.1 to +1.2 | -0.0 | no |
| death: down 60 s or more | 283 | -4.6 | -9.0 to -0.2 | -5.2 | yes |
| death: healer | 207 | -1.2 | -4.4 to +1.8 | -2.2 | no |
| death: healer in own base or pit, back within 15 s (likely deliberate) | 13 | +3.3 | -7.8 to +20.0 | +4.1 | no |
| death: healer, other | 194 | -1.5 | -4.4 to +1.0 | -2.7 | no |
| death: not a healer | 379 | -5.9 | -10.1 to -1.8 | -3.4 | yes |
| pit NPC lost (any): taken by a spike build | 60 | -1.8 | -9.1 to +9.8 | -1.3 | no |
| pit NPC lost (any): taken by other builds | 181 | -3.6 | -8.0 to +0.2 | +3.9 | no |
| pit NPC lost: archer | 138 | -4.2 | -8.3 to -0.7 | -1.0 | yes |
| pit NPC lost: bodyguard | 35 | +0.1 | -6.0 to +7.0 | +6.2 | no |
| pit NPC lost: knight | 68 | -2.5 | -9.3 to +3.8 | +8.3 | no |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value.

*deaths* (per 10 s in that state; result worth -4.2 points, base rate 1.3%):

- enemies within 1,500 7.5 to 8: result chance +2.7 points, worth -0.11 win points
- current health % 1 to 48.5: result chance +11.1 points, worth -0.46 win points
- own minus enemy team strength 480.5 to 1092: result chance -0.7 points, worth +0.03 win points
- maximum health after death penalty, as a share of normal 0.4 to 0.64: result chance +5.8 points, worth -0.24 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +4.4 points, worth -0.19 win points
- distance from its own pit 13044.5 to 18511: result chance +1.4 points, worth -0.06 win points

*kill conversion* (per burst, for the attacking team; result worth +4.2 points, base rate 29.8%):

- target's health ceiling 0.4 to 0.56: result chance +30.0 points, worth +1.26 win points
- damage in the 2 s burst 547.5 to 839: result chance +19.9 points, worth +0.83 win points
- target health % when the burst started 0 to 41.5: result chance +23.5 points, worth +0.99 win points
- target's healers in range 0 to 0.5: result chance +22.4 points, worth +0.94 win points
- a prot on the target 0.5 to 1: result chance -7.5 points, worth -0.32 win points
- match minute 0.3 to 1.35: result chance -9.0 points, worth -0.38 win points

*npc loss* (per case, for the defending team; result worth -3.1 points, base rate 19.1%):

- own players in the pit 7.5 to 8: result chance -17.0 points, worth +0.52 win points
- damage on the pit NPCs in the last 5 s 360.5 to 1170: result chance +28.7 points, worth -0.89 win points
- own players alive outside the pit 0 to 0.5: result chance +21.7 points, worth -0.67 win points
- enemy players in the pit 7.5 to 8: result chance +20.5 points, worth -0.63 win points
- attackers' measured damage per second against a Lord (benchmarks) 101.65 to 156.3: result chance +14.9 points, worth -0.46 win points
- attacking minus defending team strength 480.5 to 636: result chance +14.7 points, worth -0.46 win points
- pit NPCs alive (targets the defending monks must watch, P9) 6.5 to 9: result chance +26.0 points, worth -0.81 win points
- of which healers 0 to 0.5: result chance +11.8 points, worth -0.36 win points

