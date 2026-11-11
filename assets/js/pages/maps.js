import { esc, readJson, writeJson, canSave, toast } from "../core.js";

// Guild hall maps (Model > Guild hall maps). Each hall is drawn from data built by tools/maps/build_maps.py:
//   data/maps/index.json          the halls (id, name, replays, outline source, wiki page)
//   data/maps/outline/<id>.json   the walkable outline: gvg.report's pathing trapezoids, or where players walked
//   data/maps/auto/<id>.json      points the replays give (flag stand, team starts, flag spawns, estimated NPCs)
// Denning's labels are saved to data/maps/labels/<id>.json: {map_id, map, labels: [{id, kind, type, name, note, pts}]}
// with kind "point" (one [x, y]), "area" (a closed shape) or "route" (a line), all in game coordinates.
// The engine does not read the labels yet; they define zones, routes and NPC positions from the next engine bundle on.
// Drafts: data/maps/draft/<id>.json (tools/maps/draft_labels.py) holds labels guessed from the replays, each with its
// evidence ("how"). They are drawn dashed and listed for Denning to accept (copied into his labels with from_draft = the
// draft's id) or remove (the id is added to "dismissed" in his labels file). Draft ids are stable, so a draft he has
// dealt with stays dealt with when the drafts are rebuilt.

const TYPES = {
  point: ["Footman", "Archer", "Knight", "Bodyguard", "Guild Lord", "Res shrine", "Flag spawn", "Flag stand", "Obelisk flag stand", "Gate", "Gate lock", "Gate lever", "Vine seed", "Teleporter entrance", "Teleporter exit", "Teleporter", "Statue", "Catapult", "Trebuchet", "Repair kit", "Health shrine", "Flame sentinel", "Hazard", "Other"],
  area: ["Base", "Pit", "Flag stand area", "Greater stand area", "Footmen area", "Bridge", "Choke point", "Miasma", "Lava", "Tar", "Ice", "Water", "Fireball zone", "Hazard", "Other"],
  route: ["Front door", "Back door", "Flag run", "Collapse route", "Teleporter (one way)", "Other"],
};
const NPC = { guild_lord: ["Guild Lord", "#b3261e"], bodyguard: ["Bodyguard", "#d97a1c"], knight: ["Knight", "#6b4fb8"], archer: ["Archer", "#0f7a6c"], footman: ["Footman", "#c2448a"] };
const MODES = [["move", "Look around"], ["point", "Add a point"], ["area", "Trace an area"], ["route", "Draw a route"]];
// how each type is drawn: areas [fill, opacity], routes [stroke, dash in pixels or null], points [shape, colour, always named]
const AREA = { "Base": ["#5b8fd6", 0.26], "Pit": ["#c7473d", 0.5], "Flag stand area": ["#d9a514", 0.55], "Greater stand area": ["#e8c95a", 0.22], "Footmen area": ["#c2448a", 0.45], "Bridge": ["#1f9e98", 0.55],
  "Choke point": ["#e07b1f", 0.55], "Miasma": ["#7a4fb8", 0.5], "Lava": ["#d9482b", 0.55], "Tar": ["#3d3d3d", 0.5], "Ice": ["#7fc4e8", 0.6], "Water": ["#3d7fc9", 0.45],
  "Fireball zone": ["#e0662b", 0.4], "Hazard": ["#9a3fa0", 0.45], "Other": ["#8a8a85", 0.4] };
const ROUTE = { "Front door": ["#1f7a3a", null], "Back door": ["#a8432b", null], "Flag run": ["#1f5fd1", [2, 5]], "Collapse route": ["#6b4fb8", [9, 5]],
  "Teleporter (one way)": ["#0088aa", [3, 4]], "Other": ["#74746f", [9, 5]] };
