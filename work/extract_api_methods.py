import re
import json

with open('work/il2cpp_dump/dump.cs', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Find all API class blocks
api_class_regex = re.compile(r'public class (\w+API)\b[^{]*\{([^}]+)\}', re.MULTILINE)
matches = api_class_regex.findall(text)

print(f"Found {len(matches)} API class declarations in dump.cs")

api_methods = {}
for cls_name, cls_body in matches:
    # extract methods
    method_lines = [l.strip() for l in cls_body.split('\n') if '(' in l and ')' in l and not l.strip().startswith('//') and not l.strip().startswith('[')]
    api_methods[cls_name] = method_lines

for cls_name, methods in sorted(api_methods.items()):
    print(f"\n=== {cls_name} ({len(methods)} methods) ===")
    for m in methods[:10]:
        print(f"  {m}")
    if len(methods) > 10:
        print(f"  ... and {len(methods)-10} more")
