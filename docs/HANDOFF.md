# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. `CLAUDE.md` is loaded already: read this, then only the section of
`docs/ENGINE_NOTES.md` named beside the item you take up. The plan is `docs/REDESIGN.md`, the definitions
`docs/DEFINITIONS.md`, the rulings `docs/RULINGS.md` (search it), the history `docs/CHANGELOG.md`. For execution work
read `docs/EXECUTION.md` first: the catalogue of every why, its rules, and the order of work.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read docs/HANDOFF.md (CLAUDE.md is loaded automatically),
> check out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-27, afternoon: rulings to R-768; execution stages X1 to X4 built; the catalogue's stages 1, 2 and 4 done)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stages D and E) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored, each with its file beside it; 564 count (R-477); 506 trained.
  No workflow run in progress. Baseline (R-491): `baseline-2026-11-15`. Thirteen games graded (set f1); R-570 holds.
- Execution (the micro answer) is the block of work (R-701 to R-768). The catalogue, `docs/EXECUTION.md`, is the brief:
  a death is a sum, every why one part of it; 34 rules (rule n is R-(715+n) up to 28), sections A to D, five stages.
  Built before he checks anything: his marks on the Execution view (stage X5; 46 deaths on the site) wait (R-752).
- Stage 4 is built (`bundle-4` c43c85a; ENGINE_NOTES section 44, last item). The ledger: every kill attempt, death and
  failed spike carries the sum as amounts (`ledger`: health in points, what landed by kind, what was healed, the end,
  what the parts leave over; what was stopped from gvg.report's recap), every missed chance what a cast of that skill
  gave that player this match (R-734). The pressure attempt (`flag_cost[rid].pressure`: at or under 175 health for 1 s
  or longer with 90 landing in 3 s; the cut-offs from `cases.py pressure`, `data/model/pressure_cases.json`) reads the
  deaths with no spike: the heaviest 2 s is gone (R-749). Question 3 on every play to kill and every numbers
  advantage, the enemy's credit apart (R-732, R-733). The even 8v8's rows (`flag_cost[rid].even`, R-731).
- Stage 1 was built before it (4af6a49). Stage 2 is done but for the wiki sync (R-765): `data/model/skill_tags.json`,
  608 skills since d345505 (the other chat, R-767: `on`, `takes_more`, `not_snare`, `lasting`; it may push again).
- Last run: the development set at c43c85a (82 matches): 6,935 plays identical to 4af6a49, 323 Classic rows pass; 1,778
  pressure attempts; of 1,619 deaths 344 by spike, 613 kept in danger, 662 neither; 74 even 8v8 rows. Last full run:
  7d1f0ab. Stale since: `attempts_cases.json`, `execution_cases.json`, main's `execution_rows.json`. `cache` untouched.

## Next (in order, R-766): the catalogue, `docs/EXECUTION.md` "Order of work" (ENGINE_NOTES section 44)
1. Stage 3, with the tag file (fetch `bundle-4` first): Bull's knockdown, Harrier's Cripple, balling, Empathy and the
   other triggers, damage-raising stances (Primal Rage too, R-768), a spike into a block, ward or spirit, Deep Wound
   on the spike, an attacker on another target, R-725's and R-726's removals. Each join of a hit to a cast checked
   first (R-707). An interrupt's reach and the strips thrown on demand from the tags (they catch Disrupting Chop); an
   untagged skill counted and listed (R-767). Each new part is said in the sum (`say_ledger`).
2. The one full run for stages 1 to 4 (R-766), the machine to itself: `cases.py pressure` (do the cut-offs still
   follow), `attempts` and `execution` (do the three kinds still pass; each new kind checked once, the chances on a
   pressure attempt among them), the key, the truths, `execution_rows.json` (the Execution view shows no sum, failed
   spike, cast caught, pressure attempt or even row yet).
3. Stage 5: readings from positions (too deep, monk following, Flail lock, snared frontline, area damage, should have
   kited), then its own full run. Then X4's sentences on the full list, and stage X5: his marks.
4. After execution: the flag readings shown again (sections 15, 22), then the close (sections 37, 38, 34, 35, 41): new
   families beside the old kinds for one rebuild (R-323), stand-in prices replaced, replaced kinds retired (`ask.py`,
   `learning.py` still import `tq.py`), SPEC and METHODS rewritten, the readability test, his list of R-398 (items
   1, 2, 3's remainder, 6, 7, 8, 10 left), the merge, one Train batch on the same 506 (he starts it).

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand (R-553 to build) and a double run from the sender's side.
1. Put to him 2026-11-27 (stage 4), each set out in the chat: (a) the pressure line, Claude's rule (as dangerous as a
   spike: 175 health, 1 s, 90 in 3 s); (b) the 662 deaths that are neither a spike nor kept in danger (a hurt player,
   a middle 232 health, finished with 195 in 1.4 s): is a burst that takes most of his health a spike; (c) "8v8" to
   the letter, or even numbers with both runners away too; (d) a job to kill with no kill attempt made (69% of such
   plays): a play-level fault of its own; (e) the 113 deaths with nothing landed in the record: list no fault there.
2. Put to him 2026-11-27 (stage 1): casts caught are 13 a match. Each a fault (R-743 as built), or only at a death?
3. R-746, Claude's reading, his to correct: crits while moving and the extra damage of Protector's Strike, Harrier's
   Haste and Weaken Knees are context; "should have kited" is not told against Bull's Strike or Harrier's Grasp ready.
4. R-747 as built takes little (5 deaths, development set). Is a monk under R-711's 250 in 2 s also not available?
5. The speed-boost mark: 30 skills, 15 he ruled on and 15 by the same rule (none missed). His to confirm or trim.
6. Skills from the wiki: the sync fixed later (R-765). September's early matches (R-673): at R-398. R-576, R-575.

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
