# Event-layer measures (step 1), 150 matches

Descriptive only: each measure split by who won the fight (or how a run, split or power play turned out). Step 2's node models test these as causes on unseen matches.

## Wrong casts (per player per fight)
- healer, interrupted after casting into a ready interrupt (no cancel): winners 0.11 (3120), losers 0.33 (2953)
- healer, casts interrupted: winners 0.12 (3120), losers 0.36 (2953)
- healer, casts while Dazed: winners 0.0 (3120), losers 0.03 (2953)
- healer, attacks while Blind: winners 0.0 (3120), losers 0.0 (2953)
- midline, interrupted after casting into a ready interrupt (no cancel): winners 0.17 (3565), losers 0.28 (3110)
- midline, casts interrupted: winners 0.18 (3565), losers 0.29 (3110)
- midline, casts while Dazed: winners 0.0 (3565), losers 0.01 (3110)
- midline, attacks while Blind: winners 0.01 (3565), losers 0.03 (3110)
- frontline, interrupted after casting into a ready interrupt (no cancel): winners 0.04 (1810), losers 0.12 (1462)
- frontline, casts interrupted: winners 0.05 (1810), losers 0.13 (1462)
- frontline, casts while Dazed: winners 0.0 (1810), losers 0.0 (1462)
- frontline, attacks while Blind: winners 0.11 (1810), losers 0.06 (1462)

## Frontline peel (share of frontline damage, per player per fight)
- on attackers of own backline: winners 0.47, losers 0.54 (1697 / 1357)
- on enemy healers: winners 0.42, losers 0.32 (1697 / 1357)

## Strips, Blind and hex removal (per team per match; winners against losers of the match)
- strips per match: winners 26.06, losers 20.61 (150 / 150 team-matches)
- useful share of strips: winners 0.65, losers 0.69 (145 / 134 team-matches)
- prots stripped off targets under attack: winners 6.74, losers 4.97 (150 / 150 team-matches)
- wasted removal casts: winners 20.47, losers 11.69 (150 / 150 team-matches)
- Blinds on enemy frontline: winners 0.82, losers 1.79 (150 / 150 team-matches)
- defensive Blinds (on a player hitting own healers): winners 0.24, losers 0.75 (150 / 150 team-matches)
- hexes on own healers removed (share): winners 0.33, losers 0.21 (136 / 143 team-matches)
- median seconds a hex stayed on own healers: winners 6.24, losers 5.8 (136 / 143 team-matches)

## Step 2a: right strip targets, right hexes removed, damage against the role's usual
Values from data (eventlayer_values.json): enchantments by recorded output per second up, hexes by recorded damage plus the drop in the hexed player's output.
- most valuable enchantments to strip (per second up): Patient Spirit 55.04, Aura of Faith 42.0, Reversal of Fortune 25.78, Balthazar's Aura 23.78, Double Dragon 23.7, Holy Veil 21.14, Divine Spirit 20.69, Grenth's Aura 20.37
- most costly hexes (per second on): Deep Freeze 111.64 (direct 111.75, output drop -0.11, 17), Shatterstone 70.42 (direct 72.77, output drop -2.35, 928), Incendiary Bonds 59.26 (direct 59.46, output drop -0.2, 51), Smoldering Embers 55.12 (direct 57.54, output drop -2.42, 1850), Lightning Strike 43.39 (direct 44.42, output drop -1.03, 6225), Illusion of Pain 29.91 (direct 31.21, output drop -1.3, 42), Backfire 25.32 (direct 23.96, output drop 1.36, 198), Mind Freeze 24.83 (direct 23.05, output drop 1.78, 845)
- strips on the best target in range (share): winners 0.52, losers 0.44 (145 / 134 team-matches)
- hex removals that took the most costly hex in range (share): winners 0.66, losers 0.63 (136 / 137 team-matches)
- value-weighted seconds a removed hex stayed on: winners 4.79, losers 5.29 (136 / 133 team-matches)
- healer, damage against the role's usual: winners 1.32 (96), losers 0.92 (72)
- midline, damage against the role's usual: winners 1.33 (3565), losers 0.89 (3110)
- frontline, damage against the role's usual: winners 1.34 (1810), losers 0.78 (1462)

## Spike timing (kill rate by how tightly the big hits landed)
- spread 0 to 0.5 s: killed 61 of 174 (35%)
- spread 0.5 to 1.5 s: killed 183 of 416 (44%)
- spread 1.5 to 9 s: killed 209 of 644 (32%)

## Run timing (capture rate)
- into an enemy power play: 184 of 357 (52%); otherwise 983 of 1916 (51%)
- enemy holds, its boost in 0 to 30 s: 36 of 101 (36%)
- enemy holds, its boost in 30 to 60 s: 94 of 187 (50%)
- enemy holds, its boost in 60 to 121 s: 535 of 905 (59%)
- runner Crippled during the run: 129 of 184 (70%); not: 1038 of 2089 (50%) (read with care: runs that get far are the ones that get Crippled; the run-outcome node of step 2 reads it at the same point of the run)
- runner knocked down: 106 of 173 (61%)

## Enemy captures (from the defending side)
- captures: 1167; runner never pushed: 591; median run 34 s; median defenders free 8; nearest defender at mid-run, median 1799

## Splits
- splits: 965, into the base: 394
- answered on time (15 s or less): 335; pit NPCs killed per split 0.67, split deaths 0.32
- answered in 15 to 60 s: 20; pit NPCs killed per split 0.95, split deaths 0.10
- answered after 60 s: 5; pit NPCs killed per split 3.60, split deaths 0.20
- never answered: 34; pit NPCs killed per split 0.74
- size 1: 364; enemies drawn 1.3, own main minus enemy main +0.1, pit kills 0.37
- size 2: 245; enemies drawn 1.3, own main minus enemy main -0.0, pit kills 0.45
- size 3+: 356; enemies drawn 1.4, own main minus enemy main -0.4, pit kills 0.44

## Power plays (all sizes)
- 1 up: 1032; killed in 421 (41%); lost a player in 122
- 2 up: 207; killed in 100 (48%); lost a player in 24
- 3+ up: 131; killed in 77 (59%); lost a player in 15
- why the enemy was short (player-seconds): dead 17274, push side 8660, backside 7581, running flag 2413, enemy pit 2091, enemy base 1498
