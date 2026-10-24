import os
import re
import json

ROOT = r"C:\Users\gameg\Desktop\TFTF"
BASE = os.path.join(ROOT, "work", "unpacked", "assets")
pat = re.compile(rb'((?:ID_STAT|D_STAT)[A-Za-z0-9_\.]*)')
keys = set()
files = 0
for dirpath, _dirs, names in os.walk(BASE):
    for name in names:
        path = os.path.join(dirpath, name)
        try:
            size = os.path.getsize(path)
            if size > 80 * 1024 * 1024:
                continue
            with open(path, "rb") as fh:
                blob = fh.read()
        except Exception:
            continue
        found = set(m.group(1).decode("latin1") for m in pat.finditer(blob))
        if found:
            files += 1
            keys |= found
print("files with D_STAT/ID_STAT:", files, "unique keys:", len(keys))
print("D_STAT:", sum(1 for k in keys if k.startswith("D_STAT")),
      "ID_STAT:", sum(1 for k in keys if k.startswith("ID_STAT")))
cur = json.load(open(os.path.join(ROOT, "data", "wiki", "ability_localization_client.json"), encoding="utf-8"))["entries"]
print("current entries:", len(cur), "current D_STAT:", sum(1 for k in cur if k.startswith("D_STAT")),
      "current ID_STAT:", sum(1 for k in cur if k.startswith("ID_STAT")))
print("extra sample:", sorted(keys - set(cur))[:40])
print("missing sample:", sorted(set(cur) - keys)[:40])
