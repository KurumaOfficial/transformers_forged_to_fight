import json, os
p = r".\data\wiki\id_map.json"
d = json.load(open(p, encoding="utf-8"))
d["client_with_stat_page"] = sum(1 for r in d["matched"] if r["in_bots_stats"])
d["client_without_stat_page"] = sum(1 for r in d["matched"] if not r["in_bots_stats"])
d["client_without_stat_non_shark"] = sum(1 for r in d["matched"] if not r["in_bots_stats"] and not r["client_id"].startswith("sharkticon_"))
d["sharkticon_variants_without_stat"] = sum(1 for r in d["matched"] if not r["in_bots_stats"] and r["client_id"].startswith("sharkticon_"))
d["wiki_stat_pages"] = len(d["wiki_without_client"]) + d["client_with_stat_page"]
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k:d[k] for k in ["client_pack_count","non_sharkticon_client_count","sharkticon_pack_count","client_with_stat_page","client_without_stat_page","client_without_stat_non_shark","sharkticon_variants_without_stat","wiki_stat_pages","wiki_without_client"]}, ensure_ascii=False, indent=1))
