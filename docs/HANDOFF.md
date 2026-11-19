# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-19, 07:30: twelve games graded; the flag family's answer read at fixed seconds (R-544))
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one piece,
  then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in progress.
  Rulings run to R-544. The baseline (R-491) is the branch `baseline-2026-11-15`. R-531: the flag plays are ready.
- Graded and filed (set f1): twelve games (옷옷옷옷 v hdm to 9:40, R-532); per game in CHANGELOG. The last, game
  14, Dz v Team on Druid's Isle: 22 Classic and 2 Visible, all read correct, 48 of 48 calls. Out unmarked: hdm v
  HC (R-522) and game 13, Men v NwAy (R-537). No game waits for him. Not graded his new way: Corrupted, Weeping
  Stone, Isle of the Dead.
- His marks on nine picked rows (set p2 in the key; none binds). Part-runs are built (R-535, R-536). Held: cope v
  hold 14:33, a flag held at his door read as a boost runner (with Men v Crew 17:53); QenK v Fun 6:37 and NwAy v
  ohno 5:24, main team collapses whose deaths are also left on the 1 v 1 row (for the split family).
- Confidence (R-515) does not tell Classic from Visible; a measure of what is at stake (R-509) would. Not built.
- Checkpoint run (every counted match, engine bf84adb; the report from b8d6dd9): 564 matches, 34,913 plays, no errors, self-check 7 in 5
  matches; every play the same as before the flag work, new fields apart. The fourteen truths hold (T12 is his
  given on flags, R-542); 281 Classic rows pass, none fail; 129 history rows hold, 3 do not; set f1 15 of 50 open
  checks hold, p2 0 of 3. Gate 12 of 12 and 63 of 105, line-up and comms 530 of 583 (last run 2026-11-18).
- The similar cases (R-538 to R-544; `cases.py test <plays file>` on the branch, about a minute; the report is
  `data/model/flag_cases.json`), 4,332 cases; 1,606 Shadow of Haste plays and the opening (868, R-541) set aside:
  - Prices, win points from an even position: a flag of lead 6.8, a death's penalty 6.0, a morale boost 11.1, a pit
    NPC 4.7, 10% of Lord health 9.5; who wins foretold 82% on unseen matches. A footman is not priced. K 90.
  - Their boost 30 s away (1,316): "run a flag" clearly better in 31%. Held out: +9.1 win points 180 s on (4.8 to
    13.8), +11.2 without the 203 flags only held at home; in how the match ended +4.6 (-5.8 to +13.8), not clear.
  - Their run, our answer: read 15 and 30 s after their runner set off (their run still under way, nobody sent by
    the read before; a runner sent, a double run started, or none yet), judged 60, 90 and 180 s on (R-543, R-544).
    Never read to the end of their run (R-542: such a "stay" takes in their runs that came to nothing).
    In flags a runner sent is ahead at every window (15 s read, us holding the stand: +0.24, +0.39, +0.19).
    Held out, read at 15 s (2,808 cases): matching the advice is better at 60 s (+2.9, 1.9 to 4.2) and at 180 s
    (+4.8, 1.9 to 7.7; the advice "no runner yet" in 654 of 756; in how the match ended +8.5, 2.1 to 16.4), not
    clear at 90 s. Read at 30 s (2,015): nothing clear. Ten tests in all: a lead, not yet a finding.
  - What the advice is (report sections 5 and 6). With us holding the stand it says hold off in 650 of 1,417: we
    are winning the fight (up on numbers 46% against 35% where nothing is clear, on their side of the stand 41%
    against 18%, their morale -40 against -9, their runner a monk 2% against 16%). 570 held off (+1.9 win points
    180 s on), 80 sent (-1.8): +3.6 (0.9 to 6.4); where their flag got in +1.9 (-1.2 to +4.9), not clear: their
    flag got in after 69% of the holds and 94% of the sends, so part of it is their run failing. With them holding
    the stand it says send in 81 (their boost near, us behind in morale); only 10 did. Of teams with no runner at
    15 s and us holding the stand, 41% send none in 90 s (their flag in 50%, a kill within 60 s 44%).
  - The run in answer (section 7; 1,416 runs, as it fell): our flag in 81%, 1.26 times a clean run. Their snares
    slow it: 1.19 times with the fewest third, 1.35 with the most (flag in 87% against 77%, them holding the
    stand). An 8 Monk sent: +3.2 win points 180 s on; a frontline player -1.4 (who runs follows the spot).
  - His given (R-542). Flags: holds (+0.29 of a flag 90 s on for a runner sent by 30 s). "No kill, no other gain,
    so worse off": with nobody dying and no boost landing, a runner sent is +1.0 win points ahead with us holding
    the stand (-0.1 to +2.0) and +0.7 with them holding it (-0.2 to +1.6): his way, not clear. With boosts let in
    it is level, own boosts landing more where nobody was sent (the flag-beats-boost variable halves that gap).
  - Under the floor: the double run (theirs as a scenario, ours as a call: kept, R-544) and a flag in hand.

## Next (in order)
1. The flag family (R-540), at his word: his reading of the advice and of the moments put to him (Open, 0);
   who to send set against the same spot (similar cases among the runs); the push on their flagger as a call
   when it clears the floor.
2. Held for a second game (R-495): a base res with the attackers at the footmen (HC v hdm 1:40, Jade); Men v hold
   6:48, a collapse told as a push on the flagger; who and how many push a flagger; numbers through Jade's portal.
3. The other kinds after the flag family, as he says each is ready; rare plays topped up with picked rows; then
   stage E. The clean-up (R-398; REDESIGN.md "Before the next training run", nine items) comes after the games.

## Open for Denning
0. Put to him 2026-11-19: does "hold off while winning the fight with us holding the stand" read right to him,
   on the three moments in games he graded (Dz v Team 4:37, 옷옷옷옷 v RACK 1:41, Men v Crew 5:52); what next.
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
