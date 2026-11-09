# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

Win points for the team it happened to, from 506 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. Both against matched moments without the event (same minute and win chance). A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 1406 | +4.5 | +2.5 to +6.7 | +1.8 | yes |
| capture | 4442 | +2.1 | +1.9 to +2.4 | +2.6 | yes |
| capture: held longer | 3847 | +2.8 | +2.0 to +3.5 | +2.8 | yes |
| capture: overcapped within 10 s (Bounty, F36) | 595 | -2.0 | -6.3 to +2.1 | +0.9 | no |
| death (any) | 10206 | -8.7 | -9.5 to -7.9 | -4.7 | yes |
| death: against a spike build | 2923 | -8.3 | -10.8 to -5.7 | -4.7 | yes |
| death: against other builds | 7283 | -8.9 | -10.0 to -7.9 | -4.7 | yes |
| death: back within 20 s | 1772 | -7.8 | -9.5 to -6.2 | -2.5 | yes |
| death: down 20 to 60 s | 3650 | -7.6 | -8.7 to -6.3 | -4.1 | yes |
| death: down 60 s or more | 4784 | -9.9 | -11.0 to -8.7 | -6.0 | yes |
| death: healer | 3443 | -8.3 | -9.4 to -7.2 | -4.8 | yes |
| death: healer in own base or pit, back within 15 s (possibly deliberate; energy not tracked) | 239 | -5.2 | -7.5 to -3.1 | -1.7 | yes |
| death: healer, other | 3204 | -8.5 | -9.6 to -7.4 | -5.1 | yes |
| death: not a healer | 6763 | -8.9 | -9.9 to -8.0 | -4.7 | yes |
| footman lost (base NPC) | 1430 | +0.5 | -0.7 to +1.6 | +3.8 | no |
| pit NPC lost (any): taken by a spike build | 881 | -5.2 | -7.9 to -2.5 | -2.1 | yes |
| pit NPC lost (any): taken by other builds | 3199 | -5.1 | -6.2 to -4.0 | -2.3 | yes |
| pit NPC lost: archer | 2306 | -4.2 | -5.2 to -3.4 | -0.7 | yes |
| pit NPC lost: bodyguard | 548 | -5.4 | -6.5 to -4.4 | -2.5 | yes |
| pit NPC lost: knight | 1226 | -6.6 | -7.7 to -5.7 | -5.0 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value. Context (strength, build skill counts, flag lead, morale, the clock) is left out: it describes the situation, it is not a cause to fix.

*deaths* (per 10 s in that state; result worth -8.7 points, base rate 1.6%):

- enemies within 1,500 7.5 to 8: result chance +3.2 points, worth -0.28 win points
- allies within 1,500 0 to 0.5: result chance +2.1 points, worth -0.18 win points
- current health % 1 to 47.5: result chance +10.3 points, worth -0.89 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.6 points, worth -0.23 win points
- a prot (Guardian, Spirit Bond, Life Sheath, Protective Spirit...) on the player now 0.5 to 1: result chance -0.4 points, worth +0.04 win points
- own healers alive within cast range (other than the player) 0 to 0.5: result chance +0.5 points, worth -0.04 win points

*kill conversion* (per burst, for the attacking team; result worth +8.7 points, base rate 29.6%):

- damage in the 2 s burst 509.5 to 1069: result chance +30.1 points, worth +2.62 win points
- target's health ceiling 0.4 to 0.56: result chance +46.4 points, worth +4.04 win points
- target's healers in range 0 to 0.5: result chance +35.5 points, worth +3.09 win points
- target health % when the burst started 0 to 36.5: result chance +30.8 points, worth +2.68 win points
- a prot on the target 0.5 to 1: result chance -7.4 points, worth -0.65 win points

*pit npc loss* (per case, for the defending team; result worth -5.1 points, base rate 20.8%):

- own players in the pit 0 to 0.5: result chance +42.1 points, worth -2.14 win points
- own players alive outside the pit 0 to 0.5: result chance +12.5 points, worth -0.63 win points
- of which healers 0 to 0.5: result chance +16.1 points, worth -0.82 win points

