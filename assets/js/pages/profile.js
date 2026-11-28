// Profiles: a player (#/player/<person>, every character assigned to him in data/aliases.json) and a character
// (#/character/<name>, one in-game name). Built from data/recent.json, which holds every stored match with full bars.
import { esc, lazy, readJson, pct, ago, skillBar, copy, codeForPlayer, ABBR } from "../core.js";
import { matchList, newFilters, guildSlug, charLink, personLink } from "./home.js";

const lists = new Map(); // search state per profile, kept while the site is open
const picked = new Map(); // per player: the characters he narrowed the page to (none = all)

// Profession icons: the Guild Wars Wiki's tango icons (File:<Profession>-tango-icon-200.png). If one fails to load,
// the profession's colour square shows instead.
const PROF_ICON = {
  Warrior: "https://wiki.guildwars.com/images/8/88/Warrior-tango-icon-200.png",
  Ranger: "https://wiki.guildwars.com/images/4/43/Ranger-tango-icon-200.png",
  Monk: "https://wiki.guildwars.com/images/8/86/Monk-tango-icon-200.png",
  Necromancer: "https://wiki.guildwars.com/images/a/a8/Necromancer-tango-icon-200.png",
  Mesmer: "https://wiki.guildwars.com/images/c/cc/Mesmer-tango-icon-200.png",
  Elementalist: "https://wiki.guildwars.com/images/3/3c/Elementalist-tango-icon-200.png",
  Assassin: "https://wiki.guildwars.com/images/3/34/Assassin-tango-icon-200.png",
  Ritualist: "https://wiki.guildwars.com/images/1/15/Ritualist-tango-icon-200.png",
  Paragon: "https://wiki.guildwars.com/images/2/21/Paragon-tango-icon-200.png",
  Dervish: "https://wiki.guildwars.com/images/b/bf/Dervish-tango-icon-200.png",
};
export const profIcon = (p) => !p ? "" : `<span class="pico" data-p="${esc(p)}" title="${esc(p)}">${PROF_ICON[p] ? `<img src="${PROF_ICON[p]}" alt="${esc(p)}" loading="lazy" onerror="this.remove()">` : ""}</span>`;
const most = (xs) => { const c = new Map(); for (const x of xs) if (x) c.set(x, (c.get(x) || 0) + 1); return [...c.entries()].sort((a, b) => b[1] - a[1])[0]?.[0]; };

const people = async () => ((await readJson("data/aliases.json", { people: {} })) || {}).people || {};
const isAT = (occ) => /^AT-/.test(occ || "");
const rate = (rows) => rows.length ? `${pct(rows.filter((r) => r.t.won).length, rows.length)}` : "–";
const rec = (rows) => `${rows.filter((r) => r.t.won).length}–${rows.filter((r) => !r.t.won).length}`;

