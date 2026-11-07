# GvG Info — handoff for a new Claude chat

Last updated 2026-11-07 (portal sections unchanged since 2026-10-15; match replay analysis section added). Attach this file (or just ask Claude to attach the repo) in a new chat, then say what you want.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md and docs/HANDOFF.md, then: <your request>

Claude should then:
1. Clone `itsha12/gvginfo` (account itsha12, one "2"). The Claude GitHub App is installed on it.
2. Read `CLAUDE.md` (where every file lives and the rules), then this file.
3. Answer questions by querying the JSON files with short scripts, never by loading big files whole.
4. After changing the site: check it in a headless browser, commit, `git pull --rebase`, push (retry — Denning's
   player assignments from the site and the update bot commit to main at any time).

## Workstreams in this file
- **Portal** (the site, its data, and its updates): the sections from "What the site is" to "Ideas not started".
- **Match replay analysis** (in-depth match reviews from gvg.report replays): the last section of this file.

## What the site is
- **Site:** https://itsha12.github.io/gvginfo/ (GitHub Pages from branch `main`, no build step). Denning plays GvG only.
- **Look:** white, minimal, architectural (Inter / Inter Tight / IBM Plex Mono, black buttons, gold only for elites and
  tested lines). Don't use the word "My" anywhere. Never abbreviate Master of Damage.
- **Tabs, in order:** Schedule (home page `#/`), Recent matches (`#/matches`), Builds, Meta, Guilds, Players, Templates,
  Skills, Mechanics, Settings.

| Tab | What it does | Main files |
|---|---|---|
| Schedule | AT-A / AT-C start times in Eastern time only, month table, map rotation, current and next flux. Starts between midnight and 6 a.m. sit on the previous evening's row. | `assets/js/schedule.js`, `pages/schedule.js` |
| Recent matches | Update buttons; multi-term search (guild/tag, player, skill, build, profession, map; match all/any) plus event, map, month, result, length filters; lineups in party order; template-code reader | `pages/home.js`, `data/recent.json` |
| Builds | Profession tabs (All grouped by profession); compact family cards; elite first, standard skill order; bold attributes + runes/insignias; Show theme (core + optional skills); Show variations (played-by line first, 15 at a time) | `pages/builds.js`, `data/builds.json`, `data/build_gear.json` |
| Meta | Elites by share of teams per month, most played builds (no team compositions) | `pages/meta.js`, `data/meta.json` |
| Guilds | Record, rating, maps; usual lineup = a lineup they actually played (per map too), bars as played; most played full lineups; players; recent results | `pages/guilds.js`, `data/guilds.json` |
| Players | Characters view (Player / Character / Profession columns, tick + assign to a player) and Players view (assigned players only, stats added up); column picker incl. per-combat-minute stats | `pages/players.js`, `data/players.json`, `data/aliases.json`, `data/player_combat.json` |
| Templates | Folders → templates → variations, each with equipment-template sets; saving asks for equipment | `pages/templates.js`, `data/templates.json` |
| Skills | All PvP-legal skills; click headers to sort; rank number + dropdown; notes per skill | `pages/skills.js`, `data/skills.json`, `data/skill_notes.json` |
| Mechanics | 26 one-topic pages from the wiki + Denning's tests (highlighted "Tested" lines), Misc last, Edit-on-GitHub link | `knowledge/*.md`, `knowledge/index.json` |
| Settings | GitHub key (fine-grained: Contents + Actions read/write) stored only in that browser; needed to save and to run updates | `pages/settings.js` |

## Data and sources of truth
- **Skills:** `data/skills.json` from the Guild Wars Wiki (PvP versions only). Never edit by hand; Denning's corrections go
  in `data/skill_notes.json` or a Mechanics page.
- **Schedule, map rotation, flux:** Guild Wars Wiki only — `wiki/Automated_tournament` (UTC weekday times, rotation)
  and `wiki/Flux` (07:00 UTC on the 1st). No AT-B. Not gvg.report.
- **Matches:** gvg.report public API (`/api/matches`, `/api/reports/{id}?payload=summary|overview`). Stored per month in
  `data/matches/`; `tools/gvgreport/aggregate.mjs` builds every summary file from them.
  - Party slot (`pos`) comes from the "Name (N)" label.
  - gvg.report sometimes records split skills by their original id (Soul Twisting 1240, "Coward!" 869…); the
    aggregator translates them to PvP ids via `data/template_id_map.json`.
  - Runes/insignias aren't recorded: runes are derived from bonus ranks; Denning's own go in `data/build_gear.json`.
