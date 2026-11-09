# GvG Info: handoff for a new chat

Rewritten each session; stays under 80 lines. Read `CLAUDE.md`, then `docs/SPEC.md`, then this. History is in
`docs/CHANGELOG.md`; Denning's rulings in `docs/RULINGS.md` (cite R-numbers); the structure of every fitted model in
`knowledge/model.md` (generated).

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, then:
> <your request>

## State (2026-11-09, after the review bundles)
- Portal: unchanged since 2026-10-15. 1,631 of 1,661 listed matches stored; press Update matches once more.
- Model: 356 matches trained (batch 15). Before the review bundles (chunk 6): glass box 0.358 against 0.472 for
  strength alone (gain +0.114, +0.064 to +0.161), 84% against 77%. After the bundles (rebuild run 42569970450, no new
  matches): win model unchanged (0.358 against 0.472, +0.114); every learned node still beats its baseline with the
  concurrent measures out of the fit; the report now carries the diff, the kinds, the pruned inputs (collapse: 5), the
  "marks the situation" flags, the honest test by month (September 0.443 v 0.577, October 0.282 v 0.395, November
  0.317 v 0.363) and by strength band (even 0.525 v 0.65; moderate 0.33 v 0.469; uneven 0.083 v 0.078, where the
  model adds nothing over strength), and the first advice test: 2 of 13 kinds clear (runner_choice +1.1, split_or_stay
  +0.5); the advice differs from the usual play in only 1 to 5% of cases for most kinds, so today the engine's macro
  advice is mostly "do the usual thing", worth about a point. That is the honest baseline the next bundles work from.
- Everything in the November 2026 review is built (RULINGS.md R-260 to R-277; CHANGELOG.md 2026-11-09 lists each
  piece and the file it lives in). The five new decisions are detected with Claude's definitions, to confirm.

## Next (in order)
1. Read the rebuild's report (`data/model/reports/latest.md`): the "What changed" diff, the learned nodes' new kind
   labels, the pruned inputs and "marks the situation" flags, the advice test, and the TQs' macro/micro split.
   Explain it to Denning; collect his rulings (below) as one bundle; build nothing between chunks.
2. Readability test: run once after the rebuild (docs/tests/readability-2026-11-09.md): verdict no, three page
   changes asked for and built the same night (legend, glossary, one layout with a "what to act on" line per node).
   Run it again on the regenerated page; what a fresh reader still cannot explain goes on the list for the next bundle.
3. Run the Discovery workflow once (it now screens the variable catalogue; a candidate is offered after two runs), and
   `python3 advice.py --blind` once locally to write `data/model/blind_test.json` for the sealed blind test.
4. Then chunks of about 45 (Train batch, pick 45, add_batch yes; TQs run every other chunk by default), with no engine
   change between them; proposals queue in `data/model/causal_map.json` "waiting" and in this file.
5. Next bundle (after 4 or 5 chunks): Denning's rulings below; the second form of the query tool (a situation without
   a match); per-node readings by strength band; port `nodes.py` nodes into the learned-node framework if wanted.

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
- Local engine: `git fetch --depth 1 origin +replays:refs/remotes/origin/replays`; `pip install
  --break-system-packages -r .github/workflows/train-requirements.txt`; in tools/replay_analysis `cache.py sync pull`,
  `cache.py warm`. `GVG_SUBSET=40` runs any of it on the first 40 matches (local smoke tests only). Run Python with
  `PYTHONDONTWRITEBYTECODE=1`; scripts that fit in parallel need an `if __name__ == "__main__":` guard.
- Cache keys are by layer (`cache.py info`): edits to report modules (tq, learning, causalchain, snapshot, modelpage,
  advice, ask, behaviour, discover) rebuild nothing; edits to measurement modules rebuild prepared data.
- GitHub GraphQL is blocked; use `gh api` (REST). The workspace can't reach gvg.report or the wiki.

## Cautions
- Links near the line flip between runs; read "supported" by a small margin as a lead; the diff section lists flips.
- Fits differ in the last digits between GitHub processor types; small report differences are noise.
- No energy, line of sight or NPC positions in the replays; proxies carry lower confidence.
- `data/model/discovery.json` from before the catalogue still lists 18 old candidates until the Discovery workflow
  runs again.
