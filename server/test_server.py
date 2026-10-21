import urllib.request
import json
import time

base = "http://127.0.0.1:8080"

endpoints = [
    ("/auth/prelogin", {"sha1": "test_sha1"}),
    ("/auth/login", {"authenticator": "guest", "credentials": {}}),
    ("/account/data", None),
    ("/tuning", None),
    ("/bcg/getBaseHeroData", {}),
    ("/bcg/getUserData", {}),
    ("/wallet/fetch", None),
    ("/unknown/subsystem/call", {"test": 123})
]

print("Starting client test against stub server...")
for path, payload in endpoints:
    url = base + path
    data = json.dumps(payload).encode('utf-8') if payload is not None else None
    headers = {"Content-Type": "application/json", "stoken": "test_token"}
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if payload is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=3) as res:
            res_body = res.read().decode('utf-8')
            parsed = json.loads(res_body)
            print(f"[OK] {req.get_method()} {path} -> {res.status}: ts={parsed.get('ts')}, error={parsed.get('error')}, result={list(parsed.get('result', {}).keys()) if isinstance(parsed.get('result'), dict) else type(parsed.get('result'))}")
    except Exception as e:
        print(f"[FAIL] {path}: {e}")
