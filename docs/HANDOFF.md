# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-20: all 60 flag cards marked; flags done for now; numbers from kills withdrawn as a decision family (R-557); splits next; R-548 to R-557)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` (eca99d4) and lands in
  one piece, then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run
  in progress. Rulings run to R-557. The baseline (R-491) is the branch `baseline-2026-11-15`.
- Graded and filed (set f1): twelve games. Not graded his new way: Corrupted, Weeping Stone, Isle of the Dead.
- Flag advice (stage 4 of the flag family): he marked all 61 cards (58 told correctly; his own call the same as a
  clear reading in 27 of 33). The three he corrected are set c1 of the review key, each fixed: whoever set off
  first is sending (an answer before its run stops the run), the runner who waited back at his spawn, a flag of
  ours already up the field (`Moments.flag_up`). R-548: a runner sets off when he goes for good (`run_starts`).
- The cards were written again from e60a56d (60; `--site` keeps ids and his marks, `changed` only where a card
  says something else) and he marked the 14 that waited: all told correctly. "Look for a kill first, then send"
  (`own` = wait; R-549) on 3 of the 14; his 23 other "hold" marks were made without it. His notes on three games
  (key c1-4 to c1-6): hold v RACK 2:34, 4:42, 7:29 are flag decisions with no card (a flag in hand; a double run
  from the sender's side); HC v hdm 5:56, a flag left lying and taken up by another player, is not read (held).
- Checkpoint run (every counted match, engine eca99d4): 564 matches, 34,823 plays, no errors, self-check 7 in 5.
  The fourteen truths hold; 281 Classic rows pass, none fail; 132 history rows hold, 3 do not. Gate 12 of 12 and
  63 of 105; line-up and comms 530 of 583 (last run 2026-11-18, not run again).
- The similar cases (`cases.py test`, `data/model/flag_cases.json`), 4,276 cases. Section 8, as it fell, 180 s on:
  - Us holding the stand (1,260): a runner within 15 s -2.0 win points; 15 to 90 s -1.3; none for 90 s +1.1, which
    is -4.3 where their flag got in (257) and +6.9 where it did not (240, teams that started at 76%).
  - Them holding it (533): a runner within 15 s +1.7, 15 to 90 s 0.0, none for 90 s -0.2.
  - Held out, read at 15 s: better at 60 s (+1.3), 90 s (+1.2, 0.1 to 2.4) and 180 s (+2.6, 0.8 to 4.5): the first
    build on which all three show; not yet a gain to call (near the line a card's reading moves with the fit: 11 of
    59 changed between clear and not clear, none reversed). Read at 30 s: nothing. Their boost: +7.0 (3.3 to 10.6).

## Next (in order)
1. The split family, at his word: the answer to a split (no answer, one defender, mirror, two monks, add one,
   full collapse), the main fight while a split is out (3,729 numbers plays "from a split elsewhere"; his calls of
   R-551 plus collapse and send more), each through the four stages. First the readings, put to him 2026-11-20:
   (a) players moving to join their main team, or toward a back door, told as a split (Men v hold 9:56, 10:24,
   11:10, 19:38); (b) a collapse told as a split (Men v hold 18:06) or as a push on the flagger (6:48), and a
   collapse that kills within seconds not told, its death left on the 1 v 1 row (QenK v Fun 6:37, NwAy v ohno
   5:24); (c) a main team push of six by the back door told as a split of three (HC v Team 12:32); (d) hold v
   RACK 2:42, No decision with no words. He says when splits are ready (R-496). Numbers from kills: dropped (R-557);
   what is built stays (`_numbers_at`, `_hard_res`, `cases.py numbers`, `numbers-cards`): no cards to him.
2. Held for a second game (R-495): a base res with the attackers at the footmen (HC v hdm 1:40, Jade); Men v hold
   6:48, a collapse told as a push on the flagger; who and how many push a flagger; numbers through Jade's portal;
   cope v hold 14:33; HC v hdm 5:56 (a flag left lying, taken up and capped). For the split family: QenK v Fun 6:37
   and NwAy v ohno 5:24. Not built: a measure of what is at stake (R-509). Then stage E; the clean-up (R-398, and
   `st.stand_owner` on a whole second) after the games.

## Open for Denning
0. Held at his word (R-554, his "make sure you remember"): the cards for a flag in hand, with R-553 to build (no
   runner while the next flag is up is a flag-in-hand decision), and for a double run from the sender's side:
   raise them when more matches are trained. The execution list (R-557): the res, giving ground, fights.
1. Isle of Jade: is a team at the footmen on the portal side in the base at a base res (HC v hdm 1:40)?
2. Tolkano: no build (his word): give him date, guilds, hall and length with every example to find it there.

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
