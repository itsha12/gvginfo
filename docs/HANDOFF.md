# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. Read `CLAUDE.md`, `docs/SPEC.md`, this, then `docs/REDESIGN.md` (the plan)
and `docs/DEFINITIONS.md`. History: `docs/CHANGELOG.md`; rulings: `docs/RULINGS.md`; models: `knowledge/model.md`.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read CLAUDE.md, docs/SPEC.md and docs/HANDOFF.md, check
> out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-24: the engine on the new trim begun; his thoughts on energy, R-665 to R-667)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stages D and E) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored, each with its file beside it; 564 count (R-477); 506 matches
  trained. No workflow run in progress. Rulings run to R-667. The baseline (R-491): `baseline-2026-11-15`.
- Graded and filed (set f1): thirteen games. No family: numbers from kills (R-557), the push (R-597), a held team
  (R-621). No more matches until the engine is ready (R-570). No flag card and no Lord row waits for his marks.
- Built on the branch this session (stage E, step 2; CLAUDE.md "The engine on the new trim"):
  - the reader: `extras.py`, `Match.extras()`; a match with no file stops the reading (R-460);
  - flag returns from gvg.report's flag objects (R-481): `Moments.flag_backs`, `flag_lives` rebuilt on it. The
    inference had read a return that never happened about one time in seven, and real ones a median 6 s late. The
    flag tally (R-408) moves with it on about one position in seven, often by a whole flag (a returned flag had
    counted as lying on the ground until the next pickup);
  - R-505 read on true flag lives (`Moments.not_run_first`), which three Classic rows needed;
  - the Lord record (R-632 to R-635): every Lord damage figure gvg.report's, aggressiveness and gvg.report's Lord
    health on every position, the aggressiveness lead a seventh price;
  - `tools/golden/compare.py` (two runs' plays compared); a full run replaces its workers (memory).
- Checkpoint (every counted match, branch at 9022ffe): 564 matches, 33,094 plays, no errors; fifteen truths hold;
  323 Classic rows pass, none fail; self-check 6 in 4. One Visible row moved (Open, 2).

## Next (in order): the engine substantially finished before the merge and training (R-571, R-572)
1. Stage E, step 2 goes on, the order he was given on 2026-11-24: degen in every damage figure (R-638, R-649,
   R-655; gvg.report's own on players, NPCs and Lords, R-661), then interrupt attempts (R-639), what each prot did
   and the death and spike-save recaps (R-636), who stripped which enchantment from our own replays (R-637), a
   hold told with what the holders went for (R-658: the held team's healing is a reaction, never a call or a fix).
   Each piece: the development set, the key, `compare.py` against the run before; a full run at the end.
2. On the new prices and the new flag tally, before anything is read from them: `cases.py ladder`, then `cases.py
   test` (R-545), and the flag readings he has seen shown to him again (R-635). Not run this session.
3. Energy, when he says his thoughts are final (R-664 to R-667). Then the close: the new families beside the old
   kinds for one rebuild (R-323), the stand-in prices replaced by the win model, the replaced kinds retired, the
   causal map cleaned, SPEC and METHODS rewritten, the readability test, his list of R-398, the merge, then one
   Train batch on the same 506 matches (he starts it).
4. With matches in: the split family again; the danger zone's two factors; the opening hand-off and held flags.

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand, with R-553 to build, and for a double run from the
   sender's side: raise them when more matches are trained. The execution list (R-557).
1. Energy (R-665 to R-667): put to him on 2026-11-24 with a first look at the data (a monk's energy set to the
   double high scale, the energy shown plus 72 less the maximum of the set he holds; a death follows 8% of the
   moments a team's monks average 65 or more there and 41% at 25 to 35). His to answer: is that scale right (does
   every monk carry a double high set); low as a line read from the data or his 15 in single high; who counts as
   midline for energy; monk casting efficiency measured against what (the same monk role in every match, as
   forensics does, or something he names). The 19 counted matches with no energy record: blank (Claude's
   recommendation, unanswered).
2. 옷옷옷옷 v RACK 6:15 (Visible, "single run half run to stand mes"): now told at 6:27, when the Prot takes the flag
   up from where it lay at his door, not at 6:15 when he set off for it. One row, not built from (R-495); a flag
   lying on the field is told from its take-up everywhere. Say if the run should start when its taker sets off.
3. Once degen counts: the danger zone's 250 again (R-649), and the NPC damage table read again (R-659).
4. R-576's reading and R-575 on Nomad's are Claude's: bring him what either tells wrongly. Tolkano: no build (his
   word): date, guilds, hall and length with every example.

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
