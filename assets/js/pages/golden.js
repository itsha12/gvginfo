import { esc, readJson, writeJson, canSave, toast } from "../core.js";

// Golden moments (docs/REDESIGN.md "Tests", R-303). The engine picks moments from stored matches (tools/golden/golden.py
// pick, on the engine branch); Denning labels each by hand here: is it a real moment of that decision, which version
// of it (scenario), what the team did (call and shape), whether a death forced it, and optionally what the team should
// have done. The engine's own reading is never in the file, so this page cannot show it; the engine is run against the
// labels afterwards (golden.py score). The optional "should have done" answer is stored encoded in `sealed` and is not
// shown again in plain text here, so it stays out of the model's sight until the test that needs it.

const PATH = "data/model/golden_moments.json";
const OTHER_FAMILY = ["Flag decision", "Answer to a split", "Numbers advantage", "Game plan", "Engage or wait"];
let data = null;

const clock = (t) => `${Math.floor(t / 60)}:${String(Math.round(t % 60)).padStart(2, "0")}`;
const seal = (obj) => { const b = new TextEncoder().encode(JSON.stringify(obj)); let s = ""; b.forEach((c) => { s += String.fromCharCode(c); }); return btoa(s); };
const opt = (v, text, cur) => `<option value="${esc(v)}"${String(cur ?? "") === String(v) ? " selected" : ""}>${esc(text)}</option>`;
const pick = (name, options, cur, blank = "choose") => `<select data-f="${esc(name)}"><option value="">${esc(blank)}</option>${options.map(([v, t]) => opt(v, t, cur)).join("")}</select>`;
const field = (label, html, hint = "") => `<label class="gm-field"><span class="gm-q">${esc(label)}</span>${html}${hint ? `<span class="muted small">${esc(hint)}</span>` : ""}</label>`;

function callSelect(c, fam, L) {
  const cur = (L.call || {})[c.id];
  let options;
  if (c.by) {
    const group = (name, ids) => `<optgroup label="${esc(name)}">${ids.map((v) => opt(v, v, cur)).join("")}</optgroup>`;
    options = group("When the deciding team is up", c.by.up) + group("When it is down", c.by.down);
  } else options = c.options.map(([v, t]) => opt(v, t, cur)).join("");
  return `<select data-call="${esc(c.id)}"><option value="">choose</option>${options}${c.other ? opt("other", "Other (say what below)", cur) : ""}</select>
    ${c.other ? `<input type="text" data-call-text="${esc(c.id)}" placeholder="If other: what they did, in your words" value="${esc((L.call || {})[c.id + "_text"] || "")}">` : ""}`;
}

