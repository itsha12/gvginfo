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
- The main team: in an even split, the group on the stand side, responsible for flags; monks only break a tie (R-335,
  R-355). In an uneven divide, the part of five or more (R-421).
- The same 12 s holds for the numbers of the main fight: a player who stays 12 s counts from when he arrived; one who
  goes sooner was never a player more (R-449, R-459; review key s1-31). A defender still on a split when the game ends
  counts though under 12 s there (R-459). Joining and leaving are read from movement, not reach alone, and a defender on a
  split player when that player dies counts however briefly (R-464; review key s1-31, s1-15).
- *As built (one reading, `Moments.linked`, `engaged_in`, `visits`; Claude's draft thresholds):* two players are in the
  same fight within 1,600; or within 2,100 having been within 1,600 in the 6 s either side; or within 2,600 with one
  hitting or casting on the other (a heal does not link them). A player counts from when he first stands 1,000 from
  someone in the fight, acts in it or stands still in reach, to when he last does; a gap of 6 s does not end it. A
  split's defenders are read the same way, without the hold.
- A monk, when monks and damage are counted, is a backline monk only; a smiter (the WoC monks) and a ritualist healer
  count as damage (R-457).

## Flags
- Each team has one flag. A pickup held about 3 s is not a run (R-339). A hold is a flag kept in hand, or left at the
  spawn, rather than run or capped: 45 s in the stand or the greater stand area while the enemy holds the stand (R-400,
  R-407).
- A double run is never two players sent to the spawn together; its three forms are in R-305. It takes a second player
  who goes back to run the next flag while the first is still capping; a runner who caps and goes back himself is a
  single run, and a player home from a split who picks up the next flag is no second runner (R-472). A hand-off and a
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
- A flag run is judged from the decision to run to its cap: what the team does after the cap is another decision, and
  its cost is not the run's (R-471). A run is not blamed for a deficit already there: the flag test is no worse than
  half a flag behind at the end, or no further behind than at the start (R-474).
- A flag run's job counts only deaths at the main fight: deaths out on a split are the split's own (R-466, R-443).
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
  | a player or more down | survive, and gain an advantage elsewhere on the map |
  | collapsed on, or a full collapse | survive, and gain an advantage elsewhere on the map |

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
- Taken out: the race back when a split ends (R-448; it was item 6 of R-434).

## Collapse
- A collapse is its own call, apart from defending: players leave the main fight to kill the split and go back, at the
  cost of flags (R-429). The defence must become at least one more than the split; a join that makes it even is a join
  (R-441). A player who comes and stays is "add one"; come and go is a collapse (R-429). *As built:* a visit of 45 s or
  less (`COLLAPSE_VISIT_S`, draft).
- A full collapse is the whole team turning on the split. The split's job: survive and gain elsewhere. The defence's
  job: kill it or drive it out, at the cost of flags (R-428, R-429; this amends R-111, which did not count it as an
  answer to a split). *As built:* six or more defenders on it, or five or more gone back for it. Read 507 times
  over 606 matches, which he takes as fine for now.
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
