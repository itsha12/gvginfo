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
- hdm v hook (8bf4ffae), marked 2026-11-14 against engine 67e87b8, was the first measure of the rebuilt reading:
  situations right 35, partly 7, wrong 16 of 58 judged (7 repeats, 2 unmarked); calls right 50 of 54 where the
  situation was right. By kind, right of judged: pinned 6 of 6, push flagger 4 of 4, base res 4 of 4, boost 2 of 2,
  flag 3 of 5, numbers 5 of 13, split 11 of 24. Filed as set w1p2 with 20 checks from his words. He then chose to
  build from it (R-467): Men v Crew (51683de9) is the hidden game, 옷옷옷옷 v RACK (a8ba43a8) the spare.
- Built from w1p2: a numbers moment needs a fight (casts and attacks, `FOUGHT`); the kill in the main fight asked
  only where the damage can kill against the monks there; a flag never carried out of its base is no run; the flag
  decision told once, from the side that ran second; staying is met when their flag fails (R-468); a kill at a phase
  boundary credited to the phase it ended; the pinned clock with nobody dead; numbers rows grouped by their start.
- Now (development set, 42 matches): review key 80 rows pass. Open checks: w1p2 13 of 20 (six are defender counts in
  the long 4 v 4 split fight of hdm v hook; three numbers; two flags; a door; a missed solo split), w1p1 15, s1-15.
  Gate: part one 12 of 12, part two 63 of 105 (60%, at his mark). Line-up: 421 of 426 and 185 of 186 seen; comms 108
  of 157, 62 of 80. No run over every match and no `thresholds.py` since the rebuild (R-465).
- Tried and taken out: a full collapse counted from the main team closing on the split (broke his row 28 of TFS v
  옷옷옷옷); a defender kept counted while he kites out of reach (changed nothing in hdm v hook, broke that same row).
  Traced: at 9:30 of hdm v hook two of hook's four defenders stand 2,700 to 3,900 from the split for 16 s, which is
  his own note on row 40 ("4 v 2 back door") and not his mark on row 42 ("definitely 4 defending").

## Next (in order; REDESIGN.md "Build plan from here", item 6, and "Tests")
1. His answer on how a long split fight is told (open item 1), then build it; then the remaining open checks.
2. Round 3: pull two or three more games (October and November, top guilds, no earlier test, no Shadow of Haste,
   halls and styles unlike the three marked), add them to `dev_set.json`, export them as their own part, and have
   him mark them. Never export or look at Men v Crew or 옷옷옷옷 v RACK before the final measure.
3. The flag family to the end (R-451) once the flag plays pass; the other kinds as each passes; then stage E.

## Open for Denning (put to him 2026-11-14; set each out in the chat again, R-329, with replay links)
1. A long split fight (hdm v hook 5:56 to 11:48, https://gvg.report/report/8bf4ffae-780e-535e-aa7b-44027b0fa6cc#map):
   the engine tells it as 15 phases with the defenders counted each time; he reads one 4 v 4 ("still the same
   split"). Tell a split fight once, with its numbers and each change beside it, as a numbers moment is told?
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
- Transcripts never go in the repo: paraphrased statements only. Party slots are in `data/matches/`, not the replays.
- `golden_moments.json` on the branch is a copy of main's; refresh it from main before the gate.
