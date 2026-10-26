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
