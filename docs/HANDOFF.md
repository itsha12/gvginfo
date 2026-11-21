# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-20: flags done for now; numbers from kills withdrawn (R-557); the split readings fixed where they could be; game 15 waits for his marks; R-548 to R-559)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` (7e54f33) and lands in
  one piece, then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run
  in progress. Rulings run to R-559. The baseline (R-491) is the branch `baseline-2026-11-15`.
- Graded and filed (set f1): twelve games. On the page, not marked: game 15, Men v NwAy on Corrupted Isle (c19f13e3,
  19 September; the old game 13, back at R-559; 36 situations, 8 of them splits). Not graded his new way: Corrupted,
  Weeping Stone, Isle of the Dead.
- Flags: all 60 advice cards marked (three corrected and fixed: set c1 of the key). Held out, the answer read at 15 s
  is better at 60, 90 and 180 s on one build: not yet a gain to call. The cards were not written again today.
- The split readings, built 2026-11-20 (`split_plays`; CLAUDE.md "When a split ends and what kills it"): the rest of
  a split's team read at the second, so the main team coming to it ends it (Men v hold 11:10, xxx v NwAy 12:20); a
  player left alone on the enemy's ground who trades no damage is not splitting on (Men v hold 9:56); a collapse
  that kills within seconds is told, from the main fight and not from the base res (NwAy v ohno 5:24); a death
  after a turn belongs to the collapse alone (QenK v Fun 6:37). hold v RACK 2:42 needed nothing: the split of
  three is the rows beside it, graded Classic. Nine open checks closed.
- Checkpoint run (every counted match, engine 7e54f33): 564 matches, 34,460 plays (split plays 14,925 to 14,557),
  no errors. The fourteen truths hold; 281 Classic rows pass, none fail; 132 history rows hold, 3 do not. Gate 12
  of 12 and 63 of 105. Self-check 21 in 7 (was 7 in 5): twelve are one stretch, TFS v DMG 22:44, DMG's Mesmer read
  on a split among his own main team's push. Line-up and comms 530 of 583 (2026-11-18, not run again).
- The similar cases (`cases.py test`, `data/model/flag_cases.json`, written at eca99d4), 4,277 cases today. Section 8,
  180 s on, us holding the stand (1,260): a runner within 15 s -2.0 win points; 15 to 90 s -1.3; none for 90 s +1.1
  (-4.3 where their flag got in, +6.9 where it did not). Them holding it (533): +1.7, 0.0, -0.2.

## Next (in order)
1. His marks on game 15 (`game_review_marks.json`): file them the same session (`review.py file`), fix any Classic
   fault first, set the results out for him. He then says whether splits are ready (R-496, R-559).
2. His answers to the three readings put to him 2026-11-20, each held on one game or against a Classic row:
   (a) HC v Team 12:32, "a full mainteam push backdoor of 6": three go in at 12:40 and the rest arrive by 13:16;
   reading them as the head of the push fails Men v hold 10:40 (Classic: five by the back door are a split though
   the other three are in the base 20 to 30 s later). From when is it the main team's push? (b) Men v hold 19:38,
   "just players joining mainteam" (three stay at hold's door, five walk back in 34 s) against Men v Apes 7:10
   (three stay in the pit, five at the stand a minute: his 3 v 2 split). (c) Men v hold 10:24, "no split yet"
   until the back door at 10:40, against a split told from the crossing (R-458; Men v RACK, Classic).
3. The split family (R-558): the answer to a split, and the main fight while a split is out (3,729 numbers plays
   "from a split elsewhere"; his calls of R-551 with collapse and send more), through the four stages. To build: on
   every split play the position, the fixed 90 and 180 s record and the 60 s before, from the second the split is
   seen (as `_numbers_at`); the answer read at a fixed second; like spots; cards and a view (copy `ADVICE.numbers`
   in `review.js`). Numbers from kills: dropped (R-557); what is built stays, no cards to him.
4. Held for a second game (R-495): Men v hold 18:06 (two of a push standing off it) and 6:48 (a collapse told as
   a push on the flagger); TFS v DMG 22:44; a base res with the attackers at the footmen (HC v hdm 1:40); who and
   how many push a flagger; numbers through Jade's portal; cope v hold 14:33; HC v hdm 5:56 (a flag left lying).
   Not built: a measure of what is at stake (R-509). Then stage E; the clean-up (R-398) after the games.

## Open for Denning
0. Held at his word (R-554, his "make sure you remember"): the cards for a flag in hand, with R-553 to build (no
   runner while the next flag is up is a flag-in-hand decision), and for a double run from the sender's side:
   raise them when more matches are trained. The execution list (R-557): the res, giving ground, fights.
1. The three questions of "Next" 2; and Jade: is a team at the footmen on the portal side in the base at a base res?
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
