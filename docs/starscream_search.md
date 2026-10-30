# Starscream search (Step 7)

Status: **Starscream is in the retained client.** The earlier "no 9.2.0 pack"
claim was wrong: it was a catalog/ODR scan gap, not a missing bot.

## Evidence `[STATIC]`/`[RUN]`

- `work/unpacked/assets/characters/toc.txt` lists:
  - `bundles/characters/merged/starscream_gs`
  - `bundles/characters/merged/starscream_gs_lw`
  - `bundles/movedata/move_starscream_special_01/02`,
    `move_attackranged_starscream_burst_01/02`,
    `move_heavy_starscream_shoot`, `move_projectile_starscream_missile`.
- `work/unpacked/assets/assetpack/characters/characters.assetbundle` contains
  the string `Starscream_GS` at offset 792466 (byte search).
- Localization keys exist: `ID_SPECIAL_ATTACK_STARS_GS_0..2`,
  `ID_SPECIAL_ATTACK_DESCRIPTION_STARS_GS_0..2`,
  `ID_STAT_SIG_STARS_*`, `ID_CHARACTER_BIOS_STARS_GS`,
  `ID_STARSCREAM_RANGED*`, `ID_LOADING_TIPS_STARSCREAMFIGHT`.
- Portraits/loading assets: `portrait_stars_gs_large.png`,
  `portrait_stars_gs_small.jpg`, `portrait_stars_gs_quest.png`,
  `stars_gs.png`, `starscream_fight.jpg`.
- Wiki page `Starscream` exists (`data/wiki/bots.json`): class **Tactician**,
  Decepticon, release **2017-08-24**, stat table 1/1 **5400 HP / 391 ATK /
  1354 rating**.

## Catalog addition `[RUN]`

Added to `server/data/bcg_login_data.json`:

- `blueprints.starscream_gs` (Tactician, class 2, Decepticon, rarity 4,
  max_rank 4, `syn_decepticons`);
- `characters.starscream_gs` (model `starscream_gs`, Decepticon, G1);
- `heroes.starscream_gs` rank 1-4 entries;
- one `userData.heroes` roster entry with 5400/391/1354.

The server `getLoginData` now returns 60 roster heroes and 62 blueprints.
A UI page check is still open: the BOTS list first page is unchanged and the
page swipe did not move in the last check, so the visual Starcream card/model
is not yet confirmed. Do not claim a live model load until a BOTS page/fight
shows it.

## Why the earlier scan missed it

The 59-pack scan used directories under `work/unpacked/assets` (ODR pack
folders). Starscream lives in the **main** `characters.assetbundle` and the
`characters/toc.txt` merged path, so it was not in the directory list.
`bot_matrix_full` also marks `Starscream` as an unmapped wiki page because the
catalog lacked the id, not because the asset was absent.

## Conclusion

- The bot is **pre-APK** (2017), not post-APK content.
- The client data and wiki stats are present; the catalog now has a
  `starscream_gs` entry.
- The remaining task is UI/model verification and a real fight, not finding a
  pack.
