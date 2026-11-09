# What discovery found

Step 3 of the learned causal map (`discover.py`): every variable the engine measures about a team at a moment (the state table, prefix s., and the build and matchup features, prefix b.) tested against every learned node on matches the node never saw. A **discovery** predicts what the node misses by more than twice its spread, in at least 5 of 6 held-out folds. Each is held for Denning's approval: approve (it becomes a link in the causal map and a variable in the node), reject, or wait for more matches.

Variables tested: 958 (variable by node); 56 passed the screen, where chance alone would pass about 22 (2.3% at twice the spread). Treat a discovery as a lead.

| Node | Variable | Gain on unseen matches | Folds up | Result, lowest third -> highest third |
|---|---|---|---|---|
| split answer | s.main_diff | +0.3930 (+/- 0.1418) | 6 of 6 | -5.222 (at or below 0) -> -3.926 (above 1) |
| split answer | b.own_area_damage | +0.2208 (+/- 0.0975) | 6 of 6 | -4.288 (at or below 0) -> -5.018 (above 1) |
| fight outcome | s.morale_total | +0.0101 (+/- 0.0013) | 6 of 6 | 0.49 (at or below -52.67) -> 0.505 (above 0) |
| split effect | s.turtle_diff | +0.0056 (+/- 0.0013) | 6 of 6 | 0.407 (at or below 0) -> 0.362 (above 0) |
| split chance | s.spike_build_own | +0.0050 (+/- 0.0012) | 5 of 6 | 0.165 (at or below 0) -> 0.058 (above 0) |
| fight outcome | b.own_hexes | +0.0048 (+/- 0.0014) | 6 of 6 | 0.509 (at or below 3) -> 0.402 (above 4) |
| split effect | b.own_escapes_power | +0.0048 (+/- 0.0018) | 6 of 6 | 0.413 (at or below 1) -> 0.436 (above 2) |
| power play | s.morale_diff | +0.0045 (+/- 0.0020) | 5 of 6 | 0.235 (at or below 0) -> 0.578 (above 47) |
| fight outcome | b.enemy_energy_denial_v_own_heals | +0.0043 (+/- 0.0009) | 6 of 6 | 0.416 (at or below -12) -> 0.507 (above -10) |
| split chance | b.own_knockdowns | +0.0042 (+/- 0.0011) | 6 of 6 | 0.142 (at or below 1) -> 0.079 (above 3) |
| collapse | s.healing_monks_enemy | +0.0041 (+/- 0.0011) | 6 of 6 | 0.129 (at or below 3) -> 0.108 (above 3) |
| fight outcome | b.own_heals | +0.0028 (+/- 0.0006) | 6 of 6 | 0.504 (at or below 13) -> 0.402 (above 15) |
| split chance | s.map_flag_run | +0.0028 (+/- 0.0010) | 5 of 6 | 0.12 (at or below 6447) -> 0.124 (above 8335) |
| power play | b.enemy_strips_v_own_prots | +0.0023 (+/- 0.0008) | 5 of 6 | 0.359 (at or below -11) -> 0.422 (above -9) |
| run outcome | s.down_diff_s | +0.0021 (+/- 0.0006) | 6 of 6 | 0.656 (at or below 0) -> 0.704 (above 0) |
| run defence | b.own_area_damage | +0.0011 (+/- 0.0004) | 5 of 6 | 0.668 (at or below 0) -> 0.621 (above 1) |
| run defence | b.enemy_snares_v_own_speed | +0.0009 (+/- 0.0004) | 5 of 6 | 0.659 (at or below -5) -> 0.666 (above -4) |
| run defence | s.healing_monks_own | +0.0007 (+/- 0.0003) | 6 of 6 | 0.659 (at or below 3) -> 0.697 (above 3) |

## Per node

**capture speed** (R.3; 253 matches, 2255 rows, mean absolute error (s)): 91 variables screened, 0 passed the screen

**collapse** (R.1; 242 matches, 1687 rows, log loss): 90 variables screened, 15 passed the screen
- s.lord_dps_enemy: screen +0.0029, confirmed +0.0028 (+/- 0.0016, 4 of 6 folds up): not clear yet
- s.healing_monks_enemy: screen +0.0021, confirmed +0.0041 (+/- 0.0011, 6 of 6 folds up): discovery (held for Denning)
- b.own_energy_denial_v_enemy_heals: screen +0.0021, confirmed +0.0025 (+/- 0.0026, 4 of 6 folds up): not clear yet
- b.enemy_heals: screen +0.0020, confirmed +0.0021 (+/- 0.0012, 4 of 6 folds up): not clear yet
- b.own_knockdowns: screen +0.0024, confirmed +0.0005 (+/- 0.0014, 3 of 6 folds up): not clear yet
- s.morale_diff: screen +0.0028, confirmed +0.0021 (+/- 0.0014, 5 of 6 folds up): not clear yet

