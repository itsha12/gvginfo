# Event-layer measures (step 1), 90 matches

Descriptive only: each measure split by who won the fight (or how a run, split or power play turned out). Step 2's node models test these as causes on unseen matches.

## Wrong casts (per player per fight)
- healer, interrupted after casting into a ready interrupt (no cancel): winners 0.1 (1891), losers 0.32 (1838)
- healer, casts interrupted: winners 0.11 (1891), losers 0.34 (1838)
- healer, casts while Dazed: winners 0.01 (1891), losers 0.02 (1838)
- healer, attacks while Blind: winners 0 (1891), losers 0.0 (1838)
- midline, interrupted after casting into a ready interrupt (no cancel): winners 0.18 (2409), losers 0.23 (2065)
- midline, casts interrupted: winners 0.2 (2409), losers 0.25 (2065)
- midline, casts while Dazed: winners 0.0 (2409), losers 0.0 (2065)
- midline, attacks while Blind: winners 0.02 (2409), losers 0.03 (2065)
- frontline, interrupted after casting into a ready interrupt (no cancel): winners 0.03 (1014), losers 0.11 (819)
- frontline, casts interrupted: winners 0.04 (1014), losers 0.12 (819)
- frontline, casts while Dazed: winners 0 (1014), losers 0.01 (819)
- frontline, attacks while Blind: winners 0.05 (1014), losers 0.15 (819)

## Frontline peel (share of frontline damage, per player per fight)
- on attackers of own backline: winners 0.47, losers 0.54 (961 / 764)
- on enemy healers: winners 0.43, losers 0.3 (961 / 764)

## Strips, Blind and hex removal (per team per match; winners against losers of the match)
- strips per match: winners 24.77, losers 20.19 (90 / 90 team-matches)
- useful share of strips: winners 0.67, losers 0.72 (86 / 81 team-matches)
- prots stripped off targets under attack: winners 7.06, losers 4.83 (90 / 90 team-matches)
- wasted removal casts: winners 16.23, losers 9.7 (90 / 90 team-matches)
- Blinds on enemy frontline: winners 3.12, losers 0.83 (90 / 90 team-matches)
- defensive Blinds (on a player hitting own healers): winners 0.53, losers 0.23 (90 / 90 team-matches)
- hexes on own healers removed (share): winners 0.32, losers 0.21 (82 / 89 team-matches)
- median seconds a hex stayed on own healers: winners 6.48, losers 5.29 (82 / 89 team-matches)

## Step 2a: right strip targets, right hexes removed, damage against the role's usual
Values from data (eventlayer_values.json): enchantments by recorded output per second up, hexes by recorded damage plus the drop in the hexed player's output.
- most valuable enchantments to strip (per second up): Dwayna's Sorrow 60.27, Patient Spirit 52.7, Aura of Faith 42.41, Holy Veil 25.83, Reversal of Fortune 25.62, Double Dragon 23.8, Grenth's Aura 23.75, Spirit Bond 17.59
- most costly hexes (per second on): Deep Freeze 162.92 (direct 166.32, output drop -3.4, 11), Incendiary Bonds 75.52 (direct 68.11, output drop 7.4, 24), Shatterstone 67.09 (direct 68.87, output drop -1.78, 476), Smoldering Embers 53.17 (direct 56.07, output drop -2.91, 1193), Lightning Strike 41.48 (direct 42.31, output drop -0.84, 4257), Illusion of Pain 29.81 (direct 31.37, output drop -1.56, 40), Backfire 25.57 (direct 23.93, output drop 1.64, 141), Life Siphon 24.2 (direct 15.81, output drop 8.39, 9)
- strips on the best target in range (share): winners 0.56, losers 0.44 (86 / 81 team-matches)
- hex removals that took the most costly hex in range (share): winners 0.7, losers 0.64 (82 / 84 team-matches)
- value-weighted seconds a removed hex stayed on: winners 4.56, losers 5.73 (82 / 83 team-matches)
- healer, damage against the role's usual: winners 1.09 (114), losers 0.88 (36)
- midline, damage against the role's usual: winners 1.37 (2409), losers 0.95 (2065)
- frontline, damage against the role's usual: winners 1.32 (1014), losers 0.77 (819)

## Spike timing (kill rate by how tightly the big hits landed)
- spread 0 to 0.5 s: killed 55 of 136 (40%)
- spread 0.5 to 1.5 s: killed 127 of 339 (37%)
- spread 1.5 to 9 s: killed 119 of 457 (26%)

## Run timing (capture rate)
- into an enemy power play: 133 of 226 (59%); otherwise 655 of 1216 (54%)
- enemy holds, its boost in 0 to 30 s: 20 of 49 (41%)
- enemy holds, its boost in 30 to 60 s: 60 of 108 (56%)
- enemy holds, its boost in 60 to 121 s: 365 of 582 (63%)
- runner Crippled during the run: 83 of 110 (75%); not: 705 of 1332 (53%) (read with care: runs that get far are the ones that get Crippled; the run-outcome node of step 2 reads it at the same point of the run)
- runner knocked down: 70 of 101 (69%)

## Enemy captures (from the defending side)
- captures: 788; runner never pushed: 396; median run 34.0 s; median defenders free 7.0; nearest defender at mid-run, median 1873.0

## Splits
- splits: 516, into the base: 235
- answered on time (15 s or less): 201; pit NPCs killed per split 0.81, split deaths 0.41
- answered in 15 to 60 s: 13; pit NPCs killed per split 0.85, split deaths 0.31
- answered after 60 s: 2; pit NPCs killed per split 4.00, split deaths 0.50
- never answered: 19; pit NPCs killed per split 0.84
- size 1: 168; enemies drawn 1.3, own main minus enemy main +0.2, pit kills 0.47
- size 2: 128; enemies drawn 1.3, own main minus enemy main -0.1, pit kills 0.55
- size 3+: 220; enemies drawn 1.4, own main minus enemy main -0.6, pit kills 0.48

## Power plays (all sizes)
- 1 up: 594; killed in 237 (40%); lost a player in 84
- 2 up: 129; killed in 64 (50%); lost a player in 17
- 3+ up: 57; killed in 31 (54%); lost a player in 9
- why the enemy was short (player-seconds): dead 9652, backside 4828, push side 4020, running flag 1527, enemy pit 1207, stand 668
