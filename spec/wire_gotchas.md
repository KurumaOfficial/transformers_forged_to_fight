# Wire gotchas — BCG roster, quest map, async

Сводная таблица находок 2026-10-22. Все RVAs — из `work/il2cpp_dump/dump.cs`
(ARM64 `libil2cpp.so`). Схема подтверждена запуском, если указано [RUN].

| # | Ключ / место | Что оказалось | Источник | RVA |
|---|---|---|---|---|
| 1 | `/bcg/getLoginData.result.userData` | Не плоский блок, а обёртка `{userData:{blueprintsMax,teamSizeMax,teamCountMax}, updates:{heroes,savedTeams,activeTeams,inventory}, deletes:{}}`. Плоский блок игнорируется. | [CLIENT]+[RUN] | `OnBCGData 0x168C7C4`, `UpdateUserData 0x1695AA8` |
| 2 | `updates.heroes[]` -> `entity_type` | Должно быть `"bot"`, не `"hero"`: `BCGHelper.GetHeroes` читает `entities["bot"]`. | [CLIENT]+[RUN] | `HandleUserDataUpdates 0x1695CC0`, `GetEntities 0xC210D4` |
| 3 | `updates.savedTeams` / `updates.activeTeams` | **Массивы**, не словари. `activeTeams[]` = `{aid,type,modes,expire,heroes:{bid:details}}`; `savedTeams[]` = `{sid,heroes:[details]}`. | [CLIENT]+[RUN] | `HandleUserDataUpdates 0x1695CC0`, `BCGUserActiveTeam..ctor 0xA610F0`, `BCGUserSavedTeam..ctor 0xA635C4` |
| 4 | Каталог `blueprints` | Id blueprint читается из ключа **`id`**, не `blueprint`; иначе `HeroData.CreateForDisplay ... does not exist in BCG data`. Ранг героя тоже требует `id` + `rank`. | [CLIENT]+[RUN] | `BCGBlueprintBase..ctor 0xC15708`, `BCGHeroBaseCommon..ctor 0xC21EA0` |
| 5 | `featuredhero` | Должен лежать в **`/account/data`** (не только в `/auth/login`): `{cdn,orderType,heroes:[{id,gacha,...,images3}]}`. Иначе BOTS падает в `SetFeaturedHeroData`. | [CLIENT]+[RUN] | `FeaturedHeroManager.Connect 0xB565B4`, `SetFeaturedHeroData 0xC59748` |
| 6 | `/bcg/getBaseHeroData` | Ответ — **JSON-массив** `BCGHeroDetails`, не `{}`. Запрос: `{heroes:[{bid,rank,level,sig_lvl,flvl}],api,nonce}`. | [CLIENT]+[RUN] | `BCGAPI.GetHeroBaseAttributes 0xC120F4`, `BCGHeroDetails..ctor 0xA5AA14` |
| 7 | `/bcg/setSavedTeam` | Запрос `{teamID,heroes[]}`; ответ — полный BCG-каталог + обёртка userData. `{}`/плоский userData откатывают команду. | [CLIENT]+[RUN] | `BCGAPI.SetSavedTeam 0xC133A0` |
| 8 | `/quests/quest-begin/{qid}` | Ответ — `{activeQuests:{qid:{...,teamData}}}`; `teamData` — та же обёртка BCG userData. Запрос содержит `tm0..tm3`. | [CLIENT]+[RUN] | `QuestsManager.BeginQuest callback 0xCDD210` |
| 9 | Карта активного квеста | `grid` — квадратная `gridDimension × gridDimension`; 3×1 при `gridDimension:3` даёт `ArgumentOutOfRangeException`. Выдуманные `entities` дают NRE. | [CLIENT]+[RUN] | `Map.Deserialize 0x14837EC`, `MapTile.Deserialize 0x1484C04` |
| 10 | `/quests/quest-movedir/{qid}/{dx}/{dy}` | Ход фиксируется результатом **`{"action":"moveto","moveto":{"x":..,"y":..}}`**; `progression.currentPos`/`cleared` обновляют карту. `actionType:1` и `actionPos` игнорируются. | [CLIENT]+[RUN] | `QuestActionResult..ctor 0xEA28BC`, `ActiveQuest.AddActionResultsAndUpdateProgression 0xC3A278` |
| 11 | Sparx `async` | Каждое сообщение: `{component:"quests", message:"avx-update"/"sync"/..., payload:{...}, id, channel}`. `QuestsManager.Async` (`RVA 0xD65038`) диспетчеризует по `message`. Для `avx-update` — `AvxQuestsSync.OnAsyncUpdate`. | [CLIENT] | `HttpEndPoint.OnComplete 0xFC024C`, `PushManager.HandleMessage 0x12FE17C`, `QuestsManager.Async 0xD65038` |
| 12 | Очередь хода | `BeginPendingProgression` +1 к `pendingProgressionCount` (`+0xC8`), `EndPendingProgression` -1; при 0 вызывает `ProcessPendingUpdates` (`0xC3A820`) по очереди `pendingUpdates` (`+0xD0`). | [CLIENT] | `Begin 0xC3A6A4`, `End 0xC3A6B4`, `Process 0xC3A820` |
| 13 | Боевой вход | `ActiveQuest.ActivateMatch` (`0x10A0038`) требует `battleId` и героя; вызывает `MatchManager.ActivateMatch<QuestsMatchData>`, который шлёт `/matches/activate-match`. Триггер — battle-тайл/действие, не обычный ход. | [CLIENT] | `ActiveQuest.ActivateMatch 0x10A0038` |

## Практический вывод

- Ростер: обёртка userData + `entity_type:"bot"` + массивы команд + `id` в каталоге.
- Карта: квадратная сетка, без выдуманных entities.
- Ход: `action:"moveto"`, `moveto:{x,y}` + `progression`.
- Бой: нужен battle-action/entity или `currentBattleId`; обычный `moveto` его не запускает.