- **Combat-minute stats:** gvg.report `/api/player-categories?period=all` → `data/player_combat.json` (≈630 regular
  characters).
- **Players:** `data/aliases.json` {"people": {"Player": ["Character", …]}} — Denning edits it from the Players page
  (66 players so far).
- **Denning's tests:** "Tested (date):" lines on the matching `knowledge/` page (or `misc.md`), plus `test-scenarios.md`.
  They override the wiki. Recorded so far: axe/hammer DPS predictions right; Weakness = 66% less auto-attack damage and
  −1 attributes; Vampiric life steal counts on the Master of Damage; Cracked Armor no effect on him; Victory or Death
  removed from the game.
- **Damage math:** `tools/gw_calc.py` (inscriptions +15%/+21%, Sundering, Vampiric, Zealous, Weakness).
- **Template codes:** `tools/gwtemplate.py` and `assets/js/template.js` (codes use canonical ids; mapped automatically).

## Updating
- **Update matches** (Recent matches page, or ask Claude): GitHub Action `update-matches.yml`. Fetches up to 400 new
  matches, fills missing party slots, refreshes combat stats, then rebuilds all summaries on the latest `main` and pushes
  (retries on races). If gvg.report's reports fail 8 times in a row it stops early and the page shows why
  (`data/sync_status.json`); skipped matches are retried next run. Claude can start it with
  `gh api -X POST repos/itsha12/gvginfo/actions/workflows/update-matches.yml/dispatches -f ref=main -f 'inputs[max_matches]=400'`.
- **Update skills from wiki:** `update-wiki.yml` (`tools/wiki/sync.mjs`; aborts if it parses <90% of skills; changes
  listed in `data/wiki_changes.json`). Never been run against the live wiki yet — check the result the first time.
- After changing aggregation code, run `node tools/gvgreport/aggregate.mjs` locally and commit the data too.

## State on 2026-10-15
- 1,631 matches stored of 1,661 listed (30 left; press Update matches once more).
- Last update: 391 fetched, 9 failed (gvg.report had an outage that day; fixed on their side).

## Things Claude can't do from its workspace (and the workarounds)
- The workspace shell can't reach gvg.report or the wiki. Use WebFetch for wiki pages, or the built-in browser pane on
  Denning's computer and `fetch()` from the page (sites already allowed: wiki.guildwars.com, gvg.report, tolkano.com).
  GitHub Actions *can* reach gvg.report, so bulk work belongs in the workflow.
- Screenshots: headless Chromium (`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`, Python Playwright). Serve the repo by
  intercepting requests to a fake host (`page.route`), launched with the proxy from `HTTPS_PROXY`; localhost doesn't work
  through the proxy.
- GitHub GraphQL is blocked; use `gh api` (REST). Action logs can't be downloaded; check step results via the jobs API.

