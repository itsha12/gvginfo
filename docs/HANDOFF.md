# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-19, 01:00: twelve games graded; the flag family's similar cases: the call's timing is at fault)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one piece,
  then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in progress.
  Rulings run to R-542. The baseline (R-491) is the branch `baseline-2026-11-15`. R-531: the flag plays are ready.
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
- Checkpoint run (every counted match, engine 9ba6fe7): 564 matches, 34,913 plays, no errors, self-check 7 in 5
  matches; flag plays 5,474, 1,491 set aside for Shadow of Haste (R-456). The reading is unchanged by the new
  fields (every play the same). The thirteen truths hold; 281 Classic rows pass, none fail; 129 history rows hold,
  3 do not; set f1 15 of 50 open checks hold, p2 0 of 3; gate 12 of 12 and 63 of 105; line-up and comms 530 of 583.
- The similar cases (R-538; `cases.py` on the branch, report in `data/model/flag_cases.json`), 5,195 cases:
  - Prices, win points from an even position: a flag of lead 6.8, a death's penalty 6.0, a morale boost 11.1, a pit
    NPC 4.7, 10% of Lord health 9.5, 100 points of strength 8.7; who wins foretold 82% on unseen matches. A footman
    is not priced (worth 0.1 alone, backwards beside the pit NPCs). K 120, chosen by the data (the miss is flat).
  - Their run, our answer (2,898 cases). First, on the eight variables of R-538: held out, matched against not
    matched -0.1 win points 180 s on (90% range -2.1 to +2.1). Then with the res clock, each main team's place,
    their runner and each team's snares (R-539, R-540): clear advice in 893, "stay" in 884; held out +1.0 (-0.7
    to +2.7). Still no gain shown. Under the floor: the double run in answer, a flag in hand.
    Measured weights +0.8 (-0.7 to +2.5), six chosen variables +0.7 (-1.3 to +2.6): the weights are not the fault.
  - The fault (R-542, his check): a "stay" is read from having sent nobody before their run ended, so their runs
    that came to nothing fall to it: their flag does not get in after 35% of stays (we hold the stand), 9% of
    runs. Where their flag got in the advice turns to "single run", and 90 s on a stay is half a flag and a win
    point worse; by 180 s it has nearly closed (the team that stayed has run its next flag). Our runs set off a
    median 17 s after theirs (71% within 30 s); 38% of their runs we "stayed" for were over within 30 s.
  - Their boost 30 s away (1,316): run a flag clearly better in 34%, never "send no flag". Held out: +8.4 win
    points 180 s on (3.6 to 13.0), +10.5 without the 203 flags only held at home; in how the match ended +4.5
    (-4.8 to +13.8), not clear. The opening (804, kept apart): not clear at 180 s; "stay" there mixes in a flag
    brought up with the team.

## Next (in order)
1. The flag family (R-540): his answers under Open, 0, then read the call at a fixed second, add how long their
   run will take, and test again; then the run in answer judged on whether it held even (who to send, their
   snares). The push on their flagger and the double run get no verdict until they clear the floor.
2. Held for a second game (R-495): a base res with the attackers at the footmen (HC v hdm 1:40, Jade: held open
   for his review); Men v hold 6:48, a collapse told as a push on the flagger; who and how many push a flagger (HC v
   Team, Men v RACK 1:08); numbers through the portal on Jade; Men v hold 2:46, defenders standing in their pit.
3. The other kinds after the flag family, as he says each is ready; rare plays topped up with picked rows; then
   stage E. The clean-up (R-398; REDESIGN.md "Before the next training run", nine items) comes after the games.

## Open for Denning
0. Put to him 2026-11-19: (a) read the call as what we had done 30 s after their runner set off, their runs over
   by then being no case; (b) judge at 90 s as well as 180 s; (c) R-542 as a known truth once (a) is built.
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
