"""Build an equivalent server rating decomposition for every wiki row (R2 3.2)."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROWS = json.loads((ROOT / "data" / "wiki" / "rating_rows.json").read_text(encoding="utf-8"))
OUT = ROOT / "data" / "rating_table.json"


def rec(r, star=None):
    rating = int(round(r["rating"]))
    hp, atk = float(r["hp"]), float(r["attack"])
    denom = hp + atk or 1.0
    hp_part = int(round(rating * hp / denom))
    hp_part = max(0, min(rating, hp_part))
    atk_part = rating - hp_part
    return {
        "bot": r["bot"],
        "star": star,
        "rank": r.get("rank"),
        "level": r.get("level"),
        "hp": hp,
        "attack": atk,
        "rating": rating,
        # equivalent decomposition of the client's sum; not the retail split
        "hero_rating_hp": hp_part,
        "hero_rating_attack": atk_part,
        "hero_rating_hp_base": hp_part,
        "hero_rating_attack_base": atk_part,
        "decomposition": "proportional to HP/ATK; equivalent, [DERIVED]",
    }


out = []
for r in ROWS.get("stat_table_rows", []):
    if r.get("rating"):
        out.append(rec(r))
for r in ROWS.get("star_rows", []):
    if r.get("rating"):
        out.append(rec(r, star=r.get("star")))

# Verify the client tail with mod=0/extra=0.
for x in out:
    if math.ceil(x["hero_rating_hp"] + x["hero_rating_attack"]) != x["rating"]:
        raise SystemExit(f"bad decomposition {x}")

(OUT).write_text(json.dumps({
    "source": "data/wiki/rating_rows.json",
    "method": "equivalent proportional HP/ATK split; not the retail HeroRating split",
    "label": "[DERIVED]",
    "note": "Use only to make the client formula reproduce the wiki rating; "
            "do not present it as original server data.",
    "rows": out,
}, ensure_ascii=False, indent=1), encoding="utf-8")
print("rows", len(out))
print(out[0])
