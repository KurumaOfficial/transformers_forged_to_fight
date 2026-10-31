# BOTS grid and cards (Step 2) - static/run findings

Status: **partially blocked by the client-side card list.** The catalog and the
live BCG data contain the bots, but the BOTS screen draws a client-side
59-card list and uses display-only `HeroData` for the cards. Server roster
additions/replacements do not change the grid. No client patch was made.

## 1. Why Starscream is not in the grid `[RUN]`/`[STATIC]`

- The grid shows exactly the **59 ODR playable bots**, in reverse-alphabetical
  name order. It does not show the two merged-only prefabs:
  `starscream_gs` and `optimusprime_gs_v` (both live only in
  `characters.assetbundle`, not in an `_odr` pack).
- I added Starscream to `getLoginData` (blueprint/character/heroes/roster) and
  restarted the app. The server response contained 60 roster entries and the
  Starscream patch, but the grid still showed the same 59 cards and no
  Starscream. `[RUN]`
- I then replaced Windblade's roster entry with Starscream (diagnostic flag) and
  restarted. The server response had Starscream instead of Windblade, but the
  grid still showed Windblade and the live `BCGUserHeroDict` still had 59
  original keys. `[RUN]`
- Live dictionary probe: `BCGManager.UserData.heroes` has **59** keys; the
  blueprint/base/character dictionaries have **62/61/61** and **do** contain
  `starscream_gs`. So the missing part is the client-side user-hero/grid list,
  not the catalog. `[RUN]` `work/probe_bcg_dicts.py`.
- Static anchor: `HeroesScreen.SetScreenType` sets `_entities` from
  `BCGHelper.GetHeroes(null)` (`0xC1F41C` -> `GetEntities 0xC210D4`), and the
  `Profile.HeroesScreenList` is a "seen" list (`0xC58B48`), not the card
  source. The screen also has a client-side blueprint list path; the observed
  59 equals the ODR pack count, not the 60-entry catalog roster.

**Conclusion:** adding Starscream by server data is correct for catalog/boss
use, but cannot create a BOTS card in this client build. The grid card needs an
ODR/playable asset entry. This is a client asset gap, not a JSON key we can
guess. Do not claim Starscream is visible in BOTS.

## 2. Flat `300` rating `[RUN]`/`[STATIC]`

- All 59 cards show `300`, including bots whose live `BCGUserHero` rating is
  correct: Windblade `_heroRating=1381`, HP `5160`, ATK `498`; Sideswipe
  `1426`, Bumblebee DOTM `155`. `[RUN]` `work/probe_bcg_dicts.py`.
- The card overlay is `RatingWidget.SetData` (`0xE1E504`). It uses
  `HeroData.userHero` rating when that object is present and non-zero;
  otherwise it falls back to the display `HeroData` (base/default, observed
  `300`). The BOTS grid is feeding it display data, not the live user hero.
- Therefore the `300` is not a server `rating` field we forgot to set; the
  login payload already carries 1381/1426/155. Changing server `rating` does
  not move the card. `[RUN]`

## 3. UPGRADE / INFO `0` HP and ATK `[RUN]`

- Opening Windblade -> UPGRADE/INFO shows `LEVEL 1/10`, `RANK 1/5`,
  `XP 100/100`, but HP/ATK `0` (`work/info_after.png`,
  `work/upg_now.png`). The model and name are Windblade.
- The live `BCGUserHero` has a valid `BCGAttributeData` (`hp=5160`,
  `attack=498`, `heroRating=1381`), so the data exists but the screen does not
  bind it.
- An earlier session requested `/bcg/getBaseHeroData` for the stale
  `optimus_c_tf_t3`, not the tapped Windblade; that stale blueprint was the
  first/default entry in the server catalog and had no character bundle.
  `server/data/catalog_removals.json` now removes it at load time. This is a
  catalog cleanup, not a UI fix; the 0/0 binding is still open.
- The `getBaseHeroData` response itself is a valid list with
  `max_hp=5160`, `attack=498`, `rating=1381`, and `attributeData`; a direct
  probe returns those keys. `[RUN]`

## 4. Denominator and sweep (Step 2.4)

- Effective catalog: 61 base characters; roster 60 (59 original + Starscream
  patch); merged-only `starscream_gs`, `optimusprime_gs_v`.
- The visible grid is **59** cards. Missing from the grid:
  - `starscream_gs` (merged, no ODR pack);
  - `optimusprime_gs_v` (merged, and not yet in the catalog roster).
- The sweep still counts cards, not ids. A true ID sweep needs card -> hero id
  feedback; the current popup does not request `getBaseHeroData` per card, so
  the ID list cannot be read from the server log. `[RUN]`
- Do not use the 59-card count as proof that 59 distinct ids were exercised
  unless each card's INFO screen is matched to a name. The earlier 59/59
  metric was a screenshot/count metric.

## 5. What is safe to keep

- `server/data/catalog_removals.json`: removes the stale `optimus_c_tf` /
  `optimus_c_tf_t3` duplicate (no character bundle, only portraits). It was
  the default/first blueprint observed in the popup request. `[STATIC]`/`[RUN]`
- `server/wiki_stats.py`: `optimusprime_gs_v` wiki row 6240/444 and Starscream
  5400/391/1354.
- No client patch, no fake card data, no invented ODR bundle.

## 6. Open

1. Find the client-side source of the 59-card list (asset/prefab/ScriptableObject)
   and whether an ODR availability flag can be set from data.
2. Bind the card `HeroData` to the live `BCGUserHero` (rating/HP/ATK) instead of
   display defaults.
3. Make `getBaseHeroData` apply to the INFO/UPGRADE screen; verify with a live
   request for the tapped bot.
