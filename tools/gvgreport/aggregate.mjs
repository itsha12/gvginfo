// Build the portal's summary files from data/matches/*.json:
//   data/recent.json       latest matches with both lineups
//   data/builds.json       bars grouped into families and variations, with template codes
//   data/players.json      per-player totals and per-minute rates
//   data/skill_stats.json  per-skill usage and per-use averages from real matches
//   data/meta.json         per-month elite usage, team compositions, family usage
import fs from "node:fs";
import path from "node:path";
import { encode } from "../../assets/js/template.js";

const readJson = (f, fb) => { try { return JSON.parse(fs.readFileSync(f, "utf8")); } catch { return fb; } };
const writeJson = (f, d) => fs.writeFileSync(f, JSON.stringify(d) + "\n");
const ABBR = { Warrior: "W", Ranger: "R", Monk: "Mo", Necromancer: "N", Mesmer: "Me", Elementalist: "E", Assassin: "A", Ritualist: "Rt", Paragon: "P", Dervish: "D", None: "X" };
const FAMILY_MIN_SHARED = 6; // a bar joins a family when it shares at least 6 of 8 skills with the family's main bar

export function aggregate(root) {
  const D = (f) => path.join(root, "data", f);
  const skills = readJson(D("skills.json"), { skills: [] }).skills;
  const byId = new Map(skills.map((s) => [s.id, s]));
  const map = readJson(D("template_id_map.json"), { pvp_to_template: {} }).pvp_to_template;
  const files = fs.readdirSync(D("matches")).filter((f) => /^\d{4}-\d{2}\.json$/.test(f)).sort();
  const matches = files.flatMap((f) => readJson(D(`matches/${f}`), [])).sort((a, b) => (b.at || 0) - (a.at || 0));
  const isElite = (id) => byId.get(id)?.elite === true;

  // ---------- recent matches ----------
  writeJson(D("recent.json"), {
    updated: new Date().toISOString(), total: matches.length,
    matches: matches.slice(0, 150).map((m) => ({
      id: m.id, date: m.date, at: m.at, occ: m.occ, map: m.map, dur: m.dur, result: m.result, flux: m.flux,
      teams: m.teams.map((t) => ({
        ...t, players: m.players.filter((p) => p.team === t.id).map((p) => ({ n: p.n, p: p.p, s: p.s, bar: p.bar, full: p.full, attrs: p.attrs })),
      })),
    })),
  });

  // ---------- builds ----------
  const rows = [];
  for (const m of matches) for (const p of m.players) {
    const known = p.bar.filter(Boolean);
    if (known.length < 6) continue;
    const team = m.teams.find((t) => t.id === p.team) || {};
    rows.push({ m, p, won: !!team.won, guild: team.tag || team.guild, set: [...known].sort((a, b) => a - b), elite: known.find(isElite) || 0 });
  }
  // exact skill sets -> variations (complete bars only)
  const varMap = new Map();
  for (const r of rows.filter((r) => r.p.full && r.set.length === 8)) {
    const key = `${r.p.p}|${r.set.join(",")}`;
    const v = varMap.get(key) || { key, p: r.p.p, set: r.set, elite: r.elite, rows: [] };
    v.rows.push(r); varMap.set(key, v);
  }
  const variations = [...varMap.values()].sort((a, b) => b.rows.length - a.rows.length);
  const families = [];
  const shared = (a, b) => { const s = new Set(a); return b.filter((x) => s.has(x)).length; };
  for (const v of variations) {
    let fam = families.find((f) => f.p === v.p && f.elite === v.elite && shared(f.core, v.set) >= FAMILY_MIN_SHARED);
    if (!fam) { fam = { p: v.p, elite: v.elite, core: v.set, vars: [], partial: [] }; families.push(fam); }
    fam.vars.push(v);
  }
  // incomplete bars count toward the family they match best (for usage and win rates)
  for (const r of rows.filter((r) => !(r.p.full && r.set.length === 8))) {
    let best = null, bestShared = 0;
    for (const f of families) if (f.p === r.p.p && (!r.elite || f.elite === r.elite)) {
      const n = shared(f.core, r.set); if (n > bestShared) { best = f; bestShared = n; }
    }
    if (best && bestShared >= Math.min(FAMILY_MIN_SHARED, r.set.length - 1)) best.partial.push(r);
  }
  const mode = (arr) => { const c = new Map(); for (const x of arr) c.set(x, (c.get(x) || 0) + 1); return [...c.entries()].sort((a, b) => b[1] - a[1])[0]?.[0]; };
  const top = (arr, n = 5) => { const c = new Map(); for (const x of arr) if (x) c.set(x, (c.get(x) || 0) + 1); return [...c.entries()].sort((a, b) => b[1] - a[1]).slice(0, n).map(([k, v]) => ({ k, n: v })); };

  function variationOut(v) {
    const rs = v.rows;
    const slotOrder = mode(rs.map((r) => r.p.bar.join(","))).split(",").map(Number);
    const secondary = mode(rs.map((r) => r.p.s));
    // most common observed rank per attribute; effective ranks above 12 become base 12 + bonus
    const attrNames = [...new Set(rs.flatMap((r) => Object.keys(r.p.attrs || {})))];
    const attributes = {}, bonus = {};
    for (const a of attrNames) {
      const r = mode(rs.map((x) => x.p.attrs?.[a]).filter((x) => x != null));
      if (r == null) continue;
      attributes[a] = Math.min(12, r); if (r > 12) bonus[a] = r - 12;
    }
    const hp = rs.map((r) => r.p.hp).filter(Boolean).sort((a, b) => a - b);
    return {
      bar: slotOrder, s: secondary, n: rs.length, wins: rs.filter((r) => r.won).length,
      code: encode({ primary: v.p, secondary, attributes, skills: slotOrder }, map), attributes, bonus,
      attrs_observed: attrNames.length > 0,
      players: top(rs.map((r) => r.p.n)), guilds: top(rs.map((r) => r.guild)),
      weapons: top(rs.flatMap((r) => (r.p.weapons || []).map((w) => w.w)), 4),
      hp: hp.length ? hp[Math.floor(hp.length / 2)] : null,
      last: rs.reduce((a, r) => Math.max(a, r.m.at || 0), 0),
      months: Object.fromEntries(top(rs.map((r) => r.m.date?.slice(0, 7)), 24).map(({ k, n }) => [k, n])),
    };
  }
  const famOut = families.map((f) => {
    const vars = f.vars.map(variationOut);
    const all = [...f.vars.flatMap((v) => v.rows), ...f.partial];
    const main = vars[0];
    const eliteName = f.elite ? byId.get(f.elite)?.name?.replace(/ \(PvP\)$/, "") : "No elite";
    return {
      id: `${ABBR[f.p]}-${f.elite}-${f.core.slice(0, 4).join(".")}`,
      name: `${eliteName} ${ABBR[f.p]}/${ABBR[main.s] || "X"}`,
      p: f.p, elite: f.elite, core: f.core, n: all.length, wins: all.filter((r) => r.won).length,
      partial: f.partial.length, last: all.reduce((a, r) => Math.max(a, r.m.at || 0), 0),
      months: Object.fromEntries(top(all.map((r) => r.m.date?.slice(0, 7)), 24).map(({ k, n }) => [k, n])),
      players: top(all.map((r) => r.p.n), 8), guilds: top(all.map((r) => r.guild), 8),
      variations: vars,
    };
  }).sort((a, b) => b.n - a.n);
  writeJson(D("builds.json"), { updated: new Date().toISOString(), matches: matches.length, rule: `bars sharing ${FAMILY_MIN_SHARED}+ of 8 skills and the same elite form a family`, families: famOut });
  const famOf = new Map();
  for (const [i, f] of families.entries()) for (const r of [...f.vars.flatMap((v) => v.rows), ...f.partial]) famOf.set(r.p, famOut.find((x) => x.core === f.core)?.id || i);

  // ---------- players ----------
  const players = new Map();
  for (const m of matches) for (const p of m.players) {
    const team = m.teams.find((t) => t.id === p.team) || {};
    const x = players.get(p.n) || { n: p.n, games: 0, wins: 0, sec: 0, kd: 0, intr: 0, dmg: 0, heal: 0, prev: 0, deaths: 0, cond: 0, hexr: 0, profs: [], guilds: [], fams: [], last: 0 };
    x.games++; x.wins += team.won ? 1 : 0; x.sec += m.dur || 0;
    for (const k of ["kd", "intr", "dmg", "heal", "prev", "deaths", "cond", "hexr"]) x[k] += p[k] || 0;
    x.profs.push(`${p.p}/${p.s}`); x.guilds.push(team.tag || team.guild); if (famOf.has(p)) x.fams.push(famOf.get(p));
    x.last = Math.max(x.last, m.at || 0);
    players.set(p.n, x);
  }
  writeJson(D("players.json"), {
    updated: new Date().toISOString(),
    note: "Names are character names; one person may play several characters. Per-minute rates use full match length.",
    players: [...players.values()].map((x) => ({ ...x, profs: top(x.profs, 4), guilds: top(x.guilds, 3), fams: top(x.fams, 5) })).sort((a, b) => b.games - a.games),
  });

  // ---------- skill stats ----------
  const st = {};
  for (const m of matches) for (const p of m.players) {
    for (const id of new Set(p.bar.filter(Boolean))) (st[id] ||= { bars: 0, uses: 0, dmg: 0, heal: 0, prev: 0, kd: 0, intr: 0 }).bars++;
    for (const [id, [uses, dmg, heal, prev, kd, intr]] of Object.entries(p.sk || {})) {
      const s = (st[id] ||= { bars: 0, uses: 0, dmg: 0, heal: 0, prev: 0, kd: 0, intr: 0 });
      s.uses += uses; s.dmg += dmg; s.heal += heal; s.prev += prev; s.kd += kd; s.intr += intr;
    }
  }
  writeJson(D("skill_stats.json"), { updated: new Date().toISOString(), matches: matches.length, players: matches.reduce((a, m) => a + m.players.length, 0), skills: st });

  // ---------- meta by month ----------
  const meta = {};
  for (const m of matches) {
    const mo = m.date?.slice(0, 7) || "unknown";
    const x = (meta[mo] ||= { matches: 0, teams: 0, elites: {}, comps: {}, maps: {}, flux: {} });
    x.matches++; x.maps[m.map] = (x.maps[m.map] || 0) + 1;
    for (const f of m.flux || []) x.flux[f] = (x.flux[f] || 0) + 1;
    for (const t of m.teams) {
      const ps = m.players.filter((p) => p.team === t.id);
      if (!ps.length) continue;
      x.teams++;
      const comp = ps.map((p) => ABBR[p.p]).sort().join(" ");
      const c = (x.comps[comp] ||= { n: 0, wins: 0 }); c.n++; c.wins += t.won ? 1 : 0;
      for (const id of new Set(ps.flatMap((p) => p.bar.filter(isElite)))) {
        const e = (x.elites[id] ||= { n: 0, wins: 0 }); e.n++; e.wins += t.won ? 1 : 0;
      }
    }
  }
  writeJson(D("meta.json"), { updated: new Date().toISOString(), months: meta });
  console.log(`Aggregated ${matches.length} matches: ${famOut.length} build families, ${players.size} players.`);
}

if (import.meta.url === `file://${process.argv[1]}`) aggregate(path.resolve(path.dirname(new URL(import.meta.url).pathname), "../.."));
