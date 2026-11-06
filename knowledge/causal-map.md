*Generated from data/model/causal_map.json by tools/replay_analysis/causal_map.py: don't edit this page; tell Claude or edit the JSON (each change is logged with a reason).*

# Causal map (version 7)

What can cause what in a GvG match. Each concept is measured from the replays; the model for each concept may only use the causes listed under it, measured earlier in time, and the data decides how much each matters. Status: **hypothesis** (not yet tested), **supported** or **rejected** by data, **mechanical** (a formula). "Confirmed" = Denning has confirmed the reasoning; the size of the effect still comes from data.

## Context (fixed for the match or set by the clock)

### Build features `C.builds`
what each team's bars can do: interrupts, knockdowns, snares, Blind, enchantment and energy removal, prots and blocks, Aura of Stability count, condition and hex removal, healing, spike capacity, speed, measured Lord damage. *Measured: counts from data/skills.json properties of each bar (scales to builds never seen).*

### Matchup `C.matchup`
each build feature against the enemy's answer to it (enemy knockdowns v own Aura of Stability, enemy Blind v own removal, enemy spike v own prot stack, enemy energy denial v own energy hiding, split capacity v defence). *Measured: pairs of build features; their effect comes from data, never a label.*

### Team strength `C.strength`
fitted rating gap from every stored result before the match. *Measured: strength.py.*

### Map geometry `C.map`
Y (flag spawn to stand), routes, where the pits and stand are. *Measured: state.py (spawns, pits, stand).*

### Clock `C.clock`
match time, both teams' res timers, the boost clock. *Measured: scoreboard.*

## Allocation and plans (macro)

### Allocation `A.allocation`
where each team's 8 players are every second: groups, who is in each, on flag duty, splitting, defending, dead. *Measured: state and scoreboard (groups, zones, flag duty).*

Caused by:
- **Flag lead**: a team that must run has players on flag duty, which changes numbers elsewhere (Denning; hypothesis; `F5` `J1`)
- **Scoreboard**: the scoreboard shapes the next second's allocation (a loop over time) (Denning; hypothesis; `J1`)

### Phase `A.phase`
a stretch with a stable global setup; ends at a collapse, death, res or capture. *Measured: to build: from changes in allocation.*

Caused by:
- **Allocation**: a phase starts and ends when the global setup changes (formula; mechanical)

### Plan `A.plan`
each team's intent in a phase (8v8 brawl, flag game, split pressure, holding in its pit, power play, late Lord push; more found in data). *Measured: to build: inferred from the setup; plans found and amended from data (Denning).*

Caused by:
- **Allocation, Scoreboard, Matchup, Clock**: a plan is inferred from the setup and the situation; plans are found and amended from data (Denning; hypothesis; `J11`)
- **Build features**: the best play differs by the two teams' builds: decisions are compared with similar situations between similar builds, and choice effects are split by build once there are enough cases (Denning; hypothesis; `J10`)

### Jobs `A.jobs`
what each group must do given the plan: strong side converts, weak side holds safely, runner caps and returns, defenders hold the pit. *Measured: to build: from the plan and the numbers in each group.*

Caused by:
- **Plan, Allocation**: each group's job follows from the plan and the numbers where it is (Denning; hypothesis; `J2`)
- **Allocation**: a group in the enemy base is labelled by what it hits: NPCs or the Lord (split), the enemy carrier (push the runner), players (fight in the enemy pit) (Claude; mechanical)

### Damage potential v healing `A.roles_ratio`
the damage a group can actually put out (measured per role and build, not heads: a mesmer is not a hammer) against the healing and prots it faces. *Measured: to build: measured damage per second per role and build against players, plus healers' measured healing.*

Caused by:
- **Allocation**: a lone ranger split drawing the Mes/A and 8 monk changes main's damage potential against healing less than the heads suggest (Claude, confirmed; hypothesis; `J4`)