function momentHtml(g, i) {
  const fam = data.families[g.family], L = g.label || {};
  const done = !!g.label;
  const shouldOptions = fam.call[fam.call.length - 1].options;
  return `<section class="gm" data-id="${esc(g.id)}">
    <div class="row" style="justify-content:space-between"><b>${i + 1}. ${esc(fam.name)}</b>
      <span class="muted small">${esc(g.team)} v ${esc(g.opponent)}, ${esc(g.map)}, at ${clock(g.t)} ${done ? `<span class="pill elite">Labelled ${esc(L.at || "")}</span>` : ""}</span></div>
    <p class="small" style="margin:.4rem 0">${esc(fam.question)}</p>
    <p style="margin:.4rem 0"><b>The call is ${esc(g.team)}'s.</b> What set it off: ${esc(g.trigger)}.
      <a href="https://gvg.report/report/${esc(g.match)}#map" target="_blank" rel="noopener">Open the replay on gvg.report</a> and watch ${clock(g.watch[0])} to ${clock(g.watch[1])}.</p>
    <div class="gm-grid">
      ${field("Is this a real moment of this decision?", pick("real", [["yes", "Yes"], ["no", "No: nothing to decide here"], ["different", "It is a different decision"]], L.real))}
      ${field("If a different decision, which?", pick("family_is", OTHER_FAMILY.map((n) => [n, n]), L.family_is, "not applicable"))}
      ${fam.became ? field("What did the leave become?", pick("became", data.became, L.became), "Judged afterwards: where the player or group ended up within a minute.") : ""}
    </div>
    <h4>Scenario <span class="muted small">(the situation at ${clock(g.t)})</span></h4>
    <div class="gm-grid">${fam.scenario.map((s) => field(s.q, `<select data-scenario="${esc(s.id)}"><option value="">choose</option>${s.options.map(([v, t]) => opt(v, t, (L.scenario || {})[s.id])).join("")}</select>`)).join("")}</div>
    <h4>What the team did <span class="muted small">(where its players stand ${clock(g.t + data.read_window[0])} to ${clock(g.t + data.read_window[1])})</span></h4>
    <div class="gm-grid">${fam.call.map((c) => field(c.q, callSelect(c, fam, L))).join("")}</div>
    <h4>Shape <span class="muted small">(who, when, which way)</span></h4>
    <div class="gm-field"><span class="gm-q">Who went (the runners, the defenders sent, or the players who left; none if nobody)</span>
      <div class="row">${g.roles.map((r) => `<label class="gm-check"><input type="checkbox" data-who="${esc(r)}"${(L.who || []).includes(r) ? " checked" : ""}> ${esc(r)}</label>`).join("")}</div></div>
    <div class="gm-grid">
      ${field("When (seconds after the trigger that the first of them moved)", `<input type="number" data-f="when_s" min="0" max="120" value="${esc(L.when_s ?? "")}">`)}
      ${field("Which way", `${pick("route", [...g.routes.map((r) => [r, r]), ["other", "Other (say which below)"]], L.route, "not applicable")}<input type="text" data-f="route_text" placeholder="If other: which way" value="${esc(L.route_text || "")}">`)}
      ${field("Did a death on the deciding team in those 30 s force it?", pick("forced", [["no", "No"], ["yes", "Yes"]], L.forced === undefined ? "" : (L.forced ? "yes" : "no")))}
    </div>
    <h4>What should they have done? <span class="muted small">(optional; stored sealed from the model)</span></h4>
    ${g.sealed ? `<p class="small">A sealed answer is saved. Fill the two fields below only to replace it.</p>` : ""}
    <div class="gm-grid">
      ${field("The better call", `<select data-should><option value="">no view, or what they did was right</option>${shouldOptions.map(([v, t]) => opt(v, t, "")).join("")}<option value="other">Other (say what)</option></select>`)}
      ${field("Why, in a line", `<input type="text" data-should-text placeholder="Not shown again after saving">`)}
    </div>
    <textarea data-f="notes" placeholder="Notes: anything the options above could not say (a missing option, the wrong moment, a hall feature in play)" style="min-height:54px;margin:.6rem 0">${esc(L.notes || "")}</textarea>
    <div class="row"><button class="btn small primary" data-save>${done ? "Save changes" : "Save this label"}</button>
      ${done ? `<button class="btn small ghost" data-clear>Clear this label</button>` : ""}</div>
  </section>`;
}

