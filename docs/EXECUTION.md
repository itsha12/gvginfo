# Execution: the whys of kills and deaths (the catalogue)

The brief for the execution work on `bundle-4`: every why found so far for a kill attempt that succeeded or failed,
whether the engine reads it, and what it needs. Worked through with Denning on 2026-11-25, reviewed and amended the
same day (R-716 to R-752); the skill tags R-753 to R-765, the order of the stages R-766. Replaced in place as the build goes: the "Read" column is kept current, nothing is appended
with a date. The rulings are in `docs/RULINGS.md` and prevail; the build notes are ENGINE_NOTES section 44; the order
of work is at the end of this page and in REDESIGN.md "Execution".

## The logical core

**A death is a sum.** Over a short window a player dies when the damage that lands is more than his health at the
start plus the healing he gets. Every why is one part of that sum, or something that changed one part:

    death  <=>  damage sent - damage lost (misses, blocks, timing, movement) - damage stopped (shield set, prots)
                >  health at the start + healing

**Many whys are triggers.** Enemy skills punish a state the player chose: Mind Burn, Teinai's Wind and scythe attacks
hit adjacent players; Bull's Strike and Harrier's Grasp punish moving; Empathy punishes attacking; Backfire punishes
casting; Frenzy raises the damage its user takes. Reading each skill's trigger from its text, then asking whether the
player met it and could reasonably have avoided it, covers skills nobody thinks to list.

**The three questions are the same sum read three ways:**
1. Why a spike did or did not kill: both sides, over the 3 to 8 s of the attempt.
2. Why a team that should have been defensive lost a player: the defenders' side, over the fight, not only the burst.
3. Why a team that should have been offensive did not kill: the attackers' side, over the whole numbers advantage
   (R-732) and every target tried.

**Every skill in use is tagged** (`data/model/skill_tags.json` on `bundle-4`; stage 2, reviewed by Denning, R-753 to
R-765). 577 skills: every one on 4 or more bars from 7 September 2026, and six this page names. Each carries the parts
of the sum it acts on (adds damage, stops damage, heals, prevents enchantments, removes, slows, disables, drains
energy, cuts healing, stops disables), its trigger, its area, its cast time, what its interrupt can stop, whether it
speeds its user up, and what the engine does with it: read, context only (known to have been used, never a why or a
fault: speed boosts, resurrection skills, energy skills, R-761 to R-763) or ignore. A skill not in the file is
untagged and is reported, never read as doing nothing (R-460). Whether a cast is worth interrupting stays the list
below, read on its own.

## Where the whys sit in the engine

Read at three levels, said in one place:
1. **The kill attempt.** Every spike of both teams has an attempt record, read to its own outcome (the death or the
   save, R-710). A pressure attempt sits beside it (R-741, R-749). Each attempt gets the parts of the sum as amounts
   and both teams' missed chances. Most of sections A to D land here.
2. **The death account.** The same reading for every death, from the dead player's side.
3. **The play.** Over the whole play the engine reads the faults tied to no attempt: balling, Flail lock, a snared
   frontline, standing in area damage. These are always listed on the play's row, by kind, each with its count and
   amount (R-745). Each attempt inside a play is listed under it.

Said on the play's row and in the death account: the call first (macro), then the faults (micro), ours, then the
enemy's apart (R-299), each with what was there (the skill ready, the monk in reach), its amount (R-734) and the replay
time. An even 8v8 with no flag, split or numbers difference has no play and no job: both teams are read as trying to
kill (R-731), on an execution-only row for the fight (not a decision family, R-557).

## The rules (rule n is R-(715+n); 29 on are the review's)

1. **Time to react** (R-716, R-748). A chance counts only if there was time to see it and act: 200 ms of reaction plus
   the skill's cast time. The clock starts at the cast's start for an interrupt and at the first big hit for a prot or
   a heal; a prot cast before the hits still counts as taken (R-085). A caster inside the three quarters of a second
   after his own cast, or knocked down, cannot act; Daze doubles his cast time. Ping is left out.
