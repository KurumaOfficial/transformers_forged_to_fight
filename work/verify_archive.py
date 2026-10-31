import json, os, collections, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"."
W = os.path.join(ROOT, "archive", "wiki")
enum = {}
for fn in os.listdir(os.path.join(W, "meta")):
    if fn.startswith("allpages_fandom_") and fn.endswith(".json"):
        enum[fn[len("allpages_fandom_"):-5]] = len(json.load(open(os.path.join(W, "meta", fn), encoding="utf-8")))
state = json.load(open(os.path.join(W, "state.json"), encoding="utf-8"))
saved = collections.Counter()
for k, v in state["pages"].items():
    if k.startswith("fandom|"):
        saved[str(v.get("ns"))] += 1
print("enum total", sum(enum.values()), "file", enum.get("6"), "nonfile", sum(v for k, v in enum.items() if k != "6"))
print("saved total", sum(saved.values()), "file", saved.get("6"), "nonfile", sum(v for k, v in saved.items() if k != "6"))
print("missing file", enum.get("6", 0) - saved.get("6", 0))
print("enum", dict(sorted(enum.items(), key=lambda x: int(x[0]))))
print("saved", dict(sorted(saved.items(), key=lambda x: int(x[0]))))
