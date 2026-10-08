# Instructions for Claude working in this repository

This repo is Henry's Guild Wars 1 GvG portal and data store. He plays GvG only.

## Answering questions
- Skill facts come from `data/skills.json` (PvP-legal skills only; split skills use their "(PvP)" version).
  Query it with a short Python script instead of reading the whole file into context.
  Fields: id (in-game id), template_id (id used in template codes), name, prof, attr, type, elite, energy, adrenaline,
  sacrifice, upkeep, overcast, activation, recharge, desc (ranges written a..b = rank 0..15), prog (values at ranks 0-21),
  causes, removes, prevents, requires, target, range, aoe, flags, notes (wiki bug/anomaly notes), icon.
- Henry's own tested notes live in `data/skill_notes.json` ({skill id: [notes]}). They override the wiki.
- Mechanics and formulas: `knowledge/` (start with `verified.md`, then `mechanics.md`, `gvg_rules.md`).
  `knowledge/verified.md` overrides everything else.
- Damage/DPS math: `tools/gw_calc.py`. Show assumptions (ranks, armor, weapon, crit chance, modifiers).
- Template codes: `tools/gwtemplate.py` (encode/decode; maps PvP ids to template ids automatically).
- His saved bars: `data/templates.json` (folders → templates → variations, each with a template code).
- Match data from gvg.report (estimates from an in-game observer; AT/mAT matches it recorded):
  - `data/matches/YYYY-MM.json`: one record per match; players have n (character name), p/s (professions), bar (8 in-game
    skill ids), full (all slots observed), attrs (effective ranks where known), dmg, heal, taken, prev (damage prevented),
    deaths, kd (knockdowns dealt), intr (interrupts landed), cond/hexr (removals), hp, weapons, and
    sk = {skill id: [casts, damage, healing incl. Divine Favor, prevented, knockdowns, interrupts]}.
  - Summaries: `data/recent.json`, `data/builds.json` (families → variations with codes), `data/players.json`,
    `data/skill_stats.json` (per-skill totals; divide by casts for per-use averages), `data/meta.json` (per month).
  - Per-minute player rates use full match length. Character names are not accounts.
- Wiki change log after each skill refresh: `data/wiki_changes.json`.

## Rules
- Do not edit `data/skills.json` by hand; it is regenerated from the wiki. Put corrections in `data/skill_notes.json`
  or `knowledge/verified.md`.
- When Henry reports a tested mechanic, add it to `knowledge/verified.md` with the date.
- Victory or Death is no longer in the game; ignore wiki text that describes it.

## Layout
- `index.html`, `assets/` — the portal (static site, GitHub Pages, no build step).
- `data/` — skills, template id map, templates, skill notes.
- `knowledge/` — markdown knowledge base shown on the Knowledge page (`index.json` lists the pages).
- `tools/` — calculator (`gw_calc.py`), template codec (`gwtemplate.py`), `gvgreport/` (sync + aggregate, Node),
  `wiki/sync.mjs` (skill refresh, Node), `wiki_scraper.js` (browser version of the scraper).
- `.github/workflows/` — "Update matches" and "Update skills from the wiki", started from the portal's Home page.
