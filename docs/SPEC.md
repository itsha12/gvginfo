# GvG Info analysis engine: specification

This is the current state of the engine, not its history. Edits replace text; nothing is appended with a date. History
is in `docs/CHANGELOG.md`; Denning's definitions and decisions are in `docs/RULINGS.md` (cited here as R-nnn); what to
do next is in `docs/HANDOFF.md`. The generated structural reference (every fitted node, its rows, inputs and scores)
is `knowledge/model.md`, rebuilt by every Train batch run; this file explains the design that page reports.

## 1. Goal and the tests of it

Explainable in GvG language, white box, analyses matches, and makes GvG decisions better than an experienced player,
from data. In testable form:

1. Every number has a GvG name and a reading a player recognizes (the generated model page is the check).
2. Every model is tested on matches it never saw, by whole match.
3. A "better play" is a choice a team could have made at that moment, measured against what similar teams did in
   similar situations (the decision tier).
4. The engine's advice beats the usual play on held-out matches (the advice test, report section "Does the advice
   work?"), and beats Denning's calls in the sealed blind test (R-274, R-284): a round of eight sealed picks (six
   random, two where the advice differs from the usual play) is added after every chunk and never refreshed; Denning
   answers and scores rounds on the site (Model > Blind test; `data/model/blind_tests.json`), each call priced by the
   mean win-chance change of teams that made that choice in the 15 most similar decisions, and matched against what
   the team did.

Nothing is a weight or a default unless it is measured or is a definition (R-series "Model and engine rules").
Definitions (what counts as a fight, a hold, a power play) come from Denning; values and best plays come from data.

## 2. Data

- gvg.report replays, trimmed, on the `replays` branch (`tools/gvgreport/replay_trim.mjs` documents the format):
  positions about once a second, skills cast with target and result, damage, healing, prevented damage, conditions,
  hexes, enchantments, knockdowns, interrupts, flag events, NPC events, deaths. No energy, no line of sight, no NPC
  positions, no intent.
- Matches count from 1 September 2026 (`common.TRAIN_FROM`); picks from 2 September (`common.PICK_FROM`). Team strength
  and lineup ratings use every stored result. Game facts measured from replays (flag spawns, Lord regeneration) use
  every replay.
- Integrity (`integrity.py`, inside `Match()`): length repaired, pit roster completed, unobserved Lord damage left
  blank, unusable matches excluded.

## 3. Measurement layers (deterministic, no fitting)

| Layer | Code | What it produces |
|---|---|---|
| Game state every second | `state.py` | positions, zones, alive, morale, groups, NPCs, carriers, stand |
| Scoreboard | `scoreboard.py` | flag ETA, response, lead, numbers, DP and spike threat, NPC value, Lord damage, archetypes |
| Episodes | `episodes.py`, `fights.py` | splits, runs, flag cycles, deaths with forensics, fights, power-play windows |
| Decision points | `decisions.py` | recurring moments, the situation, the choice made, the outcome |
| Event layer | `eventlayer.py` | strips, hex removal, hexes, Blind, peel, wrong casts, damage against the usual, spikes, runs, splits, power plays, captures |
| Pressure beyond damage | `pressure.py` | kiting, pre-kiting, degen, baited interrupts, offensive knockdowns, disables, cast prevention |
| Movement power | `movepower.py` | snare, speed and escape power per player (formula, replaced by measurement at 15+ uses) |
| Build features | `buildfeat.py` | what each bar causes and removes, matchup pairs, per-player skill flags |
| Death forensics and event accounts | `forensics.py`, `events.py` | the measured answers behind a death, flag swing, power play, spike, NPC loss, split |
| Benchmarks | `benchmarks.py` and `*.py bench` | Lord damage per second, regeneration, carry capture chance, flag spawns, forensics percentiles, spike spreads, snare seconds |

Thresholds that define terms live in `common.py` and are definitions (R-series). Every measured quantity is one of
five kinds, and the kind decides what a model may do with it (section 5):

- **Context**: fixed for the match (strength gap, builds and matchup, map, flux, period).
- **State**: the situation at a second (morale, flag lead, stand, numbers, Lord damage, clock, res timer).
- **Decision**: a choice a team made at a recognizable moment (section 6).
- **Execution**: how well the chosen play was carried out (damage against the usual, spike spread, interrupts and
  strips on the right targets, kiting, knockdowns on casters, wrong casts).
- **Concurrent response**: what the other team did during the same window (its healing, prots, kiting). Described,
  never a cause.

