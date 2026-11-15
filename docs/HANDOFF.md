# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-15, evening: a fresh start, R-491 to R-497; batch 17, 506 matches trained)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one piece,
  then one rebuild (R-322). 658 replays stored; 564 count (R-477). No Train batch, Discovery or fetch run in progress.
- The engine itself did not change this session: `tools/replay_analysis/` on `bundle-4` is as at fd2b30b, kept as
  the branch `baseline-2026-11-15`. That engine is the starting point (R-491). Its reading of the 45 development games and its
  figures are in `data/model/baseline/` on main (3,524 plays; review key 120 rows passing, 40 checks open; gate 12 of
  12 and 63 of 105; line-up 421 of 426 and 185 of 186; comms 110 of 157 and 62 of 80).
- His decision (R-491): the games marked before are history. The engine no longer has to fit their rows; they are
  scored after every change and what moves is reported, like the gate and the line-up: checks, binding nothing. The
  five items that were open are dropped, to be answered when a new game raises them (the job of a held flag and "in
  position to overcap" stay Claude's drafts in `flag_plays`).
- The new marking (R-492; Model > Game review, `assets/js/pages/review.js`; driven in a browser with a mocked save,
  and read by a fresh session, whose findings on the wording were built):
  each situation shows the engine's confidence up front; he grades it Classic (green), Visible (orange), Weak (red),
  No decision (blue) or Repeat; for a decision, Correct, Partly or Incorrect with ticks (numbers, who, when, where,
  kind of play) and his words; calls are asked only under a Classic or Visible decision read Correct or Partly;
  moments the engine reads as no decision are folded rows he can open; under the rows he adds missed decisions.
  Games marked the earlier way are shown read only.
- What the grades are for (R-494, R-495): Classic binds (read exactly as he does; fixed first; one row is enough);
  Visible is a rate to watch; Weak teaches the confidence to read low; No decision should stop being read; for the
  last three a fault is built from only when it shows in two games. No pass mark (R-496): he says when it is ready.
- The engine's confidence (R-497; `tools/golden/confidence.py` on the branch, outside the engine folder): the game
  read again with each of the 62 draft numbers of the reading a quarter lower and higher and at half and double (246
  readings, about six minutes a game); high = the same in all, medium = moved only at half or double, low = moved at
  a quarter (the number is named in a player's words). Claude's draft bands. HC v Team: 54 situations: 20 high, 10
  medium, 22 low, 2 no decision; the low ones are mostly splits and pushes on a flagger, and hang mostly on how close
  players must stand to be in one fight (`FIGHT_LINK`) and the 12 s a player needs to count (`JOIN_S`).
- On the page now, unmarked (set f1, game 1, engine fd2b30b): HC v Team on Imperial Isle (9b5cdf62; 54 situations,
  87 calls). Queue after it: Men v Crew (51683de9), 옷옷옷옷 v RACK (a8ba43a8); none is hidden any more.

## Next (in order)
1. He grades HC v Team (https://gvg.report/report/9b5cdf62-edce-5ca9-a6a4-c02d48c7eb96#map). Then, the same session:
   `review.py file 9b5cdf62 <main>/data/model/game_reviews.json <main>/data/model/game_review_marks.json --set f1 --key
   <main>/data/model/review_key.json`; copy the key to the branch; set out for him in the chat his grades against the
   confidence, the Classic rows to fix first, and what his words say; write by hand the checks for Partly and Incorrect.
2. Fix the Classic faults at the root (R-465), checking after each change (CLAUDE.md). Then export the next game:
   `moments.py all <plays> --dev`, `confidence.py run <conf> 51683de9`, `review.py export <plays> <main rows> --set f1
   --part 2 --label "game 2" --confidence <conf>`. Never re-export a game he has marked.
3. After about three graded games: fit the confidence bands to his grades (which numbers, at which move, separate his
   Weak and No decision rows from his Classic ones), put the result to him, and only then move the bands. Then decide
   with him whether the confidence goes into the engine itself so that the decision tier reads only steady moments.
4. When he says the flag plays are ready: the flag family to the end (R-451); the other kinds after; then stage E.

## Open for Denning
- Nothing waits on a ruling. His to correct: 옷옷옷옷 v RACK, the spare, queued with Men v Crew (R-497); the draft bands.
- Noted, not put to him (R-491): TFS v 옷옷옷옷 1:54, a flag put on the Obelisk stand reads "our flag is capped: no".

## Data looked at on 2026-11-14 (nothing built; nothing from GW Observer in the repo)
- gvg.report's replay payload holds `report.objectives.object_transitions` (each appearance of a flag object, with
  its position); `replay_trim.mjs` drops it. R-481: keep it in the trim and read flag returns from it at the next
  rebuild, not before (a new TRIM_VERSION fetches every stored replay again; the baseline plays file is kept for
  that reason). GW Observer's licence limits the code and the data: his call. The `full` payload is not probed.

## Running it
- Train batch: the "Train batch" workflow (METHODS.md "Train batch on GitHub"; `blind` stays no). Never queue two runs.
- Local engine: `git fetch --depth 1 --filter=blob:none origin +replays:refs/remotes/origin/replays` (the blobs come
  as they are read). `jobs.py`, `moments.py`, the gate, the line-up and `confidence.py` need no cache and no packages
  beyond Python (`cache.py sync pull`, `warm` and the pinned requirements only for the fitted models).
  `PYTHONDONTWRITEBYTECODE=1`. The review key, `dev_set.json` and `game_reviews.json` are written on main: pass
  `--key <main>/data/model/review_key.json`, and copy the key and `dev_set.json` to the branch after changing them.
- Site check: `python3 -m http.server`, then playwright with `/usr/bin/google-chrome`, api.github.com mocked.

## Cautions
- Never print or decode a sealed field (blind picks, golden moments) in a chat.
- Don't merge `bundle-4` piecemeal (R-322). Label, golden and review mark files are saved whole by the site: after a
  change here, he reloads the page first. Hall labels are saved to main: copy changed `data/maps/labels/*.json` to
  the branch before reading a hall (the export refuses otherwise).
- Transcripts never go in the repo: paraphrased statements only. Party slots are in `data/matches/`, not the replays.
  Refresh the branch's `golden_moments.json` from main before the gate.
