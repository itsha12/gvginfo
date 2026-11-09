# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

Win points for the team it happened to, from 311 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. Both against matched moments without the event (same minute and win chance). A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 880 | +4.6 | +1.9 to +7.5 | +1.7 | yes |
| capture | 2863 | +2.2 | +1.8 to +2.5 | +2.8 | yes |
| capture: held longer | 2458 | +2.9 | +2.0 to +3.9 | +3.1 | yes |
| capture: overcapped within 10 s (Bounty, F36) | 405 | -2.2 | -7.7 to +3.4 | +1.1 | no |
| death (any) | 6260 | -7.9 | -9.0 to -6.9 | -4.1 | yes |
| death: against a spike build | 1902 | -7.0 | -9.8 to -3.6 | -4.0 | yes |
| death: against other builds | 4358 | -8.4 | -9.7 to -7.0 | -4.1 | yes |
| death: back within 20 s | 1039 | -7.5 | -9.3 to -5.8 | -2.4 | yes |
| death: down 20 to 60 s | 2227 | -7.3 | -8.8 to -5.7 | -3.6 | yes |
| death: down 60 s or more | 2994 | -8.6 | -10.1 to -7.2 | -5.0 | yes |
| death: healer | 2110 | -7.8 | -9.1 to -6.4 | -4.0 | yes |
| death: healer in own base or pit, back within 15 s (possibly deliberate; energy not tracked) | 135 | -3.9 | -5.9 to -1.7 | -1.7 | yes |
| death: healer, other | 1975 | -8.1 | -9.4 to -6.5 | -4.1 | yes |
| death: not a healer | 4150 | -8.0 | -9.2 to -6.9 | -4.2 | yes |
| footman lost (base NPC) | 875 | +1.0 | -0.5 to +2.6 | +3.6 | no |
| pit NPC lost (any): taken by a spike build | 573 | -4.2 | -7.9 to -0.6 | -2.2 | yes |
| pit NPC lost (any): taken by other builds | 1943 | -5.4 | -6.9 to -4.1 | -2.6 | yes |
| pit NPC lost: archer | 1436 | -3.7 | -4.8 to -2.5 | -0.9 | yes |
| pit NPC lost: bodyguard | 335 | -5.0 | -6.6 to -3.6 | -1.6 | yes |
| pit NPC lost: knight | 745 | -7.9 | -9.2 to -6.7 | -6.1 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value. Context (strength, build skill counts, flag lead, morale, the clock) is left out: it describes the situation, it is not a cause to fix.

*deaths* (per 10 s in that state; result worth -7.9 points, base rate 1.5%):

- enemies within 1,500 7.5 to 8: result chance +2.9 points, worth -0.23 win points
- current health % 1 to 48.5: result chance +11.2 points, worth -0.89 win points
- allies within 1,500 0 to 0.5: result chance +2.1 points, worth -0.17 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.6 points, worth -0.21 win points
- distance from its own pit 13289.5 to 18468: result chance +0.6 points, worth -0.05 win points
- a prot (Guardian, Spirit Bond, Life Sheath, Protective Spirit...) on the player now 0.5 to 1: result chance -0.4 points, worth +0.03 win points

*kill conversion* (per burst, for the attacking team; result worth +7.9 points, base rate 28.5%):

- target's healers in range 0 to 0.5: result chance +33.4 points, worth +2.64 win points
- target's health ceiling 0.4 to 0.56: result chance +41.3 points, worth +3.26 win points
- damage in the 2 s burst 505.5 to 1069: result chance +25.0 points, worth +1.98 win points
- target health % when the burst started 0 to 38.5: result chance +31.1 points, worth +2.45 win points
- a prot on the target 0.5 to 1: result chance -6.6 points, worth -0.52 win points
- attackers in the burst 6.5 to 7: result chance -4.9 points, worth -0.38 win points

*npc loss* (per case, for the defending team; result worth -5.1 points, base rate 20.3%):

- own players in the pit 0 to 0.5: result chance +37.6 points, worth -1.93 win points
- damage on the pit NPCs in the last 5 s 385.5 to 1370: result chance +37.8 points, worth -1.94 win points
- own players alive outside the pit 0 to 0.5: result chance +19.3 points, worth -0.99 win points
- attackers' measured damage per second against a Lord (benchmarks) 2.7 to 17.95: result chance -11.7 points, worth +0.6 win points
- of which healers 0 to 0.5: result chance +18.2 points, worth -0.93 win points
- enemy players in the pit 7.5 to 8: result chance +5.6 points, worth -0.29 win points
- healing on own pit NPCs and Lord in the last 10 s 610.5 to 1801: result chance -6.2 points, worth +0.32 win points

