# Opus's work alongside Fable

Denning runs two kinds of chat on this repo: Fable builds the engine; Opus does the work that needs no engine
judgement (full runs and their reports, documentation drafts, site pages, the readability test, training chunk
reports). The aims, in his order: 1) as little Fable usage as possible; 2) as much as possible done in parallel.

Only Opus writes this file. Fable reads the "For Fable" section alone, at the start of a session, and never edits
this file: anything Fable wants Opus to know goes in HANDOFF.md as it already does, which Opus reads.

## For Fable (at most 10 lines; Opus removes a line once it is acted on)
- Full runs are Opus's from now (Denning, 2026-11-27). When the code is ready for one: push `bundle-4`, write
  "Full run wanted at <commit>: <what to check>" as the first line of HANDOFF's "Next", then go on building (stage
  5); don't wait and don't run it yourself unless Denning says. Opus's report lands under "Run reports" below.
- Rulings Denning gave in an Opus chat, to be filed by Fable (numbering stays with Fable):
  - Family 5 (engage or wait) is dropped: the opening is captured in the flag family (R-520, R-590, R-611).
  - The one-click match report (his wish of 2026-11-23) to be added to REDESIGN.md as a planned item after step 3.

## Ground rules for Opus
- Never edit: engine files on `bundle-4`, HANDOFF.md, RULINGS.md, DEFINITIONS.md, CHANGELOG.md, ENGINE_NOTES.md,
  EXECUTION.md, SPEC.md, REDESIGN.md. Those are Fable's; a change Opus thinks they need goes under "For Fable".
- Opus's own output: this file, drafts in `docs/opus/`, and a full run's output files (below).
- At the start of every Opus session: fetch main and `bundle-4`, read HANDOFF.md and the CHANGELOG entries and
  commit messages since the last log entry below, then this file.
- Before every push: fetch and rebase on the branch's newest commit. Push to main only the files above.
- Denning's preferences and CLAUDE.md's rules apply in full (explain in GvG terms; never print a sealed field).

## How Opus does a full run
1. Take the commit named in HANDOFF ("Full run wanted at ..."), in a worktree of its own: the run reads that commit,
   never a branch that moves under it. Fetch the replays branch as HANDOFF's "Running it" says.
2. Run what HANDOFF names, one at a time (each needs the machine to itself): `moments.py all`, then the `cases.py`
   reports, the key (`review.py score` with main's key), the truths, and the rows for main's views. Compare with the
   last full run (`compare.py`). About 1.5 h in all on 2 cores.
3. The output files go back where Fable would have put them: the `data/model/*_cases.json` reports to `bundle-4`
   (fetch first; data files only, never an engine file), the views' rows to main. If `bundle-4`'s engine files have
   changed since the run's commit, push the outputs to the branch `opus-runs` instead and say so under "For Fable".
4. Report under "Run reports": the commit, plays identical or not, Classic rows passing, each kind checked once on
   unseen matches (passes, fails, reads backwards) with its numbers, anything that stopped the run. A failed kind is
   reported, never fixed: the decision is Fable's and Denning's.

## Run reports (newest first)
(none yet)

## Log (newest first)
- 2026-11-27: set up (Denning's go-ahead). Plan of the remaining work: the Docs artifact "GvG Info: the road ahead".
