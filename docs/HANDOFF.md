# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, then this, then `docs/REDESIGN.md` (the
plan for the decision tier). History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md` (cite R-numbers); every fitted
model's structure: `knowledge/model.md` (generated).

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then set out the items under "Open for Denning" and carry on with "Next".

## State (2026-11-12 night: redesign step 2 on branch `bundle-4`; batch 17, 506 matches trained)
- Main's engine is unchanged (SPEC.md). Bundle 4 is on `bundle-4` and lands in one piece, then one rebuild (R-322).
  606 replays stored (90 from 2 September on not yet trained on). No Train batch, Discovery or fetch run in progress.
- On `bundle-4`: `hallmap.py`, `moments.py` (the records and the decision moments), `story.py` (prints from the
  records, R-362), `tools/golden/golden.py pick|score|stories|gate`, `lineup.py score|lines`, `thresholds.py run|show|sweep`.
- The reading (stage R) is done: the reading gate passed (R-416); game 1's story form approved with three corrections
  (R-420); golden stories draft 9. Line-up: building 422 of 426, held-out 186 of 186; comms 109 of 157 and 62 of 80.
- R-420 as built: a push in is told with its fight's numbers over its first 12 s; a leave needs the player to go
  further than the enemy he faced; a join or a leave only at a fight (damage within 30 s, or within 1,000;
  JOIN_ENGAGE, JOIN_ENGAGE_S, Claude's). Over 606 matches joins 10,699 to 10,496, leaves 9,454 to 9,103, nothing
  else moved.
- Stage B rebuilt on the records (REDESIGN.md table): `run_starts()` (set off, waited, picked up, under way: the
  flag's runner off his own base and pit), triggers from `run_starts`, the boost, `attempts` (a split sets out or
  grows) and the numbers in each main team's fight (R-351); calls from the records in the 30 s window (`_runners`,
  `_rest`: a split of the main team, a push in, pushing the flagger, `way_out` and a split within 60 s, `ground`
  moves off the stand area, else where the main team stood); `verbs()` keeps every verb the team used in the window.
- The decision gate (R-394), first run (`golden.py gate --data <main>/data/lineup`):
  part one against `data/model/golden_key.json` (Claude's reading of his notes, for him to correct): 11 of 14 found
  (needs 9 in 10); trigger 5/5, stand 5/5, runners 5/5, rest 4/5, forced 6/6, home 2/2, side 4/4, source 4/4;
  size 1/2 and call 3/6 fail. Part two: 91 of 105 comms calls have a decision of that team within 30 s; 64 of 105
  read the same call; 30 more are calls the engine has no decision for (NPCs 14, plans, drops, boosts).

## Next (in order; REDESIGN.md "Build plan from here" and "Tests")
1. His answers to "Open for Denning" (the gate's misses and the comms pass mark), then fix and rerun the gate
   until it passes or each miss is ruled on (R-327).
2. Stage D on the branch (consequence record with flags given up beside numbers gained, R-412, and 0.8 of a player
   measured; similar cases; the job table; enemy execution; the four proposals left of R-324; radius checks to
   `st.zone`), then stage E (side by side for one rebuild, SPEC.md and METHODS.md rewritten, readability test, his
   list of R-398, merge, Train batch with `add_batch=no`).
3. Proposal for the integrity layer (an engine change, so in the bundle): flag stretches where the replay has casts
   but no damage (game 1 6:10 to 8:30; 7 of 606 replays have two or more whole minutes), so no fight is read there.

## Open for Denning (set each out in the chat, R-329)
- Comms pass mark (R-394 part two): 64 of 105 (60%) read the same call; 91 of 105 (86%) find a decision there.
- The gate's misses: hold v Apes 1:37 (the replay has no carry between the pre-gates pickup and 2:30); Men v hdm
  9:25 (hdm's 4-4 split is one attempt from 0:06 to 11:06; a split moving door or dividing is not a moment yet);
  Men v One 6:34 (his "not sure what this play is": One's main team out of its front door, not a split);
  NwAy v SKT 14:50 (SKT's three waiting at their own front door, a threat; SKT's five pushing NwAy's front door read
  as a split); Men v hdm 3:50 (push up to hdm's front door, engine stay: Men's main team stands on the stand area);
  Crew v One 8:02 (the fall out is at 8:38, past the 30 s window of R-294); Apes v Book 22:04 (out by the front door,
  the split into Book's back door at 22:48 was never long enough to be an attempt).
- His answer key: correct any line of `golden_key.json` (set out in the chat, not by pointing to the file).
- Game 1: his note has BcS's Mesmer going back to run at 7:23; the replay has him turning for home at 7:04 and at
  full speed from 7:10 (picks up at 7:36).
- From before: threat and the hand-off to hold (not records yet).

## Running it
- Train batch: `gh api -X POST repos/itsha12/gvginfo/actions/workflows/train-batch.yml/dispatches -f ref=main
  -f 'inputs[pick]=45' -f 'inputs[add_batch]=yes'` (rebuild only: `inputs[add_batch]=no`; TQs `inputs[tqs]=yes|no|auto`;
  blind round `inputs[blind]=no|yes|auto`, default no while rounds are paused). Never queue two runs at once.
- Maps: `tools/maps/build_maps.py`, `audit_labels.py [--routes]`; branch: `hallmap.py numbers|routes|reach`, `moments.py flags`.
- Local engine: `git fetch --depth 1 origin +replays:refs/remotes/origin/replays`; `pip install
  --break-system-packages -r .github/workflows/train-requirements.txt`. The records, the story, the line-up, the gate
  and the thresholds need no cache (`cache.py sync pull`, `warm` only for the fitted models). `PYTHONDONTWRITEBYTECODE=1`.
- `thresholds.py run` takes about 15 minutes with two jobs and the machine to itself; run old and new one after the other.

## Cautions
- Never print or decode a sealed field (blind picks, golden moments) in a chat.
- Don't merge `bundle-4` piecemeal (R-322). Label and golden files are saved whole by the site: after a change
  here, Denning reloads the page first. Hall labels are saved to main: copy changed `data/maps/labels/*.json` to the
  branch before reading a hall (all 14 matched main on 2026-11-12).
- Transcripts never go in the repo: paraphrased statements only. Party slots are in `data/matches/`, not the replays.
- `golden_moments.json` on the branch is a copy of main's; refresh it from main before the gate.
