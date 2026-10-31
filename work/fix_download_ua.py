from pathlib import Path
p = Path(r".\archive\wiki\archive_wiki.py")
s = p.read_text(encoding="utf-8")
old = '"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36", '
new = '"User-Agent": "TFTF-offline-archive/0.1 (personal preservation; polite; contact: local-user)", '
if old not in s:
    raise SystemExit("UA not found")
s = s.replace(old, new)
p.write_text(s, encoding="utf-8")
print("UA fixed")
