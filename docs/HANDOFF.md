# GvG Info — handoff for a new Claude chat

Last updated 2026-11-07 (portal sections unchanged since 2026-10-15; match replay analysis updated, session 4r). Attach this file (or just ask Claude to attach the repo) in a new chat, then say what you want.

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

**Status:** Active. Last updated 2026-11-07 (session 4s: Denning's rulings on the batch 9 proposals built; full
rebuild started with the Train batch workflow, add_batch no, rebuild_forensics yes; jobs may now run 3 hours).
Previous update: session 4r. Building the learned causal map: steps 1 (event layer) and 2
(data-valued wrong casts, nine learned node models with measured link strengths) done. Session 4r: the Train batch run
is split across parallel GitHub jobs, and batch 9 (20 random matches, 15 from September and 5 from October) trained:
133 matches. Next: Denning's rulings on the three pending proposals (3, 11, 14), then build the approved ones in one
engine change before the next run, then the commentary transcripts and step 3 (discovery).

### Session 4s (2026-11-07)
- Built 16 of the 17 batch 9 proposals (all but 10) in one engine change; details in METHODS.md "Rulings after batch 9".
  Notable: the data picks the `spike_killable_diff` cap (10 to 25 points, or none; data/model/cap_choices.json); win
  chances go through a calibration by minute (data/model/calibration.json); forensics position uses the last 3, 5 or
  8 s, whichever best separates deaths from other fight moments (forensics.json "position_window"); the Lord damage
  node is fitted in two parts; values are against matched moments.
- Tested here on 12 matches end to end (every report section and TQ ran). Fixed on the way: a direction correction
  leaves no spread on its curve; the robust loss diverged until centred and scaled.
- Train batch: `timeout-minutes` 180 for every job; new input `rebuild_forensics` (run `forensics.py bench` first).
- Rebuild done (27 min whole run on GitHub; a first try failed on a report line, fixed). Readings at 133 matches:
  glass box log loss 0.375 against 0.463 for strength alone (not yet clear); cap test chose no cap on
  `spike_killable_diff` (none 0.3758, 25 points 0.3761, 10 points 0.3869); calibration's biggest correction is 6 to 12
  min, where teams given about 3.5% won 21%; position window chosen 3 s (AUC 0.632 against 0.624 for 5 s and 0.611 for
  8 s, so the windows differ little); Lord damage node now honestly adds (typical error 71 against 92); flag swing and
  split effect now narrowly beat their baselines, capture speed still doesn't; values against matched moments: a death
  -8.9, a knight -9.0, a capture +1.5.
- Denning on the rebuild: mid-game comebacks about one in five match what he sees (tactics W13); a knight is worth
  about a death (W12); the 3 s position window is acceptable.
- Found reading the rebuild's report, proposed to Denning (not built; each is an engine change, so bundle them before
  the next run): (a) calibration's pooled flat stretches erase small changes (TQ 1 read 22 s of flag lead as +0.0
  points): a per-band logistic recalibration (a shift and a slope per minute band) never goes flat; (b) morale x map
  geometry pairs are now the model's top terms (morale x pit-to-stand 0.717) and drive the biggest surprises (-45.5):
  test blocking them on held-out matches, the data to decide, like the cap test; (c) TQ 4's NPC-loss what-ifs read
  more defenders as more loss (27.5% -> 31.1% -> 34.3%) against the node's own defenders curve: mark a what-if that
  runs against the variable's main curve as coming from a pairing; (d) TQ 4 text says "after it entered the base" for
  a split that never entered.
- Denning approved (a) to (d), built (METHODS.md "After the batch 9 rebuild"), plus his split-depth variable for the
  collapse node (P.20); answers recorded on tactics K14 (energy isn't tracked, so deliberate deaths can't be told
  apart) and S32 (a quick collapse that fails to kill fails twice). Second rebuild started (add_batch no).
- Second rebuild done (all sections ran): pair test kept the morale x map pairs (allowed 0.3752, blocked 0.3937);
  cap test again no cap; split depth not clear yet (gain -0.0004 +/- 0.0038, each reading alone not clear); the
  collapse timing readings alone moved from supported to not clear between the two rebuilds (near the line; the
  group P.9 stays supported); TQ 4's backwards what-ifs now marked "from a pairing"; values: death -9.5, knight -9.1,
  boost +5.8, possibly deliberate healer death -8.0.
