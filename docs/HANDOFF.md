# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then set out the items under "Open for Denning" and carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)
> (Add your answers to the open items, by their numbers, to the same message if you have them.)

## State (2026-11-13 late: redesign step 2 on branch `bundle-4`, stage D under way; batch 17, 506 matches trained)
- Main's engine is unchanged (SPEC.md). Bundle 4 is on `bundle-4` and lands in one piece, then one rebuild (R-322).
  606 replays stored (90 from 2 September on not yet trained on). No Train batch, Discovery or fetch run in progress.
  Both branches pushed; nothing uncommitted.
- On `bundle-4`: `hallmap.py`, `moments.py` (records, decision moments, shape, consequences), `jobs.py` (the plays
  and their jobs, R-423 to R-449), `story.py`, `tools/golden/golden.py`, `lineup.py`, `thresholds.py`, `review.py`.
- His answers of 2026-11-13 are built (R-455 to R-461): the ratios of damage against monks and the main fight's kill
  job from them (`can_kill`); Shadow of Haste by date (22 October); a split's moment at the crossing (`t_in`); a flag
  run's moment by hall (`moment` in `run_starts()`; Uncharted not ruled); 12 s for main-fight numbers, from arrival;
  a defender there at game end; blanks counted and a field blank on every row stops `moments.py all` (`blanks`).
- He redrew the Greater stand area on Meditation, Corrupted and Weeping Stone the same evening; the labels are copied
  to the branch. On them, after the build: both gates pass (part one 12 of 12, part two 65 of 105, 61%); line-up:
  building 422 of 426, held-out 186 of 186; comms 109 of 157, 62 of 80. `thresholds.py` not rerun: do it before the
  next change to a record (the redrawn areas move the records on three halls). Full run: 606 matches, 30,490 moments
  (32,074 before: a split is no longer read at the leave and again at the crossing), 40,866 plays, no errors, no field
  blank on every row.
- The review key (`data/model/review_key.json`; `tools/golden/review.py score <file>`): 28 rows pass, five rows
  with checks open (below). Run it after every change on the development set (`moments.py all <file> --dev`, under a minute).
- The whole-game review is on the site: Model > Game review (`assets/js/pages/review.js`, on main). Rows:
  `data/model/game_reviews.json` (from `review.py export <file> <main>/data/model/game_reviews.json --part N`); his
  marks: `data/model/game_review_marks.json` (saved by the page; absent until his first save). Part 1 is out: TFS v
  옷옷옷옷 (bdaa145f, 40 situations, 100 rows) and Men v Apes (149fbdc6, 45, 130). The page has not had the
  readability test by a fresh session.

## Next (in order; REDESIGN.md "Build plan from here", item 6, and "Tests")
1. When he has marked part 1: read `game_review_marks.json`, file every mark in the review key with his words, fix,
   rescore on the development set. A fix that changes a record: rerun the gate, the line-up and `thresholds.py`.
2. Then export part 2 from the fixed reading (`--part 2`: hdm v hook 8bf4ffae, Men v Crew 51683de9) and change nothing
   in the reading until he has marked it; it gives the accuracy by kind of play, and he sets the mark a kind must
   pass. 옷옷옷옷 v RACK (a8ba43a8) is the spare: never look at its rows. Top up rare plays (the Lord push, the
   part-run, leaving before a res) with about ten picked rows.
3. The flag family to the end (R-451), once the flag plays pass the key: similar cases for the flag plays (2.10, with
   strength R-432 and the hall R-436), then the advice test on unseen matches. Read the result with him.
4. The other kinds as each passes the key; then stage E (side by side, SPEC.md and METHODS.md, R-398, merge).

## Open for Denning (put to him 2026-11-13, late; set each out in the chat again, R-329)
1. Key s1-18, ohno v Fun 11:10: he said ohno's main team should have killed, Fun having no monk at main. By R-457
   as confirmed (only a side that meets its ratio while the other does not) neither has the job: ohno's three damage
   face no monk, Fun's six face two. Over 606 matches both meet in 824 of 4,801 defended split phases, 252 of them
   with one side facing no monk. Options: the rule stands; a side facing no monk always has the job; both have it.
2. R-461: Uncharted is in both lists (leave the greater stand area, or the flag stand area?). 255 runs wait on it.
3. Key s1-26, hdm v 옷옷옷옷 4:06: ruled an even join; by reach it is 3 v 2 for 10 s (8 Monk and Air Ele, each under
   the 12 s) and then 1 v 2. What does he see there?
4. Key s1-31, Crew v hdm: the 12 s rule does not give his 7:22 and 7:28: a player counts while within reach (1,600),
   from 7:16 to about 7:36. Should joining and leaving a fight be read from movement, not reach alone?
5. Key s1-15, Book v One: the Hammer dies with the Ritualist 8 s on him, 12 s before the game ends. Count a defender
   who is on a split player when that player dies, however briefly?
6. Key s1-24, OG v Dz 2:34 (Meditation): on his redrawn Greater stand area no split is read there at all. Right?
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
