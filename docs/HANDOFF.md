# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-22, evening: R-588 to R-590 answered; the three reports built on them)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in
  progress. Rulings run to R-590. The baseline (R-491) is the branch `baseline-2026-11-15`.
- Graded and filed (set f1): thirteen games. Numbers from kills: no family (R-557). Splits read in both halves,
  no advice from them at the matches in hand; no more matches until the engine is ready (R-570).
- Built on 2026-11-22 (CLAUDE.md says how each is read and what was tried and taken out): R-583 to R-587, the
  double count of TFS v DMG, stage 1 of pushes, holds, the base res and the opening (`cases.py`), and from his
  answers of the evening the solo push on their runs (R-588), the base res by health (R-589) and the opening by
  his four points with a 5 and 7 minute record (R-590). Pushes and holds have passed stage 2.
- Last checkpoint (every counted match, this engine): 564 matches, 33,371 plays, no errors; fourteen truths hold;
  313 Classic rows pass, none fail; 136 history rows hold, 5 do not; self-check 6 in 4. The nine reports are
  written on it. Not run again on it: the gate and the line-up.
- Flag cards (main, `flag_cards.json`, 63): six ask to be marked again (HC v Team 3:42 and 6:34, Men v Crew 4:53,
  옷옷옷옷 v RACK 6:15, Men v hold 6:18, hold v RACK 5:21), five are unmarked (Men v Crew 12:23, 옷옷옷옷 v hdm
  3:21, game 15's 8:19, 12:11, 13:29); four are gone.

## Next (in order): the engine substantially finished before the merge and training (R-571, R-572)
1. His answers to "Open for Denning" 1, then: the push as part of the answer to their run (if he says so, in the
   flag family's like spots, `Scenario`, and no family of its own); stage 3 for holds; the opening's stage 2 on
   whichever readings he picks; the hand-off told apart (a first flag returned as it changes hands).
2. The Lord push: picked rows from late games.
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
1. Put to him on 2026-11-22 (evening), in the chat; set out again if he has not answered:
   - The push: is pushing their flagger one of the answers to their run (stay, send a runner, push with one, push
     with two or more, both), to be read with the flag family, or a decision of its own?
   - The base res: with so few costly stays (13 of 945), is it a decision to read at all, or a thing to note when
     it happens (low on health in their base as the res lands)? And where "base" should end for it.
   - The opening: who the usual split response is (named by build, or measured as the player sent from the main
     team, the runner left out); and which of the readings he wants taken to the general table.
2. Eleven flag cards to mark (State). R-576's reading (held in base by five or more) is Claude's, and R-575 is
   applied to Nomad's as to Jade: bring him what either tells wrongly as it turns up in his games.
3. Tolkano: no build (his word): give him date, guilds, hall and length with every example.

## Running it
- Train batch: the "Train batch" workflow (METHODS.md; `blind` stays no). Never queue two runs. At the next rebuild,
  keep gvg.report's flag objects, which `replay_trim.mjs` drops (R-481).
- Local engine: `git fetch --depth 1 --no-filter origin +replays:refs/remotes/origin/replays`. `jobs.py`,
  `moments.py`, the gate, the line-up and `confidence.py` need only Python; `cases.py` needs numpy and scikit-learn
  (`cache.py sync pull`, `warm` only for the fitted models). A full run (`moments.py all`) takes about 17 minutes;
  `cases.py ladder` before `cases.py test` (R-545), each kept with `--json data/model/<name>.json`. Set
  `PYTHONDONTWRITEBYTECODE=1`. The key, `dev_set.json` and `game_reviews.json` are written on main: pass `--key
  <main>/data/model/review_key.json`, copy both to the branch after a change; `hall_features.json` is changed on both.
- Site check: `python3 -m http.server`, then playwright with `/usr/bin/google-chrome`, api.github.com mocked.

## Cautions
- Never print or decode a sealed field (blind picks, golden moments) in a chat.
- Don't merge `bundle-4` piecemeal (R-322). Label, golden and review mark files are saved whole by the site: after a
  change here, he reloads the page first. Hall labels are saved to main: copy changed `data/maps/labels/*.json` to
  the branch before reading a hall (the export refuses otherwise).
- Transcripts never go in the repo: paraphrased statements only. Party slots are in `data/matches/`, not the
  replays. Refresh the branch's `golden_moments.json` first.
