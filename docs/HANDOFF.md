# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-21, later: the split family read in both halves, R-564 to R-570; no advice from it at the matches in hand)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in
  progress. Rulings run to R-571. The baseline (R-491) is the branch `baseline-2026-11-15`.
- Graded and filed (set f1): thirteen games; game 15 (Men v NwAy, Corrupted) all read Correct. Not graded his new
  way: Weeping Stone, Isle of the Dead. Flags: all 60 advice cards marked; done for now. Numbers from kills:
  dropped as a family (R-557). No stay job at the opening for a team that runs no first flag (R-565).
- The split family (R-558; CLAUDE.md "The split family"). The answer to a split (`cases.py splits`): 1,936
  splits, read 20 and 40 s in (R-567, R-569); six of seven readings hold; no answer clearly better at any size;
  the game clock and the base res do not separate the answers. The main fight while a split is out
  (`cases.py main-fight`): 2,813 situations; four of six readings hold; the side up at the main fight is ahead
  +2.8 win points 180 s on with their split in its base, but was +0.9 ahead the minute before (partly who is
  up); no call clearly better, nothing held out. No cards for either half. No more matches until the engine
  is ready (R-570).
- Last checkpoint (every counted match, this engine): 564 matches, 34,376 plays, no errors; fourteen truths hold;
  313 Classic rows pass, none fail; 132 history rows hold, 3 do not; gate 12 of 12 and 63 of 105 (run at 6e827d0;
  no play has changed since); self-check 21 in 7. Line-up 530 of 583 (2026-11-18, not run again). The flag
  report (`flag_cases.json`, eca99d4) and the numbers report were not run again.

## Next (in order): what is left before the engine is ready to train (R-571; put to him 2026-11-21, his answers wait)
1. Reading faults. Two show in two games and can be built (R-495): who and how many push a flagger (HC v Team
   5:26, 6:04, 8:18 and 1:30; Men v RACK 1:08), and a flag in hand read as a runner (Men v Crew 17:53; cope v
   hold 14:33). One game each, waiting: Men v hold 18:06 and 6:48; numbers through Jade's portal (Men v Crew,
   four rows); Men v RACK 12:06; Men v Crew 12:26; HC v hdm 1:40 (his Jade question) and 5:56; TFS v DMG 22:44.
2. His word on the kinds of play not yet called ready (R-496): the opening, the boost, pushing the flagger,
   held in base, the base res, numbers from a runner away, the Lord push. All 313 Classic rows pass; Weeping
   Stone and Isle of the Dead are not graded his new way.
3. Stage D leftovers, proposed to wait for bundle 5: enemy execution (2.12), the interaction rule (2.13), NPC
   damage by class of bar (R-433), a measure of what is at stake (R-509), the decision to split at all.
4. Stage E (REDESIGN.md): the new families beside the old kinds for one rebuild (R-323), the stand-in prices
   replaced by the win model, the replaced kinds retired, the causal map cleaned, SPEC and METHODS rewritten,
   the readability test, his list of R-398, the merge, then one Train batch on the same 506 matches (he starts
   it; keep gvg.report's flag objects at that rebuild, R-481). Several sessions.
5. The split family again when matches are in (factors for the main fight; the sentence for one moment in
   either half). Players who res at the base onto a split are still read as a collapse.

## Open for Denning
0. Held at his word (R-554, his "make sure you remember"): the cards for a flag in hand, with R-553 to build (no
   runner while the next flag is up is a flag-in-hand decision), and for a double run from the sender's side:
   raise them when more matches are trained. The execution list (R-557): the res, giving ground, fights.
1. Put to him 2026-11-21 (Next 1 to 3): build the two faults that show in two games now; whether the other
   kinds of play are ready or he grades one or two more games first (Weeping Stone, Isle of the Dead); whether
   the stage D leftovers wait for bundle 5.
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
