# Test scenarios and open questions

Source: Guild Wars Wiki, pulled 2026-10-08, plus user testing where marked.

## 12. Known gaps / open questions
- Exact base crit-chance formula (approximation above).
- Weakness damage reduction wording ("66%"): 66% less or 66% of normal — test.
- Whether the Feb 2026 nature ritual range increase (3500) is live.
- Order of damage modifiers page is partly outdated per the wiki.


## 13. Verification scenarios (Master of Damage, 60 armor; predictions from the formulas above)
Assumptions: max PvP weapon (customized ×1.2), rank 12 weapon mastery, crit chance 12% (16% at rank 16), no buffs.
| # | Test | Prediction |
|---|---|---|
| 1 | Axe auto-attack DPS, 3 min | ≈17.8 DPS (≈20.4 with +15% inscription) |
| 2 | Sword auto-attack | ≈18.1 DPS |
| 3 | Hammer auto-attack | ≈20.4 DPS; non-crit hits avg 32 (23–42), crits 59 |
| 4 | Daggers auto-attack, 12 Dagger Mastery | ≈15.3 DPS (26% double-strike; effective interval ≈1.06s) |
| 5 | Scythe auto-attack (MoD counts only him) | ≈21.9 DPS; crit hits ≈54 (×1.09, not ×1.414); normal hits 11–49 |
| 6 | Same weapon at 16 mastery (rune+headgear) | ≈+15% damage per hit vs rank 12 (not +33%) |
| 7 | Any weapon under a +33% IAS (e.g. Frenzy/Flurry) | interval ×0.67; DPS ≈ ×1.49 |
| 8 | Two IAS effects stacked | still capped at ×0.67 interval |
| 9 | Eviscerate at 12 Axe, 12 Strength | non-crit 46–76 (avg ≈61: weapon with 12% AP + 38 armor-ignoring bonus); crit ≈92 |
| 10 | Eviscerate → Agonizing Chop timing | second hit lands ~0.5s after the first (vs 1.33s for a no-activation follow-up) |
| 11 | Fire spell with stated damage X (level 20) | exactly X per hit |
| 12 | Air (lightning) spell with stated damage X | ≈ X × 1.30 (25% AP vs 60 armor) |
| 13 | Burning alone on MoD, 10s | 140 damage counted (−14 HP/s) |
| 14 | Burning + Poison + Bleeding | capped at −10 pips → 20 HP/s, not 28 |
| 15 | Weakness on you, auto-attacking | either ×0.34 or ×0.66 DPS — tells us which reading is right |
| 16 | Vampiric axe | +3 per hit counted as damage (life steal) |
| 17 | Cracked Armor on MoD | no change (60 armor floor); same weapon DPS |
| 18 | Hornbow vs longbow | hornbow per-hit ×1.11 (10% AP vs 60 armor) but slower interval |
