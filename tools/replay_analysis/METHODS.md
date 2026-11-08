# How concepts are measured in replay data

Working notes for Claude: the analysis framework, where everything is stored, and how each concept on the GvG tactics
page is detected in gvg.report replays. The goal is not counting deaths: it is knowing what game state caused each
fight, what the fight caused, and what the best play was in that situation for those builds (tactics `W6`, `W7`).

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

**Built (step 4, the flag chain, node `flag_answer`):** one row per answer to an enemy capture (306 in 27 matches);
the result is how many seconds slower than possible the answer was (the flag model's ETA at the enemy's capture);
causes: runner (line, Mes/A or not, dead at the enemy's capture, distance to spawn, a runner already waiting, runners
used so far), the trip (enemies on the route), the carry (damage taken, pushers, hand-offs), the fight meanwhile (own
and enemy deaths during the answer, own players fighting, own splitters), numbers, morale, flag lead, strength.
Held out: typical error 17 s against 27 s for the median, 67% of the spread explained. First readings: each hand-off
adds time (2 hand-offs about +26 s, 3 about +50 s); enemies on the route up to +17 s; each own death during the answer
about +15 s; enemy deaths during the answer also slow it (+8 to +17 s: a team killing isn't running); a pushed
carrier up to +9 s; a runner already near its spawn about -6 s; stronger teams about 3 to 4 s faster.
Deaths also carry `before_time` and `death_set` (holding its lowest-health weapon set), for Denning's `K14`.

Flag chain revised with Denning (`F33` to `F35`): drops are classified (quick hand-off within 5 s, forced = the
carrier hit or dying, parked = lying 5 s or more, and parked in the own base: a team deciding not to run); the flag
model uses each runner's measured carry speed (speed skills); "possible" is read before the own capture. Revised
readings: seconds parked are the largest cause (30 s parked about +30 s, 60 s+ about +50 s); a quick hand-off about
+5 s; a forced drop about +16 s. Typical error 16.8 s, 68% explained.

**Built (step 5, pit NPCs and Lord damage):** while enemies are in a team's pit (every 3 s): `npc_loss` (a pit NPC dies
within 15 s; 3,236 moments, 618 losses; held out AUC 0.801 against 0.736 for attackers and defenders alone) and
`lord_damage` (Lord damage in the next 10 s; R squared 0.34 against -0.13; a usually-zero result, so judged on spread
explained as well as typical error). Causes: attackers and their measured Lord damage per second, attacker and
defender healers, defenders in the pit and elsewhere, time in the pit, knights, archers and Bodyguard alive, damage on
and healing of the NPCs, res timer, minute, strength. First readings: defenders present is the strongest cause of both
(none in the pit: NPC loss +37 points, Lord damage +168 per 10 s; 7+: -40 points, -145); a dead Bodyguard +91 Lord
damage per 10 s; no defending healer +91; attackers' measured Lord damage per second up to +76; the longer attackers
stay, the more damage reaches the Lord (2 minutes: about +58).

Pit lines from Denning (`P9` to `P11`): knights first; a full pit loads the monks (more targets, knights balled up in
area damage); two monks on the push side against a full pit; attackers leave before the defenders' res. Added: area-
damage skills on the attackers (kept in `lord_damage`, where it helped; held back from `npc_loss`, where it didn't:
`HELD_BACK` in nodes.py) and pit NPCs alive as targets.

**Built (step 6, the usual play, `usual.py`):** every decision point's outcome as the change in win chance over its
window, from a win model fitted without that match; choices refined by what the players did; the usual play in a
situation = the most common choice among the 15 most similar decisions in other matches; each choice's effect against
the most common one, adjusted for the situation (one readable number per choice), with a 90% range from resampling
whole matches; unusual choices listed. First clear readings (30 matches): power play held instead of pushed about -4
points; with the enemy's boost 30 s away, not running and falling back about -12; after a wipe, taking the flag
instead of pushing the pit about +11 (12 cases; a candidate to check). 24:00 decisions: 13 so far, not enough.

**Built (step 7, values, `values.py`):** every result priced in win points for the team it happened to: deaths (all,
healers and others, by time down), pit NPCs by kind, captures and boosts. Two measures, both from a win model fitted
without that match: the result (how the match ended against the model's expectation 5 s before, less the average gap:
data, and it includes what the event usually led to) and the model's view (its change over 30 s). Where they disagree,
the win model's curve is suspect. 90% ranges by resampling whole matches. Causes priced through them: a node model's
change in the result's chance (at its real rate) times the result's value. Flag and Lord nodes wait for a measured
value per second of flag answer and per point of Lord damage. Written to data/model/values.json and
knowledge/values.md; section 8 of the learning report. First reading (30 matches): a non-healer death about -6 (clear),
a healer death about -1 (unclear), a capture +2 (clear), a boost +5 (not yet clear), an archer -4 (clear); for knights
and Bodyguards the result is negative or flat while the win model says +6 to +8: the backwards curves confirmed as the
model's error, not the game's.

