// What the trim of a replay leaves out and the engine needs from the rebuild on (format gvginfo.extras.v1): kept in a
// file of its own beside each stored replay, <month>/<report id>.x.json.gz, so that the stored replays themselves are
// never written again (the engine on main reads them as they are). Pure function: no network.
//
// Agent numbers are those of the stored replay (the index in its `agents` list); an agent the stored replay does not
// have is listed here under `agents` with the next numbers. Times are tenths of a second of match time, as in the trim.
// Amounts are gvg.report's own estimates, rounded to one decimal.
//
// Output:
//   agents        [{a, k, n, team, npc}]       only the agents the stored replay lacks
//   flag_objects  [[t, object id, type id, x, y]]   R-481: every flag object as it appears (a flag back at its spawn is a return)
//   lord          R-632, R-634, R-635: gvg.report's own Lord damage record
//     scores      {team: {damage, blind, own_effects, penalty, aggressiveness}}
//     lords       {team: {a, max_hp, damage, life_steal, healing, hits_under_entourage}}
//     events      [[t, the Lord's team, kind (d damage, l life steal, h heal, e effect), amount, Blind miss worth,
//                   effect cost, Entourage up, source agent, source team, skill id, effect name, pit NPCs alive]]
//     deaths      [[t, the Lord's team, kind of pit NPC]]      entourage  [[the Lord's team, t, tenths]]
//     health      {team: [[t, health, max]]} where it changes (gvg.report's estimate)      worth  the scoring constants
//     check       null, or what does not rebuild from the events (R-460: said, never hidden)
//   skills        R-636, R-638: {agent: [[row key, skill id, condition, source skill id, uses, attacks blocked,
//                   knockdowns prevented, healing, overhealing, Divine Favor healing, Divine Favor overhealing,
//                   damage prevented, degen dealt, regen given]]}    rows with none of those figures are left out
//   targets       [[caster, skill id, list (c cast on, h healed, d damaged), target, casts, damage, healing, overhealing,
//                   Divine Favor healing, damage prevented, degen, regen]]   c and h rows with healing or prevention,
//                   d rows with degen (the target may be an NPC or a Lord)
//   received      [[player, source, skill id, condition, source skill id, casts, healing, overhealing, Divine Favor
//                   healing, damage prevented, attacks blocked, degen taken, regen received]]
//   lord_effects  [[start, end, family (e enchantment, h hex, w weapon spell, ...), skill id, caster, the Lord, how it ended]]
//   strip_links   [[end, skill id, caster, target, removed by agent, removed by skill id]]   gvg.report's own link, where
//                   it has one (reports it read from early November 2026): a check only, our replays are the source (R-637)
//   recaps        one a death and one a survived spike (R-636, R-638):
//     {t, kind (death, save), who, survived, hp [start, end, max], totals {...}, split {...} (a save's pressure),
//      dmg [[source, skill id, condition, amount, events]], heal [[source, skill id, attribution, amount, events]],
//      prev [[source, skill id, kind, attacks blocked, amount, events]],
//      prots [[caster, skill id, start, end, still up, blocks attacks, stops knockdown, prot proc]],
//      pips [[family, condition, skill id, caster, start, end, still up, pips]], kd [[t, seconds]],
//      intr [[t, interrupter, interrupt skill id, interrupted skill id]], cond [ms, share, applications, [still up]],
//      dw [[start, end, skill id, amount]]}
//   degen         R-638: {agent: [degen dealt, degen dealt gross, degen taken, degen taken gross, regen received,
//                   regen given, net health from regen and degen taken]}
//   degen_sources {agent: [[skill id, [conditions], degen dealt, gross, players hit]]}; degen_coverage {agent: share credited to a skill}
//   attempts      R-639: [[started, resolved, interrupter, skill id, target, hit (1 or 0), gvg.report's read of a miss,
//                   ms after the cast began]]      fakes  [[agent, likely fake casts]]      attempt_totals {...}
//   energy        gvg.report's energy model, its own estimate with bounds: {step, start, model, players: {agent: {lo, hi, cap}}}
//                   lo and hi = the least and most energy a player can have, one value every `step` tenths from `start`
//                   (null where unread); cap = [[t, maximum energy]] where it changes

