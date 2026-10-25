import subprocess
import re
import collections

out = subprocess.run(["git", "rev-list", "--objects", "--all"], capture_output=True, text=True, errors="replace").stdout
objs = {}
for line in out.splitlines():
    p = line.split(" ", 1)
    if len(p) == 2:
        objs[p[1]] = p[0]

pats = {
    "win_path": re.compile(r"[A-Za-z]:\\Users\\[^\\\s\"']+", re.I),
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "password": re.compile(r"password|passwd|secret|api[_-]?key|BEGIN (RSA|OPENSSH|PRIVATE)", re.I),
    "token": re.compile(r"stoken|bearer|authorization|session_token", re.I),
}
hits = collections.defaultdict(list)
for path, oid in objs.items():
    try:
        b = subprocess.run(["git", "cat-file", "-p", oid], capture_output=True, timeout=10).stdout
    except Exception:
        continue
    s = b.decode("utf-8", "ignore")
    for k, p in pats.items():
        m = p.search(s)
        if m:
            hits[k].append((path, m.group(0)[:100]))

for k, v in hits.items():
    print(k, len(v))
    for x in v[:15]:
        print("  ", x)
