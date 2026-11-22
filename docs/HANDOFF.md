# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-21, evening: who pushes a flagger, the flag held at home, the base res at footmen: R-573 to R-578)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in
  progress. Rulings run to R-578. The baseline (R-491) is the branch `baseline-2026-11-15`.
- Graded and filed (set f1): thirteen games (Weeping Stone and Isle of the Dead not graded his new way). Flags:
  all 60 advice cards marked. Numbers from kills: no family (R-557). Splits read in both halves, no advice
  from them at the matches in hand; no more matches until the engine is ready (R-570).
- Built this session, each with his word (CLAUDE.md says how each is read): who pushes a flagger (R-573, R-577,
  `flag_pushes`); a flag held at home is no run (R-576, `_held_carries`); the footmen are not in the base at a
  base res on Jade and five other halls (R-574, R-578, `hall_features.json`). Both two-game faults of R-572
  are built. R-575 (Jade's portal) is ruled and not built: step 1 below.
- Last checkpoint (every counted match, this engine): 564 matches, 34,317 plays, no errors; fourteen truths hold;
  313 Classic rows pass, none fail; 132 history rows hold, 3 do not; gate 12 of 12 and 63 of 105; self-check
  21 in 7. Line-up 530 of 583 (2026-11-18). Not written again: the flag, numbers and split reports, and the
  flag cards (37 flag plays fewer over every match; no marked f1 game lost a flag row on the development set).

## Next (in order): the engine substantially finished before the merge and training (R-571, R-572)
1. R-575 at the root, in the one reading of who is in which fight (`Moments._near`, `linked`). Tried: the two
   ends of a teleporter that works both ways one step apart (the shorter of the straight distance and the way
   through, hop ends from `hall.hops`, halls whose features say `two_way`: Jade and Nomad's). It closed Men v
   Crew 15:10 and cope v Team 6:04 and 11:56; it told Men v Crew 24:34 (Classic) from 24:26 and broke cope v
   Team 13:34 to 14:46 as one situation. Find why the numbers start 8 s sooner there before building it again.
   Men v Crew 14:24 is another fault (nobody through the portal: a stand-off read as numbers, R-405).
2. Run `cases.py ladder`, `test`, `splits` and `main-fight` on the new reading, and write the flag cards again
   with `--site` (tell him how many he is asked to mark again, R-549).
3. Picked rows for the faults seen in one game (R-572): like moments from other matches for Men v hold 18:06
   and 6:48, Men v RACK 12:06, Men v Crew 12:26, HC v hdm 5:56; TFS v DMG 22:44 (the self-check) as a bug.
4. The kinds Claude reads as ready (R-572): the opening, held in base, the base res and now pushing the flagger,
   each through the stages as flags and splits were. The Lord push: picked rows from late games first.
5. The measurements (R-572): enemy execution (2.12), the interaction rule (2.13), NPC damage by kind of bar
   (R-433), a measure of what is at stake (R-509), the decision to split at all (R-558).
6. Stage E (REDESIGN.md): the new families beside the old kinds for one rebuild (R-323), the stand-in prices
   replaced by the win model, the replaced kinds retired, the causal map cleaned, SPEC and METHODS rewritten,
   the readability test, his list of R-398, the merge, then one Train batch on the same 506 matches (he starts
   it; keep gvg.report's flag objects at that rebuild, R-481).
7. The split family again when matches are in (players who res at the base onto a split still read as a collapse).

## Open for Denning
0. Held at his word (R-554, his "make sure you remember"): the cards for a flag in hand, with R-553 to build, and
   for a double run from the sender's side: raise them when more matches are trained. The execution list (R-557).
1. Nothing is waiting on him. R-576's reading is Claude's (the team held in its base by five or more): bring him
   the carries it tells wrongly as they turn up in his games, as with R-562.
2. Tolkano: no build (his word): give him date, guilds, hall and length with every example.

## Running it
- Train batch: the "Train batch" workflow (METHODS.md; `blind` stays no). Never queue two runs. At the next rebuild,
  keep gvg.report's flag objects, which `replay_trim.mjs` drops (R-481).
- Local engine: `git fetch --depth 1 --no-filter origin +replays:refs/remotes/origin/replays`. `jobs.py`,
  `moments.py`, the gate, the line-up and `confidence.py` need only Python; `cases.py` needs numpy and scikit-learn
  (`cache.py sync pull`, `warm` only for the fitted models). A full run (`moments.py all`) takes about 15 minutes;
  `cases.py ladder` before `cases.py test` (R-545). `PYTHONDONTWRITEBYTECODE=1`. The review key, `dev_set.json` and
  `game_reviews.json` are written on main: pass `--key <main>/data/model/review_key.json`, and copy the key and
  `dev_set.json` to the branch after changing them; `data/maps/hall_features.json` is changed on both.
- Site check: `python3 -m http.server`, then playwright with `/usr/bin/google-chrome`, api.github.com mocked.

## Cautions
- Never print or decode a sealed field (blind picks, golden moments) in a chat.
- Don't merge `bundle-4` piecemeal (R-322). Label, golden and review mark files are saved whole by the site: after a
  change here, he reloads the page first. Hall labels are saved to main: copy changed `data/maps/labels/*.json` to
  the branch before reading a hall (the export refuses otherwise).
- Transcripts never go in the repo: paraphrased statements only. Party slots are in `data/matches/`, not the
  replays. Refresh the branch's `golden_moments.json` first.
