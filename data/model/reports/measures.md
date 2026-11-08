# Event-layer measures (step 1), 68 matches

Descriptive only: each measure split by who won the fight (or how a run, split or power play turned out). Step 2's node models test these as causes on unseen matches.

## Wrong casts (per player per fight)
- healer, interrupted after casting into a ready interrupt (no cancel): winners 0.16 (1229), losers 0.36 (1158)
- healer, casts interrupted: winners 0.17 (1229), losers 0.38 (1158)
- healer, casts while Dazed: winners 0.01 (1229), losers 0.02 (1158)
- healer, attacks while Blind: winners 0.0 (1229), losers 0.0 (1158)
- midline, interrupted after casting into a ready interrupt (no cancel): winners 0.19 (1517), losers 0.28 (1247)
- midline, casts interrupted: winners 0.2 (1517), losers 0.3 (1247)
- midline, casts while Dazed: winners 0.01 (1517), losers 0.01 (1247)
- midline, attacks while Blind: winners 0.01 (1517), losers 0.02 (1247)
- frontline, interrupted after casting into a ready interrupt (no cancel): winners 0.05 (668), losers 0.13 (663)
- frontline, casts interrupted: winners 0.06 (668), losers 0.14 (663)
- frontline, casts while Dazed: winners 0 (668), losers 0.0 (663)
- frontline, attacks while Blind: winners 0.13 (668), losers 0.12 (663)

## Frontline peel (share of frontline damage, per player per fight)
- on attackers of own backline: winners 0.49, losers 0.53 (644 / 612)
- on enemy healers: winners 0.42, losers 0.32 (644 / 612)

## Strips, Blind and hex removal (per team per match; winners against losers of the match)
- strips per match: winners 22.4, losers 19.81 (68 / 68 team-matches)
- useful share of strips: winners 0.72, losers 0.66 (66 / 62 team-matches)
- prots stripped off targets under attack: winners 5.81, losers 5.26 (68 / 68 team-matches)
- wasted removal casts: winners 18.5, losers 16.12 (68 / 68 team-matches)
- Blinds on enemy frontline: winners 1.6, losers 2.72 (68 / 68 team-matches)
- defensive Blinds (on a player hitting own healers): winners 0.47, losers 0.93 (68 / 68 team-matches)
- hexes on own healers removed (share): winners 0.27, losers 0.26 (66 / 63 team-matches)
- median seconds a hex stayed on own healers: winners 7.83, losers 6.03 (66 / 63 team-matches)

## Step 2a: right strip targets, right hexes removed, damage against the role's usual
Values from data (eventlayer_values.json): enchantments by recorded output per second up, hexes by recorded damage plus the drop in the hexed player's output.
- most valuable enchantments to strip (per second up): Dwayna's Sorrow 60.27, Patient Spirit 52.6, Aura of Faith 41.16, Spotless Mind 26.91, Reversal of Fortune 26.86, Peace and Harmony 22.81, Conjure Frost 22.7, Double Dragon 20.81
- most costly hexes (per second on): Shatterstone 76.81 (direct 76.69, output drop 0.12, 293), Smoldering Embers 53.17 (direct 56.97, output drop -3.8, 707), Deep Freeze 46.35 (direct 51.33, output drop -4.98, 30), Lightning Strike 43.64 (direct 42.94, output drop 0.71, 2242), Illusion of Pain 30.33 (direct 30.94, output drop -0.61, 51), Mind Freeze 23.3 (direct 23.54, output drop -0.24, 468), Lightning Surge 22.96 (direct 28.27, output drop -5.3, 741), Backfire 22.82 (direct 23.68, output drop -0.86, 143)
- strips on the best target in range (share): winners 0.47, losers 0.49 (66 / 62 team-matches)
- hex removals that took the most costly hex in range (share): winners 0.66, losers 0.61 (65 / 63 team-matches)
- value-weighted seconds a removed hex stayed on: winners 5.29, losers 5.63 (65 / 60 team-matches)
- healer, damage against the role's usual: winners 1.21 (41), losers 1.26 (24)
- midline, damage against the role's usual: winners 1.42 (1517), losers 1.01 (1247)
- frontline, damage against the role's usual: winners 1.36 (668), losers 0.86 (663)

## Spike timing (kill rate by how tightly the big hits landed)
- spread 0 to 0.5 s: killed 30 of 66 (45%)
- spread 0.5 to 1.5 s: killed 64 of 149 (43%)
- spread 1.5 to 9 s: killed 78 of 257 (30%)

## Run timing (capture rate)
- into an enemy power play: 79 of 144 (55%); otherwise 413 of 835 (49%)
- enemy holds, its boost in 0 to 30 s: 11 of 30 (37%)
- enemy holds, its boost in 30 to 60 s: 31 of 66 (47%)
- enemy holds, its boost in 60 to 121 s: 223 of 370 (60%)
- runner Crippled during the run: 64 of 88 (73%); not: 428 of 891 (48%) (read with care: runs that get far are the ones that get Crippled; the run-outcome node of step 2 reads it at the same point of the run)
- runner knocked down: 55 of 86 (64%)

## Enemy captures (from the defending side)
- captures: 492; runner never pushed: 194; median run 34.5 s; median defenders free 8.0; nearest defender at mid-run, median 1173.0

## Splits
- splits: 329, into the base: 139
- answered on time (15 s or less): 111; pit NPCs killed per split 0.75, split deaths 0.30
- answered in 15 to 60 s: 13; pit NPCs killed per split 1.00, split deaths 0.08
- answered after 60 s: 3; pit NPCs killed per split 3.00, split deaths 1.33
- never answered: 12; pit NPCs killed per split 0.42
- size 1: 106; enemies drawn 1.6, own main minus enemy main -0.2, pit kills 0.28
- size 2: 82; enemies drawn 0.9, own main minus enemy main -0.2, pit kills 0.35
- size 3+: 141; enemies drawn 1.4, own main minus enemy main -0.5, pit kills 0.54

## Power plays (all sizes)
- 1 up: 413; killed in 153 (37%); lost a player in 42
- 2 up: 92; killed in 36 (39%); lost a player in 11
- 3+ up: 47; killed in 28 (60%); lost a player in 6
- why the enemy was short (player-seconds): dead 6820, backside 3137, push side 2992, enemy pit 1415, running flag 982, enemy base 588
