# Event-layer measures (step 1), 90 matches

Descriptive only: each measure split by who won the fight (or how a run, split or power play turned out). Step 2's node models test these as causes on unseen matches.

## Wrong casts (per player per fight)
- healer, interrupted after casting into a ready interrupt (no cancel): winners 0.09 (1920), losers 0.31 (1825)
- healer, casts interrupted: winners 0.11 (1920), losers 0.34 (1825)
- healer, casts while Dazed: winners 0.01 (1920), losers 0.02 (1825)
- healer, attacks while Blind: winners 0 (1920), losers 0.0 (1825)
- midline, interrupted after casting into a ready interrupt (no cancel): winners 0.18 (2388), losers 0.23 (1950)
- midline, casts interrupted: winners 0.2 (2388), losers 0.25 (1950)
- midline, casts while Dazed: winners 0.0 (2388), losers 0.01 (1950)
- midline, attacks while Blind: winners 0.02 (2388), losers 0.03 (1950)
- frontline, interrupted after casting into a ready interrupt (no cancel): winners 0.04 (1003), losers 0.11 (950)
- frontline, casts interrupted: winners 0.05 (1003), losers 0.12 (950)
- frontline, casts while Dazed: winners 0.0 (1003), losers 0.0 (950)
- frontline, attacks while Blind: winners 0.07 (1003), losers 0.15 (950)

## Frontline peel (share of frontline damage, per player per fight)
- on attackers of own backline: winners 0.48, losers 0.52 (950 / 888)
- on enemy healers: winners 0.42, losers 0.3 (950 / 888)

## Strips, Blind and hex removal (per team per match; winners against losers of the match)
- strips per match: winners 25.16, losers 22.38 (90 / 90 team-matches)
- useful share of strips: winners 0.67, losers 0.72 (85 / 82 team-matches)
- prots stripped off targets under attack: winners 6.72, losers 4.59 (90 / 90 team-matches)
- wasted removal casts: winners 16.4, losers 10.94 (90 / 90 team-matches)
- Blinds on enemy frontline: winners 2.86, losers 0.88 (90 / 90 team-matches)
- defensive Blinds (on a player hitting own healers): winners 0.43, losers 0.27 (90 / 90 team-matches)
- hexes on own healers removed (share): winners 0.32, losers 0.21 (79 / 89 team-matches)
- median seconds a hex stayed on own healers: winners 6.49, losers 5.82 (79 / 89 team-matches)

## Step 2a: right strip targets, right hexes removed, damage against the role's usual
Values from data (eventlayer_values.json): enchantments by recorded output per second up, hexes by recorded damage plus the drop in the hexed player's output.
- most valuable enchantments to strip (per second up): Dwayna's Sorrow 60.27, Patient Spirit 54.53, Aura of Faith 43.36, Reversal of Fortune 26.61, Double Dragon 25.39, Holy Veil 23.7, Balthazar's Aura 22.26, Grenth's Aura 19.24
- most costly hexes (per second on): Deep Freeze 162.92 (direct 166.32, output drop -3.4, 11), Shatterstone 66.03 (direct 67.73, output drop -1.7, 532), Incendiary Bonds 64.11 (direct 59.11, output drop 5.0, 39), Smoldering Embers 53.58 (direct 56.54, output drop -2.97, 1316), Lightning Strike 41.92 (direct 43.0, output drop -1.07, 4798), Illusion of Pain 29.81 (direct 31.37, output drop -1.56, 40), Backfire 25.08 (direct 24.06, output drop 1.01, 191), Life Siphon 24.2 (direct 15.81, output drop 8.39, 9)
- strips on the best target in range (share): winners 0.56, losers 0.45 (85 / 82 team-matches)
- hex removals that took the most costly hex in range (share): winners 0.66, losers 0.59 (79 / 85 team-matches)
- value-weighted seconds a removed hex stayed on: winners 4.83, losers 5.18 (77 / 83 team-matches)
- healer, damage against the role's usual: winners 1.13 (104), losers 1.02 (48)
- midline, damage against the role's usual: winners 1.39 (2388), losers 0.85 (1950)
- frontline, damage against the role's usual: winners 1.31 (1003), losers 0.79 (950)

## Spike timing (kill rate by how tightly the big hits landed)
- spread 0 to 0.5 s: killed 59 of 131 (45%)
- spread 0.5 to 1.5 s: killed 115 of 296 (39%)
- spread 1.5 to 9 s: killed 122 of 424 (29%)

## Run timing (capture rate)
- into an enemy power play: 122 of 215 (57%); otherwise 647 of 1195 (54%)
- enemy holds, its boost in 0 to 30 s: 25 of 36 (69%)
- enemy holds, its boost in 30 to 60 s: 49 of 106 (46%)
- enemy holds, its boost in 60 to 121 s: 369 of 568 (65%)
- runner Crippled during the run: 78 of 102 (76%); not: 691 of 1308 (53%) (read with care: runs that get far are the ones that get Crippled; the run-outcome node of step 2 reads it at the same point of the run)
- runner knocked down: 72 of 103 (70%)

## Enemy captures (from the defending side)
- captures: 769; runner never pushed: 369; median run 34 s; median defenders free 7; nearest defender at mid-run, median 1967

## Splits
- splits: 564, into the base: 225
- answered on time (15 s or less): 202; pit NPCs killed per split 0.63, split deaths 0.33
- answered in 15 to 60 s: 10; pit NPCs killed per split 0.70, split deaths 0.60
- never answered: 13; pit NPCs killed per split 0.85
- size 1: 191; enemies drawn 1.4, own main minus enemy main +0.1, pit kills 0.23
- size 2: 126; enemies drawn 1.1, own main minus enemy main -0.3, pit kills 0.28
- size 3+: 247; enemies drawn 1.3, own main minus enemy main -0.4, pit kills 0.43

## Power plays (all sizes)
- 1 up: 599; killed in 235 (39%); lost a player in 67
- 2 up: 114; killed in 60 (53%); lost a player in 15
- 3+ up: 61; killed in 35 (57%); lost a player in 8
- why the enemy was short (player-seconds): dead 10110, backside 4981, push side 4410, running flag 1576, enemy pit 1087, enemy base 680