export const EXTRAS_VERSION = 1;
const r1 = (x) => (x == null || !isFinite(x) ? 0 : Math.round(x * 10) / 10);
const LORD_KIND = { damage: "d", life_steal: "l", heal: "h", healing: "h", effect: "e" };

export function buildExtras(payload, summaryPayload, stored) {
  const sum = summaryPayload?.summary || null;
  const ov = payload.overview || {}, rep = payload.report || {};
  const sess = ov.session || {}, clock = sess.observed_match_clock || {};
  // the same clock as replay_trim.mjs: the match clock starts after the prep time
  const t0 = (sess.started_at_ts || rep.sessions?.[0]?.started_at_ts || 0) + ((clock.instance_start_ms ?? 0) - (clock.match_start_ms ?? 0));
  const T = (ts) => (ts == null ? null : Math.round((ts - t0) / 100));

  const idx = new Map(), added = [];
  (stored?.agents || []).forEach((a, i) => idx.set(a.k, i));
  const base = idx.size;
  const A = (k, info = null) => {
    if (!k) return null;
    if (!idx.has(k)) { idx.set(k, base + added.length); added.push({ a: base + added.length, k, n: info?.n || k, team: info?.team ?? null, ...(info?.npc ? { npc: info.npc } : {}) }); }
    return idx.get(k);
  };

  const out = { format: "gvginfo.extras.v1", v: EXTRAS_VERSION, id: payload.id, summary: !!sum };

  // --- flag objects (R-481), from the replay payload
  out.flag_objects = (rep.objectives?.object_transitions || []).map((o) =>
    [T(o.ts_unix_ms), o.object_agent_id ?? null, o.object_type_id ?? null, Math.round(o.position?.x ?? 0), Math.round(o.position?.y ?? 0)]);

  // --- energy, from the replay payload
  out.energy = energyOf(rep.energy_state, A, T);

  if (sum) {
    out.lord = lordOf(sum.objectives?.guild_lord_damage, A, T);
    Object.assign(out, playersOf(sum.players || [], A));
    const lords = new Set((sum.objectives?.guild_lord_damage?.guild_lords || []).map((g) => g.agent_key));
    const iv = sum.skill_analytics?.skill_effect_intervals || [];
    out.lord_effects = iv.filter((e) => lords.has(e.target_agent_key)).map((e) =>
      [T(e.started_at_ts), T(e.ended_at_ts), String(e.family || "?")[0], e.skill_id ?? null, A(e.caster_agent_key), A(e.target_agent_key), e.close_reason || null]);
    out.strip_links = iv.filter((e) => e.removed_by_agent_key || e.removed_by_skill_id).map((e) =>
      [T(e.ended_at_ts), e.skill_id ?? null, A(e.caster_agent_key), A(e.target_agent_key), A(e.removed_by_agent_key), e.removed_by_skill_id ?? null]);
    out.recaps = [...(sum.death_recaps?.deaths || []).map((d) => recapOf(d, "death", A, T)),
      ...(sum.spike_saves?.saves || []).map((d) => recapOf(d, "save", A, T))].sort((x, y) => (x.t ?? 0) - (y.t ?? 0));
    const tm = sum.skill_analytics?.interrupts?.targeted_mesmer_interrupts || {};
    out.attempts = (tm.attempts || []).map((e) => [T(e.interrupt_attempt_started_at_ts_unix_ms ?? e.ts_unix_ms), T(e.interrupt_attempt_resolved_at_ts_unix_ms),
      A(e.source_agent_key), e.skill_id ?? null, A(e.target_agent_key), e.hit ? 1 : 0, e.hit ? null : e.missed_read?.kind || null,
      e.missed_read?.landed_after_cast_ms ?? e.missed_read?.cast_delta_ms ?? null]);
    out.fakes = (tm.by_fake_caster || []).map((f) => [A(f.agent_key), f.fake_casts ?? 0]);
    out.attempt_totals = tm.totals || null;
  }
  out.agents = added;
  return out;
}