export async function renderGolden(out, keep = false) {
  if (!keep || !data) data = await readJson(PATH, null);      // after a save the page is redrawn from what was just saved
  if (!data || !(data.moments || []).length) {
    out.innerHTML = `<h1>Golden moments</h1><div class="empty-state">No moments have been picked yet.</div>`;
    return;
  }
  const M = data.moments, n = M.filter((g) => g.label).length;
  out.innerHTML = `<h1>Golden moments</h1>
  <p>${M.length} moments from stored matches, picked to cover every version of the first three decision families and the hard cases. Label each by hand from the replay. The engine's reading of the same moments must then match these labels before its rebuild is accepted, and again after every later engine change. The engine's reading is not shown here, and is not in the file this page reads. ${canSave() ? "" : "<b>Add your GitHub key in Settings to save labels.</b>"}</p>
  <p class="gm-note"><b>${n} of ${M.length} labelled.</b> Each label saves on its own; stop and resume at any point. If an option list cannot say what happened, pick Other and write it in your words: those words become the new options.</p>
  <details class="gm-terms"><summary>How to read a moment</summary><ul class="small">
    <li><b>The call is X's</b>: label what team X did. "Own" is X's, "enemy" is the other team.</li>
    <li><b>What set it off</b>: the event the engine noticed, at the time shown. For a leave, the engine does not say here what it became; that is one of the labels.</li>
    <li><b>Scenario</b>: the situation at the moment of the trigger, before anyone responds.</li>
    <li><b>What the team did</b>: read from where its players stand 20 to 30 seconds after the trigger, not from damage or kills. A group is at a place when more than half of its living players stand in it. "Fall to footmen" means standing where the footmen are engaged in the fight; "retreat to the pit" means inside the pit, "fall back into the base" inside the base but outside the pit.</li>
    <li><b>Runners</b>: players on flag duty in that window (carrying, or gone for the flag). Two runners is a double run: two flags in motion, never two players sent to the spawn together.</li>
    <li><b>Answer to a split</b>: no answer, one defender, mirror (as many as the split), two monks, add one (one more than the split), full collapse (the team). Count players home or on their way home 30 seconds after the split left.</li>
    <li><b>Forced</b>: a player of the deciding team died inside those 30 seconds, so the positions show the fight's result more than a choice.</li>
    <li><b>What should they have done</b>: optional. It is stored encoded and never shown again here, so the model does not learn it before the test that uses it.</li>
  </ul></details>
  ${M.map((g, i) => momentHtml(g, i)).join("")}
  <style>.gm{border:1px solid var(--line);padding:.9rem 1rem;margin:1rem 0}.gm h4{margin:.9rem 0 .3rem}.gm-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:.6rem .9rem}
  .gm-field{display:flex;flex-direction:column;gap:.25rem;margin:.2rem 0}.gm-field select,.gm-field input[type=text],.gm-field input[type=number]{width:100%}.gm-q{font-size:.86rem;font-weight:600}
  .gm-check{display:inline-flex;gap:.3rem;align-items:center;font-size:.9rem}.gm-terms{margin:.6rem 0 1rem}.gm-terms summary{cursor:pointer}.small{font-size:.86rem}
  .gm-note{background:var(--accent-soft);border-left:3px solid var(--accent);padding:.5rem .8rem;margin:.6rem 0}</style>`;

  out.querySelectorAll(".gm").forEach((el) => {
    const g = data.moments.find((x) => x.id === el.dataset.id);
    const val = (name) => el.querySelector(`[data-f="${name}"]`)?.value ?? "";
    el.querySelector("[data-save]").onclick = async () => {
      const real = val("real");
      if (!real) { toast("Say first whether this is a real moment of this decision."); return; }
      const before = { label: g.label, sealed: g.sealed };
      const L = { real, at: new Date().toISOString().slice(0, 10) };
      if (val("family_is")) L.family_is = val("family_is");
      if (val("became")) L.became = val("became");
      L.scenario = {}; el.querySelectorAll("[data-scenario]").forEach((s) => { if (s.value) L.scenario[s.dataset.scenario] = s.value; });
      L.call = {}; el.querySelectorAll("[data-call]").forEach((s) => { if (s.value) L.call[s.dataset.call] = s.value; });
      el.querySelectorAll("[data-call-text]").forEach((s) => { if (s.value.trim()) L.call[s.dataset.callText + "_text"] = s.value.trim(); });
      L.who = [...el.querySelectorAll("[data-who]:checked")].map((c) => c.dataset.who);
      if (val("when_s") !== "") L.when_s = +val("when_s");
      if (val("route")) L.route = val("route");
      if (val("route_text").trim()) L.route_text = val("route_text").trim();
      if (val("forced")) L.forced = val("forced") === "yes";
      if (val("notes").trim()) L.notes = val("notes").trim();
      const should = el.querySelector("[data-should]").value, why = el.querySelector("[data-should-text]").value.trim();
      if (should || why) g.sealed = seal({ should, why });
      g.label = L;
      try { await writeJson(PATH, data, `Golden moments: ${g.id} labelled`); toast("Saved"); }
      catch (e) { toast(e.message); g.label = before.label; g.sealed = before.sealed; return; }
      const y = scrollY; await renderGolden(out, true); scrollTo({ top: y });
    };
    el.querySelector("[data-clear]")?.addEventListener("click", async () => {
      const before = { label: g.label, sealed: g.sealed };
      g.label = null; g.sealed = null;
      try { await writeJson(PATH, data, `Golden moments: ${g.id} cleared`); toast("Cleared"); }
      catch (e) { toast(e.message); g.label = before.label; g.sealed = before.sealed; return; }
      const y = scrollY; await renderGolden(out, true); scrollTo({ top: y });
    });
  });
}
