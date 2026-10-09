import { esc, lazy, pct, skill } from "../core.js";

let month = "";

export async function renderMeta(view) {
  const [meta, builds] = await Promise.all([lazy("meta"), lazy("builds")]);
  const months = Object.keys(meta?.months || {}).sort().reverse();
  if (!months.length) { view.innerHTML = `<h2>Meta</h2><div class="empty-state">No match data yet. Press Update matches on the Recent matches page.</div>`; return; }
  if (!months.includes(month)) month = months[0];
  const m = meta.months[month];
  const prev = meta.months[months[months.indexOf(month) + 1]];
  const elites = Object.entries(m.elites).map(([id, x]) => ({ s: skill(id), ...x, prevShare: prev?.elites[id] ? prev.elites[id].n / prev.teams : 0 }))
    .filter((x) => x.s).sort((a, b) => b.n - a.n);
  const fams = (builds?.families || []).filter((x) => x.months[month]).sort((a, b) => b.months[month] - a.months[month]).slice(0, 15);
  const delta = (now, before) => { if (!prev) return ""; const d = Math.round(100 * (now - before)); return d ? ` <span class="${d > 0 ? "up" : "down"}">${d > 0 ? "+" : ""}${d}</span>` : ""; };

  view.innerHTML = `
    <h2>Meta</h2>
    <p class="lede">${m.matches} matches and ${m.teams} team lineups in ${month}${Object.keys(m.flux).length ? `. Flux: ${Object.keys(m.flux).map(esc).join(", ").replace(/_/g, " ")}` : ""}.${prev ? " Changes are in percentage points versus the month before." : ""}</p>
    <div class="toolbar"><label>Month<select id="month">${months.map((x) => `<option${x === month ? " selected" : ""}>${x}</option>`).join("")}</select></label></div>
    <div class="meta-grid">
      <section><h3>Elites by share of teams</h3>
        <div class="scroll"><table class="data"><thead><tr><th></th><th>Elite</th><th class="num">Teams</th><th class="num">Won</th></tr></thead>
        <tbody>${elites.slice(0, 30).map((x) => `<tr><td><img class="sicon" src="${esc(x.s.icon)}" alt="" data-skill="${x.s.id}"></td><td><a href="#/skills/${x.s.id}">${esc(x.s.name)}</a></td>
          <td class="num">${pct(x.n, m.teams)}${delta(x.n / m.teams, x.prevShare)}</td><td class="num">${pct(x.wins, x.n)}</td></tr>`).join("")}</tbody></table></div>
      </section>
      <section><h3>Most played builds</h3>
        <div class="scroll"><table class="data"><thead><tr><th>Build</th><th class="num">Games</th><th class="num">Won (all time)</th></tr></thead>
        <tbody>${fams.map((x) => `<tr><td><a href="#/builds/${encodeURIComponent(x.id)}">${esc(x.name)}</a></td><td class="num">${x.months[month]}</td><td class="num">${pct(x.wins, x.n)}</td></tr>`).join("")}</tbody></table></div>
      </section>
    </div>`;
  view.querySelector("#month").onchange = (e) => { month = e.target.value; renderMeta(view); };
}
