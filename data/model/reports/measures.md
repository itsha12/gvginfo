# Event-layer measures (step 1), 42 matches

Descriptive only: each measure split by who won the fight (or how a run, split or power play turned out). Step 2's node models test these as causes on unseen matches.

## Wrong casts (per player per fight)
- healer, interrupted after casting into a ready interrupt (no cancel): winners 0.13 (833), losers 0.29 (814)
- healer, casts interrupted: winners 0.14 (833), losers 0.32 (814)
- healer, casts while Dazed: winners 0.0 (833), losers 0.01 (814)
- healer, attacks while Blind: winners 0.0 (833), losers 0 (814)
- midline, interrupted after casting into a ready interrupt (no cancel): winners 0.18 (1059), losers 0.25 (886)
- midline, casts interrupted: winners 0.19 (1059), losers 0.28 (886)
- midline, casts while Dazed: winners 0.01 (1059), losers 0.01 (886)
- midline, attacks while Blind: winners 0.01 (1059), losers 0.02 (886)
- frontline, interrupted after casting into a ready interrupt (no cancel): winners 0.04 (391), losers 0.11 (415)
- frontline, casts interrupted: winners 0.05 (391), losers 0.13 (415)
- frontline, casts while Dazed: winners 0 (391), losers 0.0 (415)
- frontline, attacks while Blind: winners 0.12 (391), losers 0.15 (415)

## Frontline peel (share of frontline damage, per player per fight)
- on attackers of own backline: winners 0.52, losers 0.57 (367 / 352)
- on enemy healers: winners 0.42, losers 0.31 (367 / 352)

## Strips, Blind and hex removal (per team per match; winners against losers of the match)
- strips per match: winners 27.48, losers 21.86 (42 / 42 team-matches)
- useful share of strips: winners 0.73, losers 0.7 (41 / 36 team-matches)
- prots stripped off targets under attack: winners 8.19, losers 6.83 (42 / 42 team-matches)
- wasted removal casts: winners 18.02, losers 16.55 (42 / 42 team-matches)
- Blinds on enemy frontline: winners 2.07, losers 1.19 (42 / 42 team-matches)
- defensive Blinds (on a player hitting own healers): winners 0.19, losers 0.5 (42 / 42 team-matches)
- hexes on own healers removed (share): winners 0.28, losers 0.23 (39 / 37 team-matches)
- median seconds a hex stayed on own healers: winners 7.94, losers 6.12 (39 / 37 team-matches)

## Step 2a: right strip targets, right hexes removed, damage against the role's usual
Values from data (eventlayer_values.json): enchantments by recorded output per second up, hexes by recorded damage plus the drop in the hexed player's output.
- most valuable enchantments to strip (per second up): Dwayna's Sorrow 60.27, Patient Spirit 54.74, Aura of Faith 43.06, Reversal of Fortune 28.08, Double Dragon 26.25, Conjure Frost 22.7, Spirit Bond 18.11, Life Sheath 18.08
- most costly hexes (per second on): Deep Freeze 162.92 (direct 166.32, output drop -3.4, 11), Shatterstone 77.31 (direct 77.38, output drop -0.07, 278), Smoldering Embers 53.69 (direct 56.45, output drop -2.76, 535), Lightning Strike 46.57 (direct 45.13, output drop 1.44, 1790), Scourge Enchantment 29.86 (direct 4.09, output drop 25.77, 11), Illusion of Pain 29.81 (direct 31.37, output drop -1.56, 40), Lightning Surge 28.82 (direct 33.39, output drop -4.57, 475), Mind Freeze 23.18 (direct 23.42, output drop -0.24, 351)
- strips on the best target in range (share): winners 0.45, losers 0.39 (41 / 36 team-matches)
- hex removals that took the most costly hex in range (share): winners 0.56, losers 0.6 (39 / 38 team-matches)
- value-weighted seconds a removed hex stayed on: winners 5.63, losers 5.54 (38 / 36 team-matches)
- healer, damage against the role's usual: winners 1.63 (22), losers 1.74 (18)
- midline, damage against the role's usual: winners 1.38 (1059), losers 1.01 (886)
- frontline, damage against the role's usual: winners 1.34 (391), losers 0.76 (415)

## Spike timing (kill rate by how tightly the big hits landed)
- spread 0 to 0.5 s: killed 25 of 51 (49%)
- spread 0.5 to 1.5 s: killed 70 of 182 (38%)
- spread 1.5 to 9 s: killed 53 of 201 (26%)

## Run timing (capture rate)
- into an enemy power play: 68 of 112 (61%); otherwise 331 of 639 (52%)
- enemy holds, its boost in 0 to 30 s: 2 of 19 (11%)
- enemy holds, its boost in 30 to 60 s: 24 of 48 (50%)
- enemy holds, its boost in 60 to 121 s: 196 of 301 (65%)
- runner Crippled during the run: 40 of 49 (82%); not: 359 of 702 (51%) (read with care: runs that get far are the ones that get Crippled; the run-outcome node of step 2 reads it at the same point of the run)
- runner knocked down: 46 of 63 (73%)

## Enemy captures (from the defending side)
- captures: 399; runner never pushed: 176; median run 35 s; median defenders free 7; nearest defender at mid-run, median 1341

## Splits
- splits: 253, into the base: 136
- answered on time (15 s or less): 110; pit NPCs killed per split 0.68, split deaths 0.27
- answered in 15 to 60 s: 9; pit NPCs killed per split 0.89, split deaths 0.11
- answered after 60 s: 4; pit NPCs killed per split 3.25, split deaths 0.25
- never answered: 13; pit NPCs killed per split 0.38
- size 1: 94; enemies drawn 1.4, own main minus enemy main -0.2, pit kills 0.34
- size 2: 67; enemies drawn 0.9, own main minus enemy main -0.4, pit kills 0.34
- size 3+: 92; enemies drawn 1.5, own main minus enemy main -0.6, pit kills 0.61

## Power plays (all sizes)
- 1 up: 303; killed in 99 (33%); lost a player in 42
- 2 up: 83; killed in 22 (27%); lost a player in 9
- 3+ up: 29; killed in 14 (48%); lost a player in 2
- why the enemy was short (player-seconds): dead 3832, push side 2310, backside 2255, enemy pit 1146, running flag 909, enemy base 440
