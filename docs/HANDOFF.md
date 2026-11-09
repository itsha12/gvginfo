# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, then this. History: `docs/CHANGELOG.md`;
rulings: `docs/RULINGS.md` (cite R-numbers); every fitted model's structure: `knowledge/model.md` (generated).

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, then:
> <your request>

## State (2026-11-09 night, batch 16 trained: 90 matches)
- Portal: Model tab (engine pages, Blind test page); Mechanics keeps the game pages; all listed matches stored.
- Bundle 3 (R-278 to R-287) and the sign rulings (R-288 to R-291) are in the engine; rebuild run 42645700361 read
  0.354 against 0.471 for strength alone (see CHANGELOG 2026-11-09 evening for what the bundle changed).
- Batch 16 (run 42675808241, 61 min): chunks 6 and 7 trained together as one batch of 90 (45 stored after four
  GitHub job-start failures, plus 45 new; Denning's call), 446 matches. Glass box 0.355 against 0.47 (gain +0.115,
  +0.067 to +0.159), 84% against 78%; by month Sept 0.421 v 0.558, Oct 0.284 v 0.399, Nov 0.342 v 0.363 (49 matches,
  still barely ahead); by band even 0.513 v 0.641, moderate 0.321 v 0.458, uneven 0.083 v 0.071 (strength alone
  still slightly better on lopsided games). Advice test 4 of 13 clear (power_play +0.9 joins after_wipe +3.5,
  runner_choice +1.2, split_or_stay +0.7); play_for_28_or_lord now reads -1.4 for matching (not clear, watch).
  New in the win model: morale_diff paired with map_bases_apart and map_flag_run; spike_killable_diff up 0.119 to 0.194.
  22 learned-node link flips (report "What changed"). Rejected link of Denning's: P.26 cast prevention -> power play.
  Blind round 1 scored (model and Denning each beside the actual choice); round 2 open (8 picks, batch 16).
  TQs ran (push v chic flag swing; chic Prot death; BcS 8v3 power play; DMG knights to an Air/Water split).
- Discovery run 1 (run 42618611013): 24 own_/diff_ candidates passed once; the second run is next (offers candidates).
- Readability test 2 (docs/tests/readability-2026-11-09b.md): no, 14 of 18 at least partly explained; items 7 and 9
  queued below. Never queue two Train batch runs at once (both failed on 2026-11-09).

## Next (in order)
1. Run the readability test a third time on the regenerated page (a fresh session reads knowledge/model.md alone).
2. Discovery workflow (second run; candidates passing twice are offered). Then chunks of about 45 (Train batch,
   pick 45, add_batch yes; TQs every other chunk; a blind round each chunk), no engine change between them; proposals queue in `data/model/causal_map.json` "waiting" and here.
3. Next bundle (after 4 or 5 chunks): the open rulings below; Tier 2 table results column (readability item 7);
   rename map groups "Control received" where there is no runner (item 9); the second form of the query tool (a
   situation without a match); per-node readings by strength band; port `nodes.py` nodes into the learned-node
   framework if wanted; a results history for blind-test rounds across engine versions.

## Open rulings for Denning
- P.26 cast prevention -> power play: rejected by the data (gain -0.0016 +/- 0.0006, 443 matches): override or not yet.
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
