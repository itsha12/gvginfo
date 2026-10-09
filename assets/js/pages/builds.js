import { state, esc, skillBar, copy, lazy, pct, toast, saveToTemplates, skill, readJson } from "../core.js";

const PROFS = ["Warrior", "Ranger", "Monk", "Necromancer", "Mesmer", "Elementalist", "Assassin", "Ritualist", "Paragon", "Dervish"];
const f = { prof: "", q: "", month: "", min: 3, sort: "games", open: null, theme: new Set(), vars: new Set(), allVars: new Set() };
let gear = {};

export async function renderBuilds(view, [openId]) {
  if (openId) f.vars.add(openId);
  const [data, gearData] = await Promise.all([lazy("builds"), readJson("data/build_gear.json", {})]);
  gear = gearData || {};
  if (!data?.families?.length) {
    view.innerHTML = `<h2>Builds</h2><div class="empty-state">No match data yet. Press Update matches on the Home page.</div>`;
    return;
  }
  const months = [...new Set(data.families.flatMap((x) => Object.keys(x.months)))].sort().reverse();
  const count = (x) => (f.month ? x.months[f.month] || 0 : x.n);
  const q = f.q.toLowerCase();
  const matchQ = (fam) => !q || fam.name.toLowerCase().includes(q) ||
    fam.variations.some((v) => v.bar.some((id) => skill(id)?.name.toLowerCase().includes(q))) ||
    fam.players.some((p) => p.k.toLowerCase().includes(q));
  let list = data.families.filter((x) => (!f.prof || x.p === f.prof) && count(x) >= f.min && matchQ(x));
  list.sort(f.sort === "win" ? (a, b) => b.wins / b.n - a.wins / a.n : f.sort === "recent" ? (a, b) => b.last - a.last : (a, b) => count(b) - count(a));
  const totalBars = data.families.reduce((a, x) => a + count(x), 0);

  view.innerHTML = `
    <h2>Builds</h2>
    <p class="lede">Every bar seen in ${data.matches} recorded matches, grouped into families: ${esc(data.rule)}. Variations list each exact bar with its own code.</p>
    <div class="toolbar" id="filters">
      <label>Profession<select name="prof"><option value="">All</option>${PROFS.map((p) => `<option${p === f.prof ? " selected" : ""}>${p}</option>`).join("")}</select></label>
      <label>Search<input type="search" name="q" value="${esc(f.q)}" placeholder="Skill, elite or player"></label>
      <label>Month<select name="month"><option value="">All time</option>${months.map((m) => `<option${m === f.month ? " selected" : ""}>${m}</option>`).join("")}</select></label>
      <label>At least<select name="min">${[1, 3, 5, 10, 25].map((n) => `<option value="${n}"${n === f.min ? " selected" : ""}>${n} games</option>`).join("")}</select></label>
      <label>Sort by<select name="sort">${[["games", "Most played"], ["win", "Win rate"], ["recent", "Most recent"]].map(([v, l]) => `<option value="${v}"${v === f.sort ? " selected" : ""}>${l}</option>`).join("")}</select></label>
    </div>
    <p class="muted">${list.length} families.</p>
    ${list.slice(0, 80).map((x) => family(x, count(x), totalBars)).join("") || `<div class="empty-state">No builds match these filters.</div>`}`;

  view.querySelector("#filters").addEventListener("change", (e) => {
    const { name, value } = e.target; f[name] = name === "min" ? +value : value; renderBuilds(view, []);
  });
  view.querySelector("#filters [name=q]").addEventListener("input", (e) => { f.q = e.target.value; clearTimeout(f.t); f.t = setTimeout(() => { renderBuilds(view, []).then(() => { const el = view.querySelector("#filters [name=q]"); el.focus(); el.setSelectionRange(el.value.length, el.value.length); }); }, 250); });
  view.querySelectorAll("[data-toggle]").forEach((b) => b.onclick = () => {
    const set = f[b.dataset.toggle], id = b.dataset.id;
    set.has(id) ? set.delete(id) : set.add(id);
    const y = b.getBoundingClientRect().top;
    renderBuilds(view, []).then(() => { const el = view.querySelector(`[data-toggle="${b.dataset.toggle}"][data-id="${CSS.escape(id)}"]`); if (el) scrollBy(0, el.getBoundingClientRect().top - y); });
  });
  view.querySelectorAll("[data-copy]").forEach((b) => b.onclick = () => copy(b.dataset.copy));
  view.querySelectorAll("[data-save]").forEach((b) => b.onclick = async () => {
    try { await saveToTemplates({ name: b.dataset.name, code: b.dataset.save, bonus: JSON.parse(b.dataset.bonus || "{}") }); } catch (e) { toast(e.message); }
  });
}

