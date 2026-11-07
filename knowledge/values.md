# What results and causes are worth

Measured by `tools/replay_analysis/values.py`; refreshed with each training batch. Values are in win points (percentage points of win chance) for the team the event happened to.

Win points for the team it happened to, from 91 matches. **Result** = how matches actually ended against what a win model that never saw the match expected just before (so it includes what the event usually led to); **model** = the win model's own change over the next 30 s. A gap between the two points at a win-model curve to check.

| Event | Cases | Result | 90% range | Model (30 s) | Clear |
|---|---|---|---|---|---|
| boost | 281 | -0.8 | -6.4 to +4.8 | +2.9 | no |
| capture | 746 | +2.6 | +1.9 to +3.4 | +2.5 | yes |
| death (any) | 1768 | -5.1 | -7.2 to -3.2 | -3.8 | yes |
| death: against a spike build | 455 | -8.2 | -15.6 to -1.6 | -3.3 | yes |
| death: against other builds | 1313 | -4.1 | -6.5 to -1.8 | -4.0 | yes |
| death: back within 20 s | 281 | -3.1 | -7.1 to +0.6 | -1.4 | no |
| death: down 20 to 60 s | 668 | -5.1 | -7.8 to -2.4 | -2.3 | yes |
| death: down 60 s or more | 819 | -5.9 | -8.4 to -3.6 | -5.9 | yes |
| death: healer | 599 | -5.2 | -8.3 to -2.5 | -4.4 | yes |
| death: healer in own base or pit, back within 15 s (likely deliberate) | 37 | +1.2 | -2.8 to +6.7 | +1.2 | no |
| death: healer, other | 562 | -5.6 | -8.5 to -3.0 | -4.8 | yes |
| death: not a healer | 1169 | -5.1 | -8.0 to -2.8 | -3.5 | yes |
| death: team boosted (morale above zero) | 206 | -24.6 | -37.2 to -13.4 | -8.1 | yes |
| death: team not boosted | 1562 | -2.6 | -5.4 to +0.2 | -3.3 | no |
| footman lost (base NPC) | 257 | +1.3 | -2.8 to +5.1 | -0.3 | no |
| pit NPC lost (any): taken by a spike build | 142 | -2.9 | -6.9 to +1.7 | -2.3 | no |
| pit NPC lost (any): taken by other builds | 573 | -1.5 | -3.6 to +1.0 | -0.3 | no |
| pit NPC lost: archer | 410 | +0.6 | -1.9 to +3.5 | +0.3 | no |
| pit NPC lost: bodyguard | 100 | -3.6 | -6.6 to -0.8 | +0.2 | yes |
| pit NPC lost: knight | 205 | -5.5 | -8.1 to -3.2 | -3.2 | yes |

**What causes are worth.** A node model's strongest range for each top variable, turned into win points: the change in the result's chance (at its real rate) times the result's value.

*deaths* (per 10 s in that state; result worth -5.1 points, base rate 1.5%):

- enemies within 1,500 7.5 to 8: result chance +3.2 points, worth -0.17 win points
- own minus enemy team strength -976 to -579.5: result chance +1.7 points, worth -0.09 win points
- current health % 1 to 46.5: result chance +11.6 points, worth -0.59 win points
- allies minus enemies within 2,000 -8 to -3.5: result chance +2.7 points, worth -0.14 win points
- allies within 1,500 0 to 0.5: result chance +1.9 points, worth -0.1 win points
- match minute 20.45 to 28: result chance +1.4 points, worth -0.07 win points
- own condition removal skills 7.5 to 8: result chance -1.1 points, worth +0.06 win points
- enemy enchantment removal skills 0 to 0.5: result chance +6.3 points, worth -0.32 win points

*kill conversion* (per burst, for the attacking team; result worth +5.1 points, base rate 30.7%):

- damage in the 2 s burst 506.5 to 839: result chance +24.1 points, worth +1.23 win points
- target's healers in range 0 to 0.5: result chance +29.3 points, worth +1.49 win points
- target health % when the burst started 0 to 38.5: result chance +20.4 points, worth +1.04 win points
- target's health ceiling 0.4 to 0.69: result chance +26.6 points, worth +1.36 win points
- attacking minus target team strength 611 to 976: result chance +13.9 points, worth +0.71 win points
- target team's prot skills 1 to 2.5: result chance +7.9 points, worth +0.4 win points
- a prot on the target 0.5 to 1: result chance -4.1 points, worth -0.21 win points
- attackers' interrupt skills minus target team's heals -5.5 to -4.5: result chance -4.6 points, worth -0.23 win points

*npc loss* (per case, for the defending team; result worth -1.7 points, base rate 19.7%):

- damage on the pit NPCs in the last 5 s 382.5 to 1170: result chance +37.5 points, worth -0.65 win points
- own players in the pit 7.5 to 8: result chance -15.5 points, worth +0.27 win points
- own players alive outside the pit 0 to 0.5: result chance +15.1 points, worth -0.26 win points
- of which healers 0 to 0.5: result chance +19.8 points, worth -0.34 win points
- attackers' measured damage per second against a Lord (benchmarks) 1.9 to 18.75: result chance -7.1 points, worth +0.12 win points
- share of the attacking team's live players in the pit (OG comms: merge before pushing the pit) 0.12 to 0.13: result chance -6.3 points, worth +0.11 win points
- enemy players in the pit 7.5 to 8: result chance +7.5 points, worth -0.13 win points

