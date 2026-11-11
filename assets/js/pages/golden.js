import { esc, readJson, writeJson, canSave, toast } from "../core.js";

// Golden moments (docs/REDESIGN.md "Tests", R-303, R-341, R-354). For each moment the engine's story of the game is shown
// (data/model/golden_stories.json, written by tools/golden/golden.py stories on the engine branch). Denning reads it,
// ticks the lines that are wrong and says why, and adds his own notes or corrections; lines he does not tick count as
// right once he saves. Notes he wrote before any engine story was shown (blind_note in the file) are kept as they are:
// they are the fixed blind check the story is compared with. The labels file holds only what he wrote. Earlier
// drop-down answers stay in the file untouched. The sealed answer is stored encoded and never shown again here.

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
  if (!lines) return `<p class="muted small" style="margin:.6rem 0">No engine story has been written for this moment yet.</p>`;
  const mk = g.label?.story || {}, wrong = new Map((mk.wrong || []).map((w) => [`${w.t}|${w.text}`, w.comment || ""]));
  let cut = false;
  const rows = lines.map(([t, text], i) => {
    const k = `${t}|${text}`, on = wrong.has(k);
    const divider = !cut && t >= g.t ? ((cut = true), `<tr class="gm-now"><td colspan="3">the moment, ${clock(g.t)}</td></tr>`) : "";
    return `${divider}<tr data-line="${i}"><td class="gm-t">${clock(t)}</td><td>${esc(text)}</td>
      <td class="gm-mark"><label><input type="checkbox" data-wrong${on ? " checked" : ""}> wrong</label><input type="text" data-why placeholder="what is wrong" value="${esc(on ? wrong.get(k) : "")}"${on ? "" : " hidden"}></td></tr>`;
  }).join("");
  const stale = mk.at && mk.draft !== stories.draft;
  return `<details class="gm-story"${mk.at && !stale ? "" : " open"}><summary><b>The engine's story of this game</b> <span class="muted small">(${lines.length} lines${mk.at ? `; marked ${esc(mk.at)}, ${(mk.wrong || []).length} wrong${stale ? "; the story has been rewritten since" : ""}` : "; not marked yet"})</span></summary>
    <div class="tablewrap"><table class="data gm-lines"><tbody>${rows}</tbody></table></div></details>`;
}

function momentHtml(g, i) {
  const fam = data.families[g.family], L = g.label || {};
  const shouldOptions = fam.call[fam.call.length - 1].options;
  return `<section class="gm" data-id="${esc(g.id)}">
    <div class="row" style="justify-content:space-between"><b>${i + 1}. ${esc(g.team)} v ${esc(g.opponent)}, ${esc(g.map)}</b>
      <span class="muted small">${esc(fam.name)} at ${clock(g.t)} ${L.story?.at ? `<span class="pill elite">Marked ${esc(L.story.at)}</span>` : ""}${L.blind_note ? ` <span class="pill type" title="written before the engine's story was shown">Blind note</span>` : ""}</span></div>
    <p style="margin:.4rem 0">What the engine noticed at ${clock(g.t)}: ${esc(g.trigger)}. <a href="https://gvg.report/report/${esc(g.match)}#map" target="_blank" rel="noopener">Open the replay on gvg.report</a>.</p>
    ${storyHtml(g)}
    <h4>${L.blind_note ? "Your note (written before the story was shown) and any corrections" : "Your notes or corrections"}</h4>
    <textarea data-f="notes" placeholder="What the story misses or gets wrong as a whole, and anything you would say differently: what a team was doing, why, what you would want the model to notice." style="min-height:${L.notes ? 150 : 90}px">${esc(L.notes || "")}</textarea>
    <details class="gm-should"><summary class="small">More (optional): the time of the decision, whether it is a real one, what they should have done</summary>
      <div class="gm-grid" style="margin-top:.4rem">
        ${field("Is there a real decision at this moment?", pick("real", [["yes", "Yes"], ["no", "No: nothing to decide here"], ["different", "Yes, but a different kind of decision"]], L.real, "not said"))}
        ${field("If a different kind, which?", pick("family_is", OTHER_FAMILY.map((n) => [n, n]), L.family_is, "not applicable"))}
        ${field("The decision was actually at (m:ss)", `<input type="text" data-f="actual_time" placeholder="for example 11:42" value="${esc(L.actual_time || "")}">`)}
        ${field("Did a death in the next 30 s force it?", pick("forced", [["no", "No"], ["yes", "Yes"]], L.forced === undefined ? "" : (L.forced ? "yes" : "no"), "not said"))}
      </div>
      <p class="small" style="margin:.6rem 0 .2rem"><b>What should they have done?</b> Stored sealed from the model.${g.sealed ? " A sealed answer is saved; fill these only to replace it." : ""}</p>
      <div class="gm-grid">
        ${field("The better call", `<select data-should><option value="">no view, or what they did was right</option>${shouldOptions.map(([v, t]) => opt(v, t, "")).join("")}<option value="other">Other (say what)</option></select>`)}
        ${field("Why, in a line", `<input type="text" data-should-text placeholder="Not shown again after saving">`)}
      </div></details>
    <div class="row" style="margin-top:.6rem"><button class="btn small primary" data-save>${L.story?.at ? "Save changes" : "Save marks and notes"}</button>
      ${g.label ? `<button class="btn small ghost" data-clear>Clear this moment</button>` : ""}</div>
  </section>`;
}

