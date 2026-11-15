# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then set out the items under "Open for Denning" and carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it. Add your
> answers to the open items, by their numbers, to the same message if you have them.)

## State (2026-11-14, late: redesign step 2 on branch `bundle-4`, stage D under way; batch 17, 506 matches trained)
- Main's engine is unchanged (SPEC.md). Bundle 4 is on `bundle-4` and lands in one piece, then one rebuild (R-322).
  658 replays stored; 564 count (R-477); the trained batches still hold some. No Train batch, Discovery or fetch run
  in progress. Both branches committed; this session's commits are pushed only once he says so.
- On `bundle-4`: `hallmap.py`, `moments.py` (records, decision moments, shape, consequences), `jobs.py` (the plays
  and their jobs, R-423 to R-449), `story.py`, `tools/golden/golden.py`, `lineup.py`, `thresholds.py`, `review.py`.
- Built at the root (R-465) from his answers (R-455 to R-480) and the six games marked before this one (detail:
  CHANGELOG): damage against monks (`can_kill`); who is in which fight (`Moments.linked`, `engaged_in`, `visits`,
  `with_rest`: one fight at a time); a split told once (R-469); a flag run judged to its cap (R-471); the double
  run as a pair (R-472); pit archers by his hall labels; the boost's own clock; a numbers difference told once;
  henchman games out (R-477; `integrity.py henchmen` after any fetch); a break-out only if nothing was lost first
  (R-478); the opening flags as runs (R-479); a draft number moves only on a fresh game's evidence (R-480).
- Whole-game scores, situations right of those he judged (R-475), each a fresh game for the engine it was marked
  against: part 1 (TFS v 옷옷옷옷, Men v Apes) 45 of 85; hdm v hook 35 of 58 (60%); round 3 (set w2): hook v hold
  24 of 41 (59%) and cope v Team 15 of 24 (62%) on b025445, RJT v RACK 33 of 45 (73%) on b09a26a. The mark is 80%
  (R-473).
- RJT v RACK on Nomad's (eea5ba87) is marked and filed: flag 6 of 10, split 12 of 19, numbers 4 of 5, the other
  kinds all right; all 52 calls he judged under a right situation right. Under the mark: the hidden games stay
  hidden. Nothing is built from it yet (his go-ahead first): 14 checks from his words, all open.
- Now (development set, 44 matches): review key 120 rows pass; 56 checks open (w1p1 15, w1p2 10, w2 30, s1-15).
  Open in w2 before this game: a split's start when it stands off first; defenders named or counted one out; a flag
  held on purpose; "no real fight" moments. Gate: 12 of 12, 62 of 105. Line-up: 421 of 426 and 185 of 186; comms
  108 of 157, 62 of 80. No run over every match, no `thresholds.py` (R-465).
- `review.py numbers` (R-470): reach, hold time and the 12 s matter. `review.py compare`: only on one marked game.

## Next (in order; REDESIGN.md "Build plan from here", item 6, and "Tests")
1. On his go-ahead, rebuild at the root from RJT v RACK (R-465), its 14 open checks as the test. Two faults sit
   under 11 of its 12 rows not right:
   - Who is on a split (rows 12, 13, 15, 21, 25, 36, 39; 48 is the same fight told twice). `split_plays` counts a
     split player only while he stands on the enemy's ground (`_deep`): a monk or mesmer a few hundred units behind,
     in the greater stand area, drops out. And `attempts()` hangs a split on the bigger group as the main team: with
     each team in two groups for minutes (4 and 4, 5 and 3) that label flips and the record loses players already
     there. Read it from who is in that fight (`linked`, `engaged_in`), with the main team by R-335 once he rules.
   - Whose flag decision, and from when (rows 8, 29, 44; 6): `run_starts` reads `runner` and `under_way` from the
     capper, so a flag handed on before its cap starts at the hand-off; a runner walking through the greater stand
     area to cap is read as a flag in hand; a double run is labelled from the first run of the pair; a return is
     timed from the next pickup (0:34 for 0:18 at the opening).
2. Then `review.py compare`, the numbers test (R-470), a fresh game as round 4; at 80% right, the hidden games
   (never export or look at Men v Crew or 옷옷옷옷 v RACK before). Then the flag family to the end (R-451), stage E.

## Open for Denning (put to him 2026-11-14; set each out in the chat again, R-329, with replay links)
RJT v RACK: https://gvg.report/report/eea5ba87-ac20-5ba3-a6c9-965f11ca8a65#map
1. The main team when a team is in two groups of 4 and 4 or 5 and 3 away from the stand: always the flag group
   (R-335 at any size)? Then each front-door fight is told once, as a split with its defenders.
2. Row 13 (3:24), "a 3 person split (with 7 monk and mesmer)": RJT's three at RACK's door, or RACK's players?
3. Row 15, "look at 4v3 for RACK at 5:30": should row 22 (5:28, marked right as 3 v 3) read 4 v 3 with the 7 Monk?
4. Row 21, "see above": read as RJT's Ranger, Stand Mes and 7 Monk, not a split of one. Right?
5. Row 6 (1:41): is the Dervish's run a single run because a double starts only when the second player goes back
   (2:27, row 9), or because 3 s before the cap is too late to be a second runner at all?
6. Row 8 (2:23), marked wrong without words: is it that no run starts there (the Mes/A ran it from 1:50)?
7. Row 40 (9:02): his words stop at "they are only down until".
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
  branch before reading a hall (the export refuses otherwise, and never shows a hidden or spare game).
- Transcripts never go in the repo: paraphrased statements only. Party slots are in `data/matches/`, not the replays. Refresh the branch's `golden_moments.json` from main before the gate.
