# Execution: the whys of kills and deaths (the catalogue)

The brief for the execution work on `bundle-4`: every why found so far for a kill attempt that succeeded or failed,
whether the engine reads it, and what it needs. Worked through with Denning on 2026-11-25, reviewed and amended the
same day (R-716 to R-752); the skill tags R-753 to R-765 and R-767 to R-778, the order of the stages R-766, his answers on stage 4 R-779 to R-784, on the questions after it R-785 to R-802, on stage 5 R-803 and R-804, after the full run at f2b8796 R-805 to R-810, on his marks of Men v Crew R-811 to R-821, on his marks of RACK v hdm and Men v NwAy R-822 to R-830, after the full run at 90223ed R-831 to R-838, on the strip and the readings kept by name R-839 to R-842. Replaced in place as the build goes: the "Read" column is kept current, nothing is appended
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
R-765, R-767 to R-778). 608 skills: every one on 4 or more bars from 1 September 2026, where the engine's matches
start, and the thirteen this page names (Shadow Form is ignored, R-770). Each carries the parts
of the sum it acts on (adds damage, stops damage, heals, prevents enchantments, removes, slows, disables, drains
energy, cuts healing, stops disables), its trigger, its area, its cast time, what its interrupt can stop, whether it
speeds its user up, who each part lands on (foe, ally, self), whether it raises the damage its user takes, whether it
is one of Rule 23's snares, whether it stays on the ground, whether a strip takes an enchantment off as it is cast and
whether an interrupt is thrown on demand, and what the engine does with it: read, context only (known to have been used, never a why or a
fault: speed boosts, resurrection skills, energy skills, R-761 to R-763) or ignore. A skill not in the file is
untagged and is counted and listed by every run, never read as doing nothing (R-460, R-767; 10 skills in 6 of the 82
development matches). Whether a cast is worth interrupting stays the list
below, read on its own.

## Where the whys sit in the engine