export async function renderPerson(view, [name = ""]) {
  const [recent, P] = await Promise.all([lazy("recent"), people()]);
  const chars = P[name];
  picked.delete(`p:${name}`); // a player page always opens on all his characters
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
  const allRows = [];
  for (const m of all) for (const t of m.teams) for (const p of t.players) if (o.chars.has(p.n)) allRows.push({ m, t, p });
  const pick = o.person ? (picked.get(o.key) || new Set()) : new Set();
  const rows = pick.size ? allRows.filter((r) => pick.has(r.p.n)) : allRows;
  const matches = [...new Map(rows.map((r) => [r.m.id, r.m])).values()];
  const back = `<p><a href="#/players">← Players</a></p>`;
  const sub = o.person
    ? `<div class="char-pick"><span class="muted small">Characters (click to show only those):</span>
        ${[...o.chars].sort((a, b) => a.localeCompare(b)).map((c) => `<button type="button" class="chip-btn" data-pick="${esc(c)}" aria-pressed="${pick.has(c)}"${allRows.some((r) => r.p.n === c) ? "" : ' disabled title="No recorded games"'}>${esc(c)}</button>`).join("")}
        ${pick.size ? `<button type="button" class="btn small ghost" data-pickall>Show all characters</button>` : ""}</div>`
    : o.playedBy ? `<p class="lede">Played by ${personLink(o.playedBy)}</p>` : "";
  if (!allRows.length) {
    view.innerHTML = `${back}<h2>${esc(o.title)}</h2>${sub}<div class="empty-state">No recorded matches.</div>`;
    return;
  }
  const at = rows.filter((r) => isAT(r.m.occ)), mat = rows.filter((r) => r.m.occ === "MAT");
  const last = Math.max(0, ...rows.map((r) => r.m.at || 0));

  // guilds played for
  const guilds = group(rows, (r) => guildSlug(r.t), (r) => ({ name: r.t.guild, tag: r.t.tag }));
  // builds played: one row per build family, its most played full bar shown
  const builds = buildsFrom(rows);
  // a player's characters
  const perChar = o.person ? group(allRows, (r) => r.p.n, (r) => ({ name: r.p.n })) : [];

  view.innerHTML = `${back}
    <h2>${esc(o.title)}</h2>${sub}
    <div class="stats" style="margin-bottom:1rem">
      <div><span>Record</span><b>${rec(rows)}</b><span>${rate(rows)} won, ${rows.length} games</span></div>
      <div><span>AT win rate</span><b>${rate(at)}</b><span>${at.length ? `${rec(at)} in ${at.length} games` : "no AT games"}</span></div>
      <div><span>MAT win rate</span><b>${rate(mat)}</b><span>${mat.length ? `${rec(mat)} in ${mat.length} games` : "no MAT games"}</span></div>
      <div><span>Last seen</span><b>${last ? esc(ago(last)) : "–"}</b><span>${last ? esc(new Date(last).toISOString().slice(0, 10)) : "no games"}</span></div>
    </div>

    <h3>Recent matches</h3>
    <div id="list"></div>

    ${perChar.length ? `<h3>Characters</h3>
    <div class="scroll"><table class="data"><thead><tr><th style="width:1%">Professions</th><th>Character</th><th class="num">Games</th><th class="num">Won</th><th class="num">Last seen</th></tr></thead>
    <tbody>${perChar.map((c) => { const pr = most(c.rows.map((r) => r.p.p)), sc = most(c.rows.filter((r) => r.p.p === pr).map((r) => r.p.s));
      return `<tr><td><span class="picos">${profIcon(pr)}${profIcon(sc)}</span></td><td>${charLink(c.name)}</td><td class="num">${c.games}</td><td class="num">${pct(c.wins, c.games)}</td><td class="num">${esc(ago(c.last))}</td></tr>`; }).join("")}</tbody></table></div>` : ""}

    <h3>Builds played</h3>
    ${buildsHtml(builds)}

    <h3>Guilds played for</h3>
    <div class="scroll"><table class="data"><thead><tr><th>Guild</th><th class="num">Games</th><th class="num">Won</th><th class="num">Last seen</th></tr></thead>
    <tbody>${guilds.map((g) => `<tr><td><a href="#/guilds/${encodeURIComponent(g.key)}"><b>${esc(g.name || "?")}</b></a> <span class="muted">[${esc(g.tag || "")}]</span></td>
      <td class="num">${g.n}</td><td class="num">${pct(g.wins, g.n)}</td><td class="num">${esc(ago(g.last))}</td></tr>`).join("")}</tbody></table></div>

`;

  if (!lists.has(o.key)) lists.set(o.key, newFilters(20));
  matchList(view.querySelector("#list"), matches, lists.get(o.key), { allMatches: all });
  view.querySelectorAll(".lineup [data-copy]").forEach((b) => b.onclick = () => copy(b.dataset.copy));
  view.querySelectorAll("[data-pick]").forEach((b) => b.onclick = () => {
    const set = new Set(pick); if (set.has(b.dataset.pick)) set.delete(b.dataset.pick); else set.add(b.dataset.pick);
    picked.set(o.key, set); const l = lists.get(o.key); if (l) l.limit = l.page || 20; draw(view, recent, o);
  });
  view.querySelector("[data-pickall]")?.addEventListener("click", () => { picked.delete(o.key); draw(view, recent, o); });
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

// Builds played, from rows of { m, t, p }: one per build family, most games first, each shown with its most
// played full bar (the build name and profession taken from that same game).
export function buildsFrom(rows) {
  return group(rows, (r) => r.p.fam || r.p.build || "?", (r) => ({ build: r.p.build || "Unknown build" })).map((b) => {
    const full = b.rows.filter((r) => r.p.bar.every(Boolean));
    const counts = new Map(); for (const r of (full.length ? full : b.rows)) { const k = r.p.bar.join(","); counts.set(k, (counts.get(k) || 0) + 1); }
    const top = [...counts.entries()].sort((x, y) => y[1] - x[1])[0][0];
    return { ...b, pick: b.rows.find((r) => r.p.bar.join(",") === top).p };
  });
}
export const buildsHtml = (builds) => `<div class="lineup">${builds.map((b) => {
  const code = codeForPlayer(b.pick);
  return `<div class="lineup-slot">
    <span class="prof" data-p="${esc(b.pick.p)}">${esc(ABBR[b.pick.p] || b.pick.p)}/${esc(ABBR[b.pick.s] || "")}</span>
    <div class="who"><b>${esc(b.pick.build || b.build)}</b><div class="muted small">${b.n} game${b.n === 1 ? "" : "s"}, ${pct(b.wins, b.n)} won</div></div>
    ${skillBar(b.pick.bar, { attributes: b.pick.attrs }, true)}
    ${code ? `<button class="btn small" data-copy="${esc(code)}">Copy</button>` : "<span></span>"}
  </div>`;
}).join("")}</div>`;
