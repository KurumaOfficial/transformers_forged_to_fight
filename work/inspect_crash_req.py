import json

with open('server/requests.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx in [0, 1, 2, 3, 4]:
    if idx < len(lines):
        entry = json.loads(lines[idx])
        print(f"\n==================== Request #{idx+1}: {entry.get('method')} {entry.get('path')} ====================")
        body = entry.get('body')
        if isinstance(body, dict):
            print(json.dumps(body, indent=2))
        else:
            print(str(body)[:1000])
