# Instructions for Claude working in this repository

This repo is Denning's Guild Wars 1 GvG portal and data store. He plays GvG only.

## Answering questions
- Skill facts come from `data/skills.json` (PvP-legal skills only; split skills use their "(PvP)" version).
  Query it with a short Python script instead of reading the whole file into context.
  Fields: id (in-game id), template_id (id used in template codes), name, prof, attr, type, elite, energy, adrenaline,
  sacrifice, upkeep, overcast, activation, recharge, desc (ranges written a..b = rank 0..15), prog (values at ranks 0-21),
  causes, removes, prevents, requires, target, range, aoe, flags, notes (wiki bug/anomaly notes), icon.
- Denning's own tested notes live in `data/skill_notes.json` ({skill id: [notes]}). They override the wiki.
- Mechanics and formulas: `knowledge/`, one page per topic (`index.json` lists them with titles and groups, e.g.
  `conditions.md`, `damage.md`, `weapon-mods.md`, `master-of-damage.md`, `gvg-rules.md`). Lines starting
  **Tested (date):** are Denning's own in-game results and override everything else; `misc.md` holds tested findings
  that don't fit another page.
- Damage/DPS math: `tools/gw_calc.py`. Show assumptions (ranks, armor, weapon, crit chance, modifiers).
- Template codes: `tools/gwtemplate.py` (encode/decode; maps PvP ids to template ids automatically).
- His saved bars: `data/templates.json` (folders → templates → variations, each with a template code).
- Match data from gvg.report (estimates from an in-game observer; AT/mAT matches it recorded):
  - `data/matches/YYYY-MM.json`: one record per match; players have n (character name), pos (party slot 1-8 as on
    gvg.report), p/s (professions), bar (8 in-game
    skill ids), full (all slots observed), attrs (effective ranks where known), dmg, heal, taken, prev (damage prevented),
    deaths, kd (knockdowns dealt), intr (interrupts landed), cond/hexr (removals), hp, weapons, and
    sk = {skill id: [casts, damage, healing incl. Divine Favor, prevented, knockdowns, interrupts]}.
  - Summaries: `data/recent.json` (lineups in party order), `data/builds.json` (families → variations with codes and
    derived runes), `data/guilds.json` (per guild: record, maps, usual lineup per map by party slot, players, recent
    results), `data/players.json`,
    `data/skill_stats.json` (per-skill totals; divide by casts for per-use averages), `data/meta.json` (per month).
  - Per-minute player rates use full match length. Character names are not accounts.
- Wiki change log after each skill refresh: `data/wiki_changes.json`.
- gvg.report sometimes records split skills by their original id (e.g. Soul Twisting 1240, "Coward!" 869) instead of
  the PvP id; `aggregate.mjs` translates them with `template_id_map.json` before building anything. Raw match files
  may still hold original ids — use the same translation when querying them.
- Bar order everywhere: elite first, then the build family's skills from most to least common (then attribute, name),
  so variations line up. Done in `tools/gvgreport/aggregate.mjs` (`orderBar`).
- Runes: derived from bonus ranks (+1 Minor, +2 Major, +3 Superior, +4 Superior + headgear). When Denning gives runes or
  insignias for a build, put them in `data/build_gear.json` (by family id or exact code); they replace derived runes.
  gvg.report doesn't resolve runes or insignias.
- Tournament schedule, map rotation and flux: `assets/js/schedule.js`. Source of truth is the Guild Wars Wiki only:
  wiki.guildwars.com/wiki/Automated_tournament (AT-A/AT-C start times in UTC by weekday, monthly map rotation) and
  wiki.guildwars.com/wiki/Flux (flux by month, changes 07:00 UTC on the 1st). Times stay in UTC and are shown in
  Eastern time only (no UTC shown). No AT-B. Don't use gvg.report for schedule data. Rows are "evenings": a start
  between midnight and 6 a.m. is listed on the previous day's row (Denning's preference).
- Build themes (`theme` in builds.json): core = skills on 70%+ of a family's bars, optional = the rest on 5%+.
- Guild usual lineup (`guilds.json`): a lineup the guild actually played, chosen as the one sharing the most builds with
  their other games (per map too), so it never shows combinations they never ran; plus their most played full lineups.
