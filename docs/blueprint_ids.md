# Blueprint id, ModelID and the unified blocker (Step 1, v4.13)

Status: **pilot done; the "rename the blueprint to the short token" hypothesis
is disproved for the BOTS grid.** The grid keys on the asset/character id.
The loc token is a separate character field; the exact JSON key that sets it
is still open. No client patch.

## 1. Key builder `[STATIC]`

`BCGHelper.GetSpecialAttackNameLocString` (`0xC1B154`):

1. input string -> `LastIndexOf("_")`;
2. substring before it -> `ToUpperInvariant()`;
3. concat `ID_SPECIAL_ATTACK_` + token + `_` + index.

The same pattern is used for the description. So the input must end in
`_<suffix>` and its prefix must be the localization token, e.g.
`windb_gs_5` -> `WINDB_GS`.

But the caller is not necessarily passing `BCGBlueprintBase.Blueprint`. The
`CharacterDetailScreen` caller loads a character object and a getter that
reads `+0x48` then `+0x10` (`0x12AD15C`), i.e. a `BCGCharacterData.Character`
string. `BCGCharacterData` has `Character` at `+0x10` and the property is read
with `Dot.String`/`Dot.Loc` in its ctor (`0xC175E4`). The exact JSON key
(`character`, `id`, ...) is not resolved yet; the slot is not a plain string.

## 2. Pilot A: rename `windblade_gs` -> `windb_gs_5`

Changed only the blueprint id + top-level `heroes` key + roster entry; kept
`character`/`modelId` = `windblade_gs`.

- `[RUN]` BOTS grid: **Windblade disappeared entirely**. The first card became
  Wheeljack. Screenshot:
  `docs/evidence/blueprint_pilot/rename_windblade_card_missing.png`.
- `[RUN]` `getLoginData` contained `windb_gs_5` in blueprints/heroes/roster and
  still contained `characters.windblade_gs`; the client still did not render a
  card.
- Conclusion: the card list is keyed by the **asset/character id**
  (`windblade_gs`), not by an arbitrary short token. Renaming the blueprint id
  breaks the card.

## 3. Pilot B: keep the asset id, set `Character` to the short token

Restored blueprint/heroes/roster to `windblade_gs`; added
`characters.windblade_gs.character = "windb_gs_5"`.

- `[RUN]` Windblade card returned. Screenshot:
  `docs/evidence/blueprint_pilot/restored_card.png`.
- `[RUN]` INFO screen still shows `LEVEL 1/10`, `RANK 1/5`, HP 0, ATK 0, and
  the "out of Ore-13" panel. Screenshot:
  `docs/evidence/blueprint_pilot/info_0hp_0atk.png`.
- The card rating is still `300` on the grid; the live `BCGUserHero` for
  Windblade has `heroRating=1381`, HP 5160, ATK 498.
- Conclusion: the blueprint-id rename is **not** the cause of the 300/0 card
  binding. The loc token hypothesis is still plausible for the strings, but
  the INFO screen is blocked by the missing resource/upgrade panel, so the
  special-attack name is not visually confirmed.

## 4. What the suffix means

- The only current `_2` blueprint is `bumblebee_cin_dotm_2`; its `rarity` is 2
  and it has one rank entry. The suffix is **not proven** to be rank, star or
  variant; it was introduced by the stub. Do not generalize it yet.
- The client accepted `bumblebee_cin_dotm_2` in the grid/roster, so a suffix
  is allowed, but the **base key before the suffix** must be the character id
  the client knows.

## 5. `data/blueprint_id_map.json`

61 rows: `client_id`, `model_id`, `blueprint_id`, `loc_token`,
`portrait_token`, string presence, bio/special keys. It records the current
asset-key mapping and the pilot result note. Do not use it to mass-rename
blueprints.

## 6. Seven bots without strings

Dirge, Ironhide G1, Rodimus, Skywarp, Slipstream, Soundblaster, Sunstreaker.
Their tokens are in `docs/special_attack_tokens.md`; no other spelling with
strings was found by the census search.

## 7. Next static step

Resolve the JSON key that sets `BCGCharacterData.Character` in `0xC175E4`
(the first `Dot.String`/`Dot.Loc` slot) and the caller's exact object. If the
key is `character`, a data-only patch can set the short token without touching
the blueprint key; then test the special-attack names on a screen that is not
blocked by the Ore-13 panel (e.g. the prefight/bot detail tab, if reachable).
