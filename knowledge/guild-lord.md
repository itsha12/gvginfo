# Guild Lord and guild hall NPCs

Source: Guild Wars Wiki, pulled 2026-10-08. Lines starting **Tested** are in-game test results and override the wiki.

## Guild Lord
- Level 20 Warrior/Ranger, 70 armor, 1680 Health, +5 pips Health regeneration. Skills: Cleave, Warrior's Cunning,
  Power Shot, Amulet of Protection (passive), Entourage.
- Amulet of Protection caps how much Health he can lose per second: 25 per second at 0:00, rising by a constant 11.6%
  per minute to 300 per second at 12:00. Damage over the cap is absorbed. Health loss from degeneration or direct loss
  is checked once per second and anything over the cap is healed back.
- The flag-stand morale boost also gives your Guild Lord +300 max Health for the rest of the match.
- Maintained enchantments can be cast on him, but only the Divine Favor heal happens; the spell itself doesn't take
  effect. Holy Veil and Purifying Veil don't remove his hexes or conditions.
- Killing him later in the match is possible with a two-person split once the cap is high.

## Entourage
Source: Guild Wars Wiki (Entourage; Developer update and Game update of 2010-07-20), pulled 2026-11-04.
- For 15 seconds the Guild Lord takes no more than 30 damage from each attack or skill and takes 30 less damage each
  second. He can only use it while the defending NPCs outnumber the attackers. It can't be interrupted or disabled.
- The defending NPCs are the five in the pit, around the Lord: the Bodyguard, two Knights and two Archers. With all five alive,
  five attackers prevent Entourage; each of these NPCs killed lowers the number of attackers needed.
- Only players and henchmen count as attackers (not pets, spirits or minions), and only while near enough to the Lord
  to fight (in casting range or close to it).
- Until July 2010 the Bodyguard's Oath of Protection gave this damage limit while the Bodyguard was alive; that was
  moved to Entourage. The Bodyguard still heals the Lord (Oath of Healing).
- Aggressiveness counts Entourage and missed attacks, and gives a much larger bonus when the opponent combines
  defensive buffs with Entourage.
- **Tested (2026-11-04):** Entourage lasts 10.5 seconds, not 15 as the wiki says.
- Replay data: the Lord recasts Entourage about every 10 seconds in some matches, but on Imperial Isle (hold vs RACK,
  2026-11-01) both Lords went minutes without casting it while no one attacked them, so a gap only means suppressed
  when attackers were at the Lord at the time.

## Guild hall NPCs (none respawn)
- **Tested (2026-11-04):** Solitude has an extra archer that counts as a pit NPC.

| NPC | Profession | Health | Armor | Skills / notes |
|---|---|---|---|---|
| Bodyguard (1) | Elementalist | 480 | — | Oath of Healing (heals the Guild Lord); priority target before the Lord |
| Knight (2, beside the Lord) | Warrior, 9 Tactics | 480 | 95 | Gash, Sever Artery, Power Attack, Healing Signet, Warrior's Cunning (Deep Wound threat) |
| Archer (several, on walls) | Ranger, longbow | 480 | 80 | Pin Down; +7 regeneration from Troll Unguent; height advantage |
| Footman (front gate) | Warrior | 480 | 95 | Pure Strike, Sever Artery |
| Guild Thief | — | — | — | removed in 2008 |
