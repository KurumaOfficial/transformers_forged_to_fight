# Live Tuning values (Step 1.2)

Source: `Tuning.Instance` live memory, pid 22912. Read-only.
Zero/empty fields are marked; custom structs/arrays show `n/a` and need
a separate decoder. Do not fill a field blindly just because it is zero.

| field | type | offset | live value | zero/empty |
|---|---|---:|---|---|
| `PathingColorMode` | `Tuning.ePATHING_COLOR_MODE` | 0x18 | n/a | **yes** |
| `AdsEnabled` | `bool` | 0x1C | True |  |
| `AllianceKillPVPHelp` | `bool` | 0x1D | False | **yes** |
| `AllianceKillPVEHelp` | `bool` | 0x1E | False | **yes** |
| `AllianceKillRequestJoins` | `bool` | 0x1F | False | **yes** |
| `AllianceKillSearch` | `bool` | 0x20 | False | **yes** |
| `AllianceKillSendInvites` | `bool` | 0x21 | False | **yes** |
| `AllianceKillTreasury` | `bool` | 0x22 | False | **yes** |
| `AllianceKillDonationSC` | `bool` | 0x23 | False | **yes** |
| `AllianceKillDonationSC_HC` | `bool` | 0x24 | False | **yes** |
| `AllianceKillDonationPVP` | `bool` | 0x25 | False | **yes** |
| `AllianceKillDonationPVP_HC` | `bool` | 0x26 | False | **yes** |
| `AllianceKillDonationAP` | `bool` | 0x27 | False | **yes** |
| `AllianceKillDonationAP_HC` | `bool` | 0x28 | False | **yes** |
| `AllianceMaxDonation` | `long` | 0x30 | 100000 |  |
| `AllianceTagColor` | `Color` | 0x38 | n/a | **yes** |
| `KillAnnouncementsWidget` | `bool` | 0x48 | False | **yes** |
| `KillAnnouncementOpenOnStart` | `bool` | 0x49 | False | **yes** |
| `KillAVEAccess` | `bool` | 0x4A | False | **yes** |
| `KillAVEStart` | `bool` | 0x4B | False | **yes** |
| `ShowGlobalNodeConnections` | `bool` | 0x4C | True |  |
| `ReshowAVEFinishedMessageTimer` | `int` | 0x50 | 60 |  |
| `AVESuggestedDifficultyMultiplier` | `float` | 0x54 | 1.0 |  |
| `AwayTeamSuccessPercentTier0` | `float` | 0x58 | 0.0 | **yes** |
| `AwayTeamSuccessPercentTier1` | `float` | 0x5C | 0.5 |  |
| `AwayTeamSuccessPercentTier2` | `float` | 0x60 | 0.75 |  |
| `AwayTeamSuccessPercentTier3` | `float` | 0x64 | 0.8999999761581421 |  |
| `AwayTeamSuccessPercentTier4` | `float` | 0x68 | 1.0 |  |
| `BaseCrystal01` | `string` | 0x70 | 'free_24hour' |  |
| `BaseCrystal02` | `string` | 0x78 | 'free_4hour' |  |
| `BaseCrystal03` | `string` | 0x80 | 'free_holiday_crystal' |  |
| `BaseCrystalFTE` | `string` | 0x88 | 'bots_fte_2' |  |
| `ShowFTERewardPrompt` | `bool` | 0x90 | False | **yes** |
| `BaseKillBuildingLevels` | `bool` | 0x91 | True |  |
| `AwayTeamBuilding` | `string` | 0x98 | 'xpB1' |  |
| `BattleCentreBuilding` | `string` | 0xA0 | 'xpB2' |  |
| `AllianceHelpBuilding` | `string` | 0xA8 | 'xpB3' |  |
| `AwayTeamBuildingLevel` | `string` | 0xB0 | 'lvlB1' |  |
| `BattleCentreBuildingLevel` | `string` | 0xB8 | 'lvlB2' |  |
| `AllianceHelpBuildingLevel` | `string` | 0xC0 | 'lvlB3' |  |
| `KillBoosts` | `bool` | 0xC8 | False | **yes** |
| `ShowUncollectedBots` | `bool` | 0xC9 | True |  |
| `CooldownStoreItemString` | `string` | 0xD0 | 't{0}_defense_cooldown' |  |
| `CooldownTimeResourceActionPopup` | `int` | 0xD8 | 14400 |  |
| `DefenderSelectGetMoreThreshold` | `int` | 0xDC | 5 |  |
| `AllowDisableDialogueOnReplay` | `bool` | 0xE0 | True |  |
| `RecommendedPIThreshold` | `float` | 0xE4 | 0.9200000166893005 |  |
| `DefaultMaxTeamSize` | `int` | 0xE8 | 5 |  |
| `EditTeamBackWarningEncounteredLimit` | `int` | 0xEC | 5 |  |
| `EventMilestoneSegmentCap` | `int` | 0xF0 | 6 |  |
| `EventsKill` | `bool` | 0xF4 | False | **yes** |
| `EventsCriticalTimeRemaining` | `int` | 0xF8 | 3600 |  |
| `EventsWarningTimeRemaining` | `int` | 0xFC | 7200 |  |
| `FightKillPlayerLogs` | `bool` | 0x100 | False | **yes** |
| `FightKillStatModLogs` | `bool` | 0x101 | False | **yes** |
| `KillWatchFight` | `bool` | 0x102 | False | **yes** |
| `ClassDisadvantageSelectionBias` | `float` | 0x104 | 0.0 | **yes** |
| `PrefightHpWeight` | `float` | 0x108 | 1.0 |  |
| `PrefightAttBonusWeight` | `float` | 0x10C | 1.0 |  |
| `PrefightAttPenaltyWeight` | `float` | 0x110 | 1.0 |  |
| `AllowSleepInFightResults` | `bool` | 0x114 | True |  |
| `BuffCharacterBase` | `string` | 0x118 | 'z_gen_utl' |  |
| `FlashOfferTimeRemainingCritical` | `int` | 0x120 | 1800 |  |
| `HomeFlowScreensToDump` | `string` | 0x128 | 'ActRewardsSummaryPopup,AwayTeamPopup,BaseGachaPopup,FlashSalePopup,LoginOptionsPopup,ResourceActionPopup,SettingsScreen' |  |
| `QuestFlowScreensToDump` | `string` | 0x130 | 'DialogueOverlay,QuestDetailsPopup' |  |
| `MinNumHeroes` | `int` | 0x138 | 6 |  |
| `MinNumMods` | `int` | 0x13C | 7 |  |
| `ForgeKill` | `bool` | 0x140 | False | **yes** |
| `MaxSmartSelectOver` | `int` | 0x144 | 250 |  |
| `ForgeHeroesRarityWarningMinimum` | `int` | 0x148 | 3 |  |
| `StartingPlayerBot` | `string` | 0x150 | 'fte_optimus_gs_t3' |  |
| `StartingOpponentBot` | `string` | 0x158 | 'fte_stars_gs_t3' |  |
| `StartingArena` | `string` | 0x160 | 'karnak' |  |
| `StartingArenaTOD` | `int` | 0x168 | 0 | **yes** |
| `FTELightAttacks` | `int` | 0x16C | 4 |  |
| `FTEMediumAttacks` | `int` | 0x170 | 2 |  |
| `FTEBlockingTime` | `float` | 0x174 | 2.0 |  |
| `FTEGachaSet` | `string` | 0x178 | 'tutorial' |  |
| `FTEGachaToken` | `string` | 0x180 | 'bots_fte_1' |  |
| `DisableReplayForQuests` | `int` | 0x188 | 4 |  |
| `Chapter1MissionsToHighlight` | `int` | 0x18C | 4 |  |
| `KillHighlightFightUntilQuest` | `bool` | 0x190 | False | **yes** |
| `HighlightFightUntilQuestComplete` | `int` | 0x194 | 4 |  |
| `DisableHighlightFightDuringFTE` | `string[]` | 0x198 | n/a | **yes** |
| `AlwaysDisableHighlightOnScreens` | `string[]` | 0x1A0 | n/a | **yes** |
| `HiddenTopBarFTEStates` | `string[]` | 0x1A8 | n/a | **yes** |
| `RankUpResourceQuantity` | `int` | 0x1B0 | 5000 |  |
| `RankUpSparkQuantity` | `int` | 0x1B4 | 2 |  |
| `AllowPreloadOfFTEFight` | `bool` | 0x1B8 | False | **yes** |
| `AllowPreloadOfFTEFightUIQualityMin` | `int` | 0x1BC | 10 |  |
| `DisableBaseBuildingRevealUntilLevel` | `int` | 0x1C0 | 2 |  |
| `DisableBaseTimersUntilLevel` | `int` | 0x1C4 | 2 |  |
| `CrystalsToShowTutorialFor` | `string` | 0x1C8 | 'bots_t1,bots_t2' |  |
| `PreloadFTEGrindor` | `bool` | 0x1D0 | False | **yes** |
| `PreloadFTEBumbleBee` | `bool` | 0x1D1 | False | **yes** |
| `FTECustomLoadingWaitForTap` | `bool` | 0x1D2 | False | **yes** |
| `FTESkipInitialCutScene` | `bool` | 0x1D3 | False | **yes** |
| `GachaMaxSpinTime` | `float` | 0x1D4 | 25.0 |  |
| `GachaPrizeSpinnerLastItemDelay` | `float` | 0x1D8 | 0.15000000596046448 |  |
| `GachaQuestionMarkDisplayTime` | `float` | 0x1DC | 3.0 |  |
| `GachaSpinnerEndTopPrizeChance` | `float` | 0x1E0 | 0.75 |  |
| `GachaCrystalSpeedFactor` | `float` | 0x1E4 | 10.0 |  |
| `GachaSpinnerSlowDeviceCarrouselMax` | `int` | 0x1E8 | 10 |  |
| `GachaSpinnerCarouselCount` | `int` | 0x1EC | 20 |  |
| `GachaSpinnerItemDisplayTime` | `float` | 0x1F0 | 0.02500000037252903 |  |
| `GachaSpinnerFeaturedRatio` | `float` | 0x1F4 | 0.5 |  |
| `GachaSetsToDisplay` | `string` | 0x1F8 | 'base,events,simple' |  |
| `GachaFTESetToDisplay` | `string` | 0x200 | 'tutorial' |  |
| `PremiumItemRarity` | `int` | 0x208 | 3 |  |
| `ShowUpgradeButtonTypes` | `string` | 0x210 | 'hero,skl,ebp,ebpf,res' |  |
| `HideNoShardCrystals` | `bool` | 0x218 | True |  |
| `HideCrystalsIfEmpty` | `bool` | 0x219 | False | **yes** |
| `HideShardsIfEmpty` | `bool` | 0x21A | False | **yes** |
| `HideSpecialIfEmpty` | `bool` | 0x21B | True |  |
| `ShowEnergonCostOnPurchaseItem` | `bool` | 0x21C | True |  |
| `MaxGachaPerDay` | `int` | 0x220 | 20 |  |
| `LimitType` | `int` | 0x224 | 3 |  |
| `LimitGachaPerDay` | `bool` | 0x228 | False | **yes** |
| `GachaLimitTimezoneOffset` | `int` | 0x22C | 28800 |  |
| `GoalsEnabled` | `bool` | 0x230 | True |  |
| `GoalsScreenShowObjectiveCompleteFullScreenText` | `bool` | 0x231 | False | **yes** |
| `PaymentsCriticalTime` | `int` | 0x234 | 180 |  |
| `PaymentsWarningTime` | `int` | 0x238 | 1800 |  |
| `MasteriesKill` | `bool` | 0x23C | False | **yes** |
| `MasteriesMinimumLevelForVisibility` | `int` | 0x240 | 2 |  |
| `UseHeroClassOnMaxSelect` | `bool` | 0x244 | True |  |
| `UseEveryClassOnMaxSelect` | `bool` | 0x245 | True |  |
| `UseGoldLimitOnMaxSelect` | `bool` | 0x246 | True |  |
| `PrimeUserProfilesForPVPRaid` | `bool` | 0x247 | False | **yes** |
| `SynergyBonusInactiveAlpha` | `float` | 0x248 | 0.6000000238418579 |  |
| `CatFragFullScreenCelebrationIntermissionTime` | `float` | 0x24C | 0.5 |  |
| `MaxDisplayableHeroRarity` | `int` | 0x250 | 4 |  |
| `MaximumTileCountForGetMore` | `int` | 0x254 | 5 |  |
| `MinimumUserLevelForHeroesScreenFeaturedTile` | `int` | 0x258 | 4 |  |
| `MaxDisplayablePVPRaidOpponents` | `int` | 0x25C | 3 |  |
| `MaxDisplayableIsoCatalystTier` | `int` | 0x260 | 9 |  |
| `MinRarityForSpecialFrameEffect` | `int` | 0x264 | 5 |  |
| `AttackedWarningMedalCountLimit` | `int` | 0x268 | 300 |  |
| `TeamSelectUnusedBotsWarningEncounteredLimit` | `int` | 0x26C | 5 |  |
| `ShowUseItemInActionPopup` | `bool` | 0x270 | True |  |
| `RarityToDisplaySpecialBackground` | `int` | 0x274 | 5 |  |
| `DisplayServerLabel` | `bool` | 0x278 | True |  |
| `PvpRewardsDisplayStash` | `bool` | 0x279 | True |  |
| `MiscInfoCount` | `int` | 0x27C | 11 |  |
| `MaxTimesOfDay` | `int` | 0x280 | 3 |  |
| `EventsToRemember` | `int` | 0x284 | 10 |  |
| `SalesToRemember` | `int` | 0x288 | 10 |  |
| `PayoutsToRemember` | `int` | 0x28C | 30 |  |
| `GoalCollectionsToRemember` | `int` | 0x290 | 31 |  |
| `RepeatingGoalCollectionsToRemember` | `int` | 0x294 | 31 |  |
| `FightWarningHealthPct` | `int` | 0x298 | 20 |  |
| `DisplayServerTag` | `bool` | 0x29C | True |  |
| `KillBotTransform` | `bool` | 0x29D | False | **yes** |
| `AllowDeviceSleepAfterSeconds` | `int` | 0x2A0 | 300 |  |
| `nextClaimWarning` | `int` | 0x2A4 | 14400 |  |
| `OverriddenPortraitPaths` | `string[]` | 0x2A8 | n/a | **yes** |
| `RigidbodyBosscard` | `bool` | 0x2B0 | False | **yes** |
| `ReverseQuestboardTapNavigation` | `bool` | 0x2B1 | False | **yes** |
| `EnableQuestboardInfoMode` | `bool` | 0x2B2 | False | **yes** |
| `ShowPushNotificationPromptUntilLevel` | `int` | 0x2B4 | 5 |  |
| `MaxLeaderboardRank` | `int` | 0x2B8 | 200 |  |
| `RecommendUpgradeQuestIndex` | `int` | 0x2BC | 3 |  |
| `RecommendUpgradeBotLevel` | `int` | 0x2C0 | 3 |  |
| `PlayersFirstBot` | `string` | 0x2C8 | 'optimus_gs_t1' |  |
| `KillStrategicMapMode` | `bool` | 0x2D0 | True |  |
| `ShowStratgicMapModeOnFirstPlay` | `bool` | 0x2D1 | False | **yes** |
| `ExploredPathsOnly` | `bool` | 0x2D2 | False | **yes** |
| `ShowFightButton` | `bool` | 0x2D3 | True |  |
| `OverrideQuestboardTimeOfDay` | `bool` | 0x2D4 | False | **yes** |
| `QuestboardTimeOfDayOverride` | `int` | 0x2D8 | 0 | **yes** |
| `OverrideQuestboardTheme` | `bool` | 0x2DC | False | **yes** |
| `QuestboardThemeOverride` | `string` | 0x2E0 | 'primordial' |  |
| `QuestboardProxyLODMed` | `int` | 0x2E8 | 1100 |  |
| `QuestboardProxyLODHigh` | `int` | 0x2EC | 1800 |  |
| `QuestboardProxyDistanceLow` | `int` | 0x2F0 | 200 |  |
| `QuestboardProxyDistanceMed` | `int` | 0x2F4 | 400 |  |
| `QuestboardProxyDistanceHigh` | `int` | 0x2F8 | 600 |  |
| `DefaultPopupQueue` | `string` | 0x300 | 'StatusUpdatePopup,ResourceActionPopup,ClaimGift,FlashSalePopup,RateUsPopup,PaymentCardsPopup,LoginRewardsPopup,DeepLinking' |  |
| `ShowStatus` | `bool` | 0x308 | True |  |
| `ShowLoginRewards` | `bool` | 0x309 | True |  |
| `ShowResource` | `bool` | 0x30A | False | **yes** |
| `ShowRateUs` | `bool` | 0x30B | True |  |
| `ShowGift` | `bool` | 0x30C | True |  |
| `ShowMPC` | `bool` | 0x30D | True |  |
| `PVPRaidMedalStat` | `string` | 0x310 | 'raid_war' |  |
| `PVPRaidKill` | `bool` | 0x318 | False | **yes** |
| `UseSingleOpponentPrefab` | `bool` | 0x319 | False | **yes** |
| `AutoAdvanceOnExpire` | `bool` | 0x31A | False | **yes** |
| `UseItemCostForRefresh` | `bool` | 0x31B | False | **yes** |
| `AllowSoftExitOfMatchExpiry` | `bool` | 0x31C | True |  |
| `AutoAdvanceRaidOpponentDisplayTime` | `int` | 0x320 | 45 |  |
| `BaseRelicPedestalScale` | `float` | 0x324 | 1.7999999523162842 |  |
| `BaseRelicScale` | `float` | 0x328 | 1.2999999523162842 |  |
| `BaseRelicYPosition` | `float` | 0x32C | 0.0 | **yes** |
| `QuestRelicPedestalScale` | `float` | 0x330 | 2.0 |  |
| `QuestRelicScale` | `float` | 0x334 | 2.0 |  |
| `QuestRelicYPosition` | `float` | 0x338 | 0.0 | **yes** |
| `KillModuleTowerSounds` | `bool` | 0x33C | False | **yes** |
| `SocialKillChat` | `bool` | 0x33D | False | **yes** |
| `SocialKillChatGlobal` | `bool` | 0x33E | False | **yes** |
| `SocialKillChatAlliance` | `bool` | 0x33F | False | **yes** |
| `SocialKillFriends` | `bool` | 0x340 | False | **yes** |
| `SocialKillFriendsContacts` | `bool` | 0x341 | False | **yes** |
| `SocialKillFriendsRequests` | `bool` | 0x342 | False | **yes** |
| `SocialKillFriendsSearch` | `bool` | 0x343 | False | **yes** |
| `SocialKillAddFriends` | `bool` | 0x344 | False | **yes** |
| `SocialKillRemoveFriends` | `bool` | 0x345 | False | **yes** |
| `SocialKillPrivateMessages` | `bool` | 0x346 | False | **yes** |
| `KillSortByIsoValue` | `bool` | 0x347 | False | **yes** |
| `KillSortByGoldValue` | `bool` | 0x348 | False | **yes** |
| `PushEvolveReadyBotsUp` | `bool` | 0x349 | False | **yes** |
| `SystemMessageDuration` | `float` | 0x34C | 3.0 |  |
| `SystemMessagePollingInterval` | `float` | 0x350 | 5.0 |  |
| `KillTelemetryCutscene` | `bool` | 0x354 | False | **yes** |
| `KillTelemetryDialog` | `bool` | 0x355 | False | **yes** |
| `KillTelemetryDetailsInfo` | `bool` | 0x356 | False | **yes** |
| `KillTelemetryMotd` | `bool` | 0x357 | False | **yes** |
| `KillTelemetryScreenOpen_AllianceHelp` | `bool` | 0x358 | False | **yes** |
| `KillTelemetryScreenOpen_Forge` | `bool` | 0x359 | False | **yes** |
| `KillTelemetryScreenOpen_GachaPurchase` | `bool` | 0x35A | False | **yes** |
| `KillTelemetryScreenOpen_GachaReveal` | `bool` | 0x35B | False | **yes** |
| `KillTelemetryScreenOpen_RaidReport` | `bool` | 0x35C | False | **yes** |
| `KillTelemetryScreenOpen_SoloEvents` | `bool` | 0x35D | False | **yes** |
| `KillTelemetryTab_Store` | `bool` | 0x35E | False | **yes** |
| `KillTelemetryTab_UpgradeRankTab` | `bool` | 0x35F | False | **yes** |
| `ODRForceDownloadAll` | `bool` | 0x360 | False | **yes** |
| `ODRForceDownloadAllPreTutorial` | `bool` | 0x361 | False | **yes** |
| `ODRShowProgressMB` | `bool` | 0x362 | True |  |
| `ODRShowTimeEstimate` | `bool` | 0x363 | True |  |
| `ODRForceDownloadAssetListPreTutorial` | `bool` | 0x364 | False | **yes** |
| `ODRAllowNative` | `bool` | 0x365 | True |  |
| `ODRAssetListForForcedDownload` | `string` | 0x368 | '' | **yes** |
| `DisplayStashWithOreOption` | `int` | 0x370 | 1 |  |
| `DisplayStashItemsInOreSelect` | `bool` | 0x374 | True |  |
| `MoveDistanceToDismissTopBarOnBaseboard` | `int` | 0x378 | 5 |  |
| `TopBarDisplayModeTuneableSetting` | `int` | 0x37C | 2 |  |
| `tuningColours` | `Tuning.TuningColour[]` | 0x380 | n/a | **yes** |
| `KillPushManagerQueue` | `bool` | 0x388 | False | **yes** |
| `PushManagerQueueSize` | `int` | 0x38C | 64 |  |
| `currencyShowLevels` | `Tuning.CurrencyShowLevel[]` | 0x390 | n/a | **yes** |
| `UseKrashNextSession` | `bool` | 0x398 | False | **yes** |
| `SocialHubStatesJSON` | `string` | 0x3A0 | '' | **yes** |

