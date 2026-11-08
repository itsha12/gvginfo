# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

Win points for the team it happened to, from 133 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. Both against matched moments without the event (same minute and win chance). A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 396 | +5.8 | +1.4 to +9.8 | +2.6 | yes |
| capture | 1150 | +1.7 | +1.2 to +2.1 | +1.6 | yes |
| death (any) | 2596 | -9.5 | -11.2 to -7.9 | -5.5 | yes |
| death: against a spike build | 820 | -8.6 | -12.1 to -4.7 | -3.9 | yes |
| death: against other builds | 1776 | -9.9 | -12.3 to -7.8 | -6.2 | yes |
| death: back within 20 s | 438 | -8.7 | -11.9 to -5.5 | -4.2 | yes |
| death: down 20 to 60 s | 946 | -10.3 | -13.0 to -7.7 | -4.9 | yes |
| death: down 60 s or more | 1212 | -9.3 | -11.1 to -7.5 | -6.5 | yes |
| death: healer | 875 | -10.2 | -12.4 to -7.8 | -6.0 | yes |
| death: healer in own base or pit, back within 15 s (possibly deliberate; energy not tracked) | 54 | -8.0 | -13.9 to -2.5 | -2.1 | yes |
| death: healer, other | 821 | -10.3 | -12.7 to -8.2 | -6.2 | yes |
| death: not a healer | 1721 | -9.2 | -10.9 to -7.5 | -5.2 | yes |
| footman lost (base NPC) | 390 | +0.7 | -1.8 to +3.3 | +0.6 | no |
| pit NPC lost (any): taken by a spike build | 255 | -5.0 | -8.0 to -1.9 | -1.8 | yes |
| pit NPC lost (any): taken by other builds | 799 | -5.9 | -8.3 to -3.5 | -2.5 | yes |
| pit NPC lost: archer | 603 | -3.3 | -5.1 to -1.3 | -0.4 | yes |
| pit NPC lost: bodyguard | 143 | -8.5 | -11.1 to -5.9 | -3.5 | yes |
| pit NPC lost: knight | 308 | -9.1 | -11.5 to -6.7 | -5.6 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value. Context (strength, build skill counts, flag lead, morale, the clock) is left out: it describes the situation, it is not a cause to fix.

*deaths* (per 10 s in that state; result worth -9.5 points, base rate 1.5%):

- enemies within 1,500 7.5 to 8: result chance +3.1 points, worth -0.29 win points
- current health % 1 to 48.5: result chance +10.9 points, worth -1.04 win points
- allies within 1,500 0 to 0.5: result chance +1.9 points, worth -0.18 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.5 points, worth -0.24 win points

*kill conversion* (per burst, for the attacking team; result worth +9.5 points, base rate 29.6%):

- damage in the 2 s burst 506.5 to 839: result chance +24.6 points, worth +2.34 win points
- target's healers in range 0 to 0.5: result chance +28.7 points, worth +2.73 win points
- target health % when the burst started 0 to 39.5: result chance +23.7 points, worth +2.25 win points
- target's health ceiling 0.4 to 0.69: result chance +29.4 points, worth +2.79 win points
- a prot on the target 0.5 to 1: result chance -4.8 points, worth -0.46 win points

*npc loss* (per case, for the defending team; result worth -5.7 points, base rate 19.5%):

- damage on the pit NPCs in the last 5 s 398.5 to 1370: result chance +39.3 points, worth -2.24 win points
- own players in the pit 0 to 0.5: result chance +35.9 points, worth -2.05 win points
- own players alive outside the pit 0 to 0.5: result chance +18.3 points, worth -1.04 win points
- of which healers 0 to 0.5: result chance +17.5 points, worth -1.0 win points
- attackers' measured damage per second against a Lord (benchmarks) 1.9 to 12.25: result chance -9.8 points, worth +0.56 win points
- enemy players in the pit 7.5 to 8: result chance +7.6 points, worth -0.43 win points
- share of the attacking team's live players in the pit (OG comms: merge before pushing the pit) 0.94 to 1: result chance +5.7 points, worth -0.33 win points

