# Definitions: the words as they stand

The current meaning of each word the engine reads, by topic, with the rulings each line rests on. This page is a
consolidation (R-452): `docs/RULINGS.md` stays the record of what Denning decided and when, and it prevails if the two
disagree (this page is then corrected). Replaced in place when a ruling changes a definition; nothing is appended with
a date. Covered so far: counting players, flags, splits, collapse, the Lord push; the other topics are consolidated at
the review of R-398. *Draft* = Claude's, not ruled. *Open* = waiting on him. *As built* = how the branch measures it.

## Counting players
- A player counts in a fight, on a split or on its defence after 12 s there; less is support, or passing by (R-350,
  R-439). A death there counts at once. A walk through a teleporter and straight back is not being there (R-442).
- Who is on a split is who is there at that time, not everyone it ever held (R-439).
- The match is over when the losing team is recorded dying all at once (its Guild Lord dead, or the 28 minutes up),
  some 12 s before the replay stops: those are not deaths, and nothing is told from that second on, nor a base res
  that falls on it (his marks on RACK v hdm 0:22, Men v RACK 19:06 and Men v Crew 27:40). *As built* (`Moments.over`):
  five or more of one team dead within 2 s in the replay's last 20 s.
- A numbers difference is answered for as long as it lasts: a team that stands at first and falls back later has
  fallen back (his marks on HC v hdm 1:00 and Men v Crew 3:38). Its row ends when the numbers do; its job is judged
  a short tail longer (R-424).
- A player counts in one fight only (R-488, R-519). Where the main fight and a split's fight stand within reach of one
  another he is in the one whose players he is hitting or casting on, or who are acting on him; if neither, the one he
  is moving to. *As built:* asked of every player the main fight's numbers and a split's reading both count for 12 s;
  a defender by his trades with the split's players against his trades with the others who stand two or more together
  (one enemy coming alone draws nobody off the defence); a split player by whether the enemies he trades with are
  trading with his own main team; with no trades, by whom he heals or protects, then the players of his side he
  stands with, then the fight he closes on, and failing all that he stays on the split or its defence. Read second by
  second, so that his fight can change; a turn of under 12 s is no turn.
- A split is a decision from when the other team would see it and have to respond (R-510). *As built:* told from the
  crossing to the enemy's side, or from 4 s after its players left their team when they go straight across; the row
  says when it reaches their base, their footmen or a defender. Where its team is held in its base, it is told from
  4 s after its player goes out past his own doors, however long he takes to cross (his Classic mark, Men v hold 17:01).
  Its door is the enemy's door it first comes to; a later phase whose players all start it out in the field takes the
  door they come to then (his Classic mark, Men v hold 10:40: the five regroup in the field and go in by the back).
- Who comes to a split fight and who leaves it are decisions of their own, each kept as its own record and shown in the
  split's row (R-511, R-514): a collapse
  when the defence becomes one more than the split as it then stands, else a join (R-441), also when the player comes
  from the main fight and only makes it even (R-516, "for now"); a leave when the player goes alive. The jobs of a join
  and a leave are drafts.
- The main team: in an even split, the group on the stand side, responsible for flags; monks only break a tie (R-335,
  R-355). In an uneven divide, the larger part (R-421, R-487). An even divide with both groups on the main flag
  path is a push team (forward, at the enemy's door) and a defence team (at its own), not a main team and a split
  (R-487).
- At an uneven divide the larger part at home is the main team and those who go out are a split (R-487, R-513); a
  team standing in its own pit has not gone round the back.
- A guide to telling a split from a main team, his of 2026-11-17, not a ruling and not to be applied strictly:
  "Splits are almost never going to be in their own base. Mainteams can end up basically anywhere on the map. A small
  group of players in their own base when their mainteam is elsewhere is most likely going to be a defense. A split
  will basically never be in their own base except when they are leaving or returning." *As built* (`main_team`,
  switch `HOME_GUIDE`): a part at home is the main team or a defence, never the split. Where more of a team stand at
  home than in any part away, and the engine's main team is a part away, the part at home becomes the main team;
  where the engine's main team is a part at home and a part away is bigger than all the players at home together,
  that part becomes the main team and those at home are defending; either only after it has stood for 12 s. An even
  divide stays with the flags and the stand side (R-335), and a base that is held in with R-506.
- A main team that goes round the back is still the main team (R-502): when all but two of a team stood together
  and then spread out, the main team is one of its own parts, not the runner and the player with him; five or more
  of its players on the enemy's ground round the back, two more than the part on the front lane, are the main team
  there; and a split is over once two or more of the rest of its team stand with it in a group of five or more.
