"""Build data/screens.json and docs/screens.md from dump.cs + manual annotations."""
import json
import re
from pathlib import Path

ROOT = Path(r".")
DUMP = ROOT / "work" / "il2cpp_dump" / "dump.cs"

KNOWN = {
    "SettingsScreen": ("ISettingsScreenDataProvider (73)", "-", "open; ACCOUNT/SOUND/STORY work [RUN]"),
    "GoalsScreen": ("IGoalsModel (58)", "/objectives", "open; empty [0/0] because stub payload is empty [RUN]"),
    "PreFightScreen": ("IPrefightDataProvider (69)", "/matches/activate-match", "open; FIGHT works; battle-init NRE [RUN]"),
    "PlayerProfilePopup": ("IPlayerProfileDataProvider (39)", "/userprofile/", "not reachable from the current home UI [RUN]"),
    "HeroesScreen": ("none (BCGHelper.GetHeroes)", "/bcg/getLoginData (cached)", "open, 59 cards [RUN]"),
    "UpgradeActorScreen": ("IUpgradeScreenModelBase (77)", "/bcg/getHeroXPCurve", "opens; NRE in SetXPCurve when curve payload is empty [RUN]"),
    "EditTeamScreen": ("IEditTeamData (57), IEditTeamCallbacks", "/bcg/setSavedTeam", "opens; NRE in EditTeamModel.RefreshHeros if active team is empty [RUN]"),
    "QuestSelect": ("IQuestSelectModel (72)", "/quests/quest-list", "open; 66+24 mission list [RUN]"),
    "QuestDetailsPopup": ("IQuestDetailsData (40)", "/quests/quest-detail", "open [RUN]"),
    "QuestboardHud": ("none", "/quests/quest-movedir", "open; HUD stacked below PreFightScreen [RUN]"),
    "QuestResultsScreen": ("IQuestResultsDataProvider (70), IQuestResultsCallbacks", "/quests/battlecomplete, /quests/fightlost", "not reached (battle does not finish) [STATIC]"),
    "TeamSelect": ("ITeamSelectModel (75), ITeamSelectCallbacks", "/bcg/setSavedTeam", "open from quest team selection [RUN]"),
    "InventoryScreen": ("none", "/inventory", "locked (red lock) at level 0 [RUN]"),
    "FuseStoreScreen": ("none", "/store", "locked (level) [RUN]"),
    "GachaPurchaseScreen": ("none", "/gacha", "locked/empty [RUN]"),
    "SoloEventsPopup": ("ISoloEventsPopupData (47)", "/events", "not reached [STATIC]"),
    "ArenaRequirementsPopup": ("IArenaRequirementsPopupModel/Callbacks", "/pvp", "locked at level 0 [RUN]"),
    "PVPArenaResultsScreen": ("IPVPArenaResultsScreenModel (61)", "/pvp", "locked [RUN]"),
    "PVPRaidSelectScreen": ("IPVPRaidSelectDataProvider (66)", "/pvp", "locked [RUN]"),
    "AllianceScreen": ("IAllianceNavScreenData (52)", "/alliance", "locked (red lock) [RUN]"),
    "BaseLeaderboardScreen": ("IBaseLeaderboardModel (59)", "/base", "not reached [STATIC]"),
    "MasteryFullScreenOverlay": ("IMasteriesScreenData (60)", "/quests/mastery", "not reached [STATIC]"),
    "LoginScreen": ("none", "/auth/*", "login flow [RUN]"),
    "KabamLoginWindow": ("none", "/auth/*", "account popup; KABAM/GOOGLE [RUN]"),
    "LoginOptionsPopup": ("none", "/invites/privacy", "login options [RUN]"),
    "CriticalError": ("none", "-", "error overlay [RUN]"),
    "FullScreenBlocker": ("none", "-", "blocker [RUN]"),
    "BusyBlocker": ("none", "-", "blocker [RUN]"),
    "FuseODRBlocker": ("none", "-", "ODR blocker [RUN]"),
    "GlobalEventHandler": ("none", "-", "global input [RUN]"),
    "UIScreenBackground": ("none", "-", "background [RUN]"),
}

lines = DUMP.read_text(encoding="utf-8", errors="replace").splitlines()
rows = []
for i, line in enumerate(lines):
    m = re.match(r"public (?:class|sealed class) (\S+) : (.+?) // TypeDefIndex: (\d+)", line)
    if not m:
        continue
    name, bases, tid = m.group(1), m.group(2), int(m.group(3))
    if not re.search(r"\b(Window|TFormWindow|Popup|TemplatePopup|PopupFader)\b", bases):
        continue
    if name in KNOWN:
        provider, endpoints, status = KNOWN[name]
    else:
        provider, endpoints, status = "", "", "untested; no dedicated stub data"
    rows.append({
        "class": name,
        "bases": bases,
        "typedef": tid,
        "provider": provider,
        "endpoints": endpoints,
        "status": status,
    })

rows.sort(key=lambda r: (r["status"].startswith("untested"), r["class"]))
(ROOT / "data" / "screens.json").write_text(
    json.dumps({"source": "work/il2cpp_dump/dump.cs", "rows": rows}, ensure_ascii=False, indent=1),
    encoding="utf-8")

md = [
    "# Window / popup screen table",
    "",
    "Generated from `dump.cs` (`Window`, `TFormWindow`, `Popup`, test windows) by",
    "`work/build_screen_table.py`. Provider and endpoint columns are filled only",
    "where the client or server actually exercised them; `untested` is honest,",
    "not a claim of a defect.",
    "",
    f"Total classes: **{len(rows)}**.",
    "",
    "| screen | base | provider | endpoints | status in our environment |",
    "|---|---|---|---|---|",
]
for r in rows:
    if not r["status"].startswith("untested"):
        md.append(f"| `{r['class']}` | {r['bases']} | {r['provider']} | {r['endpoints']} | {r['status']} |")
md += [
    "",
    "## Untested windows",
    "",
    "The remaining classes are listed in `data/screens.json`. They include test",
    "screens (`*TestScreen`), alliance/PvP/base/store popups and overlays that are",
    "locked or not reachable at account level 0. No provider was observed for them",
    "in our runs.",
    "",
]
(ROOT / "docs" / "screens.md").write_text("\n".join(md), encoding="utf-8")
print("rows", len(rows), "known", len(KNOWN))
