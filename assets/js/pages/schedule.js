import { esc } from "../core.js";
import * as S from "../schedule.js";

let offsetMonths = 0;
let timer = null;

export function renderSchedule(view) {
  clearInterval(timer);
  const slots = ["A", "C"];
  const now = Date.now();
  const lp = S.localParts(now);
  const ym = new Date(Date.UTC(lp.y, lp.mo - 1 + offsetMonths, 1));
  const y = ym.getUTCFullYear(), mo = ym.getUTCMonth() + 1;
  const monthStart = S.zonedToUtc(y, mo, 1, 0, 0, S.LOCAL_ZONE);
  const monthEnd = S.zonedToUtc(mo === 12 ? y + 1 : y, mo === 12 ? 1 : mo + 1, 1, 0, 0, S.LOCAL_ZONE);
  const events = S.atEvents(monthStart + 6 * 3600000, monthEnd + 6 * 3600000, slots); // evening rows (see below)
  const upcoming = S.atEvents(now, now + 3 * 86400000, slots);
  const next = (slot) => upcoming.find((e) => e.slot === slot);
  const midMonth = monthStart + 14 * 86400000;
  const rotMonth = S.rotationFor(midMonth);
  const nextMonthMs = Date.UTC(lp.y, lp.mo, 15);
  const monthName = S.fmtDate(midMonth, S.LOCAL_ZONE, { month: "long", year: "numeric" });
  const fluxChange = S.nextFluxChange(now);

  // Rows by "evening": a start between midnight and 6 a.m. stays on the previous day's row (12:00 a.m. Friday is
  // listed under Thursday), so each day has one AT-A and one AT-C.
  const EVENING_SHIFT = 6 * 3600000;
  const dayOf = (at) => S.fmtDate(at - EVENING_SHIFT, S.LOCAL_ZONE, { year: "numeric", month: "2-digit", day: "2-digit" });
  const days = new Map();
  for (const e of events) {
    const key = dayOf(e.at);
    ((days.get(key) || days.set(key, { at: e.at - EVENING_SHIFT, ev: {} }).get(key)).ev[e.slot] ||= []).push(e.at);
  }
  const todayKey = dayOf(now);
  // a Toronto day can hold two AT-A starts (just after midnight and late evening)
  const cell = (list) => !list?.length ? `<td class="muted">—</td>` : `<td>${list.map((at) =>
    `<div class="${at < now ? "muted" : ""}" style="margin-bottom:.3rem"><b>${esc(S.fmtTime(at))}</b> <span class="muted small">${esc(S.tzName(at, S.LOCAL_ZONE))}</span>
</div>`).join("")}</td>`;
  const tile = (label, ms) => `<div><span>${label}</span><b>${ms ? esc(S.fmtTime(ms)) : "—"}</b>
    <span>${ms ? `${esc(S.fmtDate(ms - EVENING_SHIFT))} · in <span data-countdown="${ms}">${S.countdown(ms, now)}</span>` : ""}</span></div>`;

  view.innerHTML = `
    <h2>Schedule</h2>
    <p class="lede">Automated tournament start times in Eastern time. A start just after midnight is listed on the evening
      before it. Register within the hour before the start.</p>
    <div class="stats sched-tiles">
      <div><span>Current flux</span><b class="flux">${esc(S.fluxFor(now))}</b><span>${esc(S.fluxFor(fluxChange + 3600000))} from ${esc(S.fmtDate(fluxChange))}, ${esc(S.fmtTime(fluxChange))}</span></div>
      ${tile("Next AT-A", next("A")?.at)}
      ${tile("Next AT-C", next("C")?.at)}
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
        <div class="scroll"><table class="data sched">
          <thead><tr><th>Day</th>${slots.map((s) => `<th>AT-${s}</th>`).join("")}</tr></thead>
          <tbody>${[...days.entries()].map(([key, d]) => `<tr class="${key === todayKey ? "today" : ""}${d.at < now - 86400000 ? " past" : ""}">
            <td><b>${esc(S.fmtDate(d.at))}</b>${key === todayKey ? ` <span class="pill type">Today</span>` : ""}</td>
            ${slots.map((s) => cell(d.ev[s])).join("")}</tr>`).join("")}</tbody>
        </table></div>
      </section>
      <aside>
        <h3 style="margin-top:2rem">Map rotation, ${esc(S.fmtDate(midMonth, S.LOCAL_ZONE, { month: "long" }))}</h3>
        <ol class="rotation">${rotMonth.map((m, i) => `<li><span class="label">Round ${i + 1}</span>${esc(m)}</li>`).join("")}</ol>
        ${offsetMonths === 0 ? `<h3>Next month</h3>
        <ol class="rotation small">${S.rotationFor(nextMonthMs).map((m) => `<li>${esc(m)}</li>`).join("")}</ol>
        <p class="muted small">Flux next month: <b>${esc(S.fluxFor(nextMonthMs))}</b></p>` : ""}
        <p class="muted small" style="margin-top:2rem">Source: Guild Wars Wiki —
          <a href="https://wiki.guildwars.com/wiki/Automated_tournament" target="_blank" rel="noopener">Automated tournament</a> (start times in UTC, map rotation) and
          <a href="https://wiki.guildwars.com/wiki/Flux" target="_blank" rel="noopener">Flux</a> (changes on the 1st at 07:00 UTC).</p>
      </aside>
    </div>`;

  view.querySelector("#prev").onclick = () => { offsetMonths--; renderSchedule(view); };
  view.querySelector("#next").onclick = () => { offsetMonths++; renderSchedule(view); };
  view.querySelector("#this")?.addEventListener("click", () => { offsetMonths = 0; renderSchedule(view); });
  // keep the countdowns live while the page is open
  timer = setInterval(() => {
    if (!document.body.contains(view.querySelector("[data-countdown]"))) { clearInterval(timer); return; }
    view.querySelectorAll("[data-countdown]").forEach((el) => { el.textContent = S.countdown(+el.dataset.countdown); });
    if ([...view.querySelectorAll("[data-countdown]")].some((el) => +el.dataset.countdown < Date.now())) renderSchedule(view);
  }, 30000);
}
