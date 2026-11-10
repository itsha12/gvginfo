# Guild halls and Flux

Source: Guild Wars Wiki (each hall's own page and its environment effect pages), read 2026-11-10, and the labels on
Model > Guild hall maps. **Denning:** lines are his own account and override the wiki. Lines starting **Tested** are
in-game test results and override both. The same facts, with the map label ids they point to, are in
`data/maps/hall_features.json`.

The monthly Flux changes the rules (gvg.report shows the current one, e.g. Minion Apocalypse in October 2026).

## What every hall has

- Each pit holds the Guild Lord, the Bodyguard, two Knights, and two Archers. Each side has one res shrine and one flag
  spawn, and the same number of every other NPC as the other side.
- **Denning:** Not every hall has footmen, so falling back to footmen is not always an option. Where there are none, a
  retreating team falls back to its front door or its pit.
- Footmen per side, from the labels and the replays: four on Corrupted Isle and Uncharted Isle; two on Isle of
  Meditation, Isle of Solitude, Isle of Jade, Isle of Weeping Stone, Imperial Isle, Warrior's Isle, and Isle of Wurms;
  none on Druid's Isle, Isle of the Dead, Frozen Isle, and Burning Isle. Nomad's Isle reads as none (no footman in 17
  replays; the four Footman labels there stand in the pits where the Knights should be), pending Denning's check.

## Halls with a decision of their own

### Druid's Isle
- Wiki: the water around the flag stand gives +1 Health regeneration (Fount Of Maguuma). A vine seed dropped on the
  glowing circle outside a base grows a vine bridge to its back entrance; dropped anywhere else it knocks down adjacent
  foes for 4 seconds and can be picked up again. One archer covers the rear of each base and two the front. No footmen.
- **Denning:** The water is healing water. The vine seed points inside each base are where the seed spawns; the points
  outside are where it is capped to grow the vine bridge. That way is blocked until the seed is capped, so a base has
  one way in and out without it.
- **Denning:** Decisions: whether to cap the seed, and whether to run the flag the long way or over the vine. Over the
  vine is much shorter (about 7,000 to 7,300 units as drawn, against 8,600 to 8,900) but passes two choke points and
  cannot be run until the seed is capped.
- **Denning:** Not playing in the water while the team is around the flag stand is a micro mistake.

### Isle of Jade
- Wiki: spiked coral slows movement by 10% and deals 25 damage each second while moving. Two teleporters work in
  either direction for either team. Two footmen and three archers overlook each front entrance; one archer covers the back.
- **Denning:** The hazards are the coral. There are two ways to run the flag: over the bridge (longer), or over the
  coral (shorter, but with coral damage and more exposure to the enemy team). The decision is which way to run.
- **Denning:** A split and the back door usually go through the teleporter, and a collapse can too.
- The coral flag runs are drawn through a teleporter: about 7,000 to 7,500 units are walked, against 10,800 to 11,600
  over the bridge.

### Isle of Weeping Stone
- Wiki: a gate facing the flag stand is the only direct link between the main path and the split path, and it opens
  from the split side. Stone Spores (near the giant mushrooms): 33% less damage and healing and -2 to all attributes
  for 10 seconds. Standing in water gives Blessed Water. The res shrine is far from the pit.
- **Denning:** The gate is opened by the gate lock. A team with gate control can collapse on a split through the gate;
  a split with gate control can collapse on the main team the same way.

### Nomad's Isle
- Wiki: quicksand slows movement by 15% and costs 1 Energy on every attack or skill. A teleporter outside the
  quicksand leads to each base, in both directions, for either team. Three archers stand outside each pit.
- **Denning:** The hazard is the quicksand. The back door is usually a split out the teleporter.

### Imperial Isle
- Wiki: flags spawn outside the bases in a corridor of Acid Traps (20 armor-ignoring earth damage each second). The
  teleporters are one way, to the far side of the flag stand, and a carried flag is not dropped. The gate lock does nothing.
- **Denning:** The hazard is the acid trap. There are two flag paths: the short way is more dangerous (the runner can
  be body blocked and runs straight into the enemy team); the long, safe way is longer (about 7,700 to 8,200 units as
  drawn, against 5,300). The decision is which way to run.

### Warrior's Isle
- Wiki: a trebuchet faces each base. A repair kit starts on a bluff opposite each one; holding it and using the lever
  repairs the trebuchet, which is then loaded and fired with the lever, into the ground between the gate and the Lord
  (707 fire damage against 60 armor).
- **Denning:** Of the Catapult markers, the one nearest the flag stand on each side is the repair kit; the others are
  the trebuchets. The Hazard areas are where each trebuchet lands.
- **Denning:** Decisions: whether to run the team's own repair kit back to its base, so the enemy cannot capture the
  trebuchet aimed at it; whether to run the kit to the enemy's trebuchet to capture it; whether to push for the
  enemy's kit while it has not been taken to safety, to steal it and capture their trebuchet.

### Isle of the Dead
- Wiki: tar around the flag stand slows movement by 30%. The two ways out of each base are close together. The res
  shrine is far from the pit and lets resurrected players split at once. The smallest hall. No footmen.
- **Denning:** The front door and back door paths are largely the same: each has two ways out of the base, about equal
  in length, that end in about the same place. The real difference is that the back door (usually the split side) runs
  over the bridge. There are two flag paths, but it is not really a decision, as both end in about the same place.

### Isle of Wurms
- Wiki: the Health Shrine on the southern path gives the team holding it +120 maximum Health and is captured like an
  Alliance Battle shrine. The flag stand is on the northern path, the shortest way between the bases.
- **Denning:** The Other point is the shrine. The decision is whether to fight for it, capture it, or split for it;
  capping it is paid for with a numbers disadvantage or a flag disadvantage elsewhere.

### Frozen Isle
- Wiki: a creature standing still on the ice moves 70% slower for 5 seconds (Icy Ground, checked every 2 seconds).
  Two levers on a dais near the middle each work one side's pair of gates. No footmen.
- **Denning:** There are two gates on each side, worked by that side's lever: when one is open the other is closed.
  Decisions: whether to defend or control the levers, and whether to split through the bridge gates or around the back.

### Burning Isle
- Wiki: lava applies Crippled and Burning every 3 seconds. Lesser Flame Sentinels, hostile to both teams, guard the
  short lava route between the bases; they die of their own Health degeneration at about 8:00. No footmen.
- **Denning:** The two Other points are the flame sentinels. Decisions: whether to kill them at the start (it opens
  splitting for the team, and for the enemy too), and when to split, which depends on whether they are dead (about
  8 minutes if neither team damages them).

## Halls without one

- Corrupted Isle, Uncharted Isle: four footmen a side, at the front and back doors; no map mechanics.
- Isle of Meditation: the largest hall. Miasma on the outer path (5 pips of degeneration, cannot be removed, spreads to
  adjacent creatures). The obelisk flag stand turns the beach statues' Fireballs on the team not holding it.
  **Denning:** the obelisk is still a feature but is almost never used.
- Isle of Solitude: **Denning:** the teleporters are one way: in beside the Guild Lord, out on the main field.
