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
  fetch the `replays` branch again. Read so far: the flag objects and the Lord record; the rest is listed under
  "The engine on the new trim" below.
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
  - `docs/DEFINITIONS.md`: the current definitions by topic (counting players, flags, splits, collapse, the Lord push
    so far), each line citing its rulings (R-452). Read it instead of hunting through the register; when a ruling
    changes a definition, replace the line here in the same session and mark the amended ruling where it stands.
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
- The engine on the new trim (stage E, step 2), on the branch. Built 2026-11-24: the reader (`extras.py`); flag returns
  (R-481); the Lord record (R-632 to R-635, described under "The Lord push and Lord damage"); degen as damage, the
  reading and the first figures that take it in (below). To build, in this order: the rest of the damage figures of
  R-649 (the death accounts, the nodes and the older layers), interrupt attempts (R-639), what each prot did and the
  death and spike-save recaps (R-636), who stripped which enchantment from our own replays (R-637), a hold told with
  what the holders went for (R-658); and energy, which he has settled (R-664 to R-689) and which is built beside these in the order of R-689 (below).
  Energy is one reading, `Match.energy()` (`energy.py`: read its top before using energy anywhere). gvg.report's
  estimate, the least and the most energy a player can have every two seconds, carried as `lo`, `hi` and `mid`; `ok`
  False and every figure blank where a match has none (18 counted matches, R-672). Whose: the backline monks
  (`kind` "monk"), the midline for energy (Ritualist, Mesmer, Elementalist, Necromancer, smite monk: "midline"),
  nobody else (R-665, R-670, R-675). The scale is what a player would have on his double high set now (R-668,
  R-686): shown + (top - the maximum of the set held), top 72 with death penalty or morale on it (an Elementalist's
  top is his own highest maximum in the match). `at(a, t)`, `group(ids, t)` (the average, the lowest player and how
  many, R-683), `out` (a monk under 20, a midline player under 15, R-681 and R-682: "yes" where even the most he can
  have is under it, "maybe" where only the least is). Those two lines are for the excuse only: at a decision no
  line is set and what followed is read across the range of energy there (R-669). `python3 energy.py cover` prints
  the checks of the record (2026-11-24, 546 matches: a team's monks lose 0.7 in 10 s under fire and regain 1.3 at
  rest; a death follows within 20 s 78% of the time where they average under 20 and 7% at 60 or more; a monk is out
  for certain 0.8% of his time alive). Built (2): each fight's energy on every play, a record kept beside the plays
  (`energy.record`, `flag_cost[rid].energy`: no play reads it and none moves): at the second the decision arises
  (`energy.decision_second`: a flag play's `clock.anchor`, a base res 20 s before the res, else `t0`) and 60 s
  before, the backline monks and the midline of our side (a split play's own players, `who`; on every other play our
  main team, since a flag, boost or push play names its runners or pushers) and of theirs (enemy players `linked` to
  ours in the 4 s to it, else their main team, `their_from`), each as `group`, with `team` (every living backline
  monk of each team: what the answer to their split reads, the defenders being the call itself); the split ticks
  and base res spots carry the same. `cases.py energy <plays file>` (report `data/model/energy_cases.json`): for
  each decision of R-688 with a reader (their run, run again from our cap, their boost, down and up at the main
  fight, the answer to their split, our split, the danger zone base res, after a wipe) what followed each call by
  the fight's monk energy (average and lowest monk in thirds of that decision's own cases, R-669; how many monks
  apart), the minute before beside every row, and the danger zone read both ways (damage line and monk energy).
  Not read, at his word: pressing the fight or allowing a stand-off (no decision for now, R-691) and offensive or
  defensive play, which is execution (R-692). The danger zone says the monks' energy of the players in their base
  beside the 300 line, never in its place (R-690: `monk_energy` on `danger.calls`, in the sentence). Taken out at his word: our own monks at "our flag
  just in" (R-693), energy at their boost (R-694), and the send-or-not table of our split (R-695: the decision is a
  split already out staying to kill or falling back, read by its own monks; not built until its definition is
  settled). Left of (2): energy among what like spots are matched on (2026-11-24, 546
  matches: the average told a little more than the lowest monk at most decisions). To build, in his order (R-689):
  (3) the
  excuse, in the death accounts and where a numbers advantage does not kill: who was out, and where the energy of
  the minute before went (spent, taken by the enemy, regained), energy denial read (R-685: Energy Surge and Energy
  Burn deal 7 and 9 damage a point of energy taken, so the energy taken is their damage over that; Mind Wrack to
  confirm), and whom a Mesmer drains read with offensive or defensive play, as execution (R-692); (4) monk casting efficiency
  (R-678 to R-680, R-687), with what each prot did (R-636) and the interrupt attempts (R-639), by monk role
  (R-671): healing landed plus damage prevented for the energy spent, blocks credited to any blocking skill,
  removals a count apart, cancelled casts apart as a bait that worked or energy burned.
  Degen as damage (R-638, R-649, R-655, R-661) is one reading, `Match.degen()` (`degen.py`: read its top before
  touching a damage figure). The amounts are gvg.report's totals for the match (what each player took from each
  source, net of regen; what each player's degen did to each NPC and Lord); only the timing is ours: a total is laid
  evenly over the seconds the replay shows that condition or hex on that target, and for an NPC or a Lord over the
  stretches its caster, else his team, was hitting it. `rows[target]` is [(second, amount, source, kind)]; `taken`
  and `dealt` sum it; `account` says what became of every point (R-460), `python3 degen.py cover` over every stored
  match (run it after a fetch). Four things to hold to. A weapon's own upkeep (gvg.report's "Vampiric Weapon", 11%
  of all degen it records) is no damage and is left out. Degen gvg.report credits to nobody (its "Observed
  Burning", conditions drawn or passed on, its remainders: 12% of what players took) is in what a player or a team
  took and in no figure of what a player dealt. The Miasma of Isle of Meditation (577 thousand health in the stored
  matches) is ignored at his word: in the account, in no damage figure, never read from where a player stands
  (R-677, which confirms the two readings before it too). And degen never says who is where: who is in which fight, who is hitting a player or an
  NPC, a stand-off, a spike and who killed a player stay read from hits and casts (R-655). Against gvg.report's own
  recaps (the degen in the window before 285 deaths and saves) the timing agrees at a correlation of 0.6: good for a
  minute's damage, rough for the few seconds before a death, where the recap itself is the figure to read (R-636).
  What takes it in so far: the damage a player took (`jobs._dmg_on`, rows marked degen): a base res carries
  `taken_all` (hits and degen, the figure the danger spot is asked of at 300, R-676), `taken` (the hits in it),
  `taken_degen`, and `npc_dmg_all` beside `npc_dmg`; NPC damage by kind of bar (`npcpower.py`, its benchmark
  rebuilt: a ranger adds 10.5 a second on footmen against 4.4 on hits alone, and the damage to kill a knight is 657
  against 561); the execution measures (`execution.py`: damage on their players, the shares on their monks and on
  one player, damage on their NPCs, and `degen` itself in health; the damage against the roles' usual is still hits
  against a usual of hits, until `eventlayer.py` takes degen in); and `pressure.py`, whose degen intervals are
  gvg.report's amounts now (pip-seconds as landed), so the death accounts, the nodes and `lnrows` read them without
  a change (their benchmarks are of the old figure until the rebuild). Not yet: `forensics.py`, `events.py`, `nodes.py`,
  `eventlayer.py`, `fights.py`, `scoreboard.py`, `phases.py` and `episodes.py` wherever they sum damage from hits;
  the story and the reports. The aim of a Lord push counts hits, not amounts, and stays as it is; Lord damage is
  gvg.report's Lord record (R-632), and the degen on a Lord kept in `degen.py` is read by nothing.
  Flag returns as built: `Moments.flag_backs` reads every time a team's flag came back to its spawn from gvg.report's
  flag objects (an object on the spawn spot within `RETURN_CAP_S` of that team's capture is the capture, any other a
  return), and `flag_lives` is built on it: a pickup is the next flag only when the flag had gone back; any other
  pickup takes the same flag up from where it lay, however near the spawn (the inference from the next pickup read
  a return that never happened about one time in seven, and read real ones a median 6 s and up to 7 minutes late).
  A life that ends returned ends the second it went back, so the flag tally (R-408) no longer counts a returned flag
  as lying on the ground until the next pickup (Crew v cope 5:47 to 9:23: Crew read level, a flag down in truth).
  Who returned it is the living enemy player nearest where the object lay that second (`returned`; None where nobody
  stands within `RETURN_R`). A capture the observer recorded on no carry of the life (the capper took it up again
  unseen, or the capture was named on the player taking the next flag) ends the life captured (`cap_unseen`), and a
  flag put on the hall's other flag stand (the Obelisk flag stand, Isle of Meditation) goes back at once with nobody
  near (`other_stand`). Every run prints the count of each ending (`Moments.flag_ends`). With true lives one reading
  had to follow, `Moments.not_run_first` (R-505 on the carries before a put-down: a flag brought up with the team, put
  down and taken up again later is no run until that carry; 옷옷옷옷 v RACK 0:00 and 3:03, Classic, where the inferred
  return had made two lives of one flag): it is asked by `_flag_rows`, the opening, the other side's row, the moments
  and the runners. Change it against those rows and hold v Men 0:00 (Classic: a flag put down as the gates open was
  not brought anywhere), never by a count of seconds. Left: a flag lying on the field is told from its take-up, not
  from when its taker set off for it (옷옷옷옷 v RACK 6:15, Visible, now told at 6:27).
  `tools/golden/compare.py <before> <after> [--skip key,key]` compares the plays of two runs (what "compare the plays
  with the run before" means everywhere in this file). A full run needs the machine to itself: a second run beside
  it gets a worker killed for memory and the run then hangs without a word.
- Check the reading after every change (R-453), on the branch: `moments.py all <file> --dev` (the development
  set, `data/model/dev_set.json`, about six minutes on two cores) then `tools/golden/review.py score <file> --key <main>/data/model/review_key.json`
  (the review key: every row Denning has marked, his words, and the checks read from them). Only a row he graded
  Classic is binding (R-494): a failing Classic row is fixed before anything else. Everything else is a report which
  Claude reads and tells him of only where it matters: the rows marked before 2026-11-15 (history, R-491), the Visible,
  Weak and No decision rows, the gate (`golden.py gate`) and the line-up (`lineup.py score`). Run every match
  (`moments.py all <file>`, about 10 minutes) only at a checkpoint: a benchmark rebuild, or counts a question needs. A
  full run applies the engine; it teaches it nothing.
- A fresh start from 2026-11-15 (R-491 to R-497). The engine of that day is the starting point (`bundle-4` at fd2b30b, kept as
  the branch `baseline-2026-11-15`; its reading and figures in `data/model/baseline/`), and the engine does not have to fit the
  rows marked before. His grades on a fresh game say what each row is for: Classic, the engine must identify it and
  read it exactly as he does, and one such row is enough to build from; Visible, a rate to watch; Weak, the engine
  should trend towards not identifying it (it teaches the confidence to read low); No decision, it should stop being
  identified. For Visible, Weak and No decision a fault is built from only when it shows in two games or is plainly a
  bug (R-495). There is no pass mark (R-496): show him the marks after each game, and he says when the system is ready
  for bulk training. The engine checks itself (`jobs.selfcheck`: a player counted in two fights at once) and tells a
  situation with no clear decision as context, with no call (R-488).
- Which part of a divided team is its main team is read in one place, `Moments.main_team` on the branch. His guide of
  2026-11-17 is built there (`HOME_GUIDE`): a split is almost never in its own base, and a small group at home with
  its main team elsewhere is most likely a defence. It is a guide, not a ruling, and not to be applied strictly: it
  gives way to his marks, to an even divide (R-335) and to a held base (R-506), and it is never cited as a ruling.
- A player counts in one fight only (R-519): where the main fight and a split's fight stand within reach of one
  another, `Moments._numbers` gives each player both readings count to one of them (by whom he trades with, then whom
  he heals, then whom he stands with, then where he is moving), and `split_plays` asks through `fight_side`. Change it
  there, never in one reading alone; `M._side_log` says who was given to which fight and on what; the self-check
  (`jobs.selfcheck`) should stay near nothing. Who the question arises for (`Moments._split_candidates`) is read until it
  settles: the splits silent, then again with the sides given, twice at most, whoever they count then being a candidate
  too (TFS v DMG 22:10 to 23:10: the last player of a split whose others were given to the main fight was told as a lone
  split with eight defenders while the main fight counted them all). And a defence has a split to defend: a defender
  given to the split's fight where every enemy player on that split is given to the main fight is in the main fight
  too. Over every match the self-check went from 20 in 6 matches to 6 in 4, with rows moved in 17. A split a player or more down meets its job by losing nobody (R-517).
  A player away from his fight for less than JOIN_S has not left it (R-579, the mirror of R-350), read in `_numbers` (`M._stayed`:
  counted in the fight before and after, alive, carrying no flag, on no split's fight, the missed readings spanning JOIN_S or
  less) and only to close a difference: where the fight is level with those players counted, nobody is up. It never lengthens
  one: keeping them in the count joined rows through the flicker of Jade's portal (Men v Crew 24:34, Classic) and was taken out.
  The other half is R-583 (his "(a) No. It is level"; Men v Crew 20:10, Men v hook 2:20, Book v Crew 5:08), read in `_numbers`
  too (`level`, `M._level`): a stretch of JOIN_S or less every reading of which is level once the living players are counted who
  were counted in that fight within JOIN_S before it began or are within JOIN_S after it ends (no flag in hand, given to no
  split's fight) is a player coming or going, and a situation with no other moment in it is not told. It is read on the whole
  stretch and the whole situation and moves no other row: do not turn it into "no moment in its own right" (tried: it cut the
  lead-in or tail of twelve situations, Men v RACK 18:04, Visible and correct, among them). A kill is as before (R-552).
  And any numbers difference of JOIN_S or less that comes from players being elsewhere is not told (R-585, his answer;
  `jobs.numbers_plays`: the sources "split elsewhere" and "on the way"; a runner away is the flag decision's, R-431).
- When a split ends and what kills it (2026-11-20, `split_plays` on the branch). The rest of a split's team is read at
  the second, not from the record (R-439): a player who went home from it is of the rest when the main team comes to
  the split (R-487). A player left on the enemy's ground by the others of his split who neither hits NPCs nor trades
  damage while alone is not splitting on (R-381 asked of the moment); a lone player on his way in is read from the
  crossing as before. The seconds in which a split that had not been outnumbered is killed by players come from their
  main team's fight are a collapse however short (`killed_end`): who hit him in the 6 s before he died counts on him,
  unless he came by the base res (Team v BcS 18:11) or `fight_side` gives him to the main fight; a death after a turn
  belongs to that collapse alone. Tried the same day and taken out, not to be built again without his word: players
  read as the head of their main team's push when the team comes together round them within a minute (fails Men v
  hold 10:40, Classic); players who stay where their main team's push stood (Men v Apes 7:10 reads against it); a
  split ended when all the team but two stand in one group with it (340 rows moved on the development set for one
  fault, TFS v DMG 22:44, where the self-check still counts twelve).
- When a split starts (R-562, `split_plays` on the branch): when its players are committed, and the enemy can know they
  are going for nothing else. A player who was not defending is read as before (from the crossing, or 4 s after he
  leaves when he goes straight across; from his own doors out of a held base). Players who had come to the defence of
  an enemy split before they joined the record (`was_defending`, from the answer of that split's record) are a defence
  turning into a split: while they are half or more of those on the enemy's ground nobody is on the split until one of
  its players has no way off to mid left ahead (`Hall.past_turnoff`: the walk to the stand along the rest of his way
  to the enemy's nearest door has no low point still to come; on a back path without one he is past it at once), and
  it then takes the door it comes to. It is told too from when enemy players have been on it for JOIN_S on the
  enemy's ground (`fought`: a split fight of its own, R-365; without it 4 v 4 fights on a back path were told nowhere; his word on it, R-563: leave it as built).
  He does not want this made more specific: change it against Men v hold 10:24 (No decision) and 10:40 (Classic), and
  bring him what it gets wrong rather than adding a test. A split ends, and the main team's push begins, when the rest
  come to the same fight by whichever door (R-560); players left at the enemy's door when the larger part forms
  elsewhere are a split (R-561): both are what was already built, and the first two readings "tried and taken out"
  above stay out.
- How flags are told on the page (R-520, R-521): the opening is one row, `jobs.opening` (who went where from the
  gates, who brought the first flag up, who capped first and who capped over it), with each team's first-flag job
  under it and nothing else (R-565: a team that runs no first flag has no stay play at the opening); after it every run is told once, a run and the run that answers it in one row (`review.py flag_rows`,
  from `run_id`, `answer_id` and `said` on the flag plays). The flag plays themselves, their jobs and their tests
  are as before: change what a row says in `flag_rows`, and what a play is in `flag_plays`.
- A push on a flagger is one reading, `Moments.flag_pushes` on the branch: two flaggers on one another are one push,
  the one who lands more on the other the pusher, and the flagger pushed is never counted among the players pushing
  (`M._fpush_answers` keeps what was set aside). Who pushes is R-573, his four points, read there and nowhere else: a
  player who hits or casts on the flagger and is on him (inside an aggro bubble of him for PUSHFLAG_S, or having left
  his own main team for him, or from range landing more on him than on the rest of his team; the caster at range is
  the push only when nobody is nearer); a player who travels with those players (goes with the flagger inside the
  bubble trading with nobody else, or has left his main team and comes to the flagger with them); never a player of
  the main team who stands off him or trades with his helpers, nor a monk healing the pushers across from the main
  fight; and the whole main team when it moves onto him (a push begun on him on his own goes on while their main team
  stands on him on his own ground; a holder who stands in his team when the fight is walked onto him stays R-401's
  push onto the flag). A carrier whose flag has stood in hand at the stand for HOLD_S has arrived and is not pushed.
  Change it against HC v Team 1:30, 5:26 and 8:18, Men v RACK 1:08 and hold v RACK 12:42 (Classic), never by a new
  exception; a runner who has just capped is the flagger only from when he is on his way home (R-577). On Isle of
  Jade, Warrior's Isle, Weeping Stone, Meditation, Wurms and Solitude a team at the footmen is not in the base for the
  base res (R-574, R-578: `base_res` in `hall_features.json`, read by `Moments.caught`).
  Players walking through a portal are of the main fight on either side (R-575): `Moments._reach`, asked by `_near`
  and `linked`, takes the two ends of a teleporter that works both ways (the hall's `teleporters.two_way`: Jade,
  Nomad's) as one step apart; change who is in which fight there. A numbers stretch every second of which lies in a
  stand-off (R-405, `standoff_at`) is no numbers advantage and is not told (`jobs.numbers_plays`; Men v Crew 14:24). A split's door is read phase by phase in `split_plays` (only a phase
  whose players all start it in the field takes a new door), and a split out of a base its team is held in is told
  from when its player goes out past his doors (`out_at`). The first is R-528; the other two are from his marks.
  A split record whose players all came for a flagger already on his run and left when the flag had gone is the push
  on the flagger and no split (R-530): one test, `jobs._push_not_split`, asked by `push_plays` and by `split_plays`.
- A part-run is not a flag run (R-535, R-536): a player back at home for a split who carries his flag some of the
  way on his own ground, puts it down and goes back to his base (always: it is what tells it from a run or a hand-off;
  the player who hands it on and joins his main team has run it). One reading, `Moments._part_carries` on the branch (built by `run_starts`, asked through
  `part_run_at`): such a carry is not under way and has not travelled, so `flag_rows`, the runners of a call, the
  boost and the moments all leave it out, and `split_plays` tells it on the split he defends. It is read from the
  split's own candidates (`_split_candidates`), so it is silent while those are being taken. Six forms were built on
  2026-11-18 before this one held his eleven rulings and every Classic row: change it against the set p2 rows and the
  HC v cope and hold v Men rows of the key, never by a new exception.
- A flag handed on is the same run (R-580), one reading, `Moments.handed_on` on the branch (asked by `run_starts` for the
  chain of a flag's carries and by `_held_carries`): put down and taken up by a team mate within HANDOFF_GAP_S, or, however
  long it takes, while the team mate who takes it stands by it (FIGHT_CLOSE from where it lies, every second from the
  put-down to the take-up). Any other flag taken up again is a run from where it is taken up, as before. Change it against
  Men v Crew 4:53 and 12:26 (one run, the Ranger handing it to the AoB Derv), Men v NwAy 8:19 (Classic: the Hammer who walks
  31 s to a flag left at his door runs it) and Men v hold 6:18 and hold v RACK 16:43 (Classic: the carrier who takes his own
  flag up again runs it from there), never by a count of seconds; three wider forms failed those rows on 2026-11-22 (a player
  coming straight for it, the carrier himself, a taker never away for JOIN_S).
  A player sent for a flag left on the field is a flag decision (R-581). A later flag left lying was already told from where
  it is taken up. A first flag is left when it has lain longer than FLAG_LEFT_S, two minutes (R-586, his length), read in
  `jobs._flag_rows` (`left`, `left_at` on the row) and, for a flag held before the gates that nobody carried for as long,
  in `run_starts` (`left_spawn`): the opening says what was brought up and put down, or that no flag was brought up, and
  the take-up is a run of its own, said as "sent for the flag left lying since ...", with no "The opening." before it
  (HC v hdm 5:56, 옷옷옷옷 v cope 4:55, 옷옷옷옷 v hdm 3:15). It is read from where the flag was first left that long, though it
  was put down again later for less (cope v Team: left 0:11 to 2:58, capped 3:16), and whether it is capped in the end or
  not. A first flag put down for less and then capped stays the opening's run (옷옷옷옷 v RACK 0:21, Classic; Men v Crew 0:22
  to 1:23, his "Men holds for 1:47ish before deciding to cap"), and the opening names every player who carried it in the
  match, in the order they first carried it (R-587: "brought up by Mes/A, handed to 8 Monk"; who held it before the gates
  or put it down as they opened is not one). Do not test where the flag lay or who stood by it (the taker by it, and any
  team mate by it, each fail a row he has marked). Not built: a flag whose first pickup is not at its spawn in the replay
  has no run record at all (Book v OG 7:16 and 10:56). A first flag neither capped nor returned is said as "put down at
  ..." in the opening's row, and the two first flags are "neither before the other" only when both set off by OPEN_BY_S
  (`gates` in `flag_plays`). Seen and left: a first flag put down for less than two minutes and never capped is still
  told from where it is taken up, under "The opening." and named for the player who took it up (One v Crew 6:37; read as
  one opening run it stood "under way" for five minutes in cope v Team and took the other team's runs as its answers:
  tried and taken out); and where a player goes back for the next flag before the player sent for a left flag has taken
  it up, the double run names its two runners the wrong way round (cope v Team 2:43).
- A flag held at home is no flag run (R-576), one reading, `Moments._held_carries` on the branch (built by `run_starts`
  beside the part-carries, asked through `held_at`): a carry in which the flag does not leave its own ground (nor by a
  hand-off within HANDOFF_GAP_S) while his team, all but one at most, is on that ground with him and MAIN_BIG or more
  of the enemy are in his base. Such a carry is not under way and has not travelled, sends no runner (`_runners`,
  `_runner_runs`) and is no flag on its way at a boost. Change it against cope v hold 14:09, Men v hold 7:46 and 8:12
  and Men v Crew 18:21 (no run), and HC v cope 2:53, Men v Crew 5:05 and 19:31 (Classic: runs), never by a new
  exception.
- The match is over at `Moments.over`: the second the losing team is recorded dying all at once, some 12 s before the
  replay stops. Those deaths are taken out of the deaths the reading counts, and no play starts from that second on.
- The known truths (R-533), on the branch: `tools/golden/truths.py <plays file from moments.py all>` at every checkpoint
  (a run over every match; the development set is too small for most). A short list of things any player knows (an
  undefended split takes more NPCs than a defended one; answering a run with a run is better in flags than staying),
  each a comparison of two groups of plays with a 90% range over whole matches: HOLDS, FAILS (the run exits 1), NOT
  CLEAR, TOO FEW. A truth that does not hold is looked into the same session and what was found is written in `NOTES`
  there; it is a reason to look, never proof. The truths are tests only and feed nothing in the engine. Only his
  truths and those he has approved can fail a run; Claude's proposals are reported apart. Compare calls on the fixed
  90 and 180 s record (`after` on a moment), never on a play's own end: a stay row ends at their cap, a run row at ours.
- The similar cases (R-538), on the branch: `cases.py test <plays file from moments.py all>` at a checkpoint (about two
  minutes; a report module, in no cache key; the report is kept in `data/model/flag_cases.json`). Three parts: the price
  of a result (a small model of a position fitted on every moment, mirrored, held out by `cache.fold_of`: strength gap,
  flag lead, death penalty, morale boost, pit NPCs, Lord health; a stand-in for the win model until stage E; footmen are
  not priced, their price runs backwards, and each run prints that check), the nearest cases (the same scenario, then
  the variables of R-538 in standard units, equal weight, and for the answer to their run also the res clock, each main
  team's place, their runner, each team's snares, how long their flag should take and whether the flag can beat the
  boost, R-539, R-540 and R-544: a build comes in as properties, never as a label; K chosen by the data; the floor of 30
  plays and 15 matches), and the held-out advice test (the boost read with and without the flag only held at home). The
  answer to their run is read at fixed seconds, 15 and 30 s after their runner set off, and judged 60, 90 and 180 s on
  (R-543, R-544), never to the end of their run, which takes in every run of theirs that came to nothing (R-542); his
  given is printed as a check (its half on flags is T12). Dropped at his word, not to be brought back without it:
  measured weights, the short list of six variables, the 45 s read (kept in the ladder only, R-545), the 120 s window.
  One clock (R-546): reads, windows (`after`) and position (`state`) of a flag play are counted from `clock.anchor`,
  their runner's set-off; the play's own `t0` stays the second the page tells the run (R-461). Where our runner was
  already out when theirs set off (`clock.from_cap`) the decision is another one, run again or not, counted from our
  cap, with scenarios of its own: never fold it back into the answer to a run. A runner sets off when he goes for
  good (R-548; `run_starts`, `for_good`: he came back when he had left, an aggro bubble or more nearer home, and gave
  up more than half that ground; a short step toward home and back is no leaving: test any change against HC v Team
  11:18, Classic, and hold v RACK 10:52). Whoever set off first is sending, by however little (`first` in
  `flag_plays`; the two first flags are the opening's): a pair of runs is told once, and a play or card whose answer
  is before its run stops the run (R-460). A flag play also carries what a card says beside the run: their runner
  waited back at his spawn from the gates (`clock.their_waited_back`, `their_pick`; the run record itself is left as
  graded), our first flag capped over theirs (`clock.cap_over`), and our own flag already up the field
  (`our_flag_up`, `Moments.flag_up`, read from the flag's life, carried or lying; the play stays what he graded). `Moments._state` reads the stand with
  the cap of its own second (caps are kept to the tenth of a second; `st.stand_owner` on a whole second misses one
  recorded within it, and the other readers of it are not yet changed: for the clean-up, R-398).
  The timing ladder (R-545): `cases.py ladder <plays file>` at every checkpoint, before the advice is read (a report,
  kept in `data/model/flag_ladder.json`; it can fail no run). It checks the readings themselves: is a runner sent
  sooner better off in flags, in the engine's tally and, apart, in the replay's own caps and boosts (the tally counts
  a flag on its way, so it rises with a runner by its own making); are the windows on the one clock; is the stand
  read right; is the tally flag advantage (whose boost lands next). Its raw record is `track` on every flag play. What
  followed an answer is put to him as section 8 of `cases.py test`, "as it fell" (by how soon our runner set off, and
  for no runner by whether their flag got in, with the chance of winning each row started from): the form he reads;
  never the test's counts alone, and never a mean over "no runner" without that split (2026-11-19: +1.1 was -4.4
  where their flag got in and +7.0 where it did not, teams already at 76%). The nearest cases are set level with the
  case read (`Scenario.level`; the chance of winning is matched on), and each scenario prints `level_check`: the two
  answers in the 60 s before the decision (`before` on the flag plays). Not level there means the answer marks the
  situation (SPEC 5, rule 4): say so and give no advice from it. The flag family goes through his four stages
  (2026-11-19): the readings (the ladder), the general table (section 8), the other factors (section 9, `factors`:
  what holding off is worth by what a team can see, where to look and never advice), and the sentence for one moment
  (`cases.py cards <plays file> [f1 | <report id>]`: the spot, the answer, what followed, what similar spots got; a
  verdict only where like cases stand round the case). Each later family takes the same stages. Settle the
  technical choices yourself; bring him GvG questions only. He marks the sentences on the site, Model > Game review,
  the view "Flag advice" (`assets/js/pages/review.js`; rows `data/model/flag_cards.json` on main, written by
  `cases.py cards <plays file> f1 --site <main>/data/model/flag_cards.json`; a card's id is its play's id): for each
  card whether what happened is told correctly, whether the reading makes sense to him, and what he would have done.
  His marks are in `data/model/flag_card_marks.json` (only what he marked, with the text he saw): read them the same
  session, set them out for him, and never write the cards again over a game he has marked without saying so. When
  they are written again, `--site` keeps each card's id (`play` is its play now), never touches his marks file, and
  marks a card `changed` only where it says something else than the card he marked (what happened told differently,
  or another reading at the first look; figures that only moved with the fit do not count): the page asks for those
  again with his earlier marks beside them (kept under `was`), and lists marked cards no longer written (`gone`).
  Tell him how many wait. His own call is send (at once), wait (look for a kill first, then send; R-549), hold,
  nodiff, unknown. The cards he corrected are set c1 of the review key, each with a check on the play it is written
  from (a dotted name such as `clock.cap_over` reads inside a play). The report also says what the
  advice was (section 5: the spots where it says hold off or send, with moments to look at; show him this whenever
  a test result is put to him, never the counts alone), what a team that holds off goes on to do (6), and the run in
  answer by who was sent and their snares (7: as it fell, where to look, never who to send). Every flag and boost play
  carries `state` and `after`, the position and the fixed 90 and 180 s record at the second the decision arises: judge
  calls from those, never from a play's own end. `cases.py case <plays file> <report id> <m:ss>` prints one decision
  with its nearest cases and their replay links. A verdict is a reading, not advice, until the held-out test shows a
  gain for its scenario: say so whenever one is shown to him.
- The split family (R-558; the split plays are ready, R-564), the answer to a split, on the branch. Every split play carries `split`, the record of its
  split on the clock of the second it is told (R-562): when it left, crossed, could first do something and was first defended; at `SPLIT_TRACK_S` from
  the telling its numbers (players on the enemy's ground, defenders, defending monks, its own monks) and what its players can do (`props`); every
  stretch it is told in with the kind of answer; each side's dead and each main team's place when it is told; its own deaths, its defenders', the
  NPCs it took and its damage to the Lord, by the second. The plays of its first told stretch carry `at_told`: the position each team chose from, the
  60, 90 and 180 s record and the 60 s before. It is not named `state`, which the prices are fitted on: a new family must not move the prices the flag
  readings were shown on. None of it changes a play. `cases.py splits <plays file>` (report `data/model/split_cases.json`): the clock of a split; the
  readings S1 to S7 (what any player knows); what followed each answer by the size of the split, as it fell; how the answer moves between the reads;
  and like spots (section E: matched on `SPLIT_VARS`, R-566 and R-568; each answer against the commonest at the same spot, then the test on unseen
  matches with the same test on the 60 s before; section F, `split_factors`: what matching the split or more is worth against fewer, by what the
  defending team can see, R-568: where to look, never advice). The answer is the first answer, read 20 s after the split is told and again at 40 s
  (R-567), in the names of R-566 with "no answer" told apart (R-569: a defender on his way, there within 20 s more, and nobody coming; told from what
  the defending team did alone) (`SPLIT_ANSWERS`). No row of the report is advice until the held-out test shows a gain for that size of split: say so whenever it is
  shown to him. The range of an answer's worth at a spot is the range at one spot: never narrow it by drawing matches again over spots, which share
  their nearest cases. Never ask for `_flag_rows` or `run_starts` from inside `split_plays`: it is entered while `run_starts` is being built (the part-carries),
  and the half-built runs are kept (2026-11-21: 30 flag plays moved; `runner_out` is put on the record in `plays`). After any change to the record
  compare the development set's plays with the run before, the keys `split` and `at_told` left out: nothing may differ. The split's damage against NPCs is not measured (`Moments._props`); players who res at the base onto a split are read as
  a collapse (to separate before the base res is judged against collapses). The other half, the main fight while a split is out (R-570): every numbers play carries `track.splits`, at each second of
  `NUMBERS_TRACK_S` [players on a split of ours, their defenders on it, players on a split of theirs, our defenders on it], from `M._split_at`
  (`jobs._numbers_at`; no play changes). `cases.py main-fight <plays file>` (report `data/model/main_fight_cases.json`) reads the numbers rows "from
  a split elsewhere" in four scenarios (up or down at the main fight; their split in our base or ours out; a split of each team out at once and
  rows with no told split on the ground are set aside): the readings M1 to M6, the trade (the side up at the main fight against the side down, with
  the same comparison on the 60 s before), what followed each call as it fell, like spots and the test on unseen matches. The call is read 20 s in
  (`_main_call`): a change to a split already there first (collapse on it, a defender pulled back, more sent, players brought back; a player who died
  there is no call, R-571), else his calls of R-551 (`_num_call`). No more matches are trained for either half until the engine is ready (R-570): never propose it again as the next step.
- The kinds that follow (R-572), on the branch. The push flagger, flagger pushed, pinned, base res and opening plays carry
  `at_told` (the position they are told at, the fixed 60, 90 and 180 s record and the 60 s before, as on a split; set in
  `jobs.plays`, `AT_TOLD_KINDS`; it changes no play, and the development set's plays must be the same but for that key); a
  base res play carries `res` (attackers, defenders, coming back, who stayed) and an opening play `open` (players to the
  stand, on a split, back at home, waiting for the next flag). Stage 1 of each is a report in `cases.py`, kept with
  `--json`: `pushes` (`push_cases.json`: who pushes, where the flagger was, the readings U1 to U5, and what followed as it
  fell by who pushes and whether his team sent help), `held` (`held_cases.json`: a team held in its base, by how the hold
  ended and the players alive when it began, H1 to H5), `res` (`res_cases.json`: stayed through the base res or left
  before it, B1 to B6, and the stays by the health of the players in the base as the res lands) and `opening`
  (`opening_cases.json`: set out by his four points, R-590, N1 to N14). Help sent, the break-out, staying against leaving
  and who wins mark the spot and are never read as causes (staying against leaving is not one of his truths, R-534). He
  has passed the general tables of pushes and holds (stage 2, R-588); like spots and the test on unseen matches are not
  begun for any of the four. From his answers of 2026-11-22: a one-player push is read on their runs (`their_runs`,
  section D of `pushes`: who pushed their flagger and whether the pushing team sent a runner of its own, each set level
  on the flag lead held, since a team ahead loses lead as their flag gets in whatever it does; a reading, never advice).
  The danger of a base res is dying to it (R-589): a stay carries `res.health`, `low`, `inside` and `pit_npcs` (energy is
  not in the replay; `RES_LOW_HP` in `jobs.py` and `RES_LOW` in `cases.py` are Claude's drafts and no play reads them),
  and "base" is not made smaller until he says where the line goes. The opening play carries what the other team showed
  (`open.their`, `their_flag`, `their_first_cap`), the line of the first carrier (`beside.flag.line`, `common.line`) and
  the record 5 and 8 minutes from the gates (`open.later`, `OPEN_LATER_S`, R-599, with what the price of a position reads). The hand-off and the flag
  returned (R-620 to R-625): `jobs.flag_hands`, a record kept beside the plays as `flag_cost[rid].flag_hands` (it tells no
  play and changes none): `lives`, one a flag life (who ran it and of which line, every carrier, when it first stood in
  hand at the stand and on whom, how long it was held and by whom, how it ended, the position at the pickup and at the
  start of a hold), and `put_downs`, one a carry that ended on the ground (who and of which line, dead or not, where, the
  living enemy players within an aggro bubble of it, `enemy_near`, R-623, and what became of it: a team mate took it up,
  its carrier took it up again, returned, left lying). A flag goes back only when an enemy player picks it up (R-622).
  The second of a return is gvg.report's flag object at the spawn (R-481, `Moments.flag_backs`): the put-down carries
  `return_by_s`, the seconds from the put-down to the return, `returned_by`, and `returned_soon` (back within 15 s,
  `RETURN_SOON_S`, his window, R-629); `first_enemy_s`, the first enemy to stand on it, is kept beside them. A hand-off (`handoff`) is a living player putting the flag down with a team mate within an aggro
  bubble of it (his reading of the word, R-630), read before the result. `cases.py handoff <plays file>` (report
  `data/model/handoff_cases.json`): A, the record, with X1 and X2 (in range a flag is returned more often: both hold);
  B, a hand-off returned against a flag that lay and was returned later (R-626, "contested v uncontested"), and what
  a returned hand-off costs in flags against one a team mate took up in the same range (a third of a flag a minute
  on, made up by three minutes, which he has passed as the cost of one run, R-631; the two do not start level), with his truth T13 (R-629, in
  `tools/golden/truths.py`: it reads `flag_cost[rid].flag_hands`, not a play) at 1.5 and at 2 bubbles; C, his first
  point (F52), a later flag run by a frontliner with the stand held at the pickup (R-627: that is his case), run to
  the stand on him against handed on before it; D, his second
  (F53), a first flag on a frontliner at eight against seven, kept or handed on; E, his third (F54), who holds a held
  flag, the holder named by build (R-624; the groups are Claude's, and which builds are the primary defender or the flag
  runner is left to the data, R-628: do not ask him again); F, moments to look at. How a flag is carried follows the spot a team is in:
  none of it is advice. D and E are under the floor at 564 matches. A team held in its base is no decision family and
  is read as execution with the measurements of R-572 (R-619, R-621): no stage 3 for it. What the held team heals, its
  NPCs or its players, mostly follows what the holders hit (R-658): a reaction, never a call or a fix; a hold is to be
  told with what the holders went for, NPCs or players (not built).
  After any change to these records compare the plays with the run before, `open`, `res` and `beside.flag.line` left
  out: nothing may differ (`flag_hands` is in `flag_cost`, not in the plays).
  From his answers of 2026-11-22 and 23 (R-591 to R-614), as built now.
  The base res is a call only in the danger zone (R-592, R-609, R-610, R-614): the main team, three or more of it in their
  base, with his three factors on 20 s before the res: half or more of them past their res shrine, two or more enemy NPCs
  hitting them, and 300 or more damage a player in the minute before, hits and degen (`RES_WORN`, his number, R-676; 250 on hits alone before it, R-615). One
  reading, in the engine: `jobs._res_stand` (`marks`, `danger`), on every base res play as `res.early` (20 s before, when
  staying or leaving is still the team's) and `res.at_res`, and on the res spots. Low health is not a factor (R-602). Every
  other base res is context with no call (`jobs._res_context`: `clear` false, `unclear` saying which part of the danger spot
  is missing, R-488); the Classic base res rows outside the zone check that in the key, his words under `later` (R-614,
  R-615: 18 of his 25). The call carries his two factors (R-616, amending R-613: `jobs.res_factors`, `res.factors`, said on
  the row): morale `RES_MORALE_BEHIND` (30, confirmed by him) or more under theirs over the eight, and the stand not held;
  `against` counts the two, and the res of 12:00 or later is kept as `late` and counts for nothing. No verdict is built and
  none is to be (R-617): whether a stay there is a mistake is not known, his assumption is that staying is usually correct,
  and what the engine says is the sentence (`cases.res_sentence`, kept as `danger.calls[].sentence`): the chance of winning
  the team had, what stood against the stay, the deaths it took and the points it lost or gained. Never tell him a stay
  was a mistake or the right call. The chance of winning and health are not factors of the call (R-613), though like
  spots are still set level on them. `cases.py res` (`danger_report`): D, where the danger zone is, with his eight games
  (`HIS_RES`; Men v BcS 6:00 and DUM v ohno 8:00 are outside it and stay out, R-618: never an exception for them; hook v
  Men 6:00 is left as read, R-607); E, the two factors, each and together, with the clock beside them (`his_factors`, E1 to
  E10); F, what a death costs there (`death_cost`: as it fell by how many died, raw and set level on where the team
  started, and as the price of a position reads one more death, a kill and a pit NPC at that position); G, what else
  separates the stays that take deaths (thirds of the zone's own stays, D1 to D8); H, like spots among the stays with the
  test on unseen matches (T1 to T3), set against holding what the team had, since almost nobody falls out
  (`jobs.res_spots`, the record 40 s before the res kept beside the plays in `flag_cost[rid]`, R-601, R-605; the prices
  are not fitted on it); I, every danger zone base res as its sentence (`danger.calls` in the report's file). On
  2026-11-23, at 250, 156 stays: T1 to T3 are not clear, and the factors' groups are under the floor of 30 (27 stays with
  one or both against). A fitted input needs 20 events each (SPEC 5, rule 3): 27 stays with a death carry one at most.
  The opening is set out on his seven decisions (R-611; `cases.py opening`): from the gates (`GATES`), the first flag and on
  whom, cap or hold at the stand, hand the flag on, send a player back before a cap (`open.next`), a split in the first
  3:00, and a flag against none. Each is judged on flags and kills first, then the boosts and the chance of winning at 5:00
  and 8:00, with the NPCs (R-596, R-599), from the side of the team that makes it and set level on strength alone, since an
  opening has no minute before it (`_open_cmp`; under the floor a call is shown as it fell); like spots and the unseen test
  where teams divide (`_open_scenario`, `OPEN_VARS`). Who caps first, and whether anybody caps, is what two teams' choices
  come to and is never a call (R-608): N1 to N4 only say what follows it. In control of the stand is having the flag stand
  captured (R-604): a hold by a team that has capped is the flag in hand (R-553), not the opening's. Tried and taken out at
  his word, never to be built again: a team "having the stand" because its main team stands nearer it; and the first-flag
  holds told by what the other team's flag did meanwhile. A difference between two calls counts the opponents among the
  others, who lose what the callers gain: say so whenever a size is quoted. The usual split response is the player other
  than a monk a guild most often sends first, the match's runners left out (R-593, R-598, `usual_responder(D,
  monks=False)`). Pushing the flagger is a decision of its own and no answer to their run (R-591), and no family (R-597):
  its readings (`cases.py pushes`, section E, his five questions on `their_runs`) stay a report. No verdict of any of
  these is advice.
- The Lord push and Lord damage (R-632, R-633). Lord damage is gvg.report's to say, everywhere: what decides 28:00 is
  aggressiveness, and raw damage matters only for killing the Lord. gvg.report's own record
  (`summary.objectives.guild_lord_damage`: team scores with `lord_damage_equivalent`, every hit, heal and effect on a
  Lord by the second with Entourage and the Amulet's limit, the pit NPCs' deaths, each Lord's health once a second) is
  dropped by the trim, which keeps only each Lord's total (`lords[].taken`, flux damage in it); it leaves life steal
  out, and the engine's sum of the recorded hits (`Moments.lord_hits`) does not. Aggressiveness (R-634) is each point
  of damage to the enemy Lord, 30 for an attack missed through Blind, less 50 for an enchantment or weapon spell on a
  team's own Lord, 300 with Entourage up; it rebuilds exactly from the record's event list, a hit counted for the team
  that dealt it (source "map" is the flux, nobody's). gvg.report's record also scores each Blind put on the enemy Lord at
  30 for the team that put it there (events of kind `condition`; 176 of them in 53 of the 658 matches): with it every
  team score rebuilds. Built on the branch (2026-11-24): the record is in the file beside each replay and the engine
  reads it, `Moments.lord_record()` (`extras.LordRecord`: `hits`, `damage`, `aggressiveness`, `health`). Every Lord
  damage figure is gvg.report's (`on_lord`, the split's `lord_damage`, the Lord play and the Lord line, the end
  record's `lord_damage_by`); each position carries both teams' aggressiveness (`aggr` in `consequence`, R-634) and each
  Lord's health as gvg.report estimates it (`lord`, in place of the health rebuilt by `lord.py`), and the price of a
  position reads both (R-635: `cases.position`, the seventh price "aggressiveness lead (per 500)"; one price for the
  whole match though the lead decides only at the end, a stand-in until the win model takes the prices' place). Who is
  on a Lord and when stays read from the replay's own hits (`Moments.lord_hits`, the count of hits behind `aim`), as
  who is in which fight is (R-655). A team whose Lord damage the observer did not see keeps its blank
  (`Moments.lord_unseen`). `data/model/lord_gvg.json` and `review.py lord-record` are no longer needed (for the
  clean-up, R-398). Never give him the health rebuilt by `lord.py` as gvg.report's. A fetch downloads about 180 MB of
  replay and 65 to 110 MB of summary a match, and gvg.report serves no smaller Lord damage payload. Picked Lord pushes
  are marked on the site, Model > Game review, the view "Lord push" (`review.js`; rows `data/model/lord_rows.json`,
  written on the branch by `tools/golden/review.py lord <main>/data/model/lord_rows.json <report id>:<m:ss> ... --gvg
  <main>/data/model/lord_gvg.json`, which reads the matches itself; his marks `data/model/lord_row_marks.json`, to be
  filed as set p4 of the key). Never put Lord push rows to him in the chat for marking, and never write the rows
  again over rows he has marked without saying so.
  The Lord play as built on the branch (2026-11-23; R-640 to R-646, R-650 to R-654): `jobs.lord_plays` reads the end
  of the match from where the players stand, `Moments.end_play`, never from hits on a Lord. The record
  (`moments.py <report id> end`; kept beside the plays as `flag_cost[rid].end_play`; settings `END_*` and
  `PLAY28_FROM` in `common.py`; said and summarised by `tools/golden/endplay.py <report id>` or `all <out.json>`,
  report `data/model/end_play_draft.json`): at the end of play (the Lord's death, or 6 s before the match is over)
  every player is sent (on the enemy's ground within `LORD_BASE_R` of their Lord, R-446: a player who stops at
  their footmen is not), kept (on his own ground) or in the field, and since when; a team's send is the middle of
  its sent players' `since`, the play is set at the later send. Two readings from his marks: a player who dies on
  his way into their base was sent (hold v Dz 26:15: `_end_way`, on their ground at their door, base or pit past
  the last turn-off to mid, for JOIN_S or having stood in the base); and a send is read while the play is on, not
  at its last second (R-654: a living player who left their base or his home less than JOIN_S before the end
  counts where he stood, R-579, with `left`). Change either against the eight draft rows (p4-9 to p4-16) and Book v
  hook (his "NO corresponding push"), never by a wider "sent": every door zone of their base, his labelled Base
  area, and "left after the play was set" each read a push in return that he does not see (tried and left).
  The play for 28:00 is one play of both teams (R-640): a play a team with the same sentence, start (when the first
  group went) and end, which the page reads as one row; each carries whom the team sends and keeps, `aim` and the
  Lord figures. "28" is the end of the match, not the clock (R-642); a Lord kill by a team that sent its players
  before 25:00 is a push before it (R-653, his line). A push before it is no row of its own (R-644, R-650): it is a
  Lord line (`lord`, `lord_line`; the scenario is left as it is, and `review._reads` adds the line) on the rows of
  the situation it grew out of: the losing team's held rows from the killers' first send on, the last read on to
  the kill; else the rows of the killers' split in its base (Dz v Crew 21:36); else the killers' last numbers row
  (cope v hold 22:40, the stay after a wipe). In a match that goes on to a play for 28:00 a held row from 23:30
  on, begun before that play, in which the Lord is hit carries the line (Team v hook 24:02); any other earlier
  visit is not told as a Lord row (R-652). `aim` is read over the stretches the Lord is hit (`Moments.on_lord`):
  "killing the defenders" where more hits in the base land on players than on the Lord (Crew v cope 24:44), else
  "the kill" where the send kills him (his words on ohno v Book 25:04), else "Lord damage" (Team v hook 24:02); the
  kill is read from the result, intent not being in the replay. A run prints how many pushes before it have no row
  to be told on (R-460): keep it at none. After a change compare the plays with the run before, the Lord plays and
  the keys `lord` and `lord_line` left out and each id without its running number (a play's id ends in its place
  in the match, which moves when a Lord play comes or goes). `review.py lord` is retired; rows of the play for the
  page are written by `endplay.py rows <main>/data/model/lord_rows.json <report id>=<why picked>` (ids
  `e:<report>-end`, added and never rewritten). The p4 games are in the development set. A check in the key may
  read a record kept beside the plays (`"record": "end_play"`, dotted names).
- What each prot did, degen and interrupt attempts (R-636 to R-639). Not built: at the next rebuild, with R-481 and R-632, GvG Info keeps from gvg.report's
  summary, in its own file a match (filled from the summary; only summaries are fetched again, not replays): per skill
  blocks, knockdowns prevented, overhealing and Divine Favor apart; healing and prevented by target for healing and prot
  skills (the Lord too); what each player received from each ally by skill; the enchantments on each Lord; and for every
  death and spike save the healing and prevention by source and skill, the prots up, knockdowns and interrupts on the
  target, blocks, health at the start and end and condition uptime. Crits and cast timing stay out (the event log has the
  timing). Blocks and knockdowns prevented are gvg.report's estimates, per caster and skill, with no time or target.
  Who stripped which enchantment is read from our replays, never from gvg.report's `removed_by_*` (in reports read
  from early November 2026 only; a check there): a strip's cast start naming its target, the stripper's next cast
  finish, and an enchantment on that target ending within 0.4 s of it (R-637; Gaze of Contempt takes every one that ends).
  Degen and regen too (R-638): degen dealt and taken by each player net of regen, regen received, degen by condition and
  source skill, and in deaths and spike saves the regen and degen on the target, Deep Wound and the pressure split; the
  engine's degen (`pressure.py`) then reads gvg.report's figures, since the replays record degen as no damage and most
  burning in them has no caster.
  Interrupt attempts too (R-639): every targeted interrupt attempt, hit or missed, with its target, and likely fake
  casts by player; until then only landed interrupts are kept, and forensics and `pressure.py` read the attempts once kept.
  Degen in every damage figure (R-649): once R-638 is built, NPC damage accounts for degen and so does every other
  place damage shows up; the list of places is in the ruling (NPC damage by kind of bar, the execution measures,
  the danger zone's damage line of R-615, which is put to him again on the new figure, the aim of a Lord push, the
  death accounts and nodes). Amounts take degen in; who is in which fight, a stand-off and who killed a player
  stay read from hits and casts (R-655). Degen on NPCs and on a Lord is read from gvg.report too (R-661, in place of the
  estimate of R-657): its summary credits it to the player, the condition, the skill and the target, as totals for the
  match with no time (the `targets` rows of list `d` in the file beside each replay), so it is shared out over the
  stretches a player is on an NPC. The engine is to read gvg.report's energy estimate (R-664, turning R-662 round and in place of R-177): not built; where it bears (pressure, the boost clock, the base res, execution, the death accounts) is listed in the ruling and gone through with him first.
- The measurements of R-572, on the branch (built 2026-11-23; each is a record or a report and moves no play: after any
  change to them compare the plays with the run before, the key `npc` left out wherever it stands).
  Execution, both teams by the same measures (2.12, R-299): `execution.py`. For the first `EXEC_S` (20 s, Claude's
  draft) of every play, the players the play names (`who`), else the team's main team, and the enemy players in the same
  fight as one of them (`Moments.linked`): `MEASURES`, each with the direction a player expects and its words (damage a
  living player, damage against the roles' usual, the share on their backline monks, the share on the one player hit
  most, spikes, interrupts, knockdowns, disables, cast prevention, degen, kiting, baits, useful and wasted strips, time
  their attackers spent Blind, hexes kept up and removed, damage on their NPCs, healing of our own, and the three
  measures of a team's own care named below). Kept beside the
  plays as `flag_cost[rid].execution`, one entry a play id with `own` and `their`; `python3 execution.py <report id>
  [m:ss]` prints a match. It reads `pressure.py` and the event layer, so the first run over every match builds those
  (about 3 s a match). `cases.py execution <plays file>` (report `data/model/execution_cases.json`): A, the record and
  what each kind of play is placed against (`bench`, `exec_place`: low, usual or high among plays of the same kind);
  B, each measure against what followed (the upper third of plays against the lower), with the same comparison on the
  60 s before and how far apart the two groups already stood; D, a team held in its base (R-621: the first 20 s of a
  hold against what the team then loses, only between holds alike in players down, the base res clock and pit NPCs
  already lost). The enemy's execution is scored and never offered as a fix (R-299); a measure that tells the minute
  before marks the situation, one against the expected direction is likely a reaction (SPEC 5, rules 4 and 4c); a
  clear line is a place to look, never a finding or advice. Execution said on a row in words: `cases.exec_sentence`
  (`cases.py execution-say <plays file> <report id> [m:ss]`): for the team making the play and, apart, the enemy it
  meets, the measures that stand out among plays of the same kind (`exec_out`: outside nine plays in ten, where
  `exec_place` reads the outer quarters), each with its value and what the middle half of such plays had; what stood
  out, never why, and no verdict. It is on no page yet. The team's own care is read with `forensics.py` on the
  play's window (2026-11-23): casts started into a ready interrupt (`into_ready`), attacks made while Blind
  (`blind_attacks`: Blind is named in few replays, about one side in a hundred, so it says little until the
  rebuild) and the share of damage taken off a shield set while not casting (`off_shield`). A boost play (no 60 s
  record) and the later stretches of a split (no position) are not in the report.
  NPC damage by kind of bar (R-433): `npcpower.py`. `bar_class` is the rough class (a warrior by weapon, an
  elementalist by attunement, a monk by whether he heals, else the profession); `python3 npcpower.py bench` writes
  `data/benchmarks/npc_damage.json` over every match that counts (run it again at a checkpoint when matches are added;
  about 15 s): the damage a second one player of a class adds to a group that is on a kind of NPC (he is in the group
  for the whole stretch whether he hits or not: a monk on a split adds almost nothing), and the damage it takes to kill
  one. `Moments._props` carries it as `npc` on every group; the like spots of a split are matched on it (its damage
  a second on archers, knights and the Bodyguard, in `SPLIT_VARS`, 2026-11-23); no play reads it.
  The pair rule (2.13): `model.steady_pairs`, run by `cache.py warm` before the cap tests: the `SCREEN_TOP` strongest
  pairs are screened on each half of the matches (halved by `cache.fold_of`), on what team strength and each
  variable's own curve leave, and only a pair in both lists enters the win model, the same pairs in every fit of the
  run (`steady_pairs` in `cap_choices.json`; his `interaction` and `no_interaction` corrections still act). Until the
  choice exists a fit picks its own eight and says so. It was tried on made-up data only: read its first real choice
  and the held-out score at the rebuild.
  The decision to split at all (R-558), stage 1: `jobs.split_ticks` (kept beside the plays as
  `flag_cost[rid].split_ticks`: every 30 s from 1:00, a team with six or more alive and no split of its own out, his
  definition of the old kind, SPEC 6; the position, the fixed record, and the split it sends in the next 30 s, read
  from the split records of the plays) and `cases.py split-at-all <plays file>` (report
  `data/model/split_at_all_cases.json`): what is sent, when teams send one, as it fell by the chance of winning stood
  at, and a split against none from the same standing with the 60 s before. Stages 2 to 4 wait for matches (R-570).
  What is at stake (R-509): `tools/golden/stake.py <plays file> --key <main key>` tests length, damage traded, players
  met and what followed against his grades, each game from the others. On thirteen games nothing tells his Weak and No
  decision rows apart (only 10 of them are still read by the engine): nothing is added to the confidence band, and
  none is to be guessed. Run it again when more games are graded.
- A numbers advantage from kills is not a decision family (R-557: the team up keeps killing and follows the team down,
  whose own choices read as near forced; the numbers that are decisions are those a team chose to make, a runner, a
  split or a collapse). Its cards are not marked and its view is off the page (the `ADVICE.numbers` entry in
  `review.js` stays for the split family to copy); do not put numbers cards to him again. The res (how soon it is
  tried, what stops it), giving ground a player down and fights in general are on the execution list. What was built
  stays and is described next, for the split family and for execution to use.
- The numbers record (R-550 to R-556), on the branch. Scope as built: numbers at
  the main fight from kills, a runner away and players on their way; the main fight while a split is out waits for the
  split family. Every numbers play carries `state`, `after`, `before`, a `clock` (when the numbers arose and ended,
  the base res, each side's dead, every res in the fight over three minutes: `jobs._hard_res`, a dead player alive
  again more than 3 s off the base res; a res that gets off ends an advantage from kills, R-552) and a `track` (each
  main team's step 0, 15, 30 and 60 s in, and a runner of ours gone): `jobs._numbers_at`, which changes no play.
  `cases.py numbers <plays file>` (report `data/model/numbers_cases.json`) is stage 1: the readings (a larger
  advantage, and one with the base res further off, kills more and lasts longer) and what followed each call, as it
  fell, then like spots and the test on unseen matches by scenario (section D), each with the same test on the 60 s
  before. `cases.py numbers-cards <plays file> f1 --site <main>/data/model/numbers_cards.json` writes the cards he
  marks on Model > Game review > Numbers advice (marks in `data/model/numbers_card_marks.json`; ids, `changed` and
  `gone` as for the flag cards; a situation he graded Weak or No decision has no card). A res that levels the fight
  ends the advantage unless that team dies again within 12 s (R-555: already how the stretches are read).
  The call is read 20 s in and told again at 60 s (R-556; `cases._num_call`), in his options (R-551: up, stay and kill, push into their base
  for NPCs, push their flagger, run a flag for a backup, fall back and reset; down, stay and fight, fall to footmen,
  retreat to the pit, trade with a split), never from the whole situation, which marks a team already winning. Never
  set cases with a res against cases without: a res comes where players are dying. The cards for a flag in hand
  (with R-553) and for a double run from the sender's side are held (R-554): remind him when more matches are in.
- No new rule or threshold to answer a wrong row (R-465): rebuild the reading under it at the root, with his marked
  rows as the test. Who is in which fight is one reading on the branch (`Moments.linked`, `engaged_in`, `visits`; R-464),
  used by the numbers of the main fight and by a split's defenders: change it there, never beside it. His words on a
  row become checks in the review key, open until they hold; `review.py score` counts the open checks that hold now.
  Every match moment put to him carries its replay link and time: the time of the thing he is to look at (the carry,
  the death, the turn), never the start of the row it is told in (True v One, 2026-11-18: given 0:45, the row's start,
  for a carry at 1:48, he saw no pickup).
- A reading which fails must fail loudly, never be turned into a blank (R-460). A blank that means "not in the replay"
  (unobserved Lord damage) stays a blank; a blank from a fault stops the run or is counted in the output, so that a
  field blank on every row is seen the same day.
- His marks go into the review key the same session, with his words kept as he wrote them. An engine fault he points
  out is a check in the key, not a ruling; only his definitions and his decisions on process are rulings (R-452). A
  kind of play is used downstream only once he says the system is ready (R-496).
- Reviews are by whole games, one at a time (R-454, R-492), marked on the site, Model > Game review
  (`assets/js/pages/review.js`). On the branch: `tools/golden/confidence.py run <conf.json> <report id>` (the engine's
  confidence, R-497: the game read again with every draft number of the reading moved a quarter and to half and
  double, about twelve minutes a game; one band a situation, high, medium or low, fitted to his grades of the first five games on
  2026-11-17 (R-515), the fit written at the top of `confidence.py`; `confidence.py reband <file>` after a new fit), then `tools/golden/review.py export <plays file> <main>/data/model/game_reviews.json --set f1
  --part N --confidence <conf.json>` writes the rows: every situation the engine reads with its confidence, and under
  it each side's call. He grades each situation (Classic, Visible, Weak, No decision, Repeat), says whether the engine
  read a decision Correct, Partly or Incorrect with ticks for what is off and his words, marks the calls where they are
  asked for, and adds the decisions the engine did not read; saved to `data/model/game_review_marks.json` on main, which
  holds only his marks and the text of each row as he saw it. Read his marks from that file and file them in the
  review key the same session (`review.py file <id> <rows> <marks> --set f1 --key <main key>`, which prints his grades
  against the engine's confidence and the Classic rows to fix first, and writes the plain checks; then write by hand
  the checks for what a Partly or an Incorrect means). Set every result out for him in the chat (R-329). The queue is
  set f1 in `dev_set.json` (thirteen games graded: HC v Team, Men v Crew, 옷옷옷옷 v RACK, Men v RACK, Men v hold, hold v Men, HC v hdm, RACK v hdm, hold v RACK, HC v cope, as far as 9:40 and no further (R-532) 옷옷옷옷 v hdm, whose clock on the replay page runs ahead, R-527, and game 14, Dz v Team on Druid's Isle; game 6, hdm v HC, taken out unmarked, R-522, and game 13, Men v NwAy on Corrupted Isle, taken out unmarked, R-537: game 6 is not on the page or in the development set; game 13 came back on the page as game 15, R-559, and is graded, 2026-11-21; no game
  is kept hidden, R-497); pick further games from unused October and November games of top guilds, never a henchman
  game (R-476). Export the next game only when the last one is marked and its Classic faults are fixed, unless he asks
  for more at once; never fix against a game he has not marked, and never re-export a game he has marked. Games without `scheme` 2 are history, shown read only. The golden
  moments page is retired: label nothing new there; the 15 golden moments and their key stay as part one of the gate.
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
  commentary go into these records first. The words of R-373 and R-375 to R-378 are records too: `flag_pushes()`
  (pushing the flagger, R-371), the flag route, door, hold and boost distance in `flags_record()`, `flag_lead()` and
  `lead_at()` (the flag tally, R-408: the stand counts as one flag; bands at 0.35, 0.8, 1.3 and 1.7), `pregame()`,
  `standoffs()` (the disengage, R-405, framed on OG v hdm, R-411, in place of posture: main teams standing off with
  little or no damage traded are not a fight), `timing()` (the four choices of R-377, the held flag of R-400 and
  R-407), `onto_flag` on a main team push (R-401), `monk_counts()` and `on_lord()` (R-378); their thresholds in
  `common.py` are confirmed (R-404, R-406). What the flag readings are for is R-412. To see what a looser or tighter threshold would do,
  use `tools/golden/thresholds.py sweep` (it sets `GVG_TRY`; never set that in a training run). From the gate review
  (R-416, R-417): `way_out()` (a team going out of its base by a door), and in `attempts()` who set out together,
  where a split fell back to, a main team that went home for a split, and swaps in the answer; a push on a flagger
  counts from 4 s when he reaches his team with the pushers still on him (R-418).
  The line-up is the measure of the reading (R-368 to R-397): timestamped commentary and comms filed as paraphrased
  statements in `data/lineup/` (never transcripts), checked against the story by `tools/golden/lineup.py` on the
  branch. The four games in `data/lineup/held/` were the held-out check: Denning reviewed their misses
  once (R-416), the reading gate passed, and they are spent (building games from here, R-417). The line-up only checks that what was said is
  in the story, so run `tools/golden/thresholds.py` beside every rescore to see what a change did to the records over
  all matches. The gates and the build order are in `docs/REDESIGN.md` ("Tests", "Build plan from here").
  The decision moments are read from the records (stage B: `run_starts()`, `attempts()`, the numbers in each main
  team's fight, `verbs()`); the decision gate is `tools/golden/golden.py gate --data <main>/data/lineup` (part one
  against `data/model/golden_key.json`, Claude's reading of his golden notes, R-341, which he corrects; part two the
  comms calls of the line-up).
  Stage D (depth) on the branch so far: every moment carries the shape of its call (`shape()`, R-297: who as properties,
  which way, when, with `gained_elsewhere()` for the timing rule of R-321) and what followed (`consequence()`, R-294 and
  R-412: hard results over the whole map at 90 and 180 s, the flag lead set beside the numbers meanwhile). The jobs are in
  `jobs.py` (R-423 to R-449, Denning's own table: read those rulings before changing a job or a test): a call is an
  allocation of plays (flag, push flagger, flagger pushed, split from both sides with collapse and full collapse apart,
  numbers, boost, pinned, base res, lord), each with its job, its test, its own clock (to the event that ends it, never a
  fixed 90 s) and what it cost kept beside it; a test covers only what the players of the play control. Whether a job was
  met is a result, never a verdict on the call (similar cases) or on execution. A split is read phase by phase from
  when it reaches a defender or their base (R-438 to R-449, his review of the first cases: read them before touching
  `split_plays`); flags carried by a player with Shadow of Haste are set aside (`soh`). `moments.py all <file>` then `jobs.py
  summary <file>`, `moments.py after|runner <file>`; `jobs.py <report id>` prints a match's plays. Thresholds marked
  "Claude's draft" in `common.py` are his to confirm.
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
