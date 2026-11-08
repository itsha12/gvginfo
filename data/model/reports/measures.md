# Event-layer measures (step 1), 95 matches

Descriptive only: each measure split by who won the fight (or how a run, split or power play turned out). Step 2's node models test these as causes on unseen matches.

## Wrong casts (per player per fight)
- healer, interrupted after casting into a ready interrupt (no cancel): winners 0.16 (1745), losers 0.39 (1617)
- healer, casts interrupted: winners 0.17 (1745), losers 0.41 (1617)
- healer, casts while Dazed: winners 0.01 (1745), losers 0.02 (1617)
- healer, attacks while Blind: winners 0.0 (1745), losers 0.0 (1617)
- midline, interrupted after casting into a ready interrupt (no cancel): winners 0.18 (2127), losers 0.29 (1738)
- midline, casts interrupted: winners 0.19 (2127), losers 0.3 (1738)
- midline, casts while Dazed: winners 0.0 (2127), losers 0.01 (1738)
- midline, attacks while Blind: winners 0.01 (2127), losers 0.04 (1738)
- frontline, interrupted after casting into a ready interrupt (no cancel): winners 0.04 (1001), losers 0.13 (973)
- frontline, casts interrupted: winners 0.04 (1001), losers 0.14 (973)
- frontline, casts while Dazed: winners 0.01 (1001), losers 0.0 (973)
- frontline, attacks while Blind: winners 0.15 (1001), losers 0.17 (973)

## Frontline peel (share of frontline damage, per player per fight)
- on attackers of own backline: winners 0.48, losers 0.5 (993 / 938)
- on enemy healers: winners 0.41, losers 0.33 (993 / 938)

## Strips, Blind and hex removal (per team per match; winners against losers of the match)
- strips per match: winners 27, losers 18.71 (95 / 95 team-matches)
- useful share of strips: winners 0.71, losers 0.68 (93 / 82 team-matches)
- prots stripped off targets under attack: winners 6.16, losers 4.73 (95 / 95 team-matches)
- wasted removal casts: winners 19.34, losers 13.83 (95 / 95 team-matches)
- Blinds on enemy frontline: winners 1.88, losers 2.79 (95 / 95 team-matches)
- defensive Blinds (on a player hitting own healers): winners 0.44, losers 0.87 (95 / 95 team-matches)
- hexes on own healers removed (share): winners 0.29, losers 0.23 (92 / 91 team-matches)
- median seconds a hex stayed on own healers: winners 7.25, losers 5.77 (92 / 91 team-matches)

## Step 2a: right strip targets, right hexes removed, damage against the role's usual
Values from data (eventlayer_values.json): enchantments by recorded output per second up, hexes by recorded damage plus the drop in the hexed player's output.
- most valuable enchantments to strip (per second up): Dwayna's Sorrow 60.27, Patient Spirit 53.14, Aura of Faith 41.91, Reversal of Fortune 25.76, Double Dragon 23.79, Grenth's Aura 17.68, Spirit Bond 17.47, Conjure Frost 17.41
- most costly hexes (per second on): Shatterstone 76.59 (direct 76.54, output drop 0.05, 306), Incendiary Bonds 75.52 (direct 68.11, output drop 7.4, 24), Smoldering Embers 52.97 (direct 56.44, output drop -3.46, 752), Deep Freeze 46.35 (direct 51.33, output drop -4.98, 30), Lightning Strike 43.57 (direct 42.98, output drop 0.59, 2602), Illusion of Pain 30.33 (direct 30.94, output drop -0.61, 51), Lightning Surge 23.97 (direct 29.04, output drop -5.07, 825), Vile Miasma 22.7 (direct 21.6, output drop 1.1, 103)
- strips on the best target in range (share): winners 0.49, losers 0.48 (93 / 82 team-matches)
- hex removals that took the most costly hex in range (share): winners 0.66, losers 0.68 (90 / 90 team-matches)
- value-weighted seconds a removed hex stayed on: winners 4.99, losers 5.85 (90 / 88 team-matches)
- healer, damage against the role's usual: winners 3.15 (76), losers 3.63 (38)
- midline, damage against the role's usual: winners 1.4 (2127), losers 0.96 (1738)
- frontline, damage against the role's usual: winners 1.32 (1001), losers 0.91 (973)

## Spike timing (kill rate by how tightly the big hits landed)
- spread 0 to 0.5 s: killed 37 of 82 (45%)
- spread 0.5 to 1.5 s: killed 85 of 197 (43%)
- spread 1.5 to 9 s: killed 105 of 331 (32%)

## Run timing (capture rate)
- into an enemy power play: 108 of 208 (52%); otherwise 598 of 1195 (50%)
- enemy holds, its boost in 0 to 30 s: 17 of 48 (35%)
- enemy holds, its boost in 30 to 60 s: 51 of 99 (52%)
- enemy holds, its boost in 60 to 121 s: 308 of 532 (58%)
- runner Crippled during the run: 95 of 129 (74%); not: 611 of 1274 (48%) (read with care: runs that get far are the ones that get Crippled; the run-outcome node of step 2 reads it at the same point of the run)
- runner knocked down: 90 of 129 (70%)

## Enemy captures (from the defending side)
- captures: 706; runner never pushed: 294; median run 34.0 s; median defenders free 8.0; nearest defender at mid-run, median 1220.0

## Splits
- splits: 486, into the base: 178
- answered on time (15 s or less): 150; pit NPCs killed per split 0.77, split deaths 0.42
- answered in 15 to 60 s: 13; pit NPCs killed per split 1.46, split deaths 0.00
- answered after 60 s: 4; pit NPCs killed per split 3.25, split deaths 1.25
- never answered: 11; pit NPCs killed per split 1.09
- size 1: 180; enemies drawn 1.3, own main minus enemy main -0.1, pit kills 0.44
- size 2: 125; enemies drawn 1.1, own main minus enemy main -0.1, pit kills 0.51
- size 3+: 181; enemies drawn 1.3, own main minus enemy main -0.6, pit kills 0.42

## Power plays (all sizes)
- 1 up: 610; killed in 232 (38%); lost a player in 54
- 2 up: 120; killed in 55 (46%); lost a player in 16
- 3+ up: 76; killed in 47 (62%); lost a player in 10
- why the enemy was short (player-seconds): dead 9667, backside 4827, push side 4628, running flag 1535, enemy pit 1106, enemy base 880
