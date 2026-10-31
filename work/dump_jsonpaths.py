import struct, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[0]
ADB=str(ROOT/"platform-tools"/"adb.exe")
ELF=str(ROOT/"unpacked"/"lib"/"arm64-v8a"/"libil2cpp.so")
sys.stdout.reconfigure(encoding="utf-8",errors="replace")
def adb(a,t=120): return subprocess.run([ADB]+a,capture_output=True,timeout=t)
pid=adb(["shell","pidof com.kabam.bigrobot"]).stdout.decode().strip()
elf=open(ELF,"rb").read(); e_phoff=struct.unpack_from("<Q",elf,32)[0]; e_phnum=struct.unpack_from("<H",elf,56)[0]; e_phentsize=struct.unpack_from("<H",elf,54)[0]
wv=None
for i in range(e_phnum):
 o=e_phoff+i*e_phentsize; t,fl,fo,va,pa,fs,ms,al=struct.unpack_from("<IIQQQQQQ",elf,o)
 if t==1 and (fl&2): wv=va
maps=adb(["shell",f"su 0 cat /proc/{pid}/maps"]).stdout.decode("latin1","replace"); base=None
for line in maps.splitlines():
 if "libil2cpp.so" in line and "rw-p" in line and "02a97000" in line: base=int(line.split("-")[0],16)-wv; break
def mem(a,n):
 return adb(["exec-out","su","0","dd",f"if=/proc/{pid}/mem","bs=1",f"count={n}",f"skip={a}","status=none"]).stdout
def u64(a):
 b=mem(a,8); return struct.unpack("<Q",b)[0] if len(b)==8 else None
def u32(a):
 b=mem(a,4); return struct.unpack("<I",b)[0] if len(b)==4 else None
def ilstr(a):
 if not a: return None
 n=u32(a+0x10)
 if n is None or n>200: return None
 b=mem(a+0x14,n*2)
 try: return b.decode("utf-16le")
 except: return repr(b)
klass=u64(base+0x2d0c658); print("klass",hex(klass) if klass else None)
sf=u64(klass+0xb8); print("static",hex(sf) if sf else None)
for off,name in [(0xa98,"max_hp"),(0xab0,"mhp"),(0xac8,"mhpb"),(0xae0,"hp"),(0xaf8,"attack"),(0xb10,"att"),(0xb28,"attb"),(0xb40,"armor"),(0xb58,"arm"),(0xb70,"crit_chance"),(0xb88,"cc"),(0xba0,"crit_damage"),(0xbb8,"cd"),(0xbd0,"pbc"),(0xbe8,"pbc2"),(0xc00,"bp"),(0xc18,"bp2"),(0xc30,"mg"),(0xc48,"mg2"),(0xc60,"ms"),(0xc78,"ms2")]:
 p=sf+off; data=mem(p,0x18)
 if len(data)<0x18: print(name,"short",len(data)); continue
 a,b,c=struct.unpack("<QQQ",data)
 print(name,hex(p),hex(a),ilstr(a),hex(b),ilstr(b),hex(c),ilstr(c))
