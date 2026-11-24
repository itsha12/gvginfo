// Probe gvg.report pages to find the JSON endpoints a page loads (the site is a single-page app), and save samples.
// Usage: node tools/gvgreport/probe.mjs OUTDIR /players /guilds ...   (run in a GitHub Action: the workspace can't reach gvg.report)
import fs from "node:fs";
import path from "node:path";
const BASE = "https://gvg.report";
const UA = "gvginfo-sync (personal stats portal; https://github.com/itsha12/gvginfo)";
// Arguments starting with /api/ are fetched as they are and saved whole (a known endpoint with its query), the rest are
// pages to scan. GREP (env) = a regular expression: every match in a scanned script is saved with the text around it
// (snippets.txt), to see how the site itself uses an endpoint.
const out = process.argv[2]; const args = process.argv.slice(3);
const direct = args.filter((a) => a.startsWith("/api/")); const pages = args.filter((a) => !a.startsWith("/api/"));
const GREP = process.env.GREP ? new RegExp(process.env.GREP, "gi") : null; const snippets = [];
// PICK (env) = comma-separated paths (report.map_geometry,report.sessions.0.map_id): for a directly fetched endpoint,
// save only its key outline and these parts, not the whole response (replay payloads are several MB).
const PICK = (process.env.PICK || "").split(",").map((x) => x.trim()).filter(Boolean);
const dig = (o, p) => p.split(".").reduce((a, k) => (a == null ? a : a[k]), o);
// A pick written "shape:<path>" saves the outline of that part in place of the part itself: every key down to ten levels,
// the keys of up to 80 items of a list merged into one, one example of each value, and a table keyed by ids as one entry. For parts too large to keep whole
// (summary.players is 20 MB) whose layout has to be known before the trim can keep anything from them.
const shapeOf = (vals, depth) => {
  vals = vals.filter((v) => v !== undefined);
  const objs = vals.filter((v) => v && typeof v === "object" && !Array.isArray(v)), arrs = vals.filter(Array.isArray);
  if (arrs.length) { const n = arrs.map((a) => a.length); return { "[]": `${Math.min(...n)} to ${Math.max(...n)} items`, ...(depth < 10 ? { item: shapeOf(arrs.flatMap((a) => a.slice(0, 80)).slice(0, 400), depth + 1) } : {}) }; }
  if (objs.length) { if (depth >= 10) return "{...}"; const keys = [...new Set(objs.flatMap((o) => Object.keys(o)))]; if (keys.length > 40 && keys.filter((k) => /^\d+$|:/.test(k)).length > keys.length / 2) return { "{}": `${keys.length} keys, e.g. ${keys.slice(0, 6).join(", ")}`, value: shapeOf(objs.flatMap((o) => Object.values(o).slice(0, 40)).slice(0, 200), depth + 1) }; return Object.fromEntries(keys.map((k) => [k, shapeOf(objs.map((o) => o[k]), depth + 1)])); }
  const ex = vals.find((v) => v !== null && v !== "" && v !== 0 && v !== false); const v = ex === undefined ? vals[0] : ex;
  return v === undefined ? "absent" : `${v === null ? "null" : typeof v}: ${String(v).slice(0, 60)}`;
};
const pickOf = (j, p) => (p.startsWith("shape:") ? shapeOf([dig(j, p.slice(6))], 0) : dig(j, p) ?? null);
fs.mkdirSync(out, { recursive: true });
const get = async (u) => { const r = await fetch(u, { headers: { "User-Agent": UA } }); return { status: r.status, type: r.headers.get("content-type"), text: await r.text() }; };
const found = new Set(); const seen = new Set();
async function scan(u, depth) {
  if (seen.has(u) || depth > 2) return; seen.add(u);
  let r; try { r = await get(u); } catch (e) { return; }
  for (const m of r.text.matchAll(/["'`](\/api\/[A-Za-z0-9_\-\/{}$.?=&:]+)/g)) found.add(m[1]);
  if (GREP) for (const m of r.text.matchAll(GREP)) { if (snippets.length < 400) snippets.push(`${u} @${m.index}\n${r.text.slice(Math.max(0, m.index - 300), m.index + 500)}\n`); }
  for (const m of r.text.matchAll(/(?:src|href)=["']([^"']+\.js[^"']*)["']|["'](\/[A-Za-z0-9_\-\/.]+\.js)["']|from\s*["'](\.?\.?\/[A-Za-z0-9_\-\/.]+\.js)["']|import\(\s*["'](\.?\.?\/[A-Za-z0-9_\-\/.]+\.js)["']/g)) {
    const s = m[1] || m[2] || m[3] || m[4]; if (!s) continue;
    await scan(new URL(s, u).href, depth + 1);
  }
}
for (const p of pages) await scan(BASE + p, 0);
const list = [...found].sort();
fs.writeFileSync(path.join(out, "endpoints.txt"), list.join("\n") + "\n");
fs.writeFileSync(path.join(out, "scripts.txt"), [...seen].join("\n") + "\n");
// sample every endpoint without template placeholders, plus likely ones
const cands = new Set(list.filter((x) => !/[{$]/.test(x)).map((x) => x.split("?")[0]));
for (const x of ["/api/players", "/api/guilds", "/api/guilds/elo", "/api/elo", "/api/players?limit=50", "/api/guild-elo", "/api/rankings"]) cands.add(x);
for (const c of cands) {
  try {
    const r = await get(BASE + c);
    fs.writeFileSync(path.join(out, c.replace(/[^A-Za-z0-9]+/g, "_") + ".txt"), `${r.status} ${r.type}\n` + r.text.slice(0, 60000));
  } catch (e) {}
  await new Promise((s) => setTimeout(s, 1500));
}
for (const d of direct) {
  try {
    const r = await get(BASE + d);
    let keys = "", picked = null, sizes = "";
    try { const j = JSON.parse(r.text); if (PICK.length) picked = Object.fromEntries(PICK.map((p) => [p, pickOf(j, p)])); const walk = (o, depth) => (o && typeof o === "object" && depth < 3 ? (Array.isArray(o) ? `[${o.length}${o.length ? ": " + walk(o[0], depth + 1) : ""}]` : `{${Object.entries(o).map(([k, v]) => k + (v && typeof v === "object" ? " " + walk(v, depth + 1) : "")).join(", ")}}`) : typeof o); keys = walk(j, 0);
      // SIZES: where the bytes of a response are, every part of 100 KB or more down to four levels (a summary payload is over 100 MB)
      const big = []; const size = (o, name, depth) => { const n = JSON.stringify(o)?.length || 0; if (n >= 100000 || depth === 0) { big.push(`${name || "(all)"} ${n}`); if (depth < 4 && o && typeof o === "object" && !Array.isArray(o)) for (const [k, v] of Object.entries(o)) size(v, name ? name + "." + k : k, depth + 1); else if (Array.isArray(o)) big.push(`${name} [${o.length} items]`); } };
      size(j, "", 0); sizes = big.join("; "); } catch {}
    fs.writeFileSync(path.join(out, "direct_" + d.replace(/[^A-Za-z0-9]+/g, "_") + ".txt"), `${r.status} ${r.type} ${r.text.length} bytes\nKEYS ${keys}\nSIZES ${sizes}\n` + (picked ? JSON.stringify(picked) : r.text.slice(0, 8000000)));
  } catch (e) { fs.writeFileSync(path.join(out, "direct_" + d.replace(/[^A-Za-z0-9]+/g, "_") + ".txt"), "FAILED " + e.message); }
  await new Promise((s) => setTimeout(s, 1500));
}
if (GREP) fs.writeFileSync(path.join(out, "snippets.txt"), snippets.join("\n----\n"));
console.log(list.length, "endpoints found;", direct.length, "fetched directly;", snippets.length, "snippets");
