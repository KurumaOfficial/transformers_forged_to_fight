# BOTS sweep diagnosis (Step 2.1/2.2)

## `popup_error=True` is not an NRE

`[RUN]` First 12 cards (page 0) and page 1/2 samples:

| file | bytes | mean RGB | interpretation |
|---|---:|---|---|
| `bot_00_popup.png` | 125,622 | (22,31,41) | dark transition/loading frame |
| `bot_00_info.png` | 1,045,169 | (14,14,17) | details/INFO screen loaded |
| `bot_01_popup.png` | 128,707 | (22,32,41) | transition |
| `bot_01_info.png` | 1,069,963 | (14,18,22) | details/INFO loaded |

All sampled cards: `popup_error=True` (popup screenshot <150 KB),
`info_error=False` (INFO screen >150 KB), `nre=0`. The INFO screen opens, so
the card/details flow is not broken; the popup metric is measuring a dark
transition frame, not a failed popup. `popup_error` should not be reported as
a crash. If a popup is expected, the threshold/state needs a UI-specific check.

## Pagination

`work/sweep_bots59.py` swipes left across the grid after 12 cards. `[RUN]`
page hashes changed: `44950fc2…` -> `c9981a2e…` -> `899ad084…`, so pagination
works. A full 59/59 run is in progress; it is slow (~3 s per card) and the
global blocker/navigation can interrupt it. The current evidence is **12/59**
from `sweep_12.json`; the new script writes `sweep_59.json` with all pages and
`blocked_by_odr`.

## ODR note

The global `FuseODRBlocker` was open on `HeroesScreen` with no downloads
(`docs/odr_flow.md`). It can intercept taps even when the details screen
underneath is valid. `blocked_by_odr` in `sweep_bots59.py` is a snapshot at
start; it may be false if the blocker closes/opens during the sweep. Always
check both the JSON flag and the screenshots.

## Next

1. If `sweep_59.json` reaches 59, report success/popup/info/NRE per index.
2. If not, stop at the page where the hash stops changing or the app returns
   to Home; record the blocker/window state.
3. Keep `popup_error` as a separate transition metric, not an NRE/failure.
