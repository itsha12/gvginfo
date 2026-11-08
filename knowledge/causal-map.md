*Generated from data/model/causal_map.json by tools/replay_analysis/causal_map.py: don't edit this page; tell Claude or edit the JSON (each change is logged with a reason).*

# Causal map (version 11)

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
- **Clock**: the res clock and the minute change when a split pays (Claude; hypothesis)
- **Build features**: split builds (speed, snares) and the enemy's snares decide whether a split is possible (Claude; hypothesis)
- **Team strength**: stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude; hypothesis)

Measured on unseen matches (learnednodes.py; gain = how much worse the node predicts without the link):
- Scoreboard (`S.scoreboard`), split chance node: gain +0.0153 (+/- 0.0039, log loss), supported, 133 matches
- Clock (`C.clock`), split chance node: gain +0.0007 (+/- 0.0019, log loss), not clear yet, 133 matches
- Build features (`C.builds`), split chance node: gain -0.0005 (+/- 0.0032, log loss), not clear yet, 133 matches
- Team strength (`C.strength`), split chance node: gain -0.0009 (+/- 0.0026, log loss), not clear yet, 133 matches

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
- **Scoreboard, Plan, Clock, Build features, Team strength**: decisions are made in a situation: the engine learns what teams usually do in each situation (the usual play), so a choice that does better than the usual play stands out (Claude; hypothesis)
- **Build features**: individual bars matter: a Mes/A defending 1v1 with a snare plays differently from one without (Denning; hypothesis; `B23`)
- **Mesmers free to defend**: free defenders near the base answer a split sooner (Denning; supported)
- **Allocation**: a bigger split draws more defenders (Claude; supported)

Measured on unseen matches (learnednodes.py; gain = how much worse the node predicts without the link):
- Allocation (`A.allocation`), split answer node: gain +0.81 (+/- 0.37, mean absolute error (s)), supported, 94 matches
- Mesmers free to defend (`A.mesa_free`), split answer node: gain +0.53 (+/- 0.22, mean absolute error (s)), supported, 94 matches
- Scoreboard (`S.scoreboard`), split answer node: gain +0.09 (+/- 0.14, mean absolute error (s)), not clear yet, 94 matches
- Team strength (`C.strength`), split answer node: gain +0.04 (+/- 0.06, mean absolute error (s)), not clear yet, 94 matches
- Clock (`C.clock`), split answer node: gain +0.02 (+/- 0.07, mean absolute error (s)), not clear yet, 94 matches

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
- **Damage potential v healing, Burst timing, Kiting and spacing, Commitment**: a 5v3 fails to convert when its heads hide few damage dealers against healers, its damage is shut down, its bursts don't line up, the 3 kite to their pit or NPCs, or it doesn't commit (Claude, confirmed; hypothesis; `J3`)
- **Damage uptime**: a 5v3 fails to convert when its heads hide few damage dealers against healers, its damage is shut down, its bursts don't line up, the 3 kite to their pit or NPCs, or it doesn't commit (Claude, confirmed; supported; `J3`)
- **Flag lead**: a team down on flags must send a runner soon, so its power play is shorter and less committed than its numbers suggest (Denning; hypothesis; `J5`)
- **Control received, Burst timing**: a team can't kill because of the enemy's defence (prots, blocks), shutdown of its spikers (interrupts, knockdowns, Blind, strips) or spread damage (Claude, confirmed; hypothesis; `K12`)
- **Mitigation**: a team can't kill because of the enemy's defence (prots, blocks), shutdown of its spikers (interrupts, knockdowns, Blind, strips) or spread damage (Claude, confirmed; supported; `K12`)
- **Target choice**: hitting the wrong player matters but isn't huge (Denning; hypothesis; `K12`)
- **Matchup**: the matchup sets what each capacity can be expected to be; a team can play well and still lose a hard matchup (how much comes from data) (Denning; hypothesis; `J10`)
- **Team strength**: stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude; hypothesis)
- **Build features**: a snare on the split defender makes a collapse on a lone attacker much more likely to kill; without one, holding 1v1 is the aim (Denning; supported; `S31` `B23`)
- **Allocation**: a power play is any numbers advantage at main, an 8v7 while the enemy runs included (Denning; supported)

