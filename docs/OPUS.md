# Opus's work alongside Fable

Denning runs two kinds of chat on this repo: Fable builds the engine; Opus does the work that needs no engine
judgement (full runs and their reports, documentation drafts, site pages, the readability test, training chunk
reports). The aims, in his order: 1) as little Fable usage as possible; 2) as much as possible done in parallel.

Only Opus writes this file. Fable reads the "For Fable" section alone, at the start of a session, and never edits
this file: anything Fable wants Opus to know goes in HANDOFF.md as it already does, which Opus reads.

## For Fable (at most 10 lines; Opus removes a line once it is acted on)
- The 97bac17 full run has reported (below, "Run reports"): `cases.py attempts` stops (R-460) because the interrupt on
  a spike skill now fails on unseen matches; the new kinds have no test in `cases.py`, so Opus read them once from a
  scratch script on the X3 yardstick (numbers in the report). The f2b8796 run is under way; it re-reads prot and heal.
- A full run no longer fits with two workers: `moments.py all` had a worker killed for memory 28 min in and hung; with
  `--jobs 1` it takes 38 min (HANDOFF "Running it" still says 27, two workers).
- Next time a full run is wanted: push `bundle-4`, write "Full run wanted at <commit>: <what to check>" as the first
  line of HANDOFF's "Next", and go on building. Opus's report lands under "Run reports" below. Opus pushes the
  run's `data/model/*_cases.json` to `bundle-4` (no engine file): fetch before every push there.
- Rulings Denning gave in an Opus chat, to be filed by Fable (numbering stays with Fable):
  - Family 5 (engage or wait) is dropped: the opening is captured in the flag family (R-520, R-590, R-611).
  - The one-click match report (his wish of 2026-11-23) to be added to REDESIGN.md as a planned item after step 3.
- The match report is parked (Denning, 2026-11-27): nothing to do for it until he starts it; its asks of Fable are under
  "Parked" below and move here then.

## Queued for Opus (newest last; Opus clears a line when done)
- Full run at `bundle-4` f2b8796 (HANDOFF "Next" 1, 2026-11-27 evening): stage 5's kinds and cut-offs (`cases.py
  positions`), prot, heal and interrupt as read since 6ebb141, the plays against the 97bac17 run. Under way.

## Parked (Denning starts each; neither chat acts on these until he asks)
- The match report (his one-click report on a match). Spec: the Docs artifact "GvG Info: match report spec" (layout
  agreed on the prototype, 2026-11-27). Prototype: branch `report-prototype` (`#/report/<match id>`; page
  `assets/js/pages/report.js`, data builder `tools/report/proto_build.py`, sample `data/report_proto/51683de9.json`,
  Men v Crew). When he starts it, in order:
  1. Opus builds the exporter (outside `tools/replay_analysis/`) from the output of the latest full run: one file per
     counted match on a `reports` branch; the page reads it in place of the prototype's file.
  2. Then, to "For Fable" above: Shadow Shroud on the target; their monks disabled or cast-prevented at the spike
     itself; the target's weapon set; every prot and heal ready and in reach named on a death, with energy; for a
     missed prot or heal what it would have stopped and the latest start that still saves him (`prot_would`); each
     death's change in win chance and the win chance at 0:00 if the run output lacks them. Then one review of the
     exporter by Fable.
  3. The page onto main, with buttons on Recent matches and a guild's results. Opus's pushes to main widen to the
     site pages it owns for this (Denning to confirm then).

## Ground rules for Opus
- Never edit: engine files on `bundle-4`, HANDOFF.md, RULINGS.md, DEFINITIONS.md, CHANGELOG.md, ENGINE_NOTES.md,
  EXECUTION.md, SPEC.md, REDESIGN.md. Those are Fable's; a change Opus thinks they need goes under "For Fable".
- Opus's own output: this file, drafts in `docs/opus/`, and a full run's output files (below).
- At the start of every Opus session: fetch main and `bundle-4`, read HANDOFF.md and the CHANGELOG entries and
  commit messages since the last log entry below, then this file.
- Before every push: fetch and rebase on the branch's newest commit. Push to main only the files above.
- Denning's preferences and CLAUDE.md's rules apply in full (explain in GvG terms; never print a sealed field).

## How Opus does a full run
1. Take the commit named under "Queued for Opus" or in HANDOFF ("Full run wanted at ..."), in a worktree of its own: the run reads that commit,
   never a branch that moves under it. Fetch the replays branch as HANDOFF's "Running it" says.
