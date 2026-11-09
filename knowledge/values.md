# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

Win points for the team it happened to, from 446 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. Both against matched moments without the event (same minute and win chance). A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 1275 | +3.4 | +1.3 to +5.5 | +2.3 | yes |
| capture | 3984 | +2.1 | +1.8 to +2.4 | +2.9 | yes |
| capture: held longer | 3449 | +2.7 | +1.9 to +3.5 | +3.1 | yes |
| capture: overcapped within 10 s (Bounty, F36) | 535 | -1.9 | -6.1 to +2.6 | +1.2 | no |
| death (any) | 9014 | -7.6 | -8.5 to -6.8 | -4.9 | yes |
| death: against a spike build | 2502 | -6.7 | -9.2 to -4.0 | -4.8 | yes |
| death: against other builds | 6512 | -8.0 | -9.1 to -6.9 | -5.0 | yes |
| death: back within 20 s | 1522 | -6.5 | -8.2 to -5.0 | -2.7 | yes |
| death: down 20 to 60 s | 3240 | -6.6 | -7.9 to -5.4 | -4.4 | yes |
| death: down 60 s or more | 4252 | -8.8 | -10.0 to -7.6 | -6.2 | yes |
| death: healer | 3040 | -7.2 | -8.2 to -6.1 | -5.1 | yes |
| death: healer in own base or pit, back within 15 s (possibly deliberate; energy not tracked) | 198 | -2.0 | -3.9 to +0.2 | -1.2 | no |
| death: healer, other | 2842 | -7.5 | -8.6 to -6.4 | -5.3 | yes |
| death: not a healer | 5974 | -7.9 | -8.8 to -6.9 | -4.9 | yes |
| footman lost (base NPC) | 1250 | +1.6 | +0.3 to +2.8 | +5.1 | yes |
| pit NPC lost (any): taken by a spike build | 755 | -4.0 | -7.1 to -0.8 | -1.9 | yes |
| pit NPC lost (any): taken by other builds | 2870 | -3.9 | -5.1 to -2.7 | -2.0 | yes |
| pit NPC lost: archer | 2055 | -3.1 | -4.1 to -2.2 | -0.6 | yes |
| pit NPC lost: bodyguard | 483 | -4.0 | -5.1 to -3.1 | -2.3 | yes |
| pit NPC lost: knight | 1087 | -5.3 | -6.3 to -4.4 | -4.4 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value. Context (strength, build skill counts, flag lead, morale, the clock) is left out: it describes the situation, it is not a cause to fix.

*deaths* (per 10 s in that state; result worth -7.6 points, base rate 1.5%):

- enemies within 1,500 7.5 to 8: result chance +3.2 points, worth -0.24 win points
- allies within 1,500 0 to 0.5: result chance +2.3 points, worth -0.17 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.7 points, worth -0.21 win points
- current health % 1 to 48.5: result chance +10.2 points, worth -0.78 win points
- a prot (Guardian, Spirit Bond, Life Sheath, Protective Spirit...) on the player now 0.5 to 1: result chance -0.4 points, worth +0.03 win points
- distance from its own pit 13165.5 to 18468: result chance +0.8 points, worth -0.06 win points

*kill conversion* (per burst, for the attacking team; result worth +7.6 points, base rate 29.1%):

- damage in the 2 s burst 505.5 to 1069: result chance +29.3 points, worth +2.23 win points
- target's healers in range 0 to 0.5: result chance +35.6 points, worth +2.71 win points
- target's health ceiling 0.4 to 0.56: result chance +47.6 points, worth +3.62 win points
- target health % when the burst started 0 to 36.5: result chance +32.8 points, worth +2.49 win points
- a prot on the target 0.5 to 1: result chance -7.9 points, worth -0.6 win points

*pit npc loss* (per case, for the defending team; result worth -3.9 points, base rate 20.7%):

- own players in the pit 0 to 0.5: result chance +41.9 points, worth -1.62 win points
- own players alive outside the pit 0 to 0.5: result chance +13.0 points, worth -0.51 win points
- of which healers 0 to 0.5: result chance +17.7 points, worth -0.69 win points

