import json

with open(r'work\il2cpp_dump\script.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

method_map = {m['Address']: m['Name'] for m in data['ScriptMethod']}

calls = [0x16467a0, 0x1451998, 0x146c9cc, 0x1711bec, 0x144f534, 0x1496304, 0x146fe20, 0x146eb00]

for c in calls:
    print(f"{hex(c)}: {method_map.get(c, 'UNKNOWN')}")
