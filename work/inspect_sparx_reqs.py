import json

with open('server/requests.jsonl', 'r', encoding='utf-8') as f:
    reqs = [json.loads(line) for line in f if line.strip()]

print(f"Total requests: {len(reqs)}")
# Look at requests #1 to #36 (the first login batch)
for i, r in enumerate(reqs[:36]):
    headers = {k.lower(): v for k, v in r.get('headers', {}).items()}
    ua = headers.get('user-agent', '')
    m = r.get('method')
    p = r.get('path')
    q = r.get('query')
    b = r.get('body')
    stoken = headers.get('stoken')
    print(f"#{i+1:3d}: {m:4s} {p:40s} | stoken={stoken}")
    if q:
        print(f"      Query: {q}")
    if b and isinstance(b, dict):
        # print first few keys
        keys = list(b.keys())[:5]
        print(f"      Body keys: {keys}")
    elif b:
        print(f"      Body: {str(b)[:100]}")
