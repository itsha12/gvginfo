// Guild Wars 1 skill scraper. Run in a browser tab on https://wiki.guildwars.com (same-origin API).
// Produces window.__gw.out: compact text of every player-equippable skill, PvP-legal only
// (PvE-only skills dropped; skills with a PvP split use the "(PvP)" version).
(async () => {
const G = (window.__gw = window.__gw || {});
const api = async (q) => (await fetch('/api.php?' + new URLSearchParams({ ...q, format: 'json', formatversion: '2' }))).json();

// ---------- 1. Skill list (IDs) ----------
const L = await api({ action: 'query', prop: 'revisions', rvprop: 'content', rvslots: 'main', titles: 'Skill_template_format/Skill_list' });
const txt = L.query.pages[0].revisions[0].slots.main.content;
G.list = [...txt.matchAll(/^\|\s*(\d+)\s*\|\|\s*\[\[([^\]|]+)(?:\|[^\]]*)?\]\]/gm)].map(m => ({ id: +m[1], title: m[2].trim() }));

// ---------- 2. Fetch every page (resolving redirects) ----------
G.pages = {}; G.redirects = {};
const titles = [...new Set(G.list.map(r => r.title))];
for (let i = 0; i < titles.length; i += 50) {
  const d = await api({ action: 'query', prop: 'revisions', rvprop: 'content', rvslots: 'main', redirects: '1', titles: titles.slice(i, i + 50).join('|') });
  (d.query.redirects || []).forEach(r => G.redirects[r.from] = r.to);
  (d.query.normalized || []).forEach(r => G.redirects[r.from] = r.to);
  d.query.pages.forEach(p => { G.pages[p.title] = p.missing ? null : p.revisions[0].slots.main.content; });
}
const res = t => { let x = t; for (let i = 0; i < 3 && G.redirects[x]; i++) x = G.redirects[x]; return x; };

