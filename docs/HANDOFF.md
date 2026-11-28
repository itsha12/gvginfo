# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. `CLAUDE.md` is loaded already: read this, then only the section of
`docs/ENGINE_NOTES.md` named beside the item you take up. The plan is `docs/REDESIGN.md`, the definitions
`docs/DEFINITIONS.md`, the rulings `docs/RULINGS.md` (search it), the history `docs/CHANGELOG.md`. For execution work
read `docs/EXECUTION.md` first: the catalogue of every why, its rules, and the order of work.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read docs/HANDOFF.md (CLAUDE.md is loaded automatically),
> check out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-28, after midnight: rulings to R-827; his marks of RACK v hdm and Men v NwAy actioned)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stages D and E) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored, each with its file beside it; 564 count (R-477); 506 trained.
  Baseline (R-491): `baseline-2026-11-15`. Thirteen games graded (set f1); R-570 holds.
- Execution (the micro answer) is the block of work (R-701 to R-827; `docs/EXECUTION.md`, 57 rules). Opus's full run
  at ccd0a55 reported (`docs/OPUS.md`): plays identical, 1,000 stands for too deep, monk following 450 not steady,
  the interrupt on spikes fails one group short (59 taken; 8/10), a block reads backwards, stance fails.
- His marks on the Execution view are in the review key (set x1): Men v Crew 15 deaths (R-811 to R-821), RACK v hdm
  10 and Men v NwAy 12 of 21 (R-822 to R-827), built on `bundle-4` 805b894 (ENGINE_NOTES section 44, last item, and
  EXECUTION.md Rules 52 to 57): cast times, heals that come later, Shame, Deep Wound left, what a prot did, the words.
- Last run: the development set at 805b894 (82 matches): plays and moments identical to the digest of ccd0a55, 323
  Classic rows pass; the attempts' prot and heal rows moved (the cast time). Main's `execution_rows.json` is from
  805b894 (three games, 46 deaths; written over the rows he marked, said to him).

## Next (in order, R-810)
1. His word on "Open for Denning" 1 to 3 (put to him in the chat of 2026-11-28). If a team mate's cast is no longer
   to excuse the other monks on a death: set `TEAM_MATE_EXCUSES` False in `execution.py` (built), file the ruling as
   amending R-715, run the development set, write the rows again, and change the page's "Done in time by a team
   mate" line (`assets/js/pages/review.js`). Nine deaths of Men v NwAy are not marked: his, if he wishes.
2. Then: "Full run wanted at <commit>" as the first line here (Opus's): `moments.py all`; `digest.py check` (the plays
   must not differ from ccd0a55's digest), `cases.py positions`, `attempts` (sections G and H: the interrupt on
   spikes, and prot and heal again, the cast time moved them), `pressure`, `execution`. Then bring him its verdicts:
   the interrupt on spikes if it still fails (R-744), stance, a block reading backwards.
3. Balling and Invoke Lightning: measure on the development set how far apart the record sets the hits of one cast
   on several players (`BALL_S` 0.15 misses Invoke's), then one change with his word (it moves play-level rows).
4. Then the flag readings shown again (sections 15, 22), then the close (sections 37, 38, 34, 35, 41): new families
   beside the old kinds for one rebuild (R-323), stand-in prices replaced, replaced kinds retired (`ask.py`,
   `learning.py` still import `tq.py`), SPEC and METHODS rewritten, the readability test, his list of R-398 (items
   1, 2, 3's remainder, 6, 7, 8, 10 left), the merge, one Train batch on the same 506 (he starts it).

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand (R-553 to build) and a double run from the sender's side.
1. R-715 on a death (the Mesmer at 6:15 of RACK v hdm: the Prot's Spirit Bond and Life Sheath are not listed, the 8
   Monk's Shielding Hands having landed). Off, 102 of the set's 1,619 deaths gain a prot line and 36 a heal line.
2. The front line (the Hammer at 2:04 of Men v NwAy): the most forward team mate in the fight who is no backline
   monk, there a Mesmer. Whether it is told from frontline characters alone is his (the cut-off is then read again).
3. A Shame that lands as the cast begins (the Hammer at 6:28 of RACK v hdm): no fault by Rule 1 as built (R-826).
4. Claude's readings in R-811 to R-817 and R-822 to R-827, his to correct; a dying monk's own spell on another player
   lost to Shame is a Trigger Fault on his row (new on Men v Crew 0:42). An even 6v6 and below has no row. The wiki
   sync: later (R-765). September's early matches (R-673): at R-398. R-576, R-575. The match report is parked.

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
  one match's deaths in words: `execution.py deaths <the whole report id>`.
  Site check: `python3 -m http.server`, then playwright with `/usr/bin/google-chrome`, api.github.com mocked.

## Cautions
- Never print or decode a sealed field in a chat. Don't merge `bundle-4` piecemeal (R-322). The branch's own
  `CLAUDE.md` and `docs/` are old copies: main's are kept up to date. `data/skills.json` is never edited by hand.
- `data/model/interrupt_worth.json` (branch) and `docs/EXECUTION.md`'s lists are one list: change both. Another chat
  may push to `bundle-4` (data files only): fetch before every push there.
