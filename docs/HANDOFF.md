# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. `CLAUDE.md` is loaded already: read this, then only the section of
`docs/ENGINE_NOTES.md` named beside the item you take up. The plan is `docs/REDESIGN.md`, the definitions
`docs/DEFINITIONS.md`, the rulings `docs/RULINGS.md` (search it), the history `docs/CHANGELOG.md`. For execution work
read `docs/EXECUTION.md` first: the catalogue of every why, its rules, and the order of work.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read docs/HANDOFF.md (CLAUDE.md is loaded automatically),
> check out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-28, evening: rulings to R-855; nothing running; `bundle-4` 5db24a4, main as pushed)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stages D and E) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored, each with its file beside it; 564 count (R-477); 506 trained.
  Baseline (R-491): `baseline-2026-11-15`. Thirteen games graded (set f1); R-570 holds. No workflow is running.
- The last bundled change is built (`bundle-4` 04310c3; ENGINE_NOTES sections 44 and 22, their last items): Shadow
  Shroud kept by name (R-849); a prot or heal let through with an interrupt ready, the attack's fault (R-850, R-853:
  +12.2 points, 9 groups of 10, it passes on its own); a runner gone before his team's flag is in (R-854: a second
  player gone back by the cap is a double run, told from the second he went; a capper's own set-off never before
  his cap; 228 plays told before the cap, our double runs 671 of 5,269 flag plays).
- Full run at 04310c3 (Fable, in the chat; 130e76f holds its files): 564 matches, no errors, 33,106 plays, 323
  Classic rows pass, every truth holds, nothing newly reads backwards. Every `cases.py` report and the digest are
  this run's. Its win chance file went to him in the chat (for the match report's exporter; not in the repo).
- Flag advice cards written again once (R-852; main's `flag_cards.json` at 04310c3): 40 of his 55 marked cards carry
  `changed` and 6 are under `gone`, nearly all from the six days of changes before today's; no marking round. Main's
  `execution_rows.json` again: four rows of Men v Crew gain a Shadow Shroud line (said to him).
- The close is begun (R-855): `ask.py` is rewired (R-845; 5db24a4; ENGINE_NOTES section 37, last item).

## Next (the close; sections 37, 38, 34, 35, 41; no engine reading changes from here: R-322)
1. Fable, in order: (a) the new families beside the old kinds for the one rebuild (R-323): the Train batch workflow
   and `learning.py` run `moments.py all` and the `cases.py` family reports beside the old kinds' advice test, the
   old kinds set against their reading before (6 of 13 clear at 506); (b) the stand-in prices of `cases.py`
   replaced by the win model's; (c) after that rebuild is read with him, the old kinds retired (`decisions.py`,
   `usual.py`, `advice.py`, `tq.py`; `learning.py` imports `tq.py`) and their data files (R-398 item 3). Set the
   approach to (a) and (b) out to him first: the workflow cannot be tried in a chat.
2. Opus, now (told to him 2026-11-28): the match report's exporter and page on a full run at 04310c3 (its own
   `moments.py all`; the win chance file from him); the Blind test and Golden moments pages removed (R-843, R-454);
   the old knowledge pages. After Fable's 1 (a) and (b): the SPEC and METHODS drafts; then the readability test.
3. His list of R-398 (items 1, 2, 3's remainder, 6, 7, 8, 10; from `docs/opus/pre-training-drafts.md`), his word on
   each. Then the merge only at his explicit word, and one Train batch on the same 506 (he starts it).

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand (R-553 to build) and a double run from the sender's side.
1. Claude's readings in R-853 (let through: thrown and missed counts; one interrupt a player) and R-854 (a) to (e),
   his to correct; with those of R-811 to R-817, R-822 to R-830, R-832, R-835, R-837, R-840, R-841, R-847, R-849.
2. Put to him 2026-11-28 (evening): run again, with the double runs told as such, shows a gain on unseen matches
   at 90 and 180 s (+2.0, +3.3): a reading he has not yet looked at spot by spot (`cases.py test`, section 5).
3. No row for an even 6v6 and below. The wiki sync: later (R-765). At R-398: September's early matches (R-673), R-576, R-575.

## For Opus (Fable never edits `docs/OPUS.md`)
- The guild page scrolls sideways at phone width (390 wide, about 85 px over): the "Most played full lineups"
  block (`.comp`).
- The Execution view's "How to read and mark a row" (`review.js`) is out of date (three kinds, the heaviest 2 s).
- "For Fable" lines acted on, to remove: the plan change (filed, R-843 to R-846) and the f7165b1 run's report.
- The exporter: a death's "Enemy good play:" can now hold Shadow Shroud (`shroud_by`); a failed spike's faults can
  be of kind `let through` (`skill`, `monk`, `at`, `by`, `tried`); a flag play's clock has `before_cap`.
- Full runs as before: `moments.py all` goes on where it stopped (`--fresh` starts over); `digest.py` compares.

## Running it
- Local engine: `git fetch --depth 1 --no-filter origin +replays:refs/remotes/origin/replays` (the files beside the
  replays come with it; about 150 MB). `jobs.py`, `moments.py`, `casting.py`, the gate, the line-up and
  `confidence.py` need only Python; `cases.py` needs numpy and scikit-learn (no cache for its reports). On 2 cores and
  7 GB: the development set about 6.5 minutes (`moments.py all <file> --dev`), workers near 150 MB each; a full run
  25 to 37 with two workers and the machine to itself, `cases.py attempts` 1, `cases.py execution`
  about 30 on its own, the other reports about 20 together (`ladder` before `test`, R-545; each kept with `--json
  data/model/<name>.json`). Set `PYTHONDONTWRITEBYTECODE=1`; never edit an engine file while a run is going (workers
  are started afresh and read the code again). After a change: `tools/golden/review.py score <file> --key
  <main>/data/model/review_key.json`, then `tools/golden/compare.py <before> <after>` (or `digest.py check`).
  The view's rows: `review.py execution <file> <main>/data/model/execution_rows.json 51683de9 d06ef3c7 c19f13e3`;
  one match's deaths in words: `execution.py deaths <the whole report id>`.
  Site check: `python3 -m http.server`, then playwright with `/usr/bin/google-chrome`, api.github.com mocked.

## Cautions
- Never print or decode a sealed field in a chat. Don't merge `bundle-4` piecemeal (R-322). The branch's own
  `CLAUDE.md` and `docs/` are old copies: main's are kept up to date. `data/skills.json` is never edited by hand.
- `data/model/interrupt_worth.json` (branch) and `docs/EXECUTION.md`'s lists are one list: change both. Another chat
  may push to `bundle-4` (data files only): fetch before every push there.
