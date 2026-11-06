// gvg.report's player directory (which characters belong to one player) and its guild Elo table (tournament-elo.v2),
// saved for the portal and the analysis engine:
//   data/gvgreport/players.json  { updated, source, players: [{ id, name, characters: [{ name, matches }] }] }
//   data/gvgreport/elo.json      { updated, source, rating_model, rows: [{ tag, guild, elo, observed_rating, matches, wins, losses, provisional }] }
// The Elo table is today's: it includes later results, so the engine never trains on it; strength.py rebuilds the
// same Elo in time order from stored matches and uses this table only to check the rebuild.
// Usage: node tools/gvgreport/directory.mjs   (run in a GitHub Action: the workspace can't reach gvg.report)
import fs from "node:fs";
import path from "node:path";
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../..");
const BASE = "https://gvg.report";
const UA = "gvginfo-sync (personal stats portal; https://github.com/itsha12/gvginfo)";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function getJson(u, tries = 4) {
  for (let i = 0; i < tries; i++) {
    try { const r = await fetch(u, { headers: { "User-Agent": UA, Accept: "application/json" } }); if (r.ok) return r.json(); }
    catch (e) {}
    await sleep(2000 * (i + 1));
  }
  throw new Error("failed " + u);
}
export async function directory(root = ROOT) {
  const out = path.join(root, "data/gvgreport"); fs.mkdirSync(out, { recursive: true });
  const players = []; let offset = 0;
  for (let n = 0; n < 200; n++) {
    const j = await getJson(`${BASE}/api/players?limit=100&offset=${offset}`);
    for (const e of j.entries || []) players.push({ id: e.id, name: e.display_name, matches: e.statistics?.matches ?? null,
      characters: (e.characters || []).map((c) => ({ name: c.name, matches: c.matches })) });
    const nxt = j.page?.next_offset;
    if (nxt == null || nxt <= offset || !(j.entries || []).length) break;
    offset = nxt; await sleep(1200);
  }
  fs.writeFileSync(path.join(out, "players.json"), JSON.stringify({ updated: new Date().toISOString(), source: `${BASE}/api/players`, players }, null, 1) + "\n");
  const t = await getJson(`${BASE}/api/tournament-rankings?period=all`);
  const v = t.period?.variants?.all || {};
  const rows = (v.rows || []).map((r) => ({ tag: r.guild_tag, guild: r.guild_name, elo: r.elo, observed_rating: r.observed_rating,
    matches: r.matches_played, wins: r.wins, losses: r.losses, provisional: r.provisional, inactive: r.inactive,
    last_at: r.last_recorded_at_unix_ms }));
  fs.writeFileSync(path.join(out, "elo.json"), JSON.stringify({ updated: new Date().toISOString(), source: `${BASE}/api/tournament-rankings?period=all`,
    rating_model: t.rating_model, period: t.period?.key, rows }, null, 1) + "\n");
  console.log(`${players.length} players, ${rows.length} guilds with Elo`);
}
if (import.meta.url === `file://${process.argv[1]}`) directory().catch((e) => { console.error(e.message); process.exit(1); });
