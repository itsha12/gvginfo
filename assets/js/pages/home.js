import { state, esc, skillBar, copy, lazy, runWorkflow, codeForPlayer, ago, toast, saveToTemplates, canSave, ABBR } from "../core.js";

const fmtDur = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
const RESULT = { flawless_victory: "Flawless", victory: "Victory" };
let open = null;
// Search state: terms (each matched in one field or anywhere), combined with all/any, plus quick filters.
export const newFilters = (page = 60) => ({ terms: [], mode: "all", occ: "", map: "", month: "", from: "", to: "", result: "", minLen: "", maxLen: "", limit: page, page });
const F = newFilters();
const FIELDS = [["any", "Anything"], ["guild", "Guild or tag"], ["player", "Player"], ["skill", "Skill"], ["build", "Build"], ["prof", "Profession"], ["map", "Map"]];
const norm = (x) => String(x ?? "").toLowerCase();
let index = null; // per match: searchable text by field

function buildIndex(matches) {
  return new Map(matches.map((m) => {
    const ps = m.teams.flatMap((t) => t.players.map((p) => ({ ...p, team: t })));
    const f = {
      guild: m.teams.map((t) => `${norm(t.guild)} [${norm(t.tag)}] ${norm(t.tag)}`).join(" | "),
      player: ps.map((p) => norm(p.n)).join(" | "),
      skill: ps.flatMap((p) => p.bar.filter(Boolean).map((id) => norm(state.byId.get(id)?.name || state.byTemplateId.get(id)?.name))).join(" | "),
      build: ps.map((p) => norm(p.build)).join(" | "),
      prof: ps.map((p) => `${norm(p.p)}/${norm(p.s)} ${norm(ABBR[p.p])}/${norm(ABBR[p.s])}`).join(" | "),
      map: norm(m.map),
    };
    f.any = Object.values(f).join(" | ") + " | " + norm(m.occ) + " | " + norm(m.date);
    return [m.id, f];
  }));
}
// does a term match within one team's side? (so "guild + skill" can mean that guild ran that skill)
const termHit = (m, t) => (index.get(m.id)[t.field] || "").includes(norm(t.q));

export const guildSlug = (t) => `${t.guild || "?"} ${t.tag || ""}`.toLowerCase().replace(/[^\p{L}\p{N}]+/gu, "-").replace(/^-|-$/g, "");
export const charLink = (n) => `<a href="#/character/${encodeURIComponent(n)}">${esc(n)}</a>`;
export const personLink = (n) => `<a href="#/player/${encodeURIComponent(n)}">${esc(n)}</a>`;

export async function renderHome(view) {
  const [recent, changes, sync] = await Promise.all([lazy("recent"), lazy("wiki_changes"), lazy("sync_status")]);
  const matches = recent?.matches || [];
  const lastWiki = changes?.runs?.[0];

  view.innerHTML = `
    <h2>Recent matches</h2>
    <p class="lede">${recent ? `${recent.total} matches stored, last updated ${ago(Date.parse(recent.updated))}.` : "No matches stored yet. Press Update matches to pull them from gvg.report."}
      ${lastWiki ? ` Skills last pulled from the wiki ${ago(Date.parse(lastWiki.at))}${lastWiki.changes.length ? `, with ${lastWiki.changes.length} changes` : ""}.` : ""}</p>
    <div class="row" style="margin-bottom:18px">
      <button class="btn primary" id="upd-matches">Update matches</button>
      <button class="btn" id="upd-wiki">Update skills from wiki</button>
      ${lastWiki?.changes.length ? `<a class="btn" href="#/matches/changes">What changed on the wiki</a>` : ""}
      <span class="muted" id="upd-status"></span>
    </div>
    ${sync?.message ? `<p class="callout">Last update ${esc(ago(Date.parse(sync.at)))}: ${esc(sync.message)}</p>` : ""}
    <div id="changes"></div>
    <div id="list"></div>`;

  matchList(view.querySelector("#list"), matches, F);

  const status = view.querySelector("#upd-status");
  const start = async (file, label, inputs) => {
    try {
      const url = await runWorkflow(file, inputs);
      status.innerHTML = `${label} started. It runs on GitHub and the site refreshes about a minute after it finishes. <a href="${url}" target="_blank" rel="noopener">Watch progress</a>`;
    } catch (e) { status.textContent = e.message; }
  };
  view.querySelector("#upd-matches").onclick = () => start("update-matches.yml", "Match update", { max_matches: "400" });
  view.querySelector("#upd-wiki").onclick = () => {
    if (confirm("Pull the latest skill data from the wiki? Your own skill notes are kept.")) start("update-wiki.yml", "Wiki update");
  };
  if (!canSave()) status.textContent = "Add your GitHub key in Settings to use the update buttons.";

  if (location.hash.endsWith("/changes") && lastWiki) {
    view.querySelector("#changes").innerHTML = `<div class="detail"><b>Changes in the last wiki pull (${esc(lastWiki.at.slice(0, 10))})</b>
      <ul>${lastWiki.changes.slice(0, 200).map((c) => `<li><a href="#/skills/${c.id}">${esc(c.name)}</a>: ${c.kind === "changed" ? c.diffs.map((d) => d.field === "progression" ? "numbers changed" : `${esc(d.field)} ${esc(d.before ?? "–")} → ${esc(d.after ?? "–")}`).join("; ") : esc(c.kind)}</li>`).join("")}</ul></div>`;
  }
}

