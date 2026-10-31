import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

unpacked = r".\work\unpacked"

keywords = [b"getBaseHeroData", b"getHeroXPCurve", b"baseHeroData", b"hero_data", b"bot_data", b"xp_curve", b"heroxp"]

found = {}
for root, dirs, files in os.walk(unpacked):
    for f in files:
        fp = os.path.join(root, f)
        if os.path.getsize(fp) < 50*1024*1024:
            try:
                with open(fp, "rb") as fh:
                    content = fh.read()
                for kw in keywords:
                    if kw in content:
                        found.setdefault(kw.decode(), []).append(os.path.relpath(fp, unpacked))
            except:
                pass

print("Keyword search results:")
for kw, flist in found.items():
    print(f"  {kw}: found in {len(flist)} files ({flist[:5]})")
