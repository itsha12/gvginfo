import { esc, lazy, pct, ago, skillBar, templateCode, copy } from "../core.js";

const f = { q: "", sort: "games", desc: true, map: "" };
const COLS = [["name", "Guild"], ["rating", "Rating", 1], ["games", "Games", 1], ["win", "Won", 1], ["flawless", "Flawless", 1], ["avgDur", "Avg length", 1], ["last", "Last seen", 1]];
const fmtDur = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
const label = (g) => `${esc(g.name || "?")} <span class="muted">[${esc(g.tag || "")}]</span>`;

export async function renderGuilds(view, [id]) {
  const data = await lazy("guilds");
  if (!data?.guilds?.length) { view.innerHTML = `<h2>Guilds</h2><div class="empty-state">No match data yet. Press Update matches on the Recent matches page.</div>`; return; }
  const g = id && data.guilds.find((x) => x.id === id);
  if (g) return detail(view, g, data);

  const q = f.q.toLowerCase();
  const rows = data.guilds.filter((x) => !q || `${x.name} ${x.tag}`.toLowerCase().includes(q) || x.players.some((p) => p.n.toLowerCase().includes(q)))
    .map((x) => ({ ...x, win: x.wins / x.games }));
  rows.sort((a, b) => (f.sort === "name" ? String(a.name).localeCompare(String(b.name)) : (a[f.sort] ?? -1) - (b[f.sort] ?? -1)) * (f.desc ? -1 : 1));

  view.innerHTML = `
    <h2>Guilds</h2>
    <p class="lede">Every guild in the ${data.matches} recorded matches: record, maps, usual lineup per map in party order, and who plays for them.</p>
    <div class="toolbar"><label>Search<input type="search" id="q" value="${esc(f.q)}" placeholder="Guild, tag or player"></label></div>
    <div class="scroll"><table class="data"><thead><tr>${COLS.map(([k, l, n]) => `<th class="sortable${n ? " num" : ""}" data-sort="${k}" aria-sort="${f.sort === k ? (f.desc ? "descending" : "ascending") : "none"}">${l}<span class="arrow">${f.sort === k ? (f.desc ? "↓" : "↑") : ""}</span></th>`).join("")}<th>Most played maps</th></tr></thead>
    <tbody>${rows.map((x) => `<tr class="clickable" data-g="${esc(x.id)}" tabindex="0">
      <td>${label(x)}</td><td class="num">${x.rating ?? "–"}</td><td class="num">${x.games}</td><td class="num">${pct(x.wins, x.games)}</td>
      <td class="num">${x.flawless}</td><td class="num">${fmtDur(x.avgDur)}</td><td class="num">${esc(ago(x.last))}</td>
      <td>${x.maps.slice(0, 3).map((m) => `${esc(m.map.replace(/^Isle of (the )?|\s+Isle$/g, ""))} <span class="muted">${m.wins}–${m.n - m.wins}</span>`).join(", ")}</td></tr>`).join("")}</tbody></table></div>`;

  const q$ = view.querySelector("#q");
  q$.oninput = () => { f.q = q$.value; clearTimeout(f.t); f.t = setTimeout(() => renderGuilds(view, []).then(() => { const el = view.querySelector("#q"); el.focus(); el.setSelectionRange(el.value.length, el.value.length); }), 250); };
  view.querySelectorAll("[data-sort]").forEach((th) => th.onclick = () => { if (f.sort === th.dataset.sort) f.desc = !f.desc; else { f.sort = th.dataset.sort; f.desc = th.dataset.sort !== "name"; } renderGuilds(view, []); });
  view.querySelectorAll("tr[data-g]").forEach((tr) => { const go = () => { f.map = ""; location.hash = `#/guilds/${encodeURIComponent(tr.dataset.g)}`; }; tr.onclick = go; tr.onkeydown = (e) => e.key === "Enter" && go(); });
}

// One party slot: position, profession, build name, bar, usual players.
export function lineupRows(slots) {
  return `<div class="lineup">${slots.map((x) => {
    const code = templateCode({ primary: x.p, secondary: x.s, attributes: {}, skills: x.bar });
    return `<div class="lineup-slot">
      <span class="pos">${x.pos ?? "–"}</span>
      <div class="who"><span class="prof" data-p="${esc(x.p)}" title="${esc(x.p)}"></span> <b>${esc(x.build)}</b>
        <div class="muted small">${x.players.map((p) => `${esc(p.k)}${p.n > 1 ? ` (${p.n})` : ""}`).join(", ")}${x.of ? ` · ${x.copy > 1 ? `${x.copy} of these in` : "in"} ${x.n} of ${x.of} games` : ""}</div></div>
      ${skillBar(x.bar, null, true)}
      ${code ? `<button class="btn small" data-copy="${esc(code)}" title="Skills only; attributes aren't stored for lineups">Copy</button>` : ""}
    </div>`;
  }).join("")}</div>`;
}

