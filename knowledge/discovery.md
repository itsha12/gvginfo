# What discovery found

Step 3 of the learned causal map (`discover.py`): the variable catalogue (`catalogue.py`: what each team did in the 10 s and 30 s before a moment, generated from the replay schema; decision and execution variables only) tested against every learned node on matches the node never saw. A **pass** predicts what the node misses by more than twice its spread, in at least 5 of 6 held-out folds. A candidate is **offered** to Denning once it has passed in two runs (the two-run rule): approve (it becomes a link in the causal map and an input of the node), reject, or wait.

Variables tested: 1633 (variable by node); 137 passed the screen, where chance alone would pass about 38 (2.3% at twice the spread). Treat a candidate as a lead.

Nothing offered yet (no candidate has passed in two runs).

## Passed once (waits for a second run)

- split answer: p.own_heal_30s +0.1494 (+/- 0.0701), 5 of 6 folds up
- split answer: p.enemy_heal_30s +0.1031 (+/- 0.0401), 5 of 6 folds up
- pit npc loss: p.enemy_dm_npcs_10s +0.0109 (+/- 0.0018), 6 of 6 folds up
- pit npc loss: p.diff_dm_npcs_10s +0.0083 (+/- 0.0015), 6 of 6 folds up
- pit npc loss: p.enemy_dm_npcs_30s +0.0074 (+/- 0.0016), 6 of 6 folds up
- split effect: p.own_frontline_moving_s_30s +0.0054 (+/- 0.0020), 5 of 6 folds up
- pit npc loss: p.diff_dm_npcs_30s +0.0050 (+/- 0.0010), 6 of 6 folds up
- split effect: p.own_frontline_moving_s_10s +0.0047 (+/- 0.0017), 5 of 6 folds up
- power play: p.diff_moving_s_10s +0.0032 (+/- 0.0011), 6 of 6 folds up
- power play: p.own_casts_10s +0.0024 (+/- 0.0005), 6 of 6 folds up
- split effect: p.own_frontline_dm_npcs_30s +0.0022 (+/- 0.0007), 6 of 6 folds up
- power play: p.own_backline_dm_npcs_30s +0.0021 (+/- 0.0007), 5 of 6 folds up
- collapse: p.own_midline_deaths_30s +0.0019 (+/- 0.0008), 5 of 6 folds up
- split chance: p.own_moving_s_30s +0.0019 (+/- 0.0005), 5 of 6 folds up
- split chance: p.own_moving_s_10s +0.0017 (+/- 0.0005), 5 of 6 folds up
- fight outcome: p.own_casts_10s +0.0017 (+/- 0.0005), 6 of 6 folds up
- fight outcome: p.own_backline_heal_30s +0.0017 (+/- 0.0005), 6 of 6 folds up
- fight outcome: p.own_backline_interrupts_30s +0.0013 (+/- 0.0006), 5 of 6 folds up
- fight outcome: p.diff_dm_players_10s +0.0013 (+/- 0.0006), 5 of 6 folds up
- run outcome: p.own_dm_players_30s +0.0012 (+/- 0.0005), 5 of 6 folds up
- fight outcome: p.own_conditions_on_enemies_30s +0.0011 (+/- 0.0005), 5 of 6 folds up
- run outcome: p.own_dm_healers_10s +0.0010 (+/- 0.0003), 6 of 6 folds up
- run outcome: p.diff_dm_healers_10s +0.0010 (+/- 0.0002), 6 of 6 folds up
- run outcome: p.own_frontline_dm_healers_10s +0.0009 (+/- 0.0002), 6 of 6 folds up
- collapse: p.own_frontline_heal_10s +0.0006 (+/- 0.0003), 5 of 6 folds up
- run defence: p.diff_dm_healers_10s +0.0005 (+/- 0.0002), 5 of 6 folds up
- split chance: p.diff_heal_10s +0.0004 (+/- 0.0002), 5 of 6 folds up

## Per node

**capture speed** (R.3; 340 matches, 2988 rows, mean absolute error (s)): 149 variables screened, 0 passed the screen

**collapse** (R.1; 325 matches, 2251 rows, log loss): 148 variables screened, 14 passed the screen
- p.own_midline_deaths_30s: screen +0.0018, confirmed +0.0019 (+/- 0.0008, 5 of 6 folds up): discovery (held for Denning)
- p.own_frontline_heal_10s: screen +0.0019, confirmed +0.0006 (+/- 0.0003, 5 of 6 folds up): discovery (held for Denning)
- p.own_deaths_30s: screen +0.0018, confirmed +0.0017 (+/- 0.0013, 4 of 6 folds up): not clear yet
- p.own_frontline_cancels_10s: screen +0.0014, confirmed +0.0010 (+/- 0.0006, 4 of 6 folds up): not clear yet
- p.diff_deaths_30s: screen +0.0013, confirmed +0.0014 (+/- 0.0009, 4 of 6 folds up): not clear yet
- p.own_dm_players_10s: screen +0.0011, confirmed +0.0001 (+/- 0.0008, 2 of 6 folds up): not clear yet