- Players who leave a base that is held in are a decision for the enemy at once, whether they are called the split
  or the main team (R-506, his to revisit). *As built:* with the enemy's main team (five or more) in the base, the part
  at home is the main team and those who left are a split from the second they leave, when they are as many as those
  who stay or more.
- A player cannot be in two fights at once, and some are in neither: moving to position with no output (R-488).
  Numbers are told only when they last 12 s; "no clear decision" is an answer (R-488).
- On a split: the players who came with it and stand with it, its back line included; brief support is not one more
  (R-484). A fight between a split and its defenders is told once, in the split (R-483).
- The same 12 s holds for the numbers of the main fight: a player who stays 12 s counts from when he arrived; one who
  goes sooner was never a player more (R-449, R-459; review key s1-31). A defender still on a split when the game ends
  counts though under 12 s there (R-459). Joining and leaving are read from movement, not reach alone, and a defender on a
  split player when that player dies counts however briefly (R-464; review key s1-31, s1-15).
- *As built (one reading, `Moments.linked`, `engaged_in`, `visits`; Claude's draft thresholds):* two players are in the
  same fight within 1,600; or within 2,100 having been within 1,600 in the 6 s either side; or within 2,600 with one
  hitting or casting on the other (a heal does not link them). A player counts from when he first stands 1,000 from
  someone in the fight, acts in it or stands still in reach, to when he last does; a gap of 6 s does not end it. A
  split's defenders are read the same way, without the hold.
- Defending a split is keeping it from what it came for (R-512): a player within reach of it, or one who stands in his
  pit or between the split and his pit NPCs without fighting. A split that holds defenders without dying is doing its
  job. *As built (`split_plays`, `defends`):* on his own ground, the split on his side of the hall, his walk to his own
  Lord no longer than the nearest split player's, and nearer to the split than to any group of two or more of the
  attackers' other players. Positions are read against the enemy's positions and aims, not alone (R-512).
- A monk, when monks and damage are counted, is a backline monk only; a smiter (the WoC monks) and a ritualist healer
  count as damage (R-457).

## Flags
- A team cannot capture its flag while it holds the stand: it waits for the other team to cap. A flag at the stand
  of the team that holds the stand is in hand, and that team is about a flag and a half ahead (R-482). What it does
  with it is a timing choice: get in position to overcap or keep the player in the fight; in position, cap at once
  or hold and play on with eight without giving up a boost (R-486).
- A flag picked up is not a run to answer until its carrier commits to flagging (R-488; built: it leaves the base).
- A flag brought up with the team is not a run (R-505): a team already in its base, with no fight on, walks a flag part
  of the way to its front door, sends nobody back for it, makes no serious attempt to cap and drops it at any
  resistance; it loses nothing, and the enemy has nothing to answer until the flag is capped or pushed for the stand.
  A run needs no player going back: a defender, a resurrected player or a split player on his way home, or a player
  left back for it, runs a flag, because he could be doing something else. *As built:* the carrier and all his team but
  one on their own ground at the pickup, never 12 s without his team or with the enemy's main team in his base, and
  the flag never capped or in the stand or greater stand area.
- When a team leaves to flag, the other team decides: flag again, stay, or double run (R-489).
- Each team has one flag. A pickup held about 3 s is not a run (R-339). A hold is a flag kept in hand, or left at the
  spawn, rather than run or capped: 45 s in the stand or the greater stand area while the enemy holds the stand (R-400,
  R-407).
- A double run is never two players sent to the spawn together; its three forms are in R-305. It takes a second player
  who goes back to run the next flag while the first is still capping; a runner who caps and goes back himself is a
  single run, and a player home from a split who picks up the next flag is no second runner (R-472). It is told from
  when the second player goes back: until then the first run of the pair is a single run (R-485). A hand-off and a
  double run are told apart afterwards, by what the players go on to do (R-340); in the flag grid a hand-off counts
  as a single run (R-426).
- Flag lead is a tally in which the stand counts as one flag: about half a flag from 0.35, a flag from 0.8, a flag and
  a half from 1.3, two flags from 1.7 (R-408, in his units of R-375). Flag position is never judged from who holds the
  stand (R-045). A lead is something a team keeps or gives up for something else (R-412). The runner's cost is no fixed
  figure; the data shows it (R-423).
- A flag advantage gained is 0.35 or more; going "less negative" counts (R-426). For a lone defender part-running, 0.15
  (R-430).
- The flag grid, their run against ours (R-426):

  | They | We | Our job |
  |---|---|---|
  | single | single | get the flag in, lose no more players than they do, end no worse than half a flag behind |
  | single | double | gain 0.35 or more through their next cap, and lose nobody while two are away |
  | single | stay | kill with the extra player while their runner is away |
  | double | double | as single against single |
  | double | single | kill or take ground with the extra player, and end no worse than a flag behind |
  | double | stay | kill with the two extra players before their flag is in |
  | either | a flag already in hand | answer their cap at once, or cap just before their boost (R-040) |

- Their boost 30 s away: run to deny it, or concede it for kills (R-434, item 2).
- Pushing the flagger is its own record (R-371). It counts from 4 s when the flagger reaches his team with the pushers
  still on him (R-418); a main team that walks its fight onto a flag held inside its team is a main team push onto the
  flag (R-401). The pushers' job: the flag stopped, or 30% late against the usual arrival for that hall and side; their
  own flag lead is not in the test (R-427). The flagger's side sends help or flags through it (R-034; R-434, item 8).
  Two flaggers on one another (R-528): the one who lands more on the other is the pusher (the same, the one who was
  on the other first); the flagger pushed is not counted among the players pushing, and a push left with nobody who
  landed anything on the flagger is no push (his marks, Men v hold 3:12 and HC v hdm 8:34, both No decision).
  A push on a flagger or a split (R-530; intent is not read, only what the players did): players who cross for a
  flagger already on his run (going back, at his spawn or carrying), are all on him within 20 s of crossing and leave
  the enemy's ground with him or within 20 s of the push ending are the push on the flagger and no split (Men v RACK
  0:36, 1:32; HC v Team 4:24; HC v cope 3:24). Players who stay on after the flag has gone ("a true split would
  likely stay and try to take NPCs"), or die there, are a split whose defender carries his flag (R-430; HC v cope
  0:20, 0:32, Classic).