- gvg.report endpoints: `/api/players` (directory, paged), `/api/tournament-rankings?period=all` (guild Elo),
  `/api/guilds`; the probe workflow lists the rest (branch `probe`, `endpoints.txt`).
- Combat-minute stats: `data/player_combat.json` from gvg.report `/api/player-categories?period=all` (fetched by
  `tools/gvgreport/player_stats.mjs` during "Update matches"): per character c (combat ms), m (matches), x (totals for
  damage, kills, assists, healing, prevented, cleanses, interrupts, fake casts, damage taken, knockdowns taken, deaths,
  distance). Only leaderboard-qualified characters are included.
- Match replays: trimmed gvg.report replays live on the `replays` branch (not main): `index.json` lists them,
  `YYYY-MM/<report id>.json.gz` holds one match, `maps/<map id>.json.gz` holds map outlines. Format and field meanings
  are documented at the top of `tools/gvgreport/replay_trim.mjs` (times in tenths of a second of match time). Fetched
  by the "Fetch replays" workflow from `replays/requests.txt` on main. Read them with a short script, never whole.
  Beside each replay, `YYYY-MM/<report id>.x.json.gz` holds what the trim leaves out (format at the top of
  `tools/gvgreport/replay_extras.mjs`; `x` in the index is its version): gvg.report's flag objects (R-481), Lord damage
  record (R-632), what each prot did, degen, interrupt attempts and death and spike-save recaps (R-636 to R-639), and its
  energy model (each player's least and most energy every two seconds; the engine is to read it, R-664). It uses the replay's agent numbers and clock. A new version of it fetches both payloads again and writes
  only that file: a stored replay is never written again. On the branch the engine reads it through `Match.extras()`
  (`tools/replay_analysis/extras.py`: an `Extras`, with `lord_record()` for gvg.report's Lord record by the second;
  `python3 extras.py cover` counts what every stored match holds). A match with no file stops the reading (R-460):
  fetch the `replays` branch again. Read so far: the flag objects, the Lord record, degen and energy; the rest is listed under
  "The engine on the new trim" in `docs/ENGINE_NOTES.md` (section 8).
- Replay analysis toolkit: `tools/replay_analysis/` (`replaylib.py` = Match class: positions, groups, sides, carries,
  build-based role names; `report.py <report id> [builds phases stand npcs lord deaths totals]` = the standard review
  tables). Start every match review from `report.py`, then dig into specific moments with `replaylib`. Improve these
  tools rather than writing one-off scripts, so later reviews reuse what was learned.
- Match analysis: `knowledge/tactics.md` is the general model of how GvG is won, organized by situation (win
  conditions and edges, macro vs micro, builds, splits, main team and pit, flag game, kills and timing, late game,
  spikes, monk play, interrupts, positioning, situation cards, open questions). **Denning:** lines override everything. Use it to judge
  decisions and to answer "what should they have done" questions, with a confidence level.
- `knowledge/match-reviews.md` holds one entry per reviewed match (summary paragraph, decided by macro, micro or both,
  deciding moments, what comms or commentary added). Match tags such as [Men v Team] link the two pages.
- After each review: add the entry to match-reviews.md; turn its lessons into general **Claude:** lines on
  tactics.md under the right situation, each ending with match tags as evidence; when a new match contradicts a line,
  revise it rather than adding a second one; add Denning's answers as **Denning:** lines (no dates). Keep the tactics
  page a model, not a log: merge duplicates and keep match detail on the reviews page.
- The engine's documents, and what each is for. At the start of a chat read only `docs/HANDOFF.md` (this file is
  already loaded); open the others when the task needs them:
  - `docs/HANDOFF.md`: under 80 lines: state, next step, open rulings. Rewritten, not appended.
  - `docs/ENGINE_NOTES.md`: how each engine reading is built and what it is tested against (index below). Read the
    section for a reading before changing it, and update it in the same session.
  - `docs/SPEC.md`: the engine as it is now (tiers, nodes, decisions, the rules every node follows). Current state
    only; edits replace text, nothing is appended with a date. (Until the close it describes the engine on main,
    which `bundle-4` replaces.)
  - `docs/REDESIGN.md`: the plan for the decision tier (families, scenarios, calls, steps and gates).
  - `docs/RULINGS.md`: Denning's definitions and decisions, numbered R-nnn, never renumbered; new rulings are appended
    with the next number. A ruling overrides Claude's reasoning. Cite the number, don't re-litigate. Search it; never
    read it whole.
  - `docs/DEFINITIONS.md`: the current definitions by topic (counting players, flags, splits, collapse, the Lord push
    so far), each line citing its rulings (R-452). Read it instead of hunting through the register; when a ruling
    changes a definition, replace the line here in the same session and mark the amended ruling where it stands.
  - `docs/EXECUTION.md`: the execution catalogue: every why of a kill or a death, the rules Denning set for each
    (R-716 to R-793), the skill tags, the skills worth interrupting, the limits of the data and the order of work. Read it before any
    execution work; replaced in place, its "Read" column kept current.
  - `docs/CHANGELOG.md`: dated session log, newest first, at most ten lines per session. Never read it whole.
  - `knowledge/model.md`: generated each run, the structural reference (every fitted node, rows, inputs by kind,
    held-out score). If a node can't be explained in GvG terms from that page, it isn't explainable yet.
  - `tools/replay_analysis/METHODS.md`: how each concept is measured (reference, not history).
  Deep reviews start from `analyze.py <id>` (scoreboard, fights, decision points, findings), then `fights.py <id>
  fights`, `scoreboard.py`, `report.py` and `episodes.py` for detail. Judge flag position with the scoreboard's flag
  lead, never from who holds the stand. Thresholds live in `common.py`. Findings and situation cards cite tactics
  line ids (`F1`, `S18`...); keep ids stable.
