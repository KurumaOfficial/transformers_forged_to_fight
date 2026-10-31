import json

with open("work/il2cpp_dump/stringliteral.json", "r", encoding="utf-8") as f:
    literals = json.load(f)

by_addr = {lit.get("address"): lit.get("value") for lit in literals}
print("0x2D46A58 ->", by_addr.get("0x2D46A58"))
print("0x2D56268 ->", by_addr.get("0x2D56268"))
