# GvG Info: handoff for a new chat

Rewritten each session; stays under 80 lines. Read `CLAUDE.md`, then `docs/SPEC.md`, then this. History is in
`docs/CHANGELOG.md`; Denning's rulings in `docs/RULINGS.md` (cite R-numbers); the structure of every fitted model in
`knowledge/model.md` (generated).

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, then:
> <your request>

## State (2026-11-09, after the review bundles; steps 2 to 4 of the previous Next done, no new chunk)
- Portal: unchanged since 2026-10-15. Update matches run 42618614199: 20 fetched, 0 remaining (all listed matches stored).
- Model: 356 matches trained (batch 15; rebuild run 42569970450 after the bundles, no new matches): glass box 0.358
  against 0.472 for strength alone (gain +0.114, +0.064 to +0.161), 84% against 77%; every learned node beats its
  baseline with the concurrent measures out of the fit. By month: Sept 0.443 v 0.577, Oct 0.282 v 0.395, Nov 0.317 v
  0.363; by strength band: even 0.525 v 0.65, moderate 0.33 v 0.469, uneven 0.083 v 0.078 (nothing over strength).
  Advice test: 2 of 13 kinds clear (runner_choice +1.1, split_or_stay +0.5); the advice differs from the usual play in
  only 1 to 5% of cases for most kinds, so the macro advice today is mostly "do the usual thing", worth about a point.
- The November 2026 review is built (R-260 to R-277); the five new decisions use Claude's definitions, to confirm.
- Discovery run 1 on the catalogue (run 42618611013, 4.5 min): 1,633 variable-by-node tests, 137 passed the screen
  (about 38 by chance), 27 passed once (knowledge/discovery.md); nothing offered until a second run. Several of the 27
  are enemy_* variables (e.g. pit npc loss: p.enemy_dm_npcs_10s), which are the enemy's concurrent response, not advice.
- Blind test sealed: `data/model/blind_test.json`, 10 picks, model call = usual play in 9 (only npcs_or_dp differs).
  Sealed fields are base64, never printed; `python3 advice.py blind_score` scores once every denning_call is filled.
- Readability test 2 (docs/tests/readability-2026-11-09b.md): no, but 14 of 18 items at least partly explained.

## Next (in order)
1. Denning: fill `denning_call` for the 10 blind-test picks (read only id, kind, match, team, t, situation,
   choices_seen; the model's call is visible, so decide before looking at it if the test is to be fair), then
   `python3 advice.py blind_score`. Collect his rulings (below) as one bundle; build nothing between chunks.
2. Page-text fixes from readability test 2 (modelpage.py, report layer, regenerated at the next run): define
   Importance; strip the remaining jargon; name the perspective in two-sided nodes; sign conventions for boost clock
   and arrival times; say when a curve is not monotone. Denning to say whether these go now or with the bundle.
3. Chunks of about 45 (Train batch, pick 45, add_batch yes; TQs run every other chunk by default), with no engine
   change between them; proposals queue in `data/model/causal_map.json` "waiting" and in this file. Discovery again
   after the second chunk (second run offers candidates).
4. Next bundle (after 4 or 5 chunks): Denning's rulings below; readability items 2, 3, 4, 7, 9 and the contradictions
   (docs/tests/readability-2026-11-09b.md); the second form of the query tool (a situation without a match); per-node
   readings by strength band; port `nodes.py` nodes into the learned-node framework if wanted.

## Open rulings for Denning
- The five decision definitions (SPEC.md section 6: offence_or_defence, eight_v_eight_or_flag, who_defends,
  npcs_or_dp, play_for_28_or_lord): confirm or change how each moment and choice is detected.
- Input cap: one input per 20 events (SPEC.md section 5). Several nodes cannot reach it because most of their inputs
  are Denning's links or supported (the report says "inputs N of a cap of M"): confirm the cap stands as a target, or
  set another number, or allow pruning of Denning's not-clear links too.
- The selection check flags persistent causes as well as markers (defenders in the pit through an enemy's visit).
  Ruling as built: flagged inputs are never fixes. Confirm, or exempt decision inputs (allocation counts).
- `flag_answer` stays a separate execution node (how well the answer run was executed), or is folded into the runs.
- Links the data says to reject (report section "For Denning"): override yes, or not yet.
- Blind test picks: 9 of 10 model calls equal the usual play, so the test mostly scores Denning against the usual
  play. Keep as is (it tests the whole engine's call), or re-pick with at least half the moments where the advice is
  specific (differs from the usual play).
- Discovery pool: the catalogue generates own_, enemy_ and diff_ variables. Rule as proposed: offer own_ only (what
  the team did); show enemy_ as the concurrent response beside it; diff_ not offered (half enemy).
- Reactive execution inputs: the micro answers read "disables on the enemy" (TQ 3) and "healing on own NPCs" (TQ 4)
  as pushing toward the bad result; both are reactions to a fight going badly, not causes, and the selection check did
  not catch them (power plays and NPC losses barely repeat within a match). Proposed for the next bundle: an expected
  direction per execution input (as the win model has direction corrections); an input whose curve runs against it is
  labelled "reads backwards: likely a reaction" and is never a fault or a fix. Rule on the principle.

## Running it
- Train batch: `gh api -X POST repos/itsha12/gvginfo/actions/workflows/train-batch.yml/dispatches -f ref=main
  -f 'inputs[pick]=45' -f 'inputs[add_batch]=yes'` (rebuild only: `inputs[add_batch]=no`, no pick; TQs: `inputs[tqs]=yes|no|auto`).
  Then pull main and read `data/model/reports/latest.md`. Discovery: the "Discovery" workflow.
- Query tool: `python3 ask.py <report id> <m:ss> [team]` (needs `analyze.py --all --out /tmp/ga` and the cache warm).
  Cache pulled, `analyze.py --all` takes 10 s here, `advice.py --blind-only` 3.5 min. Workflow artifacts can't be
  downloaded from the workspace (Azure blocked); `gh api` and git work.
- Local engine: `git fetch --depth 1 origin +replays:refs/remotes/origin/replays`; `pip install
  --break-system-packages -r .github/workflows/train-requirements.txt`; in tools/replay_analysis `cache.py sync pull`,
  `cache.py warm`. `GVG_SUBSET=40` runs any of it on the first 40 matches (local smoke tests only). Run Python with
  `PYTHONDONTWRITEBYTECODE=1`; scripts that fit in parallel need an `if __name__ == "__main__":` guard.
- Cache keys are by layer (`cache.py info`): edits to report modules (tq, learning, causalchain, snapshot, modelpage,
  advice, ask, behaviour, discover) rebuild nothing; edits to measurement modules rebuild prepared data.
- GitHub GraphQL is blocked; use `gh api` (REST). The workspace can't reach gvg.report or the wiki.

## Cautions
- Links near the line flip between runs ("supported" by a small margin is a lead; the diff lists flips); fits differ
  in the last digits between machines, so small report differences are noise.
- No energy, line of sight or NPC positions in the replays; proxies carry lower confidence.
