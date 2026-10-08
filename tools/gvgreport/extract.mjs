// Turn one gvg.report match (list entry + summary payload) into a compact record.
// Pure function: no network, works in Node and in a browser.

const round = (x, d = 0) => (x == null || !isFinite(x) ? 0 : Math.round(x * 10 ** d) / 10 ** d);
export const playerName = (label) => String(label || "").replace(/\s*\(\d+\)\s*$/, "").trim();

export function occasionOf(entry) {
  const o = entry.tournament_occasion || {};
  if (o.occasion_kind === "automated" && o.occasion_slot) return `AT-${o.occasion_slot}`;
  if (o.occasion_kind) return String(o.occasion_kind).toUpperCase().replace(/^MONTHLY.*/, "MAT");
  return entry.observer_type_name || "Other";
}

// Attribute ranks the observer pinned down exactly (effective ranks, may include rune/headgear bonus).
function attributesOf(p) {
  const out = {};
  for (const a of p.attribute_build_v2?.known_attributes || []) {
    const r = a.exact_rank ?? (a.allowed_effective_ranks?.length === 1 ? a.allowed_effective_ranks[0] : null);
    if (r != null) out[a.attribute_name] = r;
  }
  return out;
}

function weaponSetsOf(p) {
  const sets = {};
  for (const s of p.exact_equipment_weapon_set_max_hp || p.weapon_set_max_hp || []) {
    const sig = s.weapon_signature || {};
    const label = [sig.weapon_name, sig.offhand_name].filter(Boolean).join(" + ") || s.weapon_set_label || "Unknown";
    if (!sets[label] || (s.max_hp && !sets[label].hp)) sets[label] = { w: label, hp: s.max_hp || null };
  }
  return Object.values(sets);
}

export function extractMatch(entry, summary) {
  const S = summary;
  const winner = entry.winner_team_id ?? S.result?.winning_team_id ?? null;
  const outcomes = new Map((S.skill_analytics?.attributed_outcomes?.by_player || []).map((b) => [b.agent_key, b]));
  const teams = (S.teams || entry.guilds || []).map((t) => ({
    id: t.team_id, guild: t.guild_name || null, tag: t.guild_tag || null, rating: t.rating ?? null,
    won: winner === t.team_id, deaths: t.deaths ?? null,
  }));
  const players = [];
  for (const p of S.players || []) {
    if (!p.is_player) continue;
    const bar = Array(8).fill(0);
    for (const s of p.skillbar || []) if (s.slot >= 1 && s.slot <= 8 && s.skill_id) bar[s.slot - 1] = s.skill_id;
    const out = outcomes.get(p.agent_key);
    const perSkill = {};
    for (const r of p.skill_analytics?.skills || []) {
      if (!r.skill_id) continue;
      const row = perSkill[r.skill_id] ||= [0, 0, 0, 0, 0, 0];
      row[0] += r.uses || 0;
      row[1] += r.damage_estimate || 0;
      row[2] += (r.healing_estimate || 0) + (r.divine_favor_healing_estimate || 0);
      row[3] += r.damage_prevented_estimate || 0;
    }
    for (const r of out?.skills || []) {
      if (!r.skill_id) continue;
      const row = perSkill[r.skill_id] ||= [0, 0, 0, 0, 0, 0];
      row[4] += r.knockdowns_dealt || 0;
      row[5] += r.interrupts_landed || 0;
    }
    for (const k of Object.keys(perSkill)) perSkill[k] = perSkill[k].map((v) => round(v));
    const tot = p.skill_analytics?.totals || {};
    players.push({
      n: playerName(p.label), team: p.team_id,
      p: p.primary_profession_name || "None", s: p.secondary_profession_name || "None",
      bar, full: p.skillbar_complete === true,
      attrs: attributesOf(p),
      dmg: round(p.damage_done_estimate), heal: round(p.healing_done_estimate), taken: round(p.damage_taken_estimate),
      prev: round(tot.damage_prevented_estimate), deaths: p.deaths || 0,
      kd: out?.totals?.knockdowns_dealt || 0, intr: out?.totals?.interrupts_landed || 0,
      cond: out?.totals?.condition_removals || 0, hexr: out?.totals?.hex_removals || 0,
      hp: p.base_max_hp || null, weapons: weaponSetsOf(p),
      sk: perSkill,
    });
  }
  return {
    id: entry.id, date: entry.date, at: entry.played_at_unix_ms || null,
    map: entry.map_name || S.session?.map_name || null, dur: Math.round((entry.duration_ms || S.session?.duration_ms || 0) / 1000),
    occ: occasionOf(entry), result: entry.result_type || S.result?.result_type || null, winner,
    flux: Object.entries(S.session?.flux || {}).filter(([k, v]) => /_active$/.test(k) && v === true).map(([k]) => k.replace(/_active$/, "")),
    teams, players,
  };
}
