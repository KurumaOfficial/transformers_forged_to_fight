import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r".\work\string_literals.txt", "r", encoding="utf-8") as f:
    literals = f.readlines()

endpoints = set()
api_pattern = re.compile(r'^\[\d+\]\s*(/[a-zA-Z0-9_\-\./]+)$')

for l in literals:
    m = api_pattern.match(l.strip())
    if m:
        path = m.group(1)
        # filter out file paths like /sdcard or /system
        if not path.startswith(("/proc", "/sys", "/dev", "/system", "/data/local")):
            endpoints.add(path)

print(f"Total API Endpoints found: {len(endpoints)}")
by_service = {}
for ep in sorted(endpoints):
    parts = ep.strip("/").split("/")
    svc = parts[0] if parts else "root"
    by_service.setdefault(svc, []).append(ep)

for svc, eps in sorted(by_service.items()):
    print(f"\nService: {svc} ({len(eps)} routes)")
    for ep in eps:
        print(f"  {ep}")
