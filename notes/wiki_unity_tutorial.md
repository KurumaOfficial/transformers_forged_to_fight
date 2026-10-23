# W2 — заметки по странице «Getting Started With the Game's Unity Files and Assets»

Источник: Fandom, страница `Tutorial/Getting Started With the Game's Unity Files and
Assets`, revid **10747**, timestamp **2023-01-14T03:49:12Z** [WIKI]. Это на день
позже выбранного cutoff для «as_of_2023», поэтому страница относится к latest,
а не к as_of_2023.

## Что говорит страница (пересказ, без копирования)

Страница объясняет, что установочный APK — это, по сути, zip-контейнер с
Unity-ассетами, и что после закрытия онлайн-серверов эти файлы остаются
пригодными для изучения моделей, карт, модулей, реликвий и боевых сцен.
Предлагаемый маршрут:

1. Взять APK из открытого APK-каталога (автор рекомендует uptodown; это
   сторонний сайт, мы его не скачивали и не используем как источник истины).
2. Переименовать расширение `.apk` в `.zip` и распаковать.
3. Открыть каталог `assets/assetpack/`; в версии 9.2 он находится в
   `assets/default/assetpack` (в нашей распаковке — `assets/assetpack`).
4. Использовать **Unity Asset Bundle Extractor (UABE)** из GitHub
   `SeriousCache/UABE/releases`, открыть `.assetbundle` из `*_odr`-каталога.
5. В UABE раскрыть компоненты и смотреть `File ID #2`; экспортировать
   `Mesh` (obj/dae), `AudioClip` (wav), `Texture2D` (png/tga) через Plugins.
6. Для сборки сцен/анимаций нужен опыт Unity; автор упоминает Blender,
   стандартный 3D Viewer Windows и видео-гайд на YouTube
   (`watch?v=4sagYiG2ibo`).

## Что проверяемо на нашем APK 9.2.0

- `work/unpacked/assets/assetpack/` существует и содержит каталоги
  `arcee_gs_deluxe2014_odr`, `bumblebee_cin_dotm_odr`,
  `assets_quest_odr`, `questboard_odr`, `ui`, `primordial_odr` и др. [CLIENT]
- `assets/assetpack` — это именно каталог ассетов, отдельно от
  `assets/assets_*_odr` и `assets/characters`; в нашей распаковке
  `assetpack` и `*_odr` соседствуют. [CLIENT]
- `bumblebee_cin_dotm_odr` соответствует клиентскому `bumblebee_cin_dotm`
  из `data/wiki/id_map.json`; это подтверждает, что имена `*_odr` —
  полезный мостик к каталогу ботов. [CLIENT]+[DERIVED]

## Ограничения и что не делали

- UABE не устанавливали и не запускали: установка нового ПО/инструментов
  требует отдельного согласия. Страница полезна как карта данных, но не
  является доказательством формата ответов сервера.
- Сторонний APK-сайт и YouTube не скачивались; ссылки зафиксированы как
  указатели, не как источник данных.
- Для протокола важнее не artwork, а имена/структуры `TFBCGCharacterData` и
  `BCGAttributeDataBase`; их смотрели статически по `dump.cs`, а не через UABE.