export async function renderGolden(out, keep = false) {
  if (!keep || !data) data = await readJson(PATH, null);      // after a save the page is redrawn from what was just saved
  if (!data || !(data.moments || []).length) {
    out.innerHTML = `<h1>Golden moments</h1><div class="empty-state">No moments have been picked yet.</div>`;
    return;
  }
  if (!stories) stories = await fetch(STORIES, { cache: "no-cache" }).then((r) => (r.ok ? r.json() : null)).catch(() => null);
  const M = data.moments, m = M.filter((g) => g.label?.story?.at).length;
  out.innerHTML = `<h1>Golden moments</h1>
  <p>${M.length} games from stored matches, each told by the engine up to a minute past one moment. Read the story against the replay, tick each line that is wrong and say why, and add your own notes or corrections underneath. Lines left alone count as right. Your marks and notes are what the engine is rebuilt from and tested against. ${canSave() ? "" : "<b>Add your GitHub key in Settings to save.</b>"}</p>
  <p class="gm-note"><b>${m} of ${M.length} stories marked.</b> Each save stands on its own; stop and resume at any point. ${stories ? `The stories are draft ${esc(stories.draft)} (${esc(stories.generated)}).` : ""} What the story leaves out matters as much as what it gets wrong: say so in the notes.</p>
  <details class="gm-terms"><summary>How the engine's story reads</summary><ul class="small">
    <li><b>A fight</b> is a group of players of both teams close enough to fight, with its place and its numbers. A player counts in a fight after 12 seconds in it; less is support.</li>
    <li><b>Places</b>: the flag stand, the greater stand area (as drawn on the map page), front and back footies, front and back door, base, pit, each named for the team whose ground it is.</li>
    <li><b>Flag lines</b>: picks up, hands the flag to, caps, overcaps (a cap within 45 seconds of the other team's), double run (each half running, or each full running), dropped and back to the spawn. A pickup dropped within 5 seconds is left out.</li>
    <li><b>Matches N s behind</b>: one team's player joined a fight N seconds after the other team's. On time is within about 7 seconds; 30 seconds or more is late.</li>
    <li><b>Falls back, under pressure</b>: the fight moved down that team's side (footies, door, base, pit). Under pressure means team health under 85% or a death in the last 30 seconds; energy is not in the replays.</li>
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
      const before = { label: g.label, sealed: g.sealed };
      const L = { ...(g.label || {}), at: new Date().toISOString().slice(0, 10) };
      if (val("notes").trim()) L.notes = val("notes").trim(); else delete L.notes;
      for (const k of ["real", "family_is", "actual_time"]) { if (val(k).trim()) L[k] = val(k).trim(); else delete L[k]; }
      if (val("forced")) L.forced = val("forced") === "yes"; else delete L.forced;
      const lines = (stories?.stories || {})[g.id];
      if (lines) {
        const wrong = [...el.querySelectorAll("tr[data-line]")].filter((tr) => tr.querySelector("[data-wrong]").checked)
          .map((tr) => { const [t, text] = lines[+tr.dataset.line]; return { t, text, comment: tr.querySelector("[data-why]").value.trim() }; });
        L.story = { at: L.at, draft: stories.draft, lines: lines.length, wrong };
      }
      const should = el.querySelector("[data-should]").value, why = el.querySelector("[data-should-text]").value.trim();
      if (should || why) g.sealed = seal({ should, why });
      g.label = L;
      if (await store(`Golden moments: ${g.id} marked`, before)) await redraw();
    };
    el.querySelector("[data-clear]")?.addEventListener("click", async () => {
      const before = { label: g.label, sealed: g.sealed };
      g.label = null; g.sealed = null;
      if (await store(`Golden moments: ${g.id} cleared`, before)) await redraw();
    });
    el.querySelectorAll("[data-wrong]").forEach((c) => c.onchange = () => { const w = c.closest("td").querySelector("[data-why]"); w.hidden = !c.checked; if (c.checked) w.focus(); });
  });
}
