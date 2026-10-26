"""Generate spec/tuning_keys.md from the IL2CPP dump.

Finding: TuningManager.GetString/GetInt/GetBool/GetFloat (0x15DC204/21C/230/248)
have no direct BL callers in libil2cpp.so. Tuning.LoadTuningData uses reflection
and TuningManager.Apply, so the tuning keys are the public field names of the
Tuning components. TuningGameplay.DeserializeData has its own key mapping.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DUMP = ROOT / "work" / "il2cpp_dump" / "dump.cs"
OUT = ROOT / "spec" / "tuning_keys.md"
text = DUMP.read_text(encoding="utf-8", errors="replace")
lines = text.splitlines()


def class_fields(class_header):
    start = None
    for i, line in enumerate(lines):
        if line.startswith(class_header):
            start = i
            break
    if start is None:
        return []
    depth = 0
    seen = False
    fields = []
    for line in lines[start:]:
        depth += line.count("{") - line.count("}")
        if "{" in line:
            seen = True
        m = re.match(r"\s*public\s+([^;]+?)\s+(\w+);\s*//\s*(0x[0-9A-Fa-f]+)", line)
        if m and seen:
            fields.append((m.group(2), m.group(1).strip(), m.group(3)))
        if seen and depth <= 0:
            break
    return fields


sections = [
    ("Tuning (`/tuning` via reflection `Apply`)", "public class Tuning : MonoBehaviour"),
    ("TuningGameplay (`DeserializeData`)", "public class TuningGameplay : MonoBehaviour"),
    ("TuningClassColors", "public class TuningClassColors : MonoBehaviour"),
    ("TuningLevelLocks", "public class TuningLevelLocks : MonoBehaviour"),
    ("TuningRarityColors", "public class TuningRarityColors : MonoBehaviour"),
    ("TuningSynergyBonusColors", "public class TuningSynergyBonusColors : MonoBehaviour"),
    ("TuningWebLinks", "public class TuningWebLinks : MonoBehaviour"),
]

out = [
    "# Tuning keys (Step 6.1)",
    "",
    "Status: **structural table generated from `dump.cs`; values are client",
    "defaults unless `/tuning` supplies them.**",
    "",
    "## Mechanic (negative xref result)",
    "",
    "`[STATIC]` `TuningManager.GetString/GetInt/GetBool/GetFloat`",
    "(`0x15DC204`/`0x15DC21C`/`0x15DC230`/`0x15DC248`) are simple",
    "`Dot.*` wrappers over `_data+0x20`. A scan of every `BL`/`B` in",
    "`libil2cpp.so` found **no direct callers** of those four methods; they",
    "are not used with literal keys in this build.",
    "",
    "`[STATIC]` `Tuning.LoadTuningData` (`0x14233EC`) walks the public fields",
    "of the `Tuning` component and calls `TuningManager.Apply`",
    "(`0x15DAEB0`/`0x15DBFEC`) with the field name. `TuningGameplay` uses",
    "`DeserializeData` (`0x1425540`). The effective key namespace is therefore",
    "the **field names below**, not a separate string table.",
    "",
    "`[RUN]` Live `Tuning` ODR flags (read-only, 2026-10-27):",
    "",
    "| key | live value | meaning |",
    "|---|---:|---|",
    "| `ODRForceDownloadAll` | 0 | do not force all ODR downloads |",
    "| `ODRForceDownloadAllPreTutorial` | 0 | |",
    "| `ODRShowProgressMB` | 1 | show MB progress |",
    "| `ODRShowTimeEstimate` | 1 | show time estimate |",
    "| `ODRForceDownloadAssetListPreTutorial` | 0 | |",
    "| `ODRAllowNative` | 1 | native ODR path allowed |",
    "",
    "These are **data flags**. Do not change them to bypass the blocker without",
    "explicit consent; `ODRAllowNative=0` is only a hypothesis, not applied.",
    "",
    "## Current `/tuning` payload (verified)",
    "",
    "`server/data/tuning_data.json` sends one object:",
    "",
    "```json",
    "{",
    '  "heroRatingAttackWeight": 1.0,',
    '  "heroRatingMaxHPWeight": 0.2,',
    '  "sigLvlMax": 100,',
    '  "ratingPrecision": 0',
    "}",
    "```",
    "",
    "These four are read by the BCG layer/rating path; they are not fields of",
    "the `Tuning` component. Keep them in `/tuning` until a call-site proves a",
    "different source.",
    "",
]

for title, header in sections:
    fields = class_fields(header)
    out += [f"## {title}", ""]
    if not fields:
        out += ["_No public fields parsed._", ""]
        continue
    out += ["| key | type | offset |", "|---|---|---:|"]
    for name, typ, off in fields:
        out.append(f"| `{name}` | `{typ}` | {off} |")
    out += ["", f"_fields: {len(fields)}_", ""]

out += [
    "## Not done",
    "",
    "- Per-field consumers (which code reads each `Tuning` field) are not all",
    "  xref'd; the field list is complete, but the consumer map is partial.",
    "- `TuningGameplay.DeserializeData` key suffixes are not fully decoded.",
    "- `TuningManager.Apply` reflection behavior is documented, not every",
    "  applied field value.",
    "",
]

OUT.write_text("\n".join(out), encoding="utf-8")
print("wrote", OUT)
print("Tuning fields", len(class_fields("public class Tuning : MonoBehaviour")))
print("TuningGameplay fields", len(class_fields("public class TuningGameplay : MonoBehaviour")))
