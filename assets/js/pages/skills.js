import { state, esc, skillCard, costsHtml, writeJson, toast, canSave } from "../core.js";
import { PROF_ATTRS } from "../template.js";

const PROFS = ["Warrior", "Ranger", "Monk", "Necromancer", "Mesmer", "Elementalist", "Assassin", "Ritualist", "Paragon", "Dervish", "None"];
const f = { q: "", prof: "", attr: "", type: "", elite: "", causes: "", removes: "", maxE: "", sort: "name", rank: 12, open: null };
const num = (x) => (x === "" || x == null ? null : parseFloat(String(x).replace("¼", ".25").replace("½", ".5").replace("¾", ".75")));

export function renderSkills(view, [openId]) {
  if (openId) f.open = +openId;
  const types = [...new Set(state.skills.map((s) => s.type))].sort();
  const causes = [...new Set(state.skills.flatMap((s) => s.causes))].sort();
  const removes = [...new Set(state.skills.flatMap((s) => s.removes))].sort();
  const attrs = f.prof && PROF_ATTRS[f.prof] ? PROF_ATTRS[f.prof] : [...new Set(state.skills.map((s) => s.attr))].sort();
  const opt = (v, cur, label = v) => `<option value="${esc(v)}"${v === cur ? " selected" : ""}>${esc(label)}</option>`;

  view.innerHTML = `
    <h2>Skills</h2>
    <p class="lede">Every skill usable in GvG, with PvP versions in place of their PvE originals. Your own notes show in gold and are never overwritten by wiki updates.</p>
    <div class="toolbar" id="filters">
      <label>Search<input type="search" name="q" value="${esc(f.q)}" placeholder="Name or description"></label>
      <label>Profession<select name="prof">${opt("", f.prof, "All")}${PROFS.map((p) => opt(p, f.prof, p === "None" ? "Common" : p)).join("")}</select></label>
      <label>Attribute<select name="attr">${opt("", f.attr, "All")}${attrs.map((a) => opt(a, f.attr)).join("")}</select></label>
      <label>Type<select name="type">${opt("", f.type, "All")}${types.map((t) => opt(t, f.type)).join("")}</select></label>
      <label>Elite<select name="elite">${opt("", f.elite, "Any")}${opt("y", f.elite, "Elite only")}${opt("n", f.elite, "Non-elite")}</select></label>
      <label>Causes<select name="causes">${opt("", f.causes, "Anything")}${causes.map((c) => opt(c, f.causes)).join("")}</select></label>
      <label>Removes<select name="removes">${opt("", f.removes, "Anything")}${removes.map((c) => opt(c, f.removes)).join("")}</select></label>
      <label>Max energy<input type="number" name="maxE" min="0" max="25" value="${esc(f.maxE)}" style="width:80px"></label>
      <label>Sort by<select name="sort">${[["name", "Name"], ["energy", "Energy"], ["recharge", "Recharge"], ["activation", "Cast time"], ["adrenaline", "Adrenaline"]].map(([v, l]) => opt(v, f.sort, l)).join("")}</select></label>
      <label>Show values at rank<input type="number" name="rank" min="0" max="21" value="${f.rank}" style="width:70px"></label>
    </div>
    <div id="detail"></div>
    <p class="muted" id="count"></p>
    <div class="scroll"><table class="data"><thead><tr><th></th><th>Skill</th><th>Profession</th><th>Attribute</th><th>Type</th><th class="num">Energy</th><th class="num">Adren.</th><th class="num">Cast</th><th class="num">Recharge</th></tr></thead>
    <tbody id="rows"></tbody></table></div>`;

  const filters = view.querySelector("#filters");
  filters.addEventListener("input", (e) => {
    const { name, value } = e.target;
    f[name] = name === "rank" ? Math.max(0, Math.min(21, +value || 0)) : value;
    if (name === "prof") { f.attr = ""; renderSkills(view, []); return; }
    draw();
  });
  view.querySelector("#rows").addEventListener("click", (e) => {
    const tr = e.target.closest("tr[data-id]"); if (!tr) return;
    f.open = +tr.dataset.id; drawDetail(); view.querySelector("#detail").scrollIntoView({ block: "nearest" });
  });
  view.querySelector("#rows").addEventListener("keydown", (e) => { if (e.key === "Enter") e.target.closest("tr[data-id]")?.click(); });

  function list() {
    const q = f.q.toLowerCase();
    let out = state.skills.filter((s) =>
      (!q || s.name.toLowerCase().includes(q) || s.desc.toLowerCase().includes(q)) &&
      (!f.prof || s.prof === f.prof) && (!f.attr || s.attr === f.attr) && (!f.type || s.type === f.type) &&
      (!f.elite || (f.elite === "y") === s.elite) && (!f.causes || s.causes.includes(f.causes)) &&
      (!f.removes || s.removes.includes(f.removes)) && (f.maxE === "" || (num(s.energy) ?? 0) <= +f.maxE));
    const key = f.sort;
    out.sort((a, b) => key === "name" ? a.name.localeCompare(b.name) : ((num(a[key]) ?? 999) - (num(b[key]) ?? 999)) || a.name.localeCompare(b.name));
    return out;
  }

  function draw() {
    const rows = list();
    view.querySelector("#count").textContent = `${rows.length} skill${rows.length === 1 ? "" : "s"} match.`;
    view.querySelector("#rows").innerHTML = rows.slice(0, 400).map((s) => `
      <tr data-id="${s.id}" class="clickable" tabindex="0">
        <td><img class="sicon" src="${esc(s.icon)}" alt="" loading="lazy" data-skill="${s.id}" data-rank="${f.rank}"></td>
        <td class="${s.elite ? "elite-name" : ""}">${esc(s.name)}${state.notes[s.id]?.length ? " ✎" : ""}</td>
        <td><span class="prof" data-p="${esc(s.prof)}">${esc(s.prof === "None" ? "Common" : s.prof)}</span></td>
        <td>${esc(s.attr)}</td><td>${esc(s.type)}</td>
        <td class="num">${esc(s.energy)}</td><td class="num">${esc(s.adrenaline)}</td>
        <td class="num">${esc(s.activation)}</td><td class="num">${esc(s.recharge)}</td></tr>`).join("")
      + (rows.length > 400 ? `<tr><td colspan="9" class="muted">Showing the first 400. Narrow the filters to see the rest.</td></tr>` : "");
    drawDetail();
  }

  function drawDetail() {
    const box = view.querySelector("#detail");
    const s = f.open && state.byId.get(f.open);
    if (!s) { box.innerHTML = ""; return; }
    const ranks = [...Array(22).keys()];
    const prog = s.prog.length ? `<div class="scroll"><table class="prog"><tr><th>Rank</th>${ranks.map((r) => `<th class="${r === f.rank ? "hl" : ""}">${r}</th>`).join("")}</tr>
      ${s.prog.map((p) => `<tr><th>${esc(p.name)}${p.derived ? "*" : ""}</th>${ranks.map((r) => `<td class="${r === f.rank ? "hl" : ""}">${esc(p.values[r] ?? "")}</td>`).join("")}</tr>`).join("")}</table></div>
      ${s.prog.some((p) => p.derived) ? `<p class="muted">* Computed from the description range; the wiki has no table for it.</p>` : ""}` : "";
    const tags = [...s.causes.map((c) => `<span class="tag c">Causes ${esc(c)}</span>`), ...s.removes.map((c) => `<span class="tag r">Removes ${esc(c)}</span>`),
      ...(s.target ? [`<span class="tag">Target: ${esc(s.target)}</span>`] : []), ...(s.range ? [`<span class="tag">Range: ${esc(s.range)}</span>`] : []),
      ...s.aoe.filter((a) => !/^none$/i.test(a)).map((a) => `<span class="tag">Area: ${esc(a)}</span>`), ...s.flags.map((x) => `<span class="tag">${esc(x)}</span>`)].join("");
    const wiki = s.notes.map((n) => `<p class="note">${esc(n)}</p>`).join("");
    const mine = state.notes[s.id] || [];
    box.innerHTML = `<div class="detail">
      <div class="row" style="justify-content:space-between"><span class="muted">Skill ID ${s.id}${s.template_id !== s.id ? ` (template code ID ${s.template_id})` : ""} · ${esc(s.campaign)}</span>
      <button class="btn small" id="close">Close</button></div>
      ${skillCard(s, f.rank)}<div class="tags">${tags}</div>${prog}${wiki}
      <h3>My notes</h3>
      ${mine.map((n, i) => `<div class="row"><p class="note mine" style="flex:1">${esc(n)}</p><button class="btn small danger" data-del="${i}">Delete</button></div>`).join("") || `<p class="muted">No notes yet. Add things you've tested that the wiki gets wrong or leaves out.</p>`}
      <div class="row" style="margin-top:8px"><textarea id="newnote" placeholder="e.g. Tested: recharge is actually 8s in GvG"></textarea></div>
      <button class="btn primary" id="addnote" style="margin-top:8px">Save note</button></div>`;
    box.querySelector("#close").onclick = () => { f.open = null; drawDetail(); };
    const persist = async (next, msg) => {
      if (!canSave()) { toast("Add your GitHub key in Settings to save notes."); return; }
      const all = { ...state.notes, [s.id]: next };
      if (!next.length) delete all[s.id];
      try { await writeJson("data/skill_notes.json", all, `${msg}: ${s.name}`); state.notes = all; toast(msg); drawDetail(); }
      catch (e) { toast(e.message); }
    };
    box.querySelector("#addnote").onclick = () => {
      const t = box.querySelector("#newnote").value.trim(); if (t) persist([...mine, t], "Note saved");
    };
    box.querySelectorAll("[data-del]").forEach((b) => b.onclick = () => persist(mine.filter((_, i) => i !== +b.dataset.del), "Note deleted"));
  }

  draw();
}
