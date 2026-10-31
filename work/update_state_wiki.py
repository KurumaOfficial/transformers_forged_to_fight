import json, os, sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"."
W = os.path.join(ROOT, "archive", "wiki")
state = json.load(open(os.path.join(W, "state.json"), encoding="utf-8"))
manifest = json.load(open(os.path.join(W, "manifest.json"), encoding="utf-8"))
errors = json.load(open(os.path.join(W, "errors.json"), encoding="utf-8"))
fandom = sum(1 for k in state["pages"] if k.startswith("fandom|"))
tf = sum(1 for k in state["pages"] if k.startswith("tfwiki|"))
files = len(state.get("files", {}))
sec = f'''## 4b. Wiki archive (Part B, 2026-10-23)

- Fandom: **3613** pages enumerated in 35 namespaces; **{fandom}** saved with
  full revision history + rendered HTML ({len(manifest)} manifest entries).
  allredirects=20, allcategories=80, allimages=2752.
- TFWiki mirror: **{tf}** FTF pages saved (full history + HTML), selected by
  search; whole wiki reports 139066 pages but only FTF titles were taken.
- Image binaries downloaded: **{files}** of 2752; remaining URLs are in
  `archive/wiki/meta/allimages_fandom.json`, state is resumable.
- Extensions: Fandom Scribunto=yes, Cargo=no; TFWiki Scribunto=no, Cargo=no.
  Fandom `Module:` (ns 828) has 0 pages.
- Raw: `archive/wiki/raw/` (not in git, large); lists: `archive/wiki/meta/`;
  state: `archive/wiki/state.json`; manifest: `archive/wiki/manifest.json`;
  errors: `archive/wiki/errors.json` ({len(errors)} entries, mostly HTTP 403
  from static.wikia.nocookie.net; retry with browser UA/Referer works).
- Parsing: **0 pages** parsed into `data/wiki/`; raw only. Every saved page is
  listed in `archive/wiki/unparsed/pages.json` with the reason. No invented
  values; hidden base stats (crit/armor/block) are not claimed.
- Author collection link: `https://1drv.ms/u/s!ApD2f3dIXZ_7yjf4KMB9YQzgWQCG?e=jiLxKN`
  from `User:KRBrickBot` revid 10874, see `OPEN_QUESTIONS.md`.
- Coverage report: `COVERAGE_WIKI.md`.

'''
p = os.path.join(ROOT, "STATE.md")
s = open(p, encoding="utf-8").read()
start = s.find("## 4b. Wiki archive")
if start != -1:
    end = s.find("## 5.", start)
    s = s[:start] + sec + s[end:]
else:
    i = s.index("## 5.")
    s = s[:i] + sec + s[i:]
open(p, "w", encoding="utf-8").write(s)
print("updated STATE with", fandom, tf, files)