const POINT = { "Footman": ["circle", "#c2448a"], "Archer": ["tri", "#0f7a6c"], "Knight": ["square", "#6b4fb8"], "Bodyguard": ["diamond", "#d97a1c"], "Guild Lord": ["star", "#b3261e"],
  "Res shrine": ["plus", "#1f5fd1"], "Flag spawn": ["tri", "#1f7a3a"], "Flag stand": ["flag", "#111111"], "Obelisk flag stand": ["flag", "#7a5c2e", true], "Gate": ["bar", "#7a5c2e", true],
  "Gate lock": ["ring", "#7a5c2e", true], "Gate lever": ["ring", "#7a5c2e", true], "Vine seed": ["diamond", "#5c9a1f", true], "Hazard": ["tri", "#9a3fa0", true], "Teleporter entrance": ["hex", "#0088aa", true], "Teleporter exit": ["hex", "#0088aa", true],
  "Teleporter": ["hex", "#0088aa", true], "Statue": ["square", "#74746f", true], "Catapult": ["square", "#74746f", true], "Trebuchet": ["square", "#8a5a2b", true], "Repair kit": ["ring", "#8a5a2b", true],
  "Health shrine": ["plus", "#b3261e", true], "Flame sentinel": ["star", "#d9482b", true], "Other": ["circle", "#74746f", true] };
// a label typed "Other" but named after a known type is drawn as that type ("Miasma", "Collapse route option")
function typeOf(l) {
  const table = l.kind === "area" ? AREA : l.kind === "route" ? ROUTE : POINT;
  if (l.type !== "Other" || !l.name) return table[l.type] ? l.type : "Other";
  const n = l.name.trim().toLowerCase();
  return Object.keys(table).find((t) => t !== "Other" && n.startsWith(t.toLowerCase().replace(/ \(.*$/, ""))) || "Other";
}

const S = { index: null, id: null, outline: null, auto: null, labels: {}, dirty: new Set(), mode: "move", draft: [], view: null, show: null,
  drafts: {}, dismissed: {}, hot: null };
// the drafts of the hall being shown that Denning has neither accepted nor removed
// (a drafted point is also dropped when a label of its type already sits on it, so a hall labelled by hand is only offered what it lacks)
const pending = () => ((S.drafts[S.id] || {}).labels || []).filter((d) => !(S.dismissed[S.id] || new Set()).has(d.id)
  && !(S.labels[S.id] || []).some((l) => l.from_draft === d.id || (d.kind === "point" && l.kind === "point" && l.type === d.type && Math.hypot(l.pts[0][0] - d.pts[0][0], l.pts[0][1] - d.pts[0][1]) < 300)));
const Y = (y) => -y;                         // game y runs up, the screen's runs down
const uid = () => Math.random().toString(36).slice(2, 8);
const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1]);

// is a game point on the walkable area of the hall being shown
function inLand(x, y) {
  const o = S.outline;
  if (o.source !== "gvg.report") { const c = o.cell; return (o.rows[Math.floor(y / c)] || []).some(([a, b]) => Math.floor(x / c) >= a && Math.floor(x / c) <= b); }
  for (const [xtl, xtr, yt, xbl, xbr, yb] of o.traps) {
    if (yt === yb || y > Math.max(yt, yb) || y < Math.min(yt, yb)) continue;
    const f = (y - yb) / (yt - yb), xl = xbl + (xtl - xbl) * f, xr = xbr + (xtr - xbr) * f;
    if (x >= Math.min(xl, xr) && x <= Math.max(xl, xr)) return true;
  }
  return false;
}
function inPoly(x, y, pts) {
  let c = false;
  for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
    const [x1, y1] = pts[i], [x2, y2] = pts[j];
    if ((y1 > y) !== (y2 > y) && x < (x2 - x1) * (y - y1) / (y2 - y1) + x1) c = !c;
  }
  return c;
}
const polyArea = (pts) => Math.abs(pts.reduce((a, p, i) => { const q = pts[(i + 1) % pts.length]; return a + p[0] * q[1] - q[0] * p[1]; }, 0)) / 2;
// where an area's name goes: the walkable spot inside the shape nearest its middle (the middle itself can be a wall)
const anchors = new Map();
function anchor(l, all) {
  const smaller = all.filter((o) => o !== l && o.kind === "area" && polyArea(o.pts) < polyArea(l.pts));   // a base's name stays out of its pit
  const key = `${S.id}:${l.id}:${l.pts.length}:${smaller.length}`;
  if (anchors.has(key)) return anchors.get(key);
  const c = centre(l.pts), xs = l.pts.map((p) => p[0]), ys = l.pts.map((p) => p[1]);
  let best = c, bd = Infinity;
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys), n = 16;
  for (const clear of [true, false]) {
    for (let i = 1; i < n; i++) for (let j = 1; j < n; j++) {
      const x = x0 + (x1 - x0) * i / n, y = y0 + (y1 - y0) * j / n, d = dist([x, y], c);
      if (d < bd && inPoly(x, y, l.pts) && inLand(x, y) && (!clear || !smaller.some((o) => inPoly(x, y, o.pts)))) { best = [x, y]; bd = d; }
    }
    if (bd < Infinity) break;
  }
  anchors.set(key, best); return best;
}

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

