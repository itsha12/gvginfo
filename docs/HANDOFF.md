# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, then this, then `docs/REDESIGN.md` (the
plan for the decision tier). History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md` (cite R-numbers); every fitted
model's structure: `knowledge/model.md` (generated).

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then set out the items under "Open for Denning" and carry on with "Next".
> (Add your rulings on the open items to the same message if you have them.)

## State (2026-11-13 afternoon: redesign step 2 on branch `bundle-4`, stage D under way; batch 17, 506 matches trained)
- Main's engine is unchanged (SPEC.md). Bundle 4 is on `bundle-4` and lands in one piece, then one rebuild (R-322).
  606 replays stored (90 from 2 September on not yet trained on). No Train batch, Discovery or fetch run in progress.
- On `bundle-4`: `hallmap.py`, `moments.py` (records, decision moments, shape, consequences), `jobs.py` (the plays
  and their jobs), `story.py`, `tools/golden/golden.py pick|score|stories|gate`, `lineup.py`, `thresholds.py`.
- Both gates pass (R-422: Crew v One 8:02 accepted; key v3): part one 12 of 12, part two 65 of 105 (61%). Line-up:
  building 422 of 426, held-out 186 of 186; comms 110 of 157 and 62 of 80. Golden stories draft 10.
- Stage D so far: `shape()` (2.8) and `consequence()` (2.9, at 90 and 180 s) on every moment; `runner_cost()`;
  `jobs.py` (2.11), built to his rulings R-423 to R-437: a call is an allocation of plays, each play one record with
  its job, its tests, its own clock (R-424) and what it cost beside it. Plays: flag (their run against ours, R-426),
  push flagger (R-427), flagger pushed, split (attacker by the answer met, defender, collapse, full collapse,
  part-run, race back; R-428 to R-430), numbers (strong and weak side, after a wipe; the runner-away ones merged into
  the flag decision, R-431), boost, pinned, base res, lord (from 23:30, R-435). `allocation()` adds `alloc` to every
  moment. Over 606 matches: 27,954 plays; job rates in CHANGELOG 2026-11-13 and from `jobs.py summary`.
- Run: `moments.py all <file>` (about 10 minutes, two jobs, the machine to itself), then `jobs.py summary <file>`.

## Next (in order; REDESIGN.md "Build plan from here" and "Tests")
1. His marks on the 35 review cases (below), then the fixes they call for, in `jobs.py` and the records.
2. Stage D, the rest: similar cases (2.10: same scenario first, then nearest on the state, with strength, R-432,
   and the hall's features, R-436); enemy execution (2.12); the interaction rule (2.13); NPC damage by class of bar
   (R-433); the four proposals left of R-324; the radius checks to the labelled zones. Gate and line-up after each.
3. Stage E (side by side for one rebuild, win points into the consequence record, SPEC.md and METHODS.md rewritten,
   readability test, his list of R-398, merge, Train batch with `add_batch=no`).
4. Proposal for the integrity layer: flag stretches where the replay has casts but no damage (7 of 606 replays).

## Open for Denning (set each out in the chat, R-329)
- The review (R-437): 35 cases, one a job, were put to him in the chat on 2026-11-13 with gvg.report links. For
  each: is the reading right, is the job right, is the test right. His marks become rulings and fixes.
- Known limits he was told of: a split attempt gets one job from its usual size and usual answer, so a long split
  whose answer changes is read crudely (cut it into phases); "shadow it with a snare" (gap 9) is not built; the
  two-monk spike build's death-penalty job after a wipe is not built (no build class yet); the Lord push's aim
  (Lord damage or killing the defenders) is read from where the pushers' hits went, a draft.
- Jobs still his to rule (marked `ruled: False`): numbers up or down from kills when the team pushes, falls back
  or holds; a split left with no answer.
- Thresholds that are Claude's drafts (`common.py`): ANSWER_CAP_S 15, COLLAPSE_VISIT_S 45 and COLLAPSE_MIN_S 8,
  PINNED_S 20, RACE_MIN_S 5, NUMBERS_TAIL_S 10, FLAG_JOB_MAX_S 180; "through their next cap" is read as their cap
  plus 20 s for the answer.
- Tests that tell little: in their base at the res (met 91%). Lord damage per push comes from gvg.report's damage
  events, which run 3 to 7% above its own match total; a per-time total from gvg.report would need a probe.
- From before: threat and the hand-off to hold (not records yet; the split stand-off stands in for a threat).

## Running it
- Train batch: `gh api -X POST repos/itsha12/gvginfo/actions/workflows/train-batch.yml/dispatches -f ref=main
  -f 'inputs[pick]=45' -f 'inputs[add_batch]=yes'` (rebuild only: `inputs[add_batch]=no`; TQs `inputs[tqs]=yes|no|auto`;
  blind round `inputs[blind]=no|yes|auto`, default no while rounds are paused). Never queue two runs at once.
- Maps: `tools/maps/build_maps.py`, `audit_labels.py [--routes]`; branch: `hallmap.py numbers|routes|reach`, `moments.py flags`.
- Local engine: `git fetch --depth 1 origin +replays:refs/remotes/origin/replays`; `pip install
  --break-system-packages -r .github/workflows/train-requirements.txt`. The records, the story, the line-up, the gate
  and the thresholds need no cache (`cache.py sync pull`, `warm` only for the fitted models). `PYTHONDONTWRITEBYTECODE=1`.
- `thresholds.py run` takes about 15 minutes with two jobs and the machine to itself; run old and new one after the other.

## Cautions
- Never print or decode a sealed field (blind picks, golden moments) in a chat.
- Don't merge `bundle-4` piecemeal (R-322). Label and golden files are saved whole by the site: after a change
  here, Denning reloads the page first. Hall labels are saved to main: copy changed `data/maps/labels/*.json` to the
  branch before reading a hall (all 14 matched main on 2026-11-12).
- Transcripts never go in the repo: paraphrased statements only. Party slots are in `data/matches/`, not the replays.
- `golden_moments.json` on the branch is a copy of main's; refresh it from main before the gate.
