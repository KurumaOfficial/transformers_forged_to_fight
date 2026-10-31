import json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"."
W = os.path.join(ROOT, "data", "wiki")
bots = json.load(open(os.path.join(W, "bots.json"), encoding="utf-8"))["bots"]
pages = json.load(open(os.path.join(W, "pages.json"), encoding="utf-8"))["pages"]
all_titles = set(bots) | set(pages)

client = [
"arcee_gs_deluxe2014","barricade_cin_dotm","blaster_gs_leader2016","bludgeon_gs_rd20",
"bonecrusher_cin_rotf","bumblebee_cin_dotm","bumblebee_gs_kabam","cheetor_bw_transmetal",
"cliffjumper_gs_kabam","cyclonus_gs_uw06","dinobot_bw_kabam","dirge_gs_deluxe2008",
"drift_cin_aoe","galvatron_gs_voyager2016","grimlock_gs_mp08","grindor_cin_rotf",
"hotrod_cin_tlk","hound_cin_tlk","ironhide_cin_rotf","ironhide_gs_kabam","jazz_gs_twm05",
"jetfire_gs_leader2014","kickback_gs_kabam","megatronus_gs_kabam","megatron_cin_rotf",
"megatron_gs_leader2015","mirage_gs_deluxe2016","mixmaster_cin_rotf","motormaster_gs_voyager2015",
"necrotronus_gs_kabam","nemesisprime_gs_voyager2015","optimusprimal_bw_mp32","optimusprime_cin_tf",
"prowl_gs_deluxe2016","ramjet_gs_deluxe2008","ratchet_gs_kabam","rhinox_gs_voyager2014",
"rodimusprime_gs_mp09","scorponok_bw_kabam","sharkticon_gs_brawler","sharkticon_gs_demolition",
"sharkticon_gs_kabam","sharkticon_gs_scout","sharkticon_gs_tactician","sharkticon_gs_tech",
"sharkticon_gs_warrior","shockwave_gs","sideswipe_gs","skywarp_gs_leader2015","slipstream_gs",
"soundblaster_gs_mp13b","soundwave_gs","sunstreaker_gs_deluxe2008","tantrum_gs_kabam",
"thundercracker_gs_leader2015","ultramagnus_gs_leader","waspinator_gs_deluxe","wheeljack_gs_mp20",
"windblade_gs",
]

# manual variants / canonical wiki pages
alias = {
"arcee_gs_deluxe2014":"Arcee",
"barricade_cin_dotm":"Barricade",
"blaster_gs_leader2016":"Blaster",
"bludgeon_gs_rd20":"Bludgeon",
"bonecrusher_cin_rotf":"Bonecrusher",
"bumblebee_cin_dotm":"Bumblebee (DOTM)",
"bumblebee_gs_kabam":"Bumblebee",
"cheetor_bw_transmetal":"Cheetor",
"cliffjumper_gs_kabam":"Cliffjumper",
"cyclonus_gs_uw06":"Cyclonus",
"dinobot_bw_kabam":"Dinobot",
"dirge_gs_deluxe2008":"Dirge",
"drift_cin_aoe":"Drift",
"galvatron_gs_voyager2016":"Galvatron",
"grimlock_gs_mp08":"Grimlock",
"grindor_cin_rotf":"Grindor",
"hotrod_cin_tlk":"Hot Rod",
"hound_cin_tlk":"Hound",
"ironhide_cin_rotf":"Ironhide (ROTF)",
"ironhide_gs_kabam":"Ironhide",
"jazz_gs_twm05":"Jazz",
"jetfire_gs_leader2014":"Jetfire",
"kickback_gs_kabam":"Kickback",
"megatronus_gs_kabam":"Megatronus",
"megatron_cin_rotf":"Megatron (ROTF)",
"megatron_gs_leader2015":"Megatron",
"mirage_gs_deluxe2016":"Mirage",
"mixmaster_cin_rotf":"Mixmaster",
"motormaster_gs_voyager2015":"Motormaster",
"necrotronus_gs_kabam":"Necrotronus",
"nemesisprime_gs_voyager2015":"Nemesis Prime",
"optimusprimal_bw_mp32":"Optimus Primal",
"optimusprime_cin_tf":"Optimus Prime (MV1)",
"prowl_gs_deluxe2016":"Prowl",
"ramjet_gs_deluxe2008":"Ramjet",
"ratchet_gs_kabam":"Ratchet",
"rhinox_gs_voyager2014":"Rhinox",
"rodimusprime_gs_mp09":"Rodimus Prime",
"scorponok_bw_kabam":"Scorponok",
"sharkticon_gs_brawler":"Sharkticon",
"sharkticon_gs_demolition":"Sharkticon",
"sharkticon_gs_kabam":"Sharkticon",
"sharkticon_gs_scout":"Sharkticon",
"sharkticon_gs_tactician":"Sharkticon",
"sharkticon_gs_tech":"Sharkticon",
"sharkticon_gs_warrior":"Sharkticon",
"shockwave_gs":"Shockwave",
"sideswipe_gs":"Sideswipe",
"skywarp_gs_leader2015":"Skywarp",
"slipstream_gs":"Slipstream",
"soundblaster_gs_mp13b":"Soundblaster",
"soundwave_gs":"Soundwave",
"sunstreaker_gs_deluxe2008":"Sunstreaker",
"tantrum_gs_kabam":"Tantrum",
"thundercracker_gs_leader2015":"Thundercracker",
"ultramagnus_gs_leader":"Ultra Magnus",
"waspinator_gs_deluxe":"Waspinator",
"wheeljack_gs_mp20":"Wheeljack",
"windblade_gs":"Windblade",
}
rows = []
for cid in client:
    page = alias.get(cid)
    exists = page in all_titles if page else False
    conf = "high (manual variant/base)" if exists else "none"
    rows.append({"client_id": cid, "wiki_page": page, "wiki_page_exists": exists,
                 "confidence": conf, "in_bots_stats": bool(page in bots) if page else False})
matched = [r for r in rows if r["wiki_page_exists"]]
unmatched_client = [r for r in rows if not r["wiki_page_exists"]]
wiki_without_client = sorted(set(bots) - {r["wiki_page"] for r in rows if r["wiki_page"] in bots})
out = {
    "source": "client package directories under work/unpacked/assets (59 bot packs) vs wiki pages",
    "client_pack_count": len(client),
    "sharkticon_pack_count": sum(1 for x in client if x.startswith("sharkticon_")),
    "non_sharkticon_client_count": sum(1 for x in client if not x.startswith("sharkticon_")),
    "wiki_bot_stat_pages": len(bots),
    "matched": matched,
    "matched_count": len(matched),
    "unmatched_client": unmatched_client,
    "unmatched_client_count": len(unmatched_client),
    "wiki_without_client": wiki_without_client,
    "note": "Mapping is by canonical pack prefix + manual variants; confidence is not a pack-by-pack asset proof.",
}
json.dump(out, open(os.path.join(W, "id_map.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ["client_pack_count","sharkticon_pack_count","non_sharkticon_client_count","wiki_bot_stat_pages","matched_count","unmatched_client_count"]}, ensure_ascii=False, indent=1))
print("unmatched", [r["client_id"] for r in unmatched_client])
print("wiki without client", wiki_without_client)
