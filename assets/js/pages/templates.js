import { state, esc, skillBar, parseCode, templateCode, copy, toast, writeJson, canSave, attrsFor } from "../core.js";
import { decodeEquipment } from "../template.js";

let folderId = null;
let editing = null; // { folder, tpl, variant } ids being edited, or { new: "template"|"variant", ... }
const uid = () => Math.random().toString(36).slice(2, 10);
const PATH = "data/templates.json";

async function save(msg) {
  if (!canSave()) throw new Error("Add your GitHub key in Settings to save templates.");
  await writeJson(PATH, state.templates, msg);
}

// Rebuild a code so attribute bonuses never leak into it (codes only hold base ranks up to 12).
function info(code, bonus = {}) {
  const d = parseCode(code);
  return { ...d, bonus, code: templateCode(d) || code };
}

function attrLine(t) {
  return Object.entries(t.attributes).filter(([, r]) => r > 0).map(([a, r]) => {
    const b = +(t.bonus?.[a] || 0);
    return `${esc(a)} ${r}${b ? `<span class="muted">+${b}</span>` : ""}`;
  }).join(", ");
}

function eqSlots(code) {
  try { const { slots } = decodeEquipment(code); return slots.length ? slots.join(", ") : ""; } catch { return ""; }
}
function equipmentHtml(list = []) {
  if (!list.length) return "";
  return `<div class="eq-list">${list.map((e) => `<div class="eq">
    <div class="eq-name"><span class="label">Equipment</span>${esc(e.name || "Equipment")}</div>
    <div><div class="row"><span class="code">${esc(e.code)}</span><button class="btn small" data-copy="${esc(e.code)}" data-what="Equipment code">Copy</button></div>
      ${eqSlots(e.code) ? `<div class="muted" style="font-size:.82rem;margin-top:.3rem">${esc(eqSlots(e.code))}</div>` : ""}
      ${e.notes ? `<p class="note mine">${esc(e.notes)}</p>` : ""}</div></div>`).join("")}</div>`;
}

function buildBlock(entry, isVariant, folder, parent) {
  let t;
  try { t = info(entry.code, entry.bonus); } catch (e) {
    return `<div class="${isVariant ? "variant" : "tpl"}"><b>${esc(entry.name)}</b> <span class="muted">Can't read this code: ${esc(e.message)}</span></div>`;
  }
  const H = isVariant ? "h5" : "h4";
  const ids = `data-folder="${folder.id}" data-tpl="${(parent || entry).id}"${isVariant ? ` data-variant="${entry.id}"` : ""}`;
  return `<div class="${isVariant ? "variant" : "tpl"}">
    <${H}>${esc(entry.name)}</${H}>
    <div class="meta"><span class="prof" data-p="${t.primary}">${t.primary}</span> / <span class="prof" data-p="${t.secondary}">${t.secondary === "None" ? "No secondary" : t.secondary}</span>
      <span class="attrs">${attrLine(t)}</span></div>
    ${skillBar(t.skills, t)}
    <div class="row" style="margin-top:8px"><span class="code">${esc(t.code)}</span>
      <button class="btn small primary" data-copy="${esc(t.code)}">Copy code</button>
      <button class="btn small" data-act="edit" ${ids}>Edit</button>
      ${isVariant ? "" : `<button class="btn small" data-act="add-variant" ${ids}>Add variation</button>`}
      <button class="btn small danger" data-act="delete" ${ids}>Delete</button></div>
    ${entry.notes ? `<p class="note mine">${esc(entry.notes)}</p>` : ""}
    ${equipmentHtml(entry.equipment)}
    ${(entry.variations || []).map((v) => buildBlock(v, true, folder, entry)).join("")}
  </div>`;
}