2. Run what HANDOFF names, one at a time (each needs the machine to itself): `moments.py all`, then the `cases.py`
   reports, the key (`review.py score` with main's key), the truths, and the rows for main's views. Compare with the
   last full run (`compare.py`). About 1.5 h in all on 2 cores. A chat's background job stops a few minutes after
   its reply ends, so the run stays inside one turn: started in the background, waited on in the foreground.
3. The output files go back where Fable would have put them: the `data/model/*_cases.json` reports to `bundle-4`
   (fetch and rebase first; those data files only, never an engine file), the views' rows to main. The run report
   names the commit they were made at, so Fable can tell whether they are stale.
4. Report under "Run reports": the commit, plays identical or not, Classic rows passing, each kind checked once on
   unseen matches (passes, fails, reads backwards) with its numbers, anything that stopped the run. A failed kind is
   reported, never fixed: the decision is Fable's and Denning's.

## Run reports (newest first)
### Full run at `bundle-4` 97bac17 (2026-11-27, Opus; stages 1 to 4)
- Made at 97bac17; `bundle-4` was at f2b8796 by the end, so prot and heal here are read before R-796, R-797 and R-802.
  Outputs: `pressure_cases.json`, `attempts_cases.json`, `execution_cases.json` (bundle-4 3dca405, data only);
  main's `execution_rows.json` (the three games as before: Men v Crew, RACK v hdm, Men v NwAy; engine 97bac17).
- What stopped: the first try hung (a worker killed for memory); run again with one worker, 38 min. `cases.py attempts`
  ended with an error by design (R-460): `FAULT_KINDS` names prot, heal and interrupt, and the test passes only two.
- Plays: 564 matches, no errors; 33,089 plays, identical to a full run of 7d1f0ab made beside it (none changed, gone or
  new). Key: 323 Classic rows pass; 6 history rows no longer hold (reported, block nothing). Truths: 15 of 15 hold.
- The three checked kinds on unseen matches (section G; killed less expected, points, 90% range, groups right):
  prot passes (taken 9,277 at 19.4% killed, missed 3,634 at 45.8%; -23.7, -25.4 to -22.3, 10/10; was -10.9);
  heal passes (8,731 at 18.2%, 2,084 at 58.5%; -40.8, -42.9 to -38.6, 10/10; was -43.0);
  interrupt on a spike skill FAILS (taken 158 at 25.3%, missed 7,418 at 27.5%; -6.1, -11.1 to -0.1, 6/10; on the
  11-25 run -17.8, 8/9 with 36 taken). The spike pool is now 17,061 (hurt bursts in, R-780) against 5,317.
  Strip fails (+0.1, 6/10; ruled a fault by R-744 whatever the check); pressure on their monks fails (-1.1, 5/10).
- Pressure line (`cases.py pressure`): the rule gives 150 health, kept 1 s, 1 landed (5,521 attempts, 35.3% die within
  8 s, 51.9% of the 4,567 deaths with no spike held); at his line, 225, 1 s, 90: 9,234 attempts, 21.9%, 56.4%. A spike
  kills 33.2% (17,061).
- The new kinds, read once by Opus with a scratch script on the same yardstick (`cases._x3_expected`, `_x3_diff`,
  `_x3_word`; not the engine's test, which has none for them): pact kills out of "killed" (12 attempts) changes
  nothing (prot -23.7, heal -40.8, interrupt -6.0, fails). Stance up on the target fails (282 with, 24.1% against
  33.4%; +1.8, 5/10). A spike into a block or immunity reads backwards (2,658; +2.2, 2/10). Deep Wound on him in time,
  against carried and not on him, fails (-1.0, 4/10). An attacker on another player reads backwards (3,790; +4.7,
  0/10). Deep Wound left with a removal ready, against Deep Wound on him and no removal missed, passes (1,412 at 53.5%
  against 3,389 at 27.9%; -31.7, 10/10). On pressure attempts (16,449): prot passes (-17.9, 10/10), heal passes
  (-29.4, 10/10), Deep Wound left passes (-20.0, 10/10).
- Counted, no test (ruled kinds or context): triggers 4,938 (Bull's Strike 2,087, Empathy 1,087, Shame 647, Daze left
  507, Harrier's 355, Backfire 182, Diversion 72, Clumsiness 1); balled 10,393 (nearby 5,454, adjacent 4,893, in the
  area 46; Energy Surge 4,100, a scythe 3,741, Lamentation 1,310); casts caught 17,699. R-782: question 3 is asked of
  11,598 plays (`asks_q3`); 6,139 of them made no kill attempt, neither spike nor pressure (in 519 matches).

## Starting a chat
- Opus: "Attach my repo itsha12/gvginfo with push access, clone it, check out `bundle-4` in a second worktree. You are
  the Opus chat: read docs/OPUS.md and follow its rules, then do what is queued for Opus."
- Fable: HANDOFF's own starter message, unchanged (CLAUDE.md sends it to "For Fable" here).

## Log (newest first)
- 2026-11-27: full run at 97bac17 reported; outputs pushed; the f2b8796 run started.
- 2026-11-27: match report: spec agreed with Denning (Docs), prototype on `report-prototype` (not main); parked until
  he starts it (see "Parked").
- 2026-11-27: set up (Denning's go-ahead). Plan of the remaining work: the Docs artifact "GvG Info: the road ahead".
