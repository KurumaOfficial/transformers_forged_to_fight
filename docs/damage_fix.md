# Damage fix: ArmorRatingConstant and the `bcg-combat` config

Status: **fixed and verified [RUN].** This file records the exact static chain
and the config data, not a client patch.

## Symptom

Every hit produced `HitResultData.Damage=0` while `DamageRating=0.7`,
`AttackLevel=1`, `Flags=129` and `PlayerAttributes._attack.Get()` was 115.

## Static chain

| Element | Value / RVA | Evidence |
|---|---|---|
| Class | `TuningGameplay` (TypeDefIndex 9470) | `work/il2cpp_dump/dump.cs` |
| Field | `ArmorRatingConstant` at `+0x20`, type `SafeFloat` | `dump.cs` |
| Config callback | `TuningGameplay.OnConfigChanged` `0x14254BC` | disassembly |
| Deserializer | `TuningGameplay.DeserializeData` `0x1425540` | disassembly |
| Config mode gate | callback compares the config mode with `bcg-combat` | `0x14254BC` |
| Source dictionary | `missionsconfig.configs["bcg-combat"]` | `server/data/missions_config.json` |
| Key | `armor_break` -> `ArmorRatingConstant` | `Dot::Single` in `0x1425540` |
| Consumer | `PlayerAttributes.GetArmorDR` `0xDAD7A4` | disassembly |

`GetArmorDR` computes:

```
armor = _armorRating.Get()
dr = armor / (abs(armor) + TuningGameplay.ArmorRatingConstant)
     + _armorUpModifier.Get() - _armorBreakModifier.Get()
```

With `ArmorRatingConstant=0`, armor 50 gives `50/(50+0)=1.0` (100% reduction),
so every hit on that fighter is zero. With `200`, `dr=0.2`; a raw 80.5 hit
becomes 64.4.

## Config keys used by `bcg-combat`

The serializer reads these keys (literal JSON paths) and stores them in
`SafeFloat` fields:

| JSON key | Field | Code default | Live after config |
|---|---|---:|---:|
| `armor_break` | `ArmorRatingConstant` | 200.0 | 200.0 |
| `mana_gain` | `ManaPerSpecial` | 300.0 | 300.0 |
| `critTime` | `CritRatingConstant_A` | 111.0 | 111.0 |

Values are the client code defaults, used as `[CLIENT]` data; the live read
(`work/probe_tuning_gameplay.py`) confirms 300/200/111. Other
`TuningGameplay` fields keep their code defaults or are populated by other
paths; the full field table is in `spec/tuning_values.md`.

**Do not replace the outer `missionsconfig` wrapper.** It must remain:

```json
{"missionsconfig": {"configsHash": "v1", "configs": {..., "bcg-combat": {...}}}}
```

Replacing the wrapper with the inner `configs` object caused a
`QuestsManager.RefreshUserBase` NRE.

## Why the earlier safe-value claim was wrong

IL2CPP arrays store their elements **inline at `+0x20`**, not behind a pointer
stored at `+0x20`. The first probe treated the bytes at `+0x20` as a pointer and
decoded garbage; the correct read gives a 4-byte float 115.0 and the FNV hash
matches. The zero was entirely in `GetArmorDR`.

## Evidence

- `[RUN]` `docs/damage_pipeline.md`
- `[RUN]` `docs/evidence/post_battle_2026-10-29/`
- `[STATIC]` `work/il2cpp_dump/dump.cs`, `work/disasm_fn.py 0x1425540`
- `[RUN]` `work/probe_tuning_gameplay.py` live values
