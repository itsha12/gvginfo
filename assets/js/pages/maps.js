import { esc, readJson, writeJson, canSave, toast } from "../core.js";

// Guild hall maps (Model > Guild hall maps). Each hall is drawn from data built by tools/maps/build_maps.py:
//   data/maps/index.json          the halls (id, name, replays, outline source, wiki page)
//   data/maps/outline/<id>.json   the walkable outline: gvg.report's pathing trapezoids, or where players walked
//   data/maps/auto/<id>.json      points the replays give (flag stand, team starts, flag spawns, estimated NPCs)
// Denning's labels are saved to data/maps/labels/<id>.json: {map_id, map, labels: [{id, kind, type, name, note, pts}]}
// with kind "point" (one [x, y]), "area" (a closed shape) or "route" (a line), all in game coordinates.
// The engine does not read the labels yet; they define zones, routes and NPC positions from the next engine bundle on.

const TYPES = {
  point: ["Footman", "Archer", "Knight", "Bodyguard", "Guild Lord", "Res shrine", "Flag spawn", "Flag stand", "Gate", "Gate lock", "Teleporter", "Catapult", "Other"],
  area: ["Footmen area", "Base", "Pit", "Flag stand area", "Bridge", "Choke point", "Other"],
  route: ["Front door", "Back door", "Flag run", "Other"],
};
const NPC = { guild_lord: ["Guild Lord", "#b3261e"], bodyguard: ["Bodyguard", "#d97a1c"], knight: ["Knight", "#6b4fb8"], archer: ["Archer", "#0f7a6c"], footman: ["Footman", "#c2448a"] };
const MODES = [["move", "Look around"], ["point", "Add a point"], ["area", "Trace an area"], ["route", "Draw a route"]];

const S = { index: null, id: null, outline: null, auto: null, labels: {}, dirty: new Set(), mode: "move", draft: [], view: null, showNpc: true };
const Y = (y) => -y;                         // game y runs up, the screen's runs down
const uid = () => Math.random().toString(36).slice(2, 8);

function outlinePath(o) {
  if (o.source === "gvg.report") return o.traps.map(([xtl, xtr, yt, xbl, xbr, yb]) => `M${xtl} ${Y(yt)}L${xtr} ${Y(yt)}L${xbr} ${Y(yb)}L${xbl} ${Y(yb)}Z`).join("");
  const c = o.cell; let d = "";
  for (const [iy, runs] of Object.entries(o.rows)) for (const [x0, x1] of runs) d += `M${x0 * c} ${Y((+iy + 1) * c)}h${(x1 - x0 + 1) * c}v${c}h${-(x1 - x0 + 1) * c}Z`;
  return d;
}

function fitView(o) {
  const [x0, y0, x1, y1] = o.bounds, pad = 400;
  return { x: x0 - pad, y: Y(y1) - pad, w: x1 - x0 + 2 * pad, h: y1 - y0 + 2 * pad };
}

const centre = (pts) => [pts.reduce((a, p) => a + p[0], 0) / pts.length, pts.reduce((a, p) => a + p[1], 0) / pts.length];

