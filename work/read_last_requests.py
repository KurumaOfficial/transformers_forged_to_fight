import json

with open('server/requests.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total requests logged: {len(lines)}")
for l in lines[-35:]:
    data = json.loads(l)
    path = data.get('path', '')
    method = data.get('method', '')
    status = data.get('status', '')
    resp_body = str(data.get('response_body', ''))[:80]
    print(f"{method:4s} {path:35s} -> {status} | body: {resp_body}")
