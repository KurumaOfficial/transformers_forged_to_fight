import hashlib, os, zipfile, sys
from datetime import datetime, timezone
from pathlib import Path
root = Path(r".")
src = root / "archive" / "wiki"
stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
out = root / "archive" / f"TFTF_wiki_archive_{stamp}.zip"
files = []
for dp, dn, fs in os.walk(src):
    dn[:] = [d for d in dn if d != "__pycache__"]
    for f in fs:
        if f.endswith((".log", ".err", ".zip")):
            continue
        p = Path(dp) / f
        files.append(p)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in files:
        z.write(p, p.relative_to(root))
h = hashlib.sha256(out.read_bytes()).hexdigest()
print(out)
print(out.stat().st_size)
print(h)
