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
    let keys = "";
    try { const j = JSON.parse(r.text); const walk = (o, depth) => (o && typeof o === "object" && depth < 3 ? (Array.isArray(o) ? `[${o.length}${o.length ? ": " + walk(o[0], depth + 1) : ""}]` : `{${Object.entries(o).map(([k, v]) => k + (v && typeof v === "object" ? " " + walk(v, depth + 1) : "")).join(", ")}}`) : typeof o); keys = walk(j, 0); } catch {}
    fs.writeFileSync(path.join(out, "direct_" + d.replace(/[^A-Za-z0-9]+/g, "_") + ".txt"), `${r.status} ${r.type} ${r.text.length} bytes\nKEYS ${keys}\n` + r.text.slice(0, 8000000));
  } catch (e) { fs.writeFileSync(path.join(out, "direct_" + d.replace(/[^A-Za-z0-9]+/g, "_") + ".txt"), "FAILED " + e.message); }
  await new Promise((s) => setTimeout(s, 1500));
}
if (GREP) fs.writeFileSync(path.join(out, "snippets.txt"), snippets.join("\n----\n"));
console.log(list.length, "endpoints found;", direct.length, "fetched directly;", snippets.length, "snippets");
