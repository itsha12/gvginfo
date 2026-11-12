# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, then this, then `docs/REDESIGN.md` (the
plan for the decision tier). History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md` (cite R-numbers); every fitted
model's structure: `knowledge/model.md` (generated).

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then set out the items under "Open for Denning" and carry on with "Next".

## State (2026-11-12: redesign step 2 on branch `bundle-4`, last engine commit 02a4106; batch 17, 506 matches trained)
- Main's engine is unchanged (as SPEC.md describes). Bundle 4 is built on `bundle-4` and lands in one piece, then
  one rebuild (R-322). 606 replays stored (90 random ones from 2 September on are not yet trained on). No Train
  batch, Discovery or fetch run in progress.
- On `bundle-4`: `hallmap.py` (zones, walked distance, reach, places in his words), `moments.py` (the records),
  `story.py` (prints from the records, R-362), `tools/golden/golden.py pick|score|stories` (never reads the sealed
  field), `lineup.py score|lines` (the line-up), `thresholds.py run|show` (all-match counts, about 15 minutes).
- The records in `moments.py`, reading step 1: `attempts()`, `caught()`, `flags_record()`, `main_team()`, `lane()`,
  `moves()`, `split_fights()`, `ground()`, `undefended()`, `on_pit()`, `fights(t)`, `place_at`.
- Reading step 2 is built and ruled on (R-399 to R-412): `flag_pushes()` (players on a flagger who is on his own);
  a main team push keeps `onto_flag` (R-401); `flags_record()` keeps the flag route, the way back, the hold before a
  cap and its distance from the enemy's boost; `flag_lead()`, `lead_value()` and `lead_at()` read the flag tally
  (R-408: 1 for the stand, plus the share of the next flag run done, plus up to half for the following runner back
  at the spawn; bands at 0.35, 0.8, 1.3, 1.7); `pregame()`; `standoffs()` (R-405, R-411, R-413: the main teams standing
  off, 0.4 hits a player in 10 s for 35 s; it replaced `posture()`; a stand-off is not told as a fight); `timing()`
  (R-377's four; a flag held back 45 s around the stand, R-407; a flag left at the spawn, both only while the enemy
  holds the stand); `monk_counts()`; `on_lord()`. `story.py` prints each from its record.
- Thresholds: confirmed (R-404), the delayed pickup at 10 s (R-406); those the later rulings added are Claude's.
  `thresholds.py sweep NAME values [--data <main>/data/lineup]` shows what a looser or tighter value does to the
  records and to the building games (common.py `GVG_TRY`; never set it in a training run).
- Faults fixed: a flag dropped at the spawn and retaken was read as returned (captures 5,245 to 5,249); `story.py`
  stopped on 8 of 606 matches. Every count of reading step 1 is unchanged.
- On main: `data/lineup/` (16 transcripts as paraphrased statements: 12 for building, 4 held out in `held/`),
  Model > Golden moments (15 games, R-382; `golden_stories.json` draft 6), rulings to R-414.

## The line-up (R-368 to R-397), the measure of the reading stage
- `lineup.py score --data <main>/data/lineup [--held] [--show]` with `LINEUP_CACHE` set (delete it after an engine
  change). The gate is 90% agreement on things seen happening in the four held-out games (R-380, R-383).
- The seven kinds of reading step 2 are checked. Posture and timing statements that are not a true stand-off or a
  deliberate hold are set aside (R-414: 7 building, 15 held out). Seen events: building 422 of 426 (99%), held-out
  163 of 196 (83%). Comms calls: 108 of 157, 61 of 80. Stand-offs: 146 over 606 matches (0.24 a match).
- Held-out misses (33 seen, 19 calls): push 6, answer 5, join 5, fall 4, fight 4, others three or fewer. None read.
- Reading step 3 so far: `golden_stories.json` is draft 6; the blind check against his 13 notes covered the opening
  and the last two to three minutes before each moment (fixed: a hand-off under a push told as a dropped flag).

## Next (in order; the full build plan and both gates are in REDESIGN.md "Build plan from here" and "Tests")
1. His one review of the held-out misses at the gate (`lineup.py score --held --show --gate`, R-396), once he says
   to open it: the review can be done only once.
2. After it: only the engine's own misses count; fix them, rescore, `thresholds.py` beside it.
3. His approval of the story's form on golden game 1 only (R-395); rebuild the decision moments (triggers,
   scenarios, calls) on the records (R-351); the decision gate (R-394).
4. Stage D on the branch (consequence record, similar cases, the job table, enemy execution, the four proposals left
   of R-324, radius checks to `st.zone`), then stage E (side by side for one rebuild, SPEC.md and METHODS.md
   rewritten, readability test, his list of R-398, merge, Train batch with `add_batch=no`).

## Open for Denning (set each out in the chat, R-329)
- Whether to open the gate review now (33 seen misses, 83% against 90%), or have the blind check's gaps fixed first.
- Gaps the blind check showed: a three-a-side split posturing at a back door is told as a 3 v 3 fight (NwAy v SKT
  12:32 and 14:35; R-411 covers main teams only); a runner pushed while the fight converges on him, three or more
  team mates near, is not a push on the flagger (hdm v HC 2:50); time to cap once at the fight (Crew v hdm 3:50).
- Stage D: the consequence record sets flags given up beside numbers gained (R-412); 0.8 of a player to be measured.
- From before: comms pass rate (R-394); game 1's story form (R-395); threat, hand-off to hold, 983a47db.

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
