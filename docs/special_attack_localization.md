# Special-attack names / localization (Step 6.3)

## What is shown

`[RUN]` The bot details screen shows raw keys like
`M1_SPECIAL_ATTACK_<BOT>.<n>`. This is not a missing generic
`ID_SPECIAL_ATTACK` string.

## Search

- `work/unpacked/assets` (all files): **no** `M1_SPECIAL_ATTACK`,
  `SPECIAL_ATTACK_<BOT>` or `M1_` literal.
- `global-metadata.dat`: only generic `ID_SPECIAL_ATTACK` and
  `ID_SPECIAL_ATTACK_DESCRIPTION`; no per-bot key.
- Localization dumps: only generic `ID_SPECIAL_ATTACK` keys and move/status
  strings (`ID_STARSCREAM_RANGED*`), no `M1_SPECIAL_ATTACK_*`.
- `MoveSequencer`/`MoveSet` data is loaded from `assetpack/characters/moves`
  and per-character move bundles; the special-attack display name is built
  from the move set at runtime, then looked up as a localization key.

## Conclusion

The raw key is a **runtime-generated move/ability key**, and the per-bot
localization table that would resolve it is not in the retained 9.2.0 assets.
Adding guessed keys is unsafe: the exact case/punctuation (`<BOT>.<n>`,
`M1_` prefix) is client-generated, and the display name is also in the move
data.

## Safe next step

1. Capture the exact string at the UI (already done: `M1_SPECIAL_ATTACK_*`).
2. Find the move entry for the same `<BOT>.<n>` in the character move bundle.
3. If the move entry has a `name`/`displayName` field, write the localization
   entry with that exact key; otherwise leave the raw key and document it.
4. Do not synthesize names from wiki text without the move id mapping.

The pilot ability data (`data/wiki/ability_pilot.json`) remains the source for
names/descriptions, but it cannot be wired until the key table is recovered.

## Exact key builder (static)

`[STATIC]` `SpecialAttackInfoPanelItem.SetData` (`0xCC3188`) calls:
- `BCGHelper.GetSpecialAttackNameLocString` (`0xC1B154`)
- `BCGHelper.GetSpecialAttackDescriptionLocString` (`0xC1B21C`)

Both helpers:
1. take the special-attack id (e.g. `M1_SPECIAL_ATTACK_<BOT>.<n>`),
2. `LastIndexOf` a separator (the static field at `0x2C35A20`; the name
   helper uses it),
3. `Substring(0, index)`,
4. `ToUpperInvariant()`,
5. `String.Concat(prefix, upper, indexString)`.

The prefix fields are `0x2C35000+0xA20` (name) and `0x2C1C000+0xCA0`
(description). The screen shows the raw id because the resulting
`ID_SPECIAL_ATTACK_*` key is not present in the retained localization tables.
The metadata contains only generic `ID_SPECIAL_ATTACK` and
`ID_SPECIAL_ATTACK_DESCRIPTION`; no per-bot key was found.

To fix by data, add the exact `ID_SPECIAL_ATTACK_<UPPER>` and
`..._DESCRIPTION` keys for each move id; the move id/name must come from the
character move set, not invented. Until then, the raw `M1_SPECIAL_ATTACK_*`
display is expected.

## 2026-10-29 live bot details [RUN]

Windblade details screen (`tests/smoke/10b_bot_info.png`) shows:

- `ABILITIES` -> **NO ABILITIES** (the placeholder stat mod is not shown as a
  bot ability).
- `SPECIAL ATTACKS` -> raw keys
  `MS_ID_SPECIAL_ATTACK_WINDBLADE_0`, `..._1`, `..._2` (the client displays the
  key because the localization table has no entry).
- `Synergy Bonuses` panel is present but empty for Windblade.

This confirms the missing-data diagnosis: the client's UI slots are intact,
but there is no per-bot `statMods`/`Buff`/localization data. The raw special key
format here is `MS_ID_SPECIAL_ATTACK_<BOT>_<n>`; other bots may use a different
move id (`M1_SPECIAL_ATTACK_*` was seen earlier), so do not assume one prefix
for every bot.

## 2026-10-30 server-side localization override probe (Step 3.3)

Static path exists, but the live override is **not proven**.

- `LocalizationManager.Async` (`0x127A050`) lowercases the message and compares
  it with the metadata literal at index 18474: **`loc-cache-update`**
  (`global-metadata.dat` v27, string-literal table; resolved by hand).
  On a match it calls `loadLocData(payload)` (`0x1279C8C`).
- `LocalizationManager` keeps `Dictionary<string, IDictionary> locCache` and
  exposes `UpdateLocForSystem`/`AllLocForSystem`.
- `XlateManager.Connect` (`0x1593888`) reads the account `xlate2Resources`,
  compares category hashes and calls `updateStringsFromCDN(category,
  resource, cb)` (`0x159414C`). `account_data.json` already contains a
  `xlate2Resources.resources[]` list and `cdn: http://127.0.0.1:8080/cdn`.

Experiments (server data only, no client patch):

1. `[RUN]` Sent async `{component, message: "loc-cache-update", payload}`
   from `/bcg/getLoginData` and then from every response, with components
   `localization`, `LocalizationManager`, `localizationmanager`, `loc` and a
   flat payload overriding `ID_UI_HEROES_BOTS` (`BOTS`). The home label did
   not change; no localization error appeared in logcat.
2. `[RUN]` Changed `account_data.json` `xlate2Resources` from
   `{resources:[...]}` to a direct array (the client calls `Dot.Array` on it).
   No `/cdn/...`, `xlate/...` or `snapshot` request was observed; change
   reverted.

Conclusion: the client has a real `loc-cache-update` async hook and an Xlate2
CDN path, but neither accepted our payload in the tested shape. The exact
async component/registration and the Xlate2 enable condition are still
unknown. Do **not** invent per-bot keys or claim a server override; the raw
`MS_ID_SPECIAL_ATTACK_WINDBLADE_*` display remains the expected result.
