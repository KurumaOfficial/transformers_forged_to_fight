# InterfaceInjector registry (78 interfaces)

Generated from the live runtime registry by `work/dump_injector_names.py`;
names resolved through `Il2CppTypeDefinition.nameIndex` -> `global-metadata.dat`.
Live tag at HomeFlow/prefight: **`tform`**. `Get<T>` has a `default` fallback
(see `docs/prefight_flow.md`).

| # | interface | implementations (tag -> class) | persistent | screen / subsystem | stub status |
|---|---|---|---|---|---|
| 0 | `IAdsProvider` | tform -> TFormIronSourceAdsModel; default -> IronSourceAdsModel | yes (ads) | ads / offers / reward video | persistent; native IronSource; server only autorefresh/ads |
| 1 | `IGachaLimits` | default -> GachaLimitClient |  | gacha | no dedicated stub data; screen not verified |
| 2 | `IAllianceHelpOverlayData` | default -> AllianceHelpOverlayModel |  | alliance help overlay | no dedicated stub data; screen not verified |
| 3 | `IDialogueOverlayData` | default -> DialogueOverayModel |  | dialogue overlay | no dedicated stub data; screen not verified |
| 4 | `IAveBattleGroupInfoModel` | default -> AVEBattleGroupInfoModel |  | Ave battle group | no dedicated stub data; screen not verified |
| 5 | `IArenaRequirementsPopupModel` | default -> ArenaRequirementsPopupModel |  | arena requirements popup | no dedicated stub data; screen not verified |
| 6 | `IArenaRequirementsPopupCallbacks` | default -> ArenaRequirementsPopupCallbacks |  | arena requirements popup | no dedicated stub data; screen not verified |
| 7 | `IArenaRewardsPopupModel` | default -> ArenaRewardsPopupModel |  | arena rewards | no dedicated stub data; screen not verified |
| 8 | `IArenaRewardsPopupCallbacks` | default -> ArenaRewardsPopupCallbacks |  | arena rewards | no dedicated stub data; screen not verified |
| 9 | `IAwayTeamPopupModel` | default -> AwayTeamPopupModel |  | away team | no dedicated stub data; screen not verified |
| 10 | `IBaseEditBuildingPopupData` | default -> BaseEditBuildingPopupModel |  | base edit building | no dedicated stub data; screen not verified |
| 11 | `IBaseEditNodePopupData` | default -> BaseEditNodePopupModel |  | base edit node | no dedicated stub data; screen not verified |
| 12 | `IBaseGachaPopupData` | default -> BaseGachaPopupModel |  | base gacha | no dedicated stub data; screen not verified |
| 13 | `IBuildingSelectPopupData` | default -> BuildingSelectPopupModel |  | building select | no dedicated stub data; screen not verified |
| 14 | `IChampionItemUseConfirmationModel` | default -> ChampionItemUseConfirmationModel |  | item use confirmation | no dedicated stub data; screen not verified |
| 15 | `IDailyLoginModel` | default -> DailyLoginModel |  | daily login | no dedicated stub data; screen not verified |
| 16 | `IDailyLoginCallbacks` | default -> DailyLoginCallbacks |  | daily login | no dedicated stub data; screen not verified |
| 17 | `IDailyRewardPopupData` | default -> DailyRewardPopupData |  | daily reward | no dedicated stub data; screen not verified |
| 18 | `IDefenderSelectPopupData` | default -> DefenderSelectPopupModel |  | defender select | no dedicated stub data; screen not verified |
| 19 | `IEnergySummaryPopupData` | default -> EnergySummaryPopupModel |  | energy summary | no dedicated stub data; screen not verified |
| 20 | `IPaymentCardPurchasedPopupModel` | default -> PaymentCardPurchasedPopupModel |  | payment card | no dedicated stub data; screen not verified |
| 21 | `IFightResultsPopupModel` | default -> FightResultsPopupModel |  | fight results | no dedicated stub data; screen not verified |
| 22 | `IFightResultsCallbacks` | default -> FightResultsCallbacks |  | fight results | no dedicated stub data; screen not verified |
| 23 | `IFlashSaleDataProvider` | default -> FlashSaleModel |  | flash sale | no dedicated stub data; screen not verified |
| 24 | `IHeroConsumablesModel` | default -> HeroConsumablesData |  | hero consumables | no dedicated stub data; screen not verified |
| 25 | `IHeroConsumablesCallbacks` | default -> HeroConsumablesCallbacks |  | hero consumables | no dedicated stub data; screen not verified |
| 26 | `IHowToAvePopupData` | default -> HowToAvePopupModel |  | Ave how-to | no dedicated stub data; screen not verified |
| 27 | `IInventoryItemPopupData` | default -> InventoryItemPopupModel |  | inventory item | no dedicated stub data; screen not verified |
| 28 | `IItemOverrideWarningPopupData` | default -> ItemOverrideWarningPopupData |  | item override | no dedicated stub data; screen not verified |
| 29 | `IItemUseChooseChampionModel` | default -> ItemUseChooseChampionModel |  | item use champion | no dedicated stub data; screen not verified |
| 30 | `IItemUseSelectPopupData` | default -> ItemUseSelectPopupModel |  | item use select | no dedicated stub data; screen not verified |
| 31 | `IKabamLoginIncentivePopupData` | default -> KabamLoginIncentivePopupData |  | login incentive | no dedicated stub data; screen not verified |
| 32 | `ILoginRewardsModel` | default -> LoginRewardsPopupModel |  | login rewards | no dedicated stub data; screen not verified |
| 33 | `ILoginRewardsCallbacks` | default -> LoginRewardsCallbacks |  | login rewards | no dedicated stub data; screen not verified |
| 34 | `IMissionTeamSelectWarningPopupData` | default -> MissionTeamSelectWarningPopupData |  | mission team select warning | no dedicated stub data; screen not verified |
| 35 | `INamePopupData` | default -> NamePopupModel |  | name popup | no dedicated stub data; screen not verified |
| 36 | `IPVPRaidOpponentReviewData` | default -> PVPRaidOpponentReviewData |  | PvP raid opponent review | no dedicated stub data; screen not verified |
| 37 | `IPVPRaidReportDetailsData` | default -> PVPRaidReportDetailsData |  | PvP raid report | no dedicated stub data; screen not verified |
| 38 | `IPaymentCardsPopupModel` | default -> PaymentCardsPopupModel |  | payment cards | no dedicated stub data; screen not verified |
| 39 | `IPlayerProfileDataProvider` | default -> PlayerProfileModel |  | player profile | screen opens empty/redirect; data not implemented |
| 40 | `IQuestDetailsData` | default -> QuestDetailsModel |  | quest details | quest UI; stub partially covers |
| 41 | `IQuitArenaPopupModel` | default -> QuitArenaPopupModel |  | quit arena | no dedicated stub data; screen not verified |
| 42 | `IQuitArenaPopupCallbacks` | default -> QuitArenaPopupCallbacks |  | quit arena | no dedicated stub data; screen not verified |
| 43 | `IResourceSummaryPopupData` | default -> ResourceSummaryPopupModel |  | resource summary | no dedicated stub data; screen not verified |
| 44 | `ISoloEventsPopupData` | default -> SoloEventsPopupModel |  | solo events | no dedicated stub data; screen not verified |
| 45 | `ISummonerBoostsPopupData` | default -> SummonerBoostsPopupData |  | summoner boosts | no dedicated stub data; screen not verified |
| 46 | `IUseItemPopupData` | default -> UseItemPopupDefaultData |  | use item | no dedicated stub data; screen not verified |
| 47 | `IUseItemsPopupCallbacks` | default -> UseItemPopupDefaultCallbacks |  | use item | no dedicated stub data; screen not verified |
| 48 | `IAVEBattleGroupSelectionModel` | default -> AVEBattlegroupSelectionModel |  | Ave battle group selection | no dedicated stub data; screen not verified |
| 49 | `IAllianceNavScreenData` | default -> AllianceNavScreenModel |  | alliance nav | no dedicated stub data; screen not verified |
| 50 | `IAveHistoryScreenModel` | default -> AveHistoryScreenModel |  | Ave history | no dedicated stub data; screen not verified |
| 51 | `IAveLandingScreenModel` | default -> AveLandingScreenModel |  | Ave landing | no dedicated stub data; screen not verified |
| 52 | `IAveResultsScreenModel` | default -> AveResultsScreenModel |  | Ave results | no dedicated stub data; screen not verified |
| 53 | `IBuildingDetailsScreenData` | default -> BuildingDetailsScreenData |  | building details | no dedicated stub data; screen not verified |
| 54 | `IEditTeamData` | default -> EditTeamModel |  | edit squad | quest UI; stub partially covers |
| 55 | `IEditTeamCallbacks` | default -> EditTeamCallbacks |  | edit squad | quest UI; stub partially covers |
| 56 | `IFightLandingData` | default -> FightLandingModel |  | fight landing | no dedicated stub data; screen not verified |
| 57 | `GachaRevealDataProvider` | default -> GachaRevealModel |  | gacha reveal | no dedicated stub data; screen not verified |
| 58 | `IGoalsModel` | default -> GoalsModel |  | objectives / goals | screen opens empty/redirect; data not implemented |
| 59 | `IBaseLeaderboardModel` | default -> BaseLeaderboardModel |  | base leaderboard | no dedicated stub data; screen not verified |
| 60 | `IMasteriesScreenData` | default -> MasteriesScreenData |  | masteries | no dedicated stub data; screen not verified |
| 61 | `IPVPArenaResultsScreenModel` | default -> PVPArenaResultsScreenModel |  | PvP arena results | no dedicated stub data; screen not verified |
| 62 | `IPVPMatchSeriesScreenModel` | default -> PVPMatchSeriesScreenModel |  | PvP match series | no dedicated stub data; screen not verified |
| 63 | `IPVPMatchSeriesScreenCallbacks` | default -> PVPMatchSeriesScreenCallbacks |  | PvP match series | no dedicated stub data; screen not verified |
| 64 | `IPVPScreenCallbacks` | default -> PVPScreenCallbacks |  | PvP screen | no dedicated stub data; screen not verified |
| 65 | `IPVPScreenModel` | default -> PVPScreenModel |  | PvP screen | no dedicated stub data; screen not verified |
| 66 | `IPVPRaidResultsData` | default -> PVPRaidResultsData |  | PvP raid results | no dedicated stub data; screen not verified |
| 67 | `IPVPRaidSelectDataProvider` | default -> PVPRaidSelectDataProvider |  | PvP raid select | no dedicated stub data; screen not verified |
| 68 | `IPVPReportData` | default -> PVPReportData |  | PvP report | no dedicated stub data; screen not verified |
| 69 | `IPrefightDataProvider` | default -> PrefightScreenData |  | prefight (SELECT YOUR BOT) | **FIXED 2026-10-25**: entry 69 default-only works; enemy-key data bug fixed; battle init still blocked |
| 70 | `IQuestResultsDataProvider` | default -> QuestResultsScreenModel |  | quest results | no dedicated stub data; screen not verified |
| 71 | `IQuestResultsCallbacks` | default -> QuestResultsCallbacks |  | quest results | no dedicated stub data; screen not verified |
| 72 | `IQuestSelectModel` | default -> QuestSelectData |  | quest select | quest UI; stub partially covers |
| 73 | `ISettingsScreenDataProvider` | default -> SettingsScreenModel |  | settings | screen opens empty/redirect; data not implemented |
| 74 | `IMissionTeamSelect` | default -> MissionTeamSelectData |  | mission team select | no dedicated stub data; screen not verified |
| 75 | `ITeamSelectModel` | default -> TeamSelectModel |  | team select | no dedicated stub data; screen not verified |
| 76 | `ITeamSelectCallbacks` | default -> TeamSelectCallbacks |  | team select | no dedicated stub data; screen not verified |
| 77 | `IUpgradeScreenModelBase` | default -> UpgradeScreenData |  | upgrade screen | no dedicated stub data; screen not verified |

