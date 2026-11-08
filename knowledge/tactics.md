# GvG tactics

A working model of how GvG matches are won, organized by situation, so a match can be read and a decision judged
against general principles rather than past games. Match-by-match evidence lives on the Match reviews page.

**How to read this page**
- **Denning:** lines are Denning's own and override everything else.
- **Bounty:** and **Nick:** lines come from expert commentary (sources on the Match reviews page). Bounty's lines are
  confirmed by Denning except where a Denning line corrects one; Nick's stand until Denning corrects them.
- **OG comms:** lines are what OG (a top team) said on its own voice comms, checked against the replay.
- **Claude:** lines are Claude's generalized learnings from replays. They are proposals until Denning confirms or
  corrects them, and are revised when new matches contradict them. Each ends with its evidence, as match tags
  (for example [Men v Team]) that point to entries on the Match reviews page.
- Each principle has an id (for example `F1`) that the analysis engine's findings, Denning's rulings and the situation
  cards cite. A revised line keeps its id; a removed id is not reused.
- **Claude, confirmed by Denning:** lines are Claude's reasoning that Denning has confirmed; how much each matters
  still comes from data.
- The causal map page links these lines into the model's structure (what can cause what).
- Principles are stated generally; the evidence shows where they were seen. A principle with one match behind it is a
  hypothesis; one seen across several matches with different teams is a pattern.

## 1. How matches are won

### Win conditions
- `W1` A match ends when a Guild Lord dies, when a team resigns, or at the 28:00 tiebreak on Lord damage.
- `W2` **Denning:** Teams resign when a match is lost (RACK resigned against Men).
- `W3` The 28:00 tiebreak is aggressiveness: +1 per point of damage to the enemy Lord, -50 per enchantment or weapon
  spell on your own Lord (GvG match rules page).
- `W4` **Denning:** One of the values of taking pit NPCs during a match is that fewer players need to be sent to the
  enemy base at 28:00 while still breaking Entourage.

### The edges that decide the win condition
- `W5` A Lord dies when one team brings more to the enemy pit than it can hold. That comes from edges built up over the
  match, which together are the **scoreboard**:
  - **Flag position:** which team is better placed to make the next capture and get the next boost (section 5).
  - **Morale:** boosts from holding the stand remove death penalty and raise the Lord's Health; death penalty lowers
    health and energy.
  - **Numbers:** players alive, players away (running, splitting, dead), and when the dead come back.
  - **Pit NPCs and Entourage:** every knight, archer and the Bodyguard taken makes the final push cheaper; an intact
    pit kills attackers.
  - **Position and territory:** where the fight happens (the enemy's side, near its pit, or yours).
  - **Time:** the res timer every 2 minutes, and the clock toward 28:00 (Lord damage).
  - **Builds:** what each build can still do in the time left (section 7).
- `W6` **Denning:** Individual deaths don't win the game. What matters is the game state that caused a death (flags,
  positioning, micro mistakes) and what the death caused. The flag game, death penalty and pit NPCs are all very
  important in close games.
- `W7` **Claude:** Read a match by tracking the edges: who gained which, when, and through what decision. The decisive
  moment is usually where one edge was converted into another (a kill into NPCs, a boost into a push, numbers into a
  wipe). A fight is judged on three questions: what put the team there (cause), how it was played (execution), and
  what it cost until everyone was back (consequence). [Men v Team] [OG v chic] [OG v cope J] [OG v hdm] [OG v cope U]
- `W8` **Denning:** A team already winning (pit taken, ahead on death penalty, boosting, ahead at 28:00) has no need to
  risk a Lord kill in a close window. The safer play is to back out, wait for the res, and fight again with the
  advantages; with no pressure to end, it can always win at 28:00. [hdm v HC I2]
- `W9` **Claude:** An empty enemy pit is converted when it is safe: a team that is behind, or racing the clock, takes
  the Lord in the next wipe window; a team that is ahead uses the empty pit as leverage and keeps its lead.
  [hdm v HC I2] [Men v HC C]
- `W12` **Denning:** A pit knight is worth about as much as a death. (Measured on 133 matches against matched moments
  without the event: a knight lost -9.0 win points, a death -8.9, the Bodyguard -8.3, an archer -3.2, knowledge/values.md.)
