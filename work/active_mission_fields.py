import json

with open('work/il2cpp_dump/script.json', 'r', encoding='utf-8') as f:
    script = json.load(f)

# Let's inspect the fields of ActiveMission in dump.cs
with open('work/il2cpp_dump/dump.cs', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i in range(308330, 308375):
    print(lines[i].strip())
