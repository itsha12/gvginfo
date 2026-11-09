*Generated from data/model/causal_map.json by tools/replay_analysis/causal_map.py: don't edit this page; tell Claude or edit the JSON (each change is logged with a reason).*

# Causal map (version 12)

What can cause what in a GvG match. Each concept is measured from the replays; the model for each concept may only use the causes listed under it, measured earlier in time, and the data decides how much each matters. Status: **hypothesis** (not yet tested), **supported** or **rejected** by data, **mechanical** (a formula). "Confirmed" = Denning has confirmed the reasoning; the size of the effect still comes from data.

## Context (fixed for the match or set by the clock)

### Build features `C.builds`
what each team's bars can do: interrupts, knockdowns, snares, Blind, enchantment and energy removal, prots and blocks, Aura of Stability count, condition and hex removal, healing, spike capacity, speed, measured Lord damage. *Measured: counts from data/skills.json properties of each bar (scales to builds never seen).*

Caused by:
- **Flux**: a flux changes what builds can do (Claude; hypothesis)

### Matchup `C.matchup`
each build feature against the enemy's answer to it (enemy knockdowns v own Aura of Stability, enemy Blind v own removal, enemy spike v own prot stack, enemy energy denial v own energy hiding, split capacity v defence). *Measured: pairs of build features; their effect comes from data, never a label.*

### Team strength `C.strength`
how strong each team is: the guild's fitted rating and the lineup of players who actually played (MAT weighted by a measured amount), blended by how well each predicts later results. *Measured: strength.py (blend), lineup.py (people's records from every stored result, time ordered), context.py (matchup, map and flux beyond strength; off until it beats strength alone).*

### Map geometry `C.map`
Y (flag spawn to stand), routes, where the pits and stand are. *Measured: state.py (spawns, pits, stand).*

### Clock `C.clock`
match time, both teams' res timers, the boost clock. *Measured: scoreboard.*

### Flux `C.flux`
the month's flux (Minion Apocalypse, Meek Shall Inherit, Jack of All Trades, Chain Combo). *Measured: replay meta (gvg.report).*

## Allocation and plans (macro)

### Allocation `A.allocation`
where each team's 8 players are every second: groups, who is in each, on flag duty, splitting, defending, dead. *Measured: state and scoreboard (groups, zones, flag duty).*

Caused by:
- **Flag lead**: a team that must run has players on flag duty, which changes numbers elsewhere (Denning; hypothesis; `F5` `J1`)
- **Scoreboard**: the scoreboard shapes the next second's allocation (a loop over time) (Denning; supported; `J1`)
- **Split answer**: collapsing on a split depends on the plan (NPCs or DP), the defender's ability to hold, the flag position and how the main fight is going; the line comes from data (Denning; hypothesis; `S32` `S31`)
- **Fight state**: staying or falling back near the enemy's boost depends on whether the own team is losing the fight (Denning; hypothesis; `D4`)
- **Clock**: the res clock and the minute change when a split pays (Claude; supported)
- **Build features**: split builds (speed, snares) and the enemy's snares decide whether a split is possible (Claude; supported)
- **Team strength**: stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude; hypothesis)

Measured on unseen matches (learnednodes.py; gain = how much worse the node predicts without the link):
- Scoreboard (`S.scoreboard`), split chance node: gain +0.029 (+/- 0.0018, log loss), supported, 506 matches
- Build features (`C.builds`), split chance node: gain +0.01 (+/- 0.0033, log loss), supported, 506 matches
- Clock (`C.clock`), split chance node: gain +0.0025 (+/- 0.0006, log loss), supported, 506 matches
- Team strength (`C.strength`), split chance node: gain -0.0001 (+/- 0.0003, log loss), not clear yet, 506 matches

### Phase `A.phase`
a stretch with a stable global setup; ends at a collapse, death, res or capture. *Measured: to build: from changes in allocation.*

Caused by:
- **Allocation**: a phase starts and ends when the global setup changes (formula; mechanical)

### Plan `A.plan`
each team's intent in a phase (8v8 brawl, flag game, split pressure, holding in its pit, power play, late Lord push; more found in data). *Measured: to build: inferred from the setup; plans found and amended from data (Denning).*

Caused by:
- **Allocation, Scoreboard, Matchup, Clock**: a plan is inferred from the setup and the situation; plans are found and amended from data (Denning; hypothesis; `J11`)
- **Build features**: the best play differs by the two teams' builds: decisions are compared with similar situations between similar builds, and choice effects are split by build once there are enough cases (Denning; hypothesis; `J10`)
- **Build features**: a 2-monk spike build is behind on Lord damage late: NPCs matter less and DP more to it, so after a wipe it may prefer DP to NPCs (Denning; hypothesis; `B23` `D5`)

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
removal of Blind, Weakness and other conditions from own damage dealers and monks, and how fast; hex removal: the right hexes removed (valued from data) and how fast. *Measured: effects intervals and removal casts; eventlayer.py hex_removals.*

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
- **Scoreboard**: decisions are made in a situation: the engine learns what teams usually do in each situation (the usual play), so a choice that does better than the usual play stands out (Claude; supported)
- **Plan, Clock, Build features, Team strength**: decisions are made in a situation: the engine learns what teams usually do in each situation (the usual play), so a choice that does better than the usual play stands out (Claude; hypothesis)
- **Build features**: individual bars matter: a Mes/A defending 1v1 with a snare plays differently from one without (Denning; hypothesis; `B23`)
- **Mesmers free to defend**: free defenders near the base answer a split sooner (Denning; supported)
- **Allocation**: a bigger split draws more defenders (Claude; supported)

Measured on unseen matches (learnednodes.py; gain = how much worse the node predicts without the link):
- Allocation (`A.allocation`), split answer node: gain +1.04 (+/- 0.16, mean absolute error (s)), supported, 357 matches
- Mesmers free to defend (`A.mesa_free`), split answer node: gain +0.59 (+/- 0.15, mean absolute error (s)), supported, 357 matches
- Scoreboard (`S.scoreboard`), split answer node: gain +0.47 (+/- 0.13, mean absolute error (s)), supported, 357 matches
- Build features (`C.builds`), split answer node: gain +0.12 (+/- 0.09, mean absolute error (s)), not clear yet, 357 matches
- Clock (`C.clock`), split answer node: gain +0.06 (+/- 0.08, mean absolute error (s)), not clear yet, 357 matches
- Team strength (`C.strength`), split answer node: gain +0.05 (+/- 0.09, mean absolute error (s)), not clear yet, 357 matches

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
- **Monk uptime**: staying to fight or falling back near the enemy's boost is read from own monks' energy, enemy health, the enemy's estimated energy and numbers (Denning; hypothesis; `D4`)

### Taking conditions on oneself `P.15`
a monk transferring conditions onto itself (Draw Conditions), e.g. Deep Wound and Burning. *Measured: condition effects whose source is the own team.*

Caused by:
- **Scoreboard, Plan, Clock, Build features, Team strength**: decisions are made in a situation (the usual play) (Claude, confirmed; hypothesis)

### Death timing on purpose `P.16`
dying before time on purpose (death sets, not healing), monks dying in base before time to reset energy, and holding a kill until after the enemy's res (timing). *Measured: death timing against the res, death set held at death, own heals on the victim in its last seconds.*

Caused by:
- **Scoreboard, Clock, Plan, Team strength**: decisions are made in a situation (the usual play) (Claude, confirmed; hypothesis)
- **Res timing**: monks die on purpose only for a base res (every 2 minutes on the minute), e.g. in their own base at 17:55; never for a Pact or res signet (Denning; supported; `K14`)

### Wrong casts `P.17`
casting into a ready interrupt without cancelling, casting while Dazed, attacking while Blind (every role). *Measured: eventlayer.py casts.*

Caused by:
- **Matchup**: the enemy's interrupts, Daze and Blind against own cancels and removal set how many casts go wrong (Claude; hypothesis)

### Enchantment strips `P.18`
strips on the best target in range, valued from data (an enchantment's recorded output plus the bearer's measured drop after a strip). *Measured: eventlayer.py strips, values().*

Caused by:
- **Build features**: strips come from the enchantment removal on own bars, and the targets from the enemy's enchantments (Claude; hypothesis)

### Blind on enemies `P.19`
Blind on the enemy frontline, and on players hitting own healers (defensive). *Measured: eventlayer.py blinds.*

Caused by:
- **Build features**: Blind comes from the Blind skills on own bars (Claude; hypothesis)

### Split depth `P.20`
how deep a split plays in the enemy base: its nearest member's distance to the defending pit. *Measured: lnrows.py collapse rows.*

### Kiting `P.21`
kiting enemy melee (warriors, dervishes, assassins): seconds chased without being hit. *Measured: pressure.py.*

### Degen pressure `P.22`
degeneration put on the enemy (conditions and degen hexes), pip-seconds; the replays record degen as no damage. *Measured: pressure.py.*

### Baited interrupts `P.23`
enemy interrupts that landed on nothing because the player cancelled. *Measured: pressure.py.*

### Offensive knockdowns `P.24`
knockdowns landed on enemies, and on casting targets. *Measured: pressure.py.*

### Disables `P.25`
skill-seconds disabled on enemies by Complicate, Power Lock, Power Block and Blackout. *Measured: pressure.py.*

### Cast prevention `P.26`
Shame, Guilt and Diversion on enemies: seconds up and casts they punished. *Measured: pressure.py.*

