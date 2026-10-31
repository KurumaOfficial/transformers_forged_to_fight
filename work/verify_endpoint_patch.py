import struct

def patch_and_verify(target_url="http://127.0.0.1:8080"):
    orig_path = r"work\unpacked\assets\bin\Data\e1917cd7a6bdb4492a247b8f758df2ae"
    with open(orig_path, "rb") as f:
        orig = f.read()

    new_json = f'{{"Default":{{"Prod":"{target_url}"}}}}'.encode("utf-8")
    new_script_len = len(new_json)
    
    # 4-byte alignment
    pad_len = (4 - (new_script_len % 4)) % 4
    new_payload = new_json + (b"\x00" * pad_len)
    
    # TextAsset structure:
    # m_Name length: 4 bytes (14)
    # m_Name string: 14 bytes + 2 bytes padding = 16 bytes
    # m_Script length: 4 bytes (new_script_len)
    # m_Script bytes: new_script_len + pad_len
    # Total object data size: 4 + 16 + 4 + len(new_payload)
    new_obj_size = 4 + 16 + 4 + len(new_payload)
    
    # Data starts at offset 4096 (0x1000)
    new_file_size = 4096 + new_obj_size
    
    # Build patched binary
    patched = bytearray(orig[:4096])
    
    # Update fileSize in 64-bit Unity SerializedFile header (big-endian uint32 at offset 0x1C)
    struct.pack_into(">I", patched, 0x1C, new_file_size)
    
    # Update byte_size in Object Table (little-endian uint32 at offset 0x70)
    struct.pack_into("<I", patched, 0x70, new_obj_size)
    
    # Write TextAsset object data at offset 4096
    name_bytes = b"endpointconfig"
    patched += struct.pack("<I", len(name_bytes))
    patched += name_bytes + b"\x00\x00"
    patched += struct.pack("<I", new_script_len)
    patched += new_payload
    
    print(f"Original file size: {len(orig)} bytes")
    print(f"Patched file size:  {len(patched)} bytes")
    print(f"Original obj_size:  {struct.unpack('<I', orig[0x70:0x74])[0]} bytes")
    print(f"Patched obj_size:   {new_obj_size} bytes")
    print(f"Script length:      {new_script_len} bytes")
    print(f"JSON content:       {new_json.decode()}")
    
    # Verification by simulated Unity Deserializer
    header_fsize = struct.unpack(">I", patched[0x1C:0x20])[0]
    assert header_fsize == len(patched), f"Header fileSize mismatch: {header_fsize} != {len(patched)}"
    
    obj_size = struct.unpack("<I", patched[0x70:0x74])[0]
    assert obj_size == new_obj_size, f"Object Table byte_size mismatch: {obj_size} != {new_obj_size}"
    
    pos = 4096
    nlen = struct.unpack("<I", patched[pos:pos+4])[0]
    pos += 4
    name = patched[pos:pos+nlen].decode("utf-8")
    pos += nlen + ((4 - (nlen % 4)) % 4)
    
    slen = struct.unpack("<I", patched[pos:pos+4])[0]
    pos += 4
    script = patched[pos:pos+slen].decode("utf-8")
    pos += slen + ((4 - (slen % 4)) % 4)
    
    assert pos == len(patched), f"Deserializer read position {pos} != file length {len(patched)}"
    assert name == "endpointconfig", f"Name mismatch: {name}"
    assert script == new_json.decode(), f"Script mismatch: {script}"
    
    print("\n[SUCCESS] Re-reading verification passed! Unity deserializer will read exact clean JSON.")
    return bytes(patched)

if __name__ == "__main__":
    patch_and_verify()
