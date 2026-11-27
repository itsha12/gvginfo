# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. `CLAUDE.md` is loaded already: read this, then only the section of
`docs/ENGINE_NOTES.md` named beside the item you take up. The plan is `docs/REDESIGN.md`, the definitions
`docs/DEFINITIONS.md`, the rulings `docs/RULINGS.md` (search it), the history `docs/CHANGELOG.md`. For execution work
read `docs/EXECUTION.md` first: the catalogue of every why, its rules, and the order of work.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read docs/HANDOFF.md (CLAUDE.md is loaded automatically),
> check out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-27, evening: rulings to R-804; execution stages X1 to X4 built; the catalogue's stages 1 to 5 built)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stages D and E) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored, each with its file beside it; 564 count (R-477); 506 trained.
  Baseline (R-491): `baseline-2026-11-15`. Thirteen games graded (set f1); R-570 holds.
- Execution (the micro answer) is the block of work (R-701 to R-804). The catalogue, `docs/EXECUTION.md`, is the brief:
  a death is a sum, every why one part of it; 39 rules (rule n is R-(715+n) up to 28), sections A to D, five stages.
  Built before he checks anything: his marks on the Execution view (stage X5; 46 deaths on the site) wait (R-752).
- Stages 1 to 4 and his answers are built (ENGINE_NOTES section 44): the attempt and its sum, the pressure attempt
  (R-779), bursts (R-780), tags, triggers, balling, the prot amounts (R-791), R-796, R-797 and R-802.
- Stage 5, the readings from positions, is built (`bundle-4` f2b8796; R-803, R-804; ENGINE_NOTES section 44, last
  item). On the play's row (`flag_cost[rid].positions`, R-745): Flail lock (in Flail over 2 s, nothing within 250),
  standing in area damage (from his third hit of one cast, R-803), should have kited. On every kill attempt and
  death: `place` (too deep: 1,200 or more past his own front line, the most forward team mate who is no backline
  monk), `followed` (a monk 400 past it behind a too-deep player), `snared` (the attack's frontline slowed and out
  of reach: a why), `crits_moving` (context). The two cut-offs are the data's (`cases.py positions`, R-741). Too
  deep and monk following are whys, named faults only once they pass (`execution.POSITION_FAULTS`, R-713).
- Last run: the development set at f2b8796 (82 matches): 6,935 plays identical to 6ebb141, 323 Classic rows pass, no
  record differs but the new keys; 539 deaths with a prot fault, 389 with a heal fault (as before); 158 of 1,619
  deaths too deep (108 with no prot or heal fault), 163 Flail locks, 44 area rows, 878 should-have-kited rows.
  Checked once on the set: too deep fails like with like (+5.2 points), monk following fails, should have kited reads
  backwards (-9.4), the snared frontline passes as a why. Last full run: Opus's at 97bac17, no report yet. `cache` untouched.

## Next (in order, R-766): the catalogue, `docs/EXECUTION.md` "Order of work" (ENGINE_NOTES section 44)
1. Full run wanted at f2b8796: stage 5's kinds and cut-offs, and prot, heal and the Deep Wound left as they read
   since 6ebb141. (Opus's; it holds everything the 97bac17 run does, so it can stand in for that run if it has not
   reported.) `moments.py all`, the key, the truths, the plays against the 97bac17 run (none should differ); then
   `cases.py positions <file> --json data/model/positions_cases.json`: does the rule still give 1,200 and 400 on
   every counted match; section B's verdict for too deep, monk following, standing in area damage, should have
   kited (backwards on the set) and the snared frontline; section C's counts. `cases.py attempts`, `execution`,
   `pressure`: do prot, heal and interrupt still pass with a monk's own chance, taken means landed and too late.
2. On its report: set `POSITION_FAULTS` and the two cut-offs if the full set says otherwise (one change, the set
   run again); bring a ruled kind that reads backwards to him (R-744). Read the 97bac17 report if there is one.
3. X4's sentences on the full list (`cases.py` passes neither the stage 3 nor the stage 5 rows to `say_faults`
   yet), main's `execution_rows.json`, then stage X5: his marks on the Execution view.
4. After execution: the flag readings shown again (sections 15, 22), then the close (sections 37, 38, 34, 35, 41): new
   families beside the old kinds for one rebuild (R-323), stand-in prices replaced, replaced kinds retired (`ask.py`,
   `learning.py` still import `tq.py`), SPEC and METHODS rewritten, the readability test, his list of R-398 (items
   1, 2, 3's remainder, 6, 7, 8, 10 left), the merge, one Train batch on the same 506 (he starts it).

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand (R-553 to build) and a double run from the sender's side.
1. Put to him 2026-11-27 (evening), set out in the chat: (a) should have kited reads backwards on the set (an
   attempt on a player who stood still kills less often: 19.6% against 29.8%; 878 rows, most of one hit): keep it a
   fault as ruled, count it only inside a kill attempt on him, or make it context; (b) a backline monk 400 or more
   past his own front line with no too-deep player ahead of him (half such attempts kill, a quarter otherwise): a
   why of its own, or told only when he followed.
2. An even 6v6 and below has no row, as built.
3. Skills from the wiki: the sync fixed later (R-765). September's early matches (R-673): at R-398. R-576, R-575.
   The match report and its three readings are parked until he starts it (`docs/OPUS.md` "Parked").

## Running it
- Local engine: `git fetch --depth 1 --no-filter origin +replays:refs/remotes/origin/replays` (the files beside the
  replays come with it; about 150 MB). `jobs.py`, `moments.py`, `casting.py`, the gate, the line-up and
  `confidence.py` need only Python; `cases.py` needs numpy and scikit-learn (no cache for its reports). On 2 cores and
  7 GB: the development set about 6 minutes (`moments.py all <file> --dev`), a full run (`moments.py all`) about 27
  with the machine to itself, `cases.py execution` about 30 on its own, the other reports about 20 together (`ladder`
  before `test`, R-545; each kept with `--json data/model/<name>.json`). Set `PYTHONDONTWRITEBYTECODE=1`; never edit
  an engine file while a run is going (modules are imported late). After a change: `tools/golden/review.py score
  <file> --key <main>/data/model/review_key.json`, then `tools/golden/compare.py <before> <after>`.
  Site check: `python3 -m http.server`, then playwright with `/usr/bin/google-chrome`, api.github.com mocked.

## Cautions
- Never print or decode a sealed field in a chat. Don't merge `bundle-4` piecemeal (R-322). The branch's own
  `CLAUDE.md` and `docs/` are old copies: main's are kept up to date. `data/skills.json` is never edited by hand.
- `data/model/interrupt_worth.json` (branch) and `docs/EXECUTION.md`'s lists are one list: change both. Another chat
  may push to `bundle-4` (the tag file only): fetch before every push there.
