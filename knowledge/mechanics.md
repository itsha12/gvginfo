# Game mechanics

Source: Guild Wars Wiki, pulled 2026-10-08, plus user testing where marked.

## 1. Character baseline (level 20, PvP)

- Base max Health 480. Rune of Superior Vigor +50 (does not stack with another Vigor rune), Rune of Vitae +10 each
  (stacks), Survivor Insignia +15 chest / +10 legs / +5 other pieces. Attribute runes: Minor +1 (no Health cost),
  Major +2 (−35 Health), Superior +3 (−75 Health). Attribute bonuses from runes don't stack with each other but do stack
  with headgear; Health penalties always stack. Max possible from runes+insignia is 610 (Dervish 635).
- Martial weapon suffix "of Fortitude" +30 Health; shields/foci up to +30 (+45 while enchanted or in a stance,
  +60 while hexed) via handles/cores.
- Attribute points: 200. Rank cost (cumulative): 1:1, 2:3, 3:6, 4:10, 5:15, 6:21, 7:28, 8:37, 9:48, 10:61, 11:77, 12:97.
  12 is the max you can buy. Common spreads: 12+12+3; 12+10+8 (+5 left); 12+11+6; 12+9+9 (+7); 11+10+10 (+1).
- Secondary profession: no access to its primary attribute, and runes/headgear only work for the primary profession,
  so secondary attributes cap at 12 (from points alone).
- Skill bar: 8 skills, maximum 1 elite. PvE-only skills are permanently disabled in PvP.

### Energy (base, from profession armor)
| Profession | Max energy | Energy regen (pips) |
|---|---|---|
| Warrior | 20 | 2 |
| Ranger | 25 | 3 |
| Assassin, Dervish | 25 | 4 |
| Paragon | 30 | 2 |
| Monk, Necromancer, Mesmer, Elementalist, Ritualist | 30 | 4 |
One pip = 1 energy per 3 seconds. Energy Storage (Elementalist primary) +3 max energy per rank. Radiant Insignia
+3/+2/+1 (chest/legs/other), Rune of Attunement +2 each (stacks). Staff +10 inherent (+5 more from a prefix);
focus items up to +12; inscriptions/cores "+15 energy, −1 energy regeneration" options.
Energy regen/degen caps at ±10 pips. Overcast lowers max energy, recovers 1 per 3s, persists through death.

### Basic armor (max armor, before insignia)
| Profession | Armor | Inherent bonus |
|---|---|---|
| Warrior | 80 | +20 vs physical |
| Paragon | 80 | — (+5 energy chest/arms) |
| Ranger | 70 | +30 vs elemental |
| Assassin, Dervish | 70 | (Dervish +25 Health chest) |
| Monk, Necromancer, Mesmer, Elementalist, Ritualist | 60 | — |
Insignia (one per piece; armor from insignia is "core" armor, uncapped): Survivor (Health), Radiant (energy),
Stalwart +10 vs physical, Brawler's +10 while attacking, Blessed +10 while enchanted, Herald's +10 while holding an item,
Sentry's +10 in a stance. Warrior: Knight's (−3 physical damage received), Dreadnought +10 vs elemental, Sentinel's +20
vs elemental (needs 13 Strength), Lieutenant's (−20% hex duration, −5% damage dealt, −20 armor), Stonefist (+1s to
your knockdowns, max 3s). Ranger: Frostbound/Pyrebound/Stormbound/Earthbound +15 vs that element, Scout's +10 during a
preparation, Beastmaster's +10 while pet alive. Monk: Wanderer's +10 vs elemental, Disciple's +15 while conditioned,
Anchorite's +5/+5/+5 while recharging 1/3/5 skills. Necromancer: Blighter's +20 while hexed, Bonelace +15 vs piercing,
Minion Master's +5/+5/+5 for 1/3/5 minions, Tormentor's +10 (but +6/+4/+2 holy damage taken), Undertaker's +5 per
20% Health missing (up to +20), Bloodstained (−25% cast time of corpse spells). Mesmer: Virtuoso's +15 while
activating skills, Artificer's +3 per equipped signet, Prodigy's +5/+5/+5 recharging 1/3/5. Elementalist: Aeromancer/
Geomancer/Hydromancer/Pyromancer +10 vs elemental and +10 more vs their element, Prismatic +5 per Air/Earth/Fire/Water
at 9+. Assassin: Infiltrator's/Saboteur's/Vanguard's +10 physical and +10 vs piercing/slashing/blunt,
Nightstalker's +15 while attacking. Ritualist: Ghost Forge +15 under a weapon spell, Mystic's +15 while activating
skills, Shaman's +5/+5/+5 controlling 1/2/3 spirits. Paragon: Centurion's +10 under a shout/echo/chant.
Dervish: Forsaken +10 while not enchanted, Windwalker +5 per enchantment (up to +20). Mysticism +1 armor per rank only in PvE.
Warrior Rune of Absorption: −1/−2/−3 physical damage taken (non-stacking).
Shields: base armor 16 if requirement met (8 if not), plus handle/inscription bonuses.
Hit locations (normal and ranged attacks): chest 37.5%, legs 25%, head/hands/feet 12.5% each. Only the struck piece's
armor counts; insignia only apply to their own piece. Skill/weapon armor bonuses apply to all pieces.