2. **Estimates are fine** (R-717): gvg.report's damage, energy and amounts are used as they are, each field checked
   against the raw record before a reading is built on it (R-707).
3. **Body-blocking** is not measured and is not a why (R-718).
4. **"Coward!"** is not a fault for now (R-719, R-078).
5. **Extra damage while moving** (R-720 as amended by R-746): the knockdown from Bull's Strike stays a fault. The
   extra damage of Protector's Strike, Harrier's Haste and Weaken Knees is counted as context, never a fault.
6. **The Cripple from Harrier's Grasp** is never acceptable (R-721, R-746).
7. **Balling** (R-722): a team should almost never have more than 1 player hit by one adjacent-damage cast.
8. **Crits while moving** (R-723 as amended by R-746): melee only, on a player moving away from the attacker; counted
   over the play against the number standing still would give, as context, never a fault.
9. **Flail lock** (R-724): a warrior in Flail for more than 2 s with nothing in melee reach is a fault.
10. **Conditions on the monks' watch** (R-725): Deep Wound not removed is a fault only on a spike target or to prevent
    a death; Daze left on another monk is the only other condition fault for monks.
11. **Removal by non-monks** (R-726): where the build carries condition removal on a non-monk (a smiting monk
    included), any condition left unremoved is a fault.
12. **Interrupts** count only on the skills worth interrupting (the lists below), offensive and defensive apart;
    snares on a flag runner are read on the flag play (R-727).
13. **The frontline on defence** can stop their midline as well as their frontline (R-728, R-702).
14. **Strips** (R-729, R-744): a strip shortly before the spike or during it is the strip taken. A strip ready and
    not used on a protted target is a fault on a spike that failed, by his ruling; the check's result is shown beside
    it (it read backwards in stage X3).
15. **Well of the Profane** is not needed (R-730).
16. **An even 8v8**: both teams are read as trying to kill (R-731).
17. **Question 3's window** is the whole numbers advantage (R-732).
18. **The enemy's credit** is shown apart from our faults (R-733).
19. **Amounts shown** (R-734): each missed chance with what it would have stopped or added, measured, not ranked.
20. **Area damage**: standing in it is a fault (R-735).
21. **Empathy** (R-736): attacking with it on is the warrior's fault when his team is defensive; when it is offensive,
    the monk's, for not removing it.
22. **Backfire** (R-737): casting with it on is a fault for the midline; generally not for the backline; never with
    Spirit Bond on.
23. **Snares not checked** (R-738): Illusion of Haste, Dolyak Signet, Ward Against Foes, Seeping Wound, Barbed Trap,
    Crippling Sweep, Leaping Mantis Sting, Return.
24. **Other triggers** (R-739): casting into Shame or Diversion, attacking into Clumsiness or Ineptitude, are faults.
    Spiteful Spirit and Visions of Regret are excluded for now.
