# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-17, second session: five games graded; his rulings to R-515 built; nothing on the page unmarked)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one piece,
  then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in progress.
- The baseline (R-491) is the branch `baseline-2026-11-15` (`bundle-4` at fd2b30b; figures in `data/model/baseline/`).
  Built on `bundle-4` since, all from his marks: R-498 to R-511 (CHANGELOG, DEFINITIONS), and in this session:
  - R-512, `split_plays` `defends` (`blocks`): defending a split is keeping it from its objective. A player on his
    own ground between the split and his pit counts though nobody fights, unless a group of the attackers' other
    players is nearer to him than the split is. Undefended split rows fell from 261 of 714 to 110 of 614.
  - R-513, `main_team`: at an uneven divide a larger part at home is the main team (R-487); the stand side decides
    the even divide only. A team in its own pit had been read as gone round the back (Men v hold 18:20).
  - R-514, `split_plays` and `review.py situations`: each join, collapse and leave stays its own play (`change`,
    `of`, `at`) and is shown in the row of its split, with a call under it.
  - R-515, `confidence.py band_of`: one band a situation. Low: a quarter's move of one setting and the engine stops
    reading it. Medium: still read there but details move, or gone at half or double. High: otherwise.
- The fresh start (R-491 to R-497; all in CLAUDE.md): only Classic rows bind; earlier games are history; the other
  grades are built from when a fault shows in two games. He grades on Model > Game review, which has his reason
  ticks (R-509) and a button that shows the rows not marked yet in red.
- Confidence on his five games (228 graded situations; Classic, Visible, Weak, No decision): high 84, 35, 2, 5;
  medium 23, 34, 8, 10; low 3, 14, 4, 6. The band is his grade on 128 (56%), far off on 10 (before: 123 and 16).
  Steadiness cannot tell Visible from Weak or No decision; length and kind of play did not help out of sample. What
  would: measures of what is at stake (his four reasons, R-509). Not built; 35 Weak and No decision rows so far.
  The five marked games keep the bands he saw; the new band shows from the next export.
- Graded and filed (set f1): HC v Team (9b5cdf62), Men v Crew (51683de9), 옷옷옷옷 v RACK (a8ba43a8), Men v RACK
  (45cf6756), Men v hold (572c2f95). Of the 22 Classic faults in the last two, 19 hold now; the 3 open are below.
- Now (development set, 47 matches, 4,146 plays): 124 Classic rows pass, none fail; 118 of 120 history rows hold
  (hdm v hook 10:23, a flag row; hook v hold 12:46, the Warrior counted on the Necromancer's split for 14 s). Set f1
  has 49 open checks. Gate 12 of 12, 63 of 105. Line-up 421 of 426; comms 110 of 157. Self-check 205.

## Next (in order)
1. Next games when he asks: pick as before; `moments.py all --dev`, `confidence.py run` (about 12 minutes a game),
   `review.py export` (the first export with change rows inside the split's row and the new band: look at the page
   before he does). The moment calls in `moments.py` still read a full collapse and a split's start the old way.
2. Open Classic items in Men v hold and Men v RACK, each needing a root reading, not a rule: the door of Men's
   five-player split at 10:40 (he says back door; the engine says front); hold's Fire Ele solo split from 17:01 (read
   from 17:38); the Prot coming with the Hammer at 18:25 in Men v RACK. And an 18 s gap at 2:46 in Men v hold where
   the split walks round through the middle and the defence shadowing it in the field is not counted.
3. Held for a second game (R-495): who and how many push a flagger (HC v Team, Men v RACK 1:08); a split read where
   he sees a push on a flagger (Men v RACK 0:36, 1:32); numbers through the portal on Isle of Jade; Men v Crew
   17:53; a base res or a split told at or after the last second of a match (Men v Crew 27:40, Men v RACK 19:06).
4. When he says the flag plays are ready: the flag family to the end (R-451); the other kinds after; then stage E.

## Open for Denning (put to him 2026-11-17; set each out again, R-329, with the replay link)
1. Where else to apply his principle (R-512). Put to him: (a) a split's job when it holds more defenders than its
   own number without fighting (it is doing its job; the test today asks for a kill or an NPC when it is a player
   up); (b) pushing a flagger by standing on his route without hitting him; (c) who counts in the main fight when
   two fights are near each other (whom a player faces, not only whom he is near).
2. A defender who comes from the main fight and makes a split fight even is told as a join (R-441); he called two
   such moves collapses (Men v hold 5:18 and 6:11). His to say whether coming from the main fight makes it a collapse.

## Data looked at on 2026-11-14 (nothing built; nothing from GW Observer in the repo)
- gvg.report's replay payload holds `report.objectives.object_transitions` (flag objects with positions), which
  `replay_trim.mjs` drops. R-481: keep it at the next rebuild only (a new TRIM_VERSION fetches every replay again).

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
