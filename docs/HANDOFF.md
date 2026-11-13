# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then set out the items under "Open for Denning" and carry on with "Next".
> (Add your answers to the open items, by their numbers, to the same message if you have them.)

## State (2026-11-13 night: redesign step 2 on branch `bundle-4`, stage D under way; batch 17, 506 matches trained)
- Main's engine is unchanged (SPEC.md). Bundle 4 is on `bundle-4` and lands in one piece, then one rebuild (R-322).
  606 replays stored (90 from 2 September on not yet trained on). No Train batch, Discovery or fetch run in progress.
  Last commits: main, this handoff (after 04a93b7); `bundle-4` 2c70ac9. Both pushed; nothing uncommitted.
- On `bundle-4`: `hallmap.py`, `moments.py` (records, decision moments, shape, consequences), `jobs.py` (the plays
  and their jobs, R-423 to R-449), `story.py`, `tools/golden/golden.py`, `lineup.py`, `thresholds.py`, `review.py`.
- Both gates pass (key v3): part one 12 of 12, part two 65 of 105 (61%). Line-up: building 422 of 426, held-out 186
  of 186; comms 110 of 157 and 62 of 80. Golden stories draft 10. All unchanged by this session's last changes.
- The method changed (R-450 to R-454), because his review of the first 35 cases found 7 of 24 marked rows right while
  every gate passed: the gates check that what was said is in the story, not that what the engine says is true.
  - The review key (`data/model/review_key.json`; `tools/golden/review.py score <file>`): his marks as checks. Set 1
    = his 35 rows: 28 checked, all pass; three checks open (below). Run it after every change, on the development
    set (`moments.py all <file> --dev`: 42 matches, under a minute). Every match only at a checkpoint.
  - `docs/DEFINITIONS.md`: the current definitions by topic, citing their rulings. Faults are checks, not rulings.
  - Reviews are by whole games (`review.py game <id> <file>`); the golden moments page is retired (the 15 moments
    and their key stay as part one of the decision gate).
  - The flag decision goes to the end first (R-451): similar cases, then the held-out advice test, on the branch.
- A split is read phase by phase from when it reaches (R-438 to R-449); Shadow of Haste runs are marked and set
  aside. Last full run (before the two fixes the key found): 39,399 plays, 32,074 moments over 606 matches. No
  scratch file survives a session: start with `moments.py all /tmp/dev.json --dev`, then `review.py score`.

## Next (in order; REDESIGN.md "Build plan from here", item 6, and "Tests")
1. The whole-game review, set w1 (`dev_set.json`, `whole_game`): part 1 = TFS v 옷옷옷옷 (bdaa145f, 40 situations) and
   Men v Apes (149fbdc6, 45); put each to him in the chat, one game a message, every situation with what the engine
   reads and each side's job and result. File his marks in the review key, fix, rescore. Then part 2, which must not
   be fixed against before he marks it: hdm v hook (8bf4ffae, 72), 옷옷옷옷 v RACK (a8ba43a8, 43), Men v Crew
   (51683de9, 41, two Lord pushes). Part 2 gives the accuracy by kind of play; he sets the mark a kind must pass.
   Top up rare plays (the Lord push, the part-run, leaving before a res) with about ten picked rows.
2. R-449 (a player counts in fight numbers only after 12 s; moves the numbers moments: rerun the gate, the line-up
   and `thresholds.py`) and R-440 (when the split and flag moments are named), once he has answered.
3. The flag family to the end (R-451), once the flag plays pass the key and he has answered on Shadow of Haste:
   similar cases for the flag plays (2.10, with strength R-432 and the hall R-436), then the advice test on unseen
   matches. Read the result with him whatever it shows.
4. The other kinds as each passes the key; then stage E (side by side, SPEC.md and METHODS.md, R-398, merge).

## Open for Denning (put to him 2026-11-13; he answers next session. Set each out in the chat again, R-329)
1. The whole-game review: does he agree to two parts (two games, the fixes, then three) and one game a message?
2. Key s1-26, hdm v 옷옷옷옷 4:06: he approved as a collapse one player leaving the main fight for 16 s, one already
   defending, against a split of two; R-441 (his row 21) needs the defence one more than the split, so the engine
   now reads one defender. Which stands?
3. Key s1-23, 옷옷옷옷 v Men 6:22: he approved "not met" where an archer and two footmen were lost; R-443 (his row 24)
   counts only pit NPCs against the defence, so it now reads "met". Which stands?
4. Shadow of Haste runs: out of every flag count and the flag lead? When was the mechanic removed? (Gates R-451.)
5. To settle on the games: damage against monks (R-444: kill expected at twice the monks facing it? the main team's
   job whenever the defence puts more monks on the split than it brought? who counts as a monk: today backline
   monks only); when a split's moment is (R-440: the leave, now a median 34 s before it reaches; the crossing; or
   the reach); the 12 s rule for fight numbers (R-449, key s1-31); full collapse read 507 times (too many?); key
   s1-15, a defender on the split under 12 s at game end.
6. Remove the Golden moments page now, or with the Templates and Meta tabs at R-398 (as planned)?
7. Approve, or not, the proposed CLAUDE.md rule that a reading which fails must fail loudly.
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
