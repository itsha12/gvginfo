# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-23, late morning: R-615 to R-620; the danger zone at 250, two factors, the sentence)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in
  progress. Rulings run to R-620. The baseline (R-491) is the branch `baseline-2026-11-15`.
- Graded and filed (set f1): thirteen games. Numbers from kills: no family (R-557). The push: no family (R-597).
  Splits read in both halves, no advice at the matches in hand; no more matches until the engine is ready (R-570).
- Built in this chat: the danger zone's heavy damage at 250 a player (R-615); its call's factors are morale (30 or
  more under theirs) and the stand, the 12:00 clock kept and not counted (R-616); one sentence a danger zone base
  res, `cases.res_sentence` (R-617: no verdict); Men v BcS 6:00 and DUM v ohno 8:00 stay out (R-618).
- What it says. At 250: 157 base res in 135 matches, 156 stay; one dies in 13%, two or more within a minute in 8%,
  against 4 to 8% and 2 to 5% with fewer of the three on. One or both factors against (27 stays, started at 71%):
  22% and 19%, against 11% and 5% with neither (129, started at 95%); under the floor of 30. Two or more deaths
  go with 15 points lost against like stays. Nothing is advice, and nothing calls a stay a mistake.
- Last checkpoint (every counted match, this engine): 564 matches, 33,371 plays, no errors; fourteen truths hold;
  313 Classic rows pass, none fail (18 of 25 Classic base res rows check for context); 136 history rows hold, 5
  do not; self-check 6 in 4. Base res report written on it; the other eight unchanged (only base res plays moved
  on the development set; a full before and after was not compared).
- Flag cards (main, `flag_cards.json`, 63): six ask to be marked again (HC v Team 3:42 and 6:34, Men v Crew 4:53,
  옷옷옷옷 v RACK 6:15, Men v hold 6:18, hold v RACK 5:21), five are unmarked (Men v Crew 12:23, 옷옷옷옷 v hdm
  3:21, game 15's 8:19, 12:11, 13:29); four are gone.

## Next (in order): the engine substantially finished before the merge and training (R-571, R-572)
1. His answers to "Open for Denning" 1. Then the hand-off (R-620): the record of every put-down of a flag (who put
   it down and of which line, where, the enemy within reach, what became of it: a team mate took it up, its carrier
   took it up again, or it was returned), checked on RJT v RACK's four known returns (R-481); then his three points
   as readings on it (tactics F52 to F54) and the price of a return. Records only: no play may change.
2. The Lord push: picked rows from late games.
3. The measurements (R-572): enemy execution (2.12), the interaction rule (2.13), NPC damage by kind of bar
   (R-433), a measure of what is at stake (R-509), the decision to split at all (R-558); and with them what a team
   held in its base does (R-619), if he agrees to read it there.
4. Stage E (REDESIGN.md): the new families beside the old kinds for one rebuild (R-323), the stand-in prices
   replaced by the win model (the danger zone's sentence then goes on the Game review row), the replaced kinds
   retired, the causal map cleaned, SPEC and METHODS rewritten, the readability test, his list of R-398, the
   merge, then one Train batch on the same 506 matches (he starts it; keep gvg.report's flag objects, R-481).
5. With matches in: the split family again; the danger zone's two factors read again (the clock with them).

## Open for Denning
0. Held at his word (R-554, his "make sure you remember"): the cards for a flag in hand, with R-553 to build, and
   for a double run from the sender's side: raise them when more matches are trained. The execution list (R-557).
1. Put to him on 2026-11-23, in the chat; set out again if he has not answered:
   - A team held in its base (R-619). Claude's answer: no family and no cards; the rows stay told with their job
     (R-478); what the held team does is read as execution with step 3. Does he agree, and is any choice a held
     team has a decision to him beyond the two already told as their own plays (a split out of the base, a flag
     held at home): who to kill first, a res tried or the base res waited for, the pit or the door?
   - The hand-off (R-620). Does a flag left lying go back by itself after a time, or only when an enemy picks it
     up? Is "out of range of the enemy" no enemy player within about an aggro bubble of the put-down, or further?
     For his third point, is the primary defender the usual split responder as measured (R-598), or by build?
2. Eleven flag cards to mark (State). R-576's reading (held in base by five or more) is Claude's, and R-575 is
   applied to Nomad's as to Jade: bring him what either tells wrongly as it turns up in his games.
3. Tolkano: no build (his word): give him date, guilds, hall and length with every example.

## Running it
- Train batch: the "Train batch" workflow (METHODS.md; `blind` stays no). Never queue two runs. At the next rebuild,
  keep gvg.report's flag objects, which `replay_trim.mjs` drops (R-481).
- Local engine: `git fetch --depth 1 --no-filter origin +replays:refs/remotes/origin/replays`. `jobs.py`,
  `moments.py`, the gate, the line-up and `confidence.py` need only Python; `cases.py` needs numpy and scikit-learn
  (`cache.py sync pull`, `warm` only for the fitted models). A full run (`moments.py all`) takes about 11 minutes
  on two cores; `cases.py ladder` before `cases.py test` (R-545), each kept with `--json data/model/<name>.json`.
  Set `PYTHONDONTWRITEBYTECODE=1`. The key, `dev_set.json` and `game_reviews.json` are written on main: pass `--key
  <main>/data/model/review_key.json`, copy both to the branch after a change; `hall_features.json` is changed on both.
- Site check: `python3 -m http.server`, then playwright with `/usr/bin/google-chrome`, api.github.com mocked.

## Cautions
- Never print or decode a sealed field (blind picks, golden moments) in a chat.
- Don't merge `bundle-4` piecemeal (R-322). Label, golden and review mark files are saved whole by the site: after a
  change here, he reloads the page first. Hall labels are saved to main: copy changed `data/maps/labels/*.json` to
  the branch before reading a hall (the export refuses otherwise).
- Transcripts never go in the repo: paraphrased statements only. Party slots are in `data/matches/`, not the
  replays. Refresh the branch's `golden_moments.json` first.