## Ideas not started
- Calculator page in the site (damage / DPS / energy, rotation timing) reusing `tools/gw_calc.py`.
- Apply player assignments on the Guilds pages (they still show character names).
- Equipment-code item names (needs the wiki's item and modifier id tables).
- Counter-build helper, per-map mechanics, patch-watch view.
- Open questions: base crit-chance formula; whether inscription and customization add or multiply (test #19 on the
  Master of Damage settles it); whether the Feb 2026 nature-ritual 3500 range is live.


---

# Match replay analysis

**Status:** Active. Maga's nine OG comms matches done; Bounty and Nick still to do. Training batches now run on GitHub
(Train batch workflow). Last
updated 2026-11-06 (session 4n: forensics and event explanations, cache, match status; before that session 4m: engine
review, ENGINE 17, batches 2 to 5, first why chains).

## Start the next chat with
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/HANDOFF.md (the "Match replay
> analysis" section), knowledge/tactics.md and tools/replay_analysis/METHODS.md, then: <your request>

For a training batch, don't run it in the chat: start the "Train batch" workflow (METHODS.md "Train batch on GitHub",
e.g. pick=6, add_batch=yes), wait for it (about 10 to 15 minutes), pull main, read data/model/reports/latest.md and
explain it. For work in the chat that needs the engine: `git fetch --depth 1 origin +replays:refs/remotes/origin/replays`,
`pip install --break-system-packages interpret-core`, and in tools/replay_analysis `cache.py sync pull`, `cache.py warm`,
`analyze.py --all --out /tmp/ga`, `library.py build`, `status.py`.

How Denning wants results after each batch: the TQs (his four question categories, replacing the five random whys;
CLAUDE.md and METHODS.md "The TQs"): (1) a team behind on flags, why, and what different play would have raised its
win chances; (2) a monk death, why, and how to prevent it; (3) a power play that couldn't kill, why, and how to
convert it; (4) NPCs lost, why, and how to prevent it. Each answered with data, the alternative from measurement
(usual play, forensics' unused options, benchmarks, node models), with a confidence level.

## Next session
0. Batch 7 (2026-11-07, session 4p): 30 random matches from October and November (Train batch takes a `months`
   input). 91 matches trained. Fixed the same day (METHODS.md "Changes 2026-11-07"): phantom flag swings (lone carrier
   read as a sure capture), TQ 3's uptime, defenders listed as present at NPC kills while dead; added the lead-up trace
   and run benchmark (`tq.lead_up`, `tq.run_bench`) and the map in usual play (`MAP_COLS`, per-map splits). Rebuilt.
   Waiting on Denning: (a) cap lord_dps_own and lord_dps_enemy at 5 points (held-out log loss 0.404 -> 0.377; drop
   0.413; directions 0.393; cap + directions 0.384; all constants capped at 10 0.379; constants in 4 bins 0.502; strength
   alone 0.361), not yet in model_corrections.json; (b) whether the scoreboard should discount a carrier's ETA by its
   measured capture chance (3 to 5 alive against an enemy holding the stand with 6+: 2 of 14 captured).
1. Bounty's six matches (ask Denning for the transcripts), then Nick's one. Training batches stay paused until then.
2. Built in session 4o (2026-11-07), for Denning to check on the next real batch: the learning report's section "The
   TQs" (`tq.py`, METHODS.md "The TQs", "As built"). Ask him whether the instance picks suit him (biggest swing of each
   kind; monk death = the one that cost the most win chance, which favours late deaths) and whether the "different
   play" lines answer his question.
3. Known TQ gaps: a power play with no 2 s burst can't be read by the kill-conversion node (say so; maybe add a reading
   of the most exposed enemy at the start); the win model's flag-lead curve bends the wrong way at the extremes, so
   seconds of flag lead are sometimes not priced.
4. Speed after session 4o (Train batch workflow, 4 cores, rebuilding the report on the same 61 matches): learning
   report 11.6 min -> 5.8 min (candidate tests 4.2 -> 1.5 min, node models 3.7 -> 2.1 min, usual play 1.8 -> 0.9 min,
   TQs 0.5 min); whole run 15.6 -> 10.7 min including a one-off cache rebuild after the engine change. A normal batch
   should take about 9 to 11 min (an estimate; machine speed varies between runs: the first test run's report took 8.0
   min).

## Next: the commentary transcripts
Agreed with Denning: the matches go into training (flagged as chosen); the new variables they suggest matter most.
Process (METHODS.md "Commentary and comms"): match each transcript to its match by player names, line up with
`timeline.py`, file paraphrased claims in `data/commentary/<source>.json` with the engine's check, measure the
variables in `comms_vars.py`, move supported ones into the model and tactics, record the rest as open questions, and
`status.py mark <id> commentary <source> checked|done`.
- Done (session 4n): all nine of Maga's OG comms matches (claims in data/commentary/og_comms.json, 55 claims); batch 6;
  variables measured in data/benchmarks/comms_variables.json; made into model variables at Denning's request (METHODS.md
  "Commentary and comms"); power plays at home fixed; tactics P12 to P14, K17, L11, L12, X9, X10, M19, Q16 answered.
- Next: Bounty's six matches, then Nick's one (ask Denning for the transcripts).
- Open from the comms: lord.py's rebuilt health had the wrong leader in the OG v hold base race (both Lords died 0.3 s
  apart; check max health, boosts, the Amulet cap and player healing); area damage is found only where the skill is
  recorded or inferred; Denning to confirm gate (lock) control on Weeping Stone, "the jump", and Entourage (gvg.report
  records attackers needed to suppress it); does Aura of Faith reduce Lord damage (test on the Master of Damage).

## Fixes from the first why chains (batch 5): state
1. Done: mechanics stop at a symptom. Why chains now explain what dropped the health with forensics (`forensics.py`),
   and "why, in short" names the measured causes.
2. Partly: why damage uptime was low. Power plays now show the enemy group giving ground and joining its others, and
   own damage against the benchmark; "moving" is still not split into kiting, chasing, repositioning and running.
3. Open: fight windows overlap (a fight's consequence should end at the next fight's start).
4. Open: decisions too coarse (use the refined choice and the 15 nearest similar decisions; pick the decision that set
   up the fight).
