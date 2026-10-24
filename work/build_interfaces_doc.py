import json
from pathlib import Path

ROOT = Path(r"C:\Users\gameg\Desktop\TFTF")
d = json.loads((ROOT / "work" / "injector_registry.json").read_text(encoding="utf-8"))

SCREEN = {
    "IAdsProvider": "ads / offers / reward video",
    "IGachaLimits": "gacha",
    "IAllianceHelpOverlayData": "alliance help overlay",
    "IDialogueOverlayData": "dialogue overlay",
    "IAveBattleGroupInfoModel": "Ave battle group",
    "IArenaRequirementsPopupModel": "arena requirements popup",
    "IArenaRequirementsPopupCallbacks": "arena requirements popup",
    "IArenaRewardsPopupModel": "arena rewards",
    "IArenaRewardsPopupCallbacks": "arena rewards",
    "IAwayTeamPopupModel": "away team",
    "IBaseEditBuildingPopupData": "base edit building",
    "IBaseEditNodePopupData": "base edit node",
    "IBaseGachaPopupData": "base gacha",
    "IBuildingSelectPopupData": "building select",
    "IChampionItemUseConfirmationModel": "item use confirmation",
    "IDailyLoginModel": "daily login",
    "IDailyLoginCallbacks": "daily login",
    "IDailyRewardPopupData": "daily reward",
    "IDefenderSelectPopupData": "defender select",
    "IEnergySummaryPopupData": "energy summary",
    "IPaymentCardPurchasedPopupModel": "payment card",
    "IFightResultsPopupModel": "fight results",
    "IFightResultsCallbacks": "fight results",
    "IFlashSaleDataProvider": "flash sale",
    "IHeroConsumablesModel": "hero consumables",
    "IHeroConsumablesCallbacks": "hero consumables",
    "IHowToAvePopupData": "Ave how-to",
    "IInventoryItemPopupData": "inventory item",
    "IItemOverrideWarningPopupData": "item override",
    "IItemUseChooseChampionModel": "item use champion",
    "IItemUseSelectPopupData": "item use select",
    "IKabamLoginIncentivePopupData": "login incentive",
    "ILoginRewardsModel": "login rewards",
    "ILoginRewardsCallbacks": "login rewards",
    "IMissionTeamSelectWarningPopupData": "mission team select warning",
    "INamePopupData": "name popup",
    "IPVPRaidOpponentReviewData": "PvP raid opponent review",
    "IPVPRaidReportDetailsData": "PvP raid report",
    "IPaymentCardsPopupModel": "payment cards",
    "IPlayerProfileDataProvider": "player profile",
    "IQuestDetailsData": "quest details",
    "IQuitArenaPopupModel": "quit arena",
    "IQuitArenaPopupCallbacks": "quit arena",
    "IResourceSummaryPopupData": "resource summary",
    "ISoloEventsPopupData": "solo events",
    "ISummonerBoostsPopupData": "summoner boosts",
    "IUseItemPopupData": "use item",
    "IUseItemsPopupCallbacks": "use item",
    "IAVEBattleGroupSelectionModel": "Ave battle group selection",
    "IAllianceNavScreenData": "alliance nav",
    "IAveHistoryScreenModel": "Ave history",
    "IAveLandingScreenModel": "Ave landing",
    "IAveResultsScreenModel": "Ave results",
    "IBuildingDetailsScreenData": "building details",
    "IEditTeamData": "edit squad",
    "IEditTeamCallbacks": "edit squad",
    "IFightLandingData": "fight landing",
    "GachaRevealDataProvider": "gacha reveal",
    "IGoalsModel": "objectives / goals",
    "IBaseLeaderboardModel": "base leaderboard",
    "IMasteriesScreenData": "masteries",
    "IPVPArenaResultsScreenModel": "PvP arena results",
    "IPVPMatchSeriesScreenModel": "PvP match series",
    "IPVPMatchSeriesScreenCallbacks": "PvP match series",
    "IPVPScreenCallbacks": "PvP screen",
    "IPVPScreenModel": "PvP screen",
    "IPVPRaidResultsData": "PvP raid results",
    "IPVPRaidSelectDataProvider": "PvP raid select",
    "IPVPReportData": "PvP report",
    "IPrefightDataProvider": "prefight (SELECT YOUR BOT)",
    "IQuestResultsDataProvider": "quest results",
    "IQuestResultsCallbacks": "quest results",
    "IQuestSelectModel": "quest select",
    "ISettingsScreenDataProvider": "settings",
    "IMissionTeamSelect": "mission team select",
    "ITeamSelectModel": "team select",
    "ITeamSelectCallbacks": "team select",
    "IUpgradeScreenModelBase": "upgrade screen",
}