function glyph(shape, x, y, r, col) {
  const Yy = Y(y), a = `fill="${col}" stroke="#fff" stroke-width="${r * 0.28}"`;
  if (shape === "tri") return `<path d="M${x} ${Yy - r * 1.15}L${x + r} ${Yy + r * 0.8}H${x - r}Z" ${a}/>`;
  if (shape === "square") return `<rect x="${x - r * 0.85}" y="${Yy - r * 0.85}" width="${r * 1.7}" height="${r * 1.7}" ${a}/>`;
  if (shape === "diamond") return `<path d="M${x} ${Yy - r * 1.15}L${x + r * 1.15} ${Yy}L${x} ${Yy + r * 1.15}L${x - r * 1.15} ${Yy}Z" ${a}/>`;
  if (shape === "star") { let d = ""; for (let i = 0; i < 10; i++) { const rr = (i % 2 ? 0.62 : 1.5) * r, t = Math.PI * i / 5 - Math.PI / 2; d += `${i ? "L" : "M"}${x + rr * Math.cos(t)} ${Yy + rr * Math.sin(t)}`; } return `<path d="${d}Z" ${a}/>`; }
  if (shape === "plus") return `<path d="M${x - r * 0.4} ${Yy - r * 1.1}h${r * 0.8}v${r * 0.7}h${r * 0.7}v${r * 0.8}h${-r * 0.7}v${r * 0.7}h${-r * 0.8}v${-r * 0.7}h${-r * 0.7}v${-r * 0.8}h${r * 0.7}Z" ${a}/>`;
  if (shape === "flag") return `<path d="M${x - r * 0.7} ${Yy + r * 1.3}V${Yy - r * 1.5}L${x + r * 1.3} ${Yy - r * 0.75}L${x - r * 0.7} ${Yy}" fill="${col}" stroke="${col}" stroke-width="${r * 0.4}" stroke-linejoin="round"/>`;
  if (shape === "bar") return `<rect x="${x - r * 1.3}" y="${Yy - r * 0.45}" width="${r * 2.6}" height="${r * 0.9}" ${a}/>`;
  if (shape === "ring") return `<circle cx="${x}" cy="${Yy}" r="${r * 0.8}" fill="#fff" stroke="${col}" stroke-width="${r * 0.5}"/>`;
  if (shape === "hex") { let d = ""; for (let i = 0; i < 6; i++) { const t = Math.PI * i / 3; d += `${i ? "L" : "M"}${x + r * 1.15 * Math.cos(t)} ${Yy + r * 1.15 * Math.sin(t)}`; } return `<path d="${d}Z" ${a}/>`; }
  return `<circle cx="${x}" cy="${Yy}" r="${r}" ${a}/>`;
}
// an arrow head at the end of a line that came from `from`
function head(to, from, r, col) {
  const t = Math.atan2(Y(to[1]) - Y(from[1]), to[0] - from[0]), p = (da, k) => `${to[0] + k * r * Math.cos(t + da)} ${Y(to[1]) + k * r * Math.sin(t + da)}`;
  return `<path d="M${p(0, 1.6)}L${p(2.5, 1.5)}L${p(-2.5, 1.5)}Z" fill="${col}"/>`;
}
// plain "Teleporter" points come in pairs: the end nearer a Guild Lord is taken as the way in (they are one-way)
function teleporterPairs(L) {
  const tp = L.filter((l) => l.kind === "point" && l.type === "Teleporter"), lords = L.filter((l) => l.kind === "point" && l.type === "Guild Lord").map((l) => l.pts[0]);
  const out = [], used = new Set();
  if (!lords.length) return out;
  const toLord = (p) => Math.min(...lords.map((q) => dist(p, q)));
  for (const a of [...tp].sort((x, y) => toLord(x.pts[0]) - toLord(y.pts[0]))) {
    if (used.has(a)) continue;
    const b = tp.filter((x) => x !== a && !used.has(x)).sort((x, y) => dist(a.pts[0], x.pts[0]) - dist(a.pts[0], y.pts[0]))[0];
    if (!b) break;
    used.add(a); used.add(b); out.push([a.pts[0], b.pts[0]]);
  }
  return out;
}

