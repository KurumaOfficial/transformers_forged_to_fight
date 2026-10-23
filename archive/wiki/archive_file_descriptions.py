import json, os, time, hashlib, urllib.request, urllib.parse, sys, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\Users\gameg\Desktop\TFTF"
W = os.path.join(ROOT, "archive", "wiki")
BASE = "https://transformers-forged-to-fight.fandom.com/api.php"
UA = "TFTF-offline-archive/0.1 (personal preservation; polite; contact: local-user)"
STATE = os.path.join(W, "state.json")
MANIFEST = os.path.join(W, "manifest.json")
state = json.load(open(STATE, encoding="utf-8"))
manifest = json.load(open(MANIFEST, encoding="utf-8"))
titles = [x["title"] for x in json.load(open(os.path.join(W, "meta", "allpages_fandom_6.json"), encoding="utf-8"))]

def api(params):
    params = dict(params); params.update({"format": "json", "formatversion": "2", "maxlag": "5"})
    req = urllib.request.Request(BASE + "?" + urllib.parse.urlencode(params), headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except Exception:
            time.sleep(2 + attempt * 2)
    raise RuntimeError("api failed")

def safe(title):
    return urllib.parse.quote(title.replace("/", "_"), safe="")

outdir = os.path.join(W, "raw", "fandom", "file_descriptions")
os.makedirs(outdir, exist_ok=True)
done = 0
start = time.time()
for i in range(0, len(titles), 50):
    batch = titles[i:i + 50]
    d = api({"action": "query", "prop": "revisions", "rvprop": "ids|timestamp|user|comment|content",
             "rvslots": "main", "titles": "|".join(batch)})
    for page in d.get("query", {}).get("pages", []):
        title = page.get("title")
        rev = (page.get("revisions") or [{}])[0]
        content = rev.get("slots", {}).get("main", {}).get("content", "")
        entry = {"title": title, "pageid": page.get("pageid"), "ns": page.get("ns"),
                 "revid": rev.get("revid"), "timestamp": rev.get("timestamp"),
                 "user": rev.get("user"), "comment": rev.get("comment"), "content": content}
        fn = os.path.join(outdir, safe(title) + ".json")
        with open(fn, "w", encoding="utf-8") as f:
            json.dump(entry, f, ensure_ascii=False, indent=1)
        b = open(fn, "rb").read()
        manifest.append({"path": os.path.relpath(fn, W).replace("\\", "/"),
                         "sha256": hashlib.sha256(b).hexdigest(), "size": len(b),
                         "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                         "source": BASE, "revid": rev.get("revid")})
        done += 1
    print("batch", i // 50 + 1, "of", (len(titles) + 49) // 50, "done", done, flush=True)
    time.sleep(0.25)
json.dump(manifest, open(MANIFEST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("file descriptions", done, "elapsed", round(time.time() - start, 1))
