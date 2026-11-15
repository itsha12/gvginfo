# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then set out the items under "Open for Denning" and carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it. Add your
> answers to the open items, by their numbers, to the same message if you have them.)

## State (2026-11-15: redesign step 2 on branch `bundle-4`, stage D under way; batch 17, 506 matches trained)
- Main's engine is unchanged (SPEC.md). Bundle 4 is on `bundle-4` and lands in one piece, then one rebuild (R-322).
  658 replays stored; 564 count (R-477); the trained batches still hold some. No Train batch, Discovery or fetch run
  in progress. Both branches pushed; nothing uncommitted. The files on `bundle-4` are listed in CLAUDE.md.
- Whole-game scores, situations right of those he judged (R-475), each a fresh game for the engine it was marked
  against: part 1 (TFS v 옷옷옷옷, Men v Apes) 45 of 85; hdm v hook 35 of 58 (60%); round 3 (set w2): hook v hold
  24 of 41 (59%), cope v Team 15 of 24 (62%), RJT v RACK 33 of 45 (73%, engine b09a26a). The mark is 80% (R-473).
- Built from his marks and answers on RJT v RACK (engine 9d3a679; R-482 to R-485), at the root (R-465):
  - Who is on a split: on the enemy's ground, or standing with a split player who is (its back line); only main
    team players off the enemy's ground take a player off it (`_over`, `split_plays`). A split's fight is told once:
    a numbers moment that is a split's fight from first reading to last folds into the split (`numbers_plays`).
  - Whose flag decision: the runner's set-off passes over jumps in the walked distance; the flag is under way from
    its last unbroken chain of carries (`run_starts`: `out_by`, `chain`); a flag that lay on the ground is two runs;
    in hand by the cap rule (R-482); a double run from its second player (R-485); each run is answered in turn (a
    team whose flag is in, with theirs still coming, runs again or stays): `_flag_rows`, `flag_plays`.
  - On the development set (44 matches): flag plays 513 to 640 (stay 149 to 227, in hand 77 to 61, double 100 to
    36), split plays of one player 189 to 158, numbers plays 878 to 867. `review.py compare` on RJT v RACK: 87
    calls now, 39 of them calls he marked right, 35 never shown to him; it says 41 of his 52 right calls.
- Now (development set, 45 matches): review key 120 rows pass; 40 checks open (w1p1 14, w1p2 9, w2 16, s1-15); 18
  were made firm on 2026-11-15 (13 of RJT v RACK's, and hook v hold 8:30, hdm v hook 8:46, TFS v 옷옷옷옷 10:13 with
  them). Gate: 12 of 12, 63 of 105. Line-up: 421 of 426 and 185 of 186; comms 110 of 157, 62 of 80. No run over
  every match, no `thresholds.py`, no numbers test (R-470) since the change.
- Round 4 is on the page (set w3, engine 9d3a679), not yet marked: HC v Team on Imperial Isle (9b5cdf62; 55
  situations: 14 flags, 12 splits, 12 pushes on a flagger, 11 numbers). Men v Crew stays hidden.

## Data looked at on 2026-11-14 (nothing built; nothing from GW Observer in the repo)
- gvg.report's replay payload holds `report.objectives.object_transitions` (each appearance of a flag object, with
  its position); `replay_trim.mjs` drops it. A flag appearing at its spawn with no cap just before is a return (on
  RJT v RACK within 0.5 s of the game's four return messages; the engine's inferred returns were 3 to 69 s late).
  R-481: keep it in the trim and read returns from it at the next rebuild, not before (a new TRIM_VERSION fetches
  every stored replay again, about 90 MB a match).
- The Lord damage page (`summary.objectives.guild_lord_damage`) adds nothing stored casts and deaths do not give. GW
  Observer's match cache is the same recording kept fuller (NPC positions and health, returns, gates); no probed
  payload serves NPC tracks (`full` not probed: he said no). Its licence limits the code and the data: his call.

## Next (in order; REDESIGN.md "Build plan from here", item 6, and "Tests")
1. He marks HC v Team (Model > Game review). `review.py file <id> <rows> <marks> --set w3` files his marks and
   prints the score; write checks from his words; fix at the root (R-465). Never re-export a game he has marked.
2. The numbers test on the marked rows (R-470). At 80% of situations right on a fresh game, the hidden games.
   Never export or look at Men v Crew or 옷옷옷옷 v RACK before that.
3. The flag family to the end (R-451) once the flag plays pass; the other kinds as each passes; then stage E.

## Open for Denning (put to him 2026-11-15; set each out in the chat again, R-329, with replay links)
1. HC v Team is his to mark (https://gvg.report/report/9b5cdf62-edce-5ca9-a6a4-c02d48c7eb96#map).
2. His answers of 2026-11-15 (R-486 to R-489, none built): the flag in hand is a timing choice; the main team is
   usually the larger group, with push team and defence team at 4 and 4 on the flag paths; fluid numbers, players
   in neither fight, "no clear decision" as an answer. Put to him: which group is the push team, how long a change
   must last, and a proposal on his process question (borderline rows must not steer the engine): CHANGELOG.
3. TFS v 옷옷옷옷 2:09: now told from TFS's side (옷옷옷옷's 8 Monk set off first, 1:40; TFS's Ritualist answers).
4. RJT v RACK 4:06, "now the mainteam fight": the engine still tells RACK's split through the 8 v 8 of 4:18 to 4:36.
5. Rows he marked right on RJT v RACK that now read otherwise: 11, 24 (the Ranger's solo trips, inside the split),
   26, 30 (numbers, inside the split), 4, 47. Drafts not ruled: numbers from kills, a split with no answer.

## Running it
- Train batch: `gh api -X POST repos/itsha12/gvginfo/actions/workflows/train-batch.yml/dispatches -f ref=main
  -f 'inputs[pick]=45' -f 'inputs[add_batch]=yes'` (rebuild only: `inputs[add_batch]=no`; TQs `inputs[tqs]=yes|no|auto`;
  blind round `inputs[blind]=no|yes|auto`, default no while rounds are paused). Never queue two runs at once.
- Local engine: `git fetch --depth 1 origin +replays:refs/remotes/origin/replays`; `pip install
  --break-system-packages -r .github/workflows/train-requirements.txt`. The records, the story, the line-up, the gate
  and the thresholds need no cache (`cache.py sync pull`, `warm` only for the fitted models). `PYTHONDONTWRITEBYTECODE=1`.
  `thresholds.py run`: about 15 minutes, two jobs, the machine to itself; old and new one after the other.

## Cautions
- Never print or decode a sealed field (blind picks, golden moments) in a chat.
- Don't merge `bundle-4` piecemeal (R-322). Label and golden files are saved whole by the site: after a change
  here, Denning reloads the page first. Hall labels are saved to main: copy changed `data/maps/labels/*.json` to the
  branch before reading a hall (the export refuses otherwise, and never shows a hidden or spare game).
- Transcripts never go in the repo: paraphrased statements only. Party slots are in `data/matches/`, not the replays. Refresh the branch's `golden_moments.json` from main before the gate.
