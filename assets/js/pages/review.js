import { esc, readJson, writeJson, canSave, toast } from "../core.js";

// Game review (docs/REDESIGN.md "Tests"; R-454, R-455, R-491 to R-497). The engine's reading of whole games, one row a
// situation and, under it, one row for each side's call (its job, the result and the tests behind the result). Each
// situation carries the engine's confidence that it is a decision (high, medium, low; a moment it reads as no decision
// is kept as a thin, folded row). Denning watches the game and grades every situation: Classic, Visible, Weak, No
// decision (or Repeat). For a decision he says whether the engine read it Correct, Partly or Incorrect, ticks what is
// off, and adds his words; the calls under it are asked for only under a Classic or Visible decision read Correct or
// Partly. He adds the decisions the engine did not read at all. The rows come from data/model/game_reviews.json
// (tools/golden/review.py export on the engine branch); his marks are saved to data/model/game_review_marks.json,
// which holds only what he marked, each mark with the text of the row it was made on. Games marked before 2026-11-15
// (no "scheme": 2) are history: shown read only, and never a test the engine has to pass (R-491).
//
// A second view, Flag advice (2026-11-19): for the same games, the engine's sentence for every answer to a flag run
// and every "run again, or not": the spot, the answer, what followed, and what teams in similar spots got from each
// answer. He says whether what happened is told correctly, whether the reading makes sense to him, and what he would
// have done there. The cards come from data/model/flag_cards.json (tools/replay_analysis/cases.py cards --site, on
// the engine branch); his marks are saved to data/model/flag_card_marks.json, each with the text he saw.

const ROWS = "data/model/game_reviews.json", MARKS = "data/model/game_review_marks.json", DRAFT = "gvginfo.review.draft2";
const GRADE = [["classic", "Classic"], ["visible", "Visible"], ["weak", "Weak"], ["none", "No decision"]];
const READ = [["correct", "Correct"], ["partly", "Partly"], ["incorrect", "Incorrect"]];
const OFFS = [["numbers", "Numbers"], ["who", "Who"], ["when", "When"], ["where", "Where"], ["kind", "Kind of play"]];
// Why a situation is Weak or No decision (his four reasons, 2026-11-16): ticks, so that they can be counted. A repeat is its own grade and a misreading is "Incorrect".
const REASONS = [["brief", "Too brief", ""], ["small", "Impact too small to make a difference", ""], ["nofight", "No real fight, nothing at stake", ""],
  ["unclear", "Weak or unclear small edge in real game", "It may have been a borderline decision, but it is too unclear or weak ever to be read as a decision in a real game."]];
const BAND = { high: "High", medium: "Medium", low: "Low", none: "No decision" };
const KINDS = ["flag", "push on a flagger", "split", "collapse", "numbers", "boost", "pinned in base", "base res", "Lord push", "other"];
const SKIP = "not judged";      // a call that is not asked for
let rows = null, marks = null, cur = null, draft = {};
const CARDS = "data/model/flag_cards.json", CARD_MARKS = "data/model/flag_card_marks.json", CDRAFT = "gvginfo.review.cards1";
const SENSE = [["agree", "Makes sense"], ["disagree", "Does not"], ["unsure", "No view"]];
// His own call. "No clear answer" was two answers (his word, 2026-11-19): that it makes no difference what the team does, and that he does not know what he would do
// "Send" was two answers as well (his word, 2026-11-20): at once, or after a short look at whether the extra player gets a kill or their flag can be stopped
const OWN = [["send", "Send a runner at once"], ["wait", "Look for a kill first, then send"], ["hold", "Hold off"], ["nodiff", "It makes no difference here"], ["unknown", "I don't know"]];
const OWN_WORDS = Object.fromEntries(OWN);
let view = "games", cards = null, cmarks = null, ccur = null, cdraft = {};
try { view = localStorage.getItem("gvginfo.review.view") === "flags" ? "flags" : "games"; } catch { /* the games view */ }
let showTodo = false;           // rows not yet marked are shown in red (his request, 2026-11-17: "which rows I haven't marked yet")
try { showTodo = localStorage.getItem("gvginfo.review.todo") === "1"; } catch { /* off */ }

const clock = (t) => `${Math.floor(t / 60)}:${String(Math.round(t % 60)).padStart(2, "0")}`;
const loadDraft = () => { try { draft = JSON.parse(localStorage.getItem(DRAFT) || "{}"); } catch { draft = {}; } };
const keepDraft = () => { try { localStorage.setItem(DRAFT, JSON.stringify(draft)); } catch { /* the marks stay on the page until saved */ } };
const callText = (c) => `${c.team}${c.side ? ` (${c.side})` : ""}${c.label ? ` [${c.label}]` : ""}: ${c.job}. ${c.met ? "Met" : "Not met"}` +
  (c.tests.length ? ` (${c.tests.map(([ok, t]) => `${t}: ${ok ? "yes" : "no"}`).join("; ")})` : "");
const saved = (g) => marks.games?.[g.rid]?.marks || {};
const now = (g) => ({ ...saved(g), ...(draft[g.rid]?.marks || {}) });
const missedOf = (g) => draft[g.rid]?.missed ?? marks.games?.[g.rid]?.missed ?? [];
const unsaved = (g) => Object.keys(draft[g.rid]?.marks || {}).length + (draft[g.rid]?.notes !== undefined ? 1 : 0) + (draft[g.rid]?.missed !== undefined ? 1 : 0);
const band = (s) => s.confidence?.band || (s.unclear ? "none" : "");
const isDecision = (m) => ["classic", "visible", "weak"].includes(m?.grade);
// The calls under a situation are asked for only when it is a Classic or Visible decision which the engine read Correct or Partly.
const callsAsked = (m) => ["classic", "visible"].includes(m?.grade) && ["correct", "partly"].includes(m?.mark);
const whyNot = (s, m) => band(s) === "none" && !isDecision(m) ? "" : !m?.grade ? "Grade the situation first." : m.grade === "none" ? "Not asked: you graded this No decision." : m.grade === "repeat" ? "Not asked: a repeat."
  : m.grade === "weak" ? "Not asked: a Weak decision." : band(s) === "none" ? "Not asked: the engine set out no call here." : !m.mark ? "Say first whether the engine read the situation correctly." : m.mark === "incorrect" ? "Not asked: you marked the reading Incorrect." : "";