// ---------- 3. Wikitext helpers ----------
function tpl(w, nameRe) { // brace-matched templates
  const re = new RegExp('\\{\\{\\s*(' + nameRe + ')\\s*(?=[|\\n}])', 'ig'); let m; const outs = [];
  while ((m = re.exec(w))) {
    let i = m.index + 2, d = 1;
    while (i < w.length && d > 0) { if (w.startsWith('{{', i)) { d++; i += 2; } else if (w.startsWith('}}', i)) { d--; i += 2; } else i++; }
    outs.push({ name: m[1].trim().toLowerCase(), body: w.slice(m.index + m[0].length, i - 2), start: m.index, end: i });
  }
  return outs;
}
function params(body) {
  const ps = []; let d = 0, cur = '';
  for (let i = 0; i < body.length; i++) {
    const c2 = body.substr(i, 2);
    if (c2 === '{{' || c2 === '[[') { d++; cur += c2; i++; continue; }
    if (c2 === '}}' || c2 === ']]') { d--; cur += c2; i++; continue; }
    if (body[i] === '|' && d === 0) { ps.push(cur); cur = ''; continue; }
    cur += body[i];
  }
  ps.push(cur);
  const named = {}, pos = [];
  ps.slice(1).forEach(p => { const m = p.match(/^\s*([\w \-]+?)\s*=([\s\S]*)$/); if (m) named[m[1].toLowerCase()] = m[2].trim(); else pos.push(p.trim()); });
  return { named, pos };
}
const frac = { '1/4': '¼', '1/2': '½', '3/4': '¾', '1/3': '⅓', '2/3': '⅔' };
function clean(s) {
  if (!s) return '';
  let x = s.replace(/<!--[\s\S]*?-->/g, '').replace(/<br\s*\/?>/gi, ' ').replace(/<ref[\s\S]*?<\/ref>/gi, '').replace(/<\/?[a-z][^>]*>/gi, '');
  for (let k = 0; k < 6; k++) {
    x = x.replace(/\{\{([^{}]*)\}\}/g, (_, inner) => {
      const a = inner.split('|').map(s => s.trim()); const n = a[0].toLowerCase();
      if (n === 'gr' || n === 'gr2') { const sign = (a[3] === '+' || a[3] === '-') ? a[3] : ''; const pct = a[4] === '%' ? '%' : ''; return sign + a[1] + '..' + a[2] + pct; }
      if (frac[n]) return frac[n];
      if (n === 'gray' || n === 'grey') return '(' + a.slice(1).join('|') + ')';
      if (n === 'sic' || n === 'verify' || n === 'citation needed') return '';
      if (/^(skill icon|skill link|duplicate skill icon)$/.test(n)) return a[1];
      if (/^(w|r|mo|n|me|e|a|rt|p|d|any|x|monster)$/.test(n)) return '';
      return a.slice(1).join(' ');
    });
  }
  return x.replace(/\[\[([^\]|]*)\|([^\]]*)\]\]/g, '$2').replace(/\[\[([^\]]*)\]\]/g, '$1').replace(/'''?/g, '').replace(/\s+/g, ' ').trim();
}
const rnd = v => Math.sign(v) * Math.round(Math.abs(v));
function prog(w) {
  const P = tpl(w, 'skill progression(?: factored| max10(?: old)?| max12)?'); const out = [];
  for (const p of P) {
    const { named } = params('x|' + p.body.replace(/^[^|\n]*/, ''));
    const top = p.name.includes('max10') ? 10 : p.name.includes('max12') ? 12 : 15;
    for (const k of ['1', '2', '3', '4', '5', 'f']) {
      const nm = named['var' + k + ' name']; if (!nm) continue;
      const a0 = parseFloat(named['var' + k + ' at0']), aT = parseFloat(named['var' + k + ' at' + top]);
      if (isNaN(a0) || isNaN(aT)) continue;
      const f = k === 'f' ? parseFloat(named['varf factor'] || '1') : 1;
      const max = top === 15 ? 21 : top; const vals = [];
      for (let r = 0; r <= max; r++) vals.push(rnd(a0 + r * (aT - a0) / top) * f);
      out.push({ n: clean(nm), v: vals });
    }
    if (named['varx name']) { const vals = []; for (let r = 0; r <= 21; r++) if (named['varx' + r] !== undefined) vals.push(clean(named['varx' + r])); out.push({ n: clean(named['varx name']), v: vals }); }
  }
  return out;
}
// bug / anomaly notes anywhere on the page (outside the infobox)
function notes(w) {
  return tpl(w, 'bug|anomaly').map(t => (t.name === 'bug' ? 'BUG: ' : 'ANOMALY: ') + clean(t.body.replace(/^\s*\|/, ''))).filter(s => s.length > 8);
}

// ---------- 4. Parse ----------
G.skills = [];
for (const r of G.list) {
  const t = res(r.title); const w = G.pages[t]; if (!w) continue;
  const ibs = tpl(w, 'skill infobox'); if (!ibs.length) continue;
  const { named: raw } = params('x|' + ibs[0].body.replace(/^[^|\n]*/, ''));
  const f = {}; // normalise typo'd keys
  for (const [k, v] of Object.entries(raw)) f[k.replace(/^casues/, 'causes').replace(/^remvoes/, 'removes').replace(/^reqyires/, 'requires').replace(/^targert$/, 'target')] = v;
  const yes = k => /^\s*y/i.test(f[k] || '');
  const list = pre => Object.keys(f).filter(k => new RegExp('^' + pre + '\\d*$').test(k)).sort().map(k => clean(f[k])).filter(Boolean);
  const tags = [];
  const causes = list('causes'), removes = list('removes'), prevents = list('prevents'), requires = list('requires');
  if (causes.length) tags.push('causes: ' + causes.join(', '));
  if (removes.length) tags.push('removes: ' + removes.join(', '));
  if (prevents.length) tags.push('prevents: ' + prevents.join(', '));
  if (requires.length) tags.push('requires: ' + requires.join(', '));
  if (clean(f.target)) tags.push('target: ' + clean(f.target));
  if (clean(f.range)) tags.push('range: ' + clean(f.range));
  const aoe = [clean(f.aoe), clean(f.aoe2)].filter(Boolean); if (aoe.length) tags.push('aoe: ' + aoe.join(', '));
  if (yes('pbaoe')) tags.push('point-blank AoE');
  if (yes('unblockable')) tags.push('unblockable');
  if (yes('interrupt')) tags.push('interrupts');
  if (clean(f.special)) tags.push('special: ' + clean(f.special));
  const checks = list('checks'); if (checks.length) tags.push('checks: ' + checks.join(', '));
  G.skills.push({
    id: r.id, title: t, name: clean(f.name) || t, prof: clean(f.profession) || 'None', attr: clean(f.attribute) || 'No Attribute',
    type: clean(f.type), elite: yes('elite'), camp: clean(f.campaign),
    e: clean(f.energy), ad: clean(f.adrenaline), sac: clean(f.sacrifice), up: clean(f.upkeep), oc: clean(f.overcast), act: clean(f.activation), rec: clean(f.recharge),
    desc: clean(f.description), pveOnly: yes('pve-only'), isPvp: yes('is-pvp') || /\(PvP\)$/.test(t),
    prog: prog(w), tags, notes: notes(w)
  });
}

// ---------- 5. Filter: no PvE-only; PvP version replaces PvE version ----------
const pvpBase = new Set(G.skills.filter(s => s.isPvp).map(s => s.title.replace(/ \(PvP\)$/, '')));
const byTitle = Object.fromEntries(G.skills.map(s => [s.title, s]));
G.keep = G.skills.filter(s => !s.pveOnly && !(!s.isPvp && pvpBase.has(s.title)));
// PvP pages rarely carry notes; inherit the PvE page's bug/anomaly notes, labelled
for (const s of G.keep) if (s.isPvp) { const base = byTitle[s.title.replace(/ \(PvP\)$/, '')]; if (base && base.notes.length) s.notes = s.notes.concat(base.notes.map(n => n + ' [from PvE version page]')); }

// ---------- 6. Derived progressions for ranges with no wiki table ----------
G.derived = [];
for (const s of G.keep) {
  if (s.attr === 'No Attribute') continue;
  for (const m of s.desc.matchAll(/([+-]?)(\d+(?:\.\d+)?)\.\.(\d+(?:\.\d+)?)/g)) {
    const a = +m[2], b = +m[3];
    if (s.prog.some(p => +p.v[0] === a && +p.v[15] === b)) continue;
    const v = []; for (let r = 0; r <= 21; r++) v.push(rnd(a + r * (b - a) / 15));
    s.prog.push({ n: '(' + a + '..' + b + ')', v, auto: 1 }); G.derived.push(s.name + ' ' + a + '..' + b);
  }
}

// ---------- 7. Render ----------
const order = ['Warrior', 'Ranger', 'Monk', 'Necromancer', 'Mesmer', 'Elementalist', 'Assassin', 'Ritualist', 'Paragon', 'Dervish', 'None'];
const grp = v => { const g = []; for (let i = 0; i < v.length; i += 5) g.push(i + '-' + Math.min(i + 4, v.length - 1) + ': ' + v.slice(i, i + 5).join(' ')); return g.join(' | '); };
const cost = s => { const c = []; if (s.e) c.push('E' + s.e); if (s.ad) c.push('Ad' + s.ad); if (s.sac) c.push('S' + s.sac + (/%/.test(s.sac) ? '' : '%')); if (s.up) c.push('U' + s.up); if (s.oc) c.push('O' + s.oc); if (s.act) c.push('C' + s.act); if (s.rec) c.push('R' + s.rec); return c.join(' '); };
const esc = x => x.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const ks = [...G.keep].sort((a, b) => (order.indexOf(a.prof) - order.indexOf(b.prof)) || a.attr.localeCompare(b.attr) || a.name.localeCompare(b.name));
const out = []; let curP = '', curA = '';
for (const s of ks) {
  if (s.prof !== curP) { curP = s.prof; curA = ''; out.push('\n## ' + (s.prof === 'None' ? 'Common (no profession)' : s.prof)); }
  if (s.attr !== curA) { curA = s.attr; out.push('\n### ' + s.prof + ' / ' + s.attr); }
  const type = (s.elite ? 'Elite ' : '') + s.type;
  const d = s.desc.replace(new RegExp('^(Elite )?' + esc(s.type) + '\\.\\s*', 'i'), '');
  out.push(s.name + ' #' + s.id + ' | ' + type + ' | ' + s.camp + ' | ' + cost(s));
  out.push('  ' + d);
  for (const p of s.prog) if (p.v && p.v.length) out.push('  ~ ' + p.n + (p.auto ? ' [derived]' : '') + ' :: ' + grp(p.v));
  if (s.tags.length) out.push('  # ' + s.tags.join('; '));
  for (const n of s.notes) out.push('  ! ' + n);
}
G.out = out.join('\n');
G.stats = { listed: G.list.length, parsed: G.skills.length, kept: G.keep.length, pveOnlyDropped: G.skills.filter(s => s.pveOnly).length, pveSplitReplaced: pvpBase.size, derived: G.derived, withNotes: G.keep.filter(s => s.notes.length).length, noteLines: G.keep.reduce((a, s) => a + s.notes.length, 0), chars: G.out.length };
return G.stats;
})();