25. **Damage-raising stances** (R-740): Frenzy or Frenzied Defense up during a spike or pressure attempt is a fault.
26. **Cut-offs** ("too deep", "monk following", the pressure attempt, Flail's "nothing in melee reach") are set by
    the engine from the data (R-741).
27. **Catchable skills** (R-742, R-750). A skill can be interrupted on reaction only if it takes at least the 200 ms
    plus the interrupt's own time to land: half a second or longer against a quarter-second interrupt. An interrupt's
    own time is its cast time for a spell and half its activation or swing for an attack (Distracting Shot and Savage
    Shot a quarter second; arrow flight left out for now). An attack skill lands halfway through its swing, shortened
    by attack speed boosts. An interrupt counts as ready only if it can stop that kind of skill: a spell-only
    interrupt such as Power Spike stops no signet, ritual, touch skill or attack.
28. **Casting into a ready interrupt** (R-743) is a fault only if the cast was interrupted, the skill is on the list,
    and generally only for the backline.
29. **A fault he rules by name stands** whatever the check on unseen matches shows; the check is shown beside it, and
    a ruled kind that reads backwards is brought to him (R-744). A kind nobody ruled is told only if it passes (R-713).
30. **Play-level faults are always listed** (R-745); a missed chance on an attempt is listed by its outcome (R-714).
31. **Moving and kiting** (R-746): Bull's knockdown and Harrier's Cripple are faults; kiting is otherwise no fault;
    standing still when he should have kited a melee player is a fault. *Draft, his to correct:* not told against an
    attacker with Bull's Strike or Harrier's Grasp ready, where moving is itself the fault.
32. **A monk who is himself the spike's target** is not available to another player (R-747), as a busy monk (R-711).
33. **The pressure attempt replaces** the reading of a death with no spike from the heaviest 2 s (R-749).
34. **Built before he checks** (R-752): his marks on the Execution view wait for the catalogue's readings.

"Read" below: Yes, Partly or No on `bundle-4` as it stands; "Rule n" is the list above.

## A. The victim's own play (questions 1 and 2)

| Why | Read | What it needs |
|---|---|---|
| Pushed too deep, away from his monks | Partly: distance to the nearest monk | Distance past his own team's front line, the cut-off from data (Rule 26) |
| Pushed too deep, pulling a monk into pressure after him | No | The monk's position and the pressure he took, against the player he followed |
| Balled up (Rule 7): Mind Burn, Teinai's Wind, scythe attacks; rarely Earth Shaker, Mark of Pain | No | Players hit per cast, by joining each cast to the damage rows of its caster (damage rows carry no skill) |
| Standing in area damage (Rule 20): Chaos Storm, Symbol of Wrath and the like | No | Each skill's area from its text; repeated hits joined to the cast |
| Knocked down by Bull's Strike (Rule 5) | No | The knockdown record and the Bull's Strike that made it |
| Crippled by Harrier's Grasp (Rule 6) | No | Cripple from a melee attacker with Harrier's Grasp up |
| Crits and extra damage while moving (Rules 5, 8, 31): context only | No | Melee hits flagged critical on a player moving away, against the standing rate |
| In a stance that raises damage taken during an attempt (Rule 25) | No | His own stances at each hit of the attempt |
| Fighting in reach of their NPCs when not pushing their pit | No | NPC damage taken, against his position and the team's job |
| Standing still when he should have kited a melee player (Rule 31) | Partly: kiting measured | Kiting as a missed chance, not only a measure |
| Attacking through Empathy (Rule 21), Clumsiness or Ineptitude; casting into Backfire (Rule 22), Shame or Diversion (Rule 24) | No | Trigger tags; his attacks and casts while the hex was on him |
| Casting into a ready interrupt, not cancelling (Rule 28) | Partly: counted, not filtered | Only interrupted casts of listed skills, backline players |
| Wrong weapon set when under attack | Partly: shield set read over the play | The weapon set at each attempt |
| His own stance, escape or self-heal unused when ready | No | His own defensive skills ready at the attempt (Rule 1) |
| Fell back too late, or not to his monks | No | Movement towards safety once the attempt starts, against the time he had |

## B. The monks (questions 1 and 2)

| Why | Read | What it needs |
|---|---|---|
| Wrong spot: out of reach when the spike came | No | Each monk's reach to the players likely to be spiked, before the attempt |
| Followed an over-extended player into pressure | No | Shared with section A |
| Knocked down and could not cast | Yes | |
| Dazed, or inside his own aftercast (Rule 1) | Yes (stage 1) | |
| Himself the spike's target (Rule 32) | Yes (stage 1) | |
| Disabled (Power Block, Complicate, Blackout) or under Shame or Diversion | No | Read at the attempt; measured for the play now |
| Backfire or Visions of Regret making his casts costly | No | Trigger tags; his casts while hexed |
| Out of energy | Yes: gvg.report's model, out under 20 (R-681) | |
| Busy on another player under pressure (R-711) | Yes | |
| Prot or heal ready and not cast | Yes, with Rule 1 (stage 1) | |
| Prot cast too early, ended before the spike landed | No | Each prot's end against the first big hit |
| Both monks on the same player while another died | No | Each monk's targets during the attempt |
| Wrong kind of prot for the damage | Partly: death accounts | Each prot's effect on each damage type, from skill text |
| Prots wasted on players nobody attacked | No | Prots cast against the damage that followed on that player |
| Shadow Shroud on the target: a missed prot under it is no fault | No | Tag Shadow Shroud; read it on the target at each attempt |
| Air of Disenchantment or Mark of Insecurity not removed or interrupted | Partly: hex removal over the play | Removal and an interrupt on the cast, as missed chances on the attempt |
| Barbs left on the target | Partly: hex removal over the play | A missed chance on the attempt |
| No Aura of Stability against a hammer warrior | Partly: death accounts | A missed chance on the attempt |
| Deep Wound not removed (Rule 10) | Partly: removal timing | Only on a spike target or to prevent a death |
| Daze left on another monk (Rule 10) | Partly: removal timing | |

## C. Team support on defence (question 2, and question 1 from the defence's side)

| Why | Read | What it needs |
|---|---|---|
| No peel: no knockdown, Blind, snare or interrupt on the players hitting him | Partly: death accounts | A missed chance on the attempt |
| No defensive interrupt on a skill worth interrupting (Rules 12, 27) | Yes on a spike's skills (stage 1: listed skills, catchable, the interrupt's own time) | Any damage, not only spikes |
| Frontline attacking through Empathy when defensive (Rule 21) | No | Trigger tags; the job is already read |
| Frontline not stopping their frontline or midline when defensive (Rule 13) | Partly: targets judged by the job | Midline as a right target when defensive |
| No condition removal from a non-monk who carries it (Rule 11) | Partly: over the play | The team's bars at the attempt |
| A dead player not ressed, or the res cast into a ready interrupt | Partly: res timing and res stopped | Res as a missed chance after each death, with Rule 1 |