5. Open: recording gaps (deaths with almost no recorded damage should be flagged "not recorded").
6. Done with 1: "why, in short" built from the measured causes.
7. Questions for Denning from batch 5 still open: cope's low uptime at Team v cope 10:00; EDGE's early 4/3 split at
   hook v EDGE 1:00; whether to keep unrecorded-damage moments in why chains.
Smaller: the regeneration fit is flat (delay 10 to 20 s fit equally); lord_damage_diff and flag_lead still bend at the
extremes; fight-state thirds give small cells in the boost-clock split.
Forensics limits to know: no line of sight or facing in the data (a ranger's bow reaches 1,498, so standing closer does
not by itself allow a shot); "ready interrupt" assumes base recharge; armor per set is estimated from a shield's base
16 armor; peel counts control only (snares, Blind, Weakness, interrupts, knockdowns, hexes), not body blocks.

## Goal
Find plays that are better than experts can see, from data across many matches: not to mirror Denning's or anyone's
judgement. Rulings give definitions and test cases; values and best plays come from the data (METHODS.md, "From
rulings to data"). The model must learn like a neural network but be white box: readable, explaining why with a
breakdown of contributions, and amendable by Denning (logged, tested corrections). Build the structure first, then
train slowly, a few matches at a time, with a learning report after each batch. Discovery of variables and
interactions nobody is aware of matters most. Along the way, become an expert GvG analyst and tactician: read any match, say what game state caused each fight and what the fight
caused (flag game, death penalty and pit NPCs above all in close games), whether macro or micro decided it, and answer
"what is the best play here" for given builds and situations from data and general principles, better than players.
Calibrate on Denning's rulings, then pull hundreds of matches for benchmarks and a win-probability model.

## How the knowledge is organized
- `knowledge/tactics.md` ("GvG tactics" on the site): the general model by situation, every line with an id (`F1`,
  `S18`...) cited by findings and situation cards. Section 14 holds the situation cards (the best play per recurring
  decision, with confidence). Labels: **Denning:** (overrides everything), **Bounty:** / **Nick:** (commentary),
  **OG comms:**, **Claude:** (proposals with match tags, revised when contradicted). No dates on Denning's lines.
- `knowledge/match-reviews.md`: one entry per match (summary paragraph, decided by, deciding moments, sources).
- `tools/replay_analysis/METHODS.md` (not on the site): the engine layers, how each concept is measured, the flag
  model and its accuracy, the death causes, known limits.
- `data/review_labels.json`: every ruling Denning has made on a specific moment (the calibration record).

## The analysis engine (`tools/replay_analysis/`, ENGINE 17)
1. `common.py`: shared thresholds, spike anchors and skill lists.
2. `state.py`: game state every second; flag spawns; NPC positions (`data/maps/`, written only with `--save-maps`).
3. `scoreboard.py`: every edge per team at any second: flag position (ETA, response on the next exchange, lead,
   backup flag, waiting runner), numbers, DP and spike threat, NPCs, Lord damage, build archetypes; `swing()` = what
   changed between two moments; `edge()` = provisional value.
4. `episodes.py` / `fights.py`: splits, flag runs, flag cycles (with how much slower than possible), deaths (cause,
   graded mistakes, cost until back), fights (trigger, situation, wipe, consequence, converted), monks, windows,
   posture.
5. `decisions.py`: decision points (enemy pickup, split in base, power play, boost clock, after a wipe, 24:00) as
   situation, choice, outcome.
6. `rules.py`: findings citing tactics ids, and the edge ledger.
7. `library.py`: `build`, `query`, and `compare <decision kind>` (outcomes by choice across matches).
8. `analyze.py`: runs everything (about 1 s per match). `integrity.py` (runs inside `Match()`): length repair, full
   pit roster, unobserved Lord damage, exclusions; `python3 integrity.py` lists what it found.
9. `benchmarks.py`: measured values from all replays (`lord`: Lord damage per second at the Lord; `regen`: Lord
   natural regeneration). Rebuild after new replays.
10. Win-probability model: `strength.py` (team strength: blend of guild fitted rating and lineup, measured),
    `lineup.py` (people's MAT-weighted records), `context.py` (matchup, map, flux priors; off until they beat
    strength), `lord.py` (Lord health and exposure), `fightstate.py` (expected deaths per team, out of match),
    `discovery.py` (leverage, behaviour clusters), `features.py` (named variables), `model.py` (glass box,
    explanations, corrections), `learning.py` (learning report), `batch.py` (pick and add batches). Site pages:
    "Win-probability model" and "Learning report (latest)". Needs `pip install --break-system-packages interpret-core`.
11. Causal model: `phases.py` (phases, plans, jobs, capacities), `buildfeat.py` (team build features, matchup pairs,
    per-player skill flags), `nodes.py` (node models: deaths, kill conversion, flag answers, pit NPC loss, Lord damage),
    `usual.py` (the usual play per decision kind and each choice's effect in win chance, compared between similar
    builds, with per-kind situation extras and splits by build and by player skills), `values.py` (every result and
    node cause priced in win points), `causal_map.py` (render and check `data/model/causal_map.json`, now version 10).
12. Explaining: `why.py` (why chains for one fight or the N biggest of a batch; learning report section "Why"),
    `snapshot.py` (detailed descriptive learnings: runners, flag answers, kill participation by skill, interrupts,
    knockdowns, spikes survived, monks, deaths; report section 9), `discovery.py` (leverage, behaviour clusters).
13. gvg.report sync: `tools/gvgreport/directory.mjs` (player directory, guild Elo) and `merge_players.py`; workflows
    "Sync gvg.report players and Elo" and "Probe gvg.report" (endpoints on branch `probe`).

## Plan (see METHODS.md "From rulings to data" and "The causal model")
- Now: make the why chains explain causes (fixes above), then keep training in batches of 6 with the why of 5 events
  after each. Value a second of flag answer and a point of Lord damage; build-specific choice effects as cells fill.
  The win model alone explains who is winning, not why (Denning).
0. Done: model structure (batch 0), ENGINE 17 fixes, batches 1 to 5 (53 matches). Next: batches of 6 random replays
   (`batch.py pick 6`), the why of 5 events and Denning's answers after each. No large pull until the reports settle.
1. Done: Bounty (6), Nick ([Men v Team]), Maga's OG comms (4), 4 good-guild matches, the engine, death rulings 1 and 2,
   the engine review (bugs fixed, scoreboard, fights, decision points, tactics restructure).
2. Now: calibrate on Denning's rulings (remaining [Men v HC C] deaths and power plays, judged as fights), each ruling
   becoming a label, a tactics line and an engine check; check the situation cards' defaults with him.
3. Then: redo the Bounty, Maga, Nick and earlier reviews with the engine; settle trade-offs with `compare` (8 monk
   defending a split, always collapse vs one damage pushing, double running, holding vs running when up on flags).
4. Then: grow the batches once learning reports settle; discovery and choice values as data accumulates.

## Current state (after batch 5, 53 matches)
- Batches: 0 (24), 1 (6), 2 (4), 3 (6), 4 (6), 5 (7 incl. one "latest" request); reports `data/model/reports/
  batch_00.md` to `batch_05.md` (batches 0 and 1 refitted with ENGINE 17). Older numbers in earlier handoffs were
  measured before the ENGINE 17 fixes (NPC roster leak, truncated RACK v hdm) and are superseded.
- Win model: not yet better than team strength alone (held-out log loss 0.530 against 0.439; accuracy 77% against
  73%; gain -0.09, 90% range -0.28 to +0.06). It ranks winners better but is overconfident; the gap narrowed from
  batch 1 to 4 and held in batch 5. Interactions on since 40 matches (morale with archers, with total DP, with the
  clock). Leans on morale, players within one spike, the stand, main-group numbers, flag lead. Correction logged:
  Lord damage read with the clock (Denning; tested, about neutral).
- Strength: blend of fitted guild rating and lineup (players who played, MAT x2 by measurement) predicts the latest
  third of stored results at log loss 0.31 (89%); gvg.report's Elo, rebuilt in time order, beats the in-game ladder
  but adds nothing on top. Context priors (matchup, map, flux) off: no gain yet.
- Node models (53 matches, unseen matches): deaths AUC 0.917 (baseline 0.804); kill conversion 0.802 (0.68); flag
  answer typical error 17 s (27 s; 68% of spread); pit NPC loss 0.826 (0.759); Lord damage 37% of spread; Lord kill
  0.968 (0.953).
- Values (win points, clear unless noted): a death -6 (healer -5.8, non-healer -6.1), a capture +3.2, a knight lost
  -7.8; a boost, an archer or the Bodyguard not clear yet.
- Usual play (53 matches; placebo check over the 30 s before): after a wipe, taking the flag instead of pushing the
  pit -16 (clear, not explained by who chooses it); at the boost clock, not running and falling back -6 and not running
  and advancing -13 (both clear; by fight-state thirds falling back costs most in even and winning fights, `D4`);
  split in base, defending without a collapse +10.7 against collapsing (clear); several enemy-pickup and power-play
  differences are partly who chooses them. Leverage: the choice matters most after a wipe and at the boost clock.
- Detailed (batch 4 snapshot, 46 matches): Mes/A runs most but slowest (median 42.5 s to capture) and most pushed;
  8 Monk carries mostly end in hand-offs; losers' flag answers are slower (median 53 s against 38 s); top kill
  participation Augury of Death, Word of Censure, Decapitate; most interrupted Healing Burst on the 7 Monk and Guardian
  on prots and 8 Monks; spikes survived 76% (winners) against 59% (losers), 8 Monks 45%.
- Why chains (batch 5): the setup and the cascade after a monk dies are read well (hook v EDGE 1:00, BcS v Men 1:00);
  the mechanics and decision steps need the fixes above.
- Lord: 28 of the first 30 matches ended with a Lord kill. Health rebuilt with Denning's regeneration rules; recorded
  Lord damage is already capped by the Amulet of Protection.
- gvg.report: players and Elo synced (`data/gvgreport/`); 482 new people and 65 of Denning's extended in aliases.json.
- Engine fixes this session: integrity layer, full pit roster, RACK v hdm length, unobserved Lord damage, hand-off
  loop in `episodes.flag_cycles` (hung BcS v yM).
- Older measurements still valid in method (flag model accuracy, death-cause list, collapse cost): see METHODS.md.

## Decisions made (confirmed by Denning)
- Session 4m: pit roster is 2 knights, 2 archers, Bodyguard, Lord; a third archer only on Isle of Solitude. Lords
  regenerate 10 health per second always, plus +2 rising to +10 once unhit for a few seconds; the Amulet of Protection
  adds healing. gvg.report's Elo is its own calculation and much better than the in-game ladder; use gvg.report's player
  assignments to add to the site's (Denning's win); weigh MAT results more (amount measured: x2). Build all fixes before
  refitting; batches of 6; fight-state split by thirds; Lord damage read with the clock. Report each batch as the WHY of
  5 match events: the goal is the why, not breakdowns.
