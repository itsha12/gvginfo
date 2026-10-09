# Test scenarios and open questions

Predictions from `tools/gw_calc.py` against the Master of Damage (60 armor). Assumptions: customized max PvP weapon,
rank 12 weapon mastery, 12% critical chance (16% at rank 16), no buffs. Record results on the page they belong to and
mark them here.

| # | Test | Prediction | Result |
|---|---|---|---|
| 1 | Axe auto-attack DPS, 3 minutes | ≈17.8 DPS (≈20.4 with a +15% inscription) | **Confirmed 2026-10-08** |
| 2 | Sword auto-attack | ≈18.1 DPS | |
| 3 | Hammer auto-attack | ≈20.4 DPS; non-crit hits average 32 (23–42), crits 59 | **Confirmed 2026-10-08** |
| 4 | Daggers auto-attack, 12 Dagger Mastery | ≈15.3 DPS (26% double strike) | |
| 5 | Scythe auto-attack (the Master of Damage counts only himself) | ≈21.9 DPS; crits ≈54 (×1.09, not ×1.414); normal hits 11–49 | |
| 6 | Same weapon at 16 mastery (rune + headgear) | ≈+15% damage per hit vs rank 12 (not +33%) | |
| 7 | Any weapon under +33% attack speed (Frenzy, Flurry) | interval ×0.67; DPS ≈ ×1.49 | |
| 8 | Two attack-speed effects stacked | still capped at ×0.67 interval | |
| 9 | Eviscerate at 12 Axe, 12 Strength | non-crit 46–76 (average ≈61); crit ≈92 | |
| 10 | Eviscerate → Agonizing Chop timing | second hit lands about 0.5s after the first (vs 1.33s for a no-activation follow-up) | |
| 11 | Fire spell with stated damage X | exactly X per hit | |
| 12 | Air (lightning) spell with stated damage X | ≈ X × 1.30 (25% armor penetration vs 60 armor) | |
| 13 | Burning alone, 10s | 140 damage counted (−14 Health per second) | |
| 14 | Burning + Poison + Bleeding | capped at −10 pips → 20 per second, not 28 | |
| 15 | Weakness on you, auto-attacking | 66% less damage | **Confirmed 2026-10-08** (also −1 attributes; axe ≈5.5 DPS) |
| 16 | Vampiric axe | +3 per hit counted as damage | **Confirmed 2026-10-08** (counts life steal) |
| 17 | Cracked Armor on the Master of Damage | no change | **Confirmed 2026-10-08** |
| 18 | Hornbow vs longbow | hornbow per hit ×1.11 (10% armor penetration) but slower interval: ≈11.7 vs 11.5 DPS | |
| 19 | +20% inscription ("Vengeance is Mine" below 50% Health) | wiki says it's really +21%: axe ≈21.5 DPS | |
| 20 | Sundering axe | ≈18.6 DPS (+4.6%) | |
| 21 | Weakness with an attack skill | does the "+X" bonus get reduced? (wiki: no, only weapon base damage) | |

## Open questions
- Exact base critical-chance formula.
- Whether the Feb 2026 nature ritual range increase (3500) is live.
- The aggressiveness and order-of-damage-modifiers wiki pages are partly outdated.
- Whether inscription and customization bonuses add or multiply (the calculator multiplies; tests 1 and 3 had no
  inscription, so they don't settle it).
