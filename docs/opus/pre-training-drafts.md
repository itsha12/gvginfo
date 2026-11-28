# Drafts for the pre-training list (R-398): items 2, 3 and 8

Opus's drafts, 28 November 2026, read from main at c6275db (rulings to R-842). Nothing here is ruled or done: each
item is a proposal for Denning to decide on, and for Fable to act on at the close (step 5 of the road ahead). Items 1,
6, 7 and 10 of the list are not drafted here (1 and 7 wait for the engine to settle; 6 is his wiki button; 10 waits on
more trained matches).

## Item 2: review the rulings

### Where the register stands
- 752 rulings, numbered R-001 to R-842 (90 numbers were never used or were folded into others, e.g. R-009 to R-019).
- `docs/DEFINITIONS.md` already holds the current definitions for counting players, flags, splits, collapse, the Lord
  push, the similar cases, the numbers advantage, energy, degen and execution (R-452).
- How much of each band of the register the current documents still cite (DEFINITIONS, EXECUTION, ENGINE_NOTES or
  REDESIGN):

| Rulings | In the register | Cited by a current document |
|---|---|---|
| R-001 to R-099 | 73 | 6 |
| R-100 to R-199 | 61 | 16 |
| R-200 to R-299 | 75 | 9 |
| R-300 to R-399 | 100 | 79 |
| R-400 to R-499 | 100 | 90 |
| R-500 to R-599 | 100 | 94 |
| R-600 to R-699 | 100 | 95 |
| R-700 to R-842 | 143 | 143 |

So 220 rulings are cited nowhere today, nearly all from before the redesign of 9 November (R-001 to R-299). They are
the ones to go through. The later rulings are already carried by a current document.

