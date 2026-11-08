# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

Win points for the team it happened to, from 228 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. Both against matched moments without the event (same minute and win chance). A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 628 | +5.1 | +1.8 to +8.5 | +1.7 | yes |
| capture | 1870 | +1.9 | +1.4 to +2.4 | +2.2 | yes |
| capture: held longer | 1577 | +2.2 | +0.8 to +3.5 | +2.4 | yes |
| capture: overcapped within 10 s (Bounty, F36) | 293 | +0.4 | -7.0 to +7.6 | +0.6 | no |
| death (any) | 4427 | -7.7 | -9.0 to -6.4 | -4.6 | yes |
| death: against a spike build | 1178 | -7.3 | -11.7 to -3.0 | -4.4 | yes |
| death: against other builds | 3249 | -7.8 | -9.4 to -6.4 | -4.7 | yes |
| death: back within 20 s | 751 | -7.1 | -9.5 to -4.9 | -2.5 | yes |
| death: down 20 to 60 s | 1573 | -6.8 | -8.4 to -5.0 | -3.8 | yes |
| death: down 60 s or more | 2103 | -8.5 | -10.3 to -7.0 | -6.0 | yes |
| death: healer | 1514 | -7.4 | -9.3 to -5.5 | -4.5 | yes |
| death: healer in own base or pit, back within 15 s (possibly deliberate; energy not tracked) | 105 | -3.4 | -5.8 to -0.9 | -0.3 | yes |
| death: healer, other | 1409 | -7.7 | -9.6 to -5.9 | -4.8 | yes |
| death: not a healer | 2913 | -7.8 | -9.3 to -6.7 | -4.7 | yes |
| footman lost (base NPC) | 637 | -0.4 | -2.4 to +1.4 | +0.0 | no |
| pit NPC lost (any): taken by a spike build | 369 | -5.0 | -9.3 to -0.3 | -1.8 | yes |
| pit NPC lost (any): taken by other builds | 1391 | -4.6 | -6.2 to -3.2 | -2.5 | yes |
| pit NPC lost: archer | 988 | -3.7 | -4.9 to -2.2 | -0.8 | yes |
| pit NPC lost: bodyguard | 247 | -4.6 | -6.3 to -2.9 | -1.7 | yes |
| pit NPC lost: knight | 525 | -6.7 | -8.0 to -5.3 | -5.6 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value. Context (strength, build skill counts, flag lead, morale, the clock) is left out: it describes the situation, it is not a cause to fix.

*deaths* (per 10 s in that state; result worth -7.7 points, base rate 1.5%):

- enemies within 1,500 7.5 to 8: result chance +2.7 points, worth -0.2 win points
- current health % 1 to 47.5: result chance +11.6 points, worth -0.89 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.9 points, worth -0.22 win points
- allies within 1,500 0 to 0.5: result chance +2.1 points, worth -0.17 win points

*kill conversion* (per burst, for the attacking team; result worth +7.7 points, base rate 30.8%):

- target's healers in range 0 to 0.5: result chance +29.2 points, worth +2.25 win points
- damage in the 2 s burst 500.5 to 839: result chance +24.2 points, worth +1.86 win points
- target health % when the burst started 0 to 40.5: result chance +28.1 points, worth +2.16 win points
- target's health ceiling 0.4 to 0.69: result chance +28.1 points, worth +2.16 win points
- a prot on the target 0.5 to 1: result chance -6.2 points, worth -0.48 win points

*npc loss* (per case, for the defending team; result worth -4.7 points, base rate 20.5%):

- damage on the pit NPCs in the last 5 s 398.5 to 1370: result chance +39.8 points, worth -1.88 win points
- own players in the pit 0 to 0.5: result chance +36.1 points, worth -1.71 win points
- own players alive outside the pit 0 to 0.5: result chance +19.7 points, worth -0.93 win points
- enemy players in the pit 7.5 to 8: result chance +10.1 points, worth -0.48 win points
- of which healers 0 to 0.5: result chance +18.3 points, worth -0.87 win points
- attackers' measured damage per second against a Lord (benchmarks) 1.9 to 14.15: result chance -6.1 points, worth +0.29 win points
- healing on own pit NPCs and Lord in the last 10 s 649 to 1801: result chance -7.5 points, worth +0.35 win points

