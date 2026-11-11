import { esc, readJson, writeJson, canSave, toast } from "../core.js";

// Golden moments (docs/REDESIGN.md "Tests", R-303, R-341, R-345). Two parts for each moment:
//   1. Denning writes his note: the game up to the decision and what the team did, in his own words, with a few
//      drop-downs (is it a real decision, the time if the decision was earlier or later, forced or not) and an optional
//      sealed view of what the team should have done.
//   2. Only after his note is saved, the engine's own story of the same game is shown (data/model/golden_stories.json,
//      written by tools/golden/golden.py stories on the engine branch). He ticks the lines that are wrong, says why,
//      and writes what is missing. Lines he does not tick count as right once he saves his marks.
// The labels file never holds the engine's reading. Earlier drop-down answers (scenario, call, shape) stay in the file
// untouched; the page no longer asks for them. The sealed answer is stored encoded and never shown again here.

const PATH = "data/model/golden_moments.json", STORIES = "data/model/golden_stories.json";
const OTHER_FAMILY = ["Flag decision", "Answer to a split", "Numbers advantage", "Game plan", "Engage or wait"];
let data = null, stories = null;

const clock = (t) => `${Math.floor(t / 60)}:${String(Math.round(t % 60)).padStart(2, "0")}`;
const seal = (obj) => { const b = new TextEncoder().encode(JSON.stringify(obj)); let s = ""; b.forEach((c) => { s += String.fromCharCode(c); }); return btoa(s); };
const opt = (v, text, cur) => `<option value="${esc(v)}"${String(cur ?? "") === String(v) ? " selected" : ""}>${esc(text)}</option>`;
const pick = (name, options, cur, blank = "choose") => `<select data-f="${esc(name)}"><option value="">${esc(blank)}</option>${options.map(([v, t]) => opt(v, t, cur)).join("")}</select>`;
const field = (label, html, hint = "") => `<label class="gm-field"><span class="gm-q">${esc(label)}</span>${html}${hint ? `<span class="muted small">${esc(hint)}</span>` : ""}</label>`;

function storyHtml(g) {
  const lines = (stories?.stories || {})[g.id];
  if (!g.label) return `<p class="muted small" style="margin:.6rem 0 0">The engine's story of this game is shown here once this note is saved.</p>`;
  if (!lines) return `<p class="muted small" style="margin:.6rem 0 0">No engine story has been written for this moment yet.</p>`;
  const mk = g.label.story || {}, wrong = new Map((mk.wrong || []).map((w) => [`${w.t}|${w.text}`, w.comment || ""]));
  let cut = false;
  const rows = lines.map(([t, text], i) => {
    const k = `${t}|${text}`, on = wrong.has(k);
    const divider = !cut && t >= g.t ? ((cut = true), `<tr class="gm-now"><td colspan="3">the moment, ${clock(g.t)}</td></tr>`) : "";
    return `${divider}<tr data-line="${i}"><td class="gm-t">${clock(t)}</td><td>${esc(text)}</td>
      <td class="gm-mark"><label><input type="checkbox" data-wrong${on ? " checked" : ""}> wrong</label><input type="text" data-why placeholder="what is wrong" value="${esc(on ? wrong.get(k) : "")}"${on ? "" : " hidden"}></td></tr>`;
  }).join("");
  return `<details class="gm-story"${mk.at ? "" : " open"}><summary><b>Part 2: the engine's story of this game</b> <span class="muted small">(${lines.length} lines${mk.at ? `; marked ${esc(mk.at)}, ${(mk.wrong || []).length} wrong` : "; not marked yet"})</span></summary>
    <p class="small" style="margin:.4rem 0">Tick a line that is wrong and say why. Lines left alone count as right. Then write what is missing, or what you would say differently, and save.</p>
    <div class="tablewrap"><table class="data gm-lines"><tbody>${rows}</tbody></table></div>
    <textarea data-missing placeholder="What is missing from this story, or what you would say differently" style="min-height:70px;margin:.6rem 0">${esc(mk.missing || "")}</textarea>
    <div class="row"><button class="btn small primary" data-save-marks>Save these marks</button></div></details>`;
}