Measured on unseen matches (learnednodes.py; gain = how much worse the node predicts without the link):
- Allocation (`A.allocation`), power play node: gain +0.0611 (+/- 0.0084, log loss), supported, 133 matches
- Damage uptime (`K.2`), power play node: gain +0.0311 (+/- 0.0074, log loss), supported, 133 matches
- Mitigation (`K.5`), power play node: gain +0.0125 (+/- 0.0052, log loss), supported, 133 matches
- Burst timing (`P.2`), power play node: gain +0.007 (+/- 0.0053, log loss), not clear yet, 133 matches
- Team strength (`C.strength`), power play node: gain +0.007 (+/- 0.0067, log loss), not clear yet, 133 matches
- Commitment (`P.14`), power play node: gain +0.0066 (+/- 0.0034, log loss), not clear yet, 133 matches
- Flag lead (`R.3`), power play node: gain +0.0039 (+/- 0.0028, log loss), not clear yet, 133 matches
- Control received (`K.11`), power play node: gain -0.0016 (+/- 0.0022, log loss), not clear yet, 133 matches
- Target choice (`P.1`), power play node: gain -0.0027 (+/- 0.002, log loss), not clear yet, 133 matches

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
- **Mobility**: a splitting ranger dies to snares or a fast collapse, an escape on recharge or interrupted, going too deep into knights and Lord, or staying after a second defender arrives (Claude, confirmed; rejected; `J4`)
- **Kiting and spacing, Split answer**: a splitting ranger dies to snares or a fast collapse, an escape on recharge or interrupted, going too deep into knights and Lord, or staying after a second defender arrives (Claude, confirmed; hypothesis; `J4`)
- **Res timing**: good teams wait for their dead to return before fighting (Denning; hypothesis; `J8`)
- **Prot timing, Health ceiling, Heal targeting, Monk uptime, Kiting and spacing**: a team heals a lot but still loses a player when heals arrive instead of prots, the health ceiling is low (DP, Deep Wound), healing goes elsewhere, heals are late or interrupted, or the victim can't kite (Claude; hypothesis; `M17`)
- **Health ceiling**: death penalty stacking against a spike team makes every later spike easier (Denning; hypothesis; `K4`)
- **Sustain margin**: a group whose margin is negative loses players (Claude; hypothesis)
- **Death timing on purpose**: teams time kills and the dying team may choose to die before time; a death's cost depends on when it happens, and some deaths may be positive (energy reset, a short wait) (Denning; hypothesis; `K14` `K15` `K1` `K2`)
- **Fight state**: a team losing its fight is about to take deaths (data; hypothesis)
- **Hex pressure**: hexes on a player or its healers make it easier to kill (Claude; hypothesis)
- **Collapse timing**: collapse timing: defenders arriving together kill a split member (Denning; supported)
- **Build features**: a snare on the split defender makes a collapse on a lone attacker much more likely to kill (Denning; supported)
- **Allocation**: a split outnumbered at the point of contact dies (Claude; hypothesis)
- **Team strength**: stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude; hypothesis)
- **Split depth**: the deeper the splitters are in the base (nearer the pit), the more likely they die to a collapse (Denning; hypothesis)

Measured on unseen matches (learnednodes.py; gain = how much worse the node predicts without the link):
- Collapse timing (`P.9`), collapse node: gain +0.0102 (+/- 0.0048, log loss), supported, 120 matches
- Build features (`C.builds`), collapse node: gain +0.0047 (+/- 0.002, log loss), supported, 120 matches
- Allocation (`A.allocation`), collapse node: gain +0.0029 (+/- 0.0016, log loss), not clear yet, 120 matches
- Team strength (`C.strength`), collapse node: gain +0.0018 (+/- 0.0029, log loss), not clear yet, 120 matches
- Split answer (`P.11`), collapse node: gain +0.0011 (+/- 0.0023, log loss), not clear yet, 120 matches
- Split depth (`P.20`), collapse node: gain -0.0004 (+/- 0.0038, log loss), not clear yet, 120 matches
- Mobility (`K.13`), collapse node: gain -0.0033 (+/- 0.0013, log loss), rejected, 120 matches

