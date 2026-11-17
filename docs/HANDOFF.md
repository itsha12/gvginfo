# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-17: five games graded; his rulings to R-511 built; nothing on the page unmarked; 506 matches trained)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one piece,
  then one rebuild (R-322). 658 replays stored; 564 count (R-477). No Train batch, Discovery or fetch run in progress.
- The baseline (R-491) is the branch `baseline-2026-11-15` (`bundle-4` at fd2b30b; figures in `data/model/baseline/`).
  Built on `bundle-4` since, all from his marks: R-498 to R-509 (CHANGELOG, DEFINITIONS), and on 2026-11-17:
  - R-510, `split_plays`: a split is told from its crossing, or from 4 s after its players set out when they go
    straight across; the row says when it reaches their base or a defender (`reach0`). Its door is the enemy's
    door its first players come to (`attempts`, `ways`).
  - R-511, `split_plays`: each change of numbers inside a split fight is a row for the side that made it (join,
    collapse by R-441, leave); `change` on the play. Jobs of a join and a leave are drafts.
  - Pit archers are matched to his labels by where their attackers stood at each hit (`state.py`, `hits`); a capture
    recorded on a player away from the stand is the carrier's (`Moments._true_capper`, `recapped`); a carrier who
    caps inside a boost's window is its runner; an opening is a double run when the second player turns back before
    the first cap; the opening row says when a team brought no flag up.
- Tried on 2026-11-17 and not kept: a player standing off a split on his own ground counted as defending it (two
  forms). It read Men v hold as he does and broke his earlier rows on players hovering near a split (옷옷옷옷 v Men
  6:50, hdm v hook 7:12 and 7:52, RJT v RACK 8:00); the self-check went from 218 to 272. Needs his definition.
- The fresh start (R-491 to R-497; all in CLAUDE.md): only Classic rows bind; earlier games are history; the other
  grades are built from when a fault shows in two games. He grades on Model > Game review, which has his reason
  ticks (R-509) and a button that shows the rows not marked yet in red.
- The confidence bands on the page are those fitted to three games (top of `tools/golden/confidence.py`). On games 4
  and 5, which the fit never saw: high 28 Classic, 5 Visible, 1 Weak, 1 No decision; medium 22, 13, 1, 3; low 10, 13,
  2, 4. High holds; medium and low do not. Length does not help out of sample. Put to him, not applied: tell apart
  whether the situation vanishes when a setting moves (five games: never 103, 53, 5, 11; at half or double 4, 15, 5,
  4; at a quarter 3, 15, 4, 6) from whether its details move (read correct 81% when steady, 68% when not).
- Graded and filed (set f1): HC v Team (9b5cdf62), Men v Crew (51683de9), 옷옷옷옷 v RACK (a8ba43a8), Men v RACK
  (45cf6756), Men v hold (572c2f95). Of the 22 Classic faults in the last two, 12 hold now; the 10 open are below.
- Now (development set, 47 matches, 4,339 plays): 124 Classic rows pass; 118 of 120 history rows hold; set f1 has 57
  open checks. Gate 12 of 12, 63 of 105. Line-up 421 of 426; comms 110 of 157. Self-check 218.

## Next (in order)
1. His answers to the items below; build at the root (R-465); check after each change (CLAUDE.md).
2. The confidence: his word on the two-part measure; then change `confidence.py` and `review.py export` together.
3. Next games when he asks: pick as before; `moments.py all --dev`, `confidence.py run` (about 12 minutes a game),
   `review.py export`. The moment calls in `moments.py` still read a full collapse and a split's start the old way.
4. Held for a second game (R-495): who and how many push a flagger (HC v Team, Men v RACK 1:08); a split read where
   he sees a push on a flagger (Men v RACK 0:36, 1:32); numbers through the portal on Isle of Jade; Men v Crew
   17:53; a base res or a split told at or after the last second of a match (Men v Crew 27:40, Men v RACK 19:06).
5. When he says the flag plays are ready: the flag family to the end (R-451); the other kinds after; then stage E.

## Open for Denning (put to him 2026-11-17; set each out again, R-329, with the replay link)
1. Who defends a split without being within reach of it (Men v hold 0:48, 2:46, 4:20, 10:40 and 1:09, Classic): he
   counts Men's Ranger and Ritualist 2 standing in their pit, and the Hammer at the back footmen; in four earlier
   rows he said a player hovering near is not defending. Proposed: the home defence (never left home) counts.
2. A team's players who go out together read as its main team pushing, where he sees a split of three (Men v hold
   18:20 and 18:56, hold's Earth Ele, Fire Ele and 8 Monk); and the solo splits at 17:01 and 17:59.
3. R-510 against his note on Book v One 18:54 (the split called too early): the row now starts at the crossing and
   says when it reaches. His to confirm. And 12:48 in Men v RACK reads as a join under R-441, where he says collapse.

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