// A situation is done when it is graded and, for a decision the engine read, marked Correct, Partly or Incorrect. A moment
// the engine reads as no decision is done as it stands: leaving it alone agrees with it.
const sitDone = (s, m) => band(s) === "none" ? true : !!m?.grade && (!isDecision(m) || !!m.mark);
const todo = (g, M) => g.situations.flatMap((s) => [...(band(s) === "none" && !M[s.id]?.grade ? [] : [{ id: s.id, done: sitDone(s, M[s.id]) }]), ...(callsAsked(M[s.id]) && band(s) !== "none" ? s.calls.map((c) => ({ id: c.id, call: true, done: !!M[c.id]?.mark && M[c.id].mark !== SKIP })) : [])]);

function gradeBoxes(id, m, only) {
  const G = only ? GRADE.filter(([v]) => only.includes(v)) : GRADE;
  return `<div class="rv-grades">${G.map(([v, t]) => `<label class="rv-g rv-g-${v}${m?.grade === v ? " on" : ""}"><input type="radio" name="g-${esc(id)}" data-grade value="${v}"${m?.grade === v ? " checked" : ""}>${t}</label>`).join("")}
    ${only ? "" : `<label class="rv-g rv-g-repeat${m?.grade === "repeat" ? " on" : ""}" title="The same thing is already told in another row."><input type="radio" name="g-${esc(id)}" data-grade value="repeat"${m?.grade === "repeat" ? " checked" : ""}>Repeat</label>`}</div>`;
}
const readBoxes = (id, m) => `<div class="rv-reads">${READ.map(([v, t]) => `<label class="rv-r${m?.mark === v ? " on" : ""}"><input type="radio" name="r-${esc(id)}" data-read value="${v}"${m?.mark === v ? " checked" : ""}>${t}</label>`).join("")}</div>`;
const offBoxes = (m) => `<div class="rv-offs"><span class="muted small">What is off:</span> ${OFFS.map(([v, t]) => `<label><input type="checkbox" data-off value="${v}"${(m?.off || []).includes(v) ? " checked" : ""}> ${t}</label>`).join("")}</div>`;
const reasonBoxes = (m) => !["visible", "weak", "none"].includes(m?.grade) ? "" : `<div class="rv-offs rv-reasons"><span class="muted small">${m.grade === "visible" ? "What keeps it from Classic (optional):" : "Why:"}</span> ${REASONS.map(([v, t, tip]) => `<label${tip ? ` title="${esc(tip)}"` : ""}><input type="checkbox" data-reason value="${v}"${(m?.reason || []).includes(v) ? " checked" : ""}> ${t}</label>`).join("")}</div>`;
const words = (m, ph) => `<input type="text" data-why placeholder="${esc(ph)}" value="${esc(m?.why || "")}">`;

function sitControl(s, m) {
  const dec = isDecision(m);
  return `<td class="rv-mark" data-id="${esc(s.id)}" data-sit>${gradeBoxes(s.id, m)}
    ${dec ? `<div class="muted small rv-q">Did the engine read it correctly?</div>${readBoxes(s.id, m)}${["partly", "incorrect"].includes(m?.mark) ? offBoxes(m) : ""}` : ""}
    ${reasonBoxes(m)}
    ${words(m, dec ? "your words: what you see here" : m?.grade === "none" ? "your words: why this is not a decision" : "your words")}</td>`;
}
const callControl = (c, m) => `<td class="rv-mark" data-id="${esc(c.id)}">${readBoxes(c.id, m)}${words(m, "your words: is this the job, and is the result right")}</td>`;

function summary(g, M) {
  const S = g.situations, bands = ["high", "medium", "low", "none"], rowsOf = [...GRADE, ["repeat", "Repeat"], ["", "Not graded yet"]];
  const grade = (s) => M[s.id]?.grade || (band(s) === "none" ? "none" : "");
  const body = rowsOf.map(([v, t]) => { const R = S.filter((s) => grade(s) === v); if (!R.length) return "";
    const c = (k) => R.filter((s) => M[s.id]?.mark === k).length;
    return `<tr><td><span class="rv-dot rv-g-${v || "blank"} on"></span>${t}</td>${bands.map((b) => `<td>${R.filter((s) => band(s) === b).length || ""}</td>`).join("")}<td>${["classic", "visible", "weak"].includes(v) ? `${c("correct")} / ${c("partly")} / ${c("incorrect")}` : ""}</td></tr>`; }).join("");
  return `<details class="rv-terms" open><summary>Your grades against the engine's confidence (${S.length} situations; ${missedOf(g).length} added as missed)</summary>
    <table class="data rv-sum"><thead><tr><th>Your grade</th>${bands.map((b) => `<th>Engine: ${BAND[b]}</th>`).join("")}<th>Read correct / partly / incorrect</th></tr></thead><tbody>${body}</tbody></table></details>`;
}

