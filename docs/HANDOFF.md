# GvG Info — handoff for a new Claude chat

Last updated 2026-11-04 (portal sections unchanged since 2026-10-15; match replay analysis section added). Attach this file (or just ask Claude to attach the repo) in a new chat, then say what you want.

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

**Status:** Active. Last updated 2026-11-05 (end of the fourth session: engine review and restructure).

## Start the next chat with
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/HANDOFF.md (the "Match replay
> analysis" section), knowledge/tactics.md, knowledge/match-reviews.md, tools/replay_analysis/METHODS.md and
> data/review_labels.json, then `git fetch --depth 1 origin replays:refs/remotes/origin/replays`,
> `pip install --break-system-packages interpret-core`, and run `python3 tools/replay_analysis/analyze.py --all --out
> /tmp/ga` and `library.py build`. Then, once Denning approves, build the causal model (METHODS.md "The causal
> model", build order), or: <your request>

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

## The analysis engine (`tools/replay_analysis/`, ENGINE 15)
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
8. `analyze.py`: runs everything (about 1 s per match).
9. `benchmarks.py`: measured values from all replays (so far `lord`: Lord damage per second at the Lord). Rebuild after
   new replays.
10. Win-probability model: `strength.py` (team strength), `features.py` (named variables), `model.py` (glass box,
    explanations, corrections), `learning.py` (learning report), `batch.py` (pick and add batches). Site pages:
    "Win-probability model" and "Learning report (latest)". Needs `pip install --break-system-packages interpret-core`.

## Plan (see METHODS.md "From rulings to data" and "The causal model")
- Causal model: steps 1 to 5 built (`phases.py`; `buildfeat.py`; `nodes.py` node models for deaths, kill conversion,
  flag answers, pit NPC loss and Lord damage, all beating simple baselines on unseen matches). Next: (6) usual-play models and decision comparisons, then link the
  node models to the win model so each cause is valued in win chance. Slow training continues (3 to 5 matches a batch). The win model alone explains who is winning, not why (Denning).
0. Done: model structure on the 24 stored matches (batch 0). Next: slow training, 3 to 5 random new replays per
   batch (`batch.py pick`), a learning report and Denning's answers after each. No large pull until the reports
   settle.
1. Done: Bounty (6), Nick ([Men v Team]), Maga's OG comms (4), 4 good-guild matches, the engine, death rulings 1 and 2,
   the engine review (bugs fixed, scoreboard, fights, decision points, tactics restructure).
2. Now: calibrate on Denning's rulings (remaining [Men v HC C] deaths and power plays, judged as fights), each ruling
   becoming a label, a tactics line and an engine check; check the situation cards' defaults with him.
3. Then: redo the Bounty, Maga, Nick and earlier reviews with the engine; settle trade-offs with `compare` (8 monk
   defending a split, always collapse vs one damage pushing, double running, holding vs running when up on flags).
4. Then: grow the batches once learning reports settle; discovery and choice values as data accumulates.

## Current state
- Stored replays: 30 on the `replays` branch: batch 0 (24) and batch 1 (6: 4 random picks plus the 2 newest from the
  standing "latest:2" request).
- Model after batch 1: beats team strength alone on unseen matches (79% vs 64% of winners, log loss 0.562 vs 0.633;
  still 79% vs 61% without the 3 short stomps). Open puzzle: the knights and Bodyguard curves run backwards although
  winners had more knights late in 9 of 14 matches; forcing the direction made held-out predictions slightly worse
  (0.576), and the split candidate (split_diff) didn't explain it (0.613). Awaiting Denning's view and more batches.
- Library on 24 matches: 376 deaths in 176 fights (45 wipes), 886 decision points, 279 flag cycles, 945 findings.
- Death causes: backline down 96, caught away from its group 58, out-pressured despite support 45, coordinated enemy
  pressure 45, spike 31, out of range of its monks 24, out-damaged despite prots 21, chased down while retreating 20,
  lack of support 19, forced flag run 12, outnumbered while up on flags 3, overextended 2.
- Flag model: answer-time error median -5 s (half within 15 s); lead sign matches the real exchange in 152 of 200.

## Decisions made (confirmed by Denning)
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

## Open items
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
- No NPC positions or energy in the data; zones and NPC positions are estimates.
- Store paraphrased events from transcripts, never the transcripts (public repo).

## Conventions
- Denning's terms: base (not home), backline (monks), midline (ele, ranger, paragon, mesmer), frontline (dervish,
  warrior, assassin), all by build; Y = the run from the flag spawn to the stand. Refer to players by role; times are
  match clock (m:ss).
- Reviews: summary paragraph first (result, 8v8 or not, flag game, splits, which roles were better), then decided by,
  deciding moments, sources, questions for Denning.
- Improve the toolkit rather than writing one-off scripts; each ruling becomes a label, a tactics line and a check.

## Recent changes
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
