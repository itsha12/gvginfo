# Armor

Source: Guild Wars Wiki, pulled 2026-10-08. Lines starting **Tested** are in-game test results and override the wiki.

## Basic armor (max armor, before insignia)
| Profession | Armor | Inherent bonus |
|---|---|---|
| Warrior | 80 | +20 vs physical |
| Paragon | 80 | none (+5 energy on chest and arms) |
| Ranger | 70 | +30 vs elemental |
| Assassin, Dervish | 70 | Dervish +25 Health on chest |
| Monk, Necromancer, Mesmer, Elementalist, Ritualist | 60 | none |

## Insignia
One per armor piece. Armor from insignia is core armor (uncapped).
- **Any profession:** Survivor (Health), Radiant (energy), Stalwart +10 vs physical, Brawler's +10 while attacking,
  Blessed +10 while enchanted, Herald's +10 while holding an item, Sentry's +10 in a stance.
- **Warrior:** Knight's (−3 physical damage received), Dreadnought +10 vs elemental, Sentinel's +20 vs elemental
  (needs 13 Strength), Lieutenant's (−20% hex duration, −5% damage dealt, −20 armor), Stonefist (+1s to your
  knockdowns, max 3s).
- **Ranger:** Frostbound / Pyrebound / Stormbound / Earthbound +15 vs that element, Scout's +10 during a preparation,
  Beastmaster's +10 while your pet is alive.
- **Monk:** Wanderer's +10 vs elemental, Disciple's +15 while conditioned, Anchorite's +5/+5/+5 while recharging
  1/3/5 skills.
- **Necromancer:** Blighter's +20 while hexed, Bonelace +15 vs piercing, Minion Master's +5/+5/+5 for 1/3/5 minions,
  Tormentor's +10 (but +6/+4/+2 holy damage taken), Undertaker's +5 per 20% Health missing (up to +20),
  Bloodstained (−25% cast time of corpse spells).
- **Mesmer:** Virtuoso's +15 while activating skills, Artificer's +3 per equipped signet, Prodigy's +5/+5/+5 while
  recharging 1/3/5 skills.
- **Elementalist:** Aeromancer / Geomancer / Hydromancer / Pyromancer +10 vs elemental and +10 more vs their element,
  Prismatic +5 per Air/Earth/Fire/Water at 9+.
- **Assassin:** Infiltrator's / Saboteur's / Vanguard's +10 physical and +10 vs piercing / slashing / blunt,
  Nightstalker's +15 while attacking.
- **Ritualist:** Ghost Forge +15 under a weapon spell, Mystic's +15 while activating skills, Shaman's +5/+5/+5
  controlling 1/2/3 spirits.
- **Paragon:** Centurion's +10 under a shout, echo or chant.
- **Dervish:** Forsaken +10 while not enchanted, Windwalker +5 per enchantment (up to +20). Mysticism's armor bonus is
  PvE only.
- Warrior Rune of Absorption: −1/−2/−3 physical damage taken (doesn't stack).

## Shields and hit locations
- Shields: base armor 16 if you meet the requirement (8 if not), plus handle and inscription bonuses.
- Normal and ranged attacks hit: chest 37.5%, legs 25%, head / hands / feet 12.5% each. Only the struck piece's armor
  counts; insignia only apply to their own piece. Armor bonuses from skills and weapons apply to every piece.

## Armor calculation
1. Core armor = basic armor + insignia + base shield armor + inscriptions (uncapped).
2. Bonus armor = all other effects (skills, weapon mods, etc.). If the net bonus is 26 or more, add 25, or the largest
   single bonus if that is higher than 25 (penalties are then ignored, a known bug). If 25 or less, add it. A negative
   bonus can only lower armor to 60, or to core armor if core armor is below 60.
3. Apply armor penetration (%).
4. Special armor: "I Am Unstoppable!", Illusionary Weaponry and Mantra of Signets bonuses; critical hit, Barbed
   Arrows, Healing Signet and Shadowy Burden penalties. Added last, uncapped.
