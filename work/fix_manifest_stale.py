import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
root = Path(r"C:\Users\gameg\Desktop\TFTF")
W = root / "archive" / "wiki"
manifest = json.loads((W / "manifest.json").read_text(encoding="utf-8"))
by = {r["path"]: r for r in manifest}
paths = [
    "raw/fandom/revisions/0/Meet%20Your%20Makers.json",
    "raw/fandom/html/0/Meet%20Your%20Makers.html",
    "raw/fandom/revisions/0/Nothing%20And%20Everything.json",
    "raw/fandom/html/0/Nothing%20And%20Everything.html",
    "raw/fandom/file_descriptions/File%3A3-Star%20Bot%20Crystal%20Shard.png.json",
]
corr = []
for rel in paths:
    p = W / rel
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    old = by[rel]
    corr.append({"path": rel, "old_sha256": old.get("sha256"), "old_size": old.get("size"),
                 "new_sha256": h, "new_size": p.stat().st_size,
                 "checked": datetime.now(timezone.utc).isoformat()})
    old["sha256"] = h
    old["size"] = p.stat().st_size
    old["manifest_corrected"] = "2026-10-23 stale hash; file content validated (JSON/HTML)"
(W / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
(W / "manifest_corrections_2026-10-23.json").write_text(json.dumps({"reason": "stale manifest hashes after raw archive replacement; files validated before correction", "corrections": corr}, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"corrected": len(corr), "paths": paths}, ensure_ascii=False, indent=2))