**fight outcome** (R.2; 355 matches, 2718 rows, log loss): 148 variables screened, 11 passed the screen
- p.own_backline_heal_30s: screen +0.0010, confirmed +0.0017 (+/- 0.0005, 6 of 6 folds up): discovery (held for Denning)
- p.own_casts_10s: screen +0.0005, confirmed +0.0017 (+/- 0.0005, 6 of 6 folds up): discovery (held for Denning)
- p.diff_dm_players_10s: screen +0.0004, confirmed +0.0013 (+/- 0.0006, 5 of 6 folds up): discovery (held for Denning)
- p.own_conditions_on_enemies_30s: screen +0.0005, confirmed +0.0011 (+/- 0.0005, 5 of 6 folds up): discovery (held for Denning)
- p.own_backline_interrupts_30s: screen +0.0005, confirmed +0.0013 (+/- 0.0006, 5 of 6 folds up): discovery (held for Denning)
- p.own_backline_deaths_30s: screen +0.0004, confirmed +0.0015 (+/- 0.0006, 4 of 6 folds up): not clear yet

**flag swing** (R.3; 356 matches, 13520 rows, mean absolute error (s)): 148 variables screened, 0 passed the screen
- p.own_knockdown_s_10s: screen +0.0039, confirmed +0.0042 (+/- 0.0079, 3 of 6 folds up): not clear yet
- p.diff_dm_healers_30s: screen +0.0137, confirmed +0.0060 (+/- 0.0211, 5 of 6 folds up): not clear yet
- p.own_midline_deaths_10s: screen +0.0033, confirmed +0.0005 (+/- 0.0086, 3 of 6 folds up): not clear yet
- p.enemy_moving_s_10s: screen +0.0003, confirmed -0.0034 (+/- 0.0065, 3 of 6 folds up): not clear yet
- p.own_dm_healers_30s: screen +0.0021, confirmed +0.0024 (+/- 0.0092, 4 of 6 folds up): not clear yet
- p.own_backline_dm_healers_30s: screen +0.0034, confirmed +0.0012 (+/- 0.0037, 3 of 6 folds up): not clear yet

**pit npc loss** (R.5; 354 matches, 35789 rows, log loss): 150 variables screened, 14 passed the screen
- p.enemy_dm_npcs_10s: screen +0.0073, confirmed +0.0109 (+/- 0.0018, 6 of 6 folds up): discovery (held for Denning)
- p.diff_dm_npcs_10s: screen +0.0055, confirmed +0.0083 (+/- 0.0015, 6 of 6 folds up): discovery (held for Denning)
- p.enemy_dm_npcs_30s: screen +0.0048, confirmed +0.0074 (+/- 0.0016, 6 of 6 folds up): discovery (held for Denning)
- p.diff_dm_npcs_30s: screen +0.0034, confirmed +0.0050 (+/- 0.0010, 6 of 6 folds up): discovery (held for Denning)
- p.own_dm_players_10s: screen +0.0008, confirmed +0.0005 (+/- 0.0003, 5 of 6 folds up): not clear yet
- p.own_backline_dm_players_30s: screen +0.0007, confirmed +0.0006 (+/- 0.0003, 5 of 6 folds up): not clear yet

**power play** (K.4; 353 matches, 3277 rows, log loss): 148 variables screened, 8 passed the screen
- p.enemy_moving_s_10s: screen +0.0016, confirmed +0.0017 (+/- 0.0013, 4 of 6 folds up): not clear yet
- p.diff_moving_s_10s: screen +0.0015, confirmed +0.0032 (+/- 0.0011, 6 of 6 folds up): discovery (held for Denning)
- p.enemy_moving_s_30s: screen +0.0013, confirmed +0.0015 (+/- 0.0013, 4 of 6 folds up): not clear yet
- p.own_casts_10s: screen +0.0011, confirmed +0.0024 (+/- 0.0005, 6 of 6 folds up): discovery (held for Denning)
- p.own_backline_dm_npcs_30s: screen +0.0009, confirmed +0.0021 (+/- 0.0007, 5 of 6 folds up): discovery (held for Denning)
- p.own_interrupts_on_healers_30s: screen +0.0012, confirmed +0.0007 (+/- 0.0010, 4 of 6 folds up): not clear yet

