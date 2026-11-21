# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-21: his answers on the split readings filed, R-560 to R-562; when a split starts is built; game 15 waits for his marks)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` (26116a5) and lands in
  one piece, then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run
  in progress. Rulings run to R-562. The baseline (R-491) is the branch `baseline-2026-11-15`.
- Graded and filed (set f1): twelve games. On the page, not marked: game 15, Men v NwAy on Corrupted Isle (c19f13e3,
  19 September; 36 situations, 8 of them splits; exported at engine 7e54f33). Not graded his new way: Corrupted,
  Weeping Stone, Isle of the Dead.
- Flags: all 60 advice cards marked; done for now. Numbers from kills: dropped as a family (R-557).
- The split readings. When it ends (2026-11-20, CLAUDE.md "When a split ends and what kills it"). When it starts
  (2026-11-21, R-562, CLAUDE.md "When a split starts"): a player who was not defending as before; a defence that
  goes out after the split it defended from the last way off to mid (`Hall.past_turnoff`) or from its own fight
  on the enemy's ground (Men v hold: 10:40, not 10:24). R-560 (a split until the rest come to the same fight, by
  whichever door) and R-561 (players left at the enemy's door are a split) needed no building.
- Checkpoint run (every counted match, engine 26116a5): 564 matches, 34,456 plays, no errors; 100 of 4,956 split
  rows start later than at 6048fde (middle 10 s), 4 gone, nothing else moved. The fourteen truths hold; 281 Classic
  rows pass, none fail; 132 history rows hold, 3 do not. Gate 12 of 12 and 63 of 105. Self-check 21 in 7 (twelve
  are one stretch, TFS v DMG 22:44). Line-up and comms 530 of 583 (2026-11-18, not run again).
- The similar cases (`cases.py test`, `data/model/flag_cases.json`, written at eca99d4), 4,277 cases. Section 8,
  180 s on, us holding the stand (1,260): a runner within 15 s -2.0 win points; 15 to 90 s -1.3; none for 90 s +1.1
  (-4.3 where their flag got in, +6.9 where it did not). Them holding it (533): +1.7, 0.0, -0.2.

## Next (in order)
1. His marks on game 15 (`game_review_marks.json`): file them the same session (`review.py file`), fix any Classic
   fault first, set the results out for him. Its rows were written before R-562: a split row of a defence gone out
   may now start some seconds later than the row he sees (say so if a mark turns on it; never re-export a game he
   has marked). He then says whether splits are ready (R-496, R-559).
2. The split family (R-558): the answer to a split, and the main fight while a split is out (3,729 numbers plays
   "from a split elsewhere"; his calls of R-551 with collapse and send more), through the four stages. To build: on
   every split play the position, the fixed 90 and 180 s record and the 60 s before, from the second the split is
   told (R-562; as `_numbers_at`); the answer read at a fixed second; like spots; cards and a view (copy
   `ADVICE.numbers` in `review.js`).
3. Held for a second game (R-495): Men v hold 18:06 (two of a push standing off it) and 6:48 (a collapse told as
   a push on the flagger); TFS v DMG 22:44; a base res with the attackers at the footmen (HC v hdm 1:40); who and
   how many push a flagger; numbers through Jade's portal; cope v hold 14:33; HC v hdm 5:56 (a flag left lying).
   Not built: a measure of what is at stake (R-509). Then stage E; the clean-up (R-398) after the games.

## Open for Denning
0. Held at his word (R-554, his "make sure you remember"): the cards for a flag in hand, with R-553 to build (no
   runner while the next flag is up is a flag-in-hand decision), and for a double run from the sender's side:
   raise them when more matches are trained. The execution list (R-557): the res, giving ground, fights.
1. From 2026-11-21: (a) the grade of Men v hold 19:38 (he said it is correct; Classic, Visible or Weak is not
   given: the row stands "not marked" in the key); (b) a defence that crosses still fighting the split it defended
   is told from that fight on the enemy's ground, a little before the way off he named: built so, because without
   it 4 v 4 fights on a back path were told nowhere; his to turn round; (c) R-562 is Claude's reading of his rule,
   which he does not want made more specific: bring him the splits it tells wrongly as they turn up in his games.
2. Jade: is a team at the footmen on the portal side in the base at a base res?
3. Tolkano: no build (his word): give him date, guilds, hall and length with every example to find it there.

## Running it
- Train batch: the "Train batch" workflow (METHODS.md; `blind` stays no). Never queue two runs. At the next rebuild,
  keep gvg.report's flag objects, which `replay_trim.mjs` drops (R-481).
- Local engine: `git fetch --depth 1 --filter=blob:none origin +replays:refs/remotes/origin/replays` (the blobs come
  as they are read). `jobs.py`, `moments.py`, the gate, the line-up and `confidence.py` need no cache and no packages
  beyond Python; `cases.py` needs numpy and scikit-learn (`cache.py sync pull`, `warm` only for the fitted models).
  A full run (`moments.py all`) takes about 13 minutes here (the replays in one go: the same fetch with
  `--no-filter --refetch`); `cases.py ladder` before `cases.py test` (R-545).
  `PYTHONDONTWRITEBYTECODE=1`. The review key, `dev_set.json` and `game_reviews.json` are written on main: pass
  `--key <main>/data/model/review_key.json`, and copy the key and `dev_set.json` to the branch after changing them.
- Site check: `python3 -m http.server`, then playwright with `/usr/bin/google-chrome`, api.github.com mocked.

## Cautions
- Never print or decode a sealed field (blind picks, golden moments) in a chat.
- Don't merge `bundle-4` piecemeal (R-322). Label, golden and review mark files are saved whole by the site: after a
  change here, he reloads the page first. Hall labels are saved to main: copy changed `data/maps/labels/*.json` to
  the branch before reading a hall (the export refuses otherwise).
- Transcripts never go in the repo: paraphrased statements only. Party slots are in `data/matches/`, not the replays. Refresh the branch's `golden_moments.json` first.
