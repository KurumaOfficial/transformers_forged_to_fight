import json, os, re, time, hashlib, urllib.request, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\Users\gameg\Desktop\TFTF"
W = os.path.join(ROOT, "archive", "wiki")
UA = "TFTF-offline-archive/0.1 (personal preservation; polite; contact: local-user)"
state = json.load(open(os.path.join(W, "state.json"), encoding="utf-8"))
manifest = json.load(open(os.path.join(W, "manifest.json"), encoding="utf-8"))
errors = json.load(open(os.path.join(W, "errors.json"), encoding="utf-8"))
imgs = json.load(open(os.path.join(W, "meta", "allimages_fandom.json"), encoding="utf-8"))
pat = re.compile(r"map|mission|event|screen|stats|table|interface|menu|quest|raid|arena|story|chapter|ui", re.I)
sel = [x for x in imgs if pat.search(x.get("name", ""))]
outdir = os.path.join(W, "raw", "fandom", "files")
os.makedirs(outdir, exist_ok=True)
done = 0
start = time.time()
for it in sel:
    if time.time() - start > 480:
        break
    name = it.get("name") or os.path.basename(it.get("url", ""))
    key = "fandom|" + name
    if key in state["files"] and state["files"][key].get("complete"):
        continue
    url = it.get("url")
    if not url:
        continue
    fn = os.path.join(outdir, urllib.parse.quote(name, safe=""))
    ok = False
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA,
                "Referer": "https://transformers-forged-to-fight.fandom.com/"})
            with urllib.request.urlopen(req, timeout=120) as r:
                b = r.read()
            open(fn, "wb").write(b)
            manifest.append({"path": os.path.relpath(fn, W).replace("\\", "/"),
                             "sha256": hashlib.sha256(b).hexdigest(), "size": len(b),
                             "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                             "source": url, "revid": None})
            state["files"][key] = {"complete": True, "file": os.path.relpath(fn, W)}
            ok = True
            done += 1
            break
        except Exception as e:
            if attempt == 1:
                errors.append({"file": name, "url": url, "error": repr(e)})
            time.sleep(1.5)
    if done % 25 == 0:
        json.dump(state, open(os.path.join(W, "state.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(manifest, open(os.path.join(W, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(errors, open(os.path.join(W, "errors.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    time.sleep(0.35)
json.dump(state, open(os.path.join(W, "state.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(manifest, open(os.path.join(W, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(errors, open(os.path.join(W, "errors.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("downloaded", done, "total state files", len(state["files"]), "errors", len(errors),
      "elapsed", round(time.time() - start, 1))
