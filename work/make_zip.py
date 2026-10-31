import os, zipfile, hashlib, time, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"."
SRC = os.path.join(ROOT, "archive", "wiki")
OUT = os.path.join(ROOT, "archive", "TFTF_wiki_archive_2026-10-23.zip")
files = []
for dp, dn, fs in os.walk(SRC):
    for f in fs:
        p = os.path.join(dp, f)
        if os.path.abspath(p) == os.path.abspath(OUT):
            continue
        files.append(p)
print("files", len(files), flush=True)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for i, p in enumerate(files, 1):
        z.write(p, os.path.relpath(p, ROOT))
        if i % 500 == 0:
            print("zipped", i, flush=True)
h = hashlib.sha256()
with open(OUT, "rb") as f:
    for chunk in iter(lambda: f.read(1024 * 1024), b""):
        h.update(chunk)
print("ZIP", OUT)
print("SIZE", os.path.getsize(OUT))
print("SHA256", h.hexdigest())
