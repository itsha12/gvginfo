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
7. **Benchmarks** (`benchmarks.py`): measured values from all replays (so far Lord damage per second at the Lord).
8. **Win probability** (to build): a glass-box model trained slowly, a few matches at a time (see "From rulings to
   data"). It replaces the provisional edge: every fight and decision is then valued by the swing in win probability,
   with a readable breakdown of why.

## From rulings to data (the plan)
The goal is not to reproduce Denning's or anyone's judgement but to find plays that are better than experts can see,
by weighing more variables, and more interactions between them, across more matches than a person can hold in mind.
Rulings stay valuable, in a new role.

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

### The model
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

### Training slowly: learning reports
- Batches of a few matches (3 to 5 at first). After each batch: refit, then a **learning report**: which curves moved
  and by how much, which interactions appeared or faded, what newly became confident or uncertain, which past rulings
  the data now agrees or disagrees with, the batch's most surprising moments (where the model was most wrong) and the
  new candidate variables or interactions. Claude explains each in words with the match moments behind it; Denning
  answers or corrects; then the next batch.
- Reports are kept (one file per batch), so it is visible how the model's understanding developed.

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

### Order of work
1. Model structure on the 24 stored matches: team strength from stored results; the variables and the match table;
   the glass-box model, explanation breakdowns, the readable model file, corrections and the learning report. With 24
   matches the curves mean little; this step only proves the machinery works end to end.
2. Slow training: fetch 3 to 5 new replays at a time (the "Fetch replays" workflow), refit, learning report, Denning's
   answers and corrections, repeat. Batches grow only once the reports settle.
3. Discovery and choice values as data accumulates; tactics lines replaced by measured statements when the data
   supports them.

## The causal model (design, version 1; to build)
Why the win model alone isn't enough (Denning): boosts, wipes, cleared pits and DP are results; a model on results
says who is winning, not why. The engine has to explain why a team got behind on flags, why the other team boosted,
why a fight became a wipe, why a pit fell, why a team could or couldn't output damage, kill, or heal.

**Structure: a loop over time.** Context (builds and matchup, strength, map, clock) shapes every layer. Every second
each team allocates its 8 players (main, split, flag duty, defence, dead); allocation and the situation shape the plays
(decisions and micro); plays set each group's capacities (damage output and uptime, burst quality, kill conversion,
mitigation, healing, monk uptime and load, health ceiling, sustain margin, control received, removal capacity,
mobility); capacities produce results (deaths, wipes, flag lead, boosts, pit NPCs, Lord damage, time held, enemies
tied up, territory, tempo); results change the scoreboard, which shapes the next allocation; the win model values the
results. Fights are global (Denning `J1`): the unit is the **phase** (a stretch with a stable global setup), each team
has a **plan**, each group a **job** from that plan (strong side converts, weak side holds safely, runner caps and
returns, defenders hold), and a phase is judged as a **trade** across the whole map. Credit = what the trade would have
been had a group done its job at the level its matchup allows.

**The causal map** (`data/model/causal_map.json`, site page "Causal map", `causal_map.py render|check`): every concept
(node) with how it is measured, and every "X can cause Y" link with its reason, source (Denning, Claude, data,
formula), whether Denning confirmed the reasoning, status (hypothesis, supported, rejected, mechanical) and tactics ids.
Version 1: 50 nodes, 169 links, from the design conversation (scenarios 1 to 10 and follow-ups). Each node's model may
only use the links pointing into it, measured earlier in time; the data decides how much each link matters.
Explanations walk the map backwards from a result to the plays and context behind it.

**Amendments from reviewing the design before building:**
1. **Phases, not seconds, as rows** for jobs, capacities and trades: fewer, more independent rows, and the natural unit
   of a plan.
2. **Mechanical links are formulas, not learned** (sustain margin, health ceiling, flag ETA, a power play's deadline,
   boosts): no data is spent learning arithmetic.