### Mesmers free to defend `A.mesa_free`
whether each mesmer is in the fight, carrying, or defending elsewhere. *Measured: to build: from allocation and flag duty.*

Caused by:
- **Allocation**: a mesmer carrying the flag or defending a split isn't free (formula; mechanical)

## Plays (decisions and micro)

### Target choice `P.1`
who the damage is put on (monks, midline, out of position players). *Measured: damage events by target role.*

Caused by:
- **Scoreboard, Plan, Clock, Build features, Team strength**: decisions are made in a situation: the engine learns what teams usually do in each situation (the usual play), so a choice that does better than the usual play stands out (Claude; hypothesis)

### Burst timing `P.2`
whether the damage dealers' hits land together. *Measured: spread of hit times within bursts.*

Caused by:
- **Scoreboard, Plan, Clock, Build features, Team strength**: decisions are made in a situation: the engine learns what teams usually do in each situation (the usual play), so a choice that does better than the usual play stands out (Claude; hypothesis)

### Offensive interrupts `P.3`
interrupts on enemy monks and key enemy skills. *Measured: interrupt events by target and skill.*

Caused by:
- **Scoreboard, Plan, Clock, Build features, Team strength**: decisions are made in a situation: the engine learns what teams usually do in each situation (the usual play), so a choice that does better than the usual play stands out (Claude; hypothesis)

### Defensive interrupts `P.4`
interrupts on enemy players pressuring the own team (spikers, Blind, strips, energy denial). *Measured: interrupt events by target.*

Caused by:
- **Mesmers free to defend**: the mesmer who should interrupt defensively is carrying the flag or defending a split (Claude; hypothesis; `K13` `M14`)
- **Scoreboard, Plan, Clock, Build features, Team strength**: decisions are made in a situation: the engine learns what teams usually do in each situation (the usual play), so a choice that does better than the usual play stands out (Claude; hypothesis)

### Condition removal `P.5`
removal of Blind, Weakness and other conditions from own damage dealers and monks, and how fast. *Measured: effects intervals and removal casts.*

Caused by:
- **Mesmers free to defend, Monk load, Removal capacity, Build features**: removal and defensive interrupts are missing because the Mes/A is running or defending, the mesmer interrupts offensively, the mesmer is shut down, the monks are overloaded, the bars lack removal, or the enemy reapplies faster than removal recharges (Claude; hypothesis; `K13`)
- **Scoreboard, Plan, Clock, Build features, Team strength**: decisions are made in a situation: the engine learns what teams usually do in each situation (the usual play), so a choice that does better than the usual play stands out (Claude; hypothesis)

### Prot timing `P.6`
prots and Infuse relative to the first big hit (pre-prot, on time, late). *Measured: forensics.*

Caused by:
- **Scoreboard, Plan, Clock, Build features, Team strength**: decisions are made in a situation: the engine learns what teams usually do in each situation (the usual play), so a choice that does better than the usual play stands out (Claude; hypothesis)

### Heal targeting `P.7`
healing on players under threat against healing elsewhere and overheal. *Measured: heal events against damage taken.*

Caused by:
- **Scoreboard, Plan, Clock, Build features, Team strength**: decisions are made in a situation: the engine learns what teams usually do in each situation (the usual play), so a choice that does better than the usual play stands out (Claude; hypothesis)

### Kiting and spacing `P.8`
distance from enemy mesmer and ranger, kiting toward safety, standing still before contact. *Measured: positions.*

Caused by:
- **Scoreboard, Plan, Clock, Build features, Team strength**: decisions are made in a situation: the engine learns what teams usually do in each situation (the usual play), so a choice that does better than the usual play stands out (Claude; hypothesis)

### Collapse timing `P.9`
when a team turns players onto a group, against res timers, enemy runner and enemy numbers. *Measured: phases.*

Caused by:
- **Scoreboard, Plan, Clock, Build features, Team strength**: decisions are made in a situation: the engine learns what teams usually do in each situation (the usual play), so a choice that does better than the usual play stands out (Claude; hypothesis)

