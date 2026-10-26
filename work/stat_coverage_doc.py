import json
from pathlib import Path

d = json.loads(Path("data/wiki/stat_coverage.json").read_text(encoding="utf-8"))["rows"]
a = [r for r in d if r["label"] == "[ASSUMED]"]
lines = ["# R1 stat coverage (Step 5.1)", "",
         f"37 WIKI/table, {len(a)} ASSUMED.", "",
         "| client | class | HP | ATK | uncertainty | anchor/method |",
         "|---|---|---:|---:|---:|---|"]
for r in a:
    lines.append("| {client_id} | {class} | {level1_hp} | {level1_attack} | {uncertainty_pct}% | {reason} |".format(**r))
lines += ["", "## Missing for [DERIVED]", "",
          "- No wiki stat table and no star-1 HP/ATK for 20 bots; only class/rarity is known.",
          "- Rodimus Prime and Sunstreaker have star-3 HP/ATK; used as an anchor with the global star ratio (10% uncertainty).",
          "- The 20 class-median priors use the median of the 37 table bots in the same class; 25% uncertainty.",
          "- A live UI check is blocked by `FuseODRBlocker`; these are data priors, not UI-verified values."]
Path("docs/stat_coverage.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", len(a))
