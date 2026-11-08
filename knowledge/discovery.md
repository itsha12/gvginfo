# What discovery found

Step 3 of the learned causal map (`discover.py`): every variable the engine measures about a team at a moment (the state table, prefix s., and the build and matchup features, prefix b.) tested against every learned node on matches the node never saw. A **discovery** predicts what the node misses by more than twice its spread, in at least 5 of 6 held-out folds. Each is held for Denning's approval: approve (it becomes a link in the causal map and a variable in the node), reject, or wait for more matches.

Variables tested: 915 (variable by node); 92 passed the screen, where chance alone would pass about 21 (2.3% at twice the spread). Treat a discovery as a lead.

| Node | Variable | Gain on unseen matches | Folds up | Result, lowest third -> highest third |
|---|---|---|---|---|
| flag swing | s.morale_diff | +0.2987 (+/- 0.1434) | 5 of 6 | -1.1 (at or below -23) -> 1.815 (above 23) |
| split answer | s.split_diff | +0.1877 (+/- 0.0699) | 5 of 6 | -10.234 (at or below -2) -> 0.188 (above -1) |
| fight outcome | s.morale_diff | +0.0846 (+/- 0.0131) | 6 of 6 | 0.199 (at or below -32) -> 0.834 (above 32) |
| fight outcome | s.fight_state | +0.0417 (+/- 0.0107) | 6 of 6 | 0.139 (at or below -0.06) -> 0.834 (above 0.04) |
| fight outcome | s.down_diff_s | +0.0272 (+/- 0.0068) | 6 of 6 | 0.371 (at or below 0) -> 0.904 (above 0) |
| run defence | s.boost_clock | +0.0248 (+/- 0.0068) | 6 of 6 | 0.495 (at or below 0) -> 0.712 (above 79) |
| run defence | s.stand | +0.0226 (+/- 0.0053) | 6 of 6 | 0.494 (at or below 0) -> nan (above 1) |
| fight outcome | s.spike_killable_diff | +0.0219 (+/- 0.0052) | 6 of 6 | 0.418 (at or below 0) -> 0.855 (above 0) |
| fight outcome | s.stand | +0.0191 (+/- 0.0052) | 5 of 6 | 0.286 (at or below -1) -> nan (above 1) |
| split effect | s.morale_diff | +0.0152 (+/- 0.0028) | 6 of 6 | 0.286 (at or below -21) -> 0.423 (above 30) |
| fight outcome | s.alive_diff | +0.0143 (+/- 0.0062) | 5 of 6 | 0.367 (at or below 0) -> 0.848 (above 0) |
| run defence | s.flag_lead | +0.0113 (+/- 0.0046) | 5 of 6 | 0.522 (at or below -19) -> 0.66 (above 20) |
| split effect | s.flag_lead | +0.0113 (+/- 0.0031) | 6 of 6 | 0.307 (at or below -22) -> 0.435 (above 34) |
| split effect | b.enemy_prots | +0.0112 (+/- 0.0043) | 5 of 6 | 0.503 (at or below 11) -> 0.286 (above 14) |
| split effect | b.own_deep_wound | +0.0111 (+/- 0.0040) | 5 of 6 | 0.406 (at or below 2) -> 0.289 (above 2) |
| split effect | s.lord_damage_diff | +0.0107 (+/- 0.0045) | 5 of 6 | 0.451 (at or below 0) -> 0.264 (above 0) |
| run outcome | s.morale_diff | +0.0092 (+/- 0.0037) | 6 of 6 | 0.563 (at or below -15) -> 0.65 (above 0) |
| run outcome | s.boost_clock | +0.0090 (+/- 0.0034) | 6 of 6 | 0.715 (at or below -79) -> 0.448 (above 0) |
| run defence | b.own_snares | +0.0085 (+/- 0.0024) | 6 of 6 | 0.61 (at or below 1) -> 0.502 (above 3) |
| power play | s.down_diff_s | +0.0076 (+/- 0.0028) | 5 of 6 | 0.331 (at or below 0) -> 0.585 (above 0) |
| run outcome | b.enemy_snares | +0.0076 (+/- 0.0025) | 6 of 6 | 0.61 (at or below 1) -> 0.502 (above 3) |
| run defence | s.morale_diff | +0.0076 (+/- 0.0030) | 6 of 6 | 0.635 (at or below 0) -> 0.553 (above 15) |
| split chance | s.split_diff | +0.0067 (+/- 0.0021) | 5 of 6 | 0.129 (at or below 0) -> 0.233 (above 0) |
| power play | s.carrying_diff | +0.0066 (+/- 0.0019) | 5 of 6 | 0.411 (at or below 0) -> 0.236 (above 0) |
| run defence | s.down_diff_s | +0.0053 (+/- 0.0027) | 5 of 6 | 0.626 (at or below 0) -> 0.49 (above 0) |
| split chance | s.turtle_diff | +0.0044 (+/- 0.0017) | 5 of 6 | 0.143 (at or below 0) -> 0.108 (above 0) |
| split chance | s.pit_pressure_diff | +0.0011 (+/- 0.0005) | 5 of 6 | 0.13 (at or below 0) -> 0.146 (above 0) |

