# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

Win points for the team it happened to, from 40 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 140 | +1.2 | -9.5 to +11.6 | +1.8 | no |
| capture | 416 | +3.5 | +2.0 to +5.3 | +5.3 | yes |
| death (any) | 816 | -5.8 | -10.1 to -1.9 | -5.9 | yes |
| death: against a spike build | 225 | -6.9 | -15.0 to +3.7 | -3.5 | no |
| death: against other builds | 591 | -5.3 | -10.1 to -1.1 | -6.9 | yes |
| death: back within 20 s | 138 | -3.5 | -10.0 to +3.2 | -3.0 | no |
| death: down 20 to 60 s | 294 | -7.2 | -12.3 to -2.1 | -5.2 | yes |
| death: down 60 s or more | 384 | -5.4 | -10.1 to -1.2 | -7.6 | yes |
| death: healer | 271 | -3.1 | -6.6 to +0.3 | -5.4 | no |
| death: healer in own base or pit, back within 15 s (likely deliberate) | 17 | -1.4 | -19.3 to +16.6 | -1.6 | no |
| death: healer, other | 254 | -3.2 | -6.6 to -0.1 | -5.7 | yes |
| death: not a healer | 545 | -7.1 | -12.0 to -2.1 | -6.2 | yes |
| pit NPC lost (any): taken by a spike build | 60 | -0.9 | -7.2 to +8.8 | -0.6 | no |
| pit NPC lost (any): taken by other builds | 267 | -2.9 | -7.8 to +1.4 | -1.6 | no |
| pit NPC lost: archer | 184 | -0.5 | -4.0 to +3.2 | -1.2 | no |
| pit NPC lost: bodyguard | 49 | -0.1 | -5.0 to +4.8 | +1.6 | no |
| pit NPC lost: knight | 94 | -7.8 | -14.5 to -2.3 | -3.6 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value.

*deaths* (per 10 s in that state; result worth -5.8 points, base rate 1.3%):

- enemies within 1,500 7.5 to 8: result chance +2.5 points, worth -0.14 win points
- own minus enemy team strength -267.5 to -122.5: result chance +1.0 points, worth -0.06 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +3.2 points, worth -0.18 win points
- current health % 1 to 47.5: result chance +10.5 points, worth -0.61 win points
- maximum health after death penalty, as a share of normal 0.4 to 0.69: result chance +4.7 points, worth -0.27 win points
- own healers alive within cast range 0 to 0.5: result chance +0.7 points, worth -0.04 win points
- allies within 1,500 0 to 0.5: result chance +0.8 points, worth -0.05 win points

*kill conversion* (per burst, for the attacking team; result worth +5.8 points, base rate 29.2%):

- target's health ceiling 0.4 to 0.56: result chance +38.9 points, worth +2.26 win points
- damage in the 2 s burst 537.5 to 839: result chance +29.6 points, worth +1.72 win points
- target health % when the burst started 0 to 42.5: result chance +20.2 points, worth +1.17 win points
- target's healers in range 0 to 0.5: result chance +31.0 points, worth +1.8 win points
- a prot on the target 0.5 to 1: result chance -9.5 points, worth -0.55 win points
- attacking minus target team strength 426 to 799: result chance +15.9 points, worth +0.92 win points
- match minute 0.3 to 1.35: result chance -9.3 points, worth -0.54 win points
- hexes on the target 8.5 to 12: result chance +43.5 points, worth +2.52 win points

*npc loss* (per case, for the defending team; result worth -2.5 points, base rate 17.2%):

- own players in the pit 7.5 to 8: result chance -15.9 points, worth +0.4 win points
- damage on the pit NPCs in the last 5 s 369.5 to 1170: result chance +30.9 points, worth -0.79 win points
- own players alive outside the pit 0 to 0.5: result chance +23.7 points, worth -0.6 win points
- enemy players in the pit 7.5 to 8: result chance +14.6 points, worth -0.37 win points
- attackers' measured damage per second against a Lord (benchmarks) 2.5 to 17.15: result chance -8.0 points, worth +0.2 win points
- attacking minus defending team strength 106 to 159.5: result chance +10.2 points, worth -0.26 win points

