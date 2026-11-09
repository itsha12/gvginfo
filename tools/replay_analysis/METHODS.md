# How concepts are measured in replay data

Reference for Claude: how each concept on the GvG tactics page is detected in gvg.report replays, and the standard an
answer must meet. Current state only; history is in docs/CHANGELOG.md, the design in docs/SPEC.md, Denning's definitions
in docs/RULINGS.md. The goal is not counting deaths: it is knowing what game state caused each fight, what the fight
caused, and what the best play was in that situation for those builds (tactics `W6`, `W7`).

## The framework (layers)
0. **Data integrity** (`integrity.py`, runs inside `Match()` on load): every replay is checked and repaired before any
   layer reads it (see "Data integrity" below).
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
7. **Benchmarks** (`benchmarks.py`): measured values from all replays (so far Lord damage per second at the Lord).
8. **Win probability** (`model.py`; structure in docs/SPEC.md): a glass-box model, trained in chunks. It replaces the
   provisional edge: every fight and decision is valued by the swing in win probability, with a readable breakdown of why.

### Requirements (Denning)
- **Learns like a neural network, but white box.** Non-linear effects and interactions are learned from data, but
  everything learned is readable: no hidden layers nobody can inspect.
- **Explains why.** Every judgement comes as a breakdown of contributions, not just a probability.
- **Human readable and amendable.** Denning can see what the model learned, correct it, and add variables; every
  correction is logged with its reason and tested.
- **Built structure first, trained slowly.** The model's structure is built and tested before any large pull. Training
  then proceeds a few matches at a time; after each batch Claude reports what was learned and what changed, in words.
- **Discovery matters most.** There will be many variables and interactions nobody is aware of; the engine must
  surface them, not only test what we already believe.

**Principle: nothing is a weight or a default unless it is measured or is a definition.** Thresholds that define
terms (what counts as a fight, up on flags, a split) can come from Denning; anything that says how much something is
worth, or what the best play is, comes from the data, with its uncertainty. Measured so far: Lord damage per second at
the Lord (`benchmarks.py lord`), flag run speeds, the flag model's accuracy.

### The model (design requirements; the structure as built is in docs/SPEC.md)
- **Inputs = named variables, the visible "neurons".** In a neural network the hidden layers invent their own features;
  here the features are named and readable: per team every 5 s, the scoreboard as numbers (flag ETA, response and
  lead, stand and boost clock, carriers and flag duty; alive, down timers, players per zone, group structure; morale
  per player and effective health against the enemy's spike threat; each pit NPC alive; Lord damage; clock and res
  timer; build features such as Auras of Stability, Infuse, prots, interrupts, knockdowns and measured Lord damage;
  and the team strength gap). The match table ("state export") is one row per 5 s per team with these numbers and
  whether that team won. It is internal; nothing is downloaded.