**fight outcome** (R.2; 265 matches, 2009 rows, log loss): 85 variables screened, 6 passed the screen
- s.morale_total: screen +0.0032, confirmed +0.0101 (+/- 0.0013, 6 of 6 folds up): discovery (held for Denning)
- b.own_hexes: screen +0.0021, confirmed +0.0048 (+/- 0.0014, 6 of 6 folds up): discovery (held for Denning)
- b.own_knockdowns: screen +0.0014, confirmed +0.0020 (+/- 0.0017, 4 of 6 folds up): not clear yet
- b.enemy_energy_denial_v_own_heals: screen +0.0014, confirmed +0.0043 (+/- 0.0009, 6 of 6 folds up): discovery (held for Denning)
- b.own_heals: screen +0.0007, confirmed +0.0028 (+/- 0.0006, 6 of 6 folds up): discovery (held for Denning)
- s.split_diff: screen +0.0007, confirmed +0.0003 (+/- 0.0013, 3 of 6 folds up): not clear yet

**flag swing** (R.3; 266 matches, 10306 rows, mean absolute error (s)): 87 variables screened, 1 passed the screen
- s.turtle_diff: screen +0.0108, confirmed +0.0256 (+/- 0.0138, 5 of 6 folds up): not clear yet
- s.no_healer_groups_diff: screen +0.0060, confirmed +0.0261 (+/- 0.0196, 5 of 6 folds up): not clear yet
- s.healing_monks_enemy: screen +0.0044, confirmed +0.0109 (+/- 0.0086, 4 of 6 folds up): not clear yet
- s.map_pit_to_stand: screen +0.0012, confirmed -0.0050 (+/- 0.0087, 3 of 6 folds up): not clear yet
- s.morale_total: screen +0.0011, confirmed +0.0067 (+/- 0.0115, 3 of 6 folds up): not clear yet
- b.enemy_snares_v_own_speed: screen +0.0033, confirmed -0.0175 (+/- 0.0259, 3 of 6 folds up): not clear yet

**pit npc loss** (R.5; 264 matches, 27063 rows, log loss): 89 variables screened, 1 passed the screen
- s.main_diff: screen +0.0007, confirmed +0.0001 (+/- 0.0006, 4 of 6 folds up): not clear yet
- s.fight_state: screen +0.0007, confirmed +0.0006 (+/- 0.0007, 5 of 6 folds up): not clear yet
- s.lord_health_diff: screen +0.0008, confirmed +0.0009 (+/- 0.0009, 4 of 6 folds up): not clear yet
- b.own_interrupts: screen +0.0005, confirmed +0.0007 (+/- 0.0004, 5 of 6 folds up): not clear yet
- s.alive_diff: screen +0.0005, confirmed +0.0012 (+/- 0.0006, 5 of 6 folds up): not clear yet
- s.down_diff_s: screen +0.0006, confirmed +0.0008 (+/- 0.0008, 4 of 6 folds up): not clear yet

**power play** (K.4; 265 matches, 2503 rows, log loss): 88 variables screened, 8 passed the screen
- s.fight_state: screen +0.0053, confirmed +0.0057 (+/- 0.0040, 5 of 6 folds up): not clear yet
- s.morale_diff: screen +0.0038, confirmed +0.0045 (+/- 0.0020, 5 of 6 folds up): discovery (held for Denning)
- s.pit_pressure_diff: screen +0.0032, confirmed +0.0045 (+/- 0.0028, 4 of 6 folds up): not clear yet
- s.main_diff: screen +0.0022, confirmed +0.0026 (+/- 0.0026, 4 of 6 folds up): not clear yet
- b.enemy_strips_v_own_prots: screen +0.0013, confirmed +0.0023 (+/- 0.0008, 5 of 6 folds up): discovery (held for Denning)
- b.own_heals: screen +0.0012, confirmed +0.0017 (+/- 0.0010, 4 of 6 folds up): not clear yet

