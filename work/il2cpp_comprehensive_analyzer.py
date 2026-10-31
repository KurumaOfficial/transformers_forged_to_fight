import struct
import sys
import os
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

meta_path = r".\work\unpacked\assets\bin\Data\Managed\Metadata\global-metadata.dat"

with open(meta_path, "rb") as f:
    data = f.read()

# Layout of metadata v27
string_offset = 738752
string_size = 1547968

def get_string(idx):
    if idx < 0 or idx >= string_size:
        return ""
    pos = string_offset + idx
    end = data.find(b"\x00", pos)
    if end == -1:
        return ""
    return data[pos:end].decode("utf-8", errors="ignore")

# String literals
lit_offset = 256
lit_size = 194968
data_offset = 195224
data_size = 543528
lit_count = lit_size // 8

string_literals = []
for i in range(lit_count):
    length, off = struct.unpack("<2i", data[lit_offset + i*8 : lit_offset + (i+1)*8])
    if 0 <= off < data_size:
        s = data[data_offset + off : data_offset + off + length].decode("utf-8", errors="ignore")
        string_literals.append(s)
    else:
        string_literals.append("")

# Images
images_offset = 9454432
images_size = 1960
image_count = images_size // 40
images = []
for i in range(image_count):
    entry = struct.unpack("<10i", data[images_offset + i*40 : images_offset + (i+1)*40])
    name = get_string(entry[0])
    type_start = entry[2]
    type_count = entry[3]
    images.append({
        "index": i,
        "name": name,
        "type_start": type_start,
        "type_count": type_count
    })

# Type definitions
typedef_offset = 8267048
typedef_size = 1187384
total_types = typedef_size // 88

# Methods
method_offset = 2571416
method_size = 2856896
# Fields
field_offset = 6867340
field_size = 704676

types = []
for i in range(total_types):
    pos = typedef_offset + i * 88
    vals = struct.unpack("<22I", data[pos:pos+88])
    name = get_string(vals[0])
    ns = get_string(vals[1])
    field_start = vals[11]
    method_start = vals[12]
    # counts
    m_count = vals[19] & 0xFFFF
    p_count = (vals[19] >> 16) & 0xFFFF
    f_count = vals[20] & 0xFFFF
    e_count = (vals[20] >> 16) & 0xFFFF
    
    # find image
    img_name = ""
    for img in images:
        if img["type_start"] <= i < img["type_start"] + img["type_count"]:
            img_name = img["name"]
            break
            
    # Read methods
    methods = []
    if method_start != 0xFFFFFFFF and m_count < 10000:
        for mi in range(m_count):
            mpos = method_offset + (method_start + mi) * 32
            if mpos + 32 <= method_offset + method_size:
                mvals = struct.unpack("<6I2H2H", data[mpos:mpos+32])
                mname = get_string(mvals[0])
                pcount = mvals[7]
                methods.append({"name": mname, "params": pcount})
        
    # Read fields
    fields = []
    if field_start != 0xFFFFFFFF and f_count < 10000:
        for fi in range(f_count):
            fpos = field_offset + (field_start + fi) * 12
            if fpos + 12 <= field_offset + field_size:
                fvals = struct.unpack("<3I", data[fpos:fpos+12])
                fname = get_string(fvals[0])
                fields.append({"name": fname})
        
    types.append({
        "index": i,
        "image": img_name,
        "namespace": ns,
        "name": name,
        "full_name": f"{ns}.{name}" if ns else name,
        "methods": methods,
        "fields": fields
    })

print(f"Parsed {len(types)} types successfully!")

# Let's save a summary of Assembly-CSharp types
game_types = [t for t in types if t["image"] in ["Assembly-CSharp.dll", "Assembly-CSharp-firstpass.dll"]]
print(f"Total Game Types (Assembly-CSharp*): {len(game_types)}")

# Analyze by subsystems
subsystems = {
    "Network & RPC": [],
    "Auth & Login": [],
    "Combat & Battle": [],
    "AI & Behavior": [],
    "Bot & Roster": [],
    "Quests & Missions": [],
    "Economy & Store": [],
    "PvP & Alliance": [],
    "Base & Raids": [],
    "Data & Config Models": [],
    "Security & AntiCheat": []
}

for t in game_types:
    fn = t["full_name"].lower()
    m_names = " ".join(m["name"].lower() for m in t["methods"])
    f_names = " ".join(f["name"].lower() for f in t["fields"])
    all_text = f"{fn} {m_names} {f_names}"
    
    if any(k in fn for k in ["network", "rpc", "http", "socket", "packet", "webrequest", "restclient", "endpoint", "server", "message"]):
        subsystems["Network & RPC"].append(t)
    if any(k in fn for k in ["login", "auth", "session", "account", "kabam", "user", "credential"]):
        subsystems["Auth & Login"].append(t)
    if any(k in fn for k in ["combat", "battle", "fight", "damage", "attack", "hit", "combo", "special", "buff"]):
        subsystems["Combat & Battle"].append(t)
    if any(k in fn for k in ["behavior", "actionnode", "compositenode", "ai", "decision", "fsm", "state"]):
        subsystems["AI & Behavior"].append(t)
    if any(k in fn for k in ["character", "bot", "roster", "hero", "champion", "synergy", "signature"]):
        subsystems["Bot & Roster"].append(t)
    if any(k in fn for k in ["quest", "mission", "campaign", "story", "map", "act", "chapter", "node"]):
        subsystems["Quests & Missions"].append(t)
    if any(k in fn for k in ["economy", "store", "shop", "currency", "gold", "energon", "ore", "crystal", "inventory", "reward"]):
        subsystems["Economy & Store"].append(t)
    if any(k in fn for k in ["pvp", "alliance", "war", "guild", "clan", "leaderboard", "arena"]):
        subsystems["PvP & Alliance"].append(t)
    if any(k in fn for k in ["base", "raid", "defense", "shield", "mod", "extractor"]):
        subsystems["Base & Raids"].append(t)
    if any(k in fn for k in ["data", "model", "config", "table", "def", "vo", "dto"]):
        subsystems["Data & Config Models"].append(t)
    if any(k in fn for k in ["protect", "cheat", "security", "jailbreak", "root", "integrity", "hash", "tamper", "license"]):
        subsystems["Security & AntiCheat"].append(t)

print("\nSubsystem classification:")
for k, v in subsystems.items():
    print(f"  {k:25s}: {len(v)} classes")

# Dump all types and string literals to files for in-depth analysis
with open(r".\work\all_game_classes.json", "w", encoding="utf-8") as f:
    json.dump([{
        "full_name": t["full_name"],
        "image": t["image"],
        "methods": [m["name"] for m in t["methods"]],
        "fields": [f["name"] for f in t["fields"]]
    } for t in game_types], f, indent=2)

with open(r".\work\string_literals.txt", "w", encoding="utf-8") as f:
    for idx, s in enumerate(string_literals):
        if len(s.strip()) > 0:
            f.write(f"[{idx}] {s}\n")

print("\nSaved all_game_classes.json and string_literals.txt successfully!")
