from pathlib import Path

p = Path("MASTER_PROMPT.md")
s = p.read_text(encoding="utf-8")
s = s.replace("# MASTER_PROMPT v4.7 - current state and queue (2026-10-26)",
              "# MASTER_PROMPT v4.8 - current state and queue (2026-10-26)")
marker = "## 2026-10-26 v4.7 update (read this first)"
new = """## 2026-10-26 v4.8 update (read this first)

- **ODR manifest init:** normal `ODRManager.Initialize` does not call
  `InitAndGetManifest`. The lazy path is
  `EnsureManifest` (`0x135A730`) -> `WaitForTOC` (`0x135A6B4`) ->
  `ODRAPI.GetManifest` (`0x1355360`) -> `/odr/get-manifest`.
  `InitializedAndLoadedCoroutine` is only reached from `DownloadAllCoroutine`
  (debug). The battle bundle exists, so this lazy path is not started. The
  global `FuseODRBlocker` is still Open with 0 downloads; PlayCore
  `UnityDataAssetPack`/missing `com.android.vending` is the stronger cause.
  See `docs/odr_flow.md`, `docs/odr_report.md`.
- **Play Store image:** `РАЗРЕШАЮ_ОБРАЗ_PLAYSTORE` is empty -> nothing
  downloaded/created. Plan: `docs/playstore_image_plan.md` (API30 x86_64
  google_apis_playstore, ~1.2–1.6 GB, risks; ARM64 plan included).
- **Hidden base stats:** `spec/attribute_pipeline.md` records
  `BCGAttributeDataBase` fields/JSON keys/defaults. HP default is 1.0
  (`0xC149C0`); live Armor/Crit/Block/Mana are 0 although the flat
  `getBaseHeroData` sent non-zero values, so the battle path recalculates from
  catalog/growth tables, not the flat response. Fill `heroes[rank]` /
  `attributeGrowthDefs` / `curves`, not client code.
- **R2 inverse:** `data/rating_table.json` has 363 `[DERIVED]` rows with an
  equivalent proportional `HeroRatingHP/Attack` split that reproduces the
  wiki rating through the exact client formula. It is not the retail split.
- **Content timeline:** `docs/content_timeline.md` (252 pages with saved
  timestamps; 131 at/after APK 2022-07-26; 53 after close 2023-01-13;
  timestamps are saved revisions, not first release).
- **S1/nightly:** `work/sweep_bots59.py` **59/59**; nightly 21:19 **PASS**
  (check_all PASS, smoke PASS, BOTS 59/59). `runs/` snapshot/index added
  outside git.
- **Still blocked:** playable fight (ODR), Starscream pack, retail rating
  split, full PlayStore/ARM64 experiments, full TuningManager xref, full
  routing split, 34 wiki images.

## 2026-10-26 v4.7 update (read this first)"""
if marker not in s:
    raise SystemExit("marker missing")
s = s.replace(marker, new, 1)
p.write_text(s, encoding="utf-8")
print("v4.8 updated")