## Per node

**capture speed** (R.3; 125 matches, 1060 rows, mean absolute error (s)): 93 variables screened, 0 passed the screen

**collapse** (R.1; 120 matches, 848 rows, log loss): 92 variables screened, 9 passed the screen
- b.own_aura_of_stability: screen +0.0057, confirmed +0.0039 (+/- 0.0020, 3 of 6 folds up): not clear yet
- s.fight_state: screen +0.0063, confirmed +0.0064 (+/- 0.0041, 4 of 6 folds up): not clear yet
- b.enemy_prots: screen +0.0044, confirmed +0.0033 (+/- 0.0024, 3 of 6 folds up): not clear yet
- b.enemy_interrupts: screen +0.0039, confirmed +0.0005 (+/- 0.0015, 3 of 6 folds up): not clear yet
- s.morale_diff: screen +0.0074, confirmed +0.0062 (+/- 0.0074, 5 of 6 folds up): not clear yet
- s.turtle_diff: screen +0.0036, confirmed +0.0010 (+/- 0.0013, 2 of 6 folds up): not clear yet

**fight outcome** (R.2; 133 matches, 989 rows, log loss): 93 variables screened, 22 passed the screen
- s.morale_diff: screen +0.0732, confirmed +0.0846 (+/- 0.0131, 6 of 6 folds up): discovery (held for Denning)
- s.down_diff_s: screen +0.0279, confirmed +0.0272 (+/- 0.0068, 6 of 6 folds up): discovery (held for Denning)
- s.fight_state: screen +0.0301, confirmed +0.0417 (+/- 0.0107, 6 of 6 folds up): discovery (held for Denning)
- s.alive_diff: screen +0.0181, confirmed +0.0143 (+/- 0.0062, 5 of 6 folds up): discovery (held for Denning)
- s.stand: screen +0.0203, confirmed +0.0191 (+/- 0.0052, 5 of 6 folds up): discovery (held for Denning)
- s.spike_killable_diff: screen +0.0192, confirmed +0.0219 (+/- 0.0052, 6 of 6 folds up): discovery (held for Denning)

**flag swing** (R.3; 133 matches, 5131 rows, mean absolute error (s)): 90 variables screened, 9 passed the screen
- s.morale_diff: screen +0.1658, confirmed +0.2987 (+/- 0.1434, 5 of 6 folds up): discovery (held for Denning)
- s.no_healer_groups_diff: screen +0.0776, confirmed +0.0612 (+/- 0.0382, 5 of 6 folds up): not clear yet
- s.lord_damage_diff: screen +0.0452, confirmed +0.0653 (+/- 0.0607, 5 of 6 folds up): not clear yet
- b.own_speed: screen +0.0301, confirmed +0.0025 (+/- 0.0163, 4 of 6 folds up): not clear yet
- s.knights_diff: screen +0.0222, confirmed +0.0379 (+/- 0.0348, 4 of 6 folds up): not clear yet
- s.archers_diff: screen +0.0152, confirmed +0.0270 (+/- 0.0420, 4 of 6 folds up): not clear yet

**power play** (K.4; 133 matches, 1162 rows, log loss): 92 variables screened, 6 passed the screen
- s.carrying_diff: screen +0.0046, confirmed +0.0066 (+/- 0.0019, 5 of 6 folds up): discovery (held for Denning)
- s.down_diff_s: screen +0.0043, confirmed +0.0076 (+/- 0.0028, 5 of 6 folds up): discovery (held for Denning)
- s.flux_minion_apocalypse: screen +0.0014, confirmed +0.0011 (+/- 0.0011, 4 of 6 folds up): not clear yet
- b.own_heals: screen +0.0013, confirmed +0.0032 (+/- 0.0022, 4 of 6 folds up): not clear yet
- b.enemy_snares: screen +0.0013, confirmed +0.0001 (+/- 0.0006, 3 of 6 folds up): not clear yet
- s.alive_diff: screen +0.0020, confirmed +0.0050 (+/- 0.0041, 5 of 6 folds up): not clear yet

