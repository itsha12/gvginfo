# How concepts are measured in replay data

Working notes for Claude: the analysis framework, where everything is stored, and how each concept on the GvG tactics
page is detected in gvg.report replays. The goal is not counting deaths: it is knowing what game state caused each
fight, what the fight caused, and what the best play was in that situation for those builds (tactics `W6`, `W7`).

## The framework (layers)
1. **Shared constants** (`common.py`): every threshold, radius, spike anchor and skill list in one place.
2. **Game state every second** (`state.py`): positions and zones (own pit, own base, backside, stand, push side,
   enemy base, enemy pit), who is alive and when the dead return, morale, fight groups and the main group, pit NPCs,
   the flag carriers and stand owner, each team's flag spawn, estimated NPC positions (`data/maps/`).
3. **Scoreboard** (`scoreboard.py`): every edge, per team, at any second, the one place "who is ahead" is decided:
   - flag position: each team's flag ETA, response on the next capture exchange, flag lead (up, even, down),
     backup flag, waiting runner, flag duty, whether the challenger can cap before the boost (details below);
   - numbers: alive, main group, who is down and for how long;
   - death penalty: morale per player and team, effective max health, the enemy's spike threat and who is now within
     one spike (DP stacking, `K4`);
   - pit NPCs (counts and value), Lord damage dealt (the tiebreak);
   - build archetype per team (WoC, invoke or paragon spike, hex way, double hammer balance, balance: a grouping
     label), healing monks and measured Lord damage per second (`benchmarks.py lord`, no guessed weights);
   - `edge()`: a provisional single number per team (NPC value + morale/10 - seconds down/30 + Lord damage/300 + flag
     lead/30, against the enemy's); `swing()`: what changed between two moments (deaths, NPCs, caps, boosts, Lord
     damage, DP, flag lead, edge). Weights are first guesses until the win-probability model.
4. **Episodes** (`episodes.py`, `fights.py`):
   - splits (members, entering the base, who answered, when and from where, NPCs killed, main numbers meanwhile);
   - flag runs (runner, line, escort, pushers, help and its latency, half or full double running);
   - flag cycles: every capture answers the previous one; cap delay, the pickup that started the run (through
     hand-offs), the trip from the team's previous capture, enemies in the way, a runner waiting at the spawn, and
     how much slower than possible the answer was (`slower_than_possible_s`: a choice or an obstruction);
   - deaths: forensics (numbers, flag and DP context from the scoreboard, backline in range and alive, prots landed,
     stripped or interrupted, knockdowns, interrupts, conditions, approach, peel) and an assessment (cause, graded
     mistakes, notes), plus what the death cost until the victim was back;
   - fights (`engagements`): deaths of either team no more than 20 s apart form one fight. For the losing side: the
     trigger (first death and its cause), the situation it fought in (numbers where it fought and why, flag position,
     at whose pit, after time, DP stacking, a monk first), whether it became a wipe, and the consequence until every
     player was back (NPCs, caps, boosts, Lord damage, DP, flag lead, edge), and whether the winner converted it;
   - monk profiles, numbers windows (power plays), posture.
5. **Decision points** (`decisions.py`): enemy pickups, splits entering the base, power plays, boost clocks, after a
   wipe, 24:00. Each records what every player of the deciding team did in the next 20 s (carrying, to the spawn,
   fell back, advanced, fought, held, died), the situation key (phase, flag position and lead, stand, boost clock, numbers, DP, NPC
   value and Lord damage differences, build matchup), the choice, and the outcome (scoreboard swing). The library
   compares outcomes by choice across matches (`library.py compare <kind> --where ...`); this is how "what is the
   best play here" gets evidence before the win-probability model exists.
6. **Judgement** (`rules.py`): findings with verdicts (good, on time, late, missed, wrong role, risky, mistake, great
   enemy play, note), each citing tactics line ids, and the edge ledger (every death with its cause and fight, boost,
   NPC lost with its split or fight, Lord damage by minute). Calibrated on Denning's rulings in
   `data/review_labels.json`.
7. **Benchmarks** (after the bulk pull): distributions of every measure across good teams, so "late" is measured.
8. **Win probability** (after the bulk pull): each team's chance to win from the scoreboard at any second, trained on
   hundreds of matches. It replaces the provisional edge: every fight and decision is then valued by the swing in win
   probability, and "what should they have done" compares the win probability after different choices in similar
   situations.

## From rulings to data (the plan)
The goal is not to reproduce Denning's or anyone's judgement but to find plays that are better than experts can see,
by weighing more variables, across more matches, than a person can hold in mind. Rulings stay valuable, in a new role.

**Principle: nothing is a weight or a default unless it is measured or is a definition.** Thresholds that define
terms (what counts as a fight, up on flags, a split) can come from Denning; anything that says how much something is
worth, or what the best play is, must come from the data, with its uncertainty. Measured so far: Lord damage per
second at the Lord (`benchmarks.py lord`), flag run speeds, the flag model's accuracy.

