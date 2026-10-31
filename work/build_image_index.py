import json, re
from collections import Counter
from pathlib import Path
root = Path(r".")
m = json.loads((root / "archive/wiki/manifest.json").read_text(encoding="utf-8"))
errs = json.loads((root / "archive/wiki/errors.json").read_text(encoding="utf-8"))
imgs = [r for r in m if r.get("path", "").startswith("raw/fandom/files/")]
def cat(name):
    s = name.lower()
    if "map" in s or "quest" in s or "chapter" in s or "act" in s:
        return "maps_quests"
    if "ui" in s or "icon" in s or "button" in s or "hud" in s or "logo" in s:
        return "ui"
    if "relic" in s or "mod" in s or "crystal" in s or "chip" in s or "gold" in s or "energon" in s:
        return "items"
    if "bot" in s or "character" in s or "portrait" in s:
        return "bots"
    return "other"
rows = []
for r in imgs:
    name = r["path"].rsplit("/", 1)[-1]
    rows.append({"path": r["path"], "name": name, "bytes": r.get("size"), "sha256": r.get("sha256"),
                 "category": cat(name), "status": "present"})
present = Counter(r["category"] for r in rows)
errors = [{"file": e.get("file"), "error": e.get("error"), "category": cat(e.get("file", ""))} for e in errs]
ec = Counter(e["category"] for e in errors)
out = {
    "source": "archive/wiki/manifest.json + errors.json",
    "counts": {"present": len(rows), "errors": len(errors), "expected": len(rows) + len(errors)},
    "present_by_category": dict(present),
    "errors_by_category": dict(ec),
    "present": rows,
    "errors": errors,
    "note": "Image binaries only; no bypass. Error category is a filename heuristic.",
}
(root / "data/wiki/image_index.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(out["counts"], out["present_by_category"], out["errors_by_category"])
