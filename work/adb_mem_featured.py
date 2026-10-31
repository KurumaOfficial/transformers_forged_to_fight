import subprocess, struct, sys, os

ADB = r".\work\platform-tools\adb.exe"
PID = sys.argv[1] if len(sys.argv) > 1 else "5186"
BASE = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x7a41136c0000

def mem(addr, size):
    p = subprocess.run([ADB, "shell", f"su 0 dd if=/proc/{PID}/mem bs=1 count={size} skip={addr} 2>/dev/null | xxd -p"], capture_output=True, text=True)
    h = "".join(p.stdout.split())
    if not h:
        return b""
    return bytes.fromhex(h)

def u64(addr):
    b = mem(addr, 8)
    return struct.unpack("<Q", b)[0] if len(b) == 8 else None

def u32(addr):
    b = mem(addr, 4)
    return struct.unpack("<I", b)[0] if len(b) == 4 else None

def il2cpp_str(addr, maxlen=200):
    if not addr:
        return None
    n = u32(addr + 0x10)
    if n is None or n > maxlen:
        return None
    b = mem(addr + 0x14, n * 2)
    return b.decode("utf-16le", errors="replace")

def dump_chain():
    slot = BASE + 0x2c0fb50
    print(f"slot {slot:#x}")
    cls = u64(slot)
    print(f"  class = {cls:#x}" if cls else "  class = None")
    if not cls:
        return
    statics = u64(cls + 0xB8)
    print(f"  static_fields = {statics:#x}" if statics else "  static_fields = None")
    if not statics:
        return
    inst = u64(statics)
    print(f"  Instance = {inst:#x}" if inst else "  Instance = None")
    if not inst:
        return
    for off, name in [(0x18, "OrderType"), (0x20, "Heroes"), (0x28, "?")]:
        v = u64(inst + off)
        print(f"  inst+{off:#x} {name} = {v:#x}" if v else f"  inst+{off:#x} {name} = 0")
    heroes = u64(inst + 0x20)
    if heroes:
        cnt = u32(heroes + 0x18)
        print(f"  Heroes.Count = {cnt}")
        arr = u64(heroes + 0x10)
        print(f"  Heroes.array = {arr:#x}")
        if arr and cnt and cnt < 50:
            for i in range(cnt):
                item = u64(arr + 0x20 + i * 8)
                if not item:
                    print(f"    [{i}] null")
                    continue
                bp = u64(item + 0x10)
                print(f"    [{i}] obj={item:#x} Blueprint={il2cpp_str(bp)!r}")

if __name__ == "__main__":
    dump_chain()
