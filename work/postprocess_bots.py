import json, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = r".\data\wiki\bots.json"
d = json.load(open(p, encoding="utf-8"))

def pair(items):
    out = []
    i = 0
    while i < len(items):
        s = items[i].strip()
        if s.endswith(":") and i + 1 < len(items):
            out.append({"name": s[:-1].strip(), "description": items[i + 1].strip()})
            i += 2
        else:
            out.append({"text": s})
            i += 1
    return out

for b in d["bots"].values():
    b.setdefault("abilities", {})
    b["abilities"]["pairs"] = pair(b["abilities"].get("list", []))
    b["special_attack_pairs"] = pair(b.get("special_attacks", []))
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("postprocessed", len(d["bots"]))
b = d["bots"]["Bumblebee"]
print(b["abilities"]["pairs"][:2])