function family(x, n, total) {
  const main = x.variations[0];
  const showTheme = f.theme.has(x.id), showVars = f.vars.has(x.id);
  const t = x.theme;
  const more = x.variations.length - 1;
  return `<div class="tpl">
    <div class="row" style="justify-content:space-between">
      <h4>${esc(x.name)}</h4>
      <span class="muted">${n} games${f.month ? ` in ${f.month}` : ""} (${pct(n, total)} of bars), ${pct(x.wins, x.n)} won${x.partial ? `, ${x.partial} with unobserved slots` : ""}</span>
    </div>
    ${skillBar(main.bar, { attributes: main.attributes, bonus: main.bonus })}
    ${varRow(main, x)}
    <div class="row" style="margin-top:10px">
      ${t ? `<button class="btn small${showTheme ? " primary" : ""}" data-toggle="theme" data-id="${esc(x.id)}">${showTheme ? "Hide" : "Show"} theme</button>` : ""}
      <button class="btn small${showVars ? " primary" : ""}" data-toggle="vars" data-id="${esc(x.id)}">${showVars ? "Hide" : "Show"} variations${more ? ` (${more} more)` : ""}</button>
    </div>
    ${showTheme && t ? themeHtml(x) : ""}
    ${showVars ? `<div class="variant">
      <p class="meta" style="margin:0 0 .6rem">Played by ${x.players.slice(0, 5).map((p) => `${esc(p.k)} (${p.n})`).join(", ")}. Guilds: ${x.guilds.slice(0, 5).map((g) => `${esc(g.k)} (${g.n})`).join(", ")}.</p>
      ${x.variations.slice(1, f.allVars.has(x.id) ? undefined : 16).map((v) => `<div style="margin-bottom:1rem">${skillBar(v.bar, { attributes: v.attributes, bonus: v.bonus })}${varRow(v, x)}</div>`).join("") || `<p class="muted">Only one exact bar seen so far.</p>`}
      ${more > 15 ? `<button class="btn small" data-toggle="allVars" data-id="${esc(x.id)}">${f.allVars.has(x.id) ? "Show the 15 most played" : `Show all ${more}`}</button>` : ""}
    </div>` : ""}
  </div>`;
}

// Core skills (on 70%+ of this family's bars) with open slots, then optional skills by how often they're taken.
function themeHtml(x) {
  const t = x.theme;
  return `<div class="theme">
    <p class="meta" style="margin:0 0 .5rem">Core of ${esc(x.name)} from ${t.bars} bars: skills on at least 70% of them, then ${t.open} open slot${t.open === 1 ? "" : "s"}.</p>
    ${skillBar(t.core)}
    ${t.optional.length ? `<p class="meta" style="margin:.9rem 0 .4rem">Optional skills for the open slots (share of bars that take them):</p>
    <div class="optionals">${t.optional.map((o) => { const s = skill(o.id); return s ? `<span class="opt"><img class="sicon" src="${esc(s.icon)}" alt="${esc(s.name)}" data-skill="${s.id}" tabindex="0"><small>${o.pct}%</small></span>` : ""; }).join("")}</div>` : ""}
  </div>`;
}

// Runes and insignias: ones Henry gave (data/build_gear.json, by code or family) replace runes derived from bonus ranks.
export function gearFor(v, familyId, given = gear) {
  const g = { ...(given.families?.[familyId] || {}), ...(given.codes?.[v.code] || {}) };
  return { runes: g.runes?.length ? g.runes : (v.runes || []), insignias: g.insignias || [], given: !!(g.runes?.length || g.insignias?.length) };
}
export function attrGearLine(v, familyId) {
  const attrs = Object.entries(v.attributes || {}).map(([a, r]) => `<b>${esc(a)} ${r}${v.bonus?.[a] ? `+${v.bonus[a]}` : ""}</b>`).join(", ");
  const g = gearFor(v, familyId);
  const parts = [attrs || `<span class="muted">Attributes not observed</span>`];
  if (g.runes.length) parts.push(esc(g.runes.join(", ")));
  if (g.insignias.length) parts.push(`Insignias: ${esc(g.insignias.join(", "))}`);
  return `<span class="gear">${parts.join(" · ")}</span>`;
}

function varRow(v, x) {
  return `<div class="row" style="margin-top:6px">
    ${attrGearLine(v, x.id)}
    <span class="code">${esc(v.code)}</span>
    <button class="btn small primary" data-copy="${esc(v.code)}">Copy code</button>
    <button class="btn small" data-save="${esc(v.code)}" data-name="${esc(x.name)}" data-bonus='${esc(JSON.stringify(v.bonus))}'>Save</button>
  </div>`;
}