function overlay(svg) {
  const u = S.view.w / (svg.clientWidth || 800);           // game units per screen pixel: keeps marks the same size at any zoom
  const a = S.auto || {}, L = S.labels[S.id] || [], sh = S.show;
  const tip = (l) => `<title>${esc(l.name || l.type)}${l.name && l.name !== l.type ? ` (${esc(l.type)})` : ""}${l.note ? ": " + esc(l.note) : ""}</title>`;
  const txt = (x, y, s, cls = "", mid = false) => `<text x="${mid ? x : x + 9 * u}" y="${Y(y) + 4 * u}" font-size="${11 * u}" class="${cls}"${mid ? ' text-anchor="middle"' : ""}>${esc(s)}</text>`;
  let h = "", names = "";
  if (sh.drafts) {
    const P = pending(), w = (d) => (S.hot === d.id ? 2.2 : 1);
    h += `<g clip-path="url(#mp-clip)">`;
    for (const d of P.filter((x) => x.kind === "area").sort((x, y) => polyArea(y.pts) - polyArea(x.pts))) {
      const [col] = AREA[typeOf(d)];
      h += `<path d="${d.pts.map((p, i) => `${i ? "L" : "M"}${p[0]} ${Y(p[1])}`).join("")}Z" fill="${col}" fill-opacity="${S.hot === d.id ? 0.4 : 0.13}" stroke="${col}" stroke-width="${3 * u * w(d)}" stroke-dasharray="${7 * u} ${5 * u}"><title>Draft ${esc(d.type)}: ${esc(d.how)}</title></path>`;
    }
    h += `</g>`;
    for (const d of P.filter((x) => x.kind === "route")) {
      const [col] = ROUTE[typeOf(d)], p = d.pts;
      h += `<path d="${p.map((q, i) => `${i ? "L" : "M"}${q[0]} ${Y(q[1])}`).join("")}" fill="none" stroke="${col}" stroke-width="${2.5 * u * w(d)}" stroke-dasharray="${7 * u} ${5 * u}" stroke-linejoin="round" opacity="${S.hot === d.id ? 1 : 0.8}"><title>Draft ${esc(d.type)}: ${esc(d.how)}</title></path>`
        + `<circle cx="${p[0][0]}" cy="${Y(p[0][1])}" r="${3 * u * w(d)}" fill="${col}"/>${head(p[p.length - 1], p[p.length - 2], 4.5 * u * w(d), col)}`;
    }
    for (const d of P.filter((x) => x.kind === "point")) {
      const [shape, col] = POINT[typeOf(d)], [x, y] = d.pts[0];
      h += `<g opacity="${S.hot === d.id ? 1 : 0.75}"><title>Draft ${esc(d.type)}: ${esc(d.how)}</title><circle cx="${x}" cy="${Y(y)}" r="${10 * u * w(d)}" fill="none" stroke="${col}" stroke-width="${1.5 * u}" stroke-dasharray="${3 * u} ${3 * u}"/>${glyph(shape, x, y, 4.5 * u, col)}</g>`;
      names += txt(x + 4 * u, y, d.type, "mp-draft-t");
    }
  }
  // areas first, biggest underneath, cut to the walkable area so a rough outline still reads cleanly
  if (sh.areas) {
    h += `<g clip-path="url(#mp-clip)">`;
    for (const l of L.filter((x) => x.kind === "area").sort((x, y) => polyArea(y.pts) - polyArea(x.pts))) {
      const [col, op] = AREA[typeOf(l)];
      h += `<path d="${l.pts.map((p, i) => `${i ? "L" : "M"}${p[0]} ${Y(p[1])}`).join("")}Z" fill="${col}" fill-opacity="${op}" stroke="${col}" stroke-width="${3 * u}" stroke-linejoin="round">${tip(l)}</path>`;
      const c = anchor(l, L);
      names += `<text x="${c[0]}" y="${Y(c[1]) + 3 * u}" font-size="${9 * u}" text-anchor="middle" class="mp-area-t" fill="${col}">${esc(l.name || l.type)}</text>`;
    }
    h += `</g>`;
  }
  if (sh.npc) for (const n of a.npcs || []) {
    const [name, col] = NPC[n.kind] || [n.kind, "#888"];
    const firm = n.how === "melee";
    h += `<circle cx="${n.pos[0]}" cy="${Y(n.pos[1])}" r="${3.5 * u}" fill="${firm ? col : "none"}" stroke="${col}" stroke-width="${1.5 * u}" opacity="${Math.min(0.75, 0.25 + n.matches / Math.max(a.replays || 1, 1) * 2)}"><title>${esc(name)} (estimate): attackers stood here in ${n.matches} of ${a.replays} replays${firm ? "" : "; ranged attackers only, so rough"}</title></circle>`;
  }
  if (sh.replay) {
    for (const p of a.res_shrines || []) h += `<rect x="${p[0] - 5 * u}" y="${Y(p[1]) - 5 * u}" width="${10 * u}" height="${10 * u}" fill="none" stroke="#1f5fd1" stroke-width="${2 * u}"><title>Team start, from the replays: where a team's players stand when the replay begins</title></rect>${txt(p[0], p[1], "Team start")}`;
    for (const p of a.flag_spawns || []) h += `<path d="M${p[0]} ${Y(p[1]) - 7 * u}l${7 * u} ${13 * u}h${-14 * u}Z" fill="none" stroke="#1f7a3a" stroke-width="${2 * u}"><title>Flag spawn, from the replays: where new flags are picked up</title></path>${txt(p[0], p[1], "Flag spawn")}`;
    if (a.stand) h += `<path d="M${a.stand[0]} ${Y(a.stand[1]) - 9 * u}l${9 * u} ${9 * u}l${-9 * u} ${9 * u}l${-9 * u} ${-9 * u}Z" fill="none" stroke="#111" stroke-width="${2 * u}"><title>Flag stand, from the replays: where captures happen</title></path>${txt(a.stand[0], a.stand[1], "Flag stand")}`;
  }
  if (sh.routes) {
    for (const l of L.filter((x) => x.kind === "route")) {
      const [col, dash] = ROUTE[typeOf(l)], p = l.pts;
      h += `<path d="${p.map((q, i) => `${i ? "L" : "M"}${q[0]} ${Y(q[1])}`).join("")}" fill="none" stroke="#fff" stroke-width="${6 * u}" stroke-linejoin="round" stroke-linecap="round" opacity=".7"/>`
        + `<path d="${p.map((q, i) => `${i ? "L" : "M"}${q[0]} ${Y(q[1])}`).join("")}" fill="none" stroke="${col}" stroke-width="${3 * u}" stroke-linejoin="round" stroke-linecap="round"${dash ? ` stroke-dasharray="${dash[0] * u} ${dash[1] * u}"` : ""}>${tip(l)}</path>`
        + `<circle cx="${p[0][0]}" cy="${Y(p[0][1])}" r="${3.5 * u}" fill="${col}"/>${head(p[p.length - 1], p[p.length - 2], 5 * u, col)}`;
      const m = p[Math.floor((p.length - 1) / 2)];
      if (l.name) names += `<text x="${m[0] + 7 * u}" y="${Y(m[1]) - 5 * u}" font-size="${10 * u}" class="mp-route-t" fill="${col}">${esc(l.name)}</text>`;   // the key names the plain ones by colour
    }
    for (const [from, to] of teleporterPairs(L)) h += `<path d="M${from[0]} ${Y(from[1])}L${to[0]} ${Y(to[1])}" fill="none" stroke="#0088aa" stroke-width="${2 * u}" stroke-dasharray="${3 * u} ${4 * u}"><title>One-way teleporter. Direction is a reading: the end nearer the Guild Lord is taken as the way in.</title></path>${head([to[0] + (from[0] - to[0]) * 12 * u / dist(from, to), to[1] + (from[1] - to[1]) * 12 * u / dist(from, to)], from, 5 * u, "#0088aa")}`;
  }
  if (sh.points) for (const l of L.filter((x) => x.kind === "point")) {
    const [shape, col, named] = POINT[typeOf(l)], [x, y] = l.pts[0];
    h += `<g>${tip(l)}${glyph(shape, x, y, 5 * u, col)}</g>`;
    if (named || l.name) names += txt(x, y, l.name || l.type, "mp-label-t");
  }
  h += names;
  if (S.draft.length) {
    h += `<path d="${S.draft.map((p, i) => `${i ? "L" : "M"}${p[0]} ${Y(p[1])}`).join("")}" class="mp-draft" stroke-width="${2 * u}"/>`;
    for (const p of S.draft) h += `<circle cx="${p[0]}" cy="${Y(p[1])}" r="${3.5 * u}" class="mp-draft-pt"/>`;
  }
  svg.querySelector("#mp-over").innerHTML = h;
}

