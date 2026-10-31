import json

with open("work/il2cpp_dump/stringliteral.json", "r", encoding="utf-8") as f:
    literals = json.load(f)

by_addr = {int(l["address"], 16): l["value"] for l in literals if "address" in l}

addrs = [0x2d6a7e8, 0x2d680a0, 0x2d1c868, 0x2d158c0, 0x2d4eba8, 0x2d55238, 0x2d51c28, 0x2d61af8]

for a in addrs:
    print(f"0x{a:x} -> {by_addr.get(a, 'NOT FOUND')!r}")