function overlay(svg) {
  const u = S.view.w / (svg.clientWidth || 800);           // game units per screen pixel: keeps marks the same size at any zoom
  const a = S.auto || {}, L = S.labels[S.id] || [];
  const txt = (x, y, s, cls = "", mid = false) => `<text x="${mid ? x : x + 9 * u}" y="${Y(y) + 4 * u}" font-size="${11 * u}" class="${cls}"${mid ? ' text-anchor="middle"' : ""}>${esc(s)}</text>`;
  let h = "";
  if (S.showNpc) for (const n of a.npcs || []) {
    const [name, col] = NPC[n.kind] || [n.kind, "#888"];
    const firm = n.how === "melee";
    h += `<circle cx="${n.pos[0]}" cy="${Y(n.pos[1])}" r="${4 * u}" fill="${firm ? col : "none"}" stroke="${col}" stroke-width="${1.5 * u}" opacity="${Math.min(1, 0.35 + n.matches / Math.max(a.replays || 1, 1) * 2)}"><title>${esc(name)} (estimate): attackers stood here in ${n.matches} of ${a.replays} replays${firm ? "" : "; ranged attackers only, so rough"}</title></circle>`;
  }
  for (const p of a.res_shrines || []) h += `<rect x="${p[0] - 6 * u}" y="${Y(p[1]) - 6 * u}" width="${12 * u}" height="${12 * u}" fill="#1f5fd1"><title>Team start (res shrine): where a team's players stand when the replay begins</title></rect>${txt(p[0], p[1], "Team start")}`;
  for (const p of a.flag_spawns || []) h += `<path d="M${p[0]} ${Y(p[1]) - 7 * u}l${7 * u} ${13 * u}h${-14 * u}Z" fill="#1f7a3a"><title>Flag spawn: where new flags are picked up</title></path>${txt(p[0], p[1], "Flag spawn")}`;
  if (a.stand) h += `<path d="M${a.stand[0]} ${Y(a.stand[1]) - 9 * u}l${9 * u} ${9 * u}l${-9 * u} ${9 * u}l${-9 * u} ${-9 * u}Z" fill="#111"><title>Flag stand: where captures happen</title></path>${txt(a.stand[0], a.stand[1], "Flag stand")}`;
  for (const l of L) {
    const name = l.name || l.type;
    if (l.kind === "point") h += `<circle cx="${l.pts[0][0]}" cy="${Y(l.pts[0][1])}" r="${5.5 * u}" class="mp-label-pt" stroke-width="${2 * u}"><title>${esc(name)}${l.note ? ": " + esc(l.note) : ""}</title></circle>${txt(l.pts[0][0], l.pts[0][1], name, "mp-label-t")}`;
    else {
      const d = l.pts.map((p, i) => `${i ? "L" : "M"}${p[0]} ${Y(p[1])}`).join("") + (l.kind === "area" ? "Z" : "");
      const c = l.kind === "area" ? centre(l.pts) : l.pts[Math.floor(l.pts.length / 2)];
      h += `<path d="${d}" class="mp-label-${l.kind}" stroke-width="${2 * u}"${l.kind === "route" ? ` stroke-dasharray="${8 * u} ${5 * u}"` : ""}><title>${esc(name)}${l.note ? ": " + esc(l.note) : ""}</title></path>${txt(c[0], c[1], name, "mp-label-t", l.kind === "area")}`;
    }
  }
  if (S.draft.length) {
    h += `<path d="${S.draft.map((p, i) => `${i ? "L" : "M"}${p[0]} ${Y(p[1])}`).join("")}" class="mp-draft" stroke-width="${2 * u}"/>`;
    for (const p of S.draft) h += `<circle cx="${p[0]}" cy="${Y(p[1])}" r="${3.5 * u}" class="mp-draft-pt"/>`;
  }
  svg.querySelector("#mp-over").innerHTML = h;
}

function setView(svg) { svg.setAttribute("viewBox", `${S.view.x} ${S.view.y} ${S.view.w} ${S.view.h}`); overlay(svg); }

function listHtml() {
  const L = S.labels[S.id] || [];
  if (!L.length) return `<p class="muted">No labels on this hall yet.</p>`;
  return `<div class="tablewrap"><table class="data"><thead><tr><th>Kind</th><th>Type</th><th>Name</th><th>Note</th><th></th></tr></thead><tbody>
  ${L.map((l) => `<tr data-label="${esc(l.id)}"><td>${l.kind === "point" ? "Point" : l.kind === "area" ? `Area (${l.pts.length} corners)` : `Route (${l.pts.length} points)`}</td><td>${esc(l.type)}</td>
    <td><input type="text" data-f="name" value="${esc(l.name || "")}" placeholder="${esc(l.type)}" style="width:12rem"></td>
    <td><input type="text" data-f="note" value="${esc(l.note || "")}" placeholder="e.g. archers cover this entrance" style="width:22rem"></td>
    <td><button class="btn small ghost danger" data-remove>Remove</button></td></tr>`).join("")}
  </tbody></table></div>`;
}

