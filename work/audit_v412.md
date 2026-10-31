
## 2026-10-30 v4.12 Step 0 corrections

| # | Claim | Status | Evidence |
|---:|---|---|---|
| 57 | Starscream is absent in 9.2.0 | **corrected** | 61-base census: `starscream_gs` + `_lw` in `characters/toc.txt`, `Starscream_GS` in `characters.assetbundle`, `ID_SPECIAL_ATTACK_STARS_GS_0..2`, wiki 5400/391/1354. `[STATIC]` `data/client_character_census.json`, `docs/character_census.md`. |
| 58 | The client has 59 bot packages | **corrected / undercounted** | 59 ODR bundles + 2 merged prefabs (`starscream_gs`, `optimusprime_gs_v`) = **61 base characters**; 122 tokens with `_lw`; 108 TOCs, 102 assetbundles, 93 `_odr` dirs. `[STATIC]` `work/census_raw.json`, `work/bundle_inventory.json`. |
| 59 | BOTS 59/59 is the coverage denominator | **corrected** | 59 is the visible card count, not the catalog size: 61 characters, 60 effective roster, 61 after adding Optimus GS. The sweep denominator must come from the effective catalog/roster, and the report must list seen/missing ids. `[STATIC]` `docs/character_census.md`; `[RUN]` vertical sweep 59 cards. |
| 60 | Post-battle rewards cannot be applied / only result response | **corrected route** | `QuestsManager.Async` (`0xD65038`) lowercases the message, matches **`match-resolved`** (`0xD65338`), reads payload `qid`/`battleId`, calls `QuestProgression.UpdateMatchAttributes` / `UpdateCurrentFightId`, then `ProcessActionResultsAndProgression(quest, payload)` (`0xD65CA8`). The async payload, not the resolve result, carries progression/results/teamData. `[STATIC]` `work/quests_async.txt`, `work/find_async_slots.py`. |
| 61 | Windblade has no special-attack strings | **corrected** | Keys exist under the shortened token **`WINDB_GS`**: `ID_SPECIAL_ATTACK_WINDB_GS_0..2` and descriptions, `ID_CHARACTER_BIOS_WINDB_GS`; portrait `portrait_windb_gs_large.png`; moves `move_windblade_special_01/02`. The full-name key `WINDBLADE` is what the current catalog id produces. `[STATIC]` `work/localization_all.json`, census row `windblade_gs`. |
