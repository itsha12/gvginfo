import { state, esc, skillBar, parseCode, templateCode, copy, lazy, runWorkflow, codeForPlayer, ago, toast, saveToTemplates, canSave, ABBR } from "../core.js";

const fmtDur = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
const RESULT = { flawless_victory: "Flawless", victory: "Victory" };
let open = null;
let occFilter = "";

export async function renderHome(view) {
  const [recent, changes] = await Promise.all([lazy("recent"), lazy("wiki_changes")]);
  const matches = recent?.matches || [];
  const occs = [...new Set(matches.map((m) => m.occ))].sort();
  const shown = matches.filter((m) => !occFilter || m.occ === occFilter).slice(0, 60);
  const lastWiki = changes?.runs?.[0];

  view.innerHTML = `
    <h2>Recent matches</h2>
    <p class="lede">${recent ? `${recent.total} matches stored, last updated ${ago(Date.parse(recent.updated))}.` : "No matches stored yet. Press Update matches to pull them from gvg.report."}
      ${lastWiki ? ` Skills last pulled from the wiki ${ago(Date.parse(lastWiki.at))}${lastWiki.changes.length ? `, with ${lastWiki.changes.length} changes` : ""}.` : ""}</p>
    <div class="row" style="margin-bottom:18px">
      <button class="btn primary" id="upd-matches">Update matches</button>
      <button class="btn" id="upd-wiki">Update skills from wiki</button>
      ${lastWiki?.changes.length ? `<a class="btn" href="#/home/changes">What changed on the wiki</a>` : ""}
      <span class="muted" id="upd-status"></span>
    </div>
    <div id="changes"></div>
    <div class="toolbar">
      <label>Event<select id="occ"><option value="">All</option>${occs.map((o) => `<option${o === occFilter ? " selected" : ""}>${esc(o)}</option>`).join("")}</select></label>
    </div>
    <div class="scroll"><table class="data">
      <thead><tr><th>Date</th><th>Event</th><th>Winner</th><th>Loser</th><th>Map</th><th class="num">Length</th><th></th></tr></thead>
      <tbody>${shown.map((m) => {
        const w = m.teams.find((t) => t.won) || m.teams[0], l = m.teams.find((t) => t !== w) || {};
        return `<tr class="clickable" data-match="${m.id}" tabindex="0">
          <td>${esc(m.date)}</td><td>${esc(m.occ)}</td>
          <td><b>${esc(w.guild || "?")}</b> <span class="muted">[${esc(w.tag || "")}]</span></td>
          <td>${esc(l.guild || "?")} <span class="muted">[${esc(l.tag || "")}]</span></td>
          <td>${esc(m.map || "")}</td><td class="num">${fmtDur(m.dur || 0)}</td><td>${esc(RESULT[m.result] || "")}</td></tr>
          ${open === m.id ? `<tr><td colspan="7">${lineups(m)}</td></tr>` : ""}`;
      }).join("")}</tbody></table></div>
    <h3>Read a template code</h3>
    <form class="row" id="peek"><input type="text" name="code" placeholder="Paste any skill template code" style="flex:1;min-width:240px"><button class="btn" type="submit">Show bar</button></form>
    <div id="out" style="margin-top:14px"></div>`;

  const rerender = () => renderHome(view);
  view.querySelector("#occ").onchange = (e) => { occFilter = e.target.value; rerender(); };
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
        <button class="btn small" id="s">Save to My templates</button></div>`;
      out.querySelector("#c").onclick = () => copy(code);
      out.querySelector("#s").onclick = async () => { const name = prompt("Name for this template?"); if (name) try { await saveToTemplates({ name, code }); } catch (err) { toast(err.message); } };
    } catch (err) {
      out.innerHTML = `<p class="note">${esc(err.message)}</p>`;
    }
  };
}

function lineups(m) {
  return `<div class="layout-lineups">${m.teams.map((t) => `
    <div><b>${esc(t.guild || "?")}</b> <span class="muted">[${esc(t.tag || "")}] rating ${t.rating ?? "?"}${t.won ? ", won" : ""}</span>
    ${t.players.map((p) => {
      const code = codeForPlayer(p);
      return `<div class="lineup-row"><span class="prof" data-p="${esc(p.p)}">${esc(ABBR[p.p] || p.p)}/${esc(ABBR[p.s] || "")}</span><span class="pname">${esc(p.n)}</span>
        ${skillBar(p.bar, { attributes: p.attrs }, true)}
        ${code ? `<button class="btn small" data-copy="${esc(code)}">Copy</button><button class="btn small" data-save="${esc(code)}" data-name="${esc(p.n)} (${esc(m.date)})">Save</button>` : ""}
        ${p.full ? "" : `<span class="muted" title="Some slots were never used, so they weren't observed">partial</span>`}</div>`;
    }).join("")}</div>`).join("")}</div>`;
}
