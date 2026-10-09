// Shared state, data loading, GitHub storage and skill rendering.
import { encode, decode, decodeEquipment, PROF_ATTRS } from "./template.js";

export const state = {
  skills: [], byId: new Map(), byTemplateId: new Map(), pvpToTemplate: {},
  notes: {},              // user notes: { skillId: ["note", ...] } from data/skill_notes.json
  templates: { folders: [] },
  knowledge: [],
};

// ---------- settings (stored only in this browser) ----------
const SETTINGS_KEY = "gvginfo.settings";
export function settings() {
  try { return JSON.parse(localStorage.getItem(SETTINGS_KEY)) || {}; } catch { return {}; }
}
export function saveSettings(s) {
  try { localStorage.setItem(SETTINGS_KEY, JSON.stringify(s)); } catch { /* storage blocked */ }
}
export const canSave = () => { const s = settings(); return !!(s.token && s.owner && s.repo); };

// ---------- GitHub contents API ----------
const shas = {};
function gh(path, opts = {}) {
  const s = settings();
  return fetch(`https://api.github.com/repos/${s.owner}/${s.repo}/contents/${path}?ref=${s.branch || "main"}`, {
    ...opts,
    headers: { Authorization: `Bearer ${s.token}`, Accept: "application/vnd.github+json", ...(opts.headers || {}) },
  });
}
const b64encode = (str) => btoa(String.fromCharCode(...new TextEncoder().encode(str)));
const b64decode = (b64) => new TextDecoder().decode(Uint8Array.from(atob(b64.replace(/\n/g, "")), (c) => c.charCodeAt(0)));

// Read a JSON file: freshest copy from GitHub when a key is set, otherwise the published copy.
export async function readJson(path, fallback) {
  if (canSave()) {
    try {
      const r = await gh(path);
      if (r.ok) { const j = await r.json(); shas[path] = j.sha; return JSON.parse(b64decode(j.content)); }
      if (r.status === 404) return fallback;
    } catch { /* fall through to published copy */ }
  }
  try { const r = await fetch(path, { cache: "no-cache" }); if (r.ok) return await r.json(); } catch { /* missing */ }
  return fallback;
}

export async function writeJson(path, data, message) {
  if (!canSave()) throw new Error("Add your GitHub key in Settings to save changes.");
  if (!shas[path]) { const r = await gh(path); if (r.ok) shas[path] = (await r.json()).sha; }
  const body = { message, content: b64encode(JSON.stringify(data, null, 1) + "\n"), branch: settings().branch || "main" };
  if (shas[path]) body.sha = shas[path];
  const r = await gh(path, { method: "PUT", body: JSON.stringify(body), headers: { "Content-Type": "application/json" } });
  if (!r.ok) {
    const e = await r.json().catch(() => ({}));
    throw new Error(r.status === 409 ? "The file changed on GitHub since this page loaded. Reload and try again." : `GitHub refused the save (${r.status}): ${e.message || "unknown error"}`);
  }
  shas[path] = (await r.json()).content.sha;
}

// ---------- data ----------
export async function loadData() {
  const [sk, map, notes, tpl, kn] = await Promise.all([
    fetch("data/skills.json").then((r) => r.json()),
    fetch("data/template_id_map.json").then((r) => r.json()),
    readJson("data/skill_notes.json", {}),
    readJson("data/templates.json", { folders: [] }),
    fetch("knowledge/index.json").then((r) => r.json()).catch(() => []),
  ]);
  state.skills = sk.skills;
  state.pvpToTemplate = map.pvp_to_template;
  for (const s of state.skills) {
    state.byId.set(s.id, s);
    const existing = state.byTemplateId.get(s.template_id);
    if (!existing || s.pvp_version) state.byTemplateId.set(s.template_id, s);
  }
  state.notes = notes || {};
  state.templates = tpl && tpl.folders ? tpl : { folders: [] };
  state.knowledge = kn;
  state.meta = { source: sk.source, count: sk.count };
}

// Match-derived files load on first use; they change only when "Update matches" runs.
const cache = {};
export function lazy(name) {
  return (cache[name] ||= fetch(`data/${name}.json`, { cache: "no-cache" }).then((r) => (r.ok ? r.json() : null)).catch(() => null));
}

// Start one of the update workflows on GitHub (needs a key with Actions: Read and write).
export async function runWorkflow(file, inputs = {}) {
  const s = settings();
  if (!canSave()) throw new Error("Add your GitHub key in Settings to run updates.");
  const r = await fetch(`https://api.github.com/repos/${s.owner}/${s.repo}/actions/workflows/${file}/dispatches`, {
    method: "POST",
    headers: { Authorization: `Bearer ${s.token}`, Accept: "application/vnd.github+json", "Content-Type": "application/json" },
    body: JSON.stringify({ ref: s.branch || "main", inputs }),
  });
  if (r.status !== 204) {
    const e = await r.json().catch(() => ({}));
    throw new Error(r.status === 403 || r.status === 404 ? "Your key can't start updates. Give it Actions: Read and write in its GitHub settings." : `GitHub refused (${r.status}): ${e.message || "unknown error"}`);
  }
  return `https://github.com/${s.owner}/${s.repo}/actions`;
}

