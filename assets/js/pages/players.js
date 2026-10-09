import { esc, lazy, pct, ago, readJson, writeJson, canSave, toast } from "../core.js";

// Characters are grouped into people with data/aliases.json: { "people": { "Person name": ["Character", ...] } }.
const f = { q: "", min: 3, sort: "games", desc: true, open: null, view: "chars", sel: new Set(), picker: false };
const SUM = ["games", "wins", "sec", "kd", "intr", "dmg", "heal", "prev", "deaths", "cond", "hexr", "taken", "casts", "flawless"];

// Every column the table can show. v(p) returns a number (or null when there's no data); fmt picks the display.
// "Per combat minute" stats come from gvg.report's leaderboard data (data/player_combat.json): only characters that
// qualify there (regular players) have them, and they use time actually in combat rather than full match length.
const mm = (p) => Math.max(1, p.sec / 60);
const cm = (p) => (p.cb?.c ? p.cb.c / 60000 : null);
const cx = (k) => (p) => (cm(p) && p.cb.x[k] != null ? p.cb.x[k] / cm(p) : null);
const cdmg = (p) => (p.cb ? ["player_damage_direct", "player_damage_hybrid", "player_damage_degeneration"].reduce((a, k) => a + (p.cb.x[k] || 0), 0) : null);
const COLUMNS = [
  { k: "games", l: "Games", g: "General", v: (p) => p.games, d: 0 },
  { k: "win", l: "Won", g: "General", v: (p) => p.wins / p.games, fmt: "pct" },
  { k: "flawless", l: "Flawless wins", g: "General", v: (p) => p.flawless || 0, d: 0 },
  { k: "avglen", l: "Avg match", g: "General", v: (p) => p.sec / p.games, fmt: "dur" },
  { k: "last", l: "Last seen", g: "General", v: (p) => p.last, fmt: "ago" },
  { k: "kdm", l: "KD / min", g: "Per match minute", v: (p) => p.kd / mm(p), d: 2 },
  { k: "intrm", l: "Interrupts / min", g: "Per match minute", v: (p) => p.intr / mm(p), d: 2 },
  { k: "dmgm", l: "Damage / min", g: "Per match minute", v: (p) => p.dmg / mm(p), d: 0 },
  { k: "healm", l: "Healing / min", g: "Per match minute", v: (p) => p.heal / mm(p), d: 0 },
  { k: "prevm", l: "Prevented / min", g: "Per match minute", v: (p) => p.prev / mm(p), d: 0 },
  { k: "takenm", l: "Damage taken / min", g: "Per match minute", v: (p) => (p.taken || 0) / mm(p), d: 0 },
  { k: "condm", l: "Conditions removed / min", g: "Per match minute", v: (p) => p.cond / mm(p), d: 2 },
  { k: "hexm", l: "Hexes removed / min", g: "Per match minute", v: (p) => p.hexr / mm(p), d: 2 },
  { k: "castm", l: "Casts / min", g: "Per match minute", v: (p) => (p.casts || 0) / mm(p), d: 1 },
  { k: "cdmg", l: "Damage / combat min", g: "Per combat minute", v: (p) => (cm(p) ? cdmg(p) / cm(p) : null), d: 0 },
  { k: "ckill", l: "Kills / combat min", g: "Per combat minute", v: cx("kills"), d: 3 },
  { k: "cassist", l: "Assists / combat min", g: "Per combat minute", v: cx("assists"), d: 2 },
  { k: "cheal", l: "Healing / combat min", g: "Per combat minute", v: cx("healing_done"), d: 0 },
  { k: "cprev", l: "Prevented / combat min", g: "Per combat minute", v: cx("damage_prevented"), d: 0 },
  { k: "ccond", l: "Conditions removed / combat min", g: "Per combat minute", v: cx("condition_cleanses"), d: 2 },
  { k: "chex", l: "Hexes removed / combat min", g: "Per combat minute", v: cx("hex_cleanses"), d: 2 },
  { k: "cintr", l: "Interrupts / combat min", g: "Per combat minute", v: cx("interrupts"), d: 2 },
  { k: "ckdi", l: "Knockdown interrupts / combat min", g: "Per combat minute", v: cx("knockdown_interrupts"), d: 3 },
  { k: "cfake", l: "Fake casts / combat min", g: "Per combat minute", v: cx("fake_casts"), d: 2 },
  { k: "ctaken", l: "Damage taken / combat min", g: "Per combat minute", v: cx("damage_taken"), d: 0 },
  { k: "crupted", l: "Interrupted / combat min", g: "Per combat minute", v: cx("casts_interrupted"), d: 2 },
  { k: "ckdt", l: "Knockdowns taken / combat min", g: "Per combat minute", v: cx("knockdowns_taken"), d: 2 },
  { k: "cdeath", l: "Deaths / combat min", g: "Per combat minute", v: cx("deaths"), d: 3 },
  { k: "cdist", l: "Distance / min", g: "Per combat minute", v: (p) => (p.cb?.ld && p.cb.x.distance_travelled != null ? p.cb.x.distance_travelled / (p.cb.ld / 60000) : null), d: 0 },
  { k: "cmin", l: "Combat minutes", g: "Per combat minute", v: (p) => cm(p), d: 0 },
  { k: "dpg", l: "Deaths / game", g: "Per game", v: (p) => p.deaths / p.games, d: 2 },
  { k: "kpg", l: "Kills / game", g: "Per game", v: (p) => (p.cb?.m && p.cb.x.kills != null ? p.cb.x.kills / p.cb.m : null), d: 2 },
  { k: "apg", l: "Assists / game", g: "Per game", v: (p) => (p.cb?.m && p.cb.x.assists != null ? p.cb.x.assists / p.cb.m : null), d: 1 },
  { k: "dmgg", l: "Damage / game", g: "Per game", v: (p) => p.dmg / p.games, d: 0 },
  { k: "healg", l: "Healing / game", g: "Per game", v: (p) => p.heal / p.games, d: 0 },
  { k: "kdg", l: "KD / game", g: "Per game", v: (p) => p.kd / p.games, d: 1 },
  { k: "intrg", l: "Interrupts / game", g: "Per game", v: (p) => p.intr / p.games, d: 1 },
  { k: "tdmg", l: "Total damage", g: "Totals", v: (p) => p.dmg, d: 0 },
  { k: "theal", l: "Total healing", g: "Totals", v: (p) => p.heal, d: 0 },
  { k: "tkd", l: "Total KD", g: "Totals", v: (p) => p.kd, d: 0 },
  { k: "tintr", l: "Total interrupts", g: "Totals", v: (p) => p.intr, d: 0 },
  { k: "tkill", l: "Total kills", g: "Totals", v: (p) => p.cb?.x.kills ?? null, d: 0 },
  { k: "tdeath", l: "Total deaths", g: "Totals", v: (p) => p.deaths, d: 0 },
];
const DEFAULT_COLS = ["games", "win", "kdm", "intrm", "dmgm", "healm", "prevm", "dpg"];
const COLS_KEY = "gvginfo.playerColumns";
const loadCols = () => { try { const c = JSON.parse(localStorage.getItem(COLS_KEY)); return Array.isArray(c) && c.length ? c : DEFAULT_COLS; } catch { return DEFAULT_COLS; } };
const saveCols = (c) => { try { localStorage.setItem(COLS_KEY, JSON.stringify(c)); } catch { /* storage blocked */ } };
let colKeys = loadCols();
let aliases = null;

