// Trim a gvg.report "replay" payload to what match analysis needs (format gvginfo.replay.v1).
// Pure function: no network. Times are in tenths of a second of match time (0 = match start, negative = prep).
//
// Output:
//   meta     id, map, date, clock, result, teams, flux
//   agents   [{k, n, slot, team, p, s, player, bar}]   index in this list = agent number used everywhere below
//   tracks   {agent: {t, x, y, hp, st, sk}}           ~1 sample a second: position, HP %, state code, current skill
//            st: i idle, m moving, a attacking, c casting, k knocked down, d dead, ? unknown
//   ev       [[t, code, a, b, skill, n]]               a = actor, b = target (agent numbers or null)
//            cs cast start, ca activated, cf finished, cx stopped, ir interrupted, sa skill landed on b,
//            at attack start, af attack finished, as attack stopped, dm damage (n = amount), hl heal (n = amount),
//            ea/er effect applied/removed (b = effect id), co/cr condition applied/removed (b = condition name),
//            dh damage skill hint (b = target), dt death, mo morale (n = net max HP %)
//   objectives  flag pickups/drops/captures, carrier inferences, shrine events, match results (times converted)
//   deaths   death recaps (who dealt the damage in the 5 s before each death)
//   skills   {skill id: name} for every skill seen

// Bump when the trimmed format changes: stored matches with an older version are fetched and trimmed again.
export const TRIM_VERSION = 2;
const STATE = { idle: "i", moving: "m", attacking: "a", casting: "c", knocked_down: "k" };
const CODES = {
  "skill.started": "cs", "skill.activated": "ca", "skill.finished": "cf", "skill.stopped": "cx",
  "action.interrupted": "ir", "skill.attributed": "sa", "skill.recipient_bound": "sa",
  "attack.started": "at", "attack.finished": "af", "attack.stopped": "as",
  "damage.applied": "dm", "heal.applied": "hl", "effect.applied": "ea", "effect.removed": "er",
  "condition.applied": "co", "condition.removed": "cr", "damage.skill_hint": "dh", "death": "dt",
  "morale.death_penalty_changed": "mo", "morale.effective_max_hp_changed": "mo",
};
const r1 = (x) => (x == null ? null : Math.round(x * 10) / 10);

