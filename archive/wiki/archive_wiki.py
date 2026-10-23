import urllib.request, urllib.parse, json, os, sys, time, hashlib, re, argparse

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\Users\gameg\Desktop\TFTF\archive\wiki"
UA = "TFTF-offline-archive/0.1 (personal preservation; polite; contact: local-user)"
WIKIS = {
    "fandom": "https://transformers-forged-to-fight.fandom.com/api.php",
    "tfwiki": "https://tfwiki.duckdns.org/api.php",
}
STATE_PATH = os.path.join(ROOT, "state.json")
MANIFEST_PATH = os.path.join(ROOT, "manifest.json")
ERRORS_PATH = os.path.join(ROOT, "errors.json")


def load_json(path, default):
    if os.path.exists(path):
        try:
            return json.load(open(path, encoding="utf-8"))
        except Exception:
            pass
    return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


state = load_json(STATE_PATH, {"pages": {}, "files": {}, "lists": {}, "done": []})
manifest = load_json(MANIFEST_PATH, [])
errors = load_json(ERRORS_PATH, [])


def api(base, params, retries=4):
    params = dict(params)
    params.setdefault("format", "json")
    params.setdefault("formatversion", "2")
    params.setdefault("maxlag", "5")
    url = base + "?" + urllib.parse.urlencode(params)
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.load(r)
            if isinstance(d, dict) and d.get("error"):
                code = d["error"].get("code")
                if code == "maxlag":
                    time.sleep(2 + attempt * 2)
                    continue
                raise RuntimeError(f"API error {code}: {d['error'].get('info')}")
            return d
        except Exception as e:
            last = e
            time.sleep(1.5 + attempt * 2)
    raise last


def safe_name(title):
    return urllib.parse.quote(title.replace("/", "_"), safe="")


def add_manifest(path, source, revid=None):
    if not os.path.exists(path):
        return
    b = open(path, "rb").read()
    manifest.append({
        "path": os.path.relpath(path, ROOT).replace("\\", "/"),
        "sha256": hashlib.sha256(b).hexdigest(),
        "size": len(b),
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": source,
        "revid": revid,
    })
    save_json(MANIFEST_PATH, manifest)


def allpages(base, ns, budget_end):
    key = f"allpages_{ns}"
    cont = state["lists"].get(key, {}).get("continue")
    out = state["lists"].get(key, {}).get("items", [])
    seen = {x["title"] for x in out}
    while time.time() < budget_end:
        p = {"action": "query", "list": "allpages", "apnamespace": ns, "aplimit": "max"}
        if cont:
            p["apcontinue"] = cont
        d = api(base, p)
        q = d.get("query", {})
        for it in q.get("allpages", []):
            if it["title"] not in seen:
                out.append(it); seen.add(it["title"])
        cont = d.get("continue", {}).get("apcontinue")
        state["lists"][key] = {"items": out, "continue": cont}
        save_json(STATE_PATH, state)
        if not cont:
            break
        time.sleep(0.5)
    return out


def list_simple(base, listname, key, extra=None, budget_end=None):
    cont = state["lists"].get(key, {}).get("continue")
    out = state["lists"].get(key, {}).get("items", [])
    prefixes = {"allredirects": ("arlimit", "arcontinue"),
                "allcategories": ("aclimit", "accontinue"),
                "allimages": ("ailimit", "aicontinue")}
    limit_param, cont_param = prefixes.get(listname, ("limit", "continue"))
    while budget_end is None or time.time() < budget_end:
        p = {"action": "query", "list": listname, limit_param: "max"}
        if extra:
            p.update(extra)
        if cont:
            p[cont_param] = cont
        d = api(base, p)
        q = d.get("query", {})
        for it in q.get(listname, []):
            out.append(it)
        cont = d.get("continue", {}).get(cont_param)
        state["lists"][key] = {"items": out, "continue": cont}
        save_json(STATE_PATH, state)
        if not cont:
            break
        time.sleep(0.5)
    return out


def fetch_page(base, wiki, title, ns, budget_end):
    key = f"{wiki}|{title}"
    if key in state["pages"] and state["pages"][key].get("complete"):
        return
    outdir = os.path.join(ROOT, "raw", wiki, "revisions", str(ns))
    os.makedirs(outdir, exist_ok=True)
    fn = os.path.join(outdir, safe_name(title) + ".json")
    data = load_json(fn, {"wiki": wiki, "title": title, "ns": ns, "revisions": []})
    cont = data.get("continue")
    while time.time() < budget_end:
        p = {"action": "query", "prop": "revisions",
             "rvprop": "ids|timestamp|user|comment|content", "rvslots": "main",
             "rvlimit": "max", "titles": title}
        if cont:
            p["rvcontinue"] = cont
        d = api(base, p)
        pages = d.get("query", {}).get("pages", [])
        if not pages:
            break
        page = pages[0]
        for r in page.get("revisions", []):
            data["revisions"].append(r)
        cont = d.get("continue", {}).get("rvcontinue")
        data["continue"] = cont
        save_json(fn, data)
        if not cont:
            break
        time.sleep(0.4)
    if not cont:
        data["complete"] = True
        save_json(fn, data)
        add_manifest(fn, base, data["revisions"][0].get("revid") if data["revisions"] else None)
    state["pages"][key] = {"ns": ns, "complete": not cont, "file": os.path.relpath(fn, ROOT)}
    save_json(STATE_PATH, state)


