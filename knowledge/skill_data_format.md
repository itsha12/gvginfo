# How the skill data is written

## 0. How to use this file (instructions for the assistant)

- Treat the skill entries below as the authoritative numbers. Quote values from the file; do not rely on memory for
  skill numbers, because many skills were rebalanced in 2026.
- Only PvP-legal skills are listed. PvE-only skills are excluded. Where a skill has a separate PvP version, only the
  "(PvP)" version is listed — that is the version used in GvG.
- When asked for damage, DPS, healing, timing or energy math, compute it with the formulas in sections 3–7 and show
  the assumptions (attribute ranks, armor, weapon, crit chance, modifiers).
- Mark anything that comes from general knowledge rather than this file as such.
- Section 15 holds mechanics the user has verified by in-game testing. Those override the wiki when they conflict.
- Default GvG assumptions unless the user says otherwise: level 20, max armor, max-damage PvP weapons (PvP weapons are
  always max stats, requirement 9, and auto-customized for +20% damage), everything else (runes, insignia,
  inscriptions, attribute spread) variable.

### Skill entry format
```
Name #ID | [Elite] Type | Campaign | costs
  Description. Ranges shown as a..b = value at attribute rank 0..rank 15.
  ~ Variable :: values at ranks 0-21, grouped in fives (e.g. "10-14: v10 v11 v12 v13 v14")
  # tags: conditions/effects caused, removed or prevented; target; range; area of effect; flags
  ! BUG / ANOMALY notes from the wiki (mechanical quirks not in the description)
```
Costs: E = energy, Ad = adrenaline strikes, S = sacrifice (% of max Health), U-1 = upkeep (−1 energy regeneration
pip while maintained), O = overcast, C = activation (cast) time in seconds, R = recharge in seconds. No C means no
activation time (instant, or for attack skills: uses the weapon's attack timing — see section 5).
`[derived]` progression lines were not on the wiki's progression table; they are computed from the description range
with the wiki's own formula: value(rank) = round(v0 + rank × (v15 − v0)/15), rounding half away from zero.
"#ID" is the skill ID used in skill template codes (from Skill_template_format/Skill_list).

Effective attribute ranks above 12 come from a superior rune (+3, primary profession only), headgear (+1, primary
profession only) and skills/effects. Rank cap is 20 (21 with weapon "+1 attribute (chance)" mods).


## 14. Wiki bug/anomaly notes
Included per skill as `!` lines. Lines tagged "[from PvE version page]" are notes written for the PvE version of a skill
that also has a PvP version; they usually still apply but check numbers.