function detail(view, g, data) {
  const map = g.maps.find((m) => m.map === f.map) || null;
  const L = map ? map.lineup : g.lineup;
  view.innerHTML = `
    <p><a href="#/guilds">← All guilds</a></p>
    <h2>${esc(g.name || "?")} <span class="muted" style="font-weight:400">[${esc(g.tag || "")}]</span></h2>
    <div class="stats" style="margin-bottom:2rem">
      <div><span>Rating</span><b>${g.rating ?? "–"}</b><span>latest recorded</span></div>
      <div><span>Record</span><b>${g.wins}–${g.games - g.wins}</b><span>${pct(g.wins, g.games)} won, ${g.flawless} flawless</span></div>
      <div><span>Average length</span><b>${fmtDur(g.avgDur)}</b><span>per match</span></div>
      <div><span>Events</span><b>${Object.entries(g.occ).map(([k, v]) => `${esc(k)} ${v.n}`).join(" · ")}</b><span>${Object.entries(g.occ).map(([k, v]) => `${esc(k)} ${pct(v.wins, v.n)} won`).join(", ")}</span></div>
      <div><span>Last seen</span><b>${esc(ago(g.last))}</b><span>of ${data.matches} recorded matches</span></div>
    </div>

    <div class="row" style="justify-content:space-between;align-items:end">
      <h3 style="margin:0">Usual lineup ${map ? `on ${esc(map.map)}` : "(all maps)"}</h3>
      <label class="eyebrow" style="display:grid;gap:.3rem">Map<select id="map"><option value="">All maps (${g.games})</option>
        ${g.maps.map((m) => `<option value="${esc(m.map)}"${m.map === f.map ? " selected" : ""}>${esc(m.map)} — ${m.wins}–${m.n - m.wins}</option>`).join("")}</select></label>
    </div>
    <p class="muted small" style="margin:.5rem 0 1rem">A lineup they actually played${L.from ? ` (vs ${esc(L.from.opp)}, ${esc(L.from.date)})` : ""}, chosen because it shares the most builds with their other games${map ? " on this map" : ""}. In party order as on gvg.report; each slot says how many of their games included that build.</p>
    ${lineupRows(L.slots)}
    ${L.comps.length ? `<h3>Most played full lineups${map ? " on this map" : ""}</h3>
    <div class="scroll"><table class="data"><thead><tr><th class="num">Games</th><th class="num">Won</th><th>Builds</th></tr></thead>
    <tbody>${L.comps.map((c) => `<tr><td class="num">${c.n}</td><td class="num">${c.wins}</td><td class="wrap">${c.builds.map(esc).join(" · ")}</td></tr>`).join("")}</tbody></table></div>` : ""}

    <h3>Maps</h3>
    <div class="scroll"><table class="data"><thead><tr><th>Map</th><th class="num">Games</th><th class="num">Won</th><th class="num">Lost</th><th class="num">Win rate</th></tr></thead>
    <tbody>${g.maps.map((m) => `<tr class="clickable" data-map="${esc(m.map)}"><td>${esc(m.map)}</td><td class="num">${m.n}</td><td class="num">${m.wins}</td><td class="num">${m.n - m.wins}</td><td class="num">${pct(m.wins, m.n)}</td></tr>`).join("")}</tbody></table></div>

    <h3>Builds they run</h3>
    <div class="scroll"><table class="data"><thead><tr><th>Build</th><th class="num">Times played</th></tr></thead>
    <tbody>${g.builds.map((b) => `<tr><td>${esc(b.k)}</td><td class="num">${b.n}</td></tr>`).join("")}</tbody></table></div>

    <h3>Players</h3>
    <div class="scroll"><table class="data"><thead><tr><th>Character</th><th class="num">Usual slot</th><th class="num">Games</th><th class="num">Won</th><th>Builds</th></tr></thead>
    <tbody>${g.players.map((p) => `<tr><td><b>${esc(p.n)}</b></td><td class="num">${p.pos ?? "–"}</td><td class="num">${p.games}</td><td class="num">${pct(p.wins, p.games)}</td>
      <td>${p.builds.map((b) => `${esc(b.k)}${b.n > 1 ? ` (${b.n})` : ""}`).join(", ")}</td></tr>`).join("")}</tbody></table></div>
    <p class="muted small">Character names, not accounts: one person may play several characters.</p>

    <h3>Recent matches</h3>
    <div class="scroll"><table class="data"><thead><tr><th>Date</th><th>Event</th><th>Map</th><th>Opponent</th><th>Result</th><th class="num">Length</th><th class="num">Rating</th></tr></thead>
    <tbody>${g.recent.map((m) => `<tr><td>${esc(m.date)}</td><td>${esc(m.occ)}</td><td>${esc(m.map)}</td><td>${esc(m.opp)} <span class="muted">[${esc(m.oppTag)}]</span></td>
      <td class="${m.won ? "up" : "down"}" style="font-size:inherit">${m.won ? (m.result === "flawless_victory" ? "Won (flawless)" : "Won") : "Lost"}</td><td class="num">${fmtDur(m.dur || 0)}</td><td class="num">${m.rating ?? ""}</td></tr>`).join("")}</tbody></table></div>`;

  view.querySelector("#map").onchange = (e) => { f.map = e.target.value; detail(view, g, data); };
  view.querySelectorAll("tr[data-map]").forEach((tr) => tr.onclick = () => { f.map = tr.dataset.map; detail(view, g, data); scrollTo({ top: 0, behavior: "smooth" }); });
  view.querySelectorAll("[data-copy]").forEach((b) => b.onclick = () => copy(b.dataset.copy));
}
