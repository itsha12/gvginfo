// Match report (prototype): one match drawn from its report file, never saved. Opened as #/report/<match id>.
// The prototype reads data/report_proto/<id>.json, built from the files already on main; the real page will read the
// per-match file the exporter writes after each full run.
import { esc, skillBar } from "../core.js";

const clock = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;
const COL = ["#1f5fd1", "#b35c00"]; // first team, second team
let cut = 5;

export async function renderReport(view, [rid] = []) {
  if (!rid) { view.innerHTML = `<h2>Match report</h2><p class="lede">Open a report from Recent matches or a guild's results.</p>`; return; }
  const r = await fetch(`data/report_proto/${encodeURIComponent(rid.slice(0, 8))}.json`, { cache: "no-cache" }).then((x) => (x.ok ? x.json() : null)).catch(() => null);
  if (!r) { view.innerHTML = `<h2>Match report</h2><p class="lede">No report file for this match yet.</p>`; return; }
  const [A, B] = r.teams;
  const col = (tag) => (tag === A.tag ? COL[0] : COL[1]);
  const replay = (t) => `<a href="https://gvg.report/report/${esc(r.rid)}#map" target="_blank" rel="noopener">replay at ${clock(t)} ↗</a>`;

  const lineup = (t, i) => `<section class="rp-team">
      <h3><span class="rp-dot" style="background:${COL[i]}"></span>${esc(t.tag)} <span class="muted">${esc(t.guild)}</span></h3>
      <table class="rp-lineup">${t.players.map((p) => `<tr><td class="muted">${p.pos}</td><td class="rp-role">${esc(p.role || `${p.p}/${p.s}`)}</td>
        <td>${skillBar(p.bar, null, true)}</td><td class="muted rp-d">${p.deaths ?? ""}${p.deaths != null ? " d" : ""}</td></tr>`).join("")}</table></section>`;

  const deathLine = (d) => `<li><details><summary><b>${clock(d.t)}</b> ${esc(d.lines[0].replace(/^\d+:\d+ /, ""))}</summary>${d.lines.slice(1).map((l) => `<p>${esc(l)}</p>`).join("") || `<p class="muted">No missed chance read.</p>`}</details></li>`;

  const card = (mo, n) => `<article class="rp-card" style="border-left-color:${col(mo.team)}">
      <header><span class="rp-num" style="border-color:${col(mo.team)}">${n}</span>
        <b>${clock(mo.t)} · Flag: ${/Run again, or not/.test(mo.head) ? "run again, or not" : "answer to a run"} · ${esc(mo.team)} decides</b>
        <span class="rp-swing">${esc(A.tag)} ${mo.a_before}% → ${mo.a_after}%</span>${replay(mo.t)}</header>
      <p class="rp-lead">${esc(mo.head)}</p>
      <p class="muted">${esc(mo.spot.charAt(0).toUpperCase() + mo.spot.slice(1))}</p>
      <p><span class="muted">What ${esc(mo.team)} did:</span> ${esc(mo.answer)}</p>
      <p><span class="muted">What followed:</span> ${esc(mo.followed.replace(/^What followed, /, ""))}</p>
      ${mo.deaths.length ? `<h4>Deaths in this window</h4><ul class="rp-deaths">${mo.deaths.map((i) => deathLine(r.deaths[i])).join("")}</ul>` : `<p class="muted">No deaths in this window.</p>`}
      <div class="rp-alt"><h4>Alternatives from similar spots <span class="muted">(a reading, not advice yet)</span></h4>
        <p>${esc(mo.similar.replace(/^Similar spots, /, ""))}</p></div>
    </article>`;

  const draw = () => {
    const key = r.moments.filter((m) => Math.abs(m.swing) >= cut).sort((a, b) => a.t - b.t);
    const rest = r.moments.filter((m) => Math.abs(m.swing) < cut);
    // win chance line from the moments' before and after points (the real file carries the whole series)
    const pts = r.moments.flatMap((m) => [[m.t, m.a_before], [Math.min(m.t + 180, r.dur), m.a_after]]).sort((a, b) => a[0] - b[0]);
    const W = 900, H = 170, X = (t) => 40 + (t / r.dur) * (W - 60), Y = (v) => 10 + (1 - v / 100) * (H - 40);
    const line = pts.map(([t, v]) => `${X(t).toFixed(1)},${Y(v).toFixed(1)}`).join(" ");
    const chart = `<svg viewBox="0 0 ${W} ${H}" class="rp-chart" role="img" aria-label="${esc(A.tag)}'s chance of winning over the match">
      <rect x="40" y="10" width="${W - 60}" height="${(H - 40) / 2}" fill="${COL[0]}" opacity=".07"/>
      <rect x="40" y="${10 + (H - 40) / 2}" width="${W - 60}" height="${(H - 40) / 2}" fill="${COL[1]}" opacity=".07"/>
      <line x1="40" x2="${W - 20}" y1="${Y(50)}" y2="${Y(50)}" stroke="#999" stroke-dasharray="3 3"/>
      <text x="4" y="${Y(50) + 4}" class="rp-ax">50%</text><text x="4" y="${Y(100) + 10}" class="rp-ax" fill="${COL[0]}">${esc(A.tag)}</text>
      <text x="4" y="${Y(0)}" class="rp-ax" fill="${COL[1]}">${esc(B.tag)}</text>
      <polyline points="${line}" fill="none" stroke="#111" stroke-width="1.6"/>
      ${key.map((m, i) => `<g><circle cx="${X(m.t)}" cy="${Y(m.a_before)}" r="9" fill="#fff" stroke="${col(m.team)}" stroke-width="2"/>
        <text x="${X(m.t)}" y="${Y(m.a_before) + 4}" text-anchor="middle" class="rp-ax">${i + 1}</text></g>`).join("")}
      <text x="40" y="${H - 6}" class="rp-ax">0:00</text><text x="${W - 20}" y="${H - 6}" text-anchor="end" class="rp-ax">${clock(r.dur)}</text></svg>`;
    view.querySelector("#rp-chart").innerHTML = chart;
    view.querySelector("#rp-cutv").textContent = `${cut} points`;
    view.querySelector("#rp-key").innerHTML = key.length ? key.map((m, i) => card(m, i + 1)).join("") : `<p class="muted">No moment moved the win chance by ${cut} points or more.</p>`;
    view.querySelector("#rp-rest").innerHTML = `<summary>Other moments (${rest.length + r.other_moments.length})</summary>
      ${rest.map((m) => `<p><b>${clock(m.t)}</b> ${esc(m.head)} <span class="muted">${esc(A.tag)} ${m.a_before}% → ${m.a_after}%</span></p>`).join("")}
      ${r.other_moments.map((m) => `<p><b>${clock(m.t)}</b> <span class="muted">${esc(m.kind)}:</span> ${esc(m.reads)} <span class="muted">(win chance not in the prototype's files)</span></p>`).join("")}`;
  };

  view.innerHTML = `
    <p class="callout">Prototype: built from the flag cards and death rows already on the site for this graded game. The real report reads the engine's file for the match, with the win chance over the whole match and every family's moments.</p>
    <div class="rp-head"><div><h2>${esc(A.tag)} v ${esc(B.tag)}</h2>
      <p class="lede">${esc(A.guild)} v ${esc(B.guild)} · ${esc(r.map)} · ${esc(r.occ)} · ${esc(r.date)} · ${clock(r.dur)}</p></div>
      <span class="rp-result">${esc(r.result)}</span></div>
    <div class="rp-metrics">
      <div><span class="muted">Chance of winning at the start</span><b>${r.start_chance ? `${esc(A.tag)} ${r.start_chance}% · ${esc(B.tag)} ${100 - r.start_chance}%` : "from the engine's file"}</b></div>
      <div><span class="muted">Deaths</span><b>${esc(A.tag)} ${A.deaths} · ${esc(B.tag)} ${B.deaths}</b></div></div>
    <div class="rp-teams">${lineup(A, 0)}${lineup(B, 1)}</div>
    <h3 class="rp-h">${esc(A.tag)}'s chance of winning over the match</h3>
    <div id="rp-chart"></div>
    <div class="rp-cut"><label for="rp-cutr">Key moments: win chance moved by at least</label>
      <input type="range" id="rp-cutr" min="0" max="25" step="1" value="${cut}"><span id="rp-cutv"></span></div>
    <div id="rp-key"></div>
    ${r.lone_deaths.length ? `<h3 class="rp-h">Deaths outside the key moments</h3><ul class="rp-deaths">${r.lone_deaths.map((i) => deathLine(r.deaths[i])).join("")}</ul>` : ""}
    <details id="rp-rest" class="rp-rest"></details>`;
  view.querySelector("#rp-cutr").addEventListener("input", (e) => { cut = +e.target.value; draw(); });
  draw();
}
