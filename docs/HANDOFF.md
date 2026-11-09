# GvG Info: handoff for a new chat

Rewritten each session; stays under 80 lines. Read `CLAUDE.md`, then `docs/SPEC.md`, then this. History is in
`docs/CHANGELOG.md`; Denning's rulings in `docs/RULINGS.md` (cite R-numbers).

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, then:
> <your request>

## State (2026-11-09)
- Portal: unchanged since 2026-10-15 (Schedule, Recent matches, Builds, Meta, Guilds, Players, Templates, Skills,
  Mechanics, Settings). 1,631 of 1,661 listed matches stored; press Update matches once more.
- Model: 356 matches trained (chunk 6, batch 15, run 42560128096). Honest test clear: glass box 0.358 against 0.472
  for strength alone (gain +0.114, 90% range +0.064 to +0.161); 84% of winners picked on unseen matches; 76% against
  59% in matches even on strength. Footmen now counted as losses (footmen_lost_diff).
- Review of the engine (RULINGS.md "2026-11 review"): one model family in tiers, time order, pruning, the selection
  check, discovery scope, generated model page, spec/changelog/rulings split, cache by layer, diff reports, one
  engine change per run of chunks, macro and micro answers, five new decisions, the query tool as the end product,
  period and strength-band readings, the advice test and the blind test.
- Documents restructured this session: SPEC.md, RULINGS.md, CHANGELOG.md, this file, CLAUDE.md working rules.

## Engine bundle 1 (status in CHANGELOG.md; items not yet built are listed under Next)
M1 tiers and retired duplicates; M2 time order with the concurrent panel; M4 pruning; M5 selection check; M6
discovery scope; the five decisions; E1 generated model page; E4 cache keys by layer; E5 run-time cuts; E6 diff
report; period and strength band; the advice test.

## Next (in order)
1. Finish any bundle 1 item still open (see CHANGELOG.md for what was built), test on a few matches locally, push,
   one Train batch rebuild (add_batch no), compare the readings with chunk 6 above.
2. Bundle 2: the variable catalogue (`catalogue.py`) screened by `discover.py`; behaviour clusters at every recurring
   state (`behaviour.py`); the query tool (`ask.py`).
3. Readability test: a fresh session reads `knowledge/model.md` alone and explains each node in GvG terms.
4. First advice test reading and the sealed blind test (ten moments; Denning's call and the model's, scored by
   outcome).
5. Then chunks of about 45 (Train batch, pick 45, add_batch yes), no engine changes between them; proposals queue.

## Open rulings for Denning
- The five new decision definitions (SPEC.md section 6, marked "to confirm"): how each moment and choice is detected.
- Whether `flag_answer` stays a separate execution node (how well the answer run was executed) or is folded into
  the run nodes.
- Input cap: one per 20 events (SPEC.md section 5). Confirm or set another number.

## Running it
- Train batch: `gh api -X POST repos/itsha12/gvginfo/actions/workflows/train-batch.yml/dispatches -f ref=main
  -f 'inputs[pick]=45' -f 'inputs[add_batch]=yes'` (rebuild only: `inputs[add_batch]=no`, no pick). Then pull main
  and read `data/model/reports/latest.md`.
- Local engine: `git fetch --depth 1 origin +replays:refs/remotes/origin/replays`; `pip install
  --break-system-packages -r .github/workflows/train-requirements.txt`; in tools/replay_analysis `cache.py sync pull`,
  `cache.py warm`. Run Python with `PYTHONDONTWRITEBYTECODE=1`; scripts that fit in parallel need an
  `if __name__ == "__main__":` guard.
- GitHub GraphQL is blocked; use `gh api` (REST). The workspace can't reach gvg.report or the wiki.

## Cautions
- Links near the line flip between runs; read "supported" by a small margin as a lead.
- Fits differ in the last digits between GitHub processor types; small report differences are noise.
- No energy, line of sight or NPC positions in the replays; proxies carry lower confidence.
