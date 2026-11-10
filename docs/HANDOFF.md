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
- All 14 halls labelled and the audit clean (R-318). Batch 17, discovery run 1 and readability test 2: unchanged
  since the last handoff (CHANGELOG 2026-11-09 night, 2026-11-10).

## Next (in order)
1. Denning: label the golden moments on the site (Model > Golden moments). Where a list cannot say what happened,
   pick Other and write it; those words become options.
2. Then, on `bundle-4`: `git fetch origin && git rebase origin/main`, `python3 tools/golden/golden.py score`, fix
   the classifier or bring definitions to Denning until R-323's rate holds. Known before the labels: 39% of flag
   decisions have the main group in no named place (backside, push side, enemy base); 27% of split answers are a
   count no named call covers; a split met outside the base is not read as a collapse; a second player joining a
   split 15 s later is a second moment; timing uses hindsight purposes (fine for analysis, R-296).
3. Stage D on the branch: shape (composition properties, route with `Hall.route_followed`, timing with R-321), the
   consequence record at 90 s and about 3 min, similar cases by scenario, the job table (Claude drafts, Denning
   rules), enemy execution, interaction pairs that pass twice, the five proposals (R-324), the Tier 2 results column
   and the "Control received" rename. Swap the engine's remaining straight-line radius checks (PIT_R, BASE_R,
   STAND_R in episodes, fights, scoreboard, lnrows) for `st.zone` and walked distance.
4. Stage E: old and new kinds side by side for one rebuild (R-323), then retire the replaced kinds, clean the causal
   map, rewrite SPEC.md and METHODS.md, readability test, merge to main, Train batch with `add_batch=no` (same 506
   matches, so the comparison is the engine alone). Then step 3 (the decision card), then step 4.
5. Meanwhile, if wanted, on main: chunks of about 45, the Discovery workflow's second run, a third readability run.

## Open rulings for Denning
- Departure purpose: fixed 60 s after the leave, earlier on a pickup or on entering the enemy base (Claude's;
  asked 2026-11-10, not yet answered). The footmen reach cut at 75% of footman hits (R-320).
- P.26 cast prevention: rejected into power play (batch 16) and fight outcome (batch 17): override or not yet.
- Direction signs: spikes (own minus enemy) and damage focus on healers in fight outcome carry no sign: + or leave.
- play_for_28_or_lord starts at 10:00 and counts footmen as NPCs taken (R-281 left both open): confirm or change.
- Labels: Warrior's Isle has no Flag stand point (the replays' stand is used); footmen sit inside the Base area on
  one side only on Corrupted Isle and Uncharted Isle (the bases are drawn to different depths): leave or redraw.
- Discovery candidates after the second run; 28 behaviour clusters to name (knowledge/behaviour.md).

## Running it
- Train batch: `gh api -X POST repos/itsha12/gvginfo/actions/workflows/train-batch.yml/dispatches -f ref=main
  -f 'inputs[pick]=45' -f 'inputs[add_batch]=yes'` (rebuild only: `inputs[add_batch]=no`; TQs `inputs[tqs]=yes|no|auto`;
  blind round `inputs[blind]=no|yes|auto`, default no while rounds are paused). Then pull main and read
  `data/model/reports/latest.md`. Never queue two runs at once. Discovery: the "Discovery" workflow.
- Maps: `python3 tools/maps/build_maps.py` (needs the replays branch) rebuilds outlines; after Denning labels,
  `python3 tools/maps/audit_labels.py [--routes]`. On the branch: `python3 hallmap.py numbers|routes|reach [--write]`.
- Local engine: `git fetch --depth 1 origin +replays:refs/remotes/origin/replays`; `pip install
  --break-system-packages -r .github/workflows/train-requirements.txt`; in tools/replay_analysis `cache.py sync pull`,
  `cache.py warm`. `GVG_SUBSET=30` for smoke tests. Run Python with `PYTHONDONTWRITEBYTECODE=1`. The branch's moment
  classifier needs none of the cache: it reads replays directly.
- Site check: `python3 -m http.server` in the repo, then playwright with `/usr/bin/google-chrome` (mock
  api.github.com to test a save).
- Workflow artifacts can't be downloaded here (Azure blocked); `gh api` (REST) and git work; the workspace can't
  reach gvg.report or the wiki.

## Cautions
- Never print or decode a blind-test pick's sealed field, or a golden moment's `sealed` field, in a chat.
- Never show Denning the engine's reading of a golden moment before he has labelled it (not in chat either).
- Don't merge `bundle-4` into main piecemeal: any engine file on main changes the cache key and forces a rebuild.
- Links near the line flip between runs; fits differ in the last digits between machines.
- Label files are saved whole by the site: after a change made here, Denning reloads the map page before labelling.
- At handoff: no Train batch or Discovery run in progress.