1. **Team strength first.** Rate every guild from all stored match results (1,600+ in `data/matches/`, far more than
   the replays), e.g. Bradley-Terry or Elo with time decay. Without it, "teams that did X won" mostly measures that good
   teams do X. Every comparison below controls for the strength gap.
2. **State = the scoreboard, as numbers.** Per team every 5 s: flag ETA, response and lead, stand and boost clock,
   carriers and flag duty; alive, down timers, players per zone, group structure; morale per player and effective
   health against the enemy's spike threat; each pit NPC alive; Lord damage; clock and res timer; build features (not
   just the archetype label: Auras of Stability, Infuse, prots, interrupts, knockdowns, measured Lord damage); and the
   strength gap. Exported as one training table per match.
3. **Win probability (WP).** A model of P(win) from the state, trained on every match (outcome = the result), tested
   on matches it never saw (grouped by match), checked for calibration (when it says 70%, does that team win about 7
   in 10?). Start simple (logistic, few features, sensible directions enforced: more NPCs never lowers WP) and add
   features only when they improve held-out accuracy. It must beat the strength gap alone and simple counts (boosts,
   deaths) mid-match, or it isn't learning the game. It replaces the provisional `edge()`.
4. **Value of everything that happens.** Every death, fight, capture, boost, NPC, interrupt on a key skill and
   knockdown is valued by the change in WP it caused (as football analytics values plays). Fights, conversions and
   players' contributions are then measured in WP, not by verdicts. Death causes stay as descriptions, not judgements.
5. **Value of choices.** At each decision point (and at moments found automatically, step 6), estimate the WP after
   each option that teams actually took in similar states (same flag position, numbers, DP, NPCs, clock, builds,
   strength gap): matched comparisons plus a model of WP a short time later given state and action. The gap between
   the best option and the one taken is the decision's cost. Options that teams rarely choose but that do better in
   matched states are exactly the "more optimal plays nobody sees". Every claim carries a bootstrap interval by match
   and a minimum number of cases; most will read "not enough data" for a while.
6. **Discovery, not just the decisions we thought of.** Find the seconds where WP moves most (high-leverage moments)
   and what preceded them; measure which state variables the WP model leans on most (some will matter more than
   experts expect, e.g. a runner's route, DP spread, timing against the res); cluster what teams actually do (the
   per-player action vectors) into choices nobody named. New decision kinds come from here.
7. **Guard against false discoveries.** Many comparisons produce chance winners: confirm any discovered play on
   held-out matches before it becomes a tactics line; watch for patches and meta shifts (compare by period); the
   replays cover only matches gvg.report observed.
8. **Rulings become the test suite.** Denning's rulings (`data/review_labels.json`) stay as definitions and as test
   cases: where the data agrees, the ruling is confirmed with numbers; where it disagrees, both sides are shown to
   Denning with the evidence, and neither silently wins. A Claude line on the tactics page is replaced by a measured
   statement once the data supports it.
9. **Proof it works.** On held-out matches: WP beats the baselines; and in matched situations, teams whose choice
   agreed with the engine's recommended option did better than teams whose choice didn't.

**Order of work:** (1) team strength from stored results and (2) the state export, both possible now and tested on
the 24 replays; (3) the bulk pull in batches of about 100, with analysis and state tables built in the GitHub Action
(the workspace can't reach gvg.report); (4) WP v1 and its calibration report; (5) values of events; (6) choice
values with intervals; (7) discovery; rulings checked at every step.

## Flag position (Denning, tactics `F1` to `F4`)
- Up on flags = the better position to get a boost and to run, not the team that capped last.
- ETA to capture: carrying = distance to the stand / 205 units per second; a dropped flag = the nearest runner's walk
  (270 u/s) plus the carry; at the spawn = the best runner's walk to the spawn (a dead runner waits for the res) plus Y
  (spawn to stand). Runners = players who carried in this match. Speeds measured on 24 matches (spawn to cap carries,
  median 41 s over ~8,400 units).
- Exchange: C (not holding) caps in ETA_C; holder H answers at max(ETA_H, ETA_C), so its response is the difference;
  C's next flag is Y away if a runner is waiting at its spawn (within 1,200, out of the main group, not trading damage
  for 10 s), else the walk back plus Y (2Y). Flag lead = enemy response minus own; up/down at 10 s.
- Accuracy on 279 real answers: median error -5 s, half within 15 s; the lead's sign matches the real exchange in
  152 of 200 clear cases. Answers 30 s+ slower than possible (56 of 279) are choices or obstruction, which is what
  `slower_than_possible_s` flags.
- Dropped flags are assumed to lie where they fell until the team picks one up again; a pickup far from the drop
  means it was returned to the spawn (taken as at once).
- gvg.report occasionally records a capture without the player (4 of 304 in 24 matches). Captures alternate, so it
  belongs to the team not holding; `Match._fix_flags` assigns it to that team's open carry. Before this fix the engine
  dropped those captures and misread who held the stand (e.g. [Men v HC C] 6:29 to 7:57).

