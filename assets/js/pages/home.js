import { state, esc, skillBar, parseCode, templateCode, copy, lazy, runWorkflow, codeForPlayer, ago, toast, saveToTemplates, canSave, ABBR } from "../core.js";

const fmtDur = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
const RESULT = { flawless_victory: "Flawless", victory: "Victory" };
let open = null;
// Search state: terms (each matched in one field or anywhere), combined with all/any, plus quick filters.
const F = { terms: [], mode: "all", occ: "", map: "", month: "", result: "", minLen: "", maxLen: "", limit: 60 };
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

export async function renderHome(view) {
  const [recent, changes] = await Promise.all([lazy("recent"), lazy("wiki_changes")]);
  const matches = recent?.matches || [];
  index ||= buildIndex(matches);
  const occs = [...new Set(matches.map((m) => m.occ))].sort();
  const maps = [...new Set(matches.map((m) => m.map).filter(Boolean))].sort();
  const months = [...new Set(matches.map((m) => (m.date || "").slice(0, 7)).filter(Boolean))].sort().reverse();
  const filtered = matches.filter((m) =>
    (!F.occ || m.occ === F.occ) && (!F.map || m.map === F.map) && (!F.month || (m.date || "").startsWith(F.month)) &&
    (!F.result || m.result === F.result) && (F.minLen === "" || (m.dur || 0) >= +F.minLen * 60) && (F.maxLen === "" || (m.dur || 0) <= +F.maxLen * 60) &&
    (!F.terms.length || (F.mode === "all" ? F.terms.every((t) => termHit(m, t)) : F.terms.some((t) => termHit(m, t)))));
  const shown = filtered.slice(0, F.limit);
  // suggestions for the search box
  const sugg = new Set();
  for (const m of matches.slice(0, 400)) for (const t of m.teams) { if (t.guild) sugg.add(t.guild); if (t.tag) sugg.add(`[${t.tag}]`); for (const p of t.players) { sugg.add(p.n); if (p.build) sugg.add(p.build); } }
  const opt = (v, cur, l = v) => `<option value="${esc(v)}"${v === cur ? " selected" : ""}>${esc(l)}</option>`;
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
    <div id="changes"></div>
    <div class="home-grid"><section>
    <form class="search" id="search">
      <div class="row">
        <select id="field" aria-label="Search in">${FIELDS.map(([v, l]) => opt(v, "any", l)).join("")}</select>
        <input type="search" id="q" list="sugg" placeholder="Search guild, tag, player, skill, build, map…" style="flex:1;min-width:16rem">
        <datalist id="sugg">${[...sugg].slice(0, 1500).map((x) => `<option value="${esc(x)}">`).join("")}${state.skills.map((s) => `<option value="${esc(s.name)}">`).join("")}</datalist>
        <button class="btn primary" type="submit">Add</button>
      </div>
      ${F.terms.length ? `<div class="chips">${F.terms.map((t, i) => `<span class="chip"><small>${esc(FIELDS.find(([v]) => v === t.field)[1])}</small> ${esc(t.q)} <button type="button" data-rm="${i}" aria-label="Remove">×</button></span>`).join("")}
        ${F.terms.length > 1 ? `<span class="seg"><button type="button" data-mode="all" aria-pressed="${F.mode === "all"}">Match all</button><button type="button" data-mode="any" aria-pressed="${F.mode === "any"}">Match any</button></span>` : ""}
        <button type="button" class="btn small ghost" id="clear">Clear</button></div>` : ""}
    </form>
    <div class="toolbar" id="filters">
      <label>Event<select name="occ">${opt("", F.occ, "All")}${occs.map((o) => opt(o, F.occ)).join("")}</select></label>
      <label>Map<select name="map">${opt("", F.map, "All")}${maps.map((o) => opt(o, F.map)).join("")}</select></label>
      <label>Month<select name="month">${opt("", F.month, "All")}${months.map((o) => opt(o, F.month)).join("")}</select></label>
      <label>Result<select name="result">${opt("", F.result, "Any")}${opt("flawless_victory", F.result, "Flawless")}${opt("victory", F.result, "Victory")}</select></label>
      <label>Length (min)<span class="row" style="gap:.3rem"><input type="number" name="minLen" min="0" max="60" value="${esc(F.minLen)}" placeholder="from" style="width:5rem"><input type="number" name="maxLen" min="0" max="60" value="${esc(F.maxLen)}" placeholder="to" style="width:5rem"></span></label>
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
    ${filtered.length > shown.length ? `<button class="btn" id="more" style="margin-top:1rem">Show ${Math.min(60, filtered.length - shown.length)} more</button>` : ""}
    </section><aside>
    <h3>Read a template code</h3>
    <form class="row" id="peek"><input type="text" name="code" placeholder="Paste any skill template code" style="flex:1;min-width:240px"><button class="btn" type="submit">Show bar</button></form>
    <div id="out" style="margin-top:14px"></div>
    </aside></div>`;

  const rerender = () => renderHome(view);
  view.querySelector("#search").onsubmit = (e) => {
    e.preventDefault();
    const q = view.querySelector("#q").value.trim(); if (!q) return;
    let field = view.querySelector("#field").value, text = q;
    if (field === "any" && /^\[.+\]$/.test(q)) field = "guild"; // "[tag]" searches guild tags
    if (field === "any" && state.skills.some((s) => s.name.toLowerCase() === q.toLowerCase())) field = "skill";
    F.terms.push({ field, q: text }); F.limit = 60; rerender();
  };
  view.querySelectorAll("[data-rm]").forEach((b) => b.onclick = () => { F.terms.splice(+b.dataset.rm, 1); rerender(); });
  view.querySelectorAll("[data-mode]").forEach((b) => b.onclick = () => { F.mode = b.dataset.mode; rerender(); });
  view.querySelector("#clear")?.addEventListener("click", () => { F.terms = []; rerender(); });
  view.querySelector("#filters").addEventListener("change", (e) => { F[e.target.name] = e.target.value; F.limit = 60; rerender(); });
  view.querySelector("#more")?.addEventListener("click", () => { F.limit += 60; rerender(); });
  view.querySelectorAll("tr[data-match]").forEach((tr) => {
    const toggle = () => { open = open === tr.dataset.match ? null : tr.dataset.match; rerender(); };
    tr.onclick = toggle; tr.onkeydown = (e) => { if (e.key === "Enter") toggle(); };
  });
  view.querySelectorAll("[data-copy]").forEach((b) => b.onclick = (e) => { e.stopPropagation(); copy(b.dataset.copy); });
  view.querySelectorAll("[data-save]").forEach((b) => b.onclick = async (e) => {
    e.stopPropagation();
    try { await saveToTemplates({ name: b.dataset.name, code: b.dataset.save }); } catch (err) { toast(err.message); }
  });

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

  view.querySelector("#peek").onsubmit = (e) => {
    e.preventDefault();
    const out = view.querySelector("#out");
    try {
      const t = parseCode(e.target.code.value);
      const code = templateCode(t);
      out.innerHTML = `<div class="meta" style="margin-bottom:8px"><span class="prof" data-p="${t.primary}">${t.primary}</span> / <span class="prof" data-p="${t.secondary}">${t.secondary}</span>
        <span class="attrs">${Object.entries(t.attributes).map(([a, r]) => `${esc(a)} ${r}`).join(", ")}</span></div>
        ${skillBar(t.skills, t)}
        <div class="row" style="margin-top:8px"><span class="code">${esc(code)}</span><button class="btn small primary" id="c">Copy code</button>
        <button class="btn small" id="s">Save to Templates</button></div>`;
      out.querySelector("#c").onclick = () => copy(code);
      out.querySelector("#s").onclick = async () => { const name = prompt("Name for this template?"); if (name) try { await saveToTemplates({ name, code }); } catch (err) { toast(err.message); } };
    } catch (err) {
      out.innerHTML = `<p class="note">${esc(err.message)}</p>`;
    }
  };
}

function lineups(m) {
  return `<div class="layout-lineups">${m.teams.map((t) => `
    <div><b>${t.guild ? `<a href="#/guilds/${encodeURIComponent(`${t.guild} ${t.tag || ""}`.toLowerCase().replace(/[^\p{L}\p{N}]+/gu, "-").replace(/^-|-$/g, ""))}">${esc(t.guild)}</a>` : "?"}</b> <span class="muted">[${esc(t.tag || "")}] rating ${t.rating ?? "?"}${t.won ? ", won" : ""}</span>
    ${t.players.map((p) => {
      const code = codeForPlayer(p);
      return `<div class="lineup-row"><span class="pos">${p.pos ?? "–"}</span><span class="prof" data-p="${esc(p.p)}">${esc(ABBR[p.p] || p.p)}/${esc(ABBR[p.s] || "")}</span><span class="pname" title="${esc(p.build || "")}">${esc(p.n)}</span>
        ${skillBar(p.bar, { attributes: p.attrs }, true)}
        ${code ? `<button class="btn small" data-copy="${esc(code)}">Copy</button><button class="btn small" data-save="${esc(code)}" data-name="${esc(p.n)} (${esc(m.date)})">Save</button>` : ""}
</div>`;
    }).join("")}</div>`).join("")}</div>`;
}
