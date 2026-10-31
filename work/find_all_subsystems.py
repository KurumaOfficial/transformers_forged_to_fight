with open('work/il2cpp_dump/dump.cs', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

subsystems = []
api_classes = []

for i, line in enumerate(lines):
    if ': SubSystem' in line:
        subsystems.append(line.strip())
    elif 'class ' in line and ('API' in line or 'Service' in line):
        if not '<' in line and not 'CompilerGenerated' in line:
            api_classes.append(line.strip())

print(f"Total SubSystems: {len(subsystems)}")
for s in sorted(subsystems):
    print(" ", s)

print(f"\nTotal API classes: {len(api_classes)}")
for a in sorted(api_classes):
    if any(k in a for k in ['EB.Sparx', 'BCG', 'TF', 'Quest', 'Combat', 'Gacha', 'Shop', 'Store']):
        print(" ", a)
