import subprocess
import struct

def run_adb(cmd):
    p = subprocess.run(["work\\platform-tools\\adb.exe", "shell", f"su 0 sh -c '{cmd}'"], capture_output=True, text=True)
    return p.stdout.strip()

def read_mem(pid, addr, size):
    cmd = f"dd if=/proc/{pid}/mem bs=1 count={size} skip={addr} 2>/dev/null | xxd -p"
    out = run_adb(cmd)
    clean = "".join(out.split())
    if not clean: return b""
    try: return bytes.fromhex(clean)
    except: return b""

def read_u64(pid, addr):
    d = read_mem(pid, addr, 8)
    return struct.unpack('<Q', d)[0] if len(d) == 8 else 0

def read_u32(pid, addr):
    d = read_mem(pid, addr, 4)
    return struct.unpack('<I', d)[0] if len(d) == 4 else 0

def read_u8(pid, addr):
    d = read_mem(pid, addr, 1)
    return d[0] if len(d) == 1 else 0

def read_cs_str(pid, addr):
    if not addr: return ""
    slen = read_u32(pid, addr + 0x10)
    if not slen or slen > 128: return ""
    raw = read_mem(pid, addr + 0x14, slen * 2)
    return raw.decode('utf-16le', errors='replace')

pid = 12670
base = 0x75b9cad5e000

# QuestsManager slot at base + 0x2C08D68
slot_ptr = read_u64(pid, base + 0x2C08D68)
if slot_ptr < base:
    slot_ptr += base
print(f"slot_ptr: 0x{slot_ptr:X}")
if slot_ptr:
    klass = read_u64(pid, slot_ptr)
    print(f"klass: 0x{klass:X}")
    static_fields = read_u64(pid, klass + 0xB8)
    print(f"static_fields: 0x{static_fields:X}")
    qm_inst = read_u64(pid, static_fields + 8)
    print(f"QuestsManager.Instance: 0x{qm_inst:X}")
    if qm_inst:
        quest_db = read_u64(pid, qm_inst + 0x70)
        print(f"QuestDB: 0x{quest_db:X}")
        if quest_db:
            avail_sets = read_u64(pid, quest_db + 0x10)
            print(f"AvailableSets: 0x{avail_sets:X}")
            if avail_sets:
                items = read_u64(pid, avail_sets + 0x10)
                count = read_u32(pid, avail_sets + 0x18)
                print(f"Sets count: {count}")
                for s_i in range(count):
                    s_ptr = read_u64(pid, items + 0x20 + s_i * 8)
                    cat = read_cs_str(pid, read_u64(pid, s_ptr + 0x28))
                    set_id = read_cs_str(pid, read_u64(pid, s_ptr + 0x40))
                    print(f"  Set [{s_i}]: category='{cat}' id='{set_id}' ptr=0x{s_ptr:X}")
                    acts_arr = read_u64(pid, s_ptr + 0x10)
                    if acts_arr:
                        act_len = read_u32(pid, acts_arr + 0x18)
                        print(f"    Acts array len: {act_len}")
                        for a_i in range(act_len):
                            act_ptr = read_u64(pid, acts_arr + 0x20 + a_i * 8)
                            if act_ptr:
                                fname = read_cs_str(pid, read_u64(pid, act_ptr + 0x10))
                                unlk = read_u8(pid, act_ptr + 0x30)
                                print(f"      Act [{a_i}]: '{fname}', unlocked={unlk}, ptr=0x{act_ptr:X}")
                                ch_arr = read_u64(pid, act_ptr + 0x28)
                                if ch_arr:
                                    ch_len = read_u32(pid, ch_arr + 0x18)
                                    print(f"        Chapters array len: {ch_len}")
                                    for c_i in range(ch_len):
                                        ch_ptr = read_u64(pid, ch_arr + 0x20 + c_i * 8)
                                        if ch_ptr:
                                            ch_fname = read_cs_str(pid, read_u64(pid, ch_ptr + 0x10))
                                            ch_unlk = read_u8(pid, ch_ptr + 0x30)
                                            print(f"          Chapter [{c_i}]: '{ch_fname}', unlocked={ch_unlk}, ptr=0x{ch_ptr:X}")
                                            q_arr = read_u64(pid, ch_ptr + 0x28)
                                            if q_arr:
                                                q_len = read_u32(pid, q_arr + 0x18)
                                                print(f"            Quests array len: {q_len}")
                                                for q_i in range(q_len):
                                                    q_ptr = read_u64(pid, q_arr + 0x20 + q_i * 8)
                                                    if q_ptr:
                                                        qid = read_cs_str(pid, read_u64(pid, q_ptr + 0x20))
                                                        qunlk = read_u8(pid, q_ptr + 0xC0)
                                                        print(f"              Quest [{q_i}]: id='{qid}', unlocked={qunlk}")
