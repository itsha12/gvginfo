import { state, esc, settings } from "../core.js";
import { renderBlindTest } from "./blindtest.js";
import { renderMaps } from "./maps.js";
import { renderGolden } from "./golden.js";
import { renderReview } from "./review.js";

// Two tabs share this page: Mechanics (#/knowledge, pages without a tab) and Model (#/model, pages with tab "model",
// plus the Blind test, Guild hall maps and Golden moments pages, which are built from data rather than a markdown file).
const TABS = {
  mechanics: {
    route: "knowledge", title: "Mechanics and rules",
    lede: "",
    docs: () => state.knowledge.filter((d) => d.tab !== "model"),
  },
  model: {
    route: "model", title: "The analysis model",
    lede: "",
    docs: () => [...state.knowledge.filter((d) => d.tab === "model"), { id: "blind-test", title: "Blind test", group: "Your calls", custom: renderBlindTest, hidden: true },
      { id: "maps", title: "Guild hall maps", group: "Your labels", custom: renderMaps },
      { id: "game-review", title: "Game review", group: "Your labels", custom: renderReview },
      { id: "golden-moments", title: "Golden moments", group: "Your labels", custom: renderGolden, hidden: true }],
  },
};

export const renderKnowledge = (view, args) => renderTab(view, args, "mechanics");
export const renderModel = (view, args) => renderTab(view, args, "model");

async function renderTab(view, [docId], tabName) {
  const tab = TABS[tabName];
  const docs = tab.docs();
  // Hidden pages (paused or retired work) stay reachable by a direct link but are not listed.
  const doc = docs.find((d) => d.id === docId) || docs.find((d) => !d.hidden);
  const groups = [];
  for (const d of docs.filter((x) => !x.hidden || x === doc)) {
    const g = d.group || "Other";
    (groups.find((x) => x.name === g) || groups[groups.push({ name: g, docs: [] }) - 1]).docs.push(d);
  }
  const s = { owner: "itsha12", repo: "gvginfo", branch: "main", ...settings() };
  view.innerHTML = `
    <h2>${esc(tab.title)}</h2>
    ${tab.lede ? `<p class="lede">${esc(tab.lede)}</p>` : ""}
    <div class="kb">
      <nav class="kb-nav" aria-label="Topics">${groups.map((g) => `<h4>${esc(g.name)}</h4>${g.docs.map((d) =>
        `<a href="#/${tab.route}/${esc(d.id)}"${d.id === doc?.id ? ' aria-current="page"' : ""}>${esc(d.title)}</a>`).join("")}`).join("")}</nav>
      <div><article class="doc" id="doc"><p class="muted">Loading…</p></article>
        ${doc && doc.file ? `<div class="doc-tools"><a class="btn small" href="https://github.com/${esc(s.owner)}/${esc(s.repo)}/edit/${esc(s.branch)}/knowledge/${esc(doc.file)}" target="_blank" rel="noopener">Edit this page on GitHub</a></div>` : ""}</div>
    </div>`;
  const out = view.querySelector("#doc");
  if (!doc) { out.innerHTML = `<div class="empty-state">No pages found.</div>`; return; }
  if (doc.custom) { await doc.custom(out); scrollTo({ top: 0 }); return; }
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
