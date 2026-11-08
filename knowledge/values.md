# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

Win points for the team it happened to, from 133 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. Both against matched moments without the event (same minute and win chance). A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 396 | +5.4 | +1.3 to +9.2 | +2.7 | yes |
| capture | 1150 | +1.5 | +1.0 to +2.0 | +1.6 | yes |
| death (any) | 2596 | -9.2 | -10.7 to -7.6 | -5.4 | yes |
| death: against a spike build | 820 | -8.2 | -11.6 to -4.4 | -3.9 | yes |
| death: against other builds | 1776 | -9.7 | -11.9 to -7.6 | -6.1 | yes |
| death: back within 20 s | 438 | -8.8 | -12.0 to -5.6 | -4.2 | yes |
| death: down 20 to 60 s | 946 | -9.9 | -12.4 to -7.4 | -4.8 | yes |
| death: down 60 s or more | 1212 | -8.8 | -10.6 to -7.1 | -6.2 | yes |
| death: healer | 875 | -10.0 | -12.1 to -7.7 | -5.8 | yes |
| death: healer in own base or pit, back within 15 s (possibly deliberate; energy not tracked) | 54 | -7.5 | -13.1 to -2.1 | -1.8 | yes |
| death: healer, other | 821 | -10.1 | -12.4 to -8.0 | -6.1 | yes |
| death: not a healer | 1721 | -8.8 | -10.5 to -7.2 | -5.1 | yes |
| footman lost (base NPC) | 390 | +0.5 | -2.0 to +3.1 | +0.6 | no |
| pit NPC lost (any): taken by a spike build | 255 | -4.8 | -7.9 to -1.6 | -1.8 | yes |
| pit NPC lost (any): taken by other builds | 799 | -6.2 | -8.6 to -3.8 | -2.4 | yes |
| pit NPC lost: archer | 603 | -3.6 | -5.4 to -1.6 | -0.5 | yes |
| pit NPC lost: bodyguard | 143 | -8.4 | -11.1 to -5.8 | -3.3 | yes |
| pit NPC lost: knight | 308 | -9.2 | -11.7 to -6.8 | -5.4 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value. Context (strength, build skill counts, flag lead, morale, the clock) is left out: it describes the situation, it is not a cause to fix.

*deaths* (per 10 s in that state; result worth -9.2 points, base rate 1.5%):

- enemies within 1,500 7.5 to 8: result chance +3.1 points, worth -0.28 win points
- current health % 1 to 48.5: result chance +10.9 points, worth -1.0 win points
- allies within 1,500 0 to 0.5: result chance +1.9 points, worth -0.18 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.5 points, worth -0.23 win points

*kill conversion* (per burst, for the attacking team; result worth +9.2 points, base rate 29.6%):

- damage in the 2 s burst 506.5 to 839: result chance +25.5 points, worth +2.35 win points
- target's healers in range 0 to 0.5: result chance +29.6 points, worth +2.72 win points
- target health % when the burst started 0 to 39.5: result chance +24.2 points, worth +2.23 win points
- target's health ceiling 0.4 to 0.69: result chance +30.1 points, worth +2.77 win points
- a prot on the target 0.5 to 1: result chance -5.1 points, worth -0.47 win points

*npc loss* (per case, for the defending team; result worth -5.9 points, base rate 19.5%):

- damage on the pit NPCs in the last 5 s 398.5 to 1370: result chance +39.3 points, worth -2.32 win points
- own players in the pit 0 to 0.5: result chance +35.9 points, worth -2.12 win points
- own players alive outside the pit 0 to 0.5: result chance +18.3 points, worth -1.08 win points
- of which healers 0 to 0.5: result chance +17.5 points, worth -1.03 win points
- attackers' measured damage per second against a Lord (benchmarks) 1.9 to 12.25: result chance -9.8 points, worth +0.58 win points
- enemy players in the pit 7.5 to 8: result chance +7.6 points, worth -0.45 win points
- share of the attacking team's live players in the pit (OG comms: merge before pushing the pit) 0.94 to 1: result chance +5.7 points, worth -0.34 win points

