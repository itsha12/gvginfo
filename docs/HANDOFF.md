# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. `CLAUDE.md` is loaded already: read this, then only the section of
`docs/ENGINE_NOTES.md` named beside the item you take up. The plan is `docs/REDESIGN.md`, the definitions
`docs/DEFINITIONS.md`, the rulings `docs/RULINGS.md` (search it), the history `docs/CHANGELOG.md`. For execution work
read `docs/EXECUTION.md` first: the catalogue of every why, its rules, and the order of work.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read docs/HANDOFF.md (CLAUDE.md is loaded automatically),
> check out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-27, late night: rulings to R-821; his marks of Men v Crew actioned)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stages D and E) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored, each with its file beside it; 564 count (R-477); 506 trained.
  Baseline (R-491): `baseline-2026-11-15`. Thirteen games graded (set f1); R-570 holds.
- Execution (the micro answer) is the block of work (R-701 to R-821; `docs/EXECUTION.md`, 51 rules). Opus's full run
  at ccd0a55 reported (`docs/OPUS.md`): plays identical, 1,000 stands for too deep, monk following 450 not steady,
  the interrupt on spikes fails one group short (59 taken; 8/10), a block reads backwards, stance fails.
- He marked Men v Crew's 15 deaths (Execution view); the marks are in the review key (set x1) and his comments and
  the chat's are R-811 to R-821, built on `bundle-4` c477e8c (92de38e adds R-821's words) (ENGINE_NOTES section 44, last item): a prot listed
  only where it would have saved him, a heal the same on a spike; Divine Favor only with a heal of the skill's own;
  Shield Guardian not counted under Shadow Shroud; nine more disables by their text, Shame and Diversion not cast
  through, Arcane Thievery said on the monk; arrow flight 0.2 s; no monk in range and too fast before the hexes; one
  interrupt of a player on one spike; strips, the shield and the area damage before a burst on a death; the
  sentences in the match report's wording (`execution.death_lines`, `death_rulings`).
- Last run: the development set at c477e8c (82 matches): plays and moments identical to the digest of ccd0a55, 323
  Classic rows pass. Main's `execution_rows.json` is from 92de38e (three games, 46 deaths; Men v Crew's rows are
  written over the ones he marked, said to him; RACK v hdm and Men v NwAy not marked yet).

## Next (in order, R-810)
1. Stage X5: his marks on RACK v hdm and Men v NwAy (Model > Game review > Execution), and Men v Crew again if he
   wishes, on the rows of 92de38e. File them in the review key (set x1, as Men v Crew's are) the same session.
2. Full run wanted at 92de38e (Opus's), once his marks ask for no further change: `moments.py all`; `digest.py check`
   (the plays must not differ from ccd0a55's digest), `cases.py positions`, `attempts` (section G: the interrupt on
   spikes again, now with arrow flight and one interrupt a player; section H), `pressure`, `execution`. Then bring
   him its verdicts: the interrupt on spikes if it still fails (R-744), stance, a block reading backwards.
3. Balling and Invoke Lightning: measure on the development set how far apart the record sets the hits of one cast
   on several players (`BALL_S` 0.15 misses Invoke's), then one change with his word (it moves play-level rows).
4. Then the flag readings shown again (sections 15, 22), then the close (sections 37, 38, 34, 35, 41): new families
   beside the old kinds for one rebuild (R-323), stand-in prices replaced, replaced kinds retired (`ask.py`,
   `learning.py` still import `tq.py`), SPEC and METHODS rewritten, the readability test, his list of R-398 (items
   1, 2, 3's remainder, 6, 7, 8, 10 left), the merge, one Train batch on the same 506 (he starts it).

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand (R-553 to build) and a double run from the sender's side.
1. Claude's readings in R-811 to R-817, his to correct: a Shield Guardian cast under Shroud is not a prot landed
   either; each cast read alone; the two skills of a monk that give the most; Distracting Shot, Disrupting Chop,
   Magebane Shot, Signet of Distraction and Lyssa's Assault read as disables with his list.
2. A death's own change in win chance is small (about 2 points on the set: the death penalty alone). Said to him.
3. An even 6v6 and below has no row, as built. Skills from the wiki: the sync fixed later (R-765). September's
   early matches (R-673): at R-398. R-576, R-575. The match report is parked (`docs/OPUS.md`); its readings are built.

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
  The view's rows: `review.py execution <file> <main>/data/model/execution_rows.json 51683de9 d06ef3c7 c19f13e3`;
  one match's deaths in words: `execution.py deaths <report id>`.
  Site check: `python3 -m http.server`, then playwright with `/usr/bin/google-chrome`, api.github.com mocked.

## Cautions
- Never print or decode a sealed field in a chat. Don't merge `bundle-4` piecemeal (R-322). The branch's own
  `CLAUDE.md` and `docs/` are old copies: main's are kept up to date. `data/skills.json` is never edited by hand.
- `data/model/interrupt_worth.json` (branch) and `docs/EXECUTION.md`'s lists are one list: change both. Another chat
  may push to `bundle-4` (data files only): fetch before every push there.