The usual play now also compares decisions between similar builds (`usual.AXES`: spike, shutdown, knockdowns,
defence, sustain, own and enemy): build axes always count in choosing similar decisions; they enter the situation
adjustment from 150 decisions of a kind (`BUILD_ADJUST_FROM`); and each choice's raw difference is split by own build
(spike or not) where each cell has 10 or more cases (`INTERACT_MIN`). Situation extras per kind (`SIT_EXTRA`): after a
wipe, the margin to reach the enemy pit before its res; at the boost clock, the 30 s death difference and main-team
numbers.

Per-player skill flags (`buildfeat.player_flags`: snare, interrupt, knockdown, speed, self defence, self heal,
condition and hex removal, strip), because one skill can change the right play (`B23`). First use: split answers
(`decisions.splits_in_base`) record the response (collapsed, defended without a collapse, missed), split size, the
first defender's snare and interrupt, and the attackers' self defence; `usual.SPLIT_BY` splits choice effects by the
defender's snare. Energy is not estimated (Denning: too large a build for what it adds). The holding defender is the
first not collapsing from main; collapsers are read apart. Collapse cost (`decisions._collapse_away`,
`usual.collapse_cost`, learning report section 7): for each collapse, the collapsers' time away from the main group
(last second in it before reaching the split, first second back; capped at 180 s), whether they died, and what the
main fight lost meanwhile (`swing`: deaths, captures, flag lead, NPCs, DP), grouped by time away, before and from
20:00, and kill or no kill.

**Build order:** (1) phases, allocation per phase, plans and jobs (built); (2) capacities per group per phase,
measured (built); (3) first node models: deaths and kill conversion (built; expected-for-matchup baselines come with
the matchup features at 60 matches); (4) the flag chain (built: `flag_answer`); (5) pit NPCs and Lord damage (built:
`npc_loss`, `lord_damage`); (6) usual-play comparisons (built: `usual.py`); (3) expected-for-matchup baselines and the first node models (deaths, kill
conversion), tested on the 30 matches; (4) the flag and boost chain; (5) pit NPCs and Lord damage; (6) usual-play
models and decision comparisons; (7) learning report sections with "why" chains for the biggest moments, and the
questions where the data and the map disagree. Slow training continues throughout.

## The model as built (batch 0)
- `strength.py`: team strength from every stored result (1,737 matches, 71 guilds), Bradley-Terry with a 60-day
  half-life, rated only from results before each match; unrated guilds use the ladder gap (never 0). On later results
  it predicts 82% of winners (log loss 0.417), better than the ladder (81%, 0.473). The in-match model has to beat
  this to show it understands play rather than who the better team is. Since ENGINE 17 the baseline is the blend of
  the fitted and lineup measures (see "Data integrity, the Lord, strength").
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

## Data integrity, the Lord, strength and the review of 2026-11-06 (ENGINE 17)
A review of the engine against its goal found three measurement problems and several missing steps; all were built
before any refit (Denning).

**Data integrity** (`integrity.py`; `python3 integrity.py` lists every match, `data/model/integrity.json`):
- Length: the match ends at the first Lord death, else at the later of the recorded length and the last event.
  RACK v hdm (1f65fd3b) was stored as 2:30 but runs to 17:18; the engine had cut it there and learned a "stomp".
- Pit roster: NPCs only appear in a replay once something touches them, so an untouched pit looked empty. Winners
  "lost" their Bodyguard in 19 of 30 matches (losers 1) and showed fewer than 2 knights in 13 (losers 2): the
  backwards knights and Bodyguard curves of batches 0 and 1 measured whose pit was attacked, not tactics. Every pit
  now starts with the standard roster (Denning: 2 knights, 2 archers, 1 Bodyguard, 1 Guild Lord; a third archer on Isle
  of Solitude, map 542); NPCs never seen are added as alive all match (`state.MapGeo._fill_roster`). Archers beyond the
  roster near a pit count as outside archers.
- Lord damage: a Lord that died with no recorded damage means the attackers' Lord damage wasn't observed (OG v cope
  29b7eca0, Men v RACK 45cf6756); that team's Lord damage and the Lord nodes are left blank, not zero.
- Exclusion: matches with problems that can't be repaired leave training (`integrity.usable`, used by the win model and
  the node models); none so far. The learning report opens with a data-integrity section.

**The Lord** (`lord.py`): 28 of the first 30 matches ended with a Lord kill, only 2 at 28:00. Health is rebuilt second by
second from damage and healing on the Lord, max health +1% per boost, and regeneration as Denning gave it: 10 per
second always, plus an out-of-combat part once he hasn't been hit for a few seconds, +2 rising to +10 per second. The
delay and the rise are measured (`benchmarks.py regen`, `data/benchmarks/lord_regen.json`: the pair that best puts
the rebuilt health at 0 when Lords die, with no surviving Lord reaching 0), and so is whether the Amulet of
Protection's cap still has to be applied to gvg.report's recorded damage: applying it made the rebuilt health at death
much worse (median 629 against 332), so the recorded damage is taken as already capped. First reading: delay about
10 s, +2 every 3 s (many nearby pairs fit equally; the median error at death, 332 health, says some Lord damage is
not recorded). Scoreboard: `lord_health`, `lord_exposed` (Bodyguard and both knights dead), `lord_damage_taken_60s`.
Node `lord_kill` (nodes.py): while enemies are in a pit, the Lord dies within 30 s. Win-model variables
`lord_health_diff`, `lord_exposed_diff`.

