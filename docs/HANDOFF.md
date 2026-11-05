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

**Status:** Active. Last updated 2026-11-04.

## Start the next chat with
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/HANDOFF.md (the "Match replay
> analysis" section) and knowledge/tactics.md, then fetch the `replays` branch and review <match> with
> `python3 tools/replay_analysis/report.py <report id>`, following the review template in knowledge/tactics.md.

## Goal
In-depth reviews of GvG matches from gvg.report replays (positions about once a second, every cast with its target,
damage with type, interrupts, knockdowns, enchantments and hexes, flag events, pit NPCs, Lord damage), explaining what
led to the win condition in Denning's terms. Perfect the process on a few matches, then pull 450+ matches and learn what
winning guilds do differently.

## Current state
- **Pipeline (on main):** `tools/gvgreport/replays.mjs` + `.github/workflows/fetch-replays.yml`. Runs on GitHub (which can
  reach gvg.report) whenever `replays/requests.txt` changes. Each line: a report id or link, `latest:N`, or `list:N`
  (cheap listing of the newest matches to `listing.json`, no replays). Downloads the `replay` and `summary` payloads,
  trims them (`tools/gvgreport/replay_trim.mjs`, format gvginfo.replay.v1, TRIM_VERSION 3) and saves to the `replays`
  branch: `index.json`, `YYYY-MM/<id>.json.gz`, `maps/<map id>.json.gz` (map outlines), `listing.json` (400 newest).
- **Stored replays (9, all trim 3, 110 to 400 KB each):** RJT vs RACK (Nomad's, 2026-11-04), RACK vs MBP (Meditation,
  2026-11-04), RJT vs GW크 (Meditation, 2026-11-04), RACK vs hdm (Meditation, 2026-10-17, hdm won), 옷옷옷옷 vs RACK
  (Solitude, 2026-10-17), RACK vs hdm (Uncharted, 2026-10-17, RACK won), hold vs RACK (Meditation, 2026-10-17), hold vs
  RACK (Imperial, 2026-11-01), Men vs RACK (Nomad's, 2026-11-01).
- **Reviewed:** RJT vs RACK, RACK vs MBP (redone as a whole-game review), 옷옷옷옷 vs RACK (stomp, WoC spike), hold vs RACK
  (Imperial, invoke spike), Men vs RACK (RACK resigned).
- **Toolkit (on main):** `tools/replay_analysis/replaylib.py` (Match class: positions, groups, sides, carries, base from
  spawn positions, build-based role names) and `report.py` (sections: builds, phases, stand, npcs, lord, deaths,
  spikes, splits, totals).
- **Knowledge (on main):** `knowledge/tactics.md` holds everything Denning has taught (terms, game types, flag running,
  double running, holding the flag, splits and how 8v8 builds answer them, monk play, spike builds and saveable
  anchors, pit NPCs and 28:00, resigns, review template). `knowledge/guild-lord.md` (Entourage, Lord Health per boost),
  `knowledge/conditions.md` (Deep Wound) and `knowledge/gvg-rules.md` were updated too.
- **CLAUDE.md** points Claude to the replays branch, the toolkit and the tactics page.
- Last commit before this handoff: `143133b` (the handoff commit follows). No workflow runs in progress.

## Decisions made
- Replays stored trimmed on a separate `replays` branch, not in the portal (confirmed by Denning).
- Summary feed included with every replay (confirmed by Denning).
- Perfect the review process on a few matches before any bulk pull (confirmed by Denning).
- Goal of 450+ matches, pulled in batches of about 100 (batch size proposed by Claude, not yet confirmed).
- Save up trim format changes and apply them together, since each change re-downloads every stored match (proposed by
  Claude, not yet confirmed).
- `knowledge/tactics.md` is the single home for what Denning teaches; the analysis code lives in the repo, not in chat
  (proposed by Claude, done; Denning agreed GitHub should hold the learning).

## Key facts and figures
- gvg.report download per match: about 91 MB (replay) + 43 MB (summary); about 60 GB for 450 matches (measured on one
  match). Trimmed: about 225 KB average (measured on 9).
- Spike anchors (confirmed by Denning): 400 damage in 0.6 s should be survivable on a shield set if armor respecting; 550
  armor ignoring in 0.35 s can't be saved. Toolkit flags "not saveable" for targets at 60%+ health with 550+ armor
  ignoring, or more than their health, within 0.35 s (derived; to be honed).
- Entourage lasts 10.5 s; Solitude has an extra pit archer; Lord Health is 1,680 plus 1% per morale boost, up to 1,848
  (all confirmed by Denning).

## Open items and next steps
1. Unanswered from the Men review: what RACK should have done once Men capped at 1:27 and parked on RACK's half; whether
   falling back to base (7:00 to 10:30) was forced.
2. Review more stored matches, especially RACK vs hdm on Meditation (good vs good, a loss), then RACK vs hdm on Uncharted
   and hold vs RACK on Meditation.
3. Benchmarks: a strong prot's spike catches (Denning suggests Ali) and a good 7 monk's Infuse timing.
4. Maps: draw Isle of Meditation (outline stored) to settle whether RACK splits through the front door or backdoor;
   for maps gvg.report has no outline for (Nomad's Isle), build walkable areas from player positions across matches.
5. Pending trim changes to batch: keep the Lord spawn positions (to locate the pit and base precisely).
6. When the process is settled: bulk pull in batches (`latest:100`, or ids picked from `listing.json`); consider telling
   the gvg.report owner first given the download size.

## Known issues and cautions
- `gh` isn't logged in in Claude's workspace; start workflows by pushing a change to `replays/requests.txt`. Commit all
  local edits before `git pull --rebase`, or the push silently doesn't happen.
- Entourage cast gaps only mean suppressed when attackers were at the Lord; some Lords don't cast it while idle.
- Zones (base, stand, sides) are heuristics: base = team spawn point with a 2,000 radius; check odd results.
- Some prots have no recorded target; 277 conditions in one match were only "condition"; numbers are gvg.report
  estimates. Aura of Displacement teleports are real moves, not glitches.
- A win with no Lord damage where the Lord and pit die together at the end is a resign.
- Don't describe chaotic games with Denning's own word for them; say "chaotic".

## Conventions for this work
- Denning's terms: base, backside, push side, stand, pit, pit NPCs, outside archers; prot, 7 monk (push), 8 monk
  (backside), Mes/A, stand mes, hammer, AoB derv; holding the flag, double running (half and full), collapse, power
  play, solo split, 3 or 4 man split. Refer to players by role, not character name.
- Reviews follow the template in `knowledge/tactics.md`: result and kind of game (stomps get a short summary), builds
  with matchup call outs (matches are blind), the chain to the win condition, player detail only where decisive, and
  specific questions at the end. Add what Denning teaches as **Denning:** lines; his in-game tests as **Tested (date):**.
- Times are match clock (m:ss). Improve the toolkit rather than writing one-off scripts.

## Recent changes
- 2026-11-04: Built the replay pipeline (probe, trim, summary feed, damage types, listing) and the `replays` branch.
- 2026-11-04: Reviewed RJT vs RACK twice (split 4v4, prot coverage, the 8 monk death) and RACK vs MBP twice.
- 2026-11-04: Created and grew `knowledge/tactics.md` from Denning's corrections; fixed Lord Health, Entourage notes.
- 2026-11-04: Saved the analysis toolkit; added spike, splits and long-carry measures.
- 2026-11-04: Reviewed 옷옷옷옷 vs RACK (WoC spike stomp), hold vs RACK (invoke spike), Men vs RACK (resign).