function editorHtml(entry, title) {
  let t = null;
  try { if (entry.code) t = info(entry.code, entry.bonus); } catch { /* shown as error on save */ }
  const attrs = t ? attrsFor(t.primary, t.secondary) : [];
  return `<form class="editor" id="editor">
    <b>${esc(title)}</b>
    <div class="grid">
      <label>Name<input type="text" name="name" required value="${esc(entry.name || "")}"></label>
      <label>Template code<input type="text" name="code" required value="${esc(entry.code || "")}" placeholder="Paste a code from the game"></label>
    </div>
    ${t ? `${skillBar(t.skills, t)}
      <div><span class="muted">Bonus ranks from runes and headgear (shown in tooltips; not stored in the code)</span>
      <div class="grid">${attrs.filter((a) => (t.attributes[a] || 0) > 0).map((a) => `<label>${esc(a)} ${t.attributes[a]} +
        <input type="number" name="bonus:${esc(a)}" min="0" max="4" value="${+(entry.bonus?.[a] || 0)}" style="width:70px"></label>`).join("")}</div></div>` : ""}
    <label>Notes<textarea name="notes" placeholder="When to run it, what to watch for">${esc(entry.notes || "")}</textarea></label>
    <fieldset class="${(entry.equipment || []).length ? "" : "ask"}"><legend>Equipment templates</legend>
      <p class="muted" style="margin:0;font-size:.88rem">${(entry.equipment || []).length ? "Each set is a separate equipment template, e.g. a Vampiric set and a Zealous set." : "<b style=\"color:var(--ink)\">Add the equipment for this bar.</b> In game, open the Hero panel's Equipment tab, save a template, and paste its code here. Add more sets for options (e.g. Vampiric vs Zealous weapon)."}</p>
      ${(entry.equipment || []).map((e, i) => `<div class="eq-row" data-eq="${i}">
        <input type="text" name="eq-name" placeholder="Set name (e.g. Vampiric axe)" value="${esc(e.name || "")}">
        <input type="text" name="eq-code" placeholder="Equipment template code" value="${esc(e.code || "")}">
        <input type="text" name="eq-notes" placeholder="Notes (runes, insignia, mods)" value="${esc(e.notes || "")}">
        <button class="btn small danger" type="button" data-eq-del="${i}">Remove</button></div>`).join("")}
      <div><button class="btn small" type="button" id="eq-add">Add equipment set</button></div>
    </fieldset>
    <div class="row"><button class="btn primary" type="submit">Save</button><button class="btn" type="button" id="cancel">Cancel</button>
      <span class="muted">Paste a new code to change the skills, then save.</span></div>
  </form>`;
}