- Found, proposed to Denning: (e) TQ 1 still reads 22 s of flag lead as +0.0, because the win model's flag_lead curve is
  small (at most 2.6 points) and runs backwards at both ends (-129 to -67.5 s reads +0.4, +67.5 to +129 s reads -1.6):
  force its direction upward; (f) the shift-and-slope calibration misses some cells (12 to 18 min: predicted 93%, won
  92%, calibrated 77%; 6 to 12 min: 3.5%, won 21%, calibrated 12.7%): a pooled lookup joined by straight lines between
  the pooled blocks' middles would be as accurate as the first form and never flat.
- Denning approved (e) and (f), built (METHODS.md "After the batch 9 rebuild"); third rebuild started.
- Next: read the third rebuild with Denning, then the commentary transcripts (Bounty's six, then Nick's one).

### Session 4r (2026-11-07)
- Train batch split (`.github/workflows/train-batch.yml`, METHODS.md "Train batch on GitHub"): prepare -> six parts at
  once (main, learned, cands, nodes:deaths, nodes:lord_kill,npc_loss, nodes:kill_conversion,lord_damage,flag_answer) ->
  finish (values priced, TQs, snapshot, cache push, commit). `learning.py part <name>` / `learning.py finish`;
  `learning.py` alone still runs everything on one machine. Checked: a rebuild of batch 8 through the split gave the
  same report apart from processor noise.
