# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. `CLAUDE.md` is loaded already: read this, then only the section of
`docs/ENGINE_NOTES.md` named beside the item you take up. The plan is `docs/REDESIGN.md`, the definitions
`docs/DEFINITIONS.md`, the rulings `docs/RULINGS.md` (search it), the history `docs/CHANGELOG.md`. For execution work
read `docs/EXECUTION.md` first: the catalogue of every why, its rules, and the order of work.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read docs/HANDOFF.md (CLAUDE.md is loaded automatically),
> check out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-28, later: rulings to R-847; balling reads Invoke Lightning; a full run made at 4d3866c)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stages D and E) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored, each with its file beside it; 564 count (R-477); 506 trained.
  Baseline (R-491): `baseline-2026-11-15`. Thirteen games graded (set f1); R-570 holds.
- Execution (the micro answer) is the block of work (R-701 to R-847; `docs/EXECUTION.md`, 68 rules). His marks are
  in the review key (set x1): Men v Crew 15 deaths, RACK v hdm 10, Men v NwAy 12 of 21 (R-811 to R-830).
- `bundle-4` 16935c2: the engine is 4d3866c (16935c2 puts a comment right and holds the run's report). Fable made
  the full run at 4d3866c in this chat: 564 matches, no errors, plays and moments identical to the digest, 323 Classic
  rows pass. `attempts_cases.json` is that run's (only section I differs from f7165b1's); main's `execution_rows.json`
  is the same row for row. Not made again, nothing in them moved: the other `cases.py` reports, the digest, winchance.
- Built (R-847; ENGINE_NOTES section 44's last item holds every figure): balling reads a cast that strikes "up to N
  other foes" at each half-second step after the target's hit (Invoke Lightning 1,127 rows and Chain Lightning 451 on
  the 564; only `balled` and each play's places in it moved). Section I of `cases.py attempts` sets a late part of
  the spike against targets still alive when it landed: nothing there reads backwards now.
- Filed from `docs/OPUS.md` (REDESIGN.md amended): R-843 no blind tests, R-844 step 3 dropped, R-845 `ask.py` rewired
  at the close, R-846 the match report with the close's merge.
- A kind is tested against its own like: never with what it changes held level.

## Next (in order, R-810)
1. His answer on what fails (put to him 2026-11-28; to be filed as R-848): Claude's view is to agree that every kind
   that fails its check waits, built no further, until family 4's bundle, read again on each full run; three things
   never wait: a reading that is wrong (R-494), one that reads backwards (R-744), a ruling by name.
2. His marks on the nine deaths of Men v NwAy not yet marked, if he wishes; into the review key the same session.
3. Then the flag readings shown again (sections 15, 22: the Flag advice cards written again on this engine, his
   earlier marks beside them), then the close (sections 37, 38, 34, 35, 41): new families beside the old kinds for
   one rebuild (R-323), stand-in prices replaced, replaced kinds retired (`ask.py` rewired, R-845; `learning.py`
   still imports `tq.py`), the blind test page retired (R-843), SPEC and METHODS rewritten, the readability test,
   his list of R-398 (items 1, 2, 3's remainder, 6, 7, 8, 10 left; start from `docs/opus/pre-training-drafts.md`),
   Fable's one review of the match report's exporter (R-846), the merge, one Train batch on the same 506 (he
   starts it). Set the close's approach out for him before starting it.

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand (R-553 to build) and a double run from the sender's side.
1. Claude's readings in R-811 to R-817, R-822 to R-830, R-832, R-835, R-837, R-840, R-841 and R-847, his to correct.
   Rows written over ones he marked, all said to him (the list: ENGINE_NOTES section 44, and R-828's).
2. Not ruled: a prot or heal let through with an interrupt ready as a fault of the attack's (+6.0, 8/10; not built);
   put to him with "Next" 1 as one of the things that wait.
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
