import json, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"."
W = os.path.join(ROOT, "archive", "wiki")
s = json.load(open(os.path.join(W, "state.json"), encoding="utf-8"))
m = json.load(open(os.path.join(W, "manifest.json"), encoding="utf-8"))
e = json.load(open(os.path.join(W, "errors.json"), encoding="utf-8"))
sec = f'''## 4b. Wiki archive (Part B, 2026-10-23)

- Fandom: **3613** pages = **817 non-File + 2796 File**. All **817
  non-File** saved with full history + HTML; 5 File too; all **2796 File
  descriptions** saved (latest revision). [DERIVED] confirmed.
- TFWiki: **8** FTF pages full history + HTML.
- Images: **{len(s["files"])}/2752**; **{len(e)}** errors (mostly 403,
  no bypass). Manifest **{len(m)}** entries; state resumable.
- Parsed: **44 bots** + **252 pages**; quality matrix
  `data/wiki/bot_matrix.json`; ID map `data/wiki/id_map.json` (59 client
  packs = 52 + 7 Sharkticon; 44 wiki stat pages); version sets
  `data/wiki/versions.json` (cutoff 2023-01-13; 96 changed, 11 created
  after).
- Unparsed: `data/wiki/unparsed/pages.json`.
- OneDrive author link auth-gated; not downloaded.

'''
p = os.path.join(ROOT, "STATE.md")
t = open(p, encoding="utf-8").read()
start = t.find("## 4b. Wiki archive")
end = t.find("## 5.", start)
t = t[:start] + sec + t[end:]
open(p, "w", encoding="utf-8").write(t)
print("ok", len(s["files"]), len(e), len(m))
