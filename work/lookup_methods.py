import json

with open("work/il2cpp_dump/script.json", "r", encoding="utf-8") as f:
    data = json.load(f)

methods = data.get("ScriptMethod", [])
by_addr = {m["Address"]: m["Name"] for m in methods}

for addr in [0x1ae2854, 0x214cec4, 0x2157060, 0x150C760, 0x150C830, 0x12FA8B4, 0x12FA768, 0x12FA7D4, 0x12FA878]:
    print(f"0x{addr:x}: {by_addr.get(addr, 'Unknown')}")
