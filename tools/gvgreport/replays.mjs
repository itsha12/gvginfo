// Fetch match replays from gvg.report, trim them (replay_trim.mjs) and store them in a folder (the "replays" branch).
// Requests come from replays/requests.txt on main: one per line, either a report id / gvg.report link, or
// "latest:N" for the N most recent matches. Matches already stored are skipped, so the same list can be re-run.
// Beside each stored replay goes <report id>.x.json.gz, what the trim leaves out (replay_extras.mjs: flag objects, the
// Lord damage record, what each prot did, degen, interrupt attempts, energy). A stored match without it, or with an older
// version of it, has both payloads fetched again and only that file written: the stored replay is never written again.
// The ids in replays/extras_first.txt (optional, one a line) are done first.
// Usage: node tools/gvgreport/replays.mjs <store dir>   (env: DELAY_MS=4000, MAX_FETCH=500)
import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";
import { trimReplay, TRIM_VERSION } from "./replay_trim.mjs";
import { buildExtras, EXTRAS_VERSION } from "./replay_extras.mjs";

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

// Walkable map outline (pathing trapezoids), stored once per map in maps/<map id>.json.gz.
// gvg.report answers /api/map-geometry by map id for some halls and only by the game's map file id for others (its own
// page sends both, taken from the report's session; a report can also carry the geometry itself). The trimmed replays
// do not keep the file id, so the ids of the halls that need it are listed here (found with the probe, 2026-11-09).
const MAP_FILE_IDS = { 167: 127565, 168: 127610, 170: 127589, 174: 127592, 175: 127643 };
const noGeometry = new Set();
async function saveMap(mapId, session = null, embedded = null) {
  const file = path.join(STORE, "maps", `${mapId}.json.gz`);
  if (!mapId || fs.existsSync(file) || noGeometry.has(mapId)) return;
  let m = (Array.isArray(embedded) ? embedded : []).find((p) => p?.planes?.length) || null;
  const fileId = session?.map_file_id || MAP_FILE_IDS[mapId];
  for (const q of [`map_id=${mapId}`, fileId ? `map_file_id=${fileId}` : null]) {
    if (m || !q) continue;
    const j = await getJson(`${BASE}/api/map-geometry?${q}`, 2).catch(() => null);
    if (j?.pathing_map?.planes?.length) m = j.pathing_map;
    await sleep(1000);
  }
  if (!m) { noGeometry.add(mapId); return console.warn(`  no map geometry for map ${mapId}`); }
  const out = { map_id: m.map_id, map: m.map_name, bounds: m.bounds,
    planes: (m.planes || []).map((p) => ({ plane: p.plane_index, trapezoids: p.trapezoids })) };
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, zlib.gzipSync(JSON.stringify(out), { level: 9 }));
  console.log(`  saved map ${mapId} (${m.map_name})`);
}

// A cheap listing of the newest matches (no replays): listing.json on the replays branch, to find matches to request.
async function listing(n) {
  const out = [];
  let cursor = null;
  while (out.length < n) {
    const page = await getJson(`${BASE}/api/matches?limit=100${cursor ? "&cursor=" + cursor : ""}`);
    for (const e of page?.entries || []) {
      if (out.length >= n) break;
      const g = (e.guilds || e.teams || []).map((x) => x.guild_tag || x.tag || x.label || null);
      out.push({ id: e.id, date: e.date || e.started_at || e.created_at || e.month || null, map: e.map_name || e.map || null,
        teams: g, winner: e.winner_team_id ?? null, occasion: e.tournament_occasion?.occasion_kind || e.observer_type_name || null,
        keys: out.length ? undefined : Object.keys(e) });
    }
    cursor = page?.page?.has_more ? page.page.next_cursor : null;
    if (!cursor) break;
    await sleep(1000);
  }
  fs.writeFileSync(path.join(STORE, "listing.json"), JSON.stringify({ updated: new Date().toISOString(), matches: out }, null, 1));
  console.log(`Listed ${out.length} matches.`);
}