**Strength** (`strength.py`, `lineup.py`, `context.py`): three measures, each time ordered (only results before the
match), blended by how well they predict later results (`strength.json` "blend": logistic fits of every combination on
the earlier two thirds of the matches after the first 300, tested on the latest third; replays left out):
- ladder: the in-game ladder rating gvg.report recorded with each match;
- elo: gvg.report's own guild Elo (Denning: far better than the ladder), rebuilt in time order from the stored results
  with its published rules (tournament-elo.v2: start 1500, K 32, 21 days idle then -50 a week to 1500; tournaments
  only). Checked against gvg.report's current table (`data/gvgreport/elo.json`): mean difference 23.5 points over 68
  guilds. Today's table itself is never used for training (it includes later results);
- fitted: the Bradley-Terry guild rating;
- lineup (Denning): the eight players who played, characters grouped into people by `data/aliases.json` (Denning's
  assignments plus gvg.report's player directory, merged by `tools/gvgreport/merge_players.py`). Two measures
  tried, an opponent-adjusted rating and a shrunk win rate, each with MAT results counting 1 to 8 times as much; step
  size, MAT weight and scale chosen by log loss on later matches (`lineup.json` keeps the grid). First reading: the
  shrunk win rate predicts best (log loss 0.418 against 0.433 for the rating); extra MAT weight barely helps (x1.5 best,
  x1 equal) and more than x2 hurts, even when tested on MAT matches alone.
- Blend reading with gvg.report's player groupings and the rebuilt Elo: fitted + lineup predicts the latest third
  best (log loss 0.3115, 89%), lineup alone 0.313, Elo alone 0.399 (better than the ladder, 0.437, worse than the
  fitted rating, 0.346); adding the Elo to fitted + lineup changes nothing (0.3115), so its weight is 0 for now and it
  is retested at every run. With gvg.report's groupings the lineup measure improved (0.418 to 0.403 on all later
  matches) and MAT x2 is best, though x1 to x3 are within 0.001. The model's `strength_gap` is this blend.
- Context priors (`context.py`): build-archetype matchups, archetype by map and archetype by flux, measured on every
  stored result with strength as a fixed offset (antisymmetric features, ridge penalty chosen on later matches). First
  reading: no penalty beats strength alone on the latest third (0.3806 at best against 0.3802), so the prior is off
  (0 points) and retested whenever results are added.

**Fight state** (`fightstate.py`): expected deaths per team in the next 10 s, the sum of every live player's death
risk from the deaths node, always from a model fitted without the match (6 groups). Win-model variable `fight_state`
(enemy minus own) and a situation control in every usual-play comparison (Denning `D4`). Built by `learning.py` before
the tables.

**Other new variables**: hexes on a player and on its team's live healers (deaths and kill_conversion nodes; replay
hex intervals); map shape (`map_flag_run` = Y, `map_pit_to_stand`, `map_bases_apart`) and flux flags in the win model,
staged with the build variables (fixed for a match).

**Checks on the comparisons**:
- Pre-trend (placebo) test in `usual.py`: each choice's comparison is repeated on the win-chance change in the 30 s
  BEFORE the decision; a clear difference there means teams making that choice were already sliding or rising, so its
  effect is partly who chooses it ("ALREADY DIFFERENT BEFORE" in the report).
- The honest test reports matches lasting 15 minutes or more and matches even on strength (gap under 200) apart, and
  the gain over strength alone with a 90% range from resampling whole matches.

**Discovery built** (`discovery.py`, learning report section 7): leverage (how much of the spread in win-chance change
the choice explains beyond the situation, per decision kind) and behaviour clusters (each decision's response, the share
of players by line in each action, grouped by k-means with the clearest k; groups no named choice covers are marked
UNNAMED for Denning to name or reject).

**First effect of the fixes on the node models** (checked, not saved): with the full roster, `npc_loss` still ranks
moments better than attackers and defenders alone (AUC 0.786 against 0.755) but no longer beats them on log loss;
`lord_damage` still adds (36% of the spread explained); `lord_kill` is no better than attackers and defenders yet
(AUC 0.96 for both: who is in the pit nearly decides it).

## Training batches 2 to 5 and why chains (2026-11-06)
- Batches of 6 random replays (Denning); 53 matches after batch 5. Learning reports gained: a data-integrity section,
  the placebo (pre-trend) check, choice effects split by fight-state thirds (`usual.FIGHT_SPLIT`, thirds from the data),
  close-game and resampled accuracy, leverage and behaviour clusters, a detailed snapshot (`snapshot.py`) and why
  chains (`why.py`).
