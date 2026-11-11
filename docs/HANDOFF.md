# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, then this, then `docs/REDESIGN.md` (the
plan for the decision tier). History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md` (cite R-numbers); every fitted
model's structure: `knowledge/model.md` (generated).

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, then:
> <your request>

## State (2026-11-10, second session: redesign step 2 under way on branch `bundle-4`; batch 17, 506 matches)
- Main's engine is unchanged (still as SPEC.md describes; batch 17 readings in CHANGELOG 2026-11-09 night). Chunks
  can still run on main. Bundle 4 is built on the branch `bundle-4` and lands in one piece, then one rebuild (R-322).
- On `bundle-4` so far (stages A and B of five; REDESIGN.md "Step 2: where it stands"):
  - `hallmap.py`: zones from the labelled areas (R-306), walked distance with teleporter hops (R-316), footmen reach
    around the Footman labels (R-320; `data/benchmarks/footmen_reach.json`). `state.zone` and the three map numbers
    read it; labels, outlines and hall features are in the cache key (a saved label will rebuild prepared data).
  - `moments.py` (draft): departures, triggers, scenarios, calls as allocations, forced reads for families 1 to 3.
    `python3 moments.py <report id>` prints a match; `moments.py all /tmp/moments.json --jobs 4` then
    `moments.py counts /tmp/moments.json` gives cases per scenario and call (70 s for 506 matches).
  - `tools/golden/golden.py pick|score` (outside the engine folder): picks the golden moments, scores the engine
    against Denning's labels. It never reads the sealed field.
- On main: Model > Golden moments (`assets/js/pages/golden.js`, `data/model/golden_moments.json`): 30 moments for
  Denning to label. The file never holds the engine's reading. Rulings R-318 to R-324 recorded.
- All 14 halls labelled, audit clean (R-318). Batch 17, discovery run 1, readability test 2: unchanged (CHANGELOG).

## Next (in order)
1. Denning: label the golden moments on the site (Model > Golden moments). Where a list cannot say what happened,
   pick Other and write it; those words become options.
2. Then, on `bundle-4`: `git fetch origin && git rebase origin/main`, `python3 tools/golden/golden.py score`, fix
   the classifier or bring definitions to Denning until R-323's rate holds. Known before the labels: 39% of flag
   decisions have the main group in no named place (backside, push side, enemy base); 27% of split answers are a
   count no named call covers; a split met outside the base is not read as a collapse; a second player joining a
   split 15 s later is a second moment; timing uses hindsight purposes (fine for analysis, R-296).
   First six labels (`golden.py score`): found 5 of 6, became 3 of 3, trigger 2 of 5, runners 2 of 5, rest 2 of 5.
   Known faults: a runner whose team stands in its base is not counted; a runner passing through main leaves twice.
3. Stage D on the branch: shape (composition properties, route with `Hall.route_followed`, timing with R-321), the
   consequence record at 90 s and about 3 min, similar cases by scenario, the job table (Claude drafts, Denning
   rules), enemy execution, interaction pairs that pass twice, the five proposals (R-324), the Tier 2 results column
   and the "Control received" rename. Swap the engine's remaining straight-line radius checks (PIT_R, BASE_R,
   STAND_R in episodes, fights, scoreboard, lnrows) for `st.zone` and walked distance.
4. Stage E: old and new kinds side by side for one rebuild (R-323), then retire the replaced kinds, clean the causal
   map, rewrite SPEC.md and METHODS.md, readability test, merge to main, Train batch with `add_batch=no` (same 506
   matches, so the comparison is the engine alone). Then step 3 (the decision card), then step 4.
5. Meanwhile, if wanted, on main: chunks of about 45, the Discovery workflow's second run, a third readability run.

## Open rulings for Denning (set each out in the chat, R-329; R-318 to R-341 ruled 2026-11-10)
- R-341 sets the direction: the engine should think as his golden notes do (the story so far); options, decisions
  and variables follow from that. Ruled from the notes: R-334 to R-340 (greater stand area, main team in a 4v4, flag
  position and stand holder both, pinned teams, one flag a team, the hand-off and double run forms).
- Built 2026-11-10 night (branch, drafts): `Hall.place`, `Moments.fights`, `Moments.flag_lives`, `story.py` with the
  why words (routes, on time R-348, swaps, falls back under pressure R-349 and R-352, falls out; 12 s to count in a
  fight R-350). All 14 halls now have a Greater stand area label (9 accepted drafts, 5 drawn by him).
- Golden moments (R-354, replacing R-345's two parts): the page shows the engine's story of each of the 30 games
  (`golden_stories.json`, draft 2); he ticks wrong lines and adds notes or corrections. His 13 earlier notes are the
  fixed blind check (`blind_note`). Waiting on him: mark the stories.
- Next on the branch: read his marks (`label.story.wrong`, `label.notes`), fix the story, compare it with the 13
  blind notes; add a threat or posture, hand-off to hold, time to cap, quieter flag lines; regenerate `golden.py
  stories` (raise `draft`); then scenarios, calls and triggers rebuilt on the story (numbers advantage in every
  fight, R-351) and `golden.py score` rewritten against his marks. A monk energy estimate only if needed (R-353).
  Also open: discovery second run; 28 behaviour clusters to name.

## Running it
- Train batch: `gh api -X POST repos/itsha12/gvginfo/actions/workflows/train-batch.yml/dispatches -f ref=main
  -f 'inputs[pick]=45' -f 'inputs[add_batch]=yes'` (rebuild only: `inputs[add_batch]=no`; TQs `inputs[tqs]=yes|no|auto`;
  blind round `inputs[blind]=no|yes|auto`, default no while rounds are paused). Then pull main and read
  `data/model/reports/latest.md`. Never queue two runs at once. Discovery: the "Discovery" workflow.
- Maps: `tools/maps/build_maps.py` rebuilds outlines; `tools/maps/audit_labels.py [--routes]` after Denning labels;
  on the branch `hallmap.py numbers|routes|reach [--write]`, `moments.py flags` (the flag ledger over all matches).
- Local engine: `git fetch --depth 1 origin +replays:refs/remotes/origin/replays`; `pip install
  --break-system-packages -r .github/workflows/train-requirements.txt`; in tools/replay_analysis `cache.py sync pull`,
  `cache.py warm`. `GVG_SUBSET=30` for smoke tests; `PYTHONDONTWRITEBYTECODE=1`. `moments.py` needs no cache.
- Site check: `python3 -m http.server` and playwright with `/usr/bin/google-chrome` (mock api.github.com for a save).

## Cautions
- Never print or decode a sealed field (blind picks, golden moments) in a chat, and never show Denning the engine's
  reading of a golden moment he has not labelled.
- Don't merge `bundle-4` into main piecemeal (it would force a rebuild). No Train batch or Discovery run in progress.
- Label files are saved whole by the site: after a change here, Denning reloads the page before labelling.
