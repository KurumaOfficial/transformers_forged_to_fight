import struct, subprocess, sys
from pathlib import Path
ROOT=Path(".").resolve(); ADB=str(ROOT/"work"/"platform-tools"/"adb.exe") if (ROOT/"work"/"platform-tools"/"adb.exe").exists() else str(ROOT/"platform-tools"/"adb.exe")
ELF=str(ROOT/"work"/"unpacked"/"lib"/"arm64-v8a"/"libil2cpp.so")
sys.stdout.reconfigure(encoding="utf-8",errors="replace")
def adb(a,t=120): return subprocess.run([ADB]+a,capture_output=True,timeout=t)
pid=adb(["shell","pidof com.kabam.bigrobot"]).stdout.decode().strip(); print("pid",pid)
elf=open(ELF,"rb").read(); e_phoff=struct.unpack_from("<Q",elf,32)[0]; e_phnum=struct.unpack_from("<H",elf,56)[0]; e_phentsize=struct.unpack_from("<H",elf,54)[0]
wv=None; segs=[]
for i in range(e_phnum):
 o=e_phoff+i*e_phentsize; t,fl,fo,va,pa,fs,ms,al=struct.unpack_from("<IIQQQQQQ",elf,o)
 if t==1 and (fl&2): wv=va
maps=adb(["shell",f"su 0 cat /proc/{pid}/maps"]).stdout.decode("latin1","replace"); base=None
for line in maps.splitlines():
 if "libil2cpp.so" in line and "rw-p" in line and "02a97000" in line: base=int(line.split("-")[0],16)-wv; break
print("base",hex(base))
def mem(a,n): return adb(["exec-out","su","0","dd",f"if=/proc/{pid}/mem","bs=1",f"count={n}",f"skip={a}","status=none"]).stdout
def u64(a):
 b=mem(a,8); return struct.unpack("<Q",b)[0] if len(b)==8 else None
def u32(a):
 b=mem(a,4); return struct.unpack("<I",b)[0] if len(b)==4 else None
def cstr(a,n=80):
 if not a: return None
 b=mem(a,n); return b.split(b"\x00")[0].decode("latin1","replace") if b else None
for slot in [0x2d0c658,0x2d0da20,0x2d09380]:
 c=u64(base+slot); print(hex(slot),'->',hex(c) if c else None,'name',repr(cstr(u64(c+0x10))) if c else None,'sf',hex(u64(c+0xb8) or 0))
