# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. `CLAUDE.md` is loaded already: read this, then only the section of
`docs/ENGINE_NOTES.md` named beside the item you take up. The plan is `docs/REDESIGN.md`, the definitions
`docs/DEFINITIONS.md`, the rulings `docs/RULINGS.md` (search it), the history `docs/CHANGELOG.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read docs/HANDOFF.md (CLAUDE.md is loaded automatically),
> check out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-24, night: rulings to R-700; a backline monk told by his bar; casting efficiency built)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stages D and E) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored, each with its file beside it; 564 count (R-477); 506 matches
  trained. No workflow run in progress. The baseline (R-491): `baseline-2026-11-15`. Thirteen games graded and filed
  (set f1); no more matches until the engine is ready (R-570); nothing waits for his marks.
- Main, 2026-11-24: PR #6 (clean-up: R-398 items 3, 4, 5 and 9 done, REDESIGN.md's list marked) and PR #7 (CLAUDE.md
  slimmed; the engine's build notes are `docs/ENGINE_NOTES.md`, sections 1 to 43, and are recorded there from now on).
- On the branch at 318f689 (stage E, step 2): the reader, flag returns, the Lord record, degen as damage, and
  energy in his order, all four pieces (ENGINE_NOTES sections 8 and 43). Built this session: a backline monk told by
  his bar (R-698, section 42: `common.monk_kind`, his elite tells) and piece (4), monk casting efficiency
  (`casting.py`, section 43; report `data/model/casting_cases.json`; no play reads it).
- Last full run: 2bebbc6, 33,062 plays against 33,094 (1,935 changed in 196 matches, 44 gone, 12 new: the main
  fight's job to kill, R-457). Development set: 323 Classic rows pass. Every `cases.py` report rebuilt; the truths
  hold. Not rebuilt: `npcpower.py bench` (two of its kinds of bar moved with R-698: rebuild it before the next full
  run) and the forensics benchmark.

## Next (in order): the engine substantially finished before the merge and training (R-571, R-572)
1. Casting efficiency, once he answers (Open, 1): place by bar or by slot, and beside monks hit as hard; then into
   the execution measures and the death accounts. ENGINE_NOTES section 43 (energy: section 8; monks: section 42).
2. The rest of degen (R-649): the death accounts read gvg.report's recaps (R-636, R-638); `eventlayer.py`,
   `forensics.py`, `events.py`, `nodes.py`, `fights.py`, `scoreboard.py`, `phases.py`, `episodes.py` wherever damage
   is summed from hits; the story and the reports. ENGINE_NOTES section 8 ("Degen as damage") and section 26.
3. Interrupt attempts in the death accounts and `pressure.py` (R-639), what each prot did and the recaps (R-636),
   who stripped which enchantment (R-637): ENGINE_NOTES section 26 (the attempts and gvg.report's totals by skill
   are read by `casting.py` already: section 43). A hold told with what the holders went for (R-658): section 24.
   Each piece: the development set, the key, `compare.py` (section 9; two full plays files do not fit in memory
   together: compare them by a hash a play); a full run at the end, with `npcpower.py bench` and the truths.
4. The flag readings he has seen, shown again on the new prices and flag tally: ENGINE_NOTES sections 15 and 22.
5. The close (ENGINE_NOTES sections 37 and 38; documents 34, readability 35, the causal map 41): the new families
   beside the old kinds for one rebuild (R-323), the stand-in prices replaced by the win model, the replaced kinds
   retired, the causal map cleaned, SPEC and METHODS rewritten, the readability test, his list of R-398 (left on
   it: item 1, REDESIGN.md's status line is of 2026-11-13; item 2, the rulings; item 3's remainder, the old engine's
   data files; item 6, skills from the wiki; item 7, the Model and Mechanics pages that describe the old engine;
   items 8 and 10), the merge, then one Train batch on the same 506 matches (he starts it). With matches in: the
   split family again; the danger zone's two factors; the opening hand-off and held flags.

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand, with R-553 to build, and for a double run from the
   sender's side: raise them when more matches are trained. The execution list (R-557).
1. Put to him 2026-11-24, night, no answer yet (casting efficiency): (a) a monk's role, by slot or by what his bar
   is built on (recommended: his elite); (b) placed beside monks whose team was hit as hard (recommended: yes);
   (c) Aegis, Protective Spirit and Aura of Stability, credited with almost nothing by gvg.report: recommended,
   their energy out of the points and their casts shown apart as counts (a spike Aegis stops leaves no recap).
2. Skills from the wiki (R-398 item 6): he runs the site's "Update skills from the wiki" button between sessions;
   the next session reads `data/wiki_changes.json`.
3. The NPC damage table with degen (R-659) was shown to him 2026-11-24; no word on it yet.
4. 옷옷옷옷 v RACK 6:15 (Visible, one row, R-495): told at 6:27, the take-up of a flag lying at the door. His to say
   if a run for a flag left lying should start when its taker sets off.
5. The early September matches (R-673, with the counts): energy is built, so it is due: raise it at R-398 and
   before a pull. R-576 and R-575 on Nomad's are Claude's readings: bring him what either tells wrongly.
6. Proposed, no word yet: a rule in CLAUDE.md that a reading built on a gvg.report field is first checked against
   the raw record on a sample of matches (done for casting efficiency: `casting.py cover`).

## Running it
- Local engine: `git fetch --depth 1 --no-filter origin +replays:refs/remotes/origin/replays` (the files beside the
  replays come with it). `jobs.py`, `moments.py`, `casting.py`, the gate, the line-up and `confidence.py` need only
  Python; `cases.py` needs numpy and scikit-learn (no cache for its reports). On 2 cores and 7 GB: the development
  set about 6 minutes, a full run (`moments.py all`) about 30 with the machine to itself, the fourteen `cases.py`
  reports about 20 (`ladder` before `test`, R-545; each kept with `--json data/model/<name>.json`). Set
  `PYTHONDONTWRITEBYTECODE=1`; never edit an engine file while a run is going (modules are imported late). Train
  batch: its workflow (`blind` stays no). The key, `dev_set.json` and `game_reviews.json` are written on main.
- Site check: `python3 -m http.server`, then playwright with `/usr/bin/google-chrome`, api.github.com mocked.

## Cautions
- Never print or decode a sealed field (blind picks, golden moments) in a chat. Don't merge `bundle-4` piecemeal
  (R-322). The branch's own `CLAUDE.md` and `docs/` are old copies: main's are the ones kept up to date.
- The standing rules on the files the site saves, hall labels, party slots and transcripts are in `CLAUDE.md`.