// Write the extras file of a stored match from its two payloads; the index entry gets `x` (the version) and `x_kb`.
function writeExtras(id, entry, raw, sm) {
  const stored = JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(STORE, entry.file))));
  const x = buildExtras(raw, sm, stored);
  const gz = zlib.gzipSync(JSON.stringify(x), { level: 9 });
  fs.writeFileSync(path.join(STORE, entry.file.replace(/\.json\.gz$/, ".x.json.gz")), gz);
  entry.x = EXTRAS_VERSION; entry.x_kb = Math.round(gz.length / 1024);
  if (x.lord?.check) { entry.x_check = x.lord.check; console.warn(`  ${id}: Lord record: ${x.lord.check}`); } else delete entry.x_check;
  return { kb: entry.x_kb, flags: x.flag_objects.length, recaps: x.recaps?.length ?? 0, attempts: x.attempts?.length ?? 0, lord: x.lord?.events.length ?? 0, energy: !!x.energy };
}

async function main() {
  const indexFile = path.join(STORE, "index.json");
  const index = readJson(indexFile, { format: "gvginfo.replay.v1", updated: null, matches: {} });
  const wanted = [];
  for (const line of fs.readFileSync(path.join(ROOT, "replays/requests.txt"), "utf8").split("\n")) {
    const l = line.trim();
    if (!l || l.startsWith("#")) continue;
    const ls = l.match(/^list:(\d+)/i);
    if (ls) { await listing(+ls[1]); continue; }
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
      await saveMap(out.meta.map_id, raw.report?.sessions?.[0], raw.report?.map_geometry?.pathing_maps);
      try { writeExtras(id, index.matches[id], raw, sm); } catch (e) { console.warn(`  ${id}: extras not written: ${e.message}`); }
      done++;
      if (done % 20 === 0) { index.updated = new Date().toISOString(); fs.writeFileSync(indexFile, JSON.stringify(index, null, 1)); }
    } catch (e) { console.warn(`  ${id}: ${e.message}`); }
    await sleep(DELAY);
  }
  index.updated = new Date().toISOString();
  fs.writeFileSync(indexFile, JSON.stringify(index, null, 1));
  console.log(`Stored ${done} new replays.`);

  // the extras of matches stored before they were kept (or kept in an older version): fetched again, the replay left as it is
  const firstFile = path.join(ROOT, "replays/extras_first.txt");
  const first = fs.existsSync(firstFile) ? fs.readFileSync(firstFile, "utf8").split("\n").map((l) => (l.match(ID) || [])[0]?.toLowerCase()).filter(Boolean) : [];
  const need = (id) => index.matches[id]?.file && (index.matches[id].x || 0) < EXTRAS_VERSION && !index.matches[id].x_missing;
  const xtodo = [...new Set([...first, ...Object.keys(index.matches)])].filter(need).slice(0, Math.max(0, MAX - done));
  const left = Object.keys(index.matches).filter(need).length;
  console.log(`${left} stored matches without extras v${EXTRAS_VERSION}; ${xtodo.length} to fetch in this run.`);
  let xdone = 0;
  for (const id of xtodo) {
    const entry = index.matches[id];
    try {
      const raw = await getJson(`${BASE}/api/reports/${encodeURIComponent(id)}?payload=replay`);
      if (!raw?.report) { console.warn(`  ${id}: no replay data now (stored replay kept, no extras)`); entry.x_missing = true; }
      else {
        await sleep(1500);
        const sm = await getJson(`${BASE}/api/reports/${encodeURIComponent(id)}?payload=summary`).catch(() => null);
        // a summary that was there when the replay was stored and cannot be had now is a failed fetch: try again in a later run
        if (!sm?.summary && entry.summary) throw new Error("the summary could not be fetched; left for a later run");
        const r = writeExtras(id, entry, raw, sm);
        console.log(`  ${id}: extras ${r.kb} KB (${r.flags} flag objects, ${r.lord} Lord events, ${r.recaps} recaps, ${r.attempts} interrupt attempts${r.energy ? ", energy" : ""})`);
        xdone++;
      }
      index.updated = new Date().toISOString(); fs.writeFileSync(indexFile, JSON.stringify(index, null, 1));
    } catch (e) { console.warn(`  ${id}: ${e.message}`); }
    await sleep(DELAY);
  }
  console.log(`Wrote the extras of ${xdone} stored matches; ${left - xdone} left.`);
}

main().catch((e) => { console.error(e); process.exit(1); });