### Wipes `R.2`
fights where 3+ players or 2+ monks die. *Measured: fights.*

Caused by:
- **Collapse timing**: collapse timing is very important (Denning; hypothesis; `J7`)
- **Allocation**: numbers in a fight decide much of it (Denning; supported)
- **Peel**: frontline defensive peel (hitting or snaring enemies on its own backline) protects the healers (Denning; hypothesis)
- **Wrong casts**: wrong casts lose fights: casting into ready interrupts without cancelling, casting while Dazed, attacking while Blind (Denning; hypothesis)
- **Enchantment strips**: strips on the right target (Elementalist enchantments when defensive, prots off a target under attack) (Denning; hypothesis)
- **Blind on enemies**: Blind on the enemy frontline, above all on players hitting own healers, is defensive play (Denning; hypothesis)
- **Burst timing**: off spike timing fails to kill (Denning; supported)
- **Pressure**: damage output against the role's usual (Denning; supported)
- **Condition removal**: the right hexes removed, and fast (Denning; hypothesis)
- **Team strength**: stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude; supported)

Measured on unseen matches (learnednodes.py; gain = how much worse the node predicts without the link):
- Team strength (`C.strength`), fight outcome node: gain +0.0478 (+/- 0.0119, log loss), supported, 133 matches
- Allocation (`A.allocation`), fight outcome node: gain +0.0439 (+/- 0.0086, log loss), supported, 133 matches
- Burst timing (`P.2`), fight outcome node: gain +0.0335 (+/- 0.0119, log loss), supported, 133 matches
- Pressure (`K.1`), fight outcome node: gain +0.032 (+/- 0.0134, log loss), supported, 133 matches
- Wrong casts (`P.17`), fight outcome node: gain +0.0155 (+/- 0.0103, log loss), not clear yet, 133 matches
- Enchantment strips (`P.18`), fight outcome node: gain +0.0038 (+/- 0.0036, log loss), not clear yet, 133 matches
- Peel (`P.13`), fight outcome node: gain +0.0007 (+/- 0.0009, log loss), not clear yet, 133 matches
- Blind on enemies (`P.19`), fight outcome node: gain -0.0006 (+/- 0.0017, log loss), not clear yet, 133 matches
- Condition removal (`P.5`), fight outcome node: gain -0.0028 (+/- 0.0031, log loss), not clear yet, 133 matches

### Flag lead `R.3`
the flag position (response on the next capture exchange). *Measured: scoreboard.*

Caused by:
- **Run timing and runner choice**: being up on flags is the better position to boost and to run: runner trips, waiting runners, backup flags, routes (Denning; supported; `F1` `F2` `F3` `F4`)
- **Allocation, Map geometry**: being up on flags is the better position to boost and to run: runner trips, waiting runners, backup flags, routes (Denning; hypothesis; `F1` `F2` `F3` `F4`)
- **Allocation**: a team splitting has a different ability to run the flag (Denning; hypothesis; `J1`)
- **Run timing and runner choice**: a flag parked in base is a team deciding not to run yet; a long hand-off away from base is a response to a push or death, not double running (Denning; supported; `F33`)
- **Commitment**: a team killing during the enemy's flag cycle answers later, deliberately: it finishes the power play, then runs (Denning; hypothesis; `F34`)
- **Mobility**: runners with speed skills carry far faster than average; the flag model uses each runner's measured speed (Claude; mechanical; `F35`)
- **Map geometry**: the length of the flag run (Y) and the distance from the pits to the stand shape the flag game (Claude; hypothesis)
- **Control received**: control on the runner (Cripple, knockdowns) stops a run; read at the same point of every run (Denning; supported)
- **Team strength**: stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude; supported)
- **Scoreboard**: a flag lead tends to grow or shrink by how it stands now (boost and run timing) (Claude; hypothesis)
- **Deaths**: deaths lose flag position: the runner, the escort or the main (Claude; supported)
- **Clock**: the res clock and the minute change what a run can do (Claude; hypothesis)
- **Mesmers free to defend**: defenders free to push a runner slow the enemy's capture (Denning; hypothesis)

