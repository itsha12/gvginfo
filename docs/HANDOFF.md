# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-21, night: the picked rows of R-572 put to him; no engine change since R-573 to R-578)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in
  progress. Rulings run to R-578. The baseline (R-491) is the branch `baseline-2026-11-15`.
- Graded and filed (set f1): thirteen games (Weeping Stone and Isle of the Dead not graded his new way). Flags:
  all 60 advice cards marked. Numbers from kills: no family (R-557). Splits read in both halves, no advice
  from them at the matches in hand; no more matches until the engine is ready (R-570).
- Built this session, each with his word (CLAUDE.md says how each is read): who pushes a flagger (R-573, R-577,
  `flag_pushes`); a flag held at home is no run (R-576, `_held_carries`); the footmen are not in the base at a
  base res on Jade and five other halls (R-574, R-578, `hall_features.json`); players through a two-way
  teleporter are of the main fight on either side (R-575, `_reach`); numbers wholly in a stand-off are not told
  (R-405, `numbers_plays`). Both two-game faults of R-572 are built.
- Last checkpoint (every counted match, this engine): 564 matches, 34,272 plays, no errors; fourteen truths hold;
  313 Classic rows pass, none fail; 130 history rows hold, 3 do not; gate 12 of 12 and 63 of 105; self-check
  21 in 7. Line-up 530 of 583 (2026-11-18). The five reports and the flag cards are written on this reading.
- Flag cards (main, `flag_cards.json`, 63): two ask to be marked again (HC v Team 3:42, HC v cope 0:30) and
  three are new (game 15, Men v NwAy 8:19, 12:11, 13:29); two of hold v RACK stay listed as gone.

## Next (in order): the engine substantially finished before the merge and training (R-571, R-572)
1. Picked rows (R-572): put to him 2026-11-21 (night), unanswered ("Open for Denning" 1). File his answers as
   set p3 of the key; build only what shows in two games. TFS v DMG 22:44 (twelve of the 21 self-check counts)
   is diagnosed, not built: a lone player whose team is dead is told as a split under a full collapse (right)
   and at once as the "1 v 8" of the main fight's numbers (wrong: fix in `Moments._numbers`).
2. The kinds Claude reads as ready (R-572): the opening, held in base, the base res and now pushing the flagger,
   each through the stages as flags and splits were. The Lord push: picked rows from late games first.
3. The measurements (R-572): enemy execution (2.12), the interaction rule (2.13), NPC damage by kind of bar
   (R-433), a measure of what is at stake (R-509), the decision to split at all (R-558).
4. Stage E (REDESIGN.md): the new families beside the old kinds for one rebuild (R-323), the stand-in prices
   replaced by the win model, the replaced kinds retired, the causal map cleaned, SPEC and METHODS rewritten,
   the readability test, his list of R-398, the merge, then one Train batch on the same 506 matches (he starts
   it; keep gvg.report's flag objects at that rebuild, R-481).
5. The split family again when matches are in (players who res at the base onto a split still read as a collapse).

## Open for Denning
0. Held at his word (R-554, his "make sure you remember"): the cards for a flag in hand, with R-553 to build, and
   for a double run from the sender's side: raise them when more matches are trained. The execution list (R-557).
1. The picked rows (each with date, guilds, hall, length, time and link in the chat of 2026-11-21, night):
   - Men v hold 18:06 (on the way home to a collapse, read as a split): Apes v cope ce7e957d 11:20 (like it),
     push v True 597fe160 11:18 (may be a true counter-split). Only six such rows in 564 matches.
   - Men v hold 6:48 (flagger carrying his flag home with his team, read as pushed): one like row in 1,278
     pushes, Men v cope 2ce13ef6 11:10. Claude's recommendation: drop it unless he rules on the original.
   - Men v RACK 12:06 with Men v Crew 8:18 and 20:10 (numbers for 10 to 12 s): Men v hook ad75813a 2:20, hold v
     hook fe0bdc51 12:56, Book v Crew 6aaa0f6d 5:08. 409 of 2,083 "split elsewhere" numbers situations last 12 s
     or less; of his 11 graded ones none is Classic (13 to 20 s: 5 of 10). Two games already: asked whether a
     player away from his fight under JOIN_S has not left it (the mirror of R-350).
   - Men v Crew 12:26: asked what he meant (Crew's Water Ele capped at 12:23 and set off again at 13:17; the row
     pairs Men's Derv taking up the Ranger's flag at 12:26, then holding it 1:51, with that later run).
   - HC v hdm 5:56 (a flag left lying, taken up later and capped, no flag row): 옷옷옷옷 v cope 01c0b3c1 4:55,
     Book v OG 76b61497 10:56, Crew v Team e7a93c30 10:41. 32 such caps in 29 matches with no flag play at all.
   Five flag cards to mark (State). R-576's reading (held in base by five or more) is Claude's, and R-575 is
   applied to Nomad's as to Jade: bring him what either tells wrongly as it turns up in his games.
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
