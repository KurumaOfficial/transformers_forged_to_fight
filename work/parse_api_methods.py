with open('work/il2cpp_dump/dump.cs', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

api_classes = {}
current_class = None
brace_depth = 0
current_methods = []

for line in lines:
    stripped = line.strip()
    if stripped.startswith('public class ') and stripped.split('//')[0].strip().endswith('API'):
        current_class = stripped.split('//')[0].replace('public class ', '').strip()
        brace_depth = 0
        current_methods = []
    elif current_class:
        if '{' in line:
            brace_depth += line.count('{')
        if '(' in line and ')' in line and not stripped.startswith('//') and not stripped.startswith('[') and not 'class ' in line:
            current_methods.append(stripped)
        if '}' in line:
            brace_depth -= line.count('}')
            if brace_depth <= 0:
                api_classes[current_class] = current_methods
                current_class = None

print(f"Parsed {len(api_classes)} API classes:")
for name, methods in sorted(api_classes.items()):
    non_ctor = [m for m in methods if not '.ctor' in m and not 'Post' in m and not 'Get' in m]
    print(f"\n=== {name} ({len(non_ctor)} API operations) ===")
    for m in non_ctor:
        print(f"  {m}")