- A part-run is not a flag run (R-535, R-536): a player back at home for a split who carries his flag some of the
  way on his own ground and puts it down, because he has to be back in his base; he always goes back to it (the
  player who hands the flag on and joins his main team has run it, R-504, R-505), and usually nobody is handed the
  flag: it is taken up by another player more than 5 s later. It is told on the split he defends (the job of
  R-430: a slight flag advantage, no pit NPC lost, not dying), it has no runner, and the enemy has nothing to answer;
  the run begins when a player who is not part-running takes the flag out. As built (`Moments._part_carries`): he
  never leaves his own ground with it; he is counted in a split's defence at some second from 12 s before the pickup
  to the end of the carry; he is without three of his team on half or more of it (a carrier in the middle of his team
  is a runner being stopped); the flag was not in his hand before the gates; nobody pushes him as a flagger meanwhile;
  and for 12 s after he puts it down he is still on his own ground (R-536).
- Shadow of Haste runs are bad examples (R-438, which corrects the premise of R-393): the mechanic was removed on 22
  October 2026. Before that date they stay in the flag lead (the state of those games) and are left out of everything
  that teaches or scores the flag decision, with the other team's answers to them; from that date a bar carrying the
  skill is an ordinary runner (R-456). *As built:* a flag play is set aside when either run in it is such a run.
- A flag run's moment (R-461): a runner setting off from inside the greater stand area goes to run when he leaves that
  area (Corrupted, Meditation, Weeping Stone, Nomad's, Frozen) or the flag stand area itself (Druid's, Jade, Solitude,
  Imperial, Warrior's, Dead, Wurms, Burning, Uncharted: R-463); from anywhere else, when he sets off. *As built, from his
  marks on TFS v 옷옷옷옷 (drafts):* a flag picked up by a player already at home, or by a team held in its base, and kept
  there over 20 s starts its run when its runner takes it out; a flag is in hand only in the stand or the greater
  stand area; the answer to a run is the flag already on its way if it goes on to be capped, else the run set off for;
  a double run needs the second runner to take the next flag within 30 s of the cap; a flag put down for good ends its
  run there, and at a hall's second flag stand (the Obelisk flag stand on Meditation, his answer) that is a cap of it.
- The opening is told as one description (R-520): where each team's players went from the gates (to the stand, out on
  a split and by which door, back at home, or waiting at the flag spawn for the next flag), who brought the first flag
  up and what became of it, and who capped first and who capped over it, with the times. *As built* (`jobs.opening`):
  read when the main teams first stand within 2,500 of one another, between 0:20 and 0:46. The first run decision is
  the row after it.
