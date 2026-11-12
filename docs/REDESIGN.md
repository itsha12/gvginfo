# Decision engine redesign: plan

A plan, not the current state: `docs/SPEC.md` still describes the engine as built. This file is replaced as steps land
and removed once SPEC.md describes the new structure. Its rulings are R-292 to R-309 in `docs/RULINGS.md`.

Status (2026-11-11): step 1 built. Step 2 under way on the branch `bundle-4`: the map foundation is built, and a reading
stage was added before the decision moments (the records, the story and the line-up; see "Step 2: where it stands" and
"Build plan from here"). Steps 3 and 4 not started.

## Why
The two scored blind rounds showed the decision tier cannot say whether a call was right, whether it was executed, or
what it led to: the model's call equalled the usual play in 11 of 16 picks; 8 of 16 picks moved win chance by under
1 point; 9 of Denning's 16 calls were priced on fewer than 5 similar cases (3 on none); options were 5 second movement
labels ("pushed, fell back"), up to 16 a pick.

## Agreed with Denning
- A choice is read over 20 to 30 s; outcomes at 90 s and about 3 minutes, hard results beside win points.
- At most five options a pick, in a player's words, plus "Other".
- Blind picks are chosen for leverage, are mostly moments where the model differs from the usual play, and are scored
  cumulatively with a range.
- A call gets one of three verdicts: right, wrong, no clear difference. Execution is read before the result, and the
  enemy's execution is scored too.
- The decision card replaces the TQs. Round 3 is void.

## The structure: six layers
The first four are the decision (macro); the last two are execution (micro), scored for both teams.

| Layer | Question | Example |
|---|---|---|
| Family | Which decision is this? | Answer to a split |
| Scenario | Which version of it? | A three-player split enters the base, mains even at the stand |
| Call | What did the team choose? | Mirror with three |
| Shape of the call | Who went, when, which way? | Two damage and a monk, 12 s after the split left, by the front door |
| Objective | What was the play for, and was it played for that? | Hold the pit NPCs until the base res |
| Mechanics | How well was it carried out? | Interrupts, strips, kiting, damage against the usual |

### Families
| Family | Trigger | Scenario set by | Calls | Replaces |
|---|---|---|---|---|
| 1 Flag decision | an enemy player leaves main, the res shrine or the base to run; a boost is coming; own flag in hand | where both mains are, flag lead, enemy backup in hand, own flag in hand, seconds to boost, who holds on each side | runners (none, one, two: R-305) with where the rest go: stay at the stand, fall to footmen, retreat to the pit, push their flagger, push the flag through as a team | enemy_pickup, boost_clock, eight_v_eight_or_flag, runner_choice |
| 2 Answer to a split | an enemy group leaves main and turns out to be a split | split size and make-up, defenders home, flag state, numbers at main | no answer, one defender, mirror, two monks, add one, full collapse | split_in_base, who_defends |
| 3 Numbers advantage | numbers differ where the mains meet | source (runner away, split elsewhere, kills, wipe), how long it should last, res timer | up: stay and kill, push their flagger, run again for a backup, push the pit for NPCs, chase DP, take the flag and reset. Down: fight on, fall to footmen, retreat to the pit, trade with a split | power_play, after_wipe, npcs_or_dp |
| 4 Game plan | a slow clock, read when the state shifts | morale, NPCs, Lord damage, clock, fights so far, match-up, map | fight at main, split game (solo, two, three, 4v4), turtle, play for 28, push for the Lord | split_or_stay, play_for_28_or_lord, late_game |
| 5 Engage or wait | a stand-off: mains apart, no damage traded, incl. the opening | who gains from what is ticking, builds, positions and NPC cover, map | advance to fight, take the flag first, hold position, split first | new |

Families 1 to 3 are step 2; 4 and 5 are step 4 (the old kinds they replace keep running until then).
offence_or_defence becomes part of the objective layer of a fight.

### Shape, objective, mechanics, map
- **Composition** (who): compared on properties (healing, NPC damage, speed and escapes, snares, self-defence), not
  class names. Always a decision. **Route** (which way): a named route from the labelled map, compared on route
  properties (length, passes footmen or archers, chokes, teleporters). Always a decision. **Timing** (when): a delay is
  a decision when something was being gained elsewhere (a live numbers advantage at main), execution otherwise; the
  card shows what the delay gained and cost either way. Intent is not in a replay: the timing rule is a proxy.