## D. The attack (questions 1 and 3)

A spike (400 or more damage on one player in 3 s) is the only kill attempt today; the pressure attempt (a player kept
in danger for a while, the cut-off from data, degen counted) is needed for question 3.

| Why | Read | What it needs |
|---|---|---|
| Damage off-timed, not landing together | Yes | |
| Strip missing or off-timed (Rule 14) | Yes; a fault by ruling, not yet listed | Failed spikes listed with the attack's misses (stage 1's remainder) |
| Deep Wound missing or off-timed on the spike (R-751) | No | Deep Wound on the target against the first big hit |
| A damage player with his skill ready who hit another target (R-751) | No | Each attacker's spike skills ready, in range, and where his damage went |
| Enchantment prevention not used: Shadow Shroud | No | Tag the skill; read on the attempt |
| Their monks not pressured: interrupts, knockdowns, Daze | Yes (fails the check: never a fault) | |
| Their monks not disabled, cast-prevented or drained | No | Added to the spike package; the check run again |
| Spiked into a block or spell immunity (Aegis, Guardian, Mirage Cloak, Spell Breaker, Shadow Form, Obsidian Flesh) | No | The target's effects at the first big hit |
| Spiked into a ward or a spirit (Ward Against Melee, Shelter, Union, Displacement) (R-751) | No | Wards and spirits in reach of the target at the first big hit |
| Wrong target: frontline over monks when trying to kill | Partly: over the play | Per attempt |
| Frontline hampered: Empathy, Faintheartedness, Blurred Vision, Insidious Parasite; also Clumsiness, Sum of All Fears, Shadow of Fear, Ineptitude, Price of Failure, Spiteful Spirit, Blind, Weakness | No | Their hexes and conditions on our attackers during the attempt, and whether they were removed (a why; a fault only where Rules 21 and 24 say) |
| Frontline snared and could not reach the target | No | Every skill that cripples or slows (but Rule 23); snares on our attackers against their distance to the target |
| Flail lock (Rule 9) | No | Flail up with no enemy in melee reach |
| Attackers knocked down, interrupted or out of range | Partly: from the victim's side | The same read from the attackers' side |
| Time lost chasing a kiting target | Partly: kiting measured | Per attempt |
| Switched targets too early | No | Damage on a target against how low he was when they left him |
| Did not snare the target | No | Snares ready and unused on a target who escaped |
| The kill undone at once by Death Pact Signet or a quick res not stopped | No | Res casts after a kill against our interrupts ready (Rule 1) |
| The lead not kept long enough to convert | Partly: its length read | Tied to the attempts made during it |

