# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

Win points for the team it happened to, from 133 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 396 | +1.1 | -3.4 to +5.4 | +2.8 | no |
| capture | 1150 | +1.7 | +1.2 to +2.3 | +1.3 | yes |
| death (any) | 2596 | -5.0 | -6.5 to -3.6 | -4.1 | yes |
| death: against a spike build | 820 | -4.9 | -8.7 to -1.6 | -3.2 | yes |
| death: against other builds | 1776 | -5.0 | -6.9 to -3.2 | -4.5 | yes |
| death: back within 20 s | 438 | -5.0 | -7.9 to -2.2 | -3.6 | yes |
| death: down 20 to 60 s | 946 | -4.9 | -7.3 to -2.8 | -3.5 | yes |
| death: down 60 s or more | 1212 | -5.0 | -6.9 to -3.2 | -4.8 | yes |
| death: healer | 875 | -5.6 | -7.7 to -3.6 | -4.5 | yes |
| death: healer in own base or pit, back within 15 s (likely deliberate) | 54 | -1.3 | -4.9 to +2.6 | -0.4 | no |
| death: healer, other | 821 | -5.9 | -7.9 to -3.8 | -4.7 | yes |
| death: not a healer | 1721 | -4.7 | -6.3 to -3.1 | -3.9 | yes |
| death: team boosted (morale above zero) | 263 | -19.8 | -29.5 to -11.0 | -8.3 | yes |
| death: team not boosted | 2333 | -3.3 | -5.5 to -1.2 | -3.6 | yes |
| footman lost (base NPC) | 390 | +1.9 | -0.7 to +4.4 | +0.9 | no |
| pit NPC lost (any): taken by a spike build | 255 | -1.9 | -5.7 to +1.4 | -0.1 | no |
| pit NPC lost (any): taken by other builds | 799 | -2.6 | -4.9 to -0.3 | -1.7 | yes |
| pit NPC lost: archer | 603 | -0.9 | -2.8 to +1.1 | +0.4 | no |
| pit NPC lost: bodyguard | 143 | -3.8 | -6.0 to -1.6 | -2.9 | yes |
| pit NPC lost: knight | 308 | -4.8 | -7.3 to -2.5 | -3.8 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value.

*deaths* (per 10 s in that state; result worth -5.0 points, base rate 1.5%):

- enemies within 1,500 7.5 to 8: result chance +3.3 points, worth -0.17 win points
- own minus enemy team strength 353.5 to 434.5: result chance -0.9 points, worth +0.04 win points
- current health % 1 to 48.5: result chance +11.2 points, worth -0.56 win points
- allies within 1,500 0 to 0.5: result chance +1.9 points, worth -0.1 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.5 points, worth -0.13 win points
- enemy enchantment removal skills 0 to 0.5: result chance +2.9 points, worth -0.15 win points
- own prot skills 6.5 to 7.5: result chance +0.7 points, worth -0.04 win points
- distance from its own pit 13437.5 to 18468: result chance +0.9 points, worth -0.04 win points

*kill conversion* (per burst, for the attacking team; result worth +5.0 points, base rate 29.8%):

- damage in the 2 s burst 508.5 to 839: result chance +27.1 points, worth +1.36 win points
- target's healers in range 0 to 0.5: result chance +32.1 points, worth +1.61 win points
- attacking minus target team strength 623 to 989: result chance +24.9 points, worth +1.25 win points
- target health % when the burst started 0 to 37.5: result chance +22.4 points, worth +1.12 win points
- target's health ceiling 0.4 to 0.69: result chance +32.1 points, worth +1.61 win points
- target team's prot skills 16.5 to 17: result chance -16.2 points, worth -0.81 win points
- a prot on the target 0.5 to 1: result chance -4.6 points, worth -0.23 win points
- attackers' interrupt skills minus target team's heals -3.5 to 1: result chance -10.4 points, worth -0.52 win points

*npc loss* (per case, for the defending team; result worth -2.4 points, base rate 20.1%):

- damage on the pit NPCs in the last 5 s 397.5 to 1370: result chance +38.1 points, worth -0.93 win points
- own players in the pit 0 to 0.5: result chance +34.0 points, worth -0.83 win points
- own players alive outside the pit 0 to 0.5: result chance +17.8 points, worth -0.43 win points
- of which healers 0 to 0.5: result chance +19.2 points, worth -0.47 win points
- enemy players in the pit 7.5 to 8: result chance +10.6 points, worth -0.26 win points
- attackers' measured damage per second against a Lord (benchmarks) 85.75 to 97: result chance +7.5 points, worth -0.18 win points
- attacking minus defending team strength -416.5 to -289: result chance -10.1 points, worth +0.25 win points

