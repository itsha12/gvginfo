// Build the portal's summary files from data/matches/*.json:
//   data/recent.json       latest matches with both lineups
//   data/builds.json       bars grouped into families and variations, with template codes
//   data/players.json      per-player totals and per-minute rates
//   data/skill_stats.json  per-skill usage and per-use averages from real matches
//   data/meta.json         per-month elite usage, team compositions, family usage
//   data/guilds.json       per guild: record, maps, usual lineups per map (party order), players, recent results
// Skill order in every bar: elite first, then the family's skills from most to least common, so variations line up.
import fs from "node:fs";
import path from "node:path";
import { encode, PROF_ATTRS } from "../../assets/js/template.js";

const readJson = (f, fb) => { try { return JSON.parse(fs.readFileSync(f, "utf8")); } catch { return fb; } };
const writeJson = (f, d) => fs.writeFileSync(f, JSON.stringify(d) + "\n");
const ABBR = { Warrior: "W", Ranger: "R", Monk: "Mo", Necromancer: "N", Mesmer: "Me", Elementalist: "E", Assassin: "A", Ritualist: "Rt", Paragon: "P", Dervish: "D", None: "X" };
const RUNE = { 1: "Minor", 2: "Major", 3: "Superior" };
// Runes implied by bonus ranks above the base 12 (+1 minor, +2 major, +3 superior, +4 superior and headgear).
export const runesFromBonus = (bonus = {}) => Object.entries(bonus).filter(([, b]) => b > 0)
  .map(([a, b]) => (b >= 4 ? `Superior ${a} rune + ${a} headgear` : `${RUNE[b]} ${a} rune`));
const FAMILY_MIN_SHARED = 6; // a bar joins a family when it shares at least 6 of 8 skills with the family's main bar

