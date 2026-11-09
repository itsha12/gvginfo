# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

Win points for the team it happened to, from 266 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. Both against matched moments without the event (same minute and win chance). A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 772 | +5.7 | +2.7 to +8.4 | +1.9 | yes |
| capture | 2464 | +2.2 | +1.8 to +2.5 | +2.8 | yes |
| capture: held longer | 2112 | +3.0 | +1.9 to +3.9 | +3.1 | yes |
| capture: overcapped within 10 s (Bounty, F36) | 352 | -2.3 | -8.2 to +4.2 | +0.9 | no |
| death (any) | 5259 | -8.6 | -9.8 to -7.4 | -4.5 | yes |
| death: against a spike build | 1610 | -7.8 | -11.1 to -4.0 | -4.3 | yes |
| death: against other builds | 3649 | -9.0 | -10.5 to -7.6 | -4.6 | yes |
| death: back within 20 s | 885 | -8.1 | -10.4 to -6.0 | -2.2 | yes |
| death: down 20 to 60 s | 1846 | -7.8 | -9.4 to -6.0 | -3.9 | yes |
| death: down 60 s or more | 2528 | -9.4 | -11.1 to -7.8 | -5.8 | yes |
| death: healer | 1782 | -8.6 | -10.2 to -6.9 | -4.5 | yes |
| death: healer in own base or pit, back within 15 s (possibly deliberate; energy not tracked) | 116 | -4.3 | -6.4 to -2.1 | -1.8 | yes |
| death: healer, other | 1666 | -8.9 | -10.6 to -7.4 | -4.6 | yes |
| death: not a healer | 3477 | -8.6 | -10.0 to -7.4 | -4.5 | yes |
| footman lost (base NPC) | 762 | -1.7 | -3.5 to -0.1 | -0.1 | yes |
| pit NPC lost (any): taken by a spike build | 506 | -4.6 | -9.2 to +0.3 | -2.2 | no |
| pit NPC lost (any): taken by other builds | 1648 | -5.9 | -7.8 to -4.3 | -2.7 | yes |
| pit NPC lost: archer | 1225 | -4.2 | -5.4 to -2.8 | -1.0 | yes |
| pit NPC lost: bodyguard | 288 | -5.6 | -7.1 to -4.1 | -1.9 | yes |
| pit NPC lost: knight | 641 | -8.4 | -9.8 to -7.1 | -5.7 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value. Context (strength, build skill counts, flag lead, morale, the clock) is left out: it describes the situation, it is not a cause to fix.

*deaths* (per 10 s in that state; result worth -8.6 points, base rate 1.5%):

- enemies within 1,500 7.5 to 8: result chance +2.8 points, worth -0.24 win points
- current health % 1 to 48.5: result chance +11.2 points, worth -0.97 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.6 points, worth -0.23 win points
- allies within 1,500 0 to 0.5: result chance +2.0 points, worth -0.18 win points
- own healers alive within cast range (other than the player) 3.5 to 4: result chance +0.4 points, worth -0.03 win points

*kill conversion* (per burst, for the attacking team; result worth +8.6 points, base rate 28.9%):

- target's healers in range 0 to 0.5: result chance +30.4 points, worth +2.62 win points
- target's health ceiling 0.4 to 0.56: result chance +37.8 points, worth +3.25 win points
- damage in the 2 s burst 506.5 to 840: result chance +25.8 points, worth +2.22 win points
- target health % when the burst started 0 to 38.5: result chance +30.8 points, worth +2.65 win points
- a prot on the target 0.5 to 1: result chance -6.7 points, worth -0.58 win points

*npc loss* (per case, for the defending team; result worth -5.6 points, base rate 19.9%):

- own players in the pit 7.5 to 8: result chance -15.4 points, worth +0.87 win points
- damage on the pit NPCs in the last 5 s 387.5 to 1370: result chance +37.3 points, worth -2.1 win points
- own players alive outside the pit 0 to 0.5: result chance +17.4 points, worth -0.98 win points
- attackers' measured damage per second against a Lord (benchmarks) 2.7 to 21.35: result chance -10.6 points, worth +0.6 win points
- of which healers 0 to 0.5: result chance +17.3 points, worth -0.97 win points
- enemy players in the pit 7.5 to 8: result chance +5.3 points, worth -0.3 win points
- healing on own pit NPCs and Lord in the last 10 s 623.5 to 1801: result chance -6.3 points, worth +0.36 win points

