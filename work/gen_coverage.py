import json, os, collections, sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"."
W = os.path.join(ROOT, "archive", "wiki")
state = json.load(open(os.path.join(W, "state.json"), encoding="utf-8"))
manifest = json.load(open(os.path.join(W, "manifest.json"), encoding="utf-8"))
errors = json.load(open(os.path.join(W, "errors.json"), encoding="utf-8"))

# enumerated Fandom pages by namespace
enum = {}
for fn in os.listdir(os.path.join(W, "meta")):
    if fn.startswith("allpages_fandom_") and fn.endswith(".json"):
        ns = fn[len("allpages_fandom_"):-5]
        enum[ns] = len(json.load(open(os.path.join(W, "meta", fn), encoding="utf-8")))
fandom_total = sum(enum.values())

# saved pages by wiki/ns, revision count
saved = collections.Counter()
revs = 0
html = 0
fandom_saved = 0
tf_saved = 0
for key, v in state["pages"].items():
    wiki = key.split("|", 1)[0]
    saved[(wiki, str(v.get("ns")))] += 1
    if wiki == "fandom":
        fandom_saved += 1
    else:
        tf_saved += 1
    if v.get("html"):
        html += 1
    fn = os.path.join(W, v.get("file", ""))
    if os.path.exists(fn):
        try:
            revs += len(json.load(open(fn, encoding="utf-8")).get("revisions", []))
        except Exception:
            pass

imgs = json.load(open(os.path.join(W, "meta", "allimages_fandom.json"), encoding="utf-8"))
cats = json.load(open(os.path.join(W, "meta", "allcategories_fandom.json"), encoding="utf-8"))
redirs = json.load(open(os.path.join(W, "meta", "allredirects_fandom.json"), encoding="utf-8"))

# unparsed list: every raw page, because parser pass has not run
unparsed = []
for key, v in sorted(state["pages"].items()):
    wiki, title = key.split("|", 1)
    unparsed.append({"wiki": wiki, "title": title, "ns": v.get("ns"),
                     "reason": "parser pass not run; raw revisions/HTML only"})
os.makedirs(os.path.join(W, "unparsed"), exist_ok=True)
json.dump(unparsed, open(os.path.join(W, "unparsed", "pages.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
with open(os.path.join(W, "unparsed", "README.md"), "w", encoding="utf-8") as f:
    f.write("# Unparsed wiki pages\n\n")
    f.write("The raw archive is stored; the parser pass has not been run. Every saved page is\n")
    f.write("listed in `pages.json` with reason `parser pass not run`. No game values were\n")
    f.write("invented or copied into `data/wiki/`.\n")

lines = []
lines.append("# COVERAGE_WIKI\n")
lines.append(f"Generated: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")
lines.append("## Fandom\n")
lines.append(f"- Enumerated pages: **{fandom_total}** across {len(enum)} namespaces.")
lines.append(f"- Saved pages (full revision history + rendered HTML): **{fandom_saved}**.")
lines.append(f"- Revisions stored: **{revs}**; HTML snapshots: **{html}**.")
lines.append(f"- allredirects: **{len(redirs)}**; allcategories: **{len(cats)}**; allimages: **{len(imgs)}**.")
lines.append(f"- Images downloaded: **{len(state.get('files', {}))}** of {len(imgs)}.")
lines.append(f"- Manifest entries: **{len(manifest)}**; errors: **{len(errors)}**.")
lines.append("- Namespaces enumerated (page counts): " + ", ".join(f"{k}:{v}" for k, v in sorted(enum.items(), key=lambda x: int(x[0]))) + ".")
lines.append("- Saved by namespace: " + ", ".join(f"{k}:{v}" for (w, k), v in sorted(saved.items(), key=lambda x: (x[0][0], int(x[0][1]))) if w == "fandom") + ".")
lines.append("")
lines.append("## TFWiki (mirror)\n")
lines.append(f"- Whole wiki reports 139066 pages, but only FTF-related pages were selected.")
lines.append(f"- Saved pages: **{tf_saved}**; full revision history + HTML.")
lines.append("- Titles: " + ", ".join(k.split("|", 1)[1] for k in sorted(state["pages"]) if k.startswith("tfwiki|")) + ".")
lines.append("")
lines.append("## Extensions\n")
for name in ["fandom", "tfwiki"]:
    d = json.load(open(os.path.join(W, "meta", f"siteinfo_{name}.json"), encoding="utf-8"))
    ex = [e.get("name") for e in d.get("query", {}).get("extensions", [])]
    lines.append(f"- {name}: Scribunto={'Scribunto' in ex}; Cargo={'Cargo' in ex}; extensions={len(ex)}.")
lines.append("- Fandom `Module:` (ns 828) pages enumerated: 0.")
lines.append("")
lines.append("## Parsed game data\n")
lines.append("- **0 pages parsed.** The parser pass has not been run; only raw revisions/HTML were saved.")
lines.append("- `data/wiki/` contains no invented values; see `README.md` there.")
lines.append("- Unparsed list: `archive/wiki/unparsed/pages.json` (all saved pages).")
lines.append("")
lines.append("## What is closed / not closed\n")
lines.append("- Closed (raw): page lists, revision history, rendered HTML for saved pages, siteinfo, extension presence, image list.")
lines.append("- Not closed: all 3613 Fandom pages (File ns6 mostly), all 2752 image binaries, TFWiki categories/redirects beyond FTF titles, parser/extraction of bot stats/abilities/events, hidden base stats (crit/armor/block).")
lines.append("- No claim of full coverage; `state.json` is resumable.")
open(os.path.join(ROOT, "COVERAGE_WIKI.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines[:20]))
