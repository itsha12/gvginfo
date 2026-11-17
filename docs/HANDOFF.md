# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-17, third session: R-516; his guide on splits v main team built; games 6 and 7 on the page, unmarked)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one piece,
  then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in progress.
- The baseline (R-491) is the branch `baseline-2026-11-15` (`bundle-4` at fd2b30b; figures in `data/model/baseline/`).
  Built on `bundle-4` since, all from his marks: R-498 to R-515 (CHANGELOG, DEFINITIONS), and in this session:
  - His guide of 2026-11-17, not a ruling and not strict (DEFINITIONS "Counting players"): a split is almost never in
    its own base; a small group at home with its main team elsewhere is most likely a defence. Built in `main_team`
    (switch `HOME_GUIDE`, off with GVG_HOME_GUIDE=0): more of a team at home than in any part away, with the engine's
    main team a part away, makes the part at home the main team; the engine's main team a part at home and a part away
    bigger than all at home makes that part the main team; each after 12 s. Ten games changed (hdm v Men 13:04 to
    15:28: Men's three in hdm's base are a split against three, where hdm was read as held in). No key row moved.
    Not touched: the 4 and 3 divide with one player away, the even divide (R-335), the held base (R-506).
- The fresh start (R-491 to R-497; CLAUDE.md): only Classic rows bind; other grades build from a fault in two games.
- Confidence on his five games (228 graded; R-515, figures at the top of `confidence.py`): the band is his grade on
  128, far off on 10. Steadiness cannot tell Visible from Weak or No decision; what would is a measure of what is at
  stake (his four reasons, R-509). Not built; 35 Weak and No decision rows so far.
- Graded and filed (set f1): HC v Team (9b5cdf62), Men v Crew (51683de9), 옷옷옷옷 v RACK (a8ba43a8), Men v RACK
  (45cf6756), Men v hold (572c2f95). Three Classic faults of the last two are open (Next, 2).
- Now (development set, 49 matches, 4,275 plays): 124 Classic rows pass, none fail; 118 of 120 history rows hold
  (hdm v hook 10:23, a flag row; hook v hold 12:46, the Warrior counted on the Necromancer's split for 14 s). Set f1
  has 49 open checks. Gate 12 of 12, 63 of 105. Line-up 421 of 426; comms 110 of 157. Self-check 205.
- On the page, not marked (engine a8b77a7): game 6, hdm v HC on Imperial Isle (bbef1904; 35 situations, 55 calls; high
  17, medium 14, low 4; six pushes on a flagger), and game 7, hold v Men on Uncharted Isle (b870f84e; 21 situations,
  38 calls; high 15, medium 4, low 1, one told as context). Never export them again, and fix nothing against them
  until he has marked them. Next in the queue: HC v hdm on Isle of Jade (af831111), for numbers through the portal.

## Next (in order)
1. When he has marked games 6 and 7: `review.py file` for each, his results set out in the chat, Classic faults first.
   Further games when he asks: `moments.py all --dev`, `confidence.py run` (about 12 minutes a game), `review.py export
   --label "game N"`. The moment calls in `moments.py` still read a full collapse and a split's start the old way.
2. Open Classic items in Men v hold and Men v RACK, each needing a root reading, not a rule: the door of Men's
   five-player split at 10:40 (he says back door; the engine says front); hold's Fire Ele solo split from 17:01 (read
   from 17:38); the Prot coming with the Hammer at 18:25 in Men v RACK. And an 18 s gap at 2:46 in Men v hold where
   the split walks round through the middle and the defence shadowing it in the field is not counted.
3. Held for a second game (R-495): who and how many push a flagger (HC v Team, Men v RACK 1:08); a split read where
   he sees a push on a flagger (Men v RACK 0:36, 1:32); numbers through the portal on Isle of Jade; Men v Crew
   17:53; a base res or a split told at or after the last second of a match (Men v Crew 27:40, Men v RACK 19:06).
4. When he says the flag plays are ready: the flag family to the end (R-451); the other kinds after; then stage E.

## Open for Denning (set out in full in the chat on 2026-11-17, third session, at his asking; awaiting his answer)
1. Where else to apply his principle (R-512), each with the data put to him: (a) a split's job when it holds more
   defenders than its own number: met by holding them and losing nobody, with what the main team made of the extra
   player told beside it? Today it also needs kills or flags elsewhere: 54 of 93 such rows survive and are "not met".
   (b) Pushing a flagger by standing on his route without hitting him: a rough count finds 396 stretches not read as
   a push against 147 that are, so it cannot be taken whole; proposed: he adds the clear ones as missed decisions on
   games 6 and 7. (c) Who counts in the main fight when it is near a split's fight: all 205 self-check cases are a
   player counted in both; proposed: he counts in the fight whose players he acts on or who act on him.
2. Closed: a defender from the main fight who makes a split fight even stays a join (R-516).

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
