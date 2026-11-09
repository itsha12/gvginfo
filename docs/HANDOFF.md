# GvG Info: handoff for a new chat

Rewritten each session; stays under 80 lines. Read `CLAUDE.md`, then `docs/SPEC.md`, then this. History is in
`docs/CHANGELOG.md`; Denning's rulings in `docs/RULINGS.md` (cite R-numbers); the structure of every fitted model in
`knowledge/model.md` (generated).

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, then:
> <your request>

## State (2026-11-09 evening, after bundle 3; no chunk since batch 15)
- Portal: Model tab (engine pages, Blind test page); Mechanics keeps the game pages; all listed matches stored.
- Model: 356 matches (batch 15). Reading before bundle 3 (run 42569970450): glass box 0.358 against 0.472 for strength
  alone (gain +0.114, +0.064 to +0.161), 84% against 77%; by month Sept 0.443 v 0.577, Oct 0.282 v 0.395, Nov 0.317 v
  0.363; by strength band even 0.525 v 0.65, moderate 0.33 v 0.469, uneven 0.083 v 0.078. Advice test: 2 of 13 kinds
  clear (runner_choice +1.1, split_or_stay +0.5); macro advice mostly "the usual play", worth about a point.
- Bundle 3 (Denning's rulings R-278 to R-287, CHANGELOG 2026-11-09 evening) is built: decisions redefined (offence
  window 15 s; NPCs or DP on 3+ kills past the footmen; play for 28 from 10:00 for a team that took NPCs), kinds per
  node by perspective, allocation decisions allowed as fixes, pruning of Denning's unclear links last, P.21 kiting
  kept and P.27 pre-kiting / P.19 Blind let go by the data, direction corrections ("reads backwards") on execution
  inputs, discovery offers own_ and diff_ with the enemy's side beside, page-text fixes from readability test 2.
- Rebuild after bundle 3 (run 42645700361, 56 min, every prepared layer remade): glass box 0.354 against 0.471
  (gain +0.117, +0.065 to +0.164), 85% against 77%; by month Sept 0.441, Oct 0.279, Nov 0.308; by band even 0.519,
  moderate 0.327, uneven 0.085: the same within noise. Advice test now 3 of 13 clear (after_wipe joins runner_choice
  and split_or_stay). New decisions: npcs_or_dp 196 cases in 153 matches (NPCs the usual), play_for_28_or_lord 2,970
  in 187 (play for 28 the usual, 71% matched), offence_or_defence 913 in 302. Collapse now 14 of 14 (Denning's unclear
  links pruned, R-278). Reads backwards (R-285): run outcome damage/control on the runner and runner escapes; fight
  outcome blind attacks, disables, hexes on own, knockdowns on casters, pre-kiting, strip targeting: for Denning to
  check against the direction list. The report's "What changed" diff compares to batch 14, not to the pre-bundle
  rebuild (same batch number); the numbers above are the comparison. Blind-test round 1 written (8 picks, 3 specific).
- After the rebuild (fit layer only, no rebuild run): signs ruled (R-288 to R-291), runner_escapes retired; the next
  chunk carries these, so compare its learned-node readings against this rebuild's, not batch 14's.
- Discovery run 1 on the catalogue (run 42618611013): 1,633 tests, 24 own_/diff_ candidates passed once; nothing is
  offered until a second run (the pass history is now committed; before today it never was, so nothing could pass twice).
- Readability test 2 (docs/tests/readability-2026-11-09b.md): no, 14 of 18 at least partly explained; page-text
  items built, items 7 and 9 queued below.

- Chunk 6 (batch 16) not trained yet: its 45 replays were fetched and stored on the replays branch (run 42668315551),
  then four runs failed on GitHub's side (jobs never created, later 0 jobs). Next run: `inputs[pick]=0` to train
  exactly those 45; only then a pick-45 run for chunk 7 (a pick-45 run now would make one batch of 90). Don't queue
  two Train batch runs at once.

## Next (in order)
1. Blind-test round 1: answered and scored (read the totals when reporting the next chunk).
2. Run the readability test a third time on the regenerated page (a fresh session reads knowledge/model.md alone).
3. Chunks of about 45 (Train batch, pick 45, add_batch yes; TQs every other chunk; a blind round each chunk), no
   engine change between them; proposals queue in `data/model/causal_map.json` "waiting" and here. Discovery after
   the second chunk (second run offers candidates).
4. Next bundle (after 4 or 5 chunks): the open rulings below; Tier 2 table results column (readability item 7);
   rename map groups "Control received" where there is no runner (item 9); the second form of the query tool (a
   situation without a match); per-node readings by strength band; port `nodes.py` nodes into the learned-node
   framework if wanted; a results history for blind-test rounds across engine versions.

## Open rulings for Denning
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
  blind round `inputs[blind]=auto|yes|no`). Then pull main and read `data/model/reports/latest.md`. Discovery: the
  "Discovery" workflow (commits discovery.json, the history and knowledge/discovery.md).
- Blind test: rounds in `data/model/blind_tests.json`; the site page answers and scores (`advice.py blind_score [n]`
  from the shell; `advice.py /tmp/ga --blind-only --batch=N` adds a round; `blind_enrich` fills missing context).
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
