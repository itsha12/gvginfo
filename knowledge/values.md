# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

Win points for the team it happened to, from 91 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 281 | -0.8 | -6.4 to +4.8 | +2.9 | no |
| capture | 746 | +2.6 | +1.7 to +3.5 | +2.4 | yes |
| death (any) | 1768 | -5.2 | -7.2 to -3.2 | -3.8 | yes |
| death: against a spike build | 455 | -8.0 | -15.4 to -1.4 | -3.1 | yes |
| death: against other builds | 1313 | -4.2 | -6.8 to -1.8 | -4.0 | yes |
| death: back within 20 s | 281 | -3.6 | -7.8 to -0.1 | -1.1 | yes |
| death: down 20 to 60 s | 668 | -5.0 | -7.8 to -2.4 | -2.3 | yes |
| death: down 60 s or more | 819 | -5.9 | -8.4 to -3.6 | -5.8 | yes |
| death: healer | 599 | -5.2 | -8.3 to -2.5 | -4.3 | yes |
| death: healer in own base or pit, back within 15 s (likely deliberate) | 37 | +1.2 | -2.8 to +6.9 | +2.0 | no |
| death: healer, other | 562 | -5.6 | -8.6 to -2.9 | -4.7 | yes |
| death: not a healer | 1169 | -5.2 | -8.1 to -2.8 | -3.5 | yes |
| death: team boosted (morale above zero) | 206 | -24.0 | -36.6 to -12.7 | -7.7 | yes |
| death: team not boosted | 1562 | -2.7 | -5.6 to +0.0 | -3.2 | no |
| footman lost (base NPC) | 257 | +1.1 | -3.1 to +5.0 | -0.0 | no |
| pit NPC lost (any): taken by a spike build | 142 | -2.8 | -6.8 to +1.6 | -2.4 | no |
| pit NPC lost (any): taken by other builds | 573 | -1.7 | -3.8 to +0.8 | -0.3 | no |
| pit NPC lost: archer | 410 | +0.5 | -1.8 to +3.4 | +0.1 | no |
| pit NPC lost: bodyguard | 100 | -3.7 | -6.7 to -1.0 | +0.3 | yes |
| pit NPC lost: knight | 205 | -5.8 | -8.5 to -3.3 | -2.9 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value.

*deaths* (per 10 s in that state; result worth -5.2 points, base rate 1.5%):

- enemies within 1,500 7.5 to 8: result chance +3.2 points, worth -0.17 win points
- own minus enemy team strength -976 to -581: result chance +1.8 points, worth -0.09 win points
- current health % 1 to 46.5: result chance +11.4 points, worth -0.59 win points
- allies within 1,500 0 to 0.5: result chance +1.9 points, worth -0.1 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.7 points, worth -0.14 win points
- match minute 20.45 to 28: result chance +1.4 points, worth -0.07 win points
- own condition removal skills 7.5 to 8: result chance -0.9 points, worth +0.05 win points

*kill conversion* (per burst, for the attacking team; result worth +5.2 points, base rate 30.7%):

- damage in the 2 s burst 506.5 to 839: result chance +24.4 points, worth +1.27 win points
- target's healers in range 0 to 0.5: result chance +29.4 points, worth +1.53 win points
- target health % when the burst started 0 to 38.5: result chance +20.6 points, worth +1.07 win points
- target's health ceiling 0.4 to 0.69: result chance +26.6 points, worth +1.38 win points
- attacking minus target team strength 611 to 976: result chance +14.0 points, worth +0.73 win points
- target team's prot skills 1 to 2.5: result chance +7.7 points, worth +0.4 win points
- a prot on the target 0.5 to 1: result chance -4.1 points, worth -0.21 win points
- attackers' interrupt skills minus target team's heals -5.5 to -4.5: result chance -4.2 points, worth -0.22 win points

*npc loss* (per case, for the defending team; result worth -1.9 points, base rate 19.7%):

- damage on the pit NPCs in the last 5 s 382.5 to 1170: result chance +37.5 points, worth -0.71 win points
- own players in the pit 7.5 to 8: result chance -15.6 points, worth +0.3 win points
- own players alive outside the pit 0 to 0.5: result chance +15.2 points, worth -0.29 win points
- of which healers 0 to 0.5: result chance +19.6 points, worth -0.37 win points
- attackers' measured damage per second against a Lord (benchmarks) 1.9 to 18.75: result chance -7.1 points, worth +0.13 win points
- share of the attacking team's live players in the pit (OG comms: merge before pushing the pit) 0.12 to 0.13: result chance -6.4 points, worth +0.12 win points
- enemy players in the pit 7.5 to 8: result chance +7.6 points, worth -0.14 win points