## 4. Fitted models: one tier structure

Every fitted model belongs to one tier, answers one question, and appears once. The generated model page lists them
with rows, positives, inputs by group and kind, held-out score against baseline, and the engine version that last
changed them.

### Tier 0: context
`strength.py` (fitted guild rating blended with the lineup measure, time ordered), `lineup.py`, `context.py`
(matchup, map and flux priors; on only when they beat strength on later results), `buildfeat.py`.

### Tier 1: state
The state table (`features.py`): one row per 5 s per team. The win model's variables. `fightstate.py` (expected
deaths in the next 10 s from the deaths node) is a state variable derived from a tier 3 node.

### Tier 2: decision nodes (`decisions.py`, `usual.py`)
Each recurring decision is a kind. For each kind: the situation (tier 0 and 1 at the moment), the choice (what the
team did in its first 5 s), and the outcome (the change in win chance over the window, from a win model fitted
without the match). The usual play in a situation is the most common choice among the 15 most similar decisions in
other matches; each choice's effect is read against the most common one, adjusted for the situation, with a 90% range
from resampling whole matches and a pre-trend (placebo) check ("partly who chooses it"). Decision kinds are in
section 6. A tier 2 answer is the macro answer: "was this the right call".

### Tier 3: execution nodes (`learnednodes.py` and `nodes.py`)
A small glass-box model per question, main effects only, held out by match (6 groups), inputs limited to the causal
map's links into it, each link's strength measured by refitting without it. Two code paths today (per-event rows in
`learnednodes.py`/`lnrows.py`; per-player or per-moment rows in `nodes.py`); one tier, one page. A tier 3 answer is the
micro answer: "given the call, what went wrong in carrying it out".

| Node | Question | Row | Code |
|---|---|---|---|
| fight_outcome | who wins a fight (play before its first death) | fight | learnednodes |
| power_play | does a power play of any size kill | power-play window | learnednodes |
| run_outcome | is a flag run captured (read at 5, 15, 30 s in) | run checkpoint | learnednodes |
| run_defence | is an enemy run captured, from the defending side | run checkpoint | learnednodes |
| capture_speed | how long an enemy capture took (defence read 10 s in) | capture | learnednodes |
| flag_swing | change in flag lead over the next 60 s | 20 s moment | learnednodes |
| split_chance | does a team start a split in the next 30 s | 15 s moment | learnednodes |
| split_answer | seconds to the first defender at a split in the base | split | learnednodes |
| split_effect | does a split in the base kill a pit NPC | split | learnednodes |
| collapse | does a split member die to the collapse | split | learnednodes |
| pit_npc_loss | does the defending team lose a pit NPC in the next 15 s | 3 s moment with enemies in the pit | learnednodes |
| deaths | does this player die in the next 10 s | player every 3 s | nodes |
| kill_conversion | does this burst kill within 8 s | burst | nodes |
| flag_answer | seconds slower than possible the answer to an enemy capture was | answer | nodes |
| lord_damage | Lord damage in the next 10 s while enemies are in the pit | 3 s moment | nodes |

Retired: `nodes.py npc_loss` as a fitted node (its row builder stays: the learned node pit_npc_loss reads those
rows for the defending side), `nodes.py lord_kill` (no better than "who is in the pit"), and the TQ what-ifs that used
`npc_loss` now read `pit_npc_loss`. `chain.py` (rule-based chains) is kept only for its run benchmark helpers;
`causalchain.py` makes every chain.

### Tier 4: the win model (`model.py`)
Glass box (Explainable Boosting Machine) on the state table with team strength as the baseline, staged complexity,
calibration by minute, corrections (`data/model_corrections.json`) each tested with and without. It values results in
win points (`values.py`) and prices every decision's outcome. It says who is winning, not why; the why comes from
tiers 2 and 3 through the chains (`causalchain.py`).

### The causal map (`data/model/causal_map.json`)
Describes only what is fitted: a node entry per tier 3 node and per decision kind, a link entry per input group,
with the measured strength and status (supported, not clear yet, rejected; Denning's links are never rejected without
his ruling, R-series). Concepts that are not fitted are kept in a waiting list in the same file (`waiting`), not as
nodes. Rendered to `knowledge/causal-map.md`.

## 5. Rules every fitted node follows

1. **Time order.** Every input is measured before the window opens, or at a fixed early point inside it (runs at 5,
   15 and 30 s; captures at 10 s; fights before the first death). Nothing measured over the window that the result
   also happens in is a cause.
