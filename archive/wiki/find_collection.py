import urllib.request, urllib.parse, json, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
UA = "TFTF-offline-archive/0.1 (personal preservation)"
BASE = "https://transformers-forged-to-fight.fandom.com/api.php"

def api(p):
    p = dict(p); p.update({"format": "json", "formatversion": "2"})
    return json.load(urllib.request.urlopen(
        urllib.request.Request(BASE + "?" + urllib.parse.urlencode(p), headers={"User-Agent": UA}),
        timeout=60))

title = "Tutorial/Getting Started With the Game's Unity Files and Assets"
d = api({"action": "parse", "page": title, "prop": "text|links|externallinks|images"})
p = d.get("parse", {})
html = p.get("text", "") or ""
print("html", len(html))
print("externallinks:")
for l in p.get("externallinks", []):
    print(" ", l)
print("links:")
for l in p.get("links", []):
    print(" ", l.get("title"))
print("images:", p.get("images", []))
# also raw wikitext
d2 = api({"action": "query", "prop": "revisions", "rvprop": "content|ids|timestamp|user|comment",
          "rvslots": "main", "titles": title, "rvlimit": "1"})
pages = d2.get("query", {}).get("pages", [])
if pages:
    rev = pages[0].get("revisions", [{}])[0]
    wt = rev.get("slots", {}).get("main", {}).get("content", "")
    print("wikitext len", len(wt))
    for m in re.findall(r'https?://[^\s\]\|}]+', wt):
        print("URL", m)