- On the page every flag run is told once (R-521): a row is a run and the run that answers it; a stay that follows is
  said in the same row; the two legs of a double run are one run.
- The opening is read (R-479): each team's first flag is a run, and a player left at the spawn for the next flag is
  part of the call. While nobody has a flag capped nobody is behind on flags: a first run, single against single,
  carries only "get the first flag in" (R-500).
- A flag handed on is one runner: a half run is a single run (R-504). A double run needs a second player who has
  gone back for the next flag by the time the first caps (R-472, R-485).
- A run is the answer to theirs when its runner turned for home before their flag went in, though the run's own
  moment falls just after their cap (R-498). A stay ends when their flag is in (R-501).
- A flag run is judged from the decision to run to its cap: what the team does after the cap is another decision, and
  its cost is not the run's (R-471). A run is not blamed for a deficit already there: the flag test is no worse than
  half a flag behind at the end, or no further behind than at the start (R-474).
- *As built from his marks on round 3 (checks in the review key, not rulings):* a result counts only the players of
  the situation (the deaths that made the numbers are its cause, not its result); a numbers difference is told once (a
  level spell or a reversal shorter than a numbers moment is no break in it); a player is in one fight at a time (a
  split player, or a defender, standing with three or more of the attackers' other players is at the main fight);
  pit archers are the archers his hall labels place in the pit; a coming boost is timed from the stand's capture,
  never from another trigger of the same moment; a double run is the pair of runs, the second flag included.
- Held in its base (pinned): a break-out meets the job only if no player and no pit NPC was lost before it (R-478).
  *As built:* held in is the main team on its own ground no further out than its doors with the enemy's main team on
  that ground; a break-out is half the living players, four at least, out past the doors where being held in ends.
- Which games count: from 1 September 2026, and never a game in which a team fields a henchman (R-476, R-477); a team
  of seven with no henchman counts. A draft number moves only on a fresh game's evidence and a GvG reason (R-480).
- A flag run's job counts only deaths at the main fight: deaths out on a split, and deaths defending an enemy
  split, are the split's own (R-466, R-443, R-499).
  Staying against a run is also met when their flag does not get in (R-468). The flag decision is told once, from the
  side that ran second (his mark, hdm v hook 7:07). A flag never carried out of its own base and pit is not a run.
- A numbers difference is a moment only where that fight is being fought (*draft:* its players start more than 0.7
  casts or attacks each in 10 s), and the kill is asked of the side up on numbers only where its damage can kill
  against the monks there (R-457; his marks, hdm v hook 4:12, 6:52).

## Splits
- A solo split is one player through the back or an unusual route at the enemy's pit or NPCs; three or four go for the
  NPCs by the back door; four is a 4-4 (R-110). A split from 0:00 is a split (R-357). A main team pushing into a base
  held by a passive defence is a main team push, not a split (R-364). An even split fight is one record while the same
  two groups stay engaged, wherever it drifts (R-365). An attempt ends when its players are back with their main team,
  dead, or 20 s on their own side of the stand (R-363), and when three or more of the rest of their team are standing
  with them on the enemy's ground: it is then a main team push (his marks on Men v Apes).
- Not a split: the last one or two of a main team that wiped, left behind (R-442); defenders chasing an enemy split out
  of their own base, who set off while it is still out and take no NPC (review key s1-20, s1-26).
- It counts from when it can do something: at the enemy's footmen, base or pit, or met by a defender (R-440). Its decision
  moment is when it crosses to the enemy's side (R-458).
- It is told once while it is defended and nobody collapses on it, with each change of its numbers beside it, and cut
  only where the kind of answer changes: nobody defending, defended, a collapse, the whole team (R-469, R-365; this
  amends the phase by phase reading of R-439 to R-449). *As built:* headed by the numbers it had for longest before
  anyone in it died.
- The attacker's job is set by the answer it meets (R-428):

  | The answer | The split's job |
  |---|---|
  | undefended | take NPCs |
  | 1 v 1, the defender not a monk | kill or take NPCs |
  | 1 v 1, defended by a monk | hold him there; the main team's job is to kill (R-114) |
  | a player or more up | kill or take NPCs |
  | even | take NPCs or kills (the split made the move, so it should seek the advantage) |
  | a player or more down | hold more defenders there than its own number and lose nobody; what the team made of the extra player is beside it (R-517) |
  | collapsed on, or a full collapse | survive it and lose nobody; what the team gained elsewhere meanwhile is beside it (R-523) |

- The defender's job (R-428): one defender, or a player down: delay and stay alive. A mirror: hold it even. One more
  than the split: kill it or drive it out. A lone defender is credited with the 1 v 1 defence whether or not his
  part-run is met (R-447); the part-run's own job is a slight flag advantage, no NPC lost, not dying (R-430, R-023).
- NPCs (R-443): the defence has to protect the pit NPCs only; for the split, footmen and outer archers count as NPCs
  taken. A split is credited only with what its own players did: a death or an NPC elsewhere on the map is not its.
- Damage against monks, from good play (R-457, with R-444, R-114 and R-120): two or more damage can kill against one
  monk, four or more against two, five or more against three; three are not expected to kill two. The job to kill at
  the main fight comes from the same ratios there, not from the monks the split brought, and goes only to a side that
  meets its ratio while the other does not; a side facing no monk there always has it (R-462, ohno v Fun 11:10).
- Timing: an answer within about 15 s is on time; 60 s is late (R-116). After kills at their base, the NPC job needs
  the time to reach the pit before their base res; otherwise the job is to be out, or set for the fight, when they res
  (R-445, R-147). *As built:* 20 s more than the walk (`AFTER_WIPE_MIN_S`, draft).
- At a base res (R-507): a team that left the base before the res has left, though it stands in front of the door
  again as the res lands; a team on its way out as the res lands has not stayed; a player left at a door on his own
  has not stayed. A team standing at a door together is in the base.
- Taken out: the race back when a split ends (R-448; it was item 6 of R-434).

## Collapse
- A collapse is its own call, apart from defending: players leave the main fight to kill the split and go back, at the
  cost of flags (R-429). The defence must become at least one more than the split; a join that makes it even is a join
  (R-441). A player who comes and stays is "add one"; come and go is a collapse (R-429). *As built:* a visit of 45 s or
  less (`COLLAPSE_VISIT_S`, draft).
- A full collapse is the whole team turning on the split. The split's job: survive and gain elsewhere. The defence's
  job: kill it or drive it out, at the cost of flags (R-428, R-429; this amends R-111, which did not count it as an
  answer to a split). It counts from the turn, a few seconds on, when a player in the game could tell the team is
  going to collapse, whether or not it reaches the split (R-508). *As built:* five or more making for the split
  (400 nearer in 4 s to where it stood), or all the team but one on it or making for it, for 4 s; told 4 s after the
  turn began; 12 s of making for it when the team does not reach it; the team arriving is the same collapse. A whole
  team found on a split with no turn read before it is still a full collapse (six or more on it, five gone home).
- Not collapsed on: a player left behind after a wipe, or one walking back and forth through a teleporter (R-442).
- hdm v 옷옷옷옷 4:06 (review key s1-26): one player coming from the main fight for 16 s, with one already defending,
  against a split of two, is a join that makes it even, not a collapse; R-441 stands over his earlier approval. *Open:*
  the engine reads one defender there: two more are within reach for 10 s each, under the 12 s.
- Whether to collapse has no fixed line (R-122); a quick collapse that does not kill fails twice (R-123). Not built:
  the snare on the defender (R-121) and the shadow with a snare (R-125; R-434, item 9).

## The Lord push
- A moment of its own from about 23:30, for both sides (R-435). The result is the match: the Lord killed first, or
  more Lord damage at 28:00 (R-142).
- The attackers are the players in the enemy's base, not only those beside the Lord (R-446). They are counted against
  the pit NPCs alive: as many, more, or fewer. The pit NPCs are the Bodyguard, two knights and two archers, and on
  Isle of Solitude the archer by the bridge in each base (R-435, R-140). Taking pit NPCs earlier means fewer players
  are needed at the end to break Entourage (R-148).
- What is read beside it: one monk or two with the push (R-146); the aim, killing the defenders and the Lord before
  28:00 or playing for Lord damage (*draft reading*); Lord damage from gvg.report's totals, as a value, not per player
  (R-435, R-141).
- The defence's job is always the same: do not die, keep the Lord alive, and keep Lord damage down (R-435).
- The engine's confidence that a situation is a decision is one band (R-492, R-515): low when a quarter's move of one
  setting makes the engine stop reading it; medium when it is still read there but its details move, or it goes at
  half or double; high otherwise. Fitted to his grades of five games (top of `tools/golden/confidence.py`).

## Similar cases and the better call (the flag family so far)
- Two cases are similar when they are in the same scenario (their single or double run, who holds the stand, a flag
  already in hand) and near one another on the flag lead, the time to the next boost, the players at the main fight
  on each side, each side's morale, the strength gap and the length of the hall's flag run (R-538, R-432, R-436).
- A build is a fixed state, never a call and never a fix, but it bears on which call is right in every family: what
  the builds can do is matched on as properties, never as labels (R-539, amending "builds stay out" in R-538; R-374).
  For the answer to their run: each team's snares, who their runner is, and with them the res clock and where each
  main team stands (R-540).
- The answer to their run is read at fixed seconds after their runner set off, 15 and 30 s, with their run still
  under way and nobody of ours sent by the read before: a runner sent by now, a double run started, or none yet;
  what followed is read 60, 90 and 180 s on (R-543, R-544). It is never read to the end of their run: a "stay" so
  read takes in every run of theirs that came to nothing (R-542). The opening is a different decision (R-541).
- One clock (R-546): the reads, the windows and the position matched on are all counted from their runner's
  set-off, the second he turned for home (R-498). The page tells a run by the hall's rule (R-461), which can be
  later; that is the play's own time, not the decision's clock.
- A team whose own runner was already out when theirs set off does not answer a run. From its cap, with their flag
  still on its way, it decides whether to run again: another decision, counted from its own cap (R-546).
- The stand at a second is its holder once a cap recorded within that second has landed (R-546).
- Who holds the stand is read at the moment; a cap about to land within seconds is said with it, as context (R-547).
- A runner has not set off for a flag while he still carries the one before: his set-off is no earlier than his cap
  or his putting it down (2026-11-19; one player capping and going back single runs twice, R-485).
- A runner who turns for home, comes back to the fight and then goes sets off when he goes for good, not at his
  first turn (R-548). *As built:* he came back when he had left (an aggro bubble or more nearer home than where he
  turned, the leaving of R-464) and then gave up more than half of that ground; a short step toward home and back
  is no leaving.
- Whoever set off first is sending and the other is answering, by however little; a pair of runs is told once,
  never from the side of the team whose runner was already gone (his mark on hold v RACK 3:58, 2026-11-20). The
  two first flags, both from the gates, are the opening's (R-520). A card whose answer is before its run stops
  the run (R-460).
- A player who waits back at his flag spawn from the gates did not set off: a card says he waited back and when
  he took the flag up (his words on Men v RACK 0:51, 2026-11-20). A team's first flag that goes in over the other
  team's is said so: they capped first.
- A team's own next flag already up the field, carried or lying where it was put down and later taken up again,
  is said on the card (his words on Men v hold 2:07, 2026-11-20). A team that sends nobody while its next flag is
  already up is deciding with a flag in hand, not staying (R-553; not yet built: with the held cards, R-554).
- Who ran first is read on the same clock: the runner who turned for home first. A run is the answer to theirs only
  when its runner turned for home no earlier than theirs did (R-546, R-498; his words on hold v RACK 11:00,
  2026-11-19: hold sending an Earth Ele and RACK responding 11 s later, not hold deciding whether to run).
- The readings are checked by the timing ladder before anything is read from the advice (R-545): a runner sent
  sooner should be better off in flags, in the engine's tally and in the replay's own caps and boosts. A report,
  never a verdict; the 45 s read is kept there only.
- The better call is the one whose hard results at 90 and 180 s, priced by how much each moves the chance of winning
  the match, come out ahead among the nearest cases of other matches (R-538, R-294). A call is read only from 30
  plays or more out of 15 matches or more; under that, and where the range includes no difference, the verdict is
  "no clear difference" (R-538; REDESIGN.md "Verdict rules").

## The numbers advantage (family 3, begun 2026-11-20)
- Scope first: numbers at the main fight from kills, a runner away, and players still on their way back. The main
  fight while a split is out belongs to the split family (R-550).
- The calls (R-551). Team up: stay and kill, push into their base for NPCs, push their flagger, run a flag for a
  backup, fall back and reset. Team down: stay and fight, fall to footmen, retreat to the pit, trade with a split.
  A fight that moves up short of their base is still stay and kill. *As built:* read 30 s in, from where the main
  team stands against where it stood and whether a runner of its own has gone.
- A res that gets off (a res signet, Death Pact Signet and the like) ends a numbers advantage from kills (R-552).
  *As built:* a dead player alive again more than 3 s off the base res.
