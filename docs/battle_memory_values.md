# Battle memory values vs stub (Step 1.8)

`[RUN]` Live `PlayerAttributes._attributes` (`BCGAttributeData`) after the
init fix, `story_act1_ch4_m2`, Bumblebee vs Sideswipe:

| field | player | enemy | stub `getBaseHeroData` |
|---|---:|---:|---|
| HPMax | 1050 | 1050 | 1050 |
| Attack | 115 | 115 | 115 |
| Armor | 0.0 | 0.0 | 0.0 |
| CritChance | 0.0 | 0.0 | 0.1 |
| CritDamage | 0.0 | 0.0 | 1.5 |
| BlockProficiency | 0.0 | 0.0 | 0.5 |
| ManaGain | 0.0 | 0.0 | 1.0 |
| HeroRating | 100 | 200 | rating 107 (player) / 162 (enemy) |
| HeroRatingHP | 50 | 105 | 50 / 105 |
| HeroRatingAttack | 50 | 57 | 50 / 57 |

## What the client actually consumes

- **HPMax and Attack** from the server are applied (1050/115 match the
  `800 + rank*200 + level*50` / `80 + rank*30 + level*5` formula).
- **HeroRatingHP/HeroRatingAttack** roughly follow the server `rating_hp` /
  `rating_attack` values (player 50/50, enemy 105/57); `HeroRating` itself is
  not the server sum (100 vs 107, 200 vs 162), so the client recomputes or
  clamps it.
- **Armor/CritChance/CritDamage/BlockProficiency/ManaGain** are **0** in live
  `BCGAttributeData` although the flat `getBaseHeroData` response sends
  0/0.1/1.5/0.5/1.0. The client is not applying those flat fields (it likely
  recalculates base attributes locally via `clientCalculateHeroBaseAttributes`
  or uses the `attributeData`/catalog curves). Do not assume the flat response
  controls these stats.
- The live `CritChance` was 0 even though the nested `attributeData` sent 0.1;
  the client's local calculation wins.

## Consequence

For a faithful fight, the server must supply the fields the client **actually**
uses (`max_hp`, `attack`, rating split) and the client recalculates the rest
from the catalog curves/forge/rank. The current `getBaseHeroData` flat
Armor/Crit/Block/Mana fields are inert for this path; they should not be used
as the source of truth in FIDELITY.

The player's `BCGAttributeData.HP` read 1.0 while `HPMax` was 1050; this is a
current-HP/sentinel value, not the max. The actual `ResourceAttribute` is
private/encrypted (`FastSafeFloat`/`SafeValue`), so a direct current-HP read
needs the public getter or a debug build; it is not used to claim full HP.

## Evidence

- `work/probe_fightdata.py` output in `docs/evidence/battle_init/fightflow.txt`.
- `docs/battle_init_fix.md`, `docs/battle_started.md`.
- Live values copied from the 18:14–18:24 process; no client patch.
