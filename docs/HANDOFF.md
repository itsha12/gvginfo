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

**Status:** Active. Last updated 2026-11-04 (end of the first long session).

## Start the next chat with
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/HANDOFF.md (the "Match replay
> analysis" section) and knowledge/tactics.md, then fetch the `replays` branch. I'll attach commentary transcripts
> from Maga and Nick with their gvg.report links: fetch each replay, check every point the commentator makes against
> the data, and add what they teach to knowledge/tactics.md as commentator lines.

## Goal
In-depth reviews of GvG matches from gvg.report replays, in Denning's terms, explaining what led to the win condition.
Learn the game from Denning's corrections and from expert commentary, then test the learning on more matches, then pull
450+ matches and learn what winning guilds do differently.

## Plan (confirmed by Denning)
1. Next session: Maga and Nick commentary transcripts (same method as Bounty's).
2. Then review a few more matches to test what has been learned.
3. Only then the bulk pull.

## Current state
- **Pipeline (on main):** `tools/gvgreport/replays.mjs` + `.github/workflows/fetch-replays.yml`. Runs on GitHub (which
  can reach gvg.report) whenever `replays/requests.txt` changes. Each line: a report id or link, `latest:N`, or
  `list:N` (cheap listing of the newest matches to `listing.json`). Downloads the `replay` and `summary` payloads, trims
  them (`tools/gvgreport/replay_trim.mjs`, format gvginfo.replay.v1, TRIM_VERSION 3, keeps damage and heal kind) and
  saves to the `replays` branch: `index.json`, `YYYY-MM/<id>.json.gz`, `maps/<map id>.json.gz`, `listing.json`.
- **Stored replays: 16** (110 to 400 KB each). RACK matches: RJT vs RACK, RACK vs MBP, RACK vs hdm (Meditation and
  Uncharted), 옷옷옷옷 vs RACK, hold vs RACK (Meditation and Imperial), Men vs RACK. Commentary matches: Apes vs cope,
  옷옷옷옷 vs Book, OG vs hold, Team vs push, cope vs hdm, True vs One. Also RJT vs GW크 and OG vs cope (Uncharted,
  sent by mistake, not reviewed).
- **Reviewed with Denning:** RJT vs RACK, RACK vs MBP, 옷옷옷옷 vs RACK, hold vs RACK (Imperial), Men vs RACK.
  **Checked against Bounty's commentary:** the six commentary matches.
- **Not yet reviewed:** RACK vs hdm (Meditation, a loss, good vs good), RACK vs hdm (Uncharted), hold vs RACK
  (Meditation), RJT vs GW크, OG vs cope (no commentary; a good test of the learning).
- **Toolkit (on main):** `tools/replay_analysis/replaylib.py` (Match class: positions, groups, sides, carries, base
  from spawn positions, build-based role names incl. Eles by attunement, Rit/Para, WoC monks and the WoC snare) and
  `report.py` sections: builds, phases, stand (incl. long carries and near-miss boosts), npcs (pit kills, defenders,
  Entourage), lord (incl. base race), deaths (incl. "after time"), spikes (armor ignoring split, not saveable rule,
  prot and Infuse timing), splits (who shadowed them, snares, kills), output (damage per player per minute), totals.
- **Knowledge (on main):** `knowledge/tactics.md` holds everything taught: Denning lines (override everything), Bounty
  lines (confirmed by Denning), measures, open questions, guild notes and the review template. Also updated:
  `guild-lord.md` (Entourage incl. Tested 10.5 s, Solitude extra archer, Lord Health +1% per boost, Amulet open
  question), `conditions.md` (Deep Wound), `gvg-rules.md` (Lord Health).
- Last commit: see `git log` (this handoff is in the final commit of the session). No workflow runs in progress.

## Decisions made
- Replays trimmed on a separate `replays` branch, with the summary feed (confirmed by Denning).
- Perfect the process on a few matches and commentaries before any bulk pull (confirmed by Denning).
- 450+ matches eventually, in batches of about 100 (batch size proposed by Claude, not yet confirmed).
- Save up trim format changes, since each re-downloads every stored match (proposed by Claude, not yet confirmed).
- `knowledge/tactics.md` is the single home for what is learned; analysis code lives in the repo (agreed).
- Transcripts are attached by Denning; the YouTube transcript workflow was removed because YouTube blocks GitHub
  (confirmed by Denning).

## Key facts and figures
- gvg.report download per match: about 91 MB (replay) + 43 MB (summary); trimmed about 225 KB (measured).
- Spike anchors (Denning): 400 in 0.6 s survivable on shield set if armor respecting; 550 armor ignoring in 0.35 s
  can't be saved. Toolkit: "not saveable" only for targets at 60%+ health (derived; to be honed).
- Entourage lasts 10.5 s; Solitude has an extra pit archer; Lord Health 1,680 +1% per morale boost up to 1,848
  (all Denning).
- Denning's characters in RACK matches: Denning (8 monk), Denning E (Water Ele in the invoke spike).

## Open items and next steps
1. Maga and Nick transcripts (next session).
2. Test reviews: OG vs cope (no commentary), RACK vs hdm (Meditation), then others, leading with Bounty's frame (time,
   positioning and responses, playing the build as intended).
3. Unanswered: what RACK should have done after Men capped at 1:27 and parked on RACK's half; whether falling back to
   base (7:00 to 10:30) was forced. Whether the RJT vs RACK prots were out of position.
4. Benchmarks: a strong prot's spike catches (Ali) and a good 7 monk's Infuse timing.
5. Toolkit: race clock for base races (arrival, pit cleared, first Lord hit, Lord dead); timed kills (target held low
   before the 2-minute mark); prot position against the enemy's 3rd damage.
6. Maps: draw Isle of Meditation (outline stored) for front door vs backdoor; build walkable areas from positions for
   maps without outlines (Nomad's Isle).
7. Pending trim change to batch: keep Lord spawn positions (pit and base location).
8. Bulk pull when the process is settled; consider telling the gvg.report owner first.

## Known issues and cautions
- `gh` isn't logged in in Claude's workspace; start workflows by pushing `replays/requests.txt`. Commit all local edits
  before `git pull --rebase`, or the push silently doesn't happen.
- Check each gvg.report link matches its transcript (teams, map, winner); use `listing.json` to find the right match.
- Auto-transcripts garble names ("X-way" = hex way, "axes" = hexes, "Lisa" = Lyssa, "Shadow of Aests" = Shadow of
  Haste, "PE leak" = Power Leak); match them against the builds in the replay.
- Entourage cast gaps only mean suppressed when attackers were at the Lord. Zones are heuristics (base = spawn point,
  2,000 radius). Some prots have no recorded target; some conditions are only "condition"; numbers are estimates.
- A win with no Lord damage where the Lord and pit die together at the end is a resign.
- Don't use Denning's own word for chaotic games; say "chaotic".

## Conventions for this work
- Denning's terms: base, backside, push side, stand, pit, pit NPCs, outside archers; prot, 7 monk (push), 8 monk
  (backside), Mes/A, stand mes, hammer, AoB derv; holding the flag, double running (half, full), collapse, power play,
  solo split, 3 man split, 4-4, after time, timing someone. Refer to players by role, not character name.
- Reviews follow the template in `knowledge/tactics.md`: result and kind of game (stomps short), builds with matchup
  call outs (matches are blind), the chain to the win condition, player detail only where decisive, questions at the
  end. Denning's teachings go in as **Denning:** lines, his tests as **Tested (date):**, commentators' as named lines.
- Times are match clock (m:ss). Improve the toolkit rather than writing one-off scripts.

## Recent changes
- 2026-11-04: Built the replay pipeline and `replays` branch; saved the analysis toolkit.
- 2026-11-04: Reviewed five RACK matches with Denning; created and grew `knowledge/tactics.md` from his corrections.
- 2026-11-04: Learned from six Bounty commentaries (confirmed by Denning); added after-time, output, base race,
  near-miss boost and splits measures.
- 2026-11-04: Final check that every learning from the session is captured (prot rule wording, open questions,
  guild notes, small commentary points).