Zero/empty fields: **95 / 242**.

- `PathingColorMode` (`Tuning.ePATHING_COLOR_MODE`, 0x18)
- `AllianceKillPVPHelp` (`bool`, 0x1D)
- `AllianceKillPVEHelp` (`bool`, 0x1E)
- `AllianceKillRequestJoins` (`bool`, 0x1F)
- `AllianceKillSearch` (`bool`, 0x20)
- `AllianceKillSendInvites` (`bool`, 0x21)
- `AllianceKillTreasury` (`bool`, 0x22)
- `AllianceKillDonationSC` (`bool`, 0x23)
- `AllianceKillDonationSC_HC` (`bool`, 0x24)
- `AllianceKillDonationPVP` (`bool`, 0x25)
- `AllianceKillDonationPVP_HC` (`bool`, 0x26)
- `AllianceKillDonationAP` (`bool`, 0x27)
- `AllianceKillDonationAP_HC` (`bool`, 0x28)
- `AllianceTagColor` (`Color`, 0x38)
- `KillAnnouncementsWidget` (`bool`, 0x48)
- `KillAnnouncementOpenOnStart` (`bool`, 0x49)
- `KillAVEAccess` (`bool`, 0x4A)
- `KillAVEStart` (`bool`, 0x4B)
- `AwayTeamSuccessPercentTier0` (`float`, 0x58)
- `ShowFTERewardPrompt` (`bool`, 0x90)
- `KillBoosts` (`bool`, 0xC8)
- `EventsKill` (`bool`, 0xF4)
- `FightKillPlayerLogs` (`bool`, 0x100)
- `FightKillStatModLogs` (`bool`, 0x101)
- `KillWatchFight` (`bool`, 0x102)
- `ClassDisadvantageSelectionBias` (`float`, 0x104)
- `ForgeKill` (`bool`, 0x140)
- `StartingArenaTOD` (`int`, 0x168)
- `KillHighlightFightUntilQuest` (`bool`, 0x190)
- `DisableHighlightFightDuringFTE` (`string[]`, 0x198)
- `AlwaysDisableHighlightOnScreens` (`string[]`, 0x1A0)
- `HiddenTopBarFTEStates` (`string[]`, 0x1A8)
- `AllowPreloadOfFTEFight` (`bool`, 0x1B8)
- `PreloadFTEGrindor` (`bool`, 0x1D0)
- `PreloadFTEBumbleBee` (`bool`, 0x1D1)
- `FTECustomLoadingWaitForTap` (`bool`, 0x1D2)
- `FTESkipInitialCutScene` (`bool`, 0x1D3)
- `HideCrystalsIfEmpty` (`bool`, 0x219)
- `HideShardsIfEmpty` (`bool`, 0x21A)
- `LimitGachaPerDay` (`bool`, 0x228)
- `GoalsScreenShowObjectiveCompleteFullScreenText` (`bool`, 0x231)
- `MasteriesKill` (`bool`, 0x23C)
- `PrimeUserProfilesForPVPRaid` (`bool`, 0x247)
- `KillBotTransform` (`bool`, 0x29D)
- `OverriddenPortraitPaths` (`string[]`, 0x2A8)
- `RigidbodyBosscard` (`bool`, 0x2B0)
- `ReverseQuestboardTapNavigation` (`bool`, 0x2B1)
- `EnableQuestboardInfoMode` (`bool`, 0x2B2)
- `ShowStratgicMapModeOnFirstPlay` (`bool`, 0x2D1)
- `ExploredPathsOnly` (`bool`, 0x2D2)
- `OverrideQuestboardTimeOfDay` (`bool`, 0x2D4)
- `QuestboardTimeOfDayOverride` (`int`, 0x2D8)
- `OverrideQuestboardTheme` (`bool`, 0x2DC)
- `ShowResource` (`bool`, 0x30A)
- `PVPRaidKill` (`bool`, 0x318)
- `UseSingleOpponentPrefab` (`bool`, 0x319)
- `AutoAdvanceOnExpire` (`bool`, 0x31A)
- `UseItemCostForRefresh` (`bool`, 0x31B)
- `BaseRelicYPosition` (`float`, 0x32C)
- `QuestRelicYPosition` (`float`, 0x338)
- `KillModuleTowerSounds` (`bool`, 0x33C)
- `SocialKillChat` (`bool`, 0x33D)
- `SocialKillChatGlobal` (`bool`, 0x33E)
- `SocialKillChatAlliance` (`bool`, 0x33F)
- `SocialKillFriends` (`bool`, 0x340)
- `SocialKillFriendsContacts` (`bool`, 0x341)
- `SocialKillFriendsRequests` (`bool`, 0x342)
- `SocialKillFriendsSearch` (`bool`, 0x343)
- `SocialKillAddFriends` (`bool`, 0x344)
- `SocialKillRemoveFriends` (`bool`, 0x345)
- `SocialKillPrivateMessages` (`bool`, 0x346)
- `KillSortByIsoValue` (`bool`, 0x347)
- `KillSortByGoldValue` (`bool`, 0x348)
- `PushEvolveReadyBotsUp` (`bool`, 0x349)
- `KillTelemetryCutscene` (`bool`, 0x354)
- `KillTelemetryDialog` (`bool`, 0x355)
- `KillTelemetryDetailsInfo` (`bool`, 0x356)
- `KillTelemetryMotd` (`bool`, 0x357)
- `KillTelemetryScreenOpen_AllianceHelp` (`bool`, 0x358)
- `KillTelemetryScreenOpen_Forge` (`bool`, 0x359)
- `KillTelemetryScreenOpen_GachaPurchase` (`bool`, 0x35A)
- `KillTelemetryScreenOpen_GachaReveal` (`bool`, 0x35B)
- `KillTelemetryScreenOpen_RaidReport` (`bool`, 0x35C)
- `KillTelemetryScreenOpen_SoloEvents` (`bool`, 0x35D)
- `KillTelemetryTab_Store` (`bool`, 0x35E)
- `KillTelemetryTab_UpgradeRankTab` (`bool`, 0x35F)
- `ODRForceDownloadAll` (`bool`, 0x360)
- `ODRForceDownloadAllPreTutorial` (`bool`, 0x361)
- `ODRForceDownloadAssetListPreTutorial` (`bool`, 0x364)
- `ODRAssetListForForcedDownload` (`string`, 0x368)
- `tuningColours` (`Tuning.TuningColour[]`, 0x380)
- `KillPushManagerQueue` (`bool`, 0x388)
- `currencyShowLevels` (`Tuning.CurrencyShowLevel[]`, 0x390)
- `UseKrashNextSession` (`bool`, 0x398)
- `SocialHubStatesJSON` (`string`, 0x3A0)
