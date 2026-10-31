
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
