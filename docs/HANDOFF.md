# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. `CLAUDE.md` is loaded already: read this, then only the section of
`docs/ENGINE_NOTES.md` named beside the item you take up. The plan is `docs/REDESIGN.md`, the definitions
`docs/DEFINITIONS.md`, the rulings `docs/RULINGS.md` (search it), the history `docs/CHANGELOG.md`. For execution work
read `docs/EXECUTION.md` first: the catalogue of every why, its rules, and the order of work.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read docs/HANDOFF.md (CLAUDE.md is loaded automatically),
> check out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-28, midday: rulings to R-838; the strip, their monks and Aegis built and checked on a full run)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stages D and E) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored, each with its file beside it; 564 count (R-477); 506 trained.
  Baseline (R-491): `baseline-2026-11-15`. Thirteen games graded (set f1); R-570 holds.
- Execution (the micro answer) is the block of work (R-701 to R-838; `docs/EXECUTION.md`, 67 rules). His marks are
  in the review key (set x1): Men v Crew 15 deaths, RACK v hdm 10, Men v NwAy 12 of 21 (R-811 to R-830).
- `bundle-4` 59c47b0, with Fable's own full run at it (plays and moments identical to the digest on all 564; 323
  Classic rows pass on the set; `attempts_cases.json` and main's `execution_rows.json` are from it). ENGINE_NOTES
  section 44's last three items hold every figure. Built today: a block said above a third of attacks (R-831);
  Frenzied Defense only where spells landed (R-832); too deep and monk following paused (R-834); the strip that
  matters (R-835); the attack's good play on their monks (R-836); the spike thrown and Aegis (R-837).
- The checks: the interrupt on spikes, a block, the stance, a monk's cast stopped (+10.0) pass. The strip: before
  the first big hit +5.8, 7/10; taking a prot or heal that landed during it +8.3 on spikes, +3.7 on bursts, both
  9/10. A monk down +8.1, 7/10. Aegis coming during a spike thrown: 1.7% died against 22.4%. Shroud waits (R-838).
- A kind is tested against its own like: never with what it changes held level; a strip against what it could take.

## Next (in order, R-810)
1. His answers to "Open for Denning" 1, built with: the time of death on a spike thrown (so section J reads Aegis
   against targets still alive), `good` on a death read from a pressure attempt, the spike thrown said on the
   play's row, the "Success:" line's order made the same from run to run. Then "Full run wanted at <commit>".
2. His marks on the nine deaths of Men v NwAy not yet marked, if he wishes; into the review key the same session.
3. Balling and Invoke Lightning: measure on the development set how far apart the record sets the hits of one cast
   on several players (`BALL_S` 0.15 misses Invoke's), then one change with his word (it moves play-level rows).
4. Then the flag readings shown again (sections 15, 22), then the close (sections 37, 38, 34, 35, 41): new families
   beside the old kinds for one rebuild (R-323), stand-in prices replaced, replaced kinds retired (`ask.py`,
   `learning.py` still import `tq.py`), SPEC and METHODS rewritten, the readability test, his list of R-398 (items
   1, 2, 3's remainder, 6, 7, 8, 10 left), the merge, one Train batch on the same 506 (he starts it).

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand (R-553 to build) and a double run from the sender's side.
1. Put to him 2026-11-28 (midday), not answered: (a) on a spike a strip dealing no damage that takes a prot or heal
   during it is not counted by R-835 and reads strongest (+14.5, 9/10): count it (recommended); (b) a damaging
   strip counts today whatever it took: only where it took a prot or heal (recommended); (c) where the spike
   thrown is to be said (the play's row, a row of its own on the Execution view); (d) his sentence that broke off.
2. Claude's readings in R-811 to R-817, R-822 to R-830, R-832, R-835 and R-837, his to correct. Three rows he marked
   correct in RACK v hdm gained a line by R-828 (7:07, 7:33, 7:44 the 8 Monk): said to him.
3. An even 6v6 and below has no row. The wiki sync: later (R-765). September's early matches (R-673): at R-398.
   R-576, R-575. The match report is parked (`docs/OPUS.md`); its readings are built.

## For Opus (Fable never edits `docs/OPUS.md`)
- The guild page scrolls sideways at phone width (390 wide, about 85 px over): the "Most played full lineups"
  block (`.comp`). The two "For Fable" lines on family 5 and the match report are done (R-799, R-800).
- The Execution view's "How to read and mark a row" (`review.js`) is out of date (three kinds, the heaviest 2 s).
- "For Fable" line 1 is acted on; `attempts_cases.json` on `bundle-4` is 59c47b0's (Fable's run). No run wanted yet.
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