**run defence** (R.3; 355 matches, 11585 rows, log loss): 148 variables screened, 6 passed the screen
- p.enemy_dm_players_30s: screen +0.0009, confirmed +0.0010 (+/- 0.0007, 5 of 6 folds up): not clear yet
- p.enemy_dm_healers_10s: screen +0.0008, confirmed +0.0008 (+/- 0.0004, 5 of 6 folds up): not clear yet
- p.enemy_dm_healers_30s: screen +0.0007, confirmed +0.0007 (+/- 0.0006, 4 of 6 folds up): not clear yet
- p.diff_dm_healers_10s: screen +0.0006, confirmed +0.0005 (+/- 0.0002, 5 of 6 folds up): discovery (held for Denning)
- p.enemy_attacks_30s: screen +0.0006, confirmed +0.0005 (+/- 0.0005, 3 of 6 folds up): not clear yet
- p.enemy_dm_players_10s: screen +0.0007, confirmed +0.0007 (+/- 0.0004, 5 of 6 folds up): not clear yet

**run outcome** (R.3; 355 matches, 11585 rows, log loss): 149 variables screened, 18 passed the screen
- p.own_dm_players_30s: screen +0.0009, confirmed +0.0012 (+/- 0.0005, 5 of 6 folds up): discovery (held for Denning)
- p.diff_deaths_10s: screen +0.0012, confirmed +0.0013 (+/- 0.0009, 5 of 6 folds up): not clear yet
- p.own_dm_healers_10s: screen +0.0009, confirmed +0.0010 (+/- 0.0003, 6 of 6 folds up): discovery (held for Denning)
- p.diff_dm_healers_10s: screen +0.0008, confirmed +0.0010 (+/- 0.0002, 6 of 6 folds up): discovery (held for Denning)
- p.own_deaths_10s: screen +0.0012, confirmed +0.0012 (+/- 0.0010, 5 of 6 folds up): not clear yet
- p.own_frontline_dm_healers_10s: screen +0.0007, confirmed +0.0009 (+/- 0.0002, 6 of 6 folds up): discovery (held for Denning)

**split answer** (P.11; 250 matches, 968 rows, mean absolute error (s)): 147 variables screened, 32 passed the screen
- p.own_heal_10s: screen +0.1380, confirmed +0.1339 (+/- 0.0686, 5 of 6 folds up): not clear yet
- p.own_heal_30s: screen +0.1263, confirmed +0.1494 (+/- 0.0701, 5 of 6 folds up): discovery (held for Denning)
- p.enemy_heal_30s: screen +0.1234, confirmed +0.1031 (+/- 0.0401, 5 of 6 folds up): discovery (held for Denning)
- p.own_midline_dm_players_30s: screen +0.1330, confirmed +0.1241 (+/- 0.0641, 5 of 6 folds up): not clear yet
- p.own_casts_30s: screen +0.1007, confirmed +0.0588 (+/- 0.0817, 4 of 6 folds up): not clear yet
- p.own_moving_s_30s: screen +0.1003, confirmed +0.0406 (+/- 0.0780, 4 of 6 folds up): not clear yet

**split chance** (A.allocation; 356 matches, 26277 rows, log loss): 150 variables screened, 23 passed the screen
- p.own_moving_s_10s: screen +0.0016, confirmed +0.0017 (+/- 0.0005, 5 of 6 folds up): discovery (held for Denning)
- p.own_moving_s_30s: screen +0.0016, confirmed +0.0019 (+/- 0.0005, 5 of 6 folds up): discovery (held for Denning)
- p.own_frontline_moving_s_10s: screen +0.0008, confirmed +0.0009 (+/- 0.0005, 5 of 6 folds up): not clear yet
- p.enemy_moving_s_30s: screen +0.0006, confirmed +0.0006 (+/- 0.0004, 4 of 6 folds up): not clear yet
- p.own_frontline_moving_s_30s: screen +0.0006, confirmed +0.0009 (+/- 0.0005, 4 of 6 folds up): not clear yet
- p.diff_heal_10s: screen +0.0003, confirmed +0.0004 (+/- 0.0002, 5 of 6 folds up): discovery (held for Denning)

**split effect** (R.5; 250 matches, 968 rows, log loss): 148 variables screened, 11 passed the screen
- p.own_frontline_moving_s_10s: screen +0.0036, confirmed +0.0047 (+/- 0.0017, 5 of 6 folds up): discovery (held for Denning)
- p.own_frontline_dm_npcs_30s: screen +0.0027, confirmed +0.0022 (+/- 0.0007, 6 of 6 folds up): discovery (held for Denning)
- p.own_backline_dm_healers_30s: screen +0.0038, confirmed +0.0039 (+/- 0.0028, 4 of 6 folds up): not clear yet
- p.own_frontline_moving_s_30s: screen +0.0045, confirmed +0.0054 (+/- 0.0020, 5 of 6 folds up): discovery (held for Denning)
- p.diff_dm_players_30s: screen +0.0025, confirmed +0.0023 (+/- 0.0022, 3 of 6 folds up): not clear yet
- p.own_backline_dm_healers_10s: screen +0.0015, confirmed +0.0032 (+/- 0.0022, 5 of 6 folds up): not clear yet

