import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = r".\LEDGER.md"
s = open(p, encoding="utf-8").read()
start = s.find("## 12. Wiki archive")
new = '''## 12. Wiki archive (Part B, 2026-10-23)

- Fandom: **3613** страниц = **817 non-File + 2796 File**. Все **817
  non-File** сохранены с полной историей + HTML; 5 File тоже; все
  **2796 File-описаний** сохранены (последняя ревизия). [DERIVED]
  подтверждена. [RUN]
- TFWiki: **8** FTF-страниц с полной историей + HTML.
- Картинки: **694/2752**; **209** ошибок (в основном 403, без обхода).
  Manifest **5154** записи; state продолжается.
- Разбор: **44 бота** + **252 страницы**. Матрица качества
  `data/wiki/bot_matrix.json`: 43 — star HP/Attack, 38 — rank/level
  tables, 38 — abilities, 37 — ability rank tables, 40 — signature,
  39 — signature tables, 41 — special attacks, 1 — synergy.
- ID map `data/wiki/id_map.json`: 59 client packs = 52 bot packs + 7
  Sharkticon variants; 44 wiki stat pages; 5 wiki-only (Chromia, Dead End,
  Optimus Prime, Soundblaster/Tactician, Starscream). [CLIENT]+[WIKI]
- Версии `data/wiki/versions.json` + `versions/`: cutoff
  `2023-01-13T23:59:59Z`; 296 страниц; 96 изменённых; 11 созданных после
  cutoff (включая Netflix-страницы). as_of и latest лежат отдельно.
- OneDrive автора `isAuthenticated:false`; не скачивался.
- Отчёт: `COVERAGE_WIKI.md`, вопросы: `OPEN_QUESTIONS.md`.
'''
s = s[:start] + new
open(p, "w", encoding="utf-8").write(s)
print("ok")