## Death causes (`fights.assess`, in order)
1. **Spike**: 450+ damage within 2 s on a target at 60%+ health (judged on prot timing, `X3`).
2. **Backline down**: a monk of the team is dead and the victim had no support in range (`K11`); "in a chain" when
   that monk died in the last 20 s.
3. **Outnumbered away from pit while up on flags**: enemy running, own team up on flags, own runner not carrying, the
   victim not on flag duty, no support, on the backside or stand (minor mistake, `F6`, `F7`).
4. **Fight during a forced flag run**: enemy running, own team not up on flags, no support (`F5`, `F11`).
5. **Positioning** (no support in range): caught away from its group (2,000+ from its main group), overextended
   (1,000+ nearer the enemy pit than its main group on the enemy side), chased down while retreating, or out of range
   of its monks.
6. **Coordinated enemy pressure**: support in range and 2+ live monks under attack or knocked down (`M1`).
7. **Lack of support**: support in range, a monk free, no prots cast on the victim.
8. **Out-pressured despite support**: prots cast, one monk tied up. **Out-damaged despite prots**: backline free.
- Support in range = at least 2 live monks (1 for a monk victim) within cast range for 60% of the seconds they were
  alive in the 15 s before. Dead monks are counted as dead, never as out of range. Healing monks = slots 6 to 8 plus
  any monk without Word of Censure.
- Smaller mistakes graded basic, minor or acceptable (Daze beside a ranger, Aura of Stability not used, no defensive
  interrupts, peel on monks only); luck notes (quarter-second interrupts); a DP-stacking note when the victim's
  health was within one enemy spike.
- Verdicts follow the cause: great enemy play; mistake for positioning, lack of support and outnumbered while up on
  flags; note for the rest (a basic mistake makes it a mistake).
- Distribution on 24 matches (376 deaths): backline down 96, caught away from its group 58, out-pressured despite
  support 45, coordinated enemy pressure 45, spike 31, out of range of its monks 24, out-damaged despite prots 21,
  chased down while retreating 20, lack of support 19, forced flag run 12, outnumbered while up on flags 3,
  overextended 2. Fights: 176, of which 45 wipes.

## Where things are stored
- **Process = code** in `tools/replay_analysis/`. Prose instructions stay short; thresholds live in `common.py`.
- **Per-map knowledge**: `data/maps/<map id>.json`, NPC positions estimated from melee attackers (the replay has no
  NPC positions). Added only with `analyze.py --save-maps`, once per match (re-runs don't change the files).
- **Case library** (`library.py`): `build` gathers every kind from the analysis files; `query <kind> --where` searches
  them; `compare <decision kind> --where` compares outcomes by choice.
- **Per-match analysis**: `analyze.py <id>` writes format gvginfo.analysis.v1 (ENGINE 15). Regenerated in about a
  second per match, so not stored yet; for the bulk pull it goes to `analysis/<id>.json` on the `replays` branch.
- **Principles**: `knowledge/tactics.md`, ids cited by findings, rulings and situation cards (section 14).
- **Denning's verdicts**: `data/review_labels.json`, applied in `rules.py` and `fights.assess`.

## Known limits
- No energy in the data. Positions about once a second. No NPC positions or health (estimated). Intent and what a
  player is looking at are never in the data.
- The provisional edge's weights are guesses; compare choices by their components (deaths, NPCs, caps) as well.
- 24 matches is far too few to settle a choice; `compare` results are hypotheses until the bulk pull.
- Split detection marks a "flank" when splitters stay near the enemy main group; early-game fights on one side can
  still show as splits with the whole enemy team "answering".
- Archetypes come from bars by simple rules (e.g. hex way = 2+ hex casters with 4+ hexes and at most 2 healing
  monks); they only group matchups. Lord damage per second is measured, but rangers' figure leans on solo splits into
  empty pits (less resistance than a full push).

## Roles and positions
- Roles come from each player's build and party slot (`replaylib.Match.roles`). Positions are labelled relative to the
  player's own team: backside, push side, base, enemy base, stand.
- Position jumps from Aura of Displacement are real: the caster Shadow Steps to the target, then returns when they stop
  maintaining it.
- Pit position comes from players hitting the Lord, else the knights and Bodyguard, else the res shrine.

## Kills and timing
- "After time": within 15 s after an even 2-minute mark.
- Spike anchors (`X1`, `X2`): 550 armor ignoring in 0.35 s or more than the target's health in 0.35 s is not saveable;
  400 armor respecting in 0.6 s on a shield set should be survivable (`report.py spikes`).
- Spike catching per team (`report.py catches`): enemy bursts (3+ attackers, 250+ in 2 s) killed, saved with a prot,
  or survived without one, with prot timing.

## Monks, mesmers and comms
- Monk spacing, fakes (cancelled casts not caused by an interrupt), time dazed, peel, weapon sets as before
  (`fights.monks`, `report.py`).
- Comms and commentary: line up transcript times with match time using two or three anchors (kills, caps, boosts);
  check every claim against the data; store paraphrased events only, never transcripts (public repo).