async function loadHall(id) {
  S.id = id; S.draft = []; S.mode = "move";
  [S.outline, S.auto] = await Promise.all([
    fetch(`data/maps/outline/${id}.json`, { cache: "no-cache" }).then((r) => r.json()),
    fetch(`data/maps/auto/${id}.json`, { cache: "no-cache" }).then((r) => r.json()).catch(() => ({})),
  ]);
  if (!S.labels[id]) S.labels[id] = (await readJson(`data/maps/labels/${id}.json`, { labels: [] })).labels || [];
  S.view = fitView(S.outline);
}

export async function renderMaps(out) {
  if (!S.index) S.index = await fetch("data/maps/index.json", { cache: "no-cache" }).then((r) => r.json()).catch(() => null);
  if (!S.index?.halls?.length) { out.innerHTML = `<h1>Guild hall maps</h1><div class="empty-state">No map data yet. Run tools/maps/build_maps.py.</div>`; return; }
  if (!S.id) await loadHall(S.index.halls[0].id);
  const hall = S.index.halls.find((x) => x.id === S.id), o = S.outline;
  const types = TYPES[S.mode] || [];
  const need = S.mode === "area" ? 3 : 2;
  out.innerHTML = `<h1>Guild hall maps</h1>
  <p>Each hall as the replays see it, for you to label. Points mark a single thing (a footman, a gate), areas mark a place (the footmen area, a bridge), and routes mark a way in (front door, back door). Your labels override the estimates. The engine does not read them yet; they define zones, routes, and NPC positions from the next engine change on. ${canSave() ? "" : '<b>Add your GitHub key in Settings to save labels.</b>'}</p>
  <div class="row mp-halls">${S.index.halls.map((x) => `<button class="btn small${x.id === S.id ? " primary" : ""}" data-hall="${esc(x.id)}" title="${x.replays} stored replays">${esc(x.map)}${(S.labels[x.id] || []).length ? ` (${S.labels[x.id].length})` : ""}${S.dirty.has(x.id) ? " *" : ""}</button>`).join("")}</div>
  <p class="small muted" style="margin:.6rem 0">${esc(hall.map)}: ${hall.replays} stored replays. ${o.source === "gvg.report" ? "Outline: gvg.report's walkable area." : `gvg.report publishes no outline for this hall, so the shape is where players walked in the stored replays; corners nobody visited are missing.`}
    <a href="${esc(hall.wiki)}" target="_blank" rel="noopener">Open the wiki page for this hall</a> to compare with its map.</p>
  <div class="row" style="margin:.4rem 0">${MODES.map(([m, t]) => `<button class="btn small${S.mode === m ? " primary" : ""}" data-mode="${m}">${t}</button>`).join("")}
    ${types.length ? `<select data-type aria-label="Type">${types.map((t) => `<option>${esc(t)}</option>`).join("")}</select>` : ""}
    ${S.mode === "area" || S.mode === "route" ? `<button class="btn small" data-finish${S.draft.length >= need ? "" : " disabled"}>Finish (${S.draft.length} point${S.draft.length === 1 ? "" : "s"})</button><button class="btn small ghost" data-undo${S.draft.length ? "" : " disabled"}>Undo last point</button>` : ""}
    <label class="small" style="margin-left:auto"><input type="checkbox" data-npc${S.showNpc ? " checked" : ""}> Estimated NPCs</label>
    <button class="btn small ghost" data-fit>Whole map</button></div>
  <p class="small muted" style="margin:.2rem 0 .5rem">${S.mode === "move" ? "Drag to move, scroll to zoom." : S.mode === "point" ? "Pick a type, then click the map to place it. Drag still moves the map." : S.mode === "area" ? "Pick a type, click each corner in turn, then Finish. Drag still moves the map." : "Pick a type, click along the path from start to end, then Finish. Drag still moves the map."} <span data-xy></span></p>
  <svg class="mp-svg" role="img" aria-label="Map of ${esc(hall.map)}"><path d="${outlinePath(o)}" class="mp-land"/><g id="mp-over"></g></svg>
  <div class="row small mp-legend"><span><i style="background:#111"></i>Flag stand</span><span><i style="background:#1f5fd1"></i>Team start</span><span><i style="background:#1f7a3a"></i>Flag spawn</span>
    ${Object.values(NPC).map(([n, c]) => `<span><i style="background:${c};border-radius:50%"></i>${n} (estimate)</span>`).join("")}<span><i class="mp-yours"></i>Your labels</span></div>
  <p class="small muted">NPC estimates come from where attackers stood when they hit that NPC, so an NPC that walks out to fight shows as several spots. Solid = melee attackers (close to the NPC); hollow = ranged attackers only (rough). Fainter = seen in fewer replays.</p>
  <h3>Labels on ${esc(hall.map)} <button class="btn small primary" data-save${S.dirty.has(S.id) ? "" : " disabled"} style="margin-left:.6rem">Save labels</button></h3>
  <div data-list>${listHtml()}</div>
  <style>.mp-svg{width:100%;height:min(74vh,820px);border:1px solid var(--line);background:#fbfbfa;touch-action:none;cursor:${S.mode === "move" ? "grab" : "crosshair"};user-select:none}
  .mp-land{fill:#dfdfd8;stroke:#dfdfd8;stroke-width:1;vector-effect:non-scaling-stroke}.mp-svg text{fill:var(--ink-2);font-family:var(--sans);pointer-events:none;paint-order:stroke;stroke:#fbfbfa;stroke-width:.25em}
  .mp-label-pt{fill:var(--accent);stroke:#fff}.mp-label-area{fill:var(--accent);fill-opacity:.18;stroke:var(--accent)}.mp-label-route{fill:none;stroke:var(--accent)}.mp-svg text.mp-label-t{fill:#6b5210;font-weight:600}
  .mp-draft{fill:none;stroke:var(--bad)}.mp-draft-pt{fill:var(--bad)}.mp-legend{gap:1.1rem;margin:.5rem 0}.mp-legend i{display:inline-block;width:.7rem;height:.7rem;margin-right:.35rem;vertical-align:-1px}
  .mp-legend i.mp-yours{background:var(--accent);border-radius:50%}.mp-halls{gap:.4rem}.small{font-size:.86rem}</style>`;

  const svg = out.querySelector(".mp-svg"), xy = out.querySelector("[data-xy]");
  setView(svg);
  const toGame = (e) => { const r = svg.getBoundingClientRect(); return [Math.round(S.view.x + (e.clientX - r.left) / r.width * S.view.w), Math.round(-(S.view.y + (e.clientY - r.top) / r.height * S.view.h))]; };
  const touch = () => { S.dirty.add(S.id); renderMaps(out); };

  // the svg keeps its aspect ratio, so the visible box is fitted to the element's shape once it has a size
  const r0 = svg.getBoundingClientRect();
  if (r0.width && r0.height) {
    const want = r0.width / r0.height, have = S.view.w / S.view.h;
    if (Math.abs(want - have) > 0.01) {
      if (want > have) { const w = S.view.h * want; S.view.x -= (w - S.view.w) / 2; S.view.w = w; } else { const h = S.view.w / want; S.view.y -= (h - S.view.h) / 2; S.view.h = h; }
      setView(svg);
    }
  }

  let drag = null;
  svg.addEventListener("pointerdown", (e) => { drag = { x: e.clientX, y: e.clientY, vx: S.view.x, vy: S.view.y, moved: false }; svg.setPointerCapture(e.pointerId); });
  svg.addEventListener("pointermove", (e) => {
    const g = toGame(e); xy.textContent = `x ${g[0]}, y ${g[1]}`;
    if (!drag) return;
    const r = svg.getBoundingClientRect(), dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    if (Math.abs(dx) + Math.abs(dy) > 4) drag.moved = true;
    if (drag.moved) { S.view.x = drag.vx - dx / r.width * S.view.w; S.view.y = drag.vy - dy / r.height * S.view.h; setView(svg); }
  });
  svg.addEventListener("pointerup", (e) => {
    const d = drag; drag = null;
    if (!d || d.moved || S.mode === "move") return;
    const g = toGame(e), type = out.querySelector("[data-type]")?.value || "Other";
    if (S.mode === "point") { (S.labels[S.id] ||= []).push({ id: uid(), kind: "point", type, name: "", note: "", pts: [g] }); S.keepType = type; touch(); }
    else { S.draft.push(g); S.keepType = type; renderMaps(out); }
  });
  svg.addEventListener("wheel", (e) => {
    e.preventDefault();
    const r = svg.getBoundingClientRect(), k = e.deltaY > 0 ? 1.2 : 1 / 1.2;
    const full = fitView(S.outline), w = Math.min(Math.max(S.view.w * k, 600), full.w * 2.5), f = w / S.view.w;
    const px = (e.clientX - r.left) / r.width, py = (e.clientY - r.top) / r.height;
    S.view.x += S.view.w * px * (1 - f); S.view.y += S.view.h * py * (1 - f); S.view.w = w; S.view.h *= f;
    setView(svg);
  }, { passive: false });

  const sel = out.querySelector("[data-type]");
  if (sel && S.keepType && types.includes(S.keepType)) sel.value = S.keepType;
  sel?.addEventListener("change", () => { S.keepType = sel.value; });
  out.querySelectorAll("[data-hall]").forEach((b) => b.onclick = async () => { await loadHall(b.dataset.hall); renderMaps(out); });
  out.querySelectorAll("[data-mode]").forEach((b) => b.onclick = () => { S.mode = b.dataset.mode; S.draft = []; S.keepType = null; renderMaps(out); });
  out.querySelector("[data-npc]").onchange = (e) => { S.showNpc = e.target.checked; overlay(svg); };
  out.querySelector("[data-fit]").onclick = () => { S.view = fitView(S.outline); renderMaps(out); };
  out.querySelector("[data-undo]")?.addEventListener("click", () => { S.draft.pop(); renderMaps(out); });
  out.querySelector("[data-finish]")?.addEventListener("click", () => {
    (S.labels[S.id] ||= []).push({ id: uid(), kind: S.mode, type: sel?.value || "Other", name: "", note: "", pts: S.draft });
    S.draft = []; touch();
  });
  out.querySelectorAll("[data-label]").forEach((tr) => {
    const l = S.labels[S.id].find((x) => x.id === tr.dataset.label);
    tr.querySelectorAll("[data-f]").forEach((inp) => inp.addEventListener("change", () => {
      l[inp.dataset.f] = inp.value.trim(); S.dirty.add(S.id); overlay(svg);
      out.querySelector("[data-save]").disabled = false;
    }));
    tr.querySelector("[data-remove]").onclick = () => { S.labels[S.id] = S.labels[S.id].filter((x) => x !== l); touch(); };
  });
  out.querySelector("[data-save]").onclick = async () => {
    try {
      await writeJson(`data/maps/labels/${S.id}.json`, { map_id: S.id, map: hall.map, labels: S.labels[S.id] || [] }, `Map labels: ${hall.map}`);
      S.dirty.delete(S.id); toast("Saved"); renderMaps(out);
    } catch (e) { toast(e.message); }
  };
}