### Pre-kiting `P.27`
distance kept from enemy melee heading for the player, before contact (split from P.21, Denning R-283). *Measured: pressure.py.*

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
- **Damage potential v healing, Kiting and spacing, Commitment**: a 5v3 fails to convert when its heads hide few damage dealers against healers, its damage is shut down, its bursts don't line up, the 3 kite to their pit or NPCs, or it doesn't commit (Claude, confirmed; hypothesis; `J3`)
- **Damage uptime, Burst timing**: a 5v3 fails to convert when its heads hide few damage dealers against healers, its damage is shut down, its bursts don't line up, the 3 kite to their pit or NPCs, or it doesn't commit (Claude, confirmed; supported; `J3`)
- **Flag lead**: a team down on flags must send a runner soon, so its power play is shorter and less committed than its numbers suggest (Denning; hypothesis; `J5`)
- **Control received**: a team can't kill because of the enemy's defence (prots, blocks), shutdown of its spikers (interrupts, knockdowns, Blind, strips) or spread damage (Claude, confirmed; hypothesis; `K12`)
- **Mitigation**: a team can't kill because of the enemy's defence (prots, blocks), shutdown of its spikers (interrupts, knockdowns, Blind, strips) or spread damage (Claude, confirmed; concurrent; `K12`)
- **Burst timing**: a team can't kill because of the enemy's defence (prots, blocks), shutdown of its spikers (interrupts, knockdowns, Blind, strips) or spread damage (Claude, confirmed; supported; `K12`)
- **Target choice**: hitting the wrong player matters but isn't huge (Denning; supported; `K12`)
- **Matchup**: the matchup sets what each capacity can be expected to be; a team can play well and still lose a hard matchup (how much comes from data) (Denning; hypothesis; `J10`)
- **Team strength**: stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude; supported)
- **Build features**: a snare on the split defender makes a collapse on a lone attacker much more likely to kill; without one, holding 1v1 is the aim (Denning; supported; `S31` `B23`)
- **Allocation**: a power play is any numbers advantage at main, an 8v7 while the enemy runs included (Denning; supported)
- **Scoreboard**: time down and flag carriers when the power play starts: found by discovery, approved by Denning (Denning; supported)
- **Offensive knockdowns**: offensive knockdowns convert a power play (Denning, session 4u) (Denning; hypothesis)
- **Disables**: disables on the enemy healers convert a power play (Denning, session 4u) (Denning; supported)
- **Cast prevention**: cast prevention on the enemy healers converts a power play (Denning, session 4u) (Denning; hypothesis)
- **Degen pressure**: degen pressure helps a power play wear the enemy down (Denning, session 4u) (Denning; hypothesis)
- **Kiting**: enemies kiting a power play's melee waste its time (Denning, session 4u) (Denning; concurrent)
- **Baited interrupts**: baited interrupts leave the enemy healers free (Denning, session 4u) (Denning; concurrent)

Measured on unseen matches (learnednodes.py; gain = how much worse the node predicts without the link):
- Allocation (`A.allocation`), power play node: gain +0.0398 (+/- 0.0063, log loss), supported, 503 matches
- Damage uptime (`K.2`), power play node: gain +0.0211 (+/- 0.002, log loss), supported, 503 matches
- Burst timing (`P.2`), power play node: gain +0.0075 (+/- 0.0021, log loss), supported, 503 matches
- Team strength (`C.strength`), power play node: gain +0.0074 (+/- 0.001, log loss), supported, 503 matches
- Target choice (`P.1`), power play node: gain +0.0071 (+/- 0.0011, log loss), supported, 503 matches
- Offensive knockdowns (`P.24`), power play node: gain +0.0069 (+/- 0.0047, log loss), not clear yet, 503 matches
- Disables (`P.25`), power play node: gain +0.0063 (+/- 0.0008, log loss), supported, 503 matches
- Scoreboard (`S.scoreboard`), power play node: gain +0.0051 (+/- 0.0009, log loss), supported, 503 matches
- Degen pressure (`P.22`), power play node: gain +0.0019 (+/- 0.001, log loss), not clear yet, 503 matches
- Commitment (`P.14`), power play node: gain +0.0 (+/- 0.0008, log loss), not clear yet, 503 matches
- Cast prevention (`P.26`), power play node: gain +0.0 (+/- 0.0004, log loss), not clear yet, 503 matches
- Flag lead (`R.3`), power play node: gain -0.0001 (+/- 0.0002, log loss), not clear yet, 503 matches
- Control received (`K.11`), power play node: gain -0.0003 (+/- 0.0004, log loss), not clear yet, 503 matches
- Build features (`C.builds`), power play node: gain -0.0007 (+/- 0.0005, log loss), not clear yet, 503 matches

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

### Fight state `K.14`
who is winning the fight now: expected deaths per team in the next 10 s. *Measured: fightstate.py, from the deaths node fitted without the match.*

Caused by:
- **Deaths**: deaths in a fight show who is losing it; the fight state looks ahead (Claude; hypothesis)

### Hex pressure `K.15`
hexes on a player and on its team's live healers. *Measured: nodes.py deaths and kill_conversion features (replay hex intervals).*

Caused by:
- **Build features**: hex pressure comes from the hexes on the enemy's bars (hex way) and is answered by own hex removal (Claude; hypothesis)

## Results

### Deaths `R.1`
players killed, with cause (fights.assess). *Measured: deaths.*

Caused by:
- **Mobility, Kiting and spacing, Split answer**: a splitting ranger dies to snares or a fast collapse, an escape on recharge or interrupted, going too deep into knights and Lord, or staying after a second defender arrives (Claude, confirmed; hypothesis; `J4`)
- **Res timing**: good teams wait for their dead to return before fighting (Denning; hypothesis; `J8`)
- **Prot timing, Heal targeting, Monk uptime, Kiting and spacing**: a team heals a lot but still loses a player when heals arrive instead of prots, the health ceiling is low (DP, Deep Wound), healing goes elsewhere, heals are late or interrupted, or the victim can't kite (Claude; hypothesis; `M17`)
- **Health ceiling**: a team heals a lot but still loses a player when heals arrive instead of prots, the health ceiling is low (DP, Deep Wound), healing goes elsewhere, heals are late or interrupted, or the victim can't kite (Claude; supported; `M17`)
- **Health ceiling**: death penalty stacking against a spike team makes every later spike easier (Denning; supported; `K4`)
- **Sustain margin**: a group whose margin is negative loses players (Claude; hypothesis)
- **Death timing on purpose**: teams time kills and the dying team may choose to die before time; a death's cost depends on when it happens, and some deaths may be positive (energy reset, a short wait) (Denning; hypothesis; `K14` `K1` `K2`)
- **Fight state**: a team losing its fight is about to take deaths (data; hypothesis)
- **Hex pressure**: hexes on a player or its healers make it easier to kill (Claude; hypothesis)
- **Collapse timing**: collapse timing: defenders arriving together kill a split member (Denning; hypothesis)
- **Build features**: a snare on the split defender makes a collapse on a lone attacker much more likely to kill (Denning; hypothesis)
- **Allocation**: a split outnumbered at the point of contact dies (Claude; supported)
- **Team strength**: stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude; supported)
- **Split depth**: the deeper the splitters are in the base (nearer the pit), the more likely they die to a collapse (Denning; supported)
- **Control received**: how strong the defenders' snares are, not just whether there is one, decides whether a collapse kills (Bounty, Denning) (Denning; hypothesis)
- **Mitigation**: a split that can heal or defend itself may not be killable, so collapsing on it wastes players (Denning, batch 10) (Denning; supported)
- **Pressure**: the defenders' damage decides whether they can kill the split (Denning, batch 10) (Denning; supported)
- **Scoreboard**: what the split can get NPC-wise sets how much a collapse is worth (Denning, batch 10) (Denning; hypothesis)

Measured on unseen matches (learnednodes.py; gain = how much worse the node predicts without the link):
- Pressure (`K.1`), collapse node: gain +0.0112 (+/- 0.0027, log loss), supported, 457 matches
- Team strength (`C.strength`), collapse node: gain +0.0111 (+/- 0.0033, log loss), supported, 457 matches
- Health ceiling (`K.9`), collapse node: gain +0.0056 (+/- 0.0019, log loss), supported, 457 matches
- Allocation (`A.allocation`), collapse node: gain +0.0028 (+/- 0.0007, log loss), supported, 457 matches
- Split depth (`P.20`), collapse node: gain +0.0023 (+/- 0.0009, log loss), supported, 457 matches
- Mitigation (`K.5`), collapse node: gain +0.002 (+/- 0.0007, log loss), supported, 457 matches
- Split answer (`P.11`), collapse node: gain +0.001 (+/- 0.0006, log loss), not clear yet, 457 matches
- Mobility (`K.13`), collapse node: gain +0.0003 (+/- 0.0005, log loss), not clear yet, 457 matches
- Control received (`K.11`), collapse node: gain +0.0001 (+/- 0.0013, log loss), not clear yet, 457 matches
- Scoreboard (`S.scoreboard`), collapse node: gain +0.0001 (+/- 0.0006, log loss), not clear yet, 457 matches
- Build features (`C.builds`), collapse node: gain -0.0002 (+/- 0.0005, log loss), not clear yet, 457 matches
- Collapse timing (`P.9`), collapse node: gain -0.0016 (+/- 0.0017, log loss), not clear yet, 457 matches

### Wipes `R.2`
fights where 3+ players or 2+ monks die. *Measured: fights.*

