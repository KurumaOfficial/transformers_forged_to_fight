import json, bisect
m = json.load(open(r".\work\rva_map.json", encoding="utf-8"))
ks = sorted((int(k), v) for k, v in m.items())
a = [k for k, _ in ks]
for x in [0xCA5684,0xCA6BCC,0xCA65F0,0xCA6D1C,0xCA75DC,0xCA7A10,0xCA7BA8,0xCA7318,0xCA8A20,0xCA8ADC,0xCA9154]:
    i = bisect.bisect_right(a, x) - 1
    k, v = ks[i]
    print(hex(x), v["class"], "::", v["name"], "+", hex(x-k))
