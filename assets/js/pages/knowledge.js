import { state, esc } from "../core.js";

export async function renderKnowledge(view, [docId]) {
  const docs = state.knowledge;
  const doc = docs.find((d) => d.id === docId) || docs[0];
  view.innerHTML = `
    <h2>Knowledge</h2>
    <p class="lede">Game mechanics, GvG rules and your own tested findings. Claude reads these same files when answering questions.</p>
    <div class="doclist">${docs.map((d) => `<a class="btn${d.id === doc?.id ? " primary" : ""}" href="#/knowledge/${esc(d.id)}">${esc(d.title)}</a>`).join("")}</div>
    <article class="doc" id="doc"><p class="muted">Loading…</p></article>`;
  if (!doc) { view.querySelector("#doc").innerHTML = `<div class="empty-state">No knowledge files found.</div>`; return; }
  const md = await fetch(`knowledge/${doc.file}`).then((r) => r.text()).catch(() => "");
  view.querySelector("#doc").innerHTML = md && window.marked ? window.marked.parse(md) : `<pre>${esc(md || "This file is missing.")}</pre>`;
}