**Snares on gvg.report's bars** (1,915 matches to 9 November 2026; bars carrying the skill). The engine reads every
skill that cripples or slows except Rule 23's. For scale, frontline interference: Empathy 693, Faintheartedness 199,
Blurred Vision 130.

| Skill | Kind | Bars |
|---|---|---|
| Flail | Self-slow on our own warrior, 33% (Rule 9) | 2,971 |
| Harrier's Grasp | Cripple on moving foes hit in melee | 2,269 |
| Signet of Pious Restraint | Cripple | 1,217 |
| Caltrops | Cripple, target and adjacent | 769 |
| Mantis Touch, Hamstring, "You're All Alone!", Pin Down, Maiming Spear | Cripple | 290, 253, 225, 157, 120 |
| Siphon Speed, Freezing Gust, Mind Freeze | Hex, slower | 223, 182, 125 |
| Ethereal Burden, Kitah's Burden, Crippling Anguish | Hex, 50% slower | 171, 162, 75 |
| Earthen Shackles | Hex, 90% slower, nearby foes | 156 |
| Shatterstone, Shard Storm, Ice Prison, Winter's Embrace | Hex, 66% slower | 97, 94, 85, 81 |
| Shadow Prison, Shadowy Burden, Binding Chains, Crippling Shot, Ice Spikes, Crippling Slash, Imagined Burden, Teinai's Prison, Grasping Earth, Sum of All Fears | Rarer cripples and slows | 4 to 44 |

## Skills worth interrupting (approved by Denning, 2026-11-25; R-727)

The engine's copy is `data/model/interrupt_worth.json` on `bundle-4`; change the two together. Drawn from skills on
about 60 or more bars in 1,915 matches. Whether one is catchable is Rule 27; quarter-second prots and heals
(Protective Spirit, Aegis, Reversal of Fortune, Patient Spirit, Aura of Stability) fall outside it. Signets, binding
rituals, touch skills and attacks need an interrupt that stops any action or attacks.

**Offensive: interrupts that help us kill.** A miss is a fault on the attack.

| Use | Skills (cast time) |
|---|---|
| Res | Resurrection Signet (3 s), Death Pact Signet (4 s), Flesh of My Flesh (4 s), Signet of Return (4 s), Resurrect (5 s), Rejuvenation (3 s) |
| Heals on our target | Healing Burst, Blessed Light, Word of Healing, Gift of Health, Mend Body and Soul (¾ s); Boon Signet, Spirit Light, Healing Breeze (1 s); Signet of Devotion (2 s) |
| Prots and removal on our target | Guardian, Shield of Absorption, Weapon of Warding, Cure Hex, Deny Hexes, Convert Hexes, Holy Veil (1 s); Purge Signet (2 s); Dismiss Condition, Restore Condition, Mend Condition, Mend Ailment (¾ s) |
| Their defensive spirits | Union, Displacement, Recovery, Recuperation, Life (3 s); Shelter (5 s) |
| Hexes and conditions on our damage | Empathy, Guilt, Price of Failure, Shadow of Fear, Clumsiness, Wandering Eye (2 s); Blurred Vision, Faintheartedness, Ineptitude, Insidious Parasite, Gaze from Beyond, Steam, Weapon of Shadow, Ebon Hawk, Oppressive Gaze (1 s); Blinding Flash (¾ s); Spirit Shackles (3 s) |
| Snares on our attackers | Siphon Speed, Freezing Gust, Ethereal Burden, Kitah's Burden, Earthen Shackles, Mind Freeze, Shard Storm, Crippling Anguish, Signet of Pious Restraint (1 s); Winter's Embrace (¾ s); Shatterstone, Ice Prison (2 s); Pin Down (a bow attack). Not catchable: Caltrops (¼ s), "You're All Alone!" and Harrier's Grasp (instant) |

