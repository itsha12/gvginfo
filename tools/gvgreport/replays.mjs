// Fetch match replays from gvg.report, trim them (replay_trim.mjs) and store them in a folder (the "replays" branch).
// Requests come from replays/requests.txt on main: one per line, either a report id / gvg.report link, or
// "latest:N" for the N most recent matches. Matches already stored are skipped, so the same list can be re-run.
// Usage: node tools/gvgreport/replays.mjs <store dir>   (env: DELAY_MS=4000, MAX_FETCH=500)
import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";
import { trimReplay, TRIM_VERSION } from "./replay_trim.mjs";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../..");
const STORE = path.resolve(process.argv[2] || "store");
const BASE = "https://gvg.report";
const UA = "gvginfo-sync (personal stats portal; https://github.com/itsha12/gvginfo)";
const DELAY = +(process.env.DELAY_MS || 4000);
const MAX = +(process.env.MAX_FETCH || 500);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ID = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i;

async function getJson(url, tries = 4) {
  for (let i = 0; i < tries; i++) {
    let r;
    try { r = await fetch(url, { headers: { "User-Agent": UA, Accept: "application/json" } }); }
    catch (e) { console.warn(`  network error on ${url}: ${e.message}`); await sleep(5000 * (i + 1)); continue; }
    if (r.ok) return r.json();
    if (r.status === 404) return null;
    if (r.status >= 500 && r.status !== 503 && i >= 1) break;
    const wait = (+r.headers.get("retry-after") || 0) * 1000 || 5000 * (i + 1);
    console.warn(`  ${r.status} on ${url}; waiting ${wait / 1000}s`);
    await sleep(wait);
  }
  throw new Error(`Gave up on ${url}`);
}
const readJson = (f, fb) => { try { return JSON.parse(fs.readFileSync(f, "utf8")); } catch { return fb; } };

async function latest(n) {
  const ids = [];
  let cursor = null;
  while (ids.length < n) {
    const page = await getJson(`${BASE}/api/matches?limit=100${cursor ? "&cursor=" + cursor : ""}`);
    const list = page?.entries || [];
    for (const m of list) if (m.id && ids.length < n) ids.push(m.id);
    cursor = page?.page?.has_more ? page.page.next_cursor : null;
    if (!cursor || !list.length) break;
    await sleep(1000);
  }
  return ids;
}

// Walkable map outline (pathing trapezoids), stored once per map in maps/<map id>.json.gz
async function saveMap(mapId) {
  const file = path.join(STORE, "maps", `${mapId}.json.gz`);
  if (!mapId || fs.existsSync(file)) return;
  const j = await getJson(`${BASE}/api/map-geometry?map_id=${mapId}`, 2).catch(() => null);
  if (!j?.pathing_map) return console.warn(`  no map geometry for map ${mapId}`);
  const m = j.pathing_map;
  const out = { map_id: m.map_id, map: m.map_name, bounds: m.bounds,
    planes: (m.planes || []).map((p) => ({ plane: p.plane_index, trapezoids: p.trapezoids })) };
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, zlib.gzipSync(JSON.stringify(out), { level: 9 }));
  console.log(`  saved map ${mapId} (${m.map_name})`);
  await sleep(1000);
}

async function main() {
  const indexFile = path.join(STORE, "index.json");
  const index = readJson(indexFile, { format: "gvginfo.replay.v1", updated: null, matches: {} });
  const wanted = [];
  for (const line of fs.readFileSync(path.join(ROOT, "replays/requests.txt"), "utf8").split("\n")) {
    const l = line.trim();
    if (!l || l.startsWith("#")) continue;
    const m = l.match(/^latest:(\d+)/i);
    if (m) wanted.push(...(await latest(+m[1])));
    else if (ID.test(l)) wanted.push(l.match(ID)[0].toLowerCase());
  }
  // matches trimmed with an older format are fetched again
  const todo = [...new Set([...wanted, ...Object.keys(index.matches)])]
    .filter((id) => !index.matches[id] || (index.matches[id].file && (index.matches[id].trim || 1) < TRIM_VERSION)).slice(0, MAX);
  console.log(`${wanted.length} requested, ${todo.length} to fetch.`);
  let done = 0;
  for (const id of Object.keys(index.matches)) { // maps for matches stored before maps were kept
    const f = index.matches[id].file; if (!f) continue;
    try { await saveMap(JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(STORE, f)))).meta.map_id); } catch {}
  }
  for (const id of todo) {
    try {
      const raw = await getJson(`${BASE}/api/reports/${encodeURIComponent(id)}?payload=replay`);
      if (!raw?.report) { console.warn(`  ${id}: no replay data`); index.matches[id] = { missing: true }; continue; }
      await sleep(1500);
      const sm = await getJson(`${BASE}/api/reports/${encodeURIComponent(id)}?payload=summary`).catch(() => null);
      if (!sm?.summary) console.warn(`  ${id}: no summary data (stored without it)`);
      const out = trimReplay(raw, sm);
      const month = new Date(out.meta.started || Date.now()).toISOString().slice(0, 7);
      const file = path.join(month, `${id}.json.gz`);
      fs.mkdirSync(path.join(STORE, month), { recursive: true });
      const gz = zlib.gzipSync(JSON.stringify(out), { level: 9 });
      fs.writeFileSync(path.join(STORE, file), gz);
      const t = out.meta.teams;
      index.matches[id] = { file, date: new Date(out.meta.started).toISOString(), map: out.meta.map,
        teams: t.map((x) => x.tag), winner: t.find((x) => x.id === out.meta.result?.winning_team_id)?.tag || null,
        length_s: out.meta.match_length_s, kb: Math.round(gz.length / 1024), summary: !!sm?.summary, trim: TRIM_VERSION };
      console.log(`  ${id}: ${out.meta.map}, ${t.map((x) => x.tag).join(" vs ")}, ${Math.round(gz.length / 1024)} KB`);
      await saveMap(out.meta.map_id);
      done++;
      if (done % 20 === 0) { index.updated = new Date().toISOString(); fs.writeFileSync(indexFile, JSON.stringify(index, null, 1)); }
    } catch (e) { console.warn(`  ${id}: ${e.message}`); }
    await sleep(DELAY);
  }
  index.updated = new Date().toISOString();
  fs.writeFileSync(indexFile, JSON.stringify(index, null, 1));
  console.log(`Stored ${done} new replays.`);
}

main().catch((e) => { console.error(e); process.exit(1); });
