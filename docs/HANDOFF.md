# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. `CLAUDE.md` is loaded already: read this, then only the section of
`docs/ENGINE_NOTES.md` named beside the item you take up. The plan is `docs/REDESIGN.md`, the definitions
`docs/DEFINITIONS.md`, the rulings `docs/RULINGS.md` (search it), the history `docs/CHANGELOG.md`. For execution work
read `docs/EXECUTION.md` first: the catalogue of every why, its rules, and the order of work.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read docs/HANDOFF.md (CLAUDE.md is loaded automatically),
> check out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-27, late afternoon: rulings to R-802; execution stages X1 to X4 built; the catalogue's stages 1 to 4 built)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stages D and E) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored, each with its file beside it; 564 count (R-477); 506 trained.
  Opus's full run for stages 1 to 4 was under way at 97bac17 (below). Baseline (R-491): `baseline-2026-11-15`. Thirteen games graded (set f1); R-570 holds.
- Execution (the micro answer) is the block of work (R-701 to R-802). The catalogue, `docs/EXECUTION.md`, is the brief:
  a death is a sum, every why one part of it; 37 rules (rule n is R-(715+n) up to 28), sections A to D, five stages.
  Built before he checks anything: his marks on the Execution view (stage X5; 46 deaths on the site) wait (R-752).
- His answers on stage 4 are built (`bundle-4` 25047ff; ENGINE_NOTES section 44): the pressure line at 225 health
  (R-779); a burst that takes most of a player's health is a spike (R-780: two thirds of it and 200 or more, the
  share and the floor the engine's; `Forensics.spikes`, the record's `hurt`); the even 7v7's row (R-781); pact kills
  (`Forensics.pact_kill`) and no fault where nothing landed (R-783). R-782: "no attempt made" waits for the full run.
- Stage 3 is built with the tag file (`bundle-4` 116ef1a, f93fd2c; 608 skills, his review R-769 to R-778): the tags,
  `triggers` and `balling` named on each play (R-745), `tagged_parts` on every kill attempt, said in the sum. Not
  read: wards and spirits (not in the records); R-726 stays read over the play.
- The prot amounts (`bundle-4` 97bac17; R-787, R-789 to R-791): `Forensics.hits_on`, `forensics.PROT_RULES` (his rule
  for each skill; Spirit Bond a prot), `execution.prot_would` (the sum walked again); a pressed monk; balling at
  every reach; casts caught a fault only at a death, `caught_by_player` the context.
- His answers on the prot amounts are filed and built (`bundle-4` 3111449, 6ebb141; ENGINE_NOTES section 44, last two items): a
  block stays at the average attack (R-794), "would he have lived" stays literal (R-795), Divine Favor's heal stays
  (R-798). A monk's own prot or heal on himself is a chance (R-796: the engine read his distance to himself, nought,
  as unknown; `chances`, the row's `self`, `can_self`). Taken means landed (R-797, amending R-715: `outcome`,
  `landed`, `Forensics.begun`; a death's `begun`), and a cast cut off by the death is its caster's fault where he had
  an earlier moment (R-802: `too_late`). The reaction stays 200 ms (R-801). Family 5 dropped (R-799); the match
  report planned (R-800).
- Last run: the development set at 6ebb141 (82 matches): 6,935 plays identical to 97bac17, 323 Classic rows pass;
  539 deaths with a prot fault (387 at 97bac17), 389 with a heal fault (245); 209 carry a row on the dying monk
  himself; 87 a too-late row. Last full run: Opus's at 97bac17, begun 2026-11-27 (its report: `docs/OPUS.md`
  "Run reports"; its cases files come to `bundle-4`): before 3111449 and 6ebb141, so its prot, heal and Deep Wound left figures
  are superseded and those kinds are read again at stage 5's full run; the rest of it stands. `cache` untouched.

## Next (in order, R-766): the catalogue, `docs/EXECUTION.md` "Order of work" (ENGINE_NOTES section 44)
1. Read Opus's report of the full run for stages 1 to 4 at 97bac17 (`docs/OPUS.md` "Run reports"; fetch `bundle-4`
   first: its cases files land there): the chances on a pressure attempt, the stance, the triggers, balling, pact
   kills, R-782's no attempt made, the key, the truths. Its prot, heal and Deep Wound left are before 3111449.
2. Stage 5: readings from positions (too deep, monk following, Flail lock, snared frontline, area damage, should have
   kited). When it is built, push and write "Full run wanted at <commit>: <what to check>" as the first line here
   (full runs are Opus's): stage 5's kinds, and prot, heal and the Deep Wound left as they read at 6ebb141 (a monk's
   own chance, taken means landed, too late). Then X4's sentences on the full list, and stage X5: his marks.
3. After execution: the flag readings shown again (sections 15, 22), then the close (sections 37, 38, 34, 35, 41): new
   families beside the old kinds for one rebuild (R-323), stand-in prices replaced, replaced kinds retired (`ask.py`,
   `learning.py` still import `tq.py`), SPEC and METHODS rewritten, the readability test, his list of R-398 (items
   1, 2, 3's remainder, 6, 7, 8, 10 left), the merge, one Train batch on the same 506 (he starts it).

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand (R-553 to build) and a double run from the sender's side.
1. Nothing put to him is waiting: R-794 to R-802 answer what was asked on the prot amounts.
2. An even 6v6 and below has no row, as built.
3. Skills from the wiki: the sync fixed later (R-765). September's early matches (R-673): at R-398. R-576, R-575.

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
