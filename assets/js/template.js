// Guild Wars 1 skill template codes (spec: wiki.guildwars.com/wiki/Skill_template_format).
// Codes store canonical skill ids; PvP-split ids are mapped with pvpToTemplate before encoding.
const B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
export const PROFESSIONS = ["None", "Warrior", "Ranger", "Monk", "Necromancer", "Mesmer", "Elementalist",
  "Assassin", "Ritualist", "Paragon", "Dervish"];
export const ATTRIBUTES = {
  "Fast Casting": 0, "Illusion Magic": 1, "Domination Magic": 2, "Inspiration Magic": 3, "Blood Magic": 4,
  "Death Magic": 5, "Soul Reaping": 6, "Curses": 7, "Air Magic": 8, "Earth Magic": 9, "Fire Magic": 10,
  "Water Magic": 11, "Energy Storage": 12, "Healing Prayers": 13, "Smiting Prayers": 14, "Protection Prayers": 15,
  "Divine Favor": 16, "Strength": 17, "Axe Mastery": 18, "Hammer Mastery": 19, "Swordsmanship": 20, "Tactics": 21,
  "Beast Mastery": 22, "Expertise": 23, "Wilderness Survival": 24, "Marksmanship": 25, "Dagger Mastery": 29,
  "Deadly Arts": 30, "Shadow Arts": 31, "Communing": 32, "Restoration Magic": 33, "Channeling Magic": 34,
  "Critical Strikes": 35, "Spawning Power": 36, "Spear Mastery": 37, "Command": 38, "Motivation": 39,
  "Leadership": 40, "Scythe Mastery": 41, "Wind Prayers": 42, "Earth Prayers": 43, "Mysticism": 44,
};
const ATTR_NAME = Object.fromEntries(Object.entries(ATTRIBUTES).map(([k, v]) => [v, k]));
// Which attributes belong to which profession (primary attribute first)
export const PROF_ATTRS = {
  Warrior: ["Strength", "Axe Mastery", "Hammer Mastery", "Swordsmanship", "Tactics"],
  Ranger: ["Expertise", "Beast Mastery", "Marksmanship", "Wilderness Survival"],
  Monk: ["Divine Favor", "Healing Prayers", "Protection Prayers", "Smiting Prayers"],
  Necromancer: ["Soul Reaping", "Blood Magic", "Curses", "Death Magic"],
  Mesmer: ["Fast Casting", "Domination Magic", "Illusion Magic", "Inspiration Magic"],
  Elementalist: ["Energy Storage", "Air Magic", "Earth Magic", "Fire Magic", "Water Magic"],
  Assassin: ["Critical Strikes", "Dagger Mastery", "Deadly Arts", "Shadow Arts"],
  Ritualist: ["Spawning Power", "Channeling Magic", "Communing", "Restoration Magic"],
  Paragon: ["Leadership", "Command", "Motivation", "Spear Mastery"],
  Dervish: ["Mysticism", "Earth Prayers", "Scythe Mastery", "Wind Prayers"],
};

const width = (v, min) => Math.max(Math.max(1, Math.floor(v).toString(2).length), min);
const put = (bits, v, n) => { for (let i = 0; i < n; i++) bits.push((v >> i) & 1); };

export function encode({ primary, secondary = "None", attributes = {}, skills = [] }, pvpToTemplate = {}) {
  const p = typeof primary === "number" ? primary : PROFESSIONS.indexOf(primary);
  const s = typeof secondary === "number" ? secondary : PROFESSIONS.indexOf(secondary || "None");
  if (p <= 0 || s < 0) return null;
  const attrs = Object.entries(attributes).filter(([, r]) => +r > 0)
    .map(([a, r]) => [typeof a === "number" ? a : (ATTRIBUTES[a] ?? +a), Math.min(12, +r)]);
  const ids = [...skills.map((x) => pvpToTemplate[x] ?? (+x || 0)), 0, 0, 0, 0, 0, 0, 0, 0].slice(0, 8);
  const bits = [];
  put(bits, 14, 4); put(bits, 0, 4);
  let pw = width(Math.max(p, s), 4); if ((pw - 4) % 2) pw += 1;
  put(bits, (pw - 4) / 2, 2); put(bits, p, pw); put(bits, s, pw);
  put(bits, attrs.length, 4);
  const aw = width(Math.max(0, ...attrs.map(([a]) => a)), 4);
  put(bits, aw - 4, 4);
  for (const [a, r] of attrs) { put(bits, a, aw); put(bits, r, 4); }
  const sw = width(Math.max(...ids), 8);
  put(bits, sw - 8, 4);
  for (const x of ids) put(bits, x, sw);
  bits.push(0);
  while (bits.length % 6) bits.push(0);
  let out = "";
  for (let i = 0; i < bits.length; i += 6) { let v = 0; for (let j = 0; j < 6; j++) v |= bits[i + j] << j; out += B64[v]; }
  return out;
}

export function decode(code) {
  const bits = [];
  for (const ch of code.trim()) {
    const v = B64.indexOf(ch);
    if (v < 0) throw new Error("That isn't a template code: it contains '" + ch + "'.");
    for (let j = 0; j < 6; j++) bits.push((v >> j) & 1);
  }
  let pos = 0;
  const take = (n) => { let v = 0; for (let i = 0; i < n; i++) v |= (bits[pos + i] || 0) << i; pos += n; return v; };
  const header = take(4);
  if (header === 14) take(4); else if (header !== 0) throw new Error("This is not a skill template code (it may be an equipment template).");
  const pw = take(2) * 2 + 4;
  const primary = take(pw), secondary = take(pw);
  const n = take(4), aw = take(4) + 4;
  const attributes = {};
  for (let i = 0; i < n; i++) { const a = take(aw); attributes[ATTR_NAME[a] ?? a] = take(4); }
  const sw = take(4) + 8;
  const skills = [];
  for (let i = 0; i < 8; i++) skills.push(take(sw));
  if (!PROFESSIONS[primary]) throw new Error("Unknown primary profession in this code.");
  return { primary: PROFESSIONS[primary], secondary: PROFESSIONS[secondary] || "None", attributes, skills };
}