Caused by:
- **Collapse timing**: collapse timing is very important (Denning; hypothesis; `J7`)
- **Allocation**: numbers in a fight decide much of it (Denning; supported)
- **Peel**: frontline defensive peel (hitting or snaring enemies on its own backline) protects the healers (Denning; hypothesis)
- **Wrong casts**: wrong casts lose fights: casting into ready interrupts without cancelling, casting while Dazed, attacking while Blind (Denning; supported)
- **Enchantment strips**: strips on the right target (Elementalist enchantments when defensive, prots off a target under attack) (Denning; hypothesis)
- **Blind on enemies**: Blind on the enemy frontline, above all on players hitting own healers, is defensive play (Denning; hypothesis)
- **Burst timing**: off spike timing fails to kill (Denning; supported)
- **Pressure**: damage output against the role's usual (Denning; supported)
- **Condition removal**: the right hexes removed, and fast (Denning; hypothesis)
- **Team strength**: stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude; hypothesis)
- **Target choice**: going after the healers (Bounty: target choice costs time; the data: groups on the healers kill more) (Bounty; hypothesis)
- **Scoreboard**: the state at the fight's start (morale, numbers, time down, the stand, players within one spike): found by discovery, approved by Denning (Denning; supported)
- **Kiting**: a player who kites enemy melee avoids damage and wastes the frontline's time (Denning, session 4u) (Denning; hypothesis)
- **Degen pressure**: degen pressure (a ranger's poison on the whole team, a degen mesmer) wears a team down without showing as damage (Denning, session 4u) (Denning; hypothesis)
- **Baited interrupts**: a player who fakes out an interrupt wastes it (Denning, session 4u) (Denning; hypothesis)
- **Offensive knockdowns**: offensive knockdowns (a warrior landing many) stop casts and set up kills (Denning, session 4u) (Denning; hypothesis)
- **Disables**: disables (Complicate, Blackout, Power Lock, Power Block) take the enemy's key skills away (Denning, session 4u) (Denning; hypothesis)
- **Cast prevention**: cast prevention (Shame, Diversion, Guilt) stops the enemy's casts (Denning, session 4u) (Denning; hypothesis)
- **Build features**: hex and heal skills on the bars change fights: found by discovery, approved by Denning (Denning; hypothesis)
- **Pre-kiting**: keeping distance from melee heading for you avoids the first hit (Denning, session 4u; split from P.21, R-283) (Denning; hypothesis)

Measured on unseen matches (learnednodes.py; gain = how much worse the node predicts without the link):
- Scoreboard (`S.scoreboard`), fight outcome node: gain +0.0914 (+/- 0.0045, log loss), supported, 505 matches
- Pressure (`K.1`), fight outcome node: gain +0.0234 (+/- 0.004, log loss), supported, 505 matches
- Burst timing (`P.2`), fight outcome node: gain +0.0199 (+/- 0.0044, log loss), supported, 505 matches
- Allocation (`A.allocation`), fight outcome node: gain +0.0191 (+/- 0.0024, log loss), supported, 505 matches
- Wrong casts (`P.17`), fight outcome node: gain +0.0121 (+/- 0.0024, log loss), supported, 505 matches
- Build features (`C.builds`), fight outcome node: gain +0.0021 (+/- 0.0012, log loss), not clear yet, 505 matches
- Condition removal (`P.5`), fight outcome node: gain +0.0013 (+/- 0.0011, log loss), not clear yet, 505 matches
- Target choice (`P.1`), fight outcome node: gain +0.0006 (+/- 0.0006, log loss), not clear yet, 505 matches
- Team strength (`C.strength`), fight outcome node: gain +0.0001 (+/- 0.0013, log loss), not clear yet, 505 matches
- Peel (`P.13`), fight outcome node: gain -0.0 (+/- 0.0003, log loss), not clear yet, 505 matches
- Kiting (`P.21`), fight outcome node: gain -0.0 (+/- 0.0003, log loss), not clear yet, 505 matches
- Offensive knockdowns (`P.24`), fight outcome node: gain -0.0 (+/- 0.0024, log loss), not clear yet, 505 matches
- Baited interrupts (`P.23`), fight outcome node: gain -0.0001 (+/- 0.0004, log loss), not clear yet, 505 matches
- Disables (`P.25`), fight outcome node: gain -0.0002 (+/- 0.0007, log loss), not clear yet, 505 matches
- Enchantment strips (`P.18`), fight outcome node: gain -0.0003 (+/- 0.0012, log loss), not clear yet, 505 matches
- Degen pressure (`P.22`), fight outcome node: gain -0.0003 (+/- 0.0004, log loss), not clear yet, 505 matches
- Pre-kiting (`P.27`), fight outcome node: gain -0.0003 (+/- 0.0006, log loss), not clear yet, 505 matches
- Cast prevention (`P.26`), fight outcome node: gain -0.0009 (+/- 0.0004, log loss), rejected, 505 matches
- Blind on enemies (`P.19`), fight outcome node: gain -0.001 (+/- 0.0008, log loss), not clear yet, 505 matches
- **Held for Denning:** the data says Cast prevention -> Wipes is rejected; it stays a hypothesis until he rules.

### Flag lead `R.3`
the flag position (response on the next capture exchange). *Measured: scoreboard.*

Caused by:
- **Run timing and runner choice, Allocation, Map geometry**: being up on flags is the better position to boost and to run: runner trips, waiting runners, backup flags, routes (Denning; supported; `F1` `F2` `F3` `F4`)
- **Allocation**: a team splitting has a different ability to run the flag (Denning; supported; `J1`)
- **Run timing and runner choice**: a flag parked in base is a team deciding not to run yet; a long hand-off away from base is a response to a push or death, not double running (Denning; supported; `F33`)
- **Commitment**: a team killing during the enemy's flag cycle answers later, deliberately: it finishes the power play, then runs (Denning; hypothesis; `F34`)
- **Mobility**: runners with speed skills carry far faster than average; the flag model uses each runner's measured speed (Claude; mechanical; `F35`)
- **Map geometry**: the length of the flag run (Y) and the distance from the pits to the stand shape the flag game (Claude; supported)
- **Control received**: control on the runner (Cripple, knockdowns) stops a run; read at the same point of every run (Denning; hypothesis)
- **Team strength**: stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude; hypothesis)
- **Scoreboard**: a flag lead tends to grow or shrink by how it stands now (boost and run timing) (Claude; supported)
- **Deaths**: deaths lose flag position: the runner, the escort or the main (Claude; hypothesis)
- **Clock**: the res clock and the minute change what a run can do (Claude; hypothesis)
- **Mesmers free to defend**: defenders free to push a runner slow the enemy's capture (Denning; hypothesis)
- **Build features**: snare skills on the bars change whether runs get through: found by discovery, approved by Denning (Denning; hypothesis)
- **Mitigation**: own healing monks help defend against runs: found by discovery, approved by Denning (Denning; hypothesis)

Measured on unseen matches (learnednodes.py; gain = how much worse the node predicts without the link):
- Mobility (`K.13`), capture speed node: gain +2.31 (+/- 0.11, mean absolute error (s)), supported, 486 matches
- Run timing and runner choice (`P.10`), flag swing node: gain +0.78 (+/- 0.07, mean absolute error (s)), supported, 506 matches
- Scoreboard (`S.scoreboard`), flag swing node: gain +0.66 (+/- 0.07, mean absolute error (s)), supported, 506 matches
- Allocation (`A.allocation`), capture speed node: gain +0.41 (+/- 0.1, mean absolute error (s)), supported, 486 matches
- Map geometry (`C.map`), capture speed node: gain +0.41 (+/- 0.04, mean absolute error (s)), supported, 486 matches
- Run timing and runner choice (`P.10`), capture speed node: gain +0.19 (+/- 0.07, mean absolute error (s)), supported, 486 matches
- Team strength (`C.strength`), flag swing node: gain +0.06 (+/- 0.04, mean absolute error (s)), not clear yet, 506 matches
- Scoreboard (`S.scoreboard`), run defence node: gain +0.0403 (+/- 0.0031, log loss), supported, 505 matches
- Team strength (`C.strength`), capture speed node: gain +0.04 (+/- 0.03, mean absolute error (s)), not clear yet, 486 matches
- Mobility (`K.13`), run outcome node: gain +0.0333 (+/- 0.0028, log loss), supported, 505 matches
- Mobility (`K.13`), run defence node: gain +0.0327 (+/- 0.0027, log loss), supported, 505 matches
- Scoreboard (`S.scoreboard`), run outcome node: gain +0.0106 (+/- 0.002, log loss), supported, 505 matches
- Map geometry (`C.map`), run defence node: gain +0.0036 (+/- 0.0009, log loss), supported, 505 matches
- Map geometry (`C.map`), run outcome node: gain +0.0031 (+/- 0.0008, log loss), supported, 505 matches
- Run timing and runner choice (`P.10`), run outcome node: gain +0.0025 (+/- 0.0012, log loss), supported, 505 matches
- Run timing and runner choice (`P.10`), run defence node: gain +0.0011 (+/- 0.0004, log loss), supported, 505 matches
- Team strength (`C.strength`), run defence node: gain +0.0008 (+/- 0.0006, log loss), not clear yet, 505 matches
- Team strength (`C.strength`), run outcome node: gain +0.0005 (+/- 0.0007, log loss), not clear yet, 505 matches
- Mesmers free to defend (`A.mesa_free`), run defence node: gain +0.0002 (+/- 0.0006, log loss), not clear yet, 505 matches
- Build features (`C.builds`), run defence node: gain +0.0001 (+/- 0.0005, log loss), not clear yet, 505 matches
- Control received (`K.11`), capture speed node: gain +0.0 (+/- 0.01, mean absolute error (s)), not clear yet, 486 matches
- Control received (`K.11`), run defence node: gain +0.0 (+/- 0.0003, log loss), not clear yet, 505 matches
- Deaths (`R.1`), flag swing node: gain -0.0 (+/- 0.01, mean absolute error (s)), not clear yet, 506 matches
- Mitigation (`K.5`), run defence node: gain -0.0 (+/- 0.0004, log loss), not clear yet, 505 matches
- Allocation (`A.allocation`), run outcome node: gain -0.0001 (+/- 0.0009, log loss), not clear yet, 505 matches
- Build features (`C.builds`), run outcome node: gain -0.0001 (+/- 0.0007, log loss), not clear yet, 505 matches
- Allocation (`A.allocation`), run defence node: gain -0.0002 (+/- 0.0005, log loss), not clear yet, 505 matches
- Control received (`K.11`), run outcome node: gain -0.001 (+/- 0.0005, log loss), rejected, 505 matches
- Allocation (`A.allocation`), flag swing node: gain -0.01 (+/- 0.02, mean absolute error (s)), not clear yet, 506 matches
- Map geometry (`C.map`), flag swing node: gain -0.01 (+/- 0.01, mean absolute error (s)), not clear yet, 506 matches
- Clock (`C.clock`), flag swing node: gain -0.01 (+/- 0.01, mean absolute error (s)), not clear yet, 506 matches

