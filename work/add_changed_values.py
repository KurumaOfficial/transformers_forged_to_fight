import json, os, re, glob, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"."
W = os.path.join(ROOT, "data", "wiki")
VER = os.path.join(W, "versions")
summary = json.load(open(os.path.join(W, "versions.json"), encoding="utf-8"))

def kv(line):
    l = line.strip().lstrip("*#|").strip()
    if "=" in l:
        k, v = l.split("=", 1)
    elif ":" in l:
        k, v = l.split(":", 1)
    else:
        return None
    k = re.sub(r"\[\[|\]\]|'''|''", "", k).strip().lower()
    v = re.sub(r"\[\[|\]\]|'''|''", "", v).strip()
    if not k or not v:
        return None
    return k, v

def values(text):
    out = {}
    for line in text.splitlines():
        r = kv(line)
        if r:
            out.setdefault(r[0], r[1])
    return out

for f in glob.glob(os.path.join(VER, "*.json")):
    d = json.load(open(f, encoding="utf-8"))
    a = values(d.get("as_of_content", ""))
    b = values(d.get("latest_content", ""))
    diff = []
    for k in sorted(set(a) | set(b)):
        if a.get(k) != b.get(k):
            diff.append({"field": k, "as_of": a.get(k), "latest": b.get(k)})
    d["changed_values"] = diff
    json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if d["page"] in summary["pages"]:
        summary["pages"][d["page"]]["changed_values"] = diff
    for row in summary["changed_pages"]:
        if row["page"] == d["page"]:
            row["changed_values"] = diff
json.dump(summary, open(os.path.join(W, "versions.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("done", len(summary["changed_pages"]))
print(json.dumps(summary["changed_pages"][0].get("changed_values", [])[:5], ensure_ascii=False, indent=1))
