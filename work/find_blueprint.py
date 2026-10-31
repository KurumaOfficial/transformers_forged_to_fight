import os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
root = r".\work\unpacked\assets"
pat = b"bumblebee_cin_dotm_2"
hits = []
for dp, dn, fs in os.walk(root):
    for fn in fs:
        p = os.path.join(dp, fn)
        try:
            if os.path.getsize(p) > 200 * 1024 * 1024:
                continue
            b = open(p, "rb").read()
            if pat in b:
                hits.append(p)
        except OSError:
            pass
print(len(hits))
for h in hits[:20]:
    print(h)
