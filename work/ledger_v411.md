
## 2026-10-30 v4.11

| Пункт | Результат | Метка |
|---|---|---|
| `bcg-combat` | `armor_break/mana_gain/critTime` = 200/300/111 | `[RUN]` |
| Tuning live | 242 поля, 95 zero/empty; только bcg-combat server-controllable | `[STATIC]`/`[RUN]` |
| Post-battle | `battlecomplete` → VICTORY screen; награды/клетка/22% не применились | `[RUN]` |
| Level | `/levelrewards/fetch` запрошен после `sync`; `Level=0`, `_loginData` пуст | `[RUN]` |
| Wiki stats | Bumblebee 1066/97, Sideswipe 5160/520, Windblade 5160/498/1381 | `[RUN]`/`[WIKI]` |
| Starscream | найден в `characters/toc.txt`/bundle; патч каталога; UI не показан | `[STATIC]`/`[RUN]` |
| Abilities | Evade/Shield/Bleed нет в stat enum; Buff/trigger schema не декодирована | `[STATIC]` |
| BOTS sweep | 59/59 недействителен: horizontal swipe повторяет page 0 | `[RUN]` |
| FINAL | `report/FINAL_2026-10-30.md` (v4.11) | — |
