# Tuning keys (Step 6.1)

Status: **structural table generated from `dump.cs`; values are client
defaults unless `/tuning` supplies them.**

## Mechanic (negative xref result)

`[STATIC]` `TuningManager.GetString/GetInt/GetBool/GetFloat`
(`0x15DC204`/`0x15DC21C`/`0x15DC230`/`0x15DC248`) are simple
`Dot.*` wrappers over `_data+0x20`. A scan of every `BL`/`B` in
`libil2cpp.so` found **no direct callers** of those four methods; they
are not used with literal keys in this build.

`[STATIC]` `Tuning.LoadTuningData` (`0x14233EC`) walks the public fields
of the `Tuning` component and calls `TuningManager.Apply`
(`0x15DAEB0`/`0x15DBFEC`) with the field name. `TuningGameplay` uses
`DeserializeData` (`0x1425540`). The effective key namespace is therefore
the **field names below**, not a separate string table.

`[RUN]` Live `Tuning` ODR flags (read-only, 2026-10-27):

| key | live value | meaning |
|---|---:|---|
| `ODRForceDownloadAll` | 0 | do not force all ODR downloads |
| `ODRForceDownloadAllPreTutorial` | 0 | |
| `ODRShowProgressMB` | 1 | show MB progress |
| `ODRShowTimeEstimate` | 1 | show time estimate |
| `ODRForceDownloadAssetListPreTutorial` | 0 | |
| `ODRAllowNative` | 1 | native ODR path allowed |

These are **data flags**. Do not change them to bypass the blocker without
explicit consent; `ODRAllowNative=0` is only a hypothesis, not applied.

## Current `/tuning` payload (verified)

`server/data/tuning_data.json` sends one object:

```json
{
  "heroRatingAttackWeight": 1.0,
  "heroRatingMaxHPWeight": 0.2,
  "sigLvlMax": 100,
  "ratingPrecision": 0
}
```

These four are read by the BCG layer/rating path; they are not fields of
the `Tuning` component. Keep them in `/tuning` until a call-site proves a
different source.

## Tuning (`/tuning` via reflection `Apply`)

