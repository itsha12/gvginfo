# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

Win points for the team it happened to, from 356 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. Both against matched moments without the event (same minute and win chance). A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 1011 | +5.2 | +2.7 to +7.6 | +2.0 | yes |
| capture | 3247 | +2.5 | +2.2 to +2.9 | +3.3 | yes |
| capture: held longer | 2800 | +3.3 | +2.4 to +4.2 | +3.6 | yes |
| capture: overcapped within 10 s (Bounty, F36) | 447 | -2.4 | -7.9 to +3.1 | +1.1 | no |
| death (any) | 7194 | -7.9 | -8.8 to -7.0 | -4.8 | yes |
| death: against a spike build | 2089 | -8.1 | -11.1 to -5.2 | -4.7 | yes |
| death: against other builds | 5105 | -7.8 | -9.0 to -6.8 | -4.8 | yes |
| death: back within 20 s | 1203 | -7.2 | -9.0 to -5.5 | -2.5 | yes |
| death: down 20 to 60 s | 2552 | -6.9 | -8.4 to -5.6 | -4.3 | yes |
| death: down 60 s or more | 3439 | -8.9 | -10.2 to -7.6 | -5.9 | yes |
| death: healer | 2428 | -7.5 | -8.7 to -6.2 | -4.7 | yes |
| death: healer in own base or pit, back within 15 s (possibly deliberate; energy not tracked) | 153 | -3.4 | -5.1 to -1.4 | -1.6 | yes |
| death: healer, other | 2275 | -7.8 | -9.0 to -6.5 | -4.9 | yes |
| death: not a healer | 4766 | -8.1 | -9.2 to -7.0 | -4.8 | yes |
| footman lost (base NPC) | 998 | +1.3 | -0.2 to +2.8 | +4.6 | no |
| pit NPC lost (any): taken by a spike build | 619 | -3.8 | -7.6 to +0.1 | -2.3 | no |
| pit NPC lost (any): taken by other builds | 2243 | -4.7 | -6.0 to -3.3 | -2.2 | yes |
| pit NPC lost: archer | 1624 | -3.3 | -4.4 to -2.3 | -0.6 | yes |
| pit NPC lost: bodyguard | 379 | -4.8 | -5.8 to -3.7 | -2.2 | yes |
| pit NPC lost: knight | 859 | -6.5 | -7.7 to -5.4 | -5.4 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value. Context (strength, build skill counts, flag lead, morale, the clock) is left out: it describes the situation, it is not a cause to fix.

*deaths* (per 10 s in that state; result worth -7.9 points, base rate 1.5%):

- enemies within 1,500 7.5 to 8: result chance +2.9 points, worth -0.23 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.7 points, worth -0.21 win points
- allies within 1,500 0 to 0.5: result chance +2.2 points, worth -0.17 win points
- current health % 1 to 49.5: result chance +9.9 points, worth -0.78 win points
- a prot (Guardian, Spirit Bond, Life Sheath, Protective Spirit...) on the player now 0.5 to 1: result chance -0.4 points, worth +0.03 win points
- distance from its own pit 13260.5 to 18468: result chance +0.7 points, worth -0.06 win points

*kill conversion* (per burst, for the attacking team; result worth +7.9 points, base rate 28.7%):

- target's health ceiling 0.4 to 0.56: result chance +43.9 points, worth +3.47 win points
- damage in the 2 s burst 508.5 to 1069: result chance +27.6 points, worth +2.18 win points
- target's healers in range 0 to 0.5: result chance +34.3 points, worth +2.71 win points
- target health % when the burst started 0 to 37.5: result chance +34.0 points, worth +2.69 win points
- a prot on the target 0.5 to 1: result chance -7.8 points, worth -0.62 win points

*npc loss* (per case, for the defending team; result worth -4.5 points, base rate 20.8%):

- own players in the pit 0 to 0.5: result chance +37.7 points, worth -1.68 win points
- damage on the pit NPCs in the last 5 s 386.5 to 1370: result chance +35.6 points, worth -1.59 win points
- own players alive outside the pit 0 to 0.5: result chance +17.8 points, worth -0.79 win points
- attackers' measured damage per second against a Lord (benchmarks) 2.7 to 21.1: result chance -12.2 points, worth +0.54 win points
- of which healers 0 to 0.5: result chance +18.2 points, worth -0.81 win points
- enemy players in the pit 1 to 1.5: result chance -4.7 points, worth +0.21 win points
- healing on own pit NPCs and Lord in the last 10 s 621.5 to 2034: result chance -7.4 points, worth +0.33 win points

