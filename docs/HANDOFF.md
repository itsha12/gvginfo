# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-15, night: HC v Team graded and filed; batch 17, 506 matches trained)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one piece,
  then one rebuild (R-322). 658 replays stored; 564 count (R-477). No Train batch, Discovery or fetch run in progress.
- The baseline (R-491) is the branch `baseline-2026-11-15` (`bundle-4` at fd2b30b); its reading of the 45 development
  games and its figures are in `data/model/baseline/` on main. Since then on `bundle-4` (`jobs.py`, `moments.py`): his
  wording (a flag row names both sides and their runners, "Team single run (Monk 5 (WoC)); HC single run (Mes/A)"; a
  numbers row names the team, "HC down on numbers ..."; no "by the door" where no door is read) and one fix: a stay
  ends at their cap (202 stay plays on the development set end 10 s sooner; 4 results change). Nothing else moved.
- The fresh start (R-491 to R-497; all in CLAUDE.md): the games marked before 2026-11-15 are history, scored and
  reported like the gate and the line-up, binding nothing. He grades each situation of a fresh game on Model > Game
  review (Classic, Visible, Weak, No decision, Repeat; then Correct, Partly, Incorrect with ticks and his words; calls
  only under a Classic or Visible decision read Correct or Partly; folded rows for the engine's no decision; missed
  decisions under the table). Only Classic binds; the other grades are built from when a fault shows in two games.
- The engine's confidence (`tools/golden/confidence.py`, outside the engine folder): the game read again with each of
  the 62 draft numbers a quarter either way and at half and double; high = the same in all, medium = moved only at
  half or double, low = moved at a quarter. Claude's draft bands. On HC v Team the low rows are mostly splits and
  pushes on a flagger, hanging on `FIGHT_LINK` (how close players stand to be in one fight) and `JOIN_S` (the 12 s).
- HC v Team (set f1, game 1; 9b5cdf62) is graded and filed in the review key. His grades against the confidence, by
  situation: Classic 22 (19 high, 2 medium, 1 low); Visible 19 (1, 6, 12); Weak 6 (0, 1, 5); No decision 5 (0, 1, 4)
  and the 2 folded rows left as they are. Read correct: Classic 20 of 22, Visible 15 of 19, Weak 3 of 6; calls 53 of
  56. All 20 high-confidence rows are Classic or Visible; Low does not tell Visible from Weak (one game; he saw the
  band first). Review key now: 22 Classic rows pass, 120 history rows hold, 20 of f1's 21 open checks still open.
- Queue after it: Men v Crew (51683de9), 옷옷옷옷 v RACK (a8ba43a8). Not exported: a Classic fault is still open.

## Next (in order)
1. His answers to the three items below; build them at the root (R-465); check after each change (CLAUDE.md).
2. Then export the next game: `moments.py all <plays> --dev`, `confidence.py run <conf> 51683de9`, `review.py export
   <plays> <main rows> --set f1 --part 2 --label "game 2" --confidence <conf>`. Never re-export a game he has marked.
3. After he grades it: `review.py file <id> <main rows> <main marks> --set f1 --key <main key>`, copy the key to the
   branch, set out the results in the chat, write the checks for Partly and Incorrect by hand.
4. After about three graded games: fit the confidence bands to his grades, put the result to him, then move them.
   Faults seen in one game so far, to build only if a second game shows them (R-495): HC's main team pushing by the
   back door read as a split (rows 38, 40, 41, 46, 50); who and how many push a flagger (rows 3, 4, 16, 19, 23); a
   split read on top of a push on the flagger (12); a split's continuation read as a new split (37).
5. When he says the flag plays are ready: the flag family to the end (R-451); the other kinds after; then stage E.

## Open for Denning (put to him 2026-11-15, night; set each out again, R-329, with the replay link)
1. Classic, open (row 18, 5:58): HC's flag is capped at 6:36; Team's Monk 5 turns for home at 6:34 and leaves the
   stand area at 6:40, which is the run's moment by R-461, so the engine reads "Team stays". He reads Team's single
   run as the answer. Proposed: a run is the answer to theirs when its runner set off before their cap (20 of 232
   stays on the development set, 11 matches, are this case). His to rule: it touches R-461.
2. A death of a split's defender counted "at the main fight" in a flag job (row 31: Team's 8 Monk, 11:58, at Team's
   back door). Proposed: R-466 covers a split's defenders as it does its attackers.
3. The opening flag (rows 1, 2): nobody has a flag capped, "no one is behind on flags". Does the flag job apply?
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
