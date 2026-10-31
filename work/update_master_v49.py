from pathlib import Path

p = Path("MASTER_PROMPT.md")
s = p.read_text(encoding="utf-8")
s = s.replace("# MASTER_PROMPT v4.8 - current state and queue (2026-10-26)",
              "# MASTER_PROMPT v4.9 - current state and queue (2026-10-29)", 1)
s = s.replace("`report/FINAL_2026-10-26.md`,",
              "`report/FINAL_2026-10-29.md`, `report/FINAL_2026-10-26.md`,",
              1)
marker = "## 2026-10-26 v4.8 update (read this first)"
new = """## 2026-10-29 v4.9 update (read this first)

- **Hidden player stats are solved [RUN].** The quest team payload is the
  player's battle-attribute source, not `getBaseHeroData`. Add
  `armor/crit_chance/crit_damage/block_proficiency/mana_gain/...` to
  `quest["team"]`, `teamData.updates.activeTeams[].heroes[]`, and login
  `activeTeams[].heroes[]`. Live player: Armor 50.0, Crit 0.1, CritDamage 1.5,
  Block 0.5, ManaGain 1.0. Values are `[ASSUMED]` defaults. See
  `spec/attribute_pipeline.md`.
- **ODR overlay is not a permanent input blocker.** The battle is visible and
  controllable; swipes increment HITS. `FuseODRBlocker` still exists with 0
  downloads/pending WADs, but does not cover the HUD in `BattleArbiterMainState`.
  The earlier "input blocked" conclusion was too strong. Play Asset Delivery
  is still unavailable; ODR manifest track stays blocked.
- **New combat blocker: zero damage.** `PlayerAttributes._attack.Get()` returns
  0 while the display `_value` is 115; `HitResultData.Damage=0`,
  `DamageRating=0.7`, `Flags=129`. `GetDamageInflicted` multiplies by the safe
  value. This is a client stat commit issue, not missing data; no client patch.
- **Attack-value keys fixed by data.** `AttackLevel` maps to
  `Light/Medium/Heavy/Ranged/Special1..3/Normal`; `BCGAttackValue..ctor` reads
  the literal `attack_percent` key. New `[ASSUMED]` entries make
  `DamageRating=0.7` for Light hits. `class_power:1.0` added; live ClassPower
  is 1.0.
- **Tuning:** no direct `BL` callers of `TuningManager.Get*`; keys are the
  public field names applied by `Tuning.LoadTuningData`. `spec/tuning_keys.md`
  has 242 `Tuning` + 30 `TuningGameplay` fields. Live ODR flags:
  `ODRForceDownloadAll=0`, `ODRAllowNative=1` (data-only, not changed).
- **Routing split partial:** `routes/auth.py`, `routes/matches.py`,
  `routes/odr.py`, `routes/quests.py`; goldens refreshed. `docs/routing_split.md`.
- **Abilities blocked:** no original per-bot `statMods`/`Buff` ids/triggers.
  `docs/ability_blocker.md`; special-attack key builder is documented.
- **Economy/post-battle:** `docs/economy.md`, `docs/post_battle_quests.md`;
  numeric retail tables are missing, fight does not resolve.
- **Nightly 2026-10-29 19:54 PASS:** check_all PASS, smoke PASS,
  BOTS 59/59. Snapshot `runs/2026-10-29_200853/`, index `runs/index.json`.
- **Still blocked:** zero damage/death/resolve/rewards, Starscream pack,
  retail rating split, full PlayStore/ARM64 experiments, per-bot hidden stats,
  full routing split, 34 wiki images.

"""
if marker not in s:
    raise SystemExit("v4.8 marker missing")
s = s.replace(marker, new + marker, 1)
p.write_text(s, encoding="utf-8")
print("v4.9 inserted")
