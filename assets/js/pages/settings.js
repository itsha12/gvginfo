import { settings, saveSettings, esc, toast } from "../core.js";

export function renderSettings(view) {
  const s = { owner: "itsha12", repo: "gvginfo", branch: "main", ...settings() };
  view.innerHTML = `
    <h2>Settings</h2>
    <form class="editor" id="s" style="max-width:640px">
      <div class="grid">
        <label>GitHub account<input type="text" name="owner" value="${esc(s.owner)}" required></label>
        <label>Repository<input type="text" name="repo" value="${esc(s.repo)}" required></label>
        <label>Branch<input type="text" name="branch" value="${esc(s.branch)}" required></label>
      </div>
      <label>GitHub key<input type="password" name="token" value="${esc(s.token || "")}" autocomplete="off" placeholder="github_pat_…"></label>
      <div class="row"><button class="btn primary" type="submit">Save settings</button><button class="btn" type="button" id="test">Test connection</button><button class="btn danger" type="button" id="forget">Remove key from this browser</button></div>
      <p class="muted" id="result"></p>
    </form>`;
  const form = view.querySelector("#s");
  const read = () => ({ owner: form.owner.value.trim(), repo: form.repo.value.trim(), branch: form.branch.value.trim() || "main", token: form.token.value.trim() });
  form.onsubmit = (e) => { e.preventDefault(); saveSettings(read()); dispatchEvent(new Event("settings-changed")); toast("Settings saved"); };
  view.querySelector("#forget").onclick = () => { const v = read(); delete v.token; saveSettings(v); form.token.value = ""; dispatchEvent(new Event("settings-changed")); toast("Key removed from this browser"); };
  view.querySelector("#test").onclick = async () => {
    const v = read(); const out = view.querySelector("#result");
    out.textContent = "Checking…";
    try {
      const r = await fetch(`https://api.github.com/repos/${v.owner}/${v.repo}`, { headers: { Authorization: `Bearer ${v.token}` } });
      const j = await r.json();
      out.textContent = r.ok ? (j.permissions?.push ? "Connected. This key can save to the repository." : "Connected, but this key can't write. Give it Contents: Read and write.")
        : `GitHub said ${r.status}: ${j.message}. Check the account, repository and key.`;
    } catch (e) { out.textContent = `Couldn't reach GitHub: ${e.message}`; }
  };
}
