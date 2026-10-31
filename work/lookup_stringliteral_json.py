import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'work\il2cpp_dump\stringliteral.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

targets = {
    0x2d39f98: "0x2d39f98",
    0x2d15ed0: "0x2d15ed0",
    0x2d7dc80: "0x2d7dc80",
    0x2d6ba48: "0x2d6ba48"
}

addr_map = {int(item["address"], 16): item["value"] for item in data}

for t in targets:
    if t in addr_map:
        print(f"EXACT: {hex(t)} -> {repr(addr_map[t])}")
    else:
        for a, v in addr_map.items():
            if abs(a - t) <= 0x10:
                print(f"NEAR {hex(t)}: {hex(a)} -> {repr(v)}")