**run defence** (R.3; 265 matches, 8816 rows, log loss): 85 variables screened, 1 passed the screen
- b.own_blind_v_enemy_condition_removal: screen +0.0015, confirmed +0.0033 (+/- 0.0018, 4 of 6 folds up): not clear yet
- b.enemy_snares_v_own_speed: screen +0.0004, confirmed +0.0009 (+/- 0.0004, 5 of 6 folds up): discovery (held for Denning)
- b.own_area_damage: screen +0.0005, confirmed +0.0011 (+/- 0.0004, 5 of 6 folds up): discovery (held for Denning)
- b.own_snares_v_enemy_speed: screen +0.0005, confirmed +0.0001 (+/- 0.0003, 3 of 6 folds up): not clear yet
- s.spike_killable_diff: screen +0.0004, confirmed +0.0006 (+/- 0.0006, 5 of 6 folds up): not clear yet
- s.healing_monks_own: screen +0.0004, confirmed +0.0007 (+/- 0.0003, 6 of 6 folds up): discovery (held for Denning)

**run outcome** (R.3; 265 matches, 8816 rows, log loss): 87 variables screened, 1 passed the screen
- s.down_diff_s: screen +0.0012, confirmed +0.0021 (+/- 0.0006, 6 of 6 folds up): discovery (held for Denning)
- b.enemy_blind_v_own_condition_removal: screen +0.0011, confirmed +0.0024 (+/- 0.0018, 4 of 6 folds up): not clear yet
- b.enemy_snares_v_own_speed: screen +0.0005, confirmed -0.0000 (+/- 0.0004, 2 of 6 folds up): not clear yet
- b.own_blind_v_enemy_condition_removal: screen +0.0007, confirmed +0.0015 (+/- 0.0014, 3 of 6 folds up): not clear yet
- b.enemy_knockdowns_v_own_aura_of_stability: screen +0.0007, confirmed +0.0016 (+/- 0.0013, 5 of 6 folds up): not clear yet
- s.healing_monks_enemy: screen +0.0005, confirmed +0.0007 (+/- 0.0003, 5 of 6 folds up): not clear yet

**split answer** (P.11; 189 matches, 743 rows, mean absolute error (s)): 88 variables screened, 5 passed the screen
- s.spike_build_own: screen +0.1431, confirmed +0.3259 (+/- 0.1631, 5 of 6 folds up): not clear yet
- s.spike_killable_diff: screen +0.1298, confirmed +0.1735 (+/- 0.2492, 4 of 6 folds up): not clear yet
- s.main_diff: screen +0.0811, confirmed +0.3930 (+/- 0.1418, 6 of 6 folds up): discovery (held for Denning)
- b.own_strips_v_enemy_prots: screen +0.0867, confirmed +0.1607 (+/- 0.1325, 5 of 6 folds up): not clear yet
- b.own_area_damage: screen +0.0497, confirmed +0.2208 (+/- 0.0975, 6 of 6 folds up): discovery (held for Denning)
- s.lord_dps_own: screen +0.0716, confirmed +0.2741 (+/- 0.1965, 5 of 6 folds up): not clear yet

**split chance** (A.allocation; 266 matches, 20099 rows, log loss): 82 variables screened, 11 passed the screen
- s.spike_build_own: screen +0.0044, confirmed +0.0050 (+/- 0.0012, 5 of 6 folds up): discovery (held for Denning)
- b.own_knockdowns: screen +0.0030, confirmed +0.0042 (+/- 0.0011, 6 of 6 folds up): discovery (held for Denning)
- s.map_flag_run: screen +0.0017, confirmed +0.0028 (+/- 0.0010, 5 of 6 folds up): discovery (held for Denning)
- b.own_prots: screen +0.0015, confirmed +0.0016 (+/- 0.0009, 4 of 6 folds up): not clear yet
- b.own_knockdowns_v_enemy_aura_of_stability: screen +0.0016, confirmed +0.0015 (+/- 0.0013, 3 of 6 folds up): not clear yet
- b.own_energy_denial: screen +0.0018, confirmed +0.0020 (+/- 0.0010, 4 of 6 folds up): not clear yet

**split effect** (R.5; 189 matches, 743 rows, log loss): 86 variables screened, 7 passed the screen
- b.own_escapes_power: screen +0.0059, confirmed +0.0048 (+/- 0.0018, 6 of 6 folds up): discovery (held for Denning)
- s.minute: screen +0.0044, confirmed +0.0041 (+/- 0.0023, 5 of 6 folds up): not clear yet
- b.enemy_escapes_power: screen +0.0056, confirmed +0.0051 (+/- 0.0042, 4 of 6 folds up): not clear yet
- s.turtle_diff: screen +0.0036, confirmed +0.0056 (+/- 0.0013, 6 of 6 folds up): discovery (held for Denning)
- b.own_area_damage: screen +0.0029, confirmed -0.0010 (+/- 0.0044, 5 of 6 folds up): not clear yet
- b.own_deep_wound: screen +0.0023, confirmed -0.0038 (+/- 0.0063, 4 of 6 folds up): not clear yet