| key | type | offset |
|---|---|---:|
| `PathingColorMode` | `Tuning.ePATHING_COLOR_MODE` | 0x18 |
| `AdsEnabled` | `bool` | 0x1C |
| `AllianceKillPVPHelp` | `bool` | 0x1D |
| `AllianceKillPVEHelp` | `bool` | 0x1E |
| `AllianceKillRequestJoins` | `bool` | 0x1F |
| `AllianceKillSearch` | `bool` | 0x20 |
| `AllianceKillSendInvites` | `bool` | 0x21 |
| `AllianceKillTreasury` | `bool` | 0x22 |
| `AllianceKillDonationSC` | `bool` | 0x23 |
| `AllianceKillDonationSC_HC` | `bool` | 0x24 |
| `AllianceKillDonationPVP` | `bool` | 0x25 |
| `AllianceKillDonationPVP_HC` | `bool` | 0x26 |
| `AllianceKillDonationAP` | `bool` | 0x27 |
| `AllianceKillDonationAP_HC` | `bool` | 0x28 |
| `AllianceMaxDonation` | `long` | 0x30 |
| `AllianceTagColor` | `Color` | 0x38 |
| `KillAnnouncementsWidget` | `bool` | 0x48 |
| `KillAnnouncementOpenOnStart` | `bool` | 0x49 |
| `KillAVEAccess` | `bool` | 0x4A |
| `KillAVEStart` | `bool` | 0x4B |
| `ShowGlobalNodeConnections` | `bool` | 0x4C |
| `ReshowAVEFinishedMessageTimer` | `int` | 0x50 |
| `AVESuggestedDifficultyMultiplier` | `float` | 0x54 |
| `AwayTeamSuccessPercentTier0` | `float` | 0x58 |
| `AwayTeamSuccessPercentTier1` | `float` | 0x5C |
| `AwayTeamSuccessPercentTier2` | `float` | 0x60 |
| `AwayTeamSuccessPercentTier3` | `float` | 0x64 |
| `AwayTeamSuccessPercentTier4` | `float` | 0x68 |
| `BaseCrystal01` | `string` | 0x70 |
| `BaseCrystal02` | `string` | 0x78 |
| `BaseCrystal03` | `string` | 0x80 |
| `BaseCrystalFTE` | `string` | 0x88 |
| `ShowFTERewardPrompt` | `bool` | 0x90 |
| `BaseKillBuildingLevels` | `bool` | 0x91 |
| `AwayTeamBuilding` | `string` | 0x98 |
| `BattleCentreBuilding` | `string` | 0xA0 |
| `AllianceHelpBuilding` | `string` | 0xA8 |
| `AwayTeamBuildingLevel` | `string` | 0xB0 |
| `BattleCentreBuildingLevel` | `string` | 0xB8 |
| `AllianceHelpBuildingLevel` | `string` | 0xC0 |
| `KillBoosts` | `bool` | 0xC8 |
| `ShowUncollectedBots` | `bool` | 0xC9 |
| `CooldownStoreItemString` | `string` | 0xD0 |
| `CooldownTimeResourceActionPopup` | `int` | 0xD8 |
| `DefenderSelectGetMoreThreshold` | `int` | 0xDC |
| `AllowDisableDialogueOnReplay` | `bool` | 0xE0 |
| `RecommendedPIThreshold` | `float` | 0xE4 |
| `DefaultMaxTeamSize` | `int` | 0xE8 |
| `EditTeamBackWarningEncounteredLimit` | `int` | 0xEC |
| `EventMilestoneSegmentCap` | `int` | 0xF0 |
| `EventsKill` | `bool` | 0xF4 |
| `EventsCriticalTimeRemaining` | `int` | 0xF8 |
| `EventsWarningTimeRemaining` | `int` | 0xFC |
| `FightKillPlayerLogs` | `bool` | 0x100 |
| `FightKillStatModLogs` | `bool` | 0x101 |
| `KillWatchFight` | `bool` | 0x102 |
| `ClassDisadvantageSelectionBias` | `float` | 0x104 |
| `PrefightHpWeight` | `float` | 0x108 |
| `PrefightAttBonusWeight` | `float` | 0x10C |
| `PrefightAttPenaltyWeight` | `float` | 0x110 |
| `AllowSleepInFightResults` | `bool` | 0x114 |
| `BuffCharacterBase` | `string` | 0x118 |
| `FlashOfferTimeRemainingCritical` | `int` | 0x120 |
| `HomeFlowScreensToDump` | `string` | 0x128 |
| `QuestFlowScreensToDump` | `string` | 0x130 |
| `MinNumHeroes` | `int` | 0x138 |
| `MinNumMods` | `int` | 0x13C |
| `ForgeKill` | `bool` | 0x140 |
| `MaxSmartSelectOver` | `int` | 0x144 |
| `ForgeHeroesRarityWarningMinimum` | `int` | 0x148 |
| `StartingPlayerBot` | `string` | 0x150 |
| `StartingOpponentBot` | `string` | 0x158 |
| `StartingArena` | `string` | 0x160 |
| `StartingArenaTOD` | `int` | 0x168 |
| `FTELightAttacks` | `int` | 0x16C |
| `FTEMediumAttacks` | `int` | 0x170 |
| `FTEBlockingTime` | `float` | 0x174 |
| `FTEGachaSet` | `string` | 0x178 |
| `FTEGachaToken` | `string` | 0x180 |
| `DisableReplayForQuests` | `int` | 0x188 |
| `Chapter1MissionsToHighlight` | `int` | 0x18C |
| `KillHighlightFightUntilQuest` | `bool` | 0x190 |
| `HighlightFightUntilQuestComplete` | `int` | 0x194 |
| `DisableHighlightFightDuringFTE` | `string[]` | 0x198 |
| `AlwaysDisableHighlightOnScreens` | `string[]` | 0x1A0 |
| `HiddenTopBarFTEStates` | `string[]` | 0x1A8 |
| `RankUpResourceQuantity` | `int` | 0x1B0 |
| `RankUpSparkQuantity` | `int` | 0x1B4 |
| `AllowPreloadOfFTEFight` | `bool` | 0x1B8 |
| `AllowPreloadOfFTEFightUIQualityMin` | `int` | 0x1BC |
| `DisableBaseBuildingRevealUntilLevel` | `int` | 0x1C0 |
| `DisableBaseTimersUntilLevel` | `int` | 0x1C4 |
| `CrystalsToShowTutorialFor` | `string` | 0x1C8 |
| `PreloadFTEGrindor` | `bool` | 0x1D0 |
| `PreloadFTEBumbleBee` | `bool` | 0x1D1 |
| `FTECustomLoadingWaitForTap` | `bool` | 0x1D2 |
| `FTESkipInitialCutScene` | `bool` | 0x1D3 |
| `GachaMaxSpinTime` | `float` | 0x1D4 |
| `GachaPrizeSpinnerLastItemDelay` | `float` | 0x1D8 |
| `GachaQuestionMarkDisplayTime` | `float` | 0x1DC |
| `GachaSpinnerEndTopPrizeChance` | `float` | 0x1E0 |
| `GachaCrystalSpeedFactor` | `float` | 0x1E4 |
| `GachaSpinnerSlowDeviceCarrouselMax` | `int` | 0x1E8 |
| `GachaSpinnerCarouselCount` | `int` | 0x1EC |
| `GachaSpinnerItemDisplayTime` | `float` | 0x1F0 |
| `GachaSpinnerFeaturedRatio` | `float` | 0x1F4 |
| `GachaSetsToDisplay` | `string` | 0x1F8 |
| `GachaFTESetToDisplay` | `string` | 0x200 |
| `PremiumItemRarity` | `int` | 0x208 |
| `ShowUpgradeButtonTypes` | `string` | 0x210 |
| `HideNoShardCrystals` | `bool` | 0x218 |
| `HideCrystalsIfEmpty` | `bool` | 0x219 |
| `HideShardsIfEmpty` | `bool` | 0x21A |
| `HideSpecialIfEmpty` | `bool` | 0x21B |
| `ShowEnergonCostOnPurchaseItem` | `bool` | 0x21C |
| `MaxGachaPerDay` | `int` | 0x220 |
| `LimitType` | `int` | 0x224 |
| `LimitGachaPerDay` | `bool` | 0x228 |
| `GachaLimitTimezoneOffset` | `int` | 0x22C |
| `GoalsEnabled` | `bool` | 0x230 |
| `GoalsScreenShowObjectiveCompleteFullScreenText` | `bool` | 0x231 |
| `PaymentsCriticalTime` | `int` | 0x234 |
| `PaymentsWarningTime` | `int` | 0x238 |
| `MasteriesKill` | `bool` | 0x23C |
| `MasteriesMinimumLevelForVisibility` | `int` | 0x240 |
| `UseHeroClassOnMaxSelect` | `bool` | 0x244 |
| `UseEveryClassOnMaxSelect` | `bool` | 0x245 |
| `UseGoldLimitOnMaxSelect` | `bool` | 0x246 |
| `PrimeUserProfilesForPVPRaid` | `bool` | 0x247 |
| `SynergyBonusInactiveAlpha` | `float` | 0x248 |
| `CatFragFullScreenCelebrationIntermissionTime` | `float` | 0x24C |
| `MaxDisplayableHeroRarity` | `int` | 0x250 |
| `MaximumTileCountForGetMore` | `int` | 0x254 |
| `MinimumUserLevelForHeroesScreenFeaturedTile` | `int` | 0x258 |
| `MaxDisplayablePVPRaidOpponents` | `int` | 0x25C |
| `MaxDisplayableIsoCatalystTier` | `int` | 0x260 |
| `MinRarityForSpecialFrameEffect` | `int` | 0x264 |
| `AttackedWarningMedalCountLimit` | `int` | 0x268 |
| `TeamSelectUnusedBotsWarningEncounteredLimit` | `int` | 0x26C |
| `ShowUseItemInActionPopup` | `bool` | 0x270 |
| `RarityToDisplaySpecialBackground` | `int` | 0x274 |
| `DisplayServerLabel` | `bool` | 0x278 |
| `PvpRewardsDisplayStash` | `bool` | 0x279 |
| `MiscInfoCount` | `int` | 0x27C |
| `MaxTimesOfDay` | `int` | 0x280 |
| `EventsToRemember` | `int` | 0x284 |
| `SalesToRemember` | `int` | 0x288 |
| `PayoutsToRemember` | `int` | 0x28C |
| `GoalCollectionsToRemember` | `int` | 0x290 |
| `RepeatingGoalCollectionsToRemember` | `int` | 0x294 |
| `FightWarningHealthPct` | `int` | 0x298 |
| `DisplayServerTag` | `bool` | 0x29C |
| `KillBotTransform` | `bool` | 0x29D |
| `AllowDeviceSleepAfterSeconds` | `int` | 0x2A0 |
| `nextClaimWarning` | `int` | 0x2A4 |
| `OverriddenPortraitPaths` | `string[]` | 0x2A8 |
| `RigidbodyBosscard` | `bool` | 0x2B0 |
| `ReverseQuestboardTapNavigation` | `bool` | 0x2B1 |
| `EnableQuestboardInfoMode` | `bool` | 0x2B2 |
| `ShowPushNotificationPromptUntilLevel` | `int` | 0x2B4 |
| `MaxLeaderboardRank` | `int` | 0x2B8 |
| `RecommendUpgradeQuestIndex` | `int` | 0x2BC |
| `RecommendUpgradeBotLevel` | `int` | 0x2C0 |
| `PlayersFirstBot` | `string` | 0x2C8 |
| `KillStrategicMapMode` | `bool` | 0x2D0 |
| `ShowStratgicMapModeOnFirstPlay` | `bool` | 0x2D1 |
| `ExploredPathsOnly` | `bool` | 0x2D2 |
| `ShowFightButton` | `bool` | 0x2D3 |
| `OverrideQuestboardTimeOfDay` | `bool` | 0x2D4 |
| `QuestboardTimeOfDayOverride` | `int` | 0x2D8 |
| `OverrideQuestboardTheme` | `bool` | 0x2DC |
| `QuestboardThemeOverride` | `string` | 0x2E0 |
| `QuestboardProxyLODMed` | `int` | 0x2E8 |
| `QuestboardProxyLODHigh` | `int` | 0x2EC |
| `QuestboardProxyDistanceLow` | `int` | 0x2F0 |
| `QuestboardProxyDistanceMed` | `int` | 0x2F4 |
| `QuestboardProxyDistanceHigh` | `int` | 0x2F8 |
| `DefaultPopupQueue` | `string` | 0x300 |
| `ShowStatus` | `bool` | 0x308 |
| `ShowLoginRewards` | `bool` | 0x309 |
| `ShowResource` | `bool` | 0x30A |
| `ShowRateUs` | `bool` | 0x30B |
| `ShowGift` | `bool` | 0x30C |
| `ShowMPC` | `bool` | 0x30D |
| `PVPRaidMedalStat` | `string` | 0x310 |
| `PVPRaidKill` | `bool` | 0x318 |
| `UseSingleOpponentPrefab` | `bool` | 0x319 |
| `AutoAdvanceOnExpire` | `bool` | 0x31A |
| `UseItemCostForRefresh` | `bool` | 0x31B |
| `AllowSoftExitOfMatchExpiry` | `bool` | 0x31C |
| `AutoAdvanceRaidOpponentDisplayTime` | `int` | 0x320 |
| `BaseRelicPedestalScale` | `float` | 0x324 |
| `BaseRelicScale` | `float` | 0x328 |
| `BaseRelicYPosition` | `float` | 0x32C |
| `QuestRelicPedestalScale` | `float` | 0x330 |
| `QuestRelicScale` | `float` | 0x334 |
| `QuestRelicYPosition` | `float` | 0x338 |
| `KillModuleTowerSounds` | `bool` | 0x33C |
| `SocialKillChat` | `bool` | 0x33D |
| `SocialKillChatGlobal` | `bool` | 0x33E |
| `SocialKillChatAlliance` | `bool` | 0x33F |
| `SocialKillFriends` | `bool` | 0x340 |
| `SocialKillFriendsContacts` | `bool` | 0x341 |
| `SocialKillFriendsRequests` | `bool` | 0x342 |
| `SocialKillFriendsSearch` | `bool` | 0x343 |
| `SocialKillAddFriends` | `bool` | 0x344 |
| `SocialKillRemoveFriends` | `bool` | 0x345 |
| `SocialKillPrivateMessages` | `bool` | 0x346 |
| `KillSortByIsoValue` | `bool` | 0x347 |
| `KillSortByGoldValue` | `bool` | 0x348 |
| `PushEvolveReadyBotsUp` | `bool` | 0x349 |
| `SystemMessageDuration` | `float` | 0x34C |
| `SystemMessagePollingInterval` | `float` | 0x350 |
| `KillTelemetryCutscene` | `bool` | 0x354 |
| `KillTelemetryDialog` | `bool` | 0x355 |
| `KillTelemetryDetailsInfo` | `bool` | 0x356 |
| `KillTelemetryMotd` | `bool` | 0x357 |
| `KillTelemetryScreenOpen_AllianceHelp` | `bool` | 0x358 |
| `KillTelemetryScreenOpen_Forge` | `bool` | 0x359 |
| `KillTelemetryScreenOpen_GachaPurchase` | `bool` | 0x35A |
| `KillTelemetryScreenOpen_GachaReveal` | `bool` | 0x35B |
| `KillTelemetryScreenOpen_RaidReport` | `bool` | 0x35C |
| `KillTelemetryScreenOpen_SoloEvents` | `bool` | 0x35D |
| `KillTelemetryTab_Store` | `bool` | 0x35E |
| `KillTelemetryTab_UpgradeRankTab` | `bool` | 0x35F |
| `ODRForceDownloadAll` | `bool` | 0x360 |
| `ODRForceDownloadAllPreTutorial` | `bool` | 0x361 |
| `ODRShowProgressMB` | `bool` | 0x362 |
| `ODRShowTimeEstimate` | `bool` | 0x363 |
| `ODRForceDownloadAssetListPreTutorial` | `bool` | 0x364 |
| `ODRAllowNative` | `bool` | 0x365 |
| `ODRAssetListForForcedDownload` | `string` | 0x368 |
| `DisplayStashWithOreOption` | `int` | 0x370 |
| `DisplayStashItemsInOreSelect` | `bool` | 0x374 |
| `MoveDistanceToDismissTopBarOnBaseboard` | `int` | 0x378 |
| `TopBarDisplayModeTuneableSetting` | `int` | 0x37C |
| `tuningColours` | `Tuning.TuningColour[]` | 0x380 |
| `KillPushManagerQueue` | `bool` | 0x388 |
| `PushManagerQueueSize` | `int` | 0x38C |
| `currencyShowLevels` | `Tuning.CurrencyShowLevel[]` | 0x390 |
| `UseKrashNextSession` | `bool` | 0x398 |
| `SocialHubStatesJSON` | `string` | 0x3A0 |

