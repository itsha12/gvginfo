# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

Win points for the team it happened to, from 221 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. Both against matched moments without the event (same minute and win chance). A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 652 | +5.0 | +1.5 to +8.1 | +1.7 | yes |
| capture | 2054 | +1.8 | +1.3 to +2.2 | +2.5 | yes |
| capture: held longer | 1748 | +2.2 | +1.0 to +3.3 | +2.8 | yes |
| capture: overcapped within 10 s (Bounty, F36) | 306 | -0.6 | -6.9 to +5.6 | +0.9 | no |
| death (any) | 4382 | -7.7 | -9.0 to -6.4 | -4.3 | yes |
| death: against a spike build | 1377 | -7.0 | -10.2 to -3.4 | -3.8 | yes |
| death: against other builds | 3005 | -8.0 | -9.7 to -6.5 | -4.5 | yes |
| death: back within 20 s | 750 | -7.4 | -9.6 to -5.2 | -1.8 | yes |
| death: down 20 to 60 s | 1542 | -7.2 | -9.2 to -5.3 | -3.9 | yes |
| death: down 60 s or more | 2090 | -8.1 | -9.7 to -6.4 | -5.5 | yes |
| death: healer | 1482 | -7.6 | -9.6 to -5.9 | -4.2 | yes |
| death: healer in own base or pit, back within 15 s (possibly deliberate; energy not tracked) | 100 | -3.4 | -6.2 to -0.8 | -0.7 | yes |
| death: healer, other | 1382 | -7.9 | -9.8 to -6.1 | -4.5 | yes |
| death: not a healer | 2900 | -7.7 | -9.0 to -6.4 | -4.3 | yes |
| footman lost (base NPC) | 621 | -1.6 | -3.4 to +0.1 | +0.1 | no |
| pit NPC lost (any): taken by a spike build | 415 | -5.2 | -9.0 to -1.5 | -1.9 | yes |
| pit NPC lost (any): taken by other builds | 1335 | -5.4 | -7.1 to -3.9 | -3.0 | yes |
| pit NPC lost: archer | 991 | -3.8 | -5.0 to -2.4 | -0.8 | yes |
| pit NPC lost: bodyguard | 237 | -5.7 | -7.4 to -4.3 | -2.9 | yes |
| pit NPC lost: knight | 522 | -8.3 | -9.7 to -6.8 | -6.4 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value. Context (strength, build skill counts, flag lead, morale, the clock) is left out: it describes the situation, it is not a cause to fix.

*deaths* (per 10 s in that state; result worth -7.7 points, base rate 1.6%):

- enemies within 1,500 7.5 to 8: result chance +2.7 points, worth -0.21 win points
- current health % 1 to 47.5: result chance +11.0 points, worth -0.85 win points
- allies within 1,500 0 to 0.5: result chance +2.2 points, worth -0.17 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.7 points, worth -0.21 win points
- distance from its own pit 13552.5 to 18468: result chance +0.6 points, worth -0.05 win points

*kill conversion* (per burst, for the attacking team; result worth +7.7 points, base rate 31.0%):

- target's healers in range 0 to 0.5: result chance +34.3 points, worth +2.64 win points
- damage in the 2 s burst 499.5 to 839: result chance +30.6 points, worth +2.35 win points
- target's health ceiling 0.4 to 0.69: result chance +37.2 points, worth +2.87 win points
- target health % when the burst started 0 to 38.5: result chance +28.1 points, worth +2.17 win points
- a prot on the target 0.5 to 1: result chance -6.6 points, worth -0.51 win points

*npc loss* (per case, for the defending team; result worth -5.4 points, base rate 21.1%):

- damage on the pit NPCs in the last 5 s 389.5 to 1370: result chance +40.1 points, worth -2.16 win points
- own players in the pit 7.5 to 8: result chance -16.1 points, worth +0.87 win points
- own players alive outside the pit 0 to 0.5: result chance +20.0 points, worth -1.08 win points
- of which healers 0 to 0.5: result chance +17.9 points, worth -0.97 win points
- attackers' measured damage per second against a Lord (benchmarks) 1.9 to 12.55: result chance -5.7 points, worth +0.31 win points
- enemy players in the pit 7.5 to 8: result chance +7.0 points, worth -0.38 win points
- healing on own pit NPCs and Lord in the last 10 s 639.5 to 1801: result chance -7.5 points, worth +0.4 win points