// Template code for an observed player bar (attributes are effective ranks; codes hold base ranks ≤ 12).
export function codeForPlayer(p) {
  const attributes = {};
  for (const [a, r] of Object.entries(p.attrs || {})) attributes[a] = Math.min(12, r);
  return templateCode({ primary: p.p, secondary: p.s, attributes, skills: p.bar });
}
export const pct = (a, b) => (b ? Math.round((100 * a) / b) + "%" : "–");
export const ABBR = { Warrior: "W", Ranger: "R", Monk: "Mo", Necromancer: "N", Mesmer: "Me", Elementalist: "E", Assassin: "A", Ritualist: "Rt", Paragon: "P", Dervish: "D", None: "X" };
export const ago = (ms) => {
  if (!ms) return "";
  const m = Math.round((Date.now() - ms) / 60000);
  return m < 60 ? `${m} min ago` : m < 1440 ? `${Math.round(m / 60)} h ago` : `${Math.round(m / 1440)} day${Math.round(m / 1440) === 1 ? "" : "s"} ago`;
};

// Add a bar to a Templates folder (used by Builds and match views).
export async function saveToTemplates({ name, code, notes = "", bonus = {} }) {
  const folders = state.templates.folders;
  const names = folders.map((f, i) => `${i + 1}. ${f.name}`).join("\n");
  const pick = prompt(`Save "${name}" to which folder? Type a number, or a new folder name.\n${names}`, folders.length ? "1" : "Saved from builds");
  if (!pick) return;
  let folder = folders[+pick - 1];
  if (!folder) { folder = { id: Math.random().toString(36).slice(2, 10), name: pick.trim(), templates: [] }; folders.push(folder); }
  const equipment = [];
  const eq = prompt(`Equipment template for "${name}"? Paste the code from the game's Equipment tab, or leave empty to add it later.`, "");
  if (eq && eq.trim()) {
    try { decodeEquipment(eq.trim()); equipment.push({ name: "Main set", code: eq.trim(), notes: "" }); } catch (e) { toast(e.message); return; }
  }
  folder.templates.push({ id: Math.random().toString(36).slice(2, 10), name, code, notes, bonus, equipment, variations: [] });
  await writeJson("data/templates.json", state.templates, `Saved template: ${name}`);
  toast(`Saved to ${folder.name}`);
}

// skill lookup by in-game id or template id (template ids resolve to the PvP version)
export const skill = (id) => state.byTemplateId.get(+id) || state.byId.get(+id) || null;

export const templateCode = (t) => encode(t, state.pvpToTemplate);
export const parseCode = (code) => {
  const d = decode(code);
  d.skills = d.skills.map((id) => (id ? (skill(id)?.id ?? id) : 0)); // show PvP versions
  return d;
};

// effective rank of an attribute in a template: base + bonus (rune/headgear)
export function rankFor(t, attr) {
  if (!t || !attr) return null;
  const base = +(t.attributes?.[attr] || 0), bonus = +(t.bonus?.[attr] || 0);
  return base + bonus;
}
export const attrsFor = (p, s) => [...(PROF_ATTRS[p] || []), ...((PROF_ATTRS[s] || []).slice(1))];

