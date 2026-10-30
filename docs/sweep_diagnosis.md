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

## S1 completed: 59/59

`[RUN]` `work/sweep_bots59.py` finished all 5 pages:

```
count 59
popup_error 59 (dark transition frame; metric false positive)
info_error 0
nre 0
pages [0,1,2,3,4]
```

Page hashes changed, but the page screenshots `tests/sweep/page_01..04.png`
show the **same first 12 cards** (`Windblade..Tantrum`). The hash change is
a transition/popup artifact, not proof of pagination. The BOTS grid is a
**vertical scroll**; the horizontal-swipe sweep does not visit the other
cards. Therefore `info_error=0` for 59 rows is **not** proof of 59 distinct
bots. Fix: scroll down with `input swipe 1200 900 1200 300 400`, capture the
new rows, and rerun. The old 59/59 report is historical, not coverage
evidence. Result file: `tests/sweep/sweep_59.json`.

## Metric flakiness after a fresh restart

`[RUN]` After a force-stop/restart, the first two cards produced
`popup_error=False` (the popup screenshot was larger) while the 59/59 run had
`popup_error=True` for every card. `info_error` stayed `False` and `nre=0` in
both. The popup flag is a **timing/transition** metric, not a stable error
signal. Keep INFO/NRE as the real checks; if a popup is required, add a
UI-state assertion instead of the 150 KB threshold.


## 2026-10-30 vertical rerun `[RUN]`

Changed the page action to `input swipe 1200 900 1200 300 400`. The page
screenshots now differ: page 2 shows Sunstreaker/Soundwave/Soundblaster/
Slipstream/Skywarp/Sideswipe, page 3 shows Shockwave/Sharkticon/Scorponok/
Rodimus/Rhinox/Ratchet, etc.

- 59 rows, 5 pages.
- `info_error`: **2** (cards 1 and 2 on page 0), not 0.
- `nre`: **0**.
- `popup_error`: 55 (transition metric).
- Starscream is still not among the 59 cards, although the server roster has
  60 entries; the client list does not show the added entry.

So the valid BOTS metric is **57/59 detail screens opened**, 0 NRE. The old
59/59 clean claim is retired.


## 2026-10-30 fresh nightly rerun `[RUN]`

A fresh nightly run after a force-stop/restart produced **59/59**
`info_error=False`, **0 NRE**, with the same vertical scroll. The earlier
2 info errors were transient page-0 popup timing, not a stable failure. The
valid metric is **59/59 detail screens opened, 0 NRE** for this run; the old
horizontal-swipe 59/59 remains invalid as a pagination proof.