- **Win probability from a glass-box model**: an additive model with chosen pairwise interactions (Explainable
  Boosting Machine, `interpret` package). Its prediction is a baseline plus one contribution per variable and per
  interaction, each stored as a readable curve or table ("flag lead 0 to +30 s adds about X%"; "DP matters little
  against balance but a lot against a spike"). Accuracy compared with a black-box model on the same data, so the cost
  of readability is measured, not assumed.
- **Explanations**: every moment, death, fight and decision is shown as its breakdown ("HC 58%: flag lead +6, pit
  NPCs +4, DP -3, Men's Lord damage -2"); a choice as the comparison of options in similar situations and where the
  difference came from ("in 37 similar cases falling back did 5 points better, almost all from deaths avoided on the
  backside").
- **The model file**: the learned curves and tables are saved in a readable file in the repo (and shown on the site),
  with each variable's uncertainty and the number of matches behind it.
- **Corrections** (`data/model_corrections.json`, each with Denning's reason): a direction ("more pit NPCs never lowers
  win chance"), a fixed value or cap where data is thin, a new variable to add, an interaction to include or drop. The
  engine reports held-out accuracy with and without each correction, so a correction is tested, not trusted.

### Discovery
- **Surprises**: moments where the win probability swung most, or where the model was most wrong. Each is a place a
  variable is missing; Claude proposes one, Denning names, checks or rejects it.
- **Interactions**: the model is offered every pairwise interaction among the variables and keeps those that improve
  held-out accuracy; each kept interaction is shown as a table and explained ("a backup flag is worth much more when
  the enemy runner is the Mes/A").
- **Behaviour clusters**: what teams actually do (the per-player action vectors at decision points) clustered into
  choices nobody named.
- **Leverage**: situations where the choice changes the win probability most, so attention goes where decisions
  matter.
- **False discoveries**: many comparisons produce chance winners. A discovery becomes a tactics line only after it
  holds on matches the model hasn't seen; patches and meta shifts are watched by period; replays cover only matches
  gvg.report observed.

### Values and choices
- **Team strength** from every stored result (1,600+), so "teams that did X won" isn't just "good teams do X".
- **Value of events**: each death, fight, capture, boost, NPC, key interrupt and knockdown valued by the change in win
  probability, with its breakdown. Death causes stay as descriptions, not verdicts.
- **Value of choices**: at decision points and discovered moments, compare the options teams actually took in similar
  situations (matched on the variables and the strength gap), with intervals by match and a minimum number of cases;
  rarely chosen options that do better are the plays nobody sees.
- **Rulings are the test suite**: where the data agrees with a ruling, it is confirmed with numbers; where it
  disagrees, both sides are shown with the evidence and neither silently wins.
- **Proof it works**: on matches it hasn't seen, the model beats the strength gap alone and simple counts (boosts,
  deaths); and teams whose choices matched the recommended option did better than teams whose choices didn't.

### The TQs: what the report demonstrates after a batch
They replace the five random whys and show how the engine is learning. Each comes from the batch's matches:
  1. Flags: one instance in a batched match where a team got behind on flags, and why; then how a different play could
     have increased its win chances.
  2. Monk death: one instance where a monk died, and why; then how it could have been prevented.
  3. Power play: one instance where a team couldn't kill on a power play, and why; then how it could have been
     converted into kills.
  4. NPCs: one instance where a team lost NPCs, and why; then how it could have been prevented.
The why half comes from events.py and forensics.py (flag, death, power; npc for NPC losses). The second half (the
different play, how to prevent or convert) must also come from measurement: the usual play's effect of each choice at
the decision before (usual.py), the ready-but-unused prots and the uncontrolled attackers in the forensics, the
benchmarks for the role, and the node models' readings with the variable changed. Say when the engine can't measure
the alternative.

**As built** (`tq.py`, the learning report's section "The TQs", 2026-11-07). Each instance is the biggest of its kind in
the newest batch (from all trained matches when the batch has none): the biggest flag swing (`events.find("flag")`), the
monk death (8 Monk, 7 Monk or Prot; deliberate deaths in the own base back within 15 s left out, `K14`) that cost the
most win chance from 10 s before to 30 s after, the biggest power play without a kill (`events.find("power")`), and the
knight or Bodyguard loss that cost the most win chance. Each answer: the event's account (events.py, forensics), "why,
in short", then the different play from these sources only:
- Decisions (usual.py): each decision point of the team in the event's window, with its refined choice, the usual play
  among the 15 most similar decisions in other matches, and the choices that did measurably better (2+ points more than
  the choice made; marked clear or not, and "partly who chooses it" when the placebo check flags it; effects are
  against the kind's most common choice, so a difference between two other choices is approximate), plus the
  fight-state third where the kind has one.
- Node readings with a variable changed (`tq.what_if`, models that never saw the match): flags, the flag-answer node with
  a waiting runner, the runner alive, no forced drops, no parking, no own deaths, no enemies on the way (seconds), and
  the seconds read by the win model as flag lead; monk death, the deaths node with a prot up (only when one was ready and
  unused), another healer in range, the Daze or Cripple removed, no knockdowns, staying with the group, one attacker
  peeled off, hexes removed, and all together; power play, the kill-conversion node on its biggest burst with all damage
  dealers in it, on each other enemy player at that second (their own state from the deaths rows), with a knockdown or
  Daze on the target (only if the build has them) or a hex on the target's healers; NPCs, the NPC-loss node with one more
  defender, one more healer defender, two more, and healing on the NPCs. Each change in a result's chance is priced in
  win points at what that event actually cost (its measured win-chance change) and at the typical value (values.py).
- Unused options (forensics): prots ready and in range but not cast, knockdown immunity ready, attackers left free.
- Benchmarks: every stored power play of 3+ more at main, killed against not (damage per second, top-target share,
  damage uptime; `power_bench`, cached per match); every stored split into a base (first-defender latency).
- Confidence comes from the evidence: "medium to high" when two independent measurements support the alternative (a node
  model that beats its baseline on unseen matches and moves the chance by 5+ points or 15% of itself, and a clear
  usual-play effect not flagged as partly who chooses it), "medium" with one, "low" when the measured ranges still
  include no effect or nothing could be priced.
Known gaps: a power play with no 2 s burst can't be read by the kill-conversion node; the win model's flag-lead curve
still bends the wrong way at the extremes, so seconds of flag lead are sometimes not priced (the answer says so).

**Changes 2026-11-07 (session 4p, after batch 7):**
- Flag swings count only real deficits (`events._real_low`): the lead stays below -15 s for 15 s or more, or the enemy
  takes the stand within 30 s. The scoreboard counts any carrier as a capture in its carry time, so a lone carrier next
  to eight enemies read as a sure capture ([Team v Men] 3:30). Measured: runs with 3 to 5 own alive against an enemy
  holding the stand with 6+ captured 2 of 14.
- How it got there (`tq.lead_up`): monk-death, NPC-loss and flag answers trace back up to 120 s to when the team's main
  was first outnumbered by 3+, list who was away and doing what (dead, carrying, escorting, elsewhere), and price the
  team's flag runs in that window against every stored run made while the enemy held the stand (`tq.run_bench`: capture
  rate, own deaths in 40 s, held-out win change, by main numbers and escort size), plus the decisions in the window.
  First reading (91 matches): main outnumbered by 3+, escort 2+: captured 0 of 6; escort 0 to 1: 10 of 21.
- NPC losses with dead defenders explain each defender's death (forensics key causes).
- Power-play "why, in short": damage uptime over the whole power play in contact with an enemy group (was the phase at
  its start, often the walk in); each measure is named a cause only if it sits on the non-killing side of the midpoint
  between the killing and non-killing medians (direction from the data).
- `defenders_present` at an NPC kill (episodes.py) = defenders alive in their own base or pit at the kill (was anyone
  who had defended before it, dead or not).
- Each TQ prefers a match not used by an earlier TQ in the same report.
- Flag ETA of a carrier behind on players alive (scoreboard.py `eta`, `carry_chance`; data/benchmarks/carry_capture.json
  from `benchmarks.py carry`, Denning approved 2026-11-07): carry time plus (1 - chance / chance at even numbers) times a
  fresh run from the spawn. Measured on 91 matches, capture chance by alive difference: +2 or more 64% (107 carries),
  -1 to +1 49% (1381), -3 to -2 35% (88), -4 or less 25% (20). Even or better keeps the plain carry time. Rebuild the
  benchmark after new replays (`benchmarks.py carry`).
- Flag spawns and stands per map (state.py `_flag_spawns`, replaylib.py; data/benchmarks/flag_spawns.json from
  `benchmarks.py spawns`, 2026-11-07): each map's two spawns are the densest clusters of flag pickups pooled over every
  replay of the map, and a match uses the one nearest each team's base. The old rule (pickups 6,000+ from the stand)
  missed short flag runs: Imperial, Nomad's and Druid's Isles (spawns about 4,200 to 4,900 from the stand) fell back to
  the bases, doubling their flag run, every flag ETA and lead on them, and map_flag_run; other single matches caught a
  choke where dropped flags were picked up. Four replays with no located stand (0, 0) now use the map's median stand.
  Rebuild the table after new replays (`benchmarks.py spawns`), before `benchmarks.py carry`.
- The causal chain (`chain.py`, Denning 2026-11-07; replaces `tq.lead_up`): TQs 1, 2 and 4 trace how the game state
  came about, as a chain of states each caused by the one before (pit lost <- defenders dead or away <- the deaths and
  their measured causes <- the fight's numbers <- flag duty <- the flag deficit <- what turned it; plus an enemy split in
  the base and an isolated player). Back to the last reset (both teams 8 alive, flag lead within 10 s) or 3 minutes;
  the 2 biggest causes followed at each link (by held-out win change); ongoing states that began before the reset (a
  split, a player away, flag duty) stay in. Fixes: only the 2 that would have mattered most, priced in win points from
  measurement (usual play, deaths node read again, run benchmark).
- Defensive play by a disrupting player (`forensics.disruption`; Denning: for a Mesmer, defensive = interrupting
  offensive skills and casting on the enemy midline and frontline; offensive = interrupting the enemy monks): share of
  its interrupts and enemy-targeted casts on the midline or frontline, against every stored own-healer death
  (`chain.mes_benchmark`; first reading: median 86%, 493 cases).
- The event layer (`eventlayer.py`, step 1 of the learned causal map, 2026-11-07): strips (useful = a prot off a target
  under attack, or an enchantment off a midline/frontline player) and wasted removal casts, Blinds on enemies (frontline,
  defensive), hexes (time on, removed), frontline peel (damage on attackers of own backline / on enemy healers), wrong
  casts for every role (interrupted after casting into a ready interrupt, while Dazed, attacks while Blind), spike
  timing, run timing (enemy boost clock, enemy power play), splits (answer latency, effect, enemies drawn, cost at
  main), power plays of every size with why the enemy was short, and enemy captures from the defending side. Cached per
  match; `eventlayer.py report [--all]` writes data/model/reports/measures.md. Power plays: every size counts (Denning:
  an 8v7 while the enemy runs is a power play); TQ 3 picks the one that cost the most win chance and benchmarks it
  against power plays of the same size.
- Step 2a of the learned causal map (`eventlayer.py`, Denning 2026-11-07: what counts as right comes from data): every
  strip is judged against every enchantment on an enemy in the stripper's cast range at that moment; every hex-removal
  cast against every hex on an ally in the remover's range (and how long the removed hex had been on); every player's
  fight damage against its role's usual (median damage per second on enemy players per player per fight; class median
  under 20 cases). Values (`eventlayer.py values` -> data/benchmarks/eventlayer_values.json, rebuilt each batch): an
  enchantment = its recorded output (gvg.report damage + healing + prevented) per second up, plus the drop in the
  bearer's output in the 10 s after a strip (attunements record no output of their own); a hex = its recorded damage per
  second on, plus the drop in the hexed player's output while it was on. Both drops are differences in differences
  (the same change for allies of the same class over the same seconds is subtracted, so the fight's own rise is taken
  out); 5+ cases needed; negative values read as no measurable cost. Limits: the values include every trained match
  (not time ordered); output means damage and healing only (energy, speed and armor show only through them).
- Step 2b of the learned causal map (`learnednodes.py`): nine node models built from the event layer, each using only
  the causal-map links into it, glass box (main effects only), held out by match (6 folds): run outcome (R.3; control
  and damage on the runner read at 5, 15 and 30 s into every run), flag swing (R.3; flag lead change over the next
  60 s), run defence (R.3; every enemy run from the defending side at 5, 15 and 30 s in: free defenders, pushers,
  control and damage on the runner so far; added after capture speed, which sees captures only, could not show what
  pushing stops), capture speed (R.3; seconds of an enemy capture, the defence read 10 s into the run: pushers, control and
  damage on the runner so far; counts over the whole run grow with its length, and "seconds to the first push"
  defaulting to the run's length leaked the answer in the first build), power play (K.4; any size kills), fight outcome (R.2; play
  before the fight's first death; fights.py stores fights from the losing side, so the side read alternates), split
  chance (A.allocation; a split starts in the next 30 s), split answer (P.11; seconds to the first defender, 60 =
  never), split effect (R.5; a pit NPC killed), collapse (R.1; a split member dies; collapse timing read five ways,
  each also tested alone, since Denning left the right reading to the data: arrival spread, numbers at contact, time
  from the split's first NPC hit to the first defender, res timer at arrival, and split members' speed skills off
  recharge at arrival under K.13). A link's strength = the held-out
  loss without the link's features minus with them (same folds); supported above twice its spread across folds,
  rejected when dropping it helps by more than that, else not clear yet (link tests fit 2 bags per variant, the final
  readable model 4). Written into causal_map.json (`measured`, per node). A link's status follows the data only if it
  was a hypothesis or the data set it (`status_by: data`): supported if any node supports it, rejected if every node
  that measured it rejects it, else back to hypothesis; Denning's and formula statuses never change, and a link from Denning is never rejected without his ruling (held with `pending_rejection`; `override_approved: true` lets the data reject it and then follow the data both ways). Appended to data/model/link_log.json each run; links a node needed and
  the map lacked were added as hypotheses (logged, with source). Rows are built in `lnrows.py` (cache kind "lrows",
  keyed by that file and the values' hash), so a change to the fitting never rebuilds them. Each batch also writes
  knowledge/learned-model.md ("What the model has learned" on the site): every learned node and cause in words. New map nodes: P.17 wrong casts, P.18 enchantment
  strips, P.19 Blind on enemies; P.5 now covers hex removal. `whatif(node, row, changes)` reads a node again with
  features changed (for step 4). The power-play node keeps the window's length as exposure (a longer power play has
  more time to kill).
- Correction (Denning, batch 7): lord_dps_own and lord_dps_enemy capped at 5 points (data/model_corrections.json).
- Usual play includes the map (usual.py `MAP_COLS`): geometry in the similarity and, with the build axes, the adjustment;
  choice effects split by map name once a map has 10+ cases of the choice and of the usual one.


### Answer exemplars
These set the kind of answer the engine must produce: the event, the measured causes in order, and "why, in short".
1. **Behind on flags** (Book v TFS, a9fa1ae1, 4:05 to 5:15; TFS +78 s to -73 s): TFS held the stand with its runner
   waiting (correct); Book capped 5 s before TFS's boost and put 6 players on the stand within 6 s; TFS fought 8v8 at the
   stand to force the cap into double hammer. TFS's 8 Monk took 666 damage, all from attacks (Hammer B 630, 3
   knockdowns: Hammer Bash, Coward, Hammer Bash; Deep Wound twice); one prot was cast on him (7 Monk Guardian, interrupted
   by Power Spike) while the Prot's Guardian and Shielding Hands were ready and in range (the Prot was casting on the AoB
   dervish and itself); Aura of Stability had ended 12 s before the first knockdown and was not recast. TFS's damage was
   about 32 per second (below the median of 37) against Book's 120 (above the 90th percentile), so Book could stand on
   the stand freely. The Ritualist then died with the flag; the cascade lost three more and the flag lead.
2. **8 Monk death** (RJT v RACK, eea5ba87, 4:01): alone as the only healer in a 3v3 split defence in his own base (allied
   healers 4,800 away; nearest enemy about 220, below the median 8 monk distance of about 500); the Ranger, 300 away,
   crippled him (3:43) and dazed him (3:45, Concussion Shot) while he was on his shield set; 7 of his 9 casts came while
   Dazed and 4 were interrupted (Concussion Shot, Power Spike, Complicate, Savage Shot), far above the 8 monk norm; half
   the damage ignored armor, so his Guardians could act on only about half of it; his own Dismiss Condition never
   removed the Daze; neither attacker was snared, blinded, interrupted or knocked down (the AoB dervish was beside the
   Ranger, hitting it); he died one second after the res.
3. **Power play without a kill** (True v One, f34cb3a9, 11:21): 7v3 at the stand for 50 s; One's group gave ground and
   joined its others; True dealt 18 damage per second (below the 20th percentile) spread over four targets; One healed
   56 per second and cast Aura of Stability three times against True's hammer.
4. **Spike survived** (Team v push, 2df9b7fd, 11:38): five Word of Censure over 1.5 s and Bane Signets 3 s later (spread
   3.0 s against a median 1.1 s for spikes that killed); Spirit Bond was up 1.2 s before the first hit; Blessed Light,
   Aegis and a 440 Infuse followed.

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
- **Per-match analysis**: `analyze.py <id>` writes format gvginfo.analysis.v1 (ENGINE 17), saved in the cache keyed by
  the engine code (`cache.py`); kept between sessions on the `cache` branch (`cache.py sync push`).
- **Principles**: `knowledge/tactics.md`, ids cited by findings, rulings and situation cards (section 14).
- **Denning's verdicts**: `data/review_labels.json`, applied in `rules.py` and `fights.assess`.
- **The blind test** (`advice.py`, R-284): `data/model/blind_tests.json` holds every round (open and scored). A round =
  8 picks, 6 random decisions spread over kinds and 2 where the advice differs from the usual play; each pick carries
  the moment (match, team, opponent, map, time, situation, choices seen), the model's call, the usual play, Denning's
  call and reason, and a sealed part (base64, never printed: the actual choice, its win-chance change, and the mean
  win-chance change of each choice among the 15 most similar decisions in other matches). Added by the Train batch
  workflow after each chunk (`advice.py /tmp/ga --blind-only --batch=N`; input `blind`), never refreshed. Answered and
  scored on the site (Model > Blind test, `assets/js/pages/blindtest.js`, which decodes the sealed part only once every
  call is in) or with `advice.py blind_score [round]`; the two score the same way: each call's expected win-chance
  change in that situation, and whether it matched what the team did.

## Known limits
- Fits from the model library (interpret) can differ in the last digits between processor types: the same code and
  identical input tables gave a held-out log loss of 0.554 on one GitHub machine and 0.550 on another (2026-11-07).
  Read differences of that size between reports as noise; `timings.json` records the processor.
- Fixed 2026-11-07: `nodes._aoe_skills` cached area-damage counts by player slot only, so the npc_loss, lord_damage and
  lord_kill rows (attackers_area_damage) depended on which matches a process built first. Now keyed by the bar.
- No energy in the data. Positions about once a second. No NPC positions or health (estimated). Intent and what a
  player is looking at are never in the data.
- The provisional edge's weights are guesses; compare choices by their components (deaths, NPCs, caps) as well.
- 24 matches is far too few to settle a choice; `compare` results are hypotheses until slow training has added many more.
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
