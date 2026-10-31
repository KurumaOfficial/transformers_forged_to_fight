import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r".\work\all_game_classes.json", "r", encoding="utf-8") as f:
    classes = json.load(f)

with open(r".\work\string_literals.txt", "r", encoding="utf-8") as f:
    literals = f.readlines()

print(f"Loaded {len(classes)} classes, {len(literals)} literals")

# 1. Network & RPC Framework
print("=== 1. NETWORK & RPC FRAMEWORK ===")
net_classes = [c for c in classes if any(k in c["full_name"].lower() for k in ["network", "rpc", "transport", "protocol", "connection", "client", "request", "response", "dispatcher", "gateway"])]
print(f"Network related classes: {len(net_classes)}")

# Look specifically for Kabam / game network architecture
kabam_net = [c for c in net_classes if any(k in c["full_name"].lower() for k in ["kabam", "ebg", "gameplay", "command", "service", "net"])]
for c in kabam_net[:25]:
    print(f"  Class: {c['full_name']}")
    methods = [m for m in c['methods'] if not m.startswith("get_") and not m.startswith("set_")][:5]
    fields = c['fields'][:5]
    print(f"    Methods: {methods}")
    print(f"    Fields: {fields}")

# 2. Check for Protobuf / JSON / MsgPack
print("\n=== 2. SERIALIZATION FORMAT ===")
ser_classes = [c for c in classes if any(k in c["full_name"].lower() for k in ["protobuf", "proto", "json", "msgpack", "flatbuffer", "serializer", "deserializer"])]
print(f"Serialization classes: {len(ser_classes)}")
for c in ser_classes[:15]:
    print(f"  {c['full_name']}")

# Check string literals for RPC commands / API routes
print("\n=== 3. RPC COMMANDS & API ENDPOINTS IN STRING LITERALS ===")
rpc_patterns = re.compile(r'(/api/|/rpc/|/game/|/service/|/v\d+/|\.php|\.json|\.action|[A-Z][a-zA-Z0-9]+Request|[A-Z][a-zA-Z0-9]+Response|cmd_|rpc_)')
matching_lits = set()
for l in literals:
    # remove index [123]
    val = l.split("]", 1)[-1].strip()
    if rpc_patterns.search(val) and len(val) < 120 and " " not in val:
        matching_lits.add(val)

print(f"Found {len(matching_lits)} potential RPC / Endpoint strings:")
for s in sorted(list(matching_lits))[:40]:
    print(f"  {s}")

# 4. Certificate Pinning & Security
print("\n=== 4. CERTIFICATE PINNING & SECURITY ===")
sec_classes = [c for c in classes if any(k in c["full_name"].lower() for k in ["cert", "pinning", "ssl", "security", "tamper", "anticheat", "integrity", "verify", "validator"])]
for c in sec_classes[:20]:
    print(f"  Class: {c['full_name']} (methods: {c['methods'][:3]})")

# Check string literals for cert/security
sec_lits = [l.strip() for l in literals if any(k in l.lower() for k in ["pinning", "certificate", "publickey", "sha256/", "fingerprint", "root_detected", "jailbreak", "emulator", "tamper"])]
print(f"Security literals count: {len(sec_lits)}")
for sl in sec_lits[:15]:
    print(f"  {sl}")
