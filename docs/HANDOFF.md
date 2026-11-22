# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-21, evening: who pushes a flagger rebuilt, R-573; Isle of Jade, R-574 built, R-575 ruled only)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in
  progress. Rulings run to R-575. The baseline (R-491) is the branch `baseline-2026-11-15`.
- Graded and filed (set f1): thirteen games (Weeping Stone and Isle of the Dead not graded his new way). Flags:
  all 60 advice cards marked. Numbers from kills: no family (R-557). Splits read in both halves, no advice
  from them at the matches in hand; no more matches until the engine is ready (R-570).
- Who pushes a flagger (R-573, `Moments.flag_pushes`; CLAUDE.md says how it is read): four of his five rows read
  as he reads them (HC v Team 1:30, 5:26, 8:18; Men v RACK 1:08). Three rows he graded correct say another
  number now (HC v Team 0:40, Men v hold 3:04, HC v hdm 14:24): put to him (Open 2).
- Jade: the footmen are not in the base at a base res (R-574, built); R-575 (the portal) is step 1 below.
- Last checkpoint (every counted match, this engine): 564 matches, 34,367 plays, no errors; fourteen truths hold;
  313 Classic rows pass, none fail; 132 history rows hold, 3 do not; gate 12 of 12 and 63 of 105; self-check
  21 in 7. Line-up 530 of 583 (2026-11-18). The flag, numbers and split reports were not run again.

## Next (in order): the engine substantially finished before the merge and training (R-571, R-572)
1. R-575 at the root, in the one reading of who is in which fight (`Moments._near`, `linked`). Tried: the two
   ends of a teleporter that works both ways one step apart (the shorter of the straight distance and the way
   through, hop ends from `hall.hops`, halls whose features say `two_way`: Jade and Nomad's). It closed Men v
   Crew 15:10 and cope v Team 6:04 and 11:56; it told Men v Crew 24:34 (Classic) from 24:26 and broke cope v
   Team 13:34 to 14:46 as one situation. Find why the numbers start 8 s sooner there before building it again.
   Men v Crew 14:24 is another fault (nobody through the portal: a stand-off read as numbers, R-405).
2. The flag held at home, once he has answered Open 1: what tells a held flag from an unsuccessful run.
3. HC v Team 6:04, once he has answered Open 3 (when a player who has just capped is the flagger again).
4. Picked rows for the faults seen in one game (R-572): like moments from other matches for Men v hold 18:06
   and 6:48, Men v RACK 12:06, Men v Crew 12:26, HC v hdm 5:56; TFS v DMG 22:44 (the self-check) as a bug.
5. The kinds Claude reads as ready (R-572): the opening, held in base, the base res and now pushing the flagger,
   each through the stages as flags and splits were. The Lord push: picked rows from late games first.
6. The measurements (R-572): enemy execution (2.12), the interaction rule (2.13), NPC damage by kind of bar
   (R-433), a measure of what is at stake (R-509), the decision to split at all (R-558).
7. Stage E (REDESIGN.md): the new families beside the old kinds for one rebuild (R-323), the stand-in prices
   replaced by the win model, the replaced kinds retired, the causal map cleaned, SPEC and METHODS rewritten,
   the readability test, his list of R-398, the merge, then one Train batch on the same 506 matches (he starts
   it; keep gvg.report's flag objects at that rebuild, R-481).
8. The split family again when matches are in (players who res at the base onto a split still read as a collapse).

## Open for Denning
0. Held at his word (R-554, his "make sure you remember"): the cards for a flag in hand, with R-553 to build, and
   for a double run from the sender's side: raise them when more matches are trained. The execution list (R-557).
1. Put to him 2026-11-21: a held flag or an unsuccessful run. cope v hold 14:09 (Monk 4 stands with it 31 s in
   his team: "definitely not a flag run"); Men v hold, Nomad's, 7:46 and 8:12 (Air Ele 3, 7 s and 10 s in his
   team: "an unsuccessful flag run"); Men v Crew 18:21 (the Warrior, 10 s, runs 1,270 nearer the stand in his
   team and puts it down 2 s before Crew's boost: he saw no runner, "I could be wrong").
2. Put to him: the three rows he graded correct that say another number now (State), and whether the footmen
   of Warrior's Isle, Weeping Stone, Meditation, Wurms and Solitude are out of the base at a base res as Jade's.
3. Put to him: HC v Team 5:25, who the three are (the Hammer on the Mes/A from 5:24; the Warrior beside them to
   5:30; the Ranger and the Prot behind), and whether a runner who has just capped and is hit as he leaves the
   stand is already the flagger pushed.
4. Tolkano: no build (his word): give him date, guilds, hall and length with every example. R-562 is Claude's
   reading of his rule: bring him the splits it tells wrongly as they turn up in his games.

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
