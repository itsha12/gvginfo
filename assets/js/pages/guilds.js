import { esc, lazy, pct, ago, skillBar, templateCode, copy, readJson, ABBR } from "../core.js";
import { matchList, newFilters, guildSlug, charLink, personLink } from "./home.js";

const f = { q: "", sort: "games", desc: true, map: "", minGames: "", minRating: "" };
const lists = new Map(); // match search state per guild
const COLS = [["name", "Guild"], ["rating", "Rating", 1], ["games", "Games", 1], ["win", "Won", 1], ["flawless", "Flawless", 1], ["last", "Last seen", 1]];
const label = (g) => `${esc(g.name || "?")} <span class="muted">[${esc(g.tag || "")}]</span>`;

export async function renderGuilds(view, [id]) {
  const data = await lazy("guilds");
  if (!data?.guilds?.length) { view.innerHTML = `<h2>Guilds</h2><div class="empty-state">No match data yet. Press Update matches on the Recent matches page.</div>`; return; }
  const g = id && data.guilds.find((x) => x.id === id);
  if (g) return detail(view, g, data, await lazy("recent"), ((await readJson("data/aliases.json", { people: {} })) || {}).people || {});

  const q = f.q.toLowerCase();
  const rows = data.guilds.filter((x) => (!q || `${x.name} ${x.tag}`.toLowerCase().includes(q) || x.players.some((p) => p.n.toLowerCase().includes(q))) &&
    (f.minGames === "" || x.games >= +f.minGames) && (f.minRating === "" || (x.rating ?? -1) >= +f.minRating))
    .map((x) => ({ ...x, win: x.wins / x.games }));
  rows.sort((a, b) => (f.sort === "name" ? String(a.name).localeCompare(String(b.name)) : (a[f.sort] ?? -1) - (b[f.sort] ?? -1)) * (f.desc ? -1 : 1));

  view.innerHTML = `
    <h2>Guilds</h2>
    <div class="toolbar"><label>Search<input type="search" id="q" value="${esc(f.q)}" placeholder="Guild, tag or player"></label>
      <label>At least (games)<input type="number" id="minGames" min="0" value="${esc(f.minGames)}" placeholder="any" style="width:7rem"></label>
      <label>Rating at least<input type="number" id="minRating" min="0" step="10" value="${esc(f.minRating)}" placeholder="any" style="width:7rem"></label>
      <span class="muted small" style="align-self:center">${rows.length} of ${data.guilds.length} guilds</span></div>
    <div class="scroll"><table class="data"><thead><tr>${COLS.map(([k, l, n]) => `<th class="sortable${n ? " num" : ""}" data-sort="${k}" aria-sort="${f.sort === k ? (f.desc ? "descending" : "ascending") : "none"}">${l}<span class="arrow">${f.sort === k ? (f.desc ? "↓" : "↑") : ""}</span></th>`).join("")}</tr></thead>
    <tbody>${rows.map((x) => `<tr class="clickable" data-g="${esc(x.id)}" tabindex="0">
      <td>${label(x)}</td><td class="num">${x.rating ?? "–"}</td><td class="num">${x.games}</td><td class="num">${pct(x.wins, x.games)}</td>
      <td class="num">${x.flawless}</td><td class="num">${esc(ago(x.last))}</td></tr>`).join("")}</tbody></table></div>`;

  const q$ = view.querySelector("#q");
  q$.oninput = () => { f.q = q$.value; clearTimeout(f.t); f.t = setTimeout(() => renderGuilds(view, []).then(() => { const el = view.querySelector("#q"); el.focus(); el.setSelectionRange(el.value.length, el.value.length); }), 250); };
  ["minGames", "minRating"].forEach((k) => view.querySelector(`#${k}`).onchange = (e) => { f[k] = e.target.value; renderGuilds(view, []); });
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
        <div class="muted small">${x.players.map((p) => `${charLink(p.k)}${p.n > 1 ? ` (${p.n})` : ""}`).join(", ")}${x.of ? ` · ${x.copy > 1 ? `${x.copy} of these in` : "in"} ${x.n} of ${x.of} games` : ""}</div></div>
      ${skillBar(x.bar, null, true)}
      ${code ? `<button class="btn small" data-copy="${esc(code)}" title="Skills only; attributes aren't stored for lineups">Copy</button>` : ""}
    </div>`;
  }).join("")}</div>`;
}

