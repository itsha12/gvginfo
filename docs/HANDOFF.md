# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-18, night: eleven games graded; games 13 and 14 exported, not yet marked; no engine change today)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one piece,
  then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in progress.
  Rulings run to R-534. The baseline (R-491) is the branch `baseline-2026-11-15`; built since, from his marks: R-498
  to R-530. His answers of 2026-11-18 are in the key (`later`, `answered`). R-531: the flag plays are ready. R-532:
  game 12 stays graded to 9:40.
- Graded and filed (set f1): eleven games (the last, 옷옷옷옷 v hdm, to 9:40); per game in CHANGELOG. hdm v HC
  (bbef1904) is out (R-522). In the six games since the fifth, 153 Classic and Visible rows: 143 read correct as
  marked, 152 with his withdrawals and what was fixed (open: hold v Men 2:34); no decision he had to add.
- Exported 2026-11-18 (engine 9223e30), not marked: game 13, Men v NwAy on Corrupted Isle (c19f13e3; 35 situations,
  68 calls), and game 14, Dz v Team on Druid's Isle (15a20f7a; 25 situations, 48 calls; its splits medium or low).
- The known truths (R-533, amended R-534; `tools/golden/truths.py` on the branch, at every checkpoint): thirteen,
  all hold. Compare calls on the fixed 90 and 180 s record, never a play's own end (T7 holds only there).
- His marks on nine picked rows (set p2 in the key; their games are in the development set; none binds):
  - Part-runs (cope v One 11:39, meow v One 7:07; hold v Men 2:34 before): "not a flag run ... a part-run". Built
    three ways on 2026-11-18 and dropped each time, the engine files put back: every second in a split's defence;
    every carry by a defender that stays on his own ground; only such a carry that another player takes on. Each
    read his three rows as he does and broke a run he had marked correct (HC v cope 1:58, Classic; hold v Men 1:06,
    Visible; TFS v 옷옷옷옷 3:26, history). Nothing measured tells meow v One 7:03 (8 Monk, 14 s, his own door)
    from HC v cope 2:20 (Mes/A, 14 s, his own door): put to him. True v One: he looked at 0:45; the carry is 1:48.
  - Boost: Men v hold 8:06 and 옷옷옷옷 v cope 2:49 are unsuccessful runs (the engine's reading stands); cope v
    hold 14:33 is no run (held at his door with his team): held, with Men v Crew 17:53, for a measure of ground made.
  - Sudden deaths of a solo split: QenK v Fun 6:37 and NwAy v ohno 5:24 are main team collapses; Team v BcS 18:11
    is a base res, no collapse. The engine tells the first (from 6:28) and the base res, tells no collapse in the
    second (it kills before R-508's 4 s), and leaves each death on the 1 v 1 row as well. Held for the split family.
- Confidence (R-515) does not tell Classic from Visible on the six games since its fit; what would is a measure of
  what is at stake (R-509), from the similar cases. Not built.
- Checkpoint run (every counted match): 564 matches, 34,698 plays, no errors; self-check 7 in 5 matches. Flag plays
  5,575; 1,517 set aside for Shadow of Haste (R-456); 4,058 usable: a single run answered by a single 1,637, a stay
  1,412, a double 177, a flag in hand 155; a double run answered by a single 339, a stay 166, a double 96, in hand 76.
- Now (development set, 64 matches): 259 Classic rows pass, none fail; 126 of 129 history rows hold. Set f1: 15 of
  51 open checks hold; p2: 0 of 6. Gate 12 of 12, 63 of 105. Line-up 420 of 426; comms 110 of 157. Self-check 0.

## Next (in order)
1. The flag family to the end (R-451, R-531; REDESIGN.md, stage D, c): similar cases for the flag plays, the better
   call by the fixed 90 and 180 s record, the held-out advice test on the branch, read with him whatever it shows.
   Every result with and without the flag shapes still misread (a defender's carry; a flag held at home at a boost).
2. His marks on games 13 and 14 when he has graded them: file them the same session (`review.py file`).
3. Held for a second game (R-495): a base res counted with the attackers at the footmen (HC v hdm 1:40, Jade: held
   open for his review); Men v hold 6:48, a collapse told as a push on the flagger; who and how many push a flagger
   (HC v Team, Men v RACK 1:08); numbers through the portal on Jade (Men v Crew); Men v hold 2:46, defenders standing
   in their pit. Each is counted and put to him when its kind of play is next.
4. The other kinds after the flag family, as he says each is ready; rare plays topped up with picked rows; then
   stage E. The clean-up (R-398; REDESIGN.md "Before the next training run", nine items) comes after the games.

## Open for Denning (all set out in the chat on 2026-11-18)
1. Isle of Jade: is a team at the footmen on the portal side in the base at a base res (HC v hdm 1:40)?
2. What tells a part-run from an unsuccessful run by a defender (the pairs above)? True v One at 1:48.
3. Tolkano links: match pages are tolkano.com/match/<id>; the id cannot be worked out from gvg.report's. Asked of
   him: one Tolkano link to a game we hold, and whether a workflow may read Tolkano's match list for a lookup.

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