## I2: IAdsProvider / IronSourceAdsModel

- `IAdsProvider` is the only persistent interface (`_persistentInterfaces` count 1),
  value `TFormIronSourceAdsModel` (tform).
- `IronSourceAdsModel` fields: `appKey`, `_Listeners`, `_initialized`, `_enabled`,
  `_OnAdComplete`, `_rewardState`, `_timeout`; methods `IsEnabled`, `Disable`,
  `Enable`, `IsSupported`, `Initialize`, `ShowRewarded` etc. [STATIC]
- `TFormIronSourceAdsModel` overrides `IsEnabled`/`IsSupported` (`0x10D8078`, `0x10D813C`).
- Observed server calls: `/autorefresh/ads/refresh` only (stub returns `{}`); no
  ad-network HTTP request was observed. The native IronSource SDK is not initialized
  by the stub, so ads are not a source of extra server requests. [RUN]

## Which interfaces block which screens

- `IPrefightDataProvider` (69): blocks FIGHT/prefight.
- `IPlayerProfileDataProvider` (39): profile popup; current top-left account icon
  opens KABAM ACCOUNT?/LOGIN OPTIONS instead, so profile is not reached.
- `ISettingsScreenDataProvider` (73): settings screen; not reached yet.
- `IGoalsModel` (58): OBJECTIVES opens empty `[0/0] COMPLETE`.
- `IQuestSelectModel` (72) / `IQuestDetailsData` (40): quest list/detail work with the
  current stub; deeper data still missing.
- All other interfaces are for screens/subsystems outside the current battle slice.
