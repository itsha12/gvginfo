# Tactics for match analysis

Denning's tactical concepts, used when analyzing match replays. Lines starting **Denning:** are his own definitions and
override everything else. **Measure:** lines say how each concept is detected in the replay data (proposals, refined as
matches are reviewed). **Open:** lines are questions the match data should help answer.

## What the analysis is for
- **Denning:** Insights must be about decisions and their consequences: who did what, when, and why it decided the
  fight. Correlations such as "capping is good", "interrupts are good", "damage is good" or "deaths are bad" are not
  insights.
- **Denning:** Examples of the kind of insight wanted (hypothetical): a team ran a flag and fought 8v7 while pushing it;
  the other team double ran the flag to get up on flags, which let them play the power play while the first team was
  running; a team got behind on flags because the enemy ranger pushed their flagger with cripple and they did not
  collapse; a critical interrupt on Healing Burst at 7 minutes caused a wipe; a team failed to prot damage or interrupt
  defensively when fighting 7v8.
- **Denning:** The goal is to learn what winning guilds do differently from losing ones.

## Map and team language
- **Denning:** Each team's end of the map is its **base** (not "home"). The res shrine is at the base.
- **Denning:** **Backside** is the side of the map closest to your own base. **Push side** is the side closest to the
  enemy base. North and south don't matter; describe positions as backside and push side.
- **Denning:** Refer to players by role, not character name: prot monk, 7 monk, 8 monk, running mesmer, stand mesmer,
  hammer warrior, and so on.
- **Denning:** The 7 monk and 8 monk are the healing monks in party slots 7 and 8, with the prot monk in slot 6. The 7
  monk is usually the push monk and the 8 monk is on the backside.
- **Denning:** The prot monk follows the 3rd damage: each monk can usually survive 2 damage with team support, but not 3,
  so the prot has to mirror the 3rd damage.
- **Denning:** The stand mesmer is the main shutdown mesmer. The running mesmer is called the Mes/A; it usually has a
  running skill, but not always.
- **Measure:** roles come from each player's build and party slot. Positions are labelled by side relative to the
  player's own team (backside, push side, base, enemy base, stand).
- **Denning:** Players are resurrected at their base (res shrine) every 2 minutes as long as they have less than 60%
  death penalty. Death penalty lowers health and energy.

- **Denning:** The NPCs in the enemy base are the pit NPCs (not "guards"); the area around the Lord is the pit (not
  "lord room"). Archers outside the pit are outside archers (not "wall archers").

## What a review covers
- **Denning:** A review explains what led to the win condition, for example: did a team push the base and not get
  followed; did a team fail a collapse; was there a mistake on the flag; were critical deaths caused by lack of
  support or monk errors, or by really good plays such as knockdowns and interrupts.
- **Denning:** Kinds of game, and how much review each needs:
  - Stomps (one team far stronger, or a lopsided build matchup): a short summary is enough.
  - Games between similar good teams (for example hdm, xxx, Men, HC, HH, 옷옷옷옷): won on macro, on very good individual
    plays that a team capitalizes on, or on build differences and disadvantages.
  - Games won or lost on very small micro play (interrupts, monk play, good hammer play in a 3v3), even between
    evenly matched teams.
  - Chaotic games, for example when good guilds play [push].
- **Denning:** A match review is about the overall scope of the game. A player's own play only matters to the review
  when that player was a factor in the result.

## Builds
- **Denning:** Each review starts with a short summary of both teams' builds by role, e.g. AoB dervish, Coward hammer,
  2 E-surge mesmers, Life Sheath on the prot, Aura of Faith on the 8 monk.
- **Denning:** It is not uncommon for a team to run only 1 Aura of Stability. 1 Aura of Stability into 2 hammer warriors
  is worth a call out. Aura of Stability only prevents knockdowns on another ally, never the caster, so it does not
  protect the monk casting it.
- **Denning:** Call out skills that matter for the matchup as they are learned, e.g. having Infuse Health or not against
  a spike build, or 1 or 2 Purge Signets against a hex build or an AoD build.

## Types of game
- **Denning:** Some games are fought 8v8 (holding the flag) or 7v7 (with 1 player running the flag).
- **Denning:** The **flag game**: 2 or 3 damage, the prot and the 7 monk push the enemy flag, the enemy does the same,
  and each team defends its own flagger with 1 or 2 damage and the 8 monk.
- **Denning:** **Solo splits**: one player goes through the back or an unconventional route to try to kill the enemy pit
  or NPCs. This is sometimes defended by the 8 monk or by 1 damage, and sometimes teams collapse on the splitter to
  kill it.