function gameHtml(g) {
  const M = now(g);
  const body = g.situations.map((s) => {
    const m = M[s.id], b = band(s), asked = callsAsked(m) && b !== "none", not = whyNot(s, m);
    const calls = s.calls.map((c) => `<tr class="rv-call${asked && M[c.id]?.mark && M[c.id].mark !== SKIP ? " rv-done" : asked ? " rv-todo" : ""}${asked ? "" : " rv-skip"}"><td></td><td></td>
      <td><b>${esc(c.team)}</b>${c.side ? ` <span class="muted">(${esc(c.side)})</span>` : ""}${c.label ? ` <span class="pill type">${esc(c.label)}</span>` : ""}: ${esc(c.job)}.
        <b class="${c.met ? "rv-met" : "rv-not"}">${c.met ? "Met" : "Not met"}</b>${c.draft ? ` <span class="muted small">(this job is Claude's draft, not yet ruled)</span>` : ""}
        ${c.tests.length ? `<div class="muted small">${c.tests.map(([ok, t]) => `${esc(t)}: ${ok ? "yes" : "no"}`).join("; ")}</div>` : ""}</td>${asked ? callControl(c, M[c.id]) : `<td class="muted small">${esc(not)}</td>`}</tr>`).join("");
    if (b === "none") {     // the engine reads no decision: a thin row, folded, opened only to say that it was one
      const open = !!m?.grade;
      return `<tr class="rv-sit rv-none${open ? " rv-done" : ""}"><td class="rv-n">${s.n}</td><td class="rv-t">${clock(s.t0)}–${clock(s.t1)}</td><td colspan="2" class="rv-mark" data-id="${esc(s.id)}" data-sit>
        <details${open ? " open" : ""}><summary><span class="rv-conf rv-c-none">Engine: no decision</span> <span class="muted">${esc(s.reads)}</span></summary>
        <div class="muted small">Why the engine reads no decision: ${esc(s.confidence?.why || s.unclear || "")} Leave it as it is if you agree. If it was a decision, grade it and say what it was:</div>
        ${gradeBoxes(s.id, m, ["classic", "visible", "weak"])}${words(m, "your words: what the decision was")}${open ? ` <button class="btn small ghost" data-clear="${esc(s.id)}">Not a decision after all</button>` : ""}</details></td></tr>`;
    }
    return `<tr class="rv-sit${sitDone(s, m) ? " rv-done" : " rv-todo"}"><td class="rv-n">${s.n}</td><td class="rv-t">${clock(s.t0)}–${clock(s.t1)}</td>
      <td><span class="rv-conf rv-c-${b}" title="${esc(s.confidence?.why || "")}">Engine's confidence that this is a decision: ${BAND[b] || "not given"}</span><br>${esc(s.reads)}
        <div class="muted small">${esc(s.confidence?.why || "")}</div></td>${sitControl(s, m)}</tr>${calls}`;
  }).join("");
  const T = todo(g, M), done = T.filter((x) => x.done).length, n = unsaved(g);
  const notes = draft[g.rid]?.notes ?? marks.games?.[g.rid]?.notes ?? "";
  const missed = missedOf(g).map((x, i) => `<tr data-missed="${i}"><td><input type="text" data-m="t" placeholder="m:ss" value="${esc(x.t || "")}" style="width:5rem"></td>
    <td><select data-m="kind">${KINDS.map((k) => `<option${x.kind === k ? " selected" : ""}>${k}</option>`).join("")}</select></td>
    <td><div class="rv-grades">${GRADE.slice(0, 2).map(([v, t]) => `<label class="rv-g rv-g-${v}${x.grade === v ? " on" : ""}"><input type="radio" name="mg-${i}" data-m="grade" value="${v}"${x.grade === v ? " checked" : ""}>${t}</label>`).join("")}</div></td>
    <td><input type="text" data-m="why" placeholder="your words: what the decision was, whose, and what each side did" value="${esc(x.why || "")}" style="width:100%"></td>
    <td><button class="btn small ghost" data-unmiss="${i}">Remove</button></td></tr>`).join("");
  return `<h3 style="margin:.8rem 0 .2rem">${esc(g.teams.join(" v "))}, ${esc(g.map)}, ${esc(g.date)}</h3>
    <p style="margin:.2rem 0"><a href="https://gvg.report/report/${esc(g.rid)}#map" target="_blank" rel="noopener">Open the replay on gvg.report</a>. ${g.situations.length} situations, ${T.length} rows to mark; <b>${done} marked</b>${n ? `, <b class="rv-not">${n} not saved yet</b>` : ""}.</p>
    ${summary(g, M)}
    ${(g.selfcheck || []).length ? `<details class="rv-terms"><summary>The engine's own check: ${g.selfcheck.length} time${g.selfcheck.length === 1 ? "" : "s"} it counts a player in two fights at once (the numbers rows it touches are read as no decision)</summary><ul class="small">${g.selfcheck.map((x) => `<li>${esc(x)}</li>`).join("")}</ul></details>` : ""}
    <div class="row rv-bar"><button class="btn small primary" data-save>Save this game's marks</button>
      <button class="btn small ghost" data-rest title="Every call that is asked for and not yet marked is marked Correct. Use it after marking the calls that are partly right or incorrect.">Mark the unmarked calls Correct</button>
      <button class="btn small ${showTodo ? "primary" : "ghost"}" data-todo title="Rows you have not marked yet are shown in red. Press again to hide the red.">${showTodo ? "Hide" : "Show"} the rows not marked yet (${T.length - done})</button>
      ${showTodo && T.length - done ? `<button class="btn small ghost" data-nexttodo>Go to the next one</button>` : ""}</div>
    <div class="tablewrap"><table class="data rv-rows${showTodo ? " rv-showtodo" : ""}"><thead><tr><th>#</th><th>Time</th><th>The situation, then each side's call</th><th>Your grade and mark</th></tr></thead><tbody>${body}</tbody></table></div>
    <h4 style="margin:.9rem 0 .3rem">Decisions the engine did not read</h4>
    <p class="muted small" style="margin:.2rem 0">A decision you see in the game that has no row above, not even a folded one. Give its time, the kind of play, whether it is Classic or Visible, and what it was. A Classic one the engine must learn to read.</p>
    <div class="tablewrap"><table class="data rv-missed"><thead><tr><th>Time</th><th>Kind of play</th><th>Grade</th><th>Your words</th><th></th></tr></thead><tbody>${missed}</tbody></table></div>
    <div class="row rv-bar"><button class="btn small" data-addmiss>Add a missed decision</button></div>
    <h4 style="margin:.9rem 0 .3rem">Anything else about this game</h4>
    <textarea data-notes placeholder="Anything that holds for the whole game, or that does not fit a row." style="min-height:70px">${esc(notes)}</textarea>
    <div class="row rv-bar"><button class="btn small primary" data-save>Save this game's marks</button></div>`;
}

// A game marked before 2026-11-15: history, read only (R-491).
function historyHtml(g) {
  const M = saved(g), e = marks.games?.[g.rid] || {};
  const cell = (m) => m?.mark ? `<b>${esc(m.mark)}</b>${m.why ? `<div class="small">${esc(m.why)}</div>` : ""}` : `<span class="muted small">not marked</span>`;
  const body = g.situations.map((s) => `<tr class="rv-sit"><td class="rv-n">${s.n}</td><td class="rv-t">${clock(s.t0)}–${clock(s.t1)}</td><td>${esc(M[s.id]?.text || s.reads)}</td><td>${cell(M[s.id])}</td></tr>` +
    s.calls.map((c) => `<tr class="rv-call"><td></td><td></td><td>${esc(M[c.id]?.text || callText(c))}</td><td>${cell(M[c.id])}</td></tr>`).join("")).join("");
  return `<h3 style="margin:.8rem 0 .2rem">${esc(g.teams.join(" v "))}, ${esc(g.map)}, ${esc(g.date)} <span class="pill">history, read only</span></h3>
    <p style="margin:.2rem 0"><a href="https://gvg.report/report/${esc(g.rid)}#map" target="_blank" rel="noopener">Open the replay on gvg.report</a>. Marked ${esc(e.at || "")} against engine ${esc(e.engine || "")}, the earlier way (right, partly, wrong). Kept as a record: the engine is no longer held to these rows.</p>
    ${e.notes ? `<p class="small"><b>Your notes:</b> ${esc(e.notes)}</p>` : ""}
    <div class="tablewrap"><table class="data rv-rows"><thead><tr><th>#</th><th>Time</th><th>The row as you saw it</th><th>Your mark then</th></tr></thead><tbody>${body}</tbody></table></div>`;
}

async function renderGames(out, keep = false) {
  if (!keep || !rows) {
    rows = await readJson(ROWS, null);
    marks = (await readJson(MARKS, null)) || { about: "", games: {} };
    loadDraft();
  }
  if (!rows || !(rows.games || []).length) { out.innerHTML = `<h1>Game review</h1><div class="empty-state">No game has been set out for review yet.</div>`; return; }
  const G = rows.games, fresh = G.filter((x) => x.scheme === 2), old = G.filter((x) => x.scheme !== 2);
  const g = G.find((x) => x.rid === cur) || fresh[0] || G[0]; cur = g.rid;
  const isNew = g.scheme === 2;
  const button = (x) => { const T = x.scheme === 2 ? todo(x, now(x)) : [], d = T.filter((i) => i.done).length;
    return `<button class="btn small ${x.rid === cur ? "primary" : "ghost"}" data-game="${esc(x.rid)}">${esc(x.teams.join(" v "))}${x.scheme === 2 ? ` <span class="small">(${esc(x.label || `part ${x.part}`)}; ${d} of ${T.length})</span>` : ""}</button>`; };
  out.innerHTML = `<h1>Game review</h1>
  <p>The engine's reading of whole games. Watch the game and grade every situation: first whether it is a decision at all and how clear a one, then whether the engine read it as you do, then each side's job and result. ${canSave() ? "" : "<b>Add your GitHub key in Settings to save.</b>"}</p>
  <details class="rv-terms"><summary>How to mark a row</summary><ul class="small">
    <li><b>A situation</b> is one thing the engine saw happening between the two times: a flag run and the answer to it, a push on a flagger, a split and its defence, a numbers difference in the main fight, a team pinned in its base, a boost coming, a base resurrection, a Lord push.</li>
    <li><b>The engine's confidence</b> is shown first: how sure it is that this is a decision. It is measured by reading the game again with each of the engine's settings (its distances and times: how close players must stand to be in one fight, how long a player must be there to count) moved. <b>High</b>: the engine still reads the situation wherever they are set, down to half and up to double, and reads it the same way at a quarter either way. <b>Medium</b>: it is still read at a quarter either way, but who is counted in it or the call changes there, or it is no longer read at half or double. <b>Low</b>: a quarter's move of one setting and the engine no longer reads it; the line under it says which. These bands were fitted to your grades on the first five games, which still show the bands as they were when you marked them. <b>No decision</b>: the engine saw something and set it aside; these are the folded rows.</li>
    <li><b>Grade the moment as you see it in the game</b>, not the engine's wording of it. <span class="rv-g rv-g-classic on">Classic</span> a textbook example of this decision: the engine must read it exactly as you do. <span class="rv-g rv-g-visible on">Visible</span> a real decision a team would see in game, but messier or not the textbook case. <span class="rv-g rv-g-weak on">Weak</span> technically there, but not something a team would act on (a player up for a few seconds). <span class="rv-g rv-g-none on">No decision</span> nothing of this kind is happening (a player who passes near a split and never joins it). <span class="rv-g rv-g-repeat on">Repeat</span> the same thing is already told in another row: grade the row that tells it best, and mark the others Repeat.</li>
    <li>For a Classic, Visible or Weak decision, say whether the engine read it. <b>Correct</b>: it is what you would say. <b>Partly</b>: the engine has the right decision but a detail is off; tick which (the numbers, who, when, where). <b>Incorrect</b>: a decision is there, but a different one from what the engine says; tick Kind of play, and anything else that is off. Then say what you see in your own words.</li>
    <li>For a <b>Weak</b> or <b>No decision</b> grade, tick why: <b>Too brief</b>; <b>Impact too small to make a difference</b>; <b>No real fight, nothing at stake</b>; <b>Weak or unclear small edge in real game</b> (it may have been a borderline decision, but it is too unclear or weak ever to be read as a decision in a real game). More than one can be ticked. Under a Visible grade the same ticks are offered for what keeps it from Classic, and can be left empty. A row already told elsewhere is a Repeat; a decision the engine misread is Incorrect.</li>
    <li><b>A call</b> is what one team did about the situation. Its <b>job</b> is what a team is expected to achieve there by your rulings; <b>Met</b> or <b>Not met</b> says only whether that happened, and the small line under it lists each test with yes or no. Calls are asked for only under a Classic or Visible decision that the engine read Correct or Partly. For a call, <b>Correct</b> means that is the team's job there and the result is right; <b>Partly</b> means the job or the result is off; <b>Incorrect</b> means that is not what the team was doing.</li>
    <li><b>Folded rows</b> are moments the engine reads as no decision (numbers that never held 12 seconds, or a player it counts in two fights at once). Leave one alone if you agree; it is not counted among the rows to mark. Open it to say it was a decision.</li>
    <li><b>Decisions the engine did not read</b>, under the table: anything you see that has no row at all.</li>
    <li><b>Show the rows not marked yet</b>, beside the Save button, puts every row you still have to mark in red, with a count; press it again to hide the red. <b>Go to the next one</b> scrolls to the next red row.</li>
    <li>Marks are kept in this browser as you go and reach the engine when you press Save. Stop and resume at any point.</li>
  </ul></details>
  <div class="row rv-games">${fresh.map(button).join("")}</div>
  ${old.length ? `<details class="rv-terms"${isNew ? "" : " open"}><summary>Earlier games (history, read only): ${old.length}</summary><div class="row rv-games">${old.map(button).join("")}</div></details>` : ""}
  <p class="muted small">Rows written ${esc(rows.generated)} from engine ${esc(rows.engine)}.</p>
  <section class="rv">${isNew ? gameHtml(g) : historyHtml(g)}</section>
  <style>.rv-rows{table-layout:fixed;width:100%}.doc table.rv-rows td,.rv-rows td{vertical-align:top;white-space:normal!important;overflow-wrap:anywhere;padding:.35rem .5rem;font-size:.9rem}
  .rv-rows th:nth-child(1),.rv-n{width:2.4rem}.rv-rows th:nth-child(2),.rv-t{width:6.2rem;font-family:var(--mono);white-space:nowrap}.rv-rows th:nth-child(4),.rv-rows td.rv-mark:not([colspan]){width:25rem}
  .rv-sit td{border-top:2px solid var(--line);background:var(--accent-soft)}.rv-call td:nth-child(3){padding-left:1.4rem}.rv-done td:first-child{box-shadow:inset 3px 0 0 var(--ink)}
  .rv-none td{background:transparent;padding-top:.15rem!important;padding-bottom:.15rem!important}.rv-none summary{cursor:pointer}
  .rv-grades,.rv-reads{display:flex;flex-wrap:wrap;gap:.3rem;margin:.15rem 0}.rv-grades input,.rv-reads input{position:absolute;opacity:0;width:0;height:0}
  .rv-g{--c:#666;display:inline-block;border:2px solid var(--c);color:var(--c);background:#fff;font-weight:600;font-size:.82rem;padding:.2rem .55rem;cursor:pointer;white-space:nowrap}.rv-g.on{background:var(--c);color:#fff}
  .rv-g-classic{--c:#1c7c3c}.rv-g-visible{--c:#c26a00}.rv-g-weak{--c:#b3261e}.rv-g-none{--c:#1f5fbf}.rv-g-repeat{--c:#777;font-weight:500;font-size:.76rem;margin-left:.6rem;border-width:1px}.rv-g-blank{--c:#bbb}
  .rv-g:focus-within,.rv-r:focus-within{outline:2px solid var(--ink);outline-offset:1px}
  .rv-r{display:inline-block;border:1px solid var(--ink);background:#fff;color:var(--ink);font-size:.82rem;padding:.2rem .6rem;cursor:pointer}.rv-r.on{background:var(--ink);color:#fff}
  .rv-q{margin-top:.35rem}.rv-offs{margin:.25rem 0;font-size:.84rem}.rv-offs label{margin-right:.55rem;white-space:nowrap}
  .rv-mark input[type=text]{display:block;width:100%;height:1.9rem;margin-top:.3rem;font-size:.84rem}
  .rv-conf{display:inline-block;font-size:.74rem;font-weight:600;letter-spacing:.03em;border:1px solid var(--ink);padding:.05rem .4rem;margin-bottom:.2rem}.rv-c-high{background:var(--ink);color:#fff}.rv-c-low{border-style:dashed}.rv-c-none{border-style:dotted;color:var(--muted);border-color:var(--muted)}
  .rv-dot{display:inline-block;width:.7rem;height:.7rem;padding:0;margin-right:.4rem;vertical-align:baseline;background:var(--c,#bbb)}.rv-sum{width:auto}.rv-sum td,.rv-sum th{padding:.2rem .7rem;font-size:.86rem;text-align:center}.rv-sum td:first-child{text-align:left}
  .rv-missed td{vertical-align:middle;padding:.3rem .4rem}.rv-missed th:nth-child(4){width:55%}
  .rv-showtodo tr.rv-todo td{background:#fdecea}.rv-showtodo tr.rv-todo td:first-child{box-shadow:inset 5px 0 0 #b3261e}.rv-showtodo tr.rv-todo td.rv-mark{outline:2px solid #b3261e;outline-offset:-2px}
  .rv-skip td:nth-child(3){opacity:.5}.rv-met{color:#1c7c3c}.rv-not{color:#b3261e}.rv-bar{margin:.6rem 0;gap:.5rem}.rv-games{flex-wrap:wrap;gap:.4rem;margin:.6rem 0}.rv-terms{margin:.6rem 0}.rv-terms summary{cursor:pointer}.small{font-size:.86rem}</style>`;

  const redraw = async (focus) => { const y = scrollY; await renderReview(out, true); scrollTo({ top: y }); if (focus) out.querySelector(`.rv-mark[data-id="${CSS.escape(focus)}"] [data-why]`)?.focus({ preventScroll: true }); };
  out.querySelectorAll("[data-game]").forEach((b) => b.onclick = () => { cur = b.dataset.game; redraw(); });
  if (!isNew) return;

  const text = Object.fromEntries(g.situations.flatMap((s) => [[s.id, s.reads], ...s.calls.map((c) => [c.id, callText(c)])]));
  const bandOf = Object.fromEntries(g.situations.map((s) => [s.id, band(s)]));
  const put = (id, patch) => {
    const d = (draft[g.rid] ||= { marks: {} }); d.marks ||= {};
    d.marks[id] = { ...(saved(g)[id] || {}), ...(d.marks[id] || {}), ...patch, text: text[id], ...(id in bandOf ? { band: bandOf[id] } : {}) };
    keepDraft();
  };
  // When a situation's grade or mark changes, the calls under it are asked for or no longer asked for.
  const settle = (s) => { const ask = callsAsked(now(g)[s.id]) && band(s) !== "none";
    s.calls.forEach((c) => { const m = now(g)[c.id]?.mark; if (!ask && m !== SKIP) put(c.id, { mark: SKIP, why: "" }); else if (ask && m === SKIP) put(c.id, { mark: "", why: "" }); }); };
  out.querySelectorAll(".rv-rows .rv-mark").forEach((td) => {
    const id = td.dataset.id, why = td.querySelector("[data-why]"), s = td.hasAttribute("data-sit") ? g.situations.find((x) => x.id === id) : null;
    td.querySelectorAll("[data-grade]").forEach((r) => r.onchange = () => {
      const dec = ["classic", "visible", "weak"].includes(r.value);
      put(id, { grade: r.value, why: why.value.trim(), ...(dec ? {} : { mark: "", off: [] }), ...(["visible", "weak", "none"].includes(r.value) ? {} : { reason: [] }) }); settle(s); redraw(id);
    });
    td.querySelectorAll("[data-read]").forEach((r) => r.onchange = () => {
      put(id, { mark: r.value, why: why.value.trim(), ...(s && r.value === "correct" ? { off: [] } : {}) });
      if (s) { settle(s); redraw(id); } else { td.closest("tr").classList.add("rv-done"); td.closest("tr").classList.remove("rv-todo"); td.querySelectorAll(".rv-r").forEach((l) => l.classList.toggle("on", l.querySelector("input").checked)); if (r.value !== "correct") why.focus(); }
    });
    td.querySelectorAll("[data-off]").forEach((c) => c.onchange = () => put(id, { off: [...td.querySelectorAll("[data-off]:checked")].map((x) => x.value) }));
    td.querySelectorAll("[data-reason]").forEach((c) => c.onchange = () => put(id, { reason: [...td.querySelectorAll("[data-reason]:checked")].map((x) => x.value) }));
    why.onchange = () => { if (now(g)[id]?.grade || now(g)[id]?.mark) put(id, { why: why.value.trim() }); };
  });
  out.querySelectorAll("[data-todo]").forEach((b) => b.onclick = () => { showTodo = !showTodo; try { localStorage.setItem("gvginfo.review.todo", showTodo ? "1" : "0"); } catch { /* kept for this visit only */ } redraw(); });
  out.querySelectorAll("[data-nexttodo]").forEach((b) => b.onclick = () => {      // the first row not yet marked below the top of the window, else the first of all
    const T0 = [...out.querySelectorAll(".rv-rows tr.rv-todo")]; const tr = T0.find((r) => r.getBoundingClientRect().top > 90) || T0[0];
    tr?.scrollIntoView({ block: "center" }); });
  out.querySelectorAll("[data-clear]").forEach((b) => b.onclick = () => { put(b.dataset.clear, { grade: "", mark: "", off: [], reason: [], why: "" }); redraw(); });
  const miss = () => { const d = (draft[g.rid] ||= { marks: {} }); d.missed ??= JSON.parse(JSON.stringify(missedOf(g))); return d.missed; };
  out.querySelector("[data-addmiss]").onclick = () => { miss().push({ t: "", kind: "split", grade: "classic", why: "" }); keepDraft(); redraw().then(() => [...out.querySelectorAll('[data-m="t"]')].pop()?.focus()); };
  out.querySelectorAll("[data-unmiss]").forEach((b) => b.onclick = () => { miss().splice(+b.dataset.unmiss, 1); keepDraft(); redraw(); });
  out.querySelectorAll("[data-missed]").forEach((tr) => tr.querySelectorAll("[data-m]").forEach((el) => el.onchange = () => {
    miss()[+tr.dataset.missed][el.dataset.m] = el.value.trim(); keepDraft();
    if (el.dataset.m === "grade") tr.querySelectorAll(".rv-g").forEach((l) => l.classList.toggle("on", l.querySelector("input").checked));
  }));
  out.querySelector("[data-notes]").onchange = (e) => { (draft[g.rid] ||= { marks: {} }).notes = e.target.value.trim(); keepDraft(); };
  out.querySelector("[data-rest]").onclick = () => { const M = now(g); todo(g, M).forEach((x) => { if (x.call && !x.done) put(x.id, { mark: "correct", why: "" }); }); redraw(); };
  out.querySelectorAll("[data-save]").forEach((b) => b.onclick = async () => {
    const before = JSON.stringify(marks), d = draft[g.rid] || { marks: {} };
    marks.about = "Denning's marks on the rows of Model > Game review. Games with scheme 2 (R-492): for each situation his grade (classic, visible, weak, none = no decision, repeat), whether the engine read a decision correct, partly or incorrect, what he ticked as off, his words, the engine's confidence band and the text of the row as he saw them; for each call his mark and words; `missed` holds the decisions he added that the engine did not read. Games without a scheme were marked the earlier way (right, partly, wrong, no clear decision, repeat) and are history (R-491). Saved by the page; Claude files them in the review key.";
    const G0 = (marks.games ||= {}), e = (G0[g.rid] ||= { marks: {} });
    e.scheme = 2; e.game = `${g.teams.join(" v ")}, ${g.map}`; e.at = new Date().toISOString().slice(0, 10); e.engine = rows.engine;
    e.marks = Object.fromEntries(Object.entries({ ...e.marks, ...(d.marks || {}) }).filter(([, v]) => v.grade || v.mark));
    if (d.missed !== undefined) e.missed = d.missed.filter((x) => x.t || x.why);
    if (d.notes !== undefined) { if (d.notes) e.notes = d.notes; else delete e.notes; }
    try { await writeJson(MARKS, marks, `Game review: ${e.game} marked (${Object.keys(e.marks).length} rows, ${(e.missed || []).length} missed)`); }
    catch (err) { marks = JSON.parse(before); toast(err.message); return; }
    delete draft[g.rid]; keepDraft(); toast("Saved"); await redraw();
  });
}

// ---- Flag advice: the engine's sentence for each flag decision of the graded games
const cSaved = (g) => cmarks.games?.[g.rid]?.marks || {};
const cNow = (g) => ({ ...cSaved(g), ...(cdraft[g.rid]?.marks || {}) });
// A card that says something else than the card he marked (`changed` on the card, set when the cards are written: what happened is told differently, or the
// reading at the first look is another one; figures that only moved with the fit do not count) is to be marked again; his earlier marks are shown with it and
// kept under `was`. Once he has marked the card as it reads now, it is done
const cText = (c) => [c.head, c.spot, c.answer, c.followed, c.similar, c.second].filter(Boolean).join(" | ");
const cStale = (c, m) => !!c.changed && !!m?.text && m.text !== cText(c);
const cDone = (c, m) => !!m?.facts && !cStale(c, m) && (!c.reading || !!m?.sense);
const cWas = (m) => { const { was, text, ...rest } = m; return { ...rest, text }; };
const earlier = (m) => [m.facts && `told ${m.facts}`, m.sense && `the reading: ${m.sense}`, m.own && `your call: ${(OWN_WORDS[m.own] || m.own).toLowerCase()}`, m.why && `your words: "${m.why}"`].filter(Boolean).join("; ");
const pick = (id, key, list, m, cls) => `<div class="rv-reads">${list.map(([v, t]) => `<label class="rv-r${m?.[key] === v ? " on" : ""}"><input type="radio" name="${cls}-${esc(id)}" data-pick="${key}" value="${v}"${m?.[key] === v ? " checked" : ""}>${t}</label>`).join("")}</div>`;

function flagsHtml(g) {
  const M = cNow(g), done = g.cards.filter((c) => cDone(c, M[c.id])).length, n = Object.keys(cdraft[g.rid]?.marks || {}).length + (cdraft[g.rid]?.notes !== undefined ? 1 : 0);
  const notes = cdraft[g.rid]?.notes ?? cmarks.games?.[g.rid]?.notes ?? "";
  const body = g.cards.map((c, i) => { const m0 = M[c.id], old = cStale(c, m0), m = old ? null : m0;
    return `<tr class="rv-sit ${cDone(c, m0) ? "rv-done" : "rv-todo"}"><td class="rv-n">${i + 1}</td><td class="rv-t">${clock(c.t)}</td>
      <td><b>${esc(c.head)}</b><div>${esc(c.spot)}</div><div>${esc(c.answer)}</div><div>${esc(c.followed)}</div>
        <div class="rv-reading">${esc(c.similar)}</div>${c.second ? `<div class="rv-reading muted">${esc(c.second)}</div>` : ""}</td>
      <td class="rv-mark" data-id="${esc(c.id)}">${old ? `<div class="small rv-not">Please mark this card again. ${esc(c.changed)} Before, you marked: ${esc(earlier(m0))}.</div><details class="small"><summary>The card as you saw it</summary>${esc(m0.text)}</details>` : ""}
        <div class="muted small rv-q">Is what happened told correctly (the spot, the answer, what followed)?</div>${pick(c.id, "facts", READ, m, "f")}
        ${c.reading ? `<div class="muted small rv-q">Does the reading (similar spots) make sense to you?</div>${pick(c.id, "sense", SENSE, m, "s")}` : `<div class="muted small rv-q">No reading is given for this spot.</div>`}
        <div class="muted small rv-q">What would you have done here? (optional)</div>${pick(c.id, "own", OWN, m, "o")}
        ${words(m, "your words: what is wrong, or what the engine does not see")}</td></tr>`; }).join("");
  return `<h3 style="margin:.8rem 0 .2rem">${esc(g.teams.join(" v "))}, ${esc(g.map)}, ${esc(g.date)}</h3>
    <p style="margin:.2rem 0"><a href="https://gvg.report/report/${esc(g.rid)}#map" target="_blank" rel="noopener">Open the replay on gvg.report</a>. ${g.cards.length} flag decisions; <b><span data-cdone>${done}</span> marked</b>${n ? `, <b class="rv-not">${n} not saved yet</b>` : ""}.</p>
    ${g.cards.length ? `<div class="row rv-bar"><button class="btn small primary" data-csave>Save this game's marks</button></div>
    <div class="tablewrap"><table class="data rv-rows rv-cards${showTodo ? " rv-showtodo" : ""}"><thead><tr><th>#</th><th>Time</th><th>The decision as the engine reads it</th><th>Your marks</th></tr></thead><tbody>${body}</tbody></table></div>` : `<div class="empty-state">The engine reads no flag decision to answer in this game (its flags were the opening, or were run with Shadow of Haste).</div>`}
    ${(g.gone || []).length ? `<details class="rv-terms"><summary>${g.gone.length} card${g.gone.length === 1 ? "" : "s"} you marked that the engine no longer writes (your marks on ${g.gone.length === 1 ? "it" : "them"} are kept)</summary><ul class="small">${g.gone.map((x) => `<li>${clock(x.t)}: ${esc(x.head)} ${esc(x.answer)}</li>`).join("")}</ul></details>` : ""}
    <h4 style="margin:.9rem 0 .3rem">Anything else about the flags in this game</h4>
    <textarea data-cnotes placeholder="A flag decision with no card, or anything that holds for the whole game." style="min-height:70px">${esc(notes)}</textarea>
    <div class="row rv-bar"><button class="btn small primary" data-csave>Save this game's marks</button></div>`;
}

async function renderFlags(out, keep = false) {
  if (!keep || !cards) {
    cards = await readJson(CARDS, null);
    cmarks = (await readJson(CARD_MARKS, null)) || { about: "", games: {} };
    try { cdraft = JSON.parse(localStorage.getItem(CDRAFT) || "{}"); } catch { cdraft = {}; }
  }
  if (!cards || !(cards.games || []).length) { out.innerHTML = `<h1>Game review</h1><div class="empty-state">No flag advice has been set out yet.</div>`; return; }
  const G = cards.games, g = G.find((x) => x.rid === ccur) || G.find((x) => x.cards.length) || G[0]; ccur = g.rid;
  const keepC = () => { try { localStorage.setItem(CDRAFT, JSON.stringify(cdraft)); } catch { /* the marks stay on the page until saved */ } };
  out.innerHTML = `<h1>Game review</h1>
  <p>The engine's sentence for every flag decision in the games you graded: a team answering a flag run, or deciding whether to run again once its own flag is in. ${canSave() ? "" : "<b>Add your GitHub key in Settings to save.</b>"}</p>
  <details class="rv-terms"><summary>How to read and mark a card</summary><ul class="small">
    <li><b>The first lines are what happened</b>: who set off for a flag and who holds the stand; the spot (numbers at the main fight, where the team stands, each side's morale, the flag lead, the base res, the team's chance of winning); what the team did; and what followed over the next 180 seconds. The time is the second to go to in the replay. Mark them <b>Correct</b>, <b>Partly</b> or <b>Incorrect</b>, and say what is off.</li>
    <li><b>The similar-spots line is a reading, not advice.</b> It compares the two answers (a runner out by 15 s, or holding off) among teams in a like position, in win points 180 seconds on. It has not yet been shown to hold on matches the engine has not seen. Say whether it <b>makes sense</b> to you as a player.</li>
    <li><b>A second look</b>, where there is one, is the same question 30 seconds in, for a team that had still sent nobody.</li>
    <li><b>Please mark this card again</b> appears on a card that now says something else than when you marked it: what happened is told differently, or the reading at the first look has changed. Your earlier marks are shown with it and kept. Cards whose figures only moved a little keep your marks.</li>
    <li><b>What would you have done</b> is optional, and the most useful mark of the three: it is your call set against the engine's. <b>Send a runner at once</b> is a runner gone within about 15 seconds; <b>Look for a kill first, then send</b> is using the extra player for a short while and running once no kill is coming or their flag is plainly going to get in; <b>Hold off</b> is sending nobody. <b>It makes no difference here</b> means either answer is as good as the other in this spot; <b>I don't know</b> means you cannot say what you would do.</li>
    <li><b>Every number is said with whose it is</b>: "main fight Team 7 v HC 6 (Team up by 1)", each main team's place, each side's morale, and who is ahead on flags.</li>
    <li><b>Win points</b> are points of the chance of winning the match: +4 is a team going from 50% to 54%. A death is -15 morale on one player; the morale shown is the eight players summed.</li>
    <li>Marks are kept in this browser as you go and reach the engine when you press Save.</li>
  </ul></details>
  <div class="row rv-games">${G.map((x) => { const M = cNow(x), d = x.cards.filter((c) => cDone(c, M[c.id])).length;
    return `<button class="btn small ${x.rid === ccur ? "primary" : "ghost"}" data-cgame="${esc(x.rid)}">${esc(x.teams.join(" v "))} <span class="small">(${d} of ${x.cards.length})</span></button>`; }).join("")}</div>
  <p class="muted small">Cards written ${esc(cards.generated)} from engine ${esc(cards.engine)}.</p>
  <section class="rv">${flagsHtml(g)}</section>
  <style>.rv-rows{table-layout:fixed;width:100%}.doc table.rv-rows td,.rv-rows td{vertical-align:top;white-space:normal!important;overflow-wrap:anywhere;padding:.35rem .5rem;font-size:.9rem}
  .rv-rows th:nth-child(1),.rv-n{width:2.4rem}.rv-rows th:nth-child(2),.rv-t{width:4rem;font-family:var(--mono);white-space:nowrap}.rv-rows th:nth-child(4),.rv-rows td.rv-mark{width:24rem}
  .rv-sit td{border-top:2px solid var(--line)}.rv-done td:first-child{box-shadow:inset 3px 0 0 var(--ink)}.rv-cards td div{margin-top:.25rem}.rv-reading{border-left:3px solid var(--line);padding-left:.5rem}
  .rv-reads{display:flex;flex-wrap:wrap;gap:.3rem;margin:.15rem 0}.rv-reads input{position:absolute;opacity:0;width:0;height:0}
  .rv-r{display:inline-block;border:1px solid var(--ink);background:#fff;color:var(--ink);font-size:.82rem;padding:.2rem .6rem;cursor:pointer}.rv-r.on{background:var(--ink);color:#fff}.rv-r:focus-within{outline:2px solid var(--ink);outline-offset:1px}
  .rv-q{margin-top:.35rem}.rv-mark input[type=text]{display:block;width:100%;height:1.9rem;margin-top:.3rem;font-size:.84rem}
  .rv-not{color:#b3261e}.rv-bar{margin:.6rem 0;gap:.5rem}.rv-games{flex-wrap:wrap;gap:.4rem;margin:.6rem 0}.rv-terms{margin:.6rem 0}.rv-terms summary{cursor:pointer}.small{font-size:.86rem}</style>`;

  const redraw = async () => { const y = scrollY; await renderReview(out, true); scrollTo({ top: y }); };
  out.querySelectorAll("[data-cgame]").forEach((b) => b.onclick = () => { ccur = b.dataset.cgame; redraw(); });
  const text = Object.fromEntries(g.cards.map((c) => [c.id, cText(c)]));
  const put = (id, patch) => { const d = (cdraft[g.rid] ||= { marks: {} }); d.marks ||= {};
    const sv = cSaved(g)[id], card = g.cards.find((x) => x.id === id), base = !sv ? {} : !cStale(card, sv) ? sv : { was: [...(sv.was || []), cWas(sv)] };      // a card that says something else starts clean, his earlier marks kept under `was`
    d.marks[id] = { ...base, ...(d.marks[id] || {}), ...patch, text: text[id] }; keepC(); };
  out.querySelectorAll(".rv-cards .rv-mark").forEach((td) => {
    const id = td.dataset.id, why = td.querySelector("[data-why]");
    td.querySelectorAll("[data-pick]").forEach((r) => r.onchange = () => {
      put(id, { [r.dataset.pick]: r.value, why: why.value.trim() });
      td.querySelectorAll(".rv-r").forEach((l) => l.classList.toggle("on", l.querySelector("input").checked));
      const c = g.cards.find((x) => x.id === id), tr = td.closest("tr"), ok = cDone(c, cNow(g)[id]); tr.classList.toggle("rv-done", ok); tr.classList.toggle("rv-todo", !ok);
      const M1 = cNow(g), d1 = g.cards.filter((x) => cDone(x, M1[x.id])).length; out.querySelector("[data-cdone]").textContent = d1;
      const gb = out.querySelector(`[data-cgame="${CSS.escape(g.rid)}"] span`); if (gb) gb.textContent = `(${d1} of ${g.cards.length})`;
    });
    why.onchange = () => put(id, { why: why.value.trim() });
  });
  out.querySelector("[data-cnotes]").onchange = (e) => { (cdraft[g.rid] ||= { marks: {} }).notes = e.target.value.trim(); keepC(); };
  out.querySelectorAll("[data-csave]").forEach((b) => b.onclick = async () => {
    const before = JSON.stringify(cmarks), d = cdraft[g.rid] || { marks: {} };
    cmarks.about = "Denning's marks on the cards of Model > Game review > Flag advice. For each card: facts (is what happened told correctly: correct, partly, incorrect), sense (does the similar-spots reading make sense to him: agree, disagree, unsure), own (what he would have done: send = a runner at once, wait = look for a kill first and then send (offered from 2026-11-20), hold, nodiff = it makes no difference here, unknown = he does not know), his words, and the text of the card as he saw it. `was` holds his marks on a card as it read before it came to say something else. Marks on cards the engine no longer writes stay here under their ids (flag_cards.json lists those cards under `gone`). Only what he marked.";
    const G0 = (cmarks.games ||= {}), e = (G0[g.rid] ||= { marks: {} });
    e.game = `${g.teams.join(" v ")}, ${g.map}`; e.at = new Date().toISOString().slice(0, 10); e.engine = cards.engine;
    e.marks = Object.fromEntries(Object.entries({ ...e.marks, ...(d.marks || {}) }).filter(([, v]) => v.facts || v.sense || v.own || v.why));
    if (d.notes !== undefined) { if (d.notes) e.notes = d.notes; else delete e.notes; }
    try { await writeJson(CARD_MARKS, cmarks, `Flag advice: ${e.game} marked (${Object.keys(e.marks).length} cards)`); }
    catch (err) { cmarks = JSON.parse(before); toast(err.message); return; }
    delete cdraft[g.rid]; keepC(); toast("Saved"); await redraw();
  });
}

// The page: the two views and the switch between them.
export async function renderReview(out, keep = false) {
  if (view === "flags") await renderFlags(out, keep); else await renderGames(out, keep);
  const sw = document.createElement("div"); sw.className = "row rv-view"; sw.style.cssText = "gap:.4rem;margin:.4rem 0 .8rem";
  sw.innerHTML = [["games", "Decisions: is each read correctly?"], ["flags", "Flag advice: the engine's sentence for each flag decision"]]
    .map(([v, t]) => `<button class="btn small ${view === v ? "primary" : "ghost"}" data-view="${v}">${t}</button>`).join("");
  out.querySelector("h1")?.after(sw);
  sw.querySelectorAll("[data-view]").forEach((b) => b.onclick = () => { view = b.dataset.view; try { localStorage.setItem("gvginfo.review.view", view); } catch { /* for this visit only */ } renderReview(out); });
}