- Correction logged by Denning: `lord_damage_diff & minute` (Lord damage only decides at 28:00). Tested each batch.
- Why chains (`why.py <id> <m:ss>` or `why.py top N`): result and worth (win model without the match, with the
  variables that moved it), mechanics per death (deaths node without the match, the contributions that raised risk most,
  a few seconds before), setup (the phase before: groups, jobs, numbers, capacities where the deaths came), the decision
  before (with the usual play's value), context. First test (batch 5) showed the mechanics step stops at "health was
  low" (a symptom), fight consequences overlap the next fight, and the decision step is too coarse; the fixes are listed
  in docs/HANDOFF.md ("Next session: fixes to do").
- Fixed: `episodes.flag_cycles` could loop forever on two carriers passing the flag back and forth in one recorded
  second (BcS v yM b88983e3).

## Forensics, event explanations, the cache and match status (2026-11-06)
- **The standard for an answer** (Denning): every "why" question is answered with a measurement, placed against the
  same role or situation in every stored match, never with a guess. The four examples that set the standard are below
  ("Answer exemplars"); new event kinds are built to answer questions of that kind and depth.
- **Forensics** (`forensics.py`; benchmarks `data/benchmarks/forensics.json`, rebuilt with `forensics.py bench`): the
  questions behind a death, over the 20 s before it: position (nearest allied healer, allies and enemies in casting
  range, nearest enemy, front of its team), prots (every prot and heal cast on it with timing against the burst: pre-prot,
  reaction, late; landed, interrupted, cancelled; what each prot can act on from the skill data: blocks act on attacks
  only, damage reduction and heal-on-hit on all damage, knockdown immunity on knockdowns; allied prots ready and in range
  but unused, with what those healers were casting instead; each knockdown with whether immunity was up and who had it
  ready), healers under interrupt pressure (interrupts, knockdowns, Daze, hexes on the team's healers), damage off
  shield sets (damage taken while holding a set with no shield and not casting; a shield's 16 armor stops about 24% of
  armor-respecting damage, `knowledge/armor.md`), both teams' damage output (per second, concentration, armor-ignoring
  share, spikes), peel (snares, Blind, Weakness, interrupts, knockdowns or hexes the victim's team put on its attackers,
  and the longest each attacker was left free; damage on the attacker is reported but is not peel), casting (each cast:
  finished, interrupted, "hit while Dazed", cancelled; enemy interrupts off recharge and in range, bow range from the
  bow type; Daze), conditions (who, from how far, the attacker's pressure, the victim's set, removal and removal on its
  own bar). Verdicts come from the benchmark's 20th and 80th percentiles for the role (`BENCH_CUT`), provisional until
  rulings calibrate them. Hits recorded without a skill are named from the attacker's cast finished within 1.5 s.
- **Event kinds** (`events.py`): `flag` (a team going from up to down on flags: captures against the fastest possible,
  every run with the control put on the runner, the stand fight's output on both sides, the forensics of the first
  deaths, the cascade), `power` (a power play without a kill: the fight's shape every 5 s, the enemy group's distance to
  its others, own damage and uptime against the benchmark, the enemy's healing, prots and knockdown immunity, pressure
  on its healers, snares put on retreating players), `spike` (a spike the target survived: every hit with its skill and
  time, landing spread and share inside 1 s against spikes that killed and spikes survived, `data/benchmarks/spikes.json`
  from `events.py bench`, pre-prots up, everything cast on the target, control on the spikers, the target's set and
  health line), `npc` (pit NPCs lost: the split, the defenders and their latency, where the rest of the team was), and
  `split` (a split and its answer). `events.py find <kind>` lists the biggest events of a kind. Why chains (`why.py`)
  now explain what dropped the health with the forensics, and "why, in short" names the findings that stand out. The
  learning report answers the TQs (below) with these; why.py and `events.py <kind>` stay available for any other event.
- **Cache** (`cache.py`): every "without this match" model (win model, node models) is fitted once per training set
  and engine code, saved, and shared by the learning report, values, usual play and why chains (before: each layer
  refitted its own, so a report refitted the same 53 models several times). Each match's prepared data (analysis,
  match tables, node rows, value events) is saved keyed by the engine code it was built from (found automatically from
  the imports) and the data files it reads, so a stale entry can't be read; tables are also keyed by the fight-state
  predictions they read. `cache.py warm` builds everything for the current batches in parallel; `cache.py sync
  pull|push` keeps prepared data on the `cache` branch between sessions. Held-out models stay in the session.
- **Speed, measured 2026-11-06 (61 matches, 2 cores):** a win-model fit 12 s, a deaths-model fit 42 s, one win-model
  validation 70 s. A batch used to cost: rebuild prepared data after an engine change (about 4.5 min), one held-out win
  model and one deaths model per match (122 fits, 27 min), then the learning report (16 min, of which about 7 min was
  the candidate-variable tests, one full validation each). Changes: held-out models now come from 10 fixed groups of
  matches (`cache.FOLDS`; each match is still explained by a model that never saw it; leave-one-out 78.2% accuracy and
  log loss 0.601 against 10 groups 77.6% and 0.546 on the same matches, so accuracy holds), deaths models are fitted
  only when a why chain needs them, and candidate tests run side by side. Cache rebuild after an engine change: 32 min
  down to 5 min. Set `FOLDS = 0` to go back to leave-one-out.
- **Side by side** (`parallel.py`): each node's held-out folds and final fit, and the win model's honest-test folds,
  run on every core in fresh processes (identical results, checked on all six nodes). On 2 cores: node step 6.1 to 4.9
  min, the win model's honest test 70 to 38 s.
