// GvG tournament schedule, map rotation and flux.
// Sources (checked 2026-10-08): Guild Wars Wiki "Automated tournament" (weekday times, monthly map rotation),
// gvg.report (observed start times, flux list: changes at 07:00 UTC on the 1st, mAT third Saturday).
//
// The server runs on UK time, so tournament times are fixed on the UK clock and move for Toronto whenever the UK and
// Ontario are not both on (or both off) daylight saving time — late March and late October / early November.
// UK clock times below were confirmed against gvg.report's recorded October 2026 start times (BST).

export const SERVER_ZONE = "Europe/London";
export const LOCAL_ZONE = "America/Toronto";

// UK clock hour per weekday (0 = Sunday … 6 = Saturday, UK date).
export const AT_HOURS = {
  A: [3, 5, 4, 3, 4, 5, 4],
  B: [12, 14, 13, 12, 13, 14, 13],
  C: [19, 21, 20, 19, 20, 21, 20],
};
export const MAT = { weekday: 6, nth: 3, hour: 17 }; // third Saturday, 17:00 UK clock (16:00 UTC in summer)

export const MAP_ROTATION = [
  ["Isle of Weeping Stone", "Uncharted Isle", "Druid's Isle", "Burning Isle", "Warrior's Isle"],
  ["Isle of Wurms", "Isle of Jade", "Isle of Meditation", "Imperial Isle", "Druid's Isle"],
  ["Burning Isle", "Frozen Isle", "Warrior's Isle", "Isle of Solitude", "Uncharted Isle"],
  ["Isle of the Dead", "Isle of Solitude", "Imperial Isle", "Isle of Wurms", "Isle of Jade"],
  ["Isle of Wurms", "Imperial Isle", "Isle of Meditation", "Warrior's Isle", "Frozen Isle"],
  ["Isle of Weeping Stone", "Isle of Jade", "Warrior's Isle", "Uncharted Isle", "Imperial Isle"],
  ["Burning Isle", "Isle of Wurms", "Uncharted Isle", "Nomad's Isle", "Isle of Solitude"],
  ["Isle of the Dead", "Warrior's Isle", "Corrupted Isle", "Frozen Isle", "Isle of Meditation"],
  ["Isle of Solitude", "Druid's Isle", "Corrupted Isle", "Isle of Weeping Stone", "Uncharted Isle"],
  ["Isle of Meditation", "Uncharted Isle", "Isle of Jade", "Isle of Solitude", "Isle of the Dead"],
  ["Corrupted Isle", "Imperial Isle", "Nomad's Isle", "Isle of Meditation", "Isle of Jade"],
  ["Burning Isle", "Druid's Isle", "Warrior's Isle", "Uncharted Isle", "Frozen Isle"],
];
export const FLUX = ["Odran's Razor", "Amateur Hour", "Hidden Talent", "There Can Be Only One", "Meek Shall Inherit",
  "Jack of All Trades", "Chain Combo", "Xinrae's Revenge", "Like a Boss", "Minion Apocalypse", "All In", "Parting Gift"];
const FLUX_CHANGE_HOUR_UTC = 7;