function lordOf(g, A, T) {
  if (!g) return null;
  const t = (e) => (e.ts_unix_ms != null ? T(e.ts_unix_ms) : e.match_time_ms != null ? Math.round(e.match_time_ms / 100) : null);
  const events = (g.events || []).map((e) => [t(e), e.guild_lord_team_id, LORD_KIND[e.kind] || e.kind, r1(e.amount_estimate),
    e.kind === "damage" ? r1(e.blind_miss_activity_equivalent) : 0, e.kind === "effect" ? r1(e.activity_equivalent) : 0,
    e.entourage_active ? 1 : 0, A(e.source_agent_key), e.source_team_id ?? null, e.skill_id ?? null, e.effect_name || "", e.defenders_alive_total ?? null])
    .sort((x, y) => (x[0] ?? 0) - (y[0] ?? 0));
  const scores = {}, problems = [];
  for (const sc of g.team_scores || []) {
    const tm = sc.team_id;
    if (tm !== 1 && tm !== 2) continue; // "map": what a hall's own objects did to a Lord, which gvg.report credits to no team
    const built = events.filter((x) => x[2] === "d" && x[1] === 3 - tm && x[8] === tm).reduce((s, x) => s + x[3] + x[4], 0)
      - events.filter((x) => x[2] === "e" && x[1] === tm && x[8] === tm).reduce((s, x) => s + x[5], 0);
    if (Math.abs(built - (sc.lord_damage_equivalent ?? 0)) > 2) problems.push(`team ${tm}: the events come to ${Math.round(built)}, gvg.report's own score is ${Math.round(sc.lord_damage_equivalent ?? 0)}`);
    scores[tm] = { damage: r1(sc.damage_to_enemy_lord), blind: r1(sc.blind_miss_equivalent_to_enemy_lord), own_effects: sc.own_lord_effect_events ?? 0,
      penalty: r1(sc.own_lord_penalty_equivalent), aggressiveness: r1(sc.lord_damage_equivalent) };
  }
  const health = { 1: [], 2: [] };
  for (const h of g.health_samples?.samples || []) {
    const L = (health[h.guild_lord_team_id] ??= []), row = [Math.round((h.match_time_ms ?? 0) / 100), Math.round(h.current_hp ?? 0), Math.round(h.max_hp ?? 0)];
    const last = L[L.length - 1];
    if (!last || last[1] !== row[1] || last[2] !== row[2]) L.push(row);
  }
  const c = g.constants || {};
  return {
    scores, events, health,
    lords: Object.fromEntries((g.guild_lords || []).map((l) => [l.team_id, { a: A(l.agent_key, { n: "Guild Lord", team: l.team_id, npc: "guild_lord" }), max_hp: l.max_hp ?? null,
      damage: r1(l.damage_taken), life_steal: r1(l.life_steal_health_loss), healing: r1(l.healing_received), hits_under_entourage: l.entourage_damage_events ?? 0 }])),
    deaths: (g.defender_deaths?.events || []).map((d) => [t(d), d.guild_lord_team_id, d.defender_kind || null]),
    entourage: (g.entourage_intervals || []).map((i) => [i.team_id, i.start_ts != null ? T(i.start_ts) : Math.round((i.match_time_ms ?? 0) / 100), Math.round((i.duration_ms ?? 0) / 100)]),
    worth: { blind_miss: c.blind_miss_activity_equivalent ?? null, effect: c.lord_effect_base_equivalent ?? null, effect_under_entourage: c.lord_effect_entourage_equivalent ?? null,
      amulet_start: c.amulet_start_limit ?? null, amulet_max: c.amulet_max_limit ?? null, amulet_ramp_ms: c.amulet_full_ramp_ms ?? null },
    check: problems.length ? problems.join("; ") : null,
  };
}