### Proposed sorting of the 220 uncited rulings
1. **GvG knowledge still true, to be carried into DEFINITIONS under new topics** (about 110). They were written as
   tactics for the old engine and say things about the game that have not changed. Proposed new topics:
   - *Which matches count*: R-001 to R-003, R-005 to R-007 (the 1 September line, strength on every result, game
     facts from every replay, commentary matches, transcripts never stored).
   - *The flag game, as he plays it*: R-020 to R-048 (up on flags, the 2Y cycle, backup flags, cap timing, the
     backside group while the runner is out, the cost of running by class, double and half runs, the 8 monk as
     runner, the first cap's disadvantage, who carries). Many are now carried by measured readings; each needs a
     line saying which reading replaced it, or kept as his word where none did.
   - *Fights, power plays and kills*: R-060 to R-095 (a power play is any numbers advantage, its window, healers only
     matter through damage, waiting for the res, after time, death penalty, judge a death by its cause first, Blind as
     time Blind, peel and defensive Mesmer play, spacing, the solo monk, spike anchors).
   - *Splits and collapse*: R-112 to R-130 (a spike build is answered by splitting, the lone ranger answered by the
     Mes/A plus a frontline collapse, the 8 monk defending, split depth, snare strength from the data).
   - *Pit NPCs and the Lord*: R-143 to R-158 (a knight worth about a death, knights first, Lord damage by build,
     protting own NPCs, footmen read as lost, teams resigning).
   - *Builds and strength*: R-170 to R-180 (matches are blind, spike and 8v8 builds, single skills change the play,
     matchups from data, gvg.report's Elo, healing-monk counts out, the map as a variable).
   - *Guild halls*: R-326, R-328, R-361 (footmen reach, Warrior's Isle's stand, map objects not yet).
2. **Rules of the retired engine, to be marked "retired with the old engine" at the merge** (about 60). They govern
   parts that bundle 4 replaces or that are already dropped: the TQs (R-204, R-206, R-231), training chunks and the
   learning report (R-004, R-089 to R-095, R-153 to R-156, R-208 to R-214), discovery and learned links (R-193 to
   R-197, R-209, R-210, R-218, R-265, R-276, R-278, R-286), the causal map and node chains (R-205, R-206, R-216,
   R-217), the blind test as designed in round 1 (R-284), and golden moments and their stories (R-338, R-345, R-420).
   The register keeps them (it is never renumbered); DEFINITIONS should not.
   Two need his word before they are marked: R-283 (kiting stays in the model whatever the data says) now sits
   against R-806 (should have kited removed from the execution reading); and R-215 (his link, Blind on the enemy
   frontline helps win the fight, kept to wait for more matches): bundle 4 reads Blind on their frontline only as a
   why on a kill attempt, so Fable should say whether the link itself survives.
3. **Rules about how Claude works, to be moved out of the register** (about 25). They are process, not GvG:
   R-190 to R-192, R-219 (the goal, no guessed weights, white box, process is code), R-230, R-233 to R-239 (the
   detailed why, every why from data, terms, Master of Damage, review format), R-266 to R-269 (one bundled change,
   diffs, the generated model page, the readability test), R-470, R-490, R-647, R-648, R-660, R-663 (process notes
   on drafts, marks and stored matches). Most are already in `CLAUDE.md` or `ENGINE_NOTES.md` in other words: the
   ruling's number would be cited there and the register line kept as the record.
4. **One-match notes now closed** (about 25): R-250 to R-254 (hdm v HC and BcS v Crew deaths), R-419, R-467, R-473,
   R-475, R-503, R-518, R-525, R-529, R-531, R-582. They were answers on rows that have since been rebuilt or graded
   again. Nothing to carry; R-254 (death rulings 3 to 5 in Men v HC "remain open") should be closed by his word.

### Smaller tidy-ups
- R-779 to R-842 (64 rulings, 27 and 28 November) all sit under one heading, "Rulings of 2026-11-27, midday". Split
  them under headings by session as the earlier ones are, so a search lands in the right place.
- 35 rulings carry an "amended by" or "withdrawn" note; DEFINITIONS should cite only the amending ruling for each.

### Recommendation
Do the sorting at the close in one Fable session, with this list as its starting point: carry group 1 into
DEFINITIONS (Opus can draft the lines), mark group 2 retired at the merge, cite group 3 from the process documents,
and close group 4. Put to Denning only R-283, R-215 and R-254, the three where his word is needed.

## Item 3: old, outdated or unneeded files (the rest of it)

Already done (24 November, PR #6): the old scraper, the old export, four merged map branches. Left for the close:

### Old engine data files (`data/model/`)
| File | Size | Still read by | Proposal |
|---|---|---|---|
| `lord_gvg.json` | 107 KB | nothing | delete now or at the close |
| `golden_stories.json` | 249 KB | the hidden Golden moments page | delete with that page |
| `blind_tests.json` | 103 KB | the hidden Blind test page, `advice.py` | keep until step 7 rebuilds the blind test, then delete |
| `usual_play.json` | 147 KB | `usual.py`, `learning.py`, `why.py`, `advice.py`, the Blind test page | delete as those modules retire |
| `advice_test.json` | 6 KB | `advice.py`, `learning.py` | delete as those retire |
| `discovery.json`, `discovery_history.json`, `discovery/` | 171 KB | the discovery modules and the Discovery workflow | delete with discovery, or keep if step 6's "Discovery resumes" reuses them |
| `behaviour.json` | 74 KB | `behaviour.py`, `learning.py` | delete as those retire |
| `link_log.json` | 375 KB | `learnednodes.py`, `learning.py` | delete with the learned links |
| `causal_map.json` | small | the causal map modules | delete with the causal map |
| `history/` | 3.5 MB | the learning reports | the largest; keep one archive copy on a branch, then delete |
| `reports/`, `nodes/` | 2.8 MB | old reports and node models | as above |

### Old engine modules (`tools/replay_analysis/`)
`tq.py` is still imported by `ask.py`, `learning.py`, `causalchain.py`, `lnrows.py`, `eventlayer.py` and `cache.py`.
The handoff already plans to retire them at the close. Note: removing a file from this folder changes the
measurement cache key, so it belongs inside the one rebuild (R-322), not before.

### Site pages and knowledge pages
- Golden moments and Blind test are hidden but still reached by direct link (`golden.js`, `blindtest.js`). Proposal:
  remove Golden moments at the close; keep Blind test until step 7 replaces it.
- Knowledge pages that describe the old engine: `behaviour.md`, `causal-map.md`, `discovery.md`,
  `learned-model.md`, `learning-report.md`, `values.md`, `wp-model.md`. These are item 7's to rewrite or remove.
- `docs/tests/readability-2026-11-09.md` and `...b.md`: the first readability tests. Keep as the record, or move to
  the CHANGELOG as one line each.

### Branches
| Branch | State | Proposal |
|---|---|---|
| `site-look` | merged to main (2fdf15e) | delete |
| `step-1-blind-and-maps` | merged to main | delete |
| `probe` | the gvg.report probe's output, last 24 November | keep (the workflow writes there) |
| `cache` | the engine's prepared data | keep (`cache.py sync`) |
| `baseline-2026-11-15` | the engine at the fresh start (R-491) | keep until the merge, then decide |
| `report-prototype` | the match report prototype | keep until step 8 |
| `guild-phone` | Opus's phone fix, waiting for his approval | merge or delete |

## Item 8: everything outstanding, in one list

### Waiting on Denning now
1. **A finish line for execution follow-ups.** Each full run turns up another kind that fails or reads backwards.
   Recommendation: after the run at f7165b1, a kind that still fails is kept as context or paused, as R-834 did for
   too deep, and read again once training resumes. (R-744 still holds: a fault he ruled by name is listed with the
   check beside it, never dropped.)
2. **Claude's readings in R-811 to R-841**: his to correct or let stand; rows written over his marks were all said
   to him.
3. **A prot or heal let through while an interrupt was ready, as the attack's fault**: +6.0 points, right in 8 of
   10 groups; not built.
4. **The nine unmarked deaths of Men v NwAy**: optional.
5. **The Execution view's how-to text**: out of date; may Opus edit it in `review.js`?
6. **A "Full run" GitHub workflow**: build it, and if so who.
7. **The guild page phone fix** (branch `guild-phone`): approve to merge.

### Held by his word, to come back later
8. **The flag-in-hand and double-run cards** (R-553, R-554): once more matches are trained. He asked to be reminded.
9. **The pre-September matches** (R-673): remove those before 1 or before 5 September, or keep; nothing goes until
   he says so. At the close.
10. **Shadow Shroud** (R-838): context for now, read again with more matches.
11. **Too deep and a monk following** (R-834): paused, kept on the records.
12. **Stages 2 to 4 of the decision to split at all**: wait for more matches (R-570).
13. **The match report** (R-800): parked until he starts it.
14. **The wiki sync's missing cast times** (R-765): later.

### No row or no reading yet
15. An even 6v6 or smaller has no row.
16. R-575 and R-576 (players walking through the Isle of Jade portal; a flag held at home) are named in the handoff's
    open list without what is open; Fable to say.
17. Three rulings that need his word at the rulings review (item 2 above): R-283, R-215, R-254.

