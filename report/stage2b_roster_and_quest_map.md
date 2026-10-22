# Stage 2B — ростер, вход в квест и карта (2026-10-22)

Статус: **частично завершено**. Ростер и вход в квест работают; движение по
карте отправляет запрос, но клиент не фиксирует ход. Бой не начат.

## 1. Что проверено запуском [RUN]

| Шаг | Результат | Доказательство |
|---|---|---|
| Холодный запуск -> PLAY NOW -> хаб | работает | `work/r7.png` |
| BOTS без краша, Bumblebee 100 | работает | `work/r13.png` |
| EDIT SQUAD, TOTAL 100 | работает | `work/r38.png` |
| quest-detail 1.1, START активен | работает | `work/r38.png` |
| `POST /quests/quest-begin/story_act1_ch1_m1` | принят, карта 3×3 загружена | `work/r47.png`, `work/r51.png` |
| `POST /quests/quest-movedir/.../1/0` | запрос уходит | `server/requests.jsonl` 18:22, 18:31, 18:40, 18:46 |
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

`quest-movedir` возвращает `progression` (version 1/2, currentPos, cleared),
`results` с `actionType: 1 (MOVE_TO)`, `actionTile` и `teamData`. Клиент не
двигает бота и не логирует исключение. Похоже, ход фиксируется через
`sync`/`async`-сообщение Sparx, а не только через HTTP `result`
(`BeginPendingProgression`/`EndPendingProgression`).

## 4. Честная верность

- Клиент (APK, ассеты, UI, рендер) — оригинальный.
- Схема ростера, `getBaseHeroData`, `setSavedTeam`, `quest-begin`, карты —
  подтверждена запуском.
- Числовые данные (статы, ранги, ID, карта, награды, уровень/ресурсы) —
  синтетические [ASSUMED].
- Бой — не наблюдался.

## 5. Следующий шаг

Разобрать `ActiveQuest.ProcessPendingUpdates` (`RVA 0xC3A820`) и формат
`sync`/`async` для `movedir`; затем дойти до финального тайла и снять
`/matches/activate-match`, `/matches/match-loaded`, `/matches/resolve-match`.
