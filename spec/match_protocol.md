# Match protocol — static skeleton (not yet observed on the wire)

Status: **partial**. No `/matches/*` request has been observed. Everything below
is [STATIC] from `dump.cs`/disassembly unless marked [ASSUMED]. The exact JSON
response contract is **not** proven.

## 1. Trigger

`ActiveQuest.ActivateMatch` (`0x10A0038`) is called from the prefight UI path
(`PrefightScreenData.OnFight`, `0xE3E778`). It:

1. constructs `QuestsMatchData` (`0xD6C27C`);
2. takes `battleId` from `ActiveQuest.player.battleId` (`0xDAA974`);
3. stores the hero argument at `QuestsMatchData+0x20`;
4. rejects empty battle id / hero (`No battle id!` / `No hero!`);
5. calls `MatchManager.ActivateMatch<QuestsMatchData>` (`0x11F1FD0`).

`QuestsMatchData` fields:

| Field | Offset | Meaning |
|---|---|---|
| `qid` | `+0x10` | quest id |
| `battleId` | `+0x18` | battle id from the quest player |
| `hero` | `+0x20` | selected hero blueprint |

## 2. Match API

| Method | RVA | Role |
|---|---|---|
| `MatchAPI.ActivateMatch` | `0x11F14F8`, `0x11F1680` | build/send activate request |
| `ActivateMatchHandler` | `0x11F1754` | callback |
| `MatchManager.ActivateMatch<T>` | `0x11F1ED4` (3 args), `0x11F1FD0` (4 args) | generic entry |
| `QuestsMatchData.addToRequest` | `0xD6C1C0` | adds `qid`, `battleId`, `hero` |

The request path uses `quests_fight` as the match type. The exact URL suffix
and body are `[ASSUMED]` until the first request is captured.

## 3. Response / fighter data

`FighterData` (TypeDefIndex 8671) fields, [STATIC]:

`Id`, `PlayerName`, `PlayerTag`, `IsBoss`, `BaseAttributes`, `Attributes`,
`Blueprint`, `SigLevel`, `AttackBonus`, `AIProfile`, `OverrideAIPersonality`,
`TeamData`.

`BCGAttributeDataBase` (TypeDefIndex 8303) fields, [STATIC]:

`StatMods`, `SigMods`, `BuffMods`, `SpecialAttackCount`, `HPMax`, `HPMaxBase`,
`HP`, `Attack`, `AttackBase`, `Armor`, `CritChance`, `CritDamage`,
`PerfectBlockChance`, `BlockProficiency`, `ManaGain`, `ManaStart`,
`ResistMagic`, `ResistPhysical`, `StunTime`, `StunChance`, `HeroRating`,
`HeroRatingHP`, `HeroRatingAttack`, `HeroRatingHPBase`,
`HeroRatingAttackBase`.

Current `server/data/match_activate_response.json` is `[ASSUMED]`:
`matchId`, `matchType`, `seed`, `fighterData.enemyFighter`. Do not treat it as
Kabam data.

## 4. Follow-up endpoints

| Endpoint | Client side | Status |
|---|---|---|
| `/matches/activate-match` | `MatchManager.ActivateMatch` | never called |
| `/matches/match-loaded` | `MatchAPI.SignalMatchLoaded` | never called |
| `/matches/resolve-match` | `MatchManager.ResolveMatch` | never called |
| `/matches/match-resolved` (async) | `QuestsManager.Async` | never called |

The `async` envelope is `{component, message, payload, id, channel}`; for
quests the component is `quests` and messages include `match-activated`,
`match-resolved`, `avx-update`, `sync`.

## 5. What is needed next

1. Get a non-null `IPrefightDataProvider` so `MakeFight` can call
   `ActivateMatch` (see `docs/frida_plan.md` and `STATE.md` §15).
2. Capture the first `/matches/activate-match` request body (nonce, api,
   qid/battleId/hero).
3. Replace the [ASSUMED] response with fields observed/derived from FighterData
   and BCGAttributeDataBase; then verify prefight HP/rating and the transition
   to the fight scene.
