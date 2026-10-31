import json
import struct

with open('work/il2cpp_dump/script.json', 'r', encoding='utf-8') as f:
    script = json.load(f)

print("--- Matching Methods ---")
for m in script.get('ScriptMethod', []):
    name = m.get('Name', '')
    if any(k in name for k in ['BaseManager$$', 'BaseSubManager$$', 'SparxHub$$', 'DataManager$$', 'Hub$$']):
        if any(w in name.lower() for w in ['connect', 'login', 'deserialize', 'active', 'load', 'fatal', 'error', 'init', 'on']):
            addr = m['Address']
            print(f"0x{addr:X}: {name}")
