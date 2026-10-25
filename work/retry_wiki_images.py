"""W1: retry 403 images for priority categories (maps_quests, ui) with Referer."""
import hashlib
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(r"C:\Users\gameg\Desktop\TFTF")
INDEX = ROOT / "data" / "wiki" / "image_index.json"
MANIFEST = ROOT / "archive" / "wiki" / "manifest.json"
OUTDIR = ROOT / "archive" / "wiki" / "raw" / "fandom" / "files"
REPORT = ROOT / "archive" / "wiki" / "W1_RETRY_2026-10-25.json"

PRIORITY = {"maps_quests", "ui"}
errors = json.loads(INDEX.read_text(encoding="utf-8"))["errors"]
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
by_name = {}
for e in manifest:
    p = e.get("path", "")
    if "/files/" in p:
        by_name[Path(urllib.parse.unquote(p)).name] = e

results = []
for err in errors:
    if err.get("category") not in PRIORITY:
        continue
    name = err["file"]
    e = by_name.get(name)
    if not e:
        results.append({"file": name, "status": "no_url"})
        continue
    url = e["source"]
    req = urllib.request.Request(url, headers={
        "Referer": "https://transformers-forged-to-fight.fandom.com/wiki/File:" + urllib.parse.quote(name),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        if len(data) < 100:
            results.append({"file": name, "status": "short", "bytes": len(data)})
            continue
        dest = OUTDIR / name
        dest.write_bytes(data)
        results.append({"file": name, "status": "ok", "bytes": len(data),
                        "sha256": hashlib.sha256(data).hexdigest()})
        print("ok", name, len(data))
    except Exception as exc:
        code = getattr(exc, "code", None)
        results.append({"file": name, "status": f"http_{code}" if code else "error",
                        "error": str(exc)})
        print("fail", name, exc)
        if code == 429:
            print("429: stop")
            break
    time.sleep(1.5)

REPORT.write_text(json.dumps({
    "date": "2026-10-25",
    "method": "Referer + browser UA, 1.5 s pause, stop on 429",
    "categories": sorted(PRIORITY),
    "results": results,
}, ensure_ascii=False, indent=1), encoding="utf-8")
print("report", REPORT, "ok", sum(1 for r in results if r["status"] == "ok"))
