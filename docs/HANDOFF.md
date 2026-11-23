# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-23, evening: the measurements of R-572 built on the branch while he marks the Lord push rows)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in
  progress. Rulings run to R-648 (none new this chat). The baseline (R-491) is the branch `baseline-2026-11-15`.
- Graded and filed (set f1): thirteen games. No family: numbers from kills (R-557), the push (R-597), a team held
  in its base (R-621). No more matches until the engine is ready (R-570). The Lord push page has twelve rows: four
  filed as set p4, eight of the draft not begun (R-647). `Moments.end_play` is a draft no play reads (R-648).
- Built this chat, on the branch; no play moved (33,371 plays identical, the key `npc` aside):
  - Execution, both teams by the same measures (2.12): `execution.py`, a play's first 20 s; `cases.py execution`.
    Up on numbers, damage, interrupts on their monks, knockdowns and degen go with a better 90 s; a player down,
    what the enemy does tells far more than what the team does.
  - A team held in its base (R-621), 1,399 holds set alike: healing its own NPCs goes with a held player dying
    less (8 points); the holders' damage on players with a death (22 points more), on NPCs with a pit NPC lost
    (24 more). Most likely what the holders went for, not a choice of the held team: put to him.
  - NPC damage by kind of bar (R-433): `npcpower.py`, `npc` on a group's properties (nothing reads it yet). The
    pair rule (2.13): `model.steady_pairs`; tried on made-up data only, the fit runs at the rebuild.
  - The decision to split at all, stage 1 (R-558): `cases.py split-at-all`. A split is sent 6.0% of the times
    asked; more by a team a player down, behind on morale or late. One or two players: a worse 180 s than no
    split from the same standing; three or more: no clear difference. Not advice.
  - What is at stake (R-509): `tools/golden/stake.py`. Only 10 Weak or No decision rows are still read by the
    engine (56 of his rows are no longer read at all): no cut tells them apart, so nothing is added to the band.
- Last checkpoint (every counted match, this engine): 564 matches, 33,371 plays, no errors; fifteen truths hold;
  316 Classic rows pass (the three p4 ones now scored), none fail; self-check 6 in 4; history rows as before.

## Next (in order): the engine substantially finished before the merge and training (R-571, R-572)
1. The play for 28:00: his marks on the eight draft rows, read from `lord_row_marks.json` and filed in set p4 with
   his words; then, with his word on Open 1, `jobs.lord_plays` read from `Moments.end_play` in place of the hits
   on a Lord: one row a match for the play, a push before it as a Lord line on its pinned row (all 25 have one).
2. What is left of the measurements: his answers to Open 2 to 4; execution said on a row in words (`exec_place`
   is built, the sentence is not); the split's NPC damage in the like spots of a split; the old execution inputs
   the new record lacks (casts into a ready interrupt, attacks while Blind, damage off shield sets).
3. Stage E (REDESIGN.md): the new families beside the old kinds for one rebuild (R-323), the stand-in prices
   replaced by the win model, the replaced kinds retired, the causal map cleaned, SPEC and METHODS rewritten, the
   readability test, his list of R-398, the merge, then one Train batch on the same 506 matches (he starts it).
   Before it, a new trim keeps gvg.report's flag objects (R-481), Lord damage record (R-632) and prot, degen,
   interrupt and death items (R-636 to R-639); who stripped which enchantment is read from our replays (R-637).
4. With matches in: the split family again; the danger zone's two factors; the opening hand-off and held flags.

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand, with R-553 to build, and for a double run from the
   sender's side: raise them when more matches are trained. The execution list (R-557).
1. Eight draft rows wait on the Lord push page (R-647); the 25:00 line later. For the Lord play: three Classic
   rows are pushes before it (hold v RACK 24:48, Crew v cope 24:44, Team v hook 24:02), Men v Crew 27:03 and 27:20
   become one play, 27 early Lord visits stop being told.
2. The hold (put to him 2026-11-23): is healing the NPCs or the players a choice of the held team, or does it
   follow what the holders hit? Should a hold be told with what the holders went for (NPCs or players)?
3. One or two players sent from a level standing read worse than no split: is a lone player leaving always a
   split to him? Picked rows on the site were offered. 4. The NPC damage table: anything against what he knows.
5. Eleven flag cards to mark (six again, five new; the 2026-11-23 handoff in git has which). R-576's reading and R-575 on Nomad's are Claude's: bring him what either tells wrongly.
   Tolkano: no build (his word): give him date, guilds, hall and length with every example.

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
