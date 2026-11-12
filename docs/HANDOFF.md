# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, then this, then `docs/REDESIGN.md` (the
plan for the decision tier). History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md` (cite R-numbers); every fitted
model's structure: `knowledge/model.md` (generated).

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then set out the items under "Open for Denning" for me to rule on.

## State (2026-11-12: redesign step 2 on branch `bundle-4`, last engine commit d59ea1a; batch 17, 506 matches trained)
- Main's engine is unchanged (as SPEC.md describes). Bundle 4 is built on `bundle-4` and lands in one piece, then
  one rebuild (R-322). 606 replays stored (90 random ones from 2 September on are not yet trained on). No Train
  batch, Discovery or fetch run in progress.
- On `bundle-4`: `hallmap.py` (zones, walked distance, reach, places in his words), `moments.py` (the records),
  `story.py` (prints from the records, R-362), `tools/golden/golden.py pick|score|stories` (never reads the sealed
  field), `lineup.py score|lines` (the line-up), `thresholds.py run|show` (all-match counts, about 15 minutes).
- The records in `moments.py`, reading step 1: `attempts()`, `caught()`, `flags_record()`, `main_team()`, `lane()`,
  `moves()`, `split_fights()`, `ground()`, `undefended()`, `on_pit()`, `fights(t)`, `place_at`.
- Reading step 2, built this session (the words of R-373, R-375 to R-378): `flag_pushes()` (players on a flagger
  who is on his own: carrying, going back or at his spawn; who came to help; died, dropped, the pickup delayed);
  `flags_record()` now keeps the flag route (short way, long way on the four halls with two drawn flag runs a side;
  the own back door elsewhere), the way back, the hold in the stand area before a cap and its distance from the
  enemy's boost; `flag_lead()` and `lead_at()` (a full flag, half a flag, R-375); `pregame()`; `posture()` (R-376);
  `timing()` (the four choices of R-377); `monk_counts()` (the main team's fight, four or more of the team in it);
  `on_lord()`; every fight carries its monks a side. `story.py` prints each from its record (`_word_events`).
- Two faults fixed on the way: a flag dropped at the spawn and taken again by the same player was read as returned
  (captures 5,245 to 5,249); `story.py` stopped on 8 of 606 matches. Every other all-match count is unchanged.
- On main: `data/lineup/` (16 transcripts as paraphrased statements: 12 for building, 4 held out in `held/`),
  Model > Golden moments (15 games, R-382; `golden_stories.json` still draft 5), rulings to R-398.

## The line-up (R-368 to R-397), the measure of the reading stage
- `lineup.py score --data <main>/data/lineup [--held] [--show]` with `LINEUP_CACHE` set (delete it after an engine
  change). The gate is 90% agreement on things seen happening in the four held-out games (R-380, R-383).
- The seven kinds of reading step 2 (pushflag, route, lead, posture, timing, monks, lord) are now checked, not set
  aside. Seen events: building 419 of 434 (97%), held-out 164 of 208 (79%). Comms calls: 106 of 157, 60 of 83.
- The statements checked before are unchanged: 365 of 365 and 136 of 162. Of the newly checked: building 54 of 69,
  held-out 28 of 46 (lead 6 of 6, pushflag 7 of 10, route 6 of 7, monks 5 of 6, lord 5 of 7, posture 0 of 7,
  timing 0 of 10; kinds counted with their calls).
- The new checks: pushflag, posture and lord against the record's stretch overlapping the window; lead against the
  level the statement's words ask for (full, half, else the stand held); monks against the team's biggest fight;
  timing by the statement's words. The building games' 15 misses: `--show`. No held-out line was read.

## Next (in order; the full build plan and both gates are in REDESIGN.md "Build plan from here" and "Tests")
1. Denning's rulings on "Open for Denning" below; then the changes they ask for, with `thresholds.py` beside the rescore.
2. Reading step 3: regenerate the golden stories (`golden.py stories`, draft 6), the blind check against his 13 blind
   notes, rescore the line-up, then his review of the held-out misses at the gate (R-396).
3. His approval of the story's form on golden game 1 only (R-395); rebuild the decision moments (triggers,
   scenarios, calls) on the records (R-351); the decision gate (R-394).
4. Stage D on the branch (consequence record, similar cases, the job table, enemy execution, the four proposals left
   of R-324, radius checks to `st.zone`), then stage E (side by side for one rebuild, SPEC.md and METHODS.md
   rewritten, readability test, his list of R-398, merge, Train batch with `add_batch=no`).

## Open for Denning (set each out in the chat, R-329)
- The 22 draft thresholds of reading step 2 in `common.py` (PUSHFLAG_R to LORD_GAP_S), with their all-match counts.
- Pushing a flag that is held inside its team (a main team walking its fight onto the enemy's flag): the engine
  tells it as a fight there, not a push on the flagger (xxx v ohno 1:08, and the calls at 5:26 and 19:20).
- Posture (R-376) on a team's own side, and posture while light damage is traded: four of six building statements.
- Timing beyond the four of R-377 (not running a flag yet; keeping it in hand). Half a flag (R-375) is read as
  "picked up before the enemy's", so it stays once the enemy picks up later.
- hdm v HC 20:00 (long way then short way; read as the short way), 22:20 (a runner killed before his pickup).
- From before: the comms calls' pass rate in the decision gate (R-394); game 1's story form (R-395); threat,
  hand-off to hold, time to cap, monk energy only if needed (R-353), discovery second run, behaviour clusters, 983a47db.

## Running it
- Train batch: `gh api -X POST repos/itsha12/gvginfo/actions/workflows/train-batch.yml/dispatches -f ref=main
  -f 'inputs[pick]=45' -f 'inputs[add_batch]=yes'` (rebuild only: `inputs[add_batch]=no`; TQs `inputs[tqs]=yes|no|auto`;
  blind round `inputs[blind]=no|yes|auto`, default no while rounds are paused). Never queue two runs at once.
- Maps: `tools/maps/build_maps.py`, `audit_labels.py [--routes]`; branch: `hallmap.py numbers|routes|reach`, `moments.py flags`.
- Local engine: `git fetch --depth 1 origin +replays:refs/remotes/origin/replays`; `pip install
  --break-system-packages -r .github/workflows/train-requirements.txt`. The records, the story, the line-up and the
  thresholds need no cache (`cache.py sync pull`, `warm` only for the fitted models). `PYTHONDONTWRITEBYTECODE=1`.

## Cautions
- Never print or decode a sealed field (blind picks, golden moments) in a chat. The held-out games are scored as
  counts only until his one review (`--held --show --gate`, R-370, R-396).
- Don't merge `bundle-4` piecemeal (R-322). Label and golden files are saved whole by the site: after a change
  here, Denning reloads the page first. Hall labels are saved to main: copy changed `data/maps/labels/*.json` to the
  branch before reading a hall (all 14 matched main on 2026-11-12).
- Transcripts never go in the repo: paraphrased statements only. Party slots are in `data/matches/`, not the replays.