### Run timing and runner choice `P.10`
who runs and when after the enemy's capture. *Measured: flag cycles.*

Caused by:
- **Scoreboard, Plan, Clock, Build features, Team strength**: decisions are made in a situation: the engine learns what teams usually do in each situation (the usual play), so a choice that does better than the usual play stands out (Claude; hypothesis)

### Split answer `P.11`
who answers a split and how fast. *Measured: splits.*

Caused by:
- **Scoreboard, Plan, Clock, Build features, Team strength**: decisions are made in a situation: the engine learns what teams usually do in each situation (the usual play), so a choice that does better than the usual play stands out (Claude; hypothesis)

### Res timing `P.12`
whether a team waits for its dead to return before fighting. *Measured: fights against res timers.*

Caused by:
- **Scoreboard, Plan, Clock, Build features, Team strength**: decisions are made in a situation: the engine learns what teams usually do in each situation (the usual play), so a choice that does better than the usual play stands out (Claude; hypothesis)

### Peel `P.13`
hitting or shutting down the players attacking an ally. *Measured: forensics.*

Caused by:
- **Scoreboard, Plan, Clock, Build features, Team strength**: decisions are made in a situation: the engine learns what teams usually do in each situation (the usual play), so a choice that does better than the usual play stands out (Claude; hypothesis)

### Commitment `P.14`
damage dealers in range and attacking during a power play or kill attempt. *Measured: positions and attack events.*

Caused by:
- **Clock, Flag lead**: a power play has a deadline (the enemy runner's return); the team must capitalize on the limited window (Denning; hypothesis; `J6`)
- **Scoreboard, Plan, Clock, Build features, Team strength**: decisions are made in a situation: the engine learns what teams usually do in each situation (the usual play), so a choice that does better than the usual play stands out (Claude; hypothesis)
- **Kill conversion**: with the enemy's boost near and no run planned, a team that can fight on (a power play) should; a team losing its fight may fall back for safety (Denning; hypothesis; `D4`)

### Taking conditions on oneself `P.15`
a monk transferring conditions onto itself (Draw Conditions), e.g. Deep Wound and Burning. *Measured: condition effects whose source is the own team.*

Caused by:
- **Scoreboard, Plan, Clock, Build features, Team strength**: decisions are made in a situation (the usual play) (Claude, confirmed; hypothesis)

### Death timing on purpose `P.16`
dying before time on purpose (death sets, not healing), monks dying in base before time to reset energy, and holding a kill until after the enemy's res (timing). *Measured: death timing against the res, death set held at death, own heals on the victim in its last seconds.*

Caused by:
- **Scoreboard, Clock, Plan, Team strength**: decisions are made in a situation (the usual play) (Claude, confirmed; hypothesis)

## Capacities (what a group can do in its fight)

### Pressure `K.1`
damage per second a group puts out. *Measured: damage events.*

Caused by:
- **Damage uptime**: damage dealers who can't attack don't put out damage (formula; mechanical)
- **Matchup**: the matchup sets what each capacity can be expected to be; a team can play well and still lose a hard matchup (how much comes from data) (Denning; hypothesis; `J10`)
- **Team strength**: stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude; hypothesis)

### Damage uptime `K.2`
share of time damage dealers are actually attacking or casting; lost damage-seconds by cause: knocked down, interrupted, Blind, Weakness, hexed, carrying, kiting, peeling, out of range, dead. *Measured: states, effects, carries, positions.*

Caused by:
- **Control received, Allocation, Peel, Kiting and spacing**: damage is lost to interrupts, knockdowns, Blind, Weakness, carrying the flag, kiting and peeling (Denning; hypothesis; `J9`)
- **Matchup**: the matchup sets what each capacity can be expected to be; a team can play well and still lose a hard matchup (how much comes from data) (Denning; hypothesis; `J10`)
- **Team strength**: stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude; hypothesis)

### Burst quality `K.3`
how much of the damage lands as synchronised bursts on one target. *Measured: bursts.*

