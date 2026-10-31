"""Generate a catalog of ID_STAT/D_STAT/ID_SPECIAL_ATTACK localization keys."""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOC = json.loads((ROOT / "work" / "localization_all.json").read_text(encoding="utf-8"))
OUT = ROOT / "spec" / "buff_catalog.md"

stat = {k: v for k, v in LOC.items() if k.startswith("ID_STAT_")}
dstat = {k: v for k, v in LOC.items() if k.startswith("D_STAT")}
sp = {k: v for k, v in LOC.items() if k.startswith("ID_SPECIAL_ATTACK_")}

# Group ID_STAT by the token after the prefix. Bot keys usually start with a
# known bot token; synergy/class keys have their own prefixes.
groups = Counter()
for k in stat:
    parts = k.split("_")
    groups[parts[2] if len(parts) > 2 else ""] += 1

# Bot candidates from blueprint ids in server data.
login = json.loads((ROOT / "server" / "data" / "bcg_login_data.json").read_text(encoding="utf-8"))
bot_tokens = set()
for bid in login.get("heroes", {}):
    token = bid.upper().replace("_", "")
    bot_tokens.add(token)
    bot_tokens.add(bid.split("_")[0].upper())

bot_stat = defaultdict(list)
for k in stat:
    up = k.upper()
    for token in sorted(bot_tokens, key=len, reverse=True):
        if token and token in up:
            bot_stat[token].append(k)
            break

# Special attacks: split ID_SPECIAL_ATTACK_[DESCRIPTION_]<BOT>_<n>
special = defaultdict(list)
for k in sp:
    body = k[len("ID_SPECIAL_ATTACK_"):]
    if body.startswith("DESCRIPTION_"):
        body = body[len("DESCRIPTION_"):]
    m = re.match(r"(.+)_([0-9]+)$", body)
    if m:
        special[m.group(1)].append(k)
    else:
        special[body].append(k)

lines = [
    "# Buff / stat / special-attack key catalog (Step 2.1)",
    "",
    "Source: `work/localization_all.json` (7869 keys, saved localization table).",
    "Keys are **localization keys**, not the original server statMod/Buff",
    "definitions. They prove that effect/key names exist in the client; they do",
    "not provide the per-bot numeric `modifier`, trigger graph or statMod id.",
    "",
    f"- `ID_STAT_*`: **{len(stat)}**",
    f"- `D_STAT*`: **{len(dstat)}**",
    f"- `ID_SPECIAL_ATTACK_*`: **{len(sp)}**",
    "",
    "## Client schema anchors [STATIC]",
    "",
    "| class | fields / use | RVA |",
    "|---|---|---|",
    "| `BCGStatModifier` | `ID`, `Type`, `TypeMod`, `Trigger`, `TriggerModStr`, `TriggerRate`, `Stat`, `Target`, `ModType`, `Var`, `ModSource`, `Growth*`, `Auth`, `Modifier`, `Duration`, `Priority` | `0xA5DFBC` ctor |",
    "| `CharacterMetaData.StatModifierAttributes` | None/HP/Attack/Mana/ManaGain/Block/PerfectBlock/MaxHP/CritChance/CritDamage/StunChance/Armor | enum 8405 |",
    "| `BuffModTypes` | none/buff/debuff/passive/passive_buff/passive_debuff | enum 8807 |",
    "| `BuffTargetTypes` | none/self/opponent/owner/tower/opp_tower | enum 8810 |",
    "| `BuffTriggerConstants` | `onStart`, `onPreStart`, `onAbilityActivate`, `onAbilityExpiry`, `onTypeActivate`, `onTypeExpiry`, `onBuffImmune` | static strings |",
    "| `BuffTriggerFactory` | trigger/condition construction | `0xEE8720` |",
    "",
    "## `ID_STAT_*` key families",
    "",
    "| family token | keys | sample |",
    "|---|---:|---|",
]
for token, n in groups.most_common(40):
    sample = next((k for k in stat if k.split("_")[2:3] == [token]), "")
    lines.append(f"| `{token}` | {n} | `{sample}` |")

lines += ["", "## Bot-specific `ID_STAT_*` keys", "",
          "| bot token | keys | examples |", "|---|---:|---|"]
for token, keys in sorted(bot_stat.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:60]:
    lines.append(f"| `{token}` | {len(keys)} | " + ", ".join(f"`{k}`" for k in keys[:4]) + " |")

lines += ["", "## `D_STAT*` keys", ""]
for k, v in sorted(dstat.items()):
    lines.append(f"- `{k}` = `{v[:100]}`")

lines += ["", "## Special-attack keys", "",
          f"Unique bot/move prefixes: **{len(special)}**; total keys **{len(sp)}**.", "",
          "| bot/move token | keys | name key sample | description key sample |",
          "|---|---:|---|---|"]
for token, keys in sorted(special.items(), key=lambda kv: kv[0]):
    names = [k for k in keys if not k.startswith("ID_SPECIAL_ATTACK_DESCRIPTION_")]
    descs = [k for k in keys if k.startswith("ID_SPECIAL_ATTACK_DESCRIPTION_")]
    lines.append(f"| `{token}` | {len(keys)} | `{names[0] if names else ''}` | `{descs[0] if descs else ''}` |")

missing = [t for t in special if "WINDBLADE" in t.upper()]
lines += ["", "## Windblade check", "",
          f"Special-attack tokens containing WINDBLADE: **{len(missing)}**.",
          "The live screen showed raw `MS_ID_SPECIAL_ATTACK_WINDBLADE_0..2`; the",
          "localization table has no `ID_SPECIAL_ATTACK_WINDBLADE_*` key. This is",
          "a missing localization entry, not an NRE. Required keys:",
          "",
          "```",
          "ID_SPECIAL_ATTACK_WINDBLADE_0",
          "ID_SPECIAL_ATTACK_WINDBLADE_1",
          "ID_SPECIAL_ATTACK_WINDBLADE_2",
          "ID_SPECIAL_ATTACK_DESCRIPTION_WINDBLADE_0",
          "ID_SPECIAL_ATTACK_DESCRIPTION_WINDBLADE_1",
          "ID_SPECIAL_ATTACK_DESCRIPTION_WINDBLADE_2",
          "```",
          "",
          "## What is still missing",
          "",
          "- Numeric `statMods`/`Buff` definitions: ids, modifiers, triggers,",
          "  stacking and appearance. The localization keys alone are not enough",
          "  to build them; inventing them would be `[ASSUMED]` and unverified.",
          "- The mapping from wiki effect text to a client key is partial: many",
          "  keys are bot-specific (`ID_STAT_RHINOX_SHLD`, `ID_STAT_OPTIMUS_*`),",
          "  but the key text does not include the numeric value or trigger.",
          "- Special-attack localization for Windblade is absent; for many other",
          "  bots the `ID_SPECIAL_ATTACK_*` keys are present in the table.",
          ]
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", OUT)
print("stat", len(stat), "dstat", len(dstat), "special", len(sp), "bots", len(special))