### Primary attributes (inherent effects)
- Strength (W): attack skills gain 1% armor penetration per rank (not auto-attacks; not if the skill already has AP).
- Expertise (R): −4% energy cost per rank for attack skills, rituals, touch skills and all Ranger skills.
- Divine Favor (Mo): Monk spells that target an ally heal the primary target +3.2 per rank (rounded); untargeted Monk
  spells heal the caster. Applies after the spell's own effect.
- Soul Reaping (N): +1 energy per rank when a non-spirit creature dies within ~2508 gwinches; max 3 triggers / 15s.
- Fast Casting (Me): spells cast in time / 2^(rank/15) (≈ ×0.955^rank); signets −3% per rank. In PvP it does NOT
  affect non-Mesmer spells/signets with activation under 2 seconds. No PvP recharge benefit. Not subject to the −25% cap.
- Energy Storage (E): +3 max energy per rank.
- Critical Strikes (A): +1% crit chance per rank; energy per crit: 1 at ranks 3–7, 2 at 8–12, 3 at 13–17, 4 at 18+.
- Spawning Power (Rt): +4% Health per rank to creatures you create (spirits, minions); +4% weapon spell duration per rank.
- Leadership (P): +2 energy per ally affected by your shouts/chants, max 1 energy per 2 ranks.
- Mysticism (D): −4% cost per rank for Dervish enchantments (armor bonus is PvE only).


## 2. Health, healing, regeneration, conditions

- Regeneration/degeneration: each pip = 2 Health per second; net capped at +10 / −10 pips (cap applied after summing).
  Regeneration is not healing; degeneration is not damage.
- Natural regeneration (not attacking, not losing Health, not targeted by/using foe-targeted spells/signets): starts
  +1 pip after ~5s, +1 pip every 2s, up to +7.