// The search, filters and match table, drawn into `host` for any set of matches (all of them, one guild's, one
// player's). `F` holds that list's search state so it survives redraws; `opts.allMatches` builds the search index.
export function matchList(host, matches, F, opts = {}) {
  index ||= buildIndex(opts.allMatches || matches);
  if (matches.some((m) => !index.has(m.id))) index = buildIndex(opts.allMatches || matches);
  const occs = [...new Set(matches.map((m) => m.occ))].sort();
  const maps = [...new Set(matches.map((m) => m.map).filter(Boolean))].sort();
  const months = [...new Set(matches.map((m) => (m.date || "").slice(0, 7)).filter(Boolean))].sort().reverse();
  const dates = matches.map((m) => m.date).filter(Boolean).sort();
  const filtered = matches.filter((m) =>
    (!F.occ || m.occ === F.occ) && (!F.map || m.map === F.map) && (!F.month || (m.date || "").startsWith(F.month)) &&
    (!F.from || (m.date || "") >= F.from) && (!F.to || (m.date || "") <= F.to) &&
    (!F.result || m.result === F.result) && (F.minLen === "" || (m.dur || 0) >= +F.minLen * 60) && (F.maxLen === "" || (m.dur || 0) <= +F.maxLen * 60) &&
    (!F.terms.length || (F.mode === "all" ? F.terms.every((t) => termHit(m, t)) : F.terms.some((t) => termHit(m, t)))));
  const shown = filtered.slice(0, F.limit);
  // suggestions for the search box
  const sugg = new Set();
  for (const m of matches.slice(0, 400)) for (const t of m.teams) { if (t.guild) sugg.add(t.guild); if (t.tag) sugg.add(`[${t.tag}]`); for (const p of t.players) { sugg.add(p.n); if (p.build) sugg.add(p.build); } }
  const opt = (v, cur, l = v) => `<option value="${esc(v)}"${v === cur ? " selected" : ""}>${esc(l)}</option>`;
  const dl = `sugg-${Math.random().toString(36).slice(2, 8)}`;

  host.innerHTML = `
    <form class="search">
      <div class="row">
        <select name="field" aria-label="Search in">${FIELDS.map(([v, l]) => opt(v, "any", l)).join("")}</select>
        <input type="search" name="q" list="${dl}" placeholder="Search guild, tag, player, skill, build, map…" style="flex:1;min-width:16rem">
        <datalist id="${dl}">${[...sugg].slice(0, 1500).map((x) => `<option value="${esc(x)}">`).join("")}${state.skills.map((s) => `<option value="${esc(s.name)}">`).join("")}</datalist>
        <button class="btn primary" type="submit">Add</button>
      </div>
      ${F.terms.length ? `<div class="chips">${F.terms.map((t, i) => `<span class="chip"><small>${esc(FIELDS.find(([v]) => v === t.field)[1])}</small> ${esc(t.q)} <button type="button" data-rm="${i}" aria-label="Remove">×</button></span>`).join("")}
        ${F.terms.length > 1 ? `<span class="seg"><button type="button" data-mode="all" aria-pressed="${F.mode === "all"}">Match all</button><button type="button" data-mode="any" aria-pressed="${F.mode === "any"}">Match any</button></span>` : ""}
        <button type="button" class="btn small ghost" data-clear>Clear</button></div>` : ""}
    </form>
    <div class="toolbar filters">
      <label>Event<select name="occ">${opt("", F.occ, "All")}${occs.map((o) => opt(o, F.occ)).join("")}</select></label>
      <label>Map<select name="map">${opt("", F.map, "All")}${maps.map((o) => opt(o, F.map)).join("")}</select></label>
      <label>Month<select name="month">${opt("", F.month, "All")}${months.map((o) => opt(o, F.month)).join("")}</select></label>
      <label>Dates<span class="row" style="gap:.3rem"><input type="date" name="from" value="${esc(F.from)}" min="${esc(dates[0] || "")}" max="${esc(dates.at(-1) || "")}" aria-label="From date"><span class="muted">to</span><input type="date" name="to" value="${esc(F.to)}" min="${esc(dates[0] || "")}" max="${esc(dates.at(-1) || "")}" aria-label="To date"></span></label>
      <label>Result<select name="result">${opt("", F.result, "Any")}${opt("flawless_victory", F.result, "Flawless")}${opt("victory", F.result, "Victory")}</select></label>
      <label>Length (min)<span class="row" style="gap:.3rem"><input type="number" name="minLen" min="0" max="60" value="${esc(F.minLen)}" placeholder="from" style="width:5rem"><input type="number" name="maxLen" min="0" max="60" value="${esc(F.maxLen)}" placeholder="to" style="width:5rem"></span></label>
      ${F.from || F.to ? `<button type="button" class="btn small ghost" data-nodates>Clear dates</button>` : ""}
    </div>
    <p class="muted small">${filtered.length} of ${matches.length} matches${filtered.length > shown.length ? `, showing ${shown.length}` : ""}.</p>
    <div class="scroll"><table class="data">
      <thead><tr><th>Date</th><th>Event</th><th>Winner</th><th>Loser</th><th>Map</th><th class="num">Length</th><th></th></tr></thead>
      <tbody>${shown.map((m) => {
        const w = m.teams.find((t) => t.won) || m.teams[0], l = m.teams.find((t) => t !== w) || {};
        return `<tr class="clickable" data-match="${m.id}" tabindex="0">
          <td>${esc(m.date)}</td><td>${esc(m.occ)}</td>
          <td><b>${esc(w.guild || "?")}</b> <span class="muted">[${esc(w.tag || "")}]</span></td>
          <td>${esc(l.guild || "?")} <span class="muted">[${esc(l.tag || "")}]</span></td>
          <td>${esc(m.map || "")}</td><td class="num">${fmtDur(m.dur || 0)}</td><td>${esc(RESULT[m.result] || "")}</td></tr>
          ${open === m.id ? `<tr><td colspan="7" class="wrap">${lineups(m)}</td></tr>` : ""}`;
      }).join("")}</tbody></table></div>
    ${filtered.length > shown.length ? `<button class="btn" data-more style="margin-top:1rem">Show ${Math.min(F.page || 60, filtered.length - shown.length)} more</button>` : ""}`;

  const rerender = () => matchList(host, matches, F, opts);
  const form = host.querySelector("form.search");
  form.onsubmit = (e) => {
    e.preventDefault();
    const q = form.q.value.trim(); if (!q) return;
    let field = form.field.value;
    if (field === "any" && /^\[.+\]$/.test(q)) field = "guild"; // "[tag]" searches guild tags
    if (field === "any" && state.skills.some((s) => s.name.toLowerCase() === q.toLowerCase())) field = "skill";
    F.terms.push({ field, q }); F.limit = F.page || 60; rerender();
  };
  host.querySelectorAll("[data-rm]").forEach((b) => b.onclick = () => { F.terms.splice(+b.dataset.rm, 1); rerender(); });
  host.querySelectorAll("[data-mode]").forEach((b) => b.onclick = () => { F.mode = b.dataset.mode; rerender(); });
  host.querySelector("[data-clear]")?.addEventListener("click", () => { F.terms = []; rerender(); });
  host.querySelector("[data-nodates]")?.addEventListener("click", () => { F.from = F.to = ""; rerender(); });
  host.querySelector(".filters").addEventListener("change", (e) => {
    F[e.target.name] = e.target.value;
    if (e.target.name === "month" && e.target.value) F.from = F.to = ""; // a month and a date range don't mix
    if ((e.target.name === "from" || e.target.name === "to") && e.target.value) F.month = "";
    F.limit = F.page || 60; rerender();
  });
  host.querySelector("[data-more]")?.addEventListener("click", () => { F.limit += F.page || 60; rerender(); });
  host.querySelectorAll("tr[data-match]").forEach((tr) => {
    const toggle = () => { open = open === tr.dataset.match ? null : tr.dataset.match; rerender(); };
    tr.onclick = toggle; tr.onkeydown = (e) => { if (e.key === "Enter") toggle(); };
  });
  host.querySelectorAll("[data-copy]").forEach((b) => b.onclick = (e) => { e.stopPropagation(); copy(b.dataset.copy); });
  host.querySelectorAll("[data-save]").forEach((b) => b.onclick = async (e) => {
    e.stopPropagation();
    try { await saveToTemplates({ name: b.dataset.name, code: b.dataset.save }); } catch (err) { toast(err.message); }
  });
}

export function lineups(m) {
  return `<div class="layout-lineups">${m.teams.map((t) => `
    <div><b>${t.guild ? `<a href="#/guilds/${encodeURIComponent(guildSlug(t))}">${esc(t.guild)}</a>` : "?"}</b> <span class="muted">[${esc(t.tag || "")}] rating ${t.rating ?? "?"}${t.won ? ", won" : ""}</span>
    ${t.players.map((p) => {
      const code = codeForPlayer(p);
      return `<div class="lineup-row"><span class="pos">${p.pos ?? "–"}</span><span class="prof" data-p="${esc(p.p)}">${esc(ABBR[p.p] || p.p)}/${esc(ABBR[p.s] || "")}</span><span class="pname" title="${esc(p.build || "")}">${charLink(p.n)}</span>
        ${skillBar(p.bar, { attributes: p.attrs }, true)}
        ${code ? `<button class="btn small" data-copy="${esc(code)}">Copy</button>` : ""}
</div>`;
    }).join("")}</div>`).join("")}</div>`;
}
