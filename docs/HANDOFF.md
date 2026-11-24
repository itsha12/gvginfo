# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-23, late night: his answers R-656 to R-664; the new trim part built and its refetch started)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 660 replays stored (two added by the test fetch, his to keep or take out); 564 counted at the last
  checkpoint (R-477); 506 matches trained. The refetch run is in progress (below). Rulings run to R-664. The baseline (R-491): `baseline-2026-11-15`.
- Graded and filed (set f1): thirteen games. No family: numbers from kills (R-557), the push (R-597), a held team
  (R-621). No more matches until the engine is ready (R-570). His marks on the eight draft Lord rows (p4-9 to
  p4-16) and on the eleven flag cards are filed; no flag card waits.
- On the branch from the chat before (CHANGELOG, 2026-11-23, night): the Lord play read from the end record
  (R-650 to R-654: the play for 28:00 one row a match; a push before it a Lord line on the row it grew out of),
  execution in words, and the split's NPC damage in what like spots are matched on. Readings, not advice.
- The new trim part (stage E, step 1), on main: `tools/gvgreport/replay_extras.mjs` writes `<id>.x.json.gz` beside
  each stored replay (flag objects, Lord record, prot, degen, attempts, recaps, energy); the stored replays are not
  written again. Tested on hdm v Men, RJT v RACK, Book v hook, Team v hook and BcS v Apes: the four known returns,
  the stored Lord scores, 210 attempts and the degen figures of R-638 all come out. The refetch of every stored
  match was started at 03:54 UTC on 24 November (run 45322644533, about two hours): check `x` = 2 on every entry of
  the replays index; start "Fetch replays" again if any are left. The engine does not read the file yet.
- Last checkpoint (every counted match): 564 matches, 33,111 plays, no errors; fifteen truths hold; 323 Classic
  rows pass, none fail; self-check 6 in 4. One change after it (One v Team 22:30, the last push with no row).

## Next (in order): the engine substantially finished before the merge and training (R-571, R-572)
1. Stage E (REDESIGN.md); no Lord rows go on the page first (R-660). The order he agreed on 2026-11-23 ("2.
   Yes."): the new trim first (built; verify the refetch), then the engine on it, then the close. The close: the new families
   beside the old kinds for one rebuild (R-323), the stand-in prices replaced by the win model, the replaced kinds
   retired, the causal map cleaned, SPEC and METHODS rewritten, the readability test, his list of R-398, the
   merge, then one Train batch on the same 506 matches (he starts it).
   The new trim keeps gvg.report's flag objects (R-481), Lord damage record (R-632) and prot, degen, interrupt
   and death items (R-636 to R-639); who stripped which enchantment is read from our replays (R-637); every
   damage figure then takes degen in (R-649, R-655), gvg.report's own on players, NPCs and Lords (R-661); energy read from the same file (R-664).
   To build with it: a hold told with what the holders went for, NPCs or players; the held team's healing is a
   reaction, never a call or a fix (R-658).
2. With matches in: the split family again; the danger zone's two factors; the opening hand-off and held flags.

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand, with R-553 to build, and for a double run from the
   sender's side: raise them when more matches are trained. The execution list (R-557).
1. To do when the refetch run has saved its work (never before: its push to `replays` would fail): check `x` = 2
   on every entry of the replays index; take chic v DUM (0e935804) and HC v hdm (524ee2e7) out of the store and
   the `latest:2` line out of `replays/requests.txt` (R-663; a push of that file starts a Fetch run, which then
   does any extras left). Then remind him, as he asked, to add energy to the build (R-664: the engine reads
   gvg.report's estimate; set out for him where it bears, the list in the ruling, before building).
   BcS v Apes: gvg.report's Lord score for team 1 is 3,390 and its events rebuild to 3,360 (`x_check`).
2. Once degen counts: the danger zone's 250 again (R-649), and the NPC damage table read again (R-659).
3. Not a question for him: one or two players sent from a level standing read worse than no split (-7.6 win
   points at 180 s). The record reads the split records of the plays, so a split there is a split as he has
   ruled it (R-562); it stays a stage 1 reading and waits for matches (R-570).
4. R-576's reading and R-575 on Nomad's are Claude's: bring him what either tells wrongly. Tolkano: no build (his
   word): date, guilds, hall and length with every example.

## Running it
- Train batch: the "Train batch" workflow (METHODS.md; `blind` stays no). Never queue two runs. At the next rebuild,
  keep what R-481, R-632 and R-636 to R-639 list (dropped by the trim and `extract.mjs`; R-636 in its own file a match).
- Local engine: `git fetch --depth 1 --no-filter origin +replays:refs/remotes/origin/replays`. `jobs.py`,
  `moments.py`, the gate, the line-up and `confidence.py` need only Python; `cases.py` needs numpy and scikit-learn
  (`cache.py sync pull`, `warm` only for the fitted models). A full run (`moments.py all`) takes about 11 minutes
  on two cores; `cases.py ladder` before `cases.py test` (R-545), each kept with `--json data/model/<name>.json`.
  Set `PYTHONDONTWRITEBYTECODE=1`. The key, `dev_set.json` and `game_reviews.json` are written on main: pass `--key
  <main>/data/model/review_key.json`, copy both to the branch after a change; `hall_features.json` is changed on both.
- Site check: `python3 -m http.server`, then playwright with `/usr/bin/google-chrome`, api.github.com mocked.

## Cautions
- Never print or decode a sealed field (blind picks, golden moments) in a chat.
- Don't merge `bundle-4` piecemeal (R-322). Label, golden and review mark files are saved whole by the site: after a
  change here, he reloads the page first. Hall labels are saved to main: copy changed `data/maps/labels/*.json` to
  the branch before reading a hall (the export refuses otherwise).
- Transcripts never go in the repo: paraphrased statements only. Party slots are in `data/matches/`, not the
  replays. Refresh the branch's `golden_moments.json` first.
