import os, re, json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
root = Path(r".\work\unpacked\assets\bin\Data")
out = {}
for p in root.iterdir():
    if not p.is_file():
        continue
    b = p.read_bytes()
    if b"STAT_" not in b:
        continue
    for m in re.finditer(rb'"k":"((?:D|ID)_STAT_[^"]+)"', b):
        key = m.group(1).decode("utf-8", "replace")
        tail = b[m.end():m.end()+3000]
        vm = re.search(rb'"v":"((?:\\.|[^"\\])*)"', tail)
        if not vm:
            continue
        val = vm.group(1).decode("utf-8", "replace")
        val = val.replace('\\"', '"').replace('\\n', '\n').replace('\\/', '/')
        score = sum(ch.isascii() and (ch.isalpha() or ch.isdigit()) for ch in val)
        if key not in out or score > out[key]["ascii_score"]:
            out[key] = {"key": key, "value": val, "ascii_score": score, "file": p.name}
rows = sorted(out.values(), key=lambda r: r["key"])
for r in rows:
    r.pop("ascii_score", None)
data = {
    "source": "binary scan of work/unpacked/assets/bin/Data for D_STAT_/ID_STAT_ key/value pairs",
    "tag": "[CLIENT]",
    "count": len(rows),
    "note": "Best ASCII-containing localized value per key; values can be German/Italian/English depending on the asset language table. Not a claim of complete multilingual coverage.",
    "entries": rows,
}
(Path(r".\data\wiki\ability_localization_client.json")).write_text(
    json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
print("STAT entries", len(rows), "ascii", sum(any(c.isalpha() for c in r["value"]) for r in rows))
print(rows[:5])
