# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then set out the items under "Open for Denning" and carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it. Add your
> answers to the open items, by their numbers, to the same message if you have them.)

## State (2026-11-15: redesign step 2 on branch `bundle-4`, stage D under way; batch 17, 506 matches trained)
- Main's engine is unchanged (SPEC.md). Bundle 4 is on `bundle-4` and lands in one piece, then one rebuild (R-322).
  658 replays stored; 564 count (R-477); the trained batches still hold some. No Train batch, Discovery or fetch run
  in progress. Both branches pushed; nothing uncommitted. The files on `bundle-4` are listed in CLAUDE.md.
- Whole-game scores, situations right of those he judged (R-475), each a fresh game for the engine it was marked
  against: part 1 (TFS v 옷옷옷옷, Men v Apes) 45 of 85; hdm v hook 35 of 58 (60%); round 3 (set w2): hook v hold
  24 of 41 (59%), cope v Team 15 of 24 (62%), RJT v RACK 33 of 45 (73%, engine b09a26a). The mark is 80% (R-473).
- Built 2026-11-15, at the root (R-465), in two steps. From his marks on RJT v RACK (engine 9d3a679; R-482 to
  R-485): who is on a split (its back line counts, brief support does not: `_over`, `split_plays`); whose flag
  decision (`run_starts`: set-off, `out_by`, `chain`; a double run from its second player; each run answered in turn).
  From his answers on how to read a game (engine fd2b30b; R-486 to R-490):
  - The flag in hand is a timing choice: overcap at once, in position and hold, or hold not in position (further
    from the stand than `STAND_R`); a hold has its own clock and a draft job (`flag_plays`, field `hand`).
  - A flag picked up at home is a run from when it leaves the base (`FLAG_TAKEN_OUT_S` is no longer read).
  - Numbers are told only when they last 12 s (`scenario`); no smoothing of a split's counts. Telling each numbers
    only from its first true second was tried and failed two firm rows (Men v Apes 1:02, hook v hold 12:47): the
    seconds in which a fight forms stay with that fight.
  - `moving` (in neither fight) gives a numbers difference the source "on the way"; an even divide forward by the
    front door is named a push team (`group`).
  - `jobs.selfcheck`: 222 times on the development set a player is counted in a main fight's numbers and on a split
    for 12 s. A numbers stretch that is mostly a split's fight folds into the split; one the check faults, or whose
    numbers never held 12 s, is told as context with no call (`clear`, `unclear`): 165 of 848 numbers plays.
  - Two tiers in the review key (`tier`; six rows `tier_proposed`); the page's fourth mark, No clear decision.
- Now (development set, 45 matches): review key 120 rows pass, 40 checks open. Gate 12 of 12, 63 of 105. Line-up
  421 of 426 and 185 of 186; comms 110 of 157, 62 of 80. No run over every match, no `thresholds.py`, no numbers
  test (R-470) since. Not built: a measure of how spread out a fight is; the self-check's 222 at their root.
- Round 4 is on the page (set w3, engine fd2b30b), not yet marked: HC v Team on Imperial Isle (9b5cdf62; 54
  situations, 2 of them context, 87 calls). Men v Crew stays hidden.

## Data looked at on 2026-11-14 (nothing built; nothing from GW Observer in the repo)
- gvg.report's replay payload holds `report.objectives.object_transitions` (each appearance of a flag object, with
  its position); `replay_trim.mjs` drops it. A flag appearing at its spawn with no cap just before is a return (on
  RJT v RACK within 0.5 s of the game's four return messages; the engine's inferred returns were 3 to 69 s late).
  R-481: keep it in the trim and read returns from it at the next rebuild, not before (a new TRIM_VERSION fetches
  every stored replay again, about 90 MB a match).
- The Lord damage page (`summary.objectives.guild_lord_damage`) adds nothing stored casts and deaths do not give. GW
  Observer's match cache is the same recording kept fuller (NPC positions and health, returns, gates); no probed
  payload serves NPC tracks (`full` not probed: he said no). Its licence limits the code and the data: his call.

## Next (in order; REDESIGN.md "Build plan from here", item 6, and "Tests")
1. He marks HC v Team (Model > Game review). `review.py file <id> <rows> <marks> --set w3` files his marks and
   prints the score; write checks from his words; fix at the root (R-465). Never re-export a game he has marked.
2. The numbers test on the marked rows (R-470). At 80% of situations right on a fresh game, the hidden games.
   Never export or look at Men v Crew or 옷옷옷옷 v RACK before that.
3. The flag family to the end (R-451) once the flag plays pass; the other kinds as each passes; then stage E.

## Open for Denning (put to him 2026-11-15; set each out in the chat again, R-329, with replay links)
1. HC v Team is his to mark (https://gvg.report/report/9b5cdf62-edce-5ca9-a6a4-c02d48c7eb96#map).
2. The six rows proposed as borderline (review key, `tier_proposed`): OG v Dz 2:34, 옷옷옷옷 v Men 5:10, Men v NwAy
   11:46, hdm v hook 4:46, hook v hold 13:04, RJT v RACK 4:06. On his yes, set `tier` to borderline.
3. Drafts: a held flag's job; "in position" as within `STAND_R`; the push team named by the front door only.
4. From before: TFS v 옷옷옷옷 2:09 told from TFS's side; RJT v RACK rows 11, 24, 26, 30 now inside the split.

## Running it
- Train batch: `gh api -X POST repos/itsha12/gvginfo/actions/workflows/train-batch.yml/dispatches -f ref=main
  -f 'inputs[pick]=45' -f 'inputs[add_batch]=yes'` (rebuild only: `inputs[add_batch]=no`; TQs `inputs[tqs]=yes|no|auto`;
  blind round `inputs[blind]=no|yes|auto`, default no while rounds are paused). Never queue two runs at once.
- Local engine: `git fetch --depth 1 origin +replays:refs/remotes/origin/replays`; `pip install
  --break-system-packages -r .github/workflows/train-requirements.txt`. The records, the story, the line-up, the gate
  and the thresholds need no cache (`cache.py sync pull`, `warm` only for the fitted models). `PYTHONDONTWRITEBYTECODE=1`.
  `thresholds.py run`: about 15 minutes, two jobs, the machine to itself; old and new one after the other.

## Cautions
- Never print or decode a sealed field (blind picks, golden moments) in a chat.
- Don't merge `bundle-4` piecemeal (R-322). Label and golden files are saved whole by the site: after a change
  here, Denning reloads the page first. Hall labels are saved to main: copy changed `data/maps/labels/*.json` to the
  branch before reading a hall (the export refuses otherwise, and never shows a hidden or spare game).
- Transcripts never go in the repo: paraphrased statements only. Party slots are in `data/matches/`, not the replays. Refresh the branch's `golden_moments.json` from main before the gate.
