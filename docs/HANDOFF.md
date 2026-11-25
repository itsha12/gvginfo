# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. `CLAUDE.md` is loaded already: read this, then only the section of
`docs/ENGINE_NOTES.md` named beside the item you take up. The plan is `docs/REDESIGN.md`, the definitions
`docs/DEFINITIONS.md`, the rulings `docs/RULINGS.md` (search it), the history `docs/CHANGELOG.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read docs/HANDOFF.md (CLAUDE.md is loaded automatically),
> check out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-25, small hours: rulings to R-715; execution stages X1 to X3 built)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stages D and E) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored, each with its file beside it; 564 count (R-477); 506 matches
  trained. No workflow run in progress. The baseline (R-491): `baseline-2026-11-15`. Thirteen games graded and filed
  (set f1); no more matches until the engine is ready (R-570); nothing waits for his marks.
- Execution (the micro answer) is the block of work now (R-701 to R-715): plan in REDESIGN.md "Execution" (stages X1
  to X5), definitions in DEFINITIONS.md "Execution", build notes ENGINE_NOTES section 44. A fault is a missed chance,
  each kind checked once on unseen matches, none priced or ranked (R-713); which misses are listed (R-714, R-715).
- On the branch (stage E, step 2, then execution): the reader, flag returns, the Lord record, degen, energy, a backline
  monk by his bar (R-698), casting efficiency (R-704, section 43), stage X1 (`execution.py` over the whole play, ten
  measures from the old nodes; `tq.py` no longer under `lnrows.py`, `eventlayer.py`, `causalchain.py`) and stage X2
  (kill attempts with package, target state and missed chances; `forensics.chances`; death accounts with healed,
  recap, monk casting; interrupt attempts, target choice by objective, res, ground, conversion, water; R-706).
- Stage X3 built (section 44): the attempt record keeps the time of each strip, interrupt and knockdown, so taken and
  missed are read over the same 1.5 s. Checked on unseen matches, like with like: a prot, a heal and an interrupt on a
  spike skill missed by the defence pass (may be faults); a missed strip reads backwards and pressure on the monks
  fails (never faults). No together window shows a gain yet (R-708). Measures: 132 readings pass, about 8 by chance
  (bar set against shuffled records, `cases.X3_BUT`). Kept: `data/model/attempts_cases.json`, `execution_cases.json`.
- Last full run: the timed record, 2026-11-25 (33,089 plays, identical to the X2 run; 323 Classic rows pass). Not
  rebuilt since 2bebbc6: `npcpower.py bench`, the forensics benchmark, the other `cases.py` reports: all at X5's run.

## Next (in order): execution before the close (REDESIGN.md "Execution"; R-571, R-572)
1. X3's remainder: a split holding and a run capped or stopped read as their own outcomes in `exec_cases` (win points
   and net kills stand in now); the strip question below, if he turns it round.
2. Stage X4: the checked faults said on each play and death (R-714, R-715), the enemy's apart, each with what was
   there (the skill ready, the monk in reach) and the replay time; `spike_kill_share` and `dmg` as context only; an
   Execution view on the Game review.
3. Stage X5: he marks execution on two or three graded games (R-713); full run, truths, `npcpower.py bench`,
   forensics benchmark, every `cases.py` report.
4. The flag readings he has seen, shown again on the new prices and flag tally: ENGINE_NOTES sections 15 and 22.
5. The close (sections 37 and 38; documents 34, readability 35, the causal map 41): the new families beside the old
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

## Running it
- Local engine: `git fetch --depth 1 --no-filter origin +replays:refs/remotes/origin/replays` (the files beside the
  replays come with it). `jobs.py`, `moments.py`, `casting.py`, the gate, the line-up and `confidence.py` need only
  Python; `cases.py` needs numpy and scikit-learn (no cache for its reports). On 2 cores and 7 GB: the development
  set about 6 minutes, a full run (`moments.py all`) about 30 with the machine to itself, the fourteen `cases.py`
  reports about 20 (`ladder` before `test`, R-545; each kept with `--json data/model/<name>.json`). Set
  `PYTHONDONTWRITEBYTECODE=1`; never edit an engine file while a run is going (modules are imported late). Train
  batch: its workflow (`blind` stays no). The key, `dev_set.json` and `game_reviews.json` are written on main.
- Site check: `python3 -m http.server`, then playwright with `/usr/bin/google-chrome`, api.github.com mocked.

## Cautions
- Never print or decode a sealed field (blind picks, golden moments) in a chat. Don't merge `bundle-4` piecemeal
  (R-322). The branch's own `CLAUDE.md` and `docs/` are old copies: main's are the ones kept up to date.
- The standing rules on the files the site saves, hall labels, party slots and transcripts are in `CLAUDE.md`.
