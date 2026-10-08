import { state, esc, skillBar, parseCode, templateCode, copy } from "../core.js";

export function renderHome(view) {
  const folders = state.templates.folders;
  const nTpl = folders.reduce((a, f) => a + f.templates.length, 0);
  view.innerHTML = `
    <h2>GvG Info</h2>
    <p class="lede">${nTpl ? `${nTpl} saved template${nTpl === 1 ? "" : "s"} in ${folders.length} folder${folders.length === 1 ? "" : "s"}.` : "No saved templates yet."} Match history, meta and the build explorer come next, fed from gvg.report.</p>
    <h3>Read a template code</h3>
    <form class="row" id="peek"><input type="text" name="code" placeholder="Paste any skill template code" style="flex:1;min-width:240px"><button class="btn primary" type="submit">Show bar</button></form>
    <div id="out" style="margin-top:14px"></div>
    <h3>Shortcuts</h3>
    <div class="row">
      <a class="btn" href="#/templates">My templates</a>
      <a class="btn" href="#/skills">Find a skill</a>
      <a class="btn" href="#/knowledge">Mechanics and rules</a>
    </div>`;
  view.querySelector("#peek").onsubmit = (e) => {
    e.preventDefault();
    const out = view.querySelector("#out");
    try {
      const t = parseCode(e.target.code.value);
      const code = templateCode(t);
      out.innerHTML = `<div class="meta" style="margin-bottom:8px"><span class="prof" data-p="${t.primary}">${t.primary}</span> / <span class="prof" data-p="${t.secondary}">${t.secondary}</span>
        <span class="attrs">${Object.entries(t.attributes).map(([a, r]) => `${esc(a)} ${r}`).join(", ")}</span></div>
        ${skillBar(t.skills, t)}
        <div class="row" style="margin-top:8px"><span class="code">${esc(code)}</span><button class="btn small primary" id="c">Copy code</button>
        <a class="btn small" href="#/templates">Save it in My templates</a></div>`;
      out.querySelector("#c").onclick = () => copy(code);
    } catch (err) {
      out.innerHTML = `<p class="note">${esc(err.message)}</p>`;
    }
  };
}