// the key under the map: only what this hall shows
function legendHtml() {
  const L = S.labels[S.id] || [], sh = S.show, a = S.auto || {};
  const seen = (kind) => [...new Set(L.filter((l) => l.kind === kind).map(typeOf))];
  const rows = [];
  if (sh.areas && seen("area").length) rows.push(["Areas", seen("area").map((t) => `<span><i style="background:${AREA[t][0]};opacity:${Math.min(1, AREA[t][1] + 0.35)}"></i>${esc(t)}</span>`)]);
  if (sh.routes && seen("route").length) rows.push(["Routes", seen("route").map((t) => `<span><i class="mp-line" style="border-top:3px ${ROUTE[t][1] ? "dashed" : "solid"} ${ROUTE[t][0]}"></i>${esc(t)}</span>`).concat(teleporterPairs(L).length ? [`<span><i class="mp-line" style="border-top:3px dotted #0088aa"></i>Teleporter, one way</span>`] : [])]);
  if (sh.points && seen("point").length) rows.push(["Points", seen("point").map((t) => `<span><svg viewBox="-9 -9 18 18" width="14" height="14">${glyph(POINT[t][0], 0, 0, 5, POINT[t][1])}</svg>${esc(t)}</span>`)]);
  const rep = [];
  if (sh.replay) rep.push(`<span><i class="mp-hollow" style="border-color:#111"></i>Flag stand</span>`, `<span><i class="mp-hollow" style="border-color:#1f5fd1"></i>Team start</span>`, `<span><i class="mp-hollow" style="border-color:#1f7a3a"></i>Flag spawn</span>`);
  if (sh.npc) rep.push(...Object.values(NPC).map(([n, c]) => `<span><i style="background:${c};border-radius:50%;opacity:.6"></i>${n}</span>`));
  if (rep.length) rows.push(["From the replays (estimates)", rep]);
  if (sh.drafts && pending().length) rows.push(["Drafts", [`<span><i class="mp-line" style="border-top:3px dashed #74746f"></i>dashed, in the colour of their type, until you accept or remove them</span>`]]);
  return rows.map(([t, items]) => `<div class="row small mp-legend"><b>${t}</b>${items.join("")}</div>`).join("");
}

