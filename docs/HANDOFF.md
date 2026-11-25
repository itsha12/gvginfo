# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. `CLAUDE.md` is loaded already: read this, then only the section of
`docs/ENGINE_NOTES.md` named beside the item you take up. The plan is `docs/REDESIGN.md`, the definitions
`docs/DEFINITIONS.md`, the rulings `docs/RULINGS.md` (search it), the history `docs/CHANGELOG.md`. For execution work
read `docs/EXECUTION.md` first: the catalogue of every why, its rules, and the order of work.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read docs/HANDOFF.md (CLAUDE.md is loaded automatically),
> check out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-25, midday: rulings to R-752; execution stages X1 to X4 built; the catalogue begun, stage 1 of 5)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stages D and E) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored, each with its file beside it; 564 count (R-477); 506 matches
  trained. No workflow run in progress. The baseline (R-491): `baseline-2026-11-15`. Thirteen games graded and filed
  (set f1); no more matches until the engine is ready (R-570).
- Execution (the micro answer) is the block of work (R-701 to R-752). The catalogue, `docs/EXECUTION.md`, is the brief:
  a death is a sum, every why is one part of it; 34 rules (rule n is R-(715+n) up to 28), the whys in sections A to D
  with what each needs, the skills worth interrupting, the limits of the data, five stages of work. It is built before
  he checks anything: his marks on the Execution view (stage X5; 46 deaths set out on the site) wait (R-752).
- Stages X1 to X4 as before (ENGINE_NOTES section 44): a prot, a heal and an interrupt on a spike skill are the kinds
  told as faults, at deaths; a play's execution record names the deaths inside it.
- The catalogue's stage 1, first piece, is built (`bundle-4` 45ad7cf): a monk's chance is read from 0.2 s after the
  first big hit, Daze and his own aftercast counted, a monk with a spike on himself no chance (R-716, R-747, R-748);
  an interrupt is a chance only on an approved skill (`data/model/interrupt_worth.json`), where the cast as the replay
  records it took the 0.2 s and the interrupt's own time (R-727, R-742, R-750).
- Last run: the development set only, at 45ad7cf: 6,935 plays identical to d7aacfe, 323 Classic rows pass; interrupt
  faults at deaths 637 to 383, prot 788 to 746, heal 617 to 565. Last full run: 7d1f0ab (33,089 plays). Stale since
  the change: `attempts_cases.json`, `execution_cases.json` (the verdicts behind `FAULT_KINDS`), `execution_rows.json`
  on main (the Execution view shows the reading before stage 1). The `cache` branch was not pulled or pushed.

## Next (in order): the catalogue, `docs/EXECUTION.md` "Order of work" (ENGINE_NOTES section 44)
1. Stage 1's remainder: failed spikes listed with the attack's misses, so the strip missed is told (a fault by his
   ruling, the check beside it: R-729, R-744, R-714); `into_ready` filtered by R-743 (interrupted casts of listed
   skills, backline). Then the checkpoint: a full run, `cases.py attempts` and `cases.py execution` again (do the
   prot, the heal and the interrupt still pass on unseen matches under the new reading?), `execution_rows.json` again.
2. Stage 2: fix the wiki sync's missing cast times (41 skills; `tools/wiki/sync.mjs`), then tag every skill in use by
   the part of the sum it acts on and its trigger, in a file of its own; he reviews the tagged list.
3. Stage 3: what the records already show (Bull's knockdown, Harrier's Cripple, balling, Empathy and the other
   triggers, damage-raising stances, a spike into a block, ward or spirit, Deep Wound on the spike, an attacker on
   another target, the removals of R-725 and R-726). Damage rows carry no skill: each join to a cast is checked first.
4. Stage 4: the ledger (each part of the sum an amount, R-734) and the pressure attempt (R-741, R-749); the even
   8v8's row (R-731). Stage 5: readings from positions (too deep, monk following, Flail lock, snared frontline, area
   damage, should have kited). Then X4's sentences on the full list, and stage X5: his marks.
5. After execution: the flag readings shown again (sections 15 and 22), then the close (sections 37, 38, 34, 35, 41):
   the new families beside the old kinds for one rebuild (R-323), stand-in prices replaced, replaced kinds retired
   (`ask.py` and `learning.py` still import `tq.py`), SPEC and METHODS rewritten, the readability test, his list of
   R-398 (left: items 1, 2, 3's remainder, 6, 7, 8 and 10), the merge, one Train batch on the same 506 (he starts it).

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand (R-553 to build) and a double run from the sender's side.
1. R-746, Claude's reading of "kiting should be no fault", his to correct: crits while moving and the extra damage of
   Protector's Strike, Harrier's Haste and Weaken Knees are counted as context, never told as faults; and "should have
   kited" is not told against an attacker with Bull's Strike or Harrier's Grasp ready (where moving is the fault).
2. R-747 as built takes little: on the development set a monk had a spike on himself (400 inside 3 s, from its first
   hit) at 5 deaths. Is a monk under lighter pressure himself (R-711's 250 in 2 s) also not available to another?
3. Skills from the wiki (R-398 item 6): the sync's missing cast times are fixed first (Next 2); then he runs the
   site's "Update skills from the wiki" button and the next session reads `data/wiki_changes.json`.
4. The early September matches (R-673): raise it at R-398 and before a pull. R-576 and R-575 on Nomad's are
   Claude's readings: bring him what either tells wrongly.
5. The skill audit (stage 2): he reviews the tagged list when it is drafted. No ruling now.

## Running it
- Local engine: `git fetch --depth 1 --no-filter origin +replays:refs/remotes/origin/replays` (the files beside the
  replays come with it; about 150 MB). `jobs.py`, `moments.py`, `casting.py`, the gate, the line-up and
  `confidence.py` need only Python; `cases.py` needs numpy and scikit-learn (no cache for its reports). On 2 cores and
  7 GB: the development set about 6 minutes (`moments.py all <file> --dev`), a full run (`moments.py all`) about 27
  with the machine to itself, `cases.py execution` about 30 on its own, the other reports about 20 together (`ladder`
  before `test`, R-545; each kept with `--json data/model/<name>.json`). Set `PYTHONDONTWRITEBYTECODE=1`; never edit
  an engine file while a run is going (modules are imported late). After a change: `tools/golden/review.py score
  <file> --key <main>/data/model/review_key.json`, then `tools/golden/compare.py <before> <after>`.
- One game's deaths in sentences: `python3 execution.py deaths <report id>`; its kill attempts: `execution.py attempts`.
- Site check: `python3 -m http.server`, then playwright with `/usr/bin/google-chrome`, api.github.com mocked.

## Cautions
- Never print or decode a sealed field in a chat. Don't merge `bundle-4` piecemeal (R-322). The branch's own
  `CLAUDE.md` and `docs/` are old copies: main's are kept up to date (its standing rules too).
- `data/model/interrupt_worth.json` (branch) and the lists in `docs/EXECUTION.md` (main) are one list: change both.
- `data/skills.json` is never edited by hand: the audit's tags go in a file of their own.