_fields: 242_

## TuningGameplay (`DeserializeData`)

| key | type | offset |
|---|---|---:|
| `ManaPerSpecial` | `SafeFloat` | 0x18 |
| `ArmorRatingConstant` | `SafeFloat` | 0x20 |
| `CritRatingConstant_A` | `SafeFloat` | 0x28 |
| `DefenderManaModifier` | `SafeFloat` | 0x30 |
| `DefenderManaBlockedModifier` | `SafeFloat` | 0x38 |
| `AttackChainResetTime` | `SafeFloat` | 0x40 |
| `EvadeMeleeSpeed` | `SafeFloat` | 0x48 |
| `MeleeRangeMod` | `SafeFloat` | 0x50 |
| `DefaultAnimatorScale` | `float` | 0x58 |
| `UnstoppableKnockbackFactor` | `float` | 0x5C |
| `GrenadeGravity` | `float` | 0x60 |
| `ProjecticleMinMeleeKnockback` | `float` | 0x64 |
| `DefaultProjectileSpeed` | `float` | 0x68 |
| `MinProjectileSpeed` | `SafeFloat` | 0x70 |
| `MaxProjectileSpeed` | `SafeFloat` | 0x78 |
| `MaxQueuedActionTime` | `SafeFloat` | 0x80 |
| `MinVisibleHitStreak` | `int` | 0x88 |
| `MinSpecialGlowQuality` | `PerformanceInfo.eUI_QUALITY` | 0x8C |
| `GlobalStatMods` | `string[]` | 0x90 |
| `PlayerDashCurve` | `VelocityCurve` | 0x98 |
| `PlayerDodgeCurve` | `VelocityCurve` | 0xB0 |
| `PlayerSidestepCurve` | `VelocityCurve` | 0xC8 |
| `TutMaxTotalPerFight` | `int` | 0xE0 |
| `TutMaxUniquePerFight` | `int` | 0xE4 |
| `TutMinTimeBetween` | `float` | 0xE8 |
| `TutAttacksToTrigger` | `string` | 0xF0 |
| `SlowAnimStartLvl` | `SafeInt` | 0xF8 |
| `SlowAnimEndLvl` | `SafeInt` | 0x100 |
| `AOESelfEdgeColor` | `Color` | 0x108 |
| `AOEOpponentEdgeColor` | `Color` | 0x118 |

