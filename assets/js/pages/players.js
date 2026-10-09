import { esc, lazy, pct, ago } from "../core.js";

const f = { q: "", min: 3, sort: "games", desc: true, open: null };
const COLS = [
  ["n", "Player"], ["games", "Games"], ["win", "Won"], ["kdm", "KD / min"], ["intrm", "Interrupts / min"],
  ["dmgm", "Damage / min"], ["healm", "Healing / min"], ["prevm", "Prevented / min"], ["dpg", "Deaths / game"],
];

export async function renderPlayers(view) {
  const data = await lazy("players");
  const builds = await lazy("builds");
  if (!data?.players?.length) { view.innerHTML = `<h2>Players</h2><div class="empty-state">No match data yet. Press Update matches on the Home page.</div>`; return; }
  const famName = Object.fromEntries((builds?.families || []).map((x) => [x.id, x.name]));
  const q = f.q.toLowerCase();
  const rows = data.players.filter((p) => p.games >= f.min && (!q || p.n.toLowerCase().includes(q))).map((p) => {
    const min = Math.max(1, p.sec / 60);
    return { ...p, win: p.wins / p.games, kdm: p.kd / min, intrm: p.intr / min, dmgm: p.dmg / min, healm: p.heal / min, prevm: p.prev / min, dpg: p.deaths / p.games };
  });
  rows.sort((a, b) => (f.sort === "n" ? a.n.localeCompare(b.n) : (a[f.sort] - b[f.sort])) * (f.desc ? -1 : 1));
  const fmt = (v, d = 1) => (Math.round(v * 10 ** d) / 10 ** d).toLocaleString();

  view.innerHTML = `
    <h2>Players</h2>
    <p class="lede">Stats per character across recorded matches. ${esc(data.note)}</p>
    <div class="toolbar" id="filters">
      <label>Search<input type="search" name="q" value="${esc(f.q)}" placeholder="Character name"></label>
      <label>At least<select name="min">${[1, 3, 5, 10, 25].map((n) => `<option value="${n}"${n === f.min ? " selected" : ""}>${n} games</option>`).join("")}</select></label>
    </div>
    <div class="scroll"><table class="data"><thead><tr>${COLS.map(([k, l]) => `<th class="${k === "n" ? "" : "num"} clickable" data-sort="${k}" aria-sort="${f.sort === k ? (f.desc ? "descending" : "ascending") : "none"}">${l}${f.sort === k ? (f.desc ? " ▾" : " ▴") : ""}</th>`).join("")}</tr></thead>
    <tbody>${rows.slice(0, 300).map((p) => `
      <tr class="clickable" data-p="${esc(p.n)}" tabindex="0"><td><b>${esc(p.n)}</b> <span class="muted">${esc(p.profs[0]?.k || "")}</span></td>
      <td class="num">${p.games}</td><td class="num">${pct(p.wins, p.games)}</td><td class="num">${fmt(p.kdm, 2)}</td><td class="num">${fmt(p.intrm, 2)}</td>
      <td class="num">${fmt(p.dmgm, 0)}</td><td class="num">${fmt(p.healm, 0)}</td><td class="num">${fmt(p.prevm, 0)}</td><td class="num">${fmt(p.dpg, 2)}</td></tr>
      ${f.open === p.n ? `<tr><td colspan="9" class="wrap"><div class="detail" style="margin:4px 0">
        <p>${p.games} games, ${Math.round(p.sec / 60)} minutes, last seen ${ago(p.last)}. Totals: ${p.kd} knockdowns, ${p.intr} interrupts, ${p.cond} conditions and ${p.hexr} hexes removed, ${p.deaths} deaths.</p>
        <p>Plays ${p.profs.map((x) => `${esc(x.k)} (${x.n})`).join(", ")}. Guilds: ${p.guilds.map((x) => `${esc(x.k)} (${x.n})`).join(", ")}.</p>
        <p>Builds: ${p.fams.map((x) => `<a href="#/builds/${encodeURIComponent(x.k)}">${esc(famName[x.k] || x.k)}</a> (${x.n})`).join(", ") || "none grouped yet"}.</p>
      </div></td></tr>` : ""}`).join("")}</tbody></table></div>`;

  view.querySelector("#filters").addEventListener("change", (e) => { if (e.target.name === "min") { f.min = +e.target.value; renderPlayers(view); } });
  view.querySelector("[name=q]").addEventListener("input", (e) => { f.q = e.target.value; clearTimeout(f.t); f.t = setTimeout(() => renderPlayers(view).then(() => { const el = view.querySelector("[name=q]"); el.focus(); el.setSelectionRange(el.value.length, el.value.length); }), 250); });
  view.querySelectorAll("[data-sort]").forEach((th) => th.onclick = () => { if (f.sort === th.dataset.sort) f.desc = !f.desc; else { f.sort = th.dataset.sort; f.desc = th.dataset.sort !== "n"; } renderPlayers(view); });
  view.querySelectorAll("tr[data-p]").forEach((tr) => { const t = () => { f.open = f.open === tr.dataset.p ? null : tr.dataset.p; renderPlayers(view); }; tr.onclick = t; tr.onkeydown = (e) => e.key === "Enter" && t(); });
}
