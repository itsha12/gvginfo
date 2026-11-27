# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. `CLAUDE.md` is loaded already: read this, then only the section of
`docs/ENGINE_NOTES.md` named beside the item you take up. The plan is `docs/REDESIGN.md`, the definitions
`docs/DEFINITIONS.md`, the rulings `docs/RULINGS.md` (search it), the history `docs/CHANGELOG.md`. For execution work
read `docs/EXECUTION.md` first: the catalogue of every why, its rules, and the order of work.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read docs/HANDOFF.md (CLAUDE.md is loaded automatically),
> check out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-27, early afternoon: rulings to R-790; execution stages X1 to X4 built; the catalogue's stages 1 to 4 built)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stages D and E) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored, each with its file beside it; 564 count (R-477); 506 trained.
  No workflow run in progress. Baseline (R-491): `baseline-2026-11-15`. Thirteen games graded (set f1); R-570 holds.
- Execution (the micro answer) is the block of work (R-701 to R-790). The catalogue, `docs/EXECUTION.md`, is the brief:
  a death is a sum, every why one part of it; 34 rules (rule n is R-(715+n) up to 28), sections A to D, five stages.
  Built before he checks anything: his marks on the Execution view (stage X5; 46 deaths on the site) wait (R-752).
- His answers on stage 4 are built (`bundle-4` 25047ff; ENGINE_NOTES section 44): the pressure line at 225 health
  (R-779); a burst that takes most of a player's health is a spike (R-780: two thirds of it and 200 or more, the
  share and the floor the engine's; `Forensics.spikes`, the record's `hurt`); the even 7v7's row (R-781); pact kills
  (`Forensics.pact_kill`) and no fault where nothing landed (R-783). R-782: "no attempt made" waits for the full run.
- Stage 3 is built with the tag file (`bundle-4` 116ef1a, the pact reading corrected in f93fd2c; 608 skills, his review R-769 to R-778): the tags read
  (interrupt reach and on demand, strips on demand, removals; untagged skills listed by the run); `triggers` (Bull's
  Strike, Harrier's Grasp, Empathy, Backfire, Shame, Diversion, Clumsiness, Ineptitude, Daze left on a monk) and
  `balling`, named on each play (R-745); `tagged_parts` on every kill attempt (the target's damage-raising skills,
  Deep Wound left on him, what a spike went into, Deep Wound on the spike, an attacker elsewhere), said in the sum.
  Not read: wards and spirits (not in the records); R-726 stays read over the play.
- Last run: the development set at f93fd2c (82 matches): 6,935 plays identical to c43c85a, 323 Classic rows pass;
  1,034 spikes of 400 and 1,944 bursts, 1,707 pressure attempts, 54 pact kills, 877 trigger rows, 773 times balled.
  Last full run: 7d1f0ab. Stale since: `attempts_cases.json`, `execution_cases.json`, `pressure_cases.json`, main's
  `execution_rows.json`. `cache` untouched. No new kind is checked on unseen matches yet.

## Next (in order, R-766): the catalogue, `docs/EXECUTION.md` "Order of work" (ENGINE_NOTES section 44)
1. One bundled build once he approves the rule for each prot (the list is with him, "Open" 1): what a missed prot
   would have stopped (R-784, R-785: each prot's own rule over the hits that landed, `is_prot` moved to the tags,
   "would he have lived" from the sum walked again); balling by nearby and in-the-area casts as faults (R-787); casts
   caught a fault only inside the kill attempt of a death, every player's count kept as context (R-789); a monk
   under R-711's pressure not available (R-790). Then the development set, the key, `compare.py`.
2. The one full run for stages 1 to 4 (R-766), the machine to itself: `cases.py pressure`, `attempts` and
   `execution` (do the three kinds still pass; each new kind checked once: the chances on a pressure attempt, the
   Deep Wound left, the stance, the triggers, balling; pact kills left out of "killed"; R-782's no attempt made),
   the key, the truths, `execution_rows.json` (the Execution view shows none of stage 1, 3 or 4 yet).
3. Stage 5: readings from positions (too deep, monk following, Flail lock, snared frontline, area damage, should have
   kited), then its own full run. Then X4's sentences on the full list, and stage X5: his marks.
4. After execution: the flag readings shown again (sections 15, 22), then the close (sections 37, 38, 34, 35, 41): new
   families beside the old kinds for one rebuild (R-323), stand-in prices replaced, replaced kinds retired (`ask.py`,
   `learning.py` still import `tq.py`), SPEC and METHODS rewritten, the readability test, his list of R-398 (items
   1, 2, 3's remainder, 6, 7, 8, 10 left), the merge, one Train batch on the same 506 (he starts it).

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand (R-553 to build) and a double run from the sender's side.
1. Put to him 2026-11-27 (early afternoon), in the chat: the one-line rule for each prot skill (the tags' 33 that
   stop damage on an ally, and Spirit Bond, Ballad of Restoration, Aura of Stability). His answer starts "Next" 1.
2. Claude's readings, his to correct: "at a death" (R-789) is inside the kill attempt that killed a player of the
   caster's team; the pressed monk's heals are left out as his prots are (R-790); a lasting ground effect stays
   "standing in area damage" (R-735), not balling (R-787). An even 6v6 and below has no row, as built.
3. R-746, set out again in full (he had forgotten it), Claude's reading: crits while moving and the extra damage of
   Protector's Strike, Harrier's Haste and Weaken Knees are context; "should have kited" is not told against Bull's
   Strike or Harrier's Grasp ready.
4. Skills from the wiki: the sync fixed later (R-765). September's early matches (R-673): at R-398. R-576, R-575.

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