export function trimReplay(payload, summaryPayload = null) {
  const sum = summaryPayload?.summary || null;
  const ov = payload.overview || {}, rep = payload.report || {};
  const sess = ov.session || {}, clock = sess.observed_match_clock || {};
  // started_at_ts is the start of the recording; the match clock (as shown in game) starts after the prep time
  const t0 = (sess.started_at_ts || rep.sessions?.[0]?.started_at_ts || 0) + ((clock.instance_start_ms ?? 0) - (clock.match_start_ms ?? 0));
  const T = (ts) => (ts == null ? null : Math.round((ts - t0) / 100));

  // agents: players from the overview first (party order), then anything else that appears in events
  const agents = [], idx = new Map();
  const add = (k, info) => { if (!k || idx.has(k)) return idx.get(k); idx.set(k, agents.length); agents.push({ k, ...info }); return agents.length - 1; };
  for (const p of [...(ov.players || [])].sort((a, b) => (a.display_order || 99) - (b.display_order || 99))) {
    add(p.agent_key, {
      n: String(p.label || "").replace(/\s*\(\d+\)\s*$/, ""), slot: +(String(p.label).match(/\((\d+)\)\s*$/) || [])[1] || null,
      team: p.team_id, p: p.primary_profession_name, s: p.secondary_profession_name, player: !!p.is_player,
      bar: (p.skillbar || []).map((b) => b.skill_id ?? null), hp: p.base_max_hp ?? null,
    });
  }
  const labels = new Map();
  for (const a of rep.agents || []) labels.set(a.agent_key, a);
  const A = (k) => {
    if (!k) return null;
    if (!idx.has(k)) { const a = labels.get(k) || {}; add(k, { n: a.label || k, team: a.team_id ?? null, player: !!a.is_player }); }
    return idx.get(k);
  };

  // weapon sets (from the summary): item ids -> set label per player, plus which sets cast faster (HCT) or lengthen enchantments
  const sets = {}, setIdx = new Map();
  for (const p of sum?.players || []) {
    const a = A(p.agent_key); if (a == null) continue;
    const hct = new Set((p.hct_cast_modifier_weapon_sets || []).map((w) => w.weapon_set_label));
    const ench = new Set((p.enchantment_duration_modifier_weapon_sets || []).map((w) => w.weapon_set_label));
    sets[a] = [];
    for (const w of p.weapon_set_max_hp || []) {
      const g = w.weapon_signature || {}, key = `${a}|${g.weapon_item_id}|${g.offhand_item_id}`;
      if (setIdx.has(key)) continue;
      setIdx.set(key, sets[a].length);
      sets[a].push({ label: w.weapon_set_label, hp: w.max_hp ?? null, hct: hct.has(w.weapon_set_label), ench: ench.has(w.weapon_set_label) });
    }
  }
  const skills = {};
  const tracks = {};
  const ev = [];
  for (const e of rep.events || []) {
    if (e.skill_id && e.skill_name) skills[e.skill_id] = e.skill_name.replace(/_/g, " ");
    const t = T(e.ts_unix_ms);
    if (e.type === "agent.snapshot") {
      const a = A(e.agent_key);
      const tr = (tracks[a] ??= { t: [], x: [], y: [], hp: [], st: [], sk: [], w: [] });
      tr.t.push(t); tr.x.push(Math.round(e.position?.x ?? 0)); tr.y.push(Math.round(e.position?.y ?? 0));
      tr.hp.push(Math.round((e.hp_fraction ?? 0) * 100));
      tr.st.push(e.is_alive === false ? "d" : STATE[e.model_state_family] || "?");
      tr.sk.push(e.current_skill_id || 0);
      // weapon set index into sets[agent]; -1 = not a known set (flag carried, bundle, or unarmed)
      tr.w.push(setIdx.get(`${a}|${e.weapon_item_id}|${e.offhand_item_id}`) ?? -1);
      continue;
    }
    const code = CODES[e.type];
    if (!code) continue; // regen changes and cast-time/activation duplicates are dropped
    const actor = A(e.agent_key || e.source_agent_key);
    let b = A(e.target_agent_key), n = null;
    if (code === "dm" || code === "hl") n = r1(e.amount_estimate);
    if (code === "ea" || code === "er") b = e.effect_id ?? null;
    if (code === "co" || code === "cr") b = e.condition_name || e.effect_name || e.effect_id || null;
    if (code === "mo") n = e.net_max_hp_adjustment_percent ?? null;
    if ((code === "co" || code === "cr") && b == null) continue; // unnamed condition bits duplicate the named rows
    const row = [t, code, actor, b, e.skill_id || null, n], last = ev[ev.length - 1];
    if (last && (code === "co" || code === "cr" || code === "sa") && last.join() === row.join()) continue;
    ev.push(row);
  }

  const ob = rep.objectives || {};
  const conv = (list) => (list || []).map((o) => {
    const out = { t: T(o.ts_unix_ms) };
    for (const [k, v] of Object.entries(o)) {
      if (/^(ts_unix_ms|session_id|interpretation_note|source_detail|session_elapsed_ms|game_time_ms)$/.test(k)) continue;
      if (/agent_key$/.test(k)) out[k.replace(/_key$/, "")] = A(v);
      else if (!/agent_id$/.test(k)) out[k] = v;
    }
    return out;
  });
  const objectives = {};
  for (const k of ["flag_pickups", "flag_drops", "flagstand_captures", "carrier_inferences", "health_shrine_events", "match_results"]) objectives[k] = conv(ob[k]);

  const deaths = (ov.death_recaps?.deaths || []).map((d) => ({
    t: T(d.ts_unix_ms), who: A(d.target?.agent_key),
    from: (d.damage_sources || []).map((s) => ({ a: A(s.source_agent_key), dmg: r1(s.amount_estimate), hits: s.events })),
  }));

  const extra = sum ? summaryParts(sum, A, T, idx, agents) : null;

  return {
    format: "gvginfo.replay.v1",
    meta: {
      id: payload.id, map: sess.map_name, map_id: sess.map_id, started: sess.started_at_ts,
      match_length_s: Math.round((clock.live_end_ms - clock.live_start_ms) / 1000),
      prep_s: Math.round((clock.prep_offset_ms || 0) / 1000), joined_mid_match: !!clock.joined_mid_match,
      occasion: sess.observer_match?.occasion || null, flux: rep.sessions?.[0]?.flux || null,
      result: ov.result || null,
      teams: (ov.teams || []).map((t) => ({ id: t.team_id, tag: t.guild_tag, name: t.guild_name, side: t.side, rating: t.rating,
        deaths: t.deaths, captures: t.flagstand_captures, dmg: Math.round(t.damage_done_estimate || 0), heal: Math.round(t.healing_done_estimate || 0) })),
    },
    agents, tracks, ev, objectives, deaths, skills, sets, ...(extra || {}),
  };
}

