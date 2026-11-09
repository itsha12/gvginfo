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
const QUESTION = {
  enemy_pickup: "the enemy just picked up its flag: what does the team do?", split_in_base: "an enemy split has entered the base: how is it answered?",
  power_play: "the team has the numbers at main: push or hold?", boost_clock: "the enemy's boost is near: run, fall back, advance or fight?",
  after_wipe: "the team just wiped the enemy: push the pit, take the flag or hold?", split_or_stay: "start a split in the next 30 s, or stay together?",
  runner_choice: "a fresh flag at the spawn: who carries it?", offence_or_defence: "a fight starts: do the disruptors play offensively (on enemy healers) or defensively (on enemy midline and frontline)?",
  eight_v_eight_or_flag: "the enemy picks up with 7+ of the team alive: commit all 8 to kill, or keep the flag game?", who_defends: "a split enters the base: who goes to defend, and with a collapse?",
  npcs_or_dp: "3+ enemies dead in their base: take NPCs before the res, or chase DP on the survivors?", play_for_28_or_lord: "the team has taken enemy NPCs: play safe for 28 (win on Lord damage) or push for the kill?",
};
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

// zones are recorded from each team's own point of view; shown from the deciding team's
function zoneName(z, mine, own, enemy) {
  const m = { "own base": `${own}'s base`, "own pit": `${own}'s pit`, "enemy base": `${enemy}'s base`, "enemy pit": `${enemy}'s pit`,
    "push side": `${own}'s push side (toward ${enemy}'s base)`, "backside": `${own}'s backside (own half)`, stand: "the stand", dead: "dead", field: "the field" };
  const e = { "own base": `${enemy}'s base`, "own pit": `${enemy}'s pit`, "enemy base": `${own}'s base`, "enemy pit": `${own}'s pit`,
    "push side": `${enemy}'s push side (toward ${own}'s base)`, "backside": `${enemy}'s backside (their half)`, stand: "the stand", dead: "dead", field: "the field" };
  return (mine ? m : e)[z] || z;
}
function sideHtml(c, mine) {
  const own = c.team, enemy = c.opponent || "?", t = mine ? c.own : c.enemy;
  if (!t) return "";
  const order = ["stand", "push side", "field", "backside", "own base", "own pit", "enemy base", "enemy pit", "dead"];
  const zones = Object.entries(t.zones || {}).sort((a, b) => order.indexOf(a[0]) - order.indexOf(b[0]))
    .map(([z, rs]) => `${zoneName(z, mine, own, enemy)}: ${rs.join(", ")}`).join(" · ");
  const flag = t.flag_lead === null || t.flag_lead === undefined ? "" : `flags ${t.flag_lead > 0 ? "+" : ""}${t.flag_lead} s (${t.flag_lead > 0 ? "could capture that much sooner than the other side" : t.flag_lead < 0 ? "the other side could capture that much sooner" : "even"})`;
  const npc = t.pit_npcs ? `pit: ${esc(t.pit_npcs).replace(/K(\d+) A(\d+) B(\d+)/, "knights $1, archers $2, bodyguard $3")}` : "";
  return `<div class="bt-side"><b>${esc(t.tag)}</b> <span class="muted">(${esc(t.build || "?")}${t.healing_monks ? `, ${t.healing_monks} healing monks` : ""}${t.spike_build ? ", spike build" : ""})</span>:
    ${t.alive} alive${t.dead?.length ? ` (dead: ${esc(t.dead.join(", "))})` : ""}, main group ${t.main}${t.main_roles?.length ? ` (${esc(t.main_roles.join(", "))})` : ""}.<br>
    <span class="small">Where: ${esc(zones) || "–"}.</span><br>
    <span class="small">${esc(flag)}${t.flag_how ? `; flag: ${esc(t.flag_how)}` : ""}${t.waiting_runner ? `; runner waiting: ${esc(t.waiting_runner)}` : ""}; morale ${t.morale > 0 ? "+" : ""}${t.morale ?? "?"}; ${npc} (worth ${t.npc_value ?? "?"} win points); Lord damage dealt ${t.lord_damage ?? 0}${t.lord_health !== undefined && t.lord_health !== null ? `, own Lord at ${Math.round(t.lord_health * 100)}%` : ""}.</span></div>`;
}
function contextHtml(p) {
  const c = p.context;
  if (!c) return `<p class="muted small">${situation(p.situation)}</p>`;
  const st = c.stand || {};
  const stand = st.owner ? `${esc(st.owner)} holds the stand (${st.held_s} s held${st.boost_in !== null && st.boost_in !== undefined ? `, boost in ${st.boost_in} s` : ""})` : "nobody holds the stand";
  const sp = c.split ? `<p class="small" style="margin:.3rem 0"><b>Split in play:</b> ${esc(c.split.team)}'s ${esc((c.split.members || []).join(" + "))}${c.split.entered_base !== null && c.split.entered_base !== undefined ? ` entered ${esc(c.split.team === c.team ? c.opponent : c.team)}'s base at ${clock(c.split.entered_base)}` : ` started at ${clock(c.split.start)}`}${c.split.main_numbers ? ` (mains meanwhile about ${Math.round(c.split.main_numbers[0])} v ${Math.round(c.split.main_numbers[1])})` : ""}.</p>` : "";
  return `<p class="small" style="margin:.4rem 0"><b>The call is ${esc(c.team)}'s</b> (against ${esc(c.opponent || "?")}), ${esc(p.map || c.map || "")}, at ${clock(c.t)}; ${stand}; next res in ${c.res_in ?? "?"} s${c.mains_apart ? `; the two main groups are ${Math.round(c.mains_apart / 100) * 100} units apart` : ""}.
    <a href="https://gvg.report/report/${esc(p.match)}#map" target="_blank" rel="noopener">Open the replay on gvg.report</a> and drag the time to ${clock(c.t)}.</p>
    ${sideHtml(c, true)}${sideHtml(c, false)}${sp}`;
}