2. **Kinds decide roles.** Context and state inputs are adjustment: they may be in every node so a play's effect is
   read at the same situation, and they are never a fix. Decision and execution inputs are the only candidates for
   "what should have been done" and "what went wrong". Concurrent response is not an input; it is reported beside
   the node's reading as "what the enemy did" (in the TQs and the query tool).
3. **Inputs the data can carry.** A node has at most one input per 20 events (the rarer class for yes/no nodes;
   rows / 40 for number nodes). Above that, inputs are dropped in this order until the limit holds: Claude's links not
   clear yet, Claude's links rejected, approved discoveries not clear yet, then Denning's links not clear yet (R-278).
   Supported links, and links Denning ruled to keep (`denning_keep` on the map; today P.21 kiting -> fight outcome,
   R-283), are never pruned. Dropped inputs go to the waiting list with the reason and return as the data grows.
4. **Selection check.** Every decision and execution input is tested against the same team's *previous* outcome of
   that kind in the match as well as the next. An input that predicts the past at least as well as the future marks the
   situation; it is labelled "marks the situation" on the page and in the report and is never offered as a fix. (This
   is the standing form of the "partly who chooses it" check.) Exception (R-282): an **allocation decision** (escorts,
   defenders in the pit, players on flag duty, split size and healers; `learnednodes.ALLOCATION`) keeps the label but
   may still be a fix, because it is a choice the team can change even though it persists through a match.
