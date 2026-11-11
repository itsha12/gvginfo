# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, then this, then `docs/REDESIGN.md` (the
plan for the decision tier). History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md` (cite R-numbers); every fitted
model's structure: `knowledge/model.md` (generated).

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, then:
> <your request>

## State (2026-11-11: redesign step 2 under way on branch `bundle-4`; batch 17, 506 matches)
- Main's engine is unchanged (still as SPEC.md describes; batch 17 readings in CHANGELOG 2026-11-09 night). Chunks
  can still run on main. Bundle 4 is built on the branch `bundle-4` and lands in one piece, then one rebuild (R-322).
- On `bundle-4` so far (stages A and B of five; REDESIGN.md "Step 2: where it stands"):
  - `hallmap.py`: zones, walked distance with teleporter hops, footmen reach, places in his words (R-306, R-316, R-320).
  - `moments.py`: the old draft moments (families 1 to 3: triggers, scenarios, calls) and, since 2026-11-11, the records.
  - `tools/golden/golden.py pick|score|stories` (outside the engine folder); it never reads the sealed field.
- On main: Model > Golden moments (`golden.js`, `golden_moments.json`: his labels only). Rulings to R-364 recorded.

## Next (in order)
1. Denning: label the golden moments on the site (Model > Golden moments). Where a list cannot say what happened,
   pick Other and write it; those words become options.
2. Then, on `bundle-4`: `git fetch origin && git rebase origin/main`, regenerate the stories after each change to
   `story.py`, run the blind check, and rewrite `golden.py score` against his marks (R-354; the drop-down score is
   set aside, R-341).
3. Stage D on the branch: shape (composition properties, route with `Hall.route_followed`, timing with R-321), the
   consequence record at 90 s and about 3 min, similar cases by scenario, the job table (Claude drafts, Denning
   rules), enemy execution, interaction pairs that pass twice, the five proposals (R-324), the Tier 2 results column
   and the "Control received" rename. Swap the engine's remaining straight-line radius checks (PIT_R, BASE_R,
   STAND_R in episodes, fights, scoreboard, lnrows) for `st.zone` and walked distance.
4. Stage E: old and new kinds side by side for one rebuild (R-323), then retire the replaced kinds, clean the causal
   map, rewrite SPEC.md and METHODS.md, readability test, merge to main, Train batch with `add_batch=no` (same 506
   matches, so the comparison is the engine alone). Then step 3 (the decision card), then step 4.

## Open rulings for Denning (set each out in the chat, R-329; R-318 to R-341 ruled 2026-11-10)
- R-341 sets the direction: the engine should think as his golden notes do (the story so far); options, decisions
  and variables follow from that. Ruled from the notes: R-334 to R-340 (greater stand area, main team in a 4v4, flag
  position and stand holder both, pinned teams, one flag a team, the hand-off and double run forms).
- On the branch (drafts): `Hall.place`, `Moments.fights`, `Moments.flag_lives`, `story.py` (R-348 to R-352). All 14
  halls have a Greater stand area label (9 accepted drafts, 5 drawn by him).
- Golden moments (R-354): the page shows the engine's story of each of the 30 games (`golden_stories.json`, draft
  5); he ticks wrong lines and adds notes. His 13 earlier notes are the fixed blind check (`blind_note`). Draft 3
  (from his marks on game 1): STATE lines, who goes back for the flag and when, dropped flags, footmen engaged,
  doors as routes. Draft 4 (from Nick's commentary): one death line per place, the base res read from whether it
  took the player (the replay clock is off by up to 2 s), the Lord's death ends the story, a resignation is named.
  Waiting on him: review game 1's story, then say whether the form is right before marking the rest.
- Commentary trial (2026-11-11): Nick's transcripts have no timestamps, but the order of deaths, caps, splits and
  NPC kills lines them up with the story every 30 to 60 s. `data/commentary/nick.json` now holds 9 games (81
  claims, each with the story's check). "Boss" is September's flux (Like a Boss), not the boost: corrected.
  Still to line up: 983a47db (xxx v ohno, report d70f3684); 00cb0759 has no transcript.
- Built 2026-11-11 on the branch from R-355 to R-364 (the record is the work, R-362): `Moments.attempts()` (one
  record a split attempt or main team push: who, monks, way in, the answer, main team numbers meanwhile, end,
  result, linked moves), `caught()` (in the enemy base at the defenders' base res), `flags_record()` (runner, time
  away, backup flag, back cap, with a split, drop place, boost clock, died carrying), `main_team()` and `lane()`,
  `common.flux_at`. `moments.py <id> splits|flags` prints them; `story.py` prints its split, push and cap lines from
  them. 513 matches: 1,909 splits (3.7 a match), 1,681 pushes. Against Nick's three games 12 of 13 attempts found.
- Ruled 2026-11-11 (R-365 to R-367), next to build: one split fight record for as long as the same two groups
  stay engaged, wherever it drifts (whose ground, how long, who started it); this also covers a split met in the
  middle. Back cap confirmed as built. Solo splits parked (45% of records; do not rely on them). Still unchecked:
  "main team joined" is 35% of endings; the main team rule was tuned on Nick's three games; giving ground is read
  from the middle player. The old F1 to F3 moments still run beside the records and are not rebuilt on them.
- Also open: noisy "go to split" lines, threat or posture, hand-off to hold, time to cap, `golden.py score` against
  his marks, a monk energy estimate only if needed (R-353), discovery second run, behaviour clusters.

## Running it
- Train batch: `gh api -X POST repos/itsha12/gvginfo/actions/workflows/train-batch.yml/dispatches -f ref=main
  -f 'inputs[pick]=45' -f 'inputs[add_batch]=yes'` (rebuild only: `inputs[add_batch]=no`; TQs `inputs[tqs]=yes|no|auto`;
  blind round `inputs[blind]=no|yes|auto`, default no while rounds are paused). Then pull main and read
  `data/model/reports/latest.md`. Never queue two runs at once. Discovery: the "Discovery" workflow.
- Maps: `tools/maps/build_maps.py`, `audit_labels.py [--routes]`; branch: `hallmap.py numbers|routes|reach`, `moments.py flags`.
- Local engine: `git fetch --depth 1 origin +replays:refs/remotes/origin/replays`; `pip install
  --break-system-packages -r .github/workflows/train-requirements.txt`; in tools/replay_analysis `cache.py sync pull`,
  `cache.py warm`. `GVG_SUBSET=30` for smoke tests; `PYTHONDONTWRITEBYTECODE=1`. `moments.py` needs no cache. Site check:
  `python3 -m http.server` and playwright with `/usr/bin/google-chrome` (mock api.github.com for a save).

## Cautions
- Never print or decode a sealed field (blind picks, golden moments) in a chat.
- Don't merge `bundle-4` piecemeal (R-322). No Train batch or Discovery run in progress. Label and golden files are
  saved whole by the site: after a change here, Denning reloads the page first.