- **Objective**: each call in each scenario has a job with a success test read across the whole map (three players
  splitting into four defenders succeed by surviving and holding them while main plays 5v4; NPCs are not required).
  Playing for the wrong job is an execution fault of kind "objective", apart from mechanics. This builds the causal
  map's `A.jobs` node. The job table is a definition (Claude drafts, Denning rules); each job is then tested on
  held-out matches.
- **Mechanics**: the existing execution nodes and forensics, read before the result, for both teams.
- **Map**: moments are compared across halls, weighted by map features, never restricted to one hall; a single-hall
  reading is shown when the hall has enough cases. Labelled maps add entrances, door path lengths, the collapse path,
  NPC cover and teleporters to today's three numbers.
- **Hall features** (R-310 to R-314; `data/maps/hall_features.json`, `knowledge/guild-halls.md`): a hall can add
  options to a scenario or a scenario of its own. Flag route choice (Druid's Isle, Isle of Jade, Imperial Isle) is the
  route of a family 1 call, read from which labelled flag run the carrier followed. Object control (vine seed, gate
  lock and levers, repair kit and trebuchet, health shrine, flame sentinels) is a family 4 decision with its own state
  (seed capped, gate open, kit position, shrine holder, sentinels alive), read from positions since the replays carry
  no object events. The fall-back zones of a retreat are footmen, front door, pit, or front door and pit alone on the
  five halls without footmen (R-311). Environment areas (healing water, coral, acid, quicksand, tar, ice, lava, spores,
  miasma) are execution inputs: time spent in them, by role.
- Path distance must treat a teleporter as a hop of no length (R-316): a route drawn through one shows the full drawn
  distance (Isle of Jade's coral flag runs: 11,500 to 12,000 drawn, 6,700 to 7,300 walked; its back doors and Nomad's
  Isle's too). One-way and two-way teleporters are edges of no length in the walk graph; a labelled route's length is
  its walked length (`tools/maps/audit_labels.py` `walked`, the rule to carry into the engine). Today's three map
  numbers are straight lines and know no teleporters; this is fixed with the step 2 rebuild, not before.

## The decision card
One format for the blind test, match review and query tool:
1. Situation (family, scenario, positions by named zone, flags and holders, stand and boost, morale, NPCs, Lord damage,
   builds, map, replay link). 2. Options (at most five; the blind test stops here and asks). 3. What the team did (call
   and shape). 4. What followed (the consequence record at 90 s and about 3 min for the whole map, then win points with
   their range). 5. Verdict on the call, with evidence as rates; the shape is judged where the call was right.
6. Own execution: objective, then mechanics against the role benchmark and as a percentile among teams that made the
   same call. 7. Enemy execution, scored the same way. 8. Cases behind each number, with links to two or three.

Verdict rules: right or wrong is judged against the best alternative with enough cases in the same scenario, never by
this match's result; "no clear difference" when the range includes zero or cases are too few; execution is read before
the result; whether the job was achieved is a result, not an input; enemy execution is scored and never offered as a
fix; no number without its cases.

## Steps
| Step | Rebuild | Delivers | Gate |
|---|---|---|---|
| 1 (done) | none | round 3 void, rounds paused, blind page fixes, the map page | Denning labels the most played halls |
| 2 | one (bundle 4) | zones and path distance, the reading (records and story), families 1 to 3, calls read as allocations, the consequence record | the reading gate (R-380, R-383, R-396); the decision gate (R-394); advice test no worse |
| 3 | none | the decision card in the blind test, match review and query tool; TQs retired | readability test; Denning approves mock picks |
| 4 | one (bundle 5) | families 4 and 5, win model stability, speed | as step 2 |

### Step 2 items (build order)
2.1 named zones from labelled areas (all 14 halls are labelled); 2.2 path distance along the walkable outline, with
teleporters as hops of no length (R-316), replacing the three straight-line map numbers;
2.3 departures (every leave from a main group, the res shrine or the base, labelled afterwards as run, split, collapse, retreat
or return); 2.4 event triggers instead of polls, one record a moment; 2.5 scenario from the state at the trigger;
2.6 the call as an allocation over 20 to 30 s (runners, where the rest are, defenders and their mix; never from damage
or deaths); 2.7 "forced" reads (a death in the read window) kept apart; 2.8 shape (composition properties, timing with
the gain-elsewhere test, route); 2.9 the consequence record, both theatres, 90 s and about 3 min; 2.10 similar cases =
same scenario first, then nearest on continuous variables, with a count that depends on the scenario's size; 2.11 jobs
and success tests; 2.12 enemy execution against the same role benchmarks; 2.13 an interaction pair must pass twice
before entering the win model; 2.14 retire replaced kinds, clean the causal map (202 hypothesis links and 12 duplicate
pairs today), rewrite SPEC.md.

Items 2.3 to 2.7 were drafted before the records existed and are rebuilt on them (R-351, R-362): a trigger is any
change the enemy makes to the map that the records hold, not only a leave or a numbers difference.

Adoption: kept only if the reading gate and the decision gate pass (see "Tests"), the held-out advice test is no worse
than before (6 of 13 kinds clear at 506 matches), and the readability test passes.

### Step 3
`card.py` (report layer) builds the card. Blind test: five picks a round, at least three where the model differs from
the usual play, win chance 25 to 75% before the moment, two or more options with enough cases; reveal = the full card;
scored cumulatively, on matches that played no part in choosing the picks; no verdict before roughly 50 to 100
disagreement picks; each reason filed as a candidate variable or ruling request. The TQ section leaves the report;
forensics stay as the mechanics evidence.

### Step 2: where it stands (branch `bundle-4`, R-322)
| Stage | Items | State |
|---|---|---|
| A Map foundation | 2.1, 2.2 | built: `hallmap.py` (zones R-306, walked distance R-316, footmen reach R-320); `state.zone` and the three map numbers read it |
| R The reading (added; R-341, R-362) | the records, the story, the line-up | reading step 1 built and its 17 thresholds confirmed (R-390): `moments.py` keeps split attempts and main team pushes, split fights, joins, leaves and swaps, ground moves, the flag record, who is on the pit NPCs, undefended splits; `story.py` prints from them. Reading step 2 (the words of R-373, R-375 to R-378) is next |
| B Decision moments | 2.3 to 2.7 | drafted before the records (departures, triggers, scenarios, calls, forced; 23,041 moments in 506 matches); to be rebuilt on the records |
| C The decision gate | test | not started: R-394 (the 15 golden moments from his notes; the calls on comms) |
| D Depth | 2.8 to 2.13 | not started (shape, consequence record, similar cases, jobs, enemy execution, interaction rule, the four proposals left of R-324: the Shadow Step flag drop is out, R-393) |
| E Close | 2.14 | not started (side by side for one rebuild R-323, retire, causal map, SPEC and METHODS, readability, the list of R-398, merge, rebuild on the same matches) |

Scenarios as first drafted (the key the cases are grouped by; the rest of the state rides along for similar cases):
family 1 = what set it off (an enemy player leaves to run, the enemy's boost is 30 s away, an own player picks up a
fresh flag) x who holds the stand (7 in use, 39 to 2,630 cases); family 2 = split size (1, 2, 3, 4+) x who is home
(nobody, a defender, the main group) (12, 25 to 787 cases); family 3 = up or down x why the short side is short
(kills, a runner away, players split elsewhere, a wipe) (8, 33 to 2,562 cases).

What that draft showed: the family 1 call list has no option for a main group fighting in the field (39% of flag
decisions: backside 14%, push side 14%, enemy base 9%), and the family 2 list none for three or more defenders against
a solo split or other uneven counts (27%). The rebuild on the records takes its words from his notes and commentary.

### Build plan from here
1. **Reading step 2: the words** (R-373, R-375 to R-378), into the records in his order: pushing the flagger (its own
   record, R-371); flag route and flag lead (a full flag and half a flag up, R-375); the pre-game flag; then posture
   (R-376; a record now, family 5 itself stays in step 4), the four timing choices (R-377), monk counts in a fight and
   who is on the Guild Lord (R-378).
2. **Reading step 3: the check.** Regenerate the golden stories; Claude compares them with the 13 blind notes; rescore
   the line-up; Denning reviews the held-out misses once, at the gate (R-396).
3. **Denning approves the story's form** on golden game 1 (R-395).
4. **Stage B rebuilt on the records**: triggers, scenarios and calls for families 1 to 3.
5. **Stage C: the decision gate** (R-394).
6. **Stage D: depth**: shape (composition, route, timing), the consequence record at 90 s and about 3 min, similar
   cases, the job table (Claude drafts, Denning rules), enemy execution, the interaction rule.
7. **Stage E: close**: old and new decision kinds side by side, SPEC.md and METHODS.md rewritten, the readability
   test, the list below, the merge, then one rebuild.
8. Training chunks and Discovery resume; then step 3 (the decision card, the blind test, the sealed judgement lines as
   the test of verdicts) and step 4 (families 4 and 5).

### Before the next training run (R-398)
After the engine is built and before the rebuild, Claude goes through this with Denning:
1. Check that this file and SPEC.md are accurate or need updating.
2. Review the rulings: condense what can be, move "rules" that belong elsewhere, drop those no longer needed, add or
   amend.
3. Review the repository for old, outdated or unneeded files.
4. Remove the Templates tab from the site (not used).
5. Remove the Meta tab from the site (not used).
6. See whether the skills need updating from the wiki.
7. See whether the model pages (structure, results and the rest) need amending to match the approach taken.
8. Any other outstanding items, questions or rulings he has not addressed.

### The story so far (R-341; from Denning's notes on 14 golden moments)
His notes tell a match as a chain, and the engine is being rebuilt to read it the same way. What the notes use:
- **The map at any second** is a set of fights, each with its place, its numbers and who is in it: the main fight,
  a split fight, a solo split and its defender, a flag run being pushed, two groups posturing without engaging.
  Numbers are per fight ("2v3 back door, but main 5v4"); a player who casts a few skills from between two fights is
  support, not a player more.
- **Places, a ladder a fight moves along**: greater stand area, footies (front and back), front door, base, pit; a
  fight moving down a team's ladder is that team under pressure. **Routes**: through mid, through the pit, front
  door, back door, the portal, the short and the long flag way; route length decides who arrives first.
- **Flag verbs**: run, wait back for the second flag, hand off (to cap, to hold), cap first when a player down,
  overcap, match, double run (half, full), hold, push the flagger, support the runner, time taken to cap once at
  the fight.
- **Split verbs**: split (who, which door), defend (who; 1v1, 2v3), collapse, match or mirror (instantly, on time,
  late), swap who is in it, fall out or pull out, threaten, abandon, rejoin; undefended and taking NPCs. A split can
  be the build's plan from 0:00 (4-4), not a leave from main.
- **Main verbs**: fight N v N at a place, take deaths, retreat down the ladder, push in, fall out, full collapse.
- **Clocks and stocks**: the base res ("time": a kill before it, a death right after it), death penalty and boosts,
  NPCs (he often cannot see them; the engine can), builds (4-4 split build, spike, Lyssa dervish, WoC).
- Some movement has no purpose he can name ("not sure what this play is"); the engine may say so too.
Decisions are then the points where a team chose one of these verbs in a given map state; the three families remain as
groupings, but a trigger is any change the enemy makes to the map, not only a leave or a numbers difference.
Built on the branch as records (R-362: the record is the work, the story only prints it): the flag's lives and the
flag record, every fight with its place and numbers, split attempts and main team pushes, the split fight kept as one
record (R-365), joins, leaves and swaps, ground moves, who is on the pit NPCs, undefended splits. Not yet in the
records: pushing the flagger, flag route and flag lead, posture, the timing choices, monk counts (reading step 2).

## Tests
- **The reading gate: the line-up** (R-368 to R-397). Denning's timestamped commentary on 7 games and Maga's comms on
  9, filed as paraphrased statements (`data/lineup/`; 16 transcripts, 1,121 statements) and checked against the story
  by `tools/golden/lineup.py`. Twelve transcripts are for building; four are held out (`data/lineup/held/`, R-370,
  R-397) and never read line by line before the gate. The gate is 90% agreement on things seen happening in the
  held-out games (R-380, R-383). He reviews their misses once; after that review only the engine's own misses count,
  and if it still fails they are fixed, the four games become building games and two new timestamped games are needed
  (R-396). At 2026-11-11: building 365 of 365, held-out 136 of 162 (84%), not yet reviewed.
- **The blind check**: the 13 notes Denning wrote before seeing any engine story; Claude compares each rewritten
  story with them (R-354). He marks the story of game 1 only, for its form (R-395).
- **The decision gate** (R-394, replacing how R-327 is scored): on the 15 golden moments (R-382), the scenario and
  the call read from his notes, not the drop-downs (R-341): the moment found in 9 of 10, each part of the scenario
  and the call in 8 of 10. And on the comms: where a team says what it means to do, the engine finds a decision there
  and reads the same call (228 such calls filed; the pass rate is set when first measured).
- **Verdicts**: his sealed judgement lines (R-372; 65 filed) test the decision card's verdicts in step 3. Never fed
  in as rules.
- Held-out advice test; readability test (also the blind page and the card); mock picks; the cumulative blind test.

## Rulings
Confirmed by Denning on 2026-11-09 and appended to `docs/RULINGS.md` as R-292 to R-305 (R-296 widened to a player
leaving base; R-304 offence or defence in the objective layer; R-305 the double run). His answers to the open
questions: the timing rule is right (R-297); a blind pick says what a leave became, because players can usually tell
(R-296); the down side of a numbers advantage is its own decision (R-301). Later rulings that changed this plan:
R-341 (think as his notes do), R-354 and R-395 (the golden test), R-362 (the record is the work), R-368 to R-389 (the
line-up), R-390 to R-393 (thresholds, own footies, a split whose main team is dead), R-394 to R-398 (the gates, the
held-out folder, the list before the next training run).

## Definitions
Ruled 2026-11-10: at a place = more than half of the group's living players inside the labelled area (R-319); fell to
footmen from the Footman labels and the measured reach (R-320); something gained elsewhere = a live numbers advantage
at main, NPC damage in progress or a boost about to land (R-321); a departure's purpose is fixed 60 s after the
leave, or earlier on a pickup or on entering the enemy base (R-325). Still needed: the job table (Claude drafts in
stage D). For step 4: a stand-off, a turtle. The thresholds are in `common.py` on the branch; those of the reading are
confirmed (R-390).

### Reading the flag (R-305, R-339, R-340)
A team has one flag. Its life runs from the pickup at the spawn to the capture or to its return to the spawn (not
recorded; read from the next pickup being at the spawn). A pickup dropped within about 5 s without a capture is not a
carry. Each life is labelled afterwards by what the players went on to do: single run; hand-off to cap; hand-off to
hold; double run with each player half running; double run with each player full running (R-340's four forms). Drafted
as `Moments.flag_lives` on the branch (`python3 moments.py flags`): of 5,977 lives in 506 matches, single run 36%,
returned 19%, hand-off to cap 15%, double run full 14%, double run half 7%, open at the end 9%. Not yet read: the
hand-off to hold. A capture gvg.report recorded with no pickup is given its pickup (69 of 5,245 captures); a return
the observer missed is read from the flag being back at the spawn (R-389).

## What the labelled halls show (all 14 labelled; the first three in detail)
- The labels read cleanly: equal rosters on both sides, flag runs that start at the replay-derived spawn and end at
  the stand, routes wholly on walkable ground. Sides are assigned by the nearer Guild Lord.
- Areas overlap by design (a pit and its choke points sit inside the base hull): the zone of a point is the smallest
  labelled area containing it, cut to the walkable ground (R-306).
- "Fell to footmen" is not an area on the map: it is the team standing where its footmen are engaged in the fight
  (R-307). Read it from the footmen themselves: the team's fight is within reach of its living footmen (they deal or
  take damage, or the main group is close enough that they would).
- Isle of Meditation has two stands. All 279 recorded captures in 40 replays are at the tower stand (morale); none at
  the obelisk, so obelisk control and the fireballs it turns on are not in the replay data; it is almost never used
  (R-308), so it is not modelled. The gate nearest neither
  base opens from outside; the two nearest the bases open from the lever inside; the paths to the outer gate carry
  Miasma (5 pips of degeneration, not removable, spreads to adjacent players).
- Isle of Solitude has a one-way teleporter in each base near the Guild Lord, out to the main field: a split's escape
  route and a path that bypasses both doors. Direction confirmed (R-309): in beside the Lord, out on the field.
- Route direction: front and back doors are drawn from inside the base outward; flag runs from the spawn to the stand.
- All 14 halls are labelled (43 to 60 labels each). `tools/maps/audit_labels.py` checks them against R-310 (pit
  roster, one res shrine and flag spawn a side, equal NPCs, mirror partners, doubles); step 2 starts only when it reads
  clean. Isle of Solitude's two flag spawns and Isle of Weeping Stone's outer archer are settled (R-318).

## Risks
Thin cells at 506 matches (many cards will read "no clear difference"); intent is not recorded; hindsight labels suit
analysis but not the blind test's question; longer reads risk recording the fight's result (positions and commitments
only, forced reads apart, the pre-trend check stays); the win model prices every decision (hard results do not depend on
it); stronger teams choose differently (strength stays in the adjustment); the replays lack energy and line of sight.
Added 2026-11-11: the line-up checks that what was said is in the story, not that the story is free of extra lines, so
a change that adds lines can look like a gain (count the records over all matches beside every score:
`tools/golden/thresholds.py`); the held-out set is four games, and once reviewed it is spent; the decision gate's
golden part rests on 15 moments, so the comms calls carry most of its weight; main's engine is frozen at 506 of 606
matches until the bundle lands.
