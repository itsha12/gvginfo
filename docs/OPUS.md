# Opus's work alongside Fable

Denning runs two kinds of chat on this repo: Fable builds the engine; Opus does the work that needs no engine
judgement (full runs and their reports, documentation drafts, site pages, the readability test, training chunk
reports). The aims, in his order: 1) as little Fable usage as possible; 2) as much as possible done in parallel.

Only Opus writes this file. Fable reads the "For Fable" section alone, at the start of a session, and never edits
this file: anything Fable wants Opus to know goes in HANDOFF.md as it already does, which Opus reads.

## For Fable (at most 10 lines; Opus removes a line once it is acted on)
- The ccd0a55 full run has reported (HANDOFF "Next" 1 is done; outputs bundle-4 0dbc722, digest for all 564 matches):
  plays identical on the 82 of the digest; too deep 1,000 stands (1,000 or 950 in every group) but fails as a why
  (+1.9, 6/10); monk following 450 is unstable again (0 in five groups) and fails (+5.6, 7/10); `attempts` now runs to
  its end; the interrupt on spikes fails narrowly (59 taken, -15.5, -23.3 to -6.5, 8/10: one group short), for
  Denning by R-744; a block reads backwards, stance fails; Deep Wound left passes. Numbers under "Run reports".
- Two workers fit again: `moments.py all --jobs 2` took 30 min, workers near 290 MB, no kill. `cases.py pressure`
  10 min, `execution` 25 min, the rest under a minute each.
- Next time a full run is wanted: push `bundle-4`, write "Full run wanted at <commit>: <what to check>" as the first
  line of HANDOFF's "Next", and go on building. Opus's report lands under "Run reports" below. Opus pushes the
  run's `data/model/*_cases.json` to `bundle-4` (no engine file): fetch before every push there.
- Rulings Denning gave in an Opus chat, to be filed by Fable (numbering stays with Fable):
  - Family 5 (engage or wait) is dropped: the opening is captured in the flag family (R-520, R-590, R-611).
  - The one-click match report (his wish of 2026-11-23) to be added to REDESIGN.md as a planned item after step 3.
- The match report is parked (Denning, 2026-11-27): nothing to do for it until he starts it; its asks of Fable are under
  "Parked" below and move here then.
- The site's look and pages changed (Opus, main 4c54818 to 2fdf15e): `index.html`, `assets/app.css`, `assets/js/app.js`,
  `schedule.js`, and the pages `home.js`, `guilds.js`, `builds.js`, `skills.js`, `knowledge.js`, `settings.js`, new
  `profile.js`. `review.js` and `golden.js` untouched. The match search is now one piece (`home.js` `matchList`) used
  by Recent matches, guild and player pages. Rebase any branch of yours that touches these files.

## Queued for Opus (newest last; Opus clears a line when done)
(none)

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
  3. The page onto main. The Match report buttons are already on every match row (main 2fdf15e) and open
     `#/report/<match id>`, for now a "not built yet" page (`home.js` `renderReportPending`); the real page takes
     that route over.

## Ground rules for Opus
- Never edit: engine files on `bundle-4`, HANDOFF.md, RULINGS.md, DEFINITIONS.md, CHANGELOG.md, ENGINE_NOTES.md,
  EXECUTION.md, SPEC.md, REDESIGN.md. Those are Fable's; a change Opus thinks they need goes under "For Fable".
