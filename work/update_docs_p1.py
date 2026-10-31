from pathlib import Path
root = Path(r".")
spec = root / "spec" / "quest_protocol.md"
ledger = root / "LEDGER.md"
state = root / "STATE.md"
fidelity = root / "FIDELITY.md"
openq = root / "OPEN_QUESTIONS.md"
cov = root / "COVERAGE_WIKI.md"

spec_add = r'''

## 2k. A6: жизненный цикл квеста (статика)

| Шаг | Запрос/ответ | Что читает клиент | Статус |
|---|---|---|---|
| begin | `POST /quests/quest-begin/{qid}` body `tm0..tm3` | `activeQuests[qid].teamData` -> `BCGManager.UpdateUserData`; `team` | [RUN] |
| detail | `POST /quests/quest-detail/{qid}` | `map`, `builder.summary.bossTable`, `scaledBossTable`, `tiles` | [RUN] |
| move | `POST /quests/quest-movedir/{qid}/{x}/{y}` body `{}` | `results[]` `QuestActionResult`; `progression`; `localPlayer` | [RUN] |
| quit | `POST /quests/quest-quit/{qid}` | expected progression/result; not reached | [ASSUMED] |
| battle action | `results[].action.battle` | `x`,`y`,`isFinalBoss`,`battleEnemy`,`battleTower`; opens prefight | [RUN] |
| activate | `/matches/activate-match/{matchType}` | `QuestsMatchData`, `FighterData`; not reached | [ASSUMED] |

Action table (from `QuestActionResult..ctor` `0xEA28BC`): `moveto`=1,
`teleport`=2, `battle`=3, `ambush`=4, `battlecomplete`=5, `fightlost`=6,
`questcomplete`=7, `chaptercomplete`=8, `actcomplete`=9,
`barrierBlocked`=10, `outOfEnergy`=11. For non-`battle` actions only the
type is proven; their field keys and client reactions are not yet observed.
`battlecomplete`/`fightlost`/`questcomplete`/`chaptercomplete`/`actcomplete`
are the post-match progression actions; they should be emitted in the movedir
or match-resolve result after a fight, but no fight completed. [STATIC]
'''

if "## 2k." not in spec.read_text(encoding="utf-8"):
    spec.write_text(spec.read_text(encoding="utf-8") + spec_add, encoding="utf-8")

ledger_add = r'''

### 14. P1 W1–W6 / C2–C5 / P2 I2 (2026-10-23)

- W1: synergy parser fixed; **40/44** bots, matrix regenerated. [WIKI]
- W2: `notes/wiki_unity_tutorial.md`; page revid 10747, 2023-01-14; APK
  `assets/assetpack` verified. UABE not installed. [WIKI]+[CLIENT]
- W3: `data/wiki/topics/*.json` (13 topics) with as_of_2023/latest and
  curated page sets; no invented values. [WIKI]
- W4: `data/wiki/client_only.json`: 13 client-only non-Sharkticon, 7
  Sharkticon variants, 5 wiki-only pages. [CLIENT]+[WIKI]
- W6: `archive/INTEGRITY.md`; 5154/5154 manifest verified after correcting
  5 stale hashes; 209 errors all 403; new zip
  `TFTF_wiki_archive_2026-10-23_210335.zip`, sha256 `0731484c...`.
- C2: `spec/rating_formula.md`; entry `0xA4814C`, weights
  `heroRatingAttackWeight`/`heroRatingMaxHPWeight`, formula partial. [STATIC]
- C3: `server/data/tuning_client_defaults.json` with only four verified
  defaults; rest intentionally absent.
- C4: `data/wiki/ability_localization_client.json`; only 8 `D_STAT` keys
  found by the current extractor — blocked, see OPEN_QUESTIONS.
- C5: `server/data/bot_catalog_real.json`, 59 packs, class/faction for 59,
  stars for 39; missing values empty with reasons.
- I2: `docs/persistence_design.md` (design only).
'''

with ledger.open("a", encoding="utf-8") as f:
    f.write(ledger_add)

with state.open("a", encoding="utf-8") as f:
    f.write("\n\n## 13. P1/P2 data and docs (2026-10-23)\n"
            "- W1 synergy 40/44; W3 topics in `data/wiki/topics/`;\n"
            "  W4 `data/wiki/client_only.json`; W6 `archive/INTEGRITY.md`.\n"
            "- C2 `spec/rating_formula.md`; C3 four verified tuning defaults;\n"
            "  C4 only 8 D_STAT keys found; C5 `server/data/bot_catalog_real.json`.\n"
            "- C1 OpenAPI remains partial; C4 full localization blocked.\n")

with fidelity.open("a", encoding="utf-8") as f:
    f.write("\n**2026-10-23, wiki/data:** synergy 40/44; 13 topic files with\n"
            "as_of/latest; client-only map 13+7+5; manifest 5154/5154 verified\n"
            "after 5 stale-hash corrections; C5 catalog 59 packs; C2 formula partial.\n")

with openq.open("a", encoding="utf-8") as f:
    f.write("\n- C1: OpenAPI quest endpoints still `[NOT OBSERVED]`; depth for\n"
            "  login/tuning/gacha/shop/etc. is partial. [STATIC]\n"
            "- C3: full TuningManager key/default scan not done; only four defaults\n"
            "  verified in `server/data/tuning_client_defaults.json`.\n"
            "- C4: only 8 `D_STAT` keys found by the JSON-object extractor; full\n"
            "  ability localization needs another text-asset extraction path.\n"
            "- C2: rating pseudocode partial; need runtime `BCGAttributeData` dump.\n"
            "- W3: topic files are curated page sets, not complete numeric tables for\n"
            "  every event/relic/crystal chance; values missing where not in wikitext.\n")

cov_add = r'''

## Structured topic sets (W3)

`data/wiki/topics/` — curated page sets with separate `as_of_2023` and
`latest` records and source URLs:

- `missions_story.json` (11 pages + story/netflix/special-mission headings)
- `events.json` (7 pages + special-mission headings)
- `arena.json` (2), `raids.json` (4), `away.json` (3), `mods.json` (2),
  `relics.json` (14), `crystals.json` (2), `currencies.json` (6),
  `forge.json` (7), `progression.json` (3), `class_triangle.json` (5),
  `status_effects.json` (8).

These are page-level structured records, not yet a complete numeric economy
table; fields absent from the saved wikitext stay absent. [WIKI]

## Client-only / wiki-only (W4)

`data/wiki/client_only.json`: 13 client packs without a parsed wiki stat page,
7 Sharkticon variants, and 5 wiki-only pages (Chromia, Dead End, Optimus Prime,
Soundblaster/Tactician, Starscream). [CLIENT]+[WIKI]
'''
with cov.open("a", encoding="utf-8") as f:
    f.write(cov_add)
print("docs updated")
