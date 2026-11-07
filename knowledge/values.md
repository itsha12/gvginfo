# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

Win points for the team it happened to, from 61 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 208 | +0.3 | -8.4 to +9.0 | +2.7 | no |
| capture | 587 | +3.0 | +1.9 to +4.3 | +2.8 | yes |
| death (any) | 1204 | -6.2 | -9.0 to -3.5 | -3.0 | yes |
| death: against a spike build | 288 | -9.1 | -15.0 to -2.3 | -1.1 | yes |
| death: against other builds | 916 | -5.3 | -8.4 to -2.2 | -3.5 | yes |
| death: back within 20 s | 190 | -4.7 | -9.7 to +0.2 | -1.7 | no |
| death: down 20 to 60 s | 447 | -8.4 | -11.9 to -4.5 | -2.2 | yes |
| death: down 60 s or more | 567 | -4.9 | -7.6 to -2.2 | -4.0 | yes |
| death: healer | 411 | -5.0 | -7.7 to -2.3 | -3.2 | yes |
| death: healer in own base or pit, back within 15 s (likely deliberate) | 26 | -0.5 | -8.3 to +8.9 | +0.3 | no |
| death: healer, other | 385 | -5.3 | -8.1 to -2.8 | -3.5 | yes |
| death: not a healer | 793 | -6.8 | -10.3 to -3.3 | -2.8 | yes |
| death: team boosted (morale above zero) | 171 | -27.6 | -41.3 to -14.0 | -7.7 | yes |
| death: team not boosted | 1033 | -2.6 | -6.8 to +1.9 | -2.2 | no |
| footman lost (base NPC) | 188 | +1.1 | -3.9 to +5.8 | -0.3 | no |
| pit NPC lost (any): taken by a spike build | 88 | -7.6 | -14.0 to +0.9 | -4.1 | no |
| pit NPC lost (any): taken by other builds | 417 | -3.7 | -6.9 to -0.6 | -1.1 | yes |
| pit NPC lost: archer | 291 | -2.4 | -5.3 to +0.8 | -0.5 | no |
| pit NPC lost: bodyguard | 71 | -2.7 | -7.3 to +0.7 | +2.1 | no |
| pit NPC lost: knight | 143 | -9.2 | -13.0 to -5.7 | -5.7 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value.

*deaths* (per 10 s in that state; result worth -6.2 points, base rate 1.4%):

- enemies within 1,500 7.5 to 8: result chance +2.5 points, worth -0.16 win points
- current health % 1 to 47.5: result chance +10.7 points, worth -0.67 win points
- own minus enemy team strength -901 to -523: result chance +1.3 points, worth -0.08 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.5 points, worth -0.15 win points
- allies within 1,500 0 to 0.5: result chance +1.6 points, worth -0.1 win points
- match minute 20.95 to 28: result chance +1.6 points, worth -0.1 win points
- enemy enchantment removal skills 5.5 to 6: result chance -1.3 points, worth +0.08 win points

*kill conversion* (per burst, for the attacking team; result worth +6.2 points, base rate 29.7%):

- damage in the 2 s burst 518.5 to 839: result chance +31.7 points, worth +1.96 win points
- target's health ceiling 0.4 to 0.56: result chance +34.3 points, worth +2.13 win points
- target health % when the burst started 0 to 38.5: result chance +25.9 points, worth +1.61 win points
- target's healers in range 0 to 0.5: result chance +32.2 points, worth +2.0 win points
- attacking minus target team strength 459 to 901: result chance +23.0 points, worth +1.43 win points
- target team's prot skills 5.5 to 6.5: result chance +19.9 points, worth +1.24 win points
- a prot on the target 0.5 to 1: result chance -7.7 points, worth -0.48 win points
- match minute 0.3 to 1.45: result chance -14.8 points, worth -0.92 win points

*npc loss* (per case, for the defending team; result worth -4.4 points, base rate 18.5%):

- own players in the pit 7.5 to 8: result chance -15.5 points, worth +0.67 win points
- damage on the pit NPCs in the last 5 s 367 to 1170: result chance +36.4 points, worth -1.59 win points
- own players alive outside the pit 0 to 0.5: result chance +17.6 points, worth -0.77 win points
- share of the attacking team's live players in the pit (OG comms: merge before pushing the pit) 0.87 to 0.94: result chance +7.8 points, worth -0.34 win points
- of which healers 0 to 0.5: result chance +15.9 points, worth -0.7 win points
- attackers' measured damage per second against a Lord (benchmarks) 18.75 to 28.65: result chance -6.8 points, worth +0.3 win points
- enemy players in the pit 7.5 to 8: result chance +7.0 points, worth -0.3 win points
- match minute 23.45 to 28: result chance -4.7 points, worth +0.21 win points

