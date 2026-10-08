// Pull new matches from gvg.report into data/matches/, then rebuild the aggregate files.
// Usage: node tools/gvgreport/sync.mjs   (env: MAX_MATCHES=400, DELAY_MS=1500)
import fs from "node:fs";
import path from "node:path";
import { extractMatch } from "./extract.mjs";
import { aggregate } from "./aggregate.mjs";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../..");
const DIR = path.join(ROOT, "data/matches");
const BASE = "https://gvg.report";
const MAX = +(process.env.MAX_MATCHES || 400);
const DELAY = +(process.env.DELAY_MS || 1500);
const UA = "gvginfo-sync (personal stats portal; https://github.com/itsha12/gvginfo)";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function getJson(url, tries = 4) {
  for (let i = 0; i < tries; i++) {
    const r = await fetch(url, { headers: { "User-Agent": UA, Accept: "application/json" } });
    if (r.ok) return r.json();
    if (r.status === 404) return null;
    const wait = (+r.headers.get("retry-after") || 0) * 1000 || 5000 * (i + 1);
    console.warn(`  ${r.status} on ${url}; waiting ${wait / 1000}s`);
    await sleep(wait);
  }
  throw new Error(`Gave up on ${url}`);
}

const readJson = (f, fb) => { try { return JSON.parse(fs.readFileSync(f, "utf8")); } catch { return fb; } };
const writeJson = (f, d) => { fs.mkdirSync(path.dirname(f), { recursive: true }); fs.writeFileSync(f, JSON.stringify(d) + "\n"); };

export async function sync() {
  const index = readJson(path.join(DIR, "index.json"), { matches: {}, updated: null });
  // 1. list every match on gvg.report (newest first)
  const listed = [];
  let cursor = "";
  do {
    const page = await getJson(`${BASE}/api/matches?limit=100${cursor ? "&cursor=" + cursor : ""}`);
    if (!page) break;
    listed.push(...page.entries);
    cursor = page.page?.has_more ? page.page.next_cursor : "";
    await sleep(400);
  } while (cursor);
  const todo = listed.filter((e) => !index.matches[e.id]).slice(0, MAX);
  console.log(`${listed.length} matches on gvg.report, ${Object.keys(index.matches).length} already stored, fetching ${todo.length}`);

  // 2. fetch and extract each new match
  const months = {};
  const monthFile = (m) => path.join(DIR, `${m}.json`);
  const load = (m) => (months[m] ||= readJson(monthFile(m), []));
  let done = 0;
  for (const e of todo) {
    const month = e.month || (e.date || "").slice(0, 7) || "unknown";
    let rec;
    try {
      const rep = await getJson(`${BASE}/api/reports/${encodeURIComponent(e.id)}?payload=summary`);
      rec = extractMatch(e, rep?.summary || {});
      if (!rep?.summary) rec.partial = true;
    } catch (err) {
      console.warn(`  skipped ${e.id}: ${err.message}`);
      continue;
    }
    const list = load(month).filter((m) => m.id !== rec.id);
    list.push(rec);
    months[month] = list;
    index.matches[e.id] = month;
    if (++done % 25 === 0) { flush(); console.log(`  ${done}/${todo.length}`); }
    await sleep(DELAY);
  }
  function flush() {
    for (const [m, list] of Object.entries(months)) writeJson(monthFile(m), list.sort((a, b) => (b.at || 0) - (a.at || 0)));
    index.updated = new Date().toISOString();
    index.listed = listed.length;
    writeJson(path.join(DIR, "index.json"), index);
  }
  flush();
  console.log(`Stored ${done} new matches; ${listed.length - Object.keys(index.matches).length} still to fetch.`);
  // 3. rebuild aggregates
  aggregate(ROOT);
}

if (import.meta.url === `file://${process.argv[1]}`) sync().catch((e) => { console.error(e); process.exit(1); });
