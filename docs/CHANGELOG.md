# Changelog

Dated session log of the GvG Info analysis engine and portal, newest first. Entries were moved here from docs/HANDOFF.md and tools/replay_analysis/METHODS.md, which now hold current state only. Future sessions add at most ten lines each at the top. Decisions in these entries that are still in force are numbered in docs/RULINGS.md.

## 2026-11-12 (night): game 1's marks, the decision moments rebuilt on the records, the decision gate first run (R-419, R-420; branch `bundle-4`)
- His answers to the gate review's three points (R-419: the front door rule, WAY_OUT_GAP_S and the 3 s drop kept, hdm v HC 2:56 untold, 983a47db dropped). His marks on game 1 (R-420): a push in is told with its fight's numbers over its first 12 s; a leave needs the player to go further than the enemy he faced; a join or a leave only at a fight (damage within 30 s, or within 1,000: JOIN_ENGAGE, JOIN_ENGAGE_S). Game 1's replay has one damage event from 6:10 to 8:30; 7 of 606 replays have two or more whole minutes of casts with no damage recorded.
- All-match counts: joins 10,699 to 10,496, leaves 9,454 to 9,103; every other count unchanged. Line-up unchanged: building 422 of 426, held-out 186 of 186; comms 109 of 157 and 62 of 80. Golden stories draft 9 (64 lines differ from draft 8: push numbers, and joins and leaves at no fight).
- `Moments.run_starts()` (when a runner goes to run, when the flag is under way; the story's go-back lines print from it). Stage B rebuilt on the records: family 1 from `run_starts` and the boost; family 2 from `attempts` (a split sets out or grows; the call from its answer); family 3 from the numbers in each main team's fight (R-351); the call from the records in the window, with every verb kept (`verbs`).
- The decision gate (R-394), first run: `golden.py gate`, part one against `data/model/golden_key.json` (Claude's reading of his notes): 11 of 14 moments found; trigger 5/5, stand 5/5, runners 5/5, rest 4/5, forced 6/6, home 2/2, side 4/4, source 4/4; size 1/2, call 3/6. Part two, comms: 91 of 105 calls with a decision of that team within 30 s, 64 of 105 the same call.

## 2026-11-12: reading step 2, the words of R-373 and R-375 to R-378 as records, and rulings R-399 to R-415 (branch `bundle-4`, d59ea1a to 5f43768)
- `moments.py`: `flag_pushes()` (R-371: players on a flagger who is on his own, with who helped, died, dropped, the pickup delayed), the flag route, door, hold and boost distance in `flags_record()`, `flag_lead()` (R-375), `pregame()`, `posture()` (R-376), `timing()` (R-377), `monk_counts()` and `on_lord()` (R-378). `story.py` prints each from its record.
- 22 draft thresholds in `common.py` (PUSHFLAG_R to LORD_GAP_S), to confirm. Over 606 matches: 1,181 pushes on a flagger (1.9 a match), 1,324 flag routes read to the stand, 987 full-flag and 738 half-flag stretches, 1,006 postures, 293 timing choices (114 delayed pickups, 80 held to the boost, 35 stayed to help, 64 left before the res), 4,933 monk count changes, 1,061 stretches on a Guild Lord told. The story's median length is 164 lines a match.
- The line-up now checks the seven kinds it used to set aside (first reading: building 419 of 434 seen events, held-out 164 of 208); lead, route, monks, the Lord and pushing the flagger read well, posture and timing did not, which led to R-405 and R-414.
- Fixed on the way: a flag dropped at the spawn and taken again by the same player was read as returned (hdm v HC 2:56: the missed pickup was placed before the drop); captures 5,245 to 5,249, pickups given 69 to 72. `story.py` stopped on 8 of 606 matches (a player dead 10 s after a fight ended had no place). Every other all-match count is identical to the count before the change.
- Denning ruled R-399 to R-404 the same night, built on the branch (4dc4347): posture on either side with a small damage allowance; a fifth timing choice (a flag held back in hand, or left at the spawn); a main team push keeps `onto_flag`; flag lead as timing (how much of its run each next flag has done: a full flag = the backup at the stand, half a flag = 0.3 of a run ahead); the delayed pickup at 12 s; the other thresholds as they stand.
- After the rulings: seen events 421 of 433 (97%) building, 167 of 208 (80%) held out; calls 109 of 157 and 61 of 83. Over 606 matches: 600 full-flag and 664 half-flag stretches, 3,205 postures (1,367 on the enemy's ground, 1,838 on a team's own), 780 pushes walked onto a held flag, 91 delayed pickups, 2,120 flags held back, 1,460 left at the spawn. Posture gained one statement in each set for 2,199 more records: still the weak word.
- `thresholds.py sweep NAME values [--data ...]` (with `GVG_TRY` in `common.py`): what a looser or tighter threshold does to the records and to the building games' line-up, without editing the engine. One comms statement retyped as a plan (R-400).
- Next morning, R-405 to R-415 (5f43768). Posture dropped as a word of its own; `standoffs()` records the disengage, framed on OG v hdm (R-411, R-413: the two main teams, five or more each, within 4,000, no more than 0.4 hits a player in any 10 s, for 35 s): 146 over 606 matches (0.24 a match), and the story stops telling one as a fight. Flag lead is a tally (R-408: 1 for the stand, plus the share of the next flag run done, plus up to half for the following runner back at the spawn; his bands at 0.35, 0.8, 1.3, 1.7). The delayed pickup is 10 s; a held flag is 45 s around the stand, and a flag left at the spawn is told, only while the enemy holds the stand (121 each). R-412 records what the flag readings are for.
- Reading step 3 begun: golden stories regenerated (draft 6, 15 games, 2,199 lines); the blind check against his 13 notes (the opening and the last two to three minutes before each moment) found the new lines in agreement in eight games and one fault, fixed: a hand-off under a push was told as a dropped flag. Line-up with posture and timing statements set aside when not a true stand-off or a deliberate hold (R-414): seen events 422 of 426 (99%) building, 163 of 196 (83%) held out; calls 108 of 157 and 61 of 80. A stand-off on a split was added (R-415: 60 over 606 matches), and the gate review of the 33 held-out misses was opened at his direction.
- Evening: the gate review (R-416 to R-418; 7837d95). His answers on the 33 held-out misses: 7 confirmed, 8 withdrawn, 18 stand. The engine as reviewed agrees with 171 of 188 things seen (91%): the reading gate is passed. His question on Weeping Stone's doors found door routes cut at the first cell off the walkable ground (13 doors, seven halls). Built from the misses: `way_out()`, splits told by who set out together, a main team going home as an answer, swaps in an answer, drops told where they lay, repeated pickups and unattributed captures repaired (captures 5,249 to 5,257), the flag route to the stand, left-before-res at every res, Lord damage in the state line. He then withdrew two of the three left and ruled a push on a flagger counts from 4 s when he reaches his team with them on him (R-418; 1,179 pushes to 1,287). After them: held-out 186 of 186, building 422 of 426; 1,607 door lines (2.7 a match), 104 answer swaps, left before res 64 to 79; golden stories draft 8.

## 2026-11-11 (sixth): rulings R-390 to R-398; R-391 and R-392 built (branch `bundle-4`, aa39a29)
- Denning confirmed the 17 draft thresholds (R-390), ruled own footies (R-391), a split whose main team is dead (R-392) and no Shadow Step input (R-393).
- R-391: `place_at` names a team's own footies within reach of its own living footmen, by front or back group (a dead footman's group is read from where his killers stood); a fall back that comes to rest there is told as falling to them.
- R-392: `main_team()` keeps the main team as its survivors, or nobody, while its dead are down; 88 fewer main team pushes over 606 matches (1,993 to 1,905), 16 more split attempts. Apes v hold is one split from 0:24 to 5:00.
- The line-up takes a split's end from its split fight record. Seen events 365 of 365 (building), 136 of 162 (84%, held out; the one gained came from that change to the check); comms calls 106 of 152 and 59 of 76.
- He then ruled R-394 to R-398: the decision gate (his notes on the 15 golden moments, and the calls on comms); he marks game 1's story only; after his review the reading gate counts only the engine's misses, with two new games if it fails; the held-out files moved to `data/lineup/held/` (`lineup.py` prints their lines only with `--gate`; branch at 0c46762); his list before the next training run. REDESIGN.md rewritten to match (the reading stage, both gates, the build plan, that list).

## 2026-11-11 (fifth): the reading's open items, and the thresholds counted (branch `bundle-4`, 9fca5f5)
- Men's hand-off at 2:17 (hdm v Men): gvg.report recorded the dervish's capture with no pickup. `Moments.flag_ev` now gives such a capture its pickup (where a team mate dropped the flag, else at the spawn): 69 of 5,245 captures in 58 of 606 matches. The story had been missing that capture altogether.
- The xxx air elementalist at 12:52: the split fight fell back into the main fight for a moment, so no join was seen. A split fight's record now keeps `pulled` (a player taken off it onto the main fight, 231 in 111 matches) and the story tells it. Reading every player's company against 16 s earlier was tried first and dropped: it added a third more joins, most of them a leave and a join two seconds apart.
- Line-up: seen events 364 of 365 on the building games, 135 of 162 (83%) held out, unchanged; comms calls 104 of 152 and 59 of 76. The statement for 12:52 is retyped to the air elementalist alone (it had named both).
- Shadow Step: 24 casts by a flag carrier in 658 replays; in all 19 where he steps the flag drops 0.3 s after the cast starts (first 20 August 2026), and none shows the flag kept. The change predates every stored case, so no date is needed.
- `tools/golden/thresholds.py`: the all-match counts beside the 17 draft thresholds (606 matches: 10,699 joins, 887 split fights, 199 swaps, 24.8 ground moves a match of which 11.9 told, 1,546 undefended stretches, 2,581 stretches on pit NPCs).

## 2026-11-11 (fourth): timestamped commentary and comms lined up with the record
- Denning sent 17 timestamped transcripts (7 of his own on golden games, 10 of Maga's comms) and ruled R-368 to R-372.
- `tools/golden/lineup.py` (branch `bundle-4`): paraphrased statements a line (`data/lineup/`, on main) checked against the story and the fight numbers; kinds the story has no word for are counted.
- 16 transcripts filed (12 for building, 4 held out, R-370): 1,126 statements; of 761 checked, 555 agree (73%; held-out 74%), 206 differ.
- Reads well: caps, deaths, who goes back for the flag, fight numbers, NPCs. Reads badly: collapses (25 of 66), swaps (0 of 5), falling back, pushes, answers, a split's later joiners listed from the opening, pre-game flag events, a half run (hdm v Men 2:01).
- Denning ruled the scope (R-373): build flag route, pushing the flagger, flag lead, posture, timing; plans, options, reasons, micro calls and build labels stay out; what reads badly is fixed in the engine's rules (R-374).
- Built on `bundle-4`: the split fight record (R-365) and joins, leaves and swaps read player by player (`moves()`, `split_fights()`); xxx v ohno's back side is one record 0:30 to 14:14 where six split attempts stood; joins agree 35 of 66 (from 25), swaps 3 of 5. Six draft thresholds in `common.py` to confirm; all-match counts and the golden stories not yet rerun.
- Then on the branch: answers (a defender who traded damage; later defenders told), split openings, retreats told with both teams, the flag at the gates; all 516 matches run clean (711 split fights, median 92 s; 12.9 joins per 10 minutes; 507 swaps, a count not yet trusted). Line-up 76%, held-out 77%; gate 90% and golden set of 15 (R-380).
- Replays queued: 453bd7a0 (Men v OG), cc1e770d (NwAy v ohno, stored as 11:49; the comms run 28 minutes), ee3a719f.
- Denning ruled R-379 to R-382 (vine seed transcript dropped; gate 90% on held-out games; solo split; golden set of 15, the other 15 parked). 90 random matches from 2 September on fetched (606 replays; the records read all of them).
- Then on the branch: solo split, swaps from each stay, the ground record `ground()` (main team and each side of a split fight), 'through mid' from his collapse route, the pit by its NPCs, side fights cut from a bigger fight, `undefended()`, `on_pit()`, hand-off by a brief carrier. R-383 to R-389. He reviewed the 61 seen misses of the building games: 12 were the engine's (10 fixed), 5 calls withdrawn, 36 confirmed. Seen events 99% (building), 83% (held-out, not reviewed); comms calls 68% and 78%. About 17 draft thresholds to confirm.

## 2026-11-11 (third): the engine's split, push and flag records (branch `bundle-4`; stories draft 5)
- Denning ruled R-355 to R-364 and directed that the record, not the description, is the work (R-362).
- `moments.py`: `attempts()` (split attempts and main team pushes, one record each), `caught()`, `flags_record()`, `main_team()` (the part that carries the flags and stays; the part on the front lane when the other went round the back), `lane()`; `common.flux_at`. `story.py` prints from these; the old "go to split" and "go back to defend" lines are gone.
- Checked against Nick's three games (12 of 13 attempts, composition and answers right) and four of the blind notes (opening and solo splits agree; an even 4v4 split fight that crosses the middle does not).
- 513 matches run in 2.5 minutes: 1,909 splits, 1,681 pushes, 22 flags carried with a split, 226 splits back ahead of or behind their defenders.
- He then ruled R-365 (an even split fight is one record while the same groups stay engaged), R-366 (back cap as built) and R-367 (solo splits parked). R-365 is not built.

## 2026-11-11 (second): Nick's commentary lined up with the story (stories draft 4)
- Denning attached eight of Nick's transcripts and nine report links. The transcripts carry no timestamps; five reports were not stored and were fetched (`replays/requests.txt`). One link (00cb0759, xxx v Apes) has no transcript.
- Lining up works without timestamps: deaths, caps, splits and NPC kills in the commentary fall in the story's order, an anchor every 30 to 60 s. Four games added to `data/commentary/nick.json` (now 9 games, 81 claims, each with the story's check). One game (983a47db) still to do.
- The commentary found four plain errors in `story.py`, fixed on `bundle-4`: deaths in different places merged into one line; "N s before the base res" read from the replay clock, which is off by up to 2 s (it now reads whether the res took the player: "just too late for the base res"); no line for the Lord's death (the story now ends there); a resignation shown as a Lord kill and a list of deaths.
- Stories regenerated (2,342 lines); only death, Lord and resignation lines changed; none of his marked lines; blind notes agree ("before time", "right after time", "gets based").
- "Boss" in the transcripts is September's flux (Like a Boss), not the morale boost: the file's vocabulary note and three older claims corrected. The engine has no reading of any flux.
- Waiting list for his ruling (nothing built): the flux and its holder, opening splits, main team in a 4-4 (R-335 against the monks rule), returning defender, arriving ahead after a collapse, caught out of position, runner-seconds away, inverted position, map objects, minions, pushing in before the defenders' base res.
- He ruled the same night (R-355 to R-362): six items yes, Druid's Isle items not yet, and the record is the work, not the description. `moments.py` checked against Nick's splits: about 11 of 15 attempts found, about half its split records repeats or not splits.

## 2026-11-11: the story rewritten from Denning's first marks (branch `bundle-4`; stories draft 3)
- He marked game 1 (BcS v hook): 7 lines wrong and a note asking for the game state (who is where, what they are doing) and for when players go to run, not only pickups. `story.py` now writes STATE lines at the opening and each minute, who leaves to go back for the flag, a dropped flag that stays where it falls and its return, resurrections, footmen taken, where the next runner came from; fights are told only once damage is traded, and a fight's place and numbers are followed apart.
- Places: footies only where the footmen are engaged (R-307), a door is its drawn route out to 1,500 past the base, his greater stand areas (all 14 halls) come before doors. Low team health under 85% (R-352); no energy estimate for now (R-353); golden page shows the story first (R-354).

## 2026-11-10 (evening): the engine starts to read a match as Denning's notes do (branch `bundle-4`)
- Denning set the first drop-down labels aside and wrote notes on 14 golden moments; rulings R-334 to R-347 (greater stand area; main team in a 4v4; flag position and stand holder both; pinned teams; one flag a team and the four hand-off and double run forms; the model thinks as his notes do, R-341; golden test in two parts).
- Drafted on the branch: the flag ledger (`Moments.flag_lives`: 5,977 flag lives; single run 36%, returned 19%, hand-off to cap 15%, double run full 13%, half 7%), every fight with its numbers (`Moments.fights`), places in his words (`Hall.place`: doors, front and back footies, greater stand area), and `story.py`, which prints the chain. Against his notes on three games the numbers, places, swaps, deaths and flag forms agree; the "why" words and routes are not written yet.
- Map page: area type "Greater stand area", drafted for 9 halls from where fights of 3+ a side stand around the stand (`tools/maps/draft_greater_stand.py`); the engine reads his drawn area where one exists.
- Later: rulings R-348 to R-351 (on time; under pressure is health, energy and deaths, position the result; 12 s to count in a fight; numbers advantage in every fight). The story now says how a player came (through mid, through the pit, by a door), whether an answer was on time, swaps, who falls back and whether under pressure, who falls out. Golden page rebuilt in two parts (R-345): his note, then the engine's story of the game to mark; stories written for all 30 moments.
- Night: R-352 to R-354. Low team health under 85%; energy left out for now. The golden page now shows the engine's story first for him to mark, with his 13 earlier notes kept as the blind check; stories regenerated (draft 2) on his 14 Greater stand area labels.
- Also in the branch from his rulings: cast prevention by casts punished (R-330), spikes signed (R-331), play for 28 on pit NPCs from 12:00 (R-332), the worth of each team's next boost in every moment (R-333).

## 2026-11-10 (second session): redesign step 2 started on branch `bundle-4`; golden moments page
- Denning accepted Isle of Solitude's flag spawns and ruled Weeping Stone's unmirrored outer archer as in the game (R-318); the audit reads clean, so step 2 began. Rulings R-318 to R-324 (more than half = at a place; footmen from the labels; gained elsewhere; the branch; pass rates left to Claude; all five proposals in the bundle).
- Branch `bundle-4` (not on main: one bundled engine change, one rebuild). `hallmap.py`: zones from the labelled areas (R-306), walked distance over the outline with teleporters as hops of no length (R-316), footmen reach measured around the Footman labels (1,190 to 1,620 units by hall; `data/benchmarks/footmen_reach.json`). `state.zone` and the three map numbers read it; the labels and outlines join the cache key.
- Read against the old circles on one match a hall: 35% of player-seconds change zone, mostly backside to own base and push side to enemy base (the labelled bases are far larger than a 2,500 circle). Walked map numbers against straight lines: Nomad's Isle flag run 4,330 to 8,964, Isle of Jade 9,232 to 6,998 (teleporter), bases apart on Nomad's 5,334 to 17,050.
- `moments.py` (draft, REDESIGN 2.3 to 2.7): departures labelled by what they became, triggers for families 1 to 3, scenario, the call read 20 to 30 s later as an allocation, forced reads. 506 matches: 23,041 moments (9,135 flag decisions, 3,570 split answers, 10,336 numbers moments), 19% forced, 70 s on 4 cores.
- Found by the draft: in 39% of flag decisions the main group stands in no named place (on the backside 14%, on the push side 14%, in the enemy base 9%), and 27% of split answers are a count no named call covers (most often three or more against a solo split). The call lists need options for these, in Denning's words, from the golden moments.
- Site: Model > Golden moments (`assets/js/pages/golden.js`, `data/model/golden_moments.json`): 30 moments (one for each of the 27 scenarios of families 1 to 3, plus a double run and two forced reads), each labelled by hand: real or not, what the leave became, scenario, call, shape, forced, and an optional sealed "should have done". The file never holds the engine's reading. `tools/golden/golden.py` (on the branch) picks and scores.
- Later the same day: rulings R-325 to R-333 (definitions confirmed; how to write to Denning; cast prevention by casts punished; spikes signed; play for 28 on pit NPCs from 12:00; enemy boost worth), the last four in the branch. First six golden labels scored (found 5 of 6; trigger, runners and rest 2 of 5 each); his notes read for what the design misses (HANDOFF "Open rulings", items 1 to 7).
- Label notes for Denning: Warrior's Isle has no Flag stand point (the engine uses the replays' stand); Isle of Meditation has two (the one in the Flag stand area is used, R-308).

