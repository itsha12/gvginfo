"""Build features and matchup context (causal map C.builds, C.matchup): what each team's bars can do, counted from the
skill data (what a skill causes and removes), so any build, even one never seen, gets the same description. Matchup
features pair a threat with its answer (enemy knockdowns against own Aura of Stability, and so on); how much each
matters comes from data, never from a label.

Usage:  python3 buildfeat.py <report id>
In code: team_features(m, tm) -> dict; matchup(m, tm) -> dict from tm's side."""
import json, os, sys
from common import REPO

_S = None
def _skills():
    global _S
    if _S is None:
        d = json.load(open(os.path.join(REPO, "data", "skills.json")))
        rows = d["skills"] if isinstance(d, dict) and "skills" in d else d
        rows = list(rows.values()) if isinstance(rows, dict) else rows
        _S = {}
        for s in rows:
            _S[s["name"]] = s; _S[s["name"].replace(" (PvP)", " PvP")] = s
    return _S


FEATURES = {   # feature: test on a skill record
    "interrupts": lambda s: "Interrupt" in (s.get("causes") or []),
    "knockdowns": lambda s: "Knockdown" in (s.get("causes") or []),
    "blind": lambda s: "Blind" in (s.get("causes") or []),
    "weakness": lambda s: "Weakness" in (s.get("causes") or []),
    "daze": lambda s: "Dazed" in (s.get("causes") or []),
    "snares": lambda s: bool({"Crippled", "Decreased Movement Speed"} & set(s.get("causes") or [])),
    "deep_wound": lambda s: "Deep Wound" in (s.get("causes") or []),
    "energy_denial": lambda s: "Energy Loss" in (s.get("causes") or []),
    "strips": lambda s: "Enchantment" in (s.get("removes") or []) and (s.get("target") or "").lower().startswith("foe"),
    "hexes": lambda s: "Hex" in (s.get("type") or ""),
    "condition_removal": lambda s: any(x.lower() == "condition" for x in (s.get("removes") or [])) and "foe" not in (s.get("target") or "").lower(),
    "hex_removal": lambda s: "Hex spell" in (s.get("removes") or []),
    "prots": lambda s: s.get("attr") == "Protection Prayers" and "Enchantment" in (s.get("type") or "") or s["name"].startswith(("Infuse Health", "Reversal of Fortune", "Protective Spirit")),
    "blocks": lambda s: "Block" in (s.get("causes") or []),
    "aura_of_stability": lambda s: s["name"] == "Aura of Stability",
    "heals": lambda s: "Healing" in (s.get("causes") or []),
    "speed": lambda s: "Increased Movement Speed" in (s.get("causes") or []),
}
# threat (enemy) against answer (own): the matchup pairs
PAIRS = [("knockdowns", "aura_of_stability"), ("blind", "condition_removal"), ("hexes", "hex_removal"),
         ("strips", "prots"), ("energy_denial", "heals"), ("interrupts", "heals"), ("snares", "speed")]


def team_features(m, tm):
    S = _skills()
    out = {k: 0 for k in FEATURES}
    for a in m.PL:
        if m.team(a) != tm: continue
        for b in m.A[a].get("bar", []):
            if not b: continue
            s = S.get(m.sk(b))
            if not s: continue
            for k, f in FEATURES.items():
                if f(s): out[k] += 1
    return out


def matchup(m, tm):
    own, foe = team_features(m, tm), team_features(m, 3 - tm)
    out = {f"own_{k}": v for k, v in own.items()}
    out.update({f"enemy_{k}": v for k, v in foe.items()})
    for threat, answer in PAIRS:
        out[f"enemy_{threat}_v_own_{answer}"] = foe[threat] - own[answer]
        out[f"own_{threat}_v_enemy_{answer}"] = own[threat] - foe[answer]
    return out


if __name__ == "__main__":
    from replaylib import Match
    m = Match.from_branch(sys.argv[1])
    for tm in (1, 2): print(m.tag[tm], team_features(m, tm))
