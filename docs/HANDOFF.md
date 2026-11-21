# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-21, later: game 15 graded and filed, every row read correct; R-563; waiting on his word that splits are ready)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in
  progress. Rulings run to R-563. The baseline (R-491) is the branch `baseline-2026-11-15`.
- Graded and filed (set f1): thirteen games. Game 15, Men v NwAy on Corrupted Isle (c19f13e3): 36 situations, 32
  Classic and 2 Visible, all read Correct, none missed, two without a grade (12:11 flag, 12:12 boost); all eight
  split rows Correct. Not graded his new way: Weeping Stone, Isle of the Dead.
- Flags: all 60 advice cards marked; done for now. Numbers from kills: dropped as a family (R-557).
- The split readings: when it ends (2026-11-20) and when it starts (R-562, with the fight clause his by R-563) are
  in CLAUDE.md. No engine change since 26116a5; game 15 reads now exactly as the rows he marked.
- Last checkpoint (every counted match, engine 26116a5): 564 matches, 34,456 plays, no errors; fourteen truths
  hold; gate 12 of 12 and 63 of 105; self-check 21 in 7 (twelve are TFS v DMG 22:44). Development set today: 313
  Classic rows pass, none fail; 132 history rows hold, 3 do not. Line-up 530 of 583 (2026-11-18, not run again).
- The similar cases (`cases.py test`, `data/model/flag_cases.json`, written at eca99d4), 4,277 cases. Section 8,
  180 s on, us holding the stand (1,260): a runner within 15 s -2.0 win points; 15 to 90 s -1.3; none for 90 s +1.1
  (-4.3 where their flag got in, +6.9 where it did not). Them holding it (533): +1.7, 0.0, -0.2.

## Next (in order)
1. His answers to "Open for Denning" 1: (a) are splits ready (R-496, R-559)? (b) the first-flag stay call at the
   opening: build what he rules (in `flag_plays`, the `ours == "stay"` branch; the open check on f1-c19f-1; test
   against RACK v hdm 0:00, where he marked the same call correct, and every Classic opening row).
2. When splits are ready, the split family (R-558): the answer to a split, and the main fight while a split is out
   (3,729 numbers plays "from a split elsewhere"; his calls of R-551 with collapse and send more), through the four
   stages. To build: on every split play the position, the fixed 90 and 180 s record and the 60 s before, from the
   second the split is told (R-562; as `_numbers_at`); the answer read at a fixed second; like spots; cards and a
   view (copy `ADVICE.numbers` in `review.js`).
3. Held for a second game (R-495): Men v hold 18:06 (two of a push standing off it) and 6:48 (a collapse told as
   a push on the flagger); TFS v DMG 22:44; a base res with the attackers at the footmen (HC v hdm 1:40); who and
   how many push a flagger; numbers through Jade's portal; cope v hold 14:33; HC v hdm 5:56 (a flag left lying).
   Not built: a measure of what is at stake (R-509). Then stage E; the clean-up (R-398) after the games.

## Open for Denning
0. Held at his word (R-554, his "make sure you remember"): the cards for a flag in hand, with R-553 to build (no
   runner while the next flag is up is a flag-in-hand decision), and for a double run from the sender's side:
   raise them when more matches are trained. The execution list (R-557): the res, giving ground, fights.
1. Put to him 2026-11-21: (a) whether splits are ready; (b) Men v NwAy 0:00, "they don't have 2 extra players":
   does a team that runs no first flag carry any stay job at the opening (recommended: none, only "get the first
   flag in", R-500 and R-541, which also takes the call off RACK v hdm 0:00), or the job with the players truly
   away counted; (c) the two rows of game 15 he left without a grade (12:11 and 12:12): meant, or passed over?
   R-562 stays Claude's reading of his rule: bring him the splits it tells wrongly as they turn up in his games.
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
