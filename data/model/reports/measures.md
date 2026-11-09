# Event-layer measures (step 1), 135 matches

Descriptive only: each measure split by who won the fight (or how a run, split or power play turned out). Step 2's node models test these as causes on unseen matches.

## Wrong casts (per player per fight)
- healer, interrupted after casting into a ready interrupt (no cancel): winners 0.1 (2864), losers 0.32 (2655)
- healer, casts interrupted: winners 0.12 (2864), losers 0.35 (2655)
- healer, casts while Dazed: winners 0.0 (2864), losers 0.02 (2655)
- healer, attacks while Blind: winners 0.0 (2864), losers 0.0 (2655)
- midline, interrupted after casting into a ready interrupt (no cancel): winners 0.18 (3281), losers 0.27 (2700)
- midline, casts interrupted: winners 0.2 (3281), losers 0.29 (2700)
- midline, casts while Dazed: winners 0.0 (3281), losers 0.01 (2700)
- midline, attacks while Blind: winners 0.01 (3281), losers 0.01 (2700)
- frontline, interrupted after casting into a ready interrupt (no cancel): winners 0.04 (1624), losers 0.11 (1471)
- frontline, casts interrupted: winners 0.05 (1624), losers 0.13 (1471)
- frontline, casts while Dazed: winners 0.0 (1624), losers 0.0 (1471)
- frontline, attacks while Blind: winners 0.08 (1624), losers 0.07 (1471)

## Frontline peel (share of frontline damage, per player per fight)
- on attackers of own backline: winners 0.47, losers 0.51 (1526 / 1369)
- on enemy healers: winners 0.42, losers 0.34 (1526 / 1369)

## Strips, Blind and hex removal (per team per match; winners against losers of the match)
- strips per match: winners 27.44, losers 22.53 (135 / 135 team-matches)
- useful share of strips: winners 0.66, losers 0.7 (128 / 119 team-matches)
- prots stripped off targets under attack: winners 6.83, losers 5.04 (135 / 135 team-matches)
- wasted removal casts: winners 21.04, losers 12.71 (135 / 135 team-matches)
- Blinds on enemy frontline: winners 1.74, losers 1.33 (135 / 135 team-matches)
- defensive Blinds (on a player hitting own healers): winners 0.42, losers 0.62 (135 / 135 team-matches)
- hexes on own healers removed (share): winners 0.3, losers 0.21 (119 / 132 team-matches)
- median seconds a hex stayed on own healers: winners 6.37, losers 6.27 (119 / 132 team-matches)

## Step 2a: right strip targets, right hexes removed, damage against the role's usual
Values from data (eventlayer_values.json): enchantments by recorded output per second up, hexes by recorded damage plus the drop in the hexed player's output.
- most valuable enchantments to strip (per second up): Patient Spirit 54.88, Aura of Faith 42.13, Reversal of Fortune 25.65, Double Dragon 24.09, Balthazar's Aura 23.88, Holy Veil 21.12, Divine Spirit 20.66, Grenth's Aura 19.48
- most costly hexes (per second on): Deep Freeze 162.92 (direct 166.32, output drop -3.4, 11), Shatterstone 67.91 (direct 69.67, output drop -1.76, 726), Incendiary Bonds 64.11 (direct 59.11, output drop 5.0, 39), Smoldering Embers 54.27 (direct 56.84, output drop -2.56, 1646), Lightning Strike 42.86 (direct 43.85, output drop -0.99, 5540), Illusion of Pain 29.81 (direct 31.37, output drop -1.56, 40), Backfire 25.32 (direct 23.96, output drop 1.36, 198), Mind Freeze 24.59 (direct 22.46, output drop 2.13, 785)
- strips on the best target in range (share): winners 0.52, losers 0.46 (128 / 119 team-matches)
- hex removals that took the most costly hex in range (share): winners 0.67, losers 0.6 (118 / 127 team-matches)
- value-weighted seconds a removed hex stayed on: winners 5.01, losers 5.46 (116 / 123 team-matches)
- healer, damage against the role's usual: winners 1.2 (121), losers 0.97 (79)
- midline, damage against the role's usual: winners 1.36 (3281), losers 0.86 (2700)
- frontline, damage against the role's usual: winners 1.3 (1624), losers 0.82 (1471)

## Spike timing (kill rate by how tightly the big hits landed)
- spread 0 to 0.5 s: killed 61 of 144 (42%)
- spread 0.5 to 1.5 s: killed 141 of 319 (44%)
- spread 1.5 to 9 s: killed 190 of 561 (34%)

## Run timing (capture rate)
- into an enemy power play: 186 of 350 (53%); otherwise 915 of 1784 (51%)
- enemy holds, its boost in 0 to 30 s: 37 of 92 (40%)
- enemy holds, its boost in 30 to 60 s: 86 of 190 (45%)
- enemy holds, its boost in 60 to 121 s: 522 of 837 (62%)
- runner Crippled during the run: 128 of 177 (72%); not: 973 of 1957 (50%) (read with care: runs that get far are the ones that get Crippled; the run-outcome node of step 2 reads it at the same point of the run)
- runner knocked down: 120 of 172 (70%)

## Enemy captures (from the defending side)
- captures: 1101; runner never pushed: 525; median run 34 s; median defenders free 7; nearest defender at mid-run, median 1778

## Splits
- splits: 928, into the base: 381
- answered on time (15 s or less): 340; pit NPCs killed per split 0.59, split deaths 0.32
- answered in 15 to 60 s: 16; pit NPCs killed per split 0.94, split deaths 0.19
- answered after 60 s: 3; pit NPCs killed per split 3.00, split deaths 0.00
- never answered: 22; pit NPCs killed per split 0.95
- size 1: 329; enemies drawn 1.3, own main minus enemy main +0.1, pit kills 0.30
- size 2: 230; enemies drawn 1.4, own main minus enemy main -0.1, pit kills 0.35
- size 3+: 369; enemies drawn 1.5, own main minus enemy main -0.4, pit kills 0.40

## Power plays (all sizes)
- 1 up: 991; killed in 385 (39%); lost a player in 114
- 2 up: 186; killed in 89 (48%); lost a player in 22
- 3+ up: 122; killed in 71 (58%); lost a player in 15
- why the enemy was short (player-seconds): dead 15150, push side 8339, backside 7801, running flag 2459, enemy pit 1999, enemy base 1473
