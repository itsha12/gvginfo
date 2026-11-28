# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. `CLAUDE.md` is loaded already: read this, then only the section of
`docs/ENGINE_NOTES.md` named beside the item you take up. The plan is `docs/REDESIGN.md`, the definitions
`docs/DEFINITIONS.md`, the rulings `docs/RULINGS.md` (search it), the history `docs/CHANGELOG.md`. For execution work
read `docs/EXECUTION.md` first: the catalogue of every why, its rules, and the order of work.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read docs/HANDOFF.md (CLAUDE.md is loaded automatically),
> check out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-27, night: rulings to R-810; the catalogue built; the bundled change after the full run built)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stages D and E) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored, each with its file beside it; 564 count (R-477); 506 trained.
  Baseline (R-491): `baseline-2026-11-15`. Thirteen games graded (set f1); R-570 holds.
- Execution (the micro answer) is the block of work (R-701 to R-810; `docs/EXECUTION.md`, 45 rules). Opus's full run
  at f2b8796 reported (`docs/OPUS.md`); on it he ruled R-805 to R-809, and R-810 sets the order.
- Built on `bundle-4` 0a8cca9 (ENGINE_NOTES section 44, last item): too deep at 1,000 and monk following at 450
  (from the 564 matches); should have kited, standing in area damage and an attacker on another target are not read
  (R-806, R-807, R-809); a death is a spike (400 inside 3 s) or a burst on a hurt player, and the interrupt is a
  fault on a spike only (R-805, by his ruling: `FAULT_BY_RULING`); a skill the enemy disabled is not ready, no
  enchantment on a target under Shadow Shroud, no spell from a monk under Shame; on every attempt the set held,
  Shadow Shroud, his monks stopped, what landed for him; on every death what each missed prot, heal and interrupt
  would have done and the latest start that still saves him; the death's sentences in the match report's wording.
- `cases.py attempts` section H checks the stage 3 and 4 kinds; `cases.py winchance <file> --json <out>` gives the
  win chance over each match, at 0:00 and each death's change (for the match report's exporter; not kept in the repo).
- Last run: the development set at 0a8cca9 (82 matches): 6,935 plays and 5,420 records identical to f2b8796, 323
  Classic rows pass. Main's `execution_rows.json` is from 0a8cca9 (three games, 46 deaths, none marked yet).

## Next (in order, R-810)
1. Full run wanted at ccd0a55 (Opus's; engine 0a8cca9 plus the digest tool): `moments.py all` (two workers fit
   again); `tools/golden/digest.py check <file> data/model/plays_digest.json` (the 82 matches of the set must not
   differ), then `digest.py make` for every match, pushed; the key, the truths; `cases.py positions`, `attempts`
   (it should run to its end: read section G's interrupt on spikes alone, and every row of section H), `pressure`,
   `execution`; `cases.py winchance` once, to see it runs on every match. Report: do 1,000 and 450 stand; does the
   interrupt pass on spikes; which ruled kinds fail or read backwards (stance, Deep Wound left); a block, Shadow
   Shroud, a monk stopped.
2. Stage X5: his marks on the Execution view (46 deaths in three games; Model > Game review > Execution). The rows
   are written and wait for him (R-752 is met: the catalogue is built). Bring him the full run's verdicts with them.
3. On his marks and the report: one bundled change if they ask for one; then the flag readings shown again
   (sections 15, 22), then the close (sections 37, 38, 34, 35, 41): new families beside the old kinds for one
   rebuild (R-323), stand-in prices replaced, replaced kinds retired (`ask.py`, `learning.py` still import `tq.py`),
   SPEC and METHODS rewritten, the readability test, his list of R-398 (items 1, 2, 3's remainder, 6, 7, 8, 10
   left), the merge, one Train batch on the same 506 (he starts it).

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand (R-553 to build) and a double run from the sender's side.
1. Put to him 2026-11-27 (night): does a party-wide enchantment (Shield Guardian) land on a player under Shadow
   Shroud? Read as landing, so a Shield Guardian not cast is still a missed prot under Shroud.
2. A death's own change in win chance is small (about 2 points on the set: the death penalty alone, by the stand-in
   prices); the swing of the moment around it is on the decision cards. Said to him; his to change for the report.
3. An even 6v6 and below has no row, as built.
4. Skills from the wiki: the sync fixed later (R-765). September's early matches (R-673): at R-398. R-576, R-575.
   The match report is parked until he starts it (`docs/OPUS.md` "Parked"); its readings are built (R-810).

## For Opus (Fable never edits `docs/OPUS.md`)
- The guild page scrolls sideways at phone width (390 wide, about 85 px over): the "Most played full lineups"
  block (`.comp`). The two "For Fable" lines on family 5 and the match report are done (R-799, R-800).
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
  The view's rows: `review.py execution <file> <main>/data/model/execution_rows.json 51683de9 d06ef3c7 c19f13e3`.
  Site check: `python3 -m http.server`, then playwright with `/usr/bin/google-chrome`, api.github.com mocked.

## Cautions
- Never print or decode a sealed field in a chat. Don't merge `bundle-4` piecemeal (R-322). The branch's own
  `CLAUDE.md` and `docs/` are old copies: main's are kept up to date. `data/skills.json` is never edited by hand.
- `data/model/interrupt_worth.json` (branch) and `docs/EXECUTION.md`'s lists are one list: change both. Another chat
  may push to `bundle-4` (data files only): fetch before every push there.