function momentHtml(g, i) {
  const fam = data.families[g.family], L = g.label || {};
  const shouldOptions = fam.call[fam.call.length - 1].options;
  return `<section class="gm" data-id="${esc(g.id)}">
    <div class="row" style="justify-content:space-between"><b>${i + 1}. ${esc(fam.name)}</b>
      <span class="muted small">${esc(g.team)} v ${esc(g.opponent)}, ${esc(g.map)}, at ${clock(g.t)} ${g.label ? `<span class="pill elite">Note saved ${esc(L.at || "")}</span>` : ""}${L.story?.at ? ` <span class="pill type">Story marked</span>` : ""}</span></div>
    <p style="margin:.4rem 0">What the engine noticed: ${esc(g.trigger)}. <a href="https://gvg.report/report/${esc(g.match)}#map" target="_blank" rel="noopener">Open the replay on gvg.report</a>; the moment is at ${clock(g.t)}.</p>
    <h4>Part 1: your note</h4>
    <textarea data-f="notes" placeholder="The game up to this decision, as you would tell it: the opening, the flag exchange, splits and their numbers, who is under pressure, deaths and death penalty. Then what each team did at this moment, and anything you would want the model to notice." style="min-height:150px">${esc(L.notes || "")}</textarea>
    <div class="gm-grid" style="margin-top:.5rem">
      ${field("Is there a real decision here?", pick("real", [["yes", "Yes"], ["no", "No: nothing to decide here"], ["different", "Yes, but a different kind of decision"]], L.real))}
      ${field("If a different kind, which?", pick("family_is", OTHER_FAMILY.map((n) => [n, n]), L.family_is, "not applicable"))}
      ${field("The decision was actually at (m:ss), if not at the time shown", `<input type="text" data-f="actual_time" placeholder="for example 11:42" value="${esc(L.actual_time || "")}">`)}
      ${field("Did a death on either team in the next 30 s force it?", pick("forced", [["no", "No"], ["yes", "Yes"]], L.forced === undefined ? "" : (L.forced ? "yes" : "no"), "not sure"))}
    </div>
    <details class="gm-should"><summary class="small">What should they have done? (optional; stored sealed from the model)</summary>
      ${g.sealed ? `<p class="small">A sealed answer is saved. Fill the two fields below only to replace it.</p>` : ""}
      <div class="gm-grid">
        ${field("The better call", `<select data-should><option value="">no view, or what they did was right</option>${shouldOptions.map(([v, t]) => opt(v, t, "")).join("")}<option value="other">Other (say what)</option></select>`)}
        ${field("Why, in a line", `<input type="text" data-should-text placeholder="Not shown again after saving">`)}
      </div></details>
    <div class="row" style="margin-top:.6rem"><button class="btn small primary" data-save>${g.label ? "Save changes to this note" : "Save this note"}</button>
      ${g.label ? `<button class="btn small ghost" data-clear>Clear this moment</button>` : ""}</div>
    ${storyHtml(g)}
  </section>`;
}

