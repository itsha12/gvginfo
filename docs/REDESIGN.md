# Decision engine redesign: plan

A plan, not the current state: `docs/SPEC.md` still describes the engine as built. This file is replaced as steps land
and removed once SPEC.md describes the new structure. Its rulings are R-292 to R-309 in `docs/RULINGS.md`.

Status: step 1 built (2026-11-09). Step 2 under way on the branch `bundle-4` (stages A and B drafted 2026-11-10; see "Step 2: where it stands"). Steps 3 and 4 not started.

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
| 2 | one (bundle 4) | zones and path distance, families 1 to 3, calls read as allocations, the consequence record | golden moments agree; advice test no worse |
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

Adoption: kept only if golden moments agree at the agreed rate, the held-out advice test is no worse than before
(6 of 13 kinds clear at 506 matches), and the readability test passes.

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
| B Moments | 2.3 to 2.7 | drafted: `moments.py` (departures, triggers, scenarios, calls, forced); 23,041 moments in 506 matches |
| C Golden moments | test | page on main (Model > Golden moments), 30 moments picked; waits for Denning's labels, then `tools/golden/golden.py score` |
| D Depth | 2.8 to 2.13 | not started (shape, consequence record, similar cases, jobs, enemy execution, interaction rule, the five proposals R-324) |
| E Close | 2.14 | not started (side by side for one rebuild R-323, retire, causal map, SPEC and METHODS, readability, merge, rebuild on the same 506 matches) |

Scenarios as drafted (the key the cases are grouped by; the rest of the state rides along for similar cases):
family 1 = what set it off (an enemy player leaves to run, the enemy's boost is 30 s away, an own player picks up a
fresh flag) x who holds the stand (7 in use, 39 to 2,630 cases); family 2 = split size (1, 2, 3, 4+) x who is home
(nobody, a defender, the main group) (12, 25 to 787 cases); family 3 = up or down x why the short side is short
(kills, a runner away, players split elsewhere, a wipe) (8, 33 to 2,562 cases).

What the draft shows before any label: the family 1 call list has no option for a main group fighting in the field
(39% of flag decisions: backside 14%, push side 14%, enemy base 9%), and the family 2 list none for three or more
defenders against a solo split or other uneven counts (27%). Both wait for Denning's words from the golden moments.

## Tests
- **Golden moments** (new): about 20 to 30 moments (a match and a time) Denning labels by hand on a site page: which
  scenario, what the team did (call and shape), optionally what they should have done (stored sealed from the model).
  Claude picks them once the classifier's first draft exists, to cover every scenario of families 1 to 3 and the hard
  cases. The engine's labels must match before a rebuild is accepted; the set is re-run after every engine change.
- Held-out advice test; readability test (now also the blind page and the card); mock picks; the cumulative blind test.

## Rulings
Confirmed by Denning on 2026-11-09 and appended to `docs/RULINGS.md` as R-292 to R-305 (R-296 widened to a player
leaving base; R-304 offence or defence in the objective layer; R-305 the double run). His answers to the open
questions: the timing rule is right (R-297); a blind pick says what a leave became, because players can usually tell
(R-296); the down side of a numbers advantage is its own decision (R-301).

## Definitions
Ruled 2026-11-10: at a place = more than half of the group's living players inside the labelled area (R-319); fell to
footmen from the Footman labels and the measured reach (R-320); something gained elsewhere = a live numbers advantage
at main, NPC damage in progress or a boost about to land (R-321). Still needed: how long after leaving a departure's
purpose is fixed (in use as a draft: 60 s, or earlier on a pickup or on entering the enemy base); the job table
(Claude drafts in stage D). For step 4: a stand-off, a turtle. The draft's thresholds are in `common.py` on the branch.

### Reading a double run (R-305)
Two flags in motion at once, never two players leaving for the spawn together. Detected from: a second player leaving
for the spawn while the first flag is carried or about to be capped; a second runner who leaves main only after the
first pickup; a drop and pickup between two team-mates part-way to the stand (the half run), after which the first
carrier returns to the spawn. In family 1 the "two runners" calls are these forms; which form was used is part of the
call's shape (timing and who).

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
  clean. Open at 2026-11-10 after Denning's corrections: the two flag spawns on Isle of Solitude (drafted, not yet
  accepted), and one outer archer a side on Isle of Weeping Stone that does not mirror (his to judge).

## Risks
Thin cells at 506 matches (many cards will read "no clear difference"); intent is not recorded; hindsight labels suit
analysis but not the blind test's question; longer reads risk recording the fight's result (positions and commitments
only, forced reads apart, the pre-trend check stays); the win model prices every decision (hard results do not depend on
it); stronger teams choose differently (strength stays in the adjustment); the replays lack energy and line of sight.
