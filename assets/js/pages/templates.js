import { state, esc, skillBar, parseCode, templateCode, copy, toast, writeJson, canSave, attrsFor } from "../core.js";

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
    if (editing.new === "template") { editTitle = `New template in ${folder.name}`; editing.draft ??= {}; }
    else if (editing.new === "variant") { editTitle = `New variation of ${tpl?.name}`; editing.draft ??= { code: tpl?.code, bonus: { ...(tpl?.bonus || {}) } }; }
    else {
      original = editing.variant ? tpl?.variations.find((v) => v.id === editing.variant) : tpl;
      editTitle = `Edit ${original?.name}`;
      editing.draft ??= { name: original?.name, code: original?.code, notes: original?.notes, bonus: { ...(original?.bonus || {}) } };
    }
    editTarget = editing.draft;
  }

  view.innerHTML = `
    <h2>My templates</h2>
    <p class="lede">Your bars, organised in folders, with variations under each one. Hover a skill for its numbers at your ranks; copy a code to load it in game.</p>
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

  view.querySelectorAll("[data-copy]").forEach((b) => b.onclick = () => copy(b.dataset.copy));
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
    form.onsubmit = (e) => {
      e.preventDefault();
      const data = readForm();
      try { data.code = info(data.code).code; } catch (err) { toast(err.message); return; }
      if (editing.new === "template") folder.templates.push({ id: uid(), variations: [], ...data });
      else if (editing.new === "variant") folder.templates.find((x) => x.id === editing.tpl).variations.push({ id: uid(), ...data });
      else Object.assign(original, data);
      editing = null;
      commit(`Saved: ${data.name}`);
    };
    function readForm() {
      const bonus = {};
      for (const el of form.querySelectorAll('[name^="bonus:"]')) if (+el.value) bonus[el.name.slice(6)] = +el.value;
      return { name: form.name.value.trim(), code: form.code.value.trim(), notes: form.notes.value.trim(), bonus };
    }
  }
}
