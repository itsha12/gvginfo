# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-22: R-583 answered; R-580, R-581, R-583 and the double count built on `bundle-4`)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in
  progress. Rulings run to R-583. The baseline (R-491) is the branch `baseline-2026-11-15`.
- Graded and filed (set f1): thirteen games. Numbers from kills: no family (R-557). Splits read in both halves,
  no advice from them at the matches in hand; no more matches until the engine is ready (R-570).
- Built this session (CLAUDE.md says how each is read and what was tried and taken out): R-583 (`_numbers`,
  `level`), R-580 (`Moments.handed_on`), R-581 (`jobs._flag_rows`); the double count of TFS v DMG 22:44
  (`_split_candidates` read until it settles; a defender with no split left is in the main fight); two small
  flag faults; `at_told` on the push, held-in-base and base res plays; stage 1 of pushing the flagger
  (`cases.py pushes`) and of a team held in its base (`cases.py held`): every reading but one holds.
- Last checkpoint (every counted match, this engine): 564 matches, 33,892 plays, no errors; fourteen truths hold;
  313 Classic rows pass, none fail; 137 history rows hold, 4 do not; self-check 6 in 4. The seven reports are
  written on it. Not run again on it: the gate and the line-up.
- Flag cards (main, `flag_cards.json`, 63, written from the run before the last fixes; no graded game changed
  since): six ask to be marked again (HC v Team 3:42 and 6:34, Men v Crew 4:53, 옷옷옷옷 v RACK 6:15, Men v hold
  6:18, hold v RACK 5:21; four only a verdict at the range's edge), five are unmarked (Men v Crew 12:23,
  옷옷옷옷 v hdm 3:21, game 15's 8:19, 12:11, 13:29); four are gone (two of hold v RACK, Men v Crew 5:52, 12:26).

## Next (in order): the engine substantially finished before the merge and training (R-571, R-572)
1. His answers to the four questions put to him on 2026-11-22 ("Open for Denning" 1): each changes a reading
   (R-583's reach, the length of R-581, the opening's words). File each as a ruling and build it.
2. The kinds Claude reads as ready (R-572), each through his four stages. Pushing the flagger and held in base
   have stage 1 (the readings hold): next their general tables put to him, then like spots. The base res and
   the opening are not begun (the base res plays carry `at_told`). The Lord push: picked rows from late games.
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
1. Put to him on 2026-11-22, each with its replay link (set them out again in the chat if he has not answered):
   - R-583 took out two rows he graded Visible and correct (Men v Crew 23:30, Men v hold 12:46: a player leaves
     and the other team's player leaves 12 to 14 s later). Level, as he ruled, or a decision?
   - 268 brief rows "from players split elsewhere" are still told: nobody was in the fight within 12 s either
     side (a short fight with a player elsewhere throughout). Of three he has graded: Weak (Men v hold 0:24),
     No decision (hold v Men 0:24), Visible and correct (Men v hold 18:18). Stop telling these too?
   - R-581's length (180 s) is Claude's draft. It changes 옷옷옷옷 v hdm's opening (Visible, correct: now the
     flag put down at 0:03 and the Warrior sent for it at 3:15) and tells Men v 옷옷옷옷 5:16 the same way.
   - R-580 names the hand-on in Men v NwAy's opening (Classic): "brought up by Mes/A, handed to 8 Monk".
   Asked as (a)/(b) options in the chat; none answered when this was written.
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
