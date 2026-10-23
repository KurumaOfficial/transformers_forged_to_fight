import json
from pathlib import Path
root = Path(r"C:\Users\gameg\Desktop\TFTF")
d = json.loads((root / "work/localization_all.json").read_text(encoding="utf-8"))
stat = {k: v for k, v in d.items() if k.startswith("D_STAT")}
out = {
    "source": "work/localization_all.json extracted from work/unpacked/assets/bin/Data",
    "tag": "[CLIENT]",
    "total_localization_keys": len(d),
    "d_stat_keys": len(stat),
    "note": "Only D_STAT keys found by the JSON-object extractor are listed. Ability descriptions may live in other text assets; this is not a complete ability table.",
    "entries": stat,
}
(root / "data/wiki/ability_localization_client.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(len(stat), "D_STAT keys")
for k, v in stat.items():
    print(k, "=", v[:100].replace("\n", " "))
