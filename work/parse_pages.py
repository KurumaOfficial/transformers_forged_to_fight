import json, glob, re, os, sys
from urllib.parse import quote
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"."
SRC = os.path.join(ROOT, "archive", "wiki", "raw", "fandom", "revisions", "0")
OUT = os.path.join(ROOT, "data", "wiki")
os.makedirs(OUT, exist_ok=True)
bots = json.load(open(os.path.join(OUT, "bots.json"), encoding="utf-8"))["bots"]

def clean(s):
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\[\[File:[^\]]+\]\]", "", s, flags=re.I)
    s = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", s)
    s = re.sub(r"\[\[([^\]]+)\]\]", r"\1", s)
    s = s.replace("'''", "").replace("''", "")
    s = s.replace("&nbsp;", " ").replace("&amp;", "&")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def parse_tables(block):
    out = []
    for m in re.finditer(r"(?ms)\{\|.*?\|\}", block):
        rows, cur = [], []
        for line in m.group(0).splitlines():
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
                for c in re.split(r"\|\||!!", line[1:]):
                    cur.append(clean(c))
        if rows:
            out.append(rows)
    return out

def infobox(text):
    m = re.search(r"(?is)\{\{Infobox[^}\n]*(.*?)\n?\}\}", text)
    if not m:
        return {}
    d = {}
    for line in m.group(1).splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            k = k.strip().lstrip("|").strip()
            if k:
                d[k] = clean(v)
    return d

pages = {}
for f in sorted(glob.glob(os.path.join(SRC, "*.json"))):
    d = json.load(open(f, encoding="utf-8"))
    title = d["title"]
    if title in bots:
        continue
    rev = d["revisions"][0]
    text = rev["slots"]["main"]["content"]
    heads = list(re.finditer(r"(?m)^(={2,4})\s*(.*?)\s*\1\s*$", text))
    sections = []
    for i, m in enumerate(heads):
        start = m.end()
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        body = text[start:end]
        sections.append({
            "level": len(m.group(1)),
            "heading": clean(m.group(2)),
            "text": clean(body),
            "tables": parse_tables(body),
        })
    pages[title] = {
        "source": {
            "wiki": "fandom",
            "page": title,
            "url": "https://transformers-forged-to-fight.fandom.com/wiki/" + quote(title.replace(" ", "_")),
            "revid": rev.get("revid"),
            "timestamp": rev.get("timestamp"),
            "tag": "[WIKI]",
        },
        "infobox": infobox(text),
        "lead": clean(re.split(r"(?m)^==+", text, 1)[0]),
        "sections": sections,
    }

out = {
    "source": "Fandom Transformers: Forged to Fight Wiki (CC BY-SA where applicable)",
    "method": "generic parse of saved raw wikitext; page/revid/url on every entry",
    "note": "Tables and section text are verbatim-derived; no values are invented.",
    "pages": pages,
}
p = os.path.join(OUT, "pages.json")
json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("pages", len(pages), "out", p)
print("sample", list(pages)[:10])
