// Profiles: a player (#/player/<person>, every character assigned to him in data/aliases.json) and a character
// (#/character/<name>, one in-game name). Built from data/recent.json, which holds every stored match with full bars.
import { esc, lazy, readJson, pct, ago, skillBar, copy, codeForPlayer, ABBR } from "../core.js";
import { matchList, newFilters, guildSlug, charLink, personLink } from "./home.js";

const lists = new Map(); // search state per profile, kept while the site is open

const people = async () => ((await readJson("data/aliases.json", { people: {} })) || {}).people || {};
const isAT = (occ) => /^AT-/.test(occ || "");
const rate = (rows) => rows.length ? `${pct(rows.filter((r) => r.t.won).length, rows.length)}` : "–";
const rec = (rows) => `${rows.filter((r) => r.t.won).length}–${rows.filter((r) => !r.t.won).length}`;

export async function renderPerson(view, [name = ""]) {
  const [recent, P] = await Promise.all([lazy("recent"), people()]);
  const chars = P[name];
  if (!chars) {
    view.innerHTML = `<p><a href="#/players">← Players</a></p><h2>${esc(name)}</h2><div class="empty-state">No player of this name. Players are made on the Players page by assigning characters to a name.</div>`;
    return;
  }
  draw(view, recent, { title: name, key: `p:${name}`, chars: new Set(chars), person: name });
}

export async function renderCharacter(view, [name = ""]) {
  const [recent, P] = await Promise.all([lazy("recent"), people()]);
  const person = Object.entries(P).find(([, list]) => list.includes(name))?.[0];
  draw(view, recent, { title: name, key: `c:${name}`, chars: new Set([name]), playedBy: person });
}

function draw(view, recent, o) {
  const all = recent?.matches || [];
  const rows = [];
  for (const m of all) for (const t of m.teams) for (const p of t.players) if (o.chars.has(p.n)) rows.push({ m, t, p });
  const matches = [...new Map(rows.map((r) => [r.m.id, r.m])).values()];
  const back = `<p><a href="#/players">← Players</a></p>`;
  const sub = o.person
    ? `<p class="lede">Characters: ${[...o.chars].sort((a, b) => a.localeCompare(b)).map(charLink).join(", ")}</p>`
    : o.playedBy ? `<p class="lede">Played by ${personLink(o.playedBy)}</p>` : "";
  if (!rows.length) {
    view.innerHTML = `${back}<h2>${esc(o.title)}</h2>${sub}<div class="empty-state">No recorded matches.</div>`;
    return;
  }
  const at = rows.filter((r) => isAT(r.m.occ)), mat = rows.filter((r) => r.m.occ === "MAT");
  const last = Math.max(...rows.map((r) => r.m.at || 0));

  // guilds played for
  const guilds = group(rows, (r) => guildSlug(r.t), (r) => ({ name: r.t.guild, tag: r.t.tag }));
  // builds played: one row per build family, its most played full bar shown
  const builds = group(rows, (r) => r.p.fam || r.p.build || "?", (r) => ({ build: r.p.build || "Unknown build" })).map((b) => {
    const full = b.rows.filter((r) => r.p.bar.every(Boolean));
    const counts = new Map(); for (const r of (full.length ? full : b.rows)) { const k = r.p.bar.join(","); counts.set(k, (counts.get(k) || 0) + 1); }
    const top = [...counts.entries()].sort((x, y) => y[1] - x[1])[0][0];
    const pick = b.rows.find((r) => r.p.bar.join(",") === top);
    return { ...b, pick: pick.p };
  });
  // a player's characters
  const perChar = o.person ? group(rows, (r) => r.p.n, (r) => ({ name: r.p.n })) : [];

  view.innerHTML = `${back}
    <h2>${esc(o.title)}</h2>${sub}
    <div class="stats" style="margin-bottom:1rem">
      <div><span>Record</span><b>${rec(rows)}</b><span>${rate(rows)} won, ${rows.length} games</span></div>
      <div><span>AT win rate</span><b>${rate(at)}</b><span>${at.length ? `${rec(at)} in ${at.length} games` : "no AT games"}</span></div>
      <div><span>MAT win rate</span><b>${rate(mat)}</b><span>${mat.length ? `${rec(mat)} in ${mat.length} games` : "no MAT games"}</span></div>
      <div><span>Last seen</span><b>${esc(ago(last))}</b><span>${esc(new Date(last).toISOString().slice(0, 10))}</span></div>
    </div>

    <h3>Recent matches</h3>
    <div id="list"></div>

    <h3>Builds played</h3>
    <div class="lineup">${builds.map((b) => {
      const code = codeForPlayer(b.pick);
      return `<div class="lineup-slot">
        <span class="prof" data-p="${esc(b.pick.p)}">${esc(ABBR[b.pick.p] || b.pick.p)}/${esc(ABBR[b.pick.s] || "")}</span>
        <div class="who"><b>${esc(b.pick.build || b.build)}</b><div class="muted small">${b.n} game${b.n === 1 ? "" : "s"}, ${pct(b.wins, b.n)} won</div></div>
        ${skillBar(b.pick.bar, { attributes: b.pick.attrs }, true)}
        ${code ? `<button class="btn small" data-copy="${esc(code)}">Copy</button>` : "<span></span>"}
      </div>`;
    }).join("")}</div>

    <h3>Guilds played for</h3>
    <div class="scroll"><table class="data"><thead><tr><th>Guild</th><th class="num">Games</th><th class="num">Won</th><th class="num">Last seen</th></tr></thead>
    <tbody>${guilds.map((g) => `<tr><td><a href="#/guilds/${encodeURIComponent(g.key)}"><b>${esc(g.name || "?")}</b></a> <span class="muted">[${esc(g.tag || "")}]</span></td>
      <td class="num">${g.n}</td><td class="num">${pct(g.wins, g.n)}</td><td class="num">${esc(ago(g.last))}</td></tr>`).join("")}</tbody></table></div>

    ${perChar.length ? `<h3>Characters</h3>
    <div class="scroll"><table class="data"><thead><tr><th>Character</th><th class="num">Games</th><th class="num">Won</th><th class="num">Last seen</th></tr></thead>
    <tbody>${perChar.map((c) => `<tr><td>${charLink(c.name)}</td><td class="num">${c.games}</td><td class="num">${pct(c.wins, c.games)}</td><td class="num">${esc(ago(c.last))}</td></tr>`).join("")}</tbody></table></div>` : ""}`;

  if (!lists.has(o.key)) lists.set(o.key, newFilters(20));
  matchList(view.querySelector("#list"), matches, lists.get(o.key), { allMatches: all });
  view.querySelectorAll(".lineup [data-copy]").forEach((b) => b.onclick = () => copy(b.dataset.copy));
}

// rows grouped by key, most games first; `head` gives the fields shown for the group
function group(rows, keyOf, head) {
  const g = new Map();
  for (const r of rows) {
    const k = keyOf(r);
    const x = g.get(k) || g.set(k, { key: k, ...head(r), rows: [], n: 0, games: 0, wins: 0, last: 0 }).get(k);
    x.rows.push(r); x.n++; x.games++; x.wins += r.t.won ? 1 : 0; x.last = Math.max(x.last, r.m.at || 0);
  }
  return [...g.values()].sort((a, b) => b.n - a.n || b.last - a.last);
}