export function aggregate(root) {
  const D = (f) => path.join(root, "data", f);
  const skills = readJson(D("skills.json"), { skills: [] }).skills;
  const byId = new Map(skills.map((s) => [s.id, s]));
  const map = readJson(D("template_id_map.json"), { pvp_to_template: {} }).pvp_to_template;
  const files = fs.readdirSync(D("matches")).filter((f) => /^\d{4}-\d{2}\.json$/.test(f)).sort();
  const matches = files.flatMap((f) => readJson(D(`matches/${f}`), [])).sort((a, b) => (b.at || 0) - (a.at || 0));
  const isElite = (id) => byId.get(id)?.elite === true;
  // Standard bar order: elite, then by how common the skill is in its build family, then by attribute and name.
  function orderBar(bar, primary, secondary, rank = new Map()) {
    const attrIdx = (s) => {
      const i = (PROF_ATTRS[primary] || []).indexOf(s?.attr); if (i >= 0) return i;
      const j = (PROF_ATTRS[secondary] || []).indexOf(s?.attr); if (j >= 0) return 10 + j;
      return /no attribute/i.test(s?.attr || "") ? 30 : 20;
    };
    const known = [...new Set(bar.filter(Boolean))];
    known.sort((a, b) => {
      const A = byId.get(a), B = byId.get(b);
      return (isElite(b) - isElite(a)) || ((rank.get(b) || 0) - (rank.get(a) || 0)) || (attrIdx(A) - attrIdx(B)) ||
        String(A?.name || a).localeCompare(String(B?.name || b));
    });
    return [...known, ...Array(8).fill(0)].slice(0, 8);
  }

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
    const secondary = mode(rs.map((r) => r.p.s));
    const slotOrder = orderBar(v.set, v.p, secondary, v.rank);
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
      code: encode({ primary: v.p, secondary, attributes, skills: slotOrder }, map), attributes, bonus, runes: runesFromBonus(bonus),
      attrs_observed: attrNames.length > 0,
      players: top(rs.map((r) => r.p.n)), guilds: top(rs.map((r) => r.guild)),
      weapons: top(rs.flatMap((r) => (r.p.weapons || []).map((w) => w.w)), 4),
      hp: hp.length ? hp[Math.floor(hp.length / 2)] : null,
      last: rs.reduce((a, r) => Math.max(a, r.m.at || 0), 0),
      months: Object.fromEntries(top(rs.map((r) => r.m.date?.slice(0, 7)), 24).map(({ k, n }) => [k, n])),
    };
  }
  for (const f of families) {
    f.rank = new Map();
    for (const r of [...f.vars.flatMap((v) => v.rows), ...f.partial]) for (const id of new Set(r.p.bar.filter(Boolean))) f.rank.set(id, (f.rank.get(id) || 0) + 1);
    for (const v of f.vars) v.rank = f.rank;
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
  const famOf = new Map(), famRank = new Map(), famName = new Map(famOut.map((x) => [x.id, x.name]));
  for (const [i, f] of families.entries()) {
    const id = famOut.find((x) => x.core === f.core)?.id || i;
    famRank.set(id, f.rank);
    for (const r of [...f.vars.flatMap((v) => v.rows), ...f.partial]) famOf.set(r.p, id);
  }
  // a player's bar in standard order (family order when the bar belongs to a family)
  const playerBar = (p) => orderBar(p.bar, p.p, p.s, famRank.get(famOf.get(p)));
  const eliteName = (p) => { const e = p.bar.find(isElite); return e ? byId.get(e)?.name?.replace(/ \(PvP\)$/, "") : null; };
  const buildLabel = (p) => famName.get(famOf.get(p)) || `${eliteName(p) || "No elite seen"} ${ABBR[p.p]}/${ABBR[p.s] || "X"}`;
  // party slot order; matches without slots fall back to a typical order (frontline, midline, backline)
  const ROLE = ["Warrior", "Dervish", "Assassin", "Paragon", "Ranger", "Elementalist", "Necromancer", "Mesmer", "Ritualist", "Monk"];
  const slotKey = (p) => p.pos ?? 10 + (ROLE.indexOf(p.p) + 1 || 11);
  const byPos = (a, b) => slotKey(a) - slotKey(b);
  // ---------- recent matches ----------
  writeJson(D("recent.json"), {
    updated: new Date().toISOString(), total: matches.length,
    matches: matches.slice(0, 150).map((m) => ({
      id: m.id, date: m.date, at: m.at, occ: m.occ, map: m.map, dur: m.dur, result: m.result, flux: m.flux,
      teams: m.teams.map((t) => ({
        ...t, players: m.players.filter((p) => p.team === t.id).sort(byPos).map((p) => ({ n: p.n, pos: p.pos ?? null, p: p.p, s: p.s, bar: playerBar(p), full: p.full, attrs: p.attrs, build: buildLabel(p), fam: famOf.get(p) ?? null })),
      })),
    })),
  });


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

  // ---------- guilds ----------
  const guilds = new Map();
  const slug = (t) => `${t.guild || "?"} ${t.tag || ""}`.toLowerCase().replace(/[^\p{L}\p{N}]+/gu, "-").replace(/^-|-$/g, "");
  for (const m of [...matches].reverse()) for (const t of m.teams) {
    const id = slug(t);
    const g = guilds.get(id) || { id, name: t.guild, tag: t.tag, games: 0, wins: 0, flawless: 0, rating: null, last: 0, sec: 0, maps: {}, occ: {}, players: new Map(), lineups: [], recent: [], fams: [] };
    const won = !!t.won, opp = m.teams.find((x) => x !== t) || {};
    g.games++; g.wins += won ? 1 : 0; g.flawless += won && m.result === "flawless_victory" ? 1 : 0; g.sec += m.dur || 0;
    if ((m.at || 0) >= g.last) { g.last = m.at || 0; if (t.rating != null) g.rating = t.rating; }
    const mp = (g.maps[m.map || "Unknown"] ||= { n: 0, wins: 0 }); mp.n++; mp.wins += won ? 1 : 0;
    const oc = (g.occ[m.occ || "Other"] ||= { n: 0, wins: 0 }); oc.n++; oc.wins += won ? 1 : 0;
    const ps = m.players.filter((p) => p.team === t.id).sort(byPos);
    for (const p of ps) {
      const x = g.players.get(p.n) || { n: p.n, games: 0, wins: 0, builds: [], pos: [] };
      x.games++; x.wins += won ? 1 : 0; x.builds.push(buildLabel(p)); if (p.pos) x.pos.push(p.pos);
      g.players.set(p.n, x);
      g.fams.push(buildLabel(p));
    }
    g.lineups.push({ map: m.map || "Unknown", won, players: ps.map((p) => ({ pos: p.pos ?? null, n: p.n, p: p.p, s: p.s, build: buildLabel(p), fam: famOf.get(p) ?? null, bar: playerBar(p), attrs: p.attrs })) });
    g.recent.push({ id: m.id, date: m.date, at: m.at, map: m.map, occ: m.occ, opp: opp.guild || "?", oppTag: opp.tag || "", won, result: m.result, dur: m.dur, rating: t.rating ?? null });
    guilds.set(id, g);
  }
  // usual lineup: for each party slot, the most common build there (with its usual player and bar)
  function usualLineup(lineups) {
    const out = [];
    for (let pos = 1; pos <= 8; pos++) {
      const here = lineups.flatMap((l) => l.players.filter((p) => p.pos === pos));
      if (!here.length) continue;
      const build = mode(here.map((p) => p.build));
      const same = here.filter((p) => p.build === build);
      const p0 = same[0];
      out.push({ pos, build, fam: p0.fam, p: p0.p, s: mode(same.map((p) => p.s)), n: same.length, of: here.length,
        players: top(same.map((p) => p.n), 3), bar: mode(same.map((p) => p.bar.join(","))).split(",").map(Number) });
    }
    return out;
  }
  writeJson(D("guilds.json"), {
    updated: new Date().toISOString(), matches: matches.length,
    guilds: [...guilds.values()].map((g) => {
      const maps = Object.entries(g.maps).sort((a, b) => b[1].n - a[1].n).map(([map, x]) => ({
        map, ...x, lineup: usualLineup(g.lineups.filter((l) => l.map === map)),
      }));
      return {
        id: g.id, name: g.name, tag: g.tag, games: g.games, wins: g.wins, flawless: g.flawless, rating: g.rating, last: g.last,
        avgDur: Math.round(g.sec / Math.max(1, g.games)), occ: g.occ,
        lineup: usualLineup(g.lineups), maps,
        players: [...g.players.values()].map((x) => ({ n: x.n, games: x.games, wins: x.wins, builds: top(x.builds, 3), pos: mode(x.pos) ?? null }))
          .sort((a, b) => b.games - a.games),
        builds: top(g.fams, 12),
        recent: g.recent.reverse().slice(0, 20),
      };
    }).sort((a, b) => b.games - a.games || (b.rating || 0) - (a.rating || 0)),
  });

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
  console.log(`Aggregated ${matches.length} matches: ${famOut.length} build families, ${players.size} players, ${guilds.size} guilds.`);
}

if (import.meta.url === `file://${process.argv[1]}`) aggregate(path.resolve(path.dirname(new URL(import.meta.url).pathname), "../.."));