**Flag plays: interrupts that keep our runner moving.** The same snares as the last row, read against flag timing:
the cost is seconds of flag time on the flag play, not any kill attempt.

**Defensive: interrupts that help us live.** A miss is a fault on the defence.

| Use | Skills (cast time) |
|---|---|
| Hammer and axe | Hammer Bash, Crushing Blow, Decapitate (the swing: Rule 27) |
| Ranged attacks | Cruel Spear, Burning Arrow, Chest Thumper, Vicious Attack |
| Elementalist damage | Lightning Strike, Spirit Burn, Essence Strike, Glowing Gaze, Immolate, Mind Burn, Teinai's Wind, Shell Shock, Invoke Lightning, Lightning Surge, Mind Shock, Shock Arrow, Glowing Ice, Lightning Bolt, Stoning, Double Dragon (1 s); Chain Lightning, Meteor, Deathly Swarm (2 s) |
| Ritualist and Necromancer damage | Lamentation, Renewing Surge, Weaken Knees, Lingering Curse, Suffering, Rising Bile, Brutal Weapon, Sundering Weapon (1 s) |
| Hexes, strips and shutdown on us | Shame, Energy Surge, Energy Burn, Drain Enchantment, Rend Enchantments, Gaze of Contempt, Migraine (2 s); Backfire, Diversion, Signet of Humility (3 s); Mind Wrack, Shatter Enchantment, Conjure Phantasm, Conjure Nightmare, Air of Disenchantment, Mark of Insecurity, Barbs, Blackout, Toxic Chill (1 s) |
| Smiting | Word of Censure, Castigation Signet, Symbol of Wrath (1 s) |
| Rituals | Bloodsong (1.5 s) |

Removed as not worth interrupting (Denning): Signet of Rejuvenation, Dwayna's Kiss, Heaven's Delight, Smite Hex, Bane
Signet, Signet of Rage, Mending Touch, Divine Healing, Remove Hex, Mantis Touch, Hamstring, Maiming Spear, Devastating
Hammer, Bull's Strike, Executioner's Strike, Dismember, Agonizing Chop, Wearying Strike, Body Blow, Sun and Moon
Slash, Protector's Strike (a ½ s attack), Mighty Throw, Unblockable Throw, Marauder's Shot, Mystic Twister, Weaken
Armor, Test of Faith (a Dervish Wind Prayers touch spell, and a strip). Left out as low value: attunements, glyphs,
preparations, echoes and chants, weapon spells other than Weapon of Warding, Brutal Weapon, Sundering Weapon and Weapon
of Shadow, and movement skills. Ethereal Burden and Kitah's Burden have no cast time in the skill data (see the limits).

## E. Context (not faults; every why is read against them)

- The play's job, which says whether a team should have been offensive or defensive (R-709; an even 8v8, Rule 16).
- Numbers in the fight, and how long an advantage lasts. Morale and death penalty.
- Health at the start of the attempt: degen, pressure and Deep Wound before the burst, so a "spike" may be a finish.
- NPCs: archer, knight and Guild Lord damage and healing. The hall and its features.
- Builds: a fixed state, but what they can do bears on what was possible (R-539).
- The enemy doing well: shown as their credit, apart from our faults (Rule 18).

## The limits of the data (checked 2026-11-25)

- Times are tenths of a second; positions and the moving state about once a second. Velocity is not in the stored
  replays (using it means a new version of the file beside each replay and fetching all of them again).
