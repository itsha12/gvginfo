// Match report (prototype): one match drawn from its report file, never saved. Opened as #/report/<match id>.
// The prototype reads data/report_proto/<id>.json, built from the files already on main plus the match's replay; the
// real page will read the per-match file the exporter writes after each full run.
import { esc, skillBar } from "../core.js";

const clock = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;
const SIDE = { blue: "#1f5fd1", red: "#c62828" };
const MISSED = { prot: "prots", heal: "heals", interrupt: "interrupts" };
let cut = 5;

export async function renderReport(view, [rid] = []) {
  if (!rid) { view.innerHTML = `<h2>Match report</h2><p class="lede">Open a report from Recent matches or a guild's results.</p>`; return; }
  const r = await fetch(`data/report_proto/${encodeURIComponent(rid.slice(0, 8))}.json`, { cache: "no-cache" }).then((x) => (x.ok ? x.json() : null)).catch(() => null);
  if (!r) { view.innerHTML = `<h2>Match report</h2><p class="lede">No report file for this match yet.</p>`; return; }
  const [A, B] = r.teams;
  const C = { [A.tag]: SIDE[A.side], [B.tag]: SIDE[B.side] };
  const named = (t) => `${esc(t.guild)} [${esc(t.tag)}]`;
  const pc = (v) => `${v > 0 ? "+" : ""}${v}%`;

  const lineup = (t) => `<section class="rp-team">
      <h3><span class="rp-dot" style="background:${C[t.tag]}"></span>${named(t)}</h3>
      <table class="rp-lineup">${t.players.map((p) => `<tr><td class="muted">${p.pos}</td>
        <td class="rp-role"><b>${esc(p.name)}</b><br><span class="muted">${esc(p.build || `${p.p}/${p.s}`)}</span></td>
        <td>${skillBar(p.bar, null, true)}</td><td class="muted rp-d">${p.deaths ?? ""}${p.deaths != null ? " d" : ""}</td></tr>`).join("")}</table></section>`;

  // one death: a line that opens into the full breakdown
  const death = (d) => `<li><details><summary><b>${clock(d.t)}</b> ${esc(d.team)}'s ${esc(d.who)} dies ${d.spike ? "to a spike" : "under pressure"}:
        ${d.dmg} in ${d.dur} s. ${d.missed.length ? `<span class="rp-fault">Missed: ${d.missed.map((k) => MISSED[k] || k).join(", ")}</span>` : `<span class="muted">No missed chance.</span>`}
        <span class="rp-swing">win chance: engine file</span></summary>
      <div class="rp-break">
        <p><span class="muted">Player:</span> ${esc(d.name)} (${esc(d.who)})</p>
        <p><span class="muted">Damage:</span> ${d.dmg} from the first big hit at ${clock(d.first)} to death at ${clock(d.t)} (${d.dur} s), by ${esc(d.by)}</p>
        ${d.breakdown.map((l) => `<p>${esc(l.replace(/^Missed by \w+, /, "Missed: "))}</p>`).join("")}
        ${d.notes.map((l) => `<p class="muted">${esc(l)}</p>`).join("")}
        <p class="muted">Not read yet: shield set, Shadow Shroud on him, their monks disabled at the spike.</p></div></details></li>`;

  const card = (mo, n) => {
    const lead1 = mo.lead_change == null ? null : +(mo.lead0 + mo.lead_change).toFixed(2);
    const leadTxt = (v) => (v === 0 ? "level" : `${v > 0 ? mo.team : mo.foe} +${Math.abs(v).toFixed(2)}`);
    return `<article class="rp-card" style="border-left-color:${C[mo.team]}">
      <header><span class="rp-num" style="border-color:${C[mo.team]};color:${C[mo.team]}">${n}</span>
        <b>${clock(mo.t)} · Flag: ${esc(mo.scenario)} · ${esc(mo.team)} decides</b></header>
      <p class="rp-lead">${esc(mo.event)}</p>
      <dl class="rp-dl">
        <dt>Flag situation</dt><dd>${/^Run again/.test(mo.stand) ? "" : esc(mo.stand.replace(/, boost in (\d+) s\./, ". Boost in $1 s.")) + " "}${esc(mo.flags)}.</dd>
        <dt>Main fight</dt><dd>${esc(mo.fight)} (${esc(mo.fight_up)})<br>${mo.places.map(esc).join("<br>")}</dd>
        <dt>Morale</dt><dd>${esc(mo.team)} ${pc(mo.morale[mo.team])}; ${esc(mo.foe)} ${pc(mo.morale[mo.foe])}</dd>
        <dt>Base res</dt><dd>in ${mo.base_res} s</dd>
        <dt>Decision</dt><dd><b>${esc(mo.decision)}</b></dd>
        <dt>Result, 180 s on</dt><dd><ul class="rp-res">
          ${mo.result.map((x) => `<li>${esc(x)}</li>`).join("")}
          ${lead1 == null ? "" : `<li>Flag lead: ${esc(leadTxt(mo.lead0))} → ${esc(leadTxt(lead1))} <span class="muted">(a flag in hand counts towards the tally)</span></li>`}
          ${mo.deaths_n ? `<li>Deaths in window: ${esc(mo.deaths_n[0])} ${mo.deaths_n[1]}, ${esc(mo.deaths_n[2])} ${mo.deaths_n[3]}</li>` : ""}
          ${mo.boosts_n ? `<li>Boosts in window: ${esc(mo.boosts_n[0])} ${mo.boosts_n[1]}, ${esc(mo.boosts_n[2])} ${mo.boosts_n[3]}</li>` : ""}</ul></dd>
        <dt>Win chance</dt><dd><b>${esc(mo.team)} ${mo.chance[0]}% to ${mo.chance[1]}% (${mo.chance[2] > 0 ? "+" : ""}${mo.chance[2]} WP)</b></dd>
      </dl>
      ${mo.deaths.length ? `<h4>Deaths in this window</h4><ul class="rp-deaths">${mo.deaths.map((i) => death(r.deaths[i])).join("")}</ul>` : ""}
      <div class="rp-alt"><h4>Alternatives from similar spots <span class="muted">(a reading, not advice yet)</span></h4>
        <p>${esc(mo.similar)}</p></div>
    </article>`;
  };

  // the hall: gvg.report's walkable outline, the key moments where the deciding team stood, the deaths where they fell
  const hall = (key) => {
    const [x0, y0, x1, y1] = typeof r.outline.bounds === "string" ? JSON.parse(r.outline.bounds) : r.outline.bounds;
    const traps = typeof r.outline.traps === "string" ? JSON.parse(r.outline.traps) : r.outline.traps;
    const pad = 300, Y = (y) => -y, R = (x1 - x0) / 90;
    const d = traps.map(([a, b, yt, c, e, yb]) => `M${a} ${Y(yt)}L${b} ${Y(yt)}L${e} ${Y(yb)}L${c} ${Y(yb)}Z`).join("");
    const dot = (dd) => { const [x, y] = dd.at, col = C[dd.team]; return `<g><title>${clock(dd.t)} ${esc(dd.team)}'s ${esc(dd.who)} dies</title>
      <path d="M${x - R} ${Y(y) - R}L${x + R} ${Y(y) + R}M${x + R} ${Y(y) - R}L${x - R} ${Y(y) + R}" stroke="${col}" stroke-width="${R * 0.45}"/></g>`; };
    const mk = (mo, i) => mo.at ? `<g><circle cx="${mo.at[0]}" cy="${Y(mo.at[1])}" r="${R * 1.7}" fill="#fff" stroke="${C[mo.team]}" stroke-width="${R * 0.4}"/>
      <text x="${mo.at[0]}" y="${Y(mo.at[1]) + R * 0.75}" text-anchor="middle" font-size="${R * 2.1}" fill="${C[mo.team]}" font-weight="600">${i + 1}</text></g>` : "";
    return `<svg viewBox="${x0 - pad} ${Y(y1) - pad} ${x1 - x0 + 2 * pad} ${y1 - y0 + 2 * pad}" class="rp-map" role="img" aria-label="${esc(r.map)}: where the key moments and deaths happened">
      <path d="${d}" fill="#e9e9e5" stroke="#cfcfca" stroke-width="${R * 0.15}"/>
      ${r.deaths.map(dot).join("")}${key.map(mk).join("")}</svg>`;
  };

  const chart = (key) => {
    const pts = r.moments.flatMap((m) => [[m.t, m.a_before], [Math.min(m.t + 180, r.dur), m.a_after]]).sort((a, b) => a[0] - b[0]);
    const W = 1000, H = 220, L0 = 46, X = (t) => L0 + (t / r.dur) * (W - L0 - 20), Y = (v) => 12 + (1 - v / 100) * (H - 44), mid = Y(50);
    const ticks = []; for (let t = 0; t <= r.dur; t += 120) ticks.push(t);
    const first = pts[0];
    return `<svg viewBox="0 0 ${W} ${H}" class="rp-chart" role="img" aria-label="${esc(A.tag)}'s win chance over the match">
      <rect x="${L0}" y="${Y(100)}" width="${W - L0 - 20}" height="${mid - Y(100)}" fill="${C[A.tag]}" opacity=".07"/>
      <rect x="${L0}" y="${mid}" width="${W - L0 - 20}" height="${Y(0) - mid}" fill="${C[B.tag]}" opacity=".07"/>
      ${ticks.map((t) => `<line x1="${X(t)}" x2="${X(t)}" y1="${Y(100)}" y2="${Y(0)}" stroke="#000" opacity=".07"/><text x="${X(t)}" y="${H - 12}" text-anchor="middle" class="rp-ax">${clock(t)}</text>`).join("")}
      <line x1="${L0}" x2="${W - 20}" y1="${mid}" y2="${mid}" stroke="#888" stroke-dasharray="4 4"/>
      <text x="${L0 - 6}" y="${mid + 4}" text-anchor="end" class="rp-ax">50%</text>
      <text x="${L0 - 6}" y="${Y(100) + 10}" text-anchor="end" class="rp-ax" style="fill:${C[A.tag]}">${esc(A.tag)}</text>
      <text x="${L0 - 6}" y="${Y(0)}" text-anchor="end" class="rp-ax" style="fill:${C[B.tag]}">${esc(B.tag)}</text>
      <line x1="${X(0)}" x2="${X(first[0])}" y1="${Y(first[1])}" y2="${Y(first[1])}" stroke="#999" stroke-width="1.6" stroke-dasharray="3 4"/>
      <polyline points="${pts.map(([t, v]) => `${X(t).toFixed(1)},${Y(v).toFixed(1)}`).join(" ")}" fill="none" stroke="#111" stroke-width="2"/>
      ${r.deaths.map((d) => `<line x1="${X(d.t)}" x2="${X(d.t)}" y1="${Y(0) - 7}" y2="${Y(0)}" stroke="${C[d.team]}" stroke-width="2"><title>${clock(d.t)} ${esc(d.team)}'s ${esc(d.who)} dies</title></line>`).join("")}
      ${key.map((m, i) => `<g><circle cx="${X(m.t)}" cy="${Y(m.a_before)}" r="10" fill="#fff" stroke="${C[m.team]}" stroke-width="2"/>
        <text x="${X(m.t)}" y="${Y(m.a_before) + 4}" text-anchor="middle" class="rp-ax" style="fill:${C[m.team]};font-weight:600">${i + 1}</text></g>`).join("")}</svg>`;
  };

  const draw = () => {
    const key = r.moments.filter((m) => Math.abs(m.swing) >= cut).sort((a, b) => a.t - b.t);
    const rest = r.moments.filter((m) => Math.abs(m.swing) < cut);
    view.querySelector("#rp-chart").innerHTML = chart(key);
    view.querySelector("#rp-map").innerHTML = hall(key);
    view.querySelector("#rp-cutv").textContent = `${cut} WP`;
    view.querySelector("#rp-key").innerHTML = key.length ? key.map((m, i) => card(m, i + 1)).join("") : `<p class="muted">No moment moved the win chance by ${cut} WP or more.</p>`;
    view.querySelector("#rp-rest").innerHTML = `<summary>Other moments (${rest.length + r.other_moments.length})</summary>
      ${rest.map((m) => `<p><b>${clock(m.t)}</b> ${esc(m.event)} <span class="muted">${esc(m.team)} ${m.chance[0]}% to ${m.chance[1]}%</span></p>`).join("")}
      ${r.other_moments.map((m) => `<p><b>${clock(m.t)}</b> <span class="muted">${esc(m.kind)}:</span> ${esc(m.reads)}</p>`).join("")}`;
  };

  view.innerHTML = `
    <p class="callout">Prototype: built from the flag cards and death rows already on the site for this graded game, plus its replay. Still to come from the engine's own file: the initial win chance, the win chance line before the first flag moment, each death's change in win chance, and the other families' moments.</p>
    <div class="rp-head"><div><h2>[${esc(A.tag)}] v [${esc(B.tag)}]</h2>
      <p class="lede">${named(A)} v ${named(B)} · ${esc(r.map)} · ${esc(r.occ)} · ${esc(r.date)} · ${clock(r.dur)} ·
        <a href="https://gvg.report/report/${esc(r.rid)}" target="_blank" rel="noopener">GvG Report</a></p></div>
      <span class="rp-result">${esc(r.result)}</span></div>
    <div class="rp-metrics">
      <div><span class="muted">Initial Win Chance</span><b>${r.start_chance != null ? `${esc(A.tag)} ${r.start_chance}% · ${esc(B.tag)} ${100 - r.start_chance}%` : "from the engine's file"}</b></div>
      <div><span class="muted">Deaths</span><b>${esc(A.tag)} ${A.deaths} · ${esc(B.tag)} ${B.deaths}</b></div></div>
    <div class="rp-teams">${lineup(A)}${lineup(B)}</div>
    <div class="rp-cols"><div>
      <h3 class="rp-h">${esc(A.tag)}'s Win Chance</h3>
      <div id="rp-chart"></div>
      <p class="muted rp-note">Numbered circles are the key moments; ticks along the bottom are deaths, in the colour of the team that lost the player.</p>
      <div class="rp-cut"><label for="rp-cutr">Key moments: win chance moved by at least</label>
        <input type="range" id="rp-cutr" min="0" max="25" step="1" value="${cut}"><span id="rp-cutv"></span></div></div>
      <div><h3 class="rp-h">${esc(r.map)}</h3><div id="rp-map"></div>
      <p class="muted rp-note">Circles: where the deciding team stood at each key moment. Crosses: where each player died.</p></div></div>
    <div id="rp-key"></div>
    ${r.lone_deaths.length ? `<h3 class="rp-h">Deaths outside the key moments</h3><ul class="rp-deaths">${r.lone_deaths.map((i) => death(r.deaths[i])).join("")}</ul>` : ""}
    <details id="rp-rest" class="rp-rest"></details>`;
  view.querySelector("#rp-cutr").addEventListener("input", (e) => { cut = +e.target.value; draw(); });
  draw();
}
