# System endpoints and ui (Step 9, static first)

Status: **static endpoint catalog; only view-only screens verified.** No
gacha/objective/store logic is implemented. Do not invent response keys; the
client classes below are the schema anchors.

## Gacha / CRYSTALS

| endpoint | client | status |
|---|---|---|
| `/gacha/store`, `/gacha/store/:type/:data` | `GachaAPI` / `GachaManager` | not requested by the current empty CRYSTALS screen |
| `/gacha/pick`, `/gacha/pick/:type/:data` | `GachaAPI.PickFromBox` (`0xF66AFC`) | not implemented |
| `/gacha/getOdds` | `GachaAPI.GetGachaOdds` (`0xF670EC`) | not implemented |
| `/gacha/claimfree`, `/gacha/claimfree/:type/:data` | `ClaimFreeBox` (`0xF66E2C`) | not implemented |

`GachaManager` fields: `_sets`, `_categories`, `_tokens`, `_fragments`,
`_odds`, `MaxCombinedSpins`. `GachaAPI.OnGachaData` parses
`GachaGroup`, `GachaCategory`, `GachaTokenCount`, `GachaFragmentCount`.
Current CRYSTALS screen: `No crystals available`; no `/gacha/*` request
observed.

## Objectives

| endpoint | client | status |
|---|---|---|
| `/objectives` | goals model | screen `[0/0]`; empty |
| `/objectives/activate`, `/cancel`, `/complete`, `/refresh` | goals API | not observed |

The screen opens without NRE. Real objective data is not in the retained
server data; `data/wiki` has no numeric objective table.

## Store / GameStore

| endpoint | client | status |
|---|---|---|
| `/store/:type`, `/store/:type/:data` | store API | STORE locked at LEVEL 2 |
| `/store/offerurl`, `/store/payouts`, `/store/verify-payout` | store/IAP | not implemented |
| `/gamestore/buy`, `/gift`, `/gift/:uid`, `/sell`, `/use` | gamestore | not implemented |

The STORE level lock is client `TuningLevelLocks` (min level 2), not a server
response. Home `LVL 0` is still the `LevelRewardsManager` issue
(`docs/level_lock.md`). Prices/items are not in the retained data.

## Base / Inventory / Profile / Away / Arena

| system | endpoint(s) | current |
|---|---|---|
| BASE | `/base`, `/base/active`, `/base/place/...`, `/base/remove/...`, `/base/swap/...`, `/base/building/...`, `/base/claim/...` | `/base/active` works; BASE view opens |
| INVENTORY | `/inventory`, `/inventory/` | top-bar currencies only |
| PROFILE | `/userprofile/` | empty result; Commander opens BOTS |
| AWAY | `/autorefresh/ave/refresh` | no AWAY entry in FIGHT list |
| ARENA | `/autorefresh/...`, PvP login | ARENAS locked |

## Safe next step

Add empty, valid responses for the endpoints the client actually requests,
then one data-driven box/objective/store item from wiki, with a screenshot.
Until a request is captured, keep the stubs empty; a guessed schema would
repeat the post-battle mistake.
