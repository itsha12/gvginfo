# GvG Info: handoff for a new chat

Rewritten each session; stays under 80 lines. Read `CLAUDE.md`, then `docs/SPEC.md`, then this. History is in
`docs/CHANGELOG.md`; Denning's rulings in `docs/RULINGS.md` (cite R-numbers); the structure of every fitted model in
`knowledge/model.md` (generated).

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, then:
> <your request>

## State (2026-11-09 evening, after bundle 3; no chunk since batch 15)
- Portal: Model tab added (engine pages plus the Blind test page); Mechanics keeps the game pages. Update matches run
  42618614199: all listed matches stored.
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
- Discovery run 1 on the catalogue (run 42618611013): 1,633 tests, 24 own_/diff_ candidates passed once; nothing is
  offered until a second run (the pass history is now committed; before today it never was, so nothing could pass twice).
- Readability test 2 (docs/tests/readability-2026-11-09b.md): verdict no, 14 of 18 items at least partly explained.
  Page-text items built; items 2, 3, 4, 7, 9 (engine or map) partly built (3: time-down sign fixed; 4: runner class
  explained in the glossary; 2: lord damage units and parts) and the rest below.

## Next (in order)
1. Denning: Model > Blind test on the site, answer round 1 (8 picks, reason optional, the model's call shows after
   saving), press Score. Then `python3 advice.py blind_score 1` is not needed (the page scores); read the totals.
2. Run the readability test a third time on the regenerated page (a fresh session reads knowledge/model.md alone).
3. Chunks of about 45 (Train batch, pick 45, add_batch yes; TQs every other chunk; a blind round each chunk), no
   engine change between them; proposals queue in `data/model/causal_map.json` "waiting" and here. Discovery after
   the second chunk (second run offers candidates).
4. Next bundle (after 4 or 5 chunks): the open rulings below; Tier 2 table results column (readability item 7);
   rename map groups "Control received" where there is no runner (item 9); the second form of the query tool (a
   situation without a match); per-node readings by strength band; port `nodes.py` nodes into the learned-node
   framework if wanted; a results history for blind-test rounds across engine versions.

## Open rulings for Denning
- Direction list (learnednodes.EXPECTED, R-285): Claude's; confirm or change the signs (the report lists what read
  backwards after the rebuild).
- play_for_28_or_lord starts at 10:00 and counts footmen as NPCs taken (R-281 left both open): confirm or change.
- `flag_answer` kept as its own node (R: keep for now); fold into the runs once they carry a lateness reading?
- Discovery candidates offered after the second run: approve, reject or wait, each.
- Behaviour clusters no named choice covers: 28 to name or reject (knowledge/behaviour.md).

## Running it
- Train batch: `gh api -X POST repos/itsha12/gvginfo/actions/workflows/train-batch.yml/dispatches -f ref=main
  -f 'inputs[pick]=45' -f 'inputs[add_batch]=yes'` (rebuild only: `inputs[add_batch]=no`; TQs `inputs[tqs]=yes|no|auto`;
  blind round `inputs[blind]=auto|yes|no`). Then pull main and read `data/model/reports/latest.md`. Discovery: the
  "Discovery" workflow (commits discovery.json, the history and knowledge/discovery.md).
- Blind test: rounds in `data/model/blind_tests.json`; the site page answers and scores; `advice.py blind_score [n]`
  scores from the shell; `advice.py /tmp/ga --blind-only --batch=N` adds a round. Sealed fields are base64: don't decode.
- Query tool: `python3 ask.py <report id> <m:ss> [team]` (needs `analyze.py --all --out /tmp/ga` and the cache warm).
- Local engine: `git fetch --depth 1 origin +replays:refs/remotes/origin/replays`; `pip install
  --break-system-packages -r .github/workflows/train-requirements.txt`; in tools/replay_analysis `cache.py sync pull`,
  `cache.py warm`. `GVG_SUBSET=30` runs any of it on the first 30 matches (local smoke tests only; `fit_all` on three
  nodes took about 10 min here on 2 cores). Run Python with `PYTHONDONTWRITEBYTECODE=1`.
- Cache keys are by layer (`cache.py info`): edits to report modules (tq, learning, causalchain, snapshot, modelpage,
  advice, ask, behaviour, discover) rebuild nothing; edits to measurement modules (decisions.py included) rebuild all
  prepared data. Workflow artifacts can't be downloaded from the chat workspace (Azure blocked); `gh api` and git work.
- GitHub GraphQL is blocked; use `gh api` (REST). The workspace can't reach gvg.report or the wiki.

## Cautions
- Links near the line flip between runs ("supported" by a small margin is a lead; the diff lists flips); fits differ
  in the last digits between machines, so small report differences are noise.
- No energy, line of sight or NPC positions in the replays; proxies carry lower confidence.
- Never print or decode a blind-test pick's sealed field in a chat; the first round of the day was discarded for that.