- **Train batch on GitHub** (`.github/workflows/train-batch.yml`, 4 cores, pinned library versions in
  `train-requirements.txt`): optionally picks and fetches random matches, adds the batch, analyses, builds the
  held-out models, writes the learning report, saves the cache and commits the results to main. Start it from the
  Actions tab or with `gh api -X POST repos/itsha12/gvginfo/actions/workflows/train-batch.yml/dispatches -f ref=main -f
  'inputs[pick]=6' -f 'inputs[add_batch]=yes' -f 'inputs[note]=...'`; then pull main and read
  `data/model/reports/latest.md`. Runs on GitHub, so it doesn't use the chat's time or usage.
  Split across machines (session 4r): job "prepare" (pick, fetch, add the batch, analyse, held-out win models,
  fight-state predictions) hands a git patch and its cache files to six "part" jobs that run side by side
  (`learning.py part main` = honest test, curves, discovery screen, surprises, rulings, usual play, values measured;
  `part learned` = event layer and learned nodes (the causal map); `part cands` = candidate variables; `part nodes:<list>` = the node models over three machines),
  then "finish" joins them and runs what reads the node models' files (values priced, the TQs, the snapshot) with
  `learning.py finish`, saves the cache and commits. `learning.py` with no argument still runs the whole report on one
  machine, same text. timings.json keeps each part's wall time under "split". A section added to the report must be put
  in one part (PART_SECTIONS, or finish if it reads files another part writes) and in ORDER.
- **Match status** (`status.py`, `data/model/match_status.json`): per match, its batch, engine version, review entry,
  commentary sources and their state (pending, checked, done), Denning's rulings, the events whose why was walked
  through, and notes. `status.py sync` rebuilds the derived fields; `status.py mark` records the rest.

### The TQs (Denning, 2026-11-07): what to answer after every batch
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


### Answer exemplars (the four questions of 2026-11-06)
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

## Rulings after batch 9 (Denning, built 2026-11-07)
Sixteen of the seventeen proposals from the batch 9 review approved and built as one engine change (item 10, links
changing status only after two batches in a row, declined: links keep changing status batch by batch).
- **Win model** (`model.py`, `data/model_corrections.json`): `lord_damage_diff` has no curve of its own (`main_drop`;
  its pair with the clock stays); build-fixed values (Lord damage per second, spike build) never pair with morale
  (`no_interaction`); `down_diff_s` can only rise (`direction`); `spike_killable_diff` gets the cap the data picks
  (`cap_test`, options 10, 15, 20, 25 points or none: `model.cap_test`, run by `cache.py warm` before the held-out
  models, the choice and every option's held-out log loss in `data/model/cap_choices.json`, a hash input of the
  held-out models).
- **Calibration by minute** (`model.calibrate`, run by `cache.py warm` after the held-out models): every training match
  predicted by its group's held-out model every 15 s, grouped by minute band (0-6, 6-12, 12-18, 18+) and predicted
  chance, against how often those teams won; thin cells lean on the model's number (5 matches' worth) and each band is
  made to rise with the prediction. `WPModel.explain` reports the calibrated chance (the contributions stay as
  learned), so values, the usual play, why chains and the TQs all use it; `raw_chance` gives the model's own number.
  Pooled cells give flat stretches, where small changes read as none.
- **Usual play** (`decisions.py`, `usual.py`): the choice is what the team did in its first 5 s (`first_actions`,
  movement threshold scaled to the window); the 20 s actions stay as context.
- **Power plays** (`fights.windows`, `decisions.py`, `lnrows.py`): pushing, pressure and the power-play node's damage,
  enemy prots and healing, spikes and Blind are read up to the first kill (the whole window without a kill);
  `window_s` stays the whole window.
- **Values** (`values.py`): each event against matched moments without it (same 2-minute band and 10-point win chance
  band, no event of that kind in the window; the band alone when a cell has under 20 moments). Context (strength, build
  skill counts, flag lead, morale, the clock, the res timer) is never priced as a cause (`context_only`).
- **Snapshot** (`snapshot.py`): winners against losers compared at moments when a held-out model gave the team 35 to
  65%, with every moment beside it, labelled as including who was ahead.
- **Lord damage node** (`nodes.py` `TwoPart`): chance of any Lord damage in the window (classifier) and the amount when
  there is some (regressor on log(1 + damage)); typical error from the middle of the predicted spread against the
  median, spread explained from its average against the average. Number nodes now "add" only if no worse on typical
  error and better on the spread explained (flag answer too).
- **Kill-conversion node**: `attackers_blinded` is seconds the burst's physical attackers spent Blind, 3 s before to
  3 s after the burst.
