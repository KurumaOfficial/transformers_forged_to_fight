import json

with open("work/il2cpp_dump/stringliteral.json", "r", encoding="utf-8") as f:
    literals = json.load(f)

for lit in literals:
    addr_int = int(lit.get("address", "0"), 16)
    if abs(addr_int - 0x2D46A58) < 0x200:
        print(lit.get("address"), "->", lit.get("value"))