export function renderTemplates(view) {
  const folders = state.templates.folders;
  if (!folderId || !folders.find((x) => x.id === folderId)) folderId = folders[0]?.id || null;
  const folder = folders.find((x) => x.id === folderId);

  // The editor works on a draft copy so Cancel leaves the saved template untouched.
  let editTarget = null, editTitle = "", original = null;
  if (editing && folder) {
    const tpl = folder.templates.find((x) => x.id === editing.tpl);
    if (editing.new === "template") { editTitle = `New template in ${folder.name}`; editing.draft ??= { equipment: [] }; }
    else if (editing.new === "variant") { editTitle = `New variation of ${tpl?.name}`; editing.draft ??= { code: tpl?.code, bonus: { ...(tpl?.bonus || {}) }, equipment: (tpl?.equipment || []).map((e) => ({ ...e })) }; }
    else {
      original = editing.variant ? tpl?.variations.find((v) => v.id === editing.variant) : tpl;
      editTitle = `Edit ${original?.name}`;
      editing.draft ??= { name: original?.name, code: original?.code, notes: original?.notes, bonus: { ...(original?.bonus || {}) }, equipment: (original?.equipment || []).map((e) => ({ ...e })) };
    }
    editTarget = editing.draft;
  }

  view.innerHTML = `
    <h2>Templates</h2>
    <p class="lede">Your bars, organised in folders, with variations under each one. Each bar and variation can carry one or more equipment templates. Hover a skill for its numbers at your ranks; copy a code to load it in game.</p>
    <div class="layout-2">
      <div>
        <div class="folders" role="list">
          ${folders.map((x) => `<button class="f" role="listitem" data-folder-pick="${x.id}" aria-current="${x.id === folderId}">${esc(x.name)}<span class="muted">${x.templates.length}</span></button>`).join("") || `<p class="muted" style="padding:6px">No folders yet.</p>`}
        </div>
        <form class="row" id="newfolder" style="margin-top:10px"><input type="text" name="name" placeholder="New folder name" required style="flex:1"><button class="btn" type="submit">Add folder</button></form>
        ${folder ? `<div class="row" style="margin-top:10px"><button class="btn small" id="rename">Rename folder</button><button class="btn small danger" id="delfolder">Delete folder</button></div>` : ""}
      </div>
      <section>
        ${folder ? `
          <div class="row"><h3 style="margin:0;flex:1">${esc(folder.name)}</h3><button class="btn primary" id="newtpl">Add template</button></div>
          ${editTarget ? editorHtml(editTarget, editTitle) : ""}
          ${folder.templates.map((t) => buildBlock(t, false, folder)).join("") || (editTarget ? "" : `<div class="empty-state" style="margin-top:12px">This folder is empty. Use Add template and paste a code from the game.</div>`)}
        ` : `<div class="empty-state">Create a folder to start, for example "Frontline", "Midline" or "Backline".</div>`}
      </section>
    </div>`;

  const rerender = () => renderTemplates(view);
  const commit = async (msg) => { try { await save(msg); toast(msg); } catch (e) { toast(e.message); } rerender(); };

  view.querySelectorAll("[data-folder-pick]").forEach((b) => b.onclick = () => { folderId = b.dataset.folderPick; editing = null; rerender(); });
  view.querySelector("#newfolder").onsubmit = (e) => {
    e.preventDefault();
    const name = e.target.name.value.trim(); if (!name) return;
    const f = { id: uid(), name, templates: [] }; folders.push(f); folderId = f.id; commit(`Folder added: ${name}`);
  };
  view.querySelector("#rename")?.addEventListener("click", () => {
    const name = prompt("Folder name", folder.name)?.trim(); if (name) { folder.name = name; commit(`Folder renamed: ${name}`); }
  });
  view.querySelector("#delfolder")?.addEventListener("click", () => {
    if (!confirm(`Delete the folder "${folder.name}" and its ${folder.templates.length} templates?`)) return;
    state.templates.folders = folders.filter((x) => x.id !== folder.id); folderId = null; commit(`Folder deleted: ${folder.name}`);
  });
  view.querySelector("#newtpl")?.addEventListener("click", () => { editing = { new: "template" }; rerender(); });

  view.querySelectorAll("[data-copy]").forEach((b) => b.onclick = () => copy(b.dataset.copy, b.dataset.what));
  view.querySelectorAll("[data-act]").forEach((b) => b.onclick = () => {
    const tpl = folder.templates.find((x) => x.id === b.dataset.tpl);
    const variant = b.dataset.variant;
    if (b.dataset.act === "edit") editing = { tpl: tpl.id, variant };
    if (b.dataset.act === "add-variant") editing = { new: "variant", tpl: tpl.id };
    if (b.dataset.act === "delete") {
      const name = variant ? tpl.variations.find((v) => v.id === variant).name : tpl.name;
      if (!confirm(`Delete "${name}"?`)) return;
      if (variant) tpl.variations = tpl.variations.filter((v) => v.id !== variant);
      else folder.templates = folder.templates.filter((x) => x.id !== tpl.id);
      commit(`Deleted: ${name}`); return;
    }
    rerender();
  });

  const form = view.querySelector("#editor");
  if (form) {
    form.querySelector("#cancel").onclick = () => { editing = null; rerender(); };
    // show the bar as soon as a code is pasted
    form.code.addEventListener("change", () => { Object.assign(editTarget, readForm()); rerender(); });
    form.querySelector("#eq-add").onclick = () => { const d = readForm(); d.equipment.push({ name: "", code: "", notes: "" }); Object.assign(editTarget, d); rerender(); [...view.querySelectorAll('.eq-row [name="eq-name"]')].pop()?.focus(); };
    form.querySelectorAll("[data-eq-del]").forEach((b) => b.onclick = () => { const d = readForm(); d.equipment.splice(+b.dataset.eqDel, 1); Object.assign(editTarget, d); rerender(); });
    form.onsubmit = (e) => {
      e.preventDefault();
      const data = readForm();
      try { data.code = info(data.code).code; } catch (err) { toast(err.message); return; }
      if (data.equipment.some((x) => !x.code && (x.name || x.notes))) { toast("Paste an equipment template code for each set, or remove the empty set."); return; }
      data.equipment = data.equipment.filter((x) => x.code);
      for (const eq of data.equipment) {
        try { decodeEquipment(eq.code); } catch (err) { toast(`${eq.name || "Equipment set"}: ${err.message}`); return; }
      }
      // ask for the equipment before saving a bar without any
      if (!data.equipment.length) {
        const code = prompt(`Equipment template for "${data.name}"?\nPaste the code from the game's Equipment tab, or leave empty to save without one.`, "");
        if (code === null) return;
        if (code.trim()) {
          try { decodeEquipment(code.trim()); } catch (err) { toast(err.message); return; }
          const name = prompt("Name for this equipment set?", "Main set") || "Main set";
          data.equipment.push({ name: name.trim(), code: code.trim(), notes: "" });
        }
      }
      if (editing.new === "template") folder.templates.push({ id: uid(), variations: [], ...data });
      else if (editing.new === "variant") folder.templates.find((x) => x.id === editing.tpl).variations.push({ id: uid(), ...data });
      else Object.assign(original, data);
      editing = null;
      commit(`Saved: ${data.name}`);
    };
    function readForm() {
      const bonus = {};
      for (const el of form.querySelectorAll('[name^="bonus:"]')) if (+el.value) bonus[el.name.slice(6)] = +el.value;
      const equipment = [...form.querySelectorAll(".eq-row")].map((r) => ({
        name: r.querySelector('[name="eq-name"]').value.trim(), code: r.querySelector('[name="eq-code"]').value.trim(), notes: r.querySelector('[name="eq-notes"]').value.trim(),
      }));
      return { name: form.name.value.trim(), code: form.code.value.trim(), notes: form.notes.value.trim(), bonus, equipment };
    }
  }
}
