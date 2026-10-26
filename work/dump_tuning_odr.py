import struct,subprocess,sys
from pathlib import Path
ROOT=Path(".").resolve(); ADB=str(ROOT/"work"/"platform-tools"/"adb.exe"); ELF=str(ROOT/"work"/"unpacked"/"lib"/"arm64-v8a"/"libil2cpp.so")
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
print("pid",pid,"base",hex(base))
def mem(a,n): return adb(["exec-out","su","0","dd",f"if=/proc/{pid}/mem","bs=1",f"count={n}",f"skip={a}","status=none"]).stdout
def u64(a):
 b=mem(a,8); return struct.unpack("<Q",b)[0] if len(b)==8 else None
def u32(a):
 b=mem(a,4); return struct.unpack("<I",b)[0] if len(b)==4 else None
def cstr(a,n=80):
 b=mem(a,n); return b.split(b"\x00")[0].decode("latin1","replace") if b else None
def cname(o):
 if not o: return None
 c=u64(o); return cstr(u64(c+0x10)) if c else None
def ilstr(a):
 if not a: return None
 n=u32(a+0x10)
 if n is None or n>300: return None
 return mem(a+0x14,n*2).decode("utf-16le","replace")
# Tuning_TypeInfo slot -> pointer -> class -> static fields
p=u64(base+0x2d0f7d0); cls=u64(p) if p else None
print("typeinfo",hex(p) if p else None,"class",hex(cls) if cls else None,cname(cls) if cls else None)
sf=u64(cls+0xb8) if cls else None
print("static",hex(sf) if sf else None)
inst=u64(sf) if sf else None
print("Tuning.Instance",hex(inst) if inst else None,cname(inst) if inst else None)
if inst:
 for off,lab,kind in [(0x360,'ODRForceDownloadAll','b'),(0x361,'ODRForceDownloadAllPreTutorial','b'),(0x362,'ODRShowProgressMB','b'),(0x363,'ODRShowTimeEstimate','b'),(0x364,'ODRForceDownloadAssetListPreTutorial','b'),(0x365,'ODRAllowNative','b')]:
  print(lab,mem(inst+off,1).hex())
 p=u64(inst+0x368); print("ODRAssetListForForcedDownload",hex(p) if p else None,repr(ilstr(p)) if p else None)
