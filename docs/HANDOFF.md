# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. `CLAUDE.md` is loaded already: read this, then only the section of
`docs/ENGINE_NOTES.md` named beside the item you take up. The plan is `docs/REDESIGN.md`, the definitions
`docs/DEFINITIONS.md`, the rulings `docs/RULINGS.md` (search it), the history `docs/CHANGELOG.md`. For execution work
read `docs/EXECUTION.md` first: the catalogue of every why, its rules, and the order of work.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read docs/HANDOFF.md (CLAUDE.md is loaded automatically),
> check out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-28, evening: rulings to R-856; nothing running; `bundle-4` 5db24a4, main as pushed)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stages D and E) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored, each with its file beside it; 564 count (R-477); 506 trained.
  Baseline (R-491): `baseline-2026-11-15`. Thirteen games graded (set f1); R-570 holds. No workflow is running.
- The last bundled change is built and run (`bundle-4` 04310c3; ENGINE_NOTES sections 44 and 22, last items): Shadow
  Shroud by name (R-849); a prot or heal let through, the attack's fault (R-850, R-853: +12.2 points, 9/10); a second
  player gone back by the cap is a double run, told from that second (R-854, R-856: 228 plays, no minimum lead).
- Full run at 04310c3 (130e76f holds its files): 564 matches, no errors, 33,106 plays, 323 Classic rows pass, every
  truth holds, nothing newly reads backwards. Every `cases.py` report and the digest are this run's. Its win chance
  file went to him in the chat (for Opus's exporter; not in the repo).
- Flag advice cards written again (R-852; `flag_cards.json` at 04310c3): 40 of his 55 marked cards carry `changed`,
  6 `gone`, nearly all from changes before today's; no marking round. `execution_rows.json` again (four rows gain a
  Shadow Shroud line). The close is begun (R-855): `ask.py` is rewired (R-845; 5db24a4).

## Next (the close; ENGINE_NOTES section 37, its last item, is the approach: read it first. No reading changes: R-322)
1. His answers to the two questions under "Open for Denning" 1 come first (he may give them in the first message).
2. Fable, on `bundle-4`, in one chat: (a) the `families` job in `train-batch.yml` (`moments.py all`, the key and
   truths as gates, the digest check, the `cases.py` reports) and the learning report's section "The new families
   beside the old kinds", with the old kinds' reading before kept (`advice_test_before.json`); a `trial` input that
   runs the new job alone from the branch and commits nothing; (b) `cases.py --prices model` beside the stand-in
   (the win model's held-out chance every 5 s, written by `prepare`). Try every command in the chat (this chat's
   script: `moments.py all`, then ladder, test, the other reports, execution last; about 1.5 h). Nothing is retired yet.
3. Then word to him: Opus drafts SPEC and METHODS and runs the readability test (Opus is already on the match
   report, the Blind test and Golden moments pages, and the old knowledge pages; started 2026-11-28).
4. His list of R-398 (items 1, 2, 3's remainder, 6, 7, 8, 10; from `docs/opus/pre-training-drafts.md`), his word on
   each. The merge only at his explicit word; one Train batch on the same 506 (he starts it, `add_batch` no).
5. The rebuild read with him; then the old kinds retired (`decisions.py`, `usual.py`, `advice.py`, `tq.py`, their
   parts of `learning.py` and the workflow, R-398 item 3's data files); the cards again if the prices moved them.

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand (R-553 to build) and a double run from the sender's side.
1. Put to him 2026-11-28 (evening), with the approach: (i) a trial of the new job alone on GitHub from `bundle-4`
   before the merge (about an hour, he starts it, nothing committed): recommended; (ii) for the one rebuild the
   families priced both ways, stand-in and win model, the win model's kept if their tests are no worse: recommended.
2. Run again shows a gain on unseen matches (+2.0 at 90 s, +3.3 at 180 s): noted as a reading (R-856); to set out
   to him spot by spot (`cases.py test`, sections 5 and 8) when he asks or at the rebuild.
3. Claude's readings in R-811 to R-817, R-822 to R-830, R-832, R-835, R-837, R-840, R-841, R-847, R-849: his to correct.
   No row for an even 6v6 and below. Wiki sync: his button before the retrain (R-765, R-398 item 6). R-673, R-576, R-575.

## For Opus (Fable never edits `docs/OPUS.md`)
- The guild page scrolls sideways at phone width (390 wide, about 85 px over): the "Most played full lineups"
  block (`.comp`).
- The Execution view's "How to read and mark a row" (`review.js`) is out of date (three kinds, the heaviest 2 s).
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
  may push to `bundle-4` (data files only): fetch before every push there. When a fault is found, say how many plays its
  fix would move, not only how many trip the check (2026-11-28: 62 tripped, 228 moved).
