import json
from pathlib import Path
p = Path(r"C:\Users\gameg\Desktop\TFTF\data\wiki\image_index.json")
d = json.loads(p.read_text(encoding="utf-8"))
names = {r["name"] for r in d["present"]}
d["counts"]["present_manifest_entries"] = len(d["present"])
d["counts"]["present_unique_files"] = len(names)
d["note"] = (d.get("note", "") + " Four manifest entries are duplicate paths/names; unique files = 694.").strip()
p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(d["present"]), len(names))
