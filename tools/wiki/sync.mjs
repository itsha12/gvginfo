// Rebuild data/skills.json from the Guild Wars Wiki and write data/wiki_changes.json listing what changed.
// PvP-legal skills only: PvE-only skills are dropped and split skills keep only their "(PvP)" version.
// Henry's own notes live in data/skill_notes.json and are never touched here.
import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../..");
const D = (f) => path.join(ROOT, "data", f);
const WIKI = "https://wiki.guildwars.com";
const UA = "gvginfo-sync (personal stats portal; https://github.com/itsha12/gvginfo)";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const readJson = (f, fb) => { try { return JSON.parse(fs.readFileSync(f, "utf8")); } catch { return fb; } };

async function api(q) {
  for (let i = 0; i < 4; i++) {
    const r = await fetch(`${WIKI}/api.php?` + new URLSearchParams({ ...q, format: "json", formatversion: "2" }), { headers: { "User-Agent": UA } });
    if (r.ok) { await sleep(300); return r.json(); }
    await sleep(3000 * (i + 1));
  }
  throw new Error("Wiki API unavailable");
}

// ---------- wikitext helpers (same logic as tools/wiki_scraper.js) ----------
function tpl(w, nameRe) {
  const re = new RegExp("\\{\\{\\s*(" + nameRe + ")\\s*(?=[|\\n}])", "ig"); let m; const outs = [];
  while ((m = re.exec(w))) {
    let i = m.index + 2, d = 1;
    while (i < w.length && d > 0) { if (w.startsWith("{{", i)) { d++; i += 2; } else if (w.startsWith("}}", i)) { d--; i += 2; } else i++; }
    outs.push({ name: m[1].trim().toLowerCase(), body: w.slice(m.index + m[0].length, i - 2) });
  }
  return outs;
}
function params(body) {
  const ps = []; let d = 0, cur = "";
  for (let i = 0; i < body.length; i++) {
    const c2 = body.substr(i, 2);
    if (c2 === "{{" || c2 === "[[") { d++; cur += c2; i++; continue; }
    if (c2 === "}}" || c2 === "]]") { d--; cur += c2; i++; continue; }
    if (body[i] === "|" && d === 0) { ps.push(cur); cur = ""; continue; }
    cur += body[i];
  }
  ps.push(cur);
  const named = {};
  ps.slice(1).forEach((p) => { const m = p.match(/^\s*([\w \-]+?)\s*=([\s\S]*)$/); if (m) named[m[1].toLowerCase()] = m[2].trim(); });
  return named;
}
const frac = { "1/4": "¼", "1/2": "½", "3/4": "¾", "1/3": "⅓", "2/3": "⅔" };
function clean(s) {
  if (!s) return "";
  let x = s.replace(/<!--[\s\S]*?-->/g, "").replace(/<br\s*\/?>/gi, " ").replace(/<ref[\s\S]*?<\/ref>/gi, "").replace(/<\/?[a-z][^>]*>/gi, "");
  for (let k = 0; k < 6; k++) {
    x = x.replace(/\{\{([^{}]*)\}\}/g, (_, inner) => {
      const a = inner.split("|").map((s) => s.trim()); const n = a[0].toLowerCase();
      if (n === "gr" || n === "gr2") { const sign = a[3] === "+" || a[3] === "-" ? a[3] : ""; const pct = a[4] === "%" ? "%" : ""; return sign + a[1] + ".." + a[2] + pct; }
      if (frac[n]) return frac[n];
      if (n === "gray" || n === "grey") return "(" + a.slice(1).join("|") + ")";
      if (n === "sic" || n === "verify" || n === "citation needed") return "";
      if (/^(skill icon|skill link|duplicate skill icon)$/.test(n)) return a[1];
      if (/^(w|r|mo|n|me|e|a|rt|p|d|any|x|monster)$/.test(n)) return "";
      return a.slice(1).join(" ");
    });
  }
  return x.replace(/\[\[([^\]|]*)\|([^\]]*)\]\]/g, "$2").replace(/\[\[([^\]]*)\]\]/g, "$1").replace(/'''?/g, "").replace(/\s+/g, " ").trim();
}
const rnd = (v) => Math.sign(v) * Math.round(Math.abs(v));
function prog(w) {
  const out = [];
  for (const p of tpl(w, "skill progression(?: factored| max10(?: old)?| max12)?")) {
    const named = params("x|" + p.body.replace(/^[^|\n]*/, ""));
    const top = p.name.includes("max10") ? 10 : p.name.includes("max12") ? 12 : 15;
    for (const k of ["1", "2", "3", "4", "5", "f"]) {
      const nm = named["var" + k + " name"]; if (!nm) continue;
      const a0 = parseFloat(named["var" + k + " at0"]), aT = parseFloat(named["var" + k + " at" + top]);
      if (isNaN(a0) || isNaN(aT)) continue;
      const f = k === "f" ? parseFloat(named["varf factor"] || "1") : 1;
      const values = []; for (let r = 0; r <= (top === 15 ? 21 : top); r++) values.push(rnd(a0 + (r * (aT - a0)) / top) * f);
      out.push({ name: clean(nm), values, derived: false });
    }
    if (named["varx name"]) { const values = []; for (let r = 0; r <= 21; r++) if (named["varx" + r] !== undefined) values.push(clean(named["varx" + r])); out.push({ name: clean(named["varx name"]), values, derived: false }); }
  }
  return out;
}
const notes = (w) => tpl(w, "bug|anomaly").map((t) => (t.name === "bug" ? "BUG: " : "ANOMALY: ") + clean(t.body.replace(/^\s*\|/, ""))).filter((s) => s.length > 8);

export async function syncWiki() {
  // 1. skill list with ids
  const L = await api({ action: "query", prop: "revisions", rvprop: "content", rvslots: "main", titles: "Skill_template_format/Skill_list" });
  const listText = L.query.pages[0].revisions[0].slots.main.content;
  const list = [...listText.matchAll(/^\|\s*(\d+)\s*\|\|\s*\[\[([^\]|]+)(?:\|[^\]]*)?\]\]/gm)].map((m) => ({ id: +m[1], title: m[2].trim() }));
  // 2. pages
  const pages = {}, redirects = {};
  const titles = [...new Set(list.map((r) => r.title))];
  for (let i = 0; i < titles.length; i += 50) {
    const d = await api({ action: "query", prop: "revisions", rvprop: "content", rvslots: "main", redirects: "1", titles: titles.slice(i, i + 50).join("|") });
    (d.query.redirects || []).forEach((r) => (redirects[r.from] = r.to));
    (d.query.normalized || []).forEach((r) => (redirects[r.from] = r.to));
    d.query.pages.forEach((p) => (pages[p.title] = p.missing ? null : p.revisions[0].slots.main.content));
  }
  const res = (t) => { let x = t; for (let i = 0; i < 3 && redirects[x]; i++) x = redirects[x]; return x; };
  // 3. parse
  const all = [];
  for (const r of list) {
    const t = res(r.title); const w = pages[t]; if (!w) continue;
    const ib = tpl(w, "skill infobox")[0]; if (!ib) continue;
    const raw = params("x|" + ib.body.replace(/^[^|\n]*/, ""));
    const f = {};
    for (const [k, v] of Object.entries(raw)) f[k.replace(/^casues/, "causes").replace(/^remvoes/, "removes").replace(/^reqyires/, "requires").replace(/^targert$/, "target")] = v;
    const yes = (k) => /^\s*y/i.test(f[k] || "");
    const many = (pre) => Object.keys(f).filter((k) => new RegExp("^" + pre + "\\d*$").test(k)).sort().map((k) => clean(f[k])).filter(Boolean);
    const flags = [];
    if (yes("pbaoe")) flags.push("point_blank_aoe");
    if (yes("unblockable")) flags.push("unblockable");
    if (yes("interrupt")) flags.push("interrupts");
    const extra = {};
    if (clean(f.special)) extra.special = clean(f.special);
    const checks = many("checks"); if (checks.length) extra.checks = checks;
    all.push({
      id: r.id, name: clean(f.name) || t, title: t, prof: clean(f.profession) || "None", attr: clean(f.attribute) || "No Attribute",
      type: clean(f.type), elite: yes("elite"), campaign: clean(f.campaign),
      energy: clean(f.energy), adrenaline: clean(f.adrenaline), sacrifice: clean(f.sacrifice), upkeep: clean(f.upkeep),
      overcast: clean(f.overcast), activation: clean(f.activation), recharge: clean(f.recharge),
      pvp_version: yes("is-pvp") || /\(PvP\)$/.test(t), pve_only: yes("pve-only"),
      desc: clean(f.description), prog: prog(w), notes: notes(w),
      causes: many("causes"), removes: many("removes"), prevents: many("prevents"), requires: many("requires"),
      target: clean(f.target) || null, range: clean(f.range) || null, aoe: [clean(f.aoe), clean(f.aoe2)].filter(Boolean), flags, extra,
    });
  }
  // 4. PvP-legal filter
  const pvpBase = new Set(all.filter((s) => s.pvp_version).map((s) => s.title.replace(/ \(PvP\)$/, "")));
  const byTitle = Object.fromEntries(all.map((s) => [s.title, s]));
  const keep = all.filter((s) => !s.pve_only && !(!s.pvp_version && pvpBase.has(s.title)));
  for (const s of keep) {
    if (s.pvp_version) { const base = byTitle[s.title.replace(/ \(PvP\)$/, "")]; if (base?.notes.length) s.notes = s.notes.concat(base.notes.map((n) => n + " [from PvE version page]")); }
    delete s.pve_only;
    if (s.attr !== "No Attribute") for (const m of s.desc.matchAll(/(\d+(?:\.\d+)?)\.\.(\d+(?:\.\d+)?)/g)) {
      const a = +m[1], b = +m[2];
      if (s.prog.some((p) => +p.values[0] === a && +p.values[15] === b)) continue;
      const values = []; for (let k = 0; k <= 21; k++) values.push(rnd(a + (k * (b - a)) / 15));
      s.prog.push({ name: `(${a}..${b})`, values, derived: true });
    }
  }
  // 5. template ids: wiki list + gvg.report's PvP alias table (keeps newer 2026 splits)
  const mapFile = D("template_id_map.json");
  const map = readJson(mapFile, { pvp_to_template: {} });
  try {
    const js = await (await fetch("https://gvg.report/ui/skill-template.js", { headers: { "User-Agent": UA } })).text();
    for (const [, a, b] of js.matchAll(/\[(\d+),\s*(\d+)\]/g)) map.pvp_to_template[a] = +b;
    map.source = `gvg.report ui/skill-template.js + wiki (refreshed ${new Date().toISOString().slice(0, 10)})`;
    fs.writeFileSync(mapFile, JSON.stringify(map, null, 0) + "\n");
  } catch (e) { console.warn("Could not refresh template id map from gvg.report:", e.message); }
  for (const s of keep) s.template_id = map.pvp_to_template[s.id] ?? s.id;
  // 6. icons
  const bases = [...new Set(keep.map((s) => s.title.replace(/ \(PvP\)$/, "")))];
  const icons = {};
  for (let i = 0; i < bases.length; i += 50) {
    const d = await api({ action: "query", prop: "imageinfo", iiprop: "url", titles: bases.slice(i, i + 50).map((n) => `File:${n}.jpg`).join("|") });
    const norm = {}; (d.query.normalized || []).forEach((r) => (norm[r.to] = r.from));
    for (const p of d.query.pages) if (p.imageinfo) icons[(norm[p.title] || p.title).replace(/^File:/, "").replace(/\.jpg$/, "")] = p.imageinfo[0].url;
  }
  const old = readJson(D("skills.json"), { skills: [] }).skills;
  const oldIcons = Object.fromEntries(old.map((s) => [s.id, s.icon]));
  for (const s of keep) s.icon = icons[s.title.replace(/ \(PvP\)$/, "")] || oldIcons[s.id] || null;
  keep.sort((a, b) => a.id - b.id);
  // 7. sanity check before replacing anything
  if (keep.length < old.length * 0.9) throw new Error(`Only ${keep.length} skills parsed (had ${old.length}); keeping the existing file.`);
  // 8. change report
  const oldById = new Map(old.map((s) => [s.id, s]));
  const FIELDS = ["energy", "adrenaline", "sacrifice", "upkeep", "overcast", "activation", "recharge", "desc", "elite", "type", "attr"];
  const changes = [];
  for (const s of keep) {
    const o = oldById.get(s.id);
    if (!o) { changes.push({ id: s.id, name: s.name, kind: "added" }); continue; }
    const diffs = FIELDS.filter((k) => JSON.stringify(o[k]) !== JSON.stringify(s[k])).map((k) => ({ field: k, before: o[k], after: s[k] }));
    if (JSON.stringify(o.prog?.map((p) => p.values)) !== JSON.stringify(s.prog.map((p) => p.values))) diffs.push({ field: "progression", before: null, after: null });
    if (diffs.length) changes.push({ id: s.id, name: s.name, kind: "changed", diffs });
  }
  const keepIds = new Set(keep.map((s) => s.id));
  for (const o of old) if (!keepIds.has(o.id)) changes.push({ id: o.id, name: o.name, kind: "removed" });
  const now = new Date().toISOString();
  fs.writeFileSync(D("skills.json"), JSON.stringify({ schema: "gw-portal.skills.v1", source: `wiki.guildwars.com, pulled ${now.slice(0, 10)}`, count: keep.length, skills: keep }) + "\n");
  const log = readJson(D("wiki_changes.json"), { runs: [] });
  log.runs.unshift({ at: now, count: keep.length, changes });
  log.runs = log.runs.slice(0, 20);
  fs.writeFileSync(D("wiki_changes.json"), JSON.stringify(log) + "\n");
  console.log(`Wrote ${keep.length} skills; ${changes.length} changes since the last pull.`);
}

if (import.meta.url === `file://${process.argv[1]}`) syncWiki().catch((e) => { console.error(e); process.exit(1); });
