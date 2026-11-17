# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-16, evening: three games graded; his rulings to R-507 built, R-508 not yet; games 4 and 5 on the page; 506 matches trained)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one piece,
  then one rebuild (R-322). 658 replays stored; 564 count (R-477). No Train batch, Discovery or fetch run in progress.
- The baseline (R-491) is the branch `baseline-2026-11-15` (`bundle-4` at fd2b30b); its reading and figures are in
  `data/model/baseline/` on main. Built on `bundle-4` since, all from his marks on the three games: R-498 to R-504
  (CHANGELOG), and on 2026-11-16 from his four answers:
  - R-505, `Moments.brought_up` and `not_run`: a flag brought up with the team (team on its own ground at the pickup,
    carrier never 12 s without it, enemy's main team not in the base, never capped or at the stand) is no run, no
    runner, no moment; the other side's row says "brings a flag up with its team (who) but does not run it".
  - The opening's first flag is one run from 0:00 though put down on the way; a flag answer is read inside the
    play's own clock (180 s), not from a run minutes later.
  - R-506, in `main_team` and `_over` (`held_out`): players who leave a base held in by the enemy's main team are a
    split from the second they leave, when as many as those who stay. A 12 s look-back on "held in" was tried and
    not kept (36 doubtful splits on the development set).
  - R-507, `caught`: no base res row for a team that left before the res or is leaving as it lands; a lone player at
    a door has not stayed.
- The fresh start (R-491 to R-497; all in CLAUDE.md): only Classic rows bind; earlier games are history; the other
  grades are built from when a fault shows in two games. He grades on Model > Game review.
- The confidence bands are fitted to his grades of the three games (top of `tools/golden/confidence.py`): high = the
  same under every move; medium = moved only at half or double, or by one setting at a quarter; low = two or more
  settings move it at a quarter. His grades (Classic, Visible, Weak, No decision): high 43, 19, 1, 2; medium 6, 19, 2,
  4; low 1, 14, 7, 7. Steadiness tells Classic from the rest, not Visible from Weak; nothing else is fitted.
- Graded and filed (set f1): HC v Team (9b5cdf62), Men v Crew (51683de9), 옷옷옷옷 v RACK (a8ba43a8). On the page,
  unmarked: game 4, Men v RACK on Nomad's Isle (45cf6756; 40 situations), and game 5, Men v hold on Isle of
  Meditation (572c2f95; 67 situations, 2 folded), both exported at 8e8e9ea with the fitted bands.
- Now (development set, 47 matches, 3,725 plays): 55 Classic rows pass; 119 of 120 history rows hold (hdm v hook
  10:23 is a flag brought up, R-505); set f1 has 30 open checks, none holding. Gate 12 of 12, 63 of 105. Line-up 421
  of 426; comms 110 of 157. Self-check 229.

## Next (in order)
1. His marks on games 4 and 5: `review.py file`, checks by hand, Classic faults first; refit the bands with five games.
2. Build R-508 at the root in `split_plays` (R-465): a full collapse counts from the turn, a few seconds on, reached
   or not (옷옷옷옷 v RACK 1:51, 4:39, 6:01, 8:16; today it is read at arrival, 2:06 and 6:28, or not at all).
3. Held for a second game (R-495): who and how many push a flagger (HC v Team); numbers read through the portal on
   Isle of Jade; Men v Crew 17:53, a pickup 2 s before the boost read as a runner; a base res that lands at the
   last second of a match (Men v Crew 27:40).
4. When he says the flag plays are ready: the flag family to the end (R-451); the other kinds after; then stage E.

## Open for Denning (put to him 2026-11-16; set each out again, R-329, with the replay link)
1. Nothing waits on a ruling. Put to him 2026-11-16, his to answer: reason ticks on Weak and No decision rows (too
   brief, edge too small, no real fight, misread, already covered), and length as a second part of the confidence.
2. Men v Crew 23:56 (Visible, correct) stays a run under R-505 only because Crew's main team was in Men's base
   until 23:50; told to him. 19:53 (Classic, correct, "one runner") stays for the same reason.
- Noted, not put to him (R-491): TFS v 옷옷옷옷 1:54, a flag put on the Obelisk stand reads "our flag is capped: no".

## Data looked at on 2026-11-14 (nothing built; nothing from GW Observer in the repo)
- gvg.report's replay payload holds `report.objectives.object_transitions` (each appearance of a flag object, with
  its position); `replay_trim.mjs` drops it. R-481: keep it in the trim and read flag returns from it at the next
  rebuild, not before (a new TRIM_VERSION fetches every stored replay again; the baseline plays file is kept for
  that reason). GW Observer's licence limits the code and the data: his call. The `full` payload is not probed.

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
