from pathlib import Path
root = Path(r".")
spec = root / "spec" / "quest_protocol.md"
ledger = root / "LEDGER.md"
state = root / "STATE.md"
fidelity = root / "FIDELITY.md"
openq = root / "OPEN_QUESTIONS.md"

spec_text = r'''

## 2j. A1/A2: откуда префайт берёт команду (2026-10-23)

`PrefightScreenData.GetCurrentTeam` (`0xE3D188`):

1. `_activeQuest = [PrefightScreenData+0x50]` (`ActiveQuest`).
2. `x0 = [ActiveQuest+0x18]` — это **`ActiveQuest.mode`**, не `qid` и не
   `uniqueId`; строка ошибки «Could not get active team for quest id »
   вводит в заблуждение.
3. `BCGHelper.GetActiveTeam` (`0xC1FFDC`) берёт
   `BCGManager.Instance.UserData.activeTeams` (`+0x30` -> `+0x30`),
   делает `TryGetValue(mode)`; при попадании создаёт
   `BCGUserActiveTeam` и `TeamData`.

Поэтому активная команда должна существовать под ключом/`aid` = `mode`
(`story`), а не только под `qid` (`story_act1_ch1_m1`) или `uniqueId`
(`active_quest_1001`). В `server/data/bcg_login_data.json` добавлен
клон с `aid:"story"`; в movedir/quest-begin также отправляются клоны.
Это не сделало префайт непустым: `TeamData`/`TeamHeroes` всё ещё не
даёт героя. [RUN] `work/mode_team.png`, `work/mode_team2.png`.

`QuestUserInfo` (`0x103D5D8`): поле `team` — `List<QuestUserHero>`
(`+0x68`), но JSON-источник разбирается через `Dot.Object` и
`QuestUserHero..ctor` (`0x103CC70`), то есть на входе ожидается
**словарь**. `currentBattleId` читается как строка (`+0x38`),
`matchResult` — `+0x58`, `currentBattleState` — `+0x40`.
В server/data/quest_begin_response.json `team` переведён из массива в
словарь `bid -> {hp,pi,sig_lvl,stat_mods,sig_mods}`; в памяти
`localPlayer.team` всё ещё count 0. [RUN]
`work/read_prefight_state.py`.

Вывод: префайт и map-marker используют разные представления команды;
блокер prefight — не `QuestUserInfo.team`, а `BCGUserActiveTeam`/
`TeamData.RefreshHeroData` либо id, которым `GetActiveTeam` ищет mode.
'''

ledger_text = r'''

### 12.1 P0 A1/A2 + S1/S2 (2026-10-23, [RUN])

- `PrefightScreenData.GetCurrentTeam`: `_activeQuest+0x50` ->
  `ActiveQuest.mode+0x18` -> `BCGHelper.GetActiveTeam` (`0xC1FFDC`);
  lookup идёт по `BCGManager.UserData.activeTeams` с ключом **mode**
  (`story`). `qid`/`uniqueId` — не тот ключ.
- Добавлены mode-клоны `aid:"story"`/`"Story"` в login/quest-begin/
  movedir. Префайт всё равно пуст, NRE `GetNewScale`, `/matches` не
  вызван. [RUN] `work/mode_team.png`, `mode_team2.png`.
- `QuestUserInfo.team` — внутренний `List<QuestUserHero>` (+0x68);
  JSON-вход разбирается `Dot.Object` -> `QuestUserHero..ctor`
  (`0x103CC70`). Верхнеуровневый `team` quest-begin переведён в
  словарь `bid -> {hp,pi,sig_lvl,stat_mods,sig_mods}`; memory count
  всё ещё 0.
- `work/smoke_test.py`: холодный запуск -> PLAY NOW -> FIGHT -> STORY ->
  квест -> START -> карта -> боевой тайл; PASS, 7 скриншотов,
  `tests/smoke/latest.json`. `activate_match=false`, NRE есть.
- `work/golden_regression.py --record` + check: 9 эталонных запросов
  (`getLoginData`, account, tuning, quest-list/active/progression/
  detail/begin/movedir), PASS. `tests/golden/`.
- [RUN] `npm` не использовался; Frida/gadget/патчи не использовались.
'''

if "## 2j." not in spec.read_text(encoding="utf-8"):
    spec.write_text(spec.read_text(encoding="utf-8") + spec_text, encoding="utf-8")
with ledger.open("a", encoding="utf-8") as f:
    f.write(ledger_text)
with state.open("a", encoding="utf-8") as f:
    f.write("\n\n## 12. Verification / P0 A3, S1, S2 (2026-10-23)\n"
            "- `work/smoke_test.py` — ADB-сценарий с 7 скриншотами; PASS.\n"
            "- `work/golden_regression.py --record` — 9 эталонных запросов;\n"
            "  `--check` PASS, `tests/golden/`.\n"
            "- `PrefightScreenData.GetCurrentTeam` использует\n"
            "  `ActiveQuest.mode`, а не qid/uniqueId; mode-клоны\n"
            "  `aid:\"story\"` добавлены, но prefight пуст.\n"
            "- `QuestUserInfo.team` — List<QuestUserHero>; JSON — dict;\n"
            "  верхнеуровневый team quest-begin переведён в dict.\n"
            "- `/matches/activate-match` по-прежнему не вызван.\n")
with fidelity.open("a", encoding="utf-8") as f:
    f.write("\n**2026-10-23, A1/A2/S1/S2:** `GetCurrentTeam` ищет active team\n"
            "по `ActiveQuest.mode`; mode-клоны добавлены, prefight пуст. `QuestUserInfo.team`\n"
            "внутри List, JSON — dict; верхнеуровневый team переведён в dict. Smoke PASS,\n"
            "golden regression 9/9 PASS; `/matches` не вызван.\n")
with openq.open("a", encoding="utf-8") as f:
    f.write("\n- A2: `QuestUserInfo.team` JSON принят как dict на верхнем уровне,\n"
            "  но memory `localPlayer.team` count 0; точная вложенность (users/localPlayer)\n"
            "  не подтверждена. [RUN]\n"
            "- A5: `/matches/activate-match` не вызван; тела и `FighterInitData`\n"
            "  остаются `[ASSUMED]`.\n"
            "- A3: harness variants не запускался пакетом 10–20; smoke/golden готовы.\n")
print("docs updated")
