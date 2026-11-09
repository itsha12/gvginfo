# Decision engine redesign: plan

A plan, not the current state: `docs/SPEC.md` still describes the engine as built. This file is replaced as steps land
and removed once SPEC.md describes the new structure. Draft rulings below are **not in force** until Denning confirms
them; only then are they appended to `docs/RULINGS.md`.

Status: step 1 built (2026-11-09). Steps 2 to 4 not started.

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
| 1 Flag decision | an enemy player leaves main to run; a boost is coming; own flag in hand | where both mains are, flag lead, enemy backup in hand, own flag in hand, seconds to boost, who holds on each side | runners (none, one, two) with where the rest go: stay at the stand, fall to footmen, retreat to the pit, push their flagger, push the flag through as a team | enemy_pickup, boost_clock, eight_v_eight_or_flag, runner_choice |
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
2.1 named zones from labelled areas (unlabelled halls keep the circles); 2.2 path distance along the walkable outline;
2.3 departures (every leave from a main group or the res shrine, labelled afterwards as run, split, collapse, retreat
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

## Tests
- **Golden moments** (new): about 20 to 30 moments (a match and a time) Denning labels by hand on a site page: which
  scenario, what the team did (call and shape), optionally what they should have done (stored sealed from the model).
  Claude picks them once the classifier's first draft exists, to cover every scenario of families 1 to 3 and the hard
  cases. The engine's labels must match before a rebuild is accepted; the set is re-run after every engine change.
- Held-out advice test; readability test (now also the blind page and the card); mock picks; the cumulative blind test.

## Draft rulings (awaiting Denning's confirmation)
- R-292. Blind round 3 is void; new rounds are paused until the decision card exists; rounds 1 and 2 are kept as the
  first design and left out of the cumulative score.
- R-293. R-284 amended: five picks a round, at least three where the model differs from the usual play, chosen for
  leverage and a real choice; at most five options plus "Other"; scored cumulatively with a range; a reason whenever
  Denning differs from the model.
- R-294. A call is read over 20 to 30 s from positions and commitments, not damage or deaths; outcomes at 90 s and about
  3 minutes, as hard results beside win points.
- R-295. Decisions are five families, each with scenarios, each scenario with its own options.
- R-296. The enemy's decision to run or split is read from the moment a player leaves main or the res shrine, labelled
  afterwards by what the leave became.
- R-297. A call has a shape: composition, route, timing. Composition and route are decisions; a delay is a decision
  when something was being gained elsewhere, execution otherwise.
- R-298. Each call has a job with a success test read across the whole map; playing for the wrong job is an execution
  fault, apart from mechanics.
- R-299. Three verdicts on a call; execution read before the result; enemy execution scored, never a fix.
- R-300. The decision card is the one answer format; the TQs are retired from the report.
- R-301. A numbers advantage is read from both sides.
- R-302. Maps are pooled by features, never restricted to one hall; Denning's map labels override estimates.
- R-303. Detection is tested against Denning's golden moments before a rebuild is accepted and after every engine change.

## Open questions for Denning
1. Is the timing rule (R-297) the right line?
2. When an enemy player leaves main, should a blind pick say what the leave became (hindsight the team lacked, though
   players usually read it), or be set a few seconds later once the direction is unmistakable?
3. The down side of a numbers advantage as its own decision inside family 3?
4. Offence or defence moved from a decision to the objective layer of a fight?
5. Definitions needed before step 2: at the stand / fell to footmen / retreated to the pit (from labelled areas); a
   double run; how long after leaving a departure's purpose is fixed (proposed 60 s, or earlier on a pickup or entering
   the enemy base); the job table; what counts as something gained elsewhere. For step 4: a stand-off, a turtle.

## Risks
Thin cells at 506 matches (many cards will read "no clear difference"); intent is not recorded; hindsight labels suit
analysis but not the blind test's question; longer reads risk recording the fight's result (positions and commitments
only, forced reads apart, the pre-trend check stays); the win model prices every decision (hard results do not depend on
it); stronger teams choose differently (strength stays in the adjustment); the replays lack energy and line of sight.
