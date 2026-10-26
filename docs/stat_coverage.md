# R1 stat coverage (Step 5.1)

37 WIKI/table, 22 ASSUMED.

| client | class | HP | ATK | uncertainty | anchor/method |
|---|---|---:|---:|---:|---|
| blaster_gs_leader2016 | Tech | 874.0 | 82.0 | 25.0% | no stat table, no star-1; class median prior |
| bumblebee_cin_dotm | Tactician | 1066.0 | 97.0 | 25.0% | no stat table, no star-1; class median prior |
| cheetor_bw_transmetal | Scout | 826.0 | 106.0 | 25.0% | no stat table, no star-1; class median prior |
| cyclonus_gs_uw06 | Tactician | 1066.0 | 97.0 | 25.0% | no stat table, no star-1; class median prior |
| dinobot_bw_kabam | Tactician | 1066.0 | 97.0 | 25.0% | no stat table, no star-1; class median prior |
| dirge_gs_deluxe2008 | Warrior | 912.5 | 97.5 | 25.0% | no stat table, no star-1; class median prior |
| grimlock_gs_mp08 | Brawler | 1076.0 | 103.0 | 25.0% | no stat table, no star-1; class median prior |
| grindor_cin_rotf | Brawler | 1076.0 | 103.0 | 25.0% | no stat table, no star-1; class median prior |
| kickback_gs_kabam | Scout | 826.0 | 106.0 | 25.0% | no stat table, no star-1; class median prior |
| megatronus_gs_kabam | Demolitions | 1009.0 | 79.5 | 25.0% | no stat table, no star-1; class median prior |
| optimusprimal_bw_mp32 | Brawler | 1076.0 | 103.0 | 25.0% | no stat table, no star-1; class median prior |
| ratchet_gs_kabam | Tech | 874.0 | 82.0 | 25.0% | no stat table, no star-1; class median prior |
| rodimusprime_gs_mp09 | Tactician | 1066.2 | 91.9 | 10.0% | no stat table/star-1; star-3 anchor (4768 HP/322 ATK) x global star ratio |
| sharkticon_gs_brawler | Warrior • Scout • Tech • Demolitions • Tactician • Brawler | 951.0 | 89.0 | 25.0% | no stat table, no star-1; class median prior |
| sharkticon_gs_demolition | Warrior • Scout • Tech • Demolitions • Tactician • Brawler | 951.0 | 89.0 | 25.0% | no stat table, no star-1; class median prior |
| sharkticon_gs_kabam | Warrior • Scout • Tech • Demolitions • Tactician • Brawler | 951.0 | 89.0 | 25.0% | no stat table, no star-1; class median prior |
| sharkticon_gs_scout | Warrior • Scout • Tech • Demolitions • Tactician • Brawler | 951.0 | 89.0 | 25.0% | no stat table, no star-1; class median prior |
| sharkticon_gs_tactician | Warrior • Scout • Tech • Demolitions • Tactician • Brawler | 951.0 | 89.0 | 25.0% | no stat table, no star-1; class median prior |
| sharkticon_gs_tech | Warrior • Scout • Tech • Demolitions • Tactician • Brawler | 951.0 | 89.0 | 25.0% | no stat table, no star-1; class median prior |
| sharkticon_gs_warrior | Warrior • Scout • Tech • Demolitions • Tactician • Brawler | 951.0 | 89.0 | 25.0% | no stat table, no star-1; class median prior |
| soundwave_gs | Tech | 874.0 | 82.0 | 25.0% | no stat table, no star-1; class median prior |
| sunstreaker_gs_deluxe2008 | Brawler | 1066.2 | 109.9 | 10.0% | no stat table/star-1; star-3 anchor (4768 HP/385 ATK) x global star ratio |

## Missing for [DERIVED]

- No wiki stat table and no star-1 HP/ATK for 20 bots; only class/rarity is known.
- Rodimus Prime and Sunstreaker have star-3 HP/ATK; used as an anchor with the global star ratio (10% uncertainty).
- The 20 class-median priors use the median of the 37 table bots in the same class; 25% uncertainty.
- A live UI check is blocked by `FuseODRBlocker`; these are data priors, not UI-verified values.