- The goal is plays better than experts can see, from data: values and best plays come from measurement, never from
  guessed weights or defaults. The win-probability model must stay white box (readable contributions, explanation
  breakdowns, Denning's logged corrections) and is trained a few matches at a time with a learning report after each
  batch (METHODS.md "From rulings to data", "A training round"). Explain the learning report to Denning in words,
  with match moments; his corrections go in `data/model_corrections.json` with his reason. Denning: after each batch
  give a snapshot across all the learnings, not one highlighted item, and favour the detailed ones (skills cast, run
  times, runners, node-model readings, values, usual play, discovery).
- Matches count from 1 September 2026 (Denning): replays before `common.TRAIN_FROM` are left out of training and of
  replay benchmarks, and new picks start at `common.PICK_FROM` (2 September); strength and lineup ratings still use
  every result (METHODS.md "Which matches count"). Games in which a team fields a henchman are out the same way
  (R-476, R-477: `data/model/henchman_games.json`; run `integrity.py henchmen` on the branch after replays are
  fetched). Use `common.replay_ids()` for any new replay pool.
- Data integrity first (`integrity.py`, inside `Match()`): match length repaired, pit NPCs never seen in a replay added
  from the standard roster (2 knights, 2 archers, Bodyguard, Lord; 3 archers on Isle of Solitude), unobserved Lord damage
  left blank. Strength is the measured blend of the guild's fitted rating and the lineup who played (`strength.py`,
  `lineup.py`); `lord.py` rebuilds Lord health; `fightstate.py` gives who is winning the fight; `behaviour.py` gives
  leverage and behaviour clusters (responses nobody named, for Denning to name). gvg.report's player directory and guild Elo are synced to `data/gvgreport/`
  (`tools/gvgreport/directory.mjs`); its player groupings are merged into aliases.json with Denning's assignments
  winning (`merge_players.py`, additions under `gvgreport_added`). Today's Elo table must not train the model (it
  includes later results): `strength.py` rebuilds that Elo in time order.
- Every "why" is answered with data (Denning): `forensics.py` answers the questions behind a death (position, prots and
  whether they were the right kind, interrupt pressure on the healers, damage off shield sets, both teams' damage
  output, peel, casting into ready interrupts and cancelling, conditions and their removal), each placed against the
  same role in every stored match (`data/benchmarks/forensics.json`); `events.py` explains the smaller events (flag
  swings, power plays without a kill, survived spikes, pit NPC losses, splits); `why.py` uses both. METHODS.md
  "Answer exemplars" shows the depth expected. When a question can't be answered from the data, say so and add the
  measurement to forensics.py rather than guessing.