Measured on unseen matches (learnednodes.py; gain = how much worse the node predicts without the link):
- Run timing and runner choice (`P.10`), flag swing node: gain +0.36 (+/- 0.13, mean absolute error (s)), supported, 133 matches
- Scoreboard (`S.scoreboard`), flag swing node: gain +0.18 (+/- 0.18, mean absolute error (s)), not clear yet, 133 matches
- Team strength (`C.strength`), flag swing node: gain +0.17 (+/- 0.11, mean absolute error (s)), not clear yet, 133 matches
- Control received (`K.11`), capture speed node: gain +0.12 (+/- 0.05, mean absolute error (s)), supported, 125 matches
- Team strength (`C.strength`), capture speed node: gain +0.1 (+/- 0.03, mean absolute error (s)), supported, 125 matches
- Deaths (`R.1`), flag swing node: gain +0.05 (+/- 0.02, mean absolute error (s)), supported, 133 matches
- Run timing and runner choice (`P.10`), run outcome node: gain +0.0107 (+/- 0.0053, log loss), supported, 133 matches
- Allocation (`A.allocation`), capture speed node: gain +0.01 (+/- 0.13, mean absolute error (s)), not clear yet, 125 matches
- Map geometry (`C.map`), run defence node: gain +0.0014 (+/- 0.0031, log loss), not clear yet, 133 matches
- Map geometry (`C.map`), run outcome node: gain +0.0009 (+/- 0.0025, log loss), not clear yet, 133 matches
- Mesmers free to defend (`A.mesa_free`), run defence node: gain +0.0008 (+/- 0.0011, log loss), not clear yet, 133 matches
- Control received (`K.11`), run outcome node: gain +0.0002 (+/- 0.0012, log loss), not clear yet, 133 matches
- Clock (`C.clock`), flag swing node: gain +0.0 (+/- 0.04, mean absolute error (s)), not clear yet, 133 matches
- Team strength (`C.strength`), run outcome node: gain -0.001 (+/- 0.0029, log loss), not clear yet, 133 matches
- Team strength (`C.strength`), run defence node: gain -0.0023 (+/- 0.0022, log loss), not clear yet, 133 matches
- Allocation (`A.allocation`), run outcome node: gain -0.0031 (+/- 0.0037, log loss), not clear yet, 133 matches
- Allocation (`A.allocation`), run defence node: gain -0.0031 (+/- 0.0028, log loss), not clear yet, 133 matches
- Map geometry (`C.map`), flag swing node: gain -0.02 (+/- 0.02, mean absolute error (s)), not clear yet, 133 matches
- Allocation (`A.allocation`), flag swing node: gain -0.03 (+/- 0.11, mean absolute error (s)), not clear yet, 133 matches
- Map geometry (`C.map`), capture speed node: gain -0.08 (+/- 0.08, mean absolute error (s)), not clear yet, 125 matches

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
- **Team strength**: stronger teams play better at everything; kept in every model so play isn't confused with strength (Claude; hypothesis)
- **Scoreboard**: a pit already short of NPCs, or a base with few free defenders, loses an NPC to a split more easily (Claude; hypothesis)

Measured on unseen matches (learnednodes.py; gain = how much worse the node predicts without the link):
- Scoreboard (`S.scoreboard`), split effect node: gain +0.0056 (+/- 0.0146, log loss), not clear yet, 94 matches
- Split answer (`P.11`), split effect node: gain -0.0002 (+/- 0.003, log loss), not clear yet, 94 matches
- Allocation (`A.allocation`), split effect node: gain -0.0027 (+/- 0.0042, log loss), not clear yet, 94 matches
- Monk load (`K.8`), split effect node: gain -0.0037 (+/- 0.0021, log loss), not clear yet, 94 matches
- Team strength (`C.strength`), split effect node: gain -0.0044 (+/- 0.0079, log loss), not clear yet, 94 matches

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
