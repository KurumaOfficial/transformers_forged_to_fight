"""Add the literal key attack_percent used by BCGAttackValue..ctor.

Disassembly 0xC145BC..0xC147B8 builds the Percent field from two JSONPaths:
the second is the literal string "attack_percent". Our entries only had
percent/p, so Percent stayed 0 and every hit dealt zero damage.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "server" / "data" / "bcg_login_data.json"
data = json.loads(PATH.read_text(encoding="utf-8"))
av = data.setdefault("attackValues", {})
n = 0
for key, entry in av.items():
    if not isinstance(entry, dict):
        continue
    entry.setdefault("attack_percent", entry.get("percent", entry.get("p", 1.0)))
    n += 1
PATH.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print("updated", n, "entries")
print({k: v.get("attack_percent") for k, v in av.items()})
