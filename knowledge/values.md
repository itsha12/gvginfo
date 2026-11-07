# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

Win points for the team it happened to, from 113 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 331 | +0.5 | -4.9 to +5.8 | +2.7 | no |
| capture | 940 | +1.8 | +0.9 to +2.8 | +2.1 | yes |
| death (any) | 2174 | -6.0 | -8.1 to -3.9 | -3.6 | yes |
| death: against a spike build | 591 | -6.2 | -11.5 to -1.3 | -2.4 | yes |
| death: against other builds | 1583 | -6.0 | -8.5 to -3.6 | -4.1 | yes |
| death: back within 20 s | 359 | -5.1 | -8.8 to -1.8 | -2.4 | yes |
| death: down 20 to 60 s | 809 | -7.3 | -10.7 to -4.1 | -3.1 | yes |
| death: down 60 s or more | 1006 | -5.4 | -7.5 to -3.4 | -4.5 | yes |
| death: healer | 731 | -5.6 | -8.0 to -3.3 | -4.0 | yes |
| death: healer in own base or pit, back within 15 s (likely deliberate) | 44 | +0.0 | -3.3 to +4.4 | +1.0 | no |
| death: healer, other | 687 | -6.0 | -8.4 to -3.6 | -4.4 | yes |
| death: not a healer | 1443 | -6.3 | -8.9 to -4.0 | -3.4 | yes |
| death: team boosted (morale above zero) | 227 | -22.1 | -33.3 to -11.5 | -7.1 | yes |
| death: team not boosted | 1947 | -4.2 | -7.1 to -1.5 | -3.2 | yes |
| footman lost (base NPC) | 327 | +0.5 | -2.5 to +3.3 | +1.0 | no |
| pit NPC lost (any): taken by a spike build | 186 | -1.5 | -5.6 to +3.1 | -0.2 | no |
| pit NPC lost (any): taken by other builds | 708 | -3.4 | -5.7 to -1.3 | -1.8 | yes |
| pit NPC lost: archer | 513 | -1.0 | -2.9 to +1.0 | +0.0 | no |
| pit NPC lost: bodyguard | 124 | -2.9 | -5.3 to -0.5 | -0.2 | yes |
| pit NPC lost: knight | 257 | -7.1 | -9.6 to -4.9 | -4.9 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value.

*deaths* (per 10 s in that state; result worth -6.0 points, base rate 1.5%):

- enemies within 1,500 7.5 to 8: result chance +3.3 points, worth -0.2 win points
- own minus enemy team strength 353.5 to 434.5: result chance -0.9 points, worth +0.05 win points
- current health % 1 to 48.5: result chance +11.0 points, worth -0.66 win points
- allies within 1,500 0 to 0.5: result chance +1.9 points, worth -0.12 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.5 points, worth -0.15 win points
- enemy enchantment removal skills 0 to 0.5: result chance +3.0 points, worth -0.18 win points
- own prot skills 6.5 to 7.5: result chance +0.8 points, worth -0.05 win points
- distance from its own pit 13437.5 to 18468: result chance +0.9 points, worth -0.05 win points

*kill conversion* (per burst, for the attacking team; result worth +6.0 points, base rate 29.8%):

- damage in the 2 s burst 508.5 to 839: result chance +27.1 points, worth +1.63 win points
- target's healers in range 0 to 0.5: result chance +32.1 points, worth +1.93 win points
- attacking minus target team strength 623 to 989: result chance +24.9 points, worth +1.49 win points
- target health % when the burst started 0 to 37.5: result chance +22.4 points, worth +1.34 win points
- target's health ceiling 0.4 to 0.69: result chance +32.1 points, worth +1.93 win points
- target team's prot skills 16.5 to 17: result chance -16.2 points, worth -0.97 win points
- a prot on the target 0.5 to 1: result chance -4.6 points, worth -0.28 win points
- attackers' interrupt skills minus target team's heals -3.5 to 1: result chance -10.4 points, worth -0.63 win points

*npc loss* (per case, for the defending team; result worth -3.0 points, base rate 20.1%):

- damage on the pit NPCs in the last 5 s 397.5 to 1370: result chance +38.1 points, worth -1.15 win points
- own players in the pit 0 to 0.5: result chance +34.0 points, worth -1.03 win points
- own players alive outside the pit 0 to 0.5: result chance +17.8 points, worth -0.54 win points
- of which healers 0 to 0.5: result chance +19.2 points, worth -0.58 win points
- enemy players in the pit 7.5 to 8: result chance +10.6 points, worth -0.32 win points
- attackers' measured damage per second against a Lord (benchmarks) 85.75 to 97: result chance +7.5 points, worth -0.23 win points
- attacking minus defending team strength -416.5 to -289: result chance -10.1 points, worth +0.3 win points

