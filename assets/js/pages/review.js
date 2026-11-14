import { esc, readJson, writeJson, canSave, toast } from "../core.js";

// Game review (docs/REDESIGN.md "Tests"; R-450, R-454, R-455). The engine's reading of whole games, one row a situation
// and, under it, one row for each side's call (its job, the result and the tests behind the result). Denning watches the
// game and marks every row on its own: right, partly or wrong, with his words. The rows come from
// data/model/game_reviews.json (written by tools/golden/review.py export on the engine branch); his marks are saved to
// data/model/game_review_marks.json, which holds only what he marked, each mark with the text of the row it was made on.
// Claude files the marks in the review key (data/model/review_key.json), where they become checks the reading must pass.

const ROWS = "data/model/game_reviews.json", MARKS = "data/model/game_review_marks.json", DRAFT = "gvginfo.review.draft";
const MARK = [["right", "Right"], ["partly", "Partly"], ["wrong", "Wrong"], ["repeat", "Repeat"]];
const SKIP = "not judged";      // a call under a situation he marked wrong or a repeat: nothing to judge, and not asked for
let rows = null, marks = null, cur = null, draft = {};

const clock = (t) => `${Math.floor(t / 60)}:${String(Math.round(t % 60)).padStart(2, "0")}`;
const loadDraft = () => { try { draft = JSON.parse(localStorage.getItem(DRAFT) || "{}"); } catch { draft = {}; } };
const keepDraft = () => { try { localStorage.setItem(DRAFT, JSON.stringify(draft)); } catch { /* the marks stay on the page until saved */ } };
const callText = (c) => `${c.team}${c.side ? ` (${c.side})` : ""}${c.label ? ` [${c.label}]` : ""}: ${c.job}. ${c.met ? "Met" : "Not met"}` +
  (c.tests.length ? ` (${c.tests.map(([ok, t]) => `${ok ? "yes" : "no"}: ${t}`).join("; ")})` : "");
const items = (g) => g.situations.flatMap((s) => [{ id: s.id, text: s.reads }, ...s.calls.map((c) => ({ id: c.id, text: callText(c), under: s.id }))]);
const off = (M, sid) => ["wrong", "repeat"].includes(M[sid]?.mark);
const asked = (g, M) => items(g).filter((x) => !x.under || !off(M, x.under));
const saved = (g) => marks.games?.[g.rid]?.marks || {};
const now = (g) => ({ ...saved(g), ...(draft[g.rid]?.marks || {}) });
const unsaved = (g) => Object.keys(draft[g.rid]?.marks || {}).length + (draft[g.rid]?.notes !== undefined ? 1 : 0);

function control(id, m) {
  return `<td class="rv-mark" data-id="${esc(id)}">${MARK.map(([v, t]) => `<label class="rv-${v}"><input type="radio" name="m-${esc(id)}" value="${v}"${m?.mark === v ? " checked" : ""}> ${t}</label>`).join("")}
    <input type="text" data-why placeholder="your words: what is right or wrong here" value="${esc(m?.why || "")}"></td>`;
}

