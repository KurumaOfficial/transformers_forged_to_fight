# Stage 2B — вертикальный срез квеста (промежуточный результат)

Дата: 2026-10-21. Статус: **не завершён**. Дошли до экрана деталей квеста;
бой не запущен, потому что ростер пуст.

## 1. Что подтверждено `[RUN]`

Последовательность (сокращённо, полный лог — `server/requests.jsonl`):

```text
GET  /quests/quest-list                  -> сет Story
GET  /quests/quest-active
GET  /quests/quest-progression
...
POST /quests/quest-detail/story_act1_ch1_m1
     body: {"hash":"v1","nonce":"...","api":11,"setId":"story_act_1"}
```

UI:
- HomeFlow (3D-база) — `work/FINAL_hub.png`
- FIGHT → STORY → ACT 1 → Chapter 1: Arrival → тайл «1.1 Landing Site» —
  `work/FINAL_story_chapters.png`
- экран деталей квеста: «1.1 LANDING SITE», `TOTAL 0 / RECOMMENDED 100-200`,
  кнопки `EDIT SQUAD`, `START` (серая) — `work/stage2_quest_select.png`
- `EDIT SQUAD` с пустыми слотами — `work/stage2_addbot.png`

## 2. Ключевое открытие протокола

Клиент строит дерево `Act[act].Chapters[chapter].Quests[mission]` из полей
сводки `act`, `chapter`, `mission`, а **не** из `actIndex`, `chapterIndex`,
`missionIndex`. После замены ключей глава и тайл квеста появились. `[RUN]`

`chapterCount` — массив с 1-based индексацией: `[0, 1]` = один акт, одна глава.
`[1]` вызывает `ArgumentOutOfRangeException` в `BuildSummaryTable`. `[RUN]`

Подробная схема: `spec/quest_protocol.md`.

## 3. Блокер

`/bcg/getLoginData` отдаёт каталог (`heroes`, `blueprints`, `characters`), но
клиент не видит ни одного bot в `EDIT SQUAD`. `/bcg/getUserData` при этом не
запрашивается. Попытка открыть BOTS приводит к:

```text
NullReferenceException
  at HeroesScreen.SetFeaturedHeroData(Boolean state)
  at HeroesScreen.WindowEnter(Boolean isFirstEntry)
```

Причина: не восстановлен точный формат `BCGUserData.heroes` /
`BCGUserHero` (ключи `userData`, `heroes`, `blueprint`, `rank`, `level`,
`attributeData`, ...). Экспериментальный блок `userData` в
`bcg_login_data.json` клиентом не принят. `[RUN]`

## 4. Честная таблица верности среза

| Слой | Что есть | Источник | Оценка |
|---|---|---|---|
| Клиент, UI, 3D-база, экран квестов | Оригинальный APK | — | 1:1 (клиент не менялся) |
| Схема Sparx-конверта | `ts/result/sync/async/error` | [STATIC]+[RUN] | подтверждена |
| Схема quest-list (ключи) | `actCount`, `chapterCount`, `act/chapter/mission` | [STATIC]+[RUN] | подтверждена |
| Содержимое quest-list (акты, главы, карта, награды) | «All Fall Down», «Arrival», «Landing Site», 3x1 | [ASSUMED] | выдумано |
| quest-detail запрос | `{hash,nonce,api,setId}` | [RUN] | подтверждён |
| quest-detail ответ | summary/map | [ASSUMED] | принят клиентом, но не сверен |
| Ростер | пусто | — | не реализовано |
| Бой | не запускался | — | 0 доказательств |

## 5. Следующий шаг (ровно один)

Восстановить `BCGUserHero`/`BCGUserData` и получить одного бота в `EDIT SQUAD`.
Только после этого нажимать `START` и писать `quest-begin` / `activate-match`.
