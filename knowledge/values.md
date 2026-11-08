# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

Win points for the team it happened to, from 181 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. Both against matched moments without the event (same minute and win chance). A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 504 | +3.4 | -0.0 to +6.5 | +2.2 | no |
| capture | 1440 | +1.3 | +0.9 to +1.8 | +1.4 | yes |
| capture: held longer | 1219 | +2.3 | +0.8 to +3.6 | +1.5 | yes |
| capture: overcapped within 10 s (Bounty, F36) | 221 | -3.8 | -11.1 to +3.0 | +1.0 | no |
| death (any) | 3486 | -7.6 | -8.8 to -6.5 | -4.7 | yes |
| death: against a spike build | 929 | -7.2 | -10.0 to -4.6 | -3.4 | yes |
| death: against other builds | 2557 | -7.8 | -9.3 to -6.4 | -5.1 | yes |
| death: back within 20 s | 606 | -5.8 | -8.3 to -3.4 | -3.0 | yes |
| death: down 20 to 60 s | 1256 | -7.2 | -8.8 to -5.6 | -3.8 | yes |
| death: down 60 s or more | 1624 | -8.7 | -10.3 to -7.0 | -5.9 | yes |
| death: healer | 1192 | -7.8 | -9.5 to -6.3 | -4.5 | yes |
| death: healer in own base or pit, back within 15 s (possibly deliberate; energy not tracked) | 82 | -3.1 | -4.7 to -1.0 | -0.6 | yes |
| death: healer, other | 1110 | -8.1 | -9.8 to -6.6 | -4.8 | yes |
| death: not a healer | 2294 | -7.6 | -8.8 to -6.4 | -4.7 | yes |
| footman lost (base NPC) | 529 | +1.2 | -0.6 to +3.2 | +0.5 | no |
| pit NPC lost (any): taken by a spike build | 295 | -3.6 | -5.8 to -1.5 | -1.2 | yes |
| pit NPC lost (any): taken by other builds | 1112 | -3.7 | -5.3 to -2.1 | -1.9 | yes |
| pit NPC lost: archer | 797 | -2.2 | -3.5 to -0.7 | -0.3 | yes |
| pit NPC lost: bodyguard | 194 | -5.0 | -7.0 to -3.2 | -2.3 | yes |
| pit NPC lost: knight | 416 | -6.1 | -7.9 to -4.3 | -4.4 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value. Context (strength, build skill counts, flag lead, morale, the clock) is left out: it describes the situation, it is not a cause to fix.

*deaths* (per 10 s in that state; result worth -7.6 points, base rate 1.5%):

- enemies within 1,500 7.5 to 8: result chance +3.0 points, worth -0.23 win points
- current health % 1 to 48.5: result chance +10.9 points, worth -0.83 win points
- allies within 1,500 0 to 0.5: result chance +1.9 points, worth -0.15 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.5 points, worth -0.19 win points

*kill conversion* (per burst, for the attacking team; result worth +7.6 points, base rate 29.6%):

- damage in the 2 s burst 506.5 to 839: result chance +24.6 points, worth +1.87 win points
- target's healers in range 0 to 0.5: result chance +28.7 points, worth +2.18 win points
- target health % when the burst started 0 to 39.5: result chance +23.7 points, worth +1.8 win points
- target's health ceiling 0.4 to 0.69: result chance +29.4 points, worth +2.24 win points
- a prot on the target 0.5 to 1: result chance -4.8 points, worth -0.37 win points

*npc loss* (per case, for the defending team; result worth -3.7 points, base rate 19.5%):

- damage on the pit NPCs in the last 5 s 398.5 to 1370: result chance +39.3 points, worth -1.47 win points
- own players in the pit 0 to 0.5: result chance +35.9 points, worth -1.34 win points
- own players alive outside the pit 0 to 0.5: result chance +18.3 points, worth -0.68 win points
- of which healers 0 to 0.5: result chance +17.5 points, worth -0.65 win points
- attackers' measured damage per second against a Lord (benchmarks) 1.9 to 12.25: result chance -9.8 points, worth +0.37 win points
- enemy players in the pit 7.5 to 8: result chance +7.6 points, worth -0.28 win points
- share of the attacking team's live players in the pit (OG comms: merge before pushing the pit) 0.94 to 1: result chance +5.6 points, worth -0.21 win points

