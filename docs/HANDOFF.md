# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then set out the items under "Open for Denning" and carry on with "Next".
> (Add your answers to the open items, by their numbers, to the same message if you have them.)

## State (2026-11-13 late: redesign step 2 on branch `bundle-4`, stage D under way; batch 17, 506 matches trained)
- Main's engine is unchanged (SPEC.md). Bundle 4 is on `bundle-4` and lands in one piece, then one rebuild (R-322).
  606 replays stored (90 from 2 September on not yet trained on). No Train batch, Discovery or fetch run in progress.
  Last commits: main, this handoff; `bundle-4`, the review key copy (after 2c70ac9). Both pushed; nothing uncommitted.
- On `bundle-4`: `hallmap.py`, `moments.py` (records, decision moments, shape, consequences), `jobs.py` (the plays
  and their jobs, R-423 to R-449), `story.py`, `tools/golden/golden.py`, `lineup.py`, `thresholds.py`, `review.py`.
- Both gates pass (key v3): part one 12 of 12, part two 65 of 105 (61%). Line-up: building 422 of 426, held-out 186
  of 186; comms 110 of 157 and 62 of 80. Golden stories draft 10. All unchanged by this session's last changes.
- The method changed (R-450 to R-454), because his review of the first 35 cases found 7 of 24 marked rows right while
  every gate passed: the gates check that what was said is in the story, not that what the engine says is true.
  - The review key (`data/model/review_key.json`; `tools/golden/review.py score <file>`): his marks as checks. Set 1
    = his 35 rows: 28 checked, all pass; three checks open (s1-15, s1-26, s1-31). Run it after every change, on the development
    set (`moments.py all <file> --dev`: 42 matches, under a minute). Every match only at a checkpoint.
  - `docs/DEFINITIONS.md`: the current definitions by topic, citing their rulings. Faults are checks, not rulings.
  - Reviews are by whole games (`review.py game <id> <file>`); the golden moments page is retired (the 15 moments
    and their key stay as part one of the decision gate).
  - The flag decision goes to the end first (R-451): similar cases, then the held-out advice test, on the branch.
- A split is read phase by phase from when it reaches (R-438 to R-449); Shadow of Haste runs are marked and set
  aside. Last full run (before the two fixes the key found): 39,399 plays, 32,074 moments over 606 matches. No
  scratch file survives a session: start with `moments.py all /tmp/dev.json --dev`, then `review.py score`.

## Next (in order; REDESIGN.md "Build plan from here", item 6, and "Tests")
1. Build his answers on the branch before any game is put to him (R-456 to R-460; none is built): Shadow of Haste by
   date (22 October) with the other team's answers set aside; the ratios of R-457 in place of `KILL_RATIO` (the main
   team's kill job waits on open item 2); the split moment at the crossing; the 12 s rule for main-fight numbers from
   arrival, and a defender there at game end; the loud-failure check (blanks by field in the development run). Then
   the review key, the gate, the line-up and `thresholds.py` (R-459 moves the numbers moments). Look at s1-26's open
   check: 옷옷옷옷's player already defending at 4:06 is not counted, so the join reads 1 v 2 and not 2 v 2.
2. The whole-game review, set w1, four games (R-455): part 1 = TFS v 옷옷옷옷 (bdaa145f, 40 situations) and Men v Apes
   (149fbdc6, 45): every situation with what the engine reads and each side's job and result. File his marks in the
   review key, fix, rescore. Then part 2 (open item 1), which must not be fixed against before he marks it; it gives
   the accuracy by kind of play, and he sets the mark a kind must pass. Top up rare plays (the Lord push, the
   part-run, leaving before a res) with about ten picked rows.
3. The flag family to the end (R-451; it no longer waits on Shadow of Haste), once the flag plays pass the key:
   similar cases for the flag plays (2.10, with strength R-432 and the hall R-436), then the advice test on unseen
   matches. Read the result with him whatever it shows.
4. The other kinds as each passes the key; then stage E (side by side, SPEC.md and METHODS.md, R-398, merge).

## Open for Denning (put to him 2026-11-13, late; set each out in the chat again, R-329)
1. The review: marked on a page of the site (the retired golden page adapted: rows from a file, his marks saved to
   the repo) or in the chat, one game a message? Claude recommends the page. Part 2: Claude recommends hdm v hook
   (8bf4ffae, 72 situations, 41 split phases a side) and Men v Crew (51683de9, 41, two Lord pushes), with 옷옷옷옷 v
   RACK (a8ba43a8, 43) kept unmarked as a spare.
2. R-457: "5+ damage against 3 damage" was read as three monks: confirm. In an ordinary 8 v 8 both main teams meet a
   ratio (five damage against two monks): who has the job to kill? Claude proposes only a side that meets its ratio
   while the other does not.
3. R-458 names the split's moment (the crossing). Does a flag run's moment stay at the runner setting off?
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