- **Denning:** Whether a solo split is worth it depends on how effective it is and what it accomplishes; it may cost a
  team one game and win it others.
- **Open:** when a solo split pays off, measured across many matches (what it killed or drew away against what it
  cost the main fights).
- **Denning:** A good answer to a solo split: one player collapses on the splitter (for example the dervish killing a
  splitting ranger) while another defends (for example the Mes/A).
- **Denning:** **3 or 4 man splits**: a group pushes the enemy's backdoor to try to take NPCs.
- **Denning:** Sending the 8 monk alone against a 3 man push is a mistake; that monk needs support.
- **Denning:** All of these need to be understood; a match can move between them.
- **Measure:** each team's groups every few seconds (who is with whom and where), so each phase of a match can be
  labelled: 8v8, 7v7, flag game, solo split, or 3 or 4 man split; plus who answered a split and how (8 monk, 1 damage,
  or a collapse) and what it cost or gained (NPCs killed, kills, flag time).
- **Measure:** position jumps from Aura of Displacement are real, not recording errors: the caster Shadow Steps to the
  target foe, then returns to where they started when they stop maintaining it.

## Flag running
- **Denning:** Running the flag costs pressure. A frontline runner puts out basically no damage with the flag in hand.
- **Denning:** A midline runner can't use their 40/40 set, so they cast fewer skills, have less energy, and are more
  likely to be interrupted. They can't be in their shield set, so they take more damage when attacked. Their position
  is compromised: they are in range of the enemy frontline and can't kite. Carrying the flag also slows the runner
  (25%, see GvG match rules).
- **Measure:** carries come from the flag timeline (pickup to drop or capture). For each carry: the runner's role
  (frontline, midline or backline by build), their damage and casts during the carry compared with the rest of their
  match, damage taken, interrupts suffered, and the number of their teammates left in the main fight.

### Double running
- **Denning:** Double running means using 2 players to run the flag. It gets a team up on flags faster, but the team is
  essentially fighting 2 players down, which costs pressure.
- **Denning:** Half running: one player runs the flag halfway and drops it to another player, then runs back for a second
  flag while the other player caps.
- **Denning:** Full running: one player runs back or waits back for the next flag while the other player caps.
- **Denning:** Half running and full running are both types of double running.
- **Measure:** half running = a drop by one player followed within a few seconds by a pickup by a teammate near the
  same spot, then the first player heading back toward base. Full running = a teammate picking up or waiting at base
  for the next flag while the first runner is still carrying or capping. Track how long each team plays with 2 players
  away from the main fight.

### Power play
- **Denning:** When the enemy is running the flag, the team with more players in the fight can play the power play.
- **Measure:** players in the main fight for each team every second (alive, within casting range of their team's fight
  centre), so 8v7 and 8v6 windows stand out, and what each team did with them (pressure, kills, deaths).
- **Open:** when the power play should be pushed hard and when it is safer to hold.

### Pushing the flagger and collapsing
- **Denning:** When one enemy player solo pushes the flagger, the flagging team should likely support the flagger by
  sending players back to assist: a monk to heal, or a few damage characters to train the pusher out.
- **Denning:** Sometimes a flagger has to flag through one damage character, and that's fine.
- **Denning:** The right number of players to send is not known; that is what the games should teach.
- **Measure:** an enemy within casting range of the carrier who damages or snares them (cripple and other snares,
  knockdowns, interrupts); which teammates move toward the carrier and how soon; the outcome (capped, flag dropped,
  carrier died, pusher killed or driven off) and what it cost in the main fight.
- **Open:** how many players to send back, and when, depending on who is pushing and the state of the main fight.

## Pit NPCs and the 28:00 tiebreak
- **Denning:** One of the values of taking pit NPCs during a match is that fewer players need to be sent to the enemy
  base at 28:00 (winning on Lord damage at the very end) while still breaking Entourage.
- **Denning:** Protting your own NPCs instead of your Lord is deliberate: enchantments on your own Lord cost
  aggressiveness.
- **Measure:** the Lord's Entourage casts (a gap = suppressed), attackers near the Lord against the pit NPCs
  still alive, Lord damage by minute, and enchantments or weapon spells cast on each team's own Lord.
- **Open:** whether RACK splits through the front door or the backdoor on Isle of Meditation (Denning thinks the front
  door; check against the map).

## Not running the flag
- **Denning:** Not running the flag can be a deliberate choice. A team already on death penalty and under pressure may not
  be able to run without the rest of the team being wiped, because running costs so much pressure.

