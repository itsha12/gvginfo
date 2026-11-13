# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, then this, then `docs/REDESIGN.md` (the
plan for the decision tier). History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md` (cite R-numbers); every fitted
model's structure: `knowledge/model.md` (generated).

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then set out the items under "Open for Denning" and carry on with "Next".
> (Add your rulings on the open items to the same message if you have them.)

## State (2026-11-13: redesign step 2 on branch `bundle-4`, stage D under way; batch 17, 506 matches trained)
- Main's engine is unchanged (SPEC.md). Bundle 4 is on `bundle-4` and lands in one piece, then one rebuild (R-322).
  606 replays stored (90 from 2 September on not yet trained on). No Train batch, Discovery or fetch run in progress.
- On `bundle-4`: `hallmap.py`, `moments.py` (the records, the decision moments, and now the shape of the call and
  what followed), `story.py`, `tools/golden/golden.py pick|score|stories|gate`, `lineup.py score|lines`,
  `thresholds.py run|show|sweep`.
- The reading (stage R) and the decision moments (stages B and C) are done: both gates passed. The decision gate
  after R-422 (Crew v One 8:02 accepted; `accepted_parts` in the key, v3): part one 12 of 12 found, every part
  passes; part two 65 of 105 comms calls read the same (61%; his mark 60%). Line-up: building 422 of 426, held-out
  186 of 186; comms 110 of 157 and 62 of 80. Golden stories draft 10.
- Stage D so far (`moments.py`; every moment of `records()` carries both):
  - `shape()` (2.8, R-297): who (the players the call was read from, as properties: monks, heals, prots,
    self-defence, snare and speed power, escapes; `_props`), which way (drawn flag run and door; the door a defender
    came home by, `_came_by`; the door or ground of a push or a fall back), when (seconds to the first move; a delay
    past ON_TIME_S is a decision when `gained_elsewhere()` finds something, R-321, else execution).
  - `consequence()` (2.9, R-294, R-412) at 90 and 180 s (`CONSEQ_S`): deaths, NPCs by kind, Guild Lord health, caps,
    boosts, morale, flag lead then and now, the stand, the numbers meanwhile (main team's fight and the other
    fights, in seconds and player-seconds; seconds with a player away for the flag; all from `_tl()`), ladder step.
  - `runner_cost()`, `flag_duty()`: what a flag run costs in players at the main fight (the numbers are under
    "Open for Denning").
  - `JOBS`, `JOB_TESTS`, `job_of()`: the job table as drafted (2.11, R-298). Used by nothing until he rules.
  - `moments.py all <file>` (about 20 minutes, two jobs), then `moments.py counts|after|runner|jobs <file>`.
- A moment's state now carries the flag lead (`flag_lead` in flags, `lead_band`); before, it was None on every moment.

## Next (in order; REDESIGN.md "Build plan from here" and "Tests")
1. Stage D, the rest, on the branch: similar cases (2.10: same scenario first, then nearest on the state, the count
   set by the scenario's size); the job table as he rules it, each job then tested on held-out matches; enemy
   execution against the same role benchmarks (2.12, R-299); the interaction rule (2.13); NPC damage as a
   composition property (measured per bar); the four proposals left of R-324 (control by distance to the stand, hex
   value with trigger damage, NPC healing by target and kind, teleporter hops); the radius checks to the labelled
   zones (PIT_R, BASE_R, STAND_R in episodes, fights, scoreboard, lnrows). Rerun the gate and the line-up after each.
2. Stage E (side by side for one rebuild, win points into the consequence record, SPEC.md and METHODS.md rewritten,
   readability test, his list of R-398, merge, Train batch with `add_batch=no`).
3. Proposal for the integrity layer (in the bundle): flag stretches where the replay has casts but no damage (game 1
   6:10 to 8:30; 7 of 606 replays have two or more whole minutes), so no fight is read there.

## Open for Denning (set each out in the chat, R-329; all three were put to him on 2026-11-13)
- The runner's cost (R-412: "roughly 0.8 of a player down, to be measured"). Measured three ways, none 0.8: over a
  flag from the runner leaving to its end, a carrier is missing from his main team's fight 0.56 of the fought
  seconds (single run; 0.56 with the fight around the stand, 0.36 on his own ground, 0.71 on the enemy's; 0.76 on a
  half double run); R-360's seconds away are 41 of 64 on a captured flag; over a whole match 0.22 of a player is away
  for the flag. Which reading does he mean, and should the record use the measured figure?
- The job table (R-298): 18 drafted jobs with tests on the 90 s record (`moments.py jobs`: met 24% to 76%). He rules
  each job and its test; whether a job differs by scenario; whether 90 s or the base res is the right clock.
- Whether the consequence readings make sense (`moments.py after`): the first unadjusted reading of R-412's trade is
  in CHANGELOG 2026-11-13.
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
