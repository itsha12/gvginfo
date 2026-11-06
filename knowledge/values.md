# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

Win points for the team it happened to, from 53 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 168 | -0.1 | -9.8 to +9.7 | +1.4 | no |
| capture | 512 | +3.2 | +1.9 to +4.5 | +2.8 | yes |
| death (any) | 1056 | -6.0 | -9.6 to -3.1 | -5.3 | yes |
| death: against a spike build | 254 | -3.9 | -8.3 to +2.9 | -2.7 | no |
| death: against other builds | 802 | -6.6 | -11.0 to -2.6 | -6.1 | yes |
| death: back within 20 s | 164 | -2.6 | -7.7 to +2.2 | -1.8 | no |
| death: down 20 to 60 s | 385 | -7.1 | -11.5 to -2.7 | -4.7 | yes |
| death: down 60 s or more | 507 | -6.2 | -10.1 to -2.7 | -6.9 | yes |
| death: healer | 365 | -5.8 | -9.5 to -2.3 | -5.6 | yes |
| death: healer in own base or pit, back within 15 s (likely deliberate) | 23 | -0.8 | -10.8 to +9.7 | -0.7 | no |
| death: healer, other | 342 | -6.2 | -10.0 to -2.7 | -6.0 | yes |
| death: not a healer | 691 | -6.1 | -9.7 to -2.3 | -5.1 | yes |
| pit NPC lost (any): taken by a spike build | 72 | -1.8 | -7.2 to +6.4 | -1.6 | no |
| pit NPC lost (any): taken by other builds | 360 | -2.2 | -5.7 to +1.3 | -1.5 | no |
| pit NPC lost: archer | 243 | +0.7 | -2.2 to +3.9 | +0.0 | no |
| pit NPC lost: bodyguard | 65 | -1.6 | -6.1 to +2.6 | -0.2 | no |
| pit NPC lost: knight | 124 | -7.8 | -14.0 to -2.7 | -5.3 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value.

*deaths* (per 10 s in that state; result worth -6.0 points, base rate 1.4%):

- enemies within 1,500 7.5 to 8: result chance +2.3 points, worth -0.14 win points
- own minus enemy team strength -815 to -529: result chance +1.1 points, worth -0.07 win points
- current health % 1 to 47.5: result chance +10.8 points, worth -0.65 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +3.1 points, worth -0.19 win points
- maximum health after death penalty, as a share of normal 0.4 to 0.66: result chance +4.5 points, worth -0.27 win points
- own healers alive within cast range 0 to 0.5: result chance +0.8 points, worth -0.05 win points
- allies within 1,500 0 to 0.5: result chance +0.8 points, worth -0.05 win points

*kill conversion* (per burst, for the attacking team; result worth +6.0 points, base rate 31.1%):

- target's health ceiling 0.4 to 0.56: result chance +30.9 points, worth +1.85 win points
- target health % when the burst started 0 to 36.5: result chance +23.6 points, worth +1.42 win points
- damage in the 2 s burst 542 to 839: result chance +21.6 points, worth +1.3 win points
- target's healers in range 0 to 0.5: result chance +23.7 points, worth +1.42 win points
- a prot on the target 0.5 to 1: result chance -6.8 points, worth -0.41 win points
- attacking minus target team strength 498.5 to 815: result chance +13.9 points, worth +0.83 win points

*npc loss* (per case, for the defending team; result worth -2.1 points, base rate 19.1%):

- own players in the pit 0 to 0.5: result chance +37.7 points, worth -0.79 win points
- damage on the pit NPCs in the last 5 s 372.5 to 1170: result chance +32.9 points, worth -0.69 win points
- enemy players in the pit 7.5 to 8: result chance +16.4 points, worth -0.34 win points
- own players alive outside the pit 0 to 0.5: result chance +14.7 points, worth -0.31 win points
- of which healers 0 to 0.5: result chance +14.1 points, worth -0.29 win points
- attacking minus defending team strength -415.5 to -316.5: result chance -5.8 points, worth +0.12 win points
- attackers' measured damage per second against a Lord (benchmarks) 17.9 to 19.45: result chance -7.4 points, worth +0.15 win points

