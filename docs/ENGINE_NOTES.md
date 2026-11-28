# Engine notes: how each reading is built, and what it was tested against

Moved word for word from CLAUDE.md on 2026-11-24 (Denning's approval, PR "slim CLAUDE.md") so that it is read when a task needs it,
not at the start of every session. Nothing here was reworded or removed. CLAUDE.md keeps the rules every session needs and an
index pointing here. Read the section for a reading before changing it, and keep this file up to date as CLAUDE.md asked before.

## Working rules for the analysis engine (Denning, November 2026 review; RULINGS.md "2026-11 review")

### 1. One model family in tiers
- One model family in tiers (SPEC.md section 4): context, state, decision nodes, execution nodes, win model. Every
  fitted model answers one question and appears once. Don't add a second model for a question a node already answers;
  change the node.

### 2. Five kinds of input
- Every input is one of five kinds (context, state, decision, execution, concurrent response). Context and state are
  adjustment and never a fix. Concurrent response (what the enemy did during the window) is never an input; show it
  apart. Inputs are measured before the window or at a fixed early point in it.

### 3. Inputs capped by the data
- Inputs are capped by the data (one per 20 events); the cap and the pruning order are in SPEC.md section 5. Every
  decision and execution input carries the selection check ("marks the situation"); such inputs are never fixes.

### 4. No engine change between chunks
- No engine change between chunks. Proposals (new variables, decisions, corrections) go on the waiting list in
  `data/model/causal_map.json` and in HANDOFF.md; one bundled engine change per run of chunks, then one rebuild,
  compared against the reading just before it. A text-only change to a report section is not an engine change and
  must not invalidate prepared data (cache keys by layer).

### 5. Discovery
- Discovery offers Denning only decision and execution variables, and only after a candidate passes in two runs.
  State and build variables are never offered (they are already adjustment).

### 6. Macro and micro answers
- Answers are macro ("was it the right call": the decision tier) and micro ("what went wrong in carrying it out":
  the execution tier), kept apart, each with its evidence. Enemy response is described beside them.

### 7. Questions for Denning
- Questions for Denning come from the catalogue and cluster mechanisms (name this cluster, approve this candidate),
  not a list of Claude's ideas after each batch.

### 8. The engine on the new trim: energy, degen, flag returns (stage E, step 2)
- The engine on the new trim (stage E, step 2), on the branch. Built 2026-11-24: the reader (`extras.py`); flag returns
  (R-481); the Lord record (R-632 to R-635, described under "The Lord push and Lord damage"); degen as damage, the
  reading and the first figures that take it in (below). To build, in this order: the rest of the damage figures of
  R-649 (the death accounts, the nodes and the older layers), interrupt attempts (R-639), what each prot did and the
  death and spike-save recaps (R-636), who stripped which enchantment from our own replays (R-637), a hold told with
  what the holders went for (R-658); and energy, which he has settled (R-664 to R-689) and which is built beside these in the order of R-689 (below).
  Energy is one reading, `Match.energy()` (`energy.py`: read its top before using energy anywhere). gvg.report's
  estimate, the least and the most energy a player can have every two seconds, carried as `lo`, `hi` and `mid`; `ok`
  False and every figure blank where a match has none (18 counted matches, R-672). Whose: the backline monks
  (`kind` "monk"), the midline for energy (Ritualist, Mesmer, Elementalist, Necromancer, smite monk: "midline"),
  nobody else (R-665, R-670, R-675). The scale is what a player would have on his double high set now (R-668,
  R-686): shown + what the change of set would add. For everybody but an Elementalist that is the double high top
  less the maximum of the set held, the top 72 + 20 x morale / 100: death penalty and morale move a maximum by their
  share of the BASE 20 energy only (+2 at a full boost, -3 a death, -12 at 60%), the game's rule and what
  gvg.report's maximum does, so what a change of set adds never moves with morale. An Elementalist's maximum holds
  his Energy Storage and falls with Overcast, so his is read from the set he holds (the replay's weapon set of each
  sample, gvg.report's labels; `SET_HOLDS`: wand and focus 42, staff 40, single high 62, double high 72, anything
  else 30). Found in the review of 2026-11-24 and not to be undone: the top had been 72 x (1 + morale / 100), which
  read a monk on a boost 5 too high and one with death penalty 6 to 30 too low (43% of readings, against the team
  with deaths behind it), and an Elementalist's top had been his highest maximum in the match, which counted his
  Overcast as energy. A reading is the sample at or before its second, never the one after. `at(a, t)`, `group(ids, t)` (the average, the lowest player and how
  many, R-683), `out` (a monk under 20, a midline player under 15, R-681 and R-682: "yes" where even the most he can
  have is under it, "maybe" where only the least is). Those two lines are for the excuse only: at a decision no
  line is set and what followed is read across the range of energy there (R-669). `python3 energy.py cover` prints
  the checks of the record (2026-11-24, 546 matches, on the corrected scale: a team's monks lose 0.8 in 10 s under
  fire and regain 1.2 at rest; a death follows within 20 s 89% of the time where they average under 20 and 8% at 60
  or more; a monk is out for certain 0.5% of his time alive, a midline player 0.1%). Built (2): each fight's energy on every play, a record kept beside the plays
  (`energy.record`, `flag_cost[rid].energy`: no play reads it and none moves): at the second the decision arises
  (`energy.decision_second`: a flag play's `clock.anchor`, a base res 20 s before the res, else `t0`) and 60 s
  before, the backline monks and the midline of our side (a split play's own players, `who`; on every other play our
  main team, since a flag, boost or push play names its runners or pushers) and of theirs (enemy players `linked` to
  ours in the 4 s to it, else their main team, `their_from`), each as `group`, with `team` (every living backline
  monk of each team: what the answer to their split reads, the defenders being the call itself); the split ticks
  and base res spots carry the same. `cases.py energy <plays file>` (report `data/model/energy_cases.json`): for
  each decision of R-688 with a reader (their run, run again from our cap, their boost, down and up at the main
  fight, the answer to their split, our split, the danger zone base res, after a wipe) what followed each call by
  the fight's monk energy (average and lowest monk in thirds of that decision's own cases, R-669; how many monks
  apart), the minute before beside every row, and the danger zone read both ways (damage line and monk energy).
  Not read, at his word: pressing the fight or allowing a stand-off (no decision for now, R-691) and offensive or
  defensive play, which is execution (R-692). The danger zone says the monks' energy of the players in their base
  beside the 300 line, never in its place (R-690: `monk_energy` on `danger.calls`, in the sentence). Taken out at his word: our own monks at "our flag
  just in" (R-693), energy at their boost (R-694), and the send-or-not table of our split (R-695). A split already out staying to kill or falling back is
  `jobs.split_holds` (R-696; kept beside the plays as `flag_cost[rid].split_holds`, no play reads it): each stretch
  of a split's own plays that opens with defenders, a collapse or the whole team, the call 20 s on ("died there" where
  half or more died, else "fell back" where half or more of the living are off the enemy's ground by `_deep`, else
  "stayed"; the halves are Claude's), the position and what followed; `cases.py energy` reads it as decision 8 by the
  split's own monks (its energy is the play's own record). Energy is among what like spots are matched on (`cases._e_mean`, the average, R-683: it told a little more
  than the lowest monk at most decisions): their monks' energy in MORE for every flag play (the answer to their run and
  our flag just in, R-693), both teams' at the numbers and main fight like spots, our team's (`team`) in SPLIT_VARS,
  both teams' in DANGER_VARS; none at their boost (R-694); a match with no energy takes the scenario's middle. (2) is
  done. (3), the excuse, is built (2026-11-24; R-666 the second aspect, R-681, R-682, R-685, R-692), all of it in
  `energy.py` (read the section "the excuse" there before touching it). `denial(m)`: every time an enemy skill took
  energy from a player, with how much and how surely: Energy Surge and Energy Burn from their damage on the target
  over 7 and 9 (exact where a whole multiple, a lower bound where a prot cut it, nothing where no damage is seen: a
  player with no energy on the set he holds loses none); Mind Wrack 1 for every non-hex Mesmer skill its caster
  finishes on the hexed player; Power Leak, Shame and Guilt the skill's figure at the caster's Domination Magic and
  no more than the most the player can have (not sure); Malaise 1 every 3 s. `Energy.account(a, t0, t1)`: what he
  had, the listed cost of every cast he started (R-680: finished, interrupted or cancelled), what was taken, and what
  came back (the balance: regeneration, energy skills, a cost cut by a skill, and the error of the estimate; never
  call it regeneration). `excuse(M, plays)`, kept beside the plays as `flag_cost[rid].excuse` (no play reads it and
  none moves): at every death the backline monks in the dead player's fight a second before (`Moments.linked`), who
  was out and each one's account of the minute before; and for every play with the job to kill (`kill_job`: the test
  "more of theirs die"), met or not, the midline of the team in that fight, how long each was out, and his account.
  `energy.py <report id> excuse [m:ss]` says a match's in sentences (`say_death`, `say_no_kill`); the death accounts
  carry it as the answer "energy" (`forensics.death`); `execution.py` reads whom a team drains as two measures,
  `drain` and `drain_on_monks` (execution, R-692). `cases.py excuse <plays file>` (report
  `data/model/excuse_cases.json`): over 546 matches 7,432 deaths with a monk in the fight, every monk out at 1.1%
  and one or more at 5.0%; a monk out at a death spent 88 in the minute before and had 3.5 taken (4% had 20 or more
  taken, 76% under 5: a monk out is mostly a monk who spent it); about 440 energy a match is taken in all, 38% of
  it from backline monks; of 2,393 failures to kill, a midline player was out for half the stretch in 0.1%. An excuse says what was so, never why a player died, and is no fix. (4), monk
  casting efficiency, is built (2026-11-24, `casting.py`): section 43. With it energy is built in his order
  (R-689); who is a backline monk in all of it is `common.monk_kind` (R-698, section 42).
  Degen as damage (R-638, R-649, R-655, R-661) is one reading, `Match.degen()` (`degen.py`: read its top before
  touching a damage figure). The amounts are gvg.report's totals for the match (what each player took from each
  source, net of regen; what each player's degen did to each NPC and Lord); only the timing is ours: a total is laid
  evenly over the seconds the replay shows that condition or hex on that target, and for an NPC or a Lord over the
  stretches its caster, else his team, was hitting it. `rows[target]` is [(second, amount, source, kind)]; `taken`
  and `dealt` sum it; `account` says what became of every point (R-460), `python3 degen.py cover` over every stored
  match (run it after a fetch). Four things to hold to. A weapon's own upkeep (gvg.report's "Vampiric Weapon", 11%
  of all degen it records) is no damage and is left out. Degen gvg.report credits to nobody (its "Observed
  Burning", conditions drawn or passed on, its remainders: 12% of what players took) is in what a player or a team
  took and in no figure of what a player dealt. The Miasma of Isle of Meditation (577 thousand health in the stored
  matches) is ignored at his word: in the account, in no damage figure, never read from where a player stands
  (R-677, which confirms the two readings before it too). And degen never says who is where: who is in which fight, who is hitting a player or an
  NPC, a stand-off, a spike and who killed a player stay read from hits and casts (R-655). Against gvg.report's own
  recaps (the degen in the window before 285 deaths and saves) the timing agrees at a correlation of 0.6: good for a
  minute's damage, rough for the few seconds before a death, where the recap itself is the figure to read (R-636).
  What takes it in so far: the damage a player took (`jobs._dmg_on`, rows marked degen): a base res carries
  `taken_all` (hits and degen, the figure the danger spot is asked of at 300, R-676), `taken` (the hits in it),
  `taken_degen`, and `npc_dmg_all` beside `npc_dmg`; NPC damage by kind of bar (`npcpower.py`, its benchmark
  rebuilt: a ranger adds 10.5 a second on footmen against 4.4 on hits alone, and the damage to kill a knight is 657
  against 561); the execution measures (`execution.py`: damage on their players, the shares on their monks and on
  one player, damage on their NPCs, and `degen` itself in health; the damage against the roles' usual is still hits
  against a usual of hits, until `eventlayer.py` takes degen in); and `pressure.py`, whose degen intervals are
  gvg.report's amounts now (pip-seconds as landed), so the death accounts, the nodes and `lnrows` read them without
  a change (their benchmarks are of the old figure until the rebuild). Not yet: `forensics.py`, `events.py`, `nodes.py`,
  `eventlayer.py`, `fights.py`, `scoreboard.py`, `phases.py` and `episodes.py` wherever they sum damage from hits;
  the story and the reports. The aim of a Lord push counts hits, not amounts, and stays as it is; Lord damage is
  gvg.report's Lord record (R-632), and the degen on a Lord kept in `degen.py` is read by nothing.
  Flag returns as built: `Moments.flag_backs` reads every time a team's flag came back to its spawn from gvg.report's
  flag objects (an object on the spawn spot within `RETURN_CAP_S` of that team's capture is the capture, any other a
  return), and `flag_lives` is built on it: a pickup is the next flag only when the flag had gone back; any other
  pickup takes the same flag up from where it lay, however near the spawn (the inference from the next pickup read
  a return that never happened about one time in seven, and read real ones a median 6 s and up to 7 minutes late).
  A life that ends returned ends the second it went back, so the flag tally (R-408) no longer counts a returned flag
  as lying on the ground until the next pickup (Crew v cope 5:47 to 9:23: Crew read level, a flag down in truth).
  Who returned it is the living enemy player nearest where the object lay that second (`returned`; None where nobody
  stands within `RETURN_R`). A capture the observer recorded on no carry of the life (the capper took it up again
  unseen, or the capture was named on the player taking the next flag) ends the life captured (`cap_unseen`), and a
  flag put on the hall's other flag stand (the Obelisk flag stand, Isle of Meditation) goes back at once with nobody
  near (`other_stand`). Every run prints the count of each ending (`Moments.flag_ends`). With true lives one reading
  had to follow, `Moments.not_run_first` (R-505 on the carries before a put-down: a flag brought up with the team, put
  down and taken up again later is no run until that carry; 옷옷옷옷 v RACK 0:00 and 3:03, Classic, where the inferred
  return had made two lives of one flag): it is asked by `_flag_rows`, the opening, the other side's row, the moments
  and the runners. Change it against those rows and hold v Men 0:00 (Classic: a flag put down as the gates open was
  not brought anywhere), never by a count of seconds. Left: a flag lying on the field is told from its take-up, not
  from when its taker set off for it (옷옷옷옷 v RACK 6:15, Visible, now told at 6:27).
  `tools/golden/compare.py <before> <after> [--skip key,key]` compares the plays of two runs (what "compare the plays
  with the run before" means everywhere in this file). A full run needs the machine to itself: a second run beside
  it gets a worker killed for memory and the run then hangs without a word.

### 9. Checking the reading after every change
- Check the reading after every change (R-453), on the branch: `moments.py all <file> --dev` (the development
  set, `data/model/dev_set.json`, about six minutes on two cores) then `tools/golden/review.py score <file> --key <main>/data/model/review_key.json`
  (the review key: every row Denning has marked, his words, and the checks read from them). Only a row he graded
  Classic is binding (R-494): a failing Classic row is fixed before anything else. Everything else is a report which
  Claude reads and tells him of only where it matters: the rows marked before 2026-11-15 (history, R-491), the Visible,
  Weak and No decision rows, the gate (`golden.py gate`) and the line-up (`lineup.py score`). Run every match
  (`moments.py all <file>`, about 10 minutes) only at a checkpoint: a benchmark rebuild, or counts a question needs. A
  full run applies the engine; it teaches it nothing.

### 10. The fresh start of 2026-11-15 and his grades
- A fresh start from 2026-11-15 (R-491 to R-497). The engine of that day is the starting point (`bundle-4` at fd2b30b, kept as
  the branch `baseline-2026-11-15`; its reading and figures in `data/model/baseline/`), and the engine does not have to fit the
  rows marked before. His grades on a fresh game say what each row is for: Classic, the engine must identify it and
  read it exactly as he does, and one such row is enough to build from; Visible, a rate to watch; Weak, the engine
  should trend towards not identifying it (it teaches the confidence to read low); No decision, it should stop being
  identified. For Visible, Weak and No decision a fault is built from only when it shows in two games or is plainly a
  bug (R-495). There is no pass mark (R-496): show him the marks after each game, and he says when the system is ready
  for bulk training. The engine checks itself (`jobs.selfcheck`: a player counted in two fights at once) and tells a
  situation with no clear decision as context, with no call (R-488).

### 11. Which part of a divided team is the main team
- Which part of a divided team is its main team is read in one place, `Moments.main_team` on the branch. His guide of
  2026-11-17 is built there (`HOME_GUIDE`): a split is almost never in its own base, and a small group at home with
  its main team elsewhere is most likely a defence. It is a guide, not a ruling, and not to be applied strictly: it
  gives way to his marks, to an even divide (R-335) and to a held base (R-506), and it is never cited as a ruling.

### 12. A player counts in one fight only; numbers flickers
- A player counts in one fight only (R-519): where the main fight and a split's fight stand within reach of one
  another, `Moments._numbers` gives each player both readings count to one of them (by whom he trades with, then whom
  he heals, then whom he stands with, then where he is moving), and `split_plays` asks through `fight_side`. Change it
  there, never in one reading alone; `M._side_log` says who was given to which fight and on what; the self-check
  (`jobs.selfcheck`) should stay near nothing. Who the question arises for (`Moments._split_candidates`) is read until it
  settles: the splits silent, then again with the sides given, twice at most, whoever they count then being a candidate
  too (TFS v DMG 22:10 to 23:10: the last player of a split whose others were given to the main fight was told as a lone
  split with eight defenders while the main fight counted them all). And a defence has a split to defend: a defender
  given to the split's fight where every enemy player on that split is given to the main fight is in the main fight
  too. Over every match the self-check went from 20 in 6 matches to 6 in 4, with rows moved in 17. A split a player or more down meets its job by losing nobody (R-517).
  A player away from his fight for less than JOIN_S has not left it (R-579, the mirror of R-350), read in `_numbers` (`M._stayed`:
  counted in the fight before and after, alive, carrying no flag, on no split's fight, the missed readings spanning JOIN_S or
  less) and only to close a difference: where the fight is level with those players counted, nobody is up. It never lengthens
  one: keeping them in the count joined rows through the flicker of Jade's portal (Men v Crew 24:34, Classic) and was taken out.
  The other half is R-583 (his "(a) No. It is level"; Men v Crew 20:10, Men v hook 2:20, Book v Crew 5:08), read in `_numbers`
  too (`level`, `M._level`): a stretch of JOIN_S or less every reading of which is level once the living players are counted who
  were counted in that fight within JOIN_S before it began or are within JOIN_S after it ends (no flag in hand, given to no
  split's fight) is a player coming or going, and a situation with no other moment in it is not told. It is read on the whole
  stretch and the whole situation and moves no other row: do not turn it into "no moment in its own right" (tried: it cut the
  lead-in or tail of twelve situations, Men v RACK 18:04, Visible and correct, among them). A kill is as before (R-552).
  And any numbers difference of JOIN_S or less that comes from players being elsewhere is not told (R-585, his answer;
  `jobs.numbers_plays`: the sources "split elsewhere" and "on the way"; a runner away is the flag decision's, R-431).

### 13. When a split ends and what kills it
- When a split ends and what kills it (2026-11-20, `split_plays` on the branch). The rest of a split's team is read at
  the second, not from the record (R-439): a player who went home from it is of the rest when the main team comes to
  the split (R-487). A player left on the enemy's ground by the others of his split who neither hits NPCs nor trades
  damage while alone is not splitting on (R-381 asked of the moment); a lone player on his way in is read from the
  crossing as before. The seconds in which a split that had not been outnumbered is killed by players come from their
  main team's fight are a collapse however short (`killed_end`): who hit him in the 6 s before he died counts on him,
  unless he came by the base res (Team v BcS 18:11) or `fight_side` gives him to the main fight; a death after a turn
  belongs to that collapse alone. Tried the same day and taken out, not to be built again without his word: players
  read as the head of their main team's push when the team comes together round them within a minute (fails Men v
  hold 10:40, Classic); players who stay where their main team's push stood (Men v Apes 7:10 reads against it); a
  split ended when all the team but two stand in one group with it (340 rows moved on the development set for one
  fault, TFS v DMG 22:44, where the self-check still counts twelve).

### 14. When a split starts
- When a split starts (R-562, `split_plays` on the branch): when its players are committed, and the enemy can know they
  are going for nothing else. A player who was not defending is read as before (from the crossing, or 4 s after he
  leaves when he goes straight across; from his own doors out of a held base). Players who had come to the defence of
  an enemy split before they joined the record (`was_defending`, from the answer of that split's record) are a defence
  turning into a split: while they are half or more of those on the enemy's ground nobody is on the split until one of
  its players has no way off to mid left ahead (`Hall.past_turnoff`: the walk to the stand along the rest of his way
  to the enemy's nearest door has no low point still to come; on a back path without one he is past it at once), and
  it then takes the door it comes to. It is told too from when enemy players have been on it for JOIN_S on the
  enemy's ground (`fought`: a split fight of its own, R-365; without it 4 v 4 fights on a back path were told nowhere; his word on it, R-563: leave it as built).
  He does not want this made more specific: change it against Men v hold 10:24 (No decision) and 10:40 (Classic), and
  bring him what it gets wrong rather than adding a test. A split ends, and the main team's push begins, when the rest
  come to the same fight by whichever door (R-560); players left at the enemy's door when the larger part forms
  elsewhere are a split (R-561): both are what was already built, and the first two readings "tried and taken out"
  above stay out.

### 15. How flags are told on the page
- How flags are told on the page (R-520, R-521): the opening is one row, `jobs.opening` (who went where from the
  gates, who brought the first flag up, who capped first and who capped over it), with each team's first-flag job
  under it and nothing else (R-565: a team that runs no first flag has no stay play at the opening); after it every run is told once, a run and the run that answers it in one row (`review.py flag_rows`,
  from `run_id`, `answer_id` and `said` on the flag plays). The flag plays themselves, their jobs and their tests
  are as before: change what a row says in `flag_rows`, and what a play is in `flag_plays`.

### 16. A push on a flagger
- A push on a flagger is one reading, `Moments.flag_pushes` on the branch: two flaggers on one another are one push,
  the one who lands more on the other the pusher, and the flagger pushed is never counted among the players pushing
  (`M._fpush_answers` keeps what was set aside). Who pushes is R-573, his four points, read there and nowhere else: a
  player who hits or casts on the flagger and is on him (inside an aggro bubble of him for PUSHFLAG_S, or having left
  his own main team for him, or from range landing more on him than on the rest of his team; the caster at range is
  the push only when nobody is nearer); a player who travels with those players (goes with the flagger inside the
  bubble trading with nobody else, or has left his main team and comes to the flagger with them); never a player of
  the main team who stands off him or trades with his helpers, nor a monk healing the pushers across from the main
  fight; and the whole main team when it moves onto him (a push begun on him on his own goes on while their main team
  stands on him on his own ground; a holder who stands in his team when the fight is walked onto him stays R-401's
  push onto the flag). A carrier whose flag has stood in hand at the stand for HOLD_S has arrived and is not pushed.
  Change it against HC v Team 1:30, 5:26 and 8:18, Men v RACK 1:08 and hold v RACK 12:42 (Classic), never by a new
  exception; a runner who has just capped is the flagger only from when he is on his way home (R-577). On Isle of
  Jade, Warrior's Isle, Weeping Stone, Meditation, Wurms and Solitude a team at the footmen is not in the base for the
  base res (R-574, R-578: `base_res` in `hall_features.json`, read by `Moments.caught`).
  Players walking through a portal are of the main fight on either side (R-575): `Moments._reach`, asked by `_near`
  and `linked`, takes the two ends of a teleporter that works both ways (the hall's `teleporters.two_way`: Jade,
  Nomad's) as one step apart; change who is in which fight there. A numbers stretch every second of which lies in a
  stand-off (R-405, `standoff_at`) is no numbers advantage and is not told (`jobs.numbers_plays`; Men v Crew 14:24). A split's door is read phase by phase in `split_plays` (only a phase
  whose players all start it in the field takes a new door), and a split out of a base its team is held in is told
  from when its player goes out past his doors (`out_at`). The first is R-528; the other two are from his marks.
  A split record whose players all came for a flagger already on his run and left when the flag had gone is the push
  on the flagger and no split (R-530): one test, `jobs._push_not_split`, asked by `push_plays` and by `split_plays`.

### 17. A part-run
- A part-run is not a flag run (R-535, R-536): a player back at home for a split who carries his flag some of the
  way on his own ground, puts it down and goes back to his base (always: it is what tells it from a run or a hand-off;
  the player who hands it on and joins his main team has run it). One reading, `Moments._part_carries` on the branch (built by `run_starts`, asked through
  `part_run_at`): such a carry is not under way and has not travelled, so `flag_rows`, the runners of a call, the
  boost and the moments all leave it out, and `split_plays` tells it on the split he defends. It is read from the
  split's own candidates (`_split_candidates`), so it is silent while those are being taken. Six forms were built on
  2026-11-18 before this one held his eleven rulings and every Classic row: change it against the set p2 rows and the
  HC v cope and hold v Men rows of the key, never by a new exception.

### 18. A flag handed on; a flag left lying
- A flag handed on is the same run (R-580), one reading, `Moments.handed_on` on the branch (asked by `run_starts` for the
  chain of a flag's carries and by `_held_carries`): put down and taken up by a team mate within HANDOFF_GAP_S, or, however
  long it takes, while the team mate who takes it stands by it (FIGHT_CLOSE from where it lies, every second from the
  put-down to the take-up). Any other flag taken up again is a run from where it is taken up, as before. Change it against
  Men v Crew 4:53 and 12:26 (one run, the Ranger handing it to the AoB Derv), Men v NwAy 8:19 (Classic: the Hammer who walks
  31 s to a flag left at his door runs it) and Men v hold 6:18 and hold v RACK 16:43 (Classic: the carrier who takes his own
  flag up again runs it from there), never by a count of seconds; three wider forms failed those rows on 2026-11-22 (a player
  coming straight for it, the carrier himself, a taker never away for JOIN_S).
  A player sent for a flag left on the field is a flag decision (R-581). A later flag left lying was already told from where
  it is taken up. A first flag is left when it has lain longer than FLAG_LEFT_S, two minutes (R-586, his length), read in
  `jobs._flag_rows` (`left`, `left_at` on the row) and, for a flag held before the gates that nobody carried for as long,
  in `run_starts` (`left_spawn`): the opening says what was brought up and put down, or that no flag was brought up, and
  the take-up is a run of its own, said as "sent for the flag left lying since ...", with no "The opening." before it
  (HC v hdm 5:56, 옷옷옷옷 v cope 4:55, 옷옷옷옷 v hdm 3:15). It is read from where the flag was first left that long, though it
  was put down again later for less (cope v Team: left 0:11 to 2:58, capped 3:16), and whether it is capped in the end or
  not. A first flag put down for less and then capped stays the opening's run (옷옷옷옷 v RACK 0:21, Classic; Men v Crew 0:22
  to 1:23, his "Men holds for 1:47ish before deciding to cap"), and the opening names every player who carried it in the
  match, in the order they first carried it (R-587: "brought up by Mes/A, handed to 8 Monk"; who held it before the gates
  or put it down as they opened is not one). Do not test where the flag lay or who stood by it (the taker by it, and any
  team mate by it, each fail a row he has marked). Not built: a flag whose first pickup is not at its spawn in the replay
  has no run record at all (Book v OG 7:16 and 10:56). A first flag neither capped nor returned is said as "put down at
  ..." in the opening's row, and the two first flags are "neither before the other" only when both set off by OPEN_BY_S
  (`gates` in `flag_plays`). Seen and left: a first flag put down for less than two minutes and never capped is still
  told from where it is taken up, under "The opening." and named for the player who took it up (One v Crew 6:37; read as
  one opening run it stood "under way" for five minutes in cope v Team and took the other team's runs as its answers:
  tried and taken out); and where a player goes back for the next flag before the player sent for a left flag has taken
  it up, the double run names its two runners the wrong way round (cope v Team 2:43).

### 19. A flag held at home
- A flag held at home is no flag run (R-576), one reading, `Moments._held_carries` on the branch (built by `run_starts`
  beside the part-carries, asked through `held_at`): a carry in which the flag does not leave its own ground (nor by a
  hand-off within HANDOFF_GAP_S) while his team, all but one at most, is on that ground with him and MAIN_BIG or more
  of the enemy are in his base. Such a carry is not under way and has not travelled, sends no runner (`_runners`,
  `_runner_runs`) and is no flag on its way at a boost. Change it against cope v hold 14:09, Men v hold 7:46 and 8:12
  and Men v Crew 18:21 (no run), and HC v cope 2:53, Men v Crew 5:05 and 19:31 (Classic: runs), never by a new
  exception.

### 20. When the match is over
- The match is over at `Moments.over`: the second the losing team is recorded dying all at once, some 12 s before the
  replay stops. Those deaths are taken out of the deaths the reading counts, and no play starts from that second on.

### 21. The known truths
- The known truths (R-533), on the branch: `tools/golden/truths.py <plays file from moments.py all>` at every checkpoint
  (a run over every match; the development set is too small for most). A short list of things any player knows (an
  undefended split takes more NPCs than a defended one; answering a run with a run is better in flags than staying),
  each a comparison of two groups of plays with a 90% range over whole matches: HOLDS, FAILS (the run exits 1), NOT
  CLEAR, TOO FEW. A truth that does not hold is looked into the same session and what was found is written in `NOTES`
  there; it is a reason to look, never proof. The truths are tests only and feed nothing in the engine. Only his
  truths and those he has approved can fail a run; Claude's proposals are reported apart. Compare calls on the fixed
  90 and 180 s record (`after` on a moment), never on a play's own end: a stay row ends at their cap, a run row at ours.

### 22. The similar cases and the flag family (cards, ladder, advice test)
- The similar cases (R-538), on the branch: `cases.py test <plays file from moments.py all>` at a checkpoint (about two
  minutes; a report module, in no cache key; the report is kept in `data/model/flag_cases.json`). Three parts: the price
  of a result (a small model of a position fitted on every moment, mirrored, held out by `cache.fold_of`: strength gap,
  flag lead, death penalty, morale boost, pit NPCs, Lord health; a stand-in for the win model until stage E; footmen are
  not priced, their price runs backwards, and each run prints that check), the nearest cases (the same scenario, then
  the variables of R-538 in standard units, equal weight, and for the answer to their run also the res clock, each main
  team's place, their runner, each team's snares, how long their flag should take and whether the flag can beat the
  boost, R-539, R-540 and R-544: a build comes in as properties, never as a label; K chosen by the data; the floor of 30
  plays and 15 matches), and the held-out advice test (the boost read with and without the flag only held at home). The
  answer to their run is read at fixed seconds, 15 and 30 s after their runner set off, and judged 60, 90 and 180 s on
  (R-543, R-544), never to the end of their run, which takes in every run of theirs that came to nothing (R-542); his
  given is printed as a check (its half on flags is T12). Dropped at his word, not to be brought back without it:
  measured weights, the short list of six variables, the 45 s read (kept in the ladder only, R-545), the 120 s window.
  One clock (R-546): reads, windows (`after`) and position (`state`) of a flag play are counted from `clock.anchor`,
  their runner's set-off; the play's own `t0` stays the second the page tells the run (R-461). Where our runner was
  already out when theirs set off (`clock.from_cap`) the decision is another one, run again or not, counted from our
  cap, with scenarios of its own: never fold it back into the answer to a run. A runner sets off when he goes for
  good (R-548; `run_starts`, `for_good`: he came back when he had left, an aggro bubble or more nearer home, and gave
  up more than half that ground; a short step toward home and back is no leaving: test any change against HC v Team
  11:18, Classic, and hold v RACK 10:52). Whoever set off first is sending, by however little (`first` in
  `flag_plays`; the two first flags are the opening's): a pair of runs is told once, and a play or card whose answer
  is before its run stops the run (R-460). A flag play also carries what a card says beside the run: their runner
  waited back at his spawn from the gates (`clock.their_waited_back`, `their_pick`; the run record itself is left as
  graded), our first flag capped over theirs (`clock.cap_over`), and our own flag already up the field
  (`our_flag_up`, `Moments.flag_up`, read from the flag's life, carried or lying; the play stays what he graded). `Moments._state` reads the stand with
  the cap of its own second (caps are kept to the tenth of a second; `st.stand_owner` on a whole second misses one
  recorded within it, and the other readers of it are not yet changed: for the clean-up, R-398).
  The timing ladder (R-545): `cases.py ladder <plays file>` at every checkpoint, before the advice is read (a report,
  kept in `data/model/flag_ladder.json`; it can fail no run). It checks the readings themselves: is a runner sent
  sooner better off in flags, in the engine's tally and, apart, in the replay's own caps and boosts (the tally counts
  a flag on its way, so it rises with a runner by its own making); are the windows on the one clock; is the stand
  read right; is the tally flag advantage (whose boost lands next). Its raw record is `track` on every flag play. What
  followed an answer is put to him as section 8 of `cases.py test`, "as it fell" (by how soon our runner set off, and
  for no runner by whether their flag got in, with the chance of winning each row started from): the form he reads;
  never the test's counts alone, and never a mean over "no runner" without that split (2026-11-19: +1.1 was -4.4
  where their flag got in and +7.0 where it did not, teams already at 76%). The nearest cases are set level with the
  case read (`Scenario.level`; the chance of winning is matched on), and each scenario prints `level_check`: the two
  answers in the 60 s before the decision (`before` on the flag plays). Not level there means the answer marks the
  situation (SPEC 5, rule 4): say so and give no advice from it. The flag family goes through his four stages
  (2026-11-19): the readings (the ladder), the general table (section 8), the other factors (section 9, `factors`:
  what holding off is worth by what a team can see, where to look and never advice), and the sentence for one moment
  (`cases.py cards <plays file> [f1 | <report id>]`: the spot, the answer, what followed, what similar spots got; a
  verdict only where like cases stand round the case). Each later family takes the same stages. Settle the
  technical choices yourself; bring him GvG questions only. He marks the sentences on the site, Model > Game review,
  the view "Flag advice" (`assets/js/pages/review.js`; rows `data/model/flag_cards.json` on main, written by
  `cases.py cards <plays file> f1 --site <main>/data/model/flag_cards.json`; a card's id is its play's id): for each
  card whether what happened is told correctly, whether the reading makes sense to him, and what he would have done.
  His marks are in `data/model/flag_card_marks.json` (only what he marked, with the text he saw): read them the same
  session, set them out for him, and never write the cards again over a game he has marked without saying so. When
  they are written again, `--site` keeps each card's id (`play` is its play now), never touches his marks file, and
  marks a card `changed` only where it says something else than the card he marked (what happened told differently,
  or another reading at the first look; figures that only moved with the fit do not count): the page asks for those
  again with his earlier marks beside them (kept under `was`), and lists marked cards no longer written (`gone`).
  Tell him how many wait. His own call is send (at once), wait (look for a kill first, then send; R-549), hold,
  nodiff, unknown. The cards he corrected are set c1 of the review key, each with a check on the play it is written
  from (a dotted name such as `clock.cap_over` reads inside a play). The report also says what the
  advice was (section 5: the spots where it says hold off or send, with moments to look at; show him this whenever
  a test result is put to him, never the counts alone), what a team that holds off goes on to do (6), and the run in
  answer by who was sent and their snares (7: as it fell, where to look, never who to send). Every flag and boost play
  carries `state` and `after`, the position and the fixed 90 and 180 s record at the second the decision arises: judge
  calls from those, never from a play's own end. `cases.py case <plays file> <report id> <m:ss>` prints one decision
  with its nearest cases and their replay links. A verdict is a reading, not advice, until the held-out test shows a
  gain for its scenario: say so whenever one is shown to him.

### 23. The split family and the main fight while a split is out
- The split family (R-558; the split plays are ready, R-564), the answer to a split, on the branch. Every split play carries `split`, the record of its
  split on the clock of the second it is told (R-562): when it left, crossed, could first do something and was first defended; at `SPLIT_TRACK_S` from
  the telling its numbers (players on the enemy's ground, defenders, defending monks, its own monks) and what its players can do (`props`); every
  stretch it is told in with the kind of answer; each side's dead and each main team's place when it is told; its own deaths, its defenders', the
  NPCs it took and its damage to the Lord, by the second. The plays of its first told stretch carry `at_told`: the position each team chose from, the
  60, 90 and 180 s record and the 60 s before. It is not named `state`, which the prices are fitted on: a new family must not move the prices the flag
  readings were shown on. None of it changes a play. `cases.py splits <plays file>` (report `data/model/split_cases.json`): the clock of a split; the
  readings S1 to S7 (what any player knows); what followed each answer by the size of the split, as it fell; how the answer moves between the reads;
  and like spots (section E: matched on `SPLIT_VARS`, R-566 and R-568; each answer against the commonest at the same spot, then the test on unseen
  matches with the same test on the 60 s before; section F, `split_factors`: what matching the split or more is worth against fewer, by what the
  defending team can see, R-568: where to look, never advice). The answer is the first answer, read 20 s after the split is told and again at 40 s
  (R-567), in the names of R-566 with "no answer" told apart (R-569: a defender on his way, there within 20 s more, and nobody coming; told from what
  the defending team did alone) (`SPLIT_ANSWERS`). No row of the report is advice until the held-out test shows a gain for that size of split: say so whenever it is
  shown to him. The range of an answer's worth at a spot is the range at one spot: never narrow it by drawing matches again over spots, which share
  their nearest cases. Never ask for `_flag_rows` or `run_starts` from inside `split_plays`: it is entered while `run_starts` is being built (the part-carries),
  and the half-built runs are kept (2026-11-21: 30 flag plays moved; `runner_out` is put on the record in `plays`). After any change to the record
  compare the development set's plays with the run before, the keys `split` and `at_told` left out: nothing may differ. The split's damage against NPCs is not measured (`Moments._props`); players who res at the base onto a split are read as
  a collapse (to separate before the base res is judged against collapses). The other half, the main fight while a split is out (R-570): every numbers play carries `track.splits`, at each second of
  `NUMBERS_TRACK_S` [players on a split of ours, their defenders on it, players on a split of theirs, our defenders on it], from `M._split_at`
  (`jobs._numbers_at`; no play changes). `cases.py main-fight <plays file>` (report `data/model/main_fight_cases.json`) reads the numbers rows "from
  a split elsewhere" in four scenarios (up or down at the main fight; their split in our base or ours out; a split of each team out at once and
  rows with no told split on the ground are set aside): the readings M1 to M6, the trade (the side up at the main fight against the side down, with
  the same comparison on the 60 s before), what followed each call as it fell, like spots and the test on unseen matches. The call is read 20 s in
  (`_main_call`): a change to a split already there first (collapse on it, a defender pulled back, more sent, players brought back; a player who died
  there is no call, R-571), else his calls of R-551 (`_num_call`). No more matches are trained for either half until the engine is ready (R-570): never propose it again as the next step.

### 24. The kinds that follow: pushes, holds, base res, opening, hand-offs
- The kinds that follow (R-572), on the branch. The push flagger, flagger pushed, pinned, base res and opening plays carry
  `at_told` (the position they are told at, the fixed 60, 90 and 180 s record and the 60 s before, as on a split; set in
  `jobs.plays`, `AT_TOLD_KINDS`; it changes no play, and the development set's plays must be the same but for that key); a
  base res play carries `res` (attackers, defenders, coming back, who stayed) and an opening play `open` (players to the
  stand, on a split, back at home, waiting for the next flag). Stage 1 of each is a report in `cases.py`, kept with
  `--json`: `pushes` (`push_cases.json`: who pushes, where the flagger was, the readings U1 to U5, and what followed as it
  fell by who pushes and whether his team sent help), `held` (`held_cases.json`: a team held in its base, by how the hold
  ended and the players alive when it began, H1 to H5), `res` (`res_cases.json`: stayed through the base res or left
  before it, B1 to B6, and the stays by the health of the players in the base as the res lands) and `opening`
  (`opening_cases.json`: set out by his four points, R-590, N1 to N14). Help sent, the break-out, staying against leaving
  and who wins mark the spot and are never read as causes (staying against leaving is not one of his truths, R-534). He
  has passed the general tables of pushes and holds (stage 2, R-588); like spots and the test on unseen matches are not
  begun for any of the four. From his answers of 2026-11-22: a one-player push is read on their runs (`their_runs`,
  section D of `pushes`: who pushed their flagger and whether the pushing team sent a runner of its own, each set level
  on the flag lead held, since a team ahead loses lead as their flag gets in whatever it does; a reading, never advice).
  The danger of a base res is dying to it (R-589): a stay carries `res.health`, `low`, `inside` and `pit_npcs` (energy is
  not in the replay; `RES_LOW_HP` in `jobs.py` and `RES_LOW` in `cases.py` are Claude's drafts and no play reads them),
  and "base" is not made smaller until he says where the line goes. The opening play carries what the other team showed
  (`open.their`, `their_flag`, `their_first_cap`), the line of the first carrier (`beside.flag.line`, `common.line`) and
  the record 5 and 8 minutes from the gates (`open.later`, `OPEN_LATER_S`, R-599, with what the price of a position reads). The hand-off and the flag
  returned (R-620 to R-625): `jobs.flag_hands`, a record kept beside the plays as `flag_cost[rid].flag_hands` (it tells no
  play and changes none): `lives`, one a flag life (who ran it and of which line, every carrier, when it first stood in
  hand at the stand and on whom, how long it was held and by whom, how it ended, the position at the pickup and at the
  start of a hold), and `put_downs`, one a carry that ended on the ground (who and of which line, dead or not, where, the
  living enemy players within an aggro bubble of it, `enemy_near`, R-623, and what became of it: a team mate took it up,
  its carrier took it up again, returned, left lying). A flag goes back only when an enemy player picks it up (R-622).
  The second of a return is gvg.report's flag object at the spawn (R-481, `Moments.flag_backs`): the put-down carries
  `return_by_s`, the seconds from the put-down to the return, `returned_by`, and `returned_soon` (back within 15 s,
  `RETURN_SOON_S`, his window, R-629); `first_enemy_s`, the first enemy to stand on it, is kept beside them. A hand-off (`handoff`) is a living player putting the flag down with a team mate within an aggro
  bubble of it (his reading of the word, R-630), read before the result. `cases.py handoff <plays file>` (report
  `data/model/handoff_cases.json`): A, the record, with X1 and X2 (in range a flag is returned more often: both hold);
  B, a hand-off returned against a flag that lay and was returned later (R-626, "contested v uncontested"), and what
  a returned hand-off costs in flags against one a team mate took up in the same range (a third of a flag a minute
  on, made up by three minutes, which he has passed as the cost of one run, R-631; the two do not start level), with his truth T13 (R-629, in
  `tools/golden/truths.py`: it reads `flag_cost[rid].flag_hands`, not a play) at 1.5 and at 2 bubbles; C, his first
  point (F52), a later flag run by a frontliner with the stand held at the pickup (R-627: that is his case), run to
  the stand on him against handed on before it; D, his second
  (F53), a first flag on a frontliner at eight against seven, kept or handed on; E, his third (F54), who holds a held
  flag, the holder named by build (R-624; the groups are Claude's, and which builds are the primary defender or the flag
  runner is left to the data, R-628: do not ask him again); F, moments to look at. How a flag is carried follows the spot a team is in:
  none of it is advice. D and E are under the floor at 564 matches. A team held in its base is no decision family and
  is read as execution with the measurements of R-572 (R-619, R-621): no stage 3 for it. What the held team heals, its
  NPCs or its players, mostly follows what the holders hit (R-658): a reaction, never a call or a fix; a hold is to be
  told with what the holders went for, NPCs or players (not built).
  After any change to these records compare the plays with the run before, `open`, `res` and `beside.flag.line` left
  out: nothing may differ (`flag_hands` is in `flag_cost`, not in the plays).
  From his answers of 2026-11-22 and 23 (R-591 to R-614), as built now.
  The base res is a call only in the danger zone (R-592, R-609, R-610, R-614): the main team, three or more of it in their
  base, with his three factors on 20 s before the res: half or more of them past their res shrine, two or more enemy NPCs
  hitting them, and 300 or more damage a player in the minute before, hits and degen (`RES_WORN`, his number, R-676; 250 on hits alone before it, R-615). One
  reading, in the engine: `jobs._res_stand` (`marks`, `danger`), on every base res play as `res.early` (20 s before, when
  staying or leaving is still the team's) and `res.at_res`, and on the res spots. Low health is not a factor (R-602). Every
  other base res is context with no call (`jobs._res_context`: `clear` false, `unclear` saying which part of the danger spot
  is missing, R-488); the Classic base res rows outside the zone check that in the key, his words under `later` (R-614,
  R-615: 18 of his 25). The call carries his two factors (R-616, amending R-613: `jobs.res_factors`, `res.factors`, said on
  the row): morale `RES_MORALE_BEHIND` (30, confirmed by him) or more under theirs over the eight, and the stand not held;
  `against` counts the two, and the res of 12:00 or later is kept as `late` and counts for nothing. No verdict is built and
  none is to be (R-617): whether a stay there is a mistake is not known, his assumption is that staying is usually correct,
  and what the engine says is the sentence (`cases.res_sentence`, kept as `danger.calls[].sentence`): the chance of winning
  the team had, what stood against the stay, the deaths it took and the points it lost or gained. Never tell him a stay
  was a mistake or the right call. The chance of winning and health are not factors of the call (R-613), though like
  spots are still set level on them. `cases.py res` (`danger_report`): D, where the danger zone is, with his eight games
  (`HIS_RES`; Men v BcS 6:00 and DUM v ohno 8:00 are outside it and stay out, R-618: never an exception for them; hook v
  Men 6:00 is left as read, R-607); E, the two factors, each and together, with the clock beside them (`his_factors`, E1 to
  E10); F, what a death costs there (`death_cost`: as it fell by how many died, raw and set level on where the team
  started, and as the price of a position reads one more death, a kill and a pit NPC at that position); G, what else
  separates the stays that take deaths (thirds of the zone's own stays, D1 to D8); H, like spots among the stays with the
  test on unseen matches (T1 to T3), set against holding what the team had, since almost nobody falls out
  (`jobs.res_spots`, the record 40 s before the res kept beside the plays in `flag_cost[rid]`, R-601, R-605; the prices
  are not fitted on it); I, every danger zone base res as its sentence (`danger.calls` in the report's file). On
  2026-11-23, at 250, 156 stays: T1 to T3 are not clear, and the factors' groups are under the floor of 30 (27 stays with
  one or both against). A fitted input needs 20 events each (SPEC 5, rule 3): 27 stays with a death carry one at most.
  The opening is set out on his seven decisions (R-611; `cases.py opening`): from the gates (`GATES`), the first flag and on
  whom, cap or hold at the stand, hand the flag on, send a player back before a cap (`open.next`), a split in the first
  3:00, and a flag against none. Each is judged on flags and kills first, then the boosts and the chance of winning at 5:00
  and 8:00, with the NPCs (R-596, R-599), from the side of the team that makes it and set level on strength alone, since an
  opening has no minute before it (`_open_cmp`; under the floor a call is shown as it fell); like spots and the unseen test
  where teams divide (`_open_scenario`, `OPEN_VARS`). Who caps first, and whether anybody caps, is what two teams' choices
  come to and is never a call (R-608): N1 to N4 only say what follows it. In control of the stand is having the flag stand
  captured (R-604): a hold by a team that has capped is the flag in hand (R-553), not the opening's. Tried and taken out at
  his word, never to be built again: a team "having the stand" because its main team stands nearer it; and the first-flag
  holds told by what the other team's flag did meanwhile. A difference between two calls counts the opponents among the
  others, who lose what the callers gain: say so whenever a size is quoted. The usual split response is the player other
  than a monk a guild most often sends first, the match's runners left out (R-593, R-598, `usual_responder(D,
  monks=False)`). Pushing the flagger is a decision of its own and no answer to their run (R-591), and no family (R-597):
  its readings (`cases.py pushes`, section E, his five questions on `their_runs`) stay a report. No verdict of any of
  these is advice.

### 25. The Lord push and Lord damage
- The Lord push and Lord damage (R-632, R-633). Lord damage is gvg.report's to say, everywhere: what decides 28:00 is
  aggressiveness, and raw damage matters only for killing the Lord. gvg.report's own record
  (`summary.objectives.guild_lord_damage`: team scores with `lord_damage_equivalent`, every hit, heal and effect on a
  Lord by the second with Entourage and the Amulet's limit, the pit NPCs' deaths, each Lord's health once a second) is
  dropped by the trim, which keeps only each Lord's total (`lords[].taken`, flux damage in it); it leaves life steal
  out, and the engine's sum of the recorded hits (`Moments.lord_hits`) does not. Aggressiveness (R-634) is each point
  of damage to the enemy Lord, 30 for an attack missed through Blind, less 50 for an enchantment or weapon spell on a
  team's own Lord, 300 with Entourage up; it rebuilds exactly from the record's event list, a hit counted for the team
  that dealt it (source "map" is the flux, nobody's). gvg.report's record also scores each Blind put on the enemy Lord at
  30 for the team that put it there (events of kind `condition`; 176 of them in 53 of the 658 matches): with it every
  team score rebuilds. Built on the branch (2026-11-24): the record is in the file beside each replay and the engine
  reads it, `Moments.lord_record()` (`extras.LordRecord`: `hits`, `damage`, `aggressiveness`, `health`). Every Lord
  damage figure is gvg.report's (`on_lord`, the split's `lord_damage`, the Lord play and the Lord line, the end
  record's `lord_damage_by`); each position carries both teams' aggressiveness (`aggr` in `consequence`, R-634) and each
  Lord's health as gvg.report estimates it (`lord`, in place of the health rebuilt by `lord.py`), and the price of a
  position reads both (R-635: `cases.position`, the seventh price "aggressiveness lead (per 500)"; one price for the
  whole match though the lead decides only at the end, a stand-in until the win model takes the prices' place). Who is
  on a Lord and when stays read from the replay's own hits (`Moments.lord_hits`, the count of hits behind `aim`), as
  who is in which fight is (R-655). A team whose Lord damage the observer did not see keeps its blank
  (`Moments.lord_unseen`). `data/model/lord_gvg.json` and `review.py lord-record` are no longer needed (for the
  clean-up, R-398). Never give him the health rebuilt by `lord.py` as gvg.report's. A fetch downloads about 180 MB of
  replay and 65 to 110 MB of summary a match, and gvg.report serves no smaller Lord damage payload. Picked Lord pushes
  are marked on the site, Model > Game review, the view "Lord push" (`review.js`; rows `data/model/lord_rows.json`,
  written on the branch by `tools/golden/review.py lord <main>/data/model/lord_rows.json <report id>:<m:ss> ... --gvg
  <main>/data/model/lord_gvg.json`, which reads the matches itself; his marks `data/model/lord_row_marks.json`, to be
  filed as set p4 of the key). Never put Lord push rows to him in the chat for marking, and never write the rows
  again over rows he has marked without saying so.
  The Lord play as built on the branch (2026-11-23; R-640 to R-646, R-650 to R-654): `jobs.lord_plays` reads the end
  of the match from where the players stand, `Moments.end_play`, never from hits on a Lord. The record
  (`moments.py <report id> end`; kept beside the plays as `flag_cost[rid].end_play`; settings `END_*` and
  `PLAY28_FROM` in `common.py`; said and summarised by `tools/golden/endplay.py <report id>` or `all <out.json>`,
  report `data/model/end_play_draft.json`): at the end of play (the Lord's death, or 6 s before the match is over)
  every player is sent (on the enemy's ground within `LORD_BASE_R` of their Lord, R-446: a player who stops at
  their footmen is not), kept (on his own ground) or in the field, and since when; a team's send is the middle of
  its sent players' `since`, the play is set at the later send. Two readings from his marks: a player who dies on
  his way into their base was sent (hold v Dz 26:15: `_end_way`, on their ground at their door, base or pit past
  the last turn-off to mid, for JOIN_S or having stood in the base); and a send is read while the play is on, not
  at its last second (R-654: a living player who left their base or his home less than JOIN_S before the end
  counts where he stood, R-579, with `left`). Change either against the eight draft rows (p4-9 to p4-16) and Book v
  hook (his "NO corresponding push"), never by a wider "sent": every door zone of their base, his labelled Base
  area, and "left after the play was set" each read a push in return that he does not see (tried and left).
  The play for 28:00 is one play of both teams (R-640): a play a team with the same sentence, start (when the first
  group went) and end, which the page reads as one row; each carries whom the team sends and keeps, `aim` and the
  Lord figures. "28" is the end of the match, not the clock (R-642); a Lord kill by a team that sent its players
  before 25:00 is a push before it (R-653, his line). A push before it is no row of its own (R-644, R-650): it is a
  Lord line (`lord`, `lord_line`; the scenario is left as it is, and `review._reads` adds the line) on the rows of
  the situation it grew out of: the losing team's held rows from the killers' first send on, the last read on to
  the kill; else the rows of the killers' split in its base (Dz v Crew 21:36); else the killers' last numbers row
  (cope v hold 22:40, the stay after a wipe). In a match that goes on to a play for 28:00 a held row from 23:30
  on, begun before that play, in which the Lord is hit carries the line (Team v hook 24:02); any other earlier
  visit is not told as a Lord row (R-652). `aim` is read over the stretches the Lord is hit (`Moments.on_lord`):
  "killing the defenders" where more hits in the base land on players than on the Lord (Crew v cope 24:44), else
  "the kill" where the send kills him (his words on ohno v Book 25:04), else "Lord damage" (Team v hook 24:02); the
  kill is read from the result, intent not being in the replay. A run prints how many pushes before it have no row
  to be told on (R-460): keep it at none. After a change compare the plays with the run before, the Lord plays and
  the keys `lord` and `lord_line` left out and each id without its running number (a play's id ends in its place
  in the match, which moves when a Lord play comes or goes). `review.py lord` is retired; rows of the play for the
  page are written by `endplay.py rows <main>/data/model/lord_rows.json <report id>=<why picked>` (ids
  `e:<report>-end`, added and never rewritten). The p4 games are in the development set. A check in the key may
  read a record kept beside the plays (`"record": "end_play"`, dotted names).

### 26. What each prot did, degen and interrupt attempts (summary data)
- What each prot did, degen and interrupt attempts (R-636 to R-639). Not built: at the next rebuild, with R-481 and R-632, GvG Info keeps from gvg.report's
  summary, in its own file a match (filled from the summary; only summaries are fetched again, not replays): per skill
  blocks, knockdowns prevented, overhealing and Divine Favor apart; healing and prevented by target for healing and prot
  skills (the Lord too); what each player received from each ally by skill; the enchantments on each Lord; and for every
  death and spike save the healing and prevention by source and skill, the prots up, knockdowns and interrupts on the
  target, blocks, health at the start and end and condition uptime. Crits and cast timing stay out (the event log has the
  timing). Blocks and knockdowns prevented are gvg.report's estimates, per caster and skill, with no time or target.
  Who stripped which enchantment is read from our replays, never from gvg.report's `removed_by_*` (in reports read
  from early November 2026 only; a check there): a strip's cast start naming its target, the stripper's next cast
  finish, and an enchantment on that target ending within 0.4 s of it (R-637; Gaze of Contempt takes every one that ends).
  Degen and regen too (R-638): degen dealt and taken by each player net of regen, regen received, degen by condition and
  source skill, and in deaths and spike saves the regen and degen on the target, Deep Wound and the pressure split; the
  engine's degen (`pressure.py`) then reads gvg.report's figures, since the replays record degen as no damage and most
  burning in them has no caster.
  Interrupt attempts too (R-639): every targeted interrupt attempt, hit or missed, with its target, and likely fake
  casts by player; until then only landed interrupts are kept, and forensics and `pressure.py` read the attempts once kept.
  Degen in every damage figure (R-649): once R-638 is built, NPC damage accounts for degen and so does every other
  place damage shows up; the list of places is in the ruling (NPC damage by kind of bar, the execution measures,
  the danger zone's damage line of R-615, which is put to him again on the new figure, the aim of a Lord push, the
  death accounts and nodes). Amounts take degen in; who is in which fight, a stand-off and who killed a player
  stay read from hits and casts (R-655). Degen on NPCs and on a Lord is read from gvg.report too (R-661, in place of the
  estimate of R-657): its summary credits it to the player, the condition, the skill and the target, as totals for the
  match with no time (the `targets` rows of list `d` in the file beside each replay), so it is shared out over the
  stretches a player is on an NPC. The engine is to read gvg.report's energy estimate (R-664, turning R-662 round and in place of R-177): not built; where it bears (pressure, the boost clock, the base res, execution, the death accounts) is listed in the ruling and gone through with him first.

### 27. The measurements of R-572: execution, NPC damage, pair rule, split at all, stake
- The measurements of R-572, on the branch (built 2026-11-23; each is a record or a report and moves no play: after any
  change to them compare the plays with the run before, the key `npc` left out wherever it stands).
  Execution, both teams by the same measures (2.12, R-299): `execution.py`. Over the whole play (R-710, 2026-11-24;
  it was the first 20 s before; a hold keeps its first 20 s as `first`, for R-621) of every play, the players the play names (`who`), else the team's main team, and the enemy players in the same
  fight as one of them (`Moments.linked`): `MEASURES`, each with the direction a player expects and its words (damage a
  living player, damage against the roles' usual, the share on their backline monks, the share on the one player hit
  most, spikes, interrupts, knockdowns, disables, cast prevention, degen, kiting, baits, useful and wasted strips, time
  their attackers spent Blind, hexes kept up and removed, damage on their NPCs, healing of our own, and the three
  measures of a team's own care named below). Kept beside the
  plays as `flag_cost[rid].execution`, one entry a play id with `own` and `their`; `python3 execution.py <report id>
  [m:ss]` prints a match. It reads `pressure.py` and the event layer, so the first run over every match builds those
  (about 3 s a match). `cases.py execution <plays file>` (report `data/model/execution_cases.json`): A, the record and
  what each kind of play is placed against (`bench`, `exec_place`: low, usual or high among plays of the same kind);
  B, each measure against what followed (the upper third of plays against the lower), with the same comparison on the
  60 s before and how far apart the two groups already stood; D, a team held in its base (R-621: the first 20 s of a
  hold against what the team then loses, only between holds alike in players down, the base res clock and pit NPCs
  already lost). The enemy's execution is scored and never offered as a fix (R-299); a measure that tells the minute
  before marks the situation, one against the expected direction is likely a reaction (SPEC 5, rules 4 and 4c); a
  clear line is a place to look, never a finding or advice. Execution said on a row in words: `cases.exec_sentence`
  (`cases.py execution-say <plays file> <report id> [m:ss]`): for the team making the play and, apart, the enemy it
  meets, the measures that stand out among plays of the same kind (`exec_out`: outside nine plays in ten, where
  `exec_place` reads the outer quarters), each with its value and what the middle half of such plays had; what stood
  out, never why, and no verdict. It is on no page yet. The team's own care is read with `forensics.py` on the
  play's window (2026-11-23): casts started into a ready interrupt (`into_ready`), attacks made while Blind
  (`blind_attacks`: Blind is named in few replays, about one side in a hundred, so it says little until the
  rebuild) and the share of damage taken off a shield set while not casting (`off_shield`). A boost play (no 60 s
  record) and the later stretches of a split (no position) are not in the report.
  NPC damage by kind of bar (R-433): `npcpower.py`. `bar_class` is the rough class (a warrior by weapon, an
  elementalist by attunement, a monk by whether he heals, else the profession); `python3 npcpower.py bench` writes
  `data/benchmarks/npc_damage.json` over every match that counts (run it again at a checkpoint when matches are added;
  about 15 s): the damage a second one player of a class adds to a group that is on a kind of NPC (he is in the group
  for the whole stretch whether he hits or not: a monk on a split adds almost nothing), and the damage it takes to kill
  one. `Moments._props` carries it as `npc` on every group; the like spots of a split are matched on it (its damage
  a second on archers, knights and the Bodyguard, in `SPLIT_VARS`, 2026-11-23); no play reads it.
  The pair rule (2.13): `model.steady_pairs`, run by `cache.py warm` before the cap tests: the `SCREEN_TOP` strongest
  pairs are screened on each half of the matches (halved by `cache.fold_of`), on what team strength and each
  variable's own curve leave, and only a pair in both lists enters the win model, the same pairs in every fit of the
  run (`steady_pairs` in `cap_choices.json`; his `interaction` and `no_interaction` corrections still act). Until the
  choice exists a fit picks its own eight and says so. It was tried on made-up data only: read its first real choice
  and the held-out score at the rebuild.
  The decision to split at all (R-558), stage 1: `jobs.split_ticks` (kept beside the plays as
  `flag_cost[rid].split_ticks`: every 30 s from 1:00, a team with six or more alive and no split of its own out, his
  definition of the old kind, SPEC 6; the position, the fixed record, and the split it sends in the next 30 s, read
  from the split records of the plays) and `cases.py split-at-all <plays file>` (report
  `data/model/split_at_all_cases.json`): what is sent, when teams send one, as it fell by the chance of winning stood
  at, and a split against none from the same standing with the 60 s before. Stages 2 to 4 wait for matches (R-570).
  What is at stake (R-509): `tools/golden/stake.py <plays file> --key <main key>` tests length, damage traded, players
  met and what followed against his grades, each game from the others. On thirteen games nothing tells his Weak and No
  decision rows apart (only 10 of them are still read by the engine): nothing is added to the confidence band, and
  none is to be guessed. Run it again when more games are graded.

### 28. A numbers advantage from kills is not a family
- A numbers advantage from kills is not a decision family (R-557: the team up keeps killing and follows the team down,
  whose own choices read as near forced; the numbers that are decisions are those a team chose to make, a runner, a
  split or a collapse). Its cards are not marked and its view is off the page (the `ADVICE.numbers` entry in
  `review.js` stays for the split family to copy); do not put numbers cards to him again. The res (how soon it is
  tried, what stops it), giving ground a player down and fights in general are on the execution list. What was built
  stays and is described next, for the split family and for execution to use.

### 29. The numbers record
- The numbers record (R-550 to R-556), on the branch. Scope as built: numbers at
  the main fight from kills, a runner away and players on their way; the main fight while a split is out waits for the
  split family. Every numbers play carries `state`, `after`, `before`, a `clock` (when the numbers arose and ended,
  the base res, each side's dead, every res in the fight over three minutes: `jobs._hard_res`, a dead player alive
  again more than 3 s off the base res; a res that gets off ends an advantage from kills, R-552) and a `track` (each
  main team's step 0, 15, 30 and 60 s in, and a runner of ours gone): `jobs._numbers_at`, which changes no play.
  `cases.py numbers <plays file>` (report `data/model/numbers_cases.json`) is stage 1: the readings (a larger
  advantage, and one with the base res further off, kills more and lasts longer) and what followed each call, as it
  fell, then like spots and the test on unseen matches by scenario (section D), each with the same test on the 60 s
  before. `cases.py numbers-cards <plays file> f1 --site <main>/data/model/numbers_cards.json` writes the cards he
  marks on Model > Game review > Numbers advice (marks in `data/model/numbers_card_marks.json`; ids, `changed` and
  `gone` as for the flag cards; a situation he graded Weak or No decision has no card). A res that levels the fight
  ends the advantage unless that team dies again within 12 s (R-555: already how the stretches are read).
  The call is read 20 s in and told again at 60 s (R-556; `cases._num_call`), in his options (R-551: up, stay and kill, push into their base
  for NPCs, push their flagger, run a flag for a backup, fall back and reset; down, stay and fight, fall to footmen,
  retreat to the pit, trade with a split), never from the whole situation, which marks a team already winning. Never
  set cases with a res against cases without: a res comes where players are dying. The cards for a flag in hand
  (with R-553) and for a double run from the sender's side are held (R-554): remind him when more matches are in.

### 30. No new rule to answer a wrong row
- No new rule or threshold to answer a wrong row (R-465): rebuild the reading under it at the root, with his marked
  rows as the test. Who is in which fight is one reading on the branch (`Moments.linked`, `engaged_in`, `visits`; R-464),
  used by the numbers of the main fight and by a split's defenders: change it there, never beside it. His words on a
  row become checks in the review key, open until they hold; `review.py score` counts the open checks that hold now.
  Every match moment put to him carries its replay link and time: the time of the thing he is to look at (the carry,
  the death, the turn), never the start of the row it is told in (True v One, 2026-11-18: given 0:45, the row's start,
  for a carry at 1:48, he saw no pickup).

### 31. Fail loudly
- A reading which fails must fail loudly, never be turned into a blank (R-460). A blank that means "not in the replay"
  (unobserved Lord damage) stays a blank; a blank from a fault stops the run or is counted in the output, so that a
  field blank on every row is seen the same day.

### 32. His marks go into the review key
- His marks go into the review key the same session, with his words kept as he wrote them. An engine fault he points
  out is a check in the key, not a ruling; only his definitions and his decisions on process are rulings (R-452). A
  kind of play is used downstream only once he says the system is ready (R-496).

### 33. Game reviews by whole games
- Reviews are by whole games, one at a time (R-454, R-492), marked on the site, Model > Game review
  (`assets/js/pages/review.js`). On the branch: `tools/golden/confidence.py run <conf.json> <report id>` (the engine's
  confidence, R-497: the game read again with every draft number of the reading moved a quarter and to half and
  double, about twelve minutes a game; one band a situation, high, medium or low, fitted to his grades of the first five games on
  2026-11-17 (R-515), the fit written at the top of `confidence.py`; `confidence.py reband <file>` after a new fit), then `tools/golden/review.py export <plays file> <main>/data/model/game_reviews.json --set f1
  --part N --confidence <conf.json>` writes the rows: every situation the engine reads with its confidence, and under
  it each side's call. He grades each situation (Classic, Visible, Weak, No decision, Repeat), says whether the engine
  read a decision Correct, Partly or Incorrect with ticks for what is off and his words, marks the calls where they are
  asked for, and adds the decisions the engine did not read; saved to `data/model/game_review_marks.json` on main, which
  holds only his marks and the text of each row as he saw it. Read his marks from that file and file them in the
  review key the same session (`review.py file <id> <rows> <marks> --set f1 --key <main key>`, which prints his grades
  against the engine's confidence and the Classic rows to fix first, and writes the plain checks; then write by hand
  the checks for what a Partly or an Incorrect means). Set every result out for him in the chat (R-329). The queue is
  set f1 in `dev_set.json` (thirteen games graded: HC v Team, Men v Crew, 옷옷옷옷 v RACK, Men v RACK, Men v hold, hold v Men, HC v hdm, RACK v hdm, hold v RACK, HC v cope, as far as 9:40 and no further (R-532) 옷옷옷옷 v hdm, whose clock on the replay page runs ahead, R-527, and game 14, Dz v Team on Druid's Isle; game 6, hdm v HC, taken out unmarked, R-522, and game 13, Men v NwAy on Corrupted Isle, taken out unmarked, R-537: game 6 is not on the page or in the development set; game 13 came back on the page as game 15, R-559, and is graded, 2026-11-21; no game
  is kept hidden, R-497); pick further games from unused October and November games of top guilds, never a henchman
  game (R-476). Export the next game only when the last one is marked and its Classic faults are fixed, unless he asks
  for more at once; never fix against a game he has not marked, and never re-export a game he has marked. Games without `scheme` 2 are history, shown read only. The golden
  moments page is retired: label nothing new there; the 15 golden moments and their key stay as part one of the gate.

### 34. Documents
- Documents: SPEC.md and METHODS.md are replaced in place; the CHANGELOG gets at most ten lines per session; HANDOFF.md
  stays under 80 lines. Don't write session narrative into any other file.

### 35. The readability test
- Before an engine change ships, a fresh session that has not seen the build reads `knowledge/model.md` alone and must
  be able to explain each node in GvG terms (the readability test). The same test covers anything Denning answers or
  reads a verdict on (the blind test page, a decision card): the fresh session must be able to say each option and
  each verdict as a sentence a player would use.

### 36. The decision tier rebuild (REDESIGN.md)
- The decision tier is being rebuilt: `docs/REDESIGN.md` is the plan (families, scenarios, calls, the decision card,
  the steps and their gates). Read it before touching `decisions.py`, `usual.py`, `advice.py`, `ask.py` or `tq.py`.
  Its rulings are R-292 to R-309. Blind rounds are paused meanwhile (Train batch input `blind` stays on no).

### 37. Bundle 4 on its branch: story, records, line-up, gates, stage D, jobs
- Redesign step 2 (bundle 4) is built on the branch `bundle-4`, never on main piecemeal (R-322): `hallmap.py` (zones
  and walked distances from the labelled halls), `moments.py` (departures, triggers, scenarios, calls) and
  `tools/golden/golden.py` (pick, score) live there until the bundle lands. Golden moments (R-303): Denning labels
  them on Model > Golden moments (`data/model/golden_moments.json`, on main). That file holds only what he wrote;
  never decode or print a moment's `sealed` field in a chat.
  Also on the branch: `story.py <report id> [from] [to]` prints the story so far (R-341: the engine reads a match as
  Denning's notes do: flag forms, every fight with its place and numbers, deaths against the base res, NPCs), and
  `tools/maps/draft_greater_stand.py` drafts each hall's "Greater stand area" (R-334, R-342) into `data/maps/draft/`.
  The golden page (R-354) shows the engine's story of each game (`data/model/golden_stories.json`, from
  `tools/golden/golden.py stories`); he ticks the lines that are wrong with his reason and adds notes or corrections
  (`label.story.wrong`, `label.notes`). The 13 notes marked `blind_note` were written before he saw any story: after
  every change to `story.py`, regenerate the stories and compare them with those notes yourself (the blind check).
  His marks keep the text of the line they were made on.
  The record is the work, not the description (R-362): `Moments.attempts()` (one record a split attempt or main team
  push, R-357, R-358, R-363, R-364), `caught()` (R-359), `flags_record()` (R-360), `main_team()` (R-335, R-355) and
  `common.flux_at` (R-356) hold what the engine keeps; `moments.py <report id> splits|flags` prints them, and `story.py`
  prints its split, push and cap lines from them, never from a second reading. Lessons from his marks, notes or
  commentary go into these records first. The words of R-373 and R-375 to R-378 are records too: `flag_pushes()`
  (pushing the flagger, R-371), the flag route, door, hold and boost distance in `flags_record()`, `flag_lead()` and
  `lead_at()` (the flag tally, R-408: the stand counts as one flag; bands at 0.35, 0.8, 1.3 and 1.7), `pregame()`,
  `standoffs()` (the disengage, R-405, framed on OG v hdm, R-411, in place of posture: main teams standing off with
  little or no damage traded are not a fight), `timing()` (the four choices of R-377, the held flag of R-400 and
  R-407), `onto_flag` on a main team push (R-401), `monk_counts()` and `on_lord()` (R-378); their thresholds in
  `common.py` are confirmed (R-404, R-406). What the flag readings are for is R-412. To see what a looser or tighter threshold would do,
  use `tools/golden/thresholds.py sweep` (it sets `GVG_TRY`; never set that in a training run). From the gate review
  (R-416, R-417): `way_out()` (a team going out of its base by a door), and in `attempts()` who set out together,
  where a split fell back to, a main team that went home for a split, and swaps in the answer; a push on a flagger
  counts from 4 s when he reaches his team with the pushers still on him (R-418).
  The line-up is the measure of the reading (R-368 to R-397): timestamped commentary and comms filed as paraphrased
  statements in `data/lineup/` (never transcripts), checked against the story by `tools/golden/lineup.py` on the
  branch. The four games in `data/lineup/held/` were the held-out check: Denning reviewed their misses
  once (R-416), the reading gate passed, and they are spent (building games from here, R-417). The line-up only checks that what was said is
  in the story, so run `tools/golden/thresholds.py` beside every rescore to see what a change did to the records over
  all matches. The gates and the build order are in `docs/REDESIGN.md` ("Tests", "Build plan from here").
  The decision moments are read from the records (stage B: `run_starts()`, `attempts()`, the numbers in each main
  team's fight, `verbs()`); the decision gate is `tools/golden/golden.py gate --data <main>/data/lineup` (part one
  against `data/model/golden_key.json`, Claude's reading of his golden notes, R-341, which he corrects; part two the
  comms calls of the line-up).
  Stage D (depth) on the branch so far: every moment carries the shape of its call (`shape()`, R-297: who as properties,
  which way, when, with `gained_elsewhere()` for the timing rule of R-321) and what followed (`consequence()`, R-294 and
  R-412: hard results over the whole map at 90 and 180 s, the flag lead set beside the numbers meanwhile). The jobs are in
  `jobs.py` (R-423 to R-449, Denning's own table: read those rulings before changing a job or a test): a call is an
  allocation of plays (flag, push flagger, flagger pushed, split from both sides with collapse and full collapse apart,
  numbers, boost, pinned, base res, lord), each with its job, its test, its own clock (to the event that ends it, never a
  fixed 90 s) and what it cost kept beside it; a test covers only what the players of the play control. Whether a job was
  met is a result, never a verdict on the call (similar cases) or on execution. A split is read phase by phase from
  when it reaches a defender or their base (R-438 to R-449, his review of the first cases: read them before touching
  `split_plays`); flags carried by a player with Shadow of Haste are set aside (`soh`). `moments.py all <file>` then `jobs.py
  summary <file>`, `moments.py after|runner <file>`; `jobs.py <report id>` prints a match's plays. Thresholds marked
  "Claude's draft" in `common.py` are his to confirm.

### 38. Before the next training run (R-398)
- Before the first training run after the engine is built, go through Denning's list with him (R-398; REDESIGN.md
  "Before the next training run"): plan and spec, rulings, old files, the Templates and Meta tabs, skills from the
  wiki, the model pages, anything outstanding.

### 39. Guild hall maps
- Guild hall maps: `tools/maps/build_maps.py` builds the site's map data from the replays branch
  (`data/maps/index.json`, `outline/<map id>.json`, `auto/<map id>.json`); Denning's labels (points, areas, routes) are
  saved by the site's Model > Guild hall maps page to `data/maps/labels/<map id>.json` and override estimates. The
  engine does not read outlines or labels yet (REDESIGN.md step 2). `tools/maps/draft_labels.py` drafts labels from
  the replays for Denning to accept (`data/maps/draft/<map id>.json`; `--score <ids>` compares drafts with his labels);
  it never reads or writes his labels, and he keeps choke points, NPCs, gates and hazards for himself. The page draws
  drafts dashed; accepting one copies it into his labels with `from_draft`, removing one adds its id to `dismissed` in
  his labels file, and draft ids are stable so rebuilding the drafts never brings back one he dealt with. gvg.report serves some halls' geometry only by the
  game's map file id (`replays.mjs` MAP_FILE_IDS); to look at any gvg.report endpoint, run the "Probe gvg.report"
  workflow with the endpoint in `pages` (optional `pick` = parts to keep, `grep` = pattern to find in its scripts) and
  read the `probe` branch. `data/maps/<map id>.json` (no subfolder) is the
  engine's own NPC store and is not touched by either. `tools/maps/audit_labels.py` checks his labels against R-310 (pit roster, one res shrine and flag
  spawn a side, equal NPCs, doubles, mirror partners) and never writes them; run it after he labels. What each hall adds to
  decisions (footmen or none, fall-back zones, effects, objects and flag routes by label id, its decisions) is in
  `data/maps/hall_features.json` and `knowledge/guild-halls.md` (R-310 to R-317). A route drawn through a teleporter
  overstates the walk: use its walked length (`audit_labels.py --routes`, R-316). Never add a `.py` file to `tools/replay_analysis/` for site or
  tooling work: every file there is part of the measurement cache key and would force a full rebuild.


### 42. A backline monk, told by his bar (R-698)
- Who is a backline monk is one reading, `common.monk_kind(m, a)` ("backline", "smite", or None for any other
  profession), with `common.backline_monk` and, for a record that holds role names and no agent numbers,
  `common.backline_roles(m, tm)`. Every count of monks asks it: never tell a backline monk by his party slot, by his
  role name or by Word of Censure on his bar. His elite tells: a Smiting Prayers elite (Word of Censure, Ray of
  Judgment) is a smite monk whatever else he carries; any other Monk elite a backline monk. Where the observer saw no
  Monk elite, the skills seen tell (more Smiting Prayers than Healing Prayers, Protection Prayers and Divine Favor is
  a smite monk; more of those a backline monk); a bar that tells neither stops the reading (R-460: none in the 564
  counted matches, one monk told by his skills). `common.skill_row` finds a bar's skill by its id, then by its name as
  the replay spells it ("Shield Guardian PvP" for "Shield Guardian (PvP)").
  Why it was built (2026-11-24): a monk was told by slot in a dozen places and not alike. `jobs.py` and `energy.py`
  read a Monk outside slots 6 to 8 as a smiter (26 heal or prot monk-games of 3,628, in 23 team-games: hook, chic and
  hdm with monks in slots 4 and 8, EDGE, One, meow and True with monks in 5, 6 and 7); `moments.py` and `story.py`
  read a Word of Censure monk in slot 6 to 8 as a backline monk (57 monk-games), as did `phases.healer`, and through
  it the death accounts, the nodes, `npcpower.py` (a smiter's NPC damage read as a backline monk's: 1.0 a second on
  footmen for 10.7) and the execution measures. Over the 564 counted matches now: 3,139 backline monk-games, 489
  smite (461 Word of Censure, 27 Ray of Judgment, 1 with no elite seen).
  What asks it: `jobs.py` (the split's monks, the ratios of R-457 at the main fight, the base res), `moments.py` (the
  monks of an attempt and its answer, `_mk`, `monk_counts`, the call keys "two monks"), `energy.py`
  (`backline_monk`), `story.py`, `phases.healer` (a backline monk, or a healing Ritualist in the 8 slot: the older
  "healer", which the death accounts, the nodes, `eventlayer.py`, `npcpower.py` and `execution.py` read),
  `fights._monks`, `scoreboard.py`, `lnrows.py`, and `common.line` (a smite monk is midline, R-670; a backline monk
  backline). `execution.py`'s `drain_on_monks` reads the backline monks alone (R-699: a healing Ritualist is no monk
  for energy); its other "healer" shares keep the older healer. Role names are unchanged (his names by slot: Prot, 7
  Monk, 8 Monk, "Monk N" elsewhere, "(WoC)" beside a Word of Censure monk): a name no longer says what a monk is.
  Still by name, and left: `cases.py` `_usual_response` ("Monk" or "Prot" in a role name), `tq.HEALER_ROLES`,
  `behaviour._line_of`, `forensics.role_group` (the role a death account is placed against: Prot, 7 Monk, 8 Monk by
  name, else healer).
  A monk with Word of Censure and four or more heal and prot skills (25 of 461 Word of Censure monk-games) is a smite
  monk by his elite, and plays as one: a median 108 healing a minute against a backline monk's 641, and 249 damage a
  minute against 4.
  Checked (R-453): the development set, 323 Classic rows pass and the review key reads as before; 234 of 6,933 plays
  moved, none gone, one new (hdm v hook 13:02: with hook's Monk 4 a backline monk its main fight is two damage and
  two monks against hdm's three damage and one monk, so hook's main team has the job to kill, R-457). The keys that
  moved: the monks of a split, of its defence and of the main fight beside it (`split.monks`, `split.numbers`,
  `defending_monks`, `beside.defence`, `beside.main`, `beside.main_can_kill`, `split_damage`), a runner's line
  (`line` on an opening's flags: 70 values, a smite monk backline to midline), and NPC damage by kind of bar
  (`props.npc`, `our_runner.npc`, `their_runner.npc`: a Word of Censure monk in slot 6 to 8 read as a smiting monk).
  The full run (2bebbc6, 29 minutes, against a full run of 7bce16e the same evening): 33,062 plays against 33,094;
  1,935 changed in 196 matches, on the keys above; 44 gone and 12 new, every one the main fight's job to kill beside
  a split (R-457): gone where "they have no monk there" was a heal monk in slot 4 or 5 unread (cope v Book nine
  times, RACK v hdm fourteen), new where a team's own monks are counted now. The truths hold as before (15 of 15).
  Every `cases.py` report rebuilt on both runs: the flag ladder, pushes and held teams read the same to the line; no
  verdict of the flag test, the base res, the hand-offs or the energy tables moved; at the margin, a split of one
  player 90 s on reads better again (+5.0, +1.6 to +8.3; it was no clear difference), an opening hold at 5:00 better
  (+4.9, +0.1 to +9.8), and three numbers and main-fight lines fell to too few to call.
  Not rebuilt: `npcpower.py bench` (57 monk-games moved from its backline kind to its smiting monk kind: rebuild it
  before the next full run, since the plays read it) and the forensics benchmark (its healers moved the same way).

### 43. Monk casting efficiency (R-689, piece 4)
- Monk casting efficiency (R-666 the first aspect; R-678 to R-680, R-687; against the same monk role, R-671) is one
  reading, `casting.py` (read its top before changing it): `record(m)` gives every backline monk's row for a match,
  `python3 casting.py report` the usual of each role over every counted match (`data/model/casting_cases.json`, about
  20 s), `casting.py <report id>` a match's monks in sentences, each placed low, usual or high for his role (under
  the 20th percentile, over the 80th), `casting.py cover` the checks of the record. It needs no energy record, so it
  reads all 564 counted matches. No play reads it and none moves; it is not yet in the death accounts or among the
  execution measures (`execution.py`), where it belongs once he has ruled on the questions below.
  What is read: energy spent is the listed cost of every cast a backline monk started from 0:00, whatever became of
  it (R-680), from the replay's own casts (`forensics.Forensics.casts`, the one reading of how a cast ended). Useful
  points are healing that landed, Divine Favor's counted, plus damage prevented, point for point (R-678), from
  gvg.report's totals for every skill he cast (the file beside the replay, `skills`: match totals with no time, so the
  measure is a monk's whole game, never a fight). Removals (the replay's own credit, `outcomes`) and knockdowns
  prevented are counts apart. No cast is marked "not needed" (R-679): a prot that prevented nothing adds its energy
  and no points. A cancelled cast is a bait where gvg.report reads an enemy interrupt on him as missed because he
  cancelled (the attempts of R-639, its read "cancel"), begun inside the cast or within a second of its end; any
  other cancel is energy burned, or an interrupter scared off unseen.
  Checked against the raw record (2026-11-24, `casting.py cover`): gvg.report's `uses` are casts started (469,754
  against 472,687 in the replays, 99.4%), so its figures and our energy cover the same casts; a blocked attack is in
  `prevented` already, at 36 damage a block on all 4,449 rows with a block, so any blocking skill is credited (R-687)
  and nothing is added; of 1,219 interrupt attempts read as missed on a cancel, 741 match a cancelled cast in the
  replay (the rest fall on a cast another interrupt took). The 39,976 targeted attempts of the counted matches: 25,412
  hit; missed, 7,926 the cast finished first, 2,650 "random", 2,592 a cancel, 1,063 "likely", 333 "ineligible".
  What gvg.report's figures do not hold, to say with every figure: Aegis (PvP: for 1 to 3 s attacks on its
  target fail and no hostile spell can be cast on him, the spike save R-679 names as the exception) is credited with
  almost nothing (122 blocks in 6,753 casts; Guardian 52,931 in 63,095), since a failed attack is no block in its
  record and a spell that could not be cast leaves nothing, so it reads as nearly worthless (2.8 points a point of
  energy against Guardian's 10.8);
  Protective Spirit prevents nothing in its figures (1.6) and Aura of Stability only heals through Divine Favor
  (4.5); Healer's Covenant cuts a cost the listed cost does not know. Nor do the recaps measure Aegis: 211 of 4,054
  survived spikes and 101 of 9,144 deaths had an Aegis up, but a spike it stops outright leaves no recap. Put to him
  (recommended: the energy of the three out of the points, their casts shown apart as counts).
  Found over 3,116 monk-games with 100 energy or more (`MIN_SPENT`, a draft): the middle monk makes 15.6 useful
  points a point of energy (three in five between 11.7 and 20.6), overheals 31% of his healing (20% to 42%), spends
  61 energy a minute alive, 1.7% of it on cancelled casts and 2.8% on casts an interrupt took; 741 of 10,782
  cancelled casts (7%) drew an interrupt. By role: Prot 12.4 (9.8 to 15.5), 7 Monk 20.2 (16.2 to 24.3), 8 Monk 15.0
  (12.0 to 18.3); by elite: Healing Burst 21.2, Word of Healing 16.0, Blessed Light 15.3, Aura of Faith 13.8, Life
  Sheath 11.7: what a bar is built on moves the figure more than how it is played, and a slot does not say the bar
  (slot 6 is Life Sheath or Aura of Faith in 77% of games and Blessed Light in 16%; slot 7 Healing Burst in 66%;
  slot 8 Blessed Light in 74%). And the figure rises with how hard a team is hit: 14.6 for the third of teams hit
  least, 16.4 for the third hit hardest, overhealing 34% against 29%; losers 16.0 against winners' 15.0, overhealing
  26% against 36%. So against the same role alone it rewards being hit: put to him (place by bar, and beside monks
  hit as hard).
  Built on his answers (R-704, 2026-11-24): `role_of` is his elite; a bar with fewer than `MIN_GROUP` (40) placed
  monk-games is pooled as "another bar" (98 monk-games); within a bar he is placed among the third of teams hit about
  as hard (`team_taken_min`, thirds at 1,991 and 2,563 a minute) where that group holds 40, else within the bar alone,
  and the sentence says which (`group_of`, `place`). Aegis, Protective Spirit and Aura of Stability (`APART`) are out
  of `spent` and every figure from it (21,845 casts, 120,570 energy, 5.0% of what monks spend), counted apart
  (`apart_casts`, `apart_energy`; `spent_all` keeps all). His name by slot is said only (`slot_name`). Middle points a
  point of energy now: Healing Burst 21.2, Word of Healing 16.9, Blessed Light 15.8, Aura of Faith 15.0, Healer's
  Covenant 14.2, Life Sheath 12.5; hit hardest against hit least, Blessed Light 16.5 against 15.1, Healing Burst 23.1
  against 19.9. Still to do (stage X2): into the execution measures and the death accounts.

### 44. Execution, the build (R-701 to R-847; plan: REDESIGN.md "Execution"; every why and its rule: `docs/EXECUTION.md`)
- One reading, `execution.py`, for both teams; the death accounts in `forensics.py`. Stages X1 to X5 as in the plan.
  What the old engine carried that the record lacked on 2026-11-24 (from `learnednodes.EXPECTED` and
  `knowledge/model.md`): spike spread, casts while Dazed, Blind split by frontline and defensive, the right hex,
  strip value and best target, control on a runner, escapes in a collapse, the burst inputs of kill conversion.
  `lnrows.py`, `eventlayer.py` and `causalchain.py` imported `tq.py`, which retires at the close.
- Stage X1, built 2026-11-24 on `bundle-4`: the window is the whole play (R-710; `HOLD_FIRST_S` keeps a hold's first
  20 s as `first` for R-621, read by `cases.py execution` section D); `MEASURES` gains `spike_spread` (the middle
  spike's spread of big hits, from the event layer's spikes), `spikes_on_healers` (no direction until X2 reads it
  against the job, R-709), `dazed_casts`, `blind_front_secs`, `blind_def_secs`, `strip_right`, `strip_value`,
  `hex_right` (the event layer's records valued against what was in range, `eventlayer.valued`, now applied in
  `Exec`), `cripple_secs` (control on a runner) and `escapes_ready` (speed and escape skills off recharge at the
  start). `lnrows.py`, `eventlayer.py` and `causalchain.py` read `events.analysis` and their own values loader, never
  `tq.py` (`ask.py` and `learning.py`, report layer, still do: rewritten or retired at the close). Development set:
  6,934 plays identical, only `flag_cost[rid].execution` moved (82 matches); 323 Classic rows pass. Not yet built
  from the old nodes: the burst inputs of kill conversion, which belong to the attempt record (X2).
- Stage X2, first piece, built 2026-11-24: the kill attempt record, `execution.attempts(E)` (kept beside the plays as
  `flag_cost[rid].attempts`; `python3 execution.py attempts <report id> [m:ss]` says each in sentences,
  `say_attempt`; `cases.py attempts <plays file>` the first look). Every spike of both teams (`events._spikes`: 400+
  on one player inside 3 s) is read to its own outcome (R-710: his death, or 8 s, `ATT_AFTER_S`). The package
  (R-708): spread and share in the first second (`events._landing`), strips on him by the spiking team from 3 s
  before the first big hit (`ATT_BEFORE_S`) with the first one's lead and whether a prot came off, pressure on his
  team's backline monks (interrupts, knockdowns, Dazed at the first hit) with its lead, prots up on him, prots and
  heals cast on him with their offsets. Missed chances (R-713, `MISSED_KINDS`): defence prot and heal (a monk with
  one ready, in reach, at a half-second moment within `CHANCE_S` 1.5 s of the first hit at which it could still land
  a quarter second before the death; casting on another player under `PRESSED` 250 in 2 s is busy, R-711, and only
  counted busy if he was so at every moment; out of energy, R-681, no chance); defence interrupt (each spike skill
  cast on him that went off with an interrupt of ours ready, in range and able to stop it: `intr_kind` reads each
  interrupt's own text for spell, attack or any action, and leaves out those thrown only on a condition the
  thrower does not choose, `CONDITIONAL`; `intr_range` melee 250, bow, else cast range); attack strip (a prot up, a
  strip ready and in range, none came); attack pressure (an interrupt able to stop a spell ready on one of their
  monks in reach of him, none landed on their monks). Every row carries who had what ready.
  First look on the development set (74 matches, 1,034 attempts, 33% killed; a report, nothing tested): big hits
  within 1.0 s killed 47%, 1.0 to 2.0 s 27%, over 2.0 s 25% (R-701 reads as he says); a heal ready and nobody
  healing within 1.5 s, 77% killed, healed 18%; a prot, no chance at all 51%, missed 30%, missed by one and taken by
  another 16%, taken 32%. Strips and pressure on the monks go with fewer kills and an interrupt missed with fewer
  than none possible (29% against 50%): both mark the situation (strips come on protted targets; no interrupt
  possible means interrupters dead or away), so X3 compares only like with like. Busy at every moment: 0 times.
  Development set: plays identical, only `execution` and the new `attempts` moved; key as before.
- Stage X2, the rest, built 2026-11-24 (the stage is complete):
  Each attempt carries `state` at the first big hit, what the old kill conversion node read (health %, maximum against
  normal from death penalty or morale, his healers in range, hexes on him, distance from his main group): context.
  One reading of a monk's chance (R-703, R-711, R-713): `forensics.Forensics.ready`, `busy`, `chances` (`CHANCE_S`,
  `PRESSED` live there), used by the attempts and the death accounts. `is_prot` and `is_heal` there too: a heal is no
  prot (Shielding Hands) and does not heal only on a removal (Dismiss Condition out, Blessed Light in, by which comes
  first in its text). The death account gains `healed` (healing landed from the start of the killing burst, and the
  heal or prot chances missed), `recap` (gvg.report's recap beside our reading: its healing by source, prots up,
  interrupts, knockdowns) and `monk_casting` (each of his team's backline monks' whole-game casting efficiency,
  placed as R-704; context, never why he died). `flag_cost[rid].casting` keeps every monk's row beside the plays.
  `execution.py` gains: `intr_tried`, `intr_missed_share`, `intr_slow_share` (gvg.report's attempts, R-639); on an
  attempt, an interrupt thrown at a spike skill that missed is told with gvg.report's read of why; target choice
  against the play's objective (R-702, R-709): `objective(p)` from the job's words (to kill, offence; to hold,
  survive, delay, keep busy, reach cover, or a team held in its base, defence; anything else none), `disrupt_right`
  (knockdowns and interrupts on their backline monks when killing, on their non-healers when holding) and
  `dmg_on_front` (damage on their frontline when killing); the record keeps `objective`. R-712: `spike_kill_share`
  (conversion), `res_tried`, `res_first_s`, `res_stopped_share` (a res cast is any cast on a dead team mate: the
  replays record no resurrection), `ground_back` (the group's walk towards its own pit over the first 20 s, no
  direction), `water_share` (of the time in a labelled flag stand area, the share in labelled Water; Druid's Isle,
  median 0.71 to 0.79 a match on the development set, R-314).
  Checked against the raw record (R-707, 40 matches): 2,006 of gvg.report's 2,011 interrupt hits are interrupts in
  the replays (its 1,309 misses are new); 680 of 821 deaths have a recap, every one on a replay death, 92% of its
  prots on him in the replay; 79% of its strip links match an enchantment ending in the replay (ours stay the source).
  The flag left lying (R-706): `run_starts` gives `sent_off`, and `jobs` starts the run there: walked back from the
  take-up while the taker drew nearer the flag (as `nearer`) and was apart from his main group; only where a team mate
  takes up a flag another put down (R-581, "sent for"); under `SENT_MIN` (600) walked, at the take-up. Built so after
  five Classic rows failed on a first reading that walked back through his team's own movement (hold v Men 5:15, Men v
  NwAy 8:19, hold v RACK 16:43 and 24:45, 옷옷옷옷 v hdm 7:29); the carrier taking up his own flag is Claude's reading of
  "sent for", his to correct. 옷옷옷옷 v RACK: RACK's run now starts 6:14 (his Visible row holds). Development set: 323
  Classic rows pass; 51 flag runs start earlier (median a few seconds), one history row no longer holds (cope v Team
  2:43, marked wrong before the fresh start).
- Stage X3, built 2026-11-24/25 (R-714, R-715 ruled first): `cases.py attempts` sections G and H, `cases.py execution` section C (`x3_*` in `cases.py`; kept
  in `data/model/attempts_cases.json` and `execution_cases.json`). Full run 2026-11-25 on the timed record: 33,089 plays identical to the run before, only
  `attempts` moved; 323 Classic rows pass. Found on the way: the attempt record read taken against missed over different seconds (a spike that kills ends at
  the death, median 1.7 s; one that fails is read 8 s), so strips and interrupts on the monks piled up on failed spikes; the record now keeps each strip's,
  interrupt's and knockdown's time (`strip.at`, `pressure.interrupts_at`, `knockdowns_at`, `at` on interrupt chances) and X3 reads taken and missed only to
  `CHANCE_S` (1.5 s) after the first big hit, a part done later kept apart as late. 78 counted matches have no attempt: no 3 s burst on one player reached
  400 (the damage record is whole; their deaths come by pressure on players already low, read by the death accounts), not a failed reading.
  Missed chances (5,317 attempts, 486 matches): like with like = killed less the kill expected from the situation at the first big hit alone (target,
  prots on him, health and ceiling, healers in range, hexes, distance from his group, attackers), the expectation fitted without the attempt's group of
  matches. Prot passes (taken 21% killed, missed 33%; -10.9 points, -13.1 to -8.3; 9 of 10 groups), heal passes (-43.0, 10 of 10), interrupt on a spike
  skill passes (-17.8, -28.4 to -6.4, 8 of 9; only 36 cleanly taken); strip reads backwards (-8.8, 3 of 10: never a fault, R-285), pressure on his monks
  fails (-2.5, -6.5 to +2.0). The together window (R-708): no lead of the strip or the first interrupt on the monks shows a gain against it ready and not
  done; strips of a prot before the first big hit are almost never seen (26), so no window is measured yet. The bar (`X3_BUT`): range clear and the right
  sign in every group but one, set against the same test on records shuffled among plays of the same kind (with a 7 of 10 bar 92 measures passed against
  9, 26 and 14 shuffled; with this bar 49 against 1, 3 and 4, win points only). Measures, both outcomes (win points and net kills 90 s on): 132 pass, 2,
  13 and 9 on shuffles; 111 read backwards, about as many as the shuffles give (36 to 52 on win points), so most backwards readings are noise, not
  reactions. `spike_kill_share` and `dmg` against net kills come close to the outcome itself: X4 says them as context, never as a fault.
- Stage X3's remainder, built 2026-11-25: a play's own outcome (`cases.exec_own`, kept on each case of `exec_cases` as `own`; `cases.py execution` section
  C2, `x3.own` in `execution_cases.json`), said from the side of the team making the play: a split holds when nobody on it dies (R-517, R-523; the
  attacker's row) and the defence's side of the same seconds is a split player killed; a push on a flagger stops their flag and the flagger's team gets it
  in. Only the rows whose job it is: no change inside a split fight (R-511), no main team's row, no push team (R-487), no split nobody defends from the
  defence's side, no Shadow of Haste run (R-456). Same bar, counted apart from the two general outcomes (which read as before: 132 pass, 2, 13 and 9
  shuffled): 30 pass against 5, 2 and 3. A split loses nobody in 86% of 1,707 plays: of its own measures only `into_ready` passes (casts into a ready
  interrupt, -10.0 points, 9 of 10) and 13 read backwards (its damage, knockdowns, kiting, strips: a split that fights is a split being fought, never a
  fault, R-285); 14 of the defence's pass against it (damage -22.9, interrupts on its healers -32.5, knockdowns on a casting player -18.6, Cripple -11.2,
  interrupts thrown late +13.3). The defence kills a split player in 17% of 1,501 plays: 11 of its own pass (damage +20.3, interrupts on the split's
  healers +29.4, knockdowns on casting +23.7, strips, drain, Cripple, interrupts thrown late -18.4). A push stops their flag in 22% of 655 plays: the
  pushers' damage against their usual passes (+14.4), their Cripple reads backwards (a long chase); of the flagger's team's own measures none passes for
  getting the flag in (79%), only the pushers' damage against it (-13.2). Damage on a split or a flagger is close to the outcome itself, as `dmg` is to
  net kills: context, never a fault.
- Stage X4, built 2026-11-25 (`execution.deaths`, `death_lines`, `say_death`, `say_faults`, `chance_tests`, `FAULT_KINDS`; `python3 execution.py deaths
  <report id> [m:ss]`; `cases.py execution-say` prints each play's faults under what stands out). All three checked kinds are the defence's, so by R-714 a
  fault is listed only where a player died: `flag_cost[rid].deaths` keeps every death of a player with the chances his team missed, and each play's
  execution record names the deaths that fell inside it (`deaths.own` for its own players, `deaths.their` for the enemy players it met: places in the
  deaths record). On a spike that killed, from its kill attempt: a prot, a heal (the monk's chance in the 1.5 s from the first big hit) and an interrupt on
  each spike skill cast from 3 s before the first big hit to 1.5 s after it; on a death with no spike (under 400 inside 3 s), as the death account reads
  it: a prot and a heal from the start of the heaviest 2 s on him (`Forensics.killing_burst`), no interrupt (the chance is defined on a spike's skills). A
  kind a team mate cast in time is no fault and is not listed against the monk who held back (R-715: `Forensics.taken_in_time`, the same seconds as on an
  attempt; the death account's `healed` answer now drops it too). Busy on a player under pressure (R-711) and out of energy (R-681) are said as no chance.
  `chance_tests` is the one reading of taken and missed (X3's test in `cases.py` and the faults listed both call it); `cases.py attempts` stops with an
  error when its verdicts and `FAULT_KINDS` differ (R-460). The record holds what was there and no sentence; the words are `say_death`.
  Found on the way: the losing team recorded dying all at once as the match ends (`Moments.over`) was read as deaths, and a spike in the last 8 s as a
  kill: both left out now (2 of 1,836 kills in the attempt record; X3's verdicts as before: prot -10.9, heal -43.0, interrupt -17.8).
  Full run 2026-11-25: 33,089 plays identical, the execution records identical but for `deaths`; 323 Classic rows pass. 10,218 deaths in 564 matches: 1,834
  on a spike, 8,384 with none; 4,978 with a missed chance (1,397 of the spike deaths, 3,581 of the others; a prot at 3,785 deaths, a heal at 3,001, an
  interrupt at 1,077); busy 5 times, out of energy 286; 1,035 deaths fall inside no play. On the development set, the interrupt faults by the spike skill:
  463 on a cast of a second or more, 24 of half or three quarters of a second, 31 of a quarter second, 114 on an attack skill; 70 of 1,405 prot and heal
  faults are by a monk who himself died within 3 s of the burst's start. Both put to him as GvG questions, neither changed (R-465).
  Not tested on its own: a chance on a death with no spike (every such player died, so there is no taken-and-lived to set it against); the kinds were
  checked on spikes, and R-714 lists them in the death accounts: his marks on the Execution view are its test (stage X5). 626 of the 10,218 deaths have
  no hit recorded on the player in the 20 s before (degen, which the replay records as no damage, or life steal): the burst is then read from 2 s before
  the death, and 170 of them list a chance (Men v NwAy 14:35, the AoB Derv). Put to him with the rest; not changed (R-465).
  The Execution view (`tools/golden/review.py execution <plays file> <main>/data/model/execution_rows.json <report id> ...`; the site's Model > Game
  review > Execution; his marks to `execution_row_marks.json`): each death told once, under the shortest situation that holds it, the others named on its
  row; beside the situation, as context, each side's share of spikes that killed and its damage. Set out: Men v Crew (51683de9), RACK v hdm (d06ef3c7),
  Men v NwAy (c19f13e3): 46 deaths, 31 with a missed chance.

- The catalogue (`docs/EXECUTION.md`; R-716 to R-752), stage 1, first piece, built 2026-11-25 (`bundle-4` 45ad7cf). A monk's chance (`Forensics.chances`):
  looked for every tenth from `REACT_S` (0.2 s, R-716) after the first big hit (R-748) to `CHANCE_S`, the cast fitting before the outcome (the quarter
  second's margin of the first build is gone: the reaction replaces it), a spell's cast time doubled while he is Dazed (`dazed_at`), his own aftercast over
  (`in_aftercast`, `AFTERCAST_S` 0.75 after a finished spell, signet or ritual), and no spike on himself (R-747: `SPIKE_DMG` inside `SPIKE_S` from a hit on
  him, the spike's own line; said as "himself under a spike", a no chance like busy and out of energy). An interrupt on a spike skill
  (`execution.attempts`): only a skill on the defensive side of the approved list (`worth`, `data/model/interrupt_worth.json` on the branch, the words in
  `docs/EXECUTION.md`; a missing file stops the reading), where the cast took at least `REACT_S` and the interrupt's own time (`intr_time`, R-750: a spell
  its cast time, an attack half its activation or its weapon's swing, `SWING`), the interrupter off recharge, hands free and out of his aftercast 0.2 s
  after the cast began. How long a cast took is the replay's record of it (cast start to finish), never the skill data's cast time: checked on 14 matches,
  Hammer Bash and Crushing Blow finish in a median 0.5 s (0.8 with no attack speed boost: the hit lands halfway through the swing, as
  `knowledge/attack-timing.md` says), Dismember and Bull's Strike 0.4, Protector's Strike 0.1; a 1 s spell 0.5 on a half-cast; a Mesmer's Shame 1.1.
  Development set: 6,935 plays identical, 323 Classic rows pass. Of 1,619 deaths, 715 list a missed chance (744 before): an interrupt 383 (637), a prot 746
  (788), a heal 565 (617); a monk himself under a spike 5 times, busy 2, out of energy 57. In the attempt record, interrupt chances 1,695 (3,080) and
  taken 89 (115: an interrupt on a skill off the list is no longer counted either way). Not yet done: the check on unseen matches again (a full run and
  `cases.py attempts`: `FAULT_KINDS` stands on the old reading's verdicts until then); the strip missed listed on failed spikes (R-729, R-744);
  `into_ready` filtered by R-743. Found in the review of the catalogue (scratch scripts, not the engine; each to be read through the engine before it is
  used, R-707): damage rows carry no skill (0 of 3,466 in d1e4b578); a melee hit is a crit on 23% of hits on a player standing, 52% moving at both samples,
  65% moving away, a ranged hit 13% either way (87 matches); 11% of Mind Burn and 10% of Teinai's Wind casts hit two or more players (101 matches); 41
  skills that are not attacks or instant have no cast time in `data/skills.json` (the wiki sync's fault); `intr_kind` misses Disrupting Chop, whose skill
  data lacks "Interrupt" among its causes.

- The skill tags (`data/model/skill_tags.json`, `bundle-4` 37f10b4; stage 2, R-753 to R-765), checked 2026-11-27 against `data/skills.json`, the bars
  in `data/matches/` and the catalogue, before anything reads them. Holds: 577 ids, all PvP ids, names and types as the skill data; every cast time
  equal to the skill data's, the eight it lacks at 1.5 s (R-764); the scope as stated (876 matches from 7 September to 8 November, 571 skills on 4 or
  more bars, six more); every word inside the file's own vocabulary; the twelve rulings applied, but for Twisting Fangs (Deep Wound, no "cuts
  healing"). The interrupt reach agrees with `execution.intr_kind` and catches Disrupting Chop, which the skill data's `causes` lacks (the engine's
  reading misses it today): stage 3 takes the reach from the tags and keeps `CONDITIONAL` for what is thrown on demand. Lacking for stage 3: who a
  skill lands on (a block on the target and a hex on the attacker are both "stops damage" with area "target"; the skill data's `target` is empty for
  307 of the 577); a mark for a skill that raises the damage its user takes (Rule 25: Frenzy, Frenzied Defense, Primal Rage); R-738's snares marked as
  not checked. Lacking for stage 5: which area effects stay on the ground (Chaos Storm and Symbol of Wrath are "in the area", Lava Font "adjacent").
  Not in the file though the catalogue names them: Spell Breaker, Shadow Form, Obsidian Flesh, Earth Shaker, Mark of Pain, Sum of All Fears, Teinai's
  Prison (and Dolyak Signet and Seeping Wound, which Rule 23 drops). From 1 September, where the engine's matches start, 221 skills on a bar are
  untagged (476 of 120,606 bar slots, in 265 of 1,000 matches; 25 of them on 4 or more bars): an untagged skill is counted and listed by the run,
  never a stop and never read as doing nothing (R-460). The path stands (beside `interrupt_worth.json`; keys the in-game PvP ids). The file goes into
  `cache.DATA_DEPS` once a prepared reading leans on it.

- The catalogue's stage 1, the remainder, built 2026-11-27 (`bundle-4` 4af6a49; the tag file's commit is da11306 since that day, with Twisting Fangs
  given "cuts healing"). Failed spikes (`execution.fails`, kept as `flag_cost[rid].fails`; `python3 execution.py fails <report id> [m:ss]`; words
  `say_fail`): every spike that did not kill, with the attack's miss of a kind he rules by name (`RULED_KINDS`, the strip: R-729, R-744), read by
  `chance_tests` over the same seconds as X3 (a prot on the target at the first big hit, a strip ready and in range, none from 3 s before it to 1.5 s
  after); a strip that took a prot off in those seconds is said as good play, one that came later or took no prot off is kept apart as late and is not
  listed as a fault (the record does not say it was ready at the first hit). The check's result is said beside the fault (`ruled_check` reads the last
  `cases.py attempts` kept in `attempts_cases.json`; that report now names the ruled kinds and which read backwards). A strip is told from the
  reviewed tags where a skill is tagged (`execution.tags`, `is_strip`; a missing file stops the reading): the skill data lists what a skill removes
  without saying from whom, so Wearying Strike and eight other skills that spend their user's own enchantment read as strips (3 attempt records on the
  development set). Casts caught (`execution.caught`, `flag_cost[rid].caught`; `python3 execution.py caught <report id>`; words `say_caught`; R-743):
  a cast by a backline monk (by his bar) of a skill on either side of the approved list, interrupted, where the interrupt that stopped it (the
  replay's own interrupt record: interrupter and skill) was ready, in range and able to stop that kind of skill when the cast began. The measure
  `into_ready` counts these alone. Checked against the raw record on 14 matches (R-707): all 296 interrupted casts of listed skills by backline monks
  have an interrupt row; 257 had some enemy interrupt ready at the start, 217 the one that stopped them (the others were stopped by Lyssa's Haste,
  Shame already on the caster, a Hammer Bash knockdown or an interrupt that came off recharge during the cast: not this fault). Each play's record
  names its failed spikes and casts caught (`fails`, `caught`: own and their, places in the match's lists) and `say_faults` says them (R-745).
  Development set (82 matches): 6,935 plays identical, 323 Classic rows pass; attempts and deaths as before but for those 3 records; 690 failed
  spikes, a prot on the target at 103, the strip in time at 47, missed at 7, late or no prot off at 18; 1,375 casts caught, a median of 13 a match
  (Guardian 486, Blessed Light 326, Healing Burst 302; by Power Spike 441, Complicate 298, Power Leak 209); `into_ready` on 654 plays where it was on
  4,461. No full run (R-766): `FAULT_KINDS` and the check beside the strip stand on the old reading's verdicts until the run for stages 1 to 4. Still
  read from the skill data, for stage 3 with the tags: which strips are thrown on demand (a spirit, a well or a hex that makes enchantments expire is
  "ready" today), and `intr_kind`, which misses Disrupting Chop.

- The catalogue's stage 4, built 2026-11-27 (`bundle-4` c43c85a, on the tag file's d345505; R-731 to R-734, R-741, R-749): the ledger, the pressure attempt, question 3 by attempt, the
  even 8v8's row. No full run (R-766): the cut-offs and every count below are the development set's (82 matches) and are read again at the run for
  stages 1 to 4.
  **Health in points** (`Forensics.max_health`, `health`, `sample`): the weapon set in his hands (gvg.report's figure for each set) plus 4.8 a point of
  morale or death penalty as it stood before that second (a death's own 15% is recorded at the death) less Deep Wound (a fifth, at most 100). Checked
  against the maximum in gvg.report's recaps (R-707): within a point at 84% of 2,171 recaps, within a weapon set (30 or 60) at 91%. A first reading
  (the set times 1 + morale, the death's own penalty in) was within a point at 15%: found by setting the two side by side.
  **The ledger** (`execution.ledger`, on every spike and pressure attempt as `ledger`, on every death and failed spike; words `say_ledger`): health at
  the start, what landed (hits by their players, by their NPCs, degen from every source, Deep Wound's cut), what was healed, health at the end, and
  `unread`, what the parts leave over, kept and shown (R-460). Read between two of his samples (the last at or before the attempt's first hit, the first
  at or after its outcome; his death where he died). Found on the way: (1) healing rows are heals as cast, overhealing in (a first sum left a middle
  +600 on a player healed to full): what landed is read by walking hits and heals in order from his health at the start, a heal filling him no further
  than his maximum then, the rest kept as `overhealed`; (2) Deep Wound gives its health back as it ends: without that, attempts with Deep Wound on a
  player who lived were a middle 30 to 77 over; with it they balance. The sum balances within 25 points on 64% of 1,002 spikes and within 60 on 88%
  (pressure attempts 66% and 86%; deaths by spike or pressure 92 to 93% within 60). Not in the replays: what never landed. `stopped` is gvg.report's
  recap of the death or the survived spike (`_recap`: its own second lies a middle 2.7 s after our first big hit; 1,006 of 1,034 spikes have one, 785
  of 1,778 pressure attempts), by prot, with attacks blocked; None where it has none, never nought. Its credit is small: nought on 72% of spike recaps,
  Reversal of Fortune a middle 50, Shielding Hands 45, Guardian 0 (a block is scored at 36 and Aegis, Protective Spirit and Aura of Stability at
  nothing, as section 43 found). `off_shield`: what landed off his shield set while not casting and what a shield would have stopped of it.
  As it fell: spikes that killed, a middle 465 health at the start, 554 landed, 22 healed; spikes he lived, 500, 625 landed, 535 healed.
  **The amount beside a missed chance** (R-734; `_amounts`, `Exec.per_use`, words `say_amounts`): what a cast of that skill gave that player on
  average this match, from gvg.report's summary: a monk's prot or heal as `casting.py` reads it (healing landed with Divine Favor, and prevention), an
  interrupt's worth as the damage a cast of the skill that went off did for its caster (`data/matches`; checked, R-707, on 14 matches: a player's
  total is the replay's own hits, middle ratio 1.00; skills hold a middle 55% of it, the rest plain attacks), a strip's as what the prots on the target
  stopped in that attempt (the recap). Aegis, Protective Spirit and Aura of Stability are said as not measured, never as nought (R-704 c). 1,507 of
  1,526 faults on deaths carry one. A limit to say whenever one is shown: these are averages of every cast, and gvg.report's prevention is low, so a
  prot reads as 20 to 60 where his own example was "about 300". The root reading would work out from each prot's text what it stops of the hits that
  did land (Protective Spirit's cap, Shielding Hands' cut, Reversal of Fortune's one hit, a block's half): not built.
  **The pressure attempt** (`Forensics.danger`, `death_start`, `killed_from`; `execution.pressure`, kept as `flag_cost[rid].pressure`; `python3
  execution.py pressure <report id> [m:ss]`, words `say_pressure`): a player at or under DANGER_HP (175) health at successive samples for
  DANGER_KEPT_S (1 s) or longer with DANGER_FIRE (90 in 3 s) landed on him by the enemy, hits by players and NPCs and degen that is theirs or
  nobody's. It starts at the first sample that finds him at or under the line (no earlier than the run of hits it is told from), and ends at his
  death, at the first sample above the line, or 6 s after the last thing landed (left alone); two on a player less than 6 s apart are one. Shaped as
  a spike's record (`prots_cast`, `heals_cast`, `missed` from `Forensics.chances`, the clock from its start as from a spike's first big hit, R-748).
  One begun inside a spike's own reading is that attempt going on (`after_spike`) and is counted in nothing. The cut-offs are from the data (R-741;
  `cases.py pressure <plays file>`, kept in `data/model/pressure_cases.json`, which also says whether the engine's constants still follow from its
  table). Claude's rule, his to correct: an attempt should be as dangerous as a spike, so of the lines "for a while" allows (a second or longer) at
  which a player dies within 8 s at least as often as a spike kills (33.3%), the one that holds the most deaths with no spike: 1,604 attempts, 34.9%
  dead within 8 s, 48.1% of the 1,275 deaths with no spike. Health in points beat health as a share at every line; a single sample under the line
  (no "while") holds more deaths but is ruled out by his words. As built: 1,778 attempts, 177 of them a spike going on; of the 1,601, 612 killed
  (38%), 941 escaped, 47 left alone; a middle 3.1 s. Killed: 140 health at the start, 180 landed, nothing healed; lived: 143, 91 landed, 203 healed.
  **Deaths** (R-749; `execution.deaths`, `forensics.death`): `Forensics.killing_burst` (the heaviest 2 s) is gone. A death by spike is read as before;
  a death with no spike from the pressure attempt that killed him (`kept` true); one that is neither, from the first thing the enemy landed on him
  after the replay last found him above the line (`death_start`; 2 s before the death where nothing is recorded). Of 1,619 deaths: 344 by spike, 613
  kept in danger, 662 neither. The 662 are players already hurt (a middle 232 health, quartiles 190 to 338) finished with a middle 195 landed in 1.4
  s: under the spike's 400 and too quick to be "kept". Put to him (is a burst that takes most of a hurt player's health a spike?); nothing changed
  (R-465). Deaths with no spike listing a fault: 405 (486 on the heaviest 2 s; a prot 311 from 406, a heal 269 from 300). 113 deaths have nothing
  landed in the record and mostly no recap (39 list a fault): `say_ledger` says the record does not tell what killed him; whether a fault should be
  listed there is his (asked before, section above).
  **Question 3 and the enemy's credit** (R-732, R-733): each play's record names the attempts made inside it (`attempts`, `pressure`: own and their,
  places in the match's lists). `asks_q3`: where the play's job is to kill, and on every numbers advantage from the side that has it whatever its
  call. `say_q3` lists every attempt with its sum; `credit` and `say_credit` say apart what the defence did in time (prots, heals, interrupts) with
  what was stopped and healed; `say_faults` and `say_fail` carry them. Of 2,166 plays with the job to kill, 664 made a kill attempt of either kind
  (numbers 47% of 366, splits 29% of 1,207, flag plays 25% of 453, boost plays 21% of 140): for most, the answer to question 3 starts with "no
  attempt was made". Whether that is itself a play-level fault (R-745) is his.
  **The even 8v8's row** (R-731; `execution.even_rows`, kept as `flag_cost[rid].even`; `python3 execution.py even <report id>`, words `say_even`):
  all sixteen alive in one fight (`Moments.fights`), no stand-off (R-405), JOIN_S (12 s) or longer with one missed reading allowed; the seconds
  inside a play of either team are that play's (a fight is told once), so a row is the part no play covers, itself 12 s or longer (`under` names the
  plays that took the rest). Both teams by `Exec.side` with the objective to kill, and question 3 for each. Sixteen stand in one fight for about a
  quarter of a match; a quarter of that is under no play. 74 rows in 32 of the 82 matches, a middle 24 s; 158 kill attempts and 36 deaths in them.
  "8v8" is read to the letter (his to correct: 7v7 with both runners away is no row). No decision, no card, no test (R-557).
  Development set: 6,935 plays identical to 4af6a49 (`compare.py`), 323 Classic rows pass; beside the plays only the deaths with no spike moved
  (1,127), the rest gained keys. Also mended: `cases.py execution-say` stopped on any play where a measure added since X1 stood out (no words for 23
  measures in `EXEC_SAY`; it now says the measure's own). Not done, for the full run: the chances on a pressure attempt checked on unseen matches
  (now possible: 989 lived), `cases.py attempts` and `execution` again, `execution_rows.json` (the Execution view shows none of this yet).

- His answers on stage 4, built 2026-11-27 (`bundle-4` 25047ff; R-779 to R-783). No full run (R-766); every count is the development set's (82 matches).
  **The pressure line** is his: `forensics.DANGER_HP` 225 (R-779), the second and the 90 in 3 s as before. `cases.py pressure` has 225 on its grid and
  prints what his line gives beside the rule's (`pressure_cases.json` is stale until it is run again). 1,707 pressure attempts of their own, 25% killed
  (at 175: 1,601 and 38%: a wider line holds more players who live).
  **A burst on a hurt player is a spike** (R-780; `Forensics.spikes`, which `attempts` and `killed_from` read; `events._spikes` and every reading built
  on the spikes of 400 untouched): 200 or more inside 3 s that is two thirds or more of the health the replay last found him at (`HURT_SHARE`,
  `HURT_FLOOR`), none inside a spike's own reading or in the 6 s before one, what a hex did to him left out (below). The share and the floor from the
  data (scratch table, 82 matches): at two thirds such a burst kills within 8 s 31 to 33% of the time at every floor from 100 to 250 (a spike of 400:
  33%), at half his health 19 to 20%, at three quarters 36 to 40%; the floor is half a spike, so that with the pressure line a player under about 300
  is read by one or the other. The record carries `hurt` (his health as it began). 1,034 spikes of 400 (33.3% killed) and 1,944 bursts (31.0%; a middle
  344 health and 285 landed): the bursts are two thirds of all spikes now, and many are on players near full health who took just under 400 (Men v Crew
  26:51, the Ranger: 369 on 414 of 493). Of 1,619 deaths 940 by spike (596 of them a burst), 378 kept in danger, 301 neither (111 nothing landed).
  **The even 7v7** (R-781; `even_rows`, `EVEN_N`): the largest fight with eight or seven a side, a stretch read at one number, ids `even_7v7`; the 74
  rows of 8v8 are as they were, 9 rows of 7v7 beside them (a middle 15 s: most 7v7s lie under a play).
  **Pact kills and nothing landed** (R-783; `Forensics.pact_kill`; corrected in f93fd2c): Death Pact Signet kills its caster ("The next time
  that ally dies within 120 seconds, so do you"): a finished cast of it by the dying player inside 120 s, on an ally whose next death after the cast
  is in the same fifth of a second as his own. Checked (R-707): of 104 finished casts where both died afterwards, 61 are at the very tenth. Built the
  wrong way round at first (the resurrected player read as the one the pact kills; 25047ff and 116ef1a carry that), found on his own example, 옷옷옷옷
  v cope 4:34: cope's Mesmer, the caster, dies with nothing landed as the 7 Monk he resurrected 117 s before dies. 54 pact kills among the deaths, 37
  of them deaths with nothing landed in the record (a third of the 111: the rest, 74, list no fault): the death says so and lists no fault, the
  resurrected player's death says whose it brought (`took`), the attempt carries `pact` (4; still counted as killed: to be left out of the check at the
  full run). A death with nothing landed (`nothing_landed`, 111) lists no fault.
- The catalogue's stage 3, built 2026-11-27 with the tag file (`bundle-4` 116ef1a; R-720 to R-726, R-736 to R-740, R-751, R-767 to R-778). No full run:
  no new kind is checked on unseen matches yet (Rule 29: at the run for stages 1 to 4). Plays identical (6,935), 323 Classic rows pass.
  **The tags read**: `intr_kind` (reach and on demand: Disrupting Chop in, Exhausting Assault out, R-774; an untagged skill by its text as before),
  `is_strip` (`strip_at_once`, R-773: Mark of Insecurity, Order of Apostasy, Rending Aura and Well of the Profane are no strip on demand),
  `removes_cond` (who a removal lands on), `tag_of`, `untagged` (`flag_cost[rid].untagged`; the run prints them: 10 skills in 6 matches).
  **Found on the way**: `Forensics.sdata` looked a skill up by the replay's spelling alone and missed eleven skills the replays write without
  punctuation (Protector's Strike 4,861 casts, Glass Arrows, Harrier's Grasp, Protector's Defense, Wounding Strike, Recovery, Bull's Strike: 2% of
  casts); it falls back to `common.skill_row` (id, then the plain name). The engine's `is_prot` (the skill data's causes) misses 16 skills the tags
  have stopping damage on an ally, Aegis, Life Sheath, Shield of Absorption, Aura of Faith and Spell Breaker among them, and reads Spirit Bond as a
  heal only: not changed here, it moves to the tags with the prot amounts (R-784).
  **The joins, checked first** (R-707; 44 matches, scratch scripts): a knockdown names its skill (97 of Bull's Strike; 36% of its finished casts on a
  player knock him down); a condition names none (the effect's skill field is no skill for conditions), so Harrier's Cripple is told from the hit: 58
  Cripples at a hit by an attacker with Harrier's Grasp up, 8 of them with another Cripple skill cast on him (left out); damage rows carry no skill
  and gvg.report's hints carry no attacker, so a hex's own damage is told by its amounts (`Forensics.trigger_rows`: under Empathy the caster's rows
  come as 47, 94, 141; 91% of plain attacks finished under it have one; attack skills set it off too, so its hits are counted, not the attacks); 85%
  of spells finished under Backfire have its hit; 59 of 81 spells started under Shame fail as the hex goes; the hits of one cast land in the tenth it
  finishes (4,860 of 4,968); Mind Burn hits two or more on 13% of casts, Energy Surge (nearby) on 30%, a scythe on 4% of its tenths.
  **Triggers** (`execution.triggers`, `flag_cost[rid].triggers`; each play names its own, `walked`; `python3 execution.py triggers <report id>`): 877
  rows, 10.7 a match: Empathy 312 (1,396 hits, 64,376 damage, in 13 matches), Bull's Strike 250, Shame 126, Harrier's Grasp 88, Daze left 83, Backfire
  18 (9 by a backline monk, 16 casts with Spirit Bond on: no fault). Clumsiness, Ineptitude and Diversion are read and did not occur.
  **Balling** (`execution.balling`, `flag_cost[rid].balled`; `execution.py balled`): 773 adjacent (a scythe 532, Mind Burn 118, Shell Shock 72, Death
  Blossom 38; a middle 28 on the other player; 82 with three or more hit) and 1,065 nearby (Energy Surge 795, Lamentation 266), counted apart: his
  rule names adjacent damage, put to him.
  **On every kill attempt** (`execution.tagged_parts`; words `say_parts`, in `say_attempt`, `say_pressure`, `say_fail` and a death): `stance` (76
  attempts with Frenzy, Frenzied Defense or Primal Rage up while hits landed; the share the skill added from its text, a third to a half by rank),
  `walked`, the missed kind "deep wound" (348 attempts, 121 deaths: `Forensics.chances` with `removes_cond`, Deep Wound still on him at the outcome);
  on a spike `into` (441: Guardian 229, Shield Guardian 166, Mirage Cloak 26, Aegis 22; 24% killed against 28%), `deep_wound` (carried in reach at
  2,388 spikes, on him in time at 1,116: 35% killed against 30% without), `elsewhere` (511: 25% against 27%). These three are whys, not faults.
  **Not read**: wards (no record but the cast: 18 Ward Against Melee in 44 matches) and spirits (no position in the replays; no Shelter, Union or
  Displacement in the 44); Rule 11 (R-726) stays read over the play. **For the full run**: every new kind once on unseen matches; pact kills out
  of the check; `cases.py pressure` again; the hurt bursts change who is a spike target in `cases.py attempts` (the situation model holds health).

- What a missed prot would have stopped, built 2026-11-27 with R-787, R-789 and R-790 as one bundled change (`bundle-4` 97bac17; R-784, R-785, R-791 to
  R-793). No full run: no kind is checked on unseen matches yet. Plays identical (6,935), 323 Classic rows pass.
  **A hit** (`Forensics.hits_on`): gvg.report writes the parts of one hit as rows of their own (an attack skill's added damage is a row that ignores
  armour beside the blow), so the rows of one source on a player in one tenth are one hit, with the part that respects armour kept. The replays name
  no skill on a hit, so it is told as an attack, a spell or neither from what its source was doing: an attack skill is a cast in the record and starts
  no attack (found here: a third of the warriors' hits read as neither until it was joined); a critical row; an armoured hit after an attack he began in
  the 3 s before; an NPC's armoured hit; a damaging cast finished in that tenth, or one on this player in the 1.5 s before (a projectile). Checked
  (R-707) against gvg.report's recaps, which name the skill, on the 82 matches: 2,056 recaps, attacks 303,000 by its skills against 308,000 here, spells
  432,000 against 441,000, 7% told as neither; the share that is attacks agrees within 10 points on 77% of recaps (middle gap 3.6 points).
  **The rules** (`forensics.PROT_RULES`, one line a skill as he approved them, R-791; `prot_rule`): block, full, next, each, fatal, share, cap, ramp,
  armor, flat, bond, onhit, blind. `is_prot` reads it: Aegis, Life Sheath, Shield of Absorption, Aura of Faith, Spell Breaker and Shield Guardian (cast
  on nobody: a prot on the players in earshot of its caster, `Forensics.cast_on`) are prots now, Spirit Bond a prot and no longer a heal; wards, spirits,
  Aura of Stability and Vital Weapon are out; Protector's Defense, the shouts and chants are never a chance; an untagged skill (Xinrae's Weapon, Life
  Bond) is read from the skill data as before and has no amount.
  **The amount** (`execution.prot_would`, in `_amounts`; the old figure kept as `gave`): the sum of the attempt walked again, event by event as `ledger`
  lays it out, once as it was and once with the prot on him from the second it would have landed (the chance's moment and the cast time, Daze doubling
  it) to the skill's end: `stopped`, `healed` (as far as he had the health missing), and on a death `lives` and `left` (above nought at every moment to
  the end: told only where the parts explain the death to within 60, else None). Technical choices, Claude's: the caster's rank from gvg.report, else
  the middle rank of those who carry the skill in the matches that count (`usual`; 1,285 of 6,390 amounts: a third of the monks have no Protection
  Prayers rank); a set that lengthens enchantments adds a fifth; a Monk spell's cast heals by its caster's Divine Favor (3.2 a rank: about 40), counted
  in `healed`; a block is its chance times that attacker's average attack this match (the ruling's words), never more than the hit; armour as if no
  other bonus were on him. On 24 matches the blocks by the average come to 11,431 over 444 chances, on the hits that landed 13,075 (14% more: a spike's
  hits are bigger than the average), and 7 of 98 deaths change from not enough to enough: put to him.
  **What moved** (82 matches, before and after): a prot cast in time on 1,697 spikes (893); missed prot rows 1,439 on spikes and 1,451 on pressure
  attempts (2,100, 1,892: a monk who cast Spirit Bond or Aegis did prot); missed heals 499 and 465 (1,374, 1,342: 1,847 of the 2,716 old missed heals
  were Spirit Bond alone); deaths with a prot fault 387 (426), a heal fault 245 (337); faults 1,769 (2,003). A prot up as the spike began on 898 spikes
  (457), so the strip missed on 123 (46) and 98 failed spikes carry that fault (32): Spirit Bond, Aegis and Life Sheath are prots to strip. A cast,
  mean stopped and healed: Guardian 27 and 36, Shield Guardian 17 and 16, Spirit Bond 0 and 120, Reversal of Fortune 40 and 78, Shielding Hands 44 and
  39, Aegis 99 and 33, Life Sheath 43 and 72, Aura of Faith 57 and 73, Protective Spirit 54 and 40. Of 378 deaths with a prot fault: on 251 a prot
  would have outlasted what landed, on 35 none, 92 not told; where it does the middle margin is 74 health and a third (265 of 815) are under 50, many
  by the Divine Favor heal alone (Men v Crew 4:05, the Prot: 23 over, Guardian stops nothing and its cast heals 45). The reading ends at the death:
  what would have landed after is in no record. Put to him.
  **A pressed monk** (R-790, R-793; `Forensics.chances`, `pressed`): 250 or more on himself in the 2 s before: 9 rows, 4 on deaths.
  **Balling** (R-787): a cast that reaches nearby foes is a fault as the adjacent is (1,065: Energy Surge 795, Lamentation 266); a cast that reaches
  foes in the area is read and none hit two players; an effect that stays on the ground is never balling (R-793).
  **Casts caught** (R-789, R-793; `execution.caught`, `caught_by_player`): every player's, as context for the report (`flag_cost[rid].caught_by_player`:
  3,555 on the 82 matches; the backline monks' 1,375 as before, 2,180 by others, 165 non-monks caught five times or more in a game); a fault is a
  backline monk's inside the kill attempt that killed a player of his team, his own or one for him, set by `deaths` and said on that death (114 casts
  on 113 deaths); a play's `caught` holds the faults alone and its row says none; the measure `into_ready` counts what it did.
  **For the full run**: prot and heal are new kinds now (the prot test and Spirit Bond moved): checked again on unseen matches with the rest.
- A monk's own chance on himself, and taken means landed, built 2026-11-27 (late afternoon) as one bundled change (`bundle-4` 3111449; R-794 to R-798). No
  full run: Opus's run at 97bac17 does not hold it, so prot, heal and the Deep Wound left are read again at stage 5's full run.
  **Found** on his question of why Guardian's Divine Favor was the answer to the Prot's death in Men v Crew at 4:05 (five spells from 4:04.3 to 4:05.7,
  563 on 540 health): `Forensics.chances` read "in reach" as `dist(h, tgt) or 1e9`, and a monk's distance to himself is nought, so no monk's own prot
  or heal on himself was ever a chance. There the Prot had Spirit Bond ready with his hands free for a second and began Blessed Light a second after
  the first big hit, cut off by his death; the 8 Monk's Guardian (nothing blocked, 45 healed by Divine Favor, 22 over) was the only row.
  **His own chance** (R-796; `chances`, the row's `self`; `forensics.can_self`): the spiked or pressed monk is read as any other monk on the same clock
  (`REACT_S` after the first big hit, then the cast: Spirit Bond lands 0.45 s after it), with the skills that can be cast on their own caster (the
  skill data's target is not "other allies", its words not "target other": Infuse Health, Heal Other, Dwayna's Kiss and Aegis are out); the guards
  for a monk under a spike or pressure (R-747, R-790) were already written for another player only. `prot_would` counts Divine Favor on his own cast
  (a targeted Monk spell heals its target, an untargeted one its caster: Shield Guardian). The same reading gives a removal of Deep Wound from himself.
  **Taken means landed** (R-797; `forensics.outcome`, `landed`, `Forensics.taken_in_time(.., end)`, `Forensics.begun`; `chance_tests` and X3's own
  `taken` in `cases.py`): a kind is taken where a cast of it on him, begun in the seconds a chance is looked for, finished, and where he died finished
  before he died. `prots_cast` and `heals_cast` say how each cast ended: the record's finished, cancelled or interrupted, or "after he died"
  (`forensics.LATE`). A death keeps `begun` ([kind, skill, seconds after the start, how it ended]) for a kind not taken, said as "Begun on him in time
  but never landed". The monk who began the cast is still skipped for that kind (he acted): whether he had an earlier moment is put to him.
  **What moved** (82 matches, before and after; 6,935 plays identical, 323 Classic rows pass): deaths with a prot fault 525 (387), a heal fault 344
  (245), faults 2,137 (1,769); 209 deaths carry a row on the dying monk himself (a prot 154, a heal 96; on 98 one of his own prots would have outlasted
  what landed: Guardian 105 rows, Shield Guardian 89, Spirit Bond 66, Blessed Light 52, Reversal of Fortune 42). A prot taken on 306 deaths (408), a
  heal on 256 (359); 192 deaths have a cast begun that never landed (118 heals, 113 prots: 126 cancelled, 95 interrupted, 10 finished after he died).
  Spikes with a prot in time 1,581 (1,697): killed 15.3% where it landed (19.1% by the old reading) and 50.5% where it was missed (47.5%); a heal
  13.8% (17.9%) and 58.9% (60.4%). Pressure attempts: a prot 15.9% (17.8%) and 34.0% (30.4%); a heal 15.1% (17.6%) and 42.9% (38.0%). Missed prot
  rows 1,709 on spikes (270 his own) and 1,871 on pressure attempts (420); missed heals 652 (153) and 619 (154); Deep Wound left 289 (58) and 295 (72).
  Of 384 deaths with a prot fault told, a prot would have outlasted what landed on 343, none on 41 (141 not told). R-798: Guardian keeps a player
  alive by Divine Favor alone on 29 of 1,491 deaths (29 to 45 healed, 1 to 45 over), kept as built.
- Too late, built 2026-11-27 (`bundle-4` 6ebb141; R-801, R-802). `Forensics.chances(.., died)`: where the player died at `end`, a monk whose cast of that
  kind on him was cut off by the death (cancelled within `CUT_S`, 0.3 s, of it, or finished after it) and none of whose casts landed is read for a moment
  before the cast he did begin at which that same skill, cast then, would have landed, by the reading of any chance: a chance row with `too_late` (the
  second he did begin it), said "Too late by <team>"; where there is no such moment he gets no row and no "no chance" (he acted; the cast is in `begun`,
  which now holds every cast on him to the death that never landed). An interrupted cast is never this (R-789). The reaction stays `REACT_S` 0.2 (R-801).
  On the 82 matches (6,935 plays identical, 323 Classic rows pass): 99 rows on 87 deaths (59 heals, 40 prots; 13 the dying monk's own; Blessed Light 26,
  Infuse Health 20, Spirit Bond 8), begun a middle 1.3 s after the start where 0.2 s was open. Deaths with a prot fault 539 (525), a heal fault 389
  (344), faults 2,236 (2,137). Spikes killed 51.4% where a prot was missed and 62.6% where a heal was (15.3% and 13.8% where it landed).
- Stage 5, the readings from positions, built 2026-11-27 (evening) as one bundled change (`bundle-4` f2b8796; R-803, R-804; `execution.positions`,
  `position_parts`, `place_at`, `followed`, `area_hits`, `say_position`, `say_place`; `cases.py positions`). No full run: Opus's is wanted (HANDOFF).
  **Two records.** `flag_cost[rid].positions`: the faults tied to no kill attempt, listed on the play's row (R-745; each play's `positions`, own and
  their): Flail lock, standing in area damage, should have kited. On every kill attempt and death: `place` (too deep), `followed` (monk following),
  `stood` (his own rows inside it), `snared` (the attack's frontline, a why) and `crits_moving` (context).
  **Flail lock** (R-724): a Flail carrier's hits land with him a middle 115 from his target, 76% within 250, flat beyond (hits told as attacks at 600
  and more are 8%: wrongly told hits, not reach), so melee reach is 250 (`MELEE_R`, R-741). Read every half second from the nearest position sample:
  a stretch of more than 2 s with no living enemy player or NPC inside 250. 163 rows, 840 s, on warriors in 5 of the 82 matches (433 stances).
  **Standing in area damage** (R-735, R-803): the skills whose damage stays at a spot are the tags' `lasting` ones that add damage on a foe, traps
  left out; how long each lasts and its beat are read from its own text (`area_skill`: a text with no length stops the reading). A hit names no
  skill: a cast's hits on a player are its caster's rows on him a whole number of beats after the cast finished (to 0.25 s; they fall on the same
  tenth, cast after cast), of the one amount most of them share, plus the rows for less on that very tenth (a prot cut the hit). Read from two such
  hits; a fault from the third, the row carrying how many counted hits found him knocked down or slowed (context, R-803). Cast on the set: Symbol of
  Wrath 112, Lava Font 89, Ray of Judgment 72; 44 rows in 6 matches (Symbol of Wrath 35), 82 counted hits, 3,064 damage; knocked down on 7 rows.
  Checked (R-707): gvg.report's recaps cannot check it, for they put the caster's other spells under the area skill (18 recap rows name one, none
  agrees; "Symbol of Wrath 258 in 5" is two hits of 40, two of 20 under a prot, Word of Censure's 130 and Castigation Signet's 28). Checked on the
  raw rows instead: the hits fall at the cast's end plus 1, 2, 3 s, at 40 or 42 each, the skill text's figure at ranks 15 and 16.
  **Should have kited** (R-746, R-792, R-804): a hit by a melee attacker (a Warrior, Dervish or Assassin within 250) on a player not of the
  frontline, standing still (idle or attacking at the position samples either side: `_states`), not casting, not knocked down, another melee hit
  having landed on him 0.2 to 3 s before (he had seen it: R-716's reaction, the slowest swing); never while the attacker has Bull's Strike off
  recharge or Harrier's Grasp up or off recharge. Hits no further than 3 s apart are one row. 878 rows in 67 matches, 1,401 hits, 54,052 damage;
  565 rows are one hit; Paragons 149, Prot monks 144. On the attempts it reads backwards (below): put to him (R-744).
  **Too deep** (R-741, R-804; `place_at`): his team in the fight is he and the team mates in a fight with an enemy he is in a fight with
  (`Moments.linked`); the line runs from the middle of those team mates to the middle of those enemies; the front line is the most forward team
  mate who is no backline monk (a monk who has followed does not make the front line). `past` is how far he stands beyond that player at the first
  big hit. No front line where only monks are with him (`alone`: 412 of 4,685 attempts; a decision, not execution). The cut-off is the one distance
  that best tells the attempts that kill from those that do not (two rates against one, the largest gain in likelihood, 30 attempts either side:
  `cases._best_cut`): 1,200 for players who are no backline monk (225 attempts at or past it, 47.6% killed; 22.4% short of it; 1,200 to 1,550
  leaving each tenth of the matches out), which is a cast range: at 1,200 past the front line no monk behind it reaches him. 158 of 1,619 deaths
  are too deep; 108 of them list no prot or heal fault. A backline monk is read on the same cut-off.
  **Monk following** (R-804; `followed`): a kill attempt on a backline monk who stands 400 or more past his front line, behind a team mate who is
  1,200 or more past it (the front line told without that player), within a cast range of him. The 400 is the same rule on the attempts on
  backline monks by the monk's own distance past the front line (319 at or past it, 50.8% killed; 24.4% short; 350 to 400 leaving each tenth out).
  71 attempts (55 of the 4,685 not carried on from a spike), 18 deaths.
  **The snared frontline** (a why, R-804): each frontline attacker in the fight with the target who was Crippled or under a slowing hex (the tags'
  `slows` on a foe, R-738's left out) and out of melee reach of the target for a second or longer of the attempt. 305 attempts.
  **Crits while moving** (context, R-746): critical melee hits on the target with both samples moving: 1,070 hits on 722 attempts.
  **Checked once on the development set** (`cases.py positions`, section B; with it against without, then on the spikes like with like as stage X3):
  too deep 51.7% killed against 27.9%, like with like +5.2 points (-0.2 to +10.2), 6 groups of 10: fails, so a why and no fault yet
  (`POSITION_FAULTS`, R-713); monk following 30.9% against 29.4%, -6.4: fails; standing in area damage 22 attempts, too few; should have kited
  19.6% against 29.8%, -9.4 (-14.7 to -3.5): reads backwards; the attack's frontline snared 21.6% against 29.9%, -9.6 (-16.0 to -4.5), 9 of 10:
  passes as a why of a failed kill. **Run** (82 matches, f2b8796 against 6ebb141): 6,935 plays identical, 323 Classic rows pass, no record differs
  but the new keys (`positions`, `place`, `followed`, `stood`, `snared`, `crits_moving`); deaths with a prot fault 539, a heal fault 389, as before.
  **Not built**: the three readings the match report asks for (Shadow Shroud on the target, their monks disabled at the spike itself, the weapon
  set the target was in: parked with the report, `docs/OPUS.md`); X4's sentences in `cases.py` do not pass the stage 3 or stage 5 rows to `say_faults` yet (X4 again, after the full run).

- **The bundled change after the full run, and the match report's readings** (2026-11-27, evening; `bundle-4` 0a8cca9; R-805 to R-810).
  **Out**: should have kited (withdrawn, R-806), standing in area damage (set aside, R-807: `area_hits` and `area_skill` are kept, nothing
  reads them), an attacker on another target (dropped, R-809). `positions` now holds Flail lock alone; the attempts and deaths lose `stood`
  and `elsewhere`. **Cut-offs** from the 564 counted matches (the full run at f2b8796): `DEEP_PAST` 1,000 (1,000 or 950 leaving each tenth
  out), `FOLLOW_PAST` 450 (not steady: nought in five tenths; told only behind a too-deep player, R-808). The development set's own rule still
  gives 1,200 and 400, so `cases.py positions` says "not the rule's cut-off on this file" there: the full run is the one that sets them.
  **Spikes and bursts apart** (R-805): the record's `hurt` tells a burst on a hurt player; `chance_tests` reads the interrupt on spikes only,
  `deaths` lists it on a spike only, and the death is said as a spike or a burst. The interrupt is a fault on a spike by his ruling
  (`FAULT_BY_RULING`): `cases.py attempts` shows its check beside it and no longer stops on it. Of the set's 940 deaths by damage inside 3 s,
  344 are spikes and 596 bursts; deaths with an interrupt fault 371 to 155.
  **At the spike itself** (the catalogue's section B; `Forensics._disables`, `disabled`, `barred`, read inside `ready` and `chances`): a skill
  the enemy disabled is not ready (Power Block: the interrupted skill and its attribute's on his bar; Power Lock, Complicate: the interrupted
  skill; Blackout: all, its target as `pressure.py` reads it; Signet of Humility: his elite; Diversion: the skill used as the hex ended, for its
  recharge and the added time; each for as long as the skill's text gives at its caster's rank). No enchantment is a chance on a target under
  Shadow Shroud (a party-wide prot, `PROT_RULES`' `party`, is left a chance: Claude's reading); no spell from a monk under Shame. A monk left
  with nothing says so (`barred`, `disabled` on the row; "Not a chance" on the death). `ready` is the one reading, so interrupts and strips
  take a disabled skill as not ready too (the trigger rows of two matches moved). On every attempt: `set` (the set he held at the first big
  hit, `has_shield`), `shroud` (its seconds from the first big hit), `monks` (each of his monks knocked down, Dazed, with prots or heals
  disabled, or under Shame or Diversion), `landed` (the prots and heals that landed for him, a heal with the healing the replay records),
  `dw` (Deep Wound on him: none, left, off), and `into` gains `attacks` and `spells` (a block is said and tested only against a spike with
  attacks in it). A chance carries the monk's `energy` (least and most, gvg.report's model).
  **What a missed chance would have done, and by when** (`saves`, `interrupt_saves`): the sum of the death walked again (`_sum_events`,
  `_sum_walk`, the ledger's own events) with the cast added at each tenth of a second from the monk's first chance to the death: a prot by
  `prot_would`, a heal by what a cast of it gave him on average this match, an interrupt by what one cast of the skill did. Lives, short by
  how much, and the latest start that still saves him; not told where the sum does not balance (`WOULD_BALANCE`). On the set: prots 1,107
  would have saved, 217 not enough, 429 not told; heals 494, 42, 208; interrupts 245, 72, 65.
  **The sentences** (`death_lines`, the match report's wording): the head (what killed him, the damage from the first big hit to the death,
  what was missed by kind), the sum, what applied at the spike, his own play, a line for each missed chance, what was done for him, what was
  no chance. `review.py execution` passes the trigger rows; `cases.exec_say` passes the stage 3 and stage 5 rows to `say_faults`.
  **Checked once** (`cases.py attempts`, section H, in the engine now: stance, block, immunity, Deep Wound in time, Deep Wound left, Shadow
  Shroud, a monk stopped, the interrupt on a burst, and prot, heal and Deep Wound on the times a player was kept in danger). On the set: Deep
  Wound left with a removal ready passes (58.2% killed against 30.7%, +29.5); Deep Wound not on him in time passes as a why (-6.5); a block
  reads backwards (+5.6, 4 of 10); the stance fails; a monk stopped +5.7 (8 of 10); the interrupt on spikes alone has 12 taken (too few on
  the set). The full run decides each.
  **The full run at 90223ed, and two tests set right** (2026-11-28; `bundle-4` d019748, `cases.py` only, no reading changes; plays and moments
  identical to the digest on all 564). The interrupt on a spike passes (168 taken; -16.1, 10/10). A block read backwards (+2.7, 2/10) and the
  stance failed (+1.8, 5/10) for faults of the test, not of the readings. A block: the situation held level counts the prots on him, and Guardian
  is one of them, so a block was set against the other prots (Spirit Bond, Shielding Hands, Protective Spirit), not against no block. Left out of
  that count (`_x3_situation`'s `leave`; the other prots still held level) it passes: 22.1% killed against 33.8%, -5.2 (-6.8 to -3.5), 10/10; no
  other prot on either side -7.3, 10/10. By how much of the spike was attacks (scratch, not in the report): a third or less -0.9 (no difference),
  a third to two thirds -5.1, two thirds or more -8.5 (10/10). The blocks: Guardian 1,389, Shield Guardian 813, Swirling Aura 104, Protector's
  Defense 62, Mirage Cloak 45, Aegis 35. Spell immunity the same way: 37 rows, +1.6, no answer. The stance: a warrior in Frenzy was set against
  every player who is no monk, and those who carry it are killed less whatever they do (the target's armour class added to the situation moves it
  to +3.9 only: not the whole of it). Set against the same players in the same matches out of a stance (`same`): 282 at 24.1% killed against 351
  at 19.1%, +11.8 (+7.0 to +17.1), 10/10. From the sum: 68 deaths with one up (Frenzy 221 attempts, Primal Rage 49, Frenzied Defense 12, the
  last on monks); the skill's own share at the least 100 or more on 48 of them (middle 126). The plain test's figure is kept beside each
  (`against_all`). Tried the same way and not changed: too deep (+5.3, 9/10 against the same players; +4.4, 8/10 among players seen both ways:
  not steady) and monk following (+11.4, 8/10): the situation already holds his distance from his group. The burst's interrupt (H2) moved to
  +7.9, 8/10 with one interrupt a player: one group short; not a fault by R-805.
  **His answers and the four that still failed** (2026-11-28, later the same morning; `bundle-4` 9ff24ab, one bundled change; development set:
  plays and moments identical to the digest, 323 Classic rows pass). R-831: a block is said, and tested, only where more than a third of the
  spike is attacks (`BLOCK_SHARE`, `into_block`; 305 spikes of the set's 389 keep the line; the check on those -6.4, -8.1 to -4.7, 10/10). R-832:
  a stance that blocks (`STANCE_BLOCKS`, Frenzied Defense) keeps `spells`, what spells landed while it was up (`Forensics.hits_on`'s class, a
  signet or touch skill with them), is a fault only where that is more than nought, and its own doing is half of it (9 of the set's 10 rows are
  faults still). R-834: too deep and monk following are kept on every record and said nowhere (`POSITIONS_PAUSED`: `say_place`, a death's
  "Positioning:" lines, `cases.py positions` sections A and B; 195 deaths of the set too deep, 25 followed). Main's rows written again (four
  lost a Positioning line).
  Why each of the four fails (evidence rows in section H; section G and `chance_tests` as they were, his rulings to come). **The strip**
  (+0.1): the test asks for a prot on him at the first big hit, so a strip before it that left no prot (395 attempts, 35.4% killed) is in
  neither group, and where a prot was left the count held level is already one lower. With the prots before the strip held level: a prot
  stripped before the first big hit 31.0% killed against 23.5% (prots on him, a strip ready, none in time), +6.8 (+2.8 to +11.0), 7/10: the
  range clear, two groups short; in the 1.5 s after it 23.6%, +0.3: nothing. After a strip in time a prot landed again on 1,164 of 1,955
  (8.0% killed where it did, 52.0% where none did). Not yet changed: `chance_tests` still leaves the 395 out of "done in time" (an engine
  fault, with his answer on R-729's "or during it"). **Pressure on their monks** (-1.1): an interrupt can only land on a monk who casts; on
  4,582 spikes the monks began nothing for the target (63.2% killed), and those sit in the missed group (1,280 of 5,168) more than in the
  taken (418 of 2,153). Read by what it stopped: a prot or heal for the target interrupted 34.3% killed against 20.8% (cast for him, none
  interrupted), +10.0 (+8.0 to +11.9), 10/10; against those with an interrupt of the attack's ready +6.0 (+4.0 to +8.3), 8/10 (scratch); a
  monk knocked down +6.0, 10/10; Dazed +10.1, 8/10 (155). **Shadow Shroud** (+3.6): no enchantment can be cast under it (a prot landed in time
  on 20% against 48% of the same teams' other spikes), so the prots held level take its work out; with none held level and against the same
  teams in the same matches 40.3% against 36.6%, +10.1 (+5.5 to +15.6), 8/10: 315 spikes by 38 teams, too few matches for the groups bar.
  **Spell immunity** (37 rows): every one is Aegis (PvP: 1 to 3 s, no hostile spell can target him and attacks on him fail; no Spell Breaker
  or Obsidian Flesh on a bar). 7,065 Aegis casts in the stored matches against 41 attempts with it up: a spike it stops lands nothing, and an
  attempt is 400 landed, so the check sees only the spikes that got through (gvg.report credits it 0.6 prevented a cast for the same
  reason). Needs a reading from the casts aimed at him while it was up (a spike thrown, not a spike landed): not built, put to him.
  **R-835 to R-838 built** (2026-11-28, midday; `bundle-4` 59c47b0, one bundled change; Fable's full run at it: plays and moments identical
  to the digest on all 564, 323 Classic rows pass on the set, `attempts_cases.json` from that run).
  **The strip that matters** (R-835; `strip_effective`, in `chance_tests`). Each strip on an attempt is kept with what it took (`strip.rows`:
  s against the first big hit, the enchantment, the strip, a prot, a heal by `is_prot` and `is_heal` on the enchantment's own skill data via
  `ench_off`, and whether the strip deals damage, `STRIP_HITS`). On the set 1,780 strips: Shatter Enchantment 1,085, Shatter Storm 316, Drain
  Enchantment 115; taken most: Patient Spirit, Spirit Bond, Shielding Hands, Guardian. The check, each part against its own like. Before the
  first big hit (section G's row; against a prot on him before, a strip ready and none): 715 at 32.3% killed against 648 at 23.5%, +5.8 (+2.1
  to +9.4), 7/10; spikes alone +9.4 (+2.8 to +17.1), 8/10; bursts +2.2, 6/10. During it: a strip can only take what the monks put on, so it
  is set against the attempts where an enchantment prot or heal landed on him during it and stayed (`during`, `took`): spikes 19.3% against
  14.2%, +8.3 (+5.8 to +10.5), 9/10; with a damaging strip +7.7, 9/10; with a strip dealing none +14.5 (116 rows), 9/10; bursts +3.7 (+2.4 to
  +5.1), 9/10. Set against a prot on him before and no strip (the first try) a strip during read nought on spikes and backwards on bursts:
  the wrong like, the same fault as the block's. Left for his word: a strip dealing no damage during a spike is not counted (it reads
  strongest), and a damaging strip counts whatever it took (1,586 spikes so counted, 1,083 of them took a prot or heal).
  **The attack's good play on their monks** (R-836; `monks_stopped` kept as `good`, `monks_at`'s `down_by`; "Enemy good play:" on a death).
  A prot or heal for the target stopped: 252 on the set (Power Spike 74, Complicate 30, Shame 28, Power Leak 21); +10.0, 10/10. A monk in
  reach down as the spike lands (his words: casting or not): 598 attempts, +8.1 (+4.8 to +11.8), 7/10; any of his monks knocked down from 3
  s before to 1.5 s after: 2,496, +6.0, 10/10. Not on a death read from a pressure attempt (no `good` there yet).
  **The spike thrown** (R-837; `thrown`, kept as `flag_cost[rid].thrown`; `say_thrown`; `python3 execution.py thrown <report id> [m:ss]
  [aegis]`; `cases.py attempts` section J). Checked against the raw record first (R-707, 16 matches, 303 Aegis): of the spells and hexes
  aimed at a player that end while Aegis is on him 46 of 56 stop with no interrupt recorded, against 13 of 320 in the 3 s either side; a
  signet lands, an attack skill is recorded finished. The record's end of Aegis is gvg.report's simulation (4 s on 125 of 163, 6 s on 14): read
  no longer than 3.6 s from its start (`AEGIS_MAX_S`). Pricing a cast from gvg.report's summary or from the replay's own hits agrees. 6,478
  thrown in 508 matches, 25.5% killed; 71% landed as a kill attempt, and of the landed spikes of 400 about 55% are found thrown (the pricing
  is the low side: a skill that never did damage in the match has no price). Aegis on him as the first skill lands: 21 (a spell cannot be
  begun on him). Aegis coming during it: 347, 1.7% killed against 29.0% with neither Aegis nor a block (-27.1, 10/10 like with like, which
  flatters it: Aegis can only come to a player still alive); against the plain spikes whose target was still alive when it came 22.4% died
  after that moment (scratch: the record keeps no time of death; add it). 315 spells stopped on Aegis in 196 of the 368 spikes. A block at
  its start, no Aegis: 1,083, 16.8% against 29.0%, -10.3 (-12.5 to -8.1), 10/10 (on the attempts -6.4: the spikes a block stops outright
  are counted here).
  **Found, not fixed**: the casts in a death's "Success:" line come in a different order from one run to the next (the same sentences): five
  rows of main's view changed so. (Fixed at f7165b1, below.)
  **The win chance over the match** (`Moments.position_series`, kept as `flag_cost[rid].series`; `cases.py winchance <file> --json <out>`):
  the position every 10 s and at each death, priced by the price of a result fitted without the match's group. A death's change is the
  price of its death penalty alone (15%, to the floor of 60%, by the game's rule: the replay writes the new figure late on one death in
  eight): -2.0 points on average on the set. For the match report's exporter; the output is not kept in the repository.
  **The full run** (`moments.run_all`): each match is written to a file of its own (`<out>.parts/`) and the plays file put together from
  them, so the parent holds nothing (82 matches are 120 MB as written; 564 held at once was what killed a worker). A run that stops goes on
  where it stopped (same engine, by a hash of the code); a worker that dies stops the run with an error (R-460). Workers peak near 150 MB.
  **Run** (82 matches, 0a8cca9 against f2b8796): 6,935 plays and 5,420 records identical, 323 Classic rows pass; beside the plays only
  `attempts`, `pressure`, `deaths`, `fails`, `positions`, `series`, the trigger rows of two matches, and the plays' places in `positions`
  differ. Deaths with a prot fault 539 to 524, a heal fault 389 to 368 (disabled skills, Shadow Shroud, Shame), Deep Wound 168 to 159; too
  deep 158 to 195, monk following 18 to 25 (the lower cut-off). 66 chances barred by a hex and 40 disabled on deaths; Shadow Shroud on 25
  deaths, a monk stopped on 198. **Not built**: an interrupter's energy (the model reads monks and the midline only); Shadow Shroud and the
  monks' state as missed chances of the attack's; the weapon set he swapped to.

- **His marks of Men v Crew actioned (2026-11-27, night; R-811 to R-820; `bundle-4` c477e8c).** `Forensics.chances` rebuilt at
  the moment of a chance: a hex or a disable is said only of a skill the monk could otherwise have cast then (in reach, in time, off
  recharge, hands free); where none applies and he was in reach with a skill off recharge, the row says there was no time (`no_time`:
  `fast`, the time to see the hit and the cast longer than the player lived; `hands`, a cast begun before he could have seen it, and
  its aftercast). Shield Guardian is an enchantment like any other under Shadow Shroud, and `cast_on` no longer counts it on a
  Shrouded player. `_disables` reads nine more skills by their own text (`DISABLE_ON_INTERRUPT`; after the skill's recharge where the
  text says "additional"; Power Lock and Complicate are left as built), Diversion bars every skill (`barred(..., "skill")`), and
  Arcane Thievery and Arcane Larceny are kept apart (`thieved`: the record names no spell). `intr_time` adds `ARROW_FLIGHT_S` 0.2 to a
  bow interrupt. On an attempt: the interrupter's energy (no chance where gvg.report's model has him out), who landed an interrupt
  (`by`, `done`), every spike skill cast (`spike_casts`), and a player who landed one or threw and missed comes off the other casts'
  chances. `prot_would` counts Divine Favor only where the walk shows the prot itself healing. `monks_at` lists only monks in reach,
  with the seconds each hex or disable was on them. `death_rulings` (on the death alone, so the checks of `cases.py attempts` on
  attempts are untouched by it): the prots and heals that fall short dropped (`short`), two skills a monk, `in_reach`, `nearest`,
  `too_fast`, the set's `held_s`, `shield_saves`, `stripped` (with `prot_would` from the strip for a prot), `hurt_before` (hits from a
  cast aimed at a team mate, inside `AREA_LAG_S` 1.2 s of it, on a burst). `death_lines` rewritten in the match report's wording.
  Tested on his fifteen marks (each comment answered in the row as rebuilt) and the development set: 6,935 plays and the moments
  identical to the digest of ccd0a55, 323 Classic rows pass. Of 1,619 deaths: a prot fault on 455 (524 before), a heal 358 (368), an
  interrupt 147 (155); 112 with a prot or heal dropped as short; too fast 57; no other monk in reach 608; an enchantment stripped on
  390, a prot on 149, of which 65 would have saved him had it stayed; hurt before a burst by area damage 20; an interrupt landed 6,
  thrown and missed 16; Arcane Thievery on a monk 25. **Found, not built**: balling (Rule 7) reads the hits of one cast on several
  players inside 0.15 s of one another, but the record sets Invoke Lightning's hits on its other targets half a second apart each
  (Men v Crew 1:57.7 to 1:59.6), so they are missed: to be measured on the development set before `BALL_S` is touched. "Sufficient
  energy" of an interrupter is the model's where it reads him; Lyssa's Assault has no length in its text the parser reads.

- **His marks of RACK v hdm and Men v NwAy actioned (2026-11-28; R-822 to R-830; `bundle-4` 805b894, then 90223ed on his rulings).** Ten deaths of RACK v hdm
  and 12 of Men v NwAy's 21 marked (14 correct, 5 partly, 3 incorrect), filed in the review key (set x1).
  **Cast times** (`forensics.cast_s`, the one reading): the skill data's activation, and the tag file's `cast_s` where the skill data has none
  (nine tagged skills, each 1.5 s: Shield Guardian, Ethereal Burden, Lava Font, Ice Spikes, Vapor Blade, Kitah's Burden, Smoldering Embers,
  Sum of All Fears, Obsidian Flame; a skill with neither stays instant, and no interrupt reads differently). Until now `_act("")` read them as instant, so Shield Guardian was a chance inside a 0.6 s burst and left
  no aftercast. Checked against the replays (R-707): of 4,092 finished Shield Guardian casts on the development set 2,775 took 1.4 to 1.6 s
  and 1,261 a half cast of 0.7 or 0.8. `has_aftercast`, `chances`, `prot_would`, `saves`, `intr_time` and the strips read it.
  **A heal that comes later** (`forensics.heal_after`, from the skill's text): Patient Spirit heals 2 s after it lands; Vigorous Spirit and
  Watchful Intervention only as something sets them off. In `saves` such a heal gives its caster's Divine Favor with the cast (his rank in
  gvg.report's record; nothing where it has none) and the rest of what a cast of it gave on average only where it comes before the death
  (`later`, `after` on the amount); `_sum_walk` takes a heal in parts. Checked (R-707): on the set Patient Spirit's later heal row comes 1.9
  to 2.1 s after the cast finished on 8,188 of 8,579 casts. Shielding Hands' end heal was read by its rule already (`end_heal`).
  **What a cast that landed gave** (`landed_casts`): the heal rows name no skill, so a row is tied to a cast by time: the healer's rows on the
  target inside 0.3 s of the cast finishing, and for Patient Spirit and Shielding Hands his row inside `END_HEAL_S` 0.2 of the end the
  effects record gives that enchantment (`_effect_of`), a row at the finish of another of his casts on the target left to that cast.
  Checked against gvg.report's recaps (R-707), on the casts that fall whole inside a recap's 5 s, 40 matches: Patient Spirit within 5 of
  the recap on 17 of 23 (12 before: the Divine Favor alone), Shielding Hands 6 of 7 (2 before); the misses sit at the edge of the recap's
  window. On 25 matches 94% of Patient Spirit effects have such a row at their end; one stripped mostly has none, as its text says.
  `did`: Aura of Faith, which the recaps never credit, by its own rule: what landed while it was up times share / (1 - share), at its
  caster's rank or the usual one. `blocks` marks a prot that blocks: the recap's count of attacks blocked is said, or "blocking nothing".
  **A spell lost to Shame** (`Forensics.stopped_by`, `triggers`): `casts` keeps who stopped an interrupted cast and with which skill
  (gvg.report's interrupt record); the record names Shame where the hex made the spell fail. The trigger row is built from it and no longer
  from the hex in the effects record, which holds none where the hex landed and went inside one tenth. Checked (R-707): on the set the
  record names Shame on all 126 casts the hex told and on 47 more; 161 of the 173 are spells on an ally. `seen`: the seconds from the
  hex landing to the start of the cast (34 of 173 under 0.2 s, 84 a second or longer); `fault` only at 0.2 s or more (Rule 1; Claude's
  reading, R-826; replaced by R-830, below). On a death: `shamed`, a monk's prot or heal on the dying player lost to Shame inside the kill attempt (8 deaths).
  **Deep Wound left** (`removal_saves`): the sum walked again with the removal landed (his health and his maximum both rise by what Deep
  Wound took, then the removal's own heal: what a cast of it gave on average this match, else its caster's Divine Favor), from the monk's
  first chance on a grid of 0.1 s: lives, short by how much, the latest start. On the set's 159 deaths with it: 148 removals would have
  saved him, 7 not enough, 58 not told (the sum does not balance).
  **`prot_would`**: a prot does not stack with itself: while the same skill is on him from a team mate (the effects record) the missed cast
  adds nothing; and `death_rulings` drops a prot that would have stopped and healed nothing, told or not (R-812).
  **The sentences** (`death_lines`, `say_trigger` and `say_caught` with `plain`): no ruling number on a death's row; "Trigger Fault:",
  "Positioning:", "Context:", "Missed Deep Wound:" each on its own line; a burst's head with the damage inside 3 s; what was done for him
  one line a player, a prot's stopping said once after his last cast of it; "lost to Shame" under "Attempted, failed".
  **Every monk on his own at a death** (R-828, amending R-715; `bundle-4` 90223ed; first built behind a switch and held, then ruled: "Go with
  B"). His question on the Mesmer at 6:15 of RACK v hdm: the Prot's Spirit Bond and Life Sheath were ready and unused, and were not listed
  because the 8 Monk's Shielding Hands had landed. `deaths` now lists every monk's chance of a kind whatever a team mate landed (`taken`
  still records it; the casts begun and not landed are said too), `death_rulings` keeps a prot only where it alone would have saved him
  (R-812), and a cast begun too late names what else of that kind he had ready at his earlier moment (`also_ready`, `began`). The kill
  attempts' own records are untouched: R-715 stands where the player lived. On the set's 1,619 deaths: a prot line on 512 (413 before;
  102 deaths gain one, 66 of them one that would have saved him), a heal line on 390 (354; 36 gain one, 27); 13 of the 46 deaths of the
  three marked games gain a line, three of them rows he had marked correct (RACK v hdm 7:07, 7:33, 7:44 the 8 Monk): said to him.
  **Shame, the fault** (R-830, replacing the reading of R-826): `seen` is the time from the hex landing to his cast stopping, a fault at
  0.2 s or longer ("only if monk could have cancelled"). Checked (R-707): 128 of the 173 casts stop in the tenth they begin (begun under
  the hex), 45 ran 0.1 to 1.1 s (under way as it landed, failing as they would have finished); 142 are faults, 31 are not.
  **The front line** (R-829): stays the most forward team mate in the fight who is no backline monk (the Hammer at 2:04 of Men v NwAy
  stood at 1,445 along the line, the Stand Mes 2 at 436, the AoB Derv at -124): not told from frontline characters alone.
  **Run** (82 matches, against 92de38e): 6,935 plays and the moments identical to the digest of ccd0a55, `compare.py` finds no play
  changed, 323 Classic rows pass; beside the plays `attempts`, `pressure`, `deaths` (all matches), `triggers` (31), `execution` (20) and
  `fails` (11) differ. Of 1,619 deaths: a prot fault on 413 (455 before), a heal 354 (358), an interrupt 147 (147), Deep Wound 159
  (159); Shield Guardian listed 80 times (171), Patient Spirit 118 (127), Vigorous Spirit 44 (68); too fast 67 (57); Shame rows 173
  (126), 139 of them faults; a landed cast with an end heal on 89 deaths; Aura of Faith said by its rule on 52. On the attempts the
  missed prot rows go 1,633 to 1,537 and the heal rows 660 to 652 (the cast time, and Shield Guardian's aftercast), so the checks of
  `cases.py attempts` are to be read again on the full run. **Run again at 90223ed** (R-828, R-830): plays and moments identical, 323
  Classic rows pass; against 805b894 only `deaths` (78 matches) and `triggers` (19) differ, the attempts not at all.
- **R-839 to R-842 built (2026-11-28, afternoon; `bundle-4` f7165b1, one bundled change; the development set only: a full run is wanted).**
  **A strip counts by what it took** (R-839, R-840; `strip_effective`): on a spike a prot taken before the first big hit, or a prot or a
  heal taken during it; on a burst a prot or a heal before or during it; whether the strip deals damage decides nothing (`STRIP_HITS` stays
  on each row as evidence). On the set's 1,034 spikes 296 strips stay effective, 64 no longer are (a damaging strip that took neither) and
  40 newly are (a strip dealing none that took a prot or heal during it); on its 1,944 bursts 552 stay and 117 no longer are. Section H:
  the row for a strip dealing no damage now reads "the strip that matters (R-839)", and a new evidence row sets a damaging strip that took
  neither against the spikes with no strip at all (on the set 23.4% killed against 37.7%, -10.9, reads backwards: not its like, the
  full run to say). A strip in time that took nothing that counts is said so on the failed spike (`say_fail`).
  **Kept by name** (R-842; `execution.BY_NAME`, by the names of the rows of section H): a spike's prot stripped before the first big hit
  and one of his monks knocked down at the spike print "kept by his ruling, R-842, whatever the groups bar says", carry `by_name` in
  `attempts_cases.json`, and say "READS BACKWARDS: to bring to him" where they do. `X3_BUT` is unchanged. A strip before a burst is not
  in the list (his words).
  **The spike thrown on the play's row** (R-841; `record`'s `thrown`, `say_faults`'s `threw`): each play's record names the spikes thrown
  inside it by its own players on the enemy it met and by them (places in `flag_cost[rid].thrown`); the row says how many, how many landed
  too little to be a kill attempt, and each into Aegis (`say_thrown`, six at most). **The time of death** (`died`, s against the first
  skill): section J's new row sets Aegis coming during a spike against the plain spikes whose target was still alive at the middle of when
  Aegis came, both read for dying after it: on the set 58 at 1.7% against 855 at 21.5%, -19.4 (-23.8 to -15.1), 9 groups of 9.
  **The attack's good play on a death by pressure** (`pressure`'s `good`, `monks_stopped(until=)`): a pressure attempt has no first big
  hit, so the monks' prots and heals for him that the attack stopped are read from 3 s before its start to its end; a death with no attempt
  of its own reads them the same way. On the set's 1,619 deaths 80 gain an "Enemy good play:" line.
  **A slip found and put right** (59c47b0): in `deaths` the `else` that reads a death with no attempt of its own had come loose from its
  `if`, so every death whose attempt held no `good` was read a second time by the other path. Nothing differed but the order of the casts
  in "Success:" (a kill attempt gives the prots before the heals, the death's own reading player by player): the order that moved "from
  one run to the next". `landed_casts` now returns them in the order they were cast, whoever asks; 67 rows of the set change in that
  order alone.
  **Run** (82 matches, against 59c47b0): 6,935 plays and the moments identical (`compare.py`: no play changed; the digest agrees on all
  82); 323 Classic rows pass; beside the plays `attempts`, `pressure`, `execution` (all matches), `thrown` (75), `deaths` (65) and `fails` (58)
  differ. Main's rows written again: eight change, seven in the order of the casts alone (RACK v hdm 7:33 the Prot, 7:44 the 8 Monk; Men
  v NwAy 5:15, 8:38, 9:20, 14:23, 14:35) and one gains "Enemy good play:" (Men v NwAy 4:35, the Stand Mes: Healing Burst stopped with
  Power Drain).

- **Balling reads a cast that strikes its other foes one after another (2026-11-28, later; R-847; `bundle-4` 4d3866c, with the full run at it; the commit after it puts a comment's figures right and holds the run's report).**
  **Measured first** (the development set, every finished cast of a tagged area skill on an enemy player, the caster's hits on other players
  set against the hit on the target; the damage rows name no skill, so a hit is tied to a cast by its caster and its time): Energy Surge,
  Lamentation, Mind Burn, Shell Shock, Lightning Touch and Meteor land on the others in the target's own tenth (Energy Surge 1,013 of its
  hits there, 3 to 13 in any tenth after). Invoke Lightning and Chain Lightning do not: of 1,326 casts that hit their target, 3 hits on
  another player in his tenth, 314 at 0.4 to 0.6 s and 111 at 0.9 to 1.1 s, 18 elsewhere in the 1.3 s; each of a spell's size (the
  middle one the same as the target's hit). Their text is "target foe and up to two other foes near your target are struck": the record
  sets each next foe half a second after the one before. Death Blossom's second strike (0.4 s) is its own hit and is left as it was.
  **Built at the root** (`balling`; `CHAIN_STEP_S` 0.5, `CHAIN_N`): no wider `BALL_S`, which would take in the caster's other hits. A cast
  whose text strikes "up to N other foes" is read at each of its N steps after the target's hit, inside `BALL_S` of the step, on players
  other than the target; `chain` on the row names the steps that landed on a player. A step is read without the one before it (a foe
  struck between may be an NPC or a spirit, which has no row here: 14 of 111 second steps on the set have no first). The count N is read
  from the skill's own text, never from a list of names. The words are unchanged (`say_balled`: "they stood within its reach, nearby").
  **Run**: the development set against the run before it (both made the same day, `compare` by key): plays, moments and every record
  identical but `balled` and each play's places in it, in the 18 matches with such a bar; 1,838 rows become 2,164 (Invoke Lightning 1 to
  261, Chain Lightning 2 to 68; no row lost, 2 gain a player); 323 Classic rows pass. The full run (564, no errors; 37 minutes on this
  machine): the digest agrees on all 564 (33,089 plays, 26,199 moments), 323 Classic rows pass, the self-check 6 times in 4 matches as
  before; balling 11,947 rows (nearby 7,008, adjacent 4,893, in the area 46): Energy Surge 4,100, a scythe attack 3,741, Lamentation
  1,310, Invoke Lightning 1,127, Mind Burn 578, Chain Lightning 451, in 147 matches with such a row. Main's `execution_rows.json` written
  again and the same row for row (its engine stamp alone moved): nothing written over his marks.
  **A late part of the spike against its own like** (`cases.py attempts`, section I; `_x3_diff_alive`; a report, no reading moves). The
  run at f7165b1 read the strip of a prot at 3 s or later after the first big hit as killing less (-6.2) and the first interrupt on his
  monks at 1.5 to 3 s and later the same (-5.1, -22.0). Opus's reading, checked and right: a part can land late only on a target who has
  lived that long, and it was set against every attempt with the part ready and not done, the targets dead inside a second among them.
  Now each attempt is set against those whose target was still alive when its own part landed (`s`, the first big hit to the outcome);
  the old figure is kept beside it (`plain`). On the full run: the strip +3.7 at 0.5 to 1 s, +4.5 at 1 to 1.5 s, +7.6 (+3.0 to +11.6)
  at 1.5 to 3 s, +9.4 (+5.1 to +14.0) at 3 s or later; the interrupt on his monks +3.0, +3.2, +8.0 (+5.3 to +10.8) and +1.5 (-0.0 to
  +3.0). Nothing in section I reads backwards. Only `together` differs in `attempts_cases.json`. The strip before a burst (section H):
  its plain test reads backwards (-6.0, 2 groups of 10) and its own like does not (+2.2, 6 of 10, fails): the plain test holds level
  the prots on him, which is what the strip changes, so it is not its test (the rule of f7165b1); it stays not kept (R-842).

## The old engine (retired at the close, R-323): the TQs and the causal map

### 40. The TQs
- The TQs (Denning's four question categories; the learning report's section "The TQs", `tq.py`, METHODS.md "The TQs")
  are a demonstration of the model after a batch, not part of it; they run every other chunk unless asked. Each is
  answered with data at the depth of METHODS.md "Answer exemplars", in two parts kept apart: macro (was the decision
  the right call: the usual play's choice effects at the decision before) and micro (given the call, what went wrong
  in execution: the execution inputs against the role's benchmark), with what the enemy did described beside them,
  and a confidence level:
  1. Flags: one instance in a batched match where a team got behind on flags, and why; then how a different play could
     have increased its win chances.
  2. Monk death: one instance where a monk died, and why; then how it could have been prevented.
  3. Power play: one instance where a team couldn't kill on a power play, and why; then how it could have been
     converted into kills.
  4. NPCs: one instance where a team lost NPCs, and why; then how it could have been prevented.

### 41. The causal map and the old node models
- Explaining why comes from the causal map (`data/model/causal_map.json`, METHODS.md "The causal model"): Denning's
  and Claude's reasoning about what causes what, as links whose strength the data measures. Add his answers as links
  (with reason, source and tactics ids) and log every change; keep `knowledge/causal-map.md` rendered. Built so far:
  `phases.py` (phases, plans, jobs, capacities), `buildfeat.py` (build and matchup features), `nodes.py` (node models: deaths,
  kill conversion, flag answers, Lord damage; `explain` for a player's risk second by second; pit NPC loss is the learned
  node `pit_npc_loss` in `learnednodes.py`), `usual.py` (the usual play and each choice's
  effect in win chance, between similar builds), `values.py` (results and causes priced in win points;
  `knowledge/values.md`). Per-player skill flags: `buildfeat.player_flags` (one skill can change the right play).
  Snare and speed power per player (how strong, not just whether): `movepower.py` (Return is an escape, not a snare).
  Pressure beyond damage per player (kiting, degen, baited interrupts, offensive knockdowns, disables, cast
  prevention): `pressure.py` (METHODS.md "After chunk 4").
  Chains from the node models with fixes carried forward to the result: `causalchain.py` (step 4). Discovery: the
  variable catalogue (`catalogue.py`, play variables generated from the replay schema) against every learned node on
  unseen matches, offered after passing twice: `discover.py` and the "Discovery" workflow (step 3). The goal test:
  `advice.py` (does matching the advice do better on unseen matches; the sealed blind test). The query tool: `ask.py`
  (a match and a moment in; state, macro, micro and the enemy's response out). The generated structure page:
  `modelpage.py` -> `knowledge/model.md`.
