# BCG userData / roster — verified wire schema

Status: **roster works** in a live run (2026-10-22). BOTS shows the bot and
`EDIT SQUAD` reaches `TOTAL 100`. Values (stats, ranks, ids) are still
[ASSUMED]; the *schema* below is [STATIC] from `dump.cs` plus [RUN].

Evidence:
- `work/r13.png` — BOTS screen with Bumblebee 100 (no crash).
- `work/r38.png` — quest detail with Bumblebee 100, `TOTAL 100`, START active.
- `work/run_logcat_8.txt` — no `HeroesScreen.SetFeaturedHeroData` exception.
- `server/requests.jsonl` 2026-10-22 18:20 — `setSavedTeam`, `quest-begin`.

## 1. Where the client reads it

`BCGManagerBase.OnBCGData` (`RVA 0x168C7C4`) reads top-level `userData` from the
`/bcg/getLoginData` result. `BCGManagerBase.UpdateUserData` (`RVA 0x1695AA8`)
expects this wrapper:

```json
{
  "userData": { "blueprintsMax": 50, "teamSizeMax": 3, "teamCountMax": 3 },
  "updates": {
    "heroes": [ ... ],
    "savedTeams": [ ... ],
    "activeTeams": [ ... ],
    "inventory": { "f": {}, "bp": {}, "max": {} }
  },
  "deletes": {}
}
```

`updates` is passed to `HandleUserDataUpdates` (`RVA 0x1695CC0`). A flat
`userData` block (without the wrapper) is ignored for the roster. [RUN]

## 2. Hero item (`updates.heroes[]`)

`BCGUserHeroBase..ctor` (`RVA 0xA62348`) reads these keys:

| Wire key | Type | Notes |
|---|---|---|
| `entity_type` | string | must be **`bot`** for `BCGHelper.GetHeroes`; `GetEntities("bot")` |
| `bid` | string | blueprint id |
| `rank` | int | |
| `level` | int | |
| `sig_lvl` | int | |
| `required_xp` | int | |
| `max_xp` | int | |
| `stamina` | int | |
| `stamina_ts` | int | |
| `stamina_full_ts` | int | |
| `stt` | string | special team flag |
| `pvpb` | object | |
| `exc` | object | |
| `id` | string | optional; entity id |
| `max_hp`, `attack`, `rating`, `rating_hp`, `rating_attack`, `rating_hp_base`, `rating_attack_base`, `special_attacks` | numbers | optional precomputed attributes |

The client adds the hero to `UserData.heroes[bid]` and
`UserData.entities[entity_type][bid]`. `BCGHelper.GetHeroes` reads
`entities["bot"]`; with `entity_type: "hero"` the bot is invisible. [STATIC]+[RUN]

## 3. Teams

`BCGUserData.savedTeams` and `activeTeams` are **arrays** parsed with
`Dot.Array`; do not send objects keyed by id.

`activeTeams[]` item (`BCGUserActiveTeam..ctor`, `RVA 0xA610F0`):

```json
{"aid":"story_act1_ch1_m1","type":"story","modes":["Story"],"expire":0,
 "heroes":{"bumblebee_cin_dotm_2": { "bid":"...", "rank":1, "level":1, ... }}}
```

`heroes` inside an active team is an **object** keyed by blueprint id.
`savedTeams[]` item (`BCGUserSavedTeam..ctor`, `RVA 0xA635C4`):

```json
{"sid":"0","heroes":[ { "bid":"...", "rank":1, "level":1, ... } ]}
```

## 4. Catalog keys (not userData)

`BCGBlueprintBase..ctor` (`RVA 0xC15708`) reads the blueprint id from key
**`id`**, not `blueprint`. `BCGHeroBaseCommon..ctor` (`RVA 0xC21EA0`) also reads
`id`, plus `rank`, `max_level`, `stamina`. Sending only `blueprint` makes
`BCGHelper.GetBlueprint` fail and produces
`HeroData.CreateForDisplay - blueprint '...' does not exist in BCG data`.

`BCGBlueprintBase` also reads `et` (entity type), `character`, `m`, `r`, `a`,
`t`, `n`, `imgID`, `s3img`, `gachaImgID`, `mdl`, `evo_blueprint`, `map_asset`,
`hero_colour`, `max_rank`, `rarity`, `class`, `attribute_base_type`,
`gachaReveal`, `base_damage`, `base_ranged_damage`, `s1..s3`, `msa`,
`attack_bonus`, `synergy_bonuses`, `tags`, `redeemer_base`. [STATIC]

## 5. `/bcg/getBaseHeroData`

Request (observed):

```json
{"heroes":[{"level":1,"sig_lvl":0,"flvl":0,"rank":5,"bid":"optimus_c_tf_t3"}],
 "nonce":"...","api":6}
```

Response is a **JSON array** of `BCGHeroDetails` dictionaries. Keys read by
`BCGHeroDetails..ctor` (`RVA 0xA5AA14`): `bid`, `rank`, `level`, `sig_lvl`,
`rating_hp`, `max_hp`, `rating_attack`, `attack`, `special_attacks`, `pvpb`,
`synergyBonuses`, `user_owned`. Current values are [ASSUMED]. [CLIENT]+[RUN]

## 6. `/bcg/setSavedTeam`

Request (observed):

```json
{"heroes":["bumblebee_cin_dotm_2"],"api":6,"nonce":"...","teamID":"0"}
```

The client applies the response through the same BCG parser. Return the full
catalog with `userData` set to the wrapper from §1 (and the updated
`updates.savedTeams`). A flat userData or `{}` makes the team revert. [RUN]

## 7. Featured hero (BOTS screen)

`HeroesScreen.SetFeaturedHeroData` (`RVA 0xC59748`) calls
`GameUtil.GetFeaturedHero` and dereferences the result. `FeaturedHeroManager`
reads `featuredhero` from `LoginManager.LoginData`; in this build the effective
login-data source is **`/account/data`**, not `/auth/login`.

`/account/data` must contain:

```json
{"featuredhero":{"cdn":"http://127.0.0.1:8080/cdn","orderType":"Random",
 "heroes":[{"id":"optimus_c_tf_t3","gacha":"","gachaCTA":"","pvp":"","pvpCTA":"",
            "questset":"","questsetCTA":"","store":"","storeCTA":"",
            "synergies":[],"abilities":[],"image":"","images3":false}]}}
```

Without it, `FeaturedHeroManager.Heroes.Count == 0` and BOTS throws
`NullReferenceException` in `SetFeaturedHeroData`. [STATIC]+[RUN]

## 8. Open items

- Real hero ids/stats/ranks from Kabam (currently invented).
- Real `featuredhero` rotation.
- Battle-side BCG fields (`BCGAttributeDataBase`, tuning) and their formulas.
