# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-19, 01:15: twelve games graded; the answer to their run read at fixed seconds (R-543))
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one piece,
  then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in progress.
  Rulings run to R-543. The baseline (R-491) is the branch `baseline-2026-11-15`. R-531: the flag plays are ready.
- Graded and filed (set f1): twelve games (옷옷옷옷 v hdm to 9:40, R-532); per game in CHANGELOG. In the six games
  after the fifth, 153 Classic and Visible rows: 152 read as he reads them with his withdrawals and what was fixed
  (open: hold v Men 2:34). Game 14, Dz v Team on Druid's Isle: 22 Classic and 2 Visible, all read correct, 48 of
  48 calls. Out unmarked: hdm v HC (R-522) and game 13, Men v NwAy on Corrupted Isle (R-537). No game waits for
  him. Not graded his new way: Corrupted, Weeping Stone, Isle of the Dead.
- His marks on nine picked rows (set p2 in the key; none binds). Part-runs are built (R-535, R-536). Held:
  - Boost: cope v hold 14:33 is no run (held at his door): held, with Men v Crew 17:53, for a measure of ground made.
  - Solo splits: QenK v Fun 6:37 and NwAy v ohno 5:24 are main team collapses (the second not told: it kills before
    R-508's 4 s); each death is also left on the 1 v 1 row. Held for the split family.
- Confidence (R-515) does not tell Classic from Visible; a measure of what is at stake (R-509) would. Not built.
- Checkpoint run (every counted match, engine f1ac7f4): 564 matches, 34,913 plays, no errors, self-check 7 in 5
  matches; flag plays 5,474, 1,491 set aside for Shadow of Haste (R-456). The reading is unchanged by the new
  fields (every play the same). The fourteen truths hold (T12 is his given, R-542); 281 Classic rows pass, none fail;
  129 history rows hold,
  3 do not; set f1 15 of 50 open checks hold, p2 0 of 3; gate 12 of 12 and 63 of 105; line-up and comms 530 of 583.
- The similar cases (R-538; `cases.py` on the branch, report in `data/model/flag_cases.json`), 5,195 cases:
  - Prices, win points from an even position: a flag of lead 6.8, a death's penalty 6.0, a morale boost 11.1, a pit
    NPC 4.7, 10% of Lord health 9.5; who wins foretold 82% on unseen matches. A footman is not priced. K 120.
  - Their run, our answer (2,898 cases), read to the end of their run: no gain held out on any weighting (-0.1 to
    +1.0 win points, none clear). The fault (R-542): a "stay" so read takes in their runs that came to nothing
    (their flag fails after 35% of stays, 9% of runs). That reading is superseded by the fixed reads below.
  - Read at 15, 30 and 45 s after their runner set off, judged at 60, 90, 120 and 180 s (R-543; section 4 of the
    report). His given holds (T12): a runner sent by 30 s is 0.28 of a flag ahead 90 s on. In win points the two
    are level (+0.1 at 90 s, 0.0 at 180 s); with nobody dying, not clear (-0.1): the flag part is as he says (2.2
    points) and is offset by own boosts, which land more where nobody was sent (0.23 against 0.04 in 90 s).
    Held out: read at 15 s, better at 60 s (+3.1) and 180 s (+4.6, advice mostly "no runner yet"), not clear at
    90 and 120; at 30 s better at 60 s only; at 45 s nothing clear. The three weightings agree nearly everywhere.
  - Their boost 30 s away (1,316): run a flag clearly better in 34%, never "send no flag". Held out: +8.4 win
    points 180 s on (3.6 to 13.0), +10.5 without the 203 flags only held at home; in how the match ended +4.5
    (-4.8 to +13.8), not clear. The opening (804 cases) is out: a different decision (R-541).

## Next (in order)
1. The flag family (R-540): his answers under Open, 0 (what to drop), then "will their flag beat our boost" as
   a matching variable, then the run in answer judged on whether it held even (who to send, their snares). The
   push on their flagger and the double run get no verdict until they clear the floor.
2. Held for a second game (R-495): a base res with the attackers at the footmen (HC v hdm 1:40, Jade: held open
   for his review); Men v hold 6:48, a collapse told as a push on the flagger; who and how many push a flagger (HC v
   Team, Men v RACK 1:08); numbers through the portal on Jade; Men v hold 2:46, defenders standing in their pit.
3. The other kinds after the flag family, as he says each is ready; rare plays topped up with picked rows; then
   stage E. The clean-up (R-398; REDESIGN.md "Before the next training run", nine items) comes after the games.

## Open for Denning
0. Put to him 2026-11-19, what to drop on this decision (R-543): the measured and six-variable weightings, the
   45 s read, the 120 s window, their double run, and the old reading to the end of their run.
1. Isle of Jade: is a team at the footmen on the portal side in the base at a base res (HC v hdm 1:40)?
2. Tolkano: no build (his word). Match pages are tolkano.com/match/<id>, the id neither gvg.report's nor the start
   time: give him date, guilds, hall and length with every example so he can find it there.

## Running it
- Train batch: the "Train batch" workflow (METHODS.md; `blind` stays no). Never queue two runs. At the next rebuild,
  keep gvg.report's flag objects, which `replay_trim.mjs` drops (R-481).
- Local engine: `git fetch --depth 1 --filter=blob:none origin +replays:refs/remotes/origin/replays` (the blobs come
  as they are read). `jobs.py`, `moments.py`, the gate, the line-up and `confidence.py` need no cache and no packages
  beyond Python; `cases.py` needs numpy and scikit-learn (`cache.py sync pull`, `warm` only for the fitted models).
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
