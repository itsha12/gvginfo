# Conditions

Source: Guild Wars Wiki, pulled 2026-10-08. Lines starting **Tested** are in-game test results and override the wiki.

Conditions have fixed effects; they don't scale with attributes.

| Condition | Effect |
|---|---|
| Bleeding | −3 regeneration pips (−6 Health per second) |
| Burning | −7 pips (−14 Health per second) |
| Poison | −4 pips (−8 Health per second) |
| Disease | −4 pips; spreads to nearby creatures of the same type |
| Blind | attacks have a 90% chance to miss |
| Cracked Armor | −20 armor (can't reduce armor below 60) |
| Crippled | move 50% slower |
| Dazed | spells take twice as long to cast; any successful attack interrupts your spells; interrupts a spell when applied |
| Deep Wound | −20% max Health; reduced benefit from healing |
| Weakness | weapon damage 66% less and −1 to all attributes (details below) |

## Weakness
- **Tested (2026-10-08):** Weakness reduces damage by 66% (you deal 34% of normal), not "deal 66% of normal". It only
  applies to auto-attack damage.
- **Tested (2026-10-08):** it also lowers attributes by 1, so weapon mastery drops a rank and damage falls further
  (rank 12 → 11 is ×0.917; critical chance also drops about 1%). Expected auto-attack DPS under Weakness ≈ 0.31 × normal.
- Wiki: the reduction applies only to the equipped weapon's base damage (so an attack skill's "+X" bonus damage isn't
  reduced). Only attributes above 0 are lowered, never below 0; rank-0 attributes stay 0 even if runes would raise
  them. Can make you fail weapon or skill requirements.

## Rules for all conditions
- Reapplying a condition only extends it if the new duration is longer than what remains.
- Condition-duration reductions (runes −20%, off-hand inscriptions −20%) apply separately and round separately.
- Weapon condition prefixes (Barbed, Crippling, Cruel, Heavy, Poisonous, Silencing) make that condition last 33%
  longer on your hits.
- Non-fleshy creatures (minions except Flesh Golem, spirits) are immune to Bleeding, Poison and Disease. Spirits are
  immune to every condition except Burning.
- Combined degeneration is capped at −10 pips: Burning + Poison + Bleeding is −20 Health per second, not −28.
