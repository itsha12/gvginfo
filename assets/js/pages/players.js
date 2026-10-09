import { esc, lazy, pct, ago, readJson, writeJson, canSave, toast } from "../core.js";

// Characters are grouped into people with data/aliases.json: { "people": { "Person name": ["Character", ...] } }.
const f = { q: "", min: 3, sort: "games", desc: true, open: null, view: "chars", sel: new Set() };
const COLS = [
  ["n", "Player"], ["games", "Games"], ["win", "Won"], ["kdm", "KD / min"], ["intrm", "Interrupts / min"],
  ["dmgm", "Damage / min"], ["healm", "Healing / min"], ["prevm", "Prevented / min"], ["dpg", "Deaths / game"],
];
const SUM = ["games", "wins", "sec", "kd", "intr", "dmg", "heal", "prev", "deaths", "cond", "hexr"];
let aliases = null;

const merge = (lists) => { const c = new Map(); for (const l of lists) for (const x of l) c.set(x.k, (c.get(x.k) || 0) + x.n); return [...c.entries()].sort((a, b) => b[1] - a[1]).map(([k, n]) => ({ k, n })); };

export async function renderPlayers(view) {
  const [data, builds] = await Promise.all([lazy("players"), lazy("builds")]);
  aliases ??= (await readJson("data/aliases.json", { people: {} })) || { people: {} };
  aliases.people ||= {};
  if (!data?.players?.length) { view.innerHTML = `<h2>Players</h2><div class="empty-state">No match data yet. Press Update matches on the Recent matches page.</div>`; return; }
  const famName = Object.fromEntries((builds?.families || []).map((x) => [x.id, x.name]));
  const personOf = new Map(Object.entries(aliases.people).flatMap(([p, chars]) => chars.map((c) => [c, p])));
  const people = Object.keys(aliases.people).sort((a, b) => a.localeCompare(b));

  // rows: characters, or people (assigned characters merged; unassigned characters stay on their own)
  let base = data.players;
  if (f.view === "people") {
    const groups = new Map();
    for (const p of data.players) {
      const who = personOf.get(p.n);
      const key = who ? `person:${who}` : `char:${p.n}`;
      const g = groups.get(key);
      if (!g) { groups.set(key, { ...p, n: who || p.n, person: !!who, chars: [p.n], profs: p.profs, guilds: p.guilds, fams: p.fams }); continue; }
      for (const k of SUM) g[k] += p[k] || 0;
      g.chars.push(p.n); g.last = Math.max(g.last, p.last);
      g.profs = merge([g.profs, p.profs]); g.guilds = merge([g.guilds, p.guilds]); g.fams = merge([g.fams, p.fams]);
    }
    base = [...groups.values()];
  }
  const q = f.q.toLowerCase();
  const rows = base.filter((p) => p.games >= f.min && (!q || p.n.toLowerCase().includes(q) || (p.chars || []).some((c) => c.toLowerCase().includes(q)) || (personOf.get(p.n) || "").toLowerCase().includes(q)))
    .map((p) => {
      const min = Math.max(1, p.sec / 60);
      return { ...p, win: p.wins / p.games, kdm: p.kd / min, intrm: p.intr / min, dmgm: p.dmg / min, healm: p.heal / min, prevm: p.prev / min, dpg: p.deaths / p.games };
    });
  rows.sort((a, b) => (f.sort === "n" ? a.n.localeCompare(b.n) : (a[f.sort] - b[f.sort])) * (f.desc ? -1 : 1));
  const shown = rows.slice(0, 300);
  const fmt = (v, d = 1) => (Math.round(v * 10 ** d) / 10 ** d).toLocaleString();
  const chars = f.view === "chars";
  const allShownSelected = chars && shown.length && shown.every((p) => f.sel.has(p.n));

  view.innerHTML = `
    <h2>Players</h2>
    <p class="lede">Stats per character across recorded matches. ${esc(data.note)} Tick character names and assign them to a
      person to group them; the People view adds their stats together.</p>
    <div class="toolbar" id="filters">
      <label>Show<select name="view"><option value="chars"${chars ? " selected" : ""}>Characters</option><option value="people"${chars ? "" : " selected"}>People (${people.length} named)</option></select></label>
      <label>Search<input type="search" name="q" value="${esc(f.q)}" placeholder="Character or person"></label>
      <label>At least<select name="min">${[1, 3, 5, 10, 25].map((n) => `<option value="${n}"${n === f.min ? " selected" : ""}>${n} games</option>`).join("")}</select></label>
    </div>
    <div class="scroll"><table class="data"><thead><tr>
      ${chars ? `<th style="width:2rem"><input type="checkbox" id="all" aria-label="Select all shown" ${allShownSelected ? "checked" : ""}></th>` : ""}
      ${COLS.map(([k, l]) => `<th class="sortable${k === "n" ? "" : " num"}" data-sort="${k}" aria-sort="${f.sort === k ? (f.desc ? "descending" : "ascending") : "none"}">${k === "n" && !chars ? "Person / character" : l}<span class="arrow">${f.sort === k ? (f.desc ? "↓" : "↑") : ""}</span></th>`).join("")}</tr></thead>
    <tbody>${shown.map((p) => `
      <tr class="clickable${f.sel.has(p.n) && chars ? " selected" : ""}" data-p="${esc(p.n)}" tabindex="0">
      ${chars ? `<td><input type="checkbox" data-sel="${esc(p.n)}" aria-label="Select ${esc(p.n)}" ${f.sel.has(p.n) ? "checked" : ""}></td>` : ""}
      <td><b>${esc(p.n)}</b> ${chars && personOf.get(p.n) ? `<span class="pill attr">${esc(personOf.get(p.n))}</span>` : ""}${!chars && p.person ? `<span class="muted small">${p.chars.length} character${p.chars.length === 1 ? "" : "s"}</span>` : ""}
        <span class="muted">${esc(p.profs[0]?.k || "")}</span></td>
      <td class="num">${p.games}</td><td class="num">${pct(p.wins, p.games)}</td><td class="num">${fmt(p.kdm, 2)}</td><td class="num">${fmt(p.intrm, 2)}</td>
      <td class="num">${fmt(p.dmgm, 0)}</td><td class="num">${fmt(p.healm, 0)}</td><td class="num">${fmt(p.prevm, 0)}</td><td class="num">${fmt(p.dpg, 2)}</td></tr>
      ${f.open === p.n ? `<tr><td colspan="${COLS.length + (chars ? 1 : 0)}" class="wrap"><div class="detail" style="margin:4px 0">
        ${p.chars?.length > 1 ? `<p><b>Characters:</b> ${p.chars.map(esc).join(", ")}</p>` : ""}
        <p>${p.games} games, ${Math.round(p.sec / 60)} minutes, last seen ${ago(p.last)}. Totals: ${p.kd} knockdowns, ${p.intr} interrupts, ${p.cond} conditions and ${p.hexr} hexes removed, ${p.deaths} deaths.</p>
        <p>Plays ${p.profs.map((x) => `${esc(x.k)} (${x.n})`).join(", ")}. Guilds: ${p.guilds.map((x) => `${esc(x.k)} (${x.n})`).join(", ")}.</p>
        <p>Builds: ${p.fams.map((x) => `<a href="#/builds/${encodeURIComponent(x.k)}">${esc(famName[x.k] || x.k)}</a> (${x.n})`).join(", ") || "none grouped yet"}.</p>
      </div></td></tr>` : ""}`).join("")}</tbody></table></div>
    ${chars && f.sel.size ? `<form class="assign" id="assign">
      <b>${f.sel.size} selected</b> <span class="muted small">${[...f.sel].slice(0, 4).map(esc).join(", ")}${f.sel.size > 4 ? "…" : ""}</span>
      <label class="sr" for="who">Person</label>
      <input type="text" id="who" list="people" placeholder="Person's name (new or existing)" required>
      <datalist id="people">${people.map((p) => `<option value="${esc(p)}">`).join("")}</datalist>
      <button class="btn primary" type="submit">Assign to person</button>
      <button class="btn" type="button" id="unassign">Remove from person</button>
      <button class="btn ghost" type="button" id="clear">Clear selection</button>
    </form>` : ""}`;

  const rerender = (keepFocus) => renderPlayers(view).then(() => { if (keepFocus) { const el = view.querySelector(keepFocus); el?.focus(); if (el?.setSelectionRange) el.setSelectionRange(el.value.length, el.value.length); } });
  view.querySelector("#filters").addEventListener("change", (e) => {
    if (e.target.name === "min") { f.min = +e.target.value; rerender(); }
    if (e.target.name === "view") { f.view = e.target.value; f.open = null; rerender(); }
  });
  view.querySelector("[name=q]").addEventListener("input", (e) => { f.q = e.target.value; clearTimeout(f.t); f.t = setTimeout(() => rerender("[name=q]"), 250); });
  view.querySelectorAll("[data-sort]").forEach((th) => th.onclick = () => { if (f.sort === th.dataset.sort) f.desc = !f.desc; else { f.sort = th.dataset.sort; f.desc = th.dataset.sort !== "n"; } rerender(); });
  view.querySelectorAll("tr[data-p]").forEach((tr) => {
    const t = (e) => { if (e.target.closest("input")) return; f.open = f.open === tr.dataset.p ? null : tr.dataset.p; rerender(); };
    tr.onclick = t; tr.onkeydown = (e) => e.key === "Enter" && t(e);
  });
  view.querySelectorAll("[data-sel]").forEach((cb) => cb.onchange = () => { cb.checked ? f.sel.add(cb.dataset.sel) : f.sel.delete(cb.dataset.sel); rerender(); });
  view.querySelector("#all")?.addEventListener("change", (e) => { for (const p of shown) e.target.checked ? f.sel.add(p.n) : f.sel.delete(p.n); rerender(); });

  const save = async (msg) => {
    for (const [k, v] of Object.entries(aliases.people)) if (!v.length) delete aliases.people[k];
    try { await writeJson("data/aliases.json", aliases, msg); toast(msg); return true; }
    catch (e) { toast(e.message); aliases = null; return false; } // reload the saved copy so nothing unsaved shows
  };
  const detach = (names) => { for (const list of Object.values(aliases.people)) for (const n of names) { const i = list.indexOf(n); if (i >= 0) list.splice(i, 1); } };
  view.querySelector("#assign")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!canSave()) { toast("Add your GitHub key in Settings to save player names."); return; }
    const who = view.querySelector("#who").value.trim(); if (!who) return;
    const names = [...f.sel];
    detach(names);
    const list = (aliases.people[who] ||= []);
    for (const n of names) if (!list.includes(n)) list.push(n);
    list.sort((a, b) => a.localeCompare(b));
    if (await save(`${names.length} character${names.length === 1 ? "" : "s"} assigned to ${who}`)) f.sel.clear();
    rerender();
  });
  view.querySelector("#unassign")?.addEventListener("click", async () => {
    if (!canSave()) { toast("Add your GitHub key in Settings to save player names."); return; }
    detach([...f.sel]);
    if (await save(`Removed ${f.sel.size} character${f.sel.size === 1 ? "" : "s"} from their person`)) f.sel.clear();
    rerender();
  });
  view.querySelector("#clear")?.addEventListener("click", () => { f.sel.clear(); rerender(); });
}
