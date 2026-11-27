# GvG Info: handoff for a new chat

Rewritten each session; under 80 lines. `CLAUDE.md` is loaded already: read this, then only the section of
`docs/ENGINE_NOTES.md` named beside the item you take up. The plan is `docs/REDESIGN.md`, the definitions
`docs/DEFINITIONS.md`, the rulings `docs/RULINGS.md` (search it), the history `docs/CHANGELOG.md`. For execution work
read `docs/EXECUTION.md` first: the catalogue of every why, its rules, and the order of work.

## Start a new chat in one message
> Attach my repo itsha12/gvginfo with push access, clone it, read docs/HANDOFF.md (CLAUDE.md is loaded automatically),
> check out `bundle-4` in a second worktree, then carry on with "Next".
> (If the clone leaves `bundle-4` untracked: `git remote set-branches --add origin bundle-4`, then fetch it.)

## State (2026-11-27, morning: rulings to R-766; execution stages X1 to X4 built; the catalogue at stage 1 of 5)
- Main's engine is unchanged (SPEC.md). Bundle 4 (redesign step 2, stages D and E) is on `bundle-4` and lands in one
  piece, then one rebuild (R-322). 658 replays stored, each with its file beside it; 564 count (R-477); 506 matches
  trained. No workflow run in progress. The baseline (R-491): `baseline-2026-11-15`. Thirteen games graded and filed
  (set f1); no more matches until the engine is ready (R-570).
- Execution (the micro answer) is the block of work (R-701 to R-766). The catalogue, `docs/EXECUTION.md`, is the brief:
  a death is a sum, every why is one part of it; 34 rules (rule n is R-(715+n) up to 28), the whys in sections A to D,
  the skill tags, the skills worth interrupting, the limits of the data, five stages. It is built before he checks
  anything: his marks on the Execution view (stage X5; 46 deaths set out on the site) wait (R-752).
- Stages X1 to X4 and the catalogue's stage 1, first piece, as before (ENGINE_NOTES section 44; `bundle-4` 45ad7cf).
- Stage 2 is done but for the wiki sync (R-765): `data/model/skill_tags.json` on `bundle-4` (37f10b4, made in another
  chat, reviewed by him): 577 skills, each with its parts of the sum, trigger, area, cast time, interrupt reach,
  speed-boost mark and read / context only / ignore. His twelve rulings from the review are R-753 to R-764.
- The file was checked on 2026-11-27 (ENGINE_NOTES section 44, last item): ids, names, cast times, scope and
  vocabulary hold, and the path stands. To correct in it: Twisting Fangs lacks "cuts healing"; four `engine_note`
  lines to be reworded. Wanted before stage 3 reads it: who each skill lands on (foe, ally, self); a mark for a skill
  that raises the damage its user takes; R-738's snares marked as not checked; the seven skills the catalogue names
  and the file lacks. Nothing was built and no run was made this session; nothing was pushed to `bundle-4`.
- Last run: the development set only, at 45ad7cf: 6,935 plays identical to d7aacfe, 323 Classic rows pass. Last full
  run: 7d1f0ab (33,089 plays). Stale since: `attempts_cases.json`, `execution_cases.json`, `execution_rows.json` on
  main (the Execution view shows the reading before stage 1). The `cache` branch was not pulled or pushed.

## Next (in order, R-766): the catalogue, `docs/EXECUTION.md` "Order of work" (ENGINE_NOTES section 44)
0. First on `bundle-4`: the two corrections to the tag file, as he answers "Open" 1. Then, in the tag file (this chat
   or the other one, as he answers "Open" 2), the additions of the State item above.
1. Stage 1's remainder: failed spikes listed with the attack's misses, so the strip missed is told (a fault by his
   ruling, the check beside it: R-729, R-744, R-714); `into_ready` filtered by R-743 (interrupted casts of listed
   skills, backline). The development set and the key after each; no full run (R-766).
2. Stage 4: the ledger (each part of the sum an amount, R-734) and the pressure attempt (R-741, R-749); the even
   8v8's row (R-731).
3. Stage 3, with the tag file: Bull's knockdown, Harrier's Cripple, balling, Empathy and the other triggers,
   damage-raising stances, a spike into a block, ward or spirit, Deep Wound on the spike, an attacker on another
   target, the removals of R-725 and R-726. Damage rows carry no skill: each join to a cast is checked first (R-707).
   The reach of an interrupt comes from the tags (it catches Disrupting Chop); an untagged skill is counted and listed.
