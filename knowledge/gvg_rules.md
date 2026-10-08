# GvG rules, Guild Lord and NPCs

Source: Guild Wars Wiki, pulled 2026-10-08. Lines marked (verify) are flagged on the wiki as outdated or historical, or
conflict with other pages.

## Match structure
- 8v8 in guild halls. Ladder matches are played on the lower-ranked team's hall; tournaments use fixed maps per round.
- Win conditions (any one): kill the enemy Guild Lord; all enemy players at 60% death penalty; at 28:00 the team with
  more aggressiveness wins the tiebreak.
- Resurrection shrine revives every dead player not at max death penalty every 2 minutes by the match clock (full
  energy, recharged skills, Untouchable on resurrect). Teams spike just before the 2:00 mark or kill stragglers just
  after it.

## Aggressiveness (tiebreaker) (verify: wiki page is tagged outdated)
- +1 per point of damage dealt to the enemy Guild Lord.
- +30 per attack against the enemy Guild Lord that misses due to Blind.
- −50 per enchantment or weapon spell cast on your own Guild Lord (can go below 0).
- Life stealing and health degeneration are not damage, so they add nothing.

## Guild Lord
- Level 20 Warrior/Ranger, 70 armor, 1680 Health, +5 pips health regeneration. Skills: Cleave, Warrior's Cunning,
  Power Shot, Amulet of Protection (passive), Entourage.
- Amulet of Protection: caps how much Health he can lose per second. 25/s at 0:00, rising at a constant 11.6% per minute
  to 300/s at 12:00. Damage over the cap is absorbed. Health loss from degeneration or direct loss is checked once per
  second and anything over the cap is healed back.
- Morale boost from the flag stand also gives your Guild Lord +300 max Health for the rest of the match.
- Maintained enchantments can be cast on him, but only the Divine Favor heal happens; the spell itself doesn't take
  effect. Holy Veil / Purifying Veil don't remove his hexes/conditions.
- Killing him later in the match is possible with a two-person split once the cap is high.

## Guild hall NPCs (none respawn)
| NPC | Profession | Health | Armor | Skills / notes |
|---|---|---|---|---|
| Bodyguard (1) | Elementalist | 480 | — | Oath of Healing (heals the Guild Lord); priority target before the Lord |
| Knight (2, beside the Lord) | Warrior, 9 Tactics | 480 | 95 | Gash, Sever Artery, Power Attack, Healing Signet, Warrior's Cunning (Deep Wound threat) |
| Archer (several, on walls) | Ranger, longbow | 480 | 80 | Pin Down; +7 regen from Troll Unguent; height advantage |
| Footman (front gate) | Warrior | 480 | 95 | Pure Strike, Sever Artery |
| Guild Thief | — | — | — | Removed in 2008 (historical) |

## Victory or Death — NOT in the current game (user-verified 2026-10-08)
- Removed. NPCs do not march to the center and get no late-game damage bonus. The wiki's GvG page still describes the
  old 18:00 march; ignore it. Matches without a Lord kill go to the 28:00 aggressiveness tiebreak.

## Flag stand, morale and death penalty
- Holding the tower flag stand with your flag for 2 minutes: +10% morale boost for the team (max +10%), which counters
  death penalty first. Also +300 max Health to your Guild Lord. Carrying a flag slows you by 25%.
- Morale boost raises base Health and energy (including Energy Storage energy), not armor/weapon bonuses. It recharges
  Resurrection Signet.
- Death penalty: −15% max Health and energy per death, up to −60%. No DP for dying within 5s of resurrecting in PvP,
  or from Unyielding Aura (PvP) / Death Pact Signet deaths. In PvP each enemy player killed removes 2% DP per living
  teammate. Resets between matches.
- Pets in PvP take 15% DP when they die, and their owner's skills are disabled for 10..3s (Beast Mastery).

## Maps (example)
- Isle of Meditation: largest hall; Obelisk flag stand on the upper path behind gates makes the beach statues fire
  Fireballs at the team not holding it; Miasma on the north path (+5 degen pips, unremovable, spreads to adjacent).
  Each hall's own wiki page lists its specific mechanics.
- Monthly Flux effects change rules (gvg.report shows the current one, e.g. Minion Apocalypse in Oct 2026).

## Template codes
- Skill template: Base64, read lowest-bit-first. Header 4 bits type (14) + 4 bits version (0); 2-bit code for bits per
  profession id (code×2+4), primary and secondary profession; 4-bit attribute count, 4-bit code for bits per attribute
  id (code+4), then per attribute: id + 4-bit rank; 4-bit code for bits per skill id (code+8), then 8 skill ids;
  1 trailing zero bit.
- Profession ids: 0 None, 1 W, 2 R, 3 Mo, 4 N, 5 Me, 6 E, 7 A, 8 Rt, 9 P, 10 D.
- Attribute ids: 0 Fast Casting, 1 Illusion, 2 Domination, 3 Inspiration, 4 Blood, 5 Death, 6 Soul Reaping, 7 Curses,
  8 Air, 9 Earth, 10 Fire, 11 Water, 12 Energy Storage, 13 Healing, 14 Smiting, 15 Protection, 16 Divine Favor,
  17 Strength, 18 Axe, 19 Hammer, 20 Swordsmanship, 21 Tactics, 22 Beast Mastery, 23 Expertise, 24 Wilderness Survival,
  25 Marksmanship, 29 Dagger Mastery, 30 Deadly Arts, 31 Shadow Arts, 32 Communing, 33 Restoration, 34 Channeling,
  35 Critical Strikes, 36 Spawning Power, 37 Spear Mastery, 38 Command, 39 Motivation, 40 Leadership,
  41 Scythe Mastery, 42 Wind Prayers, 43 Earth Prayers, 44 Mysticism.
- Equipment template: type 15; per item: slot (0 weapon, 1 off-hand, 2 chest, 3 legs, 4 head, 5 feet, 6 hands), item id,
  modifier count, dye, modifier ids. Full item and modifier id lists are on the wiki's "Equipment template format" page.
