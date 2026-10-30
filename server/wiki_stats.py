"""Wiki-derived bot stats for the server catalog and battle payloads.

The wiki has 44 bot pages with rank/level stat tables. A linear fit
`a_rank*rank + b_level*level + c` reproduces the table rows with the RMSE
recorded in `data/wiki/stat_growth_fit.json`. Bots without a fit use their
level-1 row plus the median growth; bots without a wiki row fall back to the
old placeholder and are labelled `[ASSUMED]`.

Rating is **not** exact: the client consumes server-provided
`HeroRatingHP/HeroRatingAttack`, and the wiki rating is not an integer-exact
function of raw HP/ATK. The helper therefore returns an `[ASSUMED]` split;
do not present it as retail.
"""
import json
import statistics
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "wiki"


def _load(name):
    try:
        return json.loads((DATA / name).read_text(encoding="utf-8"))
    except Exception:
        return {}


_FITS = {e["bot"]: e for e in _load("stat_growth_fit.json") if isinstance(e, dict)}
_COVER = _load("stat_coverage.json").get("rows") or []
# Client-only/wikidata bots not in the 44-page coverage table.
_EXTRA = {
    "starscream_gs": {
        "client_id": "starscream_gs",
        "wiki_page": "Starscream",
        "class": "Tactician",
        "level1_hp": 5400.0,
        "level1_attack": 391.0,
        "label": "[WIKI]",
        "uncertainty_pct": 6.0,
    },
    "optimusprime_gs_v": {
        "client_id": "optimusprime_gs_v",
        "wiki_page": "Optimus Prime",
        "class": "Tactician",
        "level1_hp": 6240.0,
        "level1_attack": 444.0,
        "label": "[WIKI]",
        "uncertainty_pct": 6.0,
    },
}
_HAVE = {r.get("client_id") for r in _COVER}
_COVER.extend(v for k, v in _EXTRA.items() if k not in _HAVE)
_BY_CLIENT = {r.get("client_id"): r for r in _COVER if r.get("client_id")}

# Some fit entries have hp/atk swapped (e.g. Rhinox). Detect by comparing the
# rank1/level1 fit value with the wiki level1 anchor.
for _r in _COVER:
    _fit = _FITS.get(_r.get("wiki_page"))
    if not _fit or not _r.get("level1_hp") or not _r.get("level1_attack"):
        continue
    _h1 = _fit["hp"]["a_rank"] + _fit["hp"]["b_level"] + _fit["hp"]["c"]
    _a1 = _fit["atk"]["a_rank"] + _fit["atk"]["b_level"] + _fit["atk"]["c"]
    if abs(_h1 - _r["level1_hp"]) > abs(_a1 - _r["level1_hp"]):
        _fit["hp"], _fit["atk"] = _fit["atk"], _fit["hp"]


def _norm(bid):
    b = str(bid or "").lower()
    for suffix in ("_2", "_3", "_4", "_5"):
        if b.endswith(suffix):
            b = b[:-2]
            break
    return b


_BY_NORM = {_norm(k): v for k, v in _BY_CLIENT.items()}

# Exact wiki rating for the rank1/level1 row, when present.
_RATING1 = {}
try:
    _BOTS = json.loads((DATA / "bots.json").read_text(encoding="utf-8")).get("bots") or {}
    for _name, _data in _BOTS.items():
        for _table in (_data.get("stat_tables") or []):
            for _row in _table:
                if len(_row) >= 4 and str(_row[0]).strip() == "1/1":
                    _m = __import__("re").search(r"\d[\d,]*", str(_row[3]))
                    if _m:
                        _RATING1[_name] = int(_m.group(0).replace(",", ""))
                    break
            if _name in _RATING1:
                break
except Exception:
    _RATING1 = {}

# Median growth for bots without a per-bot fit.
_A = [e["hp"]["a_rank"] for e in _FITS.values() if e.get("hp", {}).get("a_rank", 0) > 1000]
_B = [e["hp"]["b_level"] for e in _FITS.values() if e.get("hp", {}).get("b_level", 0) > 100]
_AA = [e["atk"]["a_rank"] for e in _FITS.values() if e.get("atk", {}).get("a_rank", 0) > 50]
_AB = [e["atk"]["b_level"] for e in _FITS.values() if e.get("atk", {}).get("b_level", 0) > 1]
MED_HP_A = statistics.median(_A) if _A else 1500.0
MED_HP_B = statistics.median(_B) if _B else 220.0
MED_ATK_A = statistics.median(_AA) if _AA else 130.0
MED_ATK_B = statistics.median(_AB) if _AB else 20.0


