# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-23, night: his marks on the Lord push rows and the flag cards filed; the end record's Classic fault fixed)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stage D) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored; 564 count (R-477); 506 matches trained. No workflow run in
  progress. Rulings run to R-649 (new: degen in every damage figure). The baseline (R-491): `baseline-2026-11-15`.
- Graded and filed (set f1): thirteen games. No family: numbers from kills (R-557), the push (R-597), a held team (R-621). No more matches until the engine is ready (R-570).
- His marks of 2026-11-23, filed. The eight draft rows of the play for 28:00 (p4-9 to p4-16): seven Classic (six
  correct; hold v Dz incorrect, numbers: "hold sends 3 but they die before reaching base") and one Visible; all
  eight consistent with the 25:00 line, which he has not set. The eleven flag cards: all told correctly, all agreed
  with; his own calls wait 5, send 4, hold 2. No card corrected.
- Built this chat, on the branch; no play moved (the development set's plays identical; 33,371 plays over every match):
  - `Moments.end_play`: a player who dies on his way into their base was sent (`_end_way`: on the enemy's ground at
    their door, base or pit, past the last turn-off to mid, for JOIN_S or having stood in the base). hold v Dz reads
    3 against 4. Over 86 late matches 10 change a count, none its kind; five go from one team sending to both.
  - The end record is kept beside the plays (`flag_cost[rid].end_play`); a check in the key may read a record
    (`"record": "end_play"`); the eleven p4 games not in the development set were added (82 games).
  - Execution said on a row in words: `cases.exec_sentence`, `cases.py execution-say <plays file> <report id>`
    (what stands out among plays of the same kind, both teams apart, no verdict). On no page yet.
- Last checkpoint (every counted match, this engine): 564 matches, 33,371 plays, no errors; fifteen truths hold;
  323 Classic rows pass (the seven Classic draft rows now scored), none fail; self-check 6 in 4. Open: p4-13.

## Next (in order): the engine substantially finished before the merge and training (R-571, R-572)
1. The play for 28:00, with his word on Open 1: `jobs.lord_plays` read from `Moments.end_play` in place of the hits
   on a Lord: one row a match for the play, saying whom each team sends and keeps and what each send played for
   (the kill, Lord damage, killing the defenders); a push before it as a Lord line on its pinned row (all 25 have one).
2. What is left of the measurements: his answers to Open 3 to 5; the execution sentence put on a page; the split's
   NPC damage in the like spots of a split; the old execution inputs the new record lacks (casts into a ready
   interrupt, attacks while Blind, damage off shield sets).
3. Stage E (REDESIGN.md): the new families beside the old kinds for one rebuild (R-323), the stand-in prices
   replaced by the win model, the replaced kinds retired, the causal map cleaned, SPEC and METHODS rewritten, the
   readability test, his list of R-398, the merge, then one Train batch on the same 506 matches (he starts it).
   Before it, a new trim keeps gvg.report's flag objects (R-481), Lord damage record (R-632) and prot, degen,
   interrupt and death items (R-636 to R-639); who stripped which enchantment is read from our replays (R-637);
   every damage figure then takes degen in (R-649: probe first whether gvg.report records degen on NPCs and Lords).
4. With matches in: the split family again; the danger zone's two factors; the opening hand-off and held flags.

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand, with R-553 to build, and for a double run from the
   sender's side: raise them when more matches are trained. The execution list (R-557).
1. His word for the Lord play (asked 2026-11-23): hold v RACK 24:48, Crew v cope 24:44 and Team v hook 24:02
   (Classic) become Lord lines on their pinned rows; Men v Crew 27:03 and 27:20 become one play set at 27:11; 27
   early Lord visits stop being told; the 25:00 line.
2. ohno v Book 25:04 (asked): the row told him Book sent nobody; three of Book's players stood in ohno's base until
   10 s before their Lord died. Should the record read a team's send at the end, or while the play was on?
   Told him: Dz's three pit NPCs at 21:52 in Dz v Crew were its three pit archers, not two knights and an archer.
3. The hold (put to him 2026-11-23): is healing the NPCs or the players a choice of the held team, or does it
   follow what the holders hit? Should a hold be told with what the holders went for (NPCs or players)?
4. One or two players sent from a level standing read worse than no split: is a lone player leaving always a
   split to him? Picked rows on the site were offered. 5. The NPC damage table: anything against what he knows.
6. R-649, Claude's reading to confirm: amounts take degen in, who is in which fight stays on hits and casts; the danger zone's 250 again once degen counts.
   R-576's reading and R-575 on Nomad's are Claude's: bring him what either tells wrongly. Tolkano: no build (his word): give him date, guilds, hall and length with every example.

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
