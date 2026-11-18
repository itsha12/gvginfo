# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-18, evening: eleven games graded and filed; all four open questions answered; nothing waiting to be built)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one piece,
  then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in progress.
  Rulings run to R-530. The only rows on the page not marked are six of game 12. The baseline (R-491) is the branch
  `baseline-2026-11-15` (figures in `data/model/baseline/`); built since, all from his marks: R-498 to R-530.
- His answers of 2026-11-18, evening, all filed in the key (`later`, `answered`), none needing an engine change: Men v
  RACK 18:25, the Prot is no part of the collapse (his word withdrawn; the Hammer alone binds); Men v hold 17:01, the
  Fire Ele's split from 17:02 is right (binds); a push on a flagger or a split is R-530 (`jobs._push_not_split` as
  built); game 12 at 9:00 and 9:32 were the clock (R-527), both readings correct (9:00, Classic, binds).
  `review.py file` now keeps `later` on refiling and lists such rows apart from "to fix first".
- Graded and filed (set f1), decisions read correct and decisions he had to add: HC v Team 85%, 0; Men v Crew 77%,
  0; 옷옷옷옷 v RACK 67%, 7; Men v RACK 71%, 4; Men v hold 80%, 5; hold v Men 95%, 0; HC v hdm 90%, 0; RACK v hdm
  100%, 0; hold v RACK 95%, 0; HC v cope 96%, 0; 옷옷옷옷 v hdm (game 12, to 9:40) 80%, 0 as marked. hdm v HC
  (bbef1904) is out (R-522); never pick it again. In the six games since the fifth, 153 Classic and Visible rows:
  143 read correct as marked, 152 with his withdrawals and what was fixed (open: hold v Men 2:34); of the No
  decision rows, HC v hdm 1:40 and hold v RACK 2:42 (no words) are still read.
- Confidence (R-515, fitted to five games, figures at the top of `confidence.py`): on the six games since, Classic is
  high 82, medium 49, low 4 and Visible high 10, medium 7, low 1, with no Weak row and three No decision rows that
  were not already context: it does not tell Classic from Visible, and more games give it nothing to learn from. What
  would is a measure of what is at stake (R-509), which the similar cases of the flag family supply. Not built.
- Checkpoint run of 2026-11-18 (every counted match, engine 8882861): 564 matches, 34,698 plays, no errors; self-check
  7 in 5 matches (0 on the development set). Flag plays 5,575; 1,517 set aside for Shadow of Haste (R-456); 4,058
  usable: a single run answered by a single 1,637, a stay 1,412, a double 177, a flag in hand 155; a double run
  answered by a single 339, a stay 166, a double 96, a flag in hand 76. By hall 683 (Corrupted) down to 147
  (Nomad's) and 13 (Isle of the Dead). Boost 1,470 (run 948, concede 522).
- Halls graded his new way: Jade 3, Imperial 2, Nomad's 2, Meditation 2, Uncharted 1, Solitude 1. Never: Corrupted
  (87 of the 564), Druid's (85), Weeping Stone (52), Isle of the Dead (6): 230 matches, 41%.
- Now (development set, 53 matches, 4,597 plays): 259 Classic rows pass, none fail; 117 of 120 history rows hold.
  Set f1: 15 of 51 open checks hold. Gate 12 of 12, 63 of 105. Line-up 420 of 426; comms 110 of 157. Self-check 0.

## Next (in order; put to him on 2026-11-18, his word awaited)
1. Claude's advice to him: no more whole games before going on. He says whether the flag plays are ready (R-496);
   then the flag family to the end (R-451; REDESIGN.md, stage D, c): similar cases for the flag plays, the better
   call by the consequence record, the held-out advice test on the branch, read with him whatever it shows. One game
   each on Corrupted and Druid's is worth grading beside that work, not before it (halls he has never graded).
2. Held for a second game (R-495): a base res counted with the attackers at the footmen, not in the base (HC v hdm
   1:40, Jade; asked of him: where the base ends on the portal side); Men v hold 6:48, hold following Men's three
   with the flag told as a push on the flagger (HC v Team 1:30 may be the same); who and how many push a flagger (HC
   v Team, Men v RACK 1:08); numbers through the portal on Isle of Jade (Men v Crew); Men v Crew 17:53; a defender's
   few seconds with a flag read as a run (hold v Men 2:34); the 18 s gap at 2:46 in Men v hold.
3. The other kinds after the flag family, as he says each is ready; rare plays (the Lord push, leaving before a res,
   the part-run) topped up with picked rows, not whole games; then stage E.
4. The clean-up (R-398; REDESIGN.md "Before the next training run", nine items: R-524 the README, R-526 the
   Templates tab) comes after the games. A boost row that repeats a single run stays its own row (R-525).

## Open for Denning
1. Are the flag plays ready (R-496), so that the flag family is taken to the end?
2. Isle of Jade: does a team at the footmen on the portal side count as in the base at a base res (HC v hdm 1:40)?
3. The six rows of game 12 after 9:40, if he wants to finish it.
## Data looked at on 2026-11-14 (nothing built; nothing from GW Observer in the repo)
- gvg.report's payload holds flag objects with positions (`report.objectives.object_transitions`), which
  `replay_trim.mjs` drops. R-481: keep them at the next rebuild only (a new TRIM_VERSION fetches every replay again).

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