- Up on flags = better position to get a boost and to run (the next capture exchange), not who capped last; backup
  flag and full running (1Y vs 2Y) are big advantages; a 1v1 defender running its flag partway shortens Y.
- Individual deaths don't win games: judge what caused a fight and what it caused. A balanced build that survives to
  26:00 without deaths or NPC losses is winning against a 2-monk hex way. DP stacking against a spike team is a big
  disadvantage even when each death is recoverable.
- Split answered on time at about 15 s; 60 s is late. Lone ranger answered by the Mes/A plus a frontline collapse.
- Deaths judged by cause first, then smaller mistakes graded basic, minor or acceptable, escalated when a monk is
  alone or after time. Quarter-second interrupts are luck.
- Death 1 ([hdm v HC I1], HC prot 8:10): a great play by hdm, with acceptable mistakes.
- Death 2 ([Men v HC C], HC 8 monk 9:31): HC was up on flags; staying out 3v4 while Men ran was an unnecessary risk.
  The runner could wait to cap; the backside group should fall back toward pit and follow only if Men went for the
  runner. Daze beside the ranger was a minor mistake. Not double running; half running is too risky.
- Cap as soon as reasonably possible after the enemy; the team running can't retreat to its pit.
- Builds change the best play, down to single skills (`B23`): a snare on a 1v1 defender favours collapsing (`S31`); a
  2-monk spike build is behind on Lord damage late, so it weighs DP over NPCs, often the reverse of other builds.
