# Rulings register

This register is the model's constitution: every definition and decision Denning has given, one line each, grouped by topic. A ruling is Denning's and overrides Claude's reasoning and any reading of the data until Denning changes it; where the data disagrees with a ruling, both are shown and Denning rules. New rulings are appended with the next free number in their group and are never renumbered; a superseded ruling is marked, not deleted. Sources in brackets: tactics line ids, docs/CHANGELOG.md session tags (e.g. [CHANGELOG 4t]), METHODS.md section names, data files.

## Which matches count

- R-001. Only replays of matches played on or after 1 September 2026 count in the model: training, and every benchmark built from replays. New picks come from matches played on or after 2 September. [METHODS "Which matches count"]
- R-002. Team strength and lineup ratings use every stored result, whatever its date, since they only rate who is good. [METHODS "Which matches count"]
- R-003. Game facts measured from replays keep every replay regardless of date: each map's flag spawns and stand, and Lord regeneration. [METHODS "Which matches count"]
- R-004. The large pull is trained in chunks of 40 to 50 matches, each with a learning report and the TQs. (Supersedes the earlier batches of 6.) [CHANGELOG 4t]
- R-005. Commentary matches (Maga's OG comms, Bounty's, Nick's) go into training, flagged as chosen; the new variables the commentary points to are the most important thing it gives. [HANDOFF "Next: the commentary transcripts"]
- R-006. Transcripts are never stored in the repo (it is public); only paraphrased claims with their check against the data. [METHODS "Commentary and comms"]
- R-007. The two OG comms matches whose claims were never filed (OG v chic, OG v cope on Uncharted Isle) are dropped. [CHANGELOG 4t]
- R-008. Open questions Q2, Q3, Q4, Q8, Q9, Q11, Q12 and Q13 on the tactics page are dropped; K19 is removed (Bounty spoke metaphorically about "one unit"). [CHANGELOG 4t]

## Flags and runners

- R-020. Up on flags means being in the better flag position: better placed to get a boost and to run on the next capture exchange. It does not mean the team that capped last. [tactics F1]
- R-021. A team single running that has just capped needs 2Y for its next flag (back to the spawn, then to the stand); a team with a flag beside the stand and a runner waiting at the spawn needs 1Y, and the Y it saves is essentially a one-player power play. [tactics F1]
- R-022. Holding a flag near the stand while your team already holds it is a backup flag, and a big advantage: the enemy's capture is answered at once. [tactics F2]
- R-023. A defender who can carry its flag partway while holding off a solo pusher, losing nothing, shortens its team's Y while the pusher accomplishes nothing. [tactics F3, S27]
- R-024. Cap as soon as reasonably possible after the enemy. When the enemy runs a flag your team has to run too or it falls behind; a team that has to run cannot retreat to its pit. [tactics F5]
- R-025. A team up on flags does not have to cap at once: if its backside group is outnumbered, the runner waits and the team stays together; running with a 3v4 behind it is an unnecessary risk. [tactics F6]
- R-026. Once the runner is capping alone with no enemy damage near it, the backside group falls back toward pit and follows only if the enemy goes for the runner. [tactics F7, D8]
- R-027. While your runner is out, the rest of the team plays defensively enough, and supports enough, for the runner to get back to base for the next flag. [tactics F11]
- R-028. A team that must run and cannot kill on its push side sends an extra damage back to assist the run. [tactics F12]
- R-029. Running costs pressure: a frontline runner puts out basically no damage; a midline runner loses its 40/40 set and shield set, casts less, is interrupted more, takes more damage and cannot kite; carrying slows the runner by 25%. [tactics F14, F15]
- R-030. Double running uses two players (half running: drop halfway to a teammate; full running: one waits back for the next flag). It gets a team up on flags faster but fights two players down. Half running is too risky: enemies contesting the hand-off spot can return the flag. [tactics F16, F17]
- R-031. Not running the flag can be deliberate: a team on death penalty and under pressure may not be able to run without being wiped. [tactics F18]
- R-032. Running on the 8 monk is a bad move, normally only when two enemy damage are dead or when desperate. [tactics F19]
- R-033. An 8 monk sometimes holds the flag without trying to capture. A hold is a carry of 10 s or more that never closes a quarter of the way to the stand; holds are kept out of the run models, the runner choice and the runners' capture rates. [tactics F19, METHODS "After batch 10"]
- R-034. When one enemy solo pushes the flagger, the flagging team should likely send help (a monk to heal, or a few damage to train the pusher out); sometimes a flagger has to flag through one damage. One damage pushing is likely fine, depending on the pusher and the runner; whether always collapsing is better comes from the data. [tactics F20, F21]
- R-035. When the enemy is running the flag, the team with more players in the fight plays the power play. [tactics F23]
- R-036. The team that capped first is at a flag disadvantage: the other team can overcap and force it to run first. [tactics F25]
- R-037. Losing the stand just before a boost is normal for the holding team; it shows the capping team was down on flags. [tactics F26]
- R-038. Where a drop happens matters: a real hand-off takes little time; a flag dropped in base and picked up much later is a team deciding not to run; away from base a long hand-off is more likely a response to a push or a death than deliberate double running. [tactics F33]
- R-039. A team getting kills during the enemy's flag cycle and answering the capture later is much more likely a deliberate trade than forgetting the flag. [tactics F34]
- R-040. 8v8 builds hold a flag near the fight so they can answer a capture quickly with the whole team; they fight 8v8 with the flag in hand as long as possible and cap right before the enemy would boost. [tactics F35, F10]
- R-041. The flag game: two or three damage, the prot and the 7 monk push the enemy flag, the enemy does the same, and each team defends its own flagger with one or two damage and the 8 monk. Some games are fought 8v8 (holding) or 7v7 (one player running). [tactics F9, F8]
- R-042. Who carries (a warrior, a midline, a dervish, a monk) is a strategic decision; runner choice is a decision kind the usual play compares. [CHANGELOG 4t]
- R-043. The runner's speed skills set the minimum time required to capture; every flag ETA, response and lead uses each runner's measured carry speed. [CHANGELOG 4t]
- R-044. A carrier behind on players alive has its ETA discounted by the measured capture chance at that numbers difference. [CHANGELOG 4p]
- R-045. Flag position is judged with the scoreboard's flag lead (the next exchange), never from who holds the stand. [HANDOFF "Known issues"]
- R-046. Boosting is a proxy for a late, winning position. A death while boosted means nothing different from one not boosted (if anything it costs less, since the boost offsets the death penalty); fights while boosted get no variable of their own, and the boosted-death split was removed. [tactics K18]
- R-047. The cost of an instant overcap (a capture overcapped within 10 s) is measured apart from captures held longer. [CHANGELOG 4t]
- R-048. Crippled runners capturing more is selection (runs that get far get Crippled), not Cripple helping; leave for now. [CHANGELOG 4r]

## Fights, power plays and kills

- R-060. Individual deaths do not win games. What matters is the game state that caused a death (flags, positioning, micro mistakes) and what the death caused. The flag game, death penalty and pit NPCs are all very important in close games. [tactics W6]
- R-061. A power play is any numbers advantage at main, e.g. an 8v7 while the enemy runs, not only three or more up. A numbers advantage held in a team's own base or pit is a defence, not a power play. [CHANGELOG 4p, METHODS "Commentary and comms"]
- R-062. A power play has a limited window (until the enemy runner is back) and the team must capitalize on it; the 7 may be unable to kill because it is behind on flags and has to run, so its power play is shorter than its numbers suggest. [tactics J5, J6]
- R-063. Fights are global: everything in a match affects everything else. A 4v3 can be intentional so the other side can fight 5v3; the weak side then plays safe (no deaths, keep the enemy busy, do not chase). Judge each group by its job, not by its local fight. [tactics J1, J2]
- R-064. Healers only matter through damage: three healers and one damage against two and two is about even. What decides a fight is the damage a group can actually put out against the healing and prots it faces, measured, not counted by heads. [tactics J12]
- R-065. Damage is lost to interrupts, knockdowns, Blind, Weakness, carrying the flag, kiting and peeling. [tactics J9]
- R-066. A good team waits for its players to come back from the res before fighting. [tactics J8]
- R-067. A team already winning (pit taken, ahead on death penalty, boosting, ahead at 28:00) has no need to risk a Lord kill in a close window; back out, wait for the res, fight again with the advantages. [tactics W8]
- R-068. "After time" is dying shortly after the 2-minute base res, so the player waits almost the full two minutes; "timing" someone is holding off a kill until right after the res. Players resurrect at their base every two minutes while under 60% death penalty; death penalty lowers health and energy. [tactics K1, K2, K3]
- R-069. Death penalty stacks. A team that piles up death penalty against a spike team is at a big disadvantage even if each death can be recovered from. [tactics K4]
- R-070. Teams time kills and deaths: a dying team tries to die before time; a monk dies on purpose only for a base res (every two minutes on the minute), so a monk dying in its own base at 17:55 is likely deliberate. Whether a death was deliberate turns on energy, which the replays do not record, so the data cannot tell it from a mistake: read such deaths as possibly deliberate, never as a mistake. [tactics K14]
- R-071. Overload through coordinated pressure is how kills happen; hitting the wrong player matters, but not hugely. [tactics M16, section 8]
- R-072. Judge a death first by its cause: a great enemy play, or a failure. Then grade the smaller mistakes basic (good players should not make it), minor (high level, not always avoidable) or acceptable (fine at the highest level); a minor mistake can be game ending when a monk is alone or after time. [tactics M1, M2]
- R-073. Interrupts on quarter-second casts (Reversal of Fortune, Aegis) are mostly luck, not a monk error. [tactics M3]
- R-074. A monk casting beside a ranger without cancel-casting first and getting Dazed is a minor mistake. [tactics M4]
- R-075. Defensive play for a Mesmer is interrupting offensive skills and casting on the enemy midline and frontline; offensive play is interrupting the enemy monks. A mesmer near a monk under attack should always interrupt defensively, and the team's mesmers interrupt defensively so Shatter Enchantment, Energy Surge and Energy Burn do not go off on the backline. [tactics M5, M8, M14; CHANGELOG 4p]
- R-076. Frontline defensive peel is hitting or snaring enemies on its own backline. Hitting the enemy Mes/A is both offensive and defensive, so it is correct; hitting enemy monks while your team is dying and needs support is purely offensive and likely incorrect. With a fast monk kill the frontline may not be able to peel, and that is not their mistake. [tactics M13; CHANGELOG 4p]
- R-077. The prot keeps Aura of Stability on a monk being knocked down. Aura of Stability only prevents knockdowns on another ally, never the caster; one Aura of Stability into two hammer warriors is worth a call out. [tactics M6, B2]
- R-078. Pre-kiting with a speed stance is the correct play for a prot, even when a Coward catches it. [tactics M7]
- R-079. Against energy denial: cast from the shield set, enchantments from the staff, swap to the high-energy set when low. [tactics M9]
- R-080. Spacing: stand as far as possible from the enemy mesmer and ranger while in cast range of the two players being healed, in the correct position relative to your own mesmer; the further the ranger, the longer arrow interrupts take. There is no "holding a spot for the flag". [tactics M10, M12]
- R-081. Against two damage, getting Dazed is critical: Guardian yourself and/or fake a cast to bait the Daze skill, then cast while the ranger is low on energy. A monk under two damage needs team support. [tactics M11, M14]
- R-082. An 8 monk using Draw Conditions on itself is normal play, but may be a mistake when it is the only healer facing a ranger and a hammer; the data will tell. [tactics M18]
- R-083. A monk alone, with no other own healer within casting range, is vulnerable ("solo monk"). [tactics M19]
- R-084. Spike anchors: 400 armour-respecting damage in 0.6 s on a shield set should be survivable; 550 armour-ignoring damage in 0.35 s, or more than the target's health in 0.35 s, cannot be saved; 600 within 0.2 s cannot be saved by any prot or Infuse. [tactics X1, X2]
- R-085. For a spike, name the primary failure: lack of prots, late Infuse, or lack of interrupts on the spike skills. Pre-protting is correct play. Whether a prot was unavailable because of energy or recharge does not matter. [tactics X3]
- R-086. A strong prot (e.g. Ali) is the benchmark for spike catches; a similar benchmark is needed for Infuse Health on a good 7 monk. [tactics X4]
- R-087. An interrupt can be critical, e.g. one on Healing Burst that leads to a wipe. [tactics I1]
- R-088. Blind is measured as time spent Blind, not the number of Blinds cast. [CHANGELOG 4r]
- R-089. In the power-play node, damage, pushing and control are measured only up to the first kill, as the fight node does. [CHANGELOG 4r, item 7]
- R-090. A team's choice at a decision point is what it did in its first seconds, not over the next 20 s. [CHANGELOG 4r, item 6]
- R-091. Pressure beyond damage is measured per player: kiting and pre-kiting (against warriors, dervishes and assassins only), degeneration (pip-seconds, uptime measured), baited interrupts (provable ones only), offensive knockdowns (and on casting targets), disables, and cast prevention. Their thresholds are definitions; what each is worth comes from the nodes. [METHODS "After chunk 4"]
- R-092. Kiting away from a frontline to avoid damage and waste its time is valuable; faking out an interrupt is valuable; degeneration pressure counts as pressure; offensive knockdowns count. [METHODS "After chunk 4"]
- R-093. Healer focus (share of damage on enemy healers) is a model variable in the power-play and fight nodes. [CHANGELOG 4t]
- R-094. "Defenders pushing the runner" read backwards because of Claude's measurement (captures only); fixed with the run defence node. [CHANGELOG 4q]
- R-095. Readings that ran against expectation at chunk 5 (knockdowns on casting targets in fights, pre-kiting on deaths) are held for more data, not corrected. [METHODS "After chunk 4", footmen note]

## Splits and collapse

- R-110. A solo split is one player going through the back or an unconventional route to hit the enemy pit or NPCs, defended by the 8 monk or one damage, or collapsed on. Three or four man splits push the enemy's backdoor to take NPCs; a four man split is a 4-4. [tactics S1, S2]
- R-111. A full team collapse (the whole team turning on an enemy group) is not a split answer. A collapse means defenders collapsing on a split. [tactics S5; CHANGELOG 4q]
- R-112. A match can move between 8v8, 7v7, the flag game and splits; all need to be understood. [tactics S4]
- R-113. Against a spike or other 8v8 build that out-damages you at main, splitting is right, and the split has to be aggressive, usually including the 8 monk; the main team then plays in its pit. [tactics S6]
- R-114. One enemy damage held by one monk in base is usually a worthwhile trade for the splitting team: four damage kill two monks more easily than five kill three. [tactics S8]
- R-115. Whether a solo split is worth it depends on how effective it is and what it accomplishes. [tactics S9]
- R-116. Answering a split within about 15 s is on time; 60 s is definitely late. [tactics S18]
- R-117. A lone ranger split is answered by the Mes/A plus a frontline collapse; the Mes/A cannot defend alone. A good answer to a solo split is one player collapsing while another defends. [tactics S19, S26]
- R-118. Defending a split with the 8 monk keeps all the damage at main: a trade-off that may pay off if the main team scores kills; needs data. Sending the 8 monk alone against a three man push is a mistake. [tactics S20, S25]
- R-119. Once the pit is dead, the 8 monk staying in base to defend the Lord is right: a Mes/A cannot hold a ranger alone with no pit. [tactics S21]
- R-120. If the enemy prot is pushing with its team while three of your damage are on your push side, your push side should be able to kill. The prot follows the third damage: each monk can usually survive two damage with team support, not three. [tactics S22, S23]
- R-121. A snare on the defender changes the answer to a lone attacker: without one, hold 1v1 and part-run flags, keeping the NPCs up; with one, collapsing is most likely the better play. [tactics S31]
- R-122. Whether to collapse on a split has no fixed line: it depends on the plan (NPCs or DP), whether the defender can hold without losing NPCs, the flag position, how the main fight is going, what the split can get NPC-wise, the death penalty on the split character and whether it can be killed. The line comes from the data. [tactics S32]
- R-123. A quick collapse that fails to kill costs, because it fails twice: no kill, and the split is not pushed out. A collapse that does not kill wastes the collapser's time. [tactics S31, S32]
- R-124. Collapse timing is very important, and the right timing is for the data: five readings are tested (arrival spread, numbers at contact, time from the split's first NPC hit, res timer at arrival, escape skills off recharge). [tactics J7; CHANGELOG 4q]
- R-125. An 8v8 build answers a three man split by ignoring it with the main team and having a snare character in the 8 slot shadow it, snaring when it commits so the spikers can collapse and kill. [tactics S41]
- R-126. A three-man group of the 8 monk and two damage on the backside is a correct answer to an enemy ranger and hammer pushing there. [tactics S36]
- R-127. Split depth (the split's nearest member's distance to the defending pit) is a collapse variable. [CHANGELOG 4s]
- R-128. Return is an escape, never a snare. Area snares count one target (rarely is more than one player snared); uptime is limited by recharge; where the replays record the slow on at least half of a skill's uses and it has 15 or more uses, the measured figure replaces the formula. [CHANGELOG 4t; METHODS "After chunk 4"]
- R-129. Snare strength is preferably measured from the data; where a rule set is used, recharge and duration must be taken into account (permanent snare worth more than a long-cooldown one). [METHODS "After chunk 4"]
- R-130. The split_or_stay decision: every 30 s from 1:00, a team not already splitting with six or more alive either starts a split within 30 s or stays. [CHANGELOG 4t]

## Pit NPCs and Lord

- R-140. The pit roster is 2 knights, 2 archers, 1 Bodyguard and 1 Guild Lord, with a third archer only on Isle of Solitude. NPCs never seen in a replay are added from the roster as alive all match. [CHANGELOG 4m; METHODS "Data integrity"]
- R-141. Guild Lords regenerate 10 health per second always, plus out-of-combat regeneration once unhit for a few seconds, rising from +2 to +10 per second; the Amulet of Protection adds healing. Recorded Lord damage is taken as already capped. [CHANGELOG 4m; METHODS "The Lord"]
- R-142. Lord damage only decides a match at 28:00 (the tiebreak), so it is read together with the clock and has no curve of its own in the win model. [data/model_corrections.json; CHANGELOG 4s, item 1]
- R-143. Each team's measured Lord damage per second is one value per team per match; its curves are capped at 5 points. [data/model_corrections.json]
- R-144. A pit knight is worth about as much as a death. [tactics W12]
- R-145. In non-split situations teams take the knights first. A full pit is harder to defend for the monks: extra targets, and knights ball up in area damage. [tactics P9]
- R-146. Two monks on the push side is the norm against a full or mostly full pit; against an empty pit a team sometimes pushes with one. [tactics P10]
- R-147. In the last seconds before the defenders' base res, attacking teams often leave the pit so they are not caught 8v8 when the team resses. [tactics P11]
- R-148. A value of taking pit NPCs during a match is that fewer players need to go to the enemy base at 28:00 while still breaking Entourage. [tactics W4]
- R-149. Builds differ in how easily they get Lord damage late: a balanced build gets it far more easily than a 2-monk hex way, so a balanced team that survives 26 minutes without deaths or NPC losses is winning against it. Winning on Lord damage at 28:00 is not viable while taking deaths against a spike build like WoC. [tactics L1, B6]
- R-150. Players cannot see Lord damage in game; sending some players for more Lord damage while defending can be the safer choice. [tactics L2]
- R-151. Protting your own NPCs instead of your Lord is deliberate: enchantments on your own Lord cost aggressiveness. [tactics L7]
- R-152. What a wipe can be turned into depends on where it happened; from a wipe at the stand a team is unlikely to reach the enemy base before the res. For a 2-monk spike build the weighing after a wipe is often reversed: DP on the enemy is worth more than NPCs. Teams very rarely rush into the enemy base to spike players as they resurrect. [tactics D5, B23]
- R-153. Footmen are read as footmen lost, not footmen alive (a footman only enters the replay once touched, so "alive" marked a base that had been visited). [METHODS "After chunk 4", footmen]
- R-154. Enemy players hitting the pit NPCs from outside the pit count as attackers in the NPC nodes. [METHODS "After chunk 4"]
- R-155. The collapse node and the split-in-base decisions carry the split's NPC damage, the defending NPCs alive, the split's worst morale, its healers and self-defence, and the defenders' damage. [METHODS "After batch 10"]
- R-156. The three engine questions after chunk 2 (npc_damage_5s as context, chaining defenders back to the fight before, testing split_diff) are disregarded; TQ 4 may keep listing "no damage on the NPCs" as its top fix and the reader reads past it. [CHANGELOG 4t]
- R-157. Teams resign when a match is lost. In mid-game (about 6 to 12 minutes) teams that look beaten still come back about one time in five. [tactics W2, W13]
- R-158. Near the enemy's boost clock, falling back is likely a mistake unless the team is losing the fight; what decides staying against falling back is own monks' energy, enemy health, the enemy's estimated energy and any numbers advantage. [tactics D4]

## Builds and strength

- R-170. Matches are blind: teams do not know the enemy build in advance, so a build call out is about the matchup, not a mistake. Call out the skills that matter for the matchup (Infuse Health against a spike, Purge Signets against hexes, Aura of Stability against hammers). [tactics B1, B2]
- R-171. Spike and 8v8 builds want to fight 8v8 and keep their damage together ("6 damage builds"). WoC spike has low healing and defence; the counter is to split hard or survive a few spikes and wipe them. Invoke spike runs air elementalists with usually two monks; in hex way a ritualist in the 8 slot is normal. [tactics B4, B5, B9, B11]
- R-172. Builds means individual bars too: one skill can change the right play, and team builds change what results are worth (a 2-monk spike build is behind on Lord damage late, so pit NPCs matter less to it and DP more). [tactics B23]
- R-173. How hard each build matchup is has to come from data. [tactics J10]
- R-174. Plans (8v8 brawl, flag game, split pressure, holding in the pit, power play, late Lord push) are a starting list; Claude finds more and amends them from data. [tactics J11]
- R-175. gvg.report's guild Elo is its own calculation and far better than the in-game ladder; gvg.report's player assignments are added to the site's, with Denning's assignments winning; MAT results are weighted more, the amount measured (x2). [CHANGELOG 4m]
- R-176. Healing-monk counts are dropped from the win model (almost every team runs three; the curves memorized teams). [data/model_corrections.json]
- R-177. Energy is not estimated from casts: too large a build for what it adds. [HANDOFF "Decisions made"]
- R-178. The optimal play differs by map, so the engine carries map geometry as a variable and splits readings by map. [CHANGELOG 4p]
- R-179. The right strip target and the right hexes to remove are valued from data (every enchantment or hex in range at the moment), not from a list. [CHANGELOG 4q]
- R-180. Situation cards (tactics section 14) are hypotheses for the data to test; D6 has no default. [HANDOFF "Open items"]

## Model and engine rules

- R-190. The goal is plays better than experts can see, from data across many matches: not to mirror Denning's or anyone's judgement. Rulings give definitions and test cases; values and best plays come from the data. [HANDOFF "Goal"]
- R-191. Nothing is a weight or a default unless it is measured or is a definition. Thresholds that define terms may come from Denning; anything that says how much something is worth comes from the data with its uncertainty. [METHODS "From rulings to data"]
- R-192. The model learns like a neural network but is white box: non-linear effects and interactions from data, everything learned readable, every judgement a breakdown of contributions, amendable by Denning with every correction logged with its reason and tested. [METHODS "Requirements"]
- R-193. Build the structure first, then train slowly with a learning report after each batch. Discovery of variables and interactions nobody is aware of matters most. [METHODS "Requirements"]
- R-194. Context-only variables (strength, build skill counts, flag lead, morale, the minute, the res timer) are never priced as causes or offered as fixes. [CHANGELOG 4r, item 8]
- R-195. A link that came from Denning is never rejected by the data without his ruling (held as pending rejection, shown with what the data looks like); once he approves the override, the link follows the data both ways and can return to supported. [CHANGELOG 4q]
- R-196. Links found by discovery are held for Denning's approval and never added automatically. [CHANGELOG 4p]
- R-197. Learned links change status batch by batch; the proposal to change status only after two batches in a row was declined. [CHANGELOG 4r, item 10] [check: possibly superseded by R-237, which applies a two-run rule to discoveries, not to link status]
- R-198. Values are measured against matched moments without the event (same minute band, same win-chance band). [CHANGELOG 4r, item 15]
- R-199. Win chances go through a calibration by minute built from held-out predictions; the calibration must follow the data in every band and never go flat. [CHANGELOG 4r, items 5, a, f]
- R-200. Directions forced, never dropped: more enemy time down can only help (down_diff_s), and flag lead can only rise. [CHANGELOG 4r, item 4, e]
- R-201. The cap on spike_killable_diff is chosen by the data (10, 15, 20, 25 points or none) on unseen matches. [CHANGELOG 4r, item 3]
- R-202. Build-fixed values (Lord damage per second, spike build) never pair with morale; morale x map geometry pairs are kept or blocked by a held-out test. [CHANGELOG 4r, item 2, b]
- R-203. Snapshot comparisons of winners against losers are made at the same win chance, or labelled as including who was ahead. [CHANGELOG 4r, item 9]
- R-204. TQ what-ifs that are not monotonic, that leave the node's training range, or that run against the changed variable's own curve ("from a pairing") are marked unreliable and kept out of fixes and confidence. [CHANGELOG 4r, item 16, c]
- R-205. Chains go back to the last reset (both teams 8 alive, flag lead within 10 s) or 3 minutes, follow the two biggest causes at each link, and name fixes only where they mattered most. "How it got there" is the chain of game states, not only position; the further-back cause is wanted, not last-second options that could not have saved it. [CHANGELOG 4p, 4t]
- R-206. Node-model chains (causalchain.py) replace the rule-based chains in the TQs; a cause or fix must sit at least a quarter of the variable's spread from its usual value (minimum-change rule). [CHANGELOG 4t]
- R-207. Forensics position is judged on the last few seconds before a death (the window the data picks from 3, 5 and 8 s); the 3 s window is acceptable. [CHANGELOG 4s]
- R-208. The power-play and fight nodes, the deaths and kill-conversion nodes, forensics and the snapshot carry the pressure measures (R-091). [METHODS "After chunk 4"]
- R-209. Discoveries approved after chunk 4: fight outcome own hexes and own heals; power play enemy strips against own prots; split chance spike build and own knockdowns; split effect own escape power; collapse enemy healing monks; run defence own area damage, enemy snares against own speed, own healing monks; split answer own area damage. The state findings were left out; enemy energy denial against own heals was held for another run. [METHODS "After chunk 4"]
- R-210. Approved after session 4t's discovery: state variables as context in the fight, flag swing, run, power-play and split nodes; snare skill counts on the run nodes; the defenders' prots on split effect; Deep Wound on split effect left for more matches. [CHANGELOG 4t]
- R-211. Moved into the win model: split_diff (after batch 10), footmen (after chunk 4; as footmen lost after chunk 5). [METHODS "After batch 10", "After chunk 4"]
- R-212. Made model variables after the first six OG comms matches: solo healer, group with no healer, own morale, allies in area; attackers' share in the pit; win-model candidates footmen, no-healer groups, solo healers and turtling. [METHODS "Commentary and comms"]
- R-213. Supported commentary variables become model variables; contradicted or unclear ones stay recorded as open questions so they are not re-proposed without new evidence. [METHODS "Commentary and comms"]
- R-214. Runner choice penalties (assassin, paragon) are not addressed for now. [CHANGELOG 4t, chunk 1]
- R-215. Blind on the enemy frontline -> fight outcome (Denning's link): keep, wait for more matches. [CHANGELOG 4q]
- R-216. The win model alone explains who is winning, not why; the causal map must explain why (flags, boosts, wipes, pits, damage output). [METHODS "The causal model"]
- R-217. The causal map's links must be reflected in the model's connections, not only in TQ reasoning; chains the data finds are held for approval. [HANDOFF "Goal of the current build"]
- R-218. Discovery runs across several machines; training batches run on GitHub (the Train batch workflow), not in the chat. [CHANGELOG 4p; CLAUDE.md]
- R-219. Process is code: thresholds live in common.py, prose instructions stay short, and the toolkit is improved rather than one-off scripts written. [METHODS "Where things are stored"]

## Reporting and process

- R-230. After each batch the report is the detailed why, not a broad breakdown or one highlighted item: a snapshot across all the learnings, favouring the detailed ones (skills cast, run times, runners, node readings, values, usual play, discovery). [CLAUDE.md]
- R-231. The TQs are the four question categories answered after each batch, each from the batch's matches, with the different play or prevention from measurement and a confidence level: (1) a team behind on flags and why, then how a different play could have increased its win chances; (2) a monk death and why, then how it could have been prevented; (3) a power play without a kill and why, then how it could have been converted; (4) NPCs lost and why, then how it could have been prevented. [CLAUDE.md; METHODS "The TQs"]
- R-232. The four answer exemplars (Book v TFS flags, the RACK 8 monk death in RJT v RACK, True v One power play, Team v push spike) set the depth every answer must reach. [METHODS "Answer exemplars"]
- R-233. Every why is answered with data: position, prots and whether they were the right kind, interrupt pressure on the healers, damage taken off shield sets, both teams' output, peel, casting into ready interrupts and cancelling, conditions and removal; and the why of smaller events, not only deaths. When the data cannot answer, say so and add the measurement rather than guess. [CLAUDE.md]
- R-234. Insights are about decisions and consequences, not correlations; each analysis ends with specific questions for Denning. [CLAUDE.md]
- R-235. Show Denning any of his links the data rejects, with what the data looks like, and he rules on each. [CHANGELOG 4q]
- R-236. No dates on Denning's tactical lines; Denning's lines override everything on the tactics page; match reviews carry Claude's own macro and micro learnings labelled as Claude's. [CLAUDE.md; tactics]
- R-237. Terms: base (not home), backside and push side, pit NPCs (not guards), the pit, outside archers, backline (monks), midline (elementalists, rangers, paragons, mesmers), frontline (dervishes, warriors, assassins, by build), roles by slot (prot, 7 monk, 8 monk, stand mesmer, Mes/A), Y (spawn to stand), backup flag; times in match clock. [tactics "Language"]
- R-238. Never abbreviate Master of Damage; do not use "My" in page names or text; Victory or Death is no longer in the game. [CLAUDE.md]
- R-239. Review format: summary paragraph first, then decided by, deciding moments, sources, questions. [HANDOFF "Conventions"]

## Moment rulings

- R-250. [hdm v HC I2] 5:01: the split was missed (131 s); the 8 monk defending the lone ranger was likely wrong but a real trade-off; at 7:10 the 8 monk in base after the pit died was the right call; losing the stand that close to the boost was normal; one damage pushing the flagger was fine; the moment at 1:02 was a full team collapse, not a split. [data/review_labels.json]
- R-251. [hdm v HC I1] 8:10, HC prot death: a great play by hdm, not a failure by HC: even 8v8, monks in position, coordinated knockdowns, Daze, interrupts and a strip; acceptable mistakes were casting beside the ranger without faking, Aura of Stability not kept on the 7, mesmers not interrupting defensively; the quarter-second interrupts were luck; pre-kiting with a stance and hitting the Mes/A were correct. [data/review_labels.json]
- R-252. [Men v HC C] 9:31, HC 8 monk death: casting beside the ranger was a minor mistake; the 3-man backside group was correct; the mesmer should have interrupted defensively and someone should have peeled so the 8 could kite. HC was up on flags; running 3v4 while Men ran was an unnecessary risk: the runner could wait to cap and the backside group should have fallen back toward pit, following only if Men went for the runner. Not double running; half running too risky. Engine cause: outnumbered away from pit while up on flags (minor). [data/review_labels.json]
- R-253. [BcS v Crew] 15:11, all five living BcS players went backside to convert with their pit empty and three dead: Denning does not know; the data decides, through discovery and priced chains. [CHANGELOG 4r]
- R-254. Death rulings 3 to 5 and power plays 6 and 7 in [Men v HC C] remain open. [HANDOFF "Open items"]

## Rulings of the 2026-11 review

- R-260. The engine is one model family in four tiers: context (fixed per match: strength, builds, map, flux, period), state (the scoreboard every 5 s), decision nodes (what a team chooses), execution nodes (how well a chosen play was carried out), and the win model. Each question lives in exactly one node; duplicate nodes, the rule-based chain engine and the duplicate discovery module are retired, and the causal map describes only what is fitted, with unfitted hypotheses in a waiting list.
- R-261. Strict time order in every execution node: inputs are measured before the window opens or in its first seconds; the enemy's concurrent response (healing, prots, kiting during the window) is shown apart as "what the enemy did", never as a cause.
- R-262. State variables are adjustment in every node and never a fix; context is never a fix.
- R-263. Inputs are pruned to what the data carries: about 20 events per input for a yes/no outcome. Supported links and Denning's links are kept; Claude's "not clear yet" hypotheses move to the waiting list instead of being refitted every chunk.
- R-264. A standing selection check on every play variable: if it predicts the outcome of the previous window as well as the next, the report labels it "marks the situation" automatically.
- R-265. Discovery offers only decision and execution variables (never state variables), and a discovery must survive two discovery runs before it is shown.
- R-266. One bundled engine change per run of chunks: chunks are data only; proposals queue; one engine change, one rebuild, compared against the reading just before it.
- R-267. Reports are diffs: what changed since the last batch (status changes, curves that moved beyond a threshold, new supported links) plus the TQs; full tables go to files.
- R-268. A generated model page, rebuilt each run (question, row unit, rows and positives, inputs grouped by link with status, held-out score against baseline, last engine version that changed it), is the structural reference. Prose documentation is a spec that is replaced, not appended to; dated session logs go to the changelog, ten lines per session at most.
- R-269. Before an engine change ships, a fresh Claude session reading only the generated model page must be able to explain each node in GvG terms.
- R-270. Every event is answered as two questions: macro ("what should the team have done", from the decision node and the usual play) and micro ("what went wrong in execution", from the execution node's play measures), each with its own answer. The TQ answers so far have told Denning nothing new.
- R-271. Decisions the engine recognizes, beyond run or hold, who carries, split or stay, collapse or defend, push or hold a power play, after a wipe and 24:00: offensive or defensive play; 8v8 or flag game; who to defend with; try for NPCs or for DP; play for 28:00 or try to kill the Lord.
- R-272. The end product is a query: a match moment (or a situation and builds) in; the data-favoured decision, the usual play, the margin, the evidence and the execution faults out.
- R-273. Period (the meta) is a context variable, and readings are checked across months so a patch does not silently invalidate advice. Readings are also checked by strength band.
- R-274. The goal test is whether teams whose choice matched the model's recommendation did better on held-out matches, plus a sealed blind test of Denning's calls against the model's, both scored by outcome.
- R-275. Questions for Denning come from the variable catalogue and the behaviour-cluster mechanisms (name this, approve that), not from a few variables proposed per batch.
- R-276. Variables are generated from the replay schema as a catalogue (recorded thing x subject x filter x window) and screened by discovery with the chance rate stated; decisions are found as behaviour clusters at every recurring state, with example moments, for Denning to name or reject.
- R-277. Denning does not need incremental result progress; the goal is a great model first and results after.

## Rulings of 2026-11-09 (after the review bundles)

- R-278. Input cap: when a node is still over its cap after Claude's links and unclear discoveries are pruned, Denning's not-clear links may be pruned too (last in the order); they wait on the waiting list and return as the data grows. Supported links and links Denning rules to keep are never pruned.
- R-279. Decision detections confirmed, with one change: offence or defence reads the disrupting players' first 15 s (10 s is short for disrupts), 60%+ on midline and frontline = defensive, 40% or less = offensive. 8v8 or flag game is a power play when not up on flags (recently capped or about to cap, the enemy about to over-cap): commit all 8 to kill, or send someone back to keep running. Who defends: as detected.
- R-280. NPCs or DP: the moment is killing 3+ enemy players at or past their footmen (inside their base, about 2,500 around the res shrine, or their pit); the choice is NPCs before the res, DP on the survivors, or both. The better play likely depends on the build (a two-monk spike build may value DP); the data decides.
- R-281. Play for 28 or the Lord is not a 24:00 decision but a global one from mid game on, for a team that has taken 1+ NPCs in the enemy base: play for 28 (safe: flags, defence, NPC and Lord damage, win on Lord damage at 28:00) or push for the kill before 28:00. Detected from 10:00 every 60 s (push = 3+ at the enemy pit in the next 60 s); Denning did not fix the exact minute.
- R-282. Allocation decisions (how many escort, how many defend, who stays on flag duty, split size and healers) are choices, not only markers: an input flagged by the selection check may still be a fix when it is an allocation decision ("don't escort your runner while a split takes your NPCs"; "send one more to push side"). The flag is kept and shown beside it.
- R-283. Kiting (P.21 -> fight outcome) stays in the model by Denning's ruling whatever the data says. Pre-kiting (split off as P.27) and Blind on enemies (P.19) sit as the data reads them (rejected for now) and are remeasured each run.
- R-284. Blind test: eight picks a round, six random and two where the engine's advice differs from the usual play; a round is added after every chunk and never refreshed, open rounds wait; answered and scored on the site (Model > Blind test), with a reason field.
- R-285. Reactive execution inputs (disables on the enemy in a power play, healing on own pit NPCs) read backwards: more of them goes with the bad result because teams do them when the result is already coming. Every execution input carries an expected direction; an input whose curve runs against it is labelled "reads backwards: likely a reaction" and is never a fault or a fix. Claude's direction list, to confirm.
- R-286. Discovery offers own_ and diff_ (own minus enemy) catalogue variables; enemy_ variables are the enemy's concurrent response, never offered, and the matching enemy_ reading is shown beside a candidate as "what the enemy did".
- R-287. The engine's pages (structure, what it learned, win model, causal map, learning report, values, behaviour clusters, discovery, blind test) live on their own Model tab; GvG tactics and match reviews stay under Mechanics.
- R-288. Direction signs confirmed (2026-11-09): run outcome: control, damage and pushes on the runner so far hurt, and read as a reaction (those runners are already nearer the stand), which should be reflected in capture speed as well; seconds the carrier still needs hurt. Run defence and capture speed: defenders pushing, controlling, damaging and snaring the enemy runner help. Power play: damage v the usual, spikes, spikes and damage on healers, knockdowns, knockdowns on casters, disables, cast prevention and degen help; loose spikes and own attackers Blind hurt. Splits: speed power, escapes and escapes off recharge help.
- R-289. A runner's Shadow Steps are no longer a variable: since a recent patch a Shadow Step drops the flag, so the mechanic is gone. Retired from run outcome; a replacement, if any, is open (Claude's suggestion: a "flag dropped by a Shadow Step" execution fault on answers).
- R-290. Fight outcome (global): good = Blind on the enemy frontline, defensive Blind, damage v the usual, removing the right hex, kiting, degen, baited interrupts, knockdowns and knockdowns on casters, disables, cast prevention, strips on the right target and strip value; bad = casting into a ready interrupt, casting while Dazed, attacking while Blind, loose spikes. No sign can be given yet for pre-kiting (unknown) or peel on own backline's attackers (good in defensive play; in offensive play damage may belong on the enemy backline or midline). Hexes on own players are generally bad but depend on the hex's value: removing a harmless hex costs monk time and energy, so leaving it can be right in a close fight; and trigger hexes (Mind Wrack) are removed when they fire, so a team under energy pressure shows fewer hexes on it while taking the damage.
- R-291. Healing on own pit NPCs and Lord helps, but needs breaking down: which NPC is healed (under AoE, such as a Dervish on balled NPCs, common wisdom heals an archer over a knight; the Bodyguard over the Lord while both are up), and heals that are enchantments (Patient Spirit, Reversal of Fortune) may be bad to cast on the Lord when Lord damage is in play.

## Rulings of 2026-11-09 (decision redesign; plan in docs/REDESIGN.md, built in steps)

- R-292. Blind round 3 is void. New rounds are paused until the decision card exists. Rounds 1 and 2 are kept as the first design and left out of the cumulative score.
- R-293. R-284 is amended: five picks a round, at least three where the model differs from the usual play, chosen for leverage and a real choice; at most five options plus "Other"; scored cumulatively with a range; a reason whenever Denning differs from the model.
- R-294. A call is read over 20 to 30 s from positions and commitments, not from damage or deaths (10 s is not enough in player-movement terms). Outcomes are read at 90 s and about 3 minutes, as hard results beside win points.
- R-295. Decisions are organized as five families (flag decision, answer to a split, numbers advantage, game plan, engage or wait), each with scenarios, and each scenario with its own options.
- R-296. The enemy's decision to run or split is read from the moment a player leaves main, the res shrine or the base (a player who waited in base from the start can go on to run a second flag after the cap, or to solo split), and is labelled afterwards by what the leave became. A player can usually tell in the moment whether an enemy is going to run or to split, from things inherent to the game that are not worth measuring, so a blind pick says what the leave became.
- R-297. A call has a shape: composition (who), route (which way) and timing (when). Composition and route are decisions. A delay is a decision when something was being gained elsewhere (a live numbers advantage at main), and execution otherwise.
- R-298. Each call has a job with a success test read across the whole map (a three-player split into four defenders succeeds by not dying and wasting enough time for main to kill 5v4; it does not have to take NPCs). Playing for the wrong job (jumping into the enemy pit and dying) is an error of execution, not of decision, and is reported apart from mechanics.
- R-299. A call gets one of three verdicts: right, wrong, or no clear difference. Execution is read before the result. The enemy's execution is scored and never offered as a fix.
- R-300. The decision card is the single answer format for the blind test, match review and query tool; the blind test, correctly built, replaces the TQs as the view of how the model is progressing.
- R-301. A numbers advantage is read from both sides: the side that is up and the side that is down each have a decision.
- R-302. Maps are pooled by their features and never restricted to the same hall (the same game state can call for a three-player split on Uncharted Isle and not on Druid's Isle); a single-hall reading is shown when the hall has enough cases. Denning's map labels override estimates.
- R-303. Detection is tested against golden moments labelled by Denning before a rebuild is accepted and after every later engine change.
- R-304. Offence or defence is not a decision of its own: it is part of the objective layer of a fight (whether the disrupting players played on the enemy healers or on the midline and frontline).
- R-305. Double run, defined: two players are never sent to the flag spawn together (a waste of one of them). The forms are: (a) one player runs back to the spawn while the flag holder goes to cap; (b) the second runner stays at main until the first has picked up, then runs back to the spawn as the first runs to cap; (c) the half run: the first player carries the flag about half-way to the stand and drops it for a second player, who picks it up and caps while the first runs back to the spawn for another flag.
- R-306. Where labelled map areas overlap, the smaller area names the zone: falling to the pit is described as distinct from falling to the base, though the pit lies within the base.
- R-307. "At the footmen" or "fell to footmen" means the area around the footmen such that they are engaged in the fight. It is not a fixed distance and not the choke point.
- R-308. The obelisk on Isle of Meditation is still a feature but is almost never used.
- R-309. Isle of Solitude's teleporters are one way: in beside the Guild Lord, out on the main field.

## Rulings of 2026-11-10 (guild halls; detail in knowledge/guild-halls.md and data/maps/hall_features.json)

- R-310. Every pit holds one Guild Lord, one Bodyguard, two Knights and two Archers; each side has one res shrine and one flag spawn, and the same number of every other NPC as the other side. A labelled hall that breaks this is a labelling gap, not a feature (`tools/maps/audit_labels.py`).
- R-311. Not every hall has footmen, so falling back to footmen is not always an option; where there are none a retreating team falls back to its front door or its pit. "Fell to footmen" (R-307) exists only on halls with footmen.
- R-312. A hall's features carry decisions of their own, and they must be accounted for in decisions: which way to run the flag where a hall has two real flag paths (Druid's Isle: the long way, or over the vine once the seed is capped; Isle of Jade: over the bridge, or over the coral; Imperial Isle: the short way, or the long, safe way); whether to cap the vine seed (Druid's Isle); gate control and collapsing through the gate (Isle of Weeping Stone); the gate levers, and splitting through the bridge gates or around the back (Frozen Isle); the repair kit: run the team's own home, run it to the enemy trebuchet, or push to steal the enemy's (Warrior's Isle); fighting or splitting for the health shrine at the cost of numbers or flags elsewhere (Isle of Wurms); killing the flame sentinels at the start, and timing a split on whether they are dead, about 8:00 if left alone (Burning Isle); splitting out the teleporter (Isle of Jade, Nomad's Isle).
- R-313. Two flag paths are a decision only when they differ in length or danger: Isle of the Dead's two end in about the same place and are not one. Its front and back doors differ only in that the back door (usually the split side) runs over the bridge.
- R-314. On Druid's Isle, not standing in the healing water while the team is around the flag stand is a micro (execution) mistake.
- R-315. Isle of Weeping Stone's gate lock is only available from the back side, so gate control is taken from there (this narrows R-312's gate line: the collapse through the gate, either way, is open only to the side holding the back).
- R-316. A route drawn through a teleporter on the map shows the full drawn distance, because a hop of no length cannot be drawn. The hop counts as no distance: route lengths and path distance take it out (Isle of Jade's coral flag runs and back doors, Nomad's Isle's back doors). In the engine this waits for the next rebuild (REDESIGN.md step 2).
- R-317. Label readings confirmed: on Warrior's Isle the marker nearest the flag stand on each side is the repair kit and the two outer ones are the trebuchets; on Druid's Isle the vine seed points inside the bases are the spawns and those outside are the drop spots; Isle of the Dead has one bridge, crossed by both back doors; Nomad's Isle has no footmen.

## Rulings of 2026-11-10, second session (redesign step 2: zones, moments, golden moments)

- R-318. Isle of Solitude's two flag spawns are accepted. On Isle of Weeping Stone the one outer archer a side that does not mirror is as it stands in the game: not a labelling gap (`as_in_game` in hall_features.json; the audit skips it).
- R-319. A group is "at" a place (the stand, the pit, the base) when more than half of its living players stand inside the labelled area.
- R-320. "Fell to footmen" (R-307) is read from the labelled Footman positions, now that the maps carry NPC positions. How far around them counts is measured, not set: the distance within which footmen actually hit players on that hall (Claude's method; the 75% cut is Claude's, to confirm).
- R-321. "Something gained elsewhere" (the timing rule of R-297) is a live numbers advantage at main, NPC damage in progress, or a boost about to land.
- R-322. Bundle 4 is built on the branch `bundle-4`. Main's engine stays frozen until the bundle is complete, so chunks can still run; the golden moments page and its data live on main.
- R-323. Left to Claude by Denning, who can change either. The golden moments pass: the engine finds the moment in 9 of 10, and agrees on each part of the scenario and on the call in 8 of 10, with every miss either fixed or brought to him as a definition to rule on. The advice test for bundle 4: the replaced kinds and the new families run side by side for that one rebuild, the old kinds are compared with their reading before it (6 of 13 clear at 506 matches), then retired.
- R-324. All five queued measurement proposals go into bundle 4 (control by distance to the stand; flag dropped by a Shadow Step; hex value including trigger damage; NPC healing by target and kind; path distance with teleporter hops).
