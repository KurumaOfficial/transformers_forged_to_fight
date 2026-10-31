import json

with open("work/il2cpp_dump/stringliteral.json", "r", encoding="utf-8") as f:
    literals = json.load(f)

for lit in literals:
    val = lit.get("value", "")
    if any(k in val.lower() for k in ["apkprotect", "signature", "detectandroidjni", "detect"]):
        print(f"Address: {lit.get('address')}, Value: {val}")