function setView(svg) { svg.setAttribute("viewBox", `${S.view.x} ${S.view.y} ${S.view.w} ${S.view.h}`); overlay(svg); }

// where a label sits on the map as drawn, in words ("top left"), so two drafts of one type can be told apart
function whereOn(pts) {
  const [x0, y0, x1, y1] = S.outline.bounds, c = centre(pts), fx = (c[0] - x0) / (x1 - x0), fy = (c[1] - y0) / (y1 - y0);
  return `${fy > 0.6 ? "top" : fy < 0.4 ? "bottom" : ""} ${fx < 0.4 ? "left" : fx > 0.6 ? "right" : ""}`.trim() || "middle";
}

function draftsHtml() {
  const P = pending(), D = S.drafts[S.id];
  if (!D) return "";
  const done = (D.labels || []).length - P.length;
  if (!P.length) return (D.labels || []).length ? `<p class="small muted">All ${(D.labels || []).length} drafts for this hall have been accepted or removed.</p>` : "";
  const order = { area: 0, route: 1, point: 2 };
  return `<h3>Drafts from the replays <span class="muted small">(${P.length} to review${done ? `, ${done} done` : ""}; from ${D.replays} stored replays)</span>
    <button class="btn small" data-accept-all style="margin-left:.6rem">Accept all ${P.length}</button></h3>
  <p class="small muted">Guesses made from where players walked, fought, and came back to life. Point at a row to pick it out on the map. Accept keeps it as your label; Remove discards it. Either way nothing is saved until you press Save labels. To change a shape, remove it and draw your own.${(D.notes || []).length ? ` <b>Gaps:</b> ${esc(D.notes.join("; "))}.` : ""}</p>
  <div class="tablewrap"><table class="data"><thead><tr><th>Kind</th><th>Type</th><th>Where</th><th>What it rests on</th><th></th></tr></thead><tbody>
  ${[...P].sort((a, b) => order[a.kind] - order[b.kind] || a.type.localeCompare(b.type)).map((d) => `<tr data-draft="${esc(d.id)}"><td>${d.kind === "point" ? "Point" : d.kind === "area" ? "Area" : "Route"}</td><td>${esc(d.type)}</td><td>${whereOn(d.kind === "route" ? [d.pts[0]] : d.pts)}</td>
    <td class="small" style="white-space:normal">${esc(d.how)}</td><td><button class="btn small" data-accept>Accept</button> <button class="btn small ghost danger" data-dismiss>Remove</button></td></tr>`).join("")}
  </tbody></table></div>`;
}

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
  if (!S.labels[id]) {
    const mine = await readJson(`data/maps/labels/${id}.json`, { labels: [] });
    S.labels[id] = mine.labels || []; S.dismissed[id] = new Set(mine.dismissed || []);
  }
  if (!(id in S.drafts)) S.drafts[id] = await fetch(`data/maps/draft/${id}.json`, { cache: "no-cache" }).then((r) => (r.ok ? r.json() : null)).catch(() => null);
  S.view = fitView(S.outline);
  const mine = S.labels[id];
  S.show = { areas: true, routes: true, points: true, drafts: true, replay: !mine.length && !pending().length, npc: !mine.some((l) => l.kind === "point" && ["Footman", "Archer", "Knight", "Bodyguard", "Guild Lord"].includes(l.type)) };
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
  <p class="small muted" style="margin:.3rem 0 0">A number is how many labels a hall has; * means unsaved changes.</p>
  <p class="small muted" style="margin:.6rem 0">${esc(hall.map)}: ${hall.replays} stored replays. ${o.source === "gvg.report" ? "Outline: gvg.report's walkable area." : `gvg.report publishes no outline for this hall, so the shape is where players walked in the stored replays; corners nobody visited are missing.`}
    <a href="${esc(hall.wiki)}" target="_blank" rel="noopener">Open the wiki page for this hall</a> to compare with its map.</p>
  <div class="row" style="margin:.4rem 0">${MODES.map(([m, t]) => `<button class="btn small${S.mode === m ? " primary" : ""}" data-mode="${m}">${t}</button>`).join("")}
    ${types.length ? `<select data-type aria-label="Type">${types.map((t) => `<option>${esc(t)}</option>`).join("")}</select>` : ""}
    ${S.mode === "area" || S.mode === "route" ? `<button class="btn small" data-finish${S.draft.length >= need ? "" : " disabled"}>Finish (${S.draft.length} point${S.draft.length === 1 ? "" : "s"})</button><button class="btn small ghost" data-undo${S.draft.length ? "" : " disabled"}>Undo last point</button>` : ""}
    <button class="btn small ghost" data-fit style="margin-left:auto">Whole map</button></div>
  <div class="row small" style="margin:.2rem 0;gap:1rem"><span class="muted">Show:</span>${[["areas", "Areas"], ["routes", "Routes"], ["points", "Points"], ["drafts", "Drafts"], ["replay", "Stand, starts, and spawns from the replays"], ["npc", "Estimated NPCs"]].map(([k, t]) => `<label><input type="checkbox" data-show="${k}"${S.show[k] ? " checked" : ""}> ${t}</label>`).join("")}</div>
  <p class="small muted" style="margin:.2rem 0 .5rem">${S.mode === "move" ? "Drag to move, scroll to zoom." : S.mode === "point" ? "Pick a type, then click the map to place it. Drag still moves the map." : S.mode === "area" ? "Pick a type, click each corner in turn, then Finish. Drag still moves the map." : "Pick a type, click along the path from start to end, then Finish. Drag still moves the map."} <span data-xy></span></p>
  <svg class="mp-svg" role="img" aria-label="Map of ${esc(hall.map)}"><defs><clipPath id="mp-clip"><path d="${outlinePath(o)}"/></clipPath></defs><path d="${outlinePath(o)}" class="mp-land"/><g id="mp-over"></g></svg>
  <div data-legend>${legendHtml()}</div>
  <p class="small muted">Areas are drawn only where the hall is walkable, with the smaller area on top where two overlap. A route starts at its dot and ends at its arrow. NPC estimates come from where attackers stood when they hit that NPC, so an NPC that walks out to fight shows as several spots.</p>
  <div data-drafts>${draftsHtml()}</div>
  <h3>Labels on ${esc(hall.map)} <button class="btn small primary" data-save${S.dirty.has(S.id) ? "" : " disabled"} style="margin-left:.6rem">Save labels</button></h3>
  <div data-list>${listHtml()}</div>
  <style>.mp-svg{width:100%;height:min(74vh,820px);border:1px solid var(--line);background:#fbfbfa;touch-action:none;cursor:${S.mode === "move" ? "grab" : "crosshair"};user-select:none}
  .mp-land{fill:#dfdfd8;stroke:#dfdfd8;stroke-width:1;vector-effect:non-scaling-stroke}.mp-svg text{fill:var(--ink-2);font-family:var(--sans);pointer-events:none;paint-order:stroke;stroke:#fbfbfa;stroke-width:.25em}
  .mp-svg text.mp-label-t{fill:var(--ink);font-weight:600}.mp-svg text.mp-draft-t{fill:var(--muted);font-style:italic}.mp-svg text.mp-area-t{font-weight:600;text-transform:uppercase;letter-spacing:.05em;filter:brightness(.5);stroke-width:.2em}.mp-svg text.mp-route-t{font-weight:600;filter:brightness(.8)}
  .mp-draft{fill:none;stroke:var(--bad)}.mp-draft-pt{fill:var(--bad)}.mp-legend{gap:1rem;margin:.35rem 0}.mp-legend b{min-width:5.5rem;font-weight:600}.mp-legend i{display:inline-block;width:.8rem;height:.8rem;margin-right:.35rem;vertical-align:-1px}
  .mp-legend i.mp-line{height:0;width:1.3rem;vertical-align:.25rem;background:none}.mp-legend i.mp-hollow{background:none;border:2px solid}.mp-legend svg{vertical-align:-2px;margin-right:.3rem}.mp-halls{gap:.4rem}.small{font-size:.86rem}</style>`;

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
  out.querySelectorAll("[data-show]").forEach((c) => c.onchange = () => { S.show[c.dataset.show] = c.checked; overlay(svg); out.querySelector("[data-legend]").innerHTML = legendHtml(); });
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
  const accept = (d) => (S.labels[S.id] ||= []).push({ id: uid(), kind: d.kind, type: d.type, name: "", note: "", pts: d.pts, from_draft: d.id });
  out.querySelectorAll("[data-draft]").forEach((tr) => {
    const d = pending().find((x) => x.id === tr.dataset.draft);
    tr.onmouseenter = () => { S.hot = d.id; overlay(svg); };
    tr.onmouseleave = () => { S.hot = null; overlay(svg); };
    tr.querySelector("[data-accept]").onclick = () => { S.hot = null; accept(d); touch(); };
    tr.querySelector("[data-dismiss]").onclick = () => { S.hot = null; (S.dismissed[S.id] ||= new Set()).add(d.id); touch(); };
  });
  out.querySelector("[data-accept-all]")?.addEventListener("click", () => { for (const d of pending()) accept(d); touch(); });
  out.querySelector("[data-save]").onclick = async () => {
    try {
      await writeJson(`data/maps/labels/${S.id}.json`, { map_id: S.id, map: hall.map, labels: S.labels[S.id] || [], dismissed: [...(S.dismissed[S.id] || [])] }, `Map labels: ${hall.map}`);
      S.dirty.delete(S.id); toast("Saved"); renderMaps(out);
    } catch (e) { toast(e.message); }
  };
}
