import { loadData, installTooltips, state, canSave } from "./core.js";
import { renderHome } from "./pages/home.js";
import { renderSkills } from "./pages/skills.js";
import { renderTemplates } from "./pages/templates.js";
import { renderKnowledge } from "./pages/knowledge.js";
import { renderSettings } from "./pages/settings.js";
import { renderBuilds } from "./pages/builds.js";
import { renderPlayers } from "./pages/players.js";
import { renderMeta } from "./pages/meta.js";
import { renderSchedule } from "./pages/schedule.js";
import { renderGuilds } from "./pages/guilds.js";

const routes = { schedule: renderSchedule, guilds: renderGuilds, "": renderHome, home: renderHome, builds: renderBuilds, meta: renderMeta, players: renderPlayers, templates: renderTemplates, skills: renderSkills, knowledge: renderKnowledge, settings: renderSettings };
const view = document.getElementById("view");

function route() {
  const [, page = "", ...rest] = location.hash.replace(/^#/, "").split("/");
  document.querySelectorAll(".top nav a").forEach((a) => {
    const target = a.getAttribute("href").replace(/^#\//, "");
    if (target === page || (target === "" && page === "home")) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
  });
  (routes[page] || renderHome)(view, rest.map(decodeURIComponent));
  view.focus({ preventScroll: true });
}

function syncLine() {
  document.getElementById("sync").textContent =
    `${state.meta.count} skills loaded. ${canSave() ? "Changes save to GitHub." : "View only: add your GitHub key in Settings to save changes."}`;
}

(async () => {
  try {
    await loadData();
  } catch (e) {
    view.innerHTML = `<div class="empty-state">The skill data didn't load (${e.message}). Check that data/skills.json is in the repository.</div>`;
    return;
  }
  installTooltips();
  syncLine();
  addEventListener("hashchange", route);
  addEventListener("settings-changed", syncLine);
  route();
})();
