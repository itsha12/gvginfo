# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. `CLAUDE.md` is loaded already: read this, then only the section of
`docs/ENGINE_NOTES.md` named beside the item you take up. The plan is `docs/REDESIGN.md`, the definitions
`docs/DEFINITIONS.md`, the rulings `docs/RULINGS.md` (search it), the history `docs/CHANGELOG.md`. For execution work
read `docs/EXECUTION.md` first: the catalogue of every why, its rules, and the order of work.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read docs/HANDOFF.md (CLAUDE.md is loaded automatically),
> check out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-28, end of the chat: rulings to R-851; nothing running; `bundle-4` 16935c2, main as pushed)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stages D and E) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored, each with its file beside it; 564 count (R-477); 506 trained.
  Baseline (R-491): `baseline-2026-11-15`. Thirteen games graded (set f1); R-570 holds. No workflow is running.
- Execution (R-701 to R-851; `docs/EXECUTION.md`, 68 rules): his marking is done for now (R-851; set x1: Men v Crew
  15 deaths, RACK v hdm 10, Men v NwAy 12 of 21). What fails its check waits until family 4 (R-848).
- `bundle-4` 16935c2: the engine is 4d3866c (balling reads Invoke Lightning and Chain Lightning, R-847). Full run at
  4d3866c made by Fable: 564 matches, no errors, the digest agrees on all, 323 Classic rows pass; `attempts_cases.json`
  is that run's; main's `execution_rows.json` the same row for row. The other reports and winchance: unmoved.
- Filed from `docs/OPUS.md` (REDESIGN.md amended): R-843 no blind tests, R-844 step 3 dropped, R-845 `ask.py` rewired
  at the close, R-846 the match report with the close's merge. The blind test page is hidden, not yet removed.

## Next (in order; the approach was set out to him on 2026-11-28, his answers to its questions come first)
1. One bundled engine change on `bundle-4`, three parts (ENGINE_NOTES sections 44 and 22, their last items):
   a. Shadow Shroud kept by name (R-849): into `BY_NAME`, its check the row against the same teams' other spikes.
   b. A prot or heal let through with an interrupt ready, the attack's fault by name (R-850): new. Put to him: on
      spikes only (as R-805 has the defence's interrupt), only a prot or heal for the target that landed, the
      interrupter with the skill ready, in reach and time to react (Rule 1), only skills on the interrupt list.
   c. The flag play whose runner set off before the moment he is told to answer (62 plays of 5,252; hold v RACK
      2:16 stops `cases.py cards`): at the root in `jobs.flag_plays`. Put to him: a double run (R-485, R-547)?
   Then the development set, the key, `compare.py` (only c moves plays), and one full run with every report, the
   digest made again, winchance (Opus, or Fable in the chat: 37 minutes).
2. The Flag advice cards written again once (`cases.py cards <run> f1 --site`): proposed to him, no marking round;
   only a card he marked that now says something else is shown to him. The held cards stay held (R-554).
3. The close (sections 37, 38, 34, 35, 41), set out to him in four parts: (i) Fable: new families beside the old
   kinds for one rebuild (R-323), stand-in prices replaced, old kinds retired (`learning.py` imports `tq.py`),
   `ask.py` rewired (R-845); (ii) Opus: SPEC and METHODS drafts, the blind test and golden pages removed, the old
   knowledge pages, the readability test, the match report (Fable reviews its exporter once, R-846); (iii) his
   list of R-398 (items 1, 2, 3's remainder, 6, 7, 8, 10; from `docs/opus/pre-training-drafts.md`), his word on
   each; (iv) the merge only at his explicit word, then one Train batch on the same 506 (he starts it).

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand (R-553 to build) and a double run from the sender's side.
1. Put to him 2026-11-28, unanswered: no new marking round of the flag cards; R-850's four points; the runner who
   goes back before his team's flag is in; which chat does which part of the close.
2. Claude's readings in R-811 to R-817, R-822 to R-830, R-832, R-835, R-837, R-840, R-841, R-847 and R-849, his to
   correct. Rows written over ones he marked, all said to him (ENGINE_NOTES section 44, and R-828's).
3. No row for an even 6v6 and below. The wiki sync: later (R-765). At R-398: September's early matches (R-673), R-576, R-575.

## For Opus (Fable never edits `docs/OPUS.md`)
- The guild page scrolls sideways at phone width (390 wide, about 85 px over): the "Most played full lineups"
  block (`.comp`).
- The Execution view's "How to read and mark a row" (`review.js`) is out of date (three kinds, the heaviest 2 s).
- "For Fable" lines acted on, to remove: the plan change (filed, R-843 to R-846) and the f7165b1 run's report (read;
  nothing reads backwards against its own like). Kept for the close: the R-398 drafts, the match report review.
- No full run is wanted (Fable's at 4d3866c). The exporter can use the f7165b1 run's files: balling is in neither.
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
