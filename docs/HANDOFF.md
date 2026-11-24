# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-24, late: rulings to R-696; the energy scale corrected, the excuse built)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stages D and E) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored, each with its file beside it; 564 count (R-477); 506 matches
  trained. No workflow run in progress. Rulings run to R-696. The baseline (R-491): `baseline-2026-11-15`.
- Graded and filed (set f1): thirteen games. No family: numbers from kills (R-557), the push (R-597), a held team
  (R-621). No more matches until the engine is ready (R-570). Nothing waits for his marks.
- On the branch (stage E, step 2; CLAUDE.md "The engine on the new trim"), at 7bce16e: the reader, flag returns
  (R-481), the Lord record (R-632 to R-635), degen as damage (R-638, R-649, R-655, R-661; R-676), and energy: the
  reading, piece (2) (every play's monk energy, the tables of R-688, R-696, the like spots) and (3), the excuse.
- The review of the energy build (2026-11-24, at his word): the scale had death penalty and morale on the whole 72;
  they act on the base 20 only. Corrected, with the Elementalist read from the set he holds; the tables and the
  danger zone were rerun and told to him. Last full run: 7bce16e (23 minutes; 33,094 plays identical to f85a242);
  development set 6,933 identical, 323 Classic rows pass; every `cases.py` report rebuilt but the truths (no play
  moved) and `npcpower.py bench`.

## Next (in order): the engine substantially finished before the merge and training (R-571, R-572)
1. Energy, in his order (R-689; CLAUDE.md "The engine on the new trim" has each piece in full). Built: the
   reading, (2) and (3). He wants no further nuance on the decisions (2026-11-24). Next: (4) casting efficiency,
   which needs what each prot did (R-636) and the interrupt attempts (R-639) read first (R-678 to R-680, R-687,
   by monk role, R-671). Each piece: the development set, the key, `compare.py`.
2. Stage E, step 2 goes on: the rest of degen (R-649): the death accounts read gvg.report's recaps (R-636, R-638);
   `eventlayer.py` (the roles' usual, so `dmg_v_usual` takes degen on both sides), `forensics.py`, `events.py`,
   `nodes.py`, `fights.py`, `scoreboard.py`, `phases.py`, `episodes.py` wherever damage is summed from hits; the
   story and the reports. Then interrupt attempts (R-639), what each prot did and the recaps (R-636), who
   stripped which enchantment (R-637), a hold told with what the holders went for (R-658). Each piece: the
   development set, the key, `compare.py` (`--skip props,npc,taken_degen,taken_all,npc_dmg_all` for the degen
   keys; two full plays files do not fit in memory together: compare them by a hash a play, as on 2026-11-24);
   a full run at the end, with `npcpower.py bench` and the truths.
3. Still to do from the runs on the new prices and flag tally: the flag readings he has seen, shown again (R-635).
4. The close: the new families beside the old kinds for one rebuild (R-323), the stand-in prices replaced by the
   win model, the replaced kinds retired, the causal map cleaned, SPEC and METHODS rewritten, the readability
   test, his list of R-398, the merge, then one Train batch on the same 506 matches (he starts it). With matches
   in: the split family again; the danger zone's two factors; the opening hand-off and held flags.

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand, with R-553 to build, and for a double run from the
   sender's side: raise them when more matches are trained. The execution list (R-557).
1. Put to him 2026-11-24 with the review, no answer yet: (a) do Elementalists carry a double high set as monks do
   (seen held in 36% of their games, monks in 26%; the build assumes yes, R-686); (b) a heal or prot monk in party
   slot 1 to 5 is read as a smite monk by the whole engine (about 30 of 3,100 monk-games; told by slot in twelve
   places): proposed, one reading by his bar, as its own step, since it moves plays; not built; (c) a team with a
   Ritualist backline has no monk energy (R-457, R-670): his to say if a healing Ritualist counts for energy.
2. RACK v hdm 7:40 is told with its call again at 300 with degen (as he first graded it): told to him.
3. The NPC damage table with degen (R-659) was shown to him 2026-11-24; no word on it yet.
4. 옷옷옷옷 v RACK 6:15 (Visible, one row, R-495): told at 6:27, the take-up of a flag lying at the door. His to say
   if a run for a flag left lying should start when its taker sets off.
5. The early September matches (R-673, with the counts): energy is built now, so it is due: raise it at R-398
   and before a pull.
6. R-576 and R-575 on Nomad's are Claude's readings: bring him what either tells wrongly. Tolkano: no build.

## Running it
- Train batch: the "Train batch" workflow (METHODS.md; `blind` stays no). Never queue two runs.
- Local engine: `git fetch --depth 1 --no-filter origin +replays:refs/remotes/origin/replays` (the files beside the
  replays come with it). `jobs.py`, `moments.py`, the gate, the line-up and `confidence.py` need only Python;
  `cases.py` needs numpy and scikit-learn (`cache.py sync pull`, `warm` only for the fitted models). On a machine
  with 2 cores and 6 GB: the development set takes about 6 minutes, a full run (`moments.py all`) about 40, and
  it needs the machine to itself. `cases.py ladder` before `cases.py test` (R-545), each kept with `--json
  data/model/<name>.json`. Set `PYTHONDONTWRITEBYTECODE=1`. The key, `dev_set.json` and `game_reviews.json` are
  written on main: pass `--key <main>/data/model/review_key.json`, copy both to the branch after a change;
  `hall_features.json` is changed on both.
- Site check: `python3 -m http.server`, then playwright with `/usr/bin/google-chrome`, api.github.com mocked.

## Cautions
- Never print or decode a sealed field (blind picks, golden moments) in a chat.
- Don't merge `bundle-4` piecemeal (R-322). Label, golden and review mark files are saved whole by the site: after a
  change here, he reloads the page first. Hall labels are saved to main: copy changed `data/maps/labels/*.json` to
  the branch before reading a hall (the export refuses otherwise).
- Transcripts never go in the repo: paraphrased statements only. Party slots are in `data/matches/`, not the
  replays. The branch's own `CLAUDE.md` and `docs/` are old copies: main's are the ones kept up to date.
