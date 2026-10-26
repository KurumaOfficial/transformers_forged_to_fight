from pathlib import Path

p = Path("MASTER_PROMPT.md")
s = p.read_text(encoding="utf-8")
s = s.replace("# MASTER_PROMPT v4.6 - current state and queue (2026-10-26)",
              "# MASTER_PROMPT v4.7 - current state and queue (2026-10-26)")
marker = "## 2026-10-26 battle init fixed (read this first)"
new = """## 2026-10-26 v4.7 update (read this first)

- **Battle init NRE root cause:** `Blueprint.BaseRangedDamageType` (character
  field `BCGCharacterData +0x48`), not `Tags`. `DamageType..ctor` (`0xBB0B70`)
  tail-calls `HashSet<string>..ctor` (`0x12A9D94`). Fixed with non-null
  `base_damage`/`base_ranged_damage` in **characters** (blueprint keys alone do
  not feed the getter) and a `bumblebee_cin_dotm` blueprint alias. Full record:
  `docs/battle_init_fix.md`; evidence `docs/evidence/battle_init/`.
- **Battle reaches `BattleArbiterMainState`** with two `PlayerController`s;
  no `/matches/match-loaded` is sent for `quests_fight`; no resolve/rewards.
- **Global blocker:** `FuseODRBlocker` is Open even with 0 active/requested
  downloads and no pending WADs; `ODRManager` has no manifest
  (`_receivedDataFromServer=0`, `_initAndGetManifestComplete=0`), and PlayCore
  cannot bind to `com.android.vending` on the sideloaded emulator. No `/odr/*`
  request reaches the stub. See `docs/odr_flow.md`.
- **R2:** client formula exact; interval LP on raw HP/ATK is infeasible
  globally and per rank/level (`data/wiki/rating_lp.json`); 20-page parser
  audit has 0 numeric misparses. Need server rating split.
- **R1:** 37 WIKI/table, 22 ASSUMED; 2 anchored with star-3 + global ratio
  (10%), 20 class-median (25%). `docs/stat_coverage.md`.
- **Q3/4:** 81/90 boss ids; 9 Starscream gaps; explicit `[ASSUMED]`
  `nemesisprime_gs_voyager2015` fallback, never called the original.
  `docs/starscream_fallback.md`.
- **S1/nightly:** BOTS sweep is 12/59 (script only sweeps the first 12); a new
  59-page script was added but the global blocker/navigation prevents a clean
  59/59. Nightly check_all PASS; full smoke FAIL by status; corrected
  `nightly.ps1` prints FAIL/PARTIAL, not exit-code PASS.
- **Enums:** `spec/battle_enums.md`; damage strings `kinetic`/`energy`, class
  flags numeric, AI selectors `aiString`/`aiPer`, default behavior tree
  `Gameplay/AIBehavior/AIBehavior-Default`.
- **Open:** ODR/asset-pack init, Starscream pack, server rating split, 34 wiki
  images (Wayback 404/503 in tried variants), BOTS pagination/full smoke.
- No client patch/Frida; no push/gc/filter-repo/remote/config.

## 2026-10-26 battle init fixed (read this first)"""
if marker not in s:
    raise SystemExit("marker missing")
s = s.replace(marker, new, 1)
p.write_text(s, encoding="utf-8")
print("v4.7 updated")
