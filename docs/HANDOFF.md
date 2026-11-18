# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-17, fourth session: game 7 graded and filed; R-520 to R-522 built; games 8 and 9 on the page, unmarked)
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
- Graded and filed (set f1): HC v Team (9b5cdf62), Men v Crew (51683de9), 옷옷옷옷 v RACK (a8ba43a8), Men v RACK
  (45cf6756), Men v hold (572c2f95), hold v Men (b870f84e: Classic 15 of 15 read correct, Visible 4 of 5, calls 36
  of 37). hdm v HC (bbef1904) is out, unmarked: its replay is not adequate to review (R-522); never pick it again.
- Now (development set, 50 matches, 4,346 plays): 139 Classic rows pass, none fail; 118 of 120 history rows hold
  (hdm v hook 10:23, a flag row; hook v hold 12:46). Set f1 has 50 open checks. Gate 12 of 12, 63 of 105. Line-up
  421 of 426; comms 110 of 157. Self-check 0.
- On the page, not marked (engine 7d00efe; the first games with the opening row and runs told once): game 8, HC v
  hdm on Isle of Jade (af831111; 27 situations, 33 calls; high 20, medium 5, two context), and game 9, RACK v hdm
  on Isle of Meditation (d06ef3c7; 11 situations, 20 calls; high 9, medium 2). Never export them again; fix nothing
  against them until he has marked them.

## Next (in order)
1. When he has marked games 8 and 9: `review.py file` for each, his results set out in the chat, Classic faults first.
   Further games when he asks: `moments.py all --dev`, `confidence.py run` (about 12 minutes a game), `review.py export
   --label "game N"`. The moment calls in `moments.py` still read a full collapse and a split's start the old way.
2. Open Classic items in Men v hold and Men v RACK, each needing a root reading, not a rule: the door of Men's
   five-player split at 10:40 (he says back door; the engine says front); hold's Fire Ele solo split from 17:01 (read
   from 17:38); the Prot coming with the Hammer at 18:25 in Men v RACK. And an 18 s gap at 2:46 in Men v hold where
   the split walks round through the middle and the defence shadowing it in the field is not counted.
3. Held for a second game (R-495): who and how many push a flagger (HC v Team, Men v RACK 1:08); a split read where
   he sees a push on a flagger (Men v RACK 0:36, 1:32); numbers through the portal on Isle of Jade; Men v Crew
   17:53; a base res or a split told at or after the last second of a match (Men v Crew 27:40, Men v RACK 19:06);
   a split defender who carries a flag a few seconds read as a single run (hold v Men 2:34: "just brings the flag up").
4. When he says the flag plays are ready: the flag family to the end (R-451); the other kinds after; then stage E.

## Open for Denning (asked in the chat on 2026-11-17, fourth session)
1. What was missing in the hdm v HC replay, so that picks can avoid it: nothing in the stored replay tells it apart.
2. Whether a split that is collapsed on should also meet its job by losing nobody (R-517 covers a split a player down).
3. The opening's wording and what else it should say, once he has seen it on games 8 and 9.

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
