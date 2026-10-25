"""R1 coverage ledger for all 59 client bots."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "server" / "data" / "bot_catalog_real.json"
BOTS = ROOT / "data" / "wiki" / "bots.json"
DER = ROOT / "data" / "wiki" / "derived_level1.json"
OUT = ROOT / "data" / "wiki" / "stat_coverage.json"

cat = json.loads(CAT.read_text(encoding="utf-8"))["rows"]
bots = json.loads(BOTS.read_text(encoding="utf-8"))["bots"]
der = json.loads(DER.read_text(encoding="utf-8"))["bots"] if DER.exists() else {}

# class medians of star-1 HP/ATK
from statistics import median
class_hp = {}
class_atk = {}
for name, b in bots.items():
    st = (b.get("stars") or {}).get("1") or {}
    try:
        hp = float(str(st.get("health", "")).replace(",", ""))
        atk = float(str(st.get("attack", "")).replace(",", ""))
    except Exception:
        continue
    cls = (b.get("infobox") or {}).get("Class") or "Unknown"
    class_hp.setdefault(cls, []).append(hp)
    class_atk.setdefault(cls, []).append(atk)
med_hp = {k: median(v) for k, v in class_hp.items()}
med_atk = {k: median(v) for k, v in class_atk.items()}
default_hp = median([x for v in class_hp.values() for x in v]) if class_hp else 1000
default_atk = median([x for v in class_atk.values() for x in v]) if class_atk else 120

rows = []
for r in cat:
    cid = r["client_id"]
    page = r.get("wiki_page")
    b = bots.get(page) or {}
    tables = b.get("stat_tables") or []
    has_table = bool(tables)
    star1 = (b.get("stars") or {}).get("1") or {}
    has_star1 = bool(star1)
    cls = r.get("class") or b.get("infobox", {}).get("Class") or "Unknown"
    if has_table:
        label = "[WIKI]"
        unc = 4.1
        d = der.get(page) or der.get(cid) or {}
        hp, atk = d.get("hp"), d.get("attack")
        reason = "stat table exists; level1 derived from global ladder"
    elif has_star1:
        label = "[WIKI]"
        unc = 0.0

        def n(v):
            try:
                return float(str(v).replace(",", ""))
            except Exception:
                return None
        hp, atk = n(star1.get("health")), n(star1.get("attack"))
        reason = "wiki star-1"
    else:
        label = "[ASSUMED]"
        unc = 25.0
        hp = round(med_hp.get(cls, default_hp), 1)
        atk = round(med_atk.get(cls, default_atk), 1)
        reason = "no stat table, no star-1; class median prior"
    rows.append({
        "client_id": cid,
        "wiki_page": page,
        "class": cls,
        "has_stat_table": has_table,
        "table_count": len(tables),
        "has_star1": has_star1,
        "level1_hp": hp,
        "level1_attack": atk,
        "label": label,
        "uncertainty_pct": unc,
        "reason": reason,
    })

OUT.write_text(json.dumps({"source": "bot_catalog_real.json + bots.json + derived_level1.json",
                            "rows": rows}, ensure_ascii=False, indent=1), encoding="utf-8")
from collections import Counter
print(Counter(r["label"] for r in rows))
print("ASSUMED:")
for r in rows:
    if r["label"] == "[ASSUMED]":
        print(" ", r["client_id"], r["wiki_page"], r["reason"])
