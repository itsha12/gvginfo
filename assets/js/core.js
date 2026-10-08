// Shared state, data loading, GitHub storage and skill rendering.
import { encode, decode, PROF_ATTRS } from "./template.js";

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

export function costsHtml(s) {
  const c = [];
  if (s.energy) c.push(`<span class="e" title="Energy">${esc(s.energy)} energy</span>`);
  if (s.adrenaline) c.push(`<span class="a" title="Adrenaline">${esc(s.adrenaline)} adrenaline</span>`);
  if (s.sacrifice) c.push(`<span class="s" title="Sacrifice">${esc(s.sacrifice)}${/%/.test(s.sacrifice) ? "" : "%"} HP</span>`);
  if (s.upkeep) c.push(`<span class="u" title="Upkeep">upkeep</span>`);
  if (s.overcast) c.push(`<span class="o" title="Overcast">${esc(s.overcast)} overcast</span>`);
  if (s.activation) c.push(`<span class="c" title="Activation">${esc(s.activation)}s cast</span>`);
  if (s.recharge) c.push(`<span class="r" title="Recharge">${esc(s.recharge)}s recharge</span>`);
  return `<div class="costs">${c.join("")}</div>`;
}

export function skillCard(s, rank) {
  const mine = (state.notes[s.id] || []).map((n) => `<p class="note mine">${esc(n)}</p>`).join("");
  return `<div class="card-head"><img src="${esc(s.icon)}" alt="">
    <div><b>${esc(s.name)}</b><span class="muted">${s.elite ? "Elite " : ""}${esc(s.type)} · ${esc(s.attr)}${rank != null ? ` ${rank}` : ""}</span></div></div>
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
  return `<div class="skillbar${compact ? " compact" : ""}">${slots.join("")}</div>`;
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
