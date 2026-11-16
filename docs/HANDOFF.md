# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-16: three games graded on the new marking; his rulings to R-504 built; 506 matches trained)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one piece,
  then one rebuild (R-322). 658 replays stored; 564 count (R-477). No Train batch, Discovery or fetch run in progress.
- The baseline (R-491) is the branch `baseline-2026-11-15` (`bundle-4` at fd2b30b); its reading of the 45 development
  games and its figures are in `data/model/baseline/` on main. Since then on `bundle-4` (now e2197e4; `jobs.py`,
  `moments.py`, `common.py`), all from HC v Team: his wording of flag, numbers and split rows (R-501); a stay ends at
  their cap; a run answers theirs when its runner set off before their cap (R-498); a split defender's death is the
  split's own (R-499); the first flags carry only "get the first flag in" (R-500); a main team round the back stays
  the main team and a split ends when the larger part of its team stands with it (R-502: read it, and what was tried
  and not kept, before touching `main_team`); runners named on boost and double-run rows, pit NPCs written out
  (R-503); a flag handed on is one runner, and a double run needs its second player gone back by the cap (R-504).
- The fresh start (R-491 to R-497; all in CLAUDE.md): the games marked before 2026-11-15 are history, scored and
  reported like the gate and the line-up, binding nothing. He grades each situation of a fresh game on Model > Game
  review (Classic, Visible, Weak, No decision, Repeat; then Correct, Partly, Incorrect with ticks and his words; calls
  only under a Classic or Visible decision read Correct or Partly; folded rows for the engine's no decision; missed
  decisions under the table). Only Classic binds; the other grades are built from when a fault shows in two games.
- The engine's confidence (`tools/golden/confidence.py`, outside the engine folder): the game read again with each of
  the 62 draft numbers a quarter either way and at half and double; high = the same in all, medium = moved only at
  half or double, low = moved at a quarter. Claude's draft bands. On HC v Team the low rows are mostly splits and
  pushes on a flagger, hanging on `FIGHT_LINK` (how close players stand to be in one fight) and `JOIN_S` (the 12 s).
- Graded and filed (set f1): HC v Team (9b5cdf62), Men v Crew (51683de9), 옷옷옷옷 v RACK (a8ba43a8). Read correct:
  Classic 20 of 22, 13 of 16, 7 of 12; Visible 15 of 19, 11 of 15, 13 of 18. His grades against the confidence, three
  games: high 43 Classic, 19 Visible, 1 Weak, 2 No decision; medium 5, 8, 1, 2; low 2, 25, 8, 9. Nothing fitted yet.
- Now (development set, 45 matches): 55 Classic rows pass, all 120 history rows hold, 10 of set f1's 50 open checks
  hold. Gate 12 of 12, 63 of 105. Line-up 421 of 426; comms 110 of 157. Nothing is on the page unmarked.

## Next (in order)
1. His answers to the items below; build them at the root (R-465); check after each change (CLAUDE.md).
2. Fit the confidence bands to his grades on the three games (which settings, at which move, separate his Weak and
   No decision rows from his Visible ones), put the result to him, and only then move the bands.
3. Next games: pick from unused October and November games of top guilds (no henchman game), add them to
   `dev_set.json`, `moments.py all <plays> --dev`, `confidence.py run <conf> <id>` (6 to 8 minutes a game: run it in
   the background), `review.py export <plays> <main rows> --set f1 --part N --label "game N" --confidence <conf>`.
4. Held for a second game (R-495): who and how many push a flagger (HC v Team); numbers read through the portal on
   Isle of Jade and a carrier falling back with his team read as a runner (Men v Crew).
5. When he says the flag plays are ready: the flag family to the end (R-451); the other kinds after; then stage E.

## Open for Denning (put to him 2026-11-16; set each out again, R-329, with the replay link; all Classic)
1. A flag carried is not always a run: 옷옷옷옷 v RACK 0:00 ("RACK brings flag up on Warrior, but DOES NOT run the
   flag"), 3:03 (the Hammer holds it; "RACK DOES NOT run"); Men v Crew 5:52. What makes a carry a run?
2. Five of RACK leave their base by the back door while it is held in (옷옷옷옷 v RACK 4:30, 8:11, 9:52): he sees a
   split of five and a full-team collapse on it (1:51, 4:39, 6:01, 8:16); the engine reads the five as RACK's main
   team (R-487, R-502). Proposed: players who leave a base that is held in, while the rest stay, are a split.
3. "Stays" at the base res (9:40, 15:40): in front of the door at the res, or leaving as it comes, is out?
4. Isle of Jade: which of the five archers a side are pit archers (Men v Crew 27:16)?
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
