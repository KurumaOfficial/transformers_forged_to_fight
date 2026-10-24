# Window / popup screen table

Generated from `dump.cs` (`Window`, `TFormWindow`, `Popup`, test windows) by
`work/build_screen_table.py`. Provider and endpoint columns are filled only
where the client or server actually exercised them; `untested` is honest,
not a claim of a defect.

Total classes: **180**.

| screen | base | provider | endpoints | status in our environment |
|---|---|---|---|---|
| `AllianceScreen` | Window | IAllianceNavScreenData (52) | /alliance | locked (red lock) [RUN] |
| `ArenaRequirementsPopup` | TFormWindow, PopupFader.Listener | IArenaRequirementsPopupModel/Callbacks | /pvp | locked at level 0 [RUN] |
| `BaseLeaderboardScreen` | Window | IBaseLeaderboardModel (59) | /base | not reached [STATIC] |
| `BusyBlocker` | Window | none | - | blocker [RUN] |
| `CriticalError` | Window | none | - | error overlay [RUN] |
| `EditTeamScreen` | TFormWindow | IEditTeamData (57), IEditTeamCallbacks | /bcg/setSavedTeam | opens; NRE in EditTeamModel.RefreshHeros if active team is empty [RUN] |
| `FullScreenBlocker` | Window | none | - | blocker [RUN] |
| `FuseODRBlocker` | Window | none | - | ODR blocker [RUN] |
| `FuseStoreScreen` | Window | none | /store | locked (level) [RUN] |
| `GachaPurchaseScreen` | Window | none | /gacha | locked/empty [RUN] |
| `GlobalEventHandler` | Window | none | - | global input [RUN] |
| `GoalsScreen` | TFormWindow | IGoalsModel (58) | /objectives | open; empty [0/0] because stub payload is empty [RUN] |
| `HeroesScreen` | Window | none (BCGHelper.GetHeroes) | /bcg/getLoginData (cached) | open, 59 cards [RUN] |
| `InventoryScreen` | Window | none | /inventory | locked (red lock) at level 0 [RUN] |
| `KabamLoginWindow` | Window | none | /auth/* | account popup; KABAM/GOOGLE [RUN] |
| `LoginOptionsPopup` | Window, PopupFader.Listener | none | /invites/privacy | login options [RUN] |
| `LoginScreen` | Window | none | /auth/* | login flow [RUN] |
| `MasteryFullScreenOverlay` | Window, ISkillTreeListener | IMasteriesScreenData (60) | /quests/mastery | not reached [STATIC] |
| `PVPArenaResultsScreen` | TFormWindow | IPVPArenaResultsScreenModel (61) | /pvp | locked [RUN] |
| `PVPRaidSelectScreen` | Window | IPVPRaidSelectDataProvider (66) | /pvp | locked [RUN] |
| `PlayerProfilePopup` | TFormWindow, PopupFader.Listener | IPlayerProfileDataProvider (39) | /userprofile/ | not reachable from the current home UI [RUN] |
| `PreFightScreen` | Window | IPrefightDataProvider (69) | /matches/activate-match | open; FIGHT works; battle-init NRE [RUN] |
| `QuestDetailsPopup` | TFormWindow, PopupFader.Listener | IQuestDetailsData (40) | /quests/quest-detail | open [RUN] |
| `QuestResultsScreen` | TFormWindow | IQuestResultsDataProvider (70), IQuestResultsCallbacks | /quests/battlecomplete, /quests/fightlost | not reached (battle does not finish) [STATIC] |
| `QuestSelect` | TFormWindow | IQuestSelectModel (72) | /quests/quest-list | open; 66+24 mission list [RUN] |
| `QuestboardHud` | Window, IGameboardHud | none | /quests/quest-movedir | open; HUD stacked below PreFightScreen [RUN] |
| `SettingsScreen` | TFormWindow | ISettingsScreenDataProvider (73) | - | open; ACCOUNT/SOUND/STORY work [RUN] |
| `SoloEventsPopup` | TFormWindow | ISoloEventsPopupData (47) | /events | not reached [STATIC] |
| `TeamSelect` | TFormWindow | ITeamSelectModel (75), ITeamSelectCallbacks | /bcg/setSavedTeam | open from quest team selection [RUN] |
| `UIScreenBackground` | Window | none | - | background [RUN] |
| `UpgradeActorScreen` | Window | IUpgradeScreenModelBase (77) | /bcg/getHeroXPCurve | opens; NRE in SetXPCurve when curve payload is empty [RUN] |

## Untested windows

The remaining classes are listed in `data/screens.json`. They include test
screens (`*TestScreen`), alliance/PvP/base/store popups and overlays that are
locked or not reachable at account level 0. No provider was observed for them
in our runs.
