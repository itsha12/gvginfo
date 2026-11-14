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
  run's moment by hall; `blanks` (R-460).
- He marked part 1 of the whole-game review on the site (Model > Game review; TFS v 옷옷옷옷 bdaa145f, Men v Apes
  149fbdc6; engine af952c6): situations right 45 of 85, calls right 62 of 68 where the situation was right. His
  marks are in the review key as set w1p1 with 36 checks written from his words (open until they hold).
- Rebuilt at the root since (R-465, no new rules for single rows): one reading of who is in which fight
  (`Moments.linked`, `engaged_in`, `visits`), used by the numbers and a split's defenders; a split ends when the rest
  of its team is with it; the flag run's start, the flag in hand, the answer to a run, the double run; the break-out
  test; a part-run is no push on a flagger; the WoC monks are damage. Thresholds in `common.py` are drafts.
- Now (development set, 42 matches): review key 60 rows pass; the checks from his words that held were made firm,
  and 16 stay open (`review.py score` lists them): s1-15; w1p1: six numbers moments one out (Men v Apes 2:10, 7:10,
  8:52, 10:28, 10:57; TFS v 옷옷옷옷 0:43, 8:40), a full collapse read from arrival and not from the turn (1:16 read
  at 1:28; 9:20 not read: the split fled first), the 5 v 4 in Apes's pit with Men divided in Apes's base, Men's 8
  Monk's flag at 10:10, the 3 v 2 at 6:58, a flag in hand at 10:13, TFS's run at 3:26.
  Gate: part one 12 of 12, part two 64 of 105 (61%). Line-up: 421 of 426 and 185 of 186 seen (one lost in each: look
  at them); comms 108 of 157, 62 of 80. No run over every match and no `thresholds.py` since the rebuild (R-465).
- Tried and taken out: a full collapse counted from when the main team closes on the split (it read the lone
  Ritualist at 7:30 of TFS v 옷옷옷옷 as collapsed on, against his row 28). It needs the team's own movement, not
  the gap between the two.
- The page: calls under a situation he marks wrong or a repeat are not asked for; Repeat is a mark.

## Next (in order; REDESIGN.md "Build plan from here", item 6, and "Tests")
1. Part 2 is out on the site (written 2026-11-13 from engine 67e87b8: hdm v hook 8bf4ffae, Men v Crew 51683de9).
   Change nothing in the reading until he has marked it. Then read `game_review_marks.json`, file his marks in the
   review key as set w1p2, and give him the accuracy by kind of play (situations, and calls where the situation was
   right); he sets the mark a kind must pass. 옷옷옷옷 v RACK (a8ba43a8) is the spare: never look at its rows.
2. The open checks by the same method (R-465); the line-up's two lost statements.
3. The flag family to the end (R-451) once the flag plays pass; the other kinds as each passes; then stage E.

## Open for Denning (put to him 2026-11-13, night; set each out in the chat again, R-329, with replay links)
1. Part 2 to mark on the site (he said to write it now).
2. TFS v 옷옷옷옷 3:26 (https://gvg.report/report/bdaa145f-1471-57b3-ab2f-a04f090b7abb#map): under R-466 TFS's run
   is still not met: three TFS deaths at the main fight (7 Monk 3:46, Mes/A 5:09, Warrior 5:20) to none. Is "not met"
   right, or is a run that gets in a success whatever it cost?
3. The four draft numbers of the fight reading (1,600 reach, 2,100 hold, 2,600 acting, 1,000 joined) and the two
   flag ones (20 s kept at home, 30 s for a double run): confirm, or say what looks wrong.
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
