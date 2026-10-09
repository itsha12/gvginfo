"""Guild Wars 1 damage/DPS calculator implementing the Guild Wars Wiki formulas plus Henry's tested results.

weapon hit  = base * custom(1.2) * inscription * weakness * 2^((SL - AL_eff)/40)
SL          = 5*rank (rank<=12) + 2*(rank-12) above 12      (level 20)
crit        = max_base * (same multipliers) * sqrt2           (scythe: * 2^(1/8))
attack-skill '+X damage' is armor-ignoring and added to the same packet (not reduced by Weakness).
Armor penetration: AL_eff = AL * (1 - AP). Only the highest AP applies.

Weapon mods (max values, Guild Wars Wiki, checked 2026-10-08):
  inscription  +15% (conditional ones: Strength and Honor, Guided by Fate, Dance with Death, Too Much Information,
               To the Pain!, Brawn over Brains) or +20% (Vengeance is Mine, Don't Fear the Reaper). The wiki notes the
               +20% ones actually give +21%. Inscriptions affect base weapon damage only.
  Sundering    20% chance per hit of 20% armor penetration (doesn't stack with Strength's AP: highest wins).
  Vampiric     life steal per hit: 3 on one-handed weapons (axe, sword, daggers, spear), 5 on two-handed (hammer,
               scythe, bows); -1 Health regeneration. Life steal ignores armor. The Master of Damage counts it
               (tested by Henry, 2026-10-08).
  Zealous      +1 energy per hit, -1 energy regeneration. No damage change.
  of <Weapon> Mastery  +1 weapon mastery with 20% chance, only while using skills (no effect on auto-attacks).
  Elemental prefixes (Ebon/Fiery/Icy/Shocking) only change the damage type; no change against the Master of Damage.
Weakness (tested by Henry, 2026-10-08): weapon damage 66% less (x0.34) on auto-attacks, and all attributes -1
  (so weapon mastery drops one rank, which lowers damage further, and crit chance drops ~1%).
Cracked Armor: no effect on the Master of Damage (tested; his 60 armor is the floor).
"""
import math

WEAPONS = {  # name: (min, max, attack interval s, crit factor, life steal from Vampiric)
    'axe': (6, 28, 1.33, 2 ** 0.5, 3),
    'sword': (15, 22, 1.33, 2 ** 0.5, 3),
    'hammer': (19, 35, 1.75, 2 ** 0.5, 5),
    'daggers': (7, 17, 1.33, 2 ** 0.5, 3),
    'scythe': (9, 41, 1.5, 2 ** 0.125, 5),
    'spear': (14, 27, 1.5, 2 ** 0.5, 3),
    'flatbow/shortbow': (15, 28, 2.025, 2 ** 0.5, 5),
    'longbow/recurve': (15, 28, 2.475, 2 ** 0.5, 5),
    'hornbow': (15, 28, 2.7, 2 ** 0.5, 5),
}
INSCRIPTION = {0: 1.0, 15: 1.15, 20: 1.21}  # +20% inscriptions behave as +21% per the wiki
WEAKNESS = 0.34


def strike_level(rank):
    return 5 * min(rank, 12) + 2 * max(rank - 12, 0)


def mult(rank, armor, ap=0.0):
    return 2 ** ((strike_level(rank) - armor * (1 - ap)) / 40)


def hit(weapon, rank=12, armor=60, inscription=0, custom=1.2, ap=0.0, bonus=0.0, crit=False,
        weakness=False, mods=1.0):
    """Average (or crit) damage of one hit. `mods` is any extra base-damage multiplier."""
    lo, hi, _, cf, _ = WEAPONS[weapon]
    if weakness:
        rank = max(0, rank - 1)
    if weapon == 'hornbow':
        ap = max(ap, 0.10)
    m = custom * INSCRIPTION.get(inscription, 1 + inscription / 100) * mods * mult(rank, armor, ap)
    if weakness:
        m *= WEAKNESS
    return (hi * m * cf if crit else ((lo + hi) / 2) * m) + bonus


def autoattack_dps(weapon, rank=12, armor=60, inscription=0, crit_chance=None, ias=0.0, dagger_ds=True,
                   sundering=False, vampiric=False, weakness=False, mods=1.0, counts_life_steal=True):
    """Expected auto-attack DPS. Vampiric life steal is added when the target counts it (the Master of Damage does)."""
    _, _, interval, _, steal = WEAPONS[weapon]
    eff_rank = max(0, rank - 1) if weakness else rank
    cc = (eff_rank / 100) if crit_chance is None else crit_chance

    def per_hit(ap):
        args = dict(rank=rank, armor=armor, inscription=inscription, ap=ap, weakness=weakness, mods=mods)
        return (1 - cc) * hit(weapon, **args) + cc * hit(weapon, crit=True, **args)

    dmg = 0.8 * per_hit(0.0) + 0.2 * per_hit(0.20) if sundering else per_hit(0.0)
    if vampiric and counts_life_steal:
        dmg += steal
    if weapon == 'daggers' and dagger_ds:
        dmg *= 1 + (0.02 + 0.02 * eff_rank)  # double strike chance
    return dmg / (interval * (1 - min(ias, 0.33)))


if __name__ == '__main__':
    print('Auto-attack DPS vs the Master of Damage (60 armor), customized max PvP weapon, rank 12, crit chance 12%:')
    print(f'  {"weapon":18s} {"plain":>7s} {"+15%":>7s} {"+20%":>7s} {"Sunder":>7s} {"Vamp":>7s} {"Weak":>7s} {"rank16":>7s}')
    for w in WEAPONS:
        print(f'  {w:18s} {autoattack_dps(w):7.2f} {autoattack_dps(w, inscription=15):7.2f} '
              f'{autoattack_dps(w, inscription=20):7.2f} {autoattack_dps(w, sundering=True):7.2f} '
              f'{autoattack_dps(w, vampiric=True):7.2f} {autoattack_dps(w, weakness=True):7.2f} '
              f'{autoattack_dps(w, rank=16, crit_chance=0.16):7.2f}')
    print('Tested by Henry 2026-10-08: axe ~17.8 and hammer ~20.4 plain are right.')
