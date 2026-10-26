# Battle started — 2026-10-26

Status: **`PlayerAttributes.Init` NRE is fixed.** The client now enters the
fight scene, spawns both fighters, and runs `BattleArbiterMainState`. No
`/matches/match-loaded` or `/matches/resolve-match` request was observed for
this quest fight.

## Fix

`[STATIC]` `DamageType..ctor(List<string>)` (`0xBB0B70`) tail-branches to
`HashSet<string>..ctor(IEnumerable<string>)` (`0x12A9D94`). The list comes from
`BCGBlueprintBase.BaseRangedDamageType` and was null for both Bumblebee and
Sideswipe (`work/probe_fightdata.py`, `BaseRangedDamageType ptr=None`).

`[RUN]` The server catalog now gives every blueprint and character a non-null
`base_damage` and `base_ranged_damage` (plus `baseRangedDamageType`). A
`bumblebee_cin_dotm` blueprint alias was added because `HeroData.Create` logs
`blueprint 'bumblebee_cin_dotm' does not exist in BCG data`.

After the fix:

```
[RUN] no ArgumentNullException in logcat
[RUN] BattleArbiter._state = BattleArbiterMainState
[RUN] BattleArbiter._fighters = PlayerController[2]
      [0] Id=0, Attributes._blueprint = TFBCGBlueprintBase bumblebee_cin_dotm_2
      [1] Id=1, Attributes._blueprint = TFBCGBlueprintBase sideswipe_gs
[RUN] fighter 0 state = PlayerHitReactState
[RUN] fighter 1 state = PlayerNewHeavyAttackState
```

The player's `BCGAttributeData.HP` reads `1.0` while `HPMax` is `1050`; the
enemy reads `1000.0`. The fight runs for tens of seconds with the enemy
attacking and the player in hit-react, but the player does not reach 0 HP and
the battle does not resolve. This is the **next** blocker (state/animation or
minimum-HP data), not the init NRE.

## Requests

`[RUN]` The only match request for the run is:

```
POST /matches/activate-match/quests_fight
{"hero":"bumblebee_cin_dotm_2","qid":"story_act1_ch4_m2","battleId":"battle1"}
```

No `/matches/match-loaded` and no `/matches/resolve-match`. For quest fights
the client may not use `match-loaded` at all; the smoke `battle_checks` now
records both as open xfails.

## Evidence

- `work/probe_fightdata.py` — FightData/Fighters and blueprint tags/damage
  lists.
- `work/dump_battlearbiter.py` — `_fighters`, `_state`, static arrays.
- `work/after_fix2.png` — live battle screenshot (outside git).
- `tests/smoke/latest.json` — smoke PASS, `prefight_detected=true`.
- `server/requests.jsonl` — activate-match request.

## Next

1. Add a `--keep-open` smoke mode (or a small run script) so the battle is not
   killed by the smoke cleanup; leave the fight running and record damage,
   death, resolve-match, `FightResultsData`, rewards and return to map.
2. If the hit-react loop is stuck, inspect `PlayerController`/`MoveSequencer`
   animation-event waits and the `min_hp` stat; capture a short screen
   recording.
3. Re-run the 30 null-safe variants only if a new null collection appears; the
   root cause is now known.

## ODR/loading blocker (discovered after the first MainState)

`[RUN]` `WindowManager.Instance.windowStacks` on the running battle shows on
top: `FuseLoadingScreen`, `PopupFader`, `BusyBlocker`, `FullScreenBlocker`,
`FuseODRBlocker`; `HudScreen` is behind them. Logcat repeatedly shows
`PlayCore ... AssetPackServiceImpl` and
`BIND_ASSET_MODULE_SERVICE ... com.android.vending not found`. The emulator has
no Play Store, so the Play Asset Delivery fetch cannot complete. The battle
logic runs behind the blocker (fighters, MoveSet, Idle/HitReact/Attack states)
but input is blocked and the loading screen stays.

This is a **hard asset blocker**, not a data-schema blocker. Options:

1. obtain the original ODR asset packs (Play Asset Delivery) and serve/install
   them locally;
2. find a supported non-ODR/debug data path in the client to skip the FuseODR
   check (without patching the client);
3. accept the battle-logic evidence (fighters spawned, states cycle) and
   continue with server/data tracks.

The NRE fix remains valid and is the important unblock. Do not claim a
playable fight until the ODR blocker is resolved.
