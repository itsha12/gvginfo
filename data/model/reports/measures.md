# Event-layer measures (step 1), 113 matches

Descriptive only: each measure split by who won the fight (or how a run, split or power play turned out). Step 2's node models test these as causes on unseen matches.

## Wrong casts (per player per fight)
- healer, interrupted after casting into a ready interrupt (no cancel): winners 0.13 (2198), losers 0.34 (2033)
- healer, casts interrupted: winners 0.14 (2198), losers 0.37 (2033)
- healer, casts while Dazed: winners 0.01 (2198), losers 0.05 (2033)
- healer, attacks while Blind: winners 0.0 (2198), losers 0 (2033)
- midline, interrupted after casting into a ready interrupt (no cancel): winners 0.17 (2850), losers 0.23 (2422)
- midline, casts interrupted: winners 0.19 (2850), losers 0.25 (2422)
- midline, casts while Dazed: winners 0.0 (2850), losers 0.02 (2422)
- midline, attacks while Blind: winners 0.01 (2850), losers 0.01 (2422)
- frontline, interrupted after casting into a ready interrupt (no cancel): winners 0.04 (1143), losers 0.1 (999)
- frontline, casts interrupted: winners 0.04 (1143), losers 0.11 (999)
- frontline, casts while Dazed: winners 0.01 (1143), losers 0.0 (999)
- frontline, attacks while Blind: winners 0.12 (1143), losers 0.16 (999)

## Frontline peel (share of frontline damage, per player per fight)
- on attackers of own backline: winners 0.48, losers 0.51 (1082 / 926)
- on enemy healers: winners 0.41, losers 0.35 (1082 / 926)

## Strips, Blind and hex removal (per team per match; winners against losers of the match)
- strips per match: winners 28.61, losers 23.48 (113 / 113 team-matches)
- useful share of strips: winners 0.73, losers 0.7 (112 / 104 team-matches)
- prots stripped off targets under attack: winners 6.74, losers 5.73 (113 / 113 team-matches)
- wasted removal casts: winners 17.64, losers 13.12 (113 / 113 team-matches)
- Blinds on enemy frontline: winners 1.69, losers 0.55 (113 / 113 team-matches)
- defensive Blinds (on a player hitting own healers): winners 0.25, losers 0.15 (113 / 113 team-matches)
- hexes on own healers removed (share): winners 0.29, losers 0.21 (108 / 110 team-matches)
- median seconds a hex stayed on own healers: winners 7.27, losers 6.24 (108 / 110 team-matches)

## Step 2a: right strip targets, right hexes removed, damage against the role's usual
Values from data (eventlayer_values.json): enchantments by recorded output per second up, hexes by recorded damage plus the drop in the hexed player's output.
- most valuable enchantments to strip (per second up): Dwayna's Sorrow 60.27, Patient Spirit 55.86, Aura of Faith 47.69, Reversal of Fortune 28.78, Double Dragon 23.84, Conjure Frost 22.7, Spirit Bond 18.47, Life Sheath 17.95
- most costly hexes (per second on): Deep Freeze 162.92 (direct 166.32, output drop -3.4, 11), Shatterstone 77.31 (direct 77.38, output drop -0.07, 278), Smoldering Embers 53.34 (direct 56.55, output drop -3.21, 424), Lightning Strike 47.53 (direct 45.75, output drop 1.78, 1590), Scourge Enchantment 29.86 (direct 4.09, output drop 25.77, 11), Illusion of Pain 29.81 (direct 31.37, output drop -1.56, 40), Lightning Surge 28.83 (direct 33.43, output drop -4.6, 464), Backfire 25.47 (direct 25.85, output drop -0.38, 84)
- strips on the best target in range (share): winners 0.49, losers 0.43 (112 / 104 team-matches)
- hex removals that took the most costly hex in range (share): winners 0.62, losers 0.64 (110 / 106 team-matches)
- value-weighted seconds a removed hex stayed on: winners 5.14, losers 5.67 (107 / 105 team-matches)
- healer, damage against the role's usual: winners 1.24 (153), losers 1.15 (81)
- midline, damage against the role's usual: winners 1.37 (2850), losers 0.97 (2422)
- frontline, damage against the role's usual: winners 1.37 (1143), losers 0.84 (999)

## Spike timing (kill rate by how tightly the big hits landed)
- spread 0 to 0.5 s: killed 81 of 167 (49%)
- spread 0.5 to 1.5 s: killed 113 of 319 (35%)
- spread 1.5 to 9 s: killed 154 of 511 (30%)

## Run timing (capture rate)
- into an enemy power play: 135 of 260 (52%); otherwise 776 of 1575 (49%)
- enemy holds, its boost in 0 to 30 s: 29 of 79 (37%)
- enemy holds, its boost in 30 to 60 s: 59 of 141 (42%)
- enemy holds, its boost in 60 to 121 s: 416 of 705 (59%)
- runner Crippled during the run: 111 of 138 (80%); not: 800 of 1697 (47%) (read with care: runs that get far are the ones that get Crippled; the run-outcome node of step 2 reads it at the same point of the run)
- runner knocked down: 91 of 137 (66%)

## Enemy captures (from the defending side)
- captures: 911; runner never pushed: 456; median run 34 s; median defenders free 7; nearest defender at mid-run, median 1716

## Splits
- splits: 742, into the base: 314
- answered on time (15 s or less): 275; pit NPCs killed per split 0.63, split deaths 0.33
- answered in 15 to 60 s: 13; pit NPCs killed per split 0.85, split deaths 0.23
- answered after 60 s: 6; pit NPCs killed per split 3.67, split deaths 0.17
- never answered: 20; pit NPCs killed per split 0.75
- size 1: 231; enemies drawn 1.1, own main minus enemy main -0.1, pit kills 0.33
- size 2: 218; enemies drawn 1.5, own main minus enemy main -0.2, pit kills 0.36
- size 3+: 293; enemies drawn 1.3, own main minus enemy main -0.5, pit kills 0.34

## Power plays (all sizes)
- 1 up: 668; killed in 265 (40%); lost a player in 76
- 2 up: 175; killed in 60 (34%); lost a player in 17
- 3+ up: 105; killed in 56 (53%); lost a player in 11
- why the enemy was short (player-seconds): dead 11106, push side 6139, backside 5962, running flag 1791, enemy pit 1723, own base 827
