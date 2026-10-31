import json

with open('work/il2cpp_dump/stringliteral.json', 'r', encoding='utf-8') as f:
    strings = json.load(f)

for s in strings:
    v = s.get('value', '')
    if v.lower() in ['user', 'alliance', 'base', 'bases', 'buildings', 'unlocks', 'available_buildings', 'available', 'user_base', 'alliance_base']:
        print(s.get('address'), repr(v))