Caused by:
- **Burst timing, Target choice**: synchronised hits on one target make a burst (Claude; hypothesis)

### Kill conversion `K.4`
bursts and pressure that become kills. *Measured: bursts against deaths.*

Caused by:
- **Damage potential v healing, Damage uptime, Burst timing, Kiting and spacing, Commitment**: a 5v3 fails to convert when its heads hide few damage dealers against healers, its damage is shut down, its bursts don't line up, the 3 kite to their pit or NPCs, or it doesn't commit (Claude, confirmed; hypothesis; `J3`)
- **Flag lead**: a team down on flags must send a runner soon, so its power play is shorter and less committed than its numbers suggest (Denning; hypothesis; `J5`)
- **Control received, Mitigation, Burst timing**: a team can't kill because of the enemy's defence (prots, blocks), shutdown of its spikers (interrupts, knockdowns, Blind, strips) or spread damage (Claude, confirmed; hypothesis; `K12`)
- **Target choice**: hitting the wrong player matters but isn't huge (Denning; hypothesis; `K12`)
- **Matchup**: the matchup sets what each capacity can be expected to be; a team can play well and still lose a hard matchup (how much comes from data) (Denning; hypothesis; `J10`)
- **Team strength**: stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude; hypothesis)

### Mitigation `K.5`
prots landed on time, blocks, damage prevented. *Measured: effects, prevented damage.*

Caused by:
- **Matchup**: the matchup sets what each capacity can be expected to be; a team can play well and still lose a hard matchup (how much comes from data) (Denning; hypothesis; `J10`)
- **Team strength**: stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude; hypothesis)

### Healing `K.6`
healing per second and response time to bursts. *Measured: heal events.*

Caused by:
- **Matchup**: the matchup sets what each capacity can be expected to be; a team can play well and still lose a hard matchup (how much comes from data) (Denning; hypothesis; `J10`)
- **Team strength**: stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude; hypothesis)

### Monk uptime `K.7`
share of time monks can cast: not interrupted, knocked down, Dazed or dead. *Measured: states, effects.*

Caused by:
- **Matchup**: the matchup sets what each capacity can be expected to be; a team can play well and still lose a hard matchup (how much comes from data) (Denning; hypothesis; `J10`)
- **Team strength**: stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude; hypothesis)

### Monk load `K.8`
casts the backline must make to keep up (overload). *Measured: incoming damage against healing per monk.*

Caused by:
- **Pressure, Burst timing**: overload is the goal when trying to kill: coordinated pressure on several targets (Denning; hypothesis; `M16`)
- **Build features**: attackers with area damage (dervish, elementalist) raise the healing a full pit needs (Denning; hypothesis; `P9`)

### Health ceiling `K.9`
each player's maximum health after DP, Deep Wound and health-reducing hexes. *Measured: morale events, effects.*

Caused by:
- **Deaths, Control received**: death penalty from deaths and Deep Wound or health-reducing hexes lower the ceiling (formula; mechanical)
- **Taking conditions on oneself**: Draw Conditions moves Deep Wound onto the monk, cutting its maximum health by a fifth: normal play, maybe a mistake for a lone 8 monk facing a ranger and a hammer; the data decides (Denning; hypothesis; `M18`)

### Sustain margin `K.10`
incoming damage against healing plus mitigation in a group. *Measured: pressure, healing, mitigation.*

Caused by:
- **Pressure, Healing, Mitigation**: incoming damage against healing plus mitigation (formula; mechanical)
- **Damage potential v healing**: healers per side only matter through damage: 3 healers + 1 damage v 2 healers + 2 damage is even (the 2-monk side maybe a bit stronger); what decides is damage potential against healing (Denning; hypothesis; `J12`)

### Control received `K.11`
interrupts, knockdowns, Blind, Daze, strips and energy denial taken, by role. *Measured: events and effects.*

