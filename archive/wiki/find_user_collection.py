import urllib.request, urllib.parse, json, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
UA = "TFTF-offline-archive/0.1 (personal preservation)"
BASE = "https://transformers-forged-to-fight.fandom.com/api.php"

def api(p):
    p = dict(p); p.update({"format": "json", "formatversion": "2"})
    req = urllib.request.Request(BASE + "?" + urllib.parse.urlencode(p), headers={"User-Agent": UA})
    return json.load(urllib.request.urlopen(req, timeout=60))

for title in ["User:KRBrickBot", "User:TransformersFan02830", "User:KRBrickBot/", "User:TransformersFan02830/"]:
    try:
        d = api({"action": "parse", "page": title, "prop": "text|externallinks|links"})
    except Exception as e:
        print(title, "ERR", e); continue
    p = d.get("parse", {})
    print("===", title, "html", len(p.get("text", "") or ""))
    for l in p.get("externallinks", []):
        print(" EXT", l)
    for l in p.get("links", []):
        t = l.get("title", "")
        if any(k in t.lower() for k in ["collection", "asset", "file", "image", "download", "archive"]):
            print(" LINK", t)
    # raw content
    d2 = api({"action": "query", "prop": "revisions", "rvprop": "content|ids|timestamp",
              "rvslots": "main", "titles": title, "rvlimit": "1"})
    pages = d2.get("query", {}).get("pages", [])
    if pages:
        rev = pages[0].get("revisions", [{}])[0]
        wt = rev.get("slots", {}).get("main", {}).get("content", "")
        print(" wikitext", len(wt))
        for m in re.findall(r"https?://[^\s\]\|}]+", wt):
            print(" URL", m)
