import urllib.request, urllib.parse, json, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
UA = "TFTF-offline-archive/0.1 (personal preservation)"
BASE = "https://transformers-forged-to-fight.fandom.com/api.php"

def api(p):
    p = dict(p); p.update({"format": "json", "formatversion": "2"})
    return json.load(urllib.request.urlopen(
        urllib.request.Request(BASE + "?" + urllib.parse.urlencode(p), headers={"User-Agent": UA}),
        timeout=60))

for title in ["Transformers: Forged to Fight Wiki", "Transformers Forged to Fight Wiki"]:
    try:
        d = api({"action": "parse", "page": title, "prop": "text|links|images"})
    except Exception as e:
        print(title, "ERR", e); continue
    p = d.get("parse", {})
    html = p.get("text", "") or ""
    print("===", title, "html", len(html), "links", len(p.get("links", [])))
    for m in re.findall(r'href="([^"]+)"', html):
        if any(k in m.lower() for k in ["user", "image", "file", "collection", "asset", "download", "archive", "special:"]):
            print("HREF", m)
    for l in p.get("links", []):
        t = l.get("title", "")
        if any(k in t.lower() for k in ["user", "image", "file", "collection", "asset", "download", "archive"]):
            print("LINK", t)
