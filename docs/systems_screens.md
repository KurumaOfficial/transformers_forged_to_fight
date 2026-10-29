# Other systems: first live screens (Step 6, partial)

Status: **screens open without NRE; no real system data yet.** This is the
"view/open first, logic later" stage requested in Step 6.

## Live checks `[RUN]`

| system | action | result | evidence |
|---|---|---|---|
| BASE | tap BASE | base view opens | `work/base2.png` |
| CRYSTALS | tap CRYSTALS | screen opens, `No crystals available.` | `work/crystals.png` |
| OBJECTIVES | tap OBJECTIVES | screen opens, `[0/0] COMPLETE` | `work/obj.png` |
| STORE | tap STORE | locked: `You must be at least LEVEL 2 to access the STORE.` | `work/store.png` |
| FIGHT | tap FIGHT | mode list; STORY open, RAIDS/ARENAS/ALLIANCE locked | `work/home.png` |
| ARENA | mode list | locked (no level/alliance) | `work/home.png` |
| AWAY MISSIONS | not reached from the mode list | open | `work/home.png` |
| PROFILE | top-left Commander / settings only | no separate profile screen observed | `work/home2.png` |

No `/gacha/*`, `/objectives/*` or `/store/*` request was observed while opening
these screens; the current data is local/empty. Do not invent response keys.

## Static/next endpoints

- **CRYSTALS/GACHA:** `GachaManager`/`GachaAPI` classes exist in `dump.cs`;
  direct endpoints were not requested because the screen had no crystals.
  `/autorefresh/gacha/refresh` is the only observed gacha path.
  Next: find the gacha purchase/open endpoint from `GachaAPI` xrefs and add a
  `[ASSUMED]` crystal set, then test opening one.
- **OBJECTIVES:** `/autorefresh/objectives/refresh` is observed; the screen
  uses local objective data from the account/login response. Next: find
  `Objective` JSON paths and add one real wiki goal.
- **STORE:** `/autorefresh/gamestore/refresh` is observed; the screen is
  level-locked at level 2. Next: raise a test account to level 2 or set the
  lock, then add item data.
- **BASE:** `/base/active` works; pathData renders. Next: inspect building
  actions and level locks.
- **ARENA/RAIDS/ALLIANCE:** client-side level/alliance locks; not independent
  of the blocked base/PvP systems.
- **PROFILE:** no separate screen/endpoint captured; do not guess the KABAM
  account/login options.

## Fidelity

These are **view-only** wins. No rewards, purchases, objectives or building
actions are implemented. The store is blocked by the level lock; the arena by
the level/alliance lock.
