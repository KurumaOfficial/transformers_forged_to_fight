from pathlib import Path
p = Path(r".\archive\wiki\archive_wiki.py")
s = p.read_text(encoding="utf-8")
old = 'req = urllib.request.Request(url, headers={"User-Agent": UA})'
new = ('req = urllib.request.Request(url, headers={'
       '"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36", '
       '"Referer": "https://transformers-forged-to-fight.fandom.com/"})')
if old not in s:
    raise SystemExit("old not found")
s = s.replace(old, new)
p.write_text(s, encoding="utf-8")
print("patched")
