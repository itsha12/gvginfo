# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-18, night: twelve games graded; the flag family's similar cases built and first read (R-538))
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one piece,
  then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in progress.
  Rulings run to R-538. The baseline (R-491) is the branch `baseline-2026-11-15`. R-531: the flag plays are ready.
- Graded and filed (set f1): twelve games (옷옷옷옷 v hdm to 9:40, R-532); per game in CHANGELOG. In the six games
  after the fifth, 153 Classic and Visible rows: 152 read as he reads them with his withdrawals and what was fixed
  (open: hold v Men 2:34). Game 14, Dz v Team on Druid's Isle: 22 Classic and 2 Visible, all read correct, 48 of
  48 calls. Out unmarked: hdm v HC (R-522) and game 13, Men v NwAy on Corrupted Isle (R-537). No game waits for
  him. Not graded his new way: Corrupted, Weeping Stone, Isle of the Dead.
- His marks on nine picked rows (set p2 in the key; their games are in the development set; none binds):
  - Part-runs: built (R-535, R-536; `Moments._part_carries`); his eleven rulings all read as he rules.
  - Boost: Men v hold 8:06 and 옷옷옷옷 v cope 2:49 are unsuccessful runs (the engine's reading stands); cope v
    hold 14:33 is no run (held at his door with his team): held, with Men v Crew 17:53, for a measure of ground made.
  - Sudden deaths of a solo split: QenK v Fun 6:37 and NwAy v ohno 5:24 are main team collapses (the second is
    not told: it kills before R-508's 4 s); each death is also left on the 1 v 1 row. Held for the split family.
- Confidence (R-515) does not tell Classic from Visible on the six games since its fit; what would is a measure of
  what is at stake (R-509), from the similar cases. Not built.
- Checkpoint run (every counted match, engine 76df8c0): 564 matches, 34,913 plays, no errors, self-check 7 in 5
  matches; flag plays 5,474, 1,491 set aside for Shadow of Haste (R-456). The reading is unchanged by the new
  fields (every play the same). The thirteen truths hold; 281 Classic rows pass, none fail; 129 history rows hold,
  3 do not; set f1 15 of 50 open checks hold, p2 0 of 3; gate 12 of 12 and 63 of 105; line-up and comms 530 of 583.
- The similar cases (R-538; `cases.py` on the branch, report in `data/model/flag_cases.json`), 5,195 cases:
  - Prices, win points from an even position: a flag of lead 6.8, a death's penalty 6.0, a morale boost 11.1, a pit
    NPC 4.7, 10% of Lord health 9.5, 100 points of strength 8.7; who wins foretold 82% on unseen matches. A footman
    is not priced (worth 0.1 alone, backwards beside the pit NPCs). K 120, chosen by the data (the miss is flat).
  - Their run, our answer (2,898 cases): no clear difference between the calls in about four of five; where
    clear it is nearly always "stay". Held out: matched against not matched -0.1 win points 180 s on (90% range
    -2.1 to +2.1). No gain shown. Under the floor: every double run in answer, a flag in hand.
  - Their boost 30 s away (1,316): run a flag clearly better in 34%, never "send no flag". Held out: +8.4 win
    points 180 s on (3.6 to 13.0), +10.5 without the 203 flags only held at home; in how the match ended +4.5
    (-4.8 to +13.8), not clear. The opening (804, kept apart): not clear at 180 s; "stay" there mixes in a flag
    brought up with the team.

## Next (in order)
1. The first advice test is put to him (2026-11-18): his answers on the three items under "Open for Denning"
   decide what is built next for the flag family, and whether the other kinds are built the same way (R-451).
2. Held for a second game (R-495): a base res with the attackers at the footmen (HC v hdm 1:40, Jade: held open
   for his review); Men v hold 6:48, a collapse told as a push on the flagger; who and how many push a flagger (HC v
   Team, Men v RACK 1:08); numbers through the portal on Jade; Men v hold 2:46, defenders standing in their pit.
3. The other kinds after the flag family, as he says each is ready; rare plays topped up with picked rows; then
   stage E. The clean-up (R-398; REDESIGN.md "Before the next training run", nine items) comes after the games.

## Open for Denning
0. From the first advice test (set out in the chat, 2026-11-18): (a) where the answer to a run shows no better
   call: add what the position leaves out (who runs, the res clock, where the teams stand) and test again, or
   accept that execution matters more there; (b) the opening: out of the verdicts, or "brings a flag up with its
   team" as its own call; (c) equal weight on the matching variables, or measured weights.
1. Isle of Jade: is a team at the footmen on the portal side in the base at a base res (HC v hdm 1:40)?
2. Tolkano: no build (his word). Match pages are tolkano.com/match/<id>, the id neither gvg.report's nor the start
   time: give him date, guilds, hall and length with every example so he can find it there.

## Data looked at on 2026-11-14 (nothing built; nothing from GW Observer in the repo)
- gvg.report's payload holds flag objects with positions, which `replay_trim.mjs` drops. R-481: at the next rebuild.

## Running it
- Train batch: the "Train batch" workflow (METHODS.md "Train batch on GitHub"; `blind` stays no). Never queue two runs.
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
