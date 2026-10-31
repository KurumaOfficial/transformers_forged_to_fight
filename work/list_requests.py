import json

with open('server/requests.jsonl', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
            m = entry.get("method")
            p = entry.get("path")
            ip = entry.get("client_ip")
            port = entry.get("client_port")
            headers = entry.get("headers", {})
            ua = headers.get("user-agent") or headers.get("User-Agent")
            print(f"#{i+1}: {m} {p} | Client: {ip}:{port} | UA: {ua}")
        except Exception as e:
            print(f"#{i+1}: parse error {e}")
