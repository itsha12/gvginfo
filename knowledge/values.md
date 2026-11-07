# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

Win points for the team it happened to, from 113 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 331 | -0.0 | -5.4 to +4.9 | +3.1 | no |
| capture | 940 | +2.3 | +1.6 to +3.0 | +2.2 | yes |
| death (any) | 2174 | -5.7 | -7.7 to -3.7 | -3.9 | yes |
| death: against a spike build | 591 | -6.2 | -11.5 to -1.3 | -3.0 | yes |
| death: against other builds | 1583 | -5.5 | -7.9 to -3.3 | -4.2 | yes |
| death: back within 20 s | 359 | -5.3 | -8.9 to -1.9 | -2.3 | yes |
| death: down 20 to 60 s | 809 | -6.6 | -10.0 to -3.6 | -3.5 | yes |
| death: down 60 s or more | 1006 | -5.0 | -7.0 to -3.2 | -4.8 | yes |
| death: healer | 731 | -5.3 | -7.7 to -3.1 | -4.3 | yes |
| death: healer in own base or pit, back within 15 s (likely deliberate) | 44 | -0.4 | -4.2 to +4.3 | +1.2 | no |
| death: healer, other | 687 | -5.7 | -8.0 to -3.4 | -4.7 | yes |
| death: not a healer | 1443 | -5.8 | -8.3 to -3.7 | -3.7 | yes |
| death: team boosted (morale above zero) | 227 | -23.3 | -34.6 to -12.4 | -8.3 | yes |
| death: team not boosted | 1947 | -3.6 | -6.5 to -1.0 | -3.4 | yes |
| footman lost (base NPC) | 327 | +0.9 | -2.2 to +3.7 | +1.0 | no |
| pit NPC lost (any): taken by a spike build | 186 | -0.3 | -4.6 to +4.4 | -0.3 | no |
| pit NPC lost (any): taken by other builds | 708 | -3.3 | -5.6 to -1.0 | -1.6 | yes |
| pit NPC lost: archer | 513 | -0.6 | -2.5 to +1.4 | +0.2 | no |
| pit NPC lost: bodyguard | 124 | -2.3 | -4.7 to +0.1 | -0.6 | no |
| pit NPC lost: knight | 257 | -7.0 | -9.9 to -4.7 | -4.7 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value.

*deaths* (per 10 s in that state; result worth -5.7 points, base rate 1.5%):

- enemies within 1,500 7.5 to 8: result chance +3.3 points, worth -0.19 win points
- own minus enemy team strength 353.5 to 434.5: result chance -0.9 points, worth +0.05 win points
- current health % 1 to 48.5: result chance +11.2 points, worth -0.64 win points
- allies within 1,500 0 to 0.5: result chance +1.9 points, worth -0.11 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.5 points, worth -0.14 win points
- enemy enchantment removal skills 0 to 0.5: result chance +3.0 points, worth -0.17 win points
- own prot skills 6.5 to 7.5: result chance +0.7 points, worth -0.04 win points
- distance from its own pit 13437.5 to 18468: result chance +0.9 points, worth -0.05 win points

*kill conversion* (per burst, for the attacking team; result worth +5.7 points, base rate 29.8%):

- damage in the 2 s burst 508.5 to 839: result chance +27.1 points, worth +1.55 win points
- target's healers in range 0 to 0.5: result chance +32.1 points, worth +1.83 win points
- attacking minus target team strength 623 to 989: result chance +24.9 points, worth +1.42 win points
- target health % when the burst started 0 to 37.5: result chance +22.4 points, worth +1.28 win points
- target's health ceiling 0.4 to 0.69: result chance +32.1 points, worth +1.83 win points
- target team's prot skills 16.5 to 17: result chance -16.2 points, worth -0.92 win points
- a prot on the target 0.5 to 1: result chance -4.6 points, worth -0.26 win points
- attackers' interrupt skills minus target team's heals -3.5 to 1: result chance -10.4 points, worth -0.6 win points

*npc loss* (per case, for the defending team; result worth -2.7 points, base rate 20.1%):

- damage on the pit NPCs in the last 5 s 397.5 to 1370: result chance +38.1 points, worth -1.02 win points
- own players in the pit 0 to 0.5: result chance +34.0 points, worth -0.91 win points
- own players alive outside the pit 0 to 0.5: result chance +17.8 points, worth -0.48 win points
- of which healers 0 to 0.5: result chance +19.2 points, worth -0.51 win points
- enemy players in the pit 7.5 to 8: result chance +10.6 points, worth -0.28 win points
- attackers' measured damage per second against a Lord (benchmarks) 85.75 to 97: result chance +7.5 points, worth -0.2 win points
- attacking minus defending team strength -416.5 to -289: result chance -10.1 points, worth +0.27 win points