// Parts only the summary payload has. Rows are arrays to keep files small; the comment on each says the order.
function summaryParts(sum, A, T, idx, agents) {
  // NPC names (Guild Lord, Bodyguard, Knight, Archer, ...) from any record that labels a target
  const seen = new Set();
  const walk = (v, depth) => {
    if (!v || typeof v !== "object" || depth > 7) return;
    if (Array.isArray(v)) { for (const x of v) walk(x, depth + 1); return; }
    if (v.target_agent_key && v.target_label && !seen.has(v.target_agent_key)) {
      seen.add(v.target_agent_key);
      const a = A(v.target_agent_key), ag = agents[a];
      if (ag && !ag.player && (ag.n === ag.k || !ag.n)) {
        ag.n = v.target_label; ag.team = v.target_team_id ?? ag.team;
        if (v.target_static_npc_kind) ag.npc = v.target_static_npc_kind;
      }
    }
    for (const x of Object.values(v)) if (x && typeof x === "object") walk(x, depth + 1);
  };
  walk(sum.skill_analytics?.attributed_outcomes, 0); walk(sum.objectives?.guild_lord_damage, 0); walk(sum.players, 0);
  for (const g of sum.objectives?.guild_lord_damage?.guild_lords || []) { const a = A(g.agent_key); Object.assign(agents[a], { n: "Guild Lord", team: g.team_id, npc: "guild_lord" }); }

  const sa = sum.skill_analytics || {};
  const short = (x) => String(x || "").replace(/_/g, " ");
  return {
    // [t, interrupter, interrupt skill, interrupted, interrupted skill, that skill's target, cast time ms]
    interrupts: (sa.interrupts?.events || []).map((e) => [T(e.ts_unix_ms), A(e.interrupter_agent_key), e.interrupt_skill_id ?? null,
      A(e.interrupted_agent_key), e.interrupted_skill_id ?? null, A(e.interrupted_skill_target_agent_key), e.cast_duration_ms ?? null]),
    // [t, source, target, skill]
    knockdowns: (sa.knockdowns?.events || []).map((e) => [T(e.ts_unix_ms), A(e.source_agent_key), A(e.target_agent_key), e.knockdown_skill_id ?? null]),
    // [start, end, family (e enchantment, h hex, c condition), skill, caster, target, how it ended, condition name]
    effects: (sum.effects?.uptime_intervals || []).map((e) => [T(e.started_at_ts), T(e.ended_at_ts), (e.family || "?")[0], e.skill_id ?? null,
      A(e.caster_agent_key), A(e.target_agent_key), e.close_reason || null,
      e.condition_name || (e.family === "condition" && e.effect_name !== "condition" ? e.effect_name : null) || null]),
    // flag and objective timeline as gvg.report reads it: [t, type, actor]
    flags: (sum.objectives?.timeline || []).map((e) => [T(e.ts_unix_ms), e.type, A(e.inferred_actor_agent_key)]),
    lords: (sum.objectives?.guild_lord_damage?.guild_lords || []).map((g) => ({ a: A(g.agent_key), team: g.team_id, max_hp: g.max_hp,
      taken: Math.round(g.damage_taken || 0), hits: g.damage_events, defenders_end: g.defender_state_end })),
    // spike saves: a player took a spike (400+ in 3 s) and survived: [t, target, damage in window, survived]
    saves: (sum.spike_saves?.saves || []).map((e) => [T(e.ts_unix_ms), A(e.target?.agent_key), Math.round(e.totals?.damage_estimate ?? e.candidate_raw_damage_estimate ?? 0), !!e.survived]),
    // per player totals credited by skill: {agent: {skill id: [knockdowns, interrupts, enchantment removals, hex removals, condition removals, conditions applied]}}
    outcomes: Object.fromEntries((sa.attributed_outcomes?.by_player || []).map((b) => [A(b.agent_key), Object.fromEntries((b.skills || []).map((x) =>
      [x.skill_id, [x.knockdowns_dealt, x.interrupts_landed, x.enchantment_removals, x.hex_removals, x.condition_removals, x.condition_applications]]))])),
    quality: sum.data_quality || null,
  };
}
