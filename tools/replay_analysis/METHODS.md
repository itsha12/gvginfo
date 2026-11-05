# How concepts are measured in replay data

Working notes for Claude: the analysis framework, where everything is stored, and how each concept on the GvG tactics
page is detected in gvg.report replays.

## The framework (layers)
1. **Game state every second** (`state.py`, built): per team, who is alive and when the dead return, morale, zones (own
   pit, own base, backside, stand, push side, enemy base, enemy pit), fight groups and the main group, pit NPCs alive
   (K2 A2 B1), the flag (carriers, stand owner, hold time, time to a boost). Still to add: what each team can know.
2. **Episodes** (`episodes.py`): splits (built: members, entering the enemy base, who answered, when, from where,
   NPCs killed with or without defenders, main numbers meanwhile) and flag runs (built: runner and line, escort,
   pushers and what they did, help and latency, half or full double running, main numbers meanwhile) and the stand
   ledger (built). To build: deaths (the 10 to 20 s before), monk profiles, numbers windows and power play, team
   posture (offensive or defensive against the situation).
3. **Judgement** (to build): each episode checked against tactics principles, giving findings (on time, late, wrong
   role, missed, good) with evidence and what the players could know.
4. **Edge ledger** (to build): each episode's effect on death penalty, boosts, pit NPCs, tiebreak and time; decides
   macro vs micro from evidence.
5. **Benchmarks** (after the bulk pull): distributions of every measure across good teams, so "late" is measured.
6. **Fixed question set**: every deep review answers the same questions (splits, flag game, power play, deaths, monk
   casting and positioning, support, posture), each mapped to the measures above.

## Where things are stored
- **Process = code** in `tools/replay_analysis/` (`state.py`, `episodes.py`, `analyze.py`, `report.py`). Prose
  instructions stay short: which commands to run; the thresholds and rules live in the code.
- **Per-map knowledge**: `data/maps/<map id>.json`, NPC positions estimated from melee attackers (the replay has no
  NPC positions), merged and refined every time a match on that map is analysed. Commit them when they change.
- **Per-match analysis**: `analyze.py <id>` writes one structured file (format gvginfo.analysis.v1, versioned by
  ENGINE). It is regenerated from the replays and the code in seconds, so it isn't stored yet; once the layers are
  stable it goes to `analysis/<id>.json` on the `replays` branch (and is built by the workflow for the bulk pull).
- **Principles**: `knowledge/tactics.md` (people read it); judgement rules in code will cite its sections.
- **Denning's verdicts on findings** (to add): `data/review_labels.json`, used to calibrate thresholds.
- **Benchmarks** (to add): one file built from all analysis files.

## Known limits
- No energy in the data. Positions about once a second. No NPC positions or health (estimated). Intent and what a
  player is looking at are never in the data.
- Split detection marks a "flank" when splitters stay near the enemy main group; early-game fights on one side can still
  show as splits with the whole enemy team "answering" (to refine with Denning's checks).

## Roles and positions
- Roles come from each player's build and party slot (`replaylib.Match.roles`). Positions are labelled relative to the
  player's own team: backside, push side, base, enemy base, stand.
- Position jumps from Aura of Displacement are real: the caster Shadow Steps to the target, then returns when they stop
  maintaining it.
- Groups every few seconds (who is with whom and where) label each phase: 8v8, 7v7, flag game, solo split, 3 or 4 man
  split, and who answered a split and how [phases, splits].
- Pit position comes from players hitting the Lord, else the res shrine (not in the pit on every map) [pit].

## Kills and timing
- Deaths "after time": within about 15 s after an even 2-minute mark; check whether the target was held low before the
  mark (a timed kill) [deaths].
- For each death: the burst (tightest window, armor ignoring vs respecting), how many attackers, the target's set and
  health; "not saveable" = 550+ armor ignoring within 0.35 s, or more than the target's health within 0.35 s; prots and
  Infuse on the target from 3 s before the first big hit, timed relative to it (negative = pre-prot); interrupts on the
  spike skills [spikes].
- Spike catching per team: enemy spikes (3+ attackers, 250+ damage in 2 s) counted as killed, saved with a prot, or
  survived without one, with prot timing and casters. The cleanest measure of monk quality, since it doesn't depend on
  who was winning [catches].
- Damage output per player per minute spots passive damage dealers, e.g. during an 8v7 [output]. Per-minute rates are
  partly game state: the winning side's players live longer.
- Time spent on a failed kill.

## Flag
- Carries come from the flag timeline (pickup to drop or capture). Per carry: the runner's role, their damage and casts
  during the carry against the rest of their match, damage taken, interrupts suffered, teammates left in the main fight.
- Half running: a drop followed within seconds by a teammate's pickup nearby, the first player heading back. Full
  running: a teammate waiting at base for the next flag while the first runner carries. Track time with 2 players away.
- Stand holds and morale boosts; holds that ended 100 to 119 s (near-missed boosts) [stand].
- Pushing the flagger: an enemy in casting range of the carrier who damages or snares them; which teammates move toward
  the carrier and how soon; the outcome and its cost in the main fight.
- Power play: players in the main fight per team every second (alive, in casting range of the fight centre), so 8v7
  and 8v6 windows stand out, and what each team did with them.

## Splits and pits
- Who shadowed each split, snares landed by its defenders, NPCs killed, kills on splitters after they commit [splits].
- The 8's distance from enemy splitters and snares landed (8v8 builds shadowing a split).
- Pit NPC kills with attackers and defenders present [npcs]; the Lord's Entourage casts (a gap counts as suppressed
  only if attackers were at the Lord), Lord damage by minute, enchantments on a team's own Lord [npcs, lord].
- A base race: 3+ of each team in the enemy base at once [lord].
- A win with no Lord damage, where the Lord and pit NPCs all die at the same moment, is a resign.

## Monks and mesmers
- Monk spacing: distance from the enemy mesmer and ranger against the distance to the allies taking damage.
- Cancelled casts (stopped without an interrupt) followed within a second by an enemy skill (a successful fake); time
  dazed; weapon set used under energy denial; peel (teammates' attacks, knockdowns and interrupts on the monk's
  attackers).
- Each interrupt records interrupter, skill used, interrupted skill and target; follow the target for 5 to 10 s to see
  whether it decided the fight. Interrupt totals per mesmer [totals].
- Weapon sets: gvg.report flags which sets cast faster (HCT) and lengthen enchantments; the replay records the set held
  each second (a carrier shows none).

## Comms and commentary
- Line up transcript times with match time using two or three anchors (kills, caps, boosts); offsets vary by video.
- Check every claim against the data; note where the data adds or corrects.
