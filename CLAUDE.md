# Instructions for Claude working in this repository

This repo is Henry's Guild Wars 1 GvG portal and data store. He plays GvG only.

## Answering questions
- Skill facts come from `data/skills.json` (PvP-legal skills only; split skills use their "(PvP)" version).
  Query it with a short Python script instead of reading the whole file into context.
  Fields: id (in-game id), template_id (id used in template codes), name, prof, attr, type, elite, energy, adrenaline,
  sacrifice, upkeep, overcast, activation, recharge, desc (ranges written a..b = rank 0..15), prog (values at ranks 0-21),
  causes, removes, prevents, requires, target, range, aoe, flags, notes (wiki bug/anomaly notes), icon.
- Henry's own tested notes live in `data/skill_notes.json` ({skill id: [notes]}). They override the wiki.
- Mechanics and formulas: `knowledge/`, one page per topic (`index.json` lists them with titles and groups, e.g.
  `conditions.md`, `damage.md`, `weapon-mods.md`, `master-of-damage.md`, `gvg-rules.md`). Lines starting
  **Tested (date):** are Henry's own in-game results and override everything else; `misc.md` holds tested findings
  that don't fit another page.
- Damage/DPS math: `tools/gw_calc.py`. Show assumptions (ranks, armor, weapon, crit chance, modifiers).
- Template codes: `tools/gwtemplate.py` (encode/decode; maps PvP ids to template ids automatically).
- His saved bars: `data/templates.json` (folders → templates → variations, each with a template code).
- Match data from gvg.report (estimates from an in-game observer; AT/mAT matches it recorded):
  - `data/matches/YYYY-MM.json`: one record per match; players have n (character name), pos (party slot 1-8 as on
    gvg.report), p/s (professions), bar (8 in-game
    skill ids), full (all slots observed), attrs (effective ranks where known), dmg, heal, taken, prev (damage prevented),
    deaths, kd (knockdowns dealt), intr (interrupts landed), cond/hexr (removals), hp, weapons, and
    sk = {skill id: [casts, damage, healing incl. Divine Favor, prevented, knockdowns, interrupts]}.
  - Summaries: `data/recent.json` (lineups in party order), `data/builds.json` (families → variations with codes and
    derived runes), `data/guilds.json` (per guild: record, maps, usual lineup per map by party slot, players, recent
    results), `data/players.json`,
    `data/skill_stats.json` (per-skill totals; divide by casts for per-use averages), `data/meta.json` (per month).
  - Per-minute player rates use full match length. Character names are not accounts.
- Wiki change log after each skill refresh: `data/wiki_changes.json`.
- Bar order everywhere: elite first, then the build family's skills from most to least common (then attribute, name),
  so variations line up. Done in `tools/gvgreport/aggregate.mjs` (`orderBar`).
- Runes: derived from bonus ranks (+1 Minor, +2 Major, +3 Superior, +4 Superior + headgear). When Henry gives runes or
  insignias for a build, put them in `data/build_gear.json` (by family id or exact code); they replace derived runes.
  gvg.report doesn't resolve runes or insignias.
- Tournament schedule, map rotation and flux: `assets/js/schedule.js`. Source of truth is the Guild Wars Wiki only:
  wiki.guildwars.com/wiki/Automated_tournament (AT-A/AT-C start times in UTC by weekday, monthly map rotation) and
  wiki.guildwars.com/wiki/Flux (flux by month, changes 07:00 UTC on the 1st). Times stay in UTC and are shown in
  Eastern time only (no UTC shown). No AT-B. Don't use gvg.report for schedule data. Rows are "evenings": a start
  between midnight and 6 a.m. is listed on the previous day's row (Henry's preference).
- Build themes (`theme` in builds.json): core = skills on 70%+ of a family's bars, optional = the rest on 5%+.
- Guild usual lineup (`guilds.json`): a lineup the guild actually played, chosen as the one sharing the most builds with
  their other games (per map too), so it never shows combinations they never ran; plus their most played full lineups.
- Combat-minute stats: `data/player_combat.json` from gvg.report `/api/player-categories?period=all` (fetched by
  `tools/gvgreport/player_stats.mjs` during "Update matches"): per character c (combat ms), m (matches), x (totals for
  damage, kills, assists, healing, prevented, cleanses, interrupts, fake casts, damage taken, knockdowns taken, deaths,
  distance). Only leaderboard-qualified characters are included.
- Site home page is Schedule (`#/`); Recent matches is `#/matches`.
- People: `data/aliases.json` = {"people": {"Person": ["Character", ...]}}, edited from the Players page (tick names,
  assign). Use it when Henry asks about a player by their person name.

## Rules
- Do not edit `data/skills.json` by hand; it is regenerated from the wiki. Put corrections in `data/skill_notes.json`
  or the matching `knowledge/` page as a **Tested (date):** line.
- When Henry reports a tested mechanic, add a **Tested (date):** line to the page it belongs to (or `misc.md` if none
  fits), and mark the matching row in `test-scenarios.md`. When he asks to change a page, edit only that page.
- Never abbreviate Master of Damage. Don't use "My" in page names or text.
- Victory or Death is no longer in the game; ignore wiki text that describes it.

## Layout
- `index.html`, `assets/` — the portal (static site, GitHub Pages, no build step).
- `data/` — skills, template id map, templates, skill notes.
- `knowledge/` — markdown pages shown on the portal's "Mechanics and rules" page (`index.json` lists them; Misc last).
- `tools/` — calculator (`gw_calc.py`), template codec (`gwtemplate.py`), `gvgreport/` (sync + aggregate, Node),
  `wiki/sync.mjs` (skill refresh, Node), `wiki_scraper.js` (browser version of the scraper).
- `.github/workflows/` — "Update matches" and "Update skills from the wiki", started from the portal's Recent matches page.
