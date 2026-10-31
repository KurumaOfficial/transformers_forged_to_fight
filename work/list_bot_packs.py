import os, json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
root = r".\work\unpacked\assets"
bots = []
for n in os.listdir(root):
    p = os.path.join(root, n, "toc.txt")
    if not os.path.isfile(p):
        continue
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        continue
    bundles = d.get("bundles", {})
    if any("characters/merged" in str(v.get("paths", {})) for v in bundles.values()):
        bots.append(n)
print(len(bots))
print(bots)
