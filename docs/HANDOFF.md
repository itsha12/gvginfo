# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, then this, then `docs/REDESIGN.md` (the
plan for the decision tier). History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md` (cite R-numbers); every fitted
model's structure: `knowledge/model.md` (generated).

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then set out the items under "Open for Denning" and carry on with "Next".
> (Add your rulings on the open items to the same message if you have them.)

## State (2026-11-13 evening: redesign step 2 on branch `bundle-4`, stage D under way; batch 17, 506 matches trained)
- Main's engine is unchanged (SPEC.md). Bundle 4 is on `bundle-4` and lands in one piece, then one rebuild (R-322).
  606 replays stored (90 from 2 September on not yet trained on). No Train batch, Discovery or fetch run in progress.
- On `bundle-4`: `hallmap.py`, `moments.py` (records, decision moments, shape, consequences), `jobs.py` (the plays
  and their jobs), `story.py`, `tools/golden/golden.py pick|score|stories|gate`, `lineup.py`, `thresholds.py`.
- Both gates pass (key v3): part one 12 of 12, part two 65 of 105 (61%). Line-up: building 422 of 426, held-out 186
  of 186; comms 110 of 157 and 62 of 80. Golden stories draft 10 (unchanged by this session).
- Stage D so far: `shape()` (2.8), `consequence()` (2.9), and `jobs.py` (2.11) to his rulings R-423 to R-449: a
  call is an allocation of plays, each one record with its job, tests, its own clock and what it cost beside it.
  Plays: flag (their run against ours), push flagger, flagger pushed, split, numbers, boost, pinned, base res, lord.
- A split is read phase by phase (`split_plays`): who is on the enemy's ground and who defends, each counted after
  12 s there (R-350), teleporter hops left out; from the first second it reaches a defender, footies, base or pit
  (R-440); followed past the record's end and while chased out; a collapse needs the defence one up, from the main
  fight, for 45 s or less (R-441); pit NPCs for the defence, any NPC for the split (R-443); damage and monks of
  the split, the defence and both main fights kept beside every phase (R-444).
- Shadow of Haste runs are marked (`soh`), out of `data/benchmarks/flag_arrival.json` and set aside in the flag
  counts (R-438). Over 606 matches: 39,399 plays, 32,074 moments; rates from `jobs.py summary <file>`.
- Run: `moments.py all <file>` (about 10 minutes, two jobs, the machine to itself), then `jobs.py summary <file>`.

## Next (in order; REDESIGN.md "Build plan from here" and "Tests")
1. His answers to the questions below, and his marks on rows 4 to 12 and the replacement rows; then a second
   review set drawn from the rebuilt plays (no Shadow of Haste runs), since most split rows changed.
2. R-449: count a player in a fight's numbers only after 12 s in it (`_numbers`); it moves the numbers moments, so
   rerun the gate, the line-up and `thresholds.py` with it. R-440: move the split and flag moments later.
3. Stage D, the rest: similar cases (2.10, with strength, R-432, and the hall, R-436); enemy execution (2.12); the
   interaction rule (2.13); NPC damage by class of bar (R-433); the four proposals left of R-324; radius checks.
4. Stage E (side by side for one rebuild, win points, SPEC.md and METHODS.md, readability, R-398, merge).

## Open for Denning (set each out in the chat, R-329; all put to him 2026-11-13 evening)
- Damage against monks (R-444): is "expected to kill at twice the monks facing it" right, and does the main team
  get the kill job whenever the defence puts more monks on the split than the split brought? Who counts as a monk
  (today: backline monks; a smiter and a ritualist healer count as damage)?
- Shadow of Haste runs: leave them out of every flag count, and of the flag lead? When was the mechanic removed?
- When is the moment (R-440)? A split is named at the leave, a median of 34 s before it reaches a defender or the
  base (a tenth over 91 s). Options: when it crosses onto the enemy's side, or when it reaches.
- Full collapse is now read 507 times (six or more defenders on the split for 12 s): too many? It may be a split
  standing beside the enemy's main team.
- Still drafts: numbers from kills (push, fall back, hold); a split with no answer; the thresholds marked
  "Claude's draft" in `common.py`; the Lord push's aim; "in their base at the res" (met 91%, tells little).
- Not built: shadow with a snare; the two-monk spike build after a wipe; the race back (taken out, R-448).

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
