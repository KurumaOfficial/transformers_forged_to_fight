import json, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"."
W = os.path.join(ROOT, "data", "wiki")
bots = json.load(open(os.path.join(W, "bots.json"), encoding="utf-8"))["bots"]
m = json.load(open(os.path.join(W, "bot_matrix.json"), encoding="utf-8"))
for row in m["rows"]:
    b = bots[row["bot"]]
    row["stars"] = b.get("stars", {})
    row["stat_table_rows"] = b.get("stat_tables", [])
    row["ability_pairs"] = b.get("abilities", {}).get("pairs", [])
    row["signature_name"] = b.get("signature", {}).get("name", "")
json.dump(m, open(os.path.join(W, "bot_matrix.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("augmented")
