# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-23, later: R-632 to R-635; the Lord push page on gvg.report's own figures)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in
  progress. Rulings run to R-635. The baseline (R-491) is the branch `baseline-2026-11-15`.
- Graded and filed (set f1): thirteen games. Numbers from kills: no family (R-557). The push: no family (R-597).
  A team held in its base: no family, execution (R-621). Splits read in both halves, no advice at the matches in
  hand; no more matches until the engine is ready (R-570).
- Built in this chat (no engine change, no play moved). The Lord push page: Model > Game review, the view "Lord
  push", the eight picked rows (`data/model/lord_rows.json`, written by `review.py lord` on the branch), his marks
  to `lord_row_marks.json` (R-633). Lord damage is gvg.report's to say, everywhere (R-632): its record holds each
  team's aggressiveness (R-634), every hit by the second, Entourage, the pit NPCs and each Lord's health; the trim
  keeps only the totals, so the record of the seven games is kept in `lord_gvg.json` and each row reads it.
- What it says. The danger zone at 250: 157 base res in 135 matches, 156 stay; one dies in 13%, two or more in 8%
  (4 to 8% and 2 to 5% outside it). The hand-off: a flag put down is returned 13% of the time out of range, 24%
  with one enemy in range, 41% with two or more; a returned hand-off costs a third of a flag a minute on and is
  made up by three minutes; a later flag run to the stand on a frontliner and one handed on before it do not
  differ clearly; the opening at eight against seven (23) and held flags (79) are too few. Nothing is advice.
- Last checkpoint (every counted match, this engine): 564 matches, 33,371 plays, no errors; fifteen truths hold;
  313 Classic rows pass, none fail (18 of 25 Classic base res rows check for context); 136 history rows hold, 5
  do not; self-check 6 in 4. Base res and hand-off reports written on it; the other eight unchanged.
- Flag cards (main, `flag_cards.json`, 63): six ask to be marked again (HC v Team 3:42 and 6:34, Men v Crew 4:53,
  옷옷옷옷 v RACK 6:15, Men v hold 6:18, hold v RACK 5:21), five are unmarked (Men v Crew 12:23, 옷옷옷옷 v hdm
  3:21, game 15's 8:19, 12:11, 13:29); four are gone.

## Next (in order): the engine substantially finished before the merge and training (R-571, R-572)
1. The Lord push: his marks on the eight rows, read from `lord_row_marks.json` (file them as set p4 of the key
   with his words; a Classic row read wrongly is fixed first, at the root), then what they say of the reading: a
   lone player or two with no monk as a "push", visits under 15 s, the aim (179 of 191 read "Lord damage").
2. The measurements (R-572): enemy execution (2.12), the interaction rule (2.13), NPC damage by kind of bar
   (R-433), a measure of what is at stake (R-509), the decision to split at all (R-558); and with them what a team
   held in its base does in the first seconds of a hold (R-621).
3. Stage E (REDESIGN.md): the new families beside the old kinds for one rebuild (R-323), the stand-in prices
   replaced by the win model (the danger zone's sentence then goes on the Game review row), the replaced kinds
   retired, the causal map cleaned, SPEC and METHODS rewritten, the readability test, his list of R-398, the
   merge, then one Train batch on the same 506 matches (he starts it). Before it, a new trim keeps gvg.report's flag
   objects (R-481), Lord damage record (R-632), prot, degen, interrupt and death-recap items (R-636 to R-639), read by the engine;
   who stripped which enchantment is read from our replays (R-637).
4. With matches in: the split family again; the danger zone's two factors; the opening hand-off and held flags
   (and from them which builds are the primary defender or the flag runner, R-628).

## Open for Denning
0. Held at his word (R-554, his "make sure you remember"): the cards for a flag in hand, with R-553 to build, and
   for a double run from the sender's side: raise them when more matches are trained. The execution list (R-557).
1. The eight Lord push rows wait on the page for his grade and mark (R-633; never in the chat), each with
   gvg.report's own figures. Put to him, not yet answered: what the trim keeps of the Lord record at the rebuild.
   He asked for the aggressiveness counts only; recommended beside them the hits by the second and the health
   where it changes (3 KB a match, no more to download), without which R-635 cannot be read.
2. Eleven flag cards to mark (State). R-576's reading (held in base by five or more) is Claude's, and R-575 is
   applied to Nomad's as to Jade: bring him what either tells wrongly as it turns up in his games.
3. Tolkano: no build (his word): give him date, guilds, hall and length with every example.

## Running it
- Train batch: the "Train batch" workflow (METHODS.md; `blind` stays no). Never queue two runs. At the next rebuild,
  keep what R-481, R-632 and R-636 to R-639 list (dropped by the trim and `extract.mjs`; R-636 in its own file a match).
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
