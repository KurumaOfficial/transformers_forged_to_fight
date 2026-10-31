"""Generate docs/special_attack_tokens.md from the census."""
import json
from pathlib import Path

d = json.loads(Path("data/client_character_census.json").read_text(encoding="utf-8"))
rows = d["characters"]
missing = set(d["counts"]["loc_tokens_missing_spec"])

lines = [
    "# Special-attack and bio localization tokens (Step 3)",
    "",
    "Status: **static key/token map complete; on-screen verification is blocked by",
    "the BOTS card/user-data binding gap (see `docs/bots_grid.md`).**",
    "",
    "## Key builder `[STATIC]`",
    "",
    "`BCGHelper.GetSpecialAttackNameLocString` (`0xC1B154`) and",
    "`GetSpecialAttackDescriptionLocString` (`0xC1B21C`):",
    "",
    "1. take the blueprint id string;",
    "2. `LastIndexOf(\"_\")`;",
    "3. `Substring(0, index)` and `ToUpperInvariant()`;",
    "4. concatenate `ID_SPECIAL_ATTACK_` (or `ID_SPECIAL_ATTACK_DESCRIPTION_`)",
    "   + token + `_` + attack index.",
    "",
    "So a blueprint id must be **`<loc_token>_<suffix>`** to produce",
    "`ID_SPECIAL_ATTACK_<loc_token>_<n>`. Example: `windb_gs_2` ->",
    "`ID_SPECIAL_ATTACK_WINDB_GS_0`. The current catalog uses asset ids such as",
    "`windblade_gs`, which produce `ID_SPECIAL_ATTACK_WINDBLADE_0` and miss the",
    "retained strings.",
    "",
    "## Token table",
    "",
    "| client id | loc token | special names | bio | note |",
    "|---|---|---|---|---|",
]
for r in rows:
    note = "missing client strings" if r["id"] in missing else ""
    lines.append("| `%s` | `%s` | %s | %s | %s |" % (
        r["id"], r["loc_token"],
        "yes" if r["special_attack_present"] else "**no**",
        "yes" if r["bio_present"] else "**no**", note))

lines += [
    "",
    "## Bots with no client strings (7) `[STATIC]`",
    "",
    "These have a token, portrait and move data, but no",
    "`ID_SPECIAL_ATTACK_<token>_*` and no `ID_CHARACTER_BIOS_<token>` in the",
    "localization dump:",
    "",
]
for cid in sorted(missing):
    r = next(x for x in rows if x["id"] == cid)
    lines.append("- `%s` / `%s`" % (cid, r["loc_token"]))
lines += [
    "",
    "Do not invent retail strings for these. A server localization table could",
    "fill them as `[ASSUMED]`, but the client's `LocalizationManager` reads",
    "`LoginManager._loginData`, which is empty in the current flow (see",
    "`docs/level_lock.md`).",
    "",
    "## Token aliases found",
    "",
    "- Bumblebee G1: `BUMBL_GS` (spec/bio) plus alternate `BUMBLE_GS` bio.",
    "- Dinobot: `DINOB_BW` (bio) and `DINOB_GS` (some spec keys).",
    "- Mixmaster: `MIXMA_C_ROTF` and `MIXMA_GS`.",
    "- Thundercracker: portrait token `thunder_gs`, strings token",
    "  `THUNDERCRACKER_GS`.",
    "- Cyclonus: portrait typo `clyclon_gs` plus `cyclon_gs`.",
    "- Sharkticons: `SHARK_*` plus `NPC_SHARK_*`; `SHARK_GOLD2` has no",
    "  catalog id (candidate unused/event variant).",
    "",
    "## What is not proven",
    "",
    "- The exact UI request for each screen after the card is selected; the",
    "  current INFO/UPGRADE screen shows 0 HP/0 ATK, so the abilities panel was",
    "  not reachable for a clean screenshot.",
    "- A server `loc`/`XlateManager` override accepted by the client.",
    "",
]
Path("docs/special_attack_tokens.md").write_text("\n".join(lines), encoding="utf-8")
print("wrote", len(rows))
