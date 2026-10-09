import { state, esc, skillBar, copy, lazy, pct, toast, saveToTemplates, skill, readJson } from "../core.js";

const PROFS = ["Warrior", "Ranger", "Monk", "Necromancer", "Mesmer", "Elementalist", "Assassin", "Ritualist", "Paragon", "Dervish"];
const f = { prof: "", q: "", month: "", min: 3, sort: "games", open: null, theme: new Set(), vars: new Set(), allVars: new Set() };
let gear = {};

export async function renderBuilds(view, [openId]) {
  if (openId) f.vars.add(openId);
  const [data, gearData] = await Promise.all([lazy("builds"), readJson("data/build_gear.json", {})]);
  gear = gearData || {};
  if (!data?.families?.length) {
    view.innerHTML = `<h2>Builds</h2><div class="empty-state">No match data yet. Press Update matches on the Recent matches page.</div>`;
    return;
  }
  const months = [...new Set(data.families.flatMap((x) => Object.keys(x.months)))].sort().reverse();
  const count = (x) => (f.month ? x.months[f.month] || 0 : x.n);
  const q = f.q.toLowerCase();
  const matchQ = (fam) => !q || fam.name.toLowerCase().includes(q) ||
    fam.variations.some((v) => v.bar.some((id) => skill(id)?.name.toLowerCase().includes(q))) ||
    fam.players.some((p) => p.k.toLowerCase().includes(q));
  const matching = data.families.filter((x) => count(x) >= f.min && matchQ(x));
  const sorter = f.sort === "win" ? (a, b) => b.wins / b.n - a.wins / a.n : f.sort === "recent" ? (a, b) => b.last - a.last : (a, b) => count(b) - count(a);
  const list = matching.filter((x) => !f.prof || x.p === f.prof).sort(sorter);
  const totalBars = data.families.reduce((a, x) => a + count(x), 0);
  const perProf = Object.fromEntries(PROFS.map((p) => [p, matching.filter((x) => x.p === p).length]));
  const PER_GROUP = 6;
  // All tab: grouped by profession, the top few of each; a profession tab: that profession's families
  const body = f.prof
    ? list.slice(0, 80).map((x) => family(x, count(x), totalBars)).join("") || `<div class="empty-state">No builds match these filters.</div>`
    : PROFS.filter((p) => perProf[p]).map((p) => {
      const fams = list.filter((x) => x.p === p);
      return `<section class="prof-group"><div class="row" style="justify-content:space-between;align-items:baseline">
          <h3><span class="prof" data-p="${p}">${p}</span></h3>
          ${fams.length > PER_GROUP ? `<button class="btn small ghost" data-tab="${p}">All ${fams.length} ${p} builds →</button>` : ""}</div>
        ${fams.slice(0, PER_GROUP).map((x) => family(x, count(x), totalBars)).join("")}</section>`;
    }).join("") || `<div class="empty-state">No builds match these filters.</div>`;

  view.innerHTML = `
    <h2>Builds</h2>
    <p class="lede">Every bar seen in ${data.matches} recorded matches, grouped into families: ${esc(data.rule)}. Variations list each exact bar with its own code.</p>
    <div class="tabs" role="tablist">
      <button role="tab" data-tab="" aria-selected="${!f.prof}">All <span class="muted">${matching.length}</span></button>
      ${PROFS.map((p) => `<button role="tab" data-tab="${p}" aria-selected="${f.prof === p}"${perProf[p] ? "" : " disabled"}><span class="prof" data-p="${p}">${p}</span> <span class="muted">${perProf[p]}</span></button>`).join("")}
    </div>
    <div class="toolbar" id="filters">
      <label>Search<input type="search" name="q" value="${esc(f.q)}" placeholder="Skill, elite or player"></label>
      <label>Month<select name="month"><option value="">All time</option>${months.map((m) => `<option${m === f.month ? " selected" : ""}>${m}</option>`).join("")}</select></label>
      <label>At least<select name="min">${[1, 3, 5, 10, 25].map((n) => `<option value="${n}"${n === f.min ? " selected" : ""}>${n} games</option>`).join("")}</select></label>
      <label>Sort by<select name="sort">${[["games", "Most played"], ["win", "Win rate"], ["recent", "Most recent"]].map(([v, l]) => `<option value="${v}"${v === f.sort ? " selected" : ""}>${l}</option>`).join("")}</select></label>
    </div>
    ${f.prof ? `<p class="muted small">${list.length} ${esc(f.prof)} families${list.length > 80 ? ", showing the first 80" : ""}.</p>` : ""}
    ${body}`;
  view.querySelectorAll("[data-tab]").forEach((b) => b.onclick = () => { f.prof = b.dataset.tab; renderBuilds(view, []).then(() => scrollTo({ top: 0 })); });

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
  return `<div class="fam">
    <div class="fam-head"><h4>${esc(x.name)}</h4>
      <span class="muted small">${n} games${f.month ? ` in ${f.month}` : ""} · ${pct(n, total)} of bars · ${pct(x.wins, x.n)} won</span></div>
    <div class="fam-row">
      ${skillBar(main.bar, { attributes: main.attributes, bonus: main.bonus }, "mid")}
      <div class="fam-info">${attrGearLine(main, x.id)}
        <div class="row">${codeButtons(main, x)}
          ${t ? `<button class="btn small${showTheme ? " primary" : ""}" data-toggle="theme" data-id="${esc(x.id)}">${showTheme ? "Hide" : "Show"} theme</button>` : ""}
          <button class="btn small${showVars ? " primary" : ""}" data-toggle="vars" data-id="${esc(x.id)}">${showVars ? "Hide" : "Show"} variations${more ? ` (${more})` : ""}</button>
        </div></div>
    </div>
    ${showTheme && t ? themeHtml(x) : ""}
    ${showVars ? `<div class="variant">
      <p class="meta" style="margin:0 0 .6rem">Played by ${x.players.slice(0, 5).map((p) => `${esc(p.k)} (${p.n})`).join(", ")}. Guilds: ${x.guilds.slice(0, 5).map((g) => `${esc(g.k)} (${g.n})`).join(", ")}.</p>
      ${x.variations.slice(1, f.allVars.has(x.id) ? undefined : 16).map((v) => `<div class="fam-row var-row">${skillBar(v.bar, { attributes: v.attributes, bonus: v.bonus }, "mid")}
        <div class="fam-info">${attrGearLine(v, x.id)}<div class="row">${codeButtons(v, x)}</div></div></div>`).join("") || `<p class="muted">Only one exact bar seen so far.</p>`}
      ${more > 15 ? `<button class="btn small" data-toggle="allVars" data-id="${esc(x.id)}">${f.allVars.has(x.id) ? "Show the 15 most played" : `Show all ${more}`}</button>` : ""}
    </div>` : ""}
  </div>`;
}

// Core skills (on 70%+ of this family's bars) with open slots, then optional skills by how often they're taken.
function themeHtml(x) {
  const t = x.theme;
  return `<div class="theme">
    <p class="meta" style="margin:0 0 .5rem">Core of ${esc(x.name)} from ${t.bars} bars: skills on at least 70% of them, then ${t.open} open slot${t.open === 1 ? "" : "s"}.</p>
    ${skillBar(t.core, null, "mid")}
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

function codeButtons(v, x) {
  return `<span class="code">${esc(v.code)}</span>
    <button class="btn small primary" data-copy="${esc(v.code)}">Copy</button>
    <button class="btn small" data-save="${esc(v.code)}" data-name="${esc(x.name)}" data-bonus='${esc(JSON.stringify(v.bonus))}'>Save</button>`;
}
