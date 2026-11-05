// Discovery test: find which gvg.report data holds a match's replay (cast timeline, positions).
// Reads report ids from replays/requests.txt (one per line), saves what it finds under replays/probe/<id>/.
// Usage: node tools/gvgreport/replay_probe.mjs
import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../..");
const BASE = "https://gvg.report";
const UA = "gvginfo-sync (personal stats portal; https://github.com/itsha12/gvginfo)";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const OUT = path.join(ROOT, "replays/probe");

async function get(url, accept) {
  try {
    const r = await fetch(url, { headers: { "User-Agent": UA, Accept: accept } });
    return { status: r.status, type: r.headers.get("content-type") || "", body: r.ok ? await r.text() : "" };
  } catch (e) { return { status: 0, type: "", body: "", err: e.message }; }
}

// Short description of a JSON value's shape (keys, array lengths), so big payloads can be judged without reading them
function shape(v, depth = 0) {
  if (Array.isArray(v)) return v.length ? [`len ${v.length}`, depth < 4 ? shape(v[0], depth + 1) : "..."] : [];
  if (v && typeof v === "object") {
    if (depth >= 4) return `{${Object.keys(v).length} keys}`;
    const o = {};
    for (const k of Object.keys(v).slice(0, 60)) o[k] = shape(v[k], depth + 1);
    return o;
  }
  return typeof v;
}

async function probe(id) {
  const dir = path.join(OUT, id);
  fs.mkdirSync(dir, { recursive: true });
  const log = { id, fetched: new Date().toISOString(), page: null, scripts: [], api_strings: [], payloads: {} };

  // 1. the report page and its scripts: look for API paths and payload names the site's own replay uses
  const page = await get(`${BASE}/report/${id}`, "text/html");
  log.page = { status: page.status, bytes: page.body.length };
  const srcs = new Set();
  for (const m of page.body.matchAll(/(?:src|href)=["']([^"']+\.m?js[^"']*)["']/g)) srcs.add(new URL(m[1], BASE).href);
  const apiStrings = new Set(), payloadNames = new Set(), snippets = [];
  const scan = (text, from) => {
    for (const m of text.matchAll(/["'`](\/api\/[^"'`\s]{1,120})["'`]/g)) apiStrings.add(m[1]);
    for (const m of text.matchAll(/payload[=:]\s*["'`]?([a-z_]{3,30})/g)) payloadNames.add(m[1]);
    for (const m of text.matchAll(/\/api\/[a-z_\-]*(report|replay|timeline|event|position|cast|frame|track)/gi)) {
      const i = m.index;
      snippets.push({ from, text: text.slice(Math.max(0, i - 250), i + 350) });
    }
  };
  scan(page.body, "page");
  for (const s of srcs) {
    if (!s.startsWith(BASE)) continue;
    const js = await get(s, "*/*");
    log.scripts.push({ url: s, status: js.status, bytes: js.body.length });
    // follow imported chunks one level deep
    for (const m of js.body.matchAll(/["'`](\.{0,2}\/?[\w\-./]*?\.m?js)["'`]/g)) {
      try { const u = new URL(m[1], s).href; if (u.startsWith(BASE) && !srcs.has(u)) srcs.add(u); } catch {}
    }
    scan(js.body, s);
    await sleep(300);
  }
  log.api_strings = [...apiStrings].sort();
  fs.writeFileSync(path.join(dir, "snippets.json"), JSON.stringify(snippets.slice(0, 200), null, 1));

  // 2. try the report API with each payload name (known, guessed, and any found in the scripts)
  const names = new Set(["", "summary", "overview", "full", "replay", "timeline", "events", "map", "positions",
    "casts", "playback", "all", "raw", "detail", "details", ...payloadNames]);
  for (const n of names) {
    const url = `${BASE}/api/reports/${encodeURIComponent(id)}${n ? "?payload=" + n : ""}`;
    const r = await get(url, "application/json");
    const entry = { status: r.status, bytes: r.body.length };
    if (r.body && r.type.includes("json")) {
      try {
        const j = JSON.parse(r.body);
        entry.shape = shape(j);
        fs.writeFileSync(path.join(dir, `payload-${n || "none"}.json.gz`), zlib.gzipSync(r.body));
      } catch { entry.note = "not valid JSON"; }
    }
    log.payloads[n || "(none)"] = entry;
    await sleep(800);
  }
  fs.writeFileSync(path.join(dir, "probe.json"), JSON.stringify(log, null, 1));
  console.log(`${id}: page ${page.status}, ${log.scripts.length} scripts, ${log.api_strings.length} api strings, ` +
    Object.entries(log.payloads).map(([k, v]) => `${k}=${v.status}/${v.bytes}`).join(" "));
}

const ids = fs.readFileSync(path.join(ROOT, "replays/requests.txt"), "utf8").split(/\s+/)
  .map((l) => (l.match(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i) || [])[0]).filter(Boolean);
for (const id of ids) await probe(id);
