import json
import os
import re

loc = json.load(open("work/localization_all.json", encoding="utf-8"))

MAP = {
    "arcee_gs_deluxe2014": "ARCEE_GS",
    "barricade_cin_dotm": "BARRI_C",
    "blaster_gs_leader2016": "BLASTR_GS",
    "bludgeon_gs_rd20": "BLUDGE_GS",
    "bonecrusher_cin_rotf": "BONEC_C",
    "bumblebee_cin_dotm": "BUMBL_C",
    "bumblebee_gs_kabam": "BUMBL_GS",
    "cheetor_bw_transmetal": "CHEETOR_BW",
    "cliffjumper_gs_kabam": "CLIFFJUMP_GS",
    "cyclonus_gs_uw06": "CYCLON_GS",
    "dinobot_bw_kabam": "DINOB_BW",
    "dirge_gs_deluxe2008": "DIRGE_GS",
    "drift_cin_aoe": "DRIFT_C",
    "galvatron_gs_voyager2016": "GALVATRON_GS",
    "grimlock_gs_mp08": "GRIML_GS",
    "grindor_cin_rotf": "GRIND_C_ROTF",
    "hotrod_cin_tlk": "HOTRO_C",
    "hound_cin_tlk": "HOUND_C",
    "ironhide_cin_rotf": "IRONH_C_ROTF",
    "ironhide_gs_kabam": "IRONH_GS",
    "jazz_gs_twm05": "JAZZ_GS",
    "jetfire_gs_leader2014": "JETFIRE_GS",
    "kickback_gs_kabam": "KICKB_GS",
    "megatron_cin_rotf": "MEGAT_C",
    "megatron_gs_leader2015": "MEGAT_GS",
    "megatronus_gs_kabam": "MEGATRO_GS",
    "mirage_gs_deluxe2016": "MIRAG_GS",
    "mixmaster_cin_rotf": "MIXMA_C_ROTF",
    "motormaster_gs_voyager2015": "MOTORM_GS",
    "necrotronus_gs_kabam": "NECROTRO_GS",
    "nemesisprime_gs_voyager2015": "NEMESIS_GS",
    "optimusprimal_bw_mp32": "OPRIMAL_BW",
    "optimusprime_cin_tf": "OPTIMUS_C_TF",
    "optimusprime_gs_v": "OPTIMUS_GS",
    "prowl_gs_deluxe2016": "PROWL_GS",
    "ramjet_gs_deluxe2008": "RAMJET_GS",
    "ratchet_gs_kabam": "RATCH_GS",
    "rhinox_gs_voyager2014": "RHINO_BW",
    "rodimusprime_gs_mp09": "RODIMUS_GS",
    "scorponok_bw_kabam": "SCORPO_BW",
    "sharkticon_gs_brawler": "SHARK_BRAW",
    "sharkticon_gs_demolition": "SHARK_DEMO",
    "sharkticon_gs_kabam": "SHARK_GOLD",
    "sharkticon_gs_scout": "SHARK_SCOU",
    "sharkticon_gs_tactician": "SHARK_TACT",
    "sharkticon_gs_tech": "SHARK_TECH",
    "sharkticon_gs_warrior": "SHARK_WARR",
    "shockwave_gs": "SHOCK_C",
    "sideswipe_gs": "SIDES_GS",
    "skywarp_gs_leader2015": "SKYWARP_GS",
    "slipstream_gs": "SLIPSTREAM_GS",
    "soundblaster_gs_mp13b": "SOUNDBLAST_GS",
    "soundwave_gs": "SOUND_GS",
    "starscream_gs": "STARS_GS",
    "sunstreaker_gs_deluxe2008": "SUNSTREAK_GS",
    "tantrum_gs_kabam": "TANTRUM_GS",
    "thundercracker_gs_leader2015": "THUNDER_GS",
    "ultramagnus_gs_leader": "ULTRAM_GS",
    "waspinator_gs_deluxe": "WASP_BW",
    "wheeljack_gs_mp20": "WHEELJ_GS",
    "windblade_gs": "WINDB_GS",
}

ports = set()
for dp, dn, fn in os.walk("work/unpacked/assets"):
    for f in fn:
        m = re.match(r"portrait_(.+)_(large\.png|small\.jpg)$", f)
        if m:
            ports.add(m.group(1))

bios = {k[len("ID_CHARACTER_BIOS_"):] for k in loc if k.startswith("ID_CHARACTER_BIOS_")}
spec = set()
for k in loc:
    m = re.match(r"ID_SPECIAL_ATTACK_(?:DESCRIPTION_)?([A-Z0-9_]+)_(\d+)$", k)
    if m:
        spec.add(m.group(1))

print("id | token | bio | spec | portrait")
for cid in sorted(MAP):
    t = MAP[cid]
    print("%s | %s | %s | %s | %s" % (
        cid, t, t in bios, t in spec, t.lower() in ports))
print()
print("unknown bios tokens", sorted(bios - set(MAP.values())))
print("unknown spec tokens", sorted(spec - set(MAP.values())))
