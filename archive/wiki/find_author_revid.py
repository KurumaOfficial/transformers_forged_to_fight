import urllib.request, urllib.parse, json, sys, hashlib, os, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
UA = "TFTF-offline-archive/0.1 (personal preservation)"
BASE = "https://transformers-forged-to-fight.fandom.com/api.php"

def api(p):
    p = dict(p); p.update({"format": "json", "formatversion": "2"})
    req = urllib.request.Request(BASE + "?" + urllib.parse.urlencode(p), headers={"User-Agent": UA})
    return json.load(urllib.request.urlopen(req, timeout=60))

title = "User:KRBrickBot"
d = api({"action": "query", "prop": "revisions", "rvprop": "ids|timestamp|user|content",
         "rvslots": "main", "titles": title, "rvlimit": "1"})
page = d["query"]["pages"][0]
rev = page["revisions"][0]
wt = rev["slots"]["main"]["content"]
out = {
    "title": title,
    "url": "https://transformers-forged-to-fight.fandom.com/wiki/User:KRBrickBot",
    "revid": rev["revid"],
    "timestamp": rev["timestamp"],
    "user": rev["user"],
    "collection_url": "https://1drv.ms/u/s!ApD2f3dIXZ_7yjf4KMB9YQzgWQCG?e=jiLxKN",
    "evidence": "external link on User:KRBrickBot; also referenced by Tutorial/Getting Started With the Game's Unity Files and Assets",
}
os.makedirs(r"C:\Users\gameg\Desktop\TFTF\archive\wiki\meta", exist_ok=True)
p = r"C:\Users\gameg\Desktop\TFTF\archive\wiki\meta\author_collection.json"
with open(p, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