function gameHtml(g) {
  const M = now(g);
  const body = g.situations.map((s) => {
    const skip = off(M, s.id);
    const calls = s.calls.map((c) => `<tr class="rv-call${M[c.id]?.mark || skip ? " rv-done" : ""}${skip ? " rv-skip" : ""}"><td></td><td></td>
      <td><b>${esc(c.team)}</b>${c.side ? ` <span class="muted">(${esc(c.side)})</span>` : ""}${c.label ? ` <span class="pill type">${esc(c.label)}</span>` : ""}: ${esc(c.job)}.
        <b class="${c.met ? "rv-met" : "rv-not"}">${c.met ? "Met" : "Not met"}</b>${c.draft ? ` <span class="muted small">(this job is Claude's draft, not yet ruled)</span>` : ""}
        ${c.tests.length ? `<div class="muted small">${c.tests.map(([ok, t]) => `${ok ? "yes" : "no"}: ${esc(t)}`).join("; ")}</div>` : ""}</td>${skip ? `<td class="muted small">Not asked: you marked the situation ${esc(M[s.id].mark === "repeat" ? "a repeat" : "wrong")}.</td>` : control(c.id, M[c.id])}</tr>`).join("");
    return `<tr class="rv-sit${M[s.id]?.mark ? " rv-done" : ""}"><td class="rv-n">${s.n}</td><td class="rv-t">${clock(s.t0)}–${clock(s.t1)}</td>
      <td><span class="muted small">What the engine reads</span><br>${esc(s.reads)}</td>${control(s.id, M[s.id])}</tr>${calls}`;
  }).join("");
  const all = asked(g, M), done = all.filter((x) => M[x.id]?.mark).length, n = unsaved(g);
  const notes = draft[g.rid]?.notes ?? marks.games?.[g.rid]?.notes ?? "";
  return `<h3 style="margin:.8rem 0 .2rem">${esc(g.teams.join(" v "))}, ${esc(g.map)}, ${esc(g.date)}</h3>
    <p style="margin:.2rem 0"><a href="https://gvg.report/report/${esc(g.rid)}#map" target="_blank" rel="noopener">Open the replay on gvg.report</a>. ${g.situations.length} situations, ${all.length} rows to mark; <b>${done} marked</b>${n ? `, <b class="rv-not">${n} not saved yet</b>` : ""}.</p>
    <div class="row rv-bar"><button class="btn small primary" data-save>Save this game's marks</button>
      <button class="btn small ghost" data-rest title="Every row you have not marked is marked Right. Use it after marking the rows that are partly right or wrong.">Mark the unmarked rows Right</button></div>
    <div class="tablewrap"><table class="data rv-rows"><thead><tr><th>#</th><th>Time</th><th>The situation, then each side's call</th><th>Your mark</th></tr></thead><tbody>${body}</tbody></table></div>
    <h4 style="margin:.9rem 0 .3rem">Anything the engine did not read in this game</h4>
    <textarea data-notes placeholder="Situations or calls that are missing, with their times; anything that holds for the whole game." style="min-height:90px">${esc(notes)}</textarea>
    <div class="row rv-bar"><button class="btn small primary" data-save>Save this game's marks</button></div>`;
}

export async function renderReview(out, keep = false) {
  if (!keep || !rows) {
    rows = await readJson(ROWS, null);
    marks = (await readJson(MARKS, null)) || { about: "Denning's marks on the rows of Model > Game review (R-450, R-455): for each game, each row he marked (right, partly or wrong), his words, and the text of the row as it was shown to him. Saved by the page; Claude files them in the review key.", games: {} };
    loadDraft();
  }
  if (!rows || !(rows.games || []).length) { out.innerHTML = `<h1>Game review</h1><div class="empty-state">No game has been set out for review yet.</div>`; return; }
  const G = rows.games;
  const g = G.find((x) => x.rid === cur) || G[0]; cur = g.rid;
  out.innerHTML = `<h1>Game review</h1>
  <p>The engine's reading of whole games. Watch the game and mark every row on its own: the situation (did the engine see what was happening: who, where, how many against how many) and, under it, each side's call (is that the job a team has in that situation, and is the result right). ${canSave() ? "" : "<b>Add your GitHub key in Settings to save.</b>"}</p>
  <details class="rv-terms"><summary>How to read a row</summary><ul class="small">
    <li><b>A situation</b> is one thing the engine saw happening between the two times: a flag run and the answer to it, a push on a flagger, one phase of a split, a numbers difference in the main fight, a team pinned in its base, a boost coming, a base resurrection, a Lord push.</li>
    <li><b>A call</b> is what one team did about it. Its <b>job</b> is what a team is expected to achieve in that situation by your rulings; <b>Met</b> or <b>Not met</b> says only whether that happened, with the tests behind it (yes or no). It is a result, not a verdict on whether the call was right.</li>
    <li><b>Right</b>: the row is what you would say. <b>Partly</b>: the situation is there but something in it is off (the numbers, the time, who, the job or the result). <b>Wrong</b>: it did not happen, or it was something else. <b>Repeat</b>: the same thing is already told in another row. For Partly and Wrong, say what you see in your own words.</li>
    <li>When you mark a situation Wrong or a Repeat, the calls under it are not asked for.</li>
    <li>A player counts in a fight, on a split or on its defence after 12 seconds there. Flag lead is in flags: the stand counts as one flag.</li>
    <li>Marks are kept in this browser as you go and reach the engine when you press Save. Stop and resume at any point.</li>
  </ul></details>
  <div class="row rv-games">${G.map((x) => { const a = asked(x, now(x)), d = a.filter((i) => now(x)[i.id]?.mark).length;
    return `<button class="btn small ${x.rid === cur ? "primary" : "ghost"}" data-game="${esc(x.rid)}">${esc(x.teams.join(" v "))} <span class="small">(part ${esc(x.part)}; ${d} of ${a.length})</span></button>`; }).join("")}</div>
  <p class="muted small">Rows written ${esc(rows.generated)} from engine ${esc(rows.engine)}.</p>
  <section class="rv">${gameHtml(g)}</section>
  <style>.rv-rows{table-layout:fixed;width:100%}.doc table.rv-rows td,.rv-rows td{vertical-align:top;white-space:normal!important;overflow-wrap:anywhere;padding:.35rem .5rem;font-size:.9rem}
  .rv-rows th:nth-child(1),.rv-n{width:2.4rem}.rv-rows th:nth-child(2),.rv-t{width:6.2rem;font-family:var(--mono);white-space:nowrap}.rv-rows th:nth-child(4),.rv-mark{width:17rem}
  .rv-sit td{border-top:2px solid var(--line);background:var(--accent-soft)}.rv-call td:nth-child(3){padding-left:1.4rem}.rv-done td:first-child{box-shadow:inset 3px 0 0 var(--accent)}
  .rv-mark label{margin-right:.6rem;white-space:nowrap;font-size:.86rem}.rv-mark input[type=text]{display:block;width:100%;height:1.9rem;margin-top:.3rem;font-size:.84rem}
  .rv-skip td:nth-child(3){opacity:.45}.rv-met{color:#1c7c3c}.rv-not{color:#b3261e}.rv-bar{margin:.6rem 0;gap:.5rem}.rv-games{flex-wrap:wrap;gap:.4rem;margin:.6rem 0}.rv-terms{margin:.6rem 0}.rv-terms summary{cursor:pointer}.small{font-size:.86rem}</style>`;

  const redraw = async () => { const y = scrollY; await renderReview(out, true); scrollTo({ top: y }); };
  const text = Object.fromEntries(items(g).map((x) => [x.id, x.text]));
  const put = (id, patch) => {
    const d = (draft[g.rid] ||= { marks: {} }); d.marks ||= {};
    d.marks[id] = { ...(saved(g)[id] || {}), ...(d.marks[id] || {}), ...patch, text: text[id] };
    keepDraft();
  };
  out.querySelectorAll("[data-game]").forEach((b) => b.onclick = () => { cur = b.dataset.game; redraw(); });
  out.querySelectorAll(".rv-mark").forEach((td) => {
    const id = td.dataset.id, why = td.querySelector("[data-why]");
    td.querySelectorAll("input[type=radio]").forEach((r) => r.onchange = () => {
      const was = off(now(g), id);
      put(id, { mark: r.value, why: why.value.trim() }); td.closest("tr").classList.add("rv-done");
      if (id.startsWith("s:") && was !== off(now(g), id)) {     // the calls under it are no longer asked for, or are asked for again
        items(g).filter((x) => x.under === id).forEach((x) => { if (off(now(g), id)) put(x.id, { mark: SKIP, why: "" }); else if (now(g)[x.id]?.mark === SKIP) put(x.id, { mark: "", why: "" }); });
        redraw().then(() => out.querySelector(`.rv-mark[data-id="${CSS.escape(id)}"] [data-why]`)?.focus()); return;
      }
      if (r.value !== "right") why.focus();
    });
    why.onchange = () => { const m = td.querySelector("input[type=radio]:checked"); if (m) put(id, { mark: m.value, why: why.value.trim() }); };
  });
  out.querySelector("[data-notes]").onchange = (e) => { (draft[g.rid] ||= { marks: {} }).notes = e.target.value.trim(); keepDraft(); };
  out.querySelector("[data-rest]").onclick = () => { const M = now(g); asked(g, M).forEach((x) => { if (!M[x.id]?.mark) put(x.id, { mark: "right", why: "" }); }); redraw(); };
  out.querySelectorAll("[data-save]").forEach((b) => b.onclick = async () => {
    const before = JSON.stringify(marks), d = draft[g.rid] || { marks: {} };
    const G0 = (marks.games ||= {}), e = (G0[g.rid] ||= { marks: {} });
    e.game = `${g.teams.join(" v ")}, ${g.map}`; e.at = new Date().toISOString().slice(0, 10); e.engine = rows.engine;
    e.marks = Object.fromEntries(Object.entries({ ...e.marks, ...(d.marks || {}) }).filter(([, v]) => v.mark));
    if (d.notes !== undefined) { if (d.notes) e.notes = d.notes; else delete e.notes; }
    try { await writeJson(MARKS, marks, `Game review: ${e.game} marked (${Object.keys(e.marks).length} rows)`); }
    catch (err) { marks = JSON.parse(before); toast(err.message); return; }
    delete draft[g.rid]; keepDraft(); toast("Saved"); await redraw();
  });
}
