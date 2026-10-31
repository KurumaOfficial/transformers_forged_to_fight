import UnityPy
import sys

def verify_apk_endpoint():
    apk_path = r"work\patched_build\tftf_patched_v9.2.0.apk"
    print(f"[*] Loading APK via UnityPy: {apk_path}...")
    
    env = UnityPy.load(apk_path)
    found = False
    
    for obj in env.objects:
        if obj.type.name == "TextAsset":
            data = obj.read()
            if data.m_Name == "endpointconfig":
                found = True
                print(f"[+] FOUND TextAsset via UnityPy:")
                print(f"    Name:   {data.m_Name}")
                print(f"    Script: {data.m_Script}")
                assert "http://127.0.0.1:8080" in data.m_Script, "Target URL missing in script!"
                assert data.m_Script == '{"Default":{"Prod":"http://127.0.0.1:8080"}}', "Script content mismatch!"
                print(f"[SUCCESS] Independent UnityPy parser verified the patched asset inside the APK 1:1!")
                break
                
    if not found:
        print("[!] Error: endpointconfig TextAsset not found by UnityPy!")
        sys.exit(1)

if __name__ == "__main__":
    verify_apk_endpoint()