Caused by:
- **Condition removal, Defensive interrupts, Kiting and spacing**: Blind and strips stop the kill when the team doesn't defend its offence: no defensive interrupts on the casters, no condition removal on its damage dealers, a clumped frontline in AoE range (Claude, confirmed; hypothesis; `K13`)
- **Matchup**: the matchup sets what each capacity can be expected to be; a team can play well and still lose a hard matchup (how much comes from data) (Denning; hypothesis; `J10`)
- **Team strength**: stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude; hypothesis)

### Removal capacity `K.12`
condition and hex removal available against how fast the enemy reapplies. *Measured: bars and effects.*

Caused by:
- **Matchup**: the matchup sets what each capacity can be expected to be; a team can play well and still lose a hard matchup (how much comes from data) (Denning; hypothesis; `J10`)
- **Team strength**: stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude; hypothesis)

### Mobility `K.13`
speed and snares: how fast a group can collapse, escape or run. *Measured: effects, positions.*

Caused by:
- **Matchup**: the matchup sets what each capacity can be expected to be; a team can play well and still lose a hard matchup (how much comes from data) (Denning; hypothesis; `J10`)
- **Team strength**: stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude; hypothesis)

## Results

### Deaths `R.1`
players killed, with cause (fights.assess). *Measured: deaths.*

Caused by:
- **Mobility, Kiting and spacing, Split answer**: a splitting ranger dies to snares or a fast collapse, an escape on recharge or interrupted, going too deep into knights and Lord, or staying after a second defender arrives (Claude, confirmed; hypothesis; `J4`)
- **Res timing**: good teams wait for their dead to return before fighting (Denning; hypothesis; `J8`)
- **Prot timing, Health ceiling, Heal targeting, Monk uptime, Kiting and spacing**: a team heals a lot but still loses a player when heals arrive instead of prots, the health ceiling is low (DP, Deep Wound), healing goes elsewhere, heals are late or interrupted, or the victim can't kite (Claude; hypothesis; `M17`)
- **Health ceiling**: death penalty stacking against a spike team makes every later spike easier (Denning; hypothesis; `K4`)
- **Sustain margin**: a group whose margin is negative loses players (Claude; hypothesis)
- **Death timing on purpose**: teams time kills and the dying team may choose to die before time; a death's cost depends on when it happens, and some deaths may be positive (energy reset, a short wait) (Denning; hypothesis; `K14` `K15` `K1` `K2`)

### Wipes `R.2`
fights where 3+ players or 2+ monks die. *Measured: fights.*

Caused by:
- **Collapse timing**: collapse timing is very important (Denning; hypothesis; `J7`)

### Flag lead `R.3`
the flag position (response on the next capture exchange). *Measured: scoreboard.*

Caused by:
- **Run timing and runner choice, Allocation, Map geometry**: being up on flags is the better position to boost and to run: runner trips, waiting runners, backup flags, routes (Denning; hypothesis; `F1` `F2` `F3` `F4`)
- **Allocation**: a team splitting has a different ability to run the flag (Denning; hypothesis; `J1`)
- **Run timing and runner choice**: a flag parked in base is a team deciding not to run yet; a long hand-off away from base is a response to a push or death, not double running (Denning; hypothesis; `F33`)
- **Commitment**: a team killing during the enemy's flag cycle answers later, deliberately: it finishes the power play, then runs (Denning; hypothesis; `F34`)
- **Mobility**: runners with speed skills carry far faster than average; the flag model uses each runner's measured speed (Claude; mechanical; `F35`)

### Boosts `R.4`
boosts won and conceded. *Measured: stand ledger.*

Caused by:
- **Flag lead**: the holder boosts unless the other team captures within the boost clock (formula; mechanical)

### Pit NPCs `R.5`
knights, archers and Bodyguard lost. *Measured: NPC deaths.*

