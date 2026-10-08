# GvG context and the Master of Damage

Source: Guild Wars Wiki, pulled 2026-10-08, plus user testing where marked.

## 10. GvG context
- 8v8 in guild halls. Win: kill the enemy Guild Lord, or all enemies reach 60% death penalty, or at 28 minutes the
  more "aggressive" team wins the tiebreak.
- Flag stand: holding it 2 minutes with your flag grants a 10% morale boost. Most teams run a dedicated flag runner.
- Resurrection shrine cycle every 2 minutes (resurrect with full energy and recharged skills). Resurrection Signet only
  recharges on a morale boost. Death penalty applies (−15% per death).
- NPCs: footmen, archers, knights, bodyguard around the Guild Lord (see knowledge/gvg_rules.md). Victory or Death is
  no longer in the game (user-verified): NPCs don't march and get no late damage bonus.
- Team shape: frontline (warriors/assassins/dervishes), midline (mesmers/rangers/elementalists/paragons/necromancers),
  backline (monks/ritualists), flag runner; snares and at least one resurrection skill; ability to split.


## 11. Master of Damage (testing NPC, Isle of the Nameless)
- Level 20, treated as a primary Elementalist; 590 Health, 30 energy, 60 armor (so stated spell damage and rank-12
  weapon damage hit him at face value). Does not attack. Heals himself before lethal damage (he can't actually die, but
  reports time-to-kill).
- Reports average DPS for the last 5 seconds every 5 seconds. After /bow or 3 minutes: total damage, total time,
  average DPS, best single second and when, and time it took to "kill" him (590 damage).
- Counts life stealing and health degeneration; does not count Deep Wound's −20% max Health. Damage to the two
  adjacent dummies is not counted (scythe/AoE extra hits won't show).
