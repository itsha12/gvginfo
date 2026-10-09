# Weapon modifiers

Source: Guild Wars Wiki pages Inscription, Axe Haft, Axe Grip, Hammer Haft, Scythe Snathe, Bow String and Damage
calculation, pulled 2026-10-08. Max values shown (PvP weapons always get max values). Lines starting **Tested** are in-game
test results and override the wiki.

A martial weapon takes one prefix, one suffix and one inscription. On PvP weapons the inscription replaces the
inherent modifier.

## Damage inscriptions (any weapon; pick one)
| Inscription | Effect |
|---|---|
| "Strength and Honor" | +15% damage while Health is above 50% |
| "Guided by Fate" | +15% damage while enchanted |
| "Dance with Death" | +15% damage while in a stance |
| "Too Much Information" | +15% damage against hexed foes |
| "To the Pain!" | +15% damage, −10 armor while attacking (only against enemy weapon attacks) |
| "Brawn over Brains" | +15% damage, −5 energy |
| "Vengeance is Mine" | +20% damage while Health is below 50% |
| "Don't Fear the Reaper" | +20% damage while hexed |
- These raise base weapon damage only (not an attack skill's "+X" bonus).
- The wiki notes the +20% inscriptions actually give +21% (the same as 11 armor penetration). The calculator uses ×1.21.

## Other martial inscriptions
- "I have the power!": +5 energy.
- "Let the Memory Live Again": 10% chance to halve the recharge of spells. ("Don't Think Twice" — 10% chance to halve
  spell casting time — fits any weapon.)

## Prefixes (pick one)
| Prefix | Effect | Damage effect |
|---|---|---|
| Vampiric | life steal per hit: **3** on one-handed weapons (axe, sword, daggers, spear), **5** on two-handed (hammer, scythe, bows); −1 Health regeneration | life steal ignores armor; the Master of Damage counts it |
| Zealous | +1 energy per hit; −1 energy regeneration | none |
| Sundering | 20% chance per hit of 20% armor penetration | ≈ +4–5% DPS against 60 armor; doesn't add to Strength's armor penetration (highest wins) |
| Furious | 10% chance to double adrenaline gained on hit | none |
| Barbed / Crippling / Cruel / Heavy / Poisonous / Silencing | +33% duration of Bleeding / Crippled / Deep Wound / Weakness / Poison / Dazed you cause | none |
| Ebon / Fiery / Icy / Shocking | changes damage type to earth / fire / cold / lightning | gets around +armor vs physical (Warrior +20, Stalwart); no change against the Master of Damage |
Not every weapon has every prefix: bows have Silencing but no Cruel, Heavy or Furious; hammers have no Barbed,
Crippling or Poisonous.

- **Tested (2026-10-08):** a Vampiric axe's life steal does count as damage on the Master of Damage.

## Suffixes (pick one)
| Suffix | Effect |
|---|---|
| of Fortitude | +30 Health |
| of Defense | +5 armor |
| of Shelter | +7 armor against physical damage |
| of Warding | +7 armor against elemental damage |
| of Enchanting | enchantments last 20% longer |
| of <Weapon> Mastery (e.g. of Axe Mastery) | +1 to that attribute with a 20% chance, only while using skills (no effect on auto-attacks) |
| of <creature> slaying | +20% damage against one creature type (PvE only) |
Armor from suffixes is bonus armor (counts toward the +25 cap); armor from inscriptions is core armor (uncapped).

## Off-hand and shield inscriptions (for reference)
- Damage reduction: "Sheltered by Faith" −2 physical damage while enchanted; "Run For Your Life!" −2 while in a stance;
  "Nothing to Fear" −3 while hexed; "Luck of the Draw" 20% chance of −5.
- +10 armor against one damage type (blunt, piercing, slashing, cold, earth, fire, lightning).
- −20% duration of one condition (Bleeding, Blind, Crippled, Dazed, Deep Wound, Disease, Poison, Weakness).
- "Master of My Domain": +1 to the item's attribute, 20% chance, for the skill being used.
- Focus only: +5 armor under a condition (Health above 50%, enchanted, attacking, casting, against elemental or
  physical), +10 armor while Health is below 50% or hexed, "Live for Today" +15 energy and −1 energy regeneration,
  "Serenity Now" / "Forget Me Not" chance to halve spell recharge.

## Caster weapons
- Spellcasting-weapon inscriptions: "Hale and Hearty" +5 energy while Health is above 50%, "Have Faith" +5 while
  enchanted, "Don't call it a comeback!" +7 while Health is below 50%, "I am Sorrow." +7 while hexed, "Seize the Day"
  +15 energy and −1 energy regeneration, "Aptitude not Attitude" 20% chance to halve casting time of spells of the
  item's attribute.
- Staff: +10 energy inherent (+5 more from a prefix). Wands, shields and foci take a suffix only.