4b. **Perspective and kind by node.** The same count is a team's own choice in one node and the enemy's situation in
   another (escorts: the running team's decision in run outcome, state in run defence). `learnednodes.NODE_KINDS`
   fixes the kind per node, and every node on the model page says whose side its rows are read from.
4c. **Expected direction (R-285).** Every execution input carries an expected direction (`learnednodes.EXPECTED`:
   more disables should help, more damage taken by the runner should hurt). After each fit the curve is read against
   it; an input whose curve runs the other way is labelled "reads backwards: likely a reaction" (teams disable more
   when the kill is not coming, heal NPCs more when they are being hit), stays in the fit as adjustment, and is never
   a fault or a fix. The direction list is Claude's, to confirm.
5. **Status by data.** A link is supported when the held-out gain is more than twice its spread across folds,
   rejected when dropping it helps by that much, otherwise not clear yet. Near-line flips between runs are expected;
   the report shows status changes as a diff.
6. **No engine change between chunks.** Inputs are frozen for a run of chunks; proposals queue in the waiting list;
   one bundled engine change, then one rebuild compared against the reading before it.

## 6. Decisions the engine recognizes (tier 2)

Each kind has a definition (how the moment and the choice are detected: a definition, from Denning or marked Claude's
to confirm) and is compared by the usual-play method. Choices are what the team did in its first 5 s.

| Kind | Moment | Choices | Definition source |
|---|---|---|---|
| enemy_pickup | the enemy picks up its flag | run, hold, fall back, advance, fight | Denning |
| split_in_base | an enemy split enters the base | collapse, defend without a collapse, miss | Denning |
| power_play | a numbers advantage at main (any size, R: 8v7 counts) | push, hold | Denning |
| boost_clock | the enemy's boost is near | run, not running and fall back, not running and advance, fight | Denning |
| after_wipe | the team wiped the enemy | push the pit, take the flag, hold | Denning |
| late_game | 24:00 | positions and plan | Denning |
| split_or_stay | every 30 s from 1:00 with 6+ alive | start a split in 30 s, stay | Denning |
| runner_choice | a fresh run from the spawn | who carries (class) | Denning |
| offence_or_defence | a fight begins (first contact) | offensive (interrupts and casts on enemy healers: 40% or less on midline and frontline), defensive (60%+ on enemy midline and frontline), mixed; by the disrupting players' first 15 s | Denning (R-279) |
| eight_v_eight_or_flag | the enemy picks up or carries while own team has 7+ at main: a power play when not up on flags | commit all 8 (nobody on flag duty 10 s later), keep the flag game (a runner carrying, waiting or on duty) | Denning (R-279) |
| who_defends | a split enters the base | class of the first defender (Mes/A, frontline, 8 Monk or other healer, midline), and alone or with a collapse (someone from main within 60 s) | Denning (R-279) |
| npcs_or_dp | 3+ enemy players killed at or past their footmen (half or more of the kills inside their base or pit) | damage in the next 20 s on the pit NPCs (70%+), on the surviving players (DP, 30% or less), both | Denning (R-280) |
| play_for_28_or_lord | from 10:00 every 60 s, a team that has taken 1+ enemy NPCs (pit NPCs or footmen) | push for the kill (3+ at the enemy pit in the next 60 s), play for 28 (flags, defence, NPC and Lord damage without a push) | Denning (R-281); the 10:00 start is Claude's |

All thirteen are confirmed by Denning (R-279 to R-281); the usual play compares each choice against the most common one in similar situations. Behaviour clusters (section 8) are the way new kinds are found: at every
recurring state the eight players' actions are clustered, and groups no named choice covers are shown to Denning as
UNNAMED with example moments, to name or reject.

## 7. Explaining (tiers 2 to 4 together)

- `values.py`: every result (death, NPC, capture, boost) in win points, against matched moments without it.
- `usual.py`: each decision's choice effects (the macro answer).
- `causalchain.py`: a result traced back through the tier 3 nodes to the plays and the decision before it, back to
  the last reset or 3 minutes, the biggest two causes at each link; fixes are decision or execution inputs set to
  their usual value and carried forward to the result's value. Context, state and inputs marked "marks the
  situation" are never fixes.
- The TQs (`tq.py`, report section "The TQs"): after each batch, for the biggest flag swing, monk death, power play
  without a kill and NPC loss in the new matches: the account (forensics, events), how it got there (the chain), then
  two answers kept apart: **macro** (was the decision the right call: the usual play's choice effects at the decision
  before) and **micro** (given the call, what went wrong: the execution inputs that pushed the node's reading the wrong
  way, each against the role's benchmark), plus **what the enemy did** (concurrent response, described). Confidence
  from the evidence as before.
- The query tool (`ask.py`): a match and a moment in (a situation without a match is the next form); the data-favoured
  decision, the usual play, the margin with its range, the evidence (cases, nodes, benchmarks) and the execution
  faults out. The end product the rest of the engine serves.

## 8. Finding variables and decisions from data

- **Variable catalogue** (`catalogue.py`): every candidate variable generated mechanically from the replay
  schema as recorded thing x subject (own or enemy; team, group, role class, player) x filter (on healers, on casters,
  while Blind, by skill type) x window (before the window, first N seconds, per 10 s). Screened by `discover.py`
  against every tier 3 node on unseen matches, with the chance rate stated; a candidate is offered to Denning only
  after it passes in two discovery runs (R: 2026-11 review) and only if it is a decision or execution variable (state
  and build variables are already adjustment and are never offered). Of the catalogue's three forms, own_ and diff_
  (own minus enemy) are offered; enemy_ is the enemy's concurrent response, never offered, and shown beside an offered
  candidate as "what the enemy did" (R-286).
- **Behaviour clusters** (`behaviour.py`): at every recurring state, the per-player action vectors clustered; groups no
  named choice covers are UNNAMED decisions for Denning to name or reject. Leverage (how much the choice explains
  beyond the situation) says where attention goes.
- **Surprises**: the moments the win model was most wrong, listed in the report and fed to the catalogue screen first.

## 9. Reporting (`learning.py`)

- The learning report after each batch is a diff: data integrity, the honest test, what changed since the last batch
  (status changes, curves that moved beyond a quarter of their spread, inputs pruned or restored, new supported
  links), the advice test, the TQs, and questions that come from the catalogue and cluster mechanisms. Full tables go
  to files under `data/model/`.
- `knowledge/model.md` (generated): the structural reference. `knowledge/learned-model.md` and
  `knowledge/wp-model.md`: the readable curves.
- Readings are shown by period (month) and by strength band (close, uneven) where cells allow, so a meta shift or a
  top-only effect is visible.
- The TQs and the snapshot run every other chunk unless asked; candidate-variable tests run only when the queue is
  not empty.

## 10. Running it

- Train batch on GitHub (`.github/workflows/train-batch.yml`): fetch, shards, tables, prepare, rows, parts, finish.
  Inputs: pick, months, add_batch, note, rebuild_forensics. About 45 minutes a chunk.
- Cache (`cache.py`): keyed by layer. Measurement code invalidates prepared rows; fitting code invalidates fits;
  report code invalidates nothing. `cache.py info` shows the keys.
- Local engine setup for a session: `git fetch --depth 1 origin +replays:refs/remotes/origin/replays`, the pinned
  requirements, `cache.py sync pull`, `cache.py warm`.
