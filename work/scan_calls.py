import sys, struct, json
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
SO = r".\work\unpacked\lib\arm64-v8a\libil2cpp.so"
B = open(SO,'rb').read()
phoff=struct.unpack_from('<Q',B,32)[0]; ents=struct.unpack_from('<H',B,54)[0]; n=struct.unpack_from('<H',B,56)[0]
segs=[]
for i in range(n):
    t,fl,fo,va,pa,fs,ms,al=struct.unpack_from('<IIQQQQQQ',B,phoff+i*ents)
    if t==1: segs.append((va,va+fs,fo))
def off(va):
    for s,e,o in segs:
        if s<=va<e: return o+va-s
def code(va,n):
    o=off(va); return B[o:o+n]
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM); md.detail=True
start=int(sys.argv[1],0); length=int(sys.argv[2],0); targets=set(int(x,0) for x in sys.argv[3:])
insns=list(md.disasm(code(start,length),start))
for i,cur in enumerate(insns):
    if cur.mnemonic=='bl' and cur.operands and cur.operands[0].type==2 and cur.operands[0].imm in targets:
        print('--- call',hex(cur.address),'->',hex(cur.operands[0].imm))
        for j in range(max(0,i-14),min(len(insns),i+2)):
            q=insns[j]
            print(f'{q.address:#x}: {q.mnemonic} {q.op_str}')
