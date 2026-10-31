import json
import re

with open('server/requests.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    entry = json.loads(l)
    if entry.get("path") == "/krash":
        print(f"\n==================== KRASH REPORT (Request #{i+1}) ====================")
        body = entry.get("body", "")
        # Find all ASCII strings of length >= 6
        text_matches = re.findall(r'[\x20-\x7e]{6,}', body)
        for s in text_matches:
            if any(k in s for k in ['Exception', 'NullReference', 'Login', 'Sparx', 'Error', 'Stack', 'File', 'Line']):
                print("  ", s)
