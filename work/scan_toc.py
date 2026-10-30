import collections
import json
import os
import re

ROOT = "work/unpacked/assets"
chars = collections.Counter()
moves = collections.Counter()
tocs = []
for dp, dn, fn in os.walk(ROOT):
    for f in fn:
        if f != "toc.txt":
            continue
        p = os.path.join(dp, f)
        tocs.append(p)
        s = open(p, encoding="utf-8", errors="replace").read()
        for m in re.finditer(r"bundles/characters/merged/([^\"\\/]+)", s):
            chars[m.group(1)] += 1
        for m in re.finditer(r"bundles/movedata/([^\"\\/]+)", s):
            moves[m.group(1)] += 1

print("tocs", len(tocs))
print("char tokens", len(chars))
print("move tokens", len(moves))
print("chars sample", list(chars)[:50])
print("moves sample", list(moves)[:30])
json.dump({"chars": chars, "moves": moves},
          open("work/census_raw.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
