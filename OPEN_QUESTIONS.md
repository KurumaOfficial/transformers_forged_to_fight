# OPEN QUESTIONS

## 1. Коллекция автора (изображения и файлы игры)

Найдена ссылка:

**https://1drv.ms/u/s!ApD2f3dIXZ_7yjf4KMB9YQzgWQCG?e=jiLxKN**

Источник: `User:KRBrickBot`, Fandom, revid `10874` (2023-08-08T05:56:36Z),
URL: https://transformers-forged-to-fight.fandom.com/wiki/User:KRBrickBot
(сохранено в `archive/wiki/meta/author_collection.json`).

Связь с главной: главная страница ведёт на
`Tutorial/Getting Started With the Game's Unity Files and Assets`
(та же тема — Unity-ассеты игры). На странице пользователя — внешняя
ссылка на OneDrive. Содержимое OneDrive **не скачивалось**: это внешний
ресурс, не часть вики; нужно отдельное решение по доступу/лицензии.

## 2. Боевой тайл / `/matches/activate-match`

- Точная NRE-ветка найдена: `entities` должен быть `IDictionary`, не массив
  (`MapTile.Deserialize 0x1485094/0x1485098`).
- `currentBattleId + localPlayer` в `progression` **не** вызвали
  `/matches/activate-match` (05:41:47Z, `work/r119.png`).
- Неизвестен точный `battle` action schema: `battleEnemy`/`battleId`/
  `battleTower`/`isFinalBoss` и порядок вызова `ActiveQuest.ActivateMatch`.
  Нужен один новый опыт с `battle` action; без согласия пользователя
  Frida/gadget/патчи клиента не применять.
- Не проверена небоевая сущность (`generator`/`building`) отдельным
  запуском; статически фабрика разобрана (`0xEF28CC`).

## 3. Вики-архив

- Fandom: перечислено 3613 страниц, 2752 изображения, 80 категорий,
  20 редиректов. Сохранено 822 страницы (полные ревизии + HTML) и 118
  бинарников; состояние и продолжение — `archive/wiki/state.json`.
- TFWiki: 139066 страниц всего, но по поиску FTF только 6 тематических;
  сохранено 8 страниц (включая `Crossfire (Prime)`), полная история.
- Cargo нет ни на Fandom, ни на TFWiki. Scribunto на Fandom включён,
  но страниц в `Module:` (ns 828) не найдено (0).
- Файлы Fandom: список `allimages` есть (2752), скачано 118; остальные
  можно продолжить из `state.json` (часть URL отдаёт 403).
- Разбор `data/wiki/*.json` не начат; всё сырое лежит в `archive/wiki/raw/`,
  список неразобранного — `archive/wiki/unparsed/`.
- Скрытые базовые статы (крит, броня, блок) в вики могут отсутствовать;
  выдавать их за подтверждённые нельзя.

## 4. Атрибуция

Для публикации сохранять URL и revid каждой страницы (есть в
`archive/wiki/raw/.../revisions/*.json` и `manifest.json`), CC BY-SA 3.0
для TFWiki; Fandom — условия сайта. Архив только для личного использования.