- Commentary and comms: claims (paraphrased, never transcripts) in `data/commentary/<source>.json`, lined up with
  `timeline.py`; the variables they suggest are measured in every match by `comms_vars.py` and the supported ones move
  into the model and onto tactics (METHODS.md "Commentary and comms"). Denning: the new variables matter most.
- Speed: `cache.py` keeps every "without this match" model and each match's prepared data (keyed by the engine code);
  run `cache.py sync pull` then `cache.py warm` at the start of a session and `cache.py sync push` after building.
  Never refit a held-out model directly: use `WPModel.heldout` and `nodes.heldout_node` (10 fixed groups of matches,
  `cache.FOLDS`). Cache keys are by layer (`cache.py info`): an edit to a measurement module invalidates prepared data,
  an edit to a report module (tq, learning, causalchain, snapshot, modelpage, advice, ask, behaviour, discover) nothing. Run training
  batches on GitHub with the "Train batch" workflow (METHODS.md "Train batch on GitHub"), not in the chat.
- Tracking: `data/model/match_status.json` (`status.py`) records, per match, its batch, review, commentary state, the
  events whose why was walked through with Denning, and notes. Run `status.py sync` after each batch and `status.py
  mark` after walking Denning through an event.
- Insights must be about decisions and consequences, not correlations. End each analysis with specific questions for
  Denning.
- Writing to Denning in this project (R-329): explain fully, not in shorthand: what is to be done, why, and what he
  should consider. Engine labels (P.26, K.4, R.2, bundle and stage names) are always given with their GvG meaning.
  Whenever something needs his ruling, or he asks what is outstanding, set every item out in the chat itself (what it
  is in GvG terms, what the data says, the options, the recommendation) so he can rule there; never point him to a
  document to find it.
- Site home page is Schedule (`#/`); Recent matches is `#/matches`.
- People: `data/aliases.json` = {"people": {"Person": ["Character", ...]}}, edited from the Players page (tick names,
  assign). Use it when Denning asks about a player by their person name.

## Working rules for the analysis engine (every session)
The full rules, with how each reading is built and the games it is tested against, are in `docs/ENGINE_NOTES.md`
(moved there word for word on 2026-11-24). These are the ones no session may miss:
- `bundle-4` lands in one piece, then one rebuild (R-322); never merge it piecemeal. The branch's own `CLAUDE.md` and
  `docs/` are old copies: main's are the ones kept up to date. No engine change between chunks: one bundled change,
  one rebuild, compared with the reading before it.
- Check the reading after every change (R-453): the development set, then `review.py score` with main's review key.
  A failing Classic row is fixed before anything else (R-494). Full runs only at a checkpoint, and a full run needs
  the machine to itself (a second run beside it hangs without a word). After a change to a record, compare the plays
  with the run before (`tools/golden/compare.py`): nothing may differ but the keys the notes name.
- No new rule or threshold to answer a wrong row (R-465): rebuild the reading at its root, with his marked rows as the
  test. A reading which fails must fail loudly, never become a blank (R-460).
- His marks go into the review key the same session, in his words; an engine fault he points out is a check, not a
  ruling (R-452). Never write cards or rows again over ones he has marked without saying so; Lord push rows and cards
  are marked on the site, never in the chat. No kind of play is used downstream until he says it is ready (R-496).
- Every match moment put to him carries its replay link and the time of the thing he is to look at.
- A verdict is a reading, not advice, until the held-out test shows a gain for its scenario: say so whenever one is
  shown to him. Settle the technical choices yourself; bring him GvG questions only.
- No more matches are trained until the engine is ready (R-570): never propose it as the next step. Before the first
  training run after the engine is built, go through his list (R-398).
- Never decode or print a sealed field (blind picks, golden moments). Transcripts never go in the repo: paraphrased
  statements only.
- Documents: SPEC.md and METHODS.md are replaced in place; the CHANGELOG gets at most ten lines per session; HANDOFF.md
  stays under 80 lines. Don't write session narrative into any other file.
- Before an engine change ships, a fresh session reads `knowledge/model.md` alone and must be able to explain each
  node in GvG terms (the readability test).
- Never add a `.py` file to `tools/replay_analysis/` for site or tooling work: every file there is part of the
  measurement cache key and would force a full rebuild. A scratch script lives outside the repository.