3. **Expected for the matchup**: every capacity is compared with what is expected given the matchup, team strength and
   situation; the difference is how well the team played. This separates "lost to the matchup" from "lost on play"
   (`J10`).
4. **The usual play**: decisions are nodes too, caused by the situation. The engine learns what teams usually do in each
   situation and what that gets; a choice that does better than the usual play is a candidate "more optimal play".
5. **Time order is enforced**: causes are measured before the effect's window (otherwise the model learns that dead
   players stop casting).
6. **Credit follows the map's paths**, so a result isn't counted twice through correlated variables (the backwards
   knights curve in batch 1 is the kind of artifact this prevents).
7. **One measure per concept, shared**: e.g. "Mesmers free to defend" feeds both the flag and defensive interrupts.
8. **Pool by role and build features**, not by player or build name, until there is data for more.
9. **Every node model is tested on unseen matches** like the win model; a link that never helps becomes rejected, and an
   input outside the map that predicts well becomes a candidate link for Denning to explain or reject.
10. **Lower layers first**: deaths, bursts, runs and casts number in the hundreds or thousands per batch, so those
    links can be learned long before the win model has enough matches.
11. **Proxies are flagged**: there is no energy in the data (proxies: energy-denial casts, weapon swaps, drops in
    casting); nodes resting on proxies carry lower confidence.
12. **Plans are found and amended from data** (`J11`): setups are clustered into plans; Denning names or corrects them.

**Built (step 1 and 2, `phases.py`, ENGINE 16):** theatres (all alive players of both teams clustered within 2,000:
local numbers anywhere on the map), phases (setup changes lasting 8 s, deaths, res times, captures; median 13 s, about
54 per match), plan labels per team (starting list), a job per group (convert, hold, contest, cap and return, split,
defend, free) with job done or not, and capacities per group per phase: damage dealers and healers, pressure,
incoming damage, healing, sustain margin, damage uptime (active = attacking, casting or dealing damage that second)
with lost damage-seconds by cause, monk uptime, control received, bursts, kills, losses, health ceiling; plus each
phase's trade. Library kind `groups` (one row per group per phase). First look on 30 matches (descriptive, not causal):
strong sides that converted had 5 damage dealers against 4, pressure 50/s against 22/s, uptime 51% against 36%; weak
sides that held took 21/s incoming against 45/s, sustain margin +6 against -10.

**Built (step 3, first node models, `buildfeat.py`, `nodes.py`):** build features from the skill data (what each
bar causes and removes: interrupts, knockdowns, Blind, snares, strips, energy loss, prots, blocks, Aura of Stability,
removal, heals, speed) and matchup pairs (threat against answer). Node models, glass box, time order enforced:
- deaths: one row per alive player every 3 s (69,889 moments, 1,829 leading to a death within 10 s); features from the
  past only (health, health ceiling, damage taken, attackers, knockdowns, Daze, Deep Wound, cripple, interrupts, prots
  and blocks up, conditions taken on itself, healers in range or dead, allies and enemies near, local numbers, distance
  from group and pit, res timer, flag lead, minute, strength). Held out: AUC 0.896 against 0.764 for health and recent
  damage alone.
- kill_conversion: one row per burst (553; 165 killed within 8 s): target defence (prots, blocks, healers in range,
  health, ceiling, knockdown, Daze, Deep Wound, distance from group), attackers' shutdown (Blind, interrupts and
  knockdowns on them), the burst. Held out: AUC 0.784 against 0.647.
- Matchup counts are fixed for a whole match, so they switch on at 60 matches (`STAGE_FIXED`), as in the win model;
  staging raised both models' held-out accuracy.
- First readings (30 matches): health ceiling (DP) is among the strongest causes of both deaths and converted bursts
  (`K4`); two interrupts on the attackers cut a burst's kill chance by about 28 points; a burst on a healer converts
  only about 2 points more than on others (target choice matters but not hugely); being Dazed adds about 25 points to a
  player's death risk in the next 10 s, no healer in range about 11. `nodes.py explain` gives a player's risk second by
  second with its causes (from a model that never saw the match). The learning report has a section per node.