Caused by:
- **Split answer**: a split answered late or with the wrong player takes NPCs (Denning; hypothesis; `S18` `S19`)
- **Allocation**: flag play and splits change the ability to take and defend NPCs (Denning; hypothesis; `J1`)
- **Monk load**: a full pit gives the monks 5+ extra targets, and knights ball up and eat area damage, so healing needed rises sharply (Denning; supported; `P9`)
- **Map geometry**: what a wipe can be turned into depends on where it happened: from the stand a team can't reach the enemy base and take NPCs before the res (Denning; supported; `D5`)

### Lord damage `R.6`
damage dealt to the enemy Lord (tiebreak). *Measured: Lord hits.*

Caused by:
- **Allocation, Pressure, Pit NPCs, Build features**: Lord damage needs players at the Lord, their damage, a worn-down pit and builds that hit the Lord (measured Lord damage per second) (Claude; hypothesis; `L1` `L10`)
- **Allocation**: two monks on the push side are the norm against a full pit; the pit deals a lot of damage, so they keep the attackers alive long enough to hurt the Lord (Denning; supported; `P10`)
- **Clock**: attackers leave the pit in the last seconds before the defenders' res so as not to be caught 8v8 (Denning; supported; `P11`)

### Time held `R.7`
seconds a weak side or defence held without losing anything. *Measured: to build: per job.*

Caused by:
- **Jobs**: the weak side's job is to hold safely: no deaths, keep the enemy group busy, don't chase, so the other side can play its power play (Denning; hypothesis; `J2`)

### Enemies tied up `R.8`
enemy players kept busy by a group, per own player (exchange rate). *Measured: to build: per phase.*

Caused by:
- **Jobs**: a group is judged on what it holds as well as what it kills (Denning; hypothesis; `J2`)

### Territory `R.9`
where fights happen: own side, enemy side, pits. *Measured: zones.*

Caused by:
- **Allocation, Kill conversion, Sustain margin**: winning fights pushes the fight toward the enemy's side (Claude; hypothesis)

### Tempo `R.10`
fights and kills against both res timers; time spent on failed kills. *Measured: to build.*

Caused by:
- **Res timing, Collapse timing, Kill conversion**: when fights happen against both res timers, and time spent on kills that fail (Claude; hypothesis; `J8`)

## Scoreboard and win

### Scoreboard `S.scoreboard`
numbers, DP, flag lead, stand, pit NPCs, Lord damage at any second. *Measured: scoreboard.py.*

Caused by:
- **Deaths, Boosts, Pit NPCs, Lord damage**: results change the scoreboard (formula; mechanical)
- **Death timing on purpose**: a death before time costs only seconds down and can reset a monk's energy; the win model values it by its timing (Denning; hypothesis; `K14`)

### Win `S.win`
the win-probability model: values every result. *Measured: model.py.*

Caused by:
- **Scoreboard**: the win model values every result (Denning; hypothesis; `W6`)

## Change log

- 2026-11-05: version 1 from the design conversation (scenarios 1 to 10 and follow-ups); decisions linked to the situation (the usual play), remaining gaps linked (Denning and Claude)
- 2026-11-05: version 2: 'Damage v healers' became 'Damage potential v healing' (Denning: healer counts only matter through damage); J12 link added (Denning)
- 2026-11-05: version 3: 'Taking conditions on oneself' (Draw Conditions, M18); jobs in the enemy base read from targets (Denning and Claude)
- 2026-11-06: version 4: 'Death timing on purpose' (Denning K14: timing, dying before time, monks resetting energy; deaths can be positive) (Denning)
- 2026-11-06: version 5: drops by kind (F33), killing during the enemy's flag cycle as a trade (F34), runner speed (F35) (Denning and Claude)
- 2026-11-06: version 6: pit lines P9 to P11 (knights first, monk load of a full pit and area damage, two monks against a full pit, leaving before the res); three links marked supported by data (Denning)
- 2026-11-06: version 7: wipe place limits conversion (D5); falling back near the enemy boost depends on the fight (D4); builds shape the best play (Denning)
- 2026-11-06: values.py: every result priced in win points (held-out result and model view), and node causes priced through them (Claude)
