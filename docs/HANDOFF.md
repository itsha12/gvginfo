# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-18, late: eight games graded and filed; games 10 to 12 on the page, not yet marked)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one piece,
  then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in progress.
- The baseline (R-491) is the branch `baseline-2026-11-15` (`bundle-4` at fd2b30b; figures in `data/model/baseline/`).
  Built on `bundle-4` since, all from his marks: R-498 to R-523 (CHANGELOG, DEFINITIONS). In short: his guide of
  2026-11-17 on splits and main teams (a guide, never a ruling; `main_team`, switch `HOME_GUIDE`); one fight a player
  (R-519, `_numbers`, `fight_side`); the opening as one description (R-520, `jobs.opening`); every flag run told once
  (R-521, `review.py flag_rows`); the match over (`Moments.over`); a split a player down, or collapsed on, meets its
  job by losing nobody (R-517, R-523); a numbers call read for as long as the numbers last.
- Built last on 2026-11-18, from his marks (DEFINITIONS "Flags" and "Splits"):
  - `flag_pushes`: two flaggers on one another are one push; who lands more on the other is the pusher, and the
    flagger pushed is not counted among the players pushing (Men v hold 3:12, HC v hdm 8:34; 13 records in 50 games
    set aside, kept in `M._fpush_answers`). Put to him: is a duel of two flaggers one push or two?
  - `split_plays`: the door is read phase by phase where the players of a phase all start it in the field (Men v
    hold 10:40, Classic); a split out of a held base is told from 4 s after its player goes out past his doors
    (`out_at`; Men v hold 17:01, Classic). Both checks closed in the key and binding.
- Confidence (R-515, fitted to five games, figures at the top of `confidence.py`): it cannot tell Visible from Weak
  or No decision; what would is a measure of what is at stake (his four reasons, R-509). Not built; 35 such rows.
- Graded and filed (set f1): HC v Team, Men v Crew, 옷옷옷옷 v RACK, Men v RACK, Men v hold, hold v Men, HC v hdm
  (af831111) and RACK v hdm (d06ef3c7). Decisions read correct, game by game: 85, 77, 67, 71, 80, 95, 90, 100%;
  decisions he had to add: 0, 0, 7, 4, 5, 0, 0, 0. hdm v HC (bbef1904) is out (R-522); never pick it again.
- On the page, not yet marked (exported 2026-11-18, engine a552659): game 10 hold v RACK, Imperial Isle
  (d492aa6c, 25:16, many splits and full collapses); game 11 HC v cope, Nomad's Isle (3d0f3fc5, 7:22, splits);
  game 12 옷옷옷옷 v hdm, Isle of Jade (53175808, 13:49, numbers through the portal, base res at the footmen).
- Now (development set, 53 matches, 4,611 plays): 169 Classic rows pass, none fail; 118 of 120 history rows hold.
  Set f1: 15 of 51 open checks hold. Gate 12 of 12, 63 of 105. Line-up 420 of 426; comms 110 of 157. Self-check 0.

## Next (in order)
1. When he has marked games 10 to 12: `review.py file` each, write the checks by hand, set the results out in the
   chat (R-329), fix failing Classic rows first, then anything shown in two games (R-495).
2. Open Classic item: Men v RACK 18:25, "collapse by Men's hammer and prot". The Hammer is read; the replay has the
   Prot at RACK's front door until 18:24, in the greater stand area from 18:26 to 18:32 and back at RACK's front door
   at 18:34, so he never reaches the split. Put to him on 2026-11-18: is a turn toward the split for 8 s part of the
   collapse, or did he mean one of the other monks? Nothing built until he answers.
3. Held for a second game (R-495): Men v hold 6:48, hold's main part following Men's three with the flag told as a
   push on the flagger ("collapse rather than flagpush"; HC v Team 1:30 may be the same); who and how many push a
   flagger (HC v Team, Men v RACK 1:08); a split read where he sees a push on a flagger (Men v RACK 0:36, 1:32);
   numbers through the portal on Isle of Jade (Men v Crew); Men v Crew 17:53; a defender's few seconds with a flag
   read as a run (hold v Men 2:34); a base res counted with the attackers at the footmen (HC v hdm 1:40); an 18 s gap
   at 2:46 in Men v hold where the defence shadowing a split in the field is not counted.
4. When he says the flag plays are ready: the flag family to the end (R-451); the other kinds after; then stage E.
5. The clean-up (R-398; REDESIGN.md "Before the next training run", nine items: R-524 the README, R-526 the
   Templates tab) comes after the games. A boost row that repeats a single run stays its own row (R-525).

## Open for Denning (asked in the chat on 2026-11-18)
1. Two flaggers on one another: one push told from the side that lands more (as built), or both?
2. Men v RACK 18:25: the Prot (item 2 above).
3. Men v hold 17:01: the engine now tells the Fire Ele's split from 17:02 (out past his doors at 16:58). Right time?

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