4. The one full run for stages 1 to 4 (R-766), with the machine to itself: `cases.py attempts` and `cases.py
   execution` (do the prot, the heal and the interrupt still pass on unseen matches; each new kind checked once), the
   key, the truths, `execution_rows.json` again.
5. Stage 5: readings from positions (too deep, monk following, Flail lock, snared frontline, area damage, should have
   kited), then its own full run. Then X4's sentences on the full list, and stage X5: his marks.
6. After execution: the flag readings shown again (sections 15 and 22), then the close (sections 37, 38, 34, 35, 41):
   the new families beside the old kinds for one rebuild (R-323), stand-in prices replaced, replaced kinds retired
   (`ask.py` and `learning.py` still import `tq.py`), SPEC and METHODS rewritten, the readability test, his list of
   R-398 (left: items 1, 2, 3's remainder, 6, 7, 8 and 10), the merge, one Train batch on the same 506 (he starts it).

## Open for Denning
0. Held at his word (R-554): the cards for a flag in hand (R-553 to build) and a double run from the sender's side.
1. Put to him 2026-11-27: whether the tag file's commit on `bundle-4` is made again in place or corrected by a new one.
2. Put to him 2026-11-27: who adds to the tag file (this chat or the other); the skills to tag beyond the 577 (the
   seven the catalogue names; the 25 on 4 or more bars from 1 September, where the engine's matches start); whether
   Primal Rage and Healing Signet's armour penalty are read as Frenzy is (R-740).
3. R-766's reading of "after stage 4": the full run comes when stages 1, 4 and 3 are all built. His to correct.
4. R-746, Claude's reading of "kiting should be no fault", his to correct: crits while moving and the extra damage of
   Protector's Strike, Harrier's Haste and Weaken Knees are counted as context, never told as faults; and "should have
   kited" is not told against an attacker with Bull's Strike or Harrier's Grasp ready (where moving is the fault).
5. R-747 as built takes little: on the development set a monk had a spike on himself (400 inside 3 s, from its first
   hit) at 5 deaths. Is a monk under lighter pressure himself (R-711's 250 in 2 s) also not available to another?
6. The speed-boost mark covers 30 skills: the 15 he ruled on and 15 found by the same rule (all 30 say "faster" in
   their text; none was missed). His to confirm or trim.
7. Skills from the wiki (R-398 item 6): the sync's missing cast times fixed later (R-765); then he runs the site's
   "Update skills from the wiki" button and the next session reads `data/wiki_changes.json`.
8. The early September matches (R-673): raise it at R-398 and before a pull. R-576 and R-575 on Nomad's are
   Claude's readings: bring him what either tells wrongly.

## Running it
- Local engine: `git fetch --depth 1 --no-filter origin +replays:refs/remotes/origin/replays` (the files beside the
  replays come with it; about 150 MB). `jobs.py`, `moments.py`, `casting.py`, the gate, the line-up and
  `confidence.py` need only Python; `cases.py` needs numpy and scikit-learn (no cache for its reports). On 2 cores and
  7 GB: the development set about 6 minutes (`moments.py all <file> --dev`), a full run (`moments.py all`) about 27
  with the machine to itself, `cases.py execution` about 30 on its own, the other reports about 20 together (`ladder`
  before `test`, R-545; each kept with `--json data/model/<name>.json`). Set `PYTHONDONTWRITEBYTECODE=1`; never edit
  an engine file while a run is going (modules are imported late). After a change: `tools/golden/review.py score
  <file> --key <main>/data/model/review_key.json`, then `tools/golden/compare.py <before> <after>`.
- Site check: `python3 -m http.server`, then playwright with `/usr/bin/google-chrome`, api.github.com mocked.

## Cautions
- Never print or decode a sealed field in a chat. Don't merge `bundle-4` piecemeal (R-322). The branch's own
  `CLAUDE.md` and `docs/` are old copies: main's are kept up to date (its standing rules too).
- `data/model/interrupt_worth.json` (branch) and `docs/EXECUTION.md`'s lists are one list: change both. Another chat
  may push to `bundle-4` (the tag file only): fetch before every push there. `data/skills.json` is never edited by hand.
