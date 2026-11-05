// Fetch match replays from gvg.report, trim them (replay_trim.mjs) and store them in a folder (the "replays" branch).
// Requests come from replays/requests.txt on main: one per line, either a report id / gvg.report link, or
// "latest:N" for the N most recent matches. Matches already stored are skipped, so the same list can be re-run.
// Usage: node tools/gvgreport/replays.mjs <store dir>   (env: DELAY_MS=4000, MAX_FETCH=500, EXTRAS=1 to also probe
//        the game-story and map geometry data)
import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";
import { trimReplay } from "./replay_trim.mjs";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../..");
const STORE = path.resolve(process.argv[2] || "store");
const BASE = "https://gvg.report";
const UA = "gvginfo-sync (personal stats portal; https://github.com/itsha12/gvginfo)";
const DELAY = +(process.env.DELAY_MS || 4000);
const MAX = +(process.env.MAX_FETCH || 500);
const EXTRAS = process.env.EXTRAS === "1";
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

async function extras(id, mapId) {
  const dir = path.join(STORE, "probe", id);
  fs.mkdirSync(dir, { recursive: true });
  const tries = { "game-story": `${BASE}/api/reports/${id}?payload=game-story` };
  for (const q of [`map_id=${mapId}`, `map=${mapId}`, `id=${mapId}`, `report=${id}`, `report_id=${id}`]) tries[`map-geometry_${q.split("=")[0]}`] = `${BASE}/api/map-geometry?${q}`;
  for (const [name, url] of Object.entries(tries)) {
    try {
      const j = await getJson(url, 2);
      console.log(`  extra ${name}: ${j ? JSON.stringify(j).length + " bytes" : "not found"}`);
      if (j) fs.writeFileSync(path.join(dir, `${name}.json.gz`), zlib.gzipSync(JSON.stringify(j)));
    } catch (e) { console.log(`  extra ${name}: ${e.message}`); }
    await sleep(1000);
  }
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
  const todo = [...new Set(wanted)].filter((id) => !index.matches[id]).slice(0, MAX);
  console.log(`${wanted.length} requested, ${todo.length} to fetch.`);
  let done = 0;
  for (const id of todo) {
    try {
      const raw = await getJson(`${BASE}/api/reports/${encodeURIComponent(id)}?payload=replay`);
      if (!raw?.report) { console.warn(`  ${id}: no replay data`); index.matches[id] = { missing: true }; continue; }
      const out = trimReplay(raw);
      const month = new Date(out.meta.started || Date.now()).toISOString().slice(0, 7);
      const file = path.join(month, `${id}.json.gz`);
      fs.mkdirSync(path.join(STORE, month), { recursive: true });
      const gz = zlib.gzipSync(JSON.stringify(out), { level: 9 });
      fs.writeFileSync(path.join(STORE, file), gz);
      const t = out.meta.teams;
      index.matches[id] = { file, date: new Date(out.meta.started).toISOString(), map: out.meta.map,
        teams: t.map((x) => x.tag), winner: t.find((x) => x.id === out.meta.result?.winning_team_id)?.tag || null,
        length_s: out.meta.match_length_s, kb: Math.round(gz.length / 1024) };
      console.log(`  ${id}: ${out.meta.map}, ${t.map((x) => x.tag).join(" vs ")}, ${Math.round(gz.length / 1024)} KB`);
      if (EXTRAS) await extras(id, out.meta.map_id);
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