function playersOf(players, A) {
  const skills = {}, targets = [], received = [], degen = {}, degen_sources = {}, degen_coverage = {};
  const any = (...v) => v.some((x) => x && Math.abs(x) >= 0.05);
  for (const p of players) {
    const a = A(p.agent_key, { n: p.label, team: p.team_id }), sa = p.skill_analytics || {};
    const rows = [];
    for (const s of sa.skills || []) {
      const f = [s.blocked_attacks_estimate, s.knockdowns_prevented_estimate, s.healing_estimate, s.overhealing_estimate, s.divine_favor_healing_estimate,
        s.divine_favor_overhealing_estimate, s.damage_prevented_estimate, s.degeneration_effective_damage_estimate, s.regeneration_effective_healing_estimate];
      if (any(...f)) rows.push([s.row_key ?? null, s.skill_id ?? null, s.condition_name || null, s.source_skill_id ?? null, s.uses ?? 0, ...f.map(r1)]);
      for (const [code, list] of [["c", s.cast_targets], ["h", s.healing_targets], ["d", s.damage_targets]]) {
        for (const x of list || []) {
          const heal = any(x.healing_estimate, x.divine_favor_healing_estimate, x.damage_prevented_estimate), dg = any(x.degeneration_effective_damage_estimate);
          if (code === "d" ? !dg : !heal) continue;
          targets.push([a, s.skill_id ?? null, code, A(x.target_agent_key, { n: x.target_label, team: x.target_team_id, npc: x.target_static_npc_kind }), x.targeted_casts ?? 0,
            r1(x.damage_estimate), r1(x.healing_estimate), r1(x.overhealing_estimate), r1(x.divine_favor_healing_estimate), r1(x.damage_prevented_estimate),
            r1(x.degeneration_effective_damage_estimate), r1(x.regeneration_effective_healing_estimate)]);
        }
      }
    }
    if (rows.length) skills[a] = rows;
    for (const x of sa.received?.skill_rows || []) {
      const ally = x.source_team_id === p.team_id;
      const keep = ally ? any(x.healing_estimate, x.divine_favor_healing_estimate, x.damage_prevented_estimate, x.blocked_attacks_estimate, x.regeneration_effective_healing_estimate)
        : any(x.degeneration_effective_damage_estimate);
      if (!keep) continue;
      received.push([a, A(x.source_agent_key, { n: x.source_label, team: x.source_team_id }), x.skill_id ?? null, x.condition_name || null, x.source_skill_id ?? null, x.targeted_casts ?? 0,
        r1(x.healing_estimate), r1(x.overhealing_estimate), r1(x.divine_favor_healing_estimate), r1(x.damage_prevented_estimate), r1(x.blocked_attacks_estimate),
        r1(x.degeneration_effective_damage_estimate), r1(x.regeneration_effective_healing_estimate)]);
    }
    degen[a] = [p.regen_degen_done_degeneration_effective_damage_estimate, p.regen_degen_done_degeneration_gross_estimate, p.regen_degen_taken_degeneration_effective_damage_estimate,
      p.regen_degen_taken_degeneration_gross_estimate, p.regen_degen_taken_regeneration_effective_healing_estimate, p.regen_degen_done_regeneration_effective_healing_estimate,
      p.regen_degen_taken_regen_degen_net_health_delta_estimate].map(r1);
    const cd = sa.condition_damage_sources || {};
    if (cd.rows?.length) degen_sources[a] = cd.rows.map((x) => [x.skill_id ?? null, x.condition_names || [], r1(x.degeneration_effective_damage_estimate), r1(x.degeneration_gross_estimate), x.target_player_count ?? null]);
    if (cd.coverage?.source_skill_attribution_share != null) degen_coverage[a] = Math.round(cd.coverage.source_skill_attribution_share * 1000) / 1000;
  }
  return { skills, targets, received, degen, degen_sources, degen_coverage };
}

