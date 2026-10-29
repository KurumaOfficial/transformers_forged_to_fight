# Bot release dates from the saved wiki infoboxes (Step 4)

Source: `data/wiki/bots.json`, `infobox.Release Date` (44/44 bots have the
field). APK date: **2022-07-26**. A date after that is a post-APK content
candidate; it is not proof that the 9.2.0 client can load the bot.

- non-Launch dates parsed: **31**
- `Launch`: **13**
- unknown/unparsed: **0**
- post-APK candidates: **5**

## Post-APK candidates

| bot | release date (raw) | parsed |
|---|---|---|
| Sunstreaker | July 27, 2022 (update)August 11, 2022 (Bot) | 2022-07-27 |
| Soundblaster/Tactician | September 15th, 2022 | 2022-09-15 |
| Chromia | May 10, 2023 (Netflix) | 2023-05-10 |
| Dead End | May 10, 2023 | 2023-05-10 |
| Soundblaster | May 10, 2023 | 2023-05-10 |

## All bots

| bot | release date (raw) | parsed | post-APK |
|---|---|---|---|
| Arcee | Launch |  |  |
| Barricade | Launch |  |  |
| Bludgeon | Launch |  |  |
| Bonecrusher | Launch |  |  |
| Ironhide (ROTF) | Launch |  |  |
| Mirage | Launch |  |  |
| Motormaster | Launch |  |  |
| Optimus Prime | Launch |  |  |
| Optimus Prime (MV1) | Launch |  |  |
| Rhinox | Launch |  |  |
| Sideswipe | Launch |  |  |
| Ultra Magnus | Launch |  |  |
| Windblade | Launch |  |  |
| Mixmaster | April 6, 2017 | 2017-04-06 |  |
| Waspinator | April 20, 2017 | 2017-04-20 |  |
| Prowl | May 18, 2017 | 2017-05-18 |  |
| Drift | June 15, 2017 | 2017-06-15 |  |
| Hot Rod | June 29, 2017 | 2017-06-29 |  |
| Megatron (ROTF) | July 13, 2017 | 2017-07-13 |  |
| Shockwave | August 10, 2017 | 2017-08-10 |  |
| Starscream | August 24, 2017 | 2017-08-24 |  |
| Ramjet | September 21, 2017 | 2017-09-21 |  |
| Galvatron | October 5, 2017 | 2017-10-05 |  |
| Megatron | November 30, 2017 | 2017-11-30 |  |
| Bumblebee | December 21th, 2017 | 2017-12-21 |  |
| Hound | February 8th, 2018 | 2018-02-08 |  |
| Jazz | June 7, 2018 | 2018-06-07 |  |
| Tantrum | July 13, 2018 | 2018-07-13 |  |
| Wheeljack | August 9, 2018 | 2018-08-09 |  |
| Scorponok | November 1, 2018 | 2018-11-01 |  |
| Jetfire | December 7, 2018 | 2018-12-07 |  |
| Thundercracker | April 18, 2019 | 2019-04-18 |  |
| Nemesis Prime | July 11, 2019 | 2019-07-11 |  |
| Necrotronus | April 2nd, 2020 | 2020-04-02 |  |
| Cliffjumper | April 29, 2021 | 2021-04-29 |  |
| Skywarp | February 24, 2022 | 2022-02-24 |  |
| Ironhide | March 31, 2022|heavy=Melee | 2022-03-31 |  |
| Slipstream | May 19, 2022 | 2022-05-19 |  |
| Rodimus Prime | June 23, 2022 | 2022-06-23 |  |
| Sunstreaker | July 27, 2022 (update)August 11, 2022 (Bot) | 2022-07-27 | yes |
| Soundblaster/Tactician | September 15th, 2022 | 2022-09-15 | yes |
| Chromia | May 10, 2023 (Netflix) | 2023-05-10 | yes |
| Dead End | May 10, 2023 | 2023-05-10 | yes |
| Soundblaster | May 10, 2023 | 2023-05-10 | yes |

## What this changes

- **Starscream** has `August 24, 2017`: the bot is pre-APK, so the
  "Starscream is post-APK" claim is **not supported by the infobox**. The
  9 missing boss ids/pack are a separate mapping gap, not a release-date
  gap.
- **Sunstreaker** (`July 27, 2022 (update)`, `August 11, 2022 (Bot)`) is
  the clearest post-APK bot.
- **Soundblaster/Tactician** has `September 15th, 2022`; the base
  Soundblaster page says `May 10, 2023`, which is the Netflix-era page.
- **Chromia and Dead End** say `May 10, 2023`, i.e. after the 2022-07-26
  APK and after the 2023-01-13 shutdown; they are not in the 9.2.0 pack.
- Missions/events still need the same per-page treatment; their saved
  revision dates are not release dates. `docs/content_timeline.md` has the
  current partial list.
