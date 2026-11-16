# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-15, late night: HC v Team graded, his rulings built, games 2 and 3 on the page; 506 matches trained)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one piece,
  then one rebuild (R-322). 658 replays stored; 564 count (R-477). No Train batch, Discovery or fetch run in progress.
- The baseline (R-491) is the branch `baseline-2026-11-15` (`bundle-4` at fd2b30b); its reading of the 45 development
  games and its figures are in `data/model/baseline/` on main. Since then on `bundle-4` (now e2197e4; `jobs.py`,
  `moments.py`, `common.py`), all from HC v Team: his wording of flag, numbers and split rows (R-501); a stay ends at
  their cap; a run answers theirs when its runner set off before their cap (R-498); a split defender's death is the
  split's own (R-499); the first flags carry only "get the first flag in" (R-500); a main team round the back stays
  the main team and a split ends when the larger part of its team stands with it (R-502: read it, and what was tried
  and not kept, before touching `main_team`).
- The fresh start (R-491 to R-497; all in CLAUDE.md): the games marked before 2026-11-15 are history, scored and
  reported like the gate and the line-up, binding nothing. He grades each situation of a fresh game on Model > Game
  review (Classic, Visible, Weak, No decision, Repeat; then Correct, Partly, Incorrect with ticks and his words; calls
  only under a Classic or Visible decision read Correct or Partly; folded rows for the engine's no decision; missed
  decisions under the table). Only Classic binds; the other grades are built from when a fault shows in two games.
- The engine's confidence (`tools/golden/confidence.py`, outside the engine folder): the game read again with each of
  the 62 draft numbers a quarter either way and at half and double; high = the same in all, medium = moved only at
  half or double, low = moved at a quarter. Claude's draft bands. On HC v Team the low rows are mostly splits and
  pushes on a flagger, hanging on `FIGHT_LINK` (how close players stand to be in one fight) and `JOIN_S` (the 12 s).
- HC v Team (set f1, game 1; 9b5cdf62) is graded and filed. His grades against the confidence, by situation: Classic
  22 (19 high, 2 medium, 1 low); Visible 19 (1, 6, 12); Weak 6 (0, 1, 5); No decision 5 (0, 1, 4). Read correct:
  Classic 20 of 22 (both faults now fixed and firm), Visible 15 of 19, Weak 3 of 6; calls 53 of 56.
- Now (development set, 45 matches): 22 Classic rows pass, all 120 history rows hold, 9 of HC v Team's 19 open checks
  hold. Gate 12 of 12, 63 of 105. Line-up 421 of 426; comms 110 of 157. Self-check 212. Splits 1,203, numbers 863.
- On the page, unmarked (engine e2197e4): Men v Crew on Isle of Jade (51683de9; game 2; 40 situations, 56 calls) and
  옷옷옷옷 v RACK on Isle of Solitude (a8ba43a8; game 3; 37 situations, 47 calls), both at once at his word.

## Next (in order)
1. He grades games 2 and 3. For each: `review.py file <id> <main rows> <main marks> --set f1 --key <main key>`, copy
   the key to the branch, set out the results in the chat (R-329), write the checks for Partly and Incorrect by hand.
2. Fix the Classic faults at the root (R-465), checking after each change (CLAUDE.md). A fault that now shows in two
   games is built (R-495). Seen in HC v Team only so far: who and how many push a flagger (rows 3, 4, 16, 19, 23); a
   split read on top of a push on the flagger (12); a split's continuation read as a new split (37); the three-player
   split of 12:28 to 13:22 that he reads as part of the main team's push (38).
3. With three graded games: fit the confidence bands to his grades, put the result to him, then move them.
4. Next games: pick from unused October and November games of top guilds (no henchman game); `moments.py all <plays>
   --dev` after adding them to `dev_set.json`, `confidence.py run <conf> <id>` (6 to 8 minutes a game: run it in the
   background), `review.py export <plays> <main rows> --set f1 --part N --label "game N" --confidence <conf>`.
5. When he says the flag plays are ready: the flag family to the end (R-451); the other kinds after; then stage E.

## Open for Denning
- Nothing waits on a ruling. His to correct when he looks: R-502 as built (Claude's reading of "fix back door"); a
  double run at the opening keeps its own job (R-500 covers single against single); the draft confidence bands.
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
