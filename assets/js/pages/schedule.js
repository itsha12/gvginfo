import { esc } from "../core.js";
import * as S from "../schedule.js";

const PREF = "gvginfo.schedule";
const pref = () => { try { return JSON.parse(localStorage.getItem(PREF)) || {}; } catch { return {}; } };
const savePref = (p) => { try { localStorage.setItem(PREF, JSON.stringify(p)); } catch { /* storage blocked */ } };
let offsetMonths = 0;
let timer = null;

export function renderSchedule(view) {
  clearInterval(timer);
  const p = { showB: false, utc: false, ...pref() };
  const zone = p.utc ? "UTC" : S.SERVER_ZONE;
  const slots = p.showB ? ["A", "B", "C"] : ["A", "C"];
  const now = Date.now();
  const lp = S.localParts(now);
  const ym = new Date(Date.UTC(lp.y, lp.mo - 1 + offsetMonths, 1));
  const y = ym.getUTCFullYear(), mo = ym.getUTCMonth() + 1;
  const monthStart = S.zonedToUtc(y, mo, 1, 0, 0, S.LOCAL_ZONE);
  const monthEnd = S.zonedToUtc(mo === 12 ? y + 1 : y, mo === 12 ? 1 : mo + 1, 1, 0, 0, S.LOCAL_ZONE);
  const events = S.atEvents(monthStart, monthEnd, slots, zone);
  const upcoming = S.atEvents(now, now + 3 * 86400000, ["A", "C"], zone);
  const next = (slot) => upcoming.find((e) => e.slot === slot);
  const mat = S.nextMat(now, zone);
  const rotNow = S.rotationFor(now), rotMonth = S.rotationFor(monthStart + 86400000 * 2);
  const nextMonthMs = S.zonedToUtc(lp.mo === 12 ? lp.y + 1 : lp.y, lp.mo === 12 ? 1 : lp.mo + 1, 2, 12, 0, S.LOCAL_ZONE);
  // look a few weeks either side so a clock gap that spans the month boundary gets its real start and end
  const gaps = S.gapChanges(monthStart - 21 * 86400000, monthEnd + 21 * 86400000, zone)
    .map((g, i, all) => ({ ...g, end: all[i + 1]?.at ?? null }))
    .filter((g) => g.at < monthEnd && (g.end ?? Infinity) > monthStart);
  const monthName = S.fmtDate(monthStart + 86400000 * 2, S.LOCAL_ZONE, { month: "long", year: "numeric" });

  // group events by Toronto date
  const days = new Map();
  for (const e of events) {
    const key = S.fmtDate(e.at, S.LOCAL_ZONE, { year: "numeric", month: "2-digit", day: "2-digit" });
    (days.get(key) || days.set(key, { at: e.at, ev: {} }).get(key)).ev[e.slot] = e.at;
  }
  const todayKey = S.fmtDate(now, S.LOCAL_ZONE, { year: "numeric", month: "2-digit", day: "2-digit" });
  const cell = (at) => at == null ? `<td class="muted">—</td>` :
    `<td class="${at < now ? "muted" : ""}"><b>${esc(S.fmtTime(at))}</b> <span class="muted small">${esc(S.tzName(at, S.LOCAL_ZONE))}</span>
      <div class="muted small">${esc(S.fmtTime(at, zone))} ${p.utc ? "UTC" : "UK"}</div></td>`;
  const tile = (label, ms, sub = "") => `<div><span>${label}</span><b>${ms ? esc(S.fmtTime(ms)) : "—"}</b>
    <span>${ms ? `${esc(S.fmtDate(ms))} · in <span data-countdown="${ms}">${S.countdown(ms, now)}</span>` : ""}${sub}</span></div>`;
  const unusual = gaps.filter((g) => g.gap !== 5);

  view.innerHTML = `
    <h2>Schedule</h2>
    <p class="lede">Automated tournament start times in Toronto time. The server keeps UK time, so these follow both the UK and
      Ontario daylight-saving changes automatically. Register within the hour before the start.</p>
    <div class="stats sched-tiles">
      <div><span>Current flux</span><b class="flux">${esc(S.fluxFor(now))}</b><span>${esc(S.FLUX[(new Date(S.nextFluxChange(now)).getUTCMonth()) % 12])} from ${esc(S.fmtDate(S.nextFluxChange(now)))}, ${esc(S.fmtTime(S.nextFluxChange(now)))}</span></div>
      ${tile("Next AT-A", next("A")?.at)}
      ${tile("Next AT-C", next("C")?.at)}
      ${tile("Next monthly (mAT)", mat)}
    </div>

    <div class="sched-grid">
      <section>
        <div class="row" style="justify-content:space-between;align-items:baseline">
          <h3 style="margin:2rem 0 1rem">${esc(monthName)}</h3>
          <div class="row">
            <button class="btn small" id="prev" aria-label="Previous month">←</button>
            ${offsetMonths ? `<button class="btn small" id="this">This month</button>` : ""}
            <button class="btn small" id="next" aria-label="Next month">→</button>
          </div>
        </div>
        ${unusual.length ? `<p class="callout">${unusual.map((g) => {
          const end = g.end;
          return `From ${esc(S.fmtDate(g.at))}${end ? ` until ${esc(S.fmtDate(end))}` : ""} the UK is ${g.gap} hours ahead of Toronto instead of 5
            (one country has changed its clocks and the other hasn't), so tournaments start ${g.gap < 5 ? "an hour later" : "an hour earlier"} for you than usual.`;
        }).join(" ")}</p>` : ""}
        <div class="scroll"><table class="data sched">
          <thead><tr><th>Day (Toronto)</th>${slots.map((s) => `<th>AT-${s}</th>`).join("")}</tr></thead>
          <tbody>${[...days.entries()].map(([key, d]) => `<tr class="${key === todayKey ? "today" : ""}${d.at < now - 86400000 ? " past" : ""}">
            <td><b>${esc(S.fmtDate(d.at))}</b>${key === todayKey ? ` <span class="pill type">Today</span>` : ""}</td>
            ${slots.map((s) => cell(d.ev[s])).join("")}</tr>`).join("")}</tbody>
        </table></div>
      </section>
      <aside>
        <h3 style="margin-top:2rem">Map rotation, ${esc(S.fmtDate(monthStart + 86400000 * 2, S.LOCAL_ZONE, { month: "long" }))}</h3>
        <ol class="rotation">${rotMonth.map((m) => `<li><span class="label">Round ${rotMonth.indexOf(m) + 1}</span>${esc(m)}</li>`).join("")}</ol>
        ${offsetMonths === 0 ? `<h3>Next month</h3>
        <ol class="rotation small">${S.rotationFor(nextMonthMs).map((m) => `<li>${esc(m)}</li>`).join("")}</ol>
        <p class="muted small">Flux next month: <b>${esc(S.fluxFor(nextMonthMs + 86400000))}</b></p>` : ""}
        <h3>Options</h3>
        <label class="check"><input type="checkbox" id="showB" ${p.showB ? "checked" : ""}> Show AT-B</label>
        <label class="check"><input type="checkbox" id="utc" ${p.utc ? "checked" : ""}> Treat the schedule as UTC instead of UK time</label>
        <p class="muted small">Times are confirmed against gvg.report's recorded October 2026 start times. If the late-October
          week looks an hour off in game, tick the UTC box and tell Claude so it can be fixed for good.</p>
        <p class="muted small">Sources: Guild Wars Wiki (weekday times and rotation), gvg.report (flux and observed starts).
          Map rotation changes at midnight UTC on the 1st; flux at 07:00 UTC.</p>
      </aside>
    </div>`;

  view.querySelector("#prev").onclick = () => { offsetMonths--; renderSchedule(view); };
  view.querySelector("#next").onclick = () => { offsetMonths++; renderSchedule(view); };
  view.querySelector("#this")?.addEventListener("click", () => { offsetMonths = 0; renderSchedule(view); });
  view.querySelector("#showB").onchange = (e) => { savePref({ ...p, showB: e.target.checked }); renderSchedule(view); };
  view.querySelector("#utc").onchange = (e) => { savePref({ ...p, utc: e.target.checked }); renderSchedule(view); };
  // keep the countdowns live while the page is open
  timer = setInterval(() => {
    if (!document.body.contains(view.querySelector("[data-countdown]"))) { clearInterval(timer); return; }
    view.querySelectorAll("[data-countdown]").forEach((el) => { el.textContent = S.countdown(+el.dataset.countdown); });
    if ([...view.querySelectorAll("[data-countdown]")].some((el) => +el.dataset.countdown < Date.now())) renderSchedule(view);
  }, 30000);
}
