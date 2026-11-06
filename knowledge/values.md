# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

Win points for the team it happened to, from 34 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 115 | +3.0 | -8.4 to +13.8 | +2.6 | no |
| capture | 374 | +4.1 | +2.3 to +5.9 | +5.7 | yes |
| death (any) | 685 | -7.3 | -12.1 to -2.7 | -4.8 | yes |
| death: against a spike build | 225 | -6.3 | -15.8 to +5.5 | -3.9 | no |
| death: against other builds | 460 | -7.7 | -14.3 to -2.1 | -5.3 | yes |
| death: back within 20 s | 122 | -5.8 | -14.0 to +1.4 | -3.9 | no |
| death: down 20 to 60 s | 236 | -9.3 | -15.3 to -3.5 | -4.2 | yes |
| death: down 60 s or more | 327 | -6.3 | -11.9 to -1.0 | -5.6 | yes |
| death: healer | 231 | -2.6 | -7.3 to +2.0 | -3.5 | no |
| death: healer in own base or pit, back within 15 s (likely deliberate) | 15 | -6.0 | -28.3 to +15.1 | -6.0 | no |
| death: healer, other | 216 | -2.4 | -6.3 to +1.5 | -3.4 | no |
| death: not a healer | 454 | -9.6 | -15.6 to -4.3 | -5.5 | yes |
| pit NPC lost (any): taken by a spike build | 60 | +0.4 | -5.7 to +11.3 | -0.3 | no |
| pit NPC lost (any): taken by other builds | 216 | -4.6 | -9.8 to +0.3 | -0.0 | no |
| pit NPC lost: archer | 155 | -1.3 | -5.3 to +2.7 | -0.2 | no |
| pit NPC lost: bodyguard | 41 | -2.3 | -7.5 to +2.2 | +0.2 | no |
| pit NPC lost: knight | 80 | -8.3 | -15.5 to -2.0 | -0.1 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value.

*deaths* (per 10 s in that state; result worth -7.3 points, base rate 1.3%):

- enemies within 1,500 7.5 to 8: result chance +2.2 points, worth -0.16 win points
- own minus enemy team strength -285.5 to -140.5: result chance +1.1 points, worth -0.08 win points
- current health % 1 to 48.5: result chance +10.0 points, worth -0.73 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +3.6 points, worth -0.26 win points
- maximum health after death penalty, as a share of normal 0.4 to 0.67: result chance +5.1 points, worth -0.37 win points
- own healers alive within cast range 0 to 0.5: result chance +0.8 points, worth -0.06 win points
- match minute 21.25 to 28: result chance +1.2 points, worth -0.08 win points

*kill conversion* (per burst, for the attacking team; result worth +7.3 points, base rate 28.9%):

- damage in the 2 s burst 547.5 to 839: result chance +25.6 points, worth +1.87 win points
- target's health ceiling 0.4 to 0.56: result chance +36.6 points, worth +2.68 win points
- target's healers in range 0 to 0.5: result chance +33.8 points, worth +2.46 win points
- target health % when the burst started 0 to 43: result chance +21.6 points, worth +1.58 win points
- match minute 0.3 to 1.45: result chance -13.0 points, worth -0.95 win points
- a prot on the target 0.5 to 1: result chance -8.1 points, worth -0.59 win points
- attacking minus target team strength 426 to 721: result chance +19.2 points, worth +1.4 win points

*npc loss* (per case, for the defending team; result worth -3.5 points, base rate 16.9%):

- own players in the pit 7.5 to 8: result chance -15.6 points, worth +0.54 win points
- damage on the pit NPCs in the last 5 s 375.5 to 1170: result chance +30.7 points, worth -1.07 win points
- own players alive outside the pit 0 to 0.5: result chance +24.7 points, worth -0.86 win points
- enemy players in the pit 7.5 to 8: result chance +17.7 points, worth -0.61 win points
- attacking minus defending team strength -682 to -415.5: result chance -9.9 points, worth +0.34 win points
- own pit archers alive 2.5 to 3: result chance +21.1 points, worth -0.73 win points
- attackers' measured damage per second against a Lord (benchmarks) 101.05 to 148.9: result chance +6.1 points, worth -0.21 win points