function detail(view, g, data, recent, people) {
  const map = g.maps.find((m) => m.map === f.map) || null;
  const L = map ? map.lineup : g.lineup;
  const all = recent?.matches || [];
  const games = all.filter((m) => m.teams.some((t) => guildSlug(t) === g.id));
  const ours = (m) => m.teams.find((t) => guildSlug(t) === g.id);
  const occ = (pred) => Object.entries(g.occ).filter(([k]) => pred(k)).reduce((a, [, v]) => ({ n: a.n + v.n, wins: a.wins + v.wins }), { n: 0, wins: 0 });
  const at = occ((k) => /^AT-/.test(k)), mat = occ((k) => k === "MAT");
  const tile = (label, x) => `<div><span>${label}</span><b>${x.n ? pct(x.wins, x.n) : "–"}</b><span>${x.n ? `${x.wins}–${x.n - x.wins} in ${x.n} games` : "no games"}</span></div>`;

  // most played full lineups (same set of builds, 7 or 8 players seen), each shown as the latest game they played it
  const sig = (t) => t.players.map((p) => p.build).sort().join(" | ");
  const comps = new Map();
  for (const m of games) {
    if (map && m.map !== map.map) continue;
    const t = ours(m); if (t.players.length < 7) continue;
    const c = comps.get(sig(t)) || comps.set(sig(t), { n: 0, wins: 0, last: null }).get(sig(t));
    c.n++; c.wins += t.won ? 1 : 0; if (!c.last || (m.at || 0) > (c.last.m.at || 0)) c.last = { m, t };
  }
  const topComps = [...comps.values()].sort((a, b) => b.n - a.n || (b.last.m.at || 0) - (a.last.m.at || 0)).slice(0, 4);

  // players: characters grouped into the people they belong to (data/aliases.json); unassigned characters stand alone
  const personOf = new Map(Object.entries(people).flatMap(([p, chars]) => chars.map((c) => [c, p])));
  const P = new Map();
  for (const c of g.players) {
    const who = personOf.get(c.n), k = who ? `p:${who}` : `c:${c.n}`;
    const x = P.get(k) || P.set(k, { who, chars: [], games: 0, wins: 0, pos: c.pos, top: 0, builds: new Map() }).get(k);
    x.chars.push(c); x.games += c.games; x.wins += c.wins;
    if (c.games > x.top) { x.top = c.games; x.pos = c.pos; }
    for (const b of c.builds) x.builds.set(b.k, (x.builds.get(b.k) || 0) + b.n);
  }
  const players = [...P.values()].sort((a, b) => b.games - a.games);

  view.innerHTML = `
    <p><a href="#/guilds">← All guilds</a></p>
    <h2>${esc(g.name || "?")} <span class="muted" style="font-weight:400">[${esc(g.tag || "")}]</span></h2>
    <div class="stats" style="margin-bottom:1rem">
      <div><span>Rating</span><b>${g.rating ?? "–"}</b><span>latest recorded</span></div>
      <div><span>Record</span><b>${g.wins}–${g.games - g.wins}</b><span>${pct(g.wins, g.games)} won, ${g.flawless} flawless</span></div>
      ${tile("AT win rate", at)}
      ${tile("MAT win rate", mat)}
      <div><span>Last seen</span><b>${esc(ago(g.last))}</b><span>of ${data.matches} recorded matches</span></div>
    </div>

    <h3>Recent matches</h3>
    <div id="list"></div>

    <div class="row" style="justify-content:space-between;align-items:end;margin-top:2.6rem">
      <h3 style="margin:0">Usual lineup ${map ? `on ${esc(map.map)}` : "(all maps)"}</h3>
      <label class="eyebrow" style="display:grid;gap:.3rem">Map<select id="map"><option value="">All maps (${g.games})</option>
        ${g.maps.map((m) => `<option value="${esc(m.map)}"${m.map === f.map ? " selected" : ""}>${esc(m.map)} — ${m.wins}–${m.n - m.wins}</option>`).join("")}</select></label>
    </div>
    <p class="muted small" style="margin:.5rem 0 1rem">A lineup they actually played${L.from ? ` (vs ${esc(L.from.opp)}, ${esc(L.from.date)})` : ""}, chosen because it shares the most builds with their other games${map ? " on this map" : ""}.</p>
    ${lineupRows(L.slots)}
    ${topComps.length ? `<h3>Most played full lineups${map ? " on this map" : ""}</h3>
    <div class="comps">${topComps.map((c) => `<div class="comp">
      <div class="comp-head"><b>${c.n} game${c.n === 1 ? "" : "s"}, ${c.wins} won</b> <span class="muted small">shown as played ${esc(c.last.m.date)} vs ${esc(c.last.m.teams.find((t) => t !== c.last.t)?.guild || "?")} on ${esc(c.last.m.map)}</span></div>
      ${[...c.last.t.players].sort((a, b) => (a.pos ?? 9) - (b.pos ?? 9)).map((p) => `<div class="lineup-row"><span class="pos">${p.pos ?? "–"}</span><span class="prof" data-p="${esc(p.p)}">${esc(ABBR[p.p] || p.p)}/${esc(ABBR[p.s] || "")}</span><span class="pname" title="${esc(p.build || "")}">${esc(p.build || "?")}</span>${skillBar(p.bar, { attributes: p.attrs }, true)}</div>`).join("")}
    </div>`).join("")}</div>` : ""}

    <h3>Players</h3>
    <div class="scroll"><table class="data"><thead><tr><th>Player</th><th>Characters</th><th class="num">Usual slot</th><th class="num">Games</th><th class="num">Won</th><th>Builds</th></tr></thead>
    <tbody>${players.map((x) => `<tr><td><b>${x.who ? personLink(x.who) : charLink(x.chars[0].n)}</b></td>
      <td class="wrap">${x.who ? x.chars.map((c) => charLink(c.n)).join(", ") : `<span class="muted small">not assigned to a player</span>`}</td>
      <td class="num">${x.pos ?? "–"}</td><td class="num">${x.games}</td><td class="num">${pct(x.wins, x.games)}</td>
      <td>${[...x.builds.entries()].sort((a, b) => b[1] - a[1]).slice(0, 3).map(([k, n]) => `${esc(k)}${n > 1 ? ` (${n})` : ""}`).join(", ")}</td></tr>`).join("")}</tbody></table></div>`;

  if (!lists.has(g.id)) lists.set(g.id, newFilters(20));
  matchList(view.querySelector("#list"), games, lists.get(g.id), { allMatches: all });
  view.querySelector("#map").onchange = (e) => { f.map = e.target.value; detail(view, g, data, recent, people); };
  view.querySelectorAll(".lineup [data-copy]").forEach((b) => b.onclick = () => copy(b.dataset.copy));
}
