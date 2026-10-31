import json, bisect, sys
m = json.load(open(r".\work\rva_map.json", encoding="utf-8"))
ks = sorted((int(k), v) for k, v in m.items())
a = [k for k, _ in ks]
for x in [0x9bb514, 0x9bb804, 0x9bb4e0, 0x9bb53c, 0x9bb530, 0x9bb504, 0x9bb4fc, 0x146428c, 0x1486674, 0x1fff294, 0x954fd0]:
    i = bisect.bisect_right(a, x) - 1
    k, v = ks[i]
    print(hex(x), "->", hex(k), v["class"], "::", v["name"], "+", hex(x - k))
