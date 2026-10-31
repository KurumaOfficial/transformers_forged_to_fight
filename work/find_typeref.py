import struct,json,bisect,sys
from capstone import *
BIN=open('work/unpacked/lib/arm64-v8a/libil2cpp.so','rb').read()
e_phoff=struct.unpack_from('<Q',BIN,32)[0]; e_phentsize=struct.unpack_from('<H',BIN,54)[0]; e_phnum=struct.unpack_from('<H',BIN,56)[0]
segs=[]
for i in range(e_phnum):
    o=e_phoff+i*e_phentsize; t,fl,fo,va,pa,fs,ms,al=struct.unpack_from('<IIQQQQQQ',BIN,o)
    if t==1 and (fl&1): segs.append((va,va+fs,fo))
m=json.load(open('work/rva_map.json')); ks=sorted((int(k),v) for k,v in m.items()); a=[k for k,_ in ks]
def containing(addr):
    i=bisect.bisect_right(a,addr)-1
    if i<0: return None
    k,v=ks[i]
    if addr-k>0x20000: return None
    return k,v
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM); md.detail=True
target=0x2be2870
for s,e,o in segs:
    code=BIN[o:o+(e-s)]
    regs={}
    hits=[]
    for ins in md.disasm(code,s):
        if ins.mnemonic=='adrp' and len(ins.operands)>1 and ins.operands[1].type==2:
            regs[ins.reg_name(ins.operands[0].reg)]=ins.operands[1].imm
        elif ins.mnemonic=='ldr' and len(ins.operands)>1 and ins.operands[1].type==3:
            mem=ins.operands[1].mem
            if mem.base:
                base=ins.reg_name(mem.base)
                if base in regs and regs[base]+mem.disp==target:
                    hits.append(ins.address)
    print('seg',hex(s),'hits',len(hits))
    for h in hits:
        c=containing(h)
        print(' ',hex(h),c[1].get('class') if c else '?','|',c[1].get('name') if c else '?')