lines = [
    "# InterfaceInjector registry (78 interfaces)",
    "",
    "Generated from the live runtime registry by `work/dump_injector_names.py`;",
    "names resolved through `Il2CppTypeDefinition.nameIndex` -> `global-metadata.dat`.",
    "Live tag at HomeFlow/prefight: **`tform`**. `Get<T>` has a `default` fallback",
    "(see `docs/prefight_flow.md`).",
    "",
    "| # | interface | implementations (tag -> class) | persistent | screen / subsystem | stub status |",
    "|---|---|---|---|---|---|",
]
for e in d["interfaces"]:
    idx = e["index"]
    iface = e["interface"][1] if e["interface"] else "?"
    impls = "; ".join(f"{tag} -> {impl[1] if impl else '?'}" for tag, impl in e["implementations"])
    persistent = "yes (ads)" if iface == "IAdsProvider" else ""
    screen = SCREEN.get(iface, "unknown")
    if iface == "IPrefightDataProvider":
        status = "**BLOCKED**: entry 69 default-only; prefight model null"
    elif iface == "IAdsProvider":
        status = "persistent; native IronSource; server only autorefresh/ads"
    elif iface in ("IQuestSelectModel", "IQuestDetailsData", "IEditTeamData", "IEditTeamCallbacks"):
        status = "quest UI; stub partially covers"
    elif iface in ("IGoalsModel", "IPlayerProfileDataProvider", "ISettingsScreenDataProvider"):
        status = "screen opens empty/redirect; data not implemented"
    else:
        status = "no dedicated stub data; screen not verified"
    lines.append(f"| {idx} | `{iface}` | {impls} | {persistent} | {screen} | {status} |")

lines += [
    "",
    "## I2: IAdsProvider / IronSourceAdsModel",
    "",
    "- `IAdsProvider` is the only persistent interface (`_persistentInterfaces` count 1),",
    "  value `TFormIronSourceAdsModel` (tform).",
    "- `IronSourceAdsModel` fields: `appKey`, `_Listeners`, `_initialized`, `_enabled`,",
    "  `_OnAdComplete`, `_rewardState`, `_timeout`; methods `IsEnabled`, `Disable`,",
    "  `Enable`, `IsSupported`, `Initialize`, `ShowRewarded` etc. [STATIC]",
    "- `TFormIronSourceAdsModel` overrides `IsEnabled`/`IsSupported` (`0x10D8078`, `0x10D813C`).",
    "- Observed server calls: `/autorefresh/ads/refresh` only (stub returns `{}`); no",
    "  ad-network HTTP request was observed. The native IronSource SDK is not initialized",
    "  by the stub, so ads are not a source of extra server requests. [RUN]",
    "",
    "## Which interfaces block which screens",
    "",
    "- `IPrefightDataProvider` (69): blocks FIGHT/prefight.",
    "- `IPlayerProfileDataProvider` (39): profile popup; current top-left account icon",
    "  opens KABAM ACCOUNT?/LOGIN OPTIONS instead, so profile is not reached.",
    "- `ISettingsScreenDataProvider` (73): settings screen; not reached yet.",
    "- `IGoalsModel` (58): OBJECTIVES opens empty `[0/0] COMPLETE`.",
    "- `IQuestSelectModel` (72) / `IQuestDetailsData` (40): quest list/detail work with the",
    "  current stub; deeper data still missing.",
    "- All other interfaces are for screens/subsystems outside the current battle slice.",
]
out = ROOT / "docs" / "interfaces.md"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", out, "rows", len(d["interfaces"]))