- Healing modifiers: reductions stack multiplicatively, total capped at −40%. "Health gain" and life stealing are not
  healing (unaffected by healing modifiers and Deep Wound, don't trigger on-heal effects). Life stealing ignores armor
  and is not damage.
- Sacrifice is health loss as % of max Health; can kill you; not reducible except by lowering max Health.

### Conditions (fixed effects; don't scale)
| Condition | Effect |
|---|---|
| Bleeding | −3 regen pips (−6 HP/s) |
| Burning | −7 pips (−14 HP/s) |
| Poison | −4 pips (−8 HP/s) |
| Disease | −4 pips; spreads to nearby creatures of the same type |
| Blind | attacks have 90% chance to miss |
| Cracked Armor | −20 armor (cannot reduce below 60) |
| Crippled | move 50% slower |
| Dazed | spells take twice as long to cast; any successful attack interrupts your spells; interrupts a spell on application |
| Deep Wound | −20% max Health; reduced benefit from healing |
| Weakness | attacks deal less damage (wiki: "66%"; see test list) and −1 to all attributes |
Reapplying a condition only extends it if the new duration exceeds what remains. Condition-duration reductions
(runes −20%, off-hand inscriptions −20%) apply separately and round separately. Weapon condition prefixes lengthen
the condition they name by +33% on your hits. Non-fleshy creatures (minions except Flesh Golem, spirits) are immune to
Bleeding, Poison, Disease. Spirits are immune to all conditions except Burning.


## 3. Damage formulas

Armor-respecting damage (weapon damage, most elemental spell damage):
`damage = base × 2^((StrikeLevel − EffectiveArmor) / 40)`
- 60 armor is the baseline: a level 20 spell, or a weapon at rank 12, deals exactly its stated damage to 60 armor.
- Every +40 armor halves damage; every −40 doubles it. −20 armor ≈ ×1.414; +20 ≈ ×0.707.
- Weapon Strike Level = 5 × weapon-mastery rank up to 12, then only +2 per rank above 12 (level 20).
  Rank multiplier relative to 12: 0:35.6% 4:50% 8:70.7% 9:77.1% 10:84.1% 11:91.7% 12:100% 13:103.5% 14:107.2%
  15:111% 16:114.9%.
- Below the weapon's attribute requirement: 1/3 damage. PvP weapons require 9.
- Weapon base damage modifiers multiply: customization ×1.20 (all PvP weapons), damage inscription ×1.10–1.20 (see
  section 4), "slaying" suffixes (PvE only).
- Critical hit: uses the weapon's MAXIMUM damage and the equivalent of −20 armor → max × √2 (×1.414).
  SCYTHES ARE DIFFERENT: scythe crit = max damage × 2^(1/8) (×1.09) instead of ×1.414. Spirits' crits deal no extra
  damage. Pets/minions crit for ×1.414 but not max damage.
- Crit chance vs a level 20 target ≈ weapon-mastery rank % (within 1%); Critical Strikes adds +1%/rank multiplicatively
  with that; skill bonuses (Critical Eye, Way of the Assassin, etc.) add together. Melee hits on a target moving away
  (struck from behind while moving) always crit.
- Attack skill "+X damage" is armor-ignoring and is added into the same damage packet as the weapon hit. Strength's AP
  applies to the weapon part of attack skills.
- Armor penetration: EffectiveArmor = Armor × (1 − AP). Only the highest base AP applies. Air Magic lightning spells
  have 25% AP; Strength 1%/rank for attack skills; Sundering prefix: 20% chance of 20% AP.
- Armor-ignoring: typeless "X damage", shadow damage, most holy damage (undead/minions take double holy), attack-skill
  bonus damage, life stealing, health loss. Chaos/dark damage (wands/staves) respect armor.
- Damage multipliers (Frenzy-type ×2 taken, etc.) apply after armor. Damage reduction order (outline): armor →
  attack-skill bonus → ×2 effects → flat/percentage reductions (Protective Bond, Shielding Hands, etc.).
- Game damage is applied in whole numbers per packet.

### Armor calculation
1. Core armor = basic armor + insignia + base shield armor + inscriptions (uncapped).
2. Bonus armor = all other effects (skills, weapon mods, etc.): if the net bonus is 26 or more, add 25 or the largest
   single bonus if that is higher than 25 (penalties then ignored — known bug). If 25 or less, add it. Negative bonus
   can only lower armor to 60, or to core armor if core is below 60.
3. Apply armor penetration (%).
4. Special armor: "I Am Unstoppable!", Illusionary Weaponry, Mantra of Signets bonuses; critical hits, Barbed Arrows,
   Healing Signet, Shadowy Burden penalties — added last, uncapped.


## 4. Weapons (max-damage PvP weapons)

| Weapon | Damage | Attack interval (s) | Range (gwinches) | Damage type | Notes |
|---|---|---|---|---|---|
| Axe | 6–28 | 1.33 | melee | slashing | big crits |
| Sword | 15–22 | 1.33 | melee | slashing | consistent |
| Hammer | 19–35 | 1.75 | melee | blunt | 2-handed |
| Daggers | 7–17 | 1.33 | melee | piercing/slashing | double strike: 2% + 2%/Dagger Mastery rank; Dual attacks always double strike |
| Scythe | 9–41 | 1.5 | melee | slashing | hits target + up to 2 more foes adjacent to the target (within 180 gwinches of you); every hit gets all skill bonuses; crit ×1.09 |
| Spear | 14–27 | 1.5 | 1004 | piercing | one-handed (shield allowed) |
| Flatbow | 15–28 | 2.025 | 1498 | piercing | high arc, slow projectile (0.88s at shortbow range) |
| Shortbow | 15–28 | 2.025 | 1004 | piercing | |
| Longbow | 15–28 | 2.475 | 1498 | piercing | |
| Recurve | 15–28 | 2.475 | 1273 | piercing | fastest projectile (0.40s) |
| Hornbow | 15–28 | 2.7 | 1273 | piercing | 10% armor penetration |
| Staff / Wand | 11–22 | 1.75 | 1248 | by attribute | damage scales with level, not attribute; extremely low crit rate |
Projectiles deal more damage shooting downhill, less uphill; range also changes with height.

Weapon mods:
- Inscriptions (damage, choose one): "Strength and Honor" +15% while Health >50%; "Guided by Fate" +15% while enchanted;
  "Dance with Death" +15% while in a stance; "Too Much Information" +15% vs hexed foes; "To the Pain!" +15% but −10
  armor while attacking; "Brawn over Brains" +15% but −5 energy; "Vengeance is Mine" +20% while Health <50%;
  "Don't Fear the Reaper" +20% while hexed.
- Prefixes: Sundering (20% chance, 20% AP), Furious (10% chance to double adrenaline gained), Zealous (+1 energy per hit,
  −1 energy regen), Vampiric (steals 3 Health per hit on 1-handed, 5 on 2-handed weapons, −1 Health regen),
  condition prefixes (+33% duration of that condition: Barbed/Bleeding, Crippling/Crippled, Cruel/Deep Wound,
  Heavy/Weakness, Poisonous/Poison, Silencing/Dazed), Ebon/Fiery/Icy/Shocking convert damage to earth/fire/cold/lightning
  (gets around a Warrior's +20 vs physical).
- Suffixes: of Defense +5 armor, of Fortitude +30 Health, of Shelter +7 armor vs physical, of Warding +7 vs elemental,
  of Enchanting +20% enchantment duration, of Mastery (+1 attribute, 20% chance).
  (Mod numbers other than inscriptions and prefixes' condition +33% are general game knowledge, not pulled this session.)
- Caster mods: "halves casting time" and "halves skill recharge" (chance 10–20%, of the item's attribute or all spells),
  +energy, Health while enchanted/hexed/in stance.

Reference DPS (uncustomized, no crits, rank 12, vs 60 armor): axe 12.75, sword 13.88, hammer 15.43, daggers 11.34,
scythe 14.29 per target, spear 13.67, flat/short 10.75, long/recurve 8.96, hornbow 8.84, staff/wand 9.43.


## 5. Timing: attacks, casting, aftercast

### Attack skills and attack rate
- Auto-attacks: one hit per attack interval; the hit lands halfway through the swing.
- Attack skill with NO stated activation time: takes one normal attack interval of your weapon; hits at the halfway
  point. Chaining these is the same cadence as auto-attacking.
- Attack skill WITH a stated activation time (e.g. ½s or 1s): that activation replaces the weapon swing; the hit lands
  halfway through it, and it skips the "return to neutral" second half of the previous attack. So a short-activation
  attack used right after another attack lands much sooner. Example: Executioner's Strike after Eviscerate lands 1.33s
  later; Agonizing Chop (1s activation) after Eviscerate lands 0.5s later.
- IAS/DAS scale attack intervals AND attack-skill activation times. Spell-affecting cast-time effects (Migraine etc.)
  don't affect attack skills.
- IAS stacking is multiplicative, capped at +33% faster (interval ×0.67) and −50% slower (×1.5 intervals). Stated "+33%"
  shortens the interval by 33% → ~+49% attacks per second; "+25%" → +33%; "−30%" → −23%; "−50%" → −33%.
  Real rate gain = x/(100−x).
- Hit timing example: Protector's Strike under Frenzy: interval ⅓s, connects ~0.17s after activation.
- Aftercast: attack skills with a stated activation have NO aftercast, except Ranger bow skills with activation times
  (¾s aftercast). Bow/dagger/hammer attack skills without activation have a ¾s animation; other weapons ½s.
- Adrenaline: 1 strike (25 units) per successful weapon hit (per hit for multi-hit attacks); 1 unit per 1% of max Health
  lost to damage. Each adrenal skill fills its own pool. Using an adrenal skill empties its pool and removes 1 strike from
  every other adrenal skill. Recharging/disabled adrenal skills can't build adrenaline. All adrenaline is lost on death or
  after 25s without gaining any. Adrenaline gain multipliers cap at +100%; flat adrenaline gains are uncapped.

### Spells, signets and other skills
- Most spells, signets, glyphs, chants, echoes, rituals: stated cast time + ¾s aftercast (can't move, attack or act).
- No activation and no aftercast: shouts, stances, flash enchantments (can be used while acting/knocked down, except
  flash enchantments can't be used while activating another skill or knocked down).
- Activation-time modifiers (non-attack) cap at −25% and +150%; Fast Casting is outside that cap.
  Dazed doubles spell cast time.
- Recharge: starts when the skill finishes or is interrupted; failed skills recharge instantly. Recharge reductions stack
  multiplicatively to −50% (a single skill effect can exceed it). Effects altering recharge round to the nearest second.
- Interrupts stop any skill with an activation time and all attacks; interrupted skill goes on full recharge. Knockdown
  (2s default; 3s with Stonefist/some skills) is not an interrupt, so anti-interrupt effects don't stop it.
- Fail: requirement not met / target dies / failure effect → costs are lost, skill recharges instantly. Low-attribute
  skills that say so have ~50% fail chance.


## 6. Defense mechanics
- Block and miss chances stack multiplicatively (two 50% = 75%); miss is checked before block. Blocked attacks deal no
  damage and give no adrenaline. "Evade" no longer exists (now block).
- Only one stance at a time (new one replaces; old one's end effect triggers if any). One preparation, glyph, weapon
  spell, form at a time. Holding one bundle (item spell ashes) at a time.
- Enchantment/hex reapplied: if the new cast would be weaker, the stronger values continue until the original would
  expire; if equal or stronger, it acts as newly cast. Enchantment/hex removal usually takes the most recent one
  ("covering").
- Upkeep: each maintained enchantment = −1 energy pip; lost if net energy degen would pass −10, if energy hits 0, or
  if the target leaves party range (5020) for more than 5 seconds.


## 7. Ranges (gwinches)
| Range | Gwinches | Notes |
|---|---|---|
| Touch / melee | 144 | targeting distance for melee and touch skills |
| Adjacent | 166 | "adjacent to you / to target"; scythe extra hits |
| Nearby | 252 | some skills use 240 (Aftershock, Earthquake, Liquid Flame, Gust, etc.) |
| In the area | 322 | largest offensive-spell AoE; wards and wells |
| Half range | ≈624 (half casting range; ~0.6 × aggro bubble) | for bow skills, half the bow's range |
| Shortbow / spear | 1004 | |
| Earshot (aggro bubble) | 1012 | most shouts/chants AoE (some 1000); targeted shouts use casting range |
| Casting range | 1248 | spells, signets, targeted shouts, wands/staves |
| Recurve / hornbow | 1273 | |
| Flatbow / longbow / attack spirits | 1498 | |
| Spirit range | 2512 | passive spirit effects; same-name spirit replaces within this range |
| Large nature ritual range | 3500 | stated on some nature rituals since Feb 2026; wiki notes the increase may not have happened in game — test |
| Soul Reaping | 2508 | |
| Party / compass range | 5020 | party-wide skills; maintained enchantments drop beyond it |


## 8. Summoned creatures
### Spirits (nature rituals and binding rituals)
- Health ≈ 20 × level, +4% per Spawning Power rank of the creator (e.g. level 10: 200 HP at 0 SP, 296 at 12 SP;
  level 20: 400 / 592). Armor ≈ 2 + 6 × level (level 10: 62, level 15: 92, level 20: 122). Level is stated in each
  ritual's description and scales with attribute.
- Attack spirits: ranged attacks every 2s (2s activation), longbow range (1498), armor-ignoring damage, can crit but
  crits do no extra damage. 31 energy, 4 pips.
- Immune to enchantments, hexes, other spirits' passives, weapon spells, wards, healing (Divine Favor included), and all
  conditions except Burning. "Health gain" effects work on them. Can be knocked down. Affected by shouts/chants unless
  the skill says otherwise. Allies, not party members. Non-fleshy. Same-name allied spirit inside spirit range replaces
  the old one (triggering end effects); nature rituals also replace enemy ones of the same name.
### Minions (Necromancer)
- Armor 3.75 × level + 5 (Bone Fiend 2.84 × level + 3.1). Health degeneration starts at 1 pip and grows by 1 pip every
  20 seconds (a level 18 minion lives ~84s). Melee minions attack every 3.1s; Bone Fiends every 1.86s at half longbow
  range. Crits do ×1.414 but not max damage. Control limit: 2 + 1 per 2 ranks of Death Magic (12 DM → 8, 16 → 10).
- Non-fleshy (except Flesh Golem); take double holy damage; become masterless (hostile to everyone) if the master dies.
### Pets (Ranger animal companion)
- Level 20: 80 armor; Health 480 (Elder), 540 Hearty, 510 Playful, 450 Aggressive, 420 Dire. Damage at 12 Beast Mastery
  (non-crit): Elder 17–29, Dire 20–32, Hearty 15–25; crit ≈ ×1.414 (not max). Attack every 2s (Racing Beetle and Moa
  faster). Most pets move 25% faster than normal. In GvG (death penalty applies), when your pet dies your skills are
  disabled for 10..3 seconds (Beast Mastery 0..15). Pet attack skills only work within party range.


## 9. Stacking caps (summary)
| Property | Max bonus | Max penalty | Notes |
|---|---|---|---|
| Attack speed | +33% | −50% | multiplicative |
| Movement speed | +34% | −50% | a few skills exceed (Burning Speed, Pious Haste, Dash, Junundu Tunnel; Winter's Embrace below) |
| Block / miss chance | 100% | — | multiplicative |
| Healing | — | −40% | multiplicative |
| Adrenaline gain | +100% | −50% | |
| Health / energy regen | +10 pips | −10 pips | also for single effects |
| Recharge time | — | −50% | single skill effect can bypass |
| Activation time | +150% | −25% | Fast Casting exempt |
| Armor (bonus) | +25 | to 60 | see armor calculation |
| Attributes | 20 | 0 | 21 with weapon chance mods |
Most skill effects of the same skill don't stack (newest or strongest wins). Different skills' effects stack unless capped.
