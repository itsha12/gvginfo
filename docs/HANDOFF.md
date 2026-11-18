# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-18: eight games graded and filed; R-523 built; nothing on the page unmarked)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one piece,
  then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in progress.
- The baseline (R-491) is the branch `baseline-2026-11-15` (`bundle-4` at fd2b30b; figures in `data/model/baseline/`).
  Built on `bundle-4` since, all from his marks: R-498 to R-515 (CHANGELOG, DEFINITIONS), and in this session:
  - His guide of 2026-11-17, not a ruling and not strict (DEFINITIONS "Counting players"; `main_team`, switch
    `HOME_GUIDE`): a split is almost never in its own base; a small group at home with its main team elsewhere is
    most likely a defence. Not touched: the 4 and 3 divide, the even divide (R-335), the held base (R-506).
  - R-517, `split_plays`: a split holding more defenders than its number meets its job by losing nobody. R-518: no
    push on a flagger by position alone; he adds the missed ones.
  - R-519, `_numbers` and `fight_side`: one fight a player, by whom he trades with (DEFINITIONS "Counting players"),
    asked only of players the split's reading counts (`_split_candidates`); `M._side_log` says who went where.
  - R-520, `jobs.opening`: the opening as one description (who went where, who brought the first flag, who capped
    and when). R-521, `review.py flag_rows`: every flag run told once on the page (`run_id`, `answer_id`, `said` on
    flag plays). The base res test counts only the players in the base.
- The fresh start (R-491 to R-497; CLAUDE.md): only Classic rows bind; other grades build from a fault in two games.
- Confidence (R-515, fitted to five games, figures at the top of `confidence.py`): it cannot tell Visible from Weak
  or No decision; what would is a measure of what is at stake (his four reasons, R-509). Not built; 35 such rows.
- Graded and filed (set f1): HC v Team, Men v Crew, 옷옷옷옷 v RACK, Men v RACK, Men v hold, hold v Men, HC v hdm
  (af831111) and RACK v hdm (d06ef3c7). Decisions read correct, game by game: 85, 77, 67, 71, 80, 95, 90, 100%;
  decisions he had to add: 0, 0, 7, 4, 5, 0, 0, 0. The last three are short games with few splits (3, 0 and 1 split
  rows): splits in long divided games are the least proven. hdm v HC (bbef1904) is out (R-522); never pick it again.
- Built on 2026-11-18 from games 8 and 9: `Moments.over` (the match is over when the losing team is recorded dying
  all at once; nothing told from then, those deaths not counted); a numbers call read for as long as the numbers
  last, its row ending with them; the first flag a job for both teams (`opening_plays`); R-523.
- Now (development set, 50 matches, 4,424 plays): 169 Classic rows pass, none fail; 118 of 120 history rows hold.
  Set f1: 11 of 53 open checks hold. Gate 12 of 12, 63 of 105. Line-up 420 of 426; comms 110 of 157. Self-check 0.

## Next (in order)
1. Next games when he asks (told him: three to five more, long even games with many splits and pushes on a flagger):
   `moments.py all --dev`, `confidence.py run` (about 12 minutes a game), `review.py export --label "game N"`. Ready to
   build first (two games, R-495): a push on a flagger read where he sees none (Men v hold 3:12, 6:48; HC v hdm 8:34).
2. Open Classic items in Men v hold and Men v RACK, each needing a root reading, not a rule: the door of Men's
   five-player split at 10:40 (he says back door; the engine says front); hold's Fire Ele solo split from 17:01 (read
   from 17:38); the Prot coming with the Hammer at 18:25 in Men v RACK. And an 18 s gap at 2:46 in Men v hold where
   the split walks round through the middle and the defence shadowing it in the field is not counted.
3. Held for a second game (R-495): who and how many push a flagger (HC v Team, Men v RACK 1:08); a split read where
   he sees a push on a flagger (Men v RACK 0:36, 1:32); numbers through the portal on Isle of Jade (Men v Crew);
   Men v Crew 17:53; a split defender's few seconds with a flag read as a run (hold v Men 2:34); a base res counted
   with the attackers at the footmen (HC v hdm 1:40).
4. When he says the flag plays are ready: the flag family to the end (R-451); the other kinds after; then stage E.

## Open for Denning (asked in the chat on 2026-11-18)
1. A boost row that repeats a single run (HC v hdm 10:51, 14:13, graded Repeat): fold it into the run's row?
2. The Templates tab: the clean-up list removes it, but he saved a template there on 2026-11-18. Keep it?
3. The clean-up (R-398; REDESIGN.md "Before the next training run", nine items with R-524) comes after the games.

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
