import json

with open('server/requests.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total entries in requests.jsonl: {len(lines)}")
for i, line in enumerate(lines):
    if not line.strip():
        continue
    try:
        entry = json.loads(line)
        print(f"\n==================== Request #{i+1} ====================")
        print(f"Time:    {entry.get('timestamp')}")
        print(f"Client:  {entry.get('client_ip')}:{entry.get('client_port')}")
        print(f"Method:  {entry.get('method')} {entry.get('path')}")
        print(f"Headers:")
        for h, v in entry.get('headers', {}).items():
            print(f"  {h}: {v}")
        body = entry.get('body')
        if isinstance(body, dict):
            print("Body (JSON):")
            print(json.dumps(body, indent=2))
        else:
            print(f"Body (Text, len={len(str(body))}):")
            print(str(body)[:300])
    except Exception as e:
        print(f"Line {i} error: {e}")
