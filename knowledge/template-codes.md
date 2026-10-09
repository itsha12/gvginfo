# Template codes

Source: Guild Wars Wiki ("Skill template format", "Equipment template format"), pulled 2026-10-08.

## Skill templates
- Base64, read lowest bit first. Header: 4 bits type (14) + 4 bits version (0); 2-bit code for bits per profession id
  (code × 2 + 4), primary and secondary profession; 4-bit attribute count, 4-bit code for bits per attribute id
  (code + 4), then per attribute: id + 4-bit rank; 4-bit code for bits per skill id (code + 8), then 8 skill ids;
  1 trailing zero bit.
- Codes use canonical skill ids, not PvP ids (e.g. Shadow Form (PvP) 2862 → 826). `data/template_id_map.json` maps
  them; the portal and `tools/gwtemplate.py` do it automatically.
- Codes store base ranks only (max 12); rune and headgear bonuses aren't in the code.
- Profession ids: 0 None, 1 Warrior, 2 Ranger, 3 Monk, 4 Necromancer, 5 Mesmer, 6 Elementalist, 7 Assassin,
  8 Ritualist, 9 Paragon, 10 Dervish.
- Attribute ids: 0 Fast Casting, 1 Illusion, 2 Domination, 3 Inspiration, 4 Blood, 5 Death, 6 Soul Reaping, 7 Curses,
  8 Air, 9 Earth, 10 Fire, 11 Water, 12 Energy Storage, 13 Healing, 14 Smiting, 15 Protection, 16 Divine Favor,
  17 Strength, 18 Axe, 19 Hammer, 20 Swordsmanship, 21 Tactics, 22 Beast Mastery, 23 Expertise, 24 Wilderness
  Survival, 25 Marksmanship, 29 Dagger Mastery, 30 Deadly Arts, 31 Shadow Arts, 32 Communing, 33 Restoration,
  34 Channeling, 35 Critical Strikes, 36 Spawning Power, 37 Spear Mastery, 38 Command, 39 Motivation, 40 Leadership,
  41 Scythe Mastery, 42 Wind Prayers, 43 Earth Prayers, 44 Mysticism.

## Equipment templates
- Type 15. Per item: slot (0 weapon, 1 off-hand, 2 chest, 3 legs, 4 head, 5 feet, 6 hands), item id, modifier count,
  dye, modifier ids. Full item and modifier id lists are on the wiki's "Equipment template format" page.
- Saved with your bars on the Templates page (each template and variation can hold several equipment sets).
