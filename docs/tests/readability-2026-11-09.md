# Readability test, 2026-11-09 (after the review rebuild)

A fresh session that had seen nothing of the build read `knowledge/model.md` alone and explained each node in GvG terms.

**Verdict: no.** A GvG player can read most node questions and roughly half the inputs, but cannot tell what the numbers
mean, which inputs actually matter, or what several core terms measure (morale, stand, time down, strength, snare power,
"value", "the usual"). Internal tags (file names, chunk and batch numbers, "discovery, approved", commentators' names)
got in the way.

Three changes asked for, built the same night in `modelpage.py`: (1) a legend defining Gain, Reading, Status, Importance
and the units, with a worked example; (2) a glossary of the recurring measured terms in game language, and internal
tags stripped from input descriptions; (3) one table layout for every node, duplicated rows merged, and each node
ending with one line naming its supported execution inputs ("what to act on").

Still open from the test (needs engine or map changes, queued for the next bundle): the cap shown as exceeded for
collapse without an explanation on the page (now explained in the legend); run outcome, run defence and capture
speed read as one event from two sides (by design; the page now says so); split answer being both a node and an
input (by design: a node's result is another node's cause); "Mesmers free to defend" as a group name for inputs about
defenders in general (rename the map node A.mesa_free to "Defenders free"); "Condition removal (P.5)" covering hex
removal (rename to "Removal"); the Tier 2 table showing definitions but no results (the usual-play results live in the
report; a results column is queued).

The agent's full report is in the session log; the per-node explanations were accurate for 15 of 16 nodes (the win
model read as "a scoreboard, not a fix list", which is right).
