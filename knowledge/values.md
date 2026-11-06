# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

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

