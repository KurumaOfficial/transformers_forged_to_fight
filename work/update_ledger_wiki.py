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
sec = f'''

## 12. Wiki archive (Part B, 2026-10-23)

- Fandom: перечислено 3613 страниц (35 пространств), сохранено **{fandom}**
  страниц с полной историей ревизий и HTML; {len(manifest)} записей в
  manifest; 8949 ревизий. allredirects=20, allcategories=80,
  allimages=2752. [RUN]
- TFWiki: сохранено **{tf}** FTF-страниц (полная история + HTML), включая
  `Forged to Fight`, `Transformers: Forged to Fight`, `Crossfire`,
  `Generations`, `Prime Suspect`, `Magnus Opus`. [RUN]
- Файлы: **{files}** из 2752 скачано; остальные URL в
  `archive/wiki/meta/allimages_fandom.json`, state продолжается. [RUN]
- Cargo нет; Scribunto на Fandom есть, но `Module:` (ns 828) — 0 страниц.
- Разбор `data/wiki/`: **0**; всё сырое, список неразобранного —
  `archive/wiki/unparsed/pages.json`. Выдуманных значений нет.
- Ошибки: {len(errors)} (в основном HTTP 403 static.wikia.nocookie.net;
  с browser UA/Referer часть качается).
- Ссылка автора на коллекцию:
  `https://1drv.ms/u/s!ApD2f3dIXZ_7yjf4KMB9YQzgWQCG?e=jiLxKN`
  (`User:KRBrickBot`, revid 10874). Это внешний OneDrive, не скачивался.
- Отчёт: `COVERAGE_WIKI.md`, вопросы: `OPEN_QUESTIONS.md`.
'''
p = os.path.join(ROOT, "LEDGER.md")
s = open(p, encoding="utf-8").read()
start = s.find("## 12. Wiki archive")
if start != -1:
    s = s[:start] + sec
else:
    s = s.rstrip() + "\n" + sec
open(p, "w", encoding="utf-8").write(s)
print("updated LEDGER", fandom, tf, files)