def _row_for(bid):
    row = _BY_CLIENT.get(bid)
    if row:
        return row
    return _BY_NORM.get(_norm(bid))


def stats_for(bid, rank=1, level=1):
    rank = max(1, int(rank or 1))
    level = max(1, int(level or 1))
    row = _row_for(bid)
    page = (row or {}).get("wiki_page")
    fit = _FITS.get(page)
    if fit:
        hp = fit["hp"]["a_rank"] * rank + fit["hp"]["b_level"] * level + fit["hp"]["c"]
        atk = fit["atk"]["a_rank"] * rank + fit["atk"]["b_level"] * level + fit["atk"]["c"]
        source = "[DERIVED] wiki rank/level fit"
        uncertainty = round(max(fit["hp"].get("rmse", 0) / max(hp, 1), 0) * 100, 1)
    elif row and row.get("level1_hp") and row.get("level1_attack"):
        hp = row["level1_hp"] + MED_HP_A * (rank - 1) + MED_HP_B * (level - 1)
        atk = row["level1_attack"] + MED_ATK_A * (rank - 1) + MED_ATK_B * (level - 1)
        source = "[DERIVED] wiki level1 + median growth"
        uncertainty = 12.0
    else:
        hp = 800 + rank * 200 + level * 50
        atk = 80 + rank * 30 + level * 5
        source = "[ASSUMED] placeholder formula"
        uncertainty = 40.0
    hp = max(1, int(round(hp)))
    atk = max(1, int(round(atk)))
    if rank == 1 and level == 1 and page in _RATING1:
        rating = _RATING1[page]
        rating_hp = int(hp * 0.1)
        rating_attack = max(0, rating - rating_hp)
        rating_source = "[WIKI] rank1/level1 row"
    else:
        rating = int(hp * 0.1 + atk * 0.5)
        rating_hp = int(hp * 0.1)
        rating_attack = max(0, rating - rating_hp)
        rating_source = "[ASSUMED] placeholder split"
    return {
        "hp": hp,
        "attack": atk,
        "rating": rating,
        "rating_hp": rating_hp,
        "rating_attack": rating_attack,
        "rating_hp_base": rating_hp,
        "rating_attack_base": rating_attack,
        "source": source,
        "rating_source": rating_source,
        "uncertainty_pct": uncertainty,
        "wiki_page": page or "",
    }


def _apply_hero(hero, bid=None):
    if not isinstance(hero, dict):
        return
    bid = bid or hero.get("bid") or hero.get("blueprint") or hero.get("hero")
    if not bid:
        return
    rank = int(hero.get("rank", 1) or 1)
    level = int(hero.get("level", 1) or 1)
    s = stats_for(bid, rank, level)
    attr = hero.get("attributeData")
    if isinstance(attr, dict):
        attr["hpMaxBase"] = s["hp"]
        attr["hpMax"] = s["hp"]
        attr["hp"] = float(s["hp"])
        attr["attack"] = s["attack"]
        attr["attackBase"] = s["attack"]
        attr["HPMax"] = s["hp"]
        attr["Attack"] = s["attack"]
        attr["heroRating"] = s["rating"]
        attr["HeroRating"] = s["rating"]
        attr["heroRatingHP"] = s["rating_hp"]
        attr["heroRatingAttack"] = s["rating_attack"]
        attr["heroRatingHPBase"] = s["rating_hp_base"]
        attr["heroRatingAttackBase"] = s["rating_attack_base"]
    hero["hp"] = float(s["hp"])
    hero["max_hp"] = float(s["hp"])
    hero["maxHP"] = float(s["hp"])
    hero["HPMax"] = s["hp"]
    hero["attack"] = s["attack"]
    hero["Attack"] = s["attack"]
    hero["heroRating"] = s["rating"]
    hero["hero_rating"] = s["rating"]
    hero["pi"] = s["rating"]
    hero["hero_rating_hp"] = s["rating_hp"]
    hero["hero_rating_attack"] = s["rating_attack"]
    hero["rating"] = s["rating"]
    hero["stat_source"] = s["source"]
    hero["rating_source"] = s["rating_source"]
    hero["stat_uncertainty_pct"] = s["uncertainty_pct"]


def _walk_heroes(obj):
    if isinstance(obj, dict):
        if obj.get("bid") or obj.get("blueprint") or obj.get("hero"):
            _apply_hero(obj)
        for v in obj.values():
            _walk_heroes(v)
    elif isinstance(obj, list):
        for v in obj:
            _walk_heroes(v)


def enrich_login_data(data):
    """Patch a login/user-data payload in place with wiki stats."""
    if not isinstance(data, dict):
        return data
    _walk_heroes(data)
    return data
