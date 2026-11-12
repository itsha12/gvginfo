# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, then this, then `docs/REDESIGN.md` (the
plan for the decision tier). History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md` (cite R-numbers); every fitted
model's structure: `knowledge/model.md` (generated).

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next" item 1 and tell me where the line-up stands.

## State (2026-11-11: redesign step 2 on branch `bundle-4`, last engine commit 9fca5f5; batch 17, 506 matches trained)
- Main's engine is unchanged (as SPEC.md describes). Bundle 4 is built on `bundle-4` and lands in one piece, then
  one rebuild (R-322). 606 replays stored (90 random ones from 2 September on were fetched 2026-11-11 and are not
  yet trained on). No Train batch, Discovery or fetch run in progress.
- On `bundle-4`: `hallmap.py` (zones, walked distance, reach, places in his words), `moments.py` (the records),
  `story.py` (prints from the records, R-362), `tools/golden/golden.py pick|score|stories` (never reads the sealed
  field), `lineup.py score|lines` (the line-up), `thresholds.py run|show` (all-match counts, 10 minutes).
- The records in `moments.py`: `attempts()` (splits and main team pushes, solo split by R-381), `caught()`,
  `flags_record()`, `main_team()`, `lane()`, `moves()` (joins and leaves player by player), `split_fights()` (one
  record while two groups stay on each other, swaps from each stay), `ground()` (main team and each side of a
  split fight fall back or push up, by walked distance), `undefended()`, `on_pit()`; `fights(t)` cuts a small
  fight off a bigger one; `place_at` names the pit by its NPCs (R-387); a split fight keeps `pulled` (a player taken
  off it onto the main fight); `flag_ev` gives a capture with no pickup recorded its pickup (69 of 5,245).
- On main: `data/lineup/` (16 transcripts typed as paraphrased statements: 12 for building, 4 held out, R-370),
  Model > Golden moments (15 games, R-382; the other 15 under `parked`; `golden_stories.json` still draft 5),
  `data/commentary/nick.json` (9 games), rulings to R-389.

## The line-up (R-368 to R-389), the measure of the reading stage
- `lineup.py score --data <main>/data/lineup [--held] [--show]` with `LINEUP_CACHE` set (delete it after an engine
  change; about 10 minutes). The gate is 90% agreement on things seen happening in the four held-out games (R-380,
  R-383); calls on comms are reported beside it.
- Seen events: building games 364 of 365, held-out 135 of 162 (83%). Comms calls: 104 of 152 (68%), 59 of 76 (78%).
- The building figure follows Denning's review of its 61 misses (R-386): 36 confirmed as the engine reading right
  (`ok.`), 5 calls withdrawn, the rest retyped as he corrected them; 12 were the engine's and 10 are fixed (R-389).
  The one left: xxx's split "falls to its back footies" (2:57): it stands 600 to 1,050 from its back footmen, which
  are not fighting, so the engine says back door (R-307).
- The held-out games have not been reviewed. He reviews their misses once, at the gate; only statement corrections
  follow from that review, never an engine change (R-370). Do not read their individual lines before then.

## Next (in order)
1. Step 1 is built and closes on his rulings (set out to him 2026-11-11; "Open for Denning" below): apply them and
   rescore. No Shadow Step date is needed: all 19 stored steps by a carrier (first 20 August 2026) drop the flag.
2. Step 2, the words of R-373 and R-375 to R-378: flag route, pushing the flagger, flag lead (full and half a
   flag), posture, the four timing choices, monk counts in a fight, who is on the Guild Lord (`on_pit()` is a start).
3. Step 3: regenerate the golden stories (`golden.py stories`, draft 6), the blind check against his 13 blind
   notes, rescore the line-up, then his review of the held-out misses at the gate.
4. Then his review of game 1's story form; rebuild the decision moments (triggers, scenarios, calls) on the records
   (R-351) and `golden.py score` against his marks (R-354).
5. Stage D on the branch (consequence record at 90 s and about 3 min, similar cases, the job table, enemy
   execution, the five proposals of R-324, radius checks to `st.zone`), then stage E (side by side for one rebuild,
   SPEC.md and METHODS.md rewritten, readability test, merge, Train batch with `add_batch=no`). REDESIGN.md has both.
   Training chunks and Discovery resume after the merge; the decision card and the blind test follow.

## Open for Denning (set each out in the chat, R-329)
- The 17 draft thresholds (JOIN_LOOK_S to SPLIT_FIGHT_MIN in `common.py`), set out with their all-match counts.
- "Footies" when a team stands at its own living footmen and the enemy does not follow (the xxx line above).
- A split whose main team is dead is renamed the main team and told as a new "main team push" (202 pushes in 155
  matches; Apes v hold 4:20; `main_team()` is R-355, left as ruled). The Shadow Step fault (R-324) with 19 cases.
- Golden moments (R-354): waiting on him to review game 1's story form; his 13 `blind_note` notes are the blind check.
- Also open: threat or posture, hand-off to hold, time to cap, a monk energy estimate only if needed (R-353),
  discovery second run, behaviour clusters, 983a47db (xxx v ohno, report d70f3684) of Nick's commentary.

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
- Held-out files sit in `data/lineup/` with the rest (header `held_out: yes`): check the header before printing one.
- Don't merge `bundle-4` piecemeal (R-322). Label and golden files are saved whole by the site: after a change
  here, Denning reloads the page first. Hall labels are saved to main: copy changed `data/maps/labels/*.json` to the
  branch before reading a hall (174 and 542 were copied 2026-11-11).
- Transcripts never go in the repo: paraphrased statements only. Party slots are in `data/matches/`, not the replays.
