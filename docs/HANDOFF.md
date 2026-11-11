# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, then this, then `docs/REDESIGN.md` (the
plan for the decision tier). History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md` (cite R-numbers); every fitted
model's structure: `knowledge/model.md` (generated).

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out the branch `bundle-4` in a second worktree, then build the split fight record (R-365) and show it to me on
> Nick's three games before anything else.

## State (2026-11-11: redesign step 2 on branch `bundle-4`, last engine commit 9570f3d; batch 17, 506 matches trained)
- Main's engine is unchanged (as SPEC.md describes). Bundle 4 is built on `bundle-4` and lands in one piece, then
  one rebuild (R-322). 513 replays stored. No Train batch, Discovery or fetch run in progress.
- On `bundle-4`: `hallmap.py` (zones, walked distance, footmen reach, places in his words), `moments.py` (the old
  draft moments, families 1 to 3, and since 2026-11-11 the records), `story.py` (prints from the records),
  `tools/golden/golden.py pick|score|stories` (never reads the sealed field).
- On main: Model > Golden moments (`golden.js`, `golden_moments.json`: his labels only; `golden_stories.json`, draft
  5), `data/commentary/nick.json` (9 games), rulings to R-367.

## Next (in order)
1. On `bundle-4` (`git fetch origin && git rebase origin/main` first): the split fight record (R-365), one record
   while the same two groups stay engaged wherever it drifts. Test on Nick's games (b5760ac4 Men v NwAy: NwAy's
   second attempt, met in the middle; 2615ca0c; 62c3fad6) and on the blind note for ohno v xxx (29aad8d4, "the 4v4
   split"). Then the all-match counts, regenerate the stories, blind check.
2. Check what is unchecked: "main team joined" endings (35%), the main team rule on more of his notes, giving
   ground. Then rebuild the old moments (triggers, scenarios, calls) on the records (R-351) and `golden.py score`
   against his marks (R-354).
3. Line-up (`tools/golden/lineup.py` on the branch, statements in `data/lineup/` on main, R-368 to R-372): 7 of 17
   timestamped transcripts filed (549 statements: 75% of the checked ones agree, 94 differ, 166 have no word yet).
   Still to file: Maga's other comms and the four held-out games (R-370). Open: which match is the vine seed comms.
4. Stage D on the branch (consequence record at 90 s and about 3 min, similar cases, the job table, enemy
   execution, the five proposals of R-324, radius checks to `st.zone`), then stage E (side by side for one rebuild,
   SPEC.md and METHODS.md rewritten, readability test, merge, Train batch with `add_batch=no`). REDESIGN.md has both.

## Open rulings for Denning (set each out in the chat, R-329; R-318 to R-341 ruled 2026-11-10)
- R-341 sets the direction: the engine reads a match as his golden notes do; R-334 to R-340 and R-348 to R-352
  define its words. All 14 halls have a Greater stand area label.
- Golden moments (R-354): the page shows the engine's story of each of the 30 games (`golden_stories.json`, draft
  5); he ticks wrong lines and adds notes. His 13 earlier notes are the fixed blind check (`blind_note`). Draft 3
  (from his marks on game 1): STATE lines, who goes back for the flag and when, dropped flags, footmen engaged,
  doors as routes. Draft 4 (from Nick's commentary): one death line per place, the base res read from whether it
  took the player (the replay clock is off by up to 2 s), the Lord's death ends the story, a resignation is named.
  Waiting on him: review game 1's story, then say whether the form is right before marking the rest.
- Commentary trial (2026-11-11): Nick's transcripts have no timestamps, but the order of deaths, caps, splits and
  NPC kills lines them up with the story every 30 to 60 s. `data/commentary/nick.json` now holds 9 games (81
  claims, each with the story's check). "Boss" is September's flux (Like a Boss), not the boost: corrected.
  Still to line up: 983a47db (xxx v ohno, report d70f3684); 00cb0759 has no transcript.
- Built 2026-11-11 on the branch from R-355 to R-364 (the record is the work, R-362): `Moments.attempts()` (one
  record a split attempt or main team push: who, monks, way in, the answer, main team numbers meanwhile, end,
  result, linked moves), `caught()` (in the enemy base at the defenders' base res), `flags_record()` (runner, time
  away, backup flag, back cap, with a split, drop place, boost clock, died carrying), `main_team()` and `lane()`,
  `common.flux_at`. `moments.py <id> splits|flags` prints them; `story.py` prints its split, push and cap lines from
  them. 513 matches: 1,909 splits (3.7 a match), 1,681 pushes. Against Nick's three games 12 of 13 attempts found.
- Ruled 2026-11-11 (R-365 to R-367), next to build: one split fight record for as long as the same two groups
  stay engaged, wherever it drifts (whose ground, how long, who started it); this also covers a split met in the
  middle. Back cap confirmed as built. Solo splits parked (45% of records; do not rely on them). Still unchecked:
  "main team joined" is 35% of endings; the main team rule was tuned on Nick's three games; giving ground is read
  from the middle player. The old F1 to F3 moments still run beside the records and are not rebuilt on them.
- Also open: noisy "go to split" lines, threat or posture, hand-off to hold, time to cap, `golden.py score` against
  his marks, a monk energy estimate only if needed (R-353), discovery second run, behaviour clusters.

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
- Don't merge `bundle-4` piecemeal (R-322). No Train batch or Discovery run in progress. Label and golden files are
  saved whole by the site: after a change here, Denning reloads the page first.