// ---------- time zone helpers (no libraries) ----------
const partsFmt = {};
function parts(ms, zone) {
  const f = (partsFmt[zone] ||= new Intl.DateTimeFormat("en-CA", { timeZone: zone, hourCycle: "h23",
    year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", weekday: "short" }));
  const o = Object.fromEntries(f.formatToParts(new Date(ms)).map((p) => [p.type, p.value]));
  return { y: +o.year, mo: +o.month, d: +o.day, h: +o.hour % 24, mi: +o.minute, wd: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].indexOf(o.weekday) };
}
const offsetMin = (ms, zone) => { const p = parts(ms, zone); return Math.round((Date.UTC(p.y, p.mo - 1, p.d, p.h, p.mi) - ms) / 60000); };
// UTC milliseconds for a wall-clock time in `zone`
export function zonedToUtc(y, mo, d, h, mi, zone) {
  let guess = Date.UTC(y, mo - 1, d, h, mi);
  for (let i = 0; i < 3; i++) guess = Date.UTC(y, mo - 1, d, h, mi) - offsetMin(guess, zone) * 60000;
  return guess;
}
export const tzName = (ms, zone) => new Intl.DateTimeFormat("en-US", { timeZone: zone, timeZoneName: "short" })
  .formatToParts(new Date(ms)).find((p) => p.type === "timeZoneName")?.value || "";
export const fmtTime = (ms, zone = LOCAL_ZONE) => new Intl.DateTimeFormat("en-CA", { timeZone: zone, hour: "numeric", minute: "2-digit", hour12: true }).format(new Date(ms));
export const fmtDate = (ms, zone = LOCAL_ZONE, opts = { weekday: "short", month: "short", day: "numeric" }) =>
  new Intl.DateTimeFormat("en-CA", { timeZone: zone, ...opts }).format(new Date(ms));
export const localParts = (ms) => parts(ms, LOCAL_ZONE);

// ---------- events ----------
// Every AT start (slots given) whose UK date falls in [fromMs - 1 day, toMs + 1 day], as UTC ms.
export function atEvents(fromMs, toMs, slots = ["A", "C"], serverZone = SERVER_ZONE) {
  const out = [];
  for (let t = fromMs - 86400000; t <= toMs + 86400000; t += 86400000) {
    const p = parts(t, serverZone);
    for (const slot of slots) {
      const at = zonedToUtc(p.y, p.mo, p.d, AT_HOURS[slot][p.wd], 0, serverZone);
      if (at >= fromMs && at < toMs && !out.some((e) => e.at === at && e.slot === slot)) out.push({ slot, at });
    }
  }
  return out.sort((a, b) => a.at - b.at);
}
export function matStart(year, month, serverZone = SERVER_ZONE) { // month 1-12
  const first = new Date(Date.UTC(year, month - 1, 1)).getUTCDay();
  const day = 1 + ((MAT.weekday - first + 7) % 7) + 7 * (MAT.nth - 1);
  return zonedToUtc(year, month, day, MAT.hour, 0, serverZone);
}
export function nextMat(now = Date.now(), serverZone = SERVER_ZONE) {
  const d = new Date(now);
  let t = matStart(d.getUTCFullYear(), d.getUTCMonth() + 1, serverZone);
  if (t <= now) t = matStart(d.getUTCFullYear() + (d.getUTCMonth() === 11 ? 1 : 0), ((d.getUTCMonth() + 1) % 12) + 1, serverZone);
  return t;
}
export const rotationFor = (ms) => MAP_ROTATION[new Date(ms).getUTCMonth()];
export const fluxFor = (ms) => FLUX[new Date(ms - FLUX_CHANGE_HOUR_UTC * 3600000).getUTCMonth()];
export function nextFluxChange(now = Date.now()) {
  const d = new Date(now - FLUX_CHANGE_HOUR_UTC * 3600000);
  return Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + 1, 1, FLUX_CHANGE_HOUR_UTC);
}
// Differences between the UK and Toronto clocks within a range (when the gap isn't the usual 5 hours).
export function gapChanges(fromMs, toMs, serverZone = SERVER_ZONE) {
  const out = []; let prev = null;
  for (let t = fromMs; t <= toMs; t += 3600000) {
    const gap = (offsetMin(t, serverZone) - offsetMin(t, LOCAL_ZONE)) / 60;
    if (gap !== prev) { out.push({ at: t, gap }); prev = gap; }
  }
  return out;
}
export const countdown = (ms, now = Date.now()) => {
  const m = Math.max(0, Math.round((ms - now) / 60000)), d = Math.floor(m / 1440), h = Math.floor((m % 1440) / 60);
  return d ? `${d}d ${h}h` : h ? `${h}h ${m % 60}m` : `${m}m`;
};
