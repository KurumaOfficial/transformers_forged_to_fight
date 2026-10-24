import os
import re
import json

ROOT = r"C:\Users\gameg\Desktop\TFTF"
DATA = os.path.join(ROOT, "work", "unpacked", "assets", "bin", "Data")
pat = re.compile(rb'"k"\s*:\s*"((?:\\.|[^"\\])*)"')
keys = set()
per_file = {}
for name in os.listdir(DATA):
    path = os.path.join(DATA, name)
    if not os.path.isfile(path):
        continue
    with open(path, "rb") as fh:
        blob = fh.read()
    for m in pat.finditer(blob):
        try:
            key = m.group(1).decode("utf-8", "replace")
        except Exception:
            continue
        keys.add(key)
        per_file.setdefault(name, set()).add(key)
cur = set(json.load(open(os.path.join(ROOT, "work", "localization_all.json"), encoding="utf-8")))
print("bin/Data unique k keys:", len(keys))
print("current localization_all:", len(cur))
print("extra vs current:", len(keys - cur), "missing vs current:", len(cur - keys))
print("extra sample:", sorted(keys - cur)[:40])
print("missing sample:", sorted(cur - keys)[:40])
print("files with keys:", len(per_file))
# D_STAT / ID_STAT counts
for prefix in ("D_STAT", "ID_STAT"):
    print(prefix, sum(1 for k in keys if k.startswith(prefix)), "current", sum(1 for k in cur if k.startswith(prefix)))
