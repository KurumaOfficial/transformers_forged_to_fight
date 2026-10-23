import urllib.request, urllib.parse, json, re, sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
UA = "TFTF-offline-archive/0.1 (personal preservation)"
BASE = "https://transformers-forged-to-fight.fandom.com/api.php"

def api(p):
    p = dict(p); p.update({"format": "json", "formatversion": "2"})
    req = urllib.request.Request(BASE + "?" + urllib.parse.urlencode(p), headers={"User-Agent": UA})
    return json.load(urllib.request.urlopen(req, timeout=60))

terms = ["collection", "assets", "unity files", "google drive", "mega.nz", "download", "archive", "models"]
for term in terms:
    d = api({"action": "query", "list": "search", "srsearch": term, "srlimit": "20",
             "srnamespace": "0|2|4|6|10|12|14|500|502"})
    q = d.get("query", {})
    print("===", term, "total", q.get("searchinfo", {}).get("totalhits"))
    for r in q.get("search", []):
        print(" ", r.get("ns"), r.get("title"))
    time.sleep(0.6)
