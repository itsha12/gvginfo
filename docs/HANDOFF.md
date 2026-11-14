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
- Now: w1p1 checks 18 of 36 hold; set 1: 28 rows pass, s1-31 holds, open s1-15, s1-24, s1-26. Gate: part one 12 of
  12, part two 64 of 105 (61%). Line-up: 421 of 426 and 185 of 186 seen (one lost in each: look at them); comms 108
  of 157, 62 of 80. Development set only (42 matches); no run over every match and no `thresholds.py` since the
  rebuild: both are due before part 2 is written.
- The page: calls under a situation he marks wrong or a repeat are not asked for; Repeat is a mark.

## Next (in order; REDESIGN.md "Build plan from here", item 6, and "Tests")
1. The 18 open checks of w1p1 (`review.py score` lists them), by the same method: the numbers still one out at five
   moments of Men v Apes (who he counts: open item 2); a full collapse read from when the team turns to go, not from
   when it arrives (his 1:16, 4:15, 9:30 against 1:28, 4:36, none); the 5 v 4 in Apes's pit while Men's team is divided
   in Apes's base (no play covers a divided main team push); Men's 8 Monk's flag at 10:10.
2. Then the line-up's two lost statements, a run over every match, `thresholds.py`, and part 2 (`review.py export
   --part 2`: hdm v hook 8bf4ffae, Men v Crew 51683de9; change nothing until he has marked it). 옷옷옷옷 v RACK
   (a8ba43a8) is the spare: never look at its rows.
3. The flag family to the end (R-451) once the flag plays pass; the other kinds as each passes; then stage E.

## Open for Denning (put to him 2026-11-13, night; set each out in the chat again, R-329, with replay links)
1. The flag job "lose no more players than they do" (R-426): TFS v 옷옷옷옷 3:26, he says TFS's single run succeeded;
   the flag got in, but five TFS players died in the window, on the split that was collapsed on. Count only deaths
   the run causes (at the main fight, short the runner), or none?
2. Men v Apes 6:12 (https://gvg.report/report/149fbdc6-f703-5171-a24e-9165a20cecb6#map): he reads 5 v 5 in Apes's
   pit; the engine has four Apes there (7 Monk, Prot, Mesmer, Ritualist). Who is the fifth?
3. TFS v 옷옷옷옷 2:54 (https://gvg.report/report/bdaa145f-1471-57b3-ab2f-a04f090b7abb#map): "the single run ends
   when they cap the fire ball thing": what is capped there?
4. Key s1-26, hdm v 옷옷옷옷 4:06 (https://gvg.report/report/7209c1a1-20ff-5f4f-a176-9cf92f7c594c#map): 2 v 2, 3 v 2
   or 1 v 2? Key s1-24, OG v Dz 2:34 (https://gvg.report/report/a921418b-c4d1-5872-aca9-18f9ad99bf40#map): no split?
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
