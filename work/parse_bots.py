import json, glob, re, os, sys
from urllib.parse import quote
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\Users\gameg\Desktop\TFTF"
SRC = os.path.join(ROOT, "archive", "wiki", "raw", "fandom", "revisions", "0")
OUT = os.path.join(ROOT, "data", "wiki")
os.makedirs(OUT, exist_ok=True)

def clean(s):
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\[\[File:[^\]]+\]\]", "", s, flags=re.I)
    s = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", s)
    s = re.sub(r"\[\[([^\]]+)\]\]", r"\1", s)
    s = s.replace("'''", "").replace("''", "")
    s = s.replace("&nbsp;", " ").replace("&amp;", "&")
    s = re.sub(r"\s+", " ", s)
    return s.strip(" \t\r\n|")

def section(text, heading):
    pat = re.compile(r"(?ms)^==(?!=)\s*" + re.escape(heading) + r"\s*==\s*(.*?)(?=^==(?!=)\s*[^=\n]|\Z)")
    m = pat.search(text)
    return m.group(1) if m else ""

def section_any(text, heading):
    """Match == Heading ==, === Heading ===, or bold heading variants."""
    pat = re.compile(r"(?ms)^={2,4}\s*" + re.escape(heading) + r"\s*={2,4}\s*(.*?)(?=^={2,4}\s*[^=\n]|\Z)")
    m = pat.search(text)
    return m.group(1) if m else ""


def subsection(text, heading):
    pat = re.compile(r"(?ms)^===\s*" + re.escape(heading) + r"\s*===\s*(.*?)(?=^===|\Z)")
    m = pat.search(text)
    return m.group(1) if m else ""

def parse_table(block):
    m = re.search(r"(?ms)\{\|.*?\|\}", block)
    if not m:
        return None
    t = m.group(0)
    rows = []
    cur = []
    for line in t.splitlines():
        line = line.strip()
        if line.startswith("{|"):
            continue
        if line.startswith("|}"):
            if cur:
                rows.append(cur)
            break
        if line.startswith("|-"):
            if cur:
                rows.append(cur)
            cur = []
            continue
        if line.startswith("!") or line.startswith("|"):
            cells = re.split(r"\|\||!!", line[1:])
            for c in cells:
                cur.append(clean(c))
    return rows

def parse_tables(block):
    out = []
    for m in re.finditer(r"(?ms)\{\|.*?\|\}", block):
        rows = []
        cur = []
        for line in m.group(0).splitlines():
            line = line.strip()
            if line.startswith("{|") or line.startswith("|}"):
                if line.startswith("|}") and cur:
                    rows.append(cur); cur = []
                continue
            if line.startswith("|-"):
                if cur:
                    rows.append(cur); cur = []
                continue
            if line.startswith("!") or line.startswith("|"):
                cells = re.split(r"\|\||!!", line[1:])
                for c in cells:
                    cur.append(clean(c))
        if cur:
            rows.append(cur)
        if rows:
            out.append(rows)
    return out

def bullets(block):
    out = []
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("*") or line.startswith("#"):
            v = clean(line.lstrip("*#"))
            if v:
                out.append(v)
    return out

def star_stats(block):
    out = {}
    for star in range(1, 7):
        pat = re.compile(r"(?is)\*?\s*" + str(star) + r"\s*-?\s*Star\s*:?\s*(.*?)(?=\n\*\s*\d\s*-?\s*Star|\n\{|\n==|\Z)")
        m = pat.search(block)
        if not m:
            continue
        body = m.group(1)
        d = {}
        for key, label in [("Health", "health"), ("Attack", "attack"), ("Max Rating", "max_rating")]:
            mm = re.search(r"(?i)" + re.escape(key) + r"\s*:\s*([0-9][0-9,\.~]*)", body)
            if mm:
                d[label] = clean(mm.group(1))
        if d:
            out[str(star)] = d
    return out

bots = {}
skipped = []
for f in sorted(glob.glob(os.path.join(SRC, "*.json"))):
    d = json.load(open(f, encoding="utf-8"))
    title = d["title"]
    if title.startswith("Transformers: Forged to Fight Wiki:"):
        continue
    rev = d["revisions"][0]
    text = rev["slots"]["main"]["content"]
    if "Infobox_character" not in text or not ("==Stats==" in text or "==Max Stats==" in text):
        continue
    infobox = {}
    m = re.search(r"(?is)\{\{Infobox_character(.*?)\}\}", text)
    if m:
        for line in m.group(1).splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                k = k.strip().lstrip("|").strip()
                if k:
                    infobox[k] = clean(v)
    stats_block = section(text, "Stats") or section(text, "Max Stats")
    game = section(text, "Game Abilities")
    sig = subsection(game, "Signature Ability")
    abil = subsection(game, "Abilities")
    basic = subsection(game, "Basic Abilities")
    special = subsection(game, "Special Attacks")
    synergy = section_any(text, "Synergy Bonuses") or section_any(text, "Common Synergies")
    entry = {
        "source": {
            "wiki": "fandom",
            "page": title,
            "url": "https://transformers-forged-to-fight.fandom.com/wiki/" + quote(title.replace(" ", "_")),
            "revid": rev.get("revid"),
            "timestamp": rev.get("timestamp"),
            "tag": "[WIKI]",
        },
        "infobox": infobox,
        "stars": star_stats(stats_block),
        "stat_tables": parse_tables(stats_block),
        "abilities": {
            "basic": bullets(basic),
            "list": bullets(abil),
            "tables": parse_tables(abil),
        },
        "signature": {
            "name": clean(sig.splitlines()[0]) if sig.strip() else "",
            "description": clean(sig.split("\n", 1)[1]) if "\n" in sig else "",
            "tables": parse_tables(sig),
        },
        "special_attacks": bullets(special),
        "synergy": bullets(synergy),
    }
    # drop empty
    if not (entry["stars"] or entry["stat_tables"] or entry["abilities"]["list"] or entry["signature"]["name"]):
        skipped.append(title)
        continue
    bots[title] = entry

out = {
    "source": "Fandom Transformers: Forged to Fight Wiki (CC BY-SA where applicable)",
    "method": "parsed from saved raw wikitext; every page carries page/revid/url",
    "note": "Only values present in the saved wikitext; missing cells stay missing.",
    "bots": bots,
}
p = os.path.join(OUT, "bots.json")
json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("bots", len(bots), "skipped", len(skipped), "out", p)
print("sample", list(bots)[:10])
print("Bumblebee stars", json.dumps(bots.get("Bumblebee", {}).get("stars", {}), ensure_ascii=False))
