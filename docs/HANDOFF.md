# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, then this, then `docs/REDESIGN.md` (the
plan for the decision tier). History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md` (cite R-numbers); every fitted
model's structure: `knowledge/model.md` (generated).

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next" item 1 and set out the items under "Open for Denning".

## State (2026-11-12: redesign step 2 on branch `bundle-4`, last engine commit 6b8b5db; batch 17, 506 matches trained)
- Main's engine is unchanged (as SPEC.md describes). Bundle 4 is built on `bundle-4` and lands in one piece, then
  one rebuild (R-322). 606 replays stored (90 random ones from 2 September on are not yet trained on). No Train
  batch, Discovery or fetch run in progress.
- On `bundle-4`: `hallmap.py` (zones, walked distance, reach, places in his words), `moments.py` (the records),
  `story.py` (prints from the records, R-362), `tools/golden/golden.py pick|score|stories` (never reads the sealed
  field), `lineup.py score|lines` (the line-up), `thresholds.py run|show` (all-match counts, about 15 minutes).
- The records in `moments.py`, reading step 1: `attempts()`, `caught()`, `flags_record()`, `main_team()`, `lane()`,
  `moves()`, `split_fights()`, `ground()`, `undefended()`, `on_pit()`, `fights(t)`, `place_at`.
- Reading step 2 is built and ruled on (R-399 to R-407): `flag_pushes()` (players on a flagger who is on his own);
  a main team push keeps `onto_flag` (R-401); `flags_record()` keeps the flag route, the way back, the hold before a
  cap and its distance from the enemy's boost; `flag_lead()` and `lead_at()` (R-402 as first built: how much of its
  run each next flag has done; under review, see Open); `pregame()`; `standoffs()` (R-405: the disengage; it replaced
  `posture()`: two groups standing together with little or no damage traded are not told as a fight); `timing()`
  (R-377's four, a flag held back 45 s around the stand while the enemy holds it, R-407, and a flag left at the
  spawn); `monk_counts()`; `on_lord()`. `story.py` prints each from its record.
- Thresholds: confirmed (R-404), the delayed pickup at 10 s (R-406); those the later rulings added are Claude's.
  `thresholds.py sweep NAME values [--data <main>/data/lineup]` shows what a looser or tighter value does to the
  records and to the building games (common.py `GVG_TRY`; never set it in a training run).
- Faults fixed: a flag dropped at the spawn and retaken was read as returned (captures 5,245 to 5,249); `story.py`
  stopped on 8 of 606 matches. Every count of reading step 1 is unchanged.
- On main: `data/lineup/` (16 transcripts as paraphrased statements: 12 for building, 4 held out in `held/`),
  Model > Golden moments (15 games, R-382; `golden_stories.json` still draft 5), rulings to R-407.

## The line-up (R-368 to R-397), the measure of the reading stage
- `lineup.py score --data <main>/data/lineup [--held] [--show]` with `LINEUP_CACHE` set (delete it after an engine
  change). The gate is 90% agreement on things seen happening in the four held-out games (R-380, R-383).
- The seven kinds of reading step 2 are checked, not set aside. Seen events: building 423 of 433 (98%), held-out
  166 of 208 (80%). Comms calls: 107 of 157, 62 of 83. Statements checked before: unchanged (365 of 365; 136 of 162).
- By word (building; held out, with calls): lead 13 of 14; 6 of 6. Pushflag 12 of 16; 7 of 10. Route 8 of 10; 6 of
  7. Monks 10 of 11; 5 of 6. Lord 9 of 11; 5 of 7. Posture (against stand-offs) 5 of 6; 3 of 7. Timing 3 of 5; 1 of 10.
- Timing is the weak word: the held flag of R-407 (121 over 606 matches) no longer covers his two building remarks
  about a flag kept back in base or not yet run. Stand-offs: 3,855 (6.4 a match). No held-out line was read.

## Next (in order; the full build plan and both gates are in REDESIGN.md "Build plan from here" and "Tests")
1. Flag lead once Denning rules on the tally (Open, first item): rebuild `_lead_values`, the story lines and the
   line-up's lead check on it; `thresholds.py` beside the rescore.
2. Reading step 3: regenerate the golden stories (`golden.py stories`, draft 6), the blind check against his 13 blind
   notes, rescore the line-up, then his review of the held-out misses at the gate (R-396).
3. His approval of the story's form on golden game 1 only (R-395); rebuild the decision moments (triggers,
   scenarios, calls) on the records (R-351); the decision gate (R-394).
4. Stage D on the branch (consequence record, similar cases, the job table, enemy execution, the four proposals left
   of R-324, radius checks to `st.zone`), then stage E (side by side for one rebuild, SPEC.md and METHODS.md
   rewritten, readability test, his list of R-398, merge, Train batch with `add_batch=no`).

## Open for Denning (set each out in the chat, R-329)
- Flag lead as a tally (proposed 2026-11-12, he asked for it to be thought through): each team's tally is 1 for the
  stand plus the share of its next flag run done (plus up to half for the following runner already back at the
  spawn); the lead is the difference. It reads his nine building statements as he said them (full = about 1.0,
  half = about 0.4; R-402's backup with nothing coming = 2). Needs his ruling and the names of the bands.
- A flag left at the spawn (1.8 a match at 45 s): keep or tighten. The two accepted hdm v HC statements (R-403): `ok.` or misses.
- From before: comms pass rate (R-394); game 1's story form (R-395); threat, hand-off to hold, time to cap, 983a47db.

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
