import urllib.request, urllib.parse, json, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
UA = "TFTF-offline-archive/0.1 (personal preservation)"
BASE = "https://transformers-forged-to-fight.fandom.com/api.php"

def api(p):
    p = dict(p); p.update({"format": "json", "formatversion": "2"})
    req = urllib.request.Request(BASE + "?" + urllib.parse.urlencode(p), headers={"User-Agent": UA})
    return json.load(urllib.request.urlopen(req, timeout=60))

d = api({"action": "parse", "page": "Main Page", "prop": "text|links|images"})
p = d["parse"]
html = p.get("text", "") or ""
print("html len", len(html))
for m in re.findall(r'href="([^"]+)"', html):
    if any(k in m.lower() for k in ["user", "image", "file", "collection", "asset", "download", "archive", "special:"]):
        print(m)
print("links", len(p.get("links", [])))
for l in p.get("links", [])[:50]:
    print(l)
