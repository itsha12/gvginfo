# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-18, 16:45: eleven games graded and filed; his answers recorded; nothing waiting to be built)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` (engine at 8882861)
  and lands in one piece, then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No
  workflow run in progress. Rulings run to R-529. The only rows on the page not marked are six of game 12.
- The baseline (R-491) is the branch `baseline-2026-11-15` (`bundle-4` at fd2b30b; figures in `data/model/baseline/`).
  Built on `bundle-4` since, all from his marks: R-498 to R-529 (CHANGELOG, DEFINITIONS). In short: his guide of
  2026-11-17 on splits and main teams (a guide, never a ruling; `main_team`, switch `HOME_GUIDE`); one fight a player
  (R-519); the opening as one description (R-520); every flag run told once (R-521); the match over
  (`Moments.over`); a split a player down, or collapsed on, meets its job by losing nobody (R-517, R-523); two
  flaggers on one another are one push (R-528, `flag_pushes`); a split's door read phase by phase and a split out
  of a held base told from when its player goes out (`split_plays`); players who came for a flagger on his run and
  left when the flag had gone are the push and no split (`jobs._push_not_split`, built last, from four rows in three
  games; Claude's reading of his marks, not yet confirmed by him: item 3 under "Open for Denning").
- Confidence (R-515, fitted to five games, figures at the top of `confidence.py`): it cannot tell Visible from Weak
  or No decision; what would is a measure of what is at stake (his four reasons, R-509). Not built.
- Graded and filed (set f1), decisions read correct and decisions he had to add: HC v Team 85%, 0; Men v Crew 77%,
  0; 옷옷옷옷 v RACK 67%, 7; Men v RACK 71%, 4; Men v hold 80%, 5; hold v Men 95%, 0; HC v hdm 90%, 0; RACK v hdm
  100%, 0; hold v RACK (game 10, 25 minutes, 27 split rows all read correct) 95%, 0; HC v cope (game 11) 96%, 0;
  옷옷옷옷 v hdm (game 12, graded to 9:40) 80%, 0. hdm v HC (bbef1904) is out (R-522); never pick it again. He has
  since withdrawn two marks (hold v RACK 4:40, game 12 at 9:40: the engine was right) and confirmed hold v RACK 9:19
  as a single run (R-529); the key holds his words and those readings now bind.
- Game 12 and the clock (R-527): the replay page's clock ran about 6% ahead of the game (base res at 4:14 on it; the
  replay has every base res at the two-minute mark). He withdrew his mark on 9:40; 9:00 and 9:32 are still held.
- Now (development set, 53 matches, 4,597 plays): 259 Classic rows pass, none fail; 117 of 120 history rows hold.
  Set f1: 15 of 54 open checks hold. Gate 12 of 12, 63 of 105. Line-up 420 of 426; comms 110 of 157. Self-check 0.

## Next (in order)
1. His answers to "Open for Denning" below. Then further games if he wants them (told him: splits now look proven;
   pushes on a flagger and Isle of Jade are the thin parts).
2. Held for a second game (R-495): a base res counted with the attackers at the footmen, not in the base (HC v hdm
   1:40; game 12 at 9:40 turned out to be the clock); Men v hold 6:48, hold following Men's three with the flag told
   as a push on the flagger (HC v Team 1:30 may be the same); who and how many push a flagger (HC v Team, Men v RACK
   1:08); numbers through the portal on Isle of Jade (Men v Crew); Men v Crew 17:53; a defender's few seconds with a
   flag read as a run (hold v Men 2:34); the 18 s gap at 2:46 in Men v hold.
3. When he says the flag plays are ready: the flag family to the end (R-451); the other kinds after; then stage E.
4. The clean-up (R-398; REDESIGN.md "Before the next training run", nine items: R-524 the README, R-526 the
   Templates tab) comes after the games. A boost row that repeats a single run stays its own row (R-525).

## Open for Denning (all set out in the chat on 2026-11-18; he will answer later)
1. Men v RACK 18:25: the Prot turns toward the split for 8 s and goes back. Part of the collapse, or another monk?
2. Men v hold 17:01: the Fire Ele's split is now told from 17:02 (out past his doors at 16:58). Right time?
3. A push on a flagger or a split: built as "they all came for the flagger and left when the flag had gone". Is that
   his distinction between HC v cope 3:24 (push) and 0:20 (split, the defender carrying his flag)?
4. Game 12, 9:00 (numbers) and 9:32 (held in base): also the clock, as 9:40 was?

## Data looked at on 2026-11-14 (nothing built; nothing from GW Observer in the repo)
- gvg.report's payload holds flag objects with positions (`report.objectives.object_transitions`), which
  `replay_trim.mjs` drops. R-481: keep them at the next rebuild only (a new TRIM_VERSION fetches every replay again).

## Running it
- Train batch: the "Train batch" workflow (METHODS.md "Train batch on GitHub"; `blind` stays no). Never queue two runs.
- Local engine: `git fetch --depth 1 --filter=blob:none origin +replays:refs/remotes/origin/replays` (the blobs come
  as they are read). `jobs.py`, `moments.py`, the gate, the line-up and `confidence.py` need no cache and no packages
  beyond Python (`cache.py sync pull`, `warm` and the pinned requirements only for the fitted models).
  `PYTHONDONTWRITEBYTECODE=1`. The review key, `dev_set.json` and `game_reviews.json` are written on main: pass
  `--key <main>/data/model/review_key.json`, and copy the key and `dev_set.json` to the branch after changing them.
- Site check: `python3 -m http.server`, then playwright with `/usr/bin/google-chrome`, api.github.com mocked.

## Cautions
- Never print or decode a sealed field (blind picks, golden moments) in a chat.
- Don't merge `bundle-4` piecemeal (R-322). Label, golden and review mark files are saved whole by the site: after a
  change here, he reloads the page first. Hall labels are saved to main: copy changed `data/maps/labels/*.json` to
  the branch before reading a hall (the export refuses otherwise).
- Transcripts never go in the repo: paraphrased statements only. Party slots are in `data/matches/`, not the replays.
  Refresh the branch's `golden_moments.json` from main before the gate.
