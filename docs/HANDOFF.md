# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, then this, then `docs/REDESIGN.md` (the
plan for the decision tier). History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md` (cite R-numbers); every fitted
model's structure: `knowledge/model.md` (generated).

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then set out the items under "Open for Denning" and carry on with "Next".

## State (2026-11-12: redesign step 2 on branch `bundle-4`, last engine commit 138f2e7; batch 17, 506 matches trained)
- Main's engine is unchanged (SPEC.md). Bundle 4 is on `bundle-4` and lands in one piece, then one rebuild (R-322).
  606 replays stored (90 from 2 September on not yet trained on). No Train batch, Discovery or fetch run in progress.
- On `bundle-4`: `hallmap.py` (zones, walked distance, reach, places in his words), `moments.py` (the records),
  `story.py` (prints from the records, R-362), `tools/golden/golden.py pick|score|stories` (never reads the sealed
  field), `lineup.py score|lines` (the line-up), `thresholds.py run|show` (all-match counts, about 15 minutes).
- The records in `moments.py`, reading step 1: `attempts()`, `caught()`, `flags_record()`, `main_team()`, `lane()`,
  `moves()`, `split_fights()`, `ground()`, `undefended()`, `on_pit()`, `fights(t)`, `place_at`.
- Reading step 2 (R-399 to R-415): `flag_pushes()`; `onto_flag` on a main team push (R-401); the flag route, way
  back, hold and boost distance in `flags_record()`; `flag_lead()`, `lead_value()`, `lead_at()` (the flag tally,
  R-408; bands at 0.35, 0.8, 1.3, 1.7); `pregame()`; `standoffs()` (R-411, R-413: main teams, 0.4 hits a player in
  10 s for 35 s; split groups standing apart and still for 25 s, R-415; a stand-off is not told as a fight);
  `timing()` (R-377's four, a flag held back, R-407, a flag left at the spawn); `monk_counts()`; `on_lord()`.
- Thresholds: confirmed (R-404, R-406); those the later rulings added are Claude's. `thresholds.py sweep NAME
  values [--data <main>/data/lineup]` tries a looser or tighter value (`GVG_TRY`; never in a training run).
- Built from the gate review (R-417): `way_out()` (a team going out of its base by a door); a split told by who
  set out together, falling back to its own ground, answered by a main team that goes home, with swaps in the
  answer; a drop told where it lay; the Guild Lord damage so far in the state line.
- Faults fixed (R-417): door routes were cut at the first cell off the walkable ground (13 doors on seven halls:
  his Weeping Stone question); a repeated pickup lost the carry before it; a capture with no player after a drop
  on the stand was lost; the flag route read past the arrival at the stand; a team that left by the res read as
  caught. Captures 5,249 to 5,257; every other count of the reading moved by under 2%.
- On main: `data/lineup/` (16 transcripts as paraphrased statements; the four in `held/` are spent, R-417),
  Model > Golden moments (15 games; `golden_stories.json` draft 7), rulings to R-417.

## The line-up (R-368 to R-397), the measure of the reading stage
- `lineup.py score --data <main>/data/lineup [--held] [--show]` with `LINEUP_CACHE` set (delete it after an engine
  change). Posture and timing statements that are not a true stand-off or a deliberate hold are set aside (R-414).
- **The reading gate is passed (R-416).** His one review of the 33 held-out misses: 7 confirmed, 8 withdrawn, 18
  stand with his corrections. The engine as it stood at the review (5f43768) agrees with 171 of 188 things seen
  (91%; the gate is 90%, R-380, R-383). After the fixes of R-417: held-out 185 of 188, building 422 of 426; comms
  calls 62 of 80 and 109 of 157. The 185 is not a clean check: the fixes were made knowing those lines.
- The three held-out misses left: BcS v hook 6:52 (he says not a push, BcS's four at the stand; the engine has three
  there and the Dervish ahead), BcS v hook 8:21 (he has BcS's split running to hook's back door; the replay has it
  1,200 out of its own back door and back by 8:40), RACK v chic 0:29 (the flagger pushed as he reaches his team).
- Reading step 3 done: `golden_stories.json` draft 7; blind check rerun on the changed lines.

## Next (in order; the full build plan and both gates are in REDESIGN.md "Build plan from here" and "Tests")
1. His rulings on the three items under "Open for Denning" that came out of the gate review.
2. No fresh held-out check is required by R-396 (the gate passed); two new timestamped games would give one.
3. His approval of the story's form on golden game 1 only (R-395); rebuild the decision moments (triggers,
   scenarios, calls) on the records (R-351); the decision gate (R-394).
4. Stage D on the branch (consequence record, similar cases, the job table, enemy execution, the four proposals left
   of R-324, radius checks to `st.zone`), then stage E (side by side for one rebuild, SPEC.md and METHODS.md
   rewritten, readability test, his list of R-398, merge, Train batch with `add_batch=no`).

## Open for Denning (set each out in the chat, R-329)
- A runner pushed as the fight converges on him: RACK v chic 0:29 (on his own 4 s, the hit lands as he reaches
  his team) and hdm v HC 2:50. Options: count a push of 4 s when a hit or skill lands; or leave it out. Time to cap.
- BcS v hook 6:52 (withdraw as a push?) and 8:21 (does the tape show the split reaching hook's back door?).
- WAY_OUT_GAP_S (10 s) and the 3 s that make a hand-off a drop are Claude's; 2.7 door lines a match: keep them?
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
- Never print or decode a sealed field (blind picks, golden moments) in a chat.
- Don't merge `bundle-4` piecemeal (R-322). Label and golden files are saved whole by the site: after a change
  here, Denning reloads the page first. Hall labels are saved to main: copy changed `data/maps/labels/*.json` to the
  branch before reading a hall (all 14 matched main on 2026-11-12).
- Transcripts never go in the repo: paraphrased statements only. Party slots are in `data/matches/`, not the replays.
