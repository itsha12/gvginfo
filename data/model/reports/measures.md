# Event-layer measures (step 1), 90 matches

Descriptive only: each measure split by who won the fight (or how a run, split or power play turned out). Step 2's node models test these as causes on unseen matches.

## Wrong casts (per player per fight)
- healer, interrupted after casting into a ready interrupt (no cancel): winners 0.12 (1950), losers 0.35 (1882)
- healer, casts interrupted: winners 0.13 (1950), losers 0.37 (1882)
- healer, casts while Dazed: winners 0.01 (1950), losers 0.04 (1882)
- healer, attacks while Blind: winners 0 (1950), losers 0 (1882)
- midline, interrupted after casting into a ready interrupt (no cancel): winners 0.2 (2244), losers 0.25 (2006)
- midline, casts interrupted: winners 0.21 (2244), losers 0.27 (2006)
- midline, casts while Dazed: winners 0.01 (2244), losers 0.0 (2006)
- midline, attacks while Blind: winners 0.01 (2244), losers 0.01 (2006)
- frontline, interrupted after casting into a ready interrupt (no cancel): winners 0.03 (1159), losers 0.1 (903)
- frontline, casts interrupted: winners 0.03 (1159), losers 0.11 (903)
- frontline, casts while Dazed: winners 0 (1159), losers 0.0 (903)
- frontline, attacks while Blind: winners 0.13 (1159), losers 0.07 (903)

## Frontline peel (share of frontline damage, per player per fight)
- on attackers of own backline: winners 0.44, losers 0.55 (1112 / 821)
- on enemy healers: winners 0.46, losers 0.33 (1112 / 821)

## Strips, Blind and hex removal (per team per match; winners against losers of the match)
- strips per match: winners 30.81, losers 23.84 (90 / 90 team-matches)
- useful share of strips: winners 0.68, losers 0.72 (87 / 81 team-matches)
- prots stripped off targets under attack: winners 8.76, losers 5.66 (90 / 90 team-matches)
- wasted removal casts: winners 20.62, losers 11.6 (90 / 90 team-matches)
- Blinds on enemy frontline: winners 2.06, losers 3.17 (90 / 90 team-matches)
- defensive Blinds (on a player hitting own healers): winners 0.44, losers 0.69 (90 / 90 team-matches)
- hexes on own healers removed (share): winners 0.34, losers 0.22 (87 / 87 team-matches)
- median seconds a hex stayed on own healers: winners 6.2, losers 5.62 (87 / 87 team-matches)

## Step 2a: right strip targets, right hexes removed, damage against the role's usual
Values from data (eventlayer_values.json): enchantments by recorded output per second up, hexes by recorded damage plus the drop in the hexed player's output.
- most valuable enchantments to strip (per second up): Dwayna's Sorrow 60.27, Patient Spirit 53.02, Aura of Faith 42.75, Reversal of Fortune 26.19, Holy Veil 25.88, Double Dragon 25.08, Grenth's Aura 23.64, Balthazar's Aura 18.55
- most costly hexes (per second on): Deep Freeze 162.92 (direct 166.32, output drop -3.4, 11), Incendiary Bonds 75.52 (direct 68.11, output drop 7.4, 24), Shatterstone 70.72 (direct 72.56, output drop -1.83, 435), Smoldering Embers 50.8 (direct 54.44, output drop -3.63, 966), Lightning Strike 41.16 (direct 41.41, output drop -0.24, 3567), Illusion of Pain 29.81 (direct 31.37, output drop -1.56, 40), Mind Freeze 22.33 (direct 21.25, output drop 1.08, 596), Spiteful Spirit 22.21 (direct 10.41, output drop 11.8, 7)
- strips on the best target in range (share): winners 0.5, losers 0.47 (87 / 81 team-matches)
- hex removals that took the most costly hex in range (share): winners 0.69, losers 0.63 (85 / 84 team-matches)
- value-weighted seconds a removed hex stayed on: winners 4.7, losers 5.88 (85 / 83 team-matches)
- healer, damage against the role's usual: winners 1.16 (72), losers 1.46 (26)
- midline, damage against the role's usual: winners 1.36 (2244), losers 0.96 (2006)
- frontline, damage against the role's usual: winners 1.29 (1159), losers 0.81 (903)

## Spike timing (kill rate by how tightly the big hits landed)
- spread 0 to 0.5 s: killed 48 of 118 (41%)
- spread 0.5 to 1.5 s: killed 121 of 320 (38%)
- spread 1.5 to 9 s: killed 125 of 502 (25%)

## Run timing (capture rate)
- into an enemy power play: 165 of 285 (58%); otherwise 720 of 1349 (53%)
- enemy holds, its boost in 0 to 30 s: 19 of 66 (29%)
- enemy holds, its boost in 30 to 60 s: 60 of 114 (53%)
- enemy holds, its boost in 60 to 121 s: 419 of 679 (62%)
- runner Crippled during the run: 79 of 96 (82%); not: 806 of 1538 (52%) (read with care: runs that get far are the ones that get Crippled; the run-outcome node of step 2 reads it at the same point of the run)
- runner knocked down: 115 of 153 (75%)

## Enemy captures (from the defending side)
- captures: 885; runner never pushed: 413; median run 33 s; median defenders free 7; nearest defender at mid-run, median 1506

## Splits
- splits: 600, into the base: 262
- answered on time (15 s or less): 227; pit NPCs killed per split 0.60, split deaths 0.42
- answered in 15 to 60 s: 12; pit NPCs killed per split 0.67, split deaths 0.17
- answered after 60 s: 2; pit NPCs killed per split 4.00, split deaths 0.50
- never answered: 21; pit NPCs killed per split 0.48
- size 1: 187; enemies drawn 1.5, own main minus enemy main +0.2, pit kills 0.38
- size 2: 164; enemies drawn 1.4, own main minus enemy main -0.0, pit kills 0.40
- size 3+: 249; enemies drawn 1.4, own main minus enemy main -0.4, pit kills 0.35

## Power plays (all sizes)
- 1 up: 720; killed in 259 (36%); lost a player in 84
- 2 up: 136; killed in 63 (46%); lost a player in 10
- 3+ up: 74; killed in 40 (54%); lost a player in 8
- why the enemy was short (player-seconds): dead 10380, backside 5505, push side 4730, running flag 1867, enemy pit 1518, stand 756