function recapOf(d, kind, A, T) {
  const tt = d.totals || {}, src = (s) => A(s.source_agent_key, { n: s.source_label, team: s.source_team_id });
  const pick = (o, keys) => Object.fromEntries(keys.filter((k) => o[k]).map((k) => [k, typeof o[k] === "number" ? r1(o[k]) : o[k]]));
  const cu = d.target_condition_uptime || {};
  const out = {
    t: T(d.ts_unix_ms), kind, who: A(d.target?.agent_key, { n: d.target?.label, team: d.target?.team_id }), survived: kind === "save" ? !!d.survived : false,
    hp: [r1(d.starting_health?.hp_estimate), r1(d.ending_health?.hp_estimate), d.target_max_hp_context ?? d.starting_health?.max_hp ?? null],
    totals: pick(tt, ["damage_taken_estimate", "healing_received_estimate", "damage_prevented_estimate", "damage_taken_degen_estimate", "damage_taken_condition_degen_estimate",
      "damage_taken_skill_degen_estimate", "regen_degen_healing_estimate", "deep_wound_damage_estimate", "blocks", "knockdowns", "interrupts_received", "prevention_events",
      "active_defensive_effects", "active_regen_degen_effects", "self_loss_estimate"]),
    dmg: (d.damage_sources || []).map((s) => [src(s), s.skill_id ?? null, s.condition_name || null, r1(s.amount_estimate), s.events ?? 0]),
    heal: (d.healing_sources || []).map((s) => [src(s), s.skill_id ?? null, s.attribution || null, r1(s.amount_estimate), s.events ?? 0]),
    prev: (d.prevention_sources || []).map((s) => [src(s), s.skill_id ?? null, s.kind || null, s.blocked_attacks ?? 0, r1(s.amount_estimate), s.events ?? 0]),
    prots: (d.active_defensive_effects || []).map((e) => [A(e.caster_agent_key, { n: e.caster_label, team: e.caster_team_id }), e.skill_id ?? null, T(e.started_at_ts), T(e.ended_at_ts),
      e.active_at_death ? 1 : 0, e.blocks_attacks ? 1 : 0, e.prevents_knockdown ? 1 : 0, e.protection_proc ? 1 : 0]),
    pips: (d.active_regen_degen_effects || []).map((e) => [String(e.family || "?")[0], e.condition_name || null, e.skill_id ?? null,
      A(e.caster_agent_key, { n: e.caster_label, team: e.caster_team_id }), T(e.started_at_ts), T(e.ended_at_ts), e.active_at_death ? 1 : 0, e.pips_estimate ?? null]),
    kd: (d.control?.knockdowns || []).map((k) => [T(k.ts_unix_ms), k.duration_seconds ?? null]),
    intr: (d.control?.interrupts || []).map((k) => [T(k.ts_unix_ms), A(k.interrupter_agent_key, { n: k.interrupter_label, team: k.interrupter_team_id }), k.interrupt_skill_id ?? null, k.interrupted_skill_id ?? null]),
    cond: [cu.duration_ms ?? 0, Math.round((cu.uptime_share ?? 0) * 1000) / 1000, cu.condition_applications ?? 0, (cu.active_at_death_conditions || []).map((c) => (typeof c === "string" ? c : c?.condition_name || c?.name || null))],
    dw: (d.deep_wound_intervals || []).map((w) => [T(w.started_at_ts), T(w.ended_at_ts), w.skill_id ?? null, r1(w.amount_estimate)]),
  };
  if (kind === "save" && d.candidate_pressure_split) out.split = Object.fromEntries(Object.entries(d.candidate_pressure_split).map(([k, v]) => [k, r1(v)]));
  return out;
}

// gvg.report's energy model: for each player the least and most energy he can have. One value every STEP tenths.
const STEP = 20;
function energyOf(es, A, T) {
  if (!es?.players?.length) return null;
  const at = (ms) => T((es.start_ts ?? 0) + ms);
  let first = Infinity, last = -Infinity;
  for (const p of es.players) for (const i of p.intervals || []) { const t = at(i.from_ms); if (t < first) first = t; if (t > last) last = t; }
  if (!isFinite(first)) return null;
  const start = Math.ceil(first / STEP) * STEP, n = Math.max(0, Math.floor((last - start) / STEP) + 1), players = {};
  for (const p of es.players) {
    const lo = new Array(n).fill(null), hi = new Array(n).fill(null), cap = [];
    const iv = [...(p.intervals || [])].sort((x, y) => x.from_ms - y.from_ms);
    let j = 0, cur = null;
    for (let k = 0; k < n; k++) {
      const t = start + k * STEP;
      while (j < iv.length && at(iv[j].from_ms) <= t) cur = iv[j++];
      if (!cur) continue;
      lo[k] = cur.current_min == null ? null : Math.round(cur.current_min); hi[k] = cur.current_max == null ? null : Math.round(cur.current_max);
      const m = cur.maximum_max == null ? null : Math.round(cur.maximum_max);
      if (m != null && (!cap.length || cap[cap.length - 1][1] !== m)) cap.push([t, m]);
    }
    players[A(p.agent_key, { n: p.label, team: p.team_id })] = { lo, hi, cap };
  }
  return { step: STEP, start, model: es.model_version ?? null, players };
}