export async function renderGolden(out, keep = false) {
  if (!keep || !data) data = await readJson(PATH, null);      // after a save the page is redrawn from what was just saved
  if (!data || !(data.moments || []).length) {
    out.innerHTML = `<h1>Golden moments</h1><div class="empty-state">No moments have been picked yet.</div>`;
    return;
  }
  if (!stories) stories = await fetch(STORIES, { cache: "no-cache" }).then((r) => (r.ok ? r.json() : null)).catch(() => null);
  const M = data.moments, n = M.filter((g) => g.label).length, m = M.filter((g) => g.label?.story?.at).length;
  out.innerHTML = `<h1>Golden moments</h1>
  <p>${M.length} moments from stored matches. Each has two parts. First, write the game up to the decision in your own words. Then, once your note is saved, the engine's own story of the same game appears below it: tick what it gets wrong and write what it misses. Your notes and marks are what the engine is rebuilt from and tested against. ${canSave() ? "" : "<b>Add your GitHub key in Settings to save.</b>"}</p>
  <p class="gm-note"><b>${n} of ${M.length} notes written; ${m} stories marked.</b> Each save stands on its own; stop and resume at any point. ${stories ? `The engine's stories are draft ${esc(stories.draft)} (${esc(stories.generated)}).` : ""}</p>
  <details class="gm-terms"><summary>How the engine's story reads</summary><ul class="small">
    <li><b>A fight</b> is a group of players of both teams close enough to fight, with its place and its numbers. A player counts in a fight after 12 seconds in it; less is support.</li>
    <li><b>Places</b>: the flag stand, the greater stand area, front and back footies, front and back door, base, pit, each named for the team whose ground it is.</li>
    <li><b>Flag lines</b>: picks up, hands the flag to, caps, overcaps (a cap within 45 seconds of the other team's), double run (each half running, or each full running), dropped and back to the spawn. A pickup dropped within 5 seconds is left out.</li>
    <li><b>Matches N s behind</b>: one team's player joined a fight N seconds after the other team's. On time is within about 7 seconds; 30 seconds or more is late.</li>
    <li><b>Falls back, under pressure</b>: the fight moved down that team's side (footies, door, base, pit). Under pressure is read from team health and deaths; energy is not in the replays.</li>
    <li><b>Before the base res</b>: seconds from a death to the next two-minute base resurrection.</li>
    <li>The story does not yet read a threat or a posture, and it does not judge a play.</li>
  </ul></details>
  ${M.map((g, i) => momentHtml(g, i)).join("")}
  <style>.gm{border:1px solid var(--line);padding:.9rem 1rem;margin:1rem 0}.gm h4{margin:.9rem 0 .3rem}.gm-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:.6rem .9rem}
  .gm-field{display:flex;flex-direction:column;gap:.25rem;margin:.2rem 0}.gm-field select,.gm-field input[type=text]{width:100%}.gm-q{font-size:.86rem;font-weight:600}
  .gm-terms,.gm-should,.gm-story{margin:.6rem 0}.gm-terms summary,.gm-should summary,.gm-story summary{cursor:pointer}.small{font-size:.86rem}
  .gm-note{background:var(--accent-soft);border-left:3px solid var(--accent);padding:.5rem .8rem;margin:.6rem 0}
  .gm-lines{table-layout:fixed;width:100%}.doc table.gm-lines td{vertical-align:top;white-space:normal!important;overflow-wrap:anywhere;padding:.25rem .5rem;font-size:.88rem}.gm-lines td.gm-t{font-family:var(--mono);white-space:nowrap;width:3.6rem}.gm-lines td.gm-mark{width:13rem}
  .gm-mark input[hidden]{display:none!important}.gm-mark input[type=text]{display:block;height:1.9rem;width:100%;margin-top:.25rem;font-size:.82rem}.gm-now td{background:var(--accent-soft);font-weight:600;font-size:.8rem;text-transform:uppercase;letter-spacing:.05em}</style>`;

  out.querySelectorAll(".gm").forEach((el) => {
    const g = data.moments.find((x) => x.id === el.dataset.id);
    const val = (name) => el.querySelector(`[data-f="${name}"]`)?.value ?? "";
    const redraw = async () => { const y = scrollY; await renderGolden(out, true); scrollTo({ top: y }); };
    const store = async (msg, before) => {
      try { await writeJson(PATH, data, msg); toast("Saved"); }
      catch (e) { toast(e.message); g.label = before.label; g.sealed = before.sealed; return false; }
      return true;
    };
    el.querySelector("[data-save]").onclick = async () => {
      if (!val("notes").trim()) { toast("Write the note first."); return; }
      if (!val("real")) { toast("Say whether there is a real decision here."); return; }
      const before = { label: g.label, sealed: g.sealed };
      const L = { ...(g.label || {}), real: val("real"), notes: val("notes").trim(), at: new Date().toISOString().slice(0, 10) };
      for (const k of ["family_is", "actual_time"]) { if (val(k).trim()) L[k] = val(k).trim(); else delete L[k]; }
      if (val("forced")) L.forced = val("forced") === "yes"; else delete L.forced;
      const should = el.querySelector("[data-should]").value, why = el.querySelector("[data-should-text]").value.trim();
      if (should || why) g.sealed = seal({ should, why });
      g.label = L;
      if (await store(`Golden moments: ${g.id} note`, before)) await redraw();
    };
    el.querySelector("[data-clear]")?.addEventListener("click", async () => {
      const before = { label: g.label, sealed: g.sealed };
      g.label = null; g.sealed = null;
      if (await store(`Golden moments: ${g.id} cleared`, before)) await redraw();
    });
    el.querySelectorAll("[data-wrong]").forEach((c) => c.onchange = () => { const w = c.closest("td").querySelector("[data-why]"); w.hidden = !c.checked; if (c.checked) w.focus(); });
    el.querySelector("[data-save-marks]")?.addEventListener("click", async () => {
      const lines = stories.stories[g.id], before = { label: g.label, sealed: g.sealed };
      const wrong = [...el.querySelectorAll("tr[data-line]")].filter((tr) => tr.querySelector("[data-wrong]").checked)
        .map((tr) => { const [t, text] = lines[+tr.dataset.line]; return { t, text, comment: tr.querySelector("[data-why]").value.trim() }; });
      g.label = { ...g.label, story: { at: new Date().toISOString().slice(0, 10), draft: stories.draft, lines: lines.length, wrong, missing: el.querySelector("[data-missing]").value.trim() } };
      if (await store(`Golden moments: ${g.id} story marked`, before)) await redraw();
    });
  });
}
