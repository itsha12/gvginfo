# Weapons

Source: Guild Wars Wiki, pulled 2026-10-08. Lines starting **Tested** are my own in-game results and override the wiki.
Max-damage PvP weapons. Every PvP weapon requires 9 in its attribute and is customized (+20% damage).

| Weapon | Damage | Attack interval (s) | Range (gwinches) | Damage type | Notes |
|---|---|---|---|---|---|
| Axe | 6–28 | 1.33 | melee | slashing | big crits |
| Sword | 15–22 | 1.33 | melee | slashing | consistent |
| Hammer | 19–35 | 1.75 | melee | blunt | two-handed |
| Daggers | 7–17 | 1.33 | melee | piercing / slashing | double strike: 2% + 2% per Dagger Mastery rank; dual attacks always double strike |
| Scythe | 9–41 | 1.5 | melee | slashing | hits the target and up to 2 more foes adjacent to it; every hit gets all skill bonuses; crit ×1.09 |
| Spear | 14–27 | 1.5 | 1004 | piercing | one-handed (shield allowed) |
| Flatbow | 15–28 | 2.025 | 1498 | piercing | high arc, slow projectile (0.88s at shortbow range) |
| Shortbow | 15–28 | 2.025 | 1004 | piercing | |
| Longbow | 15–28 | 2.475 | 1498 | piercing | |
| Recurve | 15–28 | 2.475 | 1273 | piercing | fastest projectile (0.40s) |
| Hornbow | 15–28 | 2.7 | 1273 | piercing | 10% armor penetration |
| Staff / Wand | 11–22 | 1.75 | 1248 | by attribute | damage scales with level, not attribute |

Range also changes with height.

## Auto-attack DPS against the Master of Damage
Customized max PvP weapon, rank 12, 12% critical chance, no buffs (from `tools/gw_calc.py`).

| Weapon | Plain | +15% inscription | +20% inscription | Sundering | Vampiric | Under Weakness |
|---|---|---|---|---|---|---|
| Axe | 17.8 | 20.4 | 21.5 | 18.6 | 20.0 | 5.5 |
| Sword | 18.1 | 20.8 | 21.9 | 18.9 | 20.3 | 5.6 |
| Hammer | 20.4 | 23.4 | 24.6 | 21.3 | 23.2 | 6.3 |
| Daggers | 15.3 | 17.6 | 18.5 | 16.0 | 18.1 | 4.7 |
| Scythe (one target) | 21.9 | 25.2 | 26.5 | 22.9 | 25.2 | 6.8 |
| Spear | 18.1 | 20.8 | 21.9 | 18.9 | 20.1 | 5.6 |
| Flatbow / shortbow | 14.0 | 16.1 | 17.0 | 14.7 | 16.5 | 4.3 |
| Longbow / recurve | 11.5 | 13.2 | 13.9 | 12.0 | 13.5 | 3.6 |
| Hornbow | 11.7 | 13.4 | 14.1 | 11.9 | 13.5 | 3.6 |

- **Tested (2026-10-08):** axe ≈17.8 and hammer ≈20.4 are right.
- Vampiric adds its life steal per hit because the Master of Damage counts life steal (tested).

Reference DPS from the wiki (uncustomized, no crits, rank 12, against 60 armor): axe 12.75, sword 13.88,
hammer 15.43, daggers 11.34, scythe 14.29 per target, spear 13.67, flatbow / shortbow 10.75, longbow / recurve 8.96,
hornbow 8.84, staff / wand 9.43.
