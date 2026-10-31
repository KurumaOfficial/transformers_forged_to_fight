import struct, json, bisect
b = open(r".\work\unpacked\lib\arm64-v8a\libil2cpp.so", "rb").read()
pat = struct.pack("<I", 0x10A0038)
offs = []
start = 0
while True:
    i = b.find(pat, start)
    if i < 0:
        break
    offs.append(i)
    start = i + 1
print("hits", len(offs))
m = json.load(open(r".\work\rva_map.json", encoding="utf-8"))
ks = sorted((int(k), v) for k, v in m.items())
a = [k for k, _ in ks]
for off in offs[:50]:
    i = bisect.bisect_right(a, off) - 1
    if i >= 0:
        k, v = ks[i]
        print(f"{off:#x} -> {v['class']}::{v['name']} +{off-k:#x}")
    else:
        print(f"{off:#x}")
