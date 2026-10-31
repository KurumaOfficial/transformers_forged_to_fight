import json

with open('server/requests.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx in [0, 1, 2, 3]:
    if idx < len(lines):
        entry = json.loads(lines[idx])
        print(f"\n==================== Request #{idx+1}: {entry.get('method')} {entry.get('path')} ====================")
        print("Timestamp:", entry.get('timestamp'))
        print("Headers:", entry.get('headers'))
        body = entry.get('body')
        if isinstance(body, dict):
            # Print keys and summary
            print("Body keys:", list(body.keys()))
            for k in ['version', 'buildconfig', 'nonce', 'authenticator', 'user', 'salt', 'bid']:
                if k in body:
                    print(f"  {k}: {body[k]}")
