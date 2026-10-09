# Damage formula

Source: Guild Wars Wiki, pulled 2026-10-08. Lines starting **Tested** are my own in-game results and override the wiki.
The calculator in `tools/gw_calc.py` uses these formulas.

## Armor-respecting damage
Weapon damage and most elemental spell damage:

`damage = base × 2^((strike level − effective armor) / 40)`

- 60 armor is the baseline: a level 20 spell, or a weapon at rank 12, deals exactly its stated damage to 60 armor.
- Every +40 armor halves damage; every −40 doubles it. −20 armor ≈ ×1.414; +20 armor ≈ ×0.707.
- Weapon strike level = 5 × weapon-mastery rank up to 12, then only +2 per rank above 12 (level 20).
- Damage per mastery rank, relative to 12: 0: 35.6%, 4: 50%, 8: 70.7%, 9: 77.1%, 10: 84.1%, 11: 91.7%, 12: 100%,
  13: 103.5%, 14: 107.2%, 15: 111%, 16: 114.9%.
- Below the weapon's attribute requirement: 1/3 damage. PvP weapons require 9.
- Skill damage scales with character level: 100% at level 20 (66% at 12, 37.2% at 1).
- **Tested (2026-10-08):** the auto-attack predictions for axe (≈17.8 DPS) and hammer (≈20.4 DPS) against the Master
  of Damage were right, which confirms this formula, the ×1.2 customization and the 12% crit chance at rank 12.

## Base damage multipliers
- Customization ×1.20 (every PvP weapon is customized automatically).
- Damage inscription +15% or +20% (see Weapon modifiers). Treated as multiplying with customization; the wiki doesn't
  say whether they add or multiply.
- Weakness ×0.34 on auto-attacks (see Conditions).
- These affect base weapon damage only, not an attack skill's "+X" bonus.

## Armor penetration
- Effective armor = armor × (1 − armor penetration). Only the highest armor penetration applies.
- Air Magic lightning spells 25%; Strength 1% per rank for attack skills; Sundering prefix 20% chance of 20%;
  hornbow 10%.

## Armor-ignoring damage
- Typeless "X damage", shadow damage, most holy damage (undead and minions take double holy), attack-skill bonus
  damage, life stealing, Health loss. Chaos and dark damage (wands and staves) respect armor.
- An attack skill's "+X damage" is added into the same damage packet as the weapon hit. Strength's armor penetration
  applies to the weapon part of attack skills.

## Order
- Damage multipliers (Frenzy-type ×2 damage taken, etc.) apply after armor.
- Outline: armor → attack-skill bonus → ×2 effects → flat and percentage reductions (Protective Bond, Shielding Hands,
  etc.). Flat reductions apply last, per packet.
- Damage is applied in whole numbers per packet.
- Projectiles deal more damage shooting downhill and less uphill (up to about double from high ground).