// ---------- rendering ----------
export const esc = (x) => String(x ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

// Description with "a..b" ranges replaced by the value at `rank` (or kept as a range when rank is null).
export function descAt(s, rank) {
  const text = esc(s.desc.replace(new RegExp("^(Elite )?" + s.type.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "\\.\\s*", "i"), ""));
  return text.replace(/([+-]?)(\d+(?:\.\d+)?)\.\.(\d+(?:\.\d+)?)(%?)/g, (m, sign, a, b, pct) => {
    if (rank == null) return `<span class="v">${sign}${a}…${b}${pct}</span>`;
    const p = s.prog.find((x) => +x.values[0] === +a && +x.values[15] === +b);
    const v = p ? p.values[Math.min(rank, p.values.length - 1)] : Math.round(+a + rank * (b - a) / 15);
    return `<span class="v">${sign}${v}${pct}</span>`;
  });
}

// Small icons for skill facts (energy orb, adrenaline, sacrifice drop, upkeep, overcast, cast clock, recharge arrow).
const ICON = {
  e: `<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.5" fill="currentColor"/><circle cx="6" cy="5.8" r="1.8" fill="#fff" opacity=".55"/></svg>`,
  a: `<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 1.5 14 8l-6 6.5L2 8z" fill="currentColor"/></svg>`,
  s: `<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 1.5c2.6 3.4 4.6 6 4.6 8.3a4.6 4.6 0 0 1-9.2 0C3.4 7.5 5.4 4.9 8 1.5z" fill="currentColor"/></svg>`,
  u: `<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M4.8 8h6.4" stroke="currentColor" stroke-width="2"/></svg>`,
  o: `<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="3 2"/></svg>`,
  c: `<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.3" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M8 4.2V8l2.6 1.6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>`,
  r: `<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M13 8a5 5 0 1 1-1.6-3.7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><path d="M12.6 1.6v3.3H9.3" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
};
export const fact = (k, v, label, unit = "") =>
  v === "" || v == null ? "" : `<span class="fact ${k}" title="${label}">${ICON[k]}${esc(v)}${/^[\d¼½¾.]+$/.test(v) ? unit : ""}<small>${label}</small></span>`;

export function costsHtml(s) {
  return `<div class="facts">${[
    fact("e", s.energy, "Energy"),
    fact("a", s.adrenaline, "Adrenaline"),
    s.sacrifice ? fact("s", `${s.sacrifice}${/%/.test(s.sacrifice) ? "" : "%"}`, "Sacrifice") : "",
    s.upkeep ? fact("u", "−1", "Upkeep") : "",
    fact("o", s.overcast, "Overcast"),
    fact("c", s.activation, "Cast", "s"),
    fact("r", s.recharge, "Recharge", "s"),
  ].join("")}</div>`;
}

// Profession that owns an attribute (for colouring the attribute pill).
const ATTR_PROF = Object.fromEntries(Object.entries(PROF_ATTRS).flatMap(([p, list]) => list.map((a) => [a, p])));
export const typePill = (s) => `${s.elite ? `<span class="pill elite">Elite</span>` : ""}<span class="pill type">${esc(s.type)}</span>`;
export const attrPill = (attr) => attr && !/^no attribute$/i.test(attr) && attr !== "None"
  ? `<span class="pill attr" data-p="${esc(ATTR_PROF[attr] || "")}">${esc(attr)}</span>` : "";

// The attribute rank is shown by the highlighted numbers, not written beside the attribute name.
export function skillCard(s, rank) {
  const mine = (state.notes[s.id] || []).map((n) => `<p class="note mine">${esc(n)}</p>`).join("");
  return `<div class="card-head"><img src="${esc(s.icon)}" alt="">
    <div><b>${esc(s.name)}</b><div class="pills">${typePill(s)}${attrPill(s.attr)}</div></div></div>
    ${costsHtml(s)}<p class="desc">${descAt(s, rank)}</p>${mine}`;
}

// Skill bar: 8 framed icons. `t` (template) supplies attribute ranks for tooltips.
export function skillBar(ids, t, compact = false) {
  const slots = [...ids, 0, 0, 0, 0, 0, 0, 0, 0].slice(0, 8).map((id) => {
    const s = id ? skill(id) : null;
    if (!s) return `<span class="slot empty" aria-label="Empty slot"></span>`;
    return `<button class="slot${s.elite ? " elite" : ""}" data-skill="${s.id}" data-rank="${rankFor(t, s.attr) ?? ""}" aria-label="${esc(s.name)}">
      <img src="${esc(s.icon)}" alt="" loading="lazy"></button>`;
  });
  const size = compact === true ? " compact" : compact ? ` ${compact}` : "";
  return `<div class="skillbar${size}">${slots.join("")}</div>`;
}

// One shared tooltip for every [data-skill] element on the page.
let tipEl;
export function installTooltips() {
  tipEl = document.createElement("div");
  tipEl.className = "tip"; tipEl.hidden = true; tipEl.setAttribute("role", "tooltip");
  document.body.append(tipEl);
  const show = (el, x, y) => {
    const s = skill(el.dataset.skill); if (!s) return;
    const r = el.dataset.rank === "" || el.dataset.rank == null ? null : +el.dataset.rank;
    tipEl.innerHTML = skillCard(s, r); tipEl.hidden = false;
    const w = tipEl.offsetWidth, h = tipEl.offsetHeight;
    tipEl.style.left = Math.min(x + 14, innerWidth - w - 10) + "px";
    tipEl.style.top = (y + h + 20 > innerHeight ? Math.max(8, y - h - 14) : y + 18) + "px";
  };
  document.addEventListener("mouseover", (e) => { const el = e.target.closest("[data-skill]"); if (el) show(el, e.clientX, e.clientY); });
  document.addEventListener("mousemove", (e) => { if (!tipEl.hidden && e.target.closest("[data-skill]")) show(e.target.closest("[data-skill]"), e.clientX, e.clientY); });
  document.addEventListener("mouseout", (e) => { if (e.target.closest("[data-skill]")) tipEl.hidden = true; });
  document.addEventListener("focusin", (e) => { const el = e.target.closest("[data-skill]"); if (el) { const b = el.getBoundingClientRect(); show(el, b.left, b.bottom); } });
  document.addEventListener("focusout", () => { tipEl.hidden = true; });
}

export function toast(msg) {
  const t = document.createElement("div");
  t.className = "toast"; t.setAttribute("role", "status"); t.textContent = msg;
  document.body.append(t); setTimeout(() => t.remove(), 3200);
}

export async function copy(text, what = "Template code") {
  try { await navigator.clipboard.writeText(text); toast(`${what} copied`); }
  catch { prompt("Copy this:", text); }
}
