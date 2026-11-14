# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then set out the items under "Open for Denning" and carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it. Add your
> answers to the open items, by their numbers, to the same message if you have them.)

## State (2026-11-14: redesign step 2 on branch `bundle-4`, stage D under way; batch 17, 506 matches trained)
- Main's engine is unchanged (SPEC.md). Bundle 4 is on `bundle-4` and lands in one piece, then one rebuild (R-322).
  606 replays stored (90 from 2 September on not yet trained on). No Train batch, Discovery or fetch run in progress.
  Both branches pushed; nothing uncommitted.
- On `bundle-4`: `hallmap.py`, `moments.py` (records, decision moments, shape, consequences), `jobs.py` (the plays
  and their jobs, R-423 to R-449), `story.py`, `tools/golden/golden.py`, `lineup.py`, `thresholds.py`, `review.py`.
- Built from his answers (R-455 to R-475) and the first four marked games, at the root (R-465): the ratios of
  damage against monks (`can_kill`); one reading of who is in which fight (`Moments.linked`, `engaged_in`, `visits`);
  a split told once (R-469); a flag run judged to its cap (R-471); the double run (R-472). Detail: CHANGELOG.
- Whole-game scores, situations right of those he judged (R-475), each a fresh game for the engine it was marked
  against: part 1 (TFS v 옷옷옷옷, Men v Apes) 45 of 85; hdm v hook 35 of 58 (60%); round 3 (set w2, engine
  b025445): hook v hold 24 of 41 (59%), cope v Team 15 of 24 (62%). Calls right where the situation was right: 31 of
  35 and 22 of 23. The rebuilds since hdm v hook did not move the fresh-game figure: the mark is 80% (R-473).
- Built from round 3 (engine 7244f5b): pit archers are the ones his hall labels place in the pit (`MapGeo._by_labels`;
  the estimate had base archers in the pit on Jade and Nomad's); the boost keeps its own clock and says a flag
  already on its way; a result counts only the players of the fight (deaths that made the numbers are its cause); a
  numbers difference is told once (a level spell or a reversal shorter than a moment is no break); a player is in one
  fight at a time (`Moments.with_rest`: a split player, or a defender, standing with three of the main team is at the
  main fight); a double run is a pair of runs; held in also at its own door with the enemy deeper in.
- Round 3's third game is on the page, not yet marked: RJT v RACK on Nomad's (eea5ba87; 52 situations, splits and
  flags). chic v 戦戦戦戦 was set aside: a henchman game (R-476). Men v Crew stays hidden; its misclicked marks are out.
- Now (development set, 45 matches): review key 109 rows pass; 44 checks open (w1p1 15, w1p2 10, w2 18, s1-15).
  Open in w2: the opening flags are not read as runs; a split's start when it stands off before fighting (14:09 and
  18:44 of hook v hold); defenders named or counted one out; a flag held on purpose; a 1 v 8 on a straggler through
  the Jade portal; "no real fight" moments. Gate: 12 of 12, 62 of 105. Line-up: 421 of 426 and 185 of 186; comms 108
  of 157, 62 of 80. No run over every match, no `thresholds.py` (R-465).
- The numbers test is `review.py numbers` (R-470; 85 s a value, the whole development set each time). At 75% and
  125% (before round 3's changes): reach 1,600 (12 and 1 rows fail), hold time 6 s (8, 0), the 12 s (1, 2), acting
  distance 2,600 (2, 0), hold distance 2,100 (1, 0), joined 1,000 (1, 0); three numbers change nothing.
- Compare engines only on one marked game (`review.py compare`): today's is not shown better on hdm v hook.

## Next (in order; REDESIGN.md "Build plan from here", item 6, and "Tests")
1. He marks RJT v RACK (Model > Game review). `review.py file <id> <rows> <marks> --set w2` files his marks and
   prints the score; write checks from his words; fix at the root (R-465). Never re-export a game he has marked
   (a new game goes in as a new part of its set). The export checks the hall labels against main itself.
2. Then `review.py compare`, and the numbers test on the marked rows (R-470). At 80% of situations right on a
   fresh game, the hidden games. Never export or look at Men v Crew or 옷옷옷옷 v RACK before that.
3. The flag family to the end (R-451) once the flag plays pass; the other kinds as each passes; then stage E.

## Open for Denning (put to him 2026-11-14; set each out in the chat again, R-329, with replay links)
1. RJT v RACK is his to mark (https://gvg.report/report/eea5ba87-ac20-5ba3-a6c9-965f11ca8a65#map).
2. Henchman games out of the dataset (R-476 leaves it open): 42 of the 606 that count have one. Recommended: out of
   training, benchmarks and review picks; results still count for ratings. Two more games have a team of seven.
3. Held in (pinned): Team loses a knight at 10:42 of cope v Team and breaks out after. Is the job met?
4. The opening: read each team's opening flag as a run (hold's from 0:17 of hook v hold), and who is left back?
5. When a draft number may move (Claude's proposal): never from the marked rows alone; only when the same step
   also reads a fresh game better, scored before any fix, and the reason can be said in GvG terms.
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
