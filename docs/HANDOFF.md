# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-24, evening: rulings to R-696; energy on every play and its tables built)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stages D and E) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored, each with its file beside it; 564 count (R-477); 506 matches
  trained. No workflow run in progress. Rulings run to R-696. The baseline (R-491): `baseline-2026-11-15`.
- Graded and filed (set f1): thirteen games. No family: numbers from kills (R-557), the push (R-597), a held team
  (R-621). No more matches until the engine is ready (R-570). Nothing waits for his marks.
- On the branch (stage E, step 2; CLAUDE.md "The engine on the new trim"), at a66335f: the reader, flag returns
  (R-481), the Lord record (R-632 to R-635), and degen as damage (R-638, R-649, R-655, R-661): `degen.py`,
  `Match.degen()`, gvg.report's totals laid over the seconds the replay shows them. Taken in so far by the damage a
  player took, NPC damage by kind of bar (benchmark rebuilt), the execution measures and `pressure.py`; the
  danger zone's line is 300 a player, hits and degen (R-676).
- Development set: 6,933 plays, identical to the run before; 323 Classic rows pass. Last full run: the split holds
  commit (18 minutes; 33,094 plays identical to e7fcad1). Energy (R-664 to R-689): the reading and piece (2) built: each fight's monk energy on every play
  (`flag_cost[rid].energy`, read by no play) and `cases.py energy`, the tables of R-688, shown to him 2026-11-24.

## Next (in order): the engine substantially finished before the merge and training (R-571, R-572)
1. Energy, in his order (R-689; CLAUDE.md "The engine on the new trim" has each piece in full). Built: the
   reading; (2) the record and the tables. Next: his word on the tables (Open 1); energy among what like spots are
   matched on (the average); (3) the excuse with energy denial (R-681, R-682, R-685); (4) casting efficiency with
   R-636 and R-639 (R-678 to R-680, R-687). Each piece: the development set, the key, `compare.py`.
2. Stage E, step 2 goes on: the rest of degen (R-649): the death accounts read gvg.report's recaps (R-636, R-638);
   `eventlayer.py` (the roles' usual, so `dmg_v_usual` takes degen on both sides), `forensics.py`, `events.py`,
   `nodes.py`, `fights.py`, `scoreboard.py`, `phases.py`, `episodes.py` wherever damage is summed from hits; the
   story and the reports. Then interrupt attempts (R-639), what each prot did and the recaps (R-636), who
   stripped which enchantment (R-637), a hold told with what the holders went for (R-658). Each piece: the
   development set, the key, `compare.py` (`--skip props,npc,taken_degen,taken_all,npc_dmg_all` for the degen
   keys); a full run at the end, with `npcpower.py bench` and the truths.
3. On the new prices and the new flag tally, before anything is read from them: `cases.py ladder`, then `cases.py
   test` (R-545), and the flag readings he has seen shown to him again (R-635). Not run yet.
4. The close: the new families beside the old kinds for one rebuild (R-323), the stand-in prices replaced by the
   win model, the replaced kinds retired, the causal map cleaned, SPEC and METHODS rewritten, the readability
   test, his list of R-398, the merge, then one Train batch on the same 506 matches (he starts it). With matches
   in: the split family again; the danger zone's two factors; the opening hand-off and held flags.

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand, with R-553 to build, and for a double run from the
   sender's side: raise them when more matches are trained. The execution list (R-557).
1. Energy: his answers on the tables are R-690 to R-696 (energy beside the 300 line; no stand-off decision;
   offensive or defensive play is execution; their monks only at "our flag just in"; no energy at their boost; a
   split already out stays or falls back, by its own monks, built as `jobs.split_holds`). The split table was put
   to him 2026-11-24. Open: his nuances on the remaining decisions.
2. RACK v hdm 7:40 is told with its call again at 300 with degen (as he first graded it): told to him.
3. The NPC damage table with degen (R-659) was shown to him 2026-11-24; no word on it yet.
4. 옷옷옷옷 v RACK 6:15 (Visible, one row, R-495): told at 6:27, the take-up of a flag lying at the door. His to say
   if a run for a flag left lying should start when its taker sets off.
5. The early September matches (R-673, with the counts): raise when energy is built, at R-398 and before a pull.
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
