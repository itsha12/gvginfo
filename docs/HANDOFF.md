# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-19, late morning: twelve games graded; the flag readings checked and put on one clock (R-545, R-546))
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one piece,
  then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in progress.
  Rulings run to R-546. The baseline (R-491) is the branch `baseline-2026-11-15`. R-531: the flag plays are ready.
- Graded and filed (set f1): twelve games (옷옷옷옷 v hdm to 9:40, R-532), the last game 14, Dz v Team on Druid's
  Isle. Out unmarked: hdm v HC (R-522), Men v NwAy (R-537). No game waits for him. Not graded his new way:
  Corrupted, Weeping Stone, Isle of the Dead.
- His marks on nine picked rows (set p2 in the key; none binds). Part-runs are built (R-535, R-536). Held: cope v
  hold 14:33, a flag held at his door read as a boost runner (with Men v Crew 17:53); QenK v Fun 6:37 and NwAy v
  ohno 5:24, main team collapses whose deaths are also left on the 1 v 1 row (for the split family). Confidence
  (R-515) does not tell Classic from Visible; a measure of what is at stake (R-509) would: not built.
- Checkpoint run (every counted match, engine b3ecdc8): 564 matches, 34,913 plays, no errors, self-check 7 in 5
  matches. The fourteen truths hold; 281 Classic rows pass, none fail; 129 history rows hold, 3 do not. Gate 12 of
  12 and 63 of 105; line-up and comms 530 of 583 (last run 2026-11-18, not run again).
- The timing ladder (R-545; `cases.py ladder <plays file>`, report `data/model/flag_ladder.json`): the readings go
  with flag advantage. Us holding the stand, their flag in: the tally 90 s on -0.42, -0.59, -0.60, -1.00, -1.29 down
  the rungs (within 15 s, 15 to 30, 30 to 45, 45 to 90, later or never); their flag holds the stand 50, 54, 55, 64,
  108 of the next 180 s; their boost 16 to 20% for an answer within 90 s, 53% after. It found three faults, fixed
  at his word (R-546): the stand read a moment before our own cap (839 positions); 793 cases with our runner
  already out read as "no runner yet" (now their own decision, run again or not, from our cap); reads and windows
  on two clocks (now one, their runner's set-off: `clock.anchor`).
- The similar cases (`cases.py test`, `data/model/flag_cases.json`), 4,333 cases, on a new footing (2026-11-19): the
  chance of winning is matched on, a call's nearest cases are set level with the case read, and every scenario
  prints whether the two answers were on the same road in the 60 s before (`before` on the flag plays; level
  everywhere). Section 8, "as it fell", is the form he reads: by how soon our runner set off, and for no runner by
  whether their flag got in, with the chance of winning each row started from. Show him that, never the test alone.
  - Us holding the stand (1,308): a runner within 15 s -2.8 win points 180 s on (their flag in 92%); 15 to 90 s
    -1.4; none for 90 s +1.1, which is -4.4 where their flag got in (258) and +7.0 where it did not (241, teams
    that started at 76%). At the same position, no runner at 15 s less a runner: +2.1 (0.4 to 3.8).
  - Them holding it (540): a runner within 15 s +2.0 (flags +0.52), none for 90 s -0.1 (their boost 0.51 against
    0.16); at the same position not clear (-0.8, -2.7 to +0.8). At 30 s, and for run again or not: nothing clear.
  - Held out, spot by spot: better at 60 s (+1.2), not clear at 180 s (+1.2, -0.2 to +2.7). Their boost 30 s away:
    +5.9 (2.5 to 9.9). With the stand held, do not rush the answer; which spots, not yet. His given (R-542) holds.

## Next (in order)
1. The flag family (R-540), at his word: his reading of the ladder and of the corrected advice (Open, 0); who to
   send set against the same spot; the push on their flagger as a call when it clears the floor.
2. Held for a second game (R-495): a base res with the attackers at the footmen (HC v hdm 1:40, Jade); Men v hold
   6:48, a collapse told as a push on the flagger; who and how many push a flagger; numbers through Jade's portal.
3. The other kinds after the flag family, as he says each is ready; rare plays topped up with picked rows; then
   stage E. The clean-up (R-398; REDESIGN.md "Before the next training run", nine items, and `st.stand_owner` read
   on a whole second by the other readings) comes after the games.

## Open for Denning
0. Put to him 2026-11-19: what followed each answer (section 8) and the level check. Open from the ladder: (a) 163
   cases filed "we hold the stand" where their flag before goes in within 15 s of their runner turning for home;
   (b) the 60 s window is arithmetic for the 30 s read; (c) their flag's time foretold within 10 s in 44%.
   `LEVEL_MIN` and `RIDGE` in `cases.py` are Claude's drafts. Cause is not shown: a team may see their run failing.
1. Isle of Jade: is a team at the footmen on the portal side in the base at a base res (HC v hdm 1:40)?
2. Tolkano: no build (his word). Match pages are tolkano.com/match/<id>, the id neither gvg.report's nor the start
   time: give him date, guilds, hall and length with every example so he can find it there.

## Running it
- Train batch: the "Train batch" workflow (METHODS.md; `blind` stays no). Never queue two runs. At the next rebuild,
  keep gvg.report's flag objects, which `replay_trim.mjs` drops (R-481).
- Local engine: `git fetch --depth 1 --filter=blob:none origin +replays:refs/remotes/origin/replays` (the blobs come
  as they are read). `jobs.py`, `moments.py`, the gate, the line-up and `confidence.py` need no cache and no packages
  beyond Python; `cases.py` needs numpy and scikit-learn (`cache.py sync pull`, `warm` only for the fitted models).
  A full run (`moments.py all`) takes about 13 minutes here; `cases.py ladder` before `cases.py test` (R-545).
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
