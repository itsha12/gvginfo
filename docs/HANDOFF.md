# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. `CLAUDE.md` is loaded already: read this, then only the section of
`docs/ENGINE_NOTES.md` named beside the item you take up. The plan is `docs/REDESIGN.md`, the definitions
`docs/DEFINITIONS.md`, the rulings `docs/RULINGS.md` (search it), the history `docs/CHANGELOG.md`. For execution work
read `docs/EXECUTION.md` first: the catalogue of every why, its rules, and the order of work.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read docs/HANDOFF.md (CLAUDE.md is loaded automatically),
> check out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-28, late morning: rulings to R-834; the four checks that still failed are diagnosed and put to him)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stages D and E) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored, each with its file beside it; 564 count (R-477); 506 trained.
  Baseline (R-491): `baseline-2026-11-15`. Thirteen games graded (set f1); R-570 holds.
- Execution (the micro answer) is the block of work (R-701 to R-834; `docs/EXECUTION.md`, 63 rules). His marks are
  in the review key (set x1): Men v Crew 15 deaths, RACK v hdm 10, Men v NwAy 12 of 21 (R-811 to R-830).
- The full run at 90223ed is read. Pass: the interrupt on spikes; a block (R-831: said above a third of attacks);
  the stance against the same players (R-832: Frenzied Defense only where spells landed). Too deep and monk
  following are paused (R-834: kept on the records, said nowhere, no work). R-833: as built.
- `bundle-4` 9ff24ab (one bundled change: R-831, R-832, R-834, section H's evidence rows): the development set's
  plays and moments identical to the digest, 323 Classic rows pass. `attempts_cases.json`: the 90223ed run's records,
  9ff24ab's `cases.py`. Main's `execution_rows.json` is 9ff24ab's (four rows he marked lost a Positioning line).
- Why the four fail (ENGINE_NOTES section 44, last item): the strip before the first big hit +6.8, 7/10, after it
  +0.3; a prot or heal of the monks' interrupted +10.0, 10/10; Shroud +10.1, 8/10; immunity is Aegis, unseen.

## Next (in order, R-810)
1. His answers to "Open for Denning" 1, then one bundled change: the strip (`chance_tests`: one before the first
   big hit that left no prot counts as done in time, an engine fault whatever he answers), the monks' interrupted
   prot or heal and knockdown as good play, and at his word the spike thrown (Aegis, from the casts aimed at him;
   the raw record first, R-707). Then "Full run wanted at <commit>" for Opus.
2. His marks on the nine deaths of Men v NwAy not yet marked, if he wishes; into the review key the same session.
3. Balling and Invoke Lightning: measure on the development set how far apart the record sets the hits of one cast
   on several players (`BALL_S` 0.15 misses Invoke's), then one change with his word (it moves play-level rows).
4. Then the flag readings shown again (sections 15, 22), then the close (sections 37, 38, 34, 35, 41): new families
   beside the old kinds for one rebuild (R-323), stand-in prices replaced, replaced kinds retired (`ask.py`,
   `learning.py` still import `tq.py`), SPEC and METHODS rewritten, the readability test, his list of R-398 (items
   1, 2, 3's remainder, 6, 7, 8, 10 left), the merge, one Train batch on the same 506 (he starts it).

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand (R-553 to build) and a double run from the sender's side.
1. Put to him 2026-11-28 (late morning), not answered: (a) the strip: in time only before the first big hit, one
   after it said as late (Claude's recommendation), or R-729 as it stands; (b) their monks: a prot or heal for the
   target interrupted and a monk knocked down said as the attack's good play (recommended), and whether a prot or
   heal let through with an interrupt ready is to be built as a fault (+6.0, 8/10 as it stands: by name, or not);
   (c) Aegis: build the spike thrown from the casts next, before balling (recommended), or later.
2. Claude's readings in R-811 to R-817, R-822 to R-830 and R-832, his to correct. Three rows he marked correct in
   RACK v hdm gained a line by R-828 (7:07, 7:33, 7:44 the 8 Monk): said to him.
3. An even 6v6 and below has no row. The wiki sync: later (R-765). September's early matches (R-673): at R-398.
   R-576, R-575. The match report is parked (`docs/OPUS.md`); its readings are built.

## For Opus (Fable never edits `docs/OPUS.md`)
- The guild page scrolls sideways at phone width (390 wide, about 85 px over): the "Most played full lineups"
  block (`.comp`). The two "For Fable" lines on family 5 and the match report are done (R-799, R-800).
- The Execution view's "How to read and mark a row" (`review.js`) is out of date (three kinds, the heaviest 2 s).
- "For Fable" line 1 is acted on; `attempts_cases.json` on `bundle-4` is 9ff24ab's (Fable's). No run wanted yet.
- Full runs: `moments.py all` now writes a match at a time and goes on where it stopped (run the same command
  again; `--fresh` starts over); a worker that dies stops it with an error. Use `digest.py` in place of a second
  full run for the comparison. A "Full run" GitHub workflow is offered to Denning, not built.

## Running it
- Local engine: `git fetch --depth 1 --no-filter origin +replays:refs/remotes/origin/replays` (the files beside the
  replays come with it; about 150 MB). `jobs.py`, `moments.py`, `casting.py`, the gate, the line-up and
  `confidence.py` need only Python; `cases.py` needs numpy and scikit-learn (no cache for its reports). On 2 cores and
  7 GB: the development set about 5.5 minutes (`moments.py all <file> --dev`), workers near 150 MB each; a full run
  should be near 35 with two workers and the machine to itself (not yet timed on the new code), `cases.py execution`
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
