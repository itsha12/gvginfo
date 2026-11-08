# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

Win points for the team it happened to, from 133 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. Both against matched moments without the event (same minute and win chance). A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 396 | +6.2 | +1.8 to +10.2 | +2.4 | yes |
| capture | 1150 | +1.5 | +1.0 to +2.1 | +1.6 | yes |
| capture: held longer | 980 | +2.4 | +0.7 to +3.7 | +1.7 | yes |
| capture: overcapped within 10 s (Bounty, F36) | 170 | -3.2 | -11.1 to +5.1 | +0.8 | no |
| death (any) | 2596 | -9.6 | -11.2 to -8.0 | -5.4 | yes |
| death: against a spike build | 820 | -10.2 | -13.9 to -6.2 | -4.3 | yes |
| death: against other builds | 1776 | -9.3 | -11.6 to -7.1 | -6.0 | yes |
| death: back within 20 s | 438 | -9.9 | -13.4 to -6.3 | -4.5 | yes |
| death: down 20 to 60 s | 946 | -10.2 | -12.9 to -7.6 | -4.7 | yes |
| death: down 60 s or more | 1212 | -9.0 | -10.9 to -7.2 | -6.3 | yes |
| death: healer | 875 | -10.2 | -12.5 to -8.0 | -5.9 | yes |
| death: healer in own base or pit, back within 15 s (possibly deliberate; energy not tracked) | 54 | -9.1 | -15.3 to -2.7 | -2.8 | yes |
| death: healer, other | 821 | -10.2 | -12.6 to -8.0 | -6.1 | yes |
| death: not a healer | 1721 | -9.3 | -11.1 to -7.6 | -5.2 | yes |
| footman lost (base NPC) | 390 | +1.3 | -1.4 to +3.6 | +0.6 | no |
| pit NPC lost (any): taken by a spike build | 255 | -6.7 | -10.1 to -3.5 | -2.2 | yes |
| pit NPC lost (any): taken by other builds | 799 | -5.1 | -7.2 to -2.9 | -2.1 | yes |
| pit NPC lost: archer | 603 | -3.6 | -5.5 to -1.5 | -0.3 | yes |
| pit NPC lost: bodyguard | 143 | -7.8 | -10.4 to -5.3 | -3.3 | yes |
| pit NPC lost: knight | 308 | -8.1 | -10.5 to -6.1 | -5.2 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value. Context (strength, build skill counts, flag lead, morale, the clock) is left out: it describes the situation, it is not a cause to fix.

*deaths* (per 10 s in that state; result worth -9.6 points, base rate 1.5%):

- enemies within 1,500 7.5 to 8: result chance +3.0 points, worth -0.29 win points
- current health % 1 to 48.5: result chance +10.9 points, worth -1.05 win points
- allies within 1,500 0 to 0.5: result chance +1.9 points, worth -0.18 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.5 points, worth -0.24 win points

*kill conversion* (per burst, for the attacking team; result worth +9.6 points, base rate 29.6%):

- damage in the 2 s burst 506.5 to 839: result chance +25.5 points, worth +2.45 win points
- target's healers in range 0 to 0.5: result chance +29.6 points, worth +2.84 win points
- target health % when the burst started 0 to 39.5: result chance +24.2 points, worth +2.33 win points
- target's health ceiling 0.4 to 0.69: result chance +30.1 points, worth +2.89 win points
- a prot on the target 0.5 to 1: result chance -5.1 points, worth -0.49 win points

*npc loss* (per case, for the defending team; result worth -5.5 points, base rate 19.5%):

- damage on the pit NPCs in the last 5 s 398.5 to 1370: result chance +39.3 points, worth -2.16 win points
- own players in the pit 0 to 0.5: result chance +35.9 points, worth -1.97 win points
- own players alive outside the pit 0 to 0.5: result chance +18.3 points, worth -1.0 win points
- of which healers 0 to 0.5: result chance +17.5 points, worth -0.96 win points
- attackers' measured damage per second against a Lord (benchmarks) 1.9 to 12.25: result chance -9.8 points, worth +0.54 win points
- enemy players in the pit 7.5 to 8: result chance +7.6 points, worth -0.41 win points
- share of the attacking team's live players in the pit (OG comms: merge before pushing the pit) 0.94 to 1: result chance +5.6 points, worth -0.31 win points