- **Reworked learned nodes**: flag swing gets the flag model's readings (each team's ETA, carrying now, can capture
  before the boost); capture speed gets control on the runner in the first 10 s (K.11); split effect gets the
  defenders' pit NPC value and free defenders at entry (S.scoreboard -> R.5, a Claude hypothesis). Flag swing and
  capture speed use a robust loss (pseudo-Huber, delta = the rows' median absolute deviation, fitted on the result
  less its median: the library's default diverges); split effect uses fewer bins, larger leaves and more smoothing.
- **Forensics position** (`forensics.py`): judged on the last N s before the death (nearest healer, nearest enemy,
  allies and enemies in casting range, front share), N chosen by `forensics.py bench` from 3, 5 and 8 s as the window
  whose nearest enemy and enemies in range best separate deaths from fight moments without one (AUC; in
  `forensics.json` "position_window"); the window's medians stay as context. The shortest window partly measures the
  kill itself (attackers close in on a dying player); read the AUCs with that in mind. Rebuild with the Train batch
  input `rebuild_forensics`.
- **TQs** (`tq.py`): a what-if is marked unreliable when a change takes a variable outside the node's training range,
  or when a ladder (one more, two more defenders) stops moving the same way; unreliable readings are shown but kept
  out of the confidence and the fixes. TQ 4 tells a split's own NPC kill from a wipe's conversion and judges the
  split's answer only on the split's kills.
- **Train batch**: every job may run 3 hours.

### After the batch 9 rebuild (Denning, 2026-11-07)
- **Calibration, third form** (after the second rebuild): per minute band, cells shrunk toward the model's number in
  thin cells and pooled where they run backwards, then joined by straight lines between the pooled blocks' middles
  ("knots"), blended by minute between band middles; beyond the outer knots, the outer knot's value (each is a
  pooled block's middle, so only predictions more extreme than that block's average read flat; lines to 0 and 100, and
  then carrying the end segments on, overrode the ends where most rows sit). As accurate as the first (pooled lookup) form, never flat, no jump at a band edge. (The second form, a shift and a slope per band, missed some ranges: 12 to 18 min, 93% predicted,
  92% won, calibrated 77%.)
- **flag_lead** forced to rise (Denning): the curve was small and ran backwards at both ends. Forced, its deficit end is
  flat from about -129 to -30 s (-3.3 points), so TQ 1 still reads 22 s saved at -78 s as +0.0: the win model credits
  flag position there through the stand, knights and morale, not the lead itself. Pricing saved seconds needs the
  chain through the flag-swing and run nodes (step 4).
- **Pair test** (`pair_test` corrections, tested together with the cap tests by `model.cap_test`): morale (difference
  and total) with the map's geometry, allowed against blocked on held-out matches; blocked only if that predicts
  better (`cap_choices.json` "pairs").
- **What-ifs from a pairing** (`tq.what_if`): a reading that runs against the changed variables' own curves is marked
  "[from a pairing" and kept out of the fixes and the confidence, like unreliable readings.
- **TQ 4**: a split that never entered the base has its first defender counted from the split's start, without the
  base benchmark.
