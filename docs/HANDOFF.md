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
- Built from his answers (R-455 to R-464): the ratios of damage against monks and the main fight's kill job
  (`can_kill`; a side facing no monk always has it); Shadow of Haste by date; a split's moment at the crossing; a flag
  run's moment by hall; `blanks` (R-460). The page: Repeat is a mark; calls under a wrong situation are not asked.
- He marked part 1 of the whole-game review on the site (Model > Game review; TFS v 옷옷옷옷 bdaa145f, Men v Apes
  149fbdc6; engine af952c6): situations right 45 of 85, calls right 62 of 68 where the situation was right. His
  marks are in the review key as set w1p1 with 36 checks written from his words (open until they hold).
- Rebuilt at the root since (R-465, no new rules for single rows): one reading of who is in which fight
  (`Moments.linked`, `engaged_in`, `visits`), used by the numbers and a split's defenders; a split ends when the rest
  of its team is with it; the flag run's start, the flag in hand, the answer to a run, the double run; the break-out
  test; a part-run is no push on a flagger; the WoC monks are damage. Thresholds in `common.py` are drafts.
- hdm v hook (8bf4ffae), marked 2026-11-14 against engine 67e87b8: situations right 35, partly 7, wrong 16 of 58
  judged; calls right 50 of 54 where the situation was right (pinned, push flagger, base res, boost all right; flag 3
  of 5, numbers 5 of 13, split 11 of 24). Set w1p2, 20 checks. Built from since (R-467): Men v Crew (51683de9) is
  the hidden game, 옷옷옷옷 v RACK (a8ba43a8) the spare. Built from it: `FOUGHT` (a numbers moment needs casts and
  attacks), the monk ratio in the main fight's kill job, a flag never out of its base is no run, the flag decision
  from the side that ran second, staying met when their flag fails (R-468), the pinned clock.
- A split fight is told once (R-469): split calls on the development set 1,726 to 1,161; hdm v hook 115 calls to 69.
- Now (development set, 42 matches): review key 80 rows pass; 28 checks open (w1p1 16, w1p2 11, s1-15): numbers one
  out, a defender missed at 6:46 of TFS v 옷옷옷옷 and 13:02 of hdm v hook, two flags, a door, a missed solo split.
  Gate: 12 of 12, 63 of 105. Line-up: 421 of 426 and 185 of 186; comms 108 of 157, 62 of 80 (not rerun since the
  split change, which is in `jobs.py` only). No run over every match, no `thresholds.py` (R-465).
- The draft numbers, each tried at half and double against the 80 marked rows (R-470; rows that then fail): reach
  1,600 (8 and 2), the 12 s of R-350 (5 and 4), hold time 6 s (5 and 1), acting distance 2,600 (6 and 0), hold
  distance 2,100 (1, 0), joined 1,000 (1, 1), `FOUGHT` 0.7 (1, 1), flag kept at home 20 s (0, 1), double run 30 s (0,
  0: the value does not matter between 15 and 60).
- Tried and taken out (each broke his row 28 of TFS v 옷옷옷옷 or changed nothing): a full collapse counted from the
  main team closing on the split; a defender kept counted while he kites out of reach.
- Compare engines only on one marked game (`review.py compare`): on hdm v hook today's is not shown to be better.

## Next (in order; REDESIGN.md "Build plan from here", item 6, and "Tests")
1. His answer on the baseline: mark the 54 calls only the session's first engine makes on hdm v hook, for a true
   before and after? And on round 3 (how many games, the mark to reach).
2. Round 3: pull two or three more games (October and November, top guilds, no earlier test, no Shadow of Haste,
   halls and styles unlike the three marked), add them to `dev_set.json`, score the engine on each before any fix,
   export, he marks. After the round: `review.py compare` on a marked game, and the numbers test (R-470). Never
   export or look at Men v Crew or 옷옷옷옷 v RACK before the final measure.
3. The flag family to the end (R-451) once the flag plays pass; the other kinds as each passes; then stage E.

## Open for Denning (put to him 2026-11-14; set each out in the chat again, R-329, with replay links)
1. The baseline on hdm v hook: mark the 54 calls only the old engine makes, yes or no.
2. The same stretch, 5:52 to 7:24: he reads hook's run as a double run and hdm's as a single. In the replay both
   second runners take the next flag 17 to 19 s after the cap. What tells them apart?
3. Round 3: how many games, and the mark at which a fresh game reads well enough to go to the hidden games.
4. TFS v 옷옷옷옷 3:26 (https://gvg.report/report/bdaa145f-1471-57b3-ab2f-a04f090b7abb#map): still not met under
   R-466 (three TFS deaths at the main fight to none). Right?
- Drafts not ruled: numbers from kills, a split with no answer, "held by monks", the Lord push's aim, `common.py` drafts.

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
- Transcripts never go in the repo: paraphrased statements only. Party slots are in `data/matches/`, not the replays. Refresh the branch's `golden_moments.json` from main before the gate.
