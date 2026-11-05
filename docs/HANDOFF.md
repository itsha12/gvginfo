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

**Status:** Active. Last updated 2026-11-05 (end of the second session).

## Start the next chat with
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/HANDOFF.md (the "Match replay
> analysis" section), knowledge/tactics.md, knowledge/match-reviews.md and tools/replay_analysis/METHODS.md, then
> fetch the `replays` branch. Then: <your request>

## Goal
Become an expert GvG analyst and tactician: read any match, say whether macro or micro decided it and why, and answer
"what should they have done" questions from general principles, not just recall past games. Learn from Denning's
corrections, expert commentary and team comms; test on more matches; then pull 450+ matches to back the principles
with numbers.

## How the knowledge is organized (since 2026-11-05)
- `knowledge/tactics.md` ("GvG tactics" on the site): the general model by situation. Sections: how matches are won
  (win conditions, the edges, macro vs micro), builds and matchups, splits, main team and pit play, the flag game,
  kills and timing, late game and 28:00, spikes, monk play, interrupts, positioning, weapon sets, language, open
  questions. Line labels: **Denning:** (overrides everything), **Bounty:** / **Nick:** (commentary), **OG comms:**,
  **Claude:** (proposals, each with match tags as evidence, revised when contradicted).
- `knowledge/match-reviews.md` ("Match reviews"): how a review is written, sources, guild notes, one entry per match
  (summary paragraph, decided by, deciding moments, what comms or commentary added). Tags like [OG v cope U].
- `tools/replay_analysis/METHODS.md`: how each concept is measured (not on the site).

## Plan
1. Done: Bounty (6 matches), Nick ([Men v Team]) and Maga's OG comms ([OG v chic], [OG v cope J], [OG v hdm],
   [OG v cope U]).
2. Next: review more matches with no commentary to test the model (RACK v hdm Meditation, hold v RACK Meditation,
   RJT v GW크), each ending with questions for Denning; work through the open questions on the tactics page.
3. Then the bulk pull (450+ in batches of about 100, proposed, not confirmed), and turn principles into measured
   patterns (e.g. how often a split that never takes a knight still wins).

## Current state
- **Pipeline:** `tools/gvgreport/replays.mjs` + `.github/workflows/fetch-replays.yml`, run on GitHub whenever
  `replays/requests.txt` changes (a report id or link, `latest:N`, or `list:N`). Trimmed replays on the `replays`
  branch (format gvginfo.replay.v1, TRIM_VERSION 3).
- **Stored replays: 20.** RACK: RJT v RACK, RACK v MBP, RACK v hdm (Meditation, Uncharted), 옷옷옷옷 v RACK, hold v
  RACK (Meditation, Imperial), Men v RACK. Commentary: Bounty's six, [Men v Team]. OG comms: the four OG games. Also
  RJT v GW크 and two from `latest:2`.
- **Toolkit:** `replaylib.py` (Match class; `Match.from_branch(id)`) and `report.py <id> [sections]`: builds, phases,
  stand, npcs, lord, deaths, spikes, splits, output, pit (players in own pit / field / enemy pit, death distance from
  pit), catches (spike catching per team), totals.
- Run Python with `PYTHONDONTWRITEBYTECODE=1`, or a tracked `__pycache__` file blocks `git pull --rebase`.

## Decisions made
- Replays on a separate `replays` branch (confirmed). Perfect the process before any bulk pull (confirmed).
- Transcripts are attached by Denning (YouTube blocks GitHub).
- Knowledge restructured into a model (tactics) and evidence (match reviews), with measurement notes off the site
  (asked for by Denning).
- No dates on Denning's tactical lines; **Tested (date):** lines keep their dates (patches change mechanics).

## Key facts
- gvg.report download per match: about 91 MB (replay) + 43 MB (summary); trimmed about 225 KB.
- Spike anchors: 400 in 0.6 s survivable on shield set if armor respecting; 550 armor ignoring in 0.35 s can't be
  saved. Good spike catching: prots 0.3 to 1.0 s after the first hit (hdm caught 17 of 20; cope 12 of 34).
- Entourage lasts 10.5 s; Solitude has an extra pit archer; Lord Health 1,680 +1% per boost up to 1,848.
- Denning's characters in RACK matches: Denning (8 monk), Denning E (water ele in the invoke spike).
- Transcript offsets differ per video; anchor on 2 or 3 kills or caps.

## Open items
- The open questions at the end of the tactics page.
- Benchmarks: a strong prot's spike catches (Ali) and a good 7 monk's Infuse timing.
- Toolkit: race clock for base races; timed kills; prot position against the enemy's 3rd damage; a "decided by"
  helper (edges over time: death penalty, boosts, pit NPCs, numbers).
- Maps: draw Isle of Meditation for front door vs backdoor; walkable areas for maps without outlines.
- Pending trim change to batch: keep Lord spawn positions.
- Bulk pull when settled; consider telling the gvg.report owner first.

## Known issues and cautions
- `gh` works in the workspace; start workflows by pushing `replays/requests.txt`. Commit all local edits before
  `git pull --rebase`.
- Check each gvg.report link matches its transcript (teams, map, winner, round order).
- Auto-transcripts garble names ("X-way" = hex way, "Ellie"/"LE" = elementalist, "Lisa" = Lyssa).
- Entourage gaps only mean suppressed when attackers were at the Lord. Zones are heuristics. Numbers are estimates.
- Don't use Denning's own word for chaotic games; say "chaotic".

## Conventions
- Denning's terms (see Language on the tactics page); refer to players by role. Times are match clock (m:ss).
- Reviews: summary paragraph first (prose, with 8v8, flag game, splits and which roles were better woven in), then
  decided by, deciding moments, what sources added, questions. Lessons go to the tactics page as general lines.
- Improve the toolkit rather than writing one-off scripts.
