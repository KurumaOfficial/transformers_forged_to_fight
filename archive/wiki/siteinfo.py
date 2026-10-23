import urllib.request, urllib.parse, json, os, sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
UA = "TFTF-offline-archive/0.1 (personal preservation; polite; contact: local-user)"
OUT = r"C:\Users\gameg\Desktop\TFTF\archive\wiki\meta"
os.makedirs(OUT, exist_ok=True)

def api(base, params):
    params = dict(params)
    params.setdefault("format", "json")
    params.setdefault("formatversion", "2")
    params.setdefault("maxlag", "5")
    url = base + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

for name, base in [("fandom", "https://transformers-forged-to-fight.fandom.com/api.php"),
                   ("tfwiki", "https://tfwiki.duckdns.org/api.php")]:
    try:
        d = api(base, {"action": "query", "meta": "siteinfo",
                       "siprop": "general|namespaces|namespacealiases|extensions|statistics"})
        with open(os.path.join(OUT, f"siteinfo_{name}.json"), "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        q = d.get("query", {})
        gen = q.get("general", {})
        ns = q.get("namespaces", {})
        ext = q.get("extensions", [])
        print(name, "sitename", gen.get("sitename"), "pages", q.get("statistics", {}).get("pages"),
              "namespaces", len(ns), "extensions", [e.get("name") for e in ext][:20])
        print("  namespaces:", [(k, v.get("name")) for k, v in ns.items()][:25])
    except Exception as e:
        print(name, "ERROR", repr(e))
    time.sleep(1)