- What a wipe can be turned into depends on where it happened (`D5`); teams very rarely rush the enemy base to spike
  players as they resurrect.
- Near the enemy's boost, falling back is likely a mistake unless losing the fight; the read is own monks' energy,
  enemy health, enemy energy and numbers (`D4`). Whether to collapse on a split has no fixed line: plan, defender's
  ability, flag position and the main fight decide, and the line comes from data (`S32`).
- Monks die on purpose only for a base res (every 2 minutes on the minute), e.g. in their own base at 17:55 (`K14`).
- Healers matter only through damage: 3 healers + 1 damage against 2 + 2 is about even (`J12`).
- No energy estimate from casts: too large a build for what it adds.

## Open items
- Batch 2 next.
- Probe workflow (`probe-gvgreport.yml`, branch `probe`) finds gvg.report endpoints for new syncs.
- Death rulings 3 to 5 and power plays 6 and 7 in [Men v HC C].
- Situation cards (tactics section 14) are hypotheses for the data to test; D6 has no default.
- Lord damage weights replaced by measurement (`benchmarks.py lord`, `data/benchmarks/lord_damage.json`); the
  provisional `edge()` weights remain guesses until the win-probability model.
- Toolkit: race clock for base races; timed kills; "decided by" from the fights and edge ledger; Lord spawn positions
  in the trim.
