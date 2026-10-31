import json, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"."
W = os.path.join(ROOT, "archive", "wiki")
s = json.load(open(os.path.join(W, "state.json"), encoding="utf-8"))
m = json.load(open(os.path.join(W, "manifest.json"), encoding="utf-8"))
e = json.load(open(os.path.join(W, "errors.json"), encoding="utf-8"))
files = len(s["files"])
sec = f'''## 4b. Wiki archive (Part B, 2026-10-23)

- Fandom: **3613** pages enumerated = **817 non-File + 2796 File**.
  All **817 non-File** pages saved with full revision history + HTML; 5
  File pages too. All **2796 File descriptions** saved (latest revision)
  in `archive/wiki/raw/fandom/file_descriptions/`. This confirms the
  [DERIVED] hypothesis (the 3613-822 gap is File pages + images).
- TFWiki: **8** FTF pages with full history + HTML.
- Image binaries: **{files}/2752** (maps/missions/UI/tables first); 24
  errors (mostly static.wikia 403, no bypass).
- Manifest: **{len(m)}** entries; state: `archive/wiki/state.json`.
- Extensions: Fandom Scribunto=yes/Cargo=no, `Module:` ns 828 = 0;
  TFWiki Scribunto=no/Cargo=no.
- Parsed: **44 bots** (`data/wiki/bots.json`) + **252 pages**
  (`data/wiki/pages.json`), each with page/revid/url/[WIKI]; 2 content
  pages in `data/wiki/unparsed/pages.json`.
- Author collection link is auth-gated (`isAuthenticated:false`); not
  downloaded. See `OPEN_QUESTIONS.md`.
- Coverage: `COVERAGE_WIKI.md`; raw excludes git, zip backup pending.

'''
p = os.path.join(ROOT, "STATE.md")
text = open(p, encoding="utf-8").read()
start = text.find("## 4b. Wiki archive")
end = text.find("## 5.", start)
text = text[:start] + sec + text[end:]
open(p, "w", encoding="utf-8").write(text)
print("state wiki updated", files, len(m))
