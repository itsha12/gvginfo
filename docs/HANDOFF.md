# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. `CLAUDE.md` is loaded already: read this, then only the section of
`docs/ENGINE_NOTES.md` named beside the item you take up. The plan is `docs/REDESIGN.md`, the definitions
`docs/DEFINITIONS.md`, the rulings `docs/RULINGS.md` (search it), the history `docs/CHANGELOG.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read docs/HANDOFF.md (CLAUDE.md is loaded automatically),
> check out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-25, morning: rulings to R-715; execution stages X1 to X4 built, X5 waits for his marks)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stages D and E) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored, each with its file beside it; 564 count (R-477); 506 matches
  trained. No workflow run in progress. The baseline (R-491): `baseline-2026-11-15`. Thirteen games graded and filed
  (set f1); no more matches until the engine is ready (R-570).
- Execution (the micro answer) is the block of work now (R-701 to R-715): plan in REDESIGN.md "Execution" (stages X1
  to X5), definitions in DEFINITIONS.md "Execution", build notes ENGINE_NOTES section 44. A fault is a missed chance,
  each kind checked once on unseen matches, none priced or ranked (R-713); which misses are listed (R-714, R-715).
- Stage X3 is complete (section 44): a prot, a heal and an interrupt on a spike skill missed by the defence may be
  told as faults; a missed strip reads backwards and pressure on the monks fails (never faults). A play's own
  outcome is read too (`cases.exec_own`, `cases.py execution` C2: a split holding, the defence killing a split
  player, a push stopping their flag, the flagger's team getting it in): 30 readings pass against 5, 2 and 3 by
  chance; the split's own damage and control read backwards; the two general outcomes as before (132 pass).
- Stage X4 is built (section 44): `flag_cost[rid].deaths` keeps every death of a player with the checked chances his
  team missed; each play's execution record names the deaths inside it, own and the enemy's apart
  (`execution.say_death`, `say_faults`); the death account follows R-715; the deaths recorded as the match ends are
  none. The site has Model > Game review > Execution (`data/model/execution_rows.json`, from `review.py execution`;
  his marks to `execution_row_marks.json`): Men v Crew, RACK v hdm and Men v NwAy set out, 46 deaths to mark.
- Last full run: 2026-11-25 at 7d1f0ab (33,089 plays identical to the X3 run; 323 Classic rows pass); the commit
  after it only moved a death's words out of the record. Rebuilt on it: `attempts_cases.json`, `execution_cases.json`.
  Not rebuilt since 2bebbc6: `npcpower.py bench`, the forensics benchmark, the other `cases.py` reports: at X5's run.

## Next (in order): execution before the close (REDESIGN.md "Execution"; R-571, R-572)
1. Stage X5: his marks on the Execution view (R-713). File them in the review key (`review.py file` does not read
   `execution_row_marks.json` yet: add it, set x1, his words kept) and rebuild at the root whatever he marks wrong
   (R-465); his answers to items 5 to 7 below first, since each may turn a reading round. Then the full run, truths,
   `npcpower.py bench`, the forensics benchmark, every `cases.py` report.
2. The flag readings he has seen, shown again on the new prices and flag tally: ENGINE_NOTES sections 15 and 22.
3. The close (sections 37 and 38; documents 34, readability 35, the causal map 41): the new families beside the old
   kinds for one rebuild (R-323), stand-in prices replaced by the win model, replaced kinds retired (`ask.py` and
   `learning.py` still import `tq.py`), the causal map cleaned, SPEC and METHODS rewritten, the readability test, his
   list of R-398 (left: items 1, 2, 3's remainder, 6, 7, 8 and 10), the merge, then one Train batch on the same 506
   matches (he starts it). With matches in: the split family again; the danger zone's two factors; the opening
   hand-off and held flags.

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand, with R-553 to build, and for a double run from the
   sender's side: raise them when more matches are trained.
1. R-713: Claude's handling of faults (missed chances, each kind checked once, none ranked) was put to him with the
   ruling; he had asked "Do you think we need the cost model?". His to turn round.
2. Skills from the wiki (R-398 item 6): he runs the site's "Update skills from the wiki" button between sessions;
   the next session reads `data/wiki_changes.json`.
3. The early September matches (R-673): raise it at R-398 and before a pull. R-576 and R-575 on Nomad's are
   Claude's readings: bring him what either tells wrongly.
4. Put to him 2026-11-25: a missed strip reads backwards and pressure on the monks shows nothing, so neither is told
   as a fault; of 388 prots stripped in the first 1.5 s only 26 came before the first big hit. Is a strip meant to
   land before the spike? His answer may turn the strip round (a reading to rebuild, not a threshold, R-465).
5. Put to him 2026-11-25: is an interrupt on a quarter-second cast (Death's Charge, Power Spike) or on an attack
   skill (Decapitate, Hammer Bash) a real chance? Development set: 31 and 114 of 637 such interrupt faults.
6. Put to him 2026-11-25: is a monk who is himself being killed at that moment available to prot or heal another
   (as R-711's busy monk is not)? 70 of 1,405 prot and heal faults are by a monk dead within 3 s.
7. Put to him 2026-11-25: a chance on a death with no spike is read from the heaviest 2 s on the player, sometimes
   long before he dies, and cannot be tested as spikes were (all died): his marks are its test. 626 of 10,218 deaths
   have no hit recorded on the player (degen, life steal); 170 of them list a chance, read from 2 s before the death.

## Running it
- Local engine: `git fetch --depth 1 --no-filter origin +replays:refs/remotes/origin/replays` (the files beside the
  replays come with it). `jobs.py`, `moments.py`, `casting.py`, the gate, the line-up and `confidence.py` need only
  Python; `cases.py` needs numpy and scikit-learn (no cache for its reports). On 2 cores and 7 GB: the development
  set about 6 minutes, a full run (`moments.py all`) about 27 with the machine to itself, `cases.py execution` about
  30 on its own (its shuffles), the other reports about 20 together (`ladder` before `test`, R-545; each kept with
  `--json data/model/<name>.json`). Set `PYTHONDONTWRITEBYTECODE=1`; never edit an engine file while a run is going
  (modules are imported late): build in a second, detached worktree meanwhile. Train batch: its workflow (`blind`
  stays no). The key, `dev_set.json`, `game_reviews.json` and the other views' rows are written on main.
- Site check: `python3 -m http.server`, then playwright with `/usr/bin/google-chrome`, api.github.com mocked.

## Cautions
- Never print or decode a sealed field in a chat. Don't merge `bundle-4` piecemeal (R-322). The branch's own
  `CLAUDE.md` and `docs/` are old copies: main's are kept up to date (its standing rules too).
