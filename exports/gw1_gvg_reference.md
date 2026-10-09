# Guild Wars 1 — GvG Skill & Mechanics Reference

Source: Guild Wars Wiki (wiki.guildwars.com), pulled 2026-10-08. Skill data reflects the live game, including the
balance passes ArenaNet has shipped since February 2026. Format: GvG only (8v8, level 20, PvP rules).

## 0. How to use this file (instructions for the assistant)

- Treat the skill entries below as the authoritative numbers. Quote values from the file; do not rely on memory for
  skill numbers, because many skills were rebalanced in 2026.
- Only PvP-legal skills are listed. PvE-only skills are excluded. Where a skill has a separate PvP version, only the
  "(PvP)" version is listed — that is the version used in GvG.
- When asked for damage, DPS, healing, timing or energy math, compute it with the formulas in sections 3–7 and show
  the assumptions (attribute ranks, armor, weapon, crit chance, modifiers).
- Mark anything that comes from general knowledge rather than this file as such.
- Section 15 holds mechanics the user has verified by in-game testing. Those override the wiki when they conflict.
- Default GvG assumptions unless the user says otherwise: level 20, max armor, max-damage PvP weapons (PvP weapons are
  always max stats, requirement 9, and auto-customized for +20% damage), everything else (runes, insignia,
  inscriptions, attribute spread) variable.

### Skill entry format
```
Name #ID | [Elite] Type | Campaign | costs
  Description. Ranges shown as a..b = value at attribute rank 0..rank 15.
  ~ Variable :: values at ranks 0-21, grouped in fives (e.g. "10-14: v10 v11 v12 v13 v14")
  # tags: conditions/effects caused, removed or prevented; target; range; area of effect; flags
  ! BUG / ANOMALY notes from the wiki (mechanical quirks not in the description)
```
Costs: E = energy, Ad = adrenaline strikes, S = sacrifice (% of max Health), U-1 = upkeep (−1 energy regeneration
pip while maintained), O = overcast, C = activation (cast) time in seconds, R = recharge in seconds. No C means no
activation time (instant, or for attack skills: uses the weapon's attack timing — see section 5).
`[derived]` progression lines were not on the wiki's progression table; they are computed from the description range
with the wiki's own formula: value(rank) = round(v0 + rank × (v15 − v0)/15), rounding half away from zero.
"#ID" is the skill ID used in skill template codes (from Skill_template_format/Skill_list).

Effective attribute ranks above 12 come from a superior rune (+3, primary profession only), headgear (+1, primary
profession only) and skills/effects. Rank cap is 20 (21 with weapon "+1 attribute (chance)" mods).

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

## 10. GvG context
- 8v8 in guild halls. Win: kill the enemy Guild Lord, or all enemies reach 60% death penalty, or at 28 minutes the
  more "aggressive" team wins the tiebreak.
- Flag stand: holding it 2 minutes with your flag grants a 10% morale boost. Most teams run a dedicated flag runner.
- Resurrection shrine cycle every 2 minutes (resurrect with full energy and recharged skills). Resurrection Signet only
  recharges on a morale boost. Death penalty applies (−15% per death).
- NPCs: footmen, archers, knights, bodyguard around the Guild Lord. Victory or Death at 18 minutes: NPCs march to the
  center in waves (archers 18:00, archers 18:15, knights+bodyguard 18:30), Guild Lord advances at 20:00; NPCs deal 30%
  more damage, +5% more each minute after.
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

## 12. Known gaps / open questions
- Exact base crit-chance formula (approximation above).
- Weakness damage reduction wording ("66%"): 66% less or 66% of normal — test.
- Whether the Feb 2026 nature ritual range increase (3500) is live.
- Order of damage modifiers page is partly outdated per the wiki.

## 13. Verification scenarios (Master of Damage, 60 armor; predictions from the formulas above)
Assumptions: max PvP weapon (customized ×1.2), rank 12 weapon mastery, crit chance 12% (16% at rank 16), no buffs.
| # | Test | Prediction |
|---|---|---|
| 1 | Axe auto-attack DPS, 3 min | ≈17.8 DPS (≈20.4 with +15% inscription) |
| 2 | Sword auto-attack | ≈18.1 DPS |
| 3 | Hammer auto-attack | ≈20.4 DPS; non-crit hits avg 32 (23–42), crits 59 |
| 4 | Daggers auto-attack, 12 Dagger Mastery | ≈15.3 DPS (26% double-strike; effective interval ≈1.06s) |
| 5 | Scythe auto-attack (Master of Damage counts only him) | ≈21.9 DPS; crit hits ≈54 (×1.09, not ×1.414); normal hits 11–49 |
| 6 | Same weapon at 16 mastery (rune+headgear) | ≈+15% damage per hit vs rank 12 (not +33%) |
| 7 | Any weapon under a +33% IAS (e.g. Frenzy/Flurry) | interval ×0.67; DPS ≈ ×1.49 |
| 8 | Two IAS effects stacked | still capped at ×0.67 interval |
| 9 | Eviscerate at 12 Axe, 12 Strength | non-crit 46–76 (avg ≈61: weapon with 12% AP + 38 armor-ignoring bonus); crit ≈92 |
| 10 | Eviscerate → Agonizing Chop timing | second hit lands ~0.5s after the first (vs 1.33s for a no-activation follow-up) |
| 11 | Fire spell with stated damage X (level 20) | exactly X per hit |
| 12 | Air (lightning) spell with stated damage X | ≈ X × 1.30 (25% AP vs 60 armor) |
| 13 | Burning alone on Master of Damage, 10s | 140 damage counted (−14 HP/s) |
| 14 | Burning + Poison + Bleeding | capped at −10 pips → 20 HP/s, not 28 |
| 15 | Weakness on you, auto-attacking | either ×0.34 or ×0.66 DPS — tells us which reading is right |
| 16 | Vampiric axe | +3 per hit counted as damage (life steal) |
| 17 | Cracked Armor on Master of Damage | no change (60 armor floor); same weapon DPS |
| 18 | Hornbow vs longbow | hornbow per-hit ×1.11 (10% AP vs 60 armor) but slower interval |

## 14. Wiki bug/anomaly notes
Included per skill as `!` lines. Lines tagged "[from PvE version page]" are notes written for the PvE version of a skill
that also has a PvP version; they usually still apply but check numbers.

## 15. User-verified mechanics (overrides wiki)
(none yet — to be added from in-game testing)

---
# SKILL DATA (1,235 PvP-legal skills, grouped by profession then attribute)
## Warrior

### Warrior / Axe Mastery
Agonizing Chop #1403 | Axe Attack | Nightfall | Ad6 C1
  When this attack hits, you deal +5..20 damage. If target foe is suffering from a Deep Wound, you interrupt that foe's action.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Interrupt
Axe Rake #334 | Axe Attack | Core | Ad5
  If this attack hits a foe suffering from a Deep Wound, you strike for +4..16 damage, and that foe becomes Crippled for 15 seconds.
  ~ + Damage :: 0-4: 4 5 6 6 7 | 5-9: 8 9 10 10 11 | 10-14: 12 13 14 14 15 | 15-19: 16 17 18 18 19 | 20-21: 20 21
  # causes: Crippled
Axe Twist #342 | Axe Attack | Prophecies | Ad5
  If this attack hits a foe suffering from a Deep Wound, you strike for 5..25 more damage and that foe suffers from Weakness for 20 seconds.
  ~ + Damage :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  # causes: Weakness
Cleave #335 | Elite Axe Attack | Core | Ad4
  If this attack hits, you strike for +10..40 damage and hit 1..2 adjacent foe[s] for 10..40 slashing damage.
  ~ + Damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  ~ Adjacent foes hit :: 0-4: 1 1 1 1 1 | 5-9: 1 1 1 2 2 | 10-14: 2 2 2 2 2 | 15-19: 2 2 2 2 2 | 20-21: 2 2
  ~ Damage to adjacent foes :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  ! BUG: Contrary to the descriptions, damage is dealt to an additional 2..3 foes.
Critical Chop #1402 | Axe Attack | Nightfall | E5 C1 R15
  If this attack hits, you inflict +5..20 damage. If this attack results in a critical hit, target foe is interrupted.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Interrupt
Cyclone Axe #330 | Axe Attack | Core | E5 R4
  Perform a spinning axe attack striking for +4..12 damage to all adjacent opponents.
  ~ + Damage :: 0-4: 4 5 5 6 6 | 5-9: 7 7 8 8 9 | 10-14: 9 10 10 11 11 | 15-19: 12 13 13 14 14 | 20-21: 15 15
  # target: foes; aoe: adjacent
Decapitate #1696 | Elite Axe Attack | Nightfall | Ad7
  You lose all adrenaline and all Energy. This attack is unblockable, you deal +5..80 damage and cause a Deep Wound for 5..20 seconds. This attack is always critical and if foe is killed, nearby foes are Weakened for 8 seconds.
  ~ + Damage :: 0-4: 5 10 15 20 25 | 5-9: 30 35 40 45 50 | 10-14: 55 60 65 70 75 | 15-19: 80 85 90 95 100 | 20-21: 105 110
  ~ Deep Wound duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Deep Wound, Critical Hit, Adrenaline Loss, Energy Loss, Weakness, Unblockable
  ! ANOMALY: The concise description fails to mention that the attack is unblockable
Dismember #337 | Axe Attack | Core | Ad5
  If it hits, this axe blow will inflict a Deep Wound on the target foe, lowering that foe's maximum Health by 20% for 5..20 seconds.
  ~ Deep Wound duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Deep Wound
Disrupting Chop #340 | Axe Attack | Core | Ad5 R0
  If it hits, this attack interrupts the target's current action. If that action was a skill, that skill is disabled for an additional 20 seconds.
  # causes: Disable
Eviscerate #338 | Elite Axe Attack | Prophecies | Ad8
  If Eviscerate hits, you strike for +10..45 damage and inflict a Deep Wound, lowering your target's maximum Health by 20% for 5..20 seconds.
  ~ + Damage :: 0-4: 10 12 15 17 19 | 5-9: 22 24 26 29 31 | 10-14: 33 36 38 40 43 | 15-19: 45 47 50 52 54 | 20-21: 57 59
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Deep Wound
Executioner's Strike #336 | Axe Attack | Core | Ad7
  If this attack hits, you strike for +15..45 damage.
  ~ + Damage :: 0-4: 15 17 19 21 23 | 5-9: 25 27 29 31 33 | 10-14: 35 37 39 41 43 | 15-19: 45 47 49 51 53 | 20-21: 55 57
Furious Axe #904 | Axe Attack | Factions | E5 R6
  If Furious Axe hits, you strike for +5..35 damage. If it is blocked you gain 3 strikes worth of adrenaline.
  ~ + Damage :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  # causes: Adrenaline Gain
Keen Chop #2009 | Axe Attack | Eye of the North | Ad3
  If it hits, this attack always results in a critical hit.
  # causes: Critical Hit
Lacerating Chop #849 | Axe Attack | Factions | Ad5
  If Lacerating Chop hits, you deal +5..20 damage. If it strikes a knocked down foe your target suffers from Bleeding for 5..20 seconds.
  ~ +Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Bleeding :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Bleeding; requires: Knockdowm
Penetrating Blow #339 | Axe Attack | Prophecies | Ad5
  If this attack hits, you strike for +10..25 damage. This axe attack has 20% armor penetration.
  ~ + Damage :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  # special: Duplicate
Penetrating Chop #1136 | Axe Attack | Factions | Ad5
  If this attack hits, you strike for +10..25 damage. This axe attack has 20% armor penetration.
  ~ + Damage :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  # special: Duplicate
Swift Chop #341 | Axe Attack | Core | E5 R4
  If this attack hits, you strike for +1..20 damage. If Swift Chop is blocked, target foe takes 1..20 damage and suffers a Deep Wound for 20 seconds.
  ~ + Damage :: 0-4: 1 2 4 5 6 | 5-9: 7 9 10 11 12 | 10-14: 14 15 16 17 19 | 15-19: 20 21 23 24 25 | 20-21: 26 28
  ~ Damage if blocked :: 0-4: 1 2 4 5 6 | 5-9: 7 9 10 11 12 | 10-14: 14 15 16 17 19 | 15-19: 20 21 23 24 25 | 20-21: 26 28
  # causes: Block Punishment, Deep Wound
Triple Chop #992 | Elite Axe Attack | Factions | E5 R10
  Attack target foe and adjacent foes. Each attack that hits deals +10..40 damage.
  ~ + Damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # target: foes; aoe: adjacent
  ! ANOMALY: The concise description incorrectly implies a single attack hitting multiple targets.
Whirling Axe #888 | Elite Axe Attack | Factions | Ad4
  If Whirling Axe hits, you strike for +5..20 damage and any stance being used by your target ends. This attack cannot be blocked.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Unblockable; removes: Stance

### Warrior / Hammer Mastery
Auspicious Blow (PvP) #3455 | Hammer Attack | Factions | Ad5
  If Auspicious Blow hits, you strike for +5..20 damage and gain 2..4 Energy. If target foe is suffering from Weakness, this attack is unblockable.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Energy gain :: 0-4: 2 2 2 2 3 | 5-9: 3 3 3 3 3 | 10-14: 3 3 4 4 4 | 15-19: 4 4 4 4 5 | 20-21: 5 5
  # causes: Unblockable, Energy Gain; requires: Weakness
Backbreaker #358 | Elite Hammer Attack | Prophecies | Ad9
  If Backbreaker hits, you strike for +1..20 damage and your target is knocked down. If you have 8 Strength or higher, this knockdown lasts 4 seconds.
  ~ + Damage :: 0-4: 1 2 4 5 6 | 5-9: 7 9 10 11 12 | 10-14: 14 15 16 17 19 | 15-19: 20 21 23 24 25 | 20-21: 26 28
  # causes: Knockdown
Belly Smash #350 | Hammer Attack | Prophecies | E5 C1 R10
  If this attack strikes a foe who is knocked down, the resulting dust cloud will blind adjacent foes for 3..7 seconds.
  ~ Blind duration :: 0-4: 3 3 4 4 4 | 5-9: 4 5 5 5 5 | 10-14: 6 6 6 6 7 | 15-19: 7 7 8 8 8 | 20-21: 8 9
  # causes: Blind; target: untargeted; aoe: adjacent
Counter Blow #357 | Hammer Attack | Core | Ad4
  If this attack hits an attacking foe, that foe is knocked down.
  # causes: Knockdown
Crude Swing #353 | Hammer Attack | Prophecies | E5 R5
  Attack all adjacent foes. Each foe you hit is struck for +1..20 damage.
  ~ + Damage :: 0-4: 1 2 4 5 6 | 5-9: 7 9 10 11 12 | 10-14: 14 15 16 17 19 | 15-19: 20 21 23 24 25 | 20-21: 26 28
  # target: foes; aoe: adjacent
Crushing Blow #352 | Hammer Attack | Prophecies | E5 R10
  If this attack hits, you strike for +1..20 damage. If you hit a knocked-down foe you inflict a Deep Wound, lowering your target's maximum Health by 20% for 5..20 seconds.
  ~ + Damage :: 0-4: 1 2 4 5 6 | 5-9: 7 9 10 11 12 | 10-14: 14 15 16 17 19 | 15-19: 20 21 23 24 25 | 20-21: 26 28
  ~ Deep Wound duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Deep Wound
Devastating Hammer #355 | Elite Hammer Attack | Core | Ad7
  If Devastating Hammer hits, your target is knocked down and suffers from Weakness for 5..20 seconds.
  ~ Weakness duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Knockdown, Weakness
Earth Shaker #354 | Elite Hammer Attack | Prophecies | Ad8
  Target foe and all adjacent foes are knocked down. (50% failure chance with Hammer Mastery 4 or less.)
  # causes: Knockdown; target: foes; aoe: adjacent
Enraged Smash (PvP) #2808 | Elite Hammer Attack | Factions | E5 R10
  If Enraged Smash hits, you gain 1..3 strike[s] of adrenaline. If you hit a moving foe, you strike for +10..40 damage, and target foe is knocked down.
  ~ Adrenaline gain :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  ~ + Damage (on moving foe) :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Adrenaline Gain, Knockdown
Fierce Blow #850 | Hammer Attack | Factions | Ad6
  If Fierce Blow hits, you strike for +5..20 damage. If target foe was suffering from Weakness, that foe also suffers from a Deep Wound for 1..8 second[s].
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Deep Wound duration :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  # causes: Deep Wound
Forceful Blow #889 | Elite Hammer Attack | Factions | Ad5
  If Forceful Blow hits, you strike for +10..30 damage and any stance being used by target foe ends. Target foe suffers from Weakness for 5..20 seconds. This attack cannot be blocked.
  ~ + Damage :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  ~ Weakness duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Unblockable, Weakness; removes: Stance
Hammer Bash #331 | Hammer Attack | Core | Ad6
  Lose all adrenaline. If Hammer Bash hits, your target is knocked down.
  # causes: Knockdown, Adrenaline Loss
Heavy Blow #359 | Hammer Attack | Core | Ad5
  Lose all adrenaline. If this attack hits a foe suffering from Weakness, that foe is knocked down and you strike for +1..30 damage.
  ~ + Damage :: 0-4: 1 3 5 7 9 | 5-9: 11 13 15 16 18 | 10-14: 20 22 24 26 28 | 15-19: 30 32 34 36 38 | 20-21: 40 42
  # causes: Knockdown, Adrenaline Loss
  ! ANOMALY: If you are under the influence of Withering Aura and your target is not suffering from weakness at the beginning of this attack, then your target will be knocked down but will not suffer the extra damage.
Irresistible Blow #356 | Hammer Attack | Core | E5 R6
  If this attack hits, you strike for +5..20 damage. If Irresistible Blow is blocked, your target is knocked down and takes 5..20 damage.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Damage if blocked :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Block Punishment, Knockdown
Magehunter's Smash #1697 | Elite Hammer Attack | Nightfall | Ad8
  If this attack hits, target foe is knocked down. If your target is under the effects of an enchantment, this attack cannot be blocked.
  # causes: Knockdown, Unblockable
Mighty Blow #351 | Hammer Attack | Core | Ad7
  If this attack hits, you strike for +10..40 damage.
  ~ + Damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
Mokele Smash #1409 | Hammer Attack | Nightfall | E5 R12
  If this attack hits, you strike for +5..20 damage and gain 2 strikes of adrenaline.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Adrenaline Gain
Overbearing Smash #1410 | Hammer Attack | Nightfall | E5 R20
  If this attack hits, you deal +1..20 damage. If target foe is knocked down, that foe is Dazed for 1..8 second[s].
  ~ + Damage :: 0-4: 1 2 4 5 6 | 5-9: 7 9 10 11 12 | 10-14: 14 15 16 17 19 | 15-19: 20 21 23 24 25 | 20-21: 26 28
  ~ Dazed duration :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  # causes: Dazed
Pulverizing Smash #2008 | Hammer Attack | Eye of the North | Ad4
  If you hit a knocked-down foe, that foe suffers from Weakness and a Deep Wound for 5..20 seconds.
  ~ Weakness and Deep Wound duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Weakness, Deep Wound
Renewing Smash (PvP) #3143 | Hammer Attack | Factions | E5 R30
  If Renewing Smash hits, it deals +5..20 damage. If it hits a knocked-down foe, you gain 3 Energy and this attack recharges instantly.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Energy Gain, Recharge
Staggering Blow #360 | Hammer Attack | Core | Ad4 C1
  If this hammer blow hits, your target will suffer from Weakness for 5..20 seconds.
  ~ Weakness duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Weakness
Yeti Smash #1137 | Hammer Attack | Factions | Ad6
  Lose all adrenaline. Attack all adjacent foes. If this attack strikes a foe suffering from a condition, that foe is knocked down. (50% failure chance with Hammer Mastery 4 or less.)
  # causes: Knockdown, Adrenaline Loss; target: foes; aoe: adjacent

### Warrior / No Attribute
"Coward!" (PvP) #3456 | Elite Shout | Factions | Ad4 R4
  If target foe is moving, that foe is knocked down.
  # causes: Knockdown; target: foes; aoe: none
"For Great Justice!" (PvP) #2883 | Shout | Core | E5 R45
  For 8 seconds, when you hit with an attack, you gain 1 additional strike of adrenaline.
  # causes: Adrenaline Gain; aoe: None
  ! ANOMALY: Unlike most skills that increase the rate of adrenaline gain by a multiplier, this doubles all non-multiplier sources of adrenaline, not just the basic 1 strike from making an attack. [from PvE version page]
"On Your Knees!" #906 | Shout | Factions | Ad6
  Lose all adrenaline. If any adjacent foes are knocked down, all of your stances are recharged.
  # causes: Adrenaline Loss, Recharge; aoe: none
"You're All Alone!" #1412 | Elite Shout | Nightfall | E5 R10
  If target foe isn't near an ally, that foe suffers from Cripple and Weakness for 8 seconds.
  # causes: Crippled, Weakness; target: foes; range: Casting
Distracting Blow #325 | Melee Attack | Core | E5 C½ R10
  Swipe your weapon at the target, dealing no damage but disrupting the target's current action (and the actions of foes adjacent to your target).
  # causes: Interrupt; aoe: adjacent
  ! ANOMALY: The concise description is incorrect: the adjacent foes are interrupted but not attacked. Notably, you won't gain adrenaline from them, and Illusionary Weaponry will not damage them (unless wielding a scythe).
Distracting Strike #2194 | Melee Attack | Eye of the North | E5 C½ R15
  If Distracting Strike hits, it deals no damage and interrupts target foe's action. If target foe has Cracked Armor, that skill is disabled for 30 seconds.
  # causes: Interrupt, Disable
  ! ANOMALY: Unlike Distracting Blow, Distracting Strike deals a damage packet of zero rather than no damage.
Flurry #344 | Stance | Prophecies | E5 R5
  For 5 seconds, your attack rate is increased by 33%, but you deal 25% less damage.
  # causes: Increased Attack Speed
  ! BUG: Contrary to the description, the 25% damage reduction only applies to base damage.
Frenzied Defense #1700 | Stance | Nightfall | E5 R10
  For 8 seconds, you have a 75% chance to block incoming attacks, but take double damage.
  # causes: Block
Grapple #2011 | Touch skill | Eye of the North | E5 C¾ R8
  Skill. You and target touched foe are knocked down. You lose your current stance.
  # causes: Knockdown; removes: Stance; target: foes; range: touch
  ! ANOMALY: This skill has no aftercast delay, though this can only be observed if the self knockdown is prevented.
Skull Crack #329 | Elite Melee Attack | Prophecies | Ad6 C¼
  If it hits, this attack interrupts the target's current action. If that foe was casting a spell, that foe is Dazed for 15 seconds.
  # causes: Dazed, Interrupt
Symbolic Strike #2195 | Melee Attack | Eye of the North | Ad4
  If this attack hits, you deal +12 damage for each signet you have equipped (maximum 70 damage).
Wild Blow #321 | Melee Attack | Core | E5 R8
  Lose all adrenaline. If it hits, this attack will result in a critical hit and any stance being used by your target ends. This attack cannot be blocked.
  # causes: Unblockable, Critical Hit, Adrenaline Loss; removes: Stance

### Warrior / Strength
"I Meant to Do That!" #2067 | Shout | Eye of the North | E5 R8
  If you are knocked down, you gain 1..6 strikes of adrenaline.
  ~ Adrenaline gain :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  # causes: Adrenaline Gain; aoe: None
"I Will Avenge You!" #333 | Shout | Prophecies | E5 R45
  For each dead ally, you gain 10 seconds of +3..7 Health regeneration and your attack speed increases by 25%.
  ~ Health regeneration :: 0-4: 3 3 4 4 4 | 5-9: 4 5 5 5 5 | 10-14: 6 6 6 6 7 | 15-19: 7 7 8 8 8 | 20-21: 8 9
  # causes: Health Regeneration, Increased Attack Speed; target: self; range: compass; aoe: none
"I Will Survive!" #368 | Shout | Prophecies | E5 R30
  You gain +3 Health regeneration for each condition you are suffering. This regeneration expires after 5..11 seconds.
  ~ Duration :: 0-4: 5 5 6 6 7 | 5-9: 7 7 8 8 9 | 10-14: 9 9 10 10 11 | 15-19: 11 11 12 12 13 | 20-21: 13 13
  # causes: Health Regeneration; aoe: None
"You Will Die!" #1141 | Shout | Factions | E5 R15
  If target foe is below 90% Health, you gain 1..3 strike[s] of adrenaline.
  ~ Adrenaline gain :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Adrenaline Gain; target: foes; aoe: None
Battle Rage #317 | Elite Stance | Core | Ad4
  For 5..20 seconds, you move 33% faster and gain double adrenaline from attacks. Battle Rage ends if you use any non-adrenal skills.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Increased Movement Speed, Increased Adrenaline Build Rate
Berserker Stance #370 | Stance | Core | E10 R10
  For 8..14 seconds, you attack 33% faster and gain 100% more adrenaline. Berserker Stance ends if you use a skill.
  ~ Duration :: 0-4: 8 8 9 9 10 | 5-9: 10 10 11 11 12 | 10-14: 12 12 13 13 14 | 15-19: 14 14 15 15 16 | 20-21: 16 16
  # causes: Increased Attack Speed, Increased Adrenaline Build Rate
Body Blow #2197 | Melee Attack | Eye of the North | Ad7
  If this attack hits, target foe takes +10..40 damage. If target foe has Cracked Armor, that foe suffers from a Deep Wound for 0..15 second[s].
  ~ + Damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  ~ Deep Wound duration :: 0-4: 0 1 2 3 4 | 5-9: 5 6 7 8 9 | 10-14: 10 11 12 13 14 | 15-19: 15 16 17 18 19 | 20-21: 20 21
  # causes: Deep Wound
Bull's Charge #379 | Elite Stance | Prophecies | E5 R12
  For 1..7 seconds, you move 50% faster and if you strike a moving foe in melee, that foe is knocked down. Bull's Charge ends if you use a skill.
  ~ Duration :: 0-4: 1 1 2 2 3 | 5-9: 3 3 4 4 5 | 10-14: 5 5 6 6 7 | 15-19: 7 7 8 8 9 | 20-21: 9 9
  # causes: Increased Movement Speed, Knockdown
Bull's Strike #332 | Melee Attack | Core | E5 R10
  If this attack hits a moving foe, you strike for +5..30 damage, and your target is knocked down.
  ~ + Damage :: 0-4: 5 7 8 10 12 | 5-9: 13 15 17 18 20 | 10-14: 22 23 25 27 28 | 15-19: 30 32 33 35 37 | 20-21: 38 40
  # causes: Knockdown
Burst of Aggression #1413 | Stance | Nightfall | E5 R12
  For 2..10 seconds, you attack 33% faster. When this stance ends, you lose all adrenaline.
  ~ Duration :: 0-4: 2 3 3 4 4 | 5-9: 5 5 6 6 7 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 13
  # causes: Increased Attack Speed, Adrenaline Loss
Charging Strike (PvP) #3465 | Elite Stance | Nightfall | E5 R5
  For 1..10 second[s], you run 33% faster. Your next successful melee hit does +10..80 damage and this stance ends. This stance ends if you use a skill.
  ~ Duration :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ + Damage :: 0-4: 10 15 19 24 29 | 5-9: 33 38 43 47 52 | 10-14: 57 61 66 71 75 | 15-19: 80 85 89 94 99 | 20-21: 103 108
  # causes: Increased Movement Speed
Counterattack #1693 | Melee Attack | Nightfall | E5 R6
  If this attack hits, you strike for +5..35 damage. If you hit an attacking foe, you gain 2..6 Energy.
  ~ + Damage :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  ~ Energy gain :: 0-4: 2 2 3 3 3 | 5-9: 3 4 4 4 4 | 10-14: 5 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 7 8
  # causes: Energy Gain
Defy Pain (PvP) #3204 | Elite Stance | Prophecies | Ad5
  For 20 seconds you have an additional 90..300 Health and an additional 20 armor.
  ~ + Maximum health :: 0-4: 90 104 118 132 146 | 5-9: 160 174 188 202 216 | 10-14: 230 244 258 272 286 | 15-19: 300 314 328 342 356 | 20-21: 370 384
  # causes: Increased Maximum Health, Increased Armor Rating
Disarm #2066 | Sword Attack | Eye of the North | E5 C½ R20
  Interrupt target foe's action. If that action was an attack, all of that foe's attack skills are disabled for 0..3 second[s].
  ~ Disabled duration :: 0-4: 0 0 0 1 1 | 5-9: 1 1 1 2 2 | 10-14: 2 2 2 3 3 | 15-19: 3 3 3 4 4 | 20-21: 4 4
  # causes: Interrupt, Disable
Dolyak Signet #361 | Signet | Prophecies | R20
  For 8..20 seconds, you have +10..40 armor and cannot be knocked down, but your movement is slowed by 75%.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  ~ + Armor rating :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Increased Armor Rating, Knockdown Immunity, Decreased Movement Speed
  ! ANOMALY: Even though it has no activation time, this signet (similar to Signet of Suffering) cannot be used while knocked down or performing an action.
Dwarven Battle Stance #375 | Elite Stance | Prophecies | E5 R20
  For 5..11 seconds, if you are wielding a hammer, you attack 33% faster, you gain +40 armor, and your attack skills interrupt foes when they hit.
  ~ Duration :: 0-4: 5 5 6 6 7 | 5-9: 7 7 8 8 9 | 10-14: 9 9 10 10 11 | 15-19: 11 11 12 12 13 | 20-21: 13 13
  # causes: Increased Attack Speed, Increased Armor Rating, Interrupt
Endure Pain #347 | Skill | Core | E5 R30
  For 7..18 seconds you have an additional 90..300 Health.
  ~ Duration :: 0-4: 7 8 8 9 10 | 5-9: 11 11 12 13 14 | 10-14: 14 15 16 17 17 | 15-19: 18 19 19 20 21 | 20-21: 22 22
  ~ + Maximum health :: 0-4: 90 104 118 132 146 | 5-9: 160 174 188 202 216 | 10-14: 230 244 258 272 286 | 15-19: 300 314 328 342 356 | 20-21: 370 384
  # causes: Increased Maximum Health; target: self
Enraging Charge #1414 | Stance | Nightfall | E5 R20
  For 5..15 seconds, you move 25% faster. Enraging Charge ends when you successfully strike a target, at which point you gain 0..3 strike[s] of adrenaline if you hit with a melee attack.
  ~ Duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  ~ Adrenaline gain :: 0-4: 0 0 0 1 1 | 5-9: 1 1 1 2 2 | 10-14: 2 2 2 3 3 | 15-19: 3 3 3 4 4 | 20-21: 4 4
  # causes: Increased Movement Speed, Adrenaline Gain
Flail (PvP) #3464 | Stance | Nightfall | Ad4
  For 1..15 second[s], you attack 33% faster but move 33% slower. Ends if you use a ranged attack skill.
  ~ Duration :: 0-4: 1 2 3 4 5 | 5-9: 6 7 8 8 9 | 10-14: 10 11 12 13 14 | 15-19: 15 16 17 18 19 | 20-21: 20 21
  # causes: Increased Attack Speed, Decreased Movement Speed
Flourish #389 | Elite Skill | Prophecies | E5 C1 R8
  All of your attack skills become recharged. You gain 2..7 Energy for each skill recharged by Flourish.
  ~ Energy gain :: 0-4: 2 2 3 3 3 | 5-9: 4 4 4 5 5 | 10-14: 5 6 6 6 7 | 15-19: 7 7 8 8 8 | 20-21: 9 9
  # causes: Recharge, Energy Gain
Frenzy (PvP) #3443 | Stance | Core | E5 R4
  For 8 seconds, you attack 33% faster but take 200..150% damage.
  ~ Increased Damage % :: 0-4: 200 197 193 190 187 | 5-9: 183 180 177 173 170 | 10-14: 167 163 160 157 153 | 15-19: 150 147 143 140 137 | 20-21: 133 130
  # causes: Increased Attack Speed
Griffon's Sweep #327 | Melee Attack | Prophecies | E5 R8
  If this attack hits, you strike for +5..20 damage. If this attack is blocked, your target is knocked down and suffers 10..34 damage.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Damage if blocked :: 0-4: 10 12 13 15 16 | 5-9: 18 20 21 23 24 | 10-14: 26 28 29 31 32 | 15-19: 34 36 37 39 40 | 20-21: 42 44
  # causes: Block Punishment, Knockdown; special: Duplicate
Headbutt #1406 | Elite touch skill | Nightfall | E10 C¾ R10
  Elite Skill. Target touched foe takes 40..100 damage. You are Dazed for 10 seconds.
  ~ Damage :: 0-4: 40 44 48 52 56 | 5-9: 60 64 68 72 76 | 10-14: 80 84 88 92 96 | 15-19: 100 104 108 112 116 | 20-21: 120 124
  # causes: Dazed; target: foes; range: touch
Leviathan's Sweep #1134 | Melee Attack | Factions | E5 R8
  If this attack hits, you strike for +5..20 damage. If this attack is blocked, your target is knocked down and suffers 10..34 damage.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Damage if blocked :: 0-4: 10 12 13 15 16 | 5-9: 18 20 21 23 24 | 10-14: 26 28 29 31 32 | 15-19: 34 36 37 39 40 | 20-21: 42 44
  # causes: Block Punishment, Knockdown; special: duplicate
Lion's Comfort #1407 | Skill | Nightfall | Ad4 C1 R1
  All of your signets are disabled for 12 seconds. You are healed for 50..110 Health, and gain 0..3 strike[s] of adrenaline.
  ~ Healing :: 0-4: 50 54 58 62 66 | 5-9: 70 74 78 82 86 | 10-14: 90 94 98 102 106 | 15-19: 110 114 118 122 126 | 20-21: 130 134
  ~ Adrenaline gain :: 0-4: 0 0 0 1 1 | 5-9: 1 1 1 2 2 | 10-14: 2 2 2 3 3 | 15-19: 3 3 3 4 4 | 20-21: 4 4
  # causes: Healing, Adrenaline Gain, Disable
Magehunter Strike #1694 | Elite Melee Attack | Nightfall | E5 C½ R3
  If this attack hits, you strike for +7..25 damage. If your target is under the effects of an enchantment, this attack cannot be blocked.
  ~ + Damage :: 0-4: 7 8 9 11 12 | 5-9: 13 14 15 17 18 | 10-14: 19 20 21 23 24 | 15-19: 25 26 27 29 30 | 20-21: 31 32
  # causes: Unblockable
  ! BUG: Against unenchanted targets this skill causes block bypassing effects such as Asuran Scan or Warrior's Cunning to be ignored.
Power Attack #322 | Melee Attack | Core | E5 R3
  If this attack hits, you strike for +10..40 damage.
  ~ + Damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
Primal Rage (PvP) #3458 | Elite Stance | Factions | E5 R4
  For 1..9 second[s], you attack 33% faster and move 33% faster, but you take 200..150% damage .
  ~ Duration :: 0-4: 1 2 2 3 3 | 5-9: 4 4 5 5 6 | 10-14: 6 7 7 8 8 | 15-19: 9 10 10 11 11 | 20-21: 12 12
  ~ Damage % :: 0-4: 200 197 193 190 187 | 5-9: 183 180 177 173 170 | 10-14: 167 163 160 157 153 | 15-19: 150 147 143 140 137 | 20-21: 133 130
  # causes: Increased Attack Speed, Increased Movement Speed
Protector's Strike (PvP) #3449 | Melee Attack | Prophecies | E5 C½ R6
  If this attack strikes a moving foe, you strike for 10..40 more damage.
  ~ + Damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
Rage of the Ntouka #1408 | Elite Skill | Nightfall | E5 R15
  Gain 1..7 strike[s] of adrenaline. For 8 seconds, whenever you use an adrenal skill, that skill recharges for 3 seconds.
  ~ Adrenaline gain :: 0-4: 1 1 2 2 3 | 5-9: 3 3 4 4 5 | 10-14: 5 5 6 6 7 | 15-19: 7 7 8 8 9 | 20-21: 9 9
  # causes: Adrenaline Gain, Increased Recharge Time
Rush #319 | Stance | Prophecies | Ad4
  For 8..20 seconds, you move 25% faster.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  # causes: Increased Movement Speed
Shield Bash #363 | Skill | Core | E5 R20
  For 5..11 seconds, while wielding a shield, the next melee attack skill used against you is blocked, your attacker is knocked down and that skill is disabled for an additional 15 seconds.
  ~ Duration :: 0-4: 5 5 6 6 7 | 5-9: 7 7 8 8 9 | 10-14: 9 9 10 10 11 | 15-19: 11 11 12 12 13 | 20-21: 13 13
  # causes: Block, Knockdown, Disable
Signet of Stamina #1411 | Signet | Nightfall | C¼ R20
  You have +50..300 maximum Health. This signet ends if you successfully hit with an attack.
  ~ + Max health :: 0-4: 50 67 83 100 117 | 5-9: 133 150 167 183 200 | 10-14: 217 233 250 267 283 | 15-19: 300 317 333 350 367 | 20-21: 383 400
  # causes: Increased Maximum Health; target: self
Signet of Strength #944 | Signet | Factions | C1 R45
  Your next 1..16 attack[s] deal +5 damage.
  ~ Attacks :: 0-4: 1 2 3 4 5 | 5-9: 6 7 8 9 10 | 10-14: 11 12 13 14 15 | 15-19: 16 17 18 19 20 | 20-21: 21 22
Sprint #349 | Stance | Core | E5 R15
  For 8..14 seconds, you move 25% faster.
  ~ Duration :: 0-4: 8 8 9 9 10 | 5-9: 10 10 11 11 12 | 10-14: 12 12 13 13 14 | 15-19: 14 14 15 15 16 | 20-21: 16 16
  # causes: Increased Movement Speed
Tiger Stance #995 | Stance | Factions | E5 R20
  For 4..10 seconds, you attack 33% faster. Tiger Stance ends if any of your attacks fail to hit.
  ~ Duration :: 0-4: 4 4 5 5 6 | 5-9: 6 6 7 7 8 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 12
  # causes: Increased Attack Speed
Warrior's Cunning #362 | Skill | Core | E10 R60
  For 5..11 seconds, your melee attacks cannot be blocked.
  ~ Duration :: 0-4: 5 5 6 6 7 | 5-9: 7 7 8 8 9 | 10-14: 9 9 10 10 11 | 15-19: 11 11 12 12 13 | 20-21: 13 13
  # causes: Unblockable
Warrior's Endurance (PvP) #3002 | Elite Stance | Prophecies | E5 R30
  For 5..35 seconds, you gain 3 Energy each time you hit with a melee attack. Warrior's Endurance cannot raise your Energy above 10..25.
  ~ Duration :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  ~ Energy ceiling :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  # causes: Energy Gain

### Warrior / Swordsmanship
Barbarous Slice #1416 | Sword Attack | Nightfall | Ad6
  If this attack hits, you deal +5..30 damage. If you are currently not in a stance, you also inflict Bleeding for 5..15 seconds.
  ~ + Damage :: 0-4: 5 7 8 10 12 | 5-9: 13 15 17 18 20 | 10-14: 22 23 25 27 28 | 15-19: 30 32 33 35 37 | 20-21: 38 40
  ~ Bleeding duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Bleeding; requires: Stance
Crippling Slash #1415 | Elite Sword Attack | Nightfall | Ad5
  If this attack hits, target foe is Crippled for 5..15 seconds and begins Bleeding for 10..25 seconds.
  ~ Crippled duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  ~ Bleeding duration :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  # causes: Crippled, Bleeding
Dragon Slash #907 | Elite Sword Attack | Factions | Ad7
  If Dragon Slash hits, you strike for +10..40 damage and gain 1..5 strike[s] of adrenaline.
  ~ + Damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  ~ Adrenaline gain :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
Final Thrust #385 | Sword Attack | Core | Ad8
  Lose all adrenaline. If Final Thrust hits, you deal 5..40 more damage. This damage is doubled if your target was below 50% Health.
  ~ + Damage :: 0-4: 5 7 10 12 14 | 5-9: 17 19 21 24 26 | 10-14: 28 31 33 35 38 | 15-19: 40 42 45 47 49 | 20-21: 52 54
  ~ Additional damage :: 0-4: 5 7 10 12 14 | 5-9: 17 19 21 24 26 | 10-14: 28 31 33 35 38 | 15-19: 40 42 45 47 49 | 20-21: 52 54
  # causes: Adrenaline Loss
Galrath Slash #383 | Sword Attack | Prophecies | Ad7
  This attack strikes for +1..40 damage if it hits.
  ~ + Damage :: 0-4: 1 4 6 9 11 | 5-9: 14 17 19 22 24 | 10-14: 27 30 32 35 37 | 15-19: 40 43 45 48 50 | 20-21: 53 56
  # special: Duplicate
Gash #384 | Sword Attack | Core | Ad5
  If this attack hits a Bleeding foe, you strike for 5..20 more damage and that foe suffers a Deep Wound, lowering that foe's maximum Health by 20% for 5..20 seconds.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Deep Wound duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Deep Wound
Hamstring #320 | Sword Attack | Core | E5 R10
  If this attack hits, your target is Crippled for 3..15 seconds, slowing his movement.
  ~ Crippled duration :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Crippled
Hundred Blades (PvP) #3444 | Elite Skill | Core | E5 R20
  For 15 seconds, whenever you attack with a sword, all adjacent foes take 10..30 slashing damage.
  ~ Slashing damage :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  # causes: Slashing Damage; requires: Sword; target: untargeted; aoe: adjacent
Jaizhenju Strike #1135 | Sword Attack | Factions | E5 R8
  If Jaizhenju Strike hits, you strike for +1..30 damage. If you are not using a stance, Jaizhenju Strike cannot be blocked.
  ~ + Damage :: 0-4: 1 3 5 7 9 | 5-9: 11 13 15 16 18 | 10-14: 20 22 24 26 28 | 15-19: 30 32 34 36 38 | 20-21: 40 42
  # causes: Unblockable; special: duplicate
Knee Cutter #2010 | Sword Attack | Eye of the North | Ad5 R1
  If this attack hits a Crippled foe, you gain 2..7 Energy and 1..3 strikes of adrenaline.
  ~ Energy gain :: 0-4: 2 2 3 3 3 | 5-9: 4 4 4 5 5 | 10-14: 5 6 6 6 7 | 15-19: 7 7 8 8 8 | 20-21: 9 9
  ~ Adrenaline gain :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Energy Gain, Adrenaline Gain
Pure Strike #328 | Sword Attack | Prophecies | E5 R8
  If Pure Strike hits, you strike for +1..30 damage. If you are not using a stance, Pure Strike cannot be blocked.
  ~ + Damage :: 0-4: 1 3 5 7 9 | 5-9: 11 13 15 16 18 | 10-14: 20 22 24 26 28 | 15-19: 30 32 34 36 38 | 20-21: 40 42
  # causes: Unblockable; special: duplicate
Quivering Blade #892 | Elite Sword Attack | Factions | Ad4
  If Quivering Blade hits, you strike for +10..40 damage. If this attack hits a moving foe, that foe is Dazed for 10 seconds.
  ~ + Damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Dazed
Savage Slash #390 | Sword Attack | Core | E5 C½ R10
  If this attack hits, it interrupts target foe's action. If that action was a spell, you deal 1..40 extra damage.
  ~ + Damage :: 0-4: 1 4 6 9 11 | 5-9: 14 17 19 22 24 | 10-14: 27 30 32 35 37 | 15-19: 40 43 45 48 50 | 20-21: 53 56
  # causes: Interrupt
Seeking Blade #386 | Sword Attack | Core | E5 R4
  If this attack hits you strike for +1..20 damage. If Seeking Blade is blocked, your target begins Bleeding for 25 seconds and takes 1..20 damage.
  ~ + Damage :: 0-4: 1 2 4 5 6 | 5-9: 7 9 10 11 12 | 10-14: 14 15 16 17 19 | 15-19: 20 21 23 24 25 | 20-21: 26 28
  ~ Damage if blocked :: 0-4: 1 2 4 5 6 | 5-9: 7 9 10 11 12 | 10-14: 14 15 16 17 19 | 15-19: 20 21 23 24 25 | 20-21: 26 28
  # causes: Bleeding, Block Punishment; requires: Block
Sever Artery #382 | Sword Attack | Core | Ad3
  If this attack hits, the opponent begins Bleeding for 5..25 seconds, losing Health over time.
  ~ Bleeding duration :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  # causes: Bleeding
Silverwing Slash #1144 | Sword Attack | Factions | Ad7
  This attack strikes for +1..40 damage if it hits.
  ~ + Damage :: 0-4: 1 4 6 9 11 | 5-9: 14 17 19 22 24 | 10-14: 27 30 32 35 37 | 15-19: 40 43 45 48 50 | 20-21: 53 56
  # special: duplicate
Standing Slash #996 | Sword Attack | Factions | Ad6
  If it hits, Standing Slash deals +5..20 damage plus an additional 5..20 damage if you are in a stance.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
Steelfang Slash #1702 | Sword Attack | Nightfall | Ad7 R1
  If this attack hits, you deal +1..31 damage. If you hit a foe that is knocked down, you gain 1..5 adrenaline.
  ~ + Damage :: 0-4: 1 3 5 7 9 | 5-9: 11 13 15 17 19 | 10-14: 21 23 25 27 29 | 15-19: 31 33 35 37 39 | 20-21: 41 43
  ~ Adrenaline gain :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Adrenaline Gain
Sun and Moon Slash #851 | Sword Attack | Factions | Ad8
  Attack target foe twice. These attacks cannot be blocked.
  # causes: Unblockable

### Warrior / Tactics
"Charge!" #364 | Elite Shout | Core | E5 R20
  Allies in earshot lose the Crippled condition. For 5..13 seconds, these allies move 33% faster.
  ~ Duration :: 0-4: 5 6 6 7 7 | 5-9: 8 8 9 9 10 | 10-14: 10 11 11 12 12 | 15-19: 13 14 14 15 15 | 20-21: 16 16
  # causes: Increased Movement Speed; removes: Condition; aoe: earshot
"Fear Me!" #366 | Shout | Prophecies | Ad4 R4
  All nearby foes lose 2..6 Energy. For 1..15 second[s], your melee attacks gain +5..30% chance of a critical hit against stationary foes.
  ~ Energy loss :: 0-4: 2 2 3 3 3 | 5-9: 3 4 4 4 4 | 10-14: 5 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 7 8
  ~ Duration :: 0-4: 1 2 3 4 5 | 5-9: 6 7 8 8 9 | 10-14: 10 11 12 13 14 | 15-19: 15 16 17 18 19 | 20-21: 20 21
  ~ + Critical % chance :: 0-4: 5 7 8 10 12 | 5-9: 13 15 17 18 20 | 10-14: 22 23 25 27 28 | 15-19: 30 32 33 35 37 | 20-21: 38 40
  # causes: Energy Loss, Critical Hit; aoe: nearby
"None Shall Pass!" #891 | Shout | Factions | E5 R45
  All nearby foes that are moving are knocked down. This skill recharges 1..8 second[s] faster for each foe knocked down (maximum 25 seconds).
  ~ Faster recharge per foe :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  # causes: Knockdown, Decreased Recharge Time; aoe: nearby
  ! BUG: 1=Because the recharge reduction of "None Shall Pass!" is applied after percentile reductions such as Quickening Zephyr, the recharge can be reduced below 0. The skill will display as 'recharging' indefinitely but actually can be used again after 10 minutes and 55 seconds, which indicates that Guild Wars uses an unsigned 16 bit integer to store the recharge time in hundredths of a second (216−1 cs = 65,535 cs = 10min 55.35s).
"Retreat!" #839 | Shout | Factions | E5 R20
  If there are any dead allies within earshot, your party moves 33% faster for 5..11 seconds.
  ~ Duration :: 0-4: 5 5 6 6 7 | 5-9: 7 7 8 8 9 | 10-14: 9 9 10 10 11 | 15-19: 11 11 12 12 13 | 20-21: 13 13
  # causes: Increased Movement Speed; target: untargeted; aoe: earshot
  ! ANOMALY: Only the dead ally needs to be within earshot. The buff will apply to all party members within compass range.
  ! BUG: This skill works with any dead minion, despite not leaving a corpse. This is unlike "I Will Avenge You!".
"Shields Up!" #367 | Shout | Core | E10 R30
  For 5..11 seconds, you and all party members within earshot gain +60 armor against incoming projectile attacks.
  ~ Duration :: 0-4: 5 5 6 6 7 | 5-9: 7 7 8 8 9 | 10-14: 9 9 10 10 11 | 15-19: 11 11 12 12 13 | 20-21: 13 13
  # causes: Increased Armor Rating
"To the Limit!" #316 | Shout | Prophecies | E5 R10
  For each foe within earshot (maximum 1..6), you gain one strike of adrenaline. For 10..20 seconds, your maximum Health is increased by 10..60.
  ~ Max foes :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  ~ Duration :: 0-4: 10 11 11 12 13 | 5-9: 13 14 15 15 16 | 10-14: 17 17 18 19 19 | 15-19: 20 21 21 22 23 | 20-21: 23 24
  ~ + Max health :: 0-4: 10 13 17 20 23 | 5-9: 27 30 33 37 40 | 10-14: 43 47 50 53 57 | 15-19: 60 63 67 70 73 | 20-21: 77 80
  # causes: Adrenaline Gain, Increased Maximum Health; target: self
"Victory Is Mine!" #365 | Elite Shout | Prophecies | E5 R10
  You gain 10..68 Health and 3..7 Energy for each condition suffered by target foe.
  ~ Health gain :: 0-4: 10 14 18 22 25 | 5-9: 29 33 37 41 45 | 10-14: 49 53 56 60 64 | 15-19: 68 72 76 80 83 | 20-21: 87 91
  ~ Energy gain :: 0-4: 3 3 4 4 4 | 5-9: 4 5 5 5 5 | 10-14: 6 6 6 6 7 | 15-19: 7 7 8 8 8 | 20-21: 8 9
  # causes: Health Gain, Energy Gain; target: foes; aoe: None
"Watch Yourself!" (PvP) #2858 | Shout | Core | Ad4 R4
  Party members within earshot gain +5..25 armor for 10 seconds. This shout ends after 1..3 incoming attack[s].
  ~ + Armor rating :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  ~ Attacks :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Increased Armor Rating
  ! ANOMALY: Instead of ending on attacks as stated, it ends after an ally takes armor-respecting damage 1..3 times.
  ! ANOMALY: Instead of ending on attacks as stated, it ends after an ally takes armor-respecting damage 10 times. [from PvE version page]
Auspicious Parry #1142 | Elite Stance | Factions | Ad1 R2
  For 8 seconds, the next attack against you is blocked. You gain 1..4 strike[s] of adrenaline when this stance ends.
  ~ Adrenaline gain :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  # causes: Block, Adrenaline Gain
Balanced Stance #371 | Stance | Core | E5 R30
  For 8..20 seconds, you cannot be knocked down and you do not suffer extra damage from a critical attack.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  # causes: Knockdown Immunity
Bonetti's Defense #380 | Stance | Prophecies | Ad8
  For 5..11 seconds, you have a 75% chance to block melee and projectile attacks. You gain 5 Energy for each successful melee attack blocked. Bonetti's Defense ends if you use a skill.
  ~ Duration :: 0-4: 5 5 6 6 7 | 5-9: 7 7 8 8 9 | 10-14: 9 9 10 10 11 | 15-19: 11 11 12 12 13 | 20-21: 13 13
  # causes: Block, Energy Gain
Deadly Riposte #388 | Skill | Prophecies | E5 R10
  For 8 seconds, while you have a sword equipped, you block the next melee attack against you, and your attacker is struck for 15..90 damage and begins Bleeding for 3..25 seconds.
  ~ Damage :: 0-4: 15 20 25 30 35 | 5-9: 40 45 50 55 60 | 10-14: 65 70 75 80 85 | 15-19: 90 95 100 105 110 | 20-21: 115 120
  ~ Bleeding :: 0-4: 3 4 6 7 9 | 5-9: 10 12 13 15 16 | 10-14: 18 19 21 22 24 | 15-19: 25 26 28 29 31 | 20-21: 32 34
  # causes: Bleeding, Block; requires: Sword
Defensive Stance #345 | Stance | Core | Ad5 R8
  For 1..5 second[s], you have a 75% chance to block melee and projectile attacks. When Defensive Stance ends, you gain one strike of adrenaline for each melee attack skill you have (maximum 0..4).
  ~ Duration :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  ~ Maximum adrenaline gain :: 0-4: 0 0 1 1 1 | 5-9: 1 2 2 2 2 | 10-14: 3 3 3 3 4 | 15-19: 4 4 5 5 5 | 20-21: 5 6
  # causes: Block, Adrenaline Gain
Deflect Arrows #373 | Stance | Prophecies | Ad5 R12
  For 1..6 second[s], you have a 75% chance to block attacks. If you block a projectile attack, adjacent foes suffer from Bleeding for 5..15 seconds.
  ~ Duration :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  ~ Bleeding duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Bleeding, Block; requires: Projectile Attack; aoe: adjacent
Desperation Blow #323 | Melee Attack | Prophecies | E5 R7
  If this attack hits, you strike for +10..40 damage, and your target suffers from one of the following conditions: Deep Wound (for 20 seconds), Weakness (for 20 seconds), Bleeding (for 25 seconds), or Crippled (for 15 seconds). After making a Desperation Blow, you are knocked down.
  ~ + Damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Deep Wound, Weakness, Bleeding, Crippled, Knockdown; special: Duplicate
Disciplined Stance #376 | Stance | Prophecies | E5 R15
  For 1..4 second[s], you gain +10 armor and have a 75% chance to block attacks. Disciplined Stance ends if you use an adrenal skill.
  ~ Duration :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  # causes: Increased Armor Rating, Block
Drunken Blow #1133 | Melee Attack | Factions | E5 R7
  If this attack hits, you strike for +10..40 damage and your target suffers from one of the following conditions: Deep Wound (for 20 seconds), Weakness (for 20 seconds), Bleeding (for 25 seconds), or Crippled (for 15 seconds). After making a Drunken Blow, you are knocked down.
  ~ + Damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Deep Wound, Weakness, Bleeding, Crippled, Knockdown; special: Duplicate
Gladiator's Defense #372 | Elite Stance | Prophecies | E5 R20
  For 5..11 seconds, you have a 75% chance to block incoming attacks. Whenever you block a melee attack this way, the attacker suffers 5..35 damage.
  ~ Duration :: 0-4: 5 5 6 6 7 | 5-9: 7 7 8 8 9 | 10-14: 9 9 10 10 11 | 15-19: 11 11 12 12 13 | 20-21: 13 13
  ~ Armor-ignoring damage :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  # causes: Block
Healing Signet #1 | Signet | Core | C2 R4
  You gain 82..172 Health. You have -40 armor while using this skill.
  ~ Healing :: 0-4: 82 88 94 100 106 | 5-9: 112 118 124 130 136 | 10-14: 142 148 154 160 166 | 15-19: 172 178 184 190 196 | 20-21: 202 208
  # causes: Healing, Decreased Armor Rating
  ! ANOMALY: The armor penalty from this skill is applied after the armor cap and the effects of Cracked Armor and armor penetration.
  ! BUG: Contrary to the descriptions, this skill causes healing and not health gain.
Protector's Defense (PvP) #3457 | Skill | Factions | E5 R30
  For 4..8 seconds, allies adjacent to you have a 75% chance to block incoming attacks. Protector's Defense ends if you move.
  ~ Duration :: 0-4: 4 4 5 5 5 | 5-9: 5 6 6 6 6 | 10-14: 7 7 7 7 8 | 15-19: 8 8 9 9 9 | 20-21: 9 10
  # causes: Block; aoe: adjacent
  ! ANOMALY: The user is affected.
  ! ANOMALY: Although it has no activation time, it acts like it has one (gets queued, pauses the user, cannot be used while knocked down, etc).
  ! ANOMALY: The user is affected. [from PvE version page]
  ! ANOMALY: Although it has no activation time, it acts like it has one (gets queued, pauses the user, cannot be used while knocked down, etc). [from PvE version page]
Riposte #387 | Skill | Prophecies | Ad4
  For 8 seconds, while you have a sword equipped, you block the next melee attack against you and your attacker is struck for 20..80 damage.
  ~ Damage :: 0-4: 20 24 28 32 36 | 5-9: 40 44 48 52 56 | 10-14: 60 64 68 72 76 | 15-19: 80 84 88 92 96 | 20-21: 100 104
  # causes: Block
Shield Stance #378 | Stance | Prophecies | E5 R15
  For 1..6 second[s], while wielding a shield, you have a 75% chance to block incoming attacks, and damage is reduced by 2 for each rank of Strength (maximum 15 damage reduction).
  ~ Duration :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  # causes: Block, Damage Reduction
Shove #1146 | Elite Touch skill | Factions | E5 C¾ R10
  Elite Skill. Target touched foe takes 15..75 damage, their stance ends, and they are knocked down.
  ~ Damage :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  # causes: Knockdown; removes: Stance; target: foes; range: touch
  ! ANOMALY: This skill has no aftercast delay.
Soldier's Defense #1699 | Stance | Nightfall | E5 R15
  For 1..6 second[s], you have a 75% chance to block attacks while under the effects of a shout or chant. You gain 1 strike of adrenaline for each blocked attack.
  ~ Duration :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  # causes: Block, Adrenaline Gain
  ! ANOMALY: Adrenaline will be gained even for attacks blocked by another blocking source (regardless of whether the user is under the effects of a shout or chant).
Soldier's Speed #2196 | Stance | Eye of the North | E5 R12
  For 3..18 seconds, you move 15% faster. You move an additional 15% faster while under the effects of a chant or shout.
  ~ Duration :: 0-4: 3 4 5 6 7 | 5-9: 8 9 10 11 12 | 10-14: 13 14 15 16 17 | 15-19: 18 19 20 21 22 | 20-21: 23 24
  # causes: Increased Movement Speed
Soldier's Stance (PvP) #3156 | Elite Stance | Nightfall | E5 R8
  For 4..10 seconds, you attack 33% faster while under the effects of a shout or chant.
  ~ Duration :: 0-4: 4 4 5 5 6 | 5-9: 6 6 7 7 8 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 12
  # causes: Increased Attack Speed
Soldier's Strike #1695 | Melee Attack | Nightfall | E5 R4
  If this attack hits, you deal +10..40 more damage. If you are under the effects of a chant or shout, this attack cannot be blocked.
  ~ + Damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Unblockable
Steady Stance #1701 | Elite Stance | Nightfall | E5 R4
  For 10 seconds, the next time you would be knocked down, you gain 1..4 strike[s] of adrenaline and 1..7 Energy instead.
  ~ Adrenaline gain :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  ~ Energy gain :: 0-4: 1 1 2 2 3 | 5-9: 3 3 4 4 5 | 10-14: 5 5 6 6 7 | 15-19: 7 7 8 8 9 | 20-21: 9 9
  # causes: Knockdown Immunity, Adrenaline Gain, Energy Gain
Thrill of Victory #324 | Melee Attack | Core | E5 R8
  If this blow hits, you deal +20..40 damage. If you have more Health than target foe, you gain 1..2 strike[s] of adrenaline.
  ~ + Damage :: 0-4: 20 21 23 24 25 | 5-9: 27 28 29 31 32 | 10-14: 33 35 36 37 39 | 15-19: 40 41 43 44 45 | 20-21: 47 48
  ~ Adrenaline gain :: 0-4: 1 1 1 1 1 | 5-9: 1 1 1 2 2 | 10-14: 2 2 2 2 2 | 15-19: 2 2 2 2 2 | 20-21: 2 2
  # causes: Adrenaline Gain
Wary Stance #377 | Stance | Prophecies | E10 R10
  For 1..6 second[s], you block any attack skills used against you. For each successful block, you gain adrenaline and 5 Energy. Wary Stance ends if you use a skill.
  ~ Duration :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  # causes: Block, Adrenaline Gain, Energy Gain

## Ranger

### Ranger / Beast Mastery
Bestial Fury #1209 | Stance | Factions | E10 R10
  All your non-attack skills are disabled for 5 seconds. For 5..11 seconds, you attack 25% faster.
  ~ Duration :: 0-4: 5 5 6 6 7 | 5-9: 7 7 8 8 9 | 10-14: 9 9 10 10 11 | 15-19: 11 11 12 12 13 | 20-21: 13 13
  # causes: Disable, Increased Attack Speed; special: duplicate
Bestial Mauling #1203 | Pet Attack | Factions | E5 R10
  Your animal companion attempts a Bestial Mauling that deals +5..20 damage. If the attack strikes a knocked-down foe, that foe is Dazed for 4..10 seconds.
  ~ Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Dazed duration :: 0-4: 4 4 5 5 6 | 5-9: 6 6 7 7 8 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 12
  # causes: Dazed
Bestial Pounce #437 | Pet Attack | Prophecies | E5 R10
  Your animal companion attempts a Bestial Pounce that deals +5..20 damage. If the attack strikes a foe who is casting a spell, that foe is knocked down.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Knockdown; special: duplicate
Brutal Strike #444 | Pet Attack | Prophecies | E10 R5
  Your animal companion attempts a Brutal Strike that deals +5..35 damage. If that attack strikes a foe whose Health is below 50%, that foe takes an additional +5..35 damage.
  ~ + Damage :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
Call of Haste (PvP) #2657 | Shout | Core | E10 R25
  For 30 seconds, your animal companion has a 25% faster attack speed and moves 25% faster.
  # causes: Increased Movement Speed, Increased Attack Speed; aoe: None
Call of Protection #412 | Shout | Prophecies | E5 R90
  For 120 seconds, your animal companion has a 5..20 base damage reduction.
  ~ Damage reduction :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Damage Reduction; aoe: None
Charm Animal #411 | Skill | Core | E10 C10
  Charm target animal. Once charmed, your animal companion will travel with you whenever you have Charm Animal equipped. You cannot charm an animal that is more than 4 levels above you.
  # target: animals; range: Casting
  ! ANOMALY: Although technically considered a pet, occasionally a charmed animal will retain the red wording associated with a hostile enemy just after completing the charm animal skill.
Comfort Animal (PvP) #3045 | Skill | Core | E10 C1 R1
  You heal your animal companion for 40..120 Health. If your companion is dead, it is resurrected with 10..58% Health. If you have Comfort Animal equipped, your animal companion will travel with you.
  ~ Healing :: 0-4: 40 45 51 56 61 | 5-9: 67 72 77 83 88 | 10-14: 93 99 104 109 115 | 15-19: 120 125 131 136 141 | 20-21: 147 152
  ~ Health % :: 0-4: 10 13 16 20 23 | 5-9: 26 29 32 36 39 | 10-14: 42 45 48 52 55 | 15-19: 58 61 64 68 71 | 20-21: 74 77
  # causes: Healing
  ! ANOMALY: If this skill is cast at the exact moment of your pet's death, the pet will be resurrected without any of your skills being disabled. [from PvE version page]
  ! ANOMALY: Using this skill without a pet will still use the energy and return the message "Your pet is out of range." [from PvE version page]
  ! ANOMALY: This skill bypasses the effects of Frozen Soil [from PvE version page]
Companionship #2141 | Skill | Eye of the North | E5 C2 R10
  If you have less Health than your pet, you are healed for 30..120 Health. If your pet has less Health than you, it is healed for 30..120 Health.
  ~ Healing :: 0-4: 30 36 42 48 54 | 5-9: 60 66 72 78 84 | 10-14: 90 96 102 108 114 | 15-19: 120 126 132 138 144 | 20-21: 150 156
  # causes: Healing; target: self
Disrupting Lunge #445 | Pet Attack | Core | E5 R10
  Your animal companion attempts a Disrupting Lunge that deals +1..12 damage. If that attack strikes a foe using a skill that skill is interrupted and is disabled for an additional 20 seconds.
  ~ + Damage :: 0-4: 1 2 2 3 4 | 5-9: 5 5 6 7 8 | 10-14: 8 9 10 11 11 | 15-19: 12 13 13 14 15 | 20-21: 16 16
  # causes: Interrupt, Disable
Edge of Extinction #464 | Nature Ritual | Prophecies | E5 C2 R60
  Create a level 1..10 spirit. If a non-spirit creature within range dies, Edge of Extinction deals 14..50 damage to all creatures of the same type that are below 90% Health and within range of the spirit. This spirit dies after 30..240 seconds.
  ~ Spirit level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Damage :: 0-4: 14 16 19 21 24 | 5-9: 26 28 31 33 36 | 10-14: 38 40 43 45 48 | 15-19: 50 52 55 57 60 | 20-21: 62 64
  ~ Duration :: 0-4: 30 44 58 72 86 | 5-9: 100 114 128 142 156 | 10-14: 170 184 198 212 226 | 15-19: 240 254 268 282 296 | 20-21: 310 324
  # causes: Spirit; aoe: large spirit
Energizing Wind #474 | Nature Ritual | Core | E15 C2 R60
  Create a level 1..6 spirit. For non-spirit creatures within its range, all skills cost 15 less Energy (minimum cost 10 Energy), and skills recharge 25% slower. This spirit dies after 1..60 second[s].
  ~ Level :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  ~ Duration :: 0-4: 1 5 9 13 17 | 5-9: 21 25 29 32 36 | 10-14: 40 44 48 52 56 | 15-19: 60 64 68 72 76 | 20-21: 80 84
  # causes: Spirit, Decreased Energy Cost, Increased Recharge Time; aoe: large spirit
Enraged Lunge (PvP) #3051 | Elite Pet Attack | Factions | E5 R5
  Your animal companion attempts an Enraged Lunge that deals +3..23 damage (maximum bonus 60) for each recharging Beast Mastery skill.
  ~ + Damage :: 0-4: 3 4 6 7 8 | 5-9: 10 11 12 14 15 | 10-14: 16 18 19 20 22 | 15-19: 23 24 26 27 28 | 20-21: 30 31
Feral Aggression #2142 | Skill | Eye of the North | E15 R20
  For 5..20 seconds, your pet attacks 33% faster and deals +3..10 additional damage.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ + Damage :: 0-4: 3 3 4 4 5 | 5-9: 5 6 6 7 7 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 13
  # causes: Increased Attack Speed
  ! ANOMALY: Cannot be used while activating another skill.
Feral Lunge #439 | Pet Attack | Prophecies | E5 R10
  Your animal companion attempts a Feral Lunge that deals +5..35 damage. If the attack strikes a foe who is attacking, that foe suffers from Bleeding for 5..25 seconds.
  ~ +Damage :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  ~ Bleeding :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  # causes: Bleeding
Ferocious Strike #442 | Elite Pet Attack | Core | E5 R8
  Your animal companion attempts a Ferocious Strike that deals +13..28 damage. If that attack hits, you gain adrenaline and 3..10 Energy.
  ~ + Damage :: 0-4: 13 14 15 16 17 | 5-9: 18 19 20 21 22 | 10-14: 23 24 25 26 27 | 15-19: 28 29 30 31 32 | 20-21: 33 34
  ~ Energy gain :: 0-4: 3 3 4 4 5 | 5-9: 5 6 6 7 7 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 13
  # causes: Adrenaline Gain, Energy Gain
Fertile Season #467 | Nature Ritual | Prophecies | E15 C2 R60
  Create a level 1..10 spirit. Non-spirit creatures within range have +50..150 maximum Health and gain +8 armor. This spirit dies after 15..90 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ + Max health :: 0-4: 50 57 63 70 77 | 5-9: 83 90 97 103 110 | 10-14: 117 123 130 137 143 | 15-19: 150 157 163 170 177 | 20-21: 183 190
  ~ Duration :: 0-4: 15 20 25 30 35 | 5-9: 40 45 50 55 60 | 10-14: 65 70 75 80 85 | 15-19: 90 95 100 105 110 | 20-21: 115 120
  # causes: Spirit, Increased Maximum Health, Increased Armor Rating; aoe: large spirit
Heal as One (PvP) #3144 | Elite Skill | Factions | E5 C1 R8
  If you or your animal companion are below 75% Health, you are both healed for 25..145 Health. If your companion is dead, it is resurrected with 50% Health.
  ~ Healing :: 0-4: 25 33 41 49 57 | 5-9: 65 73 81 89 97 | 10-14: 105 113 121 129 137 | 15-19: 145 153 161 169 177 | 20-21: 185 193
  # causes: Healing; special: Resurrection
Heket's Rampage #1728 | Stance | Nightfall | E5 R10
  For 5..11 seconds, you attack 33% faster. This stance ends if you use an attack skill.
  ~ Duration :: 0-4: 5 5 6 6 7 | 5-9: 7 7 8 8 9 | 10-14: 9 9 10 10 11 | 15-19: 11 11 12 12 13 | 20-21: 13 13
  # causes: Increased Attack Speed
Lacerate #961 | Elite Nature Ritual | Factions | E10 C2 R15
  Create a level 1..10 spirit. Bleeding creatures within its range suffer -2 Health degeneration. When this spirit dies, all non-spirit creatures within its range that have less than 90% Health begin Bleeding for 5..25 seconds. This spirit dies after 30..240 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Bleeding duration :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  ~ Duration :: 0-4: 30 44 58 72 86 | 5-9: 100 114 128 142 156 | 10-14: 170 184 198 212 226 | 15-19: 240 254 268 282 296 | 20-21: 310 324
  # causes: Spirit, Health Degeneration, Bleeding; aoe: spirit
Maiming Strike #438 | Pet Attack | Core | E10 R5
  Your animal companion attempts a Maiming Strike that deals +5..20 damage. If that attack hits that foe becomes Crippled for 3..15 seconds.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Crippled duration :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Crippled
Melandru's Assault (PvP) #3047 | Pet Attack | Prophecies | E10 R5
  Your animal companion attempts a Melandru's Assault that deals +5..20 damage. If that attack strikes a foe with an enchantment, that foe and all adjacent foes take +5..35 additional damage.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ + Damage (enchanted foe) :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  # aoe: adjacent
  ! BUG: The pet does not actually attack nearby foes when this skill is used, but instead deals a flat 5...20 damage to target and nearby foes in a separate packet. *The damage to nearby foes is not increased by Feral Aggression, "Together as One!" or Ebon Battle Standard of Honor. Heal as One does not cause extra life steal and Predatory Bond does not heal for each affected foe. [from PvE version page]
Otyugh's Cry (PvP) #3451 | Shout | Prophecies | E5 R30
  For 5..15 seconds, your animal companion gains +24 armor and cannot be blocked.
  ~ Duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Increased Armor Rating, Unblockable; aoe: None
Poisonous Bite #1205 | Pet Attack | Factions | E5 R7
  Your animal companion attempts a Poisonous Bite that Poisons target foe for 5..20 seconds.
  ~ Poison duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Poison
Pounce #1206 | Pet Attack | Factions | E5 R10
  Your animal companion's next attack is a Pounce that deals +5..20 damage. If the attack strikes a moving foe, that foe is knocked down.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Knockdown
Predator's Pounce #443 | Pet Attack | Prophecies | E5 R5
  Your animal companion attempts a Predator's Pounce that deals +5..35 damage. If that attack hits, your animal companion gains 5..50 Health.
  ~ + Damage :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  ~ Health gain :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Health Gain
Predatory Bond (PvP) #3050 | Shout | Factions | E10 R30
  For 5..20 seconds, attacks by your animal companion heal you for 1..31 Health.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Healing :: 0-4: 1 3 5 7 9 | 5-9: 11 13 15 17 19 | 10-14: 21 23 25 27 29 | 15-19: 31 33 35 37 39 | 20-21: 41 43
  # causes: Healing; aoe: None
  ! BUG: Contrary to the descriptions, this skill causes healing and not health gain.
  ! BUG: Contrary to the descriptions, this skill causes healing and not health gain. [from PvE version page]
Predatory Season #470 | Nature Ritual | Prophecies | E5 C2 R60
  Create a level 1..10 spirit. For non-spirit creatures within its range, all healing is reduced by 20%. If any of your attacks hit, you gain 5 Health. This spirit dies after 30..240 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Duration :: 0-4: 30 44 58 72 86 | 5-9: 100 114 128 142 156 | 10-14: 170 184 198 212 226 | 15-19: 240 254 268 282 296 | 20-21: 310 324
  # causes: Spirit, Health Gain; aoe: large spirit
Primal Echoes #469 | Nature Ritual | Core | E5 C2 R60
  Create a level 1..10 Spirit. For non-Spirit creatures within its range, Signets cost 10 Energy to use. This Spirit dies after 30..240 seconds.
  ~ Spirit level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Spirit duration :: 0-4: 30 44 58 72 86 | 5-9: 100 114 128 142 156 | 10-14: 170 184 198 212 226 | 15-19: 240 254 268 282 296 | 20-21: 310 324
  # causes: Spirit, Increased Energy Cost; aoe: large spirit
Rampage as One #1721 | Elite Skill | Nightfall | E25 R10
  For 3..15 seconds, both you and your animal companion attack 33% faster and run 25% faster.
  ~ Duration :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Increased Movement Speed, Increased Attack Speed
  ! BUG: The full description omits that this skill needs your pet to be alive to activate.
Revive Animal #422 | Skill | Prophecies | E5 C¼ R5
  Resurrect all nearby allied animal companions. They come back to life with 10..94% Health.
  ~ % Health :: 0-4: 10 16 21 27 32 | 5-9: 38 44 49 55 60 | 10-14: 66 72 77 83 88 | 15-19: 94 100 105 111 116 | 20-21: 122 128
  # target: self; aoe: nearby
Run as One #811 | Stance | Factions | E5 R15
  For 5..15 seconds, you and your pet run 25% faster.
  ~ Duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Increased Movement Speed
Savage Pounce #1201 | Pet Attack | Factions | E5 R10
  Your animal companion attempts a Savage Pounce that deals +5..20 damage. If the attack strikes a foe who is casting a spell, that foe is knocked down.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Knockdown; special: duplicate
Scavenger Strike #440 | Pet Attack | Core | E5 R10
  Your animal companion attempts a Scavenger Strike that deals +10..25 damage. If the attack strikes a foe who is suffering a condition, you gain 3..15 Energy.
  ~ +Damage :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  ~ Energy gained :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Energy Gain
Strike as One #1468 | Elite Shout | Nightfall | E5 R10
  Your animal companion instantly moves to your target and causes Bleeding for 5..15 seconds with its next attack. The next time you hit with an attack, target foe is Crippled for 5..15 seconds.
  ~ Bleeding duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  ~ Crippled duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Crippled, Bleeding, Shadow Step; target: allies or foes; range: casting; aoe: None
  ! BUG: Targeting yourself or an ally will sometimes cause your pet to stop moving. It will unfreeze when an opponent enters your aggro bubble or attacks it. This is exploited to perform the portal jumping technique known as a SaO chain.
  ! ANOMALY: Strike as One's description omits the fact that it has a limited duration of 30 seconds.
  ! ANOMALY: The French description of the skill mention an "enemy target" for the shadow step despite the fact that the skill can target either foe or friend
Symbiosis #468 | Nature Ritual | Prophecies | E5 C2 R60
  Create a level 1..10 spirit. For each enchantment on a non-spirit creature within range, that creature has +27..150 maximum Health. This spirit dies after 30..240 seconds.
  ~ Spirit level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ + Max health :: 0-4: 27 35 43 52 60 | 5-9: 68 76 84 93 101 | 10-14: 109 117 125 134 142 | 15-19: 150 158 166 175 183 | 20-21: 191 199
  ~ Spirit duration :: 0-4: 30 44 58 72 86 | 5-9: 100 114 128 142 156 | 10-14: 170 184 198 212 226 | 15-19: 240 254 268 282 296 | 20-21: 310 324
  # causes: Spirit, Increased Maximum Health; aoe: large spirit
Symbiotic Bond #423 | Shout | Prophecies | E10 R55
  For 120..300 seconds, your animal companion gains 1..3 Health regeneration, and half of all damage dealt to your animal companion is redirected to you.
  ~ Duration :: 0-4: 120 132 144 156 168 | 5-9: 180 192 204 216 228 | 10-14: 240 252 264 276 288 | 15-19: 300 312 324 336 348 | 20-21: 360 372
  ~ Health regeneration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Health Regeneration; aoe: None
  ! BUG: Upon reconnecting from a disconnect when having this skill active it will appear as a maintained enchantment. (See the discussion page for more information and screenshots.)
Tiger's Fury #454 | Stance | Prophecies | E10 R10
  All your non-attack skills are disabled for 5 seconds. For 5..11 seconds, you attack 25% faster.
  ~ Duration :: 0-4: 5 5 6 6 7 | 5-9: 7 7 8 8 9 | 10-14: 9 9 10 10 11 | 15-19: 11 11 12 12 13 | 20-21: 13 13
  # causes: Disable, Increased Attack Speed; special: duplicate
Toxicity #1472 | Nature Ritual | Nightfall | E15 C2 R60
  Create a level 1..10 spirit. Poisoned or Diseased creatures within its range suffer -2 Health degeneration. This spirit dies after 30..180 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Duration :: 0-4: 30 40 50 60 70 | 5-9: 80 90 100 110 120 | 10-14: 130 140 150 160 170 | 15-19: 180 190 200 210 220 | 20-21: 230 240
  # causes: Spirit, Health Degeneration; aoe: large spirit
Viper's Nest #1211 | Trap | Factions | E10 C2 R20
  Create a Viper's Nest. When it is triggered, all nearby foes are struck for 5..35 piercing damage and become Poisoned for 5..20 seconds. Viper's Nest expires after 90 seconds. This Trap is easily interrupted.
  ~ Piercing damage :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  ~ Poison duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Piercing Damage, Poison; aoe: nearby

### Ranger / Expertise
Archer's Signet #1200 | Elite Signet | Factions | C1 R12
  For 1..24 second[s], conditions you apply while wielding a bow last 150% longer.
  ~ Duration :: 0-4: 1 3 4 6 7 | 5-9: 9 10 12 13 15 | 10-14: 16 18 19 21 22 | 15-19: 24 26 27 29 30 | 20-21: 32 33
  ! BUG: This skill does not increase the amount of time a target is burning from Glyph of Immolation nor Mark of Rodgort.
Distracting Shot #399 | Bow Attack | Core | E5 C½ R10
  If Distracting Shot hits, it interrupts target foe's action but deals only 1..16 damage. If the interrupted action was a skill, that skill is disabled for an additional 20 seconds.
  ~ Armor-ignoring damage :: 0-4: 1 2 3 4 5 | 5-9: 6 7 8 9 10 | 10-14: 11 12 13 14 15 | 15-19: 16 17 18 19 20 | 20-21: 21 22
  # causes: Interrupt, Disable
Dodge #425 | Stance | Prophecies | E5 R30
  For 5..11 seconds, you move 33% faster and have a 27..75% chance to block incoming projectiles. Dodge ends if you attack.
  ~ Duration :: 0-4: 5 5 6 6 7 | 5-9: 7 7 8 8 9 | 10-14: 9 9 10 10 11 | 15-19: 11 11 12 12 13 | 20-21: 13 13
  ~ Block chance % :: 0-4: 27 30 33 37 40 | 5-9: 43 46 49 53 56 | 10-14: 59 62 65 69 72 | 15-19: 75 78 81 85 88 | 20-21: 91 94
  # causes: Increased Movement Speed, Block; special: duplicate
Escape (PvP) #3060 | Elite Stance | Core | E5 R12
  For 1..8 second[s], you move 33% faster and have a 75% chance to block attacks. Escape ends if you make a melee attack.
  ~ Duration :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  # causes: Increased Movement Speed, Block
Expert Focus #2145 | Preparation | Eye of the North | E10 C2 R12
  For 24 seconds, your bow attack skills cost 1..2 less Energy and deal 1..10 extra damage.
  ~ Less energy cost :: 0-4: 1 1 1 1 1 | 5-9: 1 1 1 2 2 | 10-14: 2 2 2 2 2 | 15-19: 2 2 2 2 2 | 20-21: 2 2
  ~ + Damage :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # causes: Decreased Energy Cost; aoe: none
Expert's Dexterity (PvP) #2959 | Elite Stance | Nightfall | E5 R20
  For 1..20 second[s], you attack 15% faster and your Marksmanship attribute is increased by 1.
  ~ Duration :: 0-4: 1 2 4 5 6 | 5-9: 7 9 10 11 12 | 10-14: 14 15 16 17 19 | 15-19: 20 21 23 24 25 | 20-21: 26 28
  # causes: Increased Attack Speed, Increased Attribute
Glass Arrows (PvP) #3145 | Elite Preparation | Factions | E5 C2 R12
  For 10..35 seconds, your arrows strike for +6..18 damage if they hit and cause Bleeding for 10..20 seconds if they are blocked.
  ~ Duration :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  ~ + Damage :: 0-4: 6 7 8 8 9 | 5-9: 10 11 12 12 13 | 10-14: 14 15 16 16 17 | 15-19: 18 19 20 20 21 | 20-21: 22 23
  ~ Bleeding duration :: 0-4: 10 11 11 12 13 | 5-9: 13 14 15 15 16 | 10-14: 17 17 18 19 19 | 15-19: 20 21 21 22 23 | 20-21: 23 24
  # causes: Block Punishment, Bleeding
Infuriating Heat (PvP) #3466 | Elite Nature Ritual | Nightfall | E5 C2 R30
  Create a level 1..10 spirit. Non-spirit creatures within its range gain adrenaline 33..66% as fast. This spirit dies after 30..120 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Duration :: 0-4: 30 36 42 48 54 | 5-9: 60 66 72 78 84 | 10-14: 90 96 102 108 114 | 15-19: 120 126 132 138 144 | 20-21: 150 156
  ~ Increased Adrenaline % :: 0-4: 33 35 37 40 42 | 5-9: 44 46 48 51 53 | 10-14: 55 57 59 62 64 | 15-19: 66 68 70 73 75 | 20-21: 77 79
  # causes: Spirit, Increased Adrenaline Build Rate; aoe: large spirit
  ! BUG: Does not double adrenaline gain from all sources as stated, but rather gives one additional strike of adrenaline per attack. Despite this, it still does not stack with other skills that increase the rate of adrenaline gain, such as "For Great Justice!" or Weapon of Fury, but stacks additively with Mark of Fury or Dark Fury. [from PvE version page]
Lightning Reflexes (PvP) #3141 | Stance | Core | E10 R45
  For 5..11 seconds, you have a 75% chance to block melee and projectile attacks, and you attack 33% faster.
  ~ Duration :: 0-4: 5 5 6 6 7 | 5-9: 7 7 8 8 9 | 10-14: 9 9 10 10 11 | 15-19: 11 11 12 12 13 | 20-21: 13 13
  # causes: Block, Increased Attack Speed
Marksman's Wager #430 | Elite Preparation | Prophecies | E5 C1 R24
  For 18 seconds, you gain 5..10 Energy whenever your arrows hit, but lose 10 Energy whenever your arrows fail to strike.
  ~ Energy gain :: 0-4: 5 5 6 6 6 | 5-9: 7 7 7 8 8 | 10-14: 8 9 9 9 10 | 15-19: 10 10 11 11 11 | 20-21: 12 12
  # causes: Energy Gain, Energy Loss
Oath Shot #405 | Elite Bow Attack | Prophecies | E10 R25
  If Oath Shot hits, all of your skills except Oath Shot are recharged. If it misses, all of your skills are disabled for 10..4 seconds. (50% miss chance with Expertise 7 or less.)
  ~ Disable duration :: 0-4: 10 10 9 9 8 | 5-9: 8 8 7 7 6 | 10-14: 6 6 5 5 4 | 15-19: 4 4 3 3 2 | 20-21: 2 2
  # causes: Recharge, Disable
Point Blank Shot #407 | Bow Attack | Prophecies | E5 R3
  Shoot an arrow that has half the normal range, but strikes for +10..40 damage.
  ~ + Damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # range: half; special: duplicate
Practiced Stance #449 | Elite Stance | Prophecies | E5 R15
  For 20..35 seconds, your Preparations recharge 50% faster and last 30..300% longer.
  ~ Duration :: 0-4: 20 21 22 23 24 | 5-9: 25 26 27 28 29 | 10-14: 30 31 32 33 34 | 15-19: 35 36 37 38 39 | 20-21: 40 41
  ~ Longer Preparations % :: 0-4: 30 48 66 84 102 | 5-9: 120 138 156 174 192 | 10-14: 210 228 246 264 282 | 15-19: 300 318 336 354 372 | 20-21: 390 408
  # causes: Decreased Recharge Time
Throw Dirt #424 | Touch skill | Core | E5 C1 R30
  Skill. Target touched foe and foes adjacent to your target become Blinded for 3..15 seconds.
  ~ Blind duration :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Blind; target: foes; range: touch; aoe: adjacent
Trapper's Focus #946 | Elite Preparation | Factions | E5 C2 R12
  For 12..36 seconds, your trap skills are not easily interruptible and your Wilderness Survival attribute is increased by +0..4.
  ~ Duration :: 0-4: 12 14 15 17 18 | 5-9: 20 22 23 25 26 | 10-14: 28 30 31 33 34 | 15-19: 36 38 39 41 42 | 20-21: 44 46
  ~ + Wilderness Survival :: 0-4: 0 0 1 1 1 | 5-9: 1 2 2 2 2 | 10-14: 3 3 3 3 4 | 15-19: 4 4 5 5 5 | 20-21: 5 6
  # causes: Increased Attribute
Trapper's Speed #1475 | Stance | Nightfall | E5 R20
  For 5..30 seconds, your Traps recharge 25% faster and activate 25% faster. This Stance ends if you successfully hit with an attack.
  ~ Duration :: 0-4: 5 7 8 10 12 | 5-9: 13 15 17 18 20 | 10-14: 22 23 25 27 28 | 15-19: 30 32 33 35 37 | 20-21: 38 40
  # causes: Decreased Recharge Time, Decreased Activation Time
Whirling Defense #450 | Stance | Core | E10 R60
  For 8..20 seconds, you have 75% chance to block attacks. Whenever you block a projectile in this way, adjacent foes take 5..11 damage.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  ~ Armor-ignoring damage :: 0-4: 5 5 6 6 7 | 5-9: 7 7 8 8 9 | 10-14: 9 9 10 10 11 | 15-19: 11 11 12 12 13 | 20-21: 13 13
  # causes: Block, Physical Damage; target: untargeted; aoe: adjacent
  ! ANOMALY: Although the damage is nondescript, it does trigger Mark of Pain and Winnowing, making it armor-ignoring physical damage.
  ! BUG: The non-concise description is wrong, this skill will deal damage even if the projectile is blocked from another blocking source.
Zojun's Haste #1196 | Stance | Factions | E5 R30
  For 5..11 seconds, you move 33% faster and have a 27..75% chance to block incoming projectiles. Zojun's Haste ends if you attack.
  ~ Duration :: 0-4: 5 5 6 6 7 | 5-9: 7 7 8 8 9 | 10-14: 9 9 10 10 11 | 15-19: 11 11 12 12 13 | 20-21: 13 13
  ~ Block chance % :: 0-4: 27 30 33 37 40 | 5-9: 43 46 49 53 56 | 10-14: 59 62 65 69 72 | 15-19: 75 78 81 85 88 | 20-21: 91 94
  # causes: Increased Movement Speed, Block; special: duplicate
Zojun's Shot #1192 | Bow Attack | Factions | E5 R3
  Shoot an arrow that has half the normal range, but strikes for +10..40 damage.
  ~ + Damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # range: half; special: duplicate

### Ranger / Marksmanship
Arcing Shot #1467 | Bow Attack | Nightfall | E5 R3
  If this arrow hits, it strikes for +10..35 damage. This arrow cannot be blocked, but it moves 50% slower.
  ~ + Damage :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  # causes: Unblockable
Barrage #395 | Elite Bow Attack | Core | E5 R1
  All your preparations are removed. Shoot arrows at target foe and up to 5 foes adjacent to your target. These arrows strike for +5..20 damage if they hit.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # aoe: adjacent
Body Shot #2198 | Bow Attack | Eye of the North | E5 R8
  If this attack hits, you deal +5..20 damage. If it hits a foe with Cracked Armor, you gain 5..10 Energy.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Energy gain :: 0-4: 5 5 6 6 6 | 5-9: 7 7 7 8 8 | 10-14: 8 9 9 9 10 | 15-19: 10 10 11 11 11 | 20-21: 12 12
  # causes: Energy Gain
Broad Head Arrow #1198 | Elite Bow Attack | Factions | E10 R10
  You shoot a broad head arrow that moves slower than normal. If it hits, target foe is Dazed for 5..20 seconds, and if target foe is casting a spell that spell is interrupted.
  ~ Dazed duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Dazed, Interrupt
Burning Arrow #1466 | Elite Bow Attack | Nightfall | E10 R5
  If this attack hits, you strike for +10..30 damage and cause Burning for 2..8 seconds.
  ~ + Damage :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  ~ Burning duration :: 0-4: 2 2 3 3 4 | 5-9: 4 4 5 5 6 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 10
  # causes: Burning
Concussion Shot #408 | Bow Attack | Core | E25 C½ R5
  If Concussion Shot hits while target foe is casting a spell, the spell is interrupted and your target is Dazed for 5..20 seconds. This attack deals only 1..16 damage.
  ~ Dazed duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Armor-ignoring damage :: 0-4: 1 2 3 4 5 | 5-9: 6 7 8 9 10 | 10-14: 11 12 13 14 15 | 15-19: 16 17 18 19 20 | 20-21: 21 22
  # causes: Dazed, Interrupt
  ! BUG: This skill does not interrupt spells; the application of daze does: if the daze is not applied (i.e. if the target is enchanted by Infuse Condition and has a minion to transfer the daze to), no interrupt will occur.
Crippling Shot (PvP) #3450 | Elite Bow Attack | Prophecies | E10 R2
  If Crippling Shot hits, your target becomes Crippled for 4..14 second[s]. This attack cannot be blocked.
  ~ Cripple duration :: 0-4: 4 5 5 6 7 | 5-9: 7 8 9 9 10 | 10-14: 11 11 12 13 13 | 15-19: 14 15 15 16 17 | 20-21: 17 18
  # causes: Unblockable, Crippled
Crossfire #1469 | Bow Attack | Nightfall | E5 R4
  If this attack hits target foe, it deals +5..20 damage. If that foe is near any of your allies, this attack cannot be blocked.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Unblockable
Debilitating Shot #406 | Bow Attack | Core | E10 R10
  If Debilitating Shot hits, your target loses 1..10 Energy.
  ~ Energy loss :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # causes: Energy Loss
Determined Shot #402 | Bow Attack | Core | E5 R10
  If Determined Shot hits, you strike for +5..20 damage. If Determined Shot fails to hit, all of your attack skills are recharged.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Recharge
Disrupting Accuracy #1723 | Preparation | Nightfall | E5 C2 R12
  For 36 seconds, whenever your arrows critical, they also interrupt your target.
  # causes: Interrupt
Disrupting Shot #2143 | Bow Attack | Eye of the North | E10 C½ R15
  If this attack hits, target foe's action is interrupted. If that action was a Skill, you strike for +10..40 damage.
  ~ + Damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Interrupt
Favorable Winds #472 | Nature Ritual | Core | E5 C2 R60
  Create a level 1..10 spirit. For non-spirit creatures within its range, arrows move twice as fast and strike for +6 damage. This spirit dies after 30..240 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Duration :: 0-4: 30 44 58 72 86 | 5-9: 100 114 128 142 156 | 10-14: 170 184 198 212 226 | 15-19: 240 254 268 282 296 | 20-21: 310 324
  # causes: Spirit, Increased Projectile Speed; aoe: large spirit
Focused Shot #909 | Bow Attack | Factions | E5 R8
  This shot moves three times faster, cannot be blocked, and strikes for +10..40 damage but all of your other attack skills are disabled for 8..4 seconds.
  ~ + Damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  ~ Disabled Duration :: 0-4: 8 8 7 7 7 | 5-9: 7 6 6 6 6 | 10-14: 5 5 5 5 4 | 15-19: 4 4 3 3 3 | 20-21: 3 2
  # causes: Unblockable, Increased Projectile Speed, Disable
Hunter's Shot #391 | Bow Attack | Core | E5 C1 R10
  If this attack hits, your target bleeds for 3..25 seconds.
  ~ Bleeding duration :: 0-4: 3 4 6 7 9 | 5-9: 10 12 13 15 16 | 10-14: 18 19 21 22 24 | 15-19: 25 26 28 29 31 | 20-21: 32 34
  # causes: Bleeding
Keen Arrow (PvP) #3147 | Bow Attack | Nightfall | E5 R12
  If this attack hits, you strike for +5..15 damage. If you land a critical hit, you deal an additional +5..30 damage.
  ~ + Damage :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  ~ + Damage when critical :: 0-4: 5 7 8 10 12 | 5-9: 13 15 17 18 20 | 10-14: 22 23 25 27 28 | 15-19: 30 32 33 35 37 | 20-21: 38 40
Marauder's Shot #908 | Bow Attack | Factions | E5 R6
  If Marauder's Shot hits, you strike for +25..55 damage and all your non-attack skills are disabled for 5 seconds.
  ~ + Damage :: 0-4: 25 27 29 31 33 | 5-9: 35 37 39 41 43 | 10-14: 45 47 49 51 53 | 15-19: 55 57 59 61 63 | 20-21: 65 67
  # causes: Disable
Melandru's Shot (PvP) #3459 | Elite Bow Attack | Factions | E5 C1 R12
  If Melandru's Shot hits, your target begins Bleeding for 5..25 seconds. If it hits a foe that is moving or knocked down, that foe takes +10..25 damage and is Crippled for 5..15 seconds.
  ~ Bleeding duration :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  ~ + Damage :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  ~ Crippled duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Crippled, Bleeding
Needling Shot #1197 | Bow Attack | Factions | E5 C¾ R4
  Needling Shot strikes for only 10..30 damage and moves faster than normal. If Needling Shot strikes a foe below 50% Health, Needling Shot recharges instantly. Your other attack skills are disabled for 2 seconds.
  ~ Armor-ignoring damage :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  # causes: Increased Projectile Speed, Recharge, Disable
  ! ANOMALY: The regular description is incorrect in that the target does not have to be hit for the skill to recharge.
  ! BUG: Both descriptions are incorrect in that only bow attack skills are disabled.
Penetrating Attack (PvP) #2861 | Bow Attack | Prophecies | E10 C1 R4
  If Penetrating Attack hits, you strike for +5..15 damage and this attack has 10% armor penetration.
  ~ + Damage :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Armor Penetration; special: duplicate
Pin Down #392 | Bow Attack | Core | E15 R8
  If Pin Down hits, your target is Crippled for 3..15 seconds.
  ~ Crippled duration :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Crippled
Power Shot #394 | Bow Attack | Core | E10 R3
  If Power Shot hits, target foe takes 25..50 damage.
  ~ Armor-ignoring damage :: 0-4: 25 27 28 30 32 | 5-9: 33 35 37 38 40 | 10-14: 42 43 45 47 48 | 15-19: 50 52 53 55 57 | 20-21: 58 60
Precision Shot #400 | Bow Attack | Core | E10 C1 R6
  If Precision Shot hits, you strike for +3..10 damage. Precision Shot cannot be blocked. This action is easily interrupted.
  ~ + Damage :: 0-4: 3 3 4 4 5 | 5-9: 5 6 6 7 7 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 13
  # causes: Unblockable
Prepared Shot #1465 | Elite Bow Attack | Nightfall | E5 R6
  If this attack hits, you strike for +10..25 damage. If you are under the effects of a preparation, you gain 1..9 Energy.
  ~ + Damage :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  ~ Energy gain :: 0-4: 1 2 2 3 3 | 5-9: 4 4 5 5 6 | 10-14: 6 7 7 8 8 | 15-19: 9 10 10 11 11 | 20-21: 12 12
  # causes: Energy Gain
Punishing Shot #409 | Elite Bow Attack | Prophecies | E10 C½ R5
  If Punishing Shot hits, you strike for +10..20 damage and your target is interrupted.
  ~ + Damage :: 0-4: 10 11 11 12 13 | 5-9: 13 14 15 15 16 | 10-14: 17 17 18 19 19 | 15-19: 20 21 21 22 23 | 20-21: 23 24
  # causes: Interrupt
Rapid Fire #2068 | Preparation | Eye of the North | E5 C2 R12
  For 5..25 seconds, you attack 33% faster while wielding a bow.
  ~ Duration :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  # causes: Increased Attack Speed
Read the Wind (PvP) #2969 | Preparation | Core | E5 C2 R12
  For 24 seconds, your arrows move twice as fast.
  # causes: Increased Projectile Speed
  ! ANOMALY: Some bow attack skills with a modified flight time or arc ignore the effect of Read the Wind on their flight time and arc but still benefit from the bonus damage, e.g. Broad Head Arrow and Called Shot. Quick Shot and Arcing Shot are exceptions to this. [from PvE version page]
Savage Shot #426 | Bow Attack | Core | E10 C½ R5
  If Savage Shot hits, your target's action is interrupted. If that action was a spell, you strike for +13..28 damage.
  ~ + Damage :: 0-4: 13 14 15 16 17 | 5-9: 18 19 20 21 22 | 10-14: 23 24 25 26 27 | 15-19: 28 29 30 31 32 | 20-21: 33 34
  # causes: Interrupt
Screaming Shot #1719 | Bow Attack | Nightfall | E10 R8
  If this attack hits, you deal +10..25 damage. If your target is within earshot, that foe begins Bleeding for 5..20 seconds.
  ~ + Damage :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  ~ Bleeding duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Bleeding; target: foes
Seeking Arrows #893 | Preparation | Factions | E10 C2 R15
  For 3..14 seconds, your arrows cannot be blocked. Seeking Arrows ends if you fail to hit.
  ~ Duration :: 0-4: 3 4 4 5 6 | 5-9: 7 7 8 9 10 | 10-14: 10 11 12 13 13 | 15-19: 14 15 15 16 17 | 20-21: 18 18
  # causes: Unblockable
Sloth Hunter's Shot (PvP) #2925 | Bow Attack | Eye of the North | E10 R15
  If this attack hits, target foe takes +5..15 damage. If that foe is not using a skill, Sloth Hunter's Shot does an additional +5..20 damage.
  ~ + Damage :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  ~ Additional damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
Splinter Shot #852 | Bow Attack | Factions | E10 R5
  If Splinter Shot hits, you deal +3..15 damage. If Splinter Shot is blocked, all foes in the area to your target take 5..65 damage.
  ~ + Damage :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  ~ Damage to foes in the area :: 0-4: 5 9 13 17 21 | 5-9: 25 29 33 37 41 | 10-14: 45 49 53 57 61 | 15-19: 65 69 73 77 81 | 20-21: 85 89
  # causes: Block Punishment; aoe: in the area
Sundering Attack (PvP) #2864 | Bow Attack | Factions | E10 C1 R4
  If Sundering Attack hits, you strike for +5..15 damage and this attack has 10% armor penetration.
  ~ + Damage :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Armor Penetration; special: duplicate
Volley #2144 | Bow Attack | Eye of the North | E5 R2
  All your Preparations are removed. Shoot arrows at target foe and up to 3 foes adjacent to your target. These arrows strike for +1..10 damage if they hit.
  ~ + Damage :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # aoe: adjacent
  ! BUG: Volley also removes Glyphs. Hero AI can use Volley right after a glyph, which removes its effect.

### Ranger / No Attribute
Antidote Signet #427 | Signet | Core | C1 R4
  Cleanse yourself of Poison, Disease, and Blindness, and one additional condition.
  # removes: Condition; target: self
Called Shot #403 | Bow Attack | Core | E5 R3
  Shoot an arrow that moves 3 times faster and cannot be blocked.
  # causes: Unblockable, Increased Projectile Speed
Dual Shot #396 | Bow Attack | Core | E10 R10
  Shoot two arrows simultaneously at target foe. These arrows deal 25% less damage.
Forked Arrow #1722 | Bow Attack | Nightfall | E10 R5
  Shoot two arrows simultaneously at target foe. If you are under the effects of an enchantment or hex, you shoot only one arrow.
Magebane Shot #1726 | Elite Bow Attack | Nightfall | E10 C½ R5
  If this attack hits, it interrupts target foe's action. If that action was a spell, it is disabled for an additional 10 seconds. This attack cannot be blocked.
  # causes: Unblockable, Interrupt, Disable
Quick Shot #397 | Elite Bow Attack | Core | E5 C½ R1
  Shoot an arrow that moves twice as fast.
  # causes: Increased Projectile Speed
Storm's Embrace #1474 | Stance | Nightfall | E5 R30
  For 10 seconds, you move 25% faster. This stance is refreshed whenever you take Elemental damage.
  # causes: Increased Movement Speed, Renewal

### Ranger / Wilderness Survival
Apply Poison #435 | Preparation | Core | E15 C2 R12
  For 24 seconds, foes struck by your physical attacks become Poisoned for 3..15 seconds.
  ~ Duration :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Poison
  ! BUG: Heroes wielding a ranged weapon will target swap to new unpoisoned targets, but will not attack already poisoned ones.
Barbed Arrows #1470 | Preparation | Nightfall | E10 C2 R12
  For 24 seconds, your arrows cause Bleeding for 3..15 seconds. You have -40 armor while activating this skill.
  ~ Bleeding duration :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Bleeding, Decreased Armor Rating
  ! ANOMALY: The armor penalty from this skill is applied after the armor cap and the effects of Cracked Armor and armor penetration.
Barbed Trap #458 | Trap | Core | E10 C2 R20
  When Barbed Trap is triggered, all nearby foes are struck for 7..23 piercing damage, become Crippled, and begin Bleeding for 3..25 seconds. Barbed Trap ends after 90 seconds. While activating this skill, you are easily interrupted.
  ~ Piercing damage :: 0-4: 7 8 9 10 11 | 5-9: 12 13 14 16 17 | 10-14: 18 19 20 21 22 | 15-19: 23 24 25 26 27 | 20-21: 28 29
  ~ Crippled and Bleeding duration :: 0-4: 3 4 6 7 9 | 5-9: 10 12 13 15 16 | 10-14: 18 19 21 22 24 | 15-19: 25 26 28 29 31 | 20-21: 32 34
  # causes: Crippled, Bleeding; aoe: nearby
Brambles #947 | Nature Ritual | Factions | E10 C2 R60
  Create a level 1..10 Spirit. Non-Spirit creatures that are knocked down in its range take 5 damage and begin Bleeding for 5..20 seconds. This Spirit dies after 30..240 seconds.
  ~ Spirit level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Bleeding duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Spirit duration :: 0-4: 30 44 58 72 86 | 5-9: 100 114 128 142 156 | 10-14: 170 184 198 212 226 | 15-19: 240 254 268 282 296 | 20-21: 310 324
  # causes: Spirit, Bleeding; aoe: spirit
Choking Gas #434 | Preparation | Core | E15 C2 R24
  For 1..12 seconds, your arrows deal 1..8 more damage and spread Choking Gas to all adjacent foes on impact. Choking Gas interrupts foes attempting to cast spells.
  ~ Duration :: 0-4: 1 2 2 3 4 | 5-9: 5 5 6 7 8 | 10-14: 8 9 10 11 11 | 15-19: 12 13 13 14 15 | 20-21: 16 16
  ~ + Damage :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  # causes: Interrupt; aoe: adjacent
Conflagration #466 | Nature Ritual | Factions | E5 C2 R60
  Create a level 1..10 spirit. For non-spirit creatures within its range, all arrows that hit strike for fire damage. This spirit dies after 30..240 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Duration :: 0-4: 30 44 58 72 86 | 5-9: 100 114 128 142 156 | 10-14: 170 184 198 212 226 | 15-19: 240 254 268 282 296 | 20-21: 310 324
  # causes: Spirit, Fire Damage; aoe: large spirit
  ! ANOMALY: This spirit also causes Bone Fiend attacks and spear attacks to strike with fire damage.
  ! ANOMALY: Unlike Winter, this skill requires the attacker to be inside the spirit area of effect.
Dryder's Defenses #452 | Stance | Prophecies | E5 R60
  For 5..11 seconds, you gain 75% chance to block attacks and 34..60 armor against elemental damage.
  ~ Duration :: 0-4: 5 5 6 6 7 | 5-9: 7 7 8 8 9 | 10-14: 9 9 10 10 11 | 15-19: 11 11 12 12 13 | 20-21: 13 13
  ~ + Armor :: 0-4: 34 36 37 39 41 | 5-9: 43 44 46 48 50 | 10-14: 51 53 55 57 58 | 15-19: 60 62 63 65 67 | 20-21: 69 70
  # causes: Block, Increased Armor Rating
Dust Trap #457 | Trap | Prophecies | E25 C2 R30
  When Dust Trap is triggered, every second (for 5 seconds total), all nearby foes are Blinded for 3..8 seconds and take 10..25 damage. While activating this skill, you are easily interrupted. Dust Trap ends after 90 seconds.
  ~ Blind duration :: 0-4: 3 3 4 4 4 | 5-9: 5 5 5 6 6 | 10-14: 6 7 7 7 8 | 15-19: 8 8 9 9 9 | 20-21: 10 10
  ~ Armor-ignoring damage :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  # causes: Blind, Earth Damage; aoe: nearby
  ! BUG: The damage dealt is armor-ignoring earth damage.
Equinox #1212 | Elite Nature Ritual | Factions | E10 C2 R15
  Create a level 1..10 spirit. Spells cast within its range that cause Overcast cause an additional 10 Overcast. This spirit dies after 30..240 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Duration :: 0-4: 30 44 58 72 86 | 5-9: 100 114 128 142 156 | 10-14: 170 184 198 212 226 | 15-19: 240 254 268 282 296 | 20-21: 310 324
  # causes: Spirit, Overcast; aoe: spirit
Famine #997 | Elite Nature Ritual | Factions | E10 C2 R15
  Create a level 1..10 spirit. Whenever a non-spirit creature in its range reaches 0 Energy, that creature takes 20..70 damage. This spirit dies after 30..180 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Damage :: 0-4: 20 23 27 30 33 | 5-9: 37 40 43 47 50 | 10-14: 53 57 60 63 67 | 15-19: 70 73 77 80 83 | 20-21: 87 90
  ~ Duration :: 0-4: 30 40 50 60 70 | 5-9: 80 90 100 110 120 | 10-14: 130 140 150 160 170 | 15-19: 180 190 200 210 220 | 20-21: 230 240
  # causes: Spirit; aoe: spirit
Flame Trap #459 | Trap | Core | E10 C2 R20
  When Flame Trap is triggered, every second (for 3 seconds total), all nearby foes are struck for 5..20 fire damage and set on fire for 1..3 second[s]. Flame Trap ends after 90 seconds. While activating this skill, you are easily interrupted.
  ~ Fire damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Burning duration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Burning, Fire Damage; aoe: nearby
Frozen Soil #471 | Nature Ritual | Prophecies | E10 C2 R30
  Create a level 1..10 spirit. Non-spirit creatures within its range cannot activate resurrection skills. This spirit dies after 30..180 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Duration :: 0-4: 30 40 50 60 70 | 5-9: 80 90 100 110 120 | 10-14: 130 140 150 160 170 | 15-19: 180 190 200 210 220 | 20-21: 230 240
  # causes: Spirit; aoe: large spirit
  ! BUG: Eternal Aura can be cast while under the effects of Frozen Soil.
Greater Conflagration #465 | Elite Nature Ritual | Prophecies | E5 C2 R15
  Create a level 1..10 spirit. For non-spirit creatures within its range, all physical damage is fire damage instead. This spirit dies after 30..240 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Duration :: 0-4: 30 44 58 72 86 | 5-9: 100 114 128 142 156 | 10-14: 170 184 198 212 226 | 15-19: 240 254 268 282 296 | 20-21: 310 324
  # causes: Spirit, Fire Damage; aoe: large spirit
  ! ANOMALY: Unlike Winter this skill requires the attacker to be inside the spirit area of effect.
  ! BUG: Does not properly convert the physical damage of certain skills (notably: Ebon Vanguard Sniper Support and Veil of Thorns). As a result, the skill chain will not trigger the conditional effects of other skills that depend on fire damage (in particular, for Intensity).
Healing Spring #460 | Trap | Prophecies | E10 C2 R20
  For 10 seconds, all adjacent allies are healed for 15..60 every 2 seconds. While activating this skill, you are easily interrupted.
  ~ Healing :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  # causes: Healing; aoe: adjacent
  ! BUG: Although allied spirits will display this skill's animation effect, they will not be healed (since spirits are never affected by healing).
Ignite Arrows #431 | Preparation | Prophecies | E10 C2 R12
  For 24 seconds, your arrows explode on contact, dealing 3..18 fire damage to target and all adjacent foes.
  ~ Fire damage :: 0-4: 3 4 5 6 7 | 5-9: 8 9 10 11 12 | 10-14: 13 14 15 16 17 | 15-19: 18 19 20 21 22 | 20-21: 23 24
  # causes: Fire Damage; aoe: adjacent
Incendiary Arrows #428 | Elite Bow Attack | Prophecies | E5 R5
  Shoot arrows at target foe and up to 2 foes near your target. Those foes are set on fire for 1..3 second[s].
  ~ Burning duration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Burning; aoe: nearby
Kindle Arrows #433 | Preparation | Core | E5 C2 R12
  For 24 seconds, your arrows deal fire damage and hit for an additional 3..24 fire damage.
  ~ + Fire damage :: 0-4: 3 4 6 7 9 | 5-9: 10 11 13 14 16 | 10-14: 17 18 20 21 23 | 15-19: 24 25 27 28 30 | 20-21: 31 32
  # causes: Fire Damage
Melandru's Arrows #429 | Elite Preparation | Prophecies | E5 C2 R12
  For 18 seconds, whenever your arrows hit, they cause Bleeding for 3..25 seconds, and if they hit a target who is under an enchantment, they do +8..28 damage.
  ~ Bleeding duration :: 0-4: 3 4 6 7 9 | 5-9: 10 12 13 15 16 | 10-14: 18 19 21 22 24 | 15-19: 25 26 28 29 31 | 20-21: 32 34
  ~ + Damage :: 0-4: 8 9 11 12 13 | 5-9: 15 16 17 19 20 | 10-14: 21 23 24 25 27 | 15-19: 28 29 31 32 33 | 20-21: 35 36
  # causes: Bleeding
Melandru's Resilience #451 | Elite Stance | Prophecies | E5 R15
  For 8..20 seconds, you gain +4 Health regeneration and +1 Energy regeneration for each condition and hex you are suffering.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  # causes: Health Regeneration, Energy Regeneration
Muddy Terrain #477 | Nature Ritual | Prophecies | E5 C2 R30
  Create a level 1..10 spirit. Non-spirit creatures within its range move 10% slower and speed boosts have no effect. This spirit dies after 30..180 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Duration :: 0-4: 30 40 50 60 70 | 5-9: 80 90 100 110 120 | 10-14: 130 140 150 160 170 | 15-19: 180 190 200 210 220 | 20-21: 230 240
  # causes: Spirit, Decreased Movement Speed; aoe: large spirit
Natural Stride #1727 | Stance | Nightfall | E5 R12
  For 1..8 second[s], you run 33% faster and have a 50% chance to block incoming attacks. Natural Stride ends if you become hexed or enchanted.
  ~ Duration :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  # causes: Increased Movement Speed, Block
Nature's Renewal (PvP) #3445 | Nature Ritual | Core | E5 C2 R60
  Create a level 1..10 spirit. For 30..240 seconds, enchantments and hexes cast by non-spirit creatures in range take 50..75% longer to cast, and it costs twice as much Energy to maintain enchantments. This spirit dies after 30..240 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Duration :: 0-4: 30 44 58 72 86 | 5-9: 100 114 128 142 156 | 10-14: 170 184 198 212 226 | 15-19: 240 254 268 282 296 | 20-21: 310 324
  ~ Longer cast % :: 0-4: 50 52 53 55 57 | 5-9: 58 60 62 63 65 | 10-14: 67 68 70 72 73 | 15-19: 75 77 78 80 82 | 20-21: 83 85
  # causes: Spirit, Increased Activation Time, Increased Energy Cost; aoe: large spirit
Pestilence #870 | Nature Ritual | Nightfall | E5 C2 R60
  Create a level 1..10 spirit. When any creature within its range dies, conditions on that creature spread to any creature in the area already suffering from a condition. This spirit dies after 30..180 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Duration :: 0-4: 30 40 50 60 70 | 5-9: 80 90 100 110 120 | 10-14: 130 140 150 160 170 | 15-19: 180 190 200 210 220 | 20-21: 230 240
  # causes: Spirit, Condition; aoe: large spirit
Piercing Trap #2140 | Trap | Eye of the North | E10 C2 R30
  When Piercing Trap is triggered, all nearby foes are struck for 5..50 piercing damage. Any foes with Cracked Armor are struck for an additional 15..60 damage. Piercing Trap ends after 90 seconds. While activating this skill, you are easily interrupted.
  ~ Piercing damage :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  ~ Additional damage :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  # causes: Piercing Damage; aoe: nearby
Poison Arrow #404 | Elite Bow Attack | Prophecies | E5 R1
  If Poison Arrow hits, your target becomes Poisoned for 5..20 seconds.
  ~ Poison duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Poison
Poison Tip Signet #2199 | Signet | Eye of the North | C1 R6
  For 60 seconds, your next attack also inflicts Poison for 8..15 seconds.
  ~ Poison duration :: 0-4: 8 8 9 9 10 | 5-9: 10 11 11 12 12 | 10-14: 13 13 14 14 15 | 15-19: 15 15 16 16 17 | 20-21: 17 18
  # causes: Poison
Quickening Zephyr #475 | Nature Ritual | Core | E25 C2 R60
  Create a level 1..10 spirit. For non-spirit creatures within its range, all skills recharge twice as fast and cost 30% more of the base Energy to cast. This spirit dies after 15..90 seconds.
  ~ Spirit level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Duration :: 0-4: 15 20 25 30 35 | 5-9: 40 45 50 55 60 | 10-14: 65 70 75 80 85 | 15-19: 90 95 100 105 110 | 20-21: 115 120
  # causes: Spirit, Decreased Recharge Time, Increased Energy Cost; aoe: large spirit
Quicksand #1473 | Elite Nature Ritual | Nightfall | E10 C2 R30
  Create a level 1..10 spirit. All non-spirit creatures within its range lose 1 Energy each time they attack or use a skill. This spirit dies after 30..180 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Duration :: 0-4: 30 40 50 60 70 | 5-9: 80 90 100 110 120 | 10-14: 130 140 150 160 170 | 15-19: 180 190 200 210 220 | 20-21: 230 240
  # causes: Spirit, Energy Loss; aoe: large spirit
Roaring Winds #1725 | Nature Ritual | Nightfall | E10 C2 R60
  Create a level 1..10 spirit. Chants and shouts cost 1..5 more Energy. This spirit dies after 30..180 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Increased energy cost :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  ~ Duration :: 0-4: 30 40 50 60 70 | 5-9: 80 90 100 110 120 | 10-14: 130 140 150 160 170 | 15-19: 180 190 200 210 220 | 20-21: 230 240
  # causes: Spirit, Increased Energy Cost; aoe: spirit
Scavenger's Focus #1471 | Elite Skill | Nightfall | E5 R12
  For 10 seconds if you strike a foe who is suffering from a condition you gain 3..12 Energy.
  ~ Energy gain :: 0-4: 3 4 4 5 5 | 5-9: 6 7 7 8 8 | 10-14: 9 10 10 11 11 | 15-19: 12 13 13 14 14 | 20-21: 15 16
  # causes: Energy Gain
Serpent's Quickness #456 | Stance | Prophecies | E5 R45
  For 15..30 seconds, recharge times for your skills are reduced by 33%. Serpent's Quickness ends if your Health drops below 50%.
  ~ Duration :: 0-4: 15 16 17 18 19 | 5-9: 20 21 22 23 24 | 10-14: 25 26 27 28 29 | 15-19: 30 31 32 33 34 | 20-21: 35 36
  # causes: Decreased Recharge Time
Smoke Trap #1729 | Elite Trap | Nightfall | E10 C2 R15
  When Smoke Trap is triggered, nearby foes are Blinded and Dazed for 5..10 seconds. Smoke Trap ends after 90 seconds. While activating this skill, you are easily interrupted.
  ~ Blind and Dazed duration :: 0-4: 5 5 6 6 6 | 5-9: 7 7 7 8 8 | 10-14: 8 9 9 9 10 | 15-19: 10 10 11 11 11 | 20-21: 12 12
  # causes: Blind, Dazed; aoe: nearby
Snare #854 | Trap | Factions | E5 R15
  When Snare is triggered, all nearby foes become Crippled for 3..15 seconds. Snare ends after 90 seconds. While activating this skill, you are easily interrupted.
  ~ Crippled duration :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Crippled; aoe: nearby
Spike Trap #461 | Elite Trap | Core | E10 C2 R20
  When Spike Trap is triggered, every second (for 2 seconds), all nearby foes are struck for 10..40 piercing damage, become Crippled for 3..25 seconds, and are knocked down. Spike Trap ends after 90 seconds. While activating this skill, you are easily interrupted.
  ~ Damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  ~ Crippled duration :: 0-4: 3 4 6 7 9 | 5-9: 10 12 13 15 16 | 10-14: 18 19 21 22 24 | 15-19: 25 26 28 29 31 | 20-21: 32 34
  # causes: Piercing Damage, Knockdown, Crippled; aoe: nearby
Storm Chaser #455 | Stance | Core | E10 R20
  For 8..20 seconds, you move 25% faster, and you gain 1..5 Energy whenever you take elemental damage.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  ~ Energy gain :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Increased Movement Speed, Energy Gain
Tranquility (PvP) #3460 | Nature Ritual | Factions | E15 C2 R60
  Create a level 1..10 spirit. Enchantments cast by non-spirit creatures within its range expire 10..30% faster. This spirit dies after 15..120 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Expiration rate (%) :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  ~ Duration :: 0-4: 15 22 29 36 43 | 5-9: 50 57 64 71 78 | 10-14: 85 92 99 106 113 | 15-19: 120 127 134 141 148 | 20-21: 155 162
  # causes: Spirit; aoe: large spirit
Tripwire #1476 | Trap | Nightfall | E10 C2 R30
  When Tripwire is triggered, all nearby foes are struck for 5..20 piercing damage. Any Crippled foes are knocked down. Tripwire ends after 90 seconds. While activating this skill, you are easily interrupted.
  ~ Piercing damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Piercing Damage, Knockdown; aoe: nearby
Troll Unguent #446 | Skill | Core | E5 C3 R10
  For 13 seconds, you gain +3..10 Health regeneration.
  ~ Health regeneration :: 0-4: 3 3 4 4 5 | 5-9: 5 6 6 7 7 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 13
  # causes: Health Regeneration
Winnowing #463 | Nature Ritual | Core | E5 C2 R60
  Create a level 1..10 spirit. Non-spirit creatures within range take 4 additional damage whenever they take physical damage. This spirit dies after 30..240 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Duration :: 0-4: 30 44 58 72 86 | 5-9: 100 114 128 142 156 | 10-14: 170 184 198 212 226 | 15-19: 240 254 268 282 296 | 20-21: 310 324
  # causes: Spirit, Physical Damage; aoe: large spirit
  ! BUG: Contrary to the full description, creatures in range deal +4 damage, not receive. This means that all creatures, including spirits, do take +4 damage.
Winter #462 | Nature Ritual | Prophecies | E5 C2 R60
  Create a level 1..10 spirit. For creatures within its range, all elemental damage is cold damage instead. This spirit dies after 30..240 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Duration :: 0-4: 30 44 58 72 86 | 5-9: 100 114 128 142 156 | 10-14: 170 184 198 212 226 | 15-19: 240 254 268 282 296 | 20-21: 310 324
  # causes: Spirit, Cold Damage; aoe: large spirit
  ! ANOMALY: Unlike Greater Conflagration or Conflagration this skill requires either the attacker or the damage receiver to be inside the spirit area of effect.

## Monk

### Monk / Divine Favor
Blessed Aura #256 | Enchantment Spell | Prophecies | E10 U-1 C2 R2
  While you maintain this enchantment, Monk enchantments you cast last 10..35% longer.
  ~ % longer duration :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  # target: self
Blessed Light #941 | Elite Spell | Factions | E5 C¾ R5
  Heal target ally for 10..120 Health and remove one condition and one hex.
  ~ Healing :: 0-4: 10 17 25 32 39 | 5-9: 47 54 61 69 76 | 10-14: 83 91 98 105 113 | 15-19: 120 127 135 142 149 | 20-21: 157 164
  # causes: Healing; removes: Condition, Hex spell; target: allies
Blessed Signet #297 | Signet | Core | C2 R10
  For each enchantment you are maintaining, you gain 3 Energy. You cannot gain more than 3..24 Energy in this way.
  ~ Energy :: 0-4: 3 4 6 7 9 | 5-9: 10 11 13 14 16 | 10-14: 17 18 20 21 23 | 15-19: 24 25 27 28 30 | 20-21: 31 32
  # causes: Energy Gain; target: self
Boon Signet #847 | Elite Signet | Factions | C1 R6
  Heal target ally for 20..80 Health. Your next Healing or Protection Prayer spell that targets an ally heals for an additional 20..100 Health.
  ~ Healing :: 0-4: 20 24 28 32 36 | 5-9: 40 44 48 52 56 | 10-14: 60 64 68 72 76 | 15-19: 80 84 88 92 96 | 20-21: 100 104
  ~ Healing on next spell :: 0-4: 20 25 31 36 41 | 5-9: 47 52 57 63 68 | 10-14: 73 79 84 89 95 | 15-19: 100 105 111 116 121 | 20-21: 127 132
  # causes: Healing; target: allies
Contemplation of Purity #300 | Skill | Prophecies | E5 C¼ R10
  Lose all enchantments. For each one lost, you gain 0..80 Health, lose one hex, and lose one condition (maximum 1..8 hexes and conditions).
  ~ Health gain :: 0-4: 0 5 11 16 21 | 5-9: 27 32 37 43 48 | 10-14: 53 59 64 69 75 | 15-19: 80 85 91 96 101 | 20-21: 107 112
  ~ Maximum lost :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  # removes: Condition, Hex spell, Enchantment; target: self
  ! ANOMALY: When Contemplation of Purity (or any skill that removes "all enchantments") triggers the damage effects of Mirage Cloak or Aura of Holy Might, it behaves inconsistently compared to skills that remove a specific number of enchantments: Mirage Cloak: Damage will only trigger for a restricted list of Dervish enchantments (Aura of Thorns, Balthazar's Rage, Pious Renewal, Dust Cloak, Staggering Force, Grenth's Fingers, and itself). Aura of Holy Might: Damage will trigger for all Dervish enchantments except Eternal Aura, Shield of Force, Grenth's Aura, and Vow of Revolution. Skills that remove a defined number of enchantments (like Rend Enchantments or standard Dervish teardowns) do not suffer from these restrictions.
Deny Hexes #991 | Spell | Factions | E5 C1 R12
  Remove one hex from target ally and one additional hex for each recharging Divine Favor skill you have.
  # removes: Hex spell; target: allies
  ! BUG: The description is misleading: this skill removes a hex for each recharging Divine Favor skill, including itself. However, if Deny Hexes recharges instantly (e.g. using Glyph of Renewal), it will not be included as a recharging skill thus it is possible that no hex will be removed.
Divine Boon #284 | Enchantment Spell | Core | E5 U-1 C¼ R10
  While you maintain this enchantment, whenever you cast a Protection Prayer or Divine Favor spell that targets an ally, that ally is healed for 15..60 Health, and you lose 1 Energy.
  ~ Healing :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  # causes: Healing, Energy Loss; target: self
Divine Healing #279 | Spell | Prophecies | E5 C1 R12
  Heals you and party members within earshot for 15..60 points.
  ~ Healing :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  # causes: Healing; target: self; aoe: earshot; special: duplicate
Divine Intervention #246 | Enchantment Spell | Core | E5 C¼ R30
  For 10 seconds, the next time target ally receives damage that would be fatal, the damage is negated and that ally is healed for 26..240 Health.
  ~ Healing :: 0-4: 26 40 55 69 83 | 5-9: 97 112 126 140 154 | 10-14: 169 183 197 211 226 | 15-19: 240 254 269 283 297 | 20-21: 311 326
  # causes: Damage Reduction, Healing; target: allies
  ! BUG: This skill does not prevent damage; rather, it heals the enchanted target to the stated amount when they would die.
Divine Spirit #310 | Enchantment Spell | Prophecies | E10 C¼ R60
  For 1..14 second[s], Monk Spells cost you 5 less Energy to cast. (Minimum cost: 1 Energy.)
  ~ Duration :: 0-4: 1 2 3 4 4 | 5-9: 5 6 7 8 9 | 10-14: 10 11 11 12 13 | 15-19: 14 15 16 17 17 | 20-21: 18 19
  # causes: Decreased Energy Cost; target: self
Healer's Boon #1393 | Elite Enchantment Spell | Nightfall | E5 C¼ R10
  For 10..55 seconds. Healing Prayers spells cast 50% faster and heal for 50% more Health.
  ~ Duration :: 0-4: 10 13 16 19 22 | 5-9: 25 28 31 34 37 | 10-14: 40 43 46 49 52 | 15-19: 55 58 61 64 67 | 20-21: 70 73
  # causes: Decreased Activation Time, Increased Healing; target: self
Heaven's Delight #1117 | Spell | Factions | E5 C1 R12
  Heals you and party members within earshot for 15..60 points.
  ~ Healing :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  # causes: Healing; target: self; aoe: earshot; special: duplicate
Holy Haste #1685 | Enchantment Spell | Nightfall | E5 C1 R10
  For 1..60 second[s], your Healing Prayers spells cast 50% faster. This enchantment ends if you cast another enchantment.
  ~ Duration :: 0-4: 1 5 9 13 17 | 5-9: 21 25 29 32 36 | 10-14: 40 44 48 52 56 | 15-19: 60 64 68 72 76 | 20-21: 80 84
  # causes: Decreased Activation Time
Peace and Harmony (PvP) #3448 | Elite Enchantment Spell | Prophecies | E5 C¼ R15
  Target ally loses 0..4 condition[s] and hex[es]. For 1..3 second[s], conditions and hexes expire 90% faster on that ally. All your Smiting Prayers are disabled for 20 seconds.
  ~ # of conditions and hexes :: 0-4: 0 0 1 1 1 | 5-9: 1 2 2 2 2 | 10-14: 3 3 3 3 4 | 15-19: 4 4 5 5 5 | 20-21: 5 6
  ~ Duration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Disable; removes: Condition, Hex spell; target: allies
  ! BUG: Contrary to the description, Peace and Harmony doesn't cause conditions and hexes to expire 90% faster. Instead, all new conditions and hexes, applied during the enchantment, will have their duration reduced by 90%.
  ! BUG: Contrary to the description, Peace and Harmony doesn't cause conditions and hexes to expire 90% faster. Instead, all new conditions and hexes, applied during the enchantment, will have their duration reduced by 90%. [from PvE version page]
Release Enchantments #960 | Spell | Factions | E5 C¼ R5
  Lose all enchantments. Each party member is healed for 5..35 Health for each Monk enchantment lost.
  ~ Healing :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  # causes: Healing; removes: Enchantment; target: self; aoe: party
  ! ANOMALY: When Release Enchantments (or any skill that removes "all enchantments") triggers the damage effects of Mirage Cloak or Aura of Holy Might, it behaves inconsistently compared to skills that remove a specific number of enchantments: Mirage Cloak: Damage will only trigger for a restricted list of Dervish enchantments (Aura of Thorns, Balthazar's Rage, Pious Renewal, Dust Cloak, Staggering Force, Grenth's Fingers, and itself). Aura of Holy Might: Damage will trigger for all Dervish enchantments except Eternal Aura, Shield of Force, Grenth's Aura, and Vow of Revolution. Skills that remove a defined number of enchantments (like Rend Enchantments or standard Dervish teardowns) do not suffer from these restrictions.
Scribe's Insight #1684 | Elite Enchantment Spell | Nightfall | E5 C¼ R20
  For 10..35 seconds, you gain 3 Energy whenever you use a Signet.
  ~ Duration :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  # causes: Energy Gain
Signet of Devotion #293 | Signet | Core | C2 R5
  Heal target ally for 20..120 Health.
  ~ Healing :: 0-4: 20 27 33 40 47 | 5-9: 53 60 67 73 80 | 10-14: 87 93 100 107 113 | 15-19: 120 127 133 140 147 | 20-21: 153 160
  # causes: Healing; target: allies
Smiter's Boon (PvP) #2895 | Enchantment Spell | Eye of the North | E25 C¼ R90
  For 4 seconds, your Smiting Prayers have double the Divine Favor bonus.
  ~ Healing bonus :: 0-4: 0 3 6 10 13 | 5-9: 16 19 22 26 29 | 10-14: 32 35 38 42 45 | 15-19: 48 51 54 58 61 | 20-21: 64 67
Spell Breaker #273 | Elite Enchantment Spell | Core | E15 C1 R45
  For 5..17 seconds, target ally cannot be the target of enemy spells.
  ~ Duration :: 0-4: 5 6 7 7 8 | 5-9: 9 10 11 11 12 | 10-14: 13 14 15 15 16 | 15-19: 17 18 19 19 20 | 20-21: 21 22
Spell Shield #957 | Enchantment Spell | Factions | E10 C1 R30
  For 5..20 seconds, while you are casting spells, foes cannot target you with spells. When Spell Shield ends, all your skills are disabled for 8..4 seconds.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Disabled duration :: 0-4: 8 8 7 7 7 | 5-9: 7 6 6 6 6 | 10-14: 5 5 5 5 4 | 15-19: 4 4 3 3 3 | 20-21: 3 2
  # causes: Disable
  ! ANOMALY: The concise description omits that only enemy spells cannot target you.
Unyielding Aura (PvP) #2891 | Elite Enchantment Spell | Prophecies | E5 U-1 C3 R15
  Bring target dead party member back to life at full Health and full Energy. If you stop maintaining this enchantment or if this enchantment is removed, that party member dies and leaves an exploited corpse. Deaths while enchanted with Unyielding Aura do not incur a death penalty. (50% failure chance with Divine Favor 4 or less.)
  # target: dead party members
  ! ANOMALY: The tiny delay between the target being teleported to the casters location and being resurrected is long enough for an AI to possibly use "We Shall Return!", which takes place before UA's resurrecting effect. [from PvE version page]
  ! ANOMALY: The "random" resurrected party member is almost always the one closest to the caster when the skill is cancelled. You can therefor pick which target to rez by moving on top of the corpse before cancelling. [from PvE version page]
  ! BUG: If you are moving when it ends, the resurrected party member will be teleported to where you started running or where you last changed direction, not to your current position. [from PvE version page]
Watchful Healing #1392 | Enchantment Spell | Nightfall | E5 C1 R10
  For 10 seconds, target ally gains +1..4 Health regeneration. If this skill ends prematurely, that ally gains 30..120 Health.
  ~ Health regeneration :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  ~ Health gain :: 0-4: 30 36 42 48 54 | 5-9: 60 66 72 78 84 | 10-14: 90 96 102 108 114 | 15-19: 120 126 132 138 144 | 20-21: 150 156
  # causes: Health Regeneration, Health Gain; target: allies
Watchful Spirit #255 | Enchantment Spell | Prophecies | E15 U-1 C1 R5
  While you maintain this enchantment, target ally gains +2 Health regeneration. That ally is healed for 30..180 Health when Watchful Spirit ends.
  ~ Healing :: 0-4: 30 40 50 60 70 | 5-9: 80 90 100 110 120 | 10-14: 130 140 150 160 170 | 15-19: 180 190 200 210 220 | 20-21: 230 240
  # causes: Health Regeneration, Healing
  ! BUG: End effect healing is not affected by Unyielding Aura.
Withdraw Hexes #942 | Elite Spell | Factions | E5 C1 R5
  Remove all hexes from target ally and all adjacent allies. This spell takes an additional 2 seconds to recharge for each hex removed in this way. (50% failure chance with Divine Favor 4 or less.)
  # causes: Increased Recharge Time; removes: Hex spell; target: allies; aoe: adjacent

### Monk / Healing Prayers
Cure Hex #2003 | Spell | Eye of the North | E5 C1 R12
  Remove one Hex from target ally. If a Hex was removed, that ally is healed for 30..100 Health.
  ~ Healing :: 0-4: 30 35 39 44 49 | 5-9: 53 58 63 67 72 | 10-14: 77 81 86 91 95 | 15-19: 100 105 109 114 119 | 20-21: 123 128
  # causes: Healing; removes: Hex spell; target: allies
Dwayna's Kiss #283 | Spell | Prophecies | E5 C1 R3
  Heal target other ally for 20..65 Health and an additional 15..40 Health for each enchantment or hex on that ally.
  ~ Healing :: 0-4: 20 23 26 29 32 | 5-9: 35 38 41 44 47 | 10-14: 50 53 56 59 62 | 15-19: 65 68 71 74 77 | 20-21: 80 83
  ~ Additional healing :: 0-4: 15 17 18 20 22 | 5-9: 23 25 27 28 30 | 10-14: 32 33 35 37 38 | 15-19: 40 42 43 45 47 | 20-21: 48 50
  # causes: Healing; target: other allies
Dwayna's Sorrow #838 | Enchantment Spell | Factions | E5 C1 R5
  For 30 seconds, target ally and all nearby allies are enchanted with Dwayna's Sorrow. If an ally dies while under the effects of Dwayna's Sorrow, your party is healed for 5..50.
  ~ Healing :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Healing; target: allies
Ethereal Light #959 | Spell | Factions | E5 C1 R5
  Target ally is healed for 25..100. This spell is easily interrupted.
  ~ Healing :: 0-4: 25 30 35 40 45 | 5-9: 50 55 60 65 70 | 10-14: 75 80 85 90 95 | 15-19: 100 105 110 115 120 | 20-21: 125 130
  # causes: Healing; target: allies
Gift of Health #1121 | Spell | Factions | E5 C¾ R5
  All of your other Healing Prayers skills are disabled for 10..5 seconds. Target other ally is healed for 15..150 Health.
  ~ Disabled :: 0-4: 10 10 9 9 9 | 5-9: 8 8 8 7 7 | 10-14: 7 6 6 6 5 | 15-19: 5 5 4 4 4 | 20-21: 3 3
  ~ Healing :: 0-4: 15 24 33 42 51 | 5-9: 60 69 78 87 96 | 10-14: 105 114 123 132 141 | 15-19: 150 159 168 177 186 | 20-21: 195 204
  # causes: Healing, Disable; target: other allies
Glimmer of Light #1686 | Elite Spell | Nightfall | E5 C¼ R1
  Heal target ally for 10..115 Health.
  ~ Healing :: 0-4: 10 17 24 31 38 | 5-9: 45 52 59 66 73 | 10-14: 80 87 94 101 108 | 15-19: 115 122 129 136 143 | 20-21: 150 157
  # causes: Healing; target: allies
Heal Area #280 | Spell | Prophecies | E10 C1 R5
  Heal yourself and all adjacent creatures for 30..180 points.
  ~ Healing :: 0-4: 30 40 50 60 70 | 5-9: 80 90 100 110 120 | 10-14: 130 140 150 160 170 | 15-19: 180 190 200 210 220 | 20-21: 230 240
  # causes: Healing; target: untargeted; aoe: adjacent; special: duplicate
  ! ANOMALY: Even though this skill has the same description as Karei's Healing Circle, they have different concise descriptions.
Heal Other #286 | Spell | Prophecies | E10 C¾ R3
  Heal target other ally for 35..180 Health.
  ~ Healing :: 0-4: 35 45 54 64 74 | 5-9: 83 93 103 112 122 | 10-14: 132 141 151 161 170 | 15-19: 180 190 199 209 219 | 20-21: 228 238
  # causes: Healing; target: other allies; special: duplicate
Heal Party (PvP) #3232 | Spell | Core | E15 C1 R10
  Heal entire party for 30..75 Health.
  ~ Healing :: 0-4: 30 33 36 39 42 | 5-9: 45 48 51 54 57 | 10-14: 60 63 66 69 72 | 15-19: 75 78 81 84 87 | 20-21: 90 93
  # causes: Healing; target: self; aoe: party
Healer's Covenant #1394 | Elite Enchantment Spell | Nightfall | E5 U-1 C¼ R5
  While you maintain this enchantment, your Healing Prayers spells heal for 20% less Health, but cost -1..4 Energy.
  ~ Energy reduction :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  # causes: Decreased Energy Cost; target: self
Healing Breeze #288 | Enchantment Spell | Core | E10 C1 R5
  For 15 seconds, target ally gains +4..9 Health regeneration.
  ~ Health regeneration :: 0-4: 4 4 5 5 5 | 5-9: 6 6 6 7 7 | 10-14: 7 8 8 8 9 | 15-19: 9 9 10 10 10 | 20-21: 11 11
  # causes: Health Regeneration
Healing Burst #1118 | Elite Spell | Factions | E5 C¾ R6
  Target ally is healed for 20..120. All party members in earshot of your target gain Health equal to the Divine Favor bonus from this spell. Your Smiting Prayers are disabled for 20 seconds.
  ~ Healing :: 0-4: 20 27 33 40 47 | 5-9: 53 60 67 73 80 | 10-14: 87 93 100 107 113 | 15-19: 120 127 133 140 147 | 20-21: 153 160
  ~ Party healing :: 0-4: 0 3 6 10 13 | 5-9: 16 19 22 26 29 | 10-14: 32 35 38 42 45 | 15-19: 48 51 54 58 61 | 20-21: 64 67
  # causes: Healing, Disable; target: allies; aoe: earshot
  ! BUG: Contrary to the descriptions, this skill causes healing in earshot and not health gain.
Healing Hands #285 | Elite Enchantment Spell | Prophecies | E5 C¼ R15
  For 10 seconds, whenever target ally takes damage, that ally is healed for 5..35 Health.
  ~ Health gain :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  # causes: Health Gain; target: allies
  ! BUG: Contrary to the descriptions, this skill causes health gain and not healing.
Healing Light #867 | Elite Spell | Factions | E5 C¾ R4
  Heal target ally for 40..120 Health. If your target has an enchantment, you gain 1..3 Energy.
  ~ Healing :: 0-4: 40 45 51 56 61 | 5-9: 67 72 77 83 88 | 10-14: 93 99 104 109 115 | 15-19: 120 125 131 136 141 | 20-21: 147 152
  ~ Energy gain :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Healing, Energy Gain; target: allies
Healing Ribbon #2062 | Spell | Eye of the North | E10 C1 R5
  Target other ally is healed for 20..110 Health. Up to 2 additional allies near target ally are healed for 10..100 Health.
  ~ Healing :: 0-4: 20 26 32 38 44 | 5-9: 50 56 62 68 74 | 10-14: 80 86 92 98 104 | 15-19: 110 116 122 128 134 | 20-21: 140 146
  ~ Additional healing :: 0-4: 10 16 22 28 34 | 5-9: 40 46 52 58 64 | 10-14: 70 76 82 88 94 | 15-19: 100 106 112 118 124 | 20-21: 130 136
  # causes: Healing; target: other allies; aoe: nearby
Healing Ring #1262 | Spell | Nightfall | E5 C1 R10
  Heal adjacent creatures for 30..180 Health. The caster is not healed.
  ~ Healing :: 0-4: 30 40 50 60 70 | 5-9: 80 90 100 110 120 | 10-14: 130 140 150 160 170 | 15-19: 180 190 200 210 220 | 20-21: 230 240
  # causes: Healing; target: untargeted; aoe: adjacent
Healing Seed #274 | Enchantment Spell | Core | E10 C2 R25
  For 10 seconds, whenever target other ally takes damage, that ally and all adjacent allies gain 3..30 Health.
  ~ Health gain :: 0-4: 3 5 7 8 10 | 5-9: 12 14 16 17 19 | 10-14: 21 23 25 26 28 | 15-19: 30 32 34 35 37 | 20-21: 39 41
  # causes: Health Gain; target: other allies; aoe: adjacent
  ! ANOMALY: This skill seems to also cause miniatures to gain health.
Healing Touch #313 | Touch spell | Core | E5 C¾ R5
  Spell. Heal target touched ally for 20..80 Health. Health gain from Divine Favor is doubled for this spell.
  ~ Healing :: 0-4: 20 24 28 32 36 | 5-9: 40 44 48 52 56 | 10-14: 60 64 68 72 76 | 15-19: 80 84 88 92 96 | 20-21: 100 104
  # causes: Healing; target: allies; range: touch
Healing Whisper #958 | Spell | Factions | E5 C1 R1
  Target other ally is healed for 40..100. This spell has half the normal range.
  ~ Healing :: 0-4: 40 44 48 52 56 | 5-9: 60 64 68 72 76 | 10-14: 80 84 88 92 96 | 15-19: 100 104 108 112 116 | 20-21: 120 124
  # causes: Healing; target: other allies; range: half
Infuse Health #292 | Spell | Core | E10 C¼
  Lose half your current Health. Target other ally is healed for 100..136% of the amount you lost.
  ~ % Healing :: 0-4: 100 102 105 107 110 | 5-9: 112 114 117 119 122 | 10-14: 124 126 129 131 134 | 15-19: 136 138 141 143 146 | 20-21: 148 150
  # causes: Healing, Health Loss; target: other allies
Jamei's Gaze #1120 | Spell | Factions | E10 C¾ R3
  Heal target other ally for 35..180 Health.
  ~ Healing :: 0-4: 35 45 54 64 74 | 5-9: 83 93 103 112 122 | 10-14: 132 141 151 161 170 | 15-19: 180 190 199 209 219 | 20-21: 228 238
  # causes: Healing; target: other allies; special: duplicate
Karei's Healing Circle #1119 | Spell | Factions | E10 C1 R5
  Heal yourself and all adjacent creatures for 30..180 points.
  ~ Healing :: 0-4: 30 40 50 60 70 | 5-9: 80 90 100 110 120 | 10-14: 130 140 150 160 170 | 15-19: 180 190 200 210 220 | 20-21: 230 240
  # causes: Healing; target: untargeted; aoe: adjacent; special: duplicate
  ! ANOMALY: Even though this has the exact same description as Heal Area, this has a different concise description.
Light of Deliverance (PvP) #2871 | Elite Spell | Nightfall | E5 C1 R8
  All party members are healed for 5..70 Health. All your Smiting Prayers are disabled for 20 seconds.
  ~ Healing :: 0-4: 5 9 14 18 22 | 5-9: 27 31 35 40 44 | 10-14: 48 53 57 61 66 | 15-19: 70 74 79 83 87 | 20-21: 92 96
  # causes: Healing, Disable; target: self; aoe: party
Live Vicariously #291 | Enchantment Spell | Prophecies | E5 U-1 C2
  While you maintain this enchantment, whenever target ally hits a foe, you gain 2..17 Health.
  ~ Health gain :: 0-4: 2 3 4 5 6 | 5-9: 7 8 9 10 11 | 10-14: 12 13 14 15 16 | 15-19: 17 18 19 20 21 | 20-21: 22 23
  # causes: Health Gain; target: allies
Mending #290 | Enchantment Spell | Core | E10 U-1 C2
  While you maintain this enchantment, target ally gains +1..4 Health regeneration.
  ~ Health regeneration :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  # causes: Health Regeneration; target: allies
Orison of Healing #281 | Spell | Core | E5 C1 R2
  Heal target ally for 30..80 Health.
  ~ Healing :: 0-4: 30 33 37 40 43 | 5-9: 47 50 53 57 60 | 10-14: 63 67 70 73 77 | 15-19: 80 83 87 90 93 | 20-21: 97 100
  # causes: Healing; target: allies
Patient Spirit #2061 | Enchantment Spell | Eye of the North | E5 C¼ R4
  For 2 seconds, target ally is enchanted with Patient Spirit. Unless this enchantment ends prematurely, that ally is healed for 30..120 Health when the enchantment ends.
  ~ Healing :: 0-4: 30 36 42 48 54 | 5-9: 60 66 72 78 84 | 10-14: 90 96 102 108 114 | 15-19: 120 126 132 138 144 | 20-21: 150 156
  # causes: Healing; target: allies
Renew Life #1263 | Touch spell | Nightfall | E15 C4 R5
  Spell. Resurrect target touched dead target party member with 50% Health and 5..20% Energy. That party member and all allies within earshot are healed for 55..130 Health.
  ~ % Energy :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Healing :: 0-4: 55 60 65 70 75 | 5-9: 80 85 90 95 100 | 10-14: 105 110 115 120 125 | 15-19: 130 135 140 145 150 | 20-21: 155 160
  # causes: Healing; target: dead party members; range: touch; aoe: earshot
Restful Breeze #886 | Enchantment Spell | Nightfall | E5 C1 R8
  For 8..18 seconds, target ally has +10 Health regeneration. This enchantment ends if that ally attacks or uses a skill.
  ~ Duration :: 0-4: 8 9 9 10 11 | 5-9: 11 12 13 13 14 | 10-14: 15 15 16 17 17 | 15-19: 18 19 19 20 21 | 20-21: 21 22
  # causes: Health Regeneration; target: allies
Restore Life #314 | Touch spell | Prophecies | E10 C4 R8
  Spell. Touch the body of a fallen party member. Target party member is returned to life with 20..65% Health and 42..90% Energy.
  ~ % Health :: 0-4: 20 23 26 29 32 | 5-9: 35 38 41 44 47 | 10-14: 50 53 56 59 62 | 15-19: 65 68 71 74 77 | 20-21: 80 83
  ~ % Energy :: 0-4: 42 45 48 52 55 | 5-9: 58 61 64 68 71 | 10-14: 74 77 80 84 87 | 15-19: 90 93 96 100 103 | 20-21: 106 109
  # target: dead party members; range: touch
Resurrection Chant #1128 | Spell | Factions | E10 C6 R15
  Resurrect target party member with up to your current Health and 5..35% Energy. This spell has half the normal range.
  ~ % Energy :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  # target: dead party members; range: half; special: Resurrection
Signet of Rejuvenation #887 | Signet | Factions | C1 R8
  Heal target ally for 15..75. If target ally is casting a spell or attacking, that ally is healed for an additional 15..75 Health.
  ~ Healing :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  ~ Additional healing :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  ~ Total healing :: 0-4: 30 38 46 54 62 | 5-9: 70 78 86 94 102 | 10-14: 110 118 126 134 142 | 15-19: 150 158 166 174 182 | 20-21: 190 198
  # causes: Healing; target: allies
Spotless Mind #2064 | Enchantment Spell | Eye of the North | E5 C¼ R12
  For 1..15 seconds, target other ally loses a hex every 5 seconds.
  ~ Duration :: 0-4: 1 2 3 4 5 | 5-9: 6 7 8 8 9 | 10-14: 10 11 12 13 14 | 15-19: 15 16 17 18 19 | 20-21: 20 21
  # removes: Hex spell; target: other allies
Spotless Soul #2065 | Enchantment Spell | Eye of the North | E5 C¼ R12
  For 1..15 seconds, target other ally loses a condition every 3 seconds.
  ~ Duration :: 0-4: 1 2 3 4 5 | 5-9: 6 7 8 8 9 | 10-14: 10 11 12 13 14 | 15-19: 15 16 17 18 19 | 20-21: 20 21
  # removes: Condition; target: other allies
Supportive Spirit #1391 | Enchantment Spell | Nightfall | E10 C¾ R8
  For 5..23 seconds, whenever target ally takes damage while knocked down, that ally is healed for 5..50 Health.
  ~ Duration :: 0-4: 5 6 7 9 10 | 5-9: 11 12 13 15 16 | 10-14: 17 18 19 21 22 | 15-19: 23 24 25 27 28 | 20-21: 29 30
  ~ Healing :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Healing; target: allies
Vigorous Spirit #254 | Enchantment Spell | Prophecies | E5 C¼ R4
  For 30 seconds, each time target ally attacks or casts a spell, that ally is healed for 5..20 Health.
  ~ Healing :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Healing; target: allies
  ! ANOMALY: Empathy triggers on failed attack skills, whereas Vigorous Spirit does not.
Word of Healing #282 | Elite Spell | Core | E5 C¾ R3
  Heal target ally for 5..100 Health. Heal for an additional 30..115 Health if that ally is below 50% Health.
  ~ Healing :: 0-4: 5 11 18 24 30 | 5-9: 37 43 49 56 62 | 10-14: 68 75 81 87 94 | 15-19: 100 106 113 119 125 | 20-21: 132 138
  ~ Additional healing :: 0-4: 30 36 41 47 53 | 5-9: 58 64 70 75 81 | 10-14: 87 92 98 104 109 | 15-19: 115 121 126 132 138 | 20-21: 143 149
  ~ Total healing :: 0-4: 35 47 59 71 83 | 5-9: 95 107 119 131 143 | 10-14: 155 167 179 191 203 | 15-19: 215 227 239 251 263 | 20-21: 275 287
  # causes: Healing; target: allies
Words of Comfort #1396 | Spell | Nightfall | E5 C1 R4
  Target ally is healed for 20..65 Health and an additional 20..50 Health if that ally is suffering from a condition.
  ~ Healing :: 0-4: 20 23 26 29 32 | 5-9: 35 38 41 44 47 | 10-14: 50 53 56 59 62 | 15-19: 65 68 71 74 77 | 20-21: 80 83
  ~ + Healing :: 0-4: 20 22 24 26 28 | 5-9: 30 32 34 36 38 | 10-14: 40 42 44 46 48 | 15-19: 50 52 54 56 58 | 20-21: 60 62
  ~ Total Healing :: 0-4: 40 45 50 55 60 | 5-9: 65 70 75 80 85 | 10-14: 90 95 100 105 110 | 15-19: 115 120 125 130 135 | 20-21: 140 145
  # causes: Healing; target: allies

### Monk / No Attribute
Empathic Removal #1126 | Elite Spell | Factions | E5 C1 R7
  You and target other ally lose 1 condition and 1 hex, and are healed for 50.
  # causes: Healing; removes: Condition, Hex spell; target: other allies
  ! ANOMALY: Unlike other healing skills, this spell can target spirits to remove burning. However, Empathic Removal will not heal the spirits.
Essence Bond #250 | Enchantment Spell | Prophecies | E10 U-1 C2
  While you maintain this enchantment, whenever target ally takes physical or elemental damage, you gain 1 Energy.
  # causes: Energy Gain; target: allies
Holy Veil #309 | Enchantment Spell | Core | E5 U-1 C1 R12
  While you maintain this enchantment, any hex cast on target ally takes twice as long to cast. When Holy Veil ends, one hex is removed from target ally.
  # causes: Increased Activation Time; removes: Hex spell; target: allies
Light of Dwayna #304 | Spell | Prophecies | E25 C4 R20
  Resurrect all dead party members in the area. They are returned to life with 25% Health and zero Energy.
  # target: self; aoe: in the area
Martyr #298 | Elite Spell | Core | E5 C¼ R10
  Transfer all conditions and their remaining durations from your allies to you.
  # causes: Condition; removes: condition; target: self; aoe: party
Purge Conditions #278 | Spell | Core | E5 C¼ R20
  Remove all conditions (Poison, Disease, Blindness, Dazed, Bleeding, Crippled, Burning, Weakness, Cracked Armor, and Deep Wound) from target ally.
  # removes: Condition; target: allies
Purge Signet #295 | Signet | Core | C2 R20
  Remove all hexes and conditions from target ally. You lose 10 Energy for each hex and each condition removed.
  # causes: Energy Loss; removes: Condition, Hex spell; target: allies; range: casting
Remove Hex #301 | Spell | Core | E5 C1 R8
  Remove a hex from target ally.
  # removes: Hex spell; target: allies
Resurrect #305 | Spell | Core | E10 C5 R8
  Resurrect target party member. Target party member is returned to life with 25% Health and zero Energy.
  # target: dead party members
Signet of Removal #1690 | Elite Signet | Nightfall | C¼ R5
  If target ally is under the effects of an enchantment, that ally loses one hex and one condition.
  # removes: Condition, Hex spell; target: allies; range: casting
Succor #308 | Enchantment Spell | Prophecies | E5 U-1 C1 R10
  While you maintain this Enchantment, target other ally gains +1 Health and +1 Energy regeneration, but you lose 1 Energy each time that ally casts a Spell.
  # causes: Health Regeneration, Energy Regeneration, Energy Loss; target: other allies
Vengeance #315 | Enchantment Spell | Prophecies | E10 C4 R30
  Bring target dead party member back to life at full Health and full Energy. For 30 seconds, that party member deals 25% more damage. When this enchantment ends, target party member dies. Deaths while under the effects of this enchantment do not incur a death penalty.
  # target: dead party members
  ! ANOMALY: This skill's duration can only be extended by any of Enchanting modifier on the target's weapon. The caster's weapon and buffs like Blessed Aura do not extend the duration.

### Monk / Protection Prayers
Aegis (PvP) #2857 | Enchantment Spell | Core | E10 C¼ R30
  For 1..3 seconds, target other party member cannot be the target of hostile spells, and attacks against this party member fail.
  ~ Duration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # target: other allies
Air of Enchantment #1115 | Elite Enchantment Spell | Factions | E5 C¼ R8
  For 4..10 seconds, enchantments cast on target other ally cost 10 less Energy (minimum 1 Energy).
  ~ Duration :: 0-4: 4 4 5 5 6 | 5-9: 6 6 7 7 8 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 12
  # causes: Decreased Energy Cost; target: other allies; aoe: none
Amity #265 | Elite Hex Spell | Prophecies | E5 C¼ R20
  For 4..12 seconds, adjacent foes cannot attack. For each foe, Amity ends if that foe takes damage.
  ~ Duration :: 0-4: 4 5 5 6 6 | 5-9: 7 7 8 8 9 | 10-14: 9 10 10 11 11 | 15-19: 12 13 13 14 14 | 20-21: 15 15
  # target: untargeted; aoe: adjacent
Aura of Faith #260 | Elite Enchantment Spell | Prophecies | E5 C¼ R8
  For 3 seconds, target ally gains 50..100% more Health when healed and takes 5..50% less damage.
  ~ % extra Healing :: 0-4: 50 53 57 60 63 | 5-9: 67 70 73 77 80 | 10-14: 83 87 90 93 97 | 15-19: 100 103 107 110 113 | 20-21: 117 120
  ~ % less damage :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Damage Reduction
Aura of Stability #2063 | Enchantment Spell | Eye of the North | E5 C¼ R12
  For 3..8 seconds, target other ally cannot be knocked down.
  ~ Duration :: 0-4: 3 3 4 4 4 | 5-9: 5 5 5 6 6 | 10-14: 6 7 7 7 8 | 15-19: 8 8 9 9 9 | 20-21: 10 10
  # causes: Knockdown Immunity; target: other allies
Convert Hexes #303 | Spell | Core | E15 C1 R12
  Remove all hexes from target other ally. For 8..20 seconds, that ally gains +10 armor for each Necromancer hex that was removed.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  # causes: Increased Armor Rating; removes: Hex spell; target: other allies
  ! BUG: Convert Hexes only grants +10 armor, whether it removes one or more Necromancer hexes.
Dismiss Condition #1691 | Spell | Nightfall | E5 C¾ R3
  Remove one condition from target ally. If that ally is under the effects of an enchantment, that ally is healed for 15..75 Health.
  ~ Healing :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  # causes: Healing; removes: Condition; target: allies
  ! ANOMALY: Unlike most other skills with a healing component, Dismiss Condition can target spirits.
Divert Hexes #1692 | Elite Spell | Nightfall | E5 C¾ R8
  Remove up to 1..3 hex[es] from target ally. For each hex removed in this way, that ally loses one condition and gains 15..75 Health.
  ~ Hexes removed :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  ~ Health gain :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  # causes: Health Gain; removes: Hex spell, Condition
Draw Conditions #311 | Spell | Core | E5 C¼ R4
  All negative conditions are transferred from target other ally to yourself. For each condition acquired, you gain 6..26 Health.
  ~ Health gain :: 0-4: 6 7 9 10 11 | 5-9: 13 14 15 17 18 | 10-14: 19 21 22 23 25 | 15-19: 26 27 29 30 31 | 20-21: 33 34
  # causes: Condition, Health Gain; removes: Condition; target: other allies
Extinguish #943 | Spell | Factions | E15 C1 R12
  Remove one condition from each party member. Party members relieved of Burning are healed for 10..100 Health.
  ~ Healing :: 0-4: 10 16 22 28 34 | 5-9: 40 46 52 58 64 | 10-14: 70 76 82 88 94 | 15-19: 100 106 112 118 124 | 20-21: 130 136
  # causes: Healing; removes: Condition; aoe: party
  ! ANOMALY: Heroes only use Extinguish on allies within their aggro circle, even though the skill works within compass range.
Guardian #258 | Enchantment Spell | Core | E5 C1 R6
  For 2..7 seconds, target ally has a 50% chance to block attacks.
  ~ Duration :: 0-4: 2 2 3 3 3 | 5-9: 4 4 4 5 5 | 10-14: 5 6 6 6 7 | 15-19: 7 7 8 8 8 | 20-21: 9 9
  # causes: Block; target: allies
Life Attunement #244 | Enchantment Spell | Prophecies | E10 U-1 C2
  While you maintain this enchantment, target ally deals 30% less damage with attacks, but gains 14..50% more Health when healed.
  ~ Percentage :: 0-4: 14 16 19 21 24 | 5-9: 26 28 31 33 36 | 10-14: 38 40 43 45 48 | 15-19: 50 52 55 57 60 | 20-21: 62 64
  ! ANOMALY: Similar to Flurry, the damage reduction only applies to the equipped weapon's base damage. It will not reduce damage dealt by skills or effects, not even bonus damage from attack skills.
Life Barrier #270 | Elite Enchantment Spell | Prophecies | E15 U-1 C2 R5
  While you maintain this enchantment, damage dealt to target other ally is reduced by 20..50%. If your Health is below 50% when that ally takes damage, Life Barrier ends.
  ~ % Damage reduction :: 0-4: 20 22 24 26 28 | 5-9: 30 32 34 36 38 | 10-14: 40 42 44 46 48 | 15-19: 50 52 54 56 58 | 20-21: 60 62
  # causes: Damage Reduction; target: other allies
Life Bond #241 | Enchantment Spell | Core | E10 U-1 C2
  While you maintain this enchantment, whenever target other ally takes damage from an attack, half the damage is redirected to you. The damage you receive this way is reduced by 3..30.
  ~ Damage reduction :: 0-4: 3 5 7 8 10 | 5-9: 12 14 16 17 19 | 10-14: 21 23 25 26 28 | 15-19: 30 32 34 35 37 | 20-21: 39 41
  # causes: Damage Reduction; target: other allies
Life Sheath #1123 | Elite Enchantment Spell | Factions | E5 C¼ R2
  Remove 0..2 condition[s] from target ally. For 8 seconds, the next time that ally would take damage or life steal, that ally gains that amount of Health instead (maximum 20..100).
  ~ Conditions removed :: 0-4: 0 0 0 0 1 | 5-9: 1 1 1 1 1 | 10-14: 1 1 2 2 2 | 15-19: 2 2 2 2 3 | 20-21: 3 3
  ~ Maximum healing :: 0-4: 20 25 31 36 41 | 5-9: 47 52 57 63 68 | 10-14: 73 79 84 89 95 | 15-19: 100 105 111 116 121 | 20-21: 127 132
  # causes: Healing; removes: Condition; target: allies
  ! ANOMALY: Contrary to the full description, this skill causes healing and not health gain.
Mark of Protection #269 | Elite Enchantment Spell | Prophecies | E10 C¼ R15
  For 10 seconds, whenever target ally would take damage, that ally is healed for that amount instead, maximum 6..60. All your Protection Prayers are disabled for 5 seconds.
  ~ Maximum healing :: 0-4: 6 10 13 17 20 | 5-9: 24 28 31 35 38 | 10-14: 42 46 49 53 56 | 15-19: 60 64 67 71 74 | 20-21: 78 82
  # causes: Damage Reduction, Healing
  ! ANOMALY: Contrary to the description, this skill causes health gain and not healing.
Mend Ailment #277 | Spell | Core | E5 C¾ R5
  Remove one condition (Poison, Disease, Blindness, Dazed, Bleeding, Crippled, Burning, Weakness, Cracked Armor, or Deep Wound) from target ally. For each remaining Condition, that ally is healed for 5..70 Health.
  ~ Healing :: 0-4: 5 9 14 18 22 | 5-9: 27 31 35 40 44 | 10-14: 48 53 57 61 66 | 15-19: 70 74 79 83 87 | 20-21: 92 96
  # causes: Healing; removes: Condition; target: allies
Mend Condition #275 | Spell | Prophecies | E5 C¾ R2
  Remove one condition (Poison, Disease, Blindness, Dazed, Bleeding, Crippled, Burning, Weakness, Cracked Armor, or Deep Wound) from target other ally. If a condition is removed, that ally is healed for 5..70 Health.
  ~ Health :: 0-4: 5 9 14 18 22 | 5-9: 27 31 35 40 44 | 10-14: 48 53 57 61 66 | 15-19: 70 74 79 83 87 | 20-21: 92 96
  # causes: Healing; removes: Condition; target: other allies
Mending Touch #1401 | Touch spell | Nightfall | E5 C¾ R6
  Spell. Touched ally loses two conditions and is healed for 15..60 Health for each condition removed in this way.
  ~ Healing :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  # causes: Healing; removes: Condition; range: touch
Pacifism #264 | Hex Spell | Prophecies | E10 C2 R15
  For 4..8 seconds, target foe cannot attack. This effect ends if the target takes damage.
  ~ Duration :: 0-4: 8 8 8 8 8 | 5-9: 8 8 8 8 8 | 10-14: 8 8 8 8 8 | 15-19: 8 8 8 8 8 | 20-21: 8 8
  ~ (4..8) [derived] :: 0-4: 4 4 5 5 5 | 5-9: 5 6 6 6 6 | 10-14: 7 7 7 7 8 | 15-19: 8 8 9 9 9 | 20-21: 9 10
Pensive Guardian #1683 | Enchantment Spell | Nightfall | E5 C1 R5
  For 5..11 seconds, target ally has a 50% chance to block attacks from enchanted foes.
  ~ Duration :: 0-4: 5 5 6 6 7 | 5-9: 7 7 8 8 9 | 10-14: 9 9 10 10 11 | 15-19: 11 11 12 12 13 | 20-21: 13 13
  # causes: Block
Protective Bond #263 | Enchantment Spell | Prophecies | E10 U-1 C2
  While you maintain this enchantment, target ally cannot lose more than 5% max Health due to damage from a single attack or spell. When Protective Bond prevents damage, you lose 6..3 Energy or the spell ends.
  ~ Energy loss :: 0-4: 6 6 6 5 5 | 5-9: 5 5 5 4 4 | 10-14: 4 4 4 3 3 | 15-19: 3 3 3 2 2 | 20-21: 2 2
  # causes: Damage Reduction, Energy Loss
Protective Spirit #245 | Enchantment Spell | Core | E10 C¼ R5
  For 5..23 seconds, target ally cannot lose more than 10% max Health due to damage from a single attack or spell.
  ~ Duration :: 0-4: 5 6 7 9 10 | 5-9: 11 12 13 15 16 | 10-14: 17 18 19 21 22 | 15-19: 23 24 25 27 28 | 20-21: 29 30
  # causes: Damage Reduction; target: allies
Purifying Veil #2007 | Enchantment Spell | Eye of the North | E5 U-1 C1 R6
  While you maintain this enchantment, conditions expire 5..50% faster on target ally. When this enchantment ends, one condition is removed from that ally.
  ~ Faster condition expiration % :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # removes: Condition
Rebirth #306 | Spell | Core | E10 C5
  Resurrect target party member. Target party member is returned to life with 25% Health and zero Energy, and is teleported to your current location. All of target's skills are disabled for 10..3 seconds. This spell consumes all of your remaining Energy.
  ~ Disabled duration :: 0-4: 10 10 9 9 8 | 5-9: 8 7 7 6 6 | 10-14: 5 5 4 4 3 | 15-19: 3 3 2 2 1 | 20-21: 1 0
  # causes: Disable, Energy Loss, Shadow Step; target: dead party members; range: casting
Restore Condition #276 | Elite Spell | Prophecies | E5 C¾ R2
  Remove all conditions (Poison, Disease, Blindness, Dazed, Bleeding, Crippled, Burning, Weakness, Cracked Armor, and Deep Wound) from target other ally. For each condition removed, that ally is healed for 10..70 Health.
  ~ Healing :: 0-4: 10 14 18 22 26 | 5-9: 30 34 38 42 46 | 10-14: 50 54 58 62 66 | 15-19: 70 74 78 82 86 | 20-21: 90 94
  # causes: Healing; removes: Condition; target: other allies
Reversal of Fortune #307 | Enchantment Spell | Core | E5 C¼ R2
  For 8 seconds, the next time target ally would take damage or life steal, that ally gains that amount of Health instead, maximum 15..80.
  ~ Maximum healing :: 0-4: 15 19 24 28 32 | 5-9: 37 41 45 50 54 | 10-14: 58 63 67 71 76 | 15-19: 80 84 89 93 97 | 20-21: 102 106
  # causes: Damage Reduction, Healing; target: allies
  ! ANOMALY: Contrary to the full description, this skill causes healing and not health gain.
Reverse Hex #848 | Enchantment Spell | Factions | E10 C¼ R10
  Remove one hex from target ally. If a hex was removed in this way, for 5..10 seconds, the next time target ally would take damage, that damage is reduced by 5..50.
  ~ Duration :: 0-4: 5 5 6 6 6 | 5-9: 7 7 7 8 8 | 10-14: 8 9 9 9 10 | 15-19: 10 10 11 11 11 | 20-21: 12 12
  ~ Damage reduction :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Damage Reduction; removes: Hex spell; target: allies
Shield Guardian (PvP) #3454 | Enchantment Spell | Factions | E5 R25
  For 1..4 seconds, all party members in earshot have a 75% chance to block incoming attacks. If an attack is blocked, all allies in earshot are healed for 10..35 and Shield Guardian ends.
  ~ Duration :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  ~ Healing :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  # causes: Block, Healing; target: self; aoe: earshot
Shield of Absorption #1399 | Enchantment Spell | Nightfall | E5 C1 R10
  For 3..7 seconds, damage received by target ally is reduced by 5 each time that ally is hit while under the effects of this enchantment.
  ~ Duration :: 0-4: 3 3 4 4 4 | 5-9: 4 5 5 5 5 | 10-14: 6 6 6 6 7 | 15-19: 7 7 8 8 8 | 20-21: 8 9
  # causes: Damage Reduction
Shield of Deflection #259 | Elite Enchantment Spell | Prophecies | E10 C¼ R5
  For 3..10 seconds, target ally has a 75% chance to block attacks and gains 15..30 armor.
  ~ Duration :: 0-4: 3 3 4 4 5 | 5-9: 5 6 6 7 7 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 13
  ~ + Armor rating :: 0-4: 15 16 17 18 19 | 5-9: 20 21 22 23 24 | 10-14: 25 26 27 28 29 | 15-19: 30 31 32 33 34 | 20-21: 35 36
  # causes: Block, Increased Armor Rating
Shield of Regeneration #261 | Elite Enchantment Spell | Core | E10 C¼ R8
  For 5..13 seconds, target ally gains +3..10 Health regeneration and 20..45 armor.
  ~ Duration :: 0-4: 5 6 6 7 7 | 5-9: 8 8 9 9 10 | 10-14: 10 11 11 12 12 | 15-19: 13 14 14 15 15 | 20-21: 16 16
  ~ Health regeneration :: 0-4: 3 3 4 4 5 | 5-9: 5 6 6 7 7 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 13
  ~ Armor :: 0-4: 20 22 23 25 27 | 5-9: 28 30 32 33 35 | 10-14: 37 38 40 42 43 | 15-19: 45 47 48 50 52 | 20-21: 53 55
  # causes: Health Regeneration, Increased Armor Rating
Shielding Hands #299 | Enchantment Spell | Core | E5 C¼ R15
  For 8 seconds, damage and life steal received by target ally is reduced by 3..18. When Shielding Hands ends, that ally is healed for 5..50 Health.
  ~ Damage reduction :: 0-4: 3 4 5 6 7 | 5-9: 8 9 10 11 12 | 10-14: 13 14 15 16 17 | 15-19: 18 19 20 21 22 | 20-21: 23 24
  ~ Healing :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Damage Reduction, Healing; target: allies
Spirit Bond (PvP) #2892 | Enchantment Spell | Factions | E10 C¼ R5
  For 8 seconds, whenever target ally takes more than 50 damage from the next 10 attacks or spells, that ally is healed for 30..90 Health.
  ~ Healing :: 0-4: 30 34 38 42 46 | 5-9: 50 54 58 62 66 | 10-14: 70 74 78 82 86 | 15-19: 90 94 98 102 106 | 20-21: 110 114
  # causes: Healing; target: allies
  ! BUG: Contrary to the descriptions, Spirit Bond will only end prematurely if it triggers ten times. [from PvE version page]
  ! ANOMALY: Despite causing healing, triggering the healing from the skill does not cause Scourge Healing or Soul Bind to inflict damage. [from PvE version page]
Vital Blessing #289 | Enchantment Spell | Prophecies | E10 U-1 C¾ R2
  While you maintain this enchantment, target ally has +40..200 maximum Health.
  ~ + Maximum health :: 0-4: 40 51 61 72 83 | 5-9: 93 104 115 125 136 | 10-14: 147 157 168 179 189 | 15-19: 200 211 221 232 243 | 20-21: 253 264
  # causes: Increased Maximum Health; target: allies
Zealous Benediction #1687 | Elite Spell | Nightfall | E10 C¾ R4
  Heal target ally for 30..180 Health. If target was below 50% Health, you gain 7 Energy.
  ~ Healing :: 0-4: 30 40 50 60 70 | 5-9: 80 90 100 110 120 | 10-14: 130 140 150 160 170 | 15-19: 180 190 200 210 220 | 20-21: 230 240
  # causes: Healing, Energy Gain

### Monk / Smiting Prayers
Balthazar's Aura #272 | Enchantment Spell | Core | E15 C1 R20
  For 8 seconds, foes adjacent to target ally take 10..30 holy damage each second.
  ~ Holy damage :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  # causes: Holy Damage; target: allies; aoe: adjacent
Balthazar's Pendulum #1395 | Elite Enchantment Spell | Nightfall | E5 C¼ R5
  For 5..25 seconds, the next time target ally would be knocked down by a foe, that foe is knocked down instead.
  ~ Duration :: 0-4: 5 5 6 6 6 | 5-9: 7 7 7 8 8 | 10-14: 8 9 9 9 10 | 15-19: 10 10 11 11 11 | 20-21: 12 12
  ~ (5..25) [derived] :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  # causes: Knockdown, Knockdown Immunity; target: allies
  ! BUG: Doesn't work against Psychic Instability or Tremor.
Balthazar's Spirit #242 | Enchantment Spell | Prophecies | E10 U-1 C2
  While you maintain this enchantment, target ally gains adrenaline and 1 Energy after taking damage. (The amount of adrenaline gained increases depending on your rank in Smiting Prayers.)
  ~ Adrenaline points :: 0-4: 2 2 2 3 3 | 5-9: 3 3 3 4 4 | 10-14: 4 4 4 5 5 | 15-19: 5 5 5 6 6 | 20-21: 6 6
  # causes: Adrenaline Gain, Energy Gain
Bane Signet #296 | Signet | Core | C1 R15
  Target foe takes 30..60 holy damage. If target foe was attacking, that foe is knocked down.
  ~ Holy damage :: 0-4: 30 32 34 36 38 | 5-9: 40 42 44 46 48 | 10-14: 50 52 54 56 58 | 15-19: 60 62 64 66 68 | 20-21: 70 72
  # causes: Holy Damage, Knockdown; target: foes
Banish #252 | Spell | Core | E5 C1 R10
  Target foe takes 20..65 holy damage. This spell does double damage to summoned creatures.
  ~ Holy damage :: 0-4: 20 23 26 29 32 | 5-9: 35 38 41 44 47 | 10-14: 50 53 56 59 62 | 15-19: 65 68 71 74 77 | 20-21: 80 83
  # causes: Holy Damage; target: foes
Castigation Signet #2006 | Signet | Eye of the North | C1 R15
  Target foe takes 26..56 holy damage. If that foe was attacking, you gain 4..14 Energy.
  ~ Holy damage :: 0-4: 26 28 30 32 34 | 5-9: 36 38 40 42 44 | 10-14: 46 48 50 52 54 | 15-19: 56 58 60 62 64 | 20-21: 66 68
  ~ Energy gain :: 0-4: 4 5 5 6 7 | 5-9: 7 8 9 9 10 | 10-14: 11 11 12 13 13 | 15-19: 14 15 15 16 17 | 20-21: 17 18
  # causes: Holy Damage, Energy Gain
Defender's Zeal #1688 | Elite Hex Spell | Nightfall | E5 C1 R5
  For 10..30 seconds, whenever target foe hits with an attack, you gain 2 Energy.
  ~ Duration :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  # causes: Energy Gain
Holy Strike #312 | Touch skill | Prophecies | E5 C¾ R8
  Skill. Touched target foe takes 10..55 holy damage. If knocked down, your target takes an additional 10..55 holy damage.
  ~ Holy damage :: 0-4: 10 13 16 19 22 | 5-9: 25 28 31 34 37 | 10-14: 40 43 46 49 52 | 15-19: 55 58 61 64 67 | 20-21: 70 73
  ~ + Holy damage :: 0-4: 10 13 16 19 22 | 5-9: 25 28 31 34 37 | 10-14: 40 43 46 49 52 | 15-19: 55 58 61 64 67 | 20-21: 70 73
  # causes: Holy Damage; target: foes; range: touch; special: duplicate
Holy Wrath #249 | Enchantment Spell | Prophecies | E10 C1 R10
  For 10..30 seconds, the next 1..10 time[s] target other ally takes attack damage, this spell deals 66% of the damage back to the source (maximum of 5..50 damage).
  ~ Duration :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  ~ Number of attacks :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Maximum damage :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Holy Damage; target: other allies
Judge's Insight #267 | Enchantment Spell | Core | E10 C2 R10
  For 8..20 seconds, target ally's attacks deal holy damage and have +20% armor penetration.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  # causes: Holy Damage, Armor Penetration; target: allies
Judge's Intervention #1390 | Enchantment Spell | Nightfall | E5 C¼ R8
  For 10 seconds, the next time target ally receives damage that would be fatal, the damage is negated and one nearby foe takes 30..180 holy damage.
  ~ Holy damage :: 0-4: 30 40 50 60 70 | 5-9: 80 90 100 110 120 | 10-14: 130 140 150 160 170 | 15-19: 180 190 200 210 220 | 20-21: 230 240
  # causes: Damage Reduction, Holy Damage; target: allies; aoe: nearby
  ! ANOMALY: Unlike most other monk spells, Judge's Intervention does not invoke an animation upon the target.
Kirin's Wrath #1113 | Spell | Factions | E5 C1 R10
  For 5 seconds, foes adjacent to the location in which the spell was cast take 8..32 holy damage each second.
  ~ Holy damage :: 0-4: 8 10 11 13 14 | 5-9: 16 18 19 21 22 | 10-14: 24 26 27 29 30 | 15-19: 32 34 35 37 38 | 20-21: 40 42
  # causes: Holy Damage; target: self; aoe: adjacent
Ray of Judgment #830 | Elite Spell | Factions | E10 C1 R15
  Invoke a Ray of Judgment at target foe's location. For 5 seconds, target foe and all foes adjacent to this location take 10..50 holy damage each second and begin Burning for 1..3 second[s].
  ~ Holy damage :: 0-4: 10 13 15 18 21 | 5-9: 23 26 29 31 34 | 10-14: 37 39 42 45 47 | 15-19: 50 53 55 58 61 | 20-21: 63 66
  ~ Burning duration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Holy Damage, Burning; target: foes; range: Casting; aoe: adjacent
  ! ANOMALY: Unlike other recurring ground AOE skills, AI units often will not try to leave until the effect is nearly expired.
Retribution #248 | Enchantment Spell | Core | E10 U-1 C2
  While you maintain this enchantment, whenever target ally takes attack damage, this spell deals 33% of the damage back to the source (maximum 5..20 damage).
  ~ Maximum damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Holy Damage; target: allies
  ! BUG: If you somehow manage to maintain Retribution on a foe, it will not deal damage back to you or your allies.
Reversal of Damage #1400 | Enchantment Spell | Nightfall | E5 C¼ R3
  For 8 seconds, the next time target ally would take damage, the foe dealing the damage takes that damage instead (maximum 5..75).
  ~ Max damage returned :: 0-4: 5 10 14 19 24 | 5-9: 28 33 38 42 47 | 10-14: 52 56 61 66 70 | 15-19: 75 80 84 89 94 | 20-21: 98 103
  # causes: Damage Reduction, Holy Damage; target: allies
Scourge Enchantment #1398 | Hex Spell | Nightfall | E10 C1½ R5
  For 30 seconds, each time target foe is the target of an enchantment, the caster of that enchantment takes 15..75 damage.
  ~ Damage :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
Scourge Healing #251 | Hex Spell | Core | E10 C2 R5
  For 30 seconds, every time target foe is healed, the healer takes 15..80 holy damage.
  ~ Holy damage :: 0-4: 15 19 24 28 32 | 5-9: 37 41 45 50 54 | 10-14: 58 63 67 71 76 | 15-19: 80 84 89 93 97 | 20-21: 102 106
  # causes: Holy Damage
  ! ANOMALY: This hex does not trigger for Heal Area, Karei's Healing Circle, and Healing Ring.
Scourge Sacrifice #253 | Hex Spell | Prophecies | E5 C1 R5
  For 8..20 seconds, every time target foe and adjacent foes sacrifice life, they sacrifice twice the normal amount.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  # aoe: adjacent
Shield of Judgment #262 | Elite Enchantment Spell | Prophecies | E15 C1 R45
  For 8..20 seconds, anyone striking target ally with an attack is knocked down and suffers 5..50 holy damage.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  ~ Holy damage :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Holy Damage, Knockdown; target: allies
  ! BUG: Shield of Judgment will not be listed in the damage monitor if its damage is reduced to 0.
  ! ANOMALY: The concise description states that foes attacking target ally will be knocked down and suffer damage; however, this effect only occurs when the target ally is successfully hit.
Signet of Judgment (PvP) #2887 | Elite Signet | Core | C1 R20
  Target foe is knocked down. That foe and all adjacent foes take 5..50 holy damage. This signet has half the normal range.
  ~ Holy damage :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Knockdown, Holy Damage; target: foes; range: half; aoe: adjacent
Signet of Mystic Wrath #1689 | Signet | Nightfall | C2 R20
  Target foe takes 25 holy damage for each enchantment on you (maximum 30..120 holy damage).
  ~ maximum Holy damage :: 0-4: 30 36 42 48 54 | 5-9: 60 66 72 78 84 | 10-14: 90 96 102 108 114 | 15-19: 120 126 132 138 144 | 20-21: 150 156
  # causes: Holy Damage; target: foes
Signet of Rage #1269 | Signet | Factions | C1 R20
  Target foe takes 5..50 holy damage and +5..10 holy damage for each adrenaline skill that foe has.
  ~ Holy damage :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  ~ + Holy damage :: 0-4: 5 5 6 6 6 | 5-9: 7 7 7 8 8 | 10-14: 8 9 9 9 10 | 15-19: 10 10 11 11 11 | 20-21: 12 12
  # causes: Holy Damage; target: foes; range: casting
Smite #240 | Spell | Prophecies | E10 C1 R10
  This attack deals 10..55 Holy damage. If attacking, your target takes an additional 10..35 Holy damage.
  ~ Holy damage :: 0-4: 10 13 16 19 22 | 5-9: 25 28 31 34 37 | 10-14: 40 43 46 49 52 | 15-19: 55 58 61 64 67 | 20-21: 70 73
  ~ + Holy damage :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  # causes: Holy Damage
Smite Condition #2004 | Spell | Eye of the North | E5 C1 R7
  Remove one condition from target ally. If a condition was removed, foes in the area take 10..60 holy damage.
  ~ Holy damage :: 0-4: 10 13 17 20 23 | 5-9: 27 30 33 37 40 | 10-14: 43 47 50 53 57 | 15-19: 60 63 67 70 73 | 20-21: 77 80
  # causes: Holy Damage; removes: condition; target: allies; aoe: nearby
  ! BUG: The effect area is actually nearby foes.
Smite Hex #302 | Spell | Core | E5 C1 R12
  Remove a hex from target ally. If a hex is removed, foes in the area suffer 10..85 holy damage.
  ~ Holy damage :: 0-4: 10 15 20 25 30 | 5-9: 35 40 45 50 55 | 10-14: 60 65 70 75 80 | 15-19: 85 90 95 100 105 | 20-21: 110 115
  # causes: Holy Damage; removes: Hex spell; target: allies; aoe: in the area
Spear of Light #1130 | Spell | Factions | E5 C1 R15
  Spear of Light flies toward target foe and deals 26..56 holy damage if it hits. Spear of Light deals +15..60 damage if it hits an attacking foe.
  ~ Holy damage :: 0-4: 26 28 30 32 34 | 5-9: 36 38 40 42 44 | 10-14: 46 48 50 52 54 | 15-19: 56 58 60 62 64 | 20-21: 66 68
  ~ + Holy damage :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  # causes: Holy Damage; target: foes
  ! ANOMALY: Unlike Smite, this spell deals the additional damage on an attacking foe in a separate packet.
Stonesoul Strike #1131 | Touch skill | Factions | E5 C¾ R8
  Skill. Touched target foe takes 10..55 holy damage. If knocked down, your target takes an additional 10..55 holy damage.
  ~ Holy damage :: 0-4: 10 13 16 19 22 | 5-9: 25 28 31 34 37 | 10-14: 40 43 46 49 52 | 15-19: 55 58 61 64 67 | 20-21: 70 73
  ~ + Holy damage :: 0-4: 10 13 16 19 22 | 5-9: 25 28 31 34 37 | 10-14: 40 43 46 49 52 | 15-19: 55 58 61 64 67 | 20-21: 70 73
  # causes: Holy Damage; target: foes; range: touch; special: duplicate
Strength of Honor (PvP) #2999 | Enchantment Spell | Core | E10 U-1 C2 R15
  While you maintain this enchantment, target ally deals 1..5 more damage in melee.
  ~ Armor-ignoring damage :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # target: allies
Symbol of Wrath #247 | Spell | Prophecies | E5 C1 R20
  Create a Symbol of Wrath at target foe's location. For 5 seconds, adjacent foes are struck for 10..40 holy damage each second.
  ~ Holy damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Holy Damage; target: self; aoe: adjacent
  ! BUG: While the functionality of this spell has changed with the June 24, 2026 update, its animation has not. There is no visible animation to highlight the new area of effect.
  ! BUG: Contrary to other skills dealing Area damage over time (such as Fire Storm), this skill will fail if the target dies before the spell finishes casting.
Word of Censure #1129 | Elite Spell | Factions | E10 C1 R2
  Target foe takes 30..130 holy damage. If your target was below 50% Health, Word of Censure takes 20 additional seconds to recharge.
  ~ Holy damage :: 0-4: 30 37 43 50 57 | 5-9: 63 70 77 83 90 | 10-14: 97 103 110 117 123 | 15-19: 130 137 143 150 157 | 20-21: 163 170
  # causes: Holy Damage, Increased Recharge Time; target: foes
Zealot's Fire #271 | Enchantment Spell | Core | E10 C¼ R30
  For 60 seconds, whenever you use a skill that targets an ally, all foes adjacent to that target are struck for 5..35 fire damage and you lose 1 Energy.
  ~ Fire damage :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  # causes: Fire Damage, Energy Loss; target: self; aoe: adjacent
  ! BUG: The concise description is wrong: the energy loss is applied every time the user uses a skill that targets an ally, regardless of any damage dealt.

## Necromancer

### Necromancer / Blood Magic
Awaken the Blood #111 | Enchantment Spell | Prophecies | E10 C1 R45
  For 20..44 seconds, you gain +2 Blood Magic and +2 Curses, but whenever you sacrifice Health, you sacrifice 50% more than the normal amount.
  ~ Duration :: 0-4: 20 22 23 25 26 | 5-9: 28 30 31 33 34 | 10-14: 36 38 39 41 42 | 15-19: 44 46 47 49 50 | 20-21: 52 54
  # causes: Increased Attribute
Barbed Signet #131 | Signet | Core | S8% C1 R10
  You inflict Bleeding for 3..15 seconds on target foe and all adjacent foes.
  ~ Bleeding duration :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Bleeding; target: foes; aoe: adjacent
Blood Bond #835 | Hex Spell | Factions | E5 C1 R8
  For 3..12 seconds, target foe and all adjacent foes are hexed with Blood Bond. Whenever an ally hits one of them with an attack, that ally gains 5..20 Health. If one of these foes dies while hexed, all allies adjacent to that foe are healed for 20..100 Health.
  ~ Duration :: 0-4: 3 4 4 5 5 | 5-9: 6 7 7 8 8 | 10-14: 9 10 10 11 11 | 15-19: 12 13 13 14 14 | 20-21: 15 16
  ~ Health gain :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Healing :: 0-4: 20 25 31 36 41 | 5-9: 47 52 57 63 68 | 10-14: 73 79 84 89 95 | 15-19: 100 105 111 116 121 | 20-21: 127 132
  # causes: Health Gain, Healing; aoe: adjacent
Blood Drinker #1076 | Spell | Factions | E5 C2 R8
  If your Health is above 90%, you begin Bleeding for 6 seconds. Steal up to 20..65 Health from target foe.
  ~ Life stealing :: 0-4: 20 23 26 29 32 | 5-9: 35 38 41 44 47 | 10-14: 50 53 56 59 62 | 15-19: 65 68 71 74 77 | 20-21: 80 83
  # causes: Life Stealing, Bleeding; target: foes
Blood is Power #119 | Elite Enchantment Spell | Core | E1 S33% C¼
  For 10 seconds, target other ally gains +3..6 Energy regeneration.
  ~ Energy regeneration :: 0-4: 3 3 3 4 4 | 5-9: 4 4 4 5 5 | 10-14: 5 5 5 6 6 | 15-19: 6 6 6 7 7 | 20-21: 7 7
  # causes: Energy Regeneration; target: other allies
  ! BUG: Heroes will spam this skill on allies with heavy overcast, regardless of what percentage of energy the ally has.
Blood of the Aggressor #902 | Spell | Nightfall | E5 C1 R5
  Steal up to 5..45 Health from target foe. If that foe was attacking, that foe suffers Weakness for 3..12 seconds.
  ~ Life stealing :: 0-4: 5 8 10 13 16 | 5-9: 18 21 24 26 29 | 10-14: 32 34 37 40 42 | 15-19: 45 48 50 53 56 | 20-21: 58 61
  ~ Weakness duration :: 0-4: 3 4 4 5 5 | 5-9: 6 7 7 8 8 | 10-14: 9 10 10 11 11 | 15-19: 12 13 13 14 14 | 20-21: 15 16
  # causes: Life Stealing, Weakness; target: foes
Blood Renewal #115 | Enchantment Spell | Prophecies | E1 S15% C1 R7
  For 7 seconds, you gain +3..6 Health regeneration. When Blood Renewal ends, you gain 40..190 Health.
  ~ Regeneration :: 0-4: 3 3 3 4 4 | 5-9: 4 4 4 5 5 | 10-14: 5 5 5 6 6 | 15-19: 6 6 6 7 7 | 20-21: 7 7
  ~ Healing :: 0-4: 40 50 60 70 80 | 5-9: 90 100 110 120 130 | 10-14: 140 150 160 170 180 | 15-19: 190 200 210 220 230 | 20-21: 240 250
  ~ Total :: 0-4: 82 92 102 126 136 | 5-9: 146 156 166 190 200 | 10-14: 210 220 230 254 264 | 15-19: 274 284 294 318 328 | 20-21: 338 348
  # causes: Health Regeneration, Healing
  ! BUG: Contrary to the full description, this skill causes healing and not health gain.
  ! BUG: Despite causing healing, this skill cannot trigger Scourge Healing.
Blood Ritual #157 | Touch Enchantment Spell | Prophecies | E5 S17% C1 R2
  Enchantment Spell. For 8..14 seconds, target touched ally gains +3 Energy regeneration. Blood Ritual cannot be used on the caster.
  ~ Duration :: 0-4: 8 8 9 9 10 | 5-9: 10 10 11 11 12 | 10-14: 12 12 13 13 14 | 15-19: 14 14 15 15 16 | 20-21: 16 16
  # causes: Energy Regeneration; target: other allies; range: touch
  ! BUG: Heroes use this skill on overcast targets that cannot gain any energy.
  ! BUG: The concise description omits that this is a touch-range skill.
Cultist's Fervor #806 | Elite Enchantment Spell | Factions | E5 C1 R15
  For 5 seconds and 3 seconds longer for every rank of Soul Reaping, your Necromancer spells cost -1..6 Energy to cast but you suffer from Bleeding for 10 seconds each time you cast a Necromancer spell.
  ~ Energy reduction :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  ~ Duration :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Bleeding, Decreased Energy Cost; aoe: adjacent
  ! ANOMALY: Causes bleeding when non-fleshy creatures, such as Shadow Vaettirs, cast Necromancer spells.
Dark Bond #138 | Enchantment Spell | Core | E5 C2 R20
  For the next 30..60 seconds, whenever you receive damage, your closest minion suffers 75% of that damage for you.
  ~ Duration :: 0-4: 30 32 34 36 38 | 5-9: 40 42 44 46 48 | 10-14: 50 52 54 56 58 | 15-19: 60 62 64 66 68 | 20-21: 70 72
  # target: self
Dark Fury #147 | Enchantment Spell | Prophecies | E10 S17% C¾ R5
  For 5 seconds, whenever any party member hits with an attack, that party member gains one hit of adrenaline. (50% failure chance with Blood Magic of 4 or less.)
  # causes: Adrenaline Gain; aoe: party
Dark Pact #133 | Spell | Core | E1 S10% C1 R2
  Deal 20..60 shadow damage to target foe.
  ~ Shadow damage :: 0-4: 20 23 25 28 31 | 5-9: 33 36 39 41 44 | 10-14: 47 49 52 55 57 | 15-19: 60 63 65 68 71 | 20-21: 73 76
  # causes: Shadow Damage; target: foes
Demonic Flesh #130 | Enchantment Spell | Core | E5 C1 R30
  For 30..60 seconds, whenever you use a skill that targets a foe, you deal 5..20 shadow damage to all other foes adjacent to you.
  ~ Duration :: 0-4: 30 32 34 36 38 | 5-9: 40 42 44 46 48 | 10-14: 50 52 54 56 58 | 15-19: 60 62 64 66 68 | 20-21: 70 72
  ~ Shadow damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Shadow Damage; target: self; aoe: adjacent
Jaundiced Gaze #763 | Enchantment spell | Factions | E5 C1 R15
  Remove an enchantment from target foe. If an enchantment is removed, for the next 1..20 second[s], your next enchantment spell casts 0..1 second[s] faster and costs 1..10 less Energy.
  ~ Duration :: 0-4: 1 2 4 5 6 | 5-9: 7 9 10 11 12 | 10-14: 14 15 16 17 19 | 15-19: 20 21 23 24 25 | 20-21: 26 28
  ~ Enchantment cast reduction :: 0-4: 0 0 0 0 0 | 5-9: 0 0 0 1 1 | 10-14: 1 1 1 1 1 | 15-19: 1 1 1 1 1 | 20-21: 1 1
  ~ Enchantment cost reduction :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # causes: Decreased Activation Time, Decreased Energy Cost; removes: Enchantment; target: foes
  ! ANOMALY: Similar to other enchantments that target a foe, foes affected by Well of the Profane or spirits cannot be targeted by this enchantment.
Life Siphon #109 | Hex Spell | Core | E10 C1 R5
  For 12..24 seconds, target foe suffers -1..3 Health degeneration, and you gain +1..3 Health regeneration.
  ~ Duration :: 0-4: 12 13 14 14 15 | 5-9: 16 17 18 18 19 | 10-14: 20 21 22 22 23 | 15-19: 24 25 26 26 27 | 20-21: 28 29
  ~ Health degeneration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  ~ Health regeneration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Health Degeneration, Health Regeneration
  ! ANOMALY: Similar to Augury of Death and enchantments with upkeep, if a hexed foe moves out of compass range of the caster, Life Siphon will end.
Life Transfer #126 | Elite Hex Spell | Prophecies | E5 C1 R20
  For 6..12 seconds, target foe and adjacent foes suffer -3..8 Health degeneration, which you gain as Health regeneration.
  ~ Duration :: 0-4: 6 6 7 7 8 | 5-9: 8 8 9 9 10 | 10-14: 10 10 11 11 12 | 15-19: 12 12 13 13 14 | 20-21: 14 14
  ~ Health degeneration/regeneration :: 0-4: 3 3 4 4 4 | 5-9: 5 5 5 6 6 | 10-14: 6 7 7 7 8 | 15-19: 8 8 9 9 9 | 20-21: 10 10
  # causes: Health Degeneration, Health Regeneration; aoe: adjacent
  ! BUG: The concise description fails to mention that the regeneration is gained for each hexed foe.
Lifebane Strike #1067 | Spell | Factions | E10 C2 R15
  Target foe takes 12..48 shadow damage. If that foe's Health is above 50%, you steal up to 12..48 Health.
  ~ Shadow damage :: 0-4: 12 14 17 19 22 | 5-9: 24 26 29 31 34 | 10-14: 36 38 41 43 46 | 15-19: 48 50 53 55 58 | 20-21: 60 62
  ~ Life stealing :: 0-4: 12 14 17 19 22 | 5-9: 24 26 29 31 34 | 10-14: 36 38 41 43 46 | 15-19: 48 50 53 55 58 | 20-21: 60 62
  # causes: Shadow Damage, Life Stealing; target: foes; special: duplicate
Mark of Fury #1360 | Hex Spell | Nightfall | E5 C¾ R10
  For 5 seconds, allies hitting target foe gain 0..2 strike[s] of adrenaline. When this hex ends, that foe suffers from Cracked Armor for 1..15 second[s].
  ~ Adrenaline gain :: 0-4: 0 0 0 0 1 | 5-9: 1 1 1 1 1 | 10-14: 1 1 2 2 2 | 15-19: 2 2 2 2 3 | 20-21: 3 3
  ~ Cracked Armor duration :: 0-4: 1 2 3 4 5 | 5-9: 6 7 8 8 9 | 10-14: 10 11 12 13 14 | 15-19: 15 16 17 18 19 | 20-21: 20 21
  # causes: Adrenaline Gain, Cracked Armor; range: Casting
Mark of Subversion #127 | Hex Spell | Prophecies | E10 C2 R30
  For 6 seconds, the next time target foe casts a spell that targets an ally of that foe, the spell fails and you steal up to 10..92 Health from that foe.
  ~ Life stealing :: 0-4: 10 15 21 26 32 | 5-9: 37 43 48 54 59 | 10-14: 65 70 76 81 87 | 15-19: 92 97 103 108 114 | 20-21: 119 125
  # causes: Life Stealing
Offering of Blood #146 | Elite Spell | Prophecies | E1 S20% C¼ R15
  You gain 8..20 Energy.
  ~ Energy gain :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  # causes: Energy Gain
Oppressive Gaze #864 | Spell | Factions | E10 C1 R10
  Target foe and adjacent foes take 10..30 shadow damage. Foes already suffering from a condition are Poisoned and Weakened for 3..12 seconds.
  ~ Shadow damage :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  ~ Poison and Weakness duration :: 0-4: 3 4 4 5 5 | 5-9: 6 7 7 8 8 | 10-14: 9 10 10 11 11 | 15-19: 12 13 13 14 14 | 20-21: 15 16
  # causes: Shadow Damage, Poison, Weakness; target: foes; aoe: adjacent
  ! ANOMALY: The concise description describes the damage as typeless instead of shadow damage. This is mostly irrelevant in game as both are functionally identical armor-ignoring damage.
Order of Pain #134 | Enchantment Spell | Core | E10 S17% C2
  For 5 seconds, whenever a party member hits a foe with physical damage, that party member does +3..16 damage.
  ~ + Damage :: 0-4: 3 4 5 6 6 | 5-9: 7 8 9 10 11 | 10-14: 12 13 13 14 15 | 15-19: 16 17 18 19 19 | 20-21: 20 21
  # aoe: party
Order of the Vampire #148 | Elite Enchantment Spell | Prophecies | E5 S17% C2 R5
  For 5 seconds, whenever a party member who is not under the effects of another Necromancer enchantment hits a foe with physical damage, that party member steals up to 3..16 Health.
  ~ Life stealing :: 0-4: 3 4 5 6 6 | 5-9: 7 8 9 10 11 | 10-14: 12 13 13 14 15 | 15-19: 16 17 18 19 19 | 20-21: 20 21
  # causes: Life Stealing; target: self; aoe: party
Ravenous Gaze #862 | Elite Spell | Nightfall | E1 S8% C1 R10
  Deal 20..40 damage and steal 20..40 Health from target foe and all nearby foes.
  ~ Damage :: 0-4: 20 21 23 24 25 | 5-9: 27 28 29 31 32 | 10-14: 33 35 36 37 39 | 15-19: 40 41 43 44 45 | 20-21: 47 48
  ~ Life stealing :: 0-4: 20 21 23 24 25 | 5-9: 27 28 29 31 32 | 10-14: 33 35 36 37 39 | 15-19: 40 41 43 44 45 | 20-21: 47 48
  # causes: Life Stealing; target: foes; aoe: nearby
Shadow Strike #102 | Spell | Prophecies | E10 C2 R15
  Target foe takes 12..48 shadow damage. If that foe's Health is above 50%, you steal up to 12..48 Health.
  ~ Shadow damage :: 0-4: 12 14 17 19 22 | 5-9: 24 26 29 31 34 | 10-14: 36 38 41 43 46 | 15-19: 48 50 53 55 58 | 20-21: 60 62
  ~ Life stealing :: 0-4: 12 14 17 19 22 | 5-9: 24 26 29 31 34 | 10-14: 36 38 41 43 46 | 15-19: 48 50 53 55 58 | 20-21: 60 62
  # causes: Shadow Damage, Life Stealing; special: duplicate
Signet of Agony (PvP) #3059 | Signet | Core | S10% C¾ R20
  You suffer from Bleeding for 25 seconds. All nearby foes take 10..70 damage.
  ~ Damage :: 0-4: 10 14 18 22 26 | 5-9: 30 34 38 42 46 | 10-14: 50 54 58 62 66 | 15-19: 70 74 78 82 86 | 20-21: 90 94
  # causes: Bleeding; target: self; aoe: nearby
Signet of Suffering #1364 | Elite Signet | Nightfall | R4
  You suffer from Bleeding for 6 seconds. The next Necromancer skill that targets a foe causes Bleeding for 2..16 seconds.
  ~ Bleeding duration :: 0-4: 2 3 4 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 14 15 | 15-19: 16 17 18 19 20 | 20-21: 21 22
  # causes: Bleeding; target: foes; aoe: adjacent
  ! ANOMALY: Even though it has no activation time, this signet (similar to Dolyak Signet) cannot be used while knocked down or performing an action.
  ! ANOMALY: After being resurrected, if the player uses the skill in the middle of the stand up animation they will not begin bleeding.
Soul Leech #128 | Elite Hex Spell | Prophecies | E15 C1 R7
  For 10 seconds, whenever target foe casts a spell, you steal up to 16..80 Health from that foe.
  ~ Life stealing :: 0-4: 16 20 25 29 33 | 5-9: 37 42 46 50 54 | 10-14: 59 63 67 71 76 | 15-19: 80 84 89 93 97 | 20-21: 101 106
  # causes: Life Stealing
Spoil Victor (PvP) #3233 | Elite Hex Spell | Factions | E10 C1 R10
  For 3..15 seconds, whenever target foe attacks or casts a spell on a creature with less Health that foe loses 15..75 Health.
  ~ Duration :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  ~ Health loss :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  # causes: Health Loss
Strip Enchantment #143 | Spell | Core | E10 C1 R20
  Remove 0..2 enchantment[s] from target foe. If an enchantment is removed, you steal 5..65 Health.
  ~ Enchantments removed :: 0-4: 0 0 0 0 1 | 5-9: 1 1 1 1 1 | 10-14: 1 1 2 2 2 | 15-19: 2 2 2 2 3 | 20-21: 3 3
  ~ Life stealing :: 0-4: 5 9 13 17 21 | 5-9: 25 29 33 37 41 | 10-14: 45 49 53 57 61 | 15-19: 65 69 73 77 81 | 20-21: 85 89
  # causes: Life Stealing; removes: Enchantment; target: Foes; range: Casting
Touch of Agony #158 | Touch Skill | Prophecies | E1 S10% C¾ R3
  Skill. Target touched foe takes 20..58 shadow damage.
  ~ Shadow damage :: 0-4: 20 23 25 28 30 | 5-9: 33 35 38 40 43 | 10-14: 45 48 50 53 55 | 15-19: 58 61 63 66 68 | 20-21: 71 73
  # causes: Shadow Damage; target: foes; range: touch; special: duplicate
Unholy Feast (PvP) #3058 | Spell | Core | E15 C¾ R20
  Steal up to 10..65 Health from up to 1..4 foes in the area.
  ~ Life stealing :: 0-4: 10 14 17 21 25 | 5-9: 28 32 36 39 43 | 10-14: 47 50 54 58 61 | 15-19: 65 69 72 76 80 | 20-21: 83 87
  ~ Affected foes :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  # causes: Life Stealing; target: self; aoe: in the area
Vampiric Bite #1077 | Touch Skill | Factions | E15 C¾ R2
  Skill. Touch target foe to steal up to 29..74 Health.
  ~ Life stealing :: 0-4: 29 32 35 38 41 | 5-9: 44 47 50 53 56 | 10-14: 59 62 65 68 71 | 15-19: 74 77 80 83 86 | 20-21: 89 92
  # causes: Life Stealing; target: foes; range: touch; special: duplicate
Vampiric Gaze #153 | Spell | Core | E10 C1 R8
  Steal up to 18..60 Health from target foe.
  ~ Life stealing :: 0-4: 18 21 24 26 29 | 5-9: 32 35 38 40 43 | 10-14: 46 49 52 54 57 | 15-19: 60 63 66 68 71 | 20-21: 74 77
  # causes: Life Stealing; target: foes
Vampiric Spirit #819 | Elite Enchantment Spell | Factions | E5 C1 R8
  Steal up to 15..60 Health from target foe. For 10 seconds, you have +5..10 Health regeneration.
  ~ Life stealing :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  ~ Health regeneration :: 0-4: 5 5 6 6 6 | 5-9: 7 7 7 8 8 | 10-14: 8 9 9 9 10 | 15-19: 10 10 11 11 11 | 20-21: 12 12
  # causes: Life Stealing, Health Regeneration; target: foes
  ! ANOMALY: Similar to other enchantments that target a foe, foes affected by Well of the Profane or spirits cannot be targeted by this enchantment.
Vampiric Swarm #1075 | Spell | Factions | E15 C2 R8
  Vampiric Swarm steals up to 15..60 Health from up to three foes in the area.
  ~ Life stealing :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  # causes: Life Stealing; target: foes; aoe: in the area
  ! ANOMALY: The hits of this spell don't have an animation, unlike Deathly Swarm.
Vampiric Touch #156 | Touch Skill | Prophecies | E15 C¾ R2
  Skill. Touch target foe to steal up to 29..74 Health.
  ~ Life stealing :: 0-4: 29 32 35 38 41 | 5-9: 44 47 50 53 56 | 10-14: 59 62 65 68 71 | 15-19: 74 77 80 83 86 | 20-21: 89 92
  # causes: Life Stealing; target: foes; range: touch; special: duplicate
Wallow's Bite #1078 | Touch Skill | Factions | E1 S10% C¾ R3
  Skill. Target touched foe takes 20..58 damage.
  ~ Shadow damage :: 0-4: 20 23 25 28 30 | 5-9: 33 35 38 40 43 | 10-14: 45 48 50 53 55 | 15-19: 58 61 63 66 68 | 20-21: 71 73
  # causes: Shadow Damage; target: foes; range: touch; special: duplicate
  ! ANOMALY: Although essentially identical to Touch of Agony, Wallow's Bite isn't stated to deal shadow damage.
Well of Blood #92 | Well Spell | Core | E10 C1 R2
  Exploit nearest corpse or sacrifice 66% health to create a Well of Blood at its location. For 8..20 seconds, allies in that area receive +1..6 Health regeneration.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  ~ Health regeneration :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  # causes: Health Regeneration
Well of Power #91 | Elite Well Spell | Prophecies | E5 C1 R10
  Exploit nearest corpse or sacrifice 66% health to create a Well of Power at that location. For 10..30 seconds, allies within the area of Well of Power gain +1..6 Health regeneration and +2 Energy regeneration.
  ~ Duration :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  ~ Health regeneration :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  # causes: Health Regeneration, Energy Regeneration

### Necromancer / Curses
Atrophy #2237 | Hex Spell | Eye of the North | E10 C1 R20
  For 3..7 seconds, target foe's primary attribute is reduced to 0.
  ~ Duration :: 0-4: 3 3 4 4 4 | 5-9: 4 5 5 5 5 | 10-14: 6 6 6 6 7 | 15-19: 7 7 8 8 8 | 20-21: 8 9
  # causes: Decreased Attribute
Barbs #101 | Hex Spell | Core | E10 C1 R5
  For 30 seconds, target foe takes 4..16 more damage when hit by physical damage.
  ~ Damage :: 0-4: 4 5 6 6 7 | 5-9: 8 9 10 10 11 | 10-14: 12 13 14 14 15 | 15-19: 16 17 18 18 19 | 20-21: 20 21
  # causes: Armor-ignoring Damage
  ! BUG: Causes skills such as Xinrae's Weapon and Vengeful Weapon to trigger twice.
Cacophony #1998 | Hex Spell | Eye of the North | E10 C1 R15
  For 15 seconds, whenever target foe uses a shout or chant, that foe takes 30..105 damage.
  ~ Damage :: 0-4: 30 35 40 45 50 | 5-9: 55 60 65 70 75 | 10-14: 80 85 90 95 100 | 15-19: 105 110 115 120 125 | 20-21: 130 135
Chilblains #144 | Spell | Core | E25 C2 R8
  You become Poisoned for 10 seconds. Foes in the area of your target are struck for 10..44 cold damage and lose 1..2 enchantment[s].
  ~ Cold damage :: 0-4: 10 12 15 17 19 | 5-9: 21 24 26 28 30 | 10-14: 33 35 37 39 42 | 15-19: 44 46 49 51 53 | 20-21: 55 58
  ~ Enchantments removed :: 0-4: 1 1 1 1 1 | 5-9: 1 1 1 2 2 | 10-14: 2 2 2 2 2 | 15-19: 2 2 2 2 2 | 20-21: 2 2
  # causes: Poison, Cold Damage; removes: Enchantment; target: Foes; range: Casting; aoe: in the area
Corrupt Enchantment #1362 | Elite Hex Spell | Nightfall | E5 C¾ R5
  Remove one enchantment from target foe. If an enchantment is removed in this way, that foe suffers from -1..8 Health degeneration for 10 seconds.
  ~ Health degeneration :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  # causes: Health Degeneration; removes: Enchantment
Defile Defenses #2188 | Hex Spell | Eye of the North | E5 C1 R5
  For 5..20 seconds, the next time target foe blocks, that foe takes 30..120 damage.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Damage :: 0-4: 30 36 42 48 54 | 5-9: 60 66 72 78 84 | 10-14: 90 96 102 108 114 | 15-19: 120 126 132 138 144 | 20-21: 150 156
  # causes: Block Punishment
Defile Enchantments #1070 | Spell | Factions | E10 C2 R15
  Target foe and all nearby foes take 6..60 shadow damage and 4..20 shadow damage for each enchantment on them.
  ~ Shadow damage :: 0-4: 6 10 13 17 20 | 5-9: 24 28 31 35 38 | 10-14: 42 46 49 53 56 | 15-19: 60 64 67 71 74 | 20-21: 78 82
  ~ Damage per enchantment :: 0-4: 4 5 6 7 8 | 5-9: 9 10 11 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Shadow Damage; target: foes; aoe: nearby; special: duplicate
Defile Flesh #129 | Hex Spell | Core | E10 S10% C1 R10
  For 5..35 seconds, target foe gains only two-thirds Health from healing.
  ~ Duration :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
Depravity #820 | Elite Hex Spell | Nightfall | E10 C1 R15
  For 5..20 seconds, whenever target foe casts a spell, that foe and one nearby foe lose 1..5 Energy.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Energy lost :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Energy Loss; aoe: nearby
Desecrate Enchantments #112 | Spell | Prophecies | E10 C2 R15
  Target foe and all nearby foes take 6..60 shadow damage and 4..20 shadow damage for each enchantment on them.
  ~ Shadow damage :: 0-4: 6 10 13 17 20 | 5-9: 24 28 31 35 38 | 10-14: 42 46 49 53 56 | 15-19: 60 64 67 71 74 | 20-21: 78 82
  ~ Damage per enchantment :: 0-4: 4 5 6 7 8 | 5-9: 9 10 11 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Shadow Damage; target: foes; aoe: nearby; special: duplicate
Enfeeble (PvP) #2859 | Spell | Prophecies | E5 C¼ R10
  Target suffers from Weakness for 10..30 seconds.
  ~ Duration :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  # causes: Weakness; target: foes
Enfeebling Blood (PvP) #2885 | Spell | Core | E1 S17% C1 R8
  Target foe and all nearby foes suffer from Weakness for 1..16 second[s].
  ~ Duration :: 0-4: 1 2 3 4 5 | 5-9: 6 7 8 9 10 | 10-14: 11 12 13 14 15 | 15-19: 16 17 18 19 20 | 20-21: 21 22
  # causes: Weakness; target: foes; aoe: nearby
Enfeebling Touch #1079 | Touch skill | Factions | E5 C¾ R3
  Skill. Target touched foe loses 5..65 Health and suffers from Weakness for 5..20 seconds.
  ~ Health loss :: 0-4: 5 9 13 17 21 | 5-9: 25 29 33 37 41 | 10-14: 45 49 53 57 61 | 15-19: 65 69 73 77 81 | 20-21: 85 89
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Health Loss, Weakness; target: foes; range: touch
Envenom Enchantments #936 | Spell | Nightfall | E5 C1 R15
  Target foe loses one enchantment. For every remaining enchantment, target foe is poisoned for 3..10 seconds.
  ~ Poison duration :: 0-4: 3 3 4 4 5 | 5-9: 5 6 6 7 7 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 13
  # causes: Poison; removes: Enchantment; target: foes
Faintheartedness #135 | Hex Spell | Core | E10 C1 R8
  For the next 4..18 seconds, target foe attacks 50% slower, and that foe suffers -1..3 Health degeneration.
  ~ Duration :: 0-4: 4 5 6 7 8 | 5-9: 9 10 11 11 12 | 10-14: 13 14 15 16 17 | 15-19: 18 19 20 21 22 | 20-21: 23 24
  ~ Health degeneration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Decreased Attack Speed, Health Degeneration
Feast of Corruption #151 | Elite Spell | Prophecies | E15 C2 R15
  Target foe and all adjacent foes are struck for 16..80 shadow damage. You steal up to 8..40 Health from each struck foe who is suffering from a hex.
  ~ Shadow damage :: 0-4: 16 20 25 29 33 | 5-9: 37 42 46 50 54 | 10-14: 59 63 67 71 76 | 15-19: 80 84 89 93 97 | 20-21: 101 106
  ~ Life stealing :: 0-4: 8 10 12 14 17 | 5-9: 19 21 23 25 27 | 10-14: 29 31 34 36 38 | 15-19: 40 42 44 46 49 | 20-21: 51 53
  # causes: Life Stealing, Shadow Damage; target: foes; aoe: adjacent
Insidious Parasite #123 | Hex Spell | Prophecies | E10 C1 R8
  For 5..15 seconds, whenever target foe hits with an attack, you steal up to 15..45 Health from that foe.
  ~ Duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  ~ Life stealing :: 0-4: 15 17 19 21 23 | 5-9: 25 27 29 31 33 | 10-14: 35 37 39 41 43 | 15-19: 45 47 49 51 53 | 20-21: 55 57
  # causes: Life Stealing
Lingering Curse #142 | Elite Hex Spell | Core | E15 C1 R10
  For 6..30 seconds, target foe and all nearby foes suffer -1..4 Health degeneration, and gain 25% less benefit from healing.
  ~ Duration :: 0-4: 6 8 9 11 12 | 5-9: 14 16 17 19 20 | 10-14: 22 24 25 27 28 | 15-19: 30 32 33 35 36 | 20-21: 38 40
  ~ Health degeneration :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  # causes: Health Degeneration
Malaise #140 | Hex Spell | Prophecies | E5 C2 R2
  For 5..35 seconds, target foe suffers -1 Energy degeneration and you suffer -1 Health degeneration. If target foe's Energy reaches 0, that foe takes 5..50 damage and Malaise ends.
  ~ Duration :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  ~ Damage :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Energy Degeneration, Health Degeneration
Mark of Pain #150 | Hex Spell | Core | E10 C1 R20
  For 30 seconds, whenever target foe takes physical damage, Mark of Pain deals 10..40 shadow damage to adjacent foes.
  ~ Shadow damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Shadow Damage; aoe: adjacent
Meekness #1260 | Hex Spell | Nightfall | E15 S17% C1 R20
  For 5..30 seconds, target foe and all foes in the area attack 50% slower.
  ~ Duration :: 0-4: 5 7 8 10 12 | 5-9: 13 15 17 18 20 | 10-14: 22 23 25 27 28 | 15-19: 30 32 33 35 37 | 20-21: 38 40
  # causes: Decreased Attack Speed; aoe: in the area
Order of Apostasy #863 | Elite Enchantment Spell | Factions | E25 C2
  For 5 seconds, whenever a party member hits a foe with physical damage, that foe loses one enchantment. For each Monk enchantment removed, you lose 10..3% maximum Health.
  ~ % Health loss :: 0-4: 10 10 9 9 8 | 5-9: 8 7 7 6 6 | 10-14: 5 5 4 4 3 | 15-19: 3 3 2 2 1 | 20-21: 1 0
  # causes: Health Loss; removes: Enchantment; target: self; aoe: party
Pain of Disenchantment #1359 | Elite Spell | Nightfall | E10 C1 R15
  Target foe loses 1..3 enchantment[s]. If an enchantment was lost in this way, that foe and all adjacent foes lose 10..100 Health.
  ~ Enchantments removed :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  ~ Health loss :: 0-4: 10 16 22 28 34 | 5-9: 40 46 52 58 64 | 10-14: 70 76 82 88 94 | 15-19: 100 106 112 118 124 | 20-21: 130 136
  # causes: Health Loss; removes: Enchantment; target: foes; range: Casting; aoe: adjacent
Parasitic Bond #99 | Hex Spell | Core | E5 C1 R2
  For 20 seconds, target foe suffers -1 Health degeneration. The caster is healed for 30..120 when Parasitic Bond ends.
  ~ Healing :: 0-4: 30 36 42 48 54 | 5-9: 60 66 72 78 84 | 10-14: 90 96 102 108 114 | 15-19: 120 126 132 138 144 | 20-21: 150 156
  # causes: Health Degeneration, Healing
Plague Sending #149 | Spell | Prophecies | E1 S10% C1 R5
  Transfer 1..3 negative condition[s] and [its/their] remaining duration[s] from yourself to target foe and all adjacent foes.
  ~ Conditions transferred :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Condition; removes: Condition; target: foes; aoe: adjacent
Plague Signet #132 | Elite Signet | Core | C1 R4
  Transfer all negative conditions with 100..200% of their remaining durations from yourself to target foe. (50% failure chance with Curses 4 or less.)
  ~ Duration&nbsp;(%) :: 0-4: 100 107 113 120 127 | 5-9: 133 140 147 153 160 | 10-14: 167 173 180 187 193 | 15-19: 200 207 213 220 227 | 20-21: 233 240
  # causes: Condition; removes: Condition; target: foes
Plague Touch #154 | Touch skill | Core | E5 C¾
  Skill. Transfer 1..3 negative condition[s] and [its/their] remaining duration[s] from yourself to target touched foe.
  ~ Conditions transferred :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Condition; removes: Condition; target: foes; range: touch; aoe: none
Poisoned Heart #840 | Spell | Nightfall | E5 C¼ R12
  You and all adjacent foes are Poisoned for 5..15 seconds.
  ~ Poison duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Poison; target: untargeted; aoe: adjacent
Price of Failure #103 | Hex Spell | Prophecies | E15 C2 R20
  For 30 seconds, target foe has a 25% chance to miss with attacks and takes 1..46 damage whenever that foe fails to hit in combat.
  ~ Damage :: 0-4: 1 4 7 10 13 | 5-9: 16 19 22 25 28 | 10-14: 31 34 37 40 43 | 15-19: 46 49 52 55 58 | 20-21: 61 64
  # causes: Miss
Reckless Haste #834 | Hex Spell | Factions | E15 C1 R12
  For 6..12 seconds, target foe and all adjacent foes are hexed with Reckless Haste. While hexed, they attack 25% faster but have a 50% chance to miss with attacks.
  ~ Duration :: 0-4: 6 6 7 7 8 | 5-9: 8 8 9 9 10 | 10-14: 10 10 11 11 12 | 15-19: 12 12 13 13 14 | 20-21: 14 14
  # causes: Miss, Increased Attack Speed; aoe: adjacent
Rend Enchantments #141 | Spell | Core | E5 C2 R20
  Remove 5..9 enchantments from target foe. For each Monk enchantment removed, you lose 55..25 Health.
  ~ Enchantments removed :: 0-4: 5 5 6 6 6 | 5-9: 6 7 7 7 7 | 10-14: 8 8 8 8 9 | 15-19: 9 9 10 10 10 | 20-21: 10 11
  ~ Health loss :: 0-4: 55 53 51 49 47 | 5-9: 45 43 41 39 37 | 10-14: 35 33 31 29 27 | 15-19: 25 23 21 19 17 | 20-21: 15 13
  # causes: Health Loss; removes: Enchantment; target: foes
Rigor Mortis #137 | Hex Spell | Core | E10 C1 R20
  For 8..20 seconds, target foe cannot block.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  # causes: Unblockable
Rip Enchantment #955 | Spell | Nightfall | E5 C1 R15
  Remove 1 enchantment from target foe. If an enchantment was removed, that foe suffers from Bleeding for 5..25 seconds.
  ~ Bleeding duration :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  # causes: Bleeding; removes: Enchantment; requires: Entchantment; target: foes; aoe: adjacent
Shadow of Fear #136 | Hex Spell | Prophecies | E10 C2 R5
  Target foe and all adjacent foes attack 50% slower for the next 5..30 seconds.
  ~ Duration :: 0-4: 5 7 8 10 12 | 5-9: 13 15 17 18 20 | 10-14: 22 23 25 27 28 | 15-19: 30 32 33 35 37 | 20-21: 38 40
  # causes: Decreased Attack Speed; aoe: adjacent
Shivers of Dread #1071 | Hex Spell | Factions | E10 C2 R15
  For 10..40 seconds, whenever target foe is struck for cold damage while using a skill, that foe is interrupted and you lose 8..3 Energy or Shivers of Dread ends.
  ~ Duration :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  ~ Energy loss :: 0-4: 8 8 7 7 7 | 5-9: 6 6 6 5 5 | 10-14: 5 4 4 4 3 | 15-19: 3 3 2 2 2 | 20-21: 1 1
  # causes: Interrupt, Energy Loss; special: duplicate
Soul Barbs #100 | Hex Spell | Prophecies | E10 C2 R10
  For 30 seconds, target foe takes 15..30 damage when an enchantment or hex is cast on that target.
  ~ Damage :: 0-4: 15 16 17 18 19 | 5-9: 20 21 22 23 24 | 10-14: 25 26 27 28 29 | 15-19: 30 31 32 33 34 | 20-21: 35 36
Soul Bind #901 | Elite Hex Spell | Factions | E10 C1 R5
  For 30 seconds, every time target foe is healed, the healer takes 20..80 damage. This hex ends if target is suffering from a Smiting Prayers hex.
  ~ Damage :: 0-4: 20 24 28 32 36 | 5-9: 40 44 48 52 56 | 10-14: 60 64 68 72 76 | 15-19: 80 84 88 92 96 | 20-21: 100 104
Spinal Shivers #124 | Hex Spell | Prophecies | E10 C2 R15
  For 10..40 seconds, whenever target foe is struck for cold damage while using a skill, that foe is interrupted, and you lose 8..3 Energy or Spinal Shivers ends.
  ~ Duration :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  ~ Energy loss :: 0-4: 8 8 7 7 7 | 5-9: 6 6 6 5 5 | 10-14: 5 4 4 4 3 | 15-19: 3 3 2 2 2 | 20-21: 1 1
  # causes: Interrupt, Energy Loss; special: duplicate
Spiteful Spirit #121 | Elite Hex Spell | Prophecies | E15 C2 R10
  For 10..25 seconds, whenever target foe attacks or uses a skill, Spiteful Spirit deals 15..45 shadow damage to that foe and all adjacent allies of that foe.
  ~ Duration :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  ~ Shadow Damage :: 0-4: 15 17 19 21 23 | 5-9: 25 27 29 31 33 | 10-14: 35 37 39 41 43 | 15-19: 45 47 49 51 53 | 20-21: 55 57
  # causes: Shadow Damage; aoe: adjacent
Suffering #108 | Hex Spell | Core | E15 C1 R10
  For 6..30 seconds, target foe and all nearby foes suffer -0..3 Health degeneration.
  ~ Duration :: 0-4: 6 8 9 11 12 | 5-9: 14 16 17 19 20 | 10-14: 22 24 25 27 28 | 15-19: 30 32 33 35 36 | 20-21: 38 40
  ~ Health degeneration :: 0-4: 0 0 0 1 1 | 5-9: 1 1 1 2 2 | 10-14: 2 2 2 3 3 | 15-19: 3 3 3 4 4 | 20-21: 4 4
  # causes: Health Degeneration; aoe: nearby
Ulcerous Lungs #1358 | Hex Spell | Nightfall | E10 C1 R10
  For 10..30 seconds, target foe and all nearby foes suffer from -4 Health degeneration when Bleeding, and whenever they use a shout or chant, they Bleed for 5..20 seconds.
  ~ Duration :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  ~ Bleeding duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Health Degeneration, Bleeding; aoe: nearby
Vocal Minority #883 | Hex Spell | Nightfall | E10 C1 R20
  For 5..20 seconds, target foe and all nearby foes cannot use shouts or chants.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # aoe: nearby
Weaken Armor #159 | Spell | Core | E5 C½ R5
  Target foe and foes adjacent to your target have Cracked Armor for 5..20 seconds.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Cracked Armor; target: foes; range: Casting; aoe: adjacent
Weaken Knees #822 | Elite Hex Spell | Factions | E5 C1 R5
  For 1..16 second[s], target foe suffers -1..4 Health degeneration and takes 5..20 damage while moving.
  ~ Duration :: 0-4: 1 2 3 4 5 | 5-9: 6 7 8 9 10 | 10-14: 11 12 13 14 15 | 15-19: 16 17 18 19 20 | 20-21: 21 22
  ~ Health degeneration :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  ~ Damage while moving :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Health Degeneration
Well of Darkness #1366 | Well Spell | Nightfall | E10 C1 R20
  Exploit nearest corpse or sacrifice 66% health to create a Well of Darkness for 5..50 seconds. Hexed foes within the Well of Darkness miss 50% of the time.
  ~ Well duration :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Exploits Corpse, Miss
Well of Ruin #2236 | Well Spell | Eye of the North | E10 C1 R20
  Exploit nearest corpse or sacrifice 66% health to create a Well of Ruin at its location. For 5..30 seconds, whenever a foe in the well takes physical damage, that foe has Cracked Armor for 5..20 seconds.
  ~ Well spell duration :: 0-4: 5 7 8 10 12 | 5-9: 13 15 17 18 20 | 10-14: 22 23 25 27 28 | 15-19: 30 32 33 35 37 | 20-21: 38 40
  ~ Cracked Armor duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Exploits Corpse, Cracked Armor; range: Casting; aoe: in the area
Well of Silence #1660 | Well Spell | Nightfall | E10 C1 R20
  Exploit target corpse or sacrifice 66% health to create a Well of Silence for 10..30 seconds. Foes within the well cannot use shouts or chants and suffer -1..4 Health degeneration.
  ~ Duration :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  ~ Health degeneration :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  # causes: Exploits Corpse, Health Degeneration
Well of Weariness #818 | Well Spell | Factions | E5 C1 R5
  Exploit target corpse or sacrifice 66% health to create a Well of Weariness for 10..55 seconds. Enemies within the Well of Weariness suffer -1 Energy degeneration.
  ~ Duration :: 0-4: 10 13 16 19 22 | 5-9: 25 28 31 34 37 | 10-14: 40 43 46 49 52 | 15-19: 55 58 61 64 67 | 20-21: 70 73
  # causes: Exploits Corpse, Energy Degeneration
Wither #125 | Elite Hex Spell | Prophecies | E10 C1 R5
  For 5..35 seconds, target foe suffers -2..4 Health degeneration and -1 Energy degeneration. If target foe's Energy reaches 0, that foe takes 15..75 damage and Wither ends.
  ~ Duration :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  ~ Health degeneration :: 0-4: 2 2 2 2 3 | 5-9: 3 3 3 3 3 | 10-14: 3 3 4 4 4 | 15-19: 4 4 4 4 5 | 20-21: 5 5
  ~ Damage :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  # causes: Health Degeneration, Energy Degeneration

### Necromancer / Death Magic
Animate Bone Fiend #84 | Spell | Core | E15 C1 R5
  Exploit nearest corpse to animate a level 1..17 bone fiend. Bone fiends can attack at range.
  ~ Level :: 0-4: 1 2 3 4 5 | 5-9: 6 7 8 10 11 | 10-14: 12 13 14 15 16 | 15-19: 17 18 19 20 21 | 20-21: 22 23
  # causes: Exploits Corpse, Minion; requires: Corpse; target: self; range: Casting; aoe: none
Animate Bone Horror #83 | Spell | Prophecies | E5 C1 R5
  Exploit nearest corpse to animate a level 1..17 bone horror.
  ~ Level :: 0-4: 1 2 3 4 5 | 5-9: 6 7 8 10 11 | 10-14: 12 13 14 15 16 | 15-19: 17 18 19 20 21 | 20-21: 22 23
  # causes: Exploits Corpse, Minion; requires: Corpse; target: self; range: Casting; aoe: none
Animate Bone Minions #85 | Spell | Core | E10 C1 R5
  Exploit nearest corpse to animate two level 0..12 bone minions.
  ~ Level :: 0-4: 0 1 2 2 3 | 5-9: 4 5 6 6 7 | 10-14: 8 9 10 10 11 | 15-19: 12 13 14 14 15 | 20-21: 16 17
  # causes: Exploits Corpse, Minion; requires: Corpse; target: self; range: Casting; aoe: none
Animate Flesh Golem #832 | Elite Spell | Factions | E10 C1 R30
  Exploit nearest corpse to animate a level 3..25 Flesh Golem. The Flesh Golem leaves 1..4 exploitable corpse(s). You can have only one Flesh Golem at a time.
  ~ Level :: 0-4: 3 4 6 7 9 | 5-9: 10 12 13 15 16 | 10-14: 18 19 21 22 24 | 15-19: 25 26 28 29 31 | 20-21: 32 34
  ~ Corpses left on death :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  # causes: Exploits Corpse, Minion; requires: Corpse; target: corpse; range: Casting; aoe: none
Animate Shambling Horror #1351 | Spell | Nightfall | E10 C1 R25
  Exploit nearest corpse to create a level 1..17 shambling horror. When the shambling horror dies, it is replaced by a level 0..15 jagged horror that causes Bleeding with each of its attacks.
  ~ Shambling Horror level :: 0-4: 1 2 3 4 5 | 5-9: 6 7 8 10 11 | 10-14: 12 13 14 15 16 | 15-19: 17 18 19 20 21 | 20-21: 22 23
  ~ Jagged Horror level :: 0-4: 0 1 2 3 4 | 5-9: 5 6 7 8 9 | 10-14: 10 11 12 13 14 | 15-19: 15 16 17 18 19 | 20-21: 20 21
  # causes: Exploits Corpse, Minion, Bleeding; requires: Corpse; target: untargeted; range: Casting; aoe: none
  ! ANOMALY: The descriptions do not mention the duration of the bleeding inflicted by the Jagged Horror.
Animate Vampiric Horror #805 | Spell | Factions | E10 C1 R15
  Exploit nearest corpse to animate a level 1..17 Vampiric Horror. Whenever a Vampiric Horror you control deals damage, you gain the same amount of Health.
  ~ Level :: 0-4: 1 2 3 4 5 | 5-9: 6 7 8 10 11 | 10-14: 12 13 14 15 16 | 15-19: 17 18 19 20 21 | 20-21: 22 23
  # causes: Exploits Corpse, Minion, Health Gain; requires: Corpse; target: untargeted; range: Casting; aoe: none
Aura of the Lich #114 | Elite Enchantment Spell | Prophecies | E15 C2 R45
  All corpses within earshot are exploited and you animate a level 1..17 bone horror plus one for each corpse exploited in this way. For 5..45 seconds, your Death Magic attribute is increased by +1.
  ~ Duration :: 0-4: 5 8 10 13 16 | 5-9: 18 21 24 26 29 | 10-14: 32 34 37 40 42 | 15-19: 45 48 50 53 56 | 20-21: 58 61
  ~ Level :: 0-4: 1 2 3 4 5 | 5-9: 6 7 8 10 11 | 10-14: 12 13 14 15 16 | 15-19: 17 18 19 20 21 | 20-21: 22 23
  # causes: Exploits Corpse, Minion, Increased Attribute; requires: Corpse; target: untargeted; aoe: earshot
Bitter Chill #1068 | Spell | Factions | E5 C1 R10
  Target foe is struck for 15..60 cold damage. If that foe had more Health than you, Bitter Chill recharges instantly.
  ~ Cold damage :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  # causes: Cold Damage, Recharge; target: foes
Blood of the Master #120 | Spell | Core | E5 S5%+ C1 R2
  All of your undead allies are healed for 30..116 Health. You sacrifice an additional 2% maximum Health per minion healed in this way.
  ~ Healing :: 0-4: 30 36 41 47 53 | 5-9: 59 64 70 76 82 | 10-14: 87 93 99 105 110 | 15-19: 116 122 127 133 139 | 20-21: 145 150
  # causes: Healing; target: self
  ! BUG: The concise description is wrong regarding only healing your own minions.
Consume Corpse #98 | Spell | Prophecies | E5 C1
  Exploit a random corpse. You teleport to that corpse's location and gain 25..100 Health and 5..20 Energy.
  ~ Health gain :: 0-4: 25 30 35 40 45 | 5-9: 50 55 60 65 70 | 10-14: 75 80 85 90 95 | 15-19: 100 105 110 115 120 | 20-21: 125 130
  ~ Energy gain :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Exploits Corpse, Health Gain, Energy Gain, Shadow Step; target: self
Contagion #1356 | Elite Enchantment Spell | Nightfall | E5 C1 R10
  For 60 seconds, whenever you suffer from a new condition, all foes in the area suffer from that same condition and you sacrifice 10..5% maximum Health.
  ~ Sacrifice % :: 0-4: 10 10 9 9 9 | 5-9: 8 8 8 7 7 | 10-14: 7 6 6 6 5 | 15-19: 5 5 4 4 4 | 20-21: 3 3
  # causes: Condition; target: untargeted; aoe: in the area
Dark Aura #116 | Enchantment Spell | Core | E10 C1 R10
  For 30 seconds, whenever target ally sacrifices Health, Dark Aura deals 5..50 shadow damage to adjacent foes, and you lose 5..20 Health.
  ~ Shadow damage :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  ~ Health loss :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Shadow Damage, Health Loss; target: allies; aoe: adjacent
  ! ANOMALY: Does not cause charmable animals to turn hostile.
Death Nova #104 | Enchantment Spell | Core | E5 C2
  For 30 seconds, if target ally dies, all adjacent foes take 26..100 damage and are Poisoned for 15 seconds.
  ~ Damage :: 0-4: 26 31 36 41 46 | 5-9: 51 56 61 65 70 | 10-14: 75 80 85 90 95 | 15-19: 100 105 110 115 120 | 20-21: 125 130
  # causes: Poison; target: allies; aoe: adjacent
Deathly Chill #89 | Spell | Prophecies | E10 C1 R5
  Target foe is struck for 5..50 cold damage. If that foe's Health is above 50%, you deal an additional 5..50 shadow damage.
  ~ Cold damage :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  ~ Shadow damage :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Cold Damage, Shadow Damage
Deathly Swarm #105 | Spell | Core | E10 C2 R6
  Deathly Swarm flies out slowly and strikes for 30..90 cold damage on up to three targets in the area.
  ~ Cold damage :: 0-4: 30 34 38 42 46 | 5-9: 50 54 58 62 66 | 10-14: 70 74 78 82 86 | 15-19: 90 94 98 102 106 | 20-21: 110 114
  # causes: Cold Damage; target: foes; aoe: in the area
Discord (PvP) #2863 | Elite Spell | Factions | E5 C2 R2
  If target foe is suffering from a condition and under the effects of a hex or an enchantment, that foe suffers 30..110 damage.
  ~ Damage :: 0-4: 30 35 41 46 51 | 5-9: 57 62 67 73 78 | 10-14: 83 89 94 99 105 | 15-19: 110 115 121 126 131 | 20-21: 137 142
Feast for the Dead #1354 | Spell | Nightfall | E5 C¼ R10
  Destroy target animated undead ally. All of your other animated undead allies are healed for 10..100 Health.
  ~ Healing :: 0-4: 10 16 22 28 34 | 5-9: 40 46 52 58 64 | 10-14: 70 76 82 88 94 | 15-19: 100 106 112 118 124 | 20-21: 130 136
  # causes: Healing; removes: minion; target: minions; range: Casting; aoe: none
Fetid Ground #841 | Spell | Factions | E5 C¾ R10
  Target foe is struck for 15..65 cold damage. If that foe is knocked down, that foe becomes Poisoned for 5..20 seconds.
  ~ Cold damage :: 0-4: 15 18 22 25 28 | 5-9: 32 35 38 42 45 | 10-14: 48 52 55 58 62 | 15-19: 65 68 72 75 78 | 20-21: 82 85
  ~ Poison duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Cold Damage, Poison; target: foes
Infuse Condition #139 | Enchantment Spell | Prophecies | E5 C1 R20
  For the next 15..60 seconds, whenever you receive a condition, that condition is transferred to your closest minion instead.
  ~ Duration :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  # causes: Condition; removes: Condition
  ! BUG: This skill does transfer Bleeding, Disease, and Poison to minions, despite them being non-fleshy.
Jagged Bones #1355 | Elite Enchantment Spell | Nightfall | E5 C1 R10
  For 60 seconds, whenever target undead servant dies, it is replaced by a level 0..15 jagged horror that causes Bleeding with each of its attacks.
  ~ Level :: 0-4: 0 1 2 3 4 | 5-9: 5 6 7 8 9 | 10-14: 10 11 12 13 14 | 15-19: 15 16 17 18 19 | 20-21: 20 21
  # causes: Minion, Bleeding; requires: Minion; target: minions; range: Casting; aoe: none
  ! ANOMALY: The descriptions do not mention the duration of the bleeding inflicted by the Jagged Horror.
Malign Intervention #122 | Hex Spell | Prophecies | E10 C1 R5
  For 5..20 seconds, target foe receives 20% less benefit from healing. If target foe dies while hexed with Malign Intervention, a level 1..17 masterless bone horror is summoned.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Level :: 0-4: 1 2 3 4 5 | 5-9: 6 7 8 10 11 | 10-14: 12 13 14 15 16 | 15-19: 17 18 19 20 21 | 20-21: 22 23
  # causes: Minion; requires: Death; target: foes; range: Casting; aoe: none
  ! ANOMALY: Cannot be used on non-fleshy targets.
Necrotic Traversal #97 | Spell | Prophecies | E5 C¾
  Exploit a random corpse or sacrifice 30..20% health to teleport to target foe's location. You become Diseased for 6 seconds and all nearby foes become Poisoned for 5..20 second[s].
  ~ Sacrifice :: 0-4: 30 29 29 28 27 | 5-9: 27 26 25 25 24 | 10-14: 23 23 22 21 21 | 15-19: 20 19 19 18 17 | 20-21: 17 16
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Exploits Corpse, Poison, Shadow Step; target: untargeted; aoe: nearby
Order of Undeath #1352 | Elite Spell | Nightfall | E10 C1 R5
  For 5 seconds, your minions deal +3..16 damage, but you lose 2% of your maximum Health whenever one of your minions hits with an attack.
  ~ + Damage :: 0-4: 3 4 5 6 6 | 5-9: 7 8 9 10 11 | 10-14: 12 13 13 14 15 | 15-19: 16 17 18 19 19 | 20-21: 20 21
  # causes: Health Loss
  ! BUG: This skill can not be cast if you are targeting someone under Spell Breaker, Vow of Silence etc. and triggers the spell Mistrust, acting like a target foe spell.
Putrid Bile #2058 | Hex Spell | Eye of the North | E10 C1 R12
  For 5..25 seconds, target foe suffers -1..3 Health degeneration. If that foe dies while under the effects of this hex, all nearby foes take 25..85 damage.
  ~ Duration :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  ~ Health degeneration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  ~ Damage :: 0-4: 25 29 33 37 41 | 5-9: 45 49 53 57 61 | 10-14: 65 69 73 77 81 | 15-19: 85 89 93 97 101 | 20-21: 105 109
  # causes: Health Degeneration
Putrid Explosion #95 | Spell | Core | E10 C1 R5
  The corpse nearest your target explodes, sending out a shockwave that deals 24..120 damage to nearby foes.
  ~ Damage :: 0-4: 24 30 37 43 50 | 5-9: 56 62 69 75 82 | 10-14: 88 94 101 107 114 | 15-19: 120 126 133 139 146 | 20-21: 152 158
  # target: allies or foes; aoe: nearby
Putrid Flesh #1353 | Spell | Nightfall | E10 C¼
  Destroy one of your target animated undead minions. All foes near that creature are Diseased for 5..15 seconds.
  ~ Duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Disease; removes: minion; target: minions; range: Casting; aoe: nearby
Rising Bile #935 | Hex Spell | Factions | E10 C1 R20
  For 20 seconds, this hex does nothing. When Rising Bile ends, that foe and all foes in the area take 1..6 damage for each second Rising Bile was in effect.
  ~ (1..6) [derived] :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  # aoe: in the area
Rotting Flesh #106 | Spell | Core | E15 C3 R3
  Target fleshy foe becomes Diseased for 10..25 seconds, slowly losing Health.
  ~ Duration :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  # causes: Disease
Soul Feast #96 | Spell | Core | E10 C1
  Exploit nearest corpse to gain 50..280 Health.
  ~ Health gain :: 0-4: 50 65 81 96 111 | 5-9: 127 142 157 173 188 | 10-14: 203 219 234 249 265 | 15-19: 280 295 311 326 341 | 20-21: 357 372
  # causes: Health Gain, Exploits Corpse
Tainted Flesh #113 | Elite Enchantment Spell | Core | E5 C1
  For 20..44 seconds, allies in the area are immune to disease, and anyone striking those allies in melee becomes Diseased for 3..15 seconds.
  ~ Duration :: 0-4: 20 22 23 25 26 | 5-9: 28 30 31 33 34 | 10-14: 36 38 39 41 42 | 15-19: 44 46 47 49 50 | 20-21: 52 54
  ~ Disease duration :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Condition Immunity, Disease; removes: Condition; target: untargeted; aoe: in the area
  ! BUG: Although this is a PBAoE skill with an effect centered around the caster, it still needs an allied target and you will run towards that target if not in cast range. Similar to Hex Eater Signet, the target won't be affected if it is not in range.
  ! BUG: Because it is a targeted enchantment spell, it will always trigger Shame and Mark of Subversion. If standing in a Well of the Profane, you will be able to cast this enchantment if you pick any ally in cast range that is not inside the well.
Taste of Death #152 | Spell | Core | E5 C¼
  Steal up to 100..400 Health from target animated undead ally.
  ~ Life stealing :: 0-4: 100 120 140 160 180 | 5-9: 200 220 240 260 280 | 10-14: 300 320 340 360 380 | 15-19: 400 420 440 460 480 | 20-21: 500 520
  # causes: Life Stealing; target: minions; range: Casting; aoe: none
Taste of Pain #1069 | Spell | Factions | E5 C¼ R10
  If target foe is below 50% Health, you gain 30..150 Health.
  ~ Health gain :: 0-4: 30 38 46 54 62 | 5-9: 70 78 86 94 102 | 10-14: 110 118 126 134 142 | 15-19: 150 158 166 174 182 | 20-21: 190 198
  # causes: Health Gain; target: foes
  ! BUG: Contrary to the concise description, this skill causes health gain and not healing.
Toxic Chill #1659 | Elite Spell | Nightfall | E5 C1 R5
  Target foe is struck for 15..75 cold damage. If that foe is under the effects of a hex or enchantment, that foe becomes Poisoned for 10..25 seconds.
  ~ Cold damage :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  ~ Poison duration :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  # causes: Cold Damage, Poison; target: foes
Verata's Aura #88 | Enchantment Spell | Prophecies | E15 S33% C¾ R30
  All hostile animated undead in the area become bound to you. Verata's Aura ends after 120..300 seconds. When Verata's Aura ends, you lose your bond with any undead bound to you. (50% failure chance with Death Magic 4 or less.)
  ~ Duration :: 0-4: 120 132 144 156 168 | 5-9: 180 192 204 216 228 | 10-14: 240 252 264 276 288 | 15-19: 300 312 324 336 348 | 20-21: 360 372
  # target: untargeted; aoe: in the area
  ! ANOMALY: Recasting Verata's Aura starts a new timer; it does not reset the original one (as would be the case with other enchantments). The minions covered by the original Aura will become masterless as scheduled; any created between the two castings will be covered by the second enchantment. Consider bringing self enchantment removal skills such as Contemplation of Purity, and only renew the enchantment near its end.
Verata's Gaze #87 | Spell | Prophecies | E5 C1 R5
  If target hostile animated undead has a master, its bond to its master is broken, making it hostile to all other creatures. If it had no master, you become its master and heal it for 60..80. (50% failure chance with Death Magic 4 or less.)
  ~ Healing :: 0-4: 60 61 63 64 65 | 5-9: 67 68 69 71 72 | 10-14: 73 75 76 77 79 | 15-19: 80 81 83 84 85 | 20-21: 87 88
  # causes: Healing; target: minions
  ! BUG: When casting Verata's Gaze on a masterless minion that was in a well, the effects of that well will persist even after the minion leaves, until the well expires.
  ! BUG: When used on a Bone Horror immediately after it was created via Malign Intervention, the Bone Horror becomes stuck and will not move until you engage an enemy.
  ! BUG: If this is cast on a minion, it will still follow its original owner, not the new owner. If the minion is turned hostile and then has this skill used on it as it is being summoned, it will follow the user of this skill, however if too slow it will follow its original owner again.
  ! ANOMALY: This skill has no aftercast delay.
Verata's Sacrifice #90 | Spell | Prophecies | E10 S15% C2 R60
  For 5..10 seconds, your undead allies gain +10 Health regeneration. All conditions are removed from those allies and transferred to you. If this spell is successful and you have control of 3 or fewer minions, Verata's Sacrifice instantly recharges.
  ~ Duration :: 0-4: 5 5 6 6 6 | 5-9: 7 7 7 8 8 | 10-14: 8 9 9 9 10 | 15-19: 10 10 11 11 11 | 20-21: 12 12
  # causes: Health Regeneration, Recharge, Condition; removes: Condition
  ! BUG: Heroes take minions of other party members into consideration.
  ! BUG: The concise description fails to mention that only the caster's undead servants are affected.
Vile Miasma #828 | Hex Spell | Factions | E10 C1 R15
  Target foe is struck for 10..65 cold damage. If suffering from a condition, that foe is hexed with Vile Miasma and suffers -1..5 Health degeneration for 10 seconds.
  ~ Cold damage :: 0-4: 10 14 17 21 25 | 5-9: 28 32 36 39 43 | 10-14: 47 50 54 58 61 | 15-19: 65 69 72 76 80 | 20-21: 83 87
  ~ Health degeneration :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Cold Damage, Health Degeneration
  ! ANOMALY: Unlike regular degeneration hexes, Vile Miasma causes a health bar to turn green such as poison or disease, or pink if used from bleeding.
Vile Touch #155 | Touch Skill | Core | E10 C¾ R2
  Skill. Touch target foe to deal 20..65 damage.
  ~ Damage :: 0-4: 20 23 26 29 32 | 5-9: 35 38 41 44 47 | 10-14: 50 53 56 59 62 | 15-19: 65 68 71 74 77 | 20-21: 80 83
  # target: foes; range: touch
Virulence #107 | Elite Spell | Prophecies | E5 C1 R15
  If target foe was already suffering from a condition, that foe suffers from Disease, Poison, and Weakness for 3..15 seconds.
  ~ Disease, Poison, and Weakness duration :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Disease, Poison, Weakness; target: foes
Well of Suffering #93 | Well Spell | Prophecies | E10 C1 R10
  Exploit nearest corpse or sacrifice 66% health to create a Well of Suffering at its location. For 10..30 seconds, foes in that area suffer -1..6 Health degeneration.
  ~ Duration :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  ~ Health degeneration :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  # causes: Exploits Corpse, Health Degeneration
  ! BUG: Only non-spirit foes experience the health degeneration.
Well of the Profane #94 | Well Spell | Core | E25 C3 R10
  Exploit nearest corpse or sacrifice 66% health to create a Well of the Profane at its location. For 8..20 seconds, foes in that area are stripped of all enchantments and cannot be the target of further enchantments. (50% failure chance with Death Magic 4 or less.)
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  # causes: Exploits Corpse; removes: Enchantment
  ! ANOMALY: Foes in this well lose all enchantments and cannot be the target of further enchantments; however, untargeted enchantments still work, which includes all flash enchantment spells, and spells like Shadow Refuge. These enchantments don’t get stripped simply by being inside the well, but only each time the well is entered. If one manages to gain an enchantment while inside (i.e. Aegis, Orders, etc.), it is not removed. [https://forum.guildwars.com/forum/forums/gamebugs/Well-of-the-Profane/ Source.]
Withering Aura #1997 | Enchantment Spell | Eye of the North | E5 C1 R3
  For 5..20 seconds, target ally's melee attacks cause Weakness for 5..20 seconds.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Weakness duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Weakness; target: allies
  ! ANOMALY: Unlike Grenth's Aura, switching to a melee weapon before a weapon projectile hits does not trigger this skill.

### Necromancer / No Attribute
Gaze of Contempt #766 | Spell | Factions | E10 C2 R10
  If target foe has more than 50% Health, that foe loses all enchantments.
  # removes: Enchantment; target: foes
Grenth's Balance #86 | Elite Spell | Core | E10 C¼ R10
  If target foe has more Health than you, you gain half the difference (up to your maximum Health), and that foe loses an equal amount. If this foe has less Health than you, you lose half the difference, and that foe gains an equal amount.
  # causes: Health Gain, Health Loss
  ! ANOMALY: The concise description omits the fact that your health gain (and your target's health loss) is capped by your maximum health.

### Necromancer / Soul Reaping
Angorodon's Gaze #2189 | Spell | Eye of the North | E5 C1 R10
  Steal 10..50 Health from target foe. If you are suffering from a condition, you gain 3..12 Energy.
  ~ Life stealing :: 0-4: 10 13 15 18 21 | 5-9: 23 26 29 31 34 | 10-14: 37 39 42 45 47 | 15-19: 50 53 55 58 61 | 20-21: 63 66
  ~ Energy gain :: 0-4: 3 4 4 5 5 | 5-9: 6 7 7 8 8 | 10-14: 9 10 10 11 11 | 15-19: 12 13 13 14 14 | 20-21: 15 16
  # causes: Life Stealing, Energy Gain; target: foes
Foul Feast #2057 | Spell | Eye of the North | E5 C¼ R4
  All conditions are transferred from target other ally to yourself. For each condition acquired in this way, you gain 0..45 Health and 2..4 Energy. This skill recharges twice as fast if you remove Disease from your target.
  ~ Healing :: 0-4: 0 3 6 9 12 | 5-9: 15 18 21 24 27 | 10-14: 30 33 36 39 42 | 15-19: 45 48 51 54 57 | 20-21: 60 63
  ~ Energy gain :: 0-4: 2 2 2 2 3 | 5-9: 3 3 3 3 3 | 10-14: 3 3 4 4 4 | 15-19: 4 4 4 4 5 | 20-21: 5 5
  # causes: Healing, Energy Gain, Decreased Recharge Time, Condition; removes: Condition; target: other allies
  ! ANOMALY: This Soul Reaping skill uses the Blood Magic casting symbol because it was originally a Blood Magic skill.
  ! BUG: If this skill transfers Disease, it will recharge in 2 seconds regardless of modifiers affecting its recharge such as Diversion.
  ! BUG: Contrary to the descriptions, this skill causes healing and not health gain.
  ! BUG: Activating this skill while hexed with Soul Bind will damage the user even if no conditions are transferred.
Hexer's Vigor #2138 | Enchantment Spell | Eye of the North | E5 C¼ R10
  For 10 seconds, you have +1..8 Health regeneration. Hexer's Vigor ends if you cast a non-hex skill.
  ~ Health regeneration :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  # causes: Health Regeneration
Icy Veins #821 | Elite Hex Spell | Factions | E10 C1 R5
  Target foe is struck for 10..90 cold damage. For 10..35 seconds, if target foe dies all nearby foes are struck for 20..110 cold damage.
  ~ Cold damage :: 0-4: 10 15 21 26 31 | 5-9: 37 42 47 53 58 | 10-14: 63 69 74 79 85 | 15-19: 90 95 101 106 111 | 20-21: 117 122
  ~ Duration :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  ~ Cold damage upon death :: 0-4: 20 26 32 38 44 | 5-9: 50 56 62 68 74 | 10-14: 80 86 92 98 104 | 15-19: 110 116 122 128 134 | 20-21: 140 146
  # causes: Cold Damage; aoe: nearby
Masochism (PvP) #3054 | Enchantment Spell | Eye of the North | E5 C1 R20
  For 30 seconds, you gain 1..3 Energy whenever you sacrifice Health.
  ~ Energy gain :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Energy Gain
  ! ANOMALY: Under rare circumstances, heroes with very low health will use a spell while under the effects of Masochism and accidentally kill themselves. [from PvE version page]
Reaper's Mark #808 | Elite Hex Spell | Nightfall | E5 C1 R10
  For 30 seconds, target foe suffers -1..5 Health degeneration. If that foe dies while hexed with Reaper's Mark, you gain 5..15 Energy.
  ~ Health degeneration :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  ~ Energy gain :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Health Degeneration, Energy Gain
Signet of Lost Souls #1365 | Signet | Nightfall | C¼ R8
  If target foe is below 50% Health, you gain 10..100 Health and 1..10 Energy.
  ~ Health gain :: 0-4: 10 16 22 28 34 | 5-9: 40 46 52 58 64 | 10-14: 70 76 82 88 94 | 15-19: 100 106 112 118 124 | 20-21: 130 136
  ~ Energy gain :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # causes: Health Gain, Energy Gain; target: foes
Signet of Sorrow #1363 | Signet | Nightfall | C1 R30
  Target foe takes 15..75 damage. If target foe is near a corpse or has a dead pet, this skill recharges instantly.
  ~ Damage :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  # causes: Recharge; target: foes
Wail of Doom #764 | Elite Hex Spell | Factions | E1 S10% C¼ R15
  For 2..6 second[s], all of target foe's attributes are set to 0.
  ~ Duration :: 0-4: 2 2 3 3 3 | 5-9: 3 4 4 4 4 | 10-14: 5 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 7 8
  # causes: Decreased Attribute; target: foes

## Mesmer

### Mesmer / Domination Magic
Aneurysm #2055 | Spell | Eye of the North | E5 C1 R5
  Target foe regains all Energy. For each point of Energy gained in this way, that foe takes 1..3 damage and all adjacent foes lose 1 Energy. (Maximum 1..30).
  ~ Damage per energy gain :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  ~ Maximum energy loss :: 0-4: 1 3 5 7 9 | 5-9: 11 13 15 16 18 | 10-14: 20 22 24 26 28 | 15-19: 30 32 34 36 38 | 20-21: 40 42
  # causes: Energy Gain, Energy Loss; target: foes; aoe: adjacent
  ! ANOMALY: Aneurysm does not take overcast into account when calculating how much energy to generate; as such, it combines well with skills that force overcast (such as Arcane Languor or Exhausting Assault) as it will deal high damage without actually returning energy.
Arcane Larceny #1062 | Spell | Factions | E10 C1
  For 5..35 seconds, one random spell is disabled for target foe and Arcane Larceny is replaced by that spell.
  ~ Duration :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  # causes: Disable, Skill Copying; target: foes; special: duplicate
Arcane Thievery #81 | Spell | Prophecies | E10 C1
  For 5..35 seconds, one random spell is disabled for target foe, and Arcane Thievery is replaced by that spell.
  ~ Duration :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  # causes: Disable, Skill Copying; target: foes; special: duplicate
Backfire #28 | Hex Spell | Core | E15 C3 R20
  For 10 seconds, whenever target foe casts a spell, that foe takes 35..140 damage.
  ~ Damage :: 0-4: 35 42 49 56 63 | 5-9: 70 77 84 91 98 | 10-14: 105 112 119 126 133 | 15-19: 140 147 154 161 168 | 20-21: 175 182
  # causes: Armor-ignoring Damage
Blackout #29 | Touch skill | Prophecies | E10 C1 R12
  Skill. For 2..8 seconds, all of touched target foe's skills are disabled, and all of your skills are disabled for 5 seconds.
  ~ Duration :: 0-4: 2 2 3 3 4 | 5-9: 4 4 5 5 6 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 10
  # causes: Disable; target: foes; range: touch
Chaos Storm #77 | Spell | Prophecies | E5 C2 R30
  Create a Chaos Storm at target foe's location that lasts for 10 seconds. Each second, foes adjacent to this location take 5..25 damage and lose 0..2 Energy.
  ~ Damage :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  ~ Energy loss :: 0-4: 0 0 0 0 1 | 5-9: 1 1 1 1 1 | 10-14: 1 1 2 2 2 | 15-19: 2 2 2 2 3 | 20-21: 3 3
  # causes: Energy Loss; target: foes; aoe: adjacent
Complicate #932 | Spell | Factions | E10 C¼ R20
  If target foe is using a skill, that skill is interrupted and disabled for target foe and all foes in the area for an additional 5..12 seconds.
  ~ Duration :: 0-4: 5 5 6 6 7 | 5-9: 7 8 8 9 9 | 10-14: 10 10 11 11 12 | 15-19: 12 12 13 13 14 | 20-21: 14 15
  # causes: Interrupt, Disable; target: foes; aoe: in the area
Cry of Frustration #57 | Spell | Core | E10 C¼ R20
  If target foe is using a skill, that foe and all foes in the area are interrupted and suffer 15..75 damage and foes in the area take 75% of that damage.
  ~ Target damage :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  ~ Area damage :: 0-4: 11 14 17 20 23 | 5-9: 26 29 32 35 38 | 10-14: 41 44 47 50 53 | 15-19: 56 59 62 65 68 | 20-21: 71 74
  # causes: Interrupt, Armor-ignoring Damage; target: foes; range: Casting; aoe: in the area
Diversion #30 | Hex Spell | Core | E10 C3 R12
  For 6 seconds, the next time target foe uses a skill, that skill takes an additional 10..56 seconds to recharge.
  ~ + Recharge time :: 0-4: 10 13 16 19 22 | 5-9: 25 28 31 35 38 | 10-14: 41 44 47 50 53 | 15-19: 56 59 62 65 68 | 20-21: 71 74
  # causes: Increased Recharge Time
Empathy (PvP) #3151 | Hex Spell | Core | E10 C2 R10
  For 5..15 seconds, whenever target foe attacks, that foe takes 15..45 damage.
  ~ Duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  ~ Damage :: 0-4: 15 17 19 21 23 | 5-9: 25 27 29 31 33 | 10-14: 35 37 39 41 43 | 15-19: 45 47 49 51 53 | 20-21: 55 57
  ! ANOMALY: Unlike Vigorous Spirit, Empathy triggers on failed attack skills.
  ! ANOMALY: Empathy triggers on failed attack skills, whereas Vigorous Spirit does not. [from PvE version page]
Enchanter's Conundrum (PvP) #3192 | Elite Hex Spell | Nightfall | E10 C2 R20
  For 10 seconds, target foe casts enchantments 100..200% slower. If target foe is not under the effects of an enchantment when this hex is applied, that foe takes 10..100 damage and all adjacent foes take 75% of that damage.
  ~ Cast time % increase :: 0-4: 100 107 113 120 127 | 5-9: 133 140 147 153 160 | 10-14: 167 173 180 187 193 | 15-19: 200 207 213 220 227 | 20-21: 233 240
  ~ Target damage :: 0-4: 10 16 22 28 34 | 5-9: 40 46 52 58 64 | 10-14: 70 76 82 88 94 | 15-19: 100 106 112 118 124 | 20-21: 130 136
  ~ Area damage :: 0-4: 8 12 17 21 26 | 5-9: 30 35 39 44 48 | 10-14: 53 57 62 66 71 | 15-19: 75 79 84 88 93 | 20-21: 97 102
  # causes: Increased Activation Time; aoe: adjacent
Energy Burn #42 | Spell | Core | E10 C2 R20
  Target foe loses 1..10 Energy and takes 9 damage for each point of Energy lost.
  ~ Energy loss :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Damage :: 0-4: 9 18 18 27 27 | 5-9: 36 45 45 54 54 | 10-14: 63 72 72 81 81 | 15-19: 90 99 99 108 108 | 20-21: 117 126
  # causes: Energy Loss
Energy Surge #39 | Elite Spell | Core | E5 C2 R15
  Target foe loses 1..10 Energy. For each point of Energy lost, that foe takes 7 damage and all nearby foes take 75% of that damage.
  ~ Energy loss :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Total Damage (Target) :: 0-4: 7 14 14 21 21 | 5-9: 28 35 35 42 42 | 10-14: 49 56 56 63 63 | 15-19: 70 77 77 84 84 | 20-21: 91 98
  # causes: Energy Loss; target: foes; aoe: nearby
Guilt #46 | Hex Spell | Prophecies | E5 C2 R25
  For 6 seconds, the next time target foe casts a spell that targets a foe, the spell fails and you steal up to 5..14 Energy from that foe.
  ~ Energy stolen :: 0-4: 5 6 6 7 7 | 5-9: 8 9 9 10 10 | 10-14: 11 12 12 13 13 | 15-19: 14 15 15 16 16 | 20-21: 17 18
  # causes: Energy Stealing
  ! ANOMALY: Contrary to the concise description, Guilt will take effect if the hexed character attempts to cast a spell on any NPC hostile to them, including other foes. For example, in Varajar Fells, an Ice Imp's Maelstrom will fail if they attempt to cast it on a Modniir Hunter.
Hex Breaker #10 | Stance | Core | E5 R15
  For 5..80 seconds, the next time you are the target of a hex, that hex fails and the caster takes 10..46 damage.
  ~ Duration :: 0-4: 5 10 15 20 25 | 5-9: 30 35 40 45 50 | 10-14: 55 60 65 70 75 | 15-19: 80 85 90 95 100 | 20-21: 105 110
  ~ Damage :: 0-4: 10 12 15 17 20 | 5-9: 22 24 27 29 32 | 10-14: 34 36 39 41 44 | 15-19: 46 48 51 53 56 | 20-21: 58 60
Hex Eater Vortex #1348 | Elite Spell | Nightfall | E5 C¼ R15
  Remove a hex from target ally. If a hex is removed in this way, foes in the area of that ally take 30..90 damage and lose one enchantment.
  ~ Damage :: 0-4: 30 34 38 42 46 | 5-9: 50 54 58 62 66 | 10-14: 70 74 78 82 86 | 15-19: 90 94 98 102 106 | 20-21: 110 114
  # removes: Hex spell, Enchantment; target: allies; aoe: in the area
Ignorance #35 | Hex Spell | Core | E10 C1 R10
  For 8..20 seconds target foe cannot use signets.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
Mind Wrack (PvP) #2734 | Hex Spell | Core | E5 C1 R7
  For 5..40 seconds, whenever this foe is the target of one of your non-hex Mesmer skills, that foe loses 1 Energy. If the target foe's Energy drops to 0, Mind Wrack ends and that foe takes 15..100 damage.
  ~ Duration :: 0-4: 5 7 10 12 14 | 5-9: 17 19 21 24 26 | 10-14: 28 31 33 35 38 | 15-19: 40 42 45 47 49 | 20-21: 52 54
  ~ Damage :: 0-4: 15 21 26 32 38 | 5-9: 43 49 55 60 66 | 10-14: 72 77 83 89 94 | 15-19: 100 106 111 117 123 | 20-21: 128 134
  # causes: Energy Loss
Mistrust (PvP) #3191 | Hex Spell | Nightfall | E10 C2 R12
  For 6 seconds, the next spell that target foe casts on one of your allies fails and deals 10..60 damage to that foe and 75% of that damage to all nearby foes.
  ~ Target Damage :: 0-4: 10 13 17 20 23 | 5-9: 27 30 33 37 40 | 10-14: 43 47 50 53 57 | 15-19: 60 63 67 70 73 | 20-21: 77 80
  ~ Area Damage :: 0-4: 8 10 13 15 18 | 5-9: 20 23 25 28 30 | 10-14: 33 35 38 40 43 | 15-19: 45 47 50 52 55 | 20-21: 57 60
  # aoe: nearby
  ! BUG: The damage multiplier of 75% also applies to target foe.
  ! ANOMALY: Mistrust will take effect if the hexed character attempts to cast a spell on any NPC hostile to them, including other foes. For example, in Varajar Fells, an Ice Imp's Maelstrom will fail if they attempt to cast it on a Modniir Hunter. [from PvE version page]
Overload #898 | Hex Spell | Factions | E5 C¼ R5
  For 5 seconds, target foe suffers -1..3 Health degeneration. If target foe is using a skill, then Overload deals 15..75 damage to that foe and 75% of that damage to all adjacent foes.
  ~ Conditional Damage (Target) :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  ~ Conditional Damage (Area) :: 0-4: 11 14 17 20 23 | 5-9: 26 29 32 35 38 | 10-14: 41 44 47 50 53 | 15-19: 56 59 62 65 68 | 20-21: 71 74
  ~ Health degeneration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Health Degeneration; aoe: adjacent
Panic #52 | Elite Hex Spell | Prophecies | E10 C1 R15
  For 1..10 second[s], target foe and all nearby foes are hexed with Panic. When a foe hexed with Panic successfully uses a skill, all other nearby foes are interrupted.
  ~ Duration :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # causes: Interrupt; aoe: nearby
  ! ANOMALY: Also interrupts passive charmable animals when they are near a foe hexed with Panic.
Power Block #5 | Elite Spell | Prophecies | E15 C¼ R20
  If target foe is casting a spell or chant, that skill and all skills of the same attribute are disabled for 1..12 seconds and that skill is interrupted.
  ~ Disabled duration :: 0-4: 1 2 2 3 4 | 5-9: 5 5 6 7 8 | 10-14: 8 9 10 11 11 | 15-19: 12 13 13 14 15 | 20-21: 16 16
  # causes: Disable, Interrupt
Power Flux #953 | Elite Hex Spell | Nightfall | E10 C¼ R15
  If target foe is casting a spell or chant, that skill is interrupted and for 4..10 seconds, that foe has -2 Energy degeneration.
  ~ Duration :: 0-4: 4 4 5 5 6 | 5-9: 6 6 7 7 8 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 12
  # causes: Interrupt, Energy Degeneration
Power Leak #24 | Spell | Prophecies | E10 C¼ R20
  If target foe is casting a spell or chant, that skill is interrupted and target foe loses 3..17 Energy.
  ~ Energy loss :: 0-4: 3 4 5 6 7 | 5-9: 8 9 10 10 11 | 10-14: 12 13 14 15 16 | 15-19: 17 18 19 20 21 | 20-21: 22 23
  # causes: Interrupt, Energy Loss; target: foes
Power Lock #1994 | Spell | Eye of the North | E5 C¼ R20
  If target foe is casting a spell or chant, that skill is interrupted and disabled for an additional 5..13 seconds.
  ~ Disable duration :: 0-4: 5 6 6 7 7 | 5-9: 8 8 9 9 10 | 10-14: 10 11 11 12 12 | 15-19: 13 14 14 15 15 | 20-21: 16 16
  # causes: Interrupt, Disable; target: foes
Power Spike #23 | Spell | Core | E5 C¼ R12
  If target foe is casting a spell or a chant, that skill is interrupted and target foe takes 30..120 damage.
  ~ Damage :: 0-4: 30 36 42 48 54 | 5-9: 60 66 72 78 84 | 10-14: 90 96 102 108 114 | 15-19: 120 126 132 138 144 | 20-21: 150 156
  # causes: Interrupt; target: foes
Price of Pride #1655 | Hex Spell | Nightfall | E5 C1 R8
  For 5 seconds, the next time target foe uses an elite skill, that foe loses 3..15 Energy.
  ~ Energy loss :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Energy Loss
  ! BUG: Second Wind does not trigger this skill.
Psychic Distraction #1053 | Elite Spell | Factions | E10 C¼ R2
  All of your other skills are disabled for 8 seconds. If target foe is using a skill, that skill is interrupted and disabled for an additional 5..12 seconds.
  ~ Duration :: 0-4: 5 5 6 6 7 | 5-9: 7 8 8 9 9 | 10-14: 10 10 11 11 12 | 15-19: 12 12 13 13 14 | 20-21: 14 15
  # causes: Interrupt, Disable; target: foes
  ! BUG: Contrary to the concise description, the interrupt does not need to succeed for the skill to become disabled.
Shame #51 | Hex Spell | Prophecies | E10 C2 R30
  For 6 seconds, the next time target foe casts a spell that targets an ally, the spell fails and you steal up to 5..14 Energy from that foe.
  ~ Energy stolen :: 0-4: 5 6 6 7 7 | 5-9: 8 9 9 10 10 | 10-14: 11 12 12 13 13 | 15-19: 14 15 15 16 16 | 20-21: 17 18
  # causes: Energy Stealing
Shatter Delusions (PvP) #3180 | Spell | Prophecies | E5 C¼ R10
  Remove one Mesmer hex from target foe. If a hex was removed, that foe takes 15..75 damage and all adjacent foes take 75% of that damage.
  ~ Target Damage :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  ~ Area Damage :: 0-4: 11 14 17 20 23 | 5-9: 26 29 32 35 38 | 10-14: 41 44 47 50 53 | 15-19: 56 59 62 65 68 | 20-21: 71 74
  # removes: Hex spell; target: foes; aoe: adjacent
Shatter Enchantment #69 | Spell | Core | E10 C1 R20
  Remove an enchantment from target foe. If an enchantment is removed, that foe takes 14..100 damage.
  ~ Damage :: 0-4: 14 20 25 31 37 | 5-9: 43 48 54 60 66 | 10-14: 71 77 83 89 94 | 15-19: 100 106 111 117 123 | 20-21: 129 134
  # removes: Enchantment; target: Foes; range: Casting
Shatter Hex #67 | Spell | Core | E10 C1 R10
  Remove a hex from target ally. If a hex is removed, foes near that ally take 30..120 damage.
  ~ Damage :: 0-4: 30 36 42 48 54 | 5-9: 60 66 72 78 84 | 10-14: 90 96 102 108 114 | 15-19: 120 126 132 138 144 | 20-21: 150 156
  # removes: Hex spell; target: allies; aoe: nearby
Signet of Disruption #860 | Signet | Factions | C¼ R15
  If target foe is casting a spell, the spell is interrupted and that foe suffers 10..51 damage. If that foe is hexed, Signet of Disruption can interrupt any non-spell skills.
  ~ Damage :: 0-4: 10 13 15 18 21 | 5-9: 24 26 29 32 35 | 10-14: 37 40 43 46 48 | 15-19: 51 54 56 59 62 | 20-21: 65 67
  # causes: Interrupt; target: foes
Signet of Distraction #1992 | Signet | Eye of the North | C¼ R15
  If target foe is casting a spell, that spell is interrupted and disabled for 1..5 seconds for each signet you have equipped.
  ~ Disabled duration :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Interrupt, Disable; target: foes
  ! BUG: Contrary to the concise description, the interrupt does not need to succeed for the spell to become disabled.
Signet of Weariness #59 | Signet | Prophecies | C2 R30
  Target foe and all nearby foes lose 3..8 Energy and suffer from Weakness for 1..12 second[s].
  ~ Energy loss :: 0-4: 3 3 4 4 4 | 5-9: 5 5 5 6 6 | 10-14: 6 7 7 7 8 | 15-19: 8 8 9 9 9 | 20-21: 10 10
  ~ Weakness duration :: 0-4: 1 2 2 3 4 | 5-9: 5 5 6 7 8 | 10-14: 8 9 10 11 11 | 15-19: 12 13 13 14 15 | 20-21: 16 16
  # causes: Energy Loss, Weakness; target: foes; aoe: nearby
Simple Thievery #1350 | Elite Spell | Nightfall | E10 C¼ R10
  Interrupt target foe's action. If that action was a skill, that skill is disabled for 5..20 seconds, and Simple Thievery is replaced by that skill.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Interrupt, Disable, Skill Copying; target: foes
Spiritual Pain (PvP) #3189 | Spell | Nightfall | E5 C1 R12
  Target foe takes 5..40 damage. All hostile summoned creatures in the area of that foe take 25..125 damage.
  ~ Damage :: 0-4: 5 7 10 12 14 | 5-9: 17 19 21 24 26 | 10-14: 28 31 33 35 38 | 15-19: 40 42 45 47 49 | 20-21: 52 54
  ~ Damage to summoned creatures :: 0-4: 25 32 38 45 52 | 5-9: 58 65 72 78 85 | 10-14: 92 98 105 112 118 | 15-19: 125 132 138 145 152 | 20-21: 158 165
  # target: foes; aoe: in the area
Unnatural Signet (PvP) #3188 | Signet | Factions | C1 R20
  Target foe takes 10..60 damage. If that foe is under the effects of a hex or enchantment, foes adjacent to your target take 10..60 damage. All your non-Mesmer skills except signets are disabled for 10 seconds.
  ~ Damage :: 0-4: 10 13 17 20 23 | 5-9: 27 30 33 37 40 | 10-14: 43 47 50 53 57 | 15-19: 60 63 67 70 73 | 20-21: 77 80
  ~ Damage to adjacent :: 0-4: 10 13 17 20 23 | 5-9: 27 30 33 37 40 | 10-14: 43 47 50 53 57 | 15-19: 60 63 67 70 73 | 20-21: 77 80
  # causes: Disable; target: foes; aoe: adjacent
Visions of Regret (PvP) #3234 | Elite Hex Spell | Nightfall | E10 C2 R30
  For 10 seconds, target foe and adjacent foes take 10..30 damage whenever they use a skill and 5..40 additional damage if not under the effects of another Mesmer hex.
  ~ Damage :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  ~ Conditional damage :: 0-4: 5 7 10 12 14 | 5-9: 17 19 21 24 26 | 10-14: 28 31 33 35 38 | 15-19: 40 42 45 47 49 | 20-21: 52 54
  # aoe: adjacent
Wastrel's Demise #1335 | Hex Spell | Nightfall | E5 C¼ R4
  For 5 seconds, target foe is hexed with Wastrel's Demise. Each second while hexed, target foe and all foes adjacent to that foe take 1..10 damage and an additional 1..10 damage for each second this spell is in effect. This hex ends prematurely if target foe uses a skill.
  ~ (1..10) [derived] :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # aoe: adjacent
  ! ANOMALY: If the hex is reapplied before it ends, Wastrel's Demise will continue to add up the bonus damage until the first hex would have run out. After that, the bonus damage cycle will start over.
  ! ANOMALY: Unlike most area damage over time skills, Wastrel's Demise does not cause AI to scatter.
Wastrel's Worry (PvP) #3447 | Hex Spell | Prophecies | E5 C¼ R4
  After 3 seconds, target foe takes 20..100 damage and all adjacent foes take 75% of that damage. If that foe successfully uses a skill, Wastrel's Worry ends prematurely and does no damage.
  ~ Target Damage :: 0-4: 20 25 31 36 41 | 5-9: 47 52 57 63 68 | 10-14: 73 79 84 89 95 | 15-19: 100 105 111 116 121 | 20-21: 127 132
  ~ Area Damage :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  # aoe: adjacent

### Mesmer / Fast Casting
Arcane Languor #804 | Elite Hex Spell | Factions | E10 C2 R15
  For 1..10 second[s], all spells cast by the target foe cause 10 Overcast.
  ~ Duration :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # causes: Overcast; target: foes; range: Casting; aoe: none
Keystone Signet #63 | Elite Signet | Prophecies | C1 R15
  All of your signets except Keystone Signet are recharged. For 20 seconds, the next 0..6 time[s] you use a signet that targets a foe, all other foes adjacent to your target take 15..60 damage and are interrupted.
  ~ Signet(s) :: 0-4: 0 0 1 1 2 | 5-9: 2 2 3 3 4 | 10-14: 4 4 5 5 6 | 15-19: 6 6 7 7 8 | 20-21: 8 8
  ~ Damage :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  # causes: Recharge, Interrupt; aoe: adjacent
  ! BUG: Some non-English descriptions incorrectly expand the area of effect beyond adjacent foes: the French full description adds nearby foes and the German concise description adds the target.
  ! BUG: At ranks 0-1 Fast Casting, all signets activated within the duration will deal damage and interrupt foes.
Mantra of Recovery #13 | Elite Stance | Core | E5 R15
  For 5..20 seconds, spells you cast recharge 33% faster.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Effective PvE recharge time (%)1 :: 0-4: 67 65 63 61 59 | 5-9: 57 55 53 51 49 | 10-14: 47 45 43 41 39 | 15-19: 37 35 33 31 29 | 20-21: 27 25
  # causes: Decreased Recharge Time
Persistence of Memory #1338 | Enchantment Spell | Nightfall | E5 C1 R20
  For 5..20 seconds, whenever a spell you cast is interrupted, that spell is instantly recharged.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Recharge
Power Return #931 | Spell | Factions | E5 C¼ R7
  If target foe is casting a spell or chant, that skill is interrupted and target foe gains 10..5 Energy.
  ~ Energy gain :: 0-4: 10 10 9 9 9 | 5-9: 8 8 8 7 7 | 10-14: 7 6 6 6 5 | 15-19: 5 5 4 4 4 | 20-21: 3 3
  # causes: Interrupt, Energy Gain; target: foes
Psychic Instability (PvP) #3185 | Elite Spell | Factions | E5 C¼ R20
  Interrupts the target foe's action. If that action is a skill, that foe and all adjacent foes are knocked down for 2..3 seconds. (50% failure chance with Fast Casting 4 or less.)
  ~ Duration :: 0-4: 2 2 2 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 3 3 | 15-19: 3 3 3 3 3 | 20-21: 3 3
  # causes: Interrupt, Knockdown; target: foes; aoe: adjacent
Stolen Speed (PvP) #3187 | Elite Hex Spell | Factions | E5 C1 R12
  For 1..10 second[s], spells cast by the target foe and all adjacent foes take 100% longer to cast. Spells you cast that target these foes take 50% less time to cast.
  ~ Duration :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # causes: Increased Activation Time, Decreased Activation Time; aoe: adjacent
Symbolic Celerity #1340 | Enchantment Spell | Nightfall | E15 C1 R30
  For 36..60 seconds, all of your signets use your Fast Casting attribute instead of their normal attributes.
  ~ Duration :: 0-4: 36 38 39 41 42 | 5-9: 44 46 47 49 50 | 10-14: 52 54 55 57 58 | 15-19: 60 62 63 65 66 | 20-21: 68 70
  # target: self
  ! ANOMALY: Items that grant a 20% chance of adding +1 to Fast Casting do not affect signets that are cast while this enchantment is active. For example, you cannot use "Master of My Domain" to obtain rank 21 in the table above. Instead, other signets will use the unmodified FC rank.
Symbolic Posture #1658 | Stance | Nightfall | E10 R20
  For 5..20 seconds, the next signet you activate recharges 20..80% faster.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Faster recharge % :: 0-4: 20 24 28 32 36 | 5-9: 40 44 48 52 56 | 10-14: 60 64 68 72 76 | 15-19: 80 84 88 92 96 | 20-21: 100 104
  # causes: Decreased Recharge Time
Symbols of Inspiration #1339 | Elite Skill | Nightfall | E5 C1 R10
  For 6..40 seconds, this skill becomes the Elite of target foe. Elite skills you cast use your Fast Casting attribute instead of their normal attributes.
  ~ Duration :: 0-4: 6 8 11 13 15 | 5-9: 17 20 22 24 26 | 10-14: 29 31 33 35 38 | 15-19: 40 42 45 47 49 | 20-21: 51 54
  # causes: Skill Copying; target: foes

### Mesmer / Illusion Magic
Accumulated Pain (PvP) #3184 | Spell | Factions | E5 C2 R15
  Target foe takes 10..35 damage. If target foe is suffering from 2 or more hexes, that foe suffers a Deep Wound for 5..20 seconds.
  ~ Damage :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  ~ Deep Wound duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Deep Wound; target: foes
Air of Disenchantment #1656 | Elite Hex Spell | Nightfall | E10 C1 R10
  Remove one enchantment from target foe and all nearby foes. For 5..20 seconds, enchantments expire 150..300% faster on those foes.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Enchantment expiration speed (%) :: 0-4: 150 160 170 180 190 | 5-9: 200 210 220 230 240 | 10-14: 250 260 270 280 290 | 15-19: 300 310 320 330 340 | 20-21: 350 360
  # removes: Enchantment; range: Casting; aoe: nearby
  ! ANOMALY: If an enchantment duration is reduced below 1 second, it behaves as if it was not applied.
  ! BUG: Although the description says "150..300% faster", the actual behavior is "at 150..300% the normal rate", which is only 50..200% faster.
Ancestor's Visage #1054 | Enchantment Spell | Factions | E10 C1 R20
  For 4..10 seconds, whenever target ally is hit by a melee attack, all adjacent foes lose all adrenaline and 3 Energy.
  ~ Duration :: 0-4: 4 4 5 5 6 | 5-9: 6 6 7 7 8 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 12
  # causes: Adrenaline Loss, Energy Loss; target: allies; aoe: adjacent; special: Duplicate
Arcane Conundrum #36 | Hex Spell | Core | E10 C2 R30
  For 5..15 seconds, spells cast by target foe and all adjacent foes take twice as long to cast. When this hex ends, you gain 1..7 energy.
  ~ Duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  ~ Energy gain :: 0-4: 1 1 2 2 3 | 5-9: 3 3 4 4 5 | 10-14: 5 5 6 6 7 | 15-19: 7 7 8 8 9 | 20-21: 9 9
  # causes: Increased Activation Time, Energy Gain; aoe: adjacent
  ! ANOMALY: Unlike other hexes that affect the caster, this one doesn't end if the caster dies.
Calculated Risk (PvP) #3196 | Hex Spell | Eye of the North | E10 C1 R12
  For 3..12 seconds, target foe's attacks do +10 damage, but there is a 50% chance that the damage from each attack will be done to that foe instead. (Maximum 15..60 damage.)
  ~ Duration :: 0-4: 3 4 4 5 5 | 5-9: 6 7 7 8 8 | 10-14: 9 10 10 11 11 | 15-19: 12 13 13 14 14 | 20-21: 15 16
  ~ Maximum damage :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
Clumsiness #43 | Hex Spell | Core | E10 C2 R12
  For 4 seconds, target and adjacent foes are hexed with Clumsiness. The next time each foe attacks, the attack is interrupted and that foe suffers 10..80 damage.
  ~ Damage :: 0-4: 10 15 19 24 29 | 5-9: 33 38 43 47 52 | 10-14: 57 61 66 71 75 | 15-19: 80 85 89 94 99 | 20-21: 103 108
  # causes: Interrupt; aoe: adjacent
  ! ANOMALY: Skills which prevent interruptions will trigger when hexed with Clumsiness but will not prevent their target from being interrupted nor from taking damage
Confusing Images #2137 | Hex Spell | Eye of the North | E10 C1 R20
  For 2..10 seconds, target foe takes twice as long to activate non-attack skills.
  ~ Duration :: 0-4: 2 3 3 4 4 | 5-9: 5 5 6 6 7 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 13
  # causes: Increased Activation Time
Conjure Nightmare #859 | Hex Spell | Factions | E15 C1 R5
  For 2..16 seconds, target foe suffers -8 Health degeneration.
  ~ Duration :: 0-4: 2 3 4 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 14 15 | 15-19: 16 17 18 19 20 | 20-21: 21 22
  # causes: Health Degeneration
Conjure Phantasm #31 | Hex Spell | Core | E10 C1 R5
  For 4..18 seconds, target foe experiences -5 Health degeneration.
  ~ Duration :: 0-4: 4 5 6 7 8 | 5-9: 9 10 11 11 12 | 10-14: 13 14 15 16 17 | 15-19: 18 19 20 21 22 | 20-21: 23 24
  # causes: Health Degeneration
Crippling Anguish (PvP) #3152 | Elite Hex Spell | Core | E10 C1 R20
  For 5..20 seconds, target moves 50% slower and suffers -2..6 Health degeneration.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Health degeneration :: 0-4: 2 2 3 3 3 | 5-9: 3 4 4 4 4 | 10-14: 5 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 7 8
  # causes: Decreased Movement Speed, Health Degeneration
Distortion #11 | Stance | Prophecies | E5 R8
  For 1..5 second[s], you have a 75% chance to block attacks. Whenever you block an attack this way, you lose 2 Energy or Distortion ends.
  ~ Duration :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Block, Energy Loss
Ethereal Burden #45 | Hex Spell | Prophecies | E15 R30
  For 6..12 seconds, target foe moves 50% slower. When Ethereal Burden ends, you gain 10..18 Energy.
  ~ Duration :: 0-4: 6 6 7 7 8 | 5-9: 8 8 9 9 10 | 10-14: 10 10 11 11 12 | 15-19: 12 12 13 13 14 | 20-21: 14 14
  ~ Energy gain :: 0-4: 10 11 11 12 12 | 5-9: 13 13 14 14 15 | 10-14: 15 16 16 17 17 | 15-19: 18 19 19 20 20 | 20-21: 21 21
  # causes: Decreased Movement Speed, Energy Gain; special: duplicate
Fevered Dreams (PvP) #3289 | Elite Hex Spell | Prophecies | E5 C1 R15
  For 5..15 seconds, whenever target foe suffers from a new condition, all foes in the area suffer from that condition as well.
  ~ Duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Condition; aoe: in the area
  ! BUG: Applying or reapplying the hex on a target suffering from one or more condition(s) will trigger the Dazed effect. [from PvE version page]
  ! BUG: The Dazed caused by this hex is always spread to foes in the area, even if the target was already Dazed. [from PvE version page]
  ! BUG: The Dazed caused by this hex triggers Fragility twice upon application on the target (but not on surrounding foes). [from PvE version page]
  ! BUG: If two foes hexed with Fevered Dreams are next to each other and one of them starts suffering from a new condition, both will be Dazed. [from PvE version page]
Fragility (PvP) #2998 | Hex Spell | Core | E5 C1 R8
  For 8..20 seconds, target and adjacent foes take 5..20 damage each time they suffer or recover from a new condition.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  ~ Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # aoe: adjacent
Frustration (PvP) #3190 | Hex Spell | Nightfall | E10 C1 R15
  For 5..20 seconds, target foe casts spells 50% slower and takes 5..50 damage whenever interrupted.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Damage :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Increased Activation Time
  ! BUG: A target will still take damage even if an effect prevents interruption. [from PvE version page]
Illusion of Haste (PvP) #3373 | Enchantment Spell | Core | E5 C1 R8
  For 5..11 seconds, you move 33% faster. When Illusion of Haste ends, you become Crippled for 3 seconds.
  ~ Duration :: 0-4: 5 5 6 6 7 | 5-9: 7 7 8 8 9 | 10-14: 9 9 10 10 11 | 15-19: 11 11 12 12 13 | 20-21: 13 13
  # causes: Increased Movement Speed, Crippled; target: self
Illusion of Pain (PvP) #3374 | Hex Spell | Factions | E10 C2 R5
  For 8 seconds, target foe has -3..10 Health degeneration and takes 3..10 damage each second. When Illusion of Pain ends or is reapplied, that foe is healed for 36..120.
  ~ Health degeneration :: 0-4: 3 3 4 4 5 | 5-9: 5 6 6 7 7 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 13
  ~ Damage each second :: 0-4: 3 3 4 4 5 | 5-9: 5 6 6 7 7 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 13
  ~ Healing :: 0-4: 36 42 47 53 58 | 5-9: 64 70 75 81 86 | 10-14: 92 98 103 109 114 | 15-19: 120 126 131 137 142 | 20-21: 148 154
  # causes: Health Degeneration, Healing
Illusion of Weakness #32 | Enchantment Spell | Prophecies | E10 C2 R30
  You lose 50..240 Health. Illusion of Weakness ends if damage drops your Health below 25% of your maximum. When Illusion of Weakness ends, you gain 50..240 Health.
  ~ Health loss :: 0-4: 50 63 75 88 101 | 5-9: 113 126 139 151 164 | 10-14: 177 189 202 215 227 | 15-19: 240 253 265 278 291 | 20-21: 303 316
  ~ Healing :: 0-4: 50 63 75 88 101 | 5-9: 113 126 139 151 164 | 10-14: 177 189 202 215 227 | 15-19: 240 253 265 278 291 | 20-21: 303 316
  # causes: Healing, Health Loss
  ! BUG: Despite the skill descriptions, this skill heals rather than provide health gain.
Illusionary Weaponry (PvP) #3181 | Elite Enchantment Spell | Prophecies | E5 C1 R10
  For 30 seconds, your melee attacks neither hit nor fail to hit. Instead, Illusionary Weaponry deals 20..60 damage to your targets for each melee attack.
  ~ Damage :: 0-4: 20 23 25 28 31 | 5-9: 33 36 39 41 44 | 10-14: 47 49 52 55 57 | 15-19: 60 63 65 68 71 | 20-21: 73 76
  # target: self
  ! BUG: Similarly to "I Am Unstoppable!" and Mantra of Signets, the armor provided by this skill is only applied at the end of the armor calculation. As such, it is not counted in the bonus armor cap of +25 and is not reduced by Armor penetration. [from PvE version page]
Images of Remorse #899 | Hex Spell | Factions | E5 C1 R5
  For 5..10 seconds, target foe suffers -1..3 Health degeneration. If that foe was attacking, that foe takes 10..52 damage.
  ~ Duration :: 0-4: 5 5 6 6 6 | 5-9: 7 7 7 8 8 | 10-14: 8 9 9 9 10 | 15-19: 10 10 11 11 11 | 20-21: 12 12
  ~ Health degeneration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  ~ Damage :: 0-4: 10 13 16 18 21 | 5-9: 24 27 30 32 35 | 10-14: 38 41 44 46 49 | 15-19: 52 55 58 60 63 | 20-21: 66 69
  # causes: Health Degeneration
Imagined Burden #76 | Hex Spell | Core | E15 C1 R30
  For 8..20 seconds, target foe moves 50% slower.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  # causes: Decreased Movement Speed
Ineptitude #47 | Elite Hex Spell | Prophecies | E10 C1 R15
  For 4 seconds, the next time target foe or any adjacent foe attacks, they take 30..135 damage and are Blinded for 10 seconds.
  ~ Damage :: 0-4: 30 37 44 51 58 | 5-9: 65 72 79 86 93 | 10-14: 100 107 114 121 128 | 15-19: 135 142 149 156 163 | 20-21: 170 177
  # causes: Blind; aoe: adjacent
Kitah's Burden #1056 | Hex Spell | Factions | E15 R30
  For 6..12 seconds, target foe moves 50% slower. When Kitah's Burden ends you gain 10..18 Energy.
  ~ Duration :: 0-4: 6 6 7 7 8 | 5-9: 8 8 9 9 10 | 10-14: 10 10 11 11 12 | 15-19: 12 12 13 13 14 | 20-21: 14 14
  ~ Energy gain :: 0-4: 10 11 11 12 12 | 5-9: 13 13 14 14 15 | 10-14: 15 16 16 17 17 | 15-19: 18 19 19 20 20 | 20-21: 21 21
  # causes: Decreased Movement Speed, Energy Gain; special: duplicate
Migraine (PvP) #3183 | Elite Hex Spell | Prophecies | E10 C2 R12
  For 4..16 seconds, target foe suffers -1..8 Health degeneration and takes 100% longer to activate skills.
  ~ Duration :: 0-4: 4 5 6 6 7 | 5-9: 8 9 10 10 11 | 10-14: 12 13 14 14 15 | 15-19: 16 17 18 18 19 | 20-21: 20 21
  ~ Health degeneration :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  # causes: Health Degeneration, Increased Activation Time
  ! BUG: Similar to Deadly Paradox, Migraine does not affect attack skill activation times. [from PvE version page]
  ! ANOMALY: Monsters won't cast Migraine on you when at least five of your skills are recharging. [from PvE version page]
Phantom Pain #44 | Hex Spell | Prophecies | E5 C2 R10
  For 10 seconds, target foe suffers -1..4 Health degeneration. When Phantom Pain ends, that foe suffers a Deep Wound, lowering that foe's maximum Health by 20% for 5..20 seconds.
  ~ Health degeneration :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  ~ Deep Wound duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Health Degeneration, Deep Wound
Recurring Insecurity #1055 | Elite Hex Spell | Factions | E10 C1 R3
  For 5 seconds, target foe suffers from -1..6 Health degeneration. If that foe has another hex when Recurring Insecurity would end, it is reapplied.
  ~ Health degeneration :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  # causes: Health Degeneration, Renewal
Shared Burden (PvP) #3186 | Elite Hex Spell | Factions | E10 C2 R20
  For 5..20 seconds, target foe and all foes in the area attack, cast spells, and move 33% slower.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Decreased Attack Speed, Increased Activation Time, Decreased Movement Speed; range: Casting; aoe: in the area
Shrinking Armor #2054 | Hex Spell | Eye of the North | E5 C1 R8
  For 10 seconds, target foe suffers from -1..4 Health degeneration. When this hex ends, that foe has Cracked Armor for 5..20 seconds.
  ~ Health degeneration :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  ~ Cracked Armor duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Health Degeneration, Cracked Armor; range: Casting
Signet of Clumsiness (PvP) #3193 | Signet | Nightfall | C¼ R12
  If target foe is attacking, that foe and all adjacent foes are interrupted and take 15..60 damage. Any foes using attack skills are knocked down.
  ~ Damage :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  # causes: Interrupt, Knockdown; target: foes; aoe: adjacent
Signet of Illusions #1346 | Elite Signet | Nightfall | C2 R5
  Your next 1..3 non-Illusion spell[s] use your Illusion attribute instead of its normal attribute.
  ~ Spells :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  ! ANOMALY: Items that grant a 20% chance of adding +1 to Illusion Magic do not affect spells cast while this signet is active. For example, you cannot use "Master of My Domain" to obtain rank 21 in the table above. Instead, spells will use the unmodified Illusion rank.
Soothing Images #56 | Hex Spell | Core | E15 C2 R8
  For 8..20 seconds, target foe and all adjacent foes cannot gain adrenaline.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  # aoe: adjacent
Sum of All Fears #1996 | Hex Spell | Eye of the North | E10 R10
  For 4..12 second[s], target foe moves, attacks, and casts spells 33% slower.
  ~ Duration :: 0-4: 4 5 5 6 6 | 5-9: 7 7 8 8 9 | 10-14: 9 10 10 11 11 | 15-19: 12 13 13 14 14 | 20-21: 15 15
  # causes: Decreased Movement Speed, Decreased Attack Speed, Increased Activation Time
Sympathetic Visage #34 | Enchantment Spell | Prophecies | E10 C1 R20
  For 4..10 seconds, whenever target ally is hit by a melee attack, all adjacent foes lose all adrenaline and 3 Energy.
  ~ Duration :: 0-4: 4 4 5 5 6 | 5-9: 6 6 7 7 8 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 12
  # causes: Adrenaline Loss, Energy Loss; target: allies; aoe: adjacent; special: Duplicate
Wandering Eye (PvP) #3195 | Hex Spell | Eye of the North | E10 C2 R12
  For 4 seconds, the next time target foe attacks, that attack is interrupted and all nearby foes take 10..92 damage.
  ~ Damage :: 0-4: 10 15 21 26 32 | 5-9: 37 43 48 54 59 | 10-14: 65 70 76 81 87 | 15-19: 92 97 103 108 114 | 20-21: 119 125
  # causes: Interrupt; aoe: nearby
  ! ANOMALY: Skills which prevent interruptions will trigger when hexed with Wandering Eye but will not prevent their target from being interrupted nor from taking damage
  ! ANOMALY: Skills which prevent interruptions will trigger when hexed with Wandering Eye but will not prevent their target from being interrupted nor from taking damage [from PvE version page]
  ! ANOMALY: Miniatures seem to trigger the damage animation of this spell. [from PvE version page]

### Mesmer / Inspiration Magic
Auspicious Incantation #930 | Enchantment Spell | Factions | E5 C1 R20
  For 20 seconds, the next spell you cast is disabled for an additional 10..5 seconds, and you gain 110..200% of that spell's Energy cost.
  ~ Disabled duration :: 0-4: 10 10 9 9 9 | 5-9: 8 8 8 7 7 | 10-14: 7 6 6 6 5 | 15-19: 5 5 4 4 4 | 20-21: 3 3
  ~ % of energy cost :: 0-4: 110 116 122 128 134 | 5-9: 140 146 152 158 164 | 10-14: 170 176 182 188 194 | 15-19: 200 206 212 218 224 | 20-21: 230 236
  # causes: Increased Recharge Time, Disable, Energy Gain
Channeling #38 | Enchantment Spell | Prophecies | E5 C1 R10
  For 8..56 seconds, whenever you cast a spell, you gain 1 Energy for each foe in the area.
  ~ Duration :: 0-4: 8 11 14 18 21 | 5-9: 24 27 30 34 37 | 10-14: 40 43 46 50 53 | 15-19: 56 59 62 66 69 | 20-21: 72 75
  # causes: Energy Gain; target: self
Discharge Enchantment #1347 | Spell | Nightfall | E10 C1 R15
  Remove one enchantment from target foe. If that foe is hexed, this skill recharges 20..50% faster.
  ~ % faster recharge :: 0-4: 20 22 24 26 28 | 5-9: 30 32 34 36 38 | 10-14: 40 42 44 46 48 | 15-19: 50 52 54 56 58 | 20-21: 60 62
  # causes: Decreased Recharge Time; removes: Enchantment; target: foes
Drain Delusions #1337 | Spell | Nightfall | E5 C¼ R12
  Remove one Mesmer hex from target foe. If a hex was removed in this way, that foe loses 1..5 Energy and you gain 4 Energy for each point lost.
  ~ Energy loss :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  ~ Energy gain :: 0-4: 4 4 8 8 8 | 5-9: 8 12 12 12 12 | 10-14: 16 16 16 16 20 | 15-19: 20 20 24 24 24 | 20-21: 24 28
  # causes: Energy Loss, Energy Gain; removes: Hex spell; target: foes; range: Casting; aoe: none
Drain Enchantment #68 | Spell | Core | E5 C2 R20
  Remove an enchantment from target foe. If an enchantment is removed, you gain 8..17 Energy and 40..120 Health.
  ~ Energy gain :: 0-4: 8 9 9 10 10 | 5-9: 11 12 12 13 13 | 10-14: 14 15 15 16 16 | 15-19: 17 18 18 19 19 | 20-21: 20 21
  ~ Health gain :: 0-4: 40 45 51 56 61 | 5-9: 67 72 77 83 88 | 10-14: 93 99 104 109 115 | 15-19: 120 125 131 136 141 | 20-21: 147 152
  # causes: Energy Gain, Health Gain; removes: Enchantment; target: Foes; range: Casting
Elemental Resistance #72 | Stance | Prophecies | E10 R20
  For 30..90 seconds, You gain +40 armor against elemental damage, but you lose 24..12 armor against physical damage.
  ~ Duration :: 0-4: 30 34 38 42 46 | 5-9: 50 54 58 62 66 | 10-14: 70 74 78 82 86 | 15-19: 90 94 98 102 106 | 20-21: 110 114
  ~ - Armor against physical damage :: 0-4: 24 23 22 22 21 | 5-9: 20 19 18 18 17 | 10-14: 16 15 14 14 13 | 15-19: 12 11 10 10 9 | 20-21: 8 7
  # causes: Increased Armor Rating, Decreased Armor Rating
  ! BUG: Similar to Cracked Armor, this skill will not lower your armor rating below 60 or your "core" armor rating, if your "core" armor rating is lower than 60.
  ! BUG: If you use a skill or combination of skills and effects that, after subtraction of the penalty from Elemental Resistance, still grants +26 or more armor rating against physical damage, Elemental Resistance's armor penalty does not function. See also armor calculation.
Energy Drain #79 | Elite Spell | Core | E5 C1 R20
  Target foe loses 2..9 Energy. You gain 3 Energy for each point of Energy lost.
  ~ Energy loss :: 0-4: 2 2 3 3 4 | 5-9: 4 5 5 6 6 | 10-14: 7 7 8 8 9 | 15-19: 9 9 10 10 11 | 20-21: 11 12
  ~ Energy gain :: 0-4: 6 6 9 9 12 | 5-9: 12 15 15 18 18 | 10-14: 21 21 24 24 27 | 15-19: 27 27 30 30 33 | 20-21: 33 36
  # causes: Energy Loss, Energy Gain; target: foes; range: Casting; aoe: none
Energy Tap #80 | Spell | Core | E5 C2 R30
  Target foe loses 4..7 Energy. You gain 2 Energy for each point of Energy lost.
  ~ Energy loss :: 0-4: 4 4 4 5 5 | 5-9: 5 5 5 6 6 | 10-14: 6 6 6 7 7 | 15-19: 7 7 7 8 8 | 20-21: 8 8
  ~ Energy gain :: 0-4: 8 8 8 10 10 | 5-9: 10 10 10 12 12 | 10-14: 12 12 12 14 14 | 15-19: 14 14 14 16 16 | 20-21: 16 16
  # causes: Energy Loss, Energy Gain; target: foes
Ether Feast #40 | Spell | Core | E5 C1 R8
  Target foe loses 3 Energy. You are healed 20..65 for each point of Energy lost.
  ~ Heal per energy lost :: 0-4: 20 23 26 29 32 | 5-9: 35 38 41 44 47 | 10-14: 50 53 56 59 62 | 15-19: 65 68 71 74 77 | 20-21: 80 83
  ~ Maximum healing :: 0-4: 60 69 78 87 96 | 5-9: 105 114 123 132 141 | 10-14: 150 159 168 177 186 | 15-19: 195 204 213 222 231 | 20-21: 240 249
  # causes: Energy Loss, Healing; target: foes
  ! BUG: Contrary to the concise description, this skill causes healing and not health gain.
Ether Lord #41 | Hex Spell | Prophecies | E5 C2 R20
  You lose all Energy. For 5..10 seconds, target foe suffers -1..3 Energy degeneration, and you experience +1..3 Energy regeneration.
  ~ Duration :: 0-4: 5 5 6 6 6 | 5-9: 7 7 7 8 8 | 10-14: 8 9 9 9 10 | 15-19: 10 10 11 11 11 | 20-21: 12 12
  ~ Energy degeneration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  ~ Energy regeneration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Energy Loss, Energy Degeneration, Energy Regeneration; target: foes
Ether Phantom #1343 | Hex Spell | Nightfall | E5 C1 R10
  For 10 seconds, target foe has -1 Energy degeneration. If this hex is removed prematurely, that foe loses 1..5 Energy.
  ~ Energy loss :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Energy Degeneration, Energy Loss
  ! BUG: Ether Phantom stacks with itself causing multiple energy loss when removed prematurely
Ether Signet #881 | Signet | Factions | C1 R45
  If you have less than 5..10 Energy, gain 10..20 Energy.
  ~ Max energy req. :: 0-4: 5 5 6 6 6 | 5-9: 7 7 7 8 8 | 10-14: 8 9 9 9 10 | 15-19: 10 10 11 11 11 | 20-21: 12 12
  ~ Energy gain :: 0-4: 10 11 11 12 13 | 5-9: 13 14 15 15 16 | 10-14: 17 17 18 19 19 | 15-19: 20 21 21 22 23 | 20-21: 23 24
  # causes: Energy Gain
Extend Conditions #1333 | Elite Spell | Nightfall | E5 C¼ R5
  Spread all conditions from target foe to foes near your target. The durations of those conditions are increased by 5..100% (maximum 30 seconds).
  ~ Longer duration of conditions (%) :: 0-4: 5 11 18 24 30 | 5-9: 37 43 49 56 62 | 10-14: 68 75 81 87 94 | 15-19: 100 106 113 119 125 | 20-21: 132 138
  # causes: Condition; target: foes; aoe: nearby
Feedback #1061 | Spell | Factions | E10 C1 R30
  Target foe loses one enchantment. If an enchantment is removed in this way, that foe also loses 4..10 Energy.
  ~ Energy loss :: 0-4: 4 4 5 5 6 | 5-9: 6 6 7 7 8 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 12
  # causes: Energy Loss; removes: Enchantment; target: foes
Hex Eater Signet #1059 | Touch Signet | Factions | C1 R15
  Signet. Target touched ally and up to 2..5 adjacent allies each lose one hex. You gain 1..4 Energy for each hex removed this way.
  ~ Adjacent allies :: 0-4: 2 2 2 3 3 | 5-9: 3 3 3 4 4 | 10-14: 4 4 4 5 5 | 15-19: 5 5 5 6 6 | 20-21: 6 6
  ~ Energy gain :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  # causes: Energy Gain; removes: Hex spell; target: allies; range: touch; aoe: adjacent
  ! ANOMALY: The PBAoE effect is centered around the caster, not the touched target.
  ! BUG: Although you can target an ally with this skill (and will touch it), hexes will be removed from party members only, not even allies listed in the party window.
  ! BUG: The touched target will not necessarily have a hex removed if it is not a party member, runs out of range during cast or if there are 2..5 hexed party members in the party window above the target.
  ! BUG: The total number of hexes removed is 2..5.
Inspired Enchantment #21 | Spell | Prophecies | E10 C1
  Removes an enchantment from target foe and gain 3..15 Energy. For 20 seconds, Inspired Enchantment is replaced with the enchantment removed from target foe.
  ~ Energy gain :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Energy Gain, Recharge, Skill Copying; removes: Enchantment; target: foes; special: duplicate
Inspired Hex #22 | Spell | Prophecies | E5 C1
  Remove a hex from target ally and gain 4..10 Energy. For 20 seconds, Inspired Hex is replaced with the hex that was removed.
  ~ Energy gain :: 0-4: 4 4 5 5 6 | 5-9: 6 6 7 7 8 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 12
  # causes: Energy Gain, Recharge, Skill Copying; removes: Hex spell; target: allies; special: duplicate
Leech Signet #61 | Signet | Core | C¼ R30
  Interrupt target foe's action. If that action was a spell, you gain 3..15 Energy.
  ~ Energy gain :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Interrupt, Energy Gain; target: foes
Lyssa's Aura #813 | Elite Enchantment Spell | Factions | E5 C1 R30
  For 10 seconds, you have +0..5 Energy regeneration. This enchantment reapplies itself every time you cast a spell on a foe.
  ~ Energy regeneration :: 0-4: 0 0 1 1 1 | 5-9: 2 2 2 3 3 | 10-14: 3 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 7 7
  # causes: Energy Regeneration, Renewal
Mantra of Concentration #16 | Stance | Prophecies | E5 R30
  For 1..38 seconds, the next time you would be interrupted, you are not interrupted.
  ~ Duration :: 0-4: 1 3 6 8 11 | 5-9: 13 16 18 21 23 | 10-14: 26 28 31 33 36 | 15-19: 38 40 43 45 48 | 20-21: 50 53
Mantra of Earth #6 | Stance | Core | E10 R20
  For 30..90 seconds, whenever you take earth damage, the damage is reduced by 26..50% and you gain 2 Energy.
  ~ Duration :: 0-4: 30 34 38 42 46 | 5-9: 50 54 58 62 66 | 10-14: 70 74 78 82 86 | 15-19: 90 94 98 102 106 | 20-21: 110 114
  ~ Earth damage reduction % :: 0-4: 26 28 29 31 32 | 5-9: 34 36 37 39 40 | 10-14: 42 44 45 47 48 | 15-19: 50 52 53 55 56 | 20-21: 58 60
  # causes: Damage Reduction, Energy Gain
Mantra of Flame #7 | Stance | Core | E10 R20
  For 30..90 seconds, whenever you take fire damage, the damage is reduced by 26..50% and you gain 2 Energy.
  ~ Duration :: 0-4: 30 34 38 42 46 | 5-9: 50 54 58 62 66 | 10-14: 70 74 78 82 86 | 15-19: 90 94 98 102 106 | 20-21: 110 114
  ~ Fire damage reduction % :: 0-4: 26 28 29 31 32 | 5-9: 34 36 37 39 40 | 10-14: 42 44 45 47 48 | 15-19: 50 52 53 55 56 | 20-21: 58 60
  # causes: Damage Reduction, Energy Gain
Mantra of Frost #8 | Stance | Core | E10 R20
  For 30..90 seconds, whenever you take cold damage, the damage is reduced by 26..50% and you gain 2 Energy.
  ~ Duration :: 0-4: 30 34 38 42 46 | 5-9: 50 54 58 62 66 | 10-14: 70 74 78 82 86 | 15-19: 90 94 98 102 106 | 20-21: 110 114
  ~ Cold damage reduction % :: 0-4: 26 28 29 31 32 | 5-9: 34 36 37 39 40 | 10-14: 42 44 45 47 48 | 15-19: 50 52 53 55 56 | 20-21: 58 60
  # causes: Damage Reduction, Energy Gain
Mantra of Inscriptions #15 | Stance | Core | E10 R20
  For 5..25 seconds, signets you successfully activate while in this stance recharge 10..40% faster.
  ~ Duration :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  ~ Faster recharge % :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Decreased Recharge Time
Mantra of Lightning #9 | Stance | Core | E10 R20
  For 30..90 seconds, whenever you take lightning damage, the damage is reduced by 26..50% and you gain 2 Energy.
  ~ Duration :: 0-4: 30 34 38 42 46 | 5-9: 50 54 58 62 66 | 10-14: 70 74 78 82 86 | 15-19: 90 94 98 102 106 | 20-21: 110 114
  ~ Lightning damage reduction % :: 0-4: 26 28 29 31 32 | 5-9: 34 36 37 39 40 | 10-14: 42 44 45 47 48 | 15-19: 50 52 53 55 56 | 20-21: 58 60
  # causes: Damage Reduction, Energy Gain
Mantra of Persistence #14 | Stance | Core | E5 R15
  For 5..25 seconds, any Illusion Magic hex you cast lasts 10..40% longer.
  ~ Duration :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  ~ Longer duration % :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
Mantra of Recall #82 | Elite Enchantment Spell | Prophecies | E10 C1 R30
  For 20 seconds, you gain no benefit from it. You gain 10..25 Energy when Mantra of Recall ends.
  ~ Energy gain :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  # causes: Energy Gain
Mantra of Resolve (PvP) #3063 | Stance | Core | E10 R20
  For 5 seconds, you cannot be interrupted, but each time you would have been interrupted, you lose 10..4 Energy or Mantra of Resolve ends.
  ~ Energy loss :: 0-4: 10 10 9 9 8 | 5-9: 8 8 7 7 6 | 10-14: 6 6 5 5 4 | 15-19: 4 4 3 3 2 | 20-21: 2 2
  # causes: Energy Loss
Mantra of Signets (PvP) #3179 | Stance | Prophecies | E5 R20
  For 10..40 seconds, you have +3 armor for each signet you have equipped. Whenever you use a signet, you gain 5..60 Health.
  ~ Duration :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  ~ Healing :: 0-4: 5 9 12 16 20 | 5-9: 23 27 31 34 38 | 10-14: 42 45 49 53 56 | 15-19: 60 64 67 71 75 | 20-21: 78 82
  # causes: Healing
  ! BUG: Contrary to the descriptions, this skill causes healing and not health gain.
  ! BUG: Similarly to Illusionary Weaponry and "I Am Unstoppable!", the armor provided by this skill is only applied at the end of the armor calculation. As such, it is not counted in the bonus armor cap of +25 and is not reduced by Armor penetration. [from PvE version page]
  ! BUG: Contrary to the descriptions, this skill causes healing and not health gain. [from PvE version page]
Physical Resistance #73 | Stance | Prophecies | E10 R20
  For 30..90 seconds, You gain +40 armor against physical damage, but you lose 24..12 armor against elemental damage.
  ~ Duration :: 0-4: 30 34 38 42 46 | 5-9: 50 54 58 62 66 | 10-14: 70 74 78 82 86 | 15-19: 90 94 98 102 106 | 20-21: 110 114
  ~ - Armor against elemental damage :: 0-4: 24 23 22 22 21 | 5-9: 20 19 18 18 17 | 10-14: 16 15 14 14 13 | 15-19: 12 11 10 10 9 | 20-21: 8 7
  # causes: Increased Armor Rating, Decreased Armor Rating
  ! BUG: Similar to Cracked Armor, this skill will not lower your armor rating below 60 or your "core" armor rating, if your "core" armor rating is lower than 60.
  ! BUG: If you use a skill or combination of skills and effects that, after subtraction of the penalty from Physical Resistance, still grants +26 or more armor rating against elemental damage, Physical Resistance's armor penalty does not function. See also armor calculation.
Power Drain #25 | Spell | Core | E5 C¼ R20
  If target foe is casting a spell or chant, that skill is interrupted and you gain 1..31 Energy.
  ~ Energy gain :: 0-4: 1 3 5 7 9 | 5-9: 11 13 15 17 19 | 10-14: 21 23 25 27 29 | 15-19: 31 33 35 37 39 | 20-21: 41 43
  # causes: Interrupt, Energy Gain; target: foes
Power Leech #803 | Elite Hex Spell | Factions | E5 C¼ R20
  If target foe is casting a spell or chant, that skill is interrupted and for 10 seconds, whenever that foe casts a spell, you steal up to 5..15 Energy from that foe.
  ~ Energy stolen :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Interrupt, Energy Stealing
Revealed Enchantment #1048 | Spell | Factions | E10 C1
  Remove an enchantment from target foe and gain 3..15 Energy. For 20 seconds, Revealed Enchantment is replaced with the enchantment removed from target foe.
  ~ Energy gain :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Energy Gain, Recharge, Skill Copying; removes: Enchantment; target: foes; special: duplicate
Revealed Hex #1049 | Spell | Factions | E5 C1
  Remove a hex from target ally and gain 4..10 Energy. For 20 seconds, Revealed Hex is replaced with the hex that was removed.
  ~ Energy gain :: 0-4: 4 4 5 5 6 | 5-9: 6 6 7 7 8 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 12
  # causes: Energy Gain, Recharge, Skill Copying; removes: Hex spell; target: allies; special: duplicate
Signet of Humility #62 | Signet | Core | C3 R20
  Target foe's elite skill is disabled for 1..16 second[s]. Your non-Mesmer skills are disabled for 4 seconds.
  ~ Duration :: 0-4: 1 2 3 4 5 | 5-9: 6 7 8 9 10 | 10-14: 11 12 13 14 15 | 15-19: 16 17 18 19 20 | 20-21: 21 22
  # causes: Disable; target: foes
Signet of Recall #1993 | Signet | Eye of the North | C¼ R20
  For 6 seconds, you have -4 Energy regeneration. When this effect ends, you gain 13..20 Energy.
  ~ Energy gain :: 0-4: 13 13 14 14 15 | 5-9: 15 16 16 17 17 | 10-14: 18 18 19 19 20 | 15-19: 20 20 21 21 22 | 20-21: 22 23
  # causes: Energy Degeneration, Energy Gain
Spirit of Failure #48 | Hex Spell | Prophecies | E15 C3 R20
  For 30 seconds, target foe has a 25% chance to miss with attacks. You gain 1..3 Energy whenever that foe fails to hit in combat.
  ~ Energy gain :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Miss, Energy Gain; target: foes
Spirit Shackles #66 | Hex Spell | Core | E10 C3 R8
  For 5..20 seconds, target foe loses 5 Energy whenever that foe attacks.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Energy Loss
Tease (PvP) #3463 | Elite Spell | Nightfall | E5 C¼ R20
  If target foe is using a skill, that foe and other foes in the area are interrupted and you steal 0..5 Energy from all foes in the area.
  ~ Energy stolen :: 0-4: 0 0 1 1 1 | 5-9: 2 2 2 3 3 | 10-14: 3 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 7 7
  # causes: Interrupt, Energy Stealing; target: foes; aoe: in the area
Waste Not, Want Not #1995 | Spell | Eye of the North | E5 C¼ R15
  If target foe is not casting a spell or attacking, you gain 8..13 Energy.
  ~ Energy gain :: 0-4: 8 8 9 9 9 | 5-9: 10 10 10 11 11 | 10-14: 11 12 12 12 13 | 15-19: 13 13 14 14 14 | 20-21: 15 15
  # causes: Energy Gain; target: foes

### Mesmer / No Attribute
Arcane Echo #75 | Enchantment Spell | Core | E15 C2 R20
  If you cast a spell in the next 20 seconds, Arcane Echo is replaced with that spell for 20 seconds. Arcane Echo ends prematurely if you use a non-spell skill.
  # causes: Skill Copying
  ! ANOMALY: Arcane Echo's description omits the fact that it cannot copy itself.
Arcane Mimicry #65 | Spell | Core | E15 C2 R60
  For 20 seconds, Arcane Mimicry becomes the non-form elite skill from target other ally.
  # causes: Skill Copying; target: other allies
  ! ANOMALY: No effect if target's elite skill is Junundu Siege.
Echo #74 | Elite Enchantment Spell | Core | E5 C1 R10
  For 30 seconds, Echo is replaced with the next skill you use. Echo acts as this skill for 30 seconds.
  # causes: Skill Copying
  ! ANOMALY: Echo's description omits the fact that it cannot copy a Signet of Capture and itself.
Epidemic #78 | Spell | Core | E5 C¼ R5
  Spread all negative conditions and their remaining durations from target foe to all foes adjacent to your target.
  # causes: Condition; target: foes; aoe: adjacent
Expel Hexes #954 | Elite Spell | Factions | E5 C1 R8
  Remove up to 2 Hexes from target ally.
  # removes: Hex spell; target: allies
Hypochondria #1334 | Spell | Nightfall | E5 C¼ R7
  Transfer all conditions from all foes in the area to target foe.
  # causes: Condition; removes: Condition; target: foes; aoe: in the area
Lyssa's Balance #877 | Spell | Factions | E5 C1 R15
  Target foe loses one Enchantment. If you have more Enchantments than target foe, this skill has no effect.
  # removes: Enchantment; target: foes
Mirror of Disenchantment (PvP) #3194 | Spell | Nightfall | E10 C1 R20
  Remove one enchantment from target foe. All of that foe's party members also lose that same enchantment.
  # removes: Enchantment; target: foes; aoe: party
Shatter Storm #933 | Elite Spell | Factions | E10 C1
  Target foe loses all enchantments. For each enchantment removed this way, Shatter Storm is disabled for an additional 7 seconds.
  # causes: Increased Recharge Time; removes: Enchantment; target: foes
Signet of Disenchantment #882 | Signet | Factions | C1 R15
  Lose all Energy. Target foe loses one enchantment.
  # causes: Energy Loss; removes: Enchantment; target: foes
Signet of Midnight #58 | Elite Touch Signet | Prophecies | C2 R10
  Elite Signet. You and target touched foe become Blinded for 15 seconds.
  # causes: Blind; target: foes; range: touch
Web of Disruption (PvP) #3386 | Hex Spell | Nightfall | E10 C¼ R15
  Interrupt target foe. For 10 seconds, target foe is hexed with Web of Disruption. When this hex ends, that foe is interrupted again.
  # causes: Interrupt
  ! ANOMALY: This skill's standard description does not specify whether it can interrupt only skills or all actions, including attacks. The effect is clarified in the concise description which states that both the initial and ending interrupts only affect skills. [from PvE version page]

## Elementalist

### Elementalist / Air Magic
Air Attunement #225 | Enchantment Spell | Core | E10 C1 R30
  For 36..60 seconds, you are attuned to Air. You gain 1 Energy plus 30% of the base Energy cost of the skill whenever you use Air Magic.
  ~ Duration :: 0-4: 36 38 39 41 42 | 5-9: 44 46 47 49 50 | 10-14: 52 54 55 57 58 | 15-19: 60 62 63 65 66 | 20-21: 68 70
  # causes: Energy Gain; target: self
Arc Lightning #842 | Spell | Factions | E5 R8
  Target foe is struck for 5..40 lightning damage. If you are Overcast, two foes near your target are struck for 15..85 lightning damage. Damage from Arc Lightning has 25% armor penetration.
  ~ Lightning damage :: 0-4: 5 7 10 12 14 | 5-9: 17 19 21 24 26 | 10-14: 28 31 33 35 38 | 15-19: 40 42 45 47 49 | 20-21: 52 54
  ~ Nearby lightning damage :: 0-4: 15 20 24 29 34 | 5-9: 38 43 48 52 57 | 10-14: 62 66 71 76 80 | 15-19: 85 90 94 99 104 | 20-21: 108 113
  # causes: Lightning Damage, Armor Penetration; target: foes; aoe: nearby
  ! BUG: When this skill's functionality changed, the Polish description was updated incorrectly. It mentions too little additional damage while Overcast: Spell. Deals 5..40 lightning damage. Deals 5..40 lightning damage to two nearby foes if you are Overcast. 25% armor penetration.
Blinding Flash #220 | Spell | Core | E10 C¾ R8
  Target foe is Blinded for 3..8 seconds.
  ~ Blind duration :: 0-4: 3 3 4 4 4 | 5-9: 5 5 5 6 6 | 10-14: 6 7 7 7 8 | 15-19: 8 8 9 9 9 | 20-21: 10 10
  # causes: Blind
  ! ANOMALY: This skill can be used on a spirit but it will not inflict blindness.
Blinding Surge #1367 | Elite Spell | Nightfall | E10 C¾ R6
  Target foe is struck for 5..50 lightning damage. That foe and all adjacent foes are Blinded for 3..8 seconds. This spell has 25% armor penetration. If this spell strikes an attacking foe, all adjacent foes are also struck and this spell deals 50% more damage.
  ~ Lightning damage :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  ~ Blind duration :: 0-4: 3 3 4 4 4 | 5-9: 5 5 5 6 6 | 10-14: 6 7 7 7 8 | 15-19: 8 8 9 9 9 | 20-21: 10 10
  # causes: Lightning Damage, Blind, Armor Penetration; target: foes; aoe: adjacent
  ! ANOMALY: Unlike all other Elementalist skills that deal both damage and additional damage (except Sandstorm and Teinai's Wind), this skill's additional damage is not dealt in a separate packet.
Chain Lightning #223 | Spell | Prophecies | E10 O5 C2 R6
  Target foe and up to two other foes near your target are struck for 10..85 lightning damage. This spell has 25% armor penetration.
  ~ Lightning damage :: 0-4: 10 15 20 25 30 | 5-9: 35 40 45 50 55 | 10-14: 60 65 70 75 80 | 15-19: 85 90 95 100 105 | 20-21: 110 115
  # causes: Lightning Damage, Armor Penetration; target: foes; aoe: nearby
Chilling Winds #1368 | Hex Spell | Nightfall | E5 C1 R8
  Target foe and all adjacent foes are struck for 30..60 cold damage. For 10 seconds, the next Water Magic hex targeting a hexed foe lasts 25..100% longer.
  ~ Cold damage :: 0-4: 30 32 34 36 38 | 5-9: 40 42 44 46 48 | 10-14: 50 52 54 56 58 | 15-19: 60 62 64 66 68 | 20-21: 70 72
  ~ % longer :: 0-4: 25 30 35 40 45 | 5-9: 50 55 60 65 70 | 10-14: 75 80 85 90 95 | 15-19: 100 105 110 115 120 | 20-21: 125 130
  # causes: Cold Damage; aoe: adjacent
  ! BUG: Both descriptions fail to mention that the target and all adjacent foes also become hexed with Chilling Winds in addition to being struck with cold damage.
Conjure Lightning #221 | Enchantment Spell | Core | E10 C1 R30
  For 60 seconds, if you're wielding a lightning weapon, your attacks strike for an additional 5..20 lightning damage.
  ~ + Lightning damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Lightning Damage
Enervating Charge #224 | Spell | Core | E10 C1 R8
  Target foe is struck for 25..50 lightning damage and suffers from Weakness for 5..20 seconds. This spell has 25% armor penetration.
  ~ Lightning damage :: 0-4: 25 27 28 30 32 | 5-9: 33 35 37 38 40 | 10-14: 42 43 45 47 48 | 15-19: 50 52 53 55 57 | 20-21: 58 60
  ~ Weakness duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Lightning Damage, Weakness, Armor Penetration
Gale #162 | Spell | Core | E10 O10 C1 R5
  Knock down target foe for 2 seconds. (50% failure chance with Air Magic 4 or less.)
  # causes: Knockdown; target: foes; range: Casting; aoe: none
Glimmering Mark #227 | Elite Hex Spell | Prophecies | E10 C1 R15
  For 10 seconds, target foe and all foes adjacent to your target take 5..25 damage each second. Foes using attack skills are Blinded for 3 seconds. This hex ends if you use a skill that targets this foe.
  ~ Armor-ignoring damage :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  # causes: Blind; aoe: adjacent
  ! BUG: The concise description fails to specify the duration of the Blind condition
  ! ANOMALY: Unlike most area damage over time skills, Glimmering Mark does not cause AI to scatter.
Glyph of Swiftness #2002 | Glyph | Eye of the North | E5 C1 R10
  For 15 seconds, your next 1..5 spell[s] recharge 25% faster and projectiles from the affected spells move 200% faster.
  ~ Spells affected :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Decreased Recharge Time, Increased Projectile Speed
  ! BUG: Projectile speed boost only affects first projectile from Lava Arrows, Stone Daggers and Dancing Daggers when only one charge of Glyph of Swiftness remains.
Gust #843 | Elite Enchantment Spell | Factions | E10 C¾ R15
  For 5..11 seconds, both you and target ally move 33% faster. When you cast this spell, all foes adjacent to you and your target take 15..70 cold damage. Foes struck by Gust while attacking or moving are knocked down.
  ~ Duration :: 0-4: 5 5 6 6 7 | 5-9: 7 7 8 8 9 | 10-14: 9 9 10 10 11 | 15-19: 11 11 12 12 13 | 20-21: 13 13
  ~ Cold damage :: 0-4: 15 19 22 26 30 | 5-9: 33 37 41 44 48 | 10-14: 52 55 59 63 66 | 15-19: 70 74 77 81 85 | 20-21: 88 92
  # causes: Cold Damage, Increased Movement Speed, Knockdown; target: allies or foes; aoe: adjacent
Invoke Lightning #1664 | Elite Spell | Nightfall | E10 O5 C1 R6
  Target foe and up to two other foes near your target are struck for 10..90 lightning damage. This spell has 25% armor penetration.
  ~ Lightning damage :: 0-4: 10 15 21 26 31 | 5-9: 37 42 47 53 58 | 10-14: 63 69 74 79 85 | 15-19: 90 95 101 106 111 | 20-21: 117 122
  # causes: Lightning Damage, Armor Penetration; target: foes; range: Casting; aoe: nearby
  ! ANOMALY: Invoke Lightning's animation shows strikes on all possible targets, not just the three that are actually hit.
Lightning Bolt #1369 | Spell | Nightfall | E5 C1 R8
  Send out a Lightning Bolt that strikes for 5..50 lightning damage if it hits. If Lightning Bolt strikes a moving foe, that foe is struck for 5..50 additional lightning damage. This spell has 25% armor penetration.
  ~ Lightning damage :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  ~ Additional lightning damage :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Lightning Damage, Armor Penetration
  ! BUG: "Master of My Domain" considers each packet a separate skill.
Lightning Hammer (PvP) #3396 | Spell | Factions | E25 C2 R4
  Target foe is struck for 10..100 lightning damage. Lightning Hammer has 25% armor penetration.
  ~ Lightning damage :: 0-4: 10 16 22 28 34 | 5-9: 40 46 52 58 64 | 10-14: 70 76 82 88 94 | 15-19: 100 106 112 118 124 | 20-21: 130 136
  # causes: Lightning Damage, Armor Penetration; target: foes
Lightning Javelin #230 | Spell | Prophecies | E5 C1 R5
  Send out a Lightning Javelin that strikes for 15..50 lightning damage if it hits. Lightning Javelin interrupts attacking foes. This spell has 25% armor penetration and strikes all foes between you and your target.
  ~ Lightning damage :: 0-4: 15 17 20 22 24 | 5-9: 27 29 31 34 36 | 10-14: 38 41 43 45 48 | 15-19: 50 52 55 57 59 | 20-21: 62 64
  # causes: Lightning Damage, Interrupt, Armor Penetration; target: foes; range: Casting; aoe: linear
Lightning Orb #229 | Spell | Core | E10 C2 R5
  Send out a Lightning Orb that strikes target foe for 10..100 lightning damage. This spell has 25% armor penetration.
  ~ Lightning damage :: 0-4: 10 16 22 28 34 | 5-9: 40 46 52 58 64 | 10-14: 70 76 82 88 94 | 15-19: 100 106 112 118 124 | 20-21: 130 136
  # causes: Lightning Damage, Armor Penetration; target: foes; range: Casting; aoe: none
Lightning Strike #222 | Hex Spell | Core | E5 C1 R5
  Strike target foe for 10..60 lightning damage. This spell has 25% armor penetration. If you are Overcast, that foe is hexed with Lightning Strike for 3 seconds. When this hex ends, that foe is struck again for 20..40 lightning damage.
  ~ Initial Lightning damage :: 0-4: 10 13 17 20 23 | 5-9: 27 30 33 37 40 | 10-14: 43 47 50 53 57 | 15-19: 60 63 67 70 73 | 20-21: 77 80
  ~ Final Lightning damage :: 0-4: 20 21 23 24 25 | 5-9: 27 28 29 31 32 | 10-14: 33 35 36 37 39 | 15-19: 40 41 43 44 45 | 20-21: 47 48
  # causes: Lightning Damage, Armor Penetration; target: foes
  ! ANOMALY: Similar to Incendiary Bonds and Lightning Surge, removing the hex before it ends will negate the end effect, unlike Shatterstone and most other skills with an end effect.
  ! ANOMALY: Despite the ambiguity of the concise description, the end effect damage also has 25% armor penetration.
Lightning Surge #205 | Elite Hex Spell | Core | E10 C1 R10
  After 3 seconds, target foe is knocked down and struck for 14..100 lightning damage, and has Cracked Armor for 5..20 seconds. This spell has 25% armor penetration.
  ~ Lightning damage :: 0-4: 14 20 25 31 37 | 5-9: 43 48 54 60 66 | 10-14: 71 77 83 89 94 | 15-19: 100 106 111 117 123 | 20-21: 129 134
  ~ Cracked Armor duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Lightning Damage, Knockdown, Cracked Armor, Armor Penetration; range: Casting
Lightning Touch #232 | Touch skill | Core | E5 C¾ R5
  Skill. Target touched foe and all adjacent foes are struck for 10..60 lightning damage, are Blinded for 1..4 second[s], and have Cracked Armor for 1..10 second[s]. This skill has 25% armor penetration.
  ~ Lightning damage :: 0-4: 10 13 17 20 23 | 5-9: 27 30 33 37 40 | 10-14: 43 47 50 53 57 | 15-19: 60 63 67 70 73 | 20-21: 77 80
  ~ Blind duration :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  ~ Cracked Armor duration :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # causes: Lightning Damage, Blind, Cracked Armor, Armor Penetration; target: foes; range: touch; aoe: adjacent
Mind Shock (PvP) #2804 | Elite Spell | Prophecies | E5 O10 C1 R8
  Target foe suffers 10..50 lightning damage. If you have more Energy than target foe, that foe suffers 10..50 more lightning damage and is knocked down. This spell has 25% armor penetration.
  ~ Lightning damage :: 0-4: 10 13 15 18 21 | 5-9: 23 26 29 31 34 | 10-14: 37 39 42 45 47 | 15-19: 50 53 55 58 61 | 20-21: 63 66
  ~ + Lightning damage :: 0-4: 10 13 15 18 21 | 5-9: 23 26 29 31 34 | 10-14: 37 39 42 45 47 | 15-19: 50 53 55 58 61 | 20-21: 63 66
  # causes: Lightning Damage, Knockdown, Armor Penetration; target: foes; range: Casting; aoe: none
Ride the Lightning (PvP) #2807 | Elite Spell | Factions | E5 O5 C1 R10
  You Ride the Lightning to target. All adjacent foes are Blinded for 1..5 second[s]. If your target is a foe, it is struck for 10..70 lightning damage. This spell has 25% armor penetration.
  ~ Lightning damage :: 0-4: 10 14 18 22 26 | 5-9: 30 34 38 42 46 | 10-14: 50 54 58 62 66 | 15-19: 70 74 78 82 86 | 20-21: 90 94
  ~ Blind duration :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Lightning Damage, Armor Penetration, Blind, Shadow Step; target: allies or foes; aoe: adjacent
Shell Shock #2059 | Spell | Eye of the North | E5 C1 R8
  Target foe is struck for 10..30 lightning damage and has Cracked Armor for 5..20 seconds. This spell has 25% armor penetration. If you are Overcast, this spell strikes adjacent foes.
  ~ Lightning damage :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  ~ Cracked Armor duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Lightning Damage, Cracked Armor, Armor Penetration; target: foes; range: Casting; aoe: adjacent
Shock #231 | Touch skill | Prophecies | E5 O10 C¾ R10
  Skill. Target touched foe is knocked down and struck for 10..60 lightning damage. This skill has 25% armor penetration.
  ~ Lightning damage :: 0-4: 10 13 17 20 23 | 5-9: 27 30 33 37 40 | 10-14: 43 47 50 53 57 | 15-19: 60 63 67 70 73 | 20-21: 77 80
  # causes: Lightning Damage, Knockdown, Armor Penetration; target: foes; range: touch; aoe: none
Shock Arrow #1082 | Spell | Factions | E5 C1 R8
  Send out a shocking arrow that flies swiftly toward target foe, striking for 5..50 lightning damage. If Shock Arrow strikes a foe suffering from Cracked Armor, you gain 5 Energy plus 1 Energy for every 2 ranks of Energy Storage. Shock Arrow has 25% armor penetration.
  ~ Lightning damage :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  ~ Energy gain :: 0-4: 5 5 6 6 7 | 5-9: 7 8 8 9 9 | 10-14: 10 10 11 11 12 | 15-19: 12 13 13 14 14 | 20-21: 15 15
  # causes: Lightning Damage, Energy Gain, Armor Penetration; target: foes; range: Casting
Storm Djinn's Haste #1370 | Enchantment Spell | Nightfall | E5 C¼ R10
  For 10..25 seconds, you move 25% faster. Each second that you are moving, you lose 1 Energy.
  ~ Duration :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  # causes: Increased Movement Speed, Energy Loss
Teinai's Wind #1081 | Spell | Factions | E10 C1 R8
  Target foe and all adjacent foes take 10..40 cold damage. Burning foes struck by Teinai's Wind take an additional 40..80 damage and are interrupted.
  ~ Cold damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  ~ + Cold damage :: 0-4: 40 43 45 48 51 | 5-9: 53 56 59 61 64 | 10-14: 67 69 72 75 77 | 15-19: 80 83 85 88 91 | 20-21: 93 96
  ~ Total damage :: 0-4: 50 55 59 64 69 | 5-9: 73 78 83 87 92 | 10-14: 97 101 106 111 115 | 15-19: 120 125 129 134 139 | 20-21: 143 148
  # causes: Cold Damage, Interrupt; target: foes; aoe: adjacent
  ! ANOMALY: Unlike all other Elementalist skills that deal both damage and additional damage (except Blinding Surge and Sandstorm), this skill's additional damage is not dealt in a separate packet.
Thunderclap #228 | Elite Spell | Prophecies | E10 C1 R8
  Create a massive shockwave at target foe's location. Deals 10..50 lightning damage to target and all nearby foes. Struck foes are interrupted and suffer from Cracked Armor and Weakness for 5..20 seconds. This spell has 25% armor penetration.
  ~ Lightning damage :: 0-4: 10 13 15 18 21 | 5-9: 23 26 29 31 34 | 10-14: 37 39 42 45 47 | 15-19: 50 53 55 58 61 | 20-21: 63 66
  ~ Cracked Armor and Weakness durations :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Lightning Damage, Cracked Armor, Weakness, Interrupt, Armor Penetration; target: foes; range: Casting; aoe: nearby
Whirlwind #163 | Spell | Prophecies | E5 C¾ R8
  All adjacent foes take 15..75 cold damage. Attacking foes struck by Whirlwind are knocked down. If you are Overcast, this spell strikes nearby instead of adjacent.
  ~ Cold damage :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  # causes: Cold Damage, Knockdown; target: untargeted; aoe: adjacent, nearby
Windborne Speed #160 | Enchantment Spell | Prophecies | E10 C¾ R5
  For 5..13 seconds, target ally moves 33% faster.
  ~ Duration :: 0-4: 5 6 6 7 7 | 5-9: 8 8 9 9 10 | 10-14: 10 11 11 12 12 | 15-19: 13 14 14 15 15 | 20-21: 16 16
  # causes: Increased Movement Speed; target: allies

### Elementalist / Earth Magic
Aftershock #174 | Spell | Core | E10 C¾ R10
  Nearby foes are struck for 15..85 earth damage. Knocked down foes are struck for 15..85 additional earth damage.
  ~ Earth damage :: 0-4: 15 20 24 29 34 | 5-9: 38 43 48 52 57 | 10-14: 62 66 71 76 80 | 15-19: 85 90 94 99 104 | 20-21: 108 113
  ~ + Earth damage :: 0-4: 15 20 24 29 34 | 5-9: 38 43 48 52 57 | 10-14: 62 66 71 76 80 | 15-19: 85 90 94 99 104 | 20-21: 108 113
  # causes: Earth Damage; target: untargeted; aoe: nearby
Armor of Earth #165 | Enchantment Spell | Core | E10 C¾ R15
  For 30 seconds, you gain 24..60 armor, but move 50..14% slower.
  ~ + Armor rating :: 0-4: 24 26 29 31 34 | 5-9: 36 38 41 43 46 | 10-14: 48 50 53 55 58 | 15-19: 60 62 65 67 70 | 20-21: 72 74
  ~ % slower :: 0-4: 50 48 45 43 40 | 5-9: 38 36 33 31 28 | 10-14: 26 24 21 19 16 | 15-19: 14 12 9 7 4 | 20-21: 2 0
  # causes: Increased Armor Rating, Decreased Movement Speed
Ash Blast #1085 | Hex spell | Factions | E5 C1 R10
  Target and adjacent foes are struck for 35..65 earth damage. Burning foes struck by Ash Blast are hexed for 5 seconds and have a 20..75% chance to miss with attacks.
  ~ Earth damage :: 0-4: 35 37 39 41 43 | 5-9: 45 47 49 51 53 | 10-14: 55 57 59 61 63 | 15-19: 65 67 69 71 73 | 20-21: 75 77
  ~ Miss chance % :: 0-4: 20 24 27 31 35 | 5-9: 38 42 46 49 53 | 10-14: 57 60 64 68 71 | 15-19: 75 79 82 86 90 | 20-21: 93 97
  # causes: Earth Damage, Miss; aoe: adjacent
Churning Earth #844 | Spell | Factions | E15 C2 R30
  Create Churning Earth at target foe's location. For the next 5 seconds, Churning Earth strikes foes near that location for 10..40 earth damage each second. Any foe moving faster than normal when struck by Churning Earth is knocked down.
  ~ Earth damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Earth Damage, Knockdown; target: foes; aoe: nearby
Crystal Wave #217 | Spell | Prophecies | E15 C¾ R15
  Foes adjacent to you are struck for 10..70 damage but are cured of any negative conditions. Each condition removed deals 5..15 damage.
  ~ Armor-ignoring damage :: 0-4: 10 14 18 22 26 | 5-9: 30 34 38 42 46 | 10-14: 50 54 58 62 66 | 15-19: 70 74 78 82 86 | 20-21: 90 94
  ~ Damage per condition :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Armor-ignoring Damage; removes: Condition; target: untargeted; aoe: adjacent
Dragon's Stomp #1086 | Spell | Factions | E25 O10 C3 R15
  You invoke a Dragon's Stomp at target foe's location. All foes near this location are knocked down and are struck for 26..100 earth damage.
  ~ Earth damage :: 0-4: 26 31 36 41 46 | 5-9: 51 56 61 65 70 | 10-14: 75 80 85 90 95 | 15-19: 100 105 110 115 120 | 20-21: 125 130
  # causes: Earth Damage, Knockdown; target: foes; range: Casting; aoe: nearby; special: duplicate
Earth Attunement #169 | Enchantment Spell | Core | E10 C1 R30
  For 36..60 seconds, you are attuned to Earth. You gain 1 Energy plus 30% of the base Energy cost of the skill each time you use Earth Magic.
  ~ Duration :: 0-4: 36 38 39 41 42 | 5-9: 44 46 47 49 50 | 10-14: 52 54 55 57 58 | 15-19: 60 62 63 65 66 | 20-21: 68 70
  # causes: Energy Gain
Earthen Shackles #2000 | Hex Spell | Eye of the North | E10 C1 R15
  For 3 seconds, target and all nearby foes move 90% slower. When Earthen Shackles ends, it applies Weakness for 5..20 seconds.
  ~ Weakness duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Decreased Movement Speed, Weakness; aoe: nearby
Earthquake #170 | Spell | Prophecies | E25 O10 C3 R15
  You invoke an Earthquake at target foe's location. All foes near this location are knocked down and are struck for 26..100 earth damage.
  ~ Earth damage :: 0-4: 26 31 36 41 46 | 5-9: 51 56 61 65 70 | 10-14: 75 80 85 90 95 | 15-19: 100 105 110 115 120 | 20-21: 125 130
  # causes: Earth Damage, Knockdown; target: foes; range: Casting; aoe: nearby; special: duplicate
Ebon Hawk #1374 | Spell | Nightfall | E10 C1 R5
  Send a projectile that strikes target foe for 10..85 earth damage and causes Weakness for 5..15 seconds if it hits.
  ~ Earth damage :: 0-4: 10 15 20 25 30 | 5-9: 35 40 45 50 55 | 10-14: 60 65 70 75 80 | 15-19: 85 90 95 100 105 | 20-21: 110 115
  ~ Weakness Duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Earth Damage, Weakness; target: foes
Eruption #167 | Spell | Prophecies | E25 C2 R30
  Cause an Eruption at target foe's location. Each second for 5 seconds, foes near this location are struck for 10..40 earth damage and are Blinded for 10 seconds.
  ~ Earth damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Earth Damage, Blind; target: foes
Glowstone #1661 | Spell | Nightfall | E5 C¾ R7
  Send a projectile that strikes for 5..50 earth damage if it hits. If this spell hits a weakened foe, you gain 5 Energy plus 1 Energy for every 2 ranks of Energy Storage.
  ~ Earth damage :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  ~ Energy gain :: 0-4: 5 5 6 6 7 | 5-9: 7 8 8 9 9 | 10-14: 10 10 11 11 12 | 15-19: 12 13 13 14 14 | 20-21: 15 15
  # causes: Earth Damage, Energy Gain; target: foes
Grasping Earth #173 | Hex Spell | Prophecies | E10 C¾ R12
  For 5..20 seconds, all nearby foes move 50% slower.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Decreased Movement Speed; target: untargeted; aoe: nearby
Iron Mist #216 | Enchantment Spell | Prophecies | E10 C1 R20
  For 8..15 seconds, you have +15 armor. Your Air Magic spells that target a foe activate and recharge 33% faster, but you are Overcast by 2 points.
  ~ Duration :: 0-4: 8 8 9 9 10 | 5-9: 10 11 11 12 12 | 10-14: 13 13 14 14 15 | 15-19: 15 15 16 16 17 | 20-21: 17 18
  # causes: Increased Armor Rating, Decreased Activation Time, Decreased Recharge Time, Overcast; target: untargeted
  ! BUG: The effects of this skill apply to all spells, regardless of target or attribute.
Kinetic Armor #166 | Enchantment Spell | Prophecies | E15 C3 R30
  For 12 seconds, you gain +20..80 armor. Whenever you cast a spell, Kinetic Armor is renewed for 12 seconds.
  ~ + Armor rating :: 0-4: 20 24 28 32 36 | 5-9: 40 44 48 52 56 | 10-14: 60 64 68 72 76 | 15-19: 80 84 88 92 96 | 20-21: 100 104
  # causes: Increased Armor Rating, Renewal; target: self
Magnetic Aura #168 | Enchantment Spell | Prophecies | E10 C1 R12
  For 1..8 second[s], you block the next attack against you and deal 10..50 damage to your attacker. If you are Overcast, all party members in earshot are also enchanted.
  ~ Duration :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  ~ Damage :: 0-4: 10 13 15 18 21 | 5-9: 23 26 29 31 34 | 10-14: 37 39 42 45 47 | 15-19: 50 53 55 58 61 | 20-21: 63 66
  # causes: Block; target: untargeted; aoe: earshot
Magnetic Surge #2190 | Enchantment Spell | Eye of the North | E10 C1 R15
  Target foe takes 15..75 damage. If you are Overcast, Magnetic Surge enchants all allies in earshot for 1..5 second[s] to block the next attack against them.
  ~ Damage :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  ~ Duration :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Block; target: foe; aoe: earshot
  ! ANOMALY: Similar to other enchantments that target a foe, foes affected by Well of the Profane or spirits cannot be targeted by this enchantment.
  ! BUG: When Overcast, Magnetic Surge is applied to party members only.
Obsidian Flame (PvP) #2809 | Spell | Core | E5 O5 R5
  Deal 22..92 damage to target foe. This spell ignores armor.
  ~ Damage :: 0-4: 22 27 31 36 41 | 5-9: 45 50 55 59 64 | 10-14: 69 73 78 83 87 | 15-19: 92 97 101 106 111 | 20-21: 115 120
  # target: foes
Obsidian Flesh #218 | Elite Enchantment Spell | Core | E25 C1 R30
  For 8..20 seconds, you gain +20 armor and cannot be the target of enemy spells, but cannot attack and have -2 energy degeneration.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  # causes: Increased Armor Rating, Energy Degeneration
  ! BUG: The armor bonus from this skill only applies to physical damage.
Sandstorm #1372 | Elite Spell | Nightfall | E15 C2 R20
  Create a Sandstorm at target foe's location. For 10 seconds, nearby foes are struck for 20..40 earth damage each second and attacking foes are struck for an additional 10..30 earth damage each second.
  ~ Earth damage :: 0-4: 20 21 23 24 25 | 5-9: 27 28 29 31 32 | 10-14: 33 35 36 37 39 | 15-19: 40 41 43 44 45 | 20-21: 47 48
  ~ Conditional damage :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  # causes: Earth Damage; target: foes; range: casting; aoe: nearby
  ! ANOMALY: Unlike all other Elementalist skills that deal both damage and additional damage (except Blinding Surge and Teinai's Wind), this skill's additional damage is not dealt in a separate packet.
Shockwave #937 | Elite Spell | Factions | E10 C1 R15
  All foes in the area take 15..60 earth damage and are Weakened for 1..10 second[s]. Nearby foes also take +15..60 earth damage and have Cracked Armor for 1..10 second[s]. Adjacent foes suffer the previous effects, take +15..60 earth damage, and are Blinded for 1..10 second[s].
  ~ Each earth damage packet :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  ~ Weakness, Cracked Armor, and Blind duration :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Adjacent :: 0-4: 45 54 63 72 81 | 5-9: 90 99 108 117 126 | 10-14: 135 144 153 162 171 | 15-19: 180 189 198 207 216 | 20-21: 225 234
  ~ Nearby :: 0-4: 30 36 42 48 54 | 5-9: 60 66 72 78 84 | 10-14: 90 96 102 108 114 | 15-19: 120 126 132 138 144 | 20-21: 150 156
  ~ In the area :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  # causes: Earth Damage, Weakness, Cracked Armor, Blind; target: untargeted; aoe: in the area
  ! ANOMALY: The skill description implies that Blind covers Cracked Armor which covers Weakness, while in actuality Blind covers Weakness which covers Cracked Armor.
Sliver Armor #1084 | Enchantment Spell | Factions | E10 C1 R30
  For 5..11 seconds, you have 25..50% chance to block attacks and whenever you are the target of a hostile spell or attack one nearby foe is struck for 5..35 earth damage.
  ~ Duration :: 0-4: 5 5 6 6 7 | 5-9: 7 7 8 8 9 | 10-14: 9 9 10 10 11 | 15-19: 11 11 12 12 13 | 20-21: 13 13
  ~ Block chance % :: 0-4: 25 27 28 30 32 | 5-9: 33 35 37 38 40 | 10-14: 42 43 45 47 48 | 15-19: 50 52 53 55 57 | 20-21: 58 60
  ~ Earth damage :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  # causes: Block, Earth Damage; target: untargeted; aoe: nearby
Stone Daggers #172 | Spell | Core | E5 C1
  Send out two Stone Daggers. Each Stone Dagger strikes target foe for 8..33 earth damage if it hits. If you are Overcast, each projectile inflicts Bleeding for 1..5 second[s].
  ~ Earth damage :: 0-4: 8 10 11 13 15 | 5-9: 16 18 20 21 23 | 10-14: 25 26 28 30 31 | 15-19: 33 35 36 38 40 | 20-21: 41 43
  ~ Bleeding duration :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Bleeding, Earth Damage; target: foes
Stone Sheath #1373 | Elite Enchantment Spell | Nightfall | E10 C1 R15
  For 5..20 seconds, you and target ally have +1..30 armor and are immune to critical hits. When you cast this spell, all foes near you and your target take 15..70 earth damage and are Weakened for 5..20 seconds.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ + Armor rating :: 0-4: 1 3 5 7 9 | 5-9: 11 13 15 16 18 | 10-14: 20 22 24 26 28 | 15-19: 30 32 34 36 38 | 20-21: 40 42
  ~ Earth damage :: 0-4: 15 19 22 26 30 | 5-9: 33 37 41 44 48 | 10-14: 52 55 59 63 66 | 15-19: 70 74 77 81 85 | 20-21: 88 92
  ~ Weakness duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Increased Armor Rating, Earth Damage, Weakness; target: allies or foes; range: Casting; aoe: nearby
Stone Striker #1371 | Enchantment Spell | Nightfall | E5 C¼ R20
  For 5..30 seconds, whenever you take or deal elemental or physical damage, that damage is converted to earth damage.
  ~ Duration :: 0-4: 5 7 8 10 12 | 5-9: 13 15 17 18 20 | 10-14: 22 23 25 27 28 | 15-19: 30 32 33 35 37 | 20-21: 38 40
  # causes: Earth Damage
  ! ANOMALY: This also converts chaos, dark, holy and spirit attacks damage types into earth damage.
  ! BUG: This skill does not convert damage but instead forces the damage type of all dealt damage to be earth damage. For example when applying Winter on top of stone striker, physical damage is not converted into earth damage, since winter has no effect on it - it still considers the damage to be of physical type. This is irrespective of which damage converting skill is used first.
Stoneflesh Aura #1375 | Enchantment Spell | Nightfall | E10 C2 R15
  For 5..15 seconds, damage you receive is reduced by 1..31, and you are immune to critical attacks.
  ~ Duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  ~ Damage reduction :: 0-4: 1 3 5 7 9 | 5-9: 11 13 15 17 19 | 10-14: 21 23 25 27 29 | 15-19: 31 33 35 37 39 | 20-21: 41 43
  # causes: Damage Reduction
  ! BUG: This enchantment does not actually make you immune to critical hits, but prevents extra damage from them. As such, effects that may result from them, such as knock down, or the re-applying effect of Critical Agility and Critical Defenses will still apply. However, the damage-nullified critical hit will not trigger the energy gain of Critical Strikes.
Stoning #171 | Spell | Core | E15 C1 R5
  Send out a large stone, striking target foe for 45..105 earth damage if it hits. If Stoning hits a foe suffering from Weakness, that foe is knocked down.
  ~ Earth damage :: 0-4: 45 49 53 57 61 | 5-9: 65 69 73 77 81 | 10-14: 85 89 93 97 101 | 15-19: 105 109 113 117 121 | 20-21: 125 129
  # causes: Earth Damage, Knockdown; target: foes
Teinai's Crystals #1099 | Spell | Factions | E5 C1 R8
  Target foe takes 20..40 damage. If target foe has a Water Magic hex, this spell strikes target and nearby foes for an additional 20..40 damage, and nearby foes also suffer Cracked Armor for 5..15 seconds.
  ~ Armor-ignoring damage :: 0-4: 20 21 23 24 25 | 5-9: 27 28 29 31 32 | 10-14: 33 35 36 37 39 | 15-19: 40 41 43 44 45 | 20-21: 47 48
  ~ Additional damage :: 0-4: 20 21 23 24 25 | 5-9: 27 28 29 31 32 | 10-14: 33 35 36 37 39 | 15-19: 40 41 43 44 45 | 20-21: 47 48
  ~ Cracked Armor duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Cracked Armor; target: foes; range: Casting; aoe: nearby
Unsteady Ground #1083 | Elite Spell | Factions | E10 C2 R15
  You create Unsteady Ground at target foe's location. For 5 seconds, nearby foes take 10..40 earth damage each second. Attacking foes struck by Unsteady Ground are knocked down.
  ~ Earth damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Earth Damage, Knockdown; target: foes; range: Casting; aoe: nearby
Ward Against Elements #175 | Ward Spell | Prophecies | E10 C1 R20
  You create a Ward Against Elements at your current location. For 8..20 seconds, non-spirit allies in this area gain +24 armor against elemental damage.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  # causes: Increased Armor Rating
Ward Against Foes #177 | Ward Spell | Core | E15 C1 R20
  You create a Ward Against Foes at your current location. For 8..20 seconds, non-spirit foes in this area move 50% slower.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  # causes: Decreased Movement Speed
Ward Against Melee #176 | Ward Spell | Core | E15 C1 R30
  You create a Ward Against Melee at your current location. For 5..20 seconds, non-spirit allies in this area have a 50% chance to block melee attacks.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Block
Ward of Stability #938 | Ward Spell | Factions | E10 C1 R30
  Create a Ward of Stability at your current location. For 10..25 seconds, non-spirit allies cannot be knocked down.
  ~ Duration :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  # causes: Knockdown Immunity
  ! BUG: Similar to Ward of Weakness, this ward spell's recharge time cannot be decreased. For example, activating this ward spell while under the effects of Glyph of Renewal or Glyph of Swiftness will consume the glyph, but the recharge time will not be decreased. However, the recharge time can be increased, e.g., by Glyph of Sacrifice.
Ward of Weakness #2001 | Ward Spell | Eye of the North | E5 C1 R20
  You create a Ward of Weakness at your current location. For 5..20 seconds, foes in this area become Weakened for 5..20 seconds whenever they take elemental damage.
  ~ Ward duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Weakness duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Weakness
  ! BUG: Similar to Ward of Stability, this ward spell's recharge time cannot be decreased. E.g. activating this ward spell while under the effects of Glyph of Renewal or Glyph of Swiftness will consume the glyph, but the recharge time will not be decreased. However, the recharge time can be increased, e.g. by Glyph of Sacrifice.
  ! ANOMALY: The weakness duration is independent of duration modifiers such as the Heavy weapon upgrade.

### Elementalist / Energy Storage
Aura of Restoration (PvP) #3375 | Enchantment Spell | Core | E5 C¼ R20
  For 60 seconds, you gain 0..1 Energy and are healed for 200..400% of the Energy cost each time you cast a spell.
  ~ % of Energy cost :: 0-4: 200 213 227 240 253 | 5-9: 267 280 293 307 320 | 10-14: 333 347 360 373 387 | 15-19: 400 413 427 440 453 | 20-21: 467 480
  ~ Energy gain :: 0-4: 0 0 0 0 0 | 5-9: 0 0 0 1 1 | 10-14: 1 1 1 1 1 | 15-19: 1 1 1 1 1 | 20-21: 1 1
  ~ 1 Energy spell heal :: 0-4: 2 2 2 2 3 | 5-9: 3 3 3 3 3 | 10-14: 3 3 4 4 4 | 15-19: 4 4 4 4 5 | 20-21: 5 5
  ~ 5 Energy spell heal :: 0-4: 10 11 11 12 13 | 5-9: 13 14 15 15 16 | 10-14: 17 17 18 19 19 | 15-19: 20 21 21 22 23 | 20-21: 23 24
  ~ 10 Energy spell heal :: 0-4: 20 21 23 24 25 | 5-9: 27 28 29 31 32 | 10-14: 33 35 36 37 39 | 15-19: 40 41 43 44 45 | 20-21: 47 48
  ~ 15 Energy spell heal :: 0-4: 30 32 34 36 38 | 5-9: 40 42 44 46 48 | 10-14: 50 52 54 56 58 | 15-19: 60 62 64 66 68 | 20-21: 70 72
  ~ 25 Energy spell heal :: 0-4: 50 53 57 60 63 | 5-9: 67 70 73 77 80 | 10-14: 83 87 90 93 97 | 15-19: 100 103 107 110 113 | 20-21: 117 120
  # causes: Energy Gain, Healing
Elemental Attunement #164 | Elite Enchantment Spell | Core | E10 C1 R20
  For 25..60 seconds, you are attuned to Air, Fire, Water, and Earth and gain +1..2 to these attributes. You gain 1 Energy plus 50% of the base Energy cost of the skill each time you use magic associated with any of these elements.
  ~ Duration :: 0-4: 25 27 30 32 34 | 5-9: 37 39 41 44 46 | 10-14: 48 51 53 55 58 | 15-19: 60 62 65 67 69 | 20-21: 72 74
  ~ Attribute increase :: 0-4: 1 1 1 1 1 | 5-9: 1 1 1 2 2 | 10-14: 2 2 2 2 2 | 15-19: 2 2 2 2 2 | 20-21: 2 2
  # causes: Increased Attribute, Energy Gain
Energy Blast #2193 | Spell | Eye of the North | E5 R20
  Target foe takes 1..2 damage for each point of Energy you have (maximum 130 damage).
  ~ Armor-ignoring damage per energy :: 0-4: 1 1 1 1 1 | 5-9: 1 1 1 2 2 | 10-14: 2 2 2 2 2 | 15-19: 2 2 2 2 2 | 20-21: 2 2
Energy Boon #837 | Elite Enchantment Spell | Factions | E10 C1 R12
  For 36..60 seconds, Energy Boon raises the maximum Health of you and target ally by 1..3 for each point of your respective maximum Energy. When this enchantment is first applied, you and your target gain 1..12 Energy. You gain an additional 1 Energy for every 2 points you have in Energy Storage.
  ~ Duration :: 0-4: 36 38 39 41 42 | 5-9: 44 46 47 49 50 | 10-14: 52 54 55 57 58 | 15-19: 60 62 63 65 66 | 20-21: 68 70
  ~ + Max health :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  ~ Energy gain :: 0-4: 1 2 2 3 4 | 5-9: 5 5 6 7 8 | 10-14: 8 9 10 11 11 | 15-19: 12 13 13 14 15 | 20-21: 16 16
  # causes: Increased Maximum Health, Energy Gain; target: allies or foes; range: Casting; aoe: none
  ! ANOMALY: Changing your maximum energy lower than what it was when this was cast on you, will lower your health bonus accordingly to your new energy, however swapping back to higher energy will not bring it back up and it will remain at the lower amount, even if recast on you at higher energy before its duration ends.
Ether Prism #1377 | Elite Skill | Nightfall | E5 R20
  For 3 seconds, all damage you take is reduced by 75%. When Ether Prism ends, you gain 5..20 Energy.
  ~ Energy gain :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Damage Reduction, Energy Gain
Ether Prodigy #178 | Elite Enchantment Spell | Prophecies | E5 O10 C1 R5
  Lose all enchantments. For 8..20 seconds, you gain +6 Energy regeneration. When Ether Prodigy ends, you lose 2 Health for each point of Energy you have.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  ~ Energy gained :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  ~ Energy gain/second1 :: 0-4: 0 0 0 0 0 | 5-9: 1 1 1 1 1 | 10-14: 1 1 1 1 1 | 15-19: 1 1 1 1 1 | 20-21: 2 2
  # causes: Energy Regeneration, Health Loss; removes: Enchantment
Ether Renewal (PvP) #2860 | Elite Enchantment Spell | Prophecies | E10 C1 R30
  For 10 seconds, each time you cast a spell, you gain 1..3 Energy and 5..20 Health for each enchantment on you.
  ~ Energy gain :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  ~ Healing :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Energy Gain, Healing; target: self
  ! BUG: Contrary to the descriptions, this skill causes healing and not health gain.
  ! BUG: Contrary to the descriptions, this skill causes healing and not health gain. [from PvE version page]
Glyph of Energy #199 | Elite Glyph | Prophecies | E5 C1 R25
  Your next 1..3 spell[s] do[es] not cause Overcast and cost[s] 10..25 less Energy to cast. Your elemental attributes are increased by 1..2.
  ~ Spells affected :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  ~ Energy reduction :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  ~ Attribute increase :: 0-4: 1 1 1 1 1 | 5-9: 1 1 1 2 2 | 10-14: 2 2 2 2 2 | 15-19: 2 2 2 2 2 | 20-21: 2 2
  # causes: Decreased Energy Cost, Increased Attribute, Overcast Removal; target: self
Glyph of Lesser Energy #200 | Glyph | Core | E5 C1 R30
  For the next 15 seconds, your next 2 spells cost 10..18 less Energy to cast.
  ~ Energy reduction :: 0-4: 10 11 11 12 12 | 5-9: 13 13 14 14 15 | 10-14: 15 16 16 17 17 | 15-19: 18 19 19 20 20 | 20-21: 21 21
  # causes: Decreased Energy Cost; target: self
Glyph of Restoration #1376 | Glyph | Nightfall | E5 C1 R8
  For 15 seconds, your next 2 spells heal you for 30..105 Health, and you are healed for 150..400% of the Energy cost of each spell.
  ~ Healing :: 0-4: 30 35 40 45 50 | 5-9: 55 60 65 70 75 | 10-14: 80 85 90 95 100 | 15-19: 105 110 115 120 125 | 20-21: 130 135
  ~ % of energy cost healed :: 0-4: 150 167 183 200 217 | 5-9: 233 250 267 283 300 | 10-14: 317 333 350 367 383 | 15-19: 400 417 433 450 467 | 20-21: 483 500
  ~ 1 Energy spell heal :: 0-4: 32 37 42 47 52 | 5-9: 57 63 68 73 78 | 10-14: 83 88 94 99 104 | 15-19: 109 114 119 125 130 | 20-21: 135 140
  ~ 5 Energy spell heal :: 0-4: 38 44 50 55 61 | 5-9: 67 73 79 84 90 | 10-14: 96 102 108 113 119 | 15-19: 125 131 137 142 148 | 20-21: 154 160
  ~ 10 Energy spell heal :: 0-4: 45 52 58 65 72 | 5-9: 78 85 92 98 105 | 10-14: 112 118 125 132 138 | 15-19: 145 152 158 165 172 | 20-21: 178 185
  ~ 15 Energy spell heal :: 0-4: 53 60 68 75 83 | 5-9: 90 98 105 113 120 | 10-14: 128 135 143 150 158 | 15-19: 165 172 180 187 195 | 20-21: 202 210
  ~ 25 Energy spell heal :: 0-4: 68 77 86 95 105 | 5-9: 114 123 132 141 150 | 10-14: 159 168 178 187 196 | 15-19: 205 214 223 232 242 | 20-21: 251 260
  # causes: Healing
Master of Magic #1378 | Elite Enchantment Spell | Nightfall | E5 C1 R10
  For 1..61 second[s], all of your elemental attributes are set to 8..14 and your elemental spells return 1 Energy plus 30% of their Energy cost.
  ~ Duration :: 0-4: 1 5 9 13 17 | 5-9: 21 25 29 33 37 | 10-14: 41 45 49 53 57 | 15-19: 61 65 69 73 77 | 20-21: 81 85
  ~ Attribute rank :: 0-4: 8 8 9 9 10 | 5-9: 10 10 11 11 12 | 10-14: 12 12 13 13 14 | 15-19: 14 14 15 15 16 | 20-21: 16 16
  # causes: Increased Attribute, Energy Gain; target: untargeted
  ! BUG: While under the effects of Master of Magic, being weakened with attribute points in elemental ranks will cause elemental ranks to lower by 1. Elemental attributes without attribute points in will not lower by 1.

### Elementalist / Fire Magic
Bed of Coals #825 | Spell | Factions | E10 C1 R15
  Create a Bed of Coals at target foe's location. For 5 seconds, foes adjacent to target foe are struck for 5..29 fire damage each second. Any foe knocked down on the Bed of Coals is set on fire for 3..7 seconds.
  ~ Fire damage :: 0-4: 5 7 8 10 11 | 5-9: 13 15 16 18 19 | 10-14: 21 23 24 26 27 | 15-19: 29 31 32 34 35 | 20-21: 37 39
  ~ Burning duration :: 0-4: 3 3 4 4 4 | 5-9: 4 5 5 5 5 | 10-14: 6 6 6 6 7 | 15-19: 7 7 8 8 8 | 20-21: 8 9
  # causes: Burning, Fire Damage; target: foes; aoe: adjacent
Breath of Fire #1094 | Spell | Factions | E5 O10 C2 R10
  Create Breath of Fire at target foe's current location. For 5 seconds, foes adjacent to that location are struck for 10..40 fire damage each second.
  ~ Fire damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Fire Damage; target: foes; aoe: adjacent
Burning Speed #823 | Enchantment Spell | Factions | E10 C¼
  For 7 seconds, you are set on fire and move 30..45% faster. When Burning Speed ends, all adjacent foes are set on fire for 3..9 seconds.
  ~ Speed boost % :: 0-4: 30 31 32 33 34 | 5-9: 35 36 37 38 39 | 10-14: 40 41 42 43 44 | 15-19: 45 46 47 48 49 | 20-21: 50 51
  ~ Burning duration :: 0-4: 3 3 4 4 5 | 5-9: 5 5 6 6 7 | 10-14: 7 7 8 8 9 | 15-19: 9 9 10 10 11 | 20-21: 11 11
  # causes: Burning, Increased Movement Speed; target: untargeted; aoe: adjacent
Conjure Flame #182 | Enchantment Spell | Core | E10 C1 R30
  For 60 seconds, if you're wielding a fire weapon, your attacks strike for an additional 5..20 fire damage.
  ~ + Fire damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Fire Damage
Double Dragon #1091 | Elite Enchantment Spell | Factions | E10 C1 R15
  Invoke the power of the Dragon. For 8 seconds, you and target ally are enchanted with Double Dragon. Adjacent foes are dealt 10..40 fire damage each second. Additionally, when you or your ally use skills that target a foe, that foe is set on fire for 1..4 second[s].
  ~ Fire damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  ~ Burning duration :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  # causes: Burning, Fire Damage; target: allies; aoe: adjacent
  ! ANOMALY: If a foe with a spell targeting prevention skill is targeted, Double Dragon will fail, despite the enchantment applying to the ally nearest to the target foe.
  ! ANOMALY: Whenever a target under the effects of Double Dragon is interrupted, the animation restarts.
  ! ANOMALY: Unlike most area damage over time skills, Double Dragon does not cause AI to scatter.
Elemental Flame (PvP) #3397 | Enchantment Spell | Nightfall | E10 C1 R30
  For 5..20 seconds, whenever you apply an Elemental hex to a foe, that foe is set on fire for 1..2 second[s].
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Burning duration :: 0-4: 1 1 1 1 1 | 5-9: 1 1 1 2 2 | 10-14: 2 2 2 2 2 | 15-19: 2 2 2 2 2 | 20-21: 2 2
  # causes: Burning; target: untargeted
Fire Attunement #184 | Enchantment Spell | Core | E10 C1 R30
  For 36..60 seconds, you are attuned to Fire. You gain 1 Energy plus 30% of the base Energy cost of the skill each time you use Fire Magic.
  ~ Duration :: 0-4: 36 38 39 41 42 | 5-9: 44 46 47 49 50 | 10-14: 52 54 55 57 58 | 15-19: 60 62 63 65 66 | 20-21: 68 70
  # causes: Energy Gain
Fire Storm #197 | Spell | Core | E10 C2 R20
  Create a Fire Storm at target foe's location. For 10 seconds, foes adjacent to that location are struck for 5..35 fire damage each second.
  ~ Fire damage :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  # causes: Fire Damage; target: foes; aoe: adjacent
Fireball #186 | Spell | Core | E10 R7
  Send out a ball of fire that strikes target foe and all nearby foes for 7..112 fire damage.
  ~ Fire damage :: 0-4: 7 14 21 28 35 | 5-9: 42 49 56 63 70 | 10-14: 77 84 91 98 105 | 15-19: 112 119 126 133 140 | 20-21: 147 154
  # causes: Fire Damage; target: foes; aoe: nearby
Flame Burst #188 | Spell | Prophecies | E15 C¾ R5
  All nearby foes are struck for 15..120 fire damage.
  ~ Fire damage :: 0-4: 15 22 29 36 43 | 5-9: 50 57 64 71 78 | 10-14: 85 92 99 106 113 | 15-19: 120 127 134 141 148 | 20-21: 155 162
  # causes: Fire Damage; target: untargeted; aoe: nearby
Flame Djinn's Haste #1381 | Enchantment Spell | Nightfall | E10 C¾ R20
  All adjacent foes are struck for 15..120 fire damage. For 8..14 seconds, you move 25% faster. Flame Djinn's Haste recharges 50% faster if a foe was struck by this spell.
  ~ Fire damage :: 0-4: 15 22 29 36 43 | 5-9: 50 57 64 71 78 | 10-14: 85 92 99 106 113 | 15-19: 120 127 134 141 148 | 20-21: 155 162
  ~ Duration :: 0-4: 8 8 9 9 10 | 5-9: 10 10 11 11 12 | 10-14: 12 12 13 13 14 | 15-19: 14 14 15 15 16 | 20-21: 16 16
  # causes: Fire Damage, Increased Movement Speed, Decreased Recharge Time; target: untargeted; aoe: adjacent
Flare #194 | Spell | Core | E5 C1
  Send out a flare that strikes target foe for 20..65 fire damage if it hits. If you are Overcast, Flare hits adjacent foes as well.
  ~ Fire damage :: 0-4: 20 23 26 29 32 | 5-9: 35 38 41 44 47 | 10-14: 50 53 56 59 62 | 15-19: 65 68 71 74 77 | 20-21: 80 83
  # causes: Fire Damage; target: foes; aoe: adjacent
Glowing Gaze #1379 | Spell | Nightfall | E5 C1 R8
  Target foe takes 5..50 fire damage. If that foe is on Fire, you gain 5 Energy plus 1 Energy for every 2 ranks of Energy Storage.
  ~ Fire damage :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  ~ Energy gain :: 0-4: 5 5 6 6 7 | 5-9: 7 8 8 9 9 | 10-14: 10 10 11 11 12 | 15-19: 12 13 13 14 14 | 20-21: 15 15
  # causes: Fire Damage, Energy Gain; target: foes
Glyph of Immolation #2060 | Glyph | Eye of the North | E5 C1 R10
  For 15 seconds, your next 1..4 spell[s] that target[s] a foe also cause[s] Burning for 1..4 second[s].
  ~ Spells affected :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  ~ Burning duration :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  # causes: Burning
Immolate #191 | Spell | Core | E10 C1 R5
  Target foe is struck for 20..75 fire damage and is set on fire for 1..3 second[s].
  ~ Fire damage :: 0-4: 20 24 27 31 35 | 5-9: 38 42 46 49 53 | 10-14: 57 60 64 68 71 | 15-19: 75 79 82 86 90 | 20-21: 93 97
  ~ Burning duration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Burning, Fire Damage; target: foes
Incendiary Bonds #179 | Hex Spell | Prophecies | E10 O5 C1 R7
  After 3 seconds, target foe and all nearby foes are struck for 20..80 fire damage and are set on fire for 1..3 second[s]. Activates early if target foe dies.
  ~ Fire damage :: 0-4: 20 24 28 32 36 | 5-9: 40 44 48 52 56 | 10-14: 60 64 68 72 76 | 15-19: 80 84 88 92 96 | 20-21: 100 104
  ~ Burning duration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Burning, Fire Damage; target: foes; aoe: nearby
  ! ANOMALY: Similar to Lightning Strike and Lightning Surge, removing the hex before it ends will negate the end effect, unlike Shatterstone and most other skills with an end effect.
Inferno #183 | Spell | Core | E10 C¾ R10
  All adjacent foes are struck for 30..135 fire damage.
  ~ Fire Damage :: 0-4: 30 37 44 51 58 | 5-9: 65 72 79 86 93 | 10-14: 100 107 114 121 128 | 15-19: 135 142 149 156 163 | 20-21: 170 177
  # causes: Fire Damage; target: untargeted; aoe: adjacent
Lava Arrows #824 | Spell | Factions | E5 C1 R2
  Lava Arrows fly toward up to 3 foes near your target and strike for 20..65 fire damage if they hit.
  ~ Damage :: 0-4: 20 23 26 29 32 | 5-9: 35 38 41 44 47 | 10-14: 50 53 56 59 62 | 15-19: 65 68 71 74 77 | 20-21: 80 83
  # causes: Fire Damage; target: foes; aoe: nearby
Lava Font #195 | Spell | Prophecies | E10 R4
  For 5 seconds, foes adjacent to the location where this spell was cast are struck for 5..50 fire damage each second. If you are Overcast, this spell strikes nearby foes instead of adjacent ones.
  ~ Fire damage :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Fire Damage; target: untargeted; aoe: nearby, adjacent
  ! BUG: Hero AI will use this spell without considering whether there are foes adjacent to them.
Liquid Flame #845 | Spell | Nightfall | E10 C1 R15
  Target foe is struck for 7..112 fire damage. If that foe is attacking or casting a spell, nearby foes are also struck for 7..112 fire damage.
  ~ Fire damage :: 0-4: 7 14 21 28 35 | 5-9: 42 49 56 63 70 | 10-14: 77 84 91 98 105 | 15-19: 112 119 126 133 140 | 20-21: 147 154
  # causes: Fire Damage; target: foes; aoe: nearby
Mark of Rodgort #190 | Hex Spell | Prophecies | E15 C1 R15
  Target foe and all nearby foes are hexed with Mark of Rodgort. For 10..35 seconds, whenever each foe is struck for fire damage, that foe is set on fire for 1..4 second[s].
  ~ Duration :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  ~ Burning duration :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  # causes: Burning; target: foes
Meteor #187 | Spell | Core | E5 O10 C2 R30
  Target foe and all adjacent foes are struck for 7..112 fire damage and knocked down.
  ~ Fire damage :: 0-4: 7 14 21 28 35 | 5-9: 42 49 56 63 70 | 10-14: 77 84 91 98 105 | 15-19: 112 119 126 133 140 | 20-21: 147 154
  # causes: Fire Damage, Knockdown; target: foes; range: Casting; aoe: adjacent
  ! ANOMALY: There is a short delay between the skill activation and the actual effect of this spell that is not stated in the description. This spell actually hits target foe's location one second after being activated (and doesn't compensate for the movement of the target), so the effect can be avoided with speed boosts (including the speed buff given to hostile NPCs in Hard mode).
Meteor Shower #192 | Spell | Prophecies | E25 O10 C5 R60
  Create a Meteor Shower at target foe's location. For 9 seconds, foes adjacent to that location are struck for 7..112 fire damage and knocked down every 3 seconds.
  ~ Fire damage :: 0-4: 7 14 21 28 35 | 5-9: 42 49 56 63 70 | 10-14: 77 84 91 98 105 | 15-19: 112 119 126 133 140 | 20-21: 147 154
  # causes: Fire Damage, Knockdown; target: foes; range: Casting; aoe: adjacent
Mind Blast #1662 | Elite Spell | Nightfall | E5 C1 R2
  Target foe is struck for 15..60 fire damage. If you have more Energy than target foe, you gain 1..8 Energy.
  ~ Fire damage :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  ~ Energy gain :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  # causes: Fire Damage, Energy Gain; target: foes
Mind Burn #185 | Elite Spell | Core | E5 O5 C1 R5
  Target foe and all adjacent foes take 15..60 fire damage. If you have more Energy than target foe, that foe and all adjacent foes take an additional 15..60 fire damage and are set on fire for 1..10 second[s].
  ~ Fire damage :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  ~ + Fire damage :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  ~ Burning duration :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # causes: Fire Damage, Burning; target: foes; range: Casting; aoe: adjacent
  ! ANOMALY: This skill checks the energy condition independently for each target hit.
Phoenix #193 | Spell | Prophecies | E10 R7
  A fiery Phoenix rises at your location and flies out to your target, exploding on impact. This explosion strikes your target and nearby foes for 10..60 fire damage. If you are Overcast, allies in the blast radius are healed for 20..80 Health.
  ~ Fire damage :: 0-4: 10 13 17 20 23 | 5-9: 27 30 33 37 40 | 10-14: 43 47 50 53 57 | 15-19: 60 63 67 70 73 | 20-21: 77 80
  ~ Healing :: 0-4: 20 24 28 32 36 | 5-9: 40 44 48 52 56 | 10-14: 60 64 68 72 76 | 15-19: 80 84 88 92 96 | 20-21: 100 104
  # causes: Fire Damage, Healing; requires: Overcast; target: foes; aoe: nearby
Rodgort's Invocation #189 | Spell | Prophecies | E25 C2 R8
  Target foe and all nearby foes are struck for 15..120 fire damage and set on fire for 1..3 second[s].
  ~ Fire damage :: 0-4: 15 22 29 36 43 | 5-9: 50 57 64 71 78 | 10-14: 85 92 99 106 113 | 15-19: 120 127 134 141 148 | 20-21: 155 162
  ~ Burning duration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Burning, Fire Damage; target: foes; aoe: nearby
Savannah Heat (PvP) #3021 | Elite Spell | Nightfall | E15 C2 R25
  You create Savannah Heat at target foe's location. For 5 seconds, all nearby foes take 5..20 fire damage for each second this spell has been in effect.
  ~ Fire damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ + Fire damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Maximum damage :: 0-4: 75 90 105 120 135 | 5-9: 150 165 180 195 210 | 10-14: 225 240 255 270 285 | 15-19: 300 315 330 345 360 | 20-21: 375 390
  # causes: Fire Damage; target: foes; aoe: nearby
Searing Flames #884 | Elite Spell | Nightfall | E15 C1 R2
  Target foe and all nearby foes are struck with Searing Flames. Foes already on fire when this skill is cast are struck for 10..100 fire damage. Foes not already on fire begin Burning for 1..7 seconds.
  ~ Fire damage :: 0-4: 10 16 22 28 34 | 5-9: 40 46 52 58 64 | 10-14: 70 76 82 88 94 | 15-19: 100 106 112 118 124 | 20-21: 130 136
  ~ Burning duration :: 0-4: 1 1 2 2 3 | 5-9: 3 3 4 4 5 | 10-14: 5 5 6 6 7 | 15-19: 7 7 8 8 9 | 20-21: 9 9
  # causes: Fire Damage, Burning; target: foes; range: Casting; aoe: nearby
Searing Heat #196 | Spell | Prophecies | E15 C2 R25
  Cause Searing Heat at target foe's location. For 5 seconds, foes near this location are struck for 10..40 fire damage each second. When Searing Heat ends, foes in the area of effect are set on fire for 3 seconds.
  ~ Fire damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Burning, Fire Damage; target: foes; aoe: nearby
Smoldering Embers #1090 | Hex Spell | Factions | E10 R7
  Target foe is struck for 10..70 fire damage. If you are Overcast, that foe is hexed with Smoldering Embers for 3 seconds and takes 5..25 additional fire damage each second.
  ~ Fire damage :: 0-4: 10 14 18 22 26 | 5-9: 30 34 38 42 46 | 10-14: 50 54 58 62 66 | 15-19: 70 74 78 82 86 | 20-21: 90 94
  ~ Fire damage each second :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  # causes: Fire Damage
Star Burst #1095 | Elite Touch spell | Factions | E5 C¾ R7
  Elite Spell. Target touched foe and all foes in the area are struck for 7..112 fire damage and set on fire for 1..4 second[s]. For each foe you hit, gain 2 Energy.
  ~ Fire damage :: 0-4: 7 14 21 28 35 | 5-9: 42 49 56 63 70 | 10-14: 77 84 91 98 105 | 15-19: 112 119 126 133 140 | 20-21: 147 154
  ~ Burning duration :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  # causes: Burning, Fire Damage, Energy Gain; target: foes; range: touch; aoe: in the area
  ! BUG: In the Polish translation, description was not updated when skill functionality changed. It still says: You lose 5 Energy if more than one foe is struck.
Teinai's Heat #1093 | Ward Spell | Factions | E15 C1 R20
  Place a ward of Teinai's Heat at your location for 10..15 seconds. Foes within the ward suffer 2..5 health degeneration. Weakened foes attack 33% slower. This skill is disabled for 20 seconds.
  ~ Duration :: 0-4: 10 10 11 11 11 | 5-9: 12 12 12 13 13 | 10-14: 13 14 14 14 15 | 15-19: 15 15 16 16 16 | 20-21: 17 17
  ~ Health degeneration :: 0-4: 2 2 2 3 3 | 5-9: 3 3 3 4 4 | 10-14: 4 4 4 5 5 | 15-19: 5 5 5 6 6 | 20-21: 6 6
  # causes: Health Degeneration, Decreased Attack Speed, Disable

### Elementalist / No Attribute
Glyph of Concentration #201 | Glyph | Prophecies | E5 C1 R10
  For 15 seconds, your next 1 spell cannot be interrupted and ignores the effects of being Dazed.
  ! BUG: It is sometimes possible to be interrupted by a Destroyer of Deeds using Broad Head Arrow in Glint's Challenge or by the environment effect Cathedral Collapse in Arborstone while this glyph is still active.
Glyph of Elemental Power #198 | Glyph | Core | E5 C1 R5
  For 25 seconds, your elemental attributes are boosted by 2 for your next 10 spells.
  # causes: Increased Attribute
  ! ANOMALY: This skill actually behaves identically to Glyph of Energy, in that your elemental attributes are boosted for all purposes while under the effects of this glyph. * Non-spell skills (Lightning Touch, Shock, Glyph of Immolation and Glyph of Swiftness) will take advantage of the bonus and will not count as a use of the glyph. * Any elemental attribute raised to at least 9 will trigger the bonus armor from Prismatic Insignia.
Glyph of Essence #1096 | Glyph | Factions | E5 C1 R20
  For 15 seconds, your next spell casts instantly but causes you to lose all Energy.
  # causes: Decreased Activation Time, Energy Loss
Glyph of Renewal #203 | Elite Glyph | Prophecies | E5 C1 R10
  For 15 seconds, your next spell instantly recharges.
  # causes: Recharge
Glyph of Sacrifice #202 | Glyph | Prophecies | E5 C1 R15
  For 15 seconds, your next spell casts instantly, but it takes an additional 30 seconds to recharge. Ends prematurely if you use a non-spell skill.
  # causes: Increased Recharge Time, Decreased Activation Time
  ! ANOMALY: Despite the descriptions saying that the next spell casts instantly, a better description would be very quickly, as the activation time of the spell cast through it is a 1/4 second and there's still a slight chance it might be interrupted.
Second Wind #1088 | Elite Spell | Factions | E5 O5 C1 R5
  You gain 1 Energy and 5 Health for each point of Energy restricted by Overcast. You lose all enchantments.
  # causes: Energy Gain, Health Gain; removes: Enchantment

### Elementalist / Water Magic
Armor of Frost #206 | Enchantment Spell | Prophecies | E5 C1 R20
  For 10..34 seconds, you gain +40 armor against physical damage and have +1 Water Magic.
  ~ Duration :: 0-4: 10 12 13 15 16 | 5-9: 18 20 21 23 24 | 10-14: 26 28 29 31 32 | 15-19: 34 36 37 39 40 | 20-21: 42 44
  # causes: Increased Armor Rating, Increased Attribute
Armor of Mist #238 | Enchantment Spell | Prophecies | E10 C1 R30
  For 8..20 seconds, you gain +10..40 armor and move 33% faster.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  ~ + Armor rating :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Increased Armor Rating, Increased Movement Speed; target: self
Blurred Vision #235 | Hex Spell | Core | E10 C1 R12
  For 4..10 seconds, target foe and adjacent foes are hexed with Blurred Vision. While hexed, those foes have a 50% chance to miss with attacks.
  ~ Duration :: 0-4: 4 4 5 5 6 | 5-9: 6 6 7 7 8 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 12
  # causes: Miss; target: foes; aoe: adjacent
Conjure Frost #207 | Enchantment Spell | Core | E10 C1 R30
  For 60 seconds, if you're wielding a cold weapon, your attacks strike for an additional 5..20 cold damage.
  ~ + Cold damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Cold Damage; target: self
Deep Freeze #234 | Hex Spell | Core | E25 C2 R15
  You cause a Deep Freeze at target foe's location. All foes in this area are struck for 10..85 cold damage, and for 10 seconds, they move 66% slower.
  ~ Cold damage :: 0-4: 10 15 20 25 30 | 5-9: 35 40 45 50 55 | 10-14: 60 65 70 75 80 | 15-19: 85 90 95 100 105 | 20-21: 110 115
  # causes: Cold Damage, Decreased Movement Speed; target: foes; aoe: in the area
Freezing Gust #1382 | Hex Spell | Nightfall | E10 C1 R8
  If target foe is under the effect of a Water Magic hex, that foe is struck for 20..80 cold damage. Otherwise, that foe moves 66% slower for 1..5 second[s].
  ~ Cold damage :: 0-4: 20 24 28 32 36 | 5-9: 40 44 48 52 56 | 10-14: 60 64 68 72 76 | 15-19: 80 84 88 92 96 | 20-21: 100 104
  ~ Duration :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Cold Damage, Decreased Movement Speed; target: foes
Frigid Armor #1261 | Enchantment Spell | Nightfall | E5 C1 R20
  For 10..25 seconds, you have +10..40 armor against physical damage and cannot be set on fire.
  ~ Duration :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  ~ + Armor rating :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Increased Armor Rating, Condition Immunity; target: self
  ! ANOMALY: This skill does not remove existing Burning, unlike other skills that grant immunity to a condition (e.g. Tainted Flesh removes Disease).
Frozen Burst #212 | Hex Spell | Prophecies | E15 C¾ R8
  All nearby foes are struck for 10..85 cold damage and move 66% slower for 3..8 seconds.
  ~ Cold damage :: 0-4: 10 15 20 25 30 | 5-9: 35 40 45 50 55 | 10-14: 60 65 70 75 80 | 15-19: 85 90 95 100 105 | 20-21: 110 115
  ~ Duration :: 0-4: 3 3 4 4 4 | 5-9: 5 5 5 6 6 | 10-14: 6 7 7 7 8 | 15-19: 8 8 9 9 9 | 20-21: 10 10
  # causes: Cold Damage, Decreased Movement Speed; target: untargeted; aoe: nearby
  ! BUG: Some foes (notably Ice Elementals in pre-Searing) will sometimes overestimate this skill's range and use it while foes are slightly out of it.
Glowing Ice #2192 | Spell | Eye of the North | E5 C1 R8
  Target foe is struck for 5..50 cold damage. If that foe is under the effects of a Water Magic hex, you gain 5 Energy plus 1 Energy for every 2 ranks of Energy Storage.
  ~ Cold damage :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  ~ Energy gain :: 0-4: 5 5 6 6 7 | 5-9: 7 8 8 9 9 | 10-14: 10 10 11 11 12 | 15-19: 12 13 13 14 14 | 20-21: 15 15
  # causes: Cold Damage, Energy Gain; target: foes
Ice Prison #210 | Hex Spell | Prophecies | E10 C2 R30
  For 8..20 seconds, target foe's legs are encased in ice, causing the foe to move 66% slower.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  # causes: Decreased Movement Speed; target: foes
Ice Spear #214 | Enchantment spell | Core | E5 C1
  Send out an Ice Spear, striking target foe for 10..60 cold damage if it hits. If you are Overcast, you gain +1..4 Health regeneration for 5 seconds.
  ~ Cold damage :: 0-4: 10 13 17 20 23 | 5-9: 27 30 33 37 40 | 10-14: 43 47 50 53 57 | 15-19: 60 63 67 70 73 | 20-21: 77 80
  ~ Health regeneration :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  # causes: Cold Damage, Health Regeneration; target: foes
  ! ANOMALY: Similar to other enchantments that target a foe, foes affected by Well of the Profane or spirits cannot be targeted by this enchantment.
Ice Spikes #211 | Hex Spell | Core | E15 R10
  Target and adjacent foes are struck for 20..80 cold damage and move 66% slower for 2..6 seconds.
  ~ Cold damage :: 0-4: 20 24 28 32 36 | 5-9: 40 44 48 52 56 | 10-14: 60 64 68 72 76 | 15-19: 80 84 88 92 96 | 20-21: 100 104
  ~ Duration :: 0-4: 2 2 3 3 3 | 5-9: 3 4 4 4 4 | 10-14: 5 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 7 8
  # causes: Cold Damage, Decreased Movement Speed; target: foes; aoe: adjacent
Icy Prism #903 | Spell | Factions | E5 O5 C1 R5
  Target foe is struck for 15..75 cold damage. If that foe has a Water Magic hex, Icy Prism deals +15..75 cold damage to all other nearby foes.
  ~ Cold damage :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  ~ + Cold damage :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  # causes: Cold Damage; target: foes; aoe: nearby
Icy Shackles #939 | Elite Hex Spell | Nightfall | E10 C1 R12
  For 1..10 second[s], target foe's movement speed is reduced by 66%. While under the effects of an enchantment, that foe's movement is reduced by 90%.
  ~ Duration :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # causes: Decreased Movement Speed
Maelstrom #215 | Spell | Core | E15 O10 C1½ R20
  Create a Maelstrom at target foe's location. For 10 seconds, foes adjacent to that area are struck for 10..25 cold damage each second. Maelstrom interrupts spell-casting when it hits.
  ~ Cold damage :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  # causes: Cold Damage, Interrupt; target: foes; range: Casting; aoe: adjacent
Mind Freeze (PvP) #2803 | Elite Hex Spell | Core | E10 O5 C1 R5
  Target foe takes 10..60 cold damage. If you have more Energy than target foe, that foe suffers an additional 10..60 cold damage and moves 90% slower for 1..5 seconds.
  ~ Cold damage :: 0-4: 10 13 17 20 23 | 5-9: 27 30 33 37 40 | 10-14: 43 47 50 53 57 | 15-19: 60 63 67 70 73 | 20-21: 77 80
  ~ + Cold damage :: 0-4: 10 13 17 20 23 | 5-9: 27 30 33 37 40 | 10-14: 43 47 50 53 57 | 15-19: 60 63 67 70 73 | 20-21: 77 80
  ~ Duration :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Cold Damage, Decreased Movement Speed
Mirror of Ice #1098 | Elite Hex Spell | Factions | E10 C¾ R15
  Shatter a Mirror of Ice. All foes near you and target ally take 15..70 cold damage and move 66% slower for 2..6 seconds. If you strike a foe hexed with Water Magic, Mirror of Ice recharges 50% faster.
  ~ Cold damage :: 0-4: 15 19 22 26 30 | 5-9: 33 37 41 44 48 | 10-14: 52 55 59 63 66 | 15-19: 70 74 77 81 85 | 20-21: 88 92
  ~ Duration :: 0-4: 2 2 3 3 3 | 5-9: 3 4 4 4 4 | 10-14: 5 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 7 8
  # causes: Cold Damage, Decreased Movement Speed, Decreased Recharge Time; target: allies or foes
Mist Form (PvP) #2805 | Elite Enchantment Spell | Prophecies | E5 C1 R20
  For 10..45 seconds, you take 33% less damage from foes under the effects of Water Magic hexes. Whenever you cast an elemental spell, all non-spirit allies in earshot are healed for 50..250% of the Energy cost of the spell. This spell does not heal allies above 80% Health.
  ~ Duration :: 0-4: 10 12 15 17 19 | 5-9: 22 24 26 29 31 | 10-14: 33 36 38 40 43 | 15-19: 45 47 50 52 54 | 20-21: 57 59
  ~ Healing % :: 0-4: 50 63 77 90 103 | 5-9: 117 130 143 157 170 | 10-14: 183 197 210 223 237 | 15-19: 250 263 277 290 303 | 20-21: 317 330
  ~ 5 Energy spell heal :: 0-4: 2 3 4 4 5 | 5-9: 6 6 7 8 8 | 10-14: 9 10 10 11 12 | 15-19: 12 13 14 14 15 | 20-21: 16 16
  ~ 10 Energy spell heal :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  ~ 15 Energy spell heal :: 0-4: 7 9 11 13 15 | 5-9: 17 19 21 23 25 | 10-14: 27 29 31 33 35 | 15-19: 37 39 41 43 45 | 20-21: 47 49
  ~ 25 Energy spell heal :: 0-4: 12 16 19 22 26 | 5-9: 29 32 36 39 42 | 10-14: 46 49 52 56 59 | 15-19: 62 66 69 72 76 | 20-21: 79 82
  # causes: Damage Reduction, Healing; target: untargeted; aoe: earshot
Rust #204 | Hex Spell | Core | E10 C1 R8
  Deals 10..85 cold damage to target and adjacent foes. For 5..20 seconds, target foe and all adjacent foes take twice as long to activate signets. If you are Overcast, foes struck with Rust have their signets interrupted and disabled for 1..10 second[s].
  ~ Cold damage :: 0-4: 10 15 20 25 30 | 5-9: 35 40 45 50 55 | 10-14: 60 65 70 75 80 | 15-19: 85 90 95 100 105 | 20-21: 110 115
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Disable duration :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # causes: Cold Damage, Increased Activation Time, Interrupt, Disable; aoe: adjacent
Shard Storm #213 | Hex Spell | Prophecies | E10 C1 R10
  Send out an ice shard that strikes target foe for 10..85 cold damage if it hits and causing target foe to move 66% slower for 2..6 seconds.
  ~ Cold damage :: 0-4: 10 15 20 25 30 | 5-9: 35 40 45 50 55 | 10-14: 60 65 70 75 80 | 15-19: 85 90 95 100 105 | 20-21: 110 115
  ~ Duration :: 0-4: 2 2 3 3 3 | 5-9: 3 4 4 4 4 | 10-14: 5 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 7 8
  # causes: Cold Damage, Decreased Movement Speed; target: foes
Shatterstone #809 | Elite Hex Spell | Factions | E10 C2 R8
  Target foe is struck for 25..100 cold damage, moves 66% slower, and is hexed with Shatterstone for 3 seconds. When Shatterstone ends, that foe and all nearby foes are struck for 25..100 cold damage.
  ~ Cold damage :: 0-4: 25 30 35 40 45 | 5-9: 50 55 60 65 70 | 10-14: 75 80 85 90 95 | 15-19: 100 105 110 115 120 | 20-21: 125 130
  ~ Cold damage :: 0-4: 25 30 35 40 45 | 5-9: 50 55 60 65 70 | 10-14: 75 80 85 90 95 | 15-19: 100 105 110 115 120 | 20-21: 125 130
  # causes: Cold Damage; aoe: nearby
Slippery Ground (PvP) #3398 | Spell | Eye of the North | E5 C1 R15
  If target foe is Blind or moving, that foe is knocked down. (50% failure chance with Water Magic 4 or less.)
  # causes: Knockdown; target: foes
Steam #846 | Spell | Nightfall | E5 C1 R8
  Target foe is struck for 20..60 cold damage. If target foe is on fire, Steam Blinds that foe for 5..10 seconds and they take an additional 20..60 fire damage.
  ~ Cold damage :: 0-4: 20 23 25 28 31 | 5-9: 33 36 39 41 44 | 10-14: 47 49 52 55 57 | 15-19: 60 63 65 68 71 | 20-21: 73 76
  ~ Blind duration :: 0-4: 5 5 6 6 6 | 5-9: 7 7 7 8 8 | 10-14: 8 9 9 9 10 | 15-19: 10 10 11 11 11 | 20-21: 12 12
  ~ Fire damage :: 0-4: 20 23 25 28 31 | 5-9: 33 36 39 41 44 | 10-14: 47 49 52 55 57 | 15-19: 60 63 65 68 71 | 20-21: 73 76
  # causes: Cold Damage, Blind; target: foes
Swirling Aura #233 | Enchantment Spell | Prophecies | E10 C1 R15
  For 3..7 second[s], you are enchanted with Swirling Aura and have 1..6 Health regeneration and a 50% chance to block projectiles. If you are Overcast when you cast this spell, all party members in earshot are also enchanted.
  ~ Duration :: 0-4: 3 3 4 4 4 | 5-9: 4 5 5 5 5 | 10-14: 6 6 6 6 7 | 15-19: 7 7 8 8 8 | 20-21: 8 9
  ~ Health regeneration :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  # causes: Health Regeneration, Block; target: untargeted; aoe: earshot
Teinai's Prison #1097 | Hex Spell | Factions | E10 C1 R15
  For 1..8 second[s], target foe's legs are encased in ice, causing the foe to move 66% slower. If that foe has Cracked Armor, the chill seeps through causing 5..9 Health degeneration.
  ~ Duration :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  ~ Health degeneration :: 0-4: 5 5 6 6 6 | 5-9: 6 7 7 7 7 | 10-14: 8 8 8 8 9 | 15-19: 9 9 10 10 10 | 20-21: 10 11
  # causes: Decreased Movement Speed, Health Degeneration
Vapor Blade #866 | Spell | Factions | E5 O5 R7
  Target foe is struck for 15..135 cold damage. Vapor Blade deals half damage if that foe has any enchantments on them.
  ~ Cold damage :: 0-4: 15 23 31 39 47 | 5-9: 55 63 71 79 87 | 10-14: 95 103 111 119 127 | 15-19: 135 143 151 159 167 | 20-21: 175 183
  # causes: Cold Damage; target: foes
Ward Against Harm (PvP) #2806 | Elite Ward Spell | Prophecies | E15 C1 R20
  Create a Ward Against Harm at this location. For 5..15 seconds, non-spirit allies in this area have +1..3 health regeneration, +12..24 armor, and an additional +12..24 armor against elemental damage. This spell is disabled for 30 seconds.
  ~ Duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  ~ Health regeneration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  ~ +Armor :: 0-4: 12 13 14 14 15 | 5-9: 16 17 18 18 19 | 10-14: 20 21 22 22 23 | 15-19: 24 25 26 26 27 | 20-21: 28 29
  ~ +Armor vs elemental damage :: 0-4: 12 13 14 14 15 | 5-9: 16 17 18 18 19 | 10-14: 20 21 22 22 23 | 15-19: 24 25 26 26 27 | 20-21: 28 29
  # causes: Health Regeneration, Increased Armor Rating
  ! BUG: This skill does not actually become disabled, as it can be instantly recharged by Glyph of Renewal, and the recharge reduced by Glyph of Swiftness.
  ! BUG: This skill does not actually become disabled, as it can be instantly recharged by Glyph of Renewal, and the recharge reduced by Glyph of Swiftness. [from PvE version page]
Water Attunement #208 | Enchantment Spell | Core | E10 C1 R30
  For 36..60 seconds, you are attuned to Water. You gain 1 Energy plus 30% of the base Energy cost of the skill each time you use Water Magic.
  ~ Duration :: 0-4: 36 38 39 41 42 | 5-9: 44 46 47 49 50 | 10-14: 52 54 55 57 58 | 15-19: 60 62 63 65 66 | 20-21: 68 70
  # causes: Energy Gain
Water Trident #237 | Elite Spell | Prophecies | E5 C1 R3
  Send out a fast-moving Water Trident, striking target foe and up to 2 adjacent foes for 10..90 cold damage if it hits. If it hits a moving foe, that foe is knocked down.
  ~ Cold damage :: 0-4: 10 15 21 26 31 | 5-9: 37 42 47 53 58 | 10-14: 63 69 74 79 85 | 15-19: 90 95 101 106 111 | 20-21: 117 122
  # causes: Cold Damage, Knockdown, Increased Projectile Speed; target: foes; aoe: adjacent
Winter's Embrace #1999 | Hex Spell | Eye of the North | E10 C¾ R15
  For 2..6 seconds, target foe moves 66% slower and takes 5..15 damage while moving.
  ~ Duration :: 0-4: 2 2 3 3 3 | 5-9: 3 4 4 4 4 | 10-14: 5 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 7 8
  ~ Damage while moving :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Decreased Movement Speed

## Assassin

### Assassin / Critical Strikes
Assassin's Remedy (PvP) #2869 | Enchantment Spell | Nightfall | E10 C1 R20
  For 30 seconds, the next 1..10 attack skills you use remove one condition.
  ~ Attack skills :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # removes: Condition; target: self
  ! ANOMALY: Using a pet attack while enchanted with Assassin's Remedy doesn't remove a condition, unlike Zealous Anthem and Anthem of Fury. [from PvE version page]
Black Lotus Strike #779 | Lead Attack | Factions | E5 R6
  If it hits, Black Lotus Strike strikes for +10..31 damage. If target foe is suffering from a Hex, you gain 5..13 Energy.
  ~ + Damage :: 0-4: 10 11 13 14 16 | 5-9: 17 18 20 21 23 | 10-14: 24 25 27 28 30 | 15-19: 31 32 34 35 37 | 20-21: 38 39
  ~ Energy gain :: 0-4: 5 6 6 7 7 | 5-9: 8 8 9 9 10 | 10-14: 10 11 11 12 12 | 15-19: 13 14 14 15 15 | 20-21: 16 16
  # causes: Energy Gain; checks: hex
Critical Defenses #1027 | Enchantment Spell | Factions | E10 C1 R30
  For 4..10 seconds, you have a 75% chance to block. Critical Defenses refreshes every time you land a critical hit.
  ~ Duration :: 0-4: 4 4 5 5 6 | 5-9: 6 6 7 7 8 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 12
  # causes: Block, Renewal
Critical Eye #1018 | Skill | Factions | E5 R30
  For 10..35 seconds, you have an additional 3..15% chance to land a critical hit when attacking. You gain 1 Energy whenever you score a critical hit.
  ~ Duration :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  ~ % for Critical hit :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Critical Hit, Energy Gain
Critical Strike #1019 | Dual Attack | Factions | E5 R6
  Must follow an off-hand attack. If it hits, this attack strikes for +10..30 damage, results in a critical hit, and you gain 1..3 Energy.
  ~ Damage :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  ~ Energy :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Critical Hit, Energy Gain; requires: offhand; target: foes; checks: hit
Dark Apostasy #1029 | Elite Enchantment Spell | Factions | E10 C¼ R15
  For 3..17 seconds, every time you successfully land a critical hit, you remove one enchantment from your target. If you remove an enchantment in this way, you lose 10..3 Energy or Dark Apostasy ends.
  ~ Duration :: 0-4: 3 4 5 6 7 | 5-9: 8 9 10 10 11 | 10-14: 12 13 14 15 16 | 15-19: 17 18 19 20 21 | 20-21: 22 23
  ~ Energy loss :: 0-4: 10 10 9 9 8 | 5-9: 8 7 7 6 6 | 10-14: 5 5 4 4 3 | 15-19: 3 3 2 2 1 | 20-21: 1 0
  # causes: Energy Loss; removes: Enchantment
Deadly Haste #1638 | Enchantment Spell | Nightfall | E5 C1 R20
  For 10..35 seconds, half-ranged spells cast 5..50% faster and recharge 5..60% faster.
  ~ Duration :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  ~ Casting % :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  ~ Recharge % :: 0-4: 5 9 12 16 20 | 5-9: 23 27 31 34 38 | 10-14: 42 45 49 53 56 | 15-19: 60 64 67 71 75 | 20-21: 78 82
  # causes: Decreased Activation Time, Decreased Recharge Time
Locust's Fury #1030 | Elite Enchantment Spell | Factions | E10 C½ R10
  For 10..35 seconds, you have an additional 50% chance to double strike while using daggers.
  ~ Duration :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
Malicious Strike #1633 | Melee Attack | Nightfall | E5 R6
  If this attack hits a foe suffering from a condition, you deal +10..30 damage and this attack results in a critical hit.
  ~ + Damage :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  # causes: Critical Hit; checks: condition
Palm Strike #1045 | Elite Touch skill | Factions | E5 C¾ R7
  Elite Skill. Target touched foe takes 10..65 damage and is Crippled for 1..5 second[s]. This skill counts as an off-hand attack.
  ~ Damage :: 0-4: 10 14 17 21 25 | 5-9: 28 32 36 39 43 | 10-14: 47 50 54 58 61 | 15-19: 65 69 72 76 80 | 20-21: 83 87
  ~ Crippled duration :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Crippled; target: foes; range: touch
Seeping Wound #1034 | Elite Hex Spell | Factions | E10 C¼ R10
  For 1..7 second[s], target foe moves 33% slower. That foe takes 5..25 damage each second while suffering from a condition.
  ~ Duration :: 0-4: 1 1 2 2 3 | 5-9: 3 3 4 4 5 | 10-14: 5 5 6 6 7 | 15-19: 7 7 8 8 9 | 20-21: 9 9
  ~ Damage :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  # causes: Decreased Movement Speed
Sharpen Daggers #926 | Enchantment Spell | Factions | E5 C½ R20
  For 5..30 seconds, your dagger attacks cause Bleeding for 5..15 seconds.
  ~ Duration :: 0-4: 5 7 8 10 12 | 5-9: 13 15 17 18 20 | 10-14: 22 23 25 27 28 | 15-19: 30 32 33 35 37 | 20-21: 38 40
  ~ Bleeding duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Bleeding
  ! BUG: If a ranged weapon is swapped for daggers after the attack was made and before the projectile hit, Sharpen Daggers will count this projectile hit as a dagger attack.
Shattering Assault #1634 | Elite Dual Attack | Nightfall | E10 R6
  Must follow an off-hand attack. If it hits, you deal 5..50 damage and target foe loses one enchantment. This attack cannot be blocked.
  ~ Damage :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Unblockable; removes: Enchantment; requires: offhand; unblockable; checks: hit
  ! BUG: This skill replaces your dagger's attack damage with the stated damage, which is non-armor-ignoring damage (unlike other attack skills such as Distracting Shot and Needling Shot). This damage is affected by Dagger Mastery, critical hits, armor penetration, inscription and inscription-equivalent weapon damage bonuses and the target's armor rating, but does not benefit from the customization damage bonus.
Twisting Fangs #776 | Dual Attack | Factions | E10 R15
  Must follow an off-hand attack. If it hits, Twisting Fangs strikes for +10..20 damage and struck foe suffers from Bleeding and Deep Wound for 5..20 seconds.
  ~ + Damage :: 0-4: 10 11 11 12 13 | 5-9: 13 14 15 15 16 | 10-14: 17 17 18 19 19 | 15-19: 20 21 21 22 23 | 20-21: 23 24
  ~ Bleeding and Deep Wound duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Bleeding, Deep Wound; requires: offhand; checks: hit
Unsuspecting Strike #783 | Lead Attack | Factions | E10 R2
  If this attack hits, you strike for +19..31 damage. If your target was above 90% Health you deal an additional 15..75 damage.
  ~ + Damage :: 0-4: 19 20 21 21 22 | 5-9: 23 24 25 25 26 | 10-14: 27 28 29 29 30 | 15-19: 31 32 33 33 34 | 20-21: 35 36
  ~ + Damage >90% health :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  # checks: health
Way of the Assassin #1649 | Elite Stance | Nightfall | E5 R12
  For the next 20 seconds while wielding daggers, you attack 5..20% faster and have a +5..35% chance to land a critical hit.
  ~ Attack speed increase :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ + Critical hit chance :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  # causes: Increased Attack Speed, Critical Hit
Way of the Master #2187 | Enchantment Spell | Eye of the North | E5 C¼ R30
  For 60 seconds, while holding a non-dagger weapon, you have an additional 3..33% chance to land a critical hit.
  ~ Additional crit chance% :: 0-4: 3 5 7 9 11 | 5-9: 13 15 17 19 21 | 10-14: 23 25 27 29 31 | 15-19: 33 35 37 39 41 | 20-21: 43 45
  # causes: Critical Hit

### Assassin / Dagger Mastery
Black Mantis Thrust #1024 | Lead Attack | Factions | E5 C1 R6
  If this attack hits, you strike for +8..20 damage. If target foe is suffering from a Hex, that foe is Crippled for 3..15 seconds.
  ~ + Damage :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  ~ Crippled duration :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Crippled; checks: hexed
Black Spider Strike #1636 | Off-Hand Attack | Nightfall | E5 R8
  Must strike a hexed foe. If it hits, this attack strikes for +5..20 damage and target foe is Poisoned for 5..20 seconds.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Poison duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Poison; requires: hexed
Blades of Steel #1020 | Dual Attack | Factions | E5 R8
  Must follow an off-hand attack. If it hits, this attack strikes for +5..16 damage (maximum bonus 60) for each recharging dagger attack.
  ~ + Damage :: 0-4: 5 6 6 7 8 | 5-9: 9 9 10 11 12 | 10-14: 12 13 14 15 15 | 15-19: 16 17 17 18 19 | 20-21: 20 20
  # requires: offhand
  ! BUG: Melee attacks also contribute to the bonus damage of this skill.
Death Blossom (PvP) #3061 | Dual Attack | Factions | E5 R6
  Must follow an off-hand attack. If it hits, Death Blossom strikes target foe for +20..45 damage and all adjacent foes take 20..45 damage.
  ~ + Damage :: 0-4: 20 22 23 25 27 | 5-9: 28 30 32 33 35 | 10-14: 37 38 40 42 43 | 15-19: 45 47 48 50 52 | 20-21: 53 55
  ~ Damage (adjacent foes) :: 0-4: 20 22 23 25 27 | 5-9: 28 30 32 33 35 | 10-14: 37 38 40 42 43 | 15-19: 45 47 48 50 52 | 20-21: 53 55
  # requires: offhand; aoe: adjacent
Desperate Strike #948 | Lead Attack | Factions | E5 R6
  If you have less than 50..80% Health, you deal +15..60 damage.
  ~ % Health :: 0-4: 50 52 54 56 58 | 5-9: 60 62 64 66 68 | 10-14: 70 72 74 76 78 | 15-19: 80 82 84 86 88 | 20-21: 90 92
  ~ + Damage :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
Disrupting Stab #1025 | Lead Attack | Factions | E5 R10
  If this attack hits, it interrupts target foe's action. If that action was a spell, it is disabled for 3..10 seconds.
  ~ Disabled duration :: 0-4: 3 3 4 4 5 | 5-9: 5 6 6 7 7 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 13
  # causes: Interrupt, Disable; checks: hit
Exhausting Assault #975 | Dual Attack | Factions | E5 C½ R8
  Must follow a lead attack. Target foe's action is interrupted. If that action was casting a spell, target foe suffers 10 Overcast.
  # causes: Interrupt, Overcast; requires: lead; target: foes; aoe: none; interrupts
Falling Lotus Strike #1990 | Off-Hand Attack | Eye of the North | E5 R8
  Must strike a knocked-down foe. If it hits, you strike for +15..35 damage and gain 1..12 Energy.
  ~ + Damage :: 0-4: 15 16 18 19 20 | 5-9: 22 23 24 26 27 | 10-14: 28 30 31 32 34 | 15-19: 35 36 38 39 40 | 20-21: 42 43
  ~ Energy gain :: 0-4: 1 2 2 3 4 | 5-9: 5 5 6 7 8 | 10-14: 8 9 10 11 11 | 15-19: 12 13 13 14 15 | 20-21: 16 16
  # causes: Energy Gain; requires: knockdown
Falling Spider #778 | Off-Hand Attack | Factions | E5 R8
  Must strike a knocked-down foe. If it hits, Falling Spider strikes for +15..35 damage and target foe is Poisoned for 5..20 seconds.
  ~ + Damage :: 0-4: 15 16 18 19 20 | 5-9: 22 23 24 26 27 | 10-14: 28 30 31 32 34 | 15-19: 35 36 38 39 40 | 20-21: 42 43
  ~ Poisoned duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Poison; requires: knockdown
Flashing Blades #1042 | Elite Stance | Factions | E10 R30
  For 5..30 seconds, you have a 75% chance to block incoming attacks while attacking. If you block an attack in this way, your attacker takes 5..20 damage.
  ~ Duration :: 0-4: 5 7 8 10 12 | 5-9: 13 15 17 18 20 | 10-14: 22 23 25 27 28 | 15-19: 30 32 33 35 37 | 20-21: 38 40
  ~ Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Block
  ! BUG: The non-concise description is wrong, attacks blocked by another blocking source while under the effects of this skill and while attacking will still trigger the damage.
Fox Fangs (PvP) #3251 | Off-Hand Attack | Factions | E5 C½ R6
  Must follow a lead attack. Fox Fangs cannot be blocked and strikes for +10..25 damage if it hits.
  ~ + Damage :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  # causes: Unblockable; requires: lead; unblockable
Fox's Promise #1640 | Elite Enchantment Spell | Nightfall | E10 C1 R20
  For 5..20 seconds, your dagger attacks cannot be blocked. This enchantment ends the next time you fail to hit.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Unblockable; target: self
Golden Fang Strike #1988 | Off-Hand Attack | Eye of the North | E5 R4
  Must follow a lead attack. If you are under the effects of an enchantment and this attack hits, target foe suffers from a Deep Wound for 5..20 seconds.
  ~ Deep Wound duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Deep Wound; requires: lead; checks: enchantment
Golden Fox Strike #1637 | Lead Attack | Nightfall | E5 R4
  If this attack hits, target foe takes +10..30 damage. If you are under the effects of an Enchantment, this attack cannot be blocked.
  ~ + Damage :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  # causes: Unblockable; checks: enchantment
Golden Lotus Strike #1026 | Lead Attack | Factions | E5 R5
  If it hits, this attack strikes for +5..20 damage. If you are under the effects of an Enchantment, you gain 5..8 Energy.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Energy gain :: 0-4: 5 5 5 6 6 | 5-9: 6 6 6 7 7 | 10-14: 7 7 7 8 8 | 15-19: 8 8 8 9 9 | 20-21: 9 9
  # causes: Energy Gain; checks: enchantment
Golden Phoenix Strike #989 | Off-Hand Attack | Factions | E5 R8
  If you are not under the effects of an enchantment, this skill misses. If it hits, Golden Phoenix Strike deals +10..30 damage and all adjacent foes take 10..30 damage.
  ~ + Damage :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  # requires: enchantment; aoe: adjacent
Golden Skull Strike #1635 | Elite Off-Hand Attack | Nightfall | E10 R15
  If you are under the effects of an enchantment and this attack hits, target foe is Dazed 1..12 seconds.
  ~ Dazed duration :: 0-4: 1 2 2 3 4 | 5-9: 5 5 6 7 8 | 10-14: 8 9 10 11 11 | 15-19: 12 13 13 14 15 | 20-21: 16 16
  # causes: Dazed; checks: enchantment
  ! ANOMALY: The concise description fails to mention that only daze will not have effect if not enchanted (the attack will not fail).
Horns of the Ox #777 | Dual Attack | Factions | E5 R12
  Must follow an off-hand attack. If it hits, Horns of the Ox strikes for +1..11 damage. If struck foe is not adjacent to any allies, that foe is knocked down.
  ~ + Damage :: 0-4: 1 2 2 3 4 | 5-9: 4 5 6 6 7 | 10-14: 8 8 9 10 10 | 15-19: 11 12 12 13 14 | 20-21: 14 15
  # causes: Knockdown; requires: offhand; checks: adjacent ally
Jagged Strike #782 | Lead Attack | Factions | E5 C½ R2
  If Jagged Strike hits, your target suffers from Bleeding for 5..20 seconds.
  ~ Bleeding duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Bleeding
Jungle Strike #1021 | Off-Hand Attack | Factions | E5 C½ R6
  Must follow a lead attack. If it hits, this attack strikes for +10..25 damage. If it hits a foe that was Crippled, that foe and all adjacent foes take 1..31 damage.
  ~ + Damage :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  ~ Conditional damage :: 0-4: 1 3 5 7 9 | 5-9: 11 13 15 17 19 | 10-14: 21 23 25 27 29 | 15-19: 31 33 35 37 39 | 20-21: 41 43
  # requires: lead; aoe: adjacent; checks: crippled
Leaping Mantis Sting #1023 | Lead Attack | Factions | E5 C½ R8
  If Mantis Sting hits, target foe takes +5..15 damage. If this attack strikes a moving foe, that foe is Crippled for 3..15 seconds.
  ~ + Damage :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  ~ Crippled duration :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Crippled; checks: movement
Lotus Strike #1987 | Off-Hand Attack | Eye of the North | E10 R12
  Must follow a lead attack. If it hits, this attack strikes for +10..25 damage and you gain 5..20 Energy.
  ~ + Damage :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  ~ Energy gain :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Energy Gain; requires: lead; checks: hit
Moebius Strike #781 | Elite Off-Hand Attack | Factions | E5 R2
  Must follow a Dual Attack. If it hits, Moebius Strike strikes for +10..35 damage. If you strike a foe whose Health is below 50%, all your other attack skills are recharged.
  ~ + Damage :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  # causes: Recharge; requires: dual; checks: health
Nine Tail Strike #986 | Dual Attack | Factions | E5 R8
  Must follow an off-hand attack. Nine Tail Strike cannot be blocked and strikes for +15..40 damage if it hits.
  ~ + Damage :: 0-4: 15 17 18 20 22 | 5-9: 23 25 27 28 30 | 10-14: 32 33 35 37 38 | 15-19: 40 42 43 45 47 | 20-21: 48 50
  # causes: Unblockable; requires: offhand; unblockable
Repeating Strike #976 | Off-Hand Attack | Factions | E5
  Must follow an off-hand attack. If it hits, this attack strikes for +10..30 damage. If it misses, it takes an additional 15 seconds to recharge.
  ~ + Damage :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  # causes: Increased Recharge Time; requires: offhand; checks: hit
Temple Strike #988 | Elite Off-Hand Attack | Factions | E15 R20
  Must follow a lead attack. If this attack hits, target foe is Dazed and Blinded for 1..10 seconds, and if target foe is casting a spell, that foe is interrupted.
  ~ Dazed and Blind duration :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # causes: Interrupt, Dazed, Blind; requires: lead
Trampling Ox #2135 | Dual Attack | Eye of the North | E5 R8
  Must follow an off-hand attack. If it hits, you deal +5..20 damage. If you a hit a Crippled foe, that foe is knocked down.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Knockdown; requires: offhand
Wild Strike (PvP) #3252 | Off-Hand Attack | Factions | E5 R6
  Must follow a lead attack. If it hits, this attack strikes for +10..35 damage and any stance being used by target foe ends. This attack cannot be blocked.
  ~ + Damage :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  # causes: Unblockable; removes: Stance; requires: lead; unblockable; checks: hit

### Assassin / Deadly Arts
Assassin's Promise #1035 | Elite Hex Spell | Factions | E5 C¾ R45
  For 5..15 seconds, if target foe dies, you gain 5..20 Energy and all your skills are recharged.
  ~ Duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  ~ Energy gain :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Energy Gain, Recharge
Augury of Death #1646 | Hex Spell | Nightfall | E5 C1 R20
  For 5..35 seconds, the next time damage would drop target foe's Health below 50%, you inflict a Deep Wound for 5..20 seconds and Shadow Step to that foe. This spell has half the normal range.
  ~ Duration :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  ~ Deep Wound duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Deep Wound, Shadow Step; range: half
  ! ANOMALY: Similar to Life Siphon and enchantments with upkeep, if a hexed foe moves out of compass range of the caster, Augury of Death will end.
Crippling Dagger #1038 | Spell | Factions | E5 C1 R5
  Send out a Crippling Dagger at target foe. Crippling Dagger strikes for 15..60 earth damage if it hits, and Cripples moving foes for 3..15 seconds. This spell has half the normal range.
  ~ Earth damage :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  ~ Crippled duration :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Crippled, Earth Damage; target: foes; range: half
Dancing Daggers #858 | Spell | Factions | E5 C1 R5
  Send out three Dancing Daggers at target foe, each striking for 5..35 earth damage if they hit. Dancing Daggers has half the normal range. This skill counts as a lead attack.
  ~ Earth damage :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  # causes: Earth Damage; target: foes; range: half
  ! BUG: The daggers will randomly trigger -2 physical damage mods on shields even though they cause earth damage.
Dark Prison #1044 | Hex Spell | Factions | E10 C¼ R30
  Shadow Step to target foe. For 1..6 seconds, that foe moves 33% slower.
  ~ Duration :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  # causes: Shadow Step, Decreased Movement Speed
Deadly Paradox #572 | Stance | Nightfall | E15 R10
  All of your attack skills are disabled for 10 seconds. For 5..15 seconds, your Assassin skills activate and recharge 33% faster.
  ~ Duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Disable, Decreased Activation Time, Decreased Recharge Time
  ! BUG: Similar to Migraine, this skill does not decrease the activation time of dagger attack skills. Recharge time of dagger attack skills are affected as the skill describes.
Disrupting Dagger #571 | Spell | Nightfall | E5 C¼ R10
  Send out a Disrupting Dagger at target foe that strikes for 10..35 earth damage. If that foe was activating a skill, that skill is interrupted. This spell has half the normal range.
  ~ Earth damage :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  # causes: Earth Damage, Interrupt; target: foes; range: half
Enduring Toxin #800 | Hex Spell | Factions | E5 C¼ R10
  For 5 seconds, target foe suffers -1..5 Health degeneration. If that foe is moving when Enduring Toxin would end, Enduring Toxin is renewed for another 5 seconds.
  ~ Health degeneration :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Health Degeneration, Renewal
Entangling Asp #784 | Spell | Factions | E10 C1 R20
  Entangling Asp must follow a lead attack. Target foe is knocked down and becomes Poisoned for 5..20 seconds.
  ~ Poison duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Knockdown, Poison; requires: lead; target: foes
Expose Defenses #802 | Hex Spell | Factions | E5 C1 R25
  For 1..11 second[s], target foe cannot block your attacks.
  ~ Duration :: 0-4: 1 2 2 3 4 | 5-9: 4 5 6 6 7 | 10-14: 8 8 9 10 10 | 15-19: 11 12 12 13 14 | 20-21: 14 15
  # causes: Unblockable
Expunge Enchantments #990 | Touch skill | Factions | E10 C¾ R30
  Skill. Target foe loses 1 enchantment. All of your other non-attack skills are disabled for 8..4 seconds. For each skill disabled in this way, target touched foe loses 1 additional enchantment.
  ~ Disable duration :: 0-4: 8 8 7 7 7 | 5-9: 7 6 6 6 6 | 10-14: 5 5 5 5 4 | 15-19: 4 4 3 3 3 | 20-21: 3 2
  # causes: Disable; removes: Enchantment; target: foes; range: touch
Impale #1033 | Skill | Factions | E5 C1 R15
  Must follow a dual attack. Target foe is struck for 25..100 earth damage and suffers from a Deep Wound for 5..20 seconds.
  ~ Earth damage :: 0-4: 25 30 35 40 45 | 5-9: 50 55 60 65 70 | 10-14: 75 80 85 90 95 | 15-19: 100 105 110 115 120 | 20-21: 125 130
  ~ Deep Wound duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Earth Damage, Deep Wound; requires: dual; target: foes
Iron Palm #786 | Touch Skill | Factions | E5 C¾ R20
  Skill. Target touched foe suffers 5..50 damage, and if that foe is suffering from a hex or condition that foe is knocked down. Iron Palm counts as a lead attack.
  ~ Damage :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Knockdown; target: foes; range: touch
Mantis Touch #974 | Skill | Factions | E5 C¾ R10
  Target foe becomes Crippled for 5..20 seconds. This skill counts as an off-hand attack.
  ~ Crippled duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Crippled; target: foes
  ! ANOMALY: Although the skill name implies that the target has to be touched to be affected, this is not the case. It is a normal skill, which can be activated at casting range.
Mark of Death #785 | Hex Spell | Factions | E10 C¼ R20
  For 4..10 seconds, target foe gains 50% less benefit from healing.
  ~ Duration :: 0-4: 4 4 5 5 6 | 5-9: 6 6 7 7 8 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 12
Mark of Insecurity #570 | Elite Hex Spell | Nightfall | E5 C1 R10
  For 5..25 seconds, target foe suffers from -1..5 Health degeneration, and enchantments and stances on target foe expire 20..60% faster. All of your non-Assassin skills are disabled for 5 seconds.
  ~ Duration :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  ~ Health degeneration :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  ~ Enchantment and stance reduction % :: 0-4: 20 23 25 28 31 | 5-9: 33 36 39 41 44 | 10-14: 47 49 52 55 57 | 15-19: 60 63 65 68 71 | 20-21: 73 76
  # causes: Health Degeneration, Disable; removes: Enchantment, Stance; target: foes; range: Casting
Sadist's Signet #1991 | Signet | Eye of the North | C1 R8
  You gain 10..45 Health for each condition on target foe.
  ~ Health gain :: 0-4: 10 12 15 17 19 | 5-9: 22 24 26 29 31 | 10-14: 33 36 38 40 43 | 15-19: 45 47 50 52 54 | 20-21: 57 59
  # causes: Health Gain; target: foes
Scorpion Wire #815 | Hex Spell | Factions | E5 C1 R10
  For 8..20 seconds, the next time you and target foe are more than 75' apart, you Shadow Step to that foe and that foe is knocked down. This spell has half the normal range.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  # causes: Shadow Step, Knockdown; range: half
Shadow Fang #2052 | Hex Spell | Eye of the North | E10 C¼ R20
  Shadow Step to target foe. For 10 seconds, this hex does nothing. When this hex ends, you return to your original location and that foe suffers from a Deep Wound for 5..20 seconds.
  ~ Deep Wound duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Shadow Step, Deep Wound
Shadow Prison #1652 | Elite Hex Spell | Nightfall | E5 C¼ R15
  Shadow Step to target foe. For 1..7 seconds, that foe moves 66% slower.
  ~ Duration :: 0-4: 1 1 2 2 3 | 5-9: 3 3 4 4 5 | 10-14: 5 5 6 6 7 | 15-19: 7 7 8 8 9 | 20-21: 9 9
  # causes: Shadow Step, Decreased Movement Speed
Shameful Fear #927 | Hex Spell | Factions | E10 C1 R10
  For 10 seconds, target foe moves 10% faster than normal. For each second, if that foe is moving, that foe takes 5..20 damage.
  ~ Damage while moving :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Increased Movement Speed
Shroud of Silence #801 | Elite Touch Hex Spell | Factions | E10 C¾ R30
  Elite Hex Spell. All of your spells are disabled for 15 seconds. For 1..6 second[s], target touched foe cannot cast spells.
  ~ Duration :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  # causes: Disable; range: touch
Signet of Deadly Corruption (PvP) #3053 | Signet | Eye of the North | C1 R12
  Must follow a dual attack. Target foe takes 5..35 damage for each condition on that foe (maximum 130 damage).
  ~ Armor-ignoring damage per condition :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  # requires: dual; target: foes
Signet of Shadows #876 | Signet | Factions | C1 R15
  Target foe takes 5..35 damage. If your target was Blinded, that foe suffers an additional 15..60 damage.
  ~ Damage :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  ~ Additional damage :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  # target: foes
Signet of Toxic Shock #1647 | Signet | Nightfall | C1 R15
  If target foe is suffering from Poison, that foe takes 10..100 damage.
  ~ Damage :: 0-4: 10 16 22 28 34 | 5-9: 40 46 52 58 64 | 10-14: 70 76 82 88 94 | 15-19: 100 106 112 118 124 | 20-21: 130 136
Siphon Speed #951 | Hex Spell | Factions | E5 C1 R30
  For 5..15 seconds, target foe moves 33% slower and you move 33% faster. This spell recharges 50% faster if cast on a moving foe.
  ~ Duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Decreased Movement Speed, Increased Movement Speed, Decreased Recharge Time
Siphon Strength #827 | Elite Hex Spell | Factions | E10 C1 R10
  For 5..20 seconds, target foe deals 5..50 less damage with attacks and all of your attacks against that foe have an additional 50% chance of being a critical hit.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Damage reduction :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Damage Reduction, Critical Hit; target: foes; range: Casting
Vampiric Assault #1986 | Dual Attack | Eye of the North | E5 R8
  Must follow an off-hand attack. If this attack hits, you steal 10..40 Health.
  ~ Life stealing :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Life Stealing; requires: offhand; checks: hit
Way of the Empty Palm #987 | Elite Enchantment Spell | Factions | E5 C¼ R10
  For 5..15 seconds, off-hand and dual attacks cost no Energy and recharge 25..50% faster.
  ~ Duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  ~ % Faster Recharge :: 0-4: 25 27 28 30 32 | 5-9: 33 35 37 38 40 | 10-14: 42 43 45 47 48 | 15-19: 50 52 53 55 57 | 20-21: 58 60
  # causes: Decreased Energy Cost; requires: Off-hand, Dual attacks

### Assassin / No Attribute
Assault Enchantments #1643 | Elite Skill | Nightfall | E5 C¼ R8
  Must follow a dual attack. Target foe loses all enchantments.
  # removes: Enchantment; requires: dual; target: foes
Aura of Displacement #771 | Elite Enchantment Spell | Factions | E5 U-1 C¼ R20
  When you cast Aura of Displacement, Shadow Step to target foe. When you stop maintaining Aura of Displacement you return to your original location.
  # causes: Shadow Step; target: foes
  ! ANOMALY: Similar to other enchantments that target a foe, foes affected by Well of the Profane or spirits cannot be targeted by this enchantment.
Lift Enchantment #1645 | Touch Skill | Nightfall | E5 C¼ R10
  If target touched foe is knocked down, that foe loses one enchantment.
  # removes: Enchantment; target: foes; range: touch
Mark of Instability #978 | Hex Spell | Factions | E10 C¼ R20
  For 20 seconds, the next time you hit target foe with a dual attack skill that foe is knocked down.
  # causes: Knockdown; target: foes; range: Casting
Recall #925 | Enchantment Spell | Factions | E10 U-1 C1 R10
  While you maintain Recall, nothing happens. When Recall ends, you Shadow Step to the ally you targeted when you activated this skill and all of your skills are disabled for 3 seconds.
  # causes: Shadow Step, Disable; target: other allies
  ! ANOMALY: The full description does not state that this skill cannot self-target.
Shadow Meld #1654 | Elite Enchantment Spell | Nightfall | E5 U-1 C¼ R10
  Shadow Step to target other ally. When you stop maintaining this Enchantment, you return to your original location.
  # causes: Shadow Step; target: other allies
  ! ANOMALY: This spell does not have an aftercast delay.
Shadow Walk #1650 | Stance | Nightfall | E5 R30
  Shadow Step to target foe. For 15 seconds nothing happens. Your attack skills are disabled for 1 second, and your stances and enchantments are disabled for 10 seconds. When this stance ends, you return to your original location.
  # causes: Shadow Step, Disable; target: foes
Signet of Malice #1036 | Signet | Factions | C¼ R5
  For each condition suffered by target foe, you lose one condition.
  # removes: Condition; target: foes
Signet of Twilight #1648 | Signet | Nightfall | C1 R20
  For each hex on target foe, that foe loses one enchantment.
  # removes: Enchantment; target: foes
Spirit Walk #1040 | Spell | Factions | E5 C¼ R8
  Shadow Step to target spirit.
  # causes: Shadow Step; target: spirits
  ! ANOMALY: This spell does not have an aftercast delay.
Swap #1653 | Spell | Nightfall | E5 C¼ R10
  You and target summoned creature Shadow Step to each other's location.
  # causes: Shadow Step; target: summoned creatures
  ! ANOMALY: This spell does not have an aftercast delay.
Wastrel's Collapse #1644 | Elite Skill | Nightfall | E5 C¼ R20
  Shadow Step to target foe. If target foe is not using a skill, that foe is knocked down. All of your non-dagger attack skills are disabled for 10 seconds.
  # causes: Shadow Step, Knockdown, Disable; target: foes

### Assassin / Shadow Arts
Beguiling Haze #799 | Elite Spell | Factions | E10 C¼ R20
  Shadow Step to target foe. That foe becomes Dazed for 3..9 seconds.
  ~ Dazed duration :: 0-4: 3 3 4 4 5 | 5-9: 5 5 6 6 7 | 10-14: 7 7 8 8 9 | 15-19: 9 9 10 10 11 | 20-21: 11 11
  # causes: Shadow Step, Dazed; target: foes
Blinding Powder #973 | Spell | Factions | E5 C¼ R20
  Must follow an off-hand attack. Target foe and all adjacent foes become Blinded for 3..15 seconds.
  ~ Blind duration :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Blind; requires: offhand; target: foes; aoe: adjacent
Caltrops #985 | Spell | Factions | E5 C¼ R10
  Target foe and all foes adjacent to your target are Crippled and Bleeding for 5..15 seconds. Caltrops has half the normal range.
  ~ Crippled duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Crippled; target: foes; range: half; aoe: adjacent
Dark Escape #1037 | Stance | Factions | E5 R30
  For 5..15 seconds, you move 25% faster and take half damage. Dark Escape ends if you successfully hit with an attack.
  ~ Duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Increased Movement Speed, Damage Reduction
Dash (PvP) #3453 | Stance | Factions | E5 R12
  For 3 seconds, you run 50% faster. Every 2 points in Shadow Arts lowers recharge by 1 second (max 6 seconds).
  # causes: Increased Movement Speed
Death's Charge #952 | Spell | Factions | E5 C¼ R30
  Shadow Step to target foe. If that foe has more Health than you, you are healed for 65..200.
  ~ Healing :: 0-4: 65 74 83 92 101 | 5-9: 110 119 128 137 146 | 10-14: 155 164 173 182 191 | 15-19: 200 209 218 227 236 | 20-21: 245 254
  # causes: Shadow Step, Healing; target: foes
Death's Retreat #1651 | Spell | Nightfall | E5 C¼ R20
  Shadow Step to target ally. If you have less Health than that ally, you gain 40..130 Health.
  ~ Health gain :: 0-4: 40 46 52 58 64 | 5-9: 70 76 82 88 94 | 10-14: 100 106 112 118 124 | 15-19: 130 136 142 148 154 | 20-21: 160 166
  # causes: Shadow Step, Health Gain; target: other allies
  ! ANOMALY: Death's Retreat is one of the few spells that do not suffer from aftercast delay.
Feigned Neutrality #1641 | Enchantment Spell | Nightfall | E5 C¼ R25
  For 4..10 seconds, you have +7 Health regeneration and +80 armor. This enchantment ends if you successfully hit with an attack or use a skill.
  ~ Duration :: 0-4: 4 4 5 5 6 | 5-9: 6 6 7 7 8 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 12
  # causes: Health Regeneration, Increased Armor Rating
Heart of Shadow #1032 | Spell | Factions | E5 C¼ R15
  You are healed for 30..150. Shadow Step to a nearby location directly away from your target.
  ~ Healing :: 0-4: 30 38 46 54 62 | 5-9: 70 78 86 94 102 | 10-14: 110 118 126 134 142 | 15-19: 150 158 166 174 182 | 20-21: 190 198
  # causes: Healing, Shadow Step; target: allies or foes; range: Casting
  ! ANOMALY: This spell does not have an aftercast delay.
Hidden Caltrops #1642 | Elite Hex Spell | Nightfall | E5 C1 R12
  Your non-Assassin skills are disabled for 3 seconds. For 1..10 seconds, target foe moves 50% slower. When this hex ends that foe is Crippled for 1..15 seconds.
  ~ Duration :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Crippled duration :: 0-4: 1 2 3 4 5 | 5-9: 6 7 8 8 9 | 10-14: 10 11 12 13 14 | 15-19: 15 16 17 18 19 | 20-21: 20 21
  # causes: Decreased Movement Speed, Crippled, Disable
  ! BUG: Crippling modifiers on weapons do not extend the duration of cripple caused by the end effect.
Mirrored Stance #816 | Hex Spell | Factions | E5 C¼ R15
  For 10..35 seconds, whenever target foe enters a stance, you enter the same stance.
  ~ Duration :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  ! ANOMALY: If the copied stance has an initial effect, the initial effect will not affect you. I.e. Bestial Fury/Tiger's Fury, Deadly Paradox, and Shadow Walk will not disable your skills; Shadow Walk will also not cause you to shadow step to a foe.
Return #770 | Spell | Factions | E5 C¼ R15
  All adjacent foes are Crippled for 3..8 seconds. Shadow Step to target other ally's location.
  ~ Crippled duration :: 0-4: 3 3 4 4 4 | 5-9: 5 5 5 6 6 | 10-14: 6 7 7 7 8 | 15-19: 8 8 9 9 9 | 20-21: 10 10
  # causes: Crippled, Shadow Step; target: other allies; aoe: adjacent
  ! ANOMALY: This spell does not have an aftercast delay.
Shadow Form (PvP) #2862 | Elite Enchantment Spell | Factions | E10 C1 R60
  For 5..15 seconds, all hostile spells that target you fail and all attacks against you miss. When Shadow Form ends, lose all but 5..50 Health.
  ~ Duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  ~ Health at end :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Miss, Health Loss
  ! BUG: The -5 damage reduction is active for the expected duration of each enchantment, not its actual duration. Refreshing an Assassin enchantment before it ends reduces the received damage by an additional -5. [from PvE version page]
Shadow of Haste #929 | Stance | Factions | E5 R45
  For 10..40 seconds you move 15% faster than normal. When Shadow of Haste ends, you shadow step to your original location.
  ~ Duration :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Increased Movement Speed, Shadow Step
Shadow Refuge #814 | Enchantment Spell | Factions | E5 C1 R8
  For 6 seconds, you gain 5..10 Health regeneration. When Shadow Refuge ends, you gain 40..100 Health if you are attacking.
  ~ Health regeneration :: 0-4: 5 5 6 6 6 | 5-9: 7 7 7 8 8 | 10-14: 8 9 9 9 10 | 15-19: 10 10 11 11 11 | 20-21: 12 12
  ~ Healing :: 0-4: 40 44 48 52 56 | 5-9: 60 64 68 72 76 | 10-14: 80 84 88 92 96 | 15-19: 100 104 108 112 116 | 20-21: 120 124
  # causes: Health Regeneration, Healing
  ! BUG: Contrary to the full description, this skill causes healing and not health gain.
Shadow Shroud (PvP) #3452 | Elite Hex Spell | Factions | E5 C¼ R20
  For 2..7 seconds, target foe cannot be the target of enchantments.
  ~ Duration :: 0-4: 2 2 3 3 3 | 5-9: 4 4 4 5 5 | 10-14: 5 6 6 6 7 | 15-19: 7 7 8 8 8 | 20-21: 9 9
Shadowy Burden #950 | Hex Spell | Factions | E10 C¼ R15
  For 3..15 seconds, target foe moves 25% slower and while target foe has no other hexes, that foe has 20..30 less armor against your attacks.
  ~ Duration :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  ~ Armor reduction :: 0-4: 20 21 21 22 23 | 5-9: 23 24 25 25 26 | 10-14: 27 27 28 29 29 | 15-19: 30 31 31 32 33 | 20-21: 33 34
  # causes: Decreased Movement Speed, Decreased Armor Rating
  ! ANOMALY: The armor penalty from this skill is applied after the armor cap and the effects of Cracked Armor and Armor Penetration.
Shroud of Distress (PvP) #3048 | Enchantment Spell | Factions | E10 C1 R45
  For 30..60 seconds, if you are below 50% Health, you have a 75% chance to block attacks.
  ~ Duration :: 0-4: 30 32 34 36 38 | 5-9: 40 42 44 46 48 | 10-14: 50 52 54 56 58 | 15-19: 60 62 64 66 68 | 20-21: 70 72
  # causes: Block; target: self
  ! BUG: When having less than 50% health, the block chance applies immediately while the health regeneration is delayed. Using any skill or swapping from a vampiric weapon to a non-vampiric one will provide you the proper health regeneration immediately. [from PvE version page]
Smoke Powder Defense #2136 | Stance | Eye of the North | E5 R20
  For 8 seconds, the next time you are struck, you take half damage and all adjacent foes are Blinded for 2..6 seconds.
  ~ Blind duration :: 0-4: 2 2 3 3 3 | 5-9: 3 4 4 4 4 | 10-14: 5 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 7 8
  # causes: Damage Reduction, Blind; target: untargeted; aoe: adjacent
Unseen Fury (PvP) #3049 | Stance | Factions | E5 R45
  For 15..60 seconds, you cannot be blocked by Blinded foes.
  ~ Duration :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  # causes: Unblockable
Viper's Defense #769 | Spell | Factions | E5 C¼ R10
  All adjacent foes are Poisoned for 5..20 seconds. Shadow Step to a nearby location directly away from your target.
  ~ Poison duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Poison, Shadow Step; target: allies or foes; aoe: adjacent
  ! ANOMALY: This spell does not have an aftercast delay.
Way of Perfection #1028 | Enchantment Spell | Factions | E5 C¼ R30
  For 60 seconds, whenever you successfully land a critical hit, you gain 10..40 Health.
  ~ Health gain :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Health Gain
  ! BUG: Contrary to the concise description, this skill's conditional effect causes health gain and not healing.
Way of the Fox #949 | Enchantment Spell | Factions | E5 C¼ R30
  For 10..35 seconds, your next 1..6 attack[s] cannot be blocked.
  ~ Duration :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  ~ Subsequent attacks :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  # causes: Unblockable
Way of the Lotus #977 | Enchantment Spell | Factions | E5 C¼ R20
  For 20 seconds, the next time you hit with a dual attack skill, you gain 5..20 Energy.
  ~ Energy gain :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Energy Gain

## Ritualist

### Ritualist / Channeling Magic
Agony (PvP) #3038 | Binding Ritual | Eye of the North | E10 C3 R30
  Create a level 1..8 spirit. This spirit causes 3..10 Health loss each second to foes within earshot. This spirit loses 3..10 Health for each foe hurt in this way. This spirit dies after 30..90 seconds.
  ~ Spirit level :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  ~ Health loss to foes per second :: 0-4: 3 3 4 4 5 | 5-9: 5 6 6 7 7 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 13
  ~ Health loss per foe affected :: 0-4: 3 3 4 4 5 | 5-9: 5 6 6 7 7 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 13
  ~ Spirit duration :: 0-4: 30 34 38 42 46 | 5-9: 50 54 58 62 66 | 10-14: 70 74 78 82 86 | 15-19: 90 94 98 102 106 | 20-21: 110 114
  # causes: Spirit, Health Loss; aoe: earshot
  ! ANOMALY: This spirit causes health loss to passive charmable animals; however, this does not turn them hostile. [from PvE version page]
Ancestors' Rage (PvP) #2867 | Skill | Factions | E5 C1 R8
  For 3 seconds all foes adjacent to target ally are struck for 4..50 lightning damage each second.
  ~ Lightning damage :: 0-4: 4 7 10 13 16 | 5-9: 19 22 25 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Lightning Damage; target: allies; aoe: adjacent
Bloodsong (PvP) #3019 | Binding Ritual | Factions | E5 C1½ R30
  Create a level 1..8 spirit who dies after 30..150 seconds. Attacks by that spirit steal up to 5..25 Health.
  ~ Level :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  ~ Duration :: 0-4: 30 38 46 54 62 | 5-9: 70 78 86 94 102 | 10-14: 110 118 126 134 142 | 15-19: 150 158 166 174 182 | 20-21: 190 198
  ~ Life stealing :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  # causes: Spirit, Life Stealing; target: untargeted; aoe: none
Caretaker's Charge #1744 | Elite Spell | Nightfall | E5 C1 R4
  Target foe is struck for 20..85 lightning damage. If you are holding an item, you gain 7 Energy and 5..50 Health.
  ~ Lightning damage :: 0-4: 20 24 29 33 37 | 5-9: 42 46 50 55 59 | 10-14: 63 68 72 76 81 | 15-19: 85 89 94 98 102 | 20-21: 107 111
  ~ Health gain :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Lightning Damage, Energy Gain, Health Gain; target: foes
Channeled Strike #1225 | Spell | Factions | E10 C2 R4
  Target foe is struck for 5..95 lightning damage. That foe is struck for an additional 5..35 lightning damage if you are holding an item.
  ~ Lightning damage :: 0-4: 5 11 17 23 29 | 5-9: 35 41 47 53 59 | 10-14: 65 71 77 83 89 | 15-19: 95 101 107 113 119 | 20-21: 125 131
  ~ Additional damage :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  ~ Total damage :: 0-4: 10 18 26 34 42 | 5-9: 50 58 66 74 82 | 10-14: 90 98 106 114 122 | 15-19: 130 138 146 154 162 | 20-21: 170 178
  # causes: Lightning Damage; target: foes
Clamor of Souls #1215 | Elite Spell | Factions | E10 C1 R8
  Target foe and all nearby foes take 10..65 lightning damage. If you are within earshot of a spirit or holding a bundle item, you gain 10 Energy.
  ~ Lightning damage :: 0-4: 10 14 17 21 25 | 5-9: 28 32 36 39 43 | 10-14: 47 50 54 58 61 | 15-19: 65 69 72 76 80 | 20-21: 83 87
  # causes: Lightning Damage, Energy Gain; target: foes; aoe: nearby
Cruel Was Daoshen #1218 | Item Spell | Factions | E15 C2 R30
  Hold Daoshen's ashes for up to 15..60 seconds. While you hold his ashes, all Ritualist skills have 10% armor penetration. When you drop his ashes, all nearby foes are struck for 15..85 lightning damage.
  ~ Duration :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  ~ Lightning damage :: 0-4: 15 20 24 29 34 | 5-9: 38 43 48 52 57 | 10-14: 62 66 71 76 80 | 15-19: 85 90 94 99 104 | 20-21: 108 113
  # causes: Armor Penetration, Lightning Damage; target: untargeted; aoe: nearby
Destruction (PvP) #3008 | Binding Ritual | Factions | E10 C3 R20
  Create a level 1..10 Spirit that dies after 30 seconds. When this Spirit dies, all foes in the area take 1..10 damage for each second the Spirit was alive (maximum of 150 damage).
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Lightning damage :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # causes: Spirit, Lightning Damage; aoe: in the area
  ! BUG: This spirit deals no damage if the caster (or his corpse) is not in compass range.
  ! BUG: This spirit deals no damage if the caster (or their corpse) is not in compass range. [from PvE version page]
  ! BUG: The damage dealt is armor-ignoring lightning damage. [from PvE version page]
  ! ANOMALY: The non-concise and concise descriptions are identical. [from PvE version page]
Destructive Was Glaive (PvP) #3157 | Elite Item Spell | Nightfall | E10 C1 R10
  Hold Glaive's ashes for up to 30..60 seconds. While you hold her ashes, all Ritualist skills have 10% armor penetration. When you drop her ashes, all foes in the area are struck for 15..85 lightning damage.
  ~ Duration :: 0-4: 30 32 34 36 38 | 5-9: 40 42 44 46 48 | 10-14: 50 52 54 56 58 | 15-19: 60 62 64 66 68 | 20-21: 70 72
  ~ Lightning damage :: 0-4: 15 20 24 29 34 | 5-9: 38 43 48 52 57 | 10-14: 62 66 71 76 80 | 15-19: 85 90 94 99 104 | 20-21: 108 113
  # causes: Armor Penetration, Lightning Damage; aoe: in the area
  ! ANOMALY: When dropped, the chat log notes your dropping the ashes as "You drop a Destructive was Glaive." When most ashes from an item spell are dropped, the chat log notes this as "You drop an Ashes of..." followed by the name of the item spell. Example: "You drop an Ashes of Grasping Kuurong." [from PvE version page]
Essence Strike #1227 | Spell | Factions | E5 C1 R8
  Target foe is struck for 15..60 lightning damage. If any spirits are within earshot, you gain 1..9 Energy.
  ~ Lightning damage :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  ~ Energy gain :: 0-4: 1 2 2 3 3 | 5-9: 4 4 5 5 6 | 10-14: 6 7 7 8 8 | 15-19: 9 10 10 11 11 | 20-21: 12 12
  # causes: Lightning Damage, Energy Gain; target: foes
Gaze from Beyond #1245 | Spell | Factions | E5 C1 R10
  Target foe is struck for 20..65 lightning damage. If you are within earshot of a spirit, that foe is Blinded for 2..6 seconds.
  ~ Damage :: 0-4: 20 23 26 29 32 | 5-9: 35 38 41 44 47 | 10-14: 50 53 56 59 62 | 15-19: 65 68 71 74 77 | 20-21: 80 83
  ~ Blind duration :: 0-4: 2 2 3 3 3 | 5-9: 3 4 4 4 4 | 10-14: 5 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 7 8
  # causes: Lightning Damage, Blind; target: foes
Gaze of Fury (PvP) #3022 | Binding Ritual | Nightfall | E10 C2 R20
  Destroy target allied spirit and create a level 1..10 Spirit of Fury. This spirit's attacks deal 5..20 damage. This spirit dies after 30..60 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Duration :: 0-4: 30 32 34 36 38 | 5-9: 40 42 44 46 48 | 10-14: 50 52 54 56 58 | 15-19: 60 62 64 66 68 | 20-21: 70 72
  # causes: Spirit; removes: Spirit; target: spirits; range: Casting; aoe: none
  ! ANOMALY: Can be used on any target, not just allied spirits; can also be cast without a target. If the target is not an allied spirit, it will destroy the allied spirit closest to the target. If cast without a target, it will destroy the allied spirit closest to the caster.
  ! ANOMALY: Can be used on any target, not just spirits; can also be cast without a target. If the target is not an enemy spirit, it will destroy the spirit closest to the target. If cast without a target, it will destroy the spirit closest to the caster. [from PvE version page]
  ! ANOMALY: Using this skill while targeting an ally (including spirits) will stop automatic health regeneration. [from PvE version page]
  ! BUG: If multiple spirits occupy exactly the same spot, using Gaze of Fury on one of them may destroy one of the others instead. [from PvE version page]
Grasping Was Kuurong #789 | Elite Item Spell | Factions | E15 R25
  Hold Kuurong's ashes for up to 15..60 seconds. When you drop his ashes, all foes in the area are struck for 15..75 damage and knocked down.
  ~ Duration :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  ~ Armor-ignoring damage :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  # causes: Knockdown; target: untargeted; aoe: nearby
Lamentation #916 | Hex spell | Factions | E10 C1 R15
  For 5..20 seconds, target foe and all nearby foes suffer -0..3 Health degeneration. When this hex is applied, these foes take 10..50 damage if you are within earshot of a spirit or corpse.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Health degeneration :: 0-4: 0 0 0 1 1 | 5-9: 1 1 1 2 2 | 10-14: 2 2 2 3 3 | 15-19: 3 3 3 4 4 | 20-21: 4 4
  ~ Armor-ignoring damage :: 0-4: 10 13 15 18 21 | 5-9: 23 26 29 31 34 | 10-14: 37 39 42 45 47 | 15-19: 50 53 55 58 61 | 20-21: 63 66
  # causes: Health Degeneration; range: Casting; aoe: nearby
Nightmare Weapon #795 | Weapon Spell | Factions | E5 C1 R10
  For 12 seconds, target ally has a Nightmare Weapon. Target ally's next 3 attacks are reduced by 10..50 damage and steal up to 10..50 Health.
  ~ Damage reduction :: 0-4: 10 13 15 18 21 | 5-9: 23 26 29 31 34 | 10-14: 37 39 42 45 47 | 15-19: 50 53 55 58 61 | 20-21: 63 66
  ~ Life stealing :: 0-4: 10 13 15 18 21 | 5-9: 23 26 29 31 34 | 10-14: 37 39 42 45 47 | 15-19: 50 53 55 58 61 | 20-21: 63 66
  # causes: Life Stealing; target: allies
Offering of Spirit #1479 | Elite Spell | Nightfall | E3 S17% C¼ R15
  Gain 8..17 Energy. If any spirits are within earshot, you do not sacrifice Health.
  ~ Energy gain :: 0-4: 8 9 9 10 10 | 5-9: 11 12 12 13 13 | 10-14: 14 15 15 16 16 | 15-19: 17 18 18 19 19 | 20-21: 20 21
  # causes: Energy Gain; target: self
Painful Bond #1237 | Hex Spell | Factions | E15 C1 R12
  For 10..20 seconds, target foe and all nearby foes are hexed with Painful Bond and take 8..20 damage whenever hit by a spirit's attack.
  ~ Duration :: 0-4: 10 11 11 12 13 | 5-9: 13 14 15 15 16 | 10-14: 17 17 18 19 19 | 15-19: 20 21 21 22 23 | 20-21: 23 24
  ~ Damage :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  # aoe: nearby
  ! BUG: The concise description incorrectly states that spirits do more damage; it is the hex causing the damage and spirits that do not deal damage with its attacks (i.e. Bloodsong, Vampirism, and Wanderlust) do not technically deal more damage. Spirits that deal damage without attacking (e.g. Destruction) don't get their damage increased by Painful Bond.
Renewing Surge #1478 | Hex Spell | Nightfall | E5 C1 R15
  For 8 seconds, target foe suffers 2..12 damage each second. When this hex ends, you gain 1..8 Energy.
  ~ Damage per second :: 0-4: 2 3 3 4 5 | 5-9: 5 6 7 7 8 | 10-14: 9 9 10 11 11 | 15-19: 12 13 13 14 15 | 20-21: 15 16
  ~ Energy gain :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  # causes: Energy Gain
  ! ANOMALY: Unlike other hexes that affect the caster, this hex does not end if the caster dies.
Signet of Spirits (PvP) #2965 | Elite Signet | Factions | C1 R20
  You gain 3..12 Energy if you are within earshot of a spirit.
  ~ Energy gain :: 0-4: 3 4 4 5 5 | 5-9: 6 7 7 8 8 | 10-14: 9 10 10 11 11 | 15-19: 12 13 13 14 14 | 20-21: 15 16
  # causes: Energy Gain; target: self
Spirit Boon Strike #1226 | Spell | Factions | E5 C1 R3
  Target foe is struck for 20..65 lightning damage, and all spirits you control within earshot gain 20..65 Health.
  ~ Lightning damage :: 0-4: 20 23 26 29 32 | 5-9: 35 38 41 44 47 | 10-14: 50 53 56 59 62 | 15-19: 65 68 71 74 77 | 20-21: 80 83
  ~ Health gain :: 0-4: 20 23 26 29 32 | 5-9: 35 38 41 44 47 | 10-14: 50 53 56 59 62 | 15-19: 65 68 71 74 77 | 20-21: 80 83
  # causes: Lightning Damage, Health Gain; target: foes; aoe: earshot
Spirit Burn #919 | Spell | Factions | E5 C1 R6
  Target foe is struck for 5..50 lightning damage. If any spirits are within earshot, Spirit Burn causes Burning for 1..5 second[s].
  ~ Lightning damage :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  ~ Burning duration :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Lightning Damage, Burning; target: foes
Spirit Rift #910 | Spell | Factions | E10 C2 R5
  Open a Spirit Rift at target foe's location. After 3 seconds, all adjacent foes are struck for 25..125 lightning damage and suffer from Cracked Armor for 1..20 second[s].
  ~ Lightning damage :: 0-4: 25 32 38 45 52 | 5-9: 58 65 72 78 85 | 10-14: 92 98 105 112 118 | 15-19: 125 132 138 145 152 | 20-21: 158 165
  ~ Cracked Armor duration :: 0-4: 1 2 4 5 6 | 5-9: 7 9 10 11 12 | 10-14: 14 15 16 17 19 | 15-19: 20 21 23 24 25 | 20-21: 26 28
  # causes: Lightning Damage, Cracked Armor; target: foes; range: Casting; aoe: adjacent
Spirit Siphon #1228 | Spell | Factions | E5 C¼ R3
  The spirit nearest you loses all Energy. You gain 30..60% of that Energy.
  ~ % Energy :: 0-4: 30 32 34 36 38 | 5-9: 40 42 44 46 48 | 10-14: 50 52 54 56 58 | 15-19: 60 62 64 66 68 | 20-21: 70 72
  ~ Energy gain1 :: 0-4: 9 10 10 11 11 | 5-9: 12 13 13 14 14 | 10-14: 15 16 16 17 17 | 15-19: 18 19 19 20 20 | 20-21: 21 22
  # causes: Energy Loss, Energy Gain; target: self
Splinter Weapon (PvP) #2868 | Weapon Spell | Factions | E5 C1 R8
  For 20 seconds, target ally has a Splinter Weapon. Target ally's next 1..5 attack[s] deal 5..40 damage to up to 4 adjacent foes.
  ~ Attacks :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  ~ Damage :: 0-4: 5 7 10 12 14 | 5-9: 17 19 21 24 26 | 10-14: 28 31 33 35 38 | 15-19: 40 42 45 47 49 | 20-21: 52 54
  # causes: Physical Damage; target: allies; aoe: adjacent
Wailing Weapon #794 | Weapon Spell | Factions | E5 C1 R15
  For 3..14 seconds, target ally has a Wailing Weapon. Whenever the Wailing Weapon strikes an attacking foe, that foe is interrupted.
  ~ Duration :: 0-4: 3 4 4 5 6 | 5-9: 7 7 8 9 10 | 10-14: 10 11 12 13 13 | 15-19: 14 15 15 16 17 | 20-21: 18 18
  # causes: Interrupt; target: allies
Warmonger's Weapon #1751 | Weapon Spell | Nightfall | E10 C1 R30
  For 3..13 seconds, if target ally attacks a foe who is not attacking, that foe is interrupted.
  ~ Duration :: 0-4: 3 4 4 5 6 | 5-9: 6 7 8 8 9 | 10-14: 10 10 11 12 12 | 15-19: 13 14 14 15 16 | 20-21: 16 17
  # causes: Interrupt; target: allies
Weapon of Aggression #2073 | Weapon Spell | Eye of the North | E10 C¼ R10
  For 5..15 seconds, you attack 25% faster.
  ~ Duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Increased Attack Speed; target: self
Weapon of Fury #1749 | Elite Weapon Spell | Nightfall | E5 C1 R8
  For 5..20 seconds, target ally gains 100% more adrenaline and 1 Energy whenever that ally successfully hits with an attack.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Increased Adrenaline Build Rate, Energy Gain; target: allies
Wielder's Strike #1733 | Spell | Nightfall | E5 C1 R6
  Target foe is struck for 10..60 lightning damage. If you are under the effects of a weapon spell, you deal an additional 10..50 lightning damage.
  ~ Lightning damage :: 0-4: 10 13 17 20 23 | 5-9: 27 30 33 37 40 | 10-14: 43 47 50 53 57 | 15-19: 60 63 67 70 73 | 20-21: 77 80
  ~ Additional damage :: 0-4: 10 13 15 18 21 | 5-9: 23 26 29 31 34 | 10-14: 37 39 42 45 47 | 15-19: 50 53 55 58 61 | 20-21: 63 66
  ~ Total damage :: 0-4: 20 26 32 38 44 | 5-9: 50 56 62 68 74 | 10-14: 80 86 92 98 104 | 15-19: 110 116 122 128 134 | 20-21: 140 146
  # causes: Lightning Damage; target: foes

### Ritualist / Communing
Anguish (PvP) #3023 | Binding Ritual | Nightfall | E25 C1½ R30
  Create a level 1..7 spirit. This spirit's attacks deal 5..20 damage and deal double damage to hexed foes. This spirit dies after 15..45 seconds.
  ~ Level :: 0-4: 1 1 2 2 3 | 5-9: 3 3 4 4 5 | 10-14: 5 5 6 6 7 | 15-19: 7 7 8 8 9 | 20-21: 9 9
  ~ Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Duration :: 0-4: 15 17 19 21 23 | 5-9: 25 27 29 31 33 | 10-14: 35 37 39 41 43 | 15-19: 45 47 49 51 53 | 20-21: 55 57
  # causes: Spirit; target: untargeted; aoe: none
Armor of Unfeeling (PvP) #3003 | Enchantment Spell | Factions | E10 C1 R20
  For 10..35 seconds, you have 10 base damage reduction while casting Binding Rituals.
  ~ Duration :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  # causes: Damage Reduction
  ! ANOMALY: This skill reduces the health loss of Shelter and Earthbind, but not that of Wanderlust or Agony. [from PvE version page]
Binding Chains #1236 | Hex Spell | Factions | E10 C1 R15
  For 3 seconds, target foe and all nearby foes move 90% slower and take 1..30 damage each second while moving.
  ~ Damage while moving :: 0-4: 1 3 5 7 9 | 5-9: 11 13 15 16 18 | 10-14: 20 22 24 26 28 | 15-19: 30 32 34 36 38 | 20-21: 40 42
  # causes: Decreased Movement Speed; aoe: nearby
Brutal Weapon #1258 | Weapon Spell | Factions | E10 C1 R15
  Give target ally a Brutal Weapon for 10..40 seconds. The bearer's weapon strikes for +5..15 damage as long as the bearer is under no enchantments.
  ~ Duration :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  ~ + Damage :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # target: allies
Disenchantment (PvP) #3017 | Binding Ritual | Factions | E25 C3 R30
  Create a level 1..8 spirit. This spirit deals 5..20 damage and anyone struck by its attack loses one enchantment. This spirit dies after 15..40 seconds.
  ~ Level :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  ~ Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Duration :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  ~ (15..40) [derived] :: 0-4: 15 17 18 20 22 | 5-9: 23 25 27 28 30 | 10-14: 32 33 35 37 38 | 15-19: 40 42 43 45 47 | 20-21: 48 50
  # causes: Spirit; removes: Enchantment; target: untargeted; aoe: none
Displacement (PvP) #3010 | Binding Ritual | Factions | E15 C3 R45
  Create a level 1..10 spirit. All non-spirit allies within its range have a 75% chance to block incoming attacks. Every time an attack is blocked in this way, this spirit takes 60 damage. This spirit dies after 30..60 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Duration :: 0-4: 30 32 34 36 38 | 5-9: 40 42 44 46 48 | 10-14: 50 52 54 56 58 | 15-19: 60 62 64 66 68 | 20-21: 70 72
  ~ Blocks X hits :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  ~ Max effective blocks :: 0-4: 4 4 4 4 5 | 5-9: 5 5 5 5 5 | 10-14: 5 5 6 6 6 | 15-19: 6 6 6 6 7 | 20-21: 7 7
  # causes: Spirit, Block; aoe: spirit
  ! ANOMALY: There is a delay of 2-3 seconds from the spirit's creation to its effect being applied, unlike other skills.
  ! BUG: The duration bar beneath the effects monitor skill icon does not shrink over time like other effects with durations.
  ! ANOMALY: There is a delay of 2-3 seconds from the spirit's creation to its effect being applied, unlike other skills. [from PvE version page]
  ! BUG: The spirit will take damage even for attacks blocked by another blocking source. [from PvE version page]
  ! BUG: The duration bar beneath the effects monitor skill icon does not shrink over time like other effects with durations. [from PvE version page]
Dissonance (PvP) #3014 | Binding Ritual | Factions | E25 C2 R30
  Create a level 1..8 spirit. This spirit deals 5..20 damage and anyone struck by its attack is interrupted. This spirit dies after 10..25 seconds.
  ~ Level :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  ~ Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Duration :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  # causes: Spirit, Interrupt; aoe: none
  ! BUG: This spirit will interrupt even when the target is using a skill like Mantra of Resolve (PvP).
  ! BUG: This spirit will interrupt even when the target is using a skill like Mantra of Resolve. [from PvE version page]
Dulled Weapon #1235 | Hex Spell | Factions | E15 C1 R20
  For 5..20 seconds, target foe and all adjacent foes cannot achieve a critical hit and deal 3..20 less damage.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Damage reduction :: 0-4: 3 4 5 6 8 | 5-9: 9 10 11 12 13 | 10-14: 14 15 17 18 19 | 15-19: 20 21 22 23 25 | 20-21: 26 27
  # causes: Damage Reduction; prevents: Critical Hit; range: Casting; aoe: adjacent
  ! ANOMALY: This hex only reduces damage from attacks.
Earthbind (PvP) #3015 | Binding Ritual | Factions | E15 C3 R45
  Create a level 1..10 spirit. All non-spirit foes knocked down within its range are knocked down for at least 3 seconds. Whenever this happens, this spirit loses 50..25 Health. This spirit dies after 15..45 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Health loss :: 0-4: 50 48 47 45 43 | 5-9: 42 40 38 37 35 | 10-14: 33 32 30 28 27 | 15-19: 25 23 22 20 18 | 20-21: 17 15
  ~ Duration :: 0-4: 15 17 19 21 23 | 5-9: 25 27 29 31 33 | 10-14: 35 37 39 41 43 | 15-19: 45 47 49 51 53 | 20-21: 55 57
  # causes: Spirit, Health Loss; aoe: spirit
  ! ANOMALY: Armor of Unfeeling will reduce the health loss of this spirit caused by its knock down effect. [from PvE version page]
Ghostly Weapon #2206 | Weapon Spell | Eye of the North | E3 C¼ R1
  For 5..20 seconds, target other ally's next attack cannot be blocked.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Unblockable; target: other allies
Guided Weapon (PvP) #3462 | Weapon Spell | Factions | E5 C2 R12
  For 4..10 seconds, target ally's attacks cannot be blocked.
  ~ Duration :: 0-4: 4 4 5 5 6 | 5-9: 6 6 7 7 8 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 12
  # causes: Unblockable; target: allies
Mighty Was Vorizun #773 | Item Spell | Factions | E5 C2 R30
  Hold Vorizun's ashes for up to 15..60 seconds. While you hold his ashes, you gain +15 armor and +30 maximum Energy.
  ~ Duration :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  # causes: Increased Armor Rating
Pain (PvP) #3007 | Binding Ritual | Factions | E5 C1½ R30
  Create a level 1..8 spirit. This spirit's attacks deal 5..30 damage. This spirit dies after 30..150 seconds.
  ~ Level :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  ~ Armor-ignoring damage :: 0-4: 5 7 8 10 12 | 5-9: 13 15 17 18 20 | 10-14: 22 23 25 27 28 | 15-19: 30 32 33 35 37 | 20-21: 38 40
  ~ Duration :: 0-4: 30 38 46 54 62 | 5-9: 70 78 86 94 102 | 10-14: 110 118 126 134 142 | 15-19: 150 158 166 174 182 | 20-21: 190 198
  # causes: Spirit; aoe: none
Restoration (PvP) #3018 | Binding Ritual | Factions | E10 C3 R45
  Create a level 1..10 spirit. When this spirit dies, all party members in the area are resurrected with 5..50% Health and zero Energy. This spirit dies after 30 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ % Health :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Spirit
  ! ANOMALY: This spirit will also resurrect creatures created via summoning stones that were dead and in the area of the spirit. [from PvE version page]
Shadowsong (PvP) #3006 | Binding Ritual | Factions | E15 C2 R30
  Create a level 1..6 spirit. The spirit's attacks deal 5..20 damage and cause Blindness for 1..6 second[s]. This spirit dies after 30 second[s].
  ~ Level :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  ~ Blind duration :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  ~ Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Spirit, Blind; aoe: none
  ! BUG: The non-concise description states that the "spirit dies after 30 second" instead of using the plural "seconds" with Communing rank 0 and 1. [from PvE version page]
Shelter (PvP) #3016 | Binding Ritual | Factions | E25 C5 R45
  Create a level 1..8 spirit. Non-spirit allies within its range cannot lose more than 10% maximum Health from a single attack. When this spirit prevents damage, it loses 75..45 Health. This spirit lasts 30..60 seconds.
  ~ Level :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  ~ Health loss :: 0-4: 75 73 71 69 67 | 5-9: 65 63 61 59 57 | 10-14: 55 53 51 49 47 | 15-19: 45 43 41 39 37 | 20-21: 35 33
  ~ Duration :: 0-4: 30 32 34 36 38 | 5-9: 40 42 44 46 48 | 10-14: 50 52 54 56 58 | 15-19: 60 62 64 66 68 | 20-21: 70 72
  # causes: Spirit, Damage Reduction, Health Loss; aoe: spirit
  ! ANOMALY: While skill descriptions state "attacks", damage from spells and signets is also reduced.
  ! ANOMALY: Armor of Unfeeling will reduce the health loss of this spirit caused by its damage mitigation effect. [from PvE version page]
  ! ANOMALY: While skill descriptions state "attacks", damage from spells and signets is also reduced. [from PvE version page]
  ! ANOMALY: Shelter's effect persists briefly after it prevents damage in a way that would have killed it ([https://youtu.be/7AFx0dp8_-o video]). [from PvE version page]
Signet of Ghostly Might (PvP) #2966 | Elite Signet | Nightfall | C1 R5
  Target allied summoned creature's attacks deal 5..35 more damage. After 10 seconds, that creature is destroyed.
  ~ + Damage :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  # removes: spirit; target: summoned creatures; range: casting
Soothing (PvP) #3009 | Binding Ritual | Factions | E25 C5 R60
  Create a level 1..8 spirit. All foes within its range take twice as long to build adrenaline. This spirit dies after 15..45 seconds.
  ~ Level :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  ~ Duration :: 0-4: 15 17 19 21 23 | 5-9: 25 27 29 31 33 | 10-14: 35 37 39 41 43 | 15-19: 45 47 49 51 53 | 20-21: 55 57
  # causes: Spirit; aoe: spirit
Sundering Weapon #2148 | Weapon Spell | Eye of the North | E5 C1 R10
  For 4..10 seconds, target ally's next 3 attacks have 10% armor penetration and cause Cracked Armor for 5..20 seconds.
  ~ Duration :: 0-4: 4 4 5 5 6 | 5-9: 6 6 7 7 8 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 12
  ~ Cracked Armor duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Cracked Armor, Armor Penetration; target: allies; range: Casting
Union (PvP) #3005 | Binding Ritual | Factions | E15 C3 R45
  Create a level 1..8 spirit. Whenever a non-spirit ally in its range takes damage or life steal, it is reduced by 15 and the spirit takes 15 damage. This spirit dies after 30..60 seconds.
  ~ Level :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  ~ Duration :: 0-4: 30 32 34 36 38 | 5-9: 40 42 44 46 48 | 10-14: 50 52 54 56 58 | 15-19: 60 62 64 66 68 | 20-21: 70 72
  # causes: Spirit, Damage Reduction; aoe: spirit
Vital Weapon #1267 | Weapon Spell | Factions | E5 C1 R2
  For 5..30 seconds, target ally has a Vital Weapon and has +40..175 maximum Health.
  ~ Duration :: 0-4: 5 7 8 10 12 | 5-9: 13 15 17 18 20 | 10-14: 22 23 25 27 28 | 15-19: 30 32 33 35 37 | 20-21: 38 40
  ~ +Max Health :: 0-4: 40 49 58 67 76 | 5-9: 85 94 103 112 121 | 10-14: 130 139 148 157 166 | 15-19: 175 184 193 202 211 | 20-21: 220 229
  # causes: Increased Maximum Health; target: allies
Wanderlust (PvP) #3020 | Elite Binding Ritual | Factions | E10 C3 R45
  Create a level 1..8 spirit. Whenever this spirit's attack hits a stationary foe, that foe is knocked down and the spirit loses 70..50 Health. This spirit dies after 30..60 seconds.
  ~ Level :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  ~ Health loss :: 0-4: 70 69 67 66 65 | 5-9: 63 62 61 59 58 | 10-14: 57 55 54 53 51 | 15-19: 50 49 47 46 45 | 20-21: 43 42
  ~ Duration :: 0-4: 30 32 34 36 38 | 5-9: 40 42 44 46 48 | 10-14: 50 52 54 56 58 | 15-19: 60 62 64 66 68 | 20-21: 70 72
  # causes: Spirit, Knockdown, Health Loss; aoe: none
Weapon of Quickening #1268 | Elite Weapon Spell | Factions | E5 C1 R5
  For 5..25 seconds, target ally has a Weapon of Quickening, and spells and binding rituals recharge 33% faster.
  ~ Duration :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  # causes: Decreased Recharge Time; target: allies

### Ritualist / No Attribute
Draw Spirit #1224 | Spell | Factions | E5 C¼ R5
  Teleport target allied spirit to your location.
  # causes: Shadow Step; target: spirits
  ! BUG: Contrary to the description, this skill causes the spirit to shadow step rather than teleport.

### Ritualist / Restoration Magic
Blind Was Mingson #788 | Item Spell | Factions | E5 C1 R20
  Hold Mingson's ashes for up to 15..60 seconds. When you drop his ashes, all nearby foes are Blinded for 3..8 seconds.
  ~ Duration :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  ~ Blind duration :: 0-4: 3 3 4 4 4 | 5-9: 5 5 5 6 6 | 10-14: 6 7 7 7 8 | 15-19: 8 8 9 9 9 | 20-21: 10 10
  # causes: Blind; target: untargeted; aoe: nearby
Death Pact Signet (PvP) #2872 | Signet | Nightfall | C4 R12
  Resurrect target party member with your current Health and 15..100% Energy. The next time that ally dies within 120 seconds, so do you.
  ~ % Energy :: 0-4: 15 21 26 32 38 | 5-9: 43 49 55 60 66 | 10-14: 72 77 83 89 94 | 15-19: 100 106 111 117 123 | 20-21: 128 134
  # target: dead party members
Defiant Was Xinrae #812 | Elite Item Spell | Factions | E5 C1 R20
  Hold Xinrae's ashes for up to 15..60 seconds. While you hold her ashes, you cannot lose more than 20% of your max Health from a single hit. When you drop her ashes, you steal 5..50 Health from all nearby foes.
  ~ Duration :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  ~ Life stealing :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Damage Reduction, Life Stealing; target: untargeted; aoe: nearby
Flesh of My Flesh (PvP) #2866 | Spell | Factions | E5 C4 R6
  Lose half your Health. Resurrect target party member with your current Health and 5..20% Energy.
  ~ % Energy :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Health Loss; target: dead party members
  ! ANOMALY: This skill does not have a casting symbol. [from PvE version page]
Generous Was Tsungrai #772 | Item Spell | Factions | E5 S10% C1 R15
  Hold Tsungrai's ashes for up to 15..60 seconds and gain +50..140 maximum Health. When you drop his ashes, you gain 100..280 Health.
  ~ Duration :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  ~ + Max health :: 0-4: 50 56 62 68 74 | 5-9: 80 86 92 98 104 | 10-14: 110 116 122 128 134 | 15-19: 140 146 152 158 164 | 20-21: 170 176
  ~ Health gain :: 0-4: 100 112 124 136 148 | 5-9: 160 172 184 196 208 | 10-14: 220 232 244 256 268 | 15-19: 280 292 304 316 328 | 20-21: 340 352
  # causes: Increased Maximum Health, Health Gain
Ghostmirror Light #1741 | Spell | Nightfall | E5 C1 R3
  Target other ally is healed for 15..90 Health. If you are within earshot of a spirit, you are also healed for 15..90 Health.
  ~ Other heal :: 0-4: 15 20 25 30 35 | 5-9: 40 45 50 55 60 | 10-14: 65 70 75 80 85 | 15-19: 90 95 100 105 110 | 20-21: 115 120
  ~ Self heal :: 0-4: 15 20 25 30 35 | 5-9: 40 45 50 55 60 | 10-14: 65 70 75 80 85 | 15-19: 90 95 100 105 110 | 20-21: 115 120
  # causes: Healing; target: other allies
  ! ANOMALY: While most healing spells can't target a spirit, this one can. Though the spirit receives no healing from it, the user does.
  ! BUG: Contrary to the concise description, this skill's conditional effect causes healing and not health gain.
Life (PvP) #3012 | Binding Ritual | Factions | E10 C3 R20
  Create a level 1..10 spirit. When this spirit dies, all non-spirit allies within its range are healed for 1..7 Health for each second this spirit was alive. This spirit dies after 20 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Healing :: 0-4: 1 1 2 2 3 | 5-9: 3 3 4 4 5 | 10-14: 5 5 6 6 7 | 15-19: 7 7 8 8 9 | 20-21: 9 9
  # causes: Spirit, Healing; aoe: spirit
  ! ANOMALY: This skill will create a spirit with an offensive appearance.
  ! ANOMALY: This skill will create a spirit with an offensive appearance. [from PvE version page]
Lively Was Naomei #1222 | Item Spell | Factions | E15 C6 R20
  Hold Naomei's ashes for up to 45 seconds. When you drop her ashes, all party members in the area are resurrected with 15..75% Health and zero Energy.
  ~ % Health :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  # aoe: in the area
Mend Body and Soul #1234 | Spell | Factions | E5 C¾ R3
  Target ally is healed for 20..115 Health. That ally loses one condition for each spirit within earshot.
  ~ Healing :: 0-4: 20 26 33 39 45 | 5-9: 52 58 64 71 77 | 10-14: 83 90 96 102 109 | 15-19: 115 121 128 134 140 | 20-21: 147 153
  # causes: Healing; removes: Condition; target: allies
  ! ANOMALY: While most other ally targeted Restoration Magic spells cast a unique visual effect on the target, Mend Body and Soul places a unique visual effect on the caster instead.
Mending Grip #2202 | Spell | Eye of the North | E5 C1 R4
  Target ally is healed for 30..90 Health. If that ally is under the effects of a weapon spell, that ally loses one condition.
  ~ Healing :: 0-4: 30 34 38 42 46 | 5-9: 50 54 58 62 66 | 10-14: 70 74 78 82 86 | 15-19: 90 94 98 102 106 | 20-21: 110 114
  # removes: Condition; target: allies
  ! ANOMALY: This skill does not have a casting symbol.
Preservation (PvP) #3011 | Elite Binding Ritual | Factions | E5 C3 R20
  Create a level 1..10 spirit. Every 4 seconds, this spirit heals one non-spirit ally in the area for 10..115 Health. This spirit dies after 90 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Healing :: 0-4: 10 17 24 31 38 | 5-9: 45 52 59 66 73 | 10-14: 80 87 94 101 108 | 15-19: 115 122 129 136 143 | 20-21: 150 157
  # causes: Spirit, Healing; aoe: in the area
Protective Was Kaolai #1219 | Item Spell | Factions | E10 C1 R20
  Hold Kaolai's ashes for up to 15..60 seconds. While you hold his ashes, you gain 20 armor. When you drop his ashes, all party members are healed for 20..95 Health.
  ~ Duration :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  ~ Healing :: 0-4: 20 25 30 35 40 | 5-9: 45 50 55 60 65 | 10-14: 70 75 80 85 90 | 15-19: 95 100 105 110 115 | 20-21: 120 125
  # causes: Increased Armor Rating, Healing; aoe: party
Pure Was Li Ming #2072 | Item Spell | Eye of the North | E5 C1 R20
  Hold Li Ming's ashes for 5..20 seconds. While you hold her ashes, conditions on you expire 10..50% faster. When you drop her ashes, all allies within earshot lose 1..4 condition[s].
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Condition duration reduction % :: 0-4: 10 13 15 18 21 | 5-9: 23 26 29 31 34 | 10-14: 37 39 42 45 47 | 15-19: 50 53 55 58 61 | 20-21: 63 66
  ~ Conditions removed :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  # removes: Condition; target: untargeted; aoe: earshot
Recovery (PvP) #3025 | Binding Ritual | Nightfall | E15 C3 R30
  Create a level 1..10 spirit. Conditions on allies within range of this spirit expire 20..50% faster. This spirit dies after 30..60 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Faster condition expiration % :: 0-4: 20 22 24 26 28 | 5-9: 30 32 34 36 38 | 10-14: 40 42 44 46 48 | 15-19: 50 52 54 56 58 | 20-21: 60 62
  ~ Duration :: 0-4: 30 32 34 36 38 | 5-9: 40 42 44 46 48 | 10-14: 50 52 54 56 58 | 15-19: 60 62 64 66 68 | 20-21: 70 72
  # causes: Spirit; aoe: spirit
  ! BUG: The French translation of Spirit of Recovery is the same as Spirit of Recuperation but with a lower case "r", which can be misleading. [from PvE version page]
  ! ANOMALY: Rather than conditions expiring at a faster rate, their duration is reduced by the stated percentage. [from PvE version page]
Recuperation (PvP) #3013 | Binding Ritual | Factions | E25 C3 R45
  Create a level 1..10 spirit. Non-spirit allies within its range gain +1..3 Health regeneration. This spirit dies after 15..45 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Health regeneration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  ~ Duration :: 0-4: 15 17 19 21 23 | 5-9: 25 27 29 31 33 | 10-14: 35 37 39 41 43 | 15-19: 45 47 49 51 53 | 20-21: 55 57
  # causes: Spirit, Health Regeneration; aoe: spirit
Rejuvenation (PvP) #3039 | Binding Ritual | Eye of the North | E10 C3 R30
  Create a level 1..16 spirit. This spirit heals all party members within earshot for 3..10 Health each second. This spirit loses 3..10 Health for each party member healed in this way. This spirit dies after 30..90 seconds.
  ~ Spirit level :: 0-4: 1 2 3 4 5 | 5-9: 6 7 8 9 10 | 10-14: 11 12 13 14 15 | 15-19: 16 17 18 19 20 | 20-21: 21 22
  ~ Heal/second-loss/member :: 0-4: 3 3 4 4 5 | 5-9: 5 6 6 7 7 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 13
  ~ Spirit duration :: 0-4: 30 34 38 42 46 | 5-9: 50 54 58 62 66 | 10-14: 70 74 78 82 86 | 15-19: 90 94 98 102 106 | 20-21: 110 114
  ~ 4 Party Members :: 0-4: 8 8 8 9 9 | 5-9: 9 10 10 10 11 | 10-14: 11 11 12 12 12 | 15-19: 13 13 14 14 14 | 20-21: 15 15
  ~ 8 Party Members :: 0-4: 4 4 4 4 4 | 5-9: 4 5 5 5 5 | 10-14: 5 6 6 6 6 | 15-19: 6 7 7 7 7 | 20-21: 7 8
  # causes: Spirit, Healing, Health Loss; aoe: earshot
Resilient Was Xiko #1221 | Item Spell | Factions | E5 C1 R10
  Hold Xiko's ashes for up to 5..20 seconds. For each hex or condition you are suffering from while holding her ashes, you gain +3 Health regeneration. When you drop her ashes, you lose 1..4 conditions.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Conditions lost :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  # causes: Health Regeneration; removes: Condition
Resilient Weapon #787 | Weapon Spell | Factions | E10 C1 R6
  For 3..12 seconds, target ally has a Resilient Weapon. While suffering from a hex or condition, that ally gains +1..6 Health regeneration and +24 armor.
  ~ Duration :: 0-4: 3 4 4 5 5 | 5-9: 6 7 7 8 8 | 10-14: 9 10 10 11 11 | 15-19: 12 13 13 14 14 | 20-21: 15 16
  ~ Health regeneration :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  # causes: Health Regeneration, Increased Armor Rating; target: allies
Soothing Memories #1233 | Spell | Factions | E5 C¾ R4
  Target ally is healed for 10..100 Health. If you are holding an item, you gain 3 Energy.
  ~ Healing :: 0-4: 10 16 22 28 34 | 5-9: 40 46 52 58 64 | 10-14: 70 76 82 88 94 | 15-19: 100 106 112 118 124 | 20-21: 130 136
  # causes: Healing, Energy Gain; target: allies
Spirit Light #915 | Spell | Factions | E5 S17% C1 R4
  Target ally is healed for 60..180. If any spirits are within earshot, you don't sacrifice Health.
  ~ Healing :: 0-4: 60 68 76 84 92 | 5-9: 100 108 116 124 132 | 10-14: 140 148 156 164 172 | 15-19: 180 188 196 204 212 | 20-21: 220 228
  # causes: Healing; target: allies
Spirit Light Weapon #1257 | Elite Weapon Spell | Factions | E5 C1 R5
  For 10 seconds, target ally gains 5..25 Health per second and an additional 5..25 Health per second if that ally is within earshot of a spirit.
  ~ Health gain per second :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  ~ Additional health gain per second :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  # causes: Health Gain; target: allies
  ! BUG: Contrary to the concise description, this skill's conditional effect causes health gain and not healing.
Spirit Transfer #962 | Spell | Factions | E10 C¼ R5
  The spirit nearest you loses 5..50 Health. Target ally is healed for 5 for each point of Health lost.
  ~ Spirit health loss :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  ~ Healing :: 0-4: 25 40 55 70 85 | 5-9: 100 115 130 145 160 | 10-14: 175 190 205 220 235 | 15-19: 250 265 280 295 310 | 20-21: 325 340
  # causes: Health Loss, Healing; target: allies
  ! ANOMALY: Can be cast while targeting a spirit, in which case the spirit will lose health and no one will be healed.
Spiritleech Aura #2203 | Skill | Eye of the North | E5 C¼ R20
  For 5..20 seconds, all of your spirits within earshot deal 5..20 less damage and steal 5..20 Health when they attack.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Damage converted to life stealing :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Life Stealing; target: self; aoe: earshot
Tranquil Was Tanasen #913 | Elite Item Spell | Factions | E5 C1 R15
  Hold Tanasen's ashes for up to 5..20 seconds. While you hold his ashes, you have +10..25 armor and cannot be interrupted.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ + Armor rating :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  # causes: Increased Armor Rating
Vengeful Was Khanhei #790 | Elite Item Spell | Factions | E5 C¾ R15
  Hold Khanhei's ashes for 5..11 seconds. Whenever a foe strikes you in combat while you are holding Khanhei's ashes, you steal 10..45 Health from that foe.
  ~ Duration :: 0-4: 5 5 6 6 7 | 5-9: 7 7 8 8 9 | 10-14: 9 9 10 10 11 | 15-19: 11 11 12 12 13 | 20-21: 13 13
  ~ Life stealing :: 0-4: 10 12 15 17 19 | 5-9: 22 24 26 29 31 | 10-14: 33 36 38 40 43 | 15-19: 45 47 50 52 54 | 20-21: 57 59
  # causes: Life Stealing
Vengeful Weapon #964 | Weapon Spell | Factions | E5 C¼ R3
  For 8 seconds, the next time target ally takes damage or life steal from a foe, that ally steals up to 15..60 Health from that foe.
  ~ Life stealing :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  # causes: Life Stealing; target: allies
Vocal Was Sogolon #1731 | Item Spell | Nightfall | E10 C1 R30
  For 60 seconds, all shouts and chants you use last 20..50% longer.
  ~ % Longer :: 0-4: 20 22 24 26 28 | 5-9: 30 32 34 36 38 | 10-14: 40 42 44 46 48 | 15-19: 50 52 54 56 58 | 20-21: 60 62
Weapon of Remedy #1752 | Elite Weapon Spell | Nightfall | E3 C¼ R3
  For 8 seconds, the next time target ally takes damage or life steal from a foe, that ally steals up to 20..80 Health from that foe and loses 2 conditions.
  ~ Life stealing :: 0-4: 20 24 28 32 36 | 5-9: 40 44 48 52 56 | 10-14: 60 64 68 72 76 | 15-19: 80 84 88 92 96 | 20-21: 100 104
  # causes: Life Stealing; removes: Condition; target: allies; range: Casting
  ! BUG: If used when taking damage from multiple sources from only one attack, Weapon of Remedy will trigger multiple times. For example, if a foe hexed with Barbs takes physical damage, Weapon of Remedy will trigger both for the physical damage and for the Barbs damage.
Weapon of Shadow #983 | Weapon Spell | Factions | E10 C1 R20
  For 1..7 second[s], target ally has a Weapon of Shadow. Whenever that ally is struck by an attack, that ally's attacker becomes Blinded for 5 seconds. The next 1..3 times that ally hits with an attack, his target is Blinded for 5 seconds.
  ~ Duration :: 0-4: 1 1 2 2 3 | 5-9: 3 3 4 4 5 | 10-14: 5 5 6 6 7 | 15-19: 7 7 8 8 9 | 20-21: 9 9
  ~ Attacks :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Blind; target: allies
  ! BUG: The descriptions do not mention that this weapon spell ends after the affected target ally causes blindness the allotted number of times.
Weapon of Warding (PvP) #2893 | Weapon Spell | Factions | E10 C1 R8
  For 3..8 seconds, target ally has a Weapon of Warding that grants target ally +2..4 Health regeneration and a 50% chance to block. Weapon of Warding ends if that ally attacks.
  ~ Duration :: 0-4: 3 3 4 4 4 | 5-9: 5 5 5 6 6 | 10-14: 6 7 7 7 8 | 15-19: 8 8 9 9 9 | 20-21: 10 10
  ~ Health regeneration :: 0-4: 2 2 2 2 3 | 5-9: 3 3 3 3 3 | 10-14: 3 3 4 4 4 | 15-19: 4 4 4 4 5 | 20-21: 5 5
  # causes: Health Regeneration, Block; target: allies
Wielder's Boon #1265 | Spell | Factions | E5 C¼ R4
  Heal target ally for 15..60 points. If that ally is under the effects of a weapon spell, Wielder's Boon heals for an additional 15..75 Health.
  ~ Healing :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  ~ Additional healing :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  ~ Total healing :: 0-4: 30 37 44 51 58 | 5-9: 65 72 79 86 93 | 10-14: 100 107 114 121 128 | 15-19: 135 142 149 156 163 | 20-21: 170 177
  # causes: Healing; target: allies
Xinrae's Weapon #1750 | Elite Weapon Spell | Nightfall | E5 C¼ R3
  For 8 seconds, the next time target ally takes damage from a foe that damage is limited to 5% of that ally's max Health and that ally steals up to 20..80 Health from that foe.
  ~ Life stealing :: 0-4: 20 24 28 32 36 | 5-9: 40 44 48 52 56 | 10-14: 60 64 68 72 76 | 15-19: 80 84 88 92 96 | 20-21: 100 104
  # causes: Damage Reduction, Life Stealing; target: allies

### Ritualist / Spawning Power
Anguished Was Lingwah #1223 | Item Spell | Factions | E5 R30
  Hold Lingwah's ashes for up to 10..60 seconds. While you hold her ashes, your Ritualist hexes cost 1..5 less energy and last 50% longer. When you drop her ashes all your Ritualist hexes are recharged.
  ~ Item spell duration :: 0-4: 10 13 17 20 23 | 5-9: 27 30 33 37 40 | 10-14: 43 47 50 53 57 | 15-19: 60 63 67 70 73 | 20-21: 77 80
  ~ Less energy :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Decreased Energy Cost, Recharge
  ! BUG: No hexes are recharged if the user drops the ashes upon death.
Attuned Was Songkai #1220 | Elite Item Spell | Factions | E10 R30
  Hold Songkai's ashes for up to 45 seconds. While you hold her ashes, your spells and binding rituals cost -5..50% of the base Energy to cast.
  ~ Energy cost reduction % :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Decreased Energy Cost; requires: Spells, Binding Rituals; target: self
Boon of Creation #1230 | Enchantment Spell | Factions | E10 C2 R45
  For 15..60 seconds, whenever you create a creature, you gain 5..50 Health and 1..6 Energy.
  ~ Duration :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  ~ Healing :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  ~ Energy gain :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  # causes: Healing, Energy Gain
  ! BUG: Contrary to the descriptions, this skill causes healing and not health gain.
Consume Soul #914 | Elite Spell | Factions | E5 C1 R5
  You steal 5..70 Health from target foe. All hostile summoned creatures in earshot of that foe take 25..125 damage.
  ~ Life stealing :: 0-4: 5 9 14 18 22 | 5-9: 27 31 35 40 44 | 10-14: 48 53 57 61 66 | 15-19: 70 74 79 83 87 | 20-21: 92 96
  ~ Damage :: 0-4: 25 32 38 45 52 | 5-9: 58 65 72 78 85 | 10-14: 92 98 105 112 118 | 15-19: 125 132 138 145 152 | 20-21: 158 165
  # causes: Life Stealing; target: foes; aoe: earshot
Doom #1264 | Spell | Factions | E10 C1 R8
  Strike target foe for 10..60 lightning (maximum 135) damage for every recharging binding ritual you have.
  ~ Lightning damage :: 0-4: 10 13 17 20 23 | 5-9: 27 30 33 37 40 | 10-14: 43 47 50 53 57 | 15-19: 60 63 67 70 73 | 20-21: 77 80
  # causes: Lightning Damage; target: foes; range: casting; aoe: none
Empowerment (PvP) #3024 | Binding Ritual | Nightfall | E5 C3 R30
  Create a level 1..10 spirit. All allies within its range holding an item gain 15..45 maximum Health and 10 maximum Energy. This spirit dies after 15..60 seconds.
  ~ Level :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ + Max health :: 0-4: 15 17 19 21 23 | 5-9: 25 27 29 31 33 | 10-14: 35 37 39 41 43 | 15-19: 45 47 49 51 53 | 20-21: 55 57
  ~ Duration :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  # causes: Spirit, Increased Maximum Health; aoe: spirit
Energetic Was Lee Sa #2016 | Item Spell | Eye of the North | E10 C2 R20
  Hold Lee Sa's ashes for 5..15 seconds. While you hold her ashes, you gain +2 Energy regeneration. When you drop her ashes, you gain +1..10 Energy.
  ~ Duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  ~ Energy gain (when dropped) :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Total energy gain (if held) :: 0-4: 4 5 6 7 8 | 5-9: 9 10 11 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Net energy gain (en-spell cost) :: 0-4: -6 -5 -4 -3 -2 | 5-9: -1 0 1 3 4 | 10-14: 5 6 7 8 9 | 15-19: 10 11 12 13 14 | 20-21: 15 16
  # causes: Energy Regeneration, Energy Gain
Explosive Growth #1229 | Enchantment Spell | Factions | E5 C2 R45
  For 15..60 seconds, whenever you create a creature, up to 5 foes near that creature are struck for 20..65 lightning damage.
  ~ Duration :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  ~ Lightning damage :: 0-4: 20 23 26 29 32 | 5-9: 35 38 41 44 47 | 10-14: 50 53 56 59 62 | 15-19: 65 68 71 74 77 | 20-21: 80 83
  # causes: Lightning Damage; target: self; aoe: nearby
Feast of Souls #980 | Spell | Factions | E5 C¼ R10
  Destroy all nearby allies' spirits. For each spirit destroyed in this way, all party members are healed for 50..100 Health.
  ~ Healing :: 0-4: 50 53 57 60 63 | 5-9: 67 70 73 77 80 | 10-14: 83 87 90 93 97 | 15-19: 100 103 107 110 113 | 20-21: 117 120
  # causes: Healing; removes: Spirit; target: untargeted; aoe: nearby, party
  ! BUG: The plain text description says "nearby allies'" spirits, instead of "nearby allied spirits". The skill works according to the concise description.
Ghostly Haste #1244 | Enchantment Spell | Factions | E10 C1 R20
  For 5..30 seconds, spells you cast while within earshot of a spirit recharge 25% faster.
  ~ Duration :: 0-4: 5 7 8 10 12 | 5-9: 13 15 17 18 20 | 10-14: 22 23 25 27 28 | 15-19: 30 32 33 35 37 | 20-21: 38 40
  # causes: Decreased Recharge Time; target: self
Reclaim Essence #1482 | Elite Spell | Nightfall | E5 C1 R30
  All of your Spirits die. You gain 5..20 Energy and all of your Binding Rituals are recharged if a Spirit died in this way.
  ~ Energy gain :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Energy Gain, Recharge; removes: spirit; target: self; range: compass; aoe: none
Renewing Memories #1739 | Enchantment Spell | Nightfall | E5 C1 R20
  For 5..20 seconds, while holding an item, any weapon and item Spells you cast cost 5..35% less Energy.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Energy reduction % :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  # causes: Decreased Energy Cost; requires: Bundle; target: self
Ritual Lord #1217 | Elite Skill | Factions | S2% R45
  For 5..35 seconds, your Ritualist attributes are boosted by 2..4 for your next skill. If that skill is a Binding Ritual, it recharges 10..60% faster and Ritual Lord recharges instantly.
  ~ Duration :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  ~ Attribute boost :: 0-4: 2 2 2 2 3 | 5-9: 3 3 3 3 3 | 10-14: 3 3 4 4 4 | 15-19: 4 4 4 4 5 | 20-21: 5 5
  ~ % Faster recharge :: 0-4: 10 13 17 20 23 | 5-9: 27 30 33 37 40 | 10-14: 43 47 50 53 57 | 15-19: 60 63 67 70 73 | 20-21: 77 80
  # causes: Decreased Recharge Time, Recharge, Increased Attribute
  ! ANOMALY: Ritual Lord will only increase the skill progression of a skill, and not inherent effects from Spawning Power.
Rupture Soul #917 | Spell | Factions | E10 C¾ R5
  Target allied spirit is destroyed. All nearby enemies are struck for 50..140 lightning damage and become blinded for 3..12 seconds.
  ~ Lightning damage :: 0-4: 50 56 62 68 74 | 5-9: 80 86 92 98 104 | 10-14: 110 116 122 128 134 | 15-19: 140 146 152 158 164 | 20-21: 170 176
  ~ Blind duration :: 0-4: 3 4 4 5 5 | 5-9: 6 7 7 8 8 | 10-14: 9 10 10 11 11 | 15-19: 12 13 13 14 14 | 20-21: 15 16
  # causes: Blind, Lightning Damage; removes: Spirit; target: spirits; range: Casting; aoe: nearby
Sight Beyond Sight #1738 | Enchantment Spell | Nightfall | E5 C¼ R15
  For 8..20 seconds, you cannot be Blinded.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  # causes: Condition Immunity; removes: Condition; target: self
Signet of Binding #1743 | Signet | Nightfall | C2 R15
  You lose 200..50 Health and take control of target enemy-controlled spirit. (50% failure chance with Spawning Power 4 or less.)
  ~ Health loss :: 0-4: 200 190 180 170 160 | 5-9: 150 140 130 120 110 | 10-14: 100 90 80 70 60 | 15-19: 50 40 30 20 10 | 20-21: 0 0
  # causes: Health Loss; target: spirits; range: casting
  ! ANOMALY: Spirits taken control of with this skill ignore the restriction of having multiple allied spirits of the same name within range of each other. The restriction will however be correctly applied should the spirit be teleported via Draw Spirit, Swap or Summon Spirits, preserving only the most recent spirit.
Signet of Creation #1238 | Signet | Factions | C1 R20
  You gain 4 Energy for every summoned creature you control within earshot (maximum 3..12 Energy).
  ~ Max energy gained :: 0-4: 3 4 4 5 5 | 5-9: 6 7 7 8 8 | 10-14: 9 10 10 11 11 | 15-19: 12 13 13 14 14 | 20-21: 15 16
  # causes: Energy Gain; target: self
Soul Twisting (PvP) #3461 | Elite Skill | Factions | E5 R15
  For 5..45 seconds, your Binding Rituals cost 15 less Energy (minimum 5) and recharge 25..50% faster. Soul Twisting ends after 1..3 Binding Ritual[s].
  ~ Binding Rituals :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  ~ Duration :: 0-4: 5 8 10 13 16 | 5-9: 18 21 24 26 29 | 10-14: 32 34 37 40 42 | 15-19: 45 48 50 53 56 | 20-21: 58 61
  ~ Recharge reduction % :: 0-4: 25 27 28 30 32 | 5-9: 33 35 37 38 40 | 10-14: 42 43 45 47 48 | 15-19: 50 52 53 55 57 | 20-21: 58 60
  # causes: Decreased Energy Cost, Recharge; target: self
Spirit Channeling #1231 | Elite Enchantment Spell | Factions | E5 C1 R30
  For 12 seconds, you have +1..6 Energy regeneration. When you cast this spell, you gain 3..12 Energy if you are within earshot of a spirit.
  ~ Energy regeneration :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  ~ Energy gain :: 0-4: 3 4 4 5 5 | 5-9: 6 7 7 8 8 | 10-14: 9 10 10 11 11 | 15-19: 12 13 13 14 14 | 20-21: 15 16
  # causes: Energy Regeneration, Energy Gain; requires: Spirit; target: self
Spirit to Flesh #918 | Touch spell | Factions | E10 C¾ R15
  Spell. Target touched allied spirit is destroyed. All nearby allies are healed for 30..240.
  ~ Healing :: 0-4: 30 44 58 72 86 | 5-9: 100 114 128 142 156 | 10-14: 170 184 198 212 226 | 15-19: 240 254 268 282 296 | 20-21: 310 324
  # causes: Healing; removes: spirit; target: spirits; range: touch; aoe: nearby
Spirit's Gift #1480 | Enchantment Spell | Nightfall | E10 C1 R45
  For 60 seconds, whenever you create a creature, all allies near that creature gain 5..50 Health and lose 1 condition.
  ~ Health gain :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Health Gain; removes: Condition; target: self; aoe: nearby
Spirit's Strength #1736 | Elite Enchantment Spell | Nightfall | E5 C1 R20
  For 15..60 seconds, your attacks deal 5..35 more damage while under the effects of a weapon spell.
  ~ Duration :: 0-4: 15 18 21 24 27 | 5-9: 30 33 36 39 42 | 10-14: 45 48 51 54 57 | 15-19: 60 63 66 69 72 | 20-21: 75 78
  ~ + Damage :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  # target: self
Weapon of Renewal #2149 | Weapon Spell | Eye of the North | E5 C1 R10
  For 5..20 seconds, the next time target ally hits with an attack skill, that ally gains 1..7 Energy.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Energy gain :: 0-4: 1 1 2 2 3 | 5-9: 3 3 4 4 5 | 10-14: 5 5 6 6 7 | 15-19: 7 7 8 8 9 | 20-21: 9 9
  # causes: Energy Gain; target: allies
Wielder's Remedy #1740 | Enchantment Spell | Nightfall | E3 C1 R10
  For 10..30 seconds, whenever you cast a weapon spell on an ally, that ally loses 2 conditions.
  ~ Duration :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  # removes: Condition; target: self
Wielder's Zeal #1737 | Elite Enchantment Spell | Nightfall | E5 C1 R10
  For 10..40 seconds, whenever you cast a Weapon Spell on an ally, you gain 1..5 Energy.
  ~ Duration :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  ~ Energy gain :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Energy Gain

## Paragon

### Paragon / Command
"Brace Yourself!" (PvP) #3027 | Shout | Nightfall | E5 R8
  For 5..15 seconds, the next time target other ally would be knocked down, 1 nearby foe takes 15..90 damage instead.
  ~ Duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  ~ Damage :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  ~ (15..90) [derived] :: 0-4: 15 20 25 30 35 | 5-9: 40 45 50 55 60 | 10-14: 65 70 75 80 85 | 15-19: 90 95 100 105 110 | 20-21: 115 120
  # causes: Knockdown Immunity; target: other allies; aoe: nearby
"Can't Touch This!" (PvP) #3031 | Shout | Nightfall | E5 R10
  For 20 seconds, the next 1..5 touch skill[s] used against you fail[s].
  ~ Failures :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # aoe: None
  ! ANOMALY: Unlike most shouts, "Can't Touch This!" ends if it's reapplied before it expires, triggering the effects of echoes. [from PvE version page]
  ! BUG: "Can't Touch This!" is applied to party members only. [from PvE version page]
"Fall Back!" (PvP) #3037 | Shout | Nightfall | E10 R25
  For 4..10 seconds, all allies within earshot gain 5..15 Health per second while moving and move 33% faster. "Fall Back!" ends on an ally affected by this shout when that ally successfully hits with an attack.
  ~ Duration :: 0-4: 4 4 5 5 6 | 5-9: 6 6 7 7 8 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 12
  ~ Health gain :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Health Gain, Increased Movement Speed
"Find Their Weakness!" (PvP) #3034 | Shout | Nightfall | E10 R15
  For 5..20 seconds, the next time target ally criticals, that ally also inflicts a Deep Wound for 5..20 seconds.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Deep Wound duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Deep Wound; target: allies; aoe: None
  ! BUG: The exact description should be "the next time target ally successfully hits with an attack", as this skill will not be removed and its effects won't be applied if the next attack misses (due to blind), is blocked or if there is no line of sight. [from PvE version page]
"Go for the Eyes!" (PvP) #3026 | Shout | Nightfall | Ad4 R4
  For 10 seconds, the next time each ally within earshot makes an attack, that attack has an additional 30..75% chance to critical.
  ~ + Chance % :: 0-4: 30 33 36 39 42 | 5-9: 45 48 51 54 57 | 10-14: 60 63 66 69 72 | 15-19: 75 78 81 84 87 | 20-21: 90 93
  # causes: Critical Hit
  ! ANOMALY: Contrary to what the description suggests, this skill triggers on hit rather than on attack. For instance, if Cyclone Axe hits several foes, only one of them has increased chance to be critically hit. [from PvE version page]
"Help!" (PvP) #3036 | Shout | Nightfall | E5 R15
  Target non-spirit ally gains 5..50 Health. For 1..10 seconds, other allies' spells targeting that ally cast 50% faster.
  ~ Duration :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  ~ Health gain :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Decreased Activation Time, Health Gain; aoe: none
  ! BUG: The effects of this skill apply to non-spell skills as well. [from PvE version page]
"Incoming!" (PvP) #2879 | Elite Shout | Nightfall | E10 R25
  For 4..10 seconds, all allies within earshot move 33% faster, and gain 5..15 Health while moving.
  ~ Duration :: 0-4: 4 4 5 5 6 | 5-9: 6 6 7 7 8 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 12
  ~ Health gain :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Increased Movement Speed, Health Gain
"Make Haste!" #1591 | Shout | Nightfall | E5 R10
  For 5..20 seconds, target other ally moves 33% faster. This skill ends if that ally successfully hits with an attack.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Increased Movement Speed; target: other allies; aoe: None
"Never Give Up!" (PvP) #3035 | Shout | Nightfall | E5 R20
  All allies within earshot and below 75% Health gain 1..10 Energy.
  ~ Energy gain :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # causes: Energy Gain
  ! BUG: Heroes consider party members outside of the actual range. [from PvE version page]
"Never Surrender!" (PvP) #2880 | Shout | Nightfall | E5 R20
  For 10 seconds, all party members within earshot and below 75% Health gain +1..5 Health regeneration.
  ~ Health regeneration :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Health Regeneration
  ! BUG: Heroes consider party members outside of the actual range (roughly twice of earshot). [from PvE version page]
  ! ANOMALY: This skill will affect summoned creatures, like spirits or minions, if used by a summoned ally, such as the Imperial Guard Captain. [from PvE version page]
"Stand Your Ground!" (PvP) #3032 | Shout | Nightfall | E15 R30
  For 5..20 seconds, all party members within earshot receive +24 armor when not moving. This effect ends on an ally affected by this shout when that ally attacks.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Increased Armor Rating
"We Shall Return!" (PvP) #3033 | Shout | Nightfall | E5 R15
  For 10 seconds, whenever party members within earshot use a resurrection skill, their fallen allies return with 10..75% more Health and 5..50% more Energy.
  ~ More health % :: 0-4: 10 14 19 23 27 | 5-9: 32 36 40 45 49 | 10-14: 53 58 62 66 71 | 15-19: 75 79 84 88 92 | 20-21: 97 101
  ~ More energy % :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  ! BUG: "We Shall Return!" does not return energy from Leadership. [from PvE version page]
Anthem of Disruption (PvP) #3040 | Chant | Eye of the North | E10 C2 R15
  For 1..10 seconds, the next attack skill used by each ally within earshot also interrupts an action.
  ~ Duration :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # causes: Interrupt
Anthem of Envy (PvP) #3148 | Chant | Nightfall | Ad6 C1 R6
  For 10 seconds, the next attack skill used by each ally within earshot deals +10..20 damage against foes with more than 50% Health.
  ~ Damage :: 0-4: 10 11 11 12 13 | 5-9: 13 14 15 15 16 | 10-14: 17 17 18 19 19 | 15-19: 20 21 21 22 23 | 20-21: 23 24
Anthem of Guidance #1568 | Elite Chant | Nightfall | Ad2 C1
  For 10 seconds, the next attack skill used by each party member within earshot cannot be blocked.
  # causes: Unblockable
Anthem of Weariness #2017 | Chant | Eye of the North | E5 C1 R10
  For 8 seconds, the next attack skill used by each ally within earshot also causes Weakness for 1..16 second[s].
  ~ Weakness duration :: 0-4: 1 2 3 4 5 | 5-9: 6 7 8 9 10 | 10-14: 11 12 13 14 15 | 15-19: 16 17 18 19 20 | 20-21: 21 22
  # causes: Weakness
Bladeturn Refrain (PvP) #3029 | Echo | Nightfall | E5 C1 R8
  For 20 seconds, target non-spirit ally has +10..40 armor against slashing damage. This echo is reapplied every time a chant or shout ends on that ally.
  ~ + Armor rating :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Increased Armor Rating, Renewal; target: allies
Crippling Anthem #1554 | Elite Chant | Nightfall | Ad3 C1
  For 10 seconds, the next attack skill used by each ally within earshot causes Crippling for 5..15 seconds.
  ~ Cripple duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Crippled
Godspeed #1556 | Shout | Nightfall | E10 R30
  For 5..20 seconds, all allies within earshot move 25% faster while under the effects of an enchantment.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Increased Movement Speed
  ! ANOMALY: This skill doesn't have punctuation in its name like other shouts, even though the character still shouts it with the punctuation.

### Paragon / Leadership
"Lead the Way!" #1590 | Shout | Nightfall | E5 R8
  Target ally moves 25% faster for 1..5 seconds for each ally within earshot (maximum of 30 seconds).
  ~ Duration :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Increased Movement Speed; target: allies
"Make Your Time!" #1779 | Shout | Nightfall | E10 R10
  You gain 2 strikes of adrenaline for each party member within earshot (maximum 1..8 adrenaline).
  ~ Adrenaline :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  # causes: Adrenaline Gain; target: self
  ! ANOMALY: This skill does not trigger any energy gain from Leadership, even for affecting the skill user.
  ! BUG: "Make Your Time!" counts all allies, not just party members.
"They're on Fire!" #1597 | Shout | Nightfall | E10 R10
  For 10 seconds, party members within earshot take 5..35% less damage from foes suffering from Burning.
  ~ Damage reduction % :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  # causes: Damage Reduction
Aggressive Refrain #1774 | Echo | Nightfall | E15 C1 R20
  For 5..25 seconds, you attack 25% faster but have -20 armor. This echo is reapplied every time a chant or shout ends on you.
  ~ Duration :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  # causes: Increased Attack Speed, Decreased Armor Rating, Renewal
  ! BUG: Similar to Cracked Armor, this skill will not lower your armor rating below 60 or your "core" armor rating, if your "core" armor rating is lower than 60.
  ! BUG: If you use a skill or combination of skills and effects that grant +46 or more armor rating, Aggressive Refrain's armor penalty does not function. See also armor calculation.
Angelic Bond #1587 | Elite Skill | Nightfall | E5 C1 R15
  For 10 seconds, the next time an ally within earshot would take fatal damage, that damage is negated and that ally is healed for 20..200 Health. Angelic Bond ends on all other allies.
  ~ Healing :: 0-4: 20 32 44 56 68 | 5-9: 80 92 104 116 128 | 10-14: 140 152 164 176 188 | 15-19: 200 212 224 236 248 | 20-21: 260 272
  # causes: Damage Reduction, Healing; aoe: earshot
  ! BUG: The skill states it will end on all other allies, however, it will only end on party members of the ally that it triggers on, not all allies.
  ! ANOMALY: Despite the skill descriptions, this skill triggers with health degeneration, health loss, life stealing, and health sacrifice, not just damage.
Angelic Protection #1586 | Skill | Nightfall | E5 R30
  For 10 seconds, any time target other ally takes more than 250..80 damage per second, that ally is healed for any damage over that amount.
  ~ Damage taken :: 0-4: 250 239 227 216 205 | 5-9: 193 182 171 159 148 | 10-14: 137 125 114 103 91 | 15-19: 80 69 57 46 35 | 20-21: 23 12
  # causes: Healing; target: other allies
  ! ANOMALY: Unlike most typeless skills with no activation time, this skill cannot be activated in the middle of another action and has a slight aftercast delay.
Anthem of Flame #1557 | Chant | Nightfall | E5 C1 R10
  For 10 seconds, the next attack skill used by each party member within earshot also causes Burning for 1..5 second[s].
  ~ Burning duration :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Burning
  ! BUG: In the case of an attack skill that hits several foes, such as Whirlwind Attack, only one will be inflicted with burning, and not necessarily the one targeted by the attack.
Anthem of Fury #1553 | Elite Chant | Nightfall | E5 C1 R10
  For 10 seconds, all party members within earshot gain 2..5 strikes of adrenaline the next time they use an attack skill.
  ~ Adrenaline gain :: 0-4: 2 2 2 3 3 | 5-9: 3 3 3 4 4 | 10-14: 4 4 4 5 5 | 15-19: 5 5 5 6 6 | 20-21: 6 6
  # causes: Adrenaline Gain
Awe #1573 | Skill | Nightfall | E10 C¾ R10
  If this skill hits a knocked-down foe, that foe becomes Dazed for 5..15 seconds.
  ~ Dazed duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Dazed; target: foes
Blazing Finale (PvP) #3028 | Echo | Nightfall | E5 C1 R8
  For 10..35 seconds, whenever a chant or shout ends on target non-spirit ally, all foes adjacent to that ally are set on Fire for 1..5 second[s].
  ~ Duration :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  ~ Burning duration :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Burning; target: allies; aoe: adjacent
Burning Refrain #1576 | Echo | Nightfall | E10 C1 R10
  For 20 seconds, if target non-spirit ally hits a foe with more Health than that ally, that foe is set on Fire for 1..3 second[s]. This echo is reapplied every time a chant or shout ends on that ally.
  ~ Burning duration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Renewal, Burning; target: allies; aoe: None
Burning Shield #2208 | Skill | Eye of the North | E5 R20
  For 3..9 seconds, while wielding a shield, the next attack skill used against you is blocked. If it was a melee attack, your attacker is set on fire for 1..6 seconds.
  ~ Duration :: 0-4: 3 3 4 4 5 | 5-9: 5 5 6 6 7 | 10-14: 7 7 8 8 9 | 15-19: 9 9 10 10 11 | 20-21: 11 11
  ~ Burning duration :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  # causes: Block, Burning
Defensive Anthem (PvP) #2876 | Elite Chant | Nightfall | E15 C2 R15
  For 4..10 seconds, each party member within earshot has a 50% chance to block incoming attacks. This chant ends if that party member hits with an attack skill.
  ~ Duration :: 0-4: 4 4 5 5 6 | 5-9: 6 6 7 7 8 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 12
  # causes: Block
Enduring Harmony #1574 | Echo | Nightfall | E5 C1 R10
  For 10..35 seconds, chants and shouts last 50% longer on target non-spirit ally.
  ~ Duration :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  # target: allies
Focused Anger #1769 | Elite Skill | Nightfall | E10 R45
  For 45 seconds, you gain 0..150% more adrenaline.
  ~ Adrenaline gain % :: 0-4: 0 10 20 30 40 | 5-9: 50 60 70 80 90 | 10-14: 100 110 120 130 140 | 15-19: 150 160 170 180 190 | 20-21: 200 210
  # causes: Increased Adrenaline Build Rate
  ! ANOMALY: Unlike most skills that increase the rate of adrenaline gain by a multiplier, this increases all non-multiplier sources of adrenaline, not just the basic 1 strike from making an attack.
Glowing Signet #1581 | Signet | Nightfall | C¼ R15
  If target foe is Burning, you gain 5..15 Energy.
  ~ Energy gain :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Energy Gain
Hasty Refrain #2075 | Echo | Eye of the North | E5 C1 R10
  For 8..20 seconds, target ally moves 25% faster. This echo is reapplied every time a chant or shout ends on that ally.
  ~ Duration :: 0-4: 8 9 10 10 11 | 5-9: 12 13 14 14 15 | 10-14: 16 17 18 18 19 | 15-19: 20 21 22 22 23 | 20-21: 24 25
  # causes: Increased Movement Speed, Renewal; target: allies
  ! ANOMALY: Unlike the descriptions of other Echo skills, this skill's descriptions do not mention that it cannot target spirits.
Leader's Comfort #1584 | Skill | Nightfall | E5 C2 R8
  You gain 30..75 Health. For each ally within earshot, you also gain +10..20 Health (maximum 140 Health).
  ~ Healing :: 0-4: 30 33 36 39 42 | 5-9: 45 48 51 54 57 | 10-14: 60 63 66 69 72 | 15-19: 75 78 81 84 87 | 20-21: 90 93
  ~ + Healing :: 0-4: 10 11 11 12 13 | 5-9: 13 14 15 15 16 | 10-14: 17 17 18 19 19 | 15-19: 20 21 21 22 23 | 20-21: 23 24
  # causes: Healing; target: self
  ! BUG: Contrary to the descriptions, this skill causes healing and not health gain.
Natural Temper #1770 | Skill | Nightfall | Ad3
  For 4..15 seconds, you gain 33% more adrenaline while not under the effects of an Enchantment.
  ~ Duration :: 0-4: 4 5 5 6 7 | 5-9: 8 8 9 10 11 | 10-14: 11 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 19 19
  # causes: Increased Adrenaline Build Rate
Signet of Return (PvP) #3030 | Signet | Nightfall | C4 R20
  Resurrect target party member with 5..20% Health and 1..4% Energy for each party member within earshot.
  ~ % Health :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  ~ % Energy :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  ~ (5..20) [derived] :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # target: dead party members
Soldier's Fury #1773 | Elite Echo | Nightfall | E5 C1 R5
  For 10..35 seconds, if you are under the effects of a chant or a shout, you attack 33% faster and gain 33% more adrenaline, but you have -20 armor.
  ~ Duration :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  # causes: Increased Attack Speed, Increased Adrenaline Build Rate, Decreased Armor Rating
  ! BUG: Similar to Cracked Armor, this skill will not lower your armor rating below 60 or your "core" armor rating, if your "core" armor rating is lower than 60.
  ! BUG: If you use a skill or combination of skills and effects that grant +46 or more armor rating, Soldier's Fury's armor penalty does not function. See also armor calculation.
Spear Swipe #2210 | Spear Attack | Eye of the North | E5 R20
  If this attack hits, you deal +5..20 damage and target foe is Dazed for 4..10 seconds. This attack has melee range.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Dazed duration :: 0-4: 4 4 5 5 6 | 5-9: 6 6 7 7 8 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 12
  # causes: Dazed; range: touch
  ! ANOMALY: Contrary to what the concise description suggests, this is not a melee attack, but a spear attack with touch range. Skills such as Strength of Honor will not trigger. "Can't Touch This!" will protect against this skill.

### Paragon / Motivation
"It's Just a Flesh Wound." #1599 | Elite Shout | Nightfall | E5 R2
  Target other ally loses all conditions. If a condition was removed in this way, that ally moves 25% faster for 1..10 second[s].
  ~ Duration :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # causes: Increased Movement Speed; removes: Condition; target: other allies; aoe: None
  ! ANOMALY: If a condition is removed, Leadership will restore energy as if it affected two targets, requiring minimum 8 Leadership to receive the doubled benefit. This causes it to have a net cost of 1 energy.
"The Power Is Yours!" #1782 | Elite Shout | Nightfall | Ad4
  For 2..4 seconds, all allies within earshot gain 1..2 Energy regeneration.
  ~ Duration :: 0-4: 2 2 2 2 3 | 5-9: 3 3 3 3 3 | 10-14: 3 3 4 4 4 | 15-19: 4 4 4 4 5 | 20-21: 5 5
  ~ Energy regeneration :: 0-4: 1 1 1 1 1 | 5-9: 1 1 1 2 2 | 10-14: 2 2 2 2 2 | 15-19: 2 2 2 2 2 | 20-21: 2 2
  # causes: Energy Regeneration
Aria of Restoration #1566 | Chant | Nightfall | E10 C1 R10
  For 10 seconds, the next time each party member within earshot uses a spell, that party member gains 30..90 Health.
  ~ Health gain :: 0-4: 30 34 38 42 46 | 5-9: 50 54 58 62 66 | 10-14: 70 74 78 82 86 | 15-19: 90 94 98 102 106 | 20-21: 110 114
  # causes: Health Gain
Aria of Zeal #1562 | Chant | Nightfall | E5 C1 R10
  For 10 seconds, the next time each ally within earshot uses a Spell, that ally gains 1..6 Energy.
  ~ Energy gained :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  # causes: Energy Gain
Ballad of Restoration (PvP) #2877 | Chant | Nightfall | E10 C1 R20
  For 10 seconds, the next time each party member within earshot takes damage, that party member gains 15..75 Health.
  ~ Health gain :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  # causes: Health Gain
Chorus of Restoration #1565 | Chant | Nightfall | Ad4 C1 R5
  For 10 seconds, the next time each ally within earshot uses a shout or chant, that ally is healed for 30..90 Health.
  ~ Healing :: 0-4: 30 34 38 42 46 | 5-9: 50 54 58 62 66 | 10-14: 70 74 78 82 86 | 15-19: 90 94 98 102 106 | 20-21: 110 114
  # causes: Healing
Energizing Chorus #1569 | Chant | Nightfall | Ad3 C1
  For 10 seconds, the next Shout or Chant used by each ally within earshot costs 3..7 less Energy.
  ~ -Energy cost :: 0-4: 3 3 4 4 4 | 5-9: 4 5 5 5 5 | 10-14: 6 6 6 6 7 | 15-19: 7 7 8 8 8 | 20-21: 8 9
  # causes: Decreased Energy Cost; target: Allies; aoe: earshot
  ! ANOMALY: Because this chant reduces cost at the beginning of skill activation and doesn't end until activation is completed, using a shout in the middle of a chant's activation will allow both skills to benefit from this chant.
Energizing Finale #1775 | Echo | Nightfall | E10 C1 R5
  For 10..35 seconds, whenever a shout or chant ends on target non-spirit ally, that ally gains 1..2 Energy.
  ~ Duration :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  ~ Energy Gain :: 0-4: 1 1 1 1 1 | 5-9: 1 1 1 2 2 | 10-14: 2 2 2 2 2 | 15-19: 2 2 2 2 2 | 20-21: 2 2
  # causes: Energy Gain; target: other allies
Finale of Restoration (PvP) #3062 | Echo | Nightfall | E5 C1 R10
  For 10..35 seconds, the next 5 times that a chant or shout ends on target non-spirit ally, that ally is healed for 15..75 Health.
  ~ Duration :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  ~ Healing :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  # causes: Healing
  ! BUG: Contrary to the concise description, this skill causes healing and not health gain.
  ! BUG: Contrary to the concise description, this skill causes healing and not health gain. [from PvE version page]
Inspirational Speech #2207 | Skill | Eye of the North | E5 R10
  You lose all adrenaline and target other ally gains 1..8 strikes of adrenaline.
  ~ Adrenaline gain :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  # causes: Adrenaline Gain, Adrenaline Loss; target: other allies
  ! ANOMALY: Unlike most skills with zero activation time, this skill cannot be activated in the middle of another action and has a slight aftercast delay.
Leader's Zeal #1583 | Skill | Nightfall | E5 R12
  For each nearby ally, you gain 2..4 Energy (maximum 8..12 Energy).
  ~ Max energy per ally :: 0-4: 2 2 2 2 3 | 5-9: 3 3 3 3 3 | 10-14: 3 3 4 4 4 | 15-19: 4 4 4 4 5 | 20-21: 5 5
  ~ Max energy gained :: 0-4: 8 8 9 9 9 | 5-9: 9 10 10 10 10 | 10-14: 11 11 11 11 12 | 15-19: 12 12 13 13 13 | 20-21: 13 14
  # causes: Energy Gain; target: self
Lyric of Purification #1772 | Chant | Nightfall | E5 C1 R10
  For 5..20 seconds, the next time each ally within earshot uses a Signet, that ally loses 1 Condition.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # removes: Condition
Lyric of Zeal #1563 | Chant | Nightfall | Ad6 C1
  For 10 seconds, the next time each ally within earshot uses a signet, that ally gains 1..8 Energy.
  ~ Energy gain :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  # causes: Energy Gain
Mending Refrain (PvP) #3149 | Echo | Nightfall | E10 C1 R8
  For 15 seconds, you have +2..3 Health regeneration. This echo is reapplied every time a chant or shout ends on you.
  ~ Health regeneration :: 0-4: 2 2 2 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 3 3 | 15-19: 3 3 3 3 3 | 20-21: 3 3
  # causes: Health Regeneration, Renewal
Purifying Finale #1579 | Echo | Nightfall | E5 C¼ R5
  For 10..35 seconds, target non-spirit ally loses 1 condition whenever a chant or shout ends on that ally.
  ~ Duration :: 0-4: 10 12 13 15 17 | 5-9: 18 20 22 23 25 | 10-14: 27 28 30 32 33 | 15-19: 35 37 38 40 42 | 20-21: 43 45
  # removes: Condition; target: allies
Signet of Synergy #1585 | Signet | Nightfall | C1 R10
  Target other ally is healed for 40..100 Health. If you are not under the effects of an enchantment, you are also healed for 40..100 Health.
  ~ Healing :: 0-4: 40 44 48 52 56 | 5-9: 60 64 68 72 76 | 10-14: 80 84 88 92 96 | 15-19: 100 104 108 112 116 | 20-21: 120 124
  ~ Self heal :: 0-4: 40 44 48 52 56 | 5-9: 60 64 68 72 76 | 10-14: 80 84 88 92 96 | 15-19: 100 104 108 112 116 | 20-21: 120 124
  # causes: Healing; target: other allies
Song of Power #1560 | Chant | Nightfall | E15 C1 R30
  For 5..20 seconds, each ally within earshot gains 4 Energy regeneration until that ally uses a Skill.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Energy Regeneration
Song of Purification #1570 | Elite Chant | Nightfall | Ad3 C2
  For 20 seconds, the next 1..6 skill[s] used by each ally within earshot remove 1 condition from that ally.
  ~ Number of skills :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  # removes: Condition
  ! BUG: Re-application does not reset the number of uses remaining until the original application would have ended. It appears to count any skill uses against both applications, and the chant will end if the number of uses remaining from the original application reaches 0.
Song of Restoration (PvP) #2878 | Elite Chant | Nightfall | E10 C1 R20
  For 10 seconds, the next time each party member within earshot uses a skill, that party member gains 45..110 Health.
  ~ Health gain :: 0-4: 45 49 54 58 62 | 5-9: 67 71 75 80 84 | 10-14: 88 93 97 101 106 | 15-19: 110 114 119 123 127 | 20-21: 132 136
  # causes: Health Gain
Zealous Anthem #1561 | Chant | Nightfall | E10 C1 R10
  For 10 seconds, the next time each ally within earshot uses an attack skill, that ally gains 1..8 Energy.
  ~ Energy gain :: 0-4: 1 1 2 2 3 | 5-9: 3 4 4 5 5 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 11
  # causes: Energy Gain

### Paragon / No Attribute
Cautery Signet #1588 | Elite Signet | Nightfall | C2 R15
  All party members lose all conditions. You are set on Fire for 1 second for each condition removed in this way.
  # causes: Burning; removes: Condition; aoe: party
  ! ANOMALY: Although the effect extends beyond party range, the AI only considers allies within the expected range.
Hexbreaker Aria #1571 | Chant | Nightfall | Ad8 C2
  For 10 seconds, the next time each ally within earshot casts a spell, that ally loses 1 hex.
  # removes: Hex spell
Remedy Signet #1777 | Signet | Nightfall | C1 R4
  You lose 1 condition.
  # removes: Condition
Signet of Aggression #1776 | Signet | Nightfall | C1 R5
  If you are under the effects of a shout or chant, you gain 2 strikes of adrenaline.
  # causes: Adrenaline Gain
Song of Concentration #1567 | Chant | Nightfall | Ad8 C2 R5
  For 10 seconds, the next skill used by each ally within earshot cannot be interrupted.

### Paragon / Spear Mastery
Barbed Spear #1600 | Spear Attack | Nightfall | Ad2
  If this attack hits, your target begins Bleeding for 5..20 seconds.
  ~ Bleeding duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Bleeding
Blazing Spear #1546 | Spear Attack | Nightfall | Ad6
  If this attack hits, it deals +5..25 damage and sets target foe on Fire for 1..3 second[s].
  ~ + Damage :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  ~ Burning duration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Burning
Chest Thumper #2074 | Spear Attack | Eye of the North | E5 R5
  If this attack hits a foe with Cracked Armor, that foe suffers a Deep Wound for 5..20 seconds.
  ~ Deep Wound duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Deep Wound
Cruel Spear #1548 | Elite Spear Attack | Nightfall | Ad6
  If this attack hits, you deal +10..50 damage. If it hits a non-moving target, you inflict a Deep Wound for 5..20 seconds.
  ~ + Damage :: 0-4: 10 13 15 18 21 | 5-9: 23 26 29 31 34 | 10-14: 37 39 42 45 47 | 15-19: 50 53 55 58 61 | 20-21: 63 66
  ~ Deep Wound duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Deep Wound
Disrupting Throw #1604 | Spear Attack | Nightfall | E5 C½ R10
  If this attack hits a foe suffering from a condition, that foe is interrupted.
  # causes: Interrupt
Harrier's Toss (PvP) #2875 | Spear Attack | Nightfall | E10 C1 R10
  If this attack hits, you deal +5..20 damage. If this attack hits a moving foe, it deals an additional 5..40 damage.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Additional damage :: 0-4: 5 7 10 12 14 | 5-9: 17 19 21 24 26 | 10-14: 28 31 33 35 38 | 15-19: 40 42 45 47 49 | 20-21: 52 54
Holy Spear #2209 | Spear Attack | Eye of the North | Ad4
  If this attack hits, you deal +5..20 damage. If it hits a summoned creature, all nearby foes take 15..90 holy damage, and are set on fire for 3 seconds.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Holy damage :: 0-4: 15 20 25 30 35 | 5-9: 40 45 50 55 60 | 10-14: 65 70 75 80 85 | 15-19: 90 95 100 105 110 | 20-21: 115 120
  # causes: Holy Damage, Burning; target: foes; aoe: nearby
  ! BUG: If the summoned creature Holy Spear is used on turns allied while the projectile is mid-flight, the extra AoE effect will still trigger but the attack will not register on the minion.
Maiming Spear #2150 | Spear Attack | Eye of the North | E5 R5
  If your attack hits a Bleeding foe, that foe is Crippled for 5..20 seconds.
  ~ Crippled duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Crippled
Merciless Spear #1603 | Spear Attack | Nightfall | Ad6
  If this attack hits a foe with less than 50% Health, that foe suffers from a Deep Wound for 5..20 seconds.
  ~ Deep Wound duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Deep Wound
Mighty Throw (PvP) #3442 | Spear Attack | Nightfall | Ad4 C1 R1
  Your spear moves three times faster. If it hits, you deal +10..40 damage.
  ~ + Damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Increased Projectile Speed
Slayer's Spear #1783 | Spear Attack | Nightfall | E10 R4
  If this attack hits, you deal +5..25 damage. If that foe has more Health than you, that foe suffers from a Deep Wound for 5..20 seconds.
  ~ + Damage :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  ~ Deep Wound duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Deep Wound
Spear of Lightning #1551 | Spear Attack | Nightfall | E5 R6
  Strikes all foes between you and your target. If this attack hits, it deals +10..20 lightning damage. This attack has 25% armor penetration.
  ~ + Lightning damage :: 0-4: 10 11 11 12 13 | 5-9: 13 14 15 15 16 | 10-14: 17 17 18 19 19 | 15-19: 20 21 21 22 23 | 20-21: 23 24
  # causes: Lightning Damage, Armor Penetration
Spear of Redemption #2238 | Spear Attack | Eye of the North | Ad3
  If this attack hits, you deal +5..20 damage. If it fails to hit, you lose one condition.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # removes: condition
Stunning Strike #1602 | Elite Spear Attack | Nightfall | Ad8
  If this attack hits, you deal +10..50 damage. If it hits a foe suffering from a condition, that foe is also Dazed for 4..10 seconds.
  ~ + Damage :: 0-4: 10 13 15 18 21 | 5-9: 23 26 29 31 34 | 10-14: 37 39 42 45 47 | 15-19: 50 53 55 58 61 | 20-21: 63 66
  ~ Dazed duration :: 0-4: 4 4 5 5 6 | 5-9: 6 6 7 7 8 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 12
  # causes: Dazed
Swift Javelin #1784 | Spear Attack | Nightfall | E5 R10
  If this attack hits, you deal +5..20 damage. If you are under the effects of an enchantment, this spear flies twice as fast and cannot be blocked.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Unblockable, Increased Projectile Speed
Unblockable Throw #1550 | Spear Attack | Nightfall | Ad6 C1 R1
  If this attack hits, you deal +10..40 damage. This attack cannot be blocked.
  ~ + Damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Unblockable
Vicious Attack #1601 | Spear Attack | Nightfall | E5 R8
  If this attack hits, you deal +5..20 damage. If you land a critical hit with this attack, target foe suffers from a Deep Wound for 5..15 seconds.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Deep Wound duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Deep Wound
Wearying Spear #1552 | Spear Attack | Nightfall | Ad3
  If this attack hits, you deal +10..40 damage. You are Weakened for 5 seconds.
  ~ + Damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Weakness
Wild Throw #1605 | Spear Attack | Nightfall | Ad7
  If this attack hits, it deals +5..20 damage, and any stance being used by your target ends. This attack cannot be blocked. All of your non-spear attack skills are disabled for 3 seconds.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Unblockable, Disable; removes: Stance

## Dervish

### Dervish / Earth Prayers
Armor of Sanctity #1515 | Enchantment Spell | Nightfall | E5 C¼ R15
  All adjacent foes suffer from Weakness for 5..15 seconds. For 15 seconds, you take 5..20 less damage from foes suffering from a condition.
  ~ Weakness duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  ~ Damage reduction :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Weakness, Damage Reduction; target: untargeted; aoe: adjacent
Aura of Thorns (PvP) #3346 | Flash Enchantment Spell | Nightfall | E10 R10
  All nearby foes begin Bleeding for 5..15 seconds. For 30 seconds, this enchantment does nothing. When this enchantment ends, all nearby foes are Crippled for 3..8 seconds.
  ~ Bleeding duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  ~ Crippled duration :: 0-4: 3 3 4 4 4 | 5-9: 5 5 5 6 6 | 10-14: 6 7 7 7 8 | 15-19: 8 8 9 9 9 | 20-21: 10 10
  # causes: Crippled, Bleeding; aoe: nearby
Conviction #1540 | Flash Enchantment Spell | Nightfall | E5 R10
  For 10 seconds, you gain +10 armor if you have a condition and gain 1..3 Health regen for each condition you are suffering from. When this enchantment ends, you are cured of 1..2 condition[s].
  ~ Health regeneration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  ~ Conditions removed :: 0-4: 1 1 1 1 1 | 5-9: 1 1 1 2 2 | 10-14: 2 2 2 2 2 | 15-19: 2 2 2 2 2 | 20-21: 2 2
  # causes: Increased Armor Rating, Health Regeneration; removes: Condition
Dust Cloak (PvP) #3347 | Flash Enchantment Spell | Nightfall | E10 R10
  All adjacent foes are struck for 10..40 earth damage. For 30 seconds, your attacks deal earth damage. When this enchantment ends, all adjacent foes are Blinded for 1..4 second[s].
  ~ Earth damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  ~ Blind duration :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  # causes: Earth Damage, Blind; aoe: adjacent
Ebon Dust Aura #1760 | Elite Flash Enchantment Spell | Nightfall | E10 R20
  When you cast this enchantment, all nearby foes are Blinded for 1..7 second[s]. For 30 seconds, if you are wielding an earth weapon, your melee attacks deal +3..30 earth damage. When this enchantment ends, you are cured of Blindness.
  ~ + Earth damage :: 0-4: 3 5 7 8 10 | 5-9: 12 14 16 17 19 | 10-14: 21 23 25 26 28 | 15-19: 30 32 34 35 37 | 20-21: 39 41
  ~ Blind duration :: 0-4: 1 1 2 2 3 | 5-9: 3 3 4 4 5 | 10-14: 5 5 6 6 7 | 15-19: 7 7 8 8 9 | 20-21: 9 9
  # causes: Blind, Earth Damage; removes: Condition; target: untargeted; aoe: nearby
Fleeting Stability (PvP) #3470 | Flash Enchantment Spell | Nightfall | E5 R10
  For 2..8 seconds, you cannot be knocked down and move 25% faster. This enchantment ends prematurely if it prevents a knockdown.
  ~ Duration :: 0-4: 2 2 3 3 4 | 5-9: 4 4 5 5 6 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 10
  # causes: Knockdown Immunity, Increased Movement Speed
Mirage Cloak (PvP) #3469 | Flash Enchantment Spell | Nightfall | E10 R15
  For 1..7 second[s], you have a 30..60% chance to block incoming attacks. When you cast this enchantment, all nearby foes are struck for 10..40 earth damage.
  ~ Duration :: 0-4: 1 1 2 2 3 | 5-9: 3 3 4 4 5 | 10-14: 5 5 6 6 7 | 15-19: 7 7 8 8 9 | 20-21: 9 9
  ~ Chance to block :: 0-4: 30 32 34 36 38 | 5-9: 40 42 44 46 48 | 10-14: 50 52 54 56 58 | 15-19: 60 62 64 66 68 | 20-21: 70 72
  ~ Earth damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Block, Earth Damage; target: untargeted; aoe: nearby
  ! ANOMALY: With skills that remove "all enchantments" (such as Contemplation of Purity), the only Dervish enchantments this skill's damage can trigger for are Aura of Thorns, Balthazar's Rage, Pious Renewal, Dust Cloak, Staggering Force, Grenth's Fingers, and Mirage Cloak itself. By contrast, there is no restriction on which Dervish enchantments will trigger damage if a specific number of enchantments is removed (such as by Rend Enchantments or Dervish teardowns), as long as they cover Mirage Cloak (plus Mirage Cloak itself). [from PvE version page]
  ! BUG: The concise description omits that block chance is capped to 80%. [from PvE version page]
Mystic Regeneration (PvP) #2884 | Enchantment Spell | Nightfall | E15 C¼ R15
  For 5..20 seconds, you have +1..4 Health regeneration for each enchantment (maximum of 3) on you.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Health regeneration :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  # causes: Health Regeneration; target: self
Mystic Sandstorm #1532 | Spell | Nightfall | Ad5 C1 R8
  Create a sandstorm at your location that lasts 3 seconds. Each second, foes nearby this location take 10..40 earth damage. Attacking foes take an additional 10..20 damage. If you are enchanted when you cast this spell, it lasts twice as long.
  ~ unconditional Earth damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  ~ conditional Earth damage :: 0-4: 10 11 11 12 13 | 5-9: 13 14 15 15 16 | 10-14: 17 17 18 19 19 | 15-19: 20 21 21 22 23 | 20-21: 23 24
  # causes: Earth Damage; target: untargeted; aoe: nearby
Pious Concentration #1542 | Stance | Nightfall | E10 R10
  For 5..20 seconds, you cannot be interrupted, but each time you would have been interrupted, you lose 1 Dervish enchantment or Pious Concentration ends.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # removes: Enchantment
Sand Shards #1510 | Flash Enchantment Spell | Nightfall | E10 R10
  For 30 seconds, the next 1..5 time[s] you hit with a scythe, all other adjacent foes take 10..60 earth damage.
  ~ Attacks affected :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  ~ Earth damage :: 0-4: 10 13 17 20 23 | 5-9: 27 30 33 37 40 | 10-14: 43 47 50 53 57 | 15-19: 60 63 67 70 73 | 20-21: 77 80
  # causes: Earth Damage; target: untargeted; aoe: adjacent
Shield of Force #2201 | Flash enchantment spell | Eye of the North | E10 R12
  For 1..16 second[s], blocks the next 1 attack against you. If an attack is blocked, all adjacent attacking foes are knocked down and suffer from Weakness for 5..20 seconds.
  ~ Duration :: 0-4: 1 2 3 4 5 | 5-9: 6 7 8 9 10 | 10-14: 11 12 13 14 15 | 15-19: 16 17 18 19 20 | 20-21: 21 22
  ~ Weakness duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Block, Weakness, Knockdown; target: untargeted; aoe: adjacent
Signet of Pious Light #1530 | Signet | Nightfall | C1 R20
  Remove 1 Dervish enchantment. Target ally is healed for 30..150 Health. If an enchantment was removed in this way, this signet recharges 75% faster.
  ~ Healing :: 0-4: 30 38 46 54 62 | 5-9: 70 78 86 94 102 | 10-14: 110 118 126 134 142 | 15-19: 150 158 166 174 182 | 20-21: 190 198
  # causes: Healing, Decreased Recharge Time; removes: Enchantment; target: allies; range: Casting
  ! ANOMALY: As long as the user is under the effects of a Dervish enchantment when attempting to activate this skill, Signet of Pious Light will recharge in 5 seconds, regardless of other effects.
Staggering Force #1498 | Flash Enchantment Spell | Nightfall | E10 R6
  All nearby foes are struck for 10..40 earth damage. For 30 seconds, your attacks deal earth damage. When this enchantment ends, all nearby foes have Cracked Armor for 1..10 second[s].
  ~ Earth damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  ~ Cracked Armor duration :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # causes: Earth Damage, Cracked Armor; target: untargeted; aoe: nearby
Veil of Thorns #1757 | Flash Enchantment Spell | Nightfall | E10 R15
  When you cast this enchantment, all nearby foes are struck for 5..50 piercing damage. For 5..25 seconds you take 5..35% less damage from spells.
  ~ Duration :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  ~ Piercing damage :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  ~ Spell damage reduction :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  # causes: Damage Reduction, Piercing Damage; target: untargeted; aoe: nearby
Vital Boon #1506 | Enchantment Spell | Nightfall | E5 C1 R8
  For 20 seconds, you have +40..100 maximum Health. When this enchantment ends, you are healed for 75..200 Health.
  ~ + Max health :: 0-4: 40 44 48 52 56 | 5-9: 60 64 68 72 76 | 10-14: 80 84 88 92 96 | 15-19: 100 104 108 112 116 | 20-21: 120 124
  ~ Health gain :: 0-4: 75 83 92 100 108 | 5-9: 117 125 133 142 150 | 10-14: 158 167 175 183 192 | 15-19: 200 208 217 225 233 | 20-21: 242 250
  # causes: Increased Maximum Health, Health Gain; target: self
  ! BUG: Contrary to the descriptions, this skill causes health gain and not healing.
Vow of Strength #1759 | Elite Enchantment Spell | Nightfall | E5 C¼ R20
  For 15 seconds, whenever you attack a foe with your scythe, you deal 10..25 slashing damage to all adjacent foes.
  ~ Slashing damage :: 0-4: 10 11 12 13 14 | 5-9: 15 16 17 18 19 | 10-14: 20 21 22 23 24 | 15-19: 25 26 27 28 29 | 20-21: 30 31
  # causes: Slashing Damage; target: untargeted; aoe: adjacent

### Dervish / Mysticism
Arcane Zeal #1502 | Elite Enchantment Spell | Nightfall | E10 C1 R5
  For 10 seconds, whenever you cast a spell, you gain 2 Energy for each enchantment on you (maximum 2..7 Energy).
  ~ Maximum Energy gain :: 0-4: 2 2 3 3 3 | 5-9: 4 4 4 5 5 | 10-14: 5 6 6 6 7 | 15-19: 7 7 8 8 8 | 20-21: 9 9
  # causes: Energy Gain; target: self
  ! BUG: This skill currently only grants 1 energy per enchantment
Aura Slicer (PvP) #3473 | Melee Attack | Eye of the North | Ad5
  If this attack hits, you inflict Bleeding for 5..15 seconds. If you are enchanted, you also inflict Cracked Armor for 1..10 second[s].
  ~ Bleeding duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  ~ Cracked Armor duration :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # causes: Bleeding, Cracked Armor
Avatar of Balthazar #1518 | Elite Form | Nightfall | E5 C2 R20
  For 10..90 seconds, you gain +20 armor against physical damage, you gain adrenaline 25% faster, your attacks deal holy damage, and whenever you lose a Dervish enchantment, nearby foes are set on fire for 1..3 second[s]. This skill is disabled for 45 seconds.
  ~ Duration :: 0-4: 10 15 21 26 31 | 5-9: 37 42 47 53 58 | 10-14: 63 69 74 79 85 | 15-19: 90 95 101 106 111 | 20-21: 117 122
  ~ Burning duration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Burning, Holy Damage, Increased Adrenaline Build Rate, Disable, Increased Armor Rating; target: untargeted; aoe: nearby
Avatar of Dwayna (PvP) #3270 | Elite Form | Nightfall | E5 C2 R20
  For 10..90 seconds, your attacks deal holy damage. Whenever you use a Dervish attack skill, you lose 1 hex. Whenever you lose a Dervish enchantment, you are healed for 5..50 Health. This skill is disabled for 45 seconds.
  ~ Duration :: 0-4: 10 15 21 26 31 | 5-9: 37 42 47 53 58 | 10-14: 63 69 74 79 85 | 15-19: 90 95 101 106 111 | 20-21: 117 122
  ~ Healing :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Holy Damage, Healing, Disable; removes: Hex spell
Avatar of Grenth #1520 | Elite Form | Nightfall | E5 C2 R20
  For 10..90 seconds, your scythe attacks deal dark damage, and steal 0..12 Health. You are immune to Disease, and inflict Disease on all adjacent foes for 3 seconds whenever you lose a Dervish enchantment. This skill is disabled for 45 seconds.
  ~ Duration :: 0-4: 10 15 21 26 31 | 5-9: 37 42 47 53 58 | 10-14: 63 69 74 79 85 | 15-19: 90 95 101 106 111 | 20-21: 117 122
  ~ Life stealing :: 0-4: 0 1 2 2 3 | 5-9: 4 5 6 6 7 | 10-14: 8 9 10 10 11 | 15-19: 12 13 14 14 15 | 20-21: 16 17
  # causes: Dark Damage, Life Stealing, Disease, Condition Immunity, Disable; target: untargeted; aoe: adjacent
Avatar of Lyssa #1521 | Elite Form | Nightfall | E5 C2 R20
  For 10..90 seconds, your Dervish enchantments recharge 50% faster and your attacks deal chaos damage. Whenever you lose a Dervish enchantment, steal 1 Energy from all nearby foes. This skill is disabled for 45 seconds.
  ~ Duration :: 0-4: 10 15 21 26 31 | 5-9: 37 42 47 53 58 | 10-14: 63 69 74 79 85 | 15-19: 90 95 101 106 111 | 20-21: 117 122
  # causes: Chaos Damage, Energy Stealing, Decreased Recharge Time, Disable; target: untargeted; aoe: nearby
Avatar of Melandru (PvP) #3271 | Elite Form | Nightfall | E5 C2 R20
  For 10..90 seconds, you have +100 Health, +30 elemental armor, and your attacks deal earth damage. Whenever you lose a Dervish enchantment you lose 2 conditions. This skill is disabled for 45 seconds.
  ~ Duration :: 0-4: 10 15 21 26 31 | 5-9: 37 42 47 53 58 | 10-14: 63 69 74 79 85 | 15-19: 90 95 101 106 111 | 20-21: 117 122
  # causes: Increased Maximum Health, Increased Armor Rating, Earth Damage, Disable; removes: Condition; target: self
Balthazar's Rage #1496 | Flash Enchantment Spell | Nightfall | E10 R10
  All nearby foes are set on fire for 1..3 second[s]. For 20 seconds afterward, this enchantment does nothing. When this enchantment ends, you gain 1..2 strike[s] of adrenaline if any foes are within earshot.
  ~ Burning duration :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  ~ Adrenaline gain :: 0-4: 1 1 1 1 1 | 5-9: 1 1 1 2 2 | 10-14: 2 2 2 2 2 | 15-19: 2 2 2 2 2 | 20-21: 2 2
  # causes: Burning, Adrenaline Gain; target: untargeted; aoe: nearby
  ! ANOMALY: Similar to other skills with an end effect, the end effect of Balthazar's Rage will trigger upon death. When a character who died while enchanted with Balthazar's Rage is resurrected, the adrenaline gained from this skill's end effect will still be active on the character, instead of having no adrenaline when resurrected.
Banishing Strike (PvP) #3263 | Melee Attack | Nightfall | E5 R3
  If it hits, this attack deals 10..60 holy damage. It deals double damage to summoned creatures.
  ~ Holy damage :: 0-4: 10 13 17 20 23 | 5-9: 27 30 33 37 40 | 10-14: 43 47 50 53 57 | 15-19: 60 63 67 70 73 | 20-21: 77 80
  # causes: Holy Damage
Eremite's Zeal #1524 | Enchantment spell | Nightfall | E5 C¼ R15
  You gain 1..3 Energy for each foe within earshot, maximum 8 Energy. For 10 seconds afterward, this enchantment does nothing. When this enchantment ends, you gain 1..3 Energy for each foe within earshot, maximum 8 Energy.
  ~ Energy gain :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Energy Gain; target: self
  ! BUG: Heroes don't use this skill unless enchanted.
Extend Enchantments #1508 | Skill | Nightfall | E5 R10
  For 10 seconds, your next Dervish enchantment lasts 10..150% longer.
  ~ + Enchantment % duration :: 0-4: 10 19 29 38 47 | 5-9: 57 66 75 85 94 | 10-14: 103 113 122 131 141 | 15-19: 150 159 169 178 187 | 20-21: 197 206
  ! BUG: The visual indicator of the maximum duration on the skill icon of Vow of Piety and Vow of Revolution in the skill monitor is not full after renewal if they were extended before.
Faithful Intervention #1509 | Enchantment Spell | Nightfall | E5 C2 R20
  If damage drops your Health below 50%, Faithful Intervention ends. When Faithful Intervention ends, you are healed for 30..150 Health.
  ~ Healing :: 0-4: 30 38 46 54 62 | 5-9: 70 78 86 94 102 | 10-14: 110 118 126 134 142 | 15-19: 150 158 166 174 182 | 20-21: 190 198
  # causes: Healing
  ! BUG: Contrary to the concise description, this skill causes healing and not health gain. It also fails to mention that the healing is an end effect.
Heart of Fury (PvP) #3366 | Stance | Nightfall | Ad4 R6
  For 2..10 seconds, you attack 25% faster.
  ~ Duration :: 0-4: 2 3 3 4 4 | 5-9: 5 5 6 6 7 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 13
  # causes: Increased Attack Speed
Heart of Holy Flame #1507 | Flash Enchantment Spell | Nightfall | E10 R10
  All nearby foes take 5..30 holy damage. For 30 seconds, your attacks deal holy damage. When this enchantment ends, all nearby foes are set on fire for 2..5 seconds.
  ~ Holy damage :: 0-4: 5 7 8 10 12 | 5-9: 13 15 17 18 20 | 10-14: 22 23 25 27 28 | 15-19: 30 32 33 35 37 | 20-21: 38 40
  ~ Burning duration :: 0-4: 2 2 2 3 3 | 5-9: 3 3 3 4 4 | 10-14: 4 4 4 5 5 | 15-19: 5 5 5 6 6 | 20-21: 6 6
  # causes: Burning, Holy Damage; target: untargeted; aoe: nearby
Imbue Health #1526 | Spell | Nightfall | E10 C¼ R10
  Target other ally is healed for 5..50% of your current Health (maximum 300 Health).
  ~ % Healing :: 0-4: 5 8 11 14 17 | 5-9: 20 23 26 29 32 | 10-14: 35 38 41 44 47 | 15-19: 50 53 56 59 62 | 20-21: 65 68
  # causes: Healing; target: other allies
Intimidating Aura #1531 | Enchantment Spell | Nightfall | E10 C¾ R20
  For 60 seconds, you have +40..100 max Health and take 1..10 less damage from foes with less Health than you.
  ~ + Maximum health :: 0-4: 40 44 48 52 56 | 5-9: 60 64 68 72 76 | 10-14: 80 84 88 92 96 | 15-19: 100 104 108 112 116 | 20-21: 120 124
  ~ Damage reduction :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # causes: Increased Maximum Health, Damage Reduction; target: self
Meditation #1523 | Enchantment Spell | Nightfall | E10 C¼ R15
  Lose all adrenaline. For 20 seconds, you gain 1..4 Energy every time an enchantment on you ends.
  ~ Energy gain :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  # causes: Adrenaline Loss, Energy Gain; target: self
Mystic Corruption (PvP) #3467 | Flash enchantment spell | Nightfall | E5 R10
  All adjacent foes suffer from Disease for 2..6 second[s]. For 20 seconds, nothing happens. Disease duration is doubled if you are enchanted when you activate this skill. When this enchantment ends, all party members in earshot are cured of Disease.
  ~ Disease duration :: 0-4: 2 2 3 3 3 | 5-9: 3 4 4 4 4 | 10-14: 5 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 7 8
  # causes: Disease; removes: Condition; target: untargeted; aoe: earshot
Mystic Sweep #1484 | Melee Attack | Nightfall | E5 C1 R6
  If this attack hits, you deal +3..12 damage. If you are enchanted, this attack deals an additional +3..12 damage.
  ~ + Damage :: 0-4: 3 4 4 5 5 | 5-9: 6 7 7 8 8 | 10-14: 9 10 10 11 11 | 15-19: 12 13 13 14 14 | 20-21: 15 16
Mystic Vigor #1503 | Enchantment Spell | Nightfall | E5 C¼ R15
  For 20 seconds, every time you successfully hit with an attack, you gain 3..15 Health for each enchantment on you (maximum 25 Health).
  ~ Health gain :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Health Gain
Pious Fury (PvP) #3368 | Stance | Eye of the North | E5 R15
  Remove one Dervish enchantment. For 1..5 second[s], you attack 25% faster. If an enchantment was removed, this stance lasts twice as long.
  ~ Duration :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Increased Attack Speed; removes: Enchantment; aoe: none
Pious Haste #1543 | Stance | Nightfall | E5 R12
  You remove 1 Dervish enchantment and for 1..7 second[s] you move 25% faster. If an enchantment was removed you move 50% faster instead.
  ~ Duration :: 0-4: 1 1 2 2 3 | 5-9: 3 3 4 4 5 | 10-14: 5 5 6 6 7 | 15-19: 7 7 8 8 9 | 20-21: 9 9
  # causes: Increased Movement Speed; removes: Enchantment; aoe: none
  ! BUG: If your Mysticism is at 0, the skill will still remove an enchantment but only give 25% move speed instead of 50%.
Pious Renewal #1499 | Elite Flash Enchantment Spell | Nightfall | E5 R8
  For 8 seconds, nothing happens. When this enchantment ends, Pious Renewal is recharged and you gain 0..5 Energy and 0..30 Health.
  ~ Energy gain :: 0-4: 0 0 1 1 1 | 5-9: 2 2 2 3 3 | 10-14: 3 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 7 7
  ~ Health gain :: 0-4: 0 2 4 6 8 | 5-9: 10 12 14 16 18 | 10-14: 20 22 24 26 28 | 15-19: 30 32 34 36 38 | 20-21: 40 42
  # causes: Recharge, Energy Gain, Health Gain; target: self
Rending Touch #1534 | Touch spell | Nightfall | E5 C¾ R12
  Spell. Deals 15..65 cold damage to target foe. You lose one Dervish enchantment. If an enchantment was removed, target foe loses 1 enchantment and you gain 2 strikes of adrenaline.
  ~ Cold damage :: 0-4: 15 18 22 25 28 | 5-9: 32 35 38 42 45 | 10-14: 48 52 55 58 62 | 15-19: 65 68 72 75 78 | 20-21: 82 85
  # causes: Cold Damage, Adrenaline Gain; removes: Enchantment; target: foes; range: touch
  ! ANOMALY: The cold damage dealt by this skill is armor-ignoring.
  ! BUG: The full description fails to mention that this spell has a touch range (the concise description is correct).
Vow of Silence #1517 | Elite Enchantment Spell | Nightfall | E5 C¼ R10
  For 5..10 seconds, you cannot be the target of spells, and you cannot cast spells.
  ~ Duration :: 0-4: 5 5 6 6 6 | 5-9: 7 7 7 8 8 | 10-14: 8 9 9 9 10 | 15-19: 10 10 11 11 11 | 20-21: 12 12
Watchful Intervention #1504 | Enchantment Spell | Nightfall | E10 C1 R15
  For 60 seconds, the next time damage drops target ally's Health below 25%, that ally is healed for 50..200 Health.
  ~ Healing :: 0-4: 50 60 70 80 90 | 5-9: 100 110 120 130 140 | 10-14: 150 160 170 180 190 | 15-19: 200 210 220 230 240 | 20-21: 250 260
  # causes: Healing; target: allies
Zealous Renewal #1763 | Flash Enchantment Spell | Nightfall | E5 R10
  All nearby foes take 5..30 holy damage. For 5..25 seconds, you have -1 Energy regeneration, and gain 1 Energy whenever you hit a foe. If this enchantment ends prematurely, you gain 1..5 Energy.
  ~ Holy damage :: 0-4: 5 7 8 10 12 | 5-9: 13 15 17 18 20 | 10-14: 22 23 25 27 28 | 15-19: 30 32 33 35 37 | 20-21: 38 40
  ~ Duration :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  ~ Energy gain :: 0-4: 1 1 2 2 2 | 5-9: 2 3 3 3 3 | 10-14: 4 4 4 4 5 | 15-19: 5 5 6 6 6 | 20-21: 6 7
  # causes: Holy Damage, Energy Degeneration, Energy Gain; target: untargeted; aoe: nearby

### Dervish / No Attribute
Enchanted Haste #1541 | Flash Enchantment Spell | Nightfall | E10 R15
  For 7 seconds, you move 25% faster. If this enchantment ends prematurely, you lose 1 condition.
  # causes: Increased Movement Speed; removes: Condition

### Dervish / Scythe Mastery
Chilling Victory #1539 | Scythe Attack | Nightfall | Ad6
  If it hits, this attack strikes for +3..15 damage. For each foe hit who has less Health than you, that foe and all adjacent foes are struck for 10..30 cold damage.
  ~ + Damage :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  ~ Cold damage :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  # causes: Cold Damage; target: foes; aoe: adjacent
Crippling Sweep #1535 | Scythe Attack | Nightfall | E5 R6
  If this attack hits a foe, that foe is Crippled for 3..12 seconds. This skill deals +3..15 extra damage if that foe is moving.
  ~ Crippled duration :: 0-4: 3 4 4 5 5 | 5-9: 6 7 7 8 8 | 10-14: 9 10 10 11 11 | 15-19: 12 13 13 14 14 | 20-21: 15 16
  ~ + Damage :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Crippled
Crippling Victory #2147 | Scythe Attack | Eye of the North | Ad6
  If this attack hits a foe, that foe is Crippled for 3..8 seconds. If you have more Health than target foe, all adjacent foes take 10..30 earth damage.
  ~ Crippled duration :: 0-4: 3 3 4 4 4 | 5-9: 5 5 5 6 6 | 10-14: 6 7 7 7 8 | 15-19: 8 8 9 9 9 | 20-21: 10 10
  ~ Earth damage :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  # causes: Crippled, Earth Damage; target: foes; aoe: adjacent
Eremite's Attack #1485 | Scythe Attack | Nightfall | E5 R6
  If it hits, this attack deals +1..10 damage and removes a Dervish enchantment. If an enchantment is removed, you do an additional +1..10 damage and strike all adjacent foes.
  ~ + Damage :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # removes: Enchantment; target: foes; aoe: adjacent
  ! BUG: The full description is incorrect: a Dervish enchantment is removed even if this attack fails to hit.
Farmer's Scythe (PvP) #3437 | Scythe Attack | Eye of the North | E5 R20
  If this attack hits, you deal +5..35 damage. If you hit more than one foe, this attack recharges instantly.
  ~ + Damage :: 0-4: 5 7 9 11 13 | 5-9: 15 17 19 21 23 | 10-14: 25 27 29 31 33 | 15-19: 35 37 39 41 43 | 20-21: 45 47
  # causes: Recharge
  ! BUG: The recharge effect will occur if you attack more than one foe; thus, this skill will recharge even if you miss or are blocked.
  ! BUG: The recharge effect will occur if you attack more than one foe; thus, this skill will recharge even if you miss or are blocked. [from PvE version page]
Irresistible Sweep (PvP) #3265 | Scythe Attack | Nightfall | Ad5
  Deal +3..15 damage and lose 1 Dervish enchantment. If you lose an enchantment in this way, Irresistible Sweep cannot be blocked and removes a stance.
  ~ + Damage :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Unblockable; removes: Enchantment, Stance
Lyssa's Assault #1538 | Scythe Attack | Nightfall | E5 C½ R15
  This attack interrupts an action if it hits. If you are enchanted, any skill you interrupt is disabled for additional 1..10 second[s]. This attack does 50% normal damage.
  ~ Disable duration :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # causes: Interrupt, Disable
Pious Assault (PvP) #3266 | Melee Attack | Nightfall | E5 R12
  You remove 1 Dervish enchantment. If a Dervish enchantment was removed, this skill recharges 75% faster and adjacent foes take 15..40 damage.
  ~ Damage :: 0-4: 15 17 18 20 22 | 5-9: 23 25 27 28 30 | 10-14: 32 33 35 37 38 | 15-19: 40 42 43 45 47 | 20-21: 48 50
  # causes: Decreased Recharge Time; removes: Enchantment; aoe: adjacent
  ! ANOMALY: As long as the user is under the effects of a Dervish enchantment when attempting to activate this skill, Pious Assault will recharge in 3 seconds, regardless of other effects (such as Diversion or Shield Bash). [from PvE version page]
Radiant Scythe #2012 | Scythe Attack | Eye of the North | Ad6
  This attack strikes for +1 damage for each point of Energy you currently have, maximum 5..30. You gain 1..7 Energy if this attack hits.
  ~ Maximum +damage :: 0-4: 5 7 8 10 12 | 5-9: 13 15 17 18 20 | 10-14: 22 23 25 27 28 | 15-19: 30 32 33 35 37 | 20-21: 38 40
  ~ Energy gain :: 0-4: 1 1 2 2 3 | 5-9: 3 3 4 4 5 | 10-14: 5 5 6 6 7 | 15-19: 7 7 8 8 9 | 20-21: 9 9
  # causes: Energy Gain
  ! BUG: Despite the phrasing of the full description, the energy gain occurs even if the attack fails to hit (as correctly noted in the concise description).
Reap Impurities #1486 | Melee Attack | Nightfall | Ad5
  If this attack hits, you deal +3..15 damage. Each foe you hit loses 1 condition. For each foe who loses a condition, all foes adjacent to that target foe take 10..40 holy damage.
  ~ + Damage :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  ~ Holy damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  # causes: Holy Damage; removes: Condition; target: foes; aoe: adjacent
  ! BUG: The holy damage is dealt to other foes adjacent to yourself, not adjacent to the target.
Reaper's Sweep #1767 | Elite Scythe Attack | Nightfall | Ad7
  If this attack hits, you Cripple your target for 3..15 seconds. You lose 1 Dervish enchantment. If an enchantment was removed, this attack knocks down for 2..3 seconds.
  ~ Cripple duration :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  ~ Knock down duration :: 0-4: 2 2 2 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 3 3 | 15-19: 3 3 3 3 3 | 20-21: 3 3
  # causes: Crippled, Knockdown; removes: Enchantment
Rending Sweep #1753 | Scythe attack | Nightfall | Ad6
  You deal +5..20 and lose 1 Dervish enchantment. If an enchantment was lost, you remove an enchantment from each foe you hit.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # removes: Enchantment
Twin Moon Sweep (PvP) #3264 | Melee Attack | Nightfall | Ad7
  You lose 1 Dervish enchantment and gain 10..20 Health. If an enchantment is lost in this way, you cannot be blocked, you strike twice, with each strike doing 25% less damage than normal, and you gain an additional 10..30 Health.
  ~ Health gain :: 0-4: 10 11 11 12 13 | 5-9: 13 14 15 15 16 | 10-14: 17 17 18 19 19 | 15-19: 20 21 21 22 23 | 20-21: 23 24
  ~ Additional health gain :: 0-4: 10 11 13 14 15 | 5-9: 17 18 19 21 22 | 10-14: 23 25 26 27 29 | 15-19: 30 31 33 34 35 | 20-21: 37 38
  # causes: Health Gain, Unblockable; removes: Enchantment
  ! ANOMALY: The concise description incorrectly states the target is attacked twice, instead of hit twice. [from PvE version page]
Victorious Sweep #1488 | Melee Attack | Nightfall | E5 R4
  If this attack hits, you deal +5..25 damage. If target foe has less Health than you, you gain 30..80 Health.
  ~ + Damage :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  ~ Health gain :: 0-4: 30 33 37 40 43 | 5-9: 47 50 53 57 60 | 10-14: 63 67 70 73 77 | 15-19: 80 83 87 90 93 | 20-21: 97 100
  # causes: Health Gain
Wearying Strike #1537 | Scythe Attack | Nightfall | Ad6
  You remove 1 Dervish enchantment. If an enchantment was removed, you inflict a Deep Wound for 3..10 seconds. You suffer from Weakness for 10 seconds if an enchantment is not removed.
  ~ Deep Wound duration :: 0-4: 3 3 4 4 5 | 5-9: 5 6 6 7 7 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 13
  # causes: Deep Wound, Weakness; removes: Enchantment
Wounding Strike (PvP) #3367 | Elite Scythe Attack | Nightfall | E5 R3
  If this attack hits, target foe suffers from Bleeding for 5..20 seconds, and you lose 1 Dervish enchantment. If an enchantment is removed, target foe also suffers from a Deep Wound for 5..20 seconds.
  ~ Bleeding and Deep Wound duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Bleeding, Deep Wound; removes: Enchantment
  ! ANOMALY: Despite the full description, a Dervish enchantment is removed even if this attack fails to hit. [from PvE version page]
Zealous Sweep #2071 | Scythe Attack | Eye of the North | E5 R10
  If this attack hits, you deal +5..20 damage. You gain 3 Energy and 1 adrenaline for each foe you hit.
  ~ + Damage :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Energy Gain, Adrenaline Gain

### Dervish / Wind Prayers
Attacker's Insight #1764 | Flash Enchantment Spell | Nightfall | E10 R10
  For 3..10 seconds you have a 50% chance to block while attacking. When this enchantment ends, you inflict Weakness on all adjacent foes for 3..15 seconds.
  ~ Duration :: 0-4: 3 3 4 4 5 | 5-9: 5 6 6 7 7 | 10-14: 8 8 9 9 10 | 15-19: 10 10 11 11 12 | 20-21: 12 13
  ~ Weakness duration :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Block, Weakness; target: untargeted; aoe: adjacent
Dwayna's Touch #1528 | Touch spell | Nightfall | E5 C¾ R5
  Spell. Target touched ally is healed for 60 Health for each Enchantment on you (maximum 60..240).
  ~ Maximum healing :: 0-4: 60 72 84 96 108 | 5-9: 120 132 144 156 168 | 10-14: 180 192 204 216 228 | 15-19: 240 252 264 276 288 | 20-21: 300 312
  # causes: Healing; target: allies; range: touch
Featherfoot Grace #1766 | Enchantment Spell | Nightfall | E10 C¼ R15
  For 5..20 seconds, you move 25% faster, and conditions expire 50% faster.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  # causes: Increased Movement Speed
Grenth's Aura #2013 | Flash Enchantment Spell | Eye of the North | E10 R10
  For 20 seconds, you deal 5..25 less damage and steal 5..25 Health whenever you hit with a scythe attack. When you cast this enchantment you steal 5..25 Health from all adjacent foes.
  ~ Life stealing and damage reduction :: 0-4: 5 6 8 9 10 | 5-9: 12 13 14 16 17 | 10-14: 18 20 21 22 24 | 15-19: 25 26 28 29 30 | 20-21: 32 33
  # causes: Life Stealing; target: untargeted; aoe: adjacent
  ! BUG: If a ranged weapon is swapped for a scythe after the attack was made and before the projectile hit, Grenth's Aura will count this projectile hit as a scythe hit.
Grenth's Fingers #1493 | Flash Enchantment Spell | Nightfall | E5 R10
  All nearby foes are struck for 10..40 cold damage. For 30 seconds, your attacks deal cold damage. When this enchantment ends, you transfer&nbsp; 1..2 condition[s] to all nearby foes.
  ~ Cold damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  ~ Conditions transferred :: 0-4: 1 1 1 1 1 | 5-9: 1 1 1 2 2 | 10-14: 2 2 2 2 2 | 15-19: 2 2 2 2 2 | 20-21: 2 2
  # causes: Cold Damage, Condition; removes: Condition; target: untargeted; aoe: nearby
Grenth's Grasp #1756 | Elite Flash Enchantment Spell | Nightfall | E5 R10
  For 20 seconds, your attack skills also Cripple that foe for 1..11 second[s] and you transfer 1..3 condition[s] from yourself to that foe.
  ~ Crippled duration :: 0-4: 1 2 2 3 4 | 5-9: 4 5 6 6 7 | 10-14: 8 8 9 10 10 | 15-19: 11 12 12 13 14 | 20-21: 14 15
  ~ Transferred conditions :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Crippled, Condition; removes: Condition
Guiding Hands (PvP) #3269 | Enchantment Spell | Nightfall | E10 C¼ R15
  For 20 seconds, your next 0..3 attack[s] cannot be blocked. When activated, this skill removes the Blindness condition.
  ~ Attacks :: 0-4: 0 0 0 1 1 | 5-9: 1 1 1 2 2 | 10-14: 2 2 2 3 3 | 15-19: 3 3 3 4 4 | 20-21: 4 4
  # causes: Unblockable; removes: Condition
Harrier's Grasp (PvP) #3468 | Flash Enchantment Spell | Nightfall | E10 R15
  For 5..20 seconds, melee attacks against moving foes also Cripple those foes for 2..9 seconds. When you cast this enchantment, you are relieved of Cripple and 1 other condition. This enchantment ends after you apply Cripple 1..3 times.
  ~ Duration :: 0-4: 5 6 7 8 9 | 5-9: 10 11 12 13 14 | 10-14: 15 16 17 18 19 | 15-19: 20 21 22 23 24 | 20-21: 25 26
  ~ Crippled duration :: 0-4: 2 2 3 3 4 | 5-9: 4 5 5 6 6 | 10-14: 7 7 8 8 9 | 15-19: 9 9 10 10 11 | 20-21: 11 12
  ~ Maximum Cripple applications :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Crippled; removes: Condition
Harrier's Haste #1768 | Flash enchantment spell | Nightfall | E10 R10
  For 2..8 seconds, you move 25% faster and deal +3..12 more damage against moving foes.
  ~ Duration :: 0-4: 2 2 3 3 4 | 5-9: 4 4 5 5 6 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 10
  ~ + Damage :: 0-4: 3 4 4 5 5 | 5-9: 6 7 7 8 8 | 10-14: 9 10 10 11 11 | 15-19: 12 13 13 14 14 | 20-21: 15 16
  # causes: Increased Movement Speed
Lyssa's Haste (PvP) #3348 | Flash Enchantment Spell | Nightfall | E5 R25
  For 3..15 seconds, your Dervish enchantments recharge 33% faster. When you activate this enchantment, all adjacent foes are interrupted. When this enchantment ends, all adjacent foes are interrupted. 50% failure chance unless Wind Prayers 5 or higher.
  ~ Duration :: 0-4: 3 4 5 5 6 | 5-9: 7 8 9 9 10 | 10-14: 11 12 13 13 14 | 15-19: 15 16 17 17 18 | 20-21: 19 20
  # causes: Decreased Recharge Time, Interrupt; target: self; aoe: adjacent
Mystic Healing (PvP) #3272 | Spell | Nightfall | E5 C1 R10
  You are healed for 5..65 Health. Also heals all enchanted party members for 5..65 Health.
  ~ Healing :: 0-4: 5 9 13 17 21 | 5-9: 25 29 33 37 41 | 10-14: 45 49 53 57 61 | 15-19: 65 69 73 77 81 | 20-21: 85 89
  # causes: Healing; target: self; aoe: party
Mystic Twister #1491 | Spell | Nightfall | Ad5 C½ R4
  Deals 10..60 cold damage to all nearby foes. If you are enchanted, this spell deals an additional 10..60 cold damage.
  ~ Cold damage :: 0-4: 10 13 17 20 23 | 5-9: 27 30 33 37 40 | 10-14: 43 47 50 53 57 | 15-19: 60 63 67 70 73 | 20-21: 77 80
  ~ Additional cold damage :: 0-4: 10 13 17 20 23 | 5-9: 27 30 33 37 40 | 10-14: 43 47 50 53 57 | 15-19: 60 63 67 70 73 | 20-21: 77 80
  # causes: Cold Damage; target: untargeted; aoe: nearby
Natural Healing #1525 | Spell | Nightfall | E5 C1 R6
  You are healed for 50..170 Health. If you are not enchanted, this spell activates 50% faster.
  ~ Healing :: 0-4: 50 58 66 74 82 | 5-9: 90 98 106 114 122 | 10-14: 130 138 146 154 162 | 15-19: 170 178 186 194 202 | 20-21: 210 218
  # causes: Healing, Decreased Activation Time; target: untargeted
Onslaught (PvP) #3365 | Elite Flash Enchantment Spell | Nightfall | E10 R10
  For 2..8 seconds, you attack and gain adrenaline 25% faster.
  ~ Duration :: 0-4: 2 2 3 3 4 | 5-9: 4 4 5 5 6 | 10-14: 6 6 7 7 8 | 15-19: 8 8 9 9 10 | 20-21: 10 10
  # causes: Increased Attack Speed, Increased Adrenaline Build Rate
Pious Restoration (PvP) #3471 | Spell | Nightfall | E5 C1 R15
  You gain 80..150 Health and remove 1 Dervish enchantment. If an enchantment was removed in this way, you also lose 1 hex.
  ~ Health gain :: 0-4: 80 85 89 94 99 | 5-9: 103 108 113 117 122 | 10-14: 127 131 136 141 145 | 15-19: 150 155 159 164 169 | 20-21: 173 178
  # causes: Health Gain; removes: Enchantment, Hex spell; target: self
Rending Aura #1765 | Flash Enchantment Spell | Nightfall | E10 R10
  When you cast this enchantment, all nearby foes take 10..40 cold damage. For&nbsp;&nbsp;30 seconds, your attack skills remove enchantments from knocked-down foes. When this enchantment ends, nearby foes are affected by Cracked Armor for 1..10 second[s].
  ~ Cold damage :: 0-4: 10 12 14 16 18 | 5-9: 20 22 24 26 28 | 10-14: 30 32 34 36 38 | 15-19: 40 42 44 46 48 | 20-21: 50 52
  ~ Cracked Armor duration :: 0-4: 1 2 2 3 3 | 5-9: 4 5 5 6 6 | 10-14: 7 8 8 9 9 | 15-19: 10 11 11 12 12 | 20-21: 13 14
  # causes: Cold Damage, Cracked Armor; removes: Enchantment; target: untargeted; aoe: nearby
Signet of Mystic Speed #2200 | Signet | Eye of the North | C1 R20
  For 30 seconds, your next 1..3 self-targeting enchantment[s] cast instantly. Flash enchantments do not consume uses of this skill.
  ~ Enchantments :: 0-4: 1 1 1 1 2 | 5-9: 2 2 2 2 2 | 10-14: 2 2 3 3 3 | 15-19: 3 3 3 3 4 | 20-21: 4 4
  # causes: Decreased Activation Time; target: self
  ! BUG: The counter does not reset if the signet is recast before the original duration ends.
Signet of Pious Restraint (PvP) #3273 | Signet | Eye of the North | C1 R16
  Lose 1 Dervish enchantment and Cripple target foe 5..15 seconds. If an enchantment was removed, this skill recharges 50% faster.
  ~ Crippled duration :: 0-4: 5 6 6 7 8 | 5-9: 8 9 10 10 11 | 10-14: 12 12 13 14 14 | 15-19: 15 16 16 17 18 | 20-21: 18 19
  # causes: Crippled, Decreased Recharge Time; removes: Enchantment; target: foes; range: casting; aoe: none
Test of Faith #1545 | Touch spell | Nightfall | Ad5 C½ R5
  Spell. Deals 15..75 cold damage and takes 1 enchantment from target foe. If that foe was not enchanted, that foe is Dazed for 2..6 second[s].
  ~ Cold damage :: 0-4: 15 19 23 27 31 | 5-9: 35 39 43 47 51 | 10-14: 55 59 63 67 71 | 15-19: 75 79 83 87 91 | 20-21: 95 99
  ~ Dazed duration :: 0-4: 2 2 3 3 3 | 5-9: 3 4 4 4 4 | 10-14: 5 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 7 8
  # causes: Dazed, Cold Damage; removes: Enchantment; target: foes; range: touch
  ! ANOMALY: The full description does not mention that this skill operates at touch-range.
Vow of Piety #1505 | Enchantment spell | Nightfall | E15 C¼ R45
  For 20 seconds, you have +24 armor and +1..4 Health regeneration. Vow of Piety renews whenever an enchantment on you ends.
  ~ Health regeneration :: 0-4: 1 1 1 2 2 | 5-9: 2 2 2 3 3 | 10-14: 3 3 3 4 4 | 15-19: 4 4 4 5 5 | 20-21: 5 5
  # causes: Increased Armor Rating, Health Regeneration, Renewal
  ! ANOMALY: When a character is enchanted with Vow of Piety and at least one Air Magic, Earth Magic, Fire Magic or Water Magic enchantment (e.g. Windborne Speed), and loses all enchantments (e.g. due to the effects of Gaze of Contempt, Release Enchantments or Second Wind, but not Rend Enchantments nor Strip Enchantment that remove a certain number of enchantments), Vow of Piety will still be reapplied. This does not occur for Energy Storage, dervish nor monk enchantments. {[https://www.youtube.com/watch?v=LnzpNuYMpxc&list=PLWqdCE9awrzQgi9axfgeRHlYI7v8zIduS Video]}.
Whirling Charge (PvP) #3472 | Flash enchantment spell | Nightfall | E5 R10
  For 1..6 second[s], you move 33% faster than normal. The next time you strike a foe, all other nearby foes take 10..50 cold damage and this enchantment ends.
  ~ Duration :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  ~ Cold damage :: 0-4: 10 13 15 18 21 | 5-9: 23 26 29 31 34 | 10-14: 37 39 42 45 47 | 15-19: 50 53 55 58 61 | 20-21: 63 66
  # causes: Cold Damage, Increased Movement Speed; target: untargeted; aoe: nearby
Winds of Disenchantment #1533 | Spell | Nightfall | E5 C¾ R15
  Lose 1 Dervish enchantment. If a Dervish enchantment was removed in this way, all nearby foes lose 1 enchantment and take 20..80 cold damage.
  ~ Cold damage :: 0-4: 20 24 28 32 36 | 5-9: 40 44 48 52 56 | 10-14: 60 64 68 72 76 | 15-19: 80 84 88 92 96 | 20-21: 100 104
  # causes: Cold Damage; removes: Enchantment; target: untargeted; aoe: nearby
Zealous Vow #1761 | Elite Enchantment Spell | Nightfall | E5 C¼ R12
  For 20 seconds, you have -2 Energy regeneration, and you gain 1..6 Energy every time you hit with an attack.
  ~ Energy gain :: 0-4: 1 1 2 2 2 | 5-9: 3 3 3 4 4 | 10-14: 4 5 5 5 6 | 15-19: 6 6 7 7 7 | 20-21: 8 8
  # causes: Energy Gain, Energy Degeneration

## Common (no profession)

### None / No Attribute
Resurrection Signet #2 | Signet | Core | C3 R(recharges only on morale boost)
  Resurrect target party member. That party member is returned to life with 100% Health and 25% Energy. This signet only recharges when you gain a morale boost.
  # target: dead party members; range: casting
  ! ANOMALY: This skill, along with all other skills, recharges when zoning, despite the description text stating it requires a morale boost.
  ! ANOMALY: When used on an invalid target, this skill incorrectly gives the "Invalid spell target." message rather than the generic "Invalid target." message.
