# Rating / stat UI check (Step 5)

Status: **UI wiring works; catalog values are placeholders, so the wiki
comparison fails for most bots.** This is a data-fidelity gap, not an NRE.

## Live checks `[RUN]`

| bot | screen | live values | evidence |
|---|---|---|---|
| Windblade | bot details | LVL 1/10, RANK 1/5, HP 826, ATK 102, rating 300 | `tests/smoke/10b_bot_info.png` |
| Bumblebee | prefight | rating 100, HP 1050/1050, ATK 115 | `work/wheel.png` |
| Sideswipe | prefight | rating 200, HP 1050/1050, ATK 115 | `work/wheel.png` |
| BOTS roster | list | every visible bot shows rating 300 | `work/roster.png` (battle view was open when captured; list values were seen earlier in `work/hm.png`/`work/lochome2.png`) |

## Wiki values `[WIKI]`

Star-1 infobox values (`data/wiki/bots.json`):

| bot | HP | ATK | max rating |
|---|---:|---:|---:|
| Windblade | 826 | 102 | 264 |
| Sideswipe | 826 | 106 | 271 |
| Optimus Prime | 1,066 | 97 | 267 |
| Rhinox | 951 | 81 | 256 |
| Wheeljack | 855 | 82 | 265 |

Rank/level 1/1 rows (same pages):

| bot | HP | ATK | rating |
|---|---:|---:|---:|
| Windblade | 5,160 | 498 | 1,381 |
| Sideswipe | 5,160 | 520 | 1,426 |
| Optimus Prime | 6,240 | 444 | 1,393 |
| Bumblebee | 4,860 | 444 | 1,353 |

## Result

- Windblade's live HP/ATK (826/102) equal the **star-1 infobox**, not the
  rank/level 1/1 table (5,160/498). Its live rating is 300, wiki 264.
- Bumblebee and Sideswipe live at 1050/115, far below the wiki 1/1 rows
  (4,860/444 and 5,160/520). These are the server's placeholder formula:
  `hp = 800 + rank*200 + level*50`, `atk = 80 + rank*30 + level*5`.
- The BOTS list rating is a flat 300 for the visible page, so it is not the
  wiki rating and not the client formula output for every bot.

Conclusion: Step 5.1/5.2 cannot be marked as matching wiki. The UI path and
the attribute plumbing are verified, but the catalog needs real per-bot
rank/level/star data. Until then, treat all displayed stats/ratings except
Windblade's HP/ATK as `[ASSUMED]` placeholders.
