# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-21, later: the answer to a split read through its first three stages, R-564 to R-569; no advice from it yet)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in
  progress. Rulings run to R-569. The baseline (R-491) is the branch `baseline-2026-11-15`.
- Graded and filed (set f1): thirteen games; game 15 (Men v NwAy, Corrupted) all read Correct. Not graded his new
  way: Weeping Stone, Isle of the Dead. Flags: all 60 advice cards marked; done for now. Numbers from kills:
  dropped as a family (R-557). No stay job at the opening for a team that runs no first flag (R-565).
- The split family (R-558), the answer to a split (CLAUDE.md "The split family"): the record on every split
  play, `cases.py splits`, `data/model/split_cases.json`. 1,936 splits in 453 matches, the first answer read at
  20 s and again at 40 s (R-567), "no answer" told apart (R-569). Readings: six of seven hold. Like spots: no
  answer clearly better than the commonest at any size; held out, one test of twelve shows a gain. Factors
  (matching the split or more against fewer): one row of 55 beyond 1 in 100, none repeated across sizes; the
  game clock and the base res do not separate the answers. So: no advice, no cards, stage 4 not built.
- Last checkpoint (every counted match, this engine): 564 matches, 34,376 plays, no errors; fourteen truths hold;
  313 Classic rows pass, none fail; 132 history rows hold, 3 do not; gate 12 of 12 and 63 of 105; self-check 21
  in 7 (twelve are TFS v DMG 22:44). Line-up 530 of 583 (2026-11-18, not run again). The flag report
  (`flag_cases.json`, eca99d4) and the numbers report were not run again.

## Next (in order)
1. On his word (Open 1): the other half of the family, the main fight while a split is out (4,285 numbers rows
   "from a split elsewhere"; his calls of R-551 with collapse and send more), through the same stages. What an
   answer costs is paid there, which the answer's own table cannot show.
2. The answer to a split again when more matches are in (an answer has 60 to 210 cases a size today): stage 4,
   the sentence for one moment, only where like spots stand round the case and the held-out test shows a gain.
   Before the base res is judged against collapses, tell players who res at the base onto a split apart from a
   collapse. The split's damage against NPCs is not measured.
3. Held for a second game (R-495): Men v hold 18:06 (two of a push standing off it) and 6:48 (a collapse told as
   a push on the flagger); TFS v DMG 22:44; a base res with the attackers at the footmen (HC v hdm 1:40); who and
   how many push a flagger; numbers through Jade's portal; cope v hold 14:33; HC v hdm 5:56 (a flag left lying).
   Not built: a measure of what is at stake (R-509). Then stage E; the clean-up (R-398) after the games.

## Open for Denning
0. Held at his word (R-554, his "make sure you remember"): the cards for a flag in hand, with R-553 to build (no
   runner while the next flag is up is a flag-in-hand decision), and for a double run from the sender's side:
   raise them when more matches are trained. The execution list (R-557): the res, giving ground, fights.
1. Put to him 2026-11-21: go on to the other half of the split family now (recommended), and whether more
   matches should be pulled and trained before the answer to a split is read again.
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