- Opus's own output: this file, drafts in `docs/opus/`, a full run's output files (below), and the site's styling and
  pages: `index.html`, `assets/app.css` and `assets/js/`, except `assets/js/pages/review.js` and `golden.js` (the
  Game review and Execution views, Fable's). Site work is done on a branch and goes to main only once Denning approves.
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
### Full run at `bundle-4` ccd0a55 (2026-11-27, night, Opus; engine 0a8cca9 plus the digest tool)
- Outputs: `positions_cases.json`, `attempts_cases.json`, `execution_cases.json`, `plays_digest.json` for all 564
  matches (bundle-4 0dbc722, data only; `pressure_cases.json` came out identical). Main's `execution_rows.json` not
  made again: the engine is that of 0a8cca9, which made it. `winchance` ran on all 564 (47,917 positions, 10,215
  deaths priced; a death -1.9 points on average; 400 positions blank where a hall's walks cannot be read); not kept.
- Plays: 564 matches, no errors, 33,089 plays and 26,199 moments; `digest.py check`: the 82 of the set identical.
  Key: 323 Classic rows pass (6 history rows do not hold, as before). Truths: 15 of 15 hold. Self-check (R-488): 6
  times a player in two fights at once for 12 s or more, in 4 matches. 134 untagged skills on bars in 112 matches.
- Positions (26,944 attempts, 32.3% killed): too deep, the rule 1,000 (1,588 at or past it, 46.5% killed; 25.9%
  short), 1,000 or 950 in every group left out: the engine's 1,000 stands. Monk following, the rule 450 (1,670 at
  48.5%; 29.3% short) but 0 in five of the ten groups left out: not stable. Section B on spikes, like with like: too
  deep fails (2,227 with; +1.9, -0.3 to +4.2, 6/10); monk following fails (355; +5.6, +0.8 to +10.4, 7/10); the
  attack's frontline snared passes (-12.3, 10/10). Area damage and kiting not read (R-806, R-807). Flail lock: 413 rows
  in 20 matches.
- Attempts (section G, now to its end): prot passes (8,626 taken at 15.8% killed, 4,523 missed at 49.5%; -28.0,
  10/10); heal passes (-44.4, 10/10); interrupt on a spike of 400 or more (R-805) fails, one group short (59 taken at
  18.6%, 2,981 missed at 29.4%; -15.5, -23.3 to -6.5, 8/10; was -6.1, 6/10 with 158 taken); strip fails (+0.1);
  pressure on their monks fails (-1.1). H1: stance fails (+1.8, 5/10; a fault by ruling); a block against attacks reads
  backwards (2,369; +2.7, 2/10); spell immunity fails (37; +10.2); Deep Wound carried and not on him in time passes
  (-5.8, 10/10); Deep Wound left with a removal ready passes (+26.2, 10/10); Shadow Shroud on him fails (315; +3.6,
  5/10; context); a monk of his stopped at the spike fails (2,190; +4.6, +2.9 to +6.3, 8/10; context). H2: the
  interrupt on a hurt-player burst fails (+0.1; not a fault by R-805). H3, kept in danger: prot passes (+19.6), heal
  passes (+30.1), Deep Wound left passes (+18.2), all 10/10.
- Pressure line: as before (the rule 150, 1 s, 1 landed; his 225 holds 56.4%). Execution (C): 135 pass, 720 fail,
  102 read backwards, 59 mark the situation, 240 no direction, 248 too few (2, 16, 10 pass on shuffled records).
### Full run at `bundle-4` f2b8796 (2026-11-27, Opus; stage 5, and prot and heal since 6ebb141)
- Outputs: `positions_cases.json`, `pressure_cases.json`, `attempts_cases.json`, `execution_cases.json` (bundle-4
  85d8294, data only; made at f2b8796). No `execution_rows.json`: "Next" 3 makes it after X4's sentences.
- Plays: 564 matches, no errors; 33,089 plays, identical to the 97bac17 run. Key: 323 Classic rows pass (6 history
  rows no longer hold, as before). Truths: 15 of 15 hold. `moments.py all` 53 min with one worker.
- Stage 5 cut-offs (`cases.py positions`, R-741), 26,944 kill attempts (17,061 spikes, 9,883 kept in danger), 32.3%
  killed. Too deep: the rule gives 1,000 (1,588 attempts at or past it, 46.5% killed; 25.9% short of it), 1,000 or 950
  in every group left out; the engine's 1,200 gives 1,141 at 49.8%. Monk following: the rule gives 450 (1,670 at
  48.5%; 29.3% short), but 0 in five of the ten groups left out; the engine's 400 gives 1,801 at 47.7%. The report
  says of both: not the rule's cut-off on this file.
- Section B (killed less expected on spikes, like with like): too deep fails (1,597 with, 52.0% against 31.1%; +3.1,
  +0.5 to +5.5, 6/10); monk following fails (278; +5.6, -0.1 to +11.8, 7/10); standing in area damage reads backwards
  (88, 13.6% against 32.4%; -13.8, 1/10); should have kited reads backwards (1,131, 28.1% against 32.5%; -5.2, -7.1 to
  -3.0, 1/10; the set said -9.4); the attack's frontline snared passes as a why (1,724, 22.2% against 33.0%; -12.3,
  -14.3 to -10.2, 10/10). Section C: 5,754 rows tied to no attempt in 472 matches: Flail lock 413 rows in 20 matches
  (2,242 s); area damage 309 rows in 54 matches (Symbol of Wrath 217, Chaos Storm 49, Ray of Judgment 28); should
  have kited 5,032 rows in 464 matches.
- The checked kinds (section G): prot passes (taken 8,626 at 15.8% killed, missed 4,654 at 49.8%; -28.0, -29.5 to
  -26.5, 10/10); heal passes (8,119 at 14.1%, 2,977 at 61.9%; -44.2, -45.9 to -42.4, 10/10); interrupt on a spike skill
  FAILS as at 97bac17 (158 against 7,418; -6.1, -11.1 to -0.1, 6/10), so the report stops (R-460). Strip fails (+0.1);
  pressure on their monks fails (-1.1). Pressure line: as at 97bac17 (the rule 150; his 225 holds 56.4%).
- The new kinds by Opus's scratch script (same yardstick): pact attempts out (12) change nothing; stance fails (+1.8,
  5/10); a spike into a block or immunity reads backwards (+2.2, 2/10); Deep Wound on him in time fails (-1.0, 4/10);
  an attacker on another player reads backwards (+4.7, 0/10); Deep Wound left with a removal ready passes (1,575 at
  54.8% against 3,308 at 26.8%; -32.0, 10/10). On pressure attempts: prot passes (-23.0, 10/10), heal passes (-36.0,
  10/10), Deep Wound left passes (-23.0, 10/10).
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
- 2026-11-27, night: full run at ccd0a55 reported; outputs and the full digest pushed (bundle-4 0dbc722).
- 2026-11-27: site look and pages (branch `site-look`, Denning's approval): parchment colours, clearer header, text
  removed, Next MAT, date range, player and character profiles, guild page reworked, Match report buttons; merged
  to main at 2fdf15e. Ground rules widened to the site's page files.
- 2026-11-27: full runs at 97bac17 and f2b8796 reported; outputs pushed (bundle-4 3dca405, 85d8294; main's rows).
- 2026-11-27: match report: spec agreed with Denning (Docs), prototype on `report-prototype` (not main); parked until
  he starts it (see "Parked").
- 2026-11-27: set up (Denning's go-ahead). Plan of the remaining work: the Docs artifact "GvG Info: the road ahead".
