# GvG Info — handoff for a new Claude chat

Paste or attach this file in a new chat, then say what you want to do next. Last updated 2026-10-08 (evening).

## Who and what
- Henry plays Guild Wars 1, **GvG only**. Goal: one portal to view recent matches, meta, build families with copyable
  template codes, player stats, his own template folders, a skill database with his own notes, and a mechanics
  knowledge base — plus cheap, accurate Q&A with Claude (skills, DPS/energy math, builds, meta, players) without
  uploading big files.
- Repo: **github.com/itsha12/gvginfo** (public; account is itsha12 — one "2", no "3"). Site: https://itsha12.github.io/gvginfo/
  (GitHub Pages, deploy from branch main, root). The repo's `CLAUDE.md` describes every data file and the rules.

## How to resume in a new chat
1. Ask Claude to attach the repo `itsha12/gvginfo` with push access (Claude GitHub App is installed on it) and clone it.
2. Claude should read `CLAUDE.md` first, then `docs/HANDOFF.md` (this file).
3. For questions, Claude should query the JSON files with short scripts, not load them whole.

## Decisions already made
- Skills come from our own sheet (`data/skills.json`), built from the wiki: PvP-legal only, PvE-only skills removed,
  split skills keep only the "(PvP)" version. Henry's own findings go in `data/skill_notes.json` (per skill) and
  **Tested (date):** lines on the matching `knowledge/` page (or `knowledge/misc.md`); both override the wiki and are
  never overwritten by updates.
- Updates are on demand only (no schedules): "Update matches" (gvg.report) and "Update skills from wiki" buttons on the
  portal's Recent matches page start GitHub Actions workflows.
- Templates are editable in the portal; saving uses a fine-grained GitHub key (Contents + Actions: Read and write)
  pasted into the portal's Settings page, stored only in that browser.
- Tolkano.com has no API (server-rendered, Cloudflare-protected) — not used as a data source.
- Victory or Death is no longer in the game (user-verified).

## What exists (all pushed)
- **Portal** (static, no build step): `index.html`, `assets/app.css`, `assets/js/` (core.js, template.js, app.js,
  pages/: schedule (AT-A/AT-C in Toronto time, rotation, flux), guilds (list + per-guild detail), home = recent
  matches + update buttons, builds, meta, players, templates, skills, knowledge
  ("Mechanics and rules"), settings). Design (2026-10-08): white, minimal, architectural — top nav, hairline rules,
  Inter / Inter Tight / IBM Plex Mono, black buttons, gold only for elites and tested lines; type scales with window
  width; home goes two-column at ≥1700px. `marked` is vendored in `assets/vendor/`.
- **Templates**: folders → templates → variations; each template and variation has `equipment: [{name, code, notes}]`
  (equipment template codes, several sets per bar). Saving a bar without equipment prompts for a code.
- **Skills page**: click any column header to sort; costs shown with icons (energy, adrenaline, sacrifice, upkeep,
  overcast, cast, recharge); type and attribute as pills; rank via number box or dropdown.
- **Data**: `data/skills.json` (1,235 skills, both in-game `id` and `template_id`, costs, progression ranks 0–21, causes/
  removes/target/range/aoe, wiki bug/anomaly notes, icon URL), `data/template_id_map.json`, `data/templates.json`,
  `data/skill_notes.json`, `data/matches/YYYY-MM.json` (40 sample matches from 2026-10 so far),
  `data/recent.json`, `builds.json`, `players.json`, `skill_stats.json`, `meta.json`.
