# TuningManager keys (Step 7.3)

`TuningManager` (`dump.cs` TypeDef 7467) is a generic key/value subsystem:
`IDictionary _data` at +0x20, `GetString/GetInt/GetBool/GetFloat`
(0x15DC204/0x15DC21C/0x15DC230/0x15DC248). It has no statically declared key
fields; keys are string call-site arguments and the `/tuning` response.

## Verified keys (`[CLIENT]`)

| key | type | value |
|---|---|---:|
| `heroRatingAttackWeight` | float | 1.0 |
| `heroRatingMaxHPWeight` | float | 0.2 |
| `sigLvlMax` | int | 100 |
| `ratingPrecision` | int/float | 0/1.0 (client defaults 0; formula uses 1.0) |

`server/data/tuning_client_defaults.json` and `tuning_data.json` carry these.

## Why the full list is not here

- The keys are not fields; they are literal strings at each `Get*` call site,
  often passed through a static `TuningAI`/`TuningManager` helper.
- A complete list needs an ARM64 xref of every `GetInt/GetFloat/GetBool/GetString`
  call and its preceding literal; that is a larger static extraction than the
  current session.
- Guessing keys or values would change combat/economy silently.

## Next

1. Disassemble each `Get*` call site, resolve the first argument string literal,
   and record `key/type/default`.
2. Compare with the `/tuning` payload and the `TuningAI` asset.
3. Add only keys observed at a call site; mark defaults `[CLIENT]`.

`docs/tuning_keys.md` remains partial; do not treat
`tuning_client_defaults.json` as a full table.