**Build order:** (1) phases, allocation per phase, plans and jobs (built); (2) capacities per group per phase,
measured (built); (3) first node models: deaths and kill conversion (built; expected-for-matchup baselines come with
the matchup features at 60 matches); (3) expected-for-matchup baselines and the first node models (deaths, kill
conversion), tested on the 30 matches; (4) the flag and boost chain; (5) pit NPCs and Lord damage; (6) usual-play
models and decision comparisons; (7) learning report sections with "why" chains for the biggest moments, and the
questions where the data and the map disagree. Slow training continues throughout.

## The model as built (batch 0)
- `strength.py`: team strength from every stored result (1,737 matches, 71 guilds), Bradley-Terry with a 60-day
  half-life, rated only from results before each match; unrated guilds use the ladder gap (never 0). On later results
  it predicts 82% of winners (log loss 0.417), better than the ladder (81%, 0.473). The in-match model has to beat
  this to show it understands play rather than who the better team is.
- `features.py`: the named variables (one line each, with a plain description). Matching own and enemy quantities are
  single differences (separate ones partly cancelled and split the data). One row per 5 s per team; training uses
  every 15 s.
- `model.py`: glass-box model (Explainable Boosting Machine). Baseline = team strength; the curves are what the game
  state adds. Staged complexity (`STAGES`): build variables from 60 matches, interactions from 40, because with few
  matches variables fixed for a whole match only fingerprint matches (seen in batch 0: both models then did worse
  than strength alone). Few boosting rounds (300), because the library's internal stopping test holds out rows, not
  whole matches. Validation holds out whole matches; compared with strength alone and a black box; verdict printed.
  Explanations are in points for an otherwise even game (readable at any win chance), and always come from a model
  fitted without that match (`model.py explain`). Writes `data/model/wp_model.json`, `wp_model.md` and the site page
  `knowledge/wp-model.md`. Corrections: `data/model_corrections.json` (direction, drop, interaction, cap), each
  tested by refitting with and without.
- `learning.py`: the learning report per batch (`data/model/reports/batch_NN.md`, `latest.md`, site page
  `knowledge/learning-report.md`; model snapshots in `data/model/history/`): the honest test, what it leans on and
  how that changed, the curves in words, discovery (interaction screen, untested; the moments it got most wrong),
  Denning's rulings through a model that never saw the match, questions.
- `batch.py`: `pick N` (random matches without replays, appended to `replays/requests.txt`, which starts the fetch
  workflow when pushed), `add` (stored replays not yet trained on become the next batch).
- Requires `pip install --break-system-packages interpret-core` in a new workspace.
- Batch 0 (24 matches): not yet better than strength alone (log loss 0.636 against 0.534; accuracy 74% both). It
  leans on morale difference, knights, Bodyguard, flag lead and Lord damage, but several curves run the wrong way
  (more own knights lowers win chance), which is the expected noise of 24 matches and a natural place for a
  direction correction.

- Candidate variables (`features.CANDIDATES`): proposed by Claude, Denning or discovery; computed for every match and
  retested in every learning report (held-out log loss with and without); moved into `VARIABLES` only once they
  improve predictions on unseen matches.

### A training round
1. `python3 batch.py pick 4`, commit and push `replays/requests.txt` (starts "Fetch replays"); wait for it.
2. `git fetch --depth 1 origin replays:refs/remotes/origin/replays`, `python3 batch.py add`, `python3 learning.py`.
3. Read the report; explain to Denning in words what changed and why (with match moments); ask the questions.
4. Log his corrections in `data/model_corrections.json`, new variables in `features.py`; commit everything.

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
  second per match, so not stored yet; once batches grow it goes to `analysis/<id>.json` on the `replays` branch.
- **Principles**: `knowledge/tactics.md`, ids cited by findings, rulings and situation cards (section 14).
- **Denning's verdicts**: `data/review_labels.json`, applied in `rules.py` and `fights.assess`.

## Known limits
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
