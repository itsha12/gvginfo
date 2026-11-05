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

**Status:** Active. Last updated 2026-11-05 (end of the third session).

## Start the next chat with
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/HANDOFF.md (the "Match replay
> analysis" section), knowledge/tactics.md, knowledge/match-reviews.md, tools/replay_analysis/METHODS.md and
> data/review_labels.json, then fetch the `replays` branch and run `python3 tools/replay_analysis/analyze.py --all
> --out /tmp/ga` and `library.py build`. Then continue the death rulings in [Men v HC C] (deaths 3 to 5, then power
> plays 6 and 7), or: <your request>

## Goal
Become an expert GvG analyst and tactician: read any match, say whether macro or micro decided it and why, and answer
"what should they have done" questions from data and general principles, better than players. Calibrate the engine on
Denning's rulings, then pull hundreds of matches to back the principles with numbers and a win-probability model.

## How the knowledge is organized
- `knowledge/tactics.md` ("GvG tactics" on the site): the general model by situation. Labels: **Denning:** (overrides
  everything), **Bounty:** / **Nick:** (commentary), **OG comms:**, **Claude:** (proposals with match tags, revised
  when contradicted). No dates on Denning's lines.
- `knowledge/match-reviews.md`: one entry per match (summary paragraph, decided by, deciding moments, sources).
- `tools/replay_analysis/METHODS.md` (not on the site): the engine layers, how each concept is measured, the rules
  and death causes, known limits.
- `data/review_labels.json`: every ruling Denning has made on a specific moment (the calibration record).

## The analysis engine (`tools/replay_analysis/`)
1. `state.py`: game state every second (positions, zones, carrier, stand owner, main group, pit NPCs, estimated NPC
   positions saved to `data/maps/`).
2. `episodes.py`: splits (split, flank, full team collapse), flag runs (escort, pushers, double running), flag cycles
   (pickup vs the enemy's, cap delay, runner trip back, enemies in the way, a second runner waiting at base), stand.
3. `fights.py`: death forensics (numbers, flag situation, backline range and state, prots, knockdowns, interrupts,
   conditions, approach, peel) and `assess` (a cause plus graded mistakes); monk profiles; numbers windows; posture.
4. `rules.py`: findings with verdicts (good, on time, late, missed, risky, mistake, great enemy play, note) and the
   edge ledger.
5. `library.py`: case library across matches (`build`, then `query <kind> --where --show --sort --limit`).
6. `analyze.py`: runs everything per match (ENGINE 14). Next layers, after the bulk pull: benchmarks and a
   win-probability model.

## Plan
1. Done: Bounty (6), Nick ([Men v Team]), Maga's OG comms (4), 4 good-guild matches, the engine (layers 1 to 4 and
   the library), death rulings 1 and 2.
2. Now: calibrate on Denning's rulings (remaining [Men v HC C] deaths and power plays), adding each as a label, a
   tactics line and an engine check.
3. Then: redo the Bounty, Maga, Nick and earlier reviews with the engine; settle trade-offs with data (8 monk
   defending a split, always collapse vs one damage pushing, double running).
4. Then: bulk pull in batches of about 100 (proposed), benchmarks, win-probability model.

## Current state
- Last commit: see `git log` (this session ended with the ENGINE 14 commit, after 84d5ab5).
- Stored replays: 24 on the `replays` branch (last workflow run 2026-11-05, none in progress).
- Library on 24 matches: 376 deaths, 234 splits, 551 flag runs, 300 flag cycles, 1,121 monk phases, 281 numbers
  windows, 844 findings. Whole run about 15 s.
- Death causes now: positioning 257, unclear 38, coordinated enemy pressure 31, forced flag run 23, spike 14,
  outnumbered away from pit while up on flags 6, lack of support 2.

## Decisions made (confirmed by Denning)
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
- Unanswered: is Men's 4-minute gap without a cap (4:52 to 8:55) a flag mistake, or normal for the team holding pit
  pressure?
- Split the "positioning" death cause (2 of 3 deaths) into real situations.
- Toolkit: race clock for base races; timed kills; "decided by" from the edge ledger; Lord spawn positions in the trim.
- Benchmarks (a strong prot's spike catches, a good 7 monk's Infuse timing).

## Known issues and cautions
- Possible bug: two HC flag cycles in [Men v HC C] (6:23 and 7:58) show the identical list of enemies in the way.
  Check before trusting runner trip numbers. `runner_back_s` is empty; the field in use is `trip_s`.
- Judge who is up on flags from the stand at boosts and the last cap, not from cap delays (I got this wrong once).
- Run Python with `PYTHONDONTWRITEBYTECODE=1` (a tracked `__pycache__` file blocks `git pull --rebase`).
- No NPC positions or energy in the data; zones and NPC positions are estimates.
- Store paraphrased events from transcripts, never the transcripts (public repo).

## Conventions
- Denning's terms: base (not home), backline (monks), midline (ele, ranger, paragon, mesmer), frontline (dervish,
  warrior, assassin), all by build. Refer to players by role; times are match clock (m:ss).
- Reviews: summary paragraph first (result, 8v8 or not, flag game, splits, which roles were better), then decided by,
  deciding moments, sources, questions for Denning.
- Improve the toolkit rather than writing one-off scripts; each ruling becomes a label, a tactics line and a check.

## Recent changes
- Session 3: engine built (state, episodes, forensics, rules, ledger, library); death 1 and 2 rulings; flag cycles
  per cap; up-on-flags death cause.
- Session 2: four good-guild matches reviewed; knowledge split into model and reviews; history rewritten.
- Session 1: Bounty, Nick and Maga reviews.