### Boosts `R.4`
boosts won and conceded. *Measured: stand ledger.*

Caused by:
- **Flag lead**: the holder boosts unless the other team captures within the boost clock (formula; mechanical)

### Pit NPCs `R.5`
knights, archers and Bodyguard lost. *Measured: NPC deaths.*

Caused by:
- **Split answer**: a split answered late or with the wrong player takes NPCs (Denning; supported; `S18` `S19`)
- **Allocation**: flag play and splits change the ability to take and defend NPCs (Denning; supported; `J1`)
- **Monk load**: a full pit gives the monks 5+ extra targets, and knights ball up and eat area damage, so healing needed rises sharply (Denning; supported; `P9`)
- **Map geometry**: what a wipe can be turned into depends on where it happened: from the stand a team can't reach the enemy base and take NPCs before the res (Denning; supported; `D5`)
- **Team strength**: stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude; supported)
- **Scoreboard**: a pit already short of NPCs, or a base with few free defenders, loses an NPC to a split more easily (Claude; supported)
- **Control received**: the defenders' snares slow a split's work on the NPCs (Denning; hypothesis)
- **Mobility**: a fast split gets in and out of the base (Denning; hypothesis)
- **Build features**: the defenders' prots make a split's NPC kills harder: found by discovery, approved by Denning (Denning; supported)
- **Pressure**: damage landing on the pit NPCs (Claude; concurrent)
- **Healing**: healing on the pit NPCs keeps them alive (Claude; supported)
- **Clock**: time in the pit and the res clock (Claude; supported)

Measured on unseen matches (learnednodes.py; gain = how much worse the node predicts without the link):
- Split answer (`P.11`), pit npc loss node: gain +0.0737 (+/- 0.0031, log loss), supported, 504 matches
- Scoreboard (`S.scoreboard`), split effect node: gain +0.0271 (+/- 0.0078, log loss), supported, 357 matches
- Scoreboard (`S.scoreboard`), pit npc loss node: gain +0.0054 (+/- 0.0007, log loss), supported, 504 matches
- Build features (`C.builds`), split effect node: gain +0.0034 (+/- 0.0028, log loss), not clear yet, 357 matches
- Allocation (`A.allocation`), pit npc loss node: gain +0.003 (+/- 0.0008, log loss), supported, 504 matches
- Split answer (`P.11`), split effect node: gain +0.0029 (+/- 0.001, log loss), supported, 357 matches
- Build features (`C.builds`), pit npc loss node: gain +0.0029 (+/- 0.0008, log loss), supported, 504 matches
- Allocation (`A.allocation`), split effect node: gain +0.0028 (+/- 0.0007, log loss), supported, 357 matches
- Team strength (`C.strength`), pit npc loss node: gain +0.0026 (+/- 0.001, log loss), supported, 504 matches
- Clock (`C.clock`), pit npc loss node: gain +0.0021 (+/- 0.0006, log loss), supported, 504 matches
- Healing (`K.6`), pit npc loss node: gain +0.0006 (+/- 0.0002, log loss), supported, 504 matches
- Mobility (`K.13`), split effect node: gain +0.0001 (+/- 0.0018, log loss), not clear yet, 357 matches
- Control received (`K.11`), split effect node: gain -0.0014 (+/- 0.0009, log loss), not clear yet, 357 matches
- Team strength (`C.strength`), split effect node: gain -0.0016 (+/- 0.001, log loss), not clear yet, 357 matches
- Monk load (`K.8`), split effect node: gain -0.002 (+/- 0.0011, log loss), not clear yet, 357 matches

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

### Lord health `R.11`
the Guild Lord's health, rebuilt from damage, healing, boosts (+1% max health each) and measured natural regeneration. *Measured: lord.py; regeneration measured by benchmarks.py regen.*

Caused by:
- **Lord damage**: damage on the Lord lowers its health; healing and regeneration restore it (formula; mechanical)
- **Boosts**: each boost adds 1% to the Lord's max health (Denning; mechanical)

### Lord exposed `R.12`
the Lord's Bodyguard and both knights are dead. *Measured: lord.py from pit NPC deaths (full roster, integrity.py).*

Caused by:
- **Pit NPCs**: the Lord is exposed once its Bodyguard and knights are dead (formula; mechanical)

### Lord killed `R.13`
the Lord dies: how 28 of the first 30 matches ended. *Measured: nodes.py lord_kill (Lord dies within 30 s while enemies are in its pit).*

Caused by:
- **Lord exposed**: an exposed Lord can be hit without its guards (Claude; hypothesis)
- **Lord health**: a Lord low on health dies sooner (formula; mechanical)

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
- **Lord killed**: killing the enemy Lord wins the match (formula; mechanical)

## Change log