def fetch_html(base, wiki, title, ns, budget_end):
    key = f"{wiki}|{title}"
    if state["pages"].get(key, {}).get("html"):
        return
    outdir = os.path.join(ROOT, "raw", wiki, "html", str(ns))
    os.makedirs(outdir, exist_ok=True)
    fn = os.path.join(outdir, safe_name(title) + ".html")
    meta_fn = os.path.join(outdir, safe_name(title) + ".meta.json")
    d = api(base, {"action": "parse", "page": title,
                   "prop": "text|categories|templates|links|images"})
    p = d.get("parse", {})
    html = p.get("text", "") or ""
    with open(fn, "w", encoding="utf-8") as f:
        f.write(html)
    save_json(meta_fn, {"title": title, "ns": ns, "categories": p.get("categories", []),
                        "templates": p.get("templates", []), "links": p.get("links", []),
                        "images": p.get("images", [])})
    add_manifest(fn, base)
    state["pages"].setdefault(key, {})["html"] = True
    save_json(STATE_PATH, state)


def download_file(url, wiki, name, budget_end):
    key = f"{wiki}|{name}"
    if key in state["files"] and state["files"][key].get("complete"):
        return
    outdir = os.path.join(ROOT, "raw", wiki, "files")
    os.makedirs(outdir, exist_ok=True)
    fn = os.path.join(outdir, safe_name(name))
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36", "Referer": "https://transformers-forged-to-fight.fandom.com/"})
            with urllib.request.urlopen(req, timeout=120) as r:
                b = r.read()
            with open(fn, "wb") as f:
                f.write(b)
            add_manifest(fn, url)
            state["files"][key] = {"complete": True, "file": os.path.relpath(fn, ROOT)}
            save_json(STATE_PATH, state)
            return
        except Exception as e:
            if attempt == 2:
                errors.append({"file": name, "url": url, "error": repr(e)})
                save_json(ERRORS_PATH, errors)
            time.sleep(2 + attempt * 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="meta")
    ap.add_argument("--minutes", type=float, default=10)
    ap.add_argument("--wiki", default="all", choices=["all", "fandom", "tfwiki"])
    args = ap.parse_args()
    budget_end = time.time() + args.minutes * 60
    for wiki, base in WIKIS.items():
        if args.wiki != "all" and wiki != args.wiki:
            continue
        if args.phase in ("meta", "all"):
            d = api(base, {"action": "query", "meta": "siteinfo",
                           "siprop": "general|namespaces|namespacealiases|extensions|statistics"})
            save_json(os.path.join(ROOT, "meta", f"siteinfo_{wiki}.json"), d)
            print(wiki, "siteinfo saved")
            for listname, key, extra in [
                ("allredirects", f"allredirects_{wiki}", {}),
                ("allcategories", f"allcategories_{wiki}", {}),
                ("allimages", f"allimages_{wiki}", {}),
            ]:
                if time.time() >= budget_end:
                    break
                try:
                    items = list_simple(base, listname, key, extra, budget_end)
                    save_json(os.path.join(ROOT, "meta", f"{key}.json"), items)
                    print(wiki, key, len(items))
                except Exception as e:
                    errors.append({"list": key, "error": repr(e)})
                    save_json(ERRORS_PATH, errors)
            # allpages for every namespace
            ns_map = d.get("query", {}).get("namespaces", {})
            for ns in ns_map:
                if wiki == "tfwiki":
                    continue
                if int(ns) < 0 or time.time() >= budget_end:
                    continue
                try:
                    items = allpages(base, int(ns), budget_end)
                    save_json(os.path.join(ROOT, "meta", f"allpages_{wiki}_{ns}.json"), items)
                    print(wiki, "ns", ns, "pages", len(items))
                except Exception as e:
                    errors.append({"ns": ns, "wiki": wiki, "error": repr(e)})
                    save_json(ERRORS_PATH, errors)
        if args.phase in ("pages", "all"):
            # page list: fandom all namespaces; tfwiki only the FTF search hits
            titles = []
            if wiki == "fandom":
                for fn in os.listdir(os.path.join(ROOT, "meta")):
                    if fn.startswith(f"allpages_fandom_") and fn.endswith(".json"):
                        ns = fn[len("allpages_fandom_"):-5]
                        for it in load_json(os.path.join(ROOT, "meta", fn), []):
                            titles.append((it["title"], int(ns)))
            else:
                for q in ["Forged to Fight", "Crossfire"]:
                    d = api(base, {"action": "query", "list": "search", "srsearch": q,
                                   "srlimit": "50", "srnamespace": "0"})
                    for r in d.get("query", {}).get("search", []):
                        titles.append((r["title"], 0))
            seen = set()
            for title, ns in titles:
                if (wiki, title) in seen or time.time() >= budget_end:
                    continue
                seen.add((wiki, title))
                try:
                    fetch_page(base, wiki, title, ns, budget_end)
                    fetch_html(base, wiki, title, ns, budget_end)
                    time.sleep(0.5)
                except Exception as e:
                    errors.append({"wiki": wiki, "title": title, "error": repr(e)})
                    save_json(ERRORS_PATH, errors)
            print(wiki, "pages pass done/partial")
        if args.phase in ("files", "all"):
            imgs = load_json(os.path.join(ROOT, "meta", f"allimages_{wiki}.json"), [])
            for it in imgs:
                if time.time() >= budget_end:
                    break
                url = it.get("url")
                name = it.get("name") or os.path.basename(urllib.parse.urlparse(url).path)
                if url:
                    download_file(url, wiki, name, budget_end)
                    time.sleep(0.3)
            print(wiki, "files pass done/partial")
    save_json(STATE_PATH, state)
    save_json(MANIFEST_PATH, manifest)
    save_json(ERRORS_PATH, errors)
    print("done. pages tracked", len(state["pages"]), "files tracked", len(state["files"]),
          "manifest", len(manifest), "errors", len(errors))


if __name__ == "__main__":
    main()
