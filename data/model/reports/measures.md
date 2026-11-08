# Event-layer measures (step 1), 70 matches

Descriptive only: each measure split by who won the fight (or how a run, split or power play turned out). Step 2's node models test these as causes on unseen matches.

## Wrong casts (per player per fight)
- healer, interrupted after casting into a ready interrupt (no cancel): winners 0.13 (1540), losers 0.31 (1486)
- healer, casts interrupted: winners 0.14 (1540), losers 0.34 (1486)
- healer, casts while Dazed: winners 0.02 (1540), losers 0.04 (1486)
- healer, attacks while Blind: winners 0.0 (1540), losers 0 (1486)
- midline, interrupted after casting into a ready interrupt (no cancel): winners 0.18 (1830), losers 0.25 (1577)
- midline, casts interrupted: winners 0.19 (1830), losers 0.28 (1577)
- midline, casts while Dazed: winners 0.0 (1830), losers 0.01 (1577)
- midline, attacks while Blind: winners 0.01 (1830), losers 0.03 (1577)
- frontline, interrupted after casting into a ready interrupt (no cancel): winners 0.03 (884), losers 0.1 (771)
- frontline, casts interrupted: winners 0.04 (884), losers 0.11 (771)
- frontline, casts while Dazed: winners 0.01 (884), losers 0.0 (771)
- frontline, attacks while Blind: winners 0.21 (884), losers 0.12 (771)

## Frontline peel (share of frontline damage, per player per fight)
- on attackers of own backline: winners 0.46, losers 0.55 (850 / 710)
- on enemy healers: winners 0.43, losers 0.33 (850 / 710)

## Strips, Blind and hex removal (per team per match; winners against losers of the match)
- strips per match: winners 35.83, losers 25.87 (70 / 70 team-matches)
- useful share of strips: winners 0.71, losers 0.73 (70 / 63 team-matches)
- prots stripped off targets under attack: winners 9.53, losers 6.61 (70 / 70 team-matches)
- wasted removal casts: winners 21.27, losers 12.96 (70 / 70 team-matches)
- Blinds on enemy frontline: winners 1.16, losers 4.66 (70 / 70 team-matches)
- defensive Blinds (on a player hitting own healers): winners 0.2, losers 1.09 (70 / 70 team-matches)
- hexes on own healers removed (share): winners 0.37, losers 0.23 (67 / 67 team-matches)
- median seconds a hex stayed on own healers: winners 5.28, losers 5.15 (67 / 67 team-matches)

## Step 2a: right strip targets, right hexes removed, damage against the role's usual
Values from data (eventlayer_values.json): enchantments by recorded output per second up, hexes by recorded damage plus the drop in the hexed player's output.
- most valuable enchantments to strip (per second up): Dwayna's Sorrow 60.27, Patient Spirit 52.95, Aura of Faith 42.11, Reversal of Fortune 26.15, Double Dragon 26.05, Holy Veil 25.88, Grenth's Aura 23.9, Balthazar's Aura 17.82
- most costly hexes (per second on): Deep Freeze 162.92 (direct 166.32, output drop -3.4, 11), Incendiary Bonds 75.52 (direct 68.11, output drop 7.4, 24), Shatterstone 73.61 (direct 74.35, output drop -0.75, 363), Smoldering Embers 49.98 (direct 54.63, output drop -4.65, 836), Lightning Strike 41.86 (direct 41.75, output drop 0.11, 2934), Illusion of Pain 29.81 (direct 31.37, output drop -1.56, 40), Spiteful Spirit 22.21 (direct 10.41, output drop 11.8, 7), Mind Freeze 21.8 (direct 21.62, output drop 0.18, 558)
- strips on the best target in range (share): winners 0.47, losers 0.46 (70 / 63 team-matches)
- hex removals that took the most costly hex in range (share): winners 0.65, losers 0.65 (66 / 67 team-matches)
- value-weighted seconds a removed hex stayed on: winners 4.6, losers 5.57 (66 / 65 team-matches)
- healer, damage against the role's usual: winners 2.42 (67), losers 1.37 (23)
- midline, damage against the role's usual: winners 1.35 (1830), losers 0.91 (1577)
- frontline, damage against the role's usual: winners 1.25 (884), losers 0.85 (771)

## Spike timing (kill rate by how tightly the big hits landed)
- spread 0 to 0.5 s: killed 40 of 90 (44%)
- spread 0.5 to 1.5 s: killed 108 of 294 (37%)
- spread 1.5 to 9 s: killed 108 of 415 (26%)

## Run timing (capture rate)
- into an enemy power play: 135 of 240 (56%); otherwise 597 of 1122 (53%)
- enemy holds, its boost in 0 to 30 s: 12 of 46 (26%)
- enemy holds, its boost in 30 to 60 s: 51 of 93 (55%)
- enemy holds, its boost in 60 to 121 s: 346 of 573 (60%)
- runner Crippled during the run: 60 of 71 (85%); not: 672 of 1291 (52%) (read with care: runs that get far are the ones that get Crippled; the run-outcome node of step 2 reads it at the same point of the run)
- runner knocked down: 109 of 147 (74%)

## Enemy captures (from the defending side)
- captures: 732; runner never pushed: 329; median run 33.0 s; median defenders free 7.0; nearest defender at mid-run, median 1307.0

## Splits
- splits: 463, into the base: 192
- answered on time (15 s or less): 169; pit NPCs killed per split 0.54, split deaths 0.37
- answered in 15 to 60 s: 9; pit NPCs killed per split 0.78, split deaths 0.22
- answered after 60 s: 1; pit NPCs killed per split 4.00, split deaths 1.00
- never answered: 13; pit NPCs killed per split 0.69
- size 1: 154; enemies drawn 1.4, own main minus enemy main +0.0, pit kills 0.31
- size 2: 111; enemies drawn 1.3, own main minus enemy main -0.1, pit kills 0.29
- size 3+: 198; enemies drawn 1.4, own main minus enemy main -0.5, pit kills 0.36

## Power plays (all sizes)
- 1 up: 573; killed in 192 (34%); lost a player in 50
- 2 up: 106; killed in 45 (42%); lost a player in 7
- 3+ up: 68; killed in 38 (56%); lost a player in 9
- why the enemy was short (player-seconds): dead 7771, push side 4283, backside 4282, running flag 1632, enemy pit 889, enemy base 711