- 2026-11-05: version 1 from the design conversation (scenarios 1 to 10 and follow-ups); decisions linked to the situation (the usual play), remaining gaps linked (Denning and Claude)
- 2026-11-05: version 2: 'Damage v healers' became 'Damage potential v healing' (Denning: healer counts only matter through damage); J12 link added (Denning)
- 2026-11-05: version 3: 'Taking conditions on oneself' (Draw Conditions, M18); jobs in the enemy base read from targets (Denning and Claude)
- 2026-11-06: version 4: 'Death timing on purpose' (Denning K14: timing, dying before time, monks resetting energy; deaths can be positive) (Denning)
- 2026-11-06: version 5: drops by kind (F33), killing during the enemy's flag cycle as a trade (F34), runner speed (F35) (Denning and Claude)
- 2026-11-06: version 6: pit lines P9 to P11 (knights first, monk load of a full pit and area damage, two monks against a full pit, leaving before the res); three links marked supported by data (Denning)
- 2026-11-06: version 7: wipe place limits conversion (D5); falling back near the enemy boost depends on the fight (D4); builds shape the best play (Denning)
- 2026-11-06: values.py: every result priced in win points (held-out result and model view), and node causes priced through them (Claude)
- 2026-11-06: version 8: deliberate deaths only for a base res; individual bars change plays; spike builds weigh DP over NPCs; what decides staying near the enemy boost (Denning)
- 2026-11-06: version 9: per-player skill flags (buildfeat.player_flags); defender snare on split answers (S31); no rushing the base to spike resurrected players (D5) (Denning)
- 2026-11-06: split answers: holder (not collapsing) and collapsers read apart; S32 what decides a collapse (Denning)
- 2026-11-06: version 10: Lord health, Lord exposed and Lord killed (R.11 to R.13; 28 of 30 matches end with a Lord kill), fight state (K.14), hex pressure (K.15), flux (C.flux); team strength now includes lineups (Claude, with Denning (lineup strength, roster))
- 2026-11-07: node P.17 Wrong casts added (step 2b: eventlayer.py casts) (Claude, from Denning's list)
- 2026-11-07: node P.18 Enchantment strips added (step 2b: eventlayer.py strips, values()) (Claude, from Denning's list)
- 2026-11-07: node P.19 Blind on enemies added (step 2b: eventlayer.py blinds) (Claude, from Denning's list)
- 2026-11-07: link C.matchup -> P.17 added as a hypothesis: the enemy's interrupts, Daze and Blind against own cancels and removal set how many casts go wrong (Claude)
- 2026-11-07: link C.builds -> P.18 added as a hypothesis: strips come from the enchantment removal on own bars, and the targets from the enemy's enchantments (Claude)
- 2026-11-07: link C.builds -> P.19 added as a hypothesis: Blind comes from the Blind skills on own bars (Claude)
- 2026-11-07: link P.10 -> R.3 supported by the run_outcome node (held-out gain 0.015 +/- 0.0066, 113 matches) (data)
- 2026-11-07: link P.10 -> R.3 supported by the run_outcome node (held-out gain 0.015 +/- 0.0066, 113 matches) (data)
- 2026-11-07: link K.11 -> R.3 added as a hypothesis (node run_outcome): control on the runner (Cripple, knockdowns) stops a run; read at the same point of every run (Denning)
- 2026-11-07: link C.strength -> R.3 added as a hypothesis (node run_outcome): stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude)
- 2026-11-07: link S.scoreboard -> R.3 added as a hypothesis (node flag_swing): a flag lead tends to grow or shrink by how it stands now (boost and run timing) (Claude)
- 2026-11-07: link A.allocation -> R.3 rejected by the flag_swing node (held-out gain -0.09 +/- 0.04, 113 matches) (data)
- 2026-11-07: link A.allocation -> R.3 rejected by the flag_swing node (held-out gain -0.09 +/- 0.04, 113 matches) (data)
- 2026-11-07: link R.1 -> R.3 added as a hypothesis (node flag_swing): deaths lose flag position: the runner, the escort or the main (Claude)
- 2026-11-07: link C.clock -> R.3 added as a hypothesis (node flag_swing): the res clock and the minute change what a run can do (Claude)
- 2026-11-07: link A.mesa_free -> R.3 added as a hypothesis (node capture_speed): defenders free to push a runner slow the enemy's capture (Denning)
- 2026-11-07: link A.mesa_free -> R.3 supported by the capture_speed node (held-out gain 6.01 +/- 0.48, 108 matches) (data)
- 2026-11-07: link A.allocation -> K.4 added as a hypothesis (node power_play): a power play is any numbers advantage at main, an 8v7 while the enemy runs included (Denning)
- 2026-11-07: link A.allocation -> K.4 supported by the power_play node (held-out gain 0.0557 +/- 0.0139, 113 matches) (data)
- 2026-11-07: link K.5 -> K.4 supported by the power_play node (held-out gain 0.0204 +/- 0.0065, 113 matches) (data)
- 2026-11-07: link P.1 -> K.4 rejected by the power_play node (held-out gain -0.003 +/- 0.0012, 113 matches) (data)
- 2026-11-07: link A.allocation -> R.2 added as a hypothesis (node fight_outcome): numbers in a fight decide much of it (Denning)
- 2026-11-07: link A.allocation -> R.2 supported by the fight_outcome node (held-out gain 0.0439 +/- 0.0092, 113 matches) (data)
- 2026-11-07: link P.13 -> R.2 added as a hypothesis (node fight_outcome): frontline defensive peel (hitting or snaring enemies on its own backline) protects the healers (Denning)
- 2026-11-07: link P.17 -> R.2 added as a hypothesis (node fight_outcome): wrong casts lose fights: casting into ready interrupts without cancelling, casting while Dazed, attacking while Blind (Denning)
- 2026-11-07: link P.18 -> R.2 added as a hypothesis (node fight_outcome): strips on the right target (Elementalist enchantments when defensive, prots off a target under attack) (Denning)
- 2026-11-07: link P.19 -> R.2 added as a hypothesis (node fight_outcome): Blind on the enemy frontline, above all on players hitting own healers, is defensive play (Denning)
- 2026-11-07: link P.19 -> R.2 rejected by the fight_outcome node (held-out gain -0.0023 +/- 0.0006, 113 matches) (data)
- 2026-11-07: link P.2 -> R.2 added as a hypothesis (node fight_outcome): off spike timing fails to kill (Denning)
- 2026-11-07: link P.2 -> R.2 supported by the fight_outcome node (held-out gain 0.0232 +/- 0.011, 113 matches) (data)
- 2026-11-07: link K.1 -> R.2 added as a hypothesis (node fight_outcome): damage output against the role's usual (Denning)
- 2026-11-07: link K.1 -> R.2 supported by the fight_outcome node (held-out gain 0.0339 +/- 0.0135, 113 matches) (data)
- 2026-11-07: link P.5 -> R.2 added as a hypothesis (node fight_outcome): the right hexes removed, and fast (Denning)
- 2026-11-07: link C.strength -> R.2 added as a hypothesis (node fight_outcome): stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude)
- 2026-11-07: link C.strength -> R.2 supported by the fight_outcome node (held-out gain 0.0632 +/- 0.008, 113 matches) (data)
- 2026-11-07: link S.scoreboard -> A.allocation supported by the split_chance node (held-out gain 0.0168 +/- 0.0056, 113 matches) (data)
- 2026-11-07: link C.clock -> A.allocation added as a hypothesis (node split_chance): the res clock and the minute change when a split pays (Claude)
- 2026-11-07: link C.builds -> A.allocation added as a hypothesis (node split_chance): split builds (speed, snares) and the enemy's snares decide whether a split is possible (Claude)
- 2026-11-07: link C.strength -> A.allocation added as a hypothesis (node split_chance): stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude)
- 2026-11-07: link A.mesa_free -> P.11 added as a hypothesis (node split_answer): free defenders near the base answer a split sooner (Denning)
- 2026-11-07: link A.mesa_free -> P.11 supported by the split_answer node (held-out gain 0.6 +/- 0.19, 78 matches) (data)
- 2026-11-07: link A.allocation -> P.11 added as a hypothesis (node split_answer): a bigger split draws more defenders (Claude)
- 2026-11-07: link P.11 -> R.5 supported by the split_effect node (held-out gain 0.0042 +/- 0.0018, 78 matches) (data)
- 2026-11-07: link C.strength -> R.5 added as a hypothesis (node split_effect): stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude)
- 2026-11-07: link P.9 -> R.1 added as a hypothesis (node collapse): collapse timing: defenders arriving together kill a split member (Denning)
- 2026-11-07: link P.9 -> R.1 supported by the collapse node (held-out gain 0.0065 +/- 0.0021, 103 matches) (data)
- 2026-11-07: link C.builds -> R.1 added as a hypothesis (node collapse): a snare on the split defender makes a collapse on a lone attacker much more likely to kill (Denning)
- 2026-11-07: link A.allocation -> R.1 added as a hypothesis (node collapse): a split outnumbered at the point of contact dies (Claude)
- 2026-11-07: link C.strength -> R.1 added as a hypothesis (node collapse): stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude)
- 2026-11-07: link K.11 -> K.4: hypothesis -> supported by data (power_play supported +0.0012) (data)
- 2026-11-07: link P.1 -> K.4: rejected -> hypothesis by data (power_play not clear yet -0.0021) (data)
- 2026-11-07: link A.allocation -> R.3: rejected -> hypothesis by data (run_outcome not clear yet +0.0028, flag_swing rejected -0.1, capture_speed not clear yet +0.3) (data)
- 2026-11-07: link A.allocation -> R.3: rejected -> hypothesis by data (run_outcome not clear yet +0.0028, flag_swing rejected -0.1, capture_speed not clear yet +0.3) (data)
- 2026-11-07: link P.11 -> R.5: supported -> hypothesis by data (split_effect not clear yet +0.0035) (data)
- 2026-11-07: link A.mesa_free -> R.3: supported -> rejected by data (capture_speed rejected -0.16) (data)
- 2026-11-07: link A.mesa_free -> P.11: supported -> hypothesis by data (split_answer not clear yet +0.57) (data)
- 2026-11-07: link A.mesa_free -> R.3: back to hypothesis; the data says rejected, held for Denning's ruling (Claude, at Denning's request)
- 2026-11-07: link P.19 -> R.2: back to hypothesis; the data says rejected, held for Denning's ruling (Claude, at Denning's request)
- 2026-11-07: link A.mesa_free -> R.3: the capture_speed node no longer uses it; its measurement there removed (Claude)
- 2026-11-07: link K.11 -> K.4: supported -> hypothesis by data (power_play not clear yet +0.0012) (data)
- 2026-11-07: link C.strength -> R.3: hypothesis -> supported by data (run_outcome not clear yet -0.0051, flag_swing not clear yet +0.25, capture_speed supported +0.2, run_defence not clear yet -0.0075) (data)
- 2026-11-07: link A.allocation -> R.1: hypothesis -> supported by data (collapse supported +0.0046) (data)
- 2026-11-07: link K.11 -> K.4: hypothesis -> supported by data (power_play supported +0.0011) (data)
- 2026-11-07: link K.2 -> K.4: hypothesis -> supported by data (power_play supported +0.0183) (data)
- 2026-11-07: link P.14 -> K.4: hypothesis -> supported by data (power_play supported +0.0129) (data)
- 2026-11-07: link P.11 -> R.1: hypothesis -> supported by data (collapse supported +0.0041) (data)
- 2026-11-07: link K.11 -> K.4: supported -> rejected by data (power_play rejected -0.0007) (data)
- 2026-11-07: link A.mesa_free -> P.11: hypothesis -> supported by data (split_answer supported +0.53) (data)
- 2026-11-07: link A.allocation -> P.11: hypothesis -> supported by data (split_answer supported +0.81) (data)
- 2026-11-07: link C.builds -> R.1: hypothesis -> supported by data (collapse supported +0.0083) (data)
- 2026-11-07: link A.allocation -> R.1: supported -> hypothesis by data (collapse not clear yet +0.0041) (data)
- 2026-11-07: Blind measured as time spent Blind, not the number of Blinds, and every Blind counted (the caster is unknown for 56% of them in the replays): K.11 -> K.4 now reads seconds own attackers spent Blind per 10 s; P.19 -> R.2 reads seconds the enemy frontline spent Blind and seconds from defensive Blinds. K.11 -> K.4 reset from rejected to hypothesis (it was rejected on the old count). (Denning)
- 2026-11-08: link S.scoreboard -> R.5 added as a hypothesis (node split_effect): a pit already short of NPCs, or a base with few free defenders, loses an NPC to a split more easily (Claude)
- 2026-11-08: link P.14 -> K.4: supported -> hypothesis by data (power_play not clear yet +0.0066) (data)
- 2026-11-08: link K.11 -> R.3: hypothesis -> supported by data (run_outcome not clear yet +0.0002, capture_speed supported +0.12) (data)
- 2026-11-08: link R.1 -> R.3: hypothesis -> supported by data (flag_swing supported +0.05) (data)
- 2026-11-08: node P.20 Split depth added (step 2b: lnrows.py collapse rows) (Claude, from Denning's list)
- 2026-11-08: link P.20 -> R.1 added as a hypothesis (node collapse): the deeper the splitters are in the base (nearer the pit), the more likely they die to a collapse (Denning)
- 2026-11-08: link K.13 -> R.1: hypothesis -> rejected by data (collapse rejected -0.0033) (data)
- 2026-11-08: link P.11 -> R.1: supported -> hypothesis by data (collapse not clear yet +0.0011) (data)
- 2026-11-08: commentary bundle (Bounty, Nick): snare and speed power (movepower.py) into the run, collapse, split effect and split chance nodes (K.11, K.13); healer focus (P.1) into the power-play and fight nodes; Return no longer a snare; tactics K15 removed from P.16 -> R.1 (Claude, approved by Denning)
- 2026-11-08: link C.builds -> R.1: the collapse node no longer uses it; its measurement there removed (Claude)
- 2026-11-08: link P.1 -> R.2 added as a hypothesis (node fight_outcome): going after the healers (Bounty: target choice costs time; the data: groups on the healers kill more) (Bounty)
- 2026-11-08: link K.11 -> R.5 added as a hypothesis (node split_effect): the defenders' snares slow a split's work on the NPCs (Denning)
- 2026-11-08: link K.13 -> R.5 added as a hypothesis (node split_effect): a fast split gets in and out of the base (Denning)
- 2026-11-08: link K.11 -> R.1 added as a hypothesis (node collapse): how strong the defenders' snares are, not just whether there is one, decides whether a collapse kills (Bounty, Denning) (Denning)
- 2026-11-08: link P.14 -> K.4: hypothesis -> supported by data (power_play supported +0.0065) (data)
- 2026-11-08: link K.13 -> R.1: rejected -> hypothesis by data (collapse not clear yet -0.0005) (data)
- 2026-11-08: link K.11 -> R.3: supported -> hypothesis by data (run_outcome not clear yet -0.0021, capture_speed not clear yet +0.0, run_defence not clear yet -0.001) (data)
- 2026-11-08: link C.strength -> R.3: supported -> hypothesis by data (run_outcome not clear yet -0.0039, flag_swing not clear yet +0.17, capture_speed not clear yet +0.13, run_defence not clear yet -0.0034) (data)
- 2026-11-08: link C.builds -> R.3 added as a hypothesis (node run_outcome): snare skills on the bars change whether runs get through: found by discovery, approved by Denning (Denning)
- 2026-11-08: link S.scoreboard -> K.4 added as a hypothesis (node power_play): time down and flag carriers when the power play starts: found by discovery, approved by Denning (Denning)
- 2026-11-08: link S.scoreboard -> R.2 added as a hypothesis (node fight_outcome): the state at the fight's start (morale, numbers, time down, the stand, players within one spike): found by discovery, approved by Denning (Denning)
- 2026-11-08: link C.builds -> R.5 added as a hypothesis (node split_effect): the defenders' prots make a split's NPC kills harder: found by discovery, approved by Denning (Denning)
- 2026-11-08: link A.allocation -> R.3: hypothesis -> supported by data (run_outcome not clear yet -0.0001, flag_swing not clear yet -0.1, capture_speed supported +0.49, run_defence not clear yet +0.0017) (data)
- 2026-11-08: link C.map -> R.3: hypothesis -> supported by data (run_outcome not clear yet +0.0023, flag_swing not clear yet -0.03, capture_speed supported +0.45, run_defence not clear yet +0.0042) (data)
- 2026-11-08: link A.allocation -> R.3: hypothesis -> supported by data (run_outcome not clear yet -0.0001, flag_swing not clear yet -0.1, capture_speed supported +0.49, run_defence not clear yet +0.0017) (data)
- 2026-11-08: link C.map -> R.3: hypothesis -> supported by data (run_outcome not clear yet +0.0023, flag_swing not clear yet -0.03, capture_speed supported +0.45, run_defence not clear yet +0.0042) (data)
- 2026-11-08: link S.scoreboard -> R.3: hypothesis -> supported by data (flag_swing supported +0.54, run_outcome supported +0.0111, run_defence supported +0.0349) (data)
- 2026-11-08: link R.1 -> R.3: supported -> hypothesis by data (flag_swing not clear yet +0.04) (data)
- 2026-11-08: link C.strength -> R.2: supported -> hypothesis by data (fight_outcome not clear yet +0.0009) (data)
- 2026-11-08: link S.scoreboard -> R.5: hypothesis -> supported by data (split_effect supported +0.0448) (data)
- 2026-11-08: link C.builds -> R.3: hypothesis -> supported by data (run_outcome supported +0.0068, run_defence supported +0.0058) (data)
- 2026-11-08: link S.scoreboard -> K.4: hypothesis -> supported by data (power_play supported +0.0136) (data)
- 2026-11-08: link S.scoreboard -> R.2: hypothesis -> supported by data (fight_outcome supported +0.0974) (data)
- 2026-11-08: link P.14 -> K.4: supported -> hypothesis by data (power_play not clear yet +0.0033) (data)
- 2026-11-08: link K.13 -> R.1: hypothesis -> rejected by data (collapse rejected -0.0033) (data)
- 2026-11-08: link P.11 -> R.1: hypothesis -> rejected by data (collapse rejected -0.0014) (data)
- 2026-11-08: link K.5 -> K.4: supported -> hypothesis by data (power_play not clear yet +0.0084) (data)
- 2026-11-08: link C.map -> R.3: supported -> hypothesis by data (run_outcome not clear yet +0.0004, flag_swing not clear yet -0.02, capture_speed not clear yet +0.31, run_defence not clear yet +0.0006) (data)
- 2026-11-08: link P.11 -> R.5: hypothesis -> supported by data (split_effect supported +0.0034) (data)
- 2026-11-08: link A.allocation -> R.5: the data says rejected; held for Denning's ruling (data)
- 2026-11-08: link C.map -> R.3: supported -> hypothesis by data (run_outcome not clear yet +0.0004, flag_swing not clear yet -0.02, capture_speed not clear yet +0.31, run_defence not clear yet +0.0006) (data)
- 2026-11-08: link K.11 -> R.3: the data says rejected; held for Denning's ruling (data)
- 2026-11-08: link A.mesa_free -> R.3: the data says rejected; held for Denning's ruling (data)
- 2026-11-08: link P.17 -> R.2: hypothesis -> supported by data (fight_outcome supported +0.0088) (data)
- 2026-11-08: link P.9 -> R.1: supported -> hypothesis by data (collapse not clear yet +0.0073) (data)
- 2026-11-08: link P.1 -> R.2: hypothesis -> rejected by data (fight_outcome rejected -0.0027) (data)
- 2026-11-08: link K.11 -> R.5: hypothesis -> supported by data (split_effect supported +0.0061) (data)
- 2026-11-08: link K.13 -> R.5: hypothesis -> supported by data (split_effect supported +0.0056) (data)
- 2026-11-08: link C.builds -> R.3: supported -> hypothesis by data (run_outcome not clear yet +0.0025, run_defence not clear yet +0.0006) (data)
- 2026-11-08: link C.builds -> R.5: hypothesis -> supported by data (split_effect supported +0.0102) (data)
- 2026-11-08: link K.1 -> R.5 added as a hypothesis (node pit_npc_loss): damage landing on the pit NPCs (Claude)
- 2026-11-08: link K.6 -> R.5 added as a hypothesis (node pit_npc_loss): healing on the pit NPCs keeps them alive (Claude)
- 2026-11-08: link C.clock -> R.5 added as a hypothesis (node pit_npc_loss): time in the pit and the res clock (Claude)
- 2026-11-08: link K.5 -> R.1 added as a hypothesis (node collapse): a split that can heal or defend itself may not be killable, so collapsing on it wastes players (Denning, batch 10) (Denning)
- 2026-11-08: link K.1 -> R.1 added as a hypothesis (node collapse): the defenders' damage decides whether they can kill the split (Denning, batch 10) (Denning)
- 2026-11-08: link S.scoreboard -> R.1 added as a hypothesis (node collapse): what the split can get NPC-wise sets how much a collapse is worth (Denning, batch 10) (Denning)
- 2026-11-08: link K.13 -> R.1: rejected -> hypothesis by data (collapse not clear yet -0.0004) (data)
- 2026-11-08: link P.11 -> R.1: rejected -> hypothesis by data (collapse not clear yet +0.0) (data)
- 2026-11-08: link K.5 -> K.4: hypothesis -> supported by data (power_play supported +0.0126) (data)
- 2026-11-08: link K.9 -> R.1: hypothesis -> supported by data (collapse supported +0.0035) (data)
- 2026-11-08: link K.9 -> R.1: hypothesis -> supported by data (collapse supported +0.0035) (data)
- 2026-11-08: link C.map -> R.3: hypothesis -> supported by data (run_outcome supported +0.0049, flag_swing not clear yet -0.01, capture_speed supported +0.38, run_defence not clear yet +0.0038) (data)
- 2026-11-08: link C.map -> R.3: hypothesis -> supported by data (run_outcome supported +0.0049, flag_swing not clear yet -0.01, capture_speed supported +0.38, run_defence not clear yet +0.0038) (data)
- 2026-11-08: link C.strength -> R.3: hypothesis -> supported by data (run_outcome not clear yet +0.0001, flag_swing not clear yet +0.06, capture_speed supported +0.05, run_defence not clear yet -0.0002) (data)
- 2026-11-08: link C.strength -> R.5: hypothesis -> supported by data (split_effect not clear yet -0.0025, pit_npc_loss supported +0.0025) (data)
- 2026-11-08: link C.builds -> R.1: supported -> hypothesis by data (collapse not clear yet -0.0006) (data)
- 2026-11-08: link C.strength -> R.1: hypothesis -> supported by data (collapse supported +0.003) (data)
- 2026-11-08: link P.1 -> R.2: rejected -> hypothesis by data (fight_outcome not clear yet -0.0009) (data)
- 2026-11-08: link K.11 -> R.5: supported -> hypothesis by data (split_effect not clear yet +0.0035) (data)
- 2026-11-08: link K.13 -> R.5: supported -> hypothesis by data (split_effect not clear yet +0.0018) (data)
- 2026-11-08: link K.1 -> R.5: hypothesis -> supported by data (pit_npc_loss supported +0.039) (data)
- 2026-11-08: link K.6 -> R.5: hypothesis -> supported by data (pit_npc_loss supported +0.0023) (data)
- 2026-11-08: link K.1 -> R.1: hypothesis -> supported by data (collapse supported +0.0118) (data)
- 2026-11-08: link P.2 -> K.4: hypothesis -> supported by data (power_play supported +0.0069) (data)
- 2026-11-08: link P.2 -> K.4: hypothesis -> supported by data (power_play supported +0.0069) (data)
- 2026-11-08: link C.strength -> K.4: hypothesis -> supported by data (power_play supported +0.0104) (data)
- 2026-11-08: link S.scoreboard -> P.11: hypothesis -> supported by data (split_answer supported +0.25) (data)
- 2026-11-08: link C.strength -> R.3: supported -> hypothesis by data (run_outcome not clear yet -0.0015, flag_swing not clear yet +0.06, capture_speed not clear yet -0.0, run_defence not clear yet -0.0015) (data)
- 2026-11-08: link C.clock -> R.3: hypothesis -> rejected by data (flag_swing rejected -0.03) (data)
- 2026-11-08: link C.clock -> A.allocation: hypothesis -> supported by data (split_chance supported +0.0026) (data)
- 2026-11-08: link C.strength -> A.allocation: hypothesis -> rejected by data (split_chance rejected -0.0009) (data)
- 2026-11-08: link A.allocation -> R.1: hypothesis -> supported by data (collapse supported +0.003) (data)
- 2026-11-08: link C.strength -> R.1: supported -> hypothesis by data (collapse not clear yet +0.0048) (data)
- 2026-11-08: link P.20 -> R.1: hypothesis -> supported by data (collapse supported +0.0044) (data)
- 2026-11-08: link C.builds -> R.5: supported -> hypothesis by data (split_effect not clear yet +0.0064, pit_npc_loss not clear yet +0.0002) (data)
- 2026-11-08: link K.6 -> R.5: supported -> hypothesis by data (pit_npc_loss not clear yet +0.0017) (data)
- 2026-11-08: link C.clock -> R.5: hypothesis -> rejected by data (pit_npc_loss rejected -0.001) (data)
- 2026-11-09: link P.1 -> K.4: hypothesis -> supported by data (power_play supported +0.0081) (data)
- 2026-11-09: link A.allocation -> R.3: supported -> hypothesis by data (run_outcome not clear yet -0.002, flag_swing not clear yet -0.02, capture_speed not clear yet +0.3, run_defence not clear yet -0.0009) (data)
- 2026-11-09: link A.allocation -> R.3: supported -> hypothesis by data (run_outcome not clear yet -0.002, flag_swing not clear yet -0.02, capture_speed not clear yet +0.3, run_defence not clear yet -0.0009) (data)
- 2026-11-09: link S.scoreboard -> P.11: supported -> hypothesis by data (split_answer not clear yet +0.27) (data)
- 2026-11-09: link C.clock -> R.3: rejected -> hypothesis by data (flag_swing not clear yet -0.01) (data)
- 2026-11-09: link C.strength -> R.2: hypothesis -> supported by data (fight_outcome supported +0.0028) (data)
- 2026-11-09: link A.mesa_free -> P.11: supported -> hypothesis by data (split_answer not clear yet +0.37) (data)
- 2026-11-09: link C.strength -> R.5: supported -> hypothesis by data (split_effect rejected -0.003, pit_npc_loss not clear yet +0.0014) (data)
- 2026-11-09: link A.allocation -> R.1: supported -> hypothesis by data (collapse not clear yet +0.0017) (data)
- 2026-11-09: link C.strength -> R.1: hypothesis -> supported by data (collapse supported +0.0057) (data)
- 2026-11-09: link P.20 -> R.1: supported -> hypothesis by data (collapse not clear yet +0.0034) (data)
- 2026-11-09: link K.11 -> R.1: hypothesis -> supported by data (collapse supported +0.0038) (data)
- 2026-11-09: link C.clock -> R.5: rejected -> hypothesis by data (pit_npc_loss not clear yet -0.0002) (data)
- 2026-11-09: node P.21 Kiting added (step 2b: pressure.py) (Claude, from Denning's list)
- 2026-11-09: node P.22 Degen pressure added (step 2b: pressure.py) (Claude, from Denning's list)
- 2026-11-09: node P.23 Baited interrupts added (step 2b: pressure.py) (Claude, from Denning's list)
- 2026-11-09: node P.24 Offensive knockdowns added (step 2b: pressure.py) (Claude, from Denning's list)
- 2026-11-09: node P.25 Disables added (step 2b: pressure.py) (Claude, from Denning's list)
- 2026-11-09: node P.26 Cast prevention added (step 2b: pressure.py) (Claude, from Denning's list)
- 2026-11-09: link K.5 -> R.3 added as a hypothesis (node run_defence): own healing monks help defend against runs: found by discovery, approved by Denning (Denning)
- 2026-11-09: link P.24 -> K.4 added as a hypothesis (node power_play): offensive knockdowns convert a power play (Denning, session 4u) (Denning)
- 2026-11-09: link P.25 -> K.4 added as a hypothesis (node power_play): disables on the enemy healers convert a power play (Denning, session 4u) (Denning)
- 2026-11-09: link P.26 -> K.4 added as a hypothesis (node power_play): cast prevention on the enemy healers converts a power play (Denning, session 4u) (Denning)
- 2026-11-09: link P.22 -> K.4 added as a hypothesis (node power_play): degen pressure helps a power play wear the enemy down (Denning, session 4u) (Denning)
- 2026-11-09: link P.21 -> K.4 added as a hypothesis (node power_play): enemies kiting a power play's melee waste its time (Denning, session 4u) (Denning)
- 2026-11-09: link P.23 -> K.4 added as a hypothesis (node power_play): baited interrupts leave the enemy healers free (Denning, session 4u) (Denning)
- 2026-11-09: link P.21 -> R.2 added as a hypothesis (node fight_outcome): a player who kites enemy melee avoids damage and wastes the frontline's time (Denning, session 4u) (Denning)
- 2026-11-09: link P.22 -> R.2 added as a hypothesis (node fight_outcome): degen pressure (a ranger's poison on the whole team, a degen mesmer) wears a team down without showing as damage (Denning, session 4u) (Denning)
- 2026-11-09: link P.23 -> R.2 added as a hypothesis (node fight_outcome): a player who fakes out an interrupt wastes it (Denning, session 4u) (Denning)
- 2026-11-09: link P.24 -> R.2 added as a hypothesis (node fight_outcome): offensive knockdowns (a warrior landing many) stop casts and set up kills (Denning, session 4u) (Denning)
- 2026-11-09: link P.25 -> R.2 added as a hypothesis (node fight_outcome): disables (Complicate, Blackout, Power Lock, Power Block) take the enemy's key skills away (Denning, session 4u) (Denning)
- 2026-11-09: link P.26 -> R.2 added as a hypothesis (node fight_outcome): cast prevention (Shame, Diversion, Guilt) stops the enemy's casts (Denning, session 4u) (Denning)
- 2026-11-09: link C.builds -> R.2 added as a hypothesis (node fight_outcome): hex and heal skills on the bars change fights: found by discovery, approved by Denning (Denning)
- 2026-11-09: link P.11 -> R.1: hypothesis -> supported by data (collapse supported +0.0004) (data)
- 2026-11-09: link A.allocation -> R.3: hypothesis -> supported by data (run_outcome not clear yet -0.0013, flag_swing not clear yet +0.02, capture_speed supported +0.4, run_defence not clear yet -0.0011) (data)
- 2026-11-09: link A.allocation -> R.3: hypothesis -> supported by data (run_outcome not clear yet -0.0013, flag_swing not clear yet +0.02, capture_speed supported +0.4, run_defence not clear yet -0.0011) (data)
- 2026-11-09: link C.strength -> K.4: supported -> hypothesis by data (power_play not clear yet +0.006) (data)
- 2026-11-09: link S.scoreboard -> P.11: hypothesis -> supported by data (split_answer supported +0.48) (data)
- 2026-11-09: link C.builds -> P.11: hypothesis -> supported by data (split_answer supported +0.22) (data)
- 2026-11-09: link C.builds -> P.11: hypothesis -> supported by data (split_answer supported +0.22) (data)
- 2026-11-09: link C.strength -> R.2: supported -> hypothesis by data (fight_outcome not clear yet +0.0021) (data)
- 2026-11-09: link C.builds -> A.allocation: hypothesis -> supported by data (split_chance supported +0.0101) (data)
- 2026-11-09: link C.strength -> A.allocation: rejected -> hypothesis by data (split_chance not clear yet -0.0003) (data)
- 2026-11-09: link A.mesa_free -> P.11: hypothesis -> supported by data (split_answer supported +0.46) (data)
- 2026-11-09: link C.strength -> R.5: hypothesis -> supported by data (split_effect not clear yet -0.0039, pit_npc_loss supported +0.0014) (data)
- 2026-11-09: link K.11 -> R.1: supported -> hypothesis by data (collapse not clear yet +0.003) (data)
- 2026-11-09: link K.6 -> R.5: hypothesis -> supported by data (pit_npc_loss supported +0.0013) (data)
- 2026-11-09: link P.24 -> K.4: hypothesis -> supported by data (power_play supported +0.0054) (data)
- 2026-11-09: link P.25 -> K.4: hypothesis -> supported by data (power_play supported +0.0045) (data)
- 2026-11-09: link P.22 -> K.4: hypothesis -> supported by data (power_play supported +0.0024) (data)
- 2026-11-09: link P.21 -> K.4: hypothesis -> supported by data (power_play supported +0.0059) (data)
- 2026-11-09: link P.24 -> R.2: hypothesis -> supported by data (fight_outcome supported +0.0029) (data)
- 2026-11-09: link C.builds -> R.2: hypothesis -> supported by data (fight_outcome supported +0.0063) (data)
- 2026-11-09: link C.strength -> K.4: hypothesis -> supported by data (power_play supported +0.0059) (data)
- 2026-11-09: link C.builds -> P.11: supported -> hypothesis by data (split_answer not clear yet +0.09) (data)
- 2026-11-09: link C.builds -> P.11: supported -> hypothesis by data (split_answer not clear yet +0.09) (data)
- 2026-11-09: link P.19 -> R.2: the data says rejected; held for Denning's ruling (data)
- 2026-11-09: link P.20 -> R.1: hypothesis -> supported by data (collapse supported +0.0023) (data)
- 2026-11-09: link C.builds -> R.5: hypothesis -> supported by data (split_effect supported +0.008, pit_npc_loss supported +0.0028) (data)
- 2026-11-09: link K.5 -> R.1: hypothesis -> supported by data (collapse supported +0.0025) (data)
- 2026-11-09: link P.22 -> K.4: supported -> hypothesis by data (power_play not clear yet +0.0018) (data)
- 2026-11-09: link P.21 -> R.2: the data says rejected; held for Denning's ruling (data)
- 2026-11-09: link P.24 -> R.2: supported -> hypothesis by data (fight_outcome not clear yet -0.0008) (data)
- 2026-11-09: link K.13 -> R.1: the collapse node no longer uses it; its measurement there removed (Claude)
- 2026-11-09: link K.5 -> K.4: the power_play node no longer uses it; its measurement there removed (Claude)
- 2026-11-09: link A.allocation -> R.1: the collapse node no longer uses it; its measurement there removed (Claude)
- 2026-11-09: link K.1 -> R.5: the pit_npc_loss node no longer uses it; its measurement there removed (Claude)
- 2026-11-09: link P.21 -> K.4: the power_play node no longer uses it; its measurement there removed (Claude)
- 2026-11-09: link P.23 -> K.4: the power_play node no longer uses it; its measurement there removed (Claude)
- 2026-11-09: link P.11 -> R.1: supported -> hypothesis by data (collapse not clear yet +0.0009) (data)
- 2026-11-09: link K.9 -> R.1: supported -> hypothesis by data (collapse not clear yet +0.0067) (data)
- 2026-11-09: link K.9 -> R.1: supported -> hypothesis by data (collapse not clear yet +0.0067) (data)
- 2026-11-09: link A.allocation -> R.5: hypothesis -> supported by data (split_effect not clear yet +0.0011, pit_npc_loss supported +0.0034) (data)
- 2026-11-09: link C.strength -> R.5: supported -> hypothesis by data (split_effect not clear yet +0.0001, pit_npc_loss not clear yet +0.0022) (data)
- 2026-11-09: link K.6 -> R.5: supported -> hypothesis by data (pit_npc_loss not clear yet +0.0005) (data)
- 2026-11-09: link C.clock -> R.5: hypothesis -> supported by data (pit_npc_loss supported +0.0025) (data)
- 2026-11-09: link K.5 -> K.4: supported -> concurrent (the enemy's response during the window; shown beside the node, not fitted; Denning, November 2026 review) (Denning)
- 2026-11-09: link K.1 -> R.5: supported -> concurrent (the enemy's response during the window; shown beside the node, not fitted; Denning, November 2026 review) (Denning)
- 2026-11-09: link P.21 -> K.4: supported -> concurrent (the enemy's response during the window; shown beside the node, not fitted; Denning, November 2026 review) (Denning)
- 2026-11-09: link P.23 -> K.4: hypothesis -> concurrent (the enemy's response during the window; shown beside the node, not fitted; Denning, November 2026 review) (Denning)
- 2026-11-09: node P.27 Pre-kiting added: split from P.21 Kiting so Denning's rulings on the two can differ (R-283) (Denning)
- 2026-11-09: link P.19 -> R.2 (Blind on enemies into fight outcome): Denning lets the data reject it for now (R-283); it sits as the data reads it and is remeasured each run (Denning)
- 2026-11-09: link P.21 -> R.2 (kiting into fight outcome): kept by Denning's ruling whatever the data says (R-283); the joint kiting + pre-kiting measurement dropped, remeasured as kiting alone (Denning)
- 2026-11-09: link P.27 -> R.2 added (pre-kiting into fight outcome), split from P.21; Denning lets the data reject it for now (R-283) (Denning)
- 2026-11-09: link P.11 -> R.1: the collapse node no longer uses it; its measurement there removed (Claude)
- 2026-11-09: link S.scoreboard -> R.1: the collapse node no longer uses it; its measurement there removed (Claude)
- 2026-11-09: link K.9 -> R.1: hypothesis -> supported by data (collapse supported +0.0069) (data)
- 2026-11-09: link K.9 -> R.1: hypothesis -> supported by data (collapse supported +0.0069) (data)
- 2026-11-09: link C.builds -> P.11: hypothesis -> supported by data (split_answer supported +0.1) (data)
- 2026-11-09: link C.builds -> P.11: hypothesis -> supported by data (split_answer supported +0.1) (data)
- 2026-11-09: link C.strength -> R.3: hypothesis -> supported by data (run_outcome not clear yet +0.0003, flag_swing not clear yet +0.05, capture_speed supported +0.06, run_defence not clear yet +0.0002) (data)
- 2026-11-09: link P.19 -> R.2: hypothesis -> rejected by data (fight_outcome rejected -0.0014) (data)
- 2026-11-09: link P.20 -> R.1: supported -> hypothesis by data (collapse not clear yet +0.0026) (data)
- 2026-11-09: R-288 to R-291: direction signs ruled; runner_escapes retired from run outcome (R.3); four measurement proposals queued (Denning)
- 2026-11-09: link K.11 -> K.4: hypothesis -> rejected by data (power_play rejected -0.0012) (data)
- 2026-11-09: link C.builds -> P.11: supported -> hypothesis by data (split_answer not clear yet +0.0) (data)
- 2026-11-09: link C.builds -> P.11: supported -> hypothesis by data (split_answer not clear yet +0.0) (data)
- 2026-11-09: link C.strength -> R.5: hypothesis -> supported by data (split_effect not clear yet +0.0001, pit_npc_loss supported +0.0027) (data)
- 2026-11-09: link P.20 -> R.1: hypothesis -> supported by data (collapse supported +0.0034) (data)
- 2026-11-09: link P.1 -> R.2: hypothesis -> rejected by data (fight_outcome rejected -0.0011) (data)
- 2026-11-09: link C.clock -> R.5: supported -> hypothesis by data (pit_npc_loss not clear yet +0.0011) (data)
- 2026-11-09: link K.5 -> R.1: supported -> hypothesis by data (collapse not clear yet +0.0017) (data)
- 2026-11-09: link P.25 -> K.4: supported -> hypothesis by data (power_play not clear yet +0.0036) (data)
- 2026-11-09: link P.26 -> K.4: the data says rejected; held for Denning's ruling (data)
- 2026-11-09: link K.11 -> K.4: rejected -> hypothesis by data (power_play not clear yet -0.0003) (data)
- 2026-11-09: link C.strength -> R.3: supported -> hypothesis by data (run_outcome not clear yet +0.0005, flag_swing not clear yet +0.06, capture_speed not clear yet +0.04, run_defence not clear yet +0.0008) (data)
- 2026-11-09: link P.19 -> R.2: rejected -> hypothesis by data (fight_outcome not clear yet -0.001) (data)
- 2026-11-09: link A.allocation -> R.1: hypothesis -> supported by data (collapse supported +0.0028) (data)
- 2026-11-09: link P.1 -> R.2: rejected -> hypothesis by data (fight_outcome not clear yet +0.0006) (data)
- 2026-11-09: link K.6 -> R.5: hypothesis -> supported by data (pit_npc_loss supported +0.0006) (data)
- 2026-11-09: link C.clock -> R.5: hypothesis -> supported by data (pit_npc_loss supported +0.0021) (data)
- 2026-11-09: link K.5 -> R.1: hypothesis -> supported by data (collapse supported +0.002) (data)
- 2026-11-09: link P.24 -> K.4: supported -> hypothesis by data (power_play not clear yet +0.0069) (data)
- 2026-11-09: link P.25 -> K.4: hypothesis -> supported by data (power_play supported +0.0063) (data)
- 2026-11-09: link P.26 -> R.2: the data says rejected; held for Denning's ruling (data)
- 2026-11-09: link C.builds -> R.2: supported -> hypothesis by data (fight_outcome not clear yet +0.0021) (data)
