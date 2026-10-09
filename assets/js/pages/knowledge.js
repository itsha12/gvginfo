import { state, esc, settings } from "../core.js";

export async function renderKnowledge(view, [docId]) {
  const docs = state.knowledge;
  const doc = docs.find((d) => d.id === docId) || docs[0];
  const groups = [];
  for (const d of docs) {
    const g = d.group || "Other";
    (groups.find((x) => x.name === g) || groups[groups.push({ name: g, docs: [] }) - 1]).docs.push(d);
  }
  const s = { owner: "itsha12", repo: "gvginfo", branch: "main", ...settings() };
  view.innerHTML = `
    <h2>Mechanics and rules</h2>
    <p class="lede">One page per topic, from the Guild Wars Wiki plus your own tests. Highlighted lines are things you've tested; they override the wiki. Claude reads these same files when answering questions.</p>
    <div class="kb">
      <nav class="kb-nav" aria-label="Topics">${groups.map((g) => `<h4>${esc(g.name)}</h4>${g.docs.map((d) =>
        `<a href="#/knowledge/${esc(d.id)}"${d.id === doc?.id ? ' aria-current="page"' : ""}>${esc(d.title)}</a>`).join("")}`).join("")}</nav>
      <div><article class="doc" id="doc"><p class="muted">Loading…</p></article>
        ${doc ? `<div class="doc-tools"><a class="btn small" href="https://github.com/${esc(s.owner)}/${esc(s.repo)}/edit/${esc(s.branch)}/knowledge/${esc(doc.file)}" target="_blank" rel="noopener">Edit this page on GitHub</a>
          <span class="muted" style="align-self:center;font-size:.85rem">Or tell Claude: “change the ${esc(doc.title)} page: …”</span></div>` : ""}</div>
    </div>`;
  const out = view.querySelector("#doc");
  if (!doc) { out.innerHTML = `<div class="empty-state">No pages found.</div>`; return; }
  const md = await fetch(`knowledge/${doc.file}`, { cache: "no-cache" }).then((r) => (r.ok ? r.text() : "")).catch(() => "");
  out.innerHTML = md && window.marked ? window.marked.parse(md) : `<pre>${esc(md || "This page is missing.")}</pre>`;
  // tables scroll sideways on narrow screens instead of squashing cells onto several lines
  out.querySelectorAll("table").forEach((t) => { const w = document.createElement("div"); w.className = "tablewrap"; t.replaceWith(w); w.append(t); });
  // highlight lines that start with **Tested…**
  out.querySelectorAll("li, p").forEach((el) => {
    const first = el.firstElementChild;
    if (first?.tagName === "STRONG" && el.firstChild === first && /^Tested/i.test(first.textContent)) el.classList.add("tested");
  });
  scrollTo({ top: 0 });
}
