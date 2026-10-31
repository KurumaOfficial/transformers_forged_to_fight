import json, glob, os, re, hashlib, sys
from urllib.parse import quote
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"."
SRC = os.path.join(ROOT, "archive", "wiki", "raw", "fandom", "revisions", "0")
OUT = os.path.join(ROOT, "data", "wiki")
VER = os.path.join(OUT, "versions")
os.makedirs(VER, exist_ok=True)
CUTOFF = "2023-01-13T23:59:59Z"

def safe(t):
    return quote(t.replace("/", "_"), safe="")

def headings(text):
    return set(m.group(2).strip() for m in re.finditer(r"(?m)^(={2,4})\s*(.*?)\s*\1\s*$", text))

def interesting_lines(text):
    out = []
    for line in text.splitlines():
        l = line.strip()
        if re.search(r"(?i)(health|attack|max rating|rank|level|signature|ability|abilities|synergy|release date|forge|crit|armor|block)", l):
            out.append(l)
    return out

pages = {}
created_after = []
changed = []
for f in sorted(glob.glob(os.path.join(SRC, "*.json"))):
    d = json.load(open(f, encoding="utf-8"))
    title = d["title"]
    revs = d.get("revisions", [])
    if not revs:
        continue
    latest = revs[0]
    as_of = None
    for r in revs:
        if (r.get("timestamp") or "") <= CUTOFF:
            as_of = r
            break
    lt = latest.get("slots", {}).get("main", {}).get("content", "")
    at = as_of.get("slots", {}).get("main", {}).get("content", "") if as_of else ""
    if as_of is None:
        created_after.append(title)
    changed_flag = hashlib.sha256(at.encode("utf-8")).hexdigest() != hashlib.sha256(lt.encode("utf-8")).hexdigest()
    h_add = sorted(headings(lt) - headings(at))
    h_del = sorted(headings(at) - headings(lt))
    line_diff = []
    if changed_flag:
        old_lines = set(interesting_lines(at))
        new_lines = set(interesting_lines(lt))
        line_diff = sorted(new_lines - old_lines)[:50]
    rec = {
        "page": title,
        "url": "https://transformers-forged-to-fight.fandom.com/wiki/" + quote(title.replace(" ", "_")),
        "latest_revid": latest.get("revid"),
        "latest_timestamp": latest.get("timestamp"),
        "as_of_revid": as_of.get("revid") if as_of else None,
        "as_of_timestamp": as_of.get("timestamp") if as_of else None,
        "created_after_cutoff": as_of is None,
        "changed": changed_flag,
        "headings_added": h_add,
        "headings_removed": h_del,
        "new_interesting_lines": line_diff,
        "as_of_content": at,
        "latest_content": lt,
        "tag": "[WIKI]",
    }
    pages[title] = rec
    fn = os.path.join(VER, safe(title) + ".json")
    json.dump(rec, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if changed_flag:
        changed.append({"page": title, "as_of_revid": rec["as_of_revid"],
                        "latest_revid": rec["latest_revid"],
                        "headings_added": h_add, "headings_removed": h_del,
                        "new_interesting_lines": line_diff})

summary = {
    "cutoff": CUTOFF,
    "source": "Fandom full-history revisions saved under archive/wiki/raw/fandom/revisions/0/",
    "note": "as_of = latest revision at/before cutoff; latest = newest saved revision. File: pages have only latest descriptions and are excluded.",
    "pages_analyzed": len(pages),
    "changed_count": len(changed),
    "created_after_cutoff": sorted(created_after),
    "changed_pages": changed,
    "pages": {k: {kk: v[kk] for kk in ["latest_revid","latest_timestamp","as_of_revid","as_of_timestamp","created_after_cutoff","changed","headings_added","headings_removed"]} for k, v in pages.items()},
}
json.dump(summary, open(os.path.join(OUT, "versions.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("pages", len(pages), "changed", len(changed), "created_after", len(created_after))
print("created_after", sorted(created_after)[:20])
print("sample changed", changed[:3])
