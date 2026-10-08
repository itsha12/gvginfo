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

## Rules
- Do not edit `data/skills.json` by hand; it is regenerated from the wiki. Put corrections in `data/skill_notes.json`
  or `knowledge/verified.md`.
- When Henry reports a tested mechanic, add it to `knowledge/verified.md` with the date.
- Victory or Death is no longer in the game; ignore wiki text that describes it.

## Layout
- `index.html`, `assets/` — the portal (static site, GitHub Pages, no build step).
- `data/` — skills, template id map, templates, skill notes.
- `knowledge/` — markdown knowledge base shown on the Knowledge page (`index.json` lists the pages).
- `tools/` — calculator, template codec, wiki scraper (`wiki_scraper.js`, runs in a browser on wiki.guildwars.com).