- Engine build notes (how a reading is built, what it is tested against, what was found) go in the section of that
  reading in `docs/ENGINE_NOTES.md`, the same session; a new reading gets the next section number and a line in the
  index below. Never in this file, and in HANDOFF.md only as state.
- The review key, `dev_set.json` and `game_reviews.json` are written on main only: pass `--key
  <main>/data/model/review_key.json` and copy a changed file to the branch. The rows of the Game review's other views
  (`lord_rows.json`, `execution_rows.json`) are written to main the same way; his marks on them are the site's files.
  Files the site saves whole (hall labels, golden and review marks) are his: after a change to one here he reloads the
  page first, and changed `data/maps/labels/*.json` are copied to the branch before a hall is read. Party slots are in
  `data/matches/`, not in the replays. Never queue two Train batch runs.
- A backline monk is told by his bar (`common.monk_kind`, R-698), never by his party slot or his role name.
- A reading built on a gvg.report field is first checked against the raw record on a sample of matches before
  it is used (R-707; e.g. `casting.py cover`).

### Index of `docs/ENGINE_NOTES.md` (read the section before changing that reading)

- 1. One model family in tiers
- 2. Five kinds of input
- 3. Inputs capped by the data
- 4. No engine change between chunks
- 5. Discovery
- 6. Macro and micro answers
- 7. Questions for Denning
- 8. The engine on the new trim: energy, degen, flag returns (stage E, step 2)
- 9. Checking the reading after every change
- 10. The fresh start of 2026-11-15 and his grades
- 11. Which part of a divided team is the main team
- 12. A player counts in one fight only; numbers flickers
- 13. When a split ends and what kills it
- 14. When a split starts
- 15. How flags are told on the page
- 16. A push on a flagger
- 17. A part-run
- 18. A flag handed on; a flag left lying
- 19. A flag held at home
- 20. When the match is over
- 21. The known truths
- 22. The similar cases and the flag family (cards, ladder, advice test)
- 23. The split family and the main fight while a split is out
- 24. The kinds that follow: pushes, holds, base res, opening, hand-offs
- 25. The Lord push and Lord damage
- 26. What each prot did, degen and interrupt attempts (summary data)
- 27. The measurements of R-572: execution, NPC damage, pair rule, split at all, stake
- 28. A numbers advantage from kills is not a family
- 29. The numbers record
- 30. No new rule to answer a wrong row
- 31. Fail loudly
- 32. His marks go into the review key
- 33. Game reviews by whole games
- 34. Documents
- 35. The readability test
- 36. The decision tier rebuild (REDESIGN.md)
- 37. Bundle 4 on its branch: story, records, line-up, gates, stage D, jobs
- 38. Before the next training run (R-398)
- 39. Guild hall maps
- 42. A backline monk, told by his bar (R-698)
- 43. Monk casting efficiency (R-689, piece 4)
- 44. Execution, the build (R-701 to R-793; the catalogue is `docs/EXECUTION.md`)
- 40. The TQs
- 41. The causal map and the old node models

## Rules
- Do not edit `data/skills.json` by hand; it is regenerated from the wiki. Put corrections in `data/skill_notes.json`
  or the matching `knowledge/` page as a **Tested (date):** line.
- When Denning reports a tested mechanic, add a **Tested (date):** line to the page it belongs to (or `misc.md` if none
  fits), and mark the matching row in `test-scenarios.md`. When he asks to change a page, edit only that page.
- Never abbreviate Master of Damage. Don't use "My" in page names or text.
- Victory or Death is no longer in the game; ignore wiki text that describes it.

## Layout
- `index.html`, `assets/` — the portal (static site, GitHub Pages, no build step).
- `data/` — skills, template id map, templates, skill notes.
- `knowledge/` — markdown pages shown on the portal's "Mechanics and rules" page (`index.json` lists them; Misc last).
- `tools/` — calculator (`gw_calc.py`), template codec (`gwtemplate.py`), `gvgreport/` (sync + aggregate, Node),
  `wiki/sync.mjs` (skill refresh, Node), `replay_analysis/` (the
  engine), `maps/` (map data for the site).
- `.github/workflows/` — "Update matches" and "Update skills from the wiki", started from the portal's Recent matches page.
