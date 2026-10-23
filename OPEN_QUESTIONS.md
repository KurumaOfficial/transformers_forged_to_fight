# OPEN QUESTIONS

## 1. Коллекция автора (изображения и файлы игры)

Ссылка:

**https://1drv.ms/u/s!ApD2f3dIXZ_7yjf4KMB9YQzgWQCG?e=jiLxKN**

Источник: `User:KRBrickBot`, Fandom, revid `10874`
(https://transformers-forged-to-fight.fandom.com/wiki/User:KRBrickBot),
сохранено в `archive/wiki/meta/author_collection.json`.

OneDrive отдаёт `isAuthenticated:false` и не содержит `downloadUrl` без
входа. Скачивание **не выполнено**: нужен вход/архив от владельца.
Ссылка не является частью вики и не входит в zip.

## 2. Боевой тайл / префайт

- `battle`-действие — правильный триггер: клиент открыл префайт
  «SELECT YOUR BOT». [RUN] `work/battle3.png`, `work/pre2.png`.
- `localPlayer.team` в памяти — `List` с count 0 даже после словаря
  `team`; «+»/FIGHT падает в
  `PrefightScreenPresentation.GetNewScale(HeroData robot)`.
  `/matches/activate-match` не вызван.
- Неизвестен точный формат `team`/`QuestUserHero`: какие ключи и
  контейнер ожидает `QuestUserInfo` (`0x103D5D8`, `0x103CC70`), почему
  `List` остаётся пустым.
- `ActiveQuest.ActivateMatch` (`0x10A0038`) не имеет прямых BL; вызов
  через UI/делегат, требует непустые `battleId` и `hero`.
- Не проверена небоевая сущность отдельным запуском; фабрика разобрана.

## 3. Вики-архив

- Fandom: 3613 страниц = 817 non-File + 2796 File. **Все 817 не-File
  сохранены** с полной историей и HTML; 5 File — тоже; для всех 2796
  File сохранены описания (последняя ревизия). Это подтверждает
  [DERIVED]-гипотезу.
- TFWiki: 8 FTF-страниц с полной историей/HTML.
- Cargo нет; Scribunto на Fandom есть, `Module:` (ns 828) — 0.
- Картинки: 523/2752; приоритет — карты, миссии, интерфейс, таблицы.
  Осталось 2229 (портреты/иконки в последнюю очередь). 24 ошибки,
  в основном 403 static.wikia.nocookie.net; без обхода блокировок.
- Разбор: 44 бота (`data/wiki/bots.json`) + 252 страницы
  (`data/wiki/pages.json`), с page/revid/url и `[WIKI]`.
  `Sharkticon` и layout-страница — в `data/wiki/unparsed/pages.json`.
- Скрытые базовые статы (крит, броня, блок) во многих вики-таблицах
  отсутствуют; не выдумывать.

## 4. Атрибуция

Сохранять URL/revid каждой страницы (есть в raw и manifest), CC BY-SA
3.0 для TFWiki; Fandom — условия сайта. Архив только для личного
использования.
