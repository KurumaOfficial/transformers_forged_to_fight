import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = r".\LEDGER.md"
s = open(p, encoding="utf-8").read()
start = s.find("## 12. Wiki archive")
new = '''## 12. Wiki archive (Part B, 2026-10-23)

- Fandom: перечислено **3613** страниц = **817 non-File + 2796 File**.
  Все **817 non-File** сохранены с полной историей ревизий и HTML; ещё 5
  File-страниц — тоже. Все **2796 File-описаний** сохранены (последняя
  ревизия). Это подтверждает [DERIVED]: разница 3613−822 — это File и
  картинки, а не пропущенные текстовые страницы. [RUN]
- TFWiki: сохранено **8** FTF-страниц с полной историей + HTML.
- Файлы: **523/2752** бинарников (карты/миссии/UI/таблицы в приоритете);
  24 ошибки, в основном 403 static.wikia.nocookie.net; без обхода.
- Manifest: **4983** записи; state: `archive/wiki/state.json`.
- Cargo нет; Scribunto на Fandom есть, `Module:` (ns 828) — 0.
- Разбор: **44 бота** (`data/wiki/bots.json`) и **252 страницы**
  (`data/wiki/pages.json`), каждая с page/revid/url/[WIKI]; 2 страницы
  в `data/wiki/unparsed/pages.json`. Скрытые статы не выдумывались.
- OneDrive автора: `isAuthenticated:false`, скачивание не выполнено.
- Отчёт: `COVERAGE_WIKI.md`, вопросы: `OPEN_QUESTIONS.md`.
'''
s = s[:start] + new
open(p, "w", encoding="utf-8").write(s)
print("ok")