- Benchmarks (a strong prot's spike catches, a good 7 monk's Infuse timing).

## Known issues and cautions
- The provisional edge's weights are guesses; with 24 matches, `compare` results are hypotheses only.
- Judge flag position with the scoreboard's flag lead (the exchange), never from who holds the stand (wrong twice,
  the second time because of a capture gvg.report recorded without a player; now fixed).
- Run Python with `PYTHONDONTWRITEBYTECODE=1`; `__pycache__` is now ignored by git.
- No NPC positions or energy in the data; zones and NPC positions are estimates. Energy will not be estimated (Denning).
- Store paraphrased events from transcripts, never the transcripts (public repo).

## Conventions
- Denning's terms: base (not home), backline (monks), midline (ele, ranger, paragon, mesmer), frontline (dervish,
  warrior, assassin), all by build; Y = the run from the flag spawn to the stand. Refer to players by role; times are
  match clock (m:ss).
- Reviews: summary paragraph first (result, 8v8 or not, flag game, splits, which roles were better), then decided by,
  deciding moments, sources, questions for Denning.
- Improve the toolkit rather than writing one-off scripts; each ruling becomes a label, a tactics line and a check.

## Recent changes
- Session 4o: the TQ section of the learning report (`tq.py`; replaces the five whys); speed-ups, each checked to give
  identical results: candidate tests pool every fold and reuse the honest test as the baseline (`model.test_candidates`),
  node models pool all their fits (`nodes.fit_nodes`), fight-state fits run side by side and only where a match is
  missing (`fightstate.build`), fight-state predictions are kept on the `cache` branch, the usual-play records are built
  once per report. Fixed `nodes._aoe_skills` (counts leaked between matches; lord_damage and lord_kill changed slightly).
  Found: the model library's fits differ in the last digits between processor types (log loss 0.554 against 0.550 on
  identical tables); `timings.json` now records the processor.
- Session 4n (end): Train batch workflow (.github/workflows/train-batch.yml, pinned libraries), fits side by side
  (parallel.py), held-out models from 10 groups of matches (cache.FOLDS), deaths models fitted only when needed,
  learning report section timers; Denning's TQs replace the five random whys (to build into learning.py next).
- Session 4n: Denning asked for the why of smaller events and every question answered with data. Built `forensics.py`
  (death questions with benchmarks by role), `events.py` (flag swings, power plays without a kill, survived spikes, pit
  NPC losses, splits; spike landing benchmarks), wired into `why.py` and the learning report (five events across kinds).
  Built `cache.py` (held-out models fitted once per batch and shared; prepared data saved by engine code, kept on the
  `cache` branch; parallel warm-up; analyze.py reuses saved analyses) and `status.py` (per-match tracking). Timing before:
  a why chain 82 s, the learning report over 11 minutes (stopped). Batches paused for the transcripts.
- Session 4m (continued): gvg.report players and Elo synced and merged; Lord regeneration per Denning; refit of batches
  0 and 1; batches 2 to 5; fight-state split by thirds; Lord-damage correction; `snapshot.py`; `why.py` and the first
  why chains with the fixes they showed are needed (see "Next session: fixes to do"); hand-off loop fixed.
