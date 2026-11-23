# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-22, night: R-591 to R-596 answered and built; the opening, base res and push reports written again)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in
  progress. Rulings run to R-596. The baseline (R-491) is the branch `baseline-2026-11-15`.
- Graded and filed (set f1): thirteen games. Numbers from kills: no family (R-557). Splits read in both halves,
  no advice from them at the matches in hand; no more matches until the engine is ready (R-570).
- Built this session (CLAUDE.md says how each is read): the opening judged call by call on flags, kills, NPCs,
  boosts and the chance of winning at 5:00 and 8:00, with like spots where teams divide (R-596); the usual split
  response as he defines it (R-593); the base res as the greedy stay, four marks read 20 s before the res (R-592,
  R-595); the push on his five questions (R-591). Records only: no play moved.
- What they say: no opening call is advice (capping first or second in an 8 v 8 is not clear; holding the flag
  reads better as it fell but not on unseen matches; eight against seven nearly all hold, so nothing to set
  beside it). The greedy stay shows (two or more die in 3% against 0%) but hardly anyone leaves, so leaving cannot
  be judged. The push gains flags only with two or more players and nothing else.
- Last checkpoint (every counted match, this engine): 564 matches, 33,371 plays, no errors; fourteen truths hold;
  313 Classic rows pass, none fail; 136 history rows hold, 5 do not; self-check 6 in 4. Opening, base res and
  push reports written on it; the other six unchanged. Not run again on it: the gate and the line-up.
- Flag cards (main, `flag_cards.json`, 63): six ask to be marked again (HC v Team 3:42 and 6:34, Men v Crew 4:53,
  옷옷옷옷 v RACK 6:15, Men v hold 6:18, hold v RACK 5:21), five are unmarked (Men v Crew 12:23, 옷옷옷옷 v hdm
  3:21, game 15's 8:19, 12:11, 13:29); four are gone.

## Next (in order): the engine substantially finished before the merge and training (R-571, R-572)
1. His answers to "Open for Denning" 1, then what they call for; stage 3 for holds; the hand-off told apart (a
   first flag returned as it changes hands).
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
1. Put to him on 2026-11-22 (night), in the chat; set out again if he has not answered:
   - The push: no family (Claude's recommendation: only two or more players gain flags, which the flag readings
     already hold, and nothing else shows), or a family all the same?
   - The split response: for his fourth point on the opening, the 8 Monk (his definition as measured, 21 of 22
     guilds) or the player other than a monk most often sent?
   - The opening's clock: he wrote that 7:00 is too far out and named 8:00; it is read at 3:00, 5:00 and 8:00.
     Which did he mean?
   - The greedy stay: hook v Men 6:00 reads as the main team with four past the shrine, against his word; and
     whether the four marks are the right ones before the family goes further.
   - Holding the flag at the stand: does a team hold because it is in control (so the gain marks the spot), as
     the unseen matches suggest?
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
