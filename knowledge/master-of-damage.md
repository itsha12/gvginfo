# Master of Damage

Source: Guild Wars Wiki, pulled 2026-10-08. Lines starting **Tested** are in-game test results and override the wiki.
The testing NPC on the Isle of the Nameless.

## Stats
- Level 20, treated as a primary Elementalist: 590 Health, 30 energy, 60 armor. So stated spell damage and rank-12
  weapon damage hit him at face value.
- Does not attack. Heals himself before lethal damage (he can't die, but reports time-to-kill).

## What he reports
- Average DPS for the last 5 seconds, every 5 seconds.
- After /bow or 3 minutes: total damage, total time, average DPS, best single second and when, and how long it took to
  "kill" him (590 damage).

## What he counts
- Counts Health degeneration.
- **Tested (2026-10-08):** counts life stealing — a Vampiric axe's life steal shows up as damage.
- Does not count Deep Wound's −20% max Health.
- Damage to the two dummies next to him is not counted (extra scythe and area hits won't show).
- **Tested (2026-10-08):** Cracked Armor has no effect on him (his 60 armor is already the floor).

## Confirmed results
- **Tested (2026-10-08):** auto-attack axe ≈17.8 DPS and hammer ≈20.4 DPS, as predicted (customized max PvP weapon,
  rank 12, no inscription).