- **Split depth** (Denning's hypothesis, map node P.20 -> R.1, collapse node, each reading also tested alone): the
  split's nearest member's distance to the defending pit at the first defender's arrival, and its median over the split.
- **K14, S32** (tactics): a monk's death before the res may be deliberate, but that turns on energy, which the replays
  don't record; a quick collapse that fails to kill fails twice (no kill, and the split stays in the base).

## Commentary and comms: claims and the variables they suggest (2026-11-06)
- Transcripts are never stored (public repo). Each is matched to its match (players' names in the transcript against the
  rosters), lined up by anchors (kills, captures, boosts, NPC losses: `timeline.py <id> --people` lists them with each
  character's person), and turned into paraphrased claims in `data/commentary/<source>.json`: approximate time, kind
  (plan, read, call, reason, prediction, diagnosis, technique), speaker's role, tactics ids, the variable it suggests,
  and the engine's check (agrees, disagrees, partly, can't measure) with evidence.
- Denning: the variables the comms point to are the most important thing they give. `comms_vars.py` measures each one in
  every stored replay against the outcome the speaker said it drives, within strata (local numbers, number of spikers),
  with 90% intervals from resampling whole matches (`data/benchmarks/comms_variables.json`). Supported variables go into
  the model they belong to (win model candidates in `features.CANDIDATES`, node variables) and onto tactics as
  **OG comms:** lines with the data; contradicted or unclear ones stay recorded there so they aren't re-proposed without
  new evidence, and become open questions.
- First six OG matches (batch 6): supported: a group with no healer loses players twice as often (`P12`), merging 7+ for
  a pit push kills 2.5 times as often (`P13`), hexed spikers halve spike kills (`X9`), players with 15%+ death penalty
  die about 4 times as often in fights (`K17`, partly selection), turtling teams usually lose (`L11`, win-model candidate
  `turtle_diff`). Not supported or unclear: "solo monk" alone (`Q16`), Shell Shock and enchantment strips on the spike
  target, tight groups dying more (deaths are the wrong outcome: area damage taken is the right one, to build).
  Can't measure: gate control, terrain and line of sight, energy, call timing.
- Made into model variables (Denning, after the first six): deaths node `solo_healer` (a healer with no other own healer
  in casting range: Denning's reading of "solo monk"; measured on the monk's own death, 3.4% against 1.1% per 10 s),
  `group_no_healer`, `own_morale` (the player's own death penalty or boost), `allies_in_area` (allies within 322) and
  `healers_in_range` now excludes the player; NPC nodes `attackers_share` (share of the attacking team in the pit:
  merging); win-model candidates `footmen_diff`, `no_healer_groups_diff`, `solo_healers_diff` (and `turtle_diff`);
  values.py prices a footman lost and splits deaths by whether the team was boosted ("we can die for NPCs"); footmen
  are read from the replay's agents (`features.footmen`). Measured in comms_vars.py: area damage against spacing
  (unclear), spikes by weapon set (unclear), interrupts on the spikers before a spike (supported: 23% against 40% kills).
- Power play fix: a numbers advantage held in the own base or pit is a defence, not a power play (`fights.windows`
  records `where` and `at_home`; `decisions.power_plays` skips those). Found when batch 6's "power play without a kill"
  was One holding 8v3 in its own pit while turtling.
- Last three OG matches: OG v hdm (OG's spikes killed 0 of 15: hdm's healing and interrupts, `X10`), OG v Dz (footmen,
  out of heal range), OG v hold (a base race won by 0.3 s after OG healed its own Lord for 1,390, `L12`). Engine issue
  found there: the rebuilt Lord health had hold ahead, the reverse of the result (lord.py to check).

- Bounty's seven matches (session 4t, 2026-11-08): Apes v cope, 옷옷옷옷 v Book, OG v hold, Team v push, cope v hdm, True v
  One and BcS v Crew (replay fetched for it). 57 claims in `data/commentary/bounty.json`, each checked. Nick's five
  (same session): Men v Team, NwAy v SKT, xxx v Men, NwAy v Men, cope v Book (four replays fetched). 47 claims in
  `data/commentary/nick.json`.
- New measures in `comms_vars.py` (144 matches): `monk_focus` (groups hitting mostly healers kill in 19% of phases
  against 13%: contradicts "don't go after the monks", partly selection, tactics `K6`); `collapse_snare` (a snare carrier
  among 2+ defenders, Return not counted: a splitter dies 20% against 11%, supported, `S33`); `instant_overcap` (16% of
  captures are overcapped within 10 s; the capturing team lost more than it killed from the run's start to 30 s after,
  22% against 16%, supported, `F36`; partly the situation); `split_size` (3-player against 4-player splits into the
  base: a pit NPC taken 36% against 35%, unclear, `S38`); `scattered` kept as a measure only (Denning: Bounty spoke
  metaphorically). New lines `F36`, `F37`, `P15`, `S38`, `S39`, `O4`, "cycle" and "inaccuracies" under Language.
- Built (Denning's go-ahead, session 4t), one engine change and one rebuild:
  - `movepower.py`: snare power and speed power per player, from the skill data at the player's attribute rank
    (match data attrs, rank 12 when unknown): snare = slow fraction x seconds per use (capped at the recharge) x
    targets (adjacent 1.5, nearby or area 2) x uses per minute; speed = speed bonus x seconds per use x uses per
    minute; escapes = Shadow Step skills. Return is an escape, never a snare. Hex snares are checked against the
    replays (`movepower.py bench`, data/benchmarks/snare_measured.json, in the cache fingerprint): with 15+ uses the
    measured slowed seconds per use replace the formula (e.g. Siphon Speed 6.2 s per use against 13 by formula: hex
    removal). Crippled can't be measured (the replays record it only now and then), so condition snares keep the
    formula.
  - Learned nodes: run outcome (runner speed and escapes, enemy snare power within 1,300 of the runner), run defence and
    capture speed (runner speed, defenders' snare power near the runner), collapse and split effect (snare power of the
    defenders who actually came; splitters' speed and escapes), split chance (team snare, speed and escape power
    replace the skill counts), power play and fight outcome (healer focus: share of damage on enemy healers, P.1).
    New groups K.13 (mobility) and K.11 (control) in those nodes; the collapse node's old C.builds counts are gone.
  - Decisions: every decision record carries the snare matchup (own and enemy snare power of the live players, own
    speed power); the boost clock, enemy pickup and the new split_or_stay decision are adjusted for it and broken down
    by it in thirds (report "By snare matchup"); split in base carries the defenders' snare power. split_or_stay: every
    30 s from 1:00, a team not already splitting with 6+ alive either starts a split in the next 30 s or stays.
  - values.py prices captures overcapped within 10 s apart from those held longer (`F36`).
  - `buildfeat.FEATURES["snares"]` no longer counts Return.

## Steps 3 and 4 of the learned causal map (session 4t, 2026-11-08)
- **Step 4, chains from the node models** (`causalchain.py`): a result is traced back through the learned nodes. The
  result's node reads the moment with a held-out model (learnednodes.py now keeps each node's six fold models of the
  "all" variant and which fold each match was held out in; data in the cache under fits/lnode, keyed by
  learnednodes.py alone). Each variable's push = its curve at this moment minus its curve at its usual value (the
  median over every trained row of the node; the nodes are additive, so the pushes separate). A variable that is
  another node's result is followed back (flag lead -> the flag swing before; own deaths and numbers -> the fight
  before; a split answer's latency -> the split-answer node) when it sits on the bad side of its usual value, the two
  biggest groups at each link, back to the last reset or 3 min, at most 4 links deep; a fight read from the enemy's
  side has its "enemy_" numbers read as this team's own. Fixes: any play variable (P, K, A.mesa_free groups) among the
  pushes, set to its usual value; the node is read again and the change carried link by link (seconds carry as they
  are, and a flag swing keeps a carried lead; a fight's chance carries as that share of a lost fight's deaths, the
  median over every trained fight, read at full size and scaled because the curves are in steps) to the result's
  node, priced with values.py (a fight = the deaths of its losing side; flag seconds through the held-out win model).
  Shown in each TQ beside the rule-based chain (chain.py) while the two are compared; it replaces the rules once
  Denning approves. Context (strength, builds, clock, map) is never a fix.
- **Step 3, discovery** (`discover.py`, workflow "Discovery", one node per machine): every variable the engine measures
  about a team at a moment (the win model's state table, prefix s., and the build and matchup features with snare,
  speed and escape power, prefix b.) is joined to each node row (same team, the 5 s state at or before the row) and
  tested on unseen matches with the node's own 6 folds. Screen: a one-variable glass-box curve fitted on top of the
  node's held-out readings (its starting score), gain = held-out loss without minus with. Confirm: the best 6
  screen gainers per node refitted as a link test (the node plus the variable against the node). A discovery =
  confirmed gain more than twice its spread and up in at least 5 of 6 folds; held for Denning's approval
  (data/model/discovery.json, knowledge/discovery.md), never added automatically. The page states how many screen
  passes chance alone would give. Tested here on the collapse node (92 variables, 49 s): no discovery yet; closest
  morale difference and fight state (not clear).

## Runner speed, who carries, approved discoveries, the speed-up (session 4t, 2026-11-08)
- Runner speed (Denning): the runner's speed skills set the minimum time required to capture. scoreboard.py's carry
  speed per player = the faster of its measured full carries and the average carry speed (205) times one plus its bar's
  speed bonus (movepower.speed_bonus: speed power / 60, capped at the bar's biggest single bonus, since boosts don't add
  up). Every flag ETA, response, flag lead and "slower than possible" follows. The run nodes' raw runner_speed is
  replaced by min_capture_s: seconds the carrier needs at least from where it is, at that speed.
- Who carries (Denning: capping on a warrior, a midline, a dervish or a monk is a strategic decision): runner_class
  (common.runner_class, the carrier's primary profession, coded 0 to 9) in the run outcome, run defence and capture
  speed nodes (P.10), and a new decision, runner_choice (every fresh run from the spawn; the usual play compares
  carriers in similar situations and by snare matchup).
- Approved discoveries (Denning, all as suggested): state variables as context (S.scoreboard) in the fight, flag
  swing, run, power-play and split nodes; snare skill counts on the run nodes (enemy snares on run outcome, own snares
  on run defence) and the defenders' prots on split effect (C.builds); Deep Wound on split effect left for more
  matches. Joined onto the rows from the state table and build features (lnrows.APPROVED).
- Chains: the node-model chain (causalchain.py) replaces chain.py in the TQs. A cause or fix must sit at least a
  quarter of the variable's spread (interquartile range over the node's rows) from its usual value.
- Speed-up: Train batch now runs fetch -> four shard jobs (cache.py shard k 4: analysis, node rows and event-layer
  records for every 4th match) -> prepare (merges the shards' cache files; analysis then takes 15 s) -> four rows jobs
  (cache.py shard_rows k 4: the learned nodes' rows, which need the event-layer values from every match) -> parts ->
  finish. First sharded run (full rebuild, before the rows shards): shards 2 to 4 min, prepare 11 min (9 of them the
  win model's tables, held-out fits and calibration), the learned part 13 min (rebuilding every node's rows on one
  machine, slowed by recomputing each bar's powers per row: now memoized), finish 3 min; 32 min in all.
  Second run (with the rows shards): learned part 13 -> 4 min, but prepare 16 min (tables 5, cap tests, held-out fits
  and calibration 4, fight-state predictions for every stored replay 5) became the long pole. Third round (Denning,
  before the large pull): seven "tables" jobs (cache.py shard_tables: the fight-state predictions for one of the six
  groups and that group's win-model tables and value events; "extra" = the stored replays outside the training set,
  fightstate.build_group / build_extra, the same fits as build) between the shards and prepare; shards and rows jobs
  now 8 machines each.

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

## After batch 10 (Denning's answers, 2026-11-08)
- **split_diff moved into the win model** (features.py VARIABLES; it was a candidate since batch 1). Held-out log loss
  0.314 to 0.307 in batch 10's candidate test.
- **Holds** (`common.is_hold`, `carry_progress`): Denning, an 8 Monk sometimes holds the flag without trying to cap. A
  carry of 10 s+ that does not end in a capture and never closes a quarter of the way to the stand is a hold. Holds are
  marked on every flag run (`hold`, `progress`) and kept out of run_outcome, run_defence, the runner choice and the
  runners table's capture rates (the table shows them as a column).
- **pit_npc_loss learned node** (R.5): the node model's npc_loss moments (nodes.py) read for the defending team, with
  defenders in the pit as play (P.11), healing on the NPCs (K.6) and damage on them (K.1). causalchain.start_npc starts
  from it (the last moment in the 15 s before the loss), so TQ 4 can price fixes.
- **Collapse context** (`common.split_context`): Denning, collapsing on a split depends on what the split can get
  NPC-wise, the death penalty on the split character and whether it can be killed. The collapse node gains split_dp
  (K.9), split_healers and split_self_defence (K.5), def_dps (K.1), def_npc_value (S.scoreboard) and split_npc_dps
  (C.builds); split-in-base decisions carry the same in their situation, so the usual play compares collapses in like
  situations.
