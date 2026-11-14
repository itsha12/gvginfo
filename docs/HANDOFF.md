# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then set out the items under "Open for Denning" and carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)
> (Add your answers to the open items, by their numbers, to the same message if you have them.)

## State (2026-11-13 night: redesign step 2 on branch `bundle-4`, stage D under way; batch 17, 506 matches trained)
- Main's engine is unchanged (SPEC.md). Bundle 4 is on `bundle-4` and lands in one piece, then one rebuild (R-322).
  606 replays stored (90 from 2 September on not yet trained on). No Train batch, Discovery or fetch run in progress.
  Both branches pushed; nothing uncommitted.
- On `bundle-4`: `hallmap.py`, `moments.py` (records, decision moments, shape, consequences), `jobs.py` (the plays
  and their jobs, R-423 to R-449), `story.py`, `tools/golden/golden.py`, `lineup.py`, `thresholds.py`, `review.py`.
- Built from his answers (R-455 to R-463): the ratios of damage against monks and the main fight's kill job
  (`can_kill`; a side facing no monk always has it); Shadow of Haste by date; a split's moment at the crossing; a flag
  run's moment by hall (`moment` in `run_starts()`); 12 s for main-fight numbers from arrival; `blanks` (R-460).
  Not built: R-464 (joining and leaving from movement; a defender on a split player who dies).
- He redrew the Greater stand area on Meditation, Corrupted and Weeping Stone (copied to the branch). Gates pass
  (part one 12 of 12, part two 65 of 105); line-up 422 of 426 and 186 of 186, comms 109 of 157 and 62 of 80.
  `thresholds.py` not rerun since: do it before the next change to a record.
- The whole-game review is on the site (Model > Game review; rows `data/model/game_reviews.json`, his marks
  `data/model/game_review_marks.json`). He marked part 1 on 2026-11-13 (TFS v 옷옷옷옷 bdaa145f, Men v Apes 149fbdc6;
  engine af952c6); every mark is in the review key as set w1p1 (85 situations, their calls, two `missed` rows; no
  checks written yet). Situations right: 45 of 85. Pinned 9 of 9, boost 4 of 5, flag 8 of 15, numbers 9 of 19,
  split 11 of 31. Calls right where the situation was right: 62 of 68: the jobs hold, the situations do not.
- What his marks show, three faults under most wrong rows (put to him; he asked whether the rules are getting too
  specific, and Claude's answer was yes for the engine patches, no for his definitions):
  1. Who is in which fight is read from reach (1,600) each 2 s and patched by time rules: numbers are off by one or
     two (4 v 2 for his 5 v 3), defenders miscounted, joins and leaves seconds out. One reading is needed, used by
     numbers, splits and defenders alike (standing together, moving with, and who hits or casts on whom), R-464.
  2. A split is kept as a split for minutes after the fight it belongs to has become the main fight on the enemy's
     ground (Men v Apes 2:30 to 7:00 and 7:48 to 11:16: 12 situations "not a split"; he notes a 5 v 4 and a 6 v 7 in
     Apes's pit that were missed), and full collapses are missed where they happen (TFS v 옷옷옷옷 1:16, 4:15, 9:30).
  3. A flag run's window: it starts minutes early and ends minutes late (0:27 for his 1:20; to 5:09 for his 2:54),
     "a flag in hand" is read far from the stand, single runs are read as double, and the wrong runner is named.
- The review key (`tools/golden/review.py score <file>`): set 1, 28 rows pass; open checks on s1-15, s1-26, s1-31
  (R-464, not built) and s1-24 (no split read on his redrawn Meditation). Run it after every change on the
  development set (`moments.py all <file> --dev`, under a minute).

## Next (in order; REDESIGN.md "Build plan from here", item 6, and "Tests")
1. His answer on the approach first. Proposed: no new rules or thresholds; rebuild the three readings above at the
   root, one at a time (who is in which fight; split or main fight; the flag run's window), writing checks from the
   w1p1 rows as each is rebuilt and rescoring on the development set; a change to a record: gate, line-up, thresholds.
2. The page: under a situation he marks wrong, the calls are not asked for; rows that repeat one reading are shown
   once; every row links to its second of the replay if gvg.report allows it.
3. Then export part 2 from the fixed reading (`--part 2`: hdm v hook 8bf4ffae, Men v Crew 51683de9) and change nothing
   until he has marked it: it gives the accuracy by kind of play, and he sets the mark a kind must pass. 옷옷옷옷 v
   RACK (a8ba43a8) is the spare: never look at its rows.
4. The flag family to the end (R-451) once the flag plays pass; the other kinds as each passes; then stage E.

## Open for Denning (put to him 2026-11-13, night; set each out in the chat again, R-329, with replay links)
1. The approach in "Next" 1: agreed?
2. Key s1-26, hdm v 옷옷옷옷 4:06 (https://gvg.report/report/7209c1a1-20ff-5f4f-a176-9cf92f7c594c#map): ruled an even
   join; by reach it is 3 v 2 for 10 s (8 Monk and Air Ele) and then 1 v 2. What does he see?
3. Key s1-24, OG v Dz 2:34 (https://gvg.report/report/a921418b-c4d1-5872-aca9-18f9ad99bf40#map): on his redrawn
   Greater stand area no split is read there. Right?
- Drafts: numbers from kills; a split with no answer; "held by monks"; the Lord push's aim; thresholds marked
  "Claude's draft". Not built: shadow with a snare; the two-monk spike build after a wipe. Maps: `tools/maps/`.

## Running it
- Train batch: `gh api -X POST repos/itsha12/gvginfo/actions/workflows/train-batch.yml/dispatches -f ref=main
  -f 'inputs[pick]=45' -f 'inputs[add_batch]=yes'` (rebuild only: `inputs[add_batch]=no`; TQs `inputs[tqs]=yes|no|auto`;
  blind round `inputs[blind]=no|yes|auto`, default no while rounds are paused). Never queue two runs at once.
- Local engine: `git fetch --depth 1 origin +replays:refs/remotes/origin/replays`; `pip install
  --break-system-packages -r .github/workflows/train-requirements.txt`. The records, the story, the line-up, the gate
  and the thresholds need no cache (`cache.py sync pull`, `warm` only for the fitted models). `PYTHONDONTWRITEBYTECODE=1`.
  `thresholds.py run`: about 15 minutes, two jobs, the machine to itself; old and new one after the other.

## Cautions
- Never print or decode a sealed field (blind picks, golden moments) in a chat.
- Don't merge `bundle-4` piecemeal (R-322). Label and golden files are saved whole by the site: after a change
  here, Denning reloads the page first. Hall labels are saved to main: copy changed `data/maps/labels/*.json` to the
  branch before reading a hall (all 14 matched main on 2026-11-12).
- Transcripts never go in the repo: paraphrased statements only. Party slots are in `data/matches/`, not the replays.
- `golden_moments.json` on the branch is a copy of main's; refresh it from main before the gate.
