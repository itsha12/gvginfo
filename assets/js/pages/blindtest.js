import { esc, readJson, writeJson, canSave, toast } from "../core.js";

// The blind test (Denning, November 2026 review). Rounds are added by the engine after each training chunk
// (tools/replay_analysis/advice.py) and never refreshed. For each pick Denning records his call before the model's is
// shown; once every call in a round is in, the round is scored here in the browser from the sealed part of each pick
// (base64: the actual choice, its win-chance change and the mean win-chance change of each choice among the 15 most
// similar decisions in other matches) and the result is saved back to the same file. Scoring matches advice.py.

const PATH = "data/model/blind_tests.json";
let data = null;
const open = new Set();          // picks whose model call Denning asked to see before saving (noted on the pick)

const clock = (t) => `${Math.floor(t / 60)}:${String(Math.round(t % 60)).padStart(2, "0")}`;
const unseal = (b64) => JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(b64), (c) => c.charCodeAt(0))));
const fmt = (x) => (x === null || x === undefined ? "–" : (x > 0 ? "+" : "") + (Math.round(x * 10) / 10));
const KIND = {
  enemy_pickup: "Enemy pickup", split_in_base: "Split in the base", power_play: "Power play", boost_clock: "Boost clock",
  after_wipe: "After a wipe", split_or_stay: "Split or stay", runner_choice: "Runner choice", offence_or_defence: "Offence or defence",
  eight_v_eight_or_flag: "8v8 or flag game", who_defends: "Who defends", npcs_or_dp: "NPCs or DP", play_for_28_or_lord: "Play for 28 or the Lord",
};

function situation(s) {
  if (!s) return "";
  const parts = [];
  if (s.phase) parts.push(`${esc(s.phase)} game`);
  if (s.flag_lead !== undefined) parts.push(`flags ${s.flag_lead > 0 ? "+" : ""}${esc(s.flag_lead)} s${s.stand ? ` (stand: ${esc(s.stand)})` : ""}`);
  if (s.boost_in !== undefined && s.boost_in !== null) parts.push(`boost in ${esc(s.boost_in)} s`);
  if (s.alive) parts.push(`alive ${esc(s.alive)}`);
  if (s.main) parts.push(`main ${esc(s.main)}`);
  if (s.dp !== undefined) parts.push(`DP ${esc(s.dp)}`);
  if (s.npcs !== undefined) parts.push(`NPC value ${esc(s.npcs)}`);
  if (s.lord_damage) parts.push(`Lord damage ${esc(s.lord_damage)}`);
  if (s.builds) parts.push(`builds: ${esc(s.builds)}`);
  return parts.join(" · ");
}

function scoreRound(rd) {
  const tot = { model: 0, denning: 0, usual: 0 }, hit = { model: 0, denning: 0, usual: 0 }, rows = [];
  for (const p of rd.picks) {
    const s = unseal(p.sealed), eff = s.choice_effects || {};
    const row = { id: p.id, actual_choice: s.actual_choice, outcome_wp_change: s.wp_change };
    for (const [who, call] of [["model", p.model_call], ["denning", p.denning_call], ["usual", p.usual_play]]) {
      const e = eff[call];
      row[who] = { call, expected: e ? e.mean_wp_change : null, cases: e ? e.cases : 0, matched_actual: call === s.actual_choice };
      if (e) tot[who] += e.mean_wp_change;
      if (call === s.actual_choice) hit[who] += 1;
    }
    rows.push(row);
  }
  const totals = {};
  for (const who of ["model", "denning", "usual"]) totals[who] = { expected_wp_change_sum: Math.round(tot[who] * 10) / 10, matched_actual: hit[who] };
  return { at: new Date().toISOString().slice(0, 10), picks: rows, totals };
}

