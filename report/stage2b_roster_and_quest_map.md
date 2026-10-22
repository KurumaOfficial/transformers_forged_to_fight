# Stage 2B — ростер, вход в квест и карта (2026-10-22)

Статус: **ростер, вход в квест и ход по карте работают**; бой не начат.
Движение подтверждено: бот перешёл на (1,0), HUD 11% -> 22% EXPLORED.

## 1. Что проверено запуском [RUN]

| Шаг | Результат | Доказательство |
|---|---|---|
| Холодный запуск -> PLAY NOW -> хаб | работает | `work/r7.png` |
| BOTS без краша, Bumblebee 100 | работает | `work/r13.png` |
| EDIT SQUAD, TOTAL 100 | работает | `work/r38.png` |
| quest-detail 1.1, START активен | работает | `work/r38.png` |
| `POST /quests/quest-begin/story_act1_ch1_m1` | принят, карта 3×3 загружена | `work/r47.png`, `work/r51.png` |
| `POST /quests/quest-movedir/.../1/0` | запрос уходит, бот переходит на (1,0), 22% | `work/r75.png`, requests 18:55 |
| `POST /quests/quest-quit/...` | запрос уходит | 18:31 |

## 2. Причины прошлого блокера и исправления

1. **BOTS NRE.** `HeroesScreen.SetFeaturedHeroData` вызывает
   `GameUtil.GetFeaturedHero()` и разыменовывает результат. `FeaturedHeroManager`
   читает `featuredhero` из login data, а фактический источник в этом билде —
   `/account/data`. Добавлен блок `featuredhero` с Optimus.
2. **Пустой ростер.** `/bcg/getLoginData.result.userData` должен быть обёрткой
   `{userData:{...},updates:{heroes,...},deletes:{}}`. Плоский блок игнорируется.
3. **Герой невидим.** `entity_type` должен быть `"bot"`; `BCGHelper.GetHeroes`
   читает `entities["bot"]`.
4. **Команда не сохранялась.** `savedTeams`/`activeTeams` — массивы, не словари.
5. **Каталог не находил blueprint.** Ключ id blueprint — `id`, не `blueprint`.
6. **`getBaseHeroData`.** Ответ — массив `BCGHeroDetails`, а не `{}`.
7. **`setSavedTeam`.** Ответ — полный BCG-каталог + обёртка userData.
8. **`quest-begin`.** Ответ — `{activeQuests:{qid:{...,teamData}}}`.
9. **Карта.** Сетка должна быть квадратной `gridDimension × gridDimension`;
   выдуманные `entities` в тайлах вызывают NRE в `MapTile.Deserialize`.

Подробности: `spec/bcg_userdata.md`, `spec/quest_protocol.md`, `LEDGER.md`.

## 3. Текущий блокер

Ход работает: результат `/quests/quest-movedir` должен содержать
`results:[{"action":"moveto","moveto":{"x":..,"y":..}}]` плюс `progression` и
`teamData`. Варианты с `actionType:1`, `actionPos`, top-level position и
version 1/2 без `moveto` не двигали бота (см. LEDGER).

Бой не запущен. `battle`-действие с минимальным `battleEnemy` не вызвало
`/matches/activate-match`. Нужен валидный battle-tile/entity (`BCGEntity`,
`QuestBoss`) или `progression.currentBattleId`/`currentFightId` + `localPlayer`.
RAIDS отключён клиентом («Raids are temporarily disabled.»), SPECIAL/ARENAS/
ALLIANCE заблокированы по уровню.

## 4. Честная верность

- Клиент (APK, ассеты, UI, рендер) — оригинальный.
- Схема ростера, `getBaseHeroData`, `setSavedTeam`, `quest-begin`, карты и
  `quest-movedir` — подтверждена запуском.
- Числовые данные (статы, ранги, ID, карта, награды, уровень/ресурсы) —
  синтетические [ASSUMED].
- Бой — не наблюдался.

## 5. Следующий шаг

Разобрать `ActiveQuest.ProcessPendingUpdates` (`RVA 0xC3A820`) и формат
`sync`/`async` для `movedir`; затем дойти до финального тайла и снять
`/matches/activate-match`, `/matches/match-loaded`, `/matches/resolve-match`.

## 6. Боевой тайл (2026-10-22)

Статика: `ActiveQuest..ctor` читает `scaledBossTable`; `MapTile.Deserialize`
читает `entityType`, `boss` (bossTableId), `links`, `visibleLinks`, `bg`, `bt`,
`ab`, `sockets`; `QuestBoss.Deserialize` использует ключи
`isFinalBoss,characters,rank,level,sig_lvl,flvl,aiType,aiString,aiPer,...`;
`Entity.Deserialize` — `uid,key,hi`.

Проверено три варианта (boss table + entity; + uid/key/hi/type/baseType;
+ bg/bt/ab/sockets). Все три дают NRE в `MapTile.Deserialize`; `/matches/*`
не вызван. Память после обычного хода: `ActiveQuests=1`,
`pendingProgressionCount=0`, `currentPos=(1,0)`, `currentBattleId=null`.
[RUN] `work/r83.png`, `spec/quest_protocol.md` §2e, `work/adb_legacy_quest.py`.

Дальше — динамическая трассировка `MapTile.Deserialize`/`QuestBoss.Deserialize`
или реальный образец `scaledBossTable`/tile entity.
