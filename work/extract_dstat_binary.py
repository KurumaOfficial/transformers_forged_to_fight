import os, re, json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
root = Path(r".\work\unpacked\assets\bin\Data")
out = {}
file_lang = {}
for p in root.iterdir():
    if not p.is_file():
        continue
    b = p.read_bytes()
    if b"D_STAT_" not in b:
        continue
    for m in re.finditer(rb'"k":"(D_STAT_[^"]+)"', b):
        key = m.group(1).decode("utf-8", "replace")
        tail = b[m.end():m.end()+2000]
        vm = re.search(rb'"v":"((?:\\.|[^"\\])*)"', tail)
        if not vm:
            continue
        raw = vm.group(1)
        try:
            val = raw.decode("utf-8", "replace")
            val = val.replace('\\"', '"').replace('\\n', '\n').replace('\\/', '/')
        except Exception:
            continue
        # Prefer a value with Latin letters or digits over pure Korean/Russian.
        score = sum(ch.isascii() and (ch.isalpha() or ch.isdigit()) for ch in val)
        if key not in out or score > out[key]["ascii_score"]:
            out[key] = {"key": key, "value": val, "ascii_score": score, "file": p.name}
rows = sorted(out.values(), key=lambda r: r["key"])
for r in rows:
    r.pop("ascii_score", None)
data = {
    "source": "binary scan of work/unpacked/assets/bin/Data for D_STAT_* key/value pairs",
    "tag": "[CLIENT]",
    "count": len(rows),
    "note": "Best ASCII-containing localized value per key; not a full multilingual table.",
    "entries": rows,
}
(Path(r".\data\wiki\ability_localization_client.json")).write_text(
    json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
print("D_STAT entries", len(rows), "ascii", sum(any(c.isalpha() for c in r["value"]) for r in rows))
print(rows[:5])