function pickHtml(rd, p) {
  const answered = !!p.denning_call;
  const showModel = answered || open.has(`${rd.id}:${p.id}`);
  return `<div class="bt-pick" data-pick="${p.id}">
    <div class="row" style="justify-content:space-between"><b>${p.id}. ${esc(KIND[p.kind] || p.kind)}</b>
      <span class="muted small">${esc(p.team)} v ${esc(p.opponent || "?")}${p.map ? `, ${esc(p.map)}` : ""}, at ${clock(p.t)}${p.specific && answered ? ' · <span title="the model\'s call differs from the usual play">specific advice</span>' : ""}</span></div>
    <p class="muted small" style="margin:.3rem 0 .6rem">${situation(p.situation)}</p>
    <div class="row">${(p.choices_seen || []).map((c) => `<button class="btn small${p.denning_call === c ? " primary" : ""}" data-call="${esc(c)}"${answered ? " disabled" : ""}>${esc(c)}</button>`).join("")}</div>
    <textarea data-reason placeholder="Why (optional)"${answered ? " disabled" : ""} style="min-height:48px;margin:.5rem 0">${esc(p.denning_reason || "")}</textarea>
    <div class="row">
      ${answered ? "" : `<button class="btn small primary" data-save>Save my call</button><button class="btn small ghost" data-peek>Show the model's call first</button>`}
      ${showModel ? `<span class="small">Model: <b>${esc(p.model_call)}</b> · usual play: ${esc(p.usual_play)}${p.peeked ? ' <span class="muted">(seen before calling)</span>' : ""}</span>` : `<span class="muted small">The model's call is shown after you save yours.</span>`}
    </div>
  </div>`;
}

function scoredHtml(rd) {
  const sc = rd.scored, T = sc.totals;
  const who = (w) => `${fmt(T[w].expected_wp_change_sum)} pts, matched the team ${T[w].matched_actual} of ${rd.picks.length}`;
  return `<p><b>Scored ${esc(sc.at)}.</b> Expected win-chance change summed over the round (each call priced by what teams making that choice in that situation went on to do), and how often each call matched what the team actually did.</p>
  <ul><li>You: ${who("denning")}</li><li>Model: ${who("model")}</li><li>Usual play: ${who("usual")}</li></ul>
  <div class="tablewrap"><table class="data"><thead><tr><th>#</th><th>Decision</th><th>Moment</th><th>Your call</th><th>Model</th><th>Usual</th><th>Team did</th><th class="num">Outcome</th></tr></thead><tbody>
  ${rd.picks.map((p) => { const r = sc.picks.find((x) => x.id === p.id); const cell = (c) => `${esc(c.call)}<br><span class="muted small">${fmt(c.expected)}${c.matched_actual ? " ✓" : ""}</span>`;
    return `<tr><td>${p.id}</td><td>${esc(KIND[p.kind] || p.kind)}</td><td class="wrap small">${esc(p.team)} v ${esc(p.opponent || "?")} ${clock(p.t)}${p.denning_reason ? `<br><span class="muted">${esc(p.denning_reason)}</span>` : ""}</td><td>${cell(r.denning)}</td><td>${cell(r.model)}</td><td>${cell(r.usual)}</td><td>${esc(r.actual_choice)}</td><td class="num">${fmt(r.outcome_wp_change)}</td></tr>`; }).join("")}
  </tbody></table></div>
  <p class="muted small">✓ = the call matched what the team did. Points under a call = the mean win-chance change of teams that made it in the 15 most similar decisions (a blank means no similar team made that call). Outcome = this team's win-chance change over the decision's window.</p>`;
}

function historyHtml(rounds) {
  const done = rounds.filter((r) => r.status === "scored");
  if (!done.length) return "";
  const sum = (w, k) => done.reduce((a, r) => a + (r.scored.totals[w][k] || 0), 0);
  const n = done.reduce((a, r) => a + r.picks.length, 0);
  return `<h3>Across ${done.length} scored round${done.length === 1 ? "" : "s"} (${n} picks)</h3>
  <div class="tablewrap"><table class="data"><thead><tr><th>Caller</th><th class="num">Expected points</th><th class="num">Matched the team</th></tr></thead><tbody>
  ${["denning", "model", "usual"].map((w) => `<tr><td>${w === "denning" ? "You" : w === "model" ? "Model" : "Usual play"}</td><td class="num">${fmt(sum(w, "expected_wp_change_sum"))}</td><td class="num">${sum(w, "matched_actual")} of ${n}</td></tr>`).join("")}
  </tbody></table></div>`;
}

export async function renderBlindTest(out) {
  data = await readJson(PATH, { rounds: [] });
  const rounds = [...(data.rounds || [])].sort((a, b) => b.id - a.id);
  const openRounds = rounds.filter((r) => r.status === "open");
  out.innerHTML = `<h1>Blind test</h1>
  <p>Ten seconds of a stored match, the situation, and the choices teams made there. Record your call before the model's is shown; when all picks in a round are answered, score it. A round is added after every training chunk and waits until you answer it. ${canSave() ? "" : '<b>Add your GitHub key in Settings to save calls.</b>'}</p>
  ${!rounds.length ? `<div class="empty-state">No rounds yet. The next training run adds one.</div>` : ""}
  ${openRounds.map((rd) => `<section class="bt-round" data-round="${rd.id}"><h2>Round ${rd.id} <span class="muted small">(${esc(rd.created)}, model trained on ${esc(rd.matches_trained)} matches${rd.batch ? `, batch ${esc(rd.batch)}` : ""}; ${rd.picks.filter((p) => p.denning_call).length} of ${rd.picks.length} answered)</span></h2>
    ${rd.picks.map((p) => pickHtml(rd, p)).join("")}
    ${rd.picks.every((p) => p.denning_call) ? `<p><button class="btn primary" data-score>Score this round</button></p>` : ""}</section>`).join("")}
  ${historyHtml(rounds)}
  ${rounds.filter((r) => r.status === "scored").map((rd) => `<section class="bt-round"><h2>Round ${rd.id} <span class="muted small">(${esc(rd.created)}, ${esc(rd.matches_trained)} matches)</span></h2>${scoredHtml(rd)}</section>`).join("")}
  <style>.bt-pick{border:1px solid var(--line);padding:.9rem 1rem;margin:.8rem 0}.bt-round h2{margin-top:2rem}.small{font-size:.86rem}</style>`;

  const save = async (msg) => { await writeJson(PATH, data, msg); };
  out.querySelectorAll(".bt-round[data-round]").forEach((sec) => {
    const rd = data.rounds.find((r) => r.id === +sec.dataset.round);
    sec.querySelectorAll(".bt-pick").forEach((el) => {
      const p = rd.picks.find((x) => x.id === +el.dataset.pick);
      let chosen = p.denning_call;
      el.querySelectorAll("[data-call]").forEach((b) => b.onclick = () => { chosen = b.dataset.call; el.querySelectorAll("[data-call]").forEach((x) => x.classList.toggle("primary", x === b)); });
      el.querySelector("[data-peek]")?.addEventListener("click", () => { open.add(`${rd.id}:${p.id}`); p.peeked = true; renderBlindTest(out); });
      el.querySelector("[data-save]")?.addEventListener("click", async () => {
        if (!chosen) { toast("Pick a call first."); return; }
        p.denning_call = chosen; p.denning_reason = el.querySelector("[data-reason]").value.trim();
        try { await save(`Blind test: round ${rd.id}, pick ${p.id} called`); toast("Saved"); } catch (e) { toast(e.message); p.denning_call = null; }
        renderBlindTest(out);
      });
    });
    sec.querySelector("[data-score]")?.addEventListener("click", async () => {
      rd.scored = scoreRound(rd); rd.status = "scored";
      try { await save(`Blind test: round ${rd.id} scored`); toast("Scored"); } catch (e) { toast(e.message); delete rd.scored; rd.status = "open"; }
      renderBlindTest(out);
    });
  });
}