- **Tools**: `tools/gvgreport/extract.mjs` + `sync.mjs` + `aggregate.mjs` (Node 22), `tools/wiki/sync.mjs`,
  `tools/gw_calc.py` (damage formulas), `tools/gwtemplate.py` (template codec, verified against gvg.report's encoder),
  `tools/wiki_scraper.js` (browser version, proven), `.github/workflows/update-matches.yml`, `update-wiki.yml`.
- **Knowledge**: `knowledge/` — 26 one-topic pages listed in `knowledge/index.json` with groups (Character, Damage,
  Skills and timing, Creatures, GvG, Testing, Reference, Misc last). Each page has an "Edit on GitHub" link.
  The export below predates this split and the 2026-10-08 test results. `exports/gw1_gvg_reference.md` is the original
  all-in-one text file (~146k tokens) for chats without repo access.

## Status / next steps
- [ ] Henry: enable GitHub Pages; create the GitHub key; press **Update matches** ~4 times to backfill ~1,520 older
      matches (400 per run). Consider a heads-up to the gvg.report dev (Discord) before the backfill.
- [ ] First real run of `tools/wiki/sync.mjs` (never run against the live wiki — workspace couldn't reach it). It aborts if
      it parses <90% of the previous skill count; check `data/wiki_changes.json` afterwards.
- [ ] Calculator page in the portal (damage/DPS/energy-per-second, armor scenarios, attack-speed and cast timing),
      reusing `tools/gw_calc.py` formulas; extend to a bar/rotation simulator.
- [ ] Player alias merging (e.g. several characters → one person) — Henry to supply aliases (asked about "Bounty").
- [ ] Henry's "hidden" tested mechanics → matching `knowledge/` page / `data/skill_notes.json`.
- [ ] Run the remaining scenarios in `knowledge/test-scenarios.md` on the Master of Damage (1, 3, 15, 16, 17 done
      2026-10-08: axe/hammer DPS right, Weakness = 66% less on auto-attacks + −1 attributes, Vampiric life steal
      counted, Cracked Armor no effect).
- [ ] Open questions: base crit-chance formula; whether inscription and customization add or multiply; whether the Feb 2026 nature
      ritual 3500 range is live; aggressiveness page flagged outdated on the wiki.
- [ ] Ideas not started: counter-build helper, per-map mechanics page, patch-watch view, Claude Skill packaging.

## Key technical facts (save re-discovery)
- **Template codes use canonical skill ids**, not PvP runtime ids (e.g. Shadow Form (PvP) 2862 → 826 in codes).
  Mapping: `data/template_id_map.json` (from gvg.report `ui/skill-template.js` + wiki). Encoders map automatically.
- **gvg.report API** (public JSON, undocumented, cache 30s):
  `/api/matches?limit=100&cursor=…` (newest first; `page.next_cursor`, `has_more`);
  `/api/reports/{id}?payload=overview|agents|summary|effects|game-story|replay` (summary ≈1.7 MB gzipped / 30 MB raw —
  per-player per-skill uses, damage, healing, Divine Favor, damage prevented, knockdowns/interrupts via
  `summary.skill_analytics.attributed_outcomes.by_player`, attributes via `players[].attribute_build_v2.known_attributes`,
  weapon sets and max HP); `/api/meta`, `/api/monthly-stats`, `/api/player-categories`, `/api/tournaments/live-index`.
  Exact weapon mods are mostly not recorded, so equipment template codes aren't feasible.
- **Network limits in Claude's workspace**: the shell can't reach wiki.guildwars.com or gvg.report (allowlist); GitHub
  works. To read those sites, use the built-in browser pane on Henry's computer (site access already granted to
  wiki.guildwars.com, gvg.report, tolkano.com) and run `fetch` from the page. Large results get saved to a tool-results
  file in the workspace; the device bridge truncates around 260–600 KB, so pull big data in chunks.
- Headless Chromium for screenshots: `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers` with Python Playwright.
- Damage model: damage = base × 2^((strike level − armor)/40); strike level = 5×weapon rank to 12, +2/rank above; PvP
  weapons auto-customized ×1.2; crit = max × √2 (scythe max × 2^(1/8)); attack-skill "+X" is armor-ignoring; IAS cap
  +33% (interval ×0.67), skills with stated activation hit at half their activation and skip swing recovery.
  Master of Damage: 590 HP, 60 armor, primary Elementalist, counts life steal and degen.
- Guild Lord: 1680 HP, 70 armor, +5 regen; Amulet of Protection caps health loss at 25/s at 0:00 rising to 300/s at
  12:00; flag-stand morale boost gives him +300 max HP. Tiebreak at 28:00 by aggressiveness.
- `tools/gw_calc.py` now models inscriptions (+15%, +20% → ×1.21 per wiki), Sundering, Vampiric (3 one-handed /
  5 two-handed, counted by the Master of Damage), Zealous, mastery suffix (skills only) and Weakness (×0.34, −1 rank).
- WebFetch can read wiki.guildwars.com directly (some pages error; `index.php?title=X&action=raw` often works).
- Party slot: gvg.report labels players "Name (N)" (N = party slot 1-8); `extract.mjs` stores it as `pos`. The 40
  sample matches were backfilled from the overview payload (`/api/reports/{id}?payload=overview`, ~100 KB).
- AT schedule: wiki lists weekday hours "in UTC"; gvg.report's recorded October 2026 (BST) starts are those hours + 1 on
  the UK clock, so `schedule.js` anchors to Europe/London (Henry: server is UK). All 24 observed starts match. The
  Schedule page has a "treat as UTC" switch in case late-October times turn out an hour off.
- gvg.report rune data: `attribute_build_v2.equipment_equivalence_classes[].hp_constraint` only gives ranges
  (possible_vigor_bonuses etc., usually empty) — not usable for exact runes/insignias.
