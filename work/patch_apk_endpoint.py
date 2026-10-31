import os
import shutil
import struct
import subprocess
import sys

# Production patcher for Transformers: Forged to Fight v9.2.0
# NEVER modifies the original APK. All artifacts go into work/patched_build/

ORIGINAL_APK = r".\com.kabam.bigrobot_9.2.0-123129100_minAPI23(arm64-v8a,armeabi-v7a)(nodpi)_apkmirror.com.apk"
BUILD_DIR = r".\work\patched_build"
SEVEN_ZIP = r"C:\Program Files\7-Zip\7z.exe"
UBER_SIGNER = r".\work\uber-apk-signer.jar"

def patch_serialized_endpoint(data: bytes, target_url: str) -> bytes:
    """
    Rewrites Unity SerializedFile format 22 (Unity 2020.3) containing TextAsset 'endpointconfig'.
    Updates 64-bit header fileSize, Object Table byte_size, and TextAsset payload.
    """
    new_json = f'{{"Default":{{"Prod":"{target_url}"}}}}'.encode("utf-8")
    new_script_len = len(new_json)
    
    pad_len = (4 - (new_script_len % 4)) % 4
    new_payload = new_json + (b"\x00" * pad_len)
    
    # 4 (name_len) + 16 (name 'endpointconfig' + 2 pad) + 4 (script_len) + len(new_payload)
    new_obj_size = 4 + 16 + 4 + len(new_payload)
    new_file_size = 4096 + new_obj_size
    
    patched = bytearray(data[:4096])
    
    # Header fileSize at 0x1C (big-endian uint32 in Unity format 22 header)
    struct.pack_into(">I", patched, 0x1C, new_file_size)
    
    # Object Table byte_size at 0x70 (little-endian uint32)
    struct.pack_into("<I", patched, 0x70, new_obj_size)
    
    # Object payload at 0x1000 (4096)
    name_bytes = b"endpointconfig"
    patched += struct.pack("<I", len(name_bytes))
    patched += name_bytes + b"\x00\x00"
    patched += struct.pack("<I", new_script_len)
    patched += new_payload
    
    # Verify integrity
    header_fsize = struct.unpack(">I", patched[0x1C:0x20])[0]
    assert header_fsize == len(patched), f"Header fileSize mismatch: {header_fsize} != {len(patched)}"
    obj_size = struct.unpack("<I", patched[0x70:0x74])[0]
    assert obj_size == new_obj_size, f"Object Table byte_size mismatch: {obj_size} != {new_obj_size}"
    
    return bytes(patched)

def build_patched_apk(target_url="http://127.0.0.1:8080"):
    os.makedirs(BUILD_DIR, exist_ok=True)
    temp_dir = os.path.join(BUILD_DIR, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    cfg_name = "e1917cd7a6bdb4492a247b8f758df2ae"
    cfg_apk_rel = f"assets/bin/Data/{cfg_name}"
    
    print(f"[*] Extracting {cfg_apk_rel} from original APK...")
    cmd_extract = [SEVEN_ZIP, "e", ORIGINAL_APK, f"-o{temp_dir}", cfg_apk_rel, "-y"]
    subprocess.check_call(cmd_extract, stdout=subprocess.DEVNULL)
    
    extracted_cfg = os.path.join(temp_dir, cfg_name)
    with open(extracted_cfg, "rb") as f:
        orig_cfg_data = f.read()
        
    print(f"[*] Patching endpoint URL to '{target_url}'...")
    patched_cfg_data = patch_serialized_endpoint(orig_cfg_data, target_url)
    
    # Verify deserialization
    pos = 4096
    nlen = struct.unpack("<I", patched_cfg_data[pos:pos+4])[0]
    pos += 4
    name = patched_cfg_data[pos:pos+nlen].decode("utf-8")
    pos += nlen + ((4 - (nlen % 4)) % 4)
    slen = struct.unpack("<I", patched_cfg_data[pos:pos+4])[0]
    pos += 4
    script = patched_cfg_data[pos:pos+slen].decode("utf-8")
    print(f"[+] Verified re-read: Asset '{name}', length={slen}, JSON={script}")
    
    # Prepare folder structure for 7z update
    assets_bin_data = os.path.join(temp_dir, "assets", "bin", "Data")
    os.makedirs(assets_bin_data, exist_ok=True)
    patched_cfg_path = os.path.join(assets_bin_data, cfg_name)
    with open(patched_cfg_path, "wb") as f:
        f.write(patched_cfg_data)
        
    intermediate_apk = os.path.join(BUILD_DIR, "tftf_unsigned.apk")
    print(f"[*] Copying original APK to working copy: {intermediate_apk}...")
    shutil.copy2(ORIGINAL_APK, intermediate_apk)
    
    print("[*] Replacing endpointconfig in APK copy via 7-Zip...")
    cmd_update = [SEVEN_ZIP, "a", "-tzip", intermediate_apk, "assets"]
    subprocess.check_call(cmd_update, cwd=temp_dir, stdout=subprocess.DEVNULL)
    
    print("[*] Running zipalign + apksigner (v1, v2, v3) via uber-apk-signer...")
    cmd_sign = [
        "java", "-jar", UBER_SIGNER,
        "--allowResign",
        "-a", intermediate_apk,
        "-o", BUILD_DIR
    ]
    subprocess.check_call(cmd_sign)
    
    final_signed_name = os.path.join(BUILD_DIR, "tftf_unsigned-aligned-debugSigned.apk")
    target_apk = os.path.join(BUILD_DIR, "tftf_patched_v9.2.0.apk")
    if os.path.exists(final_signed_name):
        if os.path.exists(target_apk):
            os.remove(target_apk)
        os.rename(final_signed_name, target_apk)
        
    print(f"\n[*] Verifying signatures of {target_apk}...")
    cmd_verify = [
        "java", "-jar", UBER_SIGNER,
        "-y",
        "-a", target_apk
    ]
    subprocess.check_call(cmd_verify)
    
    # Cleanup intermediate files
    shutil.rmtree(temp_dir, ignore_errors=True)
    if os.path.exists(intermediate_apk):
        try:
            os.remove(intermediate_apk)
        except Exception:
            pass
            
    print(f"\n=======================================================")
    print(f"[SUCCESS] Patched APK ready: {target_apk}")
    print(f"Target endpoint: {target_url}")
    print(f"Signatures: v1, v2, v3 [VERIFIED]")
    print(f"=======================================================")
    return target_apk

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080"
    build_patched_apk(url)