- Run times: rebuild with no new matches 11 min whole run (prepare 3, longest part 3, finish 4). Batch 9 (20 new
  matches) 27 min: prepare 12 (fetching 20 replays 3.3 min at gvg.report's 4 s spacing; preparing the new matches'
  data 7 min), main part 12 (learned nodes 6.7 min building the new matches' event records, values 2.3), finish 2.5.
  After batch 9 the learned nodes got their own part (`learned`; not yet run on GitHub, first use next batch), which
  should take the main part to about 5 min. Further speed-up if wanted: spread prepare's per-match data across machines.
- Batch 9 report: glass box log loss 0.377 against 0.463 for strength alone (gain +0.086, range -0.035 to +0.196, ahead
  but not yet clear; the new matches were harder for strength alone, 0.412 -> 0.463). Morale now leads (0.691), with
  new morale x Lord-damage-rate interactions. Learned-node links supported: 17 of 50 (13 before). Newly supported:
  damage against the usual -> kill conversion; commitment (pushed) -> kill conversion; split size and free defenders
  -> split answer; defender snares and split speed -> collapse deaths; split-answer latency -> deaths. Flipped to not
  clear: split size and main numbers -> collapse deaths. Rejected by data: Blind on own players in the last 10 s ->
  kill conversion (Claude's link, tiny either way, -0.0007; it was supported at +0.0011 in batch 8, a near-line
  flip). Denning's held link (Blind on the enemy frontline -> fights) moved from rejected to not clear yet.
  Usual play: split in base, collapsing -4.3 against defending without a collapse (clear); after a wipe, taking the
  flag -4.6 against pushing the pit (clear, smaller than at 53 matches); boost clock, not running and falling back
  -4.0 (clear). Values: a death -5.0, a death while the team is boosted -19.8, a knight -4.8, the Bodyguard -3.8, a
  capture +1.7.
- After batch 9, from Denning (engine changed, not yet rebuilt):
  - Blind is measured as time spent Blind, not the number of Blinds (eventlayer.py keeps each Blind's end and whether
    the target is a physical attacker; lnrows.py `_blind_secs`). Every Blind now counts: the replays leave the caster
    blank on 56% of Blinds (799 on players in 133 matches, 353 with a caster), and the old code dropped those.
    Features: `blind_secs_on_own_10s` (K.11 -> K.4, own attackers only), `blind_front_secs_diff` and
    `blind_defensive_secs_diff` (P.19 -> R.2). K.11 -> K.4 reset from rejected to hypothesis.
  - No boosted-death variable. The boosted / not boosted death split is gone from values.py: it measured position
    (later in the match, already winning), not the death (tactics K18 revised with the matched comparison).
  - The event-layer, learned-node and value data for all 133 matches rebuild on the next Train batch run. Expect the
    `learned` part to be much slower that one time (perhaps 30 to 40 min). Make the forensics position fix first if
    Denning approves it, so there is only one rebuild.
- **Proposed after batch 9, with Denning's rulings** (numbers from 133 matches). All approved except 10; built in
  session 4s as one engine change (METHODS.md "Rulings after batch 9"), then a full rebuild of the 133 matches:
  1. **Approved.** Win model: drop the `lord_damage_diff` main term, keep only its pairing with the clock (curve is a sign marker:
     +-7 to 9 points once any Lord damage exists; the most negative band reads +31.6, backwards; teams ahead on Lord
     damage won 88%, with alive +0.94 and morale +78: it marks who got into the pit, not the tiebreak).
  2. **Approved.** Win model: cap or block pairings of build-fixed values (Lord damage per second, spike build) with morale. The batch
     7 cap covers the main terms only; morale x Lord damage per second came back 3rd and 4th (0.42 each).
  3. **Approved (after an explanation).** Win model: test caps on `spike_killable_diff` (step of 35 points at one player; at the same morale the real gap is
     about 13: 64% / 50% / 37% won at morale -20..20).
  4. **Approved: force the direction (more enemy time down can only help); don't drop it.** Win model: `down_diff_s` direction forced (more enemy time down can only help) or dropped (backwards for 7 to 38 s;
     mirrors alive_diff).
  5. **Approved.** Win model: calibration by minute from held-out predictions (a readable lookup). At 6 to 12 min teams given 1% won
     4.7% and 99% won 94.9%; from 12 min 0.9% won 6.4%. Every win-point value and choice effect uses these numbers.
  6. **Approved.** Usual play: a choice is what the team did in its first seconds, not over the next 20 s (advancing over 20 s is
     partly the fight's result: held, advanced +5.5 and held, fell back -4.1, both clear).
  7. **Approved.** Power-play node: damage, pushing and control measured only up to the first kill (as the fight node does).
  8. **Approved.** Context-only variables (strength, build skill counts, flag lead, morale, minute) never priced as causes or offered as
     fixes (values.py prices strength_gap and the enemy's strip-skill count as causes now).
  9. **Approved.** Snapshot: winners-against-losers comparisons replaced by comparisons at the same win chance, or labelled.
  10. **Declined: links keep changing status batch by batch.** Learned links change status only after two batches in a row (stops near-line flips).
  11. **Approved (after an explanation).** Lord damage node: verdict rule fixed (typical error 125 against 92 for the median, still labelled "adds") and a
      form suited to its skew.
  12. **Approved.** Rework the three learned nodes still no better than the baseline (flag swing, capture speed, split effect).
  13. **Approved.** Kill-conversion node: attackers' Blind in seconds, like the new Blind measure.
  14. **Approved (after an explanation).** Forensics position judged on the last 5 s (TQ 1 fault).
  15. **Approved.** Values against matched moments without the event (same minute, same win chance).
  16. **Approved.** TQ what-ifs that aren't monotonic marked unreliable (TQ 4).
  17. **Approved.** TQ 4 text separates a wipe's NPC loss from a split's.
- Other batch 9 questions, Denning's answers:
  - BcS v Crew 15:11 (all five living BcS players went backside to convert with their pit empty and 3 dead): Denning
    doesn't know; let the data decide. Step 3 (discovery) and step 4 (chains priced from the node models) should
    measure going backside to convert against the alternatives in that state.
  - Crippled runners captured more (+16 points, even at the same point of the run): leave for now.
- Faults found in batch 9's TQs (not fixed yet):
  1. forensics.position uses the median over the whole window before a death, so a ranged spike that closes in for the
     last seconds reads "not in position" (TQ 1: Apes Necromancer at 1:54 in d9d75e55 shown 1,648 from the nearest
     enemy; the replay has Fun's Water and Air Eles at 701 and 739 for the last 4 s). Proposed fix: judge position on
     the last 5 s (as the healer distance already is), keep the window median as context; then rebuild
     `data/benchmarks/forensics.json`. Engine change (cache rebuilds): ask Denning first.
  2. TQ 1's chain stops at "already behind on flags at 4:15" although the swing began at 1:45 (chain.py's hand rules;
     step 4 replaces them).
  3. TQ 4's NPC-loss what-ifs aren't monotonic (two more defenders 74.0% to lose, one more 72.3%): the node read
     outside its data; show such readings as unreliable or cap them.
  4. TQ 4 says the split was answered on time while the first knight fell at 15:11 with 0 defenders (it was the wipe's
     conversion, not the split's); the text should separate the two losses.

## Start the next chat with
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/HANDOFF.md (the "Match replay
> analysis" section), knowledge/tactics.md and tools/replay_analysis/METHODS.md, then process the commentary transcripts
> I attach (Bounty's six matches, then Nick's one) following METHODS.md "Commentary and comms". Read
> knowledge/learned-model.md first for what the model has learned so far.

Engine setup in the chat (needed for step 2): `git fetch --depth 1 origin +replays:refs/remotes/origin/replays`,
`pip install --break-system-packages -r .github/workflows/train-requirements.txt`, then in tools/replay_analysis
`cache.py sync pull`, `cache.py warm`, `analyze.py --all --out /tmp/ga`, `library.py build`. Training batches run on
GitHub, not in the chat: the "Train batch" workflow (inputs pick, months, add_batch, note; about 11 minutes, 25 when the
engine changed), then pull main and read data/model/reports/latest.md. Python that runs the fits in parallel needs an
`if __name__ == "__main__":` guard in ad hoc scripts.

After each batch, answer the TQs (CLAUDE.md): flags, monk death, power play without a kill, NPCs lost; each with the
causal chain ("How it got there") and the fixes that mattered most, with a confidence level.

## Goal of the current build (agreed with Denning, 2026-11-07)
Make the causal map the model: every "this causes that" link is measured, learned and tested on unseen matches, so the
chains behind each result come from the data (including chains neither Denning nor Claude know), and every fix is
priced by carrying a change forward to the win chance. The causal chains must be reflected in the model, not only in
the TQ reasoning.

## Current state (commit 84b279c and later; 113 matches trained in 9 batches; 113 replays stored; match data to 2026-11-07)
- Win model: glass box log loss 0.367 against 0.412 for strength alone (ahead, not yet clear). Corrections: Lord damage
  curves capped at 5 points; healing-monk curves dropped (data/model_corrections.json).
- Node models (nodes.py): deaths, kill conversion, flag answer, NPC loss, Lord damage, Lord kill.
- Learned nodes (learnednodes.py, rows in lnrows.py; report section 6b; in words on knowledge/learned-model.md): run
  outcome, flag swing, run defence, capture speed, power play, fight outcome, split chance, split answer, split effect,
  collapse; data/model/nodes/L_<node>.json. Beat the simple baseline on unseen matches: run outcome, run defence, power
  play, fight outcome, split chance, split answer, collapse. Not yet: flag swing, capture speed, split effect.
- Causal map version 11: 61 nodes (new P.17 wrong casts, P.18 strips, P.19 Blind; P.5 covers hex removal), 241 links;
  203 hypotheses, 18 supported, 20 formulas; every link a learned node uses carries its measured strength
  ("measured"); link_log.json keeps every run's readings. Held for Denning: Blind on the enemy frontline -> fight
  outcome (data says rejected; he ruled "wait for more matches"). Supported by data include run timing -> run outcome
  and flag swing; numbers, enemy prots and healing -> power-play kills; strength, numbers, damage against the usual,
  spike timing -> fight outcome; scoreboard -> split chance; collapse timing (the five readings together; none clear
  alone yet) and split size -> collapse deaths. Pushing the runner: not clear yet over every run. Curious: a runner
  Crippled by a given point of the run is more often captured (+16 points), even read at the same point; worth a
  question for Denning. chain.py's chains are still hand-written rules (step 4 replaces them).
- Step 1 and 2a built: eventlayer.py (cached per match) with strips (judged against every enchantment in range),
  hex removals (against every hex in range; how long the removed hex was on), Blinds, hexes, peel, wrong casts, damage
  against the role's usual, spikes, runs (control and damage times), splits, power plays, captures. Values from data:
  data/benchmarks/eventlayer_values.json. Findings: data/model/reports/measures.md.
- Benchmarks to rebuild after new replays, in this order, and commit before a batch: `benchmarks.py spawns`, then
  `benchmarks.py carry`.
- Run time (rebuild of the 113 matches, session 4q): usual x64 machines vary by processor. The faster AMD EPYC 9V45
  took about 8 min for the report (about 11 min whole run, an estimate); the slower AMD EPYC 7763 took 16 min (20 min
  whole run). arm64 (ubuntu-24.04-arm, tested at Denning's request) was slowest: 23 min report, 27 min whole run (the
  older node models section took 10 min against 4.4), so keep "ubuntu-latest" (the workflow's "runner" input). Splitting
  the run into parallel jobs is the way to speed it up if Denning wants (step 2 below).

## Next steps (in order)
1. Commentary (new chat): Bounty's six matches, then Nick's one (Denning attaches the transcripts; METHODS.md
   "Commentary and comms"). The variables they suggest can become new links in the learned nodes (features in
   lnrows.py, groups in learnednodes.py SPEC), so step 3 tests them too.
2. Done (session 4r): Train batch split into parallel jobs. Next speed-up if wanted: prepare's per-match data.
3. Step 3: discovery: every measured variable tested against every node on unseen matches, in its own workflow split
   across several GitHub machines (Denning approved; public repo, no charge). Links it finds are held for Denning's
   approval, never added automatically.
4. Step 4: chains generated from the node models (replacing chain.py's rules; `learnednodes.whatif` reads a node with
   features changed) and fixes priced by carrying the change forward; the late split answer gets its value this way.
5. More batches of 20 to 30 matches from October and November; most links read "not clear yet" at 113 matches.
   Consider the larger pull (450+) now that step 2 is built (Denning to decide).

## Decisions made (session 4q)
Denning: the right strip target and the right hexes to remove are valued from data, not a list; steps 2a and 2b
first, then the transcripts (in a new chat). Data can't reject a link that came from Denning without his ruling
(held as `pending_rejection`; if he approves, `override_approved: true` and the link then follows the data both ways,
back to supported if more data says so). Rulings so far: Blind on the enemy frontline -> fight outcome: keep, wait for
more matches; defenders pushing the runner: Claude's measurement error (captures only), fixed with the run defence
node, not clear yet. Collapse = defenders collapsing on a split; collapse timing read five ways (his list approved:
arrival spread, numbers at contact, time from the split's first NPC hit, res timer, escape skills off recharge), the
data to pick. A plain-English page of the model, rebuilt each batch: knowledge/learned-model.md.

## Decisions made (session 4p)
Confirmed by Denning: Lord curves capped at 5 points; carrier ETA discounted by measured capture chance; healing-monk
curves dropped; a power play is any numbers advantage at main (an 8v7 while the enemy runs counts); chains go back to
the last reset or 3 minutes, follow the biggest few causes, and show fixes only where they mattered most; defensive
Mesmer play = interrupting offensive skills and casting on the enemy midline and frontline (offensive = interrupting
the enemy monks); frontline defensive peel = hitting or snaring enemies on its own backline; links found by discovery
are held for his approval; discovery split across several machines.

## Known issues and cautions
- Learned-node links near the line flip between runs (session 4q: split answer's free defenders and split effect's
  answer latency read supported with 4 bags, not clear yet with 2). Read "supported" by a small margin as a lead.
- Event-layer values use every trained match (not time ordered) and see output only (damage and healing): an
  enchantment or hex that works through energy, speed or armor shows only through what it does to output.
- The power-play node keeps the window's length (exposure): a longer power play has more time to kill.
- Defensive Blinds are rare before a fight's first death (45 in 113 matches overall), so P.19 has little data.
- run_bench's "escort 2+ with the main outnumbered" cell has only 6 runs; treat it as a lead, not a result.
- In the measures, Crippled runners capture more (runs that get far get Crippled): don't read it as Cripple helping.
- "Wasted" removal casts are higher for winners: probably pressure, not error; check before calling it a mistake.
- The model library's fits differ slightly between GitHub processor types; small report differences are noise.
- Data volume: with 113 matches most new links will read "not clear yet"; say so rather than over-reading.

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

---

*Background from earlier sessions (up to batch 5). Where it differs from the sections above, the sections above are current.*

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
- Session 4q: step 2a (eventlayer.py: strips against every enchantment in range, hex removals against every hex in
  range, damage against the role's usual; values from data with differences in differences) and step 2b
  (learnednodes.py and lnrows.py: nine learned nodes, each link's held-out strength written into causal_map.json and
  link_log.json; new map nodes P.17 to P.19; the map page shows the measurements). Fixed in the session: fights.py
  stores fights from the losing side (the fight node reads alternate sides); capture speed leaked its answer (seconds
  to the first push defaulted to the run's length; now read 10 s into the run). The learning report rebuilds
  measures.md and eventlayer_values.json; the workflow commits data/benchmarks.
- Session 4p (2026-11-07): batches 7 (30 matches) and 8 (22) from October and November; Train batch `months` input.
  Fixed: phantom flag swings (lone carrier read as a sure capture; carrier ETA now discounted by measured capture
  chance), flag spawns and stands per map (Imperial, Nomad's and Druid's had double-length flag runs), TQ 3 uptime, dead
  defenders listed as present at NPC kills, TQ 1 citing the wrong capture. Added: map geometry and per-map splits in the
  usual play, the causal chain (chain.py) in TQs 1, 2 and 4, the defensive-play measure, step 1 of the learned causal map
  (eventlayer.py, measures.md), TQ 3 for every power-play size. Corrections: Lord curves capped, healing-monk curves
  dropped. Model ahead of strength alone for the first time (0.367 against 0.412).
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
