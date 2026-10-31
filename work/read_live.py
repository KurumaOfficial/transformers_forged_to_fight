import subprocess
import struct

def run_adb(cmd):
    p = subprocess.run(f'work\\android-sdk\\platform-tools\\adb.exe shell "{cmd}"', shell=True, capture_output=True, text=True)
    return p.stdout.strip()

base = 0x7d2386550000
addr = base + 0x2c14120
print('Reading from addr:', hex(addr))
out = run_adb(f'dd if=/proc/6372/mem bs=1 count=16 skip={addr} 2>/dev/null | xxd -p')
b = bytes.fromhex(''.join(out.split()))
if len(b) >= 8:
    ptr = struct.unpack('<Q', b[:8])[0]
    print(f'Pointer at 0x2c14120: 0x{ptr:X}')
    if ptr:
        klass_hex = run_adb(f'dd if=/proc/6372/mem bs=1 count=16 skip={ptr} 2>/dev/null | xxd -p')
        b2 = bytes.fromhex(''.join(klass_hex.split()))
        if len(b2) >= 8:
            klass = struct.unpack('<Q', b2[:8])[0]
            print(f'klass: 0x{klass:X}')
            
            # klass + 0xB8 is static_fields
            static_fields_hex = run_adb(f'dd if=/proc/6372/mem bs=1 count=8 skip={klass + 0xB8} 2>/dev/null | xxd -p')
            static_fields = struct.unpack('<Q', bytes.fromhex(''.join(static_fields_hex.split())))[0]
            print(f'static_fields: 0x{static_fields:X}')
            
            # GameboardManager.<Instance>k__BackingField is at static_fields + 0x0
            inst_hex = run_adb(f'dd if=/proc/6372/mem bs=1 count=8 skip={static_fields} 2>/dev/null | xxd -p')
            instance = struct.unpack('<Q', bytes.fromhex(''.join(inst_hex.split())))[0]
            print(f'GameboardManager.Instance: 0x{instance:X}')
            
            if instance:
                fields_hex = run_adb(f'dd if=/proc/6372/mem bs=1 count=128 skip={instance} 2>/dev/null | xxd -p')
                fields = bytes.fromhex(''.join(fields_hex.split()))
                
                # _gameboards: 0x20
                # _activeGameboard: 0x28
                # _baseBoard: 0x30
                # _category: 0x38
                # _questNodeTuning: 0x50
                # _baseNodeTuning: 0x58
                # _questNodeTuningReady: 0x60
                # _baseNodeTuningReady: 0x61
                # _raidTutorialCompleteOnBaseLoad: 0x62
                baseboard = struct.unpack('<Q', fields[0x30:0x38])[0]
                quest_tuning = struct.unpack('<Q', fields[0x50:0x58])[0]
                base_tuning = struct.unpack('<Q', fields[0x58:0x60])[0]
                quest_ready = fields[0x60]
                base_ready = fields[0x61]
                raid_ready = fields[0x62]
                print(f'  _baseBoard: 0x{baseboard:X}')
                print(f'  _questNodeTuning: 0x{quest_tuning:X}')
                print(f'  _baseNodeTuning: 0x{base_tuning:X}')
                print(f'  _questNodeTuningReady: {quest_ready}')
                print(f'  _baseNodeTuningReady: {base_ready}')
                print(f'  _raidTutorialCompleteOnBaseLoad: {raid_ready}')


