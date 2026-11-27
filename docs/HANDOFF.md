# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. `CLAUDE.md` is loaded already: read this, then only the section of
`docs/ENGINE_NOTES.md` named beside the item you take up. The plan is `docs/REDESIGN.md`, the definitions
`docs/DEFINITIONS.md`, the rulings `docs/RULINGS.md` (search it), the history `docs/CHANGELOG.md`. For execution work
read `docs/EXECUTION.md` first: the catalogue of every why, its rules, and the order of work.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read docs/HANDOFF.md (CLAUDE.md is loaded automatically),
> check out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-27, midday: rulings to R-768; execution stages X1 to X4 built; the catalogue's stages 1 and 2 done)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stages D and E) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored, each with its file beside it; 564 count (R-477); 506 trained.
  No workflow run in progress. Baseline (R-491): `baseline-2026-11-15`. Thirteen games graded (set f1); R-570 holds.
- Execution (the micro answer) is the block of work (R-701 to R-768). The catalogue, `docs/EXECUTION.md`, is the brief:
  a death is a sum, every why is one part of it; 34 rules (rule n is R-(715+n) up to 28), the whys in sections A to D,
  the skill tags, the skills worth interrupting, the limits of the data, five stages. It is built before he checks
  anything: his marks on the Execution view (stage X5; 46 deaths set out on the site) wait (R-752).
- Stage 1 is built (`bundle-4` 4af6a49; ENGINE_NOTES section 44, last item): a monk's chance and an interrupt's on
  the new rules; every spike that did not kill listed with the strip missed (`execution.fails`; a fault by his
  ruling, the check beside it); casting into a ready interrupt read as R-743 says (`execution.caught`, the measure
  `into_ready`), listed on the play's row. A strip is told from the tags (`execution.tags`, `is_strip`).
- Stage 2 is done but for the wiki sync (R-765): `data/model/skill_tags.json` on `bundle-4` (its commit is da11306
  since 2026-11-27: a clone holding 37f10b4 fetches the branch again). 577 skills; his review's rulings R-753 to
  R-764. Being added in the other chat, where he reviews (R-767): who each skill lands on, a mark for a skill that
  raises its user's damage taken, R-738's snares marked, lasting ground effects, and 31 more skills.
- Last run: the development set at 4af6a49 (82 matches): 6,935 plays identical to 45ad7cf, 323 Classic rows pass; 690
  failed spikes, a strip missed at 7; 1,375 casts caught. Last full run: 7d1f0ab. Stale since: `attempts_cases.json`,
  `execution_cases.json`, main's `execution_rows.json` (it shows the reading before stage 1). `cache` branch untouched.

## Next (in order, R-766): the catalogue, `docs/EXECUTION.md` "Order of work" (ENGINE_NOTES section 44)
1. Stage 4: the ledger (each part of the sum a measured amount on every attempt, both teams, R-734); the pressure
   attempt beside the spike (a player kept in danger for a while, the cut-off from data, degen counted: R-741), which
   replaces the heaviest 2 s in the death accounts (R-749); the even 8v8's row (R-731). No full run.
2. Stage 3, with the tag file once its additions are in (fetch `bundle-4` first): Bull's knockdown, Harrier's Cripple,
   balling, Empathy and the other triggers, damage-raising stances (Primal Rage too, R-768), a spike into a block,
   ward or spirit, Deep Wound on the spike, an attacker on another target, R-725's and R-726's removals. Each join of
   a hit to a cast is checked first (R-707). An interrupt's reach and which strips are thrown on demand come from the
   tags (they catch Disrupting Chop); an untagged skill is counted and listed (R-767).
3. The one full run for stages 1 to 4 (R-766), the machine to itself: `cases.py attempts` and `execution` (do the
   three kinds still pass; each new kind checked once), the key, the truths, `execution_rows.json` (with the failed
   spikes and casts caught: the Execution view does not show them yet).
4. Stage 5: readings from positions (too deep, monk following, Flail lock, snared frontline, area damage, should have
   kited), then its own full run. Then X4's sentences on the full list, and stage X5: his marks.
5. After execution: the flag readings shown again (sections 15, 22), then the close (sections 37, 38, 34, 35, 41): new
   families beside the old kinds for one rebuild (R-323), stand-in prices replaced, replaced kinds retired (`ask.py`,
   `learning.py` still import `tq.py`), SPEC and METHODS rewritten, the readability test, his list of R-398 (left:
   items 1, 2, 3's remainder, 6, 7, 8, 10), the merge, one Train batch on the same 506 (he starts it).

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand (R-553 to build) and a double run from the sender's side.
1. Put to him 2026-11-27: casts caught are 13 a match. Each a fault (R-743 as built), or only at a death or spike?
2. R-746, Claude's reading, his to correct: crits while moving and the extra damage of Protector's Strike, Harrier's
   Haste and Weaken Knees are context, never faults; "should have kited" is not told against an attacker with Bull's
   Strike or Harrier's Grasp ready (where moving is the fault).
3. R-747 as built takes little (a spike on the monk himself at 5 deaths of the development set). Is a monk under
   lighter pressure himself (R-711's 250 in 2 s) also not available to another?
4. The speed-boost mark: 30 skills, 15 he ruled on and 15 by the same rule (none missed). His to confirm or trim.
5. Skills from the wiki (R-398 item 6): the sync fixed later (R-765), then he runs "Update skills from the wiki".
6. The early September matches (R-673): raise at R-398 and before a pull. R-576, R-575 (Nomad's): Claude's readings.

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
