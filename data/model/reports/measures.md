# Event-layer measures (step 1), 52 matches

Descriptive only: each measure split by who won the fight (or how a run, split or power play turned out). Step 2's node models test these as causes on unseen matches.

## Wrong casts (per player per fight)
- healer, interrupted after casting into a ready interrupt (no cancel): winners 0.12 (923), losers 0.33 (850)
- healer, casts interrupted: winners 0.13 (923), losers 0.36 (850)
- healer, casts while Dazed: winners 0.01 (923), losers 0.04 (850)
- healer, attacks while Blind: winners 0.01 (923), losers 0 (850)
- midline, interrupted after casting into a ready interrupt (no cancel): winners 0.18 (1209), losers 0.25 (1049)
- midline, casts interrupted: winners 0.19 (1209), losers 0.27 (1049)
- midline, casts while Dazed: winners 0.0 (1209), losers 0.01 (1049)
- midline, attacks while Blind: winners 0.02 (1209), losers 0.02 (1049)
- frontline, interrupted after casting into a ready interrupt (no cancel): winners 0.03 (474), losers 0.09 (406)
- frontline, casts interrupted: winners 0.03 (474), losers 0.1 (406)
- frontline, casts while Dazed: winners 0.01 (474), losers 0 (406)
- frontline, attacks while Blind: winners 0.26 (474), losers 0.27 (406)

## Frontline peel (share of frontline damage, per player per fight)
- on attackers of own backline: winners 0.51, losers 0.53 (436 / 371)
- on enemy healers: winners 0.4, losers 0.32 (436 / 371)

## Strips, Blind and hex removal (per team per match; winners against losers of the match)
- strips per match: winners 25.92, losers 17.88 (52 / 52 team-matches)
- useful share of strips: winners 0.74, losers 0.7 (52 / 45 team-matches)
- prots stripped off targets under attack: winners 6.29, losers 4.44 (52 / 52 team-matches)
- wasted removal casts: winners 17.1, losers 9.65 (52 / 52 team-matches)
- Blinds on enemy frontline: winners 2.4, losers 0.77 (52 / 52 team-matches)
- defensive Blinds (on a player hitting own healers): winners 0.27, losers 0.25 (52 / 52 team-matches)
- hexes on own healers removed (share): winners 0.14, losers 0.13 (48 / 50 team-matches)
- median seconds a hex stayed on own healers: winners 6.16, losers 5.24 (48 / 50 team-matches)

## Spike timing (kill rate by how tightly the big hits landed)
- spread 0 to 0.5 s: killed 27 of 60 (45%)
- spread 0.5 to 1.5 s: killed 58 of 158 (37%)
- spread 1.5 to 9 s: killed 75 of 233 (32%)

## Run timing (capture rate)
- into an enemy power play: 63 of 121 (52%); otherwise 281 of 609 (46%)
- enemy holds, its boost in 0 to 30 s: 8 of 33 (24%)
- enemy holds, its boost in 30 to 60 s: 21 of 51 (41%)
- enemy holds, its boost in 60 to 121 s: 160 of 260 (62%)
- runner Crippled during the run: 38 of 44 (86%); not: 306 of 686 (45%) (read with care: runs that get far are the ones that get Crippled; the run-outcome node of step 2 reads it at the same point of the run)
- runner knocked down: 30 of 41 (73%)

## Enemy captures (from the defending side)
- captures: 344; runner never pushed: 167; median run 33.0 s; median defenders free 7.0; nearest defender at mid-run, median 1641.0

## Splits
- splits: 266, into the base: 112
- answered on time (15 s or less): 93; pit NPCs killed per split 0.66, split deaths 0.31
- answered in 15 to 60 s: 5; pit NPCs killed per split 1.00, split deaths 0.20
- answered after 60 s: 4; pit NPCs killed per split 3.25, split deaths 0.25
- never answered: 10; pit NPCs killed per split 0.80
- size 1: 84; enemies drawn 1.3, own main minus enemy main +0.0, pit kills 0.52
- size 2: 85; enemies drawn 1.1, own main minus enemy main -0.5, pit kills 0.35
- size 3+: 97; enemies drawn 1.3, own main minus enemy main -0.4, pit kills 0.29

## Power plays (all sizes)
- 1 up: 270; killed in 111 (41%); lost a player in 34
- 2 up: 82; killed in 29 (35%); lost a player in 8
- 3+ up: 45; killed in 27 (60%); lost a player in 5
- why the enemy was short (player-seconds): dead 4871, backside 2431, push side 2361, running flag 761, enemy pit 478, own pit 455