- `W13` **Denning:** In mid-game (about 6 to 12 minutes), teams that look beaten still come back about one time in five,
  as he sees in his games. (The win model's held-out calibration: teams given about 3.5% then won 21%.)

### Phases, plans and jobs
- `J1` **Denning:** Fights are global: everything in a match affects everything else. A team splitting has a different
  ability to run the flag; flag plays affect numbers and the ability to take NPCs.
- `J2` **Denning:** A 4v3 can be intentional, so the other side can fight 5v3. The 3-man weak side then has a different
  objective because it is the weak side: play defensive and safe (no deaths, keep the enemy group busy, don't chase) to
  allow the other side its power play. Judge each group by its job, not by its local fight.
- `J3` **Claude, confirmed by Denning:** A 5v3 fails to convert when the heads hide little damage against the
  defenders' healing (5 with 2 damage against 3 with 2 monks), when its damage is shut down (interrupts, knockdowns, Blind, snares), when
  its bursts don't line up, when it doesn't commit, or when the 3 kite into their pit, NPCs or res shrine.
- `J4` **Claude, confirmed by Denning:** A lone ranger split drawing the Mes/A and the 8 monk is a 1-for-2 exchange, and
  its value is mostly whether main converts the 7v6. The ranger dies to snares or a fast collapse, an escape on
  recharge or interrupted, going too deep into knights and the Lord, or staying after a second defender arrives. The
  7v6 may not kill because the damage-to-healer ratio barely changed (a damage dealer left for a monk and a mesmer).
- `J12` **Denning:** Healers per side only matter through damage. 3 healers and 1 damage against 2 healers and 2 damage
  shouldn't be won by either side on the ratio alone: that 4v4 is even, the 2-monk side maybe a bit stronger. What
  decides a fight is the damage a group can actually put out against the healing and prots it faces (measured, not
  counted by heads: a mesmer is not a hammer).
- `J5` **Denning:** The 7 may also be unable to kill because it is behind on flags and has to run: its power play is
  shorter than its numbers suggest.
- `J6` **Denning:** A power play has a limited window (until the enemy runner is back); the team must capitalize on it.
- `J7` **Denning:** Collapse timing is very important.
- `J8` **Denning:** A good team waits for its players to come back from the res before fighting.
- `J9` **Denning:** Damage is lost to interrupts, knockdowns, Blind, Weakness, carrying the flag, kiting and peeling.
- `J10` **Denning:** A team can play well in micro and macro and still run into a build matchup that is very hard to
  win. How hard each matchup is has to come from data.
- `J11` **Denning:** Plans (8v8 brawl, flag game, split pressure, holding in the pit, power play, late Lord push) are a
  starting list: Claude finds more and amends them as more matches are analysed.

### Macro and micro
- `W10` **Claude:** A game is won on **macro** when one side had a structural edge before the deciding fight: more
  boosts, more pit NPCs taken, a numbers advantage, a better split trade, better flag position or timing. It is won on
  **micro** when the structure was roughly even and the deciding moment came down to execution: an interrupt, prot
  timing, an overextension, a knockdown. Many games are both: micro opens a door that macro walks through, or a macro
  choice turns a micro mistake into a loss. [OG v cope U]
- `W11` **Claude:** A useful test: if the losing team's decisions had been the winner's, would it still have lost? If
  yes, the build or execution decided it (micro or matchup); if no, the decisions did (macro).

## 2. Builds and matchups
- `B1` **Denning:** Matches are blind: teams don't know the enemy build in advance, so a build call out is about the
  matchup, not necessarily a mistake.
- `B2` **Denning:** Call out skills that matter for the matchup, e.g. having Infuse Health or not against a spike
  build, or 1 or 2 Purge Signets against a hex build or an AoD build. 1 Aura of Stability into 2 hammer warriors is
  worth a call out; running only 1 Aura of Stability is not uncommon. Aura of Stability only prevents knockdowns on
  another ally, never the caster.
- `B3` **Bounty:** Don't take a meta build and change its key skills; it creates holes. Copying a build without knowing
  how it is played doesn't work, especially a spike on an open map.

### 8v8 builds (spike and hex)
- `B4` **Denning:** Spike and 8v8 builds want to fight 8v8 and keep their damage together; they are sometimes called
  6 damage builds.
- `B5` **Denning:** WoC spike: several Mo/A smiters spike with Word of Censure. Even with so many monks it has low
  healing and defence, so it is an 8v8 build. The counter is to split hard, or to survive a few spikes and then wipe
  them.
- `B6` **Denning:** Winning on Lord damage at 28:00 isn't viable while taking deaths against a spike build like WoC;
  the team would not survive 28 minutes.
- `B7` **Bounty / Nick:** Double Paragon spike (Decapitate axe or assassin, Angelic Bond and "The Power Is Yours!"
  paragons, a WoC monk, a mesmer, 3 monks) is a beefy, strong 8v8 build, a little weak against splits. With Shatter
  Storm it strips prots; with only Shatter Enchantment its spikes are obvious and can be protted.
- `B8` **Nick:** Decapitate (always crits, unblockable, up to +80 damage) hits for about 130 to 150, about 250 with Deep
  Wound. Decapitate into Protector's Strike kills monks. [Men v Team]
- `B9` **Denning:** Invoke spike: air elementalists spiking with Invoke Lightning (plus Lightning Strike, Shell Shock,
  Blinding Flash), usually with only 2 monks. The Rit/Para calls, gives speed, and puts Deep Wound on the target.
- `B10` **Bounty:** Monk spike (Mo/A WoC with Return) comes in a mobile big-damage version and a version that stands its
  ground. The mobile version must be snappy (Return, Dash), always chasing; if it is slow, the enemy sets up on both
  fronts, the worst case for it.
- `B11` **Denning:** In hex way, a ritualist in the 8 slot (not a monk) is normal.
- `B12` **Bounty:** Hex way is a hard matchup for triple melee; the mesmers have to do a really good job.
- `B13` **Claude:** A spike build's fate is decided by whether its spikes land in the first minutes. If they do, it
  snowballs on death penalty; if the enemy catches them, a 2-monk spike loses the long game to hexes or pressure. The
  same OG invoke build went 18-1 and 1-18 against two hex ways; the difference was the enemy's spike catching and
  shutdown, not OG's play. [OG v cope J] [OG v hdm]

### Balance and pressure builds
- `B14` **Bounty:** Against a pressure build, expect the pressure team to kill slowly and the spike team to kill one
  player quickly.
- `B15` **Bounty:** A ritualist, two mesmers and two melee is a jack-of-all-trades build: decent at everything,
  exceptional at nothing.
- `B16` **Nick:** On Isle of Weeping Stone a Test of Faith Balthazar dervish (8v8 pressure) beats a Cryptic dervish,
  since the map has little flag pushing and a split can't be collapsed on through the centre.
- `B17` **Claude:** Balance mirrors tend to become long, low-death games decided by the flag game, NPCs taken and one
  late mistake or one backline wipe; neither side can force kills through equal backlines. In double hammer mirrors
  the wipe comes from knockdowns on the prot (Coward, Hammer Bash) chained with mesmer and ranger interrupts on the
  other monks' heals and prots. [OG v cope U] [hdm v HC I1] [hdm v HC I2] [hdm v Men N] [Men v HC C]

### Key skills in spike matchups
- `B18` **Bounty:** The tools for catching spikes: Reversal of Fortune on the 8, Life Sheath and Spirit Bond on the
  prot, Infuse Health on the 7.
- `B19` **Nick:** Against a build with a single enchantment remover, stack prots (Life Sheath or Aura of Faith plus
  Spirit Bond); Aura of Faith alone gets shattered. Life Sheath compresses the prot's bar, leaving room for Spirit
  Bond, Shield Guardian and a stance.
- `B20` **Nick / Bounty:** Blessed Light (5 energy) is a heal, hex remove and condition remove in one, which frees slots
  for Shield Guardian, Vigorous Spirit and Infuse Health.
- `B21` **Claude:** Where a team's prot answers sit matters as much as having them: if the only Spirit Bond and Reversal
  of Fortune are on the 8 monk and the 8 monk is away on a split, the main team has no spike answer. [Men v Team]
- `B22` **Claude:** Knockdown lock on the prot needs Aura of Stability on a second monk (it never covers its caster).
  Double Paragon WoC's warrior locks the prot down with Grapple and Bull's Strike before the kill, and both teams that
  had their only Aura of Stability on the prot lost their prots and 7 monks to it. Against double hammer a second Aura
  of Stability helps but doesn't stop it. [Men v Team] [RACK v hdm M] [hdm v HC I1] [Men v HC C] [hdm v HC I2]

## 3. Splits

### Forms
- `B23` **Denning:** Builds means individual bars too: one skill can change the right play. A Mes/A defending 1v1 with
  a snare should play differently from the same Mes/A without one. And team builds change what results are worth: a
  2-monk spike build is behind on Lord damage late, so pit NPCs matter less to it and DP matters a lot. After killing
  the enemy team, most teams prefer to push for NPCs rather than build DP; for that spike build the weighing is often
  reversed. **Claude (data, `values.py`, 133 matches):** a pit NPC taken by a spike build cost the defenders 4.8
  win points against 6.2 when taken by other builds; a death against a spike build 8.2 against 9.7 (all clear; the
  gaps between them are small).
- `S1` **Denning:** Solo splits: one player goes through the back or an unconventional route to hit the enemy pit or
  NPCs. Defended by the 8 monk or 1 damage, or collapsed on.
- `S2` **Denning:** 3 or 4 man splits push the enemy's backdoor to take NPCs; a 4 man split is a **4-4**.
- `S3` **Bounty:** A 4-4 split (e.g. two elementalists, a mesmer and a monk, the main team playing without its prot) is
  a very offensive split.
- `S4` **Denning:** A match can move between 8v8, 7v7, the flag game and splits; all need to be understood.
- `S5` **Denning:** A **full team collapse** is the whole team turning on an enemy group; it is not a split answer.

### When to split, and the trade
- `S6` **Denning:** Against a spike or other 8v8 build that out-damages you at main, splitting is right, and the split
  has to be aggressive, which usually includes the 8 monk for support. The main team then has to play in its pit.
- `S7` **Bounty:** A team whose build is worse 8v8 has to split someone (solo split, wait for it to be answered, then
  push the flag); pushing with all 8 into a better 8v8 build is a risk.
- `S8` **Denning:** 1 enemy damage held by 1 monk in base is usually a worthwhile trade for the splitting team: 4 damage
  kill 2 monks more easily than 5 damage kill 3. In that scenario it is up to the main team to win the game.
- `S9` **Denning:** Whether a solo split is worth it depends on how effective it is and what it accomplishes; it may
  cost a team one game and win it others.
- `S10` **Claude:** A split is judged by what it forces and what it takes. It must either draw more value than it costs
  (more defenders, or monks for damage) or take NPCs. A split that is answered like for like (damage for damage, monk
  for monk) only trades time. [OG v cope U]
- `S11` **Claude:** A split has to stay aggressive to keep its value: once it shrinks or stops threatening, the enemy
  answers it with fewer and the trade flips. [Men v Team] [RACK v hdm M]
- `S12` **Claude:** A split needs enough damage to beat the monks defending it. Two damage with the 8 monk can't kill
  two monks, or NPCs they heal; it only chips. Against a team that defends with its prot and 8 monk, the split needs a
  3rd damage (which also pulls the enemy prot's rule into play) or it will not take the pit. [Men v Team] [RACK v hdm M]
- `S13` **Claude:** A split that can't touch the Lord or knights only buys time; the game is then decided at main.
  [OG v chic]
- `S14` **Claude:** A lone ranger split left undefended can take a whole pit (both knights, the archers and the
  Bodyguard) in 2 to 4 minutes, which wins the tiebreak and makes the late push cheap. It has to be answered by a
  defender or a collapse; HC ignored it twice and lost every pit NPC both times. [hdm v HC I2] [Men v HC C]

### Who goes
- `S15` **Bounty:** When 3 damage are out on a split, the 8 monk should go with them, or the split achieves nothing.
- `S16` **Bounty:** Don't send both escape players (e.g. both Shadow of Haste characters) on a split; keep one in base.
- `S17` **Claude:** Taking the 8 monk off the split for another job (e.g. escorting a flag carrier) kills the split's
  value. [Men v Team]

### Defending a split
- `S18` **Denning:** Answering a split within about 15 s is on time; 60 s is definitely late.
- `S19` **Denning:** A lone ranger split is answered by the Mes/A, but the Mes/A can't defend alone: it needs collapses
  from a frontline to push the ranger out of the base.
- `S20` **Denning:** Defending a split with the 8 monk keeps all the damage at the main team: a risk that may pay off if
  the main team scores kills. It was likely wrong against hdm's ranger, but this needs data across many matches.
  [hdm v HC I2]
- `S21` **Denning:** Once the pit is dead, the 8 monk staying in base to defend the Lord is right: it is too hard for a
  Mes/A to defend a ranger alone with no pit, and some characters are very hard to defend 1v1 once the pit is dead.
  [hdm v HC I2]
- `S22` **Denning:** If the enemy prot is pushing with its team while 3 of your damage are on your push side, the enemy
  prot is out of position and your push side should be able to kill. [Men v HC C]
- `S23` **Denning:** The prot monk follows the 3rd damage: each monk can usually survive 2 damage with team support, but
  not 3, so the prot mirrors the enemy's 3rd damage, going wherever the enemy has 3 damage. (Bounty: a pit is defended
  against a split with either the third damage or the prot.)
- `S25` **Denning:** Sending the 8 monk alone against a 3 man push is a mistake; that monk needs support.
- `S26` **Denning:** A good answer to a solo split: one player collapses on the splitter (e.g. the dervish killing a
  splitting ranger) while another defends (e.g. the Mes/A).
- `S27` **Denning:** When defending 1v1, it is a big advantage if the defender can run its flag partway without losing
  anything (dying, NPCs): it shortens the team's next run while the solo pusher accomplishes nothing (see `F3`).
- `S28` **Bounty:** Against a solo splitter, a team can ignore it and fight 8v7 if it is winning the main fight.
  Answering a split with one damage is enough when the main team can finish the game.
- `S30` **Bounty:** An alternative against a single splitting mesmer: defend with both monks and push with the
  ritualist, since two monks survive better than a ritualist and a monk.
- `S31` **Denning:** A snare on the defender changes the answer to a lone attacker. Without one, the aim is to hold 1v1,
  part run or half run flags if possible and keep the NPCs up: a minor gain for the team; a collapse that doesn't kill
  just wastes the collapser's time. With one, the collapse is much more deadly, and the defender has one less skill for
  surviving or winning the 1v1, so holding alone is riskier and a missed chance: collapsing is most likely the better
  play. (Measured across splits in `S33`.)
- `S32` **Denning:** Whether to collapse on a split (the frontline leaving a main fight for the base) has no fixed line:
  it depends on the team's plan (whether it values NPCs or DP more), whether the defender can hold the attacker without
  losing NPCs, the flag position (is the frontline needed at main to keep a numbers edge for pushing a flag?) and how
  the main fight is going (is the frontline winning it?). The line is wherever the data says it is. (Measured: split
  decisions carry the defender's skills, split size, main numbers and health, flag lead and build axes.)
  **Denning:** A quick collapse that fails to kill costs, because it fails twice: no kill, and the split isn't pushed out
  of the base. (Measured, 133 matches: collapses away under 30 s -2.4 win points, collapses with no kill -4.2, those
  that killed a split member +2.9.)
- `S40` **Bounty:** When a split changes (e.g. made beefier), the defence must change too; defending the same way loses
  the pit.
- `S41` **Denning:** An 8v8 build answers a 3 man split by ignoring it with the main team and having a snare character
  in the 8 slot shadow it; when the split commits too deep, the 8 snares it so the spike characters can collapse and
  kill.
- `S33` **Bounty:** A monk spike defends against splits with the snare character and the 8 (the 6 snares, the 8 heals,
  the collapse kills). Collapsing before the snare lands is wasted time; the 8 following the main team leaves the pit
  open. **Claude (data, `comms_vars.py` collapse_snare, 144 matches):** splits answered by 2+ defenders killed a
  splitter 20% of the time with a snare carrier among them against 11% without, at the same numbers (+6.5 points,
  interval +1 to +13, supported; Return isn't counted as a snare). The order (snare first, then collapse) isn't
  measured yet. [Team v push] [BcS v Crew]
- `S34` **Bounty:** A fast ranger left at the back door can warn the team, take free footmen and lead the answer to
  splits.
- `S35` **OG comms:** Name the split's make-up the moment it is seen, ask the defenders whether they can hold it, and
  don't commit the defence until the last splitter is seen. [OG v chic]
- `S36` **Denning:** A 3-man group of the 8 monk and two damage on the backside is a correct answer to an enemy ranger
  and hammer pushing there. [Men v HC C]
- `S37` **Claude:** An 8v8 build should defend splits with monks, not damage, so its damage stays together. Freeing a
  damage dealer from defence can also give the team a runner. Double Paragon WoC teams defend with the prot and 8 monk,
  adding the WoC monk only while the split is dangerous. [OG v chic] [Men v Team] [RACK v hdm M]
- `S38` **Nick:** With a spirit light weapon ritualist in the build, a 3-player split (the ritualist kept at main to
  support the 7 monk) beats a 4-player one: a 3v3 is bad for a team defending with two monks. In [NwAy v Men] NwAy's
  4-player splits took nothing and its 3-player splits took two knights, three archers and the Bodyguard. **Claude
  (data, `comms_vars.py` split_size, 144 matches):** in general 3-player and 4-player splits into the enemy base took a
  pit NPC equally often (36% against 35%, 122 splits, unclear). [NwAy v Men] [cope v Book]
- `S39` **Nick:** On Isle of Weeping Stone a split depends on winning its matchups, not surviving collapses (the map is
  hard to collapse on); the team holding the gate locks can reinforce through them, and a split team that gives up
  gate control loses the centre of the map and its boosts. Gates aren't in the replay data. [NwAy v Men]

## 4. Main team and pit play
- `P1` **Nick / Denning:** A team relying on its split must keep its main team safe: give up ground, footmen and
  archers, play in its pit beside its NPCs, take no death penalty and give up no boosts. [Men v Team]
- `P2` **Claude:** The main team's job while its split works is to buy time: die as rarely as possible and never after
  time. Meeting the enemy in the field after each res loses a player each cycle. Playing in the pit buys time but
  doesn't win on its own: RACK held its pit to 8:17 where Team lasted 6:13 in the field, and both lost because their
  splits took too little. [Men v Team] [RACK v hdm M]
- `P3` **Bounty:** The main team has to take risks for anything to happen; trading flags for 20 minutes with no plan,
  and having the win condition on the wrong side of the map, loses slowly.
- `P4` **Bounty:** Pushing 6v8 or 7v8 at main while a player is away running or splitting is a bad idea; know the game
  state. With a numbers advantage, jump the enemy.
- `P5` **Claude:** Going back to the pit has to happen before the outer NPCs fall; once they are gone, the pit can't be
  held against a stronger main team. [OG v hdm]

- `P9` **Denning:** In non-split situations teams usually take the knights first. A full pit is harder to defend for
  the monks: 5+ extra targets to watch, and against area damage (a dervish, an elementalist) the knights ball up and
  eat it, so the healing needed rises sharply. **Claude (data):** with 4+ pit archers alive, some pit NPC is up to 29
  points more likely to die within 15 s. **Claude (data, `values.py`, 133 matches):** an archer lost costs the defending
  team 3.6 win points, a knight 9.2, the Bodyguard 8.4 (all clear; `W12`).
- `P10` **Denning:** Two monks on the push side is the norm against a full or mostly full pit; against an empty pit a
  team sometimes pushes with one. The pit deals a lot of damage, so two monks are often needed to live long enough for
  significant Lord damage. **Claude (data):** attackers with two healers in the pit dealt about 66 more Lord damage per
  10 s than with none or one.
- `P11` **Denning:** In the last seconds before the defenders' base res, attacking teams often leave the pit so they
  aren't caught in a bad position 8v8 when the team resses. **Claude (data):** Lord damage is highest 20 to 60 s
  before the defenders' res and low in the last 10 s.
- `P12` **OG comms:** Keep a healer with every group at all times (a prot and a monk on one side, the ritualist and a
  monk on the other). **Claude (data, `comms_vars.py`, 144 matches):** groups of 2+ with no healer lost a player in 25% of
  phases against 12% with one, at the same local numbers (+10 points, interval +7 to +13). [ohno v One]
- `P13` **OG comms:** Merge the whole team before pushing the enemy pit or base. **Claude (data, 144 matches):** groups of
  7+ in the enemy pit or base killed a player in 49% of phases against 18% for 3 to 6, and lost players slightly less
  often. [ohno v Crew]
- `P14` **OG comms:** Footmen (base NPCs, not pit NPCs) are worth protecting, and killing the enemy's when they split
  oddly. **Claude (data, 144 matches):** teams that lost a footman won 41% of the time against 65% for teams that lost
  none (descriptive: losing teams also get pushed). Win-model candidate `footmen_diff`; values.py prices a footman lost.
  [OG v Dz] [ohno v NwAy]
- `P15` **Bounty (Crew's rule):** If a team pushes your pit with only one monk, kill it. BcS's six-damage, one-monk
  push lost five players in 37 s (16:39 to 17:16); it is a last resort that only works by killing fast. [BcS v Crew]

### Base races
- `P6` **Bounty:** A team defending with only 2 players is saying "give us time to finish", so it should not chase
  players leaving on a split; it should finish. In a base race, defenders have to kill the attackers before the res.
- `P7` **Bounty:** Carrying the flag during a base race wastes time (clear only in hindsight).
- `P8` **Claude:** Don't race into an intact pit: the attackers die to knights, Bodyguard and Lord while the enemy walks
  into a pit that has fewer defenders. Late pushes pay off against a pit that has been worn down. [OG v cope U]

## 5. The flag game

### Flag position
- `F1` **Denning:** Being **up on flags** means being in the better flag position: better placed to get a boost and to
  run. It does not mean the team that capped last. A team single running that has just capped needs 2Y (Y = the run
  from the flag spawn to the stand) for its next flag: back to the spawn, then back to the stand. A team double running
  with a flag right beside the stand and another player waiting at the spawn can overcap at once and needs only 1Y
  for the next flag. It is up on flags, and the 1Y it saves is essentially a 1-player power play.
- `F2` **Denning:** Holding a flag near the stand while your team already holds it is a **backup flag**, and a big
  advantage: the enemy's capture is answered at once.
- `F3` **Denning:** A defender who can carry its flag partway while holding off a solo pusher (losing nothing: no
  death, no NPCs) shortens its team's Y, while the pusher accomplishes nothing.
- `F4` **Claude:** Flag position is measured on the next capture exchange: how long the team not holding the stand
  needs to capture, how long the holder then needs to answer (its response), and how long the first team then needs
  for its next flag (Y with a runner waiting at the spawn, 2Y without). Flag lead = the enemy's response minus your
  own. HC was up by about 20 s at 9:31 in [Men v HC C] even though Men was carrying, because Men's next flag was 2Y
  away and HC's Mes/A was already walking back. [Men v HC C]
- `F5` **Denning:** In the flag game, and when trying to get up on flags, the goal is to cap as soon as reasonably
  possible after the enemy. So when the enemy is running a flag, your team has to run too, or it falls behind on
  flags; a team that has to run can't retreat to its pit. [Men v HC C]
- `F6` **Denning:** A team up on flags doesn't have to cap at once. If its backside group is outnumbered, the runner
  can wait before capping and the team stays together; running with a 3v4 behind it is an unnecessary risk.
  [Men v HC C]
- `F7` **Denning:** Once the runner is capping on its own with no enemy damage near it, the backside group no longer
  needs to support it: fall back toward pit, and only follow if the enemy goes to kill the runner. [Men v HC C]

### Fighting with the flag
- `F8` **Denning:** Some games are fought 8v8 (holding the flag) or 7v7 (1 player running the flag).
- `F9` **Denning:** The flag game: 2 or 3 damage, the prot and the 7 monk push the enemy flag, the enemy does the same,
  and each team defends its own flagger with 1 or 2 damage and the 8 monk.
- `F10` **Denning:** Holding the flag: 8v8 builds often fight 8v8 as long as possible with the flag in hand, then cap
  right before the enemy would get a boost. This keeps the damage together and avoids the flag game.
- `F11` **Denning:** While your runner is out, the rest of the team plays defensively enough, and supports enough, for
  the runner to get back to base for the next flag. [Men v HC C]
- `F12` **Denning:** A team that must run a flag and can't kill on its push side should send an extra damage back to
  assist the run.
- `F13` **Claude:** A runner whose trip back to the spawn crosses the enemy's push team is slow every cycle, and the
  team falls behind on flags without the runner ever being cut off. Spreading runs over several players avoids it: Men
  used 3 runners and answered HC's captures in a median 28 s, while HC relied on its Mes/A for 13 of 20 carries and
  answered in a median 51 s. [Men v HC C]

- `F33` **Denning:** Look at where a drop happens. A real hand-off takes little time; a flag dropped in base and picked
  up much later is a team deciding not to run (and maybe deciding to run later), not a hand-off. Away from base, a
  hand-off that takes long is more likely a response to a push or a death than deliberate double running.
  **Claude (data):** of 229 drops picked up again where they fell, those on the backside and at the stand were picked
  up within a median 1.0 to 1.3 s; those in a team's own base waited a median 10 s.
- `F34` **Denning:** A team getting kills during the enemy's flag cycle and answering the capture later is much more
  likely a deliberate trade (finish the power play, then run) than forgetting the flag.
- `F35` **Denning:** 8v8 builds hold a flag near the fight, so they can answer a capture quickly with the whole team
  fighting. **Claude (data):** some fast answers also come from runners with speed skills (OG's elementalist carried
  at about 280 units per second against an average of 205); the flag model now uses each runner's measured speed.

### Running costs
- `F14` **Denning:** Running the flag costs pressure. A frontline runner puts out basically no damage with the flag in
  hand.
- `F15` **Denning:** A midline runner can't use its 40/40 set, so it casts fewer skills, has less energy and is more
  likely to be interrupted; it can't be in its shield set, so it takes more damage; it is in range of the enemy
  frontline and can't kite. Carrying slows the runner by 25%.
- `F16` **Denning:** Double running uses 2 players to run (half running: drop halfway to a teammate and run back for
  the next; full running: one waits back for the next flag). It gets a team up on flags faster but fights 2 players
  down.
- `F17` **Denning:** Half running is too risky: if enemies contest the handoff spot, they can return the flag.
- `F18` **Denning:** Not running the flag can be deliberate: a team on death penalty and under pressure may not be able
  to run without being wiped.
- `F19` **Denning:** Running on the 8 monk is a bad move, normally only when 2 enemy damage are dead or when desperate.

### Pushing the flagger
- `F20` **Denning:** When one enemy solo pushes the flagger, the flagging team should likely send help: a monk to heal,
  or a few damage to train the pusher out. Sometimes a flagger has to flag through one damage, and that's fine.
- `F21` **Denning:** One damage pushing is likely fine, depending on which damage is pushing and who is flagging.
  Whether "always collapse" is better has to come from the data.
- `F22` **Bounty:** A splitter carrying a flag has to be respected quickly. A backup flag belongs with the main team
  rather than overcapping when a splitter is threatening.

### The power play
- `F23` **Denning:** When the enemy is running the flag, the team with more players in the fight can play the power
  play.
- `F24` **Bounty:** When the enemy is running (an 8v7), damage dealers must commit and kill; a damage dealer far from
  the fight is a missed opportunity.

### Boosts
- `F25` **Denning:** The team that capped first is at a flag disadvantage: the other team can overcap and force it to
  run a flag first. [hdm v HC I1]
- `F26` **Denning:** Losing the stand just before a boost is normal for the holding team. It shows the capping team was
  down on flags: a team with an on-time flag, or up on flags, would have capped earlier. [hdm v HC I2]
- `F27` **Bounty:** Missing a boost by a few seconds matters. Don't drop the flag without a reason; dropping it to a
  better runner is fine.
- `F36` **Bounty:** If a capture will be overcapped at once, don't take it: the runner's time is a wasted cycle (BcS
  capped at 8:14 and was overcapped at 8:17). Capping can still pay off when it baits the enemy into a fight the team
  wins (BcS at 15:33, killing Crew's carrier). **Claude (data, `comms_vars.py` instant_overcap, 144 matches):** 16% of
  captures are overcapped within 10 s; those runs took longer (45 s against 37 s), and from the start of the run to 30 s
  after the capture the capturing team lost more players than it killed 22% of the time against 16% (+8.6 points,
  interval +3 to +16). Partly the situation: an instant overcap means the enemy was ready at the stand. [BcS v Crew]
- `F37` **Nick:** Shadow of Haste on a main-team runner when the enemy has none keeps a team permanently ahead on flags.
  In [NwAy v Men] Men's ritualist answered NwAy's captures in 4 to 31 s while NwAy needed 52 to 97 s. [NwAy v Men]
- `F28` **Nick:** Holding the flag to tie up an enemy prot only helps if the advantage is used somewhere else;
  otherwise it lets the enemy keep its damage together. [Men v Team]
- `F29` **Claude:** In a long even game, boosts are the scoreboard: they are often the only lasting edge, so
  near-misses (111 to 119 s holds) are real losses, and several near-misses for one team point to its flag timing.
  [OG v cope U] [hdm v HC I2]
- `F30` **Claude:** Winning the flag game outright (the enemy never capping) gives free boosts and lets the winner
  fight on the enemy's side of the map. [OG v hdm] [RACK v hdm M]
- `F31` **Claude:** A big split with the main team in its pit concedes the stand: nobody is left to run, so the enemy
  boosts every 2 minutes. A split plan has to win more than the boosts it gives away. [Men v Team] [RACK v hdm M]
- `F32` **Claude:** A good runner can swing the flag game on its own: moving a mobile player onto the flag turned a
  lost stand into 459 s of holding and 3 boosts. [OG v chic]

## 6. Kills, death penalty and timing
- `K1` **Denning:** "After time": dying shortly after the 2 minute base res, so the player waits almost the full 2
  minutes.
- `K2` **Denning:** "Timing" someone: holding off a kill until right after the res, so that player is down about 2
  minutes unless their team gets a res off.
- `K3` **Denning:** Players are resurrected at their base every 2 minutes while under 60% death penalty; death penalty
  lowers health and energy.
- `K4` **Denning:** Death penalty stacks. A team that piles up death penalty against a spike team is at a big
  disadvantage even if each death on its own can be recovered from: the lower health makes every later spike easier.
- `K14` **Denning:** Teams time kills: they may avoid killing a player just before the res, so the kill lands after
  time. The other way round, when a death is very likely or inevitable, the dying team tries to die before time (death
  sets, or not healing on purpose). A team losing and fighting in its base may have monks die before time on purpose,
  even when the death isn't inevitable, to reset their energy. Monks die on purpose only for a base res (every 2
  minutes, on the minute), never for a Pact or a res signet: a monk dying in its own base at 17:55 is likely deliberate. So a death can be positive rather than negative,
  depending on the situation; look in the data for where dying before time raises the win rate.
  **Denning:** Such a death can be deliberate, but whether it is depends on the monk's energy, which the engine doesn't
  track (the replays don't record it), so the data can't tell a deliberate death from a mistake. (Measured, 133 matches:
  healer deaths in their own base or pit within 15 s of the base res cost -7.2 win points, clear, 54 cases; read as
  "possibly deliberate", not as a mistake.)
- `K17` **OG comms:** Fight the player carrying a big death penalty. **Claude (data, 144 matches):** players in a fight
  with 15%+ death penalty died within 10 s 4.9% of the time against 1.3% with none, at the same local numbers (partly
  because the same players keep being reachable). [ohno v One]
- `K18` **Denning:** A death while boosted means nothing different from a death not boosted; if anything it should cost
  less, since the boost offsets the death penalty. Boosting is a proxy for a late, winning position: boosts take a
  while to come, so those deaths come later, and a team already winning has more win chance to lose. Fights while
  boosted get no variable of their own. **Claude (data, 133 matches):** boosted deaths came at a median 13.1 min with
  the team at 64% to win, against 7.8 min and 13% for the rest, which explains the gap (about 20 win points against 3).
  Compared at the same minute and win chance there is no consistent difference (some cells favour boosted deaths, some
  the others, each with few cases). The split is gone from `values.py`. OG's "we are boosting, so we can die for NPCs"
  stays untested as a trade. [ohno v One]
- `K5` **Bounty:** A team that always has someone timed or stuck has no moment to play tactics and gets overwhelmed.
  Resurrecting too late wastes time; teams under pressure are often scared to go for the res.
- `K6` **Bounty:** Target choice costs time: 30 to 40 s failing to kill a monk is fine at 2 minutes, not at 22. A build
  that needs time must use every 2 minutes. **Claude (data, `comms_vars.py` monk_focus, 144 matches):** in general
  the opposite holds: groups putting most of their player damage on the enemy healers killed in 19% of phases against
  13% for groups hitting other players, at the same local numbers and phase length (+2 points, interval +1 to +4).
  Partly selection (groups that can reach the healers are usually winning the fight); the late-match cost of a
  failed monk kill isn't tested. [Team v push]

- `K7` **Bounty:** The first 30 seconds shape the match. A team that double runs out front still has to survive the
  opening fight.
- `K8` **Claude:** Kills are only worth what they are converted into: the strongest teams turn each kill straight into
  pit pressure (a kill, then knights; the next kills, then archers; a kill in the pit, then the Bodyguard). A backline
  wipe is the biggest conversion chance: the winner gets one res cycle with the enemy's healing gone. [OG v chic]
  [hdm v HC I1] [Men v HC C]
- `K9` **Claude:** The team ahead on death penalty can stop chasing and make the other team come to it; the team behind
  has to push into fights it can't win. [OG v cope J]
- `K10` **Claude:** Against a hex team, kill the hex casters first; it only works if the spikes land. [OG v cope J]
  [OG v hdm]
- `K12` **Claude, confirmed by Denning:** A team that can't kill is stopped by the enemy's defence (prots, blocks), by
  shutdown of its spikers (interrupts, knockdowns, Blind, enchantment removal) or by spread damage. **Denning:** hitting
  the wrong player matters, but not hugely.
- `K13` **Claude, confirmed by Denning:** Blind and enchantment removal stop a kill when the team doesn't defend its
  offence: no defensive interrupts on the casters, no condition removal on its damage dealers, a clumped frontline in
  AoE range. **Claude:** those are missing because the Mes/A is running or defending, the mesmer interrupts offensively,
  the mesmer is itself shut down, the monks are overloaded, the bars lack removal, or the enemy reapplies faster than
  removal recharges (to test).
- `K11` **Claude:** Most deaths come in chains: about 7 in 10 deaths in 24 matches came within 20 s of a teammate's.
  The first death of a chain, and what put that player there, is what to judge; the rest are mostly its consequence,
  especially once a monk is down.

## 7. Late game and 28:00
- `L1` **Denning:** Builds differ in how easily they get Lord damage late. A balanced build (2 frontline, a ranger, 2
  mesmers) gets Lord damage far more easily than a 2-monk hex way: hexes cause degeneration, which isn't Lord damage,
  and with 2 monks a hex way usually can't both defend its own Lord and survive pushing the enemy pit. So a balanced
  team that survives 26 minutes without dying or losing NPCs is in a winning position against it, even without scoring
  any kills or NPCs.
- `L2` **Denning:** Players can't see Lord damage in game: a team knows roughly whether it is ahead at 28:00, not by
  how much. Sending some players for more Lord damage while defending can be the safer choice, since the enemy may
  out-damage the lead in the time left. A main team that dies quickly also does less Lord damage. [hdm v HC I2]
- `L3` **Claude:** Judge late decisions on what the players could know (flag, boosts, deaths, NPCs, the clock, each
  build's late push), not on the exact tiebreak score the replay shows.
- `L4` **Claude:** In long even games, know the tiebreak from about 24:00 (it decides whether to risk anything). The
  team behind must commit to Lord damage (or a Lord kill) in the last minutes; the team ahead only has to keep its
  Lord alive, so it defends with enough players and does not counter-race. [hdm v Men N] [hdm v HC I2]
- `L5` **Bounty:** When far behind, keep playing to about 26:00 to gain every edge, then try to finish the Lord.
- `L6` **Bounty:** Being too hasty loses games: take time, defend more with damage, work through the game.
- `L7` **Denning:** Protting your own NPCs instead of your Lord is deliberate: enchantments on your own Lord cost
  aggressiveness.
- `L8` **Claude:** The late push decides even games, and it is only good if the enemy pit has been worn down; a split
  that took no knights over 15 minutes leaves no late win condition. [OG v cope U]
- `L10` **Claude:** Measured Lord damage per second while at the enemy Lord (24 matches): ranger 37, elementalist 33,
  warrior 27, paragon 24, dervish 23, necromancer 10, ritualist 10, mesmer 7, monk 5. Midline casters and rangers hit
  the Lord as hard as the frontline or harder; the ranger figure leans on solo splits into empty pits.
- `L11` **OG comms:** A team that turtles (sits in its base and pit) gives up Lord damage, so the other side must
  make a play to break it, and doesn't need to chase it out late. **Claude (data, 144 matches):** 25 turtles (75%+ of
  live players at home for a minute, not just resurrected); the turtling team won 7 (28%). The win model tests `turtle_diff`
  as a candidate from batch 6. [ohno v One]
- `L12` **OG comms:** In a base race, heal your own Lord ("heal the Lord, heal the Lord"). **Claude (data):** OG won the
  race against hold by seconds (hold's Lord died at 5:17, OG's at 5:20) after healing its own Lord for 1,390; hold's got
  no healing. [OG v hold]
- `L9` **OG comms:** Watch the clock out loud ("this is 22 minutes"); the late plan (play for 28:00 or push now) has to
  be agreed, not argued during the push. [OG v cope U]

## 8. Spikes: offence and defence (micro)
- `X1` **Denning:** Against a spike build, call out a lack of interrupts on the spike skills, and call out when a team
  spikes really well: 600 damage landing within 0.2 s can't be saved by any prot or Infuse.
- `X2` **Denning:** Anchors: 400 damage in 0.6 s should be survivable if the target was in shield set and the damage was
  armor respecting; 550 armor ignoring damage in 0.35 s is impossible to save.
- `X3` **Denning:** For a spike, name the primary failure: lack of prots, late Infuse, or lack of interrupts on spike
  skills. Pre-protting is correct play. Whether a prot was unavailable because of energy or recharge doesn't matter;
  both point to other issues.
- `X4` **Denning:** A strong prot (e.g. Ali) is the benchmark for spike catches: reaction time and pre-protting. A
  similar benchmark is needed for Infuse Health on a good 7 monk.
- `X5` **Claude:** Catching spikes is the clearest measure of monk quality. Good backlines prot most spikes 0.3 to 1.0 s
  after the first hit, with some pre-prots; weak ones land prots 1 to 2 s after, when the target is already dead.
  hdm caught 17 of 20 spikes; cope caught 12 of 34; RACK caught 4 of 19 against hdm's Double Paragon WoC.
  [OG v cope J] [OG v hdm] [RACK v hdm M]
- `X6` **Claude:** Fast invoke spikes (240 to 390 damage in 0.35 s on a target already below full health) can only be
  saved by pre-protting. [OG v cope J]
- `X7` **Claude:** Not every death is a spike: deaths that take 2 to 8 s from the first big hit come from pressure,
  knockdown lock or degeneration, and the failure is support or positioning, not prot timing. [Men v Team] [OG v hdm]
- `X8` **OG comms:** Spike timing micro: land Shell Shock between "two" and "one" of the countdown; call for removal of
  Migraine on the spikers. **Claude (data, 144 matches, 1,347 spikes):** Cracked Armor on the target at the first
  hit went with fewer kills, not more (30% against 36%, interval -13 to -4 points): the Shell Shock timing isn't
  supported; why it reads backwards (e.g. teams landing it on monks with prots up) is still to check. [OG v cope J]
- `X9` **OG comms:** A spiker carrying a hex (Migraine uncovered) can't land its part; call for removal. **Claude (data,
  1,347 spikes in 144 matches):** spikes with a hexed spiker killed 28% of the time against 37% without (interval 4 to 16
  points). An enchantment strip as the spike lands showed no clear effect (interval crosses zero); for Shell Shock see
  `X8`. [OG v cope J] [ohno v Crew]
- `X10` **OG comms:** Interrupts on the spikers just before the spike stop the kill ("they keep Complicating my Deep
  Wound"). **Claude (data, 1,347 spikes):** when the spiking team was interrupted in the 5 s before the first hit, spikes
  killed 24% of the time against 38% (interval 8 to 20 points). Against hdm, OG's 15 spikes killed none: about one
  interrupt per spike and 466 healing on the target in 3 s, against 0.4 and 328 for cope, which lost 10 of 24 to the same
  spike. Weapon sets showed no clear effect yet (spikers on 40/40 sets or targets on shields: intervals cross zero).
  [OG v hdm] [OG v cope J]

## 9. Monk play under pressure (micro)
- `M1` **Denning:** Judge a death first by its cause: a great enemy play, or a failure. In an even 8v8 with the monks in
  position, the 8 trying to Guardian the prot, the 7 knocked down, the prot knocked down, the 8 Dazed and a prot
  stripped by Shatter Enchantment, none of it alone kills at a high level: the enemy's coordination of knockdowns,
  Daze, interrupts and enchantment removal is the cause. Small mistakes around it can still be acceptable even at the
  highest level. [hdm v HC I1]
- `M2` **Denning:** Mistakes have a severity: basic (a mistake good players shouldn't make), minor (high level and not
  always avoidable, e.g. getting Dazed casting beside a ranger) and acceptable (fine even at the highest level). A
  minor mistake can be game ending in the wrong moment, e.g. a monk alone with no other monk, or after time.
  [Men v HC C]
- `M3` **Denning:** Interrupts on quarter-second casts (Reversal of Fortune, Aegis) are mostly luck: a mesmer or ranger
  can't hit them reliably and a monk can't cancel them, so they are not a monk error.
- `M4` **Denning:** A monk casting right beside a ranger without cancel-casting first, and getting Dazed by Concussion
  Shot, is a minor mistake.
- `M5` **Denning:** A mesmer near a monk under attack should always interrupt defensively (e.g. hammer attack skills,
  Burning Arrow), and someone should peel the attacker so the monk can kite. [Men v HC C]
- `M6` **Denning:** The prot should keep Aura of Stability on a monk being knocked down (e.g. the 7 monk against a
  hammer).
- `M7` **Denning:** Pre-kiting with a speed stance is the correct play for a prot, even when a Coward catches it.
- `M8` **Denning:** The team's mesmers should interrupt defensively so that Shatter Enchantment, Energy Surge and Energy
  Burn don't go off on their backline.
- `M9` **Denning:** Against energy denial, cast from the shield set (hiding energy); enchantments from the staff (20%
  longer); swap to the single high energy set when low.
- `M10` **Denning:** Space the ranger: the further away, the longer arrow interrupts take; a very quick monk can dodge
  some arrows by moving.
- `M11` **Denning:** Against 2 damage, getting dazed is critical: Guardian yourself and/or fake a cast to bait the daze
  skill, then cast safely while the ranger is low on energy. Keep the ranger targeted.
- `M12` **Denning:** Spacing: stand as far as possible from the enemy mesmer (and ranger) while staying in cast range of
  the 2 players being healed, and in the correct position (e.g. in front of their own mesmer). The monk only needs to
  be in range of allies while they take damage. There is no "holding a spot for the flag".
- `M13` **Denning:** Peel: hitting the enemy Mes/A is both offensive and defensive, so it is correct; hitting enemy
  monks while your team is dying and needs support is purely offensive and likely incorrect. With the timing of a fast
  monk kill, the frontline may not be able to peel effectively, and that is not their mistake. [hdm v HC I1]
- `M14` **Denning:** A monk under 2 damage needs team support: e.g. the dervish hits the ranger and the mesmer
  defensively interrupts the enemy mesmer. When the Mes/A is not carrying the flag, it should interrupt the enemy
  mesmer defensively when that mesmer pressures its monk.
- `M16` **Denning:** Overload is the goal when trying to kill; usually through coordinated pressure.
- `M17` **Claude:** A team that heals a lot but still loses a player usually had heals arrive where prots were needed, a
  low health ceiling (DP, Deep Wound), healing going to players not under threat, heals late or interrupted, or a
  victim that couldn't kite (knockdown lock, cripple, Daze) (to test).
- `M18` **Denning:** An 8 monk using Draw Conditions to take Burning and Deep Wound onto itself is normal play, but it
  might be a mistake when it is the only healer facing a ranger and a hammer (its health ceiling drops by a fifth). The
  data will tell. [Men v HC C]
- `M19` **Denning:** A monk alone is vulnerable because it has no other monk to support it (OG comms: "solo monk, go on
  the monk"). **Claude (data, 144 matches):** a healer in a fight with no other own healer within casting range died within
  10 s 3.3% of the time against 1.1% with one, at the same local numbers (interval 2.8 to 4.8 points). Deaths-node
  variable `solo_healer`, win-model candidate `solo_healers_diff`. [ohno v One] [OG v Dz]

## 10. Interrupts and shutdown (micro)
- `I1` **Denning:** An interrupt can be critical, e.g. an interrupt on Healing Burst that leads to a wipe.
- `I2` **Bounty:** Spiking from max range gets the spikers interrupted easily (Complicate, Cry).
- `I3` **Claude:** Wipes are often chained by interrupts on monk defence: Power Spike or Psychic Instability on Guardian
  or Aegis, a Hammer Bash or Complicate on Healing Burst, Concussion Shot on Reversal of Fortune. [OG v chic]
  [OG v cope U] [hdm v HC I1] [Men v HC C]
- `I4` **Claude:** Mesmer shutdown on the spikers and the caller is what turns a spike matchup: 40 interrupts on OG's
  invoke team (vs 16 by the team that lost) went with 1 kill from 18 spikes. [OG v hdm]
- `I5` **Claude:** In mirrors, the side with the stronger mesmers holds the edge in the long game (70 interrupts to 27).
  [OG v cope U]

## 11. Positioning and overextension (micro)
- `O1` **Claude:** A single overextended player can turn an even game: a dervish holding two knights in the enemy base
  took a knockdown and died, and 3 more players followed within 36 s. When a player is pulling NPCs deep, the team has
  to be ready to cover or call them out. [OG v cope U]
- `O2` **Claude:** Monks split across the pit (one at each end) can't cover each other in the final defence.
  [OG v cope U]
- `O4` **Nick:** Against a mobile WoC spike that Returns onto its own outside archers, kill those archers first: they
  make every split or push into its base dangerous. [xxx v Men]
- `O3` **Claude:** Players who drift away from their monks are the easiest kills; a mobile killer (e.g. a Mo/A WoC
  with speed) punishes this best. [OG v chic]

## 12. Weapon sets
- Energy hiding (Guild Wars Wiki: Energy hiding, Weapon swap): swapping to a low energy set lowers the available
  energy pool so energy denial takes less; a shield set gives -5 energy, and with a +10 to +17 energy primary set up to
  22 energy can be hidden.
- A 40/40 set is a wand and offhand that each have a 20% chance to halve casting time and a 20% chance to halve
  recharge of spells (about a 36% chance of at least one). A midline carrying the flag can't use it.

## 13. Language
- **Denning:** Each team's end of the map is its **base** (not "home"); the res shrine is at the base.
- **Denning:** **Backside** is the side of the map closest to your own base; **push side** is closest to the enemy
  base. Describe positions this way, not north and south.
- **Denning:** The NPCs in the enemy base are the **pit NPCs** (not "guards"); the area around the Lord is the
  **pit**; archers outside it are **outside archers**.
- **Denning:** The monks together are the **backline**. Elementalists, rangers, paragons and mesmers are **midline**.
  Dervishes, warriors and assassins are **frontline**. It depends on the build: a caster assassin is midline, a dagger
  assassin is frontline.
- **Denning:** Refer to players by role: prot monk (slot 6), 7 monk (usually the push monk), 8 monk (usually
  backside), stand mesmer (the main shutdown mesmer), running mesmer or Mes/A (usually with a running skill), hammer
  warrior, and so on.
- **Denning:** **Y** is the run from the flag spawn to the stand; a **backup flag** is a flag held near the stand
  while your team already holds it.
- **Bounty:** A **cycle** is a 2-minute window in which a team can push, do damage and deal with the split; wasting
  one (a needless cap, chasing, a collapse that kills nothing) is how a slow build loses. **Inaccuracies** are small
  errors that add up to a blunder (his chess comparison), e.g. a monk not watching a split, a ritualist caught off
  shield set by Coward, a sleepy 8 monk.
- Auto-transcripts garble terms: "X-way" and "axes" mean hex way and hexes; "Ellie" or "LE" means elementalist.

## 14. Situations: what is the best play here?
Each card is a recurring decision: the options and the variables that may decide between them. The analysis engine
records every one of these moments in every match (the full scoreboard at that second, what each player then did, and
what followed), so the best play is meant to come from the data, not from anyone's opinion, including the defaults
below. A default is listed only where a principle already exists (from Denning or commentary); it is the hypothesis the
data tests first, and it is replaced when the data says otherwise. Where a card has a **Data** line, it comes from
`usual.py` (133 matches, the latest learning report): each choice against the usual one in win chance, adjusted for the
situation, with a range from resampling whole matches. Cards without one aren't measured yet.

- `D1` **The enemy picks up a flag.** Options: run now, hold the flag near the stand (if you hold it), don't run.
  Deciding factors: flag position, who holds the stand and the boost clock, numbers at main, whether your runner can
  get back. Default: run so you cap as soon as reasonably possible after the enemy (`F5`); if you are up on flags,
  you need not cap at once, and the group stays together rather than fight outnumbered (`F6`, `F7`). Don't run when a
  run would get you wiped on death penalty (`F18`). Confidence: high.
- `D2` **An enemy split enters your base.** Options: answer with a damage dealer, the prot, the 8 monk, or a collapse;
  ignore it. Deciding factors: the split's size and damage, your pit NPCs, your build (8v8 or not), whether the main
  fight is being won. Default: answer within 15 s (`S18`): a lone ranger with the Mes/A plus a frontline collapse
  (`S19`), a 3rd enemy damage with the prot (`S23`); an 8v8 build shadows it with a snare and collapses when it
  commits (`S41`); a team winning main can ignore a solo split (`S28`). Confidence: high on timing, medium on who.
- `D3` **You have more players in the fight (power play).** Options: push, or hold. Deciding factors: why the enemy
  is short (running, split, dead), how long it lasts, flag position, who is ahead. Default: commit and kill
  (`F23`, `F24`); a team already winning needn't force it (`W8`). Confidence: medium. **Data (133 matches,
  1,160 power plays):** no choice is clearly better than pushing and advancing (the usual): holding and fighting -0.3,
  holding and falling back -0.8 (neither clear).
- `D4` **The enemy's boost is coming.** Options: run now, or give up the boost. Deciding factors: your flag ETA against
  the boost clock, numbers, death penalty. Default: run in time to cap before the boost unless it costs a wipe
  (`F18`, `F26`, `F29`). Confidence: medium. **Denning:** falling back there is likely a mistake: a team that isn't
  going to run may gain by staying and fighting, possibly on a power play; but a team losing the fight and not running
  has no reason to hold ground and may as well fall back for safety. It depends on the situation. **Data (133 matches, 504
  decisions):** not running and falling back -2.1 against not running and fighting (not clear); by fight state, falling
  back costs most when the team is ahead in the fight (-4.5) and little when behind (-1.9): still Denning's pattern,
  but weaker than the 40-match reading (-14). Running and advancing +3.0 (clear, but partly who chooses it). Energy
  isn't recorded.
  **Denning:** what decides staying to fight against falling back: own monks' energy, enemy health (live in the score
  share), the enemy's estimated energy, and any numbers advantage. (Replays have health and numbers; energy is not
  recorded and would have to be estimated from casts.)
- `D5` **You just won a wipe.** Options: push the pit, take the flag and the stand, or reset. Deciding factors: enemy
  pit NPCs, the res timer, the clock, whether you are already winning. Default: convert straight into pit NPCs before
  the res (`K8`); a team already winning backs out rather than risk a close Lord window (`W8`, `W9`). Confidence:
  medium. **Denning:** what a wipe can be turned into depends on where it happened: from a wipe at the stand a team is
  unlikely to reach the enemy base and take NPCs in the 30 s before the res. **Data (133 matches,
  292 wipes):** taking the flag after a wipe cost 4.5 points against pushing the pit (clear; the 30-match reading of
  +12 came mostly from wipes too far from the enemy pit to reach it before the res).
  **Denning:** for a 2-monk spike build the weighing is often the reverse: after a wipe, DP on the enemy is worth more
  than NPCs (`B23`).
  **Denning:** a team very rarely rushes into the enemy base to spike players as they resurrect; it doesn't make sense in
  the context of games.
- `D6` **You are stacking death penalty against a spike build.** Options: keep fighting at main, play in the pit, take
  boosts to clear it. Variables: how many players are now within one enemy spike, boosts available, flag position.
  Default: none yet (`K4` says it is a big disadvantage; what to do about it is for the data).
- `D7` **24:00 and later.** Options: commit to Lord damage, defend, or both. Deciding factors: who is ahead on what the
  players can know, each build's late push and how many monks can defend while others push, pit NPCs left. Default:
  the team behind commits; the team ahead defends and doesn't counter-race (`L4`); a balanced build that has kept its
  pit and its players is already winning against a 2-monk hex way (`L1`). Confidence: medium.
- `D8` **Your backside group is outnumbered while you are up on flags.** Options: fight, fall back toward pit, escort
  the runner. Default: fall back toward pit; the runner can wait before capping; follow only if the enemy goes for the
  runner (`F6`, `F7`). Confidence: high.

## 15. Open questions
- `Q1` When may a pit-defending main team step out (e.g. to stop a flag cap or get a res)? [Men v Team]
- `Q5` When does a solo split pay off (what it killed or drew away against what it cost the main fights)?
- `Q6` When should the power play be pushed hard, and when is it safer to hold?
- `Q7` How many players to send back to a pushed flagger, and when?
- `Q10` What is the benchmark for a good 7 monk's Infuse Health timing?
- `Q15` What should a team do when it is stacking death penalty against a spike build (`D6`)?
