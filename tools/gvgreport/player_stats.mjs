// Per-character combat-time stats from gvg.report's leaderboard data (/api/player-categories?period=all).
// gvg.report only lists characters that qualify for its leaderboards (regular players), with their total combat time.
// Writes data/player_combat.json: { updated, source, metrics, players: { "Character": { c: combat ms, m: matches,
//   ld: match ms used for distance, x: { metric: total } } } }
import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../..");
const URL_ = "https://gvg.report/api/player-categories?period=all";
const UA = "gvginfo-sync (personal stats portal; https://github.com/itsha12/gvginfo)";
export const METRICS = ["player_damage_direct", "player_damage_hybrid", "player_damage_degeneration", "kills", "assists",
  "healing_done", "damage_prevented", "condition_cleanses", "hex_cleanses", "interrupts", "knockdown_interrupts",
  "fake_casts", "damage_taken", "casts_interrupted", "knockdowns_taken", "deaths", "distance_travelled"];

export async function playerStats(root = ROOT) {
  const r = await fetch(URL_, { headers: { "User-Agent": UA, Accept: "application/json" } });
  if (!r.ok) throw new Error(`gvg.report player stats: HTTP ${r.status}`);
  const data = await r.json();
  const players = {};
  for (const cat of data.period?.categories || []) {
    const m = cat.metrics?.[0];
    if (!m || !METRICS.includes(m.key)) continue;
    for (const row of m.rows || []) {
      const p = (players[row.player_label] ||= { c: 0, m: 0, x: {} });
      p.c = Math.max(p.c, row.combat_duration_ms || 0);
      p.m = Math.max(p.m, row.matches_played || 0);
      if (p.x[m.key] == null) p.x[m.key] = Math.round(row.total || 0);
      if (m.key === "distance_travelled") p.ld = row.match_duration_ms || null;
    }
  }
  const out = { updated: new Date().toISOString(), source: URL_, metrics: METRICS, players };
  fs.writeFileSync(path.join(root, "data/player_combat.json"), JSON.stringify(out) + "\n");
  console.log(`Combat stats for ${Object.keys(players).length} characters.`);
}

if (import.meta.url === `file://${process.argv[1]}`) playerStats().catch((e) => { console.error(e.message); process.exit(1); });