**run defence** (R.3; 133 matches, 4490 rows, log loss): 93 variables screened, 13 passed the screen
- s.boost_clock: screen +0.0223, confirmed +0.0248 (+/- 0.0068, 6 of 6 folds up): discovery (held for Denning)
- s.stand: screen +0.0201, confirmed +0.0226 (+/- 0.0053, 6 of 6 folds up): discovery (held for Denning)
- s.flag_lead: screen +0.0095, confirmed +0.0113 (+/- 0.0046, 5 of 6 folds up): discovery (held for Denning)
- s.morale_diff: screen +0.0067, confirmed +0.0076 (+/- 0.0030, 6 of 6 folds up): discovery (held for Denning)
- s.down_diff_s: screen +0.0055, confirmed +0.0053 (+/- 0.0027, 5 of 6 folds up): discovery (held for Denning)
- b.own_snares: screen +0.0055, confirmed +0.0085 (+/- 0.0024, 6 of 6 folds up): discovery (held for Denning)

**run outcome** (R.3; 133 matches, 4490 rows, log loss): 92 variables screened, 10 passed the screen
- s.morale_diff: screen +0.0071, confirmed +0.0092 (+/- 0.0037, 6 of 6 folds up): discovery (held for Denning)
- s.boost_clock: screen +0.0073, confirmed +0.0090 (+/- 0.0034, 6 of 6 folds up): discovery (held for Denning)
- s.down_diff_s: screen +0.0053, confirmed +0.0053 (+/- 0.0028, 4 of 6 folds up): not clear yet
- b.enemy_snares: screen +0.0047, confirmed +0.0076 (+/- 0.0025, 6 of 6 folds up): discovery (held for Denning)
- b.enemy_strips_v_own_prots: screen +0.0029, confirmed +0.0044 (+/- 0.0024, 4 of 6 folds up): not clear yet
- b.own_prots: screen +0.0031, confirmed +0.0059 (+/- 0.0032, 4 of 6 folds up): not clear yet

**split answer** (P.11; 94 matches, 375 rows, mean absolute error (s)): 91 variables screened, 2 passed the screen
- s.split_diff: screen +0.2118, confirmed +0.1877 (+/- 0.0699, 5 of 6 folds up): discovery (held for Denning)
- b.own_strips_v_enemy_prots: screen +0.1357, confirmed +0.0208 (+/- 0.1044, 4 of 6 folds up): not clear yet
- s.spike_build_own: screen +0.0427, confirmed +0.0772 (+/- 0.0751, 4 of 6 folds up): not clear yet
- b.own_area_damage: screen +0.0394, confirmed +0.0191 (+/- 0.0823, 3 of 6 folds up): not clear yet
- b.enemy_blocks: screen +0.0288, confirmed -0.1170 (+/- 0.1171, 1 of 6 folds up): not clear yet
- b.own_strips: screen +0.0324, confirmed +0.0322 (+/- 0.0777, 3 of 6 folds up): not clear yet

**split chance** (A.allocation; 133 matches, 10033 rows, log loss): 87 variables screened, 9 passed the screen
- s.spike_build_own: screen +0.0061, confirmed +0.0072 (+/- 0.0043, 5 of 6 folds up): not clear yet
- s.turtle_diff: screen +0.0028, confirmed +0.0044 (+/- 0.0017, 5 of 6 folds up): discovery (held for Denning)
- s.split_diff: screen +0.0040, confirmed +0.0067 (+/- 0.0021, 5 of 6 folds up): discovery (held for Denning)
- s.archers_diff: screen +0.0035, confirmed +0.0063 (+/- 0.0025, 4 of 6 folds up): not clear yet
- b.enemy_interrupts: screen +0.0021, confirmed +0.0022 (+/- 0.0013, 5 of 6 folds up): not clear yet
- s.pit_pressure_diff: screen +0.0012, confirmed +0.0011 (+/- 0.0005, 5 of 6 folds up): discovery (held for Denning)

**split effect** (R.5; 94 matches, 375 rows, log loss): 92 variables screened, 12 passed the screen
- b.own_deep_wound: screen +0.0129, confirmed +0.0111 (+/- 0.0040, 5 of 6 folds up): discovery (held for Denning)
- s.morale_diff: screen +0.0110, confirmed +0.0152 (+/- 0.0028, 6 of 6 folds up): discovery (held for Denning)
- b.enemy_prots: screen +0.0121, confirmed +0.0112 (+/- 0.0043, 5 of 6 folds up): discovery (held for Denning)
- s.lord_damage_diff: screen +0.0097, confirmed +0.0107 (+/- 0.0045, 5 of 6 folds up): discovery (held for Denning)
- s.archers_diff: screen +0.0112, confirmed +0.0107 (+/- 0.0064, 5 of 6 folds up): not clear yet
- s.flag_lead: screen +0.0079, confirmed +0.0113 (+/- 0.0031, 6 of 6 folds up): discovery (held for Denning)