## Flag running on the 8 monk
- **Denning:** Running the flag on the 8 monk is a bad move. Teams normally only run on the 8 monk when 2 enemy damage
  are dead or when they are very desperate.

## Spike builds
- **Denning:** WoC spike (Word of Censure spike): several Mo/A smiters spike with Word of Censure. Even with so many
  monks it has low healing and defense, so it is considered an 8v8 build. The counter is to split hard, or to survive
  a few spikes and then wipe them.
- **Denning:** Against a spike build, call out a lack of interrupts on the spike skills, and call out when a team spikes
  really well: for example, 600 damage landing within 0.2 seconds can't be saved by any prot or Infuse.
- **Denning:** Winning on Lord damage at 28:00 isn't viable while taking deaths against a spike build like WoC; the team
  would not survive 28 minutes.
- **Measure:** for each death: the largest damage landed in any half second, from how many players, and how long from
  the first big hit to death (under about half a second = not saveable); prots up on the target when the spike started;
  interrupts landed on the spike skills.

## Spike defence
- **Denning:** For a spike, the analysis should name the primary failure, such as lack of prots, late infuses, or lack of
  interrupts on spike skills.
- **Denning:** Pre-protting is correct play, not a mistake.
- **Denning:** Whether a prot was unavailable because of energy or recharge does not matter for the analysis; both point
  to other issues (inefficient casting or overprotting).
- **Measure:** for each spike (a death, or 400+ damage in 3 seconds): prots on the target before and during the spike
  and when they landed, Infuse Health timing against the target's health, interrupts landed on the enemy's spike
  skills, and what the target's monks were casting at the time.

## Monk play under pressure
- **Denning:** Against energy denial, the monk casts from the shield set (hiding energy). Enchantments are cast from the
  staff, which gives 20% longer enchantments. The monk swaps to the single high energy set when low on energy.
- **Denning:** Space the ranger (stand further away): the further the ranger is from the target, the longer arrow
  interrupts take to land, so the ranger needs quicker reactions; a very quick monk can also dodge some arrows by
  moving back and forth.
- **Denning:** Against 2 damage, getting dazed is critical. Guardian yourself and/or cancel cast (fake) to bait the daze
  skill. After faking the daze skill, the monk can cast safely for a while, because the daze skill is expensive and the
  ranger will be low on energy. Keep the ranger targeted to track this.
- **Denning:** Spacing means the monk stands as far as possible from the enemy mesmer (and ranger) while staying in cast
  range of the 2 players they have to heal, and in the correct position (for example in front of their own mesmer,
  not behind). The monk only needs to be in range of allies while those allies are taking damage.
- **Denning:** There is no concept of "holding a spot for the flag"; a monk waiting for their mesmer to run the flag is
  there to support the runner, and should still be spaced.
- **Denning:** When the Mes/A is not carrying the flag, it should be interrupting the enemy mesmer defensively when that
  mesmer is pressuring its monk.
- **Denning:** A monk under 2 damage needs team support: for example, the dervish hits the ranger and the mesmer
  defensively interrupts the enemy mesmer.
- **Measure:** the monk's distance from the enemy mesmer and ranger, compared with the distance to the allies taking
  damage at that moment (spaced = as far from the attackers as cast range to those allies allows); cancelled casts (a cast stopped without an interrupt) and which
  enemy skill followed within a second (a successful fake); how long the monk was dazed; which weapon set the monk
  cast from while under energy denial; peel = teammates' attacks (auto-attacks as well as skills), knockdowns and
  interrupts on the players attacking the monk.

## Weapon sets
- Source: Guild Wars Wiki (Energy hiding, Weapon swap), pulled 2026-11-04.
- Energy hiding: swapping to a low energy set (for example a martial weapon and shield) lowers the available energy
  pool, so energy denial can take less; the hidden energy comes back when swapping to the casting set. A shield set
  gives -5 energy; with a +10 to +17 energy primary set, up to 22 energy can be hidden.
- A 40/40 set is a wand and offhand that each have a 20% chance to halve casting time and a 20% chance to halve
  recharge of spells (together about a 36% chance of at least one, not 40%). A midline carrying the flag can't use it.
- **Measure:** gvg.report flags which of a player's sets cast faster (HCT) and which lengthen enchantments; the replay
  records which set a player held each second (a flag carrier shows no set).

## Interrupts
- **Denning:** An interrupt can be critical, for example an interrupt on Healing Burst that leads to a wipe.
- **Measure:** each interrupt records the interrupter, the skill used, the interrupted skill and who it was aimed at;
  follow that player for the next 5 to 10 seconds to see whether the interrupt decided the fight.