function pickHtml(rd, p) {
  const answered = !!p.denning_call;
  const showModel = answered || open.has(`${rd.id}:${p.id}`);
  return `<div class="bt-pick" data-pick="${p.id}">
    <div class="row" style="justify-content:space-between"><b>${p.id}. ${esc(KIND[p.kind] || p.kind)}: ${esc(QUESTION[p.kind] || "")}</b>
      <span class="muted small">${esc(p.team)} v ${esc(p.opponent || "?")}${p.map ? `, ${esc(p.map)}` : ""}, at ${clock(p.t)}${p.specific && answered ? ' · <span title="the model\'s call differs from the usual play">specific advice</span>' : ""}</span></div>
    ${contextHtml(p)}
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
  <details class="bt-terms"><summary>The terms used in a pick</summary><ul class="small">
    <li><b>The call is X's</b>: you decide for team X; everything "own" is X's, "the other side" is the opponent.</li>
    <li><b>Flags +N s</b>: X could capture N seconds sooner than the opponent on the next exchange (its flag is nearer the stand, or the opponent's is further); -N the reverse. "Flag: carrying (role)" says who has X's flag.</li>
    <li><b>Stand</b>: who holds it, for how long, and when the holder's next morale boost lands (every 2 minutes held).</li>
    <li><b>Morale</b>: the team's death penalty and boosts summed over its eight players (each -60 to +10).</li>
    <li><b>Pit</b>: pit NPCs alive (knights, archers, bodyguard) and what they are worth in win points by the win model (footmen are not counted here).</li>
    <li><b>Main group</b>: players within 2,500 units of each other, not splitting or running. "Where" lists every player by zone; dead players are named.</li>
    <li><b>Push side / backside</b>: the half of the map toward the opponent's base, or toward one's own.</li>
    <li><b>Lord damage dealt</b>: by that team on the enemy Lord so far (the 28:00 tiebreak); own Lord at N% is the team's own Lord's health.</li>
    <li>The replay link opens gvg.report's map replay; drag its time slider to the pick's time. Positions and events there are the source of all of this.</li>
  </ul></details>
  ${!rounds.length ? `<div class="empty-state">No rounds yet. The next training run adds one.</div>` : ""}
  ${openRounds.map((rd) => `<section class="bt-round" data-round="${rd.id}"><h2>Round ${rd.id} <span class="muted small">(${esc(rd.created)}, model trained on ${esc(rd.matches_trained)} matches${rd.batch ? `, batch ${esc(rd.batch)}` : ""}; ${rd.picks.filter((p) => p.denning_call).length} of ${rd.picks.length} answered)</span></h2>
    ${rd.picks.map((p) => pickHtml(rd, p)).join("")}
    ${rd.picks.every((p) => p.denning_call) ? `<p><button class="btn primary" data-score>Score this round</button></p>` : ""}</section>`).join("")}
  ${historyHtml(rounds)}
  ${rounds.filter((r) => r.status === "scored").map((rd) => `<section class="bt-round"><h2>Round ${rd.id} <span class="muted small">(${esc(rd.created)}, ${esc(rd.matches_trained)} matches)</span></h2>${scoredHtml(rd)}</section>`).join("")}
  <style>.bt-pick{border:1px solid var(--line);padding:.9rem 1rem;margin:.8rem 0}.bt-side{margin:.35rem 0 .35rem;padding-left:.6rem;border-left:2px solid var(--line)}.bt-terms{margin:.6rem 0 1rem}.bt-terms summary{cursor:pointer}.bt-round h2{margin-top:2rem}.small{font-size:.86rem}</style>`;

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