_fields: 30_

## TuningClassColors

| key | type | offset |
|---|---|---:|
| `colorSets` | `TuningClassColors.ColorSet[]` | 0x18 |
| `isogramColorSets` | `TuningClassColors.ColorSet[]` | 0x20 |
| `heroConsumableSets` | `TuningClassColors.ColorSet[]` | 0x28 |
| `isogramGenericColor` | `Color` | 0x30 |

_fields: 4_

## TuningLevelLocks

| key | type | offset |
|---|---|---:|
| `levelLocks` | `TuningLevelLocks.LevelLockData[]` | 0x18 |
| `tempLevelLocks` | `IDictionary` | 0x20 |

_fields: 2_

## TuningRarityColors

| key | type | offset |
|---|---|---:|
| `AwayTeamCommonColor` | `Color` | 0x18 |
| `AwayTeamUncommonColor` | `Color` | 0x28 |
| `AwayTeamRareColor` | `Color` | 0x38 |
| `AwayTeamEpicColor` | `Color` | 0x48 |
| `AwayTeamLegendaryColor` | `Color` | 0x58 |
| `colorSets` | `TuningRarityColors.ColorSet[]` | 0x68 |

_fields: 6_

## TuningSynergyBonusColors

| key | type | offset |
|---|---|---:|
| `BackgroundActiveColor` | `Color` | 0x18 |
| `BackgroundInActiveColor` | `Color` | 0x28 |
| `IconActiveColor` | `Color` | 0x38 |
| `IconInActiveColor` | `Color` | 0x48 |
| `BackgroundSelectedActiveColor` | `Color` | 0x58 |
| `BackgroundSelectedInActiveColor` | `Color` | 0x68 |
| `IconSelectedActiveColor` | `Color` | 0x78 |
| `IconSelectedInActiveColor` | `Color` | 0x88 |

_fields: 8_

## TuningWebLinks

| key | type | offset |
|---|---|---:|
| `webLinksData` | `TuningWebLinks.WebLinksData` | 0x18 |

_fields: 1_

## Not done

- Per-field consumers (which code reads each `Tuning` field) are not all
  xref'd; the field list is complete, but the consumer map is partial.
- `TuningGameplay.DeserializeData` key suffixes are not fully decoded.
- `TuningManager.Apply` reflection behavior is documented, not every
  applied field value.
