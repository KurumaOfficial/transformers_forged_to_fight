import os, sys, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
root = r".\work\unpacked\assets"
patterns = [b"scaledBossTable", b"bossTableId", b"isFinalBoss", b"entityType", b"aiType"]
hits = {}
count = 0
for dirpath, dirnames, filenames in os.walk(root):
    for fn in filenames:
        p = os.path.join(dirpath, fn)
        try:
            sz = os.path.getsize(p)
        except OSError:
            continue
        if sz > 200 * 1024 * 1024:
            continue
        try:
            with open(p, "rb") as f:
                data = f.read()
        except OSError:
            continue
        count += 1
        found = [pat.decode() for pat in patterns if pat in data]
        if found:
            hits[p] = found
print("scanned", count, "files; hits", len(hits))
for p, f in sorted(hits.items()):
    print(p, f)
