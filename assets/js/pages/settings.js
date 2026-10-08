import { settings, saveSettings, esc, toast } from "../core.js";

export function renderSettings(view) {
  const s = { owner: "itsha12", repo: "gvginfo", branch: "main", ...settings() };
  view.innerHTML = `
    <h2>Settings</h2>
    <p class="lede">Saving templates and notes writes to your GitHub repository. Your key is stored only in this browser; on a new device, paste it again.</p>
    <form class="editor" id="s" style="max-width:640px">
      <div class="grid">
        <label>GitHub account<input type="text" name="owner" value="${esc(s.owner)}" required></label>
        <label>Repository<input type="text" name="repo" value="${esc(s.repo)}" required></label>
        <label>Branch<input type="text" name="branch" value="${esc(s.branch)}" required></label>
      </div>
      <label>GitHub key<input type="password" name="token" value="${esc(s.token || "")}" autocomplete="off" placeholder="github_pat_…"></label>
      <div class="row"><button class="btn primary" type="submit">Save settings</button><button class="btn" type="button" id="test">Test connection</button><button class="btn danger" type="button" id="forget">Remove key from this browser</button></div>
      <p class="muted" id="result"></p>
    </form>
    <h3>Getting a key</h3>
    <ol class="doc">
      <li>On GitHub, open Settings, then Developer settings, then Personal access tokens, then Fine-grained tokens, and choose Generate new token.</li>
      <li>Under Repository access pick Only select repositories and choose <b>${esc(s.repo)}</b>.</li>
      <li>Under Repository permissions set Contents to Read and write and Actions to Read and write (Actions runs the update buttons).</li>
      <li>Generate it, copy it, paste it above and save.</li>
    </ol>`;
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