- Damage rows carry no skill (0 of 3,466 in chic v 戦戦戦戦, d1e4b578). A hit is tied to a skill by joining it to its
  caster's cast, or to gvg.report's hint for that target and tick: each such join is checked first (R-707). Only Bull's
  knockdown and Harrier's Cripple are shown by the hit itself.
- No block or miss is recorded per attack: only gvg.report's totals in its recaps at deaths and saves.
- How long a cast took is recorded (start and end, in tenths): Hammer Bash and Crushing Blow land in about 0.5 s (0.8 s
  with no attack speed boost), Dismember and Bull's Strike in 0.4 s, Protector's Strike in 0.1 s; a 1 s spell takes 0.5 s on
  a half-cast, and a Mesmer's Shame (2 s) about 1.1 s. So a catchable skill is told from the cast itself (Rule 27).
- Critical hits are flagged on the damage row (167 of 3,466 in the same match) and kept in the stored replays.
- Tried on 87 matches: a melee hit is a crit on 23% of hits on a player standing at both samples, 52% moving at both,
  65% moving away from the attacker; a ranged hit 13% either way. Tried on 101: 11% of Mind Burn casts and 10% of
  Teinai's Wind casts that hit their target hit two or more players, few of them two frontliners.
- 41 skills that are not attacks or instant have no cast time in `data/skills.json` (Fireball, Obsidian Flame,
  Phoenix, Arc Lightning, Ice Spikes, Ethereal Burden, Kitah's Burden, Sum of All Fears among them): a fault of the
  wiki sync, to be fixed there, later (R-765); eight of them cast in 1.5 s by his word and carry it in the tag file
  (R-764). The interrupt reading does not lean on it: how long a cast took is the replay's own record.
- Armour and insignias are left out: a player cannot change them in a match. Out of reach: ping, line of sight around
  obstacles, calls and intent (R-371).

## Order of work (all on `bundle-4`, before the close; his marks after it, R-752)

| Stage | What | Done when |
|---|---|---|
| 1. The built kinds on the new rules | Built: Rules 1, 12, 27 and 32 on the prot, the heal and the interrupt on a spike skill; the lists as a data file. Left: failed spikes listed with the strip missed (Rules 14, 29); Rule 28's filter on casting into a ready interrupt. No full run of its own (R-766) | development set and key pass; plays unchanged |
| 2. The skill data | Done but for the sync: every skill in use tagged in a file of its own, `data/model/skill_tags.json` (`data/skills.json` is never edited by hand), reviewed by Denning (R-753 to R-765). Left for later: the wiki sync's missing cast times | Denning has reviewed the tagged list (he has) |
| 3. What the records already show | Bull's knockdown, Harrier's Cripple, balling, Empathy and the other triggers, damage-raising stances, a spike into a block, ward or spirit, Deep Wound on the spike, an attacker on another target, Rule 10 and 11 removals | each join checked against the raw record (R-707); each kind checked once on unseen matches, shown beside the ruled ones (Rule 29) |
| 4. The ledger and the pressure attempt | Each part of the sum a measured amount on every attempt, for both teams (Rule 19); the pressure attempt beside the spike, its cut-off from data, degen counted; the even 8v8's row | question 3 read attempt by attempt; the heaviest 2 s retired (Rule 33) |
| 5. Readings from positions | Too deep, monk following, Flail lock, the snared frontline, area damage, should have kited; crits while moving as context | cut-offs set from data (Rule 26) |
| The runs (R-766) | Built in the order 1's remainder, 4, 3. Then one full run with every check for stages 1 to 4 together: `cases.py attempts` and `execution` (do the kinds still pass on unseen matches?), the key, the truths, `execution_rows.json`. Stage 5 has its own full run, before X4's sentences | the three built kinds still pass on unseen matches; each new kind checked once |
| Then | The faults said on each play and death (stage X4 again on the full list); his marks on the Execution view (stage X5) | his Classic execution rows read as he reads them |
