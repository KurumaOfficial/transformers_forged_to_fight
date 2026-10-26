from pathlib import Path

p = Path("MASTER_PROMPT.md")
s = p.read_text(encoding="utf-8")
s = s.replace("# MASTER_PROMPT v4.5", "# MASTER_PROMPT v4.6")
marker = "## 2026-10-25 breakthrough (read this first)"
new = """## 2026-10-26 battle init fixed (read this first)

- **`PlayerAttributes.Init` NRE resolved.** The null collection was
  `Blueprint.BaseRangedDamageType`; `DamageType..ctor` (`0xBB0B70`) tail-calls
  `HashSet<string>..ctor` (`0x12A9D94`), so the stack showed
  `HashSet..ctor <- PlayerAttributes.Init`. `Tags` was a red herring.
- Fix: non-null `base_damage` / `base_ranged_damage` /
  `baseRangedDamageType` in every blueprint and character, plus a
  `bumblebee_cin_dotm` blueprint alias. See `docs/battle_started.md`.
- `[RUN]` No NRE; `BattleArbiterMainState`, `_fighters[2]`, player
  `PlayerHitReactState`, enemy `PlayerAttackState`. Player HP 1.0 (HPMax 1050),
  enemy 1000; the hit-react loop does not finish, so no death/resolve/rewards.
- `/matches/match-loaded` is not sent for `quests_fight`; whether it is
  PvP-only is open.
- Q3: Act 4 I/II bosses filled from the wiki; 81/90 boss ids, 9 Starscream
  gaps. R2.1 client formula decoded (`spec/rating_formula.md`).
- Smoke now records `battle_checks` and open xfails for `match_loaded`,
  `fight_started`, `resolve_match`, `returned_to_map`.

## 2026-10-25 breakthrough (read this first)"""
if marker not in s:
    raise SystemExit("marker missing")
s = s.replace(marker, new, 1)
p.write_text(s, encoding="utf-8")
print("updated")
