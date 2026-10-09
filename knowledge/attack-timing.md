# Attack speed and timing

Source: Guild Wars Wiki, pulled 2026-10-08. Lines starting **Tested** are in-game test results and override the wiki.

## Auto-attacks and attack skills
- Auto-attacks: one hit per attack interval; the hit lands halfway through the swing.
- Attack skill with no stated activation time: takes one normal attack interval of your weapon and hits at the
  halfway point. Chaining these has the same cadence as auto-attacking.
- Attack skill with a stated activation time (e.g. ½s or 1s): that activation replaces the weapon swing; the hit lands
  halfway through it, and it skips the "return to neutral" second half of the previous attack. So a short-activation
  attack used right after another attack lands much sooner. Example: Executioner's Strike after Eviscerate lands
  1.33s later; Agonizing Chop (1s activation) after Eviscerate lands 0.5s later.
- Example: Protector's Strike under Frenzy — interval ⅓s, connects about 0.17s after activation.

## Attack speed (IAS and slows)
- Attack speed changes scale attack intervals and attack-skill activation times. Effects that change spell cast time
  (Migraine etc.) don't affect attack skills.
- Stacking is multiplicative, capped at +33% faster (interval ×0.67) and −50% slower (interval ×1.5).
- A stated "+33%" shortens the interval by 33% → about +49% attacks per second; "+25%" → +33%; "−30%" → −23%;
  "−50%" → −33%. Real rate gain = x / (100 − x).

## Aftercast
- Attack skills with a stated activation have no aftercast, except Ranger bow skills with activation times (¾s).
- Bow, dagger and hammer attack skills without activation have a ¾s animation; other weapons ½s.