## 2026-11-10: all 14 halls labelled; label audit and hall features
- Denning labelled the other 11 halls (43 to 59 labels each) and gave each hall's specifics. New `tools/maps/audit_labels.py` checks labels against R-310: pit roster, one res shrine and flag spawn a side, equal NPCs, doubled labels, and mirror partners (the hall's symmetry is fitted from labels that come one a side; used only where 90% of the outline maps onto itself).
- Found: no flag spawns on Corrupted Isle, Isle of Meditation, Isle of Solitude; no res shrines on Isle of the Dead; Nomad's Isle has no Knights and four Footman labels inside the pits (17 replays: two knights a team, no footman); Warrior's Isle top right pit has no archers (7 v 5); Isle of Weeping Stone has doubled flag spawn and flag stand labels. Looser: Isle of Meditation's north res shrine sits about 1,000 units from where replays and the mirror put it; a Frozen Isle bridge and a few choke points have no partner.
- NPC counts per team in every replay agree with the labels wherever enough NPCs were attacked; per-team counts above the labelled number (Imperial Isle 7, Isle of Meditation 6) are team mix-ups in the replay, since both teams together never exceed twice the labelled count.
- `draft_labels.py --only=<types>` drafts just the missing types on a hall already labelled by hand: flag spawns (and stands) for the first three halls and Isle of Meditation's north res shrine are now offered on the map page. The page hides a drafted point where a label of its type already sits, and gains the point types Trebuchet, Repair kit, Health shrine, Flame sentinel.
- Hall specifics saved: `knowledge/guild-halls.md` (wiki facts and Denning's lines per hall), `data/maps/hall_features.json` (footmen, fall-back zones, environment effects, objects and flag routes by label id, each hall's decisions with their family), RULINGS R-310 to R-314, REDESIGN.md (hall features in the layers; teleporters as hops of no length in path distance). Five halls have no footmen.
- Follow-up the same day: Denning corrected the gaps (Nomad's Isle has knights and no footmen; res shrines on Isle of the Dead; pit archers on Warrior's Isle; doubles removed). Left: Isle of Solitude's two flag spawns (drafted) and one unmirrored outer archer a side on Isle of Weeping Stone. Seven labels retyped with his approval (Trebuchet, Repair kit, Health shrine, Flame sentinel).
- R-315 (Weeping Stone's gate lock only from the back side), R-316 (a route drawn through a teleporter overstates the walk; the hop counts as no length), R-317 (label readings confirmed). `audit_labels.py --routes` gives drawn and walked lengths (Isle of Jade coral flag runs 11,500 to 12,000 drawn, 6,700 to 7,300 walked). The engine fix waits for the step 2 rebuild: waiting list in causal_map.json, REDESIGN item 2.2.
- Wiki map images could not be opened from the workspace (text only). Not an engine change: nothing in tools/replay_analysis changed.

## 2026-11-09 (late): decision redesign planned, step 1 built (no rebuild)
- Denning's review of blind rounds 1 and 2: the picks did not get to the point and the options were unreadable. Plan in docs/REDESIGN.md: five decision families with scenarios, calls read as allocations over 20 to 30 s, shape (who, when, which way), objective and mechanics, one decision card with three verdicts, enemy execution scored, the TQs replaced by the card. Rulings R-292 to R-305 confirmed the same evening (R-296 widened to a player leaving base; R-304 offence or defence as objective; R-305 the double run).
- Blind test: round 3 void (unanswered, sealed parts never opened); rounds 1 and 2 marked first design; Train batch input `blind` defaults to no. advice.py and blindtest.js: a call is priced only with 5+ similar cases, "matched the team" is no longer a score, one cumulative total with a 90% range, a reason asked for whenever Denning differs from the model. Checked with a mock round: site and advice.py give the same figures.
- Site fix (core.js): saving a file over about 120 KB failed with "Maximum call stack size exceeded"; blind_tests.json was at 107 KB, so the next round's saves would have failed.
- Guild hall maps (Model > Guild hall maps, assets/js/pages/maps.js; tools/maps/build_maps.py): all 14 halls drawn from gvg.report's walkable outline, with flag stand, team starts, flag spawns and estimated NPC spots; Denning adds points, areas and routes, saved to data/maps/labels/. The engine does not read them until bundle 4. Five halls (Burning, Druid's, Frozen, Nomad's, Isle of the Dead) had no stored outline because gvg.report serves them only by map file id; found with the probe workflow (now takes named endpoints, `pick` and `grep`) from five reports Denning linked, added to the replays branch, and replays.mjs now asks by file id too. A walked-area outline remains as the fallback for a hall with none.
- Denning labelled Corrupted Isle, Isle of Meditation and Isle of Solitude (45 to 52 labels each). Checked as the engine would read them: both sides carry the same roster on every hall, every flag run starts within about 200 units of the replay-derived flag spawn and ends at the stand, and no route point is off the walkable area. The map page now draws areas cut to the walkable ground in a colour per type (smaller area on top), routes by type with a start dot and an arrow, points by shape, a key built from what the hall shows, and layer toggles; new label types (Miasma, Fireball zone, Footmen area, Obelisk flag stand, Gate lever, Teleporter entrance and exit, Collapse route, Teleporter one way). Findings for step 2 are in REDESIGN.md "What the first labelled halls show".
- Draft labels from replays (tools/maps/draft_labels.py; data/maps/draft/): flag stand and its area, flag spawns, res shrines, pits, bases, flag runs, front and back doors, teleporters with direction; Denning keeps choke points, NPCs, gates and hazards. Scored blind against his three halls: flag runs 69 to 177 units from his lines, front doors 72 to 245, back doors 59 to 211 (617 and 635 on Isle of Solitude, where the draft stops short), res shrines 130 to 220 (one at 1,066 on Isle of Meditation), both Solitude teleporters found and none invented elsewhere, bases 75 to 91% overlap, flag stand areas 56 to 77%, pits 45 to 57%. The door ring and the base rule were set on these same halls, so expect less on new ones. Map page: buttons for Vine seed, Hazard, Lava, Tar, Ice, Water. Rulings R-306 to R-309 appended.
- Draft layer on the map page: drafts for the 11 unlabelled halls (166 in all) are drawn dashed and listed with their evidence; Denning accepts each (copied into his labels with `from_draft`) or removes it (`dismissed` in his labels file); draft ids are stable across rebuilds. Not drafted where the replays are thin: some back doors (Jade, Nomad's, Druid's, Warrior's, Burning), flag runs on Isle of the Dead, several res shrines. Teleporters drafted on Jade (4), Nomad's (4), Imperial (2) and Weeping Stone (1), for Denning to confirm.
- Docs: REDESIGN.md added; SPEC section 1, METHODS "The blind test", CLAUDE.md (readability test covers what Denning answers; maps; never add a .py to tools/replay_analysis for tooling) and HANDOFF updated. RULINGS R-292 to R-305 appended.

## 2026-11-09 (night): batches 16 (90 matches) and 17 (60)
- Four Train batch runs failed on GitHub's side (matrix jobs never created, then runs with no jobs) after two runs were queued at once; chunk 6's 45 replays stayed stored.
- Denning chose to train them with 45 new picks as one batch (run 42675808241): 446 matches, 0.355 v 0.47 (+0.115), advice test 4 of 13 clear (power_play joins), P.26 cast prevention -> power play rejected, blind round 2 written, TQs ran.
- Batch 17 (run 42689196937): 506 matches, 0.382 v 0.475 (+0.094; worse by 0.027, interaction pairs swapped), advice test 6 of 13 clear; round 2 scored (Denning ahead), round 3 written.

## 2026-11-09 (evening): bundle 3 from Denning's rulings R-278 to R-287, the Model tab and the blind test page
- Site: a Model tab (`#/model`) holds the engine's pages (discovery now listed); Mechanics keeps the game pages. Blind test page (Model > Blind test): sealed rounds in `data/model/blind_tests.json`, 8 picks (6 random, 2 specific), calls saved with a reason, model call revealed after saving, scored in the browser; Train batch adds a round per chunk (input `blind`).
- Decisions (decisions.py; R-279 to R-281): offence/defence window 15 s; NPCs or DP fires on 3+ kills at or past the enemy footmen; play for 28 or the Lord redefined (from 10:00, a team that has taken enemy NPCs, push for the kill = 3+ at the enemy pit). Measurement layer: all prepared data rebuilt.
- Learned nodes (learnednodes.py): kinds fixed per node by perspective (NODE_KINDS); allocation decisions may be fixes despite the selection flag (ALLOCATION, R-282); pruning order adds Denning's not-clear links last, `denning_keep` never pruned (R-278); P.21 kiting kept by ruling, P.27 pre-kiting split off and P.19 let go by the data (R-283); expected directions and "reads backwards" labels on execution inputs (EXPECTED, direction_check, R-285), honoured in causalchain.py and tq.py.
- Discovery (discover.py; R-286): own_ and diff_ offered, enemy_ shown beside as what the enemy did. Fixed: the two-run history (`discovery_history.json`) was never committed by the workflow, so nothing could pass twice; now committed.
- Model page (modelpage.py): perspective line per node, Importance and Direction defined on the win model, lord damage in damage units with its two parts named, plain baseline names, glossary for boost clock, time down (sign corrected), arrival seconds, runner class and escorts, curve-shape notes, legend for allocation, reads-backwards and the pruning order.
- Docs: RULINGS R-278 to R-287; SPEC sections 1, 5, 6, 8 replaced; METHODS "The blind test".
- Direction signs ruled (R-288 to R-291): fight-outcome list as Denning gave it (no sign yet for pre-kiting, peel, spikes, healer focus); runner_escapes retired (a Shadow Step drops the flag now); four measurement proposals on the waiting list (control by distance to the stand, flag dropped by Shadow Step, hex value incl. trigger damage, NPC healing by target and kind). Fit layer only; carried by the next chunk.
- Blind test picks carry their context (both teams by zone, flags, stand, morale, pit NPCs, Lord damage, builds, the split in play), the question in words, a terms list and the gvg.report replay link (`/report/<id>#map`).
- Rebuild (run 42645700361, 56 min): 0.354 v 0.471 (+0.117), the same within noise; advice test 3 of 13 clear; collapse at its cap; round 1 of the blind test written. Then (report layer) the direction rule applied at the row too: a team that did more of a good thing than usual is never shown a fault or a fix for it (tq.py, causalchain.py).

## 2026-11-09 (later): outstanding items after the review, no chunk
- Update matches (run 42618614199): the last 20 listed matches stored, 0 remaining.
- Discovery run 1 on the variable catalogue (run 42618611013, 4.5 min): 1,633 tests, 137 passed the screen, 27 passed once, nothing offered yet (two-run rule). Enemy_* variables among them; ruling asked (HANDOFF.md).
- Blind test sealed (`data/model/blind_test.json`, seed 12): sealed fields base64 and never printed; `advice.py blind_score` added (refuses until every denning_call is filled; scores each call by the mean win-chance change of that choice among the 15 most similar decisions, and against what happened); `--blind-only` flag. The first pick (seed 11) printed its sealed fields and was discarded. Report layer only, nothing rebuilt.
- Readability test 2 filed (docs/tests/readability-2026-11-09b.md): verdict no; ten ranked blockers, five page-text only (queued, HANDOFF.md Next 2), the rest for the next bundle.
- Noted: workflow artifacts can't be downloaded from the chat workspace; the local route (cache pull, `analyze.py --all`) takes seconds.

## 2026-11-09: chunk 6 and the engine review
- Chunk 6 rebuild (Train batch run 42560128096, 50 min) landed with the footmen fix (footmen counted as losses in the win model): 356 matches trained. Honest test clear: glass box log loss 0.358 against 0.472 for strength alone (gain +0.114, 90% range +0.064 to +0.161); 84% of winners picked against 77%; matches even on strength 76% against 59%.
- Review of the engine against its goal (Denning's rulings in docs/RULINGS.md, "Rulings of the 2026-11 review", R-260 to R-277): one model family in four tiers, duplicates retired, strict time order in execution nodes with the enemy's response shown apart, inputs pruned, a standing selection check, discovery limited to decision and execution variables with a two-run rule, one bundled engine change per run of chunks, diff-style reports, a generated model page, a readability test, macro and micro answers kept apart, five new decisions, a variable catalogue and behaviour clusters, the query as the end product, period and strength-band checks, and the held-out advice test plus a sealed blind test as the goal test.
- Documents split: docs/SPEC.md (current state), docs/RULINGS.md (numbered register), docs/CHANGELOG.md (this file), docs/HANDOFF.md (short); session narrative removed from METHODS.md.
- Engine bundle 1 built the same night (one engine change): every learned-node input has a kind (learnednodes.KIND_BY_GROUP, kind_of); the enemy's concurrent response left out of the power-play and pit NPC loss fits and shown beside them (CONCURRENT; links K.5, P.21, P.23 -> K.4 and K.1 -> R.5 status "concurrent"); inputs capped at one per 20 events with the pruning order and a waiting list in causal_map.json (prune_plan); the selection check on decision and execution inputs ("marks the situation", selection_check; such inputs are never fixes in causalchain.py); nodes.py npc_loss and lord_kill retired as fitted nodes (TQ 4 and values read pit_npc_loss); five decision kinds added (decisions.py offence_or_defence, eight_v_eight_or_flag, who_defends, npcs_or_dp, play_for_28_or_lord; KINDS table); TQ 3 and TQ 4 answer macro, micro and "what the enemy did" apart (tq.execution_lines); cache keys by layer (cache.REPORT_LAYER, FIT_ONLY: report edits rebuild nothing); the generated structure page (modelpage.py -> knowledge/model.md); the report's "What changed since the last batch" diff; the TQs and snapshot every other chunk (workflow input tqs, GVG_TQS); candidate tests skipped when none are queued; the honest test by month and by strength band (common.period, strength_band); questions for Denning from the mechanisms (learning.questions_lines); usual_play.json refreshed each run.
- Rebuild after the bundles (run 42569970450, 29 min, no new matches): win model unchanged (0.358 against 0.472); all 11 learned nodes beat their baselines without the concurrent measures; by month September 0.443 v 0.577, October 0.282 v 0.395, November 0.317 v 0.363; by strength band even 0.525 v 0.65, moderate 0.33 v 0.469, uneven 0.083 v 0.078; advice test 2 of 13 kinds clear (runner_choice +1.1, split_or_stay +0.5), advice differs from the usual play in 1 to 5% of cases for most kinds; 5 collapse inputs pruned; 24 inputs flagged as marking the situation. Found: reactive execution inputs (disables, healing on own NPCs) read as faults in TQ 3 and 4 (open ruling in HANDOFF.md); flag-model readings in P.10 reclassified as state (STATE_FEATURES, takes effect at the next fit).
- Bundle 2 built: the variable catalogue (catalogue.py, 180 play variables per team-moment from the replay schema, prepared kind "catalogue") as discovery's only pool, with the two-run rule (discover.py, data/model/discovery_history.json); behaviour clusters with example moments and a page (behaviour.py, formerly discovery.py, knowledge/behaviour.md); the goal test (advice.py: held-out advice test in the report, the sealed blind test file); the query tool (ask.py: a match and a moment in; state, macro, micro, enemy response out).


## Session 4u (2026-11-08/09): the 1 September cutoff, chunks 3 to 5, pressure beyond damage

- Denning: matches before 1 September 2026 don't count in the model; new picks from 2 September on. Strength and lineup
  ratings keep every result (his ruling: replays only). Built as common.TRAIN_FROM / PICK_FROM, common.replay_ids(),
  model.batches() filtered (batches.json unchanged as a record), batch.py picks and adds filtered. Map flag spawns and
  Lord regeneration (game facts) keep every replay. Benchmarks rebuilt on the 176 counting matches before chunk 3
  (forensics, spikes, snare, Lord damage, carry capture, commentary variables; collapse_snare unclear -> supported).
- Chunk 3 (batch 12, run 42533187828, 42 min, full rebuild): 221 matches. Honest test clear: 0.344 against 0.421
  (gain +0.076, +0.008 to +0.141). Cap test chose a 10-point cap; pair test blocked morale x map pairs.
- Chunk 4 (batch 13, run 42536700459, 52 min): 266 matches. Honest test not clear: 0.384 against 0.455 (gain +0.071,
  -0.001 to +0.134); both got worse on the new matches (harder for strength too). Cap test back to no cap; pairs still
  blocked. footmen_diff candidate now improves the win model (0.384 -> 0.371): asked Denning whether to move it in.
  spike_killable_diff rose to 5th (0.213). split_diff: more own players splitting reads worse (-20 points at 4+).
- Clear in both chunks: at the boost clock, running (advanced +2.0, fought +3.2, held +3.7, fell back +3.2 against
  not running and fighting); collapsing on a split -4.8 / -3.2; late game 0 to 1 at the enemy Lord -18 / -20 (clear in
  chunk 4). No longer clear after the cutoff: after a wipe taking the flag (-2.8), boost clock not running and falling
  back, assassin runner. Runner choice usual is now the monk; warrior -1.7 and paragon -2.9 clear in chunk 4.
  Values (chunk 4): death -8.6, knight -8.4, Bodyguard -5.6, archer -4.2, footman -1.7 (now clear), capture +2.2,
  boost +5.7. Links: 34 of 88 supported; newly supported in chunk 4: P.1 -> power play (healer focus), K.11 ->
  collapse (defender snare present), C.strength -> fight outcome.
- Found (not fixed): TQ 4 of chunk 3 (cope v BcS 18:40): the knight died to BcS's Dervish inside the base with both
  Air Eles hitting from outside it; the NPC node counts only attackers in the base (read 1 v 4, 2% chance), and the
  team-position line showed all of cope "backside (contest)". Proposed: count ranged attackers hitting the pit from
  outside, and check the position labels in TQ 4.
- Discovery after chunk 4 (run 42544583826, about 3 min; pit NPC loss node added to the workflow): 958 tests, 56 passed
  the screen (about 22 by chance), 18 discoveries held for Denning (knowledge/discovery.md). Tactical/build ones: more
  hexes or heals on own bars -> fewer fights won; enemy energy denial against own heals and enemy strips against own
  prots (matchup terms); spike and knockdown builds split less; splitters' escape power -> split effect; own area
  damage -> split answer and run defence; enemy snares against own speed and own healing monks -> run defence; enemy
  healing monks -> fewer collapse kills. State ones: morale_total (fights), morale_diff (power play), down_diff_s
  (runs), main_diff (split answer), turtle_diff (split effect), map_flag_run (split chance). Nothing on capture speed
  or pit NPC loss. Awaiting Denning's rulings.
- Engine change after chunk 4 (Denning): 11 discoveries approved, footmen_diff in the win model, ranged attackers on the
  pit (attackers_outside), TQ 4 positions per player, and pressure.py (kiting and pre-kiting vs warriors, dervishes and
  assassins only; degen; baited interrupts; offensive knockdowns; disables; cast prevention) as map nodes P.21 to P.26
  into fight outcome and power play, plus the deaths and kill-conversion nodes, forensics and the snapshot. Snares: area
  = one target, measured Crippled where recorded on half the uses (METHODS.md "After chunk 4").
- Chunk 5 (batch 14, run 42555058885, 50 min, rebuild_forensics yes): 311 matches. Honest test clear again: 0.367 against
  0.452 (gain +0.085, +0.026 to +0.136). New links supported: power play <- enemy kiting, own knockdowns, disables, degen;
  fight outcome <- knockdowns (and the approved own hexes and heals); split answer <- own area damage. Not clear yet:
  baits, cast prevention, kiting and degen on fights. Deaths node: kiting lowers death risk (about -6 points at 3.5 s+
  in 10 s), degen on the player raises it (+10 at 7 to 10 pips), healers disabled raise it (+8.5); pre-kiting reads
  higher risk (+8, likely selection: players being chased). Power play: 1+ knockdowns per 10 s +15 to +20; the enemy
  kiting the power play's melee -9; heavy degen +12; disables read non-monotonic (-14 in the middle).
- Found: footmen_diff reads backwards (-42 points at +4) and values price a lost footman at +1.0: footmen only enter the
  replay's agent list once seen, so 'more own footmen alive' marks a base that was visited. Proposed: count footmen
  lost (deaths), or add the standard footman roster like the pit NPCs. Not built; ask Denning.
- TQ confidence was low on 5 of 8 answers: most fixes carried to the result price under half a win point.

### From METHODS.md: which matches count
- Replays played before `common.TRAIN_FROM` (2026-09-01, the replay index's UTC date) are left out of training and of
  every benchmark built from replays. `model.batches()` drops them from each batch (batches.json keeps the record, so
  batch numbers don't change), and `common.replay_ids()` is the replay pool for analyze.py --all, the shards, fight
  state, forensics, spikes, snare power, Lord damage, carry capture and the commentary variables. 52 of the 228 trained
  matches were before the cutoff (June 1, July 17, August 34), leaving 176.
- New picks come only from matches played on or after `common.PICK_FROM` (2026-09-02); `batch.py add` never adds a
  replay before the cutoff.
- Not cut (Denning): team strength and lineup ratings (strength.py, lineup.py, context.py) still use every stored
  result, since they only rate who is good. Game facts measured from replays also keep every date: each map's flag
  spawns and stand (benchmarks.py spawns) and Lord regeneration (benchmarks.py regen).
- Benchmarks rebuilt on the 176 matches before chunk 3: forensics.json, spikes.json, snare_measured.json,
  lord_damage.json, carry_capture.json, comms_variables.json (collapse_snare moved from unclear to supported).

### From METHODS.md: after chunk 4, rulings and pressure beyond damage
- **Discoveries approved** (chunk 4's discovery; the tactical and build findings, the state ones left out, enemy energy
  denial against own heals held for another run): fight outcome own_hexes, own_heals; power play
  enemy_strips_v_own_prots; split chance spike_build_own, own_knockdowns; split effect own_escapes_power; collapse
  healing_monks_enemy; run defence own_area_damage, enemy_snares_v_own_speed, healing_monks_own; split answer
  own_area_damage (lnrows.APPROVED).
- **footmen_diff** moved into the win model (held-out log loss 0.384 to 0.371 at chunk 4).
- **Ranged attackers on the pit**: the NPC nodes (npc_loss, lord_damage, lord_kill and the learned pit_npc_loss) read
  `attackers_outside`, enemy players hitting the pit NPCs from outside the pit in the last 5 s. TQ 4 lists each player's
  own zone at the second (the phase group's zone had put a whole team "backside").
- **Pressure beyond damage** (`pressure.py`, cache kind "pressure"), per player, measured from the replays:
  kiting and pre-kiting (enemy warriors, dervishes and assassins only), degen (conditions and degen hexes; pip sizes are
  game values, uptime measured; the replays record degen as no damage), baited interrupts (only the provable ones; the
  replays record an interrupt's target only when it lands, so a miss is matched to the enemy within casting range who
  had just cancelled), offensive knockdowns (and on casting targets), disables (Complicate, Power Lock, Power Block,
  Blackout; whether they landed is measured, how long the skills stay disabled comes from the skill text at the caster's
  rank, the one partly rule-based measure; Blackout's target, unrecorded, is the nearest enemy within touch range) and
  cast prevention (Shame, Guilt, Diversion: seconds up, and triggered = ended early right after the target started a
  cast). Thresholds (250 to 1,300 apart for a chase, 200 travel over 2 s and about 37 degrees for pre-kiting, 2 s for a
  bait's cancel) are definitions, not values; what each is worth comes from the nodes.
- Where they go: new map nodes P.21 Kiting, P.22 Degen pressure, P.23 Baited interrupts, P.24 Offensive knockdowns,
  P.25 Disables, P.26 Cast prevention, each linked into fight outcome (own minus enemy per 10 s) and power play (own per
  10 s, and the enemy's kiting and baits against it), all from Denning. The deaths node reads the player's degen, its
  kiting and pre-kiting, and its healers' disables and cast prevention; kill conversion the same for the target. Death
  forensics answer "Pressure beyond damage?", placed against the same role in every stored match (forensics.json
  degen_pip_secs, kited_s, healers_disabled_skill_secs, healers_castprev_secs); "why, in short" names one only above the
  usual band. The snapshot has a per-role table per minute played.
- **Snares** (movepower.py): area snares count one target in the formula (Denning: rarely more than one player is
  snared); uptime stays limited by recharge; the measured figure (hexes, and now Crippled where the replays record it on
  at least half the skill's uses, e.g. Mantis Touch, Signet of Pious Restraint, Earthen Shackles) replaces the formula
  once a skill has 15+ uses, capped at the recharge. Crippled from Hamstring, Caltrops, Pin Down and other attack skills
  is rarely recorded with its skill, so those keep the formula.
- **Footmen** (Denning, after chunk 5): the win model reads `footmen_lost_diff` (own minus enemy footmen lost so far)
  instead of footmen alive. A footman only enters the replay once something touches it, so "own footmen alive" marked a
  base that had been visited and read backwards (-42 points at +4; values priced a lost footman at +1.0). Deaths are
  always recorded. Readings that ran against expectation at chunk 5 (knockdowns on casting targets in fights,
  pre-kiting on deaths) are held for more data (Denning).

## Session 4t (2026-11-08): transcripts, snare and speed power, steps 3 and 4, the sharded workflow, chunks 1 and 2

- Agreed order (Denning): 1) Bounty's and Nick's transcripts, then one engine change and one rebuild; 2) build and test
  steps 3 (discovery) and 4 (chains from the node models) on the current matches; 3) speed-up (spread prepare and the
  event records across machines); 4) the large pull (450+), then discovery and step 4 on the full set. Whether to
  train the large pull in chunks of 50 to 100 is still to decide.
- Dropped by Denning: the two OG comms matches whose claims were never filed (OG v chic, OG v cope U); status
  "dropped".
- Bounty done (7 matches, 57 claims, data/commentary/bounty.json; METHODS.md "Commentary and comms"). BcS v Crew
  (3dd84ec7) was added to the replays; it isn't in a training batch yet: include it in the next batch.
- New measured variables (comms_vars.py; no engine change, comms_vars isn't part of the engine fingerprint):
  scattered (supported), monk_focus (contradicted), collapse_snare (unclear). Awaiting Denning's ruling on which become
  model variables.
- Nick done (5 matches, 47 claims, data/commentary/nick.json): Men v Team, NwAy v SKT, xxx v Men, NwAy v Men, cope v
  Book. Four replays fetched (457b3a21, b31ffe18, 506102ee, 8de08cc4) and BcS v Crew: none in a training batch yet;
  include all five in the next batch.
- Denning's rulings this session: drop open questions Q2, Q3, Q4, Q8, Q9, Q11, Q12, Q13 (done); K19 removed (Bounty spoke
  metaphorically about "one unit"); Return is not a snare; measure the cost of an instant overcap (done:
  `instant_overcap`); add healer focus to the model.
- Engine change built (Denning said go): snare and speed power (movepower.py) in the run, collapse, split effect and
  split chance nodes and in the run or hold decisions; the new split_or_stay decision; healer focus in the power-play
  and fight nodes; instant overcaps priced; Return not a snare (METHODS.md "Commentary and comms", "Built"). Rebuild
  run on GitHub (Train batch, add_batch no; run 42454350473, all jobs passed, about 30 min). The 11 replays not yet in a
  batch (BcS v Crew, Nick's four and others) go into the next batch.
- Rebuild readings (133 matches): glass box 0.375 against 0.463 (unchanged). Collapse node: defenders' snare power is
  its strongest input (splitters die about 5 points less often with weak snares, about 21 more with the strongest),
  link K.11 -> R.1 +0.0066 +/- 0.0036, just short of clear. Runner speed reads backwards (fast runners captured less,
  about -13 points at the top; capture slower by about 7 s): to check (selection, or speed skills used to escape rather
  than run). Healer focus: not clear in fights or power plays. Snare matchup in the decisions (raw, thirds): against a
  lot of enemy snare, not running and falling back at the boost clock -5.9, holding and fighting at an enemy pickup -6.0,
  running and falling back -5.0. split_or_stay: splitting +0.3 overall (not clear); +0.7 against little enemy snare,
  -0.8 against a lot; by map Solitude +2.7, Corrupted +1.9, Weeping Stone -1.8, Druid's -2.2. Captures overcapped
  within 10 s -3.6 (not clear) against +2.4 for captures held longer (clear).
- Step 2 of the agreed order, built (METHODS.md "Steps 3 and 4"): causalchain.py (chains from the node models, fixes
  carried forward; shown in every TQ beside chain.py for comparison) and discover.py with the "Discovery" workflow.
  Tested here on the current matches (all four TQs produce a node-model chain; discovery on the collapse node). Then a
  Train batch rebuild (add_batch no) and the Discovery workflow were started on GitHub.
- Results: rebuild run 42485467768 passed; every TQ shows a node-model chain (e.g. TQ 2: the 26:42 fight read from
  NwAy's side, followed back to Men's 24:07 fight with 1 player in it; fix priced +1.1 win points). Discovery run
  42486486170 passed: 915 variable-by-node tests, 92 passed the screen (about 21 by chance), 27 discoveries held for
  Denning (knowledge/discovery.md). Most are state (morale, numbers, stand, boost clock, flag lead) on the fight, flag
  swing and run defence nodes; the tactical ones: snare skill counts on runs (enemy snares -> fewer captures, run
  outcome; own snares -> fewer enemy captures, run defence), enemy prots and own Deep Wound on split effect, the enemy
  carrying a flag on power plays.
- Known limits of step 4: carries through a fight to a later node shrink a lot (only a share of a lost fight's
  deaths), so most fixes price small at the result; NPC-loss chains stop at the fight before (the NPC node is not a
  learned node yet); "diff" variables have sharp steps near 0 (a -0.01 ready-interrupt difference pushed 16 points).
- Denning's rulings (yes to all): node-model chains replace chain.py; discoveries approved as suggested; minimum-change
  rule added. Plus: runner speed now sets the minimum time to capture; who carries is a variable and a decision
  (runner_choice). Speed-up built (shards). METHODS.md "Runner speed, who carries ...". Rebuild started to test.
- Readings (rebuild 42494559984, same in 42497408038): minimum capture time (runner speed) is now a strongly supported
  link in run outcome, run defence and capture speed (the old raw runner_speed read backwards); part of it is where the
  runner is, not only its speed (read at 5, 15, 30 s into the run). Snare skill counts supported on both run nodes;
  the approved state variables supported on the fight node. Who carries (runner_choice, against the Mes/A-type
  mesmer, the usual): warrior -2.7, elementalist -2.1, paragon -2.7 (clear), assassin -8.9 (clear but partly who
  chooses it), monk -0.8, dervish -1.0 (not clear), ritualist +0.1, necromancer +1.1. runner_class inside the run nodes:
  not clear yet.
- Speed-up result (full rebuilds): shards 3 to 4 min, prepare 11 to 16 min, rows shards 2 min, parts 4 to 5 min (the
  learned part fell from 13 to 4), finish 4: about 32 min either way, because prepare is now the long pole: the win
  model's tables (5 min), cap tests, held-out fits and calibration (4 min) and the fight-state predictions for every
  stored replay (5 min) all run on one machine. Proposed: a third shard round for the tables and fight-state, and 8
  shards for the large pull.
- Denning: build the speed-ups (done: 8 shards, a tables round for fight state and win-model tables, 8 rows jobs);
  train the large pull in chunks of 40 to 50 matches, each with a learning report and the TQs.
- Large pull, chunk 1 started: Train batch with pick 35 (any month) plus the 11 stored replays not yet trained (BcS v
  Crew, Nick's four, others) = about 46 matches; also the first run of the full sharded workflow.
- Chunk 1 done (run 42513495642, about 33 min for 48 new matches; batch 10, 181 matches trained). The win model now
  beats strength alone clearly for the first time (log loss 0.314 against 0.433, gain +0.119, range +0.017 to +0.214);
  every learned node adds to its baseline (flag swing, capture speed and split effect did not before). split_diff
  candidate improves the win model (0.314 -> 0.307): asked Denning whether to move it in. TQ 3 crashed on a phase with
  no group for the team (events.power, fixed; answered in the chat and written into the report).
- Denning's answers on chunk 1 built (METHODS.md "After batch 10"): split_diff into the win model; holds (an 8 Monk
  holding without trying to cap) kept out of run measures; pit_npc_loss learned node (NPC chains price fixes); collapse
  context (split NPC damage, defending NPCs alive, split DP, split healers and self-defence, defenders' damage). Runner
  choice penalties (assassin, paragon): not addressed for now (Denning).
- Chunk 2 done (run 42520678255, about 45 min; batch 11, 228 matches, 47 new). Honest test still clear but smaller
  (0.345 against 0.439; gain +0.094, range +0.02 to +0.158; batch 10 was 0.314). pit_npc_loss node works (0.370 against
  0.515; TQ 4 now has a chain). Collapse node: def_dps and split_dp supported. Runner choice: only assassin still clear.
  Collapsing still -4.2 clear. Raised with Denning: npc_damage_5s is the loss happening, not a fix (move to context?),
  and defenders_elsewhere should chain back to the fight before; test whether split_diff hurt the honest test.
- Denning on chunk 2: disregard the three engine questions (npc_damage_5s as context, chaining defenders back to the
  fight, testing split_diff), so TQ 4 will keep listing "no damage on the NPCs" as its top fix: read past it. Asked
  what discovery is and what is left; told him the issues: single-batch findings move (act on results clear across 2
  or 3 chunks; offered to mark them in the report), "partly who chooses it" readings are hints, the honest test dipped
  once, the hold and collapse thresholds are Claude's definitions, NPC and Lord data gaps, mixed seasons, run time
  growing (about 45 min a chunk). Open: whether to run discovery now or after chunk 3; whether to mark findings that
  stay clear across chunks.
- Next: discovery (Discovery workflow; held for Denning's approval), chunk 3 (Train batch, pick about 45, add_batch
  yes), explain it (snapshot, TQs, questions), update this file.
- Found: data/model/usual_play.json still holds the 30-match readings; the current ones are only in
  data/model/reports/latest.md (check whether the Train batch finish step should rewrite it).

### From METHODS.md: Bounty's and Nick's matches, new measures, the engine change
- Bounty's seven matches (session 4t, 2026-11-08): Apes v cope, 옷옷옷옷 v Book, OG v hold, Team v push, cope v hdm, True v
  One and BcS v Crew (replay fetched for it). 57 claims in `data/commentary/bounty.json`, each checked. Nick's five
  (same session): Men v Team, NwAy v SKT, xxx v Men, NwAy v Men, cope v Book (four replays fetched). 47 claims in
  `data/commentary/nick.json`.
- New measures in `comms_vars.py` (144 matches): `monk_focus` (groups hitting mostly healers kill in 19% of phases
  against 13%: contradicts "don't go after the monks", partly selection, tactics `K6`); `collapse_snare` (a snare carrier
  among 2+ defenders, Return not counted: a splitter dies 20% against 11%, supported, `S33`); `instant_overcap` (16% of
  captures are overcapped within 10 s; the capturing team lost more than it killed from the run's start to 30 s after,
  22% against 16%, supported, `F36`; partly the situation); `split_size` (3-player against 4-player splits into the
  base: a pit NPC taken 36% against 35%, unclear, `S38`); `scattered` kept as a measure only (Denning: Bounty spoke
  metaphorically). New lines `F36`, `F37`, `P15`, `S38`, `S39`, `O4`, "cycle" and "inaccuracies" under Language.
- Built (Denning's go-ahead, session 4t), one engine change and one rebuild:
  - `movepower.py`: snare power and speed power per player, from the skill data at the player's attribute rank
    (match data attrs, rank 12 when unknown): snare = slow fraction x seconds per use (capped at the recharge) x
    targets (adjacent 1.5, nearby or area 2) x uses per minute; speed = speed bonus x seconds per use x uses per
    minute; escapes = Shadow Step skills. Return is an escape, never a snare. Hex snares are checked against the
    replays (`movepower.py bench`, data/benchmarks/snare_measured.json, in the cache fingerprint): with 15+ uses the
    measured slowed seconds per use replace the formula (e.g. Siphon Speed 6.2 s per use against 13 by formula: hex
    removal). Crippled can't be measured (the replays record it only now and then), so condition snares keep the
    formula.
  - Learned nodes: run outcome (runner speed and escapes, enemy snare power within 1,300 of the runner), run defence and
    capture speed (runner speed, defenders' snare power near the runner), collapse and split effect (snare power of the
    defenders who actually came; splitters' speed and escapes), split chance (team snare, speed and escape power
    replace the skill counts), power play and fight outcome (healer focus: share of damage on enemy healers, P.1).
    New groups K.13 (mobility) and K.11 (control) in those nodes; the collapse node's old C.builds counts are gone.
  - Decisions: every decision record carries the snare matchup (own and enemy snare power of the live players, own
    speed power); the boost clock, enemy pickup and the new split_or_stay decision are adjusted for it and broken down
    by it in thirds (report "By snare matchup"); split in base carries the defenders' snare power. split_or_stay: every
    30 s from 1:00, a team not already splitting with 6+ alive either starts a split in the next 30 s or stays.
  - values.py prices captures overcapped within 10 s apart from those held longer (`F36`).
  - `buildfeat.FEATURES["snares"]` no longer counts Return.

### From METHODS.md: steps 3 and 4 of the learned causal map
- **Step 4, chains from the node models** (`causalchain.py`): a result is traced back through the learned nodes. The
  result's node reads the moment with a held-out model (learnednodes.py now keeps each node's six fold models of the
  "all" variant and which fold each match was held out in; data in the cache under fits/lnode, keyed by
  learnednodes.py alone). Each variable's push = its curve at this moment minus its curve at its usual value (the
  median over every trained row of the node; the nodes are additive, so the pushes separate). A variable that is
  another node's result is followed back (flag lead -> the flag swing before; own deaths and numbers -> the fight
  before; a split answer's latency -> the split-answer node) when it sits on the bad side of its usual value, the two
  biggest groups at each link, back to the last reset or 3 min, at most 4 links deep; a fight read from the enemy's
  side has its "enemy_" numbers read as this team's own. Fixes: any play variable (P, K, A.mesa_free groups) among the
  pushes, set to its usual value; the node is read again and the change carried link by link (seconds carry as they
  are, and a flag swing keeps a carried lead; a fight's chance carries as that share of a lost fight's deaths, the
  median over every trained fight, read at full size and scaled because the curves are in steps) to the result's
  node, priced with values.py (a fight = the deaths of its losing side; flag seconds through the held-out win model).
  Shown in each TQ beside the rule-based chain (chain.py) while the two are compared; it replaces the rules once
  Denning approves. Context (strength, builds, clock, map) is never a fix.
- **Step 3, discovery** (`discover.py`, workflow "Discovery", one node per machine): every variable the engine measures
  about a team at a moment (the win model's state table, prefix s., and the build and matchup features with snare,
  speed and escape power, prefix b.) is joined to each node row (same team, the 5 s state at or before the row) and
  tested on unseen matches with the node's own 6 folds. Screen: a one-variable glass-box curve fitted on top of the
  node's held-out readings (its starting score), gain = held-out loss without minus with. Confirm: the best 6
  screen gainers per node refitted as a link test (the node plus the variable against the node). A discovery =
  confirmed gain more than twice its spread and up in at least 5 of 6 folds; held for Denning's approval
  (data/model/discovery.json, knowledge/discovery.md), never added automatically. The page states how many screen
  passes chance alone would give. Tested here on the collapse node (92 variables, 49 s): no discovery yet; closest
  morale difference and fight state (not clear).

### From METHODS.md: runner speed, who carries, approved discoveries, the speed-up
- Runner speed (Denning): the runner's speed skills set the minimum time required to capture. scoreboard.py's carry
  speed per player = the faster of its measured full carries and the average carry speed (205) times one plus its bar's
  speed bonus (movepower.speed_bonus: speed power / 60, capped at the bar's biggest single bonus, since boosts don't add
  up). Every flag ETA, response, flag lead and "slower than possible" follows. The run nodes' raw runner_speed is
  replaced by min_capture_s: seconds the carrier needs at least from where it is, at that speed.
- Who carries (Denning: capping on a warrior, a midline, a dervish or a monk is a strategic decision): runner_class
  (common.runner_class, the carrier's primary profession, coded 0 to 9) in the run outcome, run defence and capture
  speed nodes (P.10), and a new decision, runner_choice (every fresh run from the spawn; the usual play compares
  carriers in similar situations and by snare matchup).
- Approved discoveries (Denning, all as suggested): state variables as context (S.scoreboard) in the fight, flag
  swing, run, power-play and split nodes; snare skill counts on the run nodes (enemy snares on run outcome, own snares
  on run defence) and the defenders' prots on split effect (C.builds); Deep Wound on split effect left for more
  matches. Joined onto the rows from the state table and build features (lnrows.APPROVED).
- Chains: the node-model chain (causalchain.py) replaces chain.py in the TQs. A cause or fix must sit at least a
  quarter of the variable's spread (interquartile range over the node's rows) from its usual value.
- Speed-up: Train batch now runs fetch -> four shard jobs (cache.py shard k 4: analysis, node rows and event-layer
  records for every 4th match) -> prepare (merges the shards' cache files; analysis then takes 15 s) -> four rows jobs
  (cache.py shard_rows k 4: the learned nodes' rows, which need the event-layer values from every match) -> parts ->
  finish. First sharded run (full rebuild, before the rows shards): shards 2 to 4 min, prepare 11 min (9 of them the
  win model's tables, held-out fits and calibration), the learned part 13 min (rebuilding every node's rows on one
  machine, slowed by recomputing each bar's powers per row: now memoized), finish 3 min; 32 min in all.
  Second run (with the rows shards): learned part 13 -> 4 min, but prepare 16 min (tables 5, cap tests, held-out fits
  and calibration 4, fight-state predictions for every stored replay 5) became the long pole. Third round (Denning,
  before the large pull): seven "tables" jobs (cache.py shard_tables: the fight-state predictions for one of the six
  groups and that group's win-model tables and value events; "extra" = the stored replays outside the training set,
  fightstate.build_group / build_extra, the same fits as build) between the shards and prepare; shards and rows jobs
  now 8 machines each.

### From METHODS.md: after batch 10 (Denning's answers)
- **split_diff moved into the win model** (features.py VARIABLES; it was a candidate since batch 1). Held-out log loss
  0.314 to 0.307 in batch 10's candidate test.
- **Holds** (`common.is_hold`, `carry_progress`): Denning, an 8 Monk sometimes holds the flag without trying to cap. A
  carry of 10 s+ that does not end in a capture and never closes a quarter of the way to the stand is a hold. Holds are
  marked on every flag run (`hold`, `progress`) and kept out of run_outcome, run_defence, the runner choice and the
  runners table's capture rates (the table shows them as a column).
- **pit_npc_loss learned node** (R.5): the node model's npc_loss moments (nodes.py) read for the defending team, with
  defenders in the pit as play (P.11), healing on the NPCs (K.6) and damage on them (K.1). causalchain.start_npc starts
  from it (the last moment in the 15 s before the loss), so TQ 4 can price fixes.
- **Collapse context** (`common.split_context`): Denning, collapsing on a split depends on what the split can get
  NPC-wise, the death penalty on the split character and whether it can be killed. The collapse node gains split_dp
  (K.9), split_healers and split_self_defence (K.5), def_dps (K.1), def_npc_value (S.scoreboard) and split_npc_dps
  (C.builds); split-in-base decisions carry the same in their situation, so the usual play compares collapses in like
  situations.

## Session 4s (2026-11-07): the batch 9 rulings built, five rebuilds, calibration

- Built 16 of the 17 batch 9 proposals (all but 10) in one engine change; details in METHODS.md "Rulings after batch 9".
  Notable: the data picks the `spike_killable_diff` cap (10 to 25 points, or none; data/model/cap_choices.json); win
  chances go through a calibration by minute (data/model/calibration.json); forensics position uses the last 3, 5 or
  8 s, whichever best separates deaths from other fight moments (forensics.json "position_window"); the Lord damage
  node is fitted in two parts; values are against matched moments.
- Tested here on 12 matches end to end (every report section and TQ ran). Fixed on the way: a direction correction
  leaves no spread on its curve; the robust loss diverged until centred and scaled.
- Train batch: `timeout-minutes` 180 for every job; new input `rebuild_forensics` (run `forensics.py bench` first).
- Rebuild done (27 min whole run on GitHub; a first try failed on a report line, fixed). Readings at 133 matches:
  glass box log loss 0.375 against 0.463 for strength alone (not yet clear); cap test chose no cap on
  `spike_killable_diff` (none 0.3758, 25 points 0.3761, 10 points 0.3869); calibration's biggest correction is 6 to 12
  min, where teams given about 3.5% won 21%; position window chosen 3 s (AUC 0.632 against 0.624 for 5 s and 0.611 for
  8 s, so the windows differ little); Lord damage node now honestly adds (typical error 71 against 92); flag swing and
  split effect now narrowly beat their baselines, capture speed still doesn't; values against matched moments: a death
  -8.9, a knight -9.0, a capture +1.5.
- Denning on the rebuild: mid-game comebacks about one in five match what he sees (tactics W13); a knight is worth
  about a death (W12); the 3 s position window is acceptable.
- Found reading the rebuild's report, proposed to Denning (not built; each is an engine change, so bundle them before
  the next run): (a) calibration's pooled flat stretches erase small changes (TQ 1 read 22 s of flag lead as +0.0
  points): a per-band logistic recalibration (a shift and a slope per minute band) never goes flat; (b) morale x map
  geometry pairs are now the model's top terms (morale x pit-to-stand 0.717) and drive the biggest surprises (-45.5):
  test blocking them on held-out matches, the data to decide, like the cap test; (c) TQ 4's NPC-loss what-ifs read
  more defenders as more loss (27.5% -> 31.1% -> 34.3%) against the node's own defenders curve: mark a what-if that
  runs against the variable's main curve as coming from a pairing; (d) TQ 4 text says "after it entered the base" for
  a split that never entered.
- Denning approved (a) to (d), built (METHODS.md "After the batch 9 rebuild"), plus his split-depth variable for the
  collapse node (P.20); answers recorded on tactics K14 (energy isn't tracked, so deliberate deaths can't be told
  apart) and S32 (a quick collapse that fails to kill fails twice). Second rebuild started (add_batch no).
- Second rebuild done (all sections ran): pair test kept the morale x map pairs (allowed 0.3752, blocked 0.3937);
  cap test again no cap; split depth not clear yet (gain -0.0004 +/- 0.0038, each reading alone not clear); the
  collapse timing readings alone moved from supported to not clear between the two rebuilds (near the line; the
  group P.9 stays supported); TQ 4's backwards what-ifs now marked "from a pairing"; values: death -9.5, knight -9.1,
  boost +5.8, possibly deliberate healer death -8.0.
- Found, proposed to Denning: (e) TQ 1 still reads 22 s of flag lead as +0.0, because the win model's flag_lead curve is
  small (at most 2.6 points) and runs backwards at both ends (-129 to -67.5 s reads +0.4, +67.5 to +129 s reads -1.6):
  force its direction upward; (f) the shift-and-slope calibration misses some cells (12 to 18 min: predicted 93%, won
  92%, calibrated 77%; 6 to 12 min: 3.5%, won 21%, calibrated 12.7%): a pooled lookup joined by straight lines between
  the pooled blocks' middles would be as accurate as the first form and never flat.
- Denning approved (e) and (f), built (METHODS.md "After the batch 9 rebuild"). Third rebuild: calibration followed
  the data except at the ends (lines to 0 and 100 overrode the most common cells); carrying the end segments on
  helped (12 to 18 min) but not after 18:00 (0.4% predicted, 7.6% won, read 0.5%); the outer knots' values now hold
  beyond them. Fifth rebuild done: calibration follows the data across every band (where neighbouring cells run
  backwards they are pooled, e.g. after 18:00 0.4% won 7.6% and 3.4% won 1.0%, both read about 4%); glass box 0.374;
  values: death -9.2, knight -9.2, boost +5.4, capture +1.5; after a wipe taking the flag -4.5 and collapsing on a
  split -4.2 (both clear). Forced flag_lead is flat across deficits of about 30 to 129 s, so TQ 1 still prices 22 s
  saved at +0.0 (an honest reading; step 4 prices saved seconds through the chain).
- Next: the commentary transcripts (Bounty's six, then Nick's one; Denning attaches them), then more batches.

### From METHODS.md: rulings after batch 9
Sixteen of the seventeen proposals from the batch 9 review approved and built as one engine change (item 10, links
changing status only after two batches in a row, declined: links keep changing status batch by batch).
- **Win model** (`model.py`, `data/model_corrections.json`): `lord_damage_diff` has no curve of its own (`main_drop`;
  its pair with the clock stays); build-fixed values (Lord damage per second, spike build) never pair with morale
  (`no_interaction`); `down_diff_s` can only rise (`direction`); `spike_killable_diff` gets the cap the data picks
  (`cap_test`, options 10, 15, 20, 25 points or none: `model.cap_test`, run by `cache.py warm` before the held-out
  models, the choice and every option's held-out log loss in `data/model/cap_choices.json`, a hash input of the
  held-out models).
- **Calibration by minute** (`model.calibrate`, run by `cache.py warm` after the held-out models): every training match
  predicted by its group's held-out model every 15 s, grouped by minute band (0-6, 6-12, 12-18, 18+) and predicted
  chance, against how often those teams won; thin cells lean on the model's number (5 matches' worth) and each band is
  made to rise with the prediction. `WPModel.explain` reports the calibrated chance (the contributions stay as
  learned), so values, the usual play, why chains and the TQs all use it; `raw_chance` gives the model's own number.
  Pooled cells give flat stretches, where small changes read as none.
- **Usual play** (`decisions.py`, `usual.py`): the choice is what the team did in its first 5 s (`first_actions`,
  movement threshold scaled to the window); the 20 s actions stay as context.
- **Power plays** (`fights.windows`, `decisions.py`, `lnrows.py`): pushing, pressure and the power-play node's damage,
  enemy prots and healing, spikes and Blind are read up to the first kill (the whole window without a kill);
  `window_s` stays the whole window.
- **Values** (`values.py`): each event against matched moments without it (same 2-minute band and 10-point win chance
  band, no event of that kind in the window; the band alone when a cell has under 20 moments). Context (strength, build
  skill counts, flag lead, morale, the clock, the res timer) is never priced as a cause (`context_only`).
- **Snapshot** (`snapshot.py`): winners against losers compared at moments when a held-out model gave the team 35 to
  65%, with every moment beside it, labelled as including who was ahead.
- **Lord damage node** (`nodes.py` `TwoPart`): chance of any Lord damage in the window (classifier) and the amount when
  there is some (regressor on log(1 + damage)); typical error from the middle of the predicted spread against the
  median, spread explained from its average against the average. Number nodes now "add" only if no worse on typical
  error and better on the spread explained (flag answer too).
- **Kill-conversion node**: `attackers_blinded` is seconds the burst's physical attackers spent Blind, 3 s before to
  3 s after the burst.
- **Reworked learned nodes**: flag swing gets the flag model's readings (each team's ETA, carrying now, can capture
  before the boost); capture speed gets control on the runner in the first 10 s (K.11); split effect gets the
  defenders' pit NPC value and free defenders at entry (S.scoreboard -> R.5, a Claude hypothesis). Flag swing and
  capture speed use a robust loss (pseudo-Huber, delta = the rows' median absolute deviation, fitted on the result
  less its median: the library's default diverges); split effect uses fewer bins, larger leaves and more smoothing.
- **Forensics position** (`forensics.py`): judged on the last N s before the death (nearest healer, nearest enemy,
  allies and enemies in casting range, front share), N chosen by `forensics.py bench` from 3, 5 and 8 s as the window
  whose nearest enemy and enemies in range best separate deaths from fight moments without one (AUC; in
  `forensics.json` "position_window"); the window's medians stay as context. The shortest window partly measures the
  kill itself (attackers close in on a dying player); read the AUCs with that in mind. Rebuild with the Train batch
  input `rebuild_forensics`.
- **TQs** (`tq.py`): a what-if is marked unreliable when a change takes a variable outside the node's training range,
  or when a ladder (one more, two more defenders) stops moving the same way; unreliable readings are shown but kept
  out of the confidence and the fixes. TQ 4 tells a split's own NPC kill from a wipe's conversion and judges the
  split's answer only on the split's kills.
- **Train batch**: every job may run 3 hours.

### From METHODS.md: after the batch 9 rebuild
- **Calibration, third form** (after the second rebuild): per minute band, cells shrunk toward the model's number in
  thin cells and pooled where they run backwards, then joined by straight lines between the pooled blocks' middles
  ("knots"), blended by minute between band middles; beyond the outer knots, the outer knot's value (each is a
  pooled block's middle, so only predictions more extreme than that block's average read flat; lines to 0 and 100, and
  then carrying the end segments on, overrode the ends where most rows sit). As accurate as the first (pooled lookup) form, never flat, no jump at a band edge. (The second form, a shift and a slope per band, missed some ranges: 12 to 18 min, 93% predicted,
  92% won, calibrated 77%.)
- **flag_lead** forced to rise (Denning): the curve was small and ran backwards at both ends. Forced, its deficit end is
  flat from about -129 to -30 s (-3.3 points), so TQ 1 still reads 22 s saved at -78 s as +0.0: the win model credits
  flag position there through the stand, knights and morale, not the lead itself. Pricing saved seconds needs the
  chain through the flag-swing and run nodes (step 4).
- **Pair test** (`pair_test` corrections, tested together with the cap tests by `model.cap_test`): morale (difference
  and total) with the map's geometry, allowed against blocked on held-out matches; blocked only if that predicts
  better (`cap_choices.json` "pairs").
- **What-ifs from a pairing** (`tq.what_if`): a reading that runs against the changed variables' own curves is marked
  "[from a pairing" and kept out of the fixes and the confidence, like unreliable readings.
- **TQ 4**: a split that never entered the base has its first defender counted from the split's start, without the
  base benchmark.
- **Split depth** (Denning's hypothesis, map node P.20 -> R.1, collapse node, each reading also tested alone): the
  split's nearest member's distance to the defending pit at the first defender's arrival, and its median over the split.
- **K14, S32** (tactics): a monk's death before the res may be deliberate, but that turns on energy, which the replays
  don't record; a quick collapse that fails to kill fails twice (no kill, and the split stays in the base).

## Session 4r (2026-11-07): the Train batch split, batch 9, the 17 proposals

- Train batch split (`.github/workflows/train-batch.yml`, METHODS.md "Train batch on GitHub"): prepare -> six parts at
  once (main, learned, cands, nodes:deaths, nodes:lord_kill,npc_loss, nodes:kill_conversion,lord_damage,flag_answer) ->
  finish (values priced, TQs, snapshot, cache push, commit). `learning.py part <name>` / `learning.py finish`;
  `learning.py` alone still runs everything on one machine. Checked: a rebuild of batch 8 through the split gave the
  same report apart from processor noise.
- Run times: rebuild with no new matches 11 min whole run (prepare 3, longest part 3, finish 4). Batch 9 (20 new
  matches) 27 min: prepare 12 (fetching 20 replays 3.3 min at gvg.report's 4 s spacing; preparing the new matches'
  data 7 min), main part 12 (learned nodes 6.7 min building the new matches' event records, values 2.3), finish 2.5.
  After batch 9 the learned nodes got their own part (`learned`; not yet run on GitHub, first use next batch), which
  should take the main part to about 5 min. Further speed-up if wanted: spread prepare's per-match data across machines.
- Batch 9 report: glass box log loss 0.377 against 0.463 for strength alone (gain +0.086, range -0.035 to +0.196, ahead
  but not yet clear; the new matches were harder for strength alone, 0.412 -> 0.463). Morale now leads (0.691), with
  new morale x Lord-damage-rate interactions. Learned-node links supported: 17 of 50 (13 before). Newly supported:
  damage against the usual -> kill conversion; commitment (pushed) -> kill conversion; split size and free defenders
  -> split answer; defender snares and split speed -> collapse deaths; split-answer latency -> deaths. Flipped to not
  clear: split size and main numbers -> collapse deaths. Rejected by data: Blind on own players in the last 10 s ->
  kill conversion (Claude's link, tiny either way, -0.0007; it was supported at +0.0011 in batch 8, a near-line
  flip). Denning's held link (Blind on the enemy frontline -> fights) moved from rejected to not clear yet.
  Usual play: split in base, collapsing -4.3 against defending without a collapse (clear); after a wipe, taking the
  flag -4.6 against pushing the pit (clear, smaller than at 53 matches); boost clock, not running and falling back
  -4.0 (clear). Values: a death -5.0, a death while the team is boosted -19.8, a knight -4.8, the Bodyguard -3.8, a
  capture +1.7.
- After batch 9, from Denning (engine changed, not yet rebuilt):
  - Blind is measured as time spent Blind, not the number of Blinds (eventlayer.py keeps each Blind's end and whether
    the target is a physical attacker; lnrows.py `_blind_secs`). Every Blind now counts: the replays leave the caster
    blank on 56% of Blinds (799 on players in 133 matches, 353 with a caster), and the old code dropped those.
    Features: `blind_secs_on_own_10s` (K.11 -> K.4, own attackers only), `blind_front_secs_diff` and
    `blind_defensive_secs_diff` (P.19 -> R.2). K.11 -> K.4 reset from rejected to hypothesis.
  - No boosted-death variable. The boosted / not boosted death split is gone from values.py: it measured position
    (later in the match, already winning), not the death (tactics K18 revised with the matched comparison).
  - The event-layer, learned-node and value data for all 133 matches rebuild on the next Train batch run. Expect the
    `learned` part to be much slower that one time (perhaps 30 to 40 min). Make the forensics position fix first if
    Denning approves it, so there is only one rebuild.
- **Proposed after batch 9, with Denning's rulings** (numbers from 133 matches). All approved except 10; built in
  session 4s as one engine change (METHODS.md "Rulings after batch 9"), then a full rebuild of the 133 matches:
  1. **Approved.** Win model: drop the `lord_damage_diff` main term, keep only its pairing with the clock (curve is a sign marker:
     +-7 to 9 points once any Lord damage exists; the most negative band reads +31.6, backwards; teams ahead on Lord
     damage won 88%, with alive +0.94 and morale +78: it marks who got into the pit, not the tiebreak).
  2. **Approved.** Win model: cap or block pairings of build-fixed values (Lord damage per second, spike build) with morale. The batch
     7 cap covers the main terms only; morale x Lord damage per second came back 3rd and 4th (0.42 each).
  3. **Approved (after an explanation).** Win model: test caps on `spike_killable_diff` (step of 35 points at one player; at the same morale the real gap is
     about 13: 64% / 50% / 37% won at morale -20..20).
  4. **Approved: force the direction (more enemy time down can only help); don't drop it.** Win model: `down_diff_s` direction forced (more enemy time down can only help) or dropped (backwards for 7 to 38 s;
     mirrors alive_diff).
  5. **Approved.** Win model: calibration by minute from held-out predictions (a readable lookup). At 6 to 12 min teams given 1% won
     4.7% and 99% won 94.9%; from 12 min 0.9% won 6.4%. Every win-point value and choice effect uses these numbers.
  6. **Approved.** Usual play: a choice is what the team did in its first seconds, not over the next 20 s (advancing over 20 s is
     partly the fight's result: held, advanced +5.5 and held, fell back -4.1, both clear).
  7. **Approved.** Power-play node: damage, pushing and control measured only up to the first kill (as the fight node does).
  8. **Approved.** Context-only variables (strength, build skill counts, flag lead, morale, minute) never priced as causes or offered as
     fixes (values.py prices strength_gap and the enemy's strip-skill count as causes now).
  9. **Approved.** Snapshot: winners-against-losers comparisons replaced by comparisons at the same win chance, or labelled.
  10. **Declined: links keep changing status batch by batch.** Learned links change status only after two batches in a row (stops near-line flips).
  11. **Approved (after an explanation).** Lord damage node: verdict rule fixed (typical error 125 against 92 for the median, still labelled "adds") and a
      form suited to its skew.
  12. **Approved.** Rework the three learned nodes still no better than the baseline (flag swing, capture speed, split effect).
  13. **Approved.** Kill-conversion node: attackers' Blind in seconds, like the new Blind measure.
  14. **Approved (after an explanation).** Forensics position judged on the last 5 s (TQ 1 fault).
  15. **Approved.** Values against matched moments without the event (same minute, same win chance).
  16. **Approved.** TQ what-ifs that aren't monotonic marked unreliable (TQ 4).
  17. **Approved.** TQ 4 text separates a wipe's NPC loss from a split's.
- Other batch 9 questions, Denning's answers:
  - BcS v Crew 15:11 (all five living BcS players went backside to convert with their pit empty and 3 dead): Denning
    doesn't know; let the data decide. Step 3 (discovery) and step 4 (chains priced from the node models) should
    measure going backside to convert against the alternatives in that state.
  - Crippled runners captured more (+16 points, even at the same point of the run): leave for now.
- Faults found in batch 9's TQs (not fixed yet):
  1. forensics.position uses the median over the whole window before a death, so a ranged spike that closes in for the
     last seconds reads "not in position" (TQ 1: Apes Necromancer at 1:54 in d9d75e55 shown 1,648 from the nearest
     enemy; the replay has Fun's Water and Air Eles at 701 and 739 for the last 4 s). Proposed fix: judge position on
     the last 5 s (as the healer distance already is), keep the window median as context; then rebuild
     `data/benchmarks/forensics.json`. Engine change (cache rebuilds): ask Denning first.
  2. TQ 1's chain stops at "already behind on flags at 4:15" although the swing began at 1:45 (chain.py's hand rules;
     step 4 replaces them).
  3. TQ 4's NPC-loss what-ifs aren't monotonic (two more defenders 74.0% to lose, one more 72.3%): the node read
     outside its data; show such readings as unreliable or cap them.
  4. TQ 4 says the split was answered on time while the first knight fell at 15:11 with 0 defenders (it was the wipe's
     conversion, not the split's); the text should separate the two losses.

## Sessions 4m to 4q (2026-11-06/07): ENGINE 17, forensics, the cache, batches 6 to 8, the event layer and learned nodes

### Decisions made (session 4q)
Denning: the right strip target and the right hexes to remove are valued from data, not a list; steps 2a and 2b
first, then the transcripts (in a new chat). Data can't reject a link that came from Denning without his ruling
(held as `pending_rejection`; if he approves, `override_approved: true` and the link then follows the data both ways,
back to supported if more data says so). Rulings so far: Blind on the enemy frontline -> fight outcome: keep, wait for
more matches; defenders pushing the runner: Claude's measurement error (captures only), fixed with the run defence
node, not clear yet. Collapse = defenders collapsing on a split; collapse timing read five ways (his list approved:
arrival spread, numbers at contact, time from the split's first NPC hit, res timer, escape skills off recharge), the
data to pick. A plain-English page of the model, rebuilt each batch: knowledge/learned-model.md.

### Decisions made (session 4p)
Confirmed by Denning: Lord curves capped at 5 points; carrier ETA discounted by measured capture chance; healing-monk
curves dropped; a power play is any numbers advantage at main (an 8v7 while the enemy runs counts); chains go back to
the last reset or 3 minutes, follow the biggest few causes, and show fixes only where they mattered most; defensive
Mesmer play = interrupting offensive skills and casting on the enemy midline and frontline (offensive = interrupting
the enemy monks); frontline defensive peel = hitting or snaring enemies on its own backline; links found by discovery
are held for his approval; discovery split across several machines.

### Recent changes (as recorded in the handoff)
- Session 4q: step 2a (eventlayer.py: strips against every enchantment in range, hex removals against every hex in
  range, damage against the role's usual; values from data with differences in differences) and step 2b
  (learnednodes.py and lnrows.py: nine learned nodes, each link's held-out strength written into causal_map.json and
  link_log.json; new map nodes P.17 to P.19; the map page shows the measurements). Fixed in the session: fights.py
  stores fights from the losing side (the fight node reads alternate sides); capture speed leaked its answer (seconds
  to the first push defaulted to the run's length; now read 10 s into the run). The learning report rebuilds
  measures.md and eventlayer_values.json; the workflow commits data/benchmarks.
- Session 4p (2026-11-07): batches 7 (30 matches) and 8 (22) from October and November; Train batch `months` input.
  Fixed: phantom flag swings (lone carrier read as a sure capture; carrier ETA now discounted by measured capture
  chance), flag spawns and stands per map (Imperial, Nomad's and Druid's had double-length flag runs), TQ 3 uptime, dead
  defenders listed as present at NPC kills, TQ 1 citing the wrong capture. Added: map geometry and per-map splits in the
  usual play, the causal chain (chain.py) in TQs 1, 2 and 4, the defensive-play measure, step 1 of the learned causal map
  (eventlayer.py, measures.md), TQ 3 for every power-play size. Corrections: Lord curves capped, healing-monk curves
  dropped. Model ahead of strength alone for the first time (0.367 against 0.412).
- Session 4o: the TQ section of the learning report (`tq.py`; replaces the five whys); speed-ups, each checked to give
  identical results: candidate tests pool every fold and reuse the honest test as the baseline (`model.test_candidates`),
  node models pool all their fits (`nodes.fit_nodes`), fight-state fits run side by side and only where a match is
  missing (`fightstate.build`), fight-state predictions are kept on the `cache` branch, the usual-play records are built
  once per report. Fixed `nodes._aoe_skills` (counts leaked between matches; lord_damage and lord_kill changed slightly).
  Found: the model library's fits differ in the last digits between processor types (log loss 0.554 against 0.550 on
  identical tables); `timings.json` now records the processor.
- Session 4n (end): Train batch workflow (.github/workflows/train-batch.yml, pinned libraries), fits side by side
  (parallel.py), held-out models from 10 groups of matches (cache.FOLDS), deaths models fitted only when needed,
  learning report section timers; Denning's TQs replace the five random whys (to build into learning.py next).
- Session 4n: Denning asked for the why of smaller events and every question answered with data. Built `forensics.py`
  (death questions with benchmarks by role), `events.py` (flag swings, power plays without a kill, survived spikes, pit
  NPC losses, splits; spike landing benchmarks), wired into `why.py` and the learning report (five events across kinds).
  Built `cache.py` (held-out models fitted once per batch and shared; prepared data saved by engine code, kept on the
  `cache` branch; parallel warm-up; analyze.py reuses saved analyses) and `status.py` (per-match tracking). Timing before:
  a why chain 82 s, the learning report over 11 minutes (stopped). Batches paused for the transcripts.
- Session 4m (continued): gvg.report players and Elo synced and merged; Lord regeneration per Denning; refit of batches
  0 and 1; batches 2 to 5; fight-state split by thirds; Lord-damage correction; `snapshot.py`; `why.py` and the first
  why chains with the fixes they showed are needed (see "Next session: fixes to do"); hand-off loop fixed.

### From METHODS.md: changes 2026-11-07 (session 4p, after batch 7)
- Flag swings count only real deficits (`events._real_low`): the lead stays below -15 s for 15 s or more, or the enemy
  takes the stand within 30 s. The scoreboard counts any carrier as a capture in its carry time, so a lone carrier next
  to eight enemies read as a sure capture ([Team v Men] 3:30). Measured: runs with 3 to 5 own alive against an enemy
  holding the stand with 6+ captured 2 of 14.
- How it got there (`tq.lead_up`): monk-death, NPC-loss and flag answers trace back up to 120 s to when the team's main
  was first outnumbered by 3+, list who was away and doing what (dead, carrying, escorting, elsewhere), and price the
  team's flag runs in that window against every stored run made while the enemy held the stand (`tq.run_bench`: capture
  rate, own deaths in 40 s, held-out win change, by main numbers and escort size), plus the decisions in the window.
  First reading (91 matches): main outnumbered by 3+, escort 2+: captured 0 of 6; escort 0 to 1: 10 of 21.
- NPC losses with dead defenders explain each defender's death (forensics key causes).
- Power-play "why, in short": damage uptime over the whole power play in contact with an enemy group (was the phase at
  its start, often the walk in); each measure is named a cause only if it sits on the non-killing side of the midpoint
  between the killing and non-killing medians (direction from the data).
- `defenders_present` at an NPC kill (episodes.py) = defenders alive in their own base or pit at the kill (was anyone
  who had defended before it, dead or not).
- Each TQ prefers a match not used by an earlier TQ in the same report.
- Flag ETA of a carrier behind on players alive (scoreboard.py `eta`, `carry_chance`; data/benchmarks/carry_capture.json
  from `benchmarks.py carry`, Denning approved 2026-11-07): carry time plus (1 - chance / chance at even numbers) times a
  fresh run from the spawn. Measured on 91 matches, capture chance by alive difference: +2 or more 64% (107 carries),
  -1 to +1 49% (1381), -3 to -2 35% (88), -4 or less 25% (20). Even or better keeps the plain carry time. Rebuild the
  benchmark after new replays (`benchmarks.py carry`).
- Flag spawns and stands per map (state.py `_flag_spawns`, replaylib.py; data/benchmarks/flag_spawns.json from
  `benchmarks.py spawns`, 2026-11-07): each map's two spawns are the densest clusters of flag pickups pooled over every
  replay of the map, and a match uses the one nearest each team's base. The old rule (pickups 6,000+ from the stand)
  missed short flag runs: Imperial, Nomad's and Druid's Isles (spawns about 4,200 to 4,900 from the stand) fell back to
  the bases, doubling their flag run, every flag ETA and lead on them, and map_flag_run; other single matches caught a
  choke where dropped flags were picked up. Four replays with no located stand (0, 0) now use the map's median stand.
  Rebuild the table after new replays (`benchmarks.py spawns`), before `benchmarks.py carry`.
- The causal chain (`chain.py`, Denning 2026-11-07; replaces `tq.lead_up`): TQs 1, 2 and 4 trace how the game state
  came about, as a chain of states each caused by the one before (pit lost <- defenders dead or away <- the deaths and
  their measured causes <- the fight's numbers <- flag duty <- the flag deficit <- what turned it; plus an enemy split in
  the base and an isolated player). Back to the last reset (both teams 8 alive, flag lead within 10 s) or 3 minutes;
  the 2 biggest causes followed at each link (by held-out win change); ongoing states that began before the reset (a
  split, a player away, flag duty) stay in. Fixes: only the 2 that would have mattered most, priced in win points from
  measurement (usual play, deaths node read again, run benchmark).
- Defensive play by a disrupting player (`forensics.disruption`; Denning: for a Mesmer, defensive = interrupting
  offensive skills and casting on the enemy midline and frontline; offensive = interrupting the enemy monks): share of
  its interrupts and enemy-targeted casts on the midline or frontline, against every stored own-healer death
  (`chain.mes_benchmark`; first reading: median 86%, 493 cases).
- The event layer (`eventlayer.py`, step 1 of the learned causal map, 2026-11-07): strips (useful = a prot off a target
  under attack, or an enchantment off a midline/frontline player) and wasted removal casts, Blinds on enemies (frontline,
  defensive), hexes (time on, removed), frontline peel (damage on attackers of own backline / on enemy healers), wrong
  casts for every role (interrupted after casting into a ready interrupt, while Dazed, attacks while Blind), spike
  timing, run timing (enemy boost clock, enemy power play), splits (answer latency, effect, enemies drawn, cost at
  main), power plays of every size with why the enemy was short, and enemy captures from the defending side. Cached per
  match; `eventlayer.py report [--all]` writes data/model/reports/measures.md. Power plays: every size counts (Denning:
  an 8v7 while the enemy runs is a power play); TQ 3 picks the one that cost the most win chance and benchmarks it
  against power plays of the same size.
- Step 2a of the learned causal map (`eventlayer.py`, Denning 2026-11-07: what counts as right comes from data): every
  strip is judged against every enchantment on an enemy in the stripper's cast range at that moment; every hex-removal
  cast against every hex on an ally in the remover's range (and how long the removed hex had been on); every player's
  fight damage against its role's usual (median damage per second on enemy players per player per fight; class median
  under 20 cases). Values (`eventlayer.py values` -> data/benchmarks/eventlayer_values.json, rebuilt each batch): an
  enchantment = its recorded output (gvg.report damage + healing + prevented) per second up, plus the drop in the
  bearer's output in the 10 s after a strip (attunements record no output of their own); a hex = its recorded damage per
  second on, plus the drop in the hexed player's output while it was on. Both drops are differences in differences
  (the same change for allies of the same class over the same seconds is subtracted, so the fight's own rise is taken
  out); 5+ cases needed; negative values read as no measurable cost. Limits: the values include every trained match
  (not time ordered); output means damage and healing only (energy, speed and armor show only through them).
- Step 2b of the learned causal map (`learnednodes.py`): nine node models built from the event layer, each using only
  the causal-map links into it, glass box (main effects only), held out by match (6 folds): run outcome (R.3; control
  and damage on the runner read at 5, 15 and 30 s into every run), flag swing (R.3; flag lead change over the next
  60 s), run defence (R.3; every enemy run from the defending side at 5, 15 and 30 s in: free defenders, pushers,
  control and damage on the runner so far; added after capture speed, which sees captures only, could not show what
  pushing stops), capture speed (R.3; seconds of an enemy capture, the defence read 10 s into the run: pushers, control and
  damage on the runner so far; counts over the whole run grow with its length, and "seconds to the first push"
  defaulting to the run's length leaked the answer in the first build), power play (K.4; any size kills), fight outcome (R.2; play
  before the fight's first death; fights.py stores fights from the losing side, so the side read alternates), split
  chance (A.allocation; a split starts in the next 30 s), split answer (P.11; seconds to the first defender, 60 =
  never), split effect (R.5; a pit NPC killed), collapse (R.1; a split member dies; collapse timing read five ways,
  each also tested alone, since Denning left the right reading to the data: arrival spread, numbers at contact, time
  from the split's first NPC hit to the first defender, res timer at arrival, and split members' speed skills off
  recharge at arrival under K.13). A link's strength = the held-out
  loss without the link's features minus with them (same folds); supported above twice its spread across folds,
  rejected when dropping it helps by more than that, else not clear yet (link tests fit 2 bags per variant, the final
  readable model 4). Written into causal_map.json (`measured`, per node). A link's status follows the data only if it
  was a hypothesis or the data set it (`status_by: data`): supported if any node supports it, rejected if every node
  that measured it rejects it, else back to hypothesis; Denning's and formula statuses never change, and a link from Denning is never rejected without his ruling (held with `pending_rejection`; `override_approved: true` lets the data reject it and then follow the data both ways). Appended to data/model/link_log.json each run; links a node needed and
  the map lacked were added as hypotheses (logged, with source). Rows are built in `lnrows.py` (cache kind "lrows",
  keyed by that file and the values' hash), so a change to the fitting never rebuilds them. Each batch also writes
  knowledge/learned-model.md ("What the model has learned" on the site): every learned node and cause in words. New map nodes: P.17 wrong casts, P.18 enchantment
  strips, P.19 Blind on enemies; P.5 now covers hex removal. `whatif(node, row, changes)` reads a node again with
  features changed (for step 4). The power-play node keeps the window's length as exposure (a longer power play has
  more time to kill).
- Correction (Denning, batch 7): lord_dps_own and lord_dps_enemy capped at 5 points (data/model_corrections.json).
- Usual play includes the map (usual.py `MAP_COLS`): geometry in the similarity and, with the build axes, the adjustment;
  choice effects split by map name once a map has 10+ cases of the choice and of the usual one.

### From METHODS.md: forensics, event explanations, the cache and match status (2026-11-06)
- **The standard for an answer** (Denning): every "why" question is answered with a measurement, placed against the
  same role or situation in every stored match, never with a guess. The four examples that set the standard are below
  ("Answer exemplars"); new event kinds are built to answer questions of that kind and depth.
- **Forensics** (`forensics.py`; benchmarks `data/benchmarks/forensics.json`, rebuilt with `forensics.py bench`): the
  questions behind a death, over the 20 s before it: position (nearest allied healer, allies and enemies in casting
  range, nearest enemy, front of its team), prots (every prot and heal cast on it with timing against the burst: pre-prot,
  reaction, late; landed, interrupted, cancelled; what each prot can act on from the skill data: blocks act on attacks
  only, damage reduction and heal-on-hit on all damage, knockdown immunity on knockdowns; allied prots ready and in range
  but unused, with what those healers were casting instead; each knockdown with whether immunity was up and who had it
  ready), healers under interrupt pressure (interrupts, knockdowns, Daze, hexes on the team's healers), damage off
  shield sets (damage taken while holding a set with no shield and not casting; a shield's 16 armor stops about 24% of
  armor-respecting damage, `knowledge/armor.md`), both teams' damage output (per second, concentration, armor-ignoring
  share, spikes), peel (snares, Blind, Weakness, interrupts, knockdowns or hexes the victim's team put on its attackers,
  and the longest each attacker was left free; damage on the attacker is reported but is not peel), casting (each cast:
  finished, interrupted, "hit while Dazed", cancelled; enemy interrupts off recharge and in range, bow range from the
  bow type; Daze), conditions (who, from how far, the attacker's pressure, the victim's set, removal and removal on its
  own bar). Verdicts come from the benchmark's 20th and 80th percentiles for the role (`BENCH_CUT`), provisional until
  rulings calibrate them. Hits recorded without a skill are named from the attacker's cast finished within 1.5 s.
- **Event kinds** (`events.py`): `flag` (a team going from up to down on flags: captures against the fastest possible,
  every run with the control put on the runner, the stand fight's output on both sides, the forensics of the first
  deaths, the cascade), `power` (a power play without a kill: the fight's shape every 5 s, the enemy group's distance to
  its others, own damage and uptime against the benchmark, the enemy's healing, prots and knockdown immunity, pressure
  on its healers, snares put on retreating players), `spike` (a spike the target survived: every hit with its skill and
  time, landing spread and share inside 1 s against spikes that killed and spikes survived, `data/benchmarks/spikes.json`
  from `events.py bench`, pre-prots up, everything cast on the target, control on the spikers, the target's set and
  health line), `npc` (pit NPCs lost: the split, the defenders and their latency, where the rest of the team was), and
  `split` (a split and its answer). `events.py find <kind>` lists the biggest events of a kind. Why chains (`why.py`)
  now explain what dropped the health with the forensics, and "why, in short" names the findings that stand out. The
  learning report answers the TQs (below) with these; why.py and `events.py <kind>` stay available for any other event.
- **Cache** (`cache.py`): every "without this match" model (win model, node models) is fitted once per training set
  and engine code, saved, and shared by the learning report, values, usual play and why chains (before: each layer
  refitted its own, so a report refitted the same 53 models several times). Each match's prepared data (analysis,
  match tables, node rows, value events) is saved keyed by the engine code it was built from (found automatically from
  the imports) and the data files it reads, so a stale entry can't be read; tables are also keyed by the fight-state
  predictions they read. `cache.py warm` builds everything for the current batches in parallel; `cache.py sync
  pull|push` keeps prepared data on the `cache` branch between sessions. Held-out models stay in the session.
- **Speed, measured 2026-11-06 (61 matches, 2 cores):** a win-model fit 12 s, a deaths-model fit 42 s, one win-model
  validation 70 s. A batch used to cost: rebuild prepared data after an engine change (about 4.5 min), one held-out win
  model and one deaths model per match (122 fits, 27 min), then the learning report (16 min, of which about 7 min was
  the candidate-variable tests, one full validation each). Changes: held-out models now come from 10 fixed groups of
  matches (`cache.FOLDS`; each match is still explained by a model that never saw it; leave-one-out 78.2% accuracy and
  log loss 0.601 against 10 groups 77.6% and 0.546 on the same matches, so accuracy holds), deaths models are fitted
  only when a why chain needs them, and candidate tests run side by side. Cache rebuild after an engine change: 32 min
  down to 5 min. Set `FOLDS = 0` to go back to leave-one-out.
- **Side by side** (`parallel.py`): each node's held-out folds and final fit, and the win model's honest-test folds,
  run on every core in fresh processes (identical results, checked on all six nodes). On 2 cores: node step 6.1 to 4.9
  min, the win model's honest test 70 to 38 s.
- **Train batch on GitHub** (`.github/workflows/train-batch.yml`, 4 cores, pinned library versions in
  `train-requirements.txt`): optionally picks and fetches random matches, adds the batch, analyses, builds the
  held-out models, writes the learning report, saves the cache and commits the results to main. Start it from the
  Actions tab or with `gh api -X POST repos/itsha12/gvginfo/actions/workflows/train-batch.yml/dispatches -f ref=main -f
  'inputs[pick]=6' -f 'inputs[add_batch]=yes' -f 'inputs[note]=...'`; then pull main and read
  `data/model/reports/latest.md`. Runs on GitHub, so it doesn't use the chat's time or usage.
  Split across machines (session 4r): job "prepare" (pick, fetch, add the batch, analyse, held-out win models,
  fight-state predictions) hands a git patch and its cache files to six "part" jobs that run side by side
  (`learning.py part main` = honest test, curves, discovery screen, surprises, rulings, usual play, values measured;
  `part learned` = event layer and learned nodes (the causal map); `part cands` = candidate variables; `part nodes:<list>` = the node models over three machines),
  then "finish" joins them and runs what reads the node models' files (values priced, the TQs, the snapshot) with
  `learning.py finish`, saves the cache and commits. `learning.py` with no argument still runs the whole report on one
  machine, same text. timings.json keeps each part's wall time under "split". A section added to the report must be put
  in one part (PART_SECTIONS, or finish if it reads files another part writes) and in ORDER.
- **Match status** (`status.py`, `data/model/match_status.json`): per match, its batch, engine version, review entry,
  commentary sources and their state (pending, checked, done), Denning's rulings, the events whose why was walked
  through, and notes. `status.py sync` rebuilds the derived fields; `status.py mark` records the rest.

### From METHODS.md: training batches 2 to 5 and why chains (2026-11-06)
- Batches of 6 random replays (Denning); 53 matches after batch 5. Learning reports gained: a data-integrity section,
  the placebo (pre-trend) check, choice effects split by fight-state thirds (`usual.FIGHT_SPLIT`, thirds from the data),
  close-game and resampled accuracy, leverage and behaviour clusters, a detailed snapshot (`snapshot.py`) and why
  chains (`why.py`).
- Correction logged by Denning: `lord_damage_diff & minute` (Lord damage only decides at 28:00). Tested each batch.
- Why chains (`why.py <id> <m:ss>` or `why.py top N`): result and worth (win model without the match, with the
  variables that moved it), mechanics per death (deaths node without the match, the contributions that raised risk most,
  a few seconds before), setup (the phase before: groups, jobs, numbers, capacities where the deaths came), the decision
  before (with the usual play's value), context. First test (batch 5) showed the mechanics step stops at "health was
  low" (a symptom), fight consequences overlap the next fight, and the decision step is too coarse; the fixes are listed
  in docs/HANDOFF.md ("Next session: fixes to do").
- Fixed: `episodes.flag_cycles` could loop forever on two carriers passing the flag back and forth in one recorded
  second (BcS v yM b88983e3).

### From METHODS.md: data integrity, the Lord, strength and the review of 2026-11-06 (ENGINE 17)
A review of the engine against its goal found three measurement problems and several missing steps; all were built
before any refit (Denning).

**Data integrity** (`integrity.py`; `python3 integrity.py` lists every match, `data/model/integrity.json`):
- Length: the match ends at the first Lord death, else at the later of the recorded length and the last event.
  RACK v hdm (1f65fd3b) was stored as 2:30 but runs to 17:18; the engine had cut it there and learned a "stomp".
- Pit roster: NPCs only appear in a replay once something touches them, so an untouched pit looked empty. Winners
  "lost" their Bodyguard in 19 of 30 matches (losers 1) and showed fewer than 2 knights in 13 (losers 2): the
  backwards knights and Bodyguard curves of batches 0 and 1 measured whose pit was attacked, not tactics. Every pit
  now starts with the standard roster (Denning: 2 knights, 2 archers, 1 Bodyguard, 1 Guild Lord; a third archer on Isle
  of Solitude, map 542); NPCs never seen are added as alive all match (`state.MapGeo._fill_roster`). Archers beyond the
  roster near a pit count as outside archers.
- Lord damage: a Lord that died with no recorded damage means the attackers' Lord damage wasn't observed (OG v cope
  29b7eca0, Men v RACK 45cf6756); that team's Lord damage and the Lord nodes are left blank, not zero.
- Exclusion: matches with problems that can't be repaired leave training (`integrity.usable`, used by the win model and
  the node models); none so far. The learning report opens with a data-integrity section.

**The Lord** (`lord.py`): 28 of the first 30 matches ended with a Lord kill, only 2 at 28:00. Health is rebuilt second by
second from damage and healing on the Lord, max health +1% per boost, and regeneration as Denning gave it: 10 per
second always, plus an out-of-combat part once he hasn't been hit for a few seconds, +2 rising to +10 per second. The
delay and the rise are measured (`benchmarks.py regen`, `data/benchmarks/lord_regen.json`: the pair that best puts
the rebuilt health at 0 when Lords die, with no surviving Lord reaching 0), and so is whether the Amulet of
Protection's cap still has to be applied to gvg.report's recorded damage: applying it made the rebuilt health at death
much worse (median 629 against 332), so the recorded damage is taken as already capped. First reading: delay about
10 s, +2 every 3 s (many nearby pairs fit equally; the median error at death, 332 health, says some Lord damage is
not recorded). Scoreboard: `lord_health`, `lord_exposed` (Bodyguard and both knights dead), `lord_damage_taken_60s`.
Node `lord_kill` (nodes.py): while enemies are in a pit, the Lord dies within 30 s. Win-model variables
`lord_health_diff`, `lord_exposed_diff`.

**Strength** (`strength.py`, `lineup.py`, `context.py`): three measures, each time ordered (only results before the
match), blended by how well they predict later results (`strength.json` "blend": logistic fits of every combination on
the earlier two thirds of the matches after the first 300, tested on the latest third; replays left out):
- ladder: the in-game ladder rating gvg.report recorded with each match;
- elo: gvg.report's own guild Elo (Denning: far better than the ladder), rebuilt in time order from the stored results
  with its published rules (tournament-elo.v2: start 1500, K 32, 21 days idle then -50 a week to 1500; tournaments
  only). Checked against gvg.report's current table (`data/gvgreport/elo.json`): mean difference 23.5 points over 68
  guilds. Today's table itself is never used for training (it includes later results);
- fitted: the Bradley-Terry guild rating;
- lineup (Denning): the eight players who played, characters grouped into people by `data/aliases.json` (Denning's
  assignments plus gvg.report's player directory, merged by `tools/gvgreport/merge_players.py`). Two measures
  tried, an opponent-adjusted rating and a shrunk win rate, each with MAT results counting 1 to 8 times as much; step
  size, MAT weight and scale chosen by log loss on later matches (`lineup.json` keeps the grid). First reading: the
  shrunk win rate predicts best (log loss 0.418 against 0.433 for the rating); extra MAT weight barely helps (x1.5 best,
  x1 equal) and more than x2 hurts, even when tested on MAT matches alone.
- Blend reading with gvg.report's player groupings and the rebuilt Elo: fitted + lineup predicts the latest third
  best (log loss 0.3115, 89%), lineup alone 0.313, Elo alone 0.399 (better than the ladder, 0.437, worse than the
  fitted rating, 0.346); adding the Elo to fitted + lineup changes nothing (0.3115), so its weight is 0 for now and it
  is retested at every run. With gvg.report's groupings the lineup measure improved (0.418 to 0.403 on all later
  matches) and MAT x2 is best, though x1 to x3 are within 0.001. The model's `strength_gap` is this blend.
- Context priors (`context.py`): build-archetype matchups, archetype by map and archetype by flux, measured on every
  stored result with strength as a fixed offset (antisymmetric features, ridge penalty chosen on later matches). First
  reading: no penalty beats strength alone on the latest third (0.3806 at best against 0.3802), so the prior is off
  (0 points) and retested whenever results are added.

**Fight state** (`fightstate.py`): expected deaths per team in the next 10 s, the sum of every live player's death
risk from the deaths node, always from a model fitted without the match (6 groups). Win-model variable `fight_state`
(enemy minus own) and a situation control in every usual-play comparison (Denning `D4`). Built by `learning.py` before
the tables.

**Other new variables**: hexes on a player and on its team's live healers (deaths and kill_conversion nodes; replay
hex intervals); map shape (`map_flag_run` = Y, `map_pit_to_stand`, `map_bases_apart`) and flux flags in the win model,
staged with the build variables (fixed for a match).

**Checks on the comparisons**:
- Pre-trend (placebo) test in `usual.py`: each choice's comparison is repeated on the win-chance change in the 30 s
  BEFORE the decision; a clear difference there means teams making that choice were already sliding or rising, so its
  effect is partly who chooses it ("ALREADY DIFFERENT BEFORE" in the report).
- The honest test reports matches lasting 15 minutes or more and matches even on strength (gap under 200) apart, and
  the gain over strength alone with a 90% range from resampling whole matches.

**Discovery built** (`discovery.py`, learning report section 7): leverage (how much of the spread in win-chance change
the choice explains beyond the situation, per decision kind) and behaviour clusters (each decision's response, the share
of players by line in each action, grouped by k-means with the clearest k; groups no named choice covers are marked
UNNAMED for Denning to name or reject).

**First effect of the fixes on the node models** (checked, not saved): with the full roster, `npc_loss` still ranks
moments better than attackers and defenders alone (AUC 0.786 against 0.755) but no longer beats them on log loss;
`lord_damage` still adds (36% of the spread explained); `lord_kill` is no better than attackers and defenders yet
(AUC 0.96 for both: who is in the pit nearly decides it).

### From METHODS.md: commentary and comms, the first OG comms matches
- Transcripts are never stored (public repo). Each is matched to its match (players' names in the transcript against the
  rosters), lined up by anchors (kills, captures, boosts, NPC losses: `timeline.py <id> --people` lists them with each
  character's person), and turned into paraphrased claims in `data/commentary/<source>.json`: approximate time, kind
  (plan, read, call, reason, prediction, diagnosis, technique), speaker's role, tactics ids, the variable it suggests,
  and the engine's check (agrees, disagrees, partly, can't measure) with evidence.
- Denning: the variables the comms point to are the most important thing they give. `comms_vars.py` measures each one in
  every stored replay against the outcome the speaker said it drives, within strata (local numbers, number of spikers),
  with 90% intervals from resampling whole matches (`data/benchmarks/comms_variables.json`). Supported variables go into
  the model they belong to (win model candidates in `features.CANDIDATES`, node variables) and onto tactics as
  **OG comms:** lines with the data; contradicted or unclear ones stay recorded there so they aren't re-proposed without
  new evidence, and become open questions.
- First six OG matches (batch 6): supported: a group with no healer loses players twice as often (`P12`), merging 7+ for
  a pit push kills 2.5 times as often (`P13`), hexed spikers halve spike kills (`X9`), players with 15%+ death penalty
  die about 4 times as often in fights (`K17`, partly selection), turtling teams usually lose (`L11`, win-model candidate
  `turtle_diff`). Not supported or unclear: "solo monk" alone (`Q16`), Shell Shock and enchantment strips on the spike
  target, tight groups dying more (deaths are the wrong outcome: area damage taken is the right one, to build).
  Can't measure: gate control, terrain and line of sight, energy, call timing.
- Made into model variables (Denning, after the first six): deaths node `solo_healer` (a healer with no other own healer
  in casting range: Denning's reading of "solo monk"; measured on the monk's own death, 3.4% against 1.1% per 10 s),
  `group_no_healer`, `own_morale` (the player's own death penalty or boost), `allies_in_area` (allies within 322) and
  `healers_in_range` now excludes the player; NPC nodes `attackers_share` (share of the attacking team in the pit:
  merging); win-model candidates `footmen_diff`, `no_healer_groups_diff`, `solo_healers_diff` (and `turtle_diff`);
  values.py prices a footman lost and splits deaths by whether the team was boosted ("we can die for NPCs"); footmen
  are read from the replay's agents (`features.footmen`). Measured in comms_vars.py: area damage against spacing
  (unclear), spikes by weapon set (unclear), interrupts on the spikers before a spike (supported: 23% against 40% kills).
- Power play fix: a numbers advantage held in the own base or pit is a defence, not a power play (`fights.windows`
  records `where` and `at_home`; `decisions.power_plays` skips those). Found when batch 6's "power play without a kill"
  was One holding 8v3 in its own pit while turtling.
- Last three OG matches: OG v hdm (OG's spikes killed 0 of 15: hdm's healing and interrupts, `X10`), OG v Dz (footmen,
  out of heal range), OG v hold (a base race won by 0.3 s after OG healed its own Lord for 1,390, `L12`). Engine issue
  found there: the rebuilt Lord health had hold ahead, the reverse of the result (lord.py to check).

## Up to batch 5 (early November 2026): the first structure

### Fixes from the first why chains (batch 5): state
1. Done: mechanics stop at a symptom. Why chains now explain what dropped the health with forensics (`forensics.py`),
   and "why, in short" names the measured causes.
2. Partly: why damage uptime was low. Power plays now show the enemy group giving ground and joining its others, and
   own damage against the benchmark; "moving" is still not split into kiting, chasing, repositioning and running.
3. Open: fight windows overlap (a fight's consequence should end at the next fight's start).
4. Open: decisions too coarse (use the refined choice and the 15 nearest similar decisions; pick the decision that set
   up the fight).
5. Open: recording gaps (deaths with almost no recorded damage should be flagged "not recorded").
6. Done with 1: "why, in short" built from the measured causes.
Smaller: the regeneration fit is flat (delay 10 to 20 s fit equally); lord_damage_diff and flag_lead still bend at the
extremes; fight-state thirds give small cells in the boost-clock split.
Forensics limits to know: no line of sight or facing in the data (a ranger's bow reaches 1,498, so standing closer does
not by itself allow a shot); "ready interrupt" assumes base recharge; armor per set is estimated from a shield's base
16 armor; peel counts control only (snares, Blind, Weakness, interrupts, knockdowns, hexes), not body blocks.

### Current state after batch 5 (53 matches)
- Batches: 0 (24), 1 (6), 2 (4), 3 (6), 4 (6), 5 (7 incl. one "latest" request); reports `data/model/reports/
  batch_00.md` to `batch_05.md` (batches 0 and 1 refitted with ENGINE 17). Older numbers in earlier handoffs were
  measured before the ENGINE 17 fixes (NPC roster leak, truncated RACK v hdm) and are superseded.
- Win model: not yet better than team strength alone (held-out log loss 0.530 against 0.439; accuracy 77% against
  73%; gain -0.09, 90% range -0.28 to +0.06). It ranks winners better but is overconfident; the gap narrowed from
  batch 1 to 4 and held in batch 5. Interactions on since 40 matches (morale with archers, with total DP, with the
  clock). Leans on morale, players within one spike, the stand, main-group numbers, flag lead. Correction logged:
  Lord damage read with the clock (Denning; tested, about neutral).
- Strength: blend of fitted guild rating and lineup (players who played, MAT x2 by measurement) predicts the latest
  third of stored results at log loss 0.31 (89%); gvg.report's Elo, rebuilt in time order, beats the in-game ladder
  but adds nothing on top. Context priors (matchup, map, flux) off: no gain yet.
- Node models (53 matches, unseen matches): deaths AUC 0.917 (baseline 0.804); kill conversion 0.802 (0.68); flag
  answer typical error 17 s (27 s; 68% of spread); pit NPC loss 0.826 (0.759); Lord damage 37% of spread; Lord kill
  0.968 (0.953).
- Values (win points, clear unless noted): a death -6 (healer -5.8, non-healer -6.1), a capture +3.2, a knight lost
  -7.8; a boost, an archer or the Bodyguard not clear yet.
- Usual play (53 matches; placebo check over the 30 s before): after a wipe, taking the flag instead of pushing the
  pit -16 (clear, not explained by who chooses it); at the boost clock, not running and falling back -6 and not running
  and advancing -13 (both clear; by fight-state thirds falling back costs most in even and winning fights, `D4`);
  split in base, defending without a collapse +10.7 against collapsing (clear); several enemy-pickup and power-play
  differences are partly who chooses them. Leverage: the choice matters most after a wipe and at the boost clock.
- Detailed (batch 4 snapshot, 46 matches): Mes/A runs most but slowest (median 42.5 s to capture) and most pushed;
  8 Monk carries mostly end in hand-offs; losers' flag answers are slower (median 53 s against 38 s); top kill
  participation Augury of Death, Word of Censure, Decapitate; most interrupted Healing Burst on the 7 Monk and Guardian
  on prots and 8 Monks; spikes survived 76% (winners) against 59% (losers), 8 Monks 45%.
- Why chains (batch 5): the setup and the cascade after a monk dies are read well (hook v EDGE 1:00, BcS v Men 1:00);
  the mechanics and decision steps need the fixes above.
- Lord: 28 of the first 30 matches ended with a Lord kill. Health rebuilt with Denning's regeneration rules; recorded
  Lord damage is already capped by the Amulet of Protection.
- gvg.report: players and Elo synced (`data/gvgreport/`); 482 new people and 65 of Denning's extended in aliases.json.
- Engine fixes this session: integrity layer, full pit roster, RACK v hdm length, unobserved Lord damage, hand-off
  loop in `episodes.flag_cycles` (hung BcS v yM).
- Older measurements still valid in method (flag model accuracy, death-cause list, collapse cost): see METHODS.md.

### Decisions made (confirmed by Denning)
- Session 4m: pit roster is 2 knights, 2 archers, Bodyguard, Lord; a third archer only on Isle of Solitude. Lords
  regenerate 10 health per second always, plus +2 rising to +10 once unhit for a few seconds; the Amulet of Protection
  adds healing. gvg.report's Elo is its own calculation and much better than the in-game ladder; use gvg.report's player
  assignments to add to the site's (Denning's win); weigh MAT results more (amount measured: x2). Build all fixes before
  refitting; batches of 6; fight-state split by thirds; Lord damage read with the clock. Report each batch as the WHY of
  5 match events: the goal is the why, not breakdowns.
- Up on flags = better position to get a boost and to run (the next capture exchange), not who capped last; backup
  flag and full running (1Y vs 2Y) are big advantages; a 1v1 defender running its flag partway shortens Y.
- Individual deaths don't win games: judge what caused a fight and what it caused. A balanced build that survives to
  26:00 without deaths or NPC losses is winning against a 2-monk hex way. DP stacking against a spike team is a big
  disadvantage even when each death is recoverable.
- Split answered on time at about 15 s; 60 s is late. Lone ranger answered by the Mes/A plus a frontline collapse.
- Deaths judged by cause first, then smaller mistakes graded basic, minor or acceptable, escalated when a monk is
  alone or after time. Quarter-second interrupts are luck.
- Death 1 ([hdm v HC I1], HC prot 8:10): a great play by hdm, with acceptable mistakes.
- Death 2 ([Men v HC C], HC 8 monk 9:31): HC was up on flags; staying out 3v4 while Men ran was an unnecessary risk.
  The runner could wait to cap; the backside group should fall back toward pit and follow only if Men went for the
  runner. Daze beside the ranger was a minor mistake. Not double running; half running is too risky.
- Cap as soon as reasonably possible after the enemy; the team running can't retreat to its pit.
- Builds change the best play, down to single skills (`B23`): a snare on a 1v1 defender favours collapsing (`S31`); a
  2-monk spike build is behind on Lord damage late, so it weighs DP over NPCs, often the reverse of other builds.
- What a wipe can be turned into depends on where it happened (`D5`); teams very rarely rush the enemy base to spike
  players as they resurrect.
- Near the enemy's boost, falling back is likely a mistake unless losing the fight; the read is own monks' energy,
  enemy health, enemy energy and numbers (`D4`). Whether to collapse on a split has no fixed line: plan, defender's
  ability, flag position and the main fight decide, and the line comes from data (`S32`).
- Monks die on purpose only for a base res (every 2 minutes on the minute), e.g. in their own base at 17:55 (`K14`).
- Healers matter only through damage: 3 healers + 1 damage against 2 + 2 is about even (`J12`).
- No energy estimate from casts: too large a build for what it adds.

### Open items at the time
- Batch 2 next.
- Probe workflow (`probe-gvgreport.yml`, branch `probe`) finds gvg.report endpoints for new syncs.
- Death rulings 3 to 5 and power plays 6 and 7 in [Men v HC C].
- Situation cards (tactics section 14) are hypotheses for the data to test; D6 has no default.
- Lord damage weights replaced by measurement (`benchmarks.py lord`, `data/benchmarks/lord_damage.json`); the
  provisional `edge()` weights remain guesses until the win-probability model.
- Toolkit: race clock for base races; timed kills; "decided by" from the fights and edge ledger; Lord spawn positions
  in the trim.
- Benchmarks (a strong prot's spike catches, a good 7 monk's Infuse timing).

### Known issues and cautions at the time
- The provisional edge's weights are guesses; with 24 matches, `compare` results are hypotheses only.
- Judge flag position with the scoreboard's flag lead (the exchange), never from who holds the stand (wrong twice,
  the second time because of a capture gvg.report recorded without a player; now fixed).
- Run Python with `PYTHONDONTWRITEBYTECODE=1`; `__pycache__` is now ignored by git.
- No NPC positions or energy in the data; zones and NPC positions are estimates. Energy will not be estimated (Denning).
- Store paraphrased events from transcripts, never the transcripts (public repo).

### From METHODS.md: the model as built (batch 0)
- `strength.py`: team strength from every stored result (1,737 matches, 71 guilds), Bradley-Terry with a 60-day
  half-life, rated only from results before each match; unrated guilds use the ladder gap (never 0). On later results
  it predicts 82% of winners (log loss 0.417), better than the ladder (81%, 0.473). The in-match model has to beat
  this to show it understands play rather than who the better team is. Since ENGINE 17 the baseline is the blend of
  the fitted and lineup measures (see "Data integrity, the Lord, strength").
- `features.py`: the named variables (one line each, with a plain description). Matching own and enemy quantities are
  single differences (separate ones partly cancelled and split the data). One row per 5 s per team; training uses
  every 15 s.
- `model.py`: glass-box model (Explainable Boosting Machine). Baseline = team strength; the curves are what the game
  state adds. Staged complexity (`STAGES`): build variables from 60 matches, interactions from 40, because with few
  matches variables fixed for a whole match only fingerprint matches (seen in batch 0: both models then did worse
  than strength alone). Few boosting rounds (300), because the library's internal stopping test holds out rows, not
  whole matches. Validation holds out whole matches; compared with strength alone and a black box; verdict printed.
  Explanations are in points for an otherwise even game (readable at any win chance), and always come from a model
  fitted without that match (`model.py explain`). Writes `data/model/wp_model.json`, `wp_model.md` and the site page
  `knowledge/wp-model.md`. Corrections: `data/model_corrections.json` (direction, drop, interaction, cap), each
  tested by refitting with and without.
- `learning.py`: the learning report per batch (`data/model/reports/batch_NN.md`, `latest.md`, site page
  `knowledge/learning-report.md`; model snapshots in `data/model/history/`): the honest test, what it leans on and
  how that changed, the curves in words, discovery (interaction screen, untested; the moments it got most wrong),
  Denning's rulings through a model that never saw the match, questions.
- `batch.py`: `pick N` (random matches without replays, appended to `replays/requests.txt`, which starts the fetch
  workflow when pushed), `add` (stored replays not yet trained on become the next batch).
- Requires `pip install --break-system-packages interpret-core` in a new workspace.
- Batch 0 (24 matches): not yet better than strength alone (log loss 0.636 against 0.534; accuracy 74% both). It
  leans on morale difference, knights, Bodyguard, flag lead and Lord damage, but several curves run the wrong way
  (more own knights lowers win chance), which is the expected noise of 24 matches and a natural place for a
  direction correction.

- Candidate variables (`features.CANDIDATES`): proposed by Claude, Denning or discovery; computed for every match and
  retested in every learning report (held-out log loss with and without); moved into `VARIABLES` only once they
  improve predictions on unseen matches.

### A training round
1. `python3 batch.py pick 4`, commit and push `replays/requests.txt` (starts "Fetch replays"); wait for it.
2. `git fetch --depth 1 origin replays:refs/remotes/origin/replays`, `python3 batch.py add`, `python3 learning.py`.
3. Read the report; explain to Denning in words what changed and why (with match moments); ask the questions.
4. Log his corrections in `data/model_corrections.json`, new variables in `features.py`; commit everything.

## State notes kept for comparison

### Current state at 228 matches, before the cutoff (from the handoff)
- Win model: glass box log loss 0.345 against 0.439 for strength alone (clear: gain +0.094, range +0.02 to +0.158);
  85% of winners picked on unseen matches. Batch 10 was 0.314 (first clear result). split_diff moved in after batch 10.
- Learned nodes (11): run outcome, flag swing, run defence, capture speed, power play, fight outcome, split chance,
  split answer, split effect, collapse, pit NPC loss (new). All beat their simple baselines.
- Step 4 (causalchain.py) replaces chain.py in the TQs; TQ 4 now starts from the pit NPC loss node.
- Step 3 (discover.py, "Discovery" workflow) last run at 144 matches; approved discoveries are in lnrows.APPROVED.
- Holds (common.is_hold) kept out of run measures; runner choice: only assassin still clearly worse than a mesmer.
- Collapse: still -4.2 against defending without one (clear); whether it kills depends on the defenders' damage and
  the split's death penalty (both supported). Collapses that don't kill average -5.5, those that kill +3.5.
- Values: death -7.7, knight -6.7, Bodyguard -4.6, archer -3.7, capture +1.9, boost +5.1 (clear); overcap within 10 s
  +0.4 (not clear).

### Known issues and cautions (session 4q and later)
- Learned-node links near the line flip between runs (session 4q: split answer's free defenders and split effect's
  answer latency read supported with 4 bags, not clear yet with 2). Read "supported" by a small margin as a lead.
- Event-layer values use every trained match (not time ordered) and see output only (damage and healing): an
  enchantment or hex that works through energy, speed or armor shows only through what it does to output.
- The power-play node keeps the window's length (exposure): a longer power play has more time to kill.
- Defensive Blinds are rare before a fight's first death (45 in 113 matches overall), so P.19 has little data.
- run_bench's "escort 2+ with the main outnumbered" cell has only 6 runs; treat it as a lead, not a result.
- In the measures, Crippled runners capture more (runs that get far get Crippled): don't read it as Cripple helping.
- "Wasted" removal casts are higher for winners: probably pressure, not error; check before calling it a mistake.
- The model library's fits differ slightly between GitHub processor types; small report differences are noise.
- Data volume: with 113 matches most new links will read "not clear yet"; say so rather than over-reading.

### Portal state on 2026-10-15
- 1,631 matches stored of 1,661 listed (30 left; press Update matches once more).
- Last update: 391 fetched, 9 failed (gvg.report had an outage that day; fixed on their side).
