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
- The engine's documents, and what each is for (read in this order in a new chat):
  - `docs/SPEC.md`: the engine as it is now (tiers, nodes, decisions, the rules every node follows). Current state
    only; edits replace text, nothing is appended with a date.
  - `docs/RULINGS.md`: Denning's definitions and decisions, numbered R-nnn, never renumbered; new rulings are appended
    with the next number. A ruling overrides Claude's reasoning. Cite the number, don't re-litigate.
  - `docs/HANDOFF.md`: under 80 lines: state, next step, open rulings. Rewritten, not appended.
  - `docs/CHANGELOG.md`: dated session log, newest first, at most ten lines per session.
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
- The TQs (Denning's four question categories; the learning report's section "The TQs", `tq.py`, METHODS.md "The TQs")
  are a demonstration of the model after a batch, not part of it; they run every other chunk unless asked. Each is
  answered with data at the depth of METHODS.md "Answer exemplars", in two parts kept apart: macro (was the decision
  the right call: the usual play's choice effects at the decision before) and micro (given the call, what went wrong
  in execution: the execution inputs against the role's benchmark), with what the enemy did described beside them,
  and a confidence level:
  1. Flags: one instance in a batched match where a team got behind on flags, and why; then how a different play could
     have increased its win chances.
  2. Monk death: one instance where a monk died, and why; then how it could have been prevented.
  3. Power play: one instance where a team couldn't kill on a power play, and why; then how it could have been
     converted into kills.
  4. NPCs: one instance where a team lost NPCs, and why; then how it could have been prevented.
- Explaining why comes from the causal map (`data/model/causal_map.json`, METHODS.md "The causal model"): Denning's
  and Claude's reasoning about what causes what, as links whose strength the data measures. Add his answers as links
  (with reason, source and tactics ids) and log every change; keep `knowledge/causal-map.md` rendered. Built so far:
  `phases.py` (phases, plans, jobs, capacities), `buildfeat.py` (build and matchup features), `nodes.py` (node models: deaths,
  kill conversion, flag answers, Lord damage; `explain` for a player's risk second by second; pit NPC loss is the learned
  node `pit_npc_loss` in `learnednodes.py`), `usual.py` (the usual play and each choice's
  effect in win chance, between similar builds), `values.py` (results and causes priced in win points;
  `knowledge/values.md`). Per-player skill flags: `buildfeat.player_flags` (one skill can change the right play).
  Snare and speed power per player (how strong, not just whether): `movepower.py` (Return is an escape, not a snare).
  Pressure beyond damage per player (kiting, degen, baited interrupts, offensive knockdowns, disables, cast
  prevention): `pressure.py` (METHODS.md "After chunk 4").
  Chains from the node models with fixes carried forward to the result: `causalchain.py` (step 4). Discovery: the
  variable catalogue (`catalogue.py`, play variables generated from the replay schema) against every learned node on
  unseen matches, offered after passing twice: `discover.py` and the "Discovery" workflow (step 3). The goal test:
  `advice.py` (does matching the advice do better on unseen matches; the sealed blind test). The query tool: `ask.py`
  (a match and a moment in; state, macro, micro and the enemy's response out). The generated structure page:
  `modelpage.py` -> `knowledge/model.md`.
- Matches count from 1 September 2026 (Denning): replays before `common.TRAIN_FROM` are left out of training and of
  replay benchmarks, and new picks start at `common.PICK_FROM` (2 September); strength and lineup ratings still use
  every result (METHODS.md "Which matches count"). Use `common.replay_ids()` for any new replay pool.
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

## Working rules for the analysis engine (Denning, November 2026 review; RULINGS.md "2026-11 review")
- One model family in tiers (SPEC.md section 4): context, state, decision nodes, execution nodes, win model. Every
  fitted model answers one question and appears once. Don't add a second model for a question a node already answers;
  change the node.
- Every input is one of five kinds (context, state, decision, execution, concurrent response). Context and state are
  adjustment and never a fix. Concurrent response (what the enemy did during the window) is never an input; show it
  apart. Inputs are measured before the window or at a fixed early point in it.
- Inputs are capped by the data (one per 20 events); the cap and the pruning order are in SPEC.md section 5. Every
  decision and execution input carries the selection check ("marks the situation"); such inputs are never fixes.
- No engine change between chunks. Proposals (new variables, decisions, corrections) go on the waiting list in
  `data/model/causal_map.json` and in HANDOFF.md; one bundled engine change per run of chunks, then one rebuild,
  compared against the reading just before it. A text-only change to a report section is not an engine change and
  must not invalidate prepared data (cache keys by layer).
- Discovery offers Denning only decision and execution variables, and only after a candidate passes in two runs.
  State and build variables are never offered (they are already adjustment).
- Answers are macro ("was it the right call": the decision tier) and micro ("what went wrong in carrying it out":
  the execution tier), kept apart, each with its evidence. Enemy response is described beside them.
- Questions for Denning come from the catalogue and cluster mechanisms (name this cluster, approve this candidate),
  not a list of Claude's ideas after each batch.
- Documents: SPEC.md and METHODS.md are replaced in place; the CHANGELOG gets at most ten lines per session; HANDOFF.md
  stays under 80 lines. Don't write session narrative into any other file.
- Before an engine change ships, a fresh session that has not seen the build reads `knowledge/model.md` alone and must
  be able to explain each node in GvG terms (the readability test). The same test covers anything Denning answers or
  reads a verdict on (the blind test page, a decision card): the fresh session must be able to say each option and
  each verdict as a sentence a player would use.
- The decision tier is being rebuilt: `docs/REDESIGN.md` is the plan (families, scenarios, calls, the decision card,
  the steps and their gates). Read it before touching `decisions.py`, `usual.py`, `advice.py`, `ask.py` or `tq.py`.
  Its rulings are R-292 to R-309. Blind rounds are paused meanwhile (Train batch input `blind` stays on no).
- Redesign step 2 (bundle 4) is built on the branch `bundle-4`, never on main piecemeal (R-322): `hallmap.py` (zones
  and walked distances from the labelled halls), `moments.py` (departures, triggers, scenarios, calls) and
  `tools/golden/golden.py` (pick, score) live there until the bundle lands. Golden moments (R-303): Denning labels
  them on Model > Golden moments (`data/model/golden_moments.json`, on main). That file holds only what he wrote;
  never decode or print a moment's `sealed` field in a chat.
  Also on the branch: `story.py <report id> [from] [to]` prints the story so far (R-341: the engine reads a match as
  Denning's notes do: flag forms, every fight with its place and numbers, deaths against the base res, NPCs), and
  `tools/maps/draft_greater_stand.py` drafts each hall's "Greater stand area" (R-334, R-342) into `data/maps/draft/`.
  The golden page (R-354) shows the engine's story of each game (`data/model/golden_stories.json`, from
  `tools/golden/golden.py stories`); he ticks the lines that are wrong with his reason and adds notes or corrections
  (`label.story.wrong`, `label.notes`). The 13 notes marked `blind_note` were written before he saw any story: after
  every change to `story.py`, regenerate the stories and compare them with those notes yourself (the blind check).
  His marks keep the text of the line they were made on.
  The record is the work, not the description (R-362): `Moments.attempts()` (one record a split attempt or main team
  push, R-357, R-358, R-363, R-364), `caught()` (R-359), `flags_record()` (R-360), `main_team()` (R-335, R-355) and
  `common.flux_at` (R-356) hold what the engine keeps; `moments.py <report id> splits|flags` prints them, and `story.py`
  prints its split, push and cap lines from them, never from a second reading. Lessons from his marks, notes or
  commentary go into these records first.
  The line-up is the measure of the reading (R-368 to R-397): timestamped commentary and comms filed as paraphrased
  statements in `data/lineup/` (never transcripts), checked against the story by `tools/golden/lineup.py` on the
  branch. The four held-out games are in `data/lineup/held/`: never print or read their lines before Denning's one
  review at the gate (R-370, R-396), and never tune the engine on them. The line-up only checks that what was said is
  in the story, so run `tools/golden/thresholds.py` beside every rescore to see what a change did to the records over
  all matches. The gates and the build order are in `docs/REDESIGN.md` ("Tests", "Build plan from here").
- Before the first training run after the engine is built, go through Denning's list with him (R-398; REDESIGN.md
  "Before the next training run"): plan and spec, rulings, old files, the Templates and Meta tabs, skills from the
  wiki, the model pages, anything outstanding.
- Guild hall maps: `tools/maps/build_maps.py` builds the site's map data from the replays branch
  (`data/maps/index.json`, `outline/<map id>.json`, `auto/<map id>.json`); Denning's labels (points, areas, routes) are
  saved by the site's Model > Guild hall maps page to `data/maps/labels/<map id>.json` and override estimates. The
  engine does not read outlines or labels yet (REDESIGN.md step 2). `tools/maps/draft_labels.py` drafts labels from
  the replays for Denning to accept (`data/maps/draft/<map id>.json`; `--score <ids>` compares drafts with his labels);
  it never reads or writes his labels, and he keeps choke points, NPCs, gates and hazards for himself. The page draws
  drafts dashed; accepting one copies it into his labels with `from_draft`, removing one adds its id to `dismissed` in
  his labels file, and draft ids are stable so rebuilding the drafts never brings back one he dealt with. gvg.report serves some halls' geometry only by the
  game's map file id (`replays.mjs` MAP_FILE_IDS); to look at any gvg.report endpoint, run the "Probe gvg.report"
  workflow with the endpoint in `pages` (optional `pick` = parts to keep, `grep` = pattern to find in its scripts) and
  read the `probe` branch. `data/maps/<map id>.json` (no subfolder) is the
  engine's own NPC store and is not touched by either. `tools/maps/audit_labels.py` checks his labels against R-310 (pit roster, one res shrine and flag
  spawn a side, equal NPCs, doubles, mirror partners) and never writes them; run it after he labels. What each hall adds to
  decisions (footmen or none, fall-back zones, effects, objects and flag routes by label id, its decisions) is in
  `data/maps/hall_features.json` and `knowledge/guild-halls.md` (R-310 to R-317). A route drawn through a teleporter
  overstates the walk: use its walked length (`audit_labels.py --routes`, R-316). Never add a `.py` file to `tools/replay_analysis/` for site or
  tooling work: every file there is part of the measurement cache key and would force a full rebuild.

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
  `wiki/sync.mjs` (skill refresh, Node), `wiki_scraper.js` (browser version of the scraper), `replay_analysis/` (the
  engine), `maps/` (map data for the site).
- `.github/workflows/` — "Update matches" and "Update skills from the wiki", started from the portal's Recent matches page.
