"""Guild Wars 1 damage/DPS calculator implementing the Guild Wars Wiki formulas.

weapon hit  = base * custom(1.2) * mods * 2^((SL - AL_eff)/40)
SL          = 5*rank (rank<=12) + 2*(rank-12) above 12      (level 20)
crit        = max_base * custom * mods * 2^((SL - AL_eff)/40) * sqrt2   (scythe: * 2^(1/8))
attack-skill '+X damage' is armor-ignoring and added to the same packet.
Armor penetration: AL_eff = AL * (1 - AP).
"""
import math

WEAPONS = {  # name: (min, max, attack interval s, crit factor)
    'axe': (6, 28, 1.33, 2 ** 0.5),
    'sword': (15, 22, 1.33, 2 ** 0.5),
    'hammer': (19, 35, 1.75, 2 ** 0.5),
    'daggers': (7, 17, 1.33, 2 ** 0.5),
    'scythe': (9, 41, 1.5, 2 ** 0.125),
    'spear': (14, 27, 1.5, 2 ** 0.5),
    'flatbow/shortbow': (15, 28, 2.025, 2 ** 0.5),
    'longbow/recurve': (15, 28, 2.475, 2 ** 0.5),
    'hornbow': (15, 28, 2.7, 2 ** 0.5),
}


def strike_level(rank):
    return 5 * min(rank, 12) + 2 * max(rank - 12, 0)


def mult(rank, armor, ap=0.0):
    return 2 ** ((strike_level(rank) - armor * (1 - ap)) / 40)


def hit(weapon, rank=12, armor=60, mods=1.0, custom=1.2, ap=0.0, bonus=0.0, crit=False):
    lo, hi, _, cf = WEAPONS[weapon]
    m = custom * mods * mult(rank, armor, ap)
    if crit:
        return hi * m * cf + bonus
    return ((lo + hi) / 2) * m + bonus


def autoattack_dps(weapon, rank=12, armor=60, mods=1.0, crit_chance=None, ias=0.0, dagger_ds=True):
    lo, hi, interval, cf = WEAPONS[weapon]
    cc = (rank / 100) if crit_chance is None else crit_chance
    per_hit = (1 - cc) * hit(weapon, rank, armor, mods) + cc * hit(weapon, rank, armor, mods, crit=True)
    eff_interval = interval * (1 - ias)
    if weapon == 'daggers' and dagger_ds:
        per_hit *= 1 + (0.02 + 0.02 * rank)  # double strike chance
    return per_hit / eff_interval


if __name__ == '__main__':
    print('Auto-attack DPS vs 60 AL (Master of Damage), customized max weapon, rank 12, crit chance = 12%:')
    for w in WEAPONS:
        print(f'  {w:18s} plain {autoattack_dps(w):6.2f} | +15% insc {autoattack_dps(w, mods=1.15):6.2f} | rank16 {autoattack_dps(w, rank=16, crit_chance=0.16):6.2f}')
    print('Wiki cross-check (uncustomized, no crits, rank 12): hammer', round(27 / 1.75, 2), 'sword', round(18.5 / 1.333333, 2))