- Session 4m: engine reviewed against the goal. Found and fixed: pit NPCs only recorded once touched (winners' pits
  looked empty: the backwards knights and Bodyguard curves), RACK v hdm cut at 2:30 (runs to 17:18), Lord damage
  unobserved in 2 Lord kills. Built: `integrity.py` (data checks and repairs, full roster from Denning: 2 knights, 2
  archers, Bodyguard, Lord; 3 archers on Isle of Solitude), `lord.py` (Lord health with measured regeneration, exposed;
  node `lord_kill`), lineup strength (`lineup.py`, Denning's idea, MAT weight measured) and the strength blend,
  `context.py` (priors, off), `fightstate.py` (fight state variable and situation control), hexes in the death and
  kill nodes, map shape and flux variables, pre-trend (placebo) check in the usual play, close-game and resampled
  accuracy in the honest test, `discovery.py` (leverage, behaviour clusters), data-integrity section in the learning
  report; causal map v10 (Lord health, exposed, killed; fight state; hex pressure; flux). Not refitted yet (Denning:
  build everything first).
- Session 4l: Denning on wipes and the boost clock (`D5`: a wipe at the stand can't be turned into NPCs before the res,
  and 7 of 12 "took the flag" cases couldn't reach the pit in time; `D4`: falling back with the enemy's boost near is
  likely a mistake unless losing the fight, it depends); builds in the usual play (similar builds, staged adjustment,
  splits by build); step 7 built (`values.py`, knowledge/values.md, learning report section 8); causal map v7. Then
  Denning on deliberate deaths (base res only, `K14`), individual bars and spike builds weighing DP over NPCs (`B23`),
  and what decides staying near the enemy boost (`D4`: monk energy, enemy health, enemy energy, numbers); boost-clock
  health difference added; values split by deliberate healer deaths and by the opponent's build; causal map v8.
  Then per-player skill flags built (`buildfeat.player_flags`), used for split answers (`S31`: a snare on the defender
  favours the collapse; first read conflated holder and collapser, corrected below); Denning: no energy estimate (too large);
  teams rarely rush the base to spike resurrected players (`D5`); causal map v9. Split answers then read the holding
  defender (first not collapsing from main) apart from collapsers, with main numbers and health: with a snare on the
  holder a collapse killed 5 of 10, without 0 of 14, and win chance ran Denning's way (unclear); `S32` (what decides a
  collapse; the line comes from data). Then collapse cost built (time away from main and what the main fight lost
  meanwhile; learning report section 7): median 16 s away; kills came within about 6 s; no collapse of 30 s or more
  killed; 60 s or more cost about 3.5 deaths at main (6 cases). Next: batch 2.
- Session 4k: Denning on pits (`P9` knights first, monk load of a full pit and area damage; `P10` two monks against a
  full pit; `P11` attackers leave before the res); area damage added; step 6 built (usual play); causal map v6.
- Session 4j: Denning on drops (`F33`: where a drop happens; parked in base = deciding not to run; long hand-offs away
  from base respond to pushes or deaths), killing during the enemy's flag cycle is a deliberate trade (`F34`), 8v8
  builds hold a flag near the fight (`F35`); runner speeds measured per runner; drops classified; step 5 built (pit
  NPC loss and Lord damage nodes); causal map v5.
- Session 4i: Denning on timing (`K14`: teams time kills; the dying team may die before time with death sets or by not
  healing; monks may die in base before time to reset energy; deaths can be positive); first look `K15`; distance
  threshold 3,000 for "away from the group"; step 4 built (flag-answer node); causal map v4.
- Session 4h: step 3 built (build features, death and kill-conversion node models, report section, `nodes.py
  explain`); 9:31 explained second by second; Denning: Draw Conditions onto the 8 is normal play but maybe a mistake
  (`M18`, data decides); jobs in the enemy base read from targets; `J12` healers matter only through damage.
- Session 4g: causal model steps 1 and 2 built (phases.py; ENGINE 16; library kind `groups`).
- Session 4f: causal model designed with Denning (fights are global; phases, plans, jobs and trades; capacities;
  matchup context; decisions modelled as the usual play); causal map version 1 (50 nodes, 169 links) with a site
  page; Denning's answers added to tactics (`J1` to `J11`, `K12`, `K13`, `M16`, `M17`); 12 design amendments.
- Session 4e: training round 1 (batch 1); candidate variables mechanism (`features.CANDIDATES`, tested every report);
  split_diff proposed and not yet supported.
- Session 4d: model structure built and run as batch 0 (not yet better than team strength alone, as expected at 24
  matches); strength ratings (82% of results predicted), named variables, glass-box model with staging, held-out
  explanations, corrections file, learning report, batch helper, site pages.
- Session 4c: model requirements set (white box, explains why, amendable, structure first, slow training with
  learning reports, discovery first); `interpret` (Explainable Boosting Machine) chosen and tested to install.
- Session 4b: Lord damage measured (ranger 37, ele 33, warrior 27, paragon 24, dervish 23, necro 10, mesmer 7 per
  second at the Lord); decision points record every player's action; D6 opened; data-first plan written.
- Session 4: engine review. Fixed: dead monks counted as out of range, all-monks range rule, death verdicts ignoring
  the cause, flag cycles sharing rows, the runner assumed to be the Mes/A, captures with no recorded player dropped,
  map files changing on every run, scattered thresholds. Added: scoreboard with the flag position model, fights,
  decision points, `library.py compare`, tactics ids and situation cards. Corrected the [Men v HC C] 9:31 reasoning
  (no boosts in that stretch; HC was up on flags by the exchange).
- Session 3: engine built (state, episodes, forensics, rules, ledger, library); death 1 and 2 rulings.
- Session 2: four good-guild matches reviewed; knowledge split into model and reviews; history rewritten.
- Session 1: Bounty, Nick and Maga reviews.
