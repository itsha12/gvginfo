# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, then this, then `docs/REDESIGN.md` (the
plan for the decision tier). History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md` (cite R-numbers); every fitted
model's structure: `knowledge/model.md` (generated).

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, then:
> <your request>

## State (2026-11-09 late, batch 17 trained: 506 matches; redesign step 1 built)
- Decision redesign (docs/REDESIGN.md), from Denning's review of blind rounds 1 and 2: decisions become five families
  with scenarios, calls read as allocations over 20 to 30 s, a shape (who, when, which way), an objective and
  mechanics, answered as one decision card with three verdicts. Step 1 (no rebuild) is built: round 3 void, rounds
  paused (Train batch `blind` defaults to no), blind page scores cumulatively with a 5-case minimum and asks for a
  reason on disagreement, and Model > Guild hall maps draws all 14 halls from gvg.report's outline for Denning to
  label (five halls are served only by map file id: `replays.mjs` MAP_FILE_IDS). Rulings R-292 to R-305 confirmed.
- Portal: Model tab (engine pages, Blind test, Guild hall maps); Mechanics keeps the game pages; all matches stored.
- Bundle 3 (R-278 to R-287) and the sign rulings (R-288 to R-291) are in the engine (CHANGELOG 2026-11-09 evening).
- Batch 16 (run 42675808241): 90 matches as one batch (45 left by GitHub job failures plus 45 new): 0.355 v 0.47.
- Batch 17 (run 42689196937, 65 min, no TQs): 0.382 v 0.475 (gain +0.094, +0.057 to +0.133), 84% v 78%, Brier
  0.112 -> 0.119; by month Sept 0.425 v 0.54, Oct 0.356 v 0.434 (was 0.284), Nov 0.289 v 0.353; by band even 0.517 v
  0.632, moderate 0.37 v 0.475, uneven 0.074 v 0.066. Likely cause (not tested): the interaction screen swapped
  morale_diff x map_bases_apart and x map_flag_run for spike_killable_diff x map_pit_to_stand and bodyguard_diff x
  map_flag_run, with settings unchanged; the new October matches were also harder. Advice test 6 of 13 clear
  (late_game +11.6 and npcs_or_dp +1.9 join after_wipe, power_play, runner_choice, split_or_stay); play_for_28 -1.0.
  Rejected link of Denning's now P.26 -> R.2 (fight outcome) as well as P.26 -> K.4.
- Blind test: rounds 1 and 2 are first design (kept, not counted); round 3 void; nothing counted yet.
- Discovery run 1 (run 42618611013): 24 own_/diff_ candidates passed once; the second run is next (offers candidates).
- Readability test 2 (docs/tests/readability-2026-11-09b.md): no, 14 of 18 at least partly explained; items 7 and 9
  queued below. Never queue two Train batch runs at once (both failed on 2026-11-09).

## Next (in order)
1. Denning: label the remaining 11 halls on Model > Guild hall maps (Corrupted Isle, Isle of Meditation and Isle of
   Solitude are done and read cleanly). The other halls carry drafts from the replays (`draft_labels.py`; scores
   against his three halls in the CHANGELOG) to accept or remove; he adds choke points, NPCs, gates and hazards.
2. Redesign step 2 = bundle 4, one rebuild (REDESIGN.md "Step 2 items"): zones and path distance from the maps,
   departures, event triggers, scenarios, calls as allocations, shape, the consequence record, jobs, enemy execution,
   interaction pairs that must pass twice. Before the rebuild: about 20 to 30 golden moments for Denning to label (a
   site page to build). Fold in: the open rulings below, the Tier 2 results column and the "Control received" rename
   (readability items 7 and 9). Then step 3 (the decision card; blind rounds resume; TQs retired), then step 4.
3. Meanwhile, if wanted: chunks of about 45 (Train batch, pick 45, add_batch yes; no engine change between them), the
   Discovery workflow's second run, and a third readability run on knowledge/model.md.

## Open rulings for Denning
- P.26 cast prevention: rejected into power play (batch 16) and fight outcome (batch 17): override or not yet.
- Direction signs: ruled (R-288 to R-291) except two in fight outcome Denning did not list either way: spikes
  (own minus enemy) and damage focus on healers; both now carry no sign. Say + or leave them to the data.
- Four measurement proposals from the rulings wait on the map (control by distance to the stand; flag dropped by a
  Shadow Step; hex value incl. trigger damage, Mind Wrack; NPC healing by target and kind): next bundle.
- play_for_28_or_lord starts at 10:00 and counts footmen as NPCs taken (R-281 left both open): confirm or change.
- Discovery candidates offered after the second run: approve, reject or wait, each; 28 behaviour clusters to name
  (knowledge/behaviour.md).

## Running it
- Train batch: `gh api -X POST repos/itsha12/gvginfo/actions/workflows/train-batch.yml/dispatches -f ref=main
  -f 'inputs[pick]=45' -f 'inputs[add_batch]=yes'` (rebuild only: `inputs[add_batch]=no`; TQs `inputs[tqs]=yes|no|auto`;
  blind round `inputs[blind]=no|yes|auto`, default no while rounds are paused). Then pull main and read `data/model/reports/latest.md`. Discovery: the
  "Discovery" workflow (commits discovery.json, the history and knowledge/discovery.md).
- Blind test: rounds in `data/model/blind_tests.json`; the site page answers and scores (`advice.py blind_score [n]`
  from the shell; `advice.py /tmp/ga --blind-only --batch=N` adds a round; `blind_enrich` fills missing context).
- Maps: `python3 tools/maps/build_maps.py` (needs the replays branch, about 30 s) rebuilds outlines and replay-derived
  points after new replays; it never touches `data/maps/labels/` (Denning's) or the engine's `data/maps/<id>.json`.
- Query tool: `python3 ask.py <report id> <m:ss> [team]` (needs `analyze.py --all --out /tmp/ga` and the cache warm).
- Local engine: `git fetch --depth 1 origin +replays:refs/remotes/origin/replays`; `pip install
  --break-system-packages -r .github/workflows/train-requirements.txt`; in tools/replay_analysis `cache.py sync pull`,
  `cache.py warm`. `GVG_SUBSET=30` runs any of it on the first 30 matches (local smoke tests only; `fit_all` on three
  nodes took about 10 min here on 2 cores). Run Python with `PYTHONDONTWRITEBYTECODE=1`.
- Cache keys are by layer (`cache.py info`): edits to report modules (tq, learning, causalchain, snapshot, modelpage,
  advice, ask, behaviour, discover) rebuild nothing; edits to measurement modules (decisions.py included) rebuild all
  prepared data. Workflow artifacts can't be downloaded here (Azure blocked); `gh api` (REST; GraphQL blocked) and
  git work; the workspace can't reach gvg.report or the wiki.

## Cautions
- Links near the line flip between runs ("supported" by a small margin is a lead; the diff lists flips); fits differ
  in the last digits between machines, so small report differences are noise.
- No energy, line of sight or NPC positions in the replays; proxies carry lower confidence. Never print or decode a
  blind-test pick's sealed field in a chat (a round was discarded for that).
- The site's save failed on files over about 120 KB (fixed in core.js, 2026-11-09): blind_tests.json was at 107 KB.