const merge = (lists) => { const c = new Map(); for (const l of lists) for (const x of l) c.set(x.k, (c.get(x.k) || 0) + x.n); return [...c.entries()].sort((a, b) => b[1] - a[1]).map(([k, n]) => ({ k, n })); };

export async function renderPlayers(view) {
  const [data, builds, combat] = await Promise.all([lazy("players"), lazy("builds"), lazy("player_combat")]);
  const cbOf = (n) => combat?.players?.[n] || null;
  aliases ??= (await readJson("data/aliases.json", { people: {} })) || { people: {} };
  aliases.people ||= {};
  if (!data?.players?.length) { view.innerHTML = `<h2>Players</h2><div class="empty-state">No match data yet. Press Update matches on the Recent matches page.</div>`; return; }
  const famName = Object.fromEntries((builds?.families || []).map((x) => [x.id, x.name]));
  const personOf = new Map(Object.entries(aliases.people).flatMap(([p, chars]) => chars.map((c) => [c, p])));
  const people = Object.keys(aliases.people).sort((a, b) => a.localeCompare(b));

  // rows: characters, or people (assigned characters merged; unassigned characters stay on their own)
  let base = data.players.map((p) => ({ ...p, cb: cbOf(p.n) }));
  if (f.view === "people") {
    const groups = new Map();
    for (const p of data.players) {
      const who = personOf.get(p.n);
      const key = who ? `person:${who}` : `char:${p.n}`;
      const g = groups.get(key);
      const cb = cbOf(p.n);
      if (!g) { groups.set(key, { ...p, n: who || p.n, person: !!who, chars: [p.n], profs: p.profs, guilds: p.guilds, fams: p.fams, cb: cb ? { ...cb, x: { ...cb.x } } : null }); continue; }
      for (const k of SUM) g[k] += p[k] || 0;
      if (cb) { // add combat stats across a person's characters
        g.cb ||= { c: 0, m: 0, ld: 0, x: {} };
        g.cb.c += cb.c; g.cb.m += cb.m; g.cb.ld = (g.cb.ld || 0) + (cb.ld || 0);
        for (const [k, v] of Object.entries(cb.x)) g.cb.x[k] = (g.cb.x[k] || 0) + v;
      }
      g.chars.push(p.n); g.last = Math.max(g.last, p.last);
      g.profs = merge([g.profs, p.profs]); g.guilds = merge([g.guilds, p.guilds]); g.fams = merge([g.fams, p.fams]);
    }
    base = [...groups.values()];
  }
  const q = f.q.toLowerCase();
  const rows = base.filter((p) => p.games >= f.min && (!q || p.n.toLowerCase().includes(q) || (p.chars || []).some((c) => c.toLowerCase().includes(q)) || (personOf.get(p.n) || "").toLowerCase().includes(q)))
    .map((p) => ({ ...p, val: Object.fromEntries(COLUMNS.map((c) => [c.k, c.v(p)])) }));
  const cols = colKeys.map((k) => COLUMNS.find((c) => c.k === k)).filter(Boolean);
  if (f.sort !== "n" && !cols.some((c) => c.k === f.sort)) f.sort = cols[0]?.k || "n";
  rows.sort((a, b) => {
    if (f.sort === "n") return a.n.localeCompare(b.n) * (f.desc ? -1 : 1);
    const x = a.val[f.sort], y = b.val[f.sort];
    if (x == null || y == null) return (x == null) - (y == null); // no data always last
    return (x - y) * (f.desc ? -1 : 1);
  });
  const cell = (c, p) => {
    const v = p.val[c.k];
    if (v == null || Number.isNaN(v)) return `<td class="num muted">–</td>`;
    const out = c.fmt === "pct" ? `${Math.round(v * 100)}%` : c.fmt === "dur" ? `${Math.floor(v / 60)}:${String(Math.round(v % 60)).padStart(2, "0")}` : c.fmt === "ago" ? ago(v) : fmt(v, c.d ?? 1);
    return `<td class="num">${out}</td>`;
  };
  const groupsOf = [...new Set(COLUMNS.map((c) => c.g))];
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
      <button class="btn${f.picker ? " primary" : ""}" type="button" id="picker">Columns (${cols.length})</button>
    </div>
    ${f.picker ? `<div class="col-picker">
      ${groupsOf.map((g) => `<fieldset><legend>${esc(g)}</legend>${COLUMNS.filter((c) => c.g === g).map((c) =>
        `<label class="check"><input type="checkbox" data-col="${c.k}" ${colKeys.includes(c.k) ? "checked" : ""}> ${esc(c.l)}</label>`).join("")}</fieldset>`).join("")}
      <div class="row" style="grid-column:1/-1"><button class="btn small" type="button" id="col-reset">Reset to default</button>
        <span class="muted small">Per combat minute uses time actually in combat, from gvg.report's leaderboards${combat ? ` (${Object.keys(combat.players).length} regular characters; updated ${esc(ago(Date.parse(combat.updated)))})` : " — not loaded yet; it arrives with the next Update matches"}. Others show –.</span></div>
    </div>` : ""}
    <div class="scroll"><table class="data"><thead><tr>
      ${chars ? `<th style="width:2rem"><input type="checkbox" id="all" aria-label="Select all shown" ${allShownSelected ? "checked" : ""}></th>` : ""}
      ${[{ k: "n", l: chars ? "Player" : "Person / character" }, ...cols].map((c) => `<th class="sortable${c.k === "n" ? "" : " num"}" data-sort="${c.k}" aria-sort="${f.sort === c.k ? (f.desc ? "descending" : "ascending") : "none"}">${esc(c.l)}<span class="arrow">${f.sort === c.k ? (f.desc ? "↓" : "↑") : ""}</span></th>`).join("")}</tr></thead>
    <tbody>${shown.map((p) => `
      <tr class="clickable${f.sel.has(p.n) && chars ? " selected" : ""}" data-p="${esc(p.n)}" tabindex="0">
      ${chars ? `<td><input type="checkbox" data-sel="${esc(p.n)}" aria-label="Select ${esc(p.n)}" ${f.sel.has(p.n) ? "checked" : ""}></td>` : ""}
      <td><b>${esc(p.n)}</b> ${chars && personOf.get(p.n) ? `<span class="pill attr">${esc(personOf.get(p.n))}</span>` : ""}${!chars && p.person ? `<span class="muted small">${p.chars.length} character${p.chars.length === 1 ? "" : "s"}</span>` : ""}
        <span class="muted">${esc(p.profs[0]?.k || "")}</span></td>
      ${cols.map((c) => cell(c, p)).join("")}</tr>
      ${f.open === p.n ? `<tr><td colspan="${cols.length + 1 + (chars ? 1 : 0)}" class="wrap"><div class="detail" style="margin:4px 0">
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
  view.querySelector("#picker").onclick = () => { f.picker = !f.picker; rerender(); };
  view.querySelectorAll("[data-col]").forEach((cb) => cb.onchange = () => {
    const on = new Set(view.querySelectorAll("[data-col]:checked").length ? [...view.querySelectorAll("[data-col]:checked")].map((x) => x.dataset.col) : []);
    colKeys = COLUMNS.map((c) => c.k).filter((k) => on.has(k)); // keep a stable column order
    if (!colKeys.length) colKeys = ["games"];
    saveCols(colKeys); rerender();
  });
  view.querySelector("#col-reset")?.addEventListener("click", () => { colKeys = [...DEFAULT_COLS]; saveCols(colKeys); rerender(); });
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