Read at three levels, said in one place:
1. **The kill attempt.** Every spike of both teams has an attempt record, read to its own outcome (the death or the
   save, R-710). A spike is 400 or more inside 3 s, or a burst that takes most of the health a player had (R-780). A pressure attempt sits beside it (R-741, R-749; built, stage 4). Each attempt carries the parts of
   the sum as amounts (the ledger, built: health at the start, what landed by kind, what was healed, health at the
   end, what the parts leave over; what was stopped from gvg.report's recap) and both teams' missed chances, each
   with what a cast of that skill gave that player on average this match (R-734). Most of sections A to D land here.
2. **The death account.** The same reading for every death, from the dead player's side: from the spike that killed
   him, else from the pressure attempt that did, else from the first thing landed on him after he was last above the
   line (19% of deaths on the development set, a third of them with nothing landed in the record: those list no
   fault, R-783). A pact kill (Death Pact Signet's caster dying as the player he resurrected dies) is said as one and
   reads no chance (R-783). The heaviest 2 s is retired (Rule 33).
3. **The play.** Over the whole play the engine reads the faults tied to no attempt: balling and the triggers a
   player walked into (built, stage 3), Flail lock, standing in area damage and should have kited (built, stage 5). These are always listed on the play's row, by kind, each with its count and
   amount (R-745). Each attempt inside a play is listed under it.

Said on the play's row and in the death account: the call first (macro), then the faults (micro), ours, then the
enemy's apart (R-299), each with what was there (the skill ready, the monk in reach), its amount (R-734) and the replay
time. An even 8v8 with no flag, split or numbers difference has no play and no job: both teams are read as trying to
kill (R-731), on an execution-only row for the fight (not a decision family, R-557); an even 7v7 the same (R-781).
Built: eight or seven a side in the largest fight, no stand-off, 12 s or longer, the seconds no play covers. Question 3 is said on every play whose job is
to kill and on every numbers advantage, attempt by attempt, with the enemy's credit apart (R-732, R-733).

## The rules (rule n is R-(715+n) up to 28; 29 on are the review's and later rulings')

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
7. **Balling** (R-722, R-787, R-847): a team should almost never have more than 1 player hit by one cast that reaches
   adjacent foes, nearby foes or foes in the area; Invoke Lightning and Chain Lightning are such casts.
8. **Crits while moving** (R-723 as amended by R-746): melee only, on a player moving away from the attacker; counted
   over the play against the number standing still would give, as context, never a fault.
9. **Flail lock** (R-724): a warrior in Flail for more than 2 s with nothing in melee reach is a fault.
10. **Conditions on the monks' watch** (R-725): Deep Wound not removed is a fault only on a spike target or to prevent
    a death; Daze left on another monk is the only other condition fault for monks.
11. **Removal by non-monks** (R-726): where the build carries condition removal on a non-monk (a smiting monk
    included), any condition left unremoved is a fault.
12. **Interrupts** count only on the skills worth interrupting (the lists below), offensive and defensive apart;
    snares on a flag runner are read on the flag play (R-727). A missed interrupt on a spike skill is a fault on a
    spike only (400 or more inside 3 s), never on a burst on a hurt player (R-805, Rule 40).
13. **The frontline on defence** can stop their midline as well as their frontline (R-728, R-702).
14. **Strips** (R-729, R-744): a strip shortly before the spike or during it is the strip taken. A strip ready and
    not used on a protted target is a fault on a spike that failed, by his ruling; the check's result is shown beside
    it (it read backwards in stage X3).
15. **Well of the Profane** is not needed (R-730).
16. **An even 8v8 or 7v7**: both teams are read as trying to kill (R-731, R-781).
17. **Question 3's window** is the whole numbers advantage (R-732).
18. **The enemy's credit** is shown apart from our faults (R-733).
19. **Amounts shown** (R-734): each missed chance with what it would have stopped or added, measured, not ranked.
20. **Area damage**: standing in it is a fault (R-735). Set aside for now and not read (R-807, Rule 42).
21. **Empathy** (R-736): attacking with it on is the warrior's fault when his team is defensive; when it is offensive,
    the monk's, for not removing it.
22. **Backfire** (R-737): casting with it on is a fault for the midline; generally not for the backline; never with
    Spirit Bond on.
23. **Snares not checked** (R-738): Illusion of Haste, Dolyak Signet, Ward Against Foes, Seeping Wound, Barbed Trap,
    Crippling Sweep, Leaping Mantis Sting, Return.
24. **Other triggers** (R-739): casting into Shame or Diversion, attacking into Clumsiness or Ineptitude, are faults.
    Spiteful Spirit and Visions of Regret are excluded for now.
25. **Damage-raising stances** (R-740, R-768): Frenzy, Frenzied Defense or Primal Rage up during a spike or pressure
    attempt is a fault. The armour penalty of Healing Signet is context.
26. **Cut-offs** ("too deep", "monk following", the pressure attempt, Flail's "nothing in melee reach") are set by
    the engine from the data (R-741). Too deep: 1,000 past his own front line; monk following: the monk 450 past it
    (both from the 564 counted matches, the full run at f2b8796; the second is not steady, 0 in five groups of ten);
    melee reach 250 (`cases.py positions` prints the first two from any plays file). The pressure line is his: at or under 225 health (R-779), for a second or
    longer with 90 or more landing in 3 s. The floor of a burst on a hurt player is the engine's (R-780): two thirds
    of his health and 200 or more, where such a burst kills about as often as a spike of 400.
27. **Catchable skills** (R-742, R-750). A skill can be interrupted on reaction only if it takes at least the 200 ms
    plus the interrupt's own time to land: half a second or longer against a quarter-second interrupt. An interrupt's
    own time is its cast time for a spell and half its activation or swing for an attack (Distracting Shot and Savage
    Shot a quarter second; arrow flight left out for now). An attack skill lands halfway through its swing, shortened
    by attack speed boosts. An interrupt counts as ready only if it can stop that kind of skill: a spell-only
    interrupt such as Power Spike stops no signet, ritual, touch skill or attack.
28. **Casting into a ready interrupt** (R-743 as amended by R-789) is a fault only at a death, where the cast was
    interrupted and the skill is on the list. Elsewhere it is context, counted for every player over the match
    (non-monks too), for the report.
29. **A fault he rules by name stands** whatever the check on unseen matches shows; the check is shown beside it, and
    a ruled kind that reads backwards is brought to him (R-744). A kind nobody ruled is told only if it passes (R-713).
30. **Play-level faults are always listed** (R-745); a missed chance on an attempt is listed by its outcome (R-714).
31. **Moving and kiting** (R-746 as amended by R-806): Bull's knockdown and Harrier's Cripple are faults; kiting is
    otherwise no fault. Should have kited is withdrawn and not read (R-806, Rule 41; R-792 with it).
32. **A monk who is himself the spike's target** (R-747), or himself under pressure (250 or more in 2 s, R-790), is
    not available to another player, as a busy monk (R-711).
33. **The pressure attempt replaces** the reading of a death with no spike from the heaviest 2 s (R-749). Built.
34. **Built before he checks** (R-752): his marks on the Execution view wait for the catalogue's readings.
35. **A monk's own prot or heal on himself is a chance** (R-796), on the same time as every save (Rule 1: 200 ms from
    the first big hit, then the cast), with the skills he can cast on himself. Rule 32 speaks of his chances for
    another player. Built.
36. **Taken means landed** (R-797, amending R-715): a prot or heal begun in time that was interrupted, cancelled, or
    cut off by his death is not the chance taken; it is said beside the death as context, and the other monks'
    chances are listed. Built.
37. **Too late** (R-802): a monk whose prot or heal was cut off by the death is himself at fault where he had an
    earlier moment at which the same cast would have landed; otherwise his cast is context. Built.
38. **Area damage from the third hit** (R-803): the first hit cannot be avoided, the second lets him finish his cast;
    a knockdown or a snare on him at the counted hits is context beside the fault, not an excuse. Set aside with
    Rule 20 (R-807): `execution.area_hits` is kept, nothing reads it.
39. **The readings from positions** (R-804, R-808): too deep is the distance past his own team's front line; monk
    following is a monk who takes pressure having moved up behind a player who was too deep, and a monk past his
    front line is told only then (R-808); a snared frontline is a why, not a fault. Built. Too deep and monk
    following are named faults only once they pass on unseen matches (R-713): on the 564 counted matches neither does.
40. **Spikes and bursts apart** (R-805, amending R-780): a spike is 400 or more on one player inside 3 s; a burst on a
    hurt player is most of the health he had (two thirds and 200 or more). Both are kill attempts, read for the prot
    and the heal. The interrupt on a spike skill is a fault on a spike only, by his ruling: its check is read on the
    spikes alone and stands beside it. A death is told as a spike or as a burst. Built.
41. **Should have kited is withdrawn** (R-806). Not read.
42. **Standing in area damage is set aside for now** (R-807). Not read; balling (Rule 7) is the area reading that stays.
43. **An attacker on another target is dropped for now** as a why of a failed spike (R-809). Not read.
44. **At the spike itself** (R-810, the match report's readings; section B). A skill the enemy has disabled is not
    ready: Power Block (the interrupted skill and its attribute's), Power Lock and Complicate (the interrupted
    skill), Blackout (all), Signet of Humility (the elite), Diversion (the skill used under it, for its recharge
    and the added time). No enchantment can be cast on a target under Shadow Shroud: an enchantment prot not cast
    under it is no fault, a party-wide one (Shield Guardian) included (R-811). A monk under Shame has no spell on an ally. Each is said as "not a chance" on the death. On every
    attempt: the set the target held, Shadow Shroud on him, and each of his monks knocked down, Dazed, disabled or
    hexed at the first big hit. Built.
45. **What a missed chance would have done, and by when** (R-734, R-810). Beside each missed prot and heal on a
    death: what it would have stopped and healed (a prot by its own rule, R-784; a heal by what a cast of it gave him
    on average this match), whether that would have saved him, and the latest start that still does, found by
    walking the sum of the death again with the cast added (a tenth of a second at a time). Beside a missed
    interrupt: what one cast of the skill did on average, and whether that much less would have saved him. Not told
    where the sum of the death does not balance (R-460). An upper bound (R-785). Built.
46. **Listed only where it would have saved him** (R-812, amending R-798 and R-734). A missed prot is listed only where
    that cast alone would have saved him; a missed heal the same on a spike, while a burst and a death with no spike
    keep theirs. Divine Favor's heal counts only where the prot itself heals (Spirit Bond, Shielding Hands), never on
    its own (Guardian, Shield Guardian). One whose result is not told stays and says so. No more than two skills of
    one monk, the two that give the most (R-817). Built.
47. **The other disables** (R-813). A skill whose own text disables the skill it interrupts is read as Power Lock is:
    Distracting Shot, Disrupting Chop, Disrupting Lunge, Magebane Shot, Disrupting Stab, Simple Thievery, Signet of
    Distraction, Lyssa's Assault, Psychic Distraction, for the text's length (after the skill's recharge where the
    text says "additional"). A monk does not cast through Shame or Diversion: no fault. Arcane Thievery and Arcane
    Larceny disable a spell the record does not name: said on that monk, his chances kept. Built.
48. **An arrow's flight is 0.2 s** (R-814, amending Rule 27): a bow interrupt needs a cast of 0.65 s or longer. Built.
49. **Range and speed before the hexes** (R-815). No monk in range is the reason, before Shadow Shroud; a hex or a
    disable on a monk out of range is not counted; a spike too fast for any save (the time to see it and the cast are
    longer than he lived) is said as too fast; a monk whose hands were full with a cast begun before he could have
    seen the hit is said as that. Shadow Shroud is said only where it barred a prot that could otherwise have been
    cast. Built.
50. **One interrupt of a player on one spike** (R-816): one landed is a success and no other is asked of him; one
    thrown and missed is a missed interrupt, said once, and no other is asked of him. Built.
51. **Said on the death** (R-818, R-819, R-820): the area damage that hurt him before a burst (a cast aimed at another
    player); the enchantments stripped from him, and for a prot what it would have stopped had it stayed; how long of
    the spike he held a set with no shield, and whether a shield would have saved him; the sentences in the match
    report's wording, with no ruling numbers; a cast begun too late to land reads "Late Heal:" or "Late Prot:" under
    the same "Missed:" in the head (R-821). Built.
52. **The wording of a death, further** (R-822). No ruling number and no explanation of a rule in a row he reviews.
    Each on a line of its own, under its label: "Trigger Fault:" (his own play: Bull's knockdown, Harrier's Cripple,
    Empathy, Clumsiness, Ineptitude, Backfire, Shame, Diversion, a damage-raising stance), "Positioning:" (too deep,
    monk following), "Context:" (crits while moving; a trigger that is no fault). A burst's head says the damage
    inside 3 s. What was done for him is one line a player. Built.
53. **Deep Wound left, in the form of the others** (R-823): "Missed Deep Wound: Deep Wound stayed until death, with
    7 Monk available to cast, Draw Conditions ready, in range, sufficient energy (41 to 41)", then what the removal
    would have given back and healed, whether that would have saved him, and by when (the sum walked again with the
    removal landed: his health and his maximum rise by what Deep Wound took). One line a monk. Built.
54. **A heal that comes later** (R-824). A heal whose own healing comes as its enchantment ends (Patient Spirit, 2 s
    after it lands) gives only its caster's Divine Favor with the cast; the rest counts only before he died. One that
    heals only as something sets it off (Vigorous Spirit) gives its Divine Favor alone. What a cast that landed gave
    counts the heal at its enchantment's end (Patient Spirit, Shielding Hands). Built.
55. **Cast times** (R-825): the skill data's, and the tag file's where the skill data has none (nine skills, each
    1.5 s: Shield Guardian and R-764's). One reading, `forensics.cast_s`. Built.
56. **A spell lost to Shame** (R-826, R-830, with Rule 24): told from gvg.report's interrupt record, which names
    Shame as the skill that stopped the cast, and said as lost to Shame. A fault only where the monk could have
    cancelled: the hex had been on him 0.2 s or longer when his cast stopped (begun under it, the time he had not to
    begin; under way as it landed, the time to cancel before the spell would have finished). A monk's prot or heal on
    the dying player lost to it inside the kill attempt is then a Trigger Fault on that death; otherwise it is no
    fault, said under "Attempted, failed". Built.
57. **What a prot that landed did** (R-827): gvg.report's recap of the death gives what a player's skill stopped and
    the attacks it blocked; a prot that blocks and is credited with nothing reads "blocking nothing"; Aura of Faith
    is said by its own rule. Built.
58. **Every monk on his own at a death** (R-828, amending R-715). A prot or heal a team
    mate landed did not save a player who died, so it excuses no other monk: each monk who landed none of that kind
    on him is read for his own chance, listed where his cast alone would have saved him (Rule 46). A cast begun too
    late names what else of that kind he had ready. A prot does not stack with itself. Where the player lived, a
    chance a team mate took is still the team's (R-715). Built.
59. **The front line** (R-829): the most forward team mate in the fight who is no backline monk, whatever his role;
    not told from frontline characters alone. Said as "his most forward team mate". As built.
60. **A block, by what the spike is made of** (R-831): a block (Guardian, Shield Guardian, Aegis, a blocking stance)
    is said as a why of a failed spike only where more than a third of the spike is attacks. His cut-off. Built.
61. **Frenzied Defense** (R-832, amending Rule 25): a fault only where spells landed while it was up, its own doing
    half of what they landed; with none, context. Frenzy and Primal Rage as before. Built.
62. **A dying monk's own spell lost to Shame** (R-833, with Rule 56): a Trigger Fault on his own row though the
    spell was for another player. As built.
63. **Too deep and monk following are paused** (R-834): read and kept on every record, said nowhere and shown in
    no report, no work on them until he takes them up again. Built (`execution.POSITIONS_PAUSED`).
64. **The strip that matters** (R-835, amending Rule 14's "or during it"; R-839, R-840): a strip counts by what it
    took, whether or not it deals damage. On a spike, a strip that takes a prot off the target before the first big
    hit, or a prot or a heal off him during the spike; on a burst on a hurt player, a strip that takes a prot or a
    heal (Patient Spirit) before or during it. A damaging strip (Shatter Enchantment and its like) that took neither
    is damage like any other spell. Before = the 3 s before the first big hit, during = to 3 s after it. A strip
    before the spike that left no prot on him counts. Built (`strip_effective`); the missed strip stays a prot on him,
    a strip ready and none at all.
65. **The attack's good play on their monks** (R-836): a prot or heal of a monk's for the target that the attack
    stopped (who stopped it, with what), and a monk in reach knocked down as the spike lands, casting or not. Said on
    the death as "Enemy good play:", on a death by a spike and on one by pressure (read to the death). Built. A prot
    or heal let through with an interrupt ready is a fault of the attack's, by name (R-850): to be built, what counts
    as let through put to him first.
66. **The spike thrown, and Aegis** (R-837): skills and attacks aimed at one player whose usual damage adds to 400 or
    more inside 3 s, whatever landed, each skill at what a cast of it did for its caster this match. Aegis is read on
    these, no longer than 3.6 s from its cast: the spells that stopped on it, what landed, whether he died and when.
    A record and its sentence (`execution.thrown`, `say_thrown`), said on the play's row (R-841): how many each side
    threw, how many landed too little to be a kill attempt, and each one that met Aegis. Not on the site.
67. **Shadow Shroud** (R-838, R-849): the attack's good play, kept by name on its check against the same teams' other
    spikes (+10.1, 8/10); to be built into `BY_NAME` with the next bundled change.
68. **Kept by name** (R-842): the strip before the first big hit on a spike (+9.4, 8/10) and a monk in reach down as
    the spike lands (+8.1, 7/10) stand though short of the groups bar (`execution.BY_NAME`). The bar stays 9 of 10
    for everything else; the check is said beside them after every full run; one that reads backwards goes to him.
    A strip before a burst (+2.2, 6/10) is not kept by name.

"Read" below: Yes, Partly or No on `bundle-4` as it stands; "Rule n" is the list above.

## A. The victim's own play (questions 1 and 2)

| Why | Read | What it needs |
|---|---|---|
| Pushed too deep, away from his monks | Read and kept, said nowhere: paused (R-834). As built, a why until it passes: at the first big hit, 1,200 or more past his own front line (the most forward team mate in the fight who is no backline monk), with his nearest monk's distance | |
| Pushed too deep, pulling a monk into pressure after him | Read and kept, said nowhere: paused (R-834). As built, a why until it passes: said on the kill attempt on the monk who followed (section B) | The same said on the deep player's own row |
| Balled up (Rule 7): Mind Burn, Teinai's Wind, scythe attacks; rarely Earth Shaker, Mark of Pain | Yes (stage 3): two or more players hit in one tenth by one cast that reaches adjacent foes, or by one scythe attack; listed on the play's row | Built (R-787): a cast that reaches nearby foes (Energy Surge, Lamentation) or foes in the area is the same fault; an effect on the ground never (R-793). A cast that strikes "up to two other foes near your target" (Invoke Lightning, Chain Lightning) lands on them one after another, half a second apart in the record: read at each step (R-847) |
| Standing in area damage (Rules 20, 38, 42): Chaos Storm, Symbol of Wrath, Ray of Judgment, Lava Font and the like | No: set aside for now (R-807). Built and read backwards on the full run (88 attempts with it kill 13.6% against 32.4%); `execution.area_hits` is kept | His word to bring it back |
| Knocked down by Bull's Strike (Rule 5) | Yes (stage 3): the knockdown record names the skill | |
| Crippled by Harrier's Grasp (Rule 6) | Yes (stage 3): a Cripple at a hit by an attacker with Harrier's Grasp up, no other Cripple skill cast on him then | |
| Crits and extra damage while moving (Rules 5, 8, 31): context only | Yes (stage 5), context on each attempt: the critical melee hits on the target while he was moving | The extra damage of Protector's Strike, Harrier's Haste and Weaken Knees (no skill on a hit) |
| In a stance that raises damage taken during an attempt (Rule 25) | Yes (stage 3): on every spike and pressure attempt, what landed while it was up and the share the skill added; Frenzied Defense only where spells landed (R-832). The check passes against the same players out of a stance (+11.8 points killed, 10/10) | Aggressive Refrain is context (R-788) |
| Fighting in reach of their NPCs when not pushing their pit | No | NPC damage taken, against his position and the team's job |
| Standing still when he should have kited a melee player (Rules 31, 41) | No: withdrawn (R-806). It read backwards on every counted match (28.1% killed against 32.5%) | |
| Attacking through Empathy (Rule 21), Clumsiness or Ineptitude; casting into Backfire (Rule 22), Shame or Diversion (Rule 24) | Yes (stage 3): each hit the hex did to him, told by the hex's own amounts; a spell lost to Shame, by the interrupt record's own skill (Rule 56), with how long the hex had been on him; a skill used as Diversion went | |
| Casting into a ready interrupt, not cancelling (Rule 28) | Yes (stage 1; R-789): an interrupted cast of a listed skill, the interrupt that stopped it ready when the cast began. Every player's is kept as context by player; a backline monk's inside the kill attempt that killed a player of his team is the fault, said on that death | |
| Wrong weapon set when under attack | Yes: the set he held at the first big hit, on every attempt and death (Rule 44), and on the sum what landed off his shield set and what a shield would have stopped (stage 4); said on a death only where a shield would have stopped something | As a missed chance, checked once; the set he swapped to |
| His own stance, escape or self-heal unused when ready | No | His own defensive skills ready at the attempt (Rule 1) |
| Fell back too late, or not to his monks | No | Movement towards safety once the attempt starts, against the time he had |

## B. The monks (questions 1 and 2)

| Why | Read | What it needs |
|---|---|---|
| Wrong spot: out of reach when the spike came | No | Each monk's reach to the players likely to be spiked, before the attempt |
| Followed an over-extended player into pressure | Yes (stage 5), a why until it passes: a kill attempt on a monk 400 or more past his front line, behind a too-deep team mate in reach | |
| Knocked down and could not cast | Yes | |
| Dazed, or inside his own aftercast (Rule 1) | Yes (stage 1) | |
| Himself the spike's target (Rule 32) | Yes (stage 1) | |
| Disabled (Power Block, Power Lock, Complicate, Blackout, Signet of Humility, Diversion) or under Shame | Yes (Rule 44): a disabled skill is not ready, a monk under Shame has no spell on an ally; said as "not a chance", and each monk's state at the first big hit is kept on the attempt | Complicate's reach to the foes in the area; Diversion on him before he has used a skill is context only |
| Backfire or Visions of Regret making his casts costly | No | Trigger tags; his casts while hexed |
| Out of energy | Yes: gvg.report's model, out under 20 (R-681) | |
| Busy on another player under pressure (R-711) | Yes | |
| Prot or heal ready and not cast | Yes, with Rule 1 (stage 1); his own on himself too (Rule 35); every ready skill named, with the monk's energy, what each would have done and the latest start that still saves him (Rule 45) | An interrupter's energy (the model reads monks and the midline) |
| Prot or heal begun that never landed (Rule 36) | Yes: context beside the death | |
| Prot or heal begun too late, cut off by the death (Rule 37) | Yes: a fault where he had an earlier moment at which the same cast would have landed | |
| Prot cast too early, ended before the spike landed | No | Each prot's end against the first big hit |
| Both monks on the same player while another died | No | Each monk's targets during the attempt |
| Wrong kind of prot for the damage | Partly: death accounts | Each prot's effect on each damage type, from skill text |
| Prots wasted on players nobody attacked | No | Prots cast against the damage that followed on that player |
| Shadow Shroud on the target: a missed prot under it is no fault | Yes (Rule 44): no enchantment is a chance while it is on him; kept on the attempt with its seconds | Whether a party-wide enchantment (Shield Guardian) lands on a Shrouded player (his to say) |
| Air of Disenchantment or Mark of Insecurity not removed or interrupted | Partly: hex removal over the play | Removal and an interrupt on the cast, as missed chances on the attempt |
| Barbs left on the target | Partly: hex removal over the play | A missed chance on the attempt |
| No Aura of Stability against a hammer warrior | Partly: death accounts | A missed chance on the attempt |
| Deep Wound not removed (Rule 10) | Yes (stage 3): still on the target at the outcome of a spike or pressure attempt, a removal ready on a backline monk in reach | |
| Daze left on another monk (Rule 10) | Yes (stage 3): a removal ready on another backline monk in reach and none cast | |

## C. Team support on defence (question 2, and question 1 from the defence's side)

| Why | Read | What it needs |
|---|---|---|
| No peel: no knockdown, Blind, snare or interrupt on the players hitting him | Partly: death accounts | A missed chance on the attempt |
| No defensive interrupt on a skill worth interrupting (Rules 12, 27) | Yes on a spike's skills (stage 1: listed skills, catchable, the interrupt's own time) | Any damage, not only spikes |
| Frontline attacking through Empathy when defensive (Rule 21) | Yes (stage 3): said from the play's objective, the warrior's fault when defensive, the monks' when offensive | |
| Frontline not stopping their frontline or midline when defensive (Rule 13) | Partly: targets judged by the job | Midline as a right target when defensive |
| No condition removal from a non-monk who carries it (Rule 11) | Partly: over the play | The team's bars at the attempt |
| A dead player not ressed, or the res cast into a ready interrupt | Partly: res timing and res stopped | Res as a missed chance after each death, with Rule 1 |

## D. The attack (questions 1 and 3)

Two kill attempts are read: a spike (400 or more damage on one player in 3 s, or a burst that takes most of the health
he had: two thirds of it and 200 or more, R-780) and a pressure attempt (a player kept at or under 225 health, R-779,
for a second or longer with 90 or more landing on him in 3 s, hits and degen; Rule 26). Question 3 lists every attempt of either kind over the play, each with its sum.

| Why | Read | What it needs |
|---|---|---|
| Damage off-timed, not landing together | Yes | |
| Strip missing or off-timed (Rule 14) | Yes (stage 1): listed on each spike that did not kill, the check's result beside it; a strip in time said as good play; which strips are thrown on demand is read from the tags (stage 3, R-773). The strip that matters is Rule 64 (R-835). The check: before the first big hit +5.8 points killed (+2.1 to +9.4, 7/10; on spikes alone +9.4, 8/10); a strip taking a prot or heal that landed during it, against one that landed and stayed, +8.3 on spikes and +3.7 on bursts (both 9/10) | The checks on the full run with Rule 64 as amended (R-839, R-840); a strip before a burst (+2.2, 6/10) is not kept by name (Rule 68) |
| Deep Wound missing or off-timed on the spike (R-751) | Yes (stage 3), a why: on him at the first big hit, when it came, who in reach carried it | Whether the skill was ready: adrenaline is not in the replays |
| A damage player with his skill ready who hit another target (R-751) | No: dropped for now (R-809). Built and read backwards (spikes with it killed 4.7 points more, in every group of ten) | His word to bring it back |
| Enchantment prevention not used: Shadow Shroud | Partly: where it was used is kept on every attempt (Rule 44) and checked once as the attack's good play (+10.1 points killed against the same teams' other spikes, 8/10: 38 teams, too few for the bar); kept by name (R-849), to be built | As a missed chance of the attack's: carried, ready, in reach and not cast |
| Their monks not pressured: interrupts, knockdowns, Daze | Yes (the missed chance fails the check: never a fault). Said as the attack's good play (Rule 65, R-836): a prot or heal for the target stopped +10.0 points killed (10/10); a monk in reach down as the spike lands +8.1 (+4.8 to +11.8, 7/10), kept by name (Rule 68) | A prot or heal let through with an interrupt ready as a fault: ruled by name (R-850), to be built |
| Their monks not disabled, cast-prevented or drained | Partly: each of the target's monks knocked down, Dazed, disabled or hexed at the first big hit is kept on the attempt (Rule 44) and checked once | As a missed chance of the attack's; energy drained |
| Spiked into a block or spell immunity (Aegis, Guardian, Mirage Cloak, Spell Breaker, Obsidian Flesh) | Yes (stage 3), a why: his enchantments, stances and weapon spells at the first big hit whose text blocks attacks or bars enemy spells; a block is said only where more than a third of the spike is attacks (R-831), immunity only against a spike with spells. A block passes the check (-6.4 points killed, 10/10). Immunity is Aegis alone, read on the spikes thrown (Rule 66, R-837): 368 thrown into it, 315 spells stopped on it; where it came during the spike 1.7% died against 22.4% of the spikes with neither Aegis nor a block whose target was still alive at that moment; a block at its start -10.3 points killed (10/10). Said on the play's row (R-841); the record keeps the time of death, and section J sets Aegis coming during a spike against the targets still alive then | On the site |
| Spiked into a ward or a spirit (Ward Against Melee, Shelter, Union, Displacement) (R-751) | No: not in the records (the limits) | A ward's place and length from its cast; a spirit has no position in the replays |
| Wrong target: frontline over monks when trying to kill | Partly: over the play | Per attempt |
| Frontline hampered: Empathy, Faintheartedness, Blurred Vision, Insidious Parasite; also Clumsiness, Sum of All Fears, Shadow of Fear, Ineptitude, Price of Failure, Spiteful Spirit, Blind, Weakness | No | Their hexes and conditions on our attackers during the attempt, and whether they were removed (a why; a fault only where Rules 21 and 24 say) |
| Frontline snared and could not reach the target | Yes (stage 5), a why, not a fault (R-804): each frontline attacker Crippled or under a slowing hex and out of melee reach of the target for a second or longer of the attempt (Rule 23's skills left out) | |
| Flail lock (Rule 9) | Yes (stage 5): in Flail for more than 2 s with no enemy player or NPC within 250, listed on the play's row (the one reading from positions tied to no attempt, after R-806 and R-807) | Said on the attempt it cost |
| Attackers knocked down, interrupted or out of range | Partly: from the victim's side | The same read from the attackers' side |
| Time lost chasing a kiting target | Partly: kiting measured | Per attempt |
| Switched targets too early | No | Damage on a target against how low he was when they left him |
| Did not snare the target | No | Snares ready and unused on a target who escaped |
| The kill undone at once by Death Pact Signet or a quick res not stopped | No | Res casts after a kill against our interrupts ready (Rule 1) |
| The lead not kept long enough to convert | Partly: its length read; every attempt made during it listed with its sum (stage 4). Most plays with the job to kill make none (31% make one) | Whether making no attempt is a fault of its own (his) |

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
  (R-764). The interrupt reading does not lean on it: how long a cast took is the replay's own record. A prot's or a
  heal's chance does: it reads the tag file's cast time where the skill data has none (Rule 55).
- Health is in points: the weapon set in hand, 4.8 a point of morale or death penalty, less Deep Wound (within a point
  of gvg.report's recaps at 84%). Healing rows are heals as cast, overhealing in: what landed is read by walking the
  hits and heals in order. Deep Wound gives its health back as it ends (the sum balances only so).
- What never landed is not in the replays. Damage stopped and attacks blocked are gvg.report's, only in its recap of a
  death or a survived spike (97% of spikes, 44% of pressure attempts have one), and its credit for prots is small
  (nought on 72% of spike recaps; nothing for Aegis, Protective Spirit and Aura of Stability). So the amount beside a
  missed prot is not gvg.report's (it read 20 to 60) but each prot's own rule over what landed (R-784, below).
- 7% of deaths have nothing landed on the player in the record and mostly no recap: a third of them are pact kills
  (R-783, read from the signet's cast and the two deaths); for the rest the sum says so, and no fault is listed.
- A condition names no skill (a Cripple is told as Harrier's from the hit that brought it). A ward has no record but
  its cast, and a spirit no position: neither is read. Adrenaline is not in the replays: an attack skill is "ready" by
  its recharge alone. The replays spell eleven skills without their punctuation ("Harriers Grasp"): read by id.
- What a missed prot would have stopped is built (R-784, R-785, R-791): each prot's own rule over the hits that
  landed, the sum walked again with the prot on him: what it stops, what it heals, and on a death whether he would
  have outlasted what landed. Limits: a hit names no skill, so attack or spell is told from what its source was
  doing (within 10 points of gvg.report's recaps on 77% of them); a third of the monks have no Protection Prayers
  rank in gvg.report's record (the usual rank of those who carry the skill is read, and said); a block is an
  average; the reading ends at the death, and attackers change target when they see a prot: an upper bound. Wards
  and spirits are left out; Protector's Defense, the shouts and chants are never a missed chance.
- A hit of an effect that stays on the ground names no skill either: it is its caster's row on a player a whole
  number of seconds after the cast finished, of the one amount the effect does him at every beat (40 or 42 a second
  for Symbol of Wrath, the skill text's figure). gvg.report's recaps cannot check it: they put the caster's other
  spells under the area skill (18 recap rows on the development set, none agreeing). Checked against the raw rows.
- Armour and insignias are left out: a player cannot change them in a match. Out of reach: ping, line of sight around
  obstacles, calls and intent (R-371).

## Order of work (all on `bundle-4`, before the close; his marks after it, R-752)

| Stage | What | Done when |
|---|---|---|
| 1. The built kinds on the new rules | Built: Rules 1, 12, 27 and 32 on the prot, the heal and the interrupt on a spike skill; the lists as a data file; failed spikes listed with the strip missed (Rules 14, 29); Rule 28's filter on casting into a ready interrupt. No full run of its own (R-766) | development set and key pass; plays unchanged (they do) |
| 2. The skill data | Done but for the sync: every skill in use tagged in a file of its own, `data/model/skill_tags.json` (`data/skills.json` is never edited by hand), reviewed by Denning (R-753 to R-765). Left for later: the wiki sync's missing cast times | Denning has reviewed the tagged list (he has) |
| 3. What the records already show | Built (2026-11-27), with the tag file: Bull's knockdown, Harrier's Cripple, balling, Empathy and the other triggers, damage-raising stances, a spike into a block or spell immunity, Deep Wound on the spike, an attacker on another target, Rule 10's removals; the interrupt's reach and strips on demand from the tags; untagged skills listed. Not built: wards and spirits (not in the records), Rule 11 (a non-monk's removal, read over the play as before). No full run of its own (R-766) | each join checked against the raw record (R-707): done; each kind checked once on unseen matches, shown beside the ruled ones (Rule 29): at the full run |
| 4. The ledger and the pressure attempt | Built (2026-11-27): each part of the sum a measured amount on every attempt, for both teams (Rule 19), and an amount beside each missed chance (a missed prot's by its own rule, R-784 to R-791, with whether he would have lived); the pressure attempt beside the spike, its cut-off from data, degen counted; the even 8v8's row; question 3 on every play to kill and every numbers advantage, the enemy's credit apart. No full run of its own (R-766) | question 3 read attempt by attempt; the heaviest 2 s retired (Rule 33): both done; development set and key pass, plays unchanged |
| 5. Readings from positions | Built (2026-11-27): too deep and monk following on every kill attempt and death (whys until they pass), Flail lock, standing in area damage and should have kited on the play's row, the snared frontline as a why on the attempt, crits while moving as context; `cases.py positions` reads the cut-offs and checks each kind once | cut-offs set from data (Rule 26); development set and key pass; the full run checks each kind |
| The runs (R-766) | Built in the order 1's remainder, 4, 3. Then one full run with every check for stages 1 to 4 together: `cases.py attempts` and `execution` (do the kinds still pass on unseen matches?), the key, the truths, `execution_rows.json`. Stage 5 has its own full run, before X4's sentences | the three built kinds still pass on unseen matches; each new kind checked once |
| The bundled change (R-805 to R-810) | Built (2026-11-27, evening): the cut-offs from the full run; should have kited, standing in area damage and an attacker elsewhere out; the interrupt on a spike only; Rules 44 and 45; the tests of the stage 3 and 4 kinds in `cases.py attempts` (section H); the win chance over the match (`cases.py winchance`). The faults said on each death in the match report's wording (stage X4), the Execution view's rows on main | development set and key pass, plays unchanged (they do); one full run by Opus |
| His marks (stage X5) | Men v Crew (15 deaths, R-811 to R-821), RACK v hdm (10) and Men v NwAy (12 of 21; R-822 to R-830) marked and actioned, each in one bundled change; the rows written again after each | his marked rows read as he reads them (they do; nine deaths of Men v NwAy are not marked) |
| Then | The full run's verdicts brought to him | his Classic execution rows read as he reads them |
