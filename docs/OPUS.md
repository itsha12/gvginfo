# Opus's work alongside Fable

Denning runs two kinds of chat on this repo: Fable builds the engine; Opus does the work that needs no engine
judgement (full runs and their reports, documentation drafts, site pages, the readability test, training chunk
reports). The aims, in his order: 1) as little Fable usage as possible; 2) as much as possible done in parallel.

Only Opus writes this file. Fable reads the "For Fable" section alone, at the start of a session, and never edits
this file: anything Fable wants Opus to know goes in HANDOFF.md as it already does, which Opus reads.

## For Fable (at most 10 lines; Opus removes a line once it is acted on)
- Full runs are Opus's (Denning, 2026-11-27). The stage 1 to 4 full run (HANDOFF "Next" 2) is queued for Opus at
  `bundle-4` 97bac17: don't run it; take "Next" 1 (his answers on the prot amounts), then stage 5. If those answers
  change `prot_would`, the prot and heal kinds are read again at stage 5's own full run.
- Next time a full run is wanted: push `bundle-4`, write "Full run wanted at <commit>: <what to check>" as the first
  line of HANDOFF's "Next", and go on building. Opus's report lands under "Run reports" below. Opus pushes the
  run's `data/model/*_cases.json` to `bundle-4` (no engine file): fetch before every push there.
- Rulings Denning gave in an Opus chat, to be filed by Fable (numbering stays with Fable):
  - Family 5 (engage or wait) is dropped: the opening is captured in the flag family (R-520, R-590, R-611).
  - The one-click match report (his wish of 2026-11-23) to be added to REDESIGN.md as a planned item after step 3.

## Queued for Opus (newest last; Opus clears a line when done)
- Full run for stages 1 to 4 at `bundle-4` 97bac17 (Denning, 2026-11-27): what HANDOFF "Next" 2 lists (`cases.py
  pressure`, `attempts`, `execution`: do the three kinds still pass, prot and heal as they read now, Spirit Bond a
  prot; each new kind checked once: the chances on a pressure attempt, the Deep Wound left, the stance, the triggers,
  balling; pact kills left out of "killed"; R-782's no attempt made; the key, the truths, main's `execution_rows.json`).

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
(none yet)

## Starting a chat
- Opus: "Attach my repo itsha12/gvginfo with push access, clone it, check out `bundle-4` in a second worktree. You are
  the Opus chat: read docs/OPUS.md and follow its rules, then do what is queued for Opus."
- Fable: HANDOFF's own starter message, unchanged (CLAUDE.md sends it to "For Fable" here).

## Log (newest first)
- 2026-11-27: set up (Denning's go-ahead). Plan of the remaining work: the Docs artifact "GvG Info: the road ahead".
